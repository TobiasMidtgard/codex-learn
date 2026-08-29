"""DL501 — Deep Learning & Generative AI."""

ENGINE_SOURCE = r'''
import math


class Value:
    """A scalar node in a reverse-mode automatic differentiation graph."""

    def __init__(self, data, _children=(), _op=""):
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = tuple(_children)
        self._op = _op

    def __repr__(self):
        return f"Value(data={self.data:.6g}, grad={self.grad:.6g})"

    def __add__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data + other.data, (self, other), "+")

        def _backward():
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _backward
        return out

    def __mul__(self, other):
        other = other if isinstance(other, Value) else Value(other)
        out = Value(self.data * other.data, (self, other), "*")

        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad

        out._backward = _backward
        return out

    def __pow__(self, other):
        if not isinstance(other, (int, float)) or isinstance(other, bool):
            raise TypeError("only int or float exponents are supported")
        out = Value(self.data ** other, (self,), f"**{other}")

        def _backward():
            self.grad += other * self.data ** (other - 1) * out.grad

        out._backward = _backward
        return out

    def exp(self):
        out = Value(math.exp(self.data), (self,), "exp")

        def _backward():
            self.grad += out.data * out.grad

        out._backward = _backward
        return out

    def log(self):
        if self.data <= 0.0:
            raise ValueError("log is undefined for non-positive values")
        out = Value(math.log(self.data), (self,), "log")

        def _backward():
            self.grad += (1.0 / self.data) * out.grad

        out._backward = _backward
        return out

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), "tanh")

        def _backward():
            self.grad += (1.0 - t * t) * out.grad

        out._backward = _backward
        return out

    def relu(self):
        out = Value(self.data if self.data > 0.0 else 0.0, (self,), "relu")

        def _backward():
            self.grad += (1.0 if out.data > 0.0 else 0.0) * out.grad

        out._backward = _backward
        return out

    def __neg__(self):
        return self * -1.0

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        return self + (-(other if isinstance(other, Value) else Value(other)))

    def __rsub__(self, other):
        return Value(other) + (-self)

    def __rmul__(self, other):
        return self * other

    def __truediv__(self, other):
        return self * ((other if isinstance(other, Value) else Value(other)) ** -1)

    def __rtruediv__(self, other):
        return Value(other) * (self ** -1)

    def topological_order(self):
        """Every node this one depends on, children before parents."""
        order = []
        seen = set()
        stack = [(self, False)]
        while stack:
            node, expanded = stack.pop()
            if expanded:
                order.append(node)
                continue
            if id(node) in seen:
                continue
            seen.add(id(node))
            stack.append((node, True))
            for child in node._prev:
                if id(child) not in seen:
                    stack.append((child, False))
        return order

    def backward(self):
        """Seed this node with a gradient of 1 and push it back to every leaf."""
        order = self.topological_order()
        self.grad = 1.0
        for node in reversed(order):
            node._backward()
'''

