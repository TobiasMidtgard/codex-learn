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
            "read": {
                "title": "Two readings of the same door rule",
                "minutes": 14,
                "body": r'''
A security team writes one sentence for the door controller on the ground floor:

*the door opens if the badge is valid and it is not after 18:00, or the override switch
is on.*

Two engineers implement it. The first writes `valid & (~late | override)`. The second
writes `valid & ~late | override`. Both of them will tell you they typed the sentence
out. One of the two lets a person with no badge at all flip the override switch and walk
through, and neither engineer can see which from the code, because both readings are
faithful to the English.

## The rows are the meaning

There are three atomic statements here — *the badge is valid*, *it is after 18:00*, *the
override is on* — and each of them is true or false with nothing in between. A statement
of that kind is a **proposition**. Three independent true-or-false choices give
$2 \times 2 \times 2 = 8$ combinations, and a formula built out of the three assigns a
value to each of the eight. So a formula is not really a piece of text. It is a column of
eight truth values, and two formulas mean the same thing exactly when their columns agree
in every row. Nothing weaker will do, and nothing stronger is needed.

That is a claim you can settle by machine rather than by argument:

```python
from itertools import product

def door_a(valid, late, override):
    return valid and ((not late) or override)

def door_b(valid, late, override):
    return (valid and not late) or override

rows = list(product([False, True], repeat=3))
differ = [r for r in rows if door_a(*r) != door_b(*r)]
print(len(rows), "rows,", len(differ), "disagree")
for valid, late, override in differ:
    print("valid", valid, "late", late, "override", override)
```

It prints `8 rows, 2 disagree`, then the two rows: both have an invalid badge and the
override on. On those two rows the second engine opens the door to somebody carrying no
badge, and every other row in the building's history looks identical under the two
programs. A bug that shows up on two rows out of eight is a bug that survives testing.

Precedence is the convention that decides which of the two the unparenthesised text
denotes. Tightest first: `~`, then `&`, then `|`, then `->`. So `valid & ~late | override`
groups as `(valid & ~late) | override` — the second reading, the one that opens the door.
The engine you are about to build has one parsing function per precedence level for
exactly this reason, and the levels are what make the grouping a fact about the notation
rather than a matter of taste.

## The connectives, read off the door

`~late` is true precisely when `late` is false. `A & B` is true only when both are.
`A | B` is **inclusive**: true when either holds and true when both do. English disjunction
is often exclusive — *tea or coffee* offers you one — and that is the first place a
translation from a specification quietly changes meaning. The door rule wants the
inclusive one: a valid badge before 18:00 with the override also on should still open the
door.

## The connective nobody believes at first

Now the fourth. A manufacturer prints on the box: *if the part fails within a year, we
replace it.* Rather than asking when the promise is true, ask when it is **broken**, which
is a question anybody can answer without any logic at all. There is one way, and only one:
the part failed and no replacement came. If the part never failed, the company has not broken its word —
whether or not it posted you a spare part anyway.

So the column for the promise has a single false entry, in the row where the first
statement is true and the second is false. That column is `P -> Q`, and it was not
announced; it is what "the promise was not broken" comes to. The same reading hands over
the equivalence for free: the promise stands when either the part did not fail, `~P`, or a
replacement arrived, `Q`. That is `~P | Q`, the same column by construction.

A warranty on a part that never fails is a promise kept at no cost. Statements true for
that reason are called *vacuously* true, and Module 2 shows the same effect at scale, when
a universal claim ranges over a domain with nothing in it.

## One table, carried all the way through

```python
from itertools import product

def implies(a, b):
    """The one false row: a true antecedent with a false consequent."""
    return not (a and not b)

print("P Q | P->Q  ~P|Q  ~Q->~P  Q->P")
for p, q in product([False, True], repeat=2):
    cells = [implies(p, q), (not p) or q, implies(not q, not p), implies(q, p)]
    print(int(p), int(q), " |", "     ".join(str(int(c)) for c in cells))
```

The header line, then four rows. Reading down, the first three columns are `1 1 0 1` —
identical, all four rows. The fourth column is `1 0 1 1`, and it parts from the others in
two rows: the row where `P` is false and `Q` is true, and the row where `P` is true and
`Q` is false. Those are the two rows on which `P` and `Q` disagree, which is the whole
content of the difference.

Put a sentence to it. *If it rains, the ground is wet.* Its contrapositive is *if the
ground is not wet, it is not raining*, and the table says that is the same claim — one
column, two English sentences. Its converse is *if the ground is wet, it is raining*, and
that is a different claim, refuted by a burst pipe: rain false, wet ground true, which is
precisely the row where the columns separate.

## The mistake, and why it is tempting

The mistake is reasoning from `P -> Q` and `Q` to `P` — affirming the consequent. It is
tempting because English conditionals are usually offered by a speaker who believes the
converse as well. *If you finish your dinner you can have pudding* is heard by every child
as a promise of no pudding otherwise, and the child is reading the speaker correctly while
reading the logic wrongly. Material implication carries no hint of *only if*; the arrow
says one thing about one row and is silent about the rest.

The course's capstone toolkit makes the distinction executable: `entails(["P", "P -> Q"],
"Q")` returns `True`, which is modus ponens, and `entails(["P -> Q", "Q"], "P")` returns
`False`, which is the fallacy that resembles it. The two differ by which of the two
premises is the arrow's own antecedent.

## De Morgan, without memorising it

Ask the auditor's question about the door: when does the rule *fail* to open it? Negate
`A & B` and think about what has to happen — at least one of the two conjuncts has to
fail, so the negation is `~A | ~B`. Negate `A | B` and both have to fail, so it is
`~A & ~B`. A negation crossing a connective flips the connective and lands on both sides.
Contraposition falls out of the same habit applied to `~P | Q`.

## Where the tables stop

Three limits, and each of them matters later.

The arrow is **truth-functional** and nothing more. *If 2 + 2 = 5 then the moon is cheese*
comes out true, because a false antecedent is enough on its own. Nothing in the column
tracks relevance or causation, so a conditional that means *because* is only partly
captured by this notation.

The atoms are opaque. *Every prime above 2 is odd* is a single letter here, and no
manipulation of the letters can reach inside it. Getting at the internal structure of a
statement is what Module 2's quantifiers are for.

And the table has $2^n$ rows. Ten variables give 1024, thirty give 1073741824, and a
formula with a few hundred variables is ordinary in industrial use. Walking every row is
therefore a method that works at the scale of this module and at no other; deciding
satisfiability faster than that in the worst case is the open problem behind SAT solving,
and Module 12 supplies the notation for stating what "faster" would even mean.

## What you are about to build

The lab, **A propositional logic engine**, is those columns turned into code:
`tokenise` splits the text, `parse` builds a nested-tuple tree with one function per
precedence level, `evaluate` walks it under an assignment, and `truth_table` enumerates
the $2^n$ assignments in binary-counting order with `False` first. `classify` then reads
the column — all true is a tautology, none true a contradiction, anything else a
contingency — and `equivalent` compares two columns over the **union** of the two
formulas' variables, which is why `equivalent("P", "P | (Q & ~Q)")` comes out `True`
rather than raising over a name one side has never heard of.

One detail of the grammar is worth meeting before you implement it. Implication associates
to the right, so `P -> Q -> R` is `P -> (Q -> R)`, and that is not a formality:

```python
from itertools import product

def implies(a, b):
    return not (a and not b)

for p, q, r in product([False, True], repeat=3):
    right = implies(p, implies(q, r))
    left = implies(implies(p, q), r)
    if right != left:
        print("P", p, "Q", q, "R", r, "right", right, "left", left)
```

Two rows print, and both have `P` false and `R` false. Group the arrows the other way and
the engine answers a different question on a quarter of its inputs.
''',
            },
            "quiz": {
                "title": "Columns, arrows and what a table decides",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Written without parentheses, `valid & ~late | override` is read by the engine as which grouping, and what does that cost?",
                        "opts": [
                            "`valid & (~late | override)`, since `|` is evaluated before `&`",
                            "`(valid & ~late) | override`, which opens the door on override alone",
                            "It is ambiguous, so the engine must reject it as malformed input",
                            "`(valid & ~late) | override`, which agrees with the other grouping on every row",
                        ],
                        "a": 1,
                        "whys": [
                            "This inverts the precedence. `&` binds tighter than `|`, the same way multiplication binds tighter than addition, so the conjunction is gathered first and the disjunction sees it as one operand.",
                            "`&` binds tighter, so the override is disjoined with the whole conjunction and can carry the formula on its own.",
                            "Precedence exists so that unparenthesised text has exactly one reading. The grammar is ambiguous only until the levels are fixed, and a parser with one function per level never has a choice to make.",
                            "The grouping is right and the consequence is not. The two readings disagree on two of the eight rows — the rows with an invalid badge and the override on — which is exactly the defect that matters.",
                        ],
                        "why": r'''
Precedence runs `~`, then `&`, then `|`, then `->`, so the conjunction is built first and
the override is disjoined with the whole of it. Under that reading the override alone
makes the formula true, badge or no badge. Enumerating all eight rows shows the two
readings differing on two of them, both with an invalid badge and the override on — a
disagreement narrow enough to survive casual testing and wide enough to open a door to
somebody with no badge.
''',
                    },
                    {
                        "q": "A warranty says: *if the part fails within a year, we replace it.* The part did not fail. What is the truth value of the warranty statement, and why?",
                        "opts": [
                            "False, because no replacement was ever sent",
                            "True, because the one way to break the promise did not occur",
                            "Undefined, since the antecedent never happened",
                            "True, but only if the manufacturer sent a replacement anyway",
                        ],
                        "a": 1,
                        "whys": [
                            "This reads the arrow as if it also promised a replacement. The promise was conditional on a failure, so an absent replacement after an absent failure breaks nothing.",
                            "The promise is broken only by a failure with no replacement, and no failure occurred.",
                            "A propositional formula has a truth value on every row of its table, with no gaps. There is no third value here, and an undefined entry would leave the column incomplete.",
                            "Sending a spare part to somebody whose part did not fail is generous and irrelevant. The row with a false antecedent is true under either value of the consequent, which is what makes the column the shape it is.",
                        ],
                        "why": r'''
Ask when the promise is broken rather than when it holds, and there is one answer: the
part failed and no replacement came. Every other combination leaves the manufacturer's
word intact, so the arrow's column carries a single false entry. A conditional whose
antecedent never occurs is *vacuously* true — a promise kept at no cost — and the same
effect returns in Module 2, where a universal claim over an empty domain comes out true
for the same reason.
''',
                    },
                    {
                        "q": "*If it rains, the ground is wet.* Which sentence has the identical truth column, and which one differs?",
                        "opts": [
                            "*If the ground is wet, it is raining* is identical; *if the ground is not wet, it is not raining* differs",
                            "Both of those sentences are identical to the original, since each reverses it",
                            "*If the ground is not wet, it is not raining* is identical; *if the ground is wet, it is raining* differs",
                            "Neither is identical, because negating a statement always changes its column",
                        ],
                        "a": 2,
                        "whys": [
                            "This has the pair the wrong way round. The converse is the one refuted by a burst pipe: wet ground, no rain, which the original never ruled out.",
                            "Only one of the two is a reversal. The contrapositive reverses *and* negates both parts, and those two changes cancel, which is why it survives where the plain reversal does not.",
                            "Reverse and negate both parts and the column is unchanged; reverse alone and it changes in two rows.",
                            "Negating both parts *and* reversing them leaves the column untouched, which is precisely the contrapositive. A burst pipe refutes the converse and leaves the original standing.",
                        ],
                        "why": r'''
Lay the columns side by side. `P -> Q`, `~P | Q` and `~Q -> ~P` agree in all four rows;
`Q -> P` parts from them in the two rows where `P` and `Q` disagree. The concrete
refutation of the converse is a burst pipe: the ground is wet with no rain, which is the
row where the columns separate, and the original claim says nothing about it. The
contrapositive reverses the arrow and negates both ends, and those two moves cancel.
''',
                    },
                    {
                        "q": "`equivalent(\"P\", \"P | (Q & ~Q)\")` is `True`. What does the engine have to do for that answer to come out?",
                        "opts": [
                            "Detect that `Q & ~Q` is a contradiction and delete it before comparing",
                            "Compare the two columns over the union of the variables, four rows rather than two",
                            "Refuse the comparison, since the two formulas do not use the same variables",
                            "Compare only the variables that both formulas actually mention, which here is `P` on its own",
                        ],
                        "a": 1,
                        "whys": [
                            "Simplification is one route to the answer and not the one the engine takes. It never rewrites a formula; it evaluates both over the same assignments and compares the results, which needs no algebra at all.",
                            "Two formulas are equivalent when they agree on every assignment to every variable either one mentions.",
                            "Different variable sets are ordinary. Take the union, evaluate both sides on each of its assignments, and the comparison is well defined — which is what makes this pair equivalent rather than incomparable.",
                            "Restricting to the shared variables leaves `Q` with no value, so the second formula cannot be evaluated at all. The fix runs the other way: widen to the union so both sides are defined everywhere.",
                        ],
                        "why": r'''
Equivalence is agreement on every row, so the row set has to be big enough for both
formulas to be evaluated. Taking the union of the variables gives `P` and `Q`, hence four
rows; on each of them `Q & ~Q` is false, a false disjunct changes nothing, and the two
columns match. Comparing over the intersection instead would leave `Q` unbound and the
second formula unevaluatable, which is why the lab's `equivalent` is specified over the
union.
''',
                    },
                    {
                        "q": "Why does the truth-table method stop being a practical decision procedure as formulas grow?",
                        "opts": [
                            "Because the row count is $2^n$, so thirty variables already give over a billion rows",
                            "Because tables cannot represent implication, only conjunction and disjunction",
                            "Because a formula with many variables usually turns out to be a contingency",
                            "Because floating-point rounding creeps into the truth values once a table runs to thousands of rows",
                        ],
                        "a": 0,
                        "whys": [
                            "One independent binary choice per variable, multiplied together.",
                            "Implication is a column like any other, fully determined by the values of its two parts. Its presence changes the cost of a table not at all; the number of variables is the only thing that does.",
                            "Being a contingency is a property of the answer, not a difficulty in computing it, and the walk costs the same whichever of the three classifications comes back. Plenty of large formulas are tautologies.",
                            "Nothing here is floating point. Every cell is a boolean and the arithmetic is exact at any size — what defeats the method is how many cells there are, not what happens inside one.",
                        ],
                        "why": r'''
Each variable is one independent true-or-false choice, so the product rule gives $2^n$
rows: 8 at three variables, 1024 at ten, 1073741824 at thirty. Industrial formulas carry
hundreds. The walk stays exact and stays correct at every size — what fails is the time,
and that is the whole difficulty. Deciding satisfiability faster than the exhaustive walk
in the worst case is the open problem behind SAT solving, and Module 12 gives you the
notation for saying what "faster" claims.
''',
                    },
                    {
                        "q": "`P -> Q -> R` associates to the right. How much does the grouping actually change?",
                        "opts": [
                            "Nothing, since implication is associative in the way conjunction is",
                            "Everything: the two groupings agree on no row of the eight",
                            "The two groupings disagree on two of the eight rows, both with `P` and `R` false",
                            "Only the notation, because the parser rewrites either grouping into the same `~P | Q | R`",
                        ],
                        "a": 2,
                        "whys": [
                            "Conjunction and disjunction are associative and implication is not, which is why the grammar has to make a choice. Testing the two groupings on all eight rows settles it in a few lines.",
                            "They agree on six of the eight rows, and that near-agreement is what makes the difference easy to miss. A formula that failed everywhere would be caught by the first test anyone wrote.",
                            "Enumerate the eight rows and two of them come out differently, both with a false `P` and a false `R`.",
                            "No rewriting takes place, and `~P | Q | R` is a third formula again — it is true whenever `Q` is true, which the right grouping is as well but the left grouping is not.",
                        ],
                        "why": r'''
`P -> (Q -> R)` is false only when `P` and `Q` are true and `R` is false. `(P -> Q) -> R`
is false whenever `P -> Q` holds and `R` does not, which happens in three rows. The two
columns therefore differ in two rows, both with `P` false and `R` false. Six rows of
agreement is what makes the choice easy to overlook, and why the grammar has to fix the
association rather than leave it to whoever wrote the parser.
''',
                    },
                ],
            },
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
                "`forall x P(x)` is a conjunction over the domain and `exists x P(x)` a disjunction over it — so on an empty domain the first is true and the second false, which is not a convention but what the count of predicates returns at `n = 0`",
                "Quantifier order changes the claim: `forall x exists y` lets `y` depend on `x`, while `exists y forall x` promises one `y` that works for every `x`",
                "The second implies the first and not the reverse, and the gap has a size: over a domain of `n` elements it is `2(2^n - 1)^n - 2^(n^2)` relations, which is 0 at `n = 1` — so a single example can never expose the difference — and 174 at `n = 3`",
                "Negation moves inward and flips: `~forall x P(x)` is `exists x ~P(x)`, and `~exists x P(x)` is `forall x ~P(x)`",
                "A variable is bound by the quantifier that captures it and free otherwise; a formula with a free variable is a predicate, not a proposition",
            ],
            "read": {
                "title": "What a quantifier is quantifying over",
                "minutes": 14,
                "body": r"""
A checkout system enforces one rule: *every item in the basket is in stock*. Somebody
reports a bug. There are exactly two shapes the bug can have, and telling them apart is
the whole of this module.

Either the rule is being applied when it should not be — the basket is empty and the
system still refuses — or the rule is being read as a different rule. A colleague
rewrites the check as *there is a stock level that covers every item*, which sounds like
the same sentence read aloud and is not the same claim at all. Module 1 gave you
connectives that combine whole statements. Neither of these bugs is expressible with
them, because both are about a statement with a hole in it, applied across a collection.

## A predicate is a subset, and that settles the empty case

Fix a domain $D$ with $n$ elements. A predicate $P$ on that domain is a rule that is
true of some elements and false of the others, so it is fixed by naming the elements it
holds of: $P$ *is* a subset of $D$. Module 4 will make that identification official; here
it is a counting device, and it earns its place immediately.

How many predicates are there on a domain of size $n$? One in-or-out decision per
element, so $2^n$. Of those, how many make $\forall x\, P(x)$ true? Exactly one — the
predicate that holds of everything. How many make $\exists x\, P(x)$ true? All of them
except the predicate that holds of nothing, so $2^n - 1$.

Now put $n = 0$. There is $2^0 = 1$ predicate on the empty domain. The count says
$\forall$ is true for $1$ of them, which is all of them, and $\exists$ is true for
$2^0 - 1 = 0$ of them, which is none. So on an empty domain every universal statement
is true and every existential one is false.

That result is usually presented as a convention adopted for tidiness, and it is not one.
It is what the count returns, and the count was not arranged to produce it. The
practical version: "every student who failed will resit" is true in a year when nobody
failed, and a program that loops over an empty list and reports success has not
malfunctioned. Statements true for this reason are called *vacuously* true, and the
first bug above is somebody arguing with one.

## Negation, derived once

Read `forall x P(x)` as a conjunction with one conjunct per element of the domain and
`exists x P(x)` as a disjunction. Then De Morgan from Module 1 does all the work:
negating a conjunction gives the disjunction of the negations, so `~forall x P(x)` is
`exists x ~P(x)`, and `~exists x P(x)` is `forall x ~P(x)`. Negation moves inward one
quantifier at a time and flips each as it passes. Nothing here is new; it is Module 1's
law applied to a conjunction that happens to be long.

Work one all the way through. Negate *every prime is odd*, which is
`forall x (prime(x) -> odd(x))`. The quantifier flips, giving
`exists x ~(prime(x) -> odd(x))`. Then `P -> Q` is `~P | Q`, whose negation is `P & ~Q`,
so the whole thing is `exists x (prime(x) & ~odd(x))` — some number is prime and not odd.
Refuting the claim therefore means handing over one number, and the number is 2. The slip
to avoid is negating the body but leaving it an implication: `exists x (prime(x) ->
~odd(x))` is a strictly weaker statement, satisfied by any `x` that merely fails to be
prime, and 9 satisfies it while refuting nothing.

## The order of two quantifiers, counted

Now the second bug, which is the one that survives code review. Over a domain of size
$n$, a binary relation $R$ is a choice of true or false for each of the $n^2$ ordered
pairs, so there are $2^{n^2}$ of them. Draw one as an $n \times n$ grid of noughts and
crosses, row $x$, column $y$.

$\forall x\,\exists y\,R(x,y)$ says every row contains at least one cross. A row is any
of the $2^n$ patterns except the all-noughts one, and the rows are chosen independently,
so the count is

$$(2^n - 1)^n$$

$\exists y\,\forall x\,R(x,y)$ says some column is entirely crosses. Count the complement
instead: each column may be any pattern except all-crosses, independently, which is
$(2^n - 1)^n$ again, so the count is

$$2^{n^2} - (2^n - 1)^n$$

Take $n = 2$. There are 16 relations. The first count is $3^2 = 9$, the second
$16 - 9 = 7$. Seven is smaller than nine, which it must be: a column of crosses gives
every row a cross, so every relation of the second kind is one of the first kind. The
two relations that separate them are the difference, $9 - 7 = 2$, and they are worth
looking at:

$$\begin{matrix} \cdot & \times \\ \times & \cdot \end{matrix}
\qquad\text{and}\qquad
\begin{matrix} \times & \cdot \\ \cdot & \times \end{matrix}$$

The second is *everyone is related to themselves*. Every $x$ has a $y$ — its own self —
and no single $y$ serves both. The first is *everyone is related to the other one*, with
the same property. In both, the $y$ exists but depends on the $x$, which is precisely
what the outer $\forall$ permits and the outer $\exists$ forbids.

Two more values are worth having. At $n = 1$ the gap is $2 \cdot 1 - 2 = 0$: over a
one-element domain the two orders agree, which is why a single example never exposes the
difference. At $n = 3$ the gap is $2 \cdot 7^3 - 2^9 = 174$, so it is not a rare edge
case that a large domain smooths over; it grows.

One trap in that arithmetic. The two counts add to $9 + 7 = 16$, the total, which invites
the reading that the two kinds of relation are opposites. They are not — one is contained
in the other. The sum is exact because *every row has a cross* and *no column is all
crosses* are counted by the same expression, and they are counted by the same expression
because swapping rows for columns and crosses for noughts is a bijection between them.
Equal counts, not complementary sets.

## The mistake, and why it is tempting

English puts the quantifiers in whichever order sounds better and leaves the dependence
to context. *Everybody loves somebody* and *somebody is loved by everybody* differ by one
word of word order and by an enormous amount of content. The same pair in a specification:
*every request has a handler* is what you want, and *there is a handler for every request*
is what gets built, and the second is a claim about one handler. The rule that fixes it is
short: an inner variable may depend on an outer one, never the reverse. Two quantifiers of
the same kind commute freely; mixed ones almost never do.

The other half of the discipline is the domain. A quantified formula has no truth value
until the domain is named, and $\forall x\,(x > 3)$ is true over the integers above 5 and
false over the integers. A formula whose variables are all bound, with a domain fixed, is
a proposition. Leave one free and it is a predicate — a question waiting for an argument.

## Where the counting stops

Every number above needed the domain to be finite. Over the integers there is no count of
relations to take, and yet $\forall x\,\exists y\,(y > x)$ is plainly true and
$\exists y\,\forall x\,(y > x)$ plainly false — the second asks for an integer exceeding
every integer, itself included. Those are settled by the successor function and by the
absence of a largest integer, not by any tally. So the grids above are a device for seeing
what the quantifiers claim, and not a method for deciding whether a claim holds. What
"how many" can still mean once the domain is infinite is Module 13's subject, and the
answer is not obtained by counting either.

```python
from itertools import product

def counts(n):
    fa_ex = ex_fa = 0
    for bits in product([0, 1], repeat=n * n):
        M = [bits[i * n:(i + 1) * n] for i in range(n)]
        fa_ex += all(any(row) for row in M)
        ex_fa += any(all(M[x][y] for x in range(n)) for y in range(n))
    return fa_ex, ex_fa

for n in (1, 2, 3):
    a, b = counts(n)
    print(n, a, b, a - b, (2 ** n - 1) ** n, 2 ** (n * n) - (2 ** n - 1) ** n)
```

It prints `1 1 1 0 1 1`, then `2 9 7 2 9 7`, then `3 343 169 174 343 169`: the brute-force
tally and the two formulas agree, and the fourth column is the gap.
""",
            },
            "derive": {
                "title": "Counting the models, and pricing the order of two quantifiers",
                "minutes": 12,
                "brief": r"""
The quantifiers are usually distinguished by example. Here they are distinguished by
counting, over a domain of $n$ elements, exactly how many predicates and how many
relations make each statement true — which turns the vacuous-truth convention and the
$\forall\exists$ / $\exists\forall$ asymmetry into arithmetic.

A predicate on the domain is a subset of it; a binary relation is an $n \times n$ grid of
truth values, row $x$ and column $y$.
""",
                "vars": ["n"],
                "steps": [
                    {
                        "prompt": r"A predicate is fixed by which elements it holds of, so it is one in-or-out decision per element of the domain. How many predicates are there on a domain of size $n$?",
                        "answer": r"2^{n}",
                        "placeholder": "2^{?}",
                        "hint": r"The same product rule that gave the power set its size: two choices, made $n$ times, independently.",
                        "deconstruct": [
                            "Each element is either one the predicate holds of, or one it does not.",
                            "The decisions do not constrain one another.",
                        ],
                    },
                    {
                        "prompt": r"Exactly one of those predicates makes $\forall x\, P(x)$ true. How many make $\exists x\, P(x)$ true?",
                        "answer": r"2^{n} - 1",
                        "placeholder": "?",
                        "hint": r"Every predicate witnesses $\exists$ except one. Which one fails?",
                        "deconstruct": [
                            r"$\exists x\, P(x)$ fails only when $P$ holds of nothing.",
                            "There is exactly one such predicate on any domain.",
                        ],
                    },
                    {
                        "prompt": r"Put $n = 0$ into that expression. How many predicates on the empty domain make $\exists x\, P(x)$ true? The answer is a number, and it is the whole justification for vacuous truth.",
                        "answer": r"0",
                        "placeholder": "?",
                        "hint": r"$2^0 = 1$, and the formula subtracts one from it.",
                        "deconstruct": [
                            "There is exactly one predicate on the empty domain, and it holds of nothing.",
                            r"So $\forall$ is true for all $1$ of them and $\exists$ for none.",
                        ],
                    },
                    {
                        "prompt": r"Now relations. Read $R$ as an $n \times n$ grid. $\forall x\,\exists y\,R(x,y)$ says every row has at least one true entry. Each row is any of the $2^{n}$ patterns except the empty one, and the rows are independent. How many such relations are there?",
                        "answer": r"(2^{n} - 1)^{n}",
                        "placeholder": "(?)^{n}",
                        "hint": "Count the legal patterns for one row, then raise that to the number of rows.",
                        "deconstruct": [
                            r"A row is a subset of the domain: $2^{n}$ possibilities.",
                            "Exactly one of them — the all-false row — is forbidden.",
                            "There are $n$ rows and no constraint between them.",
                        ],
                    },
                    {
                        "prompt": r"$\exists y\,\forall x\,R(x,y)$ says some column is true throughout. Count the complement — no column is full — the same way, and subtract it from the $2^{n^{2}}$ relations. Write the count.",
                        "answer": r"2^{n^{2}} - (2^{n} - 1)^{n}",
                        "placeholder": "? - ?",
                        "hint": r"A column may be any pattern except the all-true one, independently of the others, which is $(2^{n}-1)^{n}$ again.",
                        "deconstruct": [
                            r"The grid has $n^{2}$ cells, so there are $2^{n^{2}}$ relations in all.",
                            "Columns are independent of one another, exactly as rows were.",
                            "Subtract the ones with no full column from the total.",
                        ],
                    },
                    {
                        "prompt": r"A full column gives every row a true entry, so the second set sits inside the first. Subtract the second count from the first to price the difference between the two orders.",
                        "answer": r"2(2^{n} - 1)^{n} - 2^{n^{2}}",
                        "placeholder": "?",
                        "hint": r"Subtracting $2^{n^{2}} - (2^{n}-1)^{n}$ from $(2^{n}-1)^{n}$ leaves two copies of the second term.",
                        "deconstruct": [
                            r"$(2^{n}-1)^{n} - \left(2^{n^{2}} - (2^{n}-1)^{n}\right)$.",
                            "Collect the two like terms.",
                        ],
                    },
                ],
                "closing": r"""
At $n = 1$ that difference is $2 \cdot 1 - 2 = 0$: over a one-element domain the two
orders agree, which is why one example never shows the asymmetry. At $n = 2$ it is
$2 \cdot 9 - 16 = 2$, and the two relations it counts are *everyone is related to
themselves* and *everyone is related to the other one* — in each, the $y$ exists but
depends on the $x$. At $n = 3$ it is $2 \cdot 343 - 512 = 174$. The gap does not close.
""",
            },
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
                "One counterexample refutes a universal claim outright, while any number of confirming examples proves none — though one witness does settle an existential; this is Module 2's negation law cashed in, since `~forall x P(x)` *is* `exists x ~P(x)`",
                "A proof by contradiction of an existence claim establishes that an object exists and produces none — the guarantee and the object are different things, and Module 13 proves an undecidable problem exists without exhibiting one",
                "The `sqrt(2)` argument works because 2 is prime, not because of anything about roots: run it on `sqrt(4)` and the step *`a^2` divisible by 4 implies `a` divisible by 4* is false at `a = 2`, so the descent stalls and no contradiction arrives",
            ],
            "read": {
                "title": "Choosing the technique by what it hands you to work with",
                "minutes": 14,
                "body": r"""
Here is a claim almost everybody believes and almost nobody can defend on the spot: *if
$n^2$ is even then $n$ is even*. Try it directly. You are handed "$n^2$ is even", which
means $n^2 = 2m$ for some integer $m$, and you want a statement about $n$. The only route
from $n^2$ to $n$ is a square root, and $n = \sqrt{2m}$ is not an integer fact you can
compute with. The proof is not hard. The *direct* proof is hard, and that is a different
thing.

This module is about picking the technique by what it gives you to hold on to. Each one
starts you somewhere different, and the whole skill is noticing which starting point has
algebra attached.

## Contraposition: swap the ends

Module 1 established that `P -> Q` and `~Q -> ~P` are the same formula — identical
columns in the truth table, not merely similar. So proving one *is* proving the other,
and you are free to start from whichever end is more generous.

Start from "$n$ is odd". That hands you $n = 2k + 1$ for some integer $k$, which is
algebra. Square it:

$$n^2 = (2k+1)^2 = 4k^2 + 4k + 1 = 2(2k^2 + 2k) + 1$$

The right-hand side is two times an integer, plus one, so $n^2$ is odd. That establishes
`~Q -> ~P`, and the original claim comes with it. Three lines, and the only thing that
made it work was choosing the end that came with a formula.

The mistake waiting here is proving the *converse* instead. "If $n$ is even then $n^2$ is
even" is also true, also easy, and says nothing whatever about the claim you were asked
about. It is tempting precisely because it starts from the same place the contrapositive
does. The difference is where it ends: the contrapositive concludes `~P`, the converse
concludes `Q`. Check which one you finished at.

## Contradiction: assume the one thing the claim forbids

To contradict `P -> Q` you assume `P & ~Q` — the hypothesis holding while the conclusion
fails, which is the single situation the implication rules out — and drive at any
absurdity at all. Since that assumption was the only unjustified thing in the room, it is
what must go.

There is a test worth applying to your own proof afterwards. If the argument never
actually used `P`, you did not write a proof by contradiction; you wrote a
contraposition and wrapped it in one. That is not a mistake, but it is longer than it
needs to be, and a great many textbook "contradictions" are this.

## $\sqrt{2}$, all the way through, and then the same argument on $\sqrt{4}$

Suppose $\sqrt{2} = a/b$ with $a$ and $b$ integers sharing no common factor. Then
$a^2 = 2b^2$, so $a^2$ is even, so by the result above $a$ is even. Write $a = 2c$:

$$4c^2 = 2b^2 \qquad \text{hence} \qquad b^2 = 2c^2$$

By the same result $b$ is even too. But $a$ and $b$ shared no common factor and both are
divisible by 2, which is the absurdity. So no such $a$ and $b$ exist.

Now run the identical argument on $\sqrt{4}$, which is 2 and is certainly rational. It
must fail somewhere, and finding where is worth more than the original proof. Suppose
$\sqrt{4} = a/b$ in lowest terms. Then $a^2 = 4b^2$, so $a^2$ is divisible by 4, so —
here it is — you would like to conclude that $a$ is divisible by 4, and that is false.
Take $a = 2$: $a^2 = 4$ is divisible by 4 and $a$ is not. The most you get is that $a$ is
even, and putting $a = 2c$ gives $4c^2 = 4b^2$, so $b^2 = c^2$ and $b = c$. No new
divisor, no descent, no contradiction — and correctly so.

The step that carried the $\sqrt{2}$ proof was "$a^2$ even implies $a$ even", and what
makes it true is that 2 is *prime*. The argument is not about square roots. It is about
primality, which is why the same three lines settle $\sqrt{3}$ and $\sqrt{5}$ and stall
on every perfect square. A proof you cannot break on purpose is a proof you have not
finished reading.

## Cases: cover the domain, and check you did

Proof by cases splits the domain and argues each piece. Overlapping cases are harmless; a
missing case is fatal. Take *$n^2 + n$ is even for every integer $n$*. Two cases:

- $n = 2k$: then $n^2 + n = 4k^2 + 2k = 2(2k^2 + k)$, even.
- $n = 2k + 1$: then $n^2 + n = 4k^2 + 6k + 2 = 2(2k^2 + 3k + 1)$, even.

Every integer is one or the other, so the claim holds. That small fact has a use. Euler's
polynomial $n^2 + n + 41$ is *always odd*, because $n^2 + n$ is always even — which is
part of why it manages to be prime so persistently.

## One object, and what it can settle

A universal claim is refuted by one counterexample and proved by none. An existential
claim is proved by one witness and refuted by none. That asymmetry is the whole of it,
and Euler's polynomial is where it bites hardest.

It is also not a separate rule to memorise — it is Module 2's negation law, cashed in. A
universal claim is `forall x P(x)`, and its negation is `exists x ~P(x)`, which is an
existential. Refuting a universal therefore *means* proving an existential, and an
existential is proved by producing a witness. Read the other way, the same law says
refuting an existential means proving a universal, which is why no single object can do
it: `~exists x P(x)` is `forall x ~P(x)`, and one object is not every object. The two
sentences at the top of this section are one law seen from each end, and if you ever
forget which way round they go, negating the quantifier recovers both in a line.

Check $n = 0$ through $n = 39$ and every value is prime — 41, 43, 47, 53, and on up to
1601. Forty consecutive confirmations. At $n = 40$:

$$40^2 + 40 + 41 = 1681 = 41 \times 41$$

which anyone could have predicted without arithmetic, since every term carries a factor
of 41 when $n = 41$ — and in fact it fails one step earlier than that, at 40. Forty
confirmations were forty genuine proofs of forty instances and contributed nothing to the
universal claim, because a universal claim over the integers has infinitely many
instances left after any finite number of checks. "Probably true" is not a status a
theorem can have.

## Where these techniques stop

Contradiction has a cost that is invisible until you need the thing you proved. A
contradiction proof of *there exists an $x$ with $P(x)$* assumes no such $x$ exists,
derives an absurdity, and concludes that one does — **without ever producing one**. You
finish holding a guarantee and nothing to point at. Module 13 does exactly this: it
proves that undecidable problems exist by counting programs against problems, and hands
over no example of one. That is a real proof and a real limitation at the same time, and
the two are worth keeping apart in your head, because a constructive proof of the same
statement would have given you an object to compute with.

The other boundary is cases. Splitting is only sound when the pieces cover the domain,
and the failure is silent: nothing in the argument complains when a case is missing,
because each case you *did* write is correct. The habit that catches it is to name the
domain out loud, then name the union of the cases, and check the two are the same
sentence.
""",
            },
            "derive": {
                "title": "The parity of a square, the descent that proves an irrational, and where it stalls",
                "minutes": 12,
                "brief": r"""
Three proofs from this module, run as algebra rather than described. The first supplies
the lemma; the second spends it on $\sqrt{2}$; the third runs the same argument on
$\sqrt{4}$ and finds the step that quietly fails, which is the step that tells you what
the proof was really about.

Take $k$ to be an arbitrary integer throughout, and write $n = 2k + 1$ for an odd number.
""",
                "vars": ["n", "k", "m", "a", "b", "c"],
                "steps": [
                    {
                        "prompt": r"Square the odd number $n = 2k + 1$ and expand. Write the result as a polynomial in $k$.",
                        "answer": r"4k^{2} + 4k + 1",
                        "placeholder": "?",
                        "hint": r"$(2k+1)^2 = (2k)^2 + 2 \cdot 2k \cdot 1 + 1$.",
                        "deconstruct": [
                            "Multiply the bracket by itself term by term.",
                            "The two cross terms are equal, so they add rather than cancel.",
                        ],
                    },
                    {
                        "prompt": r"An odd number is one of the form $2m + 1$. Read your expansion in that form: what is $m$, in terms of $k$?",
                        "answer": r"2k^{2} + 2k",
                        "placeholder": "?",
                        "hint": r"Take the constant $1$ aside and halve everything that is left.",
                        "deconstruct": [
                            r"$4k^{2} + 4k + 1 = (4k^{2} + 4k) + 1$.",
                            "Both remaining terms are divisible by 2.",
                            r"This proves the contrapositive: $n$ odd forces $n^2$ odd, so $n^2$ even forces $n$ even.",
                        ],
                    },
                    {
                        "prompt": r"Now $\sqrt{2}$. Suppose $\sqrt{2} = a/b$ in lowest terms, so $a^{2} = 2b^{2}$. Then $a^{2}$ is even, so $a$ is even; put $a = 2c$ and solve for $b^{2}$.",
                        "answer": r"2c^{2}",
                        "placeholder": "?",
                        "hint": r"Substituting gives $4c^{2} = 2b^{2}$. Divide by 2.",
                        "deconstruct": [
                            r"$(2c)^{2} = 4c^{2}$.",
                            r"Set that equal to $2b^{2}$ and divide both sides by 2.",
                            r"The result makes $b^{2}$ even, so $b$ is even — and $a$ and $b$ were in lowest terms.",
                        ],
                    },
                    {
                        "prompt": r"Run the identical argument on $\sqrt{4}$, which is rational, so it must fail somewhere. From $a^{2} = 4b^{2}$ the number $a$ is again even; put $a = 2c$ and solve for $b^{2}$.",
                        "answer": r"c^{2}",
                        "placeholder": "?",
                        "hint": r"Now the substitution gives $4c^{2} = 4b^{2}$, and the 4 cancels rather than halving.",
                        "deconstruct": [
                            r"Substitute $a = 2c$ into $a^{2} = 4b^{2}$.",
                            "Both sides carry a factor of 4.",
                            r"So $b = c$: no new factor of 2 appears and the descent has nothing to descend on.",
                        ],
                    },
                    {
                        "prompt": r"Proof by cases, for *$n^{2} + n$ is even*. First case: put $n = 2k$ and expand $n^{2} + n$.",
                        "answer": r"4k^{2} + 2k",
                        "placeholder": "?",
                        "hint": r"$(2k)^{2} = 4k^{2}$, and then add the $n$ itself.",
                        "deconstruct": [
                            "Square the even number, then add it.",
                            r"Both terms are divisible by 2, giving $2(2k^{2} + k)$.",
                        ],
                    },
                    {
                        "prompt": r"Second case: put $n = 2k + 1$ and expand $n^{2} + n$. Every integer is covered by these two cases, which is what makes the split a proof.",
                        "answer": r"4k^{2} + 6k + 2",
                        "placeholder": "?",
                        "hint": r"You already have $n^{2} = 4k^{2} + 4k + 1$ from the first step. Add $2k + 1$ to it.",
                        "deconstruct": [
                            r"$n^{2} = 4k^{2} + 4k + 1$ and $n = 2k + 1$.",
                            "Add them and collect the like terms.",
                            r"The result is $2(2k^{2} + 3k + 1)$, so this case is even too.",
                        ],
                    },
                ],
                "closing": r"""
The last two steps prove that $n^{2} + n$ is even for every integer, so Euler's
polynomial $n^{2} + n + 41$ is always odd — part of why it stays prime for $n = 0$
through $n = 39$. It is not prime at $n = 40$, where it is $1681 = 41 \times 41$, and
those forty confirmations proved forty instances and nothing about the claim.
""",
            },
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
                "The alternation is not a pattern taken on faith: an element in exactly `j` of the sets is counted `C(j,1) - C(j,2) + C(j,3) - ...` times, and the binomial theorem applied to `(1-1)^j = 0` makes that exactly 1 for every `j` at once",
                "All of the counting here is about *finite* sets. The membership algebra survives for any sets, since De Morgan and distributivity were only ever propositional laws about one element, but `|A| + |B| - |A n B|` has no content when the sets are infinite — Module 13 supplies the replacement",
            ],
            "read": {
                "title": "Membership is the only primitive, and counting is what it costs",
                "minutes": 15,
                "body": r"""
Two course registers arrive as lists of student ids. One has 18 names, the other 15, and
the class has 30 students. How many are taking at least one of the two courses? Adding
gives 33, which is more students than exist. The overcount is the subject of the second
half of this module, and the reason the overcount has an exact size is the subject of the
first.

## One relation, and everything built from it

A set is fixed by its members and by nothing else. Order carries no information and
repetition carries none, so `{a, b}`, `{b, a}` and `{a, b, b}` are the same set written
three ways. The only primitive question is *is `x` in `A`*, and every other notion in the
module is that question asked about several sets at once.

Two relations get confused constantly, so pin them down on an example. Let
`A = {1, {2}}`. This set has exactly two members: the number 1, and the *set* `{2}`.
Then `{2}` is an element of `A`, and `{{2}}` — the one-element collection whose member is
`{2}` — is a subset of `A`. But 2 is **not** an element of `A`: it is an element of an
element, and membership does not chain. And `{2}` is not a subset of `A`, because that
would require 2 itself to be in `A`. The empty set is the sharpest case of the same
distinction: it is a subset of every set and an element of almost none.

## The power set, counted rather than quoted

How many subsets does an $n$-element set have? Building a subset means making one
decision per element — in or out — and the decisions constrain each other not at all, so
the product rule gives $2^n$. Both extremes are genuine subsets: take nothing and you
have the empty set, take everything and you have the whole set.

That count is not merely a formula with the same value as something in Module 1. It is
the same object. A subset of an $n$-element set is a choice of in-or-out per element; a
row of a truth table over $n$ variables is a choice of true-or-false per variable. Write
either as a string of $n$ bits and they are literally the same string. The 32 subsets of
`{1,2,3,4,5}` and the 32 rows of a five-variable truth table are one list under two names.

A second count, which is worth doing because it is so often guessed: of those $2^n$
subsets, how many contain a particular fixed element? Fix the decision for that one
element to "in" and let the other $n - 1$ decisions run free, giving $2^{n-1}$ — exactly
half. For `{1,2,3,4,5}` that is 16 of the 32.

## The algebra is Module 1, under a change of notation

An element lies in `A n B` exactly when *`x` is in `A`* and *`x` is in `B`* are both
true. So intersection **is** conjunction, union **is** disjunction, and complement **is**
negation, applied to membership statements. That is not an analogy between two subjects.
It is one subject with two notations.

Take the set identity `~(A n B) = ~A u ~B`. Read it one element at a time: `x` lies on
the left exactly when `~(P & Q)` holds, where `P` is "`x` is in `A`" and `Q` is "`x` is in
`B`", and `x` lies on the right exactly when `~P | ~Q` holds. Those two propositional
formulas have identical truth tables, which you checked in Module 1. Since the two sides
agree on every element, they are the same set. Every remaining law arrives the same way
and needs no new proof: distributivity, absorption, double complement, all of them.

## Inclusion-exclusion, derived

Back to the registers. Adding 18 and 15 counts every student who takes both courses
twice — once in each list — so subtracting the overlap once puts each of them back to a
single count:

$$|A \cup B| = |A| + |B| - |A \cap B| = 18 + 15 - 7 = 26$$

and $30 - 26 = 4$ students take neither. Note the sanity check that is available for
free: the uncorrected 33 exceeds the class size, so something was wrong before any
formula was consulted.

Three sets is where the pattern has to be earned rather than extended by analogy. A
faculty of 100: 60 use Python, 45 use C, 30 use Rust; 25 use Python and C, 15 use Python
and Rust, 10 use C and Rust, and 5 use all three. Then

$$60 + 45 + 30 - 25 - 15 - 10 + 5 = 90$$

so 10 people use none of the three. Why does the correction alternate, and why does the
triple term come back with a plus?

Follow a single person who uses exactly $j$ of the three languages, and count how many
times the expression counts them. The singleton terms count them once for each language
they use: $C(j,1)$ times. The pairwise terms subtract them once for each pair of
languages they use: $C(j,2)$ times. The triple term adds them back $C(j,3)$ times. So the
total number of times this person is counted is

$$C(j,1) - C(j,2) + C(j,3) - \cdots$$

and the claim of the theorem is that this equals exactly 1, whatever $j$ is. It does, and
the reason is the binomial theorem. Expanding $(1 - 1)^j$ gives
$C(j,0) - C(j,1) + C(j,2) - \cdots$, and $(1-1)^j = 0$ for every $j \ge 1$. So that whole
alternating sum is zero, and moving the leading $C(j,0) = 1$ across gives

$$C(j,1) - C(j,2) + C(j,3) - \cdots = 1$$

Every element in at least one set is counted exactly once, and the alternation is not a
patch applied repeatedly — it is one identity, checked once, covering every $j$ at the
same time. Someone in all three of our languages, $j = 3$, is counted $3 - 3 + 1 = 1$
time. Someone in exactly two is counted $2 - 1 = 1$. Someone in one is counted 1.

## The mistake, and why it is tempting

The one that costs marks is dropping the correction and not noticing, because the result
of an overcount looks exactly like the result of a count. 18 plus 15 is 33 and 33 is a
perfectly ordinary number; only comparing it against the class of 30 exposes it. When the
sets are large enough that no such comparison is available, nothing at all announces the
error. The habit worth building is to name the overlap before adding, even when you
believe it is empty — "the overlap is zero" is a claim, and writing it down is what makes
it one.

The second is subtler and it is about the shape of the correction rather than its
presence: with three sets, subtracting the three pairwise overlaps subtracts the people
in all three *three times*, having added them three times, which leaves them at zero. The
plus on the triple term is not symmetry or aesthetics. It is those people being restored
from zero to one.

## Where all of this stops holding

Every count above assumed finite sets. `|A u B| = |A| + |B| - |A n B|` has no content
when the sets are infinite: the even numbers and the odd numbers are both infinite, their
intersection is empty and their union is the integers, and "infinity plus infinity minus
zero" is not an arithmetic anyone has defined. The membership algebra survives intact —
De Morgan and distributivity hold for arbitrary sets, because they were only ever
propositional laws about a single element — but the counting does not. What size can
still mean once the sets are infinite is Module 13's subject, and the answer there comes
from Module 5's bijections rather than from any tally.
""",
            },
            "derive": {
                "title": "From one decision per element to the alternating correction",
                "minutes": 12,
                "brief": r"""
Both counts in this module come from the same move — asking what independent decision
builds the object — and the alternating signs of inclusion-exclusion come from a single
binomial identity rather than from a pattern extended on faith.

Write $a = |A|$, $b = |B|$ and $i = |A \cap B|$ for two sets. For three, write $s$ for the
sum of the three individual sizes, $p$ for the sum of the three pairwise intersections and
$t$ for the size of the triple intersection.
""",
                "vars": ["n", "k", "j", "a", "b", "i", "s", "p", "t"],
                "steps": [
                    {
                        "prompt": r"Building a subset of an $n$-element set means one independent in-or-out decision per element. How many subsets are there?",
                        "answer": r"2^{n}",
                        "placeholder": "?",
                        "hint": "Two choices, made once per element, with nothing linking the choices.",
                        "deconstruct": [
                            "The product rule multiplies the number of options at each independent choice.",
                            r"Both extremes count: all-out is the empty set, all-in is the whole set.",
                        ],
                    },
                    {
                        "prompt": r"Of those subsets, how many contain one particular fixed element? Force that element's decision and let the rest run free.",
                        "answer": r"2^{n-1}",
                        "placeholder": "2^{?}",
                        "hint": "One decision is now made for you. How many are left?",
                        "deconstruct": [
                            r"There are $n - 1$ elements still to decide.",
                            r"So exactly half of all subsets contain any given element.",
                        ],
                    },
                    {
                        "prompt": r"Two sets. Adding $a$ and $b$ counts each element of the intersection twice. Write the size of the union in terms of $a$, $b$ and $i$.",
                        "answer": r"a + b - i",
                        "placeholder": "?",
                        "hint": "Each doubly-counted element needs removing exactly once, and there are $i$ of them.",
                        "deconstruct": [
                            "An element in exactly one set is already counted once by the sum.",
                            "An element in both is counted twice and should be counted once.",
                        ],
                    },
                    {
                        "prompt": r"Three sets, in the same style. Write the size of the union in terms of $s$, $p$ and $t$.",
                        "answer": r"s - p + t",
                        "placeholder": "?",
                        "hint": r"Subtract every pairwise overlap, then repair what that did to the elements lying in all three.",
                        "deconstruct": [
                            r"An element of all three sets is counted 3 times by $s$.",
                            r"It is then subtracted 3 times by $p$, leaving it at zero.",
                            "So it has to be added back once.",
                        ],
                    },
                    {
                        "prompt": r"Justify that alternation once and for all. The binomial theorem gives $(1-1)^{j} = C(j,0) - C(j,1) + C(j,2) - \cdots$, and $(1-1)^{j} = 0$ for every $j \ge 1$. Moving $C(j,0) = 1$ across, what does $C(j,1) - C(j,2) + C(j,3) - \cdots$ equal?",
                        "answer": r"1",
                        "placeholder": "?",
                        "hint": r"The full alternating sum starting at $C(j,0)$ is zero, and $C(j,0)$ is 1.",
                        "deconstruct": [
                            r"$0 = 1 - \left(C(j,1) - C(j,2) + \cdots\right)$.",
                            "Rearrange for the bracket.",
                            r"So an element lying in exactly $j$ of the sets is counted exactly once, for every $j \ge 1$ at the same time.",
                        ],
                    },
                    {
                        "prompt": r"Spend it. In a class of 30, 18 take Python, 15 take C and 7 take both. How many take neither?",
                        "answer": r"4",
                        "placeholder": "?",
                        "hint": r"The union is $18 + 15 - 7$. Subtract that from the class.",
                        "deconstruct": [
                            r"$18 + 15 - 7 = 26$ take at least one.",
                            r"$30 - 26$ take neither.",
                            r"Note that the uncorrected $18 + 15 = 33$ already exceeds the class, which is the check that catches a dropped correction.",
                        ],
                    },
                ],
                "closing": r"""
Both halves of this module are the same move twice: name the independent decision, then
multiply. The alternating signs are the one place where that is not enough on its own,
and the binomial identity in step 5 is what turns a pattern into a proof — it covers
every $j$ at once, so nothing is left to check case by case.
""",
            },
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
                "It is not an extra axiom beside the counting, it *is* the counting: the injections from a `k`-set into an `n`-set number `n!/(n-k)!`, and at `k = n+1` that falling product reaches the factor 0 — which is why the principle can rule out every hash function at once without being shown any of them",
                "Pigeonhole reports certainty, never likelihood: 367 people force a shared birthday, and the familiar 23 is a probability of 0.5073 established by an entirely different argument that belongs to the probability course",
                "Generalised pigeonhole: `n` items in `k` boxes force some box to hold at least `ceil(n/k)` of them",
                "Pigeonhole is a theorem about *finite* sets, and the word is load-bearing: `n -> 2n` is an injection from the naturals into a proper subset of themselves, which Module 13 takes as the definition of being infinite",
            ],
            "read": {
                "title": "One value out, and what happens when there is not enough room",
                "minutes": 15,
                "body": r"""
A hash table sends keys to buckets. Somebody asks whether a good enough hash function
could avoid collisions entirely, given 1000 keys and 512 buckets. The answer is no, and
the interesting part is that answering does not require knowing anything about the hash
function — not its code, not its quality, not the keys. It is a fact about counting, and
this module is about where such facts come from.

## What a function is obliged to do

A function from $D$ to $C$ assigns to **every** element of $D$ **exactly one** element of
$C$. Two failures are possible and both disqualify the rule entirely: a gap, where some
input gets no output, and a fork, where some input gets two. Note what is *not* a
failure — two different inputs sharing an output. That is permitted, and most functions
do it.

Take the rule sending each living person to their age in whole years, into the integers
0 to 200. Every person has exactly one age, so it is a function. Two people of the same
age share a value, so it is not injective, and resoundingly so. Nobody is 200, so that
codomain value goes unused and it is not surjective. Injectivity is a condition on the
input side — no collisions — and surjectivity on the output side — nothing missed. They
are independent, and a rule that is not a function at all fails for a third reason.

## Counting functions, and watching one kind run out

Fix a domain of $k$ elements and a codomain of $n$. How many functions are there? Each of
the $k$ inputs is assigned independently, with $n$ options each, so

$$n^k$$

How many of them are injective? Now the choices are not independent: assign the first
input any of the $n$ values, the second any of the remaining $n - 1$, the third $n - 2$,
and so on for $k$ inputs. That is the falling product

$$n(n-1)(n-2)\cdots(n-k+1) \;=\; \frac{n!}{(n-k)!}$$

Put $k = n = 5$. There are $5^5 = 3125$ functions from a five-element set to itself and
$5! = 120$ injections, so under 4 per cent of them are injective — and when the domain
and codomain have the same finite size, injective, surjective and bijective all coincide,
so those 120 are exactly the bijections.

Now push $k$ one past $n$. The falling product runs
$n, n-1, \ldots$ down to $n - (n+1) + 1 = 0$, so **it contains the factor zero** and the
whole product is zero. There are no injections from an $(n+1)$-element set into an
$n$-element one.

That is the pigeonhole principle. It is not an extra axiom bolted on beside the counting;
it is the counting, read at the point where it returns zero. And it explains why the
principle can say something so strong while knowing so little: it never needed to know
which function you had, only how many there were of the kind you wanted.

For the hash table: 1000 keys into 512 buckets admits zero injections, so some bucket
receives two keys, whatever the hash function is. That is why a hash table ships with a
collision strategy rather than a hope.

## The generalised form, and the inequality it actually rests on

"Some bucket gets two" is weak when the table is badly overloaded. The sharper statement:
$t$ items in $k$ boxes force some box to hold at least `ceil(t/k)` of them.

Prove it by contradiction, and watch which step does the work. Suppose every box holds at
most $m$ items. Then the total across all boxes is at most

$$k \cdot m$$

Now take $m$ to be `ceil(t/k) - 1`. The defining property of the ceiling is that
`ceil(t/k)` is the smallest integer at or above $t/k$, so `ceil(t/k) - 1` is strictly
*below* $t/k$, and multiplying by the positive $k$ keeps it strictly below $t$. So the
total is at most something strictly less than $t$ — but the total is $t$. The supposition
fails, and some box holds more than `ceil(t/k) - 1`, which for integers means at least
`ceil(t/k)`.

With $t = 1000$ and $k = 512$: `ceil(1000/512) = 2`, and if all 512 buckets held at most
1 key they would hold at most 512 keys between them, against 1000. Note what the
conclusion is and is not. It is a lower bound on the *worst* box. It is not a description
of the distribution — the counts may be wildly uneven, no particular box is forced to be
occupied, and in principle all 1000 keys land in one.

## A pigeonhole that needs an idea

Counting alone is not always enough, and the standard example is worth doing because the
first attempt fails. Claim: in any group of $n \ge 2$ people, two of them know the same
number of the others.

The obvious move is to take people as items and acquaintance-counts as boxes. A person
can know anywhere from 0 to $n - 1$ others, which is $n$ possible values for $n$ people —
and $n$ items in $n$ boxes force nothing at all. The counting argument, applied directly,
does not work.

The idea it needs is one observation: 0 and $n-1$ cannot both occur. Somebody who knows
nobody and somebody who knows everybody cannot be in the same group, since the second
would have to know the first. So whichever end is unused, the values actually available
number at most

$$n - 1$$

and now $n$ people into $n - 1$ boxes forces a repeat. Try it at $n = 4$: the degrees must
come from `{0,1,2}` or from `{1,2,3}`, three values for four people either way.

```python
from itertools import combinations

# Search every graph on n people for one where all the degrees differ.
def find_all_distinct(n):
    pairs = list(combinations(range(n), 2))
    for mask in range(1 << len(pairs)):
        deg = [0] * n
        for i, (u, v) in enumerate(pairs):
            if mask >> i & 1:
                deg[u] += 1
                deg[v] += 1
        if len(set(deg)) == n:
            return deg
    return None

for n in range(2, 7):
    print(n, find_all_distinct(n))
```

That is an exhaustive search — every one of the $2^{C(n,2)}$ graphs on $n$ people, which
is 32768 of them at $n = 6$ — and it prints `None` on every line. There is no
counterexample to find.

The lesson generalises past this example. Pigeonhole arguments are rarely hard because
the principle is hard; they are hard because choosing the boxes is a design decision, and
the obvious boxes are often one too many.

## The mistake, and why it is tempting

Pigeonhole reports *certainty*, and the sentence next to it in most people's memory
reports *likelihood*. With 367 people some two share a birthday, guaranteed, because 367
items into 366 boxes admits no injection. With 23 people the probability that some two
share a birthday is 0.5073 — better than even. These are entirely different claims,
established by entirely different means, and the second one is not pigeonhole doing
anything at all. Pigeonhole says nothing whatever about 23 people; it is silent on every
group smaller than 367.

The confusion is tempting because both sentences begin "with enough people, two of them
share a birthday" and both feel like results about crowding. Only one of them is a
counting fact. The other is a probability calculation, and it belongs to the probability
course rather than here.

## Where it stops holding

Everything above needed the sets to be finite, and the word is load-bearing rather than
decorative. The map $n \mapsto 2n$ sends the naturals injectively into the even naturals,
which are a proper subset of them — an injection from a set into something strictly
smaller than itself, which is exactly what pigeonhole forbids. Nothing is broken. The
theorem was about finite sets, and Module 13 takes precisely this behaviour as the
*definition* of being infinite.

Two smaller boundaries in the same neighbourhood, since they are usually stated without
conditions. An injection is often said to have a left inverse, and that needs the domain
to be non-empty: with an empty domain and a non-empty codomain there is nowhere for the
reverse map to send anything, and the empty map is injective. A surjection is often said
to have a right inverse, which for a finite codomain is a matter of picking one preimage
per value, but for infinite sets is the axiom of choice — a genuine assumption rather
than a construction. Neither caveat changes anything you will do in this course. Both are
worth knowing about before you meet a proof that leans on one.
""",
            },
            "derive": {
                "title": "Injections, counted until there are none left",
                "minutes": 12,
                "brief": r"""
The pigeonhole principle is usually presented as a separate fact about boxes. Here it is
derived as the moment a count reaches zero, which is also the explanation for why it can
say so much while assuming so little.

Throughout, the domain has $k$ elements and the codomain $n$. In the last two steps, $t$
items go into $k$ boxes and $m$ is a capacity per box.
""",
                "vars": ["n", "k", "m", "t"],
                "steps": [
                    {
                        "prompt": r"Each of the $k$ inputs is assigned a value independently, and there are $n$ values available. How many functions are there from a $k$-element set to an $n$-element set?",
                        "answer": r"n^{k}",
                        "placeholder": "?",
                        "hint": r"$n$ options, chosen $k$ times, with nothing linking the choices.",
                        "deconstruct": [
                            "One choice per element of the domain.",
                            "Reusing a value is allowed, so the choices really are independent.",
                        ],
                    },
                    {
                        "prompt": r"Now demand that no two inputs collide. The first input has $n$ values available, the second $n-1$, and so on for $k$ inputs. Write that falling product as a ratio of factorials.",
                        "answer": r"\frac{n!}{(n-k)!}",
                        "placeholder": r"\frac{?}{?}",
                        "hint": r"$n(n-1)\cdots(n-k+1)$ is $n!$ with the last $n-k$ factors divided away.",
                        "deconstruct": [
                            r"The product has exactly $k$ factors, running down from $n$.",
                            r"$n!$ continues past where the product stops, at $n-k$.",
                        ],
                    },
                    {
                        "prompt": r"Set $k = n$, so the domain and codomain are the same size. What does that count become?",
                        "answer": r"n!",
                        "placeholder": "?",
                        "hint": r"$(n-n)! = 0! = 1$.",
                        "deconstruct": [
                            "Substitute and simplify the denominator.",
                            "At equal finite sizes, the injections are exactly the bijections.",
                        ],
                    },
                    {
                        "prompt": r"Now set $k = n + 1$. The falling product runs from $n$ down to $n - (n+1) + 1$. Evaluate that last factor — the number it reaches — and you have the pigeonhole principle.",
                        "answer": r"0",
                        "placeholder": "?",
                        "hint": r"$n - (n+1) + 1$ simplifies without needing a value for $n$.",
                        "deconstruct": [
                            r"The $j$-th factor is $n - j + 1$, and here $j$ runs to $k = n+1$.",
                            "A product with a zero factor is zero.",
                            "So there are no injections at all from a larger finite set into a smaller one.",
                        ],
                    },
                    {
                        "prompt": r"The generalised form, by contradiction. Suppose each of the $k$ boxes holds at most $m$ items. What is the largest the total across all boxes can be?",
                        "answer": r"km",
                        "placeholder": "?",
                        "hint": "The worst case is every box simultaneously full.",
                        "deconstruct": [
                            r"There are $k$ boxes and each contributes at most $m$.",
                            r"If that maximum is below the number of items actually placed, the supposition is false.",
                        ],
                    },
                    {
                        "prompt": r"Spend it on the hash table: $t = 1000$ keys, $k = 512$ buckets. If every bucket held at most one key, what is the largest number of keys the table could hold? Comparing it against 1000 is the whole argument.",
                        "answer": r"512",
                        "placeholder": "?",
                        "hint": r"Put $m = 1$ into the previous step.",
                        "deconstruct": [
                            r"$k \cdot m$ with $k = 512$ and $m = 1$.",
                            r"512 is short of 1000, so some bucket holds at least `ceil(1000/512) = 2`.",
                        ],
                    },
                ],
                "closing": r"""
Step 4 is the point of the whole exercise: pigeonhole is not an extra principle sitting
beside the counting, it is the counting evaluated where it returns zero. That is why it
can rule out every hash function at once without being shown any of them — it never
needed to know which function you had, only how many of the wanted kind exist.
""",
            },
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
One-sided inverses exist without both, though each carries a condition worth stating: an
injection has a left inverse provided its domain is non-empty, and a surjection has a
right inverse — which for a finite codomain means picking one preimage per value, and for
an infinite one is the axiom of choice rather than a construction. Neither undoes the map
in both directions. Computability is a
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
                "Nearly every failed induction is a missing base case or a step valid only above some threshold — the all-horses-one-colour argument fails on exactly this, and the two groups of `k` horses inside `k+1` overlap in `k-1` of them, which is 0 at `k = 1`",
                "A valid inductive step on its own determines nothing: `S(n) = n(n+1)/2 + c` survives the step for *every* `c`, so with `c = 5` it claims `1 + 2 + 3 = 11`. Only the base case picks `c` out, which is why it is half the proof rather than a formality",
                "Induction is a fact about the naturals — equivalent to every non-empty set of them having a least element — and needs every element reachable from the base in finitely many `+1` steps. There is no next rational, so there is no induction over the rationals to run",
                "A closed form for a sum is the standard thing induction is asked to prove: it can confirm a formula but never propose one, which is why Module 12 derives the geometric sum by cancellation first and only then checks it",
            ],
            "read": {
                "title": "The first domino, and the rung nobody checked",
                "minutes": 15,
                "body": r"""
Add up the odd numbers and watch what happens.

$$1 = 1, \qquad 1 + 3 = 4, \qquad 1 + 3 + 5 = 9, \qquad 1 + 3 + 5 + 7 = 16$$

Those are $1^2, 2^2, 3^2, 4^2$. The guess writes itself: the first $n$ odd numbers sum to
$n^2$.

Before proving it, notice where the guess came from, because it did not come from
induction and induction could not have produced it. It came from computing four cases and
recognising the pattern. There is also a picture that produces it: a square of side $n$
grows into a square of side $n+1$ by adding an L-shaped strip of $n$ cells along the top,
$n$ down the side and one in the corner — $2n + 1$ cells, which is the $(n+1)$-th odd
number. Induction confirms a closed form; it never proposes one. Module 12 makes the same
point about the geometric series, which is derived by cancellation first and checked
afterwards.

## The proof, and the answer to the objection

Two obligations. The base case: with $n = 0$ the sum is empty and equals $0 = 0^2$. The
inductive step: assume the claim at some arbitrary $n$ and derive it at $n+1$. The sum of
the first $n+1$ odd numbers is the sum of the first $n$, which the assumption values at
$n^2$, plus the next odd number $2n + 1$:

$$n^2 + 2n + 1 = (n+1)^2$$

Done. Now the objection everybody has and few people get answered: *you assumed the thing
you were proving*. You did not. What the step establishes is the implication `P(n) ->
P(n+1)`, and an implication can be proved without its antecedent ever being true — that
is what Module 1's truth table for `->` says. Nothing in the step claims $P(n)$ holds. The
base case supplies the one unconditional fact, and the chain of implications carries it
upward forever. This is also why $n$ must be arbitrary: a single specific link would
prove a single specific instance and stop.

## The step alone proves nothing, and here is a formula to prove it with

That last claim is usually asserted. It can be demonstrated, and the demonstration is one
line long.

Take the sum $S(n) = 1 + 2 + \cdots + n$ and consider the candidate formula

$$S(n) = \frac{n(n+1)}{2} + c$$

for a constant $c$ you may choose freely. Run the inductive step. Assume
$S(k) = k(k+1)/2 + c$ and add the next term $k+1$:

$$\frac{k(k+1)}{2} + c + (k+1) = \frac{k(k+1) + 2(k+1)}{2} + c = \frac{(k+1)(k+2)}{2} + c$$

which is the formula at $k+1$. The step is valid. It is valid **for every value of $c$**,
because $c$ sits outside everything the step touches. So with $c = 5$ the formula claims
$1 + 2 + 3 = 3 \cdot 4/2 + 5 = 11$, when the sum is 6.

A flawless inductive step, a formula that is wrong by 5 at every single $n$. The only
thing that rules $c$ out is the base case: $S(0) = 0$ and the formula gives $c$, so
$c = 0$. The base case is not a formality to be discharged before the real work. It is
half the proof, and it is the half that decides which of infinitely many formulas the
step is telling you about.

## The step that only works from the second rung

The other failure mode is a step that is valid above some threshold with no base case at
that threshold, and the classic instance is the argument that all horses are one colour.

It goes: one horse is one colour, so $P(1)$ holds. For the step, take $k+1$ horses and
look at the first $k$ and the last $k$. Each group is one colour by the hypothesis, and
the two groups overlap, so a horse in the overlap ties the two colours together and all
$k+1$ horses match.

The overlap is where it dies, and the size of it is computable rather than a matter of
opinion. Two subsets of size $k$ inside a set of size $k+1$ must share

$$k + k - (k+1) = k - 1$$

elements. For $k \ge 2$ that is at least one horse and the step is sound. At $k = 1$ it is
**zero**: the first horse and the last horse, with nothing in between to connect them. So
the argument proves $P(1)$, and proves $P(k) \rightarrow P(k+1)$ for every $k \ge 2$, and
never proves $P(1) \rightarrow P(2)$. The chain has a first link missing and everything
above it is unsupported.

The general habit that catches this: whenever a step splits, overlaps, or removes
elements, evaluate the size of the split at the smallest case by hand. Not the argument —
the arithmetic.

## Strong induction, and when the previous rung is not enough

Weak induction hands you $P(k)$ and asks for $P(k+1)$. Some arguments need more. *Every
integer above 1 has a prime factorisation*: if $n$ is composite, write $n = a \cdot b$
with $1 < a, b < n$, and now you need the claim at $a$ and at $b$, which can sit anywhere
below $n$ and are almost never $n - 1$. Strong induction assumes the claim for everything
from the base up to $k$ and proves it at $k+1$, which is exactly what that recursion
needs.

The two forms are equally powerful — apply weak induction to the statement
`Q(n) = "P(0) and P(1) and ... and P(n)"` and you recover strong induction — so the
choice is about which makes the argument short, never about which is permitted.

## Recursive definitions, and what structural induction gives you

Define a set $S$ by: 3 is in $S$, and if $x$ and $y$ are in $S$ then so is $x + y$.
Structural induction checks the property on the base objects and shows each construction
rule preserves it. Divisibility by 3: the base object 3 qualifies, and if $x$ and $y$ are
both multiples of 3 then so is $x + y$. So every member of $S$ is a multiple of 3.

Notice what that argument does **not** give you: the reverse inclusion. It says every
member of $S$ is a multiple of 3, not that every multiple of 3 is in $S$ — and the
reverse is false here, since 3 is the smallest member and 0 and the negatives never
appear. Pinning $S$ down exactly needs a second, separate argument showing each intended
element is reachable, which is an ordinary induction on the naturals and yields
`S = {3, 6, 9, ...}` informally, or `{3n : n >= 1}` written carefully. Two
inclusions, two proofs. Producing one and claiming both is the standard slip with
recursively defined sets.

## Where induction stops

Induction is not a general technique for proving universal statements. It is a specific
fact about the natural numbers — equivalent, in fact, to the statement that every
non-empty set of naturals has a least element, which is where the "first counterexample"
form of the argument comes from.

What it needs is that every element is reached from the base by finitely many steps of
$+1$. The rationals do not have that structure: there is no next rational after $1/2$, so
there is no step to take and no induction to run. Neither do the reals. A proof that
proceeds "by induction on a real number" is not a proof with a gap in it; it is a
sentence with no meaning attached. Module 13 shows that the rationals *can* be listed one
after another, which is a genuinely surprising fact — but that listing is not their
order, and induction along it proves nothing about the ordering it scrambled.
""",
            },
            "derive": {
                "title": "Two obligations, and what happens when you discharge only one",
                "minutes": 12,
                "brief": r"""
The first three steps prove a closed form the ordinary way. The next two build a formula
whose inductive step is flawless and whose conclusion is false, which is the sharpest
demonstration available that the base case is doing real work. The last pins down where
the all-horses argument dies, by computing the size of an overlap rather than describing
it.

Write $S(n)$ for the sum $1 + 2 + \cdots + n$, and let $c$ be an arbitrary constant.
""",
                "vars": ["n", "k", "c", "S"],
                "steps": [
                    {
                        "prompt": r"The first $n$ odd numbers sum to $1, 4, 9, 16$ for $n = 1, 2, 3, 4$. Write the closed form these four values suggest.",
                        "answer": r"n^{2}",
                        "placeholder": "?",
                        "hint": "Each of the four values is a perfect square, and the pattern in which one is direct.",
                        "deconstruct": [
                            r"$1 = 1^2$, $4 = 2^2$, $9 = 3^2$.",
                            "This is a guess, not yet a proof — which is the point of the next step.",
                        ],
                    },
                    {
                        "prompt": r"The inductive step. Assume the first $n$ odd numbers sum to $n^{2}$ and add the next odd number, $2n + 1$. Simplify the total to a single square.",
                        "answer": r"(n+1)^{2}",
                        "placeholder": "(?)^{2}",
                        "hint": r"$n^{2} + 2n + 1$ is a perfect square trinomial.",
                        "deconstruct": [
                            r"The $(n+1)$-th odd number is $2n+1$.",
                            r"$n^{2} + 2n + 1$ factors.",
                            r"With the base case $0 = 0^{2}$, the claim now holds for every $n$.",
                        ],
                    },
                    {
                        "prompt": r"Now the cautionary formula. Suppose $S(k) = \frac{k(k+1)}{2} + c$ and add the next term $k + 1$. Simplify to the same shape one step further on.",
                        "answer": r"\frac{(k+1)(k+2)}{2} + c",
                        "placeholder": r"\frac{?}{2} + c",
                        "hint": r"Put $k+1$ over the same denominator: $\frac{k(k+1) + 2(k+1)}{2}$, then take out the common factor.",
                        "deconstruct": [
                            r"$\frac{k(k+1)}{2} + (k+1) = \frac{k(k+1) + 2(k+1)}{2}$.",
                            r"Both terms of the numerator share the factor $(k+1)$.",
                            r"The constant $c$ was never touched, so the step holds whatever $c$ is.",
                        ],
                    },
                    {
                        "prompt": r"So that step is valid for every $c$. Take $c = 5$ and ask the formula for $S(3)$. What does it predict? The true value of $1 + 2 + 3$ is 6.",
                        "answer": r"11",
                        "placeholder": "?",
                        "hint": r"$\frac{3 \cdot 4}{2} + 5$.",
                        "deconstruct": [
                            r"$\frac{3 \cdot 4}{2} = 6$.",
                            "Then add the constant.",
                            r"The step was flawless and the formula is wrong at every $n$: only the base case, $S(0) = 0$, forces $c = 0$.",
                        ],
                    },
                    {
                        "prompt": r"The all-horses argument takes $k+1$ horses and two overlapping groups of $k$. Two subsets of size $k$ inside a set of size $k+1$ share how many elements? Use inclusion-exclusion from Module 4.",
                        "answer": r"k - 1",
                        "placeholder": "?",
                        "hint": r"The union is everything, so $k + k - |\text{overlap}| = k + 1$.",
                        "deconstruct": [
                            r"$|A \cup B| = |A| + |B| - |A \cap B|$, and here the union is all $k+1$ horses.",
                            r"Rearrange for the intersection.",
                        ],
                    },
                    {
                        "prompt": r"Evaluate that overlap at $k = 1$ — the first rung the argument needs, going from one horse to two.",
                        "answer": r"0",
                        "placeholder": "?",
                        "hint": "Substitute directly into the previous answer.",
                        "deconstruct": [
                            "The two groups of one horse are the first horse and the last horse.",
                            "With nothing shared, there is no horse to carry a colour between them.",
                            r"So $P(1) \rightarrow P(2)$ is never established, and the whole chain above it is unsupported.",
                        ],
                    },
                ],
                "closing": r"""
Steps 3 and 4 and step 6 are the same defect twice, in the two costumes it wears: a step
valid for every $c$ with no base case to choose one, and a step valid for every $k \ge 2$
with no base case at 2. Whenever a step splits, overlaps or removes elements, compute the
size of the split at the smallest case rather than describing it.
""",
            },
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
            "read": {
                "title": "Five cards, and the overcount that looks like a product",
                "minutes": 16,
                "body": r'''
Deal five cards off a shuffled deck. How many different hands can you be holding?

The number is 2598960, and the interesting part is not the number — it is that three
separate counting arguments stand between the deck and it, and skipping any one of them
gives a different answer that also looks right. This module is about which argument to
reach for, and the way to tell is to ask what a *stage* of the choice is and whether the
same hand can be reached twice.

## The product rule, and the condition it quietly imposes

A canteen offers 3 starters and 4 main courses. Draw the choices as a tree: the root
splits three ways, and each of those three splits four ways, giving
$3 \times 4 = 12$ leaves. Each leaf is a distinct meal and every meal is one leaf, so
there are 12 meals.

What the tree needed was not that the four mains are the *same* four after each starter.
It needed that there are *four of them* whichever starter was taken. Change the rule to
"any main except the one sharing a sauce with your starter" and each starter leaves three
mains, so the count is $3 \times 3 = 9$ — the sets differ, the size does not, and the
product rule still applies. Change it to "the fish starter may be followed by any main,
the others by two" and the tree is lopsided; there is no single second factor and the
count is a sum, $4 + 2 + 2 = 8$.

That is the sum rule, and it is the other half of the pair: alternatives that cannot
overlap add. Overlap is what breaks it, and overlap is what breaks most counts.

## Ordered first, because ordered is easier

Deal the five cards face up, one at a time, and record the sequence. The first card is any
of 52, the second any of the 51 that remain, and so on:

$$52 \times 51 \times 50 \times 49 \times 48 = 311875200$$

Every stage offers a number of options that does not depend on which cards came before —
one fewer each time — so the product rule applies exactly. This is $P(52, 5)$, and note
what it is: the first five factors of $52!$. Building $52!$ and dividing by $47!$ gives the
same number after passing through a 68-digit intermediate, which is why the lab computes
the falling product directly and never calls for a factorial.

## From ordered to unordered, by dividing out what you counted twice

A hand of five cards, held in the hand, has no order. The sequence
$(A\spadesuit, 7\heartsuit, 7\clubsuit, K\diamondsuit, 2\spadesuit)$ and every
rearrangement of it are the same hand. How many sequences produced each hand? Exactly
$5! = 120$, the number of orders five distinct cards can be laid out in.

The word carrying the argument is *exactly*. Every hand is overcounted by the same 120, so
dividing the whole tally by 120 is legitimate:

$$\binom{52}{5} = \frac{311875200}{120} = 2598960$$

If different hands had been overcounted by different amounts, no single division could
repair the tally, and that possibility is not hypothetical — it is what goes wrong in the
worked example below.

## Computing it without ever building a factorial

The lab asks for the multiplicative form, and it is worth watching the intermediate values
rather than trusting the loop:

```python
result = 1
for i in range(5):
    result = result * (52 - i) // (i + 1)
    print(f"step {i}: multiply by {52 - i}, divide by {i + 1} -> {result}")
print("C(52,5) =", result)
```

The running values are 52, 1326, 22100, 270725 and 2598960 — and each of them is a
binomial coefficient in its own right, $\binom{52}{1}$ through $\binom{52}{5}$. The
integer division never loses anything, and the reason is another double count. After the
multiplication the value is $\binom{52}{i}(52-i)$, which counts the pairs consisting of an
$i$-card selection together with one further card. Count the same pairs the other way —
first the $(i+1)$-card selection, then which of its members is the "further" one — and it
is $\binom{52}{i+1}(i+1)$. The two expressions count one set of objects, so the product is
divisible by $i+1$ before the division is attempted.

Order the operations the other way, dividing before multiplying, and the exactness
evaporates: $1 // 1 \times 52$ survives, but the next step would divide 52 by 2 and then
the one after by 3, and $26 // 3$ discards a remainder that the true value needs.

## Pascal's rule is a question about one card

Fix the ace of spades and sort every 5-card hand into two boxes: the hands holding it and
the hands not. A hand in the first box is the ace plus four cards from the other 51, so
there are $\binom{51}{4}$ of them. A hand in the second is five cards from the other 51,
so $\binom{51}{5}$. The boxes do not overlap and nothing is left over, so by the sum rule

$$\binom{52}{5} = \binom{51}{4} + \binom{51}{5}$$

That is Pascal's rule, derived by asking one question about one card. With small numbers:
$\binom{5}{2} = 10$ and $\binom{4}{1} + \binom{4}{2} = 4 + 6$. It is also an algorithm —
each row of the triangle is the pairwise sums of the row above, bordered by ones — and the
lab's `pascal_row` is required to build rows that way rather than by calling
`combinations`, because the additive route needs no division and no multiplication at all.

Two more facts come free from the same style of argument. Choosing which 5 cards to take
is the same act as choosing which 47 to leave, so $\binom{52}{5} = \binom{52}{47}$; the
lab uses that to make `combinations(40, 20)` do twenty loop steps rather than forty. And
every subset of an $n$-set has some size, so the sizes partition the subsets and the row
sums to the $2^n$ subsets an in-or-out decision per element produces: row 4 is
$1, 4, 6, 4, 1$, which adds to 16.

## The mistake, and why it is tempting

Count the hands containing at least one ace. The natural move is a two-stage product:
choose the ace, $\binom{4}{1}$ ways, then choose the other four cards from the remaining
51, $\binom{51}{4}$ ways. That gives $4 \times 249900 = 999600$.

It is wrong, and it is tempting because every word of the description is true: any such
hand does contain an ace, and does contain four other cards. What the description fails to
do is name each hand *once*. A hand with two aces arises from two different first
choices — pick this ace and find that one among the four others, or the reverse — so it is
counted twice, and no division by a constant can fix a tally whose entries were multiplied
by different amounts.

```python
def choose(n, k):
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result

naive = choose(4, 1) * choose(51, 4)
exact = choose(52, 5) - choose(48, 5)
print("pick an ace, then four more:", naive)
print("all hands minus the ace-free hands:", exact)
print("difference:", naive - exact)
extra = sum((j - 1) * choose(4, j) * choose(48, 5 - j) for j in range(2, 5))
print("overcount, summed by how many aces the hand holds:", extra)
```

It prints 999600, then 886656, then 112944 twice. The honest count subtracts the ace-free
hands from all of them: $2598960 - 1712304 = 886656$. And the discrepancy is not a
mystery — a hand with $j$ aces is counted $j$ times by the two-stage description, so it
contributes $j - 1$ too many, and summing that over $j = 2, 3, 4$ gives
$103776 + 9024 + 144 = 112944$, which is the difference to the digit.

The habit worth forming: after writing a two-stage count, ask what the second stage would
have to be told in order to reconstruct the first. If a finished object cannot tell you
which branch it came down, the branches are not counting it once.

## Where these arguments stop

The product rule needs a *constant* number of options per stage, and the lopsided canteen
above already breaks it. Combinations count selections of **distinct** items with no
repetition; allowing repeats is a different count, $\binom{n + k - 1}{k}$, and using
$\binom{n}{k}$ there undercounts badly. Dividing by $k!$ assumes every object is
overcounted by the same $k!$ — true for orderings of distinct cards, false the moment
symmetry enters, as it does for beads on a necklace that can be rotated, where the
overcounts differ between symmetric and asymmetric arrangements and a heavier tool is
needed.

## What you are about to build

The lab, **Counting from first principles**, forbids `math.comb`, `math.perm` and
`math.factorial` and asks for the arguments above as code: `factorial` iteratively,
`permutations` as the falling product, `combinations` multiplicatively with the symmetry
applied first, `pascal_row` built additively from its predecessor, and
`vandermonde_holds`, which checks

$$\binom{m+n}{r} = \sum_{k=0}^{r} \binom{m}{k}\binom{n}{r-k}$$

by evaluating both sides. That identity is another one-question argument: to pick $r$
people from a room holding $m$ mathematicians and $n$ physicists, split the count by how
many mathematicians you took. With $m = 4$, $n = 5$, $r = 3$ the right-hand side is
$1 \cdot 10 + 4 \cdot 10 + 6 \cdot 5 + 4 \cdot 1 = 84$, and $\binom{9}{3}$ is 84.

The last function, `catalan`, is $\binom{2n}{n}/(n+1)$, and the triangular numbers
$\binom{n+1}{2} = 1 + 2 + \dots + n$ that fall out of the same triangle come back in
Module 13, where they number the diagonals of an infinite grid.
''',
            },
            "quiz": {
                "title": "Stages, orders and the counts that overlap",
                "minutes": 8,
                "questions": [
                    {
                        "q": "To count 5-card hands holding at least one ace, someone writes $\\binom{4}{1}\\binom{51}{4} = 999600$. The true count is 886656. What went wrong?",
                        "opts": [
                            "The second factor should be $\\binom{48}{4}$, since the other four cards must not be aces",
                            "A hand holding two aces is produced by two different first choices, so it is tallied twice",
                            "Nothing is wrong; 886656 is the number of hands holding exactly one ace, rather than at least one",
                            "The product rule never applies to cards, because the deck shrinks as cards are dealt",
                        ],
                        "a": 1,
                        "whys": [
                            "That change counts the hands with *exactly* one ace, which is a different and smaller quantity — 778320 of them. It removes the double counting by removing the hands that caused it, rather than by counting them once.",
                            "The description never names a unique first ace, so hands with several are reached by several routes.",
                            "Hands with exactly one ace number 778320, so 886656 is neither that nor the naive product. It is $\\binom{52}{5} - \\binom{48}{5}$: every hand, less the ace-free ones.",
                            "Dealing in order is a textbook use of the rule — 52, then 51, then 50 — because the number of remaining cards does not depend on which ones went before. A shrinking pool is fine; a varying branch count is not.",
                        ],
                        "why": r'''
Every word of the two-stage description is true of every hand it produces, and that is
what makes it convincing. What it fails to do is name each hand once: a hand with two aces
comes down two branches, one with three comes down three. Summing $(j-1)$ over the hands
with $j$ aces gives $103776 + 9024 + 144 = 112944$, exactly the gap between 999600 and
886656. The reliable test is to ask whether a finished object can tell you which branch
produced it.
''',
                    },
                    {
                        "q": "In `result = result * (n - i) // (i + 1)`, why is the integer division never lossy?",
                        "opts": [
                            "Because Python's `//` rounds towards zero and the error stays below one",
                            "Because $n - i$ and $i + 1$ are coprime for every $i$ in the loop's range",
                            "Because $\\binom{n}{i}(n-i)$ and $\\binom{n}{i+1}(i+1)$ count the same pairs, so the product is a multiple of $i+1$",
                            "Because the multiplication is always performed before the division, and Python's integers never overflow however large the running value grows",
                        ],
                        "a": 2,
                        "whys": [
                            "`//` discards a remainder rather than keeping an error below one, and a discarded remainder here would be wrong by a factor, not by a rounding. The point is that there is no remainder to discard.",
                            "They are frequently not coprime: at $n = 52$, $i = 3$ the factors are 49 and 4, and at $i = 1$ they are 51 and 2. Divisibility comes from the running value as a whole, not from the two factors in isolation.",
                            "One set of objects counted two ways forces the divisibility before any division is attempted.",
                            "Unbounded integers are why the intermediate value is safe, not why it is divisible. Multiplying first is indeed necessary — divide first and $26 // 3$ throws away part of the answer — but the exactness itself needs the counting argument.",
                        ],
                        "why": r'''
After the multiplication the running value is $\binom{n}{i}(n-i)$, which counts pairs of
an $i$-subset together with one further element. Count those same pairs by choosing the
$(i+1)$-subset first and then which member is the extra one, and the tally is
$\binom{n}{i+1}(i+1)$. One collection, two counts, so the value is divisible by $i+1$
before `//` runs. Order matters all the same: multiply first, because dividing 1 by 1 then
26 by 3 loses what the later multiplications would have restored.
''',
                    },
                    {
                        "q": "Pascal's rule $\\binom{n}{k} = \\binom{n-1}{k-1} + \\binom{n-1}{k}$ comes from a single question. Which one?",
                        "opts": [
                            "Whether $k$ lies closer to 0 or to $n$, which decides which of the two symmetric forms to use",
                            "Whether a chosen element is being counted with order or without it",
                            "Whether one fixed element is in the selection or out of it, splitting them into two boxes",
                            "Whether the row above the current one has already been computed additively",
                        ],
                        "a": 2,
                        "whys": [
                            "That decides which end to start the multiplicative loop from and saves work. It has nothing to do with the identity, which holds whatever the size of $k$ relative to $n$.",
                            "Order is what separates permutations from combinations, and both sides of this identity are unordered counts. Nothing in the argument mentions arrangements.",
                            "In or out is exhaustive and non-overlapping, so the sum rule applies with nothing to correct.",
                            "That is the shape of the algorithm the identity licenses, not the reason the identity is true. The equation holds whether or not anything has been computed, and the additive triangle is a consequence of it.",
                        ],
                        "why": r'''
Fix any one element — the ace of spades will do. The selections containing it are that
element plus $k-1$ from the remaining $n-1$; those not containing it are $k$ from the
remaining $n-1$. No selection is in both boxes and none is outside both, so the sum rule
applies with no correction term. That is also why a triangle row can be built from its
predecessor by pairwise addition, which is what the lab's `pascal_row` is required to do —
no multiplication, no division, no factorial.
''',
                    },
                    {
                        "q": "A canteen has 3 starters; the fish starter may be followed by any of 4 mains and each of the other two by only 2. How many meals, and what does that show?",
                        "opts": [
                            "12 meals: the product rule uses the largest branch count available",
                            "8 meals, by the sum rule — the product rule needs the same number of options at every branch",
                            "9 meals, taking the average of 4, 2 and 2 as the second factor",
                            "24 meals, since each starter must be paired with every main and then the restrictions removed",
                        ],
                        "a": 1,
                        "whys": [
                            "Taking the largest branch count would count six meals nobody can order. The product rule is not an approximation to be applied with the best available factor; it is exact when the branches match and inapplicable when they do not.",
                            "The branches are 4, 2 and 2, and unequal branches are added rather than multiplied.",
                            "Averaging happens to give a whole number here and would give 8/3 with a different menu, which is a hint that no counting argument supports it. Nothing is being counted by the average of a tree's branch widths.",
                            "There are only 12 starter-main pairs to begin with, so 24 exceeds even the unrestricted count. Subtracting from a total is a sound technique, but the total has to be a real total.",
                        ],
                        "why": r'''
Draw the tree: one branch of width 4 and two of width 2, so the leaves number
$4 + 2 + 2 = 8$. The product rule applies when every node at a level has the same number of
children — the *sets* may differ, as they do when each starter forbids one main and the
count stays $3 \times 3 = 9$. What it cannot survive is branches of different widths, and
then the sum rule takes over. Recognising which of the two applies is most of counting.
''',
                    },
                    {
                        "q": "Why is $\\binom{n}{k} = \\binom{n}{n-k}$, and what does the lab do with it?",
                        "opts": [
                            "It follows from each row of the triangle being a palindrome, and it lets `pascal_row` store only half of every row and mirror the rest",
                            "Choosing the $k$ to take is the same act as choosing the $n-k$ to leave, so `combinations(40, 20)` can loop 20 times rather than 40",
                            "It holds only when $n$ is even, and the lab uses it to test its own arithmetic",
                            "It follows from the row summing to $2^n$, and the lab uses it to avoid computing a factorial",
                        ],
                        "a": 1,
                        "whys": [
                            "The palindrome is what the identity produces, not what produces it. Storing half a row would also be a different optimisation from the one the lab performs, which is to shorten the multiplicative loop.",
                            "Every selection pairs with its complement, and the pairing is one-to-one.",
                            "It holds for every $n$: $\\binom{5}{2} = \\binom{5}{3} = 10$ with $n$ odd. An identity that failed half the time would be no use in shortening a loop.",
                            "The row sum counts all the subsets and says nothing about matching one size against another. Avoiding factorials is achieved by the multiplicative loop itself, whatever number of steps it runs for.",
                        ],
                        "why": r'''
Name a selection of $k$ and you have named its complement of $n-k$, and each complement
comes from one selection, so the two collections are matched one to one and must be
equally large. No algebra is involved and none is needed. The lab's `combinations` applies
`k = min(k, n - k)` first, so $\binom{40}{20}$ costs 20 multiply-divide steps and
$\binom{40}{37}$ costs 3 rather than 37 — the same answer, a third of the arithmetic.
''',
                    },
                ],
            },
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
            "read": {
                "title": "A strip of dominoes, and the sequence that describes itself",
                "minutes": 16,
                "body": r'''
Take a strip of squares two high and $n$ long, and cover it completely with $2 \times 1$
dominoes laid either upright or flat. How many coverings are there?

For $n = 1$ there is one: a single upright domino. For $n = 2$ there are two — two
uprights side by side, or two flat dominoes stacked. For $n = 3$ there are three, and for
$n = 4$ there are five, which you can draw on paper in under a minute. The counts start
1, 2, 3, 5, and anybody who has met a sequence before has already guessed the next one.
Guessing is not the interesting part. Deriving it is.

## The leftmost column decides everything

Look only at the leftmost column of the strip. Whatever the covering, that column is
filled in one of two ways and no others. Either a single upright domino fills it, and what
remains is a strip of length $n - 1$ covered in every possible way; or two flat dominoes
have their left halves there, and what remains is a strip of length $n - 2$. The two cases
cannot both hold of one covering, and no covering escapes them, so Module 7's sum rule
applies with nothing to correct:

$$t(n) = t(n-1) + t(n-2)$$

The starting values come from the same picture. $t(1) = 1$, and $t(0) = 1$ because there
is exactly one way to cover a strip of length zero, namely by laying no dominoes. That
last one is not a convention adopted to make the arithmetic work; it is the empty covering,
counted the same way the empty product is 1.

```python
t = [1, 1]
while len(t) < 11:
    t.append(t[-1] + t[-2])
print("tilings of a 2 x n strip, n = 0..10:", t)
print("t(10) =", t[10])
```

It prints the list `[1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]` and then `t(10) = 89`. Eighty-
nine coverings of a strip ten squares long, obtained without drawing one of them.

## The recurrence on its own determines nothing

Start the same rule at $a_0 = 2$, $a_1 = 1$ and it produces 2, 1, 3, 4, 7, 11, 18, 29, 47,
76, 123 — the Lucas numbers, a different sequence obeying the identical rule. A recurrence
that reaches back $d$ steps needs $d$ initial conditions before it names a sequence at all;
with fewer it names a family. That is worth holding on to, because the algebra below
produces a family first and the initial conditions are what collapse it to one member.

## Why $r^n$ is the shape worth trying

The rule says that each term is a fixed linear combination of the terms before it, and
*fixed* is the operative word: the same coefficients at every $n$. A geometric sequence
$a_n = r^n$ is the one shape whose ratio between consecutive terms is likewise the same at
every $n$, so it is the shape with a chance of satisfying the whole infinite list of
equations at once. Substitute it and see what the demand becomes:

$$r^n = r^{n-1} + r^{n-2}$$

Divide by $r^{n-2}$, which is legitimate for any $r \neq 0$ — and $r = 0$ gives the
all-zero sequence, a solution nobody wants:

$$r^2 = r + 1, \qquad r = \frac{1 \pm \sqrt{5}}{2}$$

The infinitely many equations have become one quadratic. That collapse is the entire
technique, and it happened because the coefficients did not vary with $n$.

Call the roots $\varphi = 1.6180339\ldots$ and $\psi = -0.6180339\ldots$. Both
$\varphi^n$ and $\psi^n$ satisfy the recurrence, and so does every combination
$\alpha\varphi^n + \beta\psi^n$: substitute it, collect the $\alpha$ terms and the $\beta$
terms separately, and each group vanishes because each root satisfies the quadratic. That
is what *linear* buys, and it is why two roots give a two-parameter family exactly
matching the two initial conditions waiting to be met.

## Fitting the constants, with real numbers

Take the Fibonacci start $F(0) = 0$, $F(1) = 1$, which is the same sequence as the
tilings shifted by one place, since $t(n) = F(n+1)$. Then $\alpha + \beta = 0$ and
$\alpha\varphi + \beta\psi = 1$. The first gives $\beta = -\alpha$, and substituting into
the second gives $\alpha(\varphi - \psi) = 1$. The difference of the roots is
$\sqrt{5}$, so $\alpha = 1/\sqrt{5}$ and

$$F(n) = \frac{\varphi^n - \psi^n}{\sqrt{5}}$$

Check it at $n = 11$, where the tiling count says the answer is 89. $\varphi^{11}/\sqrt 5$
is $88.99775\ldots$, and $\psi^{11}/\sqrt 5$ is about $-0.00100$, so the difference is
$89.000$ to three places. Because $|\psi| < 1$ the second term shrinks towards nothing, so
$F(n)$ is the nearest integer to $\varphi^n/\sqrt 5$ for every $n$ — an irrational
expression that is an integer every time, which it must be, since the two roots are
conjugates and their irrational parts cancel.

## The mistake, and why it is tempting

The formula is exact, so evaluate it in floating point and skip the loop. That reasoning is
half right, which is what makes it dangerous.

```python
from math import sqrt

phi = (1 + sqrt(5)) / 2
psi = (1 - sqrt(5)) / 2

fib = [0, 1]
while len(fib) < 80:
    fib.append(fib[-1] + fib[-2])

for n in range(80):
    guess = round((phi ** n - psi ** n) / sqrt(5))
    if guess != fib[n]:
        print("first disagreement at n =", n)
        print("integer recurrence:", fib[n])
        print("closed form in floats:", guess)
        break
```

The first disagreement is at $n = 71$: the recurrence gives 308061521170129 and the
closed form rounds to 308061521170130, one too many. Note where the failure is *not*. A
double holds integers exactly up to $2^{53} \approx 9.0 \times 10^{15}$, and $F(71)$ is
about $3.1 \times 10^{14}$ — comfortably inside that, and $F(n)$ does not reach the limit
until $n = 79$. The damage is done earlier and elsewhere: $\varphi$ itself is stored with a
relative error near $1.1 \times 10^{-16}$, and raising it to the 71st power multiplies that
relative error by about 71, giving roughly $8 \times 10^{-15}$. Against a value of
$3.1 \times 10^{14}$ that is an absolute error of about 2, which is more than enough to
move the rounded result.

The mathematics is exact and the arithmetic is not, and the two claims live in different
places. Exactness of a formula never promises exactness of an evaluation of it.

## A repeated root, and the term that has to be invented

Try $a_n = 4a_{n-1} - 4a_{n-2}$. The characteristic equation is $r^2 - 4r + 4 = 0$, which
is $(r-2)^2$, so 2 is a root twice over and there is only one geometric sequence to be had.
Writing $c_1 2^n + c_2 2^n$ achieves nothing: it is $(c_1 + c_2)2^n$, one constant wearing
two names. With $a_0 = 1$ and $a_1 = 6$ it would need $C = 1$ and $2C = 6$ at the same
time.

A second, independent solution has to come from somewhere, and $n \cdot 2^n$ is it.
Substitute and watch it work:

$$4(n-1)2^{n-1} - 4(n-2)2^{n-2} = 2(n-1)2^{n} - (n-2)2^{n} = \bigl(2n - 2 - n + 2\bigr)2^{n} = n2^{n}$$

Now fit: $c_1 = 1$ from $a_0$, and $2(c_1 + c_2) = 6$ from $a_1$ gives $c_2 = 2$, so
$a_n = (1 + 2n)2^n$.

```python
a = [1, 6]
while len(a) < 12:
    a.append(4 * a[-1] - 4 * a[-2])
closed = [(1 + 2 * n) * 2 ** n for n in range(12)]
print(a == closed, closed[:6])
```

It prints `True [1, 6, 20, 56, 144, 352]`. The extra factor of $n$ is not a trick pulled
out of the air — a degree-$d$ recurrence has $d$ initial conditions to meet, so it needs
$d$ independent building blocks, and a repeated root supplies one where two were required.

## When there is no characteristic equation at all

The Towers of Hanoi puzzle satisfies $T(n) = 2T(n-1) + 1$ with $T(0) = 0$. The $+1$ is not
a multiple of an earlier term, so the substitution above has nothing to collapse. Iterate
instead: 1, 3, 7, 15, 31. The guess is $2^n - 1$, and the guess is all it is — the dots in
an unrolled recurrence are an appeal to a pattern the reader is trusted to continue.
Module 6's induction is what converts it into a theorem: $T(0) = 0 = 2^0 - 1$, and
$T(k+1) = 2(2^k - 1) + 1 = 2^{k+1} - 1$. With 64 discs that is 18446744073709551615 moves,
which is the point of the legend.

## Where the method stops

Four boundaries, and three of them are visible inside this course.

Non-linearity kills it outright: substituting $r^n$ into $a_n = a_{n-1}^2$ gives
$r^n = r^{2n-2}$, an equation that constrains $n$ rather than $r$.

Coefficients that vary with $n$ kill it too. The capstone's `derangements` obeys
$D(n) = (n-1)\bigl(D(n-1) + D(n-2)\bigr)$, whose leading coefficient changes at every
step; its values run 1, 0, 1, 2, 9, 44, 265, 1854, and its closed form,
$n!\sum_{k=0}^{n}(-1)^k/k!$, is not produced by any characteristic polynomial. It gives
$D(4)/4! = 0.375$ against $1/e = 0.36788\ldots$, and the ratio keeps closing.

A divided argument kills it as well. $T(n) = aT(n/b) + f(n)$ decrements nothing, so there
is no power of $r$ to cancel; that shape is priced by summing the cost of each level, which
is the geometric series of Module 12 and the master theorem of the algorithms course.

And a recurrence in two indices is a table rather than a polynomial. The capstone's
`stirling_second` is $S(n,k) = k\,S(n-1,k) + S(n-1,k-1)$ — filled in row by row, with
$S(4,2) = 7$ — and `bell(n)` sums a row of it to give 1, 1, 2, 5, 15, 52, 203.

## What this module asks of you

There is no lab here; the work is on paper and in the quiz, **From a recurrence to a
formula**, which walks the four moves above: read off the characteristic equation, handle
a repeated root, iterate when the shape does not fit, and remember that iteration is a
discovery and induction is the proof. The capstone toolkit then asks for three recurrences
in code — `stirling_second`, `bell` and `derangements` — none of which the characteristic
method solves, which is the honest ratio between the recurrences that have closed forms and
the ones you compute.
''',
            },
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
            "read": {
                "title": "Two cogs, and the remainder that will not go away",
                "minutes": 17,
                "body": r'''
Mesh two cogs, one with 240 teeth and one with 46. Paint a mark on one tooth of each, line
the marks up, and turn. How far do you have to turn before the two marks meet again?

The marks meet when the number of teeth that have passed is a multiple of 240 and of 46 at
once, so the answer is the least common multiple. The whole of this module is packed into
the fact that you cannot compute that by inspection, and that a procedure older than
algebra computes it in five lines.

## Euclid, and why swapping in a remainder loses nothing

Divide the larger by the smaller and keep the remainder:

```python
a, b = 240, 46
while b:
    q, r = divmod(a, b)
    print(f"{a} = {q} * {b} + {r}")
    a, b = b, r
print("gcd =", a)
```

The five lines it prints are $240 = 5 \cdot 46 + 10$, then $46 = 4 \cdot 10 + 6$, then
$10 = 1 \cdot 6 + 4$, then $6 = 1 \cdot 4 + 2$, then $4 = 2 \cdot 2 + 0$, and finally
`gcd = 2`. So the marks meet after $240 \cdot 46 / 2 = 5520$ teeth, and not before.

Why is the answer at the bottom the answer to the question at the top? Take any $d$
dividing both 240 and 46. Since $10 = 240 - 5 \cdot 46$, that same $d$ divides 10. Run it
the other way: any $d$ dividing 46 and 10 divides $5 \cdot 46 + 10 = 240$. So the pair
$(240, 46)$ and the pair $(46, 10)$ have exactly the same set of common divisors — not
merely the same largest one, the same set — and therefore the same greatest element.
Each line of the trace replaces a pair by an easier pair with nothing lost, which is a
stronger statement than "the algorithm works" and is the reason it does.

It also stops. The remainders are non-negative and strictly decreasing, and a strictly
decreasing sequence of non-negative integers cannot run forever. Module 6's induction is
the same observation in its formal dress.

## Running the trace backwards gives an identity for free

Read the five lines from the bottom up, substituting each remainder by the line that
produced it:

$$2 = 6 - 1\cdot 4 = 6 - (10 - 6) = 2\cdot 6 - 10 = 2(46 - 4\cdot 10) - 10 = 2\cdot 46 - 9\cdot 10$$

and one more step, using $10 = 240 - 5 \cdot 46$:

$$2 = 2\cdot 46 - 9(240 - 5\cdot 46) = 47\cdot 46 - 9\cdot 240$$

Check the arithmetic: $47 \cdot 46 = 2162$ and $9 \cdot 240 = 2160$. The gcd of two numbers
is always expressible as an integer combination of them, and the trace exhibits the
combination rather than promising one. That is Bezout's identity, and `extended_gcd(240,
46)` in the lab returns exactly $(2, -9, 47)$.

## The identity is what an inverse is made of

Under a modulus $m$, dividing by $a$ means multiplying by some $x$ with $ax \equiv 1$. Run
the extended algorithm on $a$ and $m$: it returns $x$ and $y$ with $ax + my = g$. If
$g = 1$ then reading that equation modulo $m$ makes the $my$ term vanish and leaves
$ax \equiv 1$ — the inverse, already computed.

The converse closes the case. If some $x$ has $ax \equiv 1 \pmod m$, then $ax - 1$ is a
multiple of $m$, so $ax - km = 1$ for some $k$, and any common divisor of $a$ and $m$
divides the left-hand side and therefore divides 1. So $a$ is invertible modulo $m$ exactly
when $\gcd(a, m) = 1$, with no case left over. Concretely, $3^{-1} \bmod 11$ is 4, because
$3 \cdot 4 = 12 = 11 + 1$; and $6^{-1} \bmod 9$ does not exist, which the lab's
`mod_inverse(6, 9)` reports as a `ValueError` rather than as a wrong number.

## The mistake, and why it is tempting

Cancelling a common factor from both sides of a congruence.

```python
print([(6 * x) % 9 for x in range(9)])
print(6 * 2 % 9, 6 * 5 % 9)
```

The first line prints `[0, 6, 3, 0, 6, 3, 0, 6, 3]` and the second prints `3 3`. Multiplying
by 6 modulo 9 can only ever land on 0, 6 or 3 — the multiples of $\gcd(6, 9) = 3$ — so 1 is
out of reach and there is no inverse to cancel with. And the collision is explicit:
$6 \cdot 2 \equiv 6 \cdot 5 \pmod 9$ while $2 \not\equiv 5$.

Cancellation is tempting because it is the one algebraic reflex that transfers almost
everywhere. It is valid over the rationals, valid over the reals, and valid modulo a prime,
which covers every congruence most people meet before this one. The correct rule keeps a
correction term: from $ac \equiv bc \pmod m$ you may conclude
$a \equiv b \pmod{m/\gcd(c, m)}$. Here that is $2 \equiv 5 \pmod 3$, which is true, and the
weakening from modulus 9 to modulus 3 is exactly the information the illegal cancellation
would have invented.

## The sieve, and the two places it saves work

To list the primes up to a limit, write the numbers down and cross out the multiples of
each prime as you meet it. Two savings turn that into the lab's `sieve`.

Crossing out the multiples of $p$ can start at $p^2$. Any smaller multiple is $kp$ with
$k < p$, so it has a prime factor below $p$, so it was crossed out when that smaller prime
was processed. Running `sieve(30)`, the multiples of 5 begin at 25: the numbers 10, 15 and
20 have already gone, struck out by 2 and by 3.

And the outer loop stops once $p^2$ exceeds the limit. A composite $n$ has a factor no
larger than $\sqrt{n}$ — if both factors exceeded it, their product would exceed $n$ — so
every composite below the limit has been struck by a prime below $\sqrt{\text{limit}}$.
For a limit of 30 that means the loop finishes after 5, and what remains uncrossed is
$[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]$.

## Exponentiation that does not explode

The lab closes on textbook RSA with $p = 61$, $q = 53$, so $n = 3233$, public exponent
$e = 17$, and private exponent $d = $ `mod_inverse(17, 60 * 52)`, which is 2753. Encrypting
the message 65 means computing $65^{17} \bmod 3233$. Computed the direct way, $65^{17}$ is
6599743590836592050933837890625 — 31 digits — and every one of those digits is thrown away
by the final remainder.

Two ideas remove them. Reduce modulo 3233 after every multiplication, so no intermediate
ever exceeds $3233^2$; the remainder of a product depends only on the remainders of its
factors, so nothing is lost. And use the binary expansion of the exponent: $17$ is
`0b10001`, so $x^{17} = x^{16} \cdot x$, and $x^{16}$ is four squarings.

```python
def mod_pow(base, exponent, modulus):
    result = 1 % modulus
    base %= modulus
    steps = 0
    while exponent:
        if exponent & 1:
            result = result * base % modulus
            steps += 1
        exponent >>= 1
        if exponent:
            base = base * base % modulus
            steps += 1
    return result, steps

n, e, d = 3233, 17, 2753
cipher, encrypt_steps = mod_pow(65, e, n)
plain, decrypt_steps = mod_pow(cipher, d, n)
print("cipher", cipher, "in", encrypt_steps, "multiplications")
print("plain", plain, "in", decrypt_steps, "multiplications")
```

It prints `cipher 2790 in 6 multiplications` and `plain 65 in 16 multiplications`. The
message comes back. Sixteen multiplications for an exponent of 2753, against 2752 for the
repeated-multiplication route, and the ratio is what matters: the count grows with the
*number of bits* in the exponent, not with the exponent. A 2048-bit exponent costs a few
thousand multiplications, and the naive route costs a number with 617 digits.

## Where all of this stops holding

Inverses need coprimality, and `mod_inverse` raising on $(6, 9)$ is the module keeping its
own rule. The lab also pins one boundary case that looks like a bug and is not:
`mod_pow(x, 0, 1)` is 0, because every integer is congruent to 0 modulo 1, and the code
gets it right by writing `1 % modulus` rather than `1`.

Fermat's little theorem — $a^{p-1} \equiv 1 \pmod p$ — needs the modulus to be prime, and
the tempting move is to run it backwards as a primality test. It does not close: 561 is
$3 \cdot 11 \cdot 17$, and $2^{560} \equiv 1 \pmod{561}$ all the same. Numbers that fool
the test for every coprime base are called Carmichael numbers, and passing a Fermat test is
evidence rather than proof.

Finally, nothing here says factoring is hard. The lab's `prime_factors` divides out small
primes and is entirely adequate for the numbers in this course; it is hopeless on a
617-digit modulus, and RSA rests on the belief that the gap between "adequate" and
"hopeless" cannot be closed. That belief is unproven, and Module 12's notation will let you
state precisely what is being assumed about it.

## What you are about to build

The lab, **Euclid, inverses, sieves and fast powers**, is the six routines above: `gcd` by
the swap that loses nothing, `extended_gcd` carrying the Bezout coefficients along instead
of recovering them by back-substitution, `mod_inverse` raising when the gcd is not 1,
`sieve` crossing from $p^2$ and stopping when $p^2$ passes the limit, `mod_pow` by
square-and-multiply with a reduction at each step, and `prime_factors` returning the
ascending factorisation with multiplicity, so that `prime_factors(360)` is
$[2, 2, 2, 3, 3, 5]$ — the unique multiset that the fundamental theorem of arithmetic
promises and that every argument above quietly leaned on.
''',
            },
            "quiz": {
                "title": "Divisors, inverses and what a modulus permits",
                "minutes": 8,
                "questions": [
                    {
                        "q": "$6 \\cdot 2 \\equiv 6 \\cdot 5 \\pmod 9$, yet $2 \\not\\equiv 5 \\pmod 9$. What is the correct conclusion from $ac \\equiv bc \\pmod m$?",
                        "opts": [
                            "$a \\equiv b \\pmod m$, provided $c$ is not zero, exactly as over the rationals",
                            "$a \\equiv b \\pmod{m / \\gcd(c, m)}$, so here the modulus drops from 9 to 3",
                            "Nothing at all can be salvaged unless $m$ happens to be prime",
                            "$a \\equiv b \\pmod{mc}$, since multiplying through by $c$ scaled the modulus up",
                        ],
                        "a": 1,
                        "whys": [
                            "A non-zero $c$ is not enough; 6 is non-zero and still uninvertible modulo 9. What cancellation needs is an inverse for $c$, and that needs $\\gcd(c, m) = 1$.",
                            "Divide the modulus by the part of it that $c$ shares, and the cancellation becomes legal.",
                            "A prime modulus makes every non-zero $c$ invertible, so cancellation is unrestricted there — but the general rule holds for any modulus and salvages a genuine conclusion, here $2 \\equiv 5 \\pmod 3$.",
                            "The modulus never grows. A congruence modulo 9 says something about multiples of 9, and no manipulation can turn it into a claim about multiples of 54, which would be strictly more information than was supplied.",
                        ],
                        "why": r'''
Multiplying by 6 modulo 9 lands only on 0, 3 and 6 — the multiples of $\gcd(6, 9) = 3$ — so
6 has no inverse and cancelling it is not a legal move. What survives is
$a \equiv b \pmod{m/\gcd(c, m)}$, which here is $2 \equiv 5 \pmod 3$, and that is true.
The reflex is tempting because cancellation is valid over the rationals, over the reals,
and modulo any prime, which is every setting most people have met. The lost precision —
modulus 9 weakened to modulus 3 — is exactly what the illegal step would have invented.
''',
                    },
                    {
                        "q": "Euclid replaces $\\gcd(240, 46)$ by $\\gcd(46, 10)$. What makes that replacement safe?",
                        "opts": [
                            "The two pairs have the same set of common divisors, since each number is an integer combination of the other pair",
                            "The remainder is smaller, and any procedure whose inputs shrink returns a correct answer",
                            "10 divides both 240 and 46, so it is already a common divisor of the original pair",
                            "The greatest common divisor of two numbers is left unchanged by subtraction, and division with remainder is repeated subtraction",
                        ],
                        "a": 0,
                        "whys": [
                            "Divisor sets are preserved in both directions, so the greatest element is preserved too.",
                            "Shrinking inputs give termination and nothing else. A procedure that replaced the pair by $(1, 1)$ would shrink beautifully and return the wrong answer every time.",
                            "10 divides neither: $240 = 24 \\cdot 10$ but $46 = 4 \\cdot 10 + 6$. The remainder is not claimed to be a common divisor — it is the second entry of an easier pair with the same answer.",
                            "Subtraction does preserve the gcd, and repeated subtraction is what division with remainder compresses. But naming the operation is not the argument; the argument is that divisibility survives it in both directions.",
                        ],
                        "why": r'''
Since $10 = 240 - 5 \cdot 46$, any $d$ dividing 240 and 46 divides 10. Since
$240 = 5 \cdot 46 + 10$, any $d$ dividing 46 and 10 divides 240. The two pairs therefore
share not merely their largest common divisor but their entire set of common divisors, so
the greatest element of that set is the same for both. That is a stronger claim than the
algorithm needs and is the reason it is correct; the strictly decreasing remainders are a
separate argument, and they supply termination rather than correctness.
''',
                    },
                    {
                        "q": "Why can the sieve start crossing out multiples of $p$ at $p^2$ rather than at $2p$?",
                        "opts": [
                            "Because multiples below $p^2$ are rare enough that missing them changes nothing",
                            "Because a multiple $kp$ with $k < p$ has a prime factor below $p$ and was crossed out already",
                            "Because $p^2$ is the first multiple of $p$ that is itself composite, all the earlier multiples being prime",
                            "Because crossing out below $p^2$ would remove $p$ itself, which must survive as a prime",
                        ],
                        "a": 1,
                        "whys": [
                            "Nothing is being approximated. Every composite still gets crossed out exactly as before; the saving is that some of them were crossed out earlier, by a smaller prime.",
                            "Its smaller prime factor did the work when that smaller prime was processed.",
                            "$2p$ is composite for every prime $p$, so this is false at the first multiple it describes. What is special about $p^2$ is that it is the smallest multiple of $p$ with no factor below $p$.",
                            "Crossing conventionally begins at $2p$, which never touches $p$ itself, so the starting point was never in danger of removing it. Starting at $p^2$ is a saving, not a rescue.",
                        ],
                        "why": r'''
Write a multiple of $p$ as $kp$. If $k < p$ then $k$ has a prime factor smaller than $p$,
so $kp$ was struck when that smaller prime was processed. In `sieve(30)` the multiples of 5
begin at 25, because 10, 15 and 20 fell to 2 and 3. The same reasoning bounds the outer
loop: a composite $n$ has a factor no larger than $\sqrt{n}$, so once $p^2$ passes the
limit every composite has already been struck and the survivors are the primes.
''',
                    },
                    {
                        "q": "What connects Bezout's identity to the existence of a modular inverse?",
                        "opts": [
                            "Nothing directly; the inverse is found by trying every residue from 1 to $m-1$ in turn",
                            "$ax + my = 1$ read modulo $m$ leaves $ax \\equiv 1$, so $x$ is the inverse whenever the gcd is 1",
                            "Bezout supplies the modulus $m$, and the inverse is then whichever coefficient turns out to be positive",
                            "It guarantees $a$ and $m$ are coprime, which is what makes every extended-gcd run terminate",
                        ],
                        "a": 1,
                        "whys": [
                            "Exhaustive search does find it and is what the gcd is there to replace — it costs $m$ steps against Euclid's few dozen, and it also gives no reason for the answer to exist.",
                            "The $my$ term vanishes modulo $m$, leaving the defining equation of an inverse.",
                            "The modulus is an input, not something Bezout produces, and the sign of a coefficient decides nothing — a negative $x$ is corrected by taking $x \\bmod m$ at the end.",
                            "Coprimality is a property of the inputs that Bezout detects, never one it guarantees. Termination comes from the strictly decreasing remainders and holds whatever the gcd turns out to be.",
                        ],
                        "why": r'''
The extended algorithm returns $x$ and $y$ with $ax + my = g$. When $g = 1$, reading that
equation modulo $m$ annihilates $my$ and leaves $ax \equiv 1$ — the inverse, already
computed, at the price of one Euclid run. The converse settles the other direction: if
$ax \equiv 1 \pmod m$ then $ax - km = 1$, and every common divisor of $a$ and $m$ divides
1, forcing the gcd to be 1. So invertibility and coprimality are the same condition, which
is why `mod_inverse(6, 9)` raises rather than returning something plausible.
''',
                    },
                    {
                        "q": "Square-and-multiply computed $65^{2753} \\bmod 3233$ in 16 multiplications. What is doing the work?",
                        "opts": [
                            "Reducing at each step, which lowers the number of multiplications needed",
                            "The exponent's binary expansion: the count follows the bit length, not the exponent",
                            "The modulus being a product of two primes, which lets the work be split between them",
                            "Python's unbounded integers, which make the direct computation of $65^{2753}$ equally fast",
                        ],
                        "a": 1,
                        "whys": [
                            "Reduction keeps every intermediate below $3233^2$, which is essential and is a separate saving — the multiplications stay cheap. Their *number* is unchanged by it.",
                            "Twelve bits give eleven squarings and five multiplies, whatever the exponent's size.",
                            "Splitting the work across the two prime factors is a real optimisation and a different one, needing the factorisation of the modulus — which is precisely what the holder of a public key does not have.",
                            "Unbounded integers make the direct computation possible rather than fast. $65^{2753}$ has over 4900 digits, and forming it costs thousands of multiplications on numbers of that size.",
                        ],
                        "why": r'''
2753 is twelve bits long, so the loop squares eleven times and multiplies in the running
result once per set bit — five of them — for sixteen multiplications in total against 2752
for the repeated-multiplication route. The count grows with the number of bits, so a
2048-bit exponent costs a few thousand steps. Reduction at every step is the second,
independent saving: it keeps each of those multiplications between numbers below the
modulus rather than letting a 4900-digit intermediate form, and it is legitimate because
the remainder of a product depends only on the remainders of its factors.
''',
                    },
                ],
            },
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
            "read": {
                "title": "Four cities, and the question the timetable does not answer",
                "minutes": 17,
                "body": r'''
A small airline publishes four direct flights: Aberdeen to Bristol, Bristol to Dundee,
Dundee to Cardiff, and Cardiff to Bristol. A passenger in Aberdeen asks whether she can get
to Cardiff. The timetable does not say. It answers a different question — *is there a
direct flight* — and she is asking *is there any route at all*.

Both questions are about the same object. The timetable is a set of ordered pairs of
cities, and that is the whole of what a **relation** is: a subset of $S \times S$, with no
further structure demanded or implied. The route question asks for a different subset of
the same $S \times S$, and the rest of this module is about getting from the first to the
second.

## The properties are quantified sentences, not adjectives

Module 2 gave you the vocabulary, so the definitions can be written down rather than
described. Over a ground set $S$, a relation $R$ is

reflexive when $\forall x\, R(x,x)$; symmetric when
$\forall x\,\forall y\,\bigl(R(x,y) \to R(y,x)\bigr)$; antisymmetric when
$\forall x\,\forall y\,\bigl(R(x,y) \wedge R(y,x) \to x = y\bigr)$; and transitive when
$\forall x\,\forall y\,\forall z\,\bigl(R(x,y) \wedge R(y,z) \to R(x,z)\bigr)$.

Every one of them is a claim about *all* of $S$, and that is the detail the next section
turns on. The flight relation above is none of the four: no city has a flight to itself,
Aberdeen to Bristol has no return, and Aberdeen reaches Cardiff by no direct flight while
reaching it by two hops.

A relation with all of reflexive, symmetric and transitive is an **equivalence**, and it
carves $S$ into disjoint classes — "reachable from" will be one once the flights are made
two-way, and the components of the lab's `two_colouring` are exactly those classes.

## The mistake, and why it is tempting

Here is an argument that symmetry and transitivity together force reflexivity. Take any
$x$. Since $R$ is symmetric, from $R(x,y)$ we get $R(y,x)$; since it is transitive,
$R(x,y)$ and $R(y,x)$ give $R(x,x)$. Reflexivity, apparently, for free.

Every step in that argument is valid, which is precisely why it is convincing. What is
wrong is the very first sentence: it says "take any $x$" and then immediately helps itself
to a $y$ with $R(x,y)$. Nothing supplies that $y$. The argument establishes $R(x,x)$ for
every $x$ that is related to *something*, and reflexivity is a claim about every $x$
whatsoever.

```python
GROUND = [1, 2, 3]
R = {(1, 1), (1, 2), (2, 1), (2, 2)}
symmetric = all((b, a) in R for (a, b) in R)
transitive = all((a, d) in R for (a, b) in R for (c, d) in R if b == c)
reflexive = all((x, x) in R for x in GROUND)
print("symmetric", symmetric, "transitive", transitive, "reflexive", reflexive)
print("missing:", [(x, x) for x in GROUND if (x, x) not in R])
```

It prints `symmetric True transitive True reflexive False`, and then `missing: [(3, 3)]`.
Element 3 is related to nothing at all, so the argument never reaches it, and one isolated
element is enough to sink the claim. This is Module 2's lesson in a new costume: a
quantifier ranges over the domain that was declared, including the parts of it nobody
mentioned.

It also explains why the lab passes `elements` separately from `pairs`. A relation given
only by its pairs cannot know that 3 exists, so `is_reflexive` would report `True` on a
ground set it had never been told about.

## Reachability is transitivity, added in

The passenger's question asks for the smallest transitive relation containing the
timetable — smallest, because adding routes nobody can fly would answer a different
question. That such a thing exists is worth a sentence: the intersection of any collection
of transitive relations is transitive, and $S \times S$ is transitive and contains $R$, so
the intersection of all transitive relations containing $R$ is itself one, and it is
contained in every other. The **transitive closure** is that intersection, and it is unique.

The direct way to build it is to apply the rule and see what appears. Do that once, to the
pairs originally given:

```python
FLIGHTS = {(0, 1), (1, 3), (3, 2), (2, 1)}
one_round = FLIGHTS | {(a, d) for (a, b) in FLIGHTS for (c, d) in FLIGHTS if b == c}
rounds, current = 0, set(FLIGHTS)
while True:
    grown = current | {(a, d) for (a, b) in current for (c, d) in current if b == c}
    rounds += 1
    if grown == current:
        break
    current = grown
print("one round gives", len(one_round), "pairs")
print("the fixed point gives", len(current), "pairs, after", rounds, "rounds")
print("missing after one round:", sorted(current - one_round))
```

One round gives 8 pairs; the answer has 12. The four it misses are $(0,2)$ — Aberdeen to
Cardiff, the passenger's own question, which needs three hops — and $(1,1)$, $(2,2)$,
$(3,3)$, the self-loops that exist because Bristol, Dundee and Cardiff sit on a cycle and
each can be left and returned to. The loop reports three rounds, the third of which changed
nothing and served to prove there was nothing left to change.

That is the honest way to say what goes wrong with applying the rule once: a two-hop route
built by the rule is itself a pair, and the rule has to be offered the chance to build on
it. Iterating to a fixed point is correct, and its cost is a number of rounds nobody knew
in advance.

## Warshall: one pass, because of the order

Warshall's algorithm reaches the same fixed point in a single sweep, and the reason is an
ordering choice rather than a trick. Number the cities $0$ to $n-1$ and define the
invariant: after the outer loop has finished with $k$, the matrix entry $(i, j)$ is true
exactly when there is a route from $i$ to $j$ whose **intermediate** stops all lie in
$\{0, \dots, k\}$.

Induction on $k$, in Module 6's pattern. Before the loop starts the only routes with no
intermediate stops at all are the direct flights, which is the matrix as given. Now suppose
the invariant holds after $k-1$ and consider a route from $i$ to $j$ whose intermediates
lie in $\{0, \dots, k\}$. Either it never visits $k$, in which case its intermediates lie in
$\{0, \dots, k-1\}$ and the entry is already true; or it visits $k$, and it may be assumed
to visit it once, since a second visit encloses a loop that can be cut out. Then the route
splits at $k$ into a leg $i \to k$ and a leg $k \to j$, each with intermediates in
$\{0, \dots, k-1\}$, so both are already recorded, and the $k$-th pass sets $(i, j)$ from
them. When $k$ reaches $n-1$ the permitted intermediates are every city, and the invariant
says the matrix is the closure.

```python
CITIES = ["Aberdeen", "Bristol", "Cardiff", "Dundee"]
FLIGHTS = [(0, 1), (1, 3), (3, 2), (2, 1)]

reach = [[False] * 4 for _ in range(4)]
for i, j in FLIGHTS:
    reach[i][j] = True

for k in range(4):
    added = []
    for i in range(4):
        if reach[i][k]:
            for j in range(4):
                if reach[k][j] and not reach[i][j]:
                    reach[i][j] = True
                    added.append(CITIES[i] + " to " + CITIES[j])
    print("via", CITIES[k] + ":", added)
print("pairs in the closure:", sum(row.count(True) for row in reach))
```

Allowing Aberdeen as an intermediate adds nothing, since no flight lands there. Bristol
adds Aberdeen to Dundee and Cardiff to Dundee. Cardiff adds Dundee to Bristol and Dundee to
Dundee. Dundee, last, adds four more, among them Aberdeen to Cardiff. Twelve pairs, one
sweep.

Watch what happened at the third step: Dundee to Dundee was added using Cardiff as an
intermediate, and Cardiff to Dundee had been added one step earlier. The passes are not
independent — each one is entitled to the results of the previous ones, and that
entitlement is what the invariant licenses. Move $k$ from the outermost loop to the
innermost and the invariant has nothing to say; on the three-city cycle
$1 \to 3 \to 2 \to 1$ that variant finishes without recording that Bristol is reachable
from Bristol, and a second pass is needed to repair it.

The inner line runs $n^3$ times exactly — 64 times for these four cities, whatever the
flights are — because none of the three loops depends on the data. Module 12 turns that
count into the notation the rest of the degree writes it in.

## Colouring, and the cycles that forbid it

Make the flights two-way and ask a different question: can the cities be split into two
groups so that every flight crosses between them? Try to build the split greedily. Put the
first city in group 0, everything it connects to in group 1, everything those connect to in
group 0, and continue.

Along any route the group alternates, so two cities joined by a route of even length are in
the same group and by a route of odd length in different groups. A cycle is a route from a
city back to itself, and a city is in the same group as itself, so every cycle must have
even length. That is the obstruction, derived rather than quoted: a graph with an odd cycle
cannot be split. And when there is no odd cycle the greedy construction never contradicts
itself, so the split exists. A triangle fails; a square succeeds.

## Where these tools stop

The closure of a relation can lose a property the relation had. Take $\{(1,2), (2,3),
(3,1)\}$, which is antisymmetric — no pair appears with its reverse. Its transitive closure
is all nine pairs on $\{1,2,3\}$, which is as far from antisymmetric as a relation can get.
Closure adds what transitivity demands and makes no promises about anything else.

Warshall answers *whether*, never *how far*. Replace the boolean and-or by minimum and
addition and the same three loops compute shortest distances instead, which is the
Floyd-Warshall algorithm, but the version in this module has thrown that information away.

The $n^3$ is a cost as well as a guarantee. At 5000 cities it is $1.25 \times 10^{11}$
inner steps and $n^2$ booleans of memory, and for a sparse network a traversal from each
vertex is far cheaper. The dense matrix is the right tool when the relation is dense and
the wrong one when it is not.

And two-colouring is a question about **undirected** graphs. On a directed timetable the
question does not arise, and on a disconnected undirected graph the colouring is not unique
— each component may be flipped independently — which is why the lab fixes the component
order and starts every component at colour 0, so that a correct implementation returns one
particular answer rather than any valid one.

## What you are about to build

The lab, **Relation properties, Warshall and bipartiteness**, works through all of it:
`to_matrix` turning pairs into the boolean matrix and raising on a pair mentioning
something outside the ground set; `is_reflexive`, `is_symmetric`, `is_transitive` and
`is_equivalence` reading the quantified sentences above straight into code; `warshall`
returning a **new** matrix with the caller's left untouched, since a closure that destroys
its input cannot be compared against it; `transitive_closure` going out through the matrix
and back to a set of pairs; and `two_colouring` and `is_bipartite` deciding the split, with
`None` returned exactly when an odd cycle is found.
''',
            },
            "quiz": {
                "title": "Pairs, closures and the order of three loops",
                "minutes": 8,
                "questions": [
                    {
                        "q": "From $R(x,y)$, symmetry gives $R(y,x)$, and transitivity then gives $R(x,x)$. Why does that not prove every symmetric transitive relation reflexive?",
                        "opts": [
                            "Because transitivity requires three distinct elements, and $x$, $y$, $x$ repeats one",
                            "Because it establishes $R(x,x)$ only for those $x$ related to something, and an isolated element has no such $y$",
                            "Because symmetry and transitivity are properties of the pairs, while reflexivity is a property of the ground set",
                            "Because the argument silently assumes the relation is already reflexive at $y$",
                        ],
                        "a": 1,
                        "whys": [
                            "Transitivity is stated with three quantified variables and nothing forbids them from coinciding; instantiating $z$ as $x$ is a legitimate use of a universal statement, and every step of the argument really is valid.",
                            "The $y$ has to come from somewhere, and for an isolated element there is none.",
                            "Reflexivity does quantify over the ground set, which is why the lab passes `elements` separately — but symmetry and transitivity quantify over it as well. The defect is a missing witness, not a difference in what the three properties range over.",
                            "Nothing about $y$ is assumed beyond $R(x,y)$, and $R(y,y)$ is never used. The gap is earlier: the argument needs some $y$ to exist before it can begin.",
                        ],
                        "why": r'''
Every inference in the argument is sound; the flaw is in what it starts from. It proves
$R(x,x)$ for each $x$ that is related to at least one thing, and reflexivity is a claim
about every element of the ground set. On $\{1,2,3\}$ the relation
$\{(1,1),(1,2),(2,1),(2,2)\}$ is symmetric and transitive with $(3,3)$ absent, because 3 is
related to nothing and the argument never reaches it. This is why the lab takes `elements`
as its own argument: a relation given only by its pairs cannot know that 3 exists.
''',
                    },
                    {
                        "q": "Applying the rule \"if $(a,b)$ and $(b,c)$ then add $(a,c)$\" once to the given pairs produced 8 pairs where the closure has 12. What was missed?",
                        "opts": [
                            "Pairs whose route is longer than two hops, since a newly added pair can itself start a new route",
                            "Pairs involving a vertex of the ground set that appears in no given pair at all",
                            "Pairs in the reverse direction, which transitivity adds along with the forward ones",
                            "Nothing at all was missed; the four extra pairs come from imposing reflexivity rather than from transitivity",
                        ],
                        "a": 0,
                        "whys": [
                            "A pair the rule creates is itself eligible to be combined again, and one round never offers it that chance.",
                            "An isolated vertex gains no pairs under transitivity at all — nothing reaches it and it reaches nothing — so it is not what the second round adds.",
                            "Transitivity says nothing about direction and adds no reverses; that is symmetry, a different property, and the closure here is emphatically not symmetric.",
                            "Reflexivity is not being imposed. The self-loops that appear are earned: Bristol, Cardiff and Dundee lie on a cycle, so each really can be left and returned to, while Aberdeen gains no self-loop.",
                        ],
                        "why": r'''
One round combines only the pairs it was handed. Aberdeen to Cardiff needs three hops, so
it can be assembled solely from a two-hop pair the first round created, and the three
self-loops need a full trip round the cycle. Feeding the output back in until nothing
changes is correct and takes an unknown number of rounds — three here, the last confirming
that the set had stopped growing. Warshall's contribution is to reach the same set in one
sweep with a known cost.
''',
                    },
                    {
                        "q": "In Warshall's algorithm the intermediate vertex $k$ is the outermost loop. What does that ordering buy?",
                        "opts": [
                            "It lets the algorithm stop early as soon as a pass adds nothing, which the other loop orderings cannot detect",
                            "It reduces the inner line's executions from $n^3$ to $n^2 \\log n$ by skipping unreachable vertices",
                            "It maintains the invariant that after pass $k$ the matrix records routes with intermediates in $\\{0..k\\}$",
                            "It guarantees the caller's matrix is not modified, since $k$ is read before $i$ and $j$ are written",
                        ],
                        "a": 2,
                        "whys": [
                            "Stopping early is available to any fixed-point loop and is exactly what the repeated-rule version does. Warshall does not stop early — it runs all $n$ passes — and the point is that $n$ passes are all it ever needs.",
                            "The inner line runs $n^3$ times whatever the data, because no loop bound depends on the matrix. That fixed count is a feature of the algorithm, and no reordering of the loops changes it.",
                            "Each pass may use the previous passes' results, and the induction on $k$ is what makes one sweep enough.",
                            "Leaving the input untouched is achieved by copying the matrix first, and the lab requires it for that reason. Loop order has no bearing on which object is written to.",
                        ],
                        "why": r'''
After the pass for $k$, entry $(i,j)$ is true exactly when a route runs from $i$ to $j$
using intermediates drawn from $\{0, \dots, k\}$. The induction is short: such a route
either avoids $k$, and was recorded earlier, or passes through it once — a second visit
encloses a removable loop — and splits into two legs whose intermediates lie in
$\{0, \dots, k-1\}$, both already recorded. So each pass is entitled to the earlier passes'
work, which is what makes a single sweep enough. Move $k$ inside and that entitlement
disappears: on the cycle $1 \to 3 \to 2 \to 1$ the reordered version fails to record that 1
reaches itself.
''',
                    },
                    {
                        "q": "What does *smallest* mean in \"the transitive closure is the smallest transitive relation containing $R$\", and why is there one?",
                        "opts": [
                            "Smallest in the number of pairs, found by trying each candidate and keeping the shortest",
                            "Smallest by containment: it sits inside every transitive relation containing $R$, being their intersection",
                            "Smallest in the number of vertices it mentions, which is why isolated elements are dropped",
                            "There need not be one at all; several minimal transitive relations can contain $R$, and Warshall returns one of them",
                        ],
                        "a": 1,
                        "whys": [
                            "Counting pairs would leave the notion resting on a search, and it is not what makes the object well defined. Fewest pairs happens to coincide with the intersection here, but containment is the property the argument actually uses.",
                            "An intersection of transitive relations is transitive, so the intersection of all of them containing $R$ is the least one.",
                            "The closure mentions exactly the ground set it was given, isolated elements included; it adds pairs and removes none. Nothing about vertices is being minimised.",
                            "Uniqueness is not in doubt: the intersection of all the candidates is itself a candidate, so it is the one and only least element rather than one of several incomparable minimal ones.",
                        ],
                        "why": r'''
Order the candidates by containment. $S \times S$ is transitive and contains $R$, so
candidates exist; and an intersection of transitive relations is transitive, because a
pair chain lying in every one of them forces the closing pair to lie in every one of them.
So the intersection of all transitive relations containing $R$ is itself transitive,
contains $R$, and is inside each of them — a least element, not merely a minimal one.
That is what makes "the" closure a definite object rather than a choice, and it is what
Warshall computes.
''',
                    },
                    {
                        "q": "Why is a graph two-colourable exactly when it contains no odd cycle?",
                        "opts": [
                            "Because colours alternate along every walk, so a closed walk returning to its start must have even length",
                            "Because an odd cycle contains more edges than it has vertices, and a graph with that imbalance needs a third colour",
                            "Because a greedy colouring visits vertices in sorted order, and an odd cycle breaks that order",
                            "Because every odd cycle contains a triangle, and a triangle plainly needs three colours",
                        ],
                        "a": 0,
                        "whys": [
                            "Alternation forces equal colours at even distance and different colours at odd, and a cycle demands both at once when its length is odd.",
                            "A cycle has exactly as many edges as vertices, odd or even, so this counts nothing — and a 4-cycle has the same balance while colouring in two.",
                            "Sorted order makes the lab's answer deterministic among the valid colourings and nothing more. A bipartite graph two-colours under every visiting order; an odd cycle defeats all of them.",
                            "A 5-cycle contains no triangle and still cannot be two-coloured, so triangles are not what is doing the work. What every odd cycle shares is its parity, not a smaller cycle inside it.",
                        ],
                        "why": r'''
In any two-colouring the colour flips along each edge, so vertices joined by a walk of even
length share a colour and vertices joined by an odd walk do not. A cycle is a walk from a
vertex to itself, and a vertex shares its own colour, so every cycle must be even. That
rules out the odd ones. In the other direction, colouring by distance parity from a start
vertex, one component at a time, only ever conflicts where two vertices at the same parity
are adjacent, and that adjacency closes an odd cycle. The lab's `two_colouring` returns
`None` in exactly that case.
''',
                    },
                ],
            },
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
            "read": {
                "title": "Counting cable ends, and the graph that cannot exist",
                "minutes": 17,
                "body": r'''
Six machines are sitting in an office with cables between them, and somebody needs to know
how many cables there are. Rather than trace them, walk to each machine and count the
cables plugged into it: A has 2, B has 3, C has 3, D has 2, E has 3, F has 1.

That is 14. There are 7 cables.

```python
EDGES = [("A", "B"), ("A", "C"), ("B", "C"), ("B", "D"),
         ("C", "E"), ("D", "E"), ("E", "F")]
degree = {v: 0 for v in "ABCDEF"}
for u, v in EDGES:
    degree[u] += 1
    degree[v] += 1
print("degrees:", degree)
print("sum:", sum(degree.values()), "= twice", len(EDGES), "edges")
print("odd degrees:", sorted(v for v in degree if degree[v] % 2))
```

The halving is not a coincidence and not an approximation. Count the pairs *(machine, cable
end plugged into it)*. Each machine contributes its own degree, so the total is
$\sum_v \deg(v)$. Each cable contributes exactly two ends, so the total is $2|E|$. One
collection of objects counted two ways — Module 7's technique, applied to hardware:

$$\sum_{v} \deg(v) = 2|E|$$

## What the parity forbids

The right-hand side is even, so the left-hand side is even, so the odd degrees must pair
off. Here they do: B, C, E and F have odd degree, and four is even. A wiring plan for six
machines in which exactly five have an odd number of cables is therefore not a plan that
needs checking — it is a plan that cannot be built, whatever the other machine does. That
is a parity argument ruling out a whole class of configurations before any construction is
attempted, and it costs one line.

The same accounting settles Euler's question. A closed walk that uses every cable exactly
once enters a machine and leaves it, consuming two cable ends each time it passes through,
and the start is also the finish, so its ends pair up too. Every degree must therefore be
even. Königsberg's four landmasses had degrees 3, 3, 3 and 5, and that is the whole of the
proof that the famous walk is impossible — no search, no case analysis.

## Components, from Module 10's machinery

Define $u \sim v$ to mean that some walk runs from $u$ to $v$. It is reflexive, by the walk
of length zero; symmetric, because an undirected walk read backwards is a walk; and
transitive, because two walks meeting at a vertex concatenate into one. So it is an
equivalence relation, and Module 10 showed that an equivalence partitions its ground set
into disjoint classes. Those classes are the **connected components**, and the capstone's
`connected_components` computes exactly them. Connectivity is not a new idea in this
course; it is a relation whose properties were established a module ago.

## A tree, four ways, and one of them derived

Four descriptions pick out the same graphs: connected and acyclic; connected with $n-1$
edges; acyclic with $n-1$ edges; and a unique path between every pair of vertices. The
useful form is that any two of *connected*, *acyclic* and *$n-1$ edges* force the third.

Derive one of the links. Claim: a connected acyclic graph on $n \geq 2$ vertices has a
vertex of degree 1. Take a path of maximum length and look at one end, $v$. If $v$ had a
neighbour off the path, the path could be extended, contradicting maximality. If $v$ had a
second neighbour on the path, that neighbour together with the path between them closes a
cycle, and there are none. So $v$ has exactly one neighbour: a leaf.

Now induct, in Module 6's pattern. A tree on 1 vertex has 0 edges. Given a tree on $n$
vertices, remove a leaf and its single edge: what remains is still connected, since the
leaf was on no path between other vertices, and still acyclic, so by the inductive
hypothesis it has $n - 2$ edges, and putting the leaf back gives $n - 1$. The count is not
a definition; it is a consequence of having no cycles and staying in one piece.

The office graph has 6 machines and 7 cables, two more than a tree, and those two extra
cables are what the two cycles cost — $A\!-\!B\!-\!C\!-\!A$ and $B\!-\!C\!-\!E\!-\!D\!-\!B$.
Every connected graph contains a **spanning tree**, and the argument is a procedure: while
a cycle remains, delete any edge on it. Connectivity survives each deletion, because the
two endpoints of the deleted edge are still joined by the rest of that cycle. The process
stops, because each step removes an edge. What is left is connected and acyclic.

How many trees are there on $n$ labelled vertices? The answer is $n^{n-2}$, which is worth
verifying rather than believing:

```python
from itertools import combinations

def is_tree(n, edges):
    parent = list(range(n))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for u, v in edges:
        ru, rv = find(u), find(v)
        if ru == rv:
            return False
        parent[ru] = rv
    return True

for n in (3, 4, 5):
    slots = list(combinations(range(n), 2))
    count = sum(1 for pick in combinations(slots, n - 1) if is_tree(n, pick))
    print("n =", n, "labelled trees:", count, "and n^(n-2) =", n ** (n - 2))
```

It prints 3 and 3, then 16 and 16, then 125 and 125. The check works by taking every set of
$n-1$ edges and keeping the acyclic ones — using two of the equivalences at once, since
acyclic with $n-1$ edges is enough.

## Colouring, and the bound greedy cannot beat

Give every machine a radio channel so that no two machines joined by a cable share one.
Colour them one at a time, each time taking the lowest-numbered channel none of its already
coloured neighbours is using. A machine has at most $\Delta$ neighbours, where $\Delta$ is
the largest degree, so among $\Delta + 1$ channels one is always free. Greedy therefore
never needs more than $\Delta + 1$, and the office graph, with $\Delta = 3$, needs at most
4. It in fact needs 3, because the triangle $A\!-\!B\!-\!C$ forces three and the assignment
$A, D, F \to 0$, $B, E \to 1$, $C \to 2$ uses three.

## The mistake, and why it is tempting

The mistake is reading greedy's answer as the chromatic number.

```python
CYCLE = {
    "a1": ["b2", "b3"], "a2": ["b1", "b3"], "a3": ["b1", "b2"],
    "b1": ["a2", "a3"], "b2": ["a1", "a3"], "b3": ["a1", "a2"],
}

def greedy(order):
    colour = {}
    for v in order:
        used = {colour[w] for w in CYCLE[v] if w in colour}
        c = 0
        while c in used:
            c += 1
        colour[v] = c
    return colour

for name, order in [("alternating", ["a1", "b1", "a2", "b2", "a3", "b3"]),
                    ("one side first", ["a1", "a2", "a3", "b1", "b2", "b3"])]:
    print(name, "uses", max(greedy(order).values()) + 1, "colours")
```

It prints `alternating uses 3 colours` and `one side first uses 2 colours`. The graph is a
six-cycle — follow $a_1, b_2, a_3, b_1, a_2, b_3$ and back to $a_1$ — so it is bipartite and
two colours are enough. One ordering finds that and the other spends three.

The reason this is tempting is that greedy never produces anything *wrong*. Its output is a
proper colouring every time, with no conflicting pair anywhere to inspect, so there is no
symptom. And 3 is a defensible-looking answer: $\Delta = 2$ here, the bound $\Delta + 1$ is
3, and the bound is genuinely attained — by complete graphs and by odd cycles. A graph that
happens to be an even cycle looks, from the answer alone, exactly like one that is not.

What greedy gives is an upper bound, and one that depends on the order it visited. What the
chromatic number needs is a claim about *every* colouring, and that is a claim about all
$k$-colourings at once, which no single run produces.

## Where all of this stops

The bound $\Delta + 1$ is loose almost everywhere. Brooks' theorem tightens it to $\Delta$
for every connected graph other than a complete graph and an odd cycle, and even that is an
upper bound: a star on 100 vertices has $\Delta = 99$ and chromatic number 2. Computing the
chromatic number exactly is NP-hard, so no rule for ordering the vertices turns greedy into
an exact method, and the algorithms course returns to what that phrase means.

The handshake lemma is necessary and not sufficient. The degree sequence $3, 3, 3, 1$ sums
to 10, which is even, and no graph on four vertices has it: a vertex of degree 3 among four
is joined to all the others, so three such vertices leave the fourth joined to all three,
with degree 3 rather than 1. Parity is a filter, not a construction, and the full condition
for a sequence to be realisable is a separate theorem.

Cayley's $n^{n-2}$ counts **labelled** trees, where the vertices are told apart. Forget the
labels and the count collapses: there are $6^4 = 1296$ labelled trees on six vertices and
six distinct shapes. Nearly every counting question in this course is about labelled
objects, and it is worth noticing each time which one is being asked.

And all four tree characterisations assume a finite simple graph. Allow infinitely many
vertices and "connected and acyclic" survives while "$n-1$ edges" has nothing to say.

## What to do with this module

There is no lab here. The work is in this module's quiz, **Degrees, trees and chromatic
numbers**, which turns each of the arguments above into a question, and in the code you
have already written or are about to: Module 10's lab, **Relation properties, Warshall and
bipartiteness**, supplies `two_colouring` and `is_bipartite`, and the capstone toolkit asks
for `connected_components` alongside them — the components being, as above, the classes of
an equivalence relation you met before you met graphs.
''',
            },
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

