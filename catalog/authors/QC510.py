"""QC510 — Advanced Elective: Quantum Computing. Author module."""

# The shared state-vector library handed to students from module 3 onward. They
# build the same thing themselves in module 2 and again, properly, in the capstone.
QLIB = r'''
"""qlib.py — a minimal state-vector toolkit. Read it; you wrote most of it in M2.

Conventions used throughout this course
---------------------------------------
* An n-qubit state is a list of 2**n complex amplitudes.
* Basis index k encodes the register in big-endian order: qubit 0 is the most
  significant bit, qubit n-1 the least. So on 3 qubits, |011> is index 3 and the
  bit of qubit q sits at position (n - 1 - q).
* Every apply_* function returns a NEW list. Nothing here mutates its argument.
"""

import cmath
import math
import random

SQRT2 = math.sqrt(2)

I = [[1 + 0j, 0j], [0j, 1 + 0j]]
X = [[0j, 1 + 0j], [1 + 0j, 0j]]
Y = [[0j, -1j], [1j, 0j]]
Z = [[1 + 0j, 0j], [0j, -1 + 0j]]
H = [[1 / SQRT2 + 0j, 1 / SQRT2 + 0j], [1 / SQRT2 + 0j, -1 / SQRT2 + 0j]]
S = [[1 + 0j, 0j], [0j, 1j]]
T = [[1 + 0j, 0j], [0j, cmath.exp(1j * math.pi / 4)]]


def phase(angle):
    """The diagonal phase gate diag(1, exp(i*angle))."""
    return [[1 + 0j, 0j], [0j, cmath.exp(1j * angle)]]


def ry(theta):
    """Rotation by theta about the Bloch y axis."""
    c = math.cos(theta / 2)
    s = math.sin(theta / 2)
    return [[c + 0j, -s + 0j], [s + 0j, c + 0j]]


def n_qubits(state):
    """How many qubits a state vector describes. ValueError if the length is bad."""
    size = len(state)
    if size < 2:
        raise ValueError("a state needs at least two amplitudes")
    n = size.bit_length() - 1
    if 2 ** n != size:
        raise ValueError(f"state length {size} is not a power of two")
    return n


def zero_state(n):
    """The n-qubit register |00...0>."""
    if n < 1:
        raise ValueError("need at least one qubit")
    state = [0j] * (2 ** n)
    state[0] = 1 + 0j
    return state


def basis_state(n, k):
    """The n-qubit computational basis state |k>."""
    if not 0 <= k < 2 ** n:
        raise ValueError(f"basis index {k} out of range for {n} qubits")
    state = [0j] * (2 ** n)
    state[k] = 1 + 0j
    return state


def bits(k, n):
    """Basis index k as a big-endian list of n bits."""
    return [(k >> (n - 1 - q)) & 1 for q in range(n)]


def apply_1q(state, gate, target):
    """Apply a 2x2 gate to one qubit of the register."""
    n = n_qubits(state)
    if not 0 <= target < n:
        raise ValueError(f"target qubit {target} out of range for {n} qubits")
    shift = n - 1 - target
    out = list(state)
    for k in range(len(state)):
        if (k >> shift) & 1:
            continue
        k1 = k | (1 << shift)
        a, b = state[k], state[k1]
        out[k] = gate[0][0] * a + gate[0][1] * b
        out[k1] = gate[1][0] * a + gate[1][1] * b
    return out


def apply_cnot(state, control, target):
    """Controlled-NOT: flip target where control is 1."""
    n = n_qubits(state)
    if control == target:
        raise ValueError("control and target must be different qubits")
    if not (0 <= control < n and 0 <= target < n):
        raise ValueError("qubit index out of range")
    cs = n - 1 - control
    ts = n - 1 - target
    out = list(state)
    for k in range(len(state)):
        if ((k >> cs) & 1) and not ((k >> ts) & 1):
            k1 = k | (1 << ts)
            out[k], out[k1] = state[k1], state[k]
    return out


def apply_cphase(state, control, target, angle):
    """Controlled phase: multiply the |11> subspace by exp(i*angle)."""
    n = n_qubits(state)
    if control == target:
        raise ValueError("control and target must be different qubits")
    if not (0 <= control < n and 0 <= target < n):
        raise ValueError("qubit index out of range")
    cs = n - 1 - control
    ts = n - 1 - target
    factor = cmath.exp(1j * angle)
    out = list(state)
    for k in range(len(state)):
        if ((k >> cs) & 1) and ((k >> ts) & 1):
            out[k] = state[k] * factor
    return out


def apply_swap(state, a, b):
    """Exchange two qubits of the register."""
    n = n_qubits(state)
    if not (0 <= a < n and 0 <= b < n):
        raise ValueError("qubit index out of range")
    if a == b:
        return list(state)
    sa = n - 1 - a
    sb = n - 1 - b
    out = list(state)
    for k in range(len(state)):
        if ((k >> sa) & 1) != ((k >> sb) & 1):
            out[k ^ (1 << sa) ^ (1 << sb)] = state[k]
    return out


def probabilities(state):
    """Born-rule probabilities. The input is normalised first."""
    norm = math.sqrt(sum(abs(a) ** 2 for a in state))
    if norm == 0:
        raise ValueError("the zero vector is not a state")
    return [abs(a / norm) ** 2 for a in state]


def measure(state, rng):
    """Sample one basis index using rng.random() and the Born rule."""
    u = rng.random()
    acc = 0.0
    probs = probabilities(state)
    for k, p in enumerate(probs):
        acc += p
        if u < acc:
            return k
    return len(probs) - 1


def sample_counts(state, shots, seed=7):
    """{basis index: count} over `shots` seeded measurements."""
    rng = random.Random(seed)
    counts = {}
    for _ in range(shots):
        k = measure(state, rng)
        counts[k] = counts.get(k, 0) + 1
    return counts
'''