COURSE = {
    "id": "DL501",
    "title": "Deep Learning & Generative AI",
    "year": 5,
    "level": "Expert",
    "prereqs": ["ML401", "MA121"],
    "stack": ["Python"],
    "credits": 15,
    "hours": 180,
    "icon": "✧",
    "summary": (
        "A generative language model has no irreducible magic in it, and this course "
        "proves that by rebuilding one from arithmetic upwards: a scalar autodiff "
        "engine, an MLP trained on it, byte-pair tokenisation, scaled dot-product "
        "attention written as plain matrix loops, and the four decoding strategies "
        "that turn logits into text. No tensor library is used or permitted — every "
        "gradient in the course is one you derived and checked."
    ),
    "outcomes": [
        "Implement reverse-mode automatic differentiation over a scalar computation graph",
        "Validate analytic gradients against central finite differences and interpret the residual",
        "Train a multilayer perceptron by stochastic gradient descent and account for the loss curve",
        "Train, encode and decode with byte-pair encoding, and reason about vocabulary size",
        "Derive and implement scaled dot-product attention, causal masking and multi-head concatenation",
        "Compare greedy, temperature, top-k and nucleus decoding, and quantify a model with perplexity",
        "Assemble the pieces into a character-level transformer that trains to a stated loss threshold",
    ],
    "assessment": "5 lab checkpoints (8% each) + transformer capstone (60%).",
    "reading": [
        "Goodfellow, Bengio & Courville, *Deep Learning* (MIT Press, 2016) — chapters 6, 8 and 10",
        "Vaswani et al., 'Attention Is All You Need', NeurIPS 2017",
        "Sennrich, Haddow & Birch, 'Neural Machine Translation of Rare Words with Subword Units', ACL 2016",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Reverse-mode automatic differentiation",
            "summary": "A scalar Value class that records its own computation graph.",
            "concepts": [
                "The chain rule applied backwards: one forward pass, one reverse pass, all partials",
                "A computation graph is a DAG whose nodes hold a value and an accumulated gradient",
                "Every operation stores a local closure that pushes gradient to its inputs",
                "Gradients *accumulate* with `+=`, which is what makes reused nodes correct",
                "Topological order guarantees a node's gradient is complete before it is spent",
                "Local derivatives: `d(a*b)/da = b`, `d(tanh x)/dx = 1 - tanh²x`, `d(exp x)/dx = exp x`",
                "Central finite differences, `(f(x+h) - f(x-h)) / 2h`, as an independent oracle",
            ],
            "lab": {
                "title": "A scalar autodiff engine",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Build the engine the rest of the course runs on. A `Value` holds a number, an
accumulated gradient, the nodes it came from, and a closure that knows how to
push gradient into those nodes.

```python
a = Value(2.0)
b = Value(-3.0)
d = (a * b + Value(10.0)).tanh()
d.backward()
a.grad   # d(d)/d(a)
```

Implement, on top of the `__init__` you are given:

- `__add__`, `__mul__` — accept a `Value` or a plain number on the right.
- `__pow__` — **constant** exponents only; a `Value` exponent must raise
  `TypeError`.
- `exp`, `log`, `tanh`, `relu` — `log` raises `ValueError` at or below zero.
- `__neg__`, `__sub__`, `__rsub__`, `__radd__`, `__rmul__`, `__truediv__`,
  `__rtruediv__` — all of these are one line each, built from the three
  primitives above. Do not give them their own backward closures.
- `topological_order()` — every node this one depends on, **children before
  parents**. Build it iteratively; a deep graph will blow the recursion limit.
- `backward()` — set `self.grad = 1.0`, then call `_backward` on the
  topological order in reverse.

Two rules decide whether this works at all:

1. Every closure uses `+=`, never `=`. `b = a + a` must give `a.grad == 2`.
2. `backward()` does **not** clear gradients. Training loops zero them
   themselves, so calling `backward()` twice accumulates — as it should.

The final check gradient-checks a composite expression against central finite
differences with `h = 1e-5`; the agreement should be around 1e-9.
''',
                "files": [{"name": "main.py", "content": r'''
import math


class Value:
    """A scalar node in a reverse-mode automatic differentiation graph."""

    def __init__(self, data, _children=(), _op=""):
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = tuple(_children)
        self._op = _op

    def __repr__(self):
        return f"Value(data={self.data:.6g}, grad={self.grad:.6g})"

    def __add__(self, other):
        # wrap `other`, build the output node, then attach a _backward closure
        pass

    def __mul__(self, other):
        pass

    def __pow__(self, other):
        # TypeError unless `other` is a plain int or float
        pass

    def exp(self):
        pass

    def log(self):
        # ValueError at or below zero
        pass

    def tanh(self):
        pass

    def relu(self):
        pass

    def __neg__(self):
        pass

    def __radd__(self, other):
        pass

    def __sub__(self, other):
        pass

    def __rsub__(self, other):
        pass

    def __rmul__(self, other):
        pass

    def __truediv__(self, other):
        pass

    def __rtruediv__(self, other):
        pass

    def topological_order(self):
        """Every node this one depends on, children before parents."""
        pass

    def backward(self):
        """Seed this node with a gradient of 1 and push it back to every leaf."""
        pass


a = Value(2.0)
b = Value(-3.0)
print(a, b)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": ENGINE_SOURCE + r'''

a = Value(2.0)
b = Value(-3.0)
c = Value(10.0)
d = (a * b + c).tanh()
d.backward()
print(d)
print("da", a.grad, "db", b.grad, "dc", c.grad)
'''}],
                "hints": [
                    "Every operation follows the same three lines: build `out` with the right data and children, define a local `_backward` that uses `+=`, then `out._backward = _backward` before returning.",
                    "`tanh` should compute `t = math.tanh(self.data)` *once* and close over it — the derivative is `1 - t*t`, and recomputing it in the closure is wasted work.",
                    "The composite operators are pure rewrites: `a - b` is `a + (-b)`, `a / b` is `a * b ** -1`, `__rsub__(self, other)` is `Value(other) + (-self)`.",
                    "For `topological_order`, push `(node, False)` onto a stack; when you pop an unvisited node, mark it seen, push `(node, True)` back, then push its children. Appending on the `True` pop gives children-before-parents.",
                ],
                "tests": [
                    {"name": "Forward arithmetic", "code": r'''
_a, _b, _c = Value(2.0), Value(-3.0), Value(10.0)
assert (_a * _b + _c).data == 4.0, f"a*b+c gave {(_a * _b + _c).data!r}, expected 4.0"
assert (_a + 5).data == 7.0, "A plain number on the right should be wrapped"
assert (5 + _a).data == 7.0, "__radd__ should handle a number on the left"
assert (2 * _a).data == 4.0 and (_a - 1).data == 1.0 and (1 - _a).data == -1.0
assert (_a / 4).data == 0.5, f"a/4 gave {(_a / 4).data!r}, expected 0.5"
assert (8 / _a).data == 4.0, f"8/a gave {(8 / _a).data!r}, expected 4.0"
assert (-_a).data == -2.0 and (_a ** 3).data == 8.0
'''},
                    {"name": "Unary functions and their error paths", "code": r'''
assert abs(Value(0.5).exp().data - math.exp(0.5)) < 1e-12
assert abs(Value(4.0).log().data - math.log(4.0)) < 1e-12
assert abs(Value(4.0).tanh().data - math.tanh(4.0)) < 1e-12
assert Value(-2.0).relu().data == 0.0 and Value(3.0).relu().data == 3.0
for _bad in (0.0, -1.0):
    try:
        Value(_bad).log()
        assert False, f"Value({_bad}).log() should raise ValueError"
    except ValueError:
        pass
try:
    Value(2.0) ** Value(3.0)
    assert False, "A Value exponent should raise TypeError"
except TypeError:
    pass
'''},
                    {"name": "The graph is topologically ordered", "code": r'''
_a, _b = Value(2.0), Value(3.0)
_c = _a * _b
_d = _c + _a
_order = _d.topological_order()
assert len(_order) == 4, f"a, b, a*b and the sum are four nodes, got {len(_order)}"
assert _order[-1] is _d, "The node you called it on comes last"
_pos = {id(_n): _i for _i, _n in enumerate(_order)}
for _n in _order:
    for _child in _n._prev:
        assert _pos[id(_child)] < _pos[id(_n)], "Every child must precede its parent"
'''},
                    {"name": "Gradients through a hand-checked expression", "code": r'''
_a, _b, _c = Value(2.0), Value(-3.0), Value(10.0)
_d = _a * _b + _c
_e = _d.tanh()
_e.backward()
_local = 1.0 - math.tanh(4.0) ** 2
assert abs(_e.data - math.tanh(4.0)) < 1e-12, f"forward gave {_e.data!r}"
assert abs(_d.grad - _local) < 1e-12, f"d.grad is {_d.grad!r}, expected {_local!r}"
assert abs(_c.grad - _local) < 1e-12, f"c.grad is {_c.grad!r}, expected {_local!r}"
assert abs(_a.grad - _local * -3.0) < 1e-12, f"a.grad is {_a.grad!r}, expected {_local * -3.0!r}"
assert abs(_b.grad - _local * 2.0) < 1e-12, f"b.grad is {_b.grad!r}, expected {_local * 2.0!r}"
'''},
                    {"name": "Reused nodes accumulate rather than overwrite", "code": r'''
_x = Value(3.0)
_y = _x + _x
_y.backward()
assert _x.grad == 2.0, f"d(x+x)/dx is 2, got {_x.grad!r} — the closures must use +="
_x = Value(3.0)
(_x * _x).backward()
assert _x.grad == 6.0, f"d(x*x)/dx at 3 is 6, got {_x.grad!r}"
_x = Value(3.0)
_z = _x * _x
_z.backward()
_z.backward()
assert _x.grad == 12.0, "backward() must not clear gradients — two passes accumulate"
'''},
                    {"name": "Elementary derivatives", "code": r'''
_x = Value(2.0)
(_x ** 3).backward()
assert abs(_x.grad - 12.0) < 1e-12, f"d(x**3)/dx at 2 is 12, got {_x.grad!r}"
_x = Value(0.5)
_y = _x.exp()
_y.backward()
assert abs(_x.grad - math.exp(0.5)) < 1e-12, f"d(exp x)/dx is exp x, got {_x.grad!r}"
_x = Value(4.0)
_x.log().backward()
assert abs(_x.grad - 0.25) < 1e-12, f"d(log x)/dx at 4 is 0.25, got {_x.grad!r}"
_x = Value(-2.0)
_x.relu().backward()
assert _x.grad == 0.0, f"relu is flat below zero, got grad {_x.grad!r}"
_x = Value(3.0)
_x.relu().backward()
assert _x.grad == 1.0, f"relu has slope 1 above zero, got {_x.grad!r}"
_x, _y = Value(4.0), Value(2.0)
(_x / _y).backward()
assert abs(_x.grad - 0.5) < 1e-12 and abs(_y.grad + 1.0) < 1e-12, \
    f"d(x/y) gave {(_x.grad, _y.grad)!r}, expected (0.5, -1.0)"
'''},
                    {"name": "Finite-difference gradient check", "code": r'''
def _f(values):
    _a, _b, _c = [Value(v) for v in values]
    _node = ((_a * _b).tanh() + (_c ** 2) * _a) * (_b + _c.exp())
    return [_a, _b, _c], _node

_point = [0.7, -1.3, 0.4]
_leaves, _node = _f(_point)
_node.backward()
_analytic = [leaf.grad for leaf in _leaves]
_h = 1e-5
for _i in range(3):
    _up = list(_point)
    _down = list(_point)
    _up[_i] += _h
    _down[_i] -= _h
    _numeric = (_f(_up)[1].data - _f(_down)[1].data) / (2 * _h)
    assert abs(_analytic[_i] - _numeric) < 1e-6, (
        f"gradient {_i}: engine says {_analytic[_i]!r}, finite differences say {_numeric!r}")
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Neurons, layers and stochastic gradient descent",
            "summary": "A multilayer perceptron built on the engine, and the loop that trains it.",
            "concepts": [
                "A neuron is an affine map followed by a non-linearity: `act(w·x + b)`",
                "A layer is a list of neurons; a network is a list of layers applied in order",
                "`parameters()` is the flat list of every learnable leaf in the graph",
                "Mean squared error, and why the loss must be a single scalar node",
                "The SGD step: zero grads, forward, backward, `p.data -= lr * p.grad`",
                "Forgetting `zero_grad` accumulates gradients across steps and diverges",
                "Learning rate as a step size: too small stalls, too large oscillates",
            ],
            "lab": {
                "title": "Training an MLP by hand",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
`engine.py` is the finished autodiff engine from module 1 — read-only, and
already imported for you. Write `mlp.py`.

**`Neuron(nin, rng, activation="tanh")`** — `nin` weights drawn with
`rng.uniform(-1.0, 1.0)` **in that order**, and a bias initialised to `0.0`.
Calling it computes `b + Σ wᵢxᵢ` and applies the activation (`"tanh"`,
`"relu"`, or `"linear"` for none). `parameters()` returns the weights followed
by the bias.

**`Layer(nin, nout, rng, activation="tanh")`** — `nout` neurons, constructed in
order. Calling it returns a list of `nout` `Value`s.

**`MLP(sizes, rng, activation="tanh")`** — for `sizes = [3, 4, 4, 1]`, three
layers: 3→4, 4→4, 4→1. Calling it with a list of numbers returns a single
`Value` when the last layer has one output, otherwise a list. Also provide
`parameters()` and `zero_grad()`.

**`mse_loss(preds, targets)`** — the mean of `(pred - target) ** 2`, as one
`Value`. `ValueError` on an empty batch or a length mismatch.

**`train(model, xs, ys, epochs, lr)`** — full-batch gradient descent. Each
epoch: forward every example, build the loss, **zero the gradients**, call
`backward()`, then step every parameter. Return the list of loss values, one
per epoch, as plain floats.

The dataset in `main.py` is the four-point problem from the module notes.
`MLP([3, 4, 4, 1])` on it, seeded with `random.Random(7)`, 100 epochs at
`lr = 0.05`, drives the loss from about 1.18 to about 0.011 — the checks
require it to end below 0.05 with every prediction on the correct side of zero.
''',
                "files": [
                    {"name": "engine.py", "ro": True, "content": ENGINE_SOURCE},
                    {"name": "mlp.py", "content": r'''
from engine import Value


class Neuron:
    """One unit: b + sum(w_i * x_i), then an activation."""

    def __init__(self, nin, rng, activation="tanh"):
        self.activation = activation
        # weights drawn with rng.uniform(-1.0, 1.0), in order; bias starts at 0.0

    def __call__(self, x):
        pass

    def parameters(self):
        pass


class Layer:
    """nout neurons that all see the same nin inputs."""

    def __init__(self, nin, nout, rng, activation="tanh"):
        pass

    def __call__(self, x):
        pass

    def parameters(self):
        pass


class MLP:
    """Layers applied in sequence."""

    def __init__(self, sizes, rng, activation="tanh"):
        pass

    def __call__(self, x):
        pass

    def parameters(self):
        pass

    def zero_grad(self):
        pass


def mse_loss(preds, targets):
    """Mean of (pred - target) ** 2 as a single Value."""
    pass


def train(model, xs, ys, epochs, lr):
    """Full-batch gradient descent. Returns one loss per epoch."""
    pass
'''},
                    {"name": "main.py", "content": r'''
import random

from mlp import MLP, mse_loss, train

XS = [[2.0, 3.0, -1.0], [3.0, -1.0, 0.5], [0.5, 1.0, 1.0], [1.0, 1.0, -1.0]]
YS = [1.0, -1.0, -1.0, 1.0]

rng = random.Random(7)
model = MLP([3, 4, 4, 1], rng)
LOSSES = train(model, XS, YS, epochs=100, lr=0.05)

print("parameters:", len(model.parameters()))
print("loss:", round(LOSSES[0], 4), "->", round(LOSSES[-1], 4))
print("predictions:", [round(model(x).data, 3) for x in XS])
'''},
                ],
                "main": "main.py",
                "solution": [
                    {"name": "mlp.py", "content": r'''
from engine import Value


class Neuron:
    """One unit: b + sum(w_i * x_i), then an activation."""

    def __init__(self, nin, rng, activation="tanh"):
        self.activation = activation
        self.w = [Value(rng.uniform(-1.0, 1.0)) for _ in range(nin)]
        self.b = Value(0.0)

    def __call__(self, x):
        total = self.b
        for weight, value in zip(self.w, x):
            total = total + weight * value
        if self.activation == "tanh":
            return total.tanh()
        if self.activation == "relu":
            return total.relu()
        return total

    def parameters(self):
        return self.w + [self.b]


class Layer:
    """nout neurons that all see the same nin inputs."""

    def __init__(self, nin, nout, rng, activation="tanh"):
        self.neurons = [Neuron(nin, rng, activation) for _ in range(nout)]

    def __call__(self, x):
        return [neuron(x) for neuron in self.neurons]

    def parameters(self):
        return [p for neuron in self.neurons for p in neuron.parameters()]


class MLP:
    """Layers applied in sequence."""

    def __init__(self, sizes, rng, activation="tanh"):
        self.sizes = list(sizes)
        self.layers = [Layer(sizes[i], sizes[i + 1], rng, activation)
                       for i in range(len(sizes) - 1)]

    def __call__(self, x):
        out = [xi if isinstance(xi, Value) else Value(xi) for xi in x]
        for layer in self.layers:
            out = layer(out)
        return out[0] if len(out) == 1 else out

    def parameters(self):
        return [p for layer in self.layers for p in layer.parameters()]

    def zero_grad(self):
        for parameter in self.parameters():
            parameter.grad = 0.0


def mse_loss(preds, targets):
    """Mean of (pred - target) ** 2 as a single Value."""
    if len(preds) != len(targets):
        raise ValueError("preds and targets must be the same length")
    if not preds:
        raise ValueError("an empty batch has no loss")
    total = None
    for pred, target in zip(preds, targets):
        term = (pred - target) ** 2
        total = term if total is None else total + term
    return total * (1.0 / len(preds))


def train(model, xs, ys, epochs, lr):
    """Full-batch gradient descent. Returns one loss per epoch."""
    losses = []
    for _ in range(epochs):
        preds = [model(x) for x in xs]
        loss = mse_loss(preds, ys)
        model.zero_grad()
        loss.backward()
        for parameter in model.parameters():
            parameter.data -= lr * parameter.grad
        losses.append(loss.data)
    return losses
'''},
                    {"name": "main.py", "content": r'''
import random

from mlp import MLP, mse_loss, train

XS = [[2.0, 3.0, -1.0], [3.0, -1.0, 0.5], [0.5, 1.0, 1.0], [1.0, 1.0, -1.0]]
YS = [1.0, -1.0, -1.0, 1.0]

rng = random.Random(7)
model = MLP([3, 4, 4, 1], rng)
LOSSES = train(model, XS, YS, epochs=100, lr=0.05)

print("parameters:", len(model.parameters()))
print("loss:", round(LOSSES[0], 4), "->", round(LOSSES[-1], 4))
print("predictions:", [round(model(x).data, 3) for x in XS])
'''},
                ],
                "hints": [
                    "Start the neuron's sum from the bias — `total = self.b` — then fold in `weight * value`. Starting from `Value(0.0)` works too but adds a node for nothing.",
                    "`MLP.__call__` should wrap raw numbers once at the top: `[xi if isinstance(xi, Value) else Value(xi) for xi in x]`, then just pass the list through each layer.",
                    "`parameters()` at every level is the same flattening comprehension: `[p for child in children for p in child.parameters()]`.",
                    "The order inside `train` matters: forward, build the loss, `model.zero_grad()`, `loss.backward()`, then step. Zeroing after `backward()` erases exactly what you need.",
                ],
                "tests": [
                    {"name": "A neuron is an affine map plus an activation", "code": r'''
import random as _random
from mlp import Neuron
_n = Neuron(3, _random.Random(7))
assert len(_n.w) == 3, f"Three inputs need three weights, got {len(_n.w)}"
assert _n.b.data == 0.0, f"The bias should start at 0.0, got {_n.b.data!r}"
_r = _random.Random(7)
_want = [_r.uniform(-1.0, 1.0) for _ in range(3)]
assert [w.data for w in _n.w] == _want, \
    f"Weights should be the first three rng.uniform(-1, 1) draws, got {[w.data for w in _n.w]!r}"
_act = _n([1.0, 2.0, 3.0])
assert -1.0 < _act.data < 1.0, f"A tanh unit lives in (-1, 1), got {_act.data!r}"
_lin = Neuron(2, _random.Random(1), activation="linear")
_lin.w[0].data, _lin.w[1].data, _lin.b.data = 2.0, -1.0, 0.5
assert _lin([3.0, 4.0]).data == 2.5, f"0.5 + 2*3 - 1*4 is 2.5, got {_lin([3.0, 4.0]).data!r}"
assert len(_lin.parameters()) == 3, "Two weights and a bias"
'''},
                    {"name": "Layers and networks flatten their parameters", "code": r'''
import random as _random
from mlp import Layer, MLP
_l = Layer(3, 4, _random.Random(7))
assert len(_l([1.0, 2.0, 3.0])) == 4, "A 3->4 layer returns four Values"
assert len(_l.parameters()) == 16, f"4 neurons x (3 weights + bias) is 16, got {len(_l.parameters())}"
_m = MLP([3, 4, 4, 1], _random.Random(7))
assert len(_m.parameters()) == 41, f"16 + 20 + 5 is 41 parameters, got {len(_m.parameters())}"
assert len(MLP([2, 1], _random.Random(7)).parameters()) == 3, "A single 2->1 layer has 3 parameters"
assert len(MLP([2, 3], _random.Random(7))([1.0, 1.0])) == 3, "Three outputs come back as a list"
_single = _m([1.0, 2.0, 3.0])
assert not isinstance(_single, list), "A one-output network returns the Value itself"
'''},
                    {"name": "The loss is a single differentiable scalar", "code": r'''
from engine import Value
from mlp import mse_loss
_loss = mse_loss([Value(2.0), Value(0.0)], [1.0, 1.0])
assert isinstance(_loss, Value), "mse_loss must return a Value, not a float"
assert abs(_loss.data - 1.0) < 1e-12, f"mean of 1 and 1 is 1.0, got {_loss.data!r}"
_p = Value(3.0)
mse_loss([_p], [1.0]).backward()
assert abs(_p.grad - 4.0) < 1e-12, f"d/dp (p-1)^2 at 3 is 4, got {_p.grad!r}"
for _bad in ([[], []], [[Value(1.0)], [1.0, 2.0]]):
    try:
        mse_loss(*_bad)
        assert False, f"mse_loss{tuple(_bad)!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "zero_grad clears every parameter", "code": r'''
import random as _random
from mlp import MLP, mse_loss
_m = MLP([2, 2, 1], _random.Random(7))
mse_loss([_m([1.0, -1.0])], [1.0]).backward()
assert any(p.grad != 0.0 for p in _m.parameters()), "backward should reach the parameters"
_m.zero_grad()
assert all(p.grad == 0.0 for p in _m.parameters()), "zero_grad must clear all of them"
'''},
                    {"name": "Training drives the loss down", "code": r'''
assert isinstance(LOSSES, list) and len(LOSSES) == 100, \
    f"train should return one loss per epoch, got {len(LOSSES) if isinstance(LOSSES, list) else LOSSES!r}"
assert all(isinstance(x, float) for x in LOSSES), "The losses should be plain floats"
assert abs(LOSSES[0] - 1.1845288187388343) < 1e-9, \
    f"With random.Random(7) the first loss is 1.1845288187388343, got {LOSSES[0]!r}"
assert LOSSES[-1] < 0.05, f"After 100 epochs the loss should be under 0.05, got {LOSSES[-1]!r}"
assert LOSSES[-1] < LOSSES[0] / 10, "The loss should fall by at least an order of magnitude"
'''},
                    {"name": "The trained network separates the four points", "code": r'''
_preds = [model(x).data for x in XS]
for _p, _y in zip(_preds, YS):
    assert _p * _y > 0.0, f"prediction {_p!r} is on the wrong side of zero for target {_y}"
    assert abs(_p - _y) < 0.25, f"prediction {_p!r} is too far from target {_y}"
'''},
                    {"name": "Training is deterministic and repeatable", "code": r'''
import random as _random
from mlp import MLP, train
_again = train(MLP([3, 4, 4, 1], _random.Random(7)), XS, YS, epochs=100, lr=0.05)
assert _again == LOSSES, "Same seed, same data, same schedule — the run must reproduce exactly"
_short = train(MLP([3, 4, 4, 1], _random.Random(7)), XS, YS, epochs=1, lr=0.05)
assert len(_short) == 1 and abs(_short[0] - LOSSES[0]) < 1e-12, \
    "The first epoch's loss must not depend on how many epochs follow"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Tokenisation and embeddings",
            "summary": "Byte-pair encoding from scratch, then vectors and cosine similarity.",
            "concepts": [
                "Bytes are the only universal alphabet: 256 symbols, no unknown-token problem",
                "BPE greedily merges the most frequent adjacent pair, repeatedly",
                "The merge list *is* the tokeniser: learned order, replayed at encode time",
                "Vocabulary size trades sequence length against embedding-table size",
                "Decoding concatenates the byte strings a merge tree stands for",
                "An embedding table is a lookup: token id to a learned dense vector",
                "Cosine similarity measures direction, ignoring magnitude — undefined at the origin",
            ],
            "lab": {
                "title": "Byte-pair encoding and vector lookup",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
## Byte-pair encoding

Work over the UTF-8 bytes of the text; ids 0-255 are the raw bytes and every
merge introduces the next free id.

- `get_stats(ids)` — a dict of every adjacent pair to how often it occurs.
- `merge(ids, pair, new_id)` — a new list with each **non-overlapping**
  left-to-right occurrence of `pair` replaced by `new_id`.
- `train_bpe(text, vocab_size)` — repeatedly merge the most frequent pair,
  **breaking ties by taking the numerically smallest pair**, until the vocabulary
  reaches `vocab_size` or no pair repeats. Returns `{pair: new_id}` in learned
  order. `ValueError` when `vocab_size < 256`.
- `build_vocab(merges)` — `{id: bytes}` for every id, base bytes included.
- `encode(text, merges)` — bytes, then replay the merges in learned order.
- `decode(ids, merges)` — the ids back to text, decoding UTF-8 with
  `errors="replace"`.

The worked example from the module notes:

```text
train_bpe("aaabdaaabac", 258)  ->  {(97, 97): 256, (97, 98): 257}
encode("aaabdaaabac", merges)  ->  [256, 257, 100, 256, 257, 97, 99]
```

Encoding then decoding must return the original string for **any** input, not
just the training text.

## Embeddings

- `EmbeddingTable(vocab_size, dim, seed=7)` — `vocab_size * dim` values drawn
  in row-major order from `random.Random(seed).uniform(-1.0, 1.0)`.
  `vector(token_id)` returns one row as a list of floats and raises
  `IndexError` outside the table.
- `cosine_similarity(u, v)` — `u·v / (|u| |v|)`. `ValueError` on a length
  mismatch or on a zero vector, which has no direction.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random


def get_stats(ids):
    """Every adjacent pair mapped to how often it occurs."""
    # your code here


def merge(ids, pair, new_id):
    """Replace each non-overlapping occurrence of pair with new_id."""
    # your code here


def train_bpe(text, vocab_size):
    """Learn merges up to vocab_size. ValueError below 256."""
    # your code here


def build_vocab(merges):
    """{id: bytes} for the 256 base bytes plus every merge."""
    # your code here


def encode(text, merges):
    """UTF-8 bytes with the merges replayed in learned order."""
    # your code here


def decode(ids, merges):
    """Token ids back to text."""
    # your code here


class EmbeddingTable:
    """vocab_size rows of dim floats, drawn row-major from a seeded RNG."""

    def __init__(self, vocab_size, dim, seed=7):
        self.vocab_size = vocab_size
        self.dim = dim
        # fill self.rows with vocab_size lists of dim uniform(-1, 1) draws

    def vector(self, token_id):
        # your code here
        pass


def cosine_similarity(u, v):
    """Direction agreement in [-1, 1]. ValueError for a zero vector."""
    # your code here


MERGES = train_bpe("aaabdaaabac", 258)
print(MERGES)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random


def get_stats(ids):
    """Every adjacent pair mapped to how often it occurs."""
    stats = {}
    for left, right in zip(ids, ids[1:]):
        stats[(left, right)] = stats.get((left, right), 0) + 1
    return stats


def merge(ids, pair, new_id):
    """Replace each non-overlapping occurrence of pair with new_id."""
    out = []
    i = 0
    while i < len(ids):
        if i < len(ids) - 1 and ids[i] == pair[0] and ids[i + 1] == pair[1]:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


def train_bpe(text, vocab_size):
    """Learn merges up to vocab_size. ValueError below 256."""
    if vocab_size < 256:
        raise ValueError("a byte-level vocabulary starts at 256")
    ids = list(text.encode("utf-8"))
    merges = {}
    for new_id in range(256, vocab_size):
        stats = get_stats(ids)
        if not stats:
            break
        pair, count = min(stats.items(), key=lambda item: (-item[1], item[0]))
        if count < 2:
            break
        ids = merge(ids, pair, new_id)
        merges[pair] = new_id
    return merges


def build_vocab(merges):
    """{id: bytes} for the 256 base bytes plus every merge."""
    vocab = {i: bytes([i]) for i in range(256)}
    for (left, right), new_id in sorted(merges.items(), key=lambda item: item[1]):
        vocab[new_id] = vocab[left] + vocab[right]
    return vocab


def encode(text, merges):
    """UTF-8 bytes with the merges replayed in learned order."""
    ids = list(text.encode("utf-8"))
    for pair, new_id in sorted(merges.items(), key=lambda item: item[1]):
        ids = merge(ids, pair, new_id)
    return ids


def decode(ids, merges):
    """Token ids back to text."""
    vocab = build_vocab(merges)
    raw = b"".join(vocab[i] for i in ids)
    return raw.decode("utf-8", errors="replace")


class EmbeddingTable:
    """vocab_size rows of dim floats, drawn row-major from a seeded RNG."""

    def __init__(self, vocab_size, dim, seed=7):
        self.vocab_size = vocab_size
        self.dim = dim
        rng = random.Random(seed)
        self.rows = [[rng.uniform(-1.0, 1.0) for _ in range(dim)]
                     for _ in range(vocab_size)]

    def vector(self, token_id):
        if not 0 <= token_id < self.vocab_size:
            raise IndexError(f"token id {token_id} is outside the table")
        return self.rows[token_id]


def cosine_similarity(u, v):
    """Direction agreement in [-1, 1]. ValueError for a zero vector."""
    if len(u) != len(v):
        raise ValueError("vectors must be the same length")
    norm_u = math.sqrt(sum(a * a for a in u))
    norm_v = math.sqrt(sum(b * b for b in v))
    if norm_u == 0.0 or norm_v == 0.0:
        raise ValueError("the zero vector has no direction")
    return sum(a * b for a, b in zip(u, v)) / (norm_u * norm_v)


MERGES = train_bpe("aaabdaaabac", 258)
print(MERGES)
print(encode("aaabdaaabac", MERGES))
print(decode(encode("aaabdaaabac", MERGES), MERGES))
TABLE = EmbeddingTable(300, 8)
print(round(cosine_similarity(TABLE.vector(256), TABLE.vector(257)), 6))
'''}],
                "hints": [
                    "`get_stats` is one pass with `zip(ids, ids[1:])` and the usual `dict.get(key, 0) + 1` accumulator.",
                    "In `merge`, advance by 2 when you replace a pair and by 1 otherwise — that `i += 2` is what makes the matches non-overlapping.",
                    "`min(stats.items(), key=lambda item: (-item[1], item[0]))` picks the most frequent pair and breaks ties on the smallest pair, in one expression.",
                    "`build_vocab` must walk the merges *in learned order* so that `vocab[left]` and `vocab[right]` already exist when a later merge refers to them.",
                ],
                "tests": [
                    {"name": "Pair statistics", "code": r'''
assert get_stats([1, 2, 1, 2, 3]) == {(1, 2): 2, (2, 1): 1, (2, 3): 1}, \
    f"Got {get_stats([1, 2, 1, 2, 3])!r}"
assert get_stats([]) == {}, "No ids, no pairs"
assert get_stats([5]) == {}, "A single id has no adjacent pair"
assert get_stats([7, 7, 7]) == {(7, 7): 2}, f"Got {get_stats([7, 7, 7])!r}"
'''},
                    {"name": "Merging is non-overlapping and left to right", "code": r'''
assert merge([1, 2, 1, 2, 3], (1, 2), 256) == [256, 256, 3], f"Got {merge([1, 2, 1, 2, 3], (1, 2), 256)!r}"
assert merge([1, 1, 1], (1, 1), 9) == [9, 1], f"Overlaps must not double-count, got {merge([1, 1, 1], (1, 1), 9)!r}"
assert merge([1, 2, 3], (4, 5), 9) == [1, 2, 3], "A pair that never occurs changes nothing"
assert merge([], (1, 2), 9) == [], "Nothing to merge"
assert merge([1], (1, 2), 9) == [1], "A trailing single id survives"
'''},
                    {"name": "The worked training example", "code": r'''
_m = train_bpe("aaabdaaabac", 258)
assert _m == {(97, 97): 256, (97, 98): 257}, f"Got {_m!r}, expected {{(97, 97): 256, (97, 98): 257}}"
assert list(_m.values()) == [256, 257], "Merge ids are handed out in learned order"
assert train_bpe("aaabdaaabac", 256) == {}, "No headroom means no merges"
assert train_bpe("abcdef", 300) == {}, "Nothing repeats, so nothing can be merged"
try:
    train_bpe("abc", 255)
    assert False, "A vocabulary below 256 should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Encoding replays the merges", "code": r'''
_m = train_bpe("aaabdaaabac", 258)
_ids = encode("aaabdaaabac", _m)
assert _ids == [256, 257, 100, 256, 257, 97, 99], f"Got {_ids!r}"
assert encode("", _m) == [], "Empty text encodes to no tokens"
assert encode("z", _m) == [122], "An unmerged byte keeps its own id"
assert len(_ids) < len("aaabdaaabac".encode("utf-8")), "The merges should shorten the sequence"
'''},
                    {"name": "The vocabulary spells out each merge", "code": r'''
_m = train_bpe("aaabdaaabac", 258)
_v = build_vocab(_m)
assert len(_v) == 258, f"256 base bytes plus two merges is 258 entries, got {len(_v)}"
assert _v[97] == b"a" and _v[256] == b"aa" and _v[257] == b"ab", \
    f"Got {_v[256]!r} and {_v[257]!r}, expected b'aa' and b'ab'"
'''},
                    {"name": "Encode and decode round-trip anything", "code": r'''
_m = train_bpe("aaabdaaabac", 258)
for _text in ["aaabdaaabac", "", "z", "banana bandana", "héllo wörld", "aaaa"]:
    _back = decode(encode(_text, _m), _m)
    assert _back == _text, f"Round trip of {_text!r} gave {_back!r}"
_trained = train_bpe("the cat sat on the mat, the cat ran", 280)
_long = "the cat sat on the mat, the cat ran"
assert decode(encode(_long, _trained), _trained) == _long, "Round trip must survive real merges"
assert len(encode(_long, _trained)) < len(_long.encode("utf-8")), "Training should compress its own text"
'''},
                    {"name": "The embedding table is a deterministic lookup", "code": r'''
_t = EmbeddingTable(300, 8)
assert len(_t.vector(0)) == 8, f"Rows should have 8 entries, got {len(_t.vector(0))}"
assert all(-1.0 <= x <= 1.0 for x in _t.vector(12)), "Draws come from uniform(-1, 1)"
assert _t.vector(5) != _t.vector(6), "Different tokens get different vectors"
assert EmbeddingTable(300, 8).vector(5) == _t.vector(5), "The same seed rebuilds the same table"
assert EmbeddingTable(300, 8, seed=8).vector(5) != _t.vector(5), "A different seed does not"
_expected_first = random.Random(7).uniform(-1.0, 1.0)
assert _t.vector(0)[0] == _expected_first, "Row-major order: row 0 takes the first draws"
for _bad in (-1, 300, 999):
    try:
        _t.vector(_bad)
        assert False, f"vector({_bad}) should raise IndexError"
    except IndexError:
        pass
'''},
                    {"name": "Cosine similarity", "code": r'''
assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0, "Orthogonal vectors score 0"
assert abs(cosine_similarity([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]) - 1.0) < 1e-12, \
    "Scaling a vector does not change its direction"
assert abs(cosine_similarity([1.0, 0.0], [-1.0, 0.0]) + 1.0) < 1e-12, "Opposite vectors score -1"
_t = EmbeddingTable(20, 6)
assert abs(cosine_similarity(_t.vector(3), _t.vector(3)) - 1.0) < 1e-12, "A vector matches itself"
for _bad in ([[1.0, 2.0], [1.0]], [[0.0, 0.0], [1.0, 1.0]]):
    try:
        cosine_similarity(*_bad)
        assert False, f"cosine_similarity{tuple(_bad)!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Attention",
            "summary": "Scaled dot-product attention, causal masking and multiple heads, in plain Python.",
            "concepts": [
                "Queries, keys and values are three linear views of the same sequence",
                "`softmax(QKᵀ / √d_k) V`: a similarity matrix turned into a convex combination",
                "The `√d_k` divisor keeps the logits out of softmax saturation as `d_k` grows",
                "Softmax needs the max-subtraction trick to stay finite for large scores",
                "A causal mask sets forbidden scores to `-inf` *before* the softmax, never after",
                "Heads split the model dimension, attend independently, then concatenate",
                "Attention is permutation-equivariant, which is why positional information is added",
            ],
            "lab": {
                "title": "Scaled dot-product attention from scratch",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Matrices are lists of row lists. No library does any of this for you.

**Linear algebra**

- `dot(u, v)` — `ValueError` on a length mismatch.
- `transpose(A)`.
- `matmul(A, B)` — `ValueError` when `A`'s width does not match `B`'s height.
- `softmax(xs)` — subtract the maximum before exponentiating. `ValueError` on
  an empty list, and on a list where every entry is `-inf`.

**Attention**

- `causal_mask(n)` — an `n × n` grid of booleans; `mask[i][j]` is `True` when
  position `i` is allowed to attend to position `j`, i.e. when `j <= i`.
- `attention(Q, K, V, mask=None)` — returns `(output, weights)`. Scores are
  `Q · Kᵀ` divided by `√d_k` where `d_k = len(Q[0])`. Where `mask[i][j]` is
  `False`, set the score to `float("-inf")` before the softmax.

Two cases you can check by hand:

```text
Q = [[0, 0]], K = [[1, 0], [0, 1]], V = [[1, 2], [3, 4]]
->  weights [[0.5, 0.5]],  output [[2.0, 3.0]]

Q = [[1, 0]],  same K and V
->  weights [[0.6697615493266569, 0.3302384506733431]]
    output  [[1.6604769013466862, 2.6604769013466862]]
```

**Heads**

- `split_heads(X, n_heads)` — split the columns of `X` into `n_heads` equal
  blocks, returning a list of matrices. `ValueError` when the width does not
  divide evenly.
- `concat_heads(heads)` — the inverse.
- `multi_head_attention(X, n_heads, Wq, Wk, Wv, Wo, causal=False)` — project
  `X` through `Wq`, `Wk`, `Wv`, split into heads, attend in each head,
  concatenate, and project through `Wo`.

With one head and identity projections this must reduce exactly to
`attention(X, X, X)[0]`.
''',
                "files": [{"name": "main.py", "content": r'''
import math

INF = float("-inf")


def dot(u, v):
    """Inner product. ValueError on a length mismatch."""
    # your code here


def transpose(A):
    """Rows become columns."""
    # your code here


def matmul(A, B):
    """Matrix product. ValueError when the inner dimensions disagree."""
    # your code here


def softmax(xs):
    """Stable softmax over a list of scores."""
    # your code here


def causal_mask(n):
    """mask[i][j] is True when position i may attend to position j."""
    # your code here


def attention(Q, K, V, mask=None):
    """(output, weights) for scaled dot-product attention."""
    # your code here


def split_heads(X, n_heads):
    """Split the columns of X into n_heads equal blocks."""
    # your code here


def concat_heads(heads):
    """Join head outputs back into one wide matrix."""
    # your code here


def multi_head_attention(X, n_heads, Wq, Wk, Wv, Wo, causal=False):
    """Project, split, attend per head, concatenate, project out."""
    # your code here


X = [[1.0, 2.0, 0.5, -1.0], [0.0, 1.0, 1.0, 2.0], [-1.0, 0.5, 2.0, 0.0]]
print(X)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

INF = float("-inf")


def dot(u, v):
    """Inner product. ValueError on a length mismatch."""
    if len(u) != len(v):
        raise ValueError(f"cannot dot a length-{len(u)} with a length-{len(v)} vector")
    return sum(a * b for a, b in zip(u, v))


def transpose(A):
    """Rows become columns."""
    return [list(column) for column in zip(*A)]


def matmul(A, B):
    """Matrix product. ValueError when the inner dimensions disagree."""
    if not A or not B:
        raise ValueError("cannot multiply an empty matrix")
    if len(A[0]) != len(B):
        raise ValueError(f"inner dimensions {len(A[0])} and {len(B)} disagree")
    columns = transpose(B)
    return [[dot(row, column) for column in columns] for row in A]


def softmax(xs):
    """Stable softmax over a list of scores."""
    if not xs:
        raise ValueError("softmax needs at least one score")
    top = max(xs)
    if top == INF:
        raise ValueError("every score is masked out")
    exps = [math.exp(x - top) for x in xs]
    total = sum(exps)
    return [e / total for e in exps]


def causal_mask(n):
    """mask[i][j] is True when position i may attend to position j."""
    return [[j <= i for j in range(n)] for i in range(n)]


def attention(Q, K, V, mask=None):
    """(output, weights) for scaled dot-product attention."""
    scale = 1.0 / math.sqrt(len(Q[0]))
    weights = []
    for i, query in enumerate(Q):
        scores = []
        for j, key in enumerate(K):
            if mask is not None and not mask[i][j]:
                scores.append(INF)
            else:
                scores.append(dot(query, key) * scale)
        weights.append(softmax(scores))
    return (matmul(weights, V), weights)


def split_heads(X, n_heads):
    """Split the columns of X into n_heads equal blocks."""
    width = len(X[0])
    if width % n_heads != 0:
        raise ValueError(f"{width} columns do not split into {n_heads} heads")
    size = width // n_heads
    return [[row[h * size:(h + 1) * size] for row in X] for h in range(n_heads)]


def concat_heads(heads):
    """Join head outputs back into one wide matrix."""
    return [[value for head in heads for value in head[i]]
            for i in range(len(heads[0]))]


def multi_head_attention(X, n_heads, Wq, Wk, Wv, Wo, causal=False):
    """Project, split, attend per head, concatenate, project out."""
    Q = matmul(X, Wq)
    K = matmul(X, Wk)
    V = matmul(X, Wv)
    mask = causal_mask(len(X)) if causal else None
    outputs = []
    for head_q, head_k, head_v in zip(split_heads(Q, n_heads),
                                      split_heads(K, n_heads),
                                      split_heads(V, n_heads)):
        outputs.append(attention(head_q, head_k, head_v, mask)[0])
    return matmul(concat_heads(outputs), Wo)


X = [[1.0, 2.0, 0.5, -1.0], [0.0, 1.0, 1.0, 2.0], [-1.0, 0.5, 2.0, 0.0]]
IDENTITY = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
print(attention([[0.0, 0.0]], [[1.0, 0.0], [0.0, 1.0]], [[1.0, 2.0], [3.0, 4.0]]))
print(multi_head_attention(X, 2, IDENTITY, IDENTITY, IDENTITY, IDENTITY, causal=True))
'''}],
                "hints": [
                    "`transpose(A)` is `[list(column) for column in zip(*A)]`; `matmul` is then a double comprehension over rows and transposed columns.",
                    "Subtract `max(xs)` before exponentiating. It cancels exactly in the ratio, and it is the only thing keeping `exp` finite for large scores.",
                    "In `attention`, decide masked-or-not *per score*, appending `float(\"-inf\")` for a blocked position. `exp(-inf - top)` is 0.0, so the weight comes out exactly zero.",
                    "`split_heads` slices each row: head `h` takes `row[h*size:(h+1)*size]`. `concat_heads` walks row index `i` and flattens across heads.",
                ],
                "tests": [
                    {"name": "Linear algebra and its error paths", "code": r'''
assert dot([1.0, 2.0, 3.0], [4.0, 5.0, 6.0]) == 32.0, f"Got {dot([1.0, 2.0, 3.0], [4.0, 5.0, 6.0])!r}"
assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]], f"Got {transpose([[1, 2, 3], [4, 5, 6]])!r}"
assert matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]]) == [[19, 22], [43, 50]], \
    f"Got {matmul([[1, 2], [3, 4]], [[5, 6], [7, 8]])!r}"
assert matmul([[1, 2, 3]], [[1], [1], [1]]) == [[6]], "A 1x3 times a 3x1 is a 1x1"
try:
    dot([1.0], [1.0, 2.0])
    assert False, "Mismatched vectors should raise ValueError"
except ValueError:
    pass
try:
    matmul([[1, 2, 3]], [[1, 2]])
    assert False, "Mismatched inner dimensions should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Softmax is normalised, shift-invariant and stable", "code": r'''
_p = softmax([2.0, 1.0, 0.1, -1.0])
assert abs(sum(_p) - 1.0) < 1e-12, f"softmax should sum to 1, got {sum(_p)!r}"
assert abs(_p[0] - 0.6380663511479376) < 1e-12, f"Got {_p!r}"
_shifted = softmax([102.0, 101.0, 100.1, 99.0])
for _a, _b in zip(_p, _shifted):
    assert abs(_a - _b) < 1e-12, "Adding a constant to every score must not change the result"
_big = softmax([1000.0, 0.0])
assert abs(_big[0] - 1.0) < 1e-12 and _big[1] == 0.0, f"Large scores must not overflow, got {_big!r}"
assert softmax([5.0]) == [1.0], "One score takes all the mass"
for _bad in ([], [INF, INF]):
    try:
        softmax(_bad)
        assert False, f"softmax({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Equal scores give a plain average", "code": r'''
_out, _w = attention([[0.0, 0.0]], [[1.0, 0.0], [0.0, 1.0]], [[1.0, 2.0], [3.0, 4.0]])
assert _w == [[0.5, 0.5]], f"Zero queries score everything equally, got {_w!r}"
assert _out == [[2.0, 3.0]], f"That is the mean of the two value rows, got {_out!r}"
'''},
                    {"name": "The hand-computed attention example", "code": r'''
_out, _w = attention([[1.0, 0.0]], [[1.0, 0.0], [0.0, 1.0]], [[1.0, 2.0], [3.0, 4.0]])
assert abs(_w[0][0] - 0.6697615493266569) < 1e-12, f"weights were {_w!r}"
assert abs(_w[0][1] - 0.3302384506733431) < 1e-12, f"weights were {_w!r}"
assert abs(_out[0][0] - 1.6604769013466862) < 1e-12, f"output was {_out!r}"
assert abs(_out[0][1] - 2.6604769013466862) < 1e-12, f"output was {_out!r}"
'''},
                    {"name": "The causal mask", "code": r'''
_m = causal_mask(3)
assert _m == [[True, False, False], [True, True, False], [True, True, True]], f"Got {_m!r}"
assert causal_mask(1) == [[True]], "A single position may always see itself"
'''},
                    {"name": "Masking blocks the future exactly", "code": r'''
_K = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
_V = [[1.0, 0.0], [0.0, 1.0], [2.0, 2.0]]
_out, _w = attention(_K, _K, _V, causal_mask(3))
assert _w[0] == [1.0, 0.0, 0.0], f"Row 0 can only attend to itself, got {_w[0]!r}"
assert _out[0] == _V[0], f"So its output is exactly V[0], got {_out[0]!r}"
assert _w[1][2] == 0.0, f"Row 1 must not see position 2, got {_w[1]!r}"
for _row in _w:
    assert abs(sum(_row) - 1.0) < 1e-12, f"Every weight row must still sum to 1, got {_row!r}"
_unmasked = attention(_K, _K, _V)[1]
assert all(x > 0.0 for x in _unmasked[0]), "Without a mask, row 0 sees everything"
'''},
                    {"name": "Heads split and rejoin", "code": r'''
_Y = [[1, 2, 3, 4], [5, 6, 7, 8]]
_h = split_heads(_Y, 2)
assert _h == [[[1, 2], [5, 6]], [[3, 4], [7, 8]]], f"Got {_h!r}"
assert concat_heads(_h) == _Y, f"concat_heads should invert split_heads, got {concat_heads(_h)!r}"
assert split_heads(_Y, 1) == [_Y], "One head is the whole matrix"
try:
    split_heads(_Y, 3)
    assert False, "Four columns do not split into three heads"
except ValueError:
    pass
'''},
                    {"name": "Multi-head attention reduces to one head", "code": r'''
_I = [[1.0 if i == j else 0.0 for j in range(4)] for i in range(4)]
_single = multi_head_attention(X, 1, _I, _I, _I, _I)
_plain = attention(X, X, X)[0]
for _r1, _r2 in zip(_single, _plain):
    for _a, _b in zip(_r1, _r2):
        assert abs(_a - _b) < 1e-12, f"One identity head should equal plain attention: {_single!r} vs {_plain!r}"
_two = multi_head_attention(X, 2, _I, _I, _I, _I)
assert len(_two) == 3 and len(_two[0]) == 4, f"Shape should survive, got {len(_two)}x{len(_two[0])}"
assert any(abs(_a - _b) > 1e-9 for _r1, _r2 in zip(_two, _plain) for _a, _b in zip(_r1, _r2)), \
    "Two heads attend on half-width keys, so the result must differ from one head"
_causal = multi_head_attention(X, 1, _I, _I, _I, _I, causal=True)
assert all(abs(_a - _b) < 1e-12 for _a, _b in zip(_causal[0], X[0])), \
    f"Under a causal mask the first row is its own value row, got {_causal[0]!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Decoding and evaluation",
            "summary": "Turning logits into tokens: greedy, temperature, top-k, nucleus — and perplexity.",
            "concepts": [
                "Logits are unnormalised scores; only softmax makes them a distribution",
                "Temperature divides the logits: below 1 sharpens, above 1 flattens, 0 is undefined",
                "Greedy decoding is `argmax` — deterministic, and prone to degenerate repetition",
                "Truncation samples from a restricted support: top-k by rank, nucleus by mass",
                "Nucleus (top-p) adapts its cut to the shape of the distribution, unlike top-k",
                "Inverse-transform sampling: one uniform draw against the cumulative distribution",
                "Perplexity is `exp` of the mean negative log-likelihood — the effective branching factor",
            ],
            "lab": {
                "title": "Four decoding strategies and a perplexity",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Everything here operates on a fixed list of logits, so the results are exactly
reproducible.

- `softmax(logits, temperature=1.0)` — divide by the temperature first.
  `ValueError` for a temperature at or below zero, and for empty logits.
- `greedy(logits)` — the index of the largest logit, the **lowest** index on a
  tie. `ValueError` on empty logits.
- `top_k_filter(logits, k)` — a new list where everything outside the `k`
  largest logits is `float("-inf")`. `k` at or above the length returns an
  unchanged copy. `ValueError` for `k < 1`.
- `nucleus_filter(logits, p)` — sort by probability descending and keep the
  shortest prefix whose cumulative probability reaches `p`; everything else
  becomes `-inf`. `ValueError` unless `0 < p <= 1`.
- `sample_index(probs, rng)` — inverse-transform sampling: draw
  `r = rng.random()` once, walk the cumulative sum, return the first index
  where the running total exceeds `r`.
- `sample(logits, rng, temperature=1.0, top_k=None, top_p=None)` — apply
  `top_k` then `top_p` (when given), then softmax at that temperature, then
  `sample_index`.
- `perplexity(probs)` — `exp(-mean(log p))` over the probabilities the model
  assigned to the tokens that actually occurred. `ValueError` on an empty list
  or on any probability at or below zero.

Worked values you can verify by hand: a uniform distribution over four tokens
gives a perplexity of exactly `4.0`; for
`probs = [0.5, 0.3, 0.15, 0.05]`, `p = 0.8` keeps two tokens and `p = 0.9`
keeps three.
''',
                "files": [{"name": "main.py", "content": r'''
import math
import random

INF = float("-inf")

LOGITS = [math.log(0.5), math.log(0.3), math.log(0.15), math.log(0.05)]


def softmax(logits, temperature=1.0):
    """Stable softmax after dividing by the temperature."""
    # your code here


def greedy(logits):
    """Index of the largest logit; lowest index on a tie."""
    # your code here


def top_k_filter(logits, k):
    """Everything outside the k largest logits becomes -inf."""
    # your code here


def nucleus_filter(logits, p):
    """Keep the shortest prefix of probability mass reaching p."""
    # your code here


def sample_index(probs, rng):
    """Inverse-transform sampling from one rng.random() draw."""
    # your code here


def sample(logits, rng, temperature=1.0, top_k=None, top_p=None):
    """Filter, soften, then draw one index."""
    # your code here


def perplexity(probs):
    """exp of the mean negative log-likelihood."""
    # your code here


print(LOGITS)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math
import random

INF = float("-inf")

LOGITS = [math.log(0.5), math.log(0.3), math.log(0.15), math.log(0.05)]


def softmax(logits, temperature=1.0):
    """Stable softmax after dividing by the temperature."""
    if not logits:
        raise ValueError("softmax needs at least one logit")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    scaled = [x / temperature for x in logits]
    top = max(scaled)
    if top == INF:
        raise ValueError("every logit is masked out")
    exps = [math.exp(x - top) for x in scaled]
    total = sum(exps)
    return [e / total for e in exps]


def greedy(logits):
    """Index of the largest logit; lowest index on a tie."""
    if not logits:
        raise ValueError("nothing to choose from")
    best = 0
    for i in range(1, len(logits)):
        if logits[i] > logits[best]:
            best = i
    return best


def top_k_filter(logits, k):
    """Everything outside the k largest logits becomes -inf."""
    if k < 1:
        raise ValueError("k must be at least 1")
    if k >= len(logits):
        return list(logits)
    ranked = sorted(range(len(logits)), key=lambda i: (-logits[i], i))
    keep = set(ranked[:k])
    return [logits[i] if i in keep else INF for i in range(len(logits))]


def nucleus_filter(logits, p):
    """Keep the shortest prefix of probability mass reaching p."""
    if not 0.0 < p <= 1.0:
        raise ValueError("p must lie in (0, 1]")
    probs = softmax(logits)
    ranked = sorted(range(len(logits)), key=lambda i: (-probs[i], i))
    keep = set()
    running = 0.0
    for i in ranked:
        keep.add(i)
        running += probs[i]
        if running >= p - 1e-12:
            break
    return [logits[i] if i in keep else INF for i in range(len(logits))]


def sample_index(probs, rng):
    """Inverse-transform sampling from one rng.random() draw."""
    if not probs:
        raise ValueError("nothing to sample from")
    draw = rng.random()
    running = 0.0
    for i, prob in enumerate(probs):
        running += prob
        if draw < running:
            return i
    return len(probs) - 1


def sample(logits, rng, temperature=1.0, top_k=None, top_p=None):
    """Filter, soften, then draw one index."""
    filtered = list(logits)
    if top_k is not None:
        filtered = top_k_filter(filtered, top_k)
    if top_p is not None:
        filtered = nucleus_filter(filtered, top_p)
    return sample_index(softmax(filtered, temperature), rng)


def perplexity(probs):
    """exp of the mean negative log-likelihood."""
    if not probs:
        raise ValueError("perplexity needs at least one probability")
    total = 0.0
    for prob in probs:
        if prob <= 0.0:
            raise ValueError("a probability of zero has infinite surprise")
        total += math.log(prob)
    return math.exp(-total / len(probs))


print("greedy:", greedy(LOGITS))
print("softmax at T=1:", [round(x, 4) for x in softmax(LOGITS)])
print("softmax at T=0.1:", [round(x, 4) for x in softmax(LOGITS, 0.1)])
print("top-2:", top_k_filter(LOGITS, 2))
print("nucleus 0.8:", nucleus_filter(LOGITS, 0.8))
print("perplexity of a uniform four-way choice:", perplexity([0.25, 0.25, 0.25]))
rng = random.Random(7)
print("ten draws:", [sample(LOGITS, rng) for _ in range(10)])
'''}],
                "hints": [
                    "Scale first, then apply the max-subtraction trick — dividing by the temperature *after* subtracting the max changes the answer.",
                    "`sorted(range(len(logits)), key=lambda i: (-logits[i], i))` ranks indices by logit descending with a stable tie-break, which both filters need.",
                    "In `nucleus_filter`, stop as soon as the running mass *reaches* `p`; compare against `p - 1e-12` so that floating-point sums do not push you one token too far.",
                    "`sample_index` draws once, outside the loop. Drawing inside the loop is a different (and wrong) distribution.",
                ],
                "tests": [
                    {"name": "Greedy decoding", "code": r'''
assert greedy(LOGITS) == 0, f"The largest logit is index 0, got {greedy(LOGITS)!r}"
assert greedy([1.0, 5.0, 5.0, 2.0]) == 1, "A tie should keep the lowest index"
assert greedy([-3.0]) == 0, "One candidate is the winner"
assert greedy([INF, 0.0, 0.0]) == 1, "A masked-out logit can never win"
try:
    greedy([])
    assert False, "greedy([]) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Temperature reshapes the distribution", "code": r'''
_p = softmax([2.0, 1.0, 0.1, -1.0])
assert abs(sum(_p) - 1.0) < 1e-12, f"Probabilities must sum to 1, got {sum(_p)!r}"
assert abs(_p[0] - 0.6380663511479376) < 1e-12, f"At T=1 got {_p!r}"
_cold = softmax([2.0, 1.0, 0.1, -1.0], 0.1)
assert _cold[0] > 0.9999, f"A cold temperature should concentrate on the top logit, got {_cold!r}"
_hot = softmax([2.0, 1.0, 0.1, -1.0], 5.0)
assert _hot[0] < _p[0] and _hot[3] > _p[3], f"A hot temperature should flatten, got {_hot!r}"
_recovered = softmax(LOGITS)
for _got, _want in zip(_recovered, [0.5, 0.3, 0.15, 0.05]):
    assert abs(_got - _want) < 1e-12, f"softmax(log p) should give p back, got {_recovered!r}"
for _bad in (0.0, -1.0):
    try:
        softmax([1.0, 2.0], _bad)
        assert False, f"A temperature of {_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Top-k truncation", "code": r'''
_f = top_k_filter(LOGITS, 2)
assert sum(1 for x in _f if x != INF) == 2, f"Exactly two logits should survive, got {_f!r}"
assert _f[0] == LOGITS[0] and _f[1] == LOGITS[1], "The two largest are kept unchanged"
assert _f[2] == INF and _f[3] == INF, "The rest are masked out"
_p = softmax(_f)
assert _p[2] == 0.0 and _p[3] == 0.0, f"Masked logits must get exactly zero probability, got {_p!r}"
assert abs(_p[0] - 0.625) < 1e-12, f"0.5 / 0.8 is 0.625, got {_p[0]!r}"
assert top_k_filter(LOGITS, 4) == LOGITS and top_k_filter(LOGITS, 9) == LOGITS, \
    "A k at or beyond the vocabulary changes nothing"
assert top_k_filter(LOGITS, 1) != LOGITS, "k=1 must mask three of the four"
try:
    top_k_filter(LOGITS, 0)
    assert False, "k must be at least 1"
except ValueError:
    pass
'''},
                    {"name": "Nucleus truncation adapts to the mass", "code": r'''
for _p_val, _want in [(0.4, 1), (0.5, 1), (0.8, 2), (0.9, 3), (1.0, 4)]:
    _kept = sum(1 for x in nucleus_filter(LOGITS, _p_val) if x != INF)
    assert _kept == _want, f"nucleus_filter(p={_p_val}) kept {_kept} tokens, expected {_want}"
_flat = [0.0, 0.0, 0.0, 0.0]
assert sum(1 for x in nucleus_filter(_flat, 0.5) if x != INF) == 2, \
    "A flat distribution needs two of the four tokens to reach half the mass"
for _bad in (0.0, -0.1, 1.5):
    try:
        nucleus_filter(LOGITS, _bad)
        assert False, f"p={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Sampling is seeded, reproducible and correctly shaped", "code": r'''
_probs = [0.5, 0.3, 0.2]
_first = [sample_index(_probs, random.Random(7)) for _ in range(1)]
_rng = random.Random(7)
_draws = [sample_index(_probs, _rng) for _ in range(10)]
assert _draws == [0, 0, 1, 0, 1, 0, 0, 1, 0, 0], f"With Random(7) the first ten draws are fixed, got {_draws!r}"
_rng = random.Random(7)
_many = [sample_index(_probs, _rng) for _ in range(2000)]
for _i, _want in enumerate(_probs):
    _freq = _many.count(_i) / 2000
    assert abs(_freq - _want) < 0.03, f"token {_i} appeared {_freq:.3f} of the time, expected about {_want}"
assert sample_index([1.0], random.Random(1)) == 0, "A certain outcome is always chosen"
'''},
                    {"name": "sample composes the filters", "code": r'''
_rng = random.Random(7)
assert all(sample(LOGITS, _rng, top_k=1) == 0 for _ in range(20)), \
    "top_k=1 collapses sampling onto the argmax"
_rng = random.Random(7)
_drawn = {sample(LOGITS, _rng, top_p=0.8) for _ in range(200)}
assert _drawn <= {0, 1}, f"A nucleus of 0.8 admits only the top two tokens, saw {_drawn!r}"
assert _drawn == {0, 1}, f"Both admitted tokens should actually appear, saw {_drawn!r}"
_rng = random.Random(7)
_cold = {sample(LOGITS, _rng, temperature=0.01) for _ in range(50)}
assert _cold == {0}, f"A near-zero temperature is greedy in the limit, saw {_cold!r}"
'''},
                    {"name": "Perplexity", "code": r'''
assert abs(perplexity([0.25, 0.25, 0.25]) - 4.0) < 1e-12, \
    f"A uniform four-way choice has perplexity 4, got {perplexity([0.25, 0.25, 0.25])!r}"
assert abs(perplexity([0.5, 0.5]) - 2.0) < 1e-12, f"Got {perplexity([0.5, 0.5])!r}"
assert abs(perplexity([1.0, 1.0, 1.0]) - 1.0) < 1e-12, "A certain model is never surprised"
assert perplexity([0.9, 0.1]) > perplexity([0.9, 0.9]), "Worse predictions are more perplexing"
for _bad in ([], [0.5, 0.0], [0.5, -0.1]):
    try:
        perplexity(_bad)
        assert False, f"perplexity({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
    ],
    "capstone": {
        "title": "Capstone — a character-level transformer",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
Every piece of the course, assembled into one small language model that trains
and then writes. `engine.py` is the finished autodiff engine — read-only.
`tinygpt.py` is your model and is what the checks import. `main.py` builds the
corpus, trains, and generates under each decoding strategy.

## Plumbing

- `vsum(items)` — fold a list of `Value`s with `+`, starting from the first
  item rather than a synthetic zero.
- `Linear(nin, nout, rng)` — `nout` weight rows of `nin` draws from
  `rng.uniform(-scale, scale)` where `scale = 1 / √nin`, taken **row by row**,
  and `nout` biases initialised to `0.0`. Calling it returns `nout` `Value`s.
- `softmax_values(logits)` — softmax over `Value`s, max-subtracted, graph intact.
- `cross_entropy(logits, target)` — `log Σ exp(z) − z_target`, evaluated with
  the same max-subtraction. `ValueError` for a target outside the vocabulary.

## Model

- `Head(d_model, rng)` — one **causal** self-attention head: `query`, `key` and
  `value` projections constructed in that order, scores scaled by `1/√d_model`,
  and position `i` attending only to positions `0..i`.
- `TinyGPT(vocab_size, d_model, block_size, rng)` — built in this order so that
  the seeded draws line up: token embeddings, position embeddings (both
  `rng.uniform(-0.5, 0.5)`), `head`, `projection`, `fc1` (`d_model → 2*d_model`),
  `fc2` (`2*d_model → d_model`), `out` (`d_model → vocab_size`).

  The forward pass is: embed and add the position, attend, project, **add the
  residual**, ReLU-MLP, add the residual again, then the output head. It returns
  one logit row per input position, and raises `ValueError` for a context that
  is empty or longer than `block_size`.

  Also provide `parameters()`, `zero_grad()` and
  `loss(idxs, targets)` — the mean cross-entropy across the positions.

## Training and evaluation

- `make_dataset(text, block_size, stoi)` — every window of `block_size`
  characters paired with the same window shifted one to the right.
- `train(model, data, steps, lr)` — full-batch descent on the mean loss.
  Returns one loss per step.
- `perplexity(model, data)` — `exp` of the mean cross-entropy over every
  predicted position.

## Decoding

`softmax_floats`, `greedy`, `top_k_filter`, `nucleus_filter` and `sample_index`
are module 5's functions, over plain floats. `generate(model, ids, n_new,
strategy="greedy", rng=None, temperature=1.0, top_k=None, top_p=None)` extends
`ids`, always feeding the **last `block_size`** tokens and reading the logits of
the **last** position. `strategy="sample"` without an `rng` is a `ValueError`,
and so is any strategy other than `greedy` or `sample`.

## The target

`main.py` trains a 4-token vocabulary over `"abcdabcdabcdabcd"` with
`d_model = 4`, `block_size = 3`, four windows, 60 steps at `lr = 0.5`, seeded
`random.Random(7)`. That is 204 parameters, a loss falling from
`1.4931467840621315` to under `0.05`, a perplexity under `1.05`, and a greedy
continuation of `"abc"` that reads `"abcdabcdabc"`.
''',
        "deliverables": [
            "`tinygpt.py` — `Linear`, `Head`, `TinyGPT`, the loss, the training loop and the four decoders, importable with no output",
            "`main.py` — a demo that builds the corpus, trains, reports the loss curve and perplexity, and generates under each strategy",
            "A causal attention head whose output at position `i` provably ignores positions after `i`",
            "Residual connections around both the attention block and the MLP",
            "A training run that reaches the stated loss threshold from the stated seed, reproducibly",
            "Greedy, temperature, top-k and nucleus decoding all driving the same trained model",
        ],
        "constraints": [
            "Standard library only — `math` and `random` on top of the supplied `engine.py`",
            "`engine.py` is read-only: if a gradient is wrong, the defect is in your model",
            "Every random draw goes through the `rng` that was passed in — no module-level `random.*` calls",
            "`tinygpt.py` must define names only: importing it must print nothing and train nothing",
            "No `LayerNorm`, no optimiser beyond plain SGD — the point is that this much is enough",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 35,
             "evidence": "Every automated check passes, including the causality, shape and error-path cases."},
            {"criterion": "Training outcome", "weight": 25,
             "evidence": "From random.Random(7) the loss falls from 1.4931 to under 0.05 in 60 steps and the perplexity lands under 1.05."},
            {"criterion": "Generation quality", "weight": 20,
             "evidence": "Greedy decoding continues the corpus exactly; each sampling strategy is reproducible under a seeded rng."},
            {"criterion": "Architecture fidelity", "weight": 12,
             "evidence": "Causal masking, residual connections and the scaled dot product are all present and correctly placed."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "Docstrings on every public class and function, no dead code, no debug prints in tinygpt.py."},
        ],
        "hints": [
            "Build the model in exactly the documented order. Every constructor pulls from the same `rng`, so a swapped line changes every subsequent draw and the expected loss curve disappears.",
            "In `Head.__call__`, the causal mask is not a matrix — it is the loop bound. Score position `i` against `j` for `j in range(i + 1)` and there is nothing to mask.",
            "`vsum` exists so the graph stays small: `sum()` would start from an integer zero and add a node per term. Fold from `items[0]` instead.",
            "`cross_entropy` should never call `exp` on a raw logit. Subtract `max(v.data for v in logits)` first — that constant cancels in the ratio and keeps `exp` finite.",
            "In `generate`, slice the context with `out[-model.block_size:]` and read `model(context)[-1]`. Feeding the whole history, or reading row 0, both look plausible and both fail.",
        ],
        "files": [
            {"name": "engine.py", "ro": True, "content": ENGINE_SOURCE},
            {"name": "tinygpt.py", "content": r'''
import math
import random

from engine import Value

INF = float("-inf")


def vsum(items):
    """Fold a list of Values with +, starting from items[0]."""
    # your code here


class Linear:
    """An affine map from nin to nout, with weights drawn row by row."""

    def __init__(self, nin, nout, rng):
        self.nin = nin
        self.nout = nout
        # self.w: nout rows of nin draws from rng.uniform(-scale, scale)
        # self.b: nout biases at 0.0

    def __call__(self, x):
        pass

    def parameters(self):
        pass


def softmax_values(logits):
    """Softmax over Values, max-subtracted, graph intact."""
    # your code here


def cross_entropy(logits, target):
    """log sum exp(z) - z_target. ValueError for a target outside the vocabulary."""
    # your code here


class Head:
    """One causal self-attention head."""

    def __init__(self, d_model, rng):
        # query, key, value — constructed in that order — plus the 1/sqrt(d_model) scale
        pass

    def __call__(self, xs):
        pass

    def parameters(self):
        pass


class TinyGPT:
    """Embeddings, one causal head, one MLP, one output head."""

    def __init__(self, vocab_size, d_model, block_size, rng):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.block_size = block_size
        # token_embedding, position_embedding, head, projection, fc1, fc2, out

    def __call__(self, idxs):
        pass

    def parameters(self):
        pass

    def zero_grad(self):
        pass

    def loss(self, idxs, targets):
        pass


def make_dataset(text, block_size, stoi):
    """Windows of block_size characters paired with the window shifted by one."""
    # your code here


def train(model, data, steps, lr):
    """Full-batch descent on the mean loss. Returns one loss per step."""
    # your code here


def perplexity(model, data):
    """exp of the mean cross-entropy over every predicted position."""
    # your code here


def softmax_floats(logits, temperature=1.0):
    """Plain-float softmax. ValueError for a temperature at or below zero."""
    # your code here


def greedy(logits):
    """Index of the largest logit; lowest index on a tie."""
    # your code here


def top_k_filter(logits, k):
    """Everything outside the k largest logits becomes -inf."""
    # your code here


def nucleus_filter(logits, p):
    """Keep the shortest prefix of probability mass reaching p."""
    # your code here


def sample_index(probs, rng):
    """Inverse-transform sampling from one rng.random() draw."""
    # your code here


def generate(model, ids, n_new, strategy="greedy", rng=None,
             temperature=1.0, top_k=None, top_p=None):
    """Extend ids by n_new tokens under the chosen decoding strategy."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
import random

from tinygpt import TinyGPT, generate, make_dataset, perplexity, train

TEXT = "abcdabcdabcdabcd"
CHARS = sorted(set(TEXT))
STOI = {c: i for i, c in enumerate(CHARS)}
ITOS = {i: c for c, i in STOI.items()}
BLOCK_SIZE = 3
SEED_IDS = [STOI[c] for c in "abc"]

DATA = make_dataset(TEXT, BLOCK_SIZE, STOI)[:4]


def as_text(ids):
    return "".join(ITOS[i] for i in ids)


rng = random.Random(7)
model = TinyGPT(len(CHARS), 4, BLOCK_SIZE, rng)
LOSSES = train(model, DATA, steps=60, lr=0.5)

print("parameters:", len(model.parameters()))
print("loss:", round(LOSSES[0], 4), "->", round(LOSSES[-1], 6))
print("perplexity:", round(perplexity(model, DATA), 4))
print("greedy:      ", as_text(generate(model, SEED_IDS, 8)))
print("temperature: ", as_text(generate(model, SEED_IDS, 8, "sample", random.Random(11))))
print("hot:         ", as_text(generate(model, SEED_IDS, 8, "sample", random.Random(11), temperature=10.0)))
print("top-k=2:     ", as_text(generate(model, SEED_IDS, 8, "sample", random.Random(11), top_k=2)))
print("nucleus 0.9: ", as_text(generate(model, SEED_IDS, 8, "sample", random.Random(11), top_p=0.9)))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "tinygpt.py", "content": r'''
import math
import random

from engine import Value

INF = float("-inf")


def vsum(items):
    """Fold a list of Values with +, starting from items[0]."""
    total = items[0]
    for item in items[1:]:
        total = total + item
    return total


class Linear:
    """An affine map from nin to nout, with weights drawn row by row."""

    def __init__(self, nin, nout, rng):
        self.nin = nin
        self.nout = nout
        scale = 1.0 / math.sqrt(nin)
        self.w = [[Value(rng.uniform(-scale, scale)) for _ in range(nin)]
                  for _ in range(nout)]
        self.b = [Value(0.0) for _ in range(nout)]

    def __call__(self, x):
        return [vsum([self.b[j]] + [wi * xi for wi, xi in zip(row, x)])
                for j, row in enumerate(self.w)]

    def parameters(self):
        return [p for row in self.w for p in row] + self.b


def softmax_values(logits):
    """Softmax over Values, max-subtracted, graph intact."""
    top = max(v.data for v in logits)
    exps = [(v - top).exp() for v in logits]
    total = vsum(exps)
    return [e / total for e in exps]


def cross_entropy(logits, target):
    """log sum exp(z) - z_target. ValueError for a target outside the vocabulary."""
    if not 0 <= target < len(logits):
        raise ValueError(f"target {target} is outside the vocabulary")
    top = max(v.data for v in logits)
    exps = [(v - top).exp() for v in logits]
    return vsum(exps).log() - (logits[target] - top)


class Head:
    """One causal self-attention head."""

    def __init__(self, d_model, rng):
        self.query = Linear(d_model, d_model, rng)
        self.key = Linear(d_model, d_model, rng)
        self.value = Linear(d_model, d_model, rng)
        self.scale = 1.0 / math.sqrt(d_model)

    def __call__(self, xs):
        queries = [self.query(x) for x in xs]
        keys = [self.key(x) for x in xs]
        values = [self.value(x) for x in xs]
        out = []
        for i in range(len(xs)):
            scores = [vsum([q * k for q, k in zip(queries[i], keys[j])]) * self.scale
                      for j in range(i + 1)]
            weights = softmax_values(scores)
            out.append([vsum([weights[j] * values[j][d] for j in range(i + 1)])
                        for d in range(len(xs[0]))])
        return out

    def parameters(self):
        return self.query.parameters() + self.key.parameters() + self.value.parameters()


class TinyGPT:
    """Embeddings, one causal head, one MLP, one output head."""

    def __init__(self, vocab_size, d_model, block_size, rng):
        self.vocab_size = vocab_size
        self.d_model = d_model
        self.block_size = block_size
        self.token_embedding = [[Value(rng.uniform(-0.5, 0.5)) for _ in range(d_model)]
                                for _ in range(vocab_size)]
        self.position_embedding = [[Value(rng.uniform(-0.5, 0.5)) for _ in range(d_model)]
                                   for _ in range(block_size)]
        self.head = Head(d_model, rng)
        self.projection = Linear(d_model, d_model, rng)
        self.fc1 = Linear(d_model, 2 * d_model, rng)
        self.fc2 = Linear(2 * d_model, d_model, rng)
        self.out = Linear(d_model, vocab_size, rng)

    def __call__(self, idxs):
        if not 1 <= len(idxs) <= self.block_size:
            raise ValueError(
                f"a context of {len(idxs)} does not fit block_size {self.block_size}")
        xs = [[t + p for t, p in zip(self.token_embedding[i], self.position_embedding[k])]
              for k, i in enumerate(idxs)]
        attended = [self.projection(row) for row in self.head(xs)]
        xs = [[a + b for a, b in zip(row, delta)] for row, delta in zip(xs, attended)]
        hidden = [self.fc2([h.relu() for h in self.fc1(row)]) for row in xs]
        xs = [[a + b for a, b in zip(row, delta)] for row, delta in zip(xs, hidden)]
        return [self.out(row) for row in xs]

    def parameters(self):
        flat = [p for row in self.token_embedding for p in row]
        flat += [p for row in self.position_embedding for p in row]
        return (flat + self.head.parameters() + self.projection.parameters()
                + self.fc1.parameters() + self.fc2.parameters() + self.out.parameters())

    def zero_grad(self):
        for parameter in self.parameters():
            parameter.grad = 0.0

    def loss(self, idxs, targets):
        rows = self(idxs)
        terms = [cross_entropy(row, t) for row, t in zip(rows, targets)]
        return vsum(terms) * (1.0 / len(terms))


def make_dataset(text, block_size, stoi):
    """Windows of block_size characters paired with the window shifted by one."""
    data = []
    for i in range(len(text) - block_size):
        xs = [stoi[c] for c in text[i:i + block_size]]
        ys = [stoi[c] for c in text[i + 1:i + block_size + 1]]
        data.append((xs, ys))
    return data


def train(model, data, steps, lr):
    """Full-batch descent on the mean loss. Returns one loss per step."""
    losses = []
    for _ in range(steps):
        terms = [model.loss(xs, ys) for xs, ys in data]
        total = vsum(terms) * (1.0 / len(terms))
        model.zero_grad()
        total.backward()
        for parameter in model.parameters():
            parameter.data -= lr * parameter.grad
        losses.append(total.data)
    return losses


def perplexity(model, data):
    """exp of the mean cross-entropy over every predicted position."""
    total = 0.0
    count = 0
    for xs, ys in data:
        for row, target in zip(model(xs), ys):
            total += cross_entropy(row, target).data
            count += 1
    if count == 0:
        raise ValueError("no positions to score")
    return math.exp(total / count)


def softmax_floats(logits, temperature=1.0):
    """Plain-float softmax. ValueError for a temperature at or below zero."""
    if not logits:
        raise ValueError("softmax needs at least one logit")
    if temperature <= 0.0:
        raise ValueError("temperature must be positive")
    scaled = [x / temperature for x in logits]
    top = max(scaled)
    exps = [math.exp(x - top) for x in scaled]
    total = sum(exps)
    return [e / total for e in exps]


def greedy(logits):
    """Index of the largest logit; lowest index on a tie."""
    if not logits:
        raise ValueError("nothing to choose from")
    best = 0
    for i in range(1, len(logits)):
        if logits[i] > logits[best]:
            best = i
    return best


def top_k_filter(logits, k):
    """Everything outside the k largest logits becomes -inf."""
    if k < 1:
        raise ValueError("k must be at least 1")
    if k >= len(logits):
        return list(logits)
    ranked = sorted(range(len(logits)), key=lambda i: (-logits[i], i))
    keep = set(ranked[:k])
    return [logits[i] if i in keep else INF for i in range(len(logits))]


def nucleus_filter(logits, p):
    """Keep the shortest prefix of probability mass reaching p."""
    if not 0.0 < p <= 1.0:
        raise ValueError("p must lie in (0, 1]")
    probs = softmax_floats(logits)
    ranked = sorted(range(len(logits)), key=lambda i: (-probs[i], i))
    keep = set()
    running = 0.0
    for i in ranked:
        keep.add(i)
        running += probs[i]
        if running >= p - 1e-12:
            break
    return [logits[i] if i in keep else INF for i in range(len(logits))]


def sample_index(probs, rng):
    """Inverse-transform sampling from one rng.random() draw."""
    if not probs:
        raise ValueError("nothing to sample from")
    draw = rng.random()
    running = 0.0
    for i, prob in enumerate(probs):
        running += prob
        if draw < running:
            return i
    return len(probs) - 1


def generate(model, ids, n_new, strategy="greedy", rng=None,
             temperature=1.0, top_k=None, top_p=None):
    """Extend ids by n_new tokens under the chosen decoding strategy."""
    if strategy not in ("greedy", "sample"):
        raise ValueError("strategy must be greedy or sample")
    if strategy == "sample" and rng is None:
        raise ValueError("sampling needs a seeded rng")
    out = list(ids)
    for _ in range(n_new):
        context = out[-model.block_size:]
        logits = [v.data for v in model(context)[-1]]
        if strategy == "greedy":
            out.append(greedy(logits))
            continue
        if top_k is not None:
            logits = top_k_filter(logits, top_k)
        if top_p is not None:
            logits = nucleus_filter(logits, top_p)
        out.append(sample_index(softmax_floats(logits, temperature), rng))
    return out
'''},
            {"name": "main.py", "content": r'''
import random

from tinygpt import TinyGPT, generate, make_dataset, perplexity, train

TEXT = "abcdabcdabcdabcd"
CHARS = sorted(set(TEXT))
STOI = {c: i for i, c in enumerate(CHARS)}
ITOS = {i: c for c, i in STOI.items()}
BLOCK_SIZE = 3
SEED_IDS = [STOI[c] for c in "abc"]

DATA = make_dataset(TEXT, BLOCK_SIZE, STOI)[:4]


def as_text(ids):
    return "".join(ITOS[i] for i in ids)


rng = random.Random(7)
model = TinyGPT(len(CHARS), 4, BLOCK_SIZE, rng)
LOSSES = train(model, DATA, steps=60, lr=0.5)

print("parameters:", len(model.parameters()))
print("loss:", round(LOSSES[0], 4), "->", round(LOSSES[-1], 6))
print("perplexity:", round(perplexity(model, DATA), 4))
print("greedy:      ", as_text(generate(model, SEED_IDS, 8)))
print("temperature: ", as_text(generate(model, SEED_IDS, 8, "sample", random.Random(11))))
print("hot:         ", as_text(generate(model, SEED_IDS, 8, "sample", random.Random(11), temperature=10.0)))
print("top-k=2:     ", as_text(generate(model, SEED_IDS, 8, "sample", random.Random(11), top_k=2)))
print("nucleus 0.9: ", as_text(generate(model, SEED_IDS, 8, "sample", random.Random(11), top_p=0.9)))
'''},
        ],
        "tests": [
            {"name": "vsum and Linear", "code": r'''
import random as _random
from engine import Value
from tinygpt import Linear, vsum
_v = vsum([Value(1.0), Value(2.0), Value(4.0)])
assert _v.data == 7.0, f"vsum gave {_v.data!r}, expected 7.0"
_v.backward()
assert vsum([Value(3.0)]).data == 3.0, "A single item folds to itself"
_lin = Linear(3, 2, _random.Random(7))
assert len(_lin.w) == 2 and len(_lin.w[0]) == 3, "Two rows of three weights"
assert all(b.data == 0.0 for b in _lin.b), "Biases start at zero"
assert len(_lin.parameters()) == 8, f"2*(3+1) is 8 parameters, got {len(_lin.parameters())}"
_lin.w[0][0].data, _lin.w[0][1].data, _lin.w[0][2].data = 1.0, 2.0, 3.0
_lin.b[0].data = 0.5
_y = _lin([Value(1.0), Value(1.0), Value(1.0)])
assert len(_y) == 2, f"A 3->2 map returns two Values, got {len(_y)}"
assert abs(_y[0].data - 6.5) < 1e-12, f"0.5 + 1 + 2 + 3 is 6.5, got {_y[0].data!r}"
'''},
            {"name": "Cross-entropy and its gradient", "code": r'''
import math as _math
from engine import Value
from tinygpt import cross_entropy, softmax_values
_logits = [Value(0.0) for _ in range(4)]
_loss = cross_entropy(_logits, 2)
assert abs(_loss.data - _math.log(4.0)) < 1e-12, \
    f"Four equal logits give a loss of ln 4, got {_loss.data!r}"
_loss.backward()
assert abs(_logits[2].grad + 0.75) < 1e-12, f"The target gradient is p-1 = -0.75, got {_logits[2].grad!r}"
for _i in (0, 1, 3):
    assert abs(_logits[_i].grad - 0.25) < 1e-12, f"Other gradients are p = 0.25, got {_logits[_i].grad!r}"
_confident = cross_entropy([Value(10.0), Value(0.0)], 0)
assert _confident.data < 0.001, f"A confident correct logit is nearly free, got {_confident.data!r}"
_p = softmax_values([Value(0.0), Value(0.0)])
assert abs(_p[0].data - 0.5) < 1e-12, f"Two equal logits split evenly, got {_p[0].data!r}"
try:
    cross_entropy([Value(0.0), Value(0.0)], 5)
    assert False, "A target outside the vocabulary should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Model shape and context validation", "code": r'''
import random as _random
from tinygpt import TinyGPT
assert len(model.parameters()) == 204, \
    f"vocab 4, d_model 4, block 3 gives 204 parameters, got {len(model.parameters())}"
_rows = model([0, 1, 2])
assert len(_rows) == 3, f"One logit row per position, got {len(_rows)}"
assert len(_rows[0]) == 4, f"Each row has one logit per vocabulary entry, got {len(_rows[0])}"
assert len(model([0])) == 1, "A one-token context is legal"
for _bad in ([], [0, 1, 2, 3]):
    try:
        model(_bad)
        assert False, f"model({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Attention is causal", "code": r'''
_a = [v.data for v in model([0, 1, 2])[0]]
_b = [v.data for v in model([0, 3, 2])[0]]
assert _a == _b, f"Position 0 must not see position 1: {_a!r} vs {_b!r}"
_c = [v.data for v in model([0, 1, 2])[1]]
_d = [v.data for v in model([0, 1, 3])[1]]
assert _c == _d, "Position 1 must not see position 2"
_e = [v.data for v in model([3, 1, 2])[0]]
assert _e != _a, "Position 0 does depend on its own token"
'''},
            {"name": "The dataset is a shifted window", "code": r'''
from tinygpt import make_dataset
assert DATA[0] == ([0, 1, 2], [1, 2, 3]), f"Got {DATA[0]!r}"
assert DATA[3] == ([3, 0, 1], [0, 1, 2]), f"Got {DATA[3]!r}"
assert len(DATA) == 4, f"main.py trains on four windows, got {len(DATA)}"
assert make_dataset("abc", 3, STOI) == [], "A text no longer than the block has no windows"
assert len(make_dataset(TEXT, BLOCK_SIZE, STOI)) == len(TEXT) - BLOCK_SIZE, \
    "One window per position that still has a target"
'''},
            {"name": "Training reaches the target loss", "code": r'''
assert isinstance(LOSSES, list) and len(LOSSES) == 60, \
    f"train should return one loss per step, got {len(LOSSES) if isinstance(LOSSES, list) else LOSSES!r}"
assert abs(LOSSES[0] - 1.4931467840621315) < 1e-9, \
    f"From random.Random(7) the first loss is 1.4931467840621315, got {LOSSES[0]!r}"
assert LOSSES[-1] < 0.05, f"After 60 steps the loss should be under 0.05, got {LOSSES[-1]!r}"
assert LOSSES[-1] < LOSSES[0] / 50, "The loss should fall by well over an order of magnitude"
assert all(LOSSES[_i + 1] < LOSSES[_i] for _i in range(len(LOSSES) - 1)), \
    "On this problem every step should reduce the full-batch loss"
'''},
            {"name": "Perplexity of the trained model", "code": r'''
from tinygpt import perplexity
_ppl = perplexity(model, DATA)
assert _ppl < 1.05, f"An overfitted four-token cycle should be nearly certain, got {_ppl!r}"
assert _ppl > 1.0, f"Perplexity is never below 1, got {_ppl!r}"
'''},
            {"name": "Greedy decoding continues the corpus", "code": r'''
from tinygpt import generate
_ids = generate(model, SEED_IDS, 8)
assert len(_ids) == 11, f"Three seed tokens plus eight new is eleven, got {len(_ids)}"
assert as_text(_ids) == "abcdabcdabc", f"Greedy continuation was {as_text(_ids)!r}"
assert generate(model, SEED_IDS, 0) == SEED_IDS, "Zero new tokens returns the seed"
assert generate(model, SEED_IDS, 8) == _ids, "Greedy decoding is deterministic"
'''},
            {"name": "The sampling strategies", "code": r'''
import random as _random
from tinygpt import generate
_greedy = as_text(generate(model, SEED_IDS, 8))
assert as_text(generate(model, SEED_IDS, 8, "sample", _random.Random(11), top_k=1)) == _greedy, \
    "top_k=1 makes sampling greedy"
assert as_text(generate(model, SEED_IDS, 8, "sample", _random.Random(11))) == _greedy, \
    "A confident model at temperature 1 still follows the pattern"
_hot = as_text(generate(model, SEED_IDS, 12, "sample", _random.Random(11), temperature=10.0))
assert _hot != as_text(generate(model, SEED_IDS, 12)), \
    f"A temperature of 10 should break the pattern, got {_hot!r}"
assert _hot == as_text(generate(model, SEED_IDS, 12, "sample", _random.Random(11), temperature=10.0)), \
    "The same seed must reproduce the same sample"
assert set(_hot) <= set(CHARS), f"Sampling must stay inside the vocabulary, got {_hot!r}"
assert as_text(generate(model, SEED_IDS, 8, "sample", _random.Random(11), top_p=0.9)) == _greedy, \
    "A nucleus of 0.9 on a confident model leaves only the argmax"
'''},
            {"name": "generate refuses an unusable configuration", "code": r'''
from tinygpt import generate
try:
    generate(model, SEED_IDS, 4, "sample")
    assert False, "Sampling without an rng should raise ValueError"
except ValueError:
    pass
try:
    generate(model, SEED_IDS, 4, "beam")
    assert False, "An unknown strategy should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The decoding primitives behave", "code": r'''
import math as _math
import random as _random
from tinygpt import greedy, nucleus_filter, sample_index, softmax_floats, top_k_filter
_lg = [_math.log(0.5), _math.log(0.3), _math.log(0.15), _math.log(0.05)]
assert greedy(_lg) == 0 and greedy([1.0, 5.0, 5.0]) == 1, "argmax, lowest index on a tie"
assert abs(sum(softmax_floats(_lg)) - 1.0) < 1e-12, "Probabilities must sum to 1"
assert softmax_floats(_lg, 0.01)[0] > 0.9999, "A cold temperature concentrates"
assert sum(1 for x in top_k_filter(_lg, 2) if x != float("-inf")) == 2, "top-2 keeps two"
assert sum(1 for x in nucleus_filter(_lg, 0.8) if x != float("-inf")) == 2, "0.8 of the mass is two tokens"
assert sum(1 for x in nucleus_filter(_lg, 0.9) if x != float("-inf")) == 3, "0.9 of the mass is three"
_rng = _random.Random(7)
assert [sample_index([0.5, 0.3, 0.2], _rng) for _ in range(10)] == [0, 0, 1, 0, 1, 0, 0, 1, 0, 0], \
    "Inverse-transform sampling from Random(7) is fixed"
for _call in (lambda: softmax_floats(_lg, 0.0), lambda: top_k_filter(_lg, 0),
              lambda: nucleus_filter(_lg, 0.0), lambda: nucleus_filter(_lg, 1.5)):
    try:
        _call()
        assert False, "That configuration should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Training is reproducible and tinygpt.py is import-clean", "code": r'''
import random as _random
from tinygpt import TinyGPT, train
_first = train(TinyGPT(len(CHARS), 4, BLOCK_SIZE, _random.Random(7)), DATA, steps=3, lr=0.5)
_second = train(TinyGPT(len(CHARS), 4, BLOCK_SIZE, _random.Random(7)), DATA, steps=3, lr=0.5)
assert _first == _second, "Same seed, same data — the run must reproduce exactly"
assert _first == LOSSES[:3], f"The first three steps must match main.py's run, got {_first!r}"
_src = open("tinygpt.py").read()
assert "print(" not in _src, "tinygpt.py defines the model; printing belongs in main.py"
assert "random.random(" not in _src and "random.uniform(" not in _src, \
    "Every draw must go through the rng that was passed in"
assert "parameters:" in _out, "main.py should report the model it built"
'''},
        ],
    },
}
