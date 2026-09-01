"""CE101 — Digital Logic & Computer Systems. Author module."""

COURSE = {
    "id": "CE101",
    "title": "Digital Logic & Computer Systems",
    "year": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Verilog (reference)", "Python"],
    "credits": 10,
    "hours": 120,
    "icon": "⎓",
    "summary": (
        "Everything a processor does is built out of one switch that says 'not both'. "
        "This course climbs that ladder in software: Boolean algebra and canonical "
        "forms, gates assembled from NAND into adders, flip-flops that give a circuit "
        "memory, and finally an arithmetic-logic unit and a small datapath that fetches "
        "and executes instructions of your own encoding."
    ),
    "outcomes": [
        "Derive a truth table, minterm list and sum-of-products form for a Boolean function",
        "Reduce a function to its prime implicants and prove the reduction preserves behaviour",
        "Construct NOT, AND, OR and XOR from NAND alone, and adders from those gates",
        "Explain why edge-triggered storage makes a synchronous circuit predictable",
        "Design a Moore finite-state machine and simulate it over discrete clock ticks",
        "Compute two's-complement arithmetic and set the zero, negative, carry and overflow flags correctly",
        "Assemble a register file, ALU and control FSM into a datapath that runs a micro-program",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone datapath build (60%).",
    "reading": [
        "Harris & Harris, *Digital Design and Computer Architecture*, 2nd ed. — chapters 1-5",
        "Nisan & Schocken, *The Elements of Computing Systems*, 2nd ed. — chapters 1-3",
        "Patterson & Hennessy, *Computer Organization and Design*, 5th ed. — appendix 'The Basics of Logic Design'",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Boolean algebra and canonical forms",
            "summary": "From a truth table to a minimal expression, with equivalence as the referee.",
            "concepts": [
                "The Boolean algebra axioms: identity, complement, distributivity, De Morgan's laws",
                "A truth table is the complete specification of a combinational function",
                "Minterms: each row where the function is 1 names one AND term",
                "Canonical sum-of-products is unique; the minimal SOP normally is not",
                "The adjacency rule `XY + XY' = X` is the single move behind all reduction",
                "Prime implicants and the Quine-McCluskey merging procedure",
                "Two expressions are equal only if they agree on all 2^n rows — check, do not assume",
            ],
            "read": [
                {
                    "title": "Eight rows, four minterms, three terms",
                    "minutes": 14,
                    "body": r'''
Three smoke detectors hang from the ceiling of a server room. Each one is cheap, and
each one is wrong now and then: dust sets one off, a dead battery silences another.
The building's rule is that the alarm sounds when at least two of the three agree, so
that no single flaky detector can either start a false alarm or hide a real fire. Call
the detectors $A$, $B$ and $C$, with 1 meaning "smoke", and the question the alarm
circuit has to answer is a Boolean function of three inputs.

Before there is any algebra there is a table. Three inputs means $2^3 = 8$
combinations, and the rule gives an answer for every one of them:

```text
row   A B C   alarm
 0    0 0 0     0
 1    0 0 1     0
 2    0 1 0     0
 3    0 1 1     1
 4    1 0 0     0
 5    1 0 1     1
 6    1 1 0     1
 7    1 1 1     1
```

The row numbers are not decoration. Read each row's inputs as a binary number with
$A$ as the most significant bit and it *is* the row number: row 5 is $101$, which is
$A = 1$, $B = 0$, $C = 1$. That convention, most significant input first, is the one
this module's lab uses throughout, and it is worth fixing in your head now, because a
table written with the bits the other way round gives every minterm the wrong name.

## The table is the function

A truth table is not a description of a combinational function; it is the function.
Two circuits that agree on all eight rows are the same circuit as far as anyone
downstream can tell, however differently they are wired inside, and two that disagree
on even one row are different, however similar they look on paper. Everything else in
this module, the algebra, the reduction, the proof, is a way of writing the same eight
answers with less ink.

Here is the table produced by a program rather than by hand. The bit extraction is
the line to notice: bit $k$ of row `index`, counting from the left, is
`(index >> (n - 1 - k)) & 1`.

```python
def majority(a, b, c):
    return 1 if a + b + c >= 2 else 0

def truth_table(fn, n):
    rows = []
    for index in range(1 << n):
        bits = tuple((index >> (n - 1 - k)) & 1 for k in range(n))
        rows.append((bits, 1 if fn(*bits) else 0))
    return rows

for index, (bits, out) in enumerate(truth_table(majority, 3)):
    print(index, bits, out)
```

The `1 if fn(*bits) else 0` is doing a quiet but necessary job. Python's `and` and
`or` return one of their operands rather than a fresh boolean, `not` returns `True`
or `False`, and a function written with arithmetic might return 2. All of those are
truthy or falsy in the right way, but a table that stores them as they come cannot be
compared row by row with `==`, and `True` printed where a 1 was expected is the kind
of small wrongness that hides a large one. The lab insists on the integers 0 and 1 for
the output column so that every row means one thing.

## From a row to a minterm

Look at row 5 on its own: $A = 1$, $B = 0$, $C = 1$. Is there a product of literals
that is 1 on this row and 0 on every other row? There is exactly one:
$A \cdot \overline{B} \cdot C$. Each factor is chosen so that it is 1 on row 5, so the
product is 1 there, and on any other row at least one input differs, so at least one
factor is 0 and the product is 0. This product is the *minterm* of row 5, written
$m_5$. Every row has one, and it is the only product of all three variables that
recognises that row alone.

Now the alarm function is 1 on rows 3, 5, 6 and 7 and nowhere else. OR together the
minterms of those four rows and you have an expression that is 1 on exactly those
rows:

$$\text{alarm} = \overline{A}BC + A\overline{B}C + AB\overline{C} + ABC$$

This is the *canonical sum of products*. It is unique, because it is nothing more than
the table's 1-rows read out loud; the row list $\{3, 5, 6, 7\}$ and the expression
carry the same information. In the lab's string form, where a 1 in the pattern
contributes the plain letter and a 0 contributes the letter followed by a prime, the
same four terms are `A'BC + AB'C + ABC' + ABC`.

```python
NAMES = "ABC"

def term_expression(pattern):
    out = []
    for position, char in enumerate(pattern):
        if char == "1":
            out.append(NAMES[position])
        elif char == "0":
            out.append(NAMES[position] + "'")
    return "".join(out) or "1"

minterms = [3, 5, 6, 7]
patterns = [format(m, "03b") for m in minterms]
print(patterns)
print(" + ".join(term_expression(p) for p in patterns))
```

The canonical form is correct and it is also wasteful. Four three-input AND gates and
one four-input OR gate, twelve literals in all, to say "at least two of three". The
reduction that follows is how a designer gets from twelve literals to six without
changing a single row.

## The one move behind every reduction

Take the first and last terms, $\overline{A}BC$ and $ABC$. They share $BC$ and differ
only in whether $A$ is complemented. Factor the shared part out:

$$\overline{A}BC + ABC = BC(\overline{A} + A)$$

That step is the distributive law, run backwards. Then $\overline{A} + A$ is 1 for any
value of $A$, which is the complement law, and $BC \cdot 1 = BC$ by the identity law.
So

$$\overline{A}BC + ABC = BC$$

Two three-literal terms have become one two-literal term, and nothing has been
assumed: each line followed from an axiom. Written generally, $XY + X\overline{Y} = X$,
the *adjacency rule*. Two products that agree everywhere except in one variable, where
one has it plain and the other has it complemented, can be replaced by the shared part
alone.

In pattern notation the rule is a mechanical operation on strings. `011` and `111`
differ in exactly one position, so they merge into `-11`, where the dash means "this
variable has been eliminated". `-11` is the pattern for $BC$, and it covers both rows
3 and 7. Apply the same rule to the other pairs: `101` and `111` merge into `1-1`,
which is $AC$; `110` and `111` merge into `11-`, which is $AB$. Three merges, three
two-literal terms:

$$\text{alarm} = BC + AC + AB$$

Six literals where there were twelve, and the meaning is now readable off the page:
any two detectors agreeing sounds the alarm.

Notice that minterm 7, `111`, took part in all three merges. People hesitate at that,
on the grounds that a row "already used" ought not to be used again. But $X + X = X$
in Boolean algebra, so writing $ABC$ into the expression three times costs nothing and
changes nothing. A minterm may join every merge it is adjacent to, and in fact it
must, or a covering term goes missing. The instinct to cross rows off comes from
ordinary arithmetic, where using a quantity twice would double-count it; here there is
nothing to count.

## Quine-McCluskey is the rule, applied until it stops

For three variables you can see the merges by eye. For seven you cannot, and the
procedure Quine and McCluskey wrote down is the adjacency rule applied exhaustively,
in rounds, by a program.

Start with the minterm patterns. Compare every pair. A pair merges when it differs in
exactly one position, and neither pattern has a dash at that position. Collect every
merged pattern into a new list, and mark the two that produced it as used. Any pattern
that merged with nothing in this round is a *prime implicant*: it cannot be enlarged
further, and it goes into the answer. Then start the next round on the merged list,
and stop when a round produces nothing.

Here is the rule as a function, with the dash condition made explicit, followed by
the trace for the alarm.

```python
def merge(left, right):
    position = -1
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            if position != -1 or a == "-" or b == "-":
                return None
            position = index
    if position == -1:
        return None
    return left[:position] + "-" + left[position + 1:]

current = ["011", "101", "110", "111"]
round_number = 1
primes = []
while current:
    used = set()
    merged = set()
    for i in range(len(current)):
        for j in range(i + 1, len(current)):
            result = merge(current[i], current[j])
            if result is not None:
                print(f"round {round_number}: {current[i]} + {current[j]} -> {result}")
                used.add(current[i])
                used.add(current[j])
                merged.add(result)
    for pattern in current:
        if pattern not in used:
            primes.append(pattern)
    current = sorted(merged)
    round_number += 1
print("prime implicants:", sorted(primes))
```

Round 1 finds the three merges written above and nothing else: `011` and `101` differ
in two positions, and so does every other pair that does not involve `111`. Every one
of the four minterms took part in a merge, so none is prime yet. Round 2 starts from
`-11`, `1-1` and `11-`, and here the dash condition earns its keep. `-11` and `1-1`
differ at position 0, where one has a dash, and again at position 1, so they do not
merge. No pair does. All three survive unmerged and are promoted to primes, the merged
list is empty, and the loop ends with `['-11', '1-1', '11-']`, which is exactly what
the lab expects `prime_implicants([3, 5, 6, 7], 3)` to return.

## Why the dash condition exists

The tempting shortcut is to treat a dash as a wildcard and merge `0-1` with `01-`
because "they only really differ in one place". They do not, and the mistake is worth
seeing in rows rather than in symbols. `0-1` covers rows 1 and 3, the set
$\{001, 011\}$. `01-` covers rows 2 and 3, the set $\{010, 011\}$. A merged `0--`
would cover rows 0, 1, 2 and 3, and row 0, `000`, is in neither original set. The
merged term would be 1 on a row where the function might be 0. The adjacency rule is
only sound when the two patterns cover sets of the same shape that differ in one
coordinate, and a dash against a fixed bit breaks that shape.

The lab's test of `prime_implicants` on the parity function is the same lesson from
the other side. Minterms 1, 2, 4 and 7 are `001`, `010`, `100` and `111`; every pair
differs in two positions, nothing merges at all, and all four minterms come back as
primes. Parity is XOR, and XOR does not shrink in sum-of-products form no matter how
carefully you push the symbols.

## The referee

Every step above was justified by an axiom, and yet the only reason to believe that
$BC + AC + AB$ is the alarm function is that it agrees with the table on all eight
rows. Algebra can be miscopied; a table cannot be argued with. So the last tool is a
function that checks two functions against each other on every row, and the habit
that goes with it is to check rather than to assume.

```python
def truth_table(fn, n):
    rows = []
    for index in range(1 << n):
        bits = tuple((index >> (n - 1 - k)) & 1 for k in range(n))
        rows.append((bits, 1 if fn(*bits) else 0))
    return rows

def equivalent(f, g, n):
    for bits, out in truth_table(f, n):
        if out != (1 if g(*bits) else 0):
            return False
    return True

def majority(a, b, c):
    return 1 if a + b + c >= 2 else 0

def reduced(a, b, c):
    return (b and c) or (a and c) or (a and b)

def too_far(a, b, c):
    return (b and c) or (a and c)

print(equivalent(majority, reduced, 3))
print(equivalent(majority, too_far, 3))
for bits, out in truth_table(majority, 3):
    if out != (1 if too_far(*bits) else 0):
        print("disagree on row", bits)
```

The first line prints `True`. The second prints `False`, and the loop names the row:
`(1, 1, 0)`, where $A$ and $B$ agree and $C$ does not, which is exactly the case the
dropped term $AB$ was covering. Dropping a term because the expression "looks about
right" is the mistake, and it is tempting because a reduced expression with one term
too few still gets seven rows out of eight correct. The lab's `equivalent` is the
referee that catches the eighth.

## Where it stops holding

Prime implicants are not yet a circuit. For the alarm, all three primes are needed,
but that is not the general case. Take the function with minterms 0, 1, 2, 5, 6 and
7. Quine-McCluskey finds six primes, `00-`, `0-0`, `-01`, `-10`, `1-1` and `11-`,
each covering two rows, and any three of them chosen well cover all six rows: `00-`,
`-10` and `1-1` do, for instance, and so do the other three; whichever three you
pick, the rest are redundant. Choosing a smallest set of primes that covers
every minterm is a separate problem, the prime implicant chart, and in general it is
as hard as the hardest search problems in computing. The lab stops at the primes on
purpose; this reading stops there too, but you should know that the word "minimal" in
"minimal sum of products" is doing more work than the reduction alone can deliver, and
that the minimal form is usually not unique even though the canonical form is.

The second limit is the table itself. Eight rows is nothing; twenty inputs is a
million rows, and forty is a trillion. Every method that starts from the full truth
table, including `equivalent`, is exponential in the number of inputs. Real tools
reason about structure instead, and the proof that two large circuits agree is a
research subject rather than a loop.

Third, the reduction assumes every input combination matters. Often some never occur,
a decimal digit encoded in four bits never shows `1010` through `1111`, and those
rows are *don't-cares* that can be set to whichever value merges better. The
procedure extends naturally, but the version you build here treats every row as
specified.

## What you are about to build

The lab for this module, *Truth tables, minterms and prime implicants*, is this
reading turned into eight functions. `truth_table` and `minterms` are the table;
`minterm_patterns`, `term_expression` and `sop_expression` are the canonical form and
its string; `prime_implicants` is the adjacency rule applied in rounds until nothing
merges, with the dash condition written into its `merge`; `from_patterns` turns a
list of implicants back into a function; and `equivalent` is the referee that proves
your reduction preserved every row. The last line of the starter file,
`equivalent(majority, from_patterns(prime_implicants(minterms(majority, 3), 3)), 3)`,
is the whole module in one expression, and it prints `True` only if every piece is
right.
''',
                },
            ],
            "quiz": {
                "title": "Rows, minterms and the merges that are legal",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Three inputs are listed most significant first, so the rows are numbered 0 to 7. Which product term is the minterm of row 6?",
                        "opts": [
                            "`ABC'`, since row 6 is `110`",
                            "`A'BC`, since row 6 is `011`",
                            "`AB'C`, since row 6 is `101`",
                            "`AB + C'`, since rows 6 and 7 share `AB`",
                        ],
                        "a": 0,
                        "whys": [
                            r"Six in binary is `110`: $A = 1$, $B = 1$, $C = 0$, and the 0 is the complemented literal.",
                            r"That is `110` read with $A$ as the least significant bit. Reverse the convention and every row changes its name; in the lab's ordering `011` is row 3, not row 6.",
                            r"`101` is row 5. Counting the rows from 1 instead of 0 makes the sixth row the one numbered 5, which is one row too early.",
                            r"A minterm contains every variable exactly once and is 1 on exactly one row. `AB + C'` is a sum, and it is 1 on five of the eight rows.",
                        ],
                        "why": r"""
With the first variable as the most significant bit, the row number written in binary
is the row's inputs: row 6 is `110`, so $A = 1$, $B = 1$, $C = 0$, and the product
that is 1 on that row alone takes each variable as it stands there, `ABC'`. Reading
the bits the other way round gives `011`, which is row 3 in this convention; starting
the count at 1 lands on row 5, `101`. A sum such as `AB + C'` is not a minterm at all,
because a minterm must recognise one row and no other.
""",
                    },
                    {
                        "q": "Why does $\\overline{A}BC + ABC$ reduce to $BC$?",
                        "opts": [
                            "The shared $BC$ factors out, leaving $\\overline{A} + A$, which is 1 whatever $A$ is",
                            "The two copies of $A$ cancel, the way $+x$ and $-x$ cancel in ordinary arithmetic",
                            "A variable that appears in both terms of a sum is redundant and can be struck from each",
                            "Row 7 is already covered by the first term, so $ABC$ can be dropped and the remaining term shortened",
                        ],
                        "a": 0,
                        "whys": [
                            r"Distributivity backwards gives $BC(\overline{A} + A)$, the complement law makes the bracket 1, and the identity law finishes it.",
                            r"Nothing subtracts in Boolean algebra; there is no $-x$. The terms are ORed, and OR does not cancel anything. What removes $A$ is that $\overline{A} + A$ covers both cases, not that they annihilate.",
                            r"A variable in both terms of a sum is not redundant in general: $\overline{A}B + AC$ has $A$ in both terms and cannot lose it. The rule needs the variable plain in one term and complemented in the other, with everything else identical.",
                            r"$\overline{A}BC$ is 0 on row 7, so row 7 is not covered by it, and dropping $ABC$ would lose that row. The reduction keeps both rows; it is the shared part of two adjacent terms, not one term surviving.",
                        ],
                        "why": r"""
The adjacency rule is three axioms in a row. $\overline{A}BC + ABC = BC(\overline{A} + A)$
is the distributive law run backwards; $\overline{A} + A = 1$ is the complement law;
$BC \cdot 1 = BC$ is the identity law. Nothing cancels and nothing is dropped: the two
terms together are 1 on rows 3 and 7, and so is $BC$. The rule only applies when the
two products are identical except in one variable, which appears plain in one and
complemented in the other; a variable that merely appears in both terms, as $A$ does
in $\overline{A}B + AC$, is not eliminated by anything.
""",
                    },
                    {
                        "q": "Which pair of implicant patterns merges under the adjacency rule?",
                        "opts": [
                            "`01-` and `11-`, giving `-1-`",
                            "`0-1` and `01-`, giving `0--`",
                            "`-11` and `1-1`, giving `--1`",
                            "`001` and `111`, giving `--1`",
                        ],
                        "a": 0,
                        "whys": [
                            r"They differ only at position 0, both have their dash in the same place, and the result covers rows 2, 3, 6 and 7, all of which the two originals covered between them.",
                            r"Position 1 has a dash against a fixed bit, so the two patterns cover different-shaped sets. A merged `0--` would cover row 0, `000`, which neither original covers.",
                            r"These differ at position 0 and again at position 1, and each of those differences is a dash against a fixed bit. Two differences is one too many, and a dash against a fixed bit is never a legal difference.",
                            r"`001` and `111` differ at positions 0 and 1. Adjacency means exactly one position, and merging across two would cover `011` and `101`, which may not be in the function at all.",
                        ],
                        "why": r"""
Two patterns merge when they differ in exactly one position and neither has a dash
there. `01-` and `11-` differ at position 0 only, and their dashes line up, so they
become `-1-`, covering the four rows the pair covered. `0-1` against `01-` has a dash
facing a fixed bit, `-11` against `1-1` differs in two positions with a dash in one of
them, and `001` against `111` differs in two fixed bits. Each of those would produce
a pattern that is 1 on a row that neither original covered, which is why the lab's
`merge` refuses all three.
""",
                    },
                    {
                        "q": "Reducing the majority function, the minterm `111` merges with `011`, with `101` and with `110`. Is using it three times allowed?",
                        "opts": [
                            "Yes: $X + X = X$, so a minterm may join every merge it is adjacent to, and must, or a term goes missing",
                            "No: each minterm may be used only once, so after the first merge the other two pairs stay as three-literal terms",
                            "Yes, provided $ABC$ is also kept in the final expression to account for the extra uses",
                            "Yes, but only in the first round; a pattern that has merged once is retired from later rounds",
                        ],
                        "a": 0,
                        "whys": [
                            r"Repeating a term costs nothing in Boolean algebra, and each of the three merges needs `111` as its partner.",
                            r"That instinct comes from arithmetic, where using a quantity twice double-counts it. Here there is nothing to count: $ABC + ABC = ABC$, so the row can be written into the expression as often as the merges require.",
                            r"$ABC$ is already covered three times over by $BC$, $AC$ and $AB$; adding it back changes nothing and undoes part of the reduction. Idempotence means the extra uses need no accounting.",
                            r"Patterns are retired when they fail to merge, not when they succeed. A merged pattern moves to the next round and may merge again there; that is how a four-row implicant is found from two two-row ones.",
                        ],
                        "why": r"""
Because $X + X = X$, writing $ABC$ into the sum three times is the same as writing it
once, so `111` can be the partner in all three merges and the result $BC + AC + AB$ is
exact. Refuse the reuse and two of the pairs are never merged, which leaves
three-literal terms in the answer and, worse, a cover that depends on which pair you
happened to merge first. Nothing needs adding back afterwards, and a pattern is not
retired for merging; it is retired, as a prime, only when a round finds nothing for it
to merge with.
""",
                    },
                    {
                        "q": "$BC + AC$ agrees with the majority function on seven of its eight rows. What is it?",
                        "opts": [
                            "A different function, because two expressions are equal only if they agree on every one of the $2^n$ rows",
                            "A valid simplification, because it drops one redundant term and still covers the common cases",
                            "Equivalent to the majority function, because the two differ only on an input combination that rarely occurs",
                            "The minimal form of the majority function, because a smaller number of terms is what reduction is for",
                        ],
                        "a": 0,
                        "whys": [
                            r"It is 0 on row 6, `110`, where the majority function is 1; one row is enough to make it a different function.",
                            r"$AB$ is not redundant: it is the only term that covers `110`. A term is redundant only if every row it covers is covered by the others, and a check on the eighth row shows that this one is not.",
                            r"How often an input occurs is not part of the definition. Two circuits that disagree on any row are different circuits, and a detector that ignores the case where $A$ and $B$ agree is not a majority detector.",
                            r"Reduction is only allowed to remove what the axioms say can be removed; fewer terms is the goal only when every row is preserved. Dropping a term that covers a row changes the function, so this is not a form of it at all.",
                        ],
                        "why": r"""
Two Boolean expressions are the same function exactly when they agree on all $2^n$
rows, and $BC + AC$ is 0 on `110`, where the majority is 1. That single row makes it a
different function, not a simplification, however many rows it gets right. This is
why the lab's `equivalent` compares every row and why dropping a term that "looks
redundant" has to be checked rather than assumed: a wrong reduction gets most rows
right, and the referee exists to find the one it does not.
""",
                    },
                    {
                        "q": "Quine-McCluskey on the minterms $\\{0, 1, 2, 5, 6, 7\\}$ returns six prime implicants, each covering two rows. How many terms does a smallest sum-of-products for that function need?",
                        "opts": [
                            "Three: the primes overlap, and a well-chosen three cover all six rows",
                            "Six: every prime implicant must appear, or a row it covers is left uncovered",
                            "One: six adjacent minterms merge into a single implicant",
                            "Two: one prime for the rows with $A = 0$ and one for the rows with $A = 1$",
                        ],
                        "a": 0,
                        "whys": [
                            r"`00-`, `-10` and `1-1` cover rows 0, 1, 2, 6, 5 and 7 between them; the other three primes are redundant in that cover, and a different three would do as well.",
                            r"Every row is covered by two primes, so any one prime can be dropped without uncovering anything. Prime implicants are the candidates for a cover, not the cover itself.",
                            r"Six rows cannot be one implicant: an implicant covers $2^k$ rows, and six is not a power of two. Nor are these rows all mutually adjacent; the procedure stopped at two-row patterns because nothing larger exists.",
                            r"The three rows with $A = 0$ are 0, 1 and 2, and no single pattern covers exactly those three, because three is not a power of two. The same holds on the other side.",
                        ],
                        "why": r"""
Finding the prime implicants is only the first half of minimisation. Here every
minterm is covered by two of the six primes, so no prime is essential and any single
one can be dropped; the smallest cover uses three of them, and there are two equally
good choices, which is why the minimal form is not unique. Choosing the cover is a
separate problem, the prime implicant chart, and the lab deliberately stops before it.
Six is what you get by mistaking the candidates for the answer; one and two both need
a pattern covering a number of rows that is not a power of two, which no implicant
can.
""",
                    },
                ],
            },
            "lab": {
                "title": "Truth tables, minterms and prime implicants",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
A Boolean function of `n` inputs is fully described by its `2**n` truth-table
rows. This lab turns that table into algebra and then shrinks the algebra.

Inputs are always listed **most significant first**, so for `n = 3` row 5 is
`(1, 0, 1)`.

**`truth_table(fn, n)`** — every row as an `(inputs, output)` pair, in binary
counting order. `inputs` is a tuple of 0/1 and `output` is `1` or `0` (never
`True`, never any other truthy value). Raise `ValueError` when `n < 1`.

```text
truth_table(lambda a, b: a and b, 2)
  -> [((0,0), 0), ((0,1), 0), ((1,0), 0), ((1,1), 1)]
```

**`minterms(fn, n)`** — the row numbers where the output is 1, ascending.

**`minterm_patterns(ms, n)`** — each minterm as an `n`-character bit string.
Raise `ValueError` if any minterm is negative or does not fit in `n` bits.

```text
minterm_patterns([3, 5], 3)  ->  ["011", "101"]
```

**`term_expression(pattern)`** — one *implicant* as a product term. A pattern
is a string of `"0"`, `"1"` and `"-"`, one character per variable, and the
variables are named `A`, `B`, `C`, ... A `"1"` contributes the plain letter, a
`"0"` the letter followed by `'`, and a `"-"` contributes nothing because that
variable has been eliminated. An all-`"-"` pattern is the constant `1`.

```text
term_expression("101")  ->  "AB'C"
term_expression("1-0")  ->  "AC'"
term_expression("--")   ->  "1"
```

**`sop_expression(patterns)`** — the terms joined with `" + "`, in the order
given. An empty list is the constant `"0"`.

**`prime_implicants(ms, n)`** — Quine-McCluskey. Start from the minterm
patterns. Repeatedly merge every pair that differs in exactly one position (and
only where neither has a `"-"` there) into one pattern with `"-"` at that
position. Any pattern that merged with nothing in a round is prime. Return the
primes sorted, with no duplicates.

```text
prime_implicants([3, 5, 6, 7], 3)  ->  ["-11", "1-1", "11-"]   (majority: BC + AC + AB)
prime_implicants([1, 2, 4, 7], 3)  ->  ["001", "010", "100", "111"]   (parity will not shrink)
prime_implicants([], 2)            ->  []
```

**`from_patterns(patterns)`** — a *function* that evaluates the OR of those
implicants: it returns 1 when the argument bits match at least one pattern,
ignoring `"-"` positions.

**`equivalent(f, g, n)`** — `True` when the two functions agree on every one of
the `2**n` rows. Compare truth values, not identities: `1` and `True` agree.

Together these let you reduce a function and then *prove* the reduction:
`equivalent(f, from_patterns(prime_implicants(minterms(f, n), n)), n)`.
''',
                "files": [{"name": "main.py", "content": r'''
NAMES = "ABCDEFGH"


def truth_table(fn, n):
    """Every (inputs, output) row for fn, MSB first. ValueError when n < 1."""
    # your code here


def minterms(fn, n):
    """Ascending row numbers where fn is 1."""
    # your code here


def minterm_patterns(ms, n):
    """Each minterm as an n-character bit string. ValueError if one will not fit."""
    # your code here


def term_expression(pattern):
    """One implicant pattern as a product term; all dashes means the constant 1."""
    # your code here


def sop_expression(patterns):
    """Product terms joined with ' + '; no patterns means the constant 0."""
    # your code here


def prime_implicants(ms, n):
    """Quine-McCluskey prime implicants of the minterm list, sorted."""
    # your code here


def from_patterns(patterns):
    """A function evaluating the OR of these implicants."""
    # your code here


def equivalent(f, g, n):
    """True when f and g agree on all 2**n rows."""
    # your code here


def majority(a, b, c):
    return 1 if a + b + c >= 2 else 0


ms = minterms(majority, 3)
print(sop_expression(minterm_patterns(ms, 3)))
print(sop_expression(prime_implicants(ms, 3)))
print(equivalent(majority, from_patterns(prime_implicants(ms, 3)), 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
NAMES = "ABCDEFGH"


def truth_table(fn, n):
    """Every (inputs, output) row for fn, MSB first. ValueError when n < 1."""
    if n < 1:
        raise ValueError("a function needs at least one input")
    rows = []
    for index in range(1 << n):
        bits = tuple((index >> (n - 1 - k)) & 1 for k in range(n))
        rows.append((bits, 1 if fn(*bits) else 0))
    return rows


def minterms(fn, n):
    """Ascending row numbers where fn is 1."""
    return [index for index, (_, out) in enumerate(truth_table(fn, n)) if out]


def minterm_patterns(ms, n):
    """Each minterm as an n-character bit string. ValueError if one will not fit."""
    if n < 1:
        raise ValueError("a function needs at least one input")
    patterns = []
    for m in ms:
        if m < 0 or m >= (1 << n):
            raise ValueError(f"minterm {m} does not fit in {n} bits")
        patterns.append(format(m, "0" + str(n) + "b"))
    return patterns


def term_expression(pattern):
    """One implicant pattern as a product term; all dashes means the constant 1."""
    literals = []
    for position, char in enumerate(pattern):
        if char == "1":
            literals.append(NAMES[position])
        elif char == "0":
            literals.append(NAMES[position] + "'")
    if not literals:
        return "1"
    return "".join(literals)


def sop_expression(patterns):
    """Product terms joined with ' + '; no patterns means the constant 0."""
    if not patterns:
        return "0"
    return " + ".join(term_expression(p) for p in patterns)


def merge(left, right):
    """The merged pattern when the two differ in exactly one fixed bit, else None."""
    position = -1
    for index, (a, b) in enumerate(zip(left, right)):
        if a != b:
            if position != -1 or a == "-" or b == "-":
                return None
            position = index
    if position == -1:
        return None
    return left[:position] + "-" + left[position + 1:]


def prime_implicants(ms, n):
    """Quine-McCluskey prime implicants of the minterm list, sorted."""
    current = sorted(set(minterm_patterns(ms, n)))
    primes = set()
    while current:
        used = set()
        nxt = set()
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                merged = merge(current[i], current[j])
                if merged is not None:
                    used.add(current[i])
                    used.add(current[j])
                    nxt.add(merged)
        for pattern in current:
            if pattern not in used:
                primes.add(pattern)
        current = sorted(nxt)
    return sorted(primes)


def from_patterns(patterns):
    """A function evaluating the OR of these implicants."""
    def fn(*bits):
        for pattern in patterns:
            if all(int(char) == bit for char, bit in zip(pattern, bits) if char != "-"):
                return 1
        return 0
    return fn


def equivalent(f, g, n):
    """True when f and g agree on all 2**n rows."""
    for bits, out in truth_table(f, n):
        if out != (1 if g(*bits) else 0):
            return False
    return True


def majority(a, b, c):
    return 1 if a + b + c >= 2 else 0


ms = minterms(majority, 3)
print(sop_expression(minterm_patterns(ms, 3)))
print(sop_expression(prime_implicants(ms, 3)))
print(equivalent(majority, from_patterns(prime_implicants(ms, 3)), 3))
'''}],
                "hints": [
                    "Row `index` has bit `k` equal to `(index >> (n - 1 - k)) & 1` when the first variable is the most significant.",
                    "`format(m, \"0\" + str(n) + \"b\")` pads a minterm to exactly n binary digits.",
                    "Two patterns merge only when they differ in one position *and* neither holds a dash there — check both conditions before returning the merged pattern.",
                    "Quine-McCluskey is a loop over rounds: collect every merge of the current list, mark the patterns that merged, promote the unmarked ones to primes, and repeat on the merged list until it is empty.",
                ],
                "tests": [
                    {"name": "truth_table shape, order and 0/1 outputs", "code": r'''
_got = truth_table(lambda a, b: a and b, 2)
_want = [((0, 0), 0), ((0, 1), 0), ((1, 0), 0), ((1, 1), 1)]
assert _got == _want, f"truth_table(AND, 2) gave {_got!r}, expected {_want}"
assert all(_o in (0, 1) and type(_o) is int for _, _o in _got), "outputs must be the ints 0 and 1"
_t3 = truth_table(lambda a, b, c: c, 3)
assert len(_t3) == 8, f"a 3-input table has 8 rows, got {len(_t3)}"
assert _t3[5][0] == (1, 0, 1), f"row 5 should be (1, 0, 1), got {_t3[5][0]!r}"
try:
    truth_table(lambda a: a, 0)
    assert False, "truth_table(fn, 0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "minterms lists the rows that are 1", "code": r'''
assert minterms(lambda a, b: a or b, 2) == [1, 2, 3], f"OR gave {minterms(lambda a, b: a or b, 2)!r}"
assert minterms(lambda a, b, c: a ^ b ^ c, 3) == [1, 2, 4, 7], "odd parity is minterms 1, 2, 4, 7"
assert minterms(lambda a, b: 0, 2) == [], "a constant-0 function has no minterms"
assert minterms(lambda a, b: 1, 2) == [0, 1, 2, 3], "a constant-1 function has every minterm"
'''},
                    {"name": "minterm_patterns pads and validates", "code": r'''
assert minterm_patterns([3, 5], 3) == ["011", "101"], f"Got {minterm_patterns([3, 5], 3)!r}"
assert minterm_patterns([], 4) == [], "no minterms, no patterns"
for _bad in ([8], [-1]):
    try:
        minterm_patterns(_bad, 3)
        assert False, f"minterm_patterns({_bad!r}, 3) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "term_expression and sop_expression", "code": r'''
assert term_expression("101") == "AB'C", f'Got {term_expression("101")!r}'
assert term_expression("1-0") == "AC'", f'Got {term_expression("1-0")!r}'
assert term_expression("--") == "1", "an implicant with no literals is the constant 1"
assert sop_expression(["-11", "1-1", "11-"]) == "BC + AC + AB", \
    f'Got {sop_expression(["-11", "1-1", "11-"])!r}'
assert sop_expression([]) == "0", "no implicants means the constant 0"
assert sop_expression(["011"]) == "A'BC", f'Got {sop_expression(["011"])!r}'
'''},
                    {"name": "prime_implicants merges adjacent minterms", "code": r'''
assert prime_implicants([3, 5, 6, 7], 3) == ["-11", "1-1", "11-"], \
    f"majority gave {prime_implicants([3, 5, 6, 7], 3)!r}, expected ['-11', '1-1', '11-']"
assert prime_implicants([1, 2, 3], 2) == ["-1", "1-"], \
    f"OR gave {prime_implicants([1, 2, 3], 2)!r}, expected ['-1', '1-']"
assert prime_implicants([0, 1, 2, 3], 2) == ["--"], "a tautology reduces to the constant 1"
assert prime_implicants([], 2) == [], "nothing to imply"
assert prime_implicants([1, 2, 4, 7], 3) == ["001", "010", "100", "111"], \
    "three-input parity has no adjacent minterms, so every minterm is prime"
'''},
                    {"name": "from_patterns rebuilds a working function", "code": r'''
_f = from_patterns(["-11", "1-1", "11-"])
for _bits, _want in [((0, 0, 0), 0), ((0, 1, 1), 1), ((1, 0, 1), 1),
                     ((1, 1, 0), 1), ((1, 1, 1), 1), ((1, 0, 0), 0)]:
    _got = _f(*_bits)
    assert _got == _want, f"rebuilt majority{_bits} gave {_got!r}, expected {_want}"
assert from_patterns([])(0, 1) == 0, "no implicants is the constant 0"
assert from_patterns(["--"])(0, 1) == 1, "an all-dash implicant is the constant 1"
'''},
                    {"name": "equivalence proves the reduction", "code": r'''
def _maj(a, b, c):
    return 1 if a + b + c >= 2 else 0
_primes = prime_implicants(minterms(_maj, 3), 3)
assert equivalent(_maj, from_patterns(_primes), 3), "the reduced form must match the original"
assert equivalent(_maj, from_patterns(minterm_patterns(minterms(_maj, 3), 3)), 3), \
    "the canonical form must match the original too"
assert equivalent(lambda a, b: a and b, lambda a, b: not (not a or not b), 2), \
    "De Morgan: AB and (A'+B')' are the same function"
assert not equivalent(lambda a, b: a and b, lambda a, b: a or b, 2), \
    "AND and OR differ on (0, 1), so equivalent() must be False"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Gates, universality and adders",
            "summary": "NAND is enough for everything; build up to a ripple-carry adder.",
            "concepts": [
                "NAND (and NOR) are functionally complete — every gate reduces to them",
                "NOT from a NAND with both inputs tied together; AND from NAND then NOT",
                "OR from NAND by De Morgan: `A + B = (A'B')'`",
                "XOR as a four-NAND network, and why it costs more than AND",
                "The half adder: sum is XOR, carry is AND",
                "The full adder chains two half adders and ORs the carries",
                "Ripple-carry delay grows linearly with word width — the motivation for carry-lookahead",
            ],
            "read": [
                {
                    "title": "Not both: one gate, and the adder you build from it",
                    "minutes": 14,
                    "body": r'''
A 7400 is a small black chip with fourteen pins and four NAND gates inside, and for
a few decades it was the cheapest logic you could buy. Wire pins 1 and 2 of one gate
together to a switch, put an LED on pin 3, and watch: switch open, LED on; switch
closed, LED off. You have built an inverter from a gate that was sold as something
else, and that small trick is the beginning of everything in this module.

NAND says "not both". Its table is AND's with the output column flipped:

```text
A B   AB   NAND
0 0    0     1
0 1    0     1
1 0    0     1
1 1    1     0
```

## NOT, AND and OR out of one part

Tie both inputs together and only two rows of the table can happen, `00` and `11`.
On `00` the output is 1; on `11` it is 0. That is an inverter:
$\overline{A} = \overline{A \cdot A}$. One gate.

AND is NAND followed by NOT, because inverting "not both" gives "both": two gates,
the second with its inputs tied.

OR takes a moment more. Write down the table for $\overline{A} \cdot \overline{B}$
next to the table for $A + B$:

```text
A B   A'B'   A+B
0 0    1      0
0 1    0      1
1 0    0      1
1 1    0      1
```

The columns are complements of each other on every row. So
$A + B = \overline{\overline{A} \cdot \overline{B}}$, which is one of De Morgan's laws
read as a construction: invert each input, then NAND. Three gates. The law was not
announced here; it was read off two tables, which is the only way any Boolean
identity is ever established.

```python
def nand(a, b):
    return 0 if (a and b) else 1

def not_gate(a):
    return nand(a, a)

def and_gate(a, b):
    return not_gate(nand(a, b))

def or_gate(a, b):
    return nand(not_gate(a), not_gate(b))

print("A B  NOT A  AND  OR")
for a in (0, 1):
    for b in (0, 1):
        print(a, b, "   ", not_gate(a), "   ", and_gate(a, b), "  ", or_gate(a, b))
```

Every line of that output should match the tables you know, and if you were to
replace `nand` by any other single gate that can do the same job, NOR for instance,
the same three constructions exist. A gate from which every other gate can be built
is *functionally complete*. NAND and NOR are; AND on its own is not, because no
arrangement of ANDs ever turns a 1 into a 0.

## XOR, and why four gates rather than nine

XOR is 1 when the inputs differ: $A \oplus B = A\overline{B} + \overline{A}B$. Build
that literally and it costs two inverters, two ANDs and an OR, which in NANDs is
$2 + 4 + 3 = 9$ gates. There is a four-gate network, and it is worth deriving rather
than memorising, because the derivation is the same De Morgan step used twice.

Let $S = \overline{AB}$, one NAND of the inputs. Now NAND $A$ with $S$:

$$\overline{A \cdot \overline{AB}} = \overline{A(\overline{A} + \overline{B})} = \overline{A\overline{A} + A\overline{B}} = \overline{A\overline{B}}$$

The first equality is De Morgan on $\overline{AB}$, the second is distributivity,
the third is $A\overline{A} = 0$. By the same steps, NAND of $B$ with $S$ is
$\overline{\overline{A}B}$. NAND those two results together:

$$\overline{\overline{A\overline{B}} \cdot \overline{\overline{A}B}} = A\overline{B} + \overline{A}B$$

by De Morgan once more. Four NANDs, one of them shared between two of the others.
The gate count is the reason the lab says XOR "costs more than AND": AND is two
NANDs, XOR is four, and in a ripple adder the XORs are where the sum bits come from,
so their cost is paid at every bit.

```python
def nand(a, b):
    return 0 if (a and b) else 1

def xor_gate(a, b):
    shared = nand(a, b)
    return nand(nand(a, shared), nand(b, shared))

for a in (0, 1):
    for b in (0, 1):
        print(a, b, xor_gate(a, b), xor_gate(a, b) == (1 if a != b else 0))
```

Four rows, four `True`s. The check against `a != b` is the referee from the previous
module in miniature: the algebra says the network is XOR, and the table confirms it.

## Adding two bits

Add two one-bit numbers and write the result in binary:

```text
A B   A+B   sum carry
0 0    0     0    0
0 1    1     1    0
1 0    1     1    0
1 1   10     0    1
```

Read the columns as functions of $A$ and $B$. The sum column is 1 when the inputs
differ: it is XOR. The carry column is 1 only when both are 1: it is AND. Nothing was
decided here; the two columns of the addition table *are* those two gates. That pair
is the *half adder*, and `half_adder(1, 1)` returning `(0, 1)` is "one plus one is
two, written `10`".

It is called a half adder because it cannot take a carry coming in from the bit to its
right. When two multi-bit numbers are added, every column except the first has three
things to add: the two bits and the carry from the previous column. The three-input
version is the *full adder*, and the natural way to build it is with the piece you
already have. Add $A$ and $B$ with one half adder, getting $S_1$ and $C_1$. Add $S_1$
and the incoming carry with a second half adder, getting $S_2$ and $C_2$. $S_2$ is the
sum bit. The carry out is $C_1 + C_2$, an OR.

Why OR is enough deserves a sentence, because it is the kind of thing people accept
without seeing. Could $C_1$ and $C_2$ both be 1? $C_1 = 1$ means $A = B = 1$, which
makes $S_1 = 0$, and then $C_2 = S_1 \cdot C_{in} = 0$. So the two carries are never
both set, and OR combines them without losing anything. XOR would also work, for the
same reason, but it costs four NANDs to OR's three, and a designer takes the cheaper
gate when both are right.

```python
def nand(a, b):
    return 0 if (a and b) else 1

def not_gate(a):
    return nand(a, a)

def and_gate(a, b):
    return not_gate(nand(a, b))

def or_gate(a, b):
    return nand(not_gate(a), not_gate(b))

def xor_gate(a, b):
    shared = nand(a, b)
    return nand(nand(a, shared), nand(b, shared))

def half_adder(a, b):
    return xor_gate(a, b), and_gate(a, b)

def full_adder(a, b, cin):
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, cin)
    return s2, or_gate(c1, c2)

for a in (0, 1):
    for b in (0, 1):
        for cin in (0, 1):
            s, cout = full_adder(a, b, cin)
            total = a + b + cin
            print(a, b, cin, "->", s, cout, (s, cout) == (total % 2, total // 2))
```

Eight rows, and the last column is `True` on every one: the sum bit is the total
modulo 2 and the carry is the total divided by 2, which is what "carry" means. The
lab's test for `full_adder` is that comparison, row for row.

## Chaining: 7 + 9 in four bits

A ripple-carry adder is one full adder per bit, with each carry out wired to the next
carry in. The first stage's carry in is 0, or whatever the caller supplies. Take
$7 + 9$ in four bits: `0111` and `1001`, most significant bit first, which is how the
lab's `to_bits` writes them. Addition starts at the *least* significant end, so the
trace runs from the right-hand bit leftwards:

```text
bit 0:  1 + 1 + 0  ->  sum 0, carry 1
bit 1:  1 + 0 + 1  ->  sum 0, carry 1
bit 2:  1 + 0 + 1  ->  sum 0, carry 1
bit 3:  0 + 1 + 1  ->  sum 0, carry 1
```

Sum bits `0000`, carry out 1. Sixteen does not fit in four bits; the carry out is the
fifth bit, and reading the answer as `1 0000` gives 16.

```python
def nand(a, b):
    return 0 if (a and b) else 1

def not_gate(a):
    return nand(a, a)

def and_gate(a, b):
    return not_gate(nand(a, b))

def or_gate(a, b):
    return nand(not_gate(a), not_gate(b))

def xor_gate(a, b):
    shared = nand(a, b)
    return nand(nand(a, shared), nand(b, shared))

def half_adder(a, b):
    return xor_gate(a, b), and_gate(a, b)

def full_adder(a, b, cin):
    s1, c1 = half_adder(a, b)
    s2, c2 = half_adder(s1, cin)
    return s2, or_gate(c1, c2)

def to_bits(value, width):
    return [(value >> (width - 1 - k)) & 1 for k in range(width)]

a_bits = to_bits(7, 4)
b_bits = to_bits(9, 4)
carry = 0
out = []
for position, (a, b) in enumerate(zip(reversed(a_bits), reversed(b_bits))):
    bit, carry = full_adder(a, b, carry)
    print(f"bit {position}: {a} + {b} -> sum {bit}, carry {carry}")
    out.append(bit)
out.reverse()
print(out, carry)
```

The `reversed` on both operands, and the `out.reverse()` at the end, are where most
first attempts go wrong. `to_bits` hands you the number the way you would write it,
big end first, and the adder consumes it the way you would add it, small end first.
Walk the lists forwards and you add the top bits first, with the carry running the
wrong way; the result is right for a few lucky inputs and wrong for most. The lab's
test adds every pair of four-bit numbers and compares against arithmetic, so a wrong
direction fails on the first row it is wrong for.

## The mistake the checks are written for

The tempting move is to write `def xor_gate(a, b): return a ^ b`. It returns the right
four values, and it is shorter. It is also not the exercise. The point of building
from NAND is to see that the whole tower rests on one part, and a Python operator is
a gate the hardware does not have. The lab watches `nand` while it calls each gate and
fails any gate that never called it. Writing `and_gate` as `a and b` fails the same
test, and so does an `if` on the signal values, because an `if` is a decision the
circuit has no way to make. Every gate is a wire from the previous one.

## Where it stops holding

The gate count is a model, and a coarse one. It assumes every NAND costs the same and
every signal arrives at once. Neither is true. A real gate takes time to switch, tens
of picoseconds in a modern process, and in a ripple-carry adder the carry into bit 3
cannot be right until bit 2's carry is, which cannot be right until bit 1's is. The
worst case is an input like `1111 + 0001`, where a carry generated at bit 0 has to
travel through every stage before the top bit settles. The delay grows in proportion
to the width: a 64-bit ripple adder waits for 64 carry stages in sequence. That is why
the same function is fine at four bits and unacceptable at sixty-four, and why real
adders compute the carries with extra logic, carry-lookahead, at the price of more
gates. Universality says NAND can build anything; it says nothing about building it
fast.

The second limit is the 0-and-1 picture itself. Between a gate's input changing and
its output settling, the output is neither 0 nor 1 for a moment, and a downstream gate
may see a brief wrong value, a glitch, before the right one arrives. In a purely
combinational circuit that is harmless, because nothing remembers the glitch. The next
module adds memory, and the reason memory is only updated on a clock edge is precisely
so that these in-between values are never stored.

## What you are about to build

The lab, *From one NAND to a 4-bit adder*, starts with `nand` written for you and
asks for the rest of this reading in the order it was told: `not_gate`, `and_gate`,
`or_gate` and `xor_gate` as the one-, two-, three- and four-gate networks;
`half_adder` as the XOR-and-AND pair; `full_adder` as two half adders and an OR;
`to_bits` and `from_bits` to move between integers and bit lists, most significant
bit first; and `ripple_add`, which walks both operands from the least significant end
passing the carry along. The starter's last line,
`ripple_add(to_bits(7, 4), to_bits(9, 4))`, is the trace above, and it should print
`([0, 0, 0, 0], 1)`.
''',
                },
            ],
            "quiz": {
                "title": "Counting gates, and where the carry goes",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Why does a NAND gate with both inputs tied together behave as an inverter?",
                        "opts": [
                            "Only the rows `00` and `11` can occur, and NAND gives 1 on the first and 0 on the second",
                            "Holding one input at 0 while the other is driven makes the output the inverse of the driven input",
                            "Feeding the same signal to both inputs doubles it, and NAND of a doubled signal is its complement",
                            "A NAND is an AND plus an output inverter, and tying the inputs bypasses the AND",
                        ],
                        "a": 0,
                        "whys": [
                            r"Tying the inputs restricts the four-row table to the two rows where they agree, and on those rows NAND is the complement of the input.",
                            r"With one input held at 0, NAND outputs 1 whatever the other input does; that is a constant, not an inverter. Holding an input at 1 would invert, but the question is about tying the inputs to each other.",
                            r"There is no doubling: a signal ANDed with itself is itself, $A \cdot A = A$, so NAND of the pair is $\overline{A}$. The complement comes from the output inversion, not from any arithmetic on the input.",
                            r"Nothing is bypassed. The AND stage is still there, computing $A \cdot A = A$, and the inverter then gives $\overline{A}$; the construction works because of what the AND does with equal inputs, not in spite of it.",
                        ],
                        "why": r"""
With both inputs the same signal, only two of NAND's four rows are reachable: `00`,
where the output is 1, and `11`, where it is 0. That is the inverter's table. In
algebra, $\overline{A \cdot A} = \overline{A}$ because $A \cdot A = A$; the AND stage is
doing its ordinary job and the output inversion does the rest. Holding one input at
0 gives a constant 1 instead, and there is no arithmetic doubling of signals anywhere
in Boolean logic.
""",
                    },
                    {
                        "q": "How many NAND gates does OR take, and what is the construction?",
                        "opts": [
                            "Three: invert each input with a NAND, then NAND the two results, by De Morgan",
                            "Two: a NAND followed by an inverter, the same as AND but with the output flipped again",
                            "One: NAND is 1 on three of its four rows and so is OR, so a single gate serves as both",
                            "Four: XOR's shared network with its final gate left out",
                        ],
                        "a": 0,
                        "whys": [
                            r"$A + B = \overline{\overline{A} \cdot \overline{B}}$, and each of the three overlines is one NAND.",
                            r"A NAND followed by an inverter is AND, and inverting once more brings you back to NAND. No number of output inversions turns AND into OR; the inversion has to happen on the inputs.",
                            r"Both are 1 on three rows, but not the same three. NAND is 0 on `11` and OR is 0 on `00`; a single gate that is right on two rows and wrong on two is not an OR gate.",
                            r"Removing XOR's final gate leaves two separate signals, $\overline{A\overline{B}}$ and $\overline{\overline{A}B}$, not an OR. XOR's last gate is the OR construction applied to those two; there is no OR inside the network to extract.",
                        ],
                        "why": r"""
The tables for $\overline{A}\,\overline{B}$ and $A + B$ are complements of each other
on every row, which is De Morgan's law, and read as a construction it says: invert
each input, then NAND. That is three gates. Inverting NAND's output gives AND, and
inverting again gives NAND back; you cannot reach OR by working on the output alone.
NAND and OR do each have three 1-rows, but on different inputs, and XOR's network is
not an OR with a piece removed.
""",
                    },
                    {
                        "q": "A full adder built from two half adders combines their two carries with an OR gate. Why is OR enough?",
                        "opts": [
                            "The two carries are never both 1, so OR loses nothing; XOR would also work but costs an extra NAND",
                            "Both carries are 1 whenever all three inputs are 1, and OR is the gate that keeps a 1 in that case",
                            "OR is not enough: a third half adder is needed, because two carries can add to 2 and need a carry of their own",
                            "OR is the wrong choice; AND is needed so that the carry out is set only when both half adders carry",
                        ],
                        "a": 0,
                        "whys": [
                            r"If the first half adder carries, $A = B = 1$ and its sum bit is 0, so the second half adder has nothing to carry.",
                            r"When all three inputs are 1, the first half adder gives sum 0 and carry 1, and the second adds 0 to the carry-in and gives carry 0. The two carries are never both set, which is the whole reason OR is safe.",
                            r"Two carries cannot add to 2, because at most one of them is 1. Three inputs sum to at most 3, which is `11` in binary: one sum bit and one carry bit, exactly what two half adders and an OR produce.",
                            r"AND would give a carry out of 0 on every row, since the two carries are never both 1. The carry out must be 1 whenever either half adder carried, and that is OR.",
                        ],
                        "why": r"""
The first half adder carries only when $A = B = 1$, and in that case its sum bit is
0, so the second half adder, adding that 0 to the carry-in, cannot carry. The two
carries are therefore never both 1, and OR combines them exactly. XOR would give the
same values, at four NANDs against OR's three, so OR is the cheaper right answer.
AND would never set the carry, and no third stage is needed because three one-bit
inputs sum to at most 3, which one sum bit and one carry bit hold.
""",
                    },
                    {
                        "q": "`to_bits` writes numbers most significant bit first. What does `ripple_add(to_bits(7, 4), to_bits(9, 4))` return?",
                        "opts": [
                            "`([0, 0, 0, 0], 1)`: the sum is 16, which is a carry out and four zeros",
                            "`([1, 0, 0, 0, 0], 0)`: the sum is 16, which needs a fifth bit",
                            "`([0, 0, 0, 0], 0)`: the sum overflows four bits, so it wraps to zero",
                            "`([1, 1, 1, 0], 1)`: the bits are added in the order they are listed, top bit first",
                        ],
                        "a": 0,
                        "whys": [
                            r"`0111 + 1001` carries at every stage from bit 0 upwards, leaving four zeros and a carry out of 1.",
                            r"The adder's width is the width of its operands. A fifth bit does not appear in the sum list; the value that would occupy it is reported separately, as the carry out.",
                            r"The wrap is right, but the carry out is not thrown away: it is the second element of the result, and it is what tells the caller the true sum did not fit.",
                            r"That is what you get by walking the lists from the top bit down, which runs the carry the wrong way. Addition starts at the least significant end, so both lists must be reversed first.",
                        ],
                        "why": r"""
Seven plus nine is sixteen, which is `10000`: four zero bits and a 1 that does not
fit. The adder keeps the width of its operands, so the sum list is `[0, 0, 0, 0]` and
the 1 is returned as the carry out. The carry is never dropped, and the list never
grows. Adding the lists in the order they are written, most significant first, runs
the carry upwards from the wrong end and gives a wrong answer for most inputs, which
is why `ripple_add` walks both operands reversed.
""",
                    },
                    {
                        "q": "`def xor_gate(a, b): return a ^ b` returns the right value on all four rows. Why does the lab reject it?",
                        "opts": [
                            "The lab counts calls to `nand` while it runs each gate, and a Python operator never calls it",
                            "`^` is bitwise XOR, which gives wrong results for the values 0 and 1 in some rows",
                            "The result has the type `bool` rather than `int`, and the tests compare with `is`",
                            "It does not reject it: the check only looks at the four output rows, and those are all correct",
                        ],
                        "a": 0,
                        "whys": [
                            r"The exercise is to build from one primitive, and the check enforces that by watching the primitive, not the outputs.",
                            r"`0 ^ 1` is 1 and `1 ^ 1` is 0; on single bits the bitwise operator is XOR exactly. The results are right, and that is not what the check is about.",
                            r"`^` on two ints returns an int, and the tests compare with `==` in any case. The rejection has nothing to do with types.",
                            r"There is a test that wraps `nand` in a counter and calls each gate; a gate that computes its answer without touching `nand` fails it regardless of what it returns.",
                        ],
                        "why": r"""
The point of the lab is that every gate is wired from NAND, so one of its tests
replaces `nand` with a counting wrapper, calls each gate, and fails any gate that
never reached it. `a ^ b` gives the right four values, of the right type, and fails
that test because it is a computation the circuit does not contain. The same goes for
`a and b`, `not a` and an `if` on the signal values: correct output is necessary, but
the check is about how it was produced.
""",
                    },
                    {
                        "q": "Why does a ripple-carry adder's worst-case delay grow in proportion to its width?",
                        "opts": [
                            "Each stage's carry-in waits on the previous stage's carry-out, so a carry from bit 0 passes through every stage in turn",
                            "A wider word needs proportionally more NAND gates, and every gate anywhere in the circuit adds its own delay to the total",
                            "The sum bits must be produced in order from the top bit downwards, and each one waits for the one above it",
                            "It does not: all the stages switch at the same moment, so the delay is constant and only the area grows",
                        ],
                        "a": 0,
                        "whys": [
                            r"The carry chain is the critical path: with `1111 + 0001` the top bit cannot settle until a carry generated at the bottom has rippled through every full adder.",
                            r"Gate count and delay are different things. Gates on separate paths switch at the same time; only gates that wait on each other add up, and in a ripple adder that is the carry chain, one stage per bit.",
                            r"Sum bits do not wait on each other, and nothing flows downwards. Each sum bit waits on the carry arriving from below, which is why the top bit is the last to settle.",
                            r"The stages cannot all switch at once, because each needs the carry from its neighbour before it knows its own carry. The waiting is sequential, and that is what makes the delay linear.",
                        ],
                        "why": r"""
Every full adder needs its carry-in before it can produce its carry-out, and the
carry-in comes from the stage below. In the worst case, `1111 + 0001`, a carry
generated at bit 0 has to pass through every stage before the top bit is right, so
the delay is one carry stage per bit. Gate count alone does not decide delay, because
gates on independent paths switch together; it is the chain of dependencies that
adds up, and it runs upwards through the carries, not downwards through the sums.
""",
                    },
                ],
            },
            "lab": {
                "title": "From one NAND to a 4-bit adder",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
`nand(a, b)` is already written for you. It is the **only** primitive you may
compute with: everything else in this file must be built from it, directly or
indirectly. No `and`, `or`, `not`, `^`, `+` or `if` on the signal values
themselves — the checks watch how often `nand` is called.

**`not_gate(a)`, `and_gate(a, b)`, `or_gate(a, b)`, `xor_gate(a, b)`** —
the four familiar gates, each returning 0 or 1.

**`half_adder(a, b)`** — returns `(sum, carry)`.

```text
half_adder(1, 1)  ->  (0, 1)
half_adder(1, 0)  ->  (1, 0)
```

**`full_adder(a, b, cin)`** — returns `(sum, cout)`. Build it from two half
adders and one OR; do not write out a fresh truth table.

**`to_bits(value, width)`** — the unsigned value as a list of 0/1,
**most significant bit first**. Raise `ValueError` when the value is negative or
will not fit.

**`from_bits(bits)`** — the reverse.

```text
to_bits(10, 4)          ->  [1, 0, 1, 0]
from_bits([1, 0, 1, 0]) ->  10
```

**`ripple_add(a_bits, b_bits, cin=0)`** — returns `(sum_bits, cout)`. Chain one
full adder per bit position, starting at the least significant end and passing
each carry along. Raise `ValueError` when the two operands have different
widths, or when they are empty.

```text
ripple_add([0, 1, 1, 1], [0, 0, 0, 1])  ->  ([1, 0, 0, 0], 0)     7 + 1 = 8
ripple_add([1, 1, 1, 1], [0, 0, 0, 1])  ->  ([0, 0, 0, 0], 1)    15 + 1 = 16
```

The width is whatever you pass, so the same function is a 4-bit adder and a
16-bit adder.
''',
                "files": [{"name": "main.py", "content": r'''
def nand(a, b):
    """The one primitive you are given: 0 only when both inputs are 1."""
    return 0 if (a and b) else 1


def not_gate(a):
    """NOT from a single NAND."""
    # your code here


def and_gate(a, b):
    """AND from NANDs."""
    # your code here


def or_gate(a, b):
    """OR from NANDs."""
    # your code here


def xor_gate(a, b):
    """XOR from NANDs."""
    # your code here


def half_adder(a, b):
    """(sum, carry) for two bits."""
    # your code here


def full_adder(a, b, cin):
    """(sum, cout) for two bits and a carry in."""
    # your code here


def to_bits(value, width):
    """Unsigned value as a width-long list of bits, MSB first."""
    # your code here


def from_bits(bits):
    """Bits, MSB first, back to an unsigned integer."""
    # your code here


def ripple_add(a_bits, b_bits, cin=0):
    """(sum_bits, cout) from a chain of full adders."""
    # your code here


print(half_adder(1, 1))
print(full_adder(1, 1, 1))
print(ripple_add(to_bits(7, 4), to_bits(9, 4)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def nand(a, b):
    """The one primitive you are given: 0 only when both inputs are 1."""
    return 0 if (a and b) else 1


def not_gate(a):
    """NOT from a single NAND."""
    return nand(a, a)


def and_gate(a, b):
    """AND from NANDs."""
    return not_gate(nand(a, b))


def or_gate(a, b):
    """OR from NANDs: De Morgan turns A + B into (A'B')'."""
    return nand(not_gate(a), not_gate(b))


def xor_gate(a, b):
    """XOR from NANDs: the classic four-gate network."""
    shared = nand(a, b)
    return nand(nand(a, shared), nand(b, shared))


def half_adder(a, b):
    """(sum, carry) for two bits."""
    return xor_gate(a, b), and_gate(a, b)


def full_adder(a, b, cin):
    """(sum, cout) for two bits and a carry in."""
    sum1, carry1 = half_adder(a, b)
    sum2, carry2 = half_adder(sum1, cin)
    return sum2, or_gate(carry1, carry2)


def to_bits(value, width):
    """Unsigned value as a width-long list of bits, MSB first."""
    if width < 1:
        raise ValueError("width must be at least 1")
    if value < 0 or value >= (1 << width):
        raise ValueError(f"{value} does not fit in {width} unsigned bits")
    return [(value >> (width - 1 - k)) & 1 for k in range(width)]


def from_bits(bits):
    """Bits, MSB first, back to an unsigned integer."""
    value = 0
    for bit in bits:
        value = value * 2 + bit
    return value


def ripple_add(a_bits, b_bits, cin=0):
    """(sum_bits, cout) from a chain of full adders."""
    if len(a_bits) != len(b_bits):
        raise ValueError("operands must be the same width")
    if not a_bits:
        raise ValueError("width must be at least 1")
    carry = cin
    out = []
    for a, b in zip(reversed(a_bits), reversed(b_bits)):
        bit, carry = full_adder(a, b, carry)
        out.append(bit)
    out.reverse()
    return out, carry


print(half_adder(1, 1))
print(full_adder(1, 1, 1))
print(ripple_add(to_bits(7, 4), to_bits(9, 4)))
'''}],
                "hints": [
                    "`not_gate(a)` is `nand(a, a)`: tying both inputs together leaves NAND with nothing to do but invert.",
                    "AND is a NAND followed by an inverter; OR is an inverter on each input followed by a NAND.",
                    "XOR needs four NANDs. Compute `shared = nand(a, b)` once, then `nand(nand(a, shared), nand(b, shared))`.",
                    "`ripple_add` walks the operands with `zip(reversed(a_bits), reversed(b_bits))`, keeps the carry in a variable between iterations, and reverses the collected sum bits at the end.",
                ],
                "tests": [
                    {"name": "NOT, AND and OR", "code": r'''
assert (not_gate(0), not_gate(1)) == (1, 0), f"not_gate gave {(not_gate(0), not_gate(1))!r}"
for _a, _b, _want in [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 1)]:
    _got = and_gate(_a, _b)
    assert _got == _want, f"and_gate({_a}, {_b}) gave {_got!r}, expected {_want}"
for _a, _b, _want in [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 1)]:
    _got = or_gate(_a, _b)
    assert _got == _want, f"or_gate({_a}, {_b}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "XOR", "code": r'''
for _a, _b, _want in [(0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)]:
    _got = xor_gate(_a, _b)
    assert _got == _want, f"xor_gate({_a}, {_b}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "Every gate is built from nand", "code": r'''
_calls = []
_real_nand = nand
def _spy(a, b):
    _calls.append((a, b))
    return _real_nand(a, b)
nand = _spy
for _name, _fn, _args in [("not_gate", not_gate, (1,)), ("and_gate", and_gate, (1, 0)),
                          ("or_gate", or_gate, (1, 0)), ("xor_gate", xor_gate, (1, 0))]:
    _before = len(_calls)
    _fn(*_args)
    assert len(_calls) > _before, f"{_name} must be built from nand(), not from Python operators"
nand = _real_nand
'''},
                    {"name": "half_adder", "code": r'''
for _a, _b, _want in [(0, 0, (0, 0)), (0, 1, (1, 0)), (1, 0, (1, 0)), (1, 1, (0, 1))]:
    _got = tuple(half_adder(_a, _b))
    assert _got == _want, f"half_adder({_a}, {_b}) gave {_got!r}, expected {_want}"
'''},
                    {"name": "full_adder, all eight rows", "code": r'''
for _a in (0, 1):
    for _b in (0, 1):
        for _c in (0, 1):
            _s, _co = full_adder(_a, _b, _c)
            _total = _a + _b + _c
            assert (_s, _co) == (_total % 2, _total // 2), \
                f"full_adder({_a}, {_b}, {_c}) gave {(_s, _co)!r}, expected {(_total % 2, _total // 2)}"
'''},
                    {"name": "to_bits / from_bits round-trip and limits", "code": r'''
assert to_bits(10, 4) == [1, 0, 1, 0], f"to_bits(10, 4) gave {to_bits(10, 4)!r}"
assert to_bits(0, 1) == [0], f"to_bits(0, 1) gave {to_bits(0, 1)!r}"
assert from_bits([1, 0, 1, 0]) == 10, f"from_bits([1,0,1,0]) gave {from_bits([1, 0, 1, 0])!r}"
assert from_bits([0]) == 0, "a single zero bit is 0"
for _v in range(64):
    assert from_bits(to_bits(_v, 6)) == _v, f"round-trip failed for {_v}"
for _bad in [(16, 4), (-1, 4), (2, 1)]:
    try:
        to_bits(*_bad)
        assert False, f"to_bits{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "ripple_add matches arithmetic on every 4-bit pair", "code": r'''
for _a in range(16):
    for _b in range(16):
        _bits, _cout = ripple_add(to_bits(_a, 4), to_bits(_b, 4))
        _total = _a + _b
        assert from_bits(_bits) == _total & 15, \
            f"{_a} + {_b} gave sum bits {_bits!r} ({from_bits(_bits)}), expected {_total & 15}"
        assert _cout == (_total >> 4) & 1, \
            f"{_a} + {_b} gave carry {_cout!r}, expected {(_total >> 4) & 1}"
_bits, _cout = ripple_add(to_bits(7, 4), to_bits(8, 4), 1)
assert (from_bits(_bits), _cout) == (0, 1), \
    f"7 + 8 + carry-in gave {(from_bits(_bits), _cout)!r}, expected (0, 1)"
'''},
                    {"name": "ripple_add rejects bad operands", "code": r'''
for _a, _b in [([1, 0], [1]), ([], [])]:
    try:
        ripple_add(_a, _b)
        assert False, f"ripple_add({_a!r}, {_b!r}) should raise ValueError"
    except ValueError:
        pass
_bits, _cout = ripple_add([1] * 16, [0] * 15 + [1])
assert (from_bits(_bits), _cout) == (0, 1), \
    f"the same function should add 16-bit words, got {(from_bits(_bits), _cout)!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Sequential logic and state machines",
            "summary": "Storage, the clock edge, and a Moore machine that watches a bit stream.",
            "concepts": [
                "Combinational output depends on inputs alone; sequential output depends on history",
                "A D flip-flop copies D to Q on the clock edge and holds it in between",
                "Sampling then updating is what makes shift registers work — every flop reads the old values",
                "A register is n flip-flops on a shared clock, usually with a load enable",
                "Setup and hold times, and why glitches between edges do not matter",
                "Moore machines output from the state; Mealy machines output from state and input",
                "Overlapping pattern detection: the next state is the longest suffix that is still a prefix",
            ],
            "read": [
                {
                    "title": "A clock edge is when memory happens",
                    "minutes": 15,
                    "body": r'''
Press the button at a pedestrian crossing and let go. The light does not change at
once, and it does not forget that you asked; a minute later, when the traffic phase
ends, it stops the cars. Somewhere in the controller a bit was set when you pressed,
held while you waited, and cleared when the light served it. No function of "is the
button pressed right now" can do that. The adder from the last module has no memory:
give it the same inputs and it gives the same answer, every time, with no idea what
it answered before. A circuit that remembers is a different kind of thing, and the
difference is the subject of this module.

## Holding a bit, and the trouble with holding it all the time

Two NAND gates can hold a bit if each one's output feeds the other's input. Push one
output to 1 and the loop holds it there after you let go; push it to 0 and it holds
that. That is a *latch*, and it is enough to remember the button press. The trouble
starts when you try to build anything out of latches that copy their input whenever
they are told to.

Suppose a latch is *transparent* while the clock is high: $Q$ follows $D$ for as long
as the clock stays 1, and freezes when it goes to 0. Now chain three of them, each
one's $Q$ wired to the next one's $D$, to make a shift register, a circuit that is
supposed to move a bit one stage to the right every clock cycle. Put a 1 on the first
input and raise the clock. The first latch's $Q$ becomes 1. But the clock is still
high, so the second latch is also transparent, and its $D$ is now 1, so its $Q$
becomes 1 too, and then the third. By the time the clock falls, the bit has raced all
the way to the end. It was meant to move one stage; it moved three, and how many it
moves depends on how long the clock stays high compared with how fast the latches
respond, which is not a thing a designer wants to reason about.

The fix is to make storage happen at an *instant* rather than during an interval. A
*D flip-flop* samples $D$ at the rising edge of the clock, copies it to $Q$, and then
ignores $D$ entirely until the next rising edge. Between edges $Q$ holds. Now chain
three flip-flops. At the edge, every flop samples the value that was on its $D$
*before* the edge; the first sees the input 1, the second sees the first's old $Q$,
the third sees the second's old $Q$. Then all three update together. The bit moves
exactly one stage per edge, whatever the clock's shape, because by the time the
second flop could see the new value the edge is over.

```python
class Latch:
    """Transparent while the clock is high: Q follows D."""
    def __init__(self):
        self.q = 0

    def clock_high(self, d):
        self.q = d
        return self.q


class DFlipFlop:
    """Samples D at the edge only."""
    def __init__(self):
        self.q = 0
        self.d = 0

    def set_d(self, value):
        self.d = value

    def tick(self):
        self.q = self.d
        return self.q


latches = [Latch(), Latch(), Latch()]
value = 1
for latch in latches:
    value = latch.clock_high(value)
print("latches after one high phase:", [lt.q for lt in latches])

flops = [DFlipFlop(), DFlipFlop(), DFlipFlop()]
for cycle in range(3):
    flops[0].set_d(1 if cycle == 0 else 0)
    for previous, flop in zip(flops, flops[1:]):
        flop.set_d(previous.q)
    for flop in flops:
        flop.tick()
    print("flops after edge", cycle + 1, ":", [f.q for f in flops])
```

The latch chain prints `[1, 1, 1]` after a single clock phase: the bit ran through.
The flip-flop chain prints `[1, 0, 0]`, then `[0, 1, 0]`, then `[0, 0, 1]`: one stage
per edge. Look at the order of operations that makes the second chain work. Every
`set_d` is done before any `tick`, so each flop samples its neighbour's *old* output.
That discipline, sample everything and then update everything, is the whole content
of the phrase "edge-triggered", and it is what the lab's `DFlipFlop` asks you to
honour: `set_d` may touch only the pending input, and only `tick` may move `q`.

The lab's test for a chain is the same experiment with two flops. One holds 1 and is
given a new $D$ of 0; the other holds 0 and is given the first one's $Q$. After both
tick, the pair reads `(0, 1)`: the 1 moved along by one, and the 0 came in behind it.
A flip-flop that updates `q` inside `set_d` passes every single-flop test and fails
this one, because the second flop would read the *new* 0 instead of the old 1.

## A register is flops on a shared clock, plus a choice

A register holding an $n$-bit word is $n$ flip-flops driven by the same clock, bit
$i$ of the word living in flop $i$. Reading it is assembling the $Q$ outputs into an
integer; loading it is putting each bit of the new value on the matching $D$ and
ticking.

Most registers also need to *not* load on some cycles. In real hardware the clock
reaches every flop on every cycle; you cannot quietly stop it for one register, so
the edge is going to happen whether the register wants a new value or not. The answer
is to put a chooser in front of each $D$: with the load enable at 1, $D$ comes from
the new value; with it at 0, $D$ is wired back from the flop's own $Q$, so that the
edge copies the old value over itself and the word is preserved. Nothing is skipped.
The flop ticks, and it ticks into the same state. That is what the lab's
`set_input(value, enable=0)` is meant to arrange: drive each flop's $D$ from its own
$Q$, so that the following `tick` keeps the word.

```python
class DFlipFlop:
    def __init__(self, q=0):
        self.q = q
        self.d = q

    def set_d(self, value):
        self.d = value

    def tick(self):
        self.q = self.d
        return self.q


class Register:
    def __init__(self, width, value=0):
        self.width = width
        self.flops = [DFlipFlop((value >> i) & 1) for i in range(width)]

    def read(self):
        word = 0
        for i, flop in enumerate(self.flops):
            word |= flop.q << i
        return word

    def set_input(self, value, enable=1):
        for i, flop in enumerate(self.flops):
            flop.set_d((value >> i) & 1 if enable else flop.q)

    def tick(self):
        for flop in self.flops:
            flop.tick()
        return self.read()


reg = Register(4)
reg.set_input(10)
print("after set_input:", reg.read())
print("after tick:     ", reg.tick())
reg.set_input(5, enable=0)
print("held:           ", reg.tick())
reg.set_input(5, enable=1)
print("loaded:         ", reg.tick())
```

`after set_input: 0`, then `10`, then `10` again with the enable low even though 5 was
offered, then `5`. Bit $i$ of the word lives at index $i$, least significant first, so
`(value >> i) & 1` picks it out and `flop.q << i` puts it back. Note that this is the
opposite of the previous module's `to_bits`, which was most significant first; both
conventions are in use, and the lab tells you which one it wants for each structure.

The enable matters even in a simulation, where skipping the tick looks easier. Suppose a
value of 7 was placed on the inputs earlier in the cycle and then the enable dropped.
A register that leaves $D$ untouched when the enable is low would load the 7 at the
edge anyway. Feeding $Q$ back is what makes the enable override whatever was offered.

## Between the edges, nothing is looking

An edge-triggered design has a comfortable consequence. Since $D$ is sampled only at
the edge, whatever $D$ does *between* edges does not matter. The combinational logic
feeding a flop, an adder, a decoder, the XOR network from the last module, can glitch
and settle and glitch again during the cycle, and none of that is stored, provided
the value is right and steady by the time the edge arrives. The requirement has a
name, *setup time*: $D$ must be stable for a short interval before the edge, and, for
*hold time*, a short interval after it. Meet those two, and the clock period only has
to be long enough for the slowest combinational path to settle. This is why
synchronous design is the default for almost everything: the timing question becomes
one number, the clock period, rather than a separate argument about every wire.

## A machine that remembers four bits

The lab's third part is a circuit that watches a stream of bits, one per clock, and
raises its output for a cycle whenever the last four bits it saw were $1, 0, 1, 1$. It
has to remember, but it does not have to remember the whole stream. Ask what the
circuit actually needs to know at each moment, and the answer is: how much of the
pattern it has matched so far. That is a number from 0 to 4, and each value is a
*state*.

Name them by what has been matched: `S0` (nothing useful yet), `S1` (a `1`), `S10`,
`S101`, and `S1011` (the whole pattern, so the output is 1). The transitions that
advance the match are easy to write down: `S0` on a 1 goes to `S1`, `S1` on a 0 goes
to `S10`, and so on. The ones that matter are the failures, and the rule for them is
the rule that makes overlapping matches work: *the next state is the longest suffix
of the stream seen so far that is still a prefix of the pattern*.

Take `S101` and a 0 arrives. The stream now ends `1010`. Going back to `S0` throws
away the `10` at the end, which is a perfectly good start on a new `1011`. The
longest suffix of `1010` that is a prefix of `1011` is `10`, so the next state is
`S10`. Take `S1011` and a 1 arrives: the stream ends `10111`, whose longest useful
suffix is the final `1`, so the next state is `S1`. Take `S1011` and a 0: the stream
ends `10110`, ending in `10`, so `S10`. And `S1` on a 1 stays in `S1`, because `11`
ends in a `1` that could still begin the pattern.

```python
PATTERN = "1011"
STATES = ["S0"] + ["S" + PATTERN[:k] for k in range(1, len(PATTERN) + 1)]

def next_state(state, bit):
    seen = ("" if state == "S0" else state[1:]) + str(bit)
    for length in range(len(seen), -1, -1):
        suffix = seen[len(seen) - length:]
        if PATTERN.startswith(suffix):
            return "S" + suffix if suffix else "S0"
    return "S0"

for state in STATES:
    for bit in (0, 1):
        print(f"{state:<6} on {bit} -> {next_state(state, bit)}")
```

That prints all ten transitions, and the four that trip people up read
`S101 on 0 -> S10`, `S1011 on 0 -> S10`, `S1011 on 1 -> S1`, and
`S10 on 0 -> S0` (the stream ends `100`, and no suffix of that begins `1011`).
Compare them with a table you wrote by hand before trusting either.

The output is a function of the state alone: 1 in `S1011`, 0 elsewhere. That is what
makes the machine a *Moore* machine. A *Mealy* machine would compute its output from
the state and the current input together, and could announce the match on the same
cycle the fourth bit arrives rather than one state later; the price is that its
output can change the moment the input does, in the middle of a cycle, which is
exactly the between-edges behaviour synchronous design was arranged to avoid. Moore
outputs come straight from flip-flops and are steady for a whole cycle.

Now run the machine over the lab's example stream and watch the state:

```python
TABLE = {
    ("S0", 0): "S0", ("S0", 1): "S1",
    ("S1", 0): "S10", ("S1", 1): "S1",
    ("S10", 0): "S0", ("S10", 1): "S101",
    ("S101", 0): "S10", ("S101", 1): "S1011",
    ("S1011", 0): "S10", ("S1011", 1): "S1",
}

state = "S0"
outputs = []
for bit in [1, 1, 0, 1, 0, 1, 1, 0, 1, 1]:
    state = TABLE[(state, bit)]
    out = 1 if state == "S1011" else 0
    outputs.append(out)
    print(f"bit {bit} -> {state:<6} output {out}")
print(outputs)
```

The stream is `1101011011`. The first `1011` ends at the seventh bit and the second
ends at the tenth, and they share a bit: the second match begins inside the first, so
the output is `[0, 0, 0, 0, 0, 0, 1, 0, 0, 1]`. Follow the state column after the
seventh bit: `S1011` on the 0 goes to `S10`, not `S0`, and that is the transition
that lets the second match be found. Send it to `S0` instead and the output ends
`1, 0, 0, 0`; the second occurrence is missed. Going back to the start on a failed
match is the mistake people make, and it is tempting because "the match failed, start
again" sounds like exactly the right thing to do. It is the right thing only when the
tail of the failed attempt cannot be the head of a new one.

## Where it stops holding

A finite-state machine has a fixed number of states, and that is its limit. The
detector cannot be extended to report "more 1s than 0s so far", because that needs an
unbounded count, and no finite table of states holds one; problems of that shape need
a counter or a memory, which is the datapath of the capstone. Five states remember
exactly as much as five states can.

The clean edge is also an idealisation. Real clocks arrive at different flops at
slightly different times, *clock skew*, and if the skew is larger than a flop's hold
time a chain can race in the way the latch chain did. An input that comes from
outside the clock domain, a button, a network line, can change during the setup
window, and a flop that samples a changing input may sit between 0 and 1 for a while,
*metastability*, before falling one way or the other. Real designs pass such inputs
through two flops in series to give them time to settle. In the simulation, `tick()`
is an ideal instant, and none of this can happen; that is the model's convenience,
and its blindness.

## What you are about to build

The lab, *Flip-flops, registers and a 1011 detector*, is the three pieces of this
reading in order. `DFlipFlop` keeps `d` and `q` apart and moves one into the other
only in `tick`. `Register` is a list of flops, least significant bit at index 0,
whose `set_input` with the enable low feeds each flop its own `q`. `SequenceDetector`
holds the ten-entry transition table, four of whose entries are failed matches that
land somewhere other than `S0`, an `output` that reads the state and nothing else, and
`run`, which steps the machine along a list and collects the outputs. The starter's
last line runs the stream traced above and should print
`[0, 0, 0, 0, 0, 0, 1, 0, 0, 1]`.
''',
                },
            ],
            "quiz": {
                "title": "Edges, holds and the transitions that fail well",
                "minutes": 8,
                "questions": [
                    {
                        "q": "After `ff = DFlipFlop()` and then `ff.set_d(1)`, what is `ff.q`, and why?",
                        "opts": [
                            "0: the D input has been driven, but Q moves only at the next clock edge",
                            "1: a D flip-flop copies its input to its output as soon as the input changes",
                            "1: a fresh flip-flop's Q follows D until the first tick freezes it in place",
                            "Undefined until the first tick, since nothing has been latched yet",
                        ],
                        "a": 0,
                        "whys": [
                            r"Driving D changes what the flop will store; storing happens on `tick`, and until then Q holds its starting 0.",
                            r"That is a transparent latch, and it is exactly the device the module rejects: chained together, latches race a value through every stage in one clock phase.",
                            r"There is no transparent phase before the first edge. A flip-flop is edge-triggered from the moment it exists; `DFlipFlop()` starts holding 0 and holds it until a tick.",
                            r"The lab specifies `DFlipFlop(q=0)`: the flop starts holding a definite 0, with D equal to it. Storage is never undefined in this model, only unchanged.",
                        ],
                        "why": r"""
`set_d` drives the input; it does not store anything. Q changes only when `tick`
models the rising edge, so after `set_d(1)` the flop still reads its starting value,
0. A flop whose Q followed D immediately would be a transparent latch, and the reason
the module insists on the edge is that latches chained together let a value race all
the way through in one clock phase. The lab's first test, `set_d` then check `q`, is
written to catch exactly that.
""",
                    },
                    {
                        "q": "Flop `a` holds 1 and flop `b` holds 0. The code runs `a.set_d(0)`, then `b.set_d(a.q)`, then `a.tick()`, then `b.tick()`. What does `(a.q, b.q)` read afterwards?",
                        "opts": [
                            "`(0, 1)`: each flop sampled the other's old value before either updated",
                            "`(0, 0)`: `a` ticks first, so `b` takes the new 0 that `a` now holds",
                            "`(0, 1)` only because `b` was set up before `a` ticked; ticking `b` first would give `(0, 0)`",
                            "`(1, 0)`: the values swap, because a chain hands each flop's value to the other",
                        ],
                        "a": 0,
                        "whys": [
                            r"`b.set_d(a.q)` captured the 1 while `a` still held it; the ticks then commit both pending inputs.",
                            r"The order of the ticks does not matter, because `b`'s D was fixed at 1 by `b.set_d(a.q)` before any tick ran. `a.tick()` changes `a.q`, not `b.d`.",
                            r"The sampling happened in the `set_d` calls, both of which ran before either tick; swapping the tick order changes nothing, since each tick reads its own D and D is already fixed.",
                            r"The chain runs one way: `b` reads from `a`, and `a` reads the new input 0. Nothing flows from `b` back to `a`, so `a` becomes 0 and `b` becomes the 1 that `a` used to hold.",
                        ],
                        "why": r"""
Both `set_d` calls happen before either `tick`, so `b` samples the 1 that `a` still
holds, and `a` samples the new 0. The ticks then commit what was sampled, in either
order, giving `(0, 1)`: the 1 moved one stage along the chain and the 0 came in
behind it. The result depends on the tick order only if `set_d` updates `q`
immediately, which is the transparent-latch mistake; with a proper edge-triggered
flop, sampling and updating are separate steps and the order of the updates is
irrelevant.
""",
                    },
                    {
                        "q": "A register's load enable is low when the clock edge arrives. Which describes what happens?",
                        "opts": [
                            "Every flop ticks and reloads its own current Q, so the stored word comes out unchanged",
                            "The clock edge is suppressed for that register, so none of its flops tick at all",
                            "The flops tick and load zeros, because no new value was supplied for them",
                            "The flops keep whatever was last placed on their D inputs, even if it was never loaded",
                        ],
                        "a": 0,
                        "whys": [
                            r"The enable steers each D input back from its own Q, so the edge copies the old word over itself.",
                            r"In hardware the clock reaches every flop on every cycle; a register cannot opt out of an edge. What it can do is arrange for the edge to store the value it already holds.",
                            r"Nothing forces zeros onto D. With the enable low, D is driven from Q, so the edge stores the current bits, not blanks.",
                            r"That is what happens if `set_input` leaves D alone when the enable is low, and it is wrong: a value offered earlier and then withdrawn would be loaded anyway. Feeding Q back is what makes the enable override it.",
                        ],
                        "why": r"""
The enable is a chooser in front of each D input, not a switch on the clock. With it
low, each flop's D is driven from its own Q, so the edge that arrives regardless
stores the same bits again and the word is preserved. Suppressing the edge is not
available in hardware, zeros are never involved, and leaving D untouched would let a
value placed there earlier in the cycle sneak in; the lab's `set_input(value, enable=0)`
has to feed Q back explicitly for that reason.
""",
                    },
                    {
                        "q": "What makes the 1011 detector a Moore machine rather than a Mealy machine?",
                        "opts": [
                            "Its output is computed from the current state alone, so it holds steady for a whole clock cycle",
                            "Its output depends on the current input as well as the state, so it can respond within the same cycle",
                            "Its behaviour is fixed by a finite transition table with one entry per state and input",
                            "It detects overlapping occurrences of the pattern instead of restarting after each match",
                        ],
                        "a": 0,
                        "whys": [
                            r"`output()` takes no input; it looks at the state and nothing else, which is the Moore property.",
                            r"That describes a Mealy machine, whose output can change the moment the input does, in the middle of a cycle. The lab's `output()` has no input argument at all.",
                            r"Both kinds of machine have a finite transition table. The distinction is where the output comes from, not how the next state is chosen.",
                            r"Overlap is a property of the transition table, which either kind of machine can have. Moore versus Mealy is about the output function.",
                        ],
                        "why": r"""
A Moore machine's output is a function of its state alone, which is why the lab's
`output()` takes no argument: it returns 1 in `S1011` and 0 elsewhere, and cannot
change until the next edge moves the state. A Mealy machine reads the input as well
and can announce a match one cycle earlier, at the price of an output that follows
the input between edges. Both kinds have finite tables, and both can handle
overlapping matches; the difference is entirely in what the output depends on.
""",
                    },
                    {
                        "q": "The detector is in `S101` and a 0 arrives. Where should it go, and why?",
                        "opts": [
                            "`S10`: the stream now ends `1010`, and `10` is the longest tail that still begins the pattern",
                            "`S0`: the attempt has failed, so everything matched so far is discarded and the search restarts",
                            "`S1`: the `1` that began the attempt is still valid, so only the later bits are discarded",
                            "`S101`: a bit that does not fit the pattern is ignored, and the state holds until a 1 arrives",
                        ],
                        "a": 0,
                        "whys": [
                            r"The last two bits, `10`, are the first two bits of `1011`, so a match may already be under way.",
                            r"Restarting throws away the `10` at the end of the stream, which is a valid start on a new match. `1010` followed by `11` contains `1011`, and a machine in `S0` would miss it.",
                            r"The first `1` of the failed attempt is now three bits back. What matters is the tail of the stream, and the tail `10` is longer than the tail `1`; the state records the longest usable suffix.",
                            r"A Moore machine moves on every clock; there is no ignoring an input. Holding in `S101` would claim that the last three bits were `101` when they were `010`.",
                        ],
                        "why": r"""
After `S101` and a 0 the stream ends `1010`. Ask which suffix of that is a prefix of
`1011`: `1010` is not, `010` is not, `10` is, so the machine goes to `S10`. Dropping to
`S0` is the tempting move, because the attempt did fail, but it discards a `10` that
could be the first two bits of the next match, and the lab's test with overlapping
streams catches exactly that. The state holds neither the beginning of the failed
attempt nor the failed attempt itself; it holds the longest tail that is still useful.
""",
                    },
                    {
                        "q": "Could a machine of this kind, with a fixed set of states, report whether the stream so far has contained more 1s than 0s?",
                        "opts": [
                            "No: that needs an unbounded count, and a fixed set of states cannot hold one",
                            "Yes: add one state per possible difference, since the difference is always small",
                            "Yes: use the output bit as a running tally that the transitions increment each cycle",
                            "No: a Moore machine cannot read its input at all, only its current state",
                        ],
                        "a": 0,
                        "whys": [
                            r"A stream of a million 1s has a lead of a million, and no finite table has a state for every possible lead.",
                            r"The difference is not bounded: a stream of $k$ ones followed by $k$ zeros needs the machine to have remembered $k$, for any $k$, and a finite table runs out of states.",
                            r"The output is a single bit read off the state; it cannot count. A tally needs storage that grows with the count, which is a register or a memory, not a state.",
                            r"A Moore machine reads its input on every transition; only its output ignores the input. The limit is the finite number of states, not the ability to see the bits.",
                        ],
                        "why": r"""
A finite-state machine remembers exactly as much as its number of states allows. To
know whether 1s lead 0s, it would need to remember the lead, which can be any
integer, and no finite table of states can distinguish a lead of a million from a
lead of a million and one. That is the boundary between a state machine and the
datapath of the capstone, which has registers to count with. The input is not the
problem, since transitions read it on every cycle; the single output bit is not a
tally either.
""",
                    },
                ],
            },
            "lab": {
                "title": "Flip-flops, registers and a 1011 detector",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Nothing here happens because you assigned a value. Things happen on a **clock
edge**, and only then.

## `DFlipFlop`

- `DFlipFlop(q=0)` — starts holding `q`, with the D input equal to it. Raise
  `ValueError` if `q` is not 0 or 1.
- `set_d(value)` — drive the D input. `ValueError` for anything but 0 or 1.
  **`q` must not change.**
- `tick()` — the rising edge: copy D into `q` and return the new `q`.

That split is the whole point. Two flops wired in a chain both sample *before*
either updates, so a value moves exactly one stage per tick rather than racing
all the way down.

## `Register`

- `Register(width, value=0)` — `width` flip-flops, LSB at index 0. `ValueError`
  for a width below 1 or a value that will not fit.
- `read()` — the stored word as an unsigned integer.
- `set_input(value, enable=1)` — with `enable` truthy, drive the D inputs from
  `value` (`ValueError` if it does not fit in `width` bits). With `enable`
  falsy, drive each flop's D from its own `q`, so the next tick keeps the word.
- `tick()` — clock every flop and return the new `read()`.

## `SequenceDetector`

A Moore machine that raises its output for one cycle whenever the last four
bits it has seen are `1, 0, 1, 1`. Occurrences may overlap.

States: `"S0"`, `"S1"`, `"S10"`, `"S101"`, `"S1011"` — each named for the part
of the pattern matched so far.

- `SequenceDetector(state="S0")` — `ValueError` for a state not in `STATES`.
- `next_state(state, bit)` — the transition table, as a pure function.
- `output()` — 1 exactly in `"S1011"`, otherwise 0. It depends on the state
  alone: that is what makes the machine Moore rather than Mealy.
- `step(bit)` — advance one clock and return the new output. `ValueError` for a
  bit that is not 0 or 1.
- `run(bits)` — the output after each bit, as a list.

The transitions you need to get right are the ones that fail a partial match.
From `"S101"` a `0` does not go back to `"S0"`: the stream now ends `1010`, and
`10` is still a live prefix, so the machine lands in `"S10"`. From `"S1011"` a
`1` leaves the stream ending `10111`, whose longest useful suffix is `1`.

```text
run([1, 1, 0, 1, 0, 1, 1, 0, 1, 1])
  -> [0, 0, 0, 0, 0, 0, 1, 0, 0, 1]
```
''',
                "files": [{"name": "main.py", "content": r'''
class DFlipFlop:
    """One bit of edge-triggered storage."""

    def __init__(self, q=0):
        # your code here
        pass

    def set_d(self, value):
        """Drive the D input. Q does not move until the next tick."""
        # your code here

    def tick(self):
        """Rising clock edge: Q takes the value of D."""
        # your code here


class Register:
    """width flip-flops sharing one clock, with a load enable."""

    def __init__(self, width, value=0):
        # your code here
        pass

    def read(self):
        """The stored word as an unsigned integer."""
        # your code here

    def set_input(self, value, enable=1):
        """Drive the D inputs, or hold the current word when enable is falsy."""
        # your code here

    def tick(self):
        """Clock every flip-flop, then return the new word."""
        # your code here


class SequenceDetector:
    """Moore machine: output 1 for one cycle on each (overlapping) 1011."""

    STATES = ("S0", "S1", "S10", "S101", "S1011")

    def __init__(self, state="S0"):
        # your code here
        pass

    def next_state(self, state, bit):
        """The transition table."""
        # your code here

    def output(self):
        """A function of the state only."""
        # your code here

    def step(self, bit):
        """One clock: move state, return the new output."""
        # your code here

    def run(self, bits):
        """The output after each bit."""
        # your code here


reg = Register(4)
reg.set_input(10)
print(reg.tick())
print(SequenceDetector().run([1, 1, 0, 1, 0, 1, 1, 0, 1, 1]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class DFlipFlop:
    """One bit of edge-triggered storage."""

    def __init__(self, q=0):
        if q not in (0, 1):
            raise ValueError("a flip-flop holds 0 or 1")
        self.q = q
        self.d = q

    def set_d(self, value):
        """Drive the D input. Q does not move until the next tick."""
        if value not in (0, 1):
            raise ValueError("D must be 0 or 1")
        self.d = value

    def tick(self):
        """Rising clock edge: Q takes the value of D."""
        self.q = self.d
        return self.q


class Register:
    """width flip-flops sharing one clock, with a load enable."""

    def __init__(self, width, value=0):
        if width < 1:
            raise ValueError("a register needs at least one bit")
        if value < 0 or value >= (1 << width):
            raise ValueError(f"{value} does not fit in {width} bits")
        self.width = width
        self.flops = [DFlipFlop((value >> i) & 1) for i in range(width)]

    def read(self):
        """The stored word as an unsigned integer."""
        word = 0
        for i, flop in enumerate(self.flops):
            word |= flop.q << i
        return word

    def set_input(self, value, enable=1):
        """Drive the D inputs, or hold the current word when enable is falsy."""
        if not enable:
            for flop in self.flops:
                flop.set_d(flop.q)
            return
        if value < 0 or value >= (1 << self.width):
            raise ValueError(f"{value} does not fit in {self.width} bits")
        for i, flop in enumerate(self.flops):
            flop.set_d((value >> i) & 1)

    def tick(self):
        """Clock every flip-flop, then return the new word."""
        for flop in self.flops:
            flop.tick()
        return self.read()


class SequenceDetector:
    """Moore machine: output 1 for one cycle on each (overlapping) 1011."""

    STATES = ("S0", "S1", "S10", "S101", "S1011")

    TABLE = {
        ("S0", 0): "S0",
        ("S0", 1): "S1",
        ("S1", 0): "S10",
        ("S1", 1): "S1",
        ("S10", 0): "S0",
        ("S10", 1): "S101",
        ("S101", 0): "S10",
        ("S101", 1): "S1011",
        ("S1011", 0): "S10",
        ("S1011", 1): "S1",
    }

    def __init__(self, state="S0"):
        if state not in self.STATES:
            raise ValueError(f"unknown state {state!r}")
        self.state = state

    def next_state(self, state, bit):
        """The transition table."""
        if state not in self.STATES:
            raise ValueError(f"unknown state {state!r}")
        if bit not in (0, 1):
            raise ValueError("the input bit must be 0 or 1")
        return self.TABLE[(state, bit)]

    def output(self):
        """A function of the state only."""
        return 1 if self.state == "S1011" else 0

    def step(self, bit):
        """One clock: move state, return the new output."""
        self.state = self.next_state(self.state, bit)
        return self.output()

    def run(self, bits):
        """The output after each bit."""
        return [self.step(bit) for bit in bits]


reg = Register(4)
reg.set_input(10)
print(reg.tick())
print(SequenceDetector().run([1, 1, 0, 1, 0, 1, 1, 0, 1, 1]))
'''}],
                "hints": [
                    "Keep `self.d` and `self.q` as separate attributes — `set_d` touches only the first, `tick` copies the first into the second.",
                    "Store the register's flops LSB first, so bit `i` of the word is `(value >> i) & 1` and reading back is `flop.q << i`.",
                    "Write the ten transitions out as a dict keyed by `(state, bit)`; it is easier to check against the pattern than a chain of ifs.",
                    "For a failed match, ask which suffix of the stream is still a prefix of 1011: after `S101` and a 0 the stream ends `...1010`, so the answer is `10`, not the start state.",
                ],
                "tests": [
                    {"name": "A flip-flop is not transparent", "code": r'''
_ff = DFlipFlop()
assert _ff.q == 0, f"a fresh flip-flop starts at 0, got {_ff.q!r}"
_ff.set_d(1)
assert _ff.q == 0, "set_d must not move Q — storage changes only on the clock edge"
assert _ff.tick() == 1, "tick() should copy D into Q and return it"
assert _ff.q == 1, f"after the edge Q is 1, got {_ff.q!r}"
_ff.tick()
assert _ff.q == 1, "with D unchanged, a second edge holds the same value"
'''},
                    {"name": "A flip-flop rejects non-binary values", "code": r'''
try:
    DFlipFlop(2)
    assert False, "DFlipFlop(2) should raise ValueError"
except ValueError:
    pass
try:
    DFlipFlop().set_d(7)
    assert False, "set_d(7) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Two flops in a chain update together", "code": r'''
_a = DFlipFlop(1)
_b = DFlipFlop(0)
_a.set_d(0)
_b.set_d(_a.q)
_a.tick()
_b.tick()
assert (_a.q, _b.q) == (0, 1), \
    f"after one edge the chain should read (0, 1), got {(_a.q, _b.q)!r} — sample before you update"
'''},
                    {"name": "Register loads, reads and holds", "code": r'''
_r = Register(4)
assert _r.read() == 0, f"a fresh register reads 0, got {_r.read()!r}"
_r.set_input(10)
assert _r.read() == 0, "set_input must not change the stored word"
assert _r.tick() == 10, f"tick() should return the newly loaded word, got {_r.tick()!r}"
_r.set_input(5, enable=0)
_r.tick()
assert _r.read() == 10, f"with enable 0 the register holds; got {_r.read()!r}, expected 10"
_r.set_input(5, enable=1)
_r.tick()
assert _r.read() == 5, f"with enable 1 the register loads; got {_r.read()!r}"
assert Register(8, 200).read() == 200, "a register may start with a value"
'''},
                    {"name": "Register widths and ranges are checked", "code": r'''
for _args in [(0,), (4, 16), (4, -1), (-3,)]:
    try:
        Register(*_args)
        assert False, f"Register{_args!r} should raise ValueError"
    except ValueError:
        pass
try:
    Register(4).set_input(16)
    assert False, "set_input(16) on a 4-bit register should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The transition table handles failed matches", "code": r'''
_m = SequenceDetector()
for _state, _bit, _want in [("S0", 0, "S0"), ("S0", 1, "S1"), ("S1", 1, "S1"),
                            ("S1", 0, "S10"), ("S10", 0, "S0"), ("S10", 1, "S101"),
                            ("S101", 0, "S10"), ("S101", 1, "S1011"),
                            ("S1011", 0, "S10"), ("S1011", 1, "S1")]:
    _got = _m.next_state(_state, _bit)
    assert _got == _want, f"next_state({_state!r}, {_bit}) gave {_got!r}, expected {_want!r}"
assert _m.output() == 0, "S0 does not assert the output"
assert SequenceDetector("S1011").output() == 1, "S1011 asserts the output"
try:
    SequenceDetector("S99")
    assert False, "an unknown start state should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The detector finds overlapping patterns", "code": r'''
for _stream in ([1, 1, 0, 1, 0, 1, 1, 0, 1, 1],
                [1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1],
                [0] * 6,
                [1, 0, 1, 1, 1, 0, 1, 1]):
    _want = [1 if _stream[max(0, _i - 3):_i + 1] == [1, 0, 1, 1] else 0
             for _i in range(len(_stream))]
    _got = SequenceDetector().run(_stream)
    assert _got == _want, f"run({_stream!r}) gave {_got!r}, expected {_want!r}"
assert SequenceDetector().run([]) == [], "an empty stream produces no outputs"
try:
    SequenceDetector().step(2)
    assert False, "step(2) should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Two's complement and the ALU",
            "summary": "One adder, several operations, and the four flags that interpret the result.",
            "concepts": [
                "Two's complement: negate by inverting every bit and adding one",
                "The same adder serves signed and unsigned operands — only the flags differ",
                "Subtraction is `a + (~b) + 1`, so one circuit does both",
                "Zero and negative flags read the result; carry and overflow read the operation",
                "Carry is the unsigned out-of-range signal; overflow is the signed one",
                "Overflow for addition: both operands share a sign and the result does not",
                "Logical shifts and their carry-out; why arithmetic right shift differs",
            ],
            "read": [
                {
                    "title": "Negatives on a wheel, and the flags that read an addition",
                    "minutes": 15,
                    "body": r'''
An old mechanical odometer has three digit wheels, so it reads from 000 to 999. Drive
it forward past 999 and it rolls to 000. Now imagine driving it backwards one mile
from 000: the wheels roll to 999. On this odometer, 999 behaves in every respect like
$-1$: add 1 to it and you get 000. There is no minus sign anywhere on the dial.
Whether 999 *means* "nine hundred and ninety-nine" or "one less than zero" is a
decision the driver makes; the wheels do the same thing either way.

An 8-bit register is a wheel with 256 positions, 0 to 255, and the adder from module
2 is the mechanism that turns it. Every result is taken modulo 256: the carry out of
the top bit is the wheel rolling past 255, and the eight bits that remain are where
it stopped.

## Negative numbers without a minus sign

On the 256-position wheel, what should $-x$ be? It should be the word that, added to
$x$, gives 0. Rolling forward $x$ steps and then $256 - x$ more brings the wheel back
to where it started, so $-x$ is $256 - x$. For $x = 1$ that is 255, which is
`11111111`; for $x = 5$ it is 251, `11111011`.

Computing $256 - x$ needs a subtractor, which is what we are trying to avoid. Split
it: $256 - x = (255 - x) + 1$. Now 255 is `11111111`, every bit set, and subtracting
$x$ from it never borrows, because at every bit position you are subtracting a 0 or
a 1 from a 1. Each bit of the result is therefore $1 - x_i$, which is $\overline{x_i}$.
So $255 - x$ is $x$ with every bit inverted, and

$$-x = \overline{x} + 1$$

That is the *two's complement* rule, invert and add one, and it was not announced: it
fell out of writing 256 as $255 + 1$. The inversion costs nothing in gates, and the
$+1$ is a carry-in the adder already has.

```python
for x in (1, 5, 127, 128, 0):
    wheel = (256 - x) % 256
    flipped = ((~x & 0xFF) + 1) % 256
    print(f"x={x:>3}  256-x={wheel:>3}  ~x+1={flipped:>3}  {wheel:08b}")
print(all((256 - x) % 256 == ((~x & 0xFF) + 1) % 256 for x in range(256)))
```

The two columns agree for every $x$, and the last line prints `True` over all 256
words. Two of the rows deserve a look. $x = 0$ gives 256, which on the wheel is 0
again; zero is its own negative, as it should be. And $x = 128$ gives 128: the word
`10000000` is its own negative too, which is the first sign that something at the
halfway point is peculiar.

## Reading a word as signed

If 255 is going to stand for $-1$, then some words must be positive and some
negative, and the split has to be chosen. The convention is that the top bit decides:
words with bit 7 clear, 0 to 127, mean themselves; words with bit 7 set, 128 to 255,
mean themselves minus 256, so 255 is $-1$, 254 is $-2$, and 128 is $-128$. That gives
a range of $-128$ to $127$, with one more negative than positive, because 0 takes one
of the 128 non-negative slots. The word `10000000` is $-128$, and its negative,
$+128$, does not exist in eight bits, which is why it came back as itself above.

```python
def to_signed(value, width):
    if value < 0 or value >= (1 << width):
        raise ValueError(f"{value} is not a {width}-bit word")
    if value >= (1 << (width - 1)):
        return value - (1 << width)
    return value

def from_signed(value, width):
    low, high = -(1 << (width - 1)), (1 << (width - 1)) - 1
    if value < low or value > high:
        raise ValueError(f"{value} does not fit in {width} signed bits")
    return value & ((1 << width) - 1)

for word in (0x00, 0x7F, 0x80, 0xFE, 0xFF):
    print(f"{word:#04x} = {word:>3} unsigned = {to_signed(word, 8):>4} signed")
print(from_signed(-1, 8), from_signed(-128, 8), from_signed(127, 8))
```

`0x7F` is 127 either way, `0x80` is 128 or $-128$, `0xFF` is 255 or $-1$. The same
eight bits, two readings. Nothing in the word records which reading was intended, and
this is the point the rest of the module turns on: the adder does not know either.

## Subtraction is addition with the second operand negated

$a - b$ is $a + (-b)$, and $-b$ is $\overline{b} + 1$, so

$$a - b = a + \overline{b} + 1$$

One adder does both operations. For subtraction the second operand passes through
inverters and the carry-in is set to 1; that is the entire difference in hardware.
Work $5 - 3$ through it in eight bits: $\overline{3}$ is `11111100`, which is 252;
$5 + 252 + 1 = 258$; 258 is `1 00000010`, a carry out of 1 and a result of 2. Now
$3 - 5$: $\overline{5}$ is 250; $3 + 250 + 1 = 254$, which is `0 11111110`: no carry,
and the result `11111110` is 254 unsigned or $-2$ signed. The signed reading is the
answer you wanted, and the unsigned reading is what the wheel shows when you drive
backwards past zero.

```python
def subtract(a, b, width=8):
    mask = (1 << width) - 1
    total = a + (~b & mask) + 1
    result = total & mask
    carry = 1 if total > mask else 0
    return result, carry

for a, b in ((5, 3), (3, 5), (7, 7), (0, 1)):
    result, carry = subtract(a, b)
    print(f"{a} - {b}: result {result:#04x} ({result:>3}), carry {carry}")
```

Look at the carry column: 1 for $5 - 3$, 0 for $3 - 5$, 1 for $7 - 7$, 0 for $0 - 1$.
After a subtraction the carry out is 1 exactly when no borrow was needed, when
$a \geq b$ as unsigned numbers. That is backwards from what the word "carry" suggests,
and it is the convention the lab uses: for `SUB`, a carry of 1 means *no borrow*.
Processor families disagree here; ARM keeps it this way and x86 inverts it into a
borrow flag, so when you move between architectures it is the first thing to check.

## Four flags, two kinds

The ALU hands back a result and four one-bit flags, and it helps to see that they
come in two pairs. **Z** and **N** describe the result word: Z is 1 when it is all
zeros, N is a copy of its top bit, which is the sign under the signed reading. Any
operation can set them, and they are read straight off the output. **C** and **V**
describe *what happened during the operation*, and they answer the same question for
the two readings: did the true answer fit in the word?

C is the unsigned answer. For addition it is the bit that fell off the top:
$255 + 1 = 256$ does not fit in eight bits, the carry is 1, the result is 0. For
subtraction it is the no-borrow signal derived above. Both are "did the wheel roll
past the end".

V is the signed answer, and it needs deriving, because the signed range is not at the
end of the wheel but in the middle. When can $a + b$ leave $-128 \ldots 127$? If $a$
and $b$ have opposite signs, the sum lies between them and cannot leave the range. If
both are non-negative, the sum is at least 0 and overflows only by exceeding 127, and
a sum that exceeds 127 but is under 256 has its top bit set: it *looks negative*. If
both are negative, the sum is at most $-1$, and overflow means going below $-128$,
where the wheel wraps into words whose top bit is clear: it looks non-negative. So
for addition, $V = 1$ exactly when the operands share a sign bit and the result has
the other one.

Trace it: $127 + 1$, or `0x7F + 0x01`, both top bits 0, result `0x80` with top bit 1,
so $V = 1$, and the true sum 128 is indeed out of range. $-1 + 1$, or `0xFF + 0x01`,
one operand negative and one positive, $V = 0$, and the result 0 is correct; but the
carry out is 1, because as unsigned numbers $255 + 1$ rolled the wheel. Same
addition, both flags set the way each reading needs.

For subtraction the sign condition flips, because subtracting $b$ is adding $-b$:
$a - b$ can overflow only when $a$ and $b$ have *different* signs, and it has
overflowed when the result's sign differs from $a$'s. $-128 - 1$, or `0x80 - 0x01`:
signs differ, result `0x7F` has a sign different from $a$'s, $V = 1$; the true answer
$-129$ is out of range. And C? $128 - 1$ needs no borrow, so $C = 1$. Both readings,
both answered.

```python
def add_flags(a, b, width=8):
    mask = (1 << width) - 1
    sign = 1 << (width - 1)
    total = a + b
    result = total & mask
    c = 1 if total > mask else 0
    v = 1 if (~(a ^ b)) & (a ^ result) & sign else 0
    return result, c, v

def to_signed(value, width=8):
    return value - (1 << width) if value >= (1 << (width - 1)) else value

for a, b in ((0x7F, 0x01), (0xFF, 0x01), (0x80, 0x80), (0x40, 0x30)):
    result, c, v = add_flags(a, b)
    print(f"{a:#04x} + {b:#04x} = {result:#04x}  C={c} V={v}")

agree = True
for a in range(256):
    for b in range(256):
        _, c, v = add_flags(a, b)
        unsigned_fits = a + b <= 255
        signed_fits = -128 <= to_signed(a) + to_signed(b) <= 127
        agree = agree and c == (0 if unsigned_fits else 1) and v == (0 if signed_fits else 1)
print(agree)
```

The expression `(~(a ^ b)) & (a ^ result) & sign` is the sentence above written in
bits: `~(a ^ b)` has its top bit set when the operands agree in sign, `a ^ result`
has its top bit set when the result disagrees with $a$, and `& sign` keeps only the
top bit. The loop at the end checks the rule against true arithmetic on all 65,536
pairs and prints `True`, which is the referee again: the flag formula is right
because it agrees with the numbers, not because it was stated. `0x80 + 0x80` is the
row to look at: $-128 + (-128) = -256$, out of the signed range, and also
$128 + 128 = 256$, out of the unsigned range, so both C and V are 1 and the result is
0, so Z is 1 as well. Three flags up on one addition, each answering its own question.

## The mistake, and why it is tempting

The mistake is to read C as "something went wrong" and V as "something went badly
wrong", or to try to decide from the result whether the operands "were" signed. They
were neither. `0xFE` is 254 and it is $-2$; the ALU adds bits, sets C for the
unsigned reading and V for the signed one, and stops. It is the program that knows
which reading it meant, and it reads the matching flag and ignores the other. After
`0xFF + 0x01` the carry is 1, and a program adding unsigned bytes has overflowed,
while a program adding signed bytes has computed $-1 + 1 = 0$ perfectly and does not
care. The temptation is that "carry" sounds like an error and there is a flag right
there to check; the discipline is to ask which reading you are using first.

A second, smaller trap is the shift. `SHL` doubles a word and the bit that falls off
the top is its carry; `SHR` as the lab defines it halves an *unsigned* word, shifting
a 0 in at the top and the old bottom bit out into C. Apply that `SHR` to `0xFE`, which
is $-2$, and you get `0x7F`, which is 127, not $-1$. Halving a signed number needs an
*arithmetic* shift that copies the sign bit into the vacated position, and the lab
does not ask for one; know that the logical shift is the wrong tool for that job.

## Where it stops holding

Every flag rule above is tied to a width. N is bit 7 in an 8-bit ALU and bit 3 in a
4-bit one; the signed range of a 4-bit word is $-8$ to $7$, and `0b0111 + 0b0001`
overflows there while being unremarkable in eight bits. The lab's `ALU(width)` makes
the width a parameter precisely so that `self.sign_bit` and `self.mask` do the right
thing at any width, and the test that runs a 4-bit ALU is there to catch a
hard-coded `0xFF`.

The one-adder story also stops at multiplication and division, which need either
repeated addition or their own hardware, and it stops entirely at floating point,
where a word is a sign, an exponent and a fraction with a different set of rules and
a different set of flags. And in the capstone, the flags become the thing the program
branches on: only the arithmetic and logic operations write them, loads and jumps
leave them alone, which is why a program that needs to test a register writes
`OR R0, R0` before its `JZ`. Z is then a fact about the last ALU operation, not the
last instruction.

## What you are about to build

The lab, *An n-bit ALU with correct flags*, is this reading as one class and two
helpers. `to_signed` and `from_signed` are the two readings of a word, with
`ValueError` at the edges of each range. `ALU.execute` runs seven operations on
masked words: `ADD` and `SUB` set C from the carry out and V from the sign conditions
derived above, the logical operations leave both clear, `SHL` and `SHR` put the
shifted-out bit into C, and every operation sets Z and N from the result. The starter
prints `ADD 0x7F, 0x01` and `SUB 0x03, 0x05`, and the answers you should see are
`(128, {'Z': 0, 'N': 1, 'C': 0, 'V': 1})` and `(254, {'Z': 0, 'N': 1, 'C': 0, 'V': 0})`.
''',
                },
            ],
            "quiz": {
                "title": "Which reading, and which flag",
                "minutes": 8,
                "questions": [
                    {
                        "q": "An 8-bit ALU executes `ADD 0x7F, 0x01`. Which flags come back?",
                        "opts": [
                            "N=1 and V=1, with both Z and C clear",
                            "C=1 and V=1, since the result left both ranges",
                            "N=1 only: 128 fits in a byte",
                            "Z=0, N=0, C=0 and V=0: a small addition sets nothing",
                        ],
                        "a": 0,
                        "whys": [
                            r"The result `0x80` has its top bit set, and two non-negative operands produced a word that reads as negative, which is the signed overflow condition.",
                            r"Nothing fell off the top: 127 + 1 is 128, which fits in eight unsigned bits, so C is 0. Only the signed reading is out of range here.",
                            r"128 fits as an unsigned byte, but the top bit set means the signed reading is $-128$, and two positive numbers summing to a negative one is exactly what V reports.",
                            r"The sum is 128, `0x80`, whose top bit is set, so N is 1; and it was reached from two positive operands, so V is 1. Small operands can still cross the signed boundary.",
                        ],
                        "why": r"""
`0x7F + 0x01` is `0x80`. The top bit of the result is set, so N is 1. Both operands
had their top bit clear and the result has it set, so the signed reading overflowed
and V is 1; the true sum 128 is one past the signed maximum. The unsigned reading,
$127 + 1 = 128$, fits with room to spare, so C is 0, and the result is not zero, so Z
is 0. This is the row where C and V part company, and it is the first worked example
in the lab brief.
""",
                    },
                    {
                        "q": "After `SUB 0x03, 0x05` the ALU reports C=0. What does that tell a program working in unsigned bytes?",
                        "opts": [
                            "A borrow was needed: 3 is smaller than 5, so the true difference is negative and the word wrapped",
                            "The subtraction was exact and no bit was lost anywhere, so `0xFE` is the correct unsigned difference",
                            "Nothing: the carry flag is only meaningful after an addition, and SUB leaves it clear",
                            "The result should be read as signed instead, since its top bit came out set",
                        ],
                        "a": 0,
                        "whys": [
                            r"Subtraction runs as $a + \overline{b} + 1$, and the carry out of that addition is 1 exactly when $a \geq b$; here it is 0, so the wheel rolled backwards past zero.",
                            r"`0xFE` is what the wheel shows, but 254 is not 3 minus 5. C=0 after a SUB is the signal that the unsigned answer does not exist, which is the opposite of exact.",
                            r"SUB sets C from the carry out of $a + \overline{b} + 1$, and the lab's tests check it on every subtraction. It carries real information: 1 for no borrow, 0 for a borrow.",
                            r"The ALU has no opinion about which reading a program uses. A program working in unsigned bytes reads C, learns that the answer went below zero, and decides what to do; the signed reading is somebody else's concern.",
                        ],
                        "why": r"""
The ALU computes `SUB` as $a + \overline{b} + 1$, and the carry out of that addition
is 1 exactly when $a \geq b$ as unsigned numbers. For $3 - 5$ the total is 254, which
does not reach 256, so C is 0: a borrow was needed and the unsigned difference does
not exist. The word `0xFE` is what the wheel shows after rolling backwards past
zero. That convention, carry set means no borrow, is the lab's and ARM's; the flag is
meaningful after every SUB, and which reading to apply is the program's decision, not
the ALU's.
""",
                    },
                    {
                        "q": "`0xFF + 0x01` gives result `0x00` with C=1 and V=0. Which description fits?",
                        "opts": [
                            "As unsigned bytes 255 + 1 overflowed; as signed bytes $-1 + 1 = 0$ is exact",
                            "The addition overflowed in both readings, since the result is smaller than either operand",
                            "The addition was exact in both readings, and C=1 records only that the result is zero",
                            "As signed bytes it overflowed; as unsigned bytes it wrapped correctly",
                        ],
                        "a": 0,
                        "whys": [
                            r"C answers the unsigned question and V answers the signed one; here they differ because the same bits are 255 and $-1$.",
                            r"A result smaller than an operand is the unsigned overflow signal, and C reports it. But in the signed reading the operands have opposite signs, and a sum of two numbers with opposite signs can never leave the range, which is why V is 0.",
                            r"C is not a zero flag; Z is. C=1 says a bit fell off the top, which means the unsigned sum 256 did not fit. The signed sum 0 did fit, and that is what V=0 says.",
                            r"Backwards on both counts. The wrap is the unsigned overflow, and C reports it; the signed sum $-1 + 1 = 0$ is exact, and V=0 reports that. Each flag belongs to one reading.",
                        ],
                        "why": r"""
The same addition is two different sums depending on the reading. As unsigned bytes
it is $255 + 1 = 256$, which does not fit, and the carry out of 1 says so. As signed
bytes it is $-1 + 1 = 0$, which fits comfortably; the operands have opposite signs,
so the sum lies between them and V is 0. Neither flag is a zero flag, and neither
tells the program which reading to use. A program adding unsigned bytes has
overflowed; a program adding signed bytes has the right answer and ignores C.
""",
                    },
                    {
                        "q": "Why does the overflow rule for addition depend on whether the two operands share a sign?",
                        "opts": [
                            "Two numbers of opposite sign sum to a value between them, which cannot leave the range",
                            "The signed range is symmetric about zero, so opposite signs always cancel to a small value",
                            "V is derived from the carry out, and only two like-signed operands can produce a carry",
                            "Two operands of the same sign always overflow, and the rule exists to catch that case",
                        ],
                        "a": 0,
                        "whys": [
                            r"If one operand is negative and the other is not, the sum is at least the smaller and at most the larger, so it stays in range; overflow needs both to push the same way.",
                            r"The range is not symmetric: it runs from $-128$ to $127$. And opposite signs do not cancel to something small; $-100 + 1$ is $-99$. What they do is stay between the operands, which is enough.",
                            r"V is not the carry out; the carry out is C. `0xFF + 0x01` has a carry and no overflow, and `0x7F + 0x01` has an overflow and no carry. Unlike-signed operands produce a carry whenever their sum is non-negative, as `0xFF + 0x01` shows.",
                            r"Like-signed operands overflow only when the sum passes the boundary: $1 + 1$ shares a sign and is fine. The rule adds a second condition, that the result's sign differs from the operands', to tell those cases apart.",
                        ],
                        "why": r"""
When the operands have opposite signs the sum lies between them, so it cannot leave
a range that contains both. Overflow is therefore possible only when both push the
same way, and it has happened only if the sum crossed the boundary, which shows up
as a result whose sign differs from the operands'. Both conditions are needed:
$1 + 1$ shares a sign and does not overflow. V is a separate flag from C, and the two
disagree on `0xFF + 0x01` and on `0x7F + 0x01`, so neither can be derived from the
other, and the signed range is not symmetric in any case.
""",
                    },
                    {
                        "q": "`SHR 0xFE` in the lab's ALU returns `0x7F`. If `0xFE` was meant as $-2$, what has gone wrong?",
                        "opts": [
                            "Nothing: a logical shift halves unsigned words, and halving a signed one needs the sign bit copied in at the top",
                            "The ALU should have produced `0xFF`, and the logical shift has mishandled the bit that was shifted out of the bottom",
                            "The word was negative, so the ALU should have refused it with a `ValueError` rather than shifting it",
                            "The shift should have set V, because the operation changed the sign of a signed word",
                        ],
                        "a": 0,
                        "whys": [
                            r"The lab's `SHR` shifts a 0 into the top; that is right for 254 becoming 127, and wrong for $-2$, which needs an arithmetic shift the lab does not define.",
                            r"`0xFF` is the right answer for a signed halving, but only an arithmetic shift produces it. The logical shift did what it defines, and the shifted-out bit went into C correctly; the mismatch is between the operation and the reading.",
                            r"The ALU cannot know the word was negative; `0xFE` is also 254. Operand checks are about width, not sign, and 254 is a valid 8-bit word.",
                            r"V is written only by ADD and SUB. A shift changing the top bit is an ordinary consequence of a logical shift on unsigned words, not a signed overflow.",
                        ],
                        "why": r"""
The ALU's `SHR` is a logical shift: it moves every bit down one place, shifts a 0
into the top and drops the old bottom bit into C. On 254 that gives 127, which is
correct for an unsigned halving. Read the same word as $-2$ and 127 is nonsense, but
the ALU never knew the word was signed; halving a signed number needs an arithmetic
shift that copies the sign bit into the vacated position, and the lab deliberately
does not ask for one. Nothing is refused, because `0xFE` is a valid word, and V
belongs to ADD and SUB alone.
""",
                    },
                    {
                        "q": "`to_signed(128, 8)` returns $-128$, but `from_signed(128, 8)` raises `ValueError`. Why the asymmetry?",
                        "opts": [
                            "128 is a valid 8-bit word, read as $-128$, but it is not a value the 8-bit signed range can hold",
                            "The two functions disagree, and one of them has an off-by-one error in its range check",
                            "`to_signed` should also raise, since a word with its top bit set is not a valid input for it either",
                            "`from_signed` is stricter because a negative number needs one extra bit for its sign",
                        ],
                        "a": 0,
                        "whys": [
                            r"The two functions check different ranges: a word is 0 to 255, a signed value is $-128$ to 127, and 128 is in the first and not the second.",
                            r"Both checks are right. `to_signed` accepts any of the 256 words, and `from_signed` accepts any of the 256 signed values; 128 happens to be a word and not a signed value.",
                            r"Words with the top bit set are exactly the ones `to_signed` exists for; refusing them would leave it unable to read any negative number.",
                            r"No extra bit is involved: eight bits hold 256 values in either reading. The sign costs nothing beyond the choice of where to split the wheel, which leaves 128 on the far side.",
                        ],
                        "why": r"""
`to_signed` takes a word, and every value from 0 to 255 is a word; 128 is `10000000`,
which the signed convention reads as $-128$. `from_signed` takes a signed value, and
the signed range of eight bits is $-128$ to 127; there is no word for $+128$, because
the wheel's 256 positions are already spoken for. The functions are inverses on the
values they share and each refuses what lies outside its own domain; no bit is added
or lost, and neither check is off by one.
""",
                    },
                ],
            },
            "lab": {
                "title": "An n-bit ALU with correct flags",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Build the arithmetic-logic unit that the capstone datapath will use.

## Helpers

**`to_signed(value, width)`** — read an unsigned word as two's complement.
**`from_signed(value, width)`** — the reverse, producing the raw word.
Both raise `ValueError` for a value outside the representable range.

```text
to_signed(0xFF, 8)   -> -1
to_signed(0x80, 8)   -> -128
from_signed(-1, 8)   ->  255
from_signed(-128, 8) ->  128
from_signed(128, 8)  ->  ValueError
```

## `ALU(width=8)`

`execute(op, a, b=0)` returns `(result, flags)`. `op` is one of `"ADD"`,
`"SUB"`, `"AND"`, `"OR"`, `"XOR"`, `"SHL"`, `"SHR"` — anything else is a
`ValueError`, as is an operand outside `0 .. 2**width - 1`. `result` is always
masked back down to `width` bits.

`flags` is a dict with exactly the keys `"Z"`, `"N"`, `"C"`, `"V"`, each 0 or 1:

- **Z** — the result is zero.
- **N** — the top bit of the result is set (negative when read as signed).
- **C** — carry out. For `ADD` it is the bit that fell off the top. For `SUB`
  it is the carry out of `a + (~b & mask) + 1`, so **1 means no borrow**. For
  `SHL` it is the bit shifted out of the top, for `SHR` the bit shifted out of
  the bottom, and for the logical operations it is 0.
- **V** — signed overflow. Nonzero only for `ADD` and `SUB`. For addition it is
  set when both operands have the same sign bit and the result does not; for
  subtraction, when the operands differ in sign and the result differs from `a`.

Worked examples for `width=8`:

```text
ADD 0x7F, 0x01  ->  0x80  Z=0 N=1 C=0 V=1     127 + 1 overflows signed
ADD 0xFF, 0x01  ->  0x00  Z=1 N=0 C=1 V=0      -1 + 1 is fine, unsigned wraps
SUB 0x05, 0x03  ->  0x02  Z=0 N=0 C=1 V=0     no borrow
SUB 0x03, 0x05  ->  0xFE  Z=0 N=1 C=0 V=0     borrow; the answer is -2
SUB 0x80, 0x01  ->  0x7F  Z=0 N=0 C=1 V=1    -128 - 1 overflows signed
SHL 0x80        ->  0x00  Z=1 N=0 C=1 V=0
SHR 0x01        ->  0x00  Z=1 N=0 C=1 V=0
```

`width` is a constructor argument, so the same class is a 4-bit or a 16-bit
ALU. Write the masks in terms of `self.width`; do not hard-code `0xFF`.
''',
                "files": [{"name": "main.py", "content": r'''
def to_signed(value, width):
    """Read an unsigned word as two's complement."""
    # your code here


def from_signed(value, width):
    """Turn a signed integer into its raw width-bit word."""
    # your code here


class ALU:
    """An n-bit arithmetic-logic unit with Z, N, C and V flags."""

    OPS = ("ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR")

    def __init__(self, width=8):
        self.width = width
        self.mask = (1 << width) - 1
        self.sign_bit = 1 << (width - 1)

    def execute(self, op, a, b=0):
        """(result, {"Z": .., "N": .., "C": .., "V": ..})."""
        # your code here


alu = ALU(8)
print(alu.execute("ADD", 0x7F, 0x01))
print(alu.execute("SUB", 0x03, 0x05))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def to_signed(value, width):
    """Read an unsigned word as two's complement."""
    if width < 1:
        raise ValueError("width must be at least 1")
    if value < 0 or value >= (1 << width):
        raise ValueError(f"{value} is not a {width}-bit word")
    if value >= (1 << (width - 1)):
        return value - (1 << width)
    return value


def from_signed(value, width):
    """Turn a signed integer into its raw width-bit word."""
    if width < 1:
        raise ValueError("width must be at least 1")
    low = -(1 << (width - 1))
    high = (1 << (width - 1)) - 1
    if value < low or value > high:
        raise ValueError(f"{value} is not representable in {width} signed bits")
    return value & ((1 << width) - 1)


class ALU:
    """An n-bit arithmetic-logic unit with Z, N, C and V flags."""

    OPS = ("ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR")

    def __init__(self, width=8):
        self.width = width
        self.mask = (1 << width) - 1
        self.sign_bit = 1 << (width - 1)

    def execute(self, op, a, b=0):
        """(result, {"Z": .., "N": .., "C": .., "V": ..})."""
        if op not in self.OPS:
            raise ValueError(f"unknown operation {op!r}")
        for operand in (a, b):
            if operand < 0 or operand > self.mask:
                raise ValueError(f"{operand} is not a {self.width}-bit word")

        carry = 0
        overflow = 0
        if op == "ADD":
            total = a + b
            result = total & self.mask
            carry = 1 if total > self.mask else 0
            overflow = 1 if (~(a ^ b)) & (a ^ result) & self.sign_bit else 0
        elif op == "SUB":
            total = a + (~b & self.mask) + 1
            result = total & self.mask
            carry = 1 if total > self.mask else 0
            overflow = 1 if (a ^ b) & (a ^ result) & self.sign_bit else 0
        elif op == "AND":
            result = a & b
        elif op == "OR":
            result = a | b
        elif op == "XOR":
            result = a ^ b
        elif op == "SHL":
            result = (a << 1) & self.mask
            carry = 1 if a & self.sign_bit else 0
        else:
            result = a >> 1
            carry = a & 1

        flags = {
            "Z": 1 if result == 0 else 0,
            "N": 1 if result & self.sign_bit else 0,
            "C": carry,
            "V": overflow,
        }
        return result, flags


alu = ALU(8)
print(alu.execute("ADD", 0x7F, 0x01))
print(alu.execute("SUB", 0x03, 0x05))
'''}],
                "hints": [
                    "`to_signed` only has to subtract `1 << width` when the sign bit is set; everything below that is already the right number.",
                    "Do subtraction the way the hardware does: `total = a + (~b & self.mask) + 1`. The carry flag is then simply whether `total` exceeded the mask.",
                    "Signed overflow for ADD is `(~(a ^ b)) & (a ^ result) & self.sign_bit` — 'the operands agreed on sign and the result disagreed'. For SUB, drop the outer complement: `(a ^ b) & (a ^ result) & self.sign_bit`.",
                    "Set Z and N once at the end from `result`; only C and V depend on which operation ran.",
                ],
                "tests": [
                    {"name": "to_signed / from_signed", "code": r'''
for _v, _want in [(0, 0), (127, 127), (128, -128), (255, -1), (1, 1)]:
    _got = to_signed(_v, 8)
    assert _got == _want, f"to_signed({_v}, 8) gave {_got!r}, expected {_want}"
for _v, _want in [(0, 0), (-1, 255), (-128, 128), (127, 127)]:
    _got = from_signed(_v, 8)
    assert _got == _want, f"from_signed({_v}, 8) gave {_got!r}, expected {_want}"
assert to_signed(8, 4) == -8, f"to_signed(8, 4) gave {to_signed(8, 4)!r}, expected -8"
for _v in range(256):
    assert from_signed(to_signed(_v, 8), 8) == _v, f"round-trip failed for {_v}"
for _args in [(256, 8), (-1, 8)]:
    try:
        to_signed(*_args)
        assert False, f"to_signed{_args!r} should raise ValueError"
    except ValueError:
        pass
for _args in [(128, 8), (-129, 8)]:
    try:
        from_signed(*_args)
        assert False, f"from_signed{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Logical operations and their flags", "code": r'''
_alu = ALU(8)
for _op, _a, _b, _want in [("AND", 0xF0, 0x3C, 0x30), ("OR", 0xF0, 0x0F, 0xFF),
                           ("XOR", 0xFF, 0x0F, 0xF0), ("AND", 0x0F, 0xF0, 0x00)]:
    _r, _f = _alu.execute(_op, _a, _b)
    assert _r == _want, f"{_op} {_a:#04x}, {_b:#04x} gave {_r:#04x}, expected {_want:#04x}"
    assert _f["C"] == 0 and _f["V"] == 0, f"{_op} must leave C and V clear, got {_f!r}"
_r, _f = _alu.execute("OR", 0xF0, 0x0F)
assert _f == {"Z": 0, "N": 1, "C": 0, "V": 0}, f"OR 0xF0, 0x0F flags were {_f!r}"
_r, _f = _alu.execute("AND", 0x0F, 0xF0)
assert _f == {"Z": 1, "N": 0, "C": 0, "V": 0}, f"AND 0x0F, 0xF0 flags were {_f!r}"
'''},
                    {"name": "ADD, with carry and overflow", "code": r'''
_alu = ALU(8)
for _a, _b, _wr, _wf in [
        (0x7F, 0x01, 0x80, {"Z": 0, "N": 1, "C": 0, "V": 1}),
        (0xFF, 0x01, 0x00, {"Z": 1, "N": 0, "C": 1, "V": 0}),
        (0x01, 0x02, 0x03, {"Z": 0, "N": 0, "C": 0, "V": 0}),
        (0x80, 0x80, 0x00, {"Z": 1, "N": 0, "C": 1, "V": 1}),
        (0x00, 0x00, 0x00, {"Z": 1, "N": 0, "C": 0, "V": 0})]:
    _r, _f = _alu.execute("ADD", _a, _b)
    assert _r == _wr, f"ADD {_a:#04x}, {_b:#04x} gave {_r:#04x}, expected {_wr:#04x}"
    assert _f == _wf, f"ADD {_a:#04x}, {_b:#04x} flags were {_f!r}, expected {_wf!r}"
'''},
                    {"name": "SUB, with borrow and overflow", "code": r'''
_alu = ALU(8)
for _a, _b, _wr, _wf in [
        (0x05, 0x03, 0x02, {"Z": 0, "N": 0, "C": 1, "V": 0}),
        (0x03, 0x05, 0xFE, {"Z": 0, "N": 1, "C": 0, "V": 0}),
        (0x80, 0x01, 0x7F, {"Z": 0, "N": 0, "C": 1, "V": 1}),
        (0x07, 0x07, 0x00, {"Z": 1, "N": 0, "C": 1, "V": 0}),
        (0x00, 0x01, 0xFF, {"Z": 0, "N": 1, "C": 0, "V": 0})]:
    _r, _f = _alu.execute("SUB", _a, _b)
    assert _r == _wr, f"SUB {_a:#04x}, {_b:#04x} gave {_r:#04x}, expected {_wr:#04x}"
    assert _f == _wf, f"SUB {_a:#04x}, {_b:#04x} flags were {_f!r}, expected {_wf!r}"
'''},
                    {"name": "Shifts and their carry-out", "code": r'''
_alu = ALU(8)
for _op, _a, _wr, _wc in [("SHL", 0x01, 0x02, 0), ("SHL", 0x80, 0x00, 1),
                          ("SHL", 0xC0, 0x80, 1), ("SHR", 0x01, 0x00, 1),
                          ("SHR", 0xFF, 0x7F, 1), ("SHR", 0x02, 0x01, 0)]:
    _r, _f = _alu.execute(_op, _a)
    assert _r == _wr, f"{_op} {_a:#04x} gave {_r:#04x}, expected {_wr:#04x}"
    assert _f["C"] == _wc, f"{_op} {_a:#04x} gave C={_f['C']}, expected {_wc}"
    assert _f["V"] == 0, f"{_op} must leave V clear, got {_f!r}"
_r, _f = _alu.execute("SHL", 0x40)
assert (_r, _f["N"]) == (0x80, 1), f"SHL 0x40 gave {(_r, _f['N'])!r}, expected (128, 1)"
'''},
                    {"name": "ADD and SUB agree with plain arithmetic", "code": r'''
_alu = ALU(8)
for _a in range(0, 256, 7):
    for _b in range(0, 256, 5):
        _r, _f = _alu.execute("ADD", _a, _b)
        assert _r == (_a + _b) & 0xFF, f"ADD {_a}, {_b} gave {_r}, expected {(_a + _b) & 0xFF}"
        assert _f["C"] == (1 if _a + _b > 255 else 0), f"ADD {_a}, {_b} carry was {_f['C']}"
        _signed = to_signed(_a, 8) + to_signed(_b, 8)
        _wantv = 0 if -128 <= _signed <= 127 else 1
        assert _f["V"] == _wantv, f"ADD {_a}, {_b} gave V={_f['V']}, expected {_wantv}"
        _r, _f = _alu.execute("SUB", _a, _b)
        assert _r == (_a - _b) & 0xFF, f"SUB {_a}, {_b} gave {_r}, expected {(_a - _b) & 0xFF}"
        assert _f["C"] == (1 if _a >= _b else 0), f"SUB {_a}, {_b} carry was {_f['C']}"
        _signed = to_signed(_a, 8) - to_signed(_b, 8)
        _wantv = 0 if -128 <= _signed <= 127 else 1
        assert _f["V"] == _wantv, f"SUB {_a}, {_b} gave V={_f['V']}, expected {_wantv}"
'''},
                    {"name": "Bad operations and operands are refused", "code": r'''
_alu = ALU(8)
for _args in [("MUL", 1, 2), ("add", 1, 2), ("ADD", 256, 0), ("ADD", 0, -1)]:
    try:
        _alu.execute(*_args)
        assert False, f"execute{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The same class works at other widths", "code": r'''
_alu4 = ALU(4)
_r, _f = _alu4.execute("ADD", 0b1111, 0b0001)
assert (_r, _f) == (0, {"Z": 1, "N": 0, "C": 1, "V": 0}), \
    f"4-bit ADD 15, 1 gave {(_r, _f)!r}, expected (0, Z=1 C=1)"
_r, _f = _alu4.execute("ADD", 0b0111, 0b0001)
assert (_r, _f["V"], _f["N"]) == (8, 1, 1), \
    f"4-bit ADD 7, 1 gave {(_r, _f['V'], _f['N'])!r}, expected (8, 1, 1)"
_r, _f = _alu4.execute("SHL", 0b1000)
assert (_r, _f["C"], _f["Z"]) == (0, 1, 1), f"4-bit SHL 8 gave {(_r, _f['C'], _f['Z'])!r}"
try:
    _alu4.execute("ADD", 16, 0)
    assert False, "16 is not a 4-bit word"
except ValueError:
    pass
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an 8-bit datapath simulator",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Put the four labs together into a machine that executes instructions.
`datapath.py` holds the hardware and is what the checks import; `main.py` is a
demo that loads a program and runs it.

## Memory and encoding

256 bytes of memory, byte-addressed. Every instruction is **two bytes**:

```text
byte 0:  opcode (4 bits) | rd (2 bits) | rs (2 bits)
byte 1:  operand — an immediate or an address
```

The sixteen opcodes are already named as module constants:

```text
0 NOP                 8  XOR rd, rs
1 LDI rd, imm         9  SHL rd
2 LD  rd, addr        10 SHR rd
3 ST  rs, addr        11 JMP addr
4 ADD rd, rs          12 JZ  addr     (taken when the Z flag is set)
5 SUB rd, rs          13 JNZ addr
6 AND rd, rs          14 MOV rd, rs
7 OR  rd, rs          15 HLT
```

`encode(op, rd=0, rs=0, operand=0)` returns the two bytes and raises
`ValueError` for a field that will not fit. `decode(byte0, byte1)` returns
`(op, rd, rs, operand)`. `assemble(instructions)` flattens a list of tuples into
a flat list of bytes, padding short tuples with zeros.

## `RegisterFile(count=4, width=8)`

`read(index)` and `write(index, value)`. Writes are masked to `width` bits;
an index outside `0 .. count - 1` is a `ValueError`.

## `ALU(width=8)`

Exactly the unit from module 4: `execute(op, a, b=0) -> (result, flags)` with
`"Z"`, `"N"`, `"C"`, `"V"`.

## `CPU(program=None, start=0)`

A Moore control FSM over the states `"FETCH"`, `"DECODE"`, `"EXECUTE"` and
`"HALTED"`, plus `pc`, `mem`, `regs`, `flags` and the instruction register `ir`.

- `load_program(program, start=0)` — assemble and write the bytes into memory.
  `ValueError` if the program does not fit.
- `tick()` — advance **one** control state and return the new state.
  - FETCH: latch `mem[pc]` and `mem[pc + 1]` into `ir`, advance `pc` by 2
    (wrapping at 256), go to DECODE.
  - DECODE: split `ir` into `op`, `rd`, `rs`, `operand`, go to EXECUTE.
  - EXECUTE: perform the operation, then go back to FETCH — or to HALTED
    for `HLT`. A tick in HALTED does nothing.
- `step()` — tick until the machine is back in FETCH or has HALTED.
- `run(max_steps=10000)` — step until HALTED, returning the number of
  instructions executed. Raise `RuntimeError` if the limit is reached first:
  a simulator that hangs the browser tab is not a simulator.

Only ADD, SUB, AND, OR, XOR, SHL and SHR touch `flags`; loads, stores, moves
and jumps leave them alone, which is what makes `OR rd, rd` a useful way to
test a register before a branch.

## The micro-program

Finish `SUM_PROGRAM`: it must read `n` from address `0x40`, compute
`n + (n-1) + ... + 1` and store the total at `0x41`, then halt. Remember that
jump targets are **byte** addresses, so instruction `k` sits at address `2 * k`.
The sketch below is one correct shape; the loop needs a flag-setting
instruction before its branch.

```text
addr 0   LD  R0, 0x40      R0 = n
addr 2   LDI R1, 0         R1 = running total
addr 4   LDI R3, 1         R3 = the constant 1
addr 6   OR  R0, R0        set Z from R0 without changing it
addr 8   JZ  16            n reached zero, go and store
addr 10  ADD R1, R0        total += n
addr 12  SUB R0, R3        n -= 1
addr 14  JMP 6             back to the test
addr 16  ST  R1, 0x41      store the total
addr 18  HLT
```
''',
        "deliverables": [
            "`datapath.py` — `encode`/`decode`/`assemble`, `RegisterFile`, `ALU` and `CPU`, importable with no side effects",
            "A control FSM whose `tick()` exposes FETCH, DECODE, EXECUTE and HALTED as separate observable states",
            "All sixteen opcodes implemented, with flags updated only by the arithmetic and logic operations",
            "`SUM_PROGRAM` — a working micro-program that reads `n` from 0x40 and leaves the triangular number at 0x41",
            "`main.py` — a demo that loads the program for a couple of values of `n` and prints the results",
            "Termination safety: `run()` raises `RuntimeError` rather than looping forever",
        ],
        "constraints": [
            "Standard library only, and no imports are needed at all",
            "`datapath.py` must define constants, classes and functions only — running it prints nothing",
            "Memory is exactly 256 bytes and every stored value stays in `0 .. 255`",
            "The program counter wraps at 256 rather than running off the end of memory",
            "Two `CPU()` objects must not share memory or registers",
        ],
        "rubric": [
            {"criterion": "Instruction set correctness", "weight": 35,
             "evidence": "Every opcode moves the right data, and encode/decode round-trip for all valid field combinations."},
            {"criterion": "Control FSM", "weight": 20,
             "evidence": "tick() exposes the three-phase cycle, HLT parks the machine, and step()/run() are built on tick() rather than duplicating it."},
            {"criterion": "Flags and branching", "weight": 20,
             "evidence": "Z, N, C and V follow the module 4 rules, only arithmetic and logic write them, and JZ/JNZ branch on the latched Z."},
            {"criterion": "Micro-program", "weight": 15,
             "evidence": "SUM_PROGRAM returns the correct total for n = 0, 1 and larger values, using byte addresses for its jump targets."},
            {"criterion": "Robustness and readability", "weight": 10,
             "evidence": "Bad opcodes, registers and addresses raise ValueError; run() refuses to hang; every public method carries a docstring."},
        ],
        "hints": [
            "Write `encode` and `decode` first and test them against each other — every later bug looks like an encoding bug until you rule it out.",
            "Keep `tick()` as a single `if`/`elif` over `self.state`; `step()` should then be nothing but `while True: self.tick()` with a stop condition.",
            "Dispatch the opcode inside EXECUTE from a plain chain of comparisons against the module constants, and map the arithmetic opcodes to their ALU operation names with one dict.",
            "The jump instructions assign to `self.pc` *after* FETCH has already advanced it, so the branch simply overwrites the sequential address.",
            "In `SUM_PROGRAM`, remember that `SUB R0, R3` sets Z but `JMP` does not — the `OR R0, R0` at the top of the loop is what makes the test at address 8 meaningful.",
        ],
        "files": [
            {"name": "datapath.py", "content": r'''
NOP, LDI, LD, ST, ADD, SUB, AND, OR, XOR, SHL, SHR, JMP, JZ, JNZ, MOV, HLT = range(16)

OPNAMES = {
    NOP: "NOP", LDI: "LDI", LD: "LD", ST: "ST", ADD: "ADD", SUB: "SUB",
    AND: "AND", OR: "OR", XOR: "XOR", SHL: "SHL", SHR: "SHR", JMP: "JMP",
    JZ: "JZ", JNZ: "JNZ", MOV: "MOV", HLT: "HLT",
}

MEM_SIZE = 256


def encode(op, rd=0, rs=0, operand=0):
    """(byte0, byte1) for one instruction. ValueError on a field that will not fit."""
    # your code here


def decode(byte0, byte1):
    """(op, rd, rs, operand)."""
    # your code here


def assemble(instructions):
    """A list of (op, rd, rs, operand) tuples as a flat list of bytes."""
    # your code here


class RegisterFile:
    """A small bank of width-bit registers."""

    def __init__(self, count=4, width=8):
        # your code here
        pass

    def read(self, index):
        """The value in register `index`."""
        # your code here

    def write(self, index, value):
        """Store `value`, masked to the register width."""
        # your code here


class ALU:
    """The unit from module 4, reused unchanged."""

    OPS = ("ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR")

    def __init__(self, width=8):
        self.width = width
        self.mask = (1 << width) - 1
        self.sign_bit = 1 << (width - 1)

    def execute(self, op, a, b=0):
        """(result, {"Z": .., "N": .., "C": .., "V": ..})."""
        # your code here


class CPU:
    """Memory, registers, an ALU and a three-phase control FSM."""

    STATES = ("FETCH", "DECODE", "EXECUTE", "HALTED")

    def __init__(self, program=None, start=0):
        # your code here
        pass

    def load_program(self, program, start=0):
        """Assemble the instructions into memory at `start`."""
        # your code here

    def tick(self):
        """Advance one control state and return the new state."""
        # your code here

    def step(self):
        """Run one whole instruction."""
        # your code here

    def run(self, max_steps=10000):
        """Step until HALTED; RuntimeError if the machine will not stop."""
        # your code here


# n at 0x40, the sum 1..n at 0x41. Finish it.
SUM_PROGRAM = [
    (LD, 0, 0, 0x40),
    (LDI, 1, 0, 0),
]
'''},
            {"name": "main.py", "content": r'''
from datapath import CPU, SUM_PROGRAM

for n in (0, 1, 5, 10):
    cpu = CPU(SUM_PROGRAM)
    cpu.mem[0x40] = n
    steps = cpu.run()
    print(f"n={n:>3}  sum={cpu.mem[0x41]:>3}  instructions={steps}")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "datapath.py", "content": r'''
NOP, LDI, LD, ST, ADD, SUB, AND, OR, XOR, SHL, SHR, JMP, JZ, JNZ, MOV, HLT = range(16)

OPNAMES = {
    NOP: "NOP", LDI: "LDI", LD: "LD", ST: "ST", ADD: "ADD", SUB: "SUB",
    AND: "AND", OR: "OR", XOR: "XOR", SHL: "SHL", SHR: "SHR", JMP: "JMP",
    JZ: "JZ", JNZ: "JNZ", MOV: "MOV", HLT: "HLT",
}

MEM_SIZE = 256

ALU_OP = {ADD: "ADD", SUB: "SUB", AND: "AND", OR: "OR", XOR: "XOR",
          SHL: "SHL", SHR: "SHR"}


def encode(op, rd=0, rs=0, operand=0):
    """(byte0, byte1) for one instruction. ValueError on a field that will not fit."""
    if not 0 <= op <= 15:
        raise ValueError(f"opcode {op} does not fit in 4 bits")
    if not 0 <= rd <= 3:
        raise ValueError(f"no register R{rd}")
    if not 0 <= rs <= 3:
        raise ValueError(f"no register R{rs}")
    if not 0 <= operand <= 255:
        raise ValueError(f"operand {operand} does not fit in a byte")
    return (op << 4) | (rd << 2) | rs, operand


def decode(byte0, byte1):
    """(op, rd, rs, operand)."""
    return byte0 >> 4, (byte0 >> 2) & 3, byte0 & 3, byte1


def assemble(instructions):
    """A list of (op, rd, rs, operand) tuples as a flat list of bytes."""
    out = []
    for instruction in instructions:
        fields = tuple(instruction) + (0,) * (4 - len(instruction))
        byte0, byte1 = encode(*fields)
        out.append(byte0)
        out.append(byte1)
    return out


class RegisterFile:
    """A small bank of width-bit registers."""

    def __init__(self, count=4, width=8):
        self.count = count
        self.width = width
        self.mask = (1 << width) - 1
        self.values = [0] * count

    def _check(self, index):
        if not 0 <= index < self.count:
            raise ValueError(f"no register R{index}")

    def read(self, index):
        """The value in register `index`."""
        self._check(index)
        return self.values[index]

    def write(self, index, value):
        """Store `value`, masked to the register width."""
        self._check(index)
        self.values[index] = value & self.mask


class ALU:
    """The unit from module 4, reused unchanged."""

    OPS = ("ADD", "SUB", "AND", "OR", "XOR", "SHL", "SHR")

    def __init__(self, width=8):
        self.width = width
        self.mask = (1 << width) - 1
        self.sign_bit = 1 << (width - 1)

    def execute(self, op, a, b=0):
        """(result, {"Z": .., "N": .., "C": .., "V": ..})."""
        if op not in self.OPS:
            raise ValueError(f"unknown operation {op!r}")
        for operand in (a, b):
            if operand < 0 or operand > self.mask:
                raise ValueError(f"{operand} is not a {self.width}-bit word")

        carry = 0
        overflow = 0
        if op == "ADD":
            total = a + b
            result = total & self.mask
            carry = 1 if total > self.mask else 0
            overflow = 1 if (~(a ^ b)) & (a ^ result) & self.sign_bit else 0
        elif op == "SUB":
            total = a + (~b & self.mask) + 1
            result = total & self.mask
            carry = 1 if total > self.mask else 0
            overflow = 1 if (a ^ b) & (a ^ result) & self.sign_bit else 0
        elif op == "AND":
            result = a & b
        elif op == "OR":
            result = a | b
        elif op == "XOR":
            result = a ^ b
        elif op == "SHL":
            result = (a << 1) & self.mask
            carry = 1 if a & self.sign_bit else 0
        else:
            result = a >> 1
            carry = a & 1

        return result, {
            "Z": 1 if result == 0 else 0,
            "N": 1 if result & self.sign_bit else 0,
            "C": carry,
            "V": overflow,
        }


class CPU:
    """Memory, registers, an ALU and a three-phase control FSM."""

    STATES = ("FETCH", "DECODE", "EXECUTE", "HALTED")

    def __init__(self, program=None, start=0):
        self.mem = [0] * MEM_SIZE
        self.regs = RegisterFile(4, 8)
        self.alu = ALU(8)
        self.flags = {"Z": 0, "N": 0, "C": 0, "V": 0}
        self.pc = start
        self.state = "FETCH"
        self.ir = (0, 0)
        self.op = NOP
        self.rd = 0
        self.rs = 0
        self.operand = 0
        if program:
            self.load_program(program, start)

    def load_program(self, program, start=0):
        """Assemble the instructions into memory at `start`."""
        code = assemble(program)
        if start < 0 or start + len(code) > MEM_SIZE:
            raise ValueError("the program does not fit in memory")
        for offset, byte in enumerate(code):
            self.mem[start + offset] = byte

    def tick(self):
        """Advance one control state and return the new state."""
        if self.state == "FETCH":
            self.ir = (self.mem[self.pc], self.mem[(self.pc + 1) % MEM_SIZE])
            self.pc = (self.pc + 2) % MEM_SIZE
            self.state = "DECODE"
        elif self.state == "DECODE":
            self.op, self.rd, self.rs, self.operand = decode(*self.ir)
            self.state = "EXECUTE"
        elif self.state == "EXECUTE":
            self._execute()
        return self.state

    def _execute(self):
        """Carry out the decoded instruction and choose the next control state."""
        op, rd, rs, operand = self.op, self.rd, self.rs, self.operand
        if op == HLT:
            self.state = "HALTED"
            return
        if op == NOP:
            pass
        elif op == LDI:
            self.regs.write(rd, operand)
        elif op == LD:
            self.regs.write(rd, self.mem[operand])
        elif op == ST:
            self.mem[operand] = self.regs.read(rs)
        elif op == MOV:
            self.regs.write(rd, self.regs.read(rs))
        elif op in (ADD, SUB, AND, OR, XOR):
            result, flags = self.alu.execute(ALU_OP[op], self.regs.read(rd),
                                             self.regs.read(rs))
            self.regs.write(rd, result)
            self.flags = flags
        elif op in (SHL, SHR):
            result, flags = self.alu.execute(ALU_OP[op], self.regs.read(rd))
            self.regs.write(rd, result)
            self.flags = flags
        elif op == JMP:
            self.pc = operand
        elif op == JZ:
            if self.flags["Z"]:
                self.pc = operand
        elif op == JNZ:
            if not self.flags["Z"]:
                self.pc = operand
        else:
            raise ValueError(f"unknown opcode {op}")
        self.state = "FETCH"

    def step(self):
        """Run one whole instruction."""
        if self.state == "HALTED":
            return self.state
        while True:
            self.tick()
            if self.state in ("FETCH", "HALTED"):
                return self.state

    def run(self, max_steps=10000):
        """Step until HALTED; RuntimeError if the machine will not stop."""
        steps = 0
        while self.state != "HALTED":
            if steps >= max_steps:
                raise RuntimeError(f"no HLT within {max_steps} instructions")
            self.step()
            steps += 1
        return steps


# n at 0x40, the sum 1..n at 0x41.
SUM_PROGRAM = [
    (LD, 0, 0, 0x40),
    (LDI, 1, 0, 0),
    (LDI, 3, 0, 1),
    (OR, 0, 0, 0),
    (JZ, 0, 0, 16),
    (ADD, 1, 0, 0),
    (SUB, 0, 3, 0),
    (JMP, 0, 0, 6),
    (ST, 0, 1, 0x41),
    (HLT, 0, 0, 0),
]
'''},
            {"name": "main.py", "content": r'''
from datapath import CPU, SUM_PROGRAM

for n in (0, 1, 5, 10):
    cpu = CPU(SUM_PROGRAM)
    cpu.mem[0x40] = n
    steps = cpu.run()
    print(f"n={n:>3}  sum={cpu.mem[0x41]:>3}  instructions={steps}")
'''},
        ],
        "tests": [
            {"name": "encode / decode round-trip", "code": r'''
from datapath import encode, decode, assemble, LDI, ADD, JMP, HLT
_b0, _b1 = encode(ADD, 2, 3, 0)
assert (_b0, _b1) == ((4 << 4) | (2 << 2) | 3, 0), f"encode(ADD, 2, 3) gave {(_b0, _b1)!r}"
for _op in range(16):
    for _rd in range(4):
        for _rs in range(4):
            for _operand in (0, 1, 128, 255):
                assert decode(*encode(_op, _rd, _rs, _operand)) == (_op, _rd, _rs, _operand), \
                    f"round-trip failed for {(_op, _rd, _rs, _operand)!r}"
assert assemble([(LDI, 1, 0, 7), (HLT,)]) == [(1 << 4) | (1 << 2), 7, 15 << 4, 0], \
    f"assemble gave {assemble([(LDI, 1, 0, 7), (HLT,)])!r}"
for _bad in [(16, 0, 0, 0), (-1, 0, 0, 0), (ADD, 4, 0, 0), (ADD, 0, 4, 0), (JMP, 0, 0, 256)]:
    try:
        encode(*_bad)
        assert False, f"encode{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "RegisterFile masks and checks", "code": r'''
from datapath import RegisterFile
_rf = RegisterFile(4, 8)
assert _rf.read(0) == 0, "registers start at zero"
_rf.write(2, 300)
assert _rf.read(2) == 300 & 0xFF, f"R2 is {_rf.read(2)!r}, expected {300 & 0xFF} after masking"
_rf.write(3, -1)
assert _rf.read(3) == 255, f"R3 is {_rf.read(3)!r}, expected 255"
for _bad in (4, -1, 99):
    try:
        _rf.read(_bad)
        assert False, f"read({_bad}) should raise ValueError"
    except ValueError:
        pass
try:
    _rf.write(4, 0)
    assert False, "write to R4 should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The ALU still sets the module 4 flags", "code": r'''
from datapath import ALU
_alu = ALU(8)
for _op, _a, _b, _wr, _wf in [
        ("ADD", 0x7F, 0x01, 0x80, {"Z": 0, "N": 1, "C": 0, "V": 1}),
        ("ADD", 0xFF, 0x01, 0x00, {"Z": 1, "N": 0, "C": 1, "V": 0}),
        ("SUB", 0x03, 0x05, 0xFE, {"Z": 0, "N": 1, "C": 0, "V": 0}),
        ("SUB", 0x80, 0x01, 0x7F, {"Z": 0, "N": 0, "C": 1, "V": 1}),
        ("OR", 0x00, 0x00, 0x00, {"Z": 1, "N": 0, "C": 0, "V": 0})]:
    _r, _f = _alu.execute(_op, _a, _b)
    assert (_r, _f) == (_wr, _wf), \
        f"{_op} {_a:#04x}, {_b:#04x} gave {(_r, _f)!r}, expected {(_wr, _wf)!r}"
'''},
            {"name": "The control FSM runs three phases per instruction", "code": r'''
from datapath import CPU, LDI, HLT
_cpu = CPU([(LDI, 1, 0, 7), (HLT,)])
assert _cpu.state == "FETCH", f"a fresh CPU starts in FETCH, got {_cpu.state!r}"
assert _cpu.pc == 0, f"pc starts at 0, got {_cpu.pc!r}"
assert _cpu.tick() == "DECODE", "FETCH is followed by DECODE"
assert _cpu.pc == 2, f"FETCH advances the pc by 2, got {_cpu.pc!r}"
assert _cpu.tick() == "EXECUTE", "DECODE is followed by EXECUTE"
assert _cpu.regs.read(1) == 0, "the write happens in EXECUTE, not in DECODE"
assert _cpu.tick() == "FETCH", "EXECUTE returns to FETCH"
assert _cpu.regs.read(1) == 7, f"R1 is {_cpu.regs.read(1)!r}, expected 7"
assert _cpu.step() == "HALTED", "the second instruction is HLT"
assert _cpu.tick() == "HALTED", "a halted machine stays halted"
'''},
            {"name": "Data movement: LDI, MOV, ST and LD", "code": r'''
from datapath import CPU, LDI, MOV, ST, LD, HLT
_cpu = CPU([(LDI, 0, 0, 0x2A), (MOV, 1, 0, 0), (ST, 0, 1, 0x80),
            (LD, 2, 0, 0x80), (HLT,)])
_cpu.run()
assert _cpu.regs.read(0) == 0x2A, f"R0 is {_cpu.regs.read(0)!r}, expected 42"
assert _cpu.regs.read(1) == 0x2A, f"MOV left R1 at {_cpu.regs.read(1)!r}, expected 42"
assert _cpu.mem[0x80] == 0x2A, f"ST wrote {_cpu.mem[0x80]!r} to 0x80, expected 42"
assert _cpu.regs.read(2) == 0x2A, f"LD left R2 at {_cpu.regs.read(2)!r}, expected 42"
_other = CPU()
assert _other.mem[0x80] == 0 and _other.regs.read(0) == 0, \
    "two CPUs must not share memory or registers"
'''},
            {"name": "Arithmetic and logic write back and set flags", "code": r'''
from datapath import CPU, LDI, ADD, SUB, AND, XOR, SHL, SHR, HLT
_cpu = CPU([(LDI, 0, 0, 200), (LDI, 1, 0, 100), (ADD, 0, 1, 0), (HLT,)])
_cpu.run()
assert _cpu.regs.read(0) == 44, f"200 + 100 in 8 bits is 44, got {_cpu.regs.read(0)!r}"
assert _cpu.flags["C"] == 1, f"that addition carries; flags were {_cpu.flags!r}"
_cpu = CPU([(LDI, 0, 0, 5), (LDI, 1, 0, 5), (SUB, 0, 1, 0), (HLT,)])
_cpu.run()
assert _cpu.regs.read(0) == 0 and _cpu.flags["Z"] == 1, \
    f"5 - 5 should leave 0 with Z set, got {_cpu.regs.read(0)!r} and {_cpu.flags!r}"
_cpu = CPU([(LDI, 0, 0, 0xF0), (LDI, 1, 0, 0x3C), (AND, 0, 1, 0),
            (LDI, 2, 0, 0x81), (SHL, 2, 0, 0), (LDI, 3, 0, 0x05), (SHR, 3, 0, 0), (HLT,)])
_cpu.run()
assert _cpu.regs.read(0) == 0x30, f"0xF0 AND 0x3C is 0x30, got {_cpu.regs.read(0):#04x}"
assert _cpu.regs.read(2) == 0x02, f"SHL 0x81 is 0x02, got {_cpu.regs.read(2):#04x}"
assert _cpu.regs.read(3) == 0x02, f"SHR 0x05 is 0x02, got {_cpu.regs.read(3):#04x}"
_cpu = CPU([(LDI, 0, 0, 9), (XOR, 0, 0, 0), (HLT,)])
_cpu.run()
assert _cpu.regs.read(0) == 0, "XOR of a register with itself clears it"
'''},
            {"name": "Loads and jumps leave the flags alone", "code": r'''
from datapath import CPU, LDI, SUB, LD, MOV, HLT
_cpu = CPU([(LDI, 0, 0, 4), (LDI, 1, 0, 4), (SUB, 0, 1, 0),
            (LDI, 2, 0, 99), (MOV, 3, 2, 0), (LD, 1, 0, 0x90), (HLT,)])
_cpu.run()
assert _cpu.flags["Z"] == 1, \
    f"only ALU operations touch the flags, so Z should still be 1; got {_cpu.flags!r}"
'''},
            {"name": "Branches", "code": r'''
from datapath import CPU, LDI, SUB, JZ, JNZ, JMP, HLT
_taken = CPU([(LDI, 0, 0, 3), (LDI, 1, 0, 3), (SUB, 0, 1, 0), (JZ, 0, 0, 10),
              (LDI, 2, 0, 111), (LDI, 3, 0, 222), (HLT,)])
_taken.run()
assert _taken.regs.read(2) == 0, "JZ with Z set must skip the instruction at address 8"
assert _taken.regs.read(3) == 222, f"execution should resume at address 10, got R3={_taken.regs.read(3)!r}"
_nottaken = CPU([(LDI, 0, 0, 3), (LDI, 1, 0, 1), (SUB, 0, 1, 0), (JZ, 0, 0, 10),
                 (LDI, 2, 0, 111), (LDI, 3, 0, 222), (HLT,)])
_nottaken.run()
assert _nottaken.regs.read(2) == 111, "with Z clear the JZ falls through"
_jnz = CPU([(LDI, 0, 0, 3), (LDI, 1, 0, 1), (SUB, 0, 1, 0), (JNZ, 0, 0, 10),
            (LDI, 2, 0, 111), (LDI, 3, 0, 222), (HLT,)])
_jnz.run()
assert _jnz.regs.read(2) == 0 and _jnz.regs.read(3) == 222, "JNZ branches when Z is clear"
_jmp = CPU([(JMP, 0, 0, 4), (LDI, 2, 0, 111), (LDI, 3, 0, 222), (HLT,)])
_jmp.run()
assert _jmp.regs.read(2) == 0 and _jmp.regs.read(3) == 222, "JMP is unconditional"
'''},
            {"name": "SUM_PROGRAM computes the triangular numbers", "code": r'''
from datapath import CPU, SUM_PROGRAM
for _n in (0, 1, 2, 5, 10, 22):
    _cpu = CPU(SUM_PROGRAM)
    _cpu.mem[0x40] = _n
    _cpu.run()
    _want = _n * (_n + 1) // 2
    _got = _cpu.mem[0x41]
    assert _got == _want, f"n={_n} left {_got!r} at 0x41, expected {_want}"
'''},
            {"name": "SUM_PROGRAM halts and does not scribble on itself", "code": r'''
from datapath import CPU, SUM_PROGRAM, assemble
_code = assemble(SUM_PROGRAM)
_cpu = CPU(SUM_PROGRAM)
_cpu.mem[0x40] = 6
_steps = _cpu.run()
assert _cpu.state == "HALTED", f"the program must end in HALTED, got {_cpu.state!r}"
assert _steps < 100, f"summing to 6 took {_steps} instructions — the loop should be tight"
assert _cpu.mem[:len(_code)] == _code, "the program must not overwrite its own instructions"
'''},
            {"name": "run() refuses to hang", "code": r'''
from datapath import CPU, JMP, NOP
_cpu = CPU([(JMP, 0, 0, 0)])
try:
    _cpu.run(max_steps=50)
    assert False, "an endless loop should raise RuntimeError, not spin forever"
except RuntimeError:
    pass
_cpu = CPU([(NOP,)])
try:
    _cpu.run(max_steps=200)
    assert False, "a program with no HLT should also raise RuntimeError"
except RuntimeError:
    pass
'''},
            {"name": "datapath.py is import-clean", "code": r'''
_src = open("datapath.py").read()
assert "print(" not in _src, "datapath.py is the hardware; the printing belongs in main.py"
assert "import " not in _src, "no imports are needed — the standard library is not required here"
'''},
        ],
    },
}