COURSE = {
    "id": "QC510",
    "title": "Advanced Elective — Quantum Computing",
    "year": 5,
    "level": "Expert",
    "prereqs": ["MA121", "CS310"],
    "stack": ["Python", "Qiskit (reference)"],
    "credits": 10,
    "hours": 150,
    "icon": "⚛",
    "summary": (
        "Quantum computation from the linear algebra up, with no framework in the way: "
        "every amplitude, gate and measurement in this course is a complex number you "
        "manipulate yourself in plain Python. You build a state-vector simulator, use it "
        "to violate the CHSH inequality, and run Deutsch-Jozsa, Grover and the quantum "
        "Fourier transform on it, checking each against amplitudes you derive by hand."
    ),
    "outcomes": [
        "Represent a multi-qubit register as a normalised complex vector and read probabilities off it with the Born rule",
        "Implement single- and two-qubit gates as sparse updates over the tensor-product index structure",
        "Prepare the four Bell states and explain their correlations through marginal and joint statistics",
        "Compute a CHSH value that exceeds the local-hidden-variable bound of 2 and account for the excess",
        "Derive and verify the query advantage of Deutsch-Jozsa and the amplitude schedule of Grover search",
        "Build the quantum Fourier transform both as a matrix and as a gate circuit, and use it to extract a period",
        "Judge which claimed quantum speed-ups survive contact with the resource counts",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone build (60%).",
    "reading": [
        "Nielsen & Chuang, *Quantum Computation and Quantum Information*, 10th anniversary ed. — chapters 1-2, 4-6",
        "Mermin, *Quantum Computer Science: An Introduction* — chapters 1-3",
        "Aaronson, *Quantum Computing Since Democritus* — chapters 9-10, for the complexity framing",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Qubits, amplitudes and measurement",
            "summary": "A qubit is a unit vector in C^2; measurement is the only way out.",
            "concepts": [
                "A pure state is a unit vector in C^(2^n); global phase is unobservable",
                "The Born rule: outcome k has probability |a_k|^2, so amplitudes must be normalised",
                "Amplitudes are complex — relative phase is physical, and interference is its consequence",
                "Measurement is projective and irreversible: the post-measurement state is the collapsed one",
                "Finite sampling error falls as 1/sqrt(shots), which is why quantum experiments are repeated",
                "The Bloch sphere: theta = 2*acos(|a0|) and phi = arg(a1) - arg(a0) for one qubit",
            ],
            "read": [
                {
                    "title": "Two detectors, one photon, and the square that makes it add up",
                    "minutes": 14,
                    "body": r'''
A single photon arrives at a half-silvered mirror. Behind the mirror are two detectors,
one on the transmitted path and one on the reflected path. You send 20,000 photons
through, one at a time, and count: about 10,000 clicks on each detector, never both at
once, and no pattern in the order. So far this is a coin. The photon goes one way or the
other, and the mirror is a fair coin flip.

Now put a second half-silvered mirror where the two paths cross again, so that a photon
on either path meets it and can again go either way, and put the two detectors after
that. A coin-flip picture says each photon takes one path, flips again at the second
mirror, and the detectors split 50/50. They do not. With the path lengths matched, every
single photon lands on one detector and none on the other. Lengthen one path by half a
wavelength and it swaps: every photon lands on the other detector. Something the photon
carries along each path is adding up at the second mirror, and it can add to zero.
Probabilities cannot do that. A probability is never negative, so two of them cannot
cancel. Whatever the photon carries has a sign, and that is where a qubit starts.

## The number that carries the sign

Call the two paths $|0\rangle$ and $|1\rangle$ and give each a number, $a_0$ and $a_1$,
that can be negative, and in general complex. The pair $(a_0, a_1)$ is the state. The
first mirror sends $|0\rangle$ to $(a_0, a_1) = (1/\sqrt{2},\ 1/\sqrt{2})$; the second
mirror does the same thing to each path, and the two contributions to the $|1\rangle$
detector arrive as $+1/2$ and $-1/2$. They cancel. The contributions to $|0\rangle$
arrive as $+1/2$ and $+1/2$ and add to $1$. That reproduces the experiment, and it forces
two conclusions about how the numbers relate to the counts.

The counts must come from a quantity that is never negative, or the $-1/2$ would mean a
negative click rate. And the quantity must respect the fact that $(1/\sqrt{2}, 1/\sqrt{2})$
after the first mirror gave 50/50, while $(1, 0)$ before it gave everything on one
detector. Squaring does both: $|a_k|^2$ is never negative, $(1/\sqrt{2})^2 = 1/2$ matches
the half-and-half split, and $1^2 + 0^2 = 1$ matches a certain outcome. The rule that
outcome $k$ occurs with probability $|a_k|^2$ is the Born rule, and the beam splitter is
the experiment that makes it the only sensible choice. Squaring is also why the
$1/\sqrt{2}$ was there in the first place: the probabilities have to add to one, so the
amplitudes have to add to one *in squares*, which is to say the state is a unit vector.

Work that through with a state that is not symmetric. Take amplitudes proportional to
$(\sqrt{3}, 1)$, which is what a mirror that transmits three quarters of the light
produces.

```python
import math

amps = [math.sqrt(3), 1]
norm = math.sqrt(sum(abs(a) ** 2 for a in amps))
state = [a / norm for a in amps]
print("moduli:       ", [round(abs(a), 4) for a in state])
print("probabilities:", [round(abs(a) ** 2, 4) for a in state])
print("they sum to:  ", round(sum(abs(a) ** 2 for a in state), 12))
```

The norm is $\sqrt{3 + 1} = 2$, so the state is $(\sqrt{3}/2,\ 1/2) = (0.866, 0.5)$, and
the probabilities are $3/4$ and $1/4$. This is the state the lab's `sample_counts` test
feeds you with 20,000 shots and expects to see land within 2% of 0.75. The first job in
the lab, `normalise`, is this block's middle three lines, with one addition: the zero
vector has norm 0, there is nothing to divide by, and there is no experiment it
describes. That is a `ValueError`, not a list of `nan`.

## The mistake: reading the amplitude as the probability

The amplitude $0.866$ *looks* like a probability. It is between 0 and 1 and it is bigger
for the likelier outcome. People read it as one, and the reason it is tempting is that
for the symmetric state both readings give the same ranking. The damage shows on the
asymmetric one: $0.866$ against $0.5$ says the odds are about $1.7 : 1$, while the real
odds are $0.75 : 0.25 = 3 : 1$. Squaring stretches the gap. A state of $(0.99, 0.14)$
gives the second outcome about one time in fifty, not one in seven.

The same habit produces a second error in the other direction. Someone who has heard
"probability is the square" will build a state from probabilities by taking the square
root of each and stopping, which loses the sign and the phase. The photon experiment is
the reason that matters: $(1/\sqrt{2}, 1/\sqrt{2})$ and $(1/\sqrt{2}, -1/\sqrt{2})$ have
identical probabilities and opposite behaviour at the second mirror. The state is the
amplitudes. The probabilities are a shadow of it.

## Sampling: what 20,000 shots can and cannot tell you

A detector count is a sample, and a sample of a $3 : 1$ coin does not come out at
exactly $3 : 1$. The lab draws each shot with a single uniform random number: walk the
cumulative probabilities and stop at the first one that exceeds the draw. That is the
whole of `measure`, and it is the same thing a physical detector does with the
amplitudes, only with `random.Random` in place of the universe.

```python
import math
import random


def measure(probs, rng):
    u = rng.random()
    acc = 0.0
    for k, p in enumerate(probs):
        acc += p
        if u < acc:
            return k
    return len(probs) - 1


probs = [0.75, 0.25]
rng = random.Random(7)
for shots in (100, 10000, 1000000):
    zeros = sum(1 for _ in range(shots) if measure(probs, rng) == 0)
    seen = zeros / shots
    print(f"{shots:>8} shots: p0 = {seen:.4f}   error {abs(seen - 0.75):.4f}"
          f"   1/sqrt(shots) = {1 / math.sqrt(shots):.4f}")
```

With seed 7 the hundred-shot estimate is $0.78$, off by $0.03$; ten thousand shots give
$0.7497$; a million give $0.7499$. Each hundredfold increase in shots buys one more
decimal place, which is the $1/\sqrt{\text{shots}}$ law: the standard deviation of a
frequency estimate is $\sqrt{p(1-p)/\text{shots}}$, and for $p$ near a half that is
close to $1/(2\sqrt{\text{shots}})$. The table's third column is a generous bound on it.
This is why the lab's convergence test allows $0.02$ at 20,000 shots rather than
demanding $0.75$ exactly, and why every quantum experiment you will read about reports
thousands of shots: the answer is a distribution, and a single shot is one draw from it.

The `return len(probs) - 1` at the end is not decoration. Floating-point probabilities
can sum to $0.9999999999999999$, and a draw of $0.99999999999999995$ would walk off the
end of the list. Returning the last index there is the difference between a simulator
that works for a billion shots and one that crashes once a year.

## Relative phase is real; global phase is not

The photon carried a sign. In general it carries a complex phase, and the question is
which phases you can measure. Take three one-qubit states: $|+\rangle$ with amplitudes
$(1, 1)/\sqrt{2}$, a state with amplitudes $(1, i)/\sqrt{2}$, and $|+\rangle$ with every
amplitude multiplied by $e^{0.9i}$.

```python
import cmath
import math

r = 1 / math.sqrt(2)
plus = [r, r]                       # (|0> + |1>) / sqrt(2)
plus_i = [r, 1j * r]                # (|0> + i|1>) / sqrt(2)
spun = [a * cmath.exp(0.9j) for a in plus]   # |+> times a global phase


def probs(state):
    return [round(abs(a) ** 2, 4) for a in state]


def hadamard(state):
    a, b = state
    return [(a + b) / math.sqrt(2), (a - b) / math.sqrt(2)]


print("measured as they are:", probs(plus), probs(plus_i), probs(spun))
print("measured after H:    ", probs(hadamard(plus)), probs(hadamard(plus_i)),
      probs(hadamard(spun)))
```

Measured directly, all three give $[0.5, 0.5]$: the Born rule takes a modulus, and a
modulus forgets phase. That is the lab's `probabilities([1, 1j])` test, and it is the
same fact as the first beam splitter giving 50/50 whatever the path lengths. Now pass
them through a second mirror, which is what the Hadamard is. The $|+\rangle$ state gives
$[1, 0]$, the $(1, i)$ state stays at $[0.5, 0.5]$, and the spun state gives $[1, 0]$,
identical to $|+\rangle$.

Two rules fall out. The phase *between* the amplitudes changed the outcome of the second
measurement, so it is physical, and interference is the name for the way it acts. The
phase *common* to all the amplitudes changed nothing, before or after the Hadamard,
because a common factor $e^{i\alpha}$ multiplies every amplitude, every gate is linear so
it rides through unchanged, and $|e^{i\alpha}|^2 = 1$ removes it at the end. Two states
that differ by a global phase are the same state. The lab's `collapse` respects this by
keeping the phase of the surviving amplitude: `collapse([1, 1j], 1)` is `[0, 1j]`, not
`[0, 1]`. Both describe the same physics, and the test asks for the one that does not
throw information away.

## The sphere, and what its angles are

A one-qubit state has two complex amplitudes, which is four real numbers. Normalisation
removes one and global phase removes another, leaving two, and two real numbers place a
point on a sphere. Write the state with the freedom used up: choose the global phase so
that $a_0$ is real and non-negative, then normalisation lets you write
$a_0 = \cos(\theta/2)$ for some $\theta \in [0, \pi]$, and what is left of $a_1$ is its
modulus $\sin(\theta/2)$ and a phase $\phi$:

$$|\psi\rangle = \cos\frac{\theta}{2}\,|0\rangle + e^{i\phi}\sin\frac{\theta}{2}\,|1\rangle.$$

Read the two angles back off any state and you have the lab's `bloch_angles`. From
$|a_0| = \cos(\theta/2)$ comes $\theta = 2\arccos|a_0|$. From the phase of $a_1$
*relative* to $a_0$ comes $\phi = \arg a_1 - \arg a_0$, which is the same difference
whatever global phase the state arrived with.

```python
import cmath
import math


def bloch_angles(a0, a1):
    theta = 2 * math.acos(min(1.0, abs(a0)))
    if abs(a0) < 1e-12 or abs(a1) < 1e-12:
        return (round(theta, 4), 0.0)
    phi = (cmath.phase(a1) - cmath.phase(a0)) % (2 * math.pi)
    return (round(theta, 4), round(phi, 4))


r = 1 / math.sqrt(2)
print("|+>  ", bloch_angles(r, r))
print("|+i> ", bloch_angles(r, 1j * r))
print("|->  ", bloch_angles(r, -r))
print("|1>  ", bloch_angles(0, 1))
print("|+> spun by a global phase", bloch_angles(r * cmath.exp(0.9j), r * cmath.exp(0.9j)))
```

$|+\rangle$ sits on the equator at $(\pi/2, 0)$; $(1, i)/\sqrt{2}$ is a quarter turn
round at $(\pi/2, \pi/2)$; $|-\rangle$ is at $(\pi/2, \pi)$, diametrically opposite
$|+\rangle$, which is why the Hadamard could tell them apart perfectly; and $|1\rangle$ is
the south pole at $\theta = \pi$. The spun $|+\rangle$ lands exactly where $|+\rangle$
does, because the difference of the two phases cancels the common $0.9$. At either pole
one amplitude is zero and its phase is meaningless, so $\phi$ is undefined; the lab asks
you to report $0.0$ there, and the `min(1.0, ...)` guards `acos` against a modulus that
floating point has nudged to $1.0000000000000002$.

## Where it stops holding

Everything above is a *pure* state: one definite vector, with all the randomness in the
measurement. A qubit that has been left to interact with its surroundings, or a
photon whose source emits $|0\rangle$ half the time and $|1\rangle$ the other half, is
not described by any vector at all. Its two outcomes are 50/50, like $|+\rangle$, but a
Hadamard does not turn it into a certainty; the "phase between the amplitudes" that
interference needs does not exist, because there are no amplitudes, only a mixture.
Describing that takes a density matrix, and the Bloch sphere's interior, not its surface.
The sphere itself stops at one qubit: two qubits have six real parameters after the two
constraints, and no sphere holds six.

Measurement in this module always means measurement in the computational basis, asking
"which detector?" for $|0\rangle$ against $|1\rangle$. Asking a different question is
done by rotating first and then asking this one, which is how module 3 measures along an
angle. And the collapse rule is irreversible: after `collapse`, the state is a basis
vector, the other amplitude and its phase are gone, and no gate recovers them. The
photon that clicked on one detector cannot be asked which path it took.

The lab, *State vectors and the Born rule*, is this reading as six functions: `normalise`
is the unit-vector requirement, `probabilities` is the square, `measure` and
`sample_counts` are the single draw and the $1/\sqrt{\text{shots}}$ law, `collapse` is
the irreversible step with its phase kept, and `bloch_angles` is the two-parameter
picture with its two poles handled. Every test in it is one of the numbers worked out
above.
''',
                },
            ],
            "quiz": {
                "title": "Amplitudes, squares and what a shot count means",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A one-qubit state has amplitudes proportional to $(3, 4)$. What is the probability of measuring $|1\\rangle$?",
                        "opts": [
                            "$4/7$, the second amplitude's share of the total of the two amplitudes",
                            "$16/25$, the square of the second amplitude over the sum of squares",
                            "$4/5$, the second amplitude once the vector has unit norm",
                            "$2/5$, half the normalised amplitude since two outcomes share it",
                        ],
                        "a": 1,
                        "whys": [
                            r"Dividing by the sum of the amplitudes treats them as probabilities that need to add to one. They add to one in squares, so the normaliser is $\sqrt{9 + 16} = 5$, not $7$, and the answer is a square, not a share.",
                            r"The norm is $5$, the normalised state is $(0.6, 0.8)$, and $0.8^2 = 0.64$.",
                            r"$4/5$ is the normalised amplitude, which is the right intermediate number and the wrong final one. The Born rule squares it: $0.8$ as an amplitude is a $0.64$ probability, and reading the amplitude as the odds understates how lopsided the state is.",
                            r"Halving has no basis in the rule; the two outcomes do not split an amplitude between them. The probabilities come out of the squares $0.36$ and $0.64$, and those already sum to one without any sharing.",
                        ],
                        "why": r"""
Normalise first: $\sqrt{3^2 + 4^2} = 5$, so the state is $(0.6, 0.8)$. Then square:
$0.8^2 = 0.64 = 16/25$. The tempting wrong answers keep the amplitude as if it were
the probability, which happens to rank the outcomes correctly and to get every ratio
wrong; the square stretches a $4 : 3$ amplitude ratio into a $16 : 9$ probability
ratio, which is what the detectors see.
""",
                    },
                    {
                        "q": "Two states have amplitudes $(1, 1)/\\sqrt{2}$ and $(1, -1)/\\sqrt{2}$. Measured directly both give 50/50. What is true of them?",
                        "opts": [
                            "They are the same state, since a sign is a global phase and a global phase is never observable",
                            "They are different states, and a Hadamard before the measurement separates them perfectly",
                            "They are different states, but no measurement in any basis can distinguish them",
                            "They are the same state written in two bases, which is why the counts agree exactly",
                        ],
                        "a": 1,
                        "whys": [
                            r"The sign is on one amplitude, not both, so it is a relative phase and not a global one. Multiply every amplitude by $-1$ and you have the same state; flip the sign of one of them and you have moved to the opposite side of the Bloch sphere.",
                            r"H sends $(1, 1)/\sqrt{2}$ to $(1, 0)$ and $(1, -1)/\sqrt{2}$ to $(0, 1)$, so after it the two states are told apart with certainty.",
                            r"The computational basis cannot distinguish them, because the Born rule takes a modulus. That is a fact about one basis, not about all of them: interference at a second beam splitter is exactly a measurement that does distinguish them.",
                            r"Nothing here has changed basis; both amplitude lists are written in the same $|0\rangle, |1\rangle$ basis and they differ in one sign. Equal counts on one measurement is a much weaker thing than being the same state.",
                        ],
                        "why": r"""
The sign sits on one amplitude, so it is a relative phase, and relative phase is
physical. A direct measurement hides it because $|{-1}|^2 = |1|^2$. Pass both states
through a Hadamard and they become $(1, 0)$ and $(0, 1)$, which are told apart on
every single shot. The states are $|+\rangle$ and $|-\rangle$, opposite points on the
equator of the Bloch sphere, and "same probabilities in one basis" is not "same
state".
""",
                    },
                    {
                        "q": "You estimate a probability of about $0.5$ from 10,000 shots and want the error bar ten times smaller. How many shots does that take?",
                        "opts": [
                            "About 100,000: the error falls in proportion to the shot count",
                            "About 1,000,000: the error falls as the square root of the shot count",
                            "About 20,000: the error halves once the estimate has stabilised",
                            "It cannot be done by shots alone; the amplitude sets a floor on the error",
                        ],
                        "a": 1,
                        "whys": [
                            r"Tenfold shots buys a factor of $\sqrt{10} \approx 3.2$, not $10$. The error of a frequency estimate goes as $1/\sqrt{\text{shots}}$, so the shot count has to grow by the square of the improvement you want.",
                            r"The standard error is $\sqrt{p(1-p)/\text{shots}}$; a hundredfold increase in shots is the tenfold reduction.",
                            r"There is no point at which the estimate stabilises and the law changes; the scatter keeps shrinking as $1/\sqrt{\text{shots}}$ all the way down. Doubling the shots gets you a factor of $1.4$, not $2$.",
                            r"The amplitude sets the probability, not a floor on how well you can estimate it. Sampling error is a property of finite counts and shrinks without limit as the count grows; only the cost of the shots stops you.",
                        ],
                        "why": r"""
The standard deviation of a frequency estimate is $\sqrt{p(1-p)/\text{shots}}$, so
the error scales as $1/\sqrt{\text{shots}}$. A tenfold reduction needs a hundredfold
increase: from 10,000 shots to 1,000,000. The seeded run in the reading shows the same
law from the other side, with each hundredfold jump in shots adding one decimal place.
""",
                    },
                    {
                        "q": "A state $(1, i)/\\sqrt{2}$ is measured and the outcome is $|1\\rangle$. Which post-measurement state does the lab's `collapse` return, and why that one?",
                        "opts": [
                            "$(0, 1)$, because after a collapse only the outcome matters and every phase is reset to zero",
                            "$(0, i)$, because the surviving amplitude keeps its phase and is scaled to modulus one",
                            "$(0, i/\\sqrt{2})$, because the surviving amplitude is left exactly as it was",
                            "$(1, i)/\\sqrt{2}$, because measurement reads the state without changing it",
                        ],
                        "a": 1,
                        "whys": [
                            r"$(0, 1)$ and $(0, i)$ are the same physical state, so this is not wrong physics; it is the choice that discards information the amplitude carried. The lab asks for the phase kept, so its test for `collapse([1, 1j], 1)` expects `[0, 1j]`.",
                            r"Zero everywhere else, phase kept, modulus set to one: `amp / abs(amp)`.",
                            r"Leaving $i/\sqrt{2}$ in place gives a vector of norm $1/2$, which is not a state; the probabilities would sum to a half. Collapse renormalises, and the way to do it while keeping the phase is to divide the amplitude by its own modulus.",
                            r"Measurement is the one operation in the course that is not reversible. After the click the other amplitude is gone, and a second measurement returns $|1\rangle$ with certainty, which $(1, i)/\sqrt{2}$ would not do.",
                        ],
                        "why": r"""
Collapse zeroes every amplitude except the outcome's and rescales that one to modulus
$1$, keeping its direction in the complex plane: $i/\sqrt{2}$ divided by its modulus
is $i$. The state $(0, i)$ differs from $(0, 1)$ only by a global phase, so both are
physically the same, but the lab's convention is to keep what the amplitude carried
rather than reset it, and its test checks for exactly `[0j, 1j]`. Leaving the
amplitude unscaled produces a vector that is not normalised, and returning the
original state pretends measurement is reversible, which it is not.
""",
                    },
                    {
                        "q": "For which one-qubit state does the Bloch azimuth $\\phi$ have no defined value?",
                        "opts": [
                            "$|+\\rangle$, because its two amplitudes are equal so their phase difference vanishes",
                            "$|1\\rangle$, because the $|0\\rangle$ amplitude is zero and a zero has no phase at all",
                            "$(1, -1)/\\sqrt{2}$, because a negative amplitude has no angle in the complex plane",
                            "Any state multiplied by a global phase, because the common factor shifts $\\phi$ arbitrarily",
                        ],
                        "a": 1,
                        "whys": [
                            r"Equal amplitudes give a phase difference of $0$, which is a perfectly good value of $\phi$; $|+\rangle$ sits at $(\pi/2, 0)$. A difference that is zero is not a difference that is undefined.",
                            r"At a pole one amplitude is $0$, and $\arg 0$ is not a number; every $\phi$ describes the same point.",
                            r"A negative real number has a phase of $\pi$, so $(1, -1)/\sqrt{2}$ has $\phi = \pi$ and sits opposite $|+\rangle$ on the equator. The complex plane has an angle for every non-zero number, including the negative ones.",
                            r"A global phase adds the same angle to $\arg a_0$ and $\arg a_1$, and $\phi$ is their difference, so it cancels. The reading's spun $|+\rangle$ lands at exactly $(\pi/2, 0)$ for that reason.",
                        ],
                        "why": r"""
$\phi$ is $\arg a_1 - \arg a_0$, and at either pole one of those amplitudes is zero.
Zero has no argument, so the difference is not defined, and geometrically every
meridian meets at the pole anyway. The lab asks for $0.0$ there as a convention. The
other states all have two non-zero amplitudes and therefore a perfectly definite
$\phi$: $0$ for $|+\rangle$, $\pi$ for $|-\rangle$, and unchanged under any global
phase because the common factor cancels in the difference.
""",
                    },
                ],
            },
            "lab": {
                "title": "State vectors and the Born rule",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Write the measurement layer of a simulator. A state is a plain Python list of
complex numbers; index `k` is basis state `|k>`.

**`normalise(amplitudes)`** — a new list scaled to unit L2 norm. The zero vector
is not a state: raise `ValueError`.

```text
normalise([1, 1])       ->  [0.7071...+0j, 0.7071...+0j]
normalise([0, 0])       ->  ValueError
```

**`probabilities(state)`** — the Born-rule probabilities. Normalise first, so the
function works on any non-zero vector.

```text
probabilities([1, 1])   ->  [0.5, 0.5]
probabilities([1, 1j])  ->  [0.5, 0.5]      relative phase is invisible here
```

**`measure(state, rng)`** — draw one basis index. Take a single `rng.random()`
value in `[0, 1)` and walk the cumulative probabilities until you pass it.

**`sample_counts(state, shots, seed=7)`** — a dict `{index: count}` over `shots`
seeded measurements. Build one `random.Random(seed)` and reuse it.

**`collapse(state, outcome)`** — the post-measurement state: every amplitude
zero except `outcome`, which keeps its phase and gets modulus 1. An outcome with
probability zero cannot occur: raise `ValueError`.

```text
collapse([1, 1j], 1)    ->  [0j, 1j]
```

**`bloch_angles(state)`** — `(theta, phi)` in radians for a **one-qubit** state,
with `phi` reported in `[0, 2*pi)`. When the state is |0> or |1> the azimuth is
undefined; report `0.0`. Anything other than two amplitudes is a `ValueError`.

```text
bloch_angles([1, 0])    ->  (0.0, 0.0)
bloch_angles([1, 1])    ->  (pi/2, 0.0)
bloch_angles([1, 1j])   ->  (pi/2, pi/2)
```
''',
                "files": [{"name": "main.py", "content": r'''
import cmath
import math
import random


def normalise(amplitudes):
    """A new list of complex amplitudes with unit L2 norm."""
    # your code here


def probabilities(state):
    """Born-rule probabilities |a_k|**2 after normalising."""
    # your code here


def measure(state, rng):
    """One basis index sampled with a single rng.random() draw."""
    # your code here


def sample_counts(state, shots, seed=7):
    """{basis index: count} over `shots` seeded measurements."""
    # your code here


def collapse(state, outcome):
    """The post-measurement state for the given outcome."""
    # your code here


def bloch_angles(state):
    """(theta, phi) on the Bloch sphere for a single-qubit state."""
    # your code here


plus = normalise([1, 1])
print("|+> probabilities:", probabilities(plus))
print("20000 shots:", sample_counts(plus, 20000))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import cmath
import math
import random


def normalise(amplitudes):
    """A new list of complex amplitudes with unit L2 norm."""
    vec = [complex(a) for a in amplitudes]
    norm = math.sqrt(sum(abs(a) ** 2 for a in vec))
    if norm == 0:
        raise ValueError("the zero vector cannot be normalised")
    return [a / norm for a in vec]


def probabilities(state):
    """Born-rule probabilities |a_k|**2 after normalising."""
    return [abs(a) ** 2 for a in normalise(state)]


def measure(state, rng):
    """One basis index sampled with a single rng.random() draw."""
    probs = probabilities(state)
    u = rng.random()
    acc = 0.0
    for k, p in enumerate(probs):
        acc += p
        if u < acc:
            return k
    # Only reachable through floating-point round-off at u very close to 1.
    return len(probs) - 1


def sample_counts(state, shots, seed=7):
    """{basis index: count} over `shots` seeded measurements."""
    rng = random.Random(seed)
    counts = {}
    for _ in range(shots):
        k = measure(state, rng)
        counts[k] = counts.get(k, 0) + 1
    return counts


def collapse(state, outcome):
    """The post-measurement state for the given outcome."""
    vec = normalise(state)
    if not 0 <= outcome < len(vec):
        raise ValueError(f"outcome {outcome} out of range")
    amp = vec[outcome]
    if abs(amp) ** 2 <= 1e-15:
        raise ValueError(f"outcome {outcome} has probability zero")
    out = [0j] * len(vec)
    # Keep the phase, discard the modulus: the collapsed state is a unit vector.
    out[outcome] = amp / abs(amp)
    return out


def bloch_angles(state):
    """(theta, phi) on the Bloch sphere for a single-qubit state."""
    if len(state) != 2:
        raise ValueError("the Bloch sphere describes exactly one qubit")
    a0, a1 = normalise(state)
    r0 = abs(a0)
    theta = 2 * math.acos(min(1.0, max(0.0, r0)))
    if r0 < 1e-12 or abs(a1) < 1e-12:
        return (theta, 0.0)
    phi = cmath.phase(a1) - cmath.phase(a0)
    phi = phi % (2 * math.pi)
    return (theta, phi)


plus = normalise([1, 1])
print("|+> probabilities:", probabilities(plus))
print("20000 shots:", sample_counts(plus, 20000))
'''}],
                "hints": [
                    "The L2 norm is `math.sqrt(sum(abs(a) ** 2 for a in vec))`; guard it against zero before dividing.",
                    "`measure` must draw exactly one random number: accumulate probabilities and return the first index whose running total exceeds it.",
                    "A collapsed amplitude keeps its direction in the complex plane: `amp / abs(amp)` has modulus 1 and the same phase.",
                    "`cmath.phase` gives the argument of a complex number; `phi % (2 * math.pi)` folds a negative difference into range.",
                ],
                "tests": [
                    {"name": "normalise scales to unit norm", "code": r'''
_v = normalise([3, 4])
_n = sum(abs(a) ** 2 for a in _v)
assert abs(_n - 1.0) < 1e-12, f"norm squared is {_n!r}, expected 1.0"
assert abs(_v[0] - 0.6) < 1e-12 and abs(_v[1] - 0.8) < 1e-12, f"normalise([3,4]) gave {_v!r}"
_already = normalise([1, 0])
assert abs(_already[0] - 1) < 1e-12 and abs(_already[1]) < 1e-12, f"Got {_already!r}"
_c = normalise([1, 1j])
assert abs(abs(_c[1]) - 0.7071067811865476) < 1e-9, "Complex amplitudes normalise the same way"
'''},
                    {"name": "normalise refuses the zero vector", "code": r'''
for _bad in ([0, 0], [0j, 0j, 0j, 0j], [0]):
    try:
        normalise(_bad)
        assert False, f"normalise({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "probabilities obey the Born rule", "code": r'''
_p = probabilities([1, 1])
assert abs(_p[0] - 0.5) < 1e-12 and abs(_p[1] - 0.5) < 1e-12, f"Got {_p!r}, expected [0.5, 0.5]"
_p = probabilities([1, 1j])
assert abs(_p[0] - 0.5) < 1e-12 and abs(_p[1] - 0.5) < 1e-12, \
    f"Relative phase must not change probabilities; got {_p!r}"
_p = probabilities([0, 0, 1, 0])
assert abs(sum(_p) - 1.0) < 1e-12 and abs(_p[2] - 1.0) < 1e-12, f"Got {_p!r}"
_p = probabilities([2, 0])
assert abs(_p[0] - 1.0) < 1e-12, "An unnormalised input should be normalised first"
'''},
                    {"name": "measure is deterministic on basis states", "code": r'''
import random as _random
_rng = _random.Random(1)
for _ in range(50):
    assert measure([1, 0], _rng) == 0, "|0> can only ever measure as 0"
    assert measure([0, 0, 1, 0], _rng) == 2, "|2> can only ever measure as 2"
assert measure([1], _random.Random(3)) == 0, "A one-dimensional state has one outcome"
'''},
                    {"name": "sample_counts converges on the amplitudes", "code": r'''
_c = sample_counts(normalise([1, 1]), 20000, seed=7)
assert sum(_c.values()) == 20000, f"Counts total {sum(_c.values())}, expected 20000"
assert abs(_c.get(0, 0) / 20000 - 0.5) < 0.02, f"|+> gave {_c!r}; each outcome should sit near 50%"
_c2 = sample_counts(normalise([1, 1]), 20000, seed=7)
assert _c == _c2, "The same seed must give the same counts"
_c3 = sample_counts(normalise([math.sqrt(3), 1]), 20000, seed=11)
assert abs(_c3.get(0, 0) / 20000 - 0.75) < 0.02, \
    f"amplitudes (sqrt3, 1)/2 give p0 = 0.75; got {_c3.get(0, 0) / 20000!r}"
assert sample_counts([1, 0], 5) == {0: 5}, "A basis state always yields the same index"
'''},
                    {"name": "collapse projects and keeps phase", "code": r'''
_c = collapse([1, 1j], 1)
assert abs(_c[0]) < 1e-12, f"Unmeasured amplitudes go to zero; got {_c!r}"
assert abs(_c[1] - 1j) < 1e-12, f"collapse([1, 1j], 1) gave {_c!r}, expected [0j, 1j]"
_c = collapse([1, 1, 1, 1], 2)
assert abs(sum(abs(a) ** 2 for a in _c) - 1.0) < 1e-12, "The collapsed state is still a unit vector"
try:
    collapse([1, 0], 1)
    assert False, "Collapsing onto a zero-probability outcome should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "bloch_angles places the state on the sphere", "code": r'''
for _st, _want in [([1, 0], (0.0, 0.0)),
                   ([0, 1], (math.pi, 0.0)),
                   ([1, 1], (math.pi / 2, 0.0)),
                   ([1, 1j], (math.pi / 2, math.pi / 2)),
                   ([1, -1], (math.pi / 2, math.pi))]:
    _t, _f = bloch_angles(_st)
    assert abs(_t - _want[0]) < 1e-9 and abs(_f - _want[1]) < 1e-9, \
        f"bloch_angles({_st!r}) gave {(_t, _f)!r}, expected {_want!r}"
try:
    bloch_angles([1, 0, 0, 0])
    assert False, "bloch_angles on more than one qubit should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Gates and circuits",
            "summary": "Unitary matrices, the tensor index trick, and a circuit runner.",
            "concepts": [
                "A gate is a unitary matrix: U*U^dagger = I, so norms and hence probabilities survive",
                "The Pauli group X, Y, Z, and the phase family S = T^2, Z = S^2",
                "H maps the Z eigenbasis to the X eigenbasis; H^2 = I, H Z H = X",
                "Applying a 1-qubit gate to an n-qubit state never builds the 2^n x 2^n matrix: it pairs indices differing in one bit",
                "CNOT is a permutation of basis states; combined with single-qubit rotations it is universal",
                "Circuit depth versus gate count, and why the simulator's cost is 2^n regardless",
            ],
            "read": [
                {
                    "title": "Eight amplitudes, three bits, and the pairs a gate touches",
                    "minutes": 14,
                    "body": r'''
A three-qubit register is a list of eight complex numbers. Write the eight indices in
binary and lay the list out:

```text
index   000  001  010  011  100  101  110  111
amp      a0   a1   a2   a3   a4   a5   a6   a7
```

Now apply an X gate, a bit flip, to qubit 1, the middle bit. Nothing about the physics
is in doubt: whatever amplitude was on $|0\mathbf{0}0\rangle$ is now on
$|0\mathbf{1}0\rangle$, and so on for every index. Trace it. $a_0$ moves to index 2,
$a_2$ to index 0, $a_1$ to 3, $a_3$ to 1, $a_4$ to 6, $a_6$ to 4, $a_5$ to 7, $a_7$ to 5.
Four swaps, and every swap is between two indices that differ in exactly the middle bit
and agree on the other two. The gate on one qubit never looked at the other qubits; it
paired up the amplitudes that differ only in *its* bit and acted inside each pair. That
observation is the whole of the simulator you are about to build.

## Why the pairs, from the tensor product

The reason it works is the structure of the state, not a coincidence of X. A three-qubit
basis state is a product $|q_0\rangle|q_1\rangle|q_2\rangle$, and a gate $U$ on qubit 1
acts as $I \otimes U \otimes I$: it does nothing to $q_0$ and $q_2$, and applies the
$2 \times 2$ matrix $U$ to $q_1$. Fix $q_0$ and $q_2$ at any values; the two basis states
$|q_0\,0\,q_2\rangle$ and $|q_0\,1\,q_2\rangle$ span a copy of one qubit, and inside it
$U$ is the ordinary $2\times 2$ multiplication:

$$\begin{pmatrix} a'_{q_0 0 q_2} \\ a'_{q_0 1 q_2} \end{pmatrix}
= \begin{pmatrix} u_{00} & u_{01} \\ u_{10} & u_{11} \end{pmatrix}
\begin{pmatrix} a_{q_0 0 q_2} \\ a_{q_0 1 q_2} \end{pmatrix}.$$

There are four choices of $(q_0, q_2)$, hence four pairs, and $U$ is applied to each
independently. For X the matrix is $\begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}$ and the
multiplication is the swap you traced by hand. For H it is a mix of the two members. For
a general $n$-qubit register the gate on one qubit is $2^{n-1}$ independent
$2 \times 2$ multiplications, each touching a pair of indices that differ in one bit.

The bit that identifies the pair depends on which qubit you mean, and this course fixes
the convention once: **qubit 0 is the most significant bit**. On $n$ qubits, qubit $q$
lives at bit position $n - 1 - q$, so on three qubits qubit 0 is bit 2 (weight 4), qubit
1 is bit 1 (weight 2), and qubit 2 is bit 0 (weight 1). Enumerate the pairs by walking
every index whose target bit is 0 and adding the bit to find its partner:

```python
n = 3
for target in range(n):
    shift = n - 1 - target
    pairs = [(k, k | (1 << shift)) for k in range(2 ** n) if not (k >> shift) & 1]
    print(f"qubit {target} (bit position {shift}):", pairs)
```

Qubit 1 gives $(0,2), (1,3), (4,6), (5,7)$, which are the four swaps from the trace.
Qubit 0 gives $(0,4), (1,5), (2,6), (3,7)$, partners four apart; qubit 2 gives
neighbours. Skipping the indices whose target bit is set is what makes each pair appear
once: $(0, 2)$ is visited from 0, and index 2 is skipped rather than producing a second
pair $(2, 0)$ that would apply the gate twice.

## The mistake: the wrong end of the register

The lab's test that fails most often reads "X on qubit 0 of $|000\rangle$ should give
index 4". People write `shift = target` because that is how bit $q$ of an integer is
normally addressed, and X on qubit 0 lands on index 1 instead of index 4. It is tempting
because both conventions are self-consistent and the textbooks are split; Nielsen and
Chuang write the register with qubit 0 on the left, which makes it the high bit, and
Qiskit puts qubit 0 on the right, which makes it the low bit. Neither is wrong. Mixing
them inside one program is, and the symptom is a CNOT that flips the wrong qubit and a
Bell state that comes out as $(|00\rangle + |01\rangle)/\sqrt{2}$, which is not
entangled at all. Write `shift = n - 1 - target` once, in one helper, and let every gate
go through it.

## The Bell state, with real numbers

Carry a two-qubit circuit through by hand and by code. Start at $|00\rangle$, apply H to
qubit 0, then CNOT with qubit 0 as control and qubit 1 as target. On two qubits, qubit 0
is bit 1, so H on qubit 0 pairs $(0, 2)$ and $(1, 3)$. The first pair holds
$(a_0, a_2) = (1, 0)$ and H sends it to $(1/\sqrt{2}, 1/\sqrt{2})$; the second holds
$(0, 0)$ and stays there. The state after H is $(0.7071, 0, 0.7071, 0)$, which reads as
$(|00\rangle + |10\rangle)/\sqrt{2}$: qubit 0 in superposition, qubit 1 still zero.

CNOT is a permutation of the basis. Where the control bit is 1, flip the target bit;
where it is 0, do nothing. With control at bit 1 and target at bit 0, the indices with
control set are 2 and 3, and they exchange amplitudes. So $(0.7071, 0, 0.7071, 0)$
becomes $(0.7071, 0, 0, 0.7071)$, which is $(|00\rangle + |11\rangle)/\sqrt{2}$.

```python
import math

r = 1 / math.sqrt(2)
H = [[r, r], [r, -r]]


def apply_1q(state, gate, target):
    n = len(state).bit_length() - 1
    shift = n - 1 - target
    out = list(state)
    for k in range(len(state)):
        if (k >> shift) & 1:
            continue
        k1 = k | (1 << shift)
        a, b = state[k], state[k1]
        out[k] = gate[0][0] * a + gate[0][1] * b
        out[k1] = gate[1][0] * a + gate[1][1] * b
    return out


def apply_cnot(state, control, target):
    n = len(state).bit_length() - 1
    cs, ts = n - 1 - control, n - 1 - target
    out = list(state)
    for k in range(len(state)):
        if ((k >> cs) & 1) and not ((k >> ts) & 1):
            k1 = k | (1 << ts)
            out[k], out[k1] = state[k1], state[k]
    return out


def show(label, state):
    print(f"{label:<14}", [round(a, 4) for a in state])


state = [1.0, 0.0, 0.0, 0.0]          # |00>
show("start", state)
state = apply_1q(state, H, 0)
show("after H on 0", state)
state = apply_cnot(state, 0, 1)
show("after CNOT", state)
print("norm squared:", round(sum(a * a for a in state), 12))
```

The two printed states are the two computed by hand, and the norm is still $1$. Notice
what `apply_cnot` does not do: it does not touch the indices where the control is 0, and
it does not build anything of size $4 \times 4$. The condition `control set and target
clear` picks out one member of each swapped pair, exactly as the `if (k >> shift) & 1:
continue` in `apply_1q` picks out one member of each mixed pair. Both functions copy the
input first and overwrite only what changes, so the amplitudes they do not touch carry
over and the caller's list is never mutated, which is what the lab's mutation test looks
for.

## Why every gate is unitary

The norm came out as $1$, and that was not luck. Probabilities have to sum to one after
the gate as well as before, for every input state, so a gate has to preserve the length
of every vector. Write the gate as a matrix $U$ and the requirement as
$\|U\psi\|^2 = \|\psi\|^2$; expanding, $\psi^\dagger U^\dagger U \psi = \psi^\dagger\psi$
for all $\psi$, which holds only when $U^\dagger U = I$. That equation is the definition
of unitary, and it is not an extra axiom: it is what "the probabilities still add to one"
says in matrix language. It also makes every gate reversible, since $U^{-1} = U^\dagger$
exists and is another gate.

```python
import math

r = 1 / math.sqrt(2)
H = [[r, r], [r, -r]]
G = [[1, 1], [0, 1]]                  # not unitary: its columns are not orthonormal


def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def apply(gate, state):
    a, b = state
    return [gate[0][0] * a + gate[0][1] * b, gate[1][0] * a + gate[1][1] * b]


def norm2(state):
    return round(sum(abs(a) ** 2 for a in state), 6)


print("H times H:", [[round(x, 6) for x in row] for row in matmul(H, H)])
plus = [r, r]
print("norm^2 of H|+>:", norm2(apply(H, plus)), "   norm^2 of G|+>:", norm2(apply(G, plus)))
```

H is real and symmetric, so $H^\dagger = H$, and $H H = I$ is the unitarity condition
and the statement that H is its own inverse at once; the printed product is the identity.
The matrix $G$ is a perfectly good linear map and it sends $|+\rangle$ to a vector of
squared norm $2.5$. There is no experiment with probabilities summing to $2.5$, so $G$ is
not a gate, and a simulator that accepted it would report nonsense with a straight face.
The lab's norm test runs twenty random circuits from X, Y, Z, H, S, T and CNOT for
exactly this reason: every one of those is unitary, so any drift from $1$ is a bug in
the index arithmetic rather than in the physics.

The phase gates are worth one remark. $S = \mathrm{diag}(1, i)$ and
$T = \mathrm{diag}(1, e^{i\pi/4})$ leave the moduli alone and rotate the phase of the
$|1\rangle$ component, so on their own they change no probability at all; the lab's
`probabilities` would not notice them. They matter because a later H turns the phase
into a modulus, which is the interference of module 1. $T^2 = S$ and $S^2 = Z$, since
$(e^{i\pi/4})^2 = i$ and $i^2 = -1$; the test that applies T twice and compares with S is
checking that you built T from `cmath.exp(1j * math.pi / 4)` rather than from a rounded
decimal.

## Where the trick stops paying

The pair trick costs $2^n$ operations per gate, because it visits every amplitude once.
Building the gate as a dense $2^n \times 2^n$ matrix and multiplying would cost $4^n$
and, before that, would need $4^n$ complex numbers of memory:

```python
def human(nbytes):
    for unit in ("bytes", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB"):
        if nbytes < 1024:
            return f"{nbytes:.0f} {unit}"
        nbytes /= 1024
    return f"{nbytes:.0f} ZiB"


for n in (10, 20, 30):
    print(f"{n} qubits: state {human(2 ** n * 16):>8}   dense gate {human(4 ** n * 16):>8}")
```

Ten qubits is a 16 KiB state and a 16 MiB matrix, which is fine. Twenty is a 16 MiB
state and a 16 TiB matrix, which is not. Thirty is a 16 GiB state, which a workstation
can hold, and a matrix of 16 EiB, which nothing can. The pair trick is what makes twenty
and thirty qubits reachable at all, and it is why the capstone rubric refuses dense
operator matrices outright.

But the state itself still doubles with every qubit, and that is the wall the trick does
not move. Every gate touches every amplitude, so a circuit of $d$ gates on $n$ qubits
costs $d \cdot 2^n$ regardless of how shallow or sparse it is; a depth-one circuit of
fifty X gates is no cheaper per gate than a deep one. Around forty-five to fifty qubits
the state no longer fits in any machine, and that is where a classical simulator stops
and a quantum computer would begin. Circuit depth, which is the number of layers that
can run in parallel, matters to hardware because it sets the running time and the
exposure to noise; it does not matter to this simulator, which runs the gates one after
another whatever the layer structure.

Two further boundaries. CNOT together with arbitrary single-qubit rotations is
universal, meaning any unitary on $n$ qubits can be built from them, but "can be built"
says nothing about how many gates it takes, and a generic $n$-qubit unitary needs
exponentially many. And the register in this module is closed: no measurement in the
middle, no noise, no reset. The lab's `run_circuit` is a pure function from an op list
to a state vector, and it is the engine the next three modules and the capstone's
`Circuit` builder are written on. Build the index helper first, make `apply_1q` and
`apply_cnot` go through it, and the Bell and GHZ tests follow from the arithmetic above.
''',
                },
            ],
            "quiz": {
                "title": "Which amplitudes a gate touches",
                "minutes": 8,
                "questions": [
                    {
                        "q": "On a four-qubit register (qubit 0 most significant), which index pairs does a gate on qubit 1 mix?",
                        "opts": [
                            "Indices that differ by 2, since qubit 1 is the second bit from the low end",
                            "Indices that differ by 4, since qubit 1 sits at bit position $4 - 1 - 1 = 2$",
                            "Indices that differ by 1, since a single-qubit gate always pairs adjacent neighbours",
                            "Indices that differ by 8, since qubit 1 is the second most significant bit",
                        ],
                        "a": 1,
                        "whys": [
                            r"A difference of 2 is bit position 1, which on four qubits is qubit 2, not qubit 1. The convention counts from the top: qubit $q$ lives at bit $n - 1 - q$, so qubit 1 is bit 2 and the partners are 4 apart.",
                            r"Bit position $n - 1 - q = 2$, weight $2^2 = 4$: the pairs are $(0,4), (1,5), (2,6), \dots$",
                            r"Neighbouring indices differ in bit 0, which is the least significant qubit, qubit 3 here. A gate on any other qubit mixes indices further apart, by the weight of its bit.",
                            r"A difference of 8 is bit 3, the most significant, which is qubit 0. Qubit 1 is one position below that, at bit 2, so its partners are 4 apart, not 8.",
                        ],
                        "why": r"""
With qubit 0 as the most significant bit, qubit $q$ of an $n$-qubit register lives at
bit position $n - 1 - q$. For $n = 4$ and $q = 1$ that is bit 2, weight 4, so a gate on
qubit 1 mixes $(k, k + 4)$ for every $k$ whose bit 2 is clear. The other spacings
belong to other qubits: 8 to qubit 0, 2 to qubit 2, 1 to qubit 3. Mixing the two
conventions up is the most common failing test in the lab, which is why the helper
computes the shift once.
""",
                    },
                    {
                        "q": "`apply_1q` loops over every index $k$ but skips those whose target bit is set. What goes wrong if the skip is removed?",
                        "opts": [
                            "Nothing, because a second visit to a pair recomputes the same two outputs from the input list, which is untouched",
                            "Each upper index is visited with itself as its partner, and that write overwrites the correct amplitude",
                            "The loop starts reading from `out` instead of `state`, so later pairs see partly updated values",
                            "Half the pairs are never reached, because an index and its partner are now both passed over",
                        ],
                        "a": 1,
                        "whys": [
                            r"That would be true if the upper visit found the same pair, but it does not: for an index whose target bit is already set, `k | (1 << shift)` is the index itself, so the second visit pairs the upper amplitude with itself rather than with its lower partner.",
                            r"When the target bit is set, `k1 = k | (1 << shift)` equals `k`, so `a` and `b` are the same amplitude and `out[k]` is overwritten with $(u_{10} + u_{11})\,a_k$; for H that is zero.",
                            r"The function reads from `state` and writes to `out` throughout, so there is no partial-update problem whatever the loop does. The bug is in which indices are visited and what partner they are given, not in aliasing.",
                            r"Removing the skip makes the loop reach *more* indices, not fewer; every $k$ is now processed. The problem is a spurious extra visit, not a missing one.",
                        ],
                        "why": r"""
Without the skip, an index $k_1$ whose target bit is set is visited too, and for it
`k | (1 << shift)` is $k_1$ itself, so `a` and `b` are both $a_{k_1}$ and the code
writes $(u_{10} + u_{11})\,a_{k_1}$ over the correct value the lower visit had placed
there. For H that factor is $1/\sqrt{2} - 1/\sqrt{2} = 0$, so `H` on $|1\rangle$ comes
out as $(0.7071, 0)$ instead of $(0.7071, -0.7071)$. The skip makes each pair appear
once, from its lower member, which is what the tensor product picture says should
happen.
""",
                    },
                    {
                        "q": "Why must every gate be a unitary matrix, in terms of what the simulator measures?",
                        "opts": [
                            "Unitarity keeps the matrix entries between $-1$ and $1$, so no amplitude can overflow",
                            "Unitarity preserves the norm of every state, so the probabilities keep summing to one",
                            "Unitarity guarantees the matrix is real, so the simulator never needs complex numbers",
                            "Unitarity makes the gate diagonal in some basis, which is what lets it be applied sparsely",
                        ],
                        "a": 1,
                        "whys": [
                            r"Entries of a unitary do sit within the unit disc, but that is a consequence, not the point, and a matrix with small entries can still shrink or stretch a vector. The condition that matters is on the whole map: $\|U\psi\| = \|\psi\|$ for every $\psi$.",
                            r"$U^\dagger U = I$ is precisely the statement that $\|U\psi\|^2 = \|\psi\|^2$ for all $\psi$, so the Born probabilities still add to one after the gate.",
                            r"Y, S and T are unitary and complex. Unitarity says nothing about being real; it says the columns are orthonormal in the complex inner product.",
                            r"Every unitary is diagonalisable, but so are many non-unitary matrices, and sparseness of application comes from the tensor product structure, not from diagonalisability. The pair trick works for any $2\times 2$ matrix, unitary or not.",
                        ],
                        "why": r"""
After a gate the state must still be a state: the Born probabilities $|a_k|^2$ must
sum to one for every possible input. That is $\|U\psi\| = \|\psi\|$ for all $\psi$,
which expands to $U^\dagger U = I$. The reading's non-unitary $G$ sends $|+\rangle$ to a
vector of squared norm $2.5$, which no experiment can produce. Unitarity also gives
reversibility for free, since $U^{-1} = U^\dagger$ is itself a gate.
""",
                    },
                    {
                        "q": "Applying S to a qubit in the state $(1, 1)/\\sqrt{2}$ leaves its measurement probabilities at 50/50. What is the gate for, then?",
                        "opts": [
                            "It is a no-op on superpositions and acts only on the two basis states $|0\\rangle$ and $|1\\rangle$",
                            "It changes the relative phase, which a later Hadamard converts into a change of probabilities",
                            "It swaps the two amplitudes' moduli, which a symmetric state cannot show",
                            "It changes the global phase, which is unobservable but needed to keep the matrix unitary",
                        ],
                        "a": 1,
                        "whys": [
                            r"S acts on every state, including this one: it turns $(1, 1)/\sqrt{2}$ into $(1, i)/\sqrt{2}$, a different point on the Bloch sphere. On the basis states it does even less visibly, multiplying $|1\rangle$ by a global phase.",
                            r"$(1, 1)/\sqrt{2}$ becomes $(1, i)/\sqrt{2}$; measured directly both are 50/50, but H sends the first to $|0\rangle$ and leaves the second at 50/50.",
                            r"S is diagonal, so it never moves amplitude between components; each modulus stays where it was. What it changes is the phase of the $|1\rangle$ component.",
                            r"The phase S applies is on one component only, so it is relative, not global. A global phase would indeed be unobservable, but this one is detected by any measurement after a Hadamard.",
                        ],
                        "why": r"""
$S = \mathrm{diag}(1, i)$ multiplies the $|1\rangle$ amplitude by $i$ and leaves the
moduli untouched, so a direct measurement cannot see it. The phase it introduces is
between the two components, and a Hadamard afterwards turns that relative phase into
a difference in moduli: $H$ takes $(1, 1)/\sqrt{2}$ to $(1, 0)$ but $(1, i)/\sqrt{2}$
to a 50/50 state. Phase gates are the half of the gate set that interference runs
on; without them there is nothing for the Hadamards to interfere.
""",
                    },
                    {
                        "q": "A circuit on 30 qubits has depth 1 and consists of thirty X gates, one per qubit. Roughly what does the sparse simulator pay to run it?",
                        "opts": [
                            "About $2^{30}$ operations in total, since a depth-one layer is applied as a single pass",
                            "About $30 \\times 2^{30}$ operations, since each gate visits every one of the $2^{30}$ amplitudes",
                            "About $30 \\times 2$ operations, since each X is a $2\\times 2$ matrix on one qubit",
                            "About $30 \\times 4^{30}$ operations, since each gate is a dense $2^{30} \\times 2^{30}$ matrix multiply",
                        ],
                        "a": 1,
                        "whys": [
                            r"The simulator has no notion of a layer; it applies the gates one after another, and each pass over the state costs $2^{30}$. Depth is what hardware cares about, not what this engine pays.",
                            r"Each gate touches all $2^n$ amplitudes once, and there are thirty gates.",
                            r"The $2\times 2$ matrix is applied to $2^{29}$ independent pairs, not to one. A single-qubit gate is cheap to describe and expensive to apply, because it acts on every amplitude in the register.",
                            r"$4^{30}$ is the dense-matrix cost that the pair trick exists to avoid. The sparse simulator never builds the $2^{30}\times 2^{30}$ matrix; it does $2^{30}$ work per gate, not $4^{30}$.",
                        ],
                        "why": r"""
The pair trick reduces a gate from $4^n$ to $2^n$ operations, and it cannot go lower,
because every amplitude belongs to some pair. Thirty gates on a $2^{30}$-amplitude
state cost $30 \times 2^{30}$, about thirty billion pair updates, whatever the depth of
the circuit. Depth matters to hardware, where a layer runs in parallel and sets the
exposure to noise; it does not matter to a state-vector simulator, which is why the
reading says the simulator's cost is $2^n$ regardless.
""",
                    },
                ],
            },
            "lab": {
                "title": "A tensor-structured circuit simulator",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
Build the engine the rest of the course runs on. **Index convention: qubit 0 is
the most significant bit.** On 3 qubits, basis index 3 is `|011>`, and the bit of
qubit `q` lives at position `n - 1 - q`.

**Gate constants** — define `I`, `X`, `Y`, `Z`, `H`, `S`, `T` as 2x2 lists of
lists of complex numbers, and `phase(angle)` returning `diag(1, exp(i*angle))`.

**`n_qubits(state)`** — the qubit count, or `ValueError` if the length is not a
power of two greater than 1.

**`zero_state(n)`** — the register `|00...0>`. `ValueError` for `n < 1`.

**`apply_1q(state, gate, target)`** — a **new** state with `gate` applied to
`target`. Do not build a 2^n x 2^n matrix. Walk every index `k` whose target bit
is 0, pair it with `k1 = k | (1 << shift)`, and mix that pair through the gate:

```text
out[k]  = g00*state[k] + g01*state[k1]
out[k1] = g10*state[k] + g11*state[k1]
```

**`apply_cnot(state, control, target)`** — swap the amplitude pairs where the
control bit is 1. `ValueError` when the two indices coincide or fall out of range.

**`run_circuit(n, ops)`** — start from `zero_state(n)` and apply an op list.
An op is `("h", 0)`, `("x", 1)`, `("phase", 2, angle)` or `("cnot", 0, 1)`.
Gate names are the lowercase constants above. An unknown name is a `ValueError`.

```text
run_circuit(2, [("h", 0), ("cnot", 0, 1)])  ->  (|00> + |11>) / sqrt(2)
```
''',
                "files": [{"name": "main.py", "content": r'''
import cmath
import math

SQRT2 = math.sqrt(2)

# 1. The gate constants. Each is a 2x2 list of lists of complex numbers.
I = None
X = None
Y = None
Z = None
H = None
S = None
T = None


def phase(angle):
    """The diagonal gate diag(1, exp(i*angle))."""
    # your code here


def n_qubits(state):
    """Qubit count for a state vector; ValueError if the length is not 2**n."""
    # your code here


def zero_state(n):
    """The n-qubit register |00...0>."""
    # your code here


def apply_1q(state, gate, target):
    """A new state with the 2x2 gate applied to one qubit."""
    # your code here


def apply_cnot(state, control, target):
    """A new state with target flipped wherever control is 1."""
    # your code here


def run_circuit(n, ops):
    """Run an op list on |0...0> and return the final state."""
    # your code here


bell = run_circuit(2, [("h", 0), ("cnot", 0, 1)])
print("Bell amplitudes:", [round(a.real, 4) + round(a.imag, 4) * 1j for a in bell])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import cmath
import math

SQRT2 = math.sqrt(2)

I = [[1 + 0j, 0j], [0j, 1 + 0j]]
X = [[0j, 1 + 0j], [1 + 0j, 0j]]
Y = [[0j, -1j], [1j, 0j]]
Z = [[1 + 0j, 0j], [0j, -1 + 0j]]
H = [[1 / SQRT2 + 0j, 1 / SQRT2 + 0j], [1 / SQRT2 + 0j, -1 / SQRT2 + 0j]]
S = [[1 + 0j, 0j], [0j, 1j]]
T = [[1 + 0j, 0j], [0j, cmath.exp(1j * math.pi / 4)]]


def phase(angle):
    """The diagonal gate diag(1, exp(i*angle))."""
    return [[1 + 0j, 0j], [0j, cmath.exp(1j * angle)]]


def n_qubits(state):
    """Qubit count for a state vector; ValueError if the length is not 2**n."""
    size = len(state)
    if size < 2:
        raise ValueError("a register needs at least two amplitudes")
    n = size.bit_length() - 1
    if 2 ** n != size:
        raise ValueError(f"state length {size} is not a power of two")
    return n


def zero_state(n):
    """The n-qubit register |00...0>."""
    if n < 1:
        raise ValueError("need at least one qubit")
    state = [0j] * (2 ** n)
    state[0] = 1 + 0j
    return state


def apply_1q(state, gate, target):
    """A new state with the 2x2 gate applied to one qubit."""
    n = n_qubits(state)
    if not 0 <= target < n:
        raise ValueError(f"target qubit {target} out of range for {n} qubits")
    shift = n - 1 - target       # qubit 0 is the most significant bit
    out = list(state)
    for k in range(len(state)):
        if (k >> shift) & 1:
            continue             # visit each pair once, from its lower member
        k1 = k | (1 << shift)
        a, b = state[k], state[k1]
        out[k] = gate[0][0] * a + gate[0][1] * b
        out[k1] = gate[1][0] * a + gate[1][1] * b
    return out


def apply_cnot(state, control, target):
    """A new state with target flipped wherever control is 1."""
    n = n_qubits(state)
    if control == target:
        raise ValueError("control and target must be different qubits")
    if not (0 <= control < n and 0 <= target < n):
        raise ValueError("qubit index out of range")
    cs = n - 1 - control
    ts = n - 1 - target
    out = list(state)
    for k in range(len(state)):
        # Touch each swapped pair once: control set, target clear.
        if ((k >> cs) & 1) and not ((k >> ts) & 1):
            k1 = k | (1 << ts)
            out[k], out[k1] = state[k1], state[k]
    return out


ONE_QUBIT_GATES = {"i": I, "x": X, "y": Y, "z": Z, "h": H, "s": S, "t": T}


def run_circuit(n, ops):
    """Run an op list on |0...0> and return the final state."""
    state = zero_state(n)
    for op in ops:
        name = op[0]
        if name in ONE_QUBIT_GATES:
            state = apply_1q(state, ONE_QUBIT_GATES[name], op[1])
        elif name == "phase":
            state = apply_1q(state, phase(op[2]), op[1])
        elif name == "cnot":
            state = apply_cnot(state, op[1], op[2])
        else:
            raise ValueError(f"unknown gate {name!r}")
    return state


bell = run_circuit(2, [("h", 0), ("cnot", 0, 1)])
print("Bell amplitudes:", [round(a.real, 4) + round(a.imag, 4) * 1j for a in bell])
'''}],
                "hints": [
                    "Write the bit position once: `shift = n - 1 - target`, then the target bit of index k is `(k >> shift) & 1`.",
                    "Start `out = list(state)` and overwrite only the entries you touch — the untouched amplitudes carry over unchanged.",
                    "CNOT is a permutation: for each k with control set and target clear, exchange `state[k]` and `state[k | (1 << ts)]`.",
                    "Keep a dict from gate name to matrix so `run_circuit` stays a short dispatch rather than a chain of elifs.",
                ],
                "tests": [
                    {"name": "Gate constants are the textbook matrices", "code": r'''
assert abs(X[0][1] - 1) < 1e-12 and abs(X[0][0]) < 1e-12, f"X is {X!r}"
assert abs(Y[0][1] + 1j) < 1e-12 and abs(Y[1][0] - 1j) < 1e-12, f"Y is {Y!r}"
assert abs(Z[1][1] + 1) < 1e-12, f"Z is {Z!r}"
assert abs(H[0][0] - 0.7071067811865476) < 1e-9 and abs(H[1][1] + 0.7071067811865476) < 1e-9, f"H is {H!r}"
assert abs(S[1][1] - 1j) < 1e-12, f"S is {S!r}"
assert abs(T[1][1] - cmath.exp(1j * math.pi / 4)) < 1e-12, f"T is {T!r}"
assert abs(phase(math.pi)[1][1] + 1) < 1e-12, "phase(pi) is Z"
'''},
                    {"name": "n_qubits and zero_state", "code": r'''
assert n_qubits([1, 0]) == 1 and n_qubits([0] * 8) == 3, "Length 8 is three qubits"
for _bad in ([1, 0, 0], [1], []):
    try:
        n_qubits(_bad)
        assert False, f"n_qubits({_bad!r}) should raise ValueError"
    except ValueError:
        pass
_z = zero_state(3)
assert len(_z) == 8 and _z[0] == 1 and all(a == 0 for a in _z[1:]), f"zero_state(3) gave {_z!r}"
try:
    zero_state(0)
    assert False, "zero_state(0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "apply_1q on a single qubit", "code": r'''
_p = apply_1q(zero_state(1), H, 0)
assert abs(_p[0] - 0.7071067811865476) < 1e-9 and abs(_p[1] - 0.7071067811865476) < 1e-9, \
    f"H|0> gave {_p!r}, expected both amplitudes 1/sqrt(2)"
_back = apply_1q(_p, H, 0)
assert abs(_back[0] - 1) < 1e-9 and abs(_back[1]) < 1e-9, f"H twice should be the identity; got {_back!r}"
_t2 = apply_1q(apply_1q([0j, 1 + 0j], T, 0), T, 0)
_s1 = apply_1q([0j, 1 + 0j], S, 0)
assert abs(_t2[1] - _s1[1]) < 1e-12, f"T applied twice must equal S; got {_t2!r} vs {_s1!r}"
_orig = zero_state(1)
apply_1q(_orig, X, 0)
assert _orig[0] == 1, "apply_1q must return a new list, not mutate its argument"
'''},
                    {"name": "apply_1q addresses the right qubit", "code": r'''
_s = apply_1q(zero_state(3), X, 1)
assert abs(_s[2] - 1) < 1e-12 and abs(_s[0]) < 1e-12, \
    f"X on qubit 1 of |000> should give |010> = index 2; got {_s!r}"
_s = apply_1q(zero_state(3), X, 0)
assert abs(_s[4] - 1) < 1e-12, "Qubit 0 is the most significant bit, so X gives index 4"
_s = apply_1q(zero_state(3), X, 2)
assert abs(_s[1] - 1) < 1e-12, "Qubit 2 is the least significant bit, so X gives index 1"
try:
    apply_1q(zero_state(2), X, 2)
    assert False, "A target beyond the register should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "CNOT permutes the basis correctly", "code": r'''
def _basis(n, k):
    _v = [0j] * (2 ** n)
    _v[k] = 1 + 0j
    return _v
for _k, _want in [(0, 0), (1, 1), (2, 3), (3, 2)]:
    _got = apply_cnot(_basis(2, _k), 0, 1)
    assert abs(_got[_want] - 1) < 1e-12, \
        f"CNOT(0->1) on |{_k:02b}> should give |{_want:02b}>; got {_got!r}"
for _k, _want in [(0, 0), (1, 3), (2, 2), (3, 1)]:
    _got = apply_cnot(_basis(2, _k), 1, 0)
    assert abs(_got[_want] - 1) < 1e-12, \
        f"CNOT(1->0) on |{_k:02b}> should give |{_want:02b}>; got {_got!r}"
for _bad in [(0, 0), (0, 5), (-1, 1)]:
    try:
        apply_cnot(zero_state(2), *_bad)
        assert False, f"apply_cnot(..., {_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "run_circuit builds Bell and GHZ states", "code": r'''
_b = run_circuit(2, [("h", 0), ("cnot", 0, 1)])
_r = 0.7071067811865476
assert abs(_b[0] - _r) < 1e-9 and abs(_b[3] - _r) < 1e-9, f"Bell state amplitudes are {_b!r}"
assert abs(_b[1]) < 1e-12 and abs(_b[2]) < 1e-12, "|01> and |10> must have zero amplitude"
_g = run_circuit(3, [("h", 0), ("cnot", 0, 1), ("cnot", 1, 2)])
assert abs(_g[0] - _r) < 1e-9 and abs(_g[7] - _r) < 1e-9, f"GHZ amplitudes are {_g!r}"
assert sum(abs(a) ** 2 for a in _g[1:7]) < 1e-18, "Only |000> and |111> survive in GHZ"
assert abs(run_circuit(1, [])[0] - 1) < 1e-12, "An empty circuit leaves |0>"
try:
    run_circuit(2, [("toffoli", 0, 1)])
    assert False, "An unknown gate name should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Circuits preserve the norm", "code": r'''
import random as _random
_rng = _random.Random(7)
_names = ["x", "y", "z", "h", "s", "t"]
for _trial in range(20):
    _n = _rng.choice([1, 2, 3])
    _ops = []
    for _ in range(12):
        if _n > 1 and _rng.random() < 0.3:
            _c = _rng.randrange(_n)
            _t = (_c + 1 + _rng.randrange(_n - 1)) % _n
            _ops.append(("cnot", _c, _t))
        else:
            _ops.append((_rng.choice(_names), _rng.randrange(_n)))
    _st = run_circuit(_n, _ops)
    _norm = sum(abs(a) ** 2 for a in _st)
    assert abs(_norm - 1.0) < 1e-9, f"Unitary gates keep the norm at 1; got {_norm!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Entanglement and the CHSH bound",
            "summary": "Bell states, marginal randomness, and a correlation no local model can fake.",
            "concepts": [
                "A two-qubit state is entangled when it cannot be written as a tensor product of one-qubit states",
                "The four Bell states form a maximally entangled orthonormal basis of C^4",
                "Each half of a Bell pair is maximally mixed: the marginals carry no information",
                "Measuring along an axis at angle theta means rotating by Ry(-theta) and then measuring in Z",
                "For |Phi+> the correlation is E(a, b) = cos(a - b), independent of the individual angles",
                "CHSH: any local hidden-variable model obeys |S| <= 2, while quantum mechanics reaches 2*sqrt(2)",
            ],
            "read": [
                {
                    "title": "Two dials, two lamps, and a correlation no instruction card can produce",
                    "minutes": 15,
                    "body": r'''
A source in the middle of a room emits pairs of particles, one to the left and one to
the right. On each side stands a box with a dial, which can be set to any angle, and a
lamp that flashes either $+1$ or $-1$ when a particle arrives. Alice runs the left box,
Bob the right, far enough apart that nothing Alice does can reach Bob before his lamp
has flashed. They record thousands of rounds, then compare notebooks.

Alone, each notebook is a fair coin. Whatever angle Alice chose, her column is half
$+1$ and half $-1$ with no pattern, and the same for Bob. Together, the notebooks are
not coins at all. When the two dials were set to the same angle, the lamps agreed on
every single round. When they differed by $45°$, the lamps agreed about $85\%$ of the
time. When they differed by $90°$, agreement dropped to $50\%$, and at $180°$ the lamps
disagreed every round. The correlation depends on the *difference* between the dials
and on nothing else. Every number in this reading is an attempt to reproduce those
notebooks, first with the state from module 2, and then with the most reasonable
classical mechanism anyone can propose, which fails.

## The state that fills the notebooks

The source emits the Bell state $|\Phi^+\rangle = (|00\rangle + |11\rangle)/\sqrt{2}$,
which the lab builds with an H and a CNOT. Alice's dial at angle $a$ means she measures
along the axis $\cos a\, Z + \sin a\, X$ on the Bloch sphere. There is no new
measurement primitive for that: rotate her qubit by $R_y(-a)$, which carries that axis
onto $Z$, then measure in the computational basis as in module 1. The rotation is

$$R_y(\theta) = \begin{pmatrix} \cos\frac{\theta}{2} & -\sin\frac{\theta}{2} \\
\sin\frac{\theta}{2} & \cos\frac{\theta}{2} \end{pmatrix},$$

applied with the `apply_1q` pair trick to qubit 0 for Alice and qubit 1 for Bob. The
correlation $E(a, b)$ is the average of the product of the two lamps: $+1$ when they
agree, $-1$ when they differ, weighted by the Born probabilities of the four outcomes.

Work one setting through. Alice at $a = 0$ does not rotate. Bob at $b = \pi/4$ applies
$R_y(-\pi/4)$ to qubit 1, with $\cos(\pi/8) = 0.9239$ and $\sin(\pi/8) = 0.3827$. On
qubit 1, the pairs are $(0, 1)$ and $(2, 3)$. The first pair holds $(1/\sqrt{2}, 0)$ and
becomes $(0.9239, -0.3827)/\sqrt{2} = (0.6533, -0.2706)$; the second holds
$(0, 1/\sqrt{2})$ and becomes $(0.3827, 0.9239)/\sqrt{2} = (0.2706, 0.6533)$. Squaring
the four amplitudes gives probabilities $0.4268, 0.0732, 0.0732, 0.4268$ for
$|00\rangle, |01\rangle, |10\rangle, |11\rangle$. Agreement is $0.4268 + 0.4268 =
0.8536$ and disagreement $0.1464$, so $E = 0.8536 - 0.1464 = 0.7071$. That is the
$85\%$ agreement at $45°$ from the notebooks, and $0.7071$ is $\cos(\pi/4)$.

```python
import math

r = 1 / math.sqrt(2)


def ry(theta):
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return [[c, -s], [s, c]]


def apply_1q(state, gate, target):
    n = len(state).bit_length() - 1
    shift = n - 1 - target
    out = list(state)
    for k in range(len(state)):
        if (k >> shift) & 1:
            continue
        k1 = k | (1 << shift)
        a, b = state[k], state[k1]
        out[k] = gate[0][0] * a + gate[0][1] * b
        out[k1] = gate[1][0] * a + gate[1][1] * b
    return out


def expectation(state, a, b):
    rotated = apply_1q(apply_1q(state, ry(-a), 0), ry(-b), 1)
    probs = [x * x for x in rotated]
    agree = probs[0] + probs[3]
    return probs, agree - (probs[1] + probs[2])


phi_plus = [r, 0.0, 0.0, r]
probs, e = expectation(phi_plus, 0.0, math.pi / 4)
print("joint probabilities:", [round(p, 4) for p in probs])
print("E(0, pi/4) =", round(e, 4), "  cos(pi/4) =", round(math.cos(math.pi / 4), 4))
for a in (0.0, 1.9):
    probs, _ = expectation(phi_plus, a, 0.0)
    print(f"Alice at {a}: Bob sees p0 = {probs[0] + probs[2]:.4f}, p1 = {probs[1] + probs[3]:.4f}")
```

The general result is $E(a, b) = \cos(a - b)$ for $|\Phi^+\rangle$, and it comes from
the same arithmetic with symbols: after both rotations, the agreeing amplitudes are
$\cos\frac{a}{2}\cos\frac{b}{2} + \sin\frac{a}{2}\sin\frac{b}{2}$ and its twin, each
equal to $\cos\frac{a-b}{2}/\sqrt{2}$, and the disagreeing ones are $\pm\sin\frac{a-b}{2}/\sqrt{2}$.
So agreement is $\cos^2\frac{a-b}{2}$, disagreement is $\sin^2\frac{a-b}{2}$, and the
difference is $\cos(a - b)$ by the double-angle identity. Only the difference survives,
which is what the notebooks showed. For $|\Psi^-\rangle$ the same steps give
$-\cos(a-b)$; the lab's `expectation_ab` test checks both.

The last two printed lines are the other half of the notebooks. Whatever Alice's dial,
Bob's marginal stays at $0.5 / 0.5$. This is the no-signalling fact, and it is why the
correlation cannot be used to send a message: Bob's column alone is a coin regardless of
what Alice did, and he learns nothing until the notebooks are brought together. The
lab's `marginal_probabilities` computes those sums and every Bell state gives
$[0.5, 0.5]$ on both halves.

## The instruction card, and why it cannot reach $2\sqrt{2}$

Here is the obvious classical mechanism. When the pair is created, each particle is
handed a card that says what to flash for every possible dial angle; the two cards are
made together, so they can be as correlated as you like. Alice's lamp is then a function
$A(a, \lambda)$ of her angle and the card $\lambda$, Bob's is $B(b, \lambda)$, and
neither depends on the other's dial. That independence is *locality*, and it is the only
assumption. The lab's `lhv_chsh` is one such card: a random angle $\lambda$, with
$A(\theta) = \mathrm{sign}\cos(\theta - \lambda)$ and $B(\theta) = -A(\theta)$.

Now fix a card and consider two settings each: $a_0, a_1$ for Alice and $b_0, b_1$ for
Bob. The four lamp values are each $\pm 1$. Form the combination

$$s(\lambda) = A_0 B_0 + A_0 B_1 + A_1 B_0 - A_1 B_1 = A_0 (B_0 + B_1) + A_1 (B_0 - B_1).$$

Since $B_0$ and $B_1$ are each $\pm 1$, either they are equal, in which case
$B_0 - B_1 = 0$ and $B_0 + B_1 = \pm 2$, or they differ, in which case $B_0 + B_1 = 0$
and $B_0 - B_1 = \pm 2$. Either way exactly one bracket is zero and the other is
$\pm 2$, so $s(\lambda) = \pm 2$ for every card. Averaging over however the cards are
distributed cannot escape an interval that every term sits in, so

$$S = E(a_0, b_0) + E(a_0, b_1) + E(a_1, b_0) - E(a_1, b_1) \quad\text{satisfies}\quad |S| \le 2.$$

That is the CHSH inequality, and notice what went into it: nothing about quantum
mechanics, nothing about the specific card, only that each lamp is a definite function
of its own dial and the shared card. Any mechanism of that shape obeys the bound.

Now put the quantum correlation in, with the angles $a_0 = 0$, $a_1 = \pi/2$,
$b_0 = \pi/4$, $b_1 = -\pi/4$:

```python
import math

a0, a1, b0, b1 = 0.0, math.pi / 2, math.pi / 4, -math.pi / 4
E = lambda a, b: math.cos(a - b)
terms = [E(a0, b0), E(a0, b1), E(a1, b0), -E(a1, b1)]
print("the four terms:", [round(t, 4) for t in terms])
print("S =", round(sum(terms), 4), "   2*sqrt(2) =", round(2 * math.sqrt(2), 4))
```

Three differences of $\pm\pi/4$ each contribute $\cos(\pi/4) = 0.7071$, and the fourth,
$a_1 - b_1 = 3\pi/4$, contributes $-\cos(3\pi/4) = +0.7071$ because of the minus sign in
$S$. Four times $0.7071$ is $2.8284 = 2\sqrt{2}$. The notebooks the source fills cannot
have come from any instruction card.

The card the lab asks you to write is worth running, because it is a good card. It gets
$E(a, b) = -1$ at equal angles and it depends only on the angle difference, both of
which the notebooks demand.

```python
import math
import random

a0, a1, b0, b1 = 0.0, math.pi / 2, math.pi / 4, -math.pi / 4
pairs = [(a0, b0), (a0, b1), (a1, b0), (a1, b1)]
rng = random.Random(7)
shots = 40000
totals = [0, 0, 0, 0]
for _ in range(shots):
    lam = rng.random() * 2 * math.pi           # the shared instruction card
    for i, (a, b) in enumerate(pairs):
        alice = 1 if math.cos(a - lam) >= 0 else -1
        bob = -1 if math.cos(b - lam) >= 0 else 1
        totals[i] += alice * bob
e = [t / shots for t in totals]
print("local correlations:", [round(x, 3) for x in e])
print("local S =", round(e[0] + e[1] + e[2] - e[3], 3))
```

With seed 7 the four correlations come out near $-0.5, -0.5, -0.5, +0.5$ and $S$ is
$-2.0$, right on the bound. The card is built to disagree at equal angles, so it
imitates $|\Psi^-\rangle$ rather than $|\Phi^+\rangle$ and its $S$ carries the opposite
sign; only the magnitude matters for the bound. That magnitude falls short because the
card's correlation is a straight line in the angle difference, $-(1 - 2|a-b|/\pi)$,
rather than a cosine, and a straight line through the same endpoints is the best a card
can manage. At a $45°$ difference it gives $|E| = 0.5$, a $75/25$ split, where the
notebooks say $0.707$, an $85/15$ split; the missing ten points, at each of four settings,
are the gap between $2$ and $2.83$.

## The mistake: reading the correlation as a message

The tempting error is to think that because Bob's lamp is correlated with Alice's
setting, Alice's choice of dial *does something* to Bob's particle, and that with enough
cleverness the effect could carry a bit. The reading's marginal check is the refutation:
Bob's outcome distribution is $0.5 / 0.5$ for every setting of Alice's dial, so nothing
Alice does changes anything Bob can observe on his own. What her setting changes is the
*joint* distribution, which is only visible once both columns are side by side, and
bringing them together takes an ordinary channel. The correlation is stronger than any
card can produce and weaker than a signal; both halves of that sentence are true, and the
first without the second is the most common misreading of the whole subject.

A more practical mistake shows up in the code. `expectation_ab` must rotate Alice's
qubit by $R_y(-a)$ and Bob's by $R_y(-b)$, both with the same sign. Use $R_y(+a)$ on one
side and $R_y(-b)$ on the other and the result is $\cos(a + b)$: at $a = b = \pi/4$ that
is $0$ instead of $1$, and the CHSH test reports $S = 0$ from a state that should give
$2\sqrt{2}$. It is tempting because for $|\Phi^+\rangle$ the *sign* of $a - b$ does not
matter, so flipping both is harmless and flipping one is not, and nothing in a single
correlation at $a = 0$ tells you which you did.

## Where the idea stops

$2\sqrt{2}$ is not merely what these angles happen to give; it is the largest value any
quantum state and any measurements can reach, a fact known as Tsirelson's bound. So the
gap between $2$ and $2.83$ is the whole of the quantum advantage here, and no cleverer
state pushes it further. The bound of $2$ is likewise not fragile: a product state, such
as $|00\rangle$, obeys it for every choice of angles, which is the lab's product-state
test, because a product state *is* an instruction card with no randomness.

Finite shots blur both numbers. The lab's `sample_correlation` estimates each $E$ from
seeded measurements with an error near $1/\sqrt{\text{shots}}$, and four of them add in
$S$, so a 40,000-shot local model can land at $2.01$ and a 40,000-shot quantum estimate
can land at $2.80$. Neither crosses the other's territory, and the tests allow the
slack. In a real laboratory the slack is where the arguments live: detectors that miss
some particles, dials chosen too slowly, or boxes too close together each open a
loophole through which a card could in principle sneak, and closing all of them at once
was worth a Nobel prize. The simulator has no loopholes, which is its virtue and its
limitation.

The lab, *Violating the CHSH inequality*, builds the four Bell states from gates,
computes the marginals that show each half as a fair coin, derives $\cos(a - b)$ from
rotations and the Born rule, estimates it from samples, assembles $S$, and then writes
the instruction card and watches it stop at $2$. Every number above appears in one of
its tests.
''',
                },
            ],
            "quiz": {
                "title": "Correlations, marginals and the bound",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Alice and Bob share $|\\Phi^+\\rangle$ and Alice sets her dial to $a = 1.9$ rad while Bob stays at $0$. What does Bob's own column of results look like?",
                        "opts": [
                            "Biased towards $+1$ by $\\cos(1.9)$, since the correlation leaks into his marginal",
                            "A fair coin, exactly as it would be for any setting of Alice's dial whatsoever",
                            "A fair coin only on average, with runs that mirror Alice's outcomes in order",
                            "Undefined until Alice's result is known, since his state is not fixed before then",
                        ],
                        "a": 1,
                        "whys": [
                            r"The correlation is a property of the *joint* distribution and never reaches a marginal. Summing the four joint probabilities over Alice's outcome gives $0.5$ and $0.5$ for every $a$, which the reading's last two printed lines show.",
                            r"Summing the joint probabilities over Alice's outcome gives $[0.5, 0.5]$ whatever her angle; that is the no-signalling fact.",
                            r"Bob's column on its own has no structure at all, in order or in total; the runs are those of a fair coin. The mirroring is only visible when his column is placed beside Alice's, which takes an ordinary channel.",
                            r"Bob's marginal is perfectly well defined before, during and after Alice's measurement, and it is $0.5 / 0.5$ in every case. Collapse changes the joint description, not what Bob can see by himself.",
                        ],
                        "why": r"""
Bob's marginal is the sum of the joint probabilities over Alice's outcome, and for
every Bell state and every angle Alice chooses that sum is $[0.5, 0.5]$. Nothing Alice
does is visible in Bob's notebook alone; the correlation lives in the comparison of
the two notebooks, which is why it cannot carry a message. This is the lab's
`marginal_probabilities`, and the reading's run at $a = 1.9$ shows the same numbers
as at $a = 0$.
""",
                    },
                    {
                        "q": "For $|\\Phi^+\\rangle$, what is $E(a, b)$ when the dials differ by $60°$?",
                        "opts": [
                            "$0.5$, because the correlation is $\\cos$ of the difference between the dials",
                            "$0.75$, because the correlation is $\\cos^2$ of half the difference",
                            "$0.33$, because the correlation falls linearly from $1$ at $0°$ to $-1$ at $180°$",
                            "$0.87$, because the correlation is $\\cos$ of half the angle difference",
                        ],
                        "a": 0,
                        "whys": [
                            r"$\cos 60° = 0.5$: agreement $\cos^2 30° = 0.75$ minus disagreement $\sin^2 30° = 0.25$.",
                            r"$\cos^2(30°) = 0.75$ is the *probability of agreement*, not the correlation. The correlation subtracts the disagreement probability, $0.25$, and $0.75 - 0.25 = 0.5$.",
                            r"A straight line through the endpoints is what the instruction-card model gives, and at $60°$ it would say $0.33$. The quantum correlation is a cosine, and the difference between the line and the curve is exactly what CHSH measures.",
                            r"$\cos 30° = 0.87$ is the modulus of the agreeing amplitude, up to the $1/\sqrt{2}$. Probabilities are squares of amplitudes and the correlation is a difference of probabilities, so the amplitude has to be squared and combined first.",
                        ],
                        "why": r"""
After the rotations the agreeing outcomes carry probability $\cos^2\frac{a-b}{2}$ and
the disagreeing ones $\sin^2\frac{a-b}{2}$. At $60°$ those are $0.75$ and $0.25$, and
the correlation is their difference, $0.5$, which is $\cos 60°$ by the double-angle
identity. The agreement probability alone, the amplitude alone, and the straight line
of the local model are each one step short of the answer.
""",
                    },
                    {
                        "q": "In the derivation of $|S| \\le 2$, what single assumption does the bound rest on?",
                        "opts": [
                            "That the hidden variable is drawn uniformly at random, so the four correlations average out to zero",
                            "That each lamp is a definite function of its own dial and the shared card, not of the other dial",
                            "That the two particles were prepared in the same state, so their cards are identical",
                            "That the four dial settings are spaced $45°$ apart, which is where the algebra closes",
                        ],
                        "a": 1,
                        "whys": [
                            r"No distribution over the cards was assumed; the argument shows $s(\lambda) = \pm 2$ for every card and then observes that an average of numbers in $[-2, 2]$ stays in $[-2, 2]$ whatever the weights.",
                            r"Locality: $A$ depends on $a$ and $\lambda$, $B$ on $b$ and $\lambda$, so the four lamp values on one card are fixed $\pm 1$s and one bracket must vanish.",
                            r"The cards may be as correlated or as different as you like; the two particles may even carry different cards, as long as each lamp reads only its own. The bound does not care what is written, only who can read it.",
                            r"The angles are chosen to make the quantum value as large as possible; the bound itself holds for any four settings whatsoever, because the algebra of $\pm 1$ values does not mention angles.",
                        ],
                        "why": r"""
Write $s = A_0(B_0 + B_1) + A_1(B_0 - B_1)$ with each lamp value $\pm 1$. That is
only possible if $A_0$ and $A_1$ are definite values on the same card, fixed
independently of which $b$ Bob chose, and likewise for Bob. Given that, one bracket
is zero and the other $\pm 2$, so $|s| \le 2$ card by card and hence on average. The
distribution of cards, their content, and the particular angles play no part.
""",
                    },
                    {
                        "q": "A student's `expectation_ab` rotates Alice by $R_y(+a)$ and Bob by $R_y(-b)$. Which symptom reveals the bug?",
                        "opts": [
                            "$E(a, b)$ comes out as $\\cos(a + b)$, so the CHSH value with the standard angles is $0$",
                            "$E(a, b)$ comes out as $-\\cos(a - b)$, so the CHSH value flips its sign to $-2\\sqrt{2}$ overall",
                            "$E(a, b)$ is right but Bob's marginal drifts away from $0.5$ at large $a$",
                            "$E(0, 0)$ is $0$ instead of $1$, so the equal-angles test fails immediately",
                        ],
                        "a": 0,
                        "whys": [
                            r"With one sign flipped only the sum of the angles survives, and at $a = b = \pi/4$ the correlation reads $\cos(\pi/2) = 0$; the four CHSH terms then cancel.",
                            r"A global sign on every correlation would come from using $|\Psi^-\rangle$ in place of $|\Phi^+\rangle$, not from a rotation sign. The rotation error changes $a - b$ into $a + b$, which is a different function, not a negated one.",
                            r"The marginals are $0.5 / 0.5$ for any rotation of either qubit, right or wrong, because a Bell state's halves are maximally mixed. The bug is invisible in the marginals, which is one reason it is easy to miss.",
                            r"At $a = b = 0$ neither rotation does anything, so $E(0, 0) = 1$ comes out correctly and the equal-angles test passes. The bug only appears once both angles are non-zero.",
                        ],
                        "why": r"""
Flipping one sign turns the difference $a - b$ into the sum $a + b$. Everything at
$a = 0$ or $b = 0$ still passes, including the equal-angles test at $0$ and every
marginal, so the bug survives until both dials move. With the standard CHSH angles
the four terms become $\cos(\pi/4), \cos(-\pi/4), \cos(3\pi/4), -\cos(\pi/4)$, and
they sum to $0$ rather than $2\sqrt{2}$.
""",
                    },
                    {
                        "q": "Could a better-designed pair of instruction cards, or a cleverer quantum state, push $|S|$ past $2\\sqrt{2}$?",
                        "opts": [
                            "Cards cannot pass $2$ and no quantum state can pass $2\\sqrt{2}$; both are hard ceilings",
                            "Cards cannot pass $2$, but a three-qubit entangled state can reach $4$ with these settings",
                            "Better cards could approach $2\\sqrt{2}$ given enough shared randomness, but never exceed it",
                            "Both ceilings are artefacts of the chosen angles and move if the angles change",
                        ],
                        "a": 0,
                        "whys": [
                            r"$|S| \le 2$ for every local model, and Tsirelson's bound caps every quantum state and measurement at $2\sqrt{2}$.",
                            r"Adding qubits does not raise the CHSH ceiling; Tsirelson's bound applies to any quantum state whatsoever. There are other inequalities for more parties, but this $S$ with two dials each stops at $2\sqrt{2}$.",
                            r"Shared randomness is exactly what the card already has, and the derivation shows every card gives $s = \pm 2$ regardless of how it was made or how much randomness went into it. Averaging cannot exceed $2$.",
                            r"The angles were chosen to *reach* the quantum maximum; changing them lowers the quantum value and leaves the local bound at $2$, since that bound never mentioned an angle.",
                        ],
                        "why": r"""
The local bound of $2$ follows from the $\pm 1$ algebra for any card and any angles.
The quantum value at these angles is $2\sqrt{2}$, and Tsirelson showed no quantum
state or measurement can exceed that for this combination of four correlations.
The gap between the two is therefore the entire quantum advantage in this
experiment, and it cannot be widened from either side.
""",
                    },
                ],
            },
            "lab": {
                "title": "Violating the CHSH inequality",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
`qlib.py` is the simulator from module 2, cleaned up and given to you. Import
from it; do not re-derive it.

**`bell_state(name)`** — build one of `"phi+"`, `"phi-"`, `"psi+"`, `"psi-"` with
gates, not by typing amplitudes. Any other name is a `ValueError`.

```text
phi+ = (|00> + |11>)/sqrt(2)      phi- = (|00> - |11>)/sqrt(2)
psi+ = (|01> + |10>)/sqrt(2)      psi- = (|01> - |10>)/sqrt(2)
```

Each is `H` on qubit 0 then `CNOT(0 -> 1)`, applied to a different starting
basis state — work out which.

**`marginal_probabilities(state, qubit)`** — `[p0, p1]` for one qubit of a
two-qubit state, summing the joint probabilities over the other qubit. Every
Bell state gives `[0.5, 0.5]` on both halves.

**`expectation_ab(state, a, b)`** — the exact correlation. Rotate qubit 0 by
`ry(-a)`, qubit 1 by `ry(-b)`, then sum `p_k` weighted by `+1` when the two bits
agree and `-1` when they differ.

**`sample_correlation(state, a, b, shots, seed)`** — the same quantity estimated
from seeded `sample_counts`. It should track `expectation_ab` to about
`1/sqrt(shots)`.

**`chsh_value(state, a0, a1, b0, b1)`**

```text
S = E(a0,b0) + E(a0,b1) + E(a1,b0) - E(a1,b1)
```

With `|Phi+>` and `a0 = 0, a1 = pi/2, b0 = pi/4, b1 = -pi/4` this reaches
`2*sqrt(2) = 2.828...`.

**`lhv_chsh(a0, a1, b0, b1, shots, seed)`** — the same `S`, but from a *local
hidden-variable* model: draw a shared angle `lam` uniformly in `[0, 2*pi)`, then
`A(theta) = +1 if cos(theta - lam) >= 0 else -1` and `B(theta) = -A(theta)`.
Both outcomes depend only on the local angle and on `lam`. No such model can
push `|S|` above 2, and yours will not.
''',
                "files": [
                    {"name": "qlib.py", "content": QLIB, "ro": True},
                    {"name": "main.py", "content": r'''
import math
import random

from qlib import (apply_1q, apply_cnot, probabilities, ry, sample_counts,
                  zero_state, H, X)


def bell_state(name):
    """One of the four Bell states, built from gates."""
    # your code here


def marginal_probabilities(state, qubit):
    """[p0, p1] for one qubit of a two-qubit state."""
    # your code here


def expectation_ab(state, a, b):
    """Exact correlation <A(a) B(b)> in {-1, +1} outcomes."""
    # your code here


def sample_correlation(state, a, b, shots, seed):
    """The same correlation estimated from seeded measurements."""
    # your code here


def chsh_value(state, a0, a1, b0, b1):
    """S = E(a0,b0) + E(a0,b1) + E(a1,b0) - E(a1,b1)."""
    # your code here


def lhv_chsh(a0, a1, b0, b1, shots, seed):
    """The same S from a shared-randomness local hidden-variable model."""
    # your code here


A0, A1, B0, B1 = 0.0, math.pi / 2, math.pi / 4, -math.pi / 4
print("quantum S:", chsh_value(bell_state("phi+"), A0, A1, B0, B1))
print("local S:  ", lhv_chsh(A0, A1, B0, B1, 40000, 7))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random

from qlib import (apply_1q, apply_cnot, probabilities, ry, sample_counts,
                  zero_state, H, X)

# Each Bell state is H then CNOT applied to a different computational basis
# state: |00> -> phi+, |10> -> phi-, |01> -> psi+, |11> -> psi-.
BELL_PREP = {"phi+": (0, 0), "phi-": (1, 0), "psi+": (0, 1), "psi-": (1, 1)}


def bell_state(name):
    """One of the four Bell states, built from gates."""
    if name not in BELL_PREP:
        raise ValueError(f"unknown Bell state {name!r}")
    flip0, flip1 = BELL_PREP[name]
    state = zero_state(2)
    if flip0:
        state = apply_1q(state, X, 0)
    if flip1:
        state = apply_1q(state, X, 1)
    state = apply_1q(state, H, 0)
    return apply_cnot(state, 0, 1)


def marginal_probabilities(state, qubit):
    """[p0, p1] for one qubit of a two-qubit state."""
    if len(state) != 4:
        raise ValueError("this lab works on two-qubit states")
    if qubit not in (0, 1):
        raise ValueError(f"qubit {qubit} out of range")
    probs = probabilities(state)
    shift = 1 - qubit
    out = [0.0, 0.0]
    for k, p in enumerate(probs):
        out[(k >> shift) & 1] += p
    return out


def expectation_ab(state, a, b):
    """Exact correlation <A(a) B(b)> in {-1, +1} outcomes."""
    # Measuring along cos(t)Z + sin(t)X is Ry(-t) followed by a Z measurement.
    rotated = apply_1q(state, ry(-a), 0)
    rotated = apply_1q(rotated, ry(-b), 1)
    total = 0.0
    for k, p in enumerate(probabilities(rotated)):
        x = (k >> 1) & 1
        y = k & 1
        total += p if x == y else -p
    return total


def sample_correlation(state, a, b, shots, seed):
    """The same correlation estimated from seeded measurements."""
    rotated = apply_1q(state, ry(-a), 0)
    rotated = apply_1q(rotated, ry(-b), 1)
    counts = sample_counts(rotated, shots, seed)
    agree = counts.get(0, 0) + counts.get(3, 0)
    differ = counts.get(1, 0) + counts.get(2, 0)
    return (agree - differ) / shots


def chsh_value(state, a0, a1, b0, b1):
    """S = E(a0,b0) + E(a0,b1) + E(a1,b0) - E(a1,b1)."""
    return (expectation_ab(state, a0, b0)
            + expectation_ab(state, a0, b1)
            + expectation_ab(state, a1, b0)
            - expectation_ab(state, a1, b1))


def lhv_chsh(a0, a1, b0, b1, shots, seed):
    """The same S from a shared-randomness local hidden-variable model."""
    rng = random.Random(seed)
    pairs = [(a0, b0), (a0, b1), (a1, b0), (a1, b1)]
    totals = [0, 0, 0, 0]
    for _ in range(shots):
        lam = rng.random() * 2 * math.pi
        for i, (a, b) in enumerate(pairs):
            # Alice sees only her angle and lam; Bob only his. That locality is
            # the whole content of the bound.
            alice = 1 if math.cos(a - lam) >= 0 else -1
            bob = -1 if math.cos(b - lam) >= 0 else 1
            totals[i] += alice * bob
    e = [t / shots for t in totals]
    return e[0] + e[1] + e[2] - e[3]


A0, A1, B0, B1 = 0.0, math.pi / 2, math.pi / 4, -math.pi / 4
print("quantum S:", chsh_value(bell_state("phi+"), A0, A1, B0, B1))
print("local S:  ", lhv_chsh(A0, A1, B0, B1, 40000, 7))
'''}],
                "hints": [
                    "Apply `X` to qubit 0, qubit 1, both or neither before the H+CNOT pair — that is the only difference between the four Bell states.",
                    "For a marginal, add up the joint probabilities that share the bit you care about: on two qubits, qubit 0's bit is `(k >> 1) & 1`.",
                    "A correlation over +/-1 outcomes is `(agreements - disagreements) / shots`; the exact version replaces counts with probabilities.",
                    "In `lhv_chsh` draw `lam` once per trial and reuse it for all four angle pairs — that shared randomness is exactly what a local model is allowed.",
                ],
                "tests": [
                    {"name": "The four Bell states have the right amplitudes", "code": r'''
_r = 0.7071067811865476
_want = {"phi+": [_r, 0, 0, _r], "phi-": [_r, 0, 0, -_r],
         "psi+": [0, _r, _r, 0], "psi-": [0, _r, -_r, 0]}
for _name, _amps in _want.items():
    _got = bell_state(_name)
    assert len(_got) == 4, f"bell_state({_name!r}) returned {len(_got)} amplitudes"
    for _k, _a in enumerate(_amps):
        assert abs(_got[_k] - _a) < 1e-9, \
            f"bell_state({_name!r})[{_k}] is {_got[_k]!r}, expected {_a!r}"
'''},
                    {"name": "An unknown Bell state is rejected", "code": r'''
for _bad in ("phi", "PHI+", "", "psi++"):
    try:
        bell_state(_bad)
        assert False, f"bell_state({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Each half of a Bell pair looks random", "code": r'''
for _name in ("phi+", "phi-", "psi+", "psi-"):
    for _q in (0, 1):
        _m = marginal_probabilities(bell_state(_name), _q)
        assert abs(_m[0] - 0.5) < 1e-9 and abs(_m[1] - 0.5) < 1e-9, \
            f"marginal of {_name!r} qubit {_q} is {_m!r}, expected [0.5, 0.5]"
from qlib import apply_1q as _a1, zero_state as _zs, H as _H
_prod = _a1(_zs(2), _H, 1)
assert abs(marginal_probabilities(_prod, 0)[0] - 1.0) < 1e-9, \
    "For |0>|+> qubit 0 is certainly 0"
assert abs(marginal_probabilities(_prod, 1)[0] - 0.5) < 1e-9, \
    "For |0>|+> qubit 1 is an even coin"
'''},
                    {"name": "expectation_ab reproduces cos(a - b)", "code": r'''
_phi = bell_state("phi+")
_psi = bell_state("psi-")
for _a in (0.0, 0.3, math.pi / 2, 1.9):
    for _b in (0.0, math.pi / 4, -math.pi / 4, 2.4):
        _got = expectation_ab(_phi, _a, _b)
        assert abs(_got - math.cos(_a - _b)) < 1e-9, \
            f"|phi+> E({_a}, {_b}) gave {_got!r}, expected {math.cos(_a - _b)!r}"
        _got = expectation_ab(_psi, _a, _b)
        assert abs(_got + math.cos(_a - _b)) < 1e-9, \
            f"|psi-> E({_a}, {_b}) gave {_got!r}, expected {-math.cos(_a - _b)!r}"
'''},
                    {"name": "Sampled correlations converge on the exact ones", "code": r'''
_phi = bell_state("phi+")
for _a, _b in [(0.0, 0.0), (0.0, math.pi / 4), (math.pi / 2, -math.pi / 4)]:
    _exact = expectation_ab(_phi, _a, _b)
    _est = sample_correlation(_phi, _a, _b, 20000, 5)
    assert abs(_est - _exact) < 0.03, \
        f"sample_correlation({_a}, {_b}) gave {_est!r}, exact value {_exact!r}"
assert sample_correlation(_phi, 0.0, 0.0, 500, 3) == 1.0, \
    "At equal angles |phi+> agrees on every shot"
assert (sample_correlation(_phi, 0.4, 1.1, 4000, 9)
        == sample_correlation(_phi, 0.4, 1.1, 4000, 9)), "The same seed must repeat"
'''},
                    {"name": "The quantum CHSH value beats the classical bound", "code": r'''
_A0, _A1, _B0, _B1 = 0.0, math.pi / 2, math.pi / 4, -math.pi / 4
_s = chsh_value(bell_state("phi+"), _A0, _A1, _B0, _B1)
assert abs(_s - 2 * math.sqrt(2)) < 1e-9, f"S is {_s!r}, expected 2*sqrt(2) = 2.8284271"
assert _s > 2.0, "The whole point is that S exceeds 2"
from qlib import zero_state as _zs2
_prod = _zs2(2)
_sp = chsh_value(_prod, _A0, _A1, _B0, _B1)
assert abs(_sp) <= 2.0 + 1e-9, f"A product state cannot violate the bound; got {_sp!r}"
'''},
                    {"name": "The local hidden-variable model stays under 2", "code": r'''
_A0, _A1, _B0, _B1 = 0.0, math.pi / 2, math.pi / 4, -math.pi / 4
_l = lhv_chsh(_A0, _A1, _B0, _B1, 40000, 7)
assert abs(_l) <= 2.06, f"A local model gave |S| = {abs(_l)!r}; it cannot exceed 2"
assert abs(_l) > 1.7, f"With these angles the local model should saturate near 2; got {_l!r}"
assert _l == lhv_chsh(_A0, _A1, _B0, _B1, 40000, 7), "The same seed must repeat"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Query algorithms: Deutsch-Jozsa and Grover",
            "summary": "Two ways interference buys you information a classical query cannot.",
            "concepts": [
                "The oracle model: cost is counted in calls to U_f, not in gates",
                "Reversibility forces the XOR form |x>|y> -> |x>|y xor f(x)>",
                "Phase kickback: with the ancilla in |->, U_f imprints (-1)^f(x) on the input register",
                "Deutsch-Jozsa separates constant from balanced in one query; classically 2^(n-1)+1 are needed in the worst case",
                "Grover as a rotation in the two-dimensional span of the marked and unmarked states",
                "Amplitude after k iterations is sin((2k+1)*theta) with sin(theta) = sqrt(M/N): overshooting makes it worse",
            ],
            "read": [
                {
                    "title": "Paying per question: one query for a promise, and a rotation that overshoots",
                    "minutes": 16,
                    "body": r'''
You are handed a sealed box. Feed it an $n$-bit number and it returns one bit, $f(x)$,
and you are charged for every use. The box comes with a promise: $f$ is either
*constant*, returning the same bit for every input, or *balanced*, returning $0$ on
exactly half the inputs and $1$ on the other half. Your job is to say which, with as few
uses as you can.

Classically you start querying. Two different answers and you are done: balanced. But
the same answer every time proves nothing until you have seen more than half the
inputs, because a balanced function could have hidden all its zeros in the half you
have not asked about yet. On $n = 3$ bits that is $5$ queries in the worst case, on
$10$ bits it is $513$, and in general $2^{n-1} + 1$. The quantum version of the box
answers with one query, for any $n$. This reading is about why, and then about a second
box, one that marks a needle in a haystack, where the quantum advantage is real but much
smaller than people expect.

## A box you can run backwards

A quantum gate is unitary and so reversible, and a function that maps eight inputs to
one bit is not; from the output $0$ you cannot recover which input produced it. The box
has to keep the input. The standard form takes an extra qubit $y$ and computes

$$U_f\,|x\rangle|y\rangle = |x\rangle|y \oplus f(x)\rangle,$$

which is its own inverse, since XOR-ing $f(x)$ in twice cancels. In the register layout
of this course, the $n$ input qubits are the high bits and the ancilla $y$ is the lowest
bit, so index $k$ is $2x + y$ and the oracle exchanges the amplitudes at $k$ and
$k \oplus 1$ wherever $f(k \gg 1) = 1$. That is the lab's `apply_oracle`, and it is a
permutation of the basis, the same kind of object as CNOT.

## Phase kickback, derived

Put the ancilla in $|-\rangle = (|0\rangle - |1\rangle)/\sqrt{2}$ before the query, by
applying X and then H to it. Now feed the box a single input $|x\rangle$:

$$U_f\,|x\rangle\frac{|0\rangle - |1\rangle}{\sqrt{2}}
= |x\rangle\frac{|f(x)\rangle - |1 \oplus f(x)\rangle}{\sqrt{2}}.$$

If $f(x) = 0$ the ancilla is unchanged. If $f(x) = 1$ it becomes
$(|1\rangle - |0\rangle)/\sqrt{2} = -|-\rangle$. Either way the ancilla ends up as
$|-\rangle$ times a sign, and the sign is $(-1)^{f(x)}$. Since the ancilla is the same
in both cases, the sign can be read as belonging to the input:

$$U_f\,|x\rangle|-\rangle = (-1)^{f(x)}\,|x\rangle|-\rangle.$$

Nothing in the box wrote to the input register, and yet the input register now carries
$f(x)$ in its phase. That is phase kickback, and it works on superpositions because
$U_f$ is linear: feed in $\sum_x c_x|x\rangle$ and every term picks up its own sign.

## Deutsch-Jozsa on one bit, amplitude by amplitude

Take $n = 1$, so the register is two qubits, index $k = 2x + y$, and carry the whole
algorithm through with numbers.

```python
import math

r = 1 / math.sqrt(2)
H = [[r, r], [r, -r]]
X = [[0, 1], [1, 0]]


def apply_1q(state, gate, target):
    n = len(state).bit_length() - 1
    shift = n - 1 - target
    out = list(state)
    for k in range(len(state)):
        if (k >> shift) & 1:
            continue
        k1 = k | (1 << shift)
        a, b = state[k], state[k1]
        out[k] = gate[0][0] * a + gate[0][1] * b
        out[k1] = gate[1][0] * a + gate[1][1] * b
    return out


def oracle(state, f):
    out = list(state)
    for k in range(len(state)):
        if f(k >> 1):
            out[k ^ 1] = state[k]
    return out


def show(label, state):
    print(f"{label:<16}", [round(a, 4) for a in state])


for name, f in (("f(x) = x", lambda x: x), ("f(x) = 0", lambda x: 0)):
    print("--", name, "--")
    state = [1.0, 0.0, 0.0, 0.0]                 # |x=0>|y=0>
    state = apply_1q(state, X, 1)                # ancilla to |1>
    state = apply_1q(apply_1q(state, H, 0), H, 1)
    show("before query", state)
    state = oracle(state, f)
    show("after query", state)
    state = apply_1q(state, H, 0)
    show("after final H", state)
    print("p(x = 0) =", round(state[0] ** 2 + state[1] ** 2, 4))
```

Before the query both runs hold $(0.5, -0.5, 0.5, -0.5)$: the input is
$(|0\rangle + |1\rangle)/\sqrt{2}$ and the ancilla is $|-\rangle$, and their product
spreads $\pm 1/2$ over the four indices with the sign following $y$. For $f(x) = x$ the
oracle swaps indices 2 and 3, the pair with $x = 1$, giving $(0.5, -0.5, -0.5, 0.5)$;
read against the ancilla, the $x = 1$ half has flipped sign, which is the kickback. The
final H on the input mixes pairs $(0, 2)$ and $(1, 3)$: index 0 gets
$(0.5 + (-0.5))/\sqrt{2} = 0$, index 2 gets $(0.5 - (-0.5))/\sqrt{2} = 0.7071$, and the
whole amplitude lands on $x = 1$. The probability of reading $x = 0$ is exactly $0$:
balanced. For $f(x) = 0$ the oracle does nothing, the final H undoes the first one, and
the amplitude returns to $x = 0$ with probability $1$: constant.

The general statement is one line. After the kickback the input register is
$\frac{1}{\sqrt{N}}\sum_x (-1)^{f(x)}|x\rangle$ with $N = 2^n$, and $H^{\otimes n}$ sends
$|x\rangle$ to $\frac{1}{\sqrt{N}}\sum_z (-1)^{x\cdot z}|z\rangle$, so the amplitude on
$z = 0$ is

$$\frac{1}{N}\sum_x (-1)^{f(x)},$$

which is $\pm 1$ for a constant function and $0$ for a balanced one, since a balanced
sum has as many $+1$s as $-1$s. There is no middle ground, so the lab's threshold of
$0.5$ on the probability of the all-zeros input is a formality. The lab's `deutsch_jozsa`
is this trace on $n$ input qubits, and its spy test counts the oracle calls to confirm
there was one.

## The mistake: believing the box was read $2^n$ times

The tempting reading of the superposition is that the box was queried on every input at
once and the answers were all collected. If that were true you could read $f$ out
entirely, and you cannot: a measurement returns one $n$-bit string, and the values of
$f$ are not sitting in any register. What the single query did was put $2^n$ signs into
$2^n$ amplitudes, and what the Hadamards did was compute *one* particular sum of those
signs and put its magnitude on a single basis state. The algorithm answers a yes/no
question about a *global property* of $f$, the promise made it a question with only two
answers, and interference is what evaluates the sum. Drop the promise and the algorithm
does not degrade gracefully; it gives a probability strictly between $0$ and $1$ that
tells you little.

## Grover: the needle, and the angle

The second box marks one index $m$ out of $N = 2^n$ by flipping its sign,
$|x\rangle \to (-1)^{[x = m]}|x\rangle$, which is the phase-kickback form of a lookup.
Classically you expect $N/2$ queries to find $m$. Start from the uniform superposition
$|s\rangle$ with every amplitude $1/\sqrt{N}$, and split it into the marked state
$|m\rangle$ and the normalised sum of the rest, $|u\rangle$. Both of these are real unit
vectors, they are orthogonal, and $|s\rangle$ lies in their plane at an angle $\theta$
from $|u\rangle$ with $\sin\theta = 1/\sqrt{N}$, since that is the overlap of $|s\rangle$
with $|m\rangle$.

The oracle reflects the state about $|u\rangle$: it negates the $|m\rangle$ component
and leaves everything else. The lab's `diffusion`, $a_k \to 2\bar{a} - a_k$ where
$\bar{a}$ is the mean amplitude, is the reflection about $|s\rangle$: written as a matrix
it is $2|s\rangle\langle s| - I$, and $\langle s|\psi\rangle/\sqrt{N}$ is the mean of the
amplitudes. Two reflections whose mirrors meet at angle $\theta$ compose to a rotation by
$2\theta$, in the direction from $|u\rangle$ towards $|m\rangle$. After $k$ rounds the
state is at angle $(2k + 1)\theta$ from $|u\rangle$, and its overlap with $|m\rangle$ is
$\sin\big((2k+1)\theta\big)$.

```python
import math

n, marked = 3, 5
N = 2 ** n
theta = math.asin(math.sqrt(1 / N))
state = [1 / math.sqrt(N)] * N
print(f"theta = {theta:.4f} rad, so one rotation turns by {2 * theta:.4f}")
for k in range(5):
    p = state[marked] ** 2
    predicted = math.sin((2 * k + 1) * theta) ** 2
    print(f"after {k} rounds: amplitude {state[marked]:>8.4f}  p = {p:.5f}  "
          f"sin^2((2k+1)theta) = {predicted:.5f}")
    state[marked] = -state[marked]                 # the phase oracle
    mean = sum(state) / N
    state = [2 * mean - a for a in state]          # inversion about the mean
```

With $N = 8$, $\theta = \arcsin(1/\sqrt{8}) = 0.3614$ rad. Round one by hand: every
amplitude starts at $0.3536$; the oracle makes the marked one $-0.3536$; the mean of
seven $0.3536$s and one $-0.3536$ is $0.2652$; reflecting, the unmarked amplitudes go to
$2(0.2652) - 0.3536 = 0.1768$ and the marked one to $2(0.2652) + 0.3536 = 0.8839$. Its
probability is $0.78125$, and $\sin^2(3\theta)$ agrees. Round two: mean of seven
$0.1768$s and one $-0.8839$ is $0.0442$; the marked amplitude becomes
$0.0884 + 0.8839 = 0.9723$, probability $0.9453$, which is the number the lab's Grover
test asks for. Round three overshoots: the rotation carries the state past
$|m\rangle$ and the probability falls to $0.3301$. Round four is worse still, at
$0.0122$, with the marked amplitude now negative.

The optimal count is where $(2k + 1)\theta$ is closest to $\pi/2$, that is
$k \approx \frac{\pi}{4\theta} - \frac{1}{2}$, and for large $N$, $\theta \approx
1/\sqrt{N}$, so $k \approx \frac{\pi}{4}\sqrt{N}$. The lab's `optimal_iterations` takes
the floor, and with $M$ marked items the same geometry gives $\sin\theta = \sqrt{M/N}$
and $k \approx \frac{\pi}{4}\sqrt{N/M}$. On two qubits, $\theta = \pi/6$, so a single
round rotates to exactly $\pi/2$ and the probability is $1$; the lab's two-qubit test
checks that exactness.

```python
import math

for n in range(1, 11):
    N = 2 ** n
    print(f"n = {n:>2}: N = {N:>5}  rounds = {math.floor(math.pi / 4 * math.sqrt(N)):>2}"
          f"  classical worst case for constant/balanced = {N // 2 + 1:>4}")
```

Ten qubits: a thousand-entry haystack searched in $25$ rounds. The right-hand column
is the other algorithm's classical cost, for scale.

## The mistake: more rounds are better

Anyone who has trained a model or run an iterative solver expects extra iterations to
help or at worst to plateau. Grover does neither. The state rotates at a fixed rate and
passes straight through the target; the probability of success is a sine squared, and
after the peak it falls back to nothing before rising again. The trace above shows it
going $0.125 \to 0.78 \to 0.95 \to 0.33 \to 0.01$. Running "a few extra rounds to be
safe" on $n = 3$ turns a $95\%$ search into a $1\%$ one. This is also why the count
depends on knowing $M$: with two marked items among sixteen, $\sin\theta$ grows from
$1/4$ to $\sqrt{2}/4$, the optimal count drops from three rounds to two, and the lab's
two-of-sixteen test lands on $0.9453$ after those two rounds, the same value as one item
among eight because the angle is the same.

## Where the advantage stops

Deutsch-Jozsa is exponential in query count but the problem is contrived: the promise
is doing the work, and a classical *randomised* algorithm that samples a handful of
inputs gets the right answer with overwhelming probability. It is a demonstration that
interference can compute a global sum with one query, not a useful program.

Grover's advantage is quadratic and it is provably the best possible for an unstructured
search: no quantum algorithm finds the marked item in fewer than order $\sqrt{N}$
queries. A quadratic gain is real but it is not the exponential one that headlines
promise, and it evaporates the moment the haystack has structure. Sorted data is
searched in $\log N$ classical steps; a database with an index does not need Grover;
and for SAT or optimisation the "oracle" is a circuit that must itself be built, so the
$\sqrt{N}$ speed-up applies to brute force, which is rarely the best classical method.
Counting only queries also hides the fact that the oracle may be expensive: a query that
costs a million gates does not become cheaper by being made in superposition.

The lab, *One query, and a quadratic search*, builds both boxes on the module 2 engine:
`apply_oracle` and `deutsch_jozsa` with its single counted call, and `phase_oracle`,
`diffusion`, `optimal_iterations` and `grover` with the $0.9453$ landing point and the
refusal of empty, repeated and out-of-range marked lists. The amplitudes in its tests
are the ones traced above.
''',
                },
            ],
            "quiz": {
                "title": "What one query can and cannot tell you",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Why is the ancilla prepared in $|-\\rangle$ rather than $|0\\rangle$ before the Deutsch-Jozsa query?",
                        "opts": [
                            "So that $f(x)$ can be read from the ancilla afterwards without disturbing the inputs",
                            "So that $U_f$ leaves the ancilla unchanged and pushes $(-1)^{f(x)}$ onto the input register",
                            "So that the ancilla is entangled with the inputs, which is what makes a single query enough",
                            "So that the oracle becomes reversible, since an XOR into $|0\\rangle$ would erase the input",
                        ],
                        "a": 1,
                        "whys": [
                            r"With $|0\rangle$ the ancilla does end up holding $f(x)$, but for a superposition of $x$ that entangles it with the input and a measurement returns $f$ at one random $x$, which is a single classical query.",
                            r"$|f(x)\rangle - |1 \oplus f(x)\rangle$ is $|-\rangle$ times $(-1)^{f(x)}$, so the ancilla factors out and the sign belongs to $|x\rangle$.",
                            r"The point of $|-\rangle$ is the opposite: it keeps the ancilla *unentangled*, a factor that can be ignored, so that the input register alone carries the phases the Hadamards then interfere.",
                            r"$U_f$ is reversible for any ancilla state; XOR is its own inverse and the input is kept regardless. Reversibility is why the ancilla exists at all, not why it is set to $|-\rangle$.",
                        ],
                        "why": r"""
The ancilla in $|-\rangle$ is an eigenstate of "flip me" with eigenvalue $-1$, so
XOR-ing $f(x)$ into it multiplies by $(-1)^{f(x)}$ and leaves the ancilla exactly as
it was. The sign has nowhere to live except on the input term $|x\rangle$, which is
phase kickback, and because the ancilla never becomes entangled it can be dropped
from the analysis. With the ancilla in $|0\rangle$ the answer is written *into* it
instead, which is the classical situation of one query returning one value.
""",
                    },
                    {
                        "q": "After the query, the input register holds $\\frac{1}{\\sqrt{N}}\\sum_x (-1)^{f(x)}|x\\rangle$. What do the final Hadamards compute?",
                        "opts": [
                            "Every value $f(x)$ at once, each stored in the phase of its own basis state for later readout",
                            "One specific sum of the signs, whose magnitude is placed on the single all-zeros basis state",
                            "The parity of $f$ over all inputs, which is $0$ for constant and $1$ for balanced functions",
                            "A uniform distribution if $f$ is constant and a random basis state if it is balanced",
                        ],
                        "a": 1,
                        "whys": [
                            r"The phases are already there before the Hadamards, and they are not readable: a measurement yields one $x$ and no phase. The Hadamards turn phases into a single interference sum, which destroys the individual values.",
                            r"The amplitude on $|0\dots0\rangle$ becomes $\frac{1}{N}\sum_x (-1)^{f(x)}$: $\pm 1$ when constant, $0$ when balanced.",
                            r"Parity is the XOR of all values, and a balanced function on $n \ge 2$ bits has even parity, the same as a constant one; parity cannot separate them. The sum computed is of $\pm 1$s, and it is its magnitude, not its parity, that distinguishes the cases.",
                            r"Backwards for the constant case: a constant $f$ produces the all-zeros state with certainty, not a uniform distribution. For balanced $f$ the all-zeros amplitude is exactly $0$ and the rest depends on which balanced function it is.",
                        ],
                        "why": r"""
$H^{\otimes n}$ sends $|x\rangle$ to $\frac{1}{\sqrt{N}}\sum_z (-1)^{x\cdot z}|z\rangle$,
so the amplitude on $z = 0$ collects $\frac{1}{N}\sum_x (-1)^{f(x)}$ with no
sign from $x \cdot z$. For constant $f$ every term has the same sign and the sum is
$\pm 1$; for balanced $f$ the terms cancel exactly. Interference evaluates one
global sum and answers one yes/no question; it does not deliver the individual
values, which is why the algorithm needs the promise.
""",
                    },
                    {
                        "q": "Grover search on $n = 3$ qubits with one marked item reaches $p = 0.945$ after two rounds. What does a third round give?",
                        "opts": [
                            "About $0.99$, since each round pushes more amplitude onto the marked state",
                            "About $0.33$, since the rotation carries the state past the target and back down",
                            "Exactly $0.945$ again, since the optimal point is a fixed point of the iteration",
                            "About $0.945$ with a flipped sign on the amplitude, which measurement cannot see",
                        ],
                        "a": 1,
                        "whys": [
                            r"Each round rotates by the same fixed angle $2\theta = 0.72$ rad regardless of where the state is. After two rounds it is at $5\theta = 1.81$ rad, already past $\pi/2$; a third round takes it to $7\theta = 2.53$ rad, where $\sin^2$ has fallen to $0.33$.",
                            r"$\sin^2(7\theta)$ with $\theta = 0.3614$ is $0.330$; the state has rotated past $|m\rangle$.",
                            r"Nothing about the iteration is a fixed point; it is a rotation by a constant angle and it never stops. The best round is where the angle happens to be nearest $\pi/2$, and the next round moves on from there.",
                            r"A sign flip alone would keep $p$ at $0.945$, but the rotation changes the magnitude too; the amplitude goes from $0.972$ to $0.575$. The sign does eventually turn negative, at round four, by which time $p$ is $0.012$.",
                        ],
                        "why": r"""
Each Grover round is a rotation by $2\theta$ in the plane of the marked and unmarked
states, with $\sin\theta = 1/\sqrt{8}$, and the success probability after $k$ rounds
is $\sin^2((2k+1)\theta)$. That is $0.945$ at $k = 2$ and $0.330$ at $k = 3$: the
state has swept through the target and is on its way back to the uniform
superposition and beyond. "More iterations are safer" is the intuition from
convergent solvers, and Grover is not one.
""",
                    },
                    {
                        "q": "Inversion about the mean sends $a_k \\to 2\\bar{a} - a_k$. What is it geometrically, and why does the pair oracle-then-diffusion make progress?",
                        "opts": [
                            "A projection onto the uniform state; repeated projections converge to the marked item",
                            "A reflection about the uniform state; two reflections compose to a rotation by twice the mirrors' angle",
                            "A normalisation step that rescales the marked amplitude after the oracle has negated it",
                            "A reflection about the marked state; repeating it alternately with the oracle cancels every unmarked amplitude",
                        ],
                        "a": 1,
                        "whys": [
                            r"A projection would collapse the state onto $|s\rangle$ and lose everything else, and repeating a projection changes nothing. The operator is $2|s\rangle\langle s| - I$, which has eigenvalues $\pm 1$: a reflection, not a projection.",
                            r"$2|s\rangle\langle s| - I$ reflects about $|s\rangle$; the oracle reflects about the unmarked state; together they rotate by $2\theta$.",
                            r"Diffusion is unitary and changes no norm; there is nothing to rescale. The oracle's sign flip is what diffusion feeds on: a negative amplitude sits far below the mean, so reflecting it about the mean sends it far above.",
                            r"Reflecting about the marked state is what the *oracle* does, up to sign, and repeating one reflection alternately with itself gives back the identity. Progress needs two *different* mirrors, and diffusion's mirror is the uniform state.",
                        ],
                        "why": r"""
Writing the uniform state as $|s\rangle$, the mean of the amplitudes is
$\langle s|\psi\rangle/\sqrt{N}$, and $a_k \to 2\bar{a} - a_k$ is the matrix
$2|s\rangle\langle s| - I$, a reflection about $|s\rangle$. The oracle is a reflection
about the unmarked state $|u\rangle$. Two reflections in mirrors that meet at angle
$\theta$ compose to a rotation by $2\theta$, and since $|s\rangle$ starts $\theta$ away
from $|u\rangle$, each round moves the state $2\theta$ closer to $|m\rangle$, which is
where the $\sin((2k+1)\theta)$ schedule comes from.
""",
                    },
                    {
                        "q": "A colleague proposes using Grover to search a sorted list of a million names. What is the best response?",
                        "opts": [
                            "Agree: Grover needs about $\\frac{\\pi}{4}\\sqrt{10^6} \\approx 785$ queries against a classical $500{,}000$",
                            "Decline: the list is sorted, so binary search finds any name in about $20$ comparisons",
                            "Decline: Grover only works when the number of marked items is exactly one",
                            "Agree, but note that the result is probabilistic and the classical search is certain",
                        ],
                        "a": 1,
                        "whys": [
                            r"The $785$ is the right Grover count and the $500{,}000$ is the right cost of *unstructured* classical search, but the list is sorted. Grover's quadratic gain is over brute force, and brute force is not the classical competitor here.",
                            r"$\log_2 10^6 \approx 20$: the structure in the data beats the quadratic speed-up by a very wide margin.",
                            r"Grover handles $M$ marked items with $\sin\theta = \sqrt{M/N}$ and $\approx\frac{\pi}{4}\sqrt{N/M}$ rounds, as the lab's two-of-sixteen test shows. The reason to decline is the sorting, not the count.",
                            r"Grover's success probability can be made as high as you like, and the deeper issue is not certainty. A sorted list has structure that a classical algorithm exploits in $\log N$ steps, and $20$ beats $785$ whether or not the $785$ come with a guarantee.",
                        ],
                        "why": r"""
Grover's $\sqrt{N}$ is a gain over *unstructured* search, where the only thing you
can do is ask the box about one index at a time. Sorted data is structured: binary
search finds any name in $\lceil\log_2 10^6\rceil = 20$ comparisons, which is far
fewer than the $785$ Grover rounds, and each Grover round also has to implement the
oracle as a circuit. The quadratic advantage is real and it is also easy to lose to
a better classical algorithm, which is the point of the reading's last section.
""",
                    },
                ],
            },
            "lab": {
                "title": "One query, and a quadratic search",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
Two algorithms on the `qlib` simulator. Registers are big-endian as before.

## Deutsch-Jozsa

`f` maps integers `0 .. 2^n - 1` to 0 or 1 and is promised to be either constant
or balanced.

**`apply_oracle(state, f, n)`** — the XOR oracle on `n + 1` qubits: the top `n`
bits are the input `x` and the bottom bit is the ancilla `y`. It sends
`|x>|y>` to `|x>|y xor f(x)>`, so amplitudes at `k` and `k xor 1` exchange
exactly when `f(k >> 1)` is 1.

**`deutsch_jozsa(f, n)`** — returns `"constant"` or `"balanced"`. Put the ancilla
in `|->` with `X` then `H`, put the inputs in uniform superposition with `H`,
call `apply_oracle` **once**, apply `H` to the inputs again, and read the total
probability of the input register being all zeros. Constant gives 1, balanced
gives 0.

## Grover

**`phase_oracle(state, marked)`** — negate the amplitude of every marked index.

**`diffusion(state)`** — inversion about the mean: `out[k] = 2*mean - state[k]`.

**`optimal_iterations(n, marked_count=1)`** — `floor(pi/4 * sqrt(N / M))`.

**`grover(n, marked, iterations=None)`** — start from the uniform superposition
over `2^n` indices, then alternate oracle and diffusion. `marked` is a list of
indices; an empty list, a repeat, or an out-of-range index is a `ValueError`.

**`grover_search(n, marked)`** — the most likely index after
`optimal_iterations` rounds.

```text
n = 2, marked = [3]  ->  1 iteration,  p(3) = 1.0 exactly
n = 3, marked = [5]  ->  2 iterations, p(5) = 0.9453...
```
''',
                "files": [
                    {"name": "qlib.py", "content": QLIB, "ro": True},
                    {"name": "main.py", "content": r'''
import math

from qlib import apply_1q, n_qubits, probabilities, zero_state, H, X


def apply_oracle(state, f, n):
    """XOR oracle on n input qubits plus one ancilla."""
    # your code here


def deutsch_jozsa(f, n):
    """Return "constant" or "balanced", using exactly one oracle call."""
    # your code here


def phase_oracle(state, marked):
    """Negate the amplitude of every marked basis index."""
    # your code here


def diffusion(state):
    """Inversion about the mean amplitude."""
    # your code here


def optimal_iterations(n, marked_count=1):
    """floor(pi/4 * sqrt(N / M))."""
    # your code here


def grover(n, marked, iterations=None):
    """The state after the Grover iterations."""
    # your code here


def grover_search(n, marked):
    """The most likely index after the optimal number of iterations."""
    # your code here


print("parity on 3 bits:", deutsch_jozsa(lambda x: bin(x).count("1") % 2, 3))
print("all zeros:       ", deutsch_jozsa(lambda x: 0, 3))
print("grover finds:    ", grover_search(3, [5]))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

from qlib import apply_1q, n_qubits, probabilities, zero_state, H, X


def apply_oracle(state, f, n):
    """XOR oracle on n input qubits plus one ancilla."""
    if len(state) != 2 ** (n + 1):
        raise ValueError("the oracle needs n input qubits plus one ancilla")
    out = list(state)
    for k in range(len(state)):
        # The ancilla is the least significant bit, so x is k >> 1.
        if f(k >> 1) & 1:
            out[k ^ 1] = state[k]
    return out


def deutsch_jozsa(f, n):
    """Return "constant" or "balanced", using exactly one oracle call."""
    if n < 1:
        raise ValueError("need at least one input qubit")
    state = zero_state(n + 1)
    state = apply_1q(state, X, n)          # ancilla -> |1>
    for q in range(n + 1):
        state = apply_1q(state, H, q)      # inputs -> uniform, ancilla -> |->
    state = apply_oracle(state, f, n)      # the single query
    for q in range(n):
        state = apply_1q(state, H, q)
    probs = probabilities(state)
    # Total probability of the input register reading all zeros.
    p_zero = sum(p for k, p in enumerate(probs) if (k >> 1) == 0)
    return "constant" if p_zero > 0.5 else "balanced"


def phase_oracle(state, marked):
    """Negate the amplitude of every marked basis index."""
    out = list(state)
    for m in marked:
        if not 0 <= m < len(state):
            raise ValueError(f"marked index {m} out of range")
        out[m] = -out[m]
    return out


def diffusion(state):
    """Inversion about the mean amplitude."""
    mean = sum(state) / len(state)
    return [2 * mean - a for a in state]


def optimal_iterations(n, marked_count=1):
    """floor(pi/4 * sqrt(N / M))."""
    if n < 1 or marked_count < 1 or marked_count > 2 ** n:
        raise ValueError("bad register size or marked count")
    return int(math.floor(math.pi / 4 * math.sqrt(2 ** n / marked_count)))


def grover(n, marked, iterations=None):
    """The state after the Grover iterations."""
    if n < 1:
        raise ValueError("need at least one qubit")
    size = 2 ** n
    if not marked:
        raise ValueError("Grover needs at least one marked index")
    if len(set(marked)) != len(marked):
        raise ValueError("marked indices must be distinct")
    for m in marked:
        if not 0 <= m < size:
            raise ValueError(f"marked index {m} out of range for {n} qubits")
    if iterations is None:
        iterations = optimal_iterations(n, len(marked))
    if iterations < 0:
        raise ValueError("iteration count cannot be negative")
    amp = 1 / math.sqrt(size)
    state = [complex(amp) for _ in range(size)]
    for _ in range(iterations):
        state = phase_oracle(state, marked)
        state = diffusion(state)
    return state


def grover_search(n, marked):
    """The most likely index after the optimal number of iterations."""
    probs = probabilities(grover(n, marked))
    best = 0
    for k, p in enumerate(probs):
        if p > probs[best]:
            best = k
    return best


print("parity on 3 bits:", deutsch_jozsa(lambda x: bin(x).count("1") % 2, 3))
print("all zeros:       ", deutsch_jozsa(lambda x: 0, 3))
print("grover finds:    ", grover_search(3, [5]))
'''}],
                "hints": [
                    "In the oracle the ancilla is the low bit: input `x` is `k >> 1` and the partner index is `k ^ 1`.",
                    "Build the result as `out = list(state)` and write `out[k ^ 1] = state[k]` only where `f(x)` is 1 — that single assignment covers both members of the pair as the loop reaches them.",
                    "After the final Hadamards, sum the probabilities of every index whose top n bits are zero; on n+1 qubits those are indices 0 and 1.",
                    "Inversion about the mean is one line: compute `mean = sum(state) / len(state)` and return `[2 * mean - a for a in state]`.",
                ],
                "tests": [
                    {"name": "The XOR oracle flips the ancilla", "code": r'''
from qlib import basis_state as _bs
# n = 2 inputs, one ancilla: index k = x*2 + y.
_f = lambda x: x & 1
for _x in range(4):
    for _y in (0, 1):
        _k = _x * 2 + _y
        _got = apply_oracle(_bs(3, _k), _f, 2)
        _want = _x * 2 + (_y ^ (_f(_x) & 1))
        assert abs(_got[_want] - 1) < 1e-12, \
            f"oracle on |{_x}>|{_y}> should give |{_x}>|{_y ^ _f(_x)}>; got {_got!r}"
_id = apply_oracle(_bs(3, 5), lambda x: 0, 2)
assert abs(_id[5] - 1) < 1e-12, "A constant-zero f leaves the register alone"
'''},
                    {"name": "Deutsch-Jozsa classifies both promises", "code": r'''
for _n in (1, 2, 3, 4):
    assert deutsch_jozsa(lambda x: 0, _n) == "constant", f"f = 0 on {_n} bits is constant"
    assert deutsch_jozsa(lambda x: 1, _n) == "constant", f"f = 1 on {_n} bits is constant"
    assert deutsch_jozsa(lambda x: bin(x).count("1") % 2, _n) == "balanced", \
        f"parity on {_n} bits is balanced"
    assert deutsch_jozsa(lambda x: x & 1, _n) == "balanced", \
        f"the low bit of x is balanced on {_n} bits"
assert deutsch_jozsa(lambda x: (x >> 2) & 1, 3) == "balanced", "The top bit is balanced too"
'''},
                    {"name": "Exactly one oracle call", "code": r'''
_calls = []
_real = apply_oracle
def _spy(state, f, n):
    _calls.append(n)
    return _real(state, f, n)
apply_oracle = _spy
deutsch_jozsa(lambda x: bin(x).count("1") % 2, 3)
apply_oracle = _real
assert len(_calls) == 1, \
    f"deutsch_jozsa called the oracle {len(_calls)} times; the whole point is one query"
'''},
                    {"name": "phase_oracle and diffusion do their jobs", "code": r'''
_s = [0.5 + 0j] * 4
_o = phase_oracle(_s, [3])
assert [round(a.real, 9) for a in _o] == [0.5, 0.5, 0.5, -0.5], f"Got {_o!r}"
assert _s[3] == 0.5, "phase_oracle must not mutate its argument"
_d = diffusion(_o)
assert abs(_d[3] - 1) < 1e-12 and all(abs(_d[k]) < 1e-12 for k in range(3)), \
    f"One iteration on two qubits should land exactly on |11>; got {_d!r}"
_m = diffusion([0.25 + 0j] * 4)
assert all(abs(a - 0.25) < 1e-12 for a in _m), "A flat state is its own mean, so nothing moves"
'''},
                    {"name": "optimal_iterations follows pi/4 sqrt(N/M)", "code": r'''
for _n, _want in [(1, 1), (2, 1), (3, 2), (4, 3), (5, 4), (6, 6), (10, 25)]:
    _got = optimal_iterations(_n)
    assert _got == _want, f"optimal_iterations({_n}) gave {_got}, expected {_want}"
assert optimal_iterations(4, 4) == 1, "Four marked items out of sixteen needs one round"
for _bad in [(0, 1), (3, 0), (2, 5)]:
    try:
        optimal_iterations(*_bad)
        assert False, f"optimal_iterations{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Grover amplifies to the known probabilities", "code": r'''
_st = grover(2, [3])
assert abs(abs(_st[3]) ** 2 - 1.0) < 1e-12, \
    f"On two qubits Grover is exact after one round; p = {abs(_st[3]) ** 2!r}"
_st = grover(3, [5])
assert abs(abs(_st[5]) ** 2 - 0.9453125) < 1e-9, \
    f"Three qubits, two rounds gives p = 0.9453125; got {abs(_st[5]) ** 2!r}"
_st = grover(4, [1, 9])
_p = abs(_st[1]) ** 2 + abs(_st[9]) ** 2
assert abs(_p - 0.9453125) < 1e-9, f"Two of sixteen marked gives 0.9453125; got {_p!r}"
_st = grover(4, [9], iterations=0)
assert abs(abs(_st[9]) ** 2 - 0.0625) < 1e-12, "Zero iterations leaves the uniform state"
assert abs(sum(abs(a) ** 2 for a in grover(5, [17])) - 1.0) < 1e-9, "Grover stays normalised"
'''},
                    {"name": "grover_search returns the marked index, and refuses nonsense", "code": r'''
for _n, _m in [(2, 3), (3, 5), (4, 9), (5, 17)]:
    _got = grover_search(_n, [_m])
    assert _got == _m, f"grover_search({_n}, [{_m}]) gave {_got}"
for _bad in [(3, []), (3, [8]), (3, [-1]), (3, [1, 1]), (0, [0])]:
    try:
        grover(*_bad)
        assert False, f"grover{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "The quantum Fourier transform and period finding",
            "summary": "The DFT as a circuit, and the peak structure that reveals a hidden period.",
            "concepts": [
                "The QFT is the discrete Fourier transform on amplitudes: out_k = sum_j x_j * exp(2*pi*i*j*k/N) / sqrt(N)",
                "As a circuit it costs O(n^2) gates: Hadamards interleaved with controlled phase rotations, then a bit reversal",
                "The controlled rotation angles halve at each step, so far-apart qubits barely interact — the basis of approximate QFT",
                "Measuring one register of a periodic superposition collapses the other into a shifted comb of period r",
                "The transform of a comb of period r is a comb of period N/r, so peaks sit near multiples of N/r",
                "Continued fractions turn a measured k/N into the denominator r, which is the classical half of Shor's algorithm",
            ],
            "read": [
                {
                    "title": "A comb of amplitudes, its transform, and the fraction that names the period",
                    "minutes": 16,
                    "body": r'''
Take the function $f(x) = 3^x \bmod 8$ and tabulate it for $x = 0$ to $7$: the values
are $1, 3, 1, 3, 1, 3, 1, 3$. It repeats every two steps. You can see that by looking,
because there are eight entries; Shor's algorithm needs the same fact about
$a^x \bmod N$ for an $N$ with hundreds of digits, where the period is astronomically long
and no table fits anywhere. The question this module answers is how a quantum register
can be made to reveal a period it cannot be made to print.

## The comb

Prepare two registers: $n$ qubits for $x$ in uniform superposition, and a second holding
$f(x)$, computed by a reversible circuit as in module 4. The joint state is
$\frac{1}{\sqrt{N}}\sum_x |x\rangle|f(x)\rangle$ with $N = 2^n$. Now measure the second
register. Suppose it reads $1$. The first register collapses onto every $x$ with
$f(x) = 1$, and nothing else: for $n = 3$ that is $x \in \{0, 2, 4, 6\}$, each with
amplitude $1/2$. A picket fence, or comb, of period $2$. Had the measurement read $3$ the
comb would be $\{1, 3, 5, 7\}$, the same fence shifted by one. The period is in the
spacing of the teeth, and the measurement told you nothing about it because every
outcome produces a comb with the same spacing. The shift, which is what you learnt, is
useless; the spacing, which is what you want, is still hidden in a state you cannot
read out. That is what the transform is for.

## The transform, straight from the definition

The quantum Fourier transform on $N$ amplitudes is the discrete Fourier transform
applied to the amplitude list:

$$\text{out}_k = \frac{1}{\sqrt{N}}\sum_{j=0}^{N-1} x_j\, e^{2\pi i\, jk/N}.$$

It is unitary, because the columns $e^{2\pi i jk/N}/\sqrt{N}$ are orthonormal, so it is
a legitimate gate, and its inverse flips the sign in the exponent. Feed it the comb.

```python
import cmath
import math

n = 3
N = 2 ** n
f = lambda x: pow(3, x, 8)
values = [f(x) for x in range(N)]
print("f(x) for x = 0..7:", values)

xs = [x for x in range(N) if f(x) == 1]
branch = [0j] * N
for x in xs:
    branch[x] = 1 / math.sqrt(len(xs))
print("branch with f = 1: ", [round(a.real, 4) for a in branch])


def qft(state):
    size = len(state)
    out = []
    for k in range(size):
        acc = 0j
        for j, amp in enumerate(state):
            acc += amp * cmath.exp(2j * math.pi * j * k / size)
        out.append(acc / math.sqrt(size))
    return out


spectrum = qft(branch)
print("QFT probabilities: ", [round(abs(a) ** 2, 4) for a in spectrum])
```

The output has probability $0.5$ at $k = 0$ and $k = 4$ and nothing anywhere else. Do
$k = 4$ by hand: the comb has teeth at $j = 0, 2, 4, 6$, and $e^{2\pi i\, j \cdot 4/8}
= e^{i\pi j}$ is $+1$ for every even $j$, so the four teeth add: $\frac{1}{\sqrt{8}} \cdot
4 \cdot \frac{1}{2} = 0.7071$, probability $0.5$. Now $k = 2$: the phases are
$e^{i\pi j/2}$ at $j = 0, 2, 4, 6$, which is $1, -1, 1, -1$, and the teeth cancel to
$0$. In general, a comb of period $r$ with $M = N/r$ teeth at $j = 0, r, 2r, \dots$
transforms to

$$\text{out}_k = \frac{1}{\sqrt{NM}}\sum_{m=0}^{M-1} e^{2\pi i\, mrk/N},$$

a geometric series in $e^{2\pi i\, rk/N}$. When $rk/N$ is an integer every term is $1$
and the sum is $M$; otherwise the terms walk evenly round the unit circle and cancel.
So the transform of a comb of period $r$ is a comb of period $N/r$: peaks at
$k = 0, N/r, 2N/r, \dots$, each with probability $1/r$. The shift of the original comb
became a phase on each peak, $e^{2\pi i\, sk/N}$ for a shift $s$, which the Born rule
discards. That is the whole trick: measurement turned the shift, which you do not want,
into an invisible phase, and left the spacing, which you do, as the position of a peak.

## From a peak to the period

Measure the transformed register and you get some $k$ near a multiple of $N/r$, so
$k/N \approx c/r$ for an unknown integer $c$. For $3^x \bmod 8$ the peaks are exactly at
$k = 0$ and $k = 4$, so $k/N = 4/8 = 1/2$ in lowest terms and the denominator is $2$.
When $r$ divides $N$ the fraction is exact; when it does not, the peaks sit near
non-integer positions and $k/N$ is only close to $c/r$. The tool for recovering a
fraction with a small denominator from a close decimal is the continued fraction
expansion, and it must be done in integers.

```python
def best_rational(num, den, qmax):
    a = num // den
    p_prev, q_prev = 1, 0
    p, q = a, 1
    r_num, r_den = num - a * den, den
    print(f"  convergent {p}/{q}")
    while r_num != 0:
        r_num, r_den = r_den, r_num
        a = r_num // r_den
        p_new, q_new = a * p + p_prev, a * q + q_prev
        if q_new > qmax:
            print(f"  next would be {p_new}/{q_new}, over qmax = {qmax}")
            break
        p_prev, q_prev = p, q
        p, q = p_new, q_new
        r_num = r_num - a * r_den
        print(f"  convergent {p}/{q}")
    return (p, q)


print("11/32 with qmax 7  ->", best_rational(11, 32, 7))
print("21/32 with qmax 10 ->", best_rational(21, 32, 10))
```

Follow $11/32$. The integer part is $0$, leaving $11/32$. Invert: $32/11 = 2$ remainder
$10/11$, so the next convergent is $1/2$. Invert the remainder: $11/10 = 1$ remainder
$1/10$, convergent $1/3$. Invert again: $10/1 = 10$, which would give $11/32$ itself with
denominator $32 > 7$, so the expansion stops and the answer is $(1, 3)$. The recurrence
$p_{\text{new}} = a\,p + p_{\text{prev}}$, $q_{\text{new}} = a\,q + q_{\text{prev}}$ is
the standard one, and every quantity in it is an integer. The `qmax` is the largest
period worth considering, which for order-finding is the modulus itself, and it is what
stops the expansion from returning the exact but useless $k/N$.

## The mistake: the first peak is not the period

Two errors come from the same misreading. The first is to take the position of the
peak as the answer. For $7^x \bmod 15$ on four qubits the period is $4$ and the peaks
are at $k = 0, 4, 8, 12$; reading "$4$" off the second peak happens to be right here,
which makes the habit stick, and for $2^x \bmod 7$ on five qubits, period $3$, the peaks
are at $k \approx 10.7$ and $21.3$ and there is no $3$ anywhere in sight. The period is
the *denominator* of $k/N$, not $k$.

The second error is to use one peak. Reduce $8/16$ and you get $1/2$, denominator $2$,
which is a divisor of the period and not the period. Any peak at $cN/r$ where $c$ and
$r$ share a factor gives a reduced denominator that is too small. The remedy is to take
every peak that clears the threshold, reduce each, and combine their denominators with
a least common multiple.

```python
import cmath
import math
from math import gcd


def qft(state):
    size = len(state)
    return [sum(amp * cmath.exp(2j * math.pi * j * k / size) for j, amp in enumerate(state))
            / math.sqrt(size) for k in range(size)]


def best_rational(num, den, qmax):
    a = num // den
    p_prev, q_prev, p, q = 1, 0, a, 1
    r_num, r_den = num - a * den, den
    while r_num != 0:
        r_num, r_den = r_den, r_num
        a = r_num // r_den
        p_new, q_new = a * p + p_prev, a * q + q_prev
        if q_new > qmax:
            break
        p_prev, q_prev, p, q = p, q, p_new, q_new
        r_num = r_num - a * r_den
    return (p, q)


def period_report(f, n, qmax):
    N = 2 ** n
    first = min(f(x) for x in range(N))
    xs = [x for x in range(N) if f(x) == first]
    branch = [0j] * N
    for x in xs:
        branch[x] = 1 / math.sqrt(len(xs))
    probs = [abs(a) ** 2 for a in qft(branch)]
    peak = max(probs[1:])
    ks = [k for k in range(1, N) if probs[k] >= 0.4 * peak]
    qs = [best_rational(k, N, qmax)[1] for k in ks]
    period = 1
    for q in qs:
        period = period * q // gcd(period, q)
    print(f"peaks at k = {ks}, denominators {qs}, lcm = {period}")


period_report(lambda x: pow(7, x, 15), 4, 15)     # 7^x mod 15 repeats every 4
period_report(lambda x: pow(2, x, 7), 5, 7)       # 2^x mod 7 repeats every 3
```

For $7^x \bmod 15$ the three non-zero peaks reduce to denominators $4, 2, 4$; the middle
one alone would have said $2$, and the lcm says $4$. For $2^x \bmod 7$ the period $3$
does not divide $32$, so the peaks are smeared: the threshold picks up $k = 11$ and
$k = 21$, whose continued fractions with `qmax = 7` both give denominator $3$. This is
the lab's `estimate_period`, threshold and lcm included, and the reason the brief says
the lcm step matters.

## The same transform as a circuit

The definition above costs $N^2$ multiplications, which for a real register is
$4^n$, hopeless. The point of the *quantum* Fourier transform is that the same unitary
factorises into $O(n^2)$ gates. Write $k$ in binary and split the exponent
$e^{2\pi i\, jk/N}$ bit by bit: it becomes a product over the bits of $j$, and the
transform of a basis state $|j\rangle$ turns out to be a product of one-qubit states,

$$\frac{1}{\sqrt{N}}\bigotimes_{l}\Big(|0\rangle + e^{2\pi i\, (0.j_l j_{l+1}\dots)}|1\rangle\Big),$$

where $0.j_l j_{l+1}\dots$ is a binary fraction. Each factor is an H on qubit $l$, which
supplies the $|0\rangle + e^{2\pi i\, 0.j_l}|1\rangle$ part since $0.j_l$ is $0$ or a
half, followed by a controlled phase from each later qubit $j$ contributing its bit at
the right binary place: $2\pi/2^{j-l+1}$, halving with distance. That is the loop in the
lab's `qft_circuit`: for each qubit $i$, H, then for each $j > i$ a controlled phase of
$2\pi/2^{j-i+1}$ with control $j$ and target $i$. The product comes out with the qubits
in reverse order, so the last step swaps qubit $i$ with $n - 1 - i$. Leave the swaps
out and every amplitude is present but permuted by bit reversal; the lab's test against
the definition will say so, and on one qubit, where there is nothing to swap, it will
pass, which is why that test also runs on two and three.

The halving angles are also why an *approximate* QFT exists: the phase from a qubit far
down the register is $2\pi/2^{d}$ for distance $d$, and past $d \approx \log n$ it is
below any realistic gate precision, so those controlled phases can be dropped for a cost
of $O(n \log n)$ gates and a negligible error.

## Where it stops

The transform reads a period out of a comb whose spacing is hidden in $2^n$ amplitudes,
and it does that with $O(n^2)$ gates. It does not let you load arbitrary data and
compute its spectrum faster than a classical FFT: preparing a general amplitude list
takes exponential work, and the transformed amplitudes cannot be read out, only sampled.
The period-finding use survives because the comb is cheap to prepare, via one reversible
evaluation of $f$ in superposition, and because the only thing you need from the
spectrum is the position of a peak, which one sample gives with reasonable probability.

Even then, one sample can return $k = 0$, which says nothing, or a $k$ whose reduced
fraction has a denominator that divides $r$, which is why the classical half of Shor's
algorithm repeats the quantum part a few times and takes lcms. The lab's threshold of
$40\%$ of the tallest peak is a simulator's convenience: it reads every peak at once
from the full probability list, which a real device cannot do. And nothing here factors
anything yet; turning a period $r$ into a factor of a modulus needs $r$ even and
$a^{r/2} \not\equiv -1$, which is more classical number theory, on top of what this
reading did. What the lab *QFT on three qubits, and finding a period* builds is the
quantum core: `qft` from the definition, `qft_circuit` from gates with its bit
reversal, `best_rational` in integers, `periodic_branches` for the comb, and
`estimate_period` to turn peaks into $r$.
''',
                },
            ],
            "quiz": {
                "title": "Combs, peaks and denominators",
                "minutes": 8,
                "questions": [
                    {
                        "q": "After the second register is measured, the first register holds a comb of period $r$ with some shift $s$. Why does the shift not matter?",
                        "opts": [
                            "Because every measurement outcome of the second register happens to produce the unshifted comb starting at $x = 0$",
                            "Because the transform turns the shift into a phase on each peak, and the Born rule discards phases",
                            "Because the shift is always a multiple of $r$, so the comb is unchanged by it",
                            "Because the continued-fraction step subtracts the shift before reducing the fraction",
                        ],
                        "a": 1,
                        "whys": [
                            r"Each distinct value of $f$ gives a differently shifted comb; measuring $3$ instead of $1$ for $3^x \bmod 8$ gives teeth at $1, 3, 5, 7$. The shift is random, and the algorithm has to be indifferent to it.",
                            r"Shifting the input by $s$ multiplies output $k$ by $e^{2\pi i\, sk/N}$; the peak positions do not move and the probabilities are unchanged.",
                            r"The shift is between $0$ and $r - 1$, never a multiple of $r$ unless it is $0$. A shift of $1$ moves every tooth, so the comb is a different vector; what stays the same is its spacing.",
                            r"The continued fraction sees only $k$ and $N$; it has no way to know $s$ and never needs to, because $s$ is already gone from the probabilities by the time $k$ is measured.",
                        ],
                        "why": r"""
The Fourier shift theorem: delaying the input by $s$ multiplies the transform at
frequency $k$ by $e^{2\pi i\, sk/N}$. That is a phase of modulus $1$, so the peak
probabilities $|{\text{out}_k}|^2$ are identical for every shift and the peaks sit at
multiples of $N/r$ regardless. Measurement of the second register produced the shift
and destroyed nothing that matters; the spacing survived as peak position.
""",
                    },
                    {
                        "q": "A comb with teeth at $j = 0, 2, 4, 6$ on eight amplitudes is transformed. Why is the output at $k = 2$ zero?",
                        "opts": [
                            "Because $k = 2$ is not a multiple of the period $2$, so the definition assigns it no weight at all",
                            "Because the phases $e^{2\\pi i\\, jk/8}$ at the four teeth are $1, -1, 1, -1$ and cancel exactly",
                            "Because the transform of a real comb is real, and only even $k$ can carry real amplitude",
                            "Because the comb has four teeth and $k = 2$ is below the first harmonic at $k = 4$",
                        ],
                        "a": 1,
                        "whys": [
                            r"Peaks sit at multiples of $N/r = 4$, not of $r = 2$; and $k = 2$ is a multiple of $2$ anyway. The definition assigns weight by summing phases, and at $k = 2$ that sum is zero, which is the actual reason.",
                            r"$e^{2\pi i\, jk/8}$ with $k = 2$ is $e^{i\pi j/2}$; at $j = 0, 2, 4, 6$ that is $1, -1, 1, -1$, summing to $0$.",
                            r"The transform of a real vector is not real in general, and $k = 2$ is even. Reality has nothing to do with it; the four terms at $k = 2$ are real and they sum to zero.",
                            r"Harmonics of a period-$2$ comb sit at multiples of $N/r = 4$, and $k = 2$ is not one; but the reason it is zero is the geometric-series cancellation, not a rule about being 'below' something.",
                        ],
                        "why": r"""
At $k = 2$ the phases at the teeth are $e^{2\pi i \cdot 0}, e^{2\pi i \cdot 4/8},
e^{2\pi i \cdot 8/8}, e^{2\pi i \cdot 12/8}$, which are $1, -1, 1, -1$; the four equal
amplitudes cancel to nothing. At $k = 4$ the phases are all $1$ and the teeth add to
$0.7071$. The general statement is that the sum $\sum_m e^{2\pi i\, mrk/N}$ is $M$
when $rk/N$ is an integer and $0$ otherwise, which places peaks at multiples of $N/r$.
""",
                    },
                    {
                        "q": "`best_rational` is required to work in integers. What goes wrong with `float` arithmetic on a fraction like $k/N = 21/32$?",
                        "opts": [
                            "Floats cannot represent $21/32$ exactly, so the expansion starts from a slightly wrong number and drifts from there",
                            "After a few inversions the remainder is a rounding residue rather than zero, so the expansion never stops",
                            "Float division is too slow for the number of steps the expansion needs",
                            "Floats lose the sign of the remainder, so the convergents alternate incorrectly",
                        ],
                        "a": 1,
                        "whys": [
                            r"$21/32$ is a dyadic rational and is represented exactly in binary floating point. The trouble is not the starting number but what happens to the remainders after repeated subtraction and inversion.",
                            r"With integers the remainder reaches exactly $0$ and the loop stops; with floats it reaches $10^{-16}$, is inverted to $10^{16}$, and manufactures a false term.",
                            r"The expansion takes at most a few dozen steps for any realistic $N$; speed is not the issue. Correctness is: a float remainder never becomes exactly zero.",
                            r"Remainders in the expansion are non-negative by construction, and the convergents do alternate above and below the target as a matter of course. Sign is not where floats fail here.",
                        ],
                        "why": r"""
The expansion ends when a remainder is exactly zero. In integer arithmetic that
happens; in floating point the remainder becomes something like $2 \times 10^{-16}$,
inverting it gives an enormous partial quotient, and the algorithm either returns an
absurd convergent or, if it is bounded by `qmax`, stops one step late with the wrong
answer. The lab's `best_rational` keeps a `(num, den)` remainder pair and inverts it
by swapping, so every quantity stays an integer and the termination test is exact.
""",
                    },
                    {
                        "q": "For $7^x \\bmod 15$ on four qubits the peaks are at $k = 4, 8, 12$. Taking only $k = 8$ gives $8/16 = 1/2$. What does the lcm across all peaks fix?",
                        "opts": [
                            "It averages the three estimates to reduce the sampling error on the period",
                            "It recovers the full period $4$ from peaks whose reduced fractions gave only a divisor of it",
                            "It removes the $k = 0$ peak, which would otherwise make the estimated period appear to be exactly $1$",
                            "It converts the peak spacing $N/r$ back into $r$ by taking the lcm with $N$",
                        ],
                        "a": 1,
                        "whys": [
                            r"There is no averaging in a least common multiple, and the individual estimates are not noisy; they are exact divisors of $r$. Combining divisors is a number-theoretic step, not a statistical one.",
                            r"$8/16$ reduces to $1/2$ because $c = 2$ shares a factor with $r = 4$; the peaks at $4$ and $12$ give $1/4$ and $3/4$, and $\mathrm{lcm}(4, 2, 4) = 4$.",
                            r"The $k = 0$ peak is excluded before any fraction is taken, by starting the scan at $k = 1$, and it would contribute a denominator of $1$ anyway, which changes no lcm. The lcm is fixing the peaks that *were* used.",
                            r"The spacing is already turned into $r$ by reducing $k/N$; that is what the continued fraction does. The lcm combines several such denominators with *each other*, never with $N$.",
                        ],
                        "why": r"""
A peak at $k = cN/r$ reduces to $c/r$ in lowest terms, and when $c$ and $r$ share a
factor the denominator that comes back is $r$ divided by that factor. For $r = 4$ the
peak with $c = 2$ says $2$; the ones with $c = 1$ and $c = 3$ say $4$. The lcm of
what every peak says is $r$ itself, provided at least one peak had $c$ coprime to $r$.
That is why the lab scans every peak above the threshold rather than the tallest one.
""",
                    },
                    {
                        "q": "A student's `qft_circuit` passes the comparison test on one qubit and fails on two and three. What is the likely cause?",
                        "opts": [
                            "The controlled-phase angles are off by a factor of two, which happens to make no difference at all on a single qubit",
                            "The final swaps that reverse the qubit order are missing, and on one qubit there is nothing to reverse",
                            "The Hadamards are applied after the controlled phases instead of before them",
                            "The circuit uses `apply_cnot` where a controlled phase is needed, which coincides on one qubit",
                        ],
                        "a": 1,
                        "whys": [
                            r"Wrong angles would corrupt the two-qubit result but there are *no* controlled phases on one qubit, so the one-qubit pass tells you nothing about angles. The brief's warning and the lab's error message both point at the swaps first.",
                            r"The product form comes out in reversed bit order; the swaps fix it, and a single qubit is its own reversal.",
                            r"Reordering H and the phases changes the transform on two qubits and would also fail there, but it is not the usual mistake, and the one-qubit case, with only an H, cannot distinguish orderings either.",
                            r"There are no two-qubit gates at all on one qubit, so nothing coincides. On two qubits a CNOT is a permutation while a controlled phase is diagonal; substituting one for the other breaks the result outright.",
                        ],
                        "why": r"""
The product form of the transform delivers the output qubits in reverse order, so the
circuit ends with a swap of qubit $i$ and $n - 1 - i$ for each $i < n/2$. On one qubit
$n/2$ is $0$ and there are no swaps to forget, so the missing step is invisible there
and shows up as a bit-reversed amplitude list on two and three. The lab's test runs on
one, two and three qubits for that reason, and its failure message names the swaps.
""",
                    },
                ],
            },
            "lab": {
                "title": "QFT on three qubits, and finding a period",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
**`qft(state)`** — the transform written straight from the definition:

```text
out[k] = (1/sqrt(N)) * sum over j of state[j] * exp(2*pi*i*j*k/N)
```

**`iqft(state)`** — the inverse, with the sign of the exponent flipped.

**`qft_circuit(state)`** — the same map built from gates in `qlib`. For each
qubit `i` from 0 to n-1: apply `H` to qubit `i`, then for every `j > i` apply a
controlled phase of `2*pi / 2**(j - i + 1)` with control `j` and target `i`.
Finish by swapping qubit `i` with qubit `n-1-i` for `i < n//2`. Get the bit
reversal wrong and the amplitudes come out permuted — the tests will say so.

**`best_rational(num, den, qmax)`** — the continued-fraction convergent `(p, q)`
of `num/den` with the largest `q <= qmax`. Use **integer** arithmetic; floating
point derails the expansion. `den <= 0` or `qmax < 1` is a `ValueError`.

```text
best_rational(3, 8, 7)   ->  (1, 3)
best_rational(21, 32, 10) ->  (2, 3)
```

**`periodic_branches(f, n)`** — the state `sum over x of |x>|f(x)>` after the
second register has been measured, one branch per distinct value of `f`. Returns
`{value: normalised n-qubit state over the x with f(x) == value}`, and the
branches come back in sorted key order.

**`estimate_period(f, n, qmax)`** — take the lowest-keyed branch, `qft` it, and
collect every non-zero index `k` whose probability is at least 40% of the largest.
Turn each into a denominator with `best_rational(k, N, qmax)` and return the lcm
of them. A flat spectrum means period 1.

```text
estimate_period(lambda x: pow(3, x, 8), 3, 8)   ->  2
estimate_period(lambda x: pow(7, x, 15), 4, 15) ->  4
estimate_period(lambda x: pow(5, x, 21), 6, 21) ->  6
```

The lcm step matters: with a period that does not divide `2**n` a single peak
only gives a divisor of `r`.
''',
                "files": [
                    {"name": "qlib.py", "content": QLIB, "ro": True},
                    {"name": "main.py", "content": r'''
import cmath
import math
from math import gcd

from qlib import apply_1q, apply_cphase, apply_swap, n_qubits, probabilities, H


def qft(state):
    """The quantum Fourier transform, straight from the definition."""
    # your code here


def iqft(state):
    """The inverse transform."""
    # your code here


def qft_circuit(state):
    """The same transform built from H, controlled phases and swaps."""
    # your code here


def best_rational(num, den, qmax):
    """(p, q): the best continued-fraction convergent with q <= qmax."""
    # your code here


def periodic_branches(f, n):
    """{value: normalised state over the x with f(x) == value}."""
    # your code here


def estimate_period(f, n, qmax):
    """The period of f, read off the QFT peaks."""
    # your code here


print("period of 3^x mod 8: ", estimate_period(lambda x: pow(3, x, 8), 3, 8))
print("period of 7^x mod 15:", estimate_period(lambda x: pow(7, x, 15), 4, 15))
'''},
                ],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import cmath
import math
from math import gcd

from qlib import apply_1q, apply_cphase, apply_swap, n_qubits, probabilities, H


def qft(state):
    """The quantum Fourier transform, straight from the definition."""
    n_qubits(state)                       # rejects a length that is not 2**n
    size = len(state)
    root = 2j * math.pi / size
    out = []
    for k in range(size):
        acc = 0j
        for j, amp in enumerate(state):
            acc += amp * cmath.exp(root * j * k)
        out.append(acc / math.sqrt(size))
    return out


def iqft(state):
    """The inverse transform."""
    n_qubits(state)
    size = len(state)
    root = -2j * math.pi / size
    out = []
    for k in range(size):
        acc = 0j
        for j, amp in enumerate(state):
            acc += amp * cmath.exp(root * j * k)
        out.append(acc / math.sqrt(size))
    return out


def qft_circuit(state):
    """The same transform built from H, controlled phases and swaps."""
    n = n_qubits(state)
    out = list(state)
    for i in range(n):
        out = apply_1q(out, H, i)
        for j in range(i + 1, n):
            # Angle halves with distance: 2*pi / 2**(j - i + 1).
            out = apply_cphase(out, j, i, 2 * math.pi / (2 ** (j - i + 1)))
    for i in range(n // 2):
        out = apply_swap(out, i, n - 1 - i)
    return out


def best_rational(num, den, qmax):
    """(p, q): the best continued-fraction convergent with q <= qmax."""
    if den <= 0:
        raise ValueError("denominator must be positive")
    if qmax < 1:
        raise ValueError("qmax must be at least 1")
    a = num // den
    p_prev, q_prev = 1, 0
    p, q = a, 1
    r_num, r_den = num - a * den, den
    while r_num != 0:
        r_num, r_den = r_den, r_num       # invert the remainder fraction
        a = r_num // r_den
        p_new, q_new = a * p + p_prev, a * q + q_prev
        if q_new > qmax:
            break
        p_prev, q_prev = p, q
        p, q = p_new, q_new
        r_num = r_num - a * r_den
    return (int(p), int(q))


def periodic_branches(f, n):
    """{value: normalised state over the x with f(x) == value}."""
    if n < 1:
        raise ValueError("need at least one qubit")
    size = 2 ** n
    groups = {}
    for x in range(size):
        groups.setdefault(f(x), []).append(x)
    branches = {}
    for value in sorted(groups):
        xs = groups[value]
        amp = 1 / math.sqrt(len(xs))
        vec = [0j] * size
        for x in xs:
            vec[x] = complex(amp)
        branches[value] = vec
    return branches


def estimate_period(f, n, qmax):
    """The period of f, read off the QFT peaks."""
    size = 2 ** n
    branches = periodic_branches(f, n)
    first = sorted(branches)[0]
    probs = probabilities(qft(branches[first]))
    peak = max(probs[1:], default=0.0)
    if peak < 1e-12:
        return 1                          # all weight at k = 0: nothing repeats
    period = 1
    for k in range(1, size):
        if probs[k] >= 0.4 * peak:
            _, q = best_rational(k, size, qmax)
            if q >= 1:
                period = period * q // gcd(period, q)
    return period


print("period of 3^x mod 8: ", estimate_period(lambda x: pow(3, x, 8), 3, 8))
print("period of 7^x mod 15:", estimate_period(lambda x: pow(7, x, 15), 4, 15))
'''}],
                "hints": [
                    "`cmath.exp(2j * math.pi * j * k / N)` is the root of unity; divide the whole sum by `math.sqrt(N)` once.",
                    "In `qft_circuit` the control is the *later* qubit and the target the earlier one; the final swaps reverse the register.",
                    "Do the continued fraction on integers: keep `(num, den)` as a remainder pair and invert it each round rather than dividing into a float.",
                    "`period * q // gcd(period, q)` accumulates a least common multiple as you walk the peaks.",
                ],
                "tests": [
                    {"name": "qft matches the analytic answers", "code": r'''
_u = qft([1 + 0j] + [0j] * 7)
assert all(abs(a - 1 / math.sqrt(8)) < 1e-12 for a in _u), \
    f"qft of |000> is the uniform state; got {_u!r}"
_flat = [1 / math.sqrt(8) + 0j] * 8
_back = qft(_flat)
assert abs(_back[0] - 1) < 1e-12 and all(abs(a) < 1e-12 for a in _back[1:]), \
    f"qft of the uniform state is |000>; got {_back!r}"
_alt = [(1 if j % 2 == 0 else -1) / math.sqrt(8) + 0j for j in range(8)]
_sp = qft(_alt)
assert abs(abs(_sp[4]) - 1) < 1e-12, f"An alternating comb transforms to |100>; got {_sp!r}"
'''},
                    {"name": "qft is unitary and iqft undoes it", "code": r'''
import random as _random
_rng = _random.Random(7)
for _n in (1, 2, 3):
    _size = 2 ** _n
    _v = [complex(_rng.gauss(0, 1), _rng.gauss(0, 1)) for _ in range(_size)]
    _nrm = math.sqrt(sum(abs(a) ** 2 for a in _v))
    _v = [a / _nrm for a in _v]
    _t = qft(_v)
    assert abs(sum(abs(a) ** 2 for a in _t) - 1.0) < 1e-9, "The QFT preserves the norm"
    _r = iqft(_t)
    _err = max(abs(x - y) for x, y in zip(_v, _r))
    assert _err < 1e-9, f"iqft(qft(v)) drifted from v by {_err!r}"
try:
    qft([1 + 0j, 0j, 0j])
    assert False, "A length that is not a power of two should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The gate circuit reproduces the transform", "code": r'''
import random as _random
_rng = _random.Random(11)
for _n in (1, 2, 3):
    _size = 2 ** _n
    for _trial in range(3):
        _v = [complex(_rng.gauss(0, 1), _rng.gauss(0, 1)) for _ in range(_size)]
        _nrm = math.sqrt(sum(abs(a) ** 2 for a in _v))
        _v = [a / _nrm for a in _v]
        _a = qft(_v)
        _b = qft_circuit(_v)
        _err = max(abs(x - y) for x, y in zip(_a, _b))
        assert _err < 1e-9, \
            f"qft_circuit differs from qft by {_err!r} on {_n} qubits — check the final swaps"
'''},
                    {"name": "best_rational finds the convergent", "code": r'''
for _args, _want in [((3, 8, 7), (1, 3)), ((5, 8, 7), (2, 3)), ((1, 2, 10), (1, 2)),
                     ((1, 4, 10), (1, 4)), ((5, 32, 10), (1, 6)), ((11, 32, 10), (1, 3)),
                     ((21, 32, 10), (2, 3)), ((27, 32, 10), (5, 6)), ((0, 8, 5), (0, 1))]:
    _got = best_rational(*_args)
    assert _got == _want, f"best_rational{_args!r} gave {_got!r}, expected {_want!r}"
assert best_rational(3, 8, 1) == (0, 1), "With qmax = 1 only the integer part survives"
for _bad in [(1, 0, 5), (1, -8, 5), (1, 8, 0)]:
    try:
        best_rational(*_bad)
        assert False, f"best_rational{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "periodic_branches splits the register", "code": r'''
_b = periodic_branches(lambda x: x % 2, 3)
assert sorted(_b) == [0, 1], f"f(x) = x % 2 has two branches; got {sorted(_b)!r}"
_even = _b[0]
assert all(abs(_even[x] - 0.5) < 1e-12 for x in (0, 2, 4, 6)), \
    f"Four even x each carry amplitude 0.5; got {_even!r}"
assert all(abs(_even[x]) < 1e-12 for x in (1, 3, 5, 7)), "Odd x are absent from that branch"
assert abs(sum(abs(a) ** 2 for a in _even) - 1.0) < 1e-12, "Each branch is normalised"
_one = periodic_branches(lambda x: 0, 3)
assert list(_one) == [0] and abs(_one[0][5] - 1 / math.sqrt(8)) < 1e-12, \
    "A constant f gives one uniform branch"
try:
    periodic_branches(lambda x: x, 0)
    assert False, "periodic_branches with n = 0 should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "estimate_period recovers modular orders", "code": r'''
for _a, _m, _n, _want in [(3, 8, 3, 2), (7, 15, 4, 4), (4, 15, 4, 2), (8, 15, 4, 4),
                          (2, 7, 5, 3), (3, 7, 5, 6), (2, 5, 5, 4), (5, 21, 6, 6)]:
    _f = (lambda a, m: (lambda x: pow(a, x, m)))(_a, _m)
    _got = estimate_period(_f, _n, _m)
    assert _got == _want, \
        f"estimate_period for {_a}^x mod {_m} on {_n} qubits gave {_got}, expected {_want}"
'''},
                    {"name": "Degenerate periods", "code": r'''
assert estimate_period(lambda x: 0, 3, 8) == 1, "A constant function has period 1"
assert estimate_period(lambda x: x % 2, 3, 8) == 2, "x % 2 has period 2"
assert estimate_period(lambda x: x % 4, 4, 16) == 4, "x % 4 has period 4"
assert estimate_period(lambda x: x % 8, 3, 8) == 8, \
    "A function that only repeats after the whole window reports the window length"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a state-vector simulator with an algorithm library",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
Everything above, rebuilt as one coherent library. `qsim.py` holds the engine
and is what the checks import; `main.py` is a demo that drives it. No helper
module is provided this time — the whole thing is yours.

## `Circuit(n)`

A builder. `n < 1` is a `ValueError`. Every gate method **returns `self`** so
calls chain, appends to `self.ops`, and validates its qubit indices immediately:
an index outside `0 .. n-1`, or a two-qubit gate whose control equals its
target, raises `ValueError` at build time rather than at run time.

- single qubit: `.h(q) .x(q) .y(q) .z(q) .s(q) .t(q) .ry(theta, q) .phase(angle, q)`
- two qubit: `.cnot(c, t) .cz(c, t) .cphase(angle, c, t) .swap(a, b)`

## Running

- `.run(initial=None)` — the final amplitudes as a list of complex numbers,
  starting from `|0...0>` unless an initial state is supplied. Calling it twice
  gives the same answer: `run` must not consume or mutate anything.
- `.probabilities(initial=None)` — the Born-rule distribution.
- `.sample(shots, seed=7, initial=None)` — `{index: count}` from seeded
  measurements.

## Module-level algorithms

- `qft(state)` and `iqft(state)` — the transform and its inverse.
- `deutsch_jozsa(f, n)` — `"constant"` or `"balanced"` from one oracle call.
- `optimal_iterations(n, marked_count=1)` and `grover(n, marked, iterations=None)`
  returning the amplified state, plus `grover_search(n, marked)` returning the
  most likely index.

## Conventions, restated

Qubit 0 is the most significant bit of the basis index. States are lists of
`complex`. Nothing mutates its input. `qsim.py` prints nothing when imported.

## Suggested order

Index helpers and `apply_1q` first, then the two-qubit gates, then `Circuit`,
then measurement, then the three algorithms. The checks are ordered the same way.
''',
        "deliverables": [
            "`qsim.py` — the simulator and algorithm library, importable with no side effects",
            "`main.py` — a demo that builds a Bell pair, samples it, and runs all three algorithms",
            "A fluent `Circuit` builder whose gate methods validate indices at build time",
            "Sparse gate application over the tensor index structure, never a dense 2^n x 2^n matrix",
            "Seeded measurement whose statistics match the analytic amplitudes",
            "Deutsch-Jozsa, Grover and the QFT, each checked against amplitudes derived by hand",
        ],
        "constraints": [
            "Standard library only: `math`, `cmath` and `random` are all you need",
            "No dense operator matrices — a gate touches 2^n amplitudes, not 4^n",
            "Every method returns new data or `self`; no function mutates a state passed to it",
            "`qsim.py` defines names only, and prints nothing when imported",
            "Every random draw goes through a `random.Random(seed)` you create, so runs repeat exactly",
        ],
        "rubric": [
            {"criterion": "Correctness of the engine", "weight": 35,
             "evidence": "Gate application, two-qubit permutations and measurement all match the analytic amplitudes, including the one-qubit and empty-circuit edge cases."},
            {"criterion": "Algorithms", "weight": 30,
             "evidence": "Deutsch-Jozsa answers in one query; Grover reaches the predicted probability at the predicted iteration count; QFT agrees with the discrete Fourier transform."},
            {"criterion": "Validation and error handling", "weight": 15,
             "evidence": "Bad qubit indices, coincident control and target, empty or out-of-range marked sets, and malformed state lengths all raise ValueError."},
            {"criterion": "Design", "weight": 12,
             "evidence": "A fluent builder over a single index-pair primitive; no duplicated gate loops and no dense matrices."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "Docstrings on every public method, the index convention stated once and honoured everywhere, no debug prints left behind."},
        ],
        "hints": [
            "Write one private helper that pairs indices differing in a single bit; every one-qubit gate is that helper plus a 2x2 multiply.",
            "Store ops as tuples like `(\"1q\", matrix, target)` and `(\"cnot\", control, target)` so `run` is a short dispatch, and validate the indices when they are appended.",
            "`cz` is `cphase` with angle pi, and `swap` is three CNOTs — but a direct index exchange is clearer and faster.",
            "For Deutsch-Jozsa the ancilla is the least significant qubit: the input register reads all zeros exactly at basis indices 0 and 1.",
            "Grover's uniform start is `[1 / math.sqrt(N)] * N`; the oracle negates the marked amplitudes and diffusion reflects everything about the mean.",
        ],
        "files": [
            {"name": "qsim.py", "content": r'''
"""qsim.py — a state-vector simulator and a small algorithm library.

Convention: an n-qubit state is a list of 2**n complex amplitudes, and qubit 0
is the MOST significant bit of the basis index.
"""

import cmath
import math
import random

SQRT2 = math.sqrt(2)

I = [[1 + 0j, 0j], [0j, 1 + 0j]]
X = None
Y = None
Z = None
H = None
S = None
T = None


def phase_gate(angle):
    """diag(1, exp(i*angle))."""
    # your code here


def ry_gate(theta):
    """Rotation by theta about the Bloch y axis."""
    # your code here


def n_qubits(state):
    """Qubit count for a state vector; ValueError if the length is not 2**n."""
    # your code here


def zero_state(n):
    """The register |00...0>."""
    # your code here


def probabilities(state):
    """Born-rule probabilities after normalising."""
    # your code here


class Circuit:
    """A fluent builder for a fixed-width register."""

    def __init__(self, n):
        # your code here
        pass

    def h(self, q):
        # your code here
        pass

    def x(self, q):
        pass

    def y(self, q):
        pass

    def z(self, q):
        pass

    def s(self, q):
        pass

    def t(self, q):
        pass

    def ry(self, theta, q):
        pass

    def phase(self, angle, q):
        pass

    def cnot(self, control, target):
        pass

    def cz(self, control, target):
        pass

    def cphase(self, angle, control, target):
        pass

    def swap(self, a, b):
        pass

    def run(self, initial=None):
        """Final amplitudes; repeatable, and it does not mutate the circuit."""
        # your code here

    def probabilities(self, initial=None):
        """The Born-rule distribution of the final state."""
        # your code here

    def sample(self, shots, seed=7, initial=None):
        """{basis index: count} from seeded measurements."""
        # your code here


def qft(state):
    """The quantum Fourier transform."""
    # your code here


def iqft(state):
    """The inverse quantum Fourier transform."""
    # your code here


def deutsch_jozsa(f, n):
    """Return "constant" or "balanced" from a single oracle call."""
    # your code here


def optimal_iterations(n, marked_count=1):
    """floor(pi/4 * sqrt(N / M))."""
    # your code here


def grover(n, marked, iterations=None):
    """The state after the Grover iterations."""
    # your code here


def grover_search(n, marked):
    """The most likely index after the optimal number of iterations."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
import math

import qsim

bell = qsim.Circuit(2).h(0).cnot(0, 1)
print("Bell amplitudes:", bell.run())
print("Bell counts:    ", bell.sample(2000, seed=7))

print("Deutsch-Jozsa:  ", qsim.deutsch_jozsa(lambda x: bin(x).count("1") % 2, 3))
print("Grover finds:   ", qsim.grover_search(4, [11]))
print("QFT of |000>:   ", qsim.qft(qsim.zero_state(3)))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "qsim.py", "content": r'''
"""qsim.py — a state-vector simulator and a small algorithm library.

Convention: an n-qubit state is a list of 2**n complex amplitudes, and qubit 0
is the MOST significant bit of the basis index.
"""

import cmath
import math
import random

SQRT2 = math.sqrt(2)

I = [[1 + 0j, 0j], [0j, 1 + 0j]]
X = [[0j, 1 + 0j], [1 + 0j, 0j]]
Y = [[0j, -1j], [1j, 0j]]
Z = [[1 + 0j, 0j], [0j, -1 + 0j]]
H = [[1 / SQRT2 + 0j, 1 / SQRT2 + 0j], [1 / SQRT2 + 0j, -1 / SQRT2 + 0j]]
S = [[1 + 0j, 0j], [0j, 1j]]
T = [[1 + 0j, 0j], [0j, cmath.exp(1j * math.pi / 4)]]


def phase_gate(angle):
    """diag(1, exp(i*angle))."""
    return [[1 + 0j, 0j], [0j, cmath.exp(1j * angle)]]


def ry_gate(theta):
    """Rotation by theta about the Bloch y axis."""
    c = math.cos(theta / 2)
    s = math.sin(theta / 2)
    return [[c + 0j, -s + 0j], [s + 0j, c + 0j]]


def n_qubits(state):
    """Qubit count for a state vector; ValueError if the length is not 2**n."""
    size = len(state)
    if size < 2:
        raise ValueError("a register needs at least two amplitudes")
    n = size.bit_length() - 1
    if 2 ** n != size:
        raise ValueError(f"state length {size} is not a power of two")
    return n


def zero_state(n):
    """The register |00...0>."""
    if n < 1:
        raise ValueError("need at least one qubit")
    state = [0j] * (2 ** n)
    state[0] = 1 + 0j
    return state


def probabilities(state):
    """Born-rule probabilities after normalising."""
    norm = math.sqrt(sum(abs(a) ** 2 for a in state))
    if norm == 0:
        raise ValueError("the zero vector is not a state")
    return [abs(a / norm) ** 2 for a in state]


def _apply_1q(state, gate, target, n):
    """Mix every index pair that differs only in the target bit."""
    shift = n - 1 - target
    out = list(state)
    for k in range(len(state)):
        if (k >> shift) & 1:
            continue
        k1 = k | (1 << shift)
        a, b = state[k], state[k1]
        out[k] = gate[0][0] * a + gate[0][1] * b
        out[k1] = gate[1][0] * a + gate[1][1] * b
    return out


def _apply_cnot(state, control, target, n):
    cs = n - 1 - control
    ts = n - 1 - target
    out = list(state)
    for k in range(len(state)):
        if ((k >> cs) & 1) and not ((k >> ts) & 1):
            k1 = k | (1 << ts)
            out[k], out[k1] = state[k1], state[k]
    return out


def _apply_cphase(state, angle, control, target, n):
    cs = n - 1 - control
    ts = n - 1 - target
    factor = cmath.exp(1j * angle)
    out = list(state)
    for k in range(len(state)):
        if ((k >> cs) & 1) and ((k >> ts) & 1):
            out[k] = state[k] * factor
    return out


def _apply_swap(state, a, b, n):
    if a == b:
        return list(state)
    sa = n - 1 - a
    sb = n - 1 - b
    out = list(state)
    for k in range(len(state)):
        if ((k >> sa) & 1) != ((k >> sb) & 1):
            out[k ^ (1 << sa) ^ (1 << sb)] = state[k]
    return out


class Circuit:
    """A fluent builder for a fixed-width register."""

    def __init__(self, n):
        if n < 1:
            raise ValueError("a circuit needs at least one qubit")
        self.n = n
        self.ops = []

    # -- validation -------------------------------------------------------
    def _check(self, *qubits):
        for q in qubits:
            if not isinstance(q, int) or isinstance(q, bool):
                raise ValueError(f"qubit index {q!r} is not an integer")
            if not 0 <= q < self.n:
                raise ValueError(f"qubit {q} out of range for {self.n} qubits")
        if len(qubits) == 2 and qubits[0] == qubits[1]:
            raise ValueError("a two-qubit gate needs two distinct qubits")

    def _gate(self, matrix, q):
        self._check(q)
        self.ops.append(("1q", matrix, q))
        return self

    # -- single-qubit gates ----------------------------------------------
    def h(self, q):
        """Hadamard on qubit q."""
        return self._gate(H, q)

    def x(self, q):
        """Pauli X on qubit q."""
        return self._gate(X, q)

    def y(self, q):
        """Pauli Y on qubit q."""
        return self._gate(Y, q)

    def z(self, q):
        """Pauli Z on qubit q."""
        return self._gate(Z, q)

    def s(self, q):
        """Phase gate S on qubit q."""
        return self._gate(S, q)

    def t(self, q):
        """Phase gate T on qubit q."""
        return self._gate(T, q)

    def ry(self, theta, q):
        """Rotation about y by theta on qubit q."""
        return self._gate(ry_gate(theta), q)

    def phase(self, angle, q):
        """Diagonal phase on qubit q."""
        return self._gate(phase_gate(angle), q)

    # -- two-qubit gates --------------------------------------------------
    def cnot(self, control, target):
        """Controlled NOT."""
        self._check(control, target)
        self.ops.append(("cnot", control, target))
        return self

    def cz(self, control, target):
        """Controlled Z, which is a controlled phase of pi."""
        return self.cphase(math.pi, control, target)

    def cphase(self, angle, control, target):
        """Controlled phase rotation."""
        self._check(control, target)
        self.ops.append(("cphase", angle, control, target))
        return self

    def swap(self, a, b):
        """Exchange two qubits."""
        self._check(a, b)
        self.ops.append(("swap", a, b))
        return self

    # -- execution --------------------------------------------------------
    def run(self, initial=None):
        """Final amplitudes; repeatable, and it does not mutate the circuit."""
        if initial is None:
            state = zero_state(self.n)
        else:
            if len(initial) != 2 ** self.n:
                raise ValueError(f"initial state must have {2 ** self.n} amplitudes")
            state = [complex(a) for a in initial]
        for op in self.ops:
            kind = op[0]
            if kind == "1q":
                state = _apply_1q(state, op[1], op[2], self.n)
            elif kind == "cnot":
                state = _apply_cnot(state, op[1], op[2], self.n)
            elif kind == "cphase":
                state = _apply_cphase(state, op[1], op[2], op[3], self.n)
            elif kind == "swap":
                state = _apply_swap(state, op[1], op[2], self.n)
            else:
                raise ValueError(f"unknown op {kind!r}")
        return state

    def probabilities(self, initial=None):
        """The Born-rule distribution of the final state."""
        return probabilities(self.run(initial))

    def sample(self, shots, seed=7, initial=None):
        """{basis index: count} from seeded measurements."""
        if shots < 0:
            raise ValueError("shots cannot be negative")
        probs = self.probabilities(initial)
        rng = random.Random(seed)
        counts = {}
        for _ in range(shots):
            u = rng.random()
            acc = 0.0
            chosen = len(probs) - 1
            for k, p in enumerate(probs):
                acc += p
                if u < acc:
                    chosen = k
                    break
            counts[chosen] = counts.get(chosen, 0) + 1
        return counts


# ---------------------------------------------------------------- transforms
def _dft(state, sign):
    n_qubits(state)
    size = len(state)
    root = sign * 2j * math.pi / size
    out = []
    for k in range(size):
        acc = 0j
        for j, amp in enumerate(state):
            acc += amp * cmath.exp(root * j * k)
        out.append(acc / math.sqrt(size))
    return out


def qft(state):
    """The quantum Fourier transform."""
    return _dft(state, 1)


def iqft(state):
    """The inverse quantum Fourier transform."""
    return _dft(state, -1)


# ---------------------------------------------------------------- algorithms
def deutsch_jozsa(f, n):
    """Return "constant" or "balanced" from a single oracle call."""
    if n < 1:
        raise ValueError("need at least one input qubit")
    total = n + 1
    state = zero_state(total)
    state = _apply_1q(state, X, n, total)          # ancilla to |1>
    for q in range(total):
        state = _apply_1q(state, H, q, total)      # inputs uniform, ancilla |->
    # The single query: |x>|y> -> |x>|y xor f(x)>.
    queried = list(state)
    for k in range(len(state)):
        if f(k >> 1) & 1:
            queried[k ^ 1] = state[k]
    state = queried
    for q in range(n):
        state = _apply_1q(state, H, q, total)
    probs = probabilities(state)
    p_zero = probs[0] + probs[1]                   # input register all zeros
    return "constant" if p_zero > 0.5 else "balanced"


def optimal_iterations(n, marked_count=1):
    """floor(pi/4 * sqrt(N / M))."""
    if n < 1 or marked_count < 1 or marked_count > 2 ** n:
        raise ValueError("bad register size or marked count")
    return int(math.floor(math.pi / 4 * math.sqrt(2 ** n / marked_count)))


def grover(n, marked, iterations=None):
    """The state after the Grover iterations."""
    if n < 1:
        raise ValueError("need at least one qubit")
    size = 2 ** n
    marked = list(marked)
    if not marked:
        raise ValueError("Grover needs at least one marked index")
    if len(set(marked)) != len(marked):
        raise ValueError("marked indices must be distinct")
    for m in marked:
        if not 0 <= m < size:
            raise ValueError(f"marked index {m} out of range for {n} qubits")
    if iterations is None:
        iterations = optimal_iterations(n, len(marked))
    if iterations < 0:
        raise ValueError("iteration count cannot be negative")
    state = [complex(1 / math.sqrt(size)) for _ in range(size)]
    for _ in range(iterations):
        for m in marked:
            state[m] = -state[m]                   # phase oracle
        mean = sum(state) / size
        state = [2 * mean - a for a in state]      # inversion about the mean
    return state


def grover_search(n, marked):
    """The most likely index after the optimal number of iterations."""
    probs = probabilities(grover(n, marked))
    best = 0
    for k, p in enumerate(probs):
        if p > probs[best]:
            best = k
    return best
'''},
            {"name": "main.py", "content": r'''
import math

import qsim

bell = qsim.Circuit(2).h(0).cnot(0, 1)
print("Bell amplitudes:", bell.run())
print("Bell counts:    ", bell.sample(2000, seed=7))

print("Deutsch-Jozsa:  ", qsim.deutsch_jozsa(lambda x: bin(x).count("1") % 2, 3))
print("Grover finds:   ", qsim.grover_search(4, [11]))
print("QFT of |000>:   ", qsim.qft(qsim.zero_state(3)))

ghz = qsim.Circuit(3).h(0).cnot(0, 1).cnot(1, 2)
print("GHZ counts:     ", ghz.sample(2000, seed=3))
'''},
        ],
        "tests": [
            {"name": "Gate constants and helpers", "code": r'''
import cmath as _cm, math as _m
from qsim import X as _X, Y as _Y, Z as _Z, H as _H, S as _S, T as _T
from qsim import phase_gate as _pg, ry_gate as _rg, n_qubits as _nq, zero_state as _zs
assert abs(_X[0][1] - 1) < 1e-12 and abs(_X[1][0] - 1) < 1e-12, f"X is {_X!r}"
assert abs(_Y[0][1] + 1j) < 1e-12 and abs(_Z[1][1] + 1) < 1e-12, "Y and Z are the Paulis"
assert abs(_H[1][1] + 0.7071067811865476) < 1e-9, f"H is {_H!r}"
assert abs(_S[1][1] - 1j) < 1e-12 and abs(_T[1][1] - _cm.exp(1j * _m.pi / 4)) < 1e-12, "S and T"
assert abs(_pg(_m.pi)[1][1] + 1) < 1e-12, "phase_gate(pi) is Z"
assert abs(_rg(_m.pi)[0][1] + 1) < 1e-12, "ry_gate(pi) maps |0> to |1>"
assert _nq([0] * 8) == 3, "Eight amplitudes is three qubits"
assert _zs(2) == [1 + 0j, 0j, 0j, 0j], f"zero_state(2) gave {_zs(2)!r}"
'''},
            {"name": "Circuit is fluent and validates at build time", "code": r'''
from qsim import Circuit as _C
_c = _C(3).h(0).x(1).cnot(0, 2)
assert isinstance(_c, _C), "Every gate method must return self so calls chain"
assert len(_c.ops) == 3, f"Three gates were added, ops holds {len(_c.ops)}"
for _call in [lambda: _C(0), lambda: _C(2).h(2), lambda: _C(2).h(-1),
              lambda: _C(2).cnot(0, 0), lambda: _C(2).cnot(0, 5),
              lambda: _C(2).cphase(1.0, 1, 1), lambda: _C(2).swap(0, 3)]:
    try:
        _call()
        assert False, "A bad qubit index should raise ValueError when the gate is added"
    except ValueError:
        pass
'''},
            {"name": "Single-qubit gates hit the right amplitudes", "code": r'''
from qsim import Circuit as _C
_r = 0.7071067811865476
_s = _C(1).h(0).run()
assert abs(_s[0] - _r) < 1e-9 and abs(_s[1] - _r) < 1e-9, f"H|0> gave {_s!r}"
assert abs(_C(1).h(0).h(0).run()[0] - 1) < 1e-9, "H twice is the identity"
_s = _C(3).x(1).run()
assert abs(_s[2] - 1) < 1e-12, f"X on qubit 1 of |000> is index 2 (qubit 0 is the MSB); got {_s!r}"
_s = _C(3).x(0).run()
assert abs(_s[4] - 1) < 1e-12, "X on qubit 0 is index 4"
_a = _C(1).x(0).t(0).t(0).run()
_b = _C(1).x(0).s(0).run()
assert abs(_a[1] - _b[1]) < 1e-12, f"T twice must equal S; got {_a!r} vs {_b!r}"
_a = _C(1).x(0).s(0).s(0).run()
assert abs(_a[1] + 1) < 1e-12, "S twice is Z"
assert abs(_C(1).run()[0] - 1) < 1e-12, "An empty circuit leaves |0>"
'''},
            {"name": "Two-qubit gates and repeatable runs", "code": r'''
from qsim import Circuit as _C
_r = 0.7071067811865476
_bell = _C(2).h(0).cnot(0, 1)
_first = _bell.run()
_second = _bell.run()
assert _first == _second, "run() must be repeatable — it may not consume the op list"
assert abs(_first[0] - _r) < 1e-9 and abs(_first[3] - _r) < 1e-9, f"Bell state is {_first!r}"
assert abs(_first[1]) < 1e-12 and abs(_first[2]) < 1e-12, "|01> and |10> vanish"
_ghz = _C(3).h(0).cnot(0, 1).cnot(1, 2).run()
assert abs(_ghz[0] - _r) < 1e-9 and abs(_ghz[7] - _r) < 1e-9, f"GHZ is {_ghz!r}"
_cz = _C(2).x(0).x(1).cz(0, 1).run()
assert abs(_cz[3] + 1) < 1e-12, f"CZ should flip the sign of |11>; got {_cz!r}"
_sw = _C(2).x(0).swap(0, 1).run()
assert abs(_sw[1] - 1) < 1e-12, f"swap should turn |10> into |01>; got {_sw!r}"
_cp = _C(2).x(0).x(1).cphase(math.pi / 2, 0, 1).run()
assert abs(_cp[3] - 1j) < 1e-12, f"cphase(pi/2) multiplies |11> by i; got {_cp!r}"
'''},
            {"name": "An initial state can be supplied", "code": r'''
from qsim import Circuit as _C
_s = _C(2).cnot(0, 1).run(initial=[0j, 0j, 1 + 0j, 0j])
assert abs(_s[3] - 1) < 1e-12, f"CNOT on |10> gives |11>; got {_s!r}"
try:
    _C(2).h(0).run(initial=[1 + 0j, 0j])
    assert False, "An initial state of the wrong width should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Sampling matches the amplitudes", "code": r'''
from qsim import Circuit as _C
_bell = _C(2).h(0).cnot(0, 1)
_p = _bell.probabilities()
assert abs(sum(_p) - 1.0) < 1e-12, f"Probabilities sum to {sum(_p)!r}"
assert abs(_p[0] - 0.5) < 1e-12 and abs(_p[3] - 0.5) < 1e-12, f"Got {_p!r}"
_c = _bell.sample(20000, seed=7)
assert sum(_c.values()) == 20000, f"Counts total {sum(_c.values())}"
assert set(_c) <= {0, 3}, f"A Bell pair never yields |01> or |10>; got {sorted(_c)!r}"
assert abs(_c.get(0, 0) / 20000 - 0.5) < 0.02, f"Outcome 0 came up {_c.get(0, 0)} times in 20000"
assert _c == _bell.sample(20000, seed=7), "The same seed must give the same counts"
assert _C(1).sample(50, seed=1) == {0: 50}, "|0> always measures as 0"
'''},
            {"name": "Deutsch-Jozsa", "code": r'''
from qsim import deutsch_jozsa as _dj
for _n in (1, 2, 3, 4):
    assert _dj(lambda x: 0, _n) == "constant", f"f = 0 on {_n} bits"
    assert _dj(lambda x: 1, _n) == "constant", f"f = 1 on {_n} bits"
    assert _dj(lambda x: bin(x).count("1") % 2, _n) == "balanced", f"parity on {_n} bits"
    assert _dj(lambda x: x & 1, _n) == "balanced", f"low bit on {_n} bits"
_seen = []
_f = lambda x: (_seen.append(x), (x >> 1) & 1)[1]
assert _dj(_f, 3) == "balanced", "Bit 1 of x is a balanced function"
try:
    _dj(lambda x: 0, 0)
    assert False, "deutsch_jozsa with n = 0 should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Grover reaches the predicted probability", "code": r'''
from qsim import grover as _g, grover_search as _gs, optimal_iterations as _oi
for _n, _want in [(2, 1), (3, 2), (4, 3), (5, 4), (6, 6), (10, 25)]:
    assert _oi(_n) == _want, f"optimal_iterations({_n}) gave {_oi(_n)}, expected {_want}"
assert _oi(4, 4) == 1, "Four of sixteen marked needs one round"
_st = _g(2, [3])
assert abs(abs(_st[3]) ** 2 - 1.0) < 1e-12, f"Two qubits is exact; p = {abs(_st[3]) ** 2!r}"
_st = _g(3, [5])
assert abs(abs(_st[5]) ** 2 - 0.9453125) < 1e-9, f"p = {abs(_st[5]) ** 2!r}, expected 0.9453125"
_st = _g(4, [1, 9])
assert abs(abs(_st[1]) ** 2 + abs(_st[9]) ** 2 - 0.9453125) < 1e-9, "Two marked of sixteen"
assert abs(abs(_g(4, [9], iterations=0)[9]) ** 2 - 0.0625) < 1e-12, "Zero rounds leaves uniform"
for _n, _m in [(2, 3), (3, 5), (4, 11), (5, 17)]:
    assert _gs(_n, [_m]) == _m, f"grover_search({_n}, [{_m}]) gave {_gs(_n, [_m])}"
'''},
            {"name": "Grover refuses impossible searches", "code": r'''
from qsim import grover as _g
for _bad in [(3, []), (3, [8]), (3, [-1]), (3, [2, 2]), (0, [0])]:
    try:
        _g(*_bad)
        assert False, f"grover{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "QFT agrees with the discrete Fourier transform", "code": r'''
import cmath as _cm, math as _m, random as _rnd
from qsim import qft as _q, iqft as _iq, zero_state as _zs
_u = _q(_zs(3))
assert all(abs(a - 1 / _m.sqrt(8)) < 1e-12 for a in _u), f"QFT of |000> is uniform; got {_u!r}"
_flat = [1 / _m.sqrt(8) + 0j] * 8
_back = _q(_flat)
assert abs(_back[0] - 1) < 1e-12 and all(abs(a) < 1e-12 for a in _back[1:]), \
    f"QFT of the uniform state is |000>; got {_back!r}"
_rng = _rnd.Random(7)
for _n in (1, 2, 3):
    _v = [complex(_rng.gauss(0, 1), _rng.gauss(0, 1)) for _ in range(2 ** _n)]
    _nrm = _m.sqrt(sum(abs(a) ** 2 for a in _v))
    _v = [a / _nrm for a in _v]
    _t = _q(_v)
    _ref = [sum(_v[j] * _cm.exp(2j * _m.pi * j * k / len(_v)) for j in range(len(_v))) / _m.sqrt(len(_v))
            for k in range(len(_v))]
    assert max(abs(x - y) for x, y in zip(_t, _ref)) < 1e-9, "QFT must match the DFT definition"
    assert max(abs(x - y) for x, y in zip(_iq(_t), _v)) < 1e-9, "iqft(qft(v)) must return v"
'''},
            {"name": "Nothing mutates its input", "code": r'''
from qsim import Circuit as _C, qft as _q, grover as _g
_init = [1 + 0j, 0j, 0j, 0j]
_C(2).h(0).cnot(0, 1).run(initial=_init)
assert _init == [1 + 0j, 0j, 0j, 0j], "run() must not write into the initial state it was given"
_v = [0.5 + 0j] * 4
_q(_v)
assert _v == [0.5 + 0j] * 4, "qft must not mutate its argument"
_marked = [1, 2]
_g(3, _marked)
assert _marked == [1, 2], "grover must not mutate the marked list it was given"
'''},
            {"name": "qsim.py is import-clean", "code": r'''
_src = open("qsim.py").read()
assert "print(" not in _src, "qsim.py is a library; the demo output belongs in main.py"
for _banned in ("numpy", "scipy", "qiskit"):
    assert _banned not in _src, f"{_banned} is not available in the browser sandbox"
assert "Bell amplitudes" in _out, "main.py should demonstrate the library it imports"
'''},
        ],
    },
}
