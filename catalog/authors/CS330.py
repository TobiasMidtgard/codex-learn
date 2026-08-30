"""CS330 — Compiler Construction & Programming Languages. Author module."""

COURSE = {
    "id": "CS330",
    "title": "Compiler Construction & Programming Languages",
    "year": 3,
    "level": "Advanced",
    "prereqs": ["CS301", "CS310"],
    "stack": ["Python", "Rust (reference)"],
    "credits": 15,
    "hours": 170,
    "icon": "⟳",
    "summary": (
        "You build a complete compiler for a small imperative language: a lexer that "
        "reports the line and column of every token, a Pratt parser that gets precedence "
        "and associativity right, a scoped type checker that names the first error, a "
        "code generator targeting a stack virtual machine with calls and jumps, and an "
        "optimiser whose transformations are checked against a corpus rather than "
        "assumed. Nothing is generated for you — there is no parser generator and no "
        "runtime library."
    ),
    "outcomes": [
        "Tokenise source text into typed tokens carrying accurate line and column positions",
        "Implement a Pratt parser whose precedence and associativity tables are explicit data",
        "Build an abstract syntax tree that a later pass can walk without re-reading the source",
        "Resolve names through a stack of scopes and report shadowing, redeclaration and use-before-declaration",
        "Type-check expressions and statements and report the first error with its position",
        "Generate stack-machine code for expressions, control flow, locals and function calls",
        "Justify an optimisation as semantics-preserving by testing it against a program corpus",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone compiler build (60%).",
    "reading": [
        "Aho, Lam, Sethi & Ullman, *Compilers: Principles, Techniques and Tools*, 2nd ed. — chapters 2-6 and 8",
        "Nystrom, *Crafting Interpreters* (2021) — parts II and III, especially the Pratt parser and the bytecode VM",
        "Pierce, *Types and Programming Languages* (2002) — chapters 8-11 for the typing rules",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Lexical analysis",
            "summary": "Turning a flat string into typed tokens that remember where they came from.",
            "concepts": [
                "A token is a triple of kind, value and source position; the position is what makes later errors usable",
                "Maximal munch: `<=` is one token, not `<` followed by `=`, so longer operators must be tried first",
                "Keywords are identifiers that lose the competition — recognise the identifier, then look it up",
                "Line and column are separate counters: a newline resets the column and bumps the line",
                "Lexical errors (unexpected character, unterminated string, malformed number) belong to this pass, not the parser",
                "Whitespace and comments are skipped, but they still advance the position counters",
                "A synthetic EOF token lets every later pass peek without a bounds check",
            ],
            "quiz": {
                "title": "What the lexer owes every pass after it",
                "minutes": 7,
                "questions": [
                    {
                        "q": "`OPERATORS` is scanned in order and the list is longest first. What does the lexer make of the four characters `a<=b`?",
                        "opts": [
                            "Three tokens: `a`, `<=`, `b`",
                            "Four tokens: `a`, `<`, `=`, `b`",
                            "Three tokens: `a`, `<`, `=b`",
                            "One token, because there is no whitespace to split it on",
                        ],
                        "a": 0,
                        "why": r"""
Maximal munch: at each position the scanner takes the longest lexeme that fits, which
is why `OPERATORS` is written longest first and why the loop stops at the first match.
Sort that list shortest first and the scanner takes `<`, leaves `=`, and hands the
parser an assignment where a comparison was written — a bug that never mentions the
lexer in its symptoms. Whitespace is a separator, not a requirement: `a<=b` and
`a <= b` produce identical tokens, which is exactly why the position has to be
recorded rather than reconstructed later.
""",
                    },
                    {
                        "q": "The source contains the word `letter`. Why does the lexer not return the keyword `let` followed by an identifier `ter`?",
                        "opts": [
                            "It scans the whole identifier first, and only then asks whether that word is in `KEYWORDS`",
                            "`let` only counts as a keyword when a space follows it",
                            "`KEYWORDS` is checked first, and the check happens to fail here",
                            "It does split it, and the parser glues the pieces back together",
                        ],
                        "a": 0,
                        "why": r"""
Keywords are identifiers that lose a lookup. The scanner consumes letters, digits and
underscores until they run out — that gives `letter` — and the word is only then
tested against `KEYWORDS`. Trying keywords first means matching `let` inside `letter`,
`if` inside `ifx`, and `return` inside `returned`, and patching that with a
"followed by a space" rule breaks `let(x)` and every other legal spacing. Doing the
lookup after the scan needs no rule at all, because the longest identifier was already
taken.
""",
                    },
                    {
                        "q": "A token carries `line` and `col`. Which position do they hold?",
                        "opts": [
                            "That of the token's first character",
                            "That of the character just past its last",
                            "That of the first non-space character on its line",
                            "A byte offset into the source, converted to a line and column when something is reported",
                        ],
                        "a": 0,
                        "why": r"""
The first character, because that is where a caret has to point. An error that says
*column 11* for a token starting at column 9 sends the reader two characters past the
thing being complained about, and on a long line that is the difference between an
obvious mistake and a mystery. Storing an offset and converting on demand is a
perfectly real design — production compilers keep spans plus a table of line starts,
which is cheaper per token and gives you end positions for free — but this lexer keeps
the pair directly, and `start_col` is recorded before the cursor moves precisely so
that it survives the scan of the lexeme.
""",
                    },
                    {
                        "q": "Which of these is a *lexical* error — one this pass should raise rather than pass on?",
                        "opts": [
                            "`\"oops` — a string literal with no closing quote",
                            "`let x = ;` — a declaration with nothing on the right",
                            "`if x { print y;` — a block that is never closed",
                            "`f(1, 2)` where `f` was declared to take three arguments",
                        ],
                        "a": 0,
                        "why": r"""
The dividing line is what you need in order to notice. An unterminated string is
noticed while forming a single lexeme: the scanner runs off the end of the line with
no closing quote and has nothing to hand back. The missing right-hand side and the
unclosed block are both perfectly good token sequences — they only look wrong against
the grammar, so they belong to the parser. The argument count is not even a grammar
question; it needs a symbol table that knows how `f` was declared, which is module 3's
work. Push errors down as far as they will go: the lower the pass, the more precise
the position it can name.
""",
                    },
                    {
                        "q": "Why does `tokenize` append a synthetic `EOF` token instead of just returning?",
                        "opts": [
                            "So that every later pass can look at the next token without first checking that one exists",
                            "So that the number of tokens matches the number of lines",
                            "Because the parser needs somewhere to store its final error message",
                            "Because the source file might not end with a newline",
                        ],
                        "a": 0,
                        "why": r"""
It is a sentinel. `peek` is `self.tokens[self.pos]` with no bounds check, and it stays
that simple because the list can never run out: past the end there is always `EOF`,
and `advance` refuses to move beyond it. One token constructed once replaces an
`if self.pos < len(self.tokens)` in every function that looks ahead, and — worth more
— it removes the class of bug where one of those functions forgets. The `EOF` token
carries a position too, which is what lets "unexpected end of input" name a line and
column instead of shrugging.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The scanner loop, hole by hole",
                "minutes": 8,
                "caption": "main.py — one turn of the scanner's while loop",
                "lang": "python",
                "brief": r"""
Three cursors move through the source together and every branch has to keep them in
step: `i` indexes the string, `line` and `col` say where `i` is in human coordinates.
Almost every position bug in a lexer is one of these four holes filled in with
something that is *nearly* right.

Nothing runs here — you are choosing what the line has to say.
""",
                "listing": """ch = src[i]

if ch == "\\n":
    i += 1
    line += 1
    col = ___
    continue

start_col = ___          # where this lexeme begins, before anything moves

if ch.isalpha() or ch == "_":
    j = i
    while j < n and (src[j].isalnum() or src[j] == "_"):
        j += 1
    word = src[i:j]
    kind = ___ if word in KEYWORDS else "IDENT"
    tokens.append(Token(kind, word, line, start_col))
    col += ___
    i = j
    continue
""",
                "blanks": [
                    {
                        "prompt": "A newline has just been consumed. What column is the next character in?",
                        "hole": "?",
                        "opts": ["col + 1", "start_col", "1", "0"],
                        "a": 2,
                        "why": "Columns are one-based here, so the first character of a line sits at column 1 — the same number the editor shows in its status bar, which is the whole point of reporting one.",
                        "whys": [
                            "That carries the old line's column across the newline, so positions on the second line come out shifted by the length of the first — and the further down the file, the worse it gets.",
                            "`start_col` belongs to the lexeme that was scanned before the newline. It has nothing to say about where the new line starts.",
                            "Columns are one-based here, so the first character of a line sits at column 1 — the same number the editor shows in its status bar, which is the whole point of reporting one.",
                            "Zero-based columns are a defensible convention, but this hole is the wrong place to adopt one: `col` is initialised to `1` at the top of `tokenize`, so line 1 stays one-based and only line 2 onwards slides down by one. Half a convention is worse than either — the check \"Line and column survive a newline\" wants `print` at 2:1 and gets 2:0.",
                        ],
                    },
                    {
                        "prompt": "The lexeme's own column, saved before any cursor moves.",
                        "hole": "?",
                        "opts": ["col", "i", "1", "col + 1"],
                        "a": 0,
                        "why": "`col` is the live column cursor, and right now it still points at the first character of this lexeme. Saving it here is what lets the scan run ahead and still report where the token began.",
                        "whys": [
                            "`col` is the live column cursor, and right now it still points at the first character of this lexeme. Saving it here is what lets the scan run ahead and still report where the token began.",
                            "`i` is an index into the whole source string. On line 4 it is already in the hundreds, so every token would be reported in a column that does not exist.",
                            "A constant puts every token at the start of its line, which is worse than reporting nothing: the caret lands somewhere plausible and confidently wrong.",
                            "One past the first character. Every position would be off by one in the direction that hides the offending character rather than pointing at it.",
                        ],
                    },
                    {
                        "prompt": "The word has been scanned. What kind is it when the lookup succeeds?",
                        "hole": "?",
                        "opts": ['"IDENT"', '"OP"', '"NUM"', '"KW"'],
                        "a": 3,
                        "why": "The word competed as an identifier, won the scan, and then lost the lookup: it is in `KEYWORDS`, so it is a keyword. Scanning first and classifying second is exactly what keeps `letter` an identifier.",
                        "whys": [
                            "That is the kind for a word the lookup did *not* find, and it is already on the other side of the conditional. Using it in both branches makes the lookup pointless and leaves the parser waiting for a `let` it will never see.",
                            "`OP` is what the operator scan produces further down the loop. A word made of letters never reaches it.",
                            "`NUM` belongs to the digit branch further down the loop, which a lexeme starting with a letter never reaches — and a digit run glued to letters, `12ab`, is a malformed number rather than either kind.",
                            "The word competed as an identifier, won the scan, and then lost the lookup: it is in `KEYWORDS`, so it is a keyword. Scanning first and classifying second is exactly what keeps `letter` an identifier.",
                        ],
                    },
                    {
                        "prompt": "How far does the column cursor move now that the whole word is consumed?",
                        "hole": "?",
                        "opts": ["len(word) + 1", "j - i", "1", "j"],
                        "a": 1,
                        "why": "`j - i` is the number of characters the scan actually crossed. `i` becomes `j` on the next line, so this is the one increment that keeps the two cursors describing the same place.",
                        "whys": [
                            "One too many: it counts a character the scan never crossed, so each identifier on a line pushes everything after it one column right.",
                            "`j - i` is the number of characters the scan actually crossed. `i` becomes `j` on the next line, so this is the one increment that keeps the two cursors describing the same place.",
                            "One character, whatever the length of the word. `i` still jumps to `j`, so the two cursors part company at the first identifier and every position after it on that line is wrong.",
                            "`j` is an absolute index into the source, not a distance. Adding it to a column adds everything before the token as well.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "Count the tokens",
                "minutes": 6,
                "brief": r"""
A lexeme is not a word, and a token is not a character. The line below has whitespace
in places that do not separate anything, punctuation inside a string literal that is
not punctuation as far as the lexer is concerned, and a comment that produces no
tokens at all while still moving the position counters.
""",
                "prompt": "How many tokens does `tokenize` return for this line, counting the `EOF` token at the end?",
                "note": "A whole number. The line is complete as shown; there is nothing after it.",
                "figure": "`let s = \"a + b\"; print !ok && s;   # let s = 1;`",
                "given": [
                    {"label": "Whitespace", "value": "separates tokens, then is dropped"},
                    {"label": "Comments", "value": "`#` to the end of the line"},
                    {"label": "Operators", "value": "longest match wins"},
                    {"label": "Count", "value": "includes the `EOF` token"},
                ],
                "aside": "Nothing here is parsed. `ok` is never declared and `!ok && s` would not type-check, "
                         "which the lexer neither knows nor cares about.",
                "answer": 12,
                "tol": 0,
                "unit": "tokens",
                "hint": "Walk the line and count lexemes. Everything between the quotes is a single `STR` "
                        "token however much punctuation is in it, `&&` is one token rather than two, and "
                        "the comment yields nothing at all.",
                "wrong": "The two things most often missed are the `EOF` token at the end and the inside of "
                         "the string literal — the `+` between the quotes is text, not an operator.",
                "why": r"""
`let`, `s`, `=`, `"a + b"`, `;`, `print`, `!`, `ok`, `&&`, `s`, `;` is eleven, and the
synthetic `EOF` makes twelve. Three details do the work: the string is one `STR` token
whose value is the five characters `a + b`, so the `+` inside it is never an operator;
`&&` is one token because `OPERATORS` is scanned longest first; and everything from
`#` onwards is dropped, comment text that looks like code included. Note that the
comment still advances `col`, which is why the `EOF` token lands at column 48 rather
than at the semicolon — dropping a lexeme is not the same as pretending it was not
there.
""",
            },
            "lab": {
                "title": "A lexer with positions and honest errors",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
Write `tokenize(src)` for the course language. It returns a list of `Token`
objects, always ending with a single `EOF` token.

Token kinds:

| kind | what it holds |
| --- | --- |
| `NUM` | an `int` for `12`, a `float` for `3.5` |
| `STR` | the *decoded* contents of a `"..."` literal |
| `IDENT` | a name such as `total` |
| `KW` | one of the words in `KEYWORDS` |
| `OP` | one of the strings in `OPERATORS` |
| `EOF` | the empty string, once, at the end |

Positions are one-based: the first character of the file is line 1, column 1.
A token's position is that of its **first** character.

Rules:

- Spaces, tabs, carriage returns and newlines separate tokens and are dropped.
- `#` starts a comment that runs to the end of the line.
- An identifier is a letter or `_` followed by letters, digits or `_`. If the
  resulting word is in `KEYWORDS` the kind is `KW`, otherwise `IDENT`.
- A number is a run of digits, optionally followed by `.` and more digits.
  `12` lexes to the integer `12`, `3.5` to the float `3.5`.
- A string literal runs from `"` to the next `"` on the same line and
  understands the escapes `\n`, `\t`, `\\` and `\"`.
- Operators use maximal munch — `OPERATORS` is already ordered longest first.

Raise `LexError(message, line, col)` for:

- an unexpected character — `unexpected character '$'`
- a string that hits a newline or the end of input — `unterminated string`
- a digit run followed immediately by a letter or `_` — `malformed number`
- an unknown escape such as `\q` — `unknown escape \q`

```text
tokenize("let x = 12;")
  Token(KW, 'let', 1:1)   Token(IDENT, 'x', 1:5)   Token(OP, '=', 1:7)
  Token(NUM, 12, 1:9)     Token(OP, ';', 1:11)     Token(EOF, '', 1:12)
```
''',
                "files": [{"name": "main.py", "content": r'''
KEYWORDS = {"let", "fn", "if", "else", "while", "return", "print", "true", "false"}

# Longest first: maximal munch falls out of scanning this list in order.
OPERATORS = ["==", "!=", "<=", ">=", "&&", "||", "->",
             "+", "-", "*", "/", "%", "^", "=", "<", ">", "!",
             "(", ")", "{", "}", ",", ";", ":"]

ESCAPES = {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}


class LexError(Exception):
    """A malformed piece of source text, with the place it starts."""

    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message = message
        self.line = line
        self.col = col


class Token:
    def __init__(self, kind, value, line, col):
        self.kind = kind
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, {self.line}:{self.col})"

    def __eq__(self, other):
        return (isinstance(other, Token) and self.kind == other.kind
                and self.value == other.value
                and self.line == other.line and self.col == other.col)


def tokenize(src):
    """Source text -> list of Token, ending with one EOF token."""
    # Walk src with an index i, a line counter and a column counter.
    # Every branch must advance i and keep col in step with it.
    # your code here


for token in tokenize("let x = 12;"):
    print(token)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
KEYWORDS = {"let", "fn", "if", "else", "while", "return", "print", "true", "false"}

# Longest first: maximal munch falls out of scanning this list in order.
OPERATORS = ["==", "!=", "<=", ">=", "&&", "||", "->",
             "+", "-", "*", "/", "%", "^", "=", "<", ">", "!",
             "(", ")", "{", "}", ",", ";", ":"]

ESCAPES = {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}


class LexError(Exception):
    """A malformed piece of source text, with the place it starts."""

    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message = message
        self.line = line
        self.col = col


class Token:
    def __init__(self, kind, value, line, col):
        self.kind = kind
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, {self.line}:{self.col})"

    def __eq__(self, other):
        return (isinstance(other, Token) and self.kind == other.kind
                and self.value == other.value
                and self.line == other.line and self.col == other.col)


def tokenize(src):
    """Source text -> list of Token, ending with one EOF token."""
    tokens = []
    i = 0
    line = 1
    col = 1
    n = len(src)
    while i < n:
        ch = src[i]
        if ch == "\n":
            i += 1
            line += 1
            col = 1
            continue
        if ch in " \t\r":
            i += 1
            col += 1
            continue
        if ch == "#":
            while i < n and src[i] != "\n":
                i += 1
                col += 1
            continue

        start_col = col

        if ch.isalpha() or ch == "_":
            j = i
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            word = src[i:j]
            kind = "KW" if word in KEYWORDS else "IDENT"
            tokens.append(Token(kind, word, line, start_col))
            col += j - i
            i = j
            continue

        if ch.isdigit():
            j = i
            while j < n and src[j].isdigit():
                j += 1
            is_float = False
            if j + 1 < n and src[j] == "." and src[j + 1].isdigit():
                is_float = True
                j += 1
                while j < n and src[j].isdigit():
                    j += 1
            if j < n and (src[j].isalpha() or src[j] == "_"):
                raise LexError("malformed number", line, start_col)
            text = src[i:j]
            tokens.append(Token("NUM", float(text) if is_float else int(text),
                                line, start_col))
            col += j - i
            i = j
            continue

        if ch == '"':
            j = i + 1
            chars = []
            while True:
                if j >= n or src[j] == "\n":
                    raise LexError("unterminated string", line, start_col)
                if src[j] == '"':
                    break
                if src[j] == "\\":
                    if j + 1 >= n:
                        raise LexError("unterminated string", line, start_col)
                    esc = src[j + 1]
                    if esc not in ESCAPES:
                        raise LexError("unknown escape \\" + esc, line, start_col)
                    chars.append(ESCAPES[esc])
                    j += 2
                    continue
                chars.append(src[j])
                j += 1
            j += 1
            tokens.append(Token("STR", "".join(chars), line, start_col))
            col += j - i
            i = j
            continue

        for op in OPERATORS:
            if src.startswith(op, i):
                tokens.append(Token("OP", op, line, start_col))
                i += len(op)
                col += len(op)
                break
        else:
            raise LexError(f"unexpected character {ch!r}", line, start_col)

    tokens.append(Token("EOF", "", line, col))
    return tokens


for token in tokenize("let x = 12;"):
    print(token)
'''}],
                "hints": [
                    "Keep three cursors in step: `i` into the string, plus `line` and `col`. Every `i += k` needs a matching `col += k`, except a newline, which sets `col = 1` and bumps `line`.",
                    "Scan a whole lexeme with a second index `j`, then append one token and set `i = j`. Record `start_col` *before* you move.",
                    "Maximal munch is a plain loop: `for op in OPERATORS: if src.startswith(op, i): ...` with a `for/else` that raises for an unexpected character.",
                    "A digit run followed by a letter is `malformed number`; the check is `if j < n and (src[j].isalpha() or src[j] == '_')` after the digits are consumed.",
                ],
                "tests": [
                    {"name": "Kinds, values and positions of a simple statement", "code": r'''
_toks = tokenize("let x = 12;")
_want = [("KW", "let", 1, 1), ("IDENT", "x", 1, 5), ("OP", "=", 1, 7),
         ("NUM", 12, 1, 9), ("OP", ";", 1, 11), ("EOF", "", 1, 12)]
_got = [(t.kind, t.value, t.line, t.col) for t in _toks]
assert _got == _want, f"tokenize('let x = 12;') gave {_got!r}, expected {_want!r}"
assert isinstance(_toks[3].value, int), "12 should lex to the int 12, not a string"
'''},
                    {"name": "Line and column survive a newline", "code": r'''
_toks = tokenize("let a = 1;\nprint a;")
_got = [(t.kind, t.value, t.line, t.col) for t in _toks[5:]]
_want = [("KW", "print", 2, 1), ("IDENT", "a", 2, 7), ("OP", ";", 2, 8), ("EOF", "", 2, 9)]
assert _got == _want, f"second line lexed as {_got!r}, expected {_want!r}"
'''},
                    {"name": "Maximal munch on multi-character operators", "code": r'''
_got = [(t.kind, t.value) for t in tokenize("a <= b != c && d || !e -> f")][:-1]
_want = [("IDENT", "a"), ("OP", "<="), ("IDENT", "b"), ("OP", "!="), ("IDENT", "c"),
         ("OP", "&&"), ("IDENT", "d"), ("OP", "||"), ("OP", "!"), ("IDENT", "e"),
         ("OP", "->"), ("IDENT", "f")]
assert _got == _want, f"Got {_got!r}, expected {_want!r}"
assert [t.value for t in tokenize("a<b")][:3] == ["a", "<", "b"], "A lone < is still one token"
'''},
                    {"name": "Keywords, identifiers, comments and empty input", "code": r'''
assert [(t.kind, t.value) for t in tokenize("letter")][0] == ("IDENT", "letter"), \
    "'letter' merely starts with a keyword — it is an identifier"
assert tokenize("let")[0].kind == "KW", "'let' on its own is a keyword"
_toks = tokenize("")
assert len(_toks) == 1 and _toks[0].kind == "EOF" and (_toks[0].line, _toks[0].col) == (1, 1), \
    f"Empty input should give one EOF token at 1:1, got {_toks!r}"
_toks = tokenize("  # only a comment\n")
assert len(_toks) == 1 and (_toks[0].line, _toks[0].col) == (2, 1), \
    f"A comment line should leave only EOF at 2:1, got {_toks!r}"
assert sum(1 for t in tokenize("a b c") if t.kind == "EOF") == 1, "Exactly one EOF token"
'''},
                    {"name": "Floats and string escapes", "code": r'''
_toks = tokenize("x = 3.5;")
assert _toks[2].value == 3.5 and isinstance(_toks[2].value, float), \
    f"3.5 lexed as {_toks[2].value!r}"
_toks = tokenize('s = "a\\tb\\nc";')
assert _toks[2].kind == "STR", f"Expected a STR token, got {_toks[2]!r}"
assert _toks[2].value == "a\tb\nc", f"String decoded to {_toks[2].value!r}, expected 'a\\tb\\nc'"
assert tokenize('"he said \\"hi\\""')[0].value == 'he said "hi"', "Escaped quotes stay in the string"
assert tokenize('""')[0].value == "", "An empty string literal is a STR token holding ''"
'''},
                    {"name": "Lexical errors carry their position", "code": r'''
try:
    tokenize("let x = $;")
    assert False, "An unexpected character should raise LexError"
except LexError as _e:
    assert (_e.line, _e.col) == (1, 9), f"LexError reported {_e.line}:{_e.col}, expected 1:9"
try:
    tokenize('let s = "oops;')
    assert False, "An unterminated string should raise LexError"
except LexError as _e:
    assert (_e.line, _e.col) == (1, 9), f"LexError reported {_e.line}:{_e.col}, expected 1:9"
    assert "unterminated" in _e.message, f"message was {_e.message!r}"
try:
    tokenize("let x = 12ab;")
    assert False, "A digit run glued to letters should raise LexError"
except LexError as _e:
    assert (_e.line, _e.col) == (1, 9), f"LexError reported {_e.line}:{_e.col}, expected 1:9"
'''},
                    {"name": "A whole program lexes without loss", "code": r'''
_src = "fn add(a: num, b: num) -> num {\n  return a + b;   # sum\n}\nprint add(1, 2.5);\n"
_toks = tokenize(_src)
assert _toks[-1].kind == "EOF" and _toks[-1].line == 5, \
    f"EOF should land on line 5, got {_toks[-1]!r}"
_kinds = [t.kind for t in _toks]
assert _kinds.count("KW") == 3, \
    f"fn/return/print are the only keywords here, but KW count was {_kinds.count('KW')}"
assert _kinds.count("IDENT") == 9, \
    f"add a num b num num a b add are all identifiers, but IDENT count was {_kinds.count('IDENT')}"
assert ("OP", "->") in [(t.kind, t.value) for t in _toks], "The arrow is one OP token"
assert 2.5 in [t.value for t in _toks if t.kind == "NUM"], "2.5 should survive as a float"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Parsing and abstract syntax",
            "summary": "A Pratt expression parser and recursive descent for statements.",
            "concepts": [
                "Concrete syntax is a string; abstract syntax is a tree with the parentheses already spent",
                "Recursive descent: one function per non-terminal, the call stack is the derivation",
                "Pratt parsing replaces one function per precedence level with a binding-power table",
                "Left associativity re-enters the loop with `prec + 1`; right associativity with `prec`",
                "Prefix operators bind their operand at a fixed level, which is what makes `-2 ^ 2` parse as `-(2 ^ 2)`",
                "One token of lookahead distinguishes assignment from an expression statement",
                "A parse error names the token it found and the position it found it at",
            ],
            "quiz": {
                "title": "Precedence, associativity and the tree that results",
                "minutes": 7,
                "questions": [
                    {
                        "q": "`(1 + 2) * 3` and `1 + 2 * 3` parse to different trees, yet neither tree contains anything representing a parenthesis. Where did the brackets go?",
                        "opts": [
                            "They were spent during the parse: they decided which tree got built, and nothing afterwards needs them",
                            "A later pass walks the tree and deletes them",
                            "They are kept, as a `(\"group\", expr)` node wrapping the inner expression",
                            "They survive as an extra field on the `bin` node",
                        ],
                        "a": 0,
                        "why": r"""
This is the whole difference between concrete and abstract syntax. A bracket is an
instruction to the parser about grouping; once the grouping is in the shape of the
tree, the instruction has been carried out and re-recording it would be recording the
same fact twice. `parse_primary` shows this directly — the `(` branch parses the inner
expression and returns it *unwrapped*, with no node of its own. The consequence to
keep in mind is that a pretty-printer walking this tree has to re-insert brackets from
precedence, because the original ones are genuinely gone; that is a known cost of
abstract syntax, and tools that must preserve the source text exactly keep a concrete
tree alongside for it.
""",
                    },
                    {
                        "q": "In the Pratt loop, a left-associative operator recurses with `prec + 1` and a right-associative one with `prec`. What does the difference do?",
                        "opts": [
                            "Recursing at the same level lets the right operand absorb another operator of equal precedence, so equals nest to the right",
                            "It changes which operators are legal on the right, not how they group",
                            "`prec + 1` is a small optimisation; both spellings build the same tree",
                            "It decides the order the operands are evaluated in at run time",
                        ],
                        "a": 0,
                        "why": r"""
Look at what each choice forbids. With `prec + 1`, the recursive call refuses any
operator at the same level, so the right operand of `1 - 2` stops at `2`, the loop
comes back round, and `- 3` attaches to the tree already built: `(1 - 2) - 3`. With
`prec`, the recursive call happily takes another `^`, so `3 ^ 2` is swallowed whole
and becomes the right child: `2 ^ (3 ^ 2)`. One integer, one bit of behaviour, no
separate function per level — which is what a Pratt parser buys over a stack of
`parse_term` / `parse_factor` functions. Evaluation order is a separate question the
tree does not answer.
""",
                    },
                    {
                        "q": "Prefix `-` parses its operand with `self.parse_expr(UNARY_BIND)` and `UNARY_BIND` is 7, the level of `^`. What is `-2 ^ 2`?",
                        "opts": [
                            "`(\"unary\", \"-\", (\"bin\", \"^\", 2, 2))` — the negation of four",
                            "`(\"bin\", \"^\", (\"unary\", \"-\", 2), 2)` — minus two, squared",
                            "A parse error: a prefix operator cannot be followed by an infix one",
                            "It depends on `RIGHT_ASSOCIATIVE`, which contains `^`",
                        ],
                        "a": 0,
                        "why": r"""
`parse_expr(7)` will accept any operator whose precedence is at least 7, and `^` is
exactly 7 — so the recursive call takes `2 ^ 2` and hands the whole thing back as the
operand of the minus. The result is $-(2^2) = -4$, which agrees with mathematical
notation and with Python. The same number, 7, is what stops `-a * b` from behaving the
same way: `*` is 6, below the bind, so the negation closes over `a` alone and the
multiplication is built around it. Binding a prefix operator tighter than everything
would give $(-2)^2 = 4$; the choice is real, and worth making deliberately rather than
by accident.
""",
                    },
                    {
                        "q": "The parser is at the start of a statement and the next token is an `IDENT`. What does it need in order to tell an assignment from an expression statement?",
                        "opts": [
                            "The token after the identifier — `=` means assignment, anything else does not",
                            "The whole rest of the line, scanned ahead to the semicolon",
                            "A way to unwind and re-parse when the first guess turns out wrong",
                            "The symbol table, to find out whether the name is a variable",
                        ],
                        "a": 0,
                        "why": r"""
One token past the one you are looking at, which is why `self.tokens[self.pos + 1]` is
safe — the `EOF` sentinel guarantees there is something there to read. That single
peek is enough because the two forms differ at their second token and nowhere earlier,
which is a property of the grammar rather than luck; a grammar without it needs
backtracking or a longer lookahead, and both are avoidable design choices. The symbol
table cannot help even in principle: it does not exist yet, and `x = 1;` is a syntactic
question that stays the same whether or not `x` was ever declared.
""",
                    },
                    {
                        "q": "In recursive descent, what corresponds to the derivation — the record of which grammar rules were applied?",
                        "opts": [
                            "The call stack: each active call is a non-terminal currently being expanded",
                            "The token list, which the parser rewrites in place as it goes",
                            "An explicit stack of rule names the parser maintains alongside its position",
                            "The tree, which is why the derivation cannot be recovered until parsing finishes",
                        ],
                        "a": 0,
                        "why": r"""
That is the trick the technique is named for. `parse_stmt` calling `parse_expr` calling
`parse_unary` calling `parse_primary` *is* the leftmost derivation, held in the
machine's own stack instead of a data structure you wrote. It also explains the two
characteristic failure modes: a deeply nested expression can overflow the Python stack,
and a left-recursive rule such as `expr -> expr '+' term` calls itself with no token
consumed and never returns. The Pratt loop sidesteps the second one by making the
left-recursive case a `while` loop rather than a call — the tree still leans left, but
the recursion does not.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The Pratt loop, four decisions",
                "minutes": 9,
                "caption": "main.py — Parser.parse_expr",
                "lang": "python",
                "brief": r"""
Every precedence and associativity rule in the language is decided by the four holes
below. There is no table of grammar rules to consult and no function per level: the
binding powers are data, and this loop is the only place that reads them.

Nothing runs here — you are choosing what each line has to say.
""",
                "listing": """def parse_expr(self, min_prec=1):
    left = self.parse_unary()
    while True:
        tok = self.peek()
        if tok.kind != "OP" or tok.value not in PRECEDENCE:
            break
        prec = PRECEDENCE[tok.value]
        if prec < ___:
            break
        op = self.advance().value
        next_min = ___ if op in RIGHT_ASSOCIATIVE else ___
        right = self.parse_expr(next_min)
        left = ___
    return left
""",
                "blanks": [
                    {
                        "prompt": "When should this loop stop and hand what it has back to its caller?",
                        "hole": "?",
                        "opts": ["UNARY_BIND", "min_prec", "prec", "1"],
                        "a": 1,
                        "why": "`min_prec` is the caller's demand: *do not take anything looser than this*. An operator below it belongs to the caller, so the loop returns and lets the outer call build that node instead.",
                        "whys": [
                            "`UNARY_BIND` is the level a prefix operator hands down to its own operand. Using it as the loop's floor would reject `+` and `*` everywhere, leaving arithmetic unparseable.",
                            "`min_prec` is the caller's demand: *do not take anything looser than this*. An operator below it belongs to the caller, so the loop returns and lets the outer call build that node instead.",
                            "Comparing `prec` against itself is never true, so the loop never stops early and every operator is swallowed by the innermost call. `1 + 2 * 3` and `1 * 2 + 3` come out with the same shape, which is to say precedence stops existing.",
                            "A constant floor accepts every operator in the table at every depth, which is the same failure: the recursion has no way to decline an operator on the caller's behalf.",
                        ],
                    },
                    {
                        "prompt": "The operator just consumed is right-associative, like `^`. What floor does its right operand get?",
                        "hole": "?",
                        "opts": ["prec + 1", "prec - 1", "min_prec", "prec"],
                        "a": 3,
                        "why": "The same level it is at. The recursive call will therefore accept another `^`, swallow it, and return the nested tree — so `2 ^ 3 ^ 2` groups as `2 ^ (3 ^ 2)`, which is what the exponent notation means.",
                        "whys": [
                            "That is the left-associative floor, and it makes `^` group like subtraction: `(2 ^ 3) ^ 2`, which is $2^6$ rather than $2^9$. Both are legal trees; only one of them is what was written.",
                            "Dropping below the operator's own level lets the right operand take *looser* operators too, so `2 ^ 3 * 4` would grab the multiplication and become `2 ^ (3 * 4)`.",
                            "Passing the caller's floor straight through ignores the operator that was just consumed, so the nesting depends on where the expression started rather than on what it contains.",
                            "The same level it is at. The recursive call will therefore accept another `^`, swallow it, and return the nested tree — so `2 ^ 3 ^ 2` groups as `2 ^ (3 ^ 2)`, which is what the exponent notation means.",
                        ],
                    },
                    {
                        "prompt": "And for everything else — `+`, `-`, `*` and the comparisons?",
                        "hole": "?",
                        "opts": ["prec + 1", "prec", "min_prec + 1", "1"],
                        "a": 0,
                        "why": "One level up, so the recursive call refuses an operator of equal precedence and leaves it for this loop's next turn. That is what makes `1 - 2 - 3` come back as `(1 - 2) - 3`.",
                        "whys": [
                            "One level up, so the recursive call refuses an operator of equal precedence and leaves it for this loop's next turn. That is what makes `1 - 2 - 3` come back as `(1 - 2) - 3`.",
                            "That is the right-associative floor. Applied to subtraction it builds `1 - (2 - 3)`, which is 2 where the answer should be $-4$ — the kind of bug that survives every test written with `+` and `*`.",
                            "Built from the caller's floor rather than this operator's, so two `*` at the same level group differently depending on what enclosed them.",
                            "A floor of 1 accepts everything, so the right operand keeps eating the rest of the expression and the whole thing leans right.",
                        ],
                    },
                    {
                        "prompt": "The right operand is parsed. What replaces `left` before the loop turns again?",
                        "hole": "?",
                        "opts": [
                            "(\"bin\", op, left, self.parse_unary())",
                            "right",
                            "(\"bin\", op, left, right)",
                            "(\"bin\", op, right, left)",
                        ],
                        "a": 2,
                        "why": "The node just built becomes the left operand of whatever comes next, and that reassignment is the entire mechanism of left associativity — the tree grows downwards on its left side, one turn of the loop per operator.",
                        "whys": [
                            "The operand was already parsed into `right`; parsing another one here consumes a token that belongs to the next operator and drops the value that was just built.",
                            "Throwing the operator and the left operand away keeps only the last operand, so `1 + 2 + 3` parses to `3`.",
                            "The node just built becomes the left operand of whatever comes next, and that reassignment is the entire mechanism of left associativity — the tree grows downwards on its left side, one turn of the loop per operator.",
                            "Swapping the children silently reverses every non-commutative operator: `5 - 3` evaluates to 2 with the operands the right way round and to $-2$ this way, and `+` and `*` keep working, so half the tests still pass.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How many trees is that expression, without a precedence table?",
                "minutes": 8,
                "brief": r"""
A grammar written as `expr -> expr OP expr` is ambiguous: it says which strings are
expressions but not which tree each one denotes. The precedence and associativity
table is what removes the ambiguity, and it is worth knowing how much ambiguity it is
removing.

Count the trees for one chain of the same operator, where precedence has nothing to
say and only the grouping is in question:

```text
a - b - c - d - e
```

Each tree is a different program: `(a - b) - c` and `a - (b - c)` disagree for almost
every input, so this is not a question about notation.
""",
                "prompt": "Ignoring precedence and associativity entirely, how many distinct binary trees could `a - b - c - d - e` denote?",
                "note": "The operands stay in the order written — only the grouping varies. A whole number.",
                "figure": "`a - b - c - d - e` — five operands, four subtractions, no rule yet about how they group",
                "given": [
                    {"label": "Operands", "value": "5, in a fixed order"},
                    {"label": "Operators", "value": "4, all the same"},
                    {"label": "Counted", "value": "distinct binary trees"},
                ],
                "aside": "Split at whichever operator ends up at the root: with $i$ operands to its left "
                         "and $5 - i$ to its right, the two sides are independent, so the counts multiply.",
                "answer": 14,
                "tol": 0,
                "unit": "trees",
                "hint": "Let $T(k)$ be the answer for $k$ operands. $T(1) = 1$, and "
                        "$T(k) = \\sum_{i=1}^{k-1} T(i)\\,T(k-i)$. That gives $T(2) = 1$, $T(3) = 2$, "
                        "$T(4) = 5$ — keep going one more step.",
                "wrong": "Counting arrangements of the operands, or subsets of the operators, both give "
                         "numbers that grow far too fast. Only the bracketing varies here: the operands "
                         "stay where they are and every tree has exactly four internal nodes.",
                "why": r"""
$T(5) = T(1)T(4) + T(2)T(3) + T(3)T(2) + T(4)T(1) = 5 + 2 + 2 + 5 = 14$. The sequence
$1, 1, 2, 5, 14, 42, 132$ is the Catalan numbers, and they count binary trees for the
same reason they count bracketings — the recurrence above *is* the recursive structure
of a tree, written down.

Fourteen candidates, and the parser returns exactly one of them without ever
enumerating the rest: the loop's `prec + 1` picks the leftmost grouping,
`(((a - b) - c) - d) - e`, in a single pass. That is the real content of an
associativity rule, and it is also why an ambiguous grammar handed to a parser
generator produces a *conflict* rather than a list — the tool is telling you it has
fourteen answers and no basis for choosing.
""",
            },
            "lab": {
                "title": "A Pratt parser for the whole grammar",
                "runtime": "python",
                "minutes": 75,
                "brief": r'''
The lexer from module 1 is given. Write the parser: `parse(src)` returns a
**list of statement nodes**. Nodes are plain tuples, so you can compare them
directly.

Expressions:

```text
("num", 12)            ("str", "hi")          ("bool", True)
("var", "x")           ("unary", "-", expr)   ("bin", "+", left, right)
("call", "add", [args])
```

Statements:

```text
("let", name, expr)        ("assign", name, expr)     ("print", expr)
("expr", expr)             ("return", expr_or_None)
("if", cond, then_stmts, else_stmts)     ("while", cond, body_stmts)
("fn", name, [params], body_stmts)
```

`let`, `assign`, `print`, `return` and expression statements all end in `;`.
`if`, `while` and `fn` take a `{ ... }` block and no semicolon. An `if` with
no `else` gets `[]`. `else if` chains: the `else` list then holds exactly one
`("if", ...)` node.

Binding powers (already in `PRECEDENCE`), loosest first:

```text
1  ||            2  &&           3  ==  !=      4  <  <=  >  >=
5  +  -          6  *  /  %      7  ^ (right associative)
```

Prefix `-` and `!` bind their operand at level `UNARY_BIND` = 7, so
`-2 ^ 2` is `-(2 ^ 2)` while `-a * b` is `(-a) * b`.

Raise `ParseError(message, line, col)` using the position of the offending
token. `Parser.expect` should do that for you once you write it.

```text
parse("1 + 2 * 3;")
  [("expr", ("bin", "+", ("num", 1), ("bin", "*", ("num", 2), ("num", 3))))]
```
''',
                "files": [{"name": "main.py", "content": r'''
# ---------------------------------------------------------------- given: lexer
KEYWORDS = {"let", "fn", "if", "else", "while", "return", "print", "true", "false"}
OPERATORS = ["==", "!=", "<=", ">=", "&&", "||", "->",
             "+", "-", "*", "/", "%", "^", "=", "<", ">", "!",
             "(", ")", "{", "}", ",", ";", ":"]
ESCAPES = {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}


class LexError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message, self.line, self.col = message, line, col


class Token:
    def __init__(self, kind, value, line, col):
        self.kind, self.value, self.line, self.col = kind, value, line, col

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, {self.line}:{self.col})"


def tokenize(src):
    tokens, i, line, col, n = [], 0, 1, 1, len(src)
    while i < n:
        ch = src[i]
        if ch == "\n":
            i, line, col = i + 1, line + 1, 1
            continue
        if ch in " \t\r":
            i, col = i + 1, col + 1
            continue
        if ch == "#":
            while i < n and src[i] != "\n":
                i, col = i + 1, col + 1
            continue
        start_col = col
        if ch.isalpha() or ch == "_":
            j = i
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            word = src[i:j]
            tokens.append(Token("KW" if word in KEYWORDS else "IDENT", word, line, start_col))
            col, i = col + j - i, j
            continue
        if ch.isdigit():
            j, is_float = i, False
            while j < n and src[j].isdigit():
                j += 1
            if j + 1 < n and src[j] == "." and src[j + 1].isdigit():
                is_float, j = True, j + 1
                while j < n and src[j].isdigit():
                    j += 1
            if j < n and (src[j].isalpha() or src[j] == "_"):
                raise LexError("malformed number", line, start_col)
            text = src[i:j]
            tokens.append(Token("NUM", float(text) if is_float else int(text), line, start_col))
            col, i = col + j - i, j
            continue
        if ch == '"':
            j, chars = i + 1, []
            while True:
                if j >= n or src[j] == "\n":
                    raise LexError("unterminated string", line, start_col)
                if src[j] == '"':
                    break
                if src[j] == "\\":
                    esc = src[j + 1] if j + 1 < n else ""
                    if esc not in ESCAPES:
                        raise LexError("bad escape", line, start_col)
                    chars.append(ESCAPES[esc])
                    j += 2
                    continue
                chars.append(src[j])
                j += 1
            j += 1
            tokens.append(Token("STR", "".join(chars), line, start_col))
            col, i = col + j - i, j
            continue
        for op in OPERATORS:
            if src.startswith(op, i):
                tokens.append(Token("OP", op, line, start_col))
                i, col = i + len(op), col + len(op)
                break
        else:
            raise LexError(f"unexpected character {ch!r}", line, start_col)
    tokens.append(Token("EOF", "", line, col))
    return tokens


# ---------------------------------------------------------------- your parser
PRECEDENCE = {"||": 1, "&&": 2, "==": 3, "!=": 3,
              "<": 4, "<=": 4, ">": 4, ">=": 4,
              "+": 5, "-": 5, "*": 6, "/": 6, "%": 6, "^": 7}
RIGHT_ASSOCIATIVE = {"^"}
UNARY_BIND = 7


class ParseError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message, self.line, self.col = message, line, col


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        if tok.kind != "EOF":
            self.pos += 1
        return tok

    def at(self, kind, value=None):
        """True when the next token has this kind (and value, when given)."""
        # your code here

    def expect(self, kind, value=None):
        """Consume and return the next token, or raise ParseError."""
        # your code here

    def parse_program(self):
        """Statements until EOF."""
        # your code here

    def parse_block(self):
        """'{' statements '}' -> a list of statements."""
        # your code here

    def parse_stmt(self):
        """One statement node."""
        # your code here

    def parse_expr(self, min_prec=1):
        """Pratt loop: a prefix expression, then operators of at least min_prec."""
        # your code here

    def parse_unary(self):
        """Prefix - and !, otherwise a primary."""
        # your code here

    def parse_primary(self):
        """Literals, names, calls and ( ... )."""
        # your code here


def parse(src):
    return Parser(tokenize(src)).parse_program()


print(parse("let x = 1 + 2 * 3;"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
# ---------------------------------------------------------------- given: lexer
KEYWORDS = {"let", "fn", "if", "else", "while", "return", "print", "true", "false"}
OPERATORS = ["==", "!=", "<=", ">=", "&&", "||", "->",
             "+", "-", "*", "/", "%", "^", "=", "<", ">", "!",
             "(", ")", "{", "}", ",", ";", ":"]
ESCAPES = {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}


class LexError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message, self.line, self.col = message, line, col


class Token:
    def __init__(self, kind, value, line, col):
        self.kind, self.value, self.line, self.col = kind, value, line, col

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, {self.line}:{self.col})"


def tokenize(src):
    tokens, i, line, col, n = [], 0, 1, 1, len(src)
    while i < n:
        ch = src[i]
        if ch == "\n":
            i, line, col = i + 1, line + 1, 1
            continue
        if ch in " \t\r":
            i, col = i + 1, col + 1
            continue
        if ch == "#":
            while i < n and src[i] != "\n":
                i, col = i + 1, col + 1
            continue
        start_col = col
        if ch.isalpha() or ch == "_":
            j = i
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            word = src[i:j]
            tokens.append(Token("KW" if word in KEYWORDS else "IDENT", word, line, start_col))
            col, i = col + j - i, j
            continue
        if ch.isdigit():
            j, is_float = i, False
            while j < n and src[j].isdigit():
                j += 1
            if j + 1 < n and src[j] == "." and src[j + 1].isdigit():
                is_float, j = True, j + 1
                while j < n and src[j].isdigit():
                    j += 1
            if j < n and (src[j].isalpha() or src[j] == "_"):
                raise LexError("malformed number", line, start_col)
            text = src[i:j]
            tokens.append(Token("NUM", float(text) if is_float else int(text), line, start_col))
            col, i = col + j - i, j
            continue
        if ch == '"':
            j, chars = i + 1, []
            while True:
                if j >= n or src[j] == "\n":
                    raise LexError("unterminated string", line, start_col)
                if src[j] == '"':
                    break
                if src[j] == "\\":
                    esc = src[j + 1] if j + 1 < n else ""
                    if esc not in ESCAPES:
                        raise LexError("bad escape", line, start_col)
                    chars.append(ESCAPES[esc])
                    j += 2
                    continue
                chars.append(src[j])
                j += 1
            j += 1
            tokens.append(Token("STR", "".join(chars), line, start_col))
            col, i = col + j - i, j
            continue
        for op in OPERATORS:
            if src.startswith(op, i):
                tokens.append(Token("OP", op, line, start_col))
                i, col = i + len(op), col + len(op)
                break
        else:
            raise LexError(f"unexpected character {ch!r}", line, start_col)
    tokens.append(Token("EOF", "", line, col))
    return tokens


# ---------------------------------------------------------------- your parser
PRECEDENCE = {"||": 1, "&&": 2, "==": 3, "!=": 3,
              "<": 4, "<=": 4, ">": 4, ">=": 4,
              "+": 5, "-": 5, "*": 6, "/": 6, "%": 6, "^": 7}
RIGHT_ASSOCIATIVE = {"^"}
UNARY_BIND = 7


class ParseError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message, self.line, self.col = message, line, col


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        if tok.kind != "EOF":
            self.pos += 1
        return tok

    def at(self, kind, value=None):
        """True when the next token has this kind (and value, when given)."""
        tok = self.peek()
        return tok.kind == kind and (value is None or tok.value == value)

    def expect(self, kind, value=None):
        """Consume and return the next token, or raise ParseError."""
        tok = self.peek()
        if not self.at(kind, value):
            wanted = value if value is not None else kind
            raise ParseError(f"expected {wanted!r}, found {tok.value!r}", tok.line, tok.col)
        return self.advance()

    def parse_program(self):
        """Statements until EOF."""
        stmts = []
        while not self.at("EOF"):
            stmts.append(self.parse_stmt())
        return stmts

    def parse_block(self):
        """'{' statements '}' -> a list of statements."""
        self.expect("OP", "{")
        stmts = []
        while not self.at("OP", "}"):
            if self.at("EOF"):
                tok = self.peek()
                raise ParseError("unclosed block", tok.line, tok.col)
            stmts.append(self.parse_stmt())
        self.expect("OP", "}")
        return stmts

    def parse_stmt(self):
        """One statement node."""
        tok = self.peek()
        if tok.kind == "KW" and tok.value == "let":
            self.advance()
            name = self.expect("IDENT").value
            self.expect("OP", "=")
            expr = self.parse_expr()
            self.expect("OP", ";")
            return ("let", name, expr)
        if tok.kind == "KW" and tok.value == "print":
            self.advance()
            expr = self.parse_expr()
            self.expect("OP", ";")
            return ("print", expr)
        if tok.kind == "KW" and tok.value == "return":
            self.advance()
            expr = None if self.at("OP", ";") else self.parse_expr()
            self.expect("OP", ";")
            return ("return", expr)
        if tok.kind == "KW" and tok.value == "if":
            self.advance()
            cond = self.parse_expr()
            then_stmts = self.parse_block()
            else_stmts = []
            if self.at("KW", "else"):
                self.advance()
                if self.at("KW", "if"):
                    else_stmts = [self.parse_stmt()]
                else:
                    else_stmts = self.parse_block()
            return ("if", cond, then_stmts, else_stmts)
        if tok.kind == "KW" and tok.value == "while":
            self.advance()
            cond = self.parse_expr()
            return ("while", cond, self.parse_block())
        if tok.kind == "KW" and tok.value == "fn":
            self.advance()
            name = self.expect("IDENT").value
            self.expect("OP", "(")
            params = []
            while not self.at("OP", ")"):
                params.append(self.expect("IDENT").value)
                if not self.at("OP", ")"):
                    self.expect("OP", ",")
            self.expect("OP", ")")
            return ("fn", name, params, self.parse_block())
        if tok.kind == "IDENT" and self.tokens[self.pos + 1].kind == "OP" \
                and self.tokens[self.pos + 1].value == "=":
            name = self.advance().value
            self.advance()
            expr = self.parse_expr()
            self.expect("OP", ";")
            return ("assign", name, expr)
        expr = self.parse_expr()
        self.expect("OP", ";")
        return ("expr", expr)

    def parse_expr(self, min_prec=1):
        """Pratt loop: a prefix expression, then operators of at least min_prec."""
        left = self.parse_unary()
        while True:
            tok = self.peek()
            if tok.kind != "OP" or tok.value not in PRECEDENCE:
                break
            prec = PRECEDENCE[tok.value]
            if prec < min_prec:
                break
            op = self.advance().value
            next_min = prec if op in RIGHT_ASSOCIATIVE else prec + 1
            right = self.parse_expr(next_min)
            left = ("bin", op, left, right)
        return left

    def parse_unary(self):
        """Prefix - and !, otherwise a primary."""
        tok = self.peek()
        if tok.kind == "OP" and tok.value in ("-", "!"):
            self.advance()
            return ("unary", tok.value, self.parse_expr(UNARY_BIND))
        return self.parse_primary()

    def parse_primary(self):
        """Literals, names, calls and ( ... )."""
        tok = self.peek()
        if tok.kind == "NUM":
            return ("num", self.advance().value)
        if tok.kind == "STR":
            return ("str", self.advance().value)
        if tok.kind == "KW" and tok.value in ("true", "false"):
            return ("bool", self.advance().value == "true")
        if tok.kind == "IDENT":
            name = self.advance().value
            if self.at("OP", "("):
                self.advance()
                args = []
                while not self.at("OP", ")"):
                    args.append(self.parse_expr())
                    if not self.at("OP", ")"):
                        self.expect("OP", ",")
                self.expect("OP", ")")
                return ("call", name, args)
            return ("var", name)
        if tok.kind == "OP" and tok.value == "(":
            self.advance()
            inner = self.parse_expr()
            self.expect("OP", ")")
            return inner
        raise ParseError(f"unexpected token {tok.value!r}", tok.line, tok.col)


def parse(src):
    return Parser(tokenize(src)).parse_program()


print(parse("let x = 1 + 2 * 3;"))
'''}],
                "hints": [
                    "`expect` is the workhorse: compare `self.peek()` against the wanted kind/value, raise `ParseError(..., tok.line, tok.col)` when it disagrees, otherwise `return self.advance()`.",
                    "The Pratt loop is: parse a prefix expression, then `while` the next token is an operator whose precedence is at least `min_prec`, consume it and recurse with `prec + 1` (or `prec` for `^`).",
                    "`parse_unary` recurses into `self.parse_expr(UNARY_BIND)`, not into `parse_primary` — that is exactly what lets `^` grab the operand first.",
                    "Assignment needs one extra token of lookahead: `self.tokens[self.pos + 1]` is safe because the EOF token is always there.",
                ],
                "tests": [
                    {"name": "Precedence and left associativity", "code": r'''
_got = parse("1 + 2 * 3;")
_want = [("expr", ("bin", "+", ("num", 1), ("bin", "*", ("num", 2), ("num", 3))))]
assert _got == _want, f"1 + 2 * 3 parsed as {_got!r}, expected {_want!r}"
_got = parse("1 - 2 - 3;")
_want = [("expr", ("bin", "-", ("bin", "-", ("num", 1), ("num", 2)), ("num", 3)))]
assert _got == _want, f"1 - 2 - 3 parsed as {_got!r}, expected left associativity {_want!r}"
_got = parse("(1 + 2) * 3;")
_want = [("expr", ("bin", "*", ("bin", "+", ("num", 1), ("num", 2)), ("num", 3)))]
assert _got == _want, f"(1 + 2) * 3 parsed as {_got!r}, expected {_want!r}"
'''},
                    {"name": "Right associativity and prefix operators", "code": r'''
_got = parse("2 ^ 3 ^ 2;")[0][1]
_want = ("bin", "^", ("num", 2), ("bin", "^", ("num", 3), ("num", 2)))
assert _got == _want, f"2 ^ 3 ^ 2 parsed as {_got!r}, expected {_want!r}"
_got = parse("-2 ^ 2;")[0][1]
_want = ("unary", "-", ("bin", "^", ("num", 2), ("num", 2)))
assert _got == _want, f"-2 ^ 2 parsed as {_got!r}, expected {_want!r}"
_got = parse("-a * b;")[0][1]
_want = ("bin", "*", ("unary", "-", ("var", "a")), ("var", "b"))
assert _got == _want, f"-a * b parsed as {_got!r}, expected {_want!r}"
_got = parse("!true;")[0][1]
assert _got == ("unary", "!", ("bool", True)), f"!true parsed as {_got!r}"
'''},
                    {"name": "Comparison binds tighter than the logical operators", "code": r'''
_got = parse("a < b && c == d || e;")[0][1]
_want = ("bin", "||",
         ("bin", "&&", ("bin", "<", ("var", "a"), ("var", "b")),
          ("bin", "==", ("var", "c"), ("var", "d"))),
         ("var", "e"))
assert _got == _want, f"Parsed as {_got!r}, expected {_want!r}"
'''},
                    {"name": "let, assignment and expression statements", "code": r'''
assert parse("let x = 1;") == [("let", "x", ("num", 1))], f'Got {parse("let x = 1;")!r}'
assert parse("x = 2;") == [("assign", "x", ("num", 2))], f'Got {parse("x = 2;")!r}'
_p = parse('print "hi";')
assert _p == [("print", ("str", "hi"))], f"print statement parsed as {_p!r}"
assert parse("f(1);") == [("expr", ("call", "f", [("num", 1)]))], f'Got {parse("f(1);")!r}'
assert parse("") == [], "An empty source is an empty program"
'''},
                    {"name": "Blocks, if/else and while", "code": r'''
_got = parse("if x < 3 { print x; } else { print 0; }")
_want = [("if", ("bin", "<", ("var", "x"), ("num", 3)),
          [("print", ("var", "x"))], [("print", ("num", 0))])]
assert _got == _want, f"Got {_got!r}, expected {_want!r}"
_got = parse("while x { x = x - 1; }")
_want = [("while", ("var", "x"), [("assign", "x", ("bin", "-", ("var", "x"), ("num", 1)))])]
assert _got == _want, f"Got {_got!r}, expected {_want!r}"
assert parse("if x { }")[0][3] == [], "An if with no else gets an empty else list"
_chain = parse("if a { } else if b { } else { }")[0]
assert _chain[3][0][0] == "if", f"else-if should nest an if node, got {_chain[3]!r}"
'''},
                    {"name": "Functions, parameters and calls", "code": r'''
_got = parse("fn add(a, b) { return a + b; }")
_want = [("fn", "add", ["a", "b"],
          [("return", ("bin", "+", ("var", "a"), ("var", "b")))])]
assert _got == _want, f"Got {_got!r}, expected {_want!r}"
assert parse("fn go() { return; }") == [("fn", "go", [], [("return", None)])], \
    f'Got {parse("fn go() { return; }")!r}'
_got = parse("print add(1, 2 * 3);")[0][1]
_want = ("call", "add", [("num", 1), ("bin", "*", ("num", 2), ("num", 3))])
assert _got == _want, f"Got {_got!r}, expected {_want!r}"
assert parse("f();")[0][1] == ("call", "f", []), "A no-argument call has an empty argument list"
'''},
                    {"name": "Parse errors name a position", "code": r'''
for _src, _pos in [("1 + ;", (1, 5)), ("let = 5;", (1, 5)),
                   ("(1 + 2;", (1, 7)), ("let x = 1", (1, 10))]:
    try:
        parse(_src)
        assert False, f"parse({_src!r}) should raise ParseError"
    except ParseError as _e:
        assert (_e.line, _e.col) == _pos, \
            f"parse({_src!r}) reported {_e.line}:{_e.col}, expected {_pos[0]}:{_pos[1]}"
try:
    parse("if x { print 1;")
    assert False, "An unclosed block should raise ParseError"
except ParseError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Semantic analysis: scopes, resolution and types",
            "summary": "A symbol table that respects blocks, and a type checker that stops at the first real error.",
            "concepts": [
                "Syntax says a program is well-formed; semantics says it means something",
                "A symbol table is a stack of dictionaries — innermost first on lookup, innermost only on declaration",
                "Shadowing is legal and redeclaration is not: the difference is which scope you look in",
                "Type judgements are compositional: the type of a node is a function of the types of its children",
                "Hoisting function signatures before checking bodies is what makes mutual recursion possible",
                "An error message is only useful with a position, so every node carries one",
                "Fail fast on the first error: cascading errors from a poisoned type are noise",
            ],
            "quiz": {
                "title": "Scopes, hoisting and the first error",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Shadowing is legal, redeclaration is not. Which property of the symbol table draws that line?",
                        "opts": [
                            "`declare` inspects only the innermost dictionary, while `lookup` walks all of them from the inside out",
                            "`declare` walks outwards too, and compares how deep the existing binding is",
                            "The parser rejects a repeated `let` before the table ever sees it",
                            "`pop` deletes any binding that shadowed an outer one",
                        ],
                        "a": 0,
                        "why": r"""
Two methods, two different reaches, and that is the entire rule. `declare` asks *is
this name already bound here*, where "here" is `self.scopes[-1]` and nothing else — so
an inner block may bind `x` even though an outer one has, and the second `let x` in
the same block is caught. `lookup` asks *what does this name mean now*, which is a
question about every enclosing scope, answered innermost first. Make `declare` walk
outwards and shadowing becomes an error; make `lookup` stop at the innermost scope and
every reference to an outer variable breaks. And the parser genuinely cannot help: it
sees two well-formed `let` statements and has no idea they collide.
""",
                    },
                    {
                        "q": "Why are all the top-level `fn` signatures declared in one loop, before any function body is checked?",
                        "opts": [
                            "So a body can call a function defined further down the file — mutual recursion needs both names bound before either body is looked at",
                            "So the bodies can be checked in any order, which lets the pass be parallelised",
                            "Because the return type of a function cannot be known until its body has been checked",
                            "Because parameters must be declared in the global scope first",
                        ],
                        "a": 0,
                        "why": r"""
Check the bodies in one pass and `is_even` calling `is_odd` fails whenever `is_odd`
happens to appear later in the file — and since `is_odd` calls back, no ordering saves
both. Hoisting the signatures first means every call, wherever it appears, finds a
`("fn", params, ret)` binding to check itself against. Note what makes this cheap: the
signature is written down by the programmer, so it can be recorded without looking at
the body at all. A language that *infers* return types has to do real work here —
Hindley-Milner solves a whole binding group at once for exactly this reason — which is
one concrete thing an explicit type annotation buys the compiler.
""",
                    },
                    {
                        "q": "`type_of` is described as compositional. What does that actually mean here?",
                        "opts": [
                            "The type of a node is a function of the types of its children, so one bottom-up walk types the tree",
                            "Every expression has exactly one type, and no expression has two",
                            "The types compose into a single type for the whole program",
                            "Any two expressions of the same type may be swapped without changing the program",
                        ],
                        "a": 0,
                        "why": r"""
It means the recursion terminates in the obvious way and never has to guess: to type
`a + b` you type `a`, type `b`, and consult one rule. No node needs to know what
encloses it, so there is no fixed-point iteration and no ordering constraint beyond
children-before-parent. That is also why the checker fits in one dispatch on `node[0]`.
Languages where this fails are the interesting ones — a lambda with no annotation
needs its argument type from the *context*, which is why bidirectional type checking
exists, and why the rule "type is a function of the children" is worth naming as an
assumption rather than assuming it silently.
""",
                    },
                    {
                        "q": "Which of these programs does `declare` reject?",
                        "opts": [
                            "`let x = 1; let x = 2;` at the top level",
                            "`let x = 1; if c { let x = \"a\"; }`",
                            "`let x = 1; while c { let y = x; }`",
                            "`fn f(a) { return a; } let a = 1;`",
                        ],
                        "a": 0,
                        "why": r"""
Only the first is two bindings of one name in a single scope; the rest are all
different scopes. The `if` body binds `x` in its own dictionary, which shadows the
outer `x` until the block is popped — legal, if not always wise. The `while` body binds
a fresh `y` and reads `x` from outside, which is what `lookup` walking outwards is for.
The parameter `a` lives in the function's scope, so a global `a` afterwards collides
with nothing. The check is mechanical: name the enclosing block of each binding, and
if two bindings name the same block with the same identifier, that is the error.
""",
                    },
                    {
                        "q": "The checker raises on the first error rather than collecting them. What is the argument for that here?",
                        "opts": [
                            "After a failed judgement the node has no type, so anything reported downstream is guesswork about an unknown",
                            "Programs rarely contain more than one error",
                            "Exceptions are faster than accumulating a list",
                            "The position information is lost once the walk has moved past the node",
                        ],
                        "a": 0,
                        "why": r"""
`type_of` has to return a type for its caller to use. When the rule fails there is no
honest type to return, and inventing one makes every enclosing expression suspect: one
misspelled name becomes fifteen errors, fourteen of which name lines that are fine.
That is a real cost, and the reason people put up with a compiler that stops early.
Compilers that do report many errors buy it deliberately — they add an `error` type
that is compatible with everything and silently absorbs further complaints, plus
parser recovery at statement boundaries. Both are worth building; neither is free, and
"report the first one accurately" is the honest version of not building them.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The two halves of a symbol table",
                "minutes": 8,
                "caption": "main.py — SymbolTable, and one typing rule",
                "lang": "python",
                "brief": r"""
`declare` and `lookup` differ in two characters, and those two characters are the
scoping rules of the language. The typing rule underneath is here for contrast: it
also compares two things, but it returns something that has nothing to do with what it
compared.

Nothing runs here — you are choosing what each line has to say.
""",
                "listing": """def declare(self, name, type_, pos=(1, 1)):
    scope = self.scopes[___]
    if name in scope:
        raise SemanticError(f"{name!r} is already declared in this scope",
                            pos[0], pos[1])
    scope[name] = type_
    return type_

def lookup(self, name):
    for scope in ___(self.scopes):
        if name in scope:
            return scope[name]
    return ___


# ... and in type_of, the rule for == and !=
if op in EQUALITY:
    if lt != rt:
        raise SemanticError(f"cannot compare {lt} with {rt}", pos[0], pos[1])
    return ___
""",
                "blanks": [
                    {
                        "prompt": "Which scope does a declaration land in — and which scope may object to it?",
                        "hole": "?",
                        "opts": ["0", ":", "1", "-1"],
                        "a": 3,
                        "why": "The innermost scope, the last one pushed. Declaring there and objecting only from there is what makes an inner `let x` shadow an outer one instead of colliding with it.",
                        "whys": [
                            "Index 0 is the global scope. Every local would be declared globally, so two functions could not each have a parameter called `n`, and popping a block would leave its bindings behind.",
                            "A slice gives a list of dictionaries; `name in scope` would then test the list for a dictionary, which is never true, so no redeclaration is ever caught.",
                            "A fixed index into a stack that grows and shrinks. It names the second scope when there are three and does not exist at the top level, where the table is one deep.",
                            "The innermost scope, the last one pushed. Declaring there and objecting only from there is what makes an inner `let x` shadow an outer one instead of colliding with it.",
                        ],
                    },
                    {
                        "prompt": "In what order does a lookup visit the scopes?",
                        "hole": "?",
                        "opts": ["list", "reversed", "sorted", "enumerate"],
                        "a": 1,
                        "why": "Innermost first. The first dictionary containing the name wins, which means the nearest enclosing binding is the one a reference means — that is shadowing, implemented.",
                        "whys": [
                            "Outermost first: the global binding is found before the local one, so a parameter never shadows anything and a function reading `n` gets whichever `n` happened to be declared first.",
                            "Innermost first. The first dictionary containing the name wins, which means the nearest enclosing binding is the one a reference means — that is shadowing, implemented.",
                            "Python cannot order dictionaries at all, so this raises `TypeError` on the second scope — and even if it could, scope order is a fact about nesting rather than about the contents.",
                            "That yields `(index, scope)` pairs, so `name in scope` asks whether the name equals 0 or 1. It never matches and every lookup fails.",
                        ],
                    },
                    {
                        "prompt": "No scope had the name. What comes back?",
                        "hole": "?",
                        "opts": ["{}", "name", "None", "\"num\""],
                        "a": 2,
                        "why": "`None` is the sentinel every caller tests for before deciding whose error it is — an undefined variable, an undefined function, or an assignment to something never declared.",
                        "whys": [
                            "An empty dictionary is truthy-adjacent trouble: it is not `None`, so the caller's check passes, and a type that is a dictionary flows into the comparisons downstream.",
                            "Handing back the name says nothing about whether it was found, and the caller would compare a variable name against `\"num\"` and report a type error for a name that does not exist.",
                            "`None` is the sentinel every caller tests for before deciding whose error it is — an undefined variable, an undefined function, or an assignment to something never declared.",
                            "Returning a type makes every misspelled name a well-typed number. The program then fails at run time, in a place with no connection to the typo.",
                        ],
                    },
                    {
                        "prompt": "The two operands agree in type. What type does `==` produce?",
                        "hole": "?",
                        "opts": ["\"bool\"", "lt", "\"num\"", "rt"],
                        "a": 0,
                        "why": "A comparison answers a yes-or-no question, so its result is `bool` whatever went into it. The operand types were checked to be equal and are then done with — this is where a rule stops being about its inputs.",
                        "whys": [
                            "A comparison answers a yes-or-no question, so its result is `bool` whatever went into it. The operand types were checked to be equal and are then done with — this is where a rule stops being about its inputs.",
                            "Passing the operand type through says `\"a\" == \"b\"` is a string, so `if s == t` would then be rejected for having a non-`bool` condition — and `1 == 2` would quietly be usable as a number.",
                            "That is right by accident when both operands are numbers and wrong for every other comparison, which makes it the version that survives a shallow test suite.",
                            "Same mistake as passing the left type through, and identical in effect since the rule has already established that the two agree.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "What a name costs to look up",
                "minutes": 8,
                "brief": r"""
`lookup` walks the scope stack from the innermost dictionary outwards and stops at the
first one that has the name. So a reference is not free, and what it costs depends on
how far the name is from where it is used — the deeper the block, the more dictionaries
a reference to a global has to miss on the way out.

```text
let x = 1;                 # scope 1
while x < 9 {              # body opens scope 2
    let y = x + 1;
    if y > 3 {             # body opens scope 3
        let z = x + y;
        print z;
    }
}
```

Count a **probe** as one dictionary examined. A name found in the innermost scope
costs 1 probe; one found two scopes out costs 3, because two dictionaries were checked
and missed before the third answered.
""",
                "prompt": "How many probes does the checker make in total while checking this program?",
                "note": "Count only reads of a variable. A block's condition is checked *before* its body's scope is pushed, and `let` declares rather than looks up.",
                "figure": "`x` is bound at depth 1, `y` at depth 2, `z` at depth 3 — and every read starts at the innermost scope and walks out",
                "given": [
                    {"label": "Probe", "value": "one dictionary examined"},
                    {"label": "Counted", "value": "variable reads only"},
                    {"label": "`while` / `if` condition", "value": "checked in the enclosing scope"},
                    {"label": "Scopes at the top level", "value": "1"},
                ],
                "aside": "There are six reads in the program. Work out the depth each one happens at, "
                         "and how far out its name is bound.",
                "answer": 10,
                "tol": 0,
                "unit": "probes",
                "hint": "The reads are `x` in the `while` condition, `x` in `let y`, `y` in the `if` "
                        "condition, then `x` and `y` in `let z`, and `z` in the `print`. Each costs "
                        "the depth of the scope where it is bound, counted from the innermost open "
                        "scope inwards.",
                "wrong": "Two things to check. The `while` condition is checked before the loop body "
                         "opens its scope, so the `x` in it costs 1, not 2. And a name found in the "
                         "innermost scope costs a probe as well — the search still had to look.",
                "why": r"""
Six reads, at these depths:

| read | scopes open | bound in | probes |
| --- | --- | --- | --- |
| `x` in `x < 9` | 1 | 1 | 1 |
| `x` in `let y = x + 1` | 2 | 1 | 2 |
| `y` in `y > 3` | 2 | 2 | 1 |
| `x` in `let z = x + y` | 3 | 1 | 3 |
| `y` in `let z = x + y` | 3 | 2 | 2 |
| `z` in `print z` | 3 | 3 | 1 |

which is 10. The shape is what matters: the innermost block reads `x` at a cost of 3
and would read it at a cost of 12 from twelve blocks in. Real compilers do not pay
this — they run resolution once and rewrite each reference as a `(depth, slot)` pair,
or as a flat slot index, which is exactly what module 4's compiler does when it turns
every name into an integer at compile time. The scope stack is the specification of
what a name means; the slot number is the implementation.
""",
            },
            "lab": {
                "title": "A scoped symbol table and a type checker",
                "runtime": "python",
                "minutes": 70,
                "brief": r'''
The tree is given to you already built — the node constructors at the top of
`main.py` are what the checks use. Every node ends with a `pos` pair, and every
error you raise must repeat that position.

```text
Num(3)            -> ("num", 3, (1, 1))
Bin("+", l, r)    -> ("bin", "+", l, r, (1, 1))
Fn(name, params, ret, body)   params are (name, type) pairs
```

There are three types: `"num"`, `"str"`, `"bool"`. A function symbol is stored
as `("fn", [param types], return type)`, and `"void"` is the return type of a
function whose `return;` carries no value.

**`SymbolTable`** — `push`, `pop`, `depth`, `declare(name, type, pos)` and
`lookup(name)`. `declare` raises `SemanticError` when the name is already in the
**innermost** scope; `lookup` walks outwards and returns `None` when nothing
matches.

**`type_of(node, table)`** — the type of an expression, by these rules:

- `+ - * / % ^` need two `num` and give `num`; `+` also joins two `str`
- `< <= > >=` need two `num` and give `bool`
- `== !=` need two operands of the same type and give `bool`
- `&& ||` need two `bool` and give `bool`
- prefix `-` needs `num`, prefix `!` needs `bool`
- a call checks the arity first, then each argument against its parameter type

**`check(program)`** — hoist every top-level `fn` signature, then check each
statement, then return a dict of the global scope. `if` and `while` conditions
must be `bool` and their blocks get their own scope. `return` outside a function
is an error, as is a `return` whose type is not the declared one. Functions may
only be declared at the top level.

Raise `SemanticError(message, line, col)` for the **first** thing that is wrong.
''',
                "files": [{"name": "main.py", "content": r'''
# ------------------------------------------------- given: node constructors
def Num(v, pos=(1, 1)):        return ("num", v, pos)
def Str(v, pos=(1, 1)):        return ("str", v, pos)
def Bool(v, pos=(1, 1)):       return ("bool", v, pos)
def Var(name, pos=(1, 1)):     return ("var", name, pos)
def Unary(op, x, pos=(1, 1)):  return ("unary", op, x, pos)
def Bin(op, l, r, pos=(1, 1)): return ("bin", op, l, r, pos)
def Call(name, args, pos=(1, 1)):        return ("call", name, args, pos)
def Let(name, expr, pos=(1, 1)):         return ("let", name, expr, pos)
def Assign(name, expr, pos=(1, 1)):      return ("assign", name, expr, pos)
def Print(expr, pos=(1, 1)):             return ("print", expr, pos)
def ExprStmt(expr, pos=(1, 1)):          return ("expr", expr, pos)
def Return(expr, pos=(1, 1)):            return ("return", expr, pos)
def If(cond, then, els, pos=(1, 1)):     return ("if", cond, then, els, pos)
def While(cond, body, pos=(1, 1)):       return ("while", cond, body, pos)
def Fn(name, params, ret, body, pos=(1, 1)):
    return ("fn", name, params, ret, body, pos)


ARITHMETIC = {"+", "-", "*", "/", "%", "^"}
COMPARISON = {"<", "<=", ">", ">="}
EQUALITY = {"==", "!="}
LOGICAL = {"&&", "||"}


class SemanticError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message, self.line, self.col = message, line, col


# ------------------------------------------------------------- your code
class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def push(self):
        """Enter a new innermost scope."""
        # your code here

    def pop(self):
        """Leave the innermost scope. The global scope must survive."""
        # your code here

    def depth(self):
        """How many scopes are open; 1 at the top level."""
        # your code here

    def declare(self, name, type_, pos=(1, 1)):
        """Bind name in the innermost scope, or raise SemanticError."""
        # your code here

    def lookup(self, name):
        """Innermost binding for name, or None."""
        # your code here


def type_of(node, table):
    """The type of an expression node: num, str, bool, or a function's return type."""
    # your code here


def check_stmt(node, table, ret_type):
    """Check one statement. ret_type is None outside a function body."""
    # your code here


def check_block(stmts, table, ret_type):
    """Check a block in its own scope."""
    # your code here


def check(program):
    """Check a whole program and return the global scope as a dict."""
    # your code here


demo = [Fn("twice", [("n", "num")], "num", [Return(Bin("*", Var("n"), Num(2)))]),
        Let("x", Call("twice", [Num(21)])),
        Print(Var("x"))]
print(check(demo))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
# ------------------------------------------------- given: node constructors
def Num(v, pos=(1, 1)):        return ("num", v, pos)
def Str(v, pos=(1, 1)):        return ("str", v, pos)
def Bool(v, pos=(1, 1)):       return ("bool", v, pos)
def Var(name, pos=(1, 1)):     return ("var", name, pos)
def Unary(op, x, pos=(1, 1)):  return ("unary", op, x, pos)
def Bin(op, l, r, pos=(1, 1)): return ("bin", op, l, r, pos)
def Call(name, args, pos=(1, 1)):        return ("call", name, args, pos)
def Let(name, expr, pos=(1, 1)):         return ("let", name, expr, pos)
def Assign(name, expr, pos=(1, 1)):      return ("assign", name, expr, pos)
def Print(expr, pos=(1, 1)):             return ("print", expr, pos)
def ExprStmt(expr, pos=(1, 1)):          return ("expr", expr, pos)
def Return(expr, pos=(1, 1)):            return ("return", expr, pos)
def If(cond, then, els, pos=(1, 1)):     return ("if", cond, then, els, pos)
def While(cond, body, pos=(1, 1)):       return ("while", cond, body, pos)
def Fn(name, params, ret, body, pos=(1, 1)):
    return ("fn", name, params, ret, body, pos)


ARITHMETIC = {"+", "-", "*", "/", "%", "^"}
COMPARISON = {"<", "<=", ">", ">="}
EQUALITY = {"==", "!="}
LOGICAL = {"&&", "||"}


class SemanticError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message, self.line, self.col = message, line, col


# ------------------------------------------------------------- your code
class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def push(self):
        """Enter a new innermost scope."""
        self.scopes.append({})

    def pop(self):
        """Leave the innermost scope. The global scope must survive."""
        if len(self.scopes) == 1:
            raise RuntimeError("the global scope cannot be popped")
        self.scopes.pop()

    def depth(self):
        """How many scopes are open; 1 at the top level."""
        return len(self.scopes)

    def declare(self, name, type_, pos=(1, 1)):
        """Bind name in the innermost scope, or raise SemanticError."""
        scope = self.scopes[-1]
        if name in scope:
            raise SemanticError(f"{name!r} is already declared in this scope",
                                pos[0], pos[1])
        scope[name] = type_
        return type_

    def lookup(self, name):
        """Innermost binding for name, or None."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None


def type_of(node, table):
    """The type of an expression node: num, str, bool, or a function's return type."""
    kind = node[0]
    if kind in ("num", "str", "bool"):
        return kind
    if kind == "var":
        _, name, pos = node
        found = table.lookup(name)
        if found is None:
            raise SemanticError(f"undefined variable {name!r}", pos[0], pos[1])
        if isinstance(found, tuple):
            raise SemanticError(f"{name!r} is a function, not a value", pos[0], pos[1])
        return found
    if kind == "unary":
        _, op, operand, pos = node
        actual = type_of(operand, table)
        if op == "-" and actual != "num":
            raise SemanticError(f"cannot negate {actual}", pos[0], pos[1])
        if op == "!" and actual != "bool":
            raise SemanticError(f"cannot apply '!' to {actual}", pos[0], pos[1])
        return actual
    if kind == "bin":
        _, op, left, right, pos = node
        lt = type_of(left, table)
        rt = type_of(right, table)
        if op in ARITHMETIC:
            if op == "+" and lt == "str" and rt == "str":
                return "str"
            if lt == "num" and rt == "num":
                return "num"
            raise SemanticError(f"cannot apply {op!r} to {lt} and {rt}", pos[0], pos[1])
        if op in COMPARISON:
            if lt == "num" and rt == "num":
                return "bool"
            raise SemanticError(f"cannot apply {op!r} to {lt} and {rt}", pos[0], pos[1])
        if op in EQUALITY:
            if lt != rt:
                raise SemanticError(f"cannot compare {lt} with {rt}", pos[0], pos[1])
            return "bool"
        if op in LOGICAL:
            if lt == "bool" and rt == "bool":
                return "bool"
            raise SemanticError(f"cannot apply {op!r} to {lt} and {rt}", pos[0], pos[1])
        raise SemanticError(f"unknown operator {op!r}", pos[0], pos[1])
    if kind == "call":
        _, name, args, pos = node
        found = table.lookup(name)
        if found is None:
            raise SemanticError(f"undefined function {name!r}", pos[0], pos[1])
        if not isinstance(found, tuple) or found[0] != "fn":
            raise SemanticError(f"{name!r} is not a function", pos[0], pos[1])
        _, params, ret = found
        if len(args) != len(params):
            raise SemanticError(
                f"{name!r} takes {len(params)} argument(s), {len(args)} given",
                pos[0], pos[1])
        for index, (arg, want) in enumerate(zip(args, params), start=1):
            got = type_of(arg, table)
            if got != want:
                raise SemanticError(
                    f"argument {index} of {name!r} is {got}, expected {want}",
                    pos[0], pos[1])
        return ret
    raise SemanticError(f"unknown expression {kind!r}", 1, 1)


def require_bool(expr, table, what):
    """Every condition in the language must be a bool."""
    actual = type_of(expr, table)
    if actual != "bool":
        pos = expr[-1]
        raise SemanticError(f"{what} condition must be bool, found {actual}",
                            pos[0], pos[1])


def check_stmt(node, table, ret_type):
    """Check one statement. ret_type is None outside a function body."""
    kind = node[0]
    if kind == "let":
        _, name, expr, pos = node
        table.declare(name, type_of(expr, table), pos)
    elif kind == "assign":
        _, name, expr, pos = node
        declared = table.lookup(name)
        if declared is None:
            raise SemanticError(f"undefined variable {name!r}", pos[0], pos[1])
        if isinstance(declared, tuple):
            raise SemanticError(f"{name!r} is a function, not a value", pos[0], pos[1])
        actual = type_of(expr, table)
        if actual != declared:
            raise SemanticError(
                f"cannot assign {actual} to {declared} variable {name!r}",
                pos[0], pos[1])
    elif kind in ("print", "expr"):
        type_of(node[1], table)
    elif kind == "if":
        _, cond, then_stmts, else_stmts, pos = node
        require_bool(cond, table, "if")
        check_block(then_stmts, table, ret_type)
        check_block(else_stmts, table, ret_type)
    elif kind == "while":
        _, cond, body, pos = node
        require_bool(cond, table, "while")
        check_block(body, table, ret_type)
    elif kind == "return":
        _, expr, pos = node
        if ret_type is None:
            raise SemanticError("return outside a function", pos[0], pos[1])
        actual = "void" if expr is None else type_of(expr, table)
        if actual != ret_type:
            raise SemanticError(f"this function returns {ret_type}, not {actual}",
                                pos[0], pos[1])
    elif kind == "fn":
        _, name, params, ret, body, pos = node
        if table.depth() > 1:
            raise SemanticError("functions may only be declared at the top level",
                                pos[0], pos[1])
        table.push()
        for pname, ptype in params:
            table.declare(pname, ptype, pos)
        for stmt in body:
            check_stmt(stmt, table, ret)
        table.pop()
    else:
        raise SemanticError(f"unknown statement {kind!r}", 1, 1)


def check_block(stmts, table, ret_type):
    """Check a block in its own scope."""
    table.push()
    for stmt in stmts:
        check_stmt(stmt, table, ret_type)
    table.pop()


def check(program):
    """Check a whole program and return the global scope as a dict."""
    table = SymbolTable()
    for node in program:
        if node[0] == "fn":
            _, name, params, ret, body, pos = node
            table.declare(name, ("fn", [t for _n, t in params], ret), pos)
    for node in program:
        check_stmt(node, table, None)
    return dict(table.scopes[0])


demo = [Fn("twice", [("n", "num")], "num", [Return(Bin("*", Var("n"), Num(2)))]),
        Let("x", Call("twice", [Num(21)])),
        Print(Var("x"))]
print(check(demo))
'''}],
                "hints": [
                    "`lookup` walks `reversed(self.scopes)` and returns the first hit; `declare` only ever inspects `self.scopes[-1]`. That one-line difference is the whole shadowing rule.",
                    "`type_of` is a dispatch on `node[0]` that recurses into the children first and then applies one rule per operator group. Every raise uses the node's own `pos`.",
                    "Blocks get `table.push()` before and `table.pop()` after — put that in `check_block` and call it from both branches of `if` as well as from `while`.",
                    "Hoist in a first loop over the program (`table.declare(name, ('fn', [t for _n, t in params], ret), pos)`) and only then check bodies, otherwise mutual recursion cannot type.",
                ],
                "tests": [
                    {"name": "SymbolTable: scopes, shadowing and redeclaration", "code": r'''
_t = SymbolTable()
assert _t.depth() == 1, f"a fresh table has depth {_t.depth()!r}, expected 1"
_t.declare("x", "num")
_got = _t.lookup("x")
assert _got == "num", f"lookup of x gave {_got!r}, expected 'num'"
assert _t.lookup("nope") is None, "an unknown name looks up to None"
_t.push()
assert _t.depth() == 2, f"after push, depth is {_t.depth()!r}, expected 2"
_t.declare("x", "str")
assert _t.lookup("x") == "str", "the inner binding shadows the outer one"
_t.declare("y", "bool")
_t.pop()
assert _t.lookup("x") == "num", "popping restores the outer binding"
assert _t.lookup("y") is None, "a name declared in a popped scope is gone"
try:
    _t.declare("x", "bool", (4, 2))
    assert False, "redeclaring x in the same scope should raise SemanticError"
except SemanticError as _e:
    assert (_e.line, _e.col) == (4, 2), f"error reported {_e.line}:{_e.col}, expected 4:2"
'''},
                    {"name": "Types of literals, arithmetic and comparison", "code": r'''
_prog = [Let("a", Num(1)),
         Let("b", Bin("+", Var("a"), Num(2))),
         Let("s", Bin("+", Str("x"), Str("y"))),
         Let("t", Bin("<", Var("a"), Var("b"))),
         Let("u", Unary("-", Var("a"))),
         Let("v", Unary("!", Var("t"))),
         Let("w", Bin("&&", Var("t"), Var("v")))]
_g = check(_prog)
_want = {"a": "num", "b": "num", "s": "str", "t": "bool",
         "u": "num", "v": "bool", "w": "bool"}
assert _g == _want, f"check() gave {_g!r}, expected {_want!r}"
'''},
                    {"name": "Undefined names and redeclaration carry a position", "code": r'''
try:
    check([Print(Var("nope", (7, 3)))])
    assert False, "using an undeclared variable should raise SemanticError"
except SemanticError as _e:
    assert (_e.line, _e.col) == (7, 3), f"reported {_e.line}:{_e.col}, expected 7:3"
try:
    check([Let("x", Num(1)), Let("x", Num(2), (5, 1))])
    assert False, "declaring x twice in one scope should raise SemanticError"
except SemanticError as _e:
    assert (_e.line, _e.col) == (5, 1), f"reported {_e.line}:{_e.col}, expected 5:1"
try:
    check([Assign("q", Num(1), (2, 4))])
    assert False, "assigning to an undeclared variable should raise SemanticError"
except SemanticError as _e:
    assert (_e.line, _e.col) == (2, 4), f"reported {_e.line}:{_e.col}, expected 2:4"
try:
    check([Let("x", Num(1)), Assign("x", Str("s"))])
    assert False, "assigning a str to a num variable should raise SemanticError"
except SemanticError:
    pass
'''},
                    {"name": "Operator typing rules", "code": r'''
for _expr in [Bin("+", Num(1), Bool(True)), Bin("-", Str("a"), Str("b")),
              Bin("<", Str("a"), Str("b")), Bin("==", Num(1), Str("a")),
              Bin("&&", Bool(True), Num(1)), Unary("-", Str("a")),
              Unary("!", Num(1))]:
    try:
        check([Print(_expr)])
        assert False, f"{_expr!r} should raise SemanticError"
    except SemanticError:
        pass
_g = check([Let("p", Bin("==", Str("a"), Str("b"))),
            Let("q", Bin("!=", Bool(True), Bool(False)))])
assert _g == {"p": "bool", "q": "bool"}, f"equality on equal types gives bool, got {_g!r}"
'''},
                    {"name": "Conditions must be bool, and blocks have their own scope", "code": r'''
for _bad in [If(Num(1, (3, 5)), [], []), While(Str("x", (4, 2)), [])]:
    try:
        check([_bad])
        assert False, "a non-bool condition should raise SemanticError"
    except SemanticError as _e:
        assert "bool" in _e.message, f"message was {_e.message!r}"
check([Let("x", Num(1)),
       If(Bool(True), [Let("x", Str("inner")), Print(Var("x"))], []),
       Print(Var("x"))])
try:
    check([If(Bool(True), [Let("inner", Num(1))], []), Print(Var("inner"))])
    assert False, "a name declared inside a block should not escape it"
except SemanticError as _e:
    assert "inner" in _e.message, f"message was {_e.message!r}"
'''},
                    {"name": "Function signatures, calls and returns", "code": r'''
_sig = [("a", "num"), ("b", "num")]
_body = [Return(Bin("+", Var("a"), Var("b")))]
_g = check([Fn("add", _sig, "num", _body),
            Let("x", Call("add", [Num(1), Num(2)])),
            Print(Var("x"))])
assert _g["add"] == ("fn", ["num", "num"], "num"), f"add was recorded as {_g['add']!r}"
assert _g["x"] == "num", f"x typed as {_g['x']!r}, expected num"
for _call in [Call("add", [Num(1)]), Call("add", [Num(1), Str("x")]), Call("nope", [])]:
    try:
        check([Fn("add", _sig, "num", _body), Print(_call)])
        assert False, f"{_call!r} should raise SemanticError"
    except SemanticError:
        pass
try:
    check([Fn("f", [], "num", [Return(Str("a"))])])
    assert False, "returning a str from a num function should raise SemanticError"
except SemanticError:
    pass
try:
    check([Return(Num(1), (2, 1))])
    assert False, "return outside a function should raise SemanticError"
except SemanticError as _e:
    assert (_e.line, _e.col) == (2, 1), f"reported {_e.line}:{_e.col}, expected 2:1"
try:
    check([If(Bool(True), [Fn("g", [], "num", [Return(Num(1))])], [])])
    assert False, "a nested function declaration should raise SemanticError"
except SemanticError:
    pass
'''},
                    {"name": "Hoisting allows mutual recursion; the first error wins", "code": r'''
_g = check([Fn("even", [("n", "num")], "bool", [Return(Call("odd", [Var("n")]))]),
            Fn("odd", [("n", "num")], "bool", [Return(Call("even", [Var("n")]))])])
assert _g["even"] == ("fn", ["num"], "bool"), f"even recorded as {_g['even']!r}"
try:
    check([Let("x", Num(1)), Print(Var("y", (7, 3))), Print(Var("z", (9, 1)))])
    assert False, "the program has two undefined names and should raise"
except SemanticError as _e:
    assert (_e.line, _e.col) == (7, 3), \
        f"reported {_e.line}:{_e.col}, expected the FIRST error at 7:3"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Code generation and a stack virtual machine",
            "summary": "Flattening the tree into instructions, and the machine that runs them.",
            "concepts": [
                "A stack machine needs no register allocator: an expression tree becomes its postorder traversal",
                "Control flow is jumps to addresses that are not known yet, so every branch needs backpatching",
                "A `while` loop is a backward jump; an `if` is a forward jump over the alternative",
                "Locals live in a frame indexed by slot number, decided once at compile time",
                "A call pushes a frame with the arguments already in slots 0..n-1 and records the return address",
                "Short-circuit `&&` and `||` are control flow, not operators — they compile to jumps",
                "An interpreter loop needs a step budget: a compiler must not be able to hang the machine forever",
            ],
            "quiz": {
                "title": "Instructions, jumps and frames",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why does compiling an expression to this machine need no register allocation?",
                        "opts": [
                            "The postorder traversal is already a correct instruction sequence: every operator finds its operands on top of the stack, whatever produced them",
                            "The VM has an unlimited supply of registers, so allocation always succeeds",
                            "The compiler gives every subexpression a slot in the frame, which is allocation done cheaply",
                            "Because operands are pushed in reverse order, which removes the need to name them",
                        ],
                        "a": 0,
                        "why": r"""
The stack is the answer to *where does this intermediate value live*, and it answers
the same way for every subexpression, so there is nothing to decide. Emit the left
subtree, emit the right subtree, emit the operator: the operator's operands are the
top two entries by construction. On a register machine that question has a different
answer each time and a finite supply of answers, which is where allocation, spilling
and Sethi-Ullman numbering come from. The price paid here is that values are addressed
by position rather than by name, so the same value cannot be reused without being
recomputed or stored — which is one reason real bytecode VMs still lower to registers
before they emit machine code.
""",
                    },
                    {
                        "q": "The compiler emits `(\"JZ\", 0)` and overwrites the 0 later. Why not emit the real address straight away?",
                        "opts": [
                            "The target is the address just past the then-branch, and that is not known until the then-branch has been emitted",
                            "Because instruction addresses shift as later code is added",
                            "Because `JZ` cannot take an argument until the condition has been compiled",
                            "To keep every instruction the same size in the list",
                        ],
                        "a": 0,
                        "why": r"""
A forward jump names a place the compiler has not reached yet. `emit` returns the
address of the instruction it just appended precisely so that address can be kept and
the slot rewritten once `len(self.code)` finally *is* the target — that is
backpatching, and it is why the code list is mutable. Nothing shifts: this compiler
appends and never inserts, so an address, once assigned, is stable. A backward jump
needs none of this, which is why the `while` loop records `start = len(self.code)`
before the test and jumps straight to it.
""",
                    },
                    {
                        "q": "`&&` compiles to `JZ` and `JMP` rather than to a `BIN`. What would a `BIN` change?",
                        "opts": [
                            "Both operands would always be evaluated, so a guard such as `n != 0 && 10 / n > 1` would divide by zero when `n` is 0",
                            "Nothing, for `&&` — only `||` genuinely needs the jumps",
                            "The result would be a number rather than a `bool`",
                            "The operands would be evaluated in the wrong order",
                        ],
                        "a": 0,
                        "why": r"""
`BIN` is a strict operator: its operands are on the stack before it runs, so both were
evaluated, so the guard has already failed to guard. Short-circuiting is not an
optimisation — it is part of what `&&` *means* in this language, and it is control
flow, so it compiles to control flow. `||` is the mirror image and needs the jumps for
the same reason. Look at the emitted shape and the asymmetry is visible: the false
branch pushes the constant `False` and never touches the right operand at all.
""",
                    },
                    {
                        "q": "An instruction reads `(\"LOAD\", 2)`. What is the 2, and when was it decided?",
                        "opts": [
                            "A slot in the current frame's locals, fixed at compile time by `declare`",
                            "An offset from the top of the stack, computed as the VM runs",
                            "An index into the global variable table, filled in when the program starts",
                            "The address of the instruction that stored the value",
                        ],
                        "a": 0,
                        "why": r"""
`declare` hands out slot numbers as names are first mentioned, and `ENTER` pads the
frame to hold them, so by run time a variable is an integer index into a list — one
array read, no name lookup, no scope walk. That is what module 3's scope stack is
*for*: it settles what each name means so this pass can throw the names away. Note the
consequence in this design: each function gets its own flat slot space and there are
no globals, so `LOAD 2` in one function and `LOAD 2` in another are unrelated, and the
frame pushed by `CALL` is what keeps them apart.
""",
                    },
                    {
                        "q": "`VM.run` counts steps and raises once the budget is exhausted. What is that for?",
                        "opts": [
                            "A compiled program can loop forever, and a runtime hosted inside a page must not be able to hang it",
                            "It detects infinite loops, which is what makes the compiler safe",
                            "It measures how fast the generated code is, for the optimiser to compare against",
                            "It bounds the recursion depth, which Python would otherwise exceed",
                        ],
                        "a": 0,
                        "why": r"""
It is a budget, not an analysis. `while true { }` is a perfectly legal program and no
compiler can decide in general whether an arbitrary one terminates, so the runtime
takes the other route: bound the work, then fail with a message that says so. The
distinction matters because a step limit will also stop a program that was merely slow,
and cannot tell you which case it just hit. The recursion depth is a separate concern
and is bounded separately — frames live in a Python list here, not on the Python call
stack, so a deep call chain in the compiled language costs memory rather than a
`RecursionError`.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Read the bytecode back",
                "minutes": 9,
                "caption": "the code for: let i = 1; while i <= 3 { i = i + 1; } print i;",
                "lang": "text",
                "brief": r"""
Three statements, fifteen instructions, and every piece of structure in the source has
become an address. The loop is a backward jump, the exit is a forward jump that was
patched once the body had been emitted, and the variable `i` has stopped being a name.

Fill the four holes. Addresses are absolute, and the instruction at address 14 is the
last one in the program.
""",
                "listing": """addr  instruction        source
  0   ENTER  1           # one local slot, for i
  1   PUSH   1
  2   STORE  0           # let i = 1;
  3   LOAD   0           # while i <= 3 {   <- the test starts here
  4   PUSH   3
  5   BIN    "<="
  6   JZ     ___         #   ... and this is where the loop leaves
  7   LOAD   0
  8   PUSH   1
  9   BIN    "+"
 10   STORE  ___         #   i = i + 1;
 11   JMP    ___         # }
 12   LOAD   0
 13   ___    None        # print i;
 14   HALT   None
""",
                "blanks": [
                    {
                        "prompt": "The test was false. Where does `JZ` send the machine?",
                        "hole": "?",
                        "opts": ["12", "11", "13", "3"],
                        "a": 0,
                        "why": "Past the whole loop — the body ends with the backward jump at 11, so the first instruction that is not part of the loop is 12. That address was unknown when the `JZ` was emitted, which is why it was patched afterwards.",
                        "whys": [
                            "Past the whole loop — the body ends with the backward jump at 11, so the first instruction that is not part of the loop is 12. That address was unknown when the `JZ` was emitted, which is why it was patched afterwards.",
                            "Landing on the backward jump runs it, which sends the machine straight back to the test it just failed. The loop becomes infinite and the step budget is what finally stops it.",
                            "One too far: the `LOAD 0` that fetches `i` for the `print` is skipped, so `PRINT` pops whatever happens to be on the stack — and on an empty stack that is a crash rather than a wrong number.",
                            "That is the top of the test, which is where the loop goes when it continues. Sending the *false* case there means the loop never ends.",
                        ],
                    },
                    {
                        "prompt": "The new value of `i` is on the stack. Where does it go?",
                        "hole": "?",
                        "opts": ["i", "3", "0", "1"],
                        "a": 2,
                        "why": "Slot 0 — the same slot the `LOAD` at address 7 read from, because `i` is the only local and `declare` gave it the first slot. `ENTER 1` is what reserved it.",
                        "whys": [
                            "The name is gone by this point in the pipeline. Slots are integers precisely so the VM never has to look a name up.",
                            "3 is the constant the loop compares against, and it appears here only because it is nearby. Slot numbers and literal values have nothing to do with each other.",
                            "Slot 0 — the same slot the `LOAD` at address 7 read from, because `i` is the only local and `declare` gave it the first slot. `ENTER 1` is what reserved it.",
                            "There is no slot 1: `ENTER 1` padded the frame to exactly one slot, so this is an index error at run time rather than a wrong answer.",
                        ],
                    },
                    {
                        "prompt": "The body is finished. Where does the loop go next?",
                        "hole": "?",
                        "opts": ["7", "3", "0", "6"],
                        "a": 1,
                        "why": "Back to the top of the *test*, at 3. A loop re-checks its condition on every turn, and the address was recorded before the condition was compiled — a backward jump needs no patching because its target is already behind it.",
                        "whys": [
                            "Skipping the test and re-entering the body is a loop with no exit: `i` climbs past 3 and nothing ever looks.",
                            "Back to the top of the *test*, at 3. A loop re-checks its condition on every turn, and the address was recorded before the condition was compiled — a backward jump needs no patching because its target is already behind it.",
                            "Address 0 re-runs `ENTER` and then `PUSH 1; STORE 0`, which resets `i` to 1 on every turn. The condition is then always true and the loop never ends.",
                            "Jumping to the `JZ` itself skips the three instructions at 3, 4 and 5 that compute the condition, so it pops whatever is on the stack instead — and there is nothing on it, since the body left nothing behind.",
                        ],
                    },
                    {
                        "prompt": "The value of `i` has just been loaded. What consumes it?",
                        "hole": "?",
                        "opts": ["POP", "STORE", "RET", "PRINT"],
                        "a": 3,
                        "why": "`PRINT` pops one value and records `format_value` of it, which is how `print i;` gets its output. Every statement leaves the stack as it found it, and this is the instruction that balances the `LOAD` before it.",
                        "whys": [
                            "`POP` also removes the value and leaves the stack balanced — which is exactly what makes it dangerous here. The program runs to completion and prints nothing, and that is what an expression statement compiles to.",
                            "`STORE` needs a slot to write into and would consume the value without producing output, turning a print into an assignment to whatever slot came to hand.",
                            "`RET` belongs to a function body: it drops a frame and hands a value back to a caller. At the top level there is no caller, and the VM says so.",
                            "`PRINT` pops one value and records `format_value` of it, which is how `print i;` gets its output. Every statement leaves the stack as it found it, and this is the instruction that balances the `LOAD` before it.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "What an expression costs on a stack machine",
                "minutes": 13,
                "vars": ["n", "k", "D", "L"],
                "brief": r"""
Take an expression that is one perfectly balanced binary tree — every internal node an
operator with two children, every leaf a literal or a variable, and both subtrees of
every node the same height. For $k = 2$ that is `(a + b) * (c + d)`.

Compiled by module 4's back end, each leaf becomes one instruction (`PUSH` or `LOAD`)
and each internal node becomes one `BIN`. Two questions follow: how long is the code,
and how deep does the stack get while running it?
""",
                "steps": [
                    {
                        "prompt": "The tree has $n$ leaves and every internal node has exactly two children. How many internal nodes are there? Write it in terms of $n$.",
                        "answer": "n - 1",
                        "hint": "Think of it as merging. You start with $n$ separate leaves and finish with one tree; count the merges.",
                        "deconstruct": [
                            "Start with the $n$ leaves as $n$ separate pieces.",
                            "Every internal node joins two pieces into one, so each one reduces the count of pieces by exactly one.",
                            "Going from $n$ pieces to $1$ therefore takes $n - 1$ of them.",
                        ],
                    },
                    {
                        "prompt": "Each leaf emits one instruction and each internal node emits one `BIN`. Write the total instruction count $L$ for the expression, in terms of $n$.",
                        "given": "There are $n$ leaves and the internal-node count you just found.",
                        "answer": "2n - 1",
                        "hint": "Add the two counts. Nothing else is emitted — there are no jumps in a plain expression.",
                        "deconstruct": [
                            "$n$ leaves give $n$ push-like instructions.",
                            "$n - 1$ internal nodes give $n - 1$ `BIN` instructions.",
                            "$n + (n - 1) = 2n - 1$, which is also just the number of nodes in the tree.",
                        ],
                    },
                    {
                        "prompt": "Now use the balance. The tree has height $k$, where $k = 0$ is a single leaf. Write the number of leaves $n$ in terms of $k$.",
                        "answer": "2^{k}",
                        "placeholder": "a power of 2",
                        "hint": "Each level down doubles the number of nodes, and the leaves are the bottom level.",
                        "deconstruct": [
                            "Height 0 is one leaf; height 1 is two; height 2 is four.",
                            "Each extra level replaces every leaf with two, doubling the count.",
                            "After $k$ doublings from a single node: $2^k$.",
                        ],
                    },
                    {
                        "prompt": "Substitute, and write the instruction count $L$ in terms of the height $k$.",
                        "answer": "2^{k+1} - 1",
                        "hint": "Put $n = 2^k$ into the count you derived, and fold the factor of 2 into the exponent.",
                        "deconstruct": [
                            "$L = 2n - 1$ and $n = 2^k$.",
                            "$2 \\cdot 2^k = 2^{k+1}$.",
                            "So $L = 2^{k+1} - 1$ — one instruction per node, and that is the number of nodes in a full binary tree of height $k$.",
                        ],
                    },
                    {
                        "prompt": "Now the peak stack depth. Both subtrees of the root are balanced of height $k-1$, and each peaks at $D$ on its own. The right subtree runs with the left subtree's single result already sitting on the stack. Write the root's peak depth in terms of $D$.",
                        "given": "Evaluating a subtree peaks at $D$ and finishes having left exactly one value behind.",
                        "answer": "D + 1",
                        "hint": "The left side reaches $D$ and leaves one value. The right side then reaches its own $D$ on top of that one value.",
                        "deconstruct": [
                            "The left subtree runs first: peak $D$, then one value remains.",
                            "The right subtree runs on top of that leftover, so its peak of $D$ becomes $D + 1$ overall.",
                            "The `BIN` then pops two and pushes one, which is below the peak already reached — so the peak is $D + 1$.",
                        ],
                    },
                    {
                        "prompt": "A single leaf peaks at a depth of 1. Solve that recurrence: write the peak depth of the balanced tree of height $k$, in terms of $k$.",
                        "answer": "k + 1",
                        "hint": "Every level of the tree adds exactly one, and the base case at $k = 0$ is 1.",
                        "deconstruct": [
                            "Depth at $k = 0$ is 1.",
                            "Each step up the tree adds 1, by the relation you just wrote.",
                            "After $k$ steps: $k + 1$.",
                        ],
                    },
                ],
                "closing": r"""
So the balanced tree over $n = 2^k$ leaves compiles to $2n - 1$ instructions and peaks
at $k + 1 = \log_2 n + 1$ stack entries.

Now compare the chain the parser actually builds from `1 + 2 + 3 + ... + n`. Left
associativity leans it all the way over, so the right operand of every operator is a
single leaf: the code is *the same length*, $2n - 1$, and the machine does the same
work — but the peak depth is 2 no matter how long the expression is, because each
`BIN` fires as soon as its two operands exist. Shape does not change the instruction
count; it changes only how much has to be held at once.

Both numbers are worth having. The depth is what a VM needs in order to size a stack
in advance instead of growing one, and on a register machine the same quantity is the
number of registers the expression needs before anything spills to memory — which is
Sethi-Ullman numbering, computed from exactly this recurrence.
""",
            },
            "lab": {
                "title": "Compile to bytecode and run it",
                "runtime": "python",
                "minutes": 80,
                "brief": r'''
Write the back end: `Compiler.compile(program)` turns the tree into a flat list
of `(op, arg)` instructions, and `VM.run(code)` executes them, returning the
list of printed lines.

The instruction set:

| instruction | effect |
| --- | --- |
| `("ENTER", n)` | pad the current frame's locals out to `n` slots |
| `("PUSH", v)` | push the constant `v` |
| `("LOAD", i)` | push local slot `i` |
| `("STORE", i)` | pop into local slot `i` |
| `("POP", None)` | discard the top of the stack |
| `("BIN", op)` | pop right, pop left, push `left op right` |
| `("NEG", None)` / `("NOT", None)` | unary minus / logical not |
| `("JMP", t)` | jump to address `t` |
| `("JZ", t)` | pop; jump to `t` when the value is falsey |
| `("CALL", (addr, nargs))` | pop `nargs` arguments into a new frame, jump to `addr` |
| `("RET", None)` | pop the result, drop the frame, push the result on the caller's stack |
| `("PRINT", None)` | pop and record `format_value(...)` |
| `("HALT", None)` | stop, returning the output |

Layout: the main body is compiled first, ending in `HALT`, and the function
bodies follow it. A `CALL` is emitted with the function *name* and patched to
its address once every body is placed. Each function gets its own flat slot
space; there are no globals, so a function sees only its parameters and its own
locals.

```text
Compiler().compile([Let("x", Num(1)), Print(Var("x"))])
  [("ENTER", 1), ("PUSH", 1), ("STORE", 0),
   ("LOAD", 0), ("PRINT", None), ("HALT", None)]
```

`&&` and `||` must not evaluate their right operand unless they have to:
compile them with `JZ` / `JMP`, not with `BIN`.

Raise `CompileError` for an undefined variable, an unknown function, or a call
with the wrong number of arguments. Raise `VMError` for division by zero, a
program counter off the end of the code, or exceeding `max_steps`.
''',
                "files": [{"name": "main.py", "content": r'''
# ------------------------------------------------- given: node constructors
def Num(v, pos=(1, 1)):        return ("num", v, pos)
def Str(v, pos=(1, 1)):        return ("str", v, pos)
def Bool(v, pos=(1, 1)):       return ("bool", v, pos)
def Var(name, pos=(1, 1)):     return ("var", name, pos)
def Unary(op, x, pos=(1, 1)):  return ("unary", op, x, pos)
def Bin(op, l, r, pos=(1, 1)): return ("bin", op, l, r, pos)
def Call(name, args, pos=(1, 1)):        return ("call", name, args, pos)
def Let(name, expr, pos=(1, 1)):         return ("let", name, expr, pos)
def Assign(name, expr, pos=(1, 1)):      return ("assign", name, expr, pos)
def Print(expr, pos=(1, 1)):             return ("print", expr, pos)
def ExprStmt(expr, pos=(1, 1)):          return ("expr", expr, pos)
def Return(expr, pos=(1, 1)):            return ("return", expr, pos)
def If(cond, then, els, pos=(1, 1)):     return ("if", cond, then, els, pos)
def While(cond, body, pos=(1, 1)):       return ("while", cond, body, pos)
def Fn(name, params, ret, body, pos=(1, 1)):
    return ("fn", name, params, ret, body, pos)


class CompileError(Exception):
    pass


class VMError(Exception):
    pass


def format_value(value):
    """How the machine prints a value. Booleans first: True is also an int."""
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# ------------------------------------------------------------- your code
class Compiler:
    def __init__(self):
        self.code = []
        self.functions = {}   # name -> (address, arity)
        self.scope = {}       # name -> slot, for the function being compiled

    def emit(self, op, arg=None):
        """Append one instruction and return its address."""
        self.code.append((op, arg))
        return len(self.code) - 1

    def declare(self, name):
        """Slot for a local, allocating one if this is its first mention."""
        # your code here

    def resolve(self, name):
        """Slot of an existing local, or CompileError."""
        # your code here

    def compile(self, program):
        """Main body, then HALT, then every function body; finally patch calls."""
        # your code here

    def compile_function(self, node):
        """Compile one fn node into its own frame at the end of the code."""
        # your code here

    def compile_stmt(self, node):
        """Emit the instructions for one statement."""
        # your code here

    def compile_expr(self, node):
        """Emit instructions leaving exactly one value on the stack."""
        # your code here


class VM:
    def __init__(self, max_steps=200000):
        self.max_steps = max_steps
        self.output = []

    def binary(self, op, left, right):
        """Apply one BIN operator, raising VMError on division by zero."""
        # your code here

    def run(self, code):
        """Execute from address 0 until HALT; return the printed lines."""
        # your code here


def run_program(program, max_steps=200000):
    return VM(max_steps=max_steps).run(Compiler().compile(program))


demo = [Let("i", Num(1)), Let("total", Num(0)),
        While(Bin("<=", Var("i"), Num(5)),
              [Assign("total", Bin("+", Var("total"), Var("i"))),
               Assign("i", Bin("+", Var("i"), Num(1)))]),
        Print(Var("total"))]
for line in run_program(demo):
    print(line)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
# ------------------------------------------------- given: node constructors
def Num(v, pos=(1, 1)):        return ("num", v, pos)
def Str(v, pos=(1, 1)):        return ("str", v, pos)
def Bool(v, pos=(1, 1)):       return ("bool", v, pos)
def Var(name, pos=(1, 1)):     return ("var", name, pos)
def Unary(op, x, pos=(1, 1)):  return ("unary", op, x, pos)
def Bin(op, l, r, pos=(1, 1)): return ("bin", op, l, r, pos)
def Call(name, args, pos=(1, 1)):        return ("call", name, args, pos)
def Let(name, expr, pos=(1, 1)):         return ("let", name, expr, pos)
def Assign(name, expr, pos=(1, 1)):      return ("assign", name, expr, pos)
def Print(expr, pos=(1, 1)):             return ("print", expr, pos)
def ExprStmt(expr, pos=(1, 1)):          return ("expr", expr, pos)
def Return(expr, pos=(1, 1)):            return ("return", expr, pos)
def If(cond, then, els, pos=(1, 1)):     return ("if", cond, then, els, pos)
def While(cond, body, pos=(1, 1)):       return ("while", cond, body, pos)
def Fn(name, params, ret, body, pos=(1, 1)):
    return ("fn", name, params, ret, body, pos)


class CompileError(Exception):
    pass


class VMError(Exception):
    pass


def format_value(value):
    """How the machine prints a value. Booleans first: True is also an int."""
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


# ------------------------------------------------------------- your code
class Compiler:
    def __init__(self):
        self.code = []
        self.functions = {}   # name -> (address, arity)
        self.scope = {}       # name -> slot, for the function being compiled

    def emit(self, op, arg=None):
        """Append one instruction and return its address."""
        self.code.append((op, arg))
        return len(self.code) - 1

    def declare(self, name):
        """Slot for a local, allocating one if this is its first mention."""
        if name not in self.scope:
            self.scope[name] = len(self.scope)
        return self.scope[name]

    def resolve(self, name):
        """Slot of an existing local, or CompileError."""
        if name not in self.scope:
            raise CompileError(f"undefined variable {name!r}")
        return self.scope[name]

    def compile(self, program):
        """Main body, then HALT, then every function body; finally patch calls."""
        self.scope = {}
        enter = self.emit("ENTER", 0)
        for node in program:
            if node[0] != "fn":
                self.compile_stmt(node)
        self.emit("HALT")
        self.code[enter] = ("ENTER", len(self.scope))
        for node in program:
            if node[0] == "fn":
                self.compile_function(node)
        for address, (op, arg) in enumerate(self.code):
            if op == "CALL" and isinstance(arg[0], str):
                name, nargs = arg
                if name not in self.functions:
                    raise CompileError(f"call to undefined function {name!r}")
                target, arity = self.functions[name]
                if arity != nargs:
                    raise CompileError(
                        f"{name!r} takes {arity} argument(s), {nargs} given")
                self.code[address] = ("CALL", (target, nargs))
        return self.code

    def compile_function(self, node):
        """Compile one fn node into its own frame at the end of the code."""
        _, name, params, ret, body, pos = node
        outer = self.scope
        self.scope = {}
        address = len(self.code)
        enter = self.emit("ENTER", 0)
        for pname, _ptype in params:
            self.declare(pname)
        self.functions[name] = (address, len(params))
        for stmt in body:
            self.compile_stmt(stmt)
        self.emit("PUSH", 0)
        self.emit("RET")
        self.code[enter] = ("ENTER", len(self.scope))
        self.scope = outer

    def compile_stmt(self, node):
        """Emit the instructions for one statement."""
        kind = node[0]
        if kind == "let":
            self.compile_expr(node[2])
            self.emit("STORE", self.declare(node[1]))
        elif kind == "assign":
            self.compile_expr(node[2])
            self.emit("STORE", self.resolve(node[1]))
        elif kind == "print":
            self.compile_expr(node[1])
            self.emit("PRINT")
        elif kind == "expr":
            self.compile_expr(node[1])
            self.emit("POP")
        elif kind == "return":
            if node[1] is None:
                self.emit("PUSH", 0)
            else:
                self.compile_expr(node[1])
            self.emit("RET")
        elif kind == "if":
            _, cond, then_stmts, else_stmts, pos = node
            self.compile_expr(cond)
            jz = self.emit("JZ", 0)
            for stmt in then_stmts:
                self.compile_stmt(stmt)
            if else_stmts:
                jmp = self.emit("JMP", 0)
                self.code[jz] = ("JZ", len(self.code))
                for stmt in else_stmts:
                    self.compile_stmt(stmt)
                self.code[jmp] = ("JMP", len(self.code))
            else:
                self.code[jz] = ("JZ", len(self.code))
        elif kind == "while":
            _, cond, body, pos = node
            start = len(self.code)
            self.compile_expr(cond)
            jz = self.emit("JZ", 0)
            for stmt in body:
                self.compile_stmt(stmt)
            self.emit("JMP", start)
            self.code[jz] = ("JZ", len(self.code))
        elif kind == "fn":
            raise CompileError("functions may only be declared at the top level")
        else:
            raise CompileError(f"unknown statement {kind!r}")

    def compile_expr(self, node):
        """Emit instructions leaving exactly one value on the stack."""
        kind = node[0]
        if kind in ("num", "str", "bool"):
            self.emit("PUSH", node[1])
        elif kind == "var":
            self.emit("LOAD", self.resolve(node[1]))
        elif kind == "unary":
            self.compile_expr(node[2])
            self.emit("NEG" if node[1] == "-" else "NOT")
        elif kind == "bin":
            _, op, left, right, pos = node
            if op == "&&":
                self.compile_expr(left)
                jz = self.emit("JZ", 0)
                self.compile_expr(right)
                jmp = self.emit("JMP", 0)
                self.code[jz] = ("JZ", len(self.code))
                self.emit("PUSH", False)
                self.code[jmp] = ("JMP", len(self.code))
            elif op == "||":
                self.compile_expr(left)
                jz = self.emit("JZ", 0)
                self.emit("PUSH", True)
                jmp = self.emit("JMP", 0)
                self.code[jz] = ("JZ", len(self.code))
                self.compile_expr(right)
                self.code[jmp] = ("JMP", len(self.code))
            else:
                self.compile_expr(left)
                self.compile_expr(right)
                self.emit("BIN", op)
        elif kind == "call":
            _, name, args, pos = node
            for arg in args:
                self.compile_expr(arg)
            self.emit("CALL", (name, len(args)))
        else:
            raise CompileError(f"unknown expression {kind!r}")


class VM:
    def __init__(self, max_steps=200000):
        self.max_steps = max_steps
        self.output = []

    def binary(self, op, left, right):
        """Apply one BIN operator, raising VMError on division by zero."""
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op in ("/", "%"):
            if right == 0:
                raise VMError("division by zero")
            return left / right if op == "/" else left % right
        if op == "^":
            return left ** right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        raise VMError(f"unknown operator {op!r}")

    def run(self, code):
        """Execute from address 0 until HALT; return the printed lines."""
        self.output = []
        stack = []
        frames = [{"locals": [], "ret": None}]
        pc = 0
        steps = 0
        while True:
            steps += 1
            if steps > self.max_steps:
                raise VMError("step limit exceeded")
            if pc < 0 or pc >= len(code):
                raise VMError(f"program counter {pc} is outside the code")
            op, arg = code[pc]
            pc += 1
            if op == "ENTER":
                locals_ = frames[-1]["locals"]
                while len(locals_) < arg:
                    locals_.append(0)
            elif op == "PUSH":
                stack.append(arg)
            elif op == "LOAD":
                stack.append(frames[-1]["locals"][arg])
            elif op == "STORE":
                frames[-1]["locals"][arg] = stack.pop()
            elif op == "POP":
                stack.pop()
            elif op == "NEG":
                stack.append(-stack.pop())
            elif op == "NOT":
                stack.append(not stack.pop())
            elif op == "BIN":
                right = stack.pop()
                left = stack.pop()
                stack.append(self.binary(arg, left, right))
            elif op == "JMP":
                pc = arg
            elif op == "JZ":
                if not stack.pop():
                    pc = arg
            elif op == "PRINT":
                self.output.append(format_value(stack.pop()))
            elif op == "CALL":
                target, nargs = arg
                cut = len(stack) - nargs
                args = stack[cut:]
                del stack[cut:]
                frames.append({"locals": args, "ret": pc})
                pc = target
            elif op == "RET":
                value = stack.pop()
                frame = frames.pop()
                if not frames:
                    raise VMError("return outside a call")
                pc = frame["ret"]
                stack.append(value)
            elif op == "HALT":
                return self.output
            else:
                raise VMError(f"unknown opcode {op!r}")


def run_program(program, max_steps=200000):
    return VM(max_steps=max_steps).run(Compiler().compile(program))


demo = [Let("i", Num(1)), Let("total", Num(0)),
        While(Bin("<=", Var("i"), Num(5)),
              [Assign("total", Bin("+", Var("total"), Var("i"))),
               Assign("i", Bin("+", Var("i"), Num(1)))]),
        Print(Var("total"))]
for line in run_program(demo):
    print(line)
'''}],
                "hints": [
                    "Emit `('ENTER', 0)` as the very first instruction, compile the body, then overwrite it with `self.code[enter] = ('ENTER', len(self.scope))` once you know how many slots you used.",
                    "Backpatching: `jz = self.emit('JZ', 0)` reserves the slot, and after the branch is compiled `self.code[jz] = ('JZ', len(self.code))` fills in the address you now know.",
                    "A `while` records `start = len(self.code)` *before* the condition, then ends with `self.emit('JMP', start)`.",
                    "`a && b` compiles to: a, `JZ false`, b, `JMP end`, `PUSH False`, end. Nothing evaluates b when a is falsey — that is the entire point.",
                ],
                "tests": [
                    {"name": "The instruction listing for a minimal program", "code": r'''
_code = Compiler().compile([Let("x", Num(1)), Print(Var("x"))])
_want = [("ENTER", 1), ("PUSH", 1), ("STORE", 0),
         ("LOAD", 0), ("PRINT", None), ("HALT", None)]
assert _code == _want, f"compiled to {_code!r}, expected {_want!r}"
assert run_program([Let("x", Num(1)), Print(Var("x"))]) == ["1"], "and it should run"
'''},
                    {"name": "Expressions evaluate in postorder", "code": r'''
_prog = [Print(Bin("+", Num(2), Bin("*", Num(3), Num(4)))),
         Print(Bin("/", Num(7), Num(2))),
         Print(Bin("/", Num(6), Num(3))),
         Print(Bin("^", Num(2), Num(10))),
         Print(Unary("-", Bin("-", Num(3), Num(10)))),
         Print(Bin("+", Str("ab"), Str("c"))),
         Print(Bin("<", Num(1), Num(2))),
         Print(Unary("!", Bool(True)))]
_got = run_program(_prog)
_want = ["14", "3.5", "2", "1024", "7", "abc", "true", "false"]
assert _got == _want, f"got {_got!r}, expected {_want!r}"
'''},
                    {"name": "Jumps: if/else and a counted loop", "code": r'''
_branch = [Let("x", Num(3)),
           If(Bin(">", Var("x"), Num(2)), [Print(Str("big"))], [Print(Str("small"))]),
           If(Bin(">", Var("x"), Num(9)), [Print(Str("huge"))], [])]
assert run_program(_branch) == ["big"], f"got {run_program(_branch)!r}, expected ['big']"
_loop = [Let("i", Num(1)), Let("total", Num(0)),
         While(Bin("<=", Var("i"), Num(5)),
               [Assign("total", Bin("+", Var("total"), Var("i"))),
                Assign("i", Bin("+", Var("i"), Num(1)))]),
         Print(Var("total"))]
assert run_program(_loop) == ["15"], f"summing 1..5 gave {run_program(_loop)!r}, expected ['15']"
_never = [While(Bool(False), [Print(Str("no"))]), Print(Str("done"))]
assert run_program(_never) == ["done"], "a loop whose guard is false runs zero times"
'''},
                    {"name": "&& and || short-circuit", "code": r'''
_prog = [Let("x", Num(0)),
         If(Bin("&&", Bin("!=", Var("x"), Num(0)),
                Bin(">", Bin("/", Num(10), Var("x")), Num(1))),
            [Print(Str("boom"))], [Print(Str("safe"))])]
_got = run_program(_prog)
assert _got == ["safe"], f"got {_got!r} — the right operand of && must not be evaluated"
_or = [Let("x", Num(0)),
       Print(Bin("||", Bin("==", Var("x"), Num(0)),
                 Bin(">", Bin("/", Num(10), Var("x")), Num(1))))]
assert run_program(_or) == ["true"], f"got {run_program(_or)!r} — || short-circuits too"
_both = [Print(Bin("&&", Bool(True), Bool(False))),
         Print(Bin("||", Bool(False), Bool(True)))]
assert run_program(_both) == ["false", "true"], f"got {run_program(_both)!r}"
'''},
                    {"name": "Calls, frames and recursion", "code": r'''
_fact = [Fn("fact", [("n", "num")], "num",
            [If(Bin("<=", Var("n"), Num(1)), [Return(Num(1))], []),
             Return(Bin("*", Var("n"), Call("fact", [Bin("-", Var("n"), Num(1))])))]),
         Print(Call("fact", [Num(5)]))]
assert run_program(_fact) == ["120"], f"fact(5) gave {run_program(_fact)!r}, expected ['120']"
_fib = [Fn("fib", [("n", "num")], "num",
           [If(Bin("<", Var("n"), Num(2)), [Return(Var("n"))], []),
            Return(Bin("+", Call("fib", [Bin("-", Var("n"), Num(1))]),
                       Call("fib", [Bin("-", Var("n"), Num(2))])))]),
        Print(Call("fib", [Num(10)]))]
assert run_program(_fib) == ["55"], f"fib(10) gave {run_program(_fib)!r}, expected ['55']"
_frames = [Let("x", Num(5)),
           Fn("double", [("y", "num")], "num",
              [Let("x", Bin("*", Var("y"), Num(2))), Return(Var("x"))]),
           Print(Call("double", [Num(3)])),
           Print(Var("x"))]
_got = run_program(_frames)
assert _got == ["6", "5"], f"got {_got!r} — a function's locals must not touch the caller's"
'''},
                    {"name": "Void calls and statement expressions leave a clean stack", "code": r'''
_prog = [Fn("shout", [("s", "str")], "void", [Print(Var("s")), Return(None)]),
         ExprStmt(Call("shout", [Str("hi")])),
         ExprStmt(Call("shout", [Str("again")])),
         Print(Str("end"))]
_got = run_program(_prog)
assert _got == ["hi", "again", "end"], f"got {_got!r}, expected ['hi', 'again', 'end']"
_code = Compiler().compile(_prog)
assert ("POP", None) in _code, "an expression statement must discard its value with POP"
'''},
                    {"name": "Compile-time and run-time errors", "code": r'''
try:
    Compiler().compile([Print(Var("ghost"))])
    assert False, "an undefined variable should raise CompileError"
except CompileError:
    pass
try:
    Compiler().compile([ExprStmt(Call("nope", []))])
    assert False, "a call to an unknown function should raise CompileError"
except CompileError:
    pass
try:
    Compiler().compile([Fn("f", [("a", "num")], "num", [Return(Var("a"))]),
                        ExprStmt(Call("f", [Num(1), Num(2)]))])
    assert False, "the wrong argument count should raise CompileError"
except CompileError:
    pass
try:
    run_program([Print(Bin("/", Num(1), Num(0)))])
    assert False, "division by zero should raise VMError"
except VMError:
    pass
try:
    run_program([While(Bool(True), [])], max_steps=500)
    assert False, "an endless loop should hit the step limit and raise VMError"
except VMError as _e:
    assert "step" in str(_e), f"VMError message was {str(_e)!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Optimisation and its obligations",
            "summary": "Constant folding, algebraic identities and dead code — each one argued for, then tested.",
            "concepts": [
                "An optimisation is a program transformation that must preserve observable behaviour",
                "Constant folding evaluates at compile time what would otherwise be evaluated every run",
                "Folding must refuse the cases the machine would refuse: `1/0` stays in the tree",
                "Algebraic identities such as `x * 1` are only sound when the discarded operand is effect-free",
                "Dead code elimination needs a constant condition, which is why folding runs first",
                "Transformations feed each other, so the pass is iterated to a fixed point",
                "A corpus with expected outputs is the cheapest available proof of semantics preservation",
            ],
            "quiz": {
                "title": "What an optimiser is allowed to do",
                "minutes": 8,
                "questions": [
                    {
                        "q": "An optimisation must preserve the program's behaviour. Which behaviour, exactly?",
                        "opts": [
                            "What can be observed from outside: the output it prints, and the errors it raises",
                            "The tree, up to a renaming of the nodes",
                            "The number of instructions executed, which must not increase",
                            "Every intermediate value the program computes along the way",
                        ],
                        "a": 0,
                        "why": r"""
Observable behaviour is the contract, and everything not observable is the budget you
get to spend. The tree obviously changes — that is the point. Intermediate values are
free to disappear; `2 + 3` never being computed at run time is the whole of constant
folding. Instruction counts usually fall but are not the promise: inlining and loop
unrolling both make the code longer on purpose. Being precise about *observable* is
what makes the hard cases decidable rather than a matter of taste — it is why dropping
a call is forbidden even when its result is unused, and why the reference interpreter
in `main.py`, which reports only the printed lines, is the right yardstick to test
against.
""",
                    },
                    {
                        "q": "`fold` leaves `1 / 0` in the tree instead of evaluating it. Why is that the right refusal?",
                        "opts": [
                            "The expression may sit in a branch that never runs, and folding it would either reject a working program or invent a value it never had",
                            "Division is not associative, so the compiler cannot reason about it",
                            "Because the result is a float rather than an int",
                            "Because the VM would raise a different exception from the one Python raises",
                        ],
                        "a": 0,
                        "why": r"""
Folding means *evaluate now what would be evaluated later*. This is precisely the case
where "later" might be never — put it inside `if false { ... }` and the program is
supposed to run fine. So the compiler has two bad options if it insists on folding: it
can raise, turning a program that works into a program that does not compile, or it
can substitute some number, in which case the division by zero silently stops
happening. So it does neither, leaves the node alone, and lets the machine raise if
and when control actually reaches it. This is why `const_apply` catches the
arithmetic exceptions and returns `None`: refusing to fold is always sound, and that
asymmetry is the safety net an optimiser is built on.
""",
                    },
                    {
                        "q": "`x * 0 -> 0` is guarded with `is_pure(x)`. What does the guard prevent?",
                        "opts": [
                            "Deleting an operand that does something observable, such as `f() * 0` where `f` prints",
                            "Folding a multiplication whose operands are not both numbers",
                            "Rewriting an expression whose value is used later in the program",
                            "Applying the rule twice to the same node",
                        ],
                        "a": 0,
                        "why": r"""
The rule is true about *values* — anything times zero is zero — and an optimiser deals
in programs, where an operand is not only a value but a thing that happens. Dropping
`f()` throws away whatever `f` printed, and the arithmetic identity has nothing to say
about that. Note which rules need the guard and which do not: `x * 1 -> x` keeps its
operand, so it is safe unconditionally, and `false && x -> false` needs no guard
either, because `&&` short-circuits — the right operand was never going to run, so
discarding it discards nothing. It is `x * 0`, `x - x`, `x ^ 0` and `x && false` that
throw away an operand the program would have evaluated, and those must ask first. In
this language `is_pure` only has
to look for a call, because nothing else can have an effect — a language with
assignment inside expressions, or exceptions, needs a much more careful test.
""",
                    },
                    {
                        "q": "Why must folding run before dead-code elimination rather than after?",
                        "opts": [
                            "Dead-code elimination looks for a literal condition, and `2 > 3` only becomes `false` once it has been folded",
                            "Because folding is cheaper, and cheap passes should run first",
                            "Because eliminating first would remove the constants folding needs",
                            "Because folding cannot be applied to code inside an `if`",
                        ],
                        "a": 0,
                        "why": r"""
`eliminate_dead` tests `cond[0] == "bool"` — it acts only on a condition that is
already a literal, and does no evaluation of its own. So `if 2 > 3` is invisible to it
until folding has turned the comparison into `false`; run in the other order, the
branch stays. This is the general shape of a pass pipeline: transformations create
each other's opportunities, and the order is a real design decision rather than a
matter of taste. It is also why `optimise` runs the whole thing to a fixed point
instead of once — a fold can enable a simplification, and a simplification can produce
a constant that folds.
""",
                    },
                    {
                        "q": "`optimise_expr` repeats `simplify(fold(node))` until nothing changes. Which of these actually needs the second pass?",
                        "opts": [
                            "`x ^ 0 + y ^ 0`",
                            "`2 * 3 + 4`",
                            "`x + 0`",
                            "`(x - x) + 3`",
                        ],
                        "a": 0,
                        "why": r"""
Follow the order inside one pass: `fold` runs first, then `simplify`. For
`x ^ 0 + y ^ 0` the fold finds nothing constant, then simplify turns each side into
`1` — and the addition of those two ones is a folding opportunity that arrived after
folding had already run. The next pass turns it into `2`. The others all finish in one
pass, because `simplify` works bottom up: it rewrites `x - x` to `0` before it looks
at the `+` above it, so `(x - x) + 3` collapses to `3` on the way back up the tree. A
fixed-point loop is the cheap way to be right about all of these without reasoning
about which pass enables which.
""",
                    },
                    {
                        "q": "Every corpus program prints the same lines before and after optimising. What has that established?",
                        "opts": [
                            "That the transformations preserved behaviour on those five programs, which is evidence rather than proof",
                            "That the transformations are semantics-preserving for every program",
                            "That the optimiser is a fixed point, since nothing changed",
                            "That the optimised programs are faster",
                        ],
                        "a": 0,
                        "why": r"""
Testing shows the presence of correctness on the inputs tested and nothing beyond
them — a corpus of five programs cannot reach the case where `x * 0` drops a call,
unless someone put that case in the corpus. Which is exactly how to use it: a corpus
is a place to record every dangerous case you thought of, and it earns its keep the
day a rule is added and an old program's output changes. Proof is available for
transformations this small — you argue that folding agrees with the evaluator on
literal operands, and that each identity holds for pure operands — and a serious
compiler does both, because the proof covers all programs and the corpus covers the
gap between the proof and the code you actually wrote.
""",
                    },
                ],
            },
            "blanks": {
                "title": "The three guards that keep the pass honest",
                "minutes": 9,
                "caption": "main.py — the refusal in fold, the purity test in simplify, the cut in eliminate_dead",
                "lang": "python",
                "brief": r"""
An optimiser is mostly rules that are obviously true, plus a small number of places
where it has to decline. Those places are what separates a pass you can trust from one
that is right about most programs. Three of them are below, one hole each, plus the
identity that keeps its operand.

Nothing runs here — you are choosing what each line has to say.
""",
                "listing": """# in const_apply: evaluate what the machine would evaluate anyway, and nothing else
try:
    value = APPLY[op](lv, rv)
except (ZeroDivisionError, KeyError, OverflowError):
    return ___                         # 1 / 0 has to survive to run time
return ("bool", value) if op in COMPARISONS else ("num", value)


# in simplify: the multiplicative identities
elif op == "*":
    if is_num(right, 1):
        return ___                     # x * 1
    if is_num(right, 0) and ___(left):
        return ("num", 0, pos)         # x * 0


# in eliminate_dead: walking a statement list
elif kind == "return":
    kept.append(node)
    ___                                # nothing later in this block can run
""",
                "blanks": [
                    {
                        "prompt": "The arithmetic refused to happen. What does `const_apply` hand back?",
                        "hole": "?",
                        "opts": ["(\"bool\", False)", "left", "None", "(\"num\", 0)"],
                        "a": 2,
                        "why": "`None` is the agreed signal for *this will not fold*, and the caller responds by leaving the node exactly as it was. Refusing to fold is always sound, which is what makes it the safe answer whenever anything is unclear.",
                        "whys": [
                            "Same fault in a different type: a value is manufactured for an expression that has none, and the type is wrong as well, so the rest of the tree is now folding against a boolean.",
                            "The caller expects a `(kind, value)` pair and appends the position to it, so handing back a node produces a malformed tree — and it silently rewrites `1 / 0` to its left operand along the way.",
                            "`None` is the agreed signal for *this will not fold*, and the caller responds by leaving the node exactly as it was. Refusing to fold is always sound, which is what makes it the safe answer whenever anything is unclear.",
                            "That invents a value for `1 / 0`. The division by zero then never happens at run time, and a program that should have stopped carries on with a number nobody computed.",
                        ],
                    },
                    {
                        "prompt": "The right operand is the literal 1. What does the multiplication become?",
                        "hole": "?",
                        "opts": ["right", "(\"num\", 1, pos)", "(\"bin\", op, left, right, pos)", "left"],
                        "a": 3,
                        "why": "The left operand, unchanged and undisturbed. This identity keeps both operands' effects — it simply stops multiplying by one — so it needs no purity guard at all.",
                        "whys": [
                            "`right` is the literal 1 that was just matched, so this rewrites `x * 1` to `1` — arithmetic nonsense that happens to be right when `x` is also 1.",
                            "Same value, thrown away differently: every multiplication by one collapses to the constant 1 rather than to the operand it should keep.",
                            "Rebuilding the node unchanged means the identity never fires. Nothing breaks; the pass just does not do its job, and the multiply survives to run time.",
                            "The left operand, unchanged and undisturbed. This identity keeps both operands' effects — it simply stops multiplying by one — so it needs no purity guard at all.",
                        ],
                    },
                    {
                        "prompt": "The right operand is the literal 0, so the left one is about to be discarded. What has to hold first?",
                        "hole": "?",
                        "opts": ["fold", "is_pure", "is_num", "bool"],
                        "a": 1,
                        "why": "The operand may only be dropped if evaluating it could not have been observed. `is_pure` says no call is hiding in there, and without that check `f() * 0` loses whatever `f` printed.",
                        "whys": [
                            "Folding returns a node, which is always truthy, so the guard passes for every operand — and it quietly does a fold in the middle of a condition, which is not what a guard is for.",
                            "The operand may only be dropped if evaluating it could not have been observed. `is_pure` says no call is hiding in there, and without that check `f() * 0` loses whatever `f` printed.",
                            "`is_num` takes a node and the value to compare against, so this does not even have the right shape — and asking whether the operand is a literal number is a much stronger demand than the rule needs.",
                            "A node is a non-empty tuple, so this is true of every expression there is. The guard reads as if it were checking something while permitting exactly everything.",
                        ],
                    },
                    {
                        "prompt": "A `return` has just been kept. What happens to the rest of the block?",
                        "hole": "?",
                        "opts": ["break", "continue", "pass", "return []"],
                        "a": 0,
                        "why": "`break` leaves the loop, so every statement after the `return` is simply never appended — which is the definition of unreachable code, expressed as three characters of control flow.",
                        "whys": [
                            "`break` leaves the loop, so every statement after the `return` is simply never appended — which is the definition of unreachable code, expressed as three characters of control flow.",
                            "`continue` goes on to the next statement and keeps it, so the unreachable code survives. The pass is then correct but pointless on exactly the case this branch exists for.",
                            "`pass` does nothing at all, which is the same outcome: the loop carries on and appends everything after the `return`.",
                            "That throws away the statements already kept, including the `return` itself, so a function body optimises down to nothing and stops returning anything.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How much is left after the pass?",
                "minutes": 8,
                "brief": r"""
`count_nodes` counts tree nodes: one for each statement, plus one for every expression
node inside it. Positions are not nodes. Run the whole optimiser over this program —
fold, then the identities, then dead-code elimination, to a fixed point — and count
what survives.

```text
let n = 6 * 7;
print n + 0;
if 2 < 3 { print "yes"; } else { print "no"; }
99;
print n ^ 0;
```

The program starts at 22 nodes. Every one of the five statements is touched by
something.
""",
                "prompt": "How many nodes does `count_nodes` report for the optimised program?",
                "note": "One node per statement and one per expression node. `Print(Var(\"n\"))` is 2 nodes.",
                "figure": "22 nodes go in, and all five statements are touched — by folding, by an identity, or by dead-code elimination",
                "given": [
                    {"label": "Before", "value": "22 nodes"},
                    {"label": "A statement", "value": "1 node, plus its expression"},
                    {"label": "`n`", "value": "a variable, and pure"},
                    {"label": "Passes", "value": "fold, simplify, eliminate_dead, to a fixed point"},
                ],
                "aside": "Write the optimised program out as source first. The count is then almost "
                         "immediate, because nothing complicated survives.",
                "answer": 8,
                "tol": 0,
                "unit": "nodes",
                "hint": "Take the statements one at a time: `6 * 7` folds; `n + 0` loses its zero; "
                        "`2 < 3` folds to `true` and the `if` collapses to the branch that runs; a bare "
                        "literal statement cannot be observed; and `n ^ 0` is 1 because `n` is pure.",
                "wrong": "Check the `if`: dead-code elimination keeps the statements of the branch that "
                         "runs, but the `if` node itself, the condition and the whole other branch are "
                         "gone. And `99;` leaves nothing behind at all.",
                "why": r"""
The optimised program is four statements:

```text
let n = 42;
print n;
print "yes";
print 1;
```

Each is one statement node holding one expression node, so the total is 8 — down from
22. Statement by statement: `6 * 7` folds to `42`; `n + 0` simplifies to `n`; `2 < 3`
folds to `true`, so the `if` is replaced by the contents of its then-branch and the
`else` disappears; `99;` is an expression statement whose expression is a literal, so
nothing about it is observable and it goes; and `n ^ 0` becomes `1`, which is legal
only because `n` is a variable and therefore pure — had it been `f() ^ 0`, the node
would have had to stay.

Worth noticing what did *not* happen: `print n;` still reads a variable at run time
even though `n` is provably 42 at this point. Propagating that constant into its uses
is a separate transformation with a separate obligation — it has to prove that nothing
reassigns `n` in between — and that is the next pass, not this one.
""",
            },
            "lab": {
                "title": "A fold / simplify / DCE pass with a corpus check",
                "runtime": "python",
                "minutes": 70,
                "brief": r'''
`main.py` gives you the tree constructors, a reference interpreter
`evaluate(program)`, a node counter, a purity test `is_pure(expr)`, and a
five-program `CORPUS`. Write the optimiser.

**`fold(expr)`** — evaluate constant subtrees, bottom up.

```text
fold(Bin("+", Num(2), Num(3)))                 -> Num(5)
fold(Bin("<", Num(1), Num(2)))                 -> Bool(True)
fold(Bin("+", Str("a"), Str("b")))             -> Str("ab")
fold(Bin("/", Num(1), Num(0)))                 -> unchanged, and no exception
fold(Bin("+", Var("x"), Num(0)))               -> unchanged (that is algebra, not folding)
```

The `APPLY` table already holds the operator semantics. Arithmetic needs two
`num` (or two `str` for `+`); comparisons need two `num` and give `bool`;
`==` and `!=` need two operands of the same kind. The folded node keeps the
position of the node it replaces.

**`simplify(expr)`** — algebraic identities, bottom up:

```text
x + 0   0 + x   x - 0   x * 1   1 * x   x / 1   x ^ 1   ->  x
x * 0   0 * x   ->  0        x ^ 0  ->  1        x - x  ->  0
true && b  ->  b       b || false  ->  b      !!x  ->  x      --x  ->  x
```

The rules that *drop* an operand (`x * 0`, `x - x`, `x ^ 0`) are only
sound when that operand is pure, so guard them with `is_pure`.

**`eliminate_dead(stmts)`** — over a statement list:

- `if` with a `Bool` condition collapses to the branch that runs
- `while false { ... }` disappears
- an expression statement whose expression is a literal or a variable disappears
- everything after a `return` in the same block disappears
- recurse into the blocks you keep

**`optimise_expr` / `optimise_stmt` / `optimise(program)`** — apply
`simplify(fold(...))` repeatedly until nothing changes, then eliminate dead
statements. `optimise` must be idempotent: optimising twice changes nothing.

The last check runs every corpus program through `evaluate` before and after
and demands identical output. That is the obligation an optimiser signs up to.
''',
                "files": [{"name": "main.py", "content": r'''
# ------------------------------------------------- given: node constructors
def Num(v, pos=(1, 1)):        return ("num", v, pos)
def Str(v, pos=(1, 1)):        return ("str", v, pos)
def Bool(v, pos=(1, 1)):       return ("bool", v, pos)
def Var(name, pos=(1, 1)):     return ("var", name, pos)
def Unary(op, x, pos=(1, 1)):  return ("unary", op, x, pos)
def Bin(op, l, r, pos=(1, 1)): return ("bin", op, l, r, pos)
def Call(name, args, pos=(1, 1)):        return ("call", name, args, pos)
def Let(name, expr, pos=(1, 1)):         return ("let", name, expr, pos)
def Assign(name, expr, pos=(1, 1)):      return ("assign", name, expr, pos)
def Print(expr, pos=(1, 1)):             return ("print", expr, pos)
def ExprStmt(expr, pos=(1, 1)):          return ("expr", expr, pos)
def Return(expr, pos=(1, 1)):            return ("return", expr, pos)
def If(cond, then, els, pos=(1, 1)):     return ("if", cond, then, els, pos)
def While(cond, body, pos=(1, 1)):       return ("while", cond, body, pos)


LITERALS = ("num", "str", "bool")

APPLY = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "%": lambda a, b: a % b,
    "^": lambda a, b: a ** b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}
COMPARISONS = ("<", "<=", ">", ">=", "==", "!=")


def format_value(value):
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def eval_expr(node, env):
    kind = node[0]
    if kind in LITERALS:
        return node[1]
    if kind == "var":
        return env[node[1]]
    if kind == "unary":
        value = eval_expr(node[2], env)
        return (not value) if node[1] == "!" else -value
    if kind == "bin":
        op = node[1]
        if op == "&&":
            return eval_expr(node[2], env) and eval_expr(node[3], env)
        if op == "||":
            return eval_expr(node[2], env) or eval_expr(node[3], env)
        return APPLY[op](eval_expr(node[2], env), eval_expr(node[3], env))
    raise RuntimeError(f"no evaluation rule for {node[0]!r}")


def run_block(stmts, env, out):
    for node in stmts:
        kind = node[0]
        if kind in ("let", "assign"):
            env[node[1]] = eval_expr(node[2], env)
        elif kind == "print":
            out.append(format_value(eval_expr(node[1], env)))
        elif kind == "expr":
            eval_expr(node[1], env)
        elif kind == "if":
            run_block(node[2] if eval_expr(node[1], env) else node[3], env, out)
        elif kind == "while":
            spins = 0
            while eval_expr(node[1], env):
                spins += 1
                if spins > 100000:
                    raise RuntimeError("runaway loop")
                run_block(node[2], env, out)
        else:
            raise RuntimeError(f"no execution rule for {kind!r}")


def evaluate(program):
    """Reference semantics: the printed lines of a program."""
    out = []
    run_block(program, {}, out)
    return out


def count_nodes(node):
    """How many tree nodes a program or expression contains."""
    if isinstance(node, list):
        return sum(count_nodes(child) for child in node)
    if isinstance(node, tuple) and node and isinstance(node[0], str):
        return 1 + sum(count_nodes(child) for child in node[1:]
                       if isinstance(child, (tuple, list)))
    return 0


def is_pure(node):
    """True when evaluating this expression cannot call anything."""
    if node[0] == "call":
        return False
    if node[0] == "unary":
        return is_pure(node[2])
    if node[0] == "bin":
        return is_pure(node[2]) and is_pure(node[3])
    return True


CORPUS = [
    [Let("x", Bin("+", Num(2), Bin("*", Num(3), Num(4)))),
     Print(Var("x")),
     Print(Bin("+", Bin("*", Var("x"), Num(1)), Num(0)))],

    [Let("n", Num(10)), Let("total", Num(0)),
     While(Bin(">", Var("n"), Num(0)),
           [Assign("total", Bin("+", Var("total"), Var("n"))),
            Assign("n", Bin("-", Var("n"), Num(1)))]),
     Print(Var("total"))],

    [If(Bin(">", Num(2), Num(3)), [Print(Str("impossible"))], [Print(Str("fine"))]),
     Print(Bin("==", Num(1), Num(1))),
     ExprStmt(Num(99))],

    [Let("s", Bin("+", Str("a"), Str("b"))),
     Print(Bin("+", Var("s"), Str("c"))),
     Print(Unary("!", Unary("!", Bool(True))))],

    [Let("x", Num(4)),
     Print(Bin("*", Bin("+", Var("x"), Num(0)), Bin("+", Num(2), Num(3)))),
     Print(Bin("-", Var("x"), Var("x"))),
     While(Bool(False), [Print(Str("never"))]),
     Print(Bin("^", Var("x"), Num(1)))],
]


# ------------------------------------------------------------- your code
def fold(node):
    """Evaluate constant subtrees. Never raise; leave what you cannot fold."""
    # your code here


def simplify(node):
    """Apply the algebraic identities, guarding the ones that drop an operand."""
    # your code here


def optimise_expr(node):
    """simplify(fold(node)) until it stops changing."""
    # your code here


def optimise_stmt(node):
    """Optimise every expression inside one statement, and its blocks."""
    # your code here


def eliminate_dead(stmts):
    """Drop the statements that cannot run or cannot be observed."""
    # your code here


def optimise(program):
    """Optimise statements and eliminate dead code, to a fixed point."""
    # your code here


for index, program in enumerate(CORPUS, 1):
    optimised = optimise(program)
    print(f"program {index}: {count_nodes(program)} -> {count_nodes(optimised)} nodes,"
          f" output {evaluate(optimised)}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
# ------------------------------------------------- given: node constructors
def Num(v, pos=(1, 1)):        return ("num", v, pos)
def Str(v, pos=(1, 1)):        return ("str", v, pos)
def Bool(v, pos=(1, 1)):       return ("bool", v, pos)
def Var(name, pos=(1, 1)):     return ("var", name, pos)
def Unary(op, x, pos=(1, 1)):  return ("unary", op, x, pos)
def Bin(op, l, r, pos=(1, 1)): return ("bin", op, l, r, pos)
def Call(name, args, pos=(1, 1)):        return ("call", name, args, pos)
def Let(name, expr, pos=(1, 1)):         return ("let", name, expr, pos)
def Assign(name, expr, pos=(1, 1)):      return ("assign", name, expr, pos)
def Print(expr, pos=(1, 1)):             return ("print", expr, pos)
def ExprStmt(expr, pos=(1, 1)):          return ("expr", expr, pos)
def Return(expr, pos=(1, 1)):            return ("return", expr, pos)
def If(cond, then, els, pos=(1, 1)):     return ("if", cond, then, els, pos)
def While(cond, body, pos=(1, 1)):       return ("while", cond, body, pos)


LITERALS = ("num", "str", "bool")

APPLY = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
    "%": lambda a, b: a % b,
    "^": lambda a, b: a ** b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}
COMPARISONS = ("<", "<=", ">", ">=", "==", "!=")


def format_value(value):
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def eval_expr(node, env):
    kind = node[0]
    if kind in LITERALS:
        return node[1]
    if kind == "var":
        return env[node[1]]
    if kind == "unary":
        value = eval_expr(node[2], env)
        return (not value) if node[1] == "!" else -value
    if kind == "bin":
        op = node[1]
        if op == "&&":
            return eval_expr(node[2], env) and eval_expr(node[3], env)
        if op == "||":
            return eval_expr(node[2], env) or eval_expr(node[3], env)
        return APPLY[op](eval_expr(node[2], env), eval_expr(node[3], env))
    raise RuntimeError(f"no evaluation rule for {node[0]!r}")


def run_block(stmts, env, out):
    for node in stmts:
        kind = node[0]
        if kind in ("let", "assign"):
            env[node[1]] = eval_expr(node[2], env)
        elif kind == "print":
            out.append(format_value(eval_expr(node[1], env)))
        elif kind == "expr":
            eval_expr(node[1], env)
        elif kind == "if":
            run_block(node[2] if eval_expr(node[1], env) else node[3], env, out)
        elif kind == "while":
            spins = 0
            while eval_expr(node[1], env):
                spins += 1
                if spins > 100000:
                    raise RuntimeError("runaway loop")
                run_block(node[2], env, out)
        else:
            raise RuntimeError(f"no execution rule for {kind!r}")


def evaluate(program):
    """Reference semantics: the printed lines of a program."""
    out = []
    run_block(program, {}, out)
    return out


def count_nodes(node):
    """How many tree nodes a program or expression contains."""
    if isinstance(node, list):
        return sum(count_nodes(child) for child in node)
    if isinstance(node, tuple) and node and isinstance(node[0], str):
        return 1 + sum(count_nodes(child) for child in node[1:]
                       if isinstance(child, (tuple, list)))
    return 0


def is_pure(node):
    """True when evaluating this expression cannot call anything."""
    if node[0] == "call":
        return False
    if node[0] == "unary":
        return is_pure(node[2])
    if node[0] == "bin":
        return is_pure(node[2]) and is_pure(node[3])
    return True


CORPUS = [
    [Let("x", Bin("+", Num(2), Bin("*", Num(3), Num(4)))),
     Print(Var("x")),
     Print(Bin("+", Bin("*", Var("x"), Num(1)), Num(0)))],

    [Let("n", Num(10)), Let("total", Num(0)),
     While(Bin(">", Var("n"), Num(0)),
           [Assign("total", Bin("+", Var("total"), Var("n"))),
            Assign("n", Bin("-", Var("n"), Num(1)))]),
     Print(Var("total"))],

    [If(Bin(">", Num(2), Num(3)), [Print(Str("impossible"))], [Print(Str("fine"))]),
     Print(Bin("==", Num(1), Num(1))),
     ExprStmt(Num(99))],

    [Let("s", Bin("+", Str("a"), Str("b"))),
     Print(Bin("+", Var("s"), Str("c"))),
     Print(Unary("!", Unary("!", Bool(True))))],

    [Let("x", Num(4)),
     Print(Bin("*", Bin("+", Var("x"), Num(0)), Bin("+", Num(2), Num(3)))),
     Print(Bin("-", Var("x"), Var("x"))),
     While(Bool(False), [Print(Str("never"))]),
     Print(Bin("^", Var("x"), Num(1)))],
]


# ------------------------------------------------------------- your code
def const_apply(op, left, right):
    """(kind, value) for two literal operands, or None when it will not fold."""
    lk, lv = left[0], left[1]
    rk, rv = right[0], right[1]
    if op in ("==", "!="):
        if lk != rk:
            return None
        return ("bool", APPLY[op](lv, rv))
    if op == "+" and lk == "str" and rk == "str":
        return ("str", lv + rv)
    if lk != "num" or rk != "num":
        return None
    try:
        value = APPLY[op](lv, rv)
    except (ZeroDivisionError, KeyError, OverflowError):
        return None
    return ("bool", value) if op in COMPARISONS else ("num", value)


def fold(node):
    """Evaluate constant subtrees. Never raise; leave what you cannot fold."""
    kind = node[0]
    if kind == "unary":
        _, op, operand, pos = node
        operand = fold(operand)
        if op == "-" and operand[0] == "num":
            return ("num", -operand[1], pos)
        if op == "!" and operand[0] == "bool":
            return ("bool", not operand[1], pos)
        return ("unary", op, operand, pos)
    if kind == "bin":
        _, op, left, right, pos = node
        left = fold(left)
        right = fold(right)
        if left[0] in LITERALS and right[0] in LITERALS and op in APPLY:
            folded = const_apply(op, left, right)
            if folded is not None:
                return folded + (pos,)
        if op in ("&&", "||") and left[0] == "bool" and right[0] == "bool":
            return ("bool", (left[1] and right[1]) if op == "&&"
                    else (left[1] or right[1]), pos)
        return ("bin", op, left, right, pos)
    if kind == "call":
        return ("call", node[1], [fold(arg) for arg in node[2]], node[3])
    return node


def is_num(node, value):
    return node[0] == "num" and node[1] == value


def is_bool(node, value):
    return node[0] == "bool" and node[1] is value


def simplify(node):
    """Apply the algebraic identities, guarding the ones that drop an operand."""
    kind = node[0]
    if kind == "call":
        return ("call", node[1], [simplify(arg) for arg in node[2]], node[3])
    if kind == "unary":
        _, op, operand, pos = node
        operand = simplify(operand)
        if operand[0] == "unary" and operand[1] == op:
            return operand[2]
        return ("unary", op, operand, pos)
    if kind == "bin":
        _, op, left, right, pos = node
        left = simplify(left)
        right = simplify(right)
        if op == "+":
            if is_num(right, 0):
                return left
            if is_num(left, 0):
                return right
        elif op == "-":
            if is_num(right, 0):
                return left
            if left == right and is_pure(left):
                return ("num", 0, pos)
        elif op == "*":
            if is_num(right, 1):
                return left
            if is_num(left, 1):
                return right
            if is_num(right, 0) and is_pure(left):
                return ("num", 0, pos)
            if is_num(left, 0) and is_pure(right):
                return ("num", 0, pos)
        elif op == "/":
            if is_num(right, 1):
                return left
        elif op == "^":
            if is_num(right, 1):
                return left
            if is_num(right, 0) and is_pure(left):
                return ("num", 1, pos)
        elif op == "&&":
            if is_bool(left, True):
                return right
            if is_bool(right, True):
                return left
            if is_bool(left, False):
                return ("bool", False, pos)
            if is_bool(right, False) and is_pure(left):
                return ("bool", False, pos)
        elif op == "||":
            if is_bool(left, False):
                return right
            if is_bool(right, False):
                return left
            if is_bool(left, True):
                return ("bool", True, pos)
            if is_bool(right, True) and is_pure(left):
                return ("bool", True, pos)
        return ("bin", op, left, right, pos)
    return node


def optimise_expr(node):
    """simplify(fold(node)) until it stops changing."""
    for _ in range(10):
        stepped = simplify(fold(node))
        if stepped == node:
            return stepped
        node = stepped
    return node


def optimise_stmt(node):
    """Optimise every expression inside one statement, and its blocks."""
    kind = node[0]
    if kind in ("let", "assign"):
        return (kind, node[1], optimise_expr(node[2]), node[3])
    if kind in ("print", "expr"):
        return (kind, optimise_expr(node[1]), node[2])
    if kind == "return":
        return ("return", None if node[1] is None else optimise_expr(node[1]), node[2])
    if kind == "if":
        return ("if", optimise_expr(node[1]),
                [optimise_stmt(s) for s in node[2]],
                [optimise_stmt(s) for s in node[3]], node[4])
    if kind == "while":
        return ("while", optimise_expr(node[1]),
                [optimise_stmt(s) for s in node[2]], node[3])
    return node


def eliminate_dead(stmts):
    """Drop the statements that cannot run or cannot be observed."""
    kept = []
    for node in stmts:
        kind = node[0]
        if kind == "if":
            _, cond, then_stmts, else_stmts, pos = node
            then_stmts = eliminate_dead(then_stmts)
            else_stmts = eliminate_dead(else_stmts)
            if cond[0] == "bool":
                kept.extend(then_stmts if cond[1] else else_stmts)
                continue
            if not then_stmts and not else_stmts and is_pure(cond):
                continue
            kept.append(("if", cond, then_stmts, else_stmts, pos))
        elif kind == "while":
            _, cond, body, pos = node
            if cond[0] == "bool" and cond[1] is False:
                continue
            kept.append(("while", cond, eliminate_dead(body), pos))
        elif kind == "expr":
            if node[1][0] in LITERALS or node[1][0] == "var":
                continue
            kept.append(node)
        elif kind == "return":
            kept.append(node)
            break
        else:
            kept.append(node)
    return kept


def optimise(program):
    """Optimise statements and eliminate dead code, to a fixed point."""
    current = program
    for _ in range(10):
        stepped = eliminate_dead([optimise_stmt(stmt) for stmt in current])
        if stepped == current:
            return stepped
        current = stepped
    return current


for index, program in enumerate(CORPUS, 1):
    optimised = optimise(program)
    print(f"program {index}: {count_nodes(program)} -> {count_nodes(optimised)} nodes,"
          f" output {evaluate(optimised)}")
'''}],
                "hints": [
                    "Write `fold` as a recursion that folds the children first and only then asks whether both are literals. Wrap the actual arithmetic in `try: ... except ZeroDivisionError: return None` so `1/0` survives untouched.",
                    "Two tiny predicates make `simplify` readable: `is_num(node, 0)` and `is_bool(node, True)`. Every identity is then one line.",
                    "`x * 0 -> 0` throws the left operand away. That is only legal when `is_pure(left)`, otherwise a call that prints something would vanish.",
                    "`eliminate_dead` builds a new list. A `return` appends itself and then `break`s, which is exactly what makes the rest of the block unreachable.",
                ],
                "tests": [
                    {"name": "Constant folding", "code": r'''
_cases = [(Bin("+", Num(2), Num(3)), Num(5)),
          (Bin("*", Num(2), Bin("+", Num(3), Num(4))), Num(14)),
          (Bin("-", Num(3), Num(10)), Num(-7)),
          (Bin("<", Num(1), Num(2)), Bool(True)),
          (Bin(">=", Num(1), Num(2)), Bool(False)),
          (Bin("==", Str("a"), Str("a")), Bool(True)),
          (Bin("+", Str("a"), Str("b")), Str("ab")),
          (Unary("-", Num(3)), Num(-3)),
          (Unary("!", Unary("!", Bool(True))), Bool(True))]
for _node, _want in _cases:
    _got = fold(_node)
    assert _got == _want, f"fold({_node!r}) gave {_got!r}, expected {_want!r}"
'''},
                    {"name": "Folding refuses what it must", "code": r'''
for _node in [Bin("/", Num(1), Num(0)), Bin("%", Num(1), Num(0)),
              Bin("+", Var("x"), Num(0)), Bin("+", Num(1), Var("x")),
              Bin("==", Num(1), Str("a")), Var("x"), Num(7)]:
    _got = fold(_node)
    assert _got == _node, f"fold({_node!r}) gave {_got!r} but should have left it alone"
_deep = Bin("*", Var("x"), Bin("+", Num(2), Num(3)))
assert fold(_deep) == Bin("*", Var("x"), Num(5)), \
    f"fold should still reach inside: got {fold(_deep)!r}"
'''},
                    {"name": "Algebraic identities", "code": r'''
_cases = [(Bin("+", Var("x"), Num(0)), Var("x")),
          (Bin("+", Num(0), Var("x")), Var("x")),
          (Bin("-", Var("x"), Num(0)), Var("x")),
          (Bin("*", Var("x"), Num(1)), Var("x")),
          (Bin("*", Num(1), Var("x")), Var("x")),
          (Bin("*", Var("x"), Num(0)), Num(0)),
          (Bin("/", Var("x"), Num(1)), Var("x")),
          (Bin("^", Var("x"), Num(1)), Var("x")),
          (Bin("^", Var("x"), Num(0)), Num(1)),
          (Bin("-", Var("x"), Var("x")), Num(0)),
          (Unary("!", Unary("!", Var("b"))), Var("b")),
          (Unary("-", Unary("-", Var("x"))), Var("x")),
          (Bin("&&", Bool(True), Var("b")), Var("b")),
          (Bin("||", Var("b"), Bool(False)), Var("b")),
          (Bin("||", Bool(True), Var("b")), Bool(True))]
for _node, _want in _cases:
    _got = simplify(_node)
    assert _got == _want, f"simplify({_node!r}) gave {_got!r}, expected {_want!r}"
_plain = Bin("+", Var("x"), Num(1))
assert simplify(_plain) == _plain, "an expression with no identity comes back unchanged"
'''},
                    {"name": "An identity that would delete an effect is refused", "code": r'''
_effectful = Bin("*", Call("f", []), Num(0))
assert simplify(_effectful) == _effectful, \
    "x * 0 -> 0 must not fire when x is a call: use is_pure"
_ok = Bin("*", Bin("+", Var("x"), Var("y")), Num(0))
assert simplify(_ok) == Num(0), f"pure operands may be dropped, got {simplify(_ok)!r}"
'''},
                    {"name": "Dead code elimination", "code": r'''
_stmts = [If(Bool(False), [Print(Str("no"))], [Print(Str("yes"))]),
          If(Bool(True), [Print(Str("kept"))], [Print(Str("dropped"))]),
          While(Bool(False), [Print(Str("never"))]),
          ExprStmt(Num(1)),
          ExprStmt(Var("x")),
          Print(Str("end"))]
_got = eliminate_dead(_stmts)
_want = [Print(Str("yes")), Print(Str("kept")), Print(Str("end"))]
assert _got == _want, f"eliminate_dead gave {_got!r}, expected {_want!r}"
_body = [Print(Str("a")), Return(Num(1)), Print(Str("unreachable"))]
_got = eliminate_dead(_body)
assert _got == [Print(Str("a")), Return(Num(1))], \
    f"statements after a return are unreachable, got {_got!r}"
_live = [If(Var("c"), [Print(Str("x"))], [])]
assert eliminate_dead(_live) == _live, "an if with a runtime condition stays"
'''},
                    {"name": "optimise composes the passes and is idempotent", "code": r'''
_prog = [Let("x", Num(4)),
         Print(Bin("*", Bin("+", Var("x"), Num(0)), Bin("+", Num(2), Num(3)))),
         ExprStmt(Num(99))]
_opt = optimise(_prog)
_want = [Let("x", Num(4)), Print(Bin("*", Var("x"), Num(5)))]
assert _opt == _want, f"optimise gave {_opt!r}, expected {_want!r}"
assert optimise(_opt) == _opt, "optimising an optimised program must change nothing"
assert _prog[1] == Print(Bin("*", Bin("+", Var("x"), Num(0)), Bin("+", Num(2), Num(3)))), \
    "optimise must build a new tree, not mutate the one it was given"
'''},
                    {"name": "The corpus keeps its behaviour and loses nodes", "code": r'''
_shrunk = 0
for _i, _program in enumerate(CORPUS):
    _before = evaluate(_program)
    _optimised = optimise(_program)
    _after = evaluate(_optimised)
    assert _after == _before, \
        f"CORPUS[{_i}] printed {_before!r} before optimising and {_after!r} after"
    _n_before, _n_after = count_nodes(_program), count_nodes(_optimised)
    assert _n_after <= _n_before, f"CORPUS[{_i}] grew from {_n_before} to {_n_after} nodes"
    if _n_after < _n_before:
        _shrunk += 1
assert _shrunk >= 3, f"only {_shrunk} of the {len(CORPUS)} corpus programs got smaller"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an end-to-end compiler and virtual machine",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
`frontend.py` is given and must not be edited: it is the lexer, the Pratt
parser and the type checker from modules 1-3, packaged. It exports
`tokenize`, `parse`, `check` and the errors `LexError`, `ParseError` and
`SemanticError`.

You write the back end in `codegen.py` and the corpus runner in `main.py`.

## The language

```text
fn gcd(a: num, b: num) -> num {
  while b != 0 {
    let t = b;
    b = a % b;
    a = t;
  }
  return a;
}
print gcd(1071, 462);
```

Types are `num`, `str`, `bool` and `void`. Parameters are annotated, `->`
declares the return type, `let` infers. Everything the checker rejects must
never reach your compiler.

## `codegen.py`

- `Compiler.compile(program)` — the instruction list, exactly the encoding from
  module 4: `ENTER PUSH LOAD STORE POP BIN NEG NOT JMP JZ CALL RET PRINT HALT`.
  Main body first, then `HALT`, then the function bodies; `CALL` carries
  `(address, nargs)` after patching, never a name.
- `VM.run(code)` — execute and return the printed lines. `max_steps` bounds the
  run; `VMError` for division by zero, a bad program counter, or the budget.
- `compile_source(src)` — `parse`, then `check`, then compile. Errors from the
  front end propagate unchanged.
- `run_source(src, max_steps=200000)` — compile and run, returning the lines.
- `disassemble(code)` — one line per instruction,
  `"{address:04d}  {op:<6} {arg}"` with the trailing space stripped when there
  is no argument.

## `main.py`

Holds `CORPUS`, a list of `(source, expected_lines)` pairs — at least six
programs covering arithmetic, loops, functions, recursion, strings and
branching — runs each one, prints whether it matched, and finishes by printing
the disassembly of a short program.

Short-circuit evaluation is not optional: `x != 0 && 10 / x > 1` must not
divide when `x` is zero.
''',
        "deliverables": [
            "`codegen.py` — `Compiler`, `VM`, `compile_source`, `run_source` and `disassemble`, importable with no output",
            "`main.py` — a `CORPUS` of at least six source programs with their expected output, run and reported",
            "Short-circuit code generation for `&&` and `||` using jumps rather than a `BIN` instruction",
            "Function calls with their own frames: parameters in slots 0..n-1, a return address, and no access to the caller's locals",
            "Errors from every phase reaching the caller intact: `LexError`, `ParseError`, `SemanticError`, `CompileError`, `VMError`",
            "A readable disassembly listing of a compiled program",
        ],
        "constraints": [
            "Standard library only, and `frontend.py` must not be edited",
            "Importing `codegen` must have no side effects — no printing, no compiling",
            "`CALL` addresses are resolved at compile time by patching, not looked up while running",
            "The VM must be unable to run forever: honour `max_steps` and raise `VMError` when it is exhausted",
            "No `eval`, no `exec`, and no Python-level recursion through the interpreter loop",
        ],
        "rubric": [
            {"criterion": "Correctness of the pipeline", "weight": 40,
             "evidence": "Every corpus program produces exactly its expected output, including recursion, loops and string work."},
            {"criterion": "Code generation quality", "weight": 25,
             "evidence": "Backpatched jumps, per-function slot allocation, short-circuit &&/||, and CALL patched to an address."},
            {"criterion": "Robustness", "weight": 20,
             "evidence": "Division by zero, an exhausted step budget, unknown names and bad arities all raise the documented error type."},
            {"criterion": "Readability", "weight": 15,
             "evidence": "One method per construct, docstrings on the public surface, and no dead code or debug prints."},
        ],
        "hints": [
            "Build `compile_source` first as three lines — `parse`, `check`, `Compiler().compile` — then work outwards; the front end already tells you when a program is not worth compiling.",
            "Reserve jump slots with `self.emit('JZ', 0)` and patch them with `self.code[slot] = ('JZ', len(self.code))` once the branch is placed. The same trick fills in `ENTER` once you know the slot count.",
            "Compile function bodies only after the main body and its `HALT`, recording `name -> (address, arity)`; a final sweep rewrites every `('CALL', (name, nargs))` into `('CALL', (address, nargs))`.",
            "For `a && b`: emit a, `JZ false`, b, `JMP end`, then at `false` a `PUSH False`, then `end`. Compare your listing against `disassemble` output when a corpus program misbehaves.",
        ],
        "files": [
            {"name": "frontend.py", "ro": True, "content": r'''
"""Given: lexer, Pratt parser and type checker for the course language."""

KEYWORDS = {"let", "fn", "if", "else", "while", "return", "print", "true", "false"}
OPERATORS = ["==", "!=", "<=", ">=", "&&", "||", "->",
             "+", "-", "*", "/", "%", "^", "=", "<", ">", "!",
             "(", ")", "{", "}", ",", ";", ":"]
ESCAPES = {"n": "\n", "t": "\t", "\\": "\\", '"': '"'}
TYPES = {"num", "str", "bool", "void"}

PRECEDENCE = {"||": 1, "&&": 2, "==": 3, "!=": 3,
              "<": 4, "<=": 4, ">": 4, ">=": 4,
              "+": 5, "-": 5, "*": 6, "/": 6, "%": 6, "^": 7}
RIGHT_ASSOCIATIVE = {"^"}
UNARY_BIND = 7

ARITHMETIC = {"+", "-", "*", "/", "%", "^"}
COMPARISON = {"<", "<=", ">", ">="}
EQUALITY = {"==", "!="}
LOGICAL = {"&&", "||"}


class LexError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message, self.line, self.col = message, line, col


class ParseError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message, self.line, self.col = message, line, col


class SemanticError(Exception):
    def __init__(self, message, line, col):
        super().__init__(f"{message} at line {line}, column {col}")
        self.message, self.line, self.col = message, line, col


class Token:
    def __init__(self, kind, value, line, col):
        self.kind, self.value, self.line, self.col = kind, value, line, col

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, {self.line}:{self.col})"


def tokenize(src):
    tokens, i, line, col, n = [], 0, 1, 1, len(src)
    while i < n:
        ch = src[i]
        if ch == "\n":
            i, line, col = i + 1, line + 1, 1
            continue
        if ch in " \t\r":
            i, col = i + 1, col + 1
            continue
        if ch == "#":
            while i < n and src[i] != "\n":
                i, col = i + 1, col + 1
            continue
        start_col = col
        if ch.isalpha() or ch == "_":
            j = i
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            word = src[i:j]
            tokens.append(Token("KW" if word in KEYWORDS else "IDENT", word, line, start_col))
            col, i = col + j - i, j
            continue
        if ch.isdigit():
            j, is_float = i, False
            while j < n and src[j].isdigit():
                j += 1
            if j + 1 < n and src[j] == "." and src[j + 1].isdigit():
                is_float, j = True, j + 1
                while j < n and src[j].isdigit():
                    j += 1
            if j < n and (src[j].isalpha() or src[j] == "_"):
                raise LexError("malformed number", line, start_col)
            text = src[i:j]
            tokens.append(Token("NUM", float(text) if is_float else int(text), line, start_col))
            col, i = col + j - i, j
            continue
        if ch == '"':
            j, chars = i + 1, []
            while True:
                if j >= n or src[j] == "\n":
                    raise LexError("unterminated string", line, start_col)
                if src[j] == '"':
                    break
                if src[j] == "\\":
                    esc = src[j + 1] if j + 1 < n else ""
                    if esc not in ESCAPES:
                        raise LexError("bad escape", line, start_col)
                    chars.append(ESCAPES[esc])
                    j += 2
                    continue
                chars.append(src[j])
                j += 1
            j += 1
            tokens.append(Token("STR", "".join(chars), line, start_col))
            col, i = col + j - i, j
            continue
        for op in OPERATORS:
            if src.startswith(op, i):
                tokens.append(Token("OP", op, line, start_col))
                i, col = i + len(op), col + len(op)
                break
        else:
            raise LexError(f"unexpected character {ch!r}", line, start_col)
    tokens.append(Token("EOF", "", line, col))
    return tokens


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos]

    def advance(self):
        tok = self.tokens[self.pos]
        if tok.kind != "EOF":
            self.pos += 1
        return tok

    def at(self, kind, value=None):
        tok = self.peek()
        return tok.kind == kind and (value is None or tok.value == value)

    def expect(self, kind, value=None):
        tok = self.peek()
        if not self.at(kind, value):
            wanted = value if value is not None else kind
            raise ParseError(f"expected {wanted!r}, found {tok.value!r}", tok.line, tok.col)
        return self.advance()

    def parse_type(self):
        tok = self.expect("IDENT")
        if tok.value not in TYPES:
            raise ParseError(f"unknown type {tok.value!r}", tok.line, tok.col)
        return tok.value

    def parse_program(self):
        stmts = []
        while not self.at("EOF"):
            stmts.append(self.parse_stmt())
        return stmts

    def parse_block(self):
        self.expect("OP", "{")
        stmts = []
        while not self.at("OP", "}"):
            if self.at("EOF"):
                tok = self.peek()
                raise ParseError("unclosed block", tok.line, tok.col)
            stmts.append(self.parse_stmt())
        self.expect("OP", "}")
        return stmts

    def parse_stmt(self):
        tok = self.peek()
        pos = (tok.line, tok.col)
        if tok.kind == "KW" and tok.value == "let":
            self.advance()
            name = self.expect("IDENT").value
            self.expect("OP", "=")
            expr = self.parse_expr()
            self.expect("OP", ";")
            return ("let", name, expr, pos)
        if tok.kind == "KW" and tok.value == "print":
            self.advance()
            expr = self.parse_expr()
            self.expect("OP", ";")
            return ("print", expr, pos)
        if tok.kind == "KW" and tok.value == "return":
            self.advance()
            expr = None if self.at("OP", ";") else self.parse_expr()
            self.expect("OP", ";")
            return ("return", expr, pos)
        if tok.kind == "KW" and tok.value == "if":
            self.advance()
            cond = self.parse_expr()
            then_stmts = self.parse_block()
            else_stmts = []
            if self.at("KW", "else"):
                self.advance()
                else_stmts = [self.parse_stmt()] if self.at("KW", "if") else self.parse_block()
            return ("if", cond, then_stmts, else_stmts, pos)
        if tok.kind == "KW" and tok.value == "while":
            self.advance()
            cond = self.parse_expr()
            return ("while", cond, self.parse_block(), pos)
        if tok.kind == "KW" and tok.value == "fn":
            self.advance()
            name = self.expect("IDENT").value
            self.expect("OP", "(")
            params = []
            while not self.at("OP", ")"):
                pname = self.expect("IDENT").value
                self.expect("OP", ":")
                params.append((pname, self.parse_type()))
                if not self.at("OP", ")"):
                    self.expect("OP", ",")
            self.expect("OP", ")")
            ret = "void"
            if self.at("OP", "->"):
                self.advance()
                ret = self.parse_type()
            return ("fn", name, params, ret, self.parse_block(), pos)
        nxt = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else self.peek()
        if tok.kind == "IDENT" and nxt.kind == "OP" and nxt.value == "=":
            name = self.advance().value
            self.advance()
            expr = self.parse_expr()
            self.expect("OP", ";")
            return ("assign", name, expr, pos)
        expr = self.parse_expr()
        self.expect("OP", ";")
        return ("expr", expr, pos)

    def parse_expr(self, min_prec=1):
        left = self.parse_unary()
        while True:
            tok = self.peek()
            if tok.kind != "OP" or tok.value not in PRECEDENCE:
                break
            prec = PRECEDENCE[tok.value]
            if prec < min_prec:
                break
            op = self.advance().value
            pos = (tok.line, tok.col)
            next_min = prec if op in RIGHT_ASSOCIATIVE else prec + 1
            right = self.parse_expr(next_min)
            left = ("bin", op, left, right, pos)
        return left

    def parse_unary(self):
        tok = self.peek()
        if tok.kind == "OP" and tok.value in ("-", "!"):
            self.advance()
            return ("unary", tok.value, self.parse_expr(UNARY_BIND), (tok.line, tok.col))
        return self.parse_primary()

    def parse_primary(self):
        tok = self.peek()
        pos = (tok.line, tok.col)
        if tok.kind == "NUM":
            return ("num", self.advance().value, pos)
        if tok.kind == "STR":
            return ("str", self.advance().value, pos)
        if tok.kind == "KW" and tok.value in ("true", "false"):
            return ("bool", self.advance().value == "true", pos)
        if tok.kind == "IDENT":
            name = self.advance().value
            if self.at("OP", "("):
                self.advance()
                args = []
                while not self.at("OP", ")"):
                    args.append(self.parse_expr())
                    if not self.at("OP", ")"):
                        self.expect("OP", ",")
                self.expect("OP", ")")
                return ("call", name, args, pos)
            return ("var", name, pos)
        if tok.kind == "OP" and tok.value == "(":
            self.advance()
            inner = self.parse_expr()
            self.expect("OP", ")")
            return inner
        raise ParseError(f"unexpected token {tok.value!r}", tok.line, tok.col)


def parse(src):
    """Source text -> a list of statement nodes."""
    return Parser(tokenize(src)).parse_program()


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def push(self):
        self.scopes.append({})

    def pop(self):
        self.scopes.pop()

    def depth(self):
        return len(self.scopes)

    def declare(self, name, type_, pos=(1, 1)):
        if name in self.scopes[-1]:
            raise SemanticError(f"{name!r} is already declared in this scope", pos[0], pos[1])
        self.scopes[-1][name] = type_
        return type_

    def lookup(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None


def type_of(node, table):
    kind = node[0]
    if kind in ("num", "str", "bool"):
        return kind
    if kind == "var":
        _, name, pos = node
        found = table.lookup(name)
        if found is None:
            raise SemanticError(f"undefined variable {name!r}", pos[0], pos[1])
        if isinstance(found, tuple):
            raise SemanticError(f"{name!r} is a function, not a value", pos[0], pos[1])
        return found
    if kind == "unary":
        _, op, operand, pos = node
        actual = type_of(operand, table)
        if op == "-" and actual != "num":
            raise SemanticError(f"cannot negate {actual}", pos[0], pos[1])
        if op == "!" and actual != "bool":
            raise SemanticError(f"cannot apply '!' to {actual}", pos[0], pos[1])
        return actual
    if kind == "bin":
        _, op, left, right, pos = node
        lt, rt = type_of(left, table), type_of(right, table)
        if op in ARITHMETIC:
            if op == "+" and lt == "str" and rt == "str":
                return "str"
            if lt == "num" and rt == "num":
                return "num"
            raise SemanticError(f"cannot apply {op!r} to {lt} and {rt}", pos[0], pos[1])
        if op in COMPARISON:
            if lt == "num" and rt == "num":
                return "bool"
            raise SemanticError(f"cannot apply {op!r} to {lt} and {rt}", pos[0], pos[1])
        if op in EQUALITY:
            if lt != rt:
                raise SemanticError(f"cannot compare {lt} with {rt}", pos[0], pos[1])
            return "bool"
        if op in LOGICAL:
            if lt == "bool" and rt == "bool":
                return "bool"
            raise SemanticError(f"cannot apply {op!r} to {lt} and {rt}", pos[0], pos[1])
        raise SemanticError(f"unknown operator {op!r}", pos[0], pos[1])
    if kind == "call":
        _, name, args, pos = node
        found = table.lookup(name)
        if found is None:
            raise SemanticError(f"undefined function {name!r}", pos[0], pos[1])
        if not isinstance(found, tuple) or found[0] != "fn":
            raise SemanticError(f"{name!r} is not a function", pos[0], pos[1])
        _, params, ret = found
        if len(args) != len(params):
            raise SemanticError(f"{name!r} takes {len(params)} argument(s), "
                                f"{len(args)} given", pos[0], pos[1])
        for index, (arg, want) in enumerate(zip(args, params), start=1):
            got = type_of(arg, table)
            if got != want:
                raise SemanticError(f"argument {index} of {name!r} is {got}, "
                                    f"expected {want}", pos[0], pos[1])
        return ret
    raise SemanticError(f"unknown expression {kind!r}", 1, 1)


def check_stmt(node, table, ret_type):
    kind = node[0]
    if kind == "let":
        _, name, expr, pos = node
        table.declare(name, type_of(expr, table), pos)
    elif kind == "assign":
        _, name, expr, pos = node
        declared = table.lookup(name)
        if declared is None:
            raise SemanticError(f"undefined variable {name!r}", pos[0], pos[1])
        if isinstance(declared, tuple):
            raise SemanticError(f"{name!r} is a function, not a value", pos[0], pos[1])
        actual = type_of(expr, table)
        if actual != declared:
            raise SemanticError(f"cannot assign {actual} to {declared} variable "
                                f"{name!r}", pos[0], pos[1])
    elif kind in ("print", "expr"):
        type_of(node[1], table)
    elif kind == "if":
        _, cond, then_stmts, else_stmts, pos = node
        require_bool(cond, table, "if")
        check_block(then_stmts, table, ret_type)
        check_block(else_stmts, table, ret_type)
    elif kind == "while":
        _, cond, body, pos = node
        require_bool(cond, table, "while")
        check_block(body, table, ret_type)
    elif kind == "return":
        _, expr, pos = node
        if ret_type is None:
            raise SemanticError("return outside a function", pos[0], pos[1])
        actual = "void" if expr is None else type_of(expr, table)
        if actual != ret_type:
            raise SemanticError(f"this function returns {ret_type}, not {actual}",
                                pos[0], pos[1])
    elif kind == "fn":
        _, name, params, ret, body, pos = node
        if table.depth() > 1:
            raise SemanticError("functions may only be declared at the top level",
                                pos[0], pos[1])
        table.push()
        for pname, ptype in params:
            table.declare(pname, ptype, pos)
        for stmt in body:
            check_stmt(stmt, table, ret)
        table.pop()
    else:
        raise SemanticError(f"unknown statement {kind!r}", 1, 1)


def require_bool(expr, table, what):
    actual = type_of(expr, table)
    if actual != "bool":
        pos = expr[-1]
        raise SemanticError(f"{what} condition must be bool, found {actual}",
                            pos[0], pos[1])


def check_block(stmts, table, ret_type):
    table.push()
    for stmt in stmts:
        check_stmt(stmt, table, ret_type)
    table.pop()


def check(program):
    """Type-check a program; return the global scope. Raises SemanticError."""
    table = SymbolTable()
    for node in program:
        if node[0] == "fn":
            _, name, params, ret, body, pos = node
            table.declare(name, ("fn", [t for _n, t in params], ret), pos)
    for node in program:
        check_stmt(node, table, None)
    return dict(table.scopes[0])
'''},
            {"name": "codegen.py", "content": r'''
from frontend import parse, check


class CompileError(Exception):
    pass


class VMError(Exception):
    pass


def format_value(value):
    """How the machine prints a value. Booleans first: True is also an int."""
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


class Compiler:
    def __init__(self):
        self.code = []
        self.functions = {}
        self.scope = {}

    def emit(self, op, arg=None):
        self.code.append((op, arg))
        return len(self.code) - 1

    def declare(self, name):
        """Slot for a local, allocating one on first mention."""
        # your code here

    def resolve(self, name):
        """Slot of an existing local, or CompileError."""
        # your code here

    def compile(self, program):
        """Main body, HALT, function bodies, then patch every CALL."""
        # your code here

    def compile_function(self, node):
        """One fn node, compiled into its own frame."""
        # your code here

    def compile_stmt(self, node):
        # your code here

    def compile_expr(self, node):
        # your code here


class VM:
    def __init__(self, max_steps=200000):
        self.max_steps = max_steps
        self.output = []

    def binary(self, op, left, right):
        """One BIN operator; VMError on division by zero."""
        # your code here

    def run(self, code):
        """Execute from address 0 until HALT; return the printed lines."""
        # your code here


def compile_source(src):
    """Source text -> instruction list. Front-end errors propagate."""
    # your code here


def run_source(src, max_steps=200000):
    """Source text -> the lines the program printed."""
    # your code here


def disassemble(code):
    """One line per instruction: 0000  ENTER  1"""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from codegen import compile_source, run_source, disassemble

CORPUS = [
    ("let a = 6;\nlet b = 7;\nprint a * b;\n", ["42"]),
    ("let i = 1;\nlet total = 0;\nwhile i <= 10 { total = total + i; i = i + 1; }\nprint total;\n",
     ["55"]),
]

for index, (source, expected) in enumerate(CORPUS, 1):
    got = run_source(source)
    print(f"[{'ok' if got == expected else 'FAIL'}] program {index}: {got}")

print(disassemble(compile_source("let x = 1;\nprint x;\n")))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "codegen.py", "content": r'''
from frontend import parse, check


class CompileError(Exception):
    pass


class VMError(Exception):
    pass


def format_value(value):
    """How the machine prints a value. Booleans first: True is also an int."""
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


class Compiler:
    """Tree -> a flat list of (op, arg) instructions."""

    def __init__(self):
        self.code = []
        self.functions = {}
        self.scope = {}

    def emit(self, op, arg=None):
        self.code.append((op, arg))
        return len(self.code) - 1

    def declare(self, name):
        """Slot for a local, allocating one on first mention."""
        if name not in self.scope:
            self.scope[name] = len(self.scope)
        return self.scope[name]

    def resolve(self, name):
        """Slot of an existing local, or CompileError."""
        if name not in self.scope:
            raise CompileError(f"undefined variable {name!r}")
        return self.scope[name]

    def compile(self, program):
        """Main body, HALT, function bodies, then patch every CALL."""
        self.scope = {}
        enter = self.emit("ENTER", 0)
        for node in program:
            if node[0] != "fn":
                self.compile_stmt(node)
        self.emit("HALT")
        self.code[enter] = ("ENTER", len(self.scope))
        for node in program:
            if node[0] == "fn":
                self.compile_function(node)
        for address, (op, arg) in enumerate(self.code):
            if op == "CALL" and isinstance(arg[0], str):
                name, nargs = arg
                if name not in self.functions:
                    raise CompileError(f"call to undefined function {name!r}")
                target, arity = self.functions[name]
                if arity != nargs:
                    raise CompileError(f"{name!r} takes {arity} argument(s), {nargs} given")
                self.code[address] = ("CALL", (target, nargs))
        return self.code

    def compile_function(self, node):
        """One fn node, compiled into its own frame."""
        _, name, params, ret, body, pos = node
        outer = self.scope
        self.scope = {}
        address = len(self.code)
        enter = self.emit("ENTER", 0)
        for pname, _ptype in params:
            self.declare(pname)
        self.functions[name] = (address, len(params))
        for stmt in body:
            self.compile_stmt(stmt)
        self.emit("PUSH", 0)
        self.emit("RET")
        self.code[enter] = ("ENTER", len(self.scope))
        self.scope = outer

    def compile_stmt(self, node):
        kind = node[0]
        if kind == "let":
            self.compile_expr(node[2])
            self.emit("STORE", self.declare(node[1]))
        elif kind == "assign":
            self.compile_expr(node[2])
            self.emit("STORE", self.resolve(node[1]))
        elif kind == "print":
            self.compile_expr(node[1])
            self.emit("PRINT")
        elif kind == "expr":
            self.compile_expr(node[1])
            self.emit("POP")
        elif kind == "return":
            if node[1] is None:
                self.emit("PUSH", 0)
            else:
                self.compile_expr(node[1])
            self.emit("RET")
        elif kind == "if":
            _, cond, then_stmts, else_stmts, pos = node
            self.compile_expr(cond)
            jz = self.emit("JZ", 0)
            for stmt in then_stmts:
                self.compile_stmt(stmt)
            if else_stmts:
                jmp = self.emit("JMP", 0)
                self.code[jz] = ("JZ", len(self.code))
                for stmt in else_stmts:
                    self.compile_stmt(stmt)
                self.code[jmp] = ("JMP", len(self.code))
            else:
                self.code[jz] = ("JZ", len(self.code))
        elif kind == "while":
            _, cond, body, pos = node
            start = len(self.code)
            self.compile_expr(cond)
            jz = self.emit("JZ", 0)
            for stmt in body:
                self.compile_stmt(stmt)
            self.emit("JMP", start)
            self.code[jz] = ("JZ", len(self.code))
        elif kind == "fn":
            raise CompileError("functions may only be declared at the top level")
        else:
            raise CompileError(f"unknown statement {kind!r}")

    def compile_expr(self, node):
        kind = node[0]
        if kind in ("num", "str", "bool"):
            self.emit("PUSH", node[1])
        elif kind == "var":
            self.emit("LOAD", self.resolve(node[1]))
        elif kind == "unary":
            self.compile_expr(node[2])
            self.emit("NEG" if node[1] == "-" else "NOT")
        elif kind == "bin":
            _, op, left, right, pos = node
            if op == "&&":
                self.compile_expr(left)
                jz = self.emit("JZ", 0)
                self.compile_expr(right)
                jmp = self.emit("JMP", 0)
                self.code[jz] = ("JZ", len(self.code))
                self.emit("PUSH", False)
                self.code[jmp] = ("JMP", len(self.code))
            elif op == "||":
                self.compile_expr(left)
                jz = self.emit("JZ", 0)
                self.emit("PUSH", True)
                jmp = self.emit("JMP", 0)
                self.code[jz] = ("JZ", len(self.code))
                self.compile_expr(right)
                self.code[jmp] = ("JMP", len(self.code))
            else:
                self.compile_expr(left)
                self.compile_expr(right)
                self.emit("BIN", op)
        elif kind == "call":
            _, name, args, pos = node
            for arg in args:
                self.compile_expr(arg)
            self.emit("CALL", (name, len(args)))
        else:
            raise CompileError(f"unknown expression {kind!r}")


class VM:
    """The stack machine the compiler targets."""

    def __init__(self, max_steps=200000):
        self.max_steps = max_steps
        self.output = []

    def binary(self, op, left, right):
        """One BIN operator; VMError on division by zero."""
        if op == "+":
            return left + right
        if op == "-":
            return left - right
        if op == "*":
            return left * right
        if op in ("/", "%"):
            if right == 0:
                raise VMError("division by zero")
            return left / right if op == "/" else left % right
        if op == "^":
            return left ** right
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        raise VMError(f"unknown operator {op!r}")

    def run(self, code):
        """Execute from address 0 until HALT; return the printed lines."""
        self.output = []
        stack = []
        frames = [{"locals": [], "ret": None}]
        pc = 0
        steps = 0
        while True:
            steps += 1
            if steps > self.max_steps:
                raise VMError("step limit exceeded")
            if pc < 0 or pc >= len(code):
                raise VMError(f"program counter {pc} is outside the code")
            op, arg = code[pc]
            pc += 1
            if op == "ENTER":
                locals_ = frames[-1]["locals"]
                while len(locals_) < arg:
                    locals_.append(0)
            elif op == "PUSH":
                stack.append(arg)
            elif op == "LOAD":
                stack.append(frames[-1]["locals"][arg])
            elif op == "STORE":
                frames[-1]["locals"][arg] = stack.pop()
            elif op == "POP":
                stack.pop()
            elif op == "NEG":
                stack.append(-stack.pop())
            elif op == "NOT":
                stack.append(not stack.pop())
            elif op == "BIN":
                right = stack.pop()
                left = stack.pop()
                stack.append(self.binary(arg, left, right))
            elif op == "JMP":
                pc = arg
            elif op == "JZ":
                if not stack.pop():
                    pc = arg
            elif op == "PRINT":
                self.output.append(format_value(stack.pop()))
            elif op == "CALL":
                target, nargs = arg
                cut = len(stack) - nargs
                args = stack[cut:]
                del stack[cut:]
                frames.append({"locals": args, "ret": pc})
                pc = target
            elif op == "RET":
                value = stack.pop()
                frame = frames.pop()
                if not frames:
                    raise VMError("return outside a call")
                pc = frame["ret"]
                stack.append(value)
            elif op == "HALT":
                return self.output
            else:
                raise VMError(f"unknown opcode {op!r}")


def compile_source(src):
    """Source text -> instruction list. Front-end errors propagate."""
    program = parse(src)
    check(program)
    return Compiler().compile(program)


def run_source(src, max_steps=200000):
    """Source text -> the lines the program printed."""
    return VM(max_steps=max_steps).run(compile_source(src))


def disassemble(code):
    """One line per instruction: 0000  ENTER  1"""
    lines = []
    for address, (op, arg) in enumerate(code):
        text = "" if arg is None else str(arg)
        lines.append(f"{address:04d}  {op:<6} {text}".rstrip())
    return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from codegen import compile_source, run_source, disassemble

CORPUS = [
    ("let a = 6;\nlet b = 7;\nprint a * b;\n", ["42"]),

    ("let i = 1;\nlet total = 0;\nwhile i <= 10 { total = total + i; i = i + 1; }\nprint total;\n",
     ["55"]),

    ("fn gcd(a: num, b: num) -> num {\n"
     "  while b != 0 { let t = b; b = a % b; a = t; }\n"
     "  return a;\n}\n"
     "print gcd(1071, 462);\n", ["21"]),

    ('let name = "world";\nprint "hello " + name;\nprint 3 < 4;\nprint !(3 < 4);\n',
     ["hello world", "true", "false"]),

    ('fn classify(n: num) -> str {\n'
     '  if n < 0 { return "negative"; } else if n == 0 { return "zero"; }\n'
     '  return "positive";\n}\n'
     'print classify(-5);\nprint classify(0);\nprint classify(7);\n',
     ["negative", "zero", "positive"]),

    ("fn fib(n: num) -> num {\n"
     "  if n < 2 { return n; }\n"
     "  return fib(n - 1) + fib(n - 2);\n}\n"
     "let i = 0;\nwhile i < 10 { print fib(i); i = i + 1; }\n",
     ["0", "1", "1", "2", "3", "5", "8", "13", "21", "34"]),

    ("let x = 0;\n"
     "if x != 0 && 10 / x > 1 { print \"boom\"; } else { print \"safe\"; }\n",
     ["safe"]),
]

for index, (source, expected) in enumerate(CORPUS, 1):
    got = run_source(source)
    print(f"[{'ok' if got == expected else 'FAIL'}] program {index}: {got}")

print(disassemble(compile_source("let x = 1;\nprint x;\n")))
'''},
        ],
        "tests": [
            {"name": "Arithmetic, precedence and associativity", "code": r'''
from codegen import run_source
for _src, _want in [("print 1 + 2 * 3;", ["7"]),
                    ("print (1 + 2) * 3;", ["9"]),
                    ("print 7 / 2;", ["3.5"]),
                    ("print 6 / 3;", ["2"]),
                    ("print 2 ^ 3 ^ 2;", ["512"]),
                    ("print 1 - 2 - 3;", ["-4"]),
                    ("print -2 ^ 2;", ["-4"]),
                    ("print 17 % 5;", ["2"])]:
    _got = run_source(_src)
    assert _got == _want, f"run_source({_src!r}) gave {_got!r}, expected {_want!r}"
'''},
            {"name": "Strings, booleans and how values print", "code": r'''
from codegen import run_source
_got = run_source('let s = "ab";\ns = s + "c";\nprint s;\nprint true;\nprint 1 == 2;\n')
assert _got == ["abc", "true", "false"], f"got {_got!r}, expected ['abc', 'true', 'false']"
_got = run_source('print "tab:\\there";')
assert _got == ["tab:\there"], f"escapes should be decoded by the lexer, got {_got!r}"
'''},
            {"name": "Variables, assignment and loops", "code": r'''
from codegen import run_source
_src = "let i = 1;\nlet total = 0;\nwhile i <= 10 { total = total + i; i = i + 1; }\nprint total;\n"
assert run_source(_src) == ["55"], f"summing 1..10 gave {run_source(_src)!r}"
_src = "let n = 0;\nwhile n < 0 { print n; }\nprint \"done\";\n"
assert run_source(_src) == ["done"], "a guard that is false at once runs the body zero times"
'''},
            {"name": "Branching, including else-if chains", "code": r'''
from codegen import run_source
_src = ('fn classify(n: num) -> str {\n'
        '  if n < 0 { return "negative"; } else if n == 0 { return "zero"; }\n'
        '  return "positive";\n}\n'
        'print classify(-5);\nprint classify(0);\nprint classify(7);\n')
_got = run_source(_src)
assert _got == ["negative", "zero", "positive"], f"got {_got!r}"
'''},
            {"name": "Functions, frames and recursion", "code": r'''
from codegen import run_source
_src = ("fn fact(n: num) -> num {\n  if n <= 1 { return 1; }\n"
        "  return n * fact(n - 1);\n}\nprint fact(6);\n")
assert run_source(_src) == ["720"], f"fact(6) gave {run_source(_src)!r}"
_src = ("fn fib(n: num) -> num {\n  if n < 2 { return n; }\n"
        "  return fib(n - 1) + fib(n - 2);\n}\nprint fib(12);\n")
assert run_source(_src) == ["144"], f"fib(12) gave {run_source(_src)!r}"
_src = ("let x = 5;\nfn double(y: num) -> num { let x = y * 2; return x; }\n"
        "print double(3);\nprint x;\n")
_got = run_source(_src)
assert _got == ["6", "5"], f"got {_got!r} — a callee must not touch the caller's locals"
_src = 'fn shout(s: str) { print s; }\nshout("hi");\nprint "end";\n'
assert run_source(_src) == ["hi", "end"], f"void call gave {run_source(_src)!r}"
'''},
            {"name": "&& and || short-circuit", "code": r'''
from codegen import run_source
_src = 'let x = 0;\nif x != 0 && 10 / x > 1 { print "boom"; } else { print "safe"; }\n'
assert run_source(_src) == ["safe"], f"got {run_source(_src)!r} — && must not evaluate the right side"
_src = 'let x = 0;\nprint x == 0 || 10 / x > 1;\n'
assert run_source(_src) == ["true"], f"got {run_source(_src)!r} — || must short-circuit too"
'''},
            {"name": "The instruction list is well formed", "code": r'''
from codegen import compile_source
_code = compile_source("let x = 1;\nprint x;\n")
_want = [("ENTER", 1), ("PUSH", 1), ("STORE", 0),
         ("LOAD", 0), ("PRINT", None), ("HALT", None)]
assert _code == _want, f"compiled to {_code!r}, expected {_want!r}"
_code = compile_source("fn f(a: num) -> num { return a; }\nprint f(1);\n")
assert all(isinstance(i, tuple) and len(i) == 2 for i in _code), \
    "every instruction is an (op, arg) pair"
_calls = [arg for op, arg in _code if op == "CALL"]
assert _calls and all(isinstance(a[0], int) for a in _calls), \
    f"CALL should carry a patched address, got {_calls!r}"
assert _code[_calls[0][0]][0] == "ENTER", "a CALL target is the ENTER of a function body"
assert ("HALT", None) in _code, "the main body ends in HALT"
'''},
            {"name": "disassemble prints one line per instruction", "code": r'''
from codegen import compile_source, disassemble
_code = compile_source("let x = 1;\nprint x;\n")
_text = disassemble(_code)
assert isinstance(_text, str), "disassemble returns a string"
_lines = _text.split("\n")
assert len(_lines) == len(_code), f"{len(_lines)} lines for {len(_code)} instructions"
assert _lines[0].startswith("0000"), f"first line was {_lines[0]!r}, expected a 0000 address"
assert "ENTER" in _lines[0] and "HALT" in _lines[-1], f"listing was:\n{_text}"
assert not _lines[-1].endswith(" "), "an instruction with no argument leaves no trailing space"
'''},
            {"name": "Every phase reports its own failure", "code": r'''
from frontend import LexError, ParseError, SemanticError
from codegen import run_source, compile_source, VMError
for _src, _exc in [("let x = $;", LexError),
                   ("let x = ;", ParseError),
                   ("let x = 1", ParseError),
                   ("print y;", SemanticError),
                   ("let x = 1 + true;", SemanticError),
                   ('let x = 1;\nx = "s";', SemanticError),
                   ("if 1 { print 1; }", SemanticError),
                   ("fn f(a: num) -> num { return a; }\nprint f(1, 2);", SemanticError)]:
    try:
        compile_source(_src)
        assert False, f"{_src!r} should raise {_exc.__name__}"
    except _exc:
        pass
try:
    run_source("print 1 / 0;")
    assert False, "division by zero should raise VMError"
except VMError:
    pass
try:
    run_source("while true { }", max_steps=500)
    assert False, "an endless loop should exhaust the step budget"
except VMError as _e:
    assert "step" in str(_e), f"VMError said {str(_e)!r}"
'''},
            {"name": "The corpus in main.py runs and matches", "code": r'''
from codegen import run_source
assert len(CORPUS) >= 6, f"the corpus has {len(CORPUS)} programs, at least 6 are required"
for _i, (_src, _want) in enumerate(CORPUS, 1):
    _got = run_source(_src)
    assert _got == _want, f"corpus program {_i} printed {_got!r}, expected {_want!r}"
assert "FAIL" not in _out, f"main.py reported a failing corpus program:\n{_out}"
assert "0000" in _out, "main.py should finish by printing a disassembly"
'''},
            {"name": "codegen.py is import-clean", "code": r'''
_src = open("codegen.py").read()
assert "print(" not in _src, "codegen.py is a library — the printing belongs in main.py"
for _forbidden in ("eval(", "exec("):
    assert _forbidden not in _src, f"{_forbidden} has no place in a compiler you wrote yourself"
'''},
        ],
    },
}
