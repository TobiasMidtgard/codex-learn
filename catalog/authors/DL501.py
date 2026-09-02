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
            "read": [
                {
                    "title": "One backward pass, every partial",
                    "minutes": 12,
                    "body": r'''
Suppose the network from the next module is in front of you: 41 numbers, and a loss that
comes out at 1.18. You want to know, for each of the 41, which way to turn it and by how
much. The direct route is to nudge one number, run the network again, and see where the
loss went — 41 extra forward passes for one step of training, 82 if you nudge both ways
for a cleaner reading. That is tolerable at 41. The models this course is heading toward
have a hundred million to a hundred billion of them, and a training run takes a million
steps. Nudging is out.

Reverse-mode automatic differentiation gets every one of those partial derivatives from
one forward pass and one backward pass, whatever the count. Here is the whole of it, on an
expression small enough to hold in your head.

## The expression, forwards

$$f = \tanh(a \cdot b + c), \qquad a = 2,\; b = -3,\; c = 10$$

Forwards, this is three steps. The product $e = a \cdot b = -6$. The sum $d = e + c = 4$.
Then $f = \tanh 4 = 0.999329$. Three intermediate numbers, each computed from the ones
before it. Draw them as boxes with arrows and you have a computation graph: $a$ and $b$
feed $e$, $e$ and $c$ feed $d$, $d$ feeds $f$.

## The same expression, backwards

Now ask the question we want answered: if $a$ moves by a small amount $\delta$, how far
does $f$ move?

Start at the far end instead. If $d$ moves by $\delta$, $f$ moves by $\tanh'(4)\,\delta$,
and since $\tanh' x = 1 - \tanh^2 x$ that slope is $1 - 0.999329^2 = 0.001341$. Call it
$f$'s sensitivity to $d$.

One step further back. $d = e + c$. If $c$ moves by $\delta$, $d$ moves by exactly
$\delta$ — the slope of a sum with respect to either input is 1 — and so $f$ moves by
$0.001341\,\delta$. The sensitivity to $c$ is the sensitivity to $d$ times the local slope,
which happens to be 1. The same holds for $e$: sensitivity $0.001341$.

One more. $e = a \cdot b$. If $a$ moves by $\delta$, $e$ moves by $b\,\delta = -3\delta$ —
the slope of a product with respect to one factor is the *other* factor. So $f$ moves by
$0.001341 \times (-3)\,\delta = -0.004023\,\delta$. And if $b$ moves by $\delta$, $e$ moves
by $a\,\delta = 2\delta$, so $f$ moves by $0.002682\,\delta$.

That is the chain rule, and notice the shape of what happened. We never asked "how does
$f$ depend on $a$" directly. We asked how $f$ depends on the node right next to it, then
multiplied by how *that* node depends on the node next to *it*, walking backwards one edge
at a time. Every node only ever needed its own local slope and the sensitivity that had
arrived from above. Nothing needed the whole formula.

```python
import math


class Value:
    def __init__(self, data, children=(), op=""):
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = tuple(children)
        self._op = op

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

    def tanh(self):
        t = math.tanh(self.data)
        out = Value(t, (self,), "tanh")

        def _backward():
            self.grad += (1.0 - t * t) * out.grad

        out._backward = _backward
        return out

    def backward(self):
        order, seen, stack = [], set(), [(self, False)]
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
                stack.append((child, False))
        self.grad = 1.0
        for node in reversed(order):
            node._backward()


a, b, c = Value(2.0), Value(-3.0), Value(10.0)
e = a * b
d = e + c
f = d.tanh()
f.backward()
print("f =", round(f.data, 6))
print("df/dd =", round(d.grad, 6), " df/de =", round(e.grad, 6), " df/dc =", round(c.grad, 6))
print("df/da =", round(a.grad, 6), " df/db =", round(b.grad, 6))
```

This prints `f = 0.999329`, then `0.001341` three times, then `-0.004023` and `0.002682` —
the numbers from the paragraph above, and the numbers the lab's "Gradients through a
hand-checked expression" test asserts to twelve decimal places.

## What a node has to remember

Look at what the code needed at each operation. `__mul__` built the output node and then
attached a small function — a closure — that knows one thing: push `out.grad` into each
input, scaled by the *other* input's value. `tanh` closed over `t` and knows to scale by
`1 - t*t`. The closure does not know what the expression is, where it sits in the graph,
or what lies downstream. It knows its own local derivative, and it reads the sensitivity
that arrived in `out.grad`.

That is the pattern for every operation in the engine, and each local rule comes from the
same nudge argument. For `exp`: $e^{x+\delta} = e^x e^\delta \approx e^x(1 + \delta)$, so
the slope is the output itself. For `log`: $\ln(x + \delta) \approx \ln x + \delta / x$,
slope $1/x$. For a constant power, $(x + \delta)^n \approx x^n + n x^{n-1}\delta$. For
`relu`, a nudge above zero passes straight through (slope 1) and below zero goes nowhere
(slope 0). Subtraction, division and negation get no closures of their own: $a - b$ is
$a + (-1 \cdot b)$ and $a / b$ is $a \cdot b^{-1}$, and the primitives already know what
to do.

## Two paths into one node

Here is where the picture earns its keep. Take $y = x + x$. Two arrows leave $x$ and both
arrive at $y$. Nudge $x$ by $\delta$ and $y$ moves by $\delta$ along the left arrow *and*
$\delta$ along the right one: $2\delta$ in total. Sensitivities along separate paths add.

In the code this is the `+=` in every closure. The `+` closure runs once, and inside it
`self` and `other` are the same object, so `self.grad += out.grad` and
`other.grad += out.grad` both land on `x` and the total is 2.

```python
class Value:
    def __init__(self, data, children=()):
        self.data = float(data)
        self.grad = 0.0
        self._backward = lambda: None
        self._prev = tuple(children)

    def __add__(self, other):
        out = Value(self.data + other.data, (self, other))

        def _backward():
            self.grad += out.grad
            other.grad += out.grad

        out._backward = _backward
        return out


x = Value(3.0)
y = x + x
y.grad = 1.0
y._backward()
print("with +=  d(x+x)/dx =", x.grad)

x = Value(3.0)
y = x + x
y.grad = 1.0
y._backward = lambda: setattr(x, "grad", y.grad)   # the overwrite version
y._backward()
print("with  =  d(x+x)/dx =", x.grad)
```

The first line reads `2.0`; the second, `1.0`.

The mistake people make is to write `self.grad = out.grad`. It is tempting because that is
what a closure looks like it should do — compute the gradient of its input and store it —
and it is correct on every expression where each node is used once, which is every
expression you will check by hand. It fails the first time a node is reused, and in a
network *every weight is reused*: a weight takes part in the forward pass of every example
in the batch, so the batch loss has one path into that weight per example. Overwrite
instead of accumulate, and the weight only ever hears from the last example. The lab's
"Reused nodes accumulate rather than overwrite" test exists because of this.

## Why the order matters

Consider $c = a \cdot b$ and $d = c + a$, then `d.backward()`. Node $d$'s closure delivers
sensitivity to $c$ and to $a$. Node $c$'s closure then delivers $c$'s sensitivity, times
$b$, to $a$, and times $a$ to $b$. Had $c$'s closure run *first*, it would have spent
`c.grad` while it was still zero and pushed nothing anywhere.

The rule that falls out: a node's closure may run only once every node that depends on it
has finished adding into its `grad`. That is a reverse topological order of the graph, and
`backward()` obtains it by listing the nodes children-before-parents and walking that list
backwards. The listing uses an explicit stack rather than recursion, because a graph is as
deep as the longest chain of operations in it, and a recursive walk over a chain of ten
thousand additions hits Python's recursion limit long before it hits anything
mathematical.

```text
order (children first):  a   b   c=a*b   d=c+a
walk in reverse:         d  ->  c.grad = 1,  a.grad = 1
                         c  ->  a.grad += b * 1,  b.grad += a * 1
```

There is a second rule in the lab, and it is the flip side of `+=`: `backward()` does not
clear anything. Call it twice on $x \cdot x$ at $x = 3$ and `x.grad` reads 12, not 6,
because the second pass added into what the first left behind. That is not an oversight.
A training loop is the thing that decides when a gradient is finished with, and it zeroes
the fields itself — module 2 is built around exactly that line.

## An oracle that owes the engine nothing

Everything above is an argument. The way to find out whether your engine agrees with the
argument is to measure the slope by nudging, which is the one thing you can do without
trusting any of the closures.

The first estimate anyone reaches for is $(f(x+h) - f(x)) / h$. Expand $f(x + h)$ as a
Taylor series, $f(x) + h f'(x) + \tfrac{h^2}{2} f''(x) + \dots$, subtract $f(x)$ and
divide by $h$, and what is left is $f'(x) + \tfrac{h}{2} f''(x) + \dots$: the error is
proportional to $h$. Now do the same with $f(x - h)$, which has the same expansion with
the sign of every odd power flipped. Subtract the two expansions and the even powers
cancel: $f(x+h) - f(x-h) = 2h f'(x) + \tfrac{h^3}{3} f^{(3)}(x) + \dots$. Divide by $2h$ and
the error is proportional to $h^2$. That is the central difference, and it is why the lab
uses it.

```python
import math


def f(a, b, c):
    return math.tanh(a * b + c)


a, b, c = 2.0, -3.0, 10.0
analytic = (1.0 - math.tanh(a * b + c) ** 2) * b
print("chain rule says df/da =", analytic)
for h in (1e-1, 1e-3, 1e-5, 1e-8, 1e-12):
    forward = (f(a + h, b, c) - f(a, b, c)) / h
    central = (f(a + h, b, c) - f(a - h, b, c)) / (2 * h)
    print(f"h = {h:<6g} forward error {abs(forward - analytic):.1e}   central error {abs(central - analytic):.1e}")
```

At $h = 10^{-3}$ the central estimate is off by $2.4 \times 10^{-8}$ against
$1.2 \times 10^{-5}$ for the one-sided one — five hundred times better — and at
$h = 10^{-5}$ it agrees with the chain rule to within $2.4 \times 10^{-12}$. Then the
table turns around. At $h = 10^{-12}$ both estimates are off by $2.6 \times 10^{-5}$,
*worse* than they were at $h = 0.1$, because $f(x+h)$ and $f(x-h)$ now agree in their
first eleven or twelve digits, subtracting them leaves three or four significant digits
behind, and dividing by $2 \times 10^{-12}$ magnifies what remains. Truncation error
falls with $h$, rounding error rises, and $10^{-5}$ is near where the two cross for a
double. The lab's gradient check uses that $h$ on a nastier composite expression and asks
for agreement within $10^{-6}$; you should see something around $10^{-9}$.

## Where the picture stops holding

A derivative is a slope, and a slope needs a smooth curve. `relu` has a corner at zero:
from the left the slope is 0 and from the right it is 1, and there is no single number at
the point itself. The engine returns 0 there because `out.data > 0.0` is false, which is
a decision rather than a fact; a finite difference straddling the corner reports 0.5, and
neither is wrong, because the question has no answer. In practice a weight lands on
exactly 0.0 about never, and the choice does not matter — but if a gradient check
disagrees with the engine at a corner, this is why.

The other limit is memory. The forward pass keeps every intermediate node alive until the
backward pass has read it, because each closure needs the values it closed over. On the
41-parameter network of the next module that is nothing. On a model with a billion
parameters and a batch of a thousand it is the dominant cost, and it is why the tensor
libraries you will eventually use do exactly this bookkeeping on whole arrays at a time
instead of one scalar per node. The graph is the same; the boxes are bigger.

In the lab, "A scalar autodiff engine", you build the class this reading walked through:
the three primitives with their closures, the unary functions, the composite operators as
one-line rewrites, an iterative `topological_order`, and `backward`. The last test is the
central-difference oracle from above, and it is the one to believe when the others
disagree.
''',
                },
            ],
            "quiz": {
                "title": "What the backward pass owes each node",
                "minutes": 8,
                "questions": [
                    {
                        "q": "For $f = \\tanh(a \\cdot b + c)$ with $a = 2$, $b = -3$, $c = 10$, the engine reports `a.grad = -0.004023` while `c.grad = 0.001341`. Where does the factor of $-3$ between them come from?",
                        "opts": [
                            "It is `b.data`: a nudge to `a` reaches the product scaled by the other factor, then passes through the same tanh slope as `c`",
                            "It is the slope of tanh at 4, which is negative there because tanh has passed its inflection point and is bending back down",
                            "It is `a.data` divided by `b.data`: the product rule splits the arriving gradient between its two inputs in proportion to their values",
                            "It is one sign flip per edge: `a` is three edges from `f` while `c` is two, and each hop through the graph multiplies by $-1$",
                        ],
                        "a": 0,
                        "whys": [
                            r"The product rule's local slope with respect to one factor is the other factor, so the $0.001341$ arriving at $e$ is multiplied by $b = -3$ on its way to $a$.",
                            r"The slope of tanh is $1 - \tanh^2 x$, which is never negative — it is $0.001341$ at 4, and it is the same factor for `a` and `c` alike. The sign comes from the product below it, not from tanh.",
                            r"Nothing is split. Each input of a product receives the *whole* arriving gradient scaled by the other input; `b.grad` came out as $0.001341 \times 2$, not as a share of something.",
                            r"Edges carry local slopes, not sign flips. The `+` edge from $e$ to $d$ has slope 1, the tanh edge has slope $0.001341$, and only the product edge carries a factor of $-3$ — which is the value of $b$, not a count of hops.",
                        ],
                        "why": r"""
Walk backwards. $f$'s sensitivity to $d$ is $1 - \tanh^2 4 = 0.001341$. The sum passes
that through unchanged to both $e$ and $c$. The product $e = a \cdot b$ then scales it
by the *other* factor on the way to each input: $b = -3$ for `a`, giving $-0.004023$,
and $a = 2$ for `b`, giving $0.002682$. The $-3$ is a value that happened to be in the
graph, not a property of tanh or of the number of edges.
""",
                    },
                    {
                        "q": "`y = x + x` followed by `y.backward()` leaves `x.grad == 1.0` instead of 2. Which defect produces that number?",
                        "opts": [
                            "The `+` closure writes `self.grad = out.grad`, so the second path into `x` overwrites what the first delivered",
                            "`topological_order` listed `x` twice, so its own closure ran twice and the second run reset what the first had done",
                            "`backward()` seeded `y.grad = 1.0` but never divided that seed between the two edges that lead down to `x`",
                            "`__add__` wrapped the second `x` in a fresh `Value`, so half the gradient went to a copy that nothing else can see",
                        ],
                        "a": 0,
                        "whys": [
                            r"Two edges arrive at `x`, each carrying 1, and `=` keeps only the last to arrive. `+=` is the whole fix.",
                            r"A leaf has no closure worth running — `x._backward` is the do-nothing lambda — and `topological_order` de-duplicates on `id(node)`, so `x` appears once. The number 1.0 comes from an overwrite, not a repeat.",
                            r"The seed is not divided along edges; it is *copied* along every edge that leaves the node, because a sum's slope with respect to each input is 1. Two edges, two contributions of 1, total 2 — provided they are added.",
                            r"`x` is already a `Value`, so `__add__` uses it as is on both sides; `self` and `other` are the same object. There is no copy, which is exactly why both `+=` lines land on the one `grad` field.",
                        ],
                        "why": r"""
Nudge `x` by $\delta$ and `y` moves by $\delta$ along each of two edges, so the
sensitivity is 2. In the closure, `self` and `other` are the same object; with `+=`
the two lines add 1 and 1, with `=` the second assignment replaces the first and the
answer is 1. Every reused node in a network — every weight, once per example in the
batch — fails the same way with the same symptom.
""",
                    },
                    {
                        "q": "Why must the closures run in *reverse topological* order rather than in the order the nodes were created?",
                        "opts": [
                            "A closure spends `out.grad`, which is complete only once every node that depends on `out` has added its own share",
                            "Creation order starts at the leaves, and a leaf's closure has nothing to push because a leaf has no children below it",
                            "The closures must run from the leaves toward the output so that the seed of 1.0 reaches every parameter first",
                            "Creation order is lost once a node is reused, so the topological walk exists to reconstruct the sequence of operations",
                        ],
                        "a": 0,
                        "whys": [
                            r"Run $c$'s closure before $d$'s in $d = a \cdot b + a$ and it multiplies a `c.grad` of zero. Order is about completeness of what is spent, not about where the walk starts.",
                            r"That is true and beside the point. The leaves' closures are harmless whenever they run; the danger is an *interior* node whose closure runs before all of its consumers have delivered. Creation order guarantees nothing about that.",
                            r"Backwards from the output is the direction, and this describes the opposite one. The seed is planted on the output and flows *down* to the parameters; it does not need to reach them before anything else runs.",
                            r"Creation order is never lost — a node's children are fixed at construction. The ordering problem is not reconstructing what happened; it is scheduling the closures so that no gradient is read before it is finished.",
                        ],
                        "why": r"""
Each closure reads its output's accumulated gradient and pushes it down. If any consumer
of that output has not yet run, the number being read is incomplete, and whatever is
pushed down is wrong by the missing share. Listing the graph children-before-parents and
walking it in reverse guarantees every consumer has run first. Creation order happens to
coincide with topological order for a straight-line expression, which is why the defect
hides until a graph has a reused node.
""",
                    },
                    {
                        "q": "With $h = 10^{-3}$ the one-sided estimate $(f(x+h) - f(x))/h$ is off by $1.2 \\times 10^{-5}$ while $(f(x+h) - f(x-h))/2h$ is off by $2.4 \\times 10^{-8}$. Why is the central one so much better?",
                        "opts": [
                            "Its error term is proportional to $h^2$: the $h f''$ term of the two Taylor expansions cancels when they are subtracted",
                            "It evaluates the function twice, so its rounding errors are averaged and its error halves at every step size",
                            "The one-sided version is biased upward wherever the function is increasing, and the central one has no bias for any function",
                            "It uses a step of $2h$, and the wider gap keeps the two function values from cancelling each other's digits",
                        ],
                        "a": 0,
                        "whys": [
                            r"Odd powers of $h$ flip sign between $f(x+h)$ and $f(x-h)$, even powers do not — so subtracting kills the $h^2 f''$ term and the leading error becomes $\tfrac{h^2}{6} f^{(3)}$.",
                            r"Both estimates evaluate the function twice — the one-sided one uses $f(x)$ and $f(x+h)$. Rounding is the *same* in both; what differs is the truncation term, and it differs by a power of $h$, not a factor of two.",
                            r"The one-sided estimate's bias is $\tfrac{h}{2} f''(x)$, which depends on the second derivative, not on whether the function is increasing. And the central estimate is not unbiased — its bias is $\tfrac{h^2}{6} f^{(3)}(x)$, which is smaller, not absent.",
                            r"A wider gap on its own would make the truncation error *worse*, not better — the one-sided estimate with step $2h$ has twice the error. The improvement comes from symmetry about $x$, not from the width.",
                        ],
                        "why": r"""
Expand both $f(x+h)$ and $f(x-h)$. The terms in $h^2 f''$ have the same sign in both and
vanish when one is subtracted from the other, while the $h f'$ terms have opposite signs
and add. What survives after dividing by $2h$ is $f'(x)$ plus a term in $h^2 f^{(3)}$. The
one-sided estimate keeps the $h f''/2$ term, so its error is a thousand times larger at
$h = 10^{-3}$ — a ratio the table shows as five hundred, because the third derivative
is not the same size as the second.
""",
                    },
                    {
                        "q": "Shrinking $h$ from $10^{-5}$ to $10^{-12}$ makes the central-difference error *worse*, from $2.4 \\times 10^{-12}$ to $2.6 \\times 10^{-5}$. What is going on?",
                        "opts": [
                            "Subtracting two nearly equal doubles leaves only a few significant digits, and dividing by a tiny $h$ magnifies that loss",
                            "The truncation error grows again below a certain $h$, because the Taylor series stops converging for very small steps",
                            "At $10^{-12}$ the nudge is below the double's resolution, so $f(x+h)$ and $f(x-h)$ are the same number and the estimate is zero",
                            "The analytic gradient carries the error: at tiny $h$ the finite difference becomes exact and exposes the engine's rounding",
                        ],
                        "a": 0,
                        "whys": [
                            r"Truncation error falls with $h$, rounding error climbs as $1/h$, and $10^{-5}$ is near where the two cross for a double.",
                            r"The Taylor series of $\tanh$ converges for any step, and the truncation term $\tfrac{h^2}{6} f^{(3)}$ only gets *smaller* as $h$ shrinks. The thing that grows is not truncation — it is the rounding error in the subtraction, which scales like $\epsilon / h$.",
                            r"Doubles near 2 are spaced about $4 \times 10^{-16}$ apart, so a nudge of $10^{-12}$ does move the argument and the two function values do differ. They differ in only their last three or four digits, which is the problem — the estimate is noisy, not zero.",
                            r"The chain rule value is computed from $\tanh 4$ and $b$ with two roundings; it is good to about $10^{-16}$. The finite difference at $h = 10^{-12}$ is the one that has lost eleven digits to cancellation.",
                        ],
                        "why": r"""
$f(x+h)$ and $f(x-h)$ are both about $0.9993$ and agree in their first eleven digits
when $h = 10^{-12}$. Their difference keeps only the digits where they disagree — three
or four of them — and dividing by $2 \times 10^{-12}$ scales that noise up by
$5 \times 10^{11}$. The total error is roughly $h^2$ from truncation plus
$\epsilon / h$ from rounding, with $\epsilon \approx 10^{-16}$; the sum is smallest
around $h \approx 10^{-5}$, which is why the lab uses that value.
""",
                    },
                    {
                        "q": "Calling `backward()` twice on the same graph doubles every gradient. Is that a defect in the engine?",
                        "opts": [
                            "No: `backward` accumulates by design, and the training loop is responsible for zeroing gradients before each pass",
                            "Yes: `backward` should reset every `grad` to zero before seeding, so that one call always means one gradient",
                            "No: the second call is correct because the second call rebuilt the whole graph, and both copies then contribute",
                            "Yes: the topological order should be cached after the first call, so a second pass finds nothing left to push",
                        ],
                        "a": 0,
                        "whys": [
                            r"The `+=` that makes reused nodes correct also adds across calls; the loop that owns the parameters decides when to clear them.",
                            r"If `backward` cleared gradients itself, a loop that accumulates over several small batches before stepping — a common thing to want — would be impossible, and the engine would be making a policy decision that belongs to the caller. The lab's test asserts 12, not 6.",
                            r"`backward()` builds nothing. It walks the graph that the forward pass already built; there is one copy of the graph, and the second walk adds into the same `grad` fields the first one filled.",
                            r"Caching the order would not change what the closures do, and the closures are the part that accumulates. A second pass that pushed nothing would silently drop the gradient contribution of any later forward pass — which is worse than doubling.",
                        ],
                        "why": r"""
`backward()` seeds 1.0 and runs the closures, and every closure adds. Nothing in the
engine subtracts or resets, and that is deliberate: the same `+=` that makes a reused
node correct within one pass makes two passes accumulate. The training loop in module 2
calls `zero_grad()` before `backward()` on every step, and forgetting that line is the
mistake this behaviour exists to make visible.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "A weighted vote, and a walk downhill",
                    "minutes": 11,
                    "body": r'''
Four rows of three numbers, and a label on each:

```text
[2.0,  3.0, -1.0]   ->  +1
[3.0, -1.0,  0.5]   ->  -1
[0.5,  1.0,  1.0]   ->  -1
[1.0,  1.0, -1.0]   ->  +1
```

The job is a machine that reads a row and produces a number near $+1$ for the first and
last rows and near $-1$ for the middle two. That is the whole of this module's lab, and
everything below exists to make it happen.

## One neuron is a weighted vote

Think of the three inputs as three advisors, each shouting a number. You do not trust them
equally, so you give each a weight $w_i$ and add up the weighted votes. You also have a
threshold of your own, $b$, that shifts the total before you decide. The decision is

$$z = b + w_1 x_1 + w_2 x_2 + w_3 x_3$$

which can be any real number, and the labels are $\pm 1$. So squash it: $\tanh z$ lives
in $(-1, 1)$, is about $z$ itself near zero, and flattens toward $\pm 1$ far from it. That
squashed value is the neuron's output, and `Neuron.__call__` in the lab computes exactly
this — the bias first, then each `weight * value` folded in, then the activation.

With four parameters you could find a working set by hand. The point of what follows is a
procedure that finds them when there are forty-one, or forty-one million.

## Layers, and why the squash is not optional

Four neurons reading the same three inputs give four outputs; that is a `Layer(3, 4)`.
Feed those four numbers to another four neurons, then to a single output neuron, and you
have `MLP([3, 4, 4, 1])`. Count what it has to learn:

```python
sizes = [3, 4, 4, 1]
total = 0
for nin, nout in zip(sizes, sizes[1:]):
    layer = nout * (nin + 1)
    total += layer
    print(f"{nin} -> {nout}: {nout} neurons x ({nin} weights + 1 bias) = {layer}")
print("total:", total)
```

That prints 16, 20 and 5, and a total of 41 — the number the lab's "Layers and networks
flatten their parameters" test expects from `model.parameters()`.

Now suppose you left the activation out — `activation="linear"` everywhere. The first
layer computes $W_1 x + b_1$; the second computes $W_2(W_1 x + b_1) + b_2$, which is
$(W_2 W_1)\,x + (W_2 b_1 + b_2)$. That is one affine map with a $4 \times 3$ matrix and
a 4-vector — nothing a single `Layer(3, 4)` could not have done, and the same collapse
happens again at the next layer. Stacking linear layers buys width and nothing else. The
tanh between them is what makes the second layer able to compute something the first
could not, and it is why every hidden layer in the lab defaults to it.

## One number to be wrong by

Training needs a single measure of how wrong the whole network is, across all four rows.
Take each prediction's distance from its label, square it so that a miss in either
direction counts and big misses count more, and average:

$$L = \frac{1}{n}\sum_{i=1}^{n}\,(\hat y_i - y_i)^2$$

Two decisions are hiding in that line. It is a *mean* rather than a sum so that the size
of the gradient — and therefore the right learning rate — does not change when the batch
does. And it is *one* `Value`, not a list of four, because `backward()` in module 1 seeds
exactly one node with 1.0 and pushes from there. A list of losses has no single "how much
does the whole thing move"; the mean gives it one. `mse_loss` in the lab returns that one
node, with the graph of all four forward passes hanging beneath it.

## The step, derived

From module 1 you can get $\partial L / \partial p$ for every parameter $p$ in one backward
pass. Collect them into a vector $g$. What should you do with it?

Move all the parameters by a small vector $\Delta$. To first order,
$L(p + \Delta) \approx L(p) + g \cdot \Delta$. To make $L$ fall as fast as possible for a
given size of $\Delta$, point $\Delta$ straight against $g$: $\Delta = -\eta\, g$ for some
small $\eta > 0$. Then $L$ changes by about $-\eta\,|g|^2$, which is negative whenever the
gradient is not zero. That is the whole of gradient descent: `p.data -= lr * p.grad` for
every parameter, with $\eta$ written as `lr`.

The approximation is only good while $\Delta$ is small enough that the loss surface looks
flat, which is the condition the learning rate has to satisfy. Watch it on a case small
enough to follow with a pencil.

## The walk, with the numbers on show

One linear neuron, one input $x = 2$, one target $y = 3$, starting at $w = 0.5$, $b = 0$.
The prediction is $wx + b = 1$, so $L = (1 - 3)^2 = 4$. The chain rule gives
$\partial L/\partial \hat y = 2(\hat y - y) = -4$, then $\partial L/\partial w = -4 \cdot x
= -8$ and $\partial L/\partial b = -4$. With $\eta = 0.05$ the step is $w \leftarrow 0.5
+ 0.4 = 0.9$ and $b \leftarrow 0 + 0.2 = 0.2$, and the new prediction is $1.8 + 0.2 =
2.0$.

```python
x, y = 2.0, 3.0
w, b, lr = 0.5, 0.0, 0.05
for step in range(1, 4):
    pred = w * x + b
    loss = (pred - y) ** 2
    d_pred = 2 * (pred - y)
    d_w, d_b = d_pred * x, d_pred
    print(f"step {step}: pred={pred:.3f} loss={loss:.4f} dw={d_w:.2f} db={d_b:.2f}")
    w -= lr * d_w
    b -= lr * d_b
print(f"after 3 steps: w={w:.3f} b={b:.3f} pred={w * x + b:.3f}")
```

The loss goes 4, 1, 0.25, and the prediction 1, 2, 2.5, 2.75. Each step closes exactly
half the remaining gap, and you can see why: write the error as $e = \hat y - y$. One step
changes $w$ by $-2\eta e x$ and $b$ by $-2\eta e$, so the prediction changes by
$-2\eta e (x^2 + 1)$ and the new error is $e\,(1 - 2\eta(x^2 + 1)) = e\,(1 - 10\eta)$.
At $\eta = 0.05$ that factor is $0.5$; the error halves and the squared error quarters.

## What the learning rate does

The same factor, $1 - 10\eta$, says what every other learning rate does on this problem.

```python
x, y = 2.0, 3.0
for lr in (0.05, 0.1, 0.2, 0.3):
    w, b = 0.5, 0.0
    losses = []
    for _ in range(4):
        pred = w * x + b
        losses.append(round((pred - y) ** 2, 4))
        d_pred = 2 * (pred - y)
        w -= lr * d_pred * x
        b -= lr * d_pred
    print(f"lr = {lr:<5}", losses)
```

At $0.1$ the factor is $0$ and the loss is exactly zero after one step. At $0.2$ the
factor is $-1$: the step overshoots the minimum by precisely the distance it started
from, the error flips sign with the same size, and the loss reads 4 for ever. At $0.3$
the factor is $-2$ and the loss quadruples every step: 4, 16, 64, 256. Too small and you
crawl; too large and you oscillate or diverge; and the threshold is set by the curvature
of the loss — $x^2 + 1$ here — which on a real network is different in every direction
and not known in advance. That is why the learning rate is found by trying, and why the
lab's $0.05$ on the 41-parameter network is a value that was found to work: it takes
the loss from 1.18 to about 0.011 in a hundred epochs, and a larger one does not.

## The mistake, and why it looks right

Every closure in the engine *adds* into `grad`. That made reused nodes correct in module
1, and it has a consequence here: nothing ever subtracts. If the training loop does not
zero the gradients before `backward()`, the second epoch's gradient lands on top of the
first, the third on top of both, and the step applied at each epoch is the sum of every
gradient so far.

```python
x, y = 2.0, 3.0
w, b, lr = 0.5, 0.0, 0.05
gw = gb = 0.0
for step in range(1, 9):
    pred = w * x + b
    d_pred = 2 * (pred - y)
    gw += d_pred * x
    gb += d_pred
    w -= lr * gw
    b -= lr * gb
    print(f"step {step}: loss={(pred - y) ** 2:8.4f}   stored dw={gw:8.3f}")
```

The first three steps look identical to the correct run — 4, 1, 0.25 — because the
accumulated gradient happens to keep pointing the right way. Then the stored gradient
keeps pushing after the error has changed sign: step 4 is back at 3.06, step 5 at 4.52,
step 7 reads 0.0010 and looks converged, and step 8 is at 1.93 again. The loop never
settles, because it is applying a momentum that nothing ever damps.

This is the mistake people make, and it is tempting because `backward()` looks like the
thing that *computes* the gradient, so the field ought to hold the current one after it
runs. It holds the running total. The lab's `train` therefore does, in this order:
forward, build the loss, `model.zero_grad()`, `loss.backward()`, step. Zeroing *after*
`backward()` erases exactly the numbers you were about to use, which is a different way
to write the same wrong loop.

## Where the picture stops holding

The tanh that made the output match the labels has a cost. Its slope is $1 - \tanh^2 z$,
and far from zero that is almost nothing:

```python
import math

for z in (0.0, 1.0, 2.0, 4.0, 8.0):
    t = math.tanh(z)
    print(f"z = {z:3}: tanh = {t:.5f}   slope 1 - tanh^2 = {1 - t * t:.5f}")
```

At $z = 4$ the slope is $0.00134$; at $z = 8$ it prints as zero. A neuron whose
pre-activation sits out there passes almost no gradient back to its weights, however
wrong its output is, and it stops learning. That is why the weights start small — the lab
draws them from `uniform(-1, 1)` — and why inputs should be of order one: feed this
network rows in the hundreds and every neuron is saturated at birth.

Two more edges. Squared error on $\pm 1$ labels works on four points, but for a
classifier with many classes the loss of choice is cross-entropy, which the capstone
uses, because its gradient does not vanish when a confident prediction is wrong. And
the lab's loop is *full-batch*: every epoch sees all four rows. On a dataset of a million
rows one would take a random handful per step — the "stochastic" in stochastic gradient
descent — which makes each step a noisy estimate of the true gradient. That noise is
tolerated because it is cheap, and it turns out to help, but it is not what you are
building here.

In the lab, "Training an MLP by hand", you write `Neuron`, `Layer` and `MLP` on top of
the engine, `mse_loss` as one differentiable scalar, and the five-line `train` loop with
its zero-forward-backward-step order. Seeded with `random.Random(7)`, the first loss must
come out at exactly 1.1845288187388343 — which it will only if the weights are drawn in
the documented order — and the hundredth below 0.05, with all four predictions on the
correct side of zero.
''',
                },
            ],
            "quiz": {
                "title": "Why the loss goes where it goes",
                "minutes": 8,
                "questions": [
                    {
                        "q": "`MLP([3, 4, 4, 1])` has 41 parameters. Which accounting produces that number?",
                        "opts": [
                            "One weight per input plus one bias for every neuron: $4(3+1) + 4(4+1) + 1(4+1)$, which is 41",
                            "One bias per layer rather than per neuron: $12 + 16 + 4$ weights and 3 biases, which is 35",
                            "Every unit including the inputs owns a weight and a bias: $3 + 4 + 4 + 1$ units, twice over, is 24",
                            "Weights alone, since a bias that starts at 0.0 is not a trainable value: $12 + 16 + 4$, which is 32",
                        ],
                        "a": 0,
                        "whys": [
                            r"16, 20 and 5: each neuron in a layer reads every output of the previous one and adds its own bias.",
                            r"The bias is per *neuron*, not per layer — each of the four neurons in a hidden layer has its own threshold. Three biases would give 35 and the test expects 41.",
                            r"Inputs are not units with parameters; they are the numbers being read. Parameters belong to neurons, and a neuron's count is its input width plus one.",
                            r"Starting at 0.0 says nothing about whether a value is trained. The bias is a `Value` in `parameters()`, it receives gradient, and it moves; the lab's `Neuron.parameters()` returns weights followed by the bias.",
                        ],
                        "why": r"""
A layer from $n_{in}$ to $n_{out}$ has $n_{out}$ neurons, each with $n_{in}$ weights
and one bias: $n_{out}(n_{in} + 1)$. For $[3, 4, 4, 1]$ that is $16 + 20 + 5 = 41$.
Biases are per neuron, inputs own nothing, and a value that starts at zero is still a
parameter if gradient reaches it.
""",
                    },
                    {
                        "q": "Build the three-layer network with `activation=\"linear\"` on every layer. What can it compute?",
                        "opts": [
                            "What one affine map from 3 inputs to 1 output computes, because composed affine maps collapse into one",
                            "Everything the tanh version can, provided the learning rate is lowered to compensate for the steeper slope",
                            "Almost everything the tanh version can, since tanh is close to linear near zero where the weights start",
                            "More than a single layer, because the two hidden widths of 4 add capacity whatever sits between them",
                        ],
                        "a": 0,
                        "whys": [
                            r"$W_2(W_1 x + b_1) + b_2 = (W_2 W_1)x + (W_2 b_1 + b_2)$, and the same collapse repeats at the next layer.",
                            r"The learning rate changes how fast the parameters move, not what functions are reachable. No setting of 41 linear parameters escapes being one affine map of the inputs.",
                            r"Near zero tanh is close to linear, and that is precisely where a *linear* network is stuck — it never leaves the linear regime. The tanh network can move its pre-activations away from zero and use the curve; the linear one has no curve to use.",
                            r"Width without a non-linearity is width in an intermediate representation that is then linearly recombined. The product $W_2 W_1$ is a $4 \times 3$ matrix whatever the widths in between; capacity did not increase.",
                        ],
                        "why": r"""
Two affine maps in a row are one affine map: multiply the matrices, combine the offsets.
Three in a row are still one. Whatever the widths, the linear network is a single
$1 \times 3$ weight row and a bias, and it can only separate the four rows if a plane
through them does. The tanh between layers is what makes depth add anything.
""",
                    },
                    {
                        "q": "Why must `mse_loss` return one `Value` rather than a list of four per-example losses?",
                        "opts": [
                            "`backward` seeds a single node with 1.0; a list has no single gradient to seed, only a scalar node does",
                            "A list of `Value`s would each need their own `zero_grad`, and the parameters can only be zeroed once per epoch",
                            "The mean keeps the loss between 0 and 1, which the tanh outputs require in order not to saturate",
                            "Per-example losses would each need a separate forward pass, and the engine keeps only the most recent graph",
                        ],
                        "a": 0,
                        "whys": [
                            r"\"How much does the whole thing move\" is a question about one number; the mean gives training that number.",
                            r"`zero_grad` clears parameters, not losses, and it runs once per step regardless of how the loss was assembled. The constraint comes from `backward`, which starts from one seed on one node.",
                            r"The mean of squared errors is not bounded by 1 — the lab's first loss is 1.18 — and tanh saturation is about pre-activations inside the network, not about the loss value. The mean is there so the gradient's scale does not depend on batch size.",
                            r"All four forward passes already happen, and all four graphs are alive at once, hanging beneath the loss node. The engine keeps every graph it built; what it needs is a single root to walk down from.",
                        ],
                        "why": r"""
`backward()` sets one node's gradient to 1.0 and walks its graph. Four separate losses
would need four separate walks, each pushing a partial gradient into the same weights —
which is what the mean does in one walk, with the $1/n$ folded in so that the step size
does not depend on how many rows the batch holds.
""",
                    },
                    {
                        "q": "On the one-neuron example ($x = 2$, $y = 3$, $w = 0.5$, $b = 0$) a learning rate of 0.2 leaves the loss at 4.0 on every step. What is happening?",
                        "opts": [
                            "Each step overshoots the minimum by the distance it started from, so the error flips its sign and keeps its size",
                            "The gradient is zero at that learning rate, because the weight update and the bias update cancel each other exactly",
                            "The parameters have landed on a saddle point where the slope vanishes, so no learning rate would move them further",
                            "A learning rate of 0.2 rounds each update to zero in floating point, so the parameters never actually change",
                        ],
                        "a": 0,
                        "whys": [
                            r"The error is multiplied by $1 - 2\eta(x^2+1) = 1 - 10\eta = -1$ each step: same size, opposite sign, same squared loss.",
                            r"The gradient is $-4$ on the bias and $-8$ on the weight at the start, and it is never zero while the error is not. The two updates push the prediction the same way; nothing cancels.",
                            r"A squared-error loss in two parameters is a bowl with one minimum and no saddle. The parameters are not stuck — they are jumping across the minimum to its mirror image every step.",
                            r"The updates are $-0.2 \times -8 = 1.6$ on $w$ and $0.8$ on $b$, nowhere near rounding. The prediction goes from 1 to 5 and back to 1: it moves a great deal, to the wrong places.",
                        ],
                        "why": r"""
One step changes the prediction by $-2\eta e(x^2 + 1)$, so the new error is
$e(1 - 10\eta)$. At $\eta = 0.2$ the factor is $-1$: from an error of $-2$ the step
lands at $+2$, then back at $-2$. The loss, being the square, cannot tell the two apart
and reads 4 for ever. At $0.1$ the factor is 0 and the problem is solved in one step;
at $0.3$ it is $-2$ and the loss quadruples.
""",
                    },
                    {
                        "q": "A training loop omits `zero_grad()`. What does it actually apply as the gradient on the third epoch?",
                        "opts": [
                            "The sum of the gradients from all three epochs, because every closure adds into a field that nothing cleared",
                            "The third epoch's gradient multiplied by three, because the backward pass re-walks the graph once per epoch so far",
                            "Only the first epoch's gradient, because a closure runs once and later passes find the node already spent",
                            "The average of the three gradients, which is why the loss still falls but more slowly than in the correct loop",
                        ],
                        "a": 0,
                        "whys": [
                            r"`+=` never subtracts. Each `backward()` adds a fresh gradient onto whatever the field already held.",
                            r"Each `backward()` walks the graph of *its own* forward pass once; it does not revisit earlier ones. What accumulates is the sum of three different gradients from three different parameter values, not one gradient scaled.",
                            r"Closures are rebuilt on every forward pass, and every one of them runs. Nothing is spent — the field keeps growing, which is the opposite of stopping after the first.",
                            r"Nothing divides by three. The applied step is the *sum*, which is typically larger than any single gradient, and the example in the reading shows the loop overshooting into oscillation rather than merely slowing.",
                        ],
                        "why": r"""
The gradient fields are running totals. On epoch three they hold $g_1 + g_2 + g_3$,
and the step applies all of it — an undamped momentum that keeps pushing after the
error has changed sign. The reading's trace shows the loss at 0.25, then 3.06, then
4.52, never settling. `zero_grad()` before `backward()` is the whole fix; zeroing after
it is a different way to write the same wrong loop.
""",
                    },
                    {
                        "q": "The slope of tanh at $z = 4$ is $0.00134$. What follows for a neuron whose pre-activation sits there?",
                        "opts": [
                            "Almost no gradient reaches its weights through that slope, so it barely learns however wrong its output is",
                            "Its output is nearly $\\pm 1$, so its contribution to the loss is small and it needs no further training",
                            "The gradient through it is large, because a tiny change in input snaps the output between $-1$ and $+1$",
                            "That neuron alone needs a higher learning rate, which is why the network trains each layer at its own rate",
                        ],
                        "a": 0,
                        "whys": [
                            r"The closure multiplies the arriving gradient by $1 - t^2 = 0.00134$; whatever came in, almost nothing gets through.",
                            r"An output near $+1$ is only good if the label is $+1$. If the label is $-1$ the neuron is as wrong as it can be — and the gradient that would fix it is scaled by $0.00134$ on its way back, which is the problem.",
                            r"Snapping is what happens at the *centre* of tanh, where the slope is 1. Out at $z = 4$ the curve is flat; a change in input changes the output almost not at all, which is exactly why the gradient is small.",
                            r"The lab's `train` uses one learning rate for every parameter, and no per-layer rate would help: the factor of $0.00134$ is inside the closure, and a larger step on a near-zero gradient is still near zero.",
                        ],
                        "why": r"""
The tanh closure multiplies the incoming gradient by $1 - \tanh^2 z$, which is
$0.00134$ at 4 and effectively zero at 8. A saturated neuron is a neuron whose weights
stop receiving useful gradient, right or wrong. Small initial weights and inputs of order
one keep the pre-activations near zero where the slope is close to 1, and that is the
whole reason the lab draws from `uniform(-1, 1)`.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "From bytes to merges to a vector",
                    "minutes": 11,
                    "body": r'''
Here is a string, and here is what the computer has of it:

```text
"aaabdaaabac"
[97, 97, 97, 98, 100, 97, 97, 97, 98, 97, 99]
```

Eleven bytes. A language model is a machine that reads a sequence of symbols and predicts
the next one, and the first decision is what a *symbol* is. Take whole words and you need
a dictionary; the first typo, name or URL that is not in it has no id at all, and every
model trained that way carries an `<unk>` token for the things it cannot name. Take single
bytes and nothing is ever unknown — there are 256 of them and every string is made of
them — but a sequence is now ten times longer than it would be in words, and each symbol
carries almost no meaning on its own.

Byte-pair encoding starts at bytes and lets the data grow the alphabet. The idea comes
from one observation about the string above: `97, 97` occurs over and over, so a symbol
that means "two a's" would shorten it.

## The merges, one at a time

Count every adjacent pair. In the eleven bytes there are ten pairs, and `(97, 97)`
accounts for four of them — note that the counting slides along one position at a time,
so `97, 97, 97` contributes two. `(97, 98)` occurs twice; everything else, once. Give the
most frequent pair the next free id, 256, and rewrite the sequence with it. Then count
again.

```python
def get_stats(ids):
    stats = {}
    for left, right in zip(ids, ids[1:]):
        stats[(left, right)] = stats.get((left, right), 0) + 1
    return stats


def merge(ids, pair, new_id):
    out, i = [], 0
    while i < len(ids):
        if i < len(ids) - 1 and (ids[i], ids[i + 1]) == pair:
            out.append(new_id)
            i += 2
        else:
            out.append(ids[i])
            i += 1
    return out


ids = list("aaabdaaabac".encode("utf-8"))
print("bytes:", ids)
merges = {}
for new_id in (256, 257, 258):
    stats = get_stats(ids)
    pair, count = min(stats.items(), key=lambda item: (-item[1], item[0]))
    ids = merge(ids, pair, new_id)
    merges[pair] = new_id
    print(f"merge {pair} seen {count}x -> {new_id}:", ids)
print(merges)
```

The first merge turns the eleven ids into nine: `[256, 97, 98, 100, 256, 97, 98, 97, 99]`.
Look at what happened to `97, 97, 97`. The counter saw two pairs there, but the rewrite
walks left to right and *consumes* both bytes of a match — that is the `i += 2` — so the
three a's become one 256 and a leftover 97, never two 256s sharing a byte. Overlapping
counts, non-overlapping replacement; the counts are a heuristic for choosing, the
replacement is what has to be exact.

The second round is a tie: `(256, 97)` and `(97, 98)` both occur twice. Something has to
decide, and it has to decide the same way every time or two runs of the trainer disagree
on the tokeniser. The lab's rule is the numerically smallest pair, and `(97, 98)` wins
because $97 < 256$. That gives `[256, 257, 100, 256, 257, 97, 99]` — seven ids, and the
exact sequence the lab's "Encoding replays the merges" test expects. The lab stops there,
at a vocabulary of 258. The block above goes one round further to show what a third merge
would take: `(256, 257)`, which is `aaab`, and the sequence shrinks to five.

## The merge list is the tokeniser

Everything learned is in the dictionary the block printed: `{(97, 97): 256, (97, 98):
257, (256, 257): 258}`. To encode new text, take its bytes and replay those merges *in
the order they were learned*. Order is not a nicety. The third merge is defined over ids
256 and 257, which exist only after the first two have been applied; replay it first and
it matches nothing. The lab's `encode` sorts the merges by their id — which is learned
order, since ids are handed out in sequence — and applies each in turn.

To decode, each id has to spell a byte string. Base ids spell themselves; a merged id
spells the concatenation of what its two halves spell, which is why `build_vocab` also
walks the merges in learned order — a merge's halves must already have their spellings.

```python
merges = {(97, 97): 256, (97, 98): 257, (256, 257): 258}
vocab = {i: bytes([i]) for i in range(256)}
for (left, right), new_id in sorted(merges.items(), key=lambda item: item[1]):
    vocab[new_id] = vocab[left] + vocab[right]
    print(new_id, "spells", vocab[new_id])
print(b"".join(vocab[i] for i in [258, 100, 258, 97, 99]).decode("utf-8"))
```

That prints `b'aa'`, `b'ab'`, `b'aaab'`, and then the original string back.

Here is the property that makes byte-level BPE safe to use on anything. `encode` only ever
replaces adjacent ids by an id that spells exactly their concatenation, and any byte it
cannot merge keeps its own id. So the bytes of `decode(encode(text))` are the bytes of
`text`, for *any* text — a string the trainer never saw merges less, but it never loses a
byte. The lab checks that round trip on `"héllo wörld"`, on an empty string, and on text
that shares nothing with the training corpus.

## Where the bytes stop being characters

UTF-8 spends more than one byte on most characters outside ASCII. The `é` in `héllo` is
the two bytes 195 and 169, and a token boundary — or a generation that stops early — can
land between them.

```python
ids = list("héllo".encode("utf-8"))
print(ids)
print(bytes(ids[:2]).decode("utf-8", errors="replace"))
print(bytes(ids[:3]).decode("utf-8", errors="replace"))
```

The first two bytes decode to `h` followed by the replacement character `�`; the first
three decode to `hé`. This is why `decode` in the lab uses `errors="replace"`: a strict
decode would raise on half a character, and a model that has emitted 195 and not yet 169
has not done anything wrong. The `�` is honest — it says a character was cut.

## What a vocabulary size buys

Every merge shortens sequences and lengthens the alphabet, and both have a price. The
lab's second corpus, `"the cat sat on the mat, the cat ran"`, is 35 bytes; trained to a
vocabulary of 280 it encodes to fewer tokens, and the test only requires *fewer*, because
how many depends on which of the 24 merges the ties allowed. The model then has fewer
positions to process — and attention, in the next module, costs the square of that
count — but the embedding table, which holds one learned row per id, has 24 more rows,
and each of those rows is learned only from the places its token occurs.

Scale it. A vocabulary of 50,257 with 768 numbers per row — the numbers of one well-known
model — is 38.6 million parameters before the first attention layer exists, and the rarest
of those 50,257 tokens might appear a handful of times in the training text. Somewhere
between 256 and a few hundred thousand is a vocabulary that balances sequence length
against a table that can be learned, and that number is chosen by experiment, not derived.

## An id is a name, not a number

Token 257 is not "more than" token 100, and 256 is not "close to" 257. Ids are labels,
and the first thing a model does with a label is look it up: an *embedding table* has one
row per id, `dim` numbers wide, and `vector(token_id)` returns that row. The rows start
random — the lab draws them from a seeded `uniform(-1, 1)`, row by row — and they are
parameters like any weight in module 2: the row for token 257 receives gradient whenever
257 appears in a training example, and it moves. What the row *means* is whatever
training makes it mean.

To compare two rows you want a measure of whether they point the same way, without
caring how long they are. The dot product gives $u \cdot v = |u|\,|v| \cos\theta$, so
dividing out the two lengths leaves $\cos\theta$ alone:

$$\text{cosine}(u, v) = \frac{u \cdot v}{|u|\,|v|}$$

```python
import math


def cosine(u, v):
    dot = sum(a * b for a, b in zip(u, v))
    return dot / (math.sqrt(sum(a * a for a in u)) * math.sqrt(sum(b * b for b in v)))


print(cosine([1.0, 2.0, 3.0], [2.0, 4.0, 6.0]))
print(cosine([1.0, 0.0], [0.0, 1.0]))
print(cosine([1.0, 0.0], [-1.0, 0.0]))
print(cosine([3.0, 4.0], [4.0, 3.0]))
```

`1.0`, `0.0`, `-1.0`, `0.96`. The first pair differ in every component and score a
perfect 1, because one is the other scaled by two and scaling does not turn a vector.
Right angles score 0, opposite directions $-1$. And the zero vector scores nothing at
all: it has no direction, the denominator is 0, and the lab's `cosine_similarity` raises
`ValueError` rather than divide.

## Where the idea stops holding

The mistake people make with a fresh embedding table is to compute the cosine between
two rows and read something into it. It is tempting because the function returns a
number between $-1$ and $1$ and the number is small, which sounds like "unrelated". Watch
what random rows do as the dimension grows:

```python
import math
import random

rng = random.Random(7)
for dim in (2, 8, 64, 512):
    total = 0.0
    for _ in range(500):
        u = [rng.uniform(-1.0, 1.0) for _ in range(dim)]
        v = [rng.uniform(-1.0, 1.0) for _ in range(dim)]
        dot = sum(a * b for a, b in zip(u, v))
        total += abs(dot) / (math.sqrt(sum(a * a for a in u)) * math.sqrt(sum(b * b for b in v)))
    print(f"dim {dim:>3}: mean |cosine| of two random rows = {total / 500:.3f}")
```

In 2 dimensions two random directions have a mean $|\cos\theta|$ of about 0.62; in 512
dimensions it is 0.035. Random vectors in high dimension are almost always nearly
orthogonal. A cosine of 0.03 between two rows of an untrained table says something about
the number 512 and nothing about the tokens. Similarity means something only after
training has moved the rows, and even then it means "these tokens were used in similar
places", which is not the same as "these tokens mean similar things".

The tokeniser has its own edge. A merge list learned on English prose compresses English
prose; hand it source code, or a language in a different script, and it falls back
toward one token per byte, with a Chinese character costing three tokens where an English
word costs one. The round trip still holds — nothing is lost — but the sequence is long,
and everything downstream pays for the length.

In the lab, "Byte-pair encoding and vector lookup", you build the four BPE functions
exactly as traced above — pair counts, non-overlapping merge, the trainer with its
smallest-pair tie-break, and the vocabulary spelled out in learned order — then `encode`
and `decode` that round-trip anything, and the seeded `EmbeddingTable` with a
`cosine_similarity` that refuses the zero vector.
''',
                },
            ],
            "quiz": {
                "title": "Merges, ids and directions",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The pair `(97, 97)` is counted four times in `[97, 97, 97, 98, 100, 97, 97, 97, 98, 97, 99]`, yet the first merge produces `[256, 97, 98, ...]` and not `[256, 256, ...]`. Why?",
                        "opts": [
                            "Counting slides over every adjacent pair, but a replacement consumes both bytes, so `aaa` becomes one 256 and a leftover `a`",
                            "The tie-break on the numerically smallest pair chose to leave the second occurrence in `aaa` for a later merge round",
                            "The count of four is an error in `get_stats`: `aaa` holds one pair, and the statistics ought to be corrected to count it once",
                            "A merge may replace only one occurrence per pass over the sequence, so the trainer returns for the others on later rounds",
                        ],
                        "a": 0,
                        "whys": [
                            r"`i += 2` after a match is the whole of it: overlapping counts to choose, non-overlapping replacement to rewrite.",
                            r"The tie-break chooses *which pair* to merge when two have equal counts; it says nothing about which occurrences to rewrite. Within `aaa` there is no second occurrence left once the first two bytes are consumed.",
                            r"The count is correct for what it measures — `zip(ids, ids[1:])` sees `(97, 97)` at two positions in `aaa`, and the lab's test asserts `get_stats([7, 7, 7]) == {(7, 7): 2}`. Counting and replacing are different operations with different rules.",
                            r"`merge` replaces every non-overlapping occurrence in one pass — the sequence goes from eleven ids to nine in a single call. What it cannot do is replace two occurrences that share a byte.",
                        ],
                        "why": r"""
`get_stats` counts with a sliding window, so `97, 97, 97` contributes two. `merge` walks
left to right and, on a match, emits the new id and skips *both* bytes. The third `97`
has no partner left and stays as it is. Overlapping counts are a heuristic for choosing
the next merge; non-overlapping replacement is what keeps decode exact.
""",
                    },
                    {
                        "q": "Why must `encode` replay the merges in the order they were learned, rather than longest-token-first?",
                        "opts": [
                            "A later merge is defined over ids that earlier merges created, so applied first it finds nothing to match",
                            "Replaying in any other order yields more tokens, and learned order is the one that compresses the text best",
                            "The ids must come out in increasing order along the sequence, and only replay in learned order guarantees that",
                            "Longest-first would merge across word boundaries, which the byte-level alphabet has no way to represent",
                        ],
                        "a": 0,
                        "whys": [
                            r"`(256, 257) -> 258` can only fire on a sequence in which 256 and 257 already exist.",
                            r"Compression is not the reason, and it is not even reliably true — the reason is correctness. Merge 258 spells `aaab`, but it is written as the pair `(256, 257)`, and before those two merges have run the sequence contains neither id.",
                            r"Ids along an encoded sequence come out in whatever order the text dictates — `[256, 257, 100, 256, 257, 97, 99]` is not sorted. Learned order is about *which merges have already happened*, not about the output.",
                            r"Byte-level BPE merges across whatever bytes are adjacent, spaces included; nothing about the alphabet forbids it. The constraint is dependency between merges, not word boundaries.",
                        ],
                        "why": r"""
Each merge is a pair of ids, and the ids in a later merge may themselves be the products
of earlier merges. `(256, 257)` matches nothing in a sequence of raw bytes; it can only
fire after `(97, 97)` and `(97, 98)` have produced the ids it names. Replaying in learned
order is what makes every merge's inputs exist by the time it runs.
""",
                    },
                    {
                        "q": "Why does `decode(encode(text))` return `text` exactly, even for text the tokeniser never saw in training?",
                        "opts": [
                            "Every id spells a fixed byte string and unmerged bytes keep their own ids, so the exact byte sequence is rebuilt",
                            "Because `train_bpe` sees enough text that every byte pair that could occur appears somewhere in its merge list",
                            "`encode` emits a special unknown-token id for unseen text, and `decode` fills its bytes back in from the original",
                            "It does not in general; the round trip holds only for text whose pairs all appear in the training corpus",
                        ],
                        "a": 0,
                        "whys": [
                            r"Merging only ever replaces adjacent ids by one that spells their concatenation, and a byte that matches no merge stays a byte.",
                            r"No trainer sees every pair — the lab's trainer sees eleven bytes. Coverage is not what makes the round trip work; the fact that unmerged bytes are already valid ids is.",
                            r"There is no unknown token in a byte-level scheme, and there is nothing to fill in from — `decode` receives ids and nothing else. That is the point of starting from bytes: every input is already made of ids.",
                            r"The lab's test round-trips `\"héllo wörld\"` and `\"banana bandana\"` through merges learned on `\"aaabdaaabac\"`. Unseen text merges less, and loses nothing.",
                        ],
                        "why": r"""
Two invariants do it. Ids 0–255 are the bytes themselves, so any text is already a valid
id sequence before a single merge runs. And every merge replaces two adjacent ids by one
whose spelling is exactly their spellings joined, so applying merges never changes the
underlying bytes — only how they are grouped. Decode concatenates the spellings and the
bytes come back untouched.
""",
                    },
                    {
                        "q": "Raising the vocabulary from 256 to 50,000. What is gained, and what is paid?",
                        "opts": [
                            "Shorter sequences to process, paid for with a 50,000-row embedding table whose rare rows are learned from few examples",
                            "More precise tokens, paid for with longer sequences because the rarer merges split the text more finely than bytes do",
                            "A smaller model overall, because fewer tokens per text means fewer weights are needed to process each one of them",
                            "Nothing downstream changes: tokens are renumbered, but the attention layers see the same number of positions either way",
                        ],
                        "a": 0,
                        "whys": [
                            r"Every merge shortens sequences and adds a row that must be learned from wherever its token happens to occur.",
                            r"Merges never split; they join. More merges means each token spells more bytes and the sequence gets *shorter*, not longer. The price is on the table side, not the sequence side.",
                            r"The processing weights — attention, the MLP — do not depend on vocabulary size at all; the embedding table and the output layer do, and both grow with it. Fewer positions makes each forward pass cheaper, not the model smaller.",
                            r"The number of positions is the number of tokens, and that is precisely what changes: the lab's 35-byte sentence becomes fewer tokens at vocabulary 280. Attention's cost grows with the square of that count.",
                        ],
                        "why": r"""
A larger vocabulary trades length for width. Sequences get shorter — which matters
because attention costs the square of sequence length — and the embedding table gets
taller, with each new row learned only from the places its token appears. Somewhere
between the two extremes is a vocabulary that balances the two costs, and it is found by
trying, not by derivation.
""",
                    },
                    {
                        "q": "`cosine_similarity([1, 2, 3], [2, 4, 6])` is exactly 1.0 although the vectors differ in every component. What does that say about the measure?",
                        "opts": [
                            "It compares direction only: scaling a vector by any positive factor leaves its cosine with anything unchanged",
                            "It saturates: any two vectors whose dot product exceeds 1 are reported as identical, as the result is capped",
                            "It rounds: the two vectors are close enough in each component to fall inside the same one-decimal-place bucket",
                            "It measures the ratio of lengths: 2 to 1 in every component gives the maximal score, as any constant ratio would",
                        ],
                        "a": 0,
                        "whys": [
                            r"Dividing the dot product by both lengths leaves $\cos\theta$, and the angle between $v$ and $2v$ is zero.",
                            r"Nothing is capped. The dot product here is 28, the lengths are $\sqrt{14}$ and $\sqrt{56}$, and $28 / \sqrt{784}$ is 1 exactly — arithmetic, not a ceiling.",
                            r"Cosine returns a full float; `[3, 4]` against `[4, 3]` gives 0.96, not 1. The 1.0 here is exact because the angle is exactly zero.",
                            r"Length is what cosine *discards*. A constant ratio of 2 gives 1.0, and so would a ratio of 1000, because the two vectors point the same way regardless of how long they are.",
                        ],
                        "why": r"""
$u \cdot v = |u|\,|v|\cos\theta$, so dividing by the two lengths leaves the cosine of
the angle and nothing else. `[2, 4, 6]` is `[1, 2, 3]` stretched, the angle between them
is zero, and the cosine is 1 exactly. Magnitude is invisible to the measure — which is
why it is useful for comparing embeddings and why the zero vector, having no direction,
has no cosine at all.
""",
                    },
                    {
                        "q": "Two rows of a freshly built `EmbeddingTable(300, 512)` have a cosine similarity of 0.03. What can you conclude?",
                        "opts": [
                            "Nothing about the tokens: two random vectors in 512 dimensions are nearly orthogonal whatever they will later mean",
                            "The two tokens are unrelated, which is what the seeded initialisation encodes about byte pairs that never co-occur",
                            "The table is defective: rows drawn from the same distribution should agree far more closely than 0.03",
                            "The two tokens are weakly related, since 0.03 is positive and a truly unrelated pair would score exactly zero",
                        ],
                        "a": 0,
                        "whys": [
                            r"The reading's block shows random pairs averaging $|\cos| \approx 0.035$ at 512 dimensions; 0.03 is what *any* two rows score before training.",
                            r"The initialisation encodes nothing — it is `uniform(-1, 1)` from a seed, with no knowledge of which ids are which. A cosine near zero is a property of the dimension, not of the tokens.",
                            r"Rows drawn independently from the same distribution are *expected* to be nearly orthogonal in high dimension; agreement would be the surprise. The table is behaving exactly as random vectors do.",
                            r"Random pairs land on either side of zero, and the sign carries no information. With 500 random pairs in 512 dimensions the typical magnitude is 0.035; a value of 0.03 is indistinguishable from chance.",
                        ],
                        "why": r"""
In high dimension, independently random vectors are nearly orthogonal: the mean
$|\cos\theta|$ of two random rows is about 0.62 in 2 dimensions and 0.035 in 512. A
cosine of 0.03 between untrained rows is what chance produces, and it says nothing
about tokens 256 and 257. Similarity between embeddings means something only after
training has moved the rows — and then it means "used in similar places".
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "A weighted average that picks its own weights",
                    "minutes": 12,
                    "body": r'''
Three tokens sit in a row, each carrying a vector of numbers. The third one has to
produce a summary of what came before it — something it can use to guess the fourth.
The crudest summary is the plain average of the three vectors. It throws away which one
mattered: if the third token is `it`, the vector that should dominate is whichever noun
`it` refers to, and a plain average weights the noun the same as the comma.

So use a weighted average, and let the weights depend on the tokens themselves. That
single decision is attention. Everything else in this module is about how the weights are
chosen and how to keep the arithmetic honest.

## Similarity as a dot product

Give each token two views of itself: a *query*, meaning "what am I looking for", and a
*key*, meaning "what do I offer". The natural measure of how well a key answers a query
is the dot product $q \cdot k$: large when the two point the same way, zero at right
angles, negative when opposed. One query against every key gives one score per position.

Scores are not weights. Weights should be positive, should sum to one so that the output
stays the same size as the values it averages, and should preserve the order of the
scores. Exponentiate — $e^{s}$ is positive for any $s$ and increasing — then divide by the
total. That is softmax:

$$w_j = \frac{e^{s_j}}{\sum_k e^{s_k}}$$

Then give each token a third view, the *value* $v_j$ — what it contributes if attended
to — and the output for the query is $\sum_j w_j v_j$.

Here it is on the smallest case worth doing by hand, which is also the case the lab's
"hand-computed attention example" test checks. One query $[1, 0]$; two keys $[1, 0]$ and
$[0, 1]$; two values $[1, 2]$ and $[3, 4]$.

```python
import math

Q = [[1.0, 0.0]]
K = [[1.0, 0.0], [0.0, 1.0]]
V = [[1.0, 2.0], [3.0, 4.0]]
scale = 1 / math.sqrt(len(Q[0]))
scores = [sum(q * k for q, k in zip(Q[0], key)) * scale for key in K]
print("scores :", scores)
top = max(scores)
exps = [math.exp(s - top) for s in scores]
weights = [e / sum(exps) for e in exps]
print("weights:", weights)
output = [sum(w * row[d] for w, row in zip(weights, V)) for d in range(2)]
print("output :", output)
```

The raw dot products are 1 and 0. Divided by $\sqrt{2}$ — the reason for that is next —
they are $0.7071$ and $0$. Exponentiated, $2.0281$ and $1$; normalised, the weights are
$0.6698$ and $0.3302$. The output is $0.6698 \times [1, 2] + 0.3302 \times [3, 4] =
[1.6605, 2.6605]$, which is what the block prints to full precision. The query leaned
toward the first key, so the first value got two thirds of the say.

Set the query to $[0, 0]$ instead and every score is 0, the weights are $[0.5, 0.5]$,
and the output is the plain average $[2, 3]$ — the crude summary from the opening
paragraph is what attention does when it has no preference.

## Why divide by the square root

Suppose the entries of $q$ and $k$ are independent with mean 0 and variance 1 — roughly
what a fresh projection produces. Then $q \cdot k$ is a sum of $d_k$ terms, each with
variance 1, so its variance is $d_k$ and its typical size is $\sqrt{d_k}$. Dividing by
$\sqrt{d_k}$ brings the typical score back to order 1 whatever the width.

```python
import math
import random

rng = random.Random(7)
for d in (2, 16, 64, 256):
    dots = []
    for _ in range(2000):
        q = [rng.gauss(0.0, 1.0) for _ in range(d)]
        k = [rng.gauss(0.0, 1.0) for _ in range(d)]
        dots.append(sum(a * b for a, b in zip(q, k)))
    std = math.sqrt(sum(x * x for x in dots) / len(dots))
    print(f"d_k = {d:>3}: spread of q.k is {std:5.2f}, after dividing by sqrt(d_k) it is {std / math.sqrt(d):.2f}")
```

The spread comes out at $1.41$, $3.94$, $7.98$ and $15.97$ — the square roots of the
widths — and after scaling it is $1.0$ every time. Why care? Because softmax of scores
that are typically $\pm 16$ is a one-hot vector: $e^{16}$ against $e^{-16}$ leaves the
runner-up with a weight of $10^{-14}$. The weighted average collapses to "copy one
value", and, exactly as with tanh at $z = 8$ in module 2, the slope of softmax out there
is nearly zero and gradient stops flowing. The $\sqrt{d_k}$ keeps the scores where
softmax still has a slope.

## Keeping exp finite

Softmax has a property worth deriving because it is the whole reason the lab's `softmax`
is written the way it is. Add the same constant $c$ to every score:

$$\frac{e^{s_j + c}}{\sum_k e^{s_k + c}} = \frac{e^{c}\,e^{s_j}}{e^{c}\sum_k e^{s_k}} =
\frac{e^{s_j}}{\sum_k e^{s_k}}$$

Nothing changes. So you may subtract whatever you like from all the scores, and the useful
choice is their maximum, because then the largest exponent is $e^0 = 1$ and every other
is between 0 and 1. Without that, a score that is large for any reason at all breaks the
arithmetic:

```python
# raises OverflowError
import math

print(math.exp(1000.0))
```

A double tops out near $e^{709}$. With the subtraction, the same scores are harmless:

```python
import math

scores = [1000.0, 0.0]
top = max(scores)
exps = [math.exp(s - top) for s in scores]
print([e / sum(exps) for e in exps])
```

That prints `[1.0, 0.0]`, which is also the right answer: a lead of 1000 is a certainty.
The lab's test "Softmax is normalised, shift-invariant and stable" checks all three
properties from this section.

## Looking only backwards

A model that generates text left to right must not let position 1 read position 2 while
training — at generation time position 2 does not exist yet. So position $i$ is allowed
to attend only to $j \le i$. The lab's `causal_mask(n)` is that rule as a grid of
booleans, and the question is where in the arithmetic to apply it.

The answer is: to the *scores*, before the softmax, by setting each forbidden score to
$-\infty$. Then $e^{-\infty - \text{top}}$ is exactly 0, the forbidden position gets
weight 0, and the remaining weights still sum to 1 because they were normalised among
themselves. Here is what happens if you instead zero the weights afterwards:

```python
import math


def softmax(xs):
    top = max(xs)
    exps = [math.exp(x - top) for x in xs]
    return [e / sum(exps) for e in exps]


scores = [0.9, 0.4, 1.3]
before = softmax([scores[0], scores[1], float("-inf")])
after = softmax(scores)
after[2] = 0.0
print("masked before softmax:", [round(w, 4) for w in before], "sum", round(sum(before), 4))
print("zeroed after softmax: ", [round(w, 4) for w in after], "sum", round(sum(after), 4))
```

Masked first, the two allowed weights are $0.6225$ and $0.3775$ and they sum to 1.
Zeroed afterwards, they are $0.3228$ and $0.1958$ and sum to $0.5185$ — the forbidden
position had the highest score, so it took half the mass with it when it was deleted,
and the output is now the allowed average scaled by about a half. This is the mistake
people make, and it is tempting because the mask looks like it belongs on the weights —
"weight of the future is zero" reads as a statement about weights. It is a statement
about what softmax is allowed to see.

One edge falls out of doing it right: a row in which *every* score is $-\infty$ has
nothing to normalise, `max` is $-\infty$, and $-\infty - (-\infty)$ is not a number. The
lab's `softmax` raises `ValueError` for that row rather than return `nan`, and
`causal_mask` never produces one, since position $i$ can always see itself.

## Several heads

A single set of weights per query can express one pattern of "what to look at". Split the
model's width into $h$ equal blocks, run attention separately in each block with its own
projections, and concatenate the results, and each head can attend somewhere different
— one to the previous token, one to the nearest noun — at the same time. `split_heads`
slices columns, `concat_heads` glues them back, and `multi_head_attention` projects
through $W_q$, $W_k$, $W_v$, does the per-head attention, and projects the concatenation
through $W_o$. With one head and identity projections it must reduce to plain
`attention(X, X, X)`, which is the lab's last test, and with two heads on the same
input it must *differ*, because each head is now scoring similarity on half the
features.

## Where the idea stops holding

Attention does not know where anything is. Reverse the order of the keys and the values
together and every output row is unchanged:

```python
import math


def attend(q, K, V):
    scale = 1 / math.sqrt(len(q))
    scores = [sum(a * b for a, b in zip(q, k)) * scale for k in K]
    top = max(scores)
    exps = [math.exp(s - top) for s in scores]
    weights = [e / sum(exps) for e in exps]
    return [round(sum(w * v[d] for w, v in zip(weights, V)), 6) for d in range(len(V[0]))]


K = [[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]]
V = [[1.0, 0.0], [0.0, 1.0], [2.0, 2.0]]
q = [0.5, -0.5]
print(attend(q, K, V))
print(attend(q, K[::-1], V[::-1]))
```

Both lines print `[1.09526, 0.864339]`. The scores are a set, softmax is a function of
the set, and the weighted sum does not care which term came first. A mechanism that
cannot tell `dog bites man` from `man bites dog` needs order supplied from outside, and
that is what the capstone's position embeddings are for: a learned vector per position,
added to the token's vector before any attention happens.

The second limit is cost. Every query scores every key, so a sequence of $n$ tokens
needs $n^2$ scores per head per layer: 9 for the three tokens in the lab, about 16.8
million for a context of 4096. That quadratic is the reason context windows are a
headline number, and the reason a good deal of current research is about approximating
this exact computation with something cheaper.

In the lab, "Scaled dot-product attention from scratch", you write the matrix helpers
with their error paths, a `softmax` that subtracts the maximum and refuses an all-masked
row, `causal_mask`, `attention` returning both output and weights, and the split, attend
and concatenate of `multi_head_attention` — every number above reproduced by code you
wrote.
''',
                },
            ],
            "quiz": {
                "title": "Where attention's numbers come from",
                "minutes": 8,
                "questions": [
                    {
                        "q": "With `Q = [[0, 0]]` the weights come out as `[0.5, 0.5]` and the output is the mean of the two value rows. Why?",
                        "opts": [
                            "A zero query scores every key at 0, and softmax of equal scores hands every value the same weight",
                            "Softmax of an all-zero score vector is undefined, so the implementation falls back to averaging the values",
                            "A zero query matches the keys $[1, 0]$ and $[0, 1]$ equally well because both keys have unit length",
                            "Scaling by $1/\\sqrt{d_k}$ maps each score to 0.5, and those scaled scores are used directly as weights",
                        ],
                        "a": 0,
                        "whys": [
                            r"$0 \cdot k = 0$ for every key, and $e^0 / (e^0 + e^0)$ is a half. Attention with no preference is a plain average.",
                            r"Softmax of `[0, 0]` is perfectly well defined — $e^0 = 1$ each, total 2, weights a half each. There is no fallback path; the average is what the formula gives.",
                            r"The keys' lengths are irrelevant to a zero query: the dot product is zero whatever the key. Two keys of different lengths would still tie at 0.",
                            r"The scores are $0 / \sqrt{2} = 0$, not 0.5, and scores are never used as weights — they pass through exponentiation and normalisation first. The 0.5 comes from the normalisation of two equal exponentials.",
                        ],
                        "why": r"""
A zero query has no preference: its dot product with every key is 0, so all scores tie.
Softmax over tied scores is uniform, and a uniform weighted sum of the value rows is
their mean, $[2, 3]$. Attention reduces to the crude average exactly when the query
gives it no reason to do otherwise.
""",
                    },
                    {
                        "q": "Why are the scores divided by $\\sqrt{d_k}$ before the softmax?",
                        "opts": [
                            "A sum of $d_k$ unit-variance products has spread $\\sqrt{d_k}$, and softmax saturates at scores that large",
                            "It normalises the scores to sum to 1 across the keys, so the softmax that follows has less correcting to do",
                            "It undoes the $\\sqrt{d_k}$ factor that the projection matrices introduce when they narrow the width per head",
                            "Dividing by the dimension makes the output independent of how many keys the query is scored against",
                        ],
                        "a": 0,
                        "whys": [
                            r"The reading's block shows the spread at $1.41, 3.94, 7.98, 15.97$ for widths $2, 16, 64, 256$ — and $1.0$ after scaling, every time.",
                            r"Softmax does the normalising; the scaling changes the *size* of the scores, not their sum. Scores of $[0.7, 0]$ do not sum to 1 and are not meant to.",
                            r"The projections introduce no such factor — they are learned matrices with whatever entries training gives them. The $\sqrt{d_k}$ is about the statistics of a sum of $d_k$ products, and it would apply with no projections at all.",
                            r"The divisor is the *width* of a key, not the number of keys; it is the same whether there are two keys or two thousand. And it is the square root of the width, because that is how the spread of a sum of $d_k$ terms grows.",
                        ],
                        "why": r"""
$q \cdot k$ is a sum of $d_k$ products. If each has variance 1, the sum has variance
$d_k$ and typical size $\sqrt{d_k}$. Left alone, a width of 256 gives scores around
$\pm 16$, softmax becomes one-hot, and its gradient vanishes — the attention equivalent
of a saturated tanh. Dividing by $\sqrt{d_k}$ keeps the typical score near 1 whatever
the width.
""",
                    },
                    {
                        "q": "Subtracting the maximum score from every score before exponentiating changes what, exactly?",
                        "opts": [
                            "Nothing in the result: $e^{-\\max}$ cancels between numerator and denominator, and `exp` stays finite",
                            "The result slightly: the largest weight becomes exactly 1.0 and the others are scaled down to fit beneath it",
                            "The ordering: the largest score maps to zero, so the smallest score now receives the largest weight",
                            "Only the running time: `exp` of a small argument is cheaper to evaluate than `exp` of a large one",
                        ],
                        "a": 0,
                        "whys": [
                            r"$e^{s_j - c} / \sum e^{s_k - c}$ is $e^{s_j} / \sum e^{s_k}$ for any $c$; choosing $c = \max$ keeps every exponent at or below 0.",
                            r"The largest *exponential* becomes 1, not the largest weight — after dividing by the total, the weights are exactly what they would have been. The lab's test checks that shifting all scores by 100 changes nothing.",
                            r"Subtracting the same constant from everything preserves order: the largest score becomes 0 and the rest become negative, so the largest still has the largest exponential. Nothing is reversed.",
                            r"`exp` costs the same whatever its argument, up to the point where it overflows and raises. The subtraction is about correctness — `exp(1000)` is an `OverflowError`, `exp(0)` is 1 — not speed.",
                        ],
                        "why": r"""
Softmax is invariant to adding a constant to every score, because the constant becomes
a common factor in numerator and denominator. Subtracting the maximum makes the largest
exponent zero and every other negative, so `exp` never overflows. The weights are
identical to the unshifted ones — where the unshifted ones can be computed at all.
""",
                    },
                    {
                        "q": "A causal mask is implemented by zeroing the forbidden weights *after* the softmax. What goes wrong?",
                        "opts": [
                            "The surviving weights no longer sum to 1, so the output is shrunk by whatever mass the future held",
                            "Nothing: the forbidden positions contribute zero either way, and the two orders produce the same output",
                            "The softmax raises on that row, because the maximum score may lie in the forbidden region",
                            "The gradient into the masked positions stays non-zero, but the forward output is the same as masking first",
                        ],
                        "a": 0,
                        "whys": [
                            r"The reading's example: $[0.6225, 0.3775]$ masked first, against $[0.3228, 0.1958]$ summing to $0.5185$ when zeroed after.",
                            r"The forbidden position's *exponential* was in the denominator when the other weights were normalised. Delete its weight afterwards and the others keep their too-small values; the output is a fraction of what it should be.",
                            r"Softmax over the unmasked row is fine — it is a row of ordinary finite scores. The row that makes softmax raise is one where *every* score is $-\infty$, which is the opposite situation.",
                            r"The forward output is not the same — that is the whole defect. The weights that remain were normalised against a total that included the future, and removing the future afterwards does not renormalise them.",
                        ],
                        "why": r"""
Softmax normalises against the sum of all the exponentials, including the forbidden
ones. Zero a weight afterwards and the others are left normalised against a total they no
longer make up. Setting the forbidden *scores* to $-\infty$ first makes their
exponentials exactly zero, so the allowed weights are normalised among themselves and
still sum to 1.
""",
                    },
                    {
                        "q": "Reversing the rows of `K` and `V` together leaves attention's output row unchanged. What does that imply?",
                        "opts": [
                            "Attention alone cannot tell which token came first, so position has to be supplied from outside",
                            "Keys and values are interchangeable, so one matrix could serve as both without any loss",
                            "Attention is symmetric in queries and keys, so swapping `Q` and `K` also leaves the output unchanged",
                            "The softmax weights are always uniform, so any reordering of the values yields their plain mean",
                        ],
                        "a": 0,
                        "whys": [
                            r"The scores form a set, softmax is a function of the set, and the weighted sum does not care which term came first. Order has to be added — the capstone's position embeddings.",
                            r"Keys and values play different roles — keys are scored, values are averaged — and they are different projections of the input. The experiment reorders them *together*; it says nothing about swapping them.",
                            r"Queries and keys are not symmetric: the query decides the weights, the keys are what it is scored against, and the two projections are learned separately. Permuting the key rows is a different operation from swapping the roles.",
                            r"The weights in the example are far from uniform — the query $[0.5, -0.5]$ prefers the first key. The output is unchanged because the *same* weight travels with the *same* value wherever the pair is moved.",
                        ],
                        "why": r"""
Each key gets a score, each score becomes a weight, each weight multiplies its own
value, and the products are summed. Permute the keys and values together and the same
products are summed in a different order — the same sum. Attention is therefore blind
to sequence order, which is why a learned vector per position is added to the token
embeddings before the first attention layer.
""",
                    },
                    {
                        "q": "Two heads of width 2 on a width-4 model, versus one head of width 4. What does the split change?",
                        "opts": [
                            "Each head scores similarity over its own half of the features, so the two can attend to different positions",
                            "Nothing in the output: concatenating the two halves back together rebuilds the single-head result exactly",
                            "It doubles the parameter count, because every head needs its own copy of the full-width projection matrices",
                            "It halves the sequence length each head must process, which is where the speed-up over one head comes from",
                        ],
                        "a": 0,
                        "whys": [
                            r"The weights in a head come from dot products over that head's columns only, so two heads can produce two different weightings of the same values.",
                            r"The lab's test asserts the two-head result *differs* from one head. The weights are computed per head from half-width dot products, so the halves of the output were averaged with different weights, and concatenation does not undo that.",
                            r"The projections are shared across heads and the same size regardless of head count — $W_q$ is $4 \times 4$ either way; heads slice its output. Splitting changes how the width is used, not how much of it there is.",
                            r"Every head sees every position — the sequence is not divided, the *feature width* is. Each head still computes $n^2$ scores; the cost per head falls only because each dot product is over fewer columns.",
                        ],
                        "why": r"""
`split_heads` divides columns, not rows. Each head computes its own scores from its own
slice of the query and key features, so each head produces its own weighting of the
value rows, and the concatenation carries two different weighted averages side by side.
One head can express one pattern of where to look; two heads can express two at once.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "From logits to a token, and how surprised the model was",
                    "minutes": 12,
                    "body": r'''
The model has read `the cat sat on the` and its last layer has produced four numbers, one
per token in a vocabulary of four:

```text
token:   mat     rug     floor   cat
logit:  -0.693  -1.204  -1.897  -2.996
```

Those are *logits*: unnormalised scores, any real numbers, larger meaning more favoured.
They are not probabilities and the model does not owe you probabilities. Turning four
numbers into one chosen token is the subject of this module, and there are several
defensible ways to do it that produce different text from the same model.

The four logits above are the lab's `LOGITS`: they are $\ln 0.5$, $\ln 0.3$, $\ln 0.15$
and $\ln 0.05$, chosen so that the probabilities they encode can be read off by eye.

## Logits to probabilities

Positive, summing to one, order-preserving: exponentiate and normalise, as in module 4.
$e^{\ln 0.5} = 0.5$ and so on, so softmax of these logits returns
$[0.5, 0.3, 0.15, 0.05]$ — and the lab's test checks that recovery to twelve places.

Now add one dial. Divide every logit by a *temperature* $T$ before the softmax. Since
$e^{z/T} = (e^{z})^{1/T}$, and $e^{z_i}$ is proportional to $p_i$, the result is
proportional to $p_i^{1/T}$. So $T = 0.5$ squares the probabilities and renormalises:
$[0.25, 0.09, 0.0225, 0.0025]$ over their sum $0.365$ is $[0.685, 0.247, 0.062, 0.007]$.
$T = 2$ takes square roots: $[0.707, 0.548, 0.387, 0.224]$ over $1.866$ is
$[0.379, 0.294, 0.208, 0.120]$.

```python
import math

logits = [math.log(0.5), math.log(0.3), math.log(0.15), math.log(0.05)]


def softmax(logits, temperature=1.0):
    scaled = [x / temperature for x in logits]
    top = max(scaled)
    exps = [math.exp(x - top) for x in scaled]
    return [e / sum(exps) for e in exps]


for t in (1.0, 0.5, 2.0, 0.1, 10.0):
    print(f"T = {t:<4}", [round(p, 3) for p in softmax(logits, t)])
```

Below 1 the distribution sharpens toward its peak; at $T = 0.1$ the top token has $0.994$
of the mass. Above 1 it flattens; at $T = 10$ the four are within $0.06$ of each other.
In the limit $T \to 0$ every bit of mass sits on the largest logit, and $T \to \infty$
is uniform. $T = 0$ itself is a division by zero, and the lab's `softmax` raises
`ValueError` for it rather than pretend. Note the order in the code: scale first, then
subtract the maximum. Subtracting first and scaling after gives a different, wrong
answer, because the shift is no longer the same constant across the logits once divided.

## Four ways to pick

**Greedy** takes the largest logit, index 0 here, on every step — the lowest index on a
tie, so that it is a function and not a coin. It is deterministic and it is what you want
when there is one right answer. Its failure mode is a loop:

```python
table = {"the": "cat", "cat": "sat", "sat": "on", "on": "the"}
word = "the"
out = [word]
for _ in range(9):
    word = table[word]
    out.append(word)
print(" ".join(out))
```

`the cat sat on the cat sat on the cat`. A model whose likeliest next word after `on` is
`the`, and after `the` is `cat`, will say so for ever under greedy decoding, and real
models do exactly this. The fix is to sample — draw from the distribution instead of
taking its mode — and the remaining three strategies are ways of sampling without letting
the long tail of unlikely tokens in.

**Top-k** keeps the $k$ largest logits and sets every other to $-\infty$, which softmax
turns into an exact zero. With $k = 2$ on our four, the survivors are $0.5$ and $0.3$,
and renormalised among themselves they become $0.625$ and $0.375$ — the lab's test
asserts that $0.5 / 0.8$.

**Nucleus**, or top-$p$, keeps the smallest set of most-probable tokens whose mass reaches
$p$. Sort by probability, accumulate, stop when the running total reaches $p$. With
$p = 0.8$: $0.5$, then $0.5 + 0.3 = 0.8$ — reached, two tokens. With $p = 0.9$:
$0.8$ is short, add $0.15$ to get $0.95$, three tokens. The lab's brief gives exactly
these two counts.

The difference between the two is what happens when the shape of the distribution
changes:

```python
def nucleus_keep(probs, p, slack=0.0):
    running, kept = 0.0, []
    for i in sorted(range(len(probs)), key=lambda i: -probs[i]):
        kept.append(i)
        running += probs[i]
        if running >= p - slack:
            break
    return kept


for probs in ([0.5, 0.3, 0.15, 0.05], [0.94, 0.02, 0.02, 0.02], [0.25, 0.25, 0.25, 0.25]):
    print(probs, " top-2 keeps 2 tokens;  nucleus 0.8 keeps", len(nucleus_keep(probs, 0.8)))
print("0.7 + 0.1 =", 0.7 + 0.1)
print("without slack:", nucleus_keep([0.7, 0.1, 0.1, 0.1], 0.8))
print("with slack:   ", nucleus_keep([0.7, 0.1, 0.1, 0.1], 0.8, 1e-12))
```

Top-2 keeps two tokens whatever the numbers. Nucleus at $0.8$ keeps two on the first
distribution, one on the peaked one — where top-2 would have let a $0.02$ token in — and
all four on the flat one, where cutting at two would have thrown away half the mass for
no reason. Nucleus cuts by mass; top-k cuts by count; and only mass adapts to how sure
the model is.

The last three lines are the floating-point trap in this function. $0.7 + 0.1$ is
$0.7999999999999999$ in a double, one unit short of $0.8$, so a strict `>=` keeps a third
token that the arithmetic never meant to include. The lab's hint is to compare against
`p - 1e-12`, and the block shows what the slack buys: `[0, 1]` instead of `[0, 1, 2]`.

## Drawing one token

Given probabilities, how do you draw? Lay the four probabilities end to end on the unit
interval: $[0, 0.5)$, $[0.5, 0.8)$, $[0.8, 0.95)$, $[0.95, 1)$. Draw one uniform number
$r$ and see which segment it fell in — the first index at which the running sum exceeds
$r$. That is inverse-transform sampling, and it uses exactly one random number per token.

```python
import random


def sample_index(probs, rng):
    draw = rng.random()
    running = 0.0
    for i, prob in enumerate(probs):
        running += prob
        if draw < running:
            return i
    return len(probs) - 1


probs = [0.5, 0.3, 0.2]
rng = random.Random(7)
print([sample_index(probs, rng) for _ in range(10)])
rng = random.Random(7)
draws = [sample_index(probs, rng) for _ in range(2000)]
print([round(draws.count(i) / 2000, 3) for i in range(3)])
```

Seeded with 7, the first ten draws are `[0, 0, 1, 0, 1, 0, 0, 1, 0, 0]` — the lab's test
asserts that exact list — and over two thousand draws the frequencies are
$[0.515, 0.279, 0.206]$ against the $[0.5, 0.3, 0.2]$ they estimate. The final
`return` is for the case where rounding leaves the running sum a hair under $1$ and the
draw lands in the gap.

## The mistake, and why it looks right

The tempting version draws a fresh random number for each token in turn: "accept token
$i$ with probability $p_i$, otherwise move on".

```python
import random


def coin_per_token(probs, rng):
    for i, prob in enumerate(probs):
        if rng.random() < prob:
            return i
    return len(probs) - 1


probs = [0.5, 0.3, 0.2]
rng = random.Random(7)
draws = [coin_per_token(probs, rng) for _ in range(2000)]
print([round(draws.count(i) / 2000, 3) for i in range(3)])
```

$[0.507, 0.146, 0.346]$. The first token is fine, because its coin is flipped
unconditionally. The second token's coin is only flipped when the first one failed, so it
is chosen with probability $0.5 \times 0.3 = 0.15$, half of what it was owed, and the
third collects everything left over. It looks right because each token *is* accepted with
its own probability — on the occasions its coin is flipped at all. One draw against the
cumulative sum flips no conditional coins.

`sample` in the lab composes the pieces in a fixed order: top-k, then nucleus, then the
temperature softmax, then one draw. The filters are defined on the untempered
distribution — `nucleus_filter` calls `softmax` at $T = 1$ to decide what to keep — and
the temperature is applied to whatever survives.

## How surprised was the model

Sampling picks tokens; something else has to say whether the model is any good. Take a
text the model did not write, feed it through, and record the probability the model gave
to each token that actually came next. A model that assigns $0.9$ to what happened is
doing well; one that assigns $0.01$ is not.

Average those in the right way. The natural quantity is surprise, $-\ln p$, which is 0
for a certainty and grows without bound as $p \to 0$. Average the surprises over the
$n$ tokens and undo the log:

$$\text{perplexity} = \exp\!\left(-\frac{1}{n}\sum_{i=1}^{n} \ln p_i\right)$$

Why undo the log? Because of what the number then means. A model that is uniform over
$N$ choices assigns $p = 1/N$ every time; its mean surprise is $\ln N$, and its perplexity
is $N$. So a perplexity of 4 means "as uncertain as a fair four-way choice", whatever the
vocabulary size. It is the effective number of options the model is hesitating between.

```python
import math


def perplexity(probs):
    return math.exp(-sum(math.log(p) for p in probs) / len(probs))


print(perplexity([0.25, 0.25, 0.25, 0.25]))
print(perplexity([0.5, 0.5]))
print(round(perplexity([0.9, 0.9, 0.9, 0.1]), 4))
print(round(perplexity([0.9, 0.9, 0.9, 0.9]), 4))
print(perplexity([1.0, 1.0, 1.0]))
```

`4.0`, `2.0`, `1.9245`, `1.1111`, `1.0`. The third and fourth lines are worth a look
together: three confident tokens and one at $0.1$ score $1.92$, against $1.11$ for four
confident ones. Because the average is taken in log space, perplexity is a *geometric*
mean of $1/p$ — one token at $1/0.1 = 10$ is a factor of ten shared across four
positions, $10^{1/4} \approx 1.78$ on its own — and a single badly predicted token costs
more than an arithmetic mean would suggest. A probability of exactly 0 has infinite
surprise, and the lab's `perplexity` raises `ValueError` rather than return `inf` and
let it propagate into an average.

## Where the idea stops holding

Perplexity is per *token*, and a token is whatever the tokeniser said it was. A model
over bytes and a model over a 50,000-token vocabulary are predicting different things
per step, and their perplexities cannot be compared; per-byte or per-character
perplexity has to be reconstructed before two such models can be lined up. And a lower
perplexity is not better text. The capstone's model reaches a perplexity under $1.05$ on
its four-character cycle, and greedy decoding from it produces exactly the cycle — which
is correct, and would also be the behaviour of a model that had memorised its training
set and nothing more.

The sampling side has its own edge. Reproducibility depends on the seed and on the
*order* of the cumulative sum, so two implementations that accumulate in different
orders can give different tokens from the same seed and both be right. And every filter
here trusts the model's probabilities: a model that is confidently wrong has a small
nucleus around the wrong answer, and no decoding strategy can fix that.

In the lab, "Four decoding strategies and a perplexity", you write the temperature
softmax with its refusals, `greedy` with its tie rule, the two filters with $-\infty$ as
the mask, `sample_index` with its single draw, `sample` composing them in order, and
`perplexity` — every number in this reading recomputed by your own code, on the same
four logits.
''',
                },
            ],
            "quiz": {
                "title": "Choosing a token, scoring a model",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A temperature of 0.5 turns $[0.5, 0.3, 0.15, 0.05]$ into $[0.685, 0.247, 0.062, 0.007]$. What operation is that on the probabilities?",
                        "opts": [
                            "Each probability squared, then the four renormalised so that they add up to 1 again",
                            "Each probability halved, with the mass that was lost handed over to the largest one",
                            "Each logit halved, which multiplies every probability by the same constant factor",
                            "The top probability doubled and the rest shrunk in proportion so that the total stays 1",
                        ],
                        "a": 0,
                        "whys": [
                            r"$e^{z/T} = (e^z)^{1/T}$, and $1/T = 2$: the squares are $[0.25, 0.09, 0.0225, 0.0025]$, summing to $0.365$.",
                            r"Halving and topping up the largest would give $[0.75, 0.15, 0.075, 0.025]$, which is not the result. The small probabilities shrink far more than by half — $0.05$ becomes $0.007$ — because the operation is a power, not a scale.",
                            r"Halving the logits is what happens, but dividing a logit by 2 does not multiply its probability by a constant — it takes the square root of $e^{z}$, which changes each token by a different factor. Renormalisation then makes the result sum to 1.",
                            r"Doubling $0.5$ gives $1$, leaving nothing for the rest; the actual top value is $0.685$. Temperature is not an adjustment to the top token — it reshapes the whole distribution by a power.",
                        ],
                        "why": r"""
Dividing the logits by $T$ raises each $e^{z_i}$, and hence each $p_i$, to the power
$1/T$. At $T = 0.5$ that is a square: $[0.25, 0.09, 0.0225, 0.0025]$, which sum to
$0.365$, and dividing through gives $[0.685, 0.247, 0.062, 0.007]$. Powers below 1
flatten, powers above 1 sharpen, and the limit $T \to 0$ is the argmax.
""",
                    },
                    {
                        "q": "Top-k with $k = 2$ and nucleus with $p = 0.8$ keep the same two tokens on $[0.5, 0.3, 0.15, 0.05]$. On $[0.94, 0.02, 0.02, 0.02]$?",
                        "opts": [
                            "Top-2 still admits a 0.02 token; nucleus keeps only the first, since it cuts by mass rather than count",
                            "Both keep exactly the first token, because a probability above 0.9 satisfies either rule on its own",
                            "Both keep two tokens, since the two rules coincide whenever the distribution is sorted in descending order",
                            "Nucleus keeps all four, because reaching 0.8 needs the small tokens once the first is taken out",
                        ],
                        "a": 0,
                        "whys": [
                            r"$0.94 \ge 0.8$ after one token, so nucleus stops; top-2 counts to two regardless of how little the second holds.",
                            r"Top-k never looks at the probabilities' sizes, only at their rank — $k = 2$ keeps two tokens on any distribution with two or more entries. Only the nucleus rule notices that $0.94$ is already enough.",
                            r"They coincided on the first distribution by arithmetic accident ($0.5 + 0.3 = 0.8$ exactly). On the peaked one they differ, and on a flat $[0.25] \times 4$ they differ the other way — nucleus keeps all four, top-2 keeps two.",
                            r"The first token is never \"taken out\" — it is the first one *kept*, and it alone reaches the mass target. The accumulation stops the moment the running total is at least $p$.",
                        ],
                        "why": r"""
Top-k cuts by count, nucleus by mass. On the peaked distribution the first token alone
holds $0.94 \ge 0.8$, so nucleus keeps one token and stops; top-2 keeps a $0.02$ token
as well. On a flat distribution the two diverge the other way, with nucleus keeping
everything needed to reach the mass. Mass adapts to how sure the model is; a fixed
count does not.
""",
                    },
                    {
                        "q": "`sample_index` draws one random number and walks the cumulative sum. Drawing a fresh number for each token instead — accept token $i$ with probability $p_i$, else move on — yields what?",
                        "opts": [
                            "A different distribution: a later token is reached only if every earlier coin failed, so its share shrinks",
                            "The same distribution, since each token is still accepted with exactly its own stated probability",
                            "The same distribution but slower, because several random numbers are drawn where one would have done",
                            "Greedy decoding in disguise: the first token whose probability exceeds 0.5 is the one chosen every single time",
                        ],
                        "a": 0,
                        "whys": [
                            r"The reading measured it: $[0.507, 0.146, 0.346]$ for probabilities $[0.5, 0.3, 0.2]$. The middle token gets $0.5 \times 0.3$.",
                            r"Each token is accepted with its own probability *when its coin is flipped*, and its coin is only flipped after every earlier token has declined. The unconditional probability of the second token is $0.5 \times 0.3 = 0.15$, not $0.3$.",
                            r"Speed is not the issue; correctness is. The per-token coins produce conditional acceptances that compound, and the frequencies come out wrong — the middle token at half its due, the last one at nearly double.",
                            r"A coin with probability 0.5 lands either way; the method is random, not greedy. Its defect is that the randomness is distributed wrongly across the tokens, not that it is absent.",
                        ],
                        "why": r"""
Token $i$ is reached only when tokens $0$ to $i-1$ have all declined, so its
unconditional probability is $p_i$ times the product of $(1 - p_j)$ for every earlier
$j$. For $[0.5, 0.3, 0.2]$ that gives $0.5$, $0.15$ and the remaining $0.35$. One
uniform draw against the cumulative sums has no conditional coins in it, which is why
it reproduces the distribution.
""",
                    },
                    {
                        "q": "Why is the perplexity of a uniform distribution over four tokens exactly 4?",
                        "opts": [
                            "Mean surprise is $\\ln 4$ per token, and $e^{\\ln 4}$ recovers the number of equally likely choices",
                            "Perplexity counts the tokens in the vocabulary, whatever probabilities the model assigns to them",
                            "The four probabilities of 0.25 add to 1, and perplexity is the reciprocal of the smallest of them",
                            "Perplexity is the sum of the negative logs, and $-4 \\ln 0.25$ happens to come out at 4",
                        ],
                        "a": 0,
                        "whys": [
                            r"$-\ln 0.25 = \ln 4$ at every position, the mean is $\ln 4$, and the exponential undoes the log.",
                            r"A model that assigns $[1.0, 1.0, 1.0]$ to what occurred has perplexity 1 over the same vocabulary. Perplexity depends entirely on the probabilities given to the tokens that actually occurred.",
                            r"The reciprocal of the smallest probability would make $[0.9, 0.9, 0.9, 0.1]$ score 10; it scores $1.92$. Perplexity is a geometric mean of the reciprocals, not the largest of them.",
                            r"$-4 \ln 0.25$ is about $5.55$, not 4. Perplexity divides the sum of surprises by $n$ *and* exponentiates; leave out either step and the number stops meaning \"effective number of choices\".",
                        ],
                        "why": r"""
Each token that occurred was given $p = 0.25$, so each has surprise $-\ln 0.25 = \ln
4$. The mean surprise is $\ln 4$, and $\exp(\ln 4) = 4$. That is the point of the
exponential: a model that is uniform over $N$ options has perplexity $N$, so the number
reads as "how many equally likely choices the model is hesitating between".
""",
                    },
                    {
                        "q": "A model gives $[0.9, 0.9, 0.9, 0.1]$ to four tokens that occurred, for a perplexity of $1.92$, against $1.11$ for $[0.9, 0.9, 0.9, 0.9]$. Why does one token cost so much?",
                        "opts": [
                            "Perplexity is a geometric mean of $1/p$, so one token at $0.1$ brings a factor of 10 spread over the four",
                            "The arithmetic mean of the probabilities fell from 0.9 to 0.7, and perplexity is the reciprocal of that mean",
                            "The $0.1$ token is treated as an error, and each error adds a fixed penalty of 1 to the perplexity",
                            "A probability under $0.5$ counts as a wrong prediction, and perplexity is one plus the number of wrong ones",
                        ],
                        "a": 0,
                        "whys": [
                            r"$\left(\tfrac{10}{9}\cdot\tfrac{10}{9}\cdot\tfrac{10}{9}\cdot 10\right)^{1/4}$ is $1.92$; the log-space average turns products into sums.",
                            r"$1 / 0.7$ is $1.43$, not $1.92$. Perplexity averages surprises — logarithms — and undoes the log afterwards, which is a geometric mean of $1/p$ and weights a bad token far more heavily than an arithmetic mean would.",
                            r"There is no threshold and no fixed penalty; the cost is continuous in $p$. Change the $0.1$ to $0.01$ and the perplexity rises to $3.4$, to $0.001$ and it is $6$. A penalty of 1 would not move.",
                            r"Perplexity never counts predictions as right or wrong. $[0.4, 0.4, 0.4, 0.4]$ has every token \"wrong\" by that rule and a perplexity of $2.5$, while $[0.9, 0.9, 0.9, 0.1]$ has one \"wrong\" token and scores $1.92$.",
                        ],
                        "why": r"""
Averaging in log space and exponentiating is a geometric mean: perplexity is
$\prod (1/p_i)^{1/n}$. Three tokens at $10/9$ and one at $10$ multiply to $13.7$, and
the fourth root is $1.92$. A single token at $0.1$ carries a factor of ten on its own,
which no amount of confidence elsewhere can average away the way an arithmetic mean
would.
""",
                    },
                    {
                        "q": "Greedy decoding from a model whose likeliest word after `on` is `the`, after `the` is `cat`, and after `sat` is `on`, produces `the cat sat on the cat sat on ...`. What is the root cause?",
                        "opts": [
                            "Greedy takes the likeliest token each step, so a cycle among the likeliest transitions repeats for ever",
                            "The model's position embeddings are defective, so it forgets everything before the most recent token",
                            "Greedy decoding is deterministic, and every deterministic decoder eventually emits a fixed-length cycle",
                            "The temperature defaulted to 1.0, which is too high for greedy decoding to break out of a repeated phrase",
                        ],
                        "a": 0,
                        "whys": [
                            r"`argmax` is a function of the context: same context, same token, and a context that recurs starts the cycle again.",
                            r"The reading's example has no model at all — a four-entry lookup table loops under greedy decoding. Position information does not help when the argmax itself points around a cycle.",
                            r"Determinism is necessary for the loop but not the cause; a deterministic decoder that emitted a non-repeating sequence is perfectly possible. The cause is that the *argmax* transitions form a cycle in this model.",
                            r"Greedy decoding does not use the temperature — it takes the largest logit, and dividing every logit by any positive number leaves the largest one largest. Temperature only matters when sampling.",
                        ],
                        "why": r"""
Greedy decoding is a deterministic function from context to next token. When the
likeliest transitions form a cycle, the context after one lap is the same as before it,
so the same tokens follow, for ever. Sampling — with or without top-k or nucleus
truncation — draws from the distribution instead of taking its mode, and a cycle that
holds with probability 0.6 breaks four times in ten.
""",
                    },
                ],
            },
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
