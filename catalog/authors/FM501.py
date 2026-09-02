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
            "read": [
                {
                    "title": "From a formula to a verdict",
                    "minutes": 12,
                    "body": r'''
Three people are deciding whether to come to a launch party, and the constraints arrive by
text message over the course of an afternoon. Ada will come only if Ben comes. Ben and Cal
have fallen out and will not both be in the same room. Somebody has to come, or there is no
party. Is there any way to keep all three messages happy at once?

You can answer this by trying combinations. There are three people, each either coming or
not, so there are eight cases, and you can check each one against the three messages in a
minute. That instinct — write down every possible world and test it — is the whole of
propositional logic in miniature, and everything in this module is about doing it faster.

## A formula, a valuation, and the relation between them

Give each person a variable: $a$, $b$, $c$, true when that person comes. The three messages
become one formula:

$$(a \to b) \;\land\; \lnot(b \land c) \;\land\; (a \lor b \lor c)$$

A choice of true or false for every variable is a *valuation*. A valuation $v$ *satisfies*
a formula $\varphi$, written $v \models \varphi$, when the formula comes out true once every
variable is replaced by its value. The formula is syntax — a tree of connectives. The
valuation is semantics — a table of facts about the world. The relation $\models$ is the
function that joins them, and it is short enough to write down:

```python
import itertools


def holds(f, v):
    op = f[0]
    if op == "var":
        return v[f[1]]
    if op == "not":
        return not holds(f[1], v)
    if op == "and":
        return holds(f[1], v) and holds(f[2], v)
    if op == "or":
        return holds(f[1], v) or holds(f[2], v)
    if op == "imp":
        return (not holds(f[1], v)) or holds(f[2], v)
    raise ValueError(op)


A, B, C = ("var", "a"), ("var", "b"), ("var", "c")
party = ("and", ("imp", A, B),
         ("and", ("not", ("and", B, C)),
          ("or", A, ("or", B, C))))
for a, b, c in itertools.product((False, True), repeat=3):
    if holds(party, {"a": a, "b": b, "c": c}):
        print(a, b, c)
```

Three of the eight valuations survive: Cal alone, Ben alone, or Ada with Ben. The formula is
*satisfiable* because at least one valuation satisfies it. Had none survived, it would have
been *unsatisfiable*, and the party organiser could stop negotiating. Two formulas are
*equivalent* when every valuation gives them the same verdict, and that is the licence for
every rewrite in this module: a rewrite is allowed when the eight-row table would not notice.

## Why clauses

Eight rows is fine. A circuit with sixty signals has $2^{60}$ rows, and the table is no longer
a method. To do better, the formula needs a shape in which a single decision has a local,
mechanical effect. That shape is *conjunctive normal form*: an AND of ORs of literals, where a
literal is a variable or its negation. In the lab's representation a clause is a `frozenset`
of literals read as an OR, and a CNF is a list of clauses read as an AND.

Why this shape and not another? Decide that some literal $\ell$ is true. Every clause that
contains $\ell$ is now satisfied, whatever else it holds, and can be forgotten. Every clause
that contains $\lnot\ell$ has lost one way of being true, so $\lnot\ell$ is struck out of it
and the clause stays, shorter. No other clause is touched. That is the entire consequence of
the decision, computable in one pass, and it is what the decision procedure will run on.

Getting to clauses takes two moves. The first is *negation normal form*: get rid of
$\to$ and $\leftrightarrow$, and push every $\lnot$ inward until it sits on a variable. Each
rewrite is an equivalence you can confirm on the table: $f \to g$ is $\lnot f \lor g$;
$f \leftrightarrow g$ is $(f \to g) \land (g \to f)$; De Morgan turns $\lnot(f \land g)$ into
$\lnot f \lor \lnot g$ and $\lnot(f \lor g)$ into $\lnot f \land \lnot g$; and
$\lnot\lnot f$ is $f$.

Take the formula the lab's starter prints, $(p \land q) \to (q \lor r)$. Removing the
implication gives $\lnot(p \land q) \lor (q \lor r)$; De Morgan gives
$(\lnot p \lor \lnot q) \lor (q \lor r)$. That is already a single clause,
$\{\lnot p, \lnot q, q, r\}$ — and it contains both $q$ and $\lnot q$. One of those is true
under every valuation, so the clause is always satisfied and the original formula was a
tautology. The clause form shows that at a glance, which the tree did not.

The second move is distribution. In NNF an $\lor$ can still sit over an $\land$, as in
$p \lor (q \land r)$, and a clause cannot hold an $\land$. For the whole to be true, either
$p$ is true, in which case both $p \lor q$ and $p \lor r$ are true, or $q$ and $r$ are both
true, in which case both are true again. Conversely if both $p \lor q$ and $p \lor r$ hold
and $p$ is false, then $q$ and $r$ must both hold. So

$$p \lor (q \land r) \;\equiv\; (p \lor q) \land (p \lor r)$$

In clause terms: the clauses of $F \lor G$ are every clause of $F$ unioned with every clause
of $G$. The lab's `to_cnf` is that cross product, and its own example is this one:
$[\{p\}] \times [\{q\}, \{r\}]$ gives $[\{p, q\}, \{p, r\}]$.

## Where distribution stops being cheap

The cross product is a product, and products grow. Take
$(x_1 \land y_1) \lor (x_2 \land y_2) \lor \cdots \lor (x_n \land y_n)$: the first disjunct
is two clauses, and each further disjunct doubles the count.

```python
def clauses_of(f):
    op = f[0]
    if op == "var":
        return [frozenset({f[1]})]
    if op == "not":
        return [frozenset({"-" + f[1][1]})]
    if op == "and":
        return clauses_of(f[1]) + clauses_of(f[2])
    if op == "or":
        return [a | b for a in clauses_of(f[1]) for b in clauses_of(f[2])]
    raise ValueError(op)


def pairs(n):
    f = ("and", ("var", "x1"), ("var", "y1"))
    for k in range(2, n + 1):
        f = ("or", f, ("and", ("var", "x%d" % k), ("var", "y%d" % k)))
    return f


for n in range(1, 7):
    print(n, len(clauses_of(pairs(n))))
```

The counts are 2, 4, 8, 16, 32, 64: $2^n$ clauses from a formula of $2n$ literals. For a
formula of any real size the equivalent CNF does not fit in memory. Industrial front ends do
not distribute; they introduce a fresh variable for each subformula and emit a few short
clauses per connective (the Tseitin transformation), which gives a clause set that is linear
in the formula and *equisatisfiable* with it — satisfiable exactly when the original is —
but not equivalent, because it has variables the original never had. The lab distributes,
because its inputs are small and equivalence is what its tests can check against `brute_force`.

## Deciding a clause set

Two edge cases come straight out of the reading of clauses. A clause is an OR of its
literals, so a clause with no literals has no way to be true: the empty clause is false. A
CNF is an AND of its clauses, so a CNF with no clauses has nothing that could fail: the empty
clause list is true, satisfied by the empty model. Both are in the lab's tests.

Davis, Putnam, Logemann and Loveland's procedure is built on the one-pass simplification
above, applied in three situations that each remove a choice.

A *unit clause* has exactly one literal. It is an OR of one thing, so that thing must be
true — there is no decision to make. Set it, simplify, and look again, because the
simplification may have produced a new unit. This is *unit propagation*.

A *pure literal* is one whose complement appears in no clause. Setting it true can only
satisfy clauses and never shortens any, so if the set had a model before, it has one with
this literal true. Set it and simplify. Notice what this step preserves: satisfiability,
not equivalence. A model of the original in which the pure literal was false is lost, and
that is fine, because a decision procedure wants one model, not all of them.

When neither applies, *split*: pick a variable, assume it true, recurse; if that fails,
assume it false, recurse. A branch fails when simplification produces an empty clause, and
succeeds when no clauses are left. This is where the exponential lives, and the other two
rules exist to reach it as rarely as possible.

Here is the procedure with a trace, on five clauses over $p$, $q$, $r$:

```python
def negate(lit):
    return lit[1:] if lit.startswith("-") else "-" + lit


def simplify(clauses, lit):
    out = []
    for c in clauses:
        if lit in c:
            continue
        if negate(lit) in c:
            out.append(c - {negate(lit)})
        else:
            out.append(c)
    return out


def show(clauses):
    key = lambda l: (l.lstrip("-"), l.startswith("-"))
    return " ".join("{" + ",".join(sorted(c, key=key)) + "}" for c in clauses) or "(no clauses)"


def dpll(clauses, depth=0):
    pad = "  " * depth
    while True:
        print(pad + show(clauses))
        if not clauses:
            print(pad + "no clauses left: satisfiable")
            return True
        if any(len(c) == 0 for c in clauses):
            print(pad + "empty clause: conflict")
            return False
        unit = next((next(iter(c)) for c in clauses if len(c) == 1), None)
        if unit is not None:
            print(pad + "unit " + unit)
            clauses = simplify(clauses, unit)
            continue
        lits = {l for c in clauses for l in c}
        pure = next((l for l in sorted(lits) if negate(l) not in lits), None)
        if pure is not None:
            print(pad + "pure " + pure)
            clauses = simplify(clauses, pure)
            continue
        break
    branch = sorted(lits)[0]
    for choice in (branch, negate(branch)):
        print(pad + "split: assume " + choice)
        if dpll(simplify(clauses, choice), depth + 1):
            return True
    return False


F = [frozenset(s.split()) for s in ["p q", "p -q", "-p q", "-p -q r", "-r -q"]]
print(dpll(F))
```

Read the trace top to bottom. The five clauses have no unit and no pure literal — every
variable appears with both signs — so the solver splits on the first literal in sorted
order, $\lnot p$. Under $\lnot p$, the clauses $\{p, q\}$ and $\{p, \lnot q\}$ lose their
$p$ and become the units $\{q\}$ and $\{\lnot q\}$, while the two clauses containing
$\lnot p$ are satisfied and vanish. Propagating $q$ empties $\{\lnot q\}$: a conflict, and
the branch is abandoned. Under $p$ instead, $\{\lnot p, q\}$ becomes the unit $\{q\}$;
propagating $q$ turns $\{\lnot p, \lnot q, r\}$ into $\{r\}$ and $\{\lnot r, \lnot q\}$
into $\{\lnot r\}$; propagating $r$ empties the last one. Both branches conflict, so the set
is unsatisfiable, and the procedure prints `False`. Six clause-set snapshots did the work of
eight table rows here; on the lab's forty-variable implication chain the gap is $2^{41}$
rows against forty-one propagation steps, which is the last test in the lab and the reason
the procedure exists.

## The mistakes people make

The first is in the split. A branch that fails has, on the way to failing, written several
propagated values into the model dict. If the second branch starts from that dict, it
inherits assignments that were consequences of the wrong assumption, and the solver can
report a model that satisfies nothing. It is tempting because the recursion looks pure —
the clause list is passed down and never mutated — but the model is the one piece of shared
state, and it has to be saved before the first branch and restored before the second.

The second is in what comes back. The procedure stops the moment no clauses remain, and by
then some variables may never have been decided: a variable whose every clause was satisfied
by other literals vanishes without a value. The recursion is correct to stop — the remaining
variables are unconstrained — but the lab asks for a *total* model, so `dpll` fills in the
missing names before returning. `satisfies` on a partial model raises `KeyError`, which is
how the omission shows up if it is made.

The third is in the reading of clauses: treating a clause with both $q$ and $\lnot q$ as a
conflict. A conflict is an *empty* clause, one with no way to be true. A clause holding a
literal and its complement is the opposite, one with no way to be false.

## Where it stops holding

Everything here is propositional. There are no quantifiers, no integers, no arrays; a claim
like "$2s = i(i+1)$ for the current $i$" cannot be written, let alone decided. The next module
produces obligations of that kind, and the industrial answer is a solver that keeps DPLL's
search but replaces the valuation with a theory: satisfiability modulo theories.

DPLL's worst case is still $2^n$, and it has to be, because SAT is NP-complete. What makes
modern solvers usable on millions of clauses is not propagation alone but *learning*: when a
branch conflicts, the solver derives a new clause that records why and adds it to the set so
the same dead end is never entered twice. That is the CDCL of the course's third reference,
and the lab's solver is the core that CDCL grows out of.

Finally, validating against enumeration is exact and only works when enumeration is
possible. The lab's random test uses five variables and up to fourteen clauses, because
$2^5$ valuations is cheap. At sixty variables you can no longer check the fast solver against
the slow one; you check it against another fast one, and against itself under a different
variable order.

In the lab *CNF conversion and a DPLL solver* you build the two halves: `to_nnf` and `to_cnf`
take the formula tree to clauses by the rewrites above, and `dpll` decides the clauses by
propagate, eliminate, split and backtrack, with `brute_force` as the oracle it must agree
with on every random instance.
''',
                },
            ],
            "quiz": {
                "title": "Clauses, propagation, and what a verdict means",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A clause set contains the clause $\\{p, \\lnot p, q\\}$. What does that clause contribute to the decision?",
                        "opts": [
                            "Nothing: it is satisfied under every valuation, so dropping it leaves the set of models unchanged",
                            "A conflict: a clause holding both a literal and its complement is the empty clause in disguise",
                            "A unit on $q$: $p$ and $\\lnot p$ cancel, leaving $q$ as the only literal that can carry the clause",
                            "A constraint that $p$ be decided first, since its two literals must be resolved before $q$ can be",
                        ],
                        "a": 0,
                        "whys": [
                            r"Whichever value $p$ takes, one of $p$ and $\lnot p$ is true, so the clause is true.",
                            r"The instinct is that contradiction lives here, but a clause is an OR, and an OR that contains a literal and its complement is always true. The empty clause is the one with no literals at all — no way to be true — which is the opposite situation.",
                            r"Cancelling is an AND idea: $p \land \lnot p$ is false. In an OR the two literals do not cancel, they cover every case between them, and $q$ is never needed.",
                            r"No literal in a clause is decided before another; a clause is a set, and the solver reads them in any order. This clause imposes nothing on $p$ because both values of $p$ satisfy it.",
                        ],
                        "why": r'''
A clause is a disjunction. If it contains both $p$ and $\lnot p$, then under any valuation one
of the two is true and the clause is satisfied, so it constrains nothing and can be dropped.
The starter's first print shows this: $(p \land q) \to (q \lor r)$ converts to the single
clause $\{\lnot p, \lnot q, q, r\}$, which is the tautology made visible. The dangerous
clause is the empty one — no literals, no way to be true — and the two must not be confused.
''',
                    },
                    {
                        "q": "Why is pure-literal elimination sound — why can setting a pure literal true never turn a satisfiable clause set into an unsatisfiable one?",
                        "opts": [
                            "Its variable is unconstrained by the other clauses, so the reduced set is logically equivalent to the original one",
                            "A pure literal occurs in exactly one clause, so setting it true affects that clause alone and leaves the rest as it was",
                            "Setting it true satisfies every clause it occurs in and shortens none, so a model of the rest extends to the whole",
                            "Setting it true is what unit propagation would do anyway once the surrounding clauses had been simplified",
                        ],
                        "a": 2,
                        "whys": [
                            r"The step preserves satisfiability, not equivalence. A model of the original in which the pure literal was false is discarded, and the reduced set has fewer models than the original, not the same ones.",
                            r"Purity is about sign, not count: a pure literal may occur in twenty clauses, and setting it true satisfies all twenty. What matters is that its complement occurs in none, so no clause gets shorter.",
                            r"Nothing is lost that a model of the remaining clauses would need, because the pure literal never appears negated in them.",
                            r"Unit propagation fires only on a clause of length one. A pure literal in a long clause would never become a unit on its own; the pure-literal rule is a separate argument, and it is about signs rather than lengths.",
                        ],
                        "why": r'''
Assume the original set has a model $m$. If $m$ already sets the pure literal true, it is a
model of the reduced set too. If $m$ sets it false, flip it: every clause containing the
literal becomes true, and no clause becomes false, because no clause contains its complement.
So the flipped $m$ is still a model. That argument proves satisfiability is preserved; it
does not prove equivalence, and it should not, because models that set the literal false are
deliberately thrown away.
''',
                    },
                    {
                        "q": "DPLL splits on $p$, the branch assuming $p$ reaches a conflict, and the solver moves to the branch assuming $\\lnot p$. What must happen to the assignments made during the failed branch?",
                        "opts": [
                            "They are kept, since propagation only ever derives values that hold in every model of the clause set",
                            "They are discarded: every value set by propagation under $p$ is removed before the second branch begins",
                            "Only the assignment to $p$ itself is undone; the propagated ones were forced and therefore remain valid",
                            "They are negated one by one, since each forced value was the wrong one for the model being sought",
                        ],
                        "a": 1,
                        "whys": [
                            r"Propagation derives values that hold in every model *of the simplified set*, and the simplified set was built on the assumption $p$. Withdraw the assumption and the derivations go with it; keeping them is the model-leak bug the lab's hint warns about.",
                            r"Every propagated value was a consequence of assuming $p$, and that assumption has been withdrawn.",
                            r"Forced by what? By clauses that had already been shortened under $p$. Those units did not exist in the original set, so the values they forced are not facts about it.",
                            r"A failed branch does not tell you that each of its values was wrong, only that the combination was. Negating them all would be a new assumption, unjustified by anything, and the correct move is to forget them and let the second branch derive its own.",
                        ],
                        "why": r'''
Everything propagated inside a branch was a consequence of that branch's assumption. When
the assumption is withdrawn, the consequences are too, so the model must be restored to what
it was before the split. The lab's solution copies the dict before each branch and restores
it after a failure; without that, the second branch inherits stale values and the solver can
return a model that satisfies nothing, which the random test against `brute_force` catches.
''',
                    },
                    {
                        "q": "Converting $(x_1 \\land y_1) \\lor (x_2 \\land y_2) \\lor \\cdots \\lor (x_n \\land y_n)$ to CNF by distribution: how does the clause count grow with $n$?",
                        "opts": [
                            "It doubles per disjunct, reaching $2^n$ clauses, because every clause of one side is joined with every clause of the other",
                            "It grows by two per disjunct, reaching $2n$ clauses, because each conjunction contributes its two literals as two separate clauses",
                            "It stays at one clause, because a disjunction of anything flattens into a single clause holding all of its literals",
                            "It grows as $n^2$, because each pair of disjuncts must be combined into a clause of its own before the rest are added",
                        ],
                        "a": 0,
                        "whys": [
                            r"The clauses of $F \lor G$ are the cross product of the clauses of $F$ and of $G$, and a product of $n$ twos is $2^n$.",
                            r"That would be the count for an AND of the conjunctions, where clauses are appended. Under an OR they are multiplied, not appended: two clauses times two clauses is four, not four added to nothing.",
                            r"A disjunction of *literals* flattens into one clause. A disjunction of *conjunctions* does not, because a clause cannot contain an AND; each conjunction has to be spread across every clause, which is what distribution does.",
                            r"Quadratic would need each disjunct to combine with each other disjunct once. Distribution combines every clause so far with every clause of the newcomer, and the count so far is already the product of everything before, so the growth compounds.",
                        ],
                        "why": r'''
`clauses_of` on an OR returns `[a | b for a in left for b in right]`, a cross product. The
first conjunction gives two clauses; OR-ing in a second multiplies by its two clauses to give
four; the third gives eight. The reading's script prints 2, 4, 8, 16, 32, 64. This is why
real front ends use the Tseitin transformation, which introduces a variable per subformula
and stays linear at the cost of equivalence.
''',
                    },
                    {
                        "q": "`brute_force` enumerates all $2^n$ valuations. On the lab's forty-one-variable implication chain, `dpll` finishes at once. What makes the difference on that input?",
                        "opts": [
                            "DPLL caches the valuations it has already tried, so each variable is examined once rather than $2^n$ times",
                            "DPLL is polynomial in the number of clauses, whereas enumeration is exponential in the number of variables",
                            "Pure-literal elimination removes every variable of the chain, since each of its literals appears with one sign",
                            "Unit propagation forces each variable from the one before it, so no branching happens at all on this input",
                        ],
                        "a": 3,
                        "whys": [
                            r"DPLL keeps no cache of valuations; it keeps a clause list that shrinks. The forty-one-step run is a single chain of forced values with no revisiting to avoid.",
                            r"DPLL is exponential in the worst case, and has to be, because SAT is NP-complete. It is fast on this input because this input never reaches the split, not because the procedure has a better complexity class.",
                            r"Only $x_{40}$ is pure. Every other variable appears positively in one clause and negatively in the next, so the pure-literal rule finds nothing until propagation has already done the work.",
                            r"$\{x_0\}$ is a unit; simplifying by it turns $\{\lnot x_0, x_1\}$ into the unit $\{x_1\}$, and so on down the chain.",
                        ],
                        "why": r'''
The chain is $\{x_0\}$, $\{\lnot x_0, x_1\}$, $\{\lnot x_1, x_2\}$ and so on. The first
clause is a unit, so $x_0$ is set true; simplification strikes $\lnot x_0$ from the second
clause, making $\{x_1\}$ a unit; and each propagation manufactures the next. Forty-one steps,
no split. Enumeration would visit up to $2^{41}$ valuations before finding the one model.
The complexity class did not change; this particular input never exercises the expensive
case.
''',
                    },
                    {
                        "q": "The lab's `dpll` must return a value for every variable of its input, but the recursive search can finish without deciding some of them. How does that happen?",
                        "opts": [
                            "A variable can vanish when every clause mentioning it is satisfied by other literals, so nothing ever decides it",
                            "The search stops at the first unit clause it finds, and any variables further down the list are never reached",
                            "Splitting assigns only the branch variable, and propagation records nothing in the model until the search ends",
                            "Variables removed by pure-literal elimination are deleted from the model to keep the reduced clause set consistent",
                        ],
                        "a": 0,
                        "whys": [
                            r"In $\{p, q, r\}$, setting $p$ satisfies the only clause; $q$ and $r$ were never constrained and never assigned.",
                            r"A unit clause is propagated, not stopped at; the search continues until no clauses remain or one is empty. Variables are missed because their clauses disappear, not because the search halts early.",
                            r"Propagation writes each forced value into the model as it goes; that is what the model is for. The missing variables are the ones no clause ever forced or split on.",
                            r"Pure-literal elimination *assigns* its literal, adding to the model rather than deleting from it. The unassigned variables are those whose clauses were satisfied before any rule reached them.",
                        ],
                        "why": r'''
The recursion stops when the clause list is empty, and a clause can be removed by a literal
other than the one you are wondering about. With the single clause $\{p, q, r\}$, setting
$p$ true removes it, and the search returns with $q$ and $r$ never mentioned. They are
unconstrained, so any value works; the lab's `dpll` fills them in with `False` because a
`satisfies` call on a partial model raises `KeyError`, and a caller deserves a model that
can be checked.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Reading a program backwards",
                    "minutes": 13,
                    "body": r'''
A gantry carries a workpiece along a rail with slots numbered from 0. The next instruction
is `x := x + 1`, one slot along, and the safety interlock demands that after it the gantry
is at slot 5 or below, because slot 6 is the end stop. Which positions is it safe to issue
the instruction from?

You answer without thinking about it: from slot 4 or below. Slot 5 would move it to 6. What
you did, without ceremony, was take a condition about *after* the step and work out the
condition about *before* it. This module is that move, made precise enough for a program to
perform, and then extended from one instruction to a whole program with a loop in it.

## The triple, and the weakest one

Write the situation as $\{P\}\; S\; \{Q\}$: if $P$ holds before $S$ runs, and $S$ finishes,
then $Q$ holds afterwards. This is a *Hoare triple*, and the clause "and $S$ finishes" is
what makes it *partial* correctness — a program that never terminates satisfies every
triple, and termination is a separate proof. For the gantry, $S$ is `x := x + 1`, $Q$ is
$x \le 5$, and $P$ is whatever makes the triple true.

Many $P$ do. $x = 0$ works. $x \le 2$ works. $x \le 4$ works. Of all of them, $x \le 4$ is
the one to want, because it admits every starting state from which the step is safe and
excludes none. That is the *weakest precondition*, written $wp(S, Q)$: the largest set of
starting states from which $S$ is guaranteed to land in $Q$. Dijkstra's insight was that
$wp$ is a function of $S$ and $Q$ that can be computed from the text of $S$, with no need to
know what $P$ the programmer had in mind.

## The assignment rule, derived from the rail

After `x := e`, the new value of $x$ is whatever $e$ evaluated to in the old state, and
nothing else changed. $Q$ is a statement about the new $x$. So $Q$ will hold afterwards
exactly when $Q$-with-$e$-written-in-place-of-$x$ holds beforehand:

$$wp(x := e,\; Q) \;=\; Q[x := e]$$

The gantry: $Q$ is $x \le 5$, $e$ is $x + 1$, so the precondition is $x + 1 \le 5$. Notice
that it is not written $x \le 4$; the rule does the substitution and leaves the arithmetic
alone, which is what makes it mechanical. The lab's `subst` builds the substituted tree, and
the evaluator can then check it at any state:

```python
def ev(e, st):
    tag = e[0]
    if tag == "num":
        return e[1]
    if tag == "var":
        return st[e[1]]
    if tag == "add":
        return ev(e[1], st) + ev(e[2], st)
    if tag == "mul":
        return ev(e[1], st) * ev(e[2], st)
    if tag == "eq":
        return ev(e[1], st) == ev(e[2], st)
    if tag == "le":
        return ev(e[1], st) <= ev(e[2], st)
    if tag == "lt":
        return ev(e[1], st) < ev(e[2], st)
    if tag == "not":
        return not ev(e[1], st)
    if tag == "and":
        return ev(e[1], st) and ev(e[2], st)
    if tag == "imp":
        return (not ev(e[1], st)) or ev(e[2], st)
    raise ValueError(tag)


def subst(node, name, expr):
    if node[0] == "var":
        return expr if node[1] == name else node
    if node[0] == "num":
        return node
    return (node[0],) + tuple(subst(k, name, expr) if isinstance(k, tuple) else k
                              for k in node[1:])


def show(n):
    tag = n[0]
    if tag == "num":
        return str(n[1])
    if tag == "var":
        return n[1]
    if tag == "not":
        return "not " + show(n[1])
    sym = {"add": "+", "mul": "*", "eq": "=", "le": "<=", "lt": "<", "and": "and", "imp": "->"}
    return "(" + show(n[1]) + " " + sym[tag] + " " + show(n[2]) + ")"


X = ("var", "x")
post = ("le", X, ("num", 5))
pre = subst(post, "x", ("add", X, ("num", 1)))
print(show(pre))
for x in (3, 4, 5):
    print(x, ev(pre, {"x": x}))
```

The script prints `((x + 1) <= 5)`, then `3 True`, `4 True`, `5 False`: slot 5 is the first
unsafe position, which is what the rail told you.

## The mistake, and why it is tempting

Almost everyone, the first time, reads the assignment forwards. "The step makes $x$ one
bigger, so the bound moves one along: $x \le 6$." It is tempting because that is how you
think about running the program, and it produces a number that looks like the right kind of
answer. Test it: from $x = 6$ the step lands on 7, past the end stop. The forward reading
computes what states the step *reaches from* a condition, which is a different transformer
(the strongest postcondition), and it moves the bound the wrong way. Substitution never asks
which way anything moves. It writes $e$ where $x$ was and stops, and that refusal to think
is the whole reason the rule can be trusted.

The same refusal is what makes the lab's second test bite: `subst` replaces every
occurrence of the named variable and nothing else, so $y = x$ with $x$ replaced by $y + 1$
becomes $y = y + 1$, which is false everywhere. That is the correct answer — there is no
state from which `x := y + 1` establishes $y = x$ — and a `subst` that tried to be clever
would get it wrong.

## Sequencing, choice, and assertion

For `S1; S2` the condition that must hold before `S2` is $wp(S_2, Q)$. That condition is
what `S1` has to establish, so it is `S1`'s postcondition:

$$wp(S_1; S_2,\; Q) \;=\; wp(S_1,\; wp(S_2, Q))$$

The inner call is the *later* statement. People write it the other way round because `S1`
runs first, and it is worth noticing that the error is invisible when the two statements
touch different variables and only surfaces when the second reads what the first wrote.

For `if b then S1 else S2`, both branches must reach $Q$ from wherever they are taken: when
$b$ holds, $wp(S_1, Q)$ is needed; when it does not, $wp(S_2, Q)$ is. So the precondition is
$(b \to wp(S_1, Q)) \land (\lnot b \to wp(S_2, Q))$. For `assert b`, the statement itself
fails unless $b$ holds, and afterwards $Q$ must hold, so the precondition is $b \land Q$.
For `skip`, nothing changes and $wp$ is $Q$ itself.

## The loop is opaque

A loop `while b do S` runs its body some number of times that depends on the state, and
$wp$ cannot unroll a number it does not know. The way through is to ask the programmer for
one fact that is true every time control reaches the top of the loop — an *invariant*
$I$ — and to treat the loop as a black box whose only interface is that fact:

$$wp(\texttt{while } b \texttt{ inv } I \texttt{ do } S,\; Q) \;=\; I$$

That is not a free lunch. Saying "$I$ is an invariant" is a claim, and the claim breaks
into two obligations that the loop leaves behind for someone to discharge. The body must
keep $I$ true: whenever $I$ holds and the guard lets the body run, the body must
re-establish $I$, which is $(I \land b) \to wp(S, I)$. And when the loop stops, $I$ together
with the failed guard must be enough for $Q$: $(I \land \lnot b) \to Q$. The lab's `vcs`
collects exactly these two per loop, then the body's own obligations against $I$.

Take the lab's program, which sums $1$ to $n$:

```text
s := 0; i := 0;
while i < n inv (i <= n and 2*s = i*(i+1)) do
    i := i + 1; s := s + i
```

with postcondition $2s = n(n+1)$. Work the preservation obligation by hand. The body is
`i := i + 1; s := s + i`, and $wp$ reads it backwards: first substitute $s + i$ for $s$ in
$I$, then $i + 1$ for $i$ in the result.

```python
def ev(e, st):
    tag = e[0]
    if tag == "num":
        return e[1]
    if tag == "var":
        return st[e[1]]
    if tag == "add":
        return ev(e[1], st) + ev(e[2], st)
    if tag == "mul":
        return ev(e[1], st) * ev(e[2], st)
    if tag == "eq":
        return ev(e[1], st) == ev(e[2], st)
    if tag == "le":
        return ev(e[1], st) <= ev(e[2], st)
    if tag == "lt":
        return ev(e[1], st) < ev(e[2], st)
    if tag == "not":
        return not ev(e[1], st)
    if tag == "and":
        return ev(e[1], st) and ev(e[2], st)
    if tag == "imp":
        return (not ev(e[1], st)) or ev(e[2], st)
    raise ValueError(tag)


def subst(node, name, expr):
    if node[0] == "var":
        return expr if node[1] == name else node
    if node[0] == "num":
        return node
    return (node[0],) + tuple(subst(k, name, expr) if isinstance(k, tuple) else k
                              for k in node[1:])


def show(n):
    tag = n[0]
    if tag == "num":
        return str(n[1])
    if tag == "var":
        return n[1]
    if tag == "not":
        return "not " + show(n[1])
    sym = {"add": "+", "mul": "*", "eq": "=", "le": "<=", "lt": "<", "and": "and", "imp": "->"}
    return "(" + show(n[1]) + " " + sym[tag] + " " + show(n[2]) + ")"


I, S, N = ("var", "i"), ("var", "s"), ("var", "n")
inv = ("and", ("le", I, N),
       ("eq", ("mul", ("num", 2), S), ("mul", I, ("add", I, ("num", 1)))))
guard = ("lt", I, N)

after_s = subst(inv, "s", ("add", S, I))            # i := i + 1 ; [s := s + i]
body_wp = subst(after_s, "i", ("add", I, ("num", 1)))   # [i := i + 1] ; ...
print(show(body_wp))
print(ev(body_wp, {"i": 2, "s": 3, "n": 5}))
print(ev(body_wp, {"i": 2, "s": 4, "n": 5}))

entry = subst(subst(inv, "i", ("num", 0)), "s", ("num", 0))   # wp of the two assignments
print(show(entry))
```

The first line printed is the body's precondition,
$(i + 1 \le n) \land (2(s + (i + 1)) = (i + 1)((i + 1) + 1))$. Put real numbers in. At
$i = 2$, $s = 3$, $n = 5$ the invariant holds ($2 \le 5$ and $6 = 2 \cdot 3$) and the guard
holds, and the body's precondition evaluates to `True`: $3 \le 5$, and
$2(3 + 3) = 12 = 3 \cdot 4$. At $i = 2$, $s = 4$ it prints `False` — $2(4 + 3) = 14$, not
12 — but that state never satisfies $I$ in the first place, so the implication
$(I \land b) \to wp(S, I)$ is not troubled by it. The last line is the whole program's
precondition, $I$ with $0$ written for $i$ and then for $s$: $(0 \le n) \land (0 = 0 \cdot 1)$,
which says the program is correct for any $n \ge 0$, and that is the right answer.

## Why $i \le n$ is in the invariant

The exit obligation is $(I \land \lnot(i < n)) \to 2s = n(n+1)$. With $i \le n$ in $I$ and
$i \ge n$ from the failed guard, $i = n$, and the invariant's equation becomes the
postcondition. Drop the conjunct and all the exit gives you is $i \ge n$, which is not
enough. The lab's last test refutes that weaker invariant with `bounded_check`, and the
state it reports is worth looking at:

```python
import itertools


def ev(e, st):
    tag = e[0]
    if tag == "num":
        return e[1]
    if tag == "var":
        return st[e[1]]
    if tag == "add":
        return ev(e[1], st) + ev(e[2], st)
    if tag == "mul":
        return ev(e[1], st) * ev(e[2], st)
    if tag == "eq":
        return ev(e[1], st) == ev(e[2], st)
    if tag == "lt":
        return ev(e[1], st) < ev(e[2], st)
    if tag == "not":
        return not ev(e[1], st)
    if tag == "and":
        return ev(e[1], st) and ev(e[2], st)
    if tag == "imp":
        return (not ev(e[1], st)) or ev(e[2], st)
    raise ValueError(tag)


def free_vars(node):
    found, stack = set(), [node]
    while stack:
        n = stack.pop()
        if n[0] == "var":
            found.add(n[1])
        stack.extend(k for k in n[1:] if isinstance(k, tuple))
    return sorted(found)


def bounded_check(formula, lo, hi):
    names = free_vars(formula)
    for values in itertools.product(range(lo, hi + 1), repeat=len(names)):
        st = dict(zip(names, values))
        if not ev(formula, st):
            return st
    return None


I, S, N = ("var", "i"), ("var", "s"), ("var", "n")
weak = ("eq", ("mul", ("num", 2), S), ("mul", I, ("add", I, ("num", 1))))
post = ("eq", ("mul", ("num", 2), S), ("mul", N, ("add", N, ("num", 1))))
exit_ob = ("imp", ("and", weak, ("not", ("lt", I, N))), post)
print(bounded_check(exit_ob, 0, 6))
```

It prints `{'i': 1, 'n': 0, 's': 1}`. Check it: $2 \cdot 1 = 1 \cdot 2$, so the weak
invariant holds; $1 < 0$ is false, so the guard has failed; and $2 \cdot 1 \ne 0 \cdot 1$,
so the postcondition does not hold. The program itself never reaches $i = 1$ with $n = 0$,
because the loop body would never have run. That is the point, and it is the second thing
people get wrong: an obligation is about the *annotation*, not about the run. The invariant
is all the verifier knows at the loop head, and if the invariant permits a state, the
verifier must answer for it. Adding $i \le n$ rules the state out, and the obligation goes
through.

## Where it stops holding

Partial correctness says nothing about termination. `while true do skip` with invariant
`true` discharges both obligations against any postcondition — the exit obligation's
antecedent is $\text{true} \land \lnot\text{true}$, which is false, so the implication is
vacuous. To prove the loop finishes you need a *variant*, a quantity that decreases on every
iteration and is bounded below; for the sum program it is $n - i$. The lab does not ask for
one, and its verdicts should be read with that clause attached.

`bounded_check` refutes and does not prove. `None` means "no state with every variable in
$[lo, hi]$ falsifies this", and the sum obligations are linear enough that seven values per
variable is convincing, but it is not a proof, and a non-linear obligation can hold on
$[0, 6]$ and fail at 7. The industrial answer is to hand each obligation to an SMT solver
such as Z3 — the propositional search of the previous module with integer arithmetic as
its theory — which either proves it or returns a state, the way `bounded_check` does, for
all integers at once.

Finally, the substitution rule is only true when $x := e$ changes $x$ and nothing else.
Arrays, pointers and aliased references break that: writing `a[i] := 3` can change what
`a[j]` denotes, and a calculus for those programs needs a model of the heap, which is where
separation logic comes in. The lab's language has integer variables only, so substitution
holds without qualification.

In the lab *A weakest-precondition calculator* you build `subst` and `wp` as the rules
above, `vcs` to collect the two obligations each loop leaves behind, and `bounded_check` to
try to refute them — and then you watch it refute the weak invariant with the state you
have now seen by hand.
''',
                },
            ],
            "quiz": {
                "title": "Preconditions, obligations, and what a refutation means",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The postcondition is $x \\le 10$ and the statement is `x := 2 * x`. Which precondition does the substitution rule give?",
                        "opts": [
                            "$x \\le 20$: the bound relaxed by the factor the statement multiplies $x$ by, since $x$ grows",
                            "$2x \\le 10$: the postcondition with the assigned expression written in place of $x$",
                            "$x \\le 10$ still, since the postcondition constrains the value after the assignment, not before",
                            "$x = 5$: the one starting value from which the assignment lands on the bound",
                        ],
                        "a": 1,
                        "whys": [
                            r"That is the forward reading: it computes where the statement *sends* states rather than which states it must start from. From $x = 20$ the assignment gives 40, well past the bound.",
                            r"$Q[x := e]$: write $2x$ wherever $Q$ mentions $x$, and stop.",
                            r"The postcondition does constrain the value afterwards, and that is why it cannot be the precondition unchanged: the value afterwards is $2x$, so the condition on the value before is $2x \le 10$.",
                            r"$x = 5$ is a valid precondition, but a strong one; $x = 3$ works too, and so does $x \le 5$. The rule asks for the weakest, the one that admits every safe start, and that is $2x \le 10$.",
                        ],
                        "why": r'''
$wp(x := e, Q)$ is $Q[x := e]$: substitute the assigned expression for the variable in the
postcondition. Here that is $2x \le 10$, equivalent to $x \le 5$. The tempting answer
$x \le 20$ comes from thinking forwards — the value doubles, so loosen the bound — and it
admits $x = 20$, from which the assignment reaches 40. Substitution refuses to reason about
direction, and that is why it is right.
''',
                    },
                    {
                        "q": "For `S1; S2` the rule is $wp(S_1, wp(S_2, Q))$ rather than $wp(S_2, wp(S_1, Q))$. Why is the later statement handled first?",
                        "opts": [
                            "`S1` runs first, so its transformer is applied first and `S2`'s is then applied to whatever it produces",
                            "The two orders give the same formula whenever the statements assign to different variables",
                            "`S1`'s precondition is the program's precondition, so it must be computed from the original $Q$",
                            "The condition needed before `S2` is what `S1` must establish, so `S2`'s transformer is applied first",
                        ],
                        "a": 3,
                        "whys": [
                            r"Execution order and transformer order are opposites, because $wp$ works from the end. Applying `S1`'s transformer to $Q$ asks what `S1` needs to reach $Q$ directly, which is not what `S1` has to reach at all.",
                            r"Sometimes, but `x := 1; y := x` and `y := x; x := 1` are different programs with different preconditions for $y = 1$. The orders coincide only when neither statement reads what the other writes, and a rule cannot depend on that.",
                            r"`S1`'s precondition is the program's, and it is computed from `S1`'s postcondition — which is not $Q$ but the condition `S2` needs. $Q$ is `S2`'s postcondition, and it enters the calculation there.",
                            r"$wp(S_2, Q)$ is what must hold between the two statements, and that is the postcondition `S1` is answerable for.",
                        ],
                        "why": r'''
Read the program backwards. $Q$ must hold after `S2`, so $wp(S_2, Q)$ must hold before
`S2`, which is the same moment as after `S1`. That intermediate condition is `S1`'s
postcondition, and `S1`'s precondition is $wp$ of it. The other order is tempting because
`S1` runs first, and the mistake hides whenever the two statements touch different
variables; it surfaces the moment `S2` reads something `S1` wrote.
''',
                    },
                    {
                        "q": "$wp$ of `while b inv I do S` against any $Q$ is $I$, nothing more. What justifies returning the annotation and ignoring $Q$?",
                        "opts": [
                            "$I$ is the strongest fact known at the loop head, so it is also the weakest precondition of the loop",
                            "The loop is opaque: $I$ is all that is assumed on entry, and its obligations are collected and checked separately",
                            "Unrolling the loop would give the true precondition, but that needs the iteration count, which is not known",
                            "$Q$ is entailed by $I \\land \\lnot b$, so $I$ already carries everything $Q$ says and adding $Q$ to it would be redundant",
                        ],
                        "a": 1,
                        "whys": [
                            r"Strongest and weakest are not the same word, and $I$ is neither of those things by itself; it is the programmer's claim. Returning it is a decision to trust the claim here and audit it elsewhere, in `vcs`.",
                            r"The two obligations — preservation and exit — are where $Q$ and the body come back in.",
                            r"Unrolling is what $wp$ cannot do, and that is the reason for the annotation, but it is not what justifies returning $I$. What justifies it is that the annotation is the loop's whole interface, with the obligations that make it honest computed by `vcs`.",
                            r"That entailment is exactly one of the obligations, and it may be *false* — the lab refutes it for the weak invariant. $wp$ does not assume it; `vcs` emits it to be checked, which is why $Q$ is absent from $wp$ and present in `vcs`.",
                        ],
                        "why": r'''
$wp$ cannot see through a loop, so it takes the invariant as the loop's entire interface:
what holds on entry is $I$, and that is what $wp$ returns. The cost is two obligations that
`vcs` collects — $(I \land b) \to wp(S, I)$ and $(I \land \lnot b) \to Q$ — and it is in the
second of these that $Q$ reappears. Returning $I$ is only sound because those obligations
are going to be checked; on their own, $wp$ and `vcs` are each half of the method.
''',
                    },
                    {
                        "q": "With $i \\le n$ dropped from the sum invariant, `bounded_check` refutes the exit obligation at $i = 1$, $n = 0$, $s = 1$. The program never reaches that state. Why does the refutation still count?",
                        "opts": [
                            "It does not count: a counterexample at a state the program cannot reach is a false alarm that the checker ought to filter out before reporting",
                            "The state is reachable after all, because $n = 0$ makes the body run once before the guard is first tested",
                            "An obligation is about the annotation, not the run: every state satisfying $I \\land \\lnot b$ must satisfy $Q$; this one does not",
                            "It shows the postcondition is wrong for $n = 0$, since a sum of no terms cannot be written as $n(n+1)/2$",
                        ],
                        "a": 2,
                        "whys": [
                            r"The checker cannot know what the program reaches; the invariant is its only description of the loop head. If the description permits a state, the checker must answer for it, and the fix is a better description, not a filter.",
                            r"The guard is tested before the body runs, and $0 < 0$ is false, so the body never runs and $i$ stays 0. The state $i = 1$ is not reached; it is *permitted* by an invariant that forgot to say so.",
                            r"The verifier knows the loop only through $I$, and this $I$ admits a state from which $Q$ fails.",
                            r"For $n = 0$ the postcondition $2s = 0$ holds with $s = 0$, which is what the program computes. The obligation fails at $s = 1$, a value the weak invariant permits and the program never produces.",
                        ],
                        "why": r'''
$wp$ threw the loop away and kept only $I$, so the verifier's picture of the loop head is
every state satisfying $I$, reachable or not. The weak invariant is satisfied by $i = 1$,
$s = 1$, and the failed guard admits $n = 0$, and from there $2s = n(n+1)$ is false. The
program would never get there, but the annotation did not say so, and the annotation is all
the verifier has. Restoring $i \le n$ excludes the state and the obligation holds throughout
the box.
''',
                    },
                    {
                        "q": "`bounded_check` returns `None` for every obligation of the sum program over the box $[0, 6]$. What has been established?",
                        "opts": [
                            "The obligations hold for all integers, since a linear obligation that holds at seven values holds everywhere",
                            "The program is totally correct: it terminates and meets its postcondition for every input $n$",
                            "The invariant is the strongest one available, since any weaker one would have produced a counterexample",
                            "No state with every variable in $0..6$ falsifies them; outside the box the obligations are unchecked",
                        ],
                        "a": 3,
                        "whys": [
                            r"The obligations are not linear — $i(i+1)$ is quadratic — and even for linear ones a box is not a proof. Seven values per variable is evidence, and the lab's brief says to report it as a refutation attempt.",
                            r"Nothing here spoke about termination; the calculus is for partial correctness, and `while true do skip` passes it. A variant such as $n - i$ would be needed, and `bounded_check` on a box says nothing about it either way.",
                            r"Strength is not what the check measures. A weaker invariant can pass too if it still implies the postcondition at exit; the invariant is strong *enough*, and that is all `None` can say.",
                            r"The box was searched exhaustively and nothing in it fails.",
                        ],
                        "why": r'''
`bounded_check` enumerates the box and returns the first falsifying state. `None` means
the box contains none, and says nothing about states outside it, about termination, or
about the invariant's strength. It is a refutation attempt, and a successful proof needs a
decision procedure over all integers — an SMT solver — rather than a finite search.
''',
                    },
                    {
                        "q": "`while true do skip` with invariant `true` discharges both obligations against any postcondition $Q$. What does that tell you?",
                        "opts": [
                            "Partial correctness is vacuous for a loop that never exits: the exit obligation's antecedent $I \\land \\lnot b$ is false",
                            "The calculus is unsound, because a program that computes nothing has been shown to meet every specification anyone could write",
                            "The invariant `true` is too weak, and a stronger invariant would have made the exit obligation fail as it should",
                            "The loop meets every postcondition because `skip` leaves the state unchanged, so whatever held before holds after",
                        ],
                        "a": 0,
                        "whys": [
                            r"$\text{true} \land \lnot\text{true}$ is false, so the exit obligation is an implication from a false antecedent.",
                            r"The calculus is sound for what it claims, which is *if the program terminates then $Q$*. This program never terminates, so the claim is true of it. Unsoundness would be proving a false statement, and no false statement was proved.",
                            r"A stronger invariant would also be preserved by `skip` and would also give a false antecedent at exit, because $\lnot\text{true}$ is false regardless of $I$. The vacuity is in the guard, not in the annotation.",
                            r"`skip` preserving the state is why the *preservation* obligation holds. The exit obligation holds for a different reason — the loop never exits — and it is that reason which makes the result say nothing about $Q$.",
                        ],
                        "why": r'''
A Hoare triple promises $Q$ *if* the program terminates. A loop with guard `true` never
does, so it satisfies every triple, and the exit obligation shows it: its antecedent
$I \land \lnot b$ is $\text{true} \land \text{false}$, and an implication from a false
antecedent holds. That is not unsoundness; it is the definition of partial correctness
doing what it says. Ruling the program out needs a termination argument, which is a variant,
and which this calculus does not ask for.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Every state the protocol can reach",
                    "minutes": 12,
                    "body": r'''
Two processes share one printer. Each of them, on its own, is a three-step cycle: it is
idle, then it wants the printer and waits, then it has the printer and prints, then it is
idle again. The rule that is meant to keep the two apart is a lock: a process may move from
waiting to printing only when the lock is free, and it takes the lock as it goes. The
disaster is both processes printing at once, interleaving their pages.

Suppose you want to know whether the rule works. You could run the two processes a million
times and watch. The trouble is that the scheduler decides who moves when, and the one
interleaving that breaks the rule may be one it never chooses in a million runs — and an
absence of failures tells you about the scheduler, not the protocol. The alternative is to
stop running and start enumerating: write down every configuration the pair can be in, and
every move from each, and look at all of them.

## From two processes to one system

A configuration is what each process is doing plus the state of the lock: a triple
$(m_1, m_2, \ell)$ with each $m$ in $\{\text{idle}, \text{wait}, \text{crit}\}$ and $\ell$
in $\{0, 1\}$. There are $3 \cdot 3 \cdot 2 = 18$ of them. A move is one process taking one
step while the other stands still; the scheduler's freedom to pick either process is what
makes the system *non-deterministic* — a state has more than one successor — and this is
*interleaving semantics*: two concurrent things become one sequential thing that branches.

That is enough to define the object the checker works on. A *Kripke structure* is a set of
states $S$, a set of initial states $I \subseteq S$, a transition relation
$R \subseteq S \times S$, and a labelling $L$ that gives each state the set of atomic facts
true in it. The labelling is there for a reason that is easy to miss: the checker does not
know what a triple means. It knows that a state is labelled `crit1` or `locked`, and a
property is a claim about labels, so the same checker serves a printer protocol and a
traffic light without change. The lab's `Kripke(initial, transitions, labels)` is this
structure with $R$ given as an ordered successor list per state.

## Reachability, and why it settles safety completely

"Both processes are never printing together" is a claim about every state the system can
*reach*, and a state is reachable when there is a finite path to it from an initial state.
Breadth-first search from the initial states visits every such state exactly once, so the
claim is checked by visiting each and testing the label. When the system is finite, the
search finishes, and a `None` from it is a proof: not "no failure was observed" but "no
reachable state violates the property", for every execution there is. That completeness is
what separates this from testing.

Breadth-first gives one thing more. States are dequeued in order of their distance from an
initial state, so the first violating state dequeued is at minimum distance, and if each
state remembers which state first reached it, the path back is a shortest violating
trace. That trace is the deliverable: a verdict of "unsafe" is an argument, and a five-state
trace a person can read is a proof.

```python
from collections import deque

MODES = ("idle", "wait", "crit")


def replace(state, index, value):
    parts = list(state)
    parts[index] = value
    return tuple(parts)


def mutex_model(safe):
    states = [(a, b, lock) for a in MODES for b in MODES for lock in (0, 1)]
    transitions = {}
    for state in states:
        nxt = []
        for i in (0, 1):
            mode = state[i]
            if mode == "idle":
                nxt.append(replace(state, i, "wait"))
            elif mode == "wait":
                if state[2] == 0 or not safe:
                    nxt.append(replace(replace(state, i, "crit"), 2, 1))
            else:
                nxt.append(replace(replace(state, i, "idle"), 2, 0))
        transitions[state] = nxt
    return [("idle", "idle", 0)], transitions


def both_critical(state):
    return state[0] == "crit" and state[1] == "crit"


def search(initial, transitions, bad):
    parent = {s: None for s in initial}
    queue = deque(initial)
    while queue:
        state = queue.popleft()
        if bad(state):
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(parent)
        for target in transitions[state]:
            if target not in parent:
                parent[target] = state
                queue.append(target)
    return None, len(parent)


for safe in (True, False):
    initial, transitions = mutex_model(safe)
    path, seen = search(initial, transitions, both_critical)
    print("safe" if safe else "unsafe", "explored", seen, "states")
    if path:
        for s in path:
            print("   ", s)
```

The safe protocol prints `safe explored 8 states` and no trace: of the 18 configurations,
only 8 are reachable, and none of them has both processes in `crit`. Look at which are
missing — `(crit, idle, 0)` is not among the 8, because a process in `crit` always holds
the lock, and that fact has now been proved for every execution, not observed in some.

The unsafe protocol, where the waiting process moves to `crit` without looking at the lock,
prints `unsafe explored 9 states` and then five lines: `(idle, idle, 0)`, `(wait, idle, 0)`,
`(crit, idle, 1)`, `(crit, wait, 1)`, `(crit, crit, 1)`. Read it as a story. Process 1
asks, process 1 enters and takes the lock, process 2 asks, process 2 enters although the
lock is held. Four transitions; the lab's test asserts the trace has five states because no
shorter one exists, and breadth-first is what guarantees that.

One detail in the search matters more than it looks. The predicate is tested when a state
is *dequeued*, not when it is enqueued. If an initial state itself violates the property,
enqueue-time testing never looks at it — nothing enqueued it — and the checker reports a
clean system that is broken at time zero.

## Bounded search: sound but incomplete

`check_always(pred, bound)` is the same search cut off at depth `bound`. Every trace it
returns is a real trace, so a counterexample from it is as good as one from the full
search: the method is *sound*. But `None` from it means only that no violation lies within
`bound` transitions, and the lab's test makes the gap concrete: a bound of 3 on the unsafe
protocol finds nothing, because the shortest violation takes four transitions, and a bound
of 4 finds it. The mistake people make is to read that `None` as "safe". It is tempting
because the full search's `None` does mean that, and the two calls look alike; they differ
in exactly the word "within".

Why bother with a bound at all, if the full search is complete? Because the full search
needs the whole reachable set to fit in memory, and a bound trades completeness for a
search that finishes on systems where it does not.

## Always, eventually, and the shape of a counterexample

Mutual exclusion is "always not both", $G\,\lnot(\text{crit}_1 \land \text{crit}_2)$. Its
counterexample is a finite path ending in a state where the property fails, which is what
the search above returns. A different kind of claim is "process 1 eventually prints",
$F\,\text{crit}_1$, and its counterexample has a different shape, because no single state
refutes it: a path along which `crit1` never holds, and which goes on forever. In a finite
system "forever" means a cycle, and within a bound it means a path that uses every one of its
`bound` transitions without a witness, or one that reaches a state with no successors at
all — a deadlock, where waiting forever is the only thing left.

```python
MODES = ("idle", "wait", "crit")


def replace(state, index, value):
    parts = list(state)
    parts[index] = value
    return tuple(parts)


def mutex_model():
    states = [(a, b, lock) for a in MODES for b in MODES for lock in (0, 1)]
    transitions = {}
    for state in states:
        nxt = []
        for i in (0, 1):
            mode = state[i]
            if mode == "idle":
                nxt.append(replace(state, i, "wait"))
            elif mode == "wait":
                if state[2] == 0:
                    nxt.append(replace(replace(state, i, "crit"), 2, 1))
            else:
                nxt.append(replace(replace(state, i, "idle"), 2, 0))
        transitions[state] = nxt
    return [("idle", "idle", 0)], transitions


def eventually(initial, transitions, good, bound):
    def walk(path, left):
        state = path[-1]
        if good(state):
            return None                 # this path already has its witness
        nxt = transitions[state]
        if left == 0 or not nxt:
            return list(path)           # bound used up, or deadlocked
        for target in nxt:
            found = walk(path + [target], left - 1)
            if found is not None:
                return found
        return None

    for s in initial:
        found = walk([s], bound)
        if found is not None:
            return found
    return None


initial, transitions = mutex_model()
for s in eventually(initial, transitions, lambda s: s[0] == "crit", 6):
    print(s)
```

This is the *safe* protocol, and it prints seven states: process 1 moves to `wait` and then
stays there while process 2 waits, enters, leaves, waits, enters again. Nothing in the
protocol says the lock has to go to the process that asked first, so a scheduler that always
favours process 2 starves process 1. The search is depth-first, because a counterexample to
$F$ is a long path rather than a near state, and it prunes the moment `good` holds — that
branch has its witness and cannot be part of a counterexample.

## Where it stops holding

Is the starvation trace a bug? The protocol does guarantee mutual exclusion, which was the
claim, and it does not guarantee progress, which was not. Whether the second matters depends
on an assumption the model does not contain: a *fairness* constraint, which says a process
that is continuously able to move eventually does. Real checkers let you state that, and
liveness verdicts without it are mostly reports about the absence of a scheduler.

The model is also only as honest as its abstraction. The lock here is a variable that is
read and written in one move; on real hardware it is a compare-and-swap with a memory
model behind it, and the interleavings the model shows are a subset of the ones the chip
allows. A model checker proves things about the model, and the gap between the model and the
program is the modeller's to close.

Finally, the reachable set is a product. Two processes with three modes and a lock gave 18
states. Ten give $3^{10} \cdot 2 = 118{,}098$; twenty give about seven billion. Explicit-state
search stores each one, and it stops at a few hundred million on a big machine. Everything
beyond is the field's response to this: symbolic representations of state sets, partial-order
reduction that ignores interleavings which cannot matter, and *bounded model checking*,
which unrolls the transition relation $k$ times into one propositional formula and hands
it to the SAT solver from the first module. The state explosion is why that first module
exists in a course on verification.

In the lab *Model checking a mutual-exclusion protocol* you build the `Kripke` class:
`reachable` and `check_invariant` as the breadth-first search above with parent pointers,
`check_always` as the same search with a depth cut, and `check_eventually` as the pruned
depth-first walk — and you watch it prove one protocol safe, refute the other with a
five-state trace, and show that the safe one still lets a process wait forever.
''',
                },
            ],
            "quiz": {
                "title": "Reachability, bounds, and the two shapes of counterexample",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Why is the protocol modelled as one transition system over $(m_1, m_2, \\ell)$ triples rather than as two separate three-state systems?",
                        "opts": [
                            "Two separate systems would have three states each, which is too few for breadth-first search to find anything at all",
                            "A violation of mutual exclusion is a fact about both processes at once, and only a joint state can express it",
                            "A shared lock cannot be represented unless every variable of the program is stored in a single tuple",
                            "Separate systems would need two searches, and merging the two counterexample traces is not possible",
                        ],
                        "a": 1,
                        "whys": [
                            r"Size is not the issue; a three-state system is searched in three steps. The issue is that neither of the small systems has a state meaning *both* are in `crit`, so the property cannot even be written against them.",
                            r"`crit1 and crit2` is a label on a joint state; no state of either process alone carries it.",
                            r"Storage is a representation choice, and the lock could be its own component. The reason for the product is semantic: interleaving the two processes is what produces the executions in which they interfere.",
                            r"The searches would be trivial and their traces would say nothing, because each process on its own is correct. The defect exists only in the way the two interleave, and that is what the product system captures.",
                        ],
                        "why": r'''
Each process on its own is a correct three-step cycle. The defect, if there is one, lies in
how the two interleave, and interleaving semantics builds the one non-deterministic system
whose states are pairs of process states plus the lock. Mutual exclusion is a label on
those joint states — `crit1` and `crit2` together — and a claim about them cannot be stated,
let alone checked, on either component alone.
''',
                    },
                    {
                        "q": "`check_invariant` returns the path to the first violating state that breadth-first search dequeues. Why is that path a shortest one?",
                        "opts": [
                            "Every path in the transition system to a given state has the same length, so any path found is a shortest one",
                            "The parent map records only the first parent seen, and overwriting it later would produce a longer path",
                            "Breadth-first dequeues states in order of distance from an initial state, so the first violation seen is at least depth",
                            "Successors are explored in the order the model lists them, and the model always lists the shortest route to each state first",
                        ],
                        "a": 2,
                        "whys": [
                            r"A state can be reached by paths of many lengths — the unsafe protocol's violating state can be reached in four transitions or in forty. Breadth-first is what picks out the four.",
                            r"Keeping the first parent is *how* the shortest path is recorded, but it is only correct because breadth-first reaches each state first along a shortest route. Under depth-first the first parent seen can be at the end of a long detour.",
                            r"All states at depth $d$ are dequeued before any at depth $d+1$, and a violation at depth $d$ is dequeued before any deeper one.",
                            r"Successor order decides which of several equally short paths is returned, not whether the path is short. The model lists moves for process 1 before process 2 and knows nothing about routes.",
                        ],
                        "why": r'''
Breadth-first search explores in layers: every state at distance $d$ is dequeued before
any at distance $d+1$. The first violating state dequeued is therefore at minimum distance,
and the parent pointer chain — each state remembering the state that first reached it — is
a path of that length. The lab checks this with the unsafe protocol, whose shortest
violation has five states, and with `check_always(both, 3)` returning `None` because four
transitions are needed.
''',
                    },
                    {
                        "q": "`check_always(both, 3)` on the unsafe protocol returns `None`. What follows from that?",
                        "opts": [
                            "The unsafe protocol is safe for three steps, so any violation must involve a process re-entering `crit`",
                            "The bound was ignored, since breadth-first search explores the whole reachable set before it can stop",
                            "Mutual exclusion holds, because an invariant violation is always found within the number of processes plus one",
                            "Nothing about safety: the shortest violation takes four transitions, and a bound of three cannot reach it",
                        ],
                        "a": 3,
                        "whys": [
                            r"Three transitions cannot put both processes in `crit` because each needs two moves to get there, and that is arithmetic about the bound, not a property of the protocol. No re-entry is involved in the four-step violation.",
                            r"The bound is honoured: a state at depth 3 is dequeued and tested but its successors are not enqueued. That is the point of `check_always`, and it is why the result changes between bounds 3 and 4.",
                            r"There is no such rule. A violation can lie arbitrarily deep, and the number of processes says nothing about where. The lab's four-step trace happens to be short because the protocol is tiny.",
                            r"Bounded search is sound — every trace it returns is real — and incomplete: `None` says only that no violation lies within the bound.",
                        ],
                        "why": r'''
A bounded search says "no violation within `bound` transitions", and that is all it says.
The unsafe protocol's shortest violation needs four moves — ask, enter, ask, enter — so a
bound of three stops one move short, and `None` is what an incomplete search reports. The
lab's next assertion, that a bound of four returns the five-state trace, is the same fact
seen from the other side. Reading a bounded `None` as a safety proof is the mistake to
watch for.
''',
                    },
                    {
                        "q": "What does a counterexample to $F\\,p$ (eventually $p$) look like, as against a counterexample to $G\\,p$ (always $p$)?",
                        "opts": [
                            "A single state in which $p$ is false, found by the same breadth-first search that refutes $G\\,p$",
                            "A whole path along which $p$ never holds, rather than a path ending in one state where $p$ fails",
                            "A cycle of states in which $p$ holds throughout, showing that $p$ can be reached but never left",
                            "A deadlocked state in which $p$ holds, since deadlock is the only way an eventuality can be denied",
                        ],
                        "a": 1,
                        "whys": [
                            r"One state where $p$ is false refutes *always* $p$; it says nothing against *eventually* $p$, because $p$ might hold two steps later. An eventuality is denied only by a whole path.",
                            r"$F\,p$ fails on an execution with no witness anywhere along it: within a bound, a path that uses every transition, or ends in deadlock, without $p$.",
                            r"A cycle where $p$ holds is a witness *for* $F\,p$, many times over. The refuting cycle is one where $p$ never holds, which is the shape the starvation trace has: process 2 cycling while process 1 waits.",
                            r"Deadlock is one way an eventuality is denied, when $p$ has not yet held; a deadlocked state where $p$ *holds* is a witness. The other way is a path that goes on without $p$ forever, which needs no deadlock at all.",
                        ],
                        "why": r'''
$G\,p$ is refuted by reaching one bad state, so its counterexample is a finite prefix and a
breadth-first search finds the shortest. $F\,p$ is refuted only by an execution on which $p$
never holds, so its counterexample is a path — infinite in principle, and within a bound
either one that spends every transition without a witness or one that reaches a state with
no successors. The lab's `check_eventually` is a depth-first walk for that shape, pruned
wherever $p$ holds because such a branch has its witness.
''',
                    },
                    {
                        "q": "On the safe protocol, `check_eventually(lambda ap: \"crit1\" in ap, 8)` returns a trace along which process 1 never enters. Is mutual exclusion broken?",
                        "opts": [
                            "Yes: a state where process 1 waits while process 2 holds the lock is exactly the violation the search looks for",
                            "No: the trace is an artefact of the bound, and with a larger bound process 1 would be found to enter the printer eventually",
                            "No: the trace shows process 1 can starve while process 2 cycles, which is a liveness failure and not a safety one",
                            "Yes: any trace a checker returns is a genuine violation of whatever property was passed to it, and this one was",
                        ],
                        "a": 2,
                        "whys": [
                            r"That state is fine for mutual exclusion — only one process is in `crit`. Waiting while another holds the lock is what the lock is for; waiting *forever* is a different complaint, and it is the one this trace makes.",
                            r"No bound helps: process 2 can cycle through `wait`, `crit`, `idle` indefinitely with nothing in the protocol obliging the scheduler to run process 1. The trace is genuine and grows with the bound.",
                            r"The property refuted was $F\,\text{crit}_1$, a liveness claim; $G\,\lnot(\text{crit}_1 \land \text{crit}_2)$ still holds in every reachable state.",
                            r"The trace is a genuine violation — of *eventually* `crit1`, the property that was passed. Mutual exclusion is a different property, checked by `check_invariant`, and the same lab proves it holds for the safe protocol.",
                        ],
                        "why": r'''
The property that was refuted is $F\,\text{crit}_1$: does process 1 always get in
eventually? It does not, because the protocol never obliges the scheduler to run it, and
process 2 can take the lock again and again. That is a liveness failure, starvation.
Mutual exclusion is a safety property, $G\,\lnot(\text{crit}_1 \land \text{crit}_2)$, and
the same protocol satisfies it in every one of its eight reachable states. Whether
starvation counts as a bug depends on a fairness assumption the model does not contain.
''',
                    },
                    {
                        "q": "Ten copies of the process, each with three modes, share one lock. How many states does the product have, and what does the number mean for explicit-state checking?",
                        "opts": [
                            "$3 \\cdot 10 \\cdot 2 = 60$: the state count adds per component, so explicit search scales linearly with the number of processes",
                            "$3^{10} \\cdot 2 = 118{,}098$: the state count multiplies per component, which is what limits explicit-state search",
                            "$3^{10} = 59{,}049$: the lock adds no states because its value is fixed by which process is in `crit`",
                            "$10 \\cdot 2 = 20$ reachable states: symmetry among identical processes collapses the product to a sum",
                        ],
                        "a": 1,
                        "whys": [
                            r"A joint state fixes the mode of *every* process at once, so the choices multiply: each process's three modes against each other's. Addition counts something else — the states if only one process existed at a time.",
                            r"Every combination of ten modes and two lock values is a distinct configuration of the system.",
                            r"In the reachable set of a correct protocol the lock is determined by the modes, but the state space is the set of all configurations, reachable or not, and the checker must represent both values. Determined-in-practice does not shrink the product.",
                            r"Symmetry reduction is a real technique and it does shrink the search, but not to a sum — it divides by permutations of identical processes at best, leaving the count exponential. And the raw product is what a plain explicit-state checker stores.",
                        ],
                        "why": r'''
A joint state is one mode for each of the ten processes plus the lock, so the count is a
product: $3^{10}$ mode combinations times 2 lock values, 118,098 states. Twenty processes
give about seven billion. Explicit-state search stores every state it visits, and that
product is the wall it hits; symbolic representations, partial-order reduction and bounded
model checking through a SAT solver are the responses to it.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Refuting with random data, then making the refutation small",
                    "minutes": 12,
                    "body": r'''
Someone on your team writes `dedup`, a function that is meant to remove duplicate elements
from a list while keeping the order of first appearance. They test it: `[1, 1, 2]` becomes
`[1, 2]`, and `[3, 3, 3, 1]` becomes `[3, 1]`. Both pass, the function ships, and three
weeks later a report arrives that `[1, 2, 1]` comes back as `[1, 2, 1]`.

```python
def dedup(xs):
    out = []
    for x in xs:
        if not out or out[-1] != x:
            out.append(x)
    return out


def unique(xs):
    return len(dedup(xs)) == len(set(dedup(xs)))


for xs in ([], [1, 1, 2], [3, 3, 3, 1], [1, 2, 1]):
    print(xs, dedup(xs), unique(xs))
```

The function compares each element with the *last one kept*, so it removes duplicates that
are adjacent and nothing else. The two hand-written tests both used adjacent duplicates,
and that is no accident: the person who chose the tests is the person who had "adjacent"
in their head when they wrote the code. Example tests probe the inputs the author thought
of, and a bug lives precisely in the inputs the author did not think of. This module is
about having something other than the author choose the inputs.

## A property is a claim about every input

Write down what `dedup` is supposed to guarantee, without reference to any particular
list: for every list `xs`, the result has no repeated elements. In symbols,
$\forall\, xs.\; |\text{dedup}(xs)| = |\text{set}(\text{dedup}(xs))|$. That is a
*property*: a universally quantified claim, which is what a specification is. A test is one
instance of it, one `xs` for which the claim has been checked. The claim is refuted by a
single counterexample and is never established by any number of passing instances, and
that asymmetry is the whole method: since you cannot prove it by testing, spend the testing
budget on looking for the counterexample as hard as possible, in the places you would not
have looked yourself.

The `unique` function above is that property as code. It takes a value and returns a bool,
and a value on which it returns a falsy result — or raises — is a counterexample. The
raising case matters: a property that throws `IndexError` on some input has been refuted
at that input as surely as one that returns `False`, and the lab's `fails` treats both the
same, so that the exception is minimised rather than allowed to crash the run.

## A generator carries its own notion of smaller

Random inputs need a source, and the source needs to know the type: a list of small
integers, of a bounded length. Call that a *generator*. The first thing a generator does is
draw a value from a `random.Random`. The second thing it does is less obvious and is the
reason the lab pairs the two in one `Gen` object: given a value, it says which values are
*smaller* than it, in an order from most aggressive to least.

Why does drawing need to know about smaller? Because a random counterexample is
random. It will be something like `[0, 0, 0, 2, 0]`, and the bug is not in the five
elements; it is in two of them. Reducing that list to the two that matter needs to know what
a smaller list is — shorter, or with smaller elements — and only the thing that built the
list knows its type. So the generator for integers in $[lo, hi]$ shrinks towards 0 (clamped
into the range): first the target itself, then halfway to it, then one step. The generator
for lists offers, in this order, the empty list, each half, each single-element deletion,
and each list with one element replaced by one of that element's own shrinks. The order is
biggest jump first, because a candidate that fails lets the search skip everything smaller
than it.

## Greedy shrinking, carried through

Shrinking is a loop: ask the generator for the candidates of the current value, take the
*first* one on which the property still fails, make it current, and start again. When no
candidate fails, stop. Here is the whole framework, with the trace of what it does to the
`dedup` failure:

```python
import random


def dedup(xs):
    out = []
    for x in xs:
        if not out or out[-1] != x:
            out.append(x)
    return out


def unique(xs):
    return len(dedup(xs)) == len(set(dedup(xs)))


def fails(prop, value):
    try:
        return not prop(value)
    except Exception:
        return True


def shrink_int(v):                      # towards 0, biggest jump first
    out = []
    for c in (0, v - v // 2, v - 1 if v > 0 else v + 1):
        if abs(c) < abs(v) and c not in out:
            out.append(c)
    return out


def shrink_list(v):
    cands = []
    if v:
        cands.append([])
        half = len(v) // 2
        if half:
            cands.append(v[:half])
            cands.append(v[half:])
        for i in range(len(v)):
            cands.append(v[:i] + v[i + 1:])
        for i, item in enumerate(v):
            for smaller in shrink_int(item):
                cands.append(v[:i] + [smaller] + v[i + 1:])
    out = []
    for c in cands:
        if c != v and c not in out:
            out.append(c)
    return out


def shrink_value(value, prop):
    current = value
    while True:
        for cand in shrink_list(current):
            if fails(prop, cand):
                print(current, "->", cand)
                current = cand
                break
        else:
            return current


rng = random.Random(7)
for trial in range(1, 201):
    n = rng.randint(0, 6)
    xs = [rng.randint(0, 3) for _ in range(n)]
    if fails(unique, xs):
        print("trial", trial, "failed on", xs)
        print("minimal:", shrink_value(xs, unique))
        break
```

With seed 7 the second trial draws `[0, 0, 0, 2, 0]`, and `dedup` of it is `[0, 2, 0]`,
which has a repeat. Now follow the shrinker. The candidates for `[0, 0, 0, 2, 0]` begin with
`[]`, which `unique` accepts — it is not a failure, so it is skipped. The first half
`[0, 0]` dedups to `[0]`, accepted. The second half `[0, 2, 0]` dedups to itself, and that
is a failure, so the shrinker prints `[0, 0, 0, 2, 0] -> [0, 2, 0]` and starts over from
there. For `[0, 2, 0]`, the empty list and both halves pass, and so do all three
single-element deletions — `[2, 0]`, `[0, 0]` and `[0, 2]` each dedup to something with no
repeat. Then the element-wise candidates: replacing the 2 by its first shrink, 0, gives
`[0, 0, 0]`, which passes; replacing it by 1 gives `[0, 1, 0]`, which fails. The shrinker
prints `[0, 2, 0] -> [0, 1, 0]`. From `[0, 1, 0]` nothing offered fails, so the loop's
`else` branch returns it, and the last line printed is `minimal: [0, 1, 0]`.

That is the counterexample worth reading: two equal elements with one different element
between them, and nothing else. The random draw found the bug; the shrinker turned the
finding into a sentence. The lab's `check` is this loop, and its test asserts that the
result has three elements and that deleting any one of them makes the property pass.

## Local, not global

"Minimal" here means something precise and something modest: no candidate the shrinker
offers from `[0, 1, 0]` still fails. It does not mean no smaller failing list exists in some
absolute sense. `[1, 0, 1]` fails too and is the same size; and if the generator's shrinks
were different, the fixed point would be different. Greedy shrinking reaches a *local*
minimum for the generator's ordering, and the claim to make about a shrunk value is that
one. It is a strong enough claim to be useful — a three-element counterexample is a bug
report — and a weaker one than people tend to assume.

## The mistakes people make

The first is the shrinker that offers the value it was given. If `shrink(v)` ever returns
`v` itself, or a candidate that is not strictly smaller by some well-founded measure, the
greedy loop takes it, starts again from the same place, and never stops. The lab's integer
shrinker guards with `abs(c - target) < abs(value - target)`, and its list shrinker
filters out `v`; both are there because the loop's termination depends on them and nothing
else enforces it.

The second is catching only `False`. A property that raises on some input is a failure, and
if `fails` lets the exception through, the framework dies on the first raising trial with a
stack trace instead of a shrunk counterexample. It is tempting because an exception feels
like a bug in the test rather than a result of it; the lab's `_boom` test exists to remove
that instinct.

The third is the unseeded run. A counterexample found by an unseeded generator is one that
cannot be produced again on demand, and a bug that reproduces "sometimes" is a rumour. The
lab's `check` takes a seed and builds `random.Random(seed)` from it, and its test runs the
same seed twice and asserts the same answer, because the value of a random failure is
entirely in being able to show it to someone else.

## Where it stops holding

Testing refutes and never verifies; that is the first sentence of this module restated, and
it has a sharper corollary. The inputs a run explores are whatever the generator's
distribution happens to reach. Run `check` with `ints(0, 0)` as the element generator and
every list is a run of zeros, every run is one element after `dedup`, and `unique` passes
200 times. The lab's last test asserts exactly that `None`, not because `dedup` is right but
because that distribution cannot see the way it is wrong. Widen the range to `ints(0, 3)`
and the bug is found on the second trial. Nothing about the function changed.

A passing property can also be the wrong property. `dedup(dedup(xs)) == dedup(xs)` — the
function is idempotent — passes every trial too, and it is true: the buggy `dedup` is
idempotent. A property that the wrong implementation satisfies cannot separate it from the
right one, and the lab's test names this case "dedup is idempotent even though it is wrong".
Round-trip and metamorphic properties are powerful because they need no reference
implementation, and they are only as good as what they fail to permit.

And the search is over a distribution, so its reach is probabilistic. Two hundred lists of
up to six elements drawn from four values is a few hundred of the $4^0 + \dots + 4^6 = 5461$
possible lists, which is fine when a third of them expose the bug and useless when one does.
The previous two modules are what to reach for when the failing input is a needle — a
model checker enumerates instead of sampling, and a proof does not look for inputs at all.
The capstone puts all three against one ring buffer to see which catches what.

In the lab *A generator and shrinker framework* you build `fails`, the `ints` and `lists`
generators with the shrink orders above, `shrink_value` as the greedy loop, and `check` as
the seeded search that hands the first failure to the shrinker — and its final assertion is
that the counterexample it returns for `dedup` is the three-element one you have followed
here.
''',
                },
            ],
            "quiz": {
                "title": "Properties, shrinking, and what a passing run does not say",
                "minutes": 8,
                "questions": [
                    {
                        "q": "`dedup` passed `[1, 1, 2]` and `[3, 3, 3, 1]` and failed in production on `[1, 2, 1]`. What is the lesson about the two tests?",
                        "opts": [
                            "Two tests are too few; with ten hand-written examples the non-adjacent case would have been covered",
                            "The tests were wrong: three copies is a different case from two, so `[3, 3, 3, 1]` should not have been used as a test",
                            "Example tests probe the inputs the author thought of, and the author of this bug thought only of adjacent duplicates",
                            "Example tests are unsuitable for list functions, because a list has infinitely many possible inputs",
                        ],
                        "a": 2,
                        "whys": [
                            r"Ten examples chosen by the same person would very likely all have adjacent duplicates too. The problem is who chooses, not how many; a random generator finds the non-adjacent case on its second draw.",
                            r"`[3, 3, 3, 1]` is a fine test and it passes correctly. The gap is not between two and three copies but between adjacent and separated ones, which neither test explores.",
                            r"The same mental model that produced the bug produced the tests, so the tests could not see it.",
                            r"Example tests are useful for lists and everything else; they pin down cases you know about. They are insufficient rather than unsuitable, and the remedy is to add inputs you did not choose, not to drop the ones you did.",
                        ],
                        "why": r'''
The person who wrote `dedup` had "adjacent" in mind, and the person who wrote the tests
was the same person with the same idea. Hand-picked examples check the inputs the author
imagined, and a bug is by definition in an input the author did not. Property-based
testing hands the choice of inputs to a generator, and the reading's run finds `[0, 2, 0]`
on its second trial with no one having thought of it.
''',
                    },
                    {
                        "q": "Why does a `Gen` carry a shrink function alongside its draw function, rather than leaving shrinking to the framework?",
                        "opts": [
                            "Shrinking is how the generator produces its next random value, by shrinking the previous one it drew",
                            "The shrink function replays the random draw with a smaller seed in order to reproduce the failure",
                            "Shrinking keeps generated values inside the bounds, since a raw draw can overshoot the range it was given",
                            "Only the generator knows what smaller means for its type, and a random failure is rarely already small",
                        ],
                        "a": 3,
                        "whys": [
                            r"Drawing and shrinking are separate operations on separate inputs: `generate` takes an RNG and makes a value, `shrink` takes a value and lists smaller ones. Neither feeds the other.",
                            r"Seeds have nothing to do with it. Shrinking is a deterministic walk over candidate values, and the seed's only role is to make the initial draw repeatable.",
                            r"A draw is in range by construction — `randint(lo, hi)` cannot overshoot. Shrink candidates are clamped into range, but that is a property the shrinker must maintain, not its purpose.",
                            r"A framework sees only opaque values; the type-specific idea of a smaller list or a smaller integer lives with the generator.",
                        ],
                        "why": r'''
A generic framework can compare nothing: it does not know that a shorter list is smaller,
that an integer nearer zero is smaller, or how to make a candidate from a value. The
generator does, because it built the value. Pairing draw with shrink in one object is what
lets `shrink_value` and `check` be written once for every type, and it is why the lab's
`lists` generator delegates element shrinking to the element generator it was given.
''',
                    },
                    {
                        "q": "`shrink_value` took `[0, 0, 0, 2, 0]` to `[0, 2, 0]` to `[0, 1, 0]` and stopped. What kind of minimality has been reached?",
                        "opts": [
                            "Global: no shorter list fails the property, because every shorter list was already tried during the halving steps",
                            "Local: no candidate the shrinker offers from `[0, 1, 0]` still fails, though a different small failure may exist",
                            "Global: the shrinker considers every list smaller in length or in element value before it stops",
                            "Neither: the shrinker stops when the candidate list is exhausted, which has no connection to size at all",
                        ],
                        "a": 1,
                        "whys": [
                            r"The halves are two candidates, not every shorter list. From `[0, 1, 0]` the shrinker looks at a handful of neighbours; `[1, 0, 1]` fails too and is never considered, because it is not a neighbour.",
                            r"Greedy descent stops at a fixed point of the generator's candidate set, and that is a local minimum.",
                            r"That would be an exhaustive search over a space that grows exponentially; the shrinker looks at the candidates its generator lists and nothing else. Its economy is the reason it terminates fast.",
                            r"The stopping condition — no candidate fails — is a statement about size, because every candidate is strictly smaller by the generator's measure. What it does not say is anything about lists that are not candidates.",
                        ],
                        "why": r'''
Greedy shrinking takes the first failing candidate and repeats, and it stops when no
candidate fails. That is a local minimum under the generator's ordering: nothing one step
smaller still fails. It is not a global one — `[1, 0, 1]` is a different failure of the same
size, and a different candidate order could land elsewhere. The lab's test checks the
local claim, that deleting any single element of the result makes the property pass.
''',
                    },
                    {
                        "q": "`fails(prop, value)` returns `True` when `prop` raises. Why catch the exception instead of letting it propagate?",
                        "opts": [
                            "Exceptions inside properties are bugs in the test harness and should be silenced so the run can continue",
                            "A property that raises has been refuted at that value, and the framework should minimise it rather than crash",
                            "Letting it propagate would stop the shrinker from reaching a value that returns `False`, the only real failure",
                            "Catching it keeps the random sequence in step, so that the next trial draws the value it otherwise would have",
                        ],
                        "a": 1,
                        "whys": [
                            r"An exception in a property is a result, not noise: it says the code under test blew up on that input. Silencing it to continue would discard the counterexample; recording it as a failure keeps it.",
                            r"A raise is a failure like any other, and one the shrinker should get to work on.",
                            r"A raise and a `False` are the same kind of thing to the framework — evidence against the property at that value. There is no need to keep searching for a `False` once a raise has been found.",
                            r"The random sequence advances at `generate`, before the property runs, so an exception in the property cannot put it out of step. The reason to catch it is what the exception means, not bookkeeping.",
                        ],
                        "why": r'''
The specification is that `prop` holds on every input. An input on which `prop` raises is
an input on which it does not hold, and it is usually the more interesting failure — an
`IndexError` out of the code under test rather than a polite `False`. Treating a raise as a
failure lets `shrink_value` reduce it to a minimal raising input; letting it propagate
turns the first such trial into a crash with no minimisation.
''',
                    },
                    {
                        "q": "`check(lists(ints(0, 0), 6), unique)` returns `None` although `dedup` is wrong. What has this run shown?",
                        "opts": [
                            "`dedup` is correct for lists of small integers, since two hundred trials over the range passed without a single failure",
                            "The property is false here: a run of zeros dedups to a single zero, which is not equal to the original list",
                            "Nothing about `dedup` in general: every list of equal elements is one run, so this distribution cannot reach the bug",
                            "The generator is defective: a range holding one value cannot produce the variety a random test needs",
                        ],
                        "a": 2,
                        "whys": [
                            r"It is correct for lists of *one* value, which is what the generator produced. Widen the range to four values and the same `check` fails on its second trial; the function did not change, the distribution did.",
                            r"`unique` compares the length of the deduplicated list with the size of its set, not with the original list. `[0, 0, 0]` dedups to `[0]`, which has no repeats, so the property holds on it as it should.",
                            r"Coverage is the generator's distribution, and a distribution that never separates two equal elements can never see this bug.",
                            r"`ints(0, 0)` is a valid generator that does what it was asked. The run says something true about that distribution — no failure exists in it — and the lesson is about what such a `None` means, not that the generator is broken.",
                        ],
                        "why": r'''
Testing explores the generator's distribution and nothing outside it. With a single
possible element, every list is one run of equal values, `dedup` collapses it to one
element, and `unique` holds — the bug needs two equal elements separated by a different
one, and no such list can be drawn. `None` means "no failure in this distribution", and the
lab's last test asserts it for that reason.
''',
                    },
                    {
                        "q": "`dedup(dedup(xs)) == dedup(xs)` passes two hundred trials, and `dedup` is known to be wrong. What does that say about the property?",
                        "opts": [
                            "It is the wrong kind of property, because idempotence can only be checked against hand-picked examples",
                            "Two hundred trials were too few, and a larger trial count would have found the input on which idempotence fails",
                            "It holds of the buggy function as well, so it cannot separate the correct implementation from this wrong one",
                            "Seed 7 happened to avoid the failing inputs, and a different seed would have produced a counterexample",
                        ],
                        "a": 2,
                        "whys": [
                            r"Idempotence is a perfectly good property to check by random trial. The trouble is with what it can distinguish, not with how it is tested.",
                            r"No count would help, because there is no such input: adjacent-only deduplication, applied twice, gives what it gave once. The property is true of the buggy function.",
                            r"A property both implementations satisfy carries no evidence about which one you have.",
                            r"Seeds change which inputs are drawn, not which inputs fail, and none fail. The reading's point is that a true property of a wrong function is still true.",
                        ],
                        "why": r'''
The buggy `dedup` removes adjacent duplicates, and its output has no adjacent duplicates
left, so applying it again changes nothing: it is idempotent, and the property is true of
it. A property that the wrong implementation satisfies cannot tell you that you have the
wrong one. `unique` can, because the bug violates it. Choosing properties that the plausible
wrong versions would fail is the skill, and the lab's test names this case to make the point.
''',
                    },
                ],
            },
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
