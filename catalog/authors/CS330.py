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

The rules that *drop* an operand (`x * 0`, `x - x`, `false && x`) are only
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
