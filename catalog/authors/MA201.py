"""MA201 — Probability & Statistics for Computing. Author module."""

COURSE = {
    "id": "MA201",
    "title": "Probability & Statistics for Computing",
    "year": 2,
    "level": "Intermediate",
    "prereqs": ["MA112"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 120,
    "icon": "σ",
    "summary": (
        "Randomness is the working material of hashing, load balancing, benchmarking "
        "and machine learning, and every claim made about it is a statistical claim. "
        "You build the distributions, estimators and tests from their definitions — no "
        "statistics library — and finish with an A/B-test analyser that states its own "
        "assumptions."
    ),
    "outcomes": [
        "Derive pmf, cdf, expectation and variance for Bernoulli, binomial and geometric variables",
        "Implement exact binomial coefficients without floating-point overflow or a library call",
        "Run reproducible Monte Carlo experiments from a seeded generator",
        "Demonstrate the law of large numbers and the central limit theorem empirically",
        "Compute sample statistics, a Welch two-sample t statistic and a chi-square goodness-of-fit test by hand",
        "Read a critical-value table correctly and state what rejecting the null does and does not mean",
        "Update beliefs with Bayes' rule and build a Laplace-smoothed naive Bayes classifier",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Ross, *A First Course in Probability*, 10th ed. — chapters 4, 5, 7 and 8",
        "Wasserman, *All of Statistics* — chapters 6-10",
        "Mitzenmacher & Upfal, *Probability and Computing*, 2nd ed. — chapters 1-4",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Sample spaces, events and the axioms",
            "summary": (
                "Probability before random variables: what the outcomes are, what an "
                "event is, and the three rules every later result is derived from."
            ),
            "concepts": [
                "A sample space is the set of outcomes a trial can produce and an event is any subset of it, which makes set algebra the algebra of probability",
                r"Kolmogorov's three axioms — $P(A) \ge 0$, $P(S) = 1$, and $P(A \cup B) = P(A) + P(B)$ for disjoint $A$ and $B$ — and everything else in the course is a theorem about them",
                r"The complement rule $P(A^{c}) = 1 - P(A)$, which is why 'at least one' is almost always counted the other way round",
                r"Inclusion-exclusion: $P(A \cup B) = P(A) + P(B) - P(A \cap B)$, because the overlap was counted in both totals",
                r"Equally likely outcomes collapse probability to counting, $P(A) = |A|/|S|$ — a claim about the world that the axioms neither supply nor check",
                r"Counting with the multiplication principle, ordered selections $n!/(n-k)!$ and unordered ones $n!/(k!\,(n-k)!)$ — the whole of finite probability, once the sample space is fixed",
                r"The union bound $P(A_1 \cup \cdots \cup A_n) \le P(A_1) + \cdots + P(A_n)$: every inclusion-exclusion correction after the first subtracts more than it adds back, so dropping all of them can only overshoot",
                r"Countable additivity extends the third axiom to infinite sequences of disjoint events, which is what makes $\sum_{k=1}^{\infty} 2^{-k} = 1$ a legitimate model for 'toss until the first head', and what forces $P = 0$ to stop meaning impossible",
            ],
            "read": [
                {
                    "title": "The three rules, and the set nobody writes down",
                    "minutes": 12,
                    "body": r'''
Two people are handed the same problem. A fair six-sided die is rolled twice and both
faces are recorded; what is the probability that the two faces sum to $7$? One answers
$1/6$. The other answers $1/11$. They agree that the die is fair, they agree on the
arithmetic, and they are working from the same three rules. What they disagree about is
a set that neither of them wrote down.

That set is where probability starts, and skipping it is the most reliable way there is
to get a probability question wrong. Every later object in this course — random
variables, expectations, confidence intervals, $p$-values — is built on top of it and
inherits whatever went wrong there.

## The sample space is a decision, not a discovery

Fix an experiment. The **sample space** $S$ is the set of outcomes you have decided to
distinguish, chosen so that exactly one of them occurs on any run. Two conditions are
doing work in that sentence: *at least* one occurs, so the list is exhaustive, and *at
most* one occurs, so the outcomes are mutually exclusive.

Nothing in the world hands you $S$. For two rolls of a die you might take $S_1$ to be
the $36$ ordered pairs $(i, j)$ with $1 \le i \le 6$ and $1 \le j \le 6$. Or you might
take $S_2$ to be the eleven possible totals $2, 3, \dots, 12$.

Both are legitimate sample spaces: exhaustive, mutually exclusive, and perfectly capable
of carrying a probability model. They are not equally *useful*, and that is the whole of
the disagreement above. The physical symmetry of the die is a statement about the six
faces of one roll. It transfers to $S_1$, where all $36$ pairs inherit the same mass
$1/36$. It does not transfer to $S_2$, where a total of $7$ arises six different ways
and a total of $2$ arises one way. Answering $1/11$ is not bad arithmetic; it is correct
arithmetic on a model that quietly assumed something false.

An **event** is any subset of $S$. In $S_1$, "the total is $7$" is the subset holding
the six pairs $(1,6)$, $(2,5)$, $(3,4)$, $(4,3)$, $(5,2)$, $(6,1)$ — so its probability
is $6/36 = 1/6$. Because events are sets, the language of events is the language of
sets. "$A$ and $B$ both happen" is $A \cap B$; "at least one of them happens" is
$A \cup B$; "$A$ does not happen" is the complement $A^{c}$; "$A$ cannot happen without
$B$ happening" is $A \subseteq B$. Two events are **disjoint**, or mutually exclusive,
when $A \cap B$ contains no outcomes at all — there is no single run of the experiment
that puts you in both.

## Three axioms, and nothing else

A probability model on $S$ is a rule $P$ assigning a number to each event, subject to
exactly three conditions.

**A1, non-negativity.** $P(A) \ge 0$ for every event $A$.

**A2, normalisation.** $P(S) = 1$.

**A3, additivity.** $P(A \cup B) = P(A) + P(B)$ whenever $A$ and $B$ are disjoint.

That is Kolmogorov's list, and it is startlingly thin. It does not say what any
particular probability is. It does not say the die is fair. It says only that masses are
non-negative, that the total mass is one, and that mass adds over pieces that do not
overlap. Every other formula in this module is a theorem about those three lines, and
the point of what follows is that you should never again have to remember one of them as
a separate fact.

## Four consequences, each one line long

**The impossible event has probability zero.** Take $E = A \cap A^{c}$, the event that an
outcome is both in $A$ and not in $A$. It contains nothing, so $E \cap E$ contains
nothing either, which means $E$ is disjoint from itself and A3 applies to $E$ with $E$:

$$P(E) = P(E \cup E) = P(E) + P(E) \quad \Rightarrow \quad P(E) = 0 .$$

**The complement rule.** $A$ and $A^{c}$ are disjoint and their union is $S$, so A3 and
then A2 give

$$P(A) + P(A^{c}) = P(S) = 1 \quad \Rightarrow \quad P(A^{c}) = 1 - P(A) .$$

**Monotonicity, and the ceiling at one.** If $A \subseteq B$, split $B$ into the part
inside $A$ and the part outside it. Those two are disjoint and their union is $B$, so
$P(B) = P(A) + P(B \cap A^{c})$, and the second term is non-negative by A1. Hence
$P(A) \le P(B)$. Since every event satisfies $A \subseteq S$, every event satisfies
$P(A) \le 1$ — an upper bound the axioms never stated and did not need to.

**Inclusion-exclusion.** A3 needs disjointness, and most pairs of events you care about
overlap. Repair it the same way: $A \cup B$ is the disjoint union of $A$ and
$B \cap A^{c}$, so $P(A \cup B) = P(A) + P(B \cap A^{c})$, and the monotonicity step
just above, applied to $A \cap B \subseteq B$, gives
$P(B \cap A^{c}) = P(B) - P(A \cap B)$. Substituting,

$$P(A \cup B) = P(A) + P(B) - P(A \cap B) .$$

Read it as an accounting correction rather than a formula. Adding the two totals counts
every outcome of the overlap twice, so the overlap is subtracted back once.

## Worked: a cohort, two courses

Of $200$ students, $120$ have taken algorithms, $100$ have taken statistics, and $60$
have taken both. Pick one student uniformly at random. What is the probability they have
taken at least one of the two, and what is the probability they have taken neither?

Let $A$ be "took algorithms" and $B$ be "took statistics".

$$P(A) = \frac{120}{200} = 0.60, \qquad P(B) = \frac{100}{200} = 0.50, \qquad
P(A \cap B) = \frac{60}{200} = 0.30$$

$$P(A \cup B) = 0.60 + 0.50 - 0.30 = 0.80$$

$$P\left((A \cup B)^{c}\right) = 1 - 0.80 = 0.20$$

So $160$ students took at least one course and $40$ took neither. Notice what the naive
sum would have said: $0.60 + 0.50 = 1.10$, a probability larger than one, which the
monotonicity result above has just ruled out. That is the useful thing about deriving
the ceiling rather than assuming it — an impossible answer becomes a signal instead of a
number you write down.

Notice too that the four cells of the table are now determined. Algorithms only is
$0.60 - 0.30 = 0.30$; statistics only is $0.50 - 0.30 = 0.20$; both is $0.30$; neither is
$0.20$. They sum to $1.00$, as they must, because those four events are disjoint and
their union is $S$.

## Worked: at least one six, and the sum that keeps being wrong

Roll two fair dice. What is the probability of at least one six?

The tempting answer is $1/6 + 1/6 = 1/3$. It is wrong, and it is wrong for a reason
worth naming. Let $A$ be "the first die shows a six" and $B$ be "the second does". A3
does not apply, because $A$ and $B$ are not disjoint: the outcome $(6,6)$ lies in both.
Inclusion-exclusion does apply. On the $36$ equally likely ordered pairs,

$$P(A) = \frac{6}{36} = \frac{1}{6}, \qquad P(B) = \frac{1}{6}, \qquad
P(A \cap B) = \frac{1}{36}$$

$$P(A \cup B) = \frac{1}{6} + \frac{1}{6} - \frac{1}{36}
= \frac{6}{36} + \frac{6}{36} - \frac{1}{36} = \frac{11}{36} \approx 0.3056 .$$

The complement route agrees and is quicker. "No six at all" means both dice avoid the
six, which is $5 \times 5 = 25$ of the $36$ pairs, so

$$P(A \cup B) = 1 - \frac{25}{36} = \frac{11}{36} .$$

Now push the same error further, because at two dice it looks like a rounding
disagreement. With three dice the naive sum gives $3 \times 1/6 = 1/2$, while counting
the complement gives $1 - (5/6)^{3} = 91/216 \approx 0.4213$. With six dice the naive
sum gives exactly $1$ — certainty — while the truth is $1 - (5/6)^{6} \approx 0.6651$.
With twelve dice the naive sum gives $2$. Adding overlapping probabilities does not
merely lose precision; it walks straight off the end of the scale.

## The mistake, and why it is tempting

Both failures in this unit have the same shape: a rule was applied outside the
hypothesis that licenses it. A3 is not "probabilities add". A3 is "probabilities add
*when the events are disjoint*", and disjointness is a property of the sets, not a
convenience. The reason the error survives is that it is invisible in the small cases
people use to build intuition. Two events that overlap only a little give a sum that is
only a little too large, and the answer looks plausible enough to keep.

The equally-likely trap has the same anatomy. $S_2$, the eleven totals, satisfies all
three axioms under the assignment "each total has mass $1/11$". Nothing internal to the
model objects. The axioms constrain how masses combine; they are entirely silent about
which outcomes deserve equal mass, and that silence is deliberate — it is what lets the
same three rules describe a fair die, a loaded die, and tomorrow's weather.

## Where the axioms stop

Three limits are worth carrying forward. First, the axioms give you no numbers: some
extra claim — symmetry, a measurement, a model — has to supply $P$ before any of this
computes anything. Second, A3 as stated covers two disjoint events, and by induction any
finite list of them; the infinite case needs a strictly stronger assumption, and the
third reading unit in this module is about what that buys and what it costs. Third,
$P(A) \le 1$ was derived from monotonicity, so any calculation that produces $1.10$ or
$2$ has not found a surprising probability. It has found a broken model, and the usual
break is an addition that assumed a disjointness nobody checked.
''',
                },
                {
                    "title": "When probability is counting, and when it only looks like it",
                    "minutes": 13,
                    "body": r'''
The axioms are silent about numbers. They will tell you that $P(A \cup B)$ equals
$P(A) + P(B) - P(A \cap B)$, but they will never tell you what $P(A)$ is, and a theory
that computes nothing is not much use for sizing a hash table. Something has to supply
the masses, and for a finite experiment with a physical symmetry there is one
particularly cheap supplier.

## The equally likely model, and why it is legal

Suppose $S$ is finite with $|S| = N$ outcomes, and suppose you are willing to claim that
no outcome is favoured over any other. Then each outcome carries mass $1/N$, and for any
event $A$,

$$P(A) = \frac{|A|}{|S|} .$$

It is worth checking once that this really is a probability model rather than a
plausible-looking recipe. A1 holds because a count is never negative. A2 holds because
$|S|/|S| = 1$. A3 holds because for disjoint $A$ and $B$ no outcome lies in both, so
$|A \cup B| = |A| + |B|$, and dividing by $N$ preserves the equation. All three axioms
come out of properties of counting, which is the real content of the phrase "probability
reduces to combinatorics": it is not an analogy, it is the same three rules wearing
different clothes.

What the claim buys is that every probability question about $S$ becomes two counting
questions. What it costs is an assumption that lives outside mathematics and can simply
be false.

## Counting, in three moves

**The multiplication principle.** If a construction is made of $k$ successive choices,
the first with $n_1$ options, the second with $n_2$ options regardless of how the first
went, and so on, then the number of constructions is $n_1 n_2 \cdots n_k$. The
justification is a picture: each of the $n_1$ first choices opens $n_2$ second choices,
none of which coincide, so the count multiplies. The clause that matters is "regardless
of how the first went" — the *number* of later options must not depend on the earlier
ones, though their identity may.

The immediate consequence: a string of $k$ symbols drawn from an alphabet of $n$,
repeats allowed, can be formed in $n^{k}$ ways. Four-digit PINs, $10^{4}$ of them.
Assignments of $k$ keys to $n$ hash buckets, $n^{k}$ of them.

**Ordered, without repeats.** Choose $k$ items from $n$ distinct ones, order mattering,
nothing reused. The first choice has $n$ options, the second $n-1$, down to $n-k+1$:

$$n (n-1) \cdots (n-k+1) = \frac{n!}{(n-k)!} .$$

**Unordered.** Now the order is not to be counted. Every $k$-element subset can be
written out in $k!$ different orders, and the ordered count above lists each subset
exactly that many times, so divide:

$$C(n,k) = \frac{n!}{k! \, (n-k)!} .$$

That division is the only subtle step in elementary counting, and it is subtle only
because it is so easy to do it without noticing you have done it.

## Worked: two aces off the top

A standard $52$-card deck is shuffled uniformly. What is the probability that the top two
cards are both aces?

Count the ordered way first. The sample space is every ordered pair of distinct cards in
the top two positions, and the event $A$ is the pairs where both are aces:

$$|S| = 52 \times 51 = 2652, \qquad |A| = 4 \times 3 = 12$$

$$P(A) = \frac{12}{2652} = \frac{1}{221} \approx 0.004525 .$$

Now count the unordered way. Take the sample space to be the two-card subsets that could
occupy the top two positions:

$$|S| = C(52,2) = \frac{52 \times 51}{2} = 1326, \qquad
|A| = C(4,2) = \frac{4 \times 3}{2} = 6$$

$$P(A) = \frac{6}{1326} = \frac{1}{221} .$$

The same number, because the factor of $2$ introduced by the ordering cancels between the
numerator and the denominator. This is the practical rule for counting problems: ordered
and unordered are both correct, and mixing them is not. Counting the numerator with order
and the denominator without would have given $12/1326$, twice the truth.

## Worked: the collision nobody expects

Twenty-three people are in a room. Treat the $365$ days as equally likely for each of
them, so that all $365^{23}$ lists of birthdays are equally likely. What is the
probability that some two of them share a birthday?

Let $D$ be the event that all twenty-three birthdays are distinct. Count $D$ rather than
its complement, because "some two share" is a union of $C(23,2) = 253$ overlapping events
while $D$ is a single ordered selection: the first person may have any of $365$ days, the
second any of the remaining $364$, and so on down to $343$.

$$|S| = 365^{23}, \qquad |D| = 365 \times 364 \times \cdots \times 343 = \frac{365!}{342!}$$

$$P(D) = \frac{365 \times 364 \times \cdots \times 343}{365^{23}}
= \left(\frac{365}{365}\right) \left(\frac{364}{365}\right) \cdots
\left(\frac{343}{365}\right)$$

Multiplying those twenty-three factors gives $P(D) = 0.4927$, so by the complement rule

$$P(D^{c}) = 1 - 0.4927 = 0.5073 .$$

Just over even money, on twenty-three people out of three hundred and sixty-five days.
Almost everyone guesses far too low, and the reason is that they are silently answering a
different question — "does someone share *my* birthday", which involves only $22$
comparisons. The event actually asked about involves $253$ pairs, and $253$ is already
comfortably more than half of $365$.

The same arithmetic with $n$ buckets in place of $365$ days says a collision becomes
likely once the number of keys reaches roughly $1.18 \sqrt{n}$. A space of $2^{64}$
values starts colliding at around $5 \times 10^{9}$ keys, not $2^{63}$ — which is why
hash lengths are chosen against the square root of the space, and why a $64$-bit content
hash is not a serious identifier.

## The mistake: a sample space whose outcomes are not equally likely

Toss two fair coins. What is the probability of one head and one tail?

The wrong answer is $1/3$, from the sample space "two heads, one of each, two tails".
That sample space is real — its three outcomes are exhaustive and mutually exclusive —
but the masses are not equal, because "one of each" happens as $HT$ or as $TH$ while "two
heads" happens only as $HH$. On the four ordered outcomes the answer is $2/4 = 1/2$.

This is exactly the die-total error from the first reading unit, and it is tempting for
the same reason: summarising outcomes feels like simplification rather than modelling.
Nothing in the axioms flags it, because the collapsed space with masses $1/3$ each is a
perfectly valid probability model — it is just a model of a different, imaginary
experiment. The physical symmetry is a symmetry of individual coins, and it survives only
in a sample space whose outcomes distinguish individual coins.

The discipline that prevents it: write $S$ down as the *finest* description the
experiment supports — every roll, every toss, every card, in order — argue for equal
masses at that level, and only then count. Collapsing afterwards is safe. Collapsing
first is not.

## Where counting stops

The equally-likely model is a claim about the world and it fails constantly. A loaded die
satisfies all three axioms. Letters in English text are not uniform over $26$ values,
which is exactly why letter frequency breaks a substitution cipher. Real birthdays are
not uniform over $365$ days: February $29$ exists, and births cluster seasonally and away
from weekends.

The birthday case comes with a useful direction. Non-uniformity can only make a collision
*more* likely, never less: among all distributions over $n$ buckets, the uniform one
minimises the chance that two independently placed keys land together. So the $0.5073$
computed above is a lower bound on the real-world figure, and a hash function that is
merely close to uniform still has its collision probability bounded below by the uniform
calculation. That is the sense in which the idealised count is worth doing even when you
know the idealisation is false.

The other place counting stops is where $S$ stops being finite. The ratio $|A|/|S|$ means
nothing when both are infinite, and the next reading unit is about what replaces it.
''',
                },
                {
                    "title": "Unions you cannot compute, and spaces you cannot count",
                    "minutes": 12,
                    "body": r'''
Inclusion-exclusion for two events is exact and cheap. In practice you rarely get to use
it, because the term it needs — $P(A \cap B)$ — is usually the one nobody measured. A
service has two hundred dependencies and you know each one's failure rate; you know
nothing whatever about how their failures coincide. The question "what is the probability
that at least one fails" has no exact answer from that data, and pretending otherwise is
how outage estimates get written.

This unit is about the three things you can do instead: extend inclusion-exclusion
exactly and watch it become unusable, bound the union instead of computing it, and handle
the sample spaces that are not finite at all.

## Three events, by treating two of them as one

Nothing new is needed. Write $D = A \cup B$ and apply the two-event rule to $D$ and $C$:

$$P(A \cup B \cup C) = P(D) + P(C) - P(D \cap C) .$$

Now expand the two pieces. The first is the two-event rule again,
$P(D) = P(A) + P(B) - P(A \cap B)$. The second uses the distributive law for sets,
$(A \cup B) \cap C = (A \cap C) \cup (B \cap C)$, and then the two-event rule a third
time. The intersection of those two pieces is $A \cap B \cap C$, so

$$P(D \cap C) = P(A \cap C) + P(B \cap C) - P(A \cap B \cap C) .$$

Substituting and collecting,

$$P(A \cup B \cup C) = P(A) + P(B) + P(C) - P(A \cap B) - P(A \cap C) - P(B \cap C)
+ P(A \cap B \cap C) .$$

Singles added, pairs subtracted, the triple added back. The alternating pattern
continues: for $n$ events the exact formula has one term for every non-empty subset of
them, $2^{n} - 1$ terms in all. For three events that is seven and perfectly workable.
For twenty it is over a million, each one a joint probability nobody has estimated. The
formula does not become wrong at scale; it becomes a demand for data that does not exist.

## Worked: divisible by 2, 3 or 5

Draw an integer uniformly from $1$ to $1000$. What is the probability that it is
divisible by $2$, by $3$, or by $5$?

Counting multiples up to $1000$: there are $500$ of $2$, $333$ of $3$ and $200$ of $5$.
An integer divisible by both $2$ and $3$ is divisible by $6$, and there are $166$ of
those; by $2$ and $5$ means by $10$, giving $100$; by $3$ and $5$ means by $15$, giving
$66$. All three at once means divisible by $30$, giving $33$.

$$|A \cup B \cup C| = 500 + 333 + 200 - 166 - 100 - 66 + 33 = 734$$

$$P(A \cup B \cup C) = \frac{734}{1000} = 0.734$$

Two details are where the marks go. The pairwise counts use the *least common multiple*,
not the product: for $2$ and $3$ that happens to be the product $6$, but for $4$ and $6$
the pair count uses $12$, and using $24$ would throw the answer away. And the singles
alone give $1033$, which is more than $1000$ — the overcount is real and large, not a
rounding artefact.

## The union bound, and what it costs

If you cannot compute the corrections, drop them. The first correction subtracts, and
dropping every correction turns the equation into an inequality in a direction you can
prove:

$$P(A_1 \cup A_2 \cup \cdots \cup A_n) \le P(A_1) + P(A_2) + \cdots + P(A_n) .$$

The proof does not go through inclusion-exclusion at all — it is the disjointness trick
from the first reading unit, applied $n$ times. Define $B_1 = A_1$ and, for $k \ge 2$,
let $B_k$ be the part of $A_k$ that lies in none of the earlier events, that is
$B_k = A_k \cap (A_1 \cup \cdots \cup A_{k-1})^{c}$. The $B_k$ are disjoint by
construction and their union is the same as the union of the $A_k$, so A3 applied
repeatedly gives $P(B_1) + \cdots + P(B_n)$ for the union. Each $B_k \subseteq A_k$, so
monotonicity gives $P(B_k) \le P(A_k)$, and summing those $n$ inequalities finishes it.

Nothing was assumed about how the events relate. That is the point of the bound, and it
is also its cost.

## Worked: two hundred dependencies

A request touches $200$ services, each of which fails with probability $10^{-4}$. Let $F$
be the event that the request fails, meaning at least one service does. What can be said
about $P(F)$?

$$P(F) \le 200 \times 10^{-4} = 0.02$$

At most one request in fifty. The bound is honest and it is also loose: if the $200$
failures were perfectly coincident — one shared power supply behind all of them — the
true probability would be $10^{-4}$, two hundred times smaller. The bound is tight in the
opposite regime, when the events barely overlap, and the near-independent case sits just
under it: $1 - (1 - 10^{-4})^{200} = 0.0198$, within one percent of $0.02$. So the union
bound is an excellent estimate for many rare, weakly related events, and a wild
overestimate for a few strongly related ones.

The failure mode to watch for: with $20 \, 000$ services the bound reads $2.0$. That is
not a probability, and it is not an error in the derivation — the inequality is still
true, since every probability is at most $1$. It has simply stopped saying anything.
Report it as "no useful bound", never as a number.

## Sample spaces that do not end

Toss a fair coin until the first head. The outcome is the toss number $k$ on which the
head lands, and the sample space is $1, 2, 3, \dots$ — infinite, but listable. The
natural model gives

$$P(k) = 2^{-k}, \qquad k = 1, 2, 3, \dots$$

For this to be a probability model at all, the masses must total one, and checking that
means adding infinitely many of them:

$$\sum_{k=1}^{\infty} 2^{-k} = \frac{1/2}{1 - 1/2} = 1 .$$

A3 as stated covers two disjoint events, and by induction any finite number of them. It
does not cover a countable infinity, and the sum above is exactly that. So the axiom is
strengthened: **countable additivity** says that for a sequence of pairwise disjoint
events $A_1, A_2, A_3, \dots$ the probability of their union is
$P(A_1) + P(A_2) + P(A_3) + \cdots$, with the infinite series on the right.

With that, "a head appears eventually" has probability $1$. Without it, the individual
masses are still assigned, but nothing licenses adding them all up, and the question has
no answer. The extra strength is not free — it is what forces the machinery of measurable
sets, and it is why $P$ is not defined on every subset of a continuous space — but
everything in this course uses it.

## Where equally likely dies completely

Now pick a real number uniformly from the interval between $0$ and $1$. The sample space
is uncountable, and $|A|/|S|$ is meaningless: both counts are infinite. Probability is
instead assigned by length, so the sub-interval from $0.2$ to $0.5$ has probability $0.3$.

What is the probability of drawing exactly $1/3$? A single point has length $0$, so the
answer is $0$ — and yet the draw certainly produces *some* number, and whichever number
it produces was an outcome of probability zero. Probability zero does not mean
impossible. It means negligible in the sense of the measure being used, and the
distinction is not a technicality: it is why the continuous distributions later in this
course are described by densities and never by the probability of a point.

Notice also that countable additivity is what makes the two cases behave differently. If
the interval held only countably many points, each of probability $0$, the total would be
$0 + 0 + 0 + \cdots = 0$, contradicting $P(S) = 1$. The uncountability is not an
inconvenience in the setup; it is a requirement of it.

## The two mistakes

The first is reporting a union bound as a probability. "The failure probability is $2.0$"
is a sentence that should stop a review, and the fix is to say the bound is vacuous
rather than to quietly renormalise it.

The second is reading $P(A) = 0$ as "$A$ cannot happen", and its mirror, reading
$P(A) = 1$ as "$A$ always happens". On a finite sample space those readings are safe. On a
continuous one they are false, and every statement in the rest of this course of the form
"the estimator converges" is a statement about an event of probability one that still has
exceptions you can write down.
''',
                },
            ],
            "derive": [
                {
                    "title": "Inclusion-exclusion, out of disjointness alone",
                    "minutes": 12,
                    "vars": ["P_A", "P_B", "P_AB", "P_D"],
                    "brief": r'''
The third axiom pays out only for disjoint events, and $A$ and $B$ overlap. The whole
derivation is one idea repeated: if the events you have are not disjoint, cut them into
pieces that are, and add those.

Write $P_{A}$ for $P(A)$, $P_{B}$ for $P(B)$, $P_{AB}$ for $P(A \cap B)$, and $P_{D}$ for
$P(B \cap A^{c})$ — the part of $B$ that lies outside $A$. Every step below is an
application of A3 to two sets that genuinely do not overlap.
''',
                    "steps": [
                        {
                            "prompt": r"$B$ splits into the part inside $A$ and the part outside it: $B = (A \cap B) \cup (B \cap A^{c})$, and those two pieces share no outcome. Write $P(B)$ in terms of $P_{AB}$ and $P_{D}$.",
                            "answer": "P_{AB} + P_{D}",
                            "placeholder": "sum of two of the named quantities",
                            "hint": r"A3 says the probabilities of two disjoint pieces add to the probability of their union, and here the union is $B$ itself.",
                        },
                        {
                            "prompt": r"That equation contains $P_{D}$, which is not one of the three quantities the final answer is allowed to use. Rearrange it and write $P_{D}$ in terms of $P_{B}$ and $P_{AB}$.",
                            "answer": "P_{B} - P_{AB}",
                            "hint": r"Subtract $P_{AB}$ from both sides of the previous line.",
                        },
                        {
                            "prompt": r"Now cut the union the same way: $A \cup B = A \cup (B \cap A^{c})$, and those two pieces are disjoint because the second one excludes everything in $A$. Write $P(A \cup B)$ in terms of $P_{A}$ and $P_{D}$.",
                            "answer": "P_{A} + P_{D}",
                            "placeholder": "A3 again, on the new pair",
                            "hint": r"Nothing is left over: every outcome of $A \cup B$ is either in $A$ or in $B$ but not $A$, and never both.",
                            "deconstruct": [
                                r"The two pieces are $A$ and $B \cap A^{c}$.",
                                r"Their intersection is empty, because the second piece was built to exclude $A$.",
                                r"So A3 applies, and $P(A \cup B) = P(A) + P(B \cap A^{c})$.",
                            ],
                        },
                        {
                            "prompt": r"Substitute the expression for $P_{D}$ from step 2 into the line from step 3. Write $P(A \cup B)$ in terms of $P_{A}$, $P_{B}$ and $P_{AB}$ only.",
                            "answer": "P_{A} + P_{B} - P_{AB}",
                            "hint": r"Replace $P_{D}$ by $P_{B} - P_{AB}$ and drop the brackets.",
                        },
                        {
                            "prompt": r"Adding the two totals overcounts the union. By exactly how much? Write the difference $P_{A} + P_{B} - P(A \cup B)$, simplified.",
                            "answer": "P_{AB}",
                            "hint": r"Substitute the result of step 4 and cancel. The answer is a single symbol, and it is the reason the naive sum fails.",
                            "deconstruct": [
                                r"$P_{A} + P_{B} - P(A \cup B) = P_{A} + P_{B} - (P_{A} + P_{B} - P_{AB})$.",
                                r"The $P_{A}$ and $P_{B}$ terms cancel in pairs.",
                                r"Every outcome of the overlap was counted once in $P_{A}$ and once in $P_{B}$, so the excess is exactly one copy of it.",
                            ],
                        },
                    ],
                    "closing": r'''
Two things fall straight out of the last line. Because $P_{AB} \ge 0$ by A1, the sum
$P_{A} + P_{B}$ can never be smaller than $P(A \cup B)$ — that inequality is the union
bound for two events, and the argument generalises to $n$ of them. And because
$P(A \cup B) \le 1$, the overlap satisfies $P_{AB} \ge P_{A} + P_{B} - 1$: if $60$ per
cent of a cohort takes algorithms and $50$ per cent takes statistics, at least $10$ per
cent takes both, whatever else is true. That is the Bonferroni inequality, and it is
often the only thing a survey's marginal totals will tell you about its overlaps.
''',
                },
                {
                    "title": "Three events, from the two-event rule",
                    "minutes": 12,
                    "vars": ["P_A", "P_B", "P_C", "P_D", "P_DC", "P_AB", "P_AC", "P_BC", "P_ABC"],
                    "brief": r'''
No new principle is needed for three events — only the two-event rule, used three times,
on a well-chosen grouping.

Set $D = A \cup B$ and treat it as a single event. Write $P_{D}$ for $P(D)$, $P_{DC}$ for
$P(D \cap C)$, and $P_{AB}$, $P_{AC}$, $P_{BC}$, $P_{ABC}$ for the probabilities of
$A \cap B$, $A \cap C$, $B \cap C$ and $A \cap B \cap C$.
''',
                    "steps": [
                        {
                            "prompt": r"Apply the two-event inclusion-exclusion rule to the pair $D$ and $C$. Write $P(D \cup C)$ in terms of $P_{D}$, $P_{C}$ and $P_{DC}$.",
                            "answer": "P_{D} + P_{C} - P_{DC}",
                            "placeholder": "the two-event rule, with D in place of A",
                            "hint": r"The rule does not care that $D$ is itself a union; it is an event like any other.",
                        },
                        {
                            "prompt": r"Expand the first piece. Write $P_{D} = P(A \cup B)$ in terms of $P_{A}$, $P_{B}$ and $P_{AB}$.",
                            "answer": "P_{A} + P_{B} - P_{AB}",
                            "hint": r"This is the same rule again, now on the pair it was originally derived for.",
                        },
                        {
                            "prompt": r"Expand the second piece. Distributing gives $D \cap C = (A \cap C) \cup (B \cap C)$, and those two overlap in $A \cap B \cap C$. Write $P_{DC}$ in terms of $P_{AC}$, $P_{BC}$ and $P_{ABC}$.",
                            "answer": "P_{AC} + P_{BC} - P_{ABC}",
                            "hint": r"The two-event rule a third time, on the pair $A \cap C$ and $B \cap C$. Their intersection is everything in $A$, in $B$ and in $C$.",
                            "deconstruct": [
                                r"$D \cap C = (A \cup B) \cap C = (A \cap C) \cup (B \cap C)$ by distributivity.",
                                r"An outcome in both $A \cap C$ and $B \cap C$ is in $A$, in $B$ and in $C$, so the overlap is $A \cap B \cap C$.",
                                r"Apply $P(X \cup Y) = P(X) + P(Y) - P(X \cap Y)$ with $X = A \cap C$ and $Y = B \cap C$.",
                            ],
                        },
                        {
                            "prompt": r"Substitute steps 2 and 3 into step 1, and write $P(A \cup B \cup C)$ using only the seven quantities $P_{A}$, $P_{B}$, $P_{C}$, $P_{AB}$, $P_{AC}$, $P_{BC}$ and $P_{ABC}$.",
                            "answer": "P_{A} + P_{B} + P_{C} - P_{AB} - P_{AC} - P_{BC} + P_{ABC}",
                            "hint": r"Mind the sign on the last term: it is subtracted inside a bracket that is itself subtracted, so it comes back positive.",
                            "deconstruct": [
                                r"Start from $P_{D} + P_{C} - P_{DC}$.",
                                r"Put in $P_{D} = P_{A} + P_{B} - P_{AB}$.",
                                r"Put in $P_{DC} = P_{AC} + P_{BC} - P_{ABC}$, and subtract the whole bracket.",
                                r"Subtracting $-P_{ABC}$ adds $P_{ABC}$ back.",
                            ],
                        },
                    ],
                    "closing": r'''
Singles added, pairs subtracted, the triple added back — and the pattern continues, with
one term for every non-empty subset of the events and a sign that alternates with the
size of the subset. For $n$ events that is $2^{n} - 1$ terms.

Which is why the formula is a theoretical result rather than a working tool past about
three or four events. Every term after the singles is a joint probability, and joint
probabilities are exactly what real data does not contain. The union bound in the third
reading unit exists because dropping all of them at once still leaves something true.
''',
                },
                {
                    "title": "The four cells of a two-event table",
                    "minutes": 11,
                    "vars": ["P_A", "P_B", "P_AB"],
                    "brief": r'''
Two events cut the sample space into four disjoint pieces: both happen, only $A$ happens,
only $B$ happens, neither happens. Every question about $A$ and $B$ is a sum of some of
those four numbers, so it is worth being able to write all four down from
$P_{A} = P(A)$, $P_{B} = P(B)$ and $P_{AB} = P(A \cap B)$ alone.

Three numbers determining four cells is not a coincidence: the cells must total $1$, so
only three of them are free.
''',
                    "steps": [
                        {
                            "prompt": r"$A$ splits into the part inside $B$ and the part outside it. Write $P(A \cap B^{c})$, the probability that $A$ happens and $B$ does not, in terms of $P_{A}$ and $P_{AB}$.",
                            "answer": "P_{A} - P_{AB}",
                            "placeholder": "a difference of two named quantities",
                            "hint": r"$P(A) = P(A \cap B) + P(A \cap B^{c})$, because those two pieces are disjoint and make up $A$.",
                        },
                        {
                            "prompt": r"By the same argument on $B$, write $P(B \cap A^{c})$ in terms of $P_{B}$ and $P_{AB}$.",
                            "answer": "P_{B} - P_{AB}",
                            "hint": r"Swap the roles of $A$ and $B$ in the previous step. The overlap term is the same one.",
                        },
                        {
                            "prompt": r"Now the last cell. By De Morgan, $A^{c} \cap B^{c} = (A \cup B)^{c}$, so its probability is $1 - P(A \cup B)$. Substitute inclusion-exclusion and write it in terms of $P_{A}$, $P_{B}$ and $P_{AB}$.",
                            "answer": "1 - P_{A} - P_{B} + P_{AB}",
                            "hint": r"Subtract the whole of $P_{A} + P_{B} - P_{AB}$ from $1$, and watch the sign on the last term.",
                            "deconstruct": [
                                r"$P\left((A \cup B)^{c}\right) = 1 - P(A \cup B)$ by the complement rule.",
                                r"$P(A \cup B) = P_{A} + P_{B} - P_{AB}$ by inclusion-exclusion.",
                                r"So the cell is $1 - (P_{A} + P_{B} - P_{AB})$, and distributing the minus sign flips all three terms.",
                            ],
                        },
                        {
                            "prompt": r"Add the two 'only' cells from steps 1 and 2 to get the probability that exactly one of $A$ and $B$ happens, in terms of $P_{A}$, $P_{B}$ and $P_{AB}$.",
                            "answer": "P_{A} + P_{B} - 2 P_{AB}",
                            "hint": r"The two cells you are adding each already had one copy of $P_{AB}$ removed, and neither of them contains the overlap.",
                        },
                        {
                            "prompt": r"Add all four cells — both, only $A$, only $B$, neither — and simplify. What number must come out?",
                            "answer": "1",
                            "placeholder": "a single number",
                            "hint": r"The four cells are disjoint and their union is the whole sample space, so A3 and A2 fix the total before you do any algebra.",
                            "deconstruct": [
                                r"The four cells are $P_{AB}$, $P_{A} - P_{AB}$, $P_{B} - P_{AB}$ and $1 - P_{A} - P_{B} + P_{AB}$.",
                                r"The $P_{AB}$ terms are $+1, -1, -1, +1$ copies, which cancel.",
                                r"The $P_{A}$ terms are $+1$ and $-1$, and likewise for $P_{B}$.",
                                r"Everything cancels except the $1$.",
                            ],
                        },
                    ],
                    "closing": r'''
The table is worth committing to memory as a picture rather than four formulas, because
it makes two common errors impossible. A cell can never be negative, so $P_{AB}$ is
trapped between $P_{A} + P_{B} - 1$ and the smaller of $P_{A}$ and $P_{B}$: a report
claiming $P(A) = 0.3$, $P(B) = 0.4$ and $P(A \cap B) = 0.35$ is describing something that
cannot exist. And "exactly one" is $P_{A} + P_{B} - 2 P_{AB}$ while "at least one" is
$P_{A} + P_{B} - P_{AB}$; the factor of two is the whole difference between the two
questions, and reading it off the table is faster than re-deriving it under pressure.
''',
                },
                {
                    "title": "The probability of a hash collision",
                    "minutes": 13,
                    "vars": ["n", "m", "k"],
                    "brief": r'''
$m$ distinct keys are hashed into $n$ buckets. Assume the hash spreads them so evenly
that every possible assignment of keys to buckets is equally likely — the idealisation
the last reading unit warned about, and the one every table-sizing rule is built on.

The event you care about is "some two keys collide". That is a union of many overlapping
events, one for each pair, and computing it directly means inclusion-exclusion over
$C(m,2)$ terms. Its complement is a single ordered count, so count the complement: let
$N$ be the event that no two keys share a bucket.
''',
                    "steps": [
                        {
                            "prompt": r"First the sample space. Each of the $m$ keys may land in any of the $n$ buckets, independently of where the others went. How many assignments are there in total? Write it in terms of $n$ and $m$.",
                            "answer": "n^{m}",
                            "placeholder": "one of the two letters raised to the other",
                            "hint": r"The multiplication principle: $n$ choices for the first key, $n$ for the second, and so on for $m$ keys.",
                        },
                        {
                            "prompt": r"Now the favourable count. How many assignments send every key to a different bucket? Write it as a ratio of two factorials in $n$ and $m$.",
                            "answer": "\\frac{n!}{(n-m)!}",
                            "placeholder": "a ratio of two factorials",
                            "hint": r"The first key has $n$ buckets, the second has $n-1$, down to $n-m+1$ for the last. That falling product is $n!$ divided by the factorial of what is left over.",
                            "deconstruct": [
                                r"The product is $n (n-1) (n-2) \cdots (n-m+1)$, with $m$ factors.",
                                r"Multiplying and dividing by $(n-m)!$ completes the top into $n!$.",
                                r"So the count is $n!$ over $(n-m)!$ — and it is $0$ once $m > n$, which is the pigeonhole principle falling out of the algebra.",
                            ],
                        },
                        {
                            "prompt": r"Divide the favourable count by the size of the sample space. Write $P(N)$, the probability that no two keys collide, in terms of $n$ and $m$.",
                            "answer": "\\frac{n!}{(n-m)! \\cdot n^{m}}",
                            "hint": r"Equally likely outcomes, so the probability is the count from step 2 over the count from step 1.",
                        },
                        {
                            "prompt": r"Finally, use the complement rule to write $P(N^{c})$, the probability that at least two keys share a bucket.",
                            "answer": "1 - \\frac{n!}{(n-m)! \\cdot n^{m}}",
                            "hint": r"'At least one collision' is exactly the failure of 'no collision', and those two events are disjoint with union $S$.",
                        },
                    ],
                    "closing": r'''
Put $n = 365$ and $m = 23$ into that expression and it returns $P(N^{c}) = 0.5073$: the
birthday problem, with days for buckets and people for keys. Put $n = 2^{32}$ into it and
the crossover to even odds arrives at about $77 \, 000$ keys, not two billion.

The useful approximation comes from the same expression. Writing the product as
$(1 - 1/n)(1 - 2/n) \cdots$ and using $1 - x \approx e^{-x}$ for small $x$ gives
$P(N) \approx e^{-m(m-1)/(2n)}$, so even odds arrive near $m \approx 1.18 \sqrt{n}$. The
square root is the whole engineering content: each extra bit of hash doubles $n$ but
multiplies the safe number of keys by only about $1.41$, so safety against collisions is
bought at half the rate the bit count suggests.

Where it stops: everything above assumed all $n^{m}$ assignments equally likely. A real
hash is not uniform, and the effect is one-directional — non-uniformity raises the
collision probability. The number computed here is the best case, so treating it as an
estimate is optimistic and treating it as a lower bound is safe.
''',
                },
            ],
            "numeric": [
                {
                    "title": "Two courses, one union",
                    "minutes": 5,
                    "brief": r'''
One rule, three numbers already in the right form. The only thing this can catch you on
is whether you subtract the overlap or add it.
''',
                    "prompt": "What is the probability that a student picked uniformly at random has taken at least one of the two courses?",
                    "note": "Give a probability between 0 and 1, to three decimal places.",
                    "figure": "A cohort is surveyed. 62 per cent of the students have written a program that uses a "
                              "hash table, 35 per cent have written one that uses a balanced tree, and 21 per cent "
                              "have written both. One student is picked uniformly at random.",
                    "given": [
                        {"label": r"$P(A)$, hash table", "value": "0.62"},
                        {"label": r"$P(B)$, balanced tree", "value": "0.35"},
                        {"label": r"$P(A \cap B)$, both", "value": "0.21"},
                    ],
                    "aside": "The two events are not disjoint — the 21 per cent are in both — so the "
                             "addition axiom does not apply on its own.",
                    "answer": 0.76,
                    "tol": 0.005,
                    "hint": r"$P(A \cup B) = P(A) + P(B) - P(A \cap B)$.",
                    "wrong": "If you got 0.97 you added the two totals without the correction, which counts "
                             "every one of the 21 per cent twice.",
                    "why": r'''
$P(A \cup B) = 0.62 + 0.35 - 0.21 = 0.76$.

The subtraction is not a fudge factor. Each of the 21 per cent who wrote both appears
once inside the 62 and once inside the 35, so the raw sum of $0.97$ contains them twice;
removing one copy leaves each student counted exactly once. The remaining $0.24$ is the
fraction who have used neither, and the four cells — both $0.21$, hash table only $0.41$,
tree only $0.14$, neither $0.24$ — total $1.00$, which is the check worth doing before
you write the number down.
''',
                },
                {
                    "title": "A PIN with a repeated digit",
                    "minutes": 7,
                    "brief": r'''
"At least one" again, and again the direct count is a mess: a repeat could be any of six
pairs of positions, and those events overlap. Count what has to fail instead.
''',
                    "prompt": "What is the probability that the PIN contains at least one repeated digit?",
                    "note": "Give a probability between 0 and 1, to three decimal places.",
                    "figure": "A four-digit PIN is drawn uniformly at random from the 10 000 strings 0000 to 9999. "
                              "Leading zeros are allowed, so every one of the 10 000 strings is equally likely.",
                    "given": [
                        {"label": "Size of the sample space", "value": "10 000"},
                        {"label": "Digits available at each position", "value": "10"},
                        {"label": "Length of the PIN", "value": "4"},
                    ],
                    "aside": "Count the PINs whose four digits are all different, using the ordered "
                             "selection rule, then use the complement.",
                    "answer": 0.496,
                    "tol": 0.001,
                    "hint": r"All-different PINs number $10 \times 9 \times 8 \times 7$.",
                    "wrong": "If you got 0.504 you computed the probability that the digits are all "
                             "different — the complement of what was asked. If you got 0.6 you added the "
                             "six pairwise-equality probabilities without correcting for their overlap.",
                    "why": r'''
The four digits are all different in $10 \times 9 \times 8 \times 7 = 5040$ ways, so

$$P(\text{distinct}) = \frac{5040}{10000} = 0.504, \qquad
P(\text{repeat}) = 1 - 0.504 = 0.496 .$$

Very nearly a coin flip, which surprises most people: a repeat feels like a coincidence,
and half of all PINs have one. That is the birthday effect on a very small scale — four
items in ten buckets, with $C(4,2) = 6$ pairs able to collide.

The direct route is available and instructive to compare. "At least one repeat" is the
union of six pairwise-equality events, each of probability $1/10$; the naive sum gives
$0.6$, which is wrong by more than a fifth because the six events overlap heavily — a PIN
like 7777 sits in all six at once.
''',
                },
                {
                    "title": "Divisible by three or by five",
                    "minutes": 8,
                    "brief": r'''
An equally likely model over a thousand outcomes, and an event that is a union of two
overlapping ones. Both counts have to be worked out before the rule can be applied.
''',
                    "prompt": "What is the probability that the number drawn is divisible by 3 or by 5?",
                    "note": "Give a probability between 0 and 1, to three decimal places.",
                    "figure": "An integer is drawn uniformly at random from 1 to 1000 inclusive. Let A be the event "
                              "that it is divisible by 3 and B the event that it is divisible by 5. 'Or' here is the "
                              "inclusive or: a number divisible by both still counts.",
                    "given": [
                        {"label": "Size of the sample space", "value": "1000"},
                        {"label": "Multiples of 3 up to 1000", "value": "333"},
                        {"label": "Multiples of 5 up to 1000", "value": "200"},
                    ],
                    "aside": "The overlap is the multiples of 15, not the multiples of 8 and not the "
                             "multiples of 3 times the multiples of 5.",
                    "answer": 0.467,
                    "tol": 0.0005,
                    "hint": r"$|A \cup B| = |A| + |B| - |A \cap B|$, and an integer divisible by both 3 and 5 is divisible by 15.",
                    "wrong": "If you got 0.533 you added the two counts and forgot the overlap. If you got "
                             "0.408 you took the intersection to be the multiples of 8, which is what "
                             "adding the two divisors rather than taking their least common multiple gives.",
                    "why": r'''
There are $333$ multiples of $3$ up to $1000$ and $200$ multiples of $5$. An integer
divisible by both is divisible by their least common multiple $15$, and there are $66$ of
those. So

$$|A \cup B| = 333 + 200 - 66 = 467, \qquad P(A \cup B) = \frac{467}{1000} = 0.467 .$$

Inclusion-exclusion is being used here on counts rather than on probabilities, which is
legitimate precisely because the equally likely model makes probability a count divided
by a fixed constant — subtracting the overlap upstairs is the same operation as
subtracting it after dividing.

Two traps worth naming. The overlap is the multiples of $15$ because $15$ is the least
common multiple of $3$ and $5$; for $4$ and $6$ the overlap would be the multiples of
$12$, not $24$, and using the product there loses half the overlap. And the three counts
are not exact fractions of $1000$ — there are $333$ multiples of $3$, not $333.33$ — so
working with $1/3 + 1/5 - 1/15 = 0.4667$ gives a number that is close but not the answer
to the question actually asked.
''',
                },
                {
                    "title": "Ten requests, fifty shards",
                    "minutes": 10,
                    "brief": r'''
Nothing here can be looked up. The count of favourable outcomes has to be built from the
ordered-selection rule first, and only then divided and complemented.
''',
                    "prompt": "What is the probability that at least two of the ten requests land on the same shard?",
                    "note": "Give a probability between 0 and 1, to three decimal places.",
                    "figure": "A load balancer hashes 10 distinct request ids across 50 shards. Model the hash as "
                              "ideal: every one of the 50^10 assignments of the ten requests to shards is equally "
                              "likely. A collision means two or more requests landing on the same shard.",
                    "given": [
                        {"label": "Requests to place", "value": "10"},
                        {"label": "Shards available", "value": "50"},
                        {"label": "Size of the sample space", "value": "50^10"},
                    ],
                    "aside": "Count the assignments that use ten different shards: 50 choices for the "
                             "first request, 49 for the second, and so on down to 41 for the tenth.",
                    "answer": 0.618,
                    "tol": 0.002,
                    "hint": r"The probability of no collision is $\dfrac{50 \times 49 \times \cdots \times 41}{50^{10}}$, and the question asks for its complement.",
                    "wrong": "If you got 0.382 you stopped at the probability of no collision, which is the "
                             "complement of what was asked. If you got 0.9 you reported the union bound over "
                             "the 45 colliding pairs; that is a true upper bound and it overshoots badly here.",
                    "why": r'''
The ten requests occupy ten different shards in $50 \times 49 \times \cdots \times 41$
ways out of $50^{10}$, so the probability of no collision is

$$\left(\frac{50}{50}\right) \left(\frac{49}{50}\right) \cdots
\left(\frac{41}{50}\right) = 0.3817,$$

and the probability of at least one collision is $1 - 0.3817 = 0.6183$.

Ten items into fifty boxes and a collision is more likely than not. The reason is the
number of pairs: there are $C(10,2) = 45$ pairs of requests that could collide, each with
probability $1/50$, and $45/50$ is already close to $1$ — the union bound gives $0.9$,
which is loose but points the right way. The intuition that fails is the one that
compares $10$ against $50$; the quantity that matters is $m^{2}$ against $n$, which is
$100$ against $50$.

The approximation $e^{-m(m-1)/(2n)} = e^{-45/50} = 0.4066$ is in the right region and
about six per cent high, because $1 - x \approx e^{-x}$ errs in one direction and the
error compounds over ten factors. It is good enough for sizing a table and not good
enough to quote as the answer.
''',
                },
            ],
            "blanks": {
                "title": "At least one six, line by line",
                "minutes": 9,
                "caption": "the complement rule doing the work twice, on the problem that started the subject",
                "lang": "text",
                "brief": r'''
In the 1650s the Chevalier de Méré was betting on two propositions he believed were
equivalent: at least one six in four rolls of one die, and at least one double six in
twenty-four rolls of two dice. He won on the first and lost on the second, and could not
see why. Both are "at least one", both are counted the same way, and the arithmetic below
is what separates them.

Each rolled sequence is one outcome, and all sequences are equally likely, so every line
is a count divided by a count.
''',
                "listing": """at least one six in four rolls of one fair die
---------------------------------------------

  sample space    S     = every ordered 4-tuple of faces
                        = 6 * 6 * 6 * 6           = ___ outcomes

  event           A     = "at least one six"
  complement      A^c   = "no six on any of the four rolls"

  count of A^c          = ___ ^ 4                 faces that are not a six
                        = 625

  P(A^c)                = 625 / 1296              = 0.4823
  P(A)                  = ___                     the complement rule
                        = 0.5177                  a shade better than even

at least one double six in twenty-four rolls of two dice
--------------------------------------------------------

  sample space    S     = 36 ^ 24                 ordered outcomes
  no double six         = ___ ^ 24                pairs that are not (6,6)

  P(no double six)      = (35/36) ^ 24            = 0.5086
  P(at least one)       = ___                     = 0.4914
                                                  a shade worse than even
""",
                "blanks": [
                    {
                        "prompt": "Four rolls, six faces each, order recorded. How many outcomes?",
                        "hole": "?",
                        "opts": ["24", "360", "1296", "4096"],
                        "a": 2,
                        "why": "The multiplication principle gives $6^{4} = 1296$. The value 24 is $6 \\times 4$, "
                               "which counts rolls rather than sequences; 4096 is $4^{6}$, the exponent and the "
                               "base swapped; 360 is $6 \\times 5 \\times 4 \\times 3$, which would be right only "
                               "if a face could not repeat — and repeats are exactly what this question is about.",
                    },
                    {
                        "prompt": "How many faces on one die are not a six?",
                        "hole": "?",
                        "opts": ["5", "6", "4", "1"],
                        "a": 0,
                        "why": "Five of the six faces avoid the six, so a four-roll sequence with no six at all "
                               "can be built in $5^{4} = 625$ ways. Using 6 would count every sequence and make "
                               "the probability of avoiding a six equal to 1; using 1 counts only the single "
                               "sequence of all ones.",
                    },
                    {
                        "prompt": "$P(A^{c}) = 0.4823$. What is $P(A)$?",
                        "hole": "?",
                        "opts": ["1 - 0.4823", "1 / 0.4823", "4 * 0.4823", "0.4823 / 2"],
                        "a": 0,
                        "why": "$A$ and $A^{c}$ are disjoint and together they are the whole sample space, so "
                               "their probabilities sum to 1 and $P(A) = 1 - 0.4823 = 0.5177$. Dividing gives "
                               "$2.07$, which is not a probability at all, and multiplying by the number of rolls "
                               "is the additive error that reaches $1$ after six rolls and keeps going.",
                    },
                    {
                        "prompt": "Of the 36 ordered face-pairs on two dice, how many are not the double six?",
                        "hole": "?",
                        "opts": ["35", "30", "25", "34"],
                        "a": 0,
                        "why": "Exactly one of the 36 pairs is $(6,6)$, so 35 survive. The value 25 is the count "
                               "of pairs with no six on either die, which answers a different question, and 30 "
                               "would be the count if a whole row of six pairs were excluded rather than one.",
                    },
                    {
                        "prompt": "The probability of no double six anywhere in the twenty-four rolls is $0.5086$. What is the probability of at least one?",
                        "hole": "?",
                        "opts": ["24 / 36", "1 - 0.5086", "24 * (1/36)", "1 / 0.5086"],
                        "a": 1,
                        "why": "The complement rule again: $1 - 0.5086 = 0.4914$, just under even money. The "
                               "additive answer $24/36 = 0.667$ is the same overcounting error as before, and it "
                               "is what made de Méré expect the two bets to behave alike — $4 \\times "
                               "1/6$ and $24 \\times 1/36$ are both $2/3$, while the true values straddle a half "
                               "and sit on opposite sides of the break-even line.",
                    },
                ],
            },
            "quiz": {
                "title": "Does the model hold up",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Two fair six-sided dice are rolled and both faces recorded. How large is the sample space, and what is the probability that the two faces sum to 7?",
                        "opts": [
                            r"$11$ outcomes, and $P = 1/11$",
                            r"$12$ outcomes, and $P = 1/6$",
                            r"$36$ outcomes, and $P = 1/12$",
                            r"$36$ outcomes, and $P = 1/6$",
                        ],
                        "a": 3,
                        "why": (
                            r"Recording both faces gives ordered pairs, so there are $6 \times 6 = 36$ equally "
                            r"likely outcomes. Six of them — $(1,6)$ through $(6,1)$ — sum to 7, so the probability "
                            r"is $6/36 = 1/6$. Taking the sample space to be the eleven possible sums is the classic "
                            r"error: those sums are not equally likely, so dividing by 11 divides by the wrong "
                            r"thing."
                        ),
                    },
                    {
                        "q": "A fair coin is tossed five times. What is the probability of at least one head?",
                        "opts": [
                            r"$31/32$",
                            r"$1/32$",
                            r"$5/32$",
                            r"$1/2$",
                        ],
                        "a": 0,
                        "why": (
                            r"'At least one' has many ways to happen and exactly one way to fail. The complement is "
                            r"'no heads at all', the single sequence TTTTT, with probability $(1/2)^5 = 1/32$, so "
                            r"the answer is $1 - 1/32 = 31/32$. Counting the successful cases directly means summing "
                            r"five separate terms to arrive at the same number."
                        ),
                    },
                    {
                        "q": r"In a cohort, $P(A) = 0.6$ take algorithms, $P(B) = 0.5$ take statistics, and $P(A \cap B) = 0.3$ take both. What is $P(A \cup B)$?",
                        "opts": [
                            r"$1.1$",
                            r"$0.3$",
                            r"$0.8$",
                            r"$0.9$",
                        ],
                        "a": 2,
                        "why": (
                            r"Adding the two totals gives $1.1$, which is already impossible — no probability "
                            r"exceeds 1 — because the $0.3$ who take both were counted once in each. Subtracting the "
                            r"overlap exactly once repairs it: $0.6 + 0.5 - 0.3 = 0.8$. The two events are not "
                            r"disjoint, so the addition axiom does not apply on its own."
                        ),
                    },
                    {
                        "q": "Which of these assignments of mass to the three outcomes of a sample space is a valid probability model?",
                        "opts": [
                            r"$0.5$, $0.3$, $0.1$",
                            r"$0.2$, $0.3$, $0.5$",
                            r"$0.5$, $0.6$, $-0.1$",
                            r"$0.4$, $0.4$, $0.4$",
                        ],
                        "a": 1,
                        "why": (
                            r"A model must give every outcome a non-negative mass and total exactly 1 across the "
                            r"whole sample space; $0.2 + 0.3 + 0.5 = 1$ with nothing negative. The set summing to "
                            r"$0.9$ leaves mass unaccounted for, the set containing $-0.1$ breaks non-negativity "
                            r"even though it totals 1, and three lots of $0.4$ total $1.2$."
                        ),
                    },
                    {
                        "q": "Why is 'every outcome is equally likely' a modelling assumption rather than a consequence of the axioms?",
                        "opts": [
                            "Because the axioms forbid equal masses unless the sample space is infinite",
                            "Because a sample space can never be listed exhaustively",
                            "Because the probability of an individual outcome must always be irrational",
                            "Because the axioms constrain how masses combine but say nothing about which outcomes deserve equal mass",
                        ],
                        "a": 3,
                        "why": (
                            r"The three axioms say the masses are non-negative, total one, and add over disjoint "
                            r"events. None of them decides that a die's six faces each carry $1/6$ — that comes from "
                            r"a claim about the die being physically symmetric, which is a statement about the world "
                            r"and can simply be false. A loaded die satisfies all three axioms perfectly well."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Conditional probability and independence",
            "summary": (
                "Rescaling to the world where something already happened, and the "
                "difference between events that cannot coincide and events that tell "
                "you nothing about each other."
            ),
            "concepts": [
                r"$P(A | B) = P(A \cap B)/P(B)$ renormalises to the outcomes where $B$ occurred; when $P(B) = 0$ it is undefined, not zero",
                r"The multiplication rule $P(A \cap B) = P(A | B) P(B)$ chains, which is how sampling without replacement and any sequential experiment are built",
                r"Independence means $P(A \cap B) = P(A) P(B)$; disjoint events with non-zero probability are the opposite of independent, since one occurring rules the other out",
                r"The law of total probability partitions the sample space and weights the branches: $P(B) = \sum_i P(B | A_i) P(A_i)$",
                r"$P(A | B)$ and $P(B | A)$ share a numerator but divide by different things, so they are equal only by coincidence — reversing them is a fallacy with a body count",
                'Conditioning is renormalisation, and $P(\\cdot | B)$ satisfies the same three axioms, so every theorem derived from them holds for conditional probabilities without being re-proved',
                '$P(A^{c} | B) = 1 - P(A | B)$ is exact, but $P(A | B^{c}) \\ne 1 - P(A | B)$ — the complement is over the event being measured, never over the one you were told',
                'Independence is a property of the numbers, not of the mechanism: ace and spade are independent in a full deck and dependent once one unrelated card is removed from it',
                'Pairwise independence is not mutual independence — two fair coins and the event that they agree are independent in every pair and rigid in all three, and mutual independence is $2^{n} - n - 1$ separate equations',
            ],
            "read": [
                {
                    "title": 'The world where B already happened, and the rule that survives the move',
                    "minutes": 13,
                    "body": r'''
Module 1 left a cohort on the table: $200$ students, $120$ who have taken algorithms,
$100$ who have taken statistics, $60$ who have taken both. Pick one at random and the
probability they have taken algorithms is $120/200 = 0.60$.

Now someone tells you the student they picked has taken statistics. What is the
probability they have taken algorithms?

There are $100$ statistics students and $60$ of them also took algorithms, so the
answer is $60/100 = 0.60$ — **exactly what it was before you were told anything**. That
is not a coincidence and it is not a general rule. It is a numerical accident of the
three numbers in the cohort, and this unit is about what makes it happen and what
happens when it does not.

## Conditioning is renormalisation, and it is not a new axiom

Fix an event $B$ with $P(B) > 0$. Being told that $B$ occurred does two things: it
discards every outcome outside $B$, and it rescales what is left so the surviving mass
totals one again. Both are in one line.

$$P(A | B) = \frac{P(A \cap B)}{P(B)}$$

The numerator is the part of $A$ that survived the news. The denominator is the total
mass that survived, and dividing by it is the rescaling. Nothing here is postulated —
it is a definition, and the reason it is *the* definition rather than one of many is
what follows.

Read $P(\cdot | B)$ as a probability model in its own right, defined on the same sample
space, and check it against module 1's three axioms.

**A1.** $P(A | B) = P(A \cap B)/P(B)$ is a non-negative number over a positive one, so
it is non-negative.

**A2.** $P(S | B) = P(S \cap B)/P(B) = P(B)/P(B) = 1$.

**A3.** If $A_1$ and $A_2$ are disjoint then $A_1 \cap B$ and $A_2 \cap B$ are disjoint
too, so the old A3 applies to them and

$$P(A_1 \cup A_2 | B) = \frac{P(A_1 \cap B) + P(A_2 \cap B)}{P(B)}
= P(A_1 | B) + P(A_2 | B) .$$

That is the whole payoff, and it is worth more than it looks. $P(\cdot | B)$ satisfies
the same three axioms, so **every theorem module 1 derived from them holds for
conditional probabilities without being re-proved**. The complement rule becomes

$$P(A^{c} | B) = 1 - P(A | B) ,$$

monotonicity becomes $P(A | B) \le P(C | B)$ whenever $A \subseteq C$, and
inclusion-exclusion becomes
$P(A \cup C | B) = P(A | B) + P(C | B) - P(A \cap C | B)$. None of these is a new fact
to memorise. They are old facts read in a smaller world.

## The complement that does not survive

Here is where the transfer stops, and it is the most common error in the subject.

The bar in $P(A^{c} | B) = 1 - P(A | B)$ is over $A$. The complement is taken on the
**left** of the bar, the event being measured. Nothing at all follows about complementing
the event on the **right**, the one you were told. In general

$$P(A | B^{c}) \ne 1 - P(A | B) .$$

Take $P(A) = 0.5$, $P(B) = 0.4$, $P(A \cap B) = 0.3$. Then

$$P(A | B) = \frac{0.3}{0.4} = 0.75, \qquad 1 - P(A | B) = 0.25 ,$$

while $A \cap B^{c}$ has probability $0.5 - 0.3 = 0.2$ and $B^{c}$ has probability
$0.6$, so

$$P(A | B^{c}) = \frac{0.2}{0.6} = \frac{1}{3} \approx 0.333 .$$

$0.333$ is not $0.25$. The two conditionals live in different worlds — one inside $B$,
one outside it — and there is no reason for them to add to anything in particular. What
*does* always hold is the pair inside a single world: $P(A | B) + P(A^{c} | B) = 1$,
because those two split the world $B$ between them.

## Worked: two machines, forwards and backwards

Machine 1 makes $70$ per cent of a part with a $2$ per cent defect rate; machine 2 makes
$30$ per cent with a $5$ per cent defect rate. Write $M_1$, $M_2$ for the sources and
$D$ for "defective".

Forwards, the law of total probability partitions the output and weights the branches:

$$P(D) = P(D | M_1)P(M_1) + P(D | M_2)P(M_2)
= 0.02 \times 0.70 + 0.05 \times 0.30 = 0.014 + 0.015 = 0.029 .$$

So $2.9$ per cent of parts are defective. Averaging $2$ and $5$ per cent to get $3.5$
assumes the machines make equal numbers, and they do not.

Backwards is the question a factory actually asks. A defective part is in front of you;
where did it come from? The numerator is the branch you want and the denominator is the
total you computed:

$$P(M_2 | D) = \frac{P(D | M_2)P(M_2)}{P(D)} = \frac{0.015}{0.029}
= \frac{15}{29} \approx 0.517 .$$

Machine 2 makes $30$ per cent of the parts and **$51.7$ per cent of the defects**. Notice
what just happened: $P(D | M_2) = 0.05$ and $P(M_2 | D) = 0.517$, two numbers differing
by a factor of ten, and swapping them is the fallacy the concepts list warns about. The
reversal above is Bayes' rule, arrived at with nothing but the definition and the
partition — module 10 will give it a name and a great deal more work to do.

## Independence is arithmetic, not physics

$A$ and $B$ are **independent** when

$$P(A \cap B) = P(A)P(B) ,$$

equivalently, when $P(B) > 0$, when $P(A | B) = P(A)$: being told $B$ moves nothing.

Now return to the cohort. $P(A) = 0.60$, $P(B) = 0.50$, $P(A \cap B) = 60/200 = 0.30$,
and $0.60 \times 0.50 = 0.30$. The cohort was independent all along, which is why
conditioning on statistics returned $0.60$ unchanged. Move a single student — make it
$70$ who took both — and the four cells become $50$, $30$, $70$, $50$. Now
$P(A \cap B) = 0.35$ against a product of $0.30$, and

$$P(A | B) = \frac{70}{100} = 0.70, \qquad P(B | A) = \frac{70}{120} \approx 0.583 .$$

Knowing about statistics moves algorithms from $0.60$ to $0.70$, the two conditionals
disagree, and nothing about the world changed except one student's transcript.

That is the point worth carrying: independence is a property of the *numbers*, not of
the mechanism. A cleaner demonstration uses a deck. "The card is an ace" and "the card
is a spade" are independent in a full deck, since
$P(\text{ace})P(\text{spade}) = \frac{4}{52} \times \frac{13}{52} = \frac{1}{52}$,
which is exactly $P(\text{ace of spades})$. Remove one card — the two of clubs, which is
neither an ace nor a spade — and independence is gone:

$$\frac{4}{51} \times \frac{13}{51} = \frac{52}{2601} \approx 0.019992, \qquad
P(\text{ace of spades}) = \frac{1}{51} \approx 0.019608 .$$

No physical relationship between suits and ranks was disturbed. A card was removed from
a box. Independence is a coincidence of ratios that the world is under no obligation to
maintain.

## The mistake, and why it is tempting

Disjoint and independent sound like synonyms for "unrelated", and they are close to
opposites. If $A$ and $B$ are disjoint with $P(A), P(B) > 0$, then $P(A \cap B) = 0$
while $P(A)P(B) > 0$, so they are dependent — maximally so, because learning that $A$
occurred tells you with certainty that $B$ did not. The word "exclusive" is doing the
damage: exclusive events are *strongly* informative about each other, and independent
events are the ones that say nothing.

## Where it stops

Two limits, both easy to walk past.

**$P(B) = 0$ makes the definition undefined, not zero.** The formula divides by
$P(B)$. For a continuous variable every single outcome has probability zero, so
conditioning on "the arrival was at exactly $10{:}03$" is asking for $0/0$; module 4
meets this properly.

**Pairwise independence is not mutual independence.** Toss two fair coins. Let $A$ be
"the first is heads", $B$ "the second is heads", $C$ "the two agree". Each has
probability $\frac{1}{2}$, and every pair is independent: $P(A \cap B)$, $P(A \cap C)$
and $P(B \cap C)$ all equal $\frac{1}{4}$, matching every product. Yet

$$P(A \cap B \cap C) = P(\text{HH}) = \frac{1}{4}, \qquad
P(A)P(B)P(C) = \frac{1}{8} .$$

Checking the pairs is not enough — and it is worse than incomplete, because here any two
of the three genuinely carry no information about each other while all three together
are rigid: $A$ and $B$ determine $C$ outright. Mutual independence demands the product
rule for **every** sub-collection, which is $2^{n} - n - 1$ separate equations for $n$
events. Module 6 will assume it for a whole sequence of simulated draws, and the
assumption is doing more work than the phrase "independent trials" suggests.
''',
                },
            ],
            "derive": [
                {
                    "title": 'The complement that survives conditioning, and the one that does not',
                    "minutes": 12,
                    "vars": ['P_A', 'P_B', 'P_AB', 'P_AcB'],
                    "brief": r'''
Conditioning on $B$ makes $P(\cdot | B)$ a probability model in its own right, and every
theorem about the axioms then applies to it. This derivation gets the conditional
complement rule out of that, and then shows precisely which neighbouring statement it
does *not* license.

Write $P_{A}$ for $P(A)$, $P_{B}$ for $P(B)$, $P_{AB}$ for $P(A \cap B)$, and $P_{AcB}$
for $P(A^{c} \cap B)$ — the part of $B$ lying outside $A$. Assume $P_{B} > 0$ and
$P_{B} < 1$ throughout.
''',
                    "steps": [
                        {
                            "prompt": '$B$ splits into the part inside $A$ and the part outside it, and those two share no outcome. Write $P_{B}$ in terms of $P_{AB}$ and $P_{AcB}$.',
                            "answer": 'P_{AB} + P_{AcB}',
                            "placeholder": 'the third axiom, on two pieces of B',
                            "hint": 'This is A3 again: $B = (A \\cap B) \\cup (A^{c} \\cap B)$, and the two pieces are disjoint by construction.',
                        },
                        {
                            "prompt": 'Divide the definition through. Write $P(A^{c} | B) = P_{AcB}/P_{B}$ using only $P_{AB}$ and $P_{B}$.',
                            "answer": '\\frac{P_{B} - P_{AB}}{P_{B}}',
                            "hint": 'Rearrange step 1 to get $P_{AcB}$ on its own, then divide by $P_{B}$.',
                            "deconstruct": [
                                'Step 1 gives $P_{AcB} = P_{B} - P_{AB}$.',
                                'The definition of conditional probability divides that by $P_{B}$.',
                                'Nothing else is needed; the answer is a single fraction.',
                            ],
                        },
                        {
                            "prompt": 'Add $P(A | B) = P_{AB}/P_{B}$ to the previous line and simplify. What is $P(A | B) + P(A^{c} | B)$?',
                            "answer": '1',
                            "hint": 'The two fractions share the denominator $P_{B}$, and their numerators add to $P_{B}$.',
                            "deconstruct": [
                                '$\\frac{P_{AB}}{P_{B}} + \\frac{P_{B} - P_{AB}}{P_{B}} = \\frac{P_{AB} + P_{B} - P_{AB}}{P_{B}}$.',
                                'The $P_{AB}$ terms cancel, leaving $P_{B}/P_{B}$.',
                                'So conditioning keeps the complement rule intact — the bar is over $A$, and $A$ with $A^{c}$ splits the world $B$.',
                            ],
                        },
                        {
                            "prompt": 'Now the neighbouring statement. Condition on $B^{c}$ instead. Since $P(A \\cap B^{c}) = P_{A} - P_{AB}$ and $P(B^{c}) = 1 - P_{B}$, write $P(A | B^{c})$ in terms of $P_{A}$, $P_{AB}$ and $P_{B}$.',
                            "answer": '\\frac{P_{A} - P_{AB}}{1 - P_{B}}',
                            "placeholder": 'a ratio built from the three named quantities',
                            "hint": 'Apply the definition with $B^{c}$ in the role of the conditioning event; both numerator and denominator are given to you in the prompt.',
                        },
                        {
                            "prompt": 'Put numbers in: $P_{A} = 0.5$, $P_{B} = 0.4$, $P_{AB} = 0.3$. Evaluate the expression from step 4, as an exact fraction.',
                            "answer": '\\frac{1}{3}',
                            "hint": 'The numerator is $0.5 - 0.3 = 0.2$ and the denominator is $1 - 0.4 = 0.6$.',
                            "deconstruct": [
                                '$P(A | B^{c}) = \\frac{0.2}{0.6} = \\frac{1}{3} \\approx 0.333$.',
                                'Meanwhile $P(A | B) = \\frac{0.3}{0.4} = 0.75$, so $1 - P(A | B) = 0.25$.',
                                '$0.333 \\ne 0.25$: complementing the event on the right of the bar is not the complement rule, and this is the counterexample.',
                            ],
                        },
                        {
                            "prompt": 'Finally, suppose $A$ and $B$ are independent, so $P_{AB} = P_{A}P_{B}$. Substitute that into $P(A \\cap B^{c}) = P_{A} - P_{AB}$ and factorise. Write $P(A \\cap B^{c})$ in terms of $P_{A}$ and $P_{B}$.',
                            "answer": 'P_{A}(1 - P_{B})',
                            "hint": 'Substitute, then take the common factor $P_{A}$ outside the bracket.',
                            "deconstruct": [
                                '$P_{A} - P_{A}P_{B} = P_{A}(1 - P_{B})$.',
                                'And $1 - P_{B}$ is $P(B^{c})$, so this reads $P(A \\cap B^{c}) = P(A)P(B^{c})$.',
                                'Independence therefore survives complementing either event, which the definition never said outright.',
                            ],
                        },
                    ],
                    "closing": r'''
Two results that look alike and are not. $P(A | B) + P(A^{c} | B) = 1$ is exact, always,
and follows from conditioning being a probability model. $P(A | B) + P(A | B^{c}) = 1$
is not a theorem, and step 5 is a counterexample with the numbers to prove it: $0.75$
and $0.333$ sum to $1.083$.

Step 6 is the small result the concepts list assumes without stating. If $A$ is
independent of $B$ it is independent of $B^{c}$, and by symmetry $A^{c}$ is independent
of both. Independence is a property of the *partition* into $B$ and $B^{c}$, not of the
particular one you happened to name — which is why a simulation may condition on either
branch of a coin flip without disturbing anything else it is measuring.
''',
                },
            ],
            "quiz": {
                "title": "What the condition changes",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A card is drawn from a standard 52-card deck. Given that it is a face card (jack, queen or king), what is the probability that it is a king?",
                        "opts": [
                            r"$1/13$",
                            r"$4/52$",
                            r"$1/3$",
                            r"$3/4$",
                        ],
                        "a": 2,
                        "why": (
                            r"Conditioning discards every outcome outside the event you were told occurred and "
                            r"rescales what remains. Twelve face cards survive and four of them are kings, so the "
                            r"probability is $4/12 = 1/3$. The unconditional $4/52 = 1/13$ throws away the "
                            r"information you were given."
                        ),
                    },
                    {
                        "q": "Two cards are drawn from a 52-card deck without replacement. Which expression gives the probability that both are aces?",
                        "opts": [
                            r"$\frac{4}{52} \cdot \frac{3}{51}$",
                            r"$\frac{4}{52} \cdot \frac{4}{52}$",
                            r"$\frac{4}{52} + \frac{3}{51}$",
                            r"$\frac{4}{52} \cdot \frac{4}{51}$",
                        ],
                        "a": 0,
                        "why": (
                            r"The multiplication rule gives $P(A_1 \cap A_2) = P(A_1) P(A_2 | A_1)$. Once the first "
                            r"ace is gone the deck holds 51 cards and only 3 aces, so the conditional factor is "
                            r"$3/51$. Squaring $4/52$ would be correct only with replacement, which is precisely "
                            r"what makes two draws independent."
                        ),
                    },
                    {
                        "q": r"Events $A$ and $B$ each have probability $0.4$ and cannot both occur. Are they independent?",
                        "opts": [
                            "Yes — mutually exclusive events are always independent",
                            r"Yes, provided both probabilities are below $0.5$",
                            r"It cannot be decided without knowing $P(A \cup B)$",
                            r"No — $P(A \cap B) = 0$ while $P(A)P(B) = 0.16$",
                        ],
                        "a": 3,
                        "why": (
                            r"Independence is the equation $P(A \cap B) = P(A)P(B)$. Here the intersection is empty "
                            r"so the left side is $0$, while the right side is $0.16$. Mutually exclusive events with "
                            r"non-zero probability are as far from independent as it is possible to get: learning "
                            r"that $A$ happened tells you with certainty that $B$ did not."
                        ),
                    },
                    {
                        "q": "Two machines make the same part. Machine 1 makes 70% of them with a 2% defect rate; machine 2 makes 30% with a 5% defect rate. What fraction of all parts are defective?",
                        "opts": [
                            "3.5%",
                            "2.9%",
                            "7%",
                            "0.1%",
                        ],
                        "a": 1,
                        "why": (
                            r"Split the output by machine — that is a partition of the sample space — and weight "
                            r"each defect rate by the share it governs: $0.70 \times 0.02 + 0.30 \times 0.05 = "
                            r"0.014 + 0.015 = 0.029$. Averaging 2% and 5% without the weights gives 3.5% and "
                            r"silently assumes the two machines make equal numbers of parts."
                        ),
                    },
                    {
                        "q": r"Why is $P(A | B)$ generally different from $P(B | A)$?",
                        "opts": [
                            "Because conditional probabilities are never symmetric under any circumstances",
                            "Because one of the two is always the larger",
                            r"Because both have the numerator $P(A \cap B)$ but divide it by different quantities",
                            r"Because $P(A | B)$ counts outcomes while $P(B | A)$ counts events",
                        ],
                        "a": 2,
                        "why": (
                            r"Both are $P(A \cap B)$ over something: one divides by $P(B)$ and the other by $P(A)$, "
                            r"so they agree only when $P(A) = P(B)$ — or when the shared numerator is itself zero, "
                            r"which is why two disjoint events have both conditionals equal to $0$ however far apart "
                            r"their marginals are. Swapping them is the reasoning behind 'most "
                            r"accidents happen close to home, so driving close to home is dangerous' — and the "
                            r"correct conversion from one to the other is exactly what Bayes' rule performs later in "
                            r"this course."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Discrete distributions from first principles",
            "summary": "Three distributions, built from their definitions rather than imported.",
            "concepts": [
                "A pmf assigns non-negative mass summing to one; a cdf is its running total",
                "Bernoulli(p) as the single-trial atom that binomial and geometric are built from",
                "Binomial(n, p) counts successes in n independent trials: C(n,k) p^k (1-p)^(n-k)",
                "Geometric(p) counts trials up to and including the first success — memoryless",
                "Expectation is linear whether or not the variables are independent",
                "Var(X) = E[(X - mu)^2] = E[X^2] - mu^2, and why the centred form loses less precision",
                "Exact integer binomial coefficients: multiply then divide, never factorial then divide",
            ],
            "read": [
                {
                    "title": 'One flaky test, and the three lists that count it',
                    "minutes": 14,
                    "body": r'''
A build server runs one integration test ten times every night. The test is flaky: on
any single run it fails with probability $0.3$, and the runs have nothing to do with
each other — a fresh container each time, no shared state, no cached artefacts. Here is
last night's log.

```text
    run       1  2  3  4  5  6  7  8  9  10
    result    .  F  .  .  F  .  .  .  F  .
```

Three failures out of ten. The question the on-call engineer actually asks is not "why
three" but "is three unusual?", and that cannot be answered from one number. It needs
the whole list — the probability of zero failures, of one, of two, of every count up to
ten — because "unusual" means "far out in that list". A list of probabilities indexed by
outcome is a **probability mass function**, and this module builds three of them out of
nothing but counting.

## One run is the atom

A single run fails or does not, so its mass function has two entries: $P(X = 1) = p$ and
$P(X = 0) = 1 - p$, here with $p = 0.3$. That is a **Bernoulli** variable. On its own it
is barely a distribution; its job is to be the piece the other two are assembled from.

Write down the probability of exactly the log above — failures on runs 2, 5 and 9,
successes on the other seven. The runs are independent, so the probability of the whole
sequence is the product of the ten single-run probabilities:

$$0.7 \times 0.3 \times 0.7 \times 0.7 \times 0.3 \times 0.7 \times 0.7 \times 0.7
\times 0.3 \times 0.7 = 0.3^{3}\,0.7^{7} \approx 0.002224 .$$

Multiplication is commutative, so nothing in that product remembers *where* the failures
fell. Every sequence with three F's and seven dots carries the same $0.002224$. And the
events "failures on runs 2, 5, 9", "failures on runs 1, 2, 3" and the rest are disjoint —
one night cannot be two of them — so module 1's third axiom says their probabilities add.
Adding a pile of equal numbers is counting:

$$P(X = 3) = (\text{number of such sequences}) \times 0.3^{3}\,0.7^{7} .$$

A sequence is fixed by choosing which three of the ten positions hold an F, and module 1
counted precisely that: $\binom{10}{3} = 120$. So

$$P(X = 3) = 120 \times 0.027 \times 0.0823543 = 0.266828 .$$

The general shape is the same two steps with letters. One specific arrangement has
probability $p^{k}(1-p)^{n-k}$, and there are $\binom{n}{k}$ arrangements, so

$$P(X = k) = \binom{n}{k} p^{k} (1-p)^{n-k} .$$

```python
def choose(n, k):
    """Exact integer C(n, k), built up multiplicatively."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def binomial_pmf(n, p, k):
    return choose(n, k) * p ** k * (1 - p) ** (n - k)


table = {k: binomial_pmf(10, 0.3, k) for k in range(11)}
for k in (2, 3, 4):
    print(f"P(X = {k}) = {table[k]:.6f}")
print(f"total mass  = {sum(table.values()):.12f}")
print(f"E[X]        = {sum(k * m for k, m in table.items()):.6f}")
```

That prints

```text
P(X = 2) = 0.233474
P(X = 3) = 0.266828
P(X = 4) = 0.200121
total mass  = 1.000000000000
E[X]        = 3.000000
```

So three failures is the single most likely night there is, and the answer to the on-call
question is that three is not unusual at all. Running totals answer the sharper version:
$P(X \le 3) = 0.6496$, and $P(X \ge 7) = 0.0106$. A running total of a mass function is a
**cumulative distribution function**, and it is a sum, not a new idea — which is why the
lab writes `binomial_cdf` as a loop over `binomial_pmf` and then checks that it never
dips.

## A different question about the same test

Do not fix the number of runs. Instead keep running until the test fails, and ask how
many runs that takes. To have the first failure on run $k$, the first $k-1$ runs must all
have passed and run $k$ must fail:

$$P(X = k) = (1-p)^{k-1} p, \qquad k = 1, 2, 3, \dots$$

There is no binomial coefficient here, and the absence is the content: only one sequence
gives a first failure on run $k$, because the positions of everything before it are
forced. This is the **geometric** distribution, and the lab counts trials *up to and
including* the first success, so its support starts at $k = 1$.

The masses do sum to one, and the check is a geometric series:
$\sum_{k \ge 1}(1-p)^{k-1}p = p/(1 - (1-p)) = 1$. The cumulative version needs no series
at all. $P(X > k)$ means the first $k$ runs all passed, which has probability $(1-p)^{k}$,
so

$$P(X \le k) = 1 - (1-p)^{k} .$$

At $p = 0.3$ that gives $P(X \le 5) = 1 - 0.7^{5} = 0.83193$, which agrees to the last
digit with summing the five masses. The lab's `geometric_cdf` uses the closed form and its
test compares it against the summed pmf at every $k$ from 1 to 11 — the two routes to one
number, which is the cheapest kind of check there is.

## The moments, derived rather than quoted

Expectation is $E[X] = \sum_k k\,P(X = k)$, and for the binomial that sum is unpleasant
head-on. Take it sideways. Write $X = I_1 + I_2 + \dots + I_{10}$, where $I_j$ is $1$ if
run $j$ failed and $0$ if it passed. Expectation is linear — and linear *whether or not*
the terms are independent, which is the fact doing the work here — so

$$E[X] = \sum_{j=1}^{10} E[I_j] = 10 \times 0.3 = 3 ,$$

since a $0/1$ variable has expectation equal to its probability of being $1$. The code
above prints exactly $3.000000$ from the eleven masses, by a completely different route.

The geometric mean comes from self-similarity. Let $\mu = E[X]$. The first run always
happens. With probability $p$ it fails and the count is $1$; with probability $1 - p$ it
passes and you are looking at the same problem again, one run further on. So

$$\mu = 1 + (1-p)\mu \quad \Longrightarrow \quad \mu = \frac{1}{p} .$$

At $p = 0.3$ the expected wait is $3.\overline{3}$ runs. The lab checks this against a
table truncated at $k_{\max}$, and the truncation is the thing to watch: at $p = 0.3$ the
first $40$ terms give $3.33331$ rather than $3.33333$, because the tail beyond $40$ was
discarded. The lab's own checks push $k_{\max}$ out to $400$ at $p = 0.25$, far enough
that the discarded tail is around $10^{-50}$ and the sum comes back exact. The $10^{-6}$
tolerance is there because a table that stops too early gives a wrong answer rather than a
noisy one, and the size of that error is set by a choice you make.

Variance is $\mathrm{Var}(X) = E[(X-\mu)^{2}]$, and expanding the square gives the
algebraically equal $E[X^{2}] - \mu^{2}$. Equal in algebra is not equal in floating point.

```python
xs = [1e7 + 0.1, 1e7 + 0.2, 1e7 + 0.3]
mass = 1 / 3
mu = sum(x * mass for x in xs)
centred = sum(mass * (x - mu) ** 2 for x in xs)
raw = sum(mass * x * x for x in xs) - mu * mu
print(f"centred form  : {centred!r}")
print(f"E[X^2] - mu^2 : {raw!r}")
```

```text
centred form  : 0.006666666741172473
E[X^2] - mu^2 : 0.0
```

The true variance is $0.00\overline{6}$. The uncentred form reports **exactly zero**: it
subtracts two numbers near $10^{14}$ whose difference is near $0.0067$, and double
precision has no digits left down there. The centred form subtracts first, while the
numbers are still close together, and keeps every digit. This is why the lab's `variance`
is specified about the mean.

## The mistake, and why it is tempting

Twenty machines sit in a rack, six of them running a bad firmware image. Pull ten at
random and count the bad ones. Ten trials, two outcomes each, and $6/20 = 0.3$ — the
binomial story fits the sentence perfectly, and it is the wrong distribution.

The binomial needs $p$ to be the same on every trial, and pulling *without replacement*
changes it: after one bad machine is drawn, the rack holds $5$ bad out of $19$, so the
next probability is $0.263$, not $0.3$. What the count follows is the hypergeometric
distribution, and the difference is not cosmetic.

```python
def choose(n, k):
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


N, K, n, p = 20, 6, 10, 0.3
binom = sum(choose(n, k) * p ** k * (1 - p) ** (n - k) for k in range(4))
hyper = sum(choose(K, k) * choose(N - K, n - k) for k in range(4)) / choose(N, n)
print(f"binomial       P(X <= 3) = {binom:.4f}   variance = {n * p * (1 - p):.4f}")
print(f"hypergeometric P(X <= 3) = {hyper:.4f}   variance = "
      f"{n * p * (1 - p) * (N - n) / (N - 1):.4f}")
```

```text
binomial       P(X <= 3) = 0.6496   variance = 2.1000
hypergeometric P(X <= 3) = 0.6858   variance = 1.1053
```

The spread is nearly halved. Sampling without replacement is self-correcting — draw too
many bad machines early and there are fewer left to draw — so the count clusters harder
around its mean than the binomial expects. The mistake is tempting because the words
"trial", "success" and "independent" all sound like descriptions of the story rather than
conditions on the arithmetic, and the story is genuinely identical. Independence is a
statement about the numbers, as module 2 insisted, and here the numbers move.

## Where these stop holding

**Constant $p$, and independence.** Both are assumptions about the mechanism that the
formula cannot check. A flaky test that fails more often when the CI machine is loaded
has neither, and the binomial will understate the tails: correlated failures cluster, and
clustered failures make "eight failures tonight" far more likely than the $0.001447$ the
formula assigns it.

**The geometric's memorylessness.** $P(X > m + k \mid X > m) = (1-p)^{k}$, free of $m$ —
seven passing runs tell you nothing about how much longer the wait is. That is a
consequence of independence, not a law of nature, and it is false of anything that wears
out or warms up. Module 4 meets the same property in continuous time.

**Exactness, and floating point.** `choose` in the lab is written as
`result = result * (n - i) // (i + 1)` rather than as a ratio of factorials, and the
reason is that the multiplicative form keeps a running product that is always divisible,
so it stays an exact `int` at every step, while $\binom{52}{5}$ built from
$52!$ discards its precision before dividing. The masses themselves are floats, and
$p^{k}$ for large $k$ and small $p$ underflows to zero — module 10 hits this hard enough
that its spam filter has to work in logs.

The lab for this module, **pmf, cdf and the first two moments**, asks you to build all of
this from the definitions: `choose` without `math.comb`, both pmfs and both cdfs, tables
over the support, and `expectation` and `variance` over any `{value: probability}` dict.
The tables are the point. They let you check $np$ and $np(1-p)$ against a sum you computed
yourself rather than against a formula somebody handed you.
''',
                },
            ],
            "quiz": {
                "title": "Mass, counting, and the moments that follow",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"A flaky test is run ten times, failing independently with probability $0.3$ each time. In $P(X = 3) = \binom{10}{3}(0.3)^{3}(0.7)^{7}$, what work is the coefficient $\binom{10}{3}$ doing?",
                        "opts": [
                            r"It counts the arrangements of three failures among ten runs, each carrying that same probability",
                            r"It corrects for the fact that the three failing runs might have occurred in any order, which makes each individual ordering more probable than it would otherwise be",
                            r"It rescales the eleven masses so that they add to one",
                            r"It accounts for the runs being independent of one another",
                        ],
                        "a": 0,
                        "whys": [
                            r"Each such arrangement has probability $0.3^{3}0.7^{7}$, they are disjoint, and adding 120 equal numbers is multiplication.",
                            r"Ordering does not change any single sequence's probability — the product $0.7 \times 0.3 \times 0.7 \cdots$ is commutative, so every arrangement is worth the same $0.002224$. The coefficient counts the arrangements; it does not reweight them.",
                            r"The masses add to one on their own once the coefficients are in place, and no separate normalising step happens. Treating $\binom{n}{k}$ as a fudge factor hides that it is a count of something you could list by hand.",
                            r"Independence is what licenses multiplying the ten single-run probabilities together in the first place, and it produces $0.3^{3}0.7^{7}$ — not the coefficient in front of it. A dependent sequence would break the product, not the count.",
                        ],
                        "why": r"""
The probability of one specific log — failures on runs 2, 5 and 9 — is the product of ten
independent single-run probabilities, which is $0.3^{3}0.7^{7} \approx 0.002224$, and
multiplication being commutative means every log with three failures is worth exactly the
same. Those logs are disjoint events, so the addition axiom says their probabilities add,
and adding 120 copies of one number is multiplying by 120. The coefficient is a count of
sequences and nothing else; $\binom{10}{3} = 120$ is a number you could in principle
obtain by listing them.
""",
                    },
                    {
                        "q": r"A geometric variable counts trials up to and including the first success, with $p = 0.3$. Why is there no binomial coefficient in $P(X = k) = (0.7)^{k-1}(0.3)$?",
                        "opts": [
                            r"Because the trials are dependent once you condition on the first success arriving late",
                            r"Because exactly one sequence produces a first success on trial $k$: everything before it is forced to be a failure",
                            r"Because the coefficient is present but equals one for every value of $k$ that the geometric distribution can take, and a factor of one is conventionally left out of the written formula",
                            r"Because the support is unbounded, and no finite count of arrangements exists",
                        ],
                        "a": 1,
                        "whys": [
                            r"The trials are independent throughout; the conditioning event is a statement about them, not a change to them. Independence is precisely what makes the $k-1$ failures multiply to $(0.7)^{k-1}$.",
                            r"Fail, fail, ..., fail, succeed — the arrangement is not a choice, so there is nothing to count.",
                            r"It is true that $\binom{k-1}{0} = 1$, which is a fair way to see it, but the phrasing has the reasoning backwards: nothing was left out for convenience. There is one arrangement because the positions before the success are forced, and the count says so.",
                            r"An unbounded support does not prevent counting the arrangements at a fixed $k$ — the binomial's support is finite and this argument would fail there too. At any given $k$ the count is a perfectly finite number, and that number is one.",
                        ],
                        "why": r"""
For the first success to land on trial $k$, trials $1$ through $k-1$ must all have failed
and trial $k$ must have succeeded. That describes one sequence, not a family of them:
there is no freedom about where the failures go, because they go everywhere before the
success. The binomial coefficient exists to count the ways of placing $k$ successes among
$n$ positions, and when the placement is forced the count is one. The formal version is
$\binom{k-1}{0} = 1$, which is a fine way to remember it as long as it is a conclusion
rather than a convention.
""",
                    },
                    {
                        "q": r"Twenty servers sit in a rack and six of them carry a bad firmware image. Ten are pulled at random, without replacement, and the bad ones counted. Why is $\mathrm{Binomial}(10, 0.3)$ the wrong model?",
                        "opts": [
                            r"Ten pulls from twenty servers is too small a sample for any distribution with a fixed number of trials to describe it honestly",
                            r"The binomial requires the count of successes to be smaller than the count of failures, which cannot be guaranteed here",
                            r"Removing a server changes the composition of the rack, so the success probability is not the same on every pull",
                            r"The pulls are made at random rather than in a fixed order, and the binomial assumes a fixed order",
                        ],
                        "a": 2,
                        "whys": [
                            r"Sample size is not the issue: a binomial with $n = 10$ is perfectly well defined and would be exactly right if the servers were sampled with replacement. The defect is in the mechanism, not the magnitude.",
                            r"No such requirement exists. $\mathrm{Binomial}(10, 0.9)$ is an ordinary distribution with far more successes than failures, and nothing in its derivation cares which of the two is commoner.",
                            r"After one bad pull the rack holds five bad of nineteen, so $p$ drops from $0.300$ to $0.263$.",
                            r"Order is irrelevant to both models — the binomial coefficient exists precisely because arrangements are pooled, and the hypergeometric pools them too. Randomising the order changes neither answer.",
                        ],
                        "why": r"""
The binomial derivation needs $p$ fixed across trials, and drawing without replacement
breaks that: after a bad server is pulled, five of the remaining nineteen are bad, so the
next probability is $0.263$ rather than $0.300$. The correct model is hypergeometric, and
the difference is real — $P(X \le 3)$ moves from $0.6496$ to $0.6858$ and the variance
falls from $2.10$ to $1.11$. Sampling without replacement is self-correcting, so the count
clusters more tightly around its mean than the binomial expects. What makes the error
tempting is that the words "trial", "success" and "independent" read as descriptions of
the story, when they are conditions on the arithmetic.
""",
                    },
                    {
                        "q": r"Over the three equally likely values $10000000.1$, $10000000.2$ and $10000000.3$, computing the variance as $E[X^{2}] - \mu^{2}$ in double precision returns exactly $0.0$, while the true answer is about $0.00667$. What went wrong?",
                        "opts": [
                            r"The two forms are not algebraically equal, and $E[X^{2}] - \mu^{2}$ is the biased one of the pair",
                            r"Two nearly equal numbers of size $10^{14}$ were subtracted, and their difference sits below the precision left there",
                            r"Squaring values that large overflows the double-precision range, so the sum saturates before the subtraction happens",
                            r"The masses $1/3$ cannot be held exactly in binary, so the two weighted sums were already wrong before either form was reached",
                        ],
                        "a": 1,
                        "whys": [
                            r"They are exactly equal in algebra — expand $E[(X-\mu)^{2}]$ and the cross term is $-2\mu E[X] + \mu^{2}$, which collapses. Neither form is biased; only one of them survives arithmetic on a finite machine.",
                            r"A double carries about sixteen significant digits, and $0.0067$ is the seventeenth digit of $10^{14}$.",
                            r"Nothing overflows here. A double reaches about $1.8 \times 10^{308}$, and $10^{14}$ squared is $10^{28}$ — comfortably inside the range. The loss is of precision, which is silent, rather than of magnitude, which is not.",
                            r"The masses really are inexact, and that is a genuine source of small error, but it is worth about $10^{-17}$ relative — nowhere near enough to erase the answer. Recomputing the same expression with exact thirds still returns zero at this scale.",
                        ],
                        "why": r"""
$E[X^{2}]$ here is about $10^{14}$ and so is $\mu^{2}$, and their difference is about
$0.0067$. A double holds roughly sixteen significant digits, so at a magnitude of $10^{14}$
the smallest distinguishable step is larger than the answer being sought: the two sums
round to the identical float and the subtraction yields zero. Computing
$E[(X - \mu)^{2}]$ instead subtracts while the numbers are still close together, keeping
every digit of the deviations, which is why the lab specifies the centred form.
""",
                    },
                    {
                        "q": r"Ten runs of the flaky test, with $E[X] = np = 3$. Which statement about that derivation is accurate?",
                        "opts": [
                            r"It follows from linearity of expectation over ten indicators, and holds even if the runs are correlated",
                            r"It follows from the independence of the ten runs, without which the expectation would have to be summed term by term instead",
                            r"It is a definition of the binomial's parameters rather than a result derived from the mass function",
                            r"It holds only in the limit of many runs, and at $n = 10$ it is an approximation",
                        ],
                        "a": 0,
                        "whys": [
                            r"$E[I_1 + \dots + I_{10}] = \sum E[I_j]$ needs no independence at all, which is exactly what makes the indicator trick worth learning.",
                            r"Independence is needed for the *variance* $np(1-p)$, and it is easy to carry that requirement backwards onto the mean. Linearity of expectation is unconditional: sums of expectations work for correlated terms too.",
                            r"The parameters $n$ and $p$ are the trial count and the per-trial probability; the mean is a consequence of them, and summing $k\,P(X=k)$ over the eleven masses returns $3.000000$ independently of any indicator argument.",
                            r"Nothing here is asymptotic. The value $3$ is exact at $n = 10$, and the direct sum over the mass function confirms it to every digit printed.",
                        ],
                        "why": r"""
Write $X = I_1 + \dots + I_{10}$ with $I_j$ equal to $1$ when run $j$ fails. Expectation is
linear, so $E[X] = \sum_j E[I_j] = 10 \times 0.3 = 3$, and linearity requires nothing
whatever about how the terms relate to one another. That is what makes the indicator
decomposition powerful: it survives correlation. Independence is needed for the variance
$np(1-p)$, since variances add only when covariances vanish, and carrying that requirement
back onto the mean is a common and unnecessary caution.
""",
                    },
                    {
                        "q": r"A geometric wait with $p = 0.3$ has run for seven trials with no success. What is the expected number of *further* trials until the first success?",
                        "opts": [
                            r"About $2.3$, since the expected total wait of $3.33$ has already been partly used up by the seven trials that have passed",
                            r"Exactly $7$, because a run of seven failures is repaid by a success within a comparable number of trials",
                            r"It cannot be determined without more information about those seven trials",
                            r"$3.\overline{3}$ further trials, exactly the wait it faced before the first one",
                        ],
                        "a": 3,
                        "whys": [
                            r"This treats the wait as a budget being spent, which is the intuition memorylessness contradicts. The expected total is not a quantity attached to the process that seven trials can deplete; it is an average over runs, most of which ended long ago.",
                            r"There is no repayment mechanism anywhere in $(1-p)^{k-1}p$. Each trial is a fresh $0.3$, and a long run of failures neither raises nor lowers the next one — this is the gambler's fallacy in its usual dress.",
                            r"The outcomes are known: all seven were failures, which is what the question states. Even if some had succeeded, independence means past outcomes carry no information about the next trial.",
                            r"$P(X > 7 + k \mid X > 7) = (0.7)^{k}$, free of the $7$ entirely.",
                        ],
                        "why": r"""
$P(X > m + k \mid X > m) = (1-p)^{k}$, with no $m$ anywhere on the right, so the
distribution of the remaining wait is the original distribution and its mean is $1/p =
3.\overline{3}$. That is memorylessness, and it is a consequence of the trials being
independent with a constant $p$ rather than a special property the geometric happens to
possess. It is also exactly where the model stops describing anything that wears out,
warms up or retries with backoff: for those, seven failures genuinely are informative,
and a geometric wait is the wrong tool.
""",
                    },
                ],
            },
            "lab": {
                "title": "pmf, cdf and the first two moments",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
No `math.comb`, no `statistics` module. Build these from the definitions.

**`choose(n, k)`** — the exact integer binomial coefficient. `0` when `k` is
negative or larger than `n`; `ValueError` when `n` is negative. Build it up
multiplicatively — `result = result * (n - i) // (i + 1)` stays exact and never
touches a huge factorial.

**`bernoulli_pmf(p, k)`** — `1 - p` at `k = 0`, `p` at `k = 1`, `0.0` elsewhere.

**`binomial_pmf(n, p, k)`** and **`binomial_cdf(n, p, k)`** — mass and running
total. Both return `0.0` below the support and the cdf returns `1.0` at or above
`n`.

**`geometric_pmf(p, k)`** and **`geometric_cdf(p, k)`** — trials up to and
including the first success, so the support starts at `k = 1`:

```text
geometric_pmf(0.5, 3)  ->  0.125
geometric_cdf(0.5, 3)  ->  0.875
```

Every one of these raises `ValueError` for a probability outside its range —
`[0, 1]` for Bernoulli and binomial, `(0, 1]` for geometric, where `p = 0` would
mean waiting for ever.

**`binomial_table(n, p)`** and **`geometric_table(p, kmax)`** — dicts from
outcome to probability, over `0..n` and `1..kmax` respectively.

**`expectation(pmf)`** and **`variance(pmf)`** — over any such dict. Both raise
`ValueError` if a mass is negative or the masses do not sum to 1 within `1e-9`.
Use the centred form for the variance.

The tables let you check the closed forms you were taught: a binomial table
should give back `n p` and `n p (1 - p)`, and a geometric table `1 / p` and
`(1 - p) / p^2`.
''',
                "files": [{"name": "main.py", "content": r'''
def choose(n, k):
    """Exact integer C(n, k). 0 outside the support, ValueError for n < 0."""
    # your code here


def bernoulli_pmf(p, k):
    """P(X = k) for a single trial with success probability p."""
    # your code here


def binomial_pmf(n, p, k):
    """P(X = k) for k successes in n independent trials."""
    # your code here


def binomial_cdf(n, p, k):
    """P(X <= k)."""
    # your code here


def geometric_pmf(p, k):
    """P(X = k), trials up to and including the first success."""
    # your code here


def geometric_cdf(p, k):
    """P(X <= k)."""
    # your code here


def binomial_table(n, p):
    """{k: P(X = k)} for k in 0..n."""
    # your code here


def geometric_table(p, kmax):
    """{k: P(X = k)} for k in 1..kmax."""
    # your code here


def expectation(pmf):
    """E[X] over a {value: probability} dict."""
    # your code here


def variance(pmf):
    """Var(X), computed about the mean."""
    # your code here


table = binomial_table(10, 0.3)
print("E[X] =", expectation(table), " Var(X) =", variance(table))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def choose(n, k):
    """Exact integer C(n, k). 0 outside the support, ValueError for n < 0."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)                     # C(n, k) == C(n, n - k), fewer terms
    result = 1
    for i in range(k):
        # the running product is always divisible, so // keeps this exact
        result = result * (n - i) // (i + 1)
    return result


def _check_prob(p, strict_low=False):
    if p < 0 or p > 1 or (strict_low and p == 0):
        raise ValueError(f"probability out of range: {p!r}")


def bernoulli_pmf(p, k):
    """P(X = k) for a single trial with success probability p."""
    _check_prob(p)
    if k == 0:
        return 1.0 - p
    if k == 1:
        return float(p)
    return 0.0


def binomial_pmf(n, p, k):
    """P(X = k) for k successes in n independent trials."""
    _check_prob(p)
    if n < 0:
        raise ValueError("n must be non-negative")
    if k < 0 or k > n:
        return 0.0
    return choose(n, k) * p ** k * (1 - p) ** (n - k)


def binomial_cdf(n, p, k):
    """P(X <= k)."""
    _check_prob(p)
    if k < 0:
        return 0.0
    return sum(binomial_pmf(n, p, j) for j in range(0, min(k, n) + 1))


def geometric_pmf(p, k):
    """P(X = k), trials up to and including the first success."""
    _check_prob(p, strict_low=True)
    if k < 1:
        return 0.0
    return (1 - p) ** (k - 1) * p


def geometric_cdf(p, k):
    """P(X <= k)."""
    _check_prob(p, strict_low=True)
    if k < 1:
        return 0.0
    return 1.0 - (1 - p) ** k             # closed form: the complement of k failures


def binomial_table(n, p):
    """{k: P(X = k)} for k in 0..n."""
    return {k: binomial_pmf(n, p, k) for k in range(n + 1)}


def geometric_table(p, kmax):
    """{k: P(X = k)} for k in 1..kmax."""
    return {k: geometric_pmf(p, k) for k in range(1, kmax + 1)}


def _check_pmf(pmf):
    if any(mass < 0 for mass in pmf.values()):
        raise ValueError("a probability mass cannot be negative")
    total = sum(pmf.values())
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"masses sum to {total!r}, not 1")


def expectation(pmf):
    """E[X] over a {value: probability} dict."""
    _check_pmf(pmf)
    return sum(value * mass for value, mass in pmf.items())


def variance(pmf):
    """Var(X), computed about the mean."""
    _check_pmf(pmf)
    mu = sum(value * mass for value, mass in pmf.items())
    return sum(mass * (value - mu) ** 2 for value, mass in pmf.items())


table = binomial_table(10, 0.3)
print("E[X] =", expectation(table), " Var(X) =", variance(table))
'''}],
                "hints": [
                    "`result = result * (n - i) // (i + 1)` is exact at every step because the partial product of i+1 consecutive integers is always divisible by (i+1)!.",
                    "Write one private validator for the probability argument and call it from every public function, so the error message is identical everywhere.",
                    "`geometric_cdf` does not need a loop: k failures then anything has probability (1-p)^k, so the cdf is 1 minus that.",
                    "Compute the mean once inside `variance` and reuse it; recomputing it inside the sum is both slower and easier to get wrong.",
                ],
                "tests": [
                    {"name": "choose is exact and bounded", "code": r'''
for _n, _k, _want in [(5, 2, 10), (0, 0, 1), (10, 5, 252), (52, 5, 2598960), (5, 5, 1)]:
    _got = choose(_n, _k)
    assert _got == _want, f"choose({_n}, {_k}) gave {_got!r}, expected {_want}"
assert isinstance(choose(52, 5), int), "choose returns an exact integer, not a float"
assert choose(5, 6) == 0 and choose(5, -1) == 0, "Outside the support the count is 0"
try:
    choose(-1, 0)
    assert False, "choose(-1, 0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Bernoulli and binomial masses", "code": r'''
assert bernoulli_pmf(0.3, 1) == 0.3 and abs(bernoulli_pmf(0.3, 0) - 0.7) < 1e-12
assert bernoulli_pmf(0.3, 2) == 0.0, "Only 0 and 1 carry mass"
assert abs(binomial_pmf(5, 0.5, 2) - 0.3125) < 1e-12, f"Got {binomial_pmf(5, 0.5, 2)!r}"
assert binomial_pmf(5, 0.5, 6) == 0.0 and binomial_pmf(5, 0.5, -1) == 0.0
assert binomial_pmf(4, 0.0, 0) == 1.0, "With p = 0 all the mass sits at k = 0"
assert binomial_pmf(4, 1.0, 4) == 1.0, "With p = 1 all the mass sits at k = n"
assert abs(sum(binomial_table(9, 0.37).values()) - 1.0) < 1e-12, "A pmf must sum to 1"
for _bad in (-0.1, 1.4):
    try:
        binomial_pmf(5, _bad, 2)
        assert False, f"binomial_pmf with p={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The binomial cdf accumulates", "code": r'''
assert binomial_cdf(5, 0.5, -1) == 0.0, "Below the support the cdf is 0"
assert abs(binomial_cdf(5, 0.5, 5) - 1.0) < 1e-12, "At n the cdf is 1"
assert abs(binomial_cdf(5, 0.5, 99) - 1.0) < 1e-12, "Above n the cdf stays 1"
assert abs(binomial_cdf(5, 0.5, 2) - 0.5) < 1e-12, f"Got {binomial_cdf(5, 0.5, 2)!r}"
_prev = -1.0
for _k in range(-1, 7):
    _now = binomial_cdf(6, 0.4, _k)
    assert _now >= _prev - 1e-15, f"The cdf dipped at k={_k}"
    _prev = _now
'''},
                    {"name": "Geometric mass and its closed-form cdf", "code": r'''
assert abs(geometric_pmf(0.5, 3) - 0.125) < 1e-12, f"Got {geometric_pmf(0.5, 3)!r}"
assert geometric_pmf(0.5, 0) == 0.0, "The support starts at one trial"
assert abs(geometric_cdf(0.5, 3) - 0.875) < 1e-12, f"Got {geometric_cdf(0.5, 3)!r}"
assert geometric_cdf(0.5, 0) == 0.0
for _k in range(1, 12):
    _summed = sum(geometric_pmf(0.31, _j) for _j in range(1, _k + 1))
    assert abs(geometric_cdf(0.31, _k) - _summed) < 1e-12, \
        f"cdf and the summed pmf disagree at k={_k}"
assert geometric_pmf(1.0, 1) == 1.0, "A certain success always lands on the first trial"
try:
    geometric_pmf(0.0, 3)
    assert False, "p = 0 never succeeds, so it should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Binomial moments match n p and n p (1 - p)", "code": r'''
for _n, _p in [(10, 0.3), (7, 0.5), (20, 0.15)]:
    _t = binomial_table(_n, _p)
    assert abs(expectation(_t) - _n * _p) < 1e-9, \
        f"E[X] for Binomial({_n}, {_p}) is {expectation(_t)!r}, expected {_n * _p}"
    assert abs(variance(_t) - _n * _p * (1 - _p)) < 1e-9, \
        f"Var(X) for Binomial({_n}, {_p}) is {variance(_t)!r}, expected {_n * _p * (1 - _p)}"
'''},
                    {"name": "Geometric moments match 1/p and (1-p)/p^2", "code": r'''
for _p, _kmax in [(0.25, 400), (0.5, 80)]:
    _t = geometric_table(_p, _kmax)
    assert abs(expectation(_t) - 1 / _p) < 1e-6, \
        f"E[X] for Geometric({_p}) is {expectation(_t)!r}, expected {1 / _p}"
    assert abs(variance(_t) - (1 - _p) / _p ** 2) < 1e-6, \
        f"Var(X) for Geometric({_p}) is {variance(_t)!r}, expected {(1 - _p) / _p ** 2}"
'''},
                    {"name": "The moment functions refuse a non-distribution", "code": r'''
for _bad in ({0: 0.5, 1: 0.2}, {0: 1.2, 1: -0.2}, {}):
    for _fn in (expectation, variance):
        try:
            _fn(_bad)
            assert False, f"{_fn.__name__}({_bad!r}) should raise ValueError"
        except ValueError:
            pass
assert abs(variance({0: 0.5, 1: 0.5}) - 0.25) < 1e-12, "A fair coin has variance 1/4"
assert variance({4: 1.0}) == 0.0, "A point mass has no spread"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Continuous random variables and densities",
            "summary": (
                "Outcomes on a continuum, where probability lives in an integral and "
                "no single point carries any of it."
            ),
            "concepts": [
                r"A density is not a probability: $f(x)$ may exceed 1, the probability is the area $\int_a^b f(x) dx$, and $P(X = c) = 0$ for every single point",
                r"The cdf $F(x) = P(X \le x)$ is the running integral of the density and $f = F'$ undoes it; every sum from the discrete module becomes an integral, including $E[X] = \int x f(x) dx$",
                r"Uniform, exponential and normal are the three shapes most of computing runs on, and the normal is fixed by $\mu$ and $\sigma$ alone",
                r"$z = (x - \mu)/\sigma$ rescales any variable to mean $0$ and spread $1$, which fixes location and scale and never shape: a normal table read off a standardised exponential is wrong by $8.5$ percentage points at $z = -0.5$",
                r"The exponential is the continuous memoryless distribution — $P(X > s + t | X > s) = P(X > t)$ — which is why it models arrivals well and wear-out not at all",
                r"Quantiles invert the cdf, and inverse-transform sampling turns a uniform draw into a draw from any distribution whose cdf you can invert",
                'Every single point carries probability zero, by monotonicity, so on a continuum $P = 0$ stops meaning impossible and conditioning on a single outcome is undefined rather than zero',
                'A density is a rate: $P(x < X \\le x + h) \\approx f(x)h$, so $f$ is probability per unit length and nothing caps its height — only $f \\ge 0$ and a total area of $1$',
                'The exponential follows from one assumption, a constant hazard $h(t) = f(t)/S(t) = \\lambda$; memorylessness and $E[T] = 1/\\lambda$ are consequences rather than extra properties',
                'A rising hazard is what wear-out means, and no $\\lambda$ expresses it: a Weibull of shape $2$ and scale $100$ has hazard $0.002$ per hour at $t = 10$ and $0.040$ at $t = 200$',
            ],
            "read": [
                {
                    "title": 'Where the probability went, and the rate that replaced it',
                    "minutes": 14,
                    "body": r'''
A bus is due between $10{:}00$ and $10{:}10$, and you are willing to say that no instant
in that window is favoured over any other. What is the probability it arrives at exactly
$10{:}03{:}00.000$?

Zero. Not small — zero. And the same argument gives zero for every other instant, while
the bus certainly arrives at *some* instant. So an event of probability zero happens on
every single run of this experiment, which is the moment module 1's warning that
$P = 0$ stops meaning "impossible" becomes concrete rather than a footnote.

## Why every point must carry nothing

The argument is short and it is worth doing rather than accepting. Suppose the arrival
$X$ lies in a window of length $L$, uniformly. Fix an instant $c$ and any $n$. The event
$X = c$ is contained in the sub-interval of length $L/n$ around $c$, so monotonicity —
module 1, derived from A1 and A3 — gives

$$P(X = c) \le \frac{L/n}{L} = \frac{1}{n} .$$

That holds for every $n$. A non-negative number below $\frac{1}{n}$ for all $n$ is zero.
Nothing about uniformity was essential; the same squeeze runs whenever the cumulative
distribution function is continuous.

The consequence is that on a continuum, probability cannot be carried by points. It has
to be carried by *intervals*, and the object that says how much each interval carries is
a density.

## The density is a rate, which is why it may exceed one

Define the **cumulative distribution function** $F(x) = P(X \le x)$. Then for a small
step $h$,

$$P(x < X \le x + h) = F(x + h) - F(x) ,$$

and dividing by $h$ and letting it shrink gives the derivative. Write $f = F'$. Then

$$P(x < X \le x + h) \approx f(x)\,h .$$

Read the units off that line. The left side is a probability, a pure number. The right
side is $f$ times a length. So $f$ is **probability per unit length** — a rate, not a
probability. The two constraints on it are that it is never negative, because $F$ never
decreases, and that $\int_{-\infty}^{\infty} f = 1$, because the total must be one.
Neither of those caps its height.

A uniform variable on $[0, 0.5]$ therefore has $f(x) = 2$ across that interval, and the
area is $2 \times 0.5 = 1$ exactly as required. A density of $2$ is not a probability of
$2$, and the difference is the same one as between $90$ kilometres per hour and $90$
kilometres.

## Worked: the exponential, out of one assumption

Most treatments announce $f(t) = \lambda e^{-\lambda t}$ and verify it afterwards. It is
more useful to see where it comes from, because the assumption it comes from is exactly
the assumption that fails in practice.

Let $T$ be a time to failure and define the **survival function**
$S(t) = P(T > t) = 1 - F(t)$. The **hazard rate** is

$$h(t) = \frac{f(t)}{S(t)} ,$$

the rate of failing right now given that you have survived until now. Suppose the hazard
is a constant $\lambda$: the component is no more likely to fail in its second hour than
in its first. Since $f = F' = -S'$,

$$-\frac{S'(t)}{S(t)} = \lambda .$$

The left side is the derivative of $-\ln S(t)$. Integrating from $0$ to $t$ and using
$S(0) = 1$ gives $\ln S(t) = -\lambda t$, so

$$S(t) = e^{-\lambda t}, \qquad F(t) = 1 - e^{-\lambda t}, \qquad
f(t) = \lambda e^{-\lambda t} .$$

Memorylessness now falls out rather than being a separate property:

$$P(T > s + t \,|\, T > s) = \frac{S(s+t)}{S(s)}
= \frac{e^{-\lambda(s+t)}}{e^{-\lambda s}} = e^{-\lambda t} = P(T > t) .$$

And the mean, using $E[T] = \int_{0}^{\infty} S(t)\,\mathrm{d}t$, is
$\int_{0}^{\infty} e^{-\lambda t}\,\mathrm{d}t = 1/\lambda$.

## Worked: manufacturing an arrival time

Take $\lambda = 1/100$ per hour, so the mean time to failure is $100$ hours. Your
generator hands you $U = 0.37$, uniform on $[0,1)$. Inverse-transform sampling says to
solve $F(t) = U$:

$$1 - e^{-\lambda t} = 0.37 \quad \Rightarrow \quad
t = -\frac{\ln(1 - 0.37)}{\lambda} = -100 \ln 0.63 = 46.2035 \text{ hours} .$$

Check it in the other direction: $F(46.2035) = 1 - e^{-0.462035} = 0.370000$. The draw
lands where it was asked to. The reason this works at all is one line —
$P(F^{-1}(U) \le t) = P(U \le F(t)) = F(t)$, the last equality being the uniform's own
cdf — and it is how a simulation makes arrival times out of nothing but a stream of
uniforms.

## The mistake, and why it is tempting

Memorylessness reads as a claim that the machine is immortal, and people reject it on
those grounds. A component that has run $100$ hours is expected to run $100$ more; run
it $500$ hours and it still expects $100$ more. That sounds like a broken model.

It is not broken, it is *assumed*. Constant hazard was the input, and everything above is
its consequence. The right response is not to distrust the arithmetic but to ask whether
constant hazard describes the thing in front of you. For arrivals at a queue —
independent users deciding independently — it is a good description. For anything that
wears out it is a bad one, and no choice of $\lambda$ repairs it, because $\lambda$ sets
the scale and the fault is in the shape.

Make that concrete. A Weibull time-to-failure with shape $2$ and scale $100$ has hazard
$h(t) = 2t/100^{2}$: at $t = 10$ hours it is $0.002$ per hour, and at $t = 200$ hours it
is $0.040$ per hour, **twenty times higher**. That rising hazard is what wear-out means,
and an exponential has no parameter that can express it.

## Memorylessness is not a property the exponential happens to have

The concepts list calls the exponential *the* continuous memoryless distribution, and the
definite article is a uniqueness claim worth checking rather than accepting. Suppose only
that $T$ is memoryless — that $P(T > s + t \,|\, T > s) = P(T > t)$ for all
$s, t \ge 0$ — and say nothing about its form. Multiplying up, that condition is

$$S(s + t) = S(s)\,S(t) .$$

A survival function is non-increasing and satisfies $S(0) = 1$, and the only such
functions turning sums into products are $S(t) = e^{-\lambda t}$. So memorylessness does
not merely hold for the exponential; it *forces* it. There is no second memoryless
continuous distribution to choose instead.

It is worth seeing the condition fail, so that it reads as a restriction rather than a
formality. Take $S(t) = 1/(1+t)$, a legitimate survival function with a heavy tail. Then

$$S(1)S(2) = \tfrac{1}{2} \times \tfrac{1}{3} = \tfrac{1}{6},
\qquad S(3) = \tfrac{1}{4} ,$$

and $\frac{1}{6} \ne \frac{1}{4}$. Having survived to time $1$ genuinely changes the
outlook for this variable, which is what a non-constant hazard means.

## Where it stops: standardising is not normalising

The concepts list says $z = (x - \mu)/\sigma$ puts distributions on one scale, and it is
worth being exact about what that buys. Subtracting the mean and dividing by the standard
deviation always produces a variable with mean $0$ and standard deviation $1$. It does
**not** produce a normal variable, and reading a normal table off the result is a
mistake with a measurable size.

An exponential with $\lambda = 1$ has mean $1$ and standard deviation $1$, so it is
already standardised. Ask for $P(Z \le -0.5)$, which is $P(X \le 0.5)$:

$$P(X \le 0.5) = 1 - e^{-0.5} = 0.393469 ,$$

while the normal table at $z = -0.5$ returns $0.308538$. The gap is **$8.5$ percentage
points**, on a variable that has been standardised perfectly. Standardising fixes
location and scale. It never touches shape, and shape is what a table is a table of.

Two further limits worth carrying. $P(X \le c)$ and $P(X < c)$ are the same number for a
continuous variable, because the point between them carries nothing — a convenience that
is false for every discrete variable in module 3. And $f$ is recovered from $F$ by
differentiating only where $F$ is differentiable: a variable that is continuous in part
and atomic in part, such as a latency that is exactly zero whenever a cache hits, has no
density at the atom and needs both descriptions at once.
''',
                },
            ],
            "derive": [
                {
                    "title": 'The exponential, out of one assumption about its hazard',
                    "minutes": 12,
                    "vars": ['S', 'f', 't', 's', 'lambda'],
                    "brief": r'''
The exponential is usually announced and then checked. Here it is built, from the single
assumption that the hazard rate is constant — which is also the assumption that decides
where the model may be used.

Write $S(t) = P(T > t)$ for the survival function and $f$ for the density. Since
$S = 1 - F$ and $f = F'$, we have $f = -S'$, and the hazard is $h = f/S$. Take
$h(t) = \lambda$ for every $t$, with $S(0) = 1$.
''',
                    "steps": [
                        {
                            "prompt": "Constant hazard says $-S'(t)/S(t) = \\lambda$, and the left side is the derivative of $-\\ln S(t)$. Integrate both sides from $0$ to $t$ and use $S(0) = 1$. Write $\\ln S(t)$.",
                            "answer": '-\\lambda t',
                            "placeholder": 'a linear function of t',
                            "hint": 'Integrating $\\frac{\\mathrm{d}}{\\mathrm{d}t}\\ln S = -\\lambda$ gives $\\ln S(t) - \\ln S(0) = -\\lambda t$, and $\\ln 1 = 0$.',
                        },
                        {
                            "prompt": 'Exponentiate the previous line. Write the survival function $S(t)$.',
                            "answer": 'e^{-\\lambda t}',
                            "hint": 'Undo the logarithm: $S(t) = e^{\\ln S(t)}$.',
                        },
                        {
                            "prompt": 'The cumulative distribution function is $F(t) = 1 - S(t)$. Write $F(t)$.',
                            "answer": '1 - e^{-\\lambda t}',
                            "hint": 'Substitute the previous answer into $F = 1 - S$.',
                        },
                        {
                            "prompt": 'Differentiate $F$ to recover the density. Write $f(t)$.',
                            "answer": '\\lambda e^{-\\lambda t}',
                            "hint": 'The derivative of $-e^{-\\lambda t}$ is $\\lambda e^{-\\lambda t}$ by the chain rule.',
                            "deconstruct": [
                                '$F(t) = 1 - e^{-\\lambda t}$, and the derivative of the constant $1$ is zero.',
                                'The chain rule on $e^{-\\lambda t}$ brings down a factor of $-\\lambda$.',
                                "So $F'(t) = -(-\\lambda e^{-\\lambda t}) = \\lambda e^{-\\lambda t}$, which is the announced density — now derived.",
                            ],
                        },
                        {
                            "prompt": 'Memorylessness is a ratio of survivals: $P(T > s + t \\,|\\, T > s) = S(s+t)/S(s)$. Form that ratio and simplify. Write the result.',
                            "answer": 'e^{-\\lambda t}',
                            "hint": '$e^{-\\lambda(s+t)}/e^{-\\lambda s}$: subtract the exponents.',
                            "deconstruct": [
                                '$S(s+t) = e^{-\\lambda(s+t)} = e^{-\\lambda s}e^{-\\lambda t}$.',
                                'Dividing by $S(s) = e^{-\\lambda s}$ cancels the first factor.',
                                'What is left is $e^{-\\lambda t} = S(t)$: the elapsed $s$ has vanished from the answer, which is exactly what memorylessness says.',
                            ],
                        },
                        {
                            "prompt": 'For a non-negative variable, $E[T] = \\int_{0}^{\\infty} S(t)\\,\\mathrm{d}t$. Evaluate that integral for this $S$. Write $E[T]$.',
                            "answer": '\\frac{1}{\\lambda}',
                            "hint": '$\\int_{0}^{\\infty} e^{-\\lambda t}\\,\\mathrm{d}t = [-e^{-\\lambda t}/\\lambda]_{0}^{\\infty}$, and the exponential vanishes at the top limit for $\\lambda > 0$.',
                        },
                    ],
                    "closing": r'''
Every property of the exponential in this module came out of one line: the hazard does
not change with age. The density was not assumed, memorylessness was not a separate
axiom, and the mean $1/\lambda$ is a consequence rather than a definition.

That also locates the model's edge precisely. Constant hazard is a strong claim, and it
is testable: plot the empirical hazard against age and see whether it is flat. If it
rises, the component wears out and a Weibull with shape above $1$ is the honest choice;
if it falls, the population has early failures burning off. Choosing an exponential
because the algebra is convenient is choosing a flat hazard whether or not the thing has
one, and step 5 is what that choice commits you to.
''',
                },
            ],
            "quiz": {
                "title": "Area, not height",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"$X$ is uniform on $[0, 0.5]$, so its density is $f(x) = 2$ across that interval. Is a density of 2 legal?",
                        "opts": [
                            "No — no probability may exceed 1",
                            "Yes — a density is probability per unit length, and only its integral has to be 1",
                            "No, unless the interval is longer than 1",
                            "Yes, because densities are permitted to be negative as well",
                        ],
                        "a": 1,
                        "why": (
                            r"A density measures probability per unit of $x$, not probability. Over an interval of "
                            r"length $0.5$ a height of $2$ encloses an area of $2 \times 0.5 = 1$, exactly as "
                            r"required. The two real constraints are that the density is never negative and that it "
                            r"integrates to 1 over the whole line; nothing caps its height."
                        ),
                    },
                    {
                        "q": r"For a continuous random variable $X$, what is $P(X = 3.5)$?",
                        "opts": [
                            r"It equals $f(3.5)$",
                            "It depends on how wide the support is",
                            "It is undefined",
                            r"$0$",
                        ],
                        "a": 3,
                        "why": (
                            r"A single point is an interval of zero width, so the area above it is zero whatever "
                            r"height the density has there. This is why continuous probabilities are always quoted "
                            r"over intervals, and why $P(X \le c)$ and $P(X < c)$ are the same number here — a "
                            r"distinction that very much matters for a discrete variable."
                        ),
                    },
                    {
                        "q": "A server's time to failure is exponential with mean 100 hours. It has already run 100 hours without failing. What is the expected additional time to failure?",
                        "opts": [
                            r"$0$ hours — it is overdue",
                            r"$50$ hours",
                            r"$100$ hours",
                            r"$200$ hours",
                        ],
                        "a": 2,
                        "why": (
                            r"Memorylessness says $P(X > s + t | X > s) = P(X > t)$, so a machine that has survived "
                            r"100 hours is statistically indistinguishable from a new one and still expects a full "
                            r"100 hours. This is the continuous twin of the geometric distribution met earlier, and "
                            r"it is precisely why an exponential model cannot express a component that wears out."
                        ),
                    },
                    {
                        "q": r"Which statement relates a density $f$ to its cdf $F$ correctly?",
                        "opts": [
                            r"$f(x) = F'(x)$ and $F(x) = \int_{-\infty}^{x} f(t) dt$",
                            r"$F(x) = f'(x)$ and $f(x) = \int_{-\infty}^{x} F(t) dt$",
                            r"$f(x) = 1 - F(x)$",
                            r"$F(x) = f(x)$ for every continuous variable",
                        ],
                        "a": 0,
                        "why": (
                            r"Accumulating the density up to $x$ gives the probability of landing at or below $x$, "
                            r"which is the definition of the cdf; differentiating undoes the accumulation. It is the "
                            r"fundamental theorem of calculus doing the work, and it is the same relationship as the "
                            r"running total in the discrete module with the sum replaced by an integral. "
                            r"$1 - F(x)$ is the survival function, a different object."
                        ),
                    },
                    {
                        "q": r"Your generator produces $U$, uniform on $[0, 1)$. How do you turn it into a draw from a distribution with an invertible cdf $F$?",
                        "opts": [
                            r"Compute $F(U)$",
                            r"Compute $F^{-1}(U)$",
                            r"Compute $U / F(U)$",
                            r"Average many independent draws of $U$",
                        ],
                        "a": 1,
                        "why": (
                            r"$F^{-1}(U)$ has cdf $F$, because $P(F^{-1}(U) \le x) = P(U \le F(x)) = F(x)$, where "
                            r"the final equality is just the uniform's own cdf. For the exponential this works out "
                            r"to $-\ln(1 - U)/\lambda$, one line of code, which is how a simulation manufactures "
                            r"arrival times from nothing but a stream of uniforms."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Joint distributions, covariance and correlation",
            "summary": (
                "Two variables at once: how their masses combine, how they move "
                "together, and what the variance of a sum really costs."
            ),
            "concepts": [
                r"A joint pmf spreads mass over pairs $(x, y)$; summing one variable out recovers the marginal of the other, because the axiom for disjoint events adds the slices",
                r"$X$ and $Y$ are independent exactly when the joint factorises, $p(x, y) = p_X(x) p_Y(y)$, for every pair — one failing pair is enough to break it",
                r"$\mathrm{Cov}(X, Y) = E[XY] - E[X]E[Y]$, and $\mathrm{Var}(X + Y) = \mathrm{Var}(X) + \mathrm{Var}(Y) + 2\mathrm{Cov}(X, Y)$, so variances add only when the covariance vanishes",
                r"Correlation is the covariance divided by both standard deviations: unitless, bounded in $[-1, 1]$, and therefore comparable across quantities that a raw covariance is not",
                "Independence forces zero covariance, but zero covariance does not force independence, because covariance only sees the linear part of a relationship",
                'Covariance is defined as $E[(X - \\mu_X)(Y - \\mu_Y)]$, and $E[XY] - E[X]E[Y]$ is what expanding that bracket gives — a consequence, not a second definition',
                '$|\\rho| \\le 1$ follows from the non-negativity of $\\mathrm{Var}(X/\\sigma_X \\pm Y/\\sigma_Y)$, read twice; reaching $\\pm 1$ forces a variance to vanish, so the endpoints mean an exact linear relation and nothing else',
                '$\\mathrm{Var}(X - Y) = \\mathrm{Var}(X) + \\mathrm{Var}(Y) - 2\\mathrm{Cov}(X, Y)$, so positively correlated quantities have a *less* variable difference — which is the whole statistical argument for a paired design',
                'Correlation divides by $\\sigma_X \\sigma_Y$, so it needs both variances finite and non-zero: a constant correlates with nothing, and a heavy-tailed variable may have no variance to divide by at all',
            ],
            "read": [
                {
                    "title": 'Two variables at once, and the bound a correlation cannot cross',
                    "minutes": 13,
                    "body": r'''
A service retries a failed request up to twice, and each request either completes or
times out. Two numbers describe a single request: $X$, the number of retries, in
$\left\{0, 1, 2\right\}$; and $Y$, which is $1$ on a timeout and $0$ otherwise. Neither variable on
its own answers the question you care about, which is whether retrying is associated with
timing out. That question lives in the **joint** distribution.

Here is one, with masses in twentieths.

```text
                Y = 0     Y = 1     row total
    X = 0        2/20      3/20        5/20
    X = 1        4/20      5/20        9/20
    X = 2        3/20      3/20        6/20
    column      9/20     11/20       20/20
```

The six masses are non-negative and total one, so this is a legitimate model. Everything
below is read off it.

## Marginals are the addition axiom, applied

The event $X = 0$ is the union of the two disjoint events $(X = 0, Y = 0)$ and
$(X = 0, Y = 1)$, so A3 adds them:
$P(X = 0) = \frac{2}{20} + \frac{3}{20} = \frac{5}{20}$.
Doing that along each row and each column gives the **marginal**
distributions in the margins of the table, which is where the name comes from.

$$p_X = \left(\tfrac{5}{20}, \tfrac{9}{20}, \tfrac{6}{20}\right), \qquad
p_Y = \left(\tfrac{9}{20}, \tfrac{11}{20}\right)$$

Summing a variable out is not an approximation and loses nothing about the variable that
remains. It does lose the relationship: two different joint tables can have identical
margins, which is why the margins alone can never answer the question this module asks.

Check independence first, because if it holds everything afterwards is easier.
Independence requires $p(x,y) = p_X(x)p_Y(y)$ for **every** cell. The first cell already
fails:

$$p(0,0) = \frac{2}{20} = 0.100, \qquad
p_X(0)p_Y(0) = \frac{5}{20} \times \frac{9}{20} = \frac{9}{80} = 0.1125 .$$

One failing cell is enough. $X$ and $Y$ are dependent.

## Covariance, derived from the definition

Covariance is defined as the mean of the product of the two deviations:

$$\mathrm{Cov}(X,Y) = E[(X - \mu_X)(Y - \mu_Y)] .$$

Expand the bracket and use linearity of expectation, which holds whatever the dependence:

$$E[XY] - \mu_Y E[X] - \mu_X E[Y] + \mu_X\mu_Y
= E[XY] - \mu_X\mu_Y - \mu_X\mu_Y + \mu_X\mu_Y = E[XY] - E[X]E[Y] .$$

The computational form is a consequence, not a second definition. Now the numbers.
$E[X] = 0 \cdot \frac{5}{20} + 1 \cdot \frac{9}{20} + 2 \cdot \frac{6}{20} = 1.05$
and $E[Y] = \frac{11}{20} = 0.55$. For $E[XY]$ only the cells with
both values non-zero contribute:

$$E[XY] = 1 \cdot 1 \cdot \tfrac{5}{20} + 2 \cdot 1 \cdot \tfrac{3}{20}
= \tfrac{11}{20} = 0.55 .$$

$$\mathrm{Cov}(X,Y) = 0.55 - 1.05 \times 0.55 = -\frac{11}{400} = -0.0275$$

Negative: more retries go very slightly with fewer timeouts in this table. Whether
$-0.0275$ is a large number is a question the covariance cannot answer, and that is the
next problem.

## What the dependence actually looks like

Before summarising the relationship with one number, it is worth reading it off the table
directly, because the summary is going to throw most of it away. Conditioning each row on
its own total — module 2's renormalisation, applied to a slice — gives the chance of a
timeout at each retry count:

$$P(Y = 1 | X = 0) = \frac{3/20}{5/20} = 0.600, \qquad
P(Y = 1 | X = 1) = \frac{5/20}{9/20} = 0.556,$$
$$P(Y = 1 | X = 2) = \frac{3/20}{6/20} = 0.500 .$$

Against an unconditional $P(Y = 1) = 0.550$. The three conditionals are not equal to it
and not equal to each other, which is dependence stated in the most direct way available:
being told the retry count moves the timeout probability. The movement is small and
monotone downward, from $0.600$ to $0.500$ — and it is that downward drift, weighted by
how much mass sits in each row, that the single negative covariance below is measuring.

## Correlation, and why it cannot leave its interval

The trouble with covariance is units. $X$ is a count and $Y$ is an indicator, so
$-0.0275$ is in units of retries times timeouts, and rescaling either variable rescales
it. Measure a latency in seconds instead of milliseconds and its covariance with anything
changes by a factor of a thousand while nothing about the relationship has moved.

Divide the units out. With $\sigma_X^2 = \frac{219}{400} = 0.5475$ and
$\sigma_Y^2 = \frac{99}{400} = 0.2475$,

$$\rho = \frac{\mathrm{Cov}(X,Y)}{\sigma_X \sigma_Y}
= \frac{-0.0275}{\sqrt{0.5475}\sqrt{0.2475}} = -0.0747 .$$

Now, why is $\rho$ trapped in $[-1, 1]$? The concepts list states the bound. It follows
from one fact — a variance is never negative — in two lines. Standardise both variables
and add them. Using
$\mathrm{Var}(U + V) = \mathrm{Var}(U) + \mathrm{Var}(V) + 2\mathrm{Cov}(U,V)$, each
standardised variable has variance $1$ and their covariance is $\rho$:

$$0 \le \mathrm{Var}\!\left(\frac{X}{\sigma_X} + \frac{Y}{\sigma_Y}\right)
= 1 + 1 + 2\rho = 2 + 2\rho \quad \Rightarrow \quad \rho \ge -1$$

$$0 \le \mathrm{Var}\!\left(\frac{X}{\sigma_X} - \frac{Y}{\sigma_Y}\right)
= 2 - 2\rho \quad \Rightarrow \quad \rho \le 1$$

The bound is not a convention and it is not an empirical observation. It is the
non-negativity of variance, read twice. The equality case is just as informative:
$\rho = -1$ forces a variance to be exactly zero, and a variable with zero variance is a
constant, so the two standardised variables differ by a constant and $Y$ is an exact
linear function of $X$. Correlation reaches its endpoints only for a perfect straight
line.

## Worked: what a sum costs, and what a difference saves

$$\mathrm{Var}(X + Y) = 0.5475 + 0.2475 + 2(-0.0275) = 0.74$$
$$\mathrm{Var}(X - Y) = 0.5475 + 0.2475 - 2(-0.0275) = 0.85$$

The sign flip on the cross term is worth more attention than it usually gets. For
**positively** correlated quantities the difference is the *less* variable of the two
combinations — which is why measuring the same servers before and after a change, and
analysing the differences, beats comparing two independent groups. The shared variation
cancels. That is the whole statistical argument for a paired design, and it is one line
of algebra.

## The mistake, and why it is tempting

Zero covariance does not mean independence. The standard counterexample takes $X$
uniform on $\left\{-1, 0, 1\right\}$ and $Y = X^{2}$. Then $E[X] = 0$ and
$E[XY] = E[X^{3}] = \frac{(-1) + 0 + 1}{3} = 0$, so

$$\mathrm{Cov}(X,Y) = 0 - 0 \times E[Y] = 0 ,$$

while $Y$ is a *function* of $X$ — knowing $X$ pins $Y$ down exactly. The relationship is
a perfect parabola and covariance sees none of it.

The reason the error is tempting is that the implication runs one way and people
remember it as an equivalence. Independence does force zero covariance: if the joint
factorises then $E[XY] = E[X]E[Y]$, and the covariance vanishes. The converse fails
because covariance is a single number summarising the *linear* part of a relationship,
and a symmetric dependence has no linear part to find. Correlation is not a general
measure of association; it is a measure of straight-line association, and a coefficient
of zero rules out only that.

## Where it stops

**Both variances must be finite and non-zero.** $\rho$ divides by $\sigma_X\sigma_Y$, so
a constant has no correlation with anything — the ratio is $0/0$, not $0$. Worse, a
distribution with heavy enough tails has no finite variance at all, and then covariance
and correlation are undefined rather than large. Module 7's Chebyshev bound runs into the
same wall from the other side.

**Linearity of expectation needs nothing; the variance rule needs the covariance.**
$E[X + Y] = E[X] + E[Y]$ holds for any pair, dependent or not, because expectation is a
weighted sum and sums split. Variances add **only** when the covariance is zero. Applying
the expectation rule's freedom to the variance is the most common route to a standard
error that is quietly too small, and in a benchmark where the runs share a machine the
covariance is exactly the term you have most reason to expect is not zero.
''',
                },
            ],
            "derive": [
                {
                    "title": 'Why a correlation cannot leave the interval from minus one to one',
                    "minutes": 11,
                    "vars": ['sigma_X', 'sigma_Y', 'C', 'rho'],
                    "brief": r'''
The bound $-1 \le \rho \le 1$ is usually stated and left. It is a consequence of one
fact — a variance is never negative — and this derivation extracts it, together with the
condition under which the endpoints are actually reached.

Write $\sigma_{X}$ and $\sigma_{Y}$ for the two standard deviations, both taken positive,
$C$ for $\mathrm{Cov}(X, Y)$, and $\rho$ for the correlation.
''',
                    "steps": [
                        {
                            "prompt": 'Start from the definition of variance and expand $E[((X - \\mu_X) + (Y - \\mu_Y))^{2}]$. Write $\\mathrm{Var}(X + Y)$ in terms of $\\sigma_{X}$, $\\sigma_{Y}$ and $C$.',
                            "answer": '\\sigma_{X}^{2} + \\sigma_{Y}^{2} + 2C',
                            "placeholder": 'two variances and a cross term',
                            "hint": 'Squaring a sum gives three terms; the cross term is $2E[(X-\\mu_X)(Y-\\mu_Y)]$, which is $2C$ by definition.',
                        },
                        {
                            "prompt": 'Correlation is the covariance with the units divided out. Write $\\rho$ in terms of $C$, $\\sigma_{X}$ and $\\sigma_{Y}$.',
                            "answer": '\\frac{C}{\\sigma_{X}\\sigma_{Y}}',
                            "hint": 'Divide the covariance by both standard deviations, which is what makes the result unitless.',
                        },
                        {
                            "prompt": 'Now standardise: let $U = X/\\sigma_{X}$ and $V = Y/\\sigma_{Y}$, so each has variance $1$ and $\\mathrm{Cov}(U,V) = \\rho$. Apply step 1 to $U + V$. Write $\\mathrm{Var}(U + V)$ in terms of $\\rho$.',
                            "answer": '2 + 2\\rho',
                            "hint": 'Both variances are now $1$, and the cross term is $2\\rho$.',
                            "deconstruct": [
                                '$\\mathrm{Var}(U) = \\mathrm{Var}(X)/\\sigma_{X}^{2} = 1$, and likewise for $V$.',
                                '$\\mathrm{Cov}(U, V) = C/(\\sigma_{X}\\sigma_{Y}) = \\rho$ by step 2.',
                                'Substituting into step 1 gives $1 + 1 + 2\\rho$.',
                            ],
                        },
                        {
                            "prompt": 'A variance is never negative, so $2 + 2\\rho \\ge 0$. Solve that for $\\rho$ and write the smallest value $\\rho$ can take.',
                            "answer": '-1',
                            "hint": 'Divide by $2$ and subtract $1$: the inequality reads $\\rho \\ge -1$.',
                        },
                        {
                            "prompt": 'Repeat the argument on the difference. $\\mathrm{Var}(U - V)$ has the cross term subtracted instead of added. Write $\\mathrm{Var}(U - V)$ in terms of $\\rho$.',
                            "answer": '2 - 2\\rho',
                            "hint": 'The only change from step 3 is the sign of the covariance term, because $\\mathrm{Cov}(U, -V) = -\\rho$.',
                            "deconstruct": [
                                '$\\mathrm{Var}(U - V) = \\mathrm{Var}(U) + \\mathrm{Var}(V) - 2\\mathrm{Cov}(U,V)$.',
                                'That is $1 + 1 - 2\\rho$.',
                                'Non-negativity then forces $\\rho \\le 1$, which closes the interval from the other end.',
                            ],
                        },
                        {
                            "prompt": 'Combining, $|\\rho| \\le 1$. Substitute $\\rho = C/(\\sigma_{X}\\sigma_{Y})$ into that and write the largest value $|C|$ can take, in terms of $\\sigma_{X}$ and $\\sigma_{Y}$.',
                            "answer": '\\sigma_{X}\\sigma_{Y}',
                            "hint": '$|C|/(\\sigma_{X}\\sigma_{Y}) \\le 1$, so multiply both sides by $\\sigma_{X}\\sigma_{Y}$.',
                            "deconstruct": [
                                '$|\\rho| \\le 1$ means $|C| \\le \\sigma_{X}\\sigma_{Y}$.',
                                'So a covariance is bounded by the product of the standard deviations — the Cauchy-Schwarz inequality, in the only form this course needs.',
                                'It also shows why a large covariance on its own says nothing: the scale it should be compared against is $\\sigma_{X}\\sigma_{Y}$.',
                            ],
                        },
                    ],
                    "closing": r'''
The bound came from one inequality used twice, and the equality case is the part worth
keeping. $\mathrm{Var}(U - V) = 0$ exactly when $\rho = 1$, and a variable with zero
variance is a constant — so $U - V$ is constant, which unwinds to $Y$ being an exact
increasing linear function of $X$. Correlation reaches $\pm 1$ for a perfect straight
line and for nothing else.

That is also the sharpest available statement of what $\rho$ measures. It is not "how
strongly the variables are related"; it is how close they are to a straight line. The
parabola $Y = X^{2}$ on $\left\{-1, 0, 1\right\}$ is a complete functional relationship with
$\rho = 0$, and no amount of extra data will move that number, because there is nothing
linear in it to find.
''',
                },
            ],
            "quiz": {
                "title": "Moving together",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"$X$ and $Y$ each have variance 4 and are independent. What is $\mathrm{Var}(X + Y)$?",
                        "opts": [
                            r"$2$",
                            r"$4$",
                            r"$8$",
                            r"$16$",
                        ],
                        "a": 2,
                        "why": (
                            r"Independence kills the covariance term, so the variances add: $4 + 4 = 8$. Standard "
                            r"deviations do not add — the sd goes from $2$ to $\sqrt{8} \approx 2.83$, not to $4$. "
                            r"This addition rule is the whole reason the standard error of a mean shrinks like "
                            r"$1/\sqrt{n}$ rather than like $1/n$."
                        ),
                    },
                    {
                        "q": r"$X$ takes the values $-1$, $0$ and $1$ with equal probability, and $Y = X^2$. What is true of the pair?",
                        "opts": [
                            r"The covariance is $0$, yet $Y$ is a function of $X$, so they are dependent",
                            r"The covariance is $0$, so the two are independent",
                            r"The covariance is $1$, and they are dependent",
                            r"The covariance is $-1$, and they are independent",
                        ],
                        "a": 0,
                        "why": (
                            r"$E[X] = 0$ and $E[XY] = E[X^3] = 0$, so the covariance is exactly zero — while knowing "
                            r"$X$ pins $Y$ down completely. The relationship here is a perfect parabola with no "
                            r"linear component at all, and covariance measures only the linear part. Independence "
                            r"implies zero covariance; the converse is false, and this is the standard "
                            r"counterexample."
                        ),
                    },
                    {
                        "q": r"Two services' latencies have covariance $300 \mathrm{ms}^2$, with standard deviations $20$ ms and $30$ ms. What is their correlation?",
                        "opts": [
                            r"$300$",
                            r"$1.5$",
                            r"$0.05$",
                            r"$0.5$",
                        ],
                        "a": 3,
                        "why": (
                            r"Divide the covariance by both standard deviations: $300/(20 \times 30) = 0.5$. The "
                            r"squared-millisecond units cancel, which is the point of the division — switch the "
                            r"measurements to seconds and the covariance changes by a factor of a million while the "
                            r"correlation does not move, and it always lies within $[-1, 1]$."
                        ),
                    },
                    {
                        "q": r"Given a joint pmf over $(X, Y)$, how do you obtain the marginal pmf of $X$?",
                        "opts": [
                            "Multiply the joint masses across each row",
                            r"For each value of $x$, sum the joint masses over every value of $y$",
                            r"Divide each joint mass by $P(Y = y)$",
                            "Take the largest joint mass in each row",
                        ],
                        "a": 1,
                        "why": (
                            r"The event $X = x$ is the union of the disjoint events $X = x$ and $Y = y$ taken over "
                            r"all $y$, so the addition axiom sums them. Dividing by $P(Y = y)$ instead gives a "
                            r"conditional distribution — a legitimate object, but the answer to a different "
                            r"question."
                        ),
                    },
                    {
                        "q": r"The rule $E[X + Y] = E[X] + E[Y]$ holds...",
                        "opts": [
                            r"only when $X$ and $Y$ are independent",
                            "only when their covariance is positive",
                            r"always, whether or not $X$ and $Y$ are related",
                            "only when both variables are discrete",
                        ],
                        "a": 2,
                        "why": (
                            r"Expectation is linear unconditionally: it is a weighted sum, and sums split apart "
                            r"regardless of any dependence between the terms. Variance is the operation that needs "
                            r"independence, since the cross term $2\mathrm{Cov}(X, Y)$ only disappears when the "
                            r"covariance is zero. Applying the variance rule as though it were the expectation rule "
                            r"is the most common route to a wrong standard error."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M6
        {
            "title": "Simulation, the law of large numbers and the CLT",
            "summary": "Seeded Monte Carlo, and the two limit theorems that make it trustworthy.",
            "concepts": [
                "A pseudo-random generator is a deterministic function of its seed — reproducibility is a choice",
                "The weak law of large numbers: the sample mean converges in probability to E[X]",
                "Convergence is in probability, not monotone — a curve that wobbles is not a bug",
                "The central limit theorem: sample means approach a normal shape whatever the parent distribution",
                "The standard error of the mean is sigma / sqrt(n), so precision costs quadratically",
                "The unbiased sample variance divides by n - 1; dividing by n underestimates systematically",
                "Binning a sample into a histogram, and what its shape can and cannot tell you",
            ],
            "read": [
                {
                    "title": 'The average you can watch converge, and the two theorems that let you stop',
                    "minutes": 15,
                    "body": r'''
A service times out on $30$ per cent of requests. Rather than compute anything, throw
requests at it and count. Here is the running fraction of timeouts from one stream, read
off at five points.

```text
    n =     10   running mean = 0.40000   error = 0.10000
    n =    100   running mean = 0.33000   error = 0.03000
    n =   1000   running mean = 0.30300   error = 0.00300
    n =  10000   running mean = 0.29200   error = 0.00800
    n = 100000   running mean = 0.29796   error = 0.00204
```

Two features of that table need accounting for before anyone should trust an answer
produced this way. The error shrinks, from $0.1$ to $0.002$, and that shrinking is the
entire justification for answering a probability question by counting rather than by
algebra. But it does not shrink *steadily*: the error at $n = 10{,}000$ is nearly three
times the error at $n = 1000$. Watching that on a progress bar, you would suspect a bug.
There is no bug, and this unit is about why — and about how many more requests it would
take to buy another decimal place.

## A seeded generator is a function, not a source of luck

The word "random" in `random.random` is a courtesy. A pseudo-random generator holds an
internal state, and each call returns a deterministic function of that state and then
advances it. Fix the starting state and the entire sequence is fixed.

```python
import random

a = random.Random(4242)
b = random.Random(4242)
print([round(a.random(), 6) for _ in range(3)])
print([round(b.random(), 6) for _ in range(3)])
```

```text
[0.862451, 0.415694, 0.028451]
[0.862451, 0.415694, 0.028451]
```

Reproducibility is therefore a choice, and the lab makes it for you by requiring
`random.Random(seed)` — a private stream — rather than the module-level `random.random`.
The difference matters more than it reads. The module-level functions share one global
state, so a logging call or a shuffle somewhere else in the program consumes draws from
the same stream and silently changes your numbers. A defect that shows up one run in
fifty is then unreproducible, which converts a bug into a rumour. A private generator per
experiment means `lln_curve(20250901, 0.3, [10, 100])` returns the same pair today and
next year.

## Why the average converges, and exactly how fast

The convergence is not a mystery to be believed; it falls out of the variance of a sum.
Let $X_1, \dots, X_n$ be independent with common mean $\mu$ and variance $\sigma^{2}$.
Module 5 showed that $\mathrm{Var}(A + B) = \mathrm{Var}(A) + \mathrm{Var}(B) +
2\,\mathrm{Cov}(A, B)$, and independence sends every covariance to zero, so the variance
of the sum is $n\sigma^{2}$. Scaling divides variance by the square of the scale factor,
so for the sample mean $\bar{X} = \frac{1}{n}\sum X_i$,

$$\mathrm{Var}(\bar{X}) = \frac{1}{n^{2}} \cdot n\sigma^{2} = \frac{\sigma^{2}}{n},
\qquad \mathrm{SE}(\bar{X}) = \frac{\sigma}{\sqrt{n}} .$$

That single line is the whole engine. The average of $n$ draws has the same centre as one
draw and a spread smaller by $\sqrt{n}$. Turning it into a statement about probability —
that $P(|\bar{X} - \mu| > \varepsilon)$ goes to zero for every $\varepsilon > 0$, which is
the **weak law of large numbers** — takes one further step, and module 7 supplies it by
applying Chebyshev's inequality to $\bar{X}$.

Now go back to the wobbling table. The draws are Bernoulli$(0.3)$, so
$\sigma^{2} = p(1-p) = 0.21$ and the standard error is $\sqrt{0.21/n}$. Measure each error
in those units, on the very stream the table came from.

```python
import math
import random

p = 0.3
rng = random.Random(20250901)
hits = 0
for n in range(1, 100001):
    if rng.random() < p:
        hits += 1
    if n in (10, 100, 1000, 10000, 100000):
        mean = hits / n
        se = math.sqrt(p * (1 - p) / n)
        print(f"n = {n:>6}   mean = {mean:.5f}   error = {abs(mean - p):.5f}   "
              f"SE = {se:.5f}   error/SE = {abs(mean - p) / se:.2f}")
```

```text
n =     10   mean = 0.40000   error = 0.10000   SE = 0.14491   error/SE = 0.69
n =    100   mean = 0.33000   error = 0.03000   SE = 0.04583   error/SE = 0.65
n =   1000   mean = 0.30300   error = 0.00300   SE = 0.01449   error/SE = 0.21
n =  10000   mean = 0.29200   error = 0.00800   SE = 0.00458   error/SE = 1.75
n = 100000   mean = 0.29796   error = 0.00204   SE = 0.00145   error/SE = 1.41
```

The apparent regression at $n = 10{,}000$ is a run that landed $1.75$ standard errors out,
following one that landed a fifth of a standard error out. Both are unremarkable; it is
the earlier point that was lucky. Convergence in probability is a statement about the
*distribution* of the error, not a promise that any particular run improves at every step,
and the lab's `lln_curve` returns the whole list of checkpoints so that this is visible
rather than asserted.

## Precision costs quadratically

Because the error scales as $1/\sqrt{n}$, cutting it in half costs four times the work.
Put a number on it. To pin a Bernoulli$(0.3)$ probability to within $\pm 0.001$ with about
$95$ per cent confidence you need $1.96\,\sigma/\sqrt{n} \le 0.001$, so

$$n \ge \frac{1.96^{2} \times 0.21}{0.001^{2}} = 806{,}736 .$$

Another decimal place — $\pm 0.0001$ — costs a hundred times that, over eighty million
draws. Monte Carlo buys the first three digits cheaply and the fourth painfully, and
knowing which of those you are in is the difference between a five-second script and an
overnight job. The relationship is checkable directly:

```python
import math
import random

for n in (4, 16, 64):
    rng = random.Random(99)
    means = [sum(rng.random() for _ in range(n)) / n for _ in range(4000)]
    mu = sum(means) / len(means)
    sd = math.sqrt(sum((m - mu) ** 2 for m in means) / (len(means) - 1))
    print(f"n = {n:>2}   sd of the {len(means)} means = {sd:.5f}   "
          f"sigma/sqrt(n) = {math.sqrt(1 / 12) / math.sqrt(n):.5f}")
```

```text
n =  4   sd of the 4000 means = 0.14469   sigma/sqrt(n) = 0.14434
n = 16   sd of the 4000 means = 0.07177   sigma/sqrt(n) = 0.07217
n = 64   sd of the 4000 means = 0.03608   sigma/sqrt(n) = 0.03608
```

Uniform$(0,1)$ has variance $1/12$, and quadrupling $n$ halves the observed scatter at
every step. That is exactly the assertion the lab's `clt_means` checks, and the division
by `len(means) - 1` rather than `len(means)` is the unbiased sample variance: the
deviations are measured about $\bar{x}$, which was fitted from the same data and therefore
sits closer to them than the true mean does, so dividing by $n$ understates the spread
every time. Module 8 works out the exact size of that shortfall.

## The shape, not the spread

The law of large numbers says where the sample mean goes. It says nothing about what the
scatter *looks like* on the way, and that is a separate theorem. Take means of eight
uniform draws and bin ten thousand of them.

```python
import random

rng = random.Random(2024)
means = [sum(rng.random() for _ in range(8)) / 8 for _ in range(10000)]
counts = [0] * 10
for v in means:
    counts[int(v * 10)] += 1
for i, c in enumerate(counts):
    print(f"[{i / 10:.1f}, {(i + 1) / 10:.1f})  {c:>5}  {'#' * (c // 100)}".rstrip())
```

```text
[0.0, 0.1)      0
[0.1, 0.2)     15
[0.2, 0.3)    218  ##
[0.3, 0.4)   1410  ##############
[0.4, 0.5)   3381  #################################
[0.5, 0.6)   3299  ################################
[0.6, 0.7)   1442  ##############
[0.7, 0.8)    220  ##
[0.8, 0.9)     15
[0.9, 1.0)      0
```

A single uniform draw is flat — every bin near a thousand. Averaging eight of them
produces a bell, and it took eight, not eight hundred. The **central limit theorem** says
this happens whatever the parent distribution is, provided its variance is finite: the
standardised mean $(\bar{X} - \mu)/(\sigma/\sqrt{n})$ has mean $0$ and variance $1$ by the
two facts derived above, and its *shape* settles onto the standard normal curve. That is
why the lab pairs `standardise` with `histogram`: standardising removes the centre and
the scale, and whatever is left is the claim the theorem actually makes.

## The mistake, and why it is tempting

"It has come up heads too often, so tails is due." The law of large numbers is offered as
the justification, and the law says nothing of the kind.

```python
import random

rng = random.Random(31337)
heads = 0
for n in range(1, 1000001):
    if rng.random() < 0.5:
        heads += 1
    if n in (100, 10000, 1000000):
        print(f"n = {n:>7}  heads = {heads:>6}  ratio = {heads / n:.5f}  "
              f"excess over n/2 = {heads - n / 2:+.1f}")
```

```text
n =     100  heads =     50  ratio = 0.50000  excess over n/2 = +0.0
n =   10000  heads =   5026  ratio = 0.50260  excess over n/2 = +26.0
n = 1000000  heads = 500551  ratio = 0.50055  excess over n/2 = +551.0
```

The ratio converges to $0.5$ and the surplus of heads **grows**, from nothing to $551$.
Both are the same arithmetic seen through different denominators. The excess
$H - n/2$ is a sum of $n$ independent $\pm\frac{1}{2}$ terms, so its standard deviation is
$\sqrt{n}/2$ — at a million flips, $500$, and the observed $551$ is an ordinary result.
The ratio is that excess divided by $n$, so its typical size is $\frac{1}{2\sqrt{n}}$,
which shrinks. Nothing repays anything. The early surplus is not cancelled; it is
out-voted by later flips that know nothing about it.

The error is tempting because "evens out" is a fair description of the ratio, and the mind
supplies the counts as though the same sentence covered both. It does not, and the sign of
the difference between the two is worth holding on to: the thing that converges is the one
you divided by $n$.

## Where it stops

**Finite variance is a real condition.** Draw from a Cauchy distribution — the ratio of
two normals, or $\tan(\pi(U - \frac{1}{2}))$ for uniform $U$ — and its variance is
infinite. The sample mean of $n$ Cauchy draws is distributed exactly as *one* Cauchy draw,
for every $n$, so it never settles anywhere:

```text
    n =     10   running mean =       0.4616
    n =    100   running mean =      -3.5530
    n =   1000   running mean =       3.2918
    n =  10000   running mean =      -0.4165
    n = 100000   running mean =      -4.2297
```

A hundred thousand draws leave the average further from zero than ten did. Averaging is
not a universal purifier, and file sizes, city populations and losses on financial trades
are all heavy-tailed enough for this to matter in practice.

**Independence is a real condition too.** The step that removed the covariances is the
only place independence entered, and if the draws are correlated the variance of the mean
is larger than $\sigma^{2}/n$ — sometimes very much larger. Consuming one generator inside
two nested loops so that the outer iterations share draws is the usual way to arrange this
by accident, which is another reason the lab gives every experiment its own seed.

**The central limit theorem is about the middle.** At any fixed $n$ the normal
approximation is best near the centre and worst far out in the tails, which is exactly
where a question about a rare event lives. Estimating a probability of $10^{-6}$ by
counting how often it happened in a million draws is a plan whose expected count is one.
Module 7's bounds exist for that case, because they do not need $n$ to be large.

The lab, **Convergence you can watch**, asks for `sample_mean`, the unbiased
`sample_variance` and `sample_sd`, `standardise`, `lln_curve`, `clt_means` and
`histogram` — every one of them seeded, so the curve you plot is the curve the checks
plot. The final assertion is the $1/\sqrt{n}$ law itself: quadruple $n$ and the scatter of
the means must halve.
''',
                },
            ],
            "quiz": {
                "title": "What converges, how fast, and what does not",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"A running mean of Bernoulli$(0.3)$ draws is $0.30300$ after $1000$ draws and $0.29200$ after $10{,}000$. Has something gone wrong with the simulation?",
                        "opts": [
                            r"Yes — the law of large numbers guarantees the error decreases as more draws are added, so a larger error at a larger $n$ indicates a defective stream",
                            r"Yes, but only because the two checkpoints came from one stream; independent streams at each checkpoint would have produced a monotone sequence of errors",
                            r"No — the errors are $0.21$ and $1.75$ standard errors, and neither is unusual",
                            r"No — a running mean need not approach $p$ at all",
                        ],
                        "a": 2,
                        "whys": [
                            r"The law is about the probability of a large error shrinking, not about any single path descending. A guarantee that every step improves would make a lucky early draw permanently binding, which no theorem could deliver.",
                            r"Independent streams would not help: each checkpoint would still land at a random distance from $p$, and a monotone sequence of errors would be a remarkable coincidence rather than the norm. The single stream is not the source of the wobble.",
                            r"$\sqrt{0.21/1000} = 0.0145$ and $\sqrt{0.21/10000} = 0.0046$; the errors were $0.0030$ and $0.0080$.",
                            r"It does approach $p$, in the precise sense that the probability of missing by more than any fixed amount goes to zero. Denying convergence outright throws away the entire justification for estimating anything by counting.",
                        ],
                        "why": r"""
Measure each error in standard errors rather than in absolute units. With
$\sigma^{2} = p(1-p) = 0.21$, the standard error is $\sqrt{0.21/1000} = 0.0145$ at the
first checkpoint and $\sqrt{0.21/10000} = 0.0046$ at the second, so an error of $0.0030$
is $0.21$ SE and an error of $0.0080$ is $1.75$ SE. It was the earlier point that was
unusually good. Convergence in probability constrains the distribution of the error at
each $n$; it does not order the errors along any particular path, and a run that improves
at every checkpoint would itself be a surprise.
""",
                    },
                    {
                        "q": r"A Monte Carlo estimate currently has a standard error of $0.004$. Roughly how many times the present number of draws is needed to bring it to $0.001$?",
                        "opts": [
                            r"Four times, since the standard error falls in proportion to the number of draws",
                            r"Sixteen times, since the standard error falls as one over the square root of the number of draws",
                            r"Twice, since each doubling of the sample removes one binary digit of uncertainty from the estimate",
                            r"It depends entirely on the variance of the underlying draws, which the question does not give",
                        ],
                        "a": 1,
                        "whys": [
                            r"This reads the standard error as $\sigma/n$ rather than $\sigma/\sqrt{n}$, and it is the optimistic version of the mistake: it promises a fourth decimal place for a hundredth of the work actually required.",
                            r"$\sigma/\sqrt{n}$ must fall by a factor of four, and $\sqrt{16} = 4$.",
                            r"Nothing here is binary, and a doubling multiplies the precision by $\sqrt{2} \approx 1.41$, not by two. The bits-of-precision picture belongs to bisection, where each step genuinely halves an interval.",
                            r"The variance is already inside the $0.004$ you were given, so it cancels: the ratio of the two standard errors is $\sqrt{n_{\text{old}}/n_{\text{new}}}$ whatever $\sigma$ is. The caution is reasonable in general and unnecessary here.",
                        ],
                        "why": r"""
The standard error of a sample mean is $\sigma/\sqrt{n}$, so it is the square root of the
sample size that does the work. Reducing $0.004$ to $0.001$ is a factor of four in
precision and therefore a factor of $16$ in draws. The $\sigma$ never has to be known,
because it appears in both standard errors and cancels in the ratio. This quadratic price
is the defining economics of simulation: three good digits are cheap and the fourth costs
a hundred times the third.
""",
                    },
                    {
                        "q": r"After a million fair coin flips a simulation reports $500{,}551$ heads. What does the law of large numbers say about the surplus of $551$?",
                        "opts": [
                            r"That later flips will tend to run short of heads until the surplus is worked off",
                            r"That the surplus is evidence of a biased generator, since a fair stream would hold the two counts close to level throughout",
                            r"That the ratio converges while the surplus typically grows like $\sqrt{n}$, and $551$ is close to the $500$ expected",
                            r"That the surplus is meaningless, because the law describes only infinite sequences",
                        ],
                        "a": 2,
                        "whys": [
                            r"Nothing in the mechanism can arrange this. Each flip is a fresh half, with no memory of the surplus and no way to consult it, and this is the gambler's fallacy in its most respectable-sounding form.",
                            r"A surplus of $551$ is about $1.1$ standard deviations, which is the least surprising thing a million flips could produce. Expecting the counts to stay level mistakes the convergence of the ratio for convergence of the difference.",
                            r"The excess is a sum of $n$ terms of size $\pm\frac{1}{2}$, so its standard deviation is $\sqrt{n}/2 = 500$.",
                            r"The law does concern a limit, but its content at finite $n$ is exactly the standard error, which is a computable number here. Declaring the surplus meaningless discards the one calculation that explains it.",
                        ],
                        "why": r"""
Write the surplus as $H - n/2$, a sum of $n$ independent terms each $+\frac{1}{2}$ or
$-\frac{1}{2}$. Variances add, so the surplus has standard deviation $\sqrt{n}/2$, which
is $500$ at a million flips — the observed $551$ is an ordinary result. The ratio is that
same surplus divided by $n$, with typical size $1/(2\sqrt{n})$, and that is what shrinks.
So the difference grows and the proportion converges, from the identical arithmetic. No
flip is ever repaid; an early surplus is out-voted by later flips that carry no record of
it.
""",
                    },
                    {
                        "q": r"Ten thousand means of eight uniform draws each are binned, and the histogram is bell-shaped rather than flat. Which theorem is that, and what does it assert?",
                        "opts": [
                            r"The law of large numbers, which asserts that the sample mean approaches the population mean as the sample grows",
                            r"The central limit theorem, which asserts that the standardised sample mean approaches a normal shape",
                            r"Neither: with only eight draws per mean the shape is an artefact of the bin widths chosen for the histogram, and it would flatten under any other binning",
                            r"Both, since the bell narrows around the mean as the number of draws per sample is increased",
                        ],
                        "a": 1,
                        "whys": [
                            r"That law is about the location the mean converges to, and it would be equally satisfied by a scatter that stayed square-shouldered for ever. The picture here is about the shape of the scatter, which is a separate claim.",
                            r"The bell appears at $n = 8$, and it appears whatever the parent distribution is, provided its variance is finite.",
                            r"Rebinning changes the resolution, never the shape: the counts rise towards $0.5$ and fall away from it under any bin width, and a flat parent gives a flat histogram under the same code. The effect is in the data, not the axes.",
                            r"Both theorems are true of this experiment, but the narrowing is the law of large numbers speaking and the bell is the central limit theorem, and the answer welds them into a single claim that neither makes. Keeping them apart is the point of standardising before plotting.",
                        ],
                        "why": r"""
The law of large numbers fixes where the sample mean goes; the central limit theorem
describes the shape of its scatter around that point, and the two are independent claims.
Standardising as $(\bar{X} - \mu)/(\sigma/\sqrt{n})$ removes the centre and the scale —
both already known from the mean and the variance of a sum — and what remains is the
theorem's actual content: that the leftover shape tends to one fixed curve, whatever the
parent distribution was. A flat uniform reaches a visible bell after averaging only eight
draws, which is why simulation leans on this so heavily.
""",
                    },
                    {
                        "q": r"A running mean of Cauchy draws is $3.29$ at $n = 1000$ and $-4.23$ at $n = 100{,}000$. Why does averaging fail to help here?",
                        "opts": [
                            r"The draws are dependent, because each one is computed from the previous state of the generator",
                            r"The Cauchy distribution has no finite variance, so the $\sigma^{2}/n$ argument has nothing to work with",
                            r"A hundred thousand draws is far too few for a distribution whose support extends over the whole of the real line",
                            r"The mean is being computed in floating point, and the extreme values destroy its precision",
                        ],
                        "a": 1,
                        "whys": [
                            r"Every generator computes each draw from its state, including the ones whose averages converge perfectly well — the stream is designed to behave as independent draws, and does. Blaming the mechanism here would condemn all of Monte Carlo.",
                            r"$\mathrm{Var}(\bar{X}) = \sigma^{2}/n$ needs a finite $\sigma^{2}$, and the mean of $n$ Cauchy draws is distributed as one draw.",
                            r"Unbounded support is not the problem: the normal distribution also lives on the whole line and its sample means converge beautifully. What matters is how much probability sits far out, not how far out the support reaches.",
                            r"Floating point handles these values accurately; the wandering is in the mathematics, not the arithmetic, and exact rational arithmetic would produce the same wandering. This one is worth resisting precisely because numerical explanations are so often right.",
                        ],
                        "why": r"""
Every guarantee in this module descends from $\mathrm{Var}(\bar{X}) = \sigma^{2}/n$, and
that identity presumes a finite $\sigma^{2}$. The Cauchy has none — its tails are heavy
enough that the defining integral diverges — and the consequence is exact rather than
approximate: the average of $n$ Cauchy draws has the same distribution as a single draw,
for every $n$. So a hundred thousand draws are worth precisely one, and the running mean
wanders for ever. Heavy tails are not exotic; file sizes, city populations and trading
losses all misbehave in this direction.
""",
                    },
                    {
                        "q": r"Why does the lab require `random.Random(seed)` rather than the module-level `random.random`?",
                        "opts": [
                            r"The module-level functions draw from a weaker generator, so the numbers they produce fail statistical tests that a private instance passes",
                            r"A private instance owns its state, so unrelated code drawing from the global stream cannot shift the experiment's numbers",
                            r"Module-level draws cannot be seeded at all, which makes any run of the experiment impossible to reproduce afterwards",
                            r"The module-level functions are slower, because each call has to acquire a lock on the shared global state before it can advance it",
                        ],
                        "a": 1,
                        "whys": [
                            r"It is the same Mersenne Twister either way — `random.random` is a bound method of one hidden instance of the very class the lab asks you to create. The quality of the numbers is identical; only their ownership differs.",
                            r"A logging call or a shuffle elsewhere consumes draws from the shared stream, and the experiment silently returns different numbers.",
                            r"`random.seed(...)` exists and works. The trouble is that it seeds a stream everything else in the process shares, so the guarantee it appears to give lasts only until some other code draws from it.",
                            r"Speed is not the issue, and a defect you cannot reproduce costs far more than any per-call overhead. Correctness of the experiment, not its throughput, is what the private instance is protecting.",
                        ],
                        "why": r"""
The module-level functions are bound methods of a single hidden generator shared by the
whole process. Seeding it fixes the sequence only for as long as nothing else draws from
it, and a shuffle, a jitter or a test helper elsewhere consumes values from the same
stream and shifts every number after it. The failure is quiet and intermittent, which
makes a defect that appears one run in fifty impossible to re-run and therefore
impossible to investigate. A private `random.Random(seed)` per experiment means the curve
you plotted is the curve the checks will plot.
""",
                    },
                ],
            },
            "lab": {
                "title": "Convergence you can watch",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Every experiment here takes a seed, so two runs of the same call produce
identical numbers. Use `random.Random(seed)` — a private generator — and never
the module-level `random.random`, which shares global state.

**`sample_mean(xs)`** — `ValueError` on an empty sample.

**`sample_variance(xs)`** — the **unbiased** estimator, dividing by `n - 1`.
`ValueError` for fewer than two values, since one observation says nothing about
spread. **`sample_sd(xs)`** is its square root.

**`standardise(xs)`** — the z-scores `(x - mean) / sd`. `ValueError` when the sd
is zero.

**`lln_curve(seed, p, checkpoints)`** — draw Bernoulli(p) values from **one**
stream and record the running mean at each checkpoint, returning
`[(n, mean_after_n), ...]` in ascending order of `n`. `ValueError` for an empty
checkpoint list or a checkpoint below 1.

**`clt_means(seed, trials, n)`** — `trials` sample means, each of `n` draws from
`Uniform(0, 1)`. `ValueError` when either count is below 1.

**`histogram(values, lo, hi, bins)`** — counts per equal-width bin over
`[lo, hi)`. Values outside the range are ignored; a value exactly equal to `lo`
lands in bin 0. `ValueError` when `bins < 1` or `hi <= lo`.

Uniform(0, 1) has mean 1/2 and variance 1/12, so the means of `n` draws should
scatter around 0.5 with standard deviation `sqrt(1/12) / sqrt(n)`. Quadrupling
`n` should halve that scatter — the checks verify exactly this.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random


def sample_mean(xs):
    """Arithmetic mean. ValueError on an empty sample."""
    # your code here


def sample_variance(xs):
    """Unbiased sample variance, dividing by n - 1."""
    # your code here


def sample_sd(xs):
    """Square root of the unbiased variance."""
    # your code here


def standardise(xs):
    """z-scores. ValueError when the sample has no spread."""
    # your code here


def lln_curve(seed, p, checkpoints):
    """Running mean of Bernoulli(p) draws at each checkpoint."""
    # your code here


def clt_means(seed, trials, n):
    """`trials` sample means, each of n Uniform(0, 1) draws."""
    # your code here


def histogram(values, lo, hi, bins):
    """Counts per equal-width bin over [lo, hi)."""
    # your code here


for n, mean in lln_curve(7, 0.3, [10, 100, 1000, 10000, 50000]):
    print(f"{n:>6}  {mean:.5f}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random


def sample_mean(xs):
    """Arithmetic mean. ValueError on an empty sample."""
    if not xs:
        raise ValueError("the mean of an empty sample is undefined")
    return sum(xs) / len(xs)


def sample_variance(xs):
    """Unbiased sample variance, dividing by n - 1."""
    if len(xs) < 2:
        raise ValueError("need at least two observations to estimate spread")
    mu = sample_mean(xs)
    return sum((x - mu) ** 2 for x in xs) / (len(xs) - 1)


def sample_sd(xs):
    """Square root of the unbiased variance."""
    return math.sqrt(sample_variance(xs))


def standardise(xs):
    """z-scores. ValueError when the sample has no spread."""
    sd = sample_sd(xs)
    if sd == 0:
        raise ValueError("a constant sample cannot be standardised")
    mu = sample_mean(xs)
    return [(x - mu) / sd for x in xs]


def lln_curve(seed, p, checkpoints):
    """Running mean of Bernoulli(p) draws at each checkpoint."""
    if not checkpoints:
        raise ValueError("need at least one checkpoint")
    marks = sorted(checkpoints)
    if marks[0] < 1:
        raise ValueError("checkpoints must be positive")
    rng = random.Random(seed)
    curve = []
    successes = 0
    wanted = set(marks)
    for i in range(1, marks[-1] + 1):
        successes += 1 if rng.random() < p else 0
        if i in wanted:
            curve.append((i, successes / i))
    return curve


def clt_means(seed, trials, n):
    """`trials` sample means, each of n Uniform(0, 1) draws."""
    if trials < 1 or n < 1:
        raise ValueError("trials and n must both be positive")
    rng = random.Random(seed)
    # one stream for the whole experiment keeps the run reproducible
    return [sum(rng.random() for _ in range(n)) / n for _ in range(trials)]


def histogram(values, lo, hi, bins):
    """Counts per equal-width bin over [lo, hi)."""
    if bins < 1:
        raise ValueError("need at least one bin")
    if hi <= lo:
        raise ValueError("hi must be greater than lo")
    counts = [0] * bins
    width = (hi - lo) / bins
    for value in values:
        if value < lo or value >= hi:
            continue
        index = int((value - lo) / width)
        counts[min(index, bins - 1)] += 1   # guard the top edge against rounding
    return counts


for n, mean in lln_curve(7, 0.3, [10, 100, 1000, 10000, 50000]):
    print(f"{n:>6}  {mean:.5f}")
'''}],
                "hints": [
                    "`sample_variance` should call `sample_mean` rather than recomputing the mean, so the two can never disagree.",
                    "`lln_curve` must draw from a single stream: loop once to the largest checkpoint, keep a running count of successes, and record when the index is a checkpoint.",
                    "`random.Random(seed)` gives an isolated generator; two calls with the same seed produce the same sequence, which is what makes these checks possible.",
                    "In `histogram`, `int((value - lo) / width)` can land on `bins` for a value a hair under `hi` — clamp with `min(index, bins - 1)`.",
                ],
                "tests": [
                    {"name": "The estimators are unbiased and guarded", "code": r'''
_xs = [2, 4, 4, 4, 5, 5, 7, 9]
assert sample_mean(_xs) == 5.0, f"sample_mean gave {sample_mean(_xs)!r}, expected 5.0"
assert abs(sample_variance(_xs) - 32 / 7) < 1e-12, \
    f"sample_variance gave {sample_variance(_xs)!r}, expected 32/7 — divide by n - 1"
assert abs(sample_sd(_xs) - (32 / 7) ** 0.5) < 1e-12
assert sample_variance([3, 5]) == 2.0, f"Got {sample_variance([3, 5])!r}, expected 2.0"
try:
    sample_mean([])
    assert False, "sample_mean([]) should raise ValueError"
except ValueError:
    pass
for _bad in ([], [4]):
    try:
        sample_variance(_bad)
        assert False, f"sample_variance({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "standardise centres and scales", "code": r'''
_z = standardise([2, 4, 4, 4, 5, 5, 7, 9])
assert abs(sample_mean(_z)) < 1e-12, f"z-scores should average 0, got {sample_mean(_z)!r}"
assert abs(sample_sd(_z) - 1.0) < 1e-12, f"z-scores should have sd 1, got {sample_sd(_z)!r}"
try:
    standardise([3, 3, 3])
    assert False, "A constant sample has no spread and should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "histogram bins and clamps", "code": r'''
assert histogram([0.0, 0.1, 0.5, 0.9], 0.0, 1.0, 2) == [2, 2], \
    f"Got {histogram([0.0, 0.1, 0.5, 0.9], 0.0, 1.0, 2)!r}"
assert histogram([1.0, -0.5, 3.0], 0.0, 1.0, 4) == [0, 0, 0, 0], \
    "hi is exclusive and values outside the range are dropped"
assert histogram([0.999999999], 0.0, 1.0, 4) == [0, 0, 0, 1], "The top bin must not overflow"
assert sum(histogram([0.2] * 7, 0.0, 1.0, 5)) == 7, "Every in-range value is counted once"
for _bad in ((0.0, 1.0, 0), (1.0, 1.0, 4), (1.0, 0.0, 4)):
    try:
        histogram([0.5], *_bad)
        assert False, f"histogram(..., {_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The law of large numbers, watched", "code": r'''
_curve = lln_curve(7, 0.3, [10, 100, 1000, 10000, 50000])
assert [n for n, _ in _curve] == [10, 100, 1000, 10000, 50000], f"Got {_curve!r}"
assert lln_curve(7, 0.3, [10, 100]) == _curve[:2], \
    "The same seed and prefix must reproduce the same running means"
assert abs(_curve[-1][1] - 0.3) < 0.01, \
    f"After 50000 draws the mean is {_curve[-1][1]!r}, it should be within 0.01 of 0.3"
assert abs(_curve[-1][1] - 0.3) < abs(_curve[0][1] - 0.3), \
    "The estimate at 50000 draws should beat the one at 10 draws"
for _bad in ([], [0], [5, -1]):
    try:
        lln_curve(7, 0.3, _bad)
        assert False, f"lln_curve with checkpoints {_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Sample means centre on the true mean", "code": r'''
_means = clt_means(11, 400, 50)
assert len(_means) == 400, f"Expected 400 sample means, got {len(_means)}"
assert all(0.0 <= m <= 1.0 for m in _means), "A mean of Uniform(0, 1) draws stays in [0, 1]"
assert abs(sample_mean(_means) - 0.5) < 0.01, \
    f"The means average {sample_mean(_means)!r}; Uniform(0, 1) has mean 0.5"
assert clt_means(11, 5, 3) == clt_means(11, 5, 3), "The same seed must give the same experiment"
assert clt_means(11, 5, 3) != clt_means(12, 5, 3), "A different seed must give a different run"
for _bad in ((0, 5), (5, 0), (-1, 5)):
    try:
        clt_means(1, *_bad)
        assert False, f"clt_means(1, {_bad[0]}, {_bad[1]}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The standard error scales as 1/sqrt(n)", "code": r'''
import math as _math
_theory = _math.sqrt(1 / 12) / _math.sqrt(50)
_sd = sample_sd(clt_means(11, 400, 50))
assert abs(_sd - _theory) / _theory < 0.20, \
    f"Spread of the sample means is {_sd!r}, theory says about {_theory!r}"
_sd25 = sample_sd(clt_means(3, 500, 25))
_sd100 = sample_sd(clt_means(3, 500, 100))
assert _sd100 < _sd25, "Four times as many draws must reduce the scatter"
assert 1.6 < _sd25 / _sd100 < 2.5, \
    f"The ratio of the two spreads is {_sd25 / _sd100!r}; sqrt(4) = 2 is the prediction"
'''},
                    {"name": "The sampling distribution is bell-shaped", "code": r'''
_z = standardise(clt_means(5, 600, 40))
_counts = histogram(_z, -3.0, 3.0, 6)
assert sum(_counts) > 570, f"Almost every z-score should fall within 3 sd, got {sum(_counts)}"
assert _counts[2] + _counts[3] > _counts[0] + _counts[5] * 3, \
    f"The centre bins should dominate the tails, counts were {_counts!r}"
assert _counts[2] > _counts[1] and _counts[3] > _counts[4], \
    f"The histogram should fall away from the centre, counts were {_counts!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M7
        {
            "title": "Tail bounds and the union bound",
            "summary": (
                "How far a random quantity can wander from its mean, bounded without "
                "knowing its distribution — the guarantees under hashing, load "
                "balancing and sampling."
            ),
            "concepts": [
                r"Markov's inequality bounds a non-negative variable from its mean alone: $P(X \ge a) \le E[X]/a$",
                r"Chebyshev's inequality adds the variance — $P(|X - \mu| \ge k\sigma) \le 1/k^2$ — and holds for every distribution with a finite spread",
                r"Applied to a sample mean, whose variance is $\sigma^2/n$, Chebyshev proves the weak law of large numbers in one line",
                r"Chernoff and Hoeffding bounds decay like $e^{-2n\varepsilon^2}$ rather than $1/n$, which is why a few thousand samples pin a proportion tightly",
                r"The union bound $P(A_1 \cup \cdots \cup A_n) \le P(A_1) + \cdots + P(A_n)$ assumes no independence, and turns a per-item failure rate into a whole-system one",
                'Chebyshev is Markov applied to $(X - \\mu)^{2}$, which is non-negative whatever $X$ does — one result used twice, not two results to remember',
                "Markov's derivation drops a sum of non-negative terms, so without $X \\ge 0$ it inverts: a uniform variable on $[-10, 10]$ has mean $0$ and true $P(X \\ge 5) = 1/4$, against a formula returning $0$",
                'A bound is not an estimate — on $10{,}000$ fair flips $P(X \\ge 5500)$ is at most $0.909$ by Markov, $0.01$ by Chebyshev and $1.93 \\times 10^{-22}$ by Hoeffding, against an exact $7.76 \\times 10^{-24}$',
                "Chebyshev prices a confidence at $\\sigma^{2}/(\\delta\\varepsilon^{2})$ samples, linear in $1/\\delta$; Hoeffding's stronger assumptions buy a logarithmic price instead, which is why the assumptions are worth having",
            ],
            "read": [
                {
                    "title": 'Guarantees you can prove without knowing the distribution',
                    "minutes": 14,
                    "body": r'''
A queue has average length $10$. Nobody will tell you the distribution of its length —
not the shape, not the variance, nothing beyond the mean and the fact that a queue cannot
be shorter than empty. What can you honestly say about the probability that it exceeds
$50$?

Something, as it turns out, and the something is provable in three lines. That is the
business of this module: results that hold for **every** distribution satisfying a short
list of conditions, bought by giving up any hope of an exact answer.

## Markov, derived

Let $X \ge 0$ and let $a > 0$. Split the expectation over the two regions:

$$E[X] = \sum_{x < a} x\,p(x) + \sum_{x \ge a} x\,p(x) .$$

Drop the first sum. This is where non-negativity earns its place — every term in it is
$\ge 0$, so removing them can only decrease the total:

$$E[X] \ge \sum_{x \ge a} x\,p(x) .$$

In the remaining sum every $x$ is at least $a$, so replacing each by $a$ decreases it
again:

$$E[X] \ge a \sum_{x \ge a} p(x) = a\,P(X \ge a) .$$

Divide by $a$:

$$P(X \ge a) \le \frac{E[X]}{a} .$$

The queue: $P(\text{length} \ge 50) \le 10/50 = 0.2$. An upper bound, from the mean
alone.

## Chebyshev is Markov, applied to the right variable

The concepts list gives Markov and Chebyshev as two facts. They are one fact used twice,
and seeing that is worth more than memorising both.

Let $X$ have mean $\mu$ and standard deviation $\sigma$. The variable $Y = (X - \mu)^{2}$
is non-negative — whatever $X$ does — so Markov applies to it. Its mean is
$E[(X-\mu)^{2}] = \sigma^{2}$, by definition of variance. Take the threshold
$a = k^{2}\sigma^{2}$:

$$P\left((X-\mu)^{2} \ge k^{2}\sigma^{2}\right) \le \frac{\sigma^{2}}{k^{2}\sigma^{2}}
= \frac{1}{k^{2}} .$$

The event on the left is exactly $|X - \mu| \ge k\sigma$, since squaring is monotone on
non-negative numbers. So

$$P(|X - \mu| \ge k\sigma) \le \frac{1}{k^{2}} ,$$

for every distribution with a finite variance, whatever its shape. Squaring was the whole
trick: it manufactured a non-negative variable out of one that was free to be negative,
and non-negativity was Markov's only structural demand.

The weak law of large numbers is now one more substitution. The mean of $n$ independent
draws has $\mathrm{Var}(\bar{X}) = \sigma^{2}/n$, so Chebyshev at a fixed distance
$\varepsilon$ gives

$$P(|\bar{X} - \mu| \ge \varepsilon) \le \frac{\sigma^{2}}{n\varepsilon^{2}}
\to 0 .$$

Note what it does not say. It does not say $\bar{X}$ equals $\mu$ for large $n$, and it
does not say the running average approaches $\mu$ without wobbling. It says the
probability of being far off shrinks, and the rate is $1/n$.

## Worked: three bounds on one question

Flip a fair coin $n = 10{,}000$ times and let $X$ be the number of heads. Then
$E[X] = 5000$, $\mathrm{Var}(X) = np(1-p) = 2500$, and $\sigma = 50$. What is
$P(X \ge 5500)$?

**Markov.** $X \ge 0$, so $P(X \ge 5500) \le 5000/5500 = 0.909$.

**Chebyshev.** $5500$ is $500$ above the mean, which is $k = 10$ standard deviations, so
$P(|X - 5000| \ge 500) \le 1/100 = 0.01$.

**Hoeffding.** The flips are independent and each contributes between $0$ and $1$, which
licenses $P(X - E[X] \ge t) \le e^{-2t^{2}/n}$. With $t = 500$ that is
$e^{-50} = 1.93 \times 10^{-22}$.

**The truth.** Summing the binomial exactly gives $7.76 \times 10^{-24}$.

```text
    Markov       <= 0.909                needs: X >= 0
    Chebyshev    <= 0.01                 needs: a finite variance
    Hoeffding    <= 1.93 x 10^-22        needs: independent, bounded terms
    exact              7.76 x 10^-24     needs: the whole distribution
```

Four rows spanning twenty-two orders of magnitude, and every one of them is a true
statement. What separates them is not cleverness but how much was assumed. Markov knows
the mean; Chebyshev knows the spread; Hoeffding knows the terms are independent and
bounded. Each extra assumption buys an enormous amount of tightness, and the exact answer
costs the entire distribution.

That is also the answer to why anyone would use Chebyshev when Hoeffding exists.
Hoeffding needs independence. Chebyshev does not care where the variance came from, so it
survives correlated data that would make Hoeffding's bound a false statement rather than
a loose one.

## The mistake, and why it is tempting

Markov's $0.909$ is not an estimate of anything. It is a ceiling, and the true value here
is below it by a factor of $10^{23}$. The error is reading a bound as an approximation
and reporting "about a $90$ per cent chance the queue exceeds $50$", when what was proved
is "no more than".

The reason the error is tempting is that a bound and an estimate are both single numbers
with the same units, and the inequality sign is the only thing distinguishing them. The
defence is to ask what the bound would say in a case you can check. Chebyshev at $k = 2$
promises at most $1/4$; for a normal variable the true two-sided tail is $0.0455$, five
and a half times smaller. A bound that is loose by five times on a distribution you know
is not going to be tight on one you do not.

The union bound has the same character and one extra failure mode. For $1000$ tasks each
failing with probability at most $0.0001$,

$$P(\text{at least one fails}) \le 1000 \times 0.0001 = 0.1 ,$$

assuming nothing about independence, which is exactly why it survives correlated failures
— tasks sharing a rack, a disk, a deployment. But push it: at $20{,}000$ tasks the same
sum gives $2$, and the bound degenerates into the true and useless claim $P \le 1$. A
union bound that has passed one is not wrong; it has stopped saying anything.

## When the union bound is exact, and when it is worst

The union bound is the one result here with a clean account of its own tightness, which
makes it a good place to see what "loose" means precisely.

$$P(A_1 \cup \cdots \cup A_n) \le P(A_1) + \cdots + P(A_n)$$

Module 1 derived it by noting that inclusion-exclusion subtracts the overlaps, and
dropping every correction can only overshoot. So the bound is **exact** when there are no
overlaps: two disjoint events at $0.3$ and $0.4$ have union $0.7$, and the bound says
$0.7$. It is at its worst when the events coincide: two copies of the same event at
$0.4$ have union $0.4$, and the bound says $0.8$ — too large by a factor of two, and by a
factor of $n$ for $n$ copies.

That gives a usable rule of thumb. The union bound costs little when the failure modes
are close to disjoint — one disk failing, a different rack losing power, a distinct
service timing out — and costs a factor approaching $n$ when they are really the same
failure counted $n$ times. Its indifference to independence is what makes it safe; its
indifference to *overlap* is what makes it loose.

## Where each one stops

**Markov needs non-negativity, and silently gives nonsense without it.** Let $X$ be
uniform on $[-10, 10]$, so $E[X] = 0$. The true $P(X \ge 5)$ is $\frac{1}{4}$. The
formula $E[X]/a$ returns $0/5 = 0$, so the "bound" asserts $0.25 \le 0$. The dropped sum
in the derivation was the step that required $x \ge 0$, and when negative values are
present dropping it *increases* rather than decreases the total.

**Chebyshev needs a finite variance.** Not a small one — a finite one. Latency and file
sizes are routinely modelled with heavy tails, and a Pareto distribution with shape
parameter below $2$ has infinite variance, so $1/k^{2}$ is not loose there but
inapplicable. The bound cannot be rescued by using the sample variance either: that
number is finite for every finite sample, including samples drawn from a distribution
that has none.

**Hoeffding needs independence and boundedness together.** Dropping either breaks it, and
the exponential rate is what is lost. The bound also decays in $n$ at fixed $\varepsilon$
— asking for higher precision as $n$ grows changes the trade entirely, which is the
calculation behind choosing a sample size rather than reporting one.
''',
                },
            ],
            "derive": [
                {
                    "title": 'Markov, then Chebyshev, then the law of large numbers',
                    "minutes": 12,
                    "vars": ['E_X', 'a', 'mu', 'sigma', 'k', 'n', 'epsilon', 'delta'],
                    "brief": r'''
Three results that are usually presented as three facts. They are one fact and two
substitutions, and doing it in that order means only the first has to be remembered.

Write $E_{X}$ for $E[X]$, $\mu$ and $\sigma$ for the mean and standard deviation of $X$,
and $\varepsilon$, $\delta$ for a tolerance and a failure probability. Assume $X \ge 0$
wherever Markov is applied, and a finite $\sigma$ throughout.
''',
                    "steps": [
                        {
                            "prompt": "Markov's inequality, for $X \\ge 0$ and $a > 0$: dropping the terms below $a$ and replacing every remaining $x$ by $a$ gives $E_{X} \\ge a\\,P(X \\ge a)$. Solve for the bound and write the upper bound on $P(X \\ge a)$.",
                            "answer": '\\frac{E_{X}}{a}',
                            "placeholder": 'the mean over the threshold',
                            "hint": 'Divide both sides of $E_{X} \\ge a\\,P(X \\ge a)$ by the positive number $a$.',
                        },
                        {
                            "prompt": 'To reach Chebyshev, apply Markov to $Y = (X - \\mu)^{2}$, which is non-negative whatever $X$ does. Write $E[Y]$ in terms of $\\sigma$.',
                            "answer": '\\sigma^{2}',
                            "hint": 'The mean of the squared deviation from the mean is the definition of the variance.',
                        },
                        {
                            "prompt": 'Now take the threshold $a = k^{2}\\sigma^{2}$ in step 1, with $E_{X}$ replaced by $E[Y]$ from step 2. Write the resulting bound on $P(Y \\ge k^{2}\\sigma^{2})$.',
                            "answer": '\\frac{1}{k^{2}}',
                            "hint": 'The bound is $\\sigma^{2}/(k^{2}\\sigma^{2})$, and the $\\sigma^{2}$ factors cancel.',
                            "deconstruct": [
                                'Markov gives $P(Y \\ge a) \\le E[Y]/a = \\sigma^{2}/(k^{2}\\sigma^{2})$.',
                                'Cancelling leaves $1/k^{2}$, with no $\\sigma$ in it at all.',
                                "And $Y \\ge k^{2}\\sigma^{2}$ is the same event as $|X - \\mu| \\ge k\\sigma$, so this is Chebyshev's inequality.",
                            ],
                        },
                        {
                            "prompt": 'Turn to the sample mean of $n$ independent draws. Since the draws are independent their variances add, and dividing by $n$ divides the variance by $n^{2}$. Write $\\mathrm{Var}(\\bar{X})$ in terms of $\\sigma$ and $n$.',
                            "answer": '\\frac{\\sigma^{2}}{n}',
                            "hint": '$\\mathrm{Var}(\\sum X_i) = n\\sigma^{2}$, and $\\mathrm{Var}(cZ) = c^{2}\\mathrm{Var}(Z)$ with $c = 1/n$.',
                        },
                        {
                            "prompt": 'Apply Chebyshev to $\\bar{X}$, whose standard deviation is $\\sigma/\\sqrt{n}$, at an absolute distance $\\varepsilon$. Write the upper bound on $P(|\\bar{X} - \\mu| \\ge \\varepsilon)$ in terms of $\\sigma$, $n$ and $\\epsilon$.',
                            "answer": '\\frac{\\sigma^{2}}{n\\epsilon^{2}}',
                            "hint": "Chebyshev's $1/k^{2}$ with $k\\sigma/\\sqrt{n} = \\varepsilon$, so $k = \\varepsilon\\sqrt{n}/\\sigma$; substitute and simplify.",
                            "deconstruct": [
                                'Set the distance $k$ standard deviations equal to $\\varepsilon$: $k \\cdot \\sigma/\\sqrt{n} = \\varepsilon$.',
                                'So $k^{2} = n\\varepsilon^{2}/\\sigma^{2}$.',
                                'The bound $1/k^{2}$ is therefore $\\sigma^{2}/(n\\varepsilon^{2})$, which tends to zero as $n$ grows — the weak law.',
                            ],
                        },
                        {
                            "prompt": 'Sizing a sample. Set the bound of step 5 equal to a failure probability $\\delta$ and solve for $n$. Write the required $n$ in terms of $\\sigma$, $\\delta$ and $\\epsilon$.',
                            "answer": '\\frac{\\sigma^{2}}{\\delta\\epsilon^{2}}',
                            "hint": 'From $\\sigma^{2}/(n\\varepsilon^{2}) = \\delta$, multiply up and divide by $\\delta$.',
                            "deconstruct": [
                                '$\\sigma^{2}/(n\\varepsilon^{2}) = \\delta$ rearranges to $n = \\sigma^{2}/(\\delta\\varepsilon^{2})$.',
                                'Halving $\\varepsilon$ multiplies the cost by four; making $\\delta$ ten times smaller multiplies it by ten.',
                                'That linear price in $\\delta$ is exactly what Hoeffding improves to a logarithmic one, which is the whole reason to want the stronger assumptions.',
                            ],
                        },
                    ],
                    "closing": r'''
Everything above rests on the one line in step 1, and that line rests on being allowed to
drop a sum of non-negative terms. Take away $X \ge 0$ and the first inequality reverses:
a uniform variable on $[-10, 10]$ has mean $0$, so the formula would claim
$P(X \ge 5) \le 0$ while the true probability is $\frac{1}{4}$.

Step 6 is the practical form and the one to carry. Chebyshev prices a confidence at
$\sigma^{2}/(\delta\varepsilon^{2})$ samples — linear in $1/\delta$. Hoeffding, at the
cost of assuming the terms are independent and bounded, prices the same confidence at
about $\ln(1/\delta)/(2\varepsilon^{2})$ — logarithmic in $1/\delta$. Going from
$95$ per cent confidence to $99.9999$ per cent costs twenty thousand times more data
under Chebyshev and about five times more under Hoeffding, on the identical question.
''',
                },
            ],
            "quiz": {
                "title": "Bounding what you cannot compute",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"A request queue has non-negative length with mean 10. What does Markov's inequality say about $P(\text{length} \ge 50)$?",
                        "opts": [
                            r"It is exactly $0.2$",
                            r"It is at most $0.2$",
                            r"It is at least $0.2$",
                            r"It is exactly $0.02$",
                        ],
                        "a": 1,
                        "why": (
                            r"Markov gives $P(X \ge a) \le E[X]/a = 10/50 = 0.2$ — an upper bound and nothing "
                            r"more. The true probability is usually far below it, because Markov uses only the "
                            r"mean and the fact that the variable cannot go negative. That is simultaneously its "
                            r"strength (it needs almost nothing) and its weakness (it knows almost nothing)."
                        ),
                    },
                    {
                        "q": r"A measurement has mean 100 and standard deviation 5. What does Chebyshev say about the probability of landing outside $[90, 110]$?",
                        "opts": [
                            r"At most $1/4$",
                            r"At most $1/2$",
                            r"Exactly $1/20$",
                            r"At most $1/10$",
                        ],
                        "a": 0,
                        "why": (
                            r"The interval is $\mu \pm 2\sigma$, so $k = 2$ and the bound is $1/k^2 = 1/4$. "
                            r"Chebyshev asks only for a finite variance, which is what makes it universal and "
                            r"also what makes it loose: if the measurement happened to be normal the real "
                            r"probability is about $0.05$, five times smaller than the bound allows."
                        ),
                    },
                    {
                        "q": r"A batch job runs 1000 tasks, each failing with probability at most $0.0001$. What can you say about the probability that at least one task fails?",
                        "opts": [
                            r"At most $0.0001$",
                            r"Exactly $0.1$",
                            r"At most $10^{-7}$",
                            r"At most $0.1$",
                        ],
                        "a": 3,
                        "why": (
                            r"The union bound adds the individual probabilities: $1000 \times 0.0001 = 0.1$ is an "
                            r"upper bound on the probability of the union, not the value of it. Nothing here "
                            r"assumed the tasks were independent, which is exactly why the bound survives "
                            r"correlated failures — and why it collapses into the useless claim "
                            r"$P \le 1$ once the sum passes one."
                        ),
                    },
                    {
                        "q": r"Why is a Chernoff or Hoeffding bound preferred to Chebyshev for the mean of $n$ independent trials?",
                        "opts": [
                            "It needs fewer assumptions about the variables",
                            "It gives the exact probability rather than a bound",
                            r"Its bound falls exponentially in $n$ rather than like $1/n$",
                            "It applies to variables that are not independent",
                        ],
                        "a": 2,
                        "why": (
                            r"Chebyshev on a sample mean gives $\sigma^2/(n\varepsilon^2)$, so ten times the "
                            r"confidence costs ten times the data. Hoeffding gives roughly $e^{-2n\varepsilon^2}$, "
                            r"so the same tightening costs a constant number of extra samples. The price is a "
                            r"stronger assumption, not a weaker one: the terms must be independent and bounded."
                        ),
                    },
                    {
                        "q": "How does Chebyshev's inequality prove the weak law of large numbers?",
                        "opts": [
                            r"By showing the sample mean equals $\mu$ once $n$ is large enough",
                            r"By bounding $P(|\bar{x} - \mu| \ge \varepsilon)$ with $\sigma^2/(n\varepsilon^2)$, which tends to zero",
                            "By showing that every sequence of running means is monotone",
                            "By assuming the parent distribution is normal",
                        ],
                        "a": 1,
                        "why": (
                            r"The sample mean of $n$ independent draws has variance $\sigma^2/n$, so Chebyshev "
                            r"bounds the chance of missing $\mu$ by more than any fixed $\varepsilon$ with "
                            r"$\sigma^2/(n\varepsilon^2)$ — and that goes to zero. Note what it does not say: "
                            r"the mean never has to *equal* $\mu$, and the running curve is free to wobble on the "
                            r"way down, which is precisely what the simulation lab showed happening."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M8
        {
            "title": "Estimators, likelihood and the bootstrap",
            "summary": (
                "Where an estimator comes from, how to judge one, and how to get its "
                "uncertainty when no closed form is available."
            ),
            "concepts": [
                r"An estimator is itself a random variable with a sampling distribution, a bias $E[\hat{\theta}] - \theta$ and a variance, combined as $\mathrm{MSE} = \mathrm{bias}^2 + \mathrm{variance}$",
                r"The squared deviations are taken about $\bar{x}$, which was fitted from the same data and so makes them too small — dividing by $n - 1$ corrects that shortfall exactly",
                r"Maximum likelihood: write $P(\text{data} | \theta)$, take logs, differentiate and solve — for Bernoulli it returns $\hat{p} = k/n$, which is how you know the method is sane",
                r"A confidence interval is $\hat{\theta} \pm t \cdot \mathrm{SE}$, and the 95% is a property of the procedure across repeated samples, not of the one interval in front of you",
                "The bootstrap resamples the observed data with replacement, giving a sampling distribution for a median, a ratio or a trimmed mean when no formula exists",
                '$E\\left[\\sum (x_i - \\bar{x})^{2}\\right] = (n-1)\\sigma^{2}$ exactly, because $\\bar{x}$ minimises that sum and $E[n(\\bar{x} - \\mu)^{2}] = \\sigma^{2}$ whatever $n$ is — the correction is a cost, not a safety margin',
                'An unbiased $s^{2}$ does not give an unbiased $s$: the square root is concave, so $E[s] < \\sigma$ strictly — about $6$ per cent low at $n = 5$, and no divisor repairs it',
                'Maximum likelihood need not be unbiased in small samples: for $n$ draws from $[0, \\theta]$ it returns $\\max x_i$, whose expectation is $n\\theta/(n+1)$ and which is below $\\theta$ every time',
                'The bootstrap needs a statistic that is smooth in the data, and fails for the maximum, whose resamples can never exceed the largest value already observed',
            ],
            "read": [
                {
                    "title": 'The degree of freedom the mean spends, and the correction it does not buy',
                    "minutes": 14,
                    "body": r'''
An estimator is a recipe: hand it data, it hands back a number. The thing that takes
getting used to is that the number is **random**, because the data were. Run the same
recipe on a second sample from the same population and you get a different answer, and
the distribution of those answers — over samples you did not take — is what "how good is
this estimate" is a question about.

That distribution has a centre and a spread, and the two failure modes have names. The
**bias** is $E[\hat{\theta}] - \theta$, how far the recipe is off on average. The
**variance** is how much it moves from sample to sample. They combine as

$$\mathrm{MSE} = \mathrm{bias}^{2} + \mathrm{variance} ,$$

which is why neither on its own recommends anything. An estimator returning $5.0$
regardless of the data, when the truth is $4.0$, has variance $0$ and is worthless.

## Where the decomposition comes from, and what it licenses

The claim that mean squared error splits into bias squared plus variance is worth
deriving, because the derivation shows why the cross term disappears and the result then
licenses something surprising. Write $b = E[\hat{\theta}] - \theta$ for the bias and
insert $E[\hat{\theta}]$ into the square:

$$E[(\hat{\theta} - \theta)^{2}]
= E[((\hat{\theta} - E[\hat{\theta}]) + b)^{2}]
= \mathrm{Var}(\hat{\theta}) + 2b\,E[\hat{\theta} - E[\hat{\theta}]] + b^{2} .$$

The middle term vanishes because $E[\hat{\theta} - E[\hat{\theta}]] = 0$ — a deviation
from the mean has mean zero — and $b$ is a constant that comes outside. So
$\mathrm{MSE} = \mathrm{Var} + \mathrm{bias}^{2}$, exactly.

Now the surprise. Since the two terms trade against each other, a *biased* estimator can
beat an unbiased one. Shrink an unbiased $\hat{\theta}$ toward zero by a factor $c$: the
bias becomes $(c-1)\theta$ and the variance becomes $c^{2}\sigma^{2}$, so

$$\mathrm{MSE}(c) = (c-1)^{2}\theta^{2} + c^{2}\sigma^{2} ,$$

which is minimised at $c = \theta^{2}/(\sigma^{2} + \theta^{2})$, a number strictly below
$1$ whenever $\sigma > 0$. When $\theta^{2} = \sigma^{2}$ the best $c$ is $\frac{1}{2}$,
and the resulting mean squared error is $\theta^{2}/2$ against the unbiased estimator's
$\sigma^{2} = \theta^{2}$ — **half the error, from an estimator that is wrong on
average**. Unbiasedness is a property, not a virtue, and this is the calculation behind
every shrinkage and regularisation method later in the degree.

## Worked: eight measurements, all the way through

Eight response times, in milliseconds:

```text
    12.1   14.3   11.8   15.2   13.4   12.9   14.8   13.1
```

The sample mean is $\bar{x} = 107.6/8 = 13.45$. The sum of squared deviations about it is

$$\sum (x_i - \bar{x})^{2} = 10.58 .$$

Now the question the concepts list answers with an assertion. Why divide that by $7$
rather than by $8$?

Compute the same sum about two other centres:

```text
    about  x-bar = 13.45     10.58     <- the smallest, necessarily
    about          13.00     12.20
    about          14.00     13.00
```

The sample mean is the value that makes the sum of squared deviations as small as it can
possibly be — that is a one-line calculus fact, and it is the entire reason for the
correction. The deviations you can compute are taken about $\bar{x}$, which was fitted
from the same eight numbers. The deviations you *want* are about the true $\mu$, which
you do not know. The first sum is systematically smaller than the second, so dividing by
$8$ would understate the spread every time, not on average by luck but structurally.

The exact size of the shortfall comes out of one identity. Writing $\mu$ for the true
mean,

$$\sum (x_i - \bar{x})^{2} = \sum (x_i - \mu)^{2} - n(\bar{x} - \mu)^{2} .$$

Take expectations. The first term is $n\sigma^{2}$. For the second,
$E[(\bar{x} - \mu)^{2}]$ is the variance of the sample mean, which is $\sigma^{2}/n$, so
the whole second term has expectation $\sigma^{2}$. Therefore

$$E\left[\sum (x_i - \bar{x})^{2}\right] = n\sigma^{2} - \sigma^{2} = (n-1)\sigma^{2} .$$

Dividing by $n - 1$ gives an estimator with expectation exactly $\sigma^{2}$. The
correction is not a safety margin and not a rounding convention: it is the precise cost,
in expectation, of having spent the data once already to locate the centre. One
constraint was imposed — the deviations about $\bar{x}$ sum to zero, so any $n-1$ of them
determine the last — and one degree of freedom is what it cost.

Finishing the example:

$$s^{2} = \frac{10.58}{7} = 1.511429, \qquad s = 1.229402, \qquad
\mathrm{SE} = \frac{s}{\sqrt{8}} = 0.434659 .$$

With $t_{0.975,\,7} = 2.364624$, the $95$ per cent interval is
$13.45 \pm 2.364624 \times 0.434659$, or $[12.4222,\, 14.4778]$. Dividing by $8$ instead
would have given $s^{2} = 1.3225$ and an interval about $6$ per cent narrower — an
overconfident answer, in the direction that matters.

## Maximum likelihood, on a case you can check

Write down the probability of the data as a function of the parameter, then pick the
parameter that makes what happened most probable. For $k$ successes in $n$ Bernoulli
trials the likelihood is proportional to $p^{k}(1-p)^{n-k}$, so the log-likelihood is

$$\ell(p) = k \ln p + (n - k)\ln(1 - p) .$$

Differentiate and set to zero:

$$\frac{k}{p} - \frac{n-k}{1-p} = 0 \quad \Rightarrow \quad k(1-p) = (n-k)p
\quad \Rightarrow \quad \hat{p} = \frac{k}{n} .$$

For $7$ successes in $20$ trials that is $0.35$. The method returns the obvious answer,
which is the point of running it somewhere obvious: it is how you learn to trust it on
the models where intuition offers nothing at all.

## The mistake, and why it is tempting

Here is the one that survives most courses. The sample variance $s^{2}$ is unbiased for
$\sigma^{2}$. **The sample standard deviation $s$ is not unbiased for $\sigma$**, and no
choice of divisor makes it so.

The reason is that the square root is a concave function, and Jensen's inequality says
$E[\sqrt{Y}] \le \sqrt{E[Y]}$ with equality only when $Y$ is constant. Since $s^{2}$
genuinely varies, $E[s] < \sigma$ strictly. For normal data the shortfall is a known
factor:

```text
    n =  2      E[s] = 0.7979 sigma
    n =  5      E[s] = 0.9400 sigma
    n = 10      E[s] = 0.9727 sigma
    n = 30      E[s] = 0.9914 sigma
```

At $n = 5$ the standard deviation you report is on average $6$ per cent too small, and
the correction that fixed the variance did nothing about it. The error is tempting
because unbiasedness feels like a property of a quantity rather than of a *function* of
it, and it does not survive nonlinear transformation. It is the same reason the mean of
the reciprocals is not the reciprocal of the mean, met here in a place where the word
"unbiased" has already been used to signal correctness.

## Where it stops

**Maximum likelihood is not unbiased in general.** Draw $n$ values uniformly from
$[0, \theta]$. The likelihood is zero for any $\theta$ below the largest observation and
decreasing above it, so the maximum-likelihood estimate is $\hat{\theta} = \max x_i$ —
which is below $\theta$ with probability $1$. Its expectation is $n\theta/(n+1)$, so at
$n = 10$ it is about $9$ per cent low, and the bias never changes sign. What maximum
likelihood does promise is consistency and, asymptotically, minimum variance. Those are
large-sample statements, and reading them as small-sample guarantees is a mistake this
example is designed to prevent.

**A confidence interval's $95$ per cent belongs to the procedure, not the interval.**
$[12.4222,\, 14.4778]$ either contains $\mu$ or does not; there is no probability left in
the statement once the data are in. The claim is about the method across repeated
samples. The interval also says nothing about where individual observations fall — that
is a prediction interval, and it is much wider.

**The bootstrap needs the statistic to be smooth in the data.** Resampling with
replacement and recomputing works well for a mean, a median, a ratio or a trimmed mean,
and it is how you get a standard error where no formula exists. It fails for the
*maximum*: a resample can never exceed the largest observed value, so the bootstrap
distribution of the maximum piles mass on that one point and reports far too little
uncertainty — the same $\max x_i$ whose bias was the previous paragraph.
''',
                },
            ],
            "derive": [
                {
                    "title": 'The degree of freedom the mean spends',
                    "minutes": 12,
                    "vars": ['n', 'sigma', 'mu', 'S'],
                    "brief": r'''
Dividing by $n - 1$ is usually asserted, sometimes with a gesture at "degrees of
freedom". Here it is derived, and what comes out is an exact statement: the sum of
squared deviations about the sample mean falls short by exactly one $\sigma^{2}$,
whatever the distribution.

Write $S = \sum_{i=1}^{n}(x_i - \bar{x})^{2}$ for the sum of squared deviations about the
sample mean, $\mu$ and $\sigma$ for the true mean and standard deviation, and take the
draws independent. The identity
$S = \sum (x_i - \mu)^{2} - n(\bar{x} - \mu)^{2}$ is algebra and may be used freely.
''',
                    "steps": [
                        {
                            "prompt": 'Take expectations of the first term on the right. Each $E[(x_i - \\mu)^{2}]$ is the variance of a single draw. Write $E\\left[\\sum (x_i - \\mu)^{2}\\right]$ in terms of $n$ and $\\sigma$.',
                            "answer": 'n\\sigma^{2}',
                            "placeholder": 'n copies of one variance',
                            "hint": 'There are $n$ terms and each has expectation $\\sigma^{2}$; expectation is linear, so they add.',
                        },
                        {
                            "prompt": 'Now the second term. $E[(\\bar{x} - \\mu)^{2}]$ is the variance of the sample mean. Write it in terms of $\\sigma$ and $n$.',
                            "answer": '\\frac{\\sigma^{2}}{n}',
                            "hint": 'Independent variances add, and dividing the sum by $n$ divides its variance by $n^{2}$.',
                        },
                        {
                            "prompt": 'The identity carries a factor of $n$ on that term. Write $E\\left[n(\\bar{x} - \\mu)^{2}\\right]$ in terms of $\\sigma$.',
                            "answer": '\\sigma^{2}',
                            "hint": 'Multiply the previous answer by $n$ and cancel.',
                            "deconstruct": [
                                '$E[n(\\bar{x} - \\mu)^{2}] = n \\cdot E[(\\bar{x} - \\mu)^{2}]$ because $n$ is a constant.',
                                'That is $n \\times \\sigma^{2}/n$.',
                                "The $n$ cancels, leaving exactly one $\\sigma^{2}$ — one variance's worth, whatever $n$ is.",
                            ],
                        },
                        {
                            "prompt": 'Subtract step 3 from step 1, as the identity instructs. Write $E[S]$ in terms of $n$ and $\\sigma$.',
                            "answer": '(n - 1)\\sigma^{2}',
                            "hint": '$n\\sigma^{2} - \\sigma^{2}$, with $\\sigma^{2}$ taken out as a common factor.',
                        },
                        {
                            "prompt": 'To make an unbiased estimator of $\\sigma^{2}$, divide $S$ by whatever makes its expectation exactly $\\sigma^{2}$. Write that estimator in terms of $S$ and $n$.',
                            "answer": '\\frac{S}{n - 1}',
                            "placeholder": 'S over something',
                            "hint": 'If $E[S] = (n-1)\\sigma^{2}$, then dividing $S$ by $n - 1$ gives an expectation of $\\sigma^{2}$.',
                        },
                        {
                            "prompt": 'Finally, price the mistake. If you divided by $n$ instead, what would the expectation of $S/n$ be? Write it in terms of $n$ and $\\sigma$.',
                            "answer": '\\frac{(n - 1)\\sigma^{2}}{n}',
                            "hint": 'Divide the result of step 4 by $n$.',
                            "deconstruct": [
                                '$E[S/n] = E[S]/n = (n-1)\\sigma^{2}/n$.',
                                'That is $\\sigma^{2}$ multiplied by $(n-1)/n$, a number below $1$.',
                                'So dividing by $n$ understates the variance by a factor of $(n-1)/n$ — $50$ per cent too small at $n = 2$, and $10$ per cent at $n = 10$.',
                            ],
                        },
                    ],
                    "closing": r'''
The shortfall is exactly one $\sigma^{2}$, and step 3 shows why it does not depend on
$n$: the factor of $n$ in the identity cancels the $1/n$ in the variance of the mean. One
parameter was estimated from the data, and it cost one variance's worth of squared
deviation — which is what "one degree of freedom" means, stated as an equation rather
than as a slogan.

The same accounting runs through the rest of the course. Fitting a straight line in
module 11 estimates two parameters from the data, and the residual sum of squares is then
divided by $n - 2$ for exactly this reason. The pattern is the number of observations
minus the number of quantities the data were used to locate.

One warning the derivation earns the right to make. Everything above is a statement about
$S$, hence about $s^{2}$. It says nothing about $s$: the square root of an unbiased
estimator is not unbiased, and $E[s] < \sigma$ strictly whenever $s^{2}$ varies at all.
''',
                },
            ],
            "quiz": {
                "title": "Judging an estimate",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"You observe 7 successes in 20 independent Bernoulli trials. What is the maximum-likelihood estimate of $p$?",
                        "opts": [
                            r"$0.5$",
                            r"$0.65$",
                            r"$0.35$",
                            r"$7$",
                        ],
                        "a": 2,
                        "why": (
                            r"The log-likelihood is $k \ln p + (n - k) \ln(1 - p)$; differentiating and setting the "
                            r"result to zero gives $\hat{p} = k/n = 7/20 = 0.35$. Here maximum likelihood confirms "
                            r"the obvious answer, which is the point of running it on a case you already know — the "
                            r"method earns its keep on the models where intuition offers nothing."
                        ),
                    },
                    {
                        "q": "An estimator returns 5.0 no matter what data it is given. The true parameter is 4.0. How would you describe it?",
                        "opts": [
                            "Biased, with zero variance",
                            "Unbiased, with high variance",
                            "Unbiased, with zero variance",
                            "Consistent, but inefficient",
                        ],
                        "a": 0,
                        "why": (
                            r"It never varies, so its variance is $0$; its expectation is $5.0$ against a truth of "
                            r"$4.0$, so its bias is $1.0$ and its mean squared error is $1^2 + 0 = 1$. It is also not "
                            r"consistent, since no amount of extra data will ever move it. Low variance on its own "
                            r"recommends nothing."
                        ),
                    },
                    {
                        "q": "Why does the unbiased sample variance divide by $n - 1$ rather than $n$?",
                        "opts": [
                            "To make the estimate larger, which is the safer direction",
                            "Because one observation is always discarded as an outlier",
                            "To make the units of the result come out right",
                            r"Because the deviations are measured about $\bar{x}$, which minimises them, so they understate the true spread",
                        ],
                        "a": 3,
                        "why": (
                            r"The sample mean is the single value that makes the sum of squared deviations as small "
                            r"as it can be — smaller than the sum about the unknown $\mu$ would have been. One "
                            r"degree of freedom was spent estimating the mean, and dividing by $n - 1$ recovers "
                            r"exactly what that cost, in expectation. It is not a safety margin and not a rounding "
                            r"convention."
                        ),
                    },
                    {
                        "q": r"A 95% confidence interval for a mean comes out as $[2.1, 4.7]$. Which reading is correct?",
                        "opts": [
                            "There is a 95% probability that the true mean lies between 2.1 and 4.7",
                            "If the experiment were repeated many times, 95% of the intervals built this way would contain the true mean",
                            "95% of the individual observations lie between 2.1 and 4.7",
                            "The true mean is 3.4, with 95% certainty",
                        ],
                        "a": 1,
                        "why": (
                            r"The 95% belongs to the *procedure* over repeated samples. The true mean is a fixed "
                            r"number and this particular interval either contains it or does not — there is no "
                            r"probability left in the statement once the data are in. The interval also says nothing "
                            r"about where individual observations fall; that is a prediction interval, and it is "
                            r"much wider."
                        ),
                    },
                    {
                        "q": "What does the bootstrap actually do?",
                        "opts": [
                            "It collects additional data from the population",
                            "It assumes the data are normal and reads a t table",
                            "It resamples the observed data with replacement to approximate the sampling distribution of a statistic",
                            "It removes outliers until the statistic stops moving",
                        ],
                        "a": 2,
                        "why": (
                            r"It treats the sample as a stand-in for the population, draws fresh samples of the same "
                            r"size from it with replacement, and recomputes the statistic each time. The spread of "
                            r"those replicates estimates the standard error. That is how you get an interval for a "
                            r"median or a ratio, neither of which has a convenient formula — and it is what the "
                            r"capstone uses."
                        ),
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M9
        {
            "title": "Estimation and hypothesis testing",
            "summary": "Two-sample comparison and goodness of fit, done by hand against a printed table.",
            "concepts": [
                "Point estimate, standard error and confidence interval as three views of one estimate",
                "The null hypothesis is the claim you try to reject, never the one you try to prove",
                "The two-sample t statistic as a signal-to-noise ratio: mean difference over its standard error",
                "Welch's variant drops the equal-variance assumption at the cost of a fractional degrees of freedom",
                "The Welch-Satterthwaite formula, and reading a table conservatively by rounding df down",
                "Chi-square goodness of fit: summed squared residuals scaled by expected counts, with k - 1 df",
                "A rejected null is not a large effect, and a p-value is not the probability of the hypothesis",
            ],
            "read": [
                {
                    "title": 'Nine point two units of difference, and the noise it has to clear',
                    "minutes": 15,
                    "body": r'''
Two versions of a checkout page ran for five days each. The numbers are sign-ups per
thousand sessions, one figure per day.

```text
    control     12   15   14   10   13        mean 12.8
    treatment   22   19   25   21   23        mean 22.0
```

The treatment is ahead by $9.2$. The question is whether that means anything, and the
first honest observation is that the day-to-day wobble inside each group is not small
either: the control ranges from $10$ to $15$, a spread of $5$, on days where nothing was
changed at all. A difference of $9.2$ against a background that moves by $5$ on its own is
suggestive, not conclusive, and the whole apparatus of this module exists to turn
"suggestive" into a number.

## The noise, computed rather than eyeballed

Start with what varies. The unbiased sample variance of the control is

$$s_a^{2} = \frac{(-0.8)^{2} + 2.2^{2} + 1.2^{2} + (-2.8)^{2} + 0.2^{2}}{4}
= \frac{14.8}{4} = 3.7 ,$$

and the treatment's is $20/4 = 5.0$. But the comparison is not between individual days;
it is between the two *means*, and module 6 established that a mean of $n$ draws has
variance $\sigma^{2}/n$. So the control mean carries variance $3.7/5 = 0.74$ and the
treatment mean carries $5.0/5 = 1.0$.

The quantity under test is the difference of the two means. Module 5 showed
$\mathrm{Var}(A - B) = \mathrm{Var}(A) + \mathrm{Var}(B) - 2\,\mathrm{Cov}(A, B)$, and the
two groups are separate sessions, so the covariance is zero and the **variances add even
though the means subtract**:

$$\mathrm{SE} = \sqrt{\frac{s_a^{2}}{n_a} + \frac{s_b^{2}}{n_b}}
= \sqrt{0.74 + 1.0} = \sqrt{1.74} = 1.3191 .$$

Now the difference has a scale to be measured against, and dividing one by the other is
the entire content of the statistic:

$$t = \frac{\bar{x}_a - \bar{x}_b}{\mathrm{SE}} = \frac{-9.2}{1.3191} = -6.9745 .$$

The observed gap is seven times the size of the noise in it. Nothing has been announced:
$t$ is a signal-to-noise ratio, and it was built out of two facts about variances that
were derived two modules ago.

## Why the null hypothesis is the one you try to reject

The next step needs a distribution for $t$, and here is the reason the logic runs
backwards from the way people want it to. Suppose the two versions are identical. Then the
difference of means is centred on zero with the standard error above, and $t$ has a known
distribution — a $t$ distribution, whose only parameter is the degrees of freedom. Every
number in the previous paragraph becomes checkable.

Now suppose instead that the treatment is better. Better by how much? Two units? Nine?
Nothing is pinned down, so no distribution follows and there is nothing to compute. The
null hypothesis is not privileged because it is more likely or more respectable. It is
privileged because it is the only one of the two that is specific enough to do arithmetic
with, and the test can therefore report evidence *against* it and never evidence for it.

## The degrees of freedom, and why they are rounded down

If both groups had the same variance you could pool them and the degrees of freedom would
be $n_a + n_b - 2 = 8$. Welch's variant drops that assumption, and the price is a
degrees-of-freedom figure that is no longer a whole number:

$$\nu = \frac{\left(\frac{s_a^{2}}{n_a} + \frac{s_b^{2}}{n_b}\right)^{2}}
{\frac{(s_a^{2}/n_a)^{2}}{n_a - 1} + \frac{(s_b^{2}/n_b)^{2}}{n_b - 1}}
= \frac{1.74^{2}}{\frac{0.74^{2}}{4} + \frac{1.0^{2}}{4}}
= \frac{3.0276}{0.3869} = 7.8253 .$$

The printed table has rows for $7$ and for $8$, not for $7.8253$. The lab's `t_critical`
rounds **down**, to $7$, and the reason is visible in the table itself: fewer degrees of
freedom means a fatter-tailed distribution and therefore a *larger* critical value, $2.365$
at $7$ against $2.306$ at $8$. Rounding down demands more evidence before rejecting. It is
the direction in which an error costs you nothing but a missed discovery, whereas rounding
up buys a slightly easier rejection with an approximation nobody has bounded.

One detail worth noticing here: with equal group sizes the Welch statistic and the pooled
statistic are numerically identical — both are $-6.9745$. The whole of Welch's
contribution in this example is the $7.8253$ instead of $8$.

```python
import math

CONTROL = [12, 15, 14, 10, 13]
TREATMENT = [22, 19, 25, 21, 23]


def summarise(xs):
    n = len(xs)
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return n, mean, var


na, ma, va = summarise(CONTROL)
nb, mb, vb = summarise(TREATMENT)
sa, sb = va / na, vb / nb
se = math.sqrt(sa + sb)
t = (ma - mb) / se
df = (sa + sb) ** 2 / (sa ** 2 / (na - 1) + sb ** 2 / (nb - 1))
print(f"control    n={na}  mean={ma:.2f}  var={va:.2f}")
print(f"treatment  n={nb}  mean={mb:.2f}  var={vb:.2f}")
print(f"difference = {ma - mb:.2f}   standard error = {se:.4f}")
print(f"t = {t:.4f}   df = {df:.4f}   critical(df rounded down to 7) = 2.365")
print(f"smallest difference this design could reject: {2.365 * se:.2f}")
```

```text
control    n=5  mean=12.80  var=3.70
treatment  n=5  mean=22.00  var=5.00
difference = -9.20   standard error = 1.3191
t = -6.9745   df = 7.8253   critical(df rounded down to 7) = 2.365
smallest difference this design could reject: 3.12
```

$6.9745$ exceeds $2.365$, so the null is rejected at the $5$ per cent level. The last line
is the one people skip, and it is the most useful number on the page: with five days per
arm and this much noise, no difference below $3.12$ sign-ups per thousand could have been
detected at all. A real improvement of two units would have left this experiment looking
exactly like a failure.

## A second question, and a second statistic

A die is rolled $120$ times. Face counts: $22, 17, 20, 26, 12, 23$. Under a fair die every
face is expected $120/6 = 20$ times, so the residuals are $+2, -3, 0, +6, -8, +3$. Squaring
removes the signs, and the question is what to divide by.

Divide each squared residual by the count it belongs to. A cell with expectation $E$ has
standard deviation close to $\sqrt{E}$, so $(O - E)/\sqrt{E}$ is roughly a $z$-score and
$(O - E)^{2}/E$ is roughly its square. Summing over the six faces gives Pearson's statistic

$$\chi^{2} = \sum_{i} \frac{(O_i - E_i)^{2}}{E_i} .$$

Dividing by $E$ rather than by the observed count is what makes a residual of $6$ on an
expectation of $20$ count for more than the same residual on an expectation of $200$ —
the same absolute miss is far less surprising when more was expected.

```python
DIE_ROLLS = [22, 17, 20, 26, 12, 23]
total = sum(DIE_ROLLS)
expected = total / len(DIE_ROLLS)
terms = [(o - expected) ** 2 / expected for o in DIE_ROLLS]
for face, (o, term) in enumerate(zip(DIE_ROLLS, terms), 1):
    print(f"face {face}: observed {o:>3}  expected {expected:.0f}  "
          f"residual {o - expected:>+5.0f}  term {term:.2f}")
print(f"chi-square = {sum(terms):.2f}   df = {len(DIE_ROLLS) - 1}   critical = 11.070")
```

```text
face 1: observed  22  expected 20  residual    +2  term 0.20
face 2: observed  17  expected 20  residual    -3  term 0.45
face 3: observed  20  expected 20  residual    +0  term 0.00
face 4: observed  26  expected 20  residual    +6  term 1.80
face 5: observed  12  expected 20  residual    -8  term 3.20
face 6: observed  23  expected 20  residual    +3  term 0.45
chi-square = 6.10   df = 5   critical = 11.070
```

Six faces, five degrees of freedom. The reason is the same currency module 8 spent on the
sample mean: the counts are forced to sum to $120$, so any five of the residuals determine
the sixth, and only five of the six terms are free to move. A separate approximation runs
the other way — a multinomial cell's standard deviation is $\sqrt{E(1-p)} = 4.08$ here,
slightly under the $\sqrt{E} = 4.47$ the denominator uses, so each term is scaled down a
little. The exact accounting of how those two effects meet is a matrix calculation; what
survives it is that the sum of $k$ such terms behaves as a $\chi^{2}$ with $k - 1$ degrees
of freedom. At $6.10$ against a critical $11.070$, this die gives no reason for suspicion.

## The mistake, and why it is tempting

"$6.10$ is well under $11.070$, so the die is fair." That sentence is the single most
common error in applied statistics, and the two tests above sit side by side to make it
visible.

The $t$ test rejected. Its report is that a difference this large is hard to explain by
chance. The $\chi^{2}$ test did not reject, and its report is emphatically not that the
die is fair — it is that $120$ rolls were not enough to catch this die out. Nothing in the
calculation ever examined the hypothesis "fair" as a candidate to be supported; the fair
die was assumed, and the data failed to embarrass it. The evidence for that reading is on
the page already: the $t$ test's own power line says a difference under $3.12$ would have
been invisible, and a die biased by a few per cent on one face is exactly that kind of
small effect.

The mistake is tempting because the two outcomes are habitually described as "reject" and
"accept", and "accept the null" sounds like a conclusion rather than a shrug. A companion
error travels with it: reading a $p$-value as the probability that the null is true. It is
the reverse conditional — the probability of data this extreme *given* the null — and
module 2 showed with two machines what happens to people who swap those two.

## Where it stops

**Small expected counts break the $\chi^{2}$ approximation.** Each term is treated as
roughly a squared $z$-score, and that leans on a normal approximation to a count. With
$12$ rolls the expected count per face is $2$, where a count cannot be even approximately
normal — it is bounded below by zero at less than one and a half standard deviations away.
The usual working rule is every expected count at least $5$. The lab's `chi_square` refuses
an expected count that is not strictly positive, which is the extreme of the same problem:
a zero expectation would divide by zero and claim infinite surprise at a category the model
declared impossible.

**Independence is assumed and rarely checked.** The five control days were treated as
independent draws. Five consecutive days on one server usually are not — a slow Monday
affects Tuesday — and positive correlation inflates the true variance of the mean while
leaving the computed standard error alone. The statistic then comes out too large and the
test rejects too often. Where the two samples are *paired* by construction, the fix is not
this test at all: take differences within pairs and run a one-sample test on them, which
turns the correlation from a violated assumption into a cancelled term.

**Every test spends its error budget.** A $5$ per cent level means a $5$ per cent chance of
rejecting a true null. Run the same test on ten metrics and the probability of at least one
spurious rejection is $1 - 0.95^{10} = 0.40$, and module 7's union bound caps it at $0.50$
without needing the ten tests to be independent. The critical value in the table is for one
test, decided on before the data were seen.

**A rejected null is not a large effect.** The standard error shrinks as $1/\sqrt{n}$, so
with enough data any non-zero difference whatever becomes significant. Significance carries
the sign of the evidence; only the estimate carries its size. Here the estimate is $9.2$
sign-ups per thousand with a standard error of $1.32$, and reporting that pair says more
than the word "significant" ever will.

The lab, **A t test and a chi-square test, by hand**, gives you the two critical-value
tables and asks for everything else: `summarise`, `welch_t` returning both the statistic
and the fractional degrees of freedom, `t_critical` with its downward rounding,
`expected_uniform`, `chi_square` with its four refusals, and the two decision functions
that pair a statistic with a verdict. Every number printed above is one your code will
have to reproduce.
''',
                },
            ],
            "quiz": {
                "title": "Signal, noise, and what a verdict does not say",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"Two independent groups of five have sample variances $3.7$ and $5.0$. Why is the standard error of the difference of the means $\sqrt{3.7/5 + 5.0/5}$ rather than $\sqrt{3.7/5 - 5.0/5}$?",
                        "opts": [
                            r"Because a variance under a square root has to be positive, and the subtraction would give an imaginary number for these particular sample values",
                            r"Because variances add for independent variables whether the means are added or subtracted",
                            r"Because the two groups are the same size, which forces the addition",
                            r"Because the difference is taken in the order control minus treatment, and reversing that order would reverse the sign inside the root as well",
                        ],
                        "a": 1,
                        "whys": [
                            r"$\mathrm{Var}(A - B) = \mathrm{Var}(A) + \mathrm{Var}(B) - 2\,\mathrm{Cov}(A, B)$, and the covariance is zero here.",
                            r"The negative sign in the difference is squared away: subtracting $B$ is adding $-B$, and $\mathrm{Var}(-B) = \mathrm{Var}(B)$. Uncertainty accumulates however the quantities are combined.",
                            r"Group sizes affect the $n$ in each $s^{2}/n$ and nothing else. The rule that variances add under independence holds for any sizes at all, and an unbalanced design changes the arithmetic without changing the sign.",
                            r"Reversing the order flips the sign of the difference and of $t$, and leaves the standard error untouched — which is why the decision uses $|t|$. The order of subtraction is a labelling choice, not a modelling one.",
                        ],
                        "why": r"""
$\mathrm{Var}(A - B) = \mathrm{Var}(A) + \mathrm{Var}(B) - 2\,\mathrm{Cov}(A, B)$, and
independent groups have zero covariance, so the two variances add. Subtracting $B$ is the
same as adding $-B$, and negating a variable leaves its variance alone because the
definition squares the deviations. The intuition worth keeping is that uncertainty never
cancels: combining two noisy measurements gives a result noisier than either, whichever
way they are combined. Each mean contributes $s^{2}/n$, giving $0.74 + 1.0 = 1.74$ and a
standard error of $1.3191$.
""",
                    },
                    {
                        "q": r"Welch's formula gives $7.8253$ degrees of freedom, and the printed table has rows only for whole numbers. Why does the lab round down to $7$ rather than to the nearer value $8$?",
                        "opts": [
                            r"Because degrees of freedom count observations, so the fraction must be discarded",
                            r"Because $7$ carries the larger critical value, so rounding down demands more evidence before rejecting",
                            r"Because the Welch-Satterthwaite formula is known to overestimate the degrees of freedom by slightly under one in every case where it is applied",
                            r"Because the table's row for $8$ assumes the two groups have equal variances, which Welch's variant has already abandoned",
                        ],
                        "a": 1,
                        "whys": [
                            r"Welch's $\nu$ is not a count of anything; it is the parameter of the $t$ distribution that best matches the statistic's actual behaviour, and a fractional value is meaningful. Even granting the premise, it would not say which direction is safe.",
                            r"$2.365$ at seven against $2.306$ at eight: the conservative reading is the one that is harder to pass.",
                            r"No such systematic bias exists — $\nu$ lands wherever the two variances and sizes put it, anywhere between the smaller $n - 1$ and $n_a + n_b - 2$. The rounding rule is a choice about which way to err, not a correction for a known error.",
                            r"The table is a table of the $t$ distribution and knows nothing about how its degrees of freedom were obtained. The pooled test would use $8$ here, but the row itself carries no assumption about variances.",
                        ],
                        "why": r"""
Fewer degrees of freedom means a fatter-tailed $t$ distribution and therefore a larger
critical value: $2.365$ at $7$ against $2.306$ at $8$. Rounding down asks for more evidence
before the null is rejected, so an error made by rounding costs a missed discovery rather
than a false one. Rounding up would buy a marginally easier rejection on the strength of
an approximation whose error nobody has bounded, and false rejections are the failure this
whole procedure is built to control. Note also that with equal group sizes the Welch and
pooled statistics coincide exactly at $-6.9745$; the degrees of freedom are the only thing
Welch changes in this example.
""",
                    },
                    {
                        "q": r"A die rolled $120$ times gives $\chi^{2} = 6.10$ against a critical value of $11.070$ at five degrees of freedom. What has been established?",
                        "opts": [
                            r"That the die is fair, since the statistic falls comfortably inside the region a fair die produces",
                            r"That the probability the die is fair is at least $95$ per cent, which is the confidence level the table was drawn at",
                            r"That $120$ rolls were not enough to catch this die out, which is a statement about the experiment",
                            r"That the six face counts are close enough to equal for the differences between them to be exactly zero",
                        ],
                        "a": 2,
                        "whys": [
                            r"Fairness was assumed in order to compute the expected counts, and an assumption that survives a weak test has not been demonstrated. A die biased by a few per cent would pass this test nearly every time.",
                            r"This reverses the conditional. The $5$ per cent belongs to the probability of data this extreme *given* a fair die, not to the probability of a fair die given the data — and the latter would need a prior, which no table supplies.",
                            r"The residuals reach $-8$ on a face, and the test still cannot separate that from ordinary variation.",
                            r"The counts plainly are not equal — $12$ against $26$ is a spread of $14$ — and the test never claimed they were. What it says is that a spread that size is unremarkable in $120$ rolls, which is a different sentence.",
                        ],
                        "why": r"""
Failing to reject is a statement about the power of the experiment, not about the truth of
the hypothesis. The fair die was assumed, in order to produce the expected count of $20$
per face, and the data then failed to embarrass that assumption — which a die biased by a
few per cent would also fail to do at this sample size. The evidence for that reading sits
in the companion $t$ test, whose own arithmetic says no difference below $3.12$ units could
have been detected at all. "Reject" and "accept" is a misleading pair of words: the second
outcome is a shrug, not a conclusion.
""",
                    },
                    {
                        "q": r"Six face counts are compared against six expected counts, and the statistic is read against $5$ degrees of freedom. Where did the sixth go?",
                        "opts": [
                            r"The six counts must sum to the total, so any five of the residuals fix the sixth",
                            r"One degree of freedom is reserved for estimating the expected counts, which were computed from the data rather than being known in advance of the experiment",
                            r"The face with a residual of exactly zero contributes nothing to the sum",
                            r"Chi-square tables are indexed by the number of comparisons rather than the number of categories, and there are five comparisons among six faces",
                        ],
                        "a": 0,
                        "whys": [
                            r"The residuals $+2, -3, 0, +6, -8, +3$ add to zero, and they must: both the observed and the expected counts total $120$.",
                            r"Tempting, and it is the right rule in a different situation — fitting a parameter from the data does cost a further degree of freedom. Here the expectation of $20$ per face comes from the fairness hypothesis itself, so nothing was fitted.",
                            r"A zero residual is an ordinary outcome, not a structural constraint, and reading it as one would make the degrees of freedom depend on the data. Roll again with no exact hit and the test is still run at five.",
                            r"There is no such indexing convention. The degrees of freedom come from the geometry of the constraint on the residuals, not from a count of pairwise comparisons, which would in any case give fifteen.",
                        ],
                        "why": r"""
Both the observed and the expected counts total $120$, so the six residuals must sum to
zero: $+2, -3, 0, +6, -8, +3$. Any five of them determine the sixth, and only five can move
independently. That is the same accounting module 8 applied to the sample variance, where
fitting the mean from the data cost one degree of freedom for the same structural reason.
The general rule is $k - 1$ for a goodness-of-fit test with no fitted parameters, and each
parameter estimated from the data afterwards costs one more.
""",
                    },
                    {
                        "q": r"The same $5$ per cent test is applied to ten different metrics from one experiment. What is the chance of at least one rejection if every null is true?",
                        "opts": [
                            r"$5$ per cent, since a test's level does not depend on repetition",
                            r"About $40$ per cent, since $1 - 0.95^{10} = 0.401$ for ten independent tests",
                            r"$50$ per cent exactly, because ten tests at five per cent each contribute five per cent of error apiece",
                            r"It cannot be stated without knowing how strongly the ten metrics are correlated with one another",
                        ],
                        "a": 1,
                        "whys": [
                            r"The level governs one test decided on in advance. Running ten and reporting whichever rejected is a different procedure with a different error rate, and this is the reasoning behind a great many irreproducible findings.",
                            r"Ten independent chances to miss, each with probability $0.95$.",
                            r"$50$ per cent is the union bound — a genuine upper limit that needs no independence — but it is a ceiling, not the value. Error probabilities do not add exactly; the overlap between two rejections is counted twice when they do.",
                            r"Correlation does change the exact figure, and the caution is a fair instinct. But independence is the stated case here, and even without it module 7's union bound pins the answer below $0.50$.",
                        ],
                        "why": r"""
Each true null survives with probability $0.95$, and ten independent survivals have
probability $0.95^{10} = 0.599$, so something rejects about $40$ per cent of the time. The
union bound from module 7 caps it at $10 \times 0.05 = 0.50$ without assuming anything
about independence, and the gap between $0.401$ and $0.50$ is the overlap the bound
double-counts. The practical consequence is that a critical value is for one test chosen
before the data were seen; searching ten metrics for the one that rejected converts a
$5$ per cent procedure into a $40$ per cent one.
""",
                    },
                    {
                        "q": r"A very large experiment reports a difference of $0.02$ sign-ups per thousand with $p < 0.001$. What follows?",
                        "opts": [
                            r"The effect is large, because a $p$-value that small can only arise from a substantial underlying difference between the two groups",
                            r"The result is evidence that the difference is not zero, and its size is $0.02$ — which may be too small to act on",
                            r"The test has been run incorrectly, since a difference that small cannot be significant",
                            r"The probability that the two versions differ is greater than $99.9$ per cent, since the $p$-value measures exactly that",
                        ],
                        "a": 1,
                        "whys": [
                            r"Significance is the difference divided by a standard error that shrinks as $1/\sqrt{n}$, so a large enough sample makes any non-zero difference significant. The $p$-value carries no information about magnitude on its own.",
                            r"The test supplies the sign of the evidence; the estimate supplies the size, and $0.02$ is the size.",
                            r"It can, and routinely does. Nothing is wrong with the arithmetic — a tiny difference measured precisely enough is exactly what a very large experiment is built to detect, which is why effect sizes are reported beside verdicts.",
                            r"Another reversed conditional: $p$ is the probability of data this extreme assuming no difference, not the probability of a difference given the data. The two are the pair module 2 separated with a machine that made $30$ per cent of the parts and $51.7$ per cent of the defects.",
                        ],
                        "why": r"""
The statistic is a difference divided by a standard error, and the standard error falls as
$1/\sqrt{n}$, so a sufficiently large experiment will find significance in any difference
that is not exactly zero. What the test reports is that the difference is unlikely to be
zero; what it never reports is whether the difference matters. Only the estimate carries
magnitude, and $0.02$ sign-ups per thousand is a number a product decision can be taken
against. Reporting the estimate and its standard error together says everything the verdict
says and more, which is why the lab's decision functions return the statistic and the
critical value rather than a bare boolean.
""",
                    },
                ],
            },
            "lab": {
                "title": "A t test and a chi-square test, by hand",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
The two critical-value tables are given to you at the top of `main.py`, both at
the 5% level. Write everything else.

**`summarise(xs)`** — `(n, mean, variance)` with the unbiased variance.
`ValueError` for fewer than two observations.

**`welch_t(a, b)`** — returns `(t, df)` where

```text
t  = (mean_a - mean_b) / sqrt(var_a/n_a + var_b/n_b)
df = (var_a/n_a + var_b/n_b)^2
     / ( (var_a/n_a)^2/(n_a-1) + (var_b/n_b)^2/(n_b-1) )
```

**`t_critical(df)`** — the two-sided 5% critical value. Real degrees of freedom
are fractional, and the table is not; round **down** to the largest tabulated
entry that does not exceed `df`. That is the conservative reading. `ValueError`
for `df < 1`.

**`t_decision(a, b)`** — `{"t", "df", "critical", "reject"}`, rejecting when
`abs(t)` exceeds the critical value.

**`expected_uniform(total, k)`** — `k` equal expected counts summing to `total`.

**`chi_square(observed, expected)`** — the statistic. `ValueError` when the two
lists differ in length, hold fewer than two categories, contain a negative
observation, or contain an expected count that is not strictly positive.

**`chi_square_decision(observed, expected)`** — `{"statistic", "df", "critical",
"reject"}` with `df = k - 1`; `ValueError` when that df is not in the table.

The die in `main.py` was rolled 120 times. Its statistic is 6.1 against a
critical value of 11.070, so the data give no reason to call it loaded.
''',
                "files": [{"name": "main.py", "content": r'''
import math

# two-sided critical values of Student's t at alpha = 0.05
T_CRITICAL_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 24: 2.064,
    30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980, 1000: 1.962,
}

# upper-tail critical values of chi-square at alpha = 0.05
CHI2_CRITICAL_95 = {
    1: 3.841, 2: 5.991, 3: 7.815, 4: 9.488, 5: 11.070, 6: 12.592, 7: 14.067,
    8: 15.507, 9: 16.919, 10: 18.307, 11: 19.675, 12: 21.026, 15: 24.996,
    20: 31.410,
}

CONTROL = [12, 15, 14, 10, 13]
TREATMENT = [22, 19, 25, 21, 23]
DIE_ROLLS = [22, 17, 20, 26, 12, 23]


def summarise(xs):
    """(n, mean, unbiased variance). ValueError for fewer than two values."""
    # your code here


def welch_t(a, b):
    """(t, df) for the Welch two-sample t statistic."""
    # your code here


def t_critical(df):
    """Two-sided 5% critical value, rounding df down to the table."""
    # your code here


def t_decision(a, b):
    """{t, df, critical, reject}."""
    # your code here


def expected_uniform(total, k):
    """k equal expected counts summing to total."""
    # your code here


def chi_square(observed, expected):
    """Sum of (O - E)^2 / E."""
    # your code here


def chi_square_decision(observed, expected):
    """{statistic, df, critical, reject}."""
    # your code here


print(t_decision(CONTROL, TREATMENT))
print(chi_square_decision(DIE_ROLLS, expected_uniform(sum(DIE_ROLLS), 6)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

# two-sided critical values of Student's t at alpha = 0.05
T_CRITICAL_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 24: 2.064,
    30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980, 1000: 1.962,
}

# upper-tail critical values of chi-square at alpha = 0.05
CHI2_CRITICAL_95 = {
    1: 3.841, 2: 5.991, 3: 7.815, 4: 9.488, 5: 11.070, 6: 12.592, 7: 14.067,
    8: 15.507, 9: 16.919, 10: 18.307, 11: 19.675, 12: 21.026, 15: 24.996,
    20: 31.410,
}

CONTROL = [12, 15, 14, 10, 13]
TREATMENT = [22, 19, 25, 21, 23]
DIE_ROLLS = [22, 17, 20, 26, 12, 23]


def summarise(xs):
    """(n, mean, unbiased variance). ValueError for fewer than two values."""
    n = len(xs)
    if n < 2:
        raise ValueError("need at least two observations")
    mean = sum(xs) / n
    variance = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return n, mean, variance


def welch_t(a, b):
    """(t, df) for the Welch two-sample t statistic."""
    na, ma, va = summarise(a)
    nb, mb, vb = summarise(b)
    sa, sb = va / na, vb / nb            # the two squared standard errors
    se = math.sqrt(sa + sb)
    if se == 0:
        raise ValueError("both samples are constant, so the statistic is undefined")
    t = (ma - mb) / se
    df = (sa + sb) ** 2 / (sa ** 2 / (na - 1) + sb ** 2 / (nb - 1))
    return t, df


def t_critical(df):
    """Two-sided 5% critical value, rounding df down to the table."""
    if df < 1:
        raise ValueError("degrees of freedom must be at least 1")
    usable = [k for k in T_CRITICAL_95 if k <= df]
    return T_CRITICAL_95[max(usable)]    # rounding down is the safe direction


def t_decision(a, b):
    """{t, df, critical, reject}."""
    t, df = welch_t(a, b)
    critical = t_critical(df)
    return {"t": t, "df": df, "critical": critical, "reject": abs(t) > critical}


def expected_uniform(total, k):
    """k equal expected counts summing to total."""
    if k < 1:
        raise ValueError("need at least one category")
    return [total / k] * k


def chi_square(observed, expected):
    """Sum of (O - E)^2 / E."""
    if len(observed) != len(expected):
        raise ValueError("observed and expected must have the same length")
    if len(observed) < 2:
        raise ValueError("goodness of fit needs at least two categories")
    if any(o < 0 for o in observed):
        raise ValueError("counts cannot be negative")
    if any(e <= 0 for e in expected):
        raise ValueError("every expected count must be strictly positive")
    return sum((o - e) ** 2 / e for o, e in zip(observed, expected))


def chi_square_decision(observed, expected):
    """{statistic, df, critical, reject}."""
    statistic = chi_square(observed, expected)
    df = len(observed) - 1
    if df not in CHI2_CRITICAL_95:
        raise ValueError(f"no tabulated critical value for df = {df}")
    critical = CHI2_CRITICAL_95[df]
    return {"statistic": statistic, "df": df, "critical": critical,
            "reject": statistic > critical}


print(t_decision(CONTROL, TREATMENT))
print(chi_square_decision(DIE_ROLLS, expected_uniform(sum(DIE_ROLLS), 6)))
'''}],
                "hints": [
                    "Name the two squared standard errors `va/na` and `vb/nb` once; both the statistic and the Welch-Satterthwaite denominator reuse them.",
                    "`max(k for k in T_CRITICAL_95 if k <= df)` is the whole of the conservative table lookup.",
                    "Validate `chi_square` before summing: a zero expected count would divide by zero, and the error message is far more useful than the traceback.",
                    "`df` for goodness of fit is the number of categories minus one — no parameters were estimated from the data here.",
                ],
                "tests": [
                    {"name": "summarise reports n, mean and unbiased variance", "code": r'''
assert summarise(CONTROL) == (5, 12.8, 3.7), f"Got {summarise(CONTROL)!r}, expected (5, 12.8, 3.7)"
_n, _m, _v = summarise(TREATMENT)
assert (_n, _m) == (5, 22.0) and abs(_v - 5.0) < 1e-12, f"Got {(_n, _m, _v)!r}"
for _bad in ([], [3]):
    try:
        summarise(_bad)
        assert False, f"summarise({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The Welch statistic and its degrees of freedom", "code": r'''
_t, _df = welch_t(CONTROL, TREATMENT)
assert abs(_t - (-6.974502000925911)) < 1e-9, f"t is {_t!r}, expected about -6.9745"
assert abs(_df - 7.825277849573533) < 1e-9, f"df is {_df!r}, expected about 7.8253"
_t2, _df2 = welch_t(TREATMENT, CONTROL)
assert abs(_t2 + _t) < 1e-12, "Swapping the samples flips the sign of t"
assert abs(_df2 - _df) < 1e-12, "The degrees of freedom are symmetric in the two samples"
'''},
                    {"name": "The table is read conservatively", "code": r'''
assert t_critical(7.825277849573533) == 2.365, \
    f"df 7.83 must round down to the df 7 row, got {t_critical(7.825277849573533)!r}"
assert t_critical(1) == 12.706 and t_critical(60) == 2.000
assert t_critical(11.9) == 2.228, "There is no df 11 row, so df 10 is used"
assert t_critical(500) == 1.980, "df 500 falls back to the df 120 row"
for _bad in (0, 0.5, -3):
    try:
        t_critical(_bad)
        assert False, f"t_critical({_bad}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The t test separates and refuses to over-claim", "code": r'''
_d = t_decision(CONTROL, TREATMENT)
assert _d["reject"] is True, f"These groups differ by nine points; got {_d!r}"
assert _d["critical"] == 2.365 and abs(_d["t"] + 6.9745) < 1e-3, f"Got {_d!r}"
_similar = t_decision(CONTROL, [13, 14, 12, 15, 11])
assert _similar["reject"] is False, \
    f"Two overlapping samples must not be declared different; got {_similar!r}"
assert abs(_similar["t"]) < _similar["critical"], "reject must agree with the comparison"
'''},
                    {"name": "The chi-square statistic", "code": r'''
assert expected_uniform(120, 6) == [20.0] * 6, f"Got {expected_uniform(120, 6)!r}"
_stat = chi_square(DIE_ROLLS, expected_uniform(120, 6))
assert abs(_stat - 6.1) < 1e-9, f"The statistic is {_stat!r}, expected 6.1"
assert chi_square([20, 20, 20], [20, 20, 20]) == 0.0, "A perfect fit scores zero"
assert abs(chi_square([40, 10, 20, 20, 20, 10], expected_uniform(120, 6)) - 30.0) < 1e-9, \
    "A badly skewed table should score 30.0"
'''},
                    {"name": "chi_square validates its inputs", "code": r'''
for _obs, _exp in [([1, 2], [1]), ([5], [5]), ([1, -2], [2, 2]), ([1, 2], [0, 3]),
                   ([1, 2], [2, -1])]:
    try:
        chi_square(_obs, _exp)
        assert False, f"chi_square({_obs!r}, {_exp!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The goodness-of-fit decision", "code": r'''
_fair = chi_square_decision(DIE_ROLLS, expected_uniform(120, 6))
assert _fair["df"] == 5 and _fair["critical"] == 11.070, f"Got {_fair!r}"
assert _fair["reject"] is False, "6.1 is well under 11.070, so the die survives the test"
_loaded = chi_square_decision([40, 10, 20, 20, 20, 10], expected_uniform(120, 6))
assert _loaded["reject"] is True, f"A statistic of 30 must reject; got {_loaded!r}"
try:
    chi_square_decision([1] * 14, [1] * 14)
    assert False, "df 13 is not in the table, so this should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M10
        {
            "title": "Bayesian reasoning and naive Bayes",
            "summary": "Turning a prior and a likelihood into a posterior, then scaling that up to a classifier.",
            "concepts": [
                "Bayes' rule as prior times likelihood, renormalised over the hypotheses",
                "The base-rate fallacy: a 99% accurate test on a rare condition still yields mostly false positives",
                "Sequential updating — yesterday's posterior is today's prior, and the order does not matter",
                "The naive conditional-independence assumption, and why it works despite being false",
                "Working in log space so a hundred-word document does not underflow to zero",
                "Laplace (add-alpha) smoothing: an unseen word must not annihilate a whole class",
                "The MAP decision rule, and how the prior shows up as a constant additive term",
            ],
            "read": [
                {
                    "title": 'A positive result, and the ninety-nine thousand people it did not come from',
                    "minutes": 15,
                    "body": r'''
Screen a hundred thousand people for a condition that one in a thousand of them has. The
test catches $99$ per cent of real cases and returns a false positive $5$ per cent of the
time. Count the people rather than reaching for anything.

```text
    100 have the condition        ->   99 test positive,      1 negative
 99,900 do not have it            -> 4,995 test positive, 94,905 negative
                                     ------
    people holding a positive result: 5,094
```

Of the $5{,}094$ people looking at a positive result, $99$ have the condition. That is
$99/5094 = 0.0194$, under $2$ per cent. The test is right $99$ per cent of the time and a
positive result still means, on the balance of probability, that you are fine.

Nothing in that table is a formula. The whole of Bayesian reasoning is in it, and the rest
of this unit is bookkeeping for cases where you cannot write out a hundred thousand people.

## The rule, and the normaliser you can skip

Module 2 turned a conditional round once already, with two machines and a defective part.
Give it a name and a shape. From the definition of conditional probability applied twice,

$$P(H | E) = \frac{P(E | H)\,P(H)}{P(E)} ,$$

where $H$ is a hypothesis and $E$ the evidence. Every number in the table above appears
here: $P(H) = 0.001$ is the prior — the row totals on the left; $P(E | H) = 0.99$ is the
likelihood — how each row splits; and $P(E) = 0.05094$ is the column total on the right.

The useful observation for code is that $P(E)$ does not depend on $H$. Compute the
numerator $P(E | H)P(H)$ for every hypothesis, then divide each by their sum. The
denominator never has to be derived separately, because it *is* that sum:

$$P(E) = \sum_{h} P(E | h)\,P(h) .$$

That is why the lab's `bayes_posterior` takes a prior dict and a likelihood dict, multiplies
them entry by entry, and renormalises. The law of total probability is a summation, not a
separate theorem to look up.

## Yesterday's posterior is today's prior

Nothing distinguishes a prior from any other probability distribution over the hypotheses,
so the output of one update is a legitimate input to the next.

```python
def posterior(prior, likelihood):
    joint = {h: prior[h] * likelihood[h] for h in prior}
    evidence = sum(joint.values())
    if evidence == 0.0:
        raise ValueError("the observation is impossible under every hypothesis")
    return {h: value / evidence for h, value in joint.items()}


prior = {"ill": 0.001, "well": 0.999}
positive = {"ill": 0.99, "well": 0.05}
negative = {"ill": 0.01, "well": 0.95}

p = prior
for step in (1, 2, 3):
    p = posterior(p, positive)
    print(f"after {step} positive test(s): P(ill) = {p['ill']:.6f}")

a = posterior(posterior(prior, positive), negative)
b = posterior(posterior(prior, negative), positive)
print(f"positive then negative: P(ill) = {a['ill']:.10f}")
print(f"negative then positive: P(ill) = {b['ill']:.10f}")
```

```text
after 1 positive test(s): P(ill) = 0.019435
after 2 positive test(s): P(ill) = 0.281832
after 3 positive test(s): P(ill) = 0.885977
positive then negative: P(ill) = 0.0002085862
negative then positive: P(ill) = 0.0002085862
```

One positive result moves the belief from $0.001$ to $0.019$, a nineteenfold jump that
still leaves the answer "probably not". A second takes it to $0.28$ and a third to $0.89$.
The evidence never stopped being strong; it began against a prior strong enough to absorb
it.

The last two lines say the order does not matter, and that is not a coincidence to be
memorised. Both routes end at the same place because the numerators multiply,
$P(H)\,P(E_1 | H)\,P(E_2 | H)$, and multiplication is commutative; the renormalisation
happens once at the end either way. The lab's `sequential_update` folds a list of
likelihood dicts left to right, and its result is independent of how the list was sorted.

## Scaling it up: many pieces of evidence at once

A document is not one observation, it is a few hundred. Write $w_1, \dots, w_m$ for its
words and $c$ for a class. The exact posterior wants $P(w_1, \dots, w_m | c)$, a joint
distribution over every word combination the language admits, which no corpus could ever
estimate. The **naive** assumption is that, given the class, the words are conditionally
independent:

$$P(w_1, \dots, w_m | c) \approx \prod_{i=1}^{m} P(w_i | c) .$$

This is false. "New" and "York" are not independent in any corpus. What rescues it is that
a classifier is asked for an $\arg\max$ and not for a probability: the products can be
wrong by orders of magnitude and still be wrong in the same direction for every class,
leaving the ranking intact. The lab's `classify` returns a label; its `log_prob` returns a
score. Only the first is trustworthy.

## Where the zero comes from, and how to remove it

Train on the lab's four-document corpus. Spam contributes `buy cheap pills` and
`cheap deal now`; ham contributes `meet me for lunch` and `lunch tomorrow`. Six tokens per
class, a shared vocabulary of ten words.

Now score the message `cheap lunch deal`. The word `lunch` never appeared in a spam
document, so its raw estimate $P(\text{lunch} | \text{spam}) = 0/6$ is exactly zero, and a
zero in a product is not evidence — it is a veto. One innocuous word would rule out spam
however many pill advertisements surrounded it.

The fix follows from asking what the zero means. It does not mean the word is impossible
in spam; it means six tokens were not enough to see it. Pretend each word in the
vocabulary was seen $\alpha$ extra times in each class:

$$P(w | c) = \frac{\mathrm{count}(w, c) + \alpha}{\mathrm{total}(c) + \alpha |V|} .$$

The denominator is forced rather than chosen: adding $\alpha$ to each of the $|V|$
vocabulary entries adds $\alpha|V|$ to the total, and only that denominator keeps the
smoothed probabilities summing to one over the vocabulary. With $\alpha = 1$ and
$|V| = 10$ every denominator here is $6 + 10 = 16$.

By hand, for `cheap lunch deal`, with `cheap` seen twice in spam, `deal` once and `lunch`
never:

$$P(\text{spam})\prod P(w | \text{spam})
= \frac{1}{2} \cdot \frac{3}{16} \cdot \frac{1}{16} \cdot \frac{2}{16}
= \frac{3}{4096} = 0.000732 ,$$

$$P(\text{ham})\prod P(w | \text{ham})
= \frac{1}{2} \cdot \frac{1}{16} \cdot \frac{3}{16} \cdot \frac{1}{16}
= \frac{3}{8192} = 0.000366 .$$

Spam wins by exactly two to one, so renormalising gives $P(\text{spam} | \text{message})
= 2/3$. Note how small both numbers already are on a three-word message.

## Logs, because the product does not survive

```python
import math

q = 0.001
print(f"a product of 200 factors of {q}: {q ** 200!r}")
print(f"the same quantity in logs:      {200 * math.log(q):.4f}")
```

```text
a product of 200 factors of 0.001: 0.0
the same quantity in logs:      -1381.5511
```

A double-precision float bottoms out near $10^{-308}$, and a two-hundred-word document
drives the product to $10^{-600}$. Both classes underflow to exactly `0.0`, and comparing
two zeros decides nothing — the classifier does not crash, it silently returns whichever
label the tie rule happens to name. Taking logarithms turns the product into a sum,
$\log P(c) + \sum_i \log P(w_i | c)$, and $-1381.55$ is a number a computer is perfectly
comfortable with. Since $\log$ is increasing, the label with the largest log score is the
label with the largest probability, which is all the $\arg\max$ needs. The prior enters as
a single additive constant, which is what the concepts list means by the MAP rule.

```python
import math
import re

CORPUS = [
    ("buy cheap pills", "spam"),
    ("cheap deal now", "spam"),
    ("meet me for lunch", "ham"),
    ("lunch tomorrow", "ham"),
]
ALPHA = 1.0


def tokenise(text):
    return re.findall(r"[a-z0-9]+", text.lower())


counts, totals, docs, vocab = {}, {}, {}, set()
for text, label in CORPUS:
    counts.setdefault(label, {})
    totals.setdefault(label, 0)
    docs[label] = docs.get(label, 0) + 1
    for word in tokenise(text):
        counts[label][word] = counts[label].get(word, 0) + 1
        totals[label] += 1
        vocab.add(word)


def log_prob(text, label):
    total = math.log(docs[label] / len(CORPUS))
    for word in tokenise(text):
        total += math.log((counts[label].get(word, 0) + ALPHA)
                          / (totals[label] + ALPHA * len(vocab)))
    return total


print(f"vocabulary {len(vocab)} words, {totals['spam']} spam tokens, "
      f"{totals['ham']} ham tokens")
for message in ("cheap lunch deal", "buy pills now", "cheap lunch"):
    spam, ham = log_prob(message, "spam"), log_prob(message, "ham")
    verdict = "spam" if spam > ham else ("ham" if ham > spam else "tie -> ham")
    print(f"{message:<18} spam {spam:.4f}   ham {ham:.4f}   {verdict}")
```

```text
vocabulary 10 words, 6 spam tokens, 6 ham tokens
cheap lunch deal   spam -7.2192   ham -7.9123   spam
buy pills now      spam -6.9315   ham -9.0109   spam
cheap lunch        spam -5.1397   ham -5.1397   tie -> ham
```

$e^{-7.2192} = 0.000732$, the number computed by hand above. And `cheap lunch` is an exact
tie: one word each way, with symmetric counts, so the two scores agree to every digit. The
lab requires ties to go to the alphabetically first label precisely so that this case, and
the all-unseen document, have a defined answer rather than one that depends on dictionary
ordering.

## The mistake, and why it is tempting

"The test is $99$ per cent accurate and mine came back positive, so I am $99$ per cent
likely to have it." The number $0.99$ is $P(\text{positive} | \text{ill})$. The number
wanted is $P(\text{ill} | \text{positive})$, and it is $0.0194$ — a factor of fifty out.

It is tempting because the two read as the same English sentence with the words shuffled,
and because the prior is invisible. Nothing in the phrase "$99$ per cent accurate"
mentions the $99{,}900$ healthy people, and they are where the $4{,}995$ false positives
come from: a small error rate on a huge group swamps a large success rate on a tiny one.
The defence is the table at the top of this unit. Count people, in whatever units make the
rare group a whole number, before dividing anything.

## Where it stops

**A prior of zero can never be updated.** If $P(H) = 0$ then $P(E | H)P(H) = 0$ for every
possible $E$, and the posterior stays at zero for ever. Excluding a hypothesis outright is
a permanent decision, not a strong opinion, which is why a filter should not be trained to
believe a word is impossible in a class — the same reason smoothing exists.

**Evidence impossible under every hypothesis breaks the arithmetic.** If every numerator is
zero the normaliser is zero too, and the update is $0/0$. That is not a number to be
patched with a default; it means the observation falsifies the model itself, so the lab
raises `ValueError` rather than returning something plausible.

**Naive Bayes probabilities are not calibrated.** The independence assumption double-counts
correlated evidence, so a document containing `cheap` five times has its spam score driven
five times further than the words jointly justify. The scores pile up near $0$ and $1$, and
using one as a confidence — thresholding at "$99$ per cent sure" — is reading a number the
model cannot supply. The ranking survives; the magnitude does not.

**Smoothing is a choice with consequences.** $\alpha$ trades a veto for a bias: large
$\alpha$ pulls every estimate towards uniform and blunts genuine evidence, small $\alpha$
lets one rare word dominate a document. With six tokens against a vocabulary of ten,
$\alpha = 1$ is contributing more mass than the data — visible in the fact that a word seen
twice gets $3/16$ while a word never seen gets $1/16$, a ratio of three rather than the
infinite one the raw counts asserted.

The lab, **Posterior updates and a spam filter**, builds both halves: `bayes_posterior` and
`sequential_update` for the screening example, then a `NaiveBayes` class with add-alpha
smoothing, `log_prob` in logs throughout, and `classify` with the alphabetical tie rule.
The numbers printed above — $0.019435$, $-7.2192$, and the tie on `cheap lunch` — are the
ones your implementation has to reproduce.
''',
                },
            ],
            "quiz": {
                "title": "Priors, products and the conditional that gets reversed",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"A condition affects $1$ in $1000$. A test catches $99$ per cent of cases and gives a false positive $5$ per cent of the time. A result comes back positive. What is the probability the condition is present?",
                        "opts": [
                            r"About $99$ per cent, which is the accuracy the test is advertised as having",
                            r"About $95$ per cent, since the false positive rate of $5$ per cent is what has to be subtracted",
                            r"About $2$ per cent, because $99$ true positives are outnumbered by $4995$ false ones",
                            r"It cannot be computed without also knowing how many people were screened in total",
                        ],
                        "a": 2,
                        "whys": [
                            r"$99$ per cent is $P(\text{positive} \mid \text{ill})$, which is how the test behaves on people who are ill. The question asks the reverse conditional, and the two differ here by a factor of fifty.",
                            r"Subtracting an error rate from one hundred treats the two groups as though they were the same size. The $5$ per cent applies to $99{,}900$ people and the $99$ per cent to $100$, and no subtraction can repair that mismatch.",
                            r"$99/(99 + 4995) = 0.0194$, and the rare group is the small one on both counts.",
                            r"The total cancels: doubling the population doubles both the true and the false positives, leaving the ratio alone. Any convenient total works, and one hundred thousand is chosen only to make the rare group a whole number.",
                        ],
                        "why": r"""
Out of $100{,}000$ people, $100$ have the condition and $99$ of them test positive, while
$99{,}900$ do not and $4{,}995$ of those test positive anyway. So $5{,}094$ people hold a
positive result and $99$ of them are ill: $99/5094 = 0.0194$. The advertised $99$ per cent
is $P(\text{positive} \mid \text{ill})$ and the answer wanted is
$P(\text{ill} \mid \text{positive})$ — the reversal module 2 met with two machines. The
prior does the damage: a small error rate applied to a very large group produces far more
positives than a high catch rate applied to a tiny one.
""",
                    },
                    {
                        "q": r"Starting from a prior of $0.001$, one positive test gives a posterior of $0.0194$ and a second gives $0.2818$. Why does the second test move the belief so much further than the first?",
                        "opts": [
                            r"Because the second test acts on a prior nineteen times larger, so the same likelihood ratio starts nearer even odds",
                            r"Because repeating a test increases its accuracy, so the second result is stronger evidence than the first",
                            r"Because the posterior after two tests is computed from the joint likelihood, which is not the same as updating twice",
                            r"Because the second update multiplies the first posterior by the likelihood ratio a second time, and repeated multiplication compounds",
                        ],
                        "a": 0,
                        "whys": [
                            r"Each positive multiplies the odds by $0.99/0.05 \approx 19.8$; odds of $1{:}999$ have far less room to move in probability than odds of $1{:}50$.",
                            r"The test's characteristics are fixed properties of the test — $0.99$ and $0.05$ on every use — and nothing about a repeat changes them. What changed is the belief the second result acts on, not the result itself.",
                            r"Updating twice and using the joint likelihood give the identical answer, which is exactly why sequential updating is legitimate: the numerators multiply and the single renormalisation at the end is the same either way.",
                            r"The multiplication is real, but by itself it would predict a jump of the same *factor* each time, and the factor is indeed about $19.8$ in odds both times. What differs is how a fixed odds factor translates into probability at different starting points.",
                        ],
                        "why": r"""
Work in odds. A positive result multiplies the odds on the condition by
$0.99/0.05 \approx 19.8$ every time it is seen. Starting odds are $1{:}999$, which become
about $1{:}50$ — a probability of $0.0194$. Applying the same factor again gives about
$2{:}5$, a probability of $0.28$. The multiplicative step is identical; what changes is
that probability compresses everything near zero and near one, so a fixed odds ratio buys
far more probability once the odds are near even. The evidence was never weak — it was
starting from a prior strong enough to absorb it.
""",
                    },
                    {
                        "q": r"In a naive Bayes filter, a word that never appeared in the spam training documents gets a raw estimate of $0/6$. What does that zero do, and why is add-alpha smoothing the answer?",
                        "opts": [
                            r"It makes the spam score negative, and smoothing restores it to a positive value so that the comparison against ham can proceed",
                            r"It vetoes the class entirely whatever the other words say, and smoothing replaces the claim of impossibility with a small count",
                            r"It leaves the product unchanged, since a factor of zero is neutral, and smoothing exists only to speed up the arithmetic on sparse vocabularies",
                            r"It biases the estimate towards ham, and smoothing corrects the bias by adding the same constant to both classes",
                        ],
                        "a": 1,
                        "whys": [
                            r"Probabilities are never negative; the zero makes the product zero, not negative. The log of that product is $-\infty$, which is a different failure, and one that no amount of restoring sign would fix.",
                            r"Zero times anything is zero, so one innocuous word outvotes every pill advertisement in the message.",
                            r"A factor of zero is the opposite of neutral — the neutral factor under multiplication is one. Smoothing is about what the model asserts, not about how fast it computes, and the arithmetic is the same speed either way.",
                            r"Symmetry is the tempting part, and it is true that $\alpha$ is added in both classes. But the defect is not a lopsided estimate to be balanced out; it is a single zero that annihilates a whole product regardless of what the other class does.",
                        ],
                        "why": r"""
A zero factor annihilates the entire product, so the class is ruled out no matter what the
remaining words say — one ordinary word can veto a message full of pill advertisements.
The zero is also a claim the data do not support: six training tokens are not evidence that
a word is impossible in spam, only that it was not seen. Add-alpha replaces the assertion
of impossibility with a small count,
$(\mathrm{count} + \alpha)/(\mathrm{total} + \alpha|V|)$, and the denominator is forced
rather than chosen — adding $\alpha$ to each of $|V|$ entries adds $\alpha|V|$ to the
total, which is what keeps the smoothed masses summing to one.
""",
                    },
                    {
                        "q": r"Why does the classifier accumulate $\log P(c) + \sum_i \log P(w_i \mid c)$ rather than multiplying the probabilities directly?",
                        "opts": [
                            r"Because a product of hundreds of small probabilities underflows to exactly $0.0$, and comparing two zeros decides nothing",
                            r"Because logarithms convert the naive independence assumption into an exact one, which removes the approximation from the model",
                            r"Because the sum and the product rank the classes differently, and the sum is the ranking that matches the true posterior",
                            r"Because probabilities cannot be multiplied unless the events are independent, whereas their logarithms may always be added together safely",
                        ],
                        "a": 0,
                        "whys": [
                            r"$0.001^{200}$ is $10^{-600}$, and a double bottoms out near $10^{-308}$: both classes reach `0.0` and the tie rule decides the answer.",
                            r"Nothing about taking logs touches the independence assumption. The words are exactly as dependent as they were, and the model exactly as approximate; only the representation of the arithmetic has changed.",
                            r"They rank identically, and that is the whole reason logs are usable: $\log$ is strictly increasing, so it preserves order. If the two rankings differed, working in logs would be a bug rather than a technique.",
                            r"The independence assumption is what licenses the product, so that part is fair — but adding logs is the same claim in different clothing, not an escape from it. $\log(ab) = \log a + \log b$ holds whether or not the product was justified.",
                        ],
                        "why": r"""
A double-precision float bottoms out near $10^{-308}$, and a two-hundred-word document
gives a product around $10^{-600}$. Both classes then evaluate to exactly `0.0` — no
exception, no warning, and a comparison of two zeros that returns whatever the tie rule
names. In logs the same quantity is about $-1381.55$, a number with plenty of room, and
because $\log$ is strictly increasing the largest log score belongs to the largest
probability. The prior becomes a single additive constant, which is the whole of the MAP
rule as it appears in code.
""",
                    },
                    {
                        "q": r"A hypothesis is assigned a prior of exactly $0$. What can later evidence do to it?",
                        "opts": [
                            r"Raise it, provided the evidence is strong enough to overcome the initial assignment of zero",
                            r"Nothing — every numerator $P(E \mid H)P(H)$ is zero, so the posterior stays at zero for ever",
                            r"Raise it once the other hypotheses have been eliminated, since the posterior masses have to sum to one",
                            r"Make the update undefined, because a zero prior means the total evidence probability is zero as well",
                        ],
                        "a": 1,
                        "whys": [
                            r"There is no strength of evidence that multiplies zero into something positive. Assigning a zero prior is a permanent exclusion, not a strongly held opinion that data could revise.",
                            r"The update multiplies the prior, and multiplying zero by any likelihood leaves zero.",
                            r"Renormalising divides by the sum of the numerators, and a zero numerator divided by anything positive is still zero. Eliminating rivals redistributes mass among hypotheses that have some, never to one that has none.",
                            r"Only if *every* hypothesis has a zero numerator. With other hypotheses carrying positive prior and likelihood the evidence total is positive, the division is well defined, and this one remains at zero.",
                        ],
                        "why": r"""
The update is prior times likelihood, renormalised, and $0 \times P(E \mid H) = 0$ for
every possible observation. The posterior is zero, and so is the posterior after that, for
ever. A zero prior is therefore not a strong opinion but a permanent exclusion — the reason
this is worth stating is that assigning zero feels like ordinary emphasis, whereas it
removes a hypothesis from consideration irreversibly. It is the same mechanism that makes
an unsmoothed count of zero veto a whole class, which is why the filter smooths. The one
case that does break the arithmetic is different: if every hypothesis has a zero numerator,
the normaliser is zero too, and the lab raises `ValueError` rather than dividing.
""",
                    },
                    {
                        "q": r"A naive Bayes filter reports $P(\text{spam}) = 0.9999$ for a message. How should that number be read?",
                        "opts": [
                            r"As a well-founded probability, since the independence assumption affects only which label is chosen and not the score attached to it",
                            r"As a ranking signal, since correlated words are counted repeatedly and push the score towards the extremes",
                            r"As an underestimate, because add-alpha smoothing pulls every estimate towards the uniform distribution",
                            r"As a probability conditional on the training corpus, which is the only sense in which any classifier's output can be read",
                        ],
                        "a": 1,
                        "whys": [
                            r"It is the other way round. The independence assumption damages the magnitudes badly and leaves the ordering largely intact, which is why the label is usable and the score is not.",
                            r"Two occurrences of `cheap`, or `new` beside `york`, are multiplied in as though each carried fresh independent evidence.",
                            r"Smoothing does pull estimates towards uniform, which would push a score down rather than up — but it is a small effect beside the double-counting, and calling $0.9999$ an underestimate gets the direction of the dominant error backwards.",
                            r"Everything a model outputs is conditional on its training data, so this is true of every classifier and therefore explains nothing about this one. It also leaves the reader believing the $0.9999$ is otherwise sound.",
                        ],
                        "why": r"""
The naive assumption treats every word as fresh independent evidence, so correlated words —
`new` and `york`, or `cheap` twice in one message — are multiplied in repeatedly and drive
the score much further than the evidence jointly warrants. The result is a distribution
piled up near $0$ and $1$: the ordering of the classes usually survives, which is why the
classifier works, but the magnitude does not, which is why thresholding at "$99$ per cent
sure" is reading a number the model cannot supply. Use it to choose a label or to rank
messages; do not report it as a probability without calibrating it against held-out data.
""",
                    },
                ],
            },
            "lab": {
                "title": "Posterior updates and a spam filter",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
## Part 1 — Bayes' rule

**`bayes_posterior(prior, likelihood)`** — both are dicts keyed by hypothesis.
Returns the renormalised posterior. `ValueError` when the prior does not sum to 1
within `1e-9`, when a hypothesis is missing from `likelihood`, or when the total
evidence probability is zero — that last case means the observation was
impossible under every hypothesis, which is a modelling error, not a number.

**`sequential_update(prior, observations)`** — fold a list of likelihood dicts in
left to right, each posterior becoming the next prior.

The screening example: a condition affecting 1 in 1000, a test that catches 99%
of cases and gives a false positive 5% of the time. One positive result takes
you from 0.001 to about 0.0194 — a nineteenfold jump that still leaves the
answer almost certainly "no".

## Part 2 — naive Bayes

`NaiveBayes(alpha=1.0)` with add-alpha smoothing over the shared vocabulary.

- `tokenise(text)` — a static method: lowercase, then every run of letters and
  digits, so `"Buy CHEAP pills!"` gives `["buy", "cheap", "pills"]`.
- `train(docs)` — `docs` is a list of `(text, label)`. `ValueError` when empty.
- `log_prob(text, label)` — `log P(label) + sum of log P(word | label)`, where

```text
P(word | label) = (count(word, label) + alpha) / (total(label) + alpha * |V|)
```

  and `|V|` is the size of the vocabulary seen in training. `ValueError` before
  training or for an unknown label.
- `classify(text)` — the label with the highest `log_prob`; ties go to the
  alphabetically first label, so an all-unseen document has a defined answer.

Work in logs throughout. A product of two hundred small probabilities underflows
to exactly zero in double precision, and a comparison of zeros decides nothing.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import re

CORPUS = [
    ("buy cheap pills", "spam"),
    ("cheap deal now", "spam"),
    ("meet me for lunch", "ham"),
    ("lunch tomorrow", "ham"),
]


def bayes_posterior(prior, likelihood):
    """Prior times likelihood, renormalised."""
    # your code here


def sequential_update(prior, observations):
    """Fold a list of likelihood dicts into the prior, left to right."""
    # your code here


class NaiveBayes:
    """Multinomial naive Bayes with add-alpha smoothing."""

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.counts = {}      # label -> {word: count}
        self.totals = {}      # label -> tokens seen
        self.docs = {}        # label -> documents seen
        self.total_docs = 0
        self.vocab = set()

    @staticmethod
    def tokenise(text):
        """Lowercased runs of letters and digits."""
        # your code here

    def train(self, docs):
        """Count words per label. ValueError on an empty corpus."""
        # your code here

    def log_prob(self, text, label):
        """log P(label) + sum of log P(word | label)."""
        # your code here

    def classify(self, text):
        """The most probable label; ties break alphabetically."""
        # your code here


print(bayes_posterior({"ill": 0.001, "well": 0.999},
                      {"ill": 0.99, "well": 0.05}))
model = NaiveBayes()
model.train(CORPUS)
print(model.classify("cheap pills"), model.classify("lunch tomorrow"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import re

CORPUS = [
    ("buy cheap pills", "spam"),
    ("cheap deal now", "spam"),
    ("meet me for lunch", "ham"),
    ("lunch tomorrow", "ham"),
]


def bayes_posterior(prior, likelihood):
    """Prior times likelihood, renormalised."""
    if abs(sum(prior.values()) - 1.0) > 1e-9:
        raise ValueError(f"the prior sums to {sum(prior.values())!r}, not 1")
    if any(mass < 0 for mass in prior.values()):
        raise ValueError("a prior probability cannot be negative")
    missing = set(prior) - set(likelihood)
    if missing:
        raise ValueError(f"no likelihood given for {sorted(missing)}")
    joint = {h: prior[h] * likelihood[h] for h in prior}
    evidence = sum(joint.values())
    if evidence == 0:
        raise ValueError("the observation is impossible under every hypothesis")
    return {h: value / evidence for h, value in joint.items()}


def sequential_update(prior, observations):
    """Fold a list of likelihood dicts into the prior, left to right."""
    posterior = dict(prior)
    for likelihood in observations:
        posterior = bayes_posterior(posterior, likelihood)
    return posterior


class NaiveBayes:
    """Multinomial naive Bayes with add-alpha smoothing."""

    def __init__(self, alpha=1.0):
        self.alpha = alpha
        self.counts = {}      # label -> {word: count}
        self.totals = {}      # label -> tokens seen
        self.docs = {}        # label -> documents seen
        self.total_docs = 0
        self.vocab = set()

    @staticmethod
    def tokenise(text):
        """Lowercased runs of letters and digits."""
        return re.findall(r"[a-z0-9]+", text.lower())

    def train(self, docs):
        """Count words per label. ValueError on an empty corpus."""
        if not docs:
            raise ValueError("cannot train on an empty corpus")
        for text, label in docs:
            self.counts.setdefault(label, {})
            self.totals.setdefault(label, 0)
            self.docs[label] = self.docs.get(label, 0) + 1
            self.total_docs += 1
            for word in self.tokenise(text):
                self.counts[label][word] = self.counts[label].get(word, 0) + 1
                self.totals[label] += 1
                self.vocab.add(word)
        return self

    def log_prob(self, text, label):
        """log P(label) + sum of log P(word | label)."""
        if not self.total_docs:
            raise ValueError("the model has not been trained")
        if label not in self.counts:
            raise ValueError(f"unknown label {label!r}")
        denominator = self.totals[label] + self.alpha * len(self.vocab)
        score = math.log(self.docs[label] / self.total_docs)
        for word in self.tokenise(text):
            count = self.counts[label].get(word, 0)
            # every word gets alpha of imaginary evidence, so nothing is impossible
            score += math.log((count + self.alpha) / denominator)
        return score

    def classify(self, text):
        """The most probable label; ties break alphabetically."""
        if not self.total_docs:
            raise ValueError("the model has not been trained")
        best_label = None
        best_score = None
        for label in sorted(self.counts):        # sorted, so ties go alphabetically
            score = self.log_prob(text, label)
            if best_score is None or score > best_score:
                best_label, best_score = label, score
        return best_label


print(bayes_posterior({"ill": 0.001, "well": 0.999},
                      {"ill": 0.99, "well": 0.05}))
model = NaiveBayes()
model.train(CORPUS)
print(model.classify("cheap pills"), model.classify("lunch tomorrow"))
'''}],
                "hints": [
                    "`bayes_posterior` is three lines of arithmetic and four of validation: multiply, sum, divide.",
                    "`sequential_update` should call `bayes_posterior` in a loop rather than reimplementing it — that also inherits the validation.",
                    "Accumulate the vocabulary across *all* labels; the smoothing denominator uses the shared |V|, not the per-label word count.",
                    "Iterate the labels in `sorted()` order inside `classify` and compare with a strict `>`; the first-seen label then wins any tie.",
                ],
                "tests": [
                    {"name": "The base-rate fallacy, in numbers", "code": r'''
_post = bayes_posterior({"ill": 0.001, "well": 0.999}, {"ill": 0.99, "well": 0.05})
assert abs(_post["ill"] - 0.019434628975265017) < 1e-12, \
    f"P(ill | positive) is {_post['ill']!r}, expected about 0.01943"
assert abs(sum(_post.values()) - 1.0) < 1e-12, "A posterior is still a distribution"
assert _post["ill"] > 0.001, "One positive test should still raise the probability nineteenfold"
'''},
                    {"name": "bayes_posterior validates its inputs", "code": r'''
for _prior, _like in [({"a": 0.5, "b": 0.2}, {"a": 1.0, "b": 1.0}),
                      ({"a": 0.5, "b": 0.5}, {"a": 1.0}),
                      ({"a": 0.5, "b": 0.5}, {"a": 0.0, "b": 0.0}),
                      ({"a": 1.5, "b": -0.5}, {"a": 1.0, "b": 1.0})]:
    try:
        bayes_posterior(_prior, _like)
        assert False, f"bayes_posterior({_prior!r}, {_like!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Evidence accumulates across observations", "code": r'''
_prior = {"ill": 0.001, "well": 0.999}
_test = {"ill": 0.99, "well": 0.05}
_one = sequential_update(_prior, [_test])
_two = sequential_update(_prior, [_test, _test])
assert abs(_one["ill"] - bayes_posterior(_prior, _test)["ill"]) < 1e-12, \
    "One observation is just a single Bayes update"
assert _two["ill"] > _one["ill"] > _prior["ill"], "A second positive must raise it further"
assert abs(_two["ill"] - 0.2818323) < 1e-6, f"After two positives: {_two['ill']!r}"
_negative = {"ill": 0.01, "well": 0.95}
assert abs(sequential_update(_prior, [_test, _negative])["ill"]
           - sequential_update(_prior, [_negative, _test])["ill"]) < 1e-12, \
    "Independent evidence gives the same posterior in either order"
assert sequential_update(_prior, []) == _prior, "No evidence leaves the prior alone"
'''},
                    {"name": "tokenise normalises text", "code": r'''
assert NaiveBayes.tokenise("Buy CHEAP pills!") == ["buy", "cheap", "pills"], \
    f'Got {NaiveBayes.tokenise("Buy CHEAP pills!")!r}'
assert NaiveBayes.tokenise("") == [], "No words, no tokens"
assert NaiveBayes.tokenise("...!!!") == [], "Punctuation alone yields nothing"
assert NaiveBayes.tokenise("win 100 now") == ["win", "100", "now"], "Digits are kept"
'''},
                    {"name": "Smoothed conditional probabilities are exact", "code": r'''
import math as _math
_nb = NaiveBayes()
_nb.train(CORPUS)
assert len(_nb.vocab) == 10, f"The shared vocabulary has {len(_nb.vocab)} words, expected 10"
assert _nb.totals["spam"] == 6 and _nb.totals["ham"] == 6, f"totals: {_nb.totals!r}"
_want = _math.log(0.5) + _math.log(3 / 16)
assert abs(_nb.log_prob("cheap", "spam") - _want) < 1e-12, \
    f"log_prob('cheap', 'spam') is {_nb.log_prob('cheap', 'spam')!r}, expected {_want!r}"
_want_ham = _math.log(0.5) + _math.log(1 / 16)
assert abs(_nb.log_prob("cheap", "ham") - _want_ham) < 1e-12, \
    "An unseen word still gets alpha / (total + alpha |V|), never zero"
'''},
                    {"name": "The classifier separates the two classes", "code": r'''
_nb = NaiveBayes()
_nb.train(CORPUS)
assert _nb.classify("cheap pills") == "spam", "Both words appear only in spam"
assert _nb.classify("lunch tomorrow") == "ham", "Both words appear only in ham"
assert _nb.classify("cheap cheap cheap lunch") == "spam", "Repeated evidence should compound"
assert _nb.classify("zzz") == "ham", \
    "An all-unseen document ties, and the tie breaks to the alphabetically first label"
assert _nb.log_prob("zzz qqq", "spam") > float("-inf"), \
    "Smoothing must keep the score finite for unseen words"
'''},
                    {"name": "The model refuses to guess before it is trained", "code": r'''
_fresh = NaiveBayes()
for _call in (lambda: _fresh.classify("anything"), lambda: _fresh.log_prob("x", "spam")):
    try:
        _call()
        assert False, "Using an untrained model should raise ValueError"
    except ValueError:
        pass
try:
    _fresh.train([])
    assert False, "Training on an empty corpus should raise ValueError"
except ValueError:
    pass
_nb = NaiveBayes()
_nb.train(CORPUS)
try:
    _nb.log_prob("cheap", "banana")
    assert False, "An unknown label should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M11
        {
            "title": "Least squares and linear regression",
            "summary": (
                "Fitting one predictor by minimising squared error, reading the "
                "residuals, and the two claims the arithmetic cannot make for you. "
                "The many-predictor matrix form belongs to Machine Learning; the "
                "statistics behind it belong here."
            ),
            "concepts": [
                r"Least squares picks the line minimising $\sum (y_i - \hat{y}_i)^2$; setting both partial derivatives to zero gives $\hat{\beta}_1 = \mathrm{Cov}(x, y)/\mathrm{Var}(x)$ and $\hat{\beta}_0 = \bar{y} - \hat{\beta}_1 \bar{x}$",
                r"Under independent normal errors of constant variance the least-squares fit *is* the maximum-likelihood fit, so squaring the residuals is a claim about the noise rather than a neutral default",
                r"$R^2$ is the fraction of the variance in $y$ the fit accounts for; it can never fall when a predictor is added, so it cannot judge whether a model is too large",
                "Residual plots test what the summary number cannot: curvature, spread that grows with the fitted value, and single points dragging the line",
                "A fitted slope is an association inside the observed range — extrapolation beyond it and any causal reading of it are both outside what least squares supports",
                'The residual is measured vertically, which makes the two variables asymmetric: the slopes of $y$ on $x$ and of $x$ on $y$ multiply to $r^{2}$, so the two lines coincide only for a perfect fit',
                'In standardised units the fit is $z_{\\hat{y}} = r z_{x}$, so every prediction is pulled toward the mean by the factor $r$ — that is regression to the mean, and where the technique got its name',
                'The first normal equation forces the residuals to sum to zero and the fitted line to pass through the centroid $(\\bar{x}, \\bar{y})$, always',
                "In a simple regression with an intercept $R^{2}$ is exactly $r^{2}$, which is what makes 'the fraction of variance explained' a concrete claim rather than a slogan",
            ],
            "read": [
                {
                    "title": 'The line that minimises squares, and the two claims it cannot make',
                    "minutes": 14,
                    "body": r'''
Five measurements of a service, batch size against mean latency:

```text
    batch x      2      4      6      8     10
    ms    y    3.1    4.2    6.5    7.1    9.6
```

Fitting a straight line to that looks like an obvious thing to want, and it is. What is
not obvious — and what the arithmetic will not tell you — is that three separate
decisions have already been made by the time anyone writes "least squares".

## The decisions inside the phrase

**The residual is measured vertically.** The quantity minimised is
$\sum (y_i - \hat{y}_i)^{2}$: the gap in $y$ at a given $x$. Not the perpendicular
distance to the line, which would be a different fit. This makes the two variables
asymmetric — $x$ is treated as known and $y$ as the thing carrying the error — and that
asymmetry has a consequence taken up at the end of this unit.

**The errors are squared.** Squaring is a claim about the noise, not a neutral default.
Write the likelihood of the data under independent normal errors of constant variance:
the only term containing the coefficients is $-\sum(y_i - \hat{y}_i)^{2}/(2\sigma^{2})$,
so maximising the likelihood **is** minimising the squared error. Least squares is
maximum likelihood for normal noise. When the noise has heavy tails, a different loss is
the principled response rather than a robustness trick bolted on afterwards.

**The relationship is a straight line.** Nothing in the fitting procedure checks this,
and $R^{2}$ will not check it either.

## Deriving the two coefficients

Minimise $Q(\beta_0, \beta_1) = \sum (y_i - \beta_0 - \beta_1 x_i)^{2}$ by setting both
partial derivatives to zero.

$$\frac{\partial Q}{\partial \beta_0} = -2\sum (y_i - \beta_0 - \beta_1 x_i) = 0$$

The sum of the residuals is therefore zero — which is a consequence, not an assumption —
and dividing by $n$ gives $\bar{y} = \beta_0 + \beta_1 \bar{x}$, so

$$\beta_0 = \bar{y} - \beta_1\bar{x} .$$

The fitted line passes through the centroid $(\bar{x}, \bar{y})$, always. For the slope,

$$\frac{\partial Q}{\partial \beta_1} = -2\sum x_i(y_i - \beta_0 - \beta_1 x_i) = 0 ,$$

and substituting $\beta_0$ from above turns this into
$\sum (x_i - \bar{x})(y_i - \bar{y}) = \beta_1 \sum (x_i - \bar{x})^{2}$, so writing
$S_{xy}$ and $S_{xx}$ for those two sums,

$$\beta_1 = \frac{S_{xy}}{S_{xx}} = \frac{\mathrm{Cov}(x,y)}{\mathrm{Var}(x)} .$$

The spread of the **predictor** is in the denominator, because that is the range the line
has to span.

## Worked, end to end

$\bar{x} = 6$ and $\bar{y} = 6.1$. The three sums are

$$S_{xx} = 40, \qquad S_{yy} = 26.02, \qquad S_{xy} = 31.8 .$$

$$\beta_1 = \frac{31.8}{40} = 0.795, \qquad
\beta_0 = 6.1 - 0.795 \times 6 = 1.33$$

So $\hat{y} = 1.33 + 0.795x$ — about $0.8$ ms per unit of batch. The fitted values and
residuals:

```text
    x        2       4       6       8      10
    y      3.10    4.20    6.50    7.10    9.60
    fit    2.92    4.51    6.10    7.69    9.28
    res    0.18   -0.31    0.40   -0.59    0.32     sum = 0
```

The residuals sum to zero, as the first normal equation guarantees. Their squared total
is $\mathrm{SSE} = 0.739$, against a total spread of $S_{yy} = 26.02$, so

$$R^{2} = 1 - \frac{0.739}{26.02} = 0.971599 .$$

The correlation is $r = 31.8/\sqrt{40 \times 26.02} = 0.985697$, and

$$r^{2} = 0.971599 = R^{2} .$$

That is not a coincidence of these numbers. In a simple regression with an intercept,
$R^{2}$ **is** the squared correlation, which is what makes the phrase "the fraction of
variance explained" mean anything concrete.

## How uncertain is that slope

$R^{2}$ says how much of the spread the line accounts for. It says nothing about whether
the slope could plausibly have been zero, and that needs the residuals turned into a
standard error.

Module 8 derived the rule: divide a sum of squared deviations by the number of
observations minus the number of quantities the data were used to locate. A line costs
two — an intercept and a slope — so the residual variance is

$$s^{2} = \frac{\mathrm{SSE}}{n - 2} = \frac{0.739}{3} = 0.246333,
\qquad s = 0.49632 \text{ ms} .$$

The divisor $3$ is the same accounting as module 8's $n - 1$, with one more parameter
paid for. The standard error of the slope then divides that by the spread of the
predictor, which is the second appearance of $S_{xx}$ in the denominator and for the same
reason — a predictor spread thinly over a wide range pins the slope down better:

$$\mathrm{SE}(\beta_1) = \frac{s}{\sqrt{S_{xx}}} = \frac{0.49632}{\sqrt{40}} = 0.078475 .$$

So $t = 0.795/0.078475 = 10.13$ on $3$ degrees of freedom, and with
$t_{0.975,\,3} = 3.182446$ the $95$ per cent interval for the slope is
$[0.5453,\, 1.0447]$. It excludes zero, so the association survives the question "could
this have been noise". Note how wide it is regardless: five points buy an estimate of
$0.795$ that is consistent with anything from $0.55$ to $1.04$, which is the honest
statement and is invisible in $R^{2} = 0.97$.

## The mistake, and why it is tempting

Regressing $y$ on $x$ and regressing $x$ on $y$ do not give the same line, and the reason
is the first decision above. Swapping the roles minimises horizontal gaps instead of
vertical ones. The slope of $x$ on $y$ is

$$\frac{S_{xy}}{S_{yy}} = \frac{31.8}{26.02} = 1.222137 ,$$

and the product of the two slopes is

$$0.795 \times 1.222137 = 0.971599 = r^{2} .$$

If the two lines were inverses of each other the product would be $1$. It is $r^{2}$, so
they coincide only when $r^{2} = 1$ — a perfect fit — and otherwise the second line is
flatter than inverting the first would suggest. This is the same fact as **regression to
the mean**, and it is where the technique got its name. In standardised units the fitted
line is

$$z_{\hat{y}} = r\,z_x ,$$

so a point two standard deviations above average in $x$ is predicted to be $2r$ — not $2$
— above average in $y$. With $r = 0.9857$ that is a slight pull toward the mean; with
$r = 0.5$ it is a strong one. The prediction is shrunk toward the average by the factor
$r$, always, and nothing about the underlying process is "regressing" anywhere. It is
what minimising vertical squared error does.

## Where it stops

**$R^{2}$ cannot judge model size.** Add a column of pure random noise as an extra
predictor and $R^{2}$ cannot fall, because the larger model can always reproduce the
smaller one by giving the new column a coefficient of zero. It will usually rise a
little. So $R^{2}$ measured on training data is not evidence that a model is better than
a smaller one, and held-out data or an adjusted criterion is needed instead.

**A high $R^{2}$ does not mean the model is right.** $R^{2}$ counts how much variance is
left over; it never inspects the *shape* of what is left. A regression scoring $0.94$
whose residuals plotted against $x$ form a clear U is telling you the relationship is
curved: the line sits above the data at both ends and below it in the middle, which is
what fitting a straight line to a curve always produces. The residual plot sees that
immediately and the summary number cannot see it at all.

**The fit is an association inside the observed range.** Two limits, both routinely
crossed. Extrapolation: this line at $x = 40$ predicts $33.13$ ms, and the data end at
$x = 10$ — nothing in the fit knows whether the service saturates, thrashes or falls over
somewhere in between. And causation: a regression of drowning deaths on ice-cream sales
gives a strongly positive, highly significant slope, because summer drives both. A
p-value asks whether the association could plausibly be zero. It does not ask about
direction or mechanism, and separating those needs an intervention or a design that
controls the confounder, not more data.
''',
                },
            ],
            "derive": [
                {
                    "title": 'The normal equations, and the shrinkage hiding in the slope',
                    "minutes": 12,
                    "vars": ['S_xx', 'S_xy', 'S_yy', 'b_0', 'b_1', 'm_x', 'm_y', 'r', 's_x', 's_y'],
                    "brief": r'''
Least squares is two partial derivatives set to zero. Doing it rather than quoting it
produces the coefficients and, at the end, an identity that explains the name of the
whole technique.

Write $m_{x}$ and $m_{y}$ for the two sample means (the reference answers use $m_{x}$
and $m_{y}$ rather than a bar, so that each mean is a symbol in its own right),
$s_{x}$ and $s_{y}$ for the two sample standard deviations, $b_{0}$ and $b_{1}$ for the
intercept and slope, $r$ for the correlation, and

$$S_{xx} = \sum (x_i - m_x)^{2}, \quad S_{yy} = \sum (y_i - m_y)^{2}, \quad
S_{xy} = \sum (x_i - m_x)(y_i - m_y) .$$
''',
                    "steps": [
                        {
                            "prompt": 'Setting $\\partial Q/\\partial b_{0} = 0$ gives $\\sum (y_i - b_0 - b_1 x_i) = 0$; divide by $n$. Write $b_{0}$ in terms of $m_{x}$, $m_{y}$ and $b_{1}$.',
                            "answer": 'm_{y} - b_{1} m_{x}',
                            "placeholder": 'rearrange the centroid equation',
                            "hint": 'Dividing by $n$ turns the sum into $m_y - b_0 - b_1 m_x = 0$; solve for $b_{0}$.',
                        },
                        {
                            "prompt": 'Setting $\\partial Q/\\partial b_{1} = 0$ and substituting the intercept gives $S_{xy} = b_{1}S_{xx}$. Write $b_{1}$ in terms of $S_{xy}$ and $S_{xx}$.',
                            "answer": '\\frac{S_{xy}}{S_{xx}}',
                            "hint": 'Divide both sides by $S_{xx}$, which is positive whenever the predictor is not constant.',
                        },
                        {
                            "prompt": 'The correlation puts the same cross-product on a unitless scale by dividing by both spreads. Write $r$ in terms of $S_{xy}$, $S_{xx}$ and $S_{yy}$.',
                            "answer": '\\frac{S_{xy}}{\\sqrt{S_{xx} \\cdot S_{yy}}}',
                            "hint": 'Divide $S_{xy}$ by the square root of the product of the two sums of squares.',
                            "deconstruct": [
                                '$r = \\mathrm{Cov}(x,y)/(s_x s_y)$, and each of the three is a sum divided by $n - 1$.',
                                'Those divisors cancel, leaving $S_{xy}$ over $\\sqrt{S_{xx}S_{yy}}$.',
                                'Write the two factors under the root separated, not run together.',
                            ],
                        },
                        {
                            "prompt": 'Now connect them. Since $s_{x}^{2} = S_{xx}/(n-1)$ and $s_{y}^{2} = S_{yy}/(n-1)$, substitute $S_{xy} = r\\sqrt{S_{xx} \\cdot S_{yy}}$ into step 2. Write $b_{1}$ in terms of $r$, $s_{x}$ and $s_{y}$.',
                            "answer": '\\frac{r s_{y}}{s_{x}}',
                            "hint": '$b_1 = r\\sqrt{S_{xx}S_{yy}}/S_{xx} = r\\sqrt{S_{yy}/S_{xx}}$, and that ratio of root sums is $s_{y}/s_{x}$.',
                            "deconstruct": [
                                '$b_1 = S_{xy}/S_{xx} = r\\sqrt{S_{xx} \\cdot S_{yy}}/S_{xx}$.',
                                'Simplifying the roots gives $r\\sqrt{S_{yy}/S_{xx}}$.',
                                'The common divisor $n-1$ turns that into $r s_{y}/s_{x}$, so in standardised units the slope is exactly $r$.',
                            ],
                        },
                        {
                            "prompt": 'Swap the roles of the variables. Regressing $x$ on $y$ minimises horizontal gaps, so the same algebra runs with $S_{yy}$ in the denominator. Write that slope in terms of $S_{xy}$ and $S_{yy}$.',
                            "answer": '\\frac{S_{xy}}{S_{yy}}',
                            "hint": 'Step 2 with $x$ and $y$ interchanged throughout.',
                        },
                        {
                            "prompt": 'Multiply the two slopes from steps 2 and 5 together and simplify using step 3. Write the product.',
                            "answer": 'r^{2}',
                            "hint": '$\\frac{S_{xy}}{S_{xx}} \\cdot \\frac{S_{xy}}{S_{yy}} = \\frac{S_{xy}^{2}}{S_{xx}S_{yy}}$, and step 3 says that is $r$ squared.',
                            "deconstruct": [
                                'The product is $S_{xy}^{2}/(S_{xx}S_{yy})$.',
                                'Step 3 gives $r = S_{xy}/\\sqrt{S_{xx}S_{yy}}$, so squaring it gives exactly that ratio.',
                                'Hence the product of the two slopes is $r^{2}$, which is $1$ only for a perfect fit.',
                            ],
                        },
                    ],
                    "closing": r'''
Step 6 settles a question that trips people up: the line of $y$ on $x$ and the line of
$x$ on $y$ are not the same line, and they are not inverses of each other. Their slopes
multiply to $r^{2}$, so they coincide only when $r^{2} = 1$. For the worked data
$0.795 \times 1.222137 = 0.971599$, which is $r^{2}$ to every digit shown.

Step 4 is the same fact wearing its more famous name. In standardised units the fitted
line is $z_{\hat{y}} = r z_{x}$, so every prediction is pulled toward the mean by the
factor $r$. That is **regression to the mean**, and it is not a force acting on the data
— it is what minimising vertical squared error does, visible here as a factor of $r$ that
appears the moment the slope is written in standardised form.

One consequence worth keeping. Because $|r| \le 1$ — module 5 derived that from the
non-negativity of a variance — the predicted spread is always narrower than the observed
spread. A fitted model under-disperses by construction, which is why fitted values should
never be used as though they were fresh data.
''',
                },
            ],
            "quiz": {
                "title": "Fitting a line, and reading it honestly",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"In a simple linear regression of $y$ on $x$, which expression gives the slope that minimises the squared error?",
                        "opts": [
                            r"$\mathrm{Cov}(x, y)/\mathrm{Var}(y)$",
                            r"$\mathrm{Var}(y)/\mathrm{Var}(x)$",
                            r"The correlation between $x$ and $y$",
                            r"$\mathrm{Cov}(x, y)/\mathrm{Var}(x)$",
                        ],
                        "a": 3,
                        "why": (
                            r"Differentiating the sum of squared residuals with respect to the slope and setting it "
                            r"to zero gives $\mathrm{Cov}(x, y)/\mathrm{Var}(x)$ — the spread of the *predictor* is "
                            r"in the denominator, since that is the range the line has to cover. The correlation is "
                            r"this same slope after both variables have been standardised, which is why it is "
                            r"unitless while the slope carries units of $y$ per unit of $x$."
                        ),
                    },
                    {
                        "q": r"You add a column of pure random noise to the model as an extra predictor. What happens to $R^2$ measured on the training data?",
                        "opts": [
                            "It cannot fall, and will usually rise a little",
                            "It falls, because the column carries no signal",
                            "It stays exactly the same",
                            "It becomes undefined",
                        ],
                        "a": 0,
                        "why": (
                            r"The larger model can always reproduce the smaller one by giving the new column a "
                            r"coefficient of zero, so the best achievable squared error can only go down and $R^2$ "
                            r"can only go up. That is exactly why $R^2$ cannot choose between models of different "
                            r"sizes, and why held-out data or an adjusted criterion is needed instead."
                        ),
                    },
                    {
                        "q": r"A regression reports $R^2 = 0.94$, but the residuals plotted against $x$ form a clear U shape. What does that tell you?",
                        "opts": [
                            "The fit is excellent, so the residuals can be ignored",
                            "The data contain a single influential outlier",
                            r"The relationship is curved, so a straight line is the wrong model despite the high $R^2$",
                            "The errors have constant variance, exactly as required",
                        ],
                        "a": 2,
                        "why": (
                            r"A U-shaped residual pattern means the line sits above the data at both ends and below "
                            r"it in the middle, which is what fitting a straight line to a curve always produces. "
                            r"$R^2$ counts only how much variance is left over; it never inspects the *shape* of "
                            r"what is left, so a systematically wrong model can still score very well."
                        ),
                    },
                    {
                        "q": "What is the connection between least squares and maximum likelihood?",
                        "opts": [
                            "There is none — they are unrelated procedures",
                            "Least squares is the maximum-likelihood fit when the errors are independent and normal with constant variance",
                            "Maximum likelihood always leaves a smaller residual sum than least squares",
                            "Least squares is the maximum-likelihood fit when the errors are uniform",
                        ],
                        "a": 1,
                        "why": (
                            r"Write the likelihood of the data under normal errors and take logs: the only term "
                            r"containing the coefficients is $-\sum (y_i - \hat{y}_i)^2/(2\sigma^2)$, so maximising "
                            r"the likelihood is minimising the squared error. Squaring is therefore an assumption "
                            r"about the noise, and when the noise has heavy tails a different loss is the "
                            r"principled response rather than a robustness trick."
                        ),
                    },
                    {
                        "q": "A regression of drowning deaths on ice-cream sales gives a strongly positive, highly significant slope. What may be concluded?",
                        "opts": [
                            "Ice cream causes drownings",
                            "Nothing at all, because a significant slope is always spurious",
                            "The two are associated in this data; the slope alone cannot separate a cause from a shared driver such as summer heat",
                            "Drownings cause ice-cream sales",
                        ],
                        "a": 2,
                        "why": (
                            r"Least squares fits an association and a p-value asks whether that association could "
                            r"plausibly be zero. Neither speaks to direction or mechanism, and a variable driving "
                            r"both — here the season — reproduces the pattern exactly. Telling the two apart needs "
                            r"an intervention or a design that controls the confounder, not more data."
                        ),
                    },
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an A/B test analyser",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
An experiment produced two samples of a continuous metric — session length,
latency, basket value. Turn them into a decision that survives being questioned.
`abtest.py` holds the statistics and is what the checks import; `main.py` runs
one analysis and prints the report.

Both critical-value tables are given at the top of the starter.

## Descriptives

`summarise(xs)` — `{"n", "mean", "var", "sd"}` with the unbiased variance;
`ValueError` for fewer than two observations.

## Classical inference

- `welch_t(a, b)` — `(t, df)`, exactly as in the inference lab, with
  `t = (mean_a - mean_b) / sqrt(var_a/n_a + var_b/n_b)`.
- `t_critical(df)` — the two-sided 5% value, rounding `df` **down** to the
  largest tabulated entry; `ValueError` for `df < 1`.
- `mean_diff_ci(a, b)` — the interval for `mean_b - mean_a`, that difference plus
  and minus `t_critical(df)` standard errors. Returned low end first.
- `cohens_d(a, b)` — `(mean_b - mean_a)` over the pooled standard deviation
  `sqrt(((n_a-1) var_a + (n_b-1) var_b) / (n_a + n_b - 2))`. `ValueError` when
  that pooled deviation is zero.

## Resampling

- `percentile(values, q)` — the `q` quantile by linear interpolation between
  order statistics: index `q * (n - 1)`, interpolating between its neighbours.
  `ValueError` on an empty sample or `q` outside `[0, 1]`.
- `bootstrap_diffs(a, b, trials=2000, seed=7)` — resample each group **with
  replacement** to its own size, `trials` times, and return the list of
  `mean_b - mean_a`. Use one `random.Random(seed)`, drawing `a` before `b` in
  each trial, so the output is reproducible. `ValueError` for `trials < 1`.
- `bootstrap_ci(a, b, trials=2000, seed=7)` — the 2.5th and 97.5th percentiles of
  those differences.

## The decision

`analyse(a, b, trials=2000, seed=7)` returns a dict with `n_control`,
`n_treatment`, `mean_control`, `mean_treatment`, `diff`, `t`, `df`, `critical`,
`significant`, `effect_size`, `ci`, `bootstrap_ci`, `decision` and
`assumptions`.

`decision` is `"ship"` when the result is significant and the difference is
positive, `"roll back"` when significant and negative, and `"hold"` otherwise.
`assumptions` is a list of at least three plain sentences naming what the
analysis takes on trust — independence, what the test does and does not say, and
what a confidence interval means.

## Suggested order

Descriptives, then the t machinery, then `percentile` (test it against a list you
can check by eye), then the bootstrap, and `analyse` last as pure assembly.
''',
        "deliverables": [
            "`abtest.py` — descriptives, Welch t, effect size, both intervals and `analyse`, importable with no side effects",
            "A conservative critical-value lookup that rounds fractional degrees of freedom down",
            "A percentile function built on linear interpolation between order statistics",
            "A seeded bootstrap whose output is bit-identical across runs",
            "`analyse` returning one dict that carries the estimate, the interval and the decision together",
            "`main.py` — a worked analysis of two samples, printed as a readable report",
        ],
        "constraints": [
            "Standard library only: `math` and `random` are the two imports you need",
            "`abtest.py` defines functions only — importing it must print nothing",
            "Every random draw comes from a `random.Random(seed)` instance, never the module-level functions",
            "No hard-coded critical values outside the two tables given",
            "`analyse` must not print or decide anything it cannot also report as a number",
        ],
        "rubric": [
            {"criterion": "Statistical correctness", "weight": 40,
             "evidence": "Welch t, degrees of freedom, effect size and both intervals reproduce the reference values to nine decimal places."},
            {"criterion": "Reproducibility", "weight": 20,
             "evidence": "The bootstrap gives identical output for a given seed and different output for a different one; nothing touches global random state."},
            {"criterion": "Edge cases and validation", "weight": 20,
             "evidence": "Single-observation samples, constant samples, empty percentile input and non-positive trial counts all raise ValueError."},
            {"criterion": "Reporting", "weight": 12,
             "evidence": "analyse returns every required field, decision agrees with significance and sign, and the assumptions are stated in the output."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "Docstrings on every public function, no duplicated variance code, and main.py free of statistics logic."},
        ],
        "hints": [
            "`summarise` is the only place that computes a mean or a variance; everything else consumes its dict.",
            "For `percentile`, `position = q * (n - 1)`, `low = int(position)`, and the weight is `position - low`; the top edge needs `min(low + 1, n - 1)`.",
            "Draw the control resample before the treatment resample inside each bootstrap trial, and take both from the same generator — that ordering is what makes the seed reproduce.",
            "`analyse` should call the other functions rather than recompute anything; if a number appears twice in your file, one of the two is wrong.",
        ],
        "files": [
            {"name": "abtest.py", "content": r'''
import math
import random

# two-sided critical values of Student's t at alpha = 0.05
T_CRITICAL_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 24: 2.064,
    30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980, 1000: 1.962,
}


def summarise(xs):
    """{n, mean, var, sd} with the unbiased variance."""
    # your code here


def welch_t(a, b):
    """(t, df) for the Welch two-sample t statistic."""
    # your code here


def t_critical(df):
    """Two-sided 5% critical value, rounding df down to the table."""
    # your code here


def mean_diff_ci(a, b):
    """Confidence interval for mean(b) - mean(a), low end first."""
    # your code here


def cohens_d(a, b):
    """Standardised mean difference, using the pooled standard deviation."""
    # your code here


def percentile(values, q):
    """The q quantile by linear interpolation between order statistics."""
    # your code here


def bootstrap_diffs(a, b, trials=2000, seed=7):
    """Resampled values of mean(b) - mean(a)."""
    # your code here


def bootstrap_ci(a, b, trials=2000, seed=7):
    """The middle 95% of the bootstrap distribution."""
    # your code here


def analyse(a, b, trials=2000, seed=7):
    """Estimate, intervals, effect size and a decision, in one dict."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from abtest import analyse

CONTROL = [12, 15, 14, 10, 13, 11, 14, 12]
TREATMENT = [22, 19, 25, 21, 23, 20, 24, 22]

report = analyse(CONTROL, TREATMENT)
print(f"control    n={report['n_control']} mean={report['mean_control']:.3f}")
print(f"treatment  n={report['n_treatment']} mean={report['mean_treatment']:.3f}")
print(f"difference {report['diff']:.3f}  effect size {report['effect_size']:.3f}")
print(f"t={report['t']:.3f} df={report['df']:.2f} critical={report['critical']}")
print("decision:", report["decision"])
for line in report["assumptions"]:
    print(" -", line)
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "abtest.py", "content": r'''
import math
import random

# two-sided critical values of Student's t at alpha = 0.05
T_CRITICAL_95 = {
    1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
    8: 2.306, 9: 2.262, 10: 2.228, 12: 2.179, 15: 2.131, 20: 2.086, 24: 2.064,
    30: 2.042, 40: 2.021, 60: 2.000, 120: 1.980, 1000: 1.962,
}


def summarise(xs):
    """{n, mean, var, sd} with the unbiased variance."""
    n = len(xs)
    if n < 2:
        raise ValueError("need at least two observations")
    mean = sum(xs) / n
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return {"n": n, "mean": mean, "var": var, "sd": math.sqrt(var)}


def _standard_error(a, b):
    """The Welch standard error of the difference, and its two components."""
    sa = summarise(a)
    sb = summarise(b)
    va = sa["var"] / sa["n"]
    vb = sb["var"] / sb["n"]
    return sa, sb, va, vb, math.sqrt(va + vb)


def welch_t(a, b):
    """(t, df) for the Welch two-sample t statistic."""
    sa, sb, va, vb, se = _standard_error(a, b)
    if se == 0:
        raise ValueError("both samples are constant, so the statistic is undefined")
    t = (sa["mean"] - sb["mean"]) / se
    df = (va + vb) ** 2 / (va ** 2 / (sa["n"] - 1) + vb ** 2 / (sb["n"] - 1))
    return t, df


def t_critical(df):
    """Two-sided 5% critical value, rounding df down to the table."""
    if df < 1:
        raise ValueError("degrees of freedom must be at least 1")
    return T_CRITICAL_95[max(k for k in T_CRITICAL_95 if k <= df)]


def mean_diff_ci(a, b):
    """Confidence interval for mean(b) - mean(a), low end first."""
    sa, sb, _va, _vb, se = _standard_error(a, b)
    _t, df = welch_t(a, b)
    margin = t_critical(df) * se
    diff = sb["mean"] - sa["mean"]
    return diff - margin, diff + margin


def cohens_d(a, b):
    """Standardised mean difference, using the pooled standard deviation."""
    sa = summarise(a)
    sb = summarise(b)
    pooled_var = ((sa["n"] - 1) * sa["var"] + (sb["n"] - 1) * sb["var"]) \
        / (sa["n"] + sb["n"] - 2)
    pooled = math.sqrt(pooled_var)
    if pooled == 0:
        raise ValueError("both samples are constant, so the effect size is undefined")
    return (sb["mean"] - sa["mean"]) / pooled


def percentile(values, q):
    """The q quantile by linear interpolation between order statistics."""
    if not values:
        raise ValueError("no values to take a percentile of")
    if q < 0 or q > 1:
        raise ValueError("q must lie in [0, 1]")
    ordered = sorted(values)
    position = q * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    weight = position - low
    return ordered[low] * (1 - weight) + ordered[high] * weight


def bootstrap_diffs(a, b, trials=2000, seed=7):
    """Resampled values of mean(b) - mean(a)."""
    if trials < 1:
        raise ValueError("need at least one bootstrap trial")
    if len(a) < 2 or len(b) < 2:
        raise ValueError("need at least two observations in each group")
    rng = random.Random(seed)              # private stream: reproducible
    diffs = []
    for _ in range(trials):
        # control first, then treatment — the draw order is part of the seed contract
        resample_a = [rng.choice(a) for _ in range(len(a))]
        resample_b = [rng.choice(b) for _ in range(len(b))]
        diffs.append(sum(resample_b) / len(b) - sum(resample_a) / len(a))
    return diffs


def bootstrap_ci(a, b, trials=2000, seed=7):
    """The middle 95% of the bootstrap distribution."""
    diffs = bootstrap_diffs(a, b, trials, seed)
    return percentile(diffs, 0.025), percentile(diffs, 0.975)


def analyse(a, b, trials=2000, seed=7):
    """Estimate, intervals, effect size and a decision, in one dict."""
    sa = summarise(a)
    sb = summarise(b)
    t, df = welch_t(a, b)
    critical = t_critical(df)
    significant = abs(t) > critical
    diff = sb["mean"] - sa["mean"]
    if significant:
        decision = "ship" if diff > 0 else "roll back"
    else:
        decision = "hold"
    return {
        "n_control": sa["n"], "n_treatment": sb["n"],
        "mean_control": sa["mean"], "mean_treatment": sb["mean"],
        "diff": diff,
        "t": t, "df": df, "critical": critical, "significant": significant,
        "effect_size": cohens_d(a, b),
        "ci": mean_diff_ci(a, b),
        "bootstrap_ci": bootstrap_ci(a, b, trials, seed),
        "decision": decision,
        "assumptions": [
            "Observations are independent within and between the two groups.",
            "The two groups may have different variances, which is why Welch's t is used "
            "rather than the pooled-variance form.",
            "A significant result means the data would be unusual if the groups were "
            "identical; it is not the probability that the treatment works.",
            "The confidence interval covers the true difference in 95% of repeated "
            "experiments, not with 95% probability for this one.",
            "The bootstrap assumes each sample represents its population well, which is "
            "a strong assumption at these sample sizes.",
        ],
    }
'''},
            {"name": "main.py", "content": r'''
from abtest import analyse

CONTROL = [12, 15, 14, 10, 13, 11, 14, 12]
TREATMENT = [22, 19, 25, 21, 23, 20, 24, 22]

report = analyse(CONTROL, TREATMENT)
print(f"control    n={report['n_control']} mean={report['mean_control']:.3f}")
print(f"treatment  n={report['n_treatment']} mean={report['mean_treatment']:.3f}")
print(f"difference {report['diff']:.3f}  effect size {report['effect_size']:.3f}")
print(f"t={report['t']:.3f} df={report['df']:.2f} critical={report['critical']}")
print(f"95% CI     [{report['ci'][0]:.3f}, {report['ci'][1]:.3f}]")
print(f"bootstrap  [{report['bootstrap_ci'][0]:.3f}, {report['bootstrap_ci'][1]:.3f}]")
print("decision:", report["decision"])
for line in report["assumptions"]:
    print(" -", line)
'''},
        ],
        "tests": [
            {"name": "summarise reports the four descriptives", "code": r'''
from abtest import summarise
_s = summarise([12, 15, 14, 10, 13])
assert _s["n"] == 5 and _s["mean"] == 12.8, f"Got {_s!r}"
assert abs(_s["var"] - 3.7) < 1e-12, f"var is {_s['var']!r}, expected 3.7 — divide by n - 1"
assert abs(_s["sd"] - 3.7 ** 0.5) < 1e-12, "sd is the square root of the variance"
for _bad in ([], [4]):
    try:
        summarise(_bad)
        assert False, f"summarise({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "The Welch statistic matches the reference", "code": r'''
from abtest import welch_t
_a = [12, 15, 14, 10, 13]
_b = [22, 19, 25, 21, 23]
_t, _df = welch_t(_a, _b)
assert abs(_t - (-6.974502000925911)) < 1e-9, f"t is {_t!r}, expected about -6.9745"
assert abs(_df - 7.825277849573533) < 1e-9, f"df is {_df!r}, expected about 7.8253"
try:
    welch_t([5, 5, 5], [5, 5, 5])
    assert False, "Two constant samples give a zero standard error and should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The critical-value lookup rounds down", "code": r'''
from abtest import t_critical
assert t_critical(7.825277849573533) == 2.365, f"Got {t_critical(7.825277849573533)!r}"
assert t_critical(1) == 12.706 and t_critical(11.9) == 2.228 and t_critical(500) == 1.980
for _bad in (0, 0.99, -4):
    try:
        t_critical(_bad)
        assert False, f"t_critical({_bad}) should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "The confidence interval brackets the difference", "code": r'''
from abtest import mean_diff_ci
_a = [12, 15, 14, 10, 13]
_b = [22, 19, 25, 21, 23]
_lo, _hi = mean_diff_ci(_a, _b)
assert _lo < 9.2 < _hi, f"The interval {(_lo, _hi)!r} should contain the observed difference 9.2"
assert abs(_lo - 6.080350742) < 1e-6, f"Lower bound is {_lo!r}, expected about 6.0804"
assert abs(_hi - 12.319649258) < 1e-6, f"Upper bound is {_hi!r}, expected about 12.3196"
assert _lo > 0, "The whole interval is above zero, which is why the result is significant"
'''},
            {"name": "Cohen's d standardises the difference", "code": r'''
from abtest import cohens_d
_a = [12, 15, 14, 10, 13]
_b = [22, 19, 25, 21, 23]
assert abs(cohens_d(_a, _b) - 4.411062373665534) < 1e-9, f"Got {cohens_d(_a, _b)!r}"
assert cohens_d(_b, _a) == -cohens_d(_a, _b), "Swapping the groups flips the sign"
assert abs(cohens_d(_a, _a)) < 1e-12, "A group against itself has no effect"
try:
    cohens_d([5, 5, 5], [7, 7, 7])
    assert False, "A zero pooled deviation should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "percentile interpolates between order statistics", "code": r'''
from abtest import percentile
assert percentile([1, 2, 3, 4, 5], 0.5) == 3, f"Got {percentile([1, 2, 3, 4, 5], 0.5)!r}"
assert percentile([1, 2, 3, 4], 0.5) == 2.5, "The median of four values sits between the middle two"
assert percentile([5, 1, 3], 0.0) == 1 and percentile([5, 1, 3], 1.0) == 5, \
    "The extremes are the smallest and largest values, whatever the input order"
assert abs(percentile([0, 10], 0.25) - 2.5) < 1e-12, f"Got {percentile([0, 10], 0.25)!r}"
for _bad in (-0.1, 1.1):
    try:
        percentile([1, 2, 3], _bad)
        assert False, f"percentile(values, {_bad}) should raise ValueError"
    except ValueError:
        pass
try:
    percentile([], 0.5)
    assert False, "percentile([], 0.5) should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The bootstrap is reproducible", "code": r'''
from abtest import bootstrap_diffs
_a = [12, 15, 14, 10, 13]
_b = [22, 19, 25, 21, 23]
_one = bootstrap_diffs(_a, _b, trials=200, seed=7)
assert len(_one) == 200, f"Expected 200 resampled differences, got {len(_one)}"
assert _one == bootstrap_diffs(_a, _b, trials=200, seed=7), \
    "The same seed must reproduce the same bootstrap exactly"
assert _one != bootstrap_diffs(_a, _b, trials=200, seed=8), \
    "A different seed must give a different bootstrap"
assert all(min(_b) - max(_a) <= d <= max(_b) - min(_a) for d in _one), \
    "A resampled mean cannot leave the range of its own sample"
for _bad in ((0, 7), (-5, 7)):
    try:
        bootstrap_diffs(_a, _b, trials=_bad[0], seed=_bad[1])
        assert False, f"bootstrap_diffs with trials={_bad[0]} should raise ValueError"
    except ValueError:
        pass
try:
    bootstrap_diffs([1], _b)
    assert False, "A one-observation group should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The bootstrap interval agrees with the t interval", "code": r'''
from abtest import bootstrap_ci, mean_diff_ci
_a = [12, 15, 14, 10, 13]
_b = [22, 19, 25, 21, 23]
_blo, _bhi = bootstrap_ci(_a, _b, trials=1000, seed=7)
assert _blo < 9.2 < _bhi, f"The bootstrap interval {(_blo, _bhi)!r} should contain 9.2"
assert _blo > 0, "The bootstrap should also place the whole interval above zero"
_tlo, _thi = mean_diff_ci(_a, _b)
assert abs(_blo - _tlo) < 4 and abs(_bhi - _thi) < 4, \
    f"The two intervals {(_blo, _bhi)!r} and {(_tlo, _thi)!r} should broadly agree"
'''},
            {"name": "analyse reports a significant difference", "code": r'''
from abtest import analyse
_r = analyse([12, 15, 14, 10, 13], [22, 19, 25, 21, 23], trials=500, seed=7)
for _key in ("n_control", "n_treatment", "mean_control", "mean_treatment", "diff",
             "t", "df", "critical", "significant", "effect_size", "ci",
             "bootstrap_ci", "decision", "assumptions"):
    assert _key in _r, f"analyse is missing the {_key!r} field"
assert _r["significant"] is True and _r["decision"] == "ship", f"Got {_r['decision']!r}"
assert abs(_r["diff"] - 9.2) < 1e-12, f"diff is {_r['diff']!r}, expected 9.2"
assert _r["critical"] == 2.365, f"critical is {_r['critical']!r}"
assert len(_r["assumptions"]) >= 3, "State at least three assumptions in plain sentences"
assert all(isinstance(s, str) and len(s) > 20 for s in _r["assumptions"]), \
    "Each assumption should be a readable sentence, not a keyword"
'''},
            {"name": "analyse holds when the groups overlap", "code": r'''
from abtest import analyse
_r = analyse([12, 15, 14, 10, 13], [13, 14, 12, 15, 11], trials=500, seed=7)
assert _r["significant"] is False, f"Overlapping groups must not be called different: {_r['t']!r}"
assert _r["decision"] == "hold", f"decision is {_r['decision']!r}, expected 'hold'"
assert _r["ci"][0] < 0 < _r["ci"][1], \
    f"An interval that straddles zero is the whole point here: {_r['ci']!r}"
_down = analyse([22, 19, 25, 21, 23], [12, 15, 14, 10, 13], trials=500, seed=7)
assert _down["decision"] == "roll back", \
    f"A significant drop should roll back, got {_down['decision']!r}"
assert _down["effect_size"] < 0, "A drop has a negative effect size"
'''},
            {"name": "abtest.py is import-clean and main.py reports", "code": r'''
_src = open("abtest.py").read()
assert "print(" not in _src, "abtest.py defines functions; the printing belongs in main.py"
assert "random.random(" not in _src and "random.choice(" not in _src, \
    "Use a random.Random(seed) instance, never the module-level generator"
assert "decision:" in _out, f"main.py should print the decision; stdout was {_out!r}"
assert "difference" in _out and "bootstrap" in _out, \
    "main.py should report the difference and the bootstrap interval"
'''},
        ],
    },
}
