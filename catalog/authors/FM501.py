"""FM501 — Formal Methods & Program Verification."""

COURSE = {
    "id": "FM501",
    "title": "Formal Methods & Program Verification",
    "year": 5,
    "level": "Expert",
    "prereqs": ["CS310", "CS330"],
    "stack": ["Python", "Z3 / Dafny (reference)"],
    "credits": 10,
    "hours": 150,
    "icon": "⊨",
    "summary": (
        "Programs are mathematical objects, and this course treats them as such. You build "
        "the four engines that industrial verification rests on — a DPLL satisfiability "
        "solver, a weakest-precondition calculator, an explicit-state model checker and a "
        "property-based testing framework with shrinking — and then apply all three "
        "verification styles to one data structure to see exactly what each one can and "
        "cannot catch."
    ),
    "outcomes": [
        "Convert an arbitrary propositional formula to conjunctive normal form and decide it with DPLL",
        "Explain why unit propagation and pure-literal elimination change the complexity in practice, not in theory",
        "Compute weakest preconditions for assignment, sequencing, conditionals and assertions",
        "State a loop invariant and discharge the two verification conditions it generates",
        "Model a concurrent protocol as a Kripke structure and extract a counterexample trace",
        "Build generators and shrinkers that reduce a random failure to a minimal one",
        "Choose deliberately between deductive proof, model checking and testing for a given obligation",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Huth & Ryan, *Logic in Computer Science: Modelling and Reasoning about Systems*, 2nd ed. — chapters 1-3",
        "Clarke, Grumberg, Kroening, Peled & Veith, *Model Checking*, 2nd ed. — chapters 2-4",
        "Biere, Heule, van Maaren & Walsh (eds), *Handbook of Satisfiability*, 2nd ed. — chapter 3 (CDCL)",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Propositional reasoning and DPLL",
            "summary": "From an arbitrary formula to clauses, and from clauses to a decision.",
            "concepts": [
                "Syntax versus semantics: a formula, a valuation, and the satisfaction relation ⊨",
                "Negation normal form, then distribution of ∨ over ∧ to reach CNF",
                "Clause form: a set of clauses, each a set of literals; the empty clause is false, the empty set is true",
                "Davis-Putnam-Logemann-Loveland: propagate, eliminate, split, backtrack",
                "Unit propagation is the Boolean constraint propagation that makes SAT tractable in practice",
                "Pure-literal elimination is sound because a pure literal can always be set true",
                "Validating an optimised solver against exhaustive enumeration on random instances",
            ],
            "lab": {
                "title": "CNF conversion and a DPLL solver",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
A formula is a nested tuple. A variable is a lowercase name.

```text
("var", "p")            p
("not", f)              ¬f
("and", f, g)           f ∧ g
("or",  f, g)           f ∨ g
("imp", f, g)           f → g
("iff", f, g)           f ↔ g
```

A **literal** is the string `"p"` or `"-p"`. A **clause** is a `frozenset` of
literals, read disjunctively. A **CNF** is a list of clauses, read conjunctively.

Implement five functions.

**`to_nnf(f)`** — negation normal form: no `imp`, no `iff`, and every `not`
applied directly to a variable. Use `f → g ≡ ¬f ∨ g`, `f ↔ g ≡ (f → g) ∧ (g → f)`,
De Morgan, and double-negation elimination. Raise `ValueError` for an unknown
connective.

**`to_cnf(f)`** — the clause list. Convert to NNF first, then distribute:
`a ∨ (b ∧ c) ≡ (a ∨ b) ∧ (a ∨ c)`.

```text
to_cnf(("or", ("var", "p"), ("and", ("var", "q"), ("var", "r"))))
    ->  [{"p", "q"}, {"p", "r"}]      as frozensets, in any order
```

**`satisfies(clauses, model)`** — does the model, a dict from variable name to
`bool`, satisfy every clause?

**`brute_force(clauses)`** — the reference decision procedure: try all `2^n`
valuations in order and return the first satisfying model, or `None`.

**`dpll(clauses)`** — the same verdict, computed properly. Loop over unit
propagation and pure-literal elimination until neither applies, then split on a
variable and recurse. Return a model that gives a value to **every** variable of
the input (unconstrained variables may be `False`), or `None` when unsatisfiable.

An empty clause list is satisfiable by the empty model. A clause list containing
the empty clause is unsatisfiable.
''',
                "files": [{"name": "main.py", "content": r'''
def negate(lit):
    """The complement of a literal: "p" <-> "-p"."""
    return lit[1:] if lit.startswith("-") else "-" + lit


def variables(clauses):
    """Sorted list of the variable names appearing in a clause list."""
    return sorted({lit.lstrip("-") for clause in clauses for lit in clause})


def to_nnf(f):
    """Negation normal form. ValueError on an unknown connective."""
    # your code here


def to_cnf(f):
    """A list of frozenset clauses equivalent to f."""
    # your code here


def satisfies(clauses, model):
    """True when every clause has a literal made true by model."""
    # your code here


def brute_force(clauses):
    """First satisfying model by exhaustive enumeration, or None."""
    # your code here


def dpll(clauses):
    """A total satisfying model found by DPLL, or None."""
    # your code here


formula = ("imp", ("and", ("var", "p"), ("var", "q")), ("or", ("var", "q"), ("var", "r")))
print(to_cnf(formula))
print(dpll(to_cnf(("and", ("var", "p"), ("not", ("var", "p"))))))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import itertools


def negate(lit):
    """The complement of a literal: "p" <-> "-p"."""
    return lit[1:] if lit.startswith("-") else "-" + lit


def variables(clauses):
    """Sorted list of the variable names appearing in a clause list."""
    return sorted({lit.lstrip("-") for clause in clauses for lit in clause})


def to_nnf(f):
    """Negation normal form. ValueError on an unknown connective."""
    op = f[0]
    if op == "var":
        return f
    if op == "and" or op == "or":
        return (op, to_nnf(f[1]), to_nnf(f[2]))
    if op == "imp":
        return to_nnf(("or", ("not", f[1]), f[2]))
    if op == "iff":
        return to_nnf(("and", ("imp", f[1], f[2]), ("imp", f[2], f[1])))
    if op == "not":
        g = f[1]
        gop = g[0]
        if gop == "var":
            return f
        if gop == "not":
            return to_nnf(g[1])          # double negation
        if gop == "and":                 # De Morgan
            return ("or", to_nnf(("not", g[1])), to_nnf(("not", g[2])))
        if gop == "or":
            return ("and", to_nnf(("not", g[1])), to_nnf(("not", g[2])))
        if gop == "imp":                 # ¬(a → b) ≡ a ∧ ¬b
            return ("and", to_nnf(g[1]), to_nnf(("not", g[2])))
        if gop == "iff":
            return to_nnf(("not", ("and", ("imp", g[1], g[2]), ("imp", g[2], g[1]))))
        raise ValueError(f"unknown connective {gop!r}")
    raise ValueError(f"unknown connective {op!r}")


def _clauses(f):
    """f is already in NNF."""
    op = f[0]
    if op == "var":
        return [frozenset({f[1]})]
    if op == "not":
        return [frozenset({"-" + f[1][1]})]
    if op == "and":
        return _clauses(f[1]) + _clauses(f[2])
    if op == "or":
        # distribute: every left clause joined with every right clause
        return [a | b for a in _clauses(f[1]) for b in _clauses(f[2])]
    raise ValueError(f"unknown connective {op!r}")


def to_cnf(f):
    """A list of frozenset clauses equivalent to f."""
    return _clauses(to_nnf(f))


def satisfies(clauses, model):
    """True when every clause has a literal made true by model."""
    for clause in clauses:
        ok = False
        for lit in clause:
            value = model[lit.lstrip("-")]
            if lit.startswith("-"):
                value = not value
            if value:
                ok = True
                break
        if not ok:
            return False
    return True


def brute_force(clauses):
    """First satisfying model by exhaustive enumeration, or None."""
    names = variables(clauses)
    for combo in itertools.product((False, True), repeat=len(names)):
        model = dict(zip(names, combo))
        if satisfies(clauses, model):
            return model
    return None


def _simplify(clauses, lit):
    """Assume lit is true: drop satisfied clauses, shrink the rest."""
    opposite = negate(lit)
    out = []
    for clause in clauses:
        if lit in clause:
            continue
        if opposite in clause:
            out.append(clause - {opposite})
        else:
            out.append(clause)
    return out


def _assign(model, lit):
    model[lit.lstrip("-")] = not lit.startswith("-")


def _dpll(clauses, model):
    while True:
        if not clauses:
            return True
        if any(len(c) == 0 for c in clauses):
            return False
        unit = None
        for clause in clauses:
            if len(clause) == 1:
                unit = next(iter(clause))
                break
        if unit is not None:
            _assign(model, unit)
            clauses = _simplify(clauses, unit)
            continue
        lits = {lit for clause in clauses for lit in clause}
        pure = next((lit for lit in sorted(lits) if negate(lit) not in lits), None)
        if pure is not None:
            _assign(model, pure)
            clauses = _simplify(clauses, pure)
            continue
        break

    branch = sorted({lit for clause in clauses for lit in clause})[0]
    for choice in (branch, negate(branch)):
        saved = dict(model)
        _assign(model, choice)
        if _dpll(_simplify(clauses, choice), model):
            return True
        model.clear()
        model.update(saved)
    return False


def dpll(clauses):
    """A total satisfying model found by DPLL, or None."""
    clauses = [frozenset(c) for c in clauses]
    model = {}
    if not _dpll(clauses, model):
        return None
    for name in variables(clauses):
        model.setdefault(name, False)
    return model


formula = ("imp", ("and", ("var", "p"), ("var", "q")), ("or", ("var", "q"), ("var", "r")))
print(to_cnf(formula))
print(dpll(to_cnf(("and", ("var", "p"), ("not", ("var", "p"))))))
'''}],
                "hints": [
                    "Write `to_nnf` as one recursion with a nested case split on the operand of `not`; every De Morgan rewrite recurses again rather than returning directly.",
                    "Distribution is a cross product: `[a | b for a in left for b in right]` where `left` and `right` are the clause lists of the two disjuncts.",
                    "`_simplify(clauses, lit)` is the whole engine — drop every clause containing `lit`, and remove `negate(lit)` from the others. A clause that shrinks to the empty set is a conflict.",
                    "Save and restore the model dict around each branch, otherwise a failed left branch leaves stale assignments behind.",
                ],
                "tests": [
                    {"name": "to_nnf removes implications and pushes negations", "code": r'''
def _ops(f):
    _found = set()
    _stack = [f]
    while _stack:
        _n = _stack.pop()
        _found.add(_n[0])
        for _k in _n[1:]:
            if isinstance(_k, tuple):
                _stack.append(_k)
    return _found

_n = to_nnf(("not", ("imp", ("var", "p"), ("and", ("var", "q"), ("var", "r")))))
assert "imp" not in _ops(_n) and "iff" not in _ops(_n), f"NNF still holds imp/iff: {_n!r}"
_bad = [_x for _x in [_n] if False]
def _walk(f):
    if f[0] == "not":
        assert f[1][0] == "var", f"not applied to {f[1][0]!r}, expected a variable"
        return
    for _k in f[1:]:
        if isinstance(_k, tuple):
            _walk(_k)
_walk(_n)
assert to_nnf(("not", ("not", ("var", "p")))) == ("var", "p"), "double negation should collapse"
'''},
                    {"name": "to_cnf distributes correctly", "code": r'''
_got = set(to_cnf(("or", ("var", "p"), ("and", ("var", "q"), ("var", "r")))))
_want = {frozenset({"p", "q"}), frozenset({"p", "r"})}
assert _got == _want, f"to_cnf gave {_got!r}, expected {_want!r}"
assert set(to_cnf(("var", "p"))) == {frozenset({"p"})}, "a bare variable is one unit clause"
assert set(to_cnf(("not", ("var", "p")))) == {frozenset({"-p"})}, "a negated variable is one unit clause"
_imp = set(to_cnf(("imp", ("var", "p"), ("var", "q"))))
assert _imp == {frozenset({"-p", "q"})}, f"p -> q should be one clause, got {_imp!r}"
'''},
                    {"name": "Unknown connectives are rejected", "code": r'''
for _bad in [("nand", ("var", "p"), ("var", "q")), ("not", ("xor", ("var", "p"), ("var", "q")))]:
    try:
        to_nnf(_bad)
        assert False, f"to_nnf({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "satisfies and brute_force agree on small cases", "code": r'''
_cl = [frozenset({"p", "q"}), frozenset({"-p"})]
_m = brute_force(_cl)
assert _m is not None and satisfies(_cl, _m), f"brute_force gave {_m!r} for a satisfiable set"
assert _m["p"] is False and _m["q"] is True, f"expected p=False q=True, got {_m!r}"
assert brute_force([frozenset({"p"}), frozenset({"-p"})]) is None, "p and -p is unsatisfiable"
assert brute_force([]) == {}, "no clauses means the empty model satisfies everything"
'''},
                    {"name": "dpll decides the boundary cases", "code": r'''
assert dpll([]) == {}, "an empty clause list is satisfiable by the empty model"
assert dpll([frozenset()]) is None, "a clause list holding the empty clause is unsatisfiable"
_all4 = [frozenset({"p", "q"}), frozenset({"p", "-q"}),
         frozenset({"-p", "q"}), frozenset({"-p", "-q"})]
assert dpll(_all4) is None, "all four clauses over p, q cannot be satisfied together"
_m = dpll([frozenset({"p", "q", "r"})])
assert _m is not None and sorted(_m) == ["p", "q", "r"], f"the model must be total, got {_m!r}"
assert satisfies([frozenset({"p", "q", "r"})], _m), f"{_m!r} does not satisfy the clause"
'''},
                    {"name": "dpll matches brute force on random 3-CNF", "code": r'''
import random as _random
_rng = _random.Random(7)
_names = ["p", "q", "r", "s", "t"]
for _trial in range(60):
    _cl = []
    for _i in range(_rng.randint(1, 14)):
        _vs = _rng.sample(_names, 3)
        _cl.append(frozenset((_v if _rng.random() < 0.5 else "-" + _v) for _v in _vs))
    _d = dpll(_cl)
    _b = brute_force(_cl)
    assert (_d is None) == (_b is None), f"dpll says {_d!r} but brute force says {_b!r} for {_cl!r}"
    if _d is not None:
        assert satisfies(_cl, _d), f"dpll model {_d!r} does not satisfy {_cl!r}"
'''},
                    {"name": "Propagation beats enumeration on a long chain", "code": r'''
_n = 40
_chain = [frozenset({"x0"})] + [frozenset({"-x%d" % _i, "x%d" % (_i + 1)}) for _range in [0] for _i in range(_n)]
_m = dpll(_chain)
assert _m is not None, "the implication chain is satisfiable"
assert all(_m["x%d" % _i] for _i in range(_n + 1)), \
    "unit propagation should force every variable in the chain to True"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Axiomatic semantics and weakest preconditions",
            "summary": "Hoare triples, computed backwards, with loops handled by annotation.",
            "concepts": [
                "The Hoare triple {P} S {Q} and the difference between partial and total correctness",
                "Dijkstra's predicate transformer: wp(S, Q) is the weakest P making the triple valid",
                "Assignment is substitution: wp(x := e, Q) = Q[x := e], read backwards, not forwards",
                "Sequencing composes transformers: wp(S1; S2, Q) = wp(S1, wp(S2, Q))",
                "A conditional splits into two guarded implications; an assert conjoins its condition",
                "A loop is opaque: the annotated invariant is the precondition, and it owes two verification conditions",
                "Discharging obligations: a decision procedure, or — here — bounded enumeration that returns a concrete counterexample",
            ],
            "lab": {
                "title": "A weakest-precondition calculator",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
Expressions, formulas and statements are nested tuples.

```text
expressions   ("num", 5) ("var", "x") ("add", a, b) ("sub", a, b) ("mul", a, b)
formulas      ("true",) ("false",) ("eq", a, b) ("le", a, b) ("lt", a, b)
              ("not", p) ("and", p, q) ("or", p, q) ("imp", p, q)
statements    ("skip",) ("assign", x, e) ("seq", s1, s2) ("assert", b)
              ("if", b, s1, s2) ("while", b, inv, body)
```

Implement six functions.

**`eval_expr(e, state)`** and **`eval_formula(f, state)`** — `state` maps variable
names to integers. Unknown node tags raise `ValueError`; an unbound variable
raises `KeyError`.

**`free_vars(node)`** — the sorted variable names in an expression or formula.

**`subst(node, name, expr)`** — replace every `("var", name)` inside `node` with
`expr`. Everything else is copied unchanged.

**`wp(stmt, post)`** — the weakest precondition:

```text
wp(skip, Q)              = Q
wp(x := e, Q)            = Q[x := e]
wp(S1; S2, Q)            = wp(S1, wp(S2, Q))
wp(assert b, Q)          = b ∧ Q
wp(if b then S1 else S2, Q) = (b → wp(S1,Q)) ∧ (¬b → wp(S2,Q))
wp(while b inv I do S, Q) = I
```

**`vcs(stmt, post)`** — the verification conditions the loops leave behind, in
source order. Each `while b inv I do S` contributes exactly two, and then the
body's own obligations against `I`:

```text
(I ∧ b)  →  wp(S, I)          the invariant is preserved
(I ∧ ¬b) →  Q                 the invariant plus the negated guard gives the post
```

**`bounded_check(formula, lo, hi)`** — try every integer assignment to the free
variables with each value in `range(lo, hi + 1)`, in sorted-name order. Return the
first state where the formula is false, or `None` when it holds throughout the
box. This is not a proof, only a refutation attempt — say so when you report it.
Raise `ValueError` when `lo > hi`.
''',
                "files": [{"name": "main.py", "content": r'''
SUM_PROGRAM = ("seq",
               ("assign", "s", ("num", 0)),
               ("seq",
                ("assign", "i", ("num", 0)),
                ("while",
                 ("lt", ("var", "i"), ("var", "n")),
                 ("and", ("le", ("var", "i"), ("var", "n")),
                  ("eq", ("mul", ("num", 2), ("var", "s")),
                   ("mul", ("var", "i"), ("add", ("var", "i"), ("num", 1))))),
                 ("seq",
                  ("assign", "i", ("add", ("var", "i"), ("num", 1))),
                  ("assign", "s", ("add", ("var", "s"), ("var", "i")))))))

SUM_POST = ("eq", ("mul", ("num", 2), ("var", "s")),
            ("mul", ("var", "n"), ("add", ("var", "n"), ("num", 1))))


def eval_expr(e, state):
    """Integer value of an expression under state."""
    # your code here


def eval_formula(f, state):
    """Truth value of a formula under state."""
    # your code here


def free_vars(node):
    """Sorted variable names occurring in an expression or formula."""
    # your code here


def subst(node, name, expr):
    """node with every occurrence of the variable `name` replaced by `expr`."""
    # your code here


def wp(stmt, post):
    """Weakest precondition of stmt with respect to post."""
    # your code here


def vcs(stmt, post):
    """Loop verification conditions, in source order."""
    # your code here


def bounded_check(formula, lo, hi):
    """First falsifying state in the box [lo, hi], or None."""
    # your code here


for obligation in vcs(SUM_PROGRAM, SUM_POST):
    print(bounded_check(obligation, 0, 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import itertools

SUM_PROGRAM = ("seq",
               ("assign", "s", ("num", 0)),
               ("seq",
                ("assign", "i", ("num", 0)),
                ("while",
                 ("lt", ("var", "i"), ("var", "n")),
                 ("and", ("le", ("var", "i"), ("var", "n")),
                  ("eq", ("mul", ("num", 2), ("var", "s")),
                   ("mul", ("var", "i"), ("add", ("var", "i"), ("num", 1))))),
                 ("seq",
                  ("assign", "i", ("add", ("var", "i"), ("num", 1))),
                  ("assign", "s", ("add", ("var", "s"), ("var", "i")))))))

SUM_POST = ("eq", ("mul", ("num", 2), ("var", "s")),
            ("mul", ("var", "n"), ("add", ("var", "n"), ("num", 1))))


def eval_expr(e, state):
    """Integer value of an expression under state."""
    tag = e[0]
    if tag == "num":
        return e[1]
    if tag == "var":
        return state[e[1]]
    if tag == "add":
        return eval_expr(e[1], state) + eval_expr(e[2], state)
    if tag == "sub":
        return eval_expr(e[1], state) - eval_expr(e[2], state)
    if tag == "mul":
        return eval_expr(e[1], state) * eval_expr(e[2], state)
    raise ValueError(f"unknown expression tag {tag!r}")


def eval_formula(f, state):
    """Truth value of a formula under state."""
    tag = f[0]
    if tag == "true":
        return True
    if tag == "false":
        return False
    if tag == "eq":
        return eval_expr(f[1], state) == eval_expr(f[2], state)
    if tag == "le":
        return eval_expr(f[1], state) <= eval_expr(f[2], state)
    if tag == "lt":
        return eval_expr(f[1], state) < eval_expr(f[2], state)
    if tag == "not":
        return not eval_formula(f[1], state)
    if tag == "and":
        return eval_formula(f[1], state) and eval_formula(f[2], state)
    if tag == "or":
        return eval_formula(f[1], state) or eval_formula(f[2], state)
    if tag == "imp":
        return (not eval_formula(f[1], state)) or eval_formula(f[2], state)
    raise ValueError(f"unknown formula tag {tag!r}")


def free_vars(node):
    """Sorted variable names occurring in an expression or formula."""
    found = set()
    stack = [node]
    while stack:
        n = stack.pop()
        if n[0] == "var":
            found.add(n[1])
            continue
        for kid in n[1:]:
            if isinstance(kid, tuple):
                stack.append(kid)
    return sorted(found)


def subst(node, name, expr):
    """node with every occurrence of the variable `name` replaced by `expr`."""
    if node[0] == "var":
        return expr if node[1] == name else node
    if node[0] in ("num", "true", "false"):
        return node
    parts = [subst(k, name, expr) if isinstance(k, tuple) else k for k in node[1:]]
    return (node[0],) + tuple(parts)


def wp(stmt, post):
    """Weakest precondition of stmt with respect to post."""
    tag = stmt[0]
    if tag == "skip":
        return post
    if tag == "assign":
        return subst(post, stmt[1], stmt[2])
    if tag == "seq":
        return wp(stmt[1], wp(stmt[2], post))
    if tag == "assert":
        return ("and", stmt[1], post)
    if tag == "if":
        guard = stmt[1]
        return ("and", ("imp", guard, wp(stmt[2], post)),
                ("imp", ("not", guard), wp(stmt[3], post)))
    if tag == "while":
        # The loop is opaque: the annotation is all we assume going in.
        return stmt[2]
    raise ValueError(f"unknown statement tag {tag!r}")


def vcs(stmt, post):
    """Loop verification conditions, in source order."""
    tag = stmt[0]
    if tag in ("skip", "assign", "assert"):
        return []
    if tag == "seq":
        return vcs(stmt[1], wp(stmt[2], post)) + vcs(stmt[2], post)
    if tag == "if":
        return vcs(stmt[2], post) + vcs(stmt[3], post)
    if tag == "while":
        guard, inv, body = stmt[1], stmt[2], stmt[3]
        preserved = ("imp", ("and", inv, guard), wp(body, inv))
        exits = ("imp", ("and", inv, ("not", guard)), post)
        return [preserved, exits] + vcs(body, inv)
    raise ValueError(f"unknown statement tag {tag!r}")


def bounded_check(formula, lo, hi):
    """First falsifying state in the box [lo, hi], or None."""
    if lo > hi:
        raise ValueError("lo must not exceed hi")
    names = free_vars(formula)
    for values in itertools.product(range(lo, hi + 1), repeat=len(names)):
        state = dict(zip(names, values))
        if not eval_formula(formula, state):
            return state
    return None


for obligation in vcs(SUM_PROGRAM, SUM_POST):
    print(bounded_check(obligation, 0, 6))
'''}],
                "hints": [
                    "`subst` is a structural copy: only the `(\"var\", name)` node changes, and `(\"num\", k)` has no children to walk.",
                    "wp for assignment goes backwards. wp(x := x+1, x ≤ 5) is x+1 ≤ 5, not x ≤ 6 rewritten by hand — build the substituted tree.",
                    "In `vcs` for a sequence, the first statement's obligations are taken against `wp(s2, post)`, not against `post`.",
                    "`itertools.product(range(lo, hi + 1), repeat=len(names))` walks the box; zip the tuple back onto the sorted names to make a state.",
                ],
                "tests": [
                    {"name": "Evaluation and free variables", "code": r'''
_st = {"x": 3, "y": 4}
assert eval_expr(("add", ("var", "x"), ("mul", ("num", 2), ("var", "y"))), _st) == 11, "3 + 2*4 = 11"
assert eval_formula(("imp", ("lt", ("var", "x"), ("var", "y")), ("le", ("num", 0), ("var", "x"))), _st) is True
assert eval_formula(("and", ("true",), ("false",)), {}) is False
assert free_vars(("and", ("le", ("var", "y"), ("var", "x")), ("eq", ("var", "x"), ("num", 1)))) == ["x", "y"]
assert free_vars(("num", 3)) == [], "a literal has no free variables"
try:
    eval_expr(("div", ("num", 1), ("num", 2)), {})
    assert False, "an unknown expression tag should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "subst replaces only the named variable", "code": r'''
_got = subst(("and", ("le", ("var", "x"), ("num", 5)), ("eq", ("var", "y"), ("var", "x"))),
             "x", ("add", ("var", "y"), ("num", 1)))
for _y in range(0, 6):
    for _x in range(0, 6):
        _want = (_y + 1 <= 5) and (_y == _y + 1)
        assert eval_formula(_got, {"x": _x, "y": _y}) == _want, \
            f"substituted formula disagrees at x={_x} y={_y}"
'''},
                    {"name": "wp of assignment and sequencing", "code": r'''
_p = wp(("assign", "x", ("add", ("var", "x"), ("num", 1))), ("le", ("var", "x"), ("num", 5)))
for _x in range(-3, 9):
    assert eval_formula(_p, {"x": _x}) == (_x + 1 <= 5), f"wp(x := x+1, x<=5) wrong at x={_x}"
_seq = ("seq", ("assign", "x", ("num", 2)), ("assign", "y", ("mul", ("var", "x"), ("num", 3))))
_q = wp(_seq, ("eq", ("var", "y"), ("num", 6)))
assert bounded_check(_q, 0, 3) is None, "after x:=2; y:=3x the postcondition y=6 always holds"
assert wp(("skip",), ("true",)) == ("true",), "skip is the identity transformer"
'''},
                    {"name": "wp of conditionals and asserts", "code": r'''
_ifs = ("if", ("lt", ("var", "x"), ("num", 0)),
        ("assign", "y", ("sub", ("num", 0), ("var", "x"))),
        ("assign", "y", ("var", "x")))
_q = wp(_ifs, ("le", ("num", 0), ("var", "y")))
for _x in range(-5, 6):
    assert eval_formula(_q, {"x": _x, "y": 0}) is True, f"abs is non-negative, but wp failed at x={_x}"
_a = wp(("assert", ("lt", ("num", 0), ("var", "x"))), ("le", ("var", "x"), ("num", 3)))
for _x in range(-2, 6):
    assert eval_formula(_a, {"x": _x}) == (0 < _x and _x <= 3), f"wp(assert 0<x, x<=3) wrong at x={_x}"
try:
    wp(("goto", "L1"), ("true",))
    assert False, "an unknown statement tag should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The loop annotation is the precondition", "code": r'''
_loop = SUM_PROGRAM[2][2]
assert _loop[0] == "while", "SUM_PROGRAM should end in the while statement"
assert wp(_loop, SUM_POST) == _loop[2], "wp of a while is exactly its annotated invariant"
'''},
                    {"name": "Both obligations of the sum program hold in the box", "code": r'''
_obs = vcs(SUM_PROGRAM, SUM_POST)
assert len(_obs) == 2, f"one loop owes exactly two verification conditions, got {len(_obs)}"
for _i, _ob in enumerate(_obs):
    _cex = bounded_check(_ob, 0, 6)
    assert _cex is None, f"obligation {_i} was falsified at {_cex!r} — check the wp rules"
'''},
                    {"name": "A weak invariant is refuted with a concrete state", "code": r'''
_bad = ("seq",
        ("assign", "s", ("num", 0)),
        ("seq",
         ("assign", "i", ("num", 0)),
         ("while",
          ("lt", ("var", "i"), ("var", "n")),
          ("eq", ("mul", ("num", 2), ("var", "s")),
           ("mul", ("var", "i"), ("add", ("var", "i"), ("num", 1)))),
          ("seq",
           ("assign", "i", ("add", ("var", "i"), ("num", 1))),
           ("assign", "s", ("add", ("var", "s"), ("var", "i")))))))
_obs = vcs(_bad, SUM_POST)
_cex = bounded_check(_obs[1], 0, 6)
assert _cex is not None, "dropping i <= n from the invariant must break the exit obligation"
assert eval_formula(_obs[1], _cex) is False, f"{_cex!r} is reported as a counterexample but satisfies the obligation"
assert bounded_check(_obs[0], 0, 6) is None, "the preservation obligation still holds"
try:
    bounded_check(("true",), 5, 1)
    assert False, "lo > hi should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Kripke structures and explicit-state model checking",
            "summary": "Search a transition system for a violation, and hand back the trace that proves it.",
            "concepts": [
                "A Kripke structure: states, a transition relation, initial states, and an atomic labelling",
                "Interleaving semantics turns a concurrent protocol into a single non-deterministic transition system",
                "Reachability by breadth-first search settles all invariants of a finite system — completely",
                "Bounded search settles nothing negative, but every counterexample it does return is real",
                "The linear-time operators G (always) and F (eventually), and what a counterexample to each looks like",
                "A counterexample to G p is a finite prefix; a counterexample to F p is a path with no witness inside the bound",
                "State explosion: the reachable set of a protocol grows as the product of its components",
            ],
            "lab": {
                "title": "Model checking a mutual-exclusion protocol",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
`mutex_model(safe)` is supplied. It builds a two-process lock protocol as a
Kripke structure: each process moves `idle -> wait -> crit -> idle`, and the
`safe` version only enters `crit` when the lock is free. Atoms are `crit1`,
`crit2`, `wait1`, `wait2`, `locked`.

Build the checker as a class `Kripke(initial, transitions, labels)`.

- `transitions` maps every state to a list of successor states, in a fixed order.
- `labels` maps every state to a `frozenset` of atoms.
- The constructor raises `ValueError` when a transition names a state that has no
  entry in `transitions`, or when a state has no label.

Predicates take the atom set, so `lambda ap: "crit1" not in ap` is a property of a
state.

**`successors(state)`** — the successor list. `KeyError` for an unknown state.

**`reachable()`** — the set of states reachable from the initial states.

**`check_invariant(pred)`** — is `pred` true in every reachable state? Return
`None` when it is, otherwise a **shortest** path — a list of states from an
initial state to a violating one. Breadth-first, exploring successors in the
given order.

**`check_always(pred, bound)`** — the same question restricted to paths of at
most `bound` transitions. Same return shape.

**`check_eventually(pred, bound)`** — does every path satisfy `F pred` within
`bound` transitions? A counterexample is a path from an initial state along which
`pred` never holds and which either uses all `bound` transitions or ends in a
deadlocked state. Return the first such path found by depth-first search in
successor order, or `None`.

Raise `ValueError` when `bound` is negative.
''',
                "files": [{"name": "main.py", "content": r'''
from collections import deque

MODES = ("idle", "wait", "crit")


def _replace(state, index, value):
    parts = list(state)
    parts[index] = value
    return tuple(parts)


def mutex_model(safe=True):
    """Two processes, one lock. Returns (initial, transitions, labels)."""
    states = [(a, b, lock) for a in MODES for b in MODES for lock in (0, 1)]
    transitions = {}
    for state in states:
        nxt = []
        for i in (0, 1):
            mode = state[i]
            if mode == "idle":
                nxt.append(_replace(state, i, "wait"))
            elif mode == "wait":
                if state[2] == 0 or not safe:
                    nxt.append(_replace(_replace(state, i, "crit"), 2, 1))
            else:
                nxt.append(_replace(_replace(state, i, "idle"), 2, 0))
        transitions[state] = nxt
    labels = {}
    for state in states:
        atoms = set()
        for i, tag in ((0, "1"), (1, "2")):
            if state[i] == "crit":
                atoms.add("crit" + tag)
            elif state[i] == "wait":
                atoms.add("wait" + tag)
        if state[2] == 1:
            atoms.add("locked")
        labels[state] = frozenset(atoms)
    return [("idle", "idle", 0)], transitions, labels


class Kripke:
    """A finite transition system with atomic labels."""

    def __init__(self, initial, transitions, labels):
        # your code here
        pass

    def successors(self, state):
        """Successors of state, in order. KeyError when the state is unknown."""
        # your code here

    def reachable(self):
        """Every state reachable from an initial state."""
        # your code here

    def check_invariant(self, pred):
        """None, or a shortest path to a state where pred fails."""
        # your code here

    def check_always(self, pred, bound):
        """None, or a shortest path of at most `bound` steps to a failure."""
        # your code here

    def check_eventually(self, pred, bound):
        """None, or a path within `bound` steps along which pred never holds."""
        # your code here


safe = Kripke(*mutex_model(True))
unsafe = Kripke(*mutex_model(False))
both = lambda ap: not ("crit1" in ap and "crit2" in ap)
print(len(safe.reachable()), safe.check_invariant(both))
print(unsafe.check_invariant(both))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
from collections import deque

MODES = ("idle", "wait", "crit")


def _replace(state, index, value):
    parts = list(state)
    parts[index] = value
    return tuple(parts)


def mutex_model(safe=True):
    """Two processes, one lock. Returns (initial, transitions, labels)."""
    states = [(a, b, lock) for a in MODES for b in MODES for lock in (0, 1)]
    transitions = {}
    for state in states:
        nxt = []
        for i in (0, 1):
            mode = state[i]
            if mode == "idle":
                nxt.append(_replace(state, i, "wait"))
            elif mode == "wait":
                if state[2] == 0 or not safe:
                    nxt.append(_replace(_replace(state, i, "crit"), 2, 1))
            else:
                nxt.append(_replace(_replace(state, i, "idle"), 2, 0))
        transitions[state] = nxt
    labels = {}
    for state in states:
        atoms = set()
        for i, tag in ((0, "1"), (1, "2")):
            if state[i] == "crit":
                atoms.add("crit" + tag)
            elif state[i] == "wait":
                atoms.add("wait" + tag)
        if state[2] == 1:
            atoms.add("locked")
        labels[state] = frozenset(atoms)
    return [("idle", "idle", 0)], transitions, labels


class Kripke:
    """A finite transition system with atomic labels."""

    def __init__(self, initial, transitions, labels):
        self.initial = list(initial)
        self.transitions = dict(transitions)
        self.labels = dict(labels)
        for state, nxt in self.transitions.items():
            if state not in self.labels:
                raise ValueError(f"state {state!r} has no label")
            for target in nxt:
                if target not in self.transitions:
                    raise ValueError(f"transition to unknown state {target!r}")
        for state in self.initial:
            if state not in self.transitions:
                raise ValueError(f"initial state {state!r} is unknown")

    def successors(self, state):
        """Successors of state, in order. KeyError when the state is unknown."""
        return self.transitions[state]

    def reachable(self):
        """Every state reachable from an initial state."""
        seen = set(self.initial)
        queue = deque(self.initial)
        while queue:
            state = queue.popleft()
            for target in self.successors(state):
                if target not in seen:
                    seen.add(target)
                    queue.append(target)
        return seen

    def _bfs(self, pred, bound=None):
        """Shortest path to a pred-violating reachable state, or None."""
        parent = {}
        seen = set()
        queue = deque()
        for state in self.initial:
            if state not in seen:
                seen.add(state)
                parent[state] = None
                queue.append((state, 0))
        while queue:
            state, depth = queue.popleft()
            if not pred(self.labels[state]):
                path = []
                node = state
                while node is not None:
                    path.append(node)
                    node = parent[node]
                path.reverse()
                return path
            if bound is not None and depth == bound:
                continue
            for target in self.successors(state):
                if target not in seen:
                    seen.add(target)
                    parent[target] = state
                    queue.append((target, depth + 1))
        return None

    def check_invariant(self, pred):
        """None, or a shortest path to a state where pred fails."""
        return self._bfs(pred, None)

    def check_always(self, pred, bound):
        """None, or a shortest path of at most `bound` steps to a failure."""
        if bound < 0:
            raise ValueError("bound must not be negative")
        return self._bfs(pred, bound)

    def check_eventually(self, pred, bound):
        """None, or a path within `bound` steps along which pred never holds."""
        if bound < 0:
            raise ValueError("bound must not be negative")
        # A pair (state, steps left) that yielded nothing will never yield
        # anything, so memoising it keeps the search linear in the bound.
        dead = set()

        def walk(path, left):
            state = path[-1]
            if pred(self.labels[state]):
                return None            # this path already satisfies F pred
            if (state, left) in dead:
                return None
            nxt = self.successors(state)
            if left == 0 or not nxt:
                return list(path)      # bound exhausted, or deadlocked
            for target in nxt:
                found = walk(path + [target], left - 1)
                if found is not None:
                    return found
            dead.add((state, left))
            return None

        for state in self.initial:
            found = walk([state], bound)
            if found is not None:
                return found
        return None


safe = Kripke(*mutex_model(True))
unsafe = Kripke(*mutex_model(False))
both = lambda ap: not ("crit1" in ap and "crit2" in ap)
print(len(safe.reachable()), safe.check_invariant(both))
print(unsafe.check_invariant(both))
'''}],
                "hints": [
                    "Reachability and `check_invariant` are the same breadth-first walk; the only addition is a `parent` dict so you can rebuild the path once you stop.",
                    "Test the predicate when you dequeue a state, not when you enqueue it, or the initial states escape unchecked.",
                    "For `check_always`, carry the depth alongside the state in the queue and simply stop expanding once `depth == bound`.",
                    "`check_eventually` is a depth-first walk that prunes as soon as `pred` holds — that branch is satisfied. Memoise `(state, steps_left)` pairs that failed to produce a counterexample.",
                ],
                "tests": [
                    {"name": "Construction validates the transition relation", "code": r'''
_init, _trans, _labs = mutex_model(True)
_k = Kripke(_init, _trans, _labs)
assert _k.successors(("idle", "idle", 0)) == _trans[("idle", "idle", 0)], "successors should preserve order"
try:
    _k.successors(("nope", "nope", 9))
    assert False, "an unknown state should raise KeyError"
except KeyError:
    pass
try:
    Kripke([("a",)], {("a",): [("b",)]}, {("a",): frozenset()})
    assert False, "a dangling transition target should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Reachability is a proper subset of the state space", "code": r'''
_k = Kripke(*mutex_model(True))
_r = _k.reachable()
assert ("idle", "idle", 0) in _r, "the initial state is reachable"
assert ("crit", "crit", 1) not in _r, "the safe protocol never reaches both-critical"
assert ("crit", "idle", 0) not in _r, "a process in crit always holds the lock"
assert 0 < len(_r) < 18, f"reachable set has {len(_r)} states, the full space has 18"
'''},
                    {"name": "The safe protocol satisfies mutual exclusion", "code": r'''
_k = Kripke(*mutex_model(True))
_both = lambda ap: not ("crit1" in ap and "crit2" in ap)
assert _k.check_invariant(_both) is None, "the safe protocol should have no violation"
assert _k.check_always(_both, 12) is None, "and no violation within twelve steps either"
'''},
                    {"name": "The unsafe protocol yields a shortest counterexample", "code": r'''
_k = Kripke(*mutex_model(False))
_both = lambda ap: not ("crit1" in ap and "crit2" in ap)
_path = _k.check_invariant(_both)
assert _path is not None, "dropping the lock test must break mutual exclusion"
assert _path[0] == ("idle", "idle", 0), f"the trace must start at the initial state, got {_path[0]!r}"
assert _path[-1][0] == "crit" and _path[-1][1] == "crit", f"the trace ends at {_path[-1]!r}"
for _a, _b in zip(_path, _path[1:]):
    assert _b in _k.successors(_a), f"{_a!r} -> {_b!r} is not a transition"
assert len(_path) == 5, f"the shortest violating trace has five states, got {len(_path)}"
'''},
                    {"name": "Bounded always is incomplete but sound", "code": r'''
_k = Kripke(*mutex_model(False))
_both = lambda ap: not ("crit1" in ap and "crit2" in ap)
assert _k.check_always(_both, 3) is None, "four transitions are needed, so a bound of three finds nothing"
_p = _k.check_always(_both, 4)
assert _p is not None and len(_p) == 5, f"a bound of four should find the trace, got {_p!r}"
try:
    _k.check_always(_both, -1)
    assert False, "a negative bound should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Eventually, on a hand-made chain", "code": r'''
_t = {"a": ["b"], "b": ["c"], "c": ["c"]}
_l = {"a": frozenset(), "b": frozenset(), "c": frozenset({"p"})}
_m = Kripke(["a"], _t, _l)
_p = lambda ap: "p" in ap
_cex = _m.check_eventually(_p, 1)
assert _cex == ["a", "b"], f"within one step p never holds, expected ['a', 'b'], got {_cex!r}"
assert _m.check_eventually(_p, 2) is None, "two steps reach c, where p holds"
assert _m.check_eventually(_p, 0) == ["a"], "at zero steps only the initial state is inspected"
'''},
                    {"name": "Deadlock and starvation are counterexamples too", "code": r'''
_dead = Kripke(["s"], {"s": []}, {"s": frozenset()})
assert _dead.check_eventually(lambda ap: "p" in ap, 5) == ["s"], \
    "a deadlocked state with no witness is a counterexample regardless of the bound"
_k = Kripke(*mutex_model(True))
_cex = _k.check_eventually(lambda ap: "crit1" in ap, 8)
assert _cex is not None, "the lock protocol does not guarantee that process 1 ever enters"
assert all("crit1" not in _k.labels[_s] for _s in _cex), "the trace must avoid crit1 throughout"
assert _cex[0] == ("idle", "idle", 0), "the trace starts at the initial state"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Property-based testing and shrinking",
            "summary": "Random search for a counterexample, then automatic reduction to the smallest one.",
            "concepts": [
                "A property is a universally quantified claim; a test is one witness that it has not yet failed",
                "Generators as data: a sampling function plus a shrinking function travel together",
                "Metamorphic and round-trip properties find bugs no example-based test was written for",
                "Greedy shrinking: repeatedly replace the counterexample with a smaller one that still fails",
                "A shrunk input is locally minimal, not globally minimal — know which claim you are making",
                "Seeding the generator makes a random failure reproducible, which is what makes it a bug report",
                "Testing refutes; it never verifies. Its coverage is the distribution the generator happens to have",
            ],
            "lab": {
                "title": "A generator and shrinker framework",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
`Gen` and the deliberately wrong `dedup` are supplied. Do not fix `dedup` — the
point of the lab is to have the framework find and minimise its failure.

A property is a function from a value to a bool. It **fails** when it returns a
falsy value or raises.

**`fails(prop, value)`** — `True` when `prop(value)` is falsy or raises anything.

**`ints(lo, hi)`** — a `Gen` of integers.
`generate` draws uniformly from `[lo, hi]`. `shrink(v)` returns candidates that
are strictly closer to the target — 0, clamped into `[lo, hi]` — ordered most
aggressive first. `shrink(target)` is empty. Raise `ValueError` when `lo > hi`.

**`lists(element, max_len)`** — a `Gen` of lists.
`generate` draws a length in `[0, max_len]` and then that many elements.
`shrink(v)` offers, in this order: the empty list, each half, each single-element
deletion, and each list with one element replaced by one of its own shrinks.
Never offer `v` itself. Raise `ValueError` when `max_len` is negative.

**`shrink_value(gen, value, prop)`** — greedy reduction. Repeatedly take the
first shrink candidate that still fails and continue from it. Stop when no
candidate fails, and return that locally minimal value.

**`check(gen, prop, trials, seed)`** — draw `trials` values from a
`random.Random(seed)`, and return the shrunk counterexample for the first failure,
or `None` when all trials pass.
''',
                "files": [{"name": "main.py", "content": r'''
import random


class Gen:
    """A generator: how to draw a value, and how to make one smaller."""

    def __init__(self, draw, reduce_fn):
        self._draw = draw
        self._reduce = reduce_fn

    def generate(self, rng):
        return self._draw(rng)

    def shrink(self, value):
        return self._reduce(value)


def dedup(xs):
    """Claims to remove duplicates. It only removes adjacent ones. Do not fix it."""
    out = []
    for x in xs:
        if not out or out[-1] != x:
            out.append(x)
    return out


def fails(prop, value):
    """True when prop(value) is falsy or raises."""
    # your code here


def ints(lo, hi):
    """A Gen of integers in [lo, hi] that shrinks towards zero."""
    # your code here


def lists(element, max_len=8):
    """A Gen of lists of values drawn from `element`."""
    # your code here


def shrink_value(gen, value, prop):
    """Greedily reduce a failing value to a locally minimal failing value."""
    # your code here


def check(gen, prop, trials=200, seed=7):
    """A minimal counterexample, or None when every trial passes."""
    # your code here


unique = lambda xs: len(dedup(xs)) == len(set(dedup(xs)))
print(check(lists(ints(0, 3), 6), unique))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import random


class Gen:
    """A generator: how to draw a value, and how to make one smaller."""

    def __init__(self, draw, reduce_fn):
        self._draw = draw
        self._reduce = reduce_fn

    def generate(self, rng):
        return self._draw(rng)

    def shrink(self, value):
        return self._reduce(value)


def dedup(xs):
    """Claims to remove duplicates. It only removes adjacent ones. Do not fix it."""
    out = []
    for x in xs:
        if not out or out[-1] != x:
            out.append(x)
    return out


def fails(prop, value):
    """True when prop(value) is falsy or raises."""
    try:
        return not prop(value)
    except Exception:
        return True


def ints(lo, hi):
    """A Gen of integers in [lo, hi] that shrinks towards zero."""
    if lo > hi:
        raise ValueError("lo must not exceed hi")
    target = min(max(0, lo), hi)

    def draw(rng):
        return rng.randint(lo, hi)

    def reduce_fn(value):
        candidates = []
        # jump to the target, then halve the gap, then step by one
        for c in (target, value - (value - target) // 2,
                  value - 1 if value > target else value + 1):
            if lo <= c <= hi and abs(c - target) < abs(value - target) and c not in candidates:
                candidates.append(c)
        return candidates

    return Gen(draw, reduce_fn)


def lists(element, max_len=8):
    """A Gen of lists of values drawn from `element`."""
    if max_len < 0:
        raise ValueError("max_len must not be negative")

    def draw(rng):
        n = rng.randint(0, max_len)
        return [element.generate(rng) for _ in range(n)]

    def reduce_fn(value):
        candidates = []
        if value:
            candidates.append([])
            half = len(value) // 2
            if half:
                candidates.append(value[:half])
                candidates.append(value[half:])
            for i in range(len(value)):
                candidates.append(value[:i] + value[i + 1:])
            for i, item in enumerate(value):
                for smaller in element.shrink(item):
                    candidates.append(value[:i] + [smaller] + value[i + 1:])
        out = []
        for c in candidates:
            if c != value and c not in out:
                out.append(c)
        return out

    return Gen(draw, reduce_fn)


def shrink_value(gen, value, prop):
    """Greedily reduce a failing value to a locally minimal failing value."""
    current = value
    while True:
        for candidate in gen.shrink(current):
            if fails(prop, candidate):
                current = candidate
                break
        else:
            return current


def check(gen, prop, trials=200, seed=7):
    """A minimal counterexample, or None when every trial passes."""
    rng = random.Random(seed)
    for _ in range(trials):
        value = gen.generate(rng)
        if fails(prop, value):
            return shrink_value(gen, value, prop)
    return None


unique = lambda xs: len(dedup(xs)) == len(set(dedup(xs)))
print(check(lists(ints(0, 3), 6), unique))
'''}],
                "hints": [
                    "`fails` must catch the exception too — a property that raises has failed just as surely as one that returns False.",
                    "For `ints`, the guard `abs(c - target) < abs(value - target)` is what stops the shrinker looping forever; without it a candidate can equal the value it came from.",
                    "Order matters in `lists.shrink`: putting `[]` and the halves before the single deletions makes the reduction converge in far fewer steps.",
                    "`shrink_value` is a `while True` loop around a `for ... else`: the `else` branch runs when no candidate failed, which is exactly the fixed point.",
                ],
                "tests": [
                    {"name": "fails handles falsy results and exceptions", "code": r'''
assert fails(lambda v: False, 1) is True
assert fails(lambda v: True, 1) is False
def _boom(v):
    raise ZeroDivisionError("nope")
assert fails(_boom, 1) is True, "a property that raises has failed"
'''},
                    {"name": "ints draws in range and shrinks towards zero", "code": r'''
import random as _random
_g = ints(-4, 9)
_rng = _random.Random(1)
for _ in range(300):
    _v = _g.generate(_rng)
    assert -4 <= _v <= 9, f"ints(-4, 9) produced {_v!r}"
assert _g.shrink(0) == [], "zero is already minimal inside [-4, 9]"
for _v in (-4, -1, 1, 5, 9):
    _c = _g.shrink(_v)
    assert _c, f"shrink({_v}) offered nothing"
    assert 0 in _c, f"shrink({_v}) should offer the target 0, got {_c!r}"
    for _x in _c:
        assert -4 <= _x <= 9 and abs(_x) < abs(_v), f"shrink({_v}) offered {_x!r}"
_h = ints(3, 8)
assert _h.shrink(3) == [], "the target is clamped to lo when lo > 0"
assert 3 in _h.shrink(8), "shrink should aim at the clamped target"
try:
    ints(5, 1)
    assert False, "lo > hi should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "lists draws within the length bound and shrinks", "code": r'''
import random as _random
_g = lists(ints(0, 3), 5)
_rng = _random.Random(2)
for _ in range(200):
    _v = _g.generate(_rng)
    assert 0 <= len(_v) <= 5, f"lists(..., 5) produced a list of length {len(_v)}"
    assert all(0 <= _x <= 3 for _x in _v), f"element out of range in {_v!r}"
assert _g.shrink([]) == [], "the empty list is minimal"
_c = _g.shrink([2, 3])
assert [] == _c[0], f"the empty list should be the first candidate, got {_c[0]!r}"
assert [2] in _c and [3] in _c, f"single deletions missing from {_c!r}"
assert [0, 3] in _c, "element-wise shrinking should be offered too"
assert [2, 3] not in _c, "a shrinker must never offer the value it was given"
try:
    lists(ints(0, 1), -1)
    assert False, "a negative max_len should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "shrink_value reaches the minimal failing list", "code": r'''
_g = lists(ints(0, 9), 8)
_got = shrink_value(_g, [5, 5, 5, 5, 5], lambda xs: len(xs) < 3)
assert _got == [0, 0, 0], f"expected [0, 0, 0], got {_got!r}"
_same = shrink_value(_g, [0, 0, 0], lambda xs: len(xs) < 3)
assert _same == [0, 0, 0], "an already minimal value comes back unchanged"
'''},
                    {"name": "check returns None when the property holds", "code": r'''
_g = lists(ints(0, 5), 6)
assert check(_g, lambda xs: list(reversed(list(reversed(xs)))) == xs, 200, 7) is None, \
    "double reversal is an identity, so no counterexample exists"
assert check(_g, lambda xs: dedup(xs) == dedup(dedup(xs)), 200, 7) is None, \
    "dedup is idempotent even though it is wrong"
'''},
                    {"name": "check minimises the dedup counterexample", "code": r'''
_unique = lambda xs: len(dedup(xs)) == len(set(dedup(xs)))
_got = check(lists(ints(0, 3), 6), _unique, 200, 7)
assert _got is not None, "dedup only removes adjacent duplicates, so a failure exists"
assert len(_got) == 3, f"the smallest failing list has three elements, got {_got!r}"
assert fails(_unique, _got), f"{_got!r} is reported as a counterexample but passes"
for _i in range(len(_got)):
    assert not fails(_unique, _got[:_i] + _got[_i + 1:]), \
        f"{_got!r} is not minimal: deleting index {_i} still fails"
'''},
                    {"name": "The same seed gives the same counterexample", "code": r'''
_unique = lambda xs: len(dedup(xs)) == len(set(dedup(xs)))
_a = check(lists(ints(0, 3), 6), _unique, 120, 11)
_b = check(lists(ints(0, 3), 6), _unique, 120, 11)
assert _a == _b, f"seeded runs must agree: {_a!r} then {_b!r}"
assert check(lists(ints(0, 0), 6), _unique, 200, 7) is None, \
    "with a single possible element every list is a run, so dedup is correct"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — one ring buffer, verified three ways",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
A bounded circular buffer is small enough to verify completely and interesting
enough that the three techniques disagree about it. You build the structure, then
three independent verifiers, and finally a report that says which technique caught
what.

`ringbuf.py` holds the data structure. `verify.py` holds the verifiers.
`main.py` runs everything.

## `ringbuf.py`

`RingBuffer(capacity)` — `ValueError` when `capacity < 1`. Attributes
`capacity`, `items` (a list of length `capacity`), `tail` (index of the oldest
item) and `size`.

- `push(item)` — appends. `ValueError("buffer is full")` when there is no room.
- `pop()` — removes and returns the oldest. `ValueError("buffer is empty")` when
  there is none.
- `__len__`, `is_empty()`, `is_full()`
- `to_list()` — the contents, oldest first.
- `invariant()` — the representation invariant, as a bool:
  `len(items) == capacity`, `0 <= size <= capacity`, `0 <= tail < capacity`.
- `from_state(capacity, tail, size)` — a **classmethod** building an arbitrary
  legal state, so the inductive check can start anywhere. `ValueError` for a
  `tail` or `size` outside its range.

`BuggyRingBuffer` is supplied. Its `is_full` is off by one. Leave it alone.

## `verify.py`

**`run_sequence(cls, capacity, ops)`** — replay a list of `"push"` / `"pop"`
strings against both a `cls(capacity)` and a plain-list reference model. At every
step: an operation the model says is legal must succeed and leave matching
contents; one the model says is illegal must raise `ValueError`; and
`invariant()` must hold afterwards. Return `None` when the run is clean, or a
string naming the first divergence. `ValueError` for an unknown operation name.

**`inductive_check(cls, capacity)`** — the proof leg. The initial state must
satisfy the invariant, and every enabled operation applied to every legal state
must preserve it. Return `None`, or a dict `{"tail": t, "size": n, "op": name}`.

**`bounded_check(cls, capacity, depth)`** — the model-checking leg. Breadth-first
over all operation sequences of length at most `depth`, `"push"` before `"pop"`.
Return the shortest failing sequence, or `None`.

**`property_check(cls, capacity, trials, max_len, seed)`** — the testing leg.
Random sequences, then greedy shrinking of the first failure by single deletions.
Return the minimal failing sequence, or `None`.

**`report(cls, capacity, depth, trials, max_len, seed)`** — five lines:

```text
target: <class name>(capacity=<n>)
inductive: <verdict>
bounded: <verdict>
property: <verdict>
verdict: clean            or   verdict: defect found by inductive, property
```

A clean inductive line reads `inductive: invariant preserved by every operation`;
a clean bounded line reads `bounded: no counterexample within <depth> operations`;
a clean property line reads `property: <trials> random sequences passed`.

Run `report(BuggyRingBuffer, 3, depth=3)` and read it: induction catches the
defect in one step, bounded search at depth three does not reach it, and random
testing does. That gap is the deliverable.
''',
        "deliverables": [
            "`ringbuf.py` — a correct bounded circular buffer with an explicit representation invariant and a `from_state` constructor",
            "`verify.py` — `run_sequence` conformance replay against a list model, plus the three verifiers",
            "`inductive_check` that establishes the invariant by induction over the abstract state space rather than by search from the initial state",
            "`bounded_check` that returns the shortest failing operation sequence within a depth",
            "`property_check` that shrinks a random failure to a minimal one, deterministically for a fixed seed",
            "`main.py` — a demo that reports on both the correct and the buggy class and prints the two reports side by side",
        ],
        "constraints": [
            "Standard library only; `random` must be seeded through `random.Random(seed)`",
            "`ringbuf.py` and `verify.py` must import cleanly and print nothing",
            "`BuggyRingBuffer` must not be repaired — it is the specimen the verifiers are measured against",
            "`inductive_check` must not simulate from the initial state; it enumerates states and takes one step",
            "The reference model inside `run_sequence` is a plain list; do not compare a ring buffer against another ring buffer",
        ],
        "rubric": [
            {"criterion": "Correctness of the structure", "weight": 25,
             "evidence": "FIFO order survives wrap-around, both guards raise ValueError, and the invariant holds after every operation."},
            {"criterion": "Soundness of the three verifiers", "weight": 35,
             "evidence": "Every verifier returns None for RingBuffer and a genuine witness for BuggyRingBuffer at an adequate depth."},
            {"criterion": "Minimality and determinism", "weight": 20,
             "evidence": "bounded_check returns a shortest sequence; property_check shrinks to four pushes and repeats exactly for a fixed seed."},
            {"criterion": "The report", "weight": 20,
             "evidence": "report() names each technique, its verdict and the depth used, and the buggy run visibly shows bounded search missing what induction caught."},
        ],
        "hints": [
            "Store `tail` and `size` rather than `head` and `tail`; the empty and full states are then distinguishable without a spare slot.",
            "`run_sequence` should ask the model first — `legal = len(model) < capacity` — and only then try the buffer, so you can compare what should have happened with what did.",
            "`inductive_check` never runs a program: it builds `cls.from_state(capacity, tail, size)` for every legal pair, applies one operation, and re-checks the invariant. A guard that refuses is a pass, not a failure.",
            "Greedy shrinking is a `while changed` loop: for each index, try the sequence with that index removed, and restart the sweep the moment a shorter sequence still fails.",
        ],
        "files": [
            {"name": "ringbuf.py", "content": r'''
class RingBuffer:
    """A bounded FIFO queue over a fixed-size circular array."""

    def __init__(self, capacity):
        # your code here
        pass

    def __len__(self):
        # your code here
        pass

    def is_empty(self):
        # your code here
        pass

    def is_full(self):
        # your code here
        pass

    def push(self, item):
        """Append item. ValueError when the buffer is full."""
        # your code here

    def pop(self):
        """Remove and return the oldest item. ValueError when empty."""
        # your code here

    def to_list(self):
        """Contents, oldest first."""
        # your code here

    def invariant(self):
        """The representation invariant, as a bool."""
        # your code here

    @classmethod
    def from_state(cls, capacity, tail, size):
        """A buffer holding `size` placeholder items with the oldest at `tail`."""
        # your code here


class BuggyRingBuffer(RingBuffer):
    """Supplied specimen: is_full is off by one. Do not repair it."""

    def is_full(self):
        return len(self) > self.capacity
'''},
            {"name": "verify.py", "content": r'''
import random
from collections import deque

from ringbuf import RingBuffer, BuggyRingBuffer

OPS = ("push", "pop")


def run_sequence(cls, capacity, ops):
    """Replay ops against cls(capacity) and a list model. None, or a message."""
    # your code here


def inductive_check(cls, capacity):
    """None, or {"tail": t, "size": n, "op": name} for a state that breaks the invariant."""
    # your code here


def bounded_check(cls, capacity, depth):
    """Shortest failing operation sequence of length <= depth, or None."""
    # your code here


def shrink(cls, capacity, ops):
    """Greedily delete operations while the sequence still fails."""
    # your code here


def property_check(cls, capacity, trials=200, max_len=10, seed=7):
    """A minimal failing random sequence, or None."""
    # your code here


def report(cls, capacity, depth=3, trials=200, max_len=10, seed=7):
    """A five-line summary of the three verification legs."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from ringbuf import RingBuffer, BuggyRingBuffer
from verify import report

print(report(RingBuffer, 3, depth=6))
print()
print(report(BuggyRingBuffer, 3, depth=3))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "ringbuf.py", "content": r'''
class RingBuffer:
    """A bounded FIFO queue over a fixed-size circular array."""

    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self.capacity = capacity
        self.items = [None] * capacity
        self.tail = 0          # index of the oldest item
        self.size = 0

    def __len__(self):
        return self.size

    def is_empty(self):
        return len(self) == 0

    def is_full(self):
        return len(self) == self.capacity

    def push(self, item):
        """Append item. ValueError when the buffer is full."""
        if self.is_full():
            raise ValueError("buffer is full")
        self.items[(self.tail + self.size) % self.capacity] = item
        self.size += 1

    def pop(self):
        """Remove and return the oldest item. ValueError when empty."""
        if self.is_empty():
            raise ValueError("buffer is empty")
        item = self.items[self.tail]
        self.items[self.tail] = None
        self.tail = (self.tail + 1) % self.capacity
        self.size -= 1
        return item

    def to_list(self):
        """Contents, oldest first."""
        return [self.items[(self.tail + k) % self.capacity] for k in range(self.size)]

    def invariant(self):
        """The representation invariant, as a bool."""
        return (len(self.items) == self.capacity
                and 0 <= self.size <= self.capacity
                and 0 <= self.tail < self.capacity)

    @classmethod
    def from_state(cls, capacity, tail, size):
        """A buffer holding `size` placeholder items with the oldest at `tail`."""
        buf = cls(capacity)
        if not 0 <= tail < capacity:
            raise ValueError("tail out of range")
        if not 0 <= size <= capacity:
            raise ValueError("size out of range")
        buf.tail = tail
        buf.size = size
        for k in range(size):
            buf.items[(tail + k) % capacity] = k
        return buf


class BuggyRingBuffer(RingBuffer):
    """Supplied specimen: is_full is off by one. Do not repair it."""

    def is_full(self):
        return len(self) > self.capacity
'''},
            {"name": "verify.py", "content": r'''
import random
from collections import deque

from ringbuf import RingBuffer, BuggyRingBuffer

OPS = ("push", "pop")


def run_sequence(cls, capacity, ops):
    """Replay ops against cls(capacity) and a list model. None, or a message."""
    buf = cls(capacity)
    model = []
    for i, op in enumerate(ops):
        if op == "push":
            legal = len(model) < capacity
            item = i
            try:
                buf.push(item)
                refused = False
            except ValueError:
                refused = True
            if legal and refused:
                return f"step {i}: push refused although the buffer had room"
            if not legal and not refused:
                return f"step {i}: push accepted although the buffer was full"
            if legal:
                model.append(item)
        elif op == "pop":
            legal = len(model) > 0
            got = None
            try:
                got = buf.pop()
                refused = False
            except ValueError:
                refused = True
            if legal and refused:
                return f"step {i}: pop refused although the buffer held items"
            if not legal and not refused:
                return f"step {i}: pop returned {got!r} from an empty buffer"
            if legal:
                want = model.pop(0)
                if got != want:
                    return f"step {i}: pop gave {got!r}, the model expected {want!r}"
        else:
            raise ValueError(f"unknown operation {op!r}")
        if not buf.invariant():
            return f"step {i}: representation invariant broken after {op}"
        if buf.to_list() != model:
            return f"step {i}: contents {buf.to_list()!r} differ from the model {model!r}"
    return None


def inductive_check(cls, capacity):
    """None, or the state and operation that break the invariant in one step."""
    if not cls(capacity).invariant():
        return {"tail": 0, "size": 0, "op": "init"}
    for tail in range(capacity):
        for size in range(capacity + 1):
            for op in OPS:
                buf = cls.from_state(capacity, tail, size)
                try:
                    if op == "push":
                        buf.push("x")
                    else:
                        buf.pop()
                except ValueError:
                    continue          # the guard refused: nothing changed
                if not buf.invariant():
                    return {"tail": tail, "size": size, "op": op}
    return None


def bounded_check(cls, capacity, depth):
    """Shortest failing operation sequence of length <= depth, or None."""
    if depth < 0:
        raise ValueError("depth must not be negative")
    queue = deque([[]])
    while queue:
        seq = queue.popleft()
        if run_sequence(cls, capacity, seq) is not None:
            return seq
        if len(seq) < depth:
            for op in OPS:
                queue.append(seq + [op])
    return None


def shrink(cls, capacity, ops):
    """Greedily delete operations while the sequence still fails."""
    current = list(ops)
    changed = True
    while changed:
        changed = False
        for i in range(len(current)):
            candidate = current[:i] + current[i + 1:]
            if run_sequence(cls, capacity, candidate) is not None:
                current = candidate
                changed = True
                break
    return current


def property_check(cls, capacity, trials=200, max_len=10, seed=7):
    """A minimal failing random sequence, or None."""
    rng = random.Random(seed)
    for _ in range(trials):
        n = rng.randint(0, max_len)
        seq = [rng.choice(OPS) for _ in range(n)]
        if run_sequence(cls, capacity, seq) is not None:
            return shrink(cls, capacity, seq)
    return None


def report(cls, capacity, depth=3, trials=200, max_len=10, seed=7):
    """A five-line summary of the three verification legs."""
    ind = inductive_check(cls, capacity)
    bnd = bounded_check(cls, capacity, depth)
    prp = property_check(cls, capacity, trials, max_len, seed)

    lines = ["target: " + cls.__name__ + "(capacity=" + str(capacity) + ")"]
    if ind is None:
        lines.append("inductive: invariant preserved by every operation")
    else:
        lines.append("inductive: violation at " + str(ind))
    if bnd is None:
        lines.append("bounded: no counterexample within " + str(depth) + " operations")
    else:
        lines.append("bounded: counterexample " + str(bnd))
    if prp is None:
        lines.append("property: " + str(trials) + " random sequences passed")
    else:
        lines.append("property: minimal failing sequence " + str(prp))

    caught = [name for name, result
              in (("inductive", ind), ("bounded", bnd), ("property", prp))
              if result is not None]
    lines.append("verdict: " + ("clean" if not caught
                                else "defect found by " + ", ".join(caught)))
    return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from ringbuf import RingBuffer, BuggyRingBuffer
from verify import report

print(report(RingBuffer, 3, depth=6))
print()
print(report(BuggyRingBuffer, 3, depth=3))
'''},
        ],
        "tests": [
            {"name": "The buffer is a FIFO queue that wraps", "code": r'''
from ringbuf import RingBuffer
_b = RingBuffer(3)
assert len(_b) == 0 and _b.is_empty() and not _b.is_full(), "a fresh buffer is empty"
for _x in ("a", "b", "c"):
    _b.push(_x)
assert _b.is_full() and _b.to_list() == ["a", "b", "c"], f"got {_b.to_list()!r}"
assert _b.pop() == "a", "pop returns the oldest item"
_b.push("d")
assert _b.to_list() == ["b", "c", "d"], f"after wrapping the contents are {_b.to_list()!r}"
assert [_b.pop(), _b.pop(), _b.pop()] == ["b", "c", "d"], "order survives the wrap"
assert _b.is_empty(), "the buffer should be empty again"
'''},
            {"name": "Both guards raise, and so does a bad capacity", "code": r'''
from ringbuf import RingBuffer
try:
    RingBuffer(0)
    assert False, "capacity 0 should raise ValueError"
except ValueError:
    pass
_b = RingBuffer(1)
try:
    _b.pop()
    assert False, "popping an empty buffer should raise ValueError"
except ValueError:
    pass
_b.push(1)
try:
    _b.push(2)
    assert False, "pushing to a full buffer should raise ValueError"
except ValueError:
    pass
assert _b.to_list() == [1], "a refused push must leave the buffer untouched"
'''},
            {"name": "from_state builds any legal state", "code": r'''
from ringbuf import RingBuffer
_b = RingBuffer.from_state(4, 3, 2)
assert _b.tail == 3 and len(_b) == 2 and _b.invariant(), f"state is tail={_b.tail} size={len(_b)}"
assert len(_b.to_list()) == 2, "to_list must respect the size"
assert RingBuffer.from_state(4, 0, 4).is_full(), "size == capacity means full"
for _bad in ((4, 4, 0), (4, -1, 0), (4, 0, 5), (4, 0, -1)):
    try:
        RingBuffer.from_state(*_bad)
        assert False, f"from_state{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "run_sequence accepts a correct run and names a divergence", "code": r'''
from ringbuf import RingBuffer, BuggyRingBuffer
from verify import run_sequence
_ok = ["push", "push", "push", "pop", "push", "pop", "pop", "pop", "pop"]
assert run_sequence(RingBuffer, 3, _ok) is None, \
    f"the correct buffer should replay cleanly, got {run_sequence(RingBuffer, 3, _ok)!r}"
assert run_sequence(RingBuffer, 3, []) is None, "an empty sequence is trivially clean"
_msg = run_sequence(BuggyRingBuffer, 3, ["push"] * 4)
assert isinstance(_msg, str), "a fourth push into a capacity-3 buffer must be reported"
assert "step 3" in _msg, f"the divergence is at step 3, the message said {_msg!r}"
try:
    run_sequence(RingBuffer, 3, ["peek"])
    assert False, "an unknown operation should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Induction proves the invariant, and refutes the buggy guard", "code": r'''
from ringbuf import RingBuffer, BuggyRingBuffer
from verify import inductive_check
for _cap in (1, 2, 3, 5):
    assert inductive_check(RingBuffer, _cap) is None, \
        f"the invariant should be inductive at capacity {_cap}"
_w = inductive_check(BuggyRingBuffer, 3)
assert _w is not None, "the off-by-one guard breaks the invariant in one step"
assert _w["op"] == "push" and _w["size"] == 3, f"witness was {_w!r}, expected a push from size 3"
'''},
            {"name": "Bounded search is shortest-first and depth-limited", "code": r'''
from ringbuf import RingBuffer, BuggyRingBuffer
from verify import bounded_check
assert bounded_check(RingBuffer, 3, 7) is None, "the correct buffer has no counterexample"
assert bounded_check(BuggyRingBuffer, 3, 3) is None, \
    "three operations cannot fill a capacity-3 buffer and overflow it"
_seq = bounded_check(BuggyRingBuffer, 3, 4)
assert _seq == ["push", "push", "push", "push"], f"expected four pushes, got {_seq!r}"
assert bounded_check(BuggyRingBuffer, 3, 8) == ["push"] * 4, "deeper search must still return the shortest"
'''},
            {"name": "Shrinking reduces a long failure to the minimal one", "code": r'''
from ringbuf import RingBuffer, BuggyRingBuffer
from verify import shrink, run_sequence
_long = ["pop", "push", "push", "pop", "push", "push", "push", "pop", "push", "push"]
assert run_sequence(BuggyRingBuffer, 3, _long) is not None, "the long sequence should already fail"
_min = shrink(BuggyRingBuffer, 3, _long)
assert _min == ["push"] * 4, f"expected four pushes, got {_min!r}"
for _i in range(len(_min)):
    assert run_sequence(BuggyRingBuffer, 3, _min[:_i] + _min[_i + 1:]) is None, \
        f"{_min!r} is not minimal: deleting index {_i} still fails"
'''},
            {"name": "Property testing is deterministic and finds the defect", "code": r'''
from ringbuf import RingBuffer, BuggyRingBuffer
from verify import property_check
assert property_check(RingBuffer, 3, 200, 10, 7) is None, "no random sequence should break the correct buffer"
_a = property_check(BuggyRingBuffer, 3, 200, 10, 7)
_b = property_check(BuggyRingBuffer, 3, 200, 10, 7)
assert _a == ["push"] * 4, f"expected the minimal four-push sequence, got {_a!r}"
assert _a == _b, "a fixed seed must give the same answer twice"
assert property_check(BuggyRingBuffer, 3, 200, 2, 7) is None, \
    "sequences of at most two operations can never reach the defect"
'''},
            {"name": "The report states each verdict", "code": r'''
from ringbuf import RingBuffer, BuggyRingBuffer
from verify import report
_clean = report(RingBuffer, 3, depth=6)
_lines = _clean.split("\n")
assert len(_lines) == 5, f"the report has five lines, got {len(_lines)}"
assert _lines[0] == "target: RingBuffer(capacity=3)", f"first line was {_lines[0]!r}"
assert _lines[1] == "inductive: invariant preserved by every operation", f"got {_lines[1]!r}"
assert _lines[2] == "bounded: no counterexample within 6 operations", f"got {_lines[2]!r}"
assert _lines[3] == "property: 200 random sequences passed", f"got {_lines[3]!r}"
assert _lines[4] == "verdict: clean", f"got {_lines[4]!r}"
'''},
            {"name": "The buggy report shows bounded search missing the defect", "code": r'''
from ringbuf import BuggyRingBuffer
from verify import report
_lines = report(BuggyRingBuffer, 3, depth=3).split("\n")
assert _lines[1].startswith("inductive: violation at"), f"got {_lines[1]!r}"
assert _lines[2] == "bounded: no counterexample within 3 operations", f"got {_lines[2]!r}"
assert _lines[3].startswith("property: minimal failing sequence"), f"got {_lines[3]!r}"
assert _lines[4] == "verdict: defect found by inductive, property", f"got {_lines[4]!r}"
'''},
            {"name": "The modules are import-clean", "code": r'''
for _name in ("ringbuf.py", "verify.py"):
    _src = open(_name).read()
    assert "print(" not in _src, f"{_name} should define things, not print — move output to main.py"
'''},
        ],
    },
}