$$S - rS = 1 - r^{n+1} \qquad \Rightarrow \qquad S = \frac{1 - r^{n+1}}{1 - r}$$

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

$$1 \;+\; \tfrac{1}{2} \;+\; \left(\tfrac{1}{3} + \tfrac{1}{4}\right) \;+\; \left(\tfrac{1}{5} + \tfrac{1}{6} + \tfrac{1}{7} + \tfrac{1}{8}\right) \;+\; \cdots$$

The blocks after the leading 1 hold 1, 2, 4, 8, ... terms, each block ending at a power
of two. Every term in a block is at most the block's first and greater than its last. The
block
of 4 terms starting at $1/5$ therefore sums to at most $4 \times \tfrac{1}{4} = 1$ and more
than $4 \times \tfrac{1}{8} = \tfrac{1}{2}$. Each block contributes between $\tfrac{1}{2}$ and $1$,
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
more for each bit that is set. Write $b$ for the number of bits in $e$, so the whole cost
is at most $2b$. A number needs one more bit than the largest power of two below it, so
$b \le \log_2 e + 1$, and $\log_2 e + 1 \le 2\log_2 e$ exactly when $\log_2 e \ge 1$ —
that is, when $e \ge 2$. Chaining those gives $2b \le 4\log_2 e$: witnesses $c = 4$,
$n_0 = 2$. For $e = 1000$ the exponent has 10 bits, so that is at most 20 multiplications where
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
                        "hint": r"$1 - \tfrac{1}{2} = \tfrac{1}{2}$, and $1$ divided by $\tfrac{1}{2}$ is not $\tfrac{1}{2}$.",
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
bijection from $\mathbf{N} \times \mathbf{N}$ onto $\mathbf{N}$ — two coordinates encoded
in one number with nothing lost and nothing repeated.

