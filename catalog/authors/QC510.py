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
