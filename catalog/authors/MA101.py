"""MA101 — Discrete Mathematics."""

COURSE = {
    "id": "MA101",
    "title": "Discrete Mathematics",
    "year": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Python"],
    "credits": 10,
    "hours": 110,
    "icon": "∀",
    "summary": (
        "The mathematics computers are actually made of: statements that are true or "
        "false, objects you can count exactly, integers under a modulus, and the "
        "relations and graphs that structure everything else. It closes on the two "
        "ideas the rest of the degree runs on and nothing else here supplies — how a "
        "cost is bounded as the input grows, and what counting can still mean once the "
        "set is infinite. Every definition in the course is turned into code, so a "
        "claim you cannot implement is a claim you have not yet understood."
    ),
    "outcomes": [
        "Translate an English argument into propositional logic and test it mechanically",
        "Build a truth table and classify a formula as tautology, contradiction or contingency",
        "Count arrangements and selections from first principles, without library shortcuts",
        "Prove and use the binomial identities behind Pascal's triangle",
        "Apply Euclid's algorithm, modular inverses and fast exponentiation to integers",
        "Decide whether a relation is reflexive, symmetric, transitive or an equivalence",
        "Compute transitive closures and two-colourings on graphs and explain their meaning",
        "Sum a geometric series in closed form and exhibit the constant and threshold behind an O, Omega or Theta claim",
        "Show a set countable by exhibiting a listing, and show one uncountable by the diagonal argument",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone toolkit (60%).",
    "reading": [
        "Rosen, *Discrete Mathematics and Its Applications*, 8th ed. — chapters 1-2, 5-6, 9-10",
        "Lehman, Leighton & Meyer, *Mathematics for Computer Science* (MIT 6.042 notes) — parts I-III",
        "Graham, Knuth & Patashnik, *Concrete Mathematics*, 2nd ed. — chapter 5",
        "Cormen, Leiserson, Rivest & Stein, *Introduction to Algorithms*, 4th ed. — chapter 3, for the asymptotic definitions in the form the algorithms courses use them",
        "Sipser, *Introduction to the Theory of Computation*, 3rd ed. — section 4.2, for countability and the diagonal argument",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Propositional logic",
            "summary": "Statements, connectives, truth tables, and equivalence decided by machine.",
            "concepts": [
                "A proposition is a statement with exactly one truth value",
                "The connectives: negation, conjunction, disjunction, implication",
                "Material implication: `P -> Q` is false only when P is true and Q is false",
                "Precedence `~` > `&` > `|` > `->`, with implication associating to the right",
                "A formula over n variables has 2^n rows in its truth table",
                "Tautology, contradiction, contingency — and logical equivalence as identical columns",
                "De Morgan's laws, contraposition, and `P -> Q` as `~P | Q`",
            ],
            "lab": {
                "title": "A propositional logic engine",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Build a small engine that reads a formula, evaluates it, tabulates it and
classifies it.

## Concrete syntax

```text
~   negation        &   conjunction
|   disjunction     ->  implication
```

Variables are identifiers: a letter followed by letters, digits or underscores
(`P`, `Q`, `rain`, `is_wet`). Parentheses group. Precedence, tightest first:
`~`, then `&`, then `|`, then `->`. Implication associates to the **right**, so
`P -> Q -> R` means `P -> (Q -> R)`.

## `tokenise(text)`

A list of token strings. Whitespace separates but is not a token. Any other
character is a `ValueError`.

```text
tokenise("P -> Q")   ->  ["P", "->", "Q"]
tokenise("~(A&B)")   ->  ["~", "(", "A", "&", "B", ")"]
tokenise("P # Q")    ->  ValueError
```

## `parse(tokens)`

Recursive descent into a nested-tuple abstract syntax tree:

```text
("var", "P")            ("not", node)
("and", left, right)    ("or", left, right)     ("implies", left, right)

parse(tokenise("~P | Q & R"))
  -> ("or", ("not", ("var", "P")), ("and", ("var", "Q"), ("var", "R")))
```

Anything malformed — `"P &"`, `"(P"`, `"P )"`, `"& Q"`, `""` — is a `ValueError`.

## The rest

- `variables(node)` — the variable names, sorted, without duplicates.
- `evaluate(node, env)` — the truth value under a dict of variable to bool.
- `truth_table(formula)` — takes the **source text** and returns
  `(names, rows)`. `rows` is a list of `(values, result)` pairs where `values`
  is a tuple lining up with `names`, enumerated in binary-counting order with
  `False` first.
- `classify(formula)` — `"tautology"`, `"contradiction"` or `"contingency"`.
- `equivalent(first, second)` — do the two formulas agree on every assignment
  of the **union** of their variables?

```text
classify("P | ~P")             ->  "tautology"
classify("P & ~P")             ->  "contradiction"
classify("P -> Q")             ->  "contingency"
equivalent("P -> Q", "~P | Q") ->  True
```
''',
                "files": [{"name": "main.py", "content": r'''
import itertools
import re

TOKEN_RE = re.compile(r"->|[~&|()]|[A-Za-z][A-Za-z0-9_]*")


def tokenise(text):
    """Split a formula into token strings. ValueError on an illegal character."""
    # your code here


def parse(tokens):
    """Turn a token list into a nested-tuple AST. ValueError when malformed."""
    # your code here


def variables(node):
    """The sorted, deduplicated variable names appearing in the AST."""
    # your code here


def evaluate(node, env):
    """The truth value of the AST under env: {name: bool}."""
    # your code here


def truth_table(formula):
    """(names, rows) for the formula source text."""
    # your code here


def classify(formula):
    """tautology, contradiction or contingency."""
    # your code here


def equivalent(first, second):
    """Do the two formulas agree on every assignment?"""
    # your code here


names, rows = truth_table("P -> Q")
print(" ".join(names), "| P -> Q")
for values, result in rows:
    print(" ".join("T" if v else "F" for v in values), "|", "T" if result else "F")
print(classify("P | ~P"), classify("P & ~P"), classify("P -> Q"))
print(equivalent("P -> Q", "~P | Q"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import itertools
import re

TOKEN_RE = re.compile(r"->|[~&|()]|[A-Za-z][A-Za-z0-9_]*")


def tokenise(text):
    """Split a formula into token strings. ValueError on an illegal character."""
    tokens = []
    position = 0
    while position < len(text):
        if text[position].isspace():
            position += 1
            continue
        match = TOKEN_RE.match(text, position)
        if match is None:
            raise ValueError(f"unexpected character {text[position]!r} at {position}")
        tokens.append(match.group(0))
        position = match.end()
    return tokens


def parse(tokens):
    """Turn a token list into a nested-tuple AST. ValueError when malformed."""
    node, position = _implication(tokens, 0)
    if position != len(tokens):
        raise ValueError(f"unexpected token {tokens[position]!r}")
    return node


def _implication(tokens, position):
    left, position = _disjunction(tokens, position)
    if position < len(tokens) and tokens[position] == "->":
        right, position = _implication(tokens, position + 1)
        return ("implies", left, right), position
    return left, position


def _disjunction(tokens, position):
    node, position = _conjunction(tokens, position)
    while position < len(tokens) and tokens[position] == "|":
        right, position = _conjunction(tokens, position + 1)
        node = ("or", node, right)
    return node, position


def _conjunction(tokens, position):
    node, position = _unary(tokens, position)
    while position < len(tokens) and tokens[position] == "&":
        right, position = _unary(tokens, position + 1)
        node = ("and", node, right)
    return node, position


def _unary(tokens, position):
    if position >= len(tokens):
        raise ValueError("formula ended too early")
    token = tokens[position]
    if token == "~":
        node, position = _unary(tokens, position + 1)
        return ("not", node), position
    if token == "(":
        node, position = _implication(tokens, position + 1)
        if position >= len(tokens) or tokens[position] != ")":
            raise ValueError("missing closing parenthesis")
        return node, position + 1
    if not token[0].isalpha():
        raise ValueError(f"expected a variable, found {token!r}")
    return ("var", token), position + 1


def variables(node):
    """The sorted, deduplicated variable names appearing in the AST."""
    found = set()
    stack = [node]
    while stack:
        current = stack.pop()
        if current[0] == "var":
            found.add(current[1])
        else:
            stack.extend(current[1:])
    return sorted(found)


def evaluate(node, env):
    """The truth value of the AST under env: {name: bool}."""
    kind = node[0]
    if kind == "var":
        if node[1] not in env:
            raise KeyError(f"no value given for {node[1]!r}")
        return bool(env[node[1]])
    if kind == "not":
        return not evaluate(node[1], env)
    if kind == "and":
        return evaluate(node[1], env) and evaluate(node[2], env)
    if kind == "or":
        return evaluate(node[1], env) or evaluate(node[2], env)
    if kind == "implies":
        return (not evaluate(node[1], env)) or evaluate(node[2], env)
    raise ValueError(f"unknown node kind {kind!r}")


def truth_table(formula):
    """(names, rows) for the formula source text."""
    node = parse(tokenise(formula))
    names = variables(node)
    rows = []
    for values in itertools.product([False, True], repeat=len(names)):
        rows.append((values, evaluate(node, dict(zip(names, values)))))
    return names, rows


def classify(formula):
    """tautology, contradiction or contingency."""
    results = [result for _, result in truth_table(formula)[1]]
    if all(results):
        return "tautology"
    if not any(results):
        return "contradiction"
    return "contingency"


def equivalent(first, second):
    """Do the two formulas agree on every assignment?"""
    left = parse(tokenise(first))
    right = parse(tokenise(second))
    names = sorted(set(variables(left)) | set(variables(right)))
    for values in itertools.product([False, True], repeat=len(names)):
        env = dict(zip(names, values))
        if evaluate(left, env) != evaluate(right, env):
            return False
    return True


names, rows = truth_table("P -> Q")
print(" ".join(names), "| P -> Q")
for values, result in rows:
    print(" ".join("T" if v else "F" for v in values), "|", "T" if result else "F")
print(classify("P | ~P"), classify("P & ~P"), classify("P -> Q"))
print(equivalent("P -> Q", "~P | Q"))
'''}],
                "hints": [
                    "Tokenise with a loop over positions: skip whitespace, then `TOKEN_RE.match(text, position)`. A `None` match means the character is illegal.",
                    "Write one helper per precedence level, each taking `(tokens, position)` and returning `(node, position)`. The lowest level handles `~`, `(` and variables.",
                    "Left-associative levels (`&`, `|`) use a `while` loop that folds the node leftwards; right-associative `->` recurses into itself instead.",
                    "`itertools.product([False, True], repeat=len(names))` enumerates the rows in exactly the required order — 2^n of them, `False` first.",
                ],
                "tests": [
                    {"name": "tokenise splits and rejects", "code": r'''
assert tokenise("P -> Q") == ["P", "->", "Q"], f"got {tokenise('P -> Q')!r}"
assert tokenise("~(A&B)") == ["~", "(", "A", "&", "B", ")"], f"got {tokenise('~(A&B)')!r}"
assert tokenise("rain -> is_wet") == ["rain", "->", "is_wet"], "identifiers may be long"
assert tokenise("   ") == [], "only whitespace gives no tokens"
for _bad in ["P # Q", "P $ Q", "P -< Q", "3P"]:
    try:
        tokenise(_bad)
        assert False, f"tokenise({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "parse honours precedence and associativity", "code": r'''
_got = parse(tokenise("P -> Q"))
assert _got == ("implies", ("var", "P"), ("var", "Q")), f"got {_got!r}"
_got = parse(tokenise("~P | Q & R"))
_want = ("or", ("not", ("var", "P")), ("and", ("var", "Q"), ("var", "R")))
assert _got == _want, f"got {_got!r}, expected {_want!r}"
_got = parse(tokenise("P -> Q -> R"))
_want = ("implies", ("var", "P"), ("implies", ("var", "Q"), ("var", "R")))
assert _got == _want, f"-> must associate right; got {_got!r}"
_got = parse(tokenise("(P | Q) & R"))
_want = ("and", ("or", ("var", "P"), ("var", "Q")), ("var", "R"))
assert _got == _want, f"parentheses ignored; got {_got!r}"
assert parse(tokenise("~~P")) == ("not", ("not", ("var", "P"))), "negation stacks"
'''},
                    {"name": "parse rejects malformed input", "code": r'''
for _bad in ["P &", "(P", "P )", "& Q", "", "P Q", "~", "()"]:
    try:
        parse(tokenise(_bad))
        assert False, f"parse of {_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "evaluate implements the connectives", "code": r'''
_p = parse(tokenise("P"))
assert evaluate(_p, {"P": True}) is True and evaluate(_p, {"P": False}) is False
_imp = parse(tokenise("P -> Q"))
for _env, _want in [({"P": False, "Q": False}, True), ({"P": False, "Q": True}, True),
                    ({"P": True, "Q": False}, False), ({"P": True, "Q": True}, True)]:
    _got = evaluate(_imp, _env)
    assert _got == _want, f"P -> Q under {_env!r} gave {_got!r}, expected {_want}"
assert evaluate(parse(tokenise("~P & Q")), {"P": False, "Q": True}) is True
assert evaluate(parse(tokenise("P | Q")), {"P": False, "Q": False}) is False
'''},
                    {"name": "variables are sorted and deduplicated", "code": r'''
assert variables(parse(tokenise("Q & P & Q"))) == ["P", "Q"], \
    f"got {variables(parse(tokenise('Q & P & Q')))!r}"
assert variables(parse(tokenise("~P"))) == ["P"], "one variable, once"
assert variables(parse(tokenise("(b -> a) | c"))) == ["a", "b", "c"], "sorted by name"
'''},
                    {"name": "truth_table has the right shape and order", "code": r'''
_names, _rows = truth_table("P -> Q")
assert _names == ["P", "Q"], f"names are {_names!r}"
assert len(_rows) == 4, f"a 2-variable formula has 4 rows, got {len(_rows)}"
_want = [((False, False), True), ((False, True), True),
         ((True, False), False), ((True, True), True)]
assert _rows == _want, f"rows are {_rows!r}, expected {_want!r}"
_names1, _rows1 = truth_table("~P")
assert _names1 == ["P"] and _rows1 == [((False,), True), ((True,), False)], f"got {_rows1!r}"
assert len(truth_table("A & B & C")[1]) == 8, "three variables give eight rows"
'''},
                    {"name": "classify and equivalent", "code": r'''
assert classify("P | ~P") == "tautology", f"got {classify('P | ~P')!r}"
assert classify("P & ~P") == "contradiction", f"got {classify('P & ~P')!r}"
assert classify("P -> Q") == "contingency", f"got {classify('P -> Q')!r}"
assert classify("(P -> Q) | (Q -> P)") == "tautology", "one of the two implications always holds"
assert classify("P") == "contingency", "a bare variable is contingent"
assert equivalent("P -> Q", "~P | Q") is True, "material implication"
assert equivalent("~(P & Q)", "~P | ~Q") is True, "De Morgan"
assert equivalent("P -> Q", "~Q -> ~P") is True, "contraposition"
assert equivalent("P -> Q", "Q -> P") is False, "the converse is not equivalent"
assert equivalent("P", "P | (Q & ~Q)") is True, "the union of variables must be tried"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Predicate logic and quantifiers",
            "summary": "Statements about *every* and *some*, the domains they range over, and negation pushed all the way in.",
            "concepts": [
                "A predicate is a statement with a hole in it: `P(x)` has no truth value until both the hole and a domain are fixed",
                "`forall x P(x)` is a conjunction over the domain and `exists x P(x)` a disjunction over it — so on an empty domain the first is true and the second false",
                "Quantifier order changes the claim: `forall x exists y` lets `y` depend on `x`, while `exists y forall x` promises one `y` that works for every `x`",
                "Negation moves inward and flips: `~forall x P(x)` is `exists x ~P(x)`, and `~exists x P(x)` is `forall x ~P(x)`",
                "A variable is bound by the quantifier that captures it and free otherwise; a formula with a free variable is a predicate, not a proposition",
            ],
            "quiz": {
                "title": "Domains, order and negation",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Over an *empty* domain, what are the truth values of `forall x P(x)` and `exists x P(x)`?",
                        "opts": [
                            "Both are true",
                            "`forall x P(x)` is true and `exists x P(x)` is false",
                            "Both are false",
                            "Neither has a truth value — an empty domain is not permitted",
                        ],
                        "a": 1,
                        "why": """
`forall` over a domain behaves like a conjunction with one conjunct per element, and
an empty conjunction is true: there is no element available to break the claim.
`exists` behaves like a disjunction, and an empty disjunction is false: there is no
element available to witness it. This is not a convention chosen for tidiness. It is
what makes "every student who failed will resit" come out true in a year when nobody
failed, and it is why an empty domain is perfectly legal. Statements true for this
reason are called *vacuously* true, and they are the reason a proof must always check
whether its domain can be empty.
""",
                    },
                    {
                        "q": "Over the integers, `forall x exists y (y > x)` is true. What does `exists y forall x (y > x)` say?",
                        "opts": [
                            "The same thing, so it is also true",
                            "Nothing — mixing the two quantifiers this way is not a legal formula",
                            "That every integer exceeds some integer, which is true",
                            "That some single integer exceeds every integer, which is false",
                        ],
                        "a": 3,
                        "why": """
With `forall` outermost, `y` is chosen after `x` is known and may depend on it: given
`x`, take `y = x + 1`. With `exists` outermost, `y` is fixed once and for all and must
then beat every `x`, including `y` itself — a single largest integer, which does not
exist. The rule worth carrying is that an inner variable may look at an outer one but
never the reverse. Two quantifiers of the same kind commute freely; mixed ones almost
never do, and this is the single most common place a formalisation of an English
sentence goes wrong ("everybody loves somebody" against "somebody is loved by
everybody").
""",
                    },
                    {
                        "q": "What is the negation of `forall x (P(x) -> Q(x))`?",
                        "opts": [
                            "`forall x (P(x) -> ~Q(x))`",
                            "`exists x (P(x) -> ~Q(x))`",
                            "`exists x (P(x) & ~Q(x))`",
                            "`forall x (~P(x) & Q(x))`",
                        ],
                        "a": 2,
                        "why": """
Two steps, each a law you already have. Negating `forall` turns it into `exists` with
the body negated, giving `exists x ~(P(x) -> Q(x))`. Then `P -> Q` is `~P | Q`, so its
negation is `P & ~Q` by De Morgan. Together: some single `x` satisfies `P` and fails
`Q`. That is exactly what refuting "every prime is odd" looks like — you do not argue
about all numbers, you hand over the number 2. Leaving the body as an implication is
the usual slip and gives a strictly weaker claim, since `P(x) -> ~Q(x)` is satisfied
by any `x` that simply fails `P`.
""",
                    },
                    {
                        "q": "Which of these is a **proposition** — something with a definite truth value on its own?",
                        "opts": [
                            "`forall x (x > 3)`, with the domain stated as the integers above 5",
                            "`P(x) & Q(y)`",
                            "`x > 3`",
                            "`exists y (x < y)` over the integers",
                        ],
                        "a": 0,
                        "why": """
A quantifier binds its variable, and a formula whose variables are all bound — with a
domain stated — is a proposition. This one is true, since every integer above 5
exceeds 3. The rest leave a variable free: `x > 3` says nothing until `x` is supplied,
and `exists y (x < y)` binds `y` but leaves `x` free, so it remains a predicate in `x`.
A formula with a free variable is a question waiting for an argument, which is what a
predicate is. Note that the domain matters as much as the binding, since the same
formula over all the integers is false.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Methods of proof",
            "summary": "Direct, contrapositive, contradiction and cases — plus the single counterexample that ends an argument.",
            "concepts": [
                "A direct proof chains implications from hypothesis to conclusion, every step licensed by a definition or a result already established",
                "Contraposition proves `~Q -> ~P` in place of `P -> Q`; Module 1 showed the two are the same formula, so nothing is lost in the swap",
                "Contradiction assumes `P & ~Q` and derives an absurdity — the strongest hypothesis available, and the easiest technique to reach for when a direct proof was there all along",
                "Proof by cases must cover the whole domain; overlapping cases are harmless, a missing case is fatal",
                "One counterexample refutes a universal claim outright, while any number of confirming examples proves none — though one witness does settle an existential",
            ],
            "quiz": {
                "title": "What each proof owes you",
                "minutes": 7,
                "questions": [
                    {
                        "q": "To prove *if `n^2` is even then `n` is even*, why is contraposition the natural route?",
                        "opts": [
                            "Because the converse, *if `n` is even then `n^2` is even*, is easier and establishes the same thing",
                            "Because assuming `n` is odd hands you `n = 2k + 1` to compute with, whereas assuming `n^2` is even hands you almost nothing to grip",
                            "Because the statement as written is false and only its contrapositive is true",
                            "Because contraposition is required whenever the conclusion concerns parity",
                        ],
                        "a": 1,
                        "why": """
Pick the technique by what it gives you to work with. Starting from "`n^2` is even"
tells you `n^2 = 2m` and leaves you needing a square root — no algebra to hold on to.
Starting from "`n` is odd" gives `n = 2k + 1`, and then
`n^2 = 4k^2 + 4k + 1 = 2(2k^2 + 2k) + 1` is odd in one line, which is the contrapositive
established. The converse is a different statement and proving it would say nothing
about this one; conflating the two is how a proof ends up proving the wrong theorem. A
statement and its contrapositive are logically equivalent, so the switch is free.
""",
                    },
                    {
                        "q": "A claim says every integer `n^2 + n + 41` is prime. You check `n = 0` through `n = 39` and every value is prime. What have you established?",
                        "opts": [
                            "The claim, since forty consecutive confirmations is past any reasonable threshold",
                            "Nothing whatever — checked cases carry no information",
                            "That the claim holds for those forty integers and nothing about the rest; at `n = 40` the value is `41^2`, which is composite",
                            "That the claim is probably true, so it may be used as a lemma",
                        ],
                        "a": 2,
                        "why": """
A universal claim ranges over infinitely many integers, so finitely many confirmations
leave infinitely many untested. This is Euler's famous polynomial, and it fails at the
first value you did not reach: `40^2 + 40 + 41 = 1681 = 41 * 41`. Checked cases are not
worthless — each is a genuine proof of its own instance, and they are how you decide a
claim is worth attempting — but they never accumulate into the universal, and
"probably true" is not a status a theorem can have. The asymmetry runs the other way
for refutation: one failing `n` would have ended the claim on the spot.
""",
                    },
                    {
                        "q": "A proof by contradiction of `P -> Q` begins by assuming what?",
                        "opts": [
                            "`~P`, and derives `~Q`",
                            "`~P & ~Q`, and derives `P`",
                            "`Q`, and derives `P`",
                            "`P` and `~Q` together, and derives an absurdity",
                        ],
                        "a": 3,
                        "why": """
To contradict `P -> Q` you assume the one situation the implication forbids: the
hypothesis holding while the conclusion fails. From `P & ~Q` you drive at any absurdity
you like — `0 = 1`, or a number both even and odd — and since that assumption was the
only unjustified thing in the room, it is what must go. Assuming `~Q` and deriving `~P`
is contraposition, a different and usually cleaner proof that many textbook
"contradictions" secretly are. Beginning from `~P` assumes the implication is vacuously
true and proves nothing at all.
""",
                    },
                    {
                        "q": "Which of these claims is settled by exhibiting a single object?",
                        "opts": [
                            "Every graph on 5 vertices is bipartite",
                            "There is an even integer that is not the sum of two primes",
                            "For every integer `n`, `n^2 >= n`",
                            "No integer is both even and odd",
                        ],
                        "a": 1,
                        "why": """
An existential claim is proved by a witness: produce one such integer and the work is
finished. The other three are universal — "every", "for every", and "no integer",
which is `forall n ~(...)` in disguise — and a single object can only refute them,
never prove them. That is the shape worth memorising: one object settles an existential
affirmatively and a universal negatively. For the record, the bipartite claim is false
(a triangle plus two spare vertices), the square inequality is true over the integers,
and the parity claim falls to a one-line contradiction.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Sets, subsets and set algebra",
            "summary": "Membership, the operations that build new collections, and identities that mirror the connectives exactly.",
            "concepts": [
                "A set is fixed by its members alone — order and repetition carry no information, so `{a, b}`, `{b, a}` and `{a, b, b}` are one set",
                "Membership and inclusion are different relations: `a` is an element of `{a, b}` while `{a}` is a subset of it, and `A = B` means each is a subset of the other",
                "The power set of an n-element set has `2^n` members, one per subset — row for row the truth table of n variables",
                "Union, intersection, difference and complement obey De Morgan, distributivity and absorption, because they are the connectives of Module 1 acting on membership",
                "Inclusion-exclusion: `|A u B| = |A| + |B| - |A n B|`, with the alternating correction continuing for three sets and beyond",
            ],
            "quiz": {
                "title": "Members, subsets and the size of a union",
                "minutes": 7,
                "questions": [
                    {
                        "q": "How many subsets does `{1, 2, 3, 4, 5}` have, and why?",
                        "opts": [
                            "5 — one per element",
                            "25 — one per ordered pair of elements",
                            "32 — each element is independently in or out",
                            "120 — one per ordering of the elements",
                        ],
                        "a": 2,
                        "why": """
Building a subset means making one two-way decision per element, in or out, and the
five decisions are independent, so the product rule gives `2^5 = 32`. Both extremes
count: taking nothing gives the empty set, taking everything gives the whole set, and
both are genuine subsets. The correspondence with the 32 rows of a five-variable truth
table is exact, since a row is also a choice of in-or-out per variable — the same
counting problem in different notation. The 120 counts orderings, and a set has no
order, so orderings are not subsets of anything.
""",
                    },
                    {
                        "q": "Let `A = {1, {2}}`. Which statement is true?",
                        "opts": [
                            "`2` is an element of `A`",
                            "`{2}` is an element of `A`, and `{{2}}` is a subset of `A`",
                            "`{2}` is a subset of `A`",
                            "`A` has three elements",
                        ],
                        "a": 1,
                        "why": """
`A` has exactly two elements: the number `1` and the set `{2}`. So `{2}` is an element,
and the one-element collection containing it, `{{2}}`, is a subset — subsets are built
out of things that are elements of `A`. The number `2` is not an element of `A`; it is
an element of an element, and membership does not chain. For `{2}` to be a subset would
require `2` itself to be in `A`, which it is not. Keeping the two relations apart is
the whole discipline here, and it is why the empty set is a subset of every set but an
element of almost none.
""",
                    },
                    {
                        "q": "In a class of 30, 18 take Python, 15 take C, and 7 take both. How many take neither?",
                        "opts": [
                            "4",
                            "3",
                            "0",
                            "7",
                        ],
                        "a": 0,
                        "why": """
Adding 18 and 15 counts the 7 who take both twice, so inclusion-exclusion subtracts the
overlap once: `|P u C| = 18 + 15 - 7 = 26`. The rest of the class, `30 - 26 = 4`, take
neither. Answering 3 comes from skipping the correction and getting 33 students inside
a class of 30, which is already impossible — a sanity check worth running every time.
The subtracted term is not an ad-hoc patch either: it is the first step of a pattern
that keeps alternating as sets are added, taking pairs off, putting triples back, and
so on.
""",
                    },
                    {
                        "q": "Why is the set identity `~(A n B) = ~A u ~B` the same fact as De Morgan's law for `&` and `|`?",
                        "opts": [
                            "It is a coincidence of notation; the two are proved by unrelated arguments",
                            "Because union is defined as the intersection of complements, making the identity a definition",
                            "Because every set can be encoded as a bit string, and bit strings obey De Morgan",
                            "Because an element belongs to a set exactly when its membership statement is true, so each set identity is a propositional equivalence checked one element at a time",
                        ],
                        "a": 3,
                        "why": """
`x` lies in `A n B` exactly when "`x` is in `A`" and "`x` is in `B`" are both true, so
membership turns each set operation into a connective. The set identity therefore
asserts that `~(P & Q)` and `~P | ~Q` agree for every element, which is precisely the
propositional law you already checked with a truth table. That correspondence is why
the entire algebra of sets — distributivity, absorption, double complement — arrives
for free with no new proofs. The bit-string picture is real and useful, but it is a
consequence of this correspondence rather than the reason for it.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Functions and the pigeonhole principle",
            "summary": "One value per input, the three ways a function can be well behaved, and the counting argument hiding inside them.",
            "concepts": [
                "A function assigns exactly one codomain value to every element of its domain; a rule with a gap or a fork is not a function at all",
                "Injective means no two inputs collide, surjective means nothing in the codomain is missed, bijective means both — and only a bijection has a two-sided inverse",
                "Composition is associative but rarely commutative, and a composition of bijections is again a bijection",
                "The pigeonhole principle: no injection runs from a larger finite set into a smaller one, so some value must be hit twice",
                "Generalised pigeonhole: `n` items in `k` boxes force some box to hold at least `ceil(n/k)` of them",
                "Pigeonhole is a theorem about *finite* sets, and the word is load-bearing: `n -> 2n` is an injection from the naturals into a proper subset of themselves, which Module 13 takes as the definition of being infinite",
            ],
            "quiz": {
                "title": "Injections, inverses and pigeons",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Domain: all living people. Codomain: the integers `0..200`. Rule: age in whole years. Which description fits?",
                        "opts": [
                            "It is injective but not surjective",
                            "It is a function, and surjective but not injective",
                            "It is a function, and neither injective nor surjective",
                            "It is not a function, since two people can share an age",
                        ],
                        "a": 2,
                        "why": """
Sharing a value is exactly what a function is permitted to do; what it may not do is
give one input two values, or none. So this is a function, and it fails injectivity
resoundingly, since any two people of the same age collide. It also fails surjectivity,
because nobody is 200 and that codomain value goes unused. Injectivity is a condition
on the domain side (no collisions) and surjectivity on the codomain side (nothing
missed), and the two are independent — a rule that is not a function fails for a
different reason entirely, namely a gap or a fork on the input side.
""",
                    },
                    {
                        "q": "Why does only a bijection have a two-sided inverse?",
                        "opts": [
                            "Because the reversed rule needs a value for every codomain element (surjectivity) and only one such value (injectivity)",
                            "Because only bijections are computable",
                            "Because an inverse must share the domain of the original, which forces the two sets to be equal",
                            "Because non-bijections have inverses too, but of a different type",
                        ],
                        "a": 0,
                        "why": """
Reverse the arrows and ask whether what you get is still a function. It needs an output
for every element of the original codomain, which is surjectivity, and it needs exactly
one, which fails the moment two inputs shared a value — that is injectivity. Both
conditions are just the definition of a function applied in the opposite direction.
One-sided inverses exist without both: an injection has a left inverse and a surjection
a right inverse, neither of which undoes the map in both directions. Computability is a
separate matter — plenty of bijections have inverses nobody can compute quickly, which
is the entire premise of public-key cryptography.
""",
                    },
                    {
                        "q": "A hash function sends 1000 distinct keys into a table of 512 buckets. What does pigeonhole guarantee?",
                        "opts": [
                            "Some bucket holds at least `ceil(1000/512) = 2` keys",
                            "The hash function is badly designed",
                            "Every bucket holds at least one key",
                            "Exactly 488 buckets hold two keys each",
                        ],
                        "a": 0,
                        "why": """
With more keys than buckets no injection is available, so a collision is certain no
matter how good the hash is, and the generalised form sharpens "some collision" into
"some bucket holds at least `ceil(1000/512) = 2` keys". That is a lower bound on the
worst bucket, not a description of the distribution: the counts may be wildly uneven,
and no particular bucket is forced to be occupied at all, since in principle all 1000
keys could land in one. The argument says nothing about the quality of the hash —
collisions here are a counting fact, which is exactly why a hash table is built with a
collision strategy rather than a hope.
""",
                    },
                    {
                        "q": "Taking the bijection definition seriously, what does *the same size* mean for two sets?",
                        "opts": [
                            "They contain the same elements",
                            "One is a subset of the other",
                            "One can be injected into the other",
                            "A bijection exists between them — for finite sets this agrees with counting, and for infinite sets it is the only definition that survives",
                        ],
                        "a": 3,
                        "why": """
Pairing off is more primitive than counting: if every element of one set matches
exactly one element of the other with nothing left over on either side, the sets are
the same size, and for finite sets that is precisely what counting to the same number
establishes. Containing the same elements is equality, a far stronger condition, and
being a subset does not imply equal size at all. An injection one way says only that
the first set is no larger than the second. The pairing definition earns its care by
surviving past the finite case, where it yields the surprise that the even integers
pair off one-for-one with all the integers.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M6
        {
            "title": "Induction and recursive definitions",
            "summary": "Base case, inductive step, and the recursively defined objects that induction exists to reason about.",
            "concepts": [
                "Weak induction: prove `P(0)`, prove `P(k) -> P(k+1)` for an arbitrary `k`, and conclude `P(n)` for every natural `n`",
                "The inductive hypothesis is an assumption about one particular `k`, not the statement being proved; a step that never uses it is a sign something has gone wrong",
                "Strong induction assumes `P(0)` through `P(k)` at once, which is what a recursion reaching further back than one step needs",
                "A recursive definition names base objects and rules for building more; structural induction then proves a property of exactly the objects those rules generate",
                "Nearly every failed induction is a missing base case or a step valid only above some threshold — the all-horses-one-colour argument fails on exactly this",
                "A closed form for a sum is the standard thing induction is asked to prove: it can confirm a formula but never propose one, which is why Module 12 derives the geometric sum by cancellation first and only then checks it",
            ],
            "quiz": {
                "title": "Base cases, hypotheses and what induction proves",
                "minutes": 7,
                "questions": [
                    {
                        "q": "The inductive step assumes `P(k)` and proves `P(k+1)`. Is that circular?",
                        "opts": [
                            "Yes, but the base case repairs the circularity",
                            "No — the step proves the implication `P(k) -> P(k+1)`, which is a claim about a link, not an assertion that `P(k)` holds",
                            "Yes, and induction is taken as an axiom precisely because it is circular",
                            "No, because `k` is a specific number chosen in advance",
                        ],
                        "a": 1,
                        "why": """
Nothing in the step claims `P(k)` is true. What it establishes is a conditional — if the
statement holds at `k` then it holds at `k+1` — for an arbitrary `k`, and a conditional
can be proved without its antecedent ever holding. The base case then supplies the one
unconditional fact, and the chain of links carries it upward forever. This is also why
`k` must be arbitrary rather than chosen: one specific link would prove one specific
instance and stop there. The induction axiom is where mathematics grants that a first
domino plus an infinite chain of links is enough.
""",
                    },
                    {
                        "q": "Which of these genuinely calls for **strong** induction rather than weak?",
                        "opts": [
                            "Every integer above 1 has a prime factorisation, since the factors of a composite `n` can be far below `n - 1`",
                            "The sum of the first `n` odd numbers is `n^2`",
                            "`2^n > n` for every natural `n`",
                            "Any statement quantified over the naturals",
                        ],
                        "a": 0,
                        "why": """
Strong induction earns its keep when the case at `n` leans on cases that are not
`n - 1`. Splitting a composite `n` as `a * b` produces two factors that may sit anywhere
below `n`, so the hypothesis has to cover everything down to the base rather than the
previous rung alone. The odd-number sum and `2^n > n` both step cleanly from `n` to
`n + 1` and need only the weak form. The two forms are in fact equally powerful —
anything provable with one is provable with the other — so the choice is about which
makes the argument short, not about which is permitted.
""",
                    },
                    {
                        "q": "The all-horses-are-one-colour proof does `n = 1` correctly and argues the step by overlapping two groups of `k` horses. Where does it break?",
                        "opts": [
                            "The base case should have been `n = 0`",
                            "It uses weak induction where strong induction was needed",
                            "At `k = 1` the two groups of one horse do not overlap, so the step fails at the very link it needs first",
                            "Nowhere — the argument is valid and its conclusion is a genuine paradox",
                        ],
                        "a": 2,
                        "why": """
The step argues that two overlapping subsets of size `k` share a horse whose colour ties
the groups together. For `k >= 2` that shared horse is really there, but going from one
horse to two the overlap is empty and the chain snaps at its first link. So the argument
establishes `P(1)` and `P(k) -> P(k+1)` only for `k >= 2`, and the rung it never proves
is `P(1) -> P(2)`. That is the standard failure mode in costume: a step silently valid
only above a threshold, with no base case at that threshold. Whenever a step splits,
overlaps or removes elements, check it by hand at the smallest case.
""",
                    },
                    {
                        "q": "A set `S` is defined recursively: `3` is in `S`, and if `x` and `y` are in `S` then so is `x + y`. What does structural induction let you prove?",
                        "opts": [
                            "That `S` is exactly the multiples of 3",
                            "Nothing, because `S` has no base case",
                            "That `S` is infinite",
                            "That every member of `S` is divisible by 3 — the reverse inclusion needs a separate argument",
                        ],
                        "a": 3,
                        "why": """
Structural induction checks the property on the base objects and shows the construction
rules preserve it: `3` is divisible by 3, and if `x` and `y` both are then so is `x + y`.
That covers every object the rules can produce, so every member of `S` is a multiple of
3. It does not give the reverse inclusion, and here the reverse is in fact false — `3`
is the smallest member, so `0` and the negative multiples are outside `S`. Pinning `S`
down exactly means showing each intended element is reachable, an ordinary induction on
the naturals that yields `S = {3, 6, 9, ...}`. The clause naming `3` is the base case.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M7
        {
            "title": "Counting and the binomial coefficients",
            "summary": "Products, permutations, selections, and the triangle that ties them together.",
            "concepts": [
                "The product and sum rules, and when a choice is independent",
                "Permutations P(n, k) = n!/(n-k)! — order matters",
                "Combinations C(n, k) = P(n, k)/k! — order does not",
                "The multiplicative form of C(n, k), which avoids ever building n!",
                "Pascal's rule C(n, k) = C(n-1, k-1) + C(n-1, k) and the triangle it generates",
                "Symmetry C(n, k) = C(n, n-k) and the row sum 2^n",
                "Vandermonde's identity as a counting argument, not an algebraic one",
                "The triangular number C(n+1, 2) = 1 + 2 + ... + n counts the pairs drawn from n+1 things, and Module 13 spends it on numbering the diagonals of an infinite grid",
            ],
            "lab": {
                "title": "Counting from first principles",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
No `math.factorial`, no `math.comb`, no `math.perm`. Build the counting
functions yourself — that is the exercise.

**`factorial(n)`** — iterative. `factorial(0)` is `1`. A negative `n` raises
`ValueError`.

**`permutations(n, k)`** — the number of ordered arrangements of `k` items
chosen from `n`. `permutations(5, 2)` is `20`; `permutations(5, 0)` is `1`;
`permutations(3, 5)` is `0`. A negative argument raises `ValueError`.

**`combinations(n, k)`** — the number of unordered selections. Compute it
multiplicatively so the intermediate values never explode:

```text
result = 1
for i in range(k):
    result = result * (n - i) // (i + 1)
```

That division is always exact. Use the symmetry `C(n, k) = C(n, n-k)` first, so
`combinations(40, 20)` does twenty steps rather than forty. `k` outside
`0..n` gives `0`; a negative `n` raises `ValueError`.

**`pascal_row(n)`** — row `n` of Pascal's triangle, built **additively** from
row `n-1`, not by calling `combinations`. `pascal_row(0)` is `[1]`;
`pascal_row(4)` is `[1, 4, 6, 4, 1]`.

**`pascal_triangle(rows)`** — the first `rows` rows as a list of lists.
`pascal_triangle(0)` is `[]`.

**`vandermonde_holds(m, n, r)`** — check Vandermonde's identity

```text
C(m + n, r) == sum over k of C(m, k) * C(n, r - k)   for k = 0 .. r
```

returning `True` or `False`.

**`catalan(n)`** — the n-th Catalan number `C(2n, n) // (n + 1)`. The first few
are `1, 1, 2, 5, 14, 42`.
''',
                "files": [{"name": "main.py", "content": r'''
def factorial(n):
    """n! computed iteratively. ValueError when n < 0."""
    # your code here


def permutations(n, k):
    """Ordered arrangements of k items from n."""
    # your code here


def combinations(n, k):
    """Unordered selections of k items from n, computed multiplicatively."""
    # your code here


def pascal_row(n):
    """Row n of Pascal's triangle, built from row n-1."""
    # your code here


def pascal_triangle(rows):
    """The first `rows` rows of Pascal's triangle."""
    # your code here


def vandermonde_holds(m, n, r):
    """Does C(m+n, r) equal the Vandermonde convolution?"""
    # your code here


def catalan(n):
    """The n-th Catalan number."""
    # your code here


for row in pascal_triangle(6):
    print(row)
print("C(52,5) =", combinations(52, 5))
print("P(5,2)  =", permutations(5, 2))
print("Catalan :", [catalan(i) for i in range(8)])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def factorial(n):
    """n! computed iteratively. ValueError when n < 0."""
    if n < 0:
        raise ValueError("factorial is undefined for negative n")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def permutations(n, k):
    """Ordered arrangements of k items from n."""
    if n < 0 or k < 0:
        raise ValueError("n and k must be non-negative")
    if k > n:
        return 0
    result = 1
    for i in range(k):
        result *= n - i
    return result


def combinations(n, k):
    """Unordered selections of k items from n, computed multiplicatively."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def pascal_row(n):
    """Row n of Pascal's triangle, built from row n-1."""
    if n < 0:
        raise ValueError("row index must be non-negative")
    row = [1]
    for _ in range(n):
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
    return row


def pascal_triangle(rows):
    """The first `rows` rows of Pascal's triangle."""
    if rows < 0:
        raise ValueError("rows must be non-negative")
    triangle = []
    row = [1]
    for _ in range(rows):
        triangle.append(row)
        row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
    return triangle


def vandermonde_holds(m, n, r):
    """Does C(m+n, r) equal the Vandermonde convolution?"""
    left = combinations(m + n, r)
    right = sum(combinations(m, k) * combinations(n, r - k) for k in range(r + 1))
    return left == right


def catalan(n):
    """The n-th Catalan number."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return combinations(2 * n, n) // (n + 1)


for row in pascal_triangle(6):
    print(row)
print("C(52,5) =", combinations(52, 5))
print("P(5,2)  =", permutations(5, 2))
print("Catalan :", [catalan(i) for i in range(8)])
'''}],
                "hints": [
                    "`factorial` is a running product over `range(2, n + 1)`; the empty range is why `factorial(0)` comes out as 1 for free.",
                    "`permutations(n, k)` is just the first k factors of n!: multiply `n, n-1, ..., n-k+1`. Never build the full factorial and divide.",
                    "In `combinations`, do the integer division *inside* the loop as shown. After i steps the running value is exactly C(n, i+1), so `//` never loses anything.",
                    "`pascal_row` grows a list: each new row is `[1] + pairwise sums of the old row + [1]`. `pascal_triangle` appends the row before growing it.",
                ],
                "tests": [
                    {"name": "factorial, and no library shortcuts", "code": r'''
for _n, _want in [(0, 1), (1, 1), (5, 120), (10, 3628800), (20, 2432902008176640000)]:
    _got = factorial(_n)
    assert _got == _want, f"factorial({_n}) gave {_got!r}, expected {_want}"
try:
    factorial(-1)
    assert False, "factorial(-1) should raise ValueError"
except ValueError:
    pass
_src = open("main.py").read()
for _banned in ["math.comb", "math.perm", "math.factorial"]:
    assert _banned not in _src, f"{_banned} defeats the exercise — write the arithmetic yourself"
'''},
                    {"name": "permutations count ordered arrangements", "code": r'''
import itertools as _it
for _n, _k, _want in [(5, 0, 1), (5, 1, 5), (5, 2, 20), (5, 5, 120), (3, 5, 0), (0, 0, 1)]:
    _got = permutations(_n, _k)
    assert _got == _want, f"permutations({_n}, {_k}) gave {_got!r}, expected {_want}"
_brute = len(list(_it.permutations(range(6), 3)))
assert permutations(6, 3) == _brute, f"permutations(6, 3) gave {permutations(6, 3)!r}, expected {_brute}"
try:
    permutations(-1, 2)
    assert False, "a negative n should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "combinations count selections", "code": r'''
import itertools as _it
for _n, _k, _want in [(0, 0, 1), (5, 0, 1), (5, 2, 10), (5, 5, 1), (5, 6, 0), (5, -1, 0),
                      (52, 5, 2598960), (40, 20, 137846528820)]:
    _got = combinations(_n, _k)
    assert _got == _want, f"combinations({_n}, {_k}) gave {_got!r}, expected {_want}"
_brute = len(list(_it.combinations(range(7), 3)))
assert combinations(7, 3) == _brute, f"combinations(7, 3) gave {combinations(7, 3)!r}, expected {_brute}"
try:
    combinations(-2, 1)
    assert False, "a negative n should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Symmetry, Pascal's rule and the row sum", "code": r'''
for _n in range(0, 15):
    for _k in range(0, _n + 1):
        assert combinations(_n, _k) == combinations(_n, _n - _k), \
            f"symmetry fails at C({_n}, {_k})"
    _total = sum(combinations(_n, _k) for _k in range(_n + 1))
    assert _total == 2 ** _n, f"row {_n} sums to {_total}, expected {2 ** _n}"
for _n in range(1, 15):
    for _k in range(1, _n):
        _lhs = combinations(_n, _k)
        _rhs = combinations(_n - 1, _k - 1) + combinations(_n - 1, _k)
        assert _lhs == _rhs, f"Pascal's rule fails at ({_n}, {_k}): {_lhs} vs {_rhs}"
'''},
                    {"name": "pascal_row builds the triangle additively", "code": r'''
assert pascal_row(0) == [1], f"row 0 is {pascal_row(0)!r}"
assert pascal_row(1) == [1, 1], f"row 1 is {pascal_row(1)!r}"
assert pascal_row(4) == [1, 4, 6, 4, 1], f"row 4 is {pascal_row(4)!r}"
assert sum(pascal_row(10)) == 1024, f"row 10 sums to {sum(pascal_row(10))}, expected 1024"
for _n in range(0, 12):
    _want = [combinations(_n, _k) for _k in range(_n + 1)]
    assert pascal_row(_n) == _want, f"row {_n} is {pascal_row(_n)!r}, expected {_want!r}"
try:
    pascal_row(-1)
    assert False, "a negative row index should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "pascal_triangle stacks the rows", "code": r'''
assert pascal_triangle(0) == [], f"got {pascal_triangle(0)!r}, expected []"
assert pascal_triangle(1) == [[1]], f"got {pascal_triangle(1)!r}"
_t = pascal_triangle(5)
assert _t == [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]], f"got {_t!r}"
assert [len(_r) for _r in pascal_triangle(8)] == [1, 2, 3, 4, 5, 6, 7, 8], "row n has n+1 entries"
'''},
                    {"name": "Vandermonde and Catalan", "code": r'''
for _m, _n, _r in [(4, 5, 3), (3, 3, 0), (6, 2, 8), (7, 4, 5), (0, 5, 2), (9, 9, 9)]:
    assert vandermonde_holds(_m, _n, _r) is True, \
        f"Vandermonde should hold for m={_m}, n={_n}, r={_r}"
_want = [1, 1, 2, 5, 14, 42, 132, 429]
_got = [catalan(_i) for _i in range(8)]
assert _got == _want, f"Catalan numbers came out as {_got!r}, expected {_want!r}"
assert catalan(10) == 16796, f"catalan(10) gave {catalan(10)!r}, expected 16796"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M8
        {
            "title": "Recurrence relations and closed forms",
            "summary": "Sequences defined by their own past, and the characteristic equation that turns them into formulas.",
            "concepts": [
                "A recurrence together with enough initial conditions determines a sequence uniquely; the recurrence alone determines nothing",
                "For a linear homogeneous recurrence with constant coefficients, substituting `a_n = r^n` collapses it to a polynomial in `r` — the characteristic equation",
                "Distinct roots give `a_n = c_1 r_1^n + ... + c_d r_d^n`, with the initial conditions fixing the constants; Fibonacci's golden-ratio formula is this in three lines",
                "A root repeated `m` times contributes `r^n, n r^n, ..., n^(m-1) r^n`, because one term cannot carry two initial conditions",
                "Where the characteristic method does not apply, iterate the recurrence, guess the closed form, and prove the guess by induction",
                "It does not apply to `T(n) = a*T(n/b) + f(n)`, where the argument is divided rather than decremented: that shape is priced by summing the cost of each level, which is the geometric series of Module 12 and the master theorem of the algorithms course",
            ],
            "quiz": {
                "title": "From a recurrence to a formula",
                "minutes": 7,
                "questions": [
                    {
                        "q": "For `a_n = 5 a_(n-1) - 6 a_(n-2)`, what is the general solution before initial conditions are applied?",
                        "opts": [
                            "`a_n = c * 5^n - c * 6^n`",
                            "`a_n = c_1 * 2^n + c_2 * 3^n`",
                            "`a_n = (c_1 + c_2 * n) * 6^n`",
                            "`a_n = c_1 * 2^n + c_2 * 3^n`, but only when `a_0` and `a_1` are positive",
                        ],
                        "a": 1,
                        "why": """
Substituting `r^n` and dividing through by `r^(n-2)` gives `r^2 = 5r - 6`, so
`r^2 - 5r + 6 = 0` and the roots are 2 and 3. Distinct roots each contribute their own
geometric term with a free constant, and any linear combination of solutions to a
homogeneous linear recurrence is again a solution, which is why the general form is
their sum. Reading the coefficients 5 and 6 off as if they were the roots skips the
characteristic equation altogether; the `n * r^n` term belongs to the repeated-root
case, which this is not. Initial conditions then pin `c_1` and `c_2`, and they may take
any values, negative included.
""",
                    },
                    {
                        "q": "Why does a repeated characteristic root require the extra term `n * r^n`?",
                        "opts": [
                            "Because `c_1 r^n + c_2 r^n` collapses to a single constant times `r^n`, which cannot generally meet two initial conditions",
                            "Because a repeated root is always zero",
                            "Because the recurrence becomes non-linear when a root repeats",
                            "Because `n * r^n` is the only sequence whose successive differences are constant",
                        ],
                        "a": 0,
                        "why": """
A degree-`d` recurrence takes `d` initial conditions, so its solution space needs `d`
independent building blocks. A double root yields only one distinct geometric sequence,
and `c_1 r^n + c_2 r^n` is simply `(c_1 + c_2) r^n` — one constant wearing two names,
unable to match two prescribed starting values. Multiplying by `n` produces a second,
genuinely independent solution, and substituting it back into the recurrence confirms
it works precisely because the root is repeated. Nothing else changes: the recurrence
stays linear, and a repeated root can be any value at all.
""",
                    },
                    {
                        "q": "`T(n) = T(n-1) + n` with `T(0) = 0`. Unrolling gives `T(n) = n + (n-1) + ... + 1`. What is the closed form, and what remains to be done?",
                        "opts": [
                            "`T(n) = n^2`, and nothing further — iteration is a proof",
                            "`T(n) = n(n+1)/2`, and nothing further — iteration is a proof",
                            "`T(n) = n(n+1)/2`, and the guess still has to be confirmed by induction",
                            "There is no closed form, because the recurrence is not homogeneous",
                        ],
                        "a": 2,
                        "why": """
Unrolling turns the recurrence into the sum of 1 through `n`, which is `n(n+1)/2`. But
iteration is a discovery technique, not a proof: the "..." in the middle is an appeal to
a pattern the reader is trusted to continue, and the induction that follows is what
turns a guess into a theorem — check `T(0) = 0`, then
`T(k+1) = T(k) + (k+1) = k(k+1)/2 + (k+1) = (k+1)(k+2)/2`. The recurrence really is
non-homogeneous, since `+ n` is an added term rather than a multiple of an earlier
value, and that is exactly why the characteristic method alone does not finish it — but
a closed form exists all the same.
""",
                    },
                    {
                        "q": "Fibonacci is `f_n = f_(n-1) + f_(n-2)` with `f_0 = 0`, `f_1 = 1`, and its closed form involves the golden ratio. Which statement is right?",
                        "opts": [
                            "The characteristic equation is `r^2 = r + 1`, whose two roots are the golden ratio and its conjugate, and the initial conditions fix the two constants",
                            "Fibonacci has no characteristic equation, because both of its coefficients are 1",
                            "The closed form is exact only for even `n`",
                            "The closed form is an approximation, since irrational numbers cannot combine to give integers",
                        ],
                        "a": 0,
                        "why": """
Substituting `r^n` gives `r^2 = r + 1`, with roots `(1 + sqrt 5)/2` and
`(1 - sqrt 5)/2` — distinct, so the general solution combines their powers, and
`f_0 = 0`, `f_1 = 1` fix the constants at `1/sqrt 5` and `-1/sqrt 5`. The formula is
exact for every `n`: the irrational parts cancel because the roots are conjugates, and
a sum of conjugate irrationals is perfectly capable of being an integer. Coefficients
of 1 are ordinary constants and cause no difficulty. Evaluating the formula in floating
point is an approximation, but that is a limitation of the arithmetic, not of the
mathematics.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M9
        {
            "title": "Number theory and modular arithmetic",
            "summary": "Divisibility, Euclid, inverses, primes, and exponentiation that stays small.",
            "concepts": [
                "Divisibility, the division algorithm, and gcd as the last non-zero remainder",
                "Euclid's algorithm terminates because the remainder strictly decreases",
                "Bezout's identity: gcd(a, b) = ax + by for some integers x, y",
                "`a` is invertible modulo `m` exactly when gcd(a, m) = 1",
                "The sieve of Eratosthenes, and why crossing out can start at p squared",
                "The fundamental theorem of arithmetic: a unique multiset of prime factors",
                "Fast modular exponentiation: O(log e) multiplications, never a huge intermediate — Module 12 defines that notation and puts the constant and the threshold on this very claim",
            ],
            "lab": {
                "title": "Euclid, inverses, sieves and fast powers",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Six routines that between them underpin most of cryptography.

**`gcd(a, b)`** — Euclid's algorithm, iteratively. Works for negatives by
taking absolute values first; `gcd(0, 0)` is `0`, `gcd(0, n)` is `abs(n)`.
Do not use `math.gcd`.

**`extended_gcd(a, b)`** — returns `(g, x, y)` with `a*x + b*y == g == gcd(a, b)`.
Both arguments must be non-negative, else `ValueError`.

**`mod_inverse(a, m)`** — the `x` in `0 .. m-1` with `a*x % m == 1`. A modulus
below 2 raises `ValueError`, and so does an `a` sharing a factor with `m`.
Negative `a` is fine: work with `a % m`.

```text
mod_inverse(3, 11)  ->  4        because 3*4 = 12 = 1 (mod 11)
mod_inverse(6, 9)   ->  ValueError
```

**`sieve(limit)`** — every prime up to and including `limit`, in order. Cross
out multiples of `p` starting at `p*p`, and stop the outer loop once `p*p`
exceeds the limit. `sieve(1)` is `[]`.

**`mod_pow(base, exponent, modulus)`** — square-and-multiply. Reduce modulo
`modulus` at every step so the numbers stay small. A negative exponent or a
modulus below 1 raises `ValueError`; note that `mod_pow(x, 0, 1)` is `0`,
because `1 % 1 == 0`. Python's three-argument built-in is off limits here.

**`prime_factors(n)`** — the prime factorisation of `n >= 2` as an ascending
list *with multiplicity*, so `prime_factors(360)` is `[2, 2, 2, 3, 3, 5]`.
An `n` below 2 raises `ValueError`.

Together these give you textbook RSA: with `p = 61`, `q = 53`, `n = 3233` and
`e = 17`, the private exponent is `mod_inverse(17, 60 * 52)`.
''',
                "files": [{"name": "main.py", "content": r'''
def gcd(a, b):
    """The greatest common divisor, by Euclid's algorithm."""
    # your code here


def extended_gcd(a, b):
    """(g, x, y) with a*x + b*y == g == gcd(a, b). Non-negative a, b only."""
    # your code here


def mod_inverse(a, m):
    """The inverse of a modulo m, in 0..m-1. ValueError when there is none."""
    # your code here


def sieve(limit):
    """Every prime up to and including limit."""
    # your code here


def mod_pow(base, exponent, modulus):
    """base ** exponent % modulus by square-and-multiply."""
    # your code here


def prime_factors(n):
    """The ascending prime factorisation of n, with multiplicity."""
    # your code here


print("gcd(240, 46)      =", gcd(240, 46))
print("extended(240, 46) =", extended_gcd(240, 46))
print("primes below 30   =", sieve(30))
print("360 factors       =", prime_factors(360))

p, q, e = 61, 53, 17
n = p * q
d = mod_inverse(e, (p - 1) * (q - 1))
cipher = mod_pow(65, e, n)
print("d, cipher, plain  =", d, cipher, mod_pow(cipher, d, n))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def gcd(a, b):
    """The greatest common divisor, by Euclid's algorithm."""
    a, b = abs(a), abs(b)
    while b:
        a, b = b, a % b
    return a


def extended_gcd(a, b):
    """(g, x, y) with a*x + b*y == g == gcd(a, b). Non-negative a, b only."""
    if a < 0 or b < 0:
        raise ValueError("extended_gcd expects non-negative arguments")
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t


def mod_inverse(a, m):
    """The inverse of a modulo m, in 0..m-1. ValueError when there is none."""
    if m < 2:
        raise ValueError("modulus must be at least 2")
    g, x, _ = extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} is not invertible modulo {m}")
    return x % m


def sieve(limit):
    """Every prime up to and including limit."""
    if limit < 2:
        return []
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    candidate = 2
    while candidate * candidate <= limit:
        if is_prime[candidate]:
            for multiple in range(candidate * candidate, limit + 1, candidate):
                is_prime[multiple] = False
        candidate += 1
    return [number for number, flag in enumerate(is_prime) if flag]


def mod_pow(base, exponent, modulus):
    """base ** exponent % modulus by square-and-multiply."""
    if exponent < 0:
        raise ValueError("exponent must be non-negative")
    if modulus < 1:
        raise ValueError("modulus must be positive")
    result = 1 % modulus
    base %= modulus
    while exponent:
        if exponent & 1:
            result = result * base % modulus
        base = base * base % modulus
        exponent >>= 1
    return result


def prime_factors(n):
    """The ascending prime factorisation of n, with multiplicity."""
    if n < 2:
        raise ValueError("n must be 2 or greater")
    factors = []
    divisor = 2
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors.append(divisor)
            n //= divisor
        divisor += 1
    if n > 1:
        factors.append(n)
    return factors


print("gcd(240, 46)      =", gcd(240, 46))
print("extended(240, 46) =", extended_gcd(240, 46))
print("primes below 30   =", sieve(30))
print("360 factors       =", prime_factors(360))

p, q, e = 61, 53, 17
n = p * q
d = mod_inverse(e, (p - 1) * (q - 1))
cipher = mod_pow(65, e, n)
print("d, cipher, plain  =", d, cipher, mod_pow(cipher, d, n))
'''}],
                "hints": [
                    "Euclid in two lines: `while b: a, b = b, a % b`, then return `a`. Take `abs` of both arguments first so negatives behave.",
                    "For the extended version carry three pairs — remainders, and the coefficients of a and of b — and apply the same `old, new = new, old - q*new` update to each.",
                    "`mod_inverse` is `extended_gcd(a % m, m)`: if the gcd is not 1 there is no inverse, otherwise the first coefficient taken `% m` is the answer.",
                    "Square-and-multiply reads the exponent bit by bit: multiply the result in when the low bit is set, then square the base and shift the exponent right.",
                ],
                "tests": [
                    {"name": "gcd, including the awkward arguments", "code": r'''
import re as _re
for _a, _b, _want in [(240, 46, 2), (46, 240, 2), (12, 18, 6), (-12, 18, 6), (12, -18, 6),
                      (17, 5, 1), (0, 7, 7), (7, 0, 7), (0, 0, 0), (13, 13, 13)]:
    _got = gcd(_a, _b)
    assert _got == _want, f"gcd({_a}, {_b}) gave {_got!r}, expected {_want}"
_src = open("main.py").read()
assert "math.gcd" not in _src, "math.gcd defeats the exercise — implement Euclid yourself"
assert not _re.search(r"(?<![\w.])pow\s*\(", _src), \
    "the built-in pow is off limits — implement square-and-multiply yourself"
'''},
                    {"name": "extended_gcd satisfies Bezout", "code": r'''
for _a, _b in [(240, 46), (46, 240), (35, 15), (17, 5), (0, 5), (5, 0), (0, 0), (99, 78)]:
    _g, _x, _y = extended_gcd(_a, _b)
    assert _g == gcd(_a, _b), f"extended_gcd({_a}, {_b}) reported g={_g}, expected {gcd(_a, _b)}"
    assert _a * _x + _b * _y == _g, \
        f"Bezout fails: {_a}*{_x} + {_b}*{_y} = {_a * _x + _b * _y}, expected {_g}"
try:
    extended_gcd(-4, 6)
    assert False, "a negative argument should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "mod_inverse inverts, or refuses", "code": r'''
for _a, _m, _want in [(3, 11, 4), (1, 5, 1), (10, 17, 12), (-3, 11, 7), (17, 3120, 2753)]:
    _got = mod_inverse(_a, _m)
    assert _got == _want, f"mod_inverse({_a}, {_m}) gave {_got!r}, expected {_want}"
for _a in range(1, 20):
    if gcd(_a, 20) == 1:
        assert _a * mod_inverse(_a, 20) % 20 == 1, f"{_a} was not inverted correctly mod 20"
for _bad in [(6, 9), (4, 8), (0, 7), (3, 1), (3, 0)]:
    try:
        mod_inverse(*_bad)
        assert False, f"mod_inverse{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "sieve finds exactly the primes", "code": r'''
assert sieve(0) == [] and sieve(1) == [], "there are no primes at or below 1"
assert sieve(2) == [2], f"sieve(2) gave {sieve(2)!r}"
_want = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
assert sieve(30) == _want, f"sieve(30) gave {sieve(30)!r}, expected {_want!r}"
assert len(sieve(100)) == 25, f"there are 25 primes below 100, got {len(sieve(100))}"
assert len(sieve(1000)) == 168, f"there are 168 primes below 1000, got {len(sieve(1000))}"
_primes = sieve(200)
for _n in range(2, 201):
    _naive = all(_n % _d for _d in range(2, int(_n ** 0.5) + 1))
    assert (_n in _primes) == _naive, f"sieve disagrees with trial division at {_n}"
'''},
                    {"name": "mod_pow is fast and correct", "code": r'''
for _b, _e, _m, _want in [(2, 10, 1000, 24), (3, 0, 7, 1), (5, 3, 1, 0), (7, 1, 13, 7),
                          (2, 12, 13, 1), (65, 17, 3233, 2790)]:
    _got = mod_pow(_b, _e, _m)
    assert _got == _want, f"mod_pow({_b}, {_e}, {_m}) gave {_got!r}, expected {_want}"
for _b in range(1, 13):
    assert mod_pow(_b, 12, 13) == 1, f"Fermat fails: {_b}^12 mod 13 should be 1"
assert mod_pow(7, 100000, 1000000007) == pow(7, 100000, 1000000007), \
    "large exponents must agree with the reference"
for _bad in [(2, -1, 5), (2, 3, 0), (2, 3, -4)]:
    try:
        mod_pow(*_bad)
        assert False, f"mod_pow{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "prime_factors reconstruct their input", "code": r'''
assert prime_factors(360) == [2, 2, 2, 3, 3, 5], f"got {prime_factors(360)!r}"
assert prime_factors(2) == [2], f"got {prime_factors(2)!r}"
assert prime_factors(97) == [97], "a prime is its own factorisation"
assert prime_factors(1024) == [2] * 10, f"got {prime_factors(1024)!r}"
_primes = set(sieve(500))
for _n in range(2, 400):
    _f = prime_factors(_n)
    _product = 1
    for _p in _f:
        _product *= _p
    assert _product == _n, f"prime_factors({_n}) = {_f!r} multiplies to {_product}"
    assert _f == sorted(_f), f"prime_factors({_n}) = {_f!r} is not ascending"
    assert all(_p in _primes for _p in _f), f"prime_factors({_n}) = {_f!r} has a composite entry"
for _bad in [1, 0, -6]:
    try:
        prime_factors(_bad)
        assert False, f"prime_factors({_bad}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The pieces compose into textbook RSA", "code": r'''
_p, _q, _e = 61, 53, 17
_n = _p * _q
_phi = (_p - 1) * (_q - 1)
assert _n == 3233 and _phi == 3120, f"n and phi came out as {_n} and {_phi}"
_d = mod_inverse(_e, _phi)
assert _d == 2753, f"the private exponent is {_d!r}, expected 2753"
assert _e * _d % _phi == 1, "e and d must be inverses modulo phi"
for _message in [0, 1, 42, 65, 3232]:
    _cipher = mod_pow(_message, _e, _n)
    _plain = mod_pow(_cipher, _d, _n)
    assert _plain == _message, f"{_message} encrypted to {_cipher} and decrypted to {_plain}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M10
        {
            "title": "Relations, graphs and closure",
            "summary": "Sets of pairs, the properties that classify them, and the algorithms that repair them.",
            "concepts": [
                "A binary relation on S is a subset of S x S — nothing more",
                "Reflexive, symmetric, antisymmetric and transitive, each as a quantified statement",
                "An equivalence relation partitions its ground set into disjoint classes",
                "The boolean adjacency matrix, and matrix entry (i, j) as the edge i to j",
                "The transitive closure is the smallest transitive relation containing R",
                "Warshall's algorithm: O(n^3) with the intermediate vertex k on the outside — three nested loops, so the innermost line runs exactly n^3 times, which Module 12 turns from a notation into a count",
                "A graph is bipartite exactly when it has no odd cycle — decided by two-colouring",
            ],
            "lab": {
                "title": "Relation properties, Warshall and bipartiteness",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
A relation is given as a ground set `elements` (a list, whose order fixes the
matrix indices) and `pairs` (an iterable of `(a, b)` tuples).

**`to_matrix(elements, pairs)`** — the boolean adjacency matrix: a list of
`len(elements)` rows of `len(elements)` booleans, with `matrix[i][j]` true when
`(elements[i], elements[j])` is in the relation. A pair mentioning something
outside the ground set is a `ValueError`. An empty ground set gives `[]`.

**`is_reflexive(elements, pairs)`** — is `(e, e)` present for every element?
Vacuously `True` on an empty ground set.

**`is_symmetric(elements, pairs)`** — does every `(a, b)` come with `(b, a)`?

**`is_transitive(elements, pairs)`** — does `(a, b)` and `(b, c)` always force
`(a, c)`?

**`is_equivalence(elements, pairs)`** — all three at once.

**`warshall(matrix)`** — the transitive closure of a boolean matrix, as a
**new** matrix. The caller's matrix must come back untouched.

```text
for k in range(n):
    for i in range(n):
        if closure[i][k]:
            for j in range(n):
                if closure[k][j]:
                    closure[i][j] = True
```

**`transitive_closure(elements, pairs)`** — the closure as a `set` of pairs,
computed through `to_matrix` and `warshall`.

```text
transitive_closure(["a", "b", "c"], {("a", "b"), ("b", "c")})
  ->  {("a", "b"), ("b", "c"), ("a", "c")}
```

**`two_colouring(adjacency)`** — the graph is a dict mapping each node to a
list of neighbours, and it is undirected, so every edge appears twice. Return a
dict from node to `0` or `1` in which no edge joins two equal colours, or
`None` when the graph is not bipartite. Start every unvisited component at
colour `0`, taking the components in sorted node order, so the answer is
deterministic. An empty graph gives `{}`.

**`is_bipartite(adjacency)`** — `True` exactly when a two-colouring exists.
''',
                "files": [{"name": "main.py", "content": r'''
def to_matrix(elements, pairs):
    """The boolean adjacency matrix of a relation."""
    # your code here


def is_reflexive(elements, pairs):
    """Is (e, e) in the relation for every element?"""
    # your code here


def is_symmetric(elements, pairs):
    """Does every pair come with its reverse?"""
    # your code here


def is_transitive(elements, pairs):
    """Do (a, b) and (b, c) always force (a, c)?"""
    # your code here


def is_equivalence(elements, pairs):
    """Reflexive, symmetric and transitive."""
    # your code here


def warshall(matrix):
    """The transitive closure of a boolean matrix, as a new matrix."""
    # your code here


def transitive_closure(elements, pairs):
    """The transitive closure of a relation, as a set of pairs."""
    # your code here


def two_colouring(adjacency):
    """A dict node -> 0/1 with no monochromatic edge, or None."""
    # your code here


def is_bipartite(adjacency):
    """Does a two-colouring exist?"""
    # your code here


people = ["a", "b", "c"]
knows = {("a", "b"), ("b", "c")}
print("reflexive? ", is_reflexive(people, knows))
print("closure    ", sorted(transitive_closure(people, knows)))

graph = {"a": ["b"], "b": ["a", "c"], "c": ["b"]}
print("colouring  ", two_colouring(graph))
print("triangle   ", two_colouring({"x": ["y", "z"], "y": ["x", "z"], "z": ["x", "y"]}))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def to_matrix(elements, pairs):
    """The boolean adjacency matrix of a relation."""
    index = {element: i for i, element in enumerate(elements)}
    size = len(elements)
    matrix = [[False] * size for _ in range(size)]
    for left, right in pairs:
        if left not in index or right not in index:
            raise ValueError(f"pair ({left!r}, {right!r}) leaves the ground set")
        matrix[index[left]][index[right]] = True
    return matrix


def is_reflexive(elements, pairs):
    """Is (e, e) in the relation for every element?"""
    known = set(pairs)
    return all((element, element) in known for element in elements)


def is_symmetric(elements, pairs):
    """Does every pair come with its reverse?"""
    known = set(pairs)
    return all((right, left) in known for left, right in known)


def is_transitive(elements, pairs):
    """Do (a, b) and (b, c) always force (a, c)?"""
    known = set(pairs)
    for left, middle in known:
        for other, right in known:
            if middle == other and (left, right) not in known:
                return False
    return True


def is_equivalence(elements, pairs):
    """Reflexive, symmetric and transitive."""
    return (is_reflexive(elements, pairs)
            and is_symmetric(elements, pairs)
            and is_transitive(elements, pairs))


def warshall(matrix):
    """The transitive closure of a boolean matrix, as a new matrix."""
    size = len(matrix)
    closure = [list(row) for row in matrix]
    for k in range(size):
        for i in range(size):
            if closure[i][k]:
                for j in range(size):
                    if closure[k][j]:
                        closure[i][j] = True
    return closure


def transitive_closure(elements, pairs):
    """The transitive closure of a relation, as a set of pairs."""
    closure = warshall(to_matrix(elements, pairs))
    return {(elements[i], elements[j])
            for i in range(len(elements))
            for j in range(len(elements))
            if closure[i][j]}


def two_colouring(adjacency):
    """A dict node -> 0/1 with no monochromatic edge, or None."""
    colours = {}
    for start in sorted(adjacency):
        if start in colours:
            continue
        colours[start] = 0
        queue = [start]
        while queue:
            node = queue.pop(0)
            for neighbour in adjacency.get(node, ()):
                if neighbour not in colours:
                    colours[neighbour] = 1 - colours[node]
                    queue.append(neighbour)
                elif colours[neighbour] == colours[node]:
                    return None
    return colours


def is_bipartite(adjacency):
    """Does a two-colouring exist?"""
    return two_colouring(adjacency) is not None


people = ["a", "b", "c"]
knows = {("a", "b"), ("b", "c")}
print("reflexive? ", is_reflexive(people, knows))
print("closure    ", sorted(transitive_closure(people, knows)))

graph = {"a": ["b"], "b": ["a", "c"], "c": ["b"]}
print("colouring  ", two_colouring(graph))
print("triangle   ", two_colouring({"x": ["y", "z"], "y": ["x", "z"], "z": ["x", "y"]}))
'''}],
                "hints": [
                    "Build a `{element: index}` dict once in `to_matrix`; then every pair is a constant-time write, and an unknown key is the error case.",
                    "The three property tests read almost like their definitions once you turn `pairs` into a `set` first — membership then costs nothing.",
                    "`[list(row) for row in matrix]` copies each row. `closure = matrix[:]` would share the rows and quietly mutate the caller's data.",
                    "Two-colouring is breadth-first search that paints each neighbour the opposite colour; a neighbour already painted the *same* colour is the odd cycle, so return None immediately.",
                ],
                "tests": [
                    {"name": "to_matrix places the pairs", "code": r'''
_m = to_matrix(["a", "b", "c"], {("a", "b"), ("b", "c")})
assert _m == [[False, True, False], [False, False, True], [False, False, False]], f"got {_m!r}"
assert to_matrix([], set()) == [], "an empty ground set gives an empty matrix"
assert to_matrix(["a"], set()) == [[False]], "no pairs means an all-false matrix"
assert to_matrix(["a"], {("a", "a")}) == [[True]], "a self-loop sits on the diagonal"
try:
    to_matrix(["a", "b"], {("a", "z")})
    assert False, "a pair outside the ground set should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Reflexivity", "code": r'''
assert is_reflexive(["a", "b"], {("a", "a"), ("b", "b")}) is True
assert is_reflexive(["a", "b"], {("a", "a")}) is False, "b has no self-loop"
assert is_reflexive([], set()) is True, "vacuously true on an empty ground set"
assert is_reflexive(["a"], {("a", "a"), ("a", "a")}) is True, "duplicates change nothing"
'''},
                    {"name": "Symmetry", "code": r'''
assert is_symmetric(["a", "b"], {("a", "b"), ("b", "a")}) is True
assert is_symmetric(["a", "b"], {("a", "b")}) is False, "the reverse pair is missing"
assert is_symmetric(["a", "b"], set()) is True, "the empty relation is symmetric"
assert is_symmetric(["a"], {("a", "a")}) is True, "a self-loop is its own reverse"
'''},
                    {"name": "Transitivity", "code": r'''
_le = {(1, 1), (1, 2), (1, 3), (2, 2), (2, 3), (3, 3)}
assert is_transitive([1, 2, 3], _le) is True, "less-or-equal is transitive"
assert is_transitive(["a", "b", "c"], {("a", "b"), ("b", "c")}) is False, "(a, c) is missing"
assert is_transitive(["a", "b"], {("a", "b"), ("b", "a")}) is False, \
    "(a, b) and (b, a) force (a, a)"
assert is_transitive(["a", "b"], set()) is True, "the empty relation is transitive"
assert is_transitive(["a", "b"], {("a", "b")}) is True, "nothing chains, so nothing is required"
'''},
                    {"name": "Equivalence relations", "code": r'''
_identity = {("a", "a"), ("b", "b"), ("c", "c")}
assert is_equivalence(["a", "b", "c"], _identity) is True, "equality is an equivalence"
_classes = _identity | {("a", "b"), ("b", "a")}
assert is_equivalence(["a", "b", "c"], _classes) is True, "two classes: {a, b} and {c}"
assert is_equivalence([1, 2, 3], _le) is False, "less-or-equal is not symmetric"
assert is_equivalence(["a", "b"], {("a", "b"), ("b", "a")}) is False, "not reflexive"
assert is_equivalence([], set()) is True, "vacuously an equivalence"
'''},
                    {"name": "Warshall closes the matrix without mutating it", "code": r'''
_m = [[False, True, False], [False, False, True], [False, False, False]]
_c = warshall(_m)
assert _c == [[False, True, True], [False, False, True], [False, False, False]], f"got {_c!r}"
assert _m == [[False, True, False], [False, False, True], [False, False, False]], \
    "warshall must not modify the matrix it was given"
assert warshall([]) == [], "an empty matrix closes to an empty matrix"
_cycle = [[False, True], [True, False]]
assert warshall(_cycle) == [[True, True], [True, True]], "a 2-cycle closes to everything"
'''},
                    {"name": "transitive_closure returns pairs", "code": r'''
_got = transitive_closure(["a", "b", "c"], {("a", "b"), ("b", "c")})
_want = {("a", "b"), ("b", "c"), ("a", "c")}
assert _got == _want, f"got {sorted(_got)!r}, expected {sorted(_want)!r}"
assert transitive_closure(["a", "b"], set()) == set(), "the empty relation closes to itself"
_ring = transitive_closure(["a", "b", "c"], {("a", "b"), ("b", "c"), ("c", "a")})
assert len(_ring) == 9, f"a 3-cycle closes to all 9 pairs, got {len(_ring)}"
_closed = transitive_closure(["a", "b", "c"], {("a", "b"), ("b", "c")})
assert is_transitive(["a", "b", "c"], _closed) is True, "the closure must itself be transitive"
'''},
                    {"name": "Two-colouring decides bipartiteness", "code": r'''
_path = {"a": ["b"], "b": ["a", "c"], "c": ["b"]}
assert two_colouring(_path) == {"a": 0, "b": 1, "c": 0}, f"got {two_colouring(_path)!r}"
_square = {"a": ["b", "d"], "b": ["a", "c"], "c": ["b", "d"], "d": ["a", "c"]}
_colours = two_colouring(_square)
assert _colours is not None, "an even cycle is bipartite"
for _node, _neighbours in _square.items():
    for _other in _neighbours:
        assert _colours[_node] != _colours[_other], f"edge {_node}-{_other} is monochromatic"
_triangle = {"x": ["y", "z"], "y": ["x", "z"], "z": ["x", "y"]}
assert two_colouring(_triangle) is None, "an odd cycle is not bipartite"
assert is_bipartite(_triangle) is False and is_bipartite(_square) is True
assert two_colouring({}) == {}, "the empty graph is trivially bipartite"
assert two_colouring({"a": [], "b": []}) == {"a": 0, "b": 0}, "isolated nodes all start at 0"
assert two_colouring({"a": ["a"]}) is None, "a self-loop is an odd cycle"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M11
        {
            "title": "Trees, connectivity and colouring",
            "summary": "Degrees, walks, the several equivalent definitions of a tree, and how few colours a graph really needs.",
            "concepts": [
                "The handshake lemma: degrees sum to twice the edge count, so odd-degree vertices come in pairs — and a connected graph has an Euler circuit exactly when every degree is even",
                "'A walk exists from u to v' is an equivalence relation on the vertices, and its classes are the connected components",
                "A tree is any of: connected and acyclic; connected with `n - 1` edges; acyclic with `n - 1` edges; a unique path between every pair — the four describe the same graphs",
                "Every connected graph contains a spanning tree, and there are `n^(n-2)` labelled trees on `n` vertices",
                "A proper colouring gives adjacent vertices different colours; the chromatic number is the fewest that suffice, it is 2 for a bipartite graph with an edge, and greedy colouring never needs more than max-degree + 1",
            ],
            "quiz": {
                "title": "Degrees, trees and chromatic numbers",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A graph has 7 vertices, exactly 5 of which have odd degree. What follows?",
                        "opts": [
                            "Nothing; any number of odd-degree vertices is possible",
                            "The graph must be disconnected",
                            "No such graph exists — the degree sum would be odd, but it must be twice the edge count",
                            "The graph has at least 5 edges",
                        ],
                        "a": 2,
                        "why": """
Every edge adds 1 to the degree of each of its two endpoints, so the degrees sum to
exactly twice the number of edges, which is even without exception. An odd number of
odd degrees would make that sum odd, so odd-degree vertices must come in pairs and five
of them is impossible regardless of what the other two vertices do. This is the
handshake lemma, and it is the smallest example of a parity argument ruling out a whole
class of configurations before any construction is attempted. It is also what makes
Euler's bridge condition work, since a closed traversal enters and leaves each vertex
equally often.
""",
                    },
                    {
                        "q": "A graph has 10 vertices and 9 edges. Is it a tree?",
                        "opts": [
                            "Yes — `n - 1` edges is the definition of a tree",
                            "Only if every vertex has degree at most 2",
                            "No — a tree on 10 vertices has 10 edges",
                            "Only if it is also connected, or equivalently only if it is acyclic; 9 edges alone permits a triangle alongside a separate 7-vertex tree",
                        ],
                        "a": 3,
                        "why": """
The count `n - 1` is necessary but not sufficient on its own. Add either connectedness
or acyclicity and you have a tree, since each of those pairs is one of the equivalent
characterisations, but with neither the 9 edges can be spent on a triangle plus a
separate tree on the remaining 7 vertices — disconnected, and carrying a cycle. That is
the useful shape of the theorem: any two of *connected*, *acyclic* and *`n - 1` edges*
force the third. Degree at most 2 describes a path, which is a tree but far from the
only one, since a star on 10 vertices has a vertex of degree 9.
""",
                    },
                    {
                        "q": "The largest degree in a graph is 4. What does greedy colouring guarantee?",
                        "opts": [
                            "At most 5 colours suffice, and the true chromatic number may be far smaller",
                            "The chromatic number is exactly 5",
                            "The chromatic number is exactly 4",
                            "At least 5 colours are needed",
                        ],
                        "a": 0,
                        "why": """
Colour the vertices one at a time, each time taking the lowest colour no neighbour has
used. A vertex has at most 4 neighbours, so out of 5 colours one is always free: the
bound is max-degree + 1, and it is an upper bound only. Plenty of graphs containing a
degree-4 vertex need just 2 colours — a star, for instance, is bipartite. The bound is
tight for complete graphs and odd cycles and loose almost everywhere else, and greedy
colouring is itself sensitive to the order the vertices are visited in, so it can spend
more colours than the minimum even where a better colouring exists.
""",
                    },
                    {
                        "q": "Which of these graphs has chromatic number 3?",
                        "opts": [
                            "A path on 5 vertices",
                            "A cycle on 5 vertices",
                            "A cycle on 6 vertices",
                            "A tree on 100 vertices",
                        ],
                        "a": 1,
                        "why": """
An odd cycle cannot be 2-coloured: walking round it the colours must alternate, and
after an odd number of steps you arrive back at the start needing it to differ from
itself. Three colours are enough, so its chromatic number is exactly 3. An even cycle
alternates cleanly and needs 2, a path needs 2, and every tree with at least one edge
needs exactly 2 — colour by depth parity, which works because a tree closes no cycles.
This is the same fact the two-colouring of Module 10 decided: a graph is bipartite, and
so 2-colourable, exactly when it contains no odd cycle.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M12
        # Appended rather than inserted after M8, where the subject would sit more
        # naturally: a lesson id is `MA101-M<n>-<KIND>` and it is the record of what
        # someone has finished, so renumbering M9 through M11 would orphan their
        # progress. Appending costs nothing pedagogically here — this module needs
        # induction (M6), the sums of M7 and the recurrences of M8, and all three are
        # already behind it.
        {
            "title": "Growth of functions: sums, and what an O actually claims",
            "summary": "The two sums every cost argument leans on, and the definition behind a notation this course has already used twice without stating.",
            "concepts": [
                "A closed form for a sum is proved, not spotted: `1 + r + ... + r^n = (1 - r^(n+1))/(1 - r)` for every `r` other than 1, by subtract-and-telescope or by induction from Module 6",
                "Doubling makes a geometric sum: `1 + 2 + 4 + ... + 2^k = 2^(k+1) - 1`, under twice its own last term — which is why a growable array's copying is cheap",
                "The harmonic sum `H_n = 1 + 1/2 + ... + 1/n` has no such closed form, but blocking it by powers of two pins `H_(2^k)` between `1 + k/2` and `1 + k`",
                "`f = O(g)` means there are constants `c > 0` and `n0` with `f(n) <= c*g(n)` for every `n >= n0` — a claim about all large `n`, with the small ones deliberately exempt",
                "The pair `(c, n0)` is never unique, and the two trade against each other: a larger `c` buys a smaller `n0`",
                "`Omega` reverses the inequality and `Theta` asks for both at once — and only `Theta` pins a growth rate down",
                "`O` is an upper bound, not a description: `n = O(n^2)` is true and uninformative, so an `O` never rules a smaller bound out",
                "`O` says nothing about which input: worst, best and average case are three different functions, each with its own `O`, `Omega` and `Theta`",
                "The base of a logarithm is a constant factor and drops out; the base of an exponent is not and does not — `2^(n+1)` is `O(2^n)`, `2^(2n)` is not",
            ],
            "read": {
                "title": "Two sums, and the definition behind the notation",
                "minutes": 14,
                "body": r"""
This course has already written down two costs without defining either of them.
Module 9 said fast modular exponentiation takes $O(\log e)$ multiplications. Module 10
said Warshall's algorithm is $O(n^3)$. Both claims are true and neither was earned:
nothing so far has said what that notation asserts, and nothing has added up the series
that most such claims reduce to. This module pays both debts. It is worth paying,
because every course that lists this one as a prerequisite is written in that notation
from its first page, and a notation you have only ever seen used is a notation you can
misread without noticing.

## A count worth doing exactly

Start with something concrete. A growable array keeps a fixed backing store and a
length. When the store fills, it allocates one of twice the capacity, copies everything
across, and carries on. Begin at capacity 1 and append until the store has doubled five
times. How many individual slot copies has that cost?

The resizes copy 1, then 2, then 4, 8 and 16 elements — the store's contents at the
moment it overflowed. The total is

$$1 + 2 + 4 + 8 + 16 = 31$$

and 31 is $2^5 - 1$. That is not a coincidence about the number five. Write the sum as
$S = 1 + r + r^2 + \cdots + r^n$ and multiply it by $r$:

$$rS = r + r^2 + \cdots + r^n + r^{n+1}$$

Subtract. Every term in the middle appears in both lines and cancels, and what survives
is the head of one and the tail of the other:

$$S - rS = 1 - r^{n+1} \qquad\Longrightarrow\qquad S = \frac{1 - r^{n+1}}{1 - r}$$

valid whenever $r \neq 1$, which is exactly the case the division would forbid. At
$r = 2$ this reads $2^{n+1} - 1$, so five doublings cost 31 copies and twenty cost
$2^{21} - 1 = 2\,097\,151$. The shape that matters is not the formula but its
consequence: the total is *less than twice the last term*. All the copying a doubling
array has ever done is cheaper than doing the most recent copy twice. That single
sentence is the whole of the amortised argument the data structures course spends two
units on, and it is a fact about geometric series rather than about arrays.

When $r < 1$ the same formula runs the other way. As $n$ grows, $r^{n+1}$ goes to zero
and the sum settles at $1/(1 - r)$: halving forever totals 2, thirding forever totals
1.5. A ratio at least 1 has no such limit, which is the entire difference between a
loop that costs a constant per item and one that does not.

## The sum that has no closed form

Not every sum closes. The harmonic sum

$$H_n = 1 + \tfrac{1}{2} + \tfrac{1}{3} + \cdots + \tfrac{1}{n}$$

has no expression in elementary functions, and looking for one is the mistake to avoid
rather than the exercise. It can still be pinned down, by a trick worth keeping: group
the terms into blocks whose lengths are powers of two.

$$1 \;+\; \underbrace{\tfrac12}_{\text{1 term}} \;+\; \underbrace{\tfrac13 + \tfrac14}_{\text{2 terms}} \;+\; \underbrace{\tfrac15 + \cdots + \tfrac18}_{\text{4 terms}} \;+\; \cdots$$

Every term in a block is at most the block's first and greater than its last. The block
of 4 terms starting at $1/5$ therefore sums to at most $4 \times \tfrac14 = 1$ and more
than $4 \times \tfrac18 = \tfrac12$. Each block contributes between $\tfrac12$ and $1$,
and $H_{2^k}$ has $k$ of them after the leading 1:

$$1 + \tfrac{k}{2} \;\le\; H_{2^k} \;\le\; 1 + k$$

Check it at $k = 3$. $H_8 = 1 + 0.5 + 0.3333 + 0.25 + 0.2 + 0.1667 + 0.1429 + 0.125 =
2.7179$, and the bounds are $2.5$ and $4$. Both hold, neither is tight, and both are
enough to say the thing that matters: $H_n$ grows like a logarithm, so it grows without
limit and does so unbelievably slowly. Summing a million terms gets you to about 14.4.

## Now the notation

Here is the definition, and it is the whole of it.

> $f = O(g)$ when there exist a constant $c > 0$ and a threshold $n_0$ such that
> $f(n) \le c\,g(n)$ for every $n \ge n_0$.

Two things in that sentence do all the work, and both are usually skipped. There is a
constant you are allowed to choose, and there is a threshold below which the claim says
nothing whatever.

Work one all the way through. Is $f(n) = 3n^2 + 20n + 500$ in $O(n^2)$? The claim is
that some $c$ makes $3n^2 + 20n + 500 \le c\,n^2$ hold from some point on. Try $c = 4$.
Then the requirement is $n^2 - 20n - 500 \ge 0$, whose positive root is
$10 + \sqrt{600} = 34.49$, so the inequality holds from $n = 35$ upward. It genuinely
fails below: at $n = 34$ the left side is $4648$ against $4\times 1156 = 4624$, and at
$n = 35$ it is $4875$ against $4900$. So $c = 4$, $n_0 = 35$ is a witness, and the claim
is established.

It is not the only witness. Take $c = 523$ instead. Since $n^2 \ge n \ge 1$ for every
$n \ge 1$, we get $3n^2 + 20n + 500 \le 3n^2 + 20n^2 + 500n^2 = 523n^2$ immediately, so
$c = 523$, $n_0 = 1$ works too. The pair is never unique and the two halves trade
against each other: pay a bigger constant and the threshold comes down. Anyone who
insists on *the* constant has misread the definition.

Reverse the inequality and you get the lower bound: $f = \Omega(g)$ when
$f(n) \ge c\,g(n)$ eventually. Ask for both and you get $f = \Theta(g)$, the only one of
the three that says what the growth rate *is* rather than what it is not.

## Four things this notation does not say

**It does not say "worst case".** These are functions being compared, and which
function you chose is a separate decision. Insertion sort's best case is $\Theta(n)$ and
its worst is $\Theta(n^2)$; both statements are about insertion sort, and $O$ appears in
neither role by itself. Writing "the algorithm is $O(n^2)$" without saying which of its
cases you measured is an unfinished sentence, and it is the most common one in the
subject.

**It does not say "tight".** $n = O(n^2)$ is true — take $c = 1$, $n_0 = 1$. So is
$n = O(2^n)$. An $O$ bound rules nothing smaller out, which is why a claim of $O(n^2)$
is compatible with the true cost being linear. If you mean the growth rate, $\Theta$ is
the symbol that means it.

**The constant hidden inside is not always constant.** $2^{n+1} = 2 \cdot 2^n$, so
$2^{n+1} = O(2^n)$ with $c = 2$. But $2^{2n} = (2^n)^2$, and if $2^{2n} \le c\,2^n$ held
for all large $n$ then $2^n \le c$ would too, which no fixed $c$ survives. So
$2^{2n} \neq O(2^n)$. The same distinction settles logarithms in the other direction:
$\log_a n = \log_b n / \log_b a$, a fixed multiple, so the base of a logarithm is
absorbed by $c$ and nobody writes it. The base of an exponent is not absorbed by
anything.

**It does not say two things cost the same.** $\Theta$ places two functions in one
class; it does not equate them. Scanning an array and walking a linked list are both
$\Theta(n)$, and the array is several times faster on real hardware because its elements
sit next to each other. That is not the notation failing. It is the notation doing what
it was defined to do, which is to answer a question about scaling and not a question
about seconds.

## Where the whole idea stops being useful

Asymptotics is a statement about large $n$, and "large" is set by $n_0$, which the
notation hides. Compare an algorithm costing $100n$ against one costing $n\log_2 n$.
Divide both by $n$: the comparison is $100$ against $\log_2 n$, so the $n\log_2 n$
algorithm is the cheaper of the two until $\log_2 n$ passes 100 — that is,
until $n$ passes $2^{100} \approx 1.27 \times 10^{30}$. Asymptotically the linear one
wins. On every input that will ever exist, it loses. The mathematics is correct and the
recommendation drawn from it is wrong, and the only defence is to ask where the
threshold sits before quoting the bound.

## The two debts, paid

Warshall's algorithm runs three nested loops, each over all $n$ vertices, with a
constant-time body inside. The innermost line executes exactly $n^3$ times — not at
most, exactly — so the count is $\Theta(n^3)$ with $c = 1$ and $n_0 = 1$, and at
$n = 100$ that is a million updates.

Fast modular exponentiation squares once per bit of the exponent and multiplies once
more for each bit that is set. An exponent $e \ge 2$ has $\lfloor \log_2 e\rfloor + 1$
bits, so the count is at most $2(\lfloor \log_2 e\rfloor + 1)$, and since
$\lfloor \log_2 e \rfloor + 1 \le 2\log_2 e$ for $e \ge 2$, the bound is $4\log_2 e$:
witnesses $c = 4$, $n_0 = 2$. For $e = 1000$ that is at most 20 multiplications where
the naive loop does 999. The notation was never doing the work in those two sentences.
The count was, and now the count is written down.
""",
            },
            "derive": {
                "title": "The geometric sum, and the bound it hands to a doubling array",
                "minutes": 12,
                "brief": r"""
The one sum that most cost arguments reduce to, derived rather than quoted, and then
spent on the question it exists to answer: how much copying a store that doubles has
done by the time it holds $n$ things.

Write $S = 1 + r + r^{2} + \cdots + r^{n}$ throughout.
""",
                "vars": ["S", "r", "n", "k"],
                "steps": [
                    {
                        "prompt": r"Multiply $S$ by $r$ and subtract the result from $S$. Every term of the middle appears in both lines and cancels. What is left, in terms of $r$ and $n$?",
                        "answer": r"1 - r^{n+1}",
                        "placeholder": "1 - ...",
                        "hint": r"$S$ starts at $1$ and stops at $r^{n}$; $rS$ starts at $r$ and stops at $r^{n+1}$. Only the two ends survive.",
                        "deconstruct": [
                            r"Which term of $S$ has no partner in $rS$?",
                            r"Which term of $rS$ has no partner in $S$?",
                            "The subtraction is S minus rS, so the second of those arrives negated.",
                        ],
                    },
                    {
                        "prompt": r"That left side is $S(1 - r)$. Divide, and write $S$ in closed form. State it for $r \neq 1$, which is the case the division itself forbids.",
                        "answer": r"\frac{1 - r^{n+1}}{1 - r}",
                        "placeholder": r"\frac{?}{?}",
                        "hint": r"Nothing new is needed — divide the previous line by $1 - r$.",
                        "deconstruct": [
                            r"$S - rS$ factors as $S(1 - r)$.",
                            r"At $r = 1$ the formula divides by zero, and the sum is $n + 1$ instead.",
                        ],
                    },
                    {
                        "prompt": r"A store that doubles copies $1, 2, 4, \ldots, 2^{k}$ elements across its resizes. Put $r = 2$ and $n = k$ into the closed form, and simplify to a single power minus a constant.",
                        "answer": r"2^{k+1} - 1",
                        "placeholder": r"2^{?} - ?",
                        "hint": r"$1 - 2 = -1$, so dividing by the denominator negates the numerator and nothing else happens.",
                        "deconstruct": [
                            r"Substituting gives $(1 - 2^{k+1})/(1 - 2)$.",
                            r"The denominator is $-1$.",
                        ],
                    },
                    {
                        "prompt": r"Compare that total against the single largest copy in it, which is $2^{k}$. Write the total as a multiple of $2^{k}$, ignoring the $-1$ — that is, give the number the total stays strictly below.",
                        "answer": r"2 \cdot 2^{k}",
                        "placeholder": r"? \cdot 2^{k}",
                        "hint": r"$2^{k+1}$ is $2^{k}$ doubled.",
                        "deconstruct": [
                            r"$2^{k+1} - 1 < 2^{k+1}$.",
                            r"Rewrite $2^{k+1}$ with $2^{k}$ as a factor.",
                        ],
                    },
                    {
                        "prompt": r"Now the other regime. Hold $r$ below 1 and let $n$ grow without bound, so $r^{n+1}$ goes to zero. What does the closed form settle to?",
                        "answer": r"\frac{1}{1 - r}",
                        "placeholder": r"\frac{1}{?}",
                        "hint": r"Only the numerator changes: $1 - r^{n+1}$ tends to $1 - 0$.",
                        "deconstruct": [
                            r"$r^{n+1} \to 0$ precisely when $|r| < 1$.",
                            "The denominator has no n in it, so it is untouched.",
                        ],
                    },
                    {
                        "prompt": r"Halving forever is $r = \tfrac{1}{2}$. Evaluate the limit there, and read off how much a store that shrinks by half at every step costs in total relative to its first step.",
                        "answer": r"2",
                        "placeholder": "a single number",
                        "hint": r"$1 - \tfrac12 = \tfrac12$, and $1$ divided by $\tfrac12$ is not $\tfrac12$.",
                        "deconstruct": [
                            r"Substitute $r = 1/2$ into $1/(1-r)$.",
                            "Dividing by a half doubles.",
                        ],
                    },
                ],
                "closing": r"""
Both regimes came out of one formula. A ratio below 1 gives a total that is a fixed
multiple of its first term no matter how long the process runs, and a ratio of 2 gives a
total under twice its *last* term. That second reading is the one the rest of the degree
uses: all the copying a doubling array has ever done costs less than doing the most
recent copy a second time, so the copying spread over $n$ appends is a constant each.
Nothing there is a fact about arrays. It is this sum, and you have now proved it.

Note what is *not* here. This is a sum over levels, and a divide-and-conquer recurrence
such as $T(n) = a\,T(n/b) + n^{d}$ becomes exactly such a sum once you price one level
and add them up — the ratio between consecutive levels is $a/b^{d}$, and the three cases
of the master theorem are the three things the geometric series above can do. Module 8's
characteristic equation cannot touch that recurrence, because $T(n/b)$ is not a step
back by a fixed number of terms. The algorithms course does that sum; this is the sum it
does it with.
""",
            },
            "numeric": {
                "title": "Where the threshold actually sits",
                "minutes": 7,
                "brief": r"""
The definition of $O$ hands you two things to choose: a constant $c$, and a threshold
$n_0$ past which the bound must hold. Fixing one fixes the other, and the arithmetic is
worth doing once by hand rather than waving at.
""",
                "prompt": r"""
Take $f(n) = 3n^2 + 20n + 500$ and $g(n) = n^2$, and fix $c = 4$. What is the smallest
integer $n_0$ for which $f(n) \le 4g(n)$ holds at every $n \ge n_0$?
""",
                "figure": r"""
```text
    n  |  f(n) = 3n^2 + 20n + 500  |  4n^2   |  f(n) <= 4n^2 ?
  -----+---------------------------+---------+-----------------
    10 |                     1 000 |     400 |       no
    20 |                     2 100 |   1 600 |       no
    30 |                     3 800 |   3 600 |       no
    34 |                     4 648 |   4 624 |       no
    35 |                     4 875 |   4 900 |       ?
    40 |                     6 100 |   6 400 |       yes
```
""",
                "given": [
                    {"label": "$f(n)$", "value": "$3n^2 + 20n + 500$"},
                    {"label": "$g(n)$", "value": "$n^2$"},
                    {"label": "$c$", "value": "4"},
                ],
                "answer": 35,
                "tol": 0,
                "unit": "",
                "hint": r"""
$3n^2 + 20n + 500 \le 4n^2$ rearranges to $n^2 - 20n - 500 \ge 0$. Solve the quadratic
and take the positive root; the smallest integer at or above it is the threshold,
because an upward parabola stays non-negative once it has passed its larger root.
""",
                "wrong": r"""
If you answered 34, you found where the table's last *failure* is rather than the first
success — the threshold is the first $n$ at which the bound holds, not the last at which
it breaks. If you answered 30 or 40 you read a row of the table rather than solving for
the crossing; the table skips from 30 to 34 and from 35 to 40 on purpose.
""",
                "why": r"""
The requirement $3n^2 + 20n + 500 \le 4n^2$ is $n^2 - 20n - 500 \ge 0$, whose roots are
$10 \pm \sqrt{600}$; the positive one is $34.4949$. The parabola opens upward, so the
inequality holds from the first integer past that root and never fails again — which is
what makes a single threshold meaningful rather than a list of intervals. At $n = 34$
the left side is $3(1156) + 680 + 500 = 4648$ against $4624$, and it fails. At $n = 35$
it is $3(1225) + 700 + 500 = 4875$ against $4900$, and it holds. So $n_0 = 35$.

The number is not a property of $f$ and $g$ alone: it belongs to the pair $(c, n_0)$
together. Choose $c = 523$ instead and $n_0 = 1$ works, since $n^2 \ge n \ge 1$ makes
$3n^2 + 20n + 500 \le 3n^2 + 20n^2 + 500n^2$ for every $n \ge 1$. Both pairs prove the
same statement, $f = O(n^2)$. What the definition demands is that *some* pair exists,
which is why nobody quotes either number afterwards — and why a bound whose threshold
sits past every input you will ever see is still, correctly, a true statement about
nothing you care about.
""",
            },
            "blanks": {
                "title": "Finding the constant and the threshold by machine",
                "minutes": 9,
                "lang": "python",
                "caption": "smallest_n0.py",
                "brief": r"""
The definition of $O$ is a search for two numbers. Written as code it stops being an
incantation: fix the constant, sweep $n$, and remember the last place the bound broke.
""",
                "listing": r'''
def smallest_n0(f, g, c, limit=10 ** 6):
    """Smallest n0 such that f(n) <= c*g(n) for every n from n0 up to limit.

    Sweep upward and move the threshold past every failure. Whatever is left when
    the sweep ends is the first point after which nothing failed."""
    n0 = 1
    for n in range(1, limit + 1):
        if f(n) > c * g(n):
            n0 = ___
    return n0


f = lambda n: 3 * n * n + 20 * n + 500
g = lambda n: ___

print(smallest_n0(f, g, 4))            # -> ___
print(smallest_n0(f, g, 523))          # -> ___
print(smallest_n0(f, g, ___))          # -> no such n0 exists below the limit
''',
                "blanks": [
                    {
                        "prompt": "The bound has just failed at `n`. Where must the threshold move to?",
                        "opts": ["n + 1", "n", "n - 1", "n0 + 1"],
                        "a": 0,
                        "why": r"""
A threshold of `n` would include the very point that just failed, so it has to sit one
past it. Setting it to `n + 1` and letting later failures push it further is what makes
the sweep correct without any backtracking: when the loop ends, every `n` at or above
the surviving value passed, because any that did not would have moved it again.
""",
                        "whys": [
                            "Correct. The failure at `n` disqualifies `n` itself, and any later failure pushes the threshold further along again.",
                            "This keeps the failing point inside the claimed range, so the returned threshold would assert a bound that demonstrably breaks at its own first value.",
                            "This moves the threshold backwards, to a point already swept, and would leave both the failure at `n` and everything before it inside the claim.",
                            "The running value is irrelevant here — the new threshold depends on where the failure happened, not on where the threshold was, and incrementing it once per failure would undercount a run of them.",
                        ],
                    },
                    {
                        "prompt": "`g` is the function `f` is being compared against.",
                        "opts": ["n * n", "n", "n * n * n", "2 ** n"],
                        "a": 0,
                        "why": r"""
The claim under test is $f = O(n^2)$, so `g` is $n^2$. The others are all true bounds
too — $f$ is $O(n^3)$ and $O(2^n)$ as well — which is exactly the point that $O$ is an
upper bound and not a description. Only $n^2$ is the one that is also a lower bound, and
so the one that makes the statement $\Theta$.
""",
                        "whys": [
                            "Correct, and it is the only choice here for which the reverse inequality also holds, so it is the $\\Theta$ as well as the $O$.",
                            "$f$ grows quadratically, so no constant multiple of $n$ can contain it: the ratio $f(n)/n$ is about $3n$ and runs away.",
                            "A true bound — $f$ really is $O(n^3)$ — but a loose one, and taking it would make the threshold 1 for every constant and teach nothing about where a bound bites.",
                            "Also true and far looser still; an exponential swallows any polynomial from a small $n$ onward, so the search would answer 1 and the exercise would collapse.",
                        ],
                    },
                    {
                        "prompt": "The threshold reported for `c = 4`.",
                        "opts": ["35", "34", "36", "10"],
                        "a": 0,
                        "why": r"""
$3n^2 + 20n + 500 \le 4n^2$ is $n^2 - 20n - 500 \ge 0$, whose positive root is
$10 + \sqrt{600} = 34.4949$. The last failure is at $n = 34$ ($4648 > 4624$), so the
sweep sets the threshold to 35 and nothing after that moves it again.
""",
                        "whys": [
                            "Correct: 34 is the last failure, so the threshold lands one past it, and $4875 \\le 4900$ holds from there on.",
                            "This is where the bound last *broke*, not where it started holding — at $n = 34$ the left side is $4648$ against $4624$.",
                            "One too far. The bound already holds at 35, so 36 would be a valid threshold but not the smallest one, and the function returns the smallest.",
                            "Far too early: at $n = 10$ the left side is $1000$ against $400$, and the bound is not close to holding.",
                        ],
                    },
                    {
                        "prompt": "The threshold reported for `c = 523`.",
                        "opts": ["1", "0", "35", "523"],
                        "a": 0,
                        "why": r"""
Since $n^2 \ge n \ge 1$ for every $n \ge 1$, the inequality
$3n^2 + 20n + 500 \le 3n^2 + 20n^2 + 500n^2 = 523n^2$ holds from the very first term,
so the sweep never fires and the threshold keeps its initial value. A bigger constant
buys a smaller threshold; the two are traded against each other and neither is a
property of $f$ on its own.
""",
                        "whys": [
                            "Correct — the bound never fails, so the initial value survives the whole sweep.",
                            "The sweep starts at 1 and the initial value is 1, so 0 is never reachable; it would also be a claim about $n = 0$, which the range never tests.",
                            "That is the threshold for $c = 4$. Raising the constant to 523 makes the bound hold everywhere, so the threshold falls rather than staying put.",
                            "The constant and the threshold are different quantities that happen to be adjacent in the call; a larger constant makes the threshold smaller, not equal to itself.",
                        ],
                    },
                    {
                        "prompt": "A constant for which the sweep finds no threshold at all below the limit.",
                        "opts": ["2", "4", "523", "1000"],
                        "a": 0,
                        "why": r"""
The leading coefficient of $f$ is 3, so $f(n)/n^2 \to 3$ from above and no constant at
or below 3 can ever contain it: $3n^2 + 20n + 500 \le 2n^2$ would need
$n^2 + 20n + 500 \le 0$, and that left side is positive for every $n$. The sweep
therefore fails at the last value it tests and reports a threshold of `limit + 1` — a
number that is not a witness to anything, and the case worth knowing about, since a
search of this shape can only ever say "not below here".
""",
                        "whys": [
                            "Correct: 2 is below the leading coefficient 3, so the bound fails at every $n$ and the threshold is pushed to the end of the sweep.",
                            "4 exceeds the leading coefficient, so the bound holds from 35 onward — a threshold is found.",
                            "523 is generous enough to hold from $n = 1$, which is the opposite of failing.",
                            "Larger still, and larger constants only make the bound easier to satisfy; the threshold would again be 1.",
                        ],
                    },
                ],
            },
            "quiz": {
                "title": "What the definition does and does not promise",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Someone shows that `f(n) <= 4n^2` for every `n >= 35`, and someone else shows `f(n) <= 523n^2` for every `n >= 1`. Which of them has established `f = O(n^2)`?",
                        "opts": [
                            "Neither, until the two witnesses are reconciled into one bound",
                            "Both, since the definition asks only that some such pair exist",
                            "Only the one with `c = 523`, whose threshold is as low as it goes",
                            "Only the one with `c = 4`, whose constant is the smaller of the two",
                        ],
                        "a": 1,
                        "why": r"""
The definition is existential: it asks whether *some* $(c, n_0)$ works. Two different
witnesses to the same statement are no more in conflict than two proofs of one theorem,
and the pair is never unique — a larger constant always buys a smaller threshold, since
raising $c$ can only make the inequality easier. There is nothing to reconcile and no
reason to prefer either witness, which is why neither number is ever quoted once the
claim is made. What the numbers are good for is the separate and much more practical
question of *where* the bound starts to bite.
""",
                        "whys": [
                            "There is nothing to reconcile: the two are witnesses to one existential claim, and a statement proved twice is not thereby in doubt.",
                            "Correct. Both exhibit a constant and a threshold that work, which is all the definition asks for.",
                            "A threshold of 1 is convenient but carries no special standing; the definition never asks for the smallest threshold, only for one that exists.",
                            "Smallness of the constant is not part of the definition either, and in any case the constants here are traded against the thresholds rather than ranked.",
                        ],
                    },
                    {
                        "q": "Is the statement `n = O(n^2)` true?",
                        "opts": [
                            "No — the two grow at different rates, so neither one bounds the other",
                            "Only for `n <= 1`, which is where the two functions cross over",
                            "Yes, with `c = 1` and `n0 = 1`; the claim is weak rather than wrong",
                            "No — `O` demands that the two functions grow at the very same rate",
                        ],
                        "a": 2,
                        "why": r"""
$n \le n^2$ for every $n \ge 1$, so $c = 1$ and $n_0 = 1$ is a witness and the statement
holds. It is also almost useless, and that is the lesson: $O$ is an upper bound and
nothing more, so quoting one never rules a smaller bound out. If you want to say that a
cost really does grow like $n^2$, the symbol that says it is $\Theta$, which demands the
matching lower bound as well. Reading $O$ as though it meant $\Theta$ is the single most
common misuse of the notation, and it is what makes "this algorithm is $O(n^2)$" so
often an admission rather than a measurement.
""",
                        "whys": [
                            "Differing growth rates are the ordinary case for an upper bound; $O$ relates a function to anything that eventually dominates it.",
                            "The crossing is where the inequality *starts* holding, not where it stops — beyond $n = 1$ the gap only widens in the bound's favour.",
                            "Correct, and the point is that a true $O$ can still be a very loose one.",
                            "That is the definition of $\\Theta$, not of $O$; requiring equal growth would make the notation unable to express an upper bound at all.",
                        ],
                    },
                    {
                        "q": "Insertion sort finishes in about `n` steps on already-sorted input and about `n^2/4` on random input. Which statement is written correctly?",
                        "opts": [
                            "It is `O(n)`, because that bound does hold on some inputs",
                            "It is `Theta(n^2)`, because the hard case is the one that matters",
                            "It is `O(n^2)` and `Omega(n)`, and those two together give a `Theta`",
                            "Its best case is `Theta(n)`, its worst `Theta(n^2)` — separately",
                        ],
                        "a": 3,
                        "why": r"""
The notation compares functions, and "insertion sort" is not a function until you say
which input you are measuring over. Best case and worst case are two different
functions, and each has its own $\Theta$. Quoting a bound without naming the case is an
unfinished sentence, and the two unfinished versions here go wrong in opposite
directions: one takes the friendliest input as though it settled the matter, the other
takes the hardest. Mixing an $O$ from one case with an $\Omega$ from another does not
produce a $\Theta$ of anything, because the two inequalities are about different
functions and $\Theta$ requires both of a single one.
""",
                        "whys": [
                            "A bound that holds on one family of inputs says nothing about the others; this is the friendly case quoted as though it were the whole story.",
                            "This takes the hard case as the only one worth naming, which is a defensible convention but not what the sentence says — and it silently drops the best case, which is genuinely linear.",
                            "The $O$ comes from the worst case and the $\\Omega$ from the best, so they are inequalities about two different functions and cannot be combined into a $\\Theta$ of either.",
                            "Correct: name the case, then the function it defines has a growth rate of its own.",
                        ],
                    },
                    {
                        "q": "Which of these is **not** true?",
                        "opts": [
                            "`2^(2n) = O(2^n)` — the exponent is doubled here",
                            "`log_10 n = O(log_2 n)` — the log base changes",
                            "`2^(n+1) = O(2^n)` — one is added to the exponent",
                            "`n log_2 n = O(n^2)` — a log against a factor of n",
                        ],
                        "a": 0,
                        "why": r"""
$2^{2n} = (2^n)^2$, so a bound $2^{2n} \le c\,2^n$ would force $2^n \le c$ for all large
$n$, and no fixed constant survives that. The near neighbour is true and is what makes
the false one tempting: $2^{n+1} = 2\cdot 2^n$, where the extra factor really is the
constant 2. Adding to an exponent multiplies by a constant; multiplying an exponent
raises to a power, and a power is not a constant factor. Changing the base of a
*logarithm* is safe for the same reason read backwards — $\log_{10} n = \log_2 n /
\log_2 10$, a fixed multiple — which is why logarithm bases are never written inside
this notation and exponent bases always are.
""",
                        "whys": [
                            "Correct — this is the false one. It would require $2^n$ itself to be bounded by a constant.",
                            "True: the two logarithms differ by the fixed factor $1/\\log_2 10$, and a fixed factor is exactly what the constant absorbs.",
                            "True, with $c = 2$: adding one to the exponent doubles, and doubling is a constant factor.",
                            "True, since $\\log_2 n \\le n$ for $n \\ge 1$; a loose bound, but the question asks which fails, not which is tight.",
                        ],
                    },
                    {
                        "q": "One algorithm costs `100n` and another costs `n log_2 n`. Which is the sound reading?",
                        "opts": [
                            "`100n` is asymptotically better, overtaking at about `n = 2^100`",
                            "`n log_2 n` is asymptotically better, since a logarithm grows slowly",
                            "They are `Theta` of each other, the difference being a constant",
                            "`100n` is better at every size, a logarithm passing 100 at once",
                        ],
                        "a": 0,
                        "why": r"""
Divide both by $n$ and the comparison is $100$ against $\log_2 n$. The logarithm passes
100 only when $n$ passes $2^{100} \approx 1.27\times10^{30}$, so the linear algorithm is
asymptotically the better of the two and loses on every input that will ever exist. This
is the honest limit of the whole notation: it is a statement about large $n$, and how
large is hidden inside the threshold. The temptation is to treat "asymptotically better"
as advice, and here it is advice to use the slower program. A logarithm is not a
constant, so the two are not $\Theta$ of each other — the ratio $\log_2 n / 100$ is
unbounded, however slowly it climbs.
""",
                        "whys": [
                            "Correct on both counts, and the second is what stops the first from being useful advice.",
                            "This has the comparison backwards: dividing by $n$ leaves $\\log_2 n$ against the constant 100, and an unbounded quantity eventually exceeds a constant.",
                            "A constant factor would make them $\\Theta$ of each other, but $\\log_2 n$ is unbounded, so the ratio never settles.",
                            "$\\log_2 n$ reaches 100 only at $n = 2^{100}$, so \"almost immediately\" is off by every size that exists — though the practical conclusion happens to be right.",
                        ],
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M13
        {
            "title": "Infinite sets: counting past the finite",
            "summary": "What 'the same size' can still mean when nothing can be counted, and the one argument that shows some sets are out of reach.",
            "concepts": [
                "Two sets have the same size when a bijection exists between them — Module 5's definition, kept unchanged and applied where counting is impossible",
                "A set is countable when it can be listed as a sequence in which every member appears at some finite position",
                "A proper subset can have the same size as the whole: `n -> 2n` is a bijection from the naturals onto the even naturals",
                "Pigeonhole is a theorem about *finite* sets, and the previous bullet is exactly what it stops forbidding once the sets are infinite",
                "The integers are countable by interleaving, and the pairs of naturals by sweeping the diagonals — the Cantor pairing function names each pair's position outright",
                "A countable union of countable sets is countable, which is why the rationals are countable and so is the set of all finite strings over a finite alphabet",
                "Cantor's diagonal argument: against *any* proposed list of infinite bit strings, the string differing from the k-th at position k is on no line of it",
                "Programs are finite strings and so countable; languages are arbitrary sets of strings and so are not — some language is therefore decided by no program at all",
            ],
            "read": {
                "title": "The same size, when nothing can be counted",
                "minutes": 13,
                "body": r"""
Module 5 defined what it means for two sets to have the same size, and the definition
never mentioned numbers: two sets have the same size when a bijection runs between them.
For finite sets that is a roundabout way of saying they have equally many elements. It
was written that way because it is the only version that survives contact with sets that
cannot be counted at all, and this module is where that matters.

## A hotel with no vacancies and a room for the new guest

Picture a hotel with one room for each natural number — room 0, room 1, room 2, and so
on without end — and every room occupied. A guest arrives. There is no free room, in the
plain sense that no room number is unoccupied. Ask everyone to move from room $n$ to
room $n+1$. Everyone still has a room, each room still holds one guest, and room 0 is
now empty.

Nothing was smuggled in. The move is a function $n \mapsto n+1$ from the naturals into
the naturals; it is injective, so nobody was doubled up, and its image is everything
except 0, so exactly one room came free. What broke is not logic but the expectation
that a set cannot be put in one-to-one correspondence with a proper part of itself. That
expectation has a name in this course: it is the pigeonhole principle from Module 5, and
Module 5 was careful to say *finite*. Pigeonhole is not a fact about sets in general
that happens to be provable for finite ones. It is a fact about finite sets specifically,
and infinity is precisely where it stops.

The same thing, stripped of the hotel: $n \mapsto 2n$ maps the naturals onto the even
naturals. It is injective, since $2a = 2b$ forces $a = b$, and it is surjective onto the
evens by construction. So there are exactly as many even numbers as numbers, even though
the evens leave out infinitely much. A set with this property — a bijection with a
proper subset of itself — is exactly what "infinite" means, and it is worth taking as
the definition rather than as a paradox about one.

## Countable means listable

Call a set **countable** when its members can be arranged in a list $x_0, x_1, x_2,
\ldots$ in which every member appears at some finite position. That is the same thing as
a bijection with the naturals, written in the form that is easiest to check: to prove a
set countable, exhibit the list.

The integers are countable. Listing them as $0, 1, 2, 3, \ldots$ and then hoping to
reach the negatives afterwards fails — no negative number ever gets a finite position —
but interleaving works: $0, -1, 1, -2, 2, -3, 3, \ldots$, which is the function
$g(n) = n/2$ for even $n$ and $-(n+1)/2$ for odd $n$. Every integer appears, and appears
once. The lesson from the failed attempt is the one to keep: the list must reach
everything at a *finite* index, and "after the whole of an infinite run" is not a
position.

The pairs of naturals are countable too, and here the listing has to be cleverer, since
the obvious sweep — all pairs $(0, y)$, then all pairs $(1, y)$ — never finishes its
first row. Sweep the diagonals instead. Take all pairs with $x + y = 0$, then all with
$x + y = 1$, then $x + y = 2$, and so on. Each diagonal is finite, holding exactly
$s + 1$ pairs when $x + y = s$, so every pair is reached after finitely many others.

That sweep can be written in closed form. Before the diagonal $x + y = s$ begins, the
earlier diagonals have contributed $1 + 2 + \cdots + s = s(s+1)/2$ pairs — the
triangular number from Module 7 — and within the diagonal the pair $(x, y)$ sits at
offset $y$. So

$$\pi(x, y) = \frac{(x+y)(x+y+1)}{2} + y$$

which is the Cantor pairing function. It sends $(0,0) \mapsto 0$, $(1,0) \mapsto 1$,
$(0,1) \mapsto 2$, $(2,0) \mapsto 3$, $(1,1) \mapsto 4$, $(0,2) \mapsto 5$, and it is a
bijection from $\mathbb{N} \times \mathbb{N}$ onto $\mathbb{N}$ — two coordinates encoded
in one number with nothing lost and nothing repeated.

From there the results come quickly. A countable union of countable sets is countable:
index the sets by $i$ and their members by $j$, and $\pi(i, j)$ lists the union. The
positive rationals are countable, because $p/q$ is a pair, so they inject into the pairs;
duplicates like $2/4$ are dropped by keeping only lowest terms, and a subset of a
countable set is countable. Add the negatives by interleaving and $\mathbb{Q}$ is
countable — a set that is dense, so that between any two rationals lie infinitely many
more, is nevertheless no bigger than $\mathbb{N}$. That is the first sign that "same
size" carries less information than intuition expects it to.

And the finite strings over a finite alphabet are countable: list them by length, and
alphabetically within each length. Every string of length $k$ appears after fewer than
$2^{k+1}$ others. This is the one to remember, because a program *is* a finite string
over a finite alphabet. **There are only countably many programs.**

## The argument that cannot be beaten

Now consider the infinite bit strings: functions from $\mathbb{N}$ to $\{0, 1\}$. Are
there countably many?

Suppose there were. Then some list $s_0, s_1, s_2, \ldots$ contains all of them. Write
the first few rows out and look down the diagonal:

```text
        pos 0   1   2   3
  s0  [   0    1   1   0  ... ]
  s1  [   1    1   0   0  ... ]
  s2  [   0    0   1   1  ... ]
  s3  [   1    0   1   1  ... ]
```

The diagonal entries are $s_0[0] = 0$, $s_1[1] = 1$, $s_2[2] = 1$, $s_3[3] = 1$. Build a
new string $d$ by flipping every one of them: $d[k] = 1 - s_k[k]$, giving
$d = 1, 0, 0, 0, \ldots$.

Where is $d$ in the list? It is not $s_0$, because they differ at position 0. It is not
$s_1$, because they differ at position 1. It is not $s_k$ for any $k$ at all, because
$d$ was built to differ from $s_k$ exactly there. So the list does not contain every
infinite bit string, and since the list was arbitrary, no list does. The set is
**uncountable**.

The tempting objection is worth stating plainly, because nearly everyone raises it: *just
add $d$ to the list.* You can. The result is a different list, with a different diagonal,
and the construction applied to that one produces a string missing from it too. The
argument was never about one particular list — it takes an arbitrary list as its
hypothesis and destroys it, so patching an instance is answering a claim that was not
made. Recognising that a proof is universally quantified over its hypothesis is the
skill Module 2 and Module 3 were building, and this is where it earns its keep.

## Where the idea stops holding

The diagonal argument needs two things, and both are easy to lose sight of. The list
must be indexed by the naturals, and each object in it must be indexed by the naturals,
so that position $k$ of row $k$ exists. Applied to finite strings it fails immediately,
and it should: the finite strings are countable, and a diagonal over a list of strings of
growing length has nothing to read once it passes the end of a row.

The other limit is a limit on what countability tells you. $\mathbb{N}$ and $\mathbb{Q}$
are the same size while being utterly unalike in order and density; "same size" was
defined by bijection alone, and a bijection is free to shatter every other structure the
sets carry. It is a coarse notion deliberately, and reading more into it than it says is
its own error.

## What this is for

A language over $\{0,1\}$ is a set of strings, that is, a subset of a countably infinite
set. Naming a subset is the same as naming, for each string in turn, whether it is in —
which is an infinite bit string. So there are exactly as many languages as infinite bit
strings: uncountably many. And there are only countably many programs.

No injection runs from an uncountable set into a countable one. So there is no
assignment of a distinct program to every language, and almost every language is decided
by no program whatever. Notice what that argument did *not* do: it exhibited no
particular undecidable problem, and it needed no clever construction. It counted. The
theory of computation course later builds a specific undecidable problem — the halting
problem, by running the diagonal argument on a supposed decider instead of on a list of
strings — and it is the same argument in different clothes. The counting comes first,
and it says that such a problem has to exist before anyone goes looking for one.
""",
            },
            "derive": {
                "title": "Numbering the diagonals: the pairing function, built",
                "minutes": 12,
                "brief": r"""
The sweep that lists $\mathbb{N} \times \mathbb{N}$ takes the diagonals $x + y = 0$,
then $x + y = 1$, then $x + y = 2$, and so on. It reaches every pair, because each
diagonal is finite and a given pair's diagonal is fixed by its coordinates. What is less
apparent is that the position of a pair can be written down in closed form, with no
counting, and that is what this derivation builds.

Write $s = x + y$ for the diagonal a pair sits on.
""",
                "vars": ["x", "y", "s", "k", "n"],
                "steps": [
                    {
                        "prompt": r"How many pairs of naturals $(x, y)$ satisfy $x + y = k$ exactly? Give the count in terms of $k$.",
                        "answer": r"k + 1",
                        "placeholder": "a count in k",
                        "hint": r"Once $x$ is chosen, $y$ is forced. So count the legal values of $x$.",
                        "deconstruct": [
                            r"$x$ can be $0, 1, \ldots, k$.",
                            "Both coordinates are naturals, so neither may be negative — that is what caps x at k.",
                        ],
                    },
                    {
                        "prompt": r"The sweep finishes every earlier diagonal before starting diagonal $s$. Add up the counts for $k = 0$ through $k = s-1$ to get the number of pairs listed before it begins.",
                        "answer": r"\frac{s(s+1)}{2}",
                        "placeholder": r"\frac{?}{2}",
                        "hint": r"Summing $k+1$ for $k = 0 \ldots s-1$ is the same as summing $j$ for $j = 1 \ldots s$ — the triangular number of Module 7.",
                        "deconstruct": [
                            r"The terms are $1, 2, 3, \ldots, s$.",
                            r"Pair the first with the last: each pair sums to $s+1$, and there are $s/2$ of them.",
                        ],
                    },
                    {
                        "prompt": r"Inside diagonal $s$ the sweep runs from $(s, 0)$ to $(0, s)$, one step at a time, so the pair $(x, y)$ sits at offset $y$ within it. Write the pair's overall position, in terms of $s$ and $y$.",
                        "answer": r"\frac{s(s+1)}{2} + y",
                        "placeholder": "everything before it, plus its offset",
                        "hint": "The position is the number of pairs listed before this diagonal, plus how far into this diagonal the pair sits.",
                        "deconstruct": [
                            r"The count before the diagonal is the previous step's answer.",
                            r"The offset within the diagonal is $y$, because $y$ climbs from 0 as the sweep advances.",
                        ],
                    },
                    {
                        "prompt": r"Now eliminate $s$ by substituting $s = x + y$, to get the pairing function in its two arguments.",
                        "answer": r"\frac{(x+y)(x+y+1)}{2} + y",
                        "placeholder": r"\frac{(?)(?)}{2} + ?",
                        "hint": "Only the s inside the fraction changes; the trailing offset is already in terms of y.",
                        "deconstruct": [
                            r"Replace both occurrences of $s$ in $s(s+1)/2$.",
                            r"Leave the $+ y$ alone.",
                        ],
                    },
                    {
                        "prompt": r"Evaluate the result at $(x, y) = (1, 1)$.",
                        "answer": r"4",
                        "placeholder": "a single number",
                        "hint": r"$s = 2$ here, so the triangular part is $2\cdot3/2$.",
                        "deconstruct": [
                            r"$(x+y) = 2$ and $(x+y+1) = 3$.",
                            r"Then add $y = 1$.",
                        ],
                    },
                    {
                        "prompt": r"The first pair on diagonal $s$ is $(s, 0)$, where the offset is zero. Write its position — the smallest index the diagonal occupies.",
                        "answer": r"\frac{s(s+1)}{2}",
                        "placeholder": r"\frac{?}{2}",
                        "hint": r"Put $y = 0$ into the position formula in terms of $s$ and $y$.",
                        "deconstruct": [
                            r"The offset term vanishes.",
                            "What is left is the count of everything on the earlier diagonals.",
                        ],
                    },
                ],
                "closing": r"""
The first six positions come out as $\pi(0,0) = 0$, $\pi(1,0) = 1$, $\pi(0,1) = 2$,
$\pi(2,0) = 3$, $\pi(1,1) = 4$, $\pi(0,2) = 5$ — every natural number used exactly once,
which is what makes $\pi$ a bijection rather than merely an injection. Two coordinates
have been folded into one number reversibly.

That is more than a curiosity. It is the machine behind two of the results this module
states: a countable union of countable sets is countable, because $\pi(i, j)$ lists the
$j$-th member of the $i$-th set at a single finite position; and the rationals are
countable, because a rational is a pair. And it is worth noticing that the argument
never counted anything. It exhibited a formula and checked it was a bijection — which is
the only kind of proof available once the sets stop being finite.
""",
            },
            "blanks": {
                "title": "Pairing, unpairing, and defeating a list",
                "minutes": 9,
                "lang": "python",
                "caption": "cantor.py",
                "brief": r"""
Two constructions from this module, written out. The first folds a pair of naturals into
one number and takes it apart again; the second takes any proposed list of infinite bit
strings and returns a string that is not on it.
""",
                "listing": r'''
def pair(x, y):
    """Cantor's pairing function: the position of (x, y) in the diagonal sweep."""
    s = x + y
    return ___ + y


def unpair(n):
    """The inverse. Find the diagonal first, then read the offset off it."""
    s = 0
    while pair(s, 0) <= n:          # diagonal s starts at or before n, so try the next
        s += 1
    s -= 1                          # step back to the diagonal that contains n
    y = n - pair(s, 0)
    return (___, y)


def diagonal(rows):
    """Given rows[k][k] for each k, return a string on none of the listed rows."""
    return [___ for k in range(len(rows))]


assert [pair(0, 0), pair(1, 0), pair(0, 1), pair(2, 0), pair(1, 1)] == [0, 1, 2, ___, 4]
assert all(pair(*unpair(n)) == n for n in range(1000))
assert diagonal([[0, 1, 1, 0], [1, 1, 0, 0], [0, 0, 1, 1], [1, 0, 1, 1]]) == ___
''',
                "blanks": [
                    {
                        "prompt": "The number of pairs the sweep lists before diagonal `s` begins.",
                        "opts": ["s * (s + 1) // 2", "s * (s - 1) // 2", "s * s // 2", "(s + y) * (s + y + 1) // 2"],
                        "a": 0,
                        "why": r"""
Diagonal $k$ holds $k+1$ pairs, so the diagonals before $s$ contribute
$1 + 2 + \cdots + s = s(s+1)/2$. Integer division is exact here because one of $s$ and
$s+1$ is always even.
""",
                        "whys": [
                            "Correct — the triangular number of $s$, which counts $1 + 2 + \\cdots + s$.",
                            "This counts $1 + 2 + \\cdots + (s-1)$, one diagonal short, so every index past the first diagonal comes out too small.",
                            "Close numerically but wrong: it drops the $+1$ that makes diagonal $k$ hold $k+1$ pairs rather than $k$, and $\\pi(0,0)$ would still be 0 while $\\pi(1,0)$ came out 0 as well.",
                            "The variable $s$ already *is* $x + y$, so this squares the diagonal index and lands far past the pair's true position.",
                        ],
                    },
                    {
                        "prompt": "The first coordinate, recovered from the diagonal and the offset.",
                        "opts": ["s - y", "s + y", "y - s", "s"],
                        "a": 0,
                        "why": r"""
The pair sits on diagonal $s = x + y$, and the offset within the diagonal is $y$, so
$x = s - y$. That is the whole of the inversion: find which diagonal $n$ falls on, then
subtract.
""",
                        "whys": [
                            "Correct, straight from $s = x + y$.",
                            "This would make $x + y$ equal $s + 2y$ rather than $s$, so the recovered pair would sit on the wrong diagonal entirely.",
                            "Negative whenever the offset exceeds the diagonal index, which the naturals do not permit; it also has the subtraction the wrong way round.",
                            "This ignores the offset, so every pair on a diagonal would decode to the same first coordinate and `unpair` would not be injective.",
                        ],
                    },
                    {
                        "prompt": "The k-th bit of a string guaranteed to be on none of the rows.",
                        "opts": ["1 - rows[k][k]", "rows[k][k]", "1 - rows[0][k]", "1 - rows[k][0]"],
                        "a": 0,
                        "why": r"""
To differ from row $k$ it is enough to differ from it at a single position, and position
$k$ is the one the construction reserves for that purpose. Flipping the diagonal entry
does exactly that, simultaneously for every $k$, which is why one string can defeat an
entire list at once.
""",
                        "whys": [
                            "Correct: at position $k$ this is the opposite of row $k$, so it matches no row anywhere.",
                            "This copies the diagonal instead of flipping it, producing a string that agrees with every row at the one position that was supposed to separate them.",
                            "This flips a single row and differs from that row alone; every other row is left free to equal it.",
                            "This reads down the first column rather than the diagonal, so it is built to differ from row $k$ at position 0 for every $k$ at once — which is impossible for more than two rows and produces no guarantee at all.",
                        ],
                    },
                    {
                        "prompt": "The position of the pair `(2, 0)` in the sweep.",
                        "opts": ["3", "2", "4", "5"],
                        "a": 0,
                        "why": r"""
$(2,0)$ opens the diagonal $x + y = 2$, and the diagonals before it held $1 + 2 = 3$
pairs, so it takes index 3. The sweep so far is $(0,0), (1,0), (0,1), (2,0), (1,1),
(0,2)$ at indices 0 through 5.
""",
                        "whys": [
                            "Correct — the first index of diagonal 2, which is the triangular number $2\\cdot3/2 = 3$.",
                            "Index 2 belongs to $(0,1)$, the last pair of diagonal 1.",
                            "Index 4 belongs to $(1,1)$, the pair one step further along diagonal 2.",
                            "Index 5 belongs to $(0,2)$, which closes diagonal 2.",
                        ],
                    },
                    {
                        "prompt": "The string the diagonal construction returns for those four rows.",
                        "opts": ["[1, 0, 0, 0]", "[0, 1, 1, 1]", "[1, 1, 0, 1]", "[0, 0, 1, 0]"],
                        "a": 0,
                        "why": r"""
The diagonal entries are $0, 1, 1, 1$, and flipping each gives $1, 0, 0, 0$. Check it
against each row in turn: it differs from the first at position 0, from the second at
position 1, from the third at position 2 and from the fourth at position 3 — one
disagreement per row, which is all that is needed.
""",
                        "whys": [
                            "Correct: the diagonal reads $0, 1, 1, 1$ and every bit is flipped.",
                            "This is the diagonal copied rather than flipped, so it agrees with each row exactly where it was meant to differ.",
                            "This is the first row's contents with one bit altered; it differs from that row but is under no constraint at all with respect to the others.",
                            "This flips the first column rather than the diagonal, and it happens to equal the third row's opening bits, so it defeats nothing.",
                        ],
                    },
                ],
            },
            "quiz": {
                "title": "Bijections, listings and what the diagonal destroys",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The map `n -> 2n` is a bijection from the naturals onto the even naturals. What does that establish?",
                        "opts": [
                            "That defining size by bijection breaks down once sets are infinite",
                            "That they are the same size, and pigeonhole is a finite theorem",
                            "That the evens are half the size, exactly as one would expect",
                            "Nothing — a bijection onto a proper subset cannot really exist",
                        ],
                        "a": 1,
                        "why": r"""
The bijection is real: $2a = 2b$ forces $a = b$, and every even number is hit. So by the
only definition of size available — the one Module 5 gave — the two sets are the same
size, even though one omits infinitely much. Nothing is broken by this. What it shows is
that the intuition being violated, "a proper subset must be smaller", is the pigeonhole
principle, and Module 5 stated pigeonhole for *finite* sets on purpose. Having a
bijection with a proper subset of itself is not an anomaly of the naturals; it is what
being infinite means, and it can be taken as the definition.
""",
                        "whys": [
                            "The definition survives intact — it is the finite intuition about subsets that does not, and that intuition was never part of the definition.",
                            "Correct, and the second half is why the first half is not a paradox.",
                            "Halving is what the map does to the *numbers*; it does nothing to the size of the set, since every even number still receives exactly one natural.",
                            "Such a bijection is impossible for finite sets and routine for infinite ones — the map here is an explicit example of one.",
                        ],
                    },
                    {
                        "q": "Why does listing the integers as `0, 1, 2, 3, ...` and then the negatives afterwards fail to show they are countable?",
                        "opts": [
                            "It does show it — the two runs together cover every integer",
                            "Because the set of the negative integers is itself uncountable",
                            "Because no negative integer would ever sit at a finite index",
                            "Because a listing has to run in increasing numerical order",
                        ],
                        "a": 2,
                        "why": r"""
Countable means every member sits at a *finite* index. The first run never ends, so
nothing after it is ever reached, and "position infinity plus one" is not a position. The
fix is not to work harder on the ordering but to interleave: $0, -1, 1, -2, 2, \ldots$
puts $-k$ at index $2k-1$ and $k$ at index $2k$, both finite, and covers everything. The
requirement is finiteness of each index, not any particular order — a listing is free to
jump about, and the interleaved one does.
""",
                        "whys": [
                            "The two runs do cover every integer as sets, but a listing needs each member at a finite index, and the second run begins at no index at all.",
                            "The negatives are countable — $n \\mapsto -n-1$ lists them — so the failure is in the arrangement rather than the set.",
                            "Correct: the first run exhausts every finite index before the second begins.",
                            "Order is not a requirement; the interleaved listing that works is not increasing, and it is a perfectly good witness.",
                        ],
                    },
                    {
                        "q": "You show someone the diagonal argument and they say: fine, add the new string `d` to the list. What is wrong with that reply?",
                        "opts": [
                            "Nothing is wrong — the argument only rules out lists omitting `d`",
                            "The hypothesis was an arbitrary list, so the new one fails too",
                            "`d` is not a genuine bit string, so it cannot be added at all",
                            "The list is already infinite, so nothing can be appended to it",
                        ],
                        "a": 1,
                        "why": r"""
The proof does not say "here is a list, and here is what it misses". It says: take any
list whatever, and it misses something. Producing a second list is producing a second
instance of the hypothesis, and the construction runs again on that one. Patching an
instance answers a claim nobody made — the statement is universally quantified over the
list, and that is exactly the shape Module 2 gave for such statements and Module 3 gave
for refuting them. Appending to an infinite list is perfectly legal, and $d$ is an
ordinary bit string, so neither of those is the objection.
""",
                        "whys": [
                            "The argument rules out every list, because it begins by assuming an arbitrary one rather than a particular one.",
                            "Correct, and this is the whole force of a universally quantified hypothesis.",
                            "$d$ is a perfectly ordinary infinite bit string — it is built one bit at a time from the entries of the list.",
                            "An infinite list can be extended; shifting every entry up by one leaves room at the front, exactly as the hotel did.",
                        ],
                    },
                    {
                        "q": "The rationals are countable and the infinite bit strings are not. Which reading is right?",
                        "opts": [
                            "The rationals list as pairs, and their density is beside the point",
                            "The rationals are countable because they lie thinly along the line",
                            "The bit strings are uncountable because each is infinitely long",
                            "The bit strings are uncountable because they outnumber the naturals",
                        ],
                        "a": 0,
                        "why": r"""
A rational is a pair of integers, the pairs of naturals are listable by the diagonal
sweep, and duplicates are removed by keeping lowest terms — so the rationals inject into
a countable set and are countable. That they are dense, with infinitely many between any
two, plays no part: "same size" was defined by bijection and is blind to order and
spacing. The uncountability of the bit strings likewise has nothing to do with any
individual string's length; the finite-position sequences $\mathbb{N} \to \mathbb{N}$
listed by the pairing function are infinite objects too. It is the diagonal construction
that does the work, and no restatement of the conclusion replaces it.
""",
                        "whys": [
                            "Correct, and noting that density is irrelevant is the part that usually goes missing.",
                            "The rationals are dense rather than thinly spread — between any two lie infinitely many more — so this gets the geometry backwards as well as making it do work it cannot do.",
                            "Length is not the issue: the diagonal sweep lists infinitely many infinite objects quite happily, so being infinite cannot be what puts a set out of reach.",
                            "True as a statement, but it restates the conclusion rather than giving the reason; what establishes it is the diagonal construction defeating every proposed list.",
                        ],
                    },
                    {
                        "q": "The counting argument says some language over `{0,1}` is decided by no program. What does it deliver?",
                        "opts": [
                            "A specific undecidable language, built by the diagonal construction",
                            "A proof that no program is able to read its own source code",
                            "Existence only: countably many programs, uncountably many languages",
                            "A proof that the languages anyone cares about are undecidable",
                        ],
                        "a": 2,
                        "why": r"""
A program is a finite string over a finite alphabet, so the programs are countable. A
language is a subset of the strings, which is the same thing as an infinite bit string,
so the languages are uncountable — and no injection runs from an uncountable set into a
countable one. That settles existence and exhibits nothing: no particular language is
named, and none of the languages anyone cares about is implicated. Building a specific
undecidable problem takes the diagonal argument applied to a supposed decider rather
than to a list, which is the halting problem and is done elsewhere. The counting comes
first and says the search is not futile.
""",
                        "whys": [
                            "No language is named here; the diagonal is applied to the abstract list of bit strings, which fixes nothing in particular.",
                            "Self-reference is the engine of the halting-problem construction, and a program can in fact be handed its own source; the counting argument uses neither idea.",
                            "Correct — pure existence, from a comparison of two cardinalities.",
                            "Most of the uncountably many languages are arbitrary and of interest to nobody, and plenty of interesting languages are perfectly decidable.",
                        ],
                    },
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a discrete mathematics toolkit",
        "runtime": "python",
        "minutes": 280,
        "brief": r'''
One reusable library spanning the whole course. `toolkit.py` holds the
functions and is what the checks import; `main.py` is a demo script.

`formula.py` is **given** — it is the tokeniser, parser and evaluator you built
in Module 1, so you can spend this build on the new mathematics. Import from
it: `from formula import parse, tokenise, variables, evaluate`.

## Logic

- `models(formula)` — every satisfying assignment, as a list of dicts mapping
  variable name to bool, in binary-counting order with `False` first.

```text
models("P & Q")  ->  [{"P": True, "Q": True}]
models("P & ~P") ->  []
```

- `classify(formula)` — `"tautology"`, `"contradiction"` or `"contingency"`.
- `entails(premises, conclusion)` — semantic entailment. `premises` is a list
  of formula strings. True when every assignment (over the union of all the
  variables) that satisfies **all** the premises also satisfies the conclusion.

```text
entails(["P", "P -> Q"], "Q")   ->  True     modus ponens
entails(["P -> Q", "Q"], "P")   ->  False    affirming the consequent
entails(["P & ~P"], "Q")        ->  True     ex falso quodlibet
entails([], "P | ~P")           ->  True
```

## Counting

- `choose(n, k)` — the binomial coefficient, multiplicatively; `0` outside
  `0 <= k <= n`, `ValueError` for a negative `n`.
- `stirling_second(n, k)` — set partitions of an n-set into exactly k non-empty
  blocks, from the recurrence `S(n, k) = k*S(n-1, k) + S(n-1, k-1)`, with
  `S(0, 0) = 1` and `S(n, 0) = 0` for `n > 0`. `S(4, 2)` is `7`.
- `bell(n)` — the sum of `stirling_second(n, k)` over all `k`. The first Bell
  numbers are `1, 1, 2, 5, 15, 52, 203`.
- `derangements(n)` — permutations with no fixed point: `D(0) = 1`, `D(1) = 0`
  and `D(n) = (n-1) * (D(n-1) + D(n-2))`. `D(4)` is `9`.

## Number theory

- `sieve(limit)` — primes up to and including `limit`.
- `mod_pow(base, exponent, modulus)` — square-and-multiply, no built-in.
- `mod_inverse(a, m)` — `ValueError` when `m < 2` or `gcd(a, m) != 1`.
- `euler_phi(n)` — how many of `1..n` are coprime to `n`. `phi(1) = 1`,
  `phi(36) = 12`. Derive it from the prime factorisation, not by counting.
- `crt(remainders, moduli)` — the Chinese remainder theorem. Returns
  `(x, product)` where `x` is the unique solution in `0 .. product-1`. Every
  modulus must be at least 2, the lists must be the same non-empty length, and
  moduli that are not pairwise coprime are a `ValueError`.

```text
crt([2, 3, 2], [3, 5, 7])  ->  (23, 105)
```

## Relations and graphs

- `transitive_closure(elements, pairs)` — the closure as a set of pairs.
- `connected_components(adjacency)` — the components as a sorted list of sorted
  lists of nodes.
- `two_colouring(adjacency)` — a dict node to `0`/`1`, or `None`.

## Suggested order

Logic first (the parser is already there), then counting, then the number
theory, then the graphs. The checks follow the same order.
''',
        "deliverables": [
            "`toolkit.py` — the fifteen functions above, importable with no side effects",
            "`main.py` — a demo that checks an argument, counts partitions, solves a congruence system and colours a graph",
            "A `crt` that reports non-coprime moduli as a `ValueError` rather than returning nonsense",
            "Counting routines that stay exact for large arguments (no floating point anywhere)",
            "Docstrings stating each function's domain and what it raises",
        ],
        "constraints": [
            "Standard library only — `itertools` is the only import you need beyond `formula`",
            "`toolkit.py` must define functions only; importing it must print nothing",
            "No `math.comb`, `math.perm`, `math.factorial`, `math.gcd`, and no three-argument `pow`",
            "Every function must be total on its documented domain and raise `ValueError` outside it",
            "`formula.py` is given and must not be edited",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "All automated checks pass, including the empty-input, boundary and non-coprime cases."},
            {"criterion": "Mathematical faithfulness", "weight": 25,
             "evidence": "Recurrences and identities are implemented as stated; results are exact integers, never floats."},
            {"criterion": "Error handling", "weight": 20,
             "evidence": "Arguments outside the documented domain raise ValueError instead of returning a wrong answer."},
            {"criterion": "Readability", "weight": 15,
             "evidence": "Docstrings name the domain and the exceptions; no duplicated logic between the counting routines."},
        ],
        "hints": [
            "`models` and `classify` both come from one truth-table walk: parse once, get `variables`, then loop over `itertools.product([False, True], repeat=n)`.",
            "`entails` is the same loop over the union of every formula's variables: fail the moment an assignment satisfies all premises but not the conclusion.",
            "`stirling_second` is cleanest as a table: build rows 0..n, each entry `k*S(n-1, k) + S(n-1, k-1)`. `bell(n)` then just sums row n.",
            "`crt` builds the answer as `sum(r * (M // m) * mod_inverse(M // m, m))` modulo `M`. If two moduli share a factor, `mod_inverse` raises for you — let it.",
        ],
        "files": [
            {"name": "formula.py", "ro": True, "content": r'''
"""Given: the tokeniser, parser and evaluator from Module 1. Do not edit."""

import re

TOKEN_RE = re.compile(r"->|[~&|()]|[A-Za-z][A-Za-z0-9_]*")


def tokenise(text):
    """Split a formula into token strings. ValueError on an illegal character."""
    tokens = []
    position = 0
    while position < len(text):
        if text[position].isspace():
            position += 1
            continue
        match = TOKEN_RE.match(text, position)
        if match is None:
            raise ValueError(f"unexpected character {text[position]!r} at {position}")
        tokens.append(match.group(0))
        position = match.end()
    return tokens


def parse(tokens):
    """Turn a token list into a nested-tuple AST. ValueError when malformed."""
    node, position = _implication(tokens, 0)
    if position != len(tokens):
        raise ValueError(f"unexpected token {tokens[position]!r}")
    return node


def _implication(tokens, position):
    left, position = _disjunction(tokens, position)
    if position < len(tokens) and tokens[position] == "->":
        right, position = _implication(tokens, position + 1)
        return ("implies", left, right), position
    return left, position


def _disjunction(tokens, position):
    node, position = _conjunction(tokens, position)
    while position < len(tokens) and tokens[position] == "|":
        right, position = _conjunction(tokens, position + 1)
        node = ("or", node, right)
    return node, position


def _conjunction(tokens, position):
    node, position = _unary(tokens, position)
    while position < len(tokens) and tokens[position] == "&":
        right, position = _unary(tokens, position + 1)
        node = ("and", node, right)
    return node, position


def _unary(tokens, position):
    if position >= len(tokens):
        raise ValueError("formula ended too early")
    token = tokens[position]
    if token == "~":
        node, position = _unary(tokens, position + 1)
        return ("not", node), position
    if token == "(":
        node, position = _implication(tokens, position + 1)
        if position >= len(tokens) or tokens[position] != ")":
            raise ValueError("missing closing parenthesis")
        return node, position + 1
    if not token[0].isalpha():
        raise ValueError(f"expected a variable, found {token!r}")
    return ("var", token), position + 1


def variables(node):
    """The sorted, deduplicated variable names appearing in the AST."""
    found = set()
    stack = [node]
    while stack:
        current = stack.pop()
        if current[0] == "var":
            found.add(current[1])
        else:
            stack.extend(current[1:])
    return sorted(found)


def evaluate(node, env):
    """The truth value of the AST under env: {name: bool}."""
    kind = node[0]
    if kind == "var":
        if node[1] not in env:
            raise KeyError(f"no value given for {node[1]!r}")
        return bool(env[node[1]])
    if kind == "not":
        return not evaluate(node[1], env)
    if kind == "and":
        return evaluate(node[1], env) and evaluate(node[2], env)
    if kind == "or":
        return evaluate(node[1], env) or evaluate(node[2], env)
    if kind == "implies":
        return (not evaluate(node[1], env)) or evaluate(node[2], env)
    raise ValueError(f"unknown node kind {kind!r}")
'''},
            {"name": "toolkit.py", "content": r'''
import itertools

from formula import evaluate, parse, tokenise, variables


# ------------------------------------------------------------------ logic
def models(formula):
    """Every satisfying assignment of the formula, as a list of dicts."""
    # your code here


def classify(formula):
    """tautology, contradiction or contingency."""
    # your code here


def entails(premises, conclusion):
    """Do all the premises together semantically entail the conclusion?"""
    # your code here


# --------------------------------------------------------------- counting
def choose(n, k):
    """The binomial coefficient C(n, k)."""
    # your code here


def stirling_second(n, k):
    """Set partitions of an n-set into exactly k non-empty blocks."""
    # your code here


def bell(n):
    """The n-th Bell number: partitions of an n-set into any number of blocks."""
    # your code here


def derangements(n):
    """Permutations of n items with no fixed point."""
    # your code here


# ---------------------------------------------------------- number theory
def sieve(limit):
    """Every prime up to and including limit."""
    # your code here


def mod_pow(base, exponent, modulus):
    """base ** exponent % modulus by square-and-multiply."""
    # your code here


def mod_inverse(a, m):
    """The inverse of a modulo m. ValueError when there is none."""
    # your code here


def euler_phi(n):
    """How many of 1..n are coprime to n."""
    # your code here


def crt(remainders, moduli):
    """(x, product) solving the system of congruences."""
    # your code here


# ------------------------------------------------------- relations, graphs
def transitive_closure(elements, pairs):
    """The transitive closure of a relation, as a set of pairs."""
    # your code here


def connected_components(adjacency):
    """The components, as a sorted list of sorted node lists."""
    # your code here


def two_colouring(adjacency):
    """A dict node -> 0/1 with no monochromatic edge, or None."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from toolkit import (bell, classify, connected_components, crt, derangements,
                     entails, euler_phi, models, sieve, stirling_second,
                     transitive_closure, two_colouring)

print("modus ponens :", entails(["P", "P -> Q"], "Q"))
print("P | ~P       :", classify("P | ~P"))
print("models P & Q :", models("P & Q"))
print("Bell 0..6    :", [bell(n) for n in range(7)])
print("crt          :", crt([2, 3, 2], [3, 5, 7]))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "toolkit.py", "content": r'''
import itertools

from formula import evaluate, parse, tokenise, variables


# ------------------------------------------------------------------ logic
def _compile(formula):
    """Parse a formula string into (ast, sorted variable names)."""
    node = parse(tokenise(formula))
    return node, variables(node)


def models(formula):
    """Every satisfying assignment of the formula, as a list of dicts."""
    node, names = _compile(formula)
    found = []
    for values in itertools.product([False, True], repeat=len(names)):
        env = dict(zip(names, values))
        if evaluate(node, env):
            found.append(env)
    return found


def classify(formula):
    """tautology, contradiction or contingency."""
    node, names = _compile(formula)
    results = [evaluate(node, dict(zip(names, values)))
               for values in itertools.product([False, True], repeat=len(names))]
    if all(results):
        return "tautology"
    if not any(results):
        return "contradiction"
    return "contingency"


def entails(premises, conclusion):
    """Do all the premises together semantically entail the conclusion?"""
    parsed = [parse(tokenise(text)) for text in premises]
    goal = parse(tokenise(conclusion))
    names = set(variables(goal))
    for node in parsed:
        names.update(variables(node))
    names = sorted(names)
    for values in itertools.product([False, True], repeat=len(names)):
        env = dict(zip(names, values))
        if all(evaluate(node, env) for node in parsed) and not evaluate(goal, env):
            return False
    return True


# --------------------------------------------------------------- counting
def choose(n, k):
    """The binomial coefficient C(n, k). ValueError for a negative n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def stirling_second(n, k):
    """Set partitions of an n-set into exactly k non-empty blocks."""
    if n < 0 or k < 0:
        raise ValueError("n and k must be non-negative")
    if k > n:
        return 0
    row = [1] + [0] * k
    for i in range(1, n + 1):
        nxt = [0] * (k + 1)
        for j in range(1, min(i, k) + 1):
            nxt[j] = j * row[j] + row[j - 1]
        row = nxt
    return row[k]


def bell(n):
    """The n-th Bell number: partitions of an n-set into any number of blocks."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return sum(stirling_second(n, k) for k in range(n + 1))


def derangements(n):
    """Permutations of n items with no fixed point."""
    if n < 0:
        raise ValueError("n must be non-negative")
    previous, current = 1, 0
    if n == 0:
        return 1
    for i in range(2, n + 1):
        previous, current = current, (i - 1) * (current + previous)
    return current


# ---------------------------------------------------------- number theory
def sieve(limit):
    """Every prime up to and including limit."""
    if limit < 2:
        return []
    flags = [True] * (limit + 1)
    flags[0] = flags[1] = False
    candidate = 2
    while candidate * candidate <= limit:
        if flags[candidate]:
            for multiple in range(candidate * candidate, limit + 1, candidate):
                flags[multiple] = False
        candidate += 1
    return [number for number, flag in enumerate(flags) if flag]


def mod_pow(base, exponent, modulus):
    """base ** exponent % modulus by square-and-multiply."""
    if exponent < 0:
        raise ValueError("exponent must be non-negative")
    if modulus < 1:
        raise ValueError("modulus must be positive")
    result = 1 % modulus
    base %= modulus
    while exponent:
        if exponent & 1:
            result = result * base % modulus
        base = base * base % modulus
        exponent >>= 1
    return result


def _extended_gcd(a, b):
    """(g, x, y) with a*x + b*y == g == gcd(a, b), for non-negative a, b."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t


def mod_inverse(a, m):
    """The inverse of a modulo m. ValueError when there is none."""
    if m < 2:
        raise ValueError("modulus must be at least 2")
    g, x, _ = _extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} is not invertible modulo {m}")
    return x % m


def euler_phi(n):
    """How many of 1..n are coprime to n. ValueError for n < 1."""
    if n < 1:
        raise ValueError("n must be positive")
    result = n
    remaining = n
    divisor = 2
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            while remaining % divisor == 0:
                remaining //= divisor
            result -= result // divisor
        divisor += 1
    if remaining > 1:
        result -= result // remaining
    return result


def crt(remainders, moduli):
    """(x, product) solving the system of congruences. ValueError if impossible."""
    if len(remainders) != len(moduli):
        raise ValueError("remainders and moduli must have the same length")
    if not moduli:
        raise ValueError("at least one congruence is required")
    for modulus in moduli:
        if modulus < 2:
            raise ValueError("every modulus must be at least 2")
    product = 1
    for modulus in moduli:
        product *= modulus
    total = 0
    for remainder, modulus in zip(remainders, moduli):
        rest = product // modulus
        total += remainder * rest * mod_inverse(rest, modulus)
    return total % product, product


# ------------------------------------------------------- relations, graphs
def transitive_closure(elements, pairs):
    """The transitive closure of a relation, as a set of pairs."""
    index = {element: i for i, element in enumerate(elements)}
    size = len(elements)
    closure = [[False] * size for _ in range(size)]
    for left, right in pairs:
        if left not in index or right not in index:
            raise ValueError(f"pair ({left!r}, {right!r}) leaves the ground set")
        closure[index[left]][index[right]] = True
    for k in range(size):
        for i in range(size):
            if closure[i][k]:
                for j in range(size):
                    if closure[k][j]:
                        closure[i][j] = True
    return {(elements[i], elements[j])
            for i in range(size) for j in range(size) if closure[i][j]}


def connected_components(adjacency):
    """The components, as a sorted list of sorted node lists."""
    seen = set()
    components = []
    for start in sorted(adjacency):
        if start in seen:
            continue
        seen.add(start)
        stack = [start]
        component = []
        while stack:
            node = stack.pop()
            component.append(node)
            for neighbour in adjacency.get(node, ()):
                if neighbour not in seen:
                    seen.add(neighbour)
                    stack.append(neighbour)
        components.append(sorted(component))
    return sorted(components)


def two_colouring(adjacency):
    """A dict node -> 0/1 with no monochromatic edge, or None."""
    colours = {}
    for start in sorted(adjacency):
        if start in colours:
            continue
        colours[start] = 0
        queue = [start]
        while queue:
            node = queue.pop(0)
            for neighbour in adjacency.get(node, ()):
                if neighbour not in colours:
                    colours[neighbour] = 1 - colours[node]
                    queue.append(neighbour)
                elif colours[neighbour] == colours[node]:
                    return None
    return colours
'''},
            {"name": "main.py", "content": r'''
from toolkit import (bell, classify, connected_components, crt, derangements,
                     entails, euler_phi, models, sieve, stirling_second,
                     transitive_closure, two_colouring)

print("modus ponens :", entails(["P", "P -> Q"], "Q"))
print("consequent   :", entails(["P -> Q", "Q"], "P"))
print("P | ~P       :", classify("P | ~P"))
print("models P & Q :", models("P & Q"))

print("S(4, k)      :", [stirling_second(4, k) for k in range(5)])
print("Bell 0..6    :", [bell(n) for n in range(7)])
print("derangements :", [derangements(n) for n in range(7)])

print("primes <= 30 :", sieve(30))
print("phi(36)      :", euler_phi(36))
print("crt          :", crt([2, 3, 2], [3, 5, 7]))

friends = {"a": ["b"], "b": ["a"], "c": ["d"], "d": ["c"]}
print("components   :", connected_components(friends))
print("colouring    :", two_colouring(friends))
print("closure      :", sorted(transitive_closure(["a", "b", "c"], {("a", "b"), ("b", "c")})))
'''},
        ],
        "tests": [
            {"name": "models enumerates the satisfying assignments", "code": r'''
from toolkit import models
assert models("P & Q") == [{"P": True, "Q": True}], f"got {models('P & Q')!r}"
assert models("P & ~P") == [], "a contradiction has no models"
_got = models("P | Q")
_want = [{"P": False, "Q": True}, {"P": True, "Q": False}, {"P": True, "Q": True}]
assert _got == _want, f"got {_got!r}, expected {_want!r}"
assert models("~P") == [{"P": False}], f"got {models('~P')!r}"
assert len(models("P -> Q")) == 3, f"P -> Q has 3 models, got {len(models('P -> Q'))}"
'''},
            {"name": "classify over the three cases", "code": r'''
from toolkit import classify
assert classify("P | ~P") == "tautology", f"got {classify('P | ~P')!r}"
assert classify("P & ~P") == "contradiction", f"got {classify('P & ~P')!r}"
assert classify("P -> Q") == "contingency", f"got {classify('P -> Q')!r}"
assert classify("(P -> Q) & (Q -> R) -> (P -> R)") == "tautology", \
    "the transitivity of implication is a tautology"
assert classify("(P & (P -> Q)) & ~Q") == "contradiction", "modus ponens cannot be denied"
'''},
            {"name": "entails decides an argument", "code": r'''
from toolkit import entails
assert entails(["P", "P -> Q"], "Q") is True, "modus ponens is valid"
assert entails(["P -> Q", "~Q"], "~P") is True, "modus tollens is valid"
assert entails(["P -> Q", "Q"], "P") is False, "affirming the consequent is invalid"
assert entails(["P -> Q", "~P"], "~Q") is False, "denying the antecedent is invalid"
assert entails(["P & ~P"], "Q") is True, "anything follows from a contradiction"
assert entails([], "P | ~P") is True, "a tautology needs no premises"
assert entails([], "P") is False, "a bare variable is not valid"
assert entails(["P -> Q", "Q -> R"], "P -> R") is True, "implication chains"
'''},
            {"name": "choose is exact and total", "code": r'''
from toolkit import choose
for _n, _k, _want in [(0, 0, 1), (5, 2, 10), (5, 5, 1), (5, 6, 0), (5, -1, 0),
                      (52, 5, 2598960), (40, 20, 137846528820)]:
    _got = choose(_n, _k)
    assert _got == _want, f"choose({_n}, {_k}) gave {_got!r}, expected {_want}"
for _n in range(0, 12):
    assert sum(choose(_n, _k) for _k in range(_n + 1)) == 2 ** _n, f"row {_n} does not sum to 2^{_n}"
try:
    choose(-1, 0)
    assert False, "a negative n should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Stirling numbers of the second kind", "code": r'''
from toolkit import stirling_second
assert stirling_second(0, 0) == 1, "the empty set has exactly one partition"
for _n in range(1, 8):
    assert stirling_second(_n, 0) == 0, f"S({_n}, 0) should be 0"
    assert stirling_second(_n, 1) == 1, f"S({_n}, 1) should be 1"
    assert stirling_second(_n, _n) == 1, f"S({_n}, {_n}) should be 1"
    assert stirling_second(_n, _n + 1) == 0, f"S({_n}, {_n + 1}) should be 0"
_row5 = [stirling_second(5, _k) for _k in range(1, 6)]
assert _row5 == [1, 15, 25, 10, 1], f"row 5 is {_row5!r}, expected [1, 15, 25, 10, 1]"
assert stirling_second(4, 2) == 7, f"S(4, 2) gave {stirling_second(4, 2)!r}, expected 7"
assert stirling_second(6, 3) == 90, f"S(6, 3) gave {stirling_second(6, 3)!r}, expected 90"
'''},
            {"name": "Bell and derangement numbers", "code": r'''
from toolkit import bell, derangements
_got = [bell(_n) for _n in range(8)]
_want = [1, 1, 2, 5, 15, 52, 203, 877]
assert _got == _want, f"Bell numbers came out as {_got!r}, expected {_want!r}"
_got = [derangements(_n) for _n in range(11)]
_want = [1, 0, 1, 2, 9, 44, 265, 1854, 14833, 133496, 1334961]
assert _got == _want, f"derangements came out as {_got!r}, expected {_want!r}"
'''},
            {"name": "sieve, mod_pow and mod_inverse", "code": r'''
from toolkit import mod_inverse, mod_pow, sieve
assert sieve(1) == [] and sieve(2) == [2], "the small cases must not crash"
assert sieve(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29], f"got {sieve(30)!r}"
assert len(sieve(1000)) == 168, f"there are 168 primes below 1000, got {len(sieve(1000))}"
for _b, _e, _m, _want in [(2, 10, 1000, 24), (3, 0, 7, 1), (5, 3, 1, 0), (65, 17, 3233, 2790)]:
    _got = mod_pow(_b, _e, _m)
    assert _got == _want, f"mod_pow({_b}, {_e}, {_m}) gave {_got!r}, expected {_want}"
assert mod_pow(7, 100000, 1000000007) == pow(7, 100000, 1000000007), \
    "large exponents must agree with the reference"
assert mod_inverse(3, 11) == 4, f"mod_inverse(3, 11) gave {mod_inverse(3, 11)!r}, expected 4"
assert mod_inverse(17, 3120) == 2753, f"got {mod_inverse(17, 3120)!r}, expected 2753"
for _bad in [(6, 9), (3, 1), (2, 4)]:
    try:
        mod_inverse(*_bad)
        assert False, f"mod_inverse{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "euler_phi counts the coprimes", "code": r'''
from toolkit import euler_phi, sieve
for _n, _want in [(1, 1), (2, 1), (9, 6), (10, 4), (36, 12), (97, 96), (100, 40)]:
    _got = euler_phi(_n)
    assert _got == _want, f"euler_phi({_n}) gave {_got!r}, expected {_want}"


def _naive_gcd(a, b):
    while b:
        a, b = b, a % b
    return a


for _n in range(1, 120):
    _brute = sum(1 for _k in range(1, _n + 1) if _naive_gcd(_k, _n) == 1)
    assert euler_phi(_n) == _brute, f"euler_phi({_n}) gave {euler_phi(_n)!r}, expected {_brute}"
for _p in sieve(60):
    assert euler_phi(_p) == _p - 1, f"phi of the prime {_p} should be {_p - 1}"
try:
    euler_phi(0)
    assert False, "euler_phi(0) should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "crt solves and refuses", "code": r'''
from toolkit import crt
_x, _m = crt([2, 3, 2], [3, 5, 7])
assert (_x, _m) == (23, 105), f"crt([2,3,2], [3,5,7]) gave {(_x, _m)!r}, expected (23, 105)"
assert crt([1], [5]) == (1, 5), f"a single congruence gave {crt([1], [5])!r}"
_x, _m = crt([0, 0], [3, 5])
assert (_x, _m) == (0, 15), f"the all-zero system gave {(_x, _m)!r}, expected (0, 15)"
_x, _m = crt([7, 9], [11, 13])
assert _x % 11 == 7 and _x % 13 == 9 and _m == 143, f"crt gave {(_x, _m)!r}"
assert 0 <= _x < _m, "the solution must be reduced into 0..product-1"
for _bad in [([1, 2], [4, 6]), ([1], [1]), ([1, 2], [3]), ([], [])]:
    try:
        crt(*_bad)
        assert False, f"crt{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "transitive_closure and connected_components", "code": r'''
from toolkit import connected_components, transitive_closure
_got = transitive_closure(["a", "b", "c"], {("a", "b"), ("b", "c")})
assert _got == {("a", "b"), ("b", "c"), ("a", "c")}, f"got {sorted(_got)!r}"
assert transitive_closure(["a", "b"], set()) == set(), "the empty relation closes to itself"
assert len(transitive_closure(["a", "b", "c"], {("a", "b"), ("b", "c"), ("c", "a")})) == 9, \
    "a 3-cycle closes to every pair"
assert transitive_closure([], set()) == set(), "an empty ground set gives an empty closure"
_friends = {"a": ["b"], "b": ["a"], "c": ["d"], "d": ["c"], "e": []}
assert connected_components(_friends) == [["a", "b"], ["c", "d"], ["e"]], \
    f"got {connected_components(_friends)!r}"
assert connected_components({}) == [], "the empty graph has no components"
assert connected_components({"x": []}) == [["x"]], "one isolated node is one component"
'''},
            {"name": "two_colouring decides bipartiteness", "code": r'''
from toolkit import two_colouring
_path = {"a": ["b"], "b": ["a", "c"], "c": ["b"]}
assert two_colouring(_path) == {"a": 0, "b": 1, "c": 0}, f"got {two_colouring(_path)!r}"
_square = {"a": ["b", "d"], "b": ["a", "c"], "c": ["b", "d"], "d": ["a", "c"]}
_colours = two_colouring(_square)
assert _colours is not None, "an even cycle is bipartite"
for _node, _neighbours in _square.items():
    for _other in _neighbours:
        assert _colours[_node] != _colours[_other], f"edge {_node}-{_other} is monochromatic"
assert two_colouring({"x": ["y", "z"], "y": ["x", "z"], "z": ["x", "y"]}) is None, \
    "a triangle is an odd cycle"
assert two_colouring({}) == {}, "the empty graph is trivially bipartite"
assert two_colouring({"a": ["a"]}) is None, "a self-loop is an odd cycle"
'''},
            {"name": "toolkit.py is import-clean and shortcut-free", "code": r'''
import re as _re
_src = open("toolkit.py").read()
assert "print(" not in _src, "toolkit.py defines functions; the printing belongs in main.py"
for _banned in ["math.comb", "math.perm", "math.factorial", "math.gcd"]:
    assert _banned not in _src, f"{_banned} defeats the exercise — write the arithmetic yourself"
assert not _re.search(r"(?<![\w.])pow\s*\(", _src), \
    "the built-in three-argument pow is off limits"
'''},
        ],
    },
}