From there the results come quickly. A countable union of countable sets is countable:
index the sets by $i$ and their members by $j$, and $\pi(i, j)$ lists the union. The
positive rationals are countable, because $p/q$ is a pair, so they inject into the pairs;
duplicates like $2/4$ are dropped by keeping only lowest terms, and a subset of a
countable set is countable. Add the negatives by interleaving and $\mathbf{Q}$ is
countable — a set that is dense, so that between any two rationals lie infinitely many
more, is nevertheless no bigger than $\mathbf{N}$. That is the first sign that "same
size" carries less information than intuition expects it to.

And the finite strings over a finite alphabet are countable: list them by length, and
alphabetically within each length. Every string of length $k$ appears after fewer than
$2^{k+1}$ others. This is the one to remember, because a program *is* a finite string
over a finite alphabet. **There are only countably many programs.**

## The argument that cannot be beaten

Now consider the infinite bit strings: functions from $\mathbf{N}$ to `{0, 1}`. Are
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

The other limit is a limit on what countability tells you. $\mathbf{N}$ and $\mathbf{Q}$
are the same size while being utterly unalike in order and density; "same size" was
defined by bijection alone, and a bijection is free to shatter every other structure the
sets carry. It is a coarse notion deliberately, and reading more into it than it says is
its own error.

## What this is for

A language over `{0,1}` is a set of strings, that is, a subset of a countably infinite
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
The sweep that lists $\mathbf{N} \times \mathbf{N}$ takes the diagonals $x + y = 0$,
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
individual string's length; the finite-position sequences $\mathbf{N} \to \mathbf{N}$
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
