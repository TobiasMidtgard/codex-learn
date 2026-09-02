"""CS411 — Information Theory & Coding. Author module."""

COURSE = {
    "id": "CS411",
    "title": "Information Theory & Coding",
    "year": 4,
    "level": "Advanced",
    "prereqs": ["MA201", "CS301"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 140,
    "icon": "⊕",
    "summary": (
        "One number governs how short a message can be made, and a second governs how "
        "much noise a link can carry. This course derives both from counting rather "
        "than announcing them, and then builds the machinery that reaches them: "
        "Huffman and arithmetic coders that close on the entropy bound, a channel "
        "simulator and a capacity solver, and linear block codes with a syndrome "
        "decoder that repairs what the channel broke. Every lab is checked against an "
        "exact reference — a code length, a syndrome, a corrected word — rather than "
        "against a tolerance."
    ),
    "outcomes": [
        "Derive entropy from the number of sequences a source can plausibly emit, not from a formula",
        "Compute joint, conditional and relative entropies and read the identities that connect them",
        "Build an optimal prefix code and prove its length sits between H and H+1",
        "Implement an arithmetic coder that spends a fractional number of bits per symbol",
        "Quantify the cost of coding with the wrong model as a relative entropy",
        "Simulate a discrete memoryless channel and compute its capacity numerically",
        "Encode, transmit and syndrome-decode a linear block code, and say which errors it cannot repair",
        "Assemble source coding, channel coding and a noisy link into one measured system",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone build (60%).",
    "reading": [
        "Cover & Thomas, *Elements of Information Theory*, 2nd ed. — chapters 2, 3, 5, 7 and 8",
        "MacKay, *Information Theory, Inference and Learning Algorithms* — chapters 1-6 and 8-10",
        "Lin & Costello, *Error Control Coding*, 2nd ed. — chapters 3 and 4",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Entropy, and where the number comes from",
            "summary": "Count the messages a source can plausibly send, and the logarithm of that count is the bill.",
            "concepts": [
                "Every log of the expected composition has the same probability, and it is exactly 2^(-nH)",
                "A set whose members each have probability at least 2^(-n(H+e)) holds at most 2^(n(H+e)) of them",
                "Entropy as the per-symbol logarithm of the count, in bits when the logarithm is base 2",
                "Joint and conditional entropy from a joint table, and the chain rule that ties them",
                "Mutual information as the symmetric overlap H(X) + H(Y) - H(X,Y)",
                "Relative entropy as the excess bits paid for coding with the wrong distribution",
                "Where the count argument stops: one string, one symbol, or a source with memory",
            ],
            "read": [
                {
                    "title": "Counting the logs a source can actually produce",
                    "minutes": 13,
                    "body": r'''
A weather station on a ridge sends one report a day down a link that charges by the bit.
The report is one of four words: `clear`, `cloud`, `rain`, `storm`. Ten years of archived
logs hold 1826 clear days, 913 cloud, 456 rain and 457 storm — near enough to $1/2$,
$1/4$, $1/8$ and $1/8$ that we will treat those fractions as the truth about the ridge.

Number the four words 00, 01, 10, 11 and a day costs two bits, so a year costs 730. The
question this module answers is whether 730 is a fact about the weather or a fact about
that numbering, and if it is the second, what number takes its place.

## Count the logs, not the symbols

Where does 730 actually come from? A year's log is a string of 365 words, there are
$4^{365}$ such strings, and the base-2 logarithm of that count is 730. Two bits a day is
the price of an index into the set of every log the station could conceivably produce.
Which means the saving, if there is one, has to come from the fact that almost none of
those logs will ever be sent.

Shrink the year to $n = 24$ days so the arithmetic stays in view. Consider a log with the
composition the frequencies predict: 12 clear, 6 cloud, 3 rain, 3 storm, in any order. Its
probability is a product of 24 factors, and because every factor is a power of two, the
product is exact:

$$P = (1/2)^{12} (1/4)^{6} (1/8)^{3} (1/8)^{3} = 2^{-12} \cdot 2^{-12} \cdot 2^{-9} \cdot 2^{-9} = 2^{-42}$$

Every log of that composition has that same probability — the factors are the same, only
their order changes. And 42 is $24 \times 1.75$, where

$$1.75 = \frac{1}{2}(1) + \frac{1}{4}(2) + \frac{1}{8}(3) + \frac{1}{8}(3)$$

is the average, over the four words, of the number of halvings it takes to reach that
word's probability. Call that average $H$. So a log of the expected composition has
probability $2^{-nH}$, and the exponent is $n$ copies of one per-symbol number.

Now run the count backwards. Probabilities add to 1. If nearly all of the probability sits
on logs that each carry about $2^{-nH}$ of it, there cannot be many more than $2^{nH}$ of
them, and there cannot be many fewer either — too few and the mass would not add up, too
many and it would overflow. Only one direction needs care, and it needs no approximation
at all: if every member of a set has probability at least $2^{-n(H + \epsilon)}$, and the
whole set has probability at most 1, then the set holds at most $2^{n(H + \epsilon)}$
members. That inequality is the entire compression argument. An index into a set of
$2^{n(H+\epsilon)}$ logs is $n(H+\epsilon)$ bits long, or $H + \epsilon$ bits a day.

Here is the count, done exactly, for a band of compositions whose surprise per day is
within 0.1 bits of 1.75. The number of arrangements of a composition is the multinomial
coefficient, and the probability of each arrangement is a power of two, so nothing is
estimated:

```python
from math import log2

COST = (1, 2, 3, 3)      # -log2 p for clear, cloud, rain, storm
H = 1.75


def band(n, width):
    """Probability mass and sequence count for logs within `width` bits/day of H."""
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i
    mass, size = 0.0, 0
    for a in range(n + 1):
        for b in range(n - a + 1):
            for c in range(n - a - b + 1):
                d = n - a - b - c
                bits = a * COST[0] + b * COST[1] + c * COST[2] + d * COST[3]
                if abs(bits / n - H) > width:
                    continue
                count = fact[n] // (fact[a] * fact[b] * fact[c] * fact[d])
                mass += count * 2.0 ** -bits
                size += count
    return mass, size


for n in (24, 96):
    mass, size = band(n, 0.1)
    print(f"n={n:3d}: the band carries {mass:.4f} of the probability and holds "
          f"2^{log2(size):.1f} of the 2^{2 * n} possible logs")
```

At 24 days the band carries 46% of the probability and holds $2^{41.5}$ of the $2^{48}$
logs. At 96 days the same width carries 76% and holds $2^{172.9}$ of $2^{192}$ — one log
in every half-million. Widen the window or lengthen the log and the mass goes to 1 while
the count stays pinned between $2^{nH}$ and $2^{n(H+\epsilon)}$. The gap between 2 bits
and 1.75 bits a day is the logarithm of the fraction of logs that never happen.

## The number, named

$$H(X) = \sum_x p_x \log_2 \frac{1}{p_x}$$

is the *entropy* of the distribution, in bits because the logarithm is base 2. It is not a
definition dropped in from outside; it is the per-symbol exponent that fell out of the
count. Run it on the ten years of archived reports rather than on the idealised fractions:

```python
from math import log2

counts = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}
n = sum(counts.values())
p = {k: v / n for k, v in counts.items()}
H = -sum(pk * log2(pk) for pk in p.values())
print(f"{n} days, H = {H:.5f} bits/day")
print(f"a year of reports: {365 * H:.1f} bits, against {365 * 2} for the two-bit numbering")
```

1.75000 bits a day, 638.7 bits a year against 730. The archive and the idealised fractions
agree to six decimal places, which is what ten years of data buys you.

## What a second variable does to the count

The station also reports whether the pass over the ridge is closed. It is never closed in
clear or cloudy weather, closed half the time it rains, and always closed in a storm. That
fixes a joint table over $X$, the report, and $Y$, the state of the pass:

```text
                open      closed
clear           0.5       0
cloud           0.25      0
rain            0.0625    0.0625
storm           0          0.125
```

Entropy of a joint table is the same sum over its cells. Conditional entropy is what is
left of $Y$ once $X$ is known: for each $x$, the entropy of the conditional distribution
$p(y | x)$, averaged with weights $p(x)$. Clear and cloudy days contribute nothing,
because the pass is certainly open; rain contributes one full bit but only $1/8$ of the
time; a storm contributes nothing, because the pass is certainly closed.

```python
from math import log2

joint = {("clear", "open"): 0.5, ("cloud", "open"): 0.25,
         ("rain", "open"): 0.0625, ("rain", "closed"): 0.0625,
         ("storm", "closed"): 0.125}


def H(dist):
    return -sum(v * log2(v) for v in dist.values() if v > 0)


px, py = {}, {}
for (x, y), v in joint.items():
    px[x] = px.get(x, 0.0) + v
    py[y] = py.get(y, 0.0) + v
print(f"H(X)   = {H(px):.4f}    H(Y)   = {H(py):.4f}")
print(f"H(X,Y) = {H(joint):.4f}")
print(f"H(Y|X) = {H(joint) - H(px):.4f}    H(X|Y) = {H(joint) - H(py):.4f}")
print(f"I(X;Y) = {H(px) + H(py) - H(joint):.4f}")
```

$H(Y) = 0.6962$ and $H(Y | X) = 0.1250$, so knowing the day's report removes 0.5712
bits of the 0.6962 that the pass carried. Go the other way and $H(X) = 1.75$ falls to
$H(X | Y) = 1.1788$ — a drop of 0.5712, the same number to every digit. It has to be:
both differences equal $H(X) + H(Y) - H(X,Y)$, which is symmetric in $X$ and $Y$ by
construction. That shared quantity is the *mutual information* $I(X;Y)$.

The chain rule falls out of the same table: $H(X,Y) = H(X) + H(Y | X)$, here
$1.875 = 1.75 + 0.125$. Send the report first and the pass costs 0.125 bits more; send the
pass first and the report costs 1.1788 more; the total is 1.875 either way.

## The mistake, and why it is tempting

The wrong formula people reach for is $I(X;Y) = H(X) - H(Y)$. It is tempting because the
correct identity $I(X;Y) = H(X) - H(X | Y)$ looks like it with the bar dropped, and
because "how much $X$ tells you about $Y$" sounds like a difference of two uncertainties.
On this table it gives $1.75 - 0.6962 = 1.0538$ bits.

That answer is refutable without knowing the right one. Mutual information cannot exceed
$H(Y)$, because it is the amount of $Y$'s uncertainty that $X$ removes and $Y$ has only
0.6962 bits of uncertainty to remove. A claim of 1.0538 says the report tells you half a
bit more about the pass than the pass contains. The second tell is asymmetry: swap the
roles and the same formula returns $-1.0538$, while information shared between two
variables cannot depend on which one you wrote first. The bar in $H(X | Y)$ is doing
real work — it is an average over a whole table, not a marginal.

A quieter version of the same error is reporting $\log_2 4 = 2$ bits as the station's
entropy. That is the entropy of the *uniform* distribution on four words, which is the
largest entropy four words can have. The gap, $2 - 1.75 = 0.25$ bits a day, is not
rounding. It is exactly the relative entropy between the true distribution and the uniform
one, and it is what a two-bit numbering overpays every single day:

```python
from math import log2

p = {"clear": 0.5, "cloud": 0.25, "rain": 0.125, "storm": 0.125}
for name, q in [("uniform", {k: 0.25 for k in p}),
                ("a fitted guess", {"clear": 0.4, "cloud": 0.3, "rain": 0.2, "storm": 0.1})]:
    D = sum(p[k] * log2(p[k] / q[k]) for k in p)
    print(f"{name:15s} D(p||q) = {D:.4f} bits  ->  {1.75 + D:.4f} bits/day")
```

Code the ridge with a model $q$ instead of the truth $p$ and you pay $H(p) + D(p \parallel q)$
bits a day. The uniform model costs 2.0000, which is the two-bit numbering recovered
exactly. A better guess costs 1.8007. $D$ is never negative, which is why no model beats
the truth, and it is not symmetric, which is why it is not a distance.

## Where the count argument stops

Entropy is a property of a distribution, never of a string. "The entropy of this file" is
shorthand for the entropy of a model somebody fitted to the file, and two models give two
answers for the same bytes. The argument above priced $n$ days together and let $n$ grow;
it says nothing about how to spend 1.75 bits on a single report, and you cannot. The next
module's Huffman code pays between $H$ and $H + 1$ bits per symbol for exactly that
reason, and the module after that recovers the fraction by refusing to code one symbol at
a time.

The count also assumed the days were independent, since the probability of a log was
written as a product. Ridge weather is not independent — a storm follows a storm more
often than chance allows — and for a source with memory the achievable rate is the entropy
*rate*, which is lower than the per-day entropy computed from the marginal. Measuring
1.75 on the archive and concluding that no scheme can beat 638.7 bits a year is an
overcharge, not a bound. Finally, the base of the logarithm is a choice of unit: natural
logarithms give nats, and $1.75$ bits is $1.2130$ nats describing the same ridge.

## What the lab asks for

The lab *Measuring a source* is these five quantities and nothing else: `entropy`,
`entropy_from_counts`, `joint_entropy`, `conditional_entropy`, `mutual_information` and
`kl_divergence`. The checks do not compare against stored decimals; they pin the
identities. The chain rule must hold on random joint tables, $I$ must come out symmetric
and non-negative, $I$ must be exactly zero on an independent table and exactly $H(X)$ when
$Y$ copies $X$, and $D(p \parallel q)$ must raise `ValueError` when $q$ gives zero probability to
something $p$ gives mass to — because that is not a large number of bits, it is an
infinite one, and returning `inf` from a compressor is how a program lies about failing.
''',
                },
            ],
            "quiz": {
                "title": "Reading a number off a distribution",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The ridge station's four reports occur with probabilities 1/2, 1/4, 1/8, 1/8. A colleague reports the source entropy as 2 bits per day. What did they compute?",
                        "opts": [
                            "The entropy of two consecutive days taken together, which is twice the per-day figure",
                            "The logarithm of the alphabet size, which equals the entropy only for a uniform source",
                            "The same entropy expressed in nats, which a change of logarithm base would rescale",
                            "The longest codeword any prefix code for four symbols can be forced to use",
                        ],
                        "a": 1,
                        "why": r"""
`log2(4) = 2` is the entropy of four *equally likely* words, and it is the largest value
the entropy of a four-word alphabet can take. The ridge is not uniform, so its entropy is
strictly smaller: 1.75 bits. The difference is not slack in the estimate — it is exactly
the relative entropy between the true distribution and the uniform one, 0.25 bits a day,
which is what a fixed two-bit numbering overpays. Any time an entropy comes out at exactly
`log2` of the alphabet size, check whether the distribution was ever consulted.
                        """,
                        "whys": [
                            r"""
Two independent days really do carry twice the entropy, but that is 3.5 bits, not 2. The
answer 2 has no factor of two in it anywhere; it is the alphabet size fed to a logarithm.
Doubling would also be the wrong repair, because the quantity asked for is a per-symbol
rate, and a rate does not change when you decide to look at symbols in pairs — that
invariance is what makes it a rate rather than a length.
                            """,
                            r"""
Right, and the diagnostic is worth keeping: `log2` of the alphabet size is an upper bound
on entropy that ignores the distribution entirely. The gap here, 0.25 bits a day, is the
relative entropy from the true distribution to the uniform one, which is another way of
saying the two-bit numbering is a code fitted to the wrong model. Every source whose
symbols are not equally likely leaves that gap on the table.
                            """,
                            r"""
Nats are a real alternative unit, but the conversion runs the other way and does not land
on 2: 1.75 bits is 1.2130 nats, and 2 nats would be 2.885 bits. A base change multiplies
by a constant, so it can never turn the ridge's distribution into a round number that
happens to equal the alphabet size. The tell is that 2 is exactly `log2(4)`, which is
about how many words there are rather than how often each is sent.
                            """,
                            r"""
The longest codeword is a fact about a particular code, not about the source, and for this
distribution an optimal code has a three-bit word for `rain` and `storm`. Entropy is an
average over the distribution, so it can sit at 1.75 while some words cost 3 and one costs
1. Confusing the maximum codeword length with the average is the same error as reading a
worst case off a table of means.
                            """,
                        ],
                    },
                    {
                        "q": "For the ridge joint table, H(X) = 1.75, H(Y) = 0.6962 and H(X,Y) = 1.875. Someone computes I(X;Y) as H(X) - H(Y) = 1.0538 bits. What is wrong with that number before you compute the right one?",
                        "opts": [
                            "It is larger than H(Y), so it claims X removes more uncertainty than Y ever had",
                            "It is larger than H(X,Y) - H(Y), so it double-counts the cells that are zero",
                            "It uses marginals where the definition of mutual information needs conditional counts",
                            "It is positive, and a difference of entropies of different alphabets has no sign",
                        ],
                        "a": 0,
                        "why": r"""
Mutual information is how much of $Y$'s uncertainty knowing $X$ removes, so it is bounded
by $H(Y)$ — and by $H(X)$, by symmetry. A value of 1.0538 against $H(Y) = 0.6962$ is
impossible on its face, which is the useful thing about the bound: it condemns the answer
without you knowing the correct one. The second tell is asymmetry. Swap the labels and
$H(Y) - H(X)$ gives $-1.0538$, and a quantity that measures what two variables share
cannot change sign when you write them in the other order. The right identity keeps the
bar: $I = H(X) - H(X | Y) = 1.75 - 1.1788 = 0.5712$.
                        """,
                        "whys": [
                            r"""
Right, and it is worth stating the bound in both directions: $I(X;Y)$ is at most
$\min(H(X), H(Y))$, so on this table nothing above 0.6962 can be an answer. That single
comparison catches the dropped-bar mistake every time, and it costs one glance at the two
marginals. The correct value, 0.5712, sits comfortably under it.
                            """,
                            r"""
$H(X,Y) - H(Y)$ is $H(X | Y) = 1.1788$, which is a real quantity but not a ceiling for
$I$, and 1.0538 sits below it rather than above — so this comparison does not fire here at
all. Zero cells are also not the problem: a cell with probability zero contributes zero to
every entropy in the identity, which is why the convention `0 log 0 = 0` is a convention
rather than a fudge.
                            """,
                            r"""
Mutual information genuinely can be written from marginals alone plus the joint entropy —
$I = H(X) + H(Y) - H(X,Y)$ uses no conditional table at all. So "it used marginals" is not
the defect; the defect is the sign on the second term and the missing joint. Adding
$H(Y)$ and subtracting $H(X,Y)$ is right, subtracting $H(Y)$ and forgetting $H(X,Y)$ is
not.
                            """,
                            r"""
A difference of two entropies does have a sign, and it is perfectly meaningful for one
marginal to be larger than another — here $X$ carries more uncertainty than $Y$ and the
difference is positive. The trouble is not the sign but the magnitude, and the fact that
the same recipe returns the negative of itself when the two variables are swapped. A
shared quantity has to survive that swap.
                            """,
                        ],
                    },
                    {
                        "q": "On the ridge table H(Y|X) = 0.125 bits, where Y is whether the pass is closed. Which reading of that number is right?",
                        "opts": [
                            "The pass is 0.125 bits from certain on every single day, whatever the report says",
                            "Each report leaves 0.125 bits about the pass, and reports repeat, so a year leaves 45.6",
                            "Averaged over reports, 0.125 bits of the pass is still unknown after the report arrives",
                            "The pass and the report disagree on 12.5% of days, which is the residual uncertainty",
                        ],
                        "a": 2,
                        "why": r"""
$H(Y | X)$ is an average, weighted by $p(x)$, of the entropy left in $Y$ once each
particular $x$ is known. On this table three of the four reports leave nothing at all —
after `clear`, `cloud` or `storm` the state of the pass is certain — and only `rain`, at
probability $1/8$, leaves a full bit. The average is $1/8 \times 1 = 0.125$. No individual
day is ever 0.125 bits uncertain; the days are 0 or 1, and 0.125 is what they come to
between them. That is why the conditional entropy of a variable can be small while
particular conditions remain wide open.
                        """,
                        "whys": [
                            r"""
No day on this table is 0.125 bits from certain. After `clear`, `cloud` or `storm` the
pass is fully determined and the residual entropy is exactly 0; after `rain` it is a coin
flip and the residual is exactly 1. Reading an average as a per-case value is the same
error as concluding from a mean household size of 2.4 that somewhere there is a household
with 0.4 of a person in it.
                            """,
                            r"""
The arithmetic is right for independent repeats — $365 \times 0.125$ is 45.6 bits — but it
answers a different question, namely what a year of pass-states costs to transmit given a
year of reports. The number asked about is a per-day rate, and calling it a yearly total
converts a rate into a length. Ridge weather also has memory, so the true yearly figure
would be below 45.6 anyway.
                            """,
                            r"""
Right, and the structure behind the average is the part worth carrying: the conditional
entropy is $\sum_x p(x) H(Y | X = x)$, so a rare condition that leaves a lot of
uncertainty and a common one that leaves none can average to a small number. Here one
report in eight leaves a whole bit and the rest leave nothing.
                            """,
                            r"""
Disagreement rate and residual entropy are different measurements, and they are not
interchangeable. A predictor that is wrong 12.5% of the time has residual entropy
$H_2(0.125) = 0.544$ bits, four times this table's figure. Entropy prices how far the
distribution is from certainty, not how often a guess would miss, and the two only line
up for a source that is already deterministic.
                            """,
                        ],
                    },
                    {
                        "q": "You compress the ridge's reports with a code fitted to q = (0.4, 0.3, 0.2, 0.1) instead of the true p = (0.5, 0.25, 0.125, 0.125). What do you pay per day, and why?",
                        "opts": [
                            "1.8465 bits — the entropy of q, since the code was built from q",
                            "1.8007 bits — the entropy of p plus the relative entropy D(p||q)",
                            "1.7500 bits — the entropy of p, since the days really are drawn from p",
                            "1.8035 bits — the entropy of p plus the relative entropy D(q||p)",
                        ],
                        "a": 1,
                        "why": r"""
A code fitted to $q$ spends about $\log_2(1/q_x)$ bits on symbol $x$, but the symbols
arrive with frequencies $p$, so the average bill is $\sum_x p_x \log_2(1/q_x)$. Split that
into $\sum_x p_x \log_2(1/p_x) + \sum_x p_x \log_2(p_x/q_x)$ and it is $H(p) + D(p \parallel q)$
— an irreducible 1.75 plus a penalty of 0.0507 for the wrong model, giving 1.8007. Both
arguments matter and in that order: the lengths come from $q$, the frequencies from $p$.
$D(q \parallel p) = 0.0536$ is a different number describing a different situation, which is the
practical face of the fact that relative entropy is not symmetric.
                        """,
                        "whys": [
                            r"""
$H(q) = 1.8465$ is what the code would cost if the source really did emit symbols with
frequencies $q$. It does not; it emits them with frequencies $p$. Averaging the codeword
lengths against the wrong frequencies is exactly the substitution the cross-entropy
formula exists to prevent, and here it happens to overshoot the true bill by 0.046 bits.
                            """,
                            r"""
Right, and the decomposition is worth remembering as a bill: $H(p)$ is what the source
costs and $D(p \parallel q)$ is what your ignorance costs on top. It also explains why $D$ is
never negative — a negative penalty would be a code that beats the entropy of the source
it codes, which the counting argument has already ruled out.
                            """,
                            r"""
1.75 is the floor, and it is reached only by a code fitted to $p$ itself. The whole point
of the question is that using $q$ costs strictly more, and the excess is a specific
computable quantity rather than a vague inefficiency. Answering with the entropy of $p$
treats the model as free, which is the assumption every practical compressor has to pay
for.
                            """,
                            r"""
$D(q \parallel p)$ is a legitimate quantity — it prices the reverse mistake, coding a $q$-source
with a $p$-fitted code — and on this pair it happens to be close, 0.0536 against 0.0507,
which is what makes the swap easy to miss. The rule that fixes the order: the distribution
the symbols actually come from is always the one the average is taken over, so it goes
first.
                            """,
                        ],
                    },
                    {
                        "q": "The counting argument fixed a composition, showed every log of that composition has probability 2^(-nH), and concluded there are about 2^(nH) plausible logs. Which step needs the days to be independent?",
                        "opts": [
                            "Multiplying the per-day probabilities to get the probability of a whole log",
                            "Counting the arrangements of a composition with the multinomial coefficient",
                            "Taking a base-2 logarithm of a count to turn it into a number of bits",
                            "Assuming the total probability of all logs of every composition is 1",
                        ],
                        "a": 0,
                        "why": r"""
$P(\text{log}) = (1/2)^{12}(1/4)^{6}(1/8)^{3}(1/8)^{3}$ is a product of per-day
probabilities, and a product is what independence buys. Drop it and the probability of a
log depends on the order of the days as well as their composition, so two logs with the
same composition no longer carry the same mass and the "every member has probability
$2^{-nH}$" step fails. The count is still about $2^{n \times \text{rate}}$, but the rate is
the entropy rate of the process, which is below the per-day entropy of the marginal. That
is why measuring 1.75 on a real weather archive gives an overcharge rather than a bound.
                        """,
                        "whys": [
                            r"""
Right, and the consequence is the useful part: with memory, logs of the same composition
stop having equal probability, so the typical set is no longer described by composition at
all. The count still grows exponentially, at a rate that is the entropy rate of the
process, and that rate is at most the marginal entropy with equality only when the days
really are independent.
                            """,
                            r"""
The multinomial coefficient counts arrangements of a fixed composition, and counting
arrangements is combinatorics that holds whatever the probabilities are — it never asks
how likely any arrangement is. Independence enters when those arrangements are assigned
probabilities, one step later. Separating the counting from the weighting is what makes
the argument portable to sources with memory.
                            """,
                            r"""
The logarithm is a unit conversion from "number of things to index" to "bits in the
index", and it is indifferent to where the count came from. It is the step that turns
$2^{nH}$ into $nH$ bits and nothing more. Blaming it would mean the same objection applied
to counting the outcomes of a fair coin, where independence is not in question.
                            """,
                            r"""
Probabilities summing to 1 over all possible logs is true of any distribution over
sequences, dependent or not — it is the definition of a distribution. In fact the argument
leans on that fact precisely because it survives dropping independence: it is what turns
"each member has probability at least $2^{-n(H+\epsilon)}$" into a hard ceiling on the
membership count.
                            """,
                        ],
                    },
                    {
                        "q": "In `kl_divergence(p, q)` the lab requires a `ValueError` when some symbol has p > 0 and q = 0. Why refuse rather than return `float('inf')`?",
                        "opts": [
                            "Because the sum has no term there, since 0 * log(1/0) is defined to be 0",
                            "Because an infinite average is a real answer here and callers should compare it",
                            "Because the true divergence is large but finite once the symbol is renormalised",
                            "Because a model that rules out an observed symbol has no codeword for it at all",
                        ],
                        "a": 3,
                        "why": r"""
$D(p \parallel q)$ prices the extra bits a $q$-fitted code spends on a $p$-source. If $q_x = 0$
the code allots symbol $x$ no codeword whatever, so when $x$ arrives — and it does, since
$p_x > 0$ — the encoder has nothing to emit. That is not an expensive outcome, it is an
impossible one, and the honest report is a raised exception naming the symbol. Returning
`inf` lets the caller keep arithmetic going: `inf` compares as larger than everything,
propagates through averages, and turns a broken model into a merely unattractive one. The
zero convention runs the other way and is fine: $p_x = 0$ contributes 0 whatever $q_x$ is,
because a symbol that never arrives is never coded.
                        """,
                        "whys": [
                            r"""
The convention $0 \log 0 = 0$ applies when $p_x$ is zero, not when $q_x$ is. Here $p_x$ is
strictly positive, so the term is $p_x \log_2(p_x / 0)$, which has a positive coefficient
in front of an undefined logarithm. Applying the zero rule to the wrong argument makes a
broken model silently score 0 on the symbol it cannot represent, which is worse than
either alternative.
                            """,
                            r"""
There is a defensible reading in which the divergence is $+\infty$, and textbooks write it
that way. The trouble is what a Python `inf` then does downstream: it survives `min`, it
poisons any mean, and it compares as merely large rather than as invalid. The lab's checks
are about the encoder, and an encoder with no codeword for an arriving symbol has a
defect, not a high score.
                            """,
                            r"""
Renormalising $q$ over the symbols it does give mass to answers a different question — the
divergence to a repaired model rather than to the one handed in. It is a reasonable repair
to offer a caller, but it must be the caller's decision, because it silently changes the
model being scored. Doing it inside `kl_divergence` would report a finite number for a
model that cannot encode the data.
                            """,
                            r"""
Right, and the encoder view settles the design question: a codeword length is
$\log_2(1/q_x)$, so $q_x = 0$ is a codeword of infinite length, which is no codeword. The
exception names the offending symbol, which is the piece of information the caller needs
to repair the model — usually by smoothing it so that nothing observed has zero mass.
                            """,
                        ],
                    },
                ],
            },
            "blanks": {
                "title": "The three entropies, in code",
                "minutes": 9,
                "caption": "measure.py — four decisions removed",
                "lang": "python",
                "brief": r"""
Every quantity in this module is the same sum with a different table fed to it. The holes
below are the four places where a sign, a guard or a marginal can go in wrong and still
return a plausible-looking number.
""",
                "listing": """import math


def entropy(dist):
    \"\"\"Shannon entropy of a distribution, in bits.\"\"\"
    total = 0.0
    for p in dist.values():
        if ___:
            continue                  # a symbol that never occurs is never coded
        total ___ p * math.log2(p)
    return total


def conditional_entropy(joint):
    \"\"\"H(Y | X) from a joint distribution keyed by (x, y).\"\"\"
    px, py = {}, {}
    for (x, y), p in joint.items():
        px[x] = px.get(x, 0.0) + p
        py[y] = py.get(y, 0.0) + p
    return entropy(joint) - ___


def mutual_information(joint):
    \"\"\"I(X; Y) = H(X) + H(Y) - H(X, Y).\"\"\"
    px, py = {}, {}
    for (x, y), p in joint.items():
        px[x] = px.get(x, 0.0) + p
        py[y] = py.get(y, 0.0) + p
    return entropy(px) + entropy(py) - ___
""",
                "blanks": [
                    {
                        "prompt": "Which guard skips the cells that contribute nothing, without skipping any that do?",
                        "hole": "?",
                        "opts": ["p <= 0", "p > 0", "p == 1", "p < 1"],
                        "a": 0,
                        "why": "A cell with zero probability contributes zero, but `math.log2(0)` raises rather than returning that zero, so the guard has to skip it. Guarding on `p <= 0` also catches the tiny negative values that arise when probabilities are computed by subtraction.",
                        "whys": [
                            "A cell with zero probability contributes zero, but `math.log2(0)` raises rather than returning that zero, so the guard has to skip it. Guarding on `p <= 0` also catches the tiny negative values that arise when probabilities are computed by subtraction.",
                            "This skips every cell that does have probability and keeps only the impossible ones, so the loop runs `math.log2` on nothing but zeros and the function raises on its first call.",
                            "A probability of 1 contributes `1 * log2(1) = 0` on its own, so skipping it changes nothing — while every zero cell still reaches the logarithm and still raises.",
                            "This keeps only the certain outcomes, discarding every genuinely uncertain cell. A fair coin would come back as 0 bits, which is the answer for a source that never surprises anyone.",
                        ],
                    },
                    {
                        "prompt": "The logarithm of a probability is negative. Which operator turns the terms into a positive number of bits?",
                        "hole": "?",
                        "opts": ["-=", "+=", "*=", "//="],
                        "a": 0,
                        "why": "Entropy is the average of `log2(1/p)`, and `log2(1/p) = -log2(p)`. Accumulating `-p*log2(p)` is that sum written without the reciprocal, and it comes out non-negative because every `log2(p)` is at most zero.",
                        "whys": [
                            "Entropy is the average of `log2(1/p)`, and `log2(1/p) = -log2(p)`. Accumulating `-p*log2(p)` is that sum written without the reciprocal, and it comes out non-negative because every `log2(p)` is at most zero.",
                            "Adding the raw terms gives the negative of the entropy: a fair coin returns -1.0 bits. Nothing else about the function is wrong, which is what makes the sign easy to leave in and hard to spot.",
                            "A running product starting from 0.0 stays 0.0 forever, so every distribution reports 0 bits. Entropy is an average of per-symbol costs, and averages are built by adding.",
                            "Floor division on a float total discards the fractional part at every step, so 1.75 bits would come back as something between -2.0 and 0.0 depending on the order of the cells.",
                        ],
                    },
                    {
                        "prompt": "Which marginal comes off the joint entropy to leave the uncertainty in Y once X is known?",
                        "hole": "?",
                        "opts": ["entropy(px)", "entropy(py)", "entropy(px) + entropy(py)", "entropy(px) - entropy(py)"],
                        "a": 0,
                        "why": "The chain rule says H(X, Y) = H(X) + H(Y | X), so subtracting H(X) is what is left. Removing the variable you are conditioning ON is the rule; the conditioned variable stays inside the joint entropy.",
                        "whys": [
                            "The chain rule says H(X, Y) = H(X) + H(Y | X), so subtracting H(X) is what is left. Removing the variable you are conditioning ON is the rule; the conditioned variable stays inside the joint entropy.",
                            "Subtracting the wrong marginal computes H(X | Y) instead — a real quantity, answering the mirror-image question. On the ridge table it returns 1.1788 where 0.1250 was wanted, and both are plausible-looking numbers.",
                            "Taking both marginals away leaves the negative of the mutual information, which is at most zero. A conditional entropy that comes out negative is the classic sign that the identity was applied twice.",
                            "A difference of marginals is not part of any of the identities here, and on an independent table it makes the conditional entropy depend on which variable happens to be larger.",
                        ],
                    },
                    {
                        "prompt": "Mutual information is the overlap of the two marginals. What is taken away to leave it?",
                        "hole": "?",
                        "opts": ["entropy(joint)", "conditional_entropy(joint)", "entropy(px)", "2 * entropy(joint)"],
                        "a": 0,
                        "why": "H(X) + H(Y) counts the shared part twice, and the joint entropy counts it once, so the difference is exactly the overlap. Writing it this way also makes the symmetry in X and Y visible on the page.",
                        "whys": [
                            "H(X) + H(Y) counts the shared part twice, and the joint entropy counts it once, so the difference is exactly the overlap. Writing it this way also makes the symmetry in X and Y visible on the page.",
                            "This mixes the two identities: I is either H(X) + H(Y) - H(X, Y) or H(Y) - H(Y | X), and taking the conditional entropy off the sum of both marginals is neither. On the ridge table it returns 2.3212 instead of 0.5712.",
                            "Subtracting H(X) leaves H(Y) alone, so every table would report the second marginal as the shared information — including an independent table, where nothing at all is shared.",
                            "Doubling the joint entropy overshoots and drives the result negative whenever the two variables are anywhere near independent, and mutual information is never negative.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Measuring a source",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
Six functions, all of them the same sum over a different table. The checks do not
compare against stored decimals; they pin the identities that connect the six.

**`entropy(dist)`** — Shannon entropy in bits. `dist` is a mapping from symbol to
probability, or a plain sequence of probabilities. A probability of exactly 0
contributes 0. Raise `ValueError` when a value is negative, when a value exceeds 1,
when the mapping is empty, or when the values miss 1 by more than `1e-9`.

```text
entropy({"H": 0.5, "T": 0.5})                       -> 1.0
entropy([0.5, 0.25, 0.125, 0.125])                  -> 1.75
entropy({"a": 1.0, "b": 0.0})                       -> 0.0
```

**`entropy_from_counts(counts)`** — the same number from a mapping of non-negative
counts, normalised internally. Zero counts are legal. Raise `ValueError` for a
negative count, an empty mapping, or a total of 0.

**`joint_entropy(joint)`** — `joint` maps a `(x, y)` pair to a probability. Same
validation as `entropy`.

**`conditional_entropy(joint)`** — `H(Y | X)`, using the chain rule
`H(X, Y) - H(X)`.

**`mutual_information(joint)`** — `I(X; Y) = H(X) + H(Y) - H(X, Y)`.

**`kl_divergence(p, q)`** — `D(p || q)` in bits, over two mappings with the same
keys. A key of `p` missing from `q` is a `ValueError`, and so is `q[k] == 0` while
`p[k] > 0`: a model that gives a symbol no probability gives it no codeword, and
that is a defect to report rather than an infinity to return. A key of `q` that `p`
does not have is fine, and contributes nothing.

```text
kl_divergence({"a": 0.5, "b": 0.5}, {"a": 0.5, "b": 0.5})   -> 0.0
kl_divergence({"a": 1.0, "b": 0.0}, {"a": 0.5, "b": 0.5})   -> 1.0
```

Do not import anything beyond `math`. The checks feed the six functions randomised
joint tables and assert the chain rule, the symmetry and non-negativity of `I`, the
exact zero on an independent table, and `I = H(X)` when `Y` copies `X`.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def entropy(dist):
    """Shannon entropy in bits, from a mapping or a sequence of probabilities."""
    # your code here


def entropy_from_counts(counts):
    """Entropy in bits from a mapping of non-negative counts."""
    # your code here


def joint_entropy(joint):
    """H(X, Y) from a mapping (x, y) -> probability."""
    # your code here


def conditional_entropy(joint):
    """H(Y | X) from a joint distribution."""
    # your code here


def mutual_information(joint):
    """I(X; Y) from a joint distribution."""
    # your code here


def kl_divergence(p, q):
    """D(p || q) in bits."""
    # your code here


print(entropy({"H": 0.5, "T": 0.5}))
print(entropy_from_counts({"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}))
print(mutual_information({("a", 0): 0.5, ("b", 1): 0.5}))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def _values(dist):
    """Probabilities out of a mapping or a sequence, validated once."""
    vals = list(dist.values()) if hasattr(dist, "values") else list(dist)
    if not vals:
        raise ValueError("an empty distribution has no entropy")
    for v in vals:
        if v < 0:
            raise ValueError(f"negative probability {v!r}")
        if v > 1 + 1e-9:
            raise ValueError(f"probability {v!r} exceeds 1")
    total = math.fsum(vals)
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"probabilities sum to {total!r}, not 1")
    return vals


def entropy(dist):
    """Shannon entropy in bits, from a mapping or a sequence of probabilities."""
    total = 0.0
    for p in _values(dist):
        if p <= 0:
            continue          # a symbol that never occurs is never coded
        total -= p * math.log2(p)
    return total


def entropy_from_counts(counts):
    """Entropy in bits from a mapping of non-negative counts."""
    vals = list(counts.values()) if hasattr(counts, "values") else list(counts)
    if not vals:
        raise ValueError("an empty count table has no entropy")
    for c in vals:
        if c < 0:
            raise ValueError(f"negative count {c!r}")
    n = math.fsum(vals)
    if n <= 0:
        raise ValueError("no observations, so no distribution")
    return entropy([c / n for c in vals])


def joint_entropy(joint):
    """H(X, Y) from a mapping (x, y) -> probability."""
    return entropy(joint)


def _marginals(joint):
    px, py = {}, {}
    for key, p in joint.items():
        x, y = key
        px[x] = px.get(x, 0.0) + p
        py[y] = py.get(y, 0.0) + p
    return px, py


def conditional_entropy(joint):
    """H(Y | X) from a joint distribution."""
    px, _py = _marginals(joint)
    return joint_entropy(joint) - entropy(px)


def mutual_information(joint):
    """I(X; Y) from a joint distribution."""
    px, py = _marginals(joint)
    return entropy(px) + entropy(py) - joint_entropy(joint)


def kl_divergence(p, q):
    """D(p || q) in bits."""
    _values(p)
    _values(q)
    total = 0.0
    for k, pk in p.items():
        if pk <= 0:
            continue          # a symbol that never arrives is never coded
        if k not in q:
            raise ValueError(f"{k!r} has no probability under q")
        qk = q[k]
        if qk <= 0:
            raise ValueError(f"q gives {k!r} no probability, so no codeword either")
        total += pk * math.log2(pk / qk)
    return total


print(entropy({"H": 0.5, "T": 0.5}))
print(entropy_from_counts({"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}))
print(mutual_information({("a", 0): 0.5, ("b", 1): 0.5}))
'''}],
                "hints": [
                    "Write one validator that returns the list of probabilities and raises on everything else; the five other functions then call it through `entropy`.",
                    "`math.log2(0)` raises rather than returning `-inf`, so skip zero cells before the logarithm rather than after it.",
                    "Build both marginals in a single pass over the joint table: for each `(x, y)` key, add the probability into `px[x]` and into `py[y]`.",
                    "Sum with `math.fsum` when checking that probabilities reach 1 — a plain `sum` over sixteen cells can drift past a 1e-9 tolerance.",
                    "In `kl_divergence`, a zero in `p` is skipped and a zero in `q` is an error. Getting those two the same way round is the whole of the function's edge behaviour.",
                ],
                "tests": [
                    {"name": "entropy on hand-checkable distributions", "code": r'''
assert abs(entropy({"H": 0.5, "T": 0.5}) - 1.0) < 1e-12, \
    f"a fair coin is 1 bit, got {entropy({'H': 0.5, 'T': 0.5})!r}"
assert abs(entropy([0.125] * 8) - 3.0) < 1e-12, f"got {entropy([0.125] * 8)!r}"
assert abs(entropy([0.5, 0.25, 0.125, 0.125]) - 1.75) < 1e-12, \
    f"got {entropy([0.5, 0.25, 0.125, 0.125])!r}"
assert abs(entropy({"a": 1.0})) < 1e-12, "a certain outcome carries no information"
assert abs(entropy({"a": 1.0, "b": 0.0})) < 1e-12, \
    "a zero-probability symbol contributes nothing, it does not raise"
_h = entropy({"a": 0.9, "b": 0.1})
assert abs(_h - 0.4689955935892812) < 1e-9, f"H2(0.1) is 0.46900, got {_h!r}"
'''},
                    {"name": "entropy refuses what is not a distribution", "code": r'''
for _bad in [{}, [], {"a": -0.5, "b": 1.5}, {"a": 0.5, "b": 0.4},
             {"a": 0.6, "b": 0.6}, [1.5, -0.5]]:
    try:
        entropy(_bad)
        assert False, f"entropy({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "entropy_from_counts normalises and validates", "code": r'''
_counts = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}
_n = sum(_counts.values())
_want = entropy({k: v / _n for k, v in _counts.items()})
_got = entropy_from_counts(_counts)
assert abs(_got - _want) < 1e-12, f"got {_got!r}, expected {_want!r}"
assert abs(_got - 1.75) < 1e-3, f"ten years of ridge weather is about 1.75 bits, got {_got!r}"
assert abs(entropy_from_counts({"a": 3, "b": 1, "c": 0}) - 0.8112781244591328) < 1e-9, \
    "a zero count is legal and contributes nothing"
assert abs(entropy_from_counts({"only": 12})) < 1e-12, "one outcome, no uncertainty"
for _bad in [{}, {"a": 0, "b": 0}, {"a": 5, "b": -1}]:
    try:
        entropy_from_counts(_bad)
        assert False, f"entropy_from_counts({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "the ridge table, to four places", "code": r'''
_joint = {("clear", "open"): 0.5, ("cloud", "open"): 0.25,
          ("rain", "open"): 0.0625, ("rain", "closed"): 0.0625,
          ("storm", "closed"): 0.125}
assert abs(joint_entropy(_joint) - 1.875) < 1e-9, f"H(X,Y) is 1.875, got {joint_entropy(_joint)!r}"
assert abs(conditional_entropy(_joint) - 0.125) < 1e-9, \
    f"H(Y|X) is 0.125, got {conditional_entropy(_joint)!r}"
assert abs(mutual_information(_joint) - 0.5712122601251459) < 1e-9, \
    f"I(X;Y) is 0.57121, got {mutual_information(_joint)!r}"
'''},
                    {"name": "the chain rule holds on random tables", "code": r'''
import random as _random

_rng = _random.Random(4111)
for _trial in range(40):
    _nx, _ny = _rng.randrange(2, 6), _rng.randrange(2, 6)
    _w = {(x, y): _rng.random() for x in range(_nx) for y in range(_ny)}
    _s = sum(_w.values())
    _j = {k: v / _s for k, v in _w.items()}
    _px = {}
    for (x, y), p in _j.items():
        _px[x] = _px.get(x, 0.0) + p
    _lhs = joint_entropy(_j)
    _rhs = entropy(_px) + conditional_entropy(_j)
    assert abs(_lhs - _rhs) < 1e-9, (
        f"H(X,Y) = {_lhs!r} but H(X) + H(Y|X) = {_rhs!r} on a {_nx}x{_ny} table")
'''},
                    {"name": "mutual information is symmetric, non-negative and bounded", "code": r'''
import random as _random

_rng = _random.Random(2718)
for _trial in range(40):
    _nx, _ny = _rng.randrange(2, 6), _rng.randrange(2, 6)
    _w = {(x, y): _rng.random() ** 3 for x in range(_nx) for y in range(_ny)}
    _s = sum(_w.values())
    _j = {k: v / _s for k, v in _w.items()}
    _flip = {(y, x): p for (x, y), p in _j.items()}
    _i = mutual_information(_j)
    assert _i > -1e-9, f"I came out negative ({_i!r}) on a {_nx}x{_ny} table"
    assert abs(_i - mutual_information(_flip)) < 1e-9, \
        f"I is symmetric, but the table gave {_i!r} and its transpose {mutual_information(_flip)!r}"
    _px, _py = {}, {}
    for (x, y), p in _j.items():
        _px[x] = _px.get(x, 0.0) + p
        _py[y] = _py.get(y, 0.0) + p
    assert _i <= min(entropy(_px), entropy(_py)) + 1e-9, \
        f"I = {_i!r} exceeds min(H(X), H(Y)) = {min(entropy(_px), entropy(_py))!r}"
'''},
                    {"name": "independence gives zero, a copy gives H(X)", "code": r'''
_px = {"a": 0.5, "b": 0.25, "c": 0.25}
_py = {0: 0.2, 1: 0.8}
_indep = {(x, y): _px[x] * _py[y] for x in _px for y in _py}
assert abs(mutual_information(_indep)) < 1e-9, \
    f"independent variables share nothing, got {mutual_information(_indep)!r}"
assert abs(conditional_entropy(_indep) - entropy(_py)) < 1e-9, \
    "conditioning on an independent variable removes nothing"
_copy = {(x, x): p for x, p in _px.items()}
assert abs(mutual_information(_copy) - entropy(_px)) < 1e-9, \
    f"a perfect copy shares all of H(X) = {entropy(_px)!r}, got {mutual_information(_copy)!r}"
assert abs(conditional_entropy(_copy)) < 1e-9, "nothing is left of Y once X is known"
'''},
                    {"name": "kl_divergence prices the wrong model", "code": r'''
_p = {"clear": 0.5, "cloud": 0.25, "rain": 0.125, "storm": 0.125}
_u = {k: 0.25 for k in _p}
assert abs(kl_divergence(_p, _p)) < 1e-12, "a model is never wrong about itself"
assert abs(kl_divergence(_p, _u) - 0.25) < 1e-9, \
    f"D(p||uniform) is exactly 0.25 bits here, got {kl_divergence(_p, _u)!r}"
assert abs(kl_divergence(_u, _p) - 0.25) < 1e-9, \
    f"this pair happens to be symmetric, got {kl_divergence(_u, _p)!r}"
_q = {"clear": 0.4, "cloud": 0.3, "rain": 0.2, "storm": 0.1}
assert abs(kl_divergence(_p, _q) - 0.05068746970707331) < 1e-9, f"got {kl_divergence(_p, _q)!r}"
assert abs(kl_divergence(_q, _p) - 0.05356065532898454) < 1e-9, \
    "D is not symmetric in general, and this pair shows it"
assert abs(kl_divergence({"a": 1.0, "b": 0.0}, {"a": 0.5, "b": 0.5}) - 1.0) < 1e-9, \
    "a zero in p contributes nothing at all"
'''},
                    {"name": "kl_divergence refuses a model with no codeword", "code": r'''
for _p, _q in [({"a": 0.5, "b": 0.5}, {"a": 1.0, "b": 0.0}),
               ({"a": 0.5, "b": 0.5}, {"a": 1.0}),
               ({"a": 0.5, "b": 0.5}, {"a": 0.5, "b": 0.4})]:
    try:
        kl_divergence(_p, _q)
        assert False, f"kl_divergence({_p!r}, {_q!r}) should raise ValueError"
    except ValueError:
        pass
_ok = kl_divergence({"a": 0.5, "b": 0.5}, {"a": 0.25, "b": 0.25, "c": 0.5})
assert abs(_ok - 1.0) < 1e-9, f"an extra symbol in q is legal and costs nothing, got {_ok!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Source coding: prefix codes and the Huffman tree",
            "summary": "A binary tree has a fixed number of leaves, and that alone fixes how short a code can be.",
            "concepts": [
                "A prefix-free codeword of length l blocks 2^(L-l) of the 2^L leaves at depth L",
                "Kraft's inequality as a leaf count, and equality as the sign that no leaf is wasted",
                "The canonical code: consecutive integers handed out shortest-first, so lengths alone define the code",
                "L = H + D(p||q) - log2 K, which gives the lower bound H and names both sources of slack",
                "The Shannon code ceil(log2 1/p) proves L < H + 1 without being optimal",
                "Huffman's greedy merge, and the exchange argument that discharges it",
                "Where a symbol code fails: one bit minimum per symbol, and blocking as the expensive repair",
            ],
            "read": [
                {
                    "title": "The tree has only so many leaves",
                    "minutes": 14,
                    "body": r'''
The ridge station has to put its four reports on a wire as bits. Give `clear` the codeword
`0`, `cloud` `10`, `rain` `110` and `storm` `111`, and five days of weather become

```text
clear clear cloud clear rain   ->   0 0 10 0 110   ->   00100110
```

Eight bits for five reports, 1.6 a day, and no separators anywhere in the stream. A
decoder reads left to right and commits the moment it recognises a codeword, because no
codeword is the beginning of another one. That property has a name — the code is
*prefix-free* — and it is the whole reason the stream needs no punctuation.

Now try to do better. The four words could take `0`, `1`, `10`, `11`, which averages
$0.5(1) + 0.25(1) + 0.125(2) + 0.125(2) = 1.25$ bits a day. Then send `cloud` followed by
`clear`: the wire carries `10`, and the decoder reads `rain`. The saving was not a saving,
it was an ambiguity. Something is stopping short codes from being handed out freely, and
the next section is a count of exactly how much.

## Codewords are leaves you have spent

Draw the binary tree of all bit strings of length $L$, where $L$ is the longest codeword
you intend to use. It has $2^L$ leaves. A codeword of length $l$ names an internal node at
depth $l$, and choosing it costs you every leaf beneath that node — because any string
extending it would have your codeword as a prefix, and prefix-freeness forbids that. The
number of leaves beneath a node at depth $l$ is $2^{L-l}$.

Prefix-freeness means those blocked sets never overlap: if two of them shared a leaf, one
codeword would sit above the other. So the blocked leaves add up, and they cannot exceed
the leaves that exist:

$$\sum_i 2^{L - l_i} \le 2^L \qquad \text{so} \qquad \sum_i 2^{-l_i} \le 1$$

That is Kraft's inequality, and it is a count of a finite tree rather than a theorem
imported from elsewhere. Check it against the two candidate codes. Lengths $1, 2, 3, 3$
give $1/2 + 1/4 + 1/8 + 1/8 = 1$ exactly — every leaf spent, nothing wasted. Lengths
$1, 1, 2, 2$ give $1/2 + 1/2 + 1/4 + 1/4 = 1.5$, which asks a tree with four leaves for
six of them. The ambiguity was arithmetic all along.

The converse holds too, and it is constructive. Given any lengths satisfying Kraft, sort
the symbols by length, hand the first one the all-zeros word of its length, and from then
on add one to the previous value and shift left by the increase in length. Nothing can be
a prefix of anything later, because every later value is numerically larger *after* being
shifted past it:

```python
def canonical_code(lengths):
    """Consecutive binary values, handed out shortest first."""
    code, value, prev = {}, 0, None
    for sym, length in sorted(lengths.items(), key=lambda kv: (kv[1], kv[0])):
        if prev is not None:
            value = (value + 1) << (length - prev)
        code[sym] = format(value, "0%db" % length)
        prev = length
    return code


ridge = {"clear": 1, "cloud": 2, "rain": 3, "storm": 3}
code = canonical_code(ridge)
print(code)
print("kraft:", sum(2.0 ** -l for l in ridge.values()))
```

The trace is worth following by hand: `clear` takes value 0 at length 1, so `0`. Then
$(0 + 1) \ll 1 = 2$ at length 2, so `10`. Then $(2 + 1) \ll 1 = 6$ at length 3, so `110`.
Then $6 + 1 = 7$, so `111`. This is the *canonical* code, and it has a practical
consequence a file format cares about: the decoder can rebuild every codeword from the
lengths alone, so a compressed file stores a list of small integers rather than a table of
bit strings.

## Which lengths, and how short can they get

The bill is $L = \sum_i p_i l_i$, and Kraft is the only constraint. The lower bound comes
out of module 1's relative entropy with no new machinery. Write $K = \sum_i 2^{-l_i} \le 1$
and define $q_i = 2^{-l_i} / K$, which is a probability distribution because it sums to 1
by construction. Then $l_i = \log_2(1/q_i) - \log_2 K$, and averaging over $p$:

$$L = \sum_i p_i \log_2 \frac{1}{q_i} - \log_2 K = H(p) + D(p \parallel q) - \log_2 K$$

Both correction terms are non-negative — $D$ because relative entropy always is, and
$-\log_2 K$ because $K \le 1$ — so $L \ge H(p)$, with equality only when the code wastes
no leaf ($K = 1$) and the lengths match the distribution exactly ($q = p$, meaning
$l_i = \log_2(1/p_i)$ for every $i$). The ridge distribution is made of powers of two, so
those logarithms are the integers 1, 2, 3, 3 and the code above hits $L = H = 1.75$ dead
on. That is not typical; it is what a dyadic distribution buys.

For the upper bound, round up: $l_i = \text{ceil}(\log_2(1/p_i))$. Kraft holds because
$2^{-\text{ceil}(x)} \le 2^{-x}$, so the sum is at most $\sum_i p_i = 1$. And each length
is under $\log_2(1/p_i) + 1$, so $L < H + 1$. That construction is the *Shannon code*, and
it proves the bound is reachable to within one bit per symbol. It is not, however, the
best code.

## The greedy merge, and what it costs to believe the rounded lengths

Take $p = (0.6, 0.2, 0.1, 0.1)$, where $H = 1.5710$. The Shannon lengths are
$\text{ceil}(0.737) = 1$, $\text{ceil}(2.322) = 3$, $\text{ceil}(3.322) = 4$ and 4,
giving $L = 2.0$ and a Kraft sum of 0.75 — a quarter of the tree unspent, which is a code
with a shortenable word in it.

Huffman's rule instead builds the tree from the bottom: repeatedly take the two least
likely items and make them siblings, replacing them by one item of the combined weight.

```python
import heapq


def huffman_lengths(weights):
    """Codeword lengths for an optimal prefix code, with the merges traced."""
    syms = list(weights)
    if len(syms) == 1:
        return {syms[0]: 1}
    heap = [(weights[s], i, [s]) for i, s in enumerate(syms)]
    heapq.heapify(heap)
    order, depth = len(syms), {s: 0 for s in syms}
    while len(heap) > 1:
        w1, _, g1 = heapq.heappop(heap)
        w2, _, g2 = heapq.heappop(heap)
        print(f"merge {w1:.2f} {g1} with {w2:.2f} {g2}")
        for s in g1 + g2:
            depth[s] += 1
        heapq.heappush(heap, (w1 + w2, order, g1 + g2))
        order += 1
    return depth


p = {"a": 0.6, "b": 0.2, "c": 0.1, "d": 0.1}
lengths = huffman_lengths(p)
print(lengths)
print("L =", sum(p[s] * lengths[s] for s in p))
```

The merges are $0.1 + 0.1 \to 0.2$, then $0.2 + 0.2 \to 0.4$, then $0.4 + 0.6 \to 1.0$,
and the depths come out $1, 2, 3, 3$ for an expected length of 1.6 bits. Against the
entropy floor of 1.5710 that is an overhead of 0.029 bits a symbol. The Shannon code's
2.0 is an overhead of 0.43 — fifteen times worse, on the same source.

Greedy rules owe a proof, and this one pays it with an exchange argument. In any optimal
tree the two least likely symbols can be assumed to be siblings at maximum depth: if the
deepest pair were some other two symbols, swapping them with the least likely two cannot
increase the expected length, because you are moving smaller probabilities onto longer
words. Once they are siblings, replacing the pair by a single symbol of their combined
weight gives a strictly smaller problem whose optimal cost differs from the original by
exactly that combined weight — so an optimal solution to the smaller problem extends to an
optimal solution of the larger one.

The mistake this module exists to head off is assuming Huffman *produces* the rounded
lengths $\text{ceil}(\log_2(1/p_i))$. It is tempting because those lengths are what the
bound was proved with, and because $\log_2(1/p)$ is the number every derivation quotes. On
the distribution above the two disagree on three of the four symbols and the gap is 0.4
bits per symbol — a quarter of the file. The diagnostic is the Kraft sum: an optimal
binary prefix code always spends every leaf, so its Kraft sum is exactly 1. The Shannon
code came in at 0.75, and slack in Kraft means a codeword that could have been shorter.

## Where a symbol code runs out

Huffman is optimal, but only among codes that assign each symbol a whole number of bits.
That restriction is invisible until the alphabet is small and the distribution is lopsided.
Take a binary source that sends `0` with probability 0.99. Its entropy is 0.0808 bits per
symbol, and no symbol code can spend fewer than one bit on a symbol:

```python
import heapq
import itertools
import math


def huffman_lengths(weights):
    syms = list(weights)
    if len(syms) == 1:
        return {syms[0]: 1}
    heap = [(weights[s], i, [s]) for i, s in enumerate(syms)]
    heapq.heapify(heap)
    order, depth = len(syms), {s: 0 for s in syms}
    while len(heap) > 1:
        w1, _, g1 = heapq.heappop(heap)
        w2, _, g2 = heapq.heappop(heap)
        for s in g1 + g2:
            depth[s] += 1
        heapq.heappush(heap, (w1 + w2, order, g1 + g2))
        order += 1
    return depth


q = 0.99
h2 = -(q * math.log2(q) + (1 - q) * math.log2(1 - q))
print(f"entropy {h2:.5f} bits/symbol")
for n in (1, 2, 4, 8):
    blocks = {}
    for tup in itertools.product("01", repeat=n):
        pr = 1.0
        for ch in tup:
            pr *= q if ch == "0" else 1 - q
        blocks["".join(tup)] = pr
    lens = huffman_lengths(blocks)
    total = sum(blocks[k] * lens[k] for k in blocks)
    print(f"blocks of {n}: {total / n:.5f} bits/symbol, {2 ** n} codewords")
```

One bit per symbol against a floor of 0.0808 is an overcharge of a factor of 12.4. Coding
pairs of symbols halves it to 0.515, fours reach 0.273, eights reach 0.157 — the $+1$ of
the bound is now amortised over eight symbols, so the overhead falls like $1/n$. The price
is a codebook of $2^n$ entries, doubling every time you take one more symbol. The next
module refuses the whole framing: it stops assigning bits to symbols and spends a
fractional number of bits on each one.

Two more limits worth stating plainly. Huffman needs the distribution before it can build
anything, so a real encoder either makes two passes over the data or transmits its
codebook; and a codebook built from the wrong counts costs $H + D(p \parallel q)$, which is
module 1's relative entropy showing up as a file size. The bound $L < H + 1$ is also
per-symbol, so a message of ten symbols can overshoot by ten bits while a message of ten
million overshoots by ten million — the guarantee is a rate, not a total.

## What the lab asks for

The lab *An optimal prefix code* wants `kraft_sum`, `is_prefix_free`, `huffman_lengths`,
`canonical_code`, `encode`, `decode` and `expected_length`. Two of the checks are the
arguments above turned into assertions. One enumerates every length vector an alphabet of
up to five symbols could have, keeps the ones Kraft allows, and asserts that your Huffman
lengths achieve the smallest expected length in that set — an exhaustive optimality proof
on small cases, which is the honest way to check a greedy rule. Another asserts your Kraft
sum is exactly 1 on every random count table it can build, because slack there is a
shortenable codeword and no other check would notice.
''',
                },
            ],
            "quiz": {
                "title": "Lengths, trees and the bound",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A code has codeword lengths 1, 2, 2, 3. What does the Kraft sum tell you about it?",
                        "opts": [
                            "It sums to 1.125, so no prefix-free code has these lengths at all",
                            "It sums to 1.125, so the code is prefix-free but wastes an eighth of the tree",
                            "It sums to 0.875, so the code is prefix-free with one leaf left unspent",
                            "It sums to 0.875, so at least one of the four codewords can be shortened by two bits",
                        ],
                        "a": 0,
                        "why": r"""
$1/2 + 1/4 + 1/4 + 1/8 = 1.125$. A codeword of length $l$ blocks $2^{-l}$ of the tree, the
blocked shares are disjoint when the code is prefix-free, and shares of a whole cannot add
to more than 1. So these lengths cannot be realised by any prefix-free code, whatever
codewords you try — the count is over budget before a single bit is assigned. The repair
is to lengthen one of the two-bit words to three bits, which brings the sum to exactly 1.
                        """,
                        "whys": [
                            r"""
Right, and the useful reading of the number is as a budget: each codeword spends
$2^{-l}$ of a unit tree, and 1.125 asks for more tree than exists. Kraft is checkable
before you have any codewords in hand, which makes it the first thing to compute when a
proposed length assignment looks too good.
                            """,
                            r"""
A sum above 1 is not waste, it is impossibility — waste is a sum *below* 1, where leaves
are left unspent. Getting the direction backwards is easy because both cases are "not
equal to 1", but they fail in opposite ways: below 1 you can shorten a codeword, above 1
you must lengthen one.
                            """,
                            r"""
The arithmetic slipped: the two length-2 words contribute $1/4$ each, not $1/8$ each. With
$1/2 + 1/4 + 1/4 + 1/8$ the total is 1.125. It is worth recomputing rather than eyeballing,
because the difference between 0.875 and 1.125 is the difference between a code that
wastes a leaf and one that cannot exist.
                            """,
                            r"""
Shortening by two bits would need a Kraft sum well under 1, and even a genuine sum of
0.875 leaves only one length-3 leaf spare — enough to shorten one three-bit word to two
bits, not to save two bits anywhere. The slack in Kraft tells you how much room there is,
and reading it as more than it is leads to codes that fail the prefix test.
                            """,
                        ],
                    },
                    {
                        "q": "For p = (0.6, 0.2, 0.1, 0.1) the entropy is 1.5710 bits. Huffman gives lengths 1, 2, 3, 3 for L = 1.6, while ceil(log2(1/p)) gives 1, 3, 4, 4 for L = 2.0. Why does the rounded rule lose?",
                        "opts": [
                            "It rounds each length independently, leaving a Kraft sum of 0.75 and a quarter of the tree unspent",
                            "It rounds each length independently, which breaks Kraft and makes the resulting code ambiguous",
                            "It uses the entropy of the wrong distribution, so its lengths price a source that is not this one",
                            "It is correct but measured wrongly, since the two codes must have equal expected length",
                        ],
                        "a": 0,
                        "why": r"""
Rounding up per symbol is safe — it can only satisfy Kraft — but it is safe by leaving room
on the table. Here the sum is $1/2 + 1/8 + 1/16 + 1/16 = 0.75$, so a quarter of the tree is
never spent, and unspent tree is exactly the resource a shorter codeword would have used.
Huffman spends all of it: its Kraft sum is 1, which is the structural reason it can be no
worse. The rounded lengths do prove the bound $L < H + 1$, which is what they were invented
for; they are a proof device, not an optimal code.
                        """,
                        "whys": [
                            r"""
Right, and Kraft equality is the fastest audit of a code you have been handed. Any binary
prefix code whose Kraft sum is under 1 has a codeword that could lose a bit without
colliding with anything, so an optimal code always sums to exactly 1. Seeing 0.75 is enough
to know a shorter code exists before you find it.
                            """,
                            r"""
Rounding up never breaks Kraft — that is the point of rounding *up* rather than to nearest.
Because $2^{-\text{ceil}(x)} \le 2^{-x}$, the sum is at most $\sum_i p_i = 1$, so the code
is always decodable. Its defect is the opposite of ambiguity: it is unambiguous with room
to spare.
                            """,
                            r"""
Both length assignments are computed from the same $p$, so no wrong distribution is
involved. What differs is how the real-valued ideal $\log_2(1/p_i)$ is turned into
integers: independently per symbol, or jointly by a tree that lets one symbol's rounding
pay for another's. That joint choice is the whole of Huffman's advantage.
                            """,
                            r"""
The expected lengths are genuinely different — 1.6 against 2.0 on the same distribution —
and both are computed the same way, as $\sum_i p_i l_i$. Two codes with different length
vectors have no reason to cost the same, and the gap here, 0.4 bits per symbol, is a
quarter of the file.
                            """,
                        ],
                    },
                    {
                        "q": "A binary source emits `0` with probability 0.99, so its entropy is 0.0808 bits per symbol. What does the best Huffman code on single symbols achieve, and why?",
                        "opts": [
                            "0.0808 bits per symbol, since Huffman is optimal and optimal codes reach the entropy",
                            "0.0808 bits per symbol on average, though individual codewords are one bit long",
                            "1 bit per symbol, because a two-symbol alphabet forces a codeword of length 1 on each",
                            "0.5 bits per symbol, because one codeword is empty and the other is a single bit",
                        ],
                        "a": 2,
                        "why": r"""
With two symbols there is exactly one prefix-free code up to relabelling: `0` and `1`. Both
codewords are one bit, so the average is one bit whatever the probabilities are, and the
coder overcharges by a factor of 12.4. Huffman being optimal does not rescue it, because
optimal here means optimal among symbol codes, and every symbol code spends at least one
bit per symbol. The repair inside this framework is to code blocks: pairs get to 0.515 bits
per symbol, blocks of eight to 0.157, at the price of a codebook of $2^n$ entries. The
repair outside it is the next module.
                        """,
                        "whys": [
                            r"""
Optimality is relative to a class of codes, and Huffman's class is codes that assign each
symbol a whole number of bits. Within that class it cannot be beaten; the class itself
cannot reach 0.0808 for a two-symbol alphabet. Conflating "best in its class" with "reaches
the bound" is the error the whole of the next module is built around.
                            """,
                            r"""
An average of one-bit codewords is one bit — there is nothing for the averaging to do when
every codeword has the same length. The averaging only buys something when the lengths
differ, which needs at least three symbols or a blocked alphabet. Here both codewords are
length 1, so the expected length is 1 regardless of how lopsided the source is.
                            """,
                            r"""
Right, and the arithmetic of the repair is worth carrying: blocking $n$ symbols amortises
the at-most-one-bit overhead over $n$ symbols, so the excess falls like $1/n$ while the
codebook grows like $2^n$. That trade is why a symbol coder on a very skewed source is
usually replaced rather than blocked.
                            """,
                            r"""
An empty codeword cannot be part of a prefix-free code with more than one symbol, because
the empty string is a prefix of everything — the decoder would commit to that symbol before
reading a bit. Kraft says so too: a length of 0 contributes $2^0 = 1$ on its own, which
leaves nothing for the second symbol.
                            """,
                        ],
                    },
                    {
                        "q": "Why can a compressed file store only the codeword *lengths* and still let the decoder rebuild the code?",
                        "opts": [
                            "Because Huffman's merge order can be recovered from the lengths, which replays the same tree",
                            "Because the canonical rule fixes every codeword from the lengths alone",
                            "Because any two prefix-free codes with the same lengths decode a stream identically",
                            "Because the decoder only ever needs lengths, and reads the symbols off the stream positionally",
                        ],
                        "a": 1,
                        "why": r"""
The canonical construction is deterministic given the lengths and an agreed order on the
symbols: start at zero, and each time you move to the next symbol add one and shift left by
the increase in length. Encoder and decoder run the same rule and land on the same table.
The merge order that Huffman happened to use is not recoverable and does not need to be —
the lengths are what matter, and any prefix code with those lengths is equally short. This
is why `canonical_code` in the lab takes lengths rather than a tree.
                        """,
                        "whys": [
                            r"""
Merge order is not recoverable from lengths, and ties in the weights mean several merge
orders give the same length vector anyway. That is not a problem to solve, because the
lengths already determine the cost; what the format needs is a deterministic rule for
turning lengths into bit strings, which is a different thing from replaying the tree.
                            """,
                            r"""
Right, and the practical payoff is the format: a canonical Huffman header is a list of
small integers, one per symbol, rather than a table of variable-length bit strings. Deflate
and JPEG both store exactly that, and both rely on encoder and decoder running the same
assignment rule.
                            """,
                            r"""
Two prefix codes with the same lengths cost the same but decode a given stream to different
symbols — swap the codewords `10` and `110` between two symbols and every message changes
meaning while the file size stays identical. Equal length vectors guarantee equal
compression, not agreement on what the bits say, which is precisely why the assignment rule
has to be pinned down.
                            """,
                            r"""
There is no positional structure to read: the stream is a run of concatenated codewords of
different lengths with no separators, so a decoder that does not know which bit pattern
means which symbol cannot even find the boundaries. Knowing the lengths matters because
they generate the codewords, not because they can be applied to the stream directly.
                            """,
                        ],
                    },
                    {
                        "q": "Huffman merges the two least likely items at each step. What does the exchange argument have to establish for that rule to be justified?",
                        "opts": [
                            "That merging the two least likely items never increases the Kraft sum of the result",
                            "That the two least likely symbols are deepest siblings in some optimal tree",
                            "That every optimal code assigns the least likely symbol the longest codeword available",
                            "That the greedy choice at each step is the one that most reduces the remaining entropy",
                        ],
                        "a": 1,
                        "why": r"""
The obligation a greedy rule carries is that its first choice is consistent with *some*
optimal solution. Here that claim is: there is an optimal tree in which the two least likely
symbols are siblings at the deepest level. The proof is a swap — if some other pair is
deepest, exchanging them with the two least likely cannot increase $\sum_i p_i l_i$, because
smaller probabilities are being moved onto the longer codewords. Once they are siblings,
replacing the pair by one symbol of the combined weight is a strictly smaller instance whose
cost differs by a constant, so induction finishes it.
                        """,
                        "whys": [
                            r"""
Kraft is satisfied automatically by any tree built this way — every merge produces a proper
binary tree, and a binary tree with every internal node full has Kraft sum exactly 1. So
this is true but empty: it holds for many merge rules, including ones that produce
needlessly long codes, and it says nothing about optimality.
                            """,
                            r"""
Right, and the shape of the claim matters as much as its content: not "every optimal tree
does this" but "some optimal tree does". Several optimal trees exist whenever weights tie,
and the greedy rule only needs one of them to agree with its first move for the induction
to go through.
                            """,
                            r"""
Not every optimal code does this — with ties the least likely symbol can sit at the same
depth as several others, and which of them is called longest is arbitrary. Claiming it of
every optimal code is a stronger statement than the argument needs and than the facts
support, and it is exactly the over-claim that makes greedy proofs fail.
                            """,
                            r"""
"Reduces the remaining entropy the most" is a plausible-sounding greedy criterion but it is
not the rule Huffman uses, and merging two items does not reduce entropy in any direct
sense — it changes the alphabet. The rule is about weights and depths, and its
justification is about trees, not about the entropy of intermediate stages.
                            """,
                        ],
                    },
                    {
                        "q": "You build a Huffman code from counts q taken from last month's data, then compress this month's data, which is distributed as p. What do you pay per symbol?",
                        "opts": [
                            "Between H(q) and H(q) + 1, since the code was built from q and codes are priced by their own model",
                            "Between H(p) and H(p) + 1, since Huffman is optimal and this month's symbols are drawn from p",
                            "Between H(p) + D(p||q) and one bit above it, since the lengths come from q",
                            "Exactly H(p) + D(q||p), since the codebook is the stale object and D measures how stale it is",
                        ],
                        "a": 2,
                        "why": r"""
The lengths are roughly $\log_2(1/q_x)$ because the tree was built from $q$, and the symbols
arrive with frequencies $p$, so the average is the cross-entropy
$\sum_x p_x \log_2(1/q_x) = H(p) + D(p \parallel q)$ — module 1's result, reappearing as a
file size. The integer rounding then adds the usual at-most-one bit. The order of the
arguments is fixed by which distribution the average is taken over, and that is always the
one the data actually comes from.
                        """,
                        "whys": [
                            r"""
$H(q)$ is what the code would cost if this month's data really were distributed as $q$. It
is not, and averaging $q$-derived lengths against $q$ instead of $p$ is the substitution the
cross-entropy exists to prevent. It can err in either direction, so it is not even a safe
over-estimate.
                            """,
                            r"""
Huffman is optimal for the distribution it was built from, and it was built from $q$. Give
it the wrong counts and it is an ordinary prefix code with no optimality claim at all. The
bound $H(p) \le L < H(p) + 1$ belongs to the code built from $p$; this one pays the
divergence on top.
                            """,
                            r"""
Right, and the practical consequence is why real compressors either make two passes or
adapt as they go: the penalty $D(p \parallel q)$ is paid on every symbol, so a stale model
is a per-byte tax rather than a fixed header cost. Measuring it is the cheapest way to
decide whether rebuilding the table is worth the pass.
                            """,
                            r"""
The arguments are the wrong way round, and the "exactly" is wrong too — integer codeword
lengths add up to one more bit per symbol on top of whatever the cross-entropy is. Both
divergences are computable and here they measure different situations: $D(p \parallel q)$
is what this month's data pays for last month's table, $D(q \parallel p)$ the reverse.
                            """,
                        ],
                    },
                ],
            },
            "blanks": {
                "title": "Huffman, merge by merge",
                "minutes": 9,
                "caption": "prefix.py — four decisions removed",
                "lang": "python",
                "brief": r"""
The merge loop is six lines and every one of them can be wrong in a way that still returns
a plausible set of lengths. Fill the holes, then check the last line: an optimal binary
prefix code always spends every leaf in the tree.
""",
                "listing": """import heapq


def huffman_lengths(weights):
    \"\"\"Codeword lengths for an optimal prefix code.\"\"\"
    syms = list(weights)
    if len(syms) == 1:
        return {syms[0]: 1}                # one symbol still needs one bit
    heap = [(weights[s], i, [s]) for i, s in enumerate(syms)]
    heapq.heapify(heap)
    order, depth = len(syms), {s: 0 for s in syms}
    while len(heap) > 1:
        w1, _, g1 = heapq.heappop(heap)
        w2, _, g2 = heapq.heappop(heap)
        for s in ___:                      # everything below the new node sinks one level
            depth[s] += 1
        heapq.heappush(heap, (___, order, g1 + g2))
        order += 1
    return depth


def canonical_code(lengths):
    \"\"\"Consecutive binary values, handed out shortest first.\"\"\"
    items = sorted(lengths.items(), key=lambda kv: (___, kv[0]))
    code, value, prev = {}, 0, None
    for sym, length in items:
        if prev is not None:
            value = (value + 1) ___ (length - prev)
        code[sym] = format(value, "0%db" % length)
        prev = length
    return code


# an optimal code wastes no leaf:  sum of 2**-length over all symbols == 1
""",
                "blanks": [
                    {
                        "prompt": "Making two nodes siblings pushes a subtree down. Whose depth increases?",
                        "hole": "?",
                        "opts": ["g1 + g2", "g1", "g2", "syms"],
                        "a": 0,
                        "why": "The merge creates one new parent above both groups, so every symbol under either of them gains a level. Counting depth this way avoids building an explicit tree at all: the length of a codeword is the number of merges its symbol took part in.",
                        "whys": [
                            "The merge creates one new parent above both groups, so every symbol under either of them gains a level. Counting depth this way avoids building an explicit tree at all: the length of a codeword is the number of merges its symbol took part in.",
                            "Sinking only the first group makes the tree lopsided in a way no tree actually is: the second group would end up with codewords shorter than their position allows, and the Kraft sum would climb above 1.",
                            "Sinking only the second group has the mirror defect, and it is harder to notice because the heap tends to hand back the lighter group second, so the symbols that lose depth are the rare ones.",
                            "Every symbol in the alphabet would gain a level on every merge, so all the lengths would come out equal to the number of merges. That is a fixed-length code with a very long word.",
                        ],
                    },
                    {
                        "prompt": "The merged node stands in for both groups from now on. What weight does it carry?",
                        "hole": "?",
                        "opts": ["w1 + w2", "max(w1, w2)", "min(w1, w2)", "w1 * w2"],
                        "a": 0,
                        "why": "The new node is reached whenever either group's symbol is sent, so its probability is the sum. That is what makes the reduced problem an honest smaller instance of the same problem, which is the step the induction in the exchange argument needs.",
                        "whys": [
                            "The new node is reached whenever either group's symbol is sent, so its probability is the sum. That is what makes the reduced problem an honest smaller instance of the same problem, which is the step the induction in the exchange argument needs.",
                            "Keeping the larger weight understates how often the merged node is used, so it stays near the bottom of the heap for too long and its symbols end up with codewords longer than optimal.",
                            "Keeping the smaller weight understates it further, and on a distribution like 0.4, 0.3, 0.2, 0.1 it produces a lopsided chain where the second-commonest symbol gets three bits.",
                            "A product of two probabilities is smaller than either of them, so the merged node sinks rather than rising, and the loop builds a tree that is upside down with respect to frequency.",
                        ],
                    },
                    {
                        "prompt": "The canonical rule hands out values shortest word first. What is the primary sort key?",
                        "hole": "?",
                        "opts": ["kv[1]", "kv[0]", "-kv[1]", "len(kv)"],
                        "a": 0,
                        "why": "`kv` is a (symbol, length) pair, so `kv[1]` is the length. Sorting by length first is what makes the shift-left step legal: values only ever grow, and growing by a shift keeps every earlier codeword from being a prefix of a later one.",
                        "whys": [
                            "`kv` is a (symbol, length) pair, so `kv[1]` is the length. Sorting by length first is what makes the shift-left step legal: values only ever grow, and growing by a shift keeps every earlier codeword from being a prefix of a later one.",
                            "Sorting by symbol name first interleaves the lengths, so the code would have to shift right when a shorter word follows a longer one — and a right shift discards the low bits that were keeping the words distinct.",
                            "Reversing the length order hands out the longest words first, and the very first codeword would then be all zeros at maximum length, with every subsequent shorter word a prefix of something already issued.",
                            "Every pair has exactly two entries, so this key is the constant 2 and the sort falls back to symbol order alone — the same defect as sorting by name, arrived at by accident.",
                        ],
                    },
                    {
                        "prompt": "Moving from a shorter length to a longer one, how does the running value grow?",
                        "hole": "?",
                        "opts": ["<<", ">>", "*", "+"],
                        "a": 0,
                        "why": "A left shift by the increase in length appends that many zero bits, which is exactly the step past every extension of the previous codeword. It is what guarantees the new value is below no earlier codeword in the tree.",
                        "whys": [
                            "A left shift by the increase in length appends that many zero bits, which is exactly the step past every extension of the previous codeword. It is what guarantees the new value is below no earlier codeword in the tree.",
                            "A right shift throws away low bits and makes the value smaller, so the next codeword would collide with one already issued — and because `format` pads to the new length, the collision shows up as a duplicate prefix rather than an error.",
                            "Multiplying by the length difference is arithmetic that happens to match the shift when the difference is 1 and diverges after that, so a code whose lengths never jump by more than one would pass every quick test and break on the first that does.",
                            "Adding the length difference nudges the value by one or two when it needs to double or quadruple, so the longer codewords start inside the region already spent by the shorter ones.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "An optimal prefix code",
                "runtime": "python",
                "minutes": 70,
                "brief": r'''
Seven functions. Three are the tree count from the reading; four build and use the
code.

**`kraft_sum(lengths)`** — `sum(2**-l)`, from a mapping symbol -> length or a plain
sequence of lengths. Every term is a power of two, so the float result is exact.
Raise `ValueError` for an empty input or a length that is not an integer of at
least 1.

```text
kraft_sum([1, 2, 3, 3])  -> 1.0
kraft_sum([1, 2, 2, 3])  -> 1.125     no prefix code has these lengths
kraft_sum([2, 2, 2])     -> 0.75      a leaf is going spare
```

**`is_prefix_free(code)`** — `code` maps a symbol to a bit string. `True` when no
codeword is a prefix of another. Raise `ValueError` for an empty code or a codeword
that is not a non-empty string of `0` and `1`.

**`huffman_lengths(weights)`** — `weights` maps each symbol to a positive count or
probability. Returns a mapping from symbol to codeword length. Merge the two
lightest items repeatedly; break ties by taking the item that entered the queue
first, so the result is deterministic. A one-symbol alphabet gets length 1. Raise
`ValueError` for an empty mapping or a weight that is not strictly positive.

```text
huffman_lengths({"clear": 1826, "cloud": 913, "rain": 456, "storm": 457})
    -> {"clear": 1, "cloud": 2, "rain": 3, "storm": 3}
huffman_lengths({"a": 3, "b": 2, "c": 1})   -> {"a": 1, "b": 2, "c": 2}
```

**`canonical_code(lengths)`** — sort the symbols by `(length, symbol)`, give the
first the all-zeros word of its length, and thereafter add one and shift left by the
increase in length. Raise `ValueError` when the Kraft sum exceeds 1.

```text
canonical_code({"clear": 1, "cloud": 2, "rain": 3, "storm": 3})
    -> {"clear": "0", "cloud": "10", "rain": "110", "storm": "111"}
```

**`encode(symbols, code)`** — concatenate the codewords into one bit string.
`ValueError` for a symbol the code does not have.

**`decode(bits, code)`** — the list of symbols. `ValueError` when the code is not
prefix-free, and when the bits run out part-way through a codeword.

**`expected_length(weights, lengths)`** — the weighted average codeword length,
`sum(w * l) / sum(w)`. `ValueError` when a symbol has a weight but no length.

Standard library only, and `heapq` is the one import you need. One of the checks
enumerates every length vector for alphabets of up to five symbols and asserts your
lengths are the shortest Kraft allows; another asserts your Kraft sum is exactly 1.
''',
                "files": [{"name": "main.py", "content": r'''
import heapq


def kraft_sum(lengths):
    """sum(2**-l) over the codeword lengths."""
    # your code here


def is_prefix_free(code):
    """True when no codeword is a prefix of another."""
    # your code here


def huffman_lengths(weights):
    """Optimal codeword lengths by repeated merging of the two lightest items."""
    # your code here


def canonical_code(lengths):
    """Consecutive binary values, handed out shortest first."""
    # your code here


def encode(symbols, code):
    """The codewords, concatenated."""
    # your code here


def decode(bits, code):
    """The symbols the bit string spells out."""
    # your code here


def expected_length(weights, lengths):
    """The weighted average codeword length."""
    # your code here


ridge = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}
print(huffman_lengths(ridge))
print(canonical_code({"clear": 1, "cloud": 2, "rain": 3, "storm": 3}))
print(kraft_sum([1, 2, 3, 3]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import heapq


def _lengths_of(lengths):
    vals = list(lengths.values()) if hasattr(lengths, "values") else list(lengths)
    if not vals:
        raise ValueError("no codeword lengths given")
    for l in vals:
        if isinstance(l, bool) or not isinstance(l, int) or l < 1:
            raise ValueError(f"{l!r} is not a codeword length")
    return vals


def kraft_sum(lengths):
    """sum(2**-l) over the codeword lengths."""
    # every term is a power of two, so this float total is exact
    return sum(2.0 ** -l for l in _lengths_of(lengths))


def is_prefix_free(code):
    """True when no codeword is a prefix of another."""
    if not code:
        raise ValueError("an empty code has nothing to check")
    words = []
    for sym, w in code.items():
        if not isinstance(w, str) or not w or set(w) - {"0", "1"}:
            raise ValueError(f"codeword {w!r} for {sym!r} is not a bit string")
        words.append(w)
    words.sort()
    # after sorting, a prefix can only be immediately before the word it prefixes
    for a, b in zip(words, words[1:]):
        if b.startswith(a):
            return False
    return True


def huffman_lengths(weights):
    """Optimal codeword lengths by repeated merging of the two lightest items."""
    if not weights:
        raise ValueError("an empty alphabet has no code")
    for sym, w in weights.items():
        if w <= 0:
            raise ValueError(f"weight {w!r} for {sym!r} is not positive")
    syms = list(weights)
    if len(syms) == 1:
        return {syms[0]: 1}       # one symbol still costs one bit to send
    heap = [(weights[s], i, [s]) for i, s in enumerate(syms)]
    heapq.heapify(heap)
    order = len(syms)             # entry counter: ties go to whoever queued first
    depth = {s: 0 for s in syms}
    while len(heap) > 1:
        w1, _, g1 = heapq.heappop(heap)
        w2, _, g2 = heapq.heappop(heap)
        for s in g1 + g2:
            depth[s] += 1         # both groups sink one level under the new parent
        heapq.heappush(heap, (w1 + w2, order, g1 + g2))
        order += 1
    return depth


def canonical_code(lengths):
    """Consecutive binary values, handed out shortest first."""
    if kraft_sum(lengths) > 1 + 1e-12:
        raise ValueError("these lengths need more leaves than a binary tree has")
    code, value, prev = {}, 0, None
    for sym, length in sorted(lengths.items(), key=lambda kv: (kv[1], kv[0])):
        if prev is not None:
            value = (value + 1) << (length - prev)
        code[sym] = format(value, "0%db" % length)
        prev = length
    return code


def encode(symbols, code):
    """The codewords, concatenated."""
    out = []
    for s in symbols:
        if s not in code:
            raise ValueError(f"no codeword for {s!r}")
        out.append(code[s])
    return "".join(out)


def decode(bits, code):
    """The symbols the bit string spells out."""
    if not is_prefix_free(code):
        raise ValueError("a code that is not prefix-free cannot be decoded left to right")
    table = {w: s for s, w in code.items()}
    out, buf = [], ""
    for ch in bits:
        if ch not in "01":
            raise ValueError(f"{ch!r} is not a bit")
        buf += ch
        if buf in table:
            out.append(table[buf])
            buf = ""
    if buf:
        raise ValueError(f"the stream ends mid-codeword on {buf!r}")
    return out


def expected_length(weights, lengths):
    """The weighted average codeword length."""
    total = 0.0
    mass = 0.0
    for s, w in weights.items():
        if s not in lengths:
            raise ValueError(f"{s!r} has a weight but no codeword length")
        total += w * lengths[s]
        mass += w
    if mass <= 0:
        raise ValueError("the weights add to nothing")
    return total / mass


ridge = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}
print(huffman_lengths(ridge))
print(canonical_code({"clear": 1, "cloud": 2, "rain": 3, "storm": 3}))
print(kraft_sum([1, 2, 3, 3]))
'''}],
                "hints": [
                    "Sort the codewords as strings before testing prefix-freeness: a word can only be a prefix of the one immediately after it in sorted order, which turns a quadratic scan into a linear one.",
                    "Do not build a tree object. Keep a list of the symbols under each heap entry and add one to each of their depths at every merge; the depth is the codeword length.",
                    "Push `(weight, counter, group)` and increment the counter on every push. Without the counter, two equal weights make Python compare the groups, and the result stops being deterministic.",
                    "`format(value, \"0%db\" % length)` pads with leading zeros, which is what makes a value of 0 at length 3 come out as `000` rather than `0`.",
                    "In `decode`, accumulate bits into a buffer and look the buffer up after every bit. Prefix-freeness is what makes that first match the right one.",
                ],
                "tests": [
                    {"name": "kraft_sum and is_prefix_free on hand cases", "code": r'''
assert kraft_sum([1, 2, 3, 3]) == 1.0, f"got {kraft_sum([1, 2, 3, 3])!r}"
assert kraft_sum([1, 2, 2, 3]) == 1.125, f"got {kraft_sum([1, 2, 2, 3])!r}"
assert kraft_sum([2, 2, 2]) == 0.75, f"got {kraft_sum([2, 2, 2])!r}"
assert kraft_sum({"a": 1, "b": 1}) == 1.0, "a mapping of lengths is accepted too"
assert is_prefix_free({"a": "0", "b": "10", "c": "110", "d": "111"}) is True
assert is_prefix_free({"a": "0", "b": "01"}) is False, "`0` is a prefix of `01`"
assert is_prefix_free({"a": "00", "b": "01", "c": "10", "d": "11"}) is True
for _bad in [[], {}, [0, 1], [1, -2], [1, 1.5]]:
    try:
        kraft_sum(_bad)
        assert False, f"kraft_sum({_bad!r}) should raise ValueError"
    except ValueError:
        pass
for _bad in [{}, {"a": ""}, {"a": "012"}, {"a": 10}]:
    try:
        is_prefix_free(_bad)
        assert False, f"is_prefix_free({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "huffman_lengths on hand-checkable alphabets", "code": r'''
_ridge = huffman_lengths({"clear": 1826, "cloud": 913, "rain": 456, "storm": 457})
assert _ridge == {"clear": 1, "cloud": 2, "rain": 3, "storm": 3}, f"got {_ridge!r}"
assert huffman_lengths({"a": 3, "b": 2, "c": 1}) == {"a": 1, "b": 2, "c": 2}, \
    f"got {huffman_lengths({'a': 3, 'b': 2, 'c': 1})!r}"
assert huffman_lengths({c: 1 for c in "abcd"}) == {c: 2 for c in "abcd"}, \
    "a uniform alphabet of four gets a fixed-length code"
assert huffman_lengths({"only": 5}) == {"only": 1}, "one symbol still needs one bit"
_skew = huffman_lengths({"a": 0.6, "b": 0.2, "c": 0.1, "d": 0.1})
assert _skew == {"a": 1, "b": 2, "c": 3, "d": 3}, f"probabilities are weights too, got {_skew!r}"
_two = huffman_lengths({"a": 99, "b": 1})
assert _two == {"a": 1, "b": 1}, f"two symbols is one bit each however skewed, got {_two!r}"
'''},
                    {"name": "huffman_lengths refuses what is not an alphabet", "code": r'''
for _bad in [{}, {"a": 0}, {"a": -3, "b": 1}, {"a": 1, "b": 0}]:
    try:
        huffman_lengths(_bad)
        assert False, f"huffman_lengths({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Huffman spends every leaf: the Kraft sum is exactly 1", "code": r'''
import random as _random

_rng = _random.Random(4110)
for _trial in range(60):
    _n = _rng.randrange(2, 13)
    _w = {chr(97 + i): _rng.randrange(1, 500) for i in range(_n)}
    _len = huffman_lengths(_w)
    assert set(_len) == set(_w), f"every symbol needs a length, got {_len!r}"
    _k = kraft_sum(_len)
    assert _k == 1.0, (
        f"Kraft sum {_k!r} on {_w!r} — an optimal binary code leaves no leaf unspent")
'''},
                    {"name": "canonical_code builds the code the lengths describe", "code": r'''
_c = canonical_code({"clear": 1, "cloud": 2, "rain": 3, "storm": 3})
assert _c == {"clear": "0", "cloud": "10", "rain": "110", "storm": "111"}, f"got {_c!r}"
assert canonical_code({"a": 2, "b": 2, "c": 2, "d": 2}) == \
    {"a": "00", "b": "01", "c": "10", "d": "11"}, "equal lengths count upwards"
assert canonical_code({"z": 3, "a": 1, "m": 2}) == {"a": "0", "m": "10", "z": "110"}, \
    "shortest first, ties broken by symbol"
import random as _random

_rng = _random.Random(1729)
for _trial in range(40):
    _n = _rng.randrange(2, 10)
    _w = {chr(97 + i): _rng.randrange(1, 200) for i in range(_n)}
    _len = huffman_lengths(_w)
    _code = canonical_code(_len)
    assert is_prefix_free(_code), f"{_code!r} is not prefix-free"
    assert {s: len(w) for s, w in _code.items()} == _len, \
        f"the code {_code!r} does not have the lengths {_len!r}"
try:
    canonical_code({"a": 1, "b": 1, "c": 2})
    assert False, "a Kraft sum above 1 should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "encode and decode are inverses", "code": r'''
import random as _random

_code = canonical_code({"clear": 1, "cloud": 2, "rain": 3, "storm": 3})
assert encode(["clear", "clear", "cloud", "clear", "rain"], _code) == "00100110", \
    f"got {encode(['clear', 'clear', 'cloud', 'clear', 'rain'], _code)!r}"
assert decode("00100110", _code) == ["clear", "clear", "cloud", "clear", "rain"]
assert encode([], _code) == "" and decode("", _code) == [], "an empty message is empty"
_rng = _random.Random(31337)
for _trial in range(30):
    _n = _rng.randrange(2, 9)
    _w = {chr(97 + i): _rng.randrange(1, 100) for i in range(_n)}
    _c = canonical_code(huffman_lengths(_w))
    _msg = [_rng.choice(list(_w)) for _ in range(_rng.randrange(0, 60))]
    _bits = encode(_msg, _c)
    assert decode(_bits, _c) == _msg, f"round trip failed on {_msg!r}"
try:
    encode(["clear", "fog"], _code)
    assert False, "an unknown symbol should raise ValueError"
except ValueError:
    pass
try:
    decode("11", _code)
    assert False, "a stream that ends mid-codeword should raise ValueError"
except ValueError:
    pass
try:
    decode("0", {"a": "0", "b": "01"})
    assert False, "a code that is not prefix-free should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "the expected length lands between H and H+1", "code": r'''
import math as _math
import random as _random

_rng = _random.Random(2024)
for _trial in range(50):
    _n = _rng.randrange(2, 15)
    _w = {chr(97 + i): _rng.random() ** 2 + 1e-3 for i in range(_n)}
    _tot = sum(_w.values())
    _p = {k: v / _tot for k, v in _w.items()}
    _h = -sum(v * _math.log2(v) for v in _p.values())
    _len = huffman_lengths(_p)
    _L = expected_length(_p, _len)
    assert _L >= _h - 1e-9, f"L = {_L!r} is below the entropy {_h!r}, which is impossible"
    assert _L < _h + 1.0 + 1e-9, f"L = {_L!r} exceeds H + 1 = {_h + 1!r}"
try:
    expected_length({"a": 1, "b": 1}, {"a": 1})
    assert False, "a symbol with no length should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "the lengths are optimal, checked exhaustively", "code": r'''
import itertools as _it
import random as _random

_rng = _random.Random(97)
for _trial in range(120):
    _n = _rng.randrange(2, 6)
    _syms = [chr(97 + i) for i in range(_n)]
    _w = {s: _rng.randrange(1, 40) for s in _syms}
    _mine = sum(_w[s] * huffman_lengths(_w)[s] for s in _syms)
    _best = None
    for _combo in _it.product(range(1, _n + 1), repeat=_n):
        if sum(2.0 ** -l for l in _combo) > 1 + 1e-12:
            continue
        _cost = sum(_w[s] * l for s, l in zip(_syms, _combo))
        if _best is None or _cost < _best:
            _best = _cost
    assert _mine == _best, (
        f"on {_w!r} your lengths cost {_mine} but a Kraft-legal assignment costs {_best}")
'''},
                    {"name": "Huffman beats the rounded lengths on a skewed source", "code": r'''
import math as _math

_p = {"a": 0.6, "b": 0.2, "c": 0.1, "d": 0.1}
_h = -sum(v * _math.log2(v) for v in _p.values())
_shannon = {k: _math.ceil(_math.log2(1 / v)) for k, v in _p.items()}
_huff = huffman_lengths(_p)
assert abs(expected_length(_p, _shannon) - 2.0) < 1e-9, "the rounded lengths cost 2.0 here"
assert abs(expected_length(_p, _huff) - 1.6) < 1e-9, \
    f"Huffman costs 1.6 here, got {expected_length(_p, _huff)!r}"
assert kraft_sum(_shannon) == 0.75, "the rounded code leaves a quarter of the tree unspent"
assert kraft_sum(_huff) == 1.0, "an optimal code spends all of it"
assert expected_length(_p, _huff) < expected_length(_p, _shannon)
assert expected_length(_p, _huff) - _h < 0.03, "the overhead here is under 0.03 bits"
_u = {c: 0.25 for c in "abcd"}
assert abs(expected_length(_u, huffman_lengths(_u)) - 2.0) < 1e-9, \
    "on a uniform alphabet Huffman is the fixed-length code"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Arithmetic coding, and the model behind it",
            "summary": "Stop giving symbols codewords. Give the whole message an interval, and name a point inside it.",
            "concepts": [
                "Nested subdivision: after n symbols the interval's width is exactly the message's probability",
                "A half-open interval of width w contains a multiple of 2^-k whenever 2^-k <= w",
                "So naming the interval costs at most -log2 P + 1 bits for the whole message, not per symbol",
                "Exact integer arithmetic: lo and hi over a denominator of total**n, never floats",
                "The decoder rescales the received value by the same subdivision the encoder used",
                "Model and coder are separate: the coder is exact, the bill for a wrong model is D(p||q)",
                "The code is not self-delimiting, and the arithmetic grows without renormalisation",
            ],
            "read": [
                {
                    "title": "Naming the message instead of its symbols",
                    "minutes": 14,
                    "body": r'''
A sensor on the ridge reports every ten minutes whether the temperature moved. It sends
`same` about 99 times in 100 and `changed` about once. Four hundred reports, and the
entropy of that source is 0.0808 bits per report, so the whole batch carries about 32 bits
of news. A Huffman coder — or any code that hands each symbol its own whole number of bits
— spends 400.

Module 2 explained where that goes: two symbols means two codewords, both of length 1,
whatever the probabilities. Blocking the reports into groups helps, at a codebook that
doubles per symbol added. This module takes the other road, which is to stop giving symbols
codewords at all.

## One interval for the whole message

Take the unit interval $[0, 1)$ and cut it into pieces whose widths are the symbol
probabilities, in a fixed order. The first symbol of the message picks its piece. Cut that
piece in the same proportions, and the second symbol picks a sub-piece. Keep going.

After $n$ symbols you hold one interval, and two facts about it are true by construction.
Its width is the product of the probabilities of the symbols you picked, which is exactly
$P(\text{message})$. And two different messages hold disjoint intervals, because they
parted company at the first symbol where they differ. So the $n$-symbol messages tile
$[0, 1)$ into pieces whose widths are their probabilities, and naming a message is the same
job as naming its piece.

Here is the subdivision done in exact integers, with the model $a: 5$, $b: 2$, $c: 1$ out
of 8, on the message `abaca`:

```python
TABLE = {"a": (0, 5), "b": (5, 7), "c": (7, 8)}
TOTAL = 8

lo, hi, den = 0, 1, 1
for s in "abaca":
    c_lo, c_hi = TABLE[s]
    span = hi - lo
    lo, hi = lo * TOTAL + span * c_lo, lo * TOTAL + span * c_hi
    den *= TOTAL
    print(f"{s}: [{lo}/{den}, {hi}/{den})   width {(hi - lo) / den:.8f}")
```

The trace runs $[0/8, 5/8)$, then $[25/64, 35/64)$, then $[200/512, 250/512)$, then
$[1950/4096, 2000/4096)$, and finally $[15600/32768, 15850/32768)$. The last width is
$250/32768 = 0.00762939$, and $\log_2(1/0.00762939) = 7.034$. Every quantity here is an
integer over a power of the model total, so nothing has been rounded anywhere.

## Naming a point costs about log of one over the width

A $k$-bit string names the dyadic rational $m / 2^k$. Those points sit on a grid of spacing
$2^{-k}$. A half-open interval whose width is at least the grid spacing must contain a grid
point — slide a window of length $2^{-k}$ along and it always covers exactly one. So as soon
as $2^{-k} \le w$, a $k$-bit string exists inside the interval, and

$$k = \text{ceil}(\log_2 (1/w)) < \log_2 \frac{1}{w} + 1$$

is enough. With $w = P(\text{message})$ that is $-\log_2 P + 1$ bits for the *entire*
message. The one-bit slack that a symbol code paid per symbol is now paid once, over the
whole message, so per symbol it is $1/n$ and it vanishes as the message grows. Nothing was
approximated to get there; the whole argument is the grid-spacing observation plus the
subdivision.

Search from $k = 0$ upwards and you often do better than the bound. For `abaca` the width
is $250/32768$, so $\text{ceil}(\log_2(1/w)) = 8$, but $k = 7$ already works: the grid point
$61/128 = 0.4765625$ falls inside $[0.4760742, 0.4836426)$, and the encoding is
`0111101`.

```python
def shortest_dyadic(lo, hi, den):
    """The shortest bit string b with 0.b inside [lo/den, hi/den)."""
    k = 0
    while True:
        m = -((-(lo << k)) // den)          # ceil(lo * 2**k / den)
        if m * den < hi << k:
            return format(m, "0%db" % k) if k else ""
        k += 1


print(shortest_dyadic(15600, 15850, 32768))
print(shortest_dyadic(0, 1, 1), shortest_dyadic(1, 2, 4), shortest_dyadic(3, 4, 8))
```

The decoder runs the subdivision forwards with the received value in hand. Read
`0111101` as $61/128 = 0.4765625$. Is it in $[0, 5/8)$? Yes, so the first symbol is `a`.
Rescale: $(0.4765625 - 0) / (5/8) = 0.7625$, times 8 is 6.1, and 6 lies in $[5, 7)$, so the
second symbol is `b`. Continue and `abaca` comes back. The decoder never sees a codeword,
because there are none — there is one number, and five nested questions asked of it.

## The mistake that eats messages

The interval picture is about real numbers in $[0, 1)$, so the natural first implementation
uses floats. It works, for a while.

```python
TABLE = {"a": (0, 5), "b": (5, 7), "c": (7, 8)}
TOTAL = 8

lo, hi = 0.0, 1.0
for i, s in enumerate("abacab" * 20, 1):
    c_lo, c_hi = TABLE[s]
    span = hi - lo
    lo, hi = lo + span * c_lo / TOTAL, lo + span * c_hi / TOTAL
    if hi <= lo:
        print(f"the interval vanished after {i} symbols: lo == hi == {lo!r}")
        break
```

After 36 symbols the interval has no width left. A double carries 53 bits of mantissa, this
message costs about 1.5 bits a symbol, and $53 / 1.5$ is 35. Past that point every symbol
narrows an interval that is already a single float, the encoder emits something, and the
decoder returns a different message with no error raised anywhere. It is a silent
data-destroying defect whose test suite passes, because the ten-symbol test cases in every
tutorial are under the limit.

The exact version keeps `lo` and `hi` as Python integers over a denominator of
$\text{total}^n$, which is why the lab's checks feed it messages of ninety symbols and
compare the decode to the original exactly. Real implementations do neither: they
renormalise, emitting settled leading bits and rescaling the interval so the registers stay
a fixed width. That is an engineering answer to the same problem, and the exact version is
the specification it has to match.

The second mistake is subtler. The encoding of the empty message is the empty bit string,
and so is the encoding of `zzzz` under a one-symbol model — and, for that matter,
`shortest_dyadic(0, 1, 2)` is the empty string too, because 0 lies in $[0, 1/2)$. An
arithmetic code is not self-delimiting. The decoder is handed the symbol count separately,
or the model carries an end-of-message symbol with a small frequency. Forget that and a
stream decodes forever.

## The coder is exact; the model is where the bits go

Every bit the coder spends past $-\log_2 P$ is at most one, for the whole message. So the
file size is decided by the model, and by nothing else. Module 1 already priced that: coding
a $p$-source under a model $q$ costs $H(p) + D(p \parallel q)$ per symbol. With an exact
coder that inequality becomes an equality up to the single trailing bit, which is why
modern compressors are described as a model plus a range coder, and why the interesting work
is all in the model.

```python
import random

FREQ = {"changed": 1, "same": 99}
TABLE, TOTAL = {"changed": (0, 1), "same": (1, 100)}, 100


def encode(symbols):
    lo, hi, den = 0, 1, 1
    for s in symbols:
        c_lo, c_hi = TABLE[s]
        span = hi - lo
        lo, hi = lo * TOTAL + span * c_lo, lo * TOTAL + span * c_hi
        den *= TOTAL
    k = 0
    while True:
        m = -((-(lo << k)) // den)
        if m * den < hi << k:
            return format(m, "0%db" % k) if k else ""
        k += 1


rng = random.Random(5)
msg = ["same" if rng.random() < 0.99 else "changed" for _ in range(400)]
bits = encode(msg)
print(f"{msg.count('changed')} changes in 400 reports")
print(f"arithmetic coder: {len(bits)} bits, {len(bits) / 400:.5f} per report")
print("any symbol code:   400 bits, 1.00000 per report")
```

Three changes in that seeded batch, twenty-five bits for the lot. A symbol code spends 400.
The gap is not cleverness in the coder; it is that the coder is allowed to spend 0.0145
bits on a `same` and 6.64 on a `changed`, and integers cannot do that.

## Where this stops

The arithmetic is exact but it grows: after $n$ symbols the denominator is
$\text{total}^n$, so the encoder does arithmetic on numbers with $n \log_2(\text{total})$
bits and the whole encode is quadratic in the message length. The renormalising
implementations exist for that reason and not for elegance. Decoding is strictly sequential
— there is no way into the middle of the stream without replaying it from the start, which
is why formats that need random access chop the data into independently coded blocks and
pay the per-block overhead again. And the guarantee is about $-\log_2 P$ under *your*
model: a coder that reaches the ideal for a bad model still produces a large file, and no
amount of coding rescues it.

## What the lab asks for

The lab *Spending a fraction of a bit* wants `cumulative`, `shortest_dyadic`,
`arith_encode`, `arith_decode` and `ideal_bits`. The checks assert the `abaca` trace above
bit for bit, round-trip ninety-symbol messages under randomised models, and hold
`len(bits)` to at most `ideal_bits + 1` — the bound derived here, not a tolerance. One check
builds a message with an exact composition and asserts that coding it under a uniform model
costs exactly 2000 bits more than coding it under the true one, which is
$8000 \times D(p \parallel q)$ with $D = 0.25$: module 1's number, arriving as a file size.
''',
                },
            ],
            "quiz": {
                "title": "Intervals, precision and the model",
                "minutes": 8,
                "questions": [
                    {
                        "q": "After coding a 400-symbol message, an arithmetic coder holds an interval of width w. How many bits does it emit, and why that many?",
                        "opts": [
                            "About log2(1/w) for the message, because a 2^-k grid meets an interval that wide",
                            "About log2(1/w) per symbol, because each symbol narrows the interval by its own probability",
                            "Exactly 400, because every symbol contributes one bit to the number being named",
                            "About log2(1/w) plus one bit per symbol, because each subdivision has to be rounded",
                        ],
                        "a": 0,
                        "why": r"""
A $k$-bit string names a point $m/2^k$ on a grid of spacing $2^{-k}$, and a half-open
interval at least that wide has to contain one of those points. So $k$ can be taken as
$\text{ceil}(\log_2(1/w))$, which is under $\log_2(1/w) + 1$. Since $w$ is the probability
of the whole message, the bill is $-\log_2 P + 1$ bits — total, not per symbol. That single
slack bit is what a symbol code pays on every symbol, and moving it outside the loop is the
entire advantage.
                        """,
                        "whys": [
                            r"""
Right, and the grid picture is the whole proof: the dyadics of denominator $2^k$ are spaced
$2^{-k}$ apart, a window of that length slid along the line always covers one, and a
half-open interval of width at least $2^{-k}$ contains such a window. Nothing about
probability enters — it is a statement about intervals, and the probability only decides how
wide this one is.
                            """,
                            r"""
$\log_2(1/w)$ is already the cost for the whole message, because $w$ is the whole message's
probability, not one symbol's. Reading it as per-symbol multiplies the true answer by 400.
The per-symbol figure is $\log_2(1/w) / n$, which for a source of entropy $H$ is close to
$H$ — and that is the point of the construction.
                            """,
                            r"""
The output length has no fixed relationship to the symbol count. On the sensor source 400
reports came out as 25 bits; on a uniform source over 256 symbols 400 reports would be 3200.
The length tracks $-\log_2$ of the message's probability, which is a fact about the model
and the data together, not about how many symbols were fed in.
                            """,
                            r"""
Nothing is rounded during the subdivision. Both endpoints are exact integers over
$\text{total}^n$, and the only rounding in the whole algorithm is the single choice of a
dyadic point at the end. Adding a bit per symbol would recreate exactly the overhead that
arithmetic coding was built to avoid.
                            """,
                        ],
                    },
                    {
                        "q": "A student's arithmetic coder keeps `lo` and `hi` as floats. It round-trips every test message and fails in production. What is the failure mode?",
                        "opts": [
                            "It raises `OverflowError` once the interval is narrower than the smallest positive float",
                            "Rounding makes the emitted bit string one or two bits longer than it needs to be",
                            "Past about 53 bits of cost the interval collapses and the decode differs",
                            "It works for any length but drifts, so the last few symbols of a long message are wrong",
                        ],
                        "a": 2,
                        "why": r"""
A double carries 53 bits of mantissa. The interval's width is $2^{-B}$ where $B$ is the
message's total cost in bits, so once $B$ passes about 53, `lo` and `hi` are the same float
and every later subdivision is a no-op. Nothing raises: the encoder emits a bit string, the
decoder decodes *a* message, and the two differ. The demonstration in the reading dies after
36 symbols on a source costing about 1.5 bits each. Test messages are short, production
messages are not, which is why this defect ships.
                        """,
                        "whys": [
                            r"""
Floats underflow to zero quietly rather than raising, and in any case the endpoints
themselves stay in a normal range — it is their *difference* that vanishes. An exception
would be a mercy here; the actual behaviour is that `hi - lo` becomes 0.0 and the loop
carries on subdividing nothing.
                            """,
                            r"""
A couple of wasted bits would be a performance defect and a tolerable one. What happens is a
correctness defect: the decoder returns different symbols. It is worth separating those two
categories when reading any coder, because the tests you write for them are different — one
compares lengths, the other compares messages.
                            """,
                            r"""
Right, and the number to carry is the budget rather than a symbol count: 53 bits of mantissa
divided by the per-symbol cost gives the length at which it breaks. A skewed source costing
0.1 bits a symbol survives 500 symbols; a uniform byte source costing 8 breaks at 6. The
same code, two very different-looking bugs.
                            """,
                            r"""
There is no gradual drift. Up to the precision limit the float version is exact for these
inputs, and past it the interval has zero width and the subdivision stops doing anything at
all. The failure is a cliff, not a slope, which is why halving the tolerance in a test never
finds it.
                            """,
                        ],
                    },
                    {
                        "q": "`arith_decode(bits, freqs, n)` takes the symbol count as an argument. Why can it not work it out from the bits?",
                        "opts": [
                            "Because the bit string is the same for a message and for that message with symbols appended",
                            "Because the decoder cannot know the model total until it has read the first symbol",
                            "Because a message of n symbols can encode to fewer than n bits, so the count is not recoverable",
                            "Because the encoder emits the shortest dyadic, which discards the trailing bits that mark the end",
                        ],
                        "a": 0,
                        "why": r"""
The code is not self-delimiting. The received value names a point, and that point sits
inside a whole nest of intervals — the one for the 5-symbol message, the one for its 6-symbol
extension, and so on forever. Every one of those is a valid decode; the bits do not say
where to stop. The empty string makes it vivid: it names the value 0, which lies inside the
interval of the empty message, of `aaaa`, and of `a` repeated any number of times. Real
formats fix this by transmitting the length or by giving the model an end-of-message symbol
with a small frequency, which costs a few bits and buys termination.
                        """,
                        "whys": [
                            r"""
Right, and the nesting is the reason no cleverness helps: the intervals for a message and
its extensions are nested by construction, so any point in the inner one is also in the
outer. The decoder is asking "which interval" and the answer is "all of them" until
something else says how deep to go.
                            """,
                            r"""
The model, including its total, is a shared parameter — the decoder is handed the same
`freqs` the encoder used, and computes the same cumulative table before reading a bit. That
is not the missing information. What is missing is where the nest of intervals stops.
                            """,
                            r"""
It is true that a message can encode to fewer bits than it has symbols — the sensor batch
was 400 symbols in 25 bits — but that is not what blocks recovery. Even a message whose
encoding is longer than itself cannot have its length read off, because the bits still name
a point that lies in infinitely many nested intervals.
                            """,
                            r"""
There are no trailing bits to discard. The encoder picks the shortest dyadic strictly inside
the final interval, and every bit of it is load-bearing — drop one and the point moves
outside. A longer emission would not encode the length either; it would name the same nest
of intervals more precisely.
                            """,
                        ],
                    },
                    {
                        "q": "You code an 8000-symbol message whose composition is exactly p = (1/2, 1/4, 1/8, 1/8) with a uniform model instead of the true one. How much larger is the file, to the nearest bit?",
                        "opts": [
                            "About 1000 bits larger, the entropy difference of 0.125 bits a symbol",
                            "About 2000 bits larger, which is 8000 times D(p||uniform) = 0.25 bits",
                            "About 4000 bits larger, since a uniform model over four symbols spends 2 bits each",
                            "The same size, since an exact coder reaches the bound whatever model it is given",
                        ],
                        "a": 1,
                        "why": r"""
An exact coder spends $-\log_2 q(\text{message})$ bits, so under the uniform model the bill
is $8000 \times 2 = 16000$ bits and under the true one $8000 \times 1.75 = 14000$. The
difference is 2000, and it is exactly $8000 \times D(p \parallel q)$ with $D = 0.25$ from
module 1. The coder was not the variable — it hit its bound both times. This is the check
the lab runs, and the arithmetic comes out to the bit because the composition is exact.
                        """,
                        "whys": [
                            r"""
0.125 is not the divergence here. $D(p \parallel q) = \sum_x p_x \log_2(p_x / 0.25)$ works
out to 0.25 bits a symbol, which is the same as $\log_2 4 - H(p) = 2 - 1.75$ for a uniform
$q$ — a shortcut worth knowing, and one that only holds when $q$ is uniform.
                            """,
                            r"""
Right, and the shape of the answer generalises: the excess is $n \, D(p \parallel q)$
whatever $q$ is, so a model's cost is linear in the message length. That is what makes a
stale model a per-byte tax and a big model header a one-off, and it is the trade every
practical compressor is tuning.
                            """,
                            r"""
4000 would be the cost of the uniform model if the true model were free — that is,
$8000 \times 2$ minus nothing. The comparison is between two real bills, 16000 and 14000,
and the true model does not cost zero: the source has 1.75 bits a symbol of genuine
uncertainty that no model can remove.
                            """,
                            r"""
The bound an exact coder reaches is $-\log_2 q$ of the message under *its own* model, not
$-\log_2 p$ under the truth. Give it a worse model and it reaches a worse bound exactly. The
coder's exactness is what makes the model's error visible as a clean 2000 bits rather than
being tangled up with rounding.
                            """,
                        ],
                    },
                    {
                        "q": "The reading builds the interval with `lo, hi = lo * total + span * c_lo, lo * total + span * c_hi` and multiplies `den` by `total`. Why is `span` computed before the assignment rather than after?",
                        "opts": [
                            "Because `span` must be measured against the old denominator, which the assignment then changes",
                            "Because Python evaluates the right-hand side of a tuple assignment before rebinding either name",
                            "Because `hi - lo` would be negative once the new `lo` has been written into place",
                            "Because the new interval is a sub-interval and its span is needed for the next symbol, not this one",
                        ],
                        "a": 0,
                        "why": r"""
`span` is the width of the *current* interval in units of the current denominator, and both
new endpoints are built from it: $\text{lo}' = \text{lo} \cdot \text{total} + \text{span}
\cdot c_{lo}$ over the denominator $\text{den} \cdot \text{total}$. Compute it after `den`
has been multiplied and it is a width measured against a denominator it no longer belongs
to, so the sub-interval lands in the wrong place. Python's tuple assignment does evaluate
the right-hand side first, which is why the two endpoint expressions can both refer to the
old `lo` — but that is a convenience, not the reason `span` exists as a separate name.
                        """,
                        "whys": [
                            r"""
Right, and stating it as a unit check is the way to keep it straight: `lo`, `hi` and `span`
are all counts over `den`, and the assignment moves everything to counts over
`den * total`. Any quantity carried across that line without being rescaled is being read in
the wrong units.
                            """,
                            r"""
Python's evaluation order is genuinely why `lo * total + span * c_hi` can use the old `lo`
on the second half of the tuple, and it is worth knowing. But `span` is bound on its own line
before the assignment, so the tuple rule is not what protects it — and two separate
statements would be equally correct as long as `span` were computed first.
                            """,
                            r"""
`hi - lo` is never negative: the new endpoints satisfy $\text{lo}' < \text{hi}'$ because
$c_{lo} < c_{hi}$ and `span` is positive. Sign is not the hazard here. The hazard is scale —
a correct-looking positive width expressed against the wrong denominator.
                            """,
                            r"""
The span used at each step is the width of the interval as it stands when the symbol
arrives, and it is consumed immediately rather than saved for later. The next symbol
recomputes its own span from the endpoints it inherits, which is what makes the loop
stateless apart from `lo`, `hi` and `den`.
                            """,
                        ],
                    },
                    {
                        "q": "Why do production arithmetic coders renormalise — emitting settled leading bits and rescaling — instead of using the exact big-integer form the lab asks for?",
                        "opts": [
                            "Because big integers lose precision once the denominator exceeds the machine word size",
                            "Because the exact form cannot represent models whose frequencies are not powers of two",
                            "Because the exact form works on numbers that grow with the message, making the encode quadratic",
                            "Because renormalising produces shorter output, closer to the entropy than the exact form gets",
                        ],
                        "a": 2,
                        "why": r"""
After $n$ symbols the denominator is $\text{total}^n$, so the endpoints are numbers of about
$n \log_2(\text{total})$ bits and every step multiplies numbers that size — the whole encode
costs on the order of $n^2$ bit operations, and megabyte files are out of reach. Renormalising
keeps the registers a fixed width by shipping leading bits that can no longer change and
rescaling what remains. It is a performance answer, and it emits the same bits: the exact
version is the specification the fast one has to match, which is why the lab builds it first.
                        """,
                        "whys": [
                            r"""
Python integers do not lose precision at any size — that is the whole reason the lab uses
them rather than floats, and the reading's demonstration is about floats collapsing, not
integers. Big integers get slow, never inaccurate, and keeping those two failure modes apart
is what lets you choose between the two implementations on purpose.
                            """,
                            r"""
The exact form handles arbitrary integer frequencies without difficulty — the `abaca` example
runs on a total of 8 with a frequency of 5, and the sensor example on a total of 100. Nothing
in the subdivision wants powers of two; the only power of two in the algorithm is the grid
the final point is chosen from.
                            """,
                            r"""
Right, and the size to picture is concrete: a one-megabyte file under a byte model has a
denominator of $256^{1000000}$, a number with eight million bits, and every symbol multiplies
two numbers that long. Quadratic in the message length is a real wall rather than a
constant-factor complaint.
                            """,
                            r"""
Renormalising does not shorten anything — a correct renormalising coder emits the same bits
as the exact one, within the final bit or two, and that agreement is how it is tested. It
buys linear time and fixed-width registers, and a scheme that produced *shorter* output than
the exact form would be beating $-\log_2 P$, which the counting argument forbids.
                            """,
                        ],
                    },
                ],
            },
            "blanks": {
                "title": "The subdivision and the search",
                "minutes": 9,
                "caption": "arith.py — four decisions removed",
                "lang": "python",
                "brief": r"""
Both loops are five lines and both are unit conversions in disguise: counts over one
denominator becoming counts over a larger one. Fill the holes, then read the comment at the
bottom, which is the only reason the whole scheme terminates.
""",
                "listing": """def arith_encode(symbols, freqs):
    \"\"\"One interval for the whole message, then a point inside it.\"\"\"
    table, total = cumulative(freqs)
    lo, hi, den = 0, 1, 1
    for s in symbols:
        c_lo, c_hi = table[s]
        span = ___
        lo, hi = lo * total + span * c_lo, lo * total + span * c_hi
        den = ___
    return shortest_dyadic(lo, hi, den)


def shortest_dyadic(lo, hi, den):
    \"\"\"The shortest bit string b with 0.b inside [lo/den, hi/den).\"\"\"
    k = 0
    while True:
        m = -((-(lo << k)) // den)          # ceil(lo * 2**k / den)
        if ___:
            return format(m, "0%db" % k) if k else ""
        k ___


# the search stops because 2**-k eventually drops below the interval width,
# and a grid that fine cannot step over a half-open interval
""",
                "blanks": [
                    {
                        "prompt": "Both new endpoints are built from the width of the interval as it stands. What is that width, in the current units?",
                        "hole": "?",
                        "opts": ["hi - lo", "hi", "hi + lo", "den"],
                        "a": 0,
                        "why": "The interval is [lo/den, hi/den), so its width in units of 1/den is hi - lo. Every sub-interval is carved out of that width, which is why it is the only quantity the symbol's cumulative counts get multiplied by.",
                        "whys": [
                            "The interval is [lo/den, hi/den), so its width in units of 1/den is hi - lo. Every sub-interval is carved out of that width, which is why it is the only quantity the symbol's cumulative counts get multiplied by.",
                            "Using the upper endpoint alone measures from zero rather than from lo, so every symbol after the first carves its share out of the wrong region and the intervals stop nesting.",
                            "A sum of the endpoints is not a width in any units. It happens to equal the width on the first step, where lo is 0, so a one-symbol test passes and everything longer fails.",
                            "The denominator is the scale, not the width. Substituting it makes each sub-interval the same size regardless of where the previous symbol left the interval, which is a coder that ignores its own history.",
                        ],
                    },
                    {
                        "prompt": "The endpoints on the line above were multiplied through by the model total. What does the denominator become?",
                        "hole": "?",
                        "opts": ["den * total", "den + total", "total", "den * span"],
                        "a": 0,
                        "why": "Each symbol divides the current interval into `total` parts, so the scale gets `total` times finer and the denominator picks up one more factor. After n symbols it is total**n, which is why the arithmetic is exact and why it grows.",
                        "whys": [
                            "Each symbol divides the current interval into `total` parts, so the scale gets `total` times finer and the denominator picks up one more factor. After n symbols it is total**n, which is why the arithmetic is exact and why it grows.",
                            "Adding rather than multiplying leaves the denominator far too small, so the endpoints, which were multiplied, describe a range outside [0, 1) after two or three symbols.",
                            "Resetting the denominator to the total throws away every earlier subdivision, so the coder codes only the last symbol and the decode returns that symbol repeated.",
                            "The span is the width of the old interval, not a scale factor, and it changes from symbol to symbol — so the denominator would stop being a power of the total and the endpoints would no longer be counts in it.",
                        ],
                    },
                    {
                        "prompt": "m/2**k is the smallest grid point at or above lo/den. What has to be true for it to be a legal encoding?",
                        "hole": "?",
                        "opts": ["m * den < hi << k", "m * den <= hi << k", "m * den < lo << k", "m < hi"],
                        "a": 0,
                        "why": "The interval is half-open, so the point has to be strictly below hi/den. Cross-multiplying by the positive den and 2**k turns that into m * den < hi * 2**k, with no division and no rounding anywhere.",
                        "whys": [
                            "The interval is half-open, so the point has to be strictly below hi/den. Cross-multiplying by the positive den and 2**k turns that into m * den < hi * 2**k, with no division and no rounding anywhere.",
                            "Allowing equality accepts the upper endpoint, which belongs to the next message along. The decoder then rescales a value sitting exactly on a boundary and picks the following symbol, so the message comes back with one symbol changed.",
                            "Comparing against the lower endpoint asks whether the point is below where it started, which m never is by construction. The loop would run until the shift overflowed the patience of whoever started it.",
                            "Comparing m with hi compares a numerator over 2**k against a numerator over den, which are different scales. It happens to be true early and false later, so short messages encode and long ones loop.",
                        ],
                    },
                    {
                        "prompt": "No grid point fitted at this resolution. How should the search refine it?",
                        "hole": "?",
                        "opts": ["+= 1", "-= 1", "*= 2", "+= den"],
                        "a": 0,
                        "why": "One more bit halves the grid spacing, and the first k whose spacing drops to or below the interval width is guaranteed to land inside it. Stepping k by one is also what makes the result the shortest such string rather than merely a short one.",
                        "whys": [
                            "One more bit halves the grid spacing, and the first k whose spacing drops to or below the interval width is guaranteed to land inside it. Stepping k by one is also what makes the result the shortest such string rather than merely a short one.",
                            "Going down coarsens the grid and drives k negative, at which point the shift raises rather than returning a wider grid. The search moves away from the answer on every iteration.",
                            "Doubling never leaves zero, so a search that starts at k = 0 stays there and loops forever on any interval that does not already contain 0. It would look correct on the empty message, which is the one case that returns immediately.",
                            "Adding the denominator jumps k past every resolution worth trying, so the emitted string is enormous — thousands of bits for a five-symbol message — while still being a legal encoding, which is why no round-trip check would catch it.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Spending a fraction of a bit",
                "runtime": "python",
                "minutes": 75,
                "brief": r'''
Five functions and no floating point anywhere in the coder.

**`cumulative(freqs)`** — `freqs` maps a symbol to a positive integer frequency.
Return `(table, total)`, where `table` maps each symbol to its half-open
`(lo, hi)` range of cumulative counts, assigned in **sorted symbol order** so
encoder and decoder agree. Raise `ValueError` for an empty model or a frequency
that is not an integer of at least 1.

```text
cumulative({"b": 2, "a": 5, "c": 3})
    -> ({"a": (0, 5), "b": (5, 7), "c": (7, 10)}, 10)
```

**`shortest_dyadic(lo, hi, den)`** — the shortest bit string `b` such that the
binary fraction `0.b` lies in `[lo/den, hi/den)`. Search `k` upwards from 0; the
value is `ceil(lo * 2**k / den)`, and it is legal when `m * den < hi * 2**k`. The
empty string denotes 0. Raise `ValueError` unless `0 <= lo < hi <= den`.

```text
shortest_dyadic(0, 1, 1)          -> ""        0 is in [0, 1)
shortest_dyadic(1, 2, 4)          -> "01"      1/4 is in [1/4, 1/2)
shortest_dyadic(3, 4, 8)          -> "011"     3/8 is in [3/8, 1/2)
shortest_dyadic(15600, 15850, 32768) -> "0111101"
```

**`arith_encode(symbols, freqs)`** — subdivide `[0, 1)` symbol by symbol, keeping
`lo`, `hi` and `den` as exact integers, then return `shortest_dyadic` of the final
interval. `ValueError` for a symbol the model does not have.

**`arith_decode(bits, freqs, n)`** — the `n` symbols the bit string spells out. Read
the bits as `m` over `2**len(bits)`, then at each step take
`idx = ((m*den - (lo << k)) * total) // ((hi - lo) << k)` and pick the symbol whose
range contains `idx`. `ValueError` for a bit string containing anything but `0` and
`1`, or a negative `n`.

**`ideal_bits(symbols, freqs)`** — `-log2` of the message's probability under the
model, as a float: `sum(log2(total / f))` over the symbols. This is the target the
coder is measured against.

Standard library only; `math` is the one import, and it is needed only by
`ideal_bits`. One check asserts `len(arith_encode(...)) <= ideal_bits(...) + 1` — the
bound the reading derives — and another asserts that coding an 8000-symbol message
under a uniform model costs exactly 2000 bits more than under the true one.
''',
                "files": [{"name": "main.py", "content": r'''
import math


def cumulative(freqs):
    """(table, total) with each symbol's half-open range of cumulative counts."""
    # your code here


def shortest_dyadic(lo, hi, den):
    """The shortest bit string b with 0.b inside [lo/den, hi/den)."""
    # your code here


def arith_encode(symbols, freqs):
    """One interval for the whole message, then the shortest point inside it."""
    # your code here


def arith_decode(bits, freqs, n):
    """The n symbols the bit string spells out."""
    # your code here


def ideal_bits(symbols, freqs):
    """-log2 of the message's probability under the model."""
    # your code here


print(cumulative({"b": 2, "a": 5, "c": 3}))
print(arith_encode("abaca", {"a": 5, "b": 2, "c": 1}))
print(arith_decode("0111101", {"a": 5, "b": 2, "c": 1}, 5))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def cumulative(freqs):
    """(table, total) with each symbol's half-open range of cumulative counts."""
    if not freqs:
        raise ValueError("a model with no symbols codes nothing")
    table, run = {}, 0
    # sorted order, so an encoder and a decoder built separately still agree
    for sym in sorted(freqs):
        f = freqs[sym]
        if isinstance(f, bool) or not isinstance(f, int) or f < 1:
            raise ValueError(f"frequency {f!r} for {sym!r} is not a positive integer")
        table[sym] = (run, run + f)
        run += f
    return table, run


def shortest_dyadic(lo, hi, den):
    """The shortest bit string b with 0.b inside [lo/den, hi/den)."""
    if not (isinstance(den, int) and isinstance(lo, int) and isinstance(hi, int)):
        raise ValueError("the interval must be given in exact integers")
    if not 0 <= lo < hi <= den:
        raise ValueError(f"[{lo}/{den}, {hi}/{den}) is not a sub-interval of [0, 1)")
    k = 0
    while True:
        m = -((-(lo << k)) // den)          # ceil(lo * 2**k / den), in integers
        if m * den < hi << k:               # strictly below hi: the interval is half-open
            return format(m, "0%db" % k) if k else ""
        k += 1                              # one more bit halves the grid spacing


def arith_encode(symbols, freqs):
    """One interval for the whole message, then the shortest point inside it."""
    table, total = cumulative(freqs)
    lo, hi, den = 0, 1, 1
    for s in symbols:
        if s not in table:
            raise ValueError(f"the model has no frequency for {s!r}")
        c_lo, c_hi = table[s]
        span = hi - lo                      # width in units of 1/den, before rescaling
        lo, hi = lo * total + span * c_lo, lo * total + span * c_hi
        den = den * total
    return shortest_dyadic(lo, hi, den)


def arith_decode(bits, freqs, n):
    """The n symbols the bit string spells out."""
    table, total = cumulative(freqs)
    if isinstance(n, bool) or not isinstance(n, int) or n < 0:
        raise ValueError("the symbol count must be a non-negative integer")
    if not isinstance(bits, str) or set(bits) - {"0", "1"}:
        raise ValueError(f"{bits!r} is not a bit string")
    k = len(bits)
    m = int(bits, 2) if bits else 0
    lo, hi, den = 0, 1, 1
    out = []
    for _ in range(n):
        span = hi - lo
        # where the received value sits inside the current interval, scaled to `total`
        idx = ((m * den - (lo << k)) * total) // (span << k)
        pick = None
        for sym, (c_lo, c_hi) in table.items():
            if c_lo <= idx < c_hi:
                pick = sym
                break
        if pick is None:
            raise ValueError("the bits do not decode under this model")
        out.append(pick)
        c_lo, c_hi = table[pick]
        lo, hi = lo * total + span * c_lo, lo * total + span * c_hi
        den = den * total
    return out


def ideal_bits(symbols, freqs):
    """-log2 of the message's probability under the model."""
    table, total = cumulative(freqs)
    bits = 0.0
    for s in symbols:
        if s not in table:
            raise ValueError(f"the model has no frequency for {s!r}")
        c_lo, c_hi = table[s]
        bits += math.log2(total / (c_hi - c_lo))
    return bits


print(cumulative({"b": 2, "a": 5, "c": 3}))
print(arith_encode("abaca", {"a": 5, "b": 2, "c": 1}))
print(arith_decode("0111101", {"a": 5, "b": 2, "c": 1}, 5))
'''}],
                "hints": [
                    "Keep `lo`, `hi` and `den` as Python integers throughout. The moment a float appears the interval collapses somewhere past the fiftieth symbol and the decode changes silently.",
                    "`-((-x) // d)` is ceiling division for non-negative integers, and it avoids the float rounding that `math.ceil(x / d)` would introduce on large values.",
                    "`lo << k` is `lo * 2**k` and is much faster on the thousand-bit integers this builds. The comparison `m * den < hi << k` is the half-open test with both divisions cleared.",
                    "The decoder repeats the encoder's update line exactly, using the same `span` computed before the assignment. If the two lines differ at all, long messages decode to something plausible but wrong.",
                    "`format(m, \"0%db\" % k)` pads to k bits; for k = 0 return the empty string explicitly, because `format(0, \"00b\")` gives `\"0\"`.",
                ],
                "tests": [
                    {"name": "cumulative lays the model out in sorted order", "code": r'''
_t, _n = cumulative({"b": 2, "a": 5, "c": 3})
assert _t == {"a": (0, 5), "b": (5, 7), "c": (7, 10)}, f"got {_t!r}"
assert _n == 10, f"total {_n!r}"
assert list(_t) == ["a", "b", "c"], f"the table must be in sorted symbol order, got {list(_t)!r}"
_t2, _n2 = cumulative({"z": 1})
assert _t2 == {"z": (0, 1)} and _n2 == 1, f"got {(_t2, _n2)!r}"
for _bad in [{}, {"a": 0}, {"a": -1}, {"a": 1.5}, {"a": 2, "b": 0}]:
    try:
        cumulative(_bad)
        assert False, f"cumulative({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "shortest_dyadic finds the shortest point inside", "code": r'''
assert shortest_dyadic(0, 1, 1) == "", "0 lies in [0, 1), so no bits are needed"
assert shortest_dyadic(1, 2, 4) == "01", f"got {shortest_dyadic(1, 2, 4)!r}"
assert shortest_dyadic(1, 2, 2) == "1", f"got {shortest_dyadic(1, 2, 2)!r}"
assert shortest_dyadic(3, 4, 8) == "011", f"got {shortest_dyadic(3, 4, 8)!r}"
assert shortest_dyadic(5, 6, 8) == "101", f"got {shortest_dyadic(5, 6, 8)!r}"
assert shortest_dyadic(15600, 15850, 32768) == "0111101", \
    f"got {shortest_dyadic(15600, 15850, 32768)!r}"
for _lo, _hi, _den in [(0, 1, 1), (1, 2, 4), (3, 4, 8), (5, 6, 8), (7, 9, 16), (99, 101, 256)]:
    _b = shortest_dyadic(_lo, _hi, _den)
    _v = (int(_b, 2) if _b else 0), (2 ** len(_b))
    assert _v[0] * _den >= _lo * _v[1] and _v[0] * _den < _hi * _v[1], \
        f"{_b!r} is not inside [{_lo}/{_den}, {_hi}/{_den})"
for _bad in [(1, 1, 4), (2, 1, 4), (0, 5, 4), (-1, 2, 4)]:
    try:
        shortest_dyadic(*_bad)
        assert False, f"shortest_dyadic{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "the traced message encodes and decodes bit for bit", "code": r'''
_f = {"a": 5, "b": 2, "c": 1}
assert arith_encode("abaca", _f) == "0111101", f"got {arith_encode('abaca', _f)!r}"
assert arith_decode("0111101", _f, 5) == list("abaca"), \
    f"got {arith_decode('0111101', _f, 5)!r}"
assert abs(ideal_bits("abaca", _f) - 7.034215715337913) < 1e-9, \
    f"got {ideal_bits('abaca', _f)!r}"
assert abs(ideal_bits("a", _f) - math.log2(8 / 5)) < 1e-12
assert ideal_bits("", _f) == 0.0, "an empty message carries nothing"
'''},
                    {"name": "encode and decode round-trip under random models", "code": r'''
import random as _random

_rng = _random.Random(4113)
for _trial in range(60):
    _syms = [chr(97 + i) for i in range(_rng.randrange(2, 7))]
    _f = {s: _rng.randrange(1, 40) for s in _syms}
    _msg = [_rng.choice(_syms) for _ in range(_rng.randrange(0, 90))]
    _bits = arith_encode(_msg, _f)
    _back = arith_decode(_bits, _f, len(_msg))
    assert _back == _msg, (
        f"round trip failed under {_f!r}: {len(_msg)} symbols in, {_bits!r} out, "
        f"first difference at {next((i for i, (x, y) in enumerate(zip(_msg, _back)) if x != y), None)!r}")
'''},
                    {"name": "the output never exceeds the ideal by more than one bit", "code": r'''
import random as _random

_rng = _random.Random(271828)
_worst = -1.0
for _trial in range(60):
    _syms = [chr(97 + i) for i in range(_rng.randrange(2, 8))]
    _f = {s: _rng.randrange(1, 60) for s in _syms}
    _msg = [_rng.choice(_syms) for _ in range(_rng.randrange(1, 80))]
    _bits = arith_encode(_msg, _f)
    _ideal = ideal_bits(_msg, _f)
    _worst = max(_worst, len(_bits) - _ideal)
    assert len(_bits) <= _ideal + 1 + 1e-9, (
        f"{len(_bits)} bits for an ideal of {_ideal!r} — the bound is ceil(log2(1/w)), "
        "so search k upwards from 0 rather than fixing it")
assert _worst > 0.0, "some message should cost more than its ideal, or the search is wrong"
'''},
                    {"name": "a skewed source costs far less than one bit a symbol", "code": r'''
import random as _random

_rng = _random.Random(5)
_msg = ["same" if _rng.random() < 0.99 else "changed" for _ in range(400)]
_f = {"changed": 1, "same": 99}
_bits = arith_encode(_msg, _f)
assert arith_decode(_bits, _f, 400) == _msg, "the skewed message must survive the round trip"
assert len(_bits) < 40, (
    f"400 reports came to {len(_bits)} bits; a symbol code spends 400, and the "
    "point of the interval is to spend a fraction of a bit on a likely symbol")
assert len(_bits) <= ideal_bits(_msg, _f) + 1 + 1e-9
_all_same = ["same"] * 1000
assert len(arith_encode(_all_same, _f)) < 20, \
    "a thousand identical reports carry almost nothing and should cost almost nothing"
assert arith_decode(arith_encode(_all_same, _f), _f, 1000) == _all_same
'''},
                    {"name": "empty messages and one-symbol alphabets", "code": r'''
_f = {"a": 5, "b": 2, "c": 1}
assert arith_encode([], _f) == "", "an empty message is an empty encoding"
assert arith_decode("", _f, 0) == [], "and decodes back to nothing"
_one = {"z": 1}
assert arith_encode("zzzz", _one) == "", "a one-symbol model carries no information"
assert arith_decode("", _one, 4) == ["z"] * 4, \
    "so the count is the only thing the decoder needs"
assert arith_decode("0111101", _f, 0) == [], "asking for no symbols returns none"
'''},
                    {"name": "the coder refuses what it cannot code", "code": r'''
_f = {"a": 5, "b": 2, "c": 1}
for _bad in [("abz", _f), ("abc", {}), ("abc", {"a": 0, "b": 1, "c": 1})]:
    try:
        arith_encode(*_bad)
        assert False, f"arith_encode{_bad!r} should raise ValueError"
    except ValueError:
        pass
for _bad in [("012", _f, 3), ("0111101", _f, -1), ("0111101", {}, 2)]:
    try:
        arith_decode(*_bad)
        assert False, f"arith_decode{_bad!r} should raise ValueError"
    except ValueError:
        pass
try:
    ideal_bits("abz", _f)
    assert False, "ideal_bits should raise ValueError on an unknown symbol"
except ValueError:
    pass
'''},
                    {"name": "the wrong model costs exactly the relative entropy", "code": r'''
import random as _random

_pool = ["a"] * 4000 + ["b"] * 2000 + ["c"] * 1000 + ["d"] * 1000
_random.Random(77).shuffle(_pool)
_true = {"a": 4, "b": 2, "c": 1, "d": 1}
_uniform = {"a": 1, "b": 1, "c": 1, "d": 1}
_t = ideal_bits(_pool, _true)
_u = ideal_bits(_pool, _uniform)
assert abs(_t - 14000.0) < 1e-6, f"the true model costs 8000 * 1.75 = 14000 bits, got {_t!r}"
assert abs(_u - 16000.0) < 1e-6, f"the uniform model costs 8000 * 2 = 16000 bits, got {_u!r}"
assert abs((_u - _t) - 2000.0) < 1e-6, \
    "the excess is 8000 * D(p||uniform) = 8000 * 0.25 exactly"
_bt = len(arith_encode(_pool, _true))
_bu = len(arith_encode(_pool, _uniform))
assert _bt <= _t + 1 + 1e-9 and _bu <= _u + 1 + 1e-9, \
    f"the coder should reach both ideals: {_bt} against {_t!r}, {_bu} against {_u!r}"
assert _bu - _bt > 1900, f"the model difference must survive into the real output, got {_bu - _bt}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Channels, noise and capacity",
            "summary": "Count the words a codeword can turn into, and the number that fit tells you the rate.",
            "concepts": [
                "A transmitted word of length n arrives as one of about 2^(n H2(p)) neighbours",
                "Sphere packing: at most 2^n / 2^(n H2(p)) codewords fit, so the rate is capped at 1 - H2(p)",
                "Capacity as the maximum of I(X;Y) over input distributions, and why the BSC's maximum is uniform",
                "H(Y|X) = H2(p) for a BSC whatever the input, so only H(Y) is left to maximise",
                "The erasure channel: the receiver knows which uses were lost, so C = 1 - p",
                "Blahut-Arimoto for channels with no closed form, and why it starts from a uniform input",
                "The theorem is asymptotic, non-constructive, and assumes the uses are independent",
            ],
            "read": [
                {
                    "title": "How much a noisy wire can carry",
                    "minutes": 14,
                    "body": r'''
The ridge station's data comes down a radio hop that flips about one bit in a hundred. The
first repair anyone reaches for is repetition: send each bit three times and take the
majority. A word is then wrong only if two or three of its three copies flipped, which is
$3 (0.01)^2 (0.99) + (0.01)^3 = 2.98 \times 10^{-4}$, and the price is that the link now
carries one useful bit for every three sent.

```python
from math import comb

q = 0.01
for n in (1, 3, 5, 7, 9):
    err = sum(comb(n, k) * q ** k * (1 - q) ** (n - k) for k in range(n // 2 + 1, n + 1))
    print(f"repeat {n}: rate {1 / n:.4f}, word error {err:.3e}")
```

The pattern in that table is the whole reason this module exists. Reliability improves,
the rate falls towards zero, and if those two are locked together then a perfectly reliable
link carries nothing at all. Everyone believed that until 1948. It is false, and the way to
see why is to count.

## Count the words a codeword can turn into

Send a block of $n$ bits through a channel that flips each one independently with
probability $p$. What arrives is the block with about $np$ positions flipped. How many
different blocks could arrive? Choose which $np$ positions flipped:
$\text{C}(n, np)$ of them, and that count has a familiar size.

```python
from math import comb, log2

p = 0.11
h2 = -(p * log2(p) + (1 - p) * log2(1 - p))
for n in (100, 1000, 10000):
    print(f"n={n:6d}: log2 C(n, {p}n) / n = {log2(comb(n, int(n * p))) / n:.6f}")
print(f"H2({p}) = {h2:.6f}")
```

The exponent per bit climbs to 0.4999, which is $H_2(p) = -p \log_2 p - (1-p)\log_2(1-p)$,
the entropy of one flip decision. That is module 1's count again: the sequences of flips
that actually happen number about $2^{n H_2(p)}$, out of $2^n$ possible flip patterns.

So each codeword arrives as one of about $2^{n H_2(p)}$ blocks — call that its noise ball.
For the decoder to name the codeword that was sent, no two balls may overlap. The whole
output space holds $2^n$ blocks. Disjoint sets of size $2^{n H_2(p)}$ inside a space of
size $2^n$ number at most

$$\frac{2^n}{2^{n H_2(p)}} = 2^{n (1 - H_2(p))}$$

and that is how many codewords there is room for. Taking the logarithm and dividing by $n$,
the rate cannot exceed $1 - H_2(p)$ bits per use. At $p = 0.11$ that is 0.5001: the ball
count for $n = 1000$ says at most $2^{500}$ codewords fit into $2^{1000}$ blocks. The
number is positive, and it does not shrink as $n$ grows. Reliability and rate were never
locked together; the repetition code was a poor way to spend the room.

## The same number, from mutual information

The packing count is the picture. The definition that generalises is

$$C = \max_{p(x)} I(X;Y)$$

the largest number of bits about the input that a single output can carry, over every way
of driving the channel. For the binary symmetric channel the maximisation is short. Write
$I(X;Y) = H(Y) - H(Y | X)$. Given the input bit, the output is that bit flipped with
probability $p$, so $H(Y | X = x) = H_2(p)$ for either $x$, and the average is $H_2(p)$
no matter what the input distribution is. That leaves $H(Y)$, which is at most 1 bit and
reaches 1 when the output is uniform — which a uniform input achieves, since the channel is
symmetric. So

$$C = 1 - H_2(p)$$

the same number the ball count produced, now with the maximising input identified as well.
Shannon's theorem adds the two halves the count could not supply: every rate below $C$ is
achievable with error going to zero as $n$ grows, and no rate above $C$ is.

The erasure channel is the case where the arithmetic is even shorter. It delivers the bit
intact with probability $1 - p$ and otherwise delivers a mark saying "this one was lost".
The receiver knows *which* uses failed, so the surviving fraction $1 - p$ of them are
perfect and the rest carry nothing: $C = 1 - p$. That the receiver knows is the whole
difference between an erasure and a flip, and it is worth an enormous amount.

## The mistake: reading the capacity off the error rate

The tempting answer for a channel that corrupts a fraction $p$ of the bits is that it
carries $1 - p$. It has the right shape, it is right for the erasure channel, and it is
wrong for the flipping one.

```text
p       1 - p     1 - H2(p)
0.01    0.9900    0.9192
0.11    0.8900    0.5001
0.50    0.5000    0.0000
0.90    0.1000    0.5310
1.00    0.0000    1.0000
```

At one flip in a hundred the true capacity is 0.9192, not 0.99 — an eighth of the link is
gone, not a hundredth, because the receiver does not know *which* bit was flipped and has
to be given enough redundancy to find out. At $p = 0.5$ both agree that something has ended,
but for different reasons, and the rows underneath settle it: a channel that flips 90% of
its bits carries 0.53 bits a use, and one that flips *every* bit is perfect. Invert the
output and it is a noiseless wire. Any formula that sends the capacity to zero as $p$ goes
to 1 has confused "damaged" with "unpredictable", and $H_2$ is the function that knows the
difference, because $H_2(1) = 0$.

## When there is no closed form

Most channels have no expression like $1 - H_2(p)$. The Z channel — input 0 always arrives,
input 1 arrives as 0 with probability $p$ — is asymmetric, and its optimal input is not
uniform. Blahut and Arimoto's algorithm finds the maximum by alternating: given the current
input distribution $r$, form the reverse channel $q(x | y)$ by Bayes, then move $r$
towards the distribution that best matches it, and repeat.

```python
import math


def mutual_information_of(px, W):
    n, m = len(px), len(W[0])
    py = [math.fsum(px[i] * W[i][j] for i in range(n)) for j in range(m)]
    total = 0.0
    for i in range(n):
        for j in range(m):
            if px[i] > 0 and W[i][j] > 0 and py[j] > 0:
                total += px[i] * W[i][j] * math.log2(W[i][j] / py[j])
    return total


def capacity(W, iterations=2000, tol=1e-13):
    n, m = len(W), len(W[0])
    r = [1.0 / n] * n
    previous = -1.0
    for _ in range(iterations):
        py = [math.fsum(r[i] * W[i][j] for i in range(n)) for j in range(m)]
        logt = []
        for i in range(n):
            s = 0.0
            for j in range(m):
                if W[i][j] > 0 and r[i] > 0:
                    s += W[i][j] * math.log(r[i] * W[i][j] / py[j])
            logt.append(s)
        t = [math.exp(v - max(logt)) for v in logt]
        z = math.fsum(t)
        r = [v / z for v in t]
        current = mutual_information_of(r, W)
        if abs(current - previous) < tol:
            break
        previous = current
    return mutual_information_of(r, W), r


p = 0.5
c, r = capacity([[1.0, 0.0], [p, 1.0 - p]])
closed = math.log2(1 + (1 - p) * p ** (p / (1 - p)))
print(f"Z channel p={p}: solver {c:.9f}, closed form {closed:.9f}")
print(f"best input: {[round(v, 4) for v in r]}")
```

The solver returns 0.321928, and the closed form
$\log_2(1 + (1-p) p^{p/(1-p)})$ returns 0.321928 as well. The optimal input is
$(0.6, 0.4)$, not $(0.5, 0.5)$: sending the reliable symbol more often is worth more than
keeping the input balanced. Starting the iteration from a uniform $r$ matters, because an
input given zero probability at the start stays at zero forever — the update multiplies by
$r_i$, so a ruled-out input can never argue its way back.

## Where capacity stops meaning what it sounds like

The theorem is asymptotic. "Every rate below $C$ is achievable" means: for any rate below
$C$ and any error target, *some* block length works. It does not say which, and the block
lengths involved can be enormous. Repetition-3 sits at rate 0.333 with error
$3 \times 10^{-4}$ on a channel of capacity 0.919; the theorem promises a code at rate 0.9
with error below $10^{-9}$, and says nothing about how to write one down. Shannon's proof
picks the codebook at random and shows the average is good, which proves existence without
exhibiting anything. Sixty years of coding theory is the constructive half of that
sentence, and the next module starts it.

The channel is also assumed memoryless: each use is independent of the last. Real links
fail in bursts — a fade, a scratch, a burst of interference — and a burst defeats a code
designed for scattered errors. The standard repair is interleaving: scramble the bit order
before coding and unscramble after, so a burst on the wire arrives as scattered errors at
the decoder. That does not raise the capacity of the physical channel; it makes the channel
the decoder sees resemble the one the code was designed for. And $C$ assumes you know the
channel: a decoder tuned for $p = 0.01$ running on a link that has drifted to $p = 0.1$
pays for the mismatch in exactly the way module 1 priced a wrong source model.

## What the lab asks for

The lab *What a noisy wire can carry* wants `binary_entropy`, the two simulators `bsc` and
`bec`, `mutual_information_of`, `capacity` by Blahut-Arimoto, and the two closed forms.
Every simulator takes a seed and is asserted to reproduce its output exactly, because a
coding check whose channel is unseeded is a check that flakes. The solver is held to nine
decimal places against $1 - H_2(p)$, against $1 - p$, and against the Z channel's closed
form — a formula nobody derives by inspection, which is why the numerical solver is worth
having.
''',
                },
            ],
            "quiz": {
                "title": "What the number C actually says",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A link flips one bit in a hundred. What fraction of its throughput survives, and why?",
                        "opts": [
                            "0.99, since one use in a hundred is destroyed and the rest arrive intact",
                            "0.9192, because the receiver must be told which use was flipped, not merely that one was",
                            "0.9192, because a flipped bit still carries half of the information it was sent with",
                            "0.98, since a flip costs the bit that was sent and the bit needed to repair it",
                        ],
                        "a": 1,
                        "why": r"""
$C = 1 - H_2(0.01) = 1 - 0.0808 = 0.9192$. The gap between that and 0.99 is the cost of
*locating* the damage. A flip carries no flag: every received bit looks the same whether it
was corrupted or not, so the code has to leave enough room to identify which positions moved.
The erasure channel is the version where the receiver is told, and there the answer really is
$1 - p$. The difference between those two channels at the same $p$ is the whole content of
the $H_2$ in the formula.
                        """,
                        "whys": [
                            r"""
$1 - p$ is the capacity of the *erasure* channel, where the receiver sees a mark in place of
the lost bit. A flip arrives looking exactly like a correct bit, so the decoder cannot skip
it — it has to spend redundancy finding it. Applying the erasure answer to a flipping channel
is the single most common error in this subject, and it always overestimates.
                            """,
                            r"""
Right, and the sanity check on any candidate formula is the $p = 1$ row: a channel that flips
every bit is noiseless, because inverting the output restores it perfectly. $1 - H_2(p)$ gives
1 there; $1 - p$ gives 0. Only a formula built from the entropy of the flip decision can see
that a perfectly predictable channel is not a damaged one.
                            """,
                            r"""
There is no partial credit for a flipped bit, and no sense in which it carries half of
anything — a single use of a BSC carries $1 - H_2(p)$ bits on average, and that average is
over all uses, corrupted or not. The number 0.9192 is right and the reason is not; the cost
comes from locating the damage across a block, not from a fraction of a bit surviving inside
each flip.
                            """,
                            r"""
"One bit lost plus one bit to repair it" gives $1 - 2p$, an arithmetic that would hit zero at
$p = 0.5$ by coincidence and go negative after. Repair is not a per-error charge; it is a
block-level redundancy whose size is governed by how many error patterns the decoder has to
distinguish, and that count is $2^{n H_2(p)}$.
                            """,
                        ],
                    },
                    {
                        "q": "Why does the sphere-packing count cap the number of codewords at 2^(n(1 - H2(p)))?",
                        "opts": [
                            "Because each codeword's noise ball holds about 2^(n H2(p)) blocks and the balls must not overlap",
                            "Because a code of length n has 2^n codewords and each error pattern removes 2^(n H2(p)) of them",
                            "Because the decoder must store one entry per codeword and 2^(n H2(p)) is the table it can hold",
                            "Because H2(p) of every block is destroyed by noise, leaving 1 - H2(p) of each block usable",
                        ],
                        "a": 0,
                        "why": r"""
A transmitted block arrives with about $np$ positions flipped, and the number of flip
patterns that actually occur is about $\text{C}(n, np) \approx 2^{n H_2(p)}$ — the same typical-set
count as module 1, applied to the noise instead of the source. Those are the blocks the
decoder might see for one codeword. If two codewords' balls shared a block, that block could
not be decoded. Disjoint sets of size $2^{n H_2(p)}$ inside a space of $2^n$ number at most
their ratio, and the logarithm of the ratio, over $n$, is $1 - H_2(p)$.
                        """,
                        "whys": [
                            r"""
Right, and the pleasing part is that it is module 1's argument with the roles moved: there,
$2^{nH}$ counted the source sequences that plausibly happen; here it counts the error patterns
that plausibly happen. Both come from the same observation that a product of $n$ probabilities
concentrates, and both turn into a rate by taking a logarithm and dividing by $n$.
                            """,
                            r"""
A code does not start with $2^n$ codewords and lose some; $2^n$ is the size of the whole block
space, and the code is a subset chosen from it. The count is about how many subsets members can
be packed with disjoint neighbourhoods, which is a packing question rather than a subtraction.
                            """,
                            r"""
Decoder memory is a real engineering constraint and it has nothing to do with this bound. The
limit holds for a decoder with unlimited storage, because it comes from the geometry of the
block space: two codewords whose noise balls overlap are ambiguous however much memory is
available to look at them.
                            """,
                            r"""
Nothing is destroyed inside a block. Every one of the $n$ bits arrives; some are wrong, and
the receiver cannot tell which. Framing it as a per-block fraction of surviving bits also
predicts the wrong thing at $p = 1$, where no bit "survives" and yet the channel is perfect.
                            """,
                        ],
                    },
                    {
                        "q": "Repetition-3 on a channel with p = 0.01 gives rate 0.333 and word error 3e-4, and the capacity is 0.919. What does the coding theorem add to that?",
                        "opts": [
                            "That repetition can reach rate 0.919 if the block length is made large enough",
                            "That some code of rate 0.9 has error below any target you name, for some block length",
                            "That every code of rate below 0.919 has error below 3e-4 at every block length",
                            "That the error of any rate-0.333 code is at least 3e-4, so repetition is optimal there",
                        ],
                        "a": 1,
                        "why": r"""
The theorem is an existence statement with two quantifiers in a particular order: for any rate
$R < C$ and any error target $\epsilon$, there is a block length $n$ and a code of rate $R$ and
length $n$ whose error is under $\epsilon$. It does not name the code, does not bound $n$, and
says nothing about any *particular* code. Repetition is a specific, and bad, code: its rate
goes to zero as its reliability improves, which is exactly the trade the theorem says is
unnecessary. The theorem's other half, the converse, is that no rate above $C$ can have error
going to zero.
                        """,
                        "whys": [
                            r"""
Repetition-$n$ has rate $1/n$ by construction, so its rate goes down as $n$ goes up and it
approaches 0, never 0.919. It is the standard example of a code that is nowhere near capacity
at any length. What the theorem says is that better codes exist, not that this one improves.
                            """,
                            r"""
Right, and the order of the quantifiers is what makes the statement both strong and modest: the
rate and the error target are chosen first, the block length after. That is why the result is
compatible with every short code being poor, and why turning it into practice took decades of
explicit constructions.
                            """,
                            r"""
The theorem says nothing about every code — most codes of rate below capacity are terrible, and
a code that maps every message to the same block has rate below $C$ and error near 1. The
claim is existential, and reading an existential statement as a universal one is what makes it
sound like it should have been useful immediately.
                            """,
                            r"""
Repetition-3 is nowhere near optimal at rate 1/3. Better rate-1/3 codes on this channel have
error orders of magnitude smaller, and the packing count is what says so: at rate 1/3 there is
room for far more separation between codewords than repetition uses. The theorem gives no
lower bound on error at rates below capacity.
                            """,
                        ],
                    },
                    {
                        "q": "Blahut-Arimoto starts from a uniform input distribution. What goes wrong if it starts with one input at probability zero?",
                        "opts": [
                            "The reverse channel becomes undefined, and the iteration raises on the first step",
                            "The update multiplies by r_i, so a zeroed input stays at zero and can never be chosen",
                            "The algorithm converges to the same answer more slowly, since it has fewer inputs to move",
                            "The mutual information comes out negative, since the input distribution no longer sums to 1",
                        ],
                        "a": 1,
                        "why": r"""
The update forms $\log t_i = \sum_j W(j | i) \log (r_i W(j | i) / p_Y(j))$ and then
normalises $\exp(\log t_i)$. With $r_i = 0$ the whole term is $-\infty$, $\exp$ of it is 0, and
the input is zero again next round — the iteration cannot resurrect it. If that input happened
to be in the optimal support, the solver converges confidently to a number below the true
capacity, with no sign that anything went wrong. Uniform is the safe start because it rules
nothing out.
                        """,
                        "whys": [
                            r"""
Nothing raises. The zero terms are guarded — an input with $r_i = 0$ contributes nothing to
$p_Y$, and the code skips terms where $W$ or $r$ is zero — so the iteration runs happily and
returns a number. A crash would be far kinder than what actually happens, which is a plausible
wrong answer.
                            """,
                            r"""
Right, and the failure is silent, which is what makes it worth a comment in the code. The
returned value is a genuine mutual information for a genuine input distribution, so every
internal consistency check passes; it is merely not the maximum. Comparing against a closed
form on a channel that has one is the only cheap way to notice.
                            """,
                            r"""
It is not a matter of speed. The zeroed input is gone permanently, so if the true optimum puts
mass on it the algorithm converges to a strictly smaller value and stays there however long it
runs. On the Z channel, whose optimal input is $(0.6, 0.4)$, zeroing either input gives a
capacity of 0.
                            """,
                            r"""
Mutual information cannot be negative, and normalising after the exponential keeps the
distribution summing to 1 at every step regardless of where it started. The invariant holds;
what fails is the maximisation, and that failure leaves every invariant intact.
                            """,
                        ],
                    },
                    {
                        "q": "A satellite link loses data in bursts: it is clean for thousands of bits, then corrupts a hundred in a row. Why does interleaving help, and what does it not do?",
                        "opts": [
                            "It lowers the average error rate, though it cannot change the channel's capacity",
                            "It makes a burst look like scattered errors, without changing the channel",
                            "It raises the capacity by spreading the noise energy across more uses of the channel",
                            "It converts the burst channel into an erasure channel, which has the higher capacity",
                        ],
                        "a": 1,
                        "why": r"""
Interleaving permutes the bit order before coding and undoes the permutation after reception,
so a run of a hundred adjacent errors on the wire lands as a hundred isolated errors spread
across many codewords. The codes in the next module correct scattered errors and are helpless
against a burst inside one block, so this is what lets them be used at all. The average error
rate is unchanged — the same bits are corrupted — and the physical channel's capacity is
whatever it was. Interleaving buys a match between the channel the decoder assumes and the
channel it gets.
                        """,
                        "whys": [
                            r"""
The average error rate is exactly what interleaving leaves alone: the same number of bits are
corrupted, in the same quantity, merely at different positions. What changes is their
distribution across codewords, and that matters because a code's guarantee is per block, not
per bit.
                            """,
                            r"""
Right, and the framing worth keeping is that interleaving is a modelling device rather than a
noise-reduction device. Every result in this module assumes a memoryless channel; a bursty link
is not one; interleaving is the standard way of making the assumption true enough for the
theory to apply to the link you actually have.
                            """,
                            r"""
There is no noise energy to spread — the errors are already there, and permuting the bits does
not remove any. Capacity is a property of the physical channel, and a permutation applied and
undone by the two ends cannot change what the wire does. A channel with memory has its own
capacity, and it is usually higher than the memoryless one with the same error rate, because
predictable noise is less costly than unpredictable noise.
                            """,
                            r"""
Interleaving produces no erasure marks. An erasure channel is one where the receiver is told
which uses were lost, and that information has to come from the physical layer — a demodulator
reporting low confidence, say. Shuffling bit positions tells the receiver nothing new about
which bits are wrong.
                            """,
                        ],
                    },
                    {
                        "q": "For a binary symmetric channel, I(X;Y) = H(Y) - H(Y|X). Why does that identity make the capacity easy to maximise?",
                        "opts": [
                            "Because H(Y|X) is H2(p) whatever the input is, so only H(Y) is left to maximise",
                            "Because H(Y|X) is zero for a symmetric channel, so the capacity is H(Y) at its largest",
                            "Because H(Y) is fixed at 1 bit for a binary output, so only H(Y|X) has to be minimised",
                            "Because the identity is symmetric, so maximising over inputs is the same as over outputs",
                        ],
                        "a": 0,
                        "why": r"""
Condition on a particular input and the output is that bit flipped with probability $p$, whose
entropy is $H_2(p)$ — the same for input 0 and input 1, so the average over any input
distribution is $H_2(p)$ and the second term does not depend on the thing being maximised. The
maximisation collapses to $\max H(Y)$, which for a binary output is at most 1 bit and is
achieved when the output is uniform. A uniform input makes it so, by symmetry. Hence
$C = 1 - H_2(p)$, with the maximising input identified as a by-product.
                        """,
                        "whys": [
                            r"""
Right, and it is worth noticing which property is doing the work: the second term being
input-independent comes from every row of the channel matrix being a permutation of the same
numbers. The Z channel's rows are not, its $H(Y | X)$ does depend on the input, and that is
precisely why it needs a numerical solver.
                            """,
                            r"""
$H(Y | X)$ is zero only for a noiseless channel, where the output is determined by the
input. Here it is $H_2(p)$, which is the whole of the loss — at $p = 0.11$ it is 0.4999 bits,
half the channel. If it were zero the capacity would be 1 for every $p$, which would make the
noise free.
                            """,
                            r"""
$H(Y)$ is at most 1 for a binary output but is not fixed at 1: an input distribution of
$(0.9, 0.1)$ through a BSC gives an output distribution near $(0.83, 0.17)$ and an $H(Y)$ of
about 0.66. Maximising it is exactly the part of the problem that the input distribution
controls, so treating it as a constant removes the only free variable.
                            """,
                            r"""
The identity $I = H(Y) - H(Y | X)$ has a mirror image, $I = H(X) - H(X | Y)$, and the
symmetry of mutual information is real. But the maximisation is over input distributions in
both forms, and the mirror version is harder here, because $H(X | Y)$ depends on the input
in a way $H(Y | X)$ does not.
                            """,
                        ],
                    },
                ],
            },
            "blanks": {
                "title": "Mutual information and the capacity solver",
                "minutes": 9,
                "caption": "channel.py — four decisions removed",
                "lang": "python",
                "brief": r"""
Both functions are the same two tables read in different directions: the input distribution
pushed forwards through the channel, and the channel read back against it. Fill the holes,
then read the comment on the starting distribution, which is the one line that decides
whether the solver can find the answer at all.
""",
                "listing": """import math


def mutual_information_of(px, W):
    \"\"\"I(X; Y) in bits for input distribution px through channel matrix W.\"\"\"
    n, m = len(px), len(W[0])
    py = [math.fsum(___ for i in range(n)) for j in range(m)]
    total = 0.0
    for i in range(n):
        for j in range(m):
            if px[i] <= 0 or W[i][j] <= 0 or py[j] <= 0:
                continue
            total += px[i] * W[i][j] * math.log2(___)
    return total


def capacity(W, iterations=2000, tol=1e-13):
    \"\"\"Blahut-Arimoto: alternate the input distribution against the reverse channel.\"\"\"
    n, m = len(W), len(W[0])
    r = [___] * n                    # an input that starts at zero can never come back
    previous = -1.0
    for _ in range(iterations):
        py = [math.fsum(r[i] * W[i][j] for i in range(n)) for j in range(m)]
        logt = []
        for i in range(n):
            s = 0.0
            for j in range(m):
                if W[i][j] > 0 and r[i] > 0:
                    s += ___ * math.log(r[i] * W[i][j] / py[j])
            logt.append(s)
        t = [math.exp(v - max(logt)) for v in logt]
        z = math.fsum(t)
        r = [v / z for v in t]
        current = mutual_information_of(r, W)
        if abs(current - previous) < tol:
            break
        previous = current
    return mutual_information_of(r, W), r
""",
                "blanks": [
                    {
                        "prompt": "The output distribution is the input distribution pushed through the channel. What is summed over the inputs?",
                        "hole": "?",
                        "opts": ["px[i] * W[i][j]", "W[i][j]", "px[i]", "px[i] + W[i][j]"],
                        "a": 0,
                        "why": "Output j happens when input i was sent and the channel produced j, so the joint probability of that pair is px[i] times W[i][j], and marginalising means adding those over i. This is the same marginal-from-a-joint step as the entropy module, written with the joint factored.",
                        "whys": [
                            "Output j happens when input i was sent and the channel produced j, so the joint probability of that pair is px[i] times W[i][j], and marginalising means adding those over i. This is the same marginal-from-a-joint step as the entropy module, written with the joint factored.",
                            "Adding a column of the channel matrix ignores how often each input is actually sent, so a rarely used input counts as much as a common one. On any asymmetric channel the resulting py does not even sum to 1.",
                            "Summing the input probabilities gives 1 for every output, so py comes out as a list of ones and every logarithm in the next loop is negative. The channel has been dropped from a calculation about the channel.",
                            "A sum rather than a product treats sending an input and the channel's response as alternatives instead of as a pair, and the result exceeds 1 for every output.",
                        ],
                    },
                    {
                        "prompt": "Each term compares what the output does when this input was sent against what it does on average. What is the ratio?",
                        "hole": "?",
                        "opts": ["W[i][j] / py[j]", "py[j] / W[i][j]", "px[i] / py[j]", "W[i][j] * py[j]"],
                        "a": 0,
                        "why": "I(X;Y) is the relative entropy from the joint to the product of the marginals, and the term inside the logarithm is p(y|x) over p(y). Knowing the input raised this output's probability from py[j] to W[i][j], and the logarithm of that lift is the information gained.",
                        "whys": [
                            "I(X;Y) is the relative entropy from the joint to the product of the marginals, and the term inside the logarithm is p(y|x) over p(y). Knowing the input raised this output's probability from py[j] to W[i][j], and the logarithm of that lift is the information gained.",
                            "Inverting the ratio negates every term, so the function returns the negative of the mutual information. On the noiseless binary channel it would report -1 bit, and a capacity solver maximising it would drive the input to the least informative distribution it could find.",
                            "This ratio has an input probability on top and an output probability underneath, which is not a lift of anything: it compares how often an input is sent with how often an output appears, two quantities that need not even be about connected events.",
                            "A product where the definition calls for a ratio makes the term negative whenever both probabilities are small, and the total loses the property that it is zero exactly when the input and output are independent.",
                        ],
                    },
                    {
                        "prompt": "The iteration starts from some input distribution. Which start rules nothing out?",
                        "hole": "?",
                        "opts": ["1.0 / n", "0.0", "1.0", "1.0 / m"],
                        "a": 0,
                        "why": "A uniform distribution over the n inputs gives every input positive probability, and since the update multiplies by r[i], any input that starts at zero stays at zero forever. Starting uniform is what stops the solver from silently converging below the true capacity.",
                        "whys": [
                            "A uniform distribution over the n inputs gives every input positive probability, and since the update multiplies by r[i], any input that starts at zero stays at zero forever. Starting uniform is what stops the solver from silently converging below the true capacity.",
                            "Starting every input at zero rules out all of them at once: the output distribution is zero everywhere, the guard skips every term, and the solver reports a capacity of zero for every channel including a noiseless one.",
                            "Giving every input probability 1 is not a distribution at all — the mass sums to n — so the first output distribution is n times too large and every logarithm is shifted by log n.",
                            "Dividing by the number of outputs rather than inputs gives a distribution that sums to n over m. It is accidentally correct for a square channel matrix, which is exactly the case most tests use.",
                        ],
                    },
                    {
                        "prompt": "The update weights each output's contribution by how likely the channel makes it. Which factor is that?",
                        "hole": "?",
                        "opts": ["W[i][j]", "r[i]", "py[j]", "1.0"],
                        "a": 0,
                        "why": "The step maximises the average of log q(x|y) over the outputs this input actually produces, and the channel row W[i] is that distribution. Weighting by anything else averages over the wrong thing and the fixed point stops being the capacity.",
                        "whys": [
                            "The step maximises the average of log q(x|y) over the outputs this input actually produces, and the channel row W[i] is that distribution. Weighting by anything else averages over the wrong thing and the fixed point stops being the capacity.",
                            "The input probability is already inside the logarithm, and it does not vary with j — pulling it out as the weight makes every output count equally, which is the same defect as using 1.0 with an extra factor in front.",
                            "The output marginal weights each output by how often it appears overall rather than by how often this input produces it, which erases the difference between the inputs and drives the iteration towards a uniform answer on every channel.",
                            "An unweighted sum treats an output the channel almost never produces as equal in importance to the one it almost always produces. On the Z channel it returns 0.5 for the optimal input rather than 0.6.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "What a noisy wire can carry",
                "runtime": "python",
                "minutes": 70,
                "brief": r'''
Two simulators, one measurement and one solver.

**`binary_entropy(p)`** — `H2(p)` in bits, with `H2(0) = H2(1) = 0`. Raise
`ValueError` outside `[0, 1]`.

**`bsc(bits, p, seed=0)`** — the binary symmetric channel. `bits` is a string of
`0` and `1`. Build `random.Random(seed)` and draw `rng.random()` **once per bit, in
order**; flip the bit when the draw is below `p`. Returns a string. Raise
`ValueError` for a character other than `0` or `1`, or a `p` outside `[0, 1]`.

```text
bsc("0000", 0.0, 7)   -> "0000"
bsc("1010", 1.0, 3)   -> "0101"
bsc("0" * 20, 0.5, 7) -> "11010110111110110001"
```

**`bec(bits, p, seed=0)`** — the erasure channel, same draw discipline, but a lost
bit becomes `?` rather than flipping.

```text
bec("0" * 20, 0.5, 7) -> "??0?0??0?????0??000?"
```

**`mutual_information_of(px, W)`** — `px` is a list of input probabilities and `W` a
list of rows, one per input, each a distribution over the outputs. Returns
`I(X; Y)` in bits. Raise `ValueError` when the lengths disagree, a row is ragged, or
a row or `px` is not a distribution to within `1e-9`.

**`capacity(W, iterations=2000, tol=1e-13)`** — Blahut-Arimoto. Returns
`(C, px)`: the capacity in bits per use and the input distribution that achieves it.
Start from a uniform `px` — an input that begins at zero can never re-enter, since
the update multiplies by it. Stop when the mutual information stops moving by `tol`.

**`bsc_capacity(p)`** — `1 - H2(p)`. **`bec_capacity(p)`** — `1 - p`. Both raise
`ValueError` outside `[0, 1]`.

Standard library only; `math` and `random` are what you need. The solver is checked
to nine decimal places against both closed forms and against the Z channel's
`log2(1 + (1-p) * p**(p/(1-p)))`, and the simulators are checked for exact
reproduction from a seed.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random


def binary_entropy(p):
    """H2(p) in bits."""
    # your code here


def bsc(bits, p, seed=0):
    """The binary symmetric channel: each bit flipped with probability p."""
    # your code here


def bec(bits, p, seed=0):
    """The binary erasure channel: each bit replaced by `?` with probability p."""
    # your code here


def mutual_information_of(px, W):
    """I(X; Y) in bits for an input distribution through a channel matrix."""
    # your code here


def capacity(W, iterations=2000, tol=1e-13):
    """(capacity in bits per use, the input distribution that achieves it)."""
    # your code here


def bsc_capacity(p):
    """The closed form for the binary symmetric channel."""
    # your code here


def bec_capacity(p):
    """The closed form for the binary erasure channel."""
    # your code here


print(binary_entropy(0.11))
print(bsc("0" * 20, 0.5, 7))
print(capacity([[0.89, 0.11], [0.11, 0.89]]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random


def _prob(p, what):
    if isinstance(p, bool) or not isinstance(p, (int, float)):
        raise ValueError(f"{what} must be a number, got {p!r}")
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"{what} = {p!r} is not a probability")
    return float(p)


def binary_entropy(p):
    """H2(p) in bits."""
    p = _prob(p, "p")
    if p in (0.0, 1.0):
        return 0.0            # a certain outcome carries nothing, either way round
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def _draws(bits, p, seed):
    p = _prob(p, "p")
    if not isinstance(bits, str):
        raise ValueError("bits must be a string of 0 and 1")
    rng = random.Random(seed)
    for ch in bits:
        if ch not in "01":
            raise ValueError(f"{ch!r} is not a bit")
        yield ch, rng.random() < p


def bsc(bits, p, seed=0):
    """The binary symmetric channel: each bit flipped with probability p."""
    return "".join(("1" if ch == "0" else "0") if hit else ch for ch, hit in _draws(bits, p, seed))


def bec(bits, p, seed=0):
    """The binary erasure channel: each bit replaced by `?` with probability p."""
    return "".join("?" if hit else ch for ch, hit in _draws(bits, p, seed))


def _check_matrix(px, W):
    if not W or not W[0]:
        raise ValueError("an empty channel carries nothing")
    if len(px) != len(W):
        raise ValueError(f"{len(px)} input probabilities for {len(W)} channel rows")
    if abs(math.fsum(px) - 1.0) > 1e-9 or any(v < 0 for v in px):
        raise ValueError("the input distribution does not sum to 1")
    m = len(W[0])
    for i, row in enumerate(W):
        if len(row) != m:
            raise ValueError(f"row {i} has {len(row)} outputs, the first has {m}")
        if abs(math.fsum(row) - 1.0) > 1e-9 or any(v < 0 for v in row):
            raise ValueError(f"channel row {i} is not a distribution")
    return m


def mutual_information_of(px, W):
    """I(X; Y) in bits for an input distribution through a channel matrix."""
    m = _check_matrix(px, W)
    n = len(px)
    py = [math.fsum(px[i] * W[i][j] for i in range(n)) for j in range(m)]
    total = 0.0
    for i in range(n):
        for j in range(m):
            if px[i] <= 0 or W[i][j] <= 0 or py[j] <= 0:
                continue
            total += px[i] * W[i][j] * math.log2(W[i][j] / py[j])
    return total


def capacity(W, iterations=2000, tol=1e-13):
    """(capacity in bits per use, the input distribution that achieves it)."""
    n = len(W)
    if n == 0:
        raise ValueError("an empty channel carries nothing")
    m = _check_matrix([1.0 / n] * n, W)
    r = [1.0 / n] * n     # uniform: an input starting at zero can never re-enter
    previous = -1.0
    for _ in range(iterations):
        py = [math.fsum(r[i] * W[i][j] for i in range(n)) for j in range(m)]
        logt = []
        for i in range(n):
            s = 0.0
            for j in range(m):
                if W[i][j] > 0 and r[i] > 0 and py[j] > 0:
                    s += W[i][j] * math.log(r[i] * W[i][j] / py[j])
            logt.append(s)
        shift = max(logt)
        t = [math.exp(v - shift) for v in logt]
        z = math.fsum(t)
        r = [v / z for v in t]
        current = mutual_information_of(r, W)
        if abs(current - previous) < tol:
            break
        previous = current
    return mutual_information_of(r, W), r


def bsc_capacity(p):
    """The closed form for the binary symmetric channel."""
    return 1.0 - binary_entropy(p)


def bec_capacity(p):
    """The closed form for the binary erasure channel."""
    return 1.0 - _prob(p, "p")


print(binary_entropy(0.11))
print(bsc("0" * 20, 0.5, 7))
print(capacity([[0.89, 0.11], [0.11, 0.89]]))
'''}],
                "hints": [
                    "Draw exactly one random number per bit, before deciding anything else about that bit. A simulator that draws twice for some bits stops being reproducible from its seed.",
                    "`bsc` and `bec` differ only in what they do when the draw lands, so one generator of `(bit, hit)` pairs can serve both — and driving them with the same seed then makes the same uses fail.",
                    "In `mutual_information_of`, build the output marginal once before the double loop. Recomputing it inside makes the function cubic and changes nothing.",
                    "Subtract `max(logt)` before exponentiating in Blahut-Arimoto. The raw exponents are large and negative, and `math.exp` underflows to zero for all of them at once.",
                    "Check convergence on the mutual information rather than on the input distribution: it settles first, and it is the quantity being maximised.",
                ],
                "tests": [
                    {"name": "binary_entropy at the ends and in the middle", "code": r'''
assert binary_entropy(0.0) == 0.0 and binary_entropy(1.0) == 0.0, \
    "a channel that never flips and one that always flips are both certain"
assert abs(binary_entropy(0.5) - 1.0) < 1e-12, f"got {binary_entropy(0.5)!r}"
assert abs(binary_entropy(0.11) - 0.499915958164528) < 1e-12, f"got {binary_entropy(0.11)!r}"
assert abs(binary_entropy(0.01) - 0.08079313589591118) < 1e-12, f"got {binary_entropy(0.01)!r}"
assert abs(binary_entropy(0.25) - binary_entropy(0.75)) < 1e-12, "H2 is symmetric about 0.5"
for _bad in [-0.1, 1.1, 2]:
    try:
        binary_entropy(_bad)
        assert False, f"binary_entropy({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "the symmetric channel reproduces from its seed", "code": r'''
assert bsc("0000", 0.0, 7) == "0000", "p = 0 is a wire"
assert bsc("1010", 1.0, 3) == "0101", "p = 1 inverts every bit"
assert bsc("0" * 20, 0.5, 7) == "11010110111110110001", f"got {bsc('0' * 20, 0.5, 7)!r}"
assert bsc("0" * 20, 0.5, 7) == bsc("0" * 20, 0.5, 7), "the same seed must give the same run"
assert bsc("0" * 20, 0.5, 7) != bsc("0" * 20, 0.5, 8), "a different seed must give a different run"
assert bsc("", 0.5, 1) == "", "an empty transmission is empty"
_src = "01" * 10000
_got = bsc(_src, 0.11, 4)
_flips = sum(1 for _a, _b in zip(_src, _got) if _a != _b)
assert abs(_flips / len(_src) - 0.11) < 0.01, \
    f"flipped {_flips / len(_src):.4f} of 20000 bits, expected about 0.11"
for _bad in [("012", 0.5, 1), ("01", 1.5, 1), ("01", -0.1, 1)]:
    try:
        bsc(*_bad)
        assert False, f"bsc{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "the erasure channel marks what it loses", "code": r'''
assert bec("1010", 0.0, 7) == "1010", "p = 0 delivers everything"
assert bec("1010", 1.0, 7) == "????", "p = 1 delivers nothing"
assert bec("0" * 20, 0.5, 7) == "??0?0??0?????0??000?", f"got {bec('0' * 20, 0.5, 7)!r}"
_src = "0110" * 5000
_got = bec(_src, 0.3, 9)
assert abs(_got.count("?") / len(_src) - 0.3) < 0.01, \
    f"erased {_got.count('?') / len(_src):.4f}, expected about 0.3"
assert all(_b == "?" or _b == _a for _a, _b in zip(_src, _got)), \
    "a bit that is not erased must arrive unchanged — this channel never flips"
assert [i for i, c in enumerate(bec("0" * 20, 0.5, 7)) if c == "?"] == \
       [i for i, (a, b) in enumerate(zip("0" * 20, bsc("0" * 20, 0.5, 7))) if a != b], \
    "one draw per bit means the same seed picks the same uses in both channels"
for _bad in [("0?0", 0.5, 1), ("01", 1.5, 1)]:
    try:
        bec(*_bad)
        assert False, f"bec{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "mutual information on channels you can check by hand", "code": r'''
assert abs(mutual_information_of([0.5, 0.5], [[1.0, 0.0], [0.0, 1.0]]) - 1.0) < 1e-12, \
    "a noiseless binary channel carries a whole bit"
assert abs(mutual_information_of([0.5, 0.5], [[0.5, 0.5], [0.5, 0.5]])) < 1e-12, \
    "a channel whose output ignores its input carries nothing"
_bsc = [[0.89, 0.11], [0.11, 0.89]]
assert abs(mutual_information_of([0.5, 0.5], _bsc) - 0.500084041835472) < 1e-9, \
    f"got {mutual_information_of([0.5, 0.5], _bsc)!r}"
assert mutual_information_of([0.9, 0.1], _bsc) < mutual_information_of([0.5, 0.5], _bsc), \
    "a lopsided input carries less through a symmetric channel"
assert abs(mutual_information_of([1.0, 0.0], _bsc)) < 1e-12, \
    "an input that never varies carries nothing whatever the channel does"
for _bad in [([0.5], _bsc), ([0.5, 0.4], _bsc), ([0.5, 0.5], [[0.5, 0.5], [0.5, 0.4]]),
             ([0.5, 0.5], [[1.0, 0.0], [0.5, 0.25, 0.25]])]:
    try:
        mutual_information_of(*_bad)
        assert False, f"mutual_information_of{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "the solver reproduces the symmetric channel's closed form", "code": r'''
for _p in (0.0, 0.01, 0.05, 0.11, 0.25, 0.4, 0.5, 0.75, 0.99, 1.0):
    _c, _px = capacity([[1 - _p, _p], [_p, 1 - _p]])
    _want = bsc_capacity(_p)
    assert abs(_c - _want) < 1e-9, f"p={_p}: solver gave {_c!r}, closed form {_want!r}"
    assert abs(_px[0] - 0.5) < 1e-6, f"p={_p}: the best input is uniform, solver said {_px!r}"
assert abs(bsc_capacity(0.01) - 0.9192068641040888) < 1e-12, "one flip in a hundred costs 0.081 bits"
assert abs(bsc_capacity(1.0) - 1.0) < 1e-12, \
    "a channel that flips every bit is noiseless — invert the output"
assert bsc_capacity(0.5) < 1e-12, "a coin flip carries nothing"
'''},
                    {"name": "the erasure channel loses exactly what it erases", "code": r'''
for _p in (0.0, 0.1, 0.3, 0.5, 0.9, 1.0):
    _W = [[1 - _p, 0.0, _p], [0.0, 1 - _p, _p]]
    _c, _px = capacity(_W)
    assert abs(_c - bec_capacity(_p)) < 1e-9, \
        f"p={_p}: solver gave {_c!r}, closed form {bec_capacity(_p)!r}"
assert abs(bec_capacity(0.11) - 0.89) < 1e-12
assert bec_capacity(0.11) > bsc_capacity(0.11), (
    "at the same p an erasure costs less than a flip, because the receiver is told "
    "which use was lost")
for _bad in [-0.1, 1.5]:
    try:
        bec_capacity(_bad)
        assert False, f"bec_capacity({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "the Z channel, where the best input is not uniform", "code": r'''
import math as _math

for _p in (0.1, 0.3, 0.5, 0.7):
    _c, _px = capacity([[1.0, 0.0], [_p, 1.0 - _p]])
    _want = _math.log2(1 + (1 - _p) * _p ** (_p / (1 - _p)))
    assert abs(_c - _want) < 1e-9, f"p={_p}: solver gave {_c!r}, closed form {_want!r}"
    assert abs(sum(_px) - 1.0) < 1e-9, f"the returned input distribution must sum to 1: {_px!r}"
    assert _px[0] > 0.5, f"p={_p}: the reliable input should be favoured, got {_px!r}"
_c5, _px5 = capacity([[1.0, 0.0], [0.5, 0.5]])
assert abs(_c5 - 0.32192809488736235) < 1e-9, f"got {_c5!r}"
assert abs(_px5[0] - 0.6) < 1e-6 and abs(_px5[1] - 0.4) < 1e-6, \
    f"the optimal input at p=0.5 is (0.6, 0.4), got {_px5!r}"
'''},
                    {"name": "capacity is a ceiling no input distribution beats", "code": r'''
import math as _math
import random as _random

_rng = _random.Random(411)
for _trial in range(25):
    _n = _rng.randrange(2, 5)
    _m = _rng.randrange(2, 5)
    _W = []
    for _ in range(_n):
        _row = [_rng.random() + 1e-6 for _ in range(_m)]
        _s = sum(_row)
        _W.append([v / _s for v in _row])
    _c, _best = capacity(_W)
    for _try in range(8):
        _px = [_rng.random() + 1e-9 for _ in range(_n)]
        _t = sum(_px)
        _px = [v / _t for v in _px]
        assert mutual_information_of(_px, _W) <= _c + 1e-9, (
            f"input {_px!r} carried {mutual_information_of(_px, _W)!r} through a channel "
            f"whose capacity the solver put at {_c!r}")
    assert abs(mutual_information_of(_best, _W) - _c) < 1e-9, \
        "the returned distribution must be the one that achieves the returned capacity"
assert abs(capacity([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])[0]
           - _math.log2(3)) < 1e-9, "three symbols, no noise, log2(3) bits a use"
assert capacity([[0.5, 0.5], [0.5, 0.5]])[0] < 1e-12, "a useless channel has zero capacity"
'''},
                    {"name": "a simulated link measures the capacity it was given", "code": r'''
import math as _math
import random as _random

_rng = _random.Random(19)
_src = "".join(_rng.choice("01") for _ in range(60000))
_got = bsc(_src, 0.11, 4)
_joint = {}
for _a, _b in zip(_src, _got):
    _joint[(_a, _b)] = _joint.get((_a, _b), 0) + 1
_j = {k: v / len(_src) for k, v in _joint.items()}
_px, _py = {}, {}
for (_x, _y), _v in _j.items():
    _px[_x] = _px.get(_x, 0.0) + _v
    _py[_y] = _py.get(_y, 0.0) + _v


def _H(_d):
    return -sum(_v * _math.log2(_v) for _v in _d.values() if _v > 0)


_measured = _H(_px) + _H(_py) - _H(_j)
assert abs(_measured - bsc_capacity(0.11)) < 0.01, (
    f"60000 uses of a p=0.11 channel measured I = {_measured!r}, "
    f"against a capacity of {bsc_capacity(0.11)!r}")
assert bsc("0" * 100, 0.11, 4) == bsc("0" * 100, 0.11, 4), \
    "the measurement is only repeatable because the channel is seeded"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Linear block codes and syndrome decoding",
            "summary": "Locating an error is a counting problem, and the count says three parity bits protect four data bits.",
            "concepts": [
                "Detecting an error is one bit of news; locating it among n positions needs n+1 outcomes",
                "The Hamming bound 2^r >= k + r + 1, and (7,4) as the case where it is tight",
                "A generator matrix G, its null space H, and the syndrome H times the received word",
                "The syndrome of a corrupted word is the column of H at the error position, and nothing else",
                "Minimum distance d corrects (d-1)/2 errors and detects d-1, and you choose which",
                "Coset leaders: the lightest error vector for each syndrome, found weight by weight",
                "Where it breaks: two errors in one block, bursts, and the distance from capacity",
            ],
            "read": [
                {
                    "title": "A syndrome names the bit that moved",
                    "minutes": 14,
                    "body": r'''
A memory chip holds the nibble `1011`. Add a parity bit so the five stored bits have an
even number of ones — `10111` — and a cosmic ray flips one of them. Read back `10101` and
the parity fails, so you know something is wrong. Which bit?

Any of the five. The parity check answered one question, and one question has two answers,
so it can separate "clean" from "damaged" and nothing more. To *repair* the word you need
to know which of five positions moved, and that is a different question with six answers:
no error, or an error in one of the five places.

## Count the answers you need

That comparison is the whole design. With $r$ parity bits you can ask $r$ independent
yes-or-no questions, so the result of the checks — call it the syndrome — is one of $2^r$
patterns. To locate a single error in a word of $n$ bits, the syndrome has to distinguish
$n + 1$ outcomes: clean, or damaged at position $1$ through $n$. So

$$2^r \ge n + 1 = k + r + 1$$

where $k = n - r$ is the number of data bits. This is the Hamming bound, and it is a count
of outcomes rather than an algebraic fact. Solve it for the smallest $r$ at each $k$:

```python
print(" k    r    n    rate")
for k in range(1, 12):
    r = 2
    while 2 ** r < k + r + 1:
        r += 1
    print(f"{k:<5}{r:<5}{k + r:<5}{k / (k + r):.4f}")
```

At $k = 4$ the bound reads $2^r \ge r + 5$, and $r = 3$ gives $8 \ge 8$ — tight, with no
syndrome pattern left over. Seven bits carry four of data and locate any single error, at a
rate of $4/7$. The rows where the bound is slack, like $k = 5$ needing $r = 4$ for
$16 \ge 9$, are codes with syndromes going spare, and they are correspondingly less
efficient.

A code that meets the bound with equality is called *perfect*, and the phrase means
something exact: the spheres of radius 1 around the $2^k$ codewords tile the whole space of
$2^n$ words with nothing left over. For the $(7,4)$ code, $2^4 \times (1 + 7) = 128 = 2^7$.
That is module 4's sphere-packing count again, at a block length small enough to check by
hand and with the inequality closed.

## The matrices, and the one fact about syndromes

A linear code is a subspace. A generator matrix $G$ has $k$ rows of length $n$, and the
codewords are all the sums of subsets of those rows, taken over GF(2) where addition is
exclusive-or. A parity-check matrix $H$ has $n - k$ rows spanning the orthogonal
complement, so $Gv^{T} = 0$ for exactly the words in the code. The lab builds $H$ from $G$
by row-reducing and reading off the null space, which makes it deterministic.

Take the systematic $(7,4)$ Hamming code:

```text
G = 1 0 0 0 0 1 1        H = 0 1 1 1 1 0 0
    0 1 0 0 1 0 1            1 0 1 1 0 1 0
    0 0 1 0 1 1 0            1 1 0 1 0 0 1
    0 0 0 1 1 1 1
```

Encode `1011` by adding rows 0, 2 and 3 of $G$: the data half is `1011` unchanged and the
parity half is $(0,1,1) + (1,1,0) + (1,1,1) = (0,1,0)$, so the codeword is `1011010`.

Now the fact that makes decoding cheap. Suppose the channel turns codeword $c$ into
$y = c + e$ for some error pattern $e$. Then $Hy^{T} = Hc^{T} + He^{T} = He^{T}$: the
syndrome does not depend on which codeword was sent, only on the error. And if $e$ is a
single 1 in position $j$, then $He^{T}$ is column $j$ of $H$. So the syndrome of a
single-error word *is* a column of $H$, and if the columns are distinct and nonzero, it
names the position.

```python
H = [[0, 1, 1, 1, 1, 0, 0],
     [1, 0, 1, 1, 0, 1, 0],
     [1, 1, 0, 1, 0, 0, 1]]


def syndrome(word):
    return [sum(h * w for h, w in zip(row, word)) % 2 for row in H]


for j in range(7):
    e = [1 if t == j else 0 for t in range(7)]
    print(f"error at {j}: syndrome {syndrome(e)}")

word = [1, 0, 1, 1, 0, 1, 0]
print("codeword syndrome:", syndrome(word))
broken = list(word)
broken[2] ^= 1
print("flip position 2  ->", broken, "syndrome", syndrome(broken))
both = list(word)
both[4] ^= 1
both[5] ^= 1
print("flip 4 and 5     ->", both, "syndrome", syndrome(both))
```

The seven columns come out as $(0,1,1)$, $(1,0,1)$, $(1,1,0)$, $(1,1,1)$, $(1,0,0)$,
$(0,1,0)$ and $(0,0,1)$: seven distinct nonzero patterns, exactly the seven nonzero
three-bit values, which is what the tight Hamming bound predicted. A clean codeword gives
$(0,0,0)$. Flipping position 2 gives $(1,1,0)$, the decoder looks that up, flips position 2
back, and the word is repaired without ever knowing which codeword was sent.

## The mistake: expecting the syndrome to be the position number

Every textbook draws the version of this code whose columns are the binary numerals 1
through 7 in order, so that the syndrome reads off as the index of the broken bit. It is a
lovely arrangement and it is a property of that column order, not of Hamming codes. In the
systematic layout above the columns are the same seven patterns in a different order, so
the syndrome of an error at position 2 is $(1,1,0)$, which reads as 6. Nothing is wrong; the
syndrome is a *fingerprint* of the error, and turning a fingerprint into a position is a
table lookup. Expecting arithmetic instead of a lookup is what makes a working decoder look
broken, and it is tempting because the numbered version is the one everybody meets first.

The lab builds that lookup for the general case, as a table of *coset leaders*: for each
syndrome, the lightest error vector producing it. Enumerate error patterns by increasing
weight and record the first one that gives each syndrome; stop when all $2^{n-k}$ syndromes
have an entry. For the $(7,4)$ code that stops after weight 1, because the eight syndromes
are covered by the all-zero error and the seven single-bit errors — the perfect-code
property, in the form the decoder actually uses.

## What two errors do

The last line of the trace above is the limit. Flipping positions 4 and 5 gives syndrome
$(1,0,0) + (0,1,0) = (1,1,0)$, which is column 2. The decoder confidently flips position 2,
and the word it hands back differs from the original in three places rather than two. A
minimum distance of $d$ buys correction of $\text{floor}((d-1)/2)$ errors, so one here, or
detection of $d - 1 = 2$ errors, and you choose one: a decoder that corrects single errors cannot also
report double errors, because it has already spent every syndrome on a single-error
hypothesis. The extended code, with an eighth overall parity bit, has distance 4 and can do
both — correct one and flag two — which is why memory modules use $(8,4)$ and $(72,64)$
rather than the bare Hamming code.

Even so, the repair is worth having:

```python
from math import comb

print("  p      uncoded 4-bit    Hamming(7,4)")
for p in (0.001, 0.01, 0.05):
    uncoded = 1 - (1 - p) ** 4
    coded = 1 - sum(comb(7, i) * p ** i * (1 - p) ** (7 - i) for i in range(2))
    print(f"{p:<8}{uncoded:<17.6f}{coded:.6f}")
```

At one flip in a hundred a bare four-bit word is wrong 3.9% of the time and the coded one
0.2% — a factor of nineteen, bought with three extra bits per nibble.

## Where this stops

The block is protected against one error, so two errors in the same seven bits defeat it,
and a burst of noise puts several errors in one block by definition. That is the failure
mode module 4's interleaving exists for: scramble the bit order so a burst on the wire
arrives as isolated errors in many different blocks. Syndrome decoding by table is also
exponential in $n - k$: the table has $2^{n-k}$ entries, fine for three or four parity bits
and hopeless for a modern code with thousands, which is why real decoders exploit algebraic
or graph structure instead of looking anything up.

And the rate is nowhere near capacity. Hamming $(7,4)$ runs at $4/7 = 0.571$ bits a use
while the capacity of a $p = 0.01$ channel is 0.919; module 4 promised a code at rate 0.9
with error below anything you like, and this is not it. Closing that gap is what took from
1948 to the 1990s, and the codes that closed it — turbo and LDPC — are iterative and
probabilistic rather than table-driven. Finally, everything here lives over GF(2), one bit
at a time. Reed-Solomon codes work over larger fields, treat a byte as one symbol, and
therefore see a burst of eight adjacent bit errors as a single symbol error, which is why
they sit under CDs, QR codes and deep-space links.

## What the lab asks for

The lab *Repairing what the channel broke* wants a `LinearCode` class built from a
generator matrix — `encode`, `parity_check`, `syndrome`, `decode`, `codewords`,
`min_distance` — plus `hamming_code(r)`, `repetition_code`, `parity_code` and the two
Hamming-metric helpers. The checks assert the exact $G$ and $H$ printed above, the exact
seven-entry syndrome table, that every one of the $16 \times 7$ single-error words decodes
back to the codeword it came from, and that a specific double error decodes to a specific
wrong codeword — because a code's limits deserve an assertion as much as its guarantees do.
''',
                },
            ],
            "quiz": {
                "title": "Distance, syndromes and their limits",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A single parity bit over four data bits detects any single error. Why can it not correct one?",
                        "opts": [
                            "Because the parity bit itself may be the corrupted one, and it cannot check itself",
                            "Because one check has two outcomes, and locating an error among five bits needs six",
                            "Because the code's minimum distance is 2, so two codewords differ in only one place",
                            "Because parity is computed over the data only, so it says nothing about its own position",
                        ],
                        "a": 1,
                        "why": r"""
Counting outcomes settles it before any algebra. One check produces one bit of news, so two
outcomes; the question "where is the error" has six answers on a five-bit word — clean, or
broken in one of five places. Two outcomes cannot separate six cases. Adding checks is the
only repair, and the general form is $2^r \ge n + 1$: three checks give eight outcomes, which
is enough for a seven-bit word. That is the Hamming bound, and it is why $(7,4)$ is the
smallest interesting code rather than $(5,4)$.
                        """,
                        "whys": [
                            r"""
The parity bit being corruptible is true and is handled by the count — it is one of the five
positions the syndrome would have to name. It is not a special case needing separate
treatment: in a Hamming code the parity bits are protected exactly as the data bits are, and
their columns of $H$ are as distinct as any other.
                            """,
                            r"""
Right, and the counting frame generalises immediately: to correct up to $t$ errors the
syndrome must distinguish every error pattern of weight at most $t$, which is
$\sum_{i \le t} \text{C}(n, i)$ patterns, and $2^{n-k}$ has to be at least that. Single-error
correction is the case $t = 1$.
                            """,
                            r"""
The minimum distance of a single-parity code is 2, and that is the algebraic statement of the
same fact — but it says two codewords differ in at least *two* places, not one. Distance 2
means a single error lands strictly between codewords and is detectable; distance 3 is what
puts it strictly nearer to one codeword than any other, which is what correction needs.
                            """,
                            r"""
An overall parity bit is computed over the data bits and is itself part of the codeword, so
it is covered by the check in the sense that the check fails if it flips. Whether it covers
itself is not the obstacle; the obstacle is that one check has only two possible answers
however it is arranged.
                            """,
                        ],
                    },
                    {
                        "q": "In the systematic (7,4) Hamming code an error at position 2 gives syndrome (1,1,0), which reads as the number 6. Is the decoder broken?",
                        "opts": [
                            "Yes — a Hamming syndrome must equal the error position, so the parity matrix is wrong",
                            "Yes — the syndrome is being computed with the rows of H rather than its columns",
                            "No — the syndrome is column 2 of H, and only a column ordering by index makes it a position",
                            "No — the syndrome of an error is arbitrary, so any decoder needs a lookup table",
                        ],
                        "a": 2,
                        "why": r"""
$He^{T}$ for a single error at position $j$ is column $j$ of $H$, whatever order the columns
are in. The textbook arrangement puts the binary numerals 1 to 7 in the columns in order, so
the syndrome reads as the position — a genuine convenience and a property of that ordering,
not of Hamming codes. The systematic layout $[A \, | \, I]$ has the same seven columns in a
different order, so position 2 carries the pattern $(1,1,0)$. The decoder looks it up and is
correct.
                        """,
                        "whys": [
                            r"""
There is no requirement that a syndrome equal a position. What the code requires is that the
columns of $H$ be distinct and nonzero, so that each single error has its own fingerprint.
Column order is free, and different orders give different but equally valid codes with the
same distance and the same rate.
                            """,
                            r"""
The syndrome is computed as $H$ times the word, which takes a dot product with each row of
$H$ — so rows do appear in the computation. The result, for a single error, happens to be a
column of $H$, and both statements are true at once. Nothing here is confused about rows and
columns; the computation is exactly the one the definition asks for.
                            """,
                            r"""
Right, and the reason for the systematic order is worth knowing: $G = [I \, | \, A^{T}]$ puts
the data bits untouched at the front of the codeword, so the decoder can read the message off
without solving anything. That convenience is paid for with a syndrome that no longer reads
as a numeral.
                            """,
                            r"""
Syndromes are not arbitrary — they are exactly the columns of $H$, which is why the table has
$2^{n-k}$ entries rather than needing search. And a lookup table is not forced by
arbitrariness: for the numbered column order the "table" is the identity on integers, which is
why that arrangement is taught first.
                            """,
                        ],
                    },
                    {
                        "q": "A (7,4) Hamming word arrives with two flipped bits. What does the decoder do?",
                        "opts": [
                            "Returns a codeword differing from the original in three places, without any warning",
                            "Reports a zero syndrome, since two errors cancel in every parity check",
                            "Detects the double error and reports a failure, because distance 3 detects two errors",
                            "Corrects one of the two errors and leaves the other, so one bit remains wrong",
                        ],
                        "a": 0,
                        "why": r"""
The syndrome of a double error is the sum of two columns of $H$, which — because the columns
are all seven nonzero patterns — is some third column. The decoder reads it as a single error
at that third position and flips a bit that was fine. The result is a genuine codeword,
differing from the transmitted one in the two broken places plus the one it broke: three.
Nothing is flagged, because every syndrome has already been assigned to a single-error
hypothesis. Distance 3 lets you correct one error *or* detect two, and a correcting decoder
has spent the syndromes on correcting.
                        """,
                        "whys": [
                            r"""
Right, and the reason the output is a codeword rather than nonsense is worth keeping: the
decoder subtracts a coset leader, so the result always lands in the code by construction. A
downstream check that only verifies "is this a valid codeword" will pass, which is exactly why
memory modules use a distance-4 code when they want a double-error alarm.
                            """,
                            r"""
Two errors cancel only if the two columns are equal, and in a Hamming code no two columns are
equal — that is the defining property. Their sum is another nonzero column, so the syndrome is
nonzero and the decoder acts on it. A zero syndrome from a corrupted word needs an error
pattern that is itself a codeword, which for this code means at least three flips.
                            """,
                            r"""
Distance 3 does allow detection of up to two errors, but only for a decoder that declines to
correct: it would flag every nonzero syndrome and repair nothing. You get one behaviour or the
other from the same code, and a single-error-correcting decoder has already chosen. Getting
both requires distance 4, which the extended $(8,4)$ code supplies.
                            """,
                            r"""
The decoder does not fix either of the two real errors. It computes one syndrome, looks up one
single-bit leader, and flips exactly one bit — and that bit is at the position named by the sum
of the two error columns, which is neither of the two positions that actually broke.
                            """,
                        ],
                    },
                    {
                        "q": "Why does a syndrome tell you about the error rather than about which codeword was sent?",
                        "opts": [
                            "Because the parity checks are computed from the received word, which no longer includes the codeword",
                            "Because H times (c + e) is H times c plus H times e, and the first term is zero for every codeword",
                            "Because the coset-leader table is built from error vectors, so it can only report error vectors",
                            "Because the syndrome has n - k bits, too few to name one of the 2^k codewords",
                        ],
                        "a": 1,
                        "why": r"""
$H$ is chosen so that $Hc^{T} = 0$ for every codeword — that is what "parity-check matrix"
means. Linearity then gives $H(c + e)^{T} = Hc^{T} + He^{T} = He^{T}$: the codeword contributes
nothing and the syndrome is a function of the error alone. That is why one table of
$2^{n-k}$ entries serves all $2^k$ codewords, and why the decoder never needs to guess what was
sent before it repairs what arrived.
                        """,
                        "whys": [
                            r"""
The received word is exactly the codeword plus the error, so it very much still contains the
codeword. If the checks were not built to annihilate codewords, the syndrome would depend on
both and the table would need an entry per (codeword, error) pair — which is the design this
one avoids.
                            """,
                            r"""
Right, and the practical consequence is the size of the table: $2^{n-k}$ entries rather than
$2^n$, because the codeword washes out. For the $(7,4)$ code that is 8 entries covering all
128 possible received words, and for the $(15,11)$ code it is 16 covering 32768.
                            """,
                            r"""
The table maps syndromes to error vectors because that is what the syndrome determines, not the
other way round. Building it out of error vectors is a consequence of the linearity fact, not
its cause — and a table built without that fact would need the codeword as part of its key.
                            """,
                            r"""
It is true that $n - k$ bits cannot name one of $2^k$ codewords, and that is a useful sanity
check on what a syndrome could possibly carry. But it does not explain why the syndrome is a
clean function of the error rather than a lossy function of both; that comes from $H$
annihilating the code.
                            """,
                        ],
                    },
                    {
                        "q": "Hamming (7,4) runs at rate 0.571 on a channel whose capacity is 0.919. What does that gap represent?",
                        "opts": [
                            "A defect in the code, since a perfect code should reach the capacity of its channel",
                            "Room the coding theorem promises is usable, which this code's structure does not take",
                            "The cost of correcting errors rather than merely detecting them, which capacity ignores",
                            "The difference between a block code and the stream codes capacity is defined for",
                        ],
                        "a": 1,
                        "why": r"""
Capacity is an asymptotic promise about existence: at any rate below 0.919 there is *some* code,
at *some* block length, with error as small as you like. Hamming $(7,4)$ is a very short code
with a rigid structure chosen to make decoding a table lookup, and it pays for that with rate.
Nothing is broken — "perfect" in coding theory means the radius-1 spheres tile the space
exactly, which is a statement about the block length 7, not about the Shannon limit. Closing
the gap took until the 1990s, with iterative codes at block lengths in the thousands.
                        """,
                        "whys": [
                            r"""
"Perfect" is a term of art meaning the spheres of radius $t$ around the codewords tile the whole
space with nothing left over — $2^4 \times 8 = 128 = 2^7$ here. It says the code wastes no
syndrome at its own block length, and it implies nothing about capacity. The Golay code and the
repetition codes of odd length are the only other binary perfect codes, and none of them is
near capacity either.
                            """,
                            r"""
Right, and the two numbers answer different questions: 0.571 is what this code achieves at
block length 7 with a bounded-distance decoder, and 0.919 is what some code achieves in the
limit of long blocks. Comparing them is worthwhile precisely because it shows how much a short,
structured code gives up.
                            """,
                            r"""
Capacity already accounts for correcting rather than detecting — it is the rate at which the
receiver can recover the message, which is correction. There is no separate surcharge that
capacity omits, and codes very close to capacity do correct rather than merely detect.
                            """,
                            r"""
Capacity is defined for a memoryless channel used $n$ times and is approached by block codes as
$n$ grows; block coding is the setting of the theorem rather than a departure from it. The
codes that approach capacity — LDPC, turbo — are block codes too, with blocks of thousands of
bits rather than seven.
                            """,
                        ],
                    },
                    {
                        "q": "The lab builds coset leaders by enumerating error vectors of weight 0, then 1, then 2, and stopping when every syndrome has an entry. Why in that order?",
                        "opts": [
                            "So the table is built in the fewest passes, since heavier errors have more syndromes",
                            "So each syndrome maps to the lightest error causing it, which is the most likely one",
                            "So that codewords are found first, since a codeword is an error vector of weight zero",
                            "So the enumeration terminates, which it would not if heavy vectors were tried first",
                        ],
                        "a": 1,
                        "why": r"""
Several error vectors share a syndrome — one per codeword, in fact, since $e$ and $e + c$ give
the same one. The decoder has to pick a representative, and on a channel that flips each bit
with probability under $1/2$ the lightest vector in the class is the most probable explanation
of what arrived. Enumerating by weight and keeping the first hit for each syndrome puts exactly
that vector in the table. This is maximum-likelihood decoding for a BSC, arrived at by sorting
rather than by computing any probability.
                        """,
                        "whys": [
                            r"""
Pass count is not what the order buys — a single sweep over all $2^n$ vectors in any order would
also fill the table, and the early stop is a speed detail rather than the reason. The reason is
which representative ends up stored, because that choice is the decoder's entire decision rule.
                            """,
                            r"""
Right, and it is worth noticing that "lightest" is only optimal because $p < 1/2$. On a channel
that flips more often than not, the most likely error pattern is a heavy one, and the correct
repair is to invert the received word first — which is the same observation that made
$C = 1 - H_2(p)$ symmetric about $p = 1/2$ in module 4.
                            """,
                            r"""
The all-zero vector does have weight zero and does map to the zero syndrome, but the other
codewords have positive weight and are found no earlier than any other vector of their weight.
The table is about syndromes and their lightest preimages; codewords enter only as the class
whose syndrome is zero.
                            """,
                            r"""
The enumeration is over a finite set of $2^n$ vectors, so it terminates in any order. The
weight ordering is about which entry is kept when several vectors collide on one syndrome, and
that is a correctness question rather than a termination one.
                            """,
                        ],
                    },
                ],
            },
            "blanks": {
                "title": "Syndromes and coset leaders",
                "minutes": 9,
                "caption": "block.py — four decisions removed",
                "lang": "python",
                "brief": r"""
Three short functions carry the whole decoder. Arithmetic here is over GF(2), where addition
and subtraction are the same operation, and each hole is a place where an ordinary-integer
habit produces a decoder that is wrong on some words and right on others.
""",
                "listing": """import itertools


def syndrome(H, word):
    \"\"\"H times word over GF(2): one parity result per check row.\"\"\"
    return [sum(h * w for h, w in zip(row, word)) ___ 2 for row in H]


def coset_leaders(H, n):
    \"\"\"The lightest error vector for every syndrome, found weight by weight.\"\"\"
    table = {}
    wanted = 2 ** len(H)
    for weight in range(n + 1):
        for positions in itertools.combinations(range(n), weight):
            e = [0] * n
            for p in positions:
                e[p] = 1
            s = tuple(syndrome(H, e))
            if s ___ table:
                table[s] = e
        if len(table) == wanted:
            break
    return table


def decode(H, table, word):
    \"\"\"Remove the lightest error pattern that carries this syndrome.\"\"\"
    e = table[tuple(syndrome(H, word))]
    return [a ___ b for a, b in zip(word, e)]


# a single error in position j always produces the syndrome ___
""",
                "blanks": [
                    {
                        "prompt": "The parity check is arithmetic over GF(2). What reduces each dot product to a single bit?",
                        "hole": "?",
                        "opts": ["%", "//", "*", "-"],
                        "a": 0,
                        "why": "Over GF(2) a parity check asks whether the number of ones in its positions is odd, so the dot product is taken modulo 2. Without the reduction the syndrome is a list of small integers and no two runs of the decoder agree on what a syndrome is.",
                        "whys": [
                            "Over GF(2) a parity check asks whether the number of ones in its positions is odd, so the dot product is taken modulo 2. Without the reduction the syndrome is a list of small integers and no two runs of the decoder agree on what a syndrome is.",
                            "Integer division by 2 halves the count instead of taking its parity, so a check covering two set positions reports 1 and one covering three also reports 1. Two different errors become indistinguishable and the lookup returns the wrong leader.",
                            "Multiplying by 2 doubles the count and never produces a bit at all, so every syndrome is even and the table key space bears no relation to the columns of H.",
                            "Subtracting 2 leaves negative values for a clean check and shifts every other value, so the zero syndrome that identifies a valid codeword becomes -2 and no codeword ever verifies.",
                        ],
                    },
                    {
                        "prompt": "Vectors are enumerated lightest first. Which test keeps the lightest one for each syndrome?",
                        "hole": "?",
                        "opts": ["not in", "in", "is not", "!="],
                        "a": 0,
                        "why": "Recording a syndrome only the first time it appears keeps the lightest vector that produced it, because the enumeration runs by increasing weight. Every later vector with the same syndrome is a heavier member of the same coset and a less likely explanation.",
                        "whys": [
                            "Recording a syndrome only the first time it appears keeps the lightest vector that produced it, because the enumeration runs by increasing weight. Every later vector with the same syndrome is a heavier member of the same coset and a less likely explanation.",
                            "Writing only when the syndrome is already present leaves the table empty forever, since nothing can be present before something is written. The function returns an empty dictionary and the decoder raises on its first lookup.",
                            "Comparing a tuple with a dictionary by identity is always true, so every vector overwrites its predecessor and the table ends up holding the heaviest error for each syndrome rather than the lightest.",
                            "Comparing a syndrome tuple against the whole table for inequality is also always true, with the same effect: the last vector enumerated wins, which is the maximum-weight coset member.",
                        ],
                    },
                    {
                        "prompt": "The leader is removed from the received word. Which operation is subtraction over GF(2)?",
                        "hole": "?",
                        "opts": ["^", "&", "|", "+"],
                        "a": 0,
                        "why": "Over GF(2) addition and subtraction are both exclusive-or, so removing the error pattern is the same operation that the channel used to add it. That symmetry is why the decoder never needs to know whether a bit was flipped up or down.",
                        "whys": [
                            "Over GF(2) addition and subtraction are both exclusive-or, so removing the error pattern is the same operation that the channel used to add it. That symmetry is why the decoder never needs to know whether a bit was flipped up or down.",
                            "A bitwise and clears every position where the leader is 0, so the corrected word keeps only the bits the decoder believes are broken. Almost every word comes back as all zeros.",
                            "A bitwise or can only set bits, never clear them, so an error that turned a 0 into a 1 is never undone. Half the single-bit errors are corrected and half are left in place.",
                            "Ordinary addition produces a 2 wherever both the word and the leader hold a 1, and the result is no longer a bit vector at all — the next syndrome computed from it is meaningless.",
                        ],
                    },
                    {
                        "prompt": "One bit has flipped, at position j. What does the parity check produce?",
                        "hole": "?",
                        "opts": ["column j of H", "row j of H", "the jth codeword", "the weight of H"],
                        "a": 0,
                        "why": "H times a vector with a single 1 in position j selects the jth column of H, and the codeword contributes nothing because H annihilates every codeword. This is the fact that makes the table depend on the error alone rather than on what was sent.",
                        "whys": [
                            "H times a vector with a single 1 in position j selects the jth column of H, and the codeword contributes nothing because H annihilates every codeword. This is the fact that makes the table depend on the error alone rather than on what was sent.",
                            "Rows of H are the parity checks themselves and are n bits long, while a syndrome has only n - k bits. The shapes do not even match, which is the quickest way to notice the mix-up.",
                            "Codewords give the zero syndrome by definition, so if the check returned a codeword it would be returning zero for every input and telling the decoder nothing at all.",
                            "The weight of the matrix is a single number, and a syndrome is a vector with one entry per check row. A scalar cannot distinguish the n positions an error might occupy.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Repairing what the channel broke",
                "runtime": "python",
                "minutes": 75,
                "brief": r'''
One class and five functions, all over GF(2), where a vector is a list of `0` and `1`
and addition is exclusive-or.

**`hamming_weight(v)`** and **`hamming_distance(a, b)`** — the number of ones, and
the number of positions where two equal-length vectors differ. `hamming_distance`
raises `ValueError` on a length mismatch.

**`LinearCode(G)`** — `G` is a list of `k` rows of `n` bits.

- `.n`, `.k` — the block length and the message length.
- `.encode(msg)` — the sum over GF(2) of the rows `msg` selects. `ValueError` unless
  `msg` is `k` bits.
- `.parity_check()` — an `(n - k)` by `n` matrix `H` spanning the null space of `G`.
  Build it deterministically: row-reduce `G`, take the non-pivot ("free") columns in
  increasing order, and for each free column `f` emit the vector with a 1 at `f` and,
  at each pivot column `p_i`, the entry of the reduced row `i` in column `f`.
- `.syndrome(word)` — `H` times the word, modulo 2. `ValueError` unless the word is
  `n` bits.
- `.decode(word)` — returns `(corrected, error)`. Build the coset-leader table once:
  enumerate error vectors by increasing weight, keep the first vector found for each
  syndrome, and stop when all `2**(n-k)` syndromes have one.
- `.codewords()` — all `2**k` codewords, in the order `itertools.product` produces
  the messages.
- `.min_distance()` — the smallest weight of a nonzero codeword.

Raise `ValueError` for an empty or ragged `G`, an entry outside `{0, 1}`, rows that
are linearly dependent, or a code too large to enumerate (`n > 20` or `k > 16`).

**`hamming_code(r)`** — the systematic `(2**r - 1, 2**r - 1 - r)` Hamming code.
Its `A` block has one column per integer in `1..2**r-1` whose binary form has at
least two ones, in increasing numeric order, written most significant bit first;
`G = [I_k | A_transpose]`. `ValueError` for `r < 2`.

```text
hamming_code(3).G == [[1, 0, 0, 0, 0, 1, 1],
                      [0, 1, 0, 0, 1, 0, 1],
                      [0, 0, 1, 0, 1, 1, 0],
                      [0, 0, 0, 1, 1, 1, 1]]
hamming_code(3).parity_check() == [[0, 1, 1, 1, 1, 0, 0],
                                   [1, 0, 1, 1, 0, 1, 0],
                                   [1, 1, 0, 1, 0, 0, 1]]
hamming_code(3).encode([1, 0, 1, 1]) == [1, 0, 1, 1, 0, 1, 0]
```

**`repetition_code(n)`** — one message bit sent `n` times.
**`parity_code(k)`** — `k` message bits plus one overall parity bit.

Standard library only; `itertools` is the one import you need. The checks assert the
exact matrices above, the exact seven-entry syndrome table, that all 112
single-error words decode back to their codewords, and that a named double error
decodes to a named wrong codeword.
''',
                "files": [{"name": "main.py", "content": r'''
import itertools


def hamming_weight(v):
    """The number of ones in a GF(2) vector."""
    # your code here


def hamming_distance(a, b):
    """The number of positions where two equal-length vectors differ."""
    # your code here


class LinearCode:
    """A binary linear code, given by its generator matrix."""

    def __init__(self, G):
        # your code here
        pass

    def encode(self, msg):
        """The sum over GF(2) of the generator rows this message selects."""
        # your code here

    def parity_check(self):
        """An (n - k) by n matrix spanning the null space of G."""
        # your code here

    def syndrome(self, word):
        """H times the word, modulo 2."""
        # your code here

    def decode(self, word):
        """(corrected word, the error removed) via the coset-leader table."""
        # your code here

    def codewords(self):
        """Every codeword, in message order."""
        # your code here

    def min_distance(self):
        """The smallest weight of a nonzero codeword."""
        # your code here


def hamming_code(r):
    """The systematic (2**r - 1, 2**r - 1 - r) Hamming code."""
    # your code here


def repetition_code(n):
    """One message bit sent n times."""
    # your code here


def parity_code(k):
    """k message bits plus one overall parity bit."""
    # your code here


code = hamming_code(3)
print(code.encode([1, 0, 1, 1]))
print(code.parity_check())
print(code.min_distance())
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import itertools


def hamming_weight(v):
    """The number of ones in a GF(2) vector."""
    return sum(1 for b in v if b)


def hamming_distance(a, b):
    """The number of positions where two equal-length vectors differ."""
    if len(a) != len(b):
        raise ValueError(f"lengths {len(a)} and {len(b)} cannot be compared")
    return sum(1 for x, y in zip(a, b) if x != y)


class LinearCode:
    """A binary linear code, given by its generator matrix."""

    def __init__(self, G):
        if not G or not G[0]:
            raise ValueError("a generator matrix needs at least one row of one bit")
        n = len(G[0])
        for row in G:
            if len(row) != n:
                raise ValueError("the generator matrix is ragged")
            if any(b not in (0, 1) for b in row):
                raise ValueError("a generator entry is not 0 or 1")
        self.G = [list(r) for r in G]
        self.k = len(self.G)
        self.n = n
        if self.n > 20 or self.k > 16:
            raise ValueError("too large to enumerate: keep n <= 20 and k <= 16")
        rows, pivots = self._rref(self.G)
        if len(pivots) != self.k:
            raise ValueError("the generator rows are linearly dependent")
        self._rows, self._pivots = rows, pivots
        self._H = None
        self._leaders = None
        self._words = None

    @staticmethod
    def _rref(matrix):
        """Row-reduce over GF(2); returns the nonzero rows and the pivot columns."""
        m = [list(r) for r in matrix]
        pivots = []
        r = 0
        for c in range(len(m[0])):
            p = next((i for i in range(r, len(m)) if m[i][c]), None)
            if p is None:
                continue
            m[r], m[p] = m[p], m[r]
            for i in range(len(m)):
                if i != r and m[i][c]:
                    m[i] = [a ^ b for a, b in zip(m[i], m[r])]
            pivots.append(c)
            r += 1
            if r == len(m):
                break
        return m[:r], pivots

    def encode(self, msg):
        """The sum over GF(2) of the generator rows this message selects."""
        if len(msg) != self.k or any(b not in (0, 1) for b in msg):
            raise ValueError(f"a message is {self.k} bits over GF(2)")
        out = [0] * self.n
        for bit, row in zip(msg, self.G):
            if bit:
                out = [a ^ b for a, b in zip(out, row)]
        return out

    def parity_check(self):
        """An (n - k) by n matrix spanning the null space of G."""
        if self._H is None:
            free = [c for c in range(self.n) if c not in self._pivots]
            H = []
            for f in free:
                v = [0] * self.n
                v[f] = 1
                for i, p in enumerate(self._pivots):
                    v[p] = self._rows[i][f]
                H.append(v)
            self._H = H
        return [list(r) for r in self._H]

    def syndrome(self, word):
        """H times the word, modulo 2."""
        if len(word) != self.n or any(b not in (0, 1) for b in word):
            raise ValueError(f"a word is {self.n} bits over GF(2)")
        self.parity_check()
        return [sum(h * w for h, w in zip(row, word)) % 2 for row in self._H]

    def _table(self):
        """Syndrome -> lightest error with that syndrome, built once."""
        if self._leaders is None:
            table = {}
            wanted = 2 ** (self.n - self.k)
            for weight in range(self.n + 1):
                for positions in itertools.combinations(range(self.n), weight):
                    e = [0] * self.n
                    for p in positions:
                        e[p] = 1
                    s = tuple(self.syndrome(e))
                    if s not in table:
                        table[s] = e
                if len(table) == wanted:
                    break
            self._leaders = table
        return self._leaders

    def decode(self, word):
        """(corrected word, the error removed) via the coset-leader table."""
        e = self._table()[tuple(self.syndrome(word))]
        return [a ^ b for a, b in zip(word, e)], list(e)

    def codewords(self):
        """Every codeword, in message order."""
        if self._words is None:
            self._words = [self.encode(list(m))
                           for m in itertools.product((0, 1), repeat=self.k)]
        return [list(c) for c in self._words]

    def min_distance(self):
        """The smallest weight of a nonzero codeword."""
        return min(hamming_weight(c) for c in self.codewords() if any(c))


def hamming_code(r):
    """The systematic (2**r - 1, 2**r - 1 - r) Hamming code."""
    if isinstance(r, bool) or not isinstance(r, int) or r < 2:
        raise ValueError("a Hamming code needs at least 2 parity bits")
    n = 2 ** r - 1
    k = n - r
    # the columns of A are the patterns of weight 2 or more; weight-1 patterns are
    # already the identity block, and 0 would be a column no error could produce
    cols = [j for j in range(1, n + 1) if bin(j).count("1") >= 2]
    A = [[(c >> (r - 1 - i)) & 1 for c in cols] for i in range(r)]
    G = [[1 if t == j else 0 for t in range(k)] + [A[i][j] for i in range(r)]
         for j in range(k)]
    return LinearCode(G)


def repetition_code(n):
    """One message bit sent n times."""
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("a repetition code repeats at least once")
    return LinearCode([[1] * n])


def parity_code(k):
    """k message bits plus one overall parity bit."""
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("a parity code needs at least one data bit")
    return LinearCode([[1 if t == j else 0 for t in range(k)] + [1] for j in range(k)])


code = hamming_code(3)
print(code.encode([1, 0, 1, 1]))
print(code.parity_check())
print(code.min_distance())
'''}],
                "hints": [
                    "Row-reduce `G` once in `__init__` and keep the reduced rows and the pivot columns; `parity_check` is then a short loop over the free columns and needs no further elimination.",
                    "If the row reduction finds fewer pivots than there are rows, two generator rows are dependent, the code has fewer than 2**k distinct codewords, and the class should refuse the matrix.",
                    "Build the coset-leader table lazily and cache it: `decode` is called hundreds of times by the checks and the table only has to be built once per code.",
                    "Stop the leader enumeration as soon as the table holds 2**(n-k) entries. For a Hamming code that happens after weight 1, which is what makes decoding a (15,11) code instant rather than a walk over 32768 vectors.",
                    "`(c >> (r - 1 - i)) & 1` reads bit `i` of `c` counting from the most significant of `r` bits, which is the order that makes column `j` of `H` the binary numeral for `j`.",
                ],
                "tests": [
                    {"name": "the Hamming metric helpers", "code": r'''
assert hamming_weight([0, 0, 0]) == 0 and hamming_weight([1, 0, 1, 1]) == 3
assert hamming_weight([]) == 0, "an empty vector weighs nothing"
assert hamming_distance([1, 0, 1, 1], [1, 1, 1, 0]) == 2, \
    f"got {hamming_distance([1, 0, 1, 1], [1, 1, 1, 0])!r}"
assert hamming_distance([1, 1], [1, 1]) == 0
try:
    hamming_distance([1, 0], [1, 0, 1])
    assert False, "a length mismatch should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "hamming_code(3) is the matrix pair from the reading", "code": r'''
_c = hamming_code(3)
assert (_c.n, _c.k) == (7, 4), f"got n={_c.n}, k={_c.k}"
assert _c.G == [[1, 0, 0, 0, 0, 1, 1],
                [0, 1, 0, 0, 1, 0, 1],
                [0, 0, 1, 0, 1, 1, 0],
                [0, 0, 0, 1, 1, 1, 1]], f"got {_c.G!r}"
assert _c.parity_check() == [[0, 1, 1, 1, 1, 0, 0],
                             [1, 0, 1, 1, 0, 1, 0],
                             [1, 1, 0, 1, 0, 0, 1]], f"got {_c.parity_check()!r}"
assert _c.encode([1, 0, 1, 1]) == [1, 0, 1, 1, 0, 1, 0], f"got {_c.encode([1, 0, 1, 1])!r}"
assert _c.encode([0, 0, 0, 0]) == [0] * 7, "the zero message is the zero codeword"
for _bad in [[1, 0, 1], [1, 0, 1, 2], [1, 0, 1, 1, 1]]:
    try:
        _c.encode(_bad)
        assert False, f"encode({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "the code is a subspace with distance 3", "code": r'''
_c = hamming_code(3)
_words = _c.codewords()
assert len(_words) == 16, f"2**4 codewords, got {len(_words)}"
assert len({tuple(w) for w in _words}) == 16, "the codewords must all be distinct"
assert _c.min_distance() == 3, f"got {_c.min_distance()!r}"
for _w in _words:
    assert _c.syndrome(_w) == [0, 0, 0], f"codeword {_w!r} has syndrome {_c.syndrome(_w)!r}"
for _a in _words[:6]:
    for _b in _words[:6]:
        if _a != _b:
            assert hamming_distance(_a, _b) >= 3, f"{_a!r} and {_b!r} are too close"
assert 2 ** _c.k * (1 + _c.n) == 2 ** _c.n, \
    "the (7,4) code is perfect: 16 spheres of size 8 fill all 128 words"
'''},
                    {"name": "the seven single-error syndromes are the columns of H", "code": r'''
_c = hamming_code(3)
_H = _c.parity_check()
_seen = []
for _j in range(7):
    _e = [1 if _t == _j else 0 for _t in range(7)]
    _s = _c.syndrome(_e)
    assert _s == [_row[_j] for _row in _H], \
        f"an error at {_j} should give column {_j} of H, got {_s!r}"
    _seen.append(tuple(_s))
assert _seen == [(0, 1, 1), (1, 0, 1), (1, 1, 0), (1, 1, 1),
                 (1, 0, 0), (0, 1, 0), (0, 0, 1)], f"got {_seen!r}"
assert len(set(_seen)) == 7 and (0, 0, 0) not in _seen, \
    "the seven columns must be distinct and nonzero, or an error cannot be located"
_cw = _c.encode([1, 0, 1, 1])
_broken = list(_cw)
_broken[2] ^= 1
assert _c.syndrome(_broken) == [1, 1, 0], f"got {_c.syndrome(_broken)!r}"
'''},
                    {"name": "every single-error word decodes back", "code": r'''
_c = hamming_code(3)
_checked = 0
for _cw in _c.codewords():
    for _j in range(_c.n):
        _rx = list(_cw)
        _rx[_j] ^= 1
        _fixed, _err = _c.decode(_rx)
        assert _fixed == _cw, f"{_rx!r} decoded to {_fixed!r}, expected {_cw!r}"
        assert _err == [1 if _t == _j else 0 for _t in range(_c.n)], \
            f"the reported error was {_err!r}, expected a single 1 at {_j}"
        _checked += 1
assert _checked == 112, f"16 codewords times 7 positions, got {_checked}"
for _cw in _c.codewords():
    assert _c.decode(_cw) == (_cw, [0] * 7), "a clean codeword is returned untouched"
'''},
                    {"name": "two errors defeat it, and in a specific way", "code": r'''
_c = hamming_code(3)
_cw = _c.encode([1, 0, 1, 1])
_both = list(_cw)
_both[4] ^= 1
_both[5] ^= 1
assert _c.syndrome(_both) == [1, 1, 0], \
    f"two error columns add to a third column, got {_c.syndrome(_both)!r}"
_fixed, _err = _c.decode(_both)
assert _fixed != _cw, "a double error cannot be repaired by a distance-3 code"
assert _fixed in _c.codewords(), "but the decoder still returns a codeword, with no warning"
assert hamming_distance(_fixed, _cw) == 3, \
    f"the decoder adds a third error: distance {hamming_distance(_fixed, _cw)}"
assert _err == [0, 0, 1, 0, 0, 0, 0], f"it flipped position 2, got {_err!r}"
'''},
                    {"name": "the other codes, and the Singleton bound", "code": r'''
_r3 = repetition_code(3)
assert (_r3.n, _r3.k, _r3.min_distance()) == (3, 1, 3), \
    f"got n={_r3.n}, k={_r3.k}, d={_r3.min_distance()}"
assert _r3.decode([1, 0, 1])[0] == [1, 1, 1], "majority vote, by syndrome"
_p4 = parity_code(4)
assert (_p4.n, _p4.k, _p4.min_distance()) == (5, 4, 2), \
    f"got n={_p4.n}, k={_p4.k}, d={_p4.min_distance()}"
assert _p4.encode([1, 0, 1, 1]) == [1, 0, 1, 1, 1], "the parity bit makes the weight even"
_h4 = hamming_code(4)
assert (_h4.n, _h4.k, _h4.min_distance()) == (15, 11, 3), \
    f"got n={_h4.n}, k={_h4.k}, d={_h4.min_distance()}"
for _c in (_r3, _p4, _h4, hamming_code(3)):
    assert _c.min_distance() <= _c.n - _c.k + 1, \
        f"the Singleton bound d <= n - k + 1 fails for n={_c.n}, k={_c.k}"
_cw = _h4.encode([1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1])
for _j in (0, 7, 14):
    _rx = list(_cw)
    _rx[_j] ^= 1
    assert _h4.decode(_rx)[0] == _cw, f"(15,11) failed to repair position {_j}"
'''},
                    {"name": "coding lowers the bit error rate on a noisy link", "code": r'''
import random as _random

_c = hamming_code(3)
_rng = _random.Random(21)
_p = 0.02
_bare, _coded = 0, 0
for _trial in range(3000):
    _msg = [_rng.randrange(2) for _ in range(4)]
    _bare += sum(1 for _ in range(4) if _rng.random() < _p)
    _cw = _c.encode(_msg)
    _rx = [_b ^ (1 if _rng.random() < _p else 0) for _b in _cw]
    _coded += hamming_distance(_c.decode(_rx)[0], _cw)
assert _bare > 150, f"a sanity check on the channel: {_bare} errors in 12000 bare bits"
assert _coded < _bare, (
    f"the coded link left {_coded} wrong bits against {_bare} uncoded — "
    "at p = 0.02 the code should repair most single-error blocks")
'''},
                    {"name": "the class refuses what is not a code", "code": r'''
for _bad in [[], [[]], [[1, 0], [1, 0, 1]], [[1, 2, 0]], [[1, 0, 1], [1, 0, 1]],
             [[1, 1, 0], [0, 1, 1], [1, 0, 1]]]:
    try:
        LinearCode(_bad)
        assert False, f"LinearCode({_bad!r}) should raise ValueError"
    except ValueError:
        pass
_c = hamming_code(3)
for _bad in [[1, 0, 1], [1, 0, 1, 1, 0, 1, 0, 1], [1, 0, 1, 1, 0, 1, 2]]:
    try:
        _c.syndrome(_bad)
        assert False, f"syndrome({_bad!r}) should raise ValueError"
    except ValueError:
        pass
for _bad in (1, 0, -3, 2.5):
    try:
        hamming_code(_bad)
        assert False, f"hamming_code({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a measured link: compress it, protect it, count what survives",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
Build the whole chain in `link.py` and drive it from `main.py`. The ridge station's
weather log is compressed with a canonical Huffman coder, protected with a (7,4)
Hamming coder, pushed through a seeded binary symmetric channel, corrected, and
decoded — and every stage reports a number that came from a real run rather than
from a formula.

The two coders pull in opposite directions and that is the point. The source coder
removes redundancy until the stream is near its entropy; the channel coder puts a
different, structured redundancy back. Compressed data is also brittle: one surviving
bit error can desynchronise a Huffman decoder and lose the rest of the message, which
is why the residual bit count and the exact-match flag are both reported.

## `SourceCoder(counts)`

- `counts` maps a symbol to a positive weight. `ValueError` for an empty mapping or a
  weight that is not strictly positive.
- `.lengths` — symbol to codeword length, from a Huffman merge that breaks ties by
  taking whichever item entered the queue first.
- `.code` — the **canonical** code built from `.lengths` alone: sort by
  `(length, symbol)`, give the first the all-zeros word of its length, then add one
  and shift left by the increase in length.
- `.encode(symbols)` — the codewords concatenated. `ValueError` for a symbol the
  alphabet does not have.
- `.decode(bits)` — the symbols. `ValueError` for a non-bit character, and for a
  stream that ends part-way through a codeword.
- `.entropy()` — the entropy of the count distribution, in bits per symbol.
- `.expected_length()` — the average codeword length under those same counts.

```text
SourceCoder({"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}).code
    == {"clear": "0", "cloud": "10", "rain": "110", "storm": "111"}
```

## `ChannelCoder()`

The systematic (7,4) Hamming code, with `BLOCK = 4` and `WORD = 7` as class
attributes.

- `.protect(bits)` — pad the payload with zeros to a whole number of 4-bit blocks,
  encode each block to 7 bits, and concatenate. `ValueError` for a non-bit character.
- `.recover(bits)` — for each 7-bit word, compute the syndrome, look up the
  single-bit coset leader, correct, and keep the leading 4 bits. `ValueError` unless
  the length is a multiple of 7 and every character is a bit.

```text
ChannelCoder().protect("1011")  == "1011010"
ChannelCoder().recover("1001010") == "1011"      one bit repaired
len(ChannelCoder().protect("10110")) == 14       padded to two blocks
```

## The link

- `bsc(bits, p, seed=0)` — one `random.Random(seed).random()` draw per bit, in
  order; flip when the draw is below `p`.
- `inject(bits, positions)` — flip exactly the listed positions, for tests that must
  not depend on a random draw. `ValueError` for a position outside the string.
- `capacity_bsc(p)` — `1 - H2(p)`, with `capacity_bsc(0) == capacity_bsc(1) == 1`.
- `link(symbols, counts, p=0.0, seed=0, errors=None)` — run the whole chain and
  return a dict with exactly these keys:

```text
symbols          how many symbols went in
entropy_bits     symbols * SourceCoder(counts).entropy()
source_bits      length of the compressed stream
channel_bits     length of the protected stream
raw_errors       bits the channel actually flipped
residual_errors  compressed-stream bits still wrong after correction
recovered        the decoded symbol list, or None if the decode raised
exact            whether `recovered` equals the input list
```

When `errors` is given it replaces the channel: those positions are flipped and `p`
and `seed` are ignored. A decode that fails must be reported as `recovered = None`
and `exact = False`, never swallowed into a partial list.

## `main.py`

Build a 2000-symbol log by sampling the ridge counts with `random.Random(411)`, run
the link at a few error rates, and print a table with the source bits, channel bits,
flipped bits, residual bits and the exact flag — then the entropy per symbol, the
channel uses per symbol, and what capacity says the floor is. At `p = 0.01` this
link spends 3.087 channel uses per symbol where capacity allows 1.904, and saying so
is part of the deliverable.
''',
        "deliverables": [
            "`link.py` — `SourceCoder`, `ChannelCoder`, `bsc`, `inject`, `capacity_bsc` and `link`, importable with no side effects",
            "`main.py` — samples a 2000-symbol weather log, runs the link at several error rates and prints the measured table",
            "A canonical Huffman source coder whose decoder is rebuilt from the codeword lengths alone, so a real format could ship the lengths",
            "A (7,4) Hamming channel coder that pads the payload to whole blocks and repairs one error in every seven-bit word by syndrome lookup",
            "A measured comparison: bits the channel flipped against bits still wrong after correction, from one run rather than from a binomial formula",
            "An honest failure path: a corrupted stream that no longer decodes is reported as `recovered = None`, not as a truncated message",
        ],
        "constraints": [
            "Standard library only — `heapq`, `math` and `random` are all you need",
            "`link.py` must define things only; importing it must print nothing and build no message",
            "Seed every channel. An unseeded run is a measurement nobody else can reproduce, and the checks assert exact counts",
            "The source decoder must be driven by the canonical code rebuilt from the lengths, not by a table smuggled out of the encoder",
            "`residual_errors` and `raw_errors` must both be counted from the actual bit strings, never estimated from `p`",
        ],
        "rubric": [
            {"criterion": "Source coding correctness", "weight": 30,
             "evidence": "The canonical code matches the lengths exactly, every message round-trips, the expected length sits between H and H+1, and a truncated stream raises rather than returning a short list."},
            {"criterion": "Channel coding correctness", "weight": 30,
             "evidence": "protect/recover is the identity with no noise at every payload length, and a single flip at each of the seven positions in a block is repaired, checked at all of them."},
            {"criterion": "End-to-end measurement", "weight": 25,
             "evidence": "link() reports source bits, channel bits, flipped bits and residual bits counted from the strings themselves, and the same seed reproduces the same numbers."},
            {"criterion": "Structure and honesty about limits", "weight": 15,
             "evidence": "link.py imports cleanly with no output, main.py prints the table, and a stream that no longer decodes is reported as a failure rather than as a partial result."},
        ],
        "hints": [
            "Build the canonical code from the lengths and then invert it once into a bit-string-to-symbol table; the decoder accumulates bits and looks the buffer up after each one.",
            "`protect` pads with `(-len(bits)) % 4` zeros. `recover` returns four bits per seven-bit word, so the caller trims to the original `source_bits` length — the padding is not the caller's business but the trim is.",
            "The (7,4) syndrome table has eight entries: the all-zero error and the seven single-bit ones. Build it once in `__init__` rather than per word.",
            "Count `raw_errors` by zipping the protected and received strings, not by counting how many draws fell below `p`. The two agree in expectation and not in any particular run.",
            "Wrap the final `decode` in `try`/`except ValueError` and record `None`. A Huffman decoder fed a corrupted stream either raises part-way through a codeword or returns a plausible wrong message, and both are failures worth reporting.",
        ],
        "files": [
            {"name": "link.py", "content": r'''
import heapq
import math
import random

HAMMING_G = [[1, 0, 0, 0, 0, 1, 1],
             [0, 1, 0, 0, 1, 0, 1],
             [0, 0, 1, 0, 1, 1, 0],
             [0, 0, 0, 1, 1, 1, 1]]
HAMMING_H = [[0, 1, 1, 1, 1, 0, 0],
             [1, 0, 1, 1, 0, 1, 0],
             [1, 1, 0, 1, 0, 0, 1]]


class SourceCoder:
    """Canonical Huffman over a symbol alphabet."""

    def __init__(self, counts):
        # your code here
        pass

    def encode(self, symbols):
        """The codewords, concatenated."""
        # your code here

    def decode(self, bits):
        """The symbols the bit string spells out."""
        # your code here

    def entropy(self):
        """The entropy of the count distribution, in bits per symbol."""
        # your code here

    def expected_length(self):
        """The average codeword length under those counts."""
        # your code here


class ChannelCoder:
    """The systematic (7,4) Hamming code, applied block by block."""

    BLOCK = 4
    WORD = 7

    def __init__(self):
        # your code here
        pass

    def protect(self, bits):
        """Pad to whole blocks and encode each one to seven bits."""
        # your code here

    def recover(self, bits):
        """Correct each seven-bit word and keep its four payload bits."""
        # your code here


def bsc(bits, p, seed=0):
    """One draw per bit; flip when it lands below p."""
    # your code here


def inject(bits, positions):
    """Flip exactly these positions, so a check need not depend on a draw."""
    # your code here


def capacity_bsc(p):
    """1 - H2(p), the capacity of a binary symmetric channel."""
    # your code here


def link(symbols, counts, p=0.0, seed=0, errors=None):
    """Compress, protect, transmit, correct, decode — and report the counts."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from link import link, capacity_bsc

# Sample a 2000-symbol weather log from the ridge counts with random.Random(411),
# run it through the link at p = 0.0, 0.001 and 0.01, and print a table of
# source bits, channel bits, flipped bits, residual bits and the exact flag.
# Then print the entropy per symbol, the channel uses per symbol, and the floor
# capacity allows at p = 0.01.
# your code here
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "link.py", "content": r'''
import heapq
import math
import random

HAMMING_G = [[1, 0, 0, 0, 0, 1, 1],
             [0, 1, 0, 0, 1, 0, 1],
             [0, 0, 1, 0, 1, 1, 0],
             [0, 0, 0, 1, 1, 1, 1]]
HAMMING_H = [[0, 1, 1, 1, 1, 0, 0],
             [1, 0, 1, 1, 0, 1, 0],
             [1, 1, 0, 1, 0, 0, 1]]


class SourceCoder:
    """Canonical Huffman over a symbol alphabet."""

    def __init__(self, counts):
        if not counts:
            raise ValueError("an empty alphabet codes nothing")
        for sym, w in counts.items():
            if w <= 0:
                raise ValueError(f"weight {w!r} for {sym!r} is not positive")
        self.counts = dict(counts)
        self.lengths = self._huffman(self.counts)
        self.code = self._canonical(self.lengths)
        # the decoder is built from the canonical code, which comes from the lengths
        # alone — a real format ships the lengths and rebuilds this table
        self._table = {word: sym for sym, word in self.code.items()}

    @staticmethod
    def _huffman(weights):
        syms = list(weights)
        if len(syms) == 1:
            return {syms[0]: 1}
        heap = [(weights[s], i, [s]) for i, s in enumerate(syms)]
        heapq.heapify(heap)
        order, depth = len(syms), {s: 0 for s in syms}
        while len(heap) > 1:
            w1, _, g1 = heapq.heappop(heap)
            w2, _, g2 = heapq.heappop(heap)
            for s in g1 + g2:
                depth[s] += 1
            heapq.heappush(heap, (w1 + w2, order, g1 + g2))
            order += 1
        return depth

    @staticmethod
    def _canonical(lengths):
        code, value, prev = {}, 0, None
        for sym, length in sorted(lengths.items(), key=lambda kv: (kv[1], kv[0])):
            if prev is not None:
                value = (value + 1) << (length - prev)
            code[sym] = format(value, "0%db" % length)
            prev = length
        return code

    def encode(self, symbols):
        """The codewords, concatenated."""
        out = []
        for s in symbols:
            if s not in self.code:
                raise ValueError(f"no codeword for {s!r}")
            out.append(self.code[s])
        return "".join(out)

    def decode(self, bits):
        """The symbols the bit string spells out."""
        out, buf = [], ""
        for ch in bits:
            if ch not in "01":
                raise ValueError(f"{ch!r} is not a bit")
            buf += ch
            if buf in self._table:
                out.append(self._table[buf])
                buf = ""
        if buf:
            raise ValueError(f"the stream ends mid-codeword on {buf!r}")
        return out

    def entropy(self):
        """The entropy of the count distribution, in bits per symbol."""
        n = math.fsum(self.counts.values())
        return -math.fsum((c / n) * math.log2(c / n) for c in self.counts.values() if c > 0)

    def expected_length(self):
        """The average codeword length under those counts."""
        n = math.fsum(self.counts.values())
        return math.fsum(c * self.lengths[s] for s, c in self.counts.items()) / n


class ChannelCoder:
    """The systematic (7,4) Hamming code, applied block by block."""

    BLOCK = 4
    WORD = 7

    def __init__(self):
        # eight syndromes: the clean word and the seven single-bit errors
        self.table = {}
        for j in range(-1, self.WORD):
            e = [0] * self.WORD
            if j >= 0:
                e[j] = 1
            self.table[tuple(self._syndrome(e))] = e

    @staticmethod
    def _syndrome(word):
        return [sum(h * w for h, w in zip(row, word)) % 2 for row in HAMMING_H]

    def protect(self, bits):
        """Pad to whole blocks and encode each one to seven bits."""
        if not isinstance(bits, str) or set(bits) - {"0", "1"}:
            raise ValueError("a payload is a string of 0 and 1")
        padded = bits + "0" * ((-len(bits)) % self.BLOCK)
        out = []
        for i in range(0, len(padded), self.BLOCK):
            word = [0] * self.WORD
            for bit, row in zip(padded[i:i + self.BLOCK], HAMMING_G):
                if bit == "1":
                    word = [a ^ b for a, b in zip(word, row)]
            out.append("".join(str(b) for b in word))
        return "".join(out)

    def recover(self, bits):
        """Correct each seven-bit word and keep its four payload bits."""
        if not isinstance(bits, str) or set(bits) - {"0", "1"}:
            raise ValueError("a protected stream is a string of 0 and 1")
        if len(bits) % self.WORD:
            raise ValueError(f"{len(bits)} bits is not a whole number of {self.WORD}-bit words")
        out = []
        for i in range(0, len(bits), self.WORD):
            word = [int(c) for c in bits[i:i + self.WORD]]
            e = self.table[tuple(self._syndrome(word))]
            fixed = [a ^ b for a, b in zip(word, e)]
            out.append("".join(str(b) for b in fixed[:self.BLOCK]))
        return "".join(out)


def bsc(bits, p, seed=0):
    """One draw per bit; flip when it lands below p."""
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"{p!r} is not a probability")
    if not isinstance(bits, str) or set(bits) - {"0", "1"}:
        raise ValueError("a transmission is a string of 0 and 1")
    rng = random.Random(seed)
    return "".join(("1" if c == "0" else "0") if rng.random() < p else c for c in bits)


def inject(bits, positions):
    """Flip exactly these positions, so a check need not depend on a draw."""
    out = list(bits)
    for i in positions:
        if not 0 <= i < len(out):
            raise ValueError(f"position {i!r} is outside a {len(out)}-bit stream")
        out[i] = "1" if out[i] == "0" else "0"
    return "".join(out)


def capacity_bsc(p):
    """1 - H2(p), the capacity of a binary symmetric channel."""
    if not 0.0 <= p <= 1.0:
        raise ValueError(f"{p!r} is not a probability")
    if p in (0.0, 1.0):
        return 1.0        # a channel that always flips is noiseless: invert it
    return 1.0 + p * math.log2(p) + (1 - p) * math.log2(1 - p)


def link(symbols, counts, p=0.0, seed=0, errors=None):
    """Compress, protect, transmit, correct, decode — and report the counts."""
    symbols = list(symbols)
    coder = SourceCoder(counts)
    channel = ChannelCoder()
    source = coder.encode(symbols)
    protected = channel.protect(source)
    received = inject(protected, errors) if errors is not None else bsc(protected, p, seed)
    raw = sum(1 for a, b in zip(protected, received) if a != b)
    payload = channel.recover(received)[:len(source)]
    residual = sum(1 for a, b in zip(source, payload) if a != b)
    try:
        recovered = coder.decode(payload)
    except ValueError:
        recovered = None      # a corrupted stream that no longer parses is a failure
    return {
        "symbols": len(symbols),
        "entropy_bits": coder.entropy() * len(symbols),
        "source_bits": len(source),
        "channel_bits": len(protected),
        "raw_errors": raw,
        "residual_errors": residual,
        "recovered": recovered,
        "exact": recovered == symbols,
    }
'''},
            {"name": "main.py", "content": r'''
import random

from link import link, capacity_bsc

COUNTS = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}

rng = random.Random(411)
pool = [s for s, n in COUNTS.items() for _ in range(n)]
log = [rng.choice(pool) for _ in range(2000)]

print("p        source  channel  flipped  residual  exact")
for p in (0.0, 0.001, 0.01):
    r = link(log, COUNTS, p=p, seed=7)
    print(f"{p:<9}{r['source_bits']:<8}{r['channel_bits']:<9}"
          f"{r['raw_errors']:<9}{r['residual_errors']:<10}{r['exact']}")

r = link(log, COUNTS, p=0.01, seed=7)
per_symbol = r["entropy_bits"] / r["symbols"]
c = capacity_bsc(0.01)
print()
print(f"entropy        {per_symbol:.4f} bits per symbol")
print(f"channel uses   {r['channel_bits'] / r['symbols']:.4f} per symbol")
print(f"capacity floor {per_symbol / c:.4f} per symbol, at capacity {c:.4f}")
'''},
        ],
        "tests": [
            {"name": "the source coder builds the canonical code from the counts", "code": r'''
import math as _math
import random as _random
from link import SourceCoder

_counts = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}
_sc = SourceCoder(_counts)
assert _sc.lengths == {"clear": 1, "cloud": 2, "rain": 3, "storm": 3}, f"got {_sc.lengths!r}"
assert _sc.code == {"clear": "0", "cloud": "10", "rain": "110", "storm": "111"}, f"got {_sc.code!r}"
assert abs(_sc.entropy() - 1.7499997836568824) < 1e-9, f"got {_sc.entropy()!r}"
assert abs(_sc.expected_length() - 1.75) < 1e-9, f"got {_sc.expected_length()!r}"
assert _sc.entropy() <= _sc.expected_length() + 1e-9 < _sc.entropy() + 1.0
assert _sc.encode(["clear", "clear", "cloud", "clear", "rain"]) == "00100110", \
    f"got {_sc.encode(['clear', 'clear', 'cloud', 'clear', 'rain'])!r}"
_rng = _random.Random(2)
for _trial in range(20):
    _msg = [_rng.choice(list(_counts)) for _ in range(_rng.randrange(0, 80))]
    assert _sc.decode(_sc.encode(_msg)) == _msg, f"round trip failed on {_msg!r}"
for _bad in [{}, {"a": 0}, {"a": 3, "b": -1}]:
    try:
        SourceCoder(_bad)
        assert False, f"SourceCoder({_bad!r}) should raise ValueError"
    except ValueError:
        pass
for _bad in ["11", "1", "01012"]:
    try:
        _sc.decode(_bad)
        assert False, f"decode({_bad!r}) should raise ValueError"
    except ValueError:
        pass
try:
    _sc.encode(["clear", "fog"])
    assert False, "an unknown symbol should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "the channel coder is the (7,4) Hamming code", "code": r'''
import random as _random
from link import ChannelCoder

_cc = ChannelCoder()
assert (_cc.BLOCK, _cc.WORD) == (4, 7), f"got BLOCK={_cc.BLOCK}, WORD={_cc.WORD}"
assert _cc.protect("1011") == "1011010", f"got {_cc.protect('1011')!r}"
assert _cc.protect("0000") == "0" * 7, "the zero block is the zero word"
assert _cc.protect("") == "" and _cc.recover("") == "", "an empty payload is empty"
assert len(_cc.protect("10110")) == 14, "five bits pad to two blocks"
assert _cc.recover(_cc.protect("10110")) == "10110000", "recover returns whole blocks"
_rng = _random.Random(5)
for _trial in range(40):
    _bits = "".join(_rng.choice("01") for _ in range(_rng.randrange(0, 40)))
    _pad = "0" * ((-len(_bits)) % 4)
    assert _cc.recover(_cc.protect(_bits)) == _bits + _pad, \
        f"clean round trip failed on {_bits!r}"
    assert len(_cc.protect(_bits)) == 7 * ((len(_bits) + 3) // 4), \
        f"protected length wrong for {len(_bits)} bits"
for _bad in ["0101010101010", "012345", "1"]:
    try:
        _cc.recover(_bad)
        assert False, f"recover({_bad!r}) should raise ValueError"
    except ValueError:
        pass
try:
    _cc.protect("10a1")
    assert False, "protect should raise ValueError on a non-bit"
except ValueError:
    pass
'''},
            {"name": "one error anywhere in a seven-bit word is repaired", "code": r'''
import itertools as _it
from link import ChannelCoder, inject

_cc = ChannelCoder()
for _nibble in _it.product("01", repeat=4):
    _payload = "".join(_nibble)
    _word = _cc.protect(_payload)
    assert _cc.recover(_word) == _payload, f"clean word {_word!r} did not survive"
    for _j in range(7):
        _broken = inject(_word, [_j])
        assert _cc.recover(_broken) == _payload, (
            f"{_payload!r} protected as {_word!r}, flipped at {_j} -> {_broken!r}, "
            f"recovered as {_cc.recover(_broken)!r}")
_long = _cc.protect("1011" * 60)
_hits = [_b * 7 + (_b % 7) for _b in range(len(_long) // 7)]
assert len(_hits) == 60, f"60 blocks, got {len(_hits)}"
assert _cc.recover(inject(_long, _hits)) == "1011" * 60, \
    "one error in every block, all of them repairable"
try:
    inject("0101", [9])
    assert False, "inject should raise ValueError outside the stream"
except ValueError:
    pass
'''},
            {"name": "the noiseless link is exact and its numbers agree", "code": r'''
import random as _random
from link import SourceCoder, link

_counts = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}
_rng = _random.Random(411)
_pool = [s for s, n in _counts.items() for _ in range(n)]
_log = [_rng.choice(_pool) for _ in range(2000)]
_r = link(_log, _counts, p=0.0, seed=7)
assert set(_r) == {"symbols", "entropy_bits", "source_bits", "channel_bits",
                   "raw_errors", "residual_errors", "recovered", "exact"}, \
    f"the report keys were {sorted(_r)}"
assert _r["symbols"] == 2000, f"got {_r['symbols']!r}"
assert _r["source_bits"] == len(SourceCoder(_counts).encode(_log)), \
    "source_bits must be the length of the compressed stream itself"
assert _r["channel_bits"] == 7 * ((_r["source_bits"] + 3) // 4), \
    f"got {_r['channel_bits']!r} channel bits for {_r['source_bits']!r} source bits"
assert _r["raw_errors"] == 0 and _r["residual_errors"] == 0, f"got {_r!r}"
assert _r["exact"] is True and _r["recovered"] == _log, "a clean link loses nothing"
assert abs(_r["entropy_bits"] - 2000 * SourceCoder(_counts).entropy()) < 1e-6
'''},
            {"name": "a seeded noisy link reproduces its own numbers", "code": r'''
import random as _random
from link import link

_counts = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}
_rng = _random.Random(411)
_pool = [s for s, n in _counts.items() for _ in range(n)]
_log = [_rng.choice(_pool) for _ in range(2000)]
_a = link(_log, _counts, p=0.01, seed=7)
_b = link(_log, _counts, p=0.01, seed=7)
assert _a == _b, "the same seed must give the same run, or nothing here is measurable"
assert _a["raw_errors"] == 63, f"p=0.01 with seed 7 flips 63 of 6174 bits, got {_a['raw_errors']!r}"
assert _a["residual_errors"] == 2, f"two survive correction, got {_a['residual_errors']!r}"
assert _a["exact"] is False, "two residual bit errors are enough to break the message"
_c = link(_log, _counts, p=0.01, seed=8)
assert _c["raw_errors"] != _a["raw_errors"] or _c["residual_errors"] != _a["residual_errors"], \
    "a different seed must give a different run"
_d = link(_log, _counts, p=0.001, seed=7)
assert _d["raw_errors"] == 7 and _d["residual_errors"] == 0 and _d["exact"] is True, \
    f"at p=0.001 every flip is repairable, got {_d['raw_errors']!r}/{_d['residual_errors']!r}"
'''},
            {"name": "correction removes most of what the channel broke", "code": r'''
import random as _random
from link import link

_counts = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}
_rng = _random.Random(411)
_pool = [s for s, n in _counts.items() for _ in range(n)]
_log = [_rng.choice(_pool) for _ in range(2000)]
_r = link(_log, _counts, p=0.02, seed=3)
assert _r["raw_errors"] > 0, "a p=0.02 channel over 6174 bits must break something"
assert _r["residual_errors"] > 0, (
    "at p=0.02 some seven-bit block gets two errors, so the claim below is not vacuous")
assert _r["residual_errors"] * 4 < _r["raw_errors"], (
    f"the channel flipped {_r['raw_errors']} bits and {_r['residual_errors']} survived "
    "correction — a (7,4) code should repair the great majority of them")
_forced = link(_log, _counts, errors=[b * 7 + (b % 7) for b in range(882)])
assert _forced["raw_errors"] == 882, f"one flip per block, got {_forced['raw_errors']!r}"
assert _forced["residual_errors"] == 0, "one error per block is exactly what the code repairs"
assert _forced["exact"] is True and _forced["recovered"] == _log
'''},
            {"name": "compression is real, and reported honestly", "code": r'''
import math as _math
import random as _random
from link import SourceCoder, link

_counts = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}
_rng = _random.Random(411)
_pool = [s for s, n in _counts.items() for _ in range(n)]
_log = [_rng.choice(_pool) for _ in range(2000)]
_r = link(_log, _counts, p=0.0, seed=1)
_per = _r["source_bits"] / _r["symbols"]
assert _per < 2.0, f"a two-bit numbering costs 2.0 a symbol; the coder spent {_per!r}"
assert _per > 1.7, f"and it cannot go below the entropy of the source: {_per!r}"
_uniform = {c: 1 for c in "abcd"}
_umsg = [_rng.choice("abcd") for _ in range(400)]
_ur = link(_umsg, _uniform, p=0.0, seed=1)
assert _ur["source_bits"] == 800, \
    f"a uniform four-symbol source offers nothing to compress, got {_ur['source_bits']!r}"
assert _ur["exact"] is True
'''},
            {"name": "a stream that no longer decodes is reported as a failure", "code": r'''
import random as _random
from link import link, capacity_bsc

_counts = {"clear": 1826, "cloud": 913, "rain": 456, "storm": 457}
_rng = _random.Random(411)
_pool = [s for s, n in _counts.items() for _ in range(n)]
_log = [_rng.choice(_pool) for _ in range(300)]
_wrecked = link(_log, _counts, errors=list(range(0, 400)))
assert _wrecked["residual_errors"] > 0, "400 adjacent flips must survive a (7,4) code"
assert _wrecked["exact"] is False, "and the report must say the message did not survive"
assert _wrecked["recovered"] is None or _wrecked["recovered"] != _log, \
    "a wrong message must never be reported as the original"
assert abs(capacity_bsc(0.01) - 0.9192068641040888) < 1e-9, f"got {capacity_bsc(0.01)!r}"
assert capacity_bsc(0.0) == 1.0 and capacity_bsc(1.0) == 1.0, \
    "a channel that always flips is noiseless"
assert capacity_bsc(0.5) < 1e-12, "a coin flip carries nothing"
for _bad in (-0.1, 1.5):
    try:
        capacity_bsc(_bad)
        assert False, f"capacity_bsc({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "link.py is import-clean and main.py prints the table", "code": r'''
_src = open("link.py").read()
assert "print(" not in _src, "link.py defines the library; the printing belongs in main.py"
assert "residual" in _out and "channel" in _out, (
    f"main.py should print the measured table; stdout was {_out[:400]!r}")
assert "capacity" in _out, "and what capacity says the floor is"
'''},
        ],
    },
}
