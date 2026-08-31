"""MA121 — Linear Algebra."""

COURSE = {
    "id": "MA121",
    "title": "Linear Algebra",
    "year": 1,
    "level": "Intermediate",
    "prereqs": ["MA101"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 120,
    "icon": "▦",
    "summary": (
        "Linear algebra written from the ground up in plain Python: no library "
        "hides the arithmetic, so every theorem has to survive contact with "
        "floating point. You build a Matrix type, then Gaussian elimination with "
        "partial pivoting, then LU factorisation, then orthogonalisation and the "
        "power method — and finish with a least-squares engine that reports rank "
        "and conditioning alongside its answer."
    ),
    "outcomes": [
        "Implement matrix addition, scaling, multiplication and transposition from the definitions",
        "Explain why partial pivoting is a numerical necessity rather than a convenience",
        "Compute rank, determinant and solutions by elimination, and detect singular systems",
        "Factor a matrix as PA = LU and reuse the factors for determinants, solves and inverses",
        "Orthonormalise a basis with Gram-Schmidt and derive the QR factorisation from it",
        "Find a dominant eigenpair by power iteration and the smallest by inverse iteration",
        "Solve a least-squares problem and report its rank and condition number honestly",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone engine (60%).",
    "reading": [
        "Strang, *Introduction to Linear Algebra*, 6th ed. — chapters 1-6",
        "Trefethen & Bau, *Numerical Linear Algebra* — lectures 1-11 and 20-27",
        "Axler, *Linear Algebra Done Right*, 4th ed. — chapters 3, 5 and 6",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Vectors, matrices and the algebra of linear maps",
            "summary": "The objects themselves, and the operations that make them an algebra.",
            "concepts": [
                "A matrix is a linear map written in a chosen pair of bases",
                "Addition and scalar multiplication act entrywise; the m-by-n matrices form a vector space",
                "Matrix multiplication is composition of maps, hence associative but not commutative",
                "The (i, j) entry of AB is the dot product of row i of A with column j of B",
                "Shapes compose: (m x k)(k x n) -> (m x n), and nothing else is defined",
                "Transposition reverses products: (AB)^T = B^T A^T",
                "Floating-point equality needs a tolerance, so `equals` takes one and `==` picks a default",
            ],
            "read": [
                {
                    "title": "Why the multiplication rule is not the obvious one",
                    "minutes": 14,
                    "body": r'''
Two tables of numbers of the same size. Adding them is not a question: line them up
and add the entries. Scaling one of them by $3$ is not a question either. Multiplying
them, though, has an obvious answer that almost nobody uses.

The obvious answer is to multiply entrywise, the way you added: put $a_{ij}b_{ij}$ in
position $(i,j)$. It is well defined, it is commutative, it is fast, and it has an
identity — the matrix of all ones. It is a perfectly good operation and it has a name,
the Hadamard product. What it does not do is the one thing matrices exist to do.

The rule everyone actually means is stranger. To multiply an $m\times k$ matrix by a
$k\times n$ matrix you take a *row* of the first, a *column* of the second, multiply
them term by term and add the results — and you do that $mn$ times. The shapes have to
agree in a specific direction. The result is not commutative. Nothing about it looks
like arithmetic. Where does it come from, and why is it worth the trouble?

## What a matrix is for

A matrix is not fundamentally a table. It is a **linear map** written down.

A map $T$ from $\mathbf{R}^{k}$ to $\mathbf{R}^{m}$ is linear when it respects the two
operations a vector space has:

$$T(u + v) = T(u) + T(v) \qquad T(cv) = c\,T(v)$$

That is a strong condition. It rules out $T(x) = x + 1$, it rules out squaring, and it
rules out almost everything else you could write down. What survives is rotations,
reflections, projections, shears, scalings, and sums of those — which is to say most
of the geometry and all of the systems of linear equations you will meet.

Here is the consequence that makes matrices possible. Write a vector in
$\mathbf{R}^{2}$ in terms of the standard basis, $v = x e_1 + y e_2$. Then linearity
gives you

$$T(v) = T(x e_1 + y e_2) = x\,T(e_1) + y\,T(e_2)$$

and the whole map has collapsed into two vectors. Once you know where $T$ sends $e_1$
and where it sends $e_2$, you know where it sends everything, forever. Those two
images, written as columns side by side, *are* the matrix of $T$:

$$A = \begin{bmatrix} T(e_1) & T(e_2) \end{bmatrix}$$

So a matrix is a list of images of basis vectors, and $Av$ means "combine the columns
of $A$ with the weights in $v$". Nothing has been invented yet — this is just the
definition of linear, written out.

## Composition forces the rule

Now take two maps. $B$ acts on $\mathbf{R}^{2}$, then $A$ acts on the result. The
composite is a map too, and it is linear (check: it respects sums and scalings because
both halves do). So it has a matrix. Call that matrix $AB$. We are not free to choose
what $AB$ means; the composite already exists, and $AB$ is whatever matrix it has.

Feed it $v = (x, y)$ and follow the arithmetic. First $B$:

$$Bv = \begin{bmatrix} b_{11}x + b_{12}y \\ b_{21}x + b_{22}y \end{bmatrix}$$

Now apply $A$ to that. The first component of $A$ applied to a vector $(p, q)$ is
$a_{11}p + a_{12}q$, so

$$(A(Bv))_1 = a_{11}(b_{11}x + b_{12}y) + a_{12}(b_{21}x + b_{22}y)$$

Expand and collect the $x$ and the $y$:

$$(A(Bv))_1 = (a_{11}b_{11} + a_{12}b_{21})\,x + (a_{11}b_{12} + a_{12}b_{22})\,y$$

The composite is linear, so its first component must be some number times $x$ plus some
number times $y$ — and there they are. The coefficient of $x$ is the $(1,1)$ entry of
the composite's matrix, and it is $a_{11}b_{11} + a_{12}b_{21}$: row $1$ of $A$ against
column $1$ of $B$. Do the same for the second component and the pattern repeats. In
general

$$(AB)_{ij} = \sum_{k} a_{ik} b_{kj}$$

The rule was not chosen. It is what falls out of "do $B$, then do $A$", and every
strange feature of it is inherited. The index $k$ runs over the *columns* of $A$ and
the *rows* of $B$, so those two counts must match — that is the shape rule
$(m\times k)(k\times n) \to (m\times n)$, and it is not a convention but a statement
that the output of $B$ has to be something $A$ can eat.

## Worked: a $2\times 3$ against a $3\times 2$

$$A = \begin{bmatrix} 1 & 2 & -1 \\ 0 & 3 & 4 \end{bmatrix} \qquad B = \begin{bmatrix} 2 & 0 \\ 1 & -3 \\ 5 & 1 \end{bmatrix}$$

$A$ is $2\times3$ and $B$ is $3\times2$, the inner $3$s agree, so $AB$ is $2\times2$.
Four entries, each a sum of three products.

$$(AB)_{11} = 1\cdot 2 + 2\cdot 1 + (-1)\cdot 5 = 2 + 2 - 5 = -1$$
$$(AB)_{12} = 1\cdot 0 + 2\cdot(-3) + (-1)\cdot 1 = 0 - 6 - 1 = -7$$
$$(AB)_{21} = 0\cdot 2 + 3\cdot 1 + 4\cdot 5 = 0 + 3 + 20 = 23$$
$$(AB)_{22} = 0\cdot 0 + 3\cdot(-3) + 4\cdot 1 = 0 - 9 + 4 = -5$$
$$AB = \begin{bmatrix} -1 & -7 \\ 23 & -5 \end{bmatrix}$$

Now turn the pair round. $B$ is $3\times2$, $A$ is $2\times3$, the inner $2$s agree, so
$BA$ exists as well — and it is $3\times3$:

$$(BA)_{11} = 2\cdot1 + 0\cdot0 = 2 \qquad (BA)_{12} = 2\cdot2 + 0\cdot3 = 4 \qquad (BA)_{13} = 2\cdot(-1) + 0\cdot4 = -2$$
$$(BA)_{21} = 1\cdot1 + (-3)\cdot0 = 1 \qquad (BA)_{22} = 1\cdot2 + (-3)\cdot3 = -7 \qquad (BA)_{23} = 1\cdot(-1) + (-3)\cdot4 = -13$$
$$(BA)_{31} = 5\cdot1 + 1\cdot0 = 5 \qquad (BA)_{32} = 5\cdot2 + 1\cdot3 = 13 \qquad (BA)_{33} = 5\cdot(-1) + 1\cdot4 = -1$$
$$BA = \begin{bmatrix} 2 & 4 & -2 \\ 1 & -7 & -13 \\ 5 & 13 & -1 \end{bmatrix}$$

$AB$ and $BA$ are not merely different numbers here. They are different *sizes*. Any
instinct that $AB$ and $BA$ ought to be comparable has to die at this example.

## Worked: the case people get wrong

Take two maps of the plane whose geometry you can see.

$$P = \begin{bmatrix} 1 & 0 \\ 0 & 0 \end{bmatrix} \qquad R = \begin{bmatrix} 0 & -1 \\ 1 & 0 \end{bmatrix}$$

$P$ flattens everything onto the horizontal axis: $P(x,y) = (x, 0)$. $R$ turns the
plane a quarter turn anticlockwise: $R(x,y) = (-y, x)$. Both are square, both are
$2\times2$, so both orders are defined and both give $2\times2$ answers. Compute them.

$$(RP)_{11} = 0\cdot1 + (-1)\cdot0 = 0 \qquad (RP)_{12} = 0\cdot0 + (-1)\cdot0 = 0$$
$$(RP)_{21} = 1\cdot1 + 0\cdot0 = 1 \qquad (RP)_{22} = 1\cdot0 + 0\cdot0 = 0$$
$$RP = \begin{bmatrix} 0 & 0 \\ 1 & 0 \end{bmatrix} \qquad PR = \begin{bmatrix} 0 & -1 \\ 0 & 0 \end{bmatrix}$$

where the second one comes out of $(PR)_{11} = 1\cdot0 + 0\cdot1 = 0$,
$(PR)_{12} = 1\cdot(-1) + 0\cdot0 = -1$, and a row of zeros underneath.

Read them as maps and the difference is not subtle. $RP$ sends $(x,y)$ to $(0, x)$:
flatten onto the horizontal axis first, then rotate that axis onto the vertical one, so
everything ends up on the vertical axis. $PR$ sends $(x,y)$ to $(-y, 0)$: rotate first,
then flatten, so everything ends up on the horizontal axis. The two composites have
*perpendicular images*. Squashing a photograph and then turning it is not the same as
turning it and then squashing it, and no amount of algebra was ever going to make it so.

Two conventions are worth fixing here, because they cause more confusion than the rule
itself. In $AB$ the matrix on the **right acts first**, because that is the one standing
next to the vector in $A(Bv)$. And the letters are usually written in the order of the
maps, not the order of the operations — so "project then rotate" is the product $RP$,
read right to left.

## The mistake, and why it is tempting

The mistake is to assume $AB = BA$ and then reorder a product to make something cancel.
It is tempting for a good reason: every product you had multiplied before this course
commuted. Integers commute, reals commute, complex numbers commute, polynomials commute.
The notation $AB$ is the same juxtaposition used for all of them, so the hand writes
$ABA^{-1}B^{-1} = I$ before the head has objected.

The cure is to remember what the letters stand for. $A$ and $B$ are *actions*, and the
order in which you do two things is part of what you did. There is nothing to prove here
and nothing to feel bad about; there is only a habit to break.

A second mistake, rarer but more damaging, is to expect the number system's other
comforts to survive. They do not. If $AB = 0$ with numbers, one of them is zero. With
matrices, take $N = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}$; then $N^2$ has
$(1,1)$ entry $0\cdot0 + 1\cdot0 = 0$ and $(1,2)$ entry $0\cdot1 + 1\cdot0 = 0$, and the
bottom row was zero to start with, so $N^2 = 0$ although $N \neq 0$. A non-zero matrix
can square to nothing, and that single example destroys the "divide both sides by $A$"
move for good.

## Where the rule stops

It stops at the shapes, and it stops hard. $AB$ requires the columns of $A$ to number
the same as the rows of $B$; there is no partial credit, no broadcasting, no padding.
That is why the lab raises `ValueError` rather than guessing.

It stops at commutativity, always — except in the special cases where it happens to
hold: any matrix commutes with $I$, with itself, with its own powers, and with any
scalar multiple of $I$. Those exceptions are exactly the ones you will use, which is
part of why the general failure is so easy to forget.

And it stops being *the* product only in the sense that other products exist. The
Hadamard product from the opening paragraph is genuinely useful — it is how you mask an
image or apply a per-pixel gain — but it does not compose maps, so it has no place in a
course whose subject is what linear maps do. When this course writes $AB$, it always
means the composition.
''',
                },
                {
                    "title": "Which rearrangements are legal",
                    "minutes": 13,
                    "body": r'''
You have just been told that $AB$ and $BA$ are different matrices. That is one
rearrangement forbidden. Which ones are still allowed? Can you move brackets? Can you
expand $(A+B)^2$? Can you transpose a product a factor at a time? Every one of those
moves is something you have done a thousand times with numbers, and each has to be
re-examined now that the multiplication has changed.

The answers are not a list to memorise. Two of the three are true, one is false, and in
each case the reason is visible in the definition.

## Brackets move freely, and the proof is one sentence

$$(AB)C = A(BC)$$

Both sides are the matrix of the same map: do $C$, then $B$, then $A$. Composition of
functions is associative because "apply $f$ to the result of applying $g$ to the result
of applying $h$" does not contain a bracket in the first place — the brackets are an
artefact of writing it down in a line. Since a matrix is only a linear map in
coordinates, and the product is only composition in coordinates, the matrices must
agree.

If you would rather see it in the entries, the argument is an exchange of summation
order:

$$((AB)C)_{ij} = \sum_{l} (AB)_{il} c_{lj} = \sum_{l} \left( \sum_{k} a_{ik} b_{kl} \right) c_{lj} = \sum_{k}\sum_{l} a_{ik} b_{kl} c_{lj}$$
$$(A(BC))_{ij} = \sum_{k} a_{ik} (BC)_{kj} = \sum_{k} a_{ik} \left( \sum_{l} b_{kl} c_{lj} \right) = \sum_{k}\sum_{l} a_{ik} b_{kl} c_{lj}$$

Same double sum, same terms, written in a different order. The exchange is free because
the sums are finite; nothing is being assumed about convergence. The hypothesis that
does matter is on the *shapes*: $A$ must be $m\times k$, $B$ must be $k\times l$ and $C$
must be $l\times n$, or one of those products does not exist and the identity has
nothing to say.

### Worked: a bracket move, checked

$$A = \begin{bmatrix} 1 & 2 \\ 0 & 1 \end{bmatrix} \quad B = \begin{bmatrix} 3 & 0 \\ -1 & 2 \end{bmatrix} \quad C = \begin{bmatrix} 1 & 1 \\ 2 & 0 \end{bmatrix}$$

Left first:

$$AB = \begin{bmatrix} 1\cdot3 + 2\cdot(-1) & 1\cdot0 + 2\cdot2 \\ 0\cdot3 + 1\cdot(-1) & 0\cdot0 + 1\cdot2 \end{bmatrix} = \begin{bmatrix} 1 & 4 \\ -1 & 2 \end{bmatrix}$$
$$(AB)C = \begin{bmatrix} 1\cdot1 + 4\cdot2 & 1\cdot1 + 4\cdot0 \\ -1\cdot1 + 2\cdot2 & -1\cdot1 + 2\cdot0 \end{bmatrix} = \begin{bmatrix} 9 & 1 \\ 3 & -1 \end{bmatrix}$$

Right first:

$$BC = \begin{bmatrix} 3\cdot1 + 0\cdot2 & 3\cdot1 + 0\cdot0 \\ -1\cdot1 + 2\cdot2 & -1\cdot1 + 2\cdot0 \end{bmatrix} = \begin{bmatrix} 3 & 3 \\ 3 & -1 \end{bmatrix}$$
$$A(BC) = \begin{bmatrix} 1\cdot3 + 2\cdot3 & 1\cdot3 + 2\cdot(-1) \\ 0\cdot3 + 1\cdot3 & 0\cdot3 + 1\cdot(-1) \end{bmatrix} = \begin{bmatrix} 9 & 1 \\ 3 & -1 \end{bmatrix}$$

Identical, as promised. The intermediate matrices $AB$ and $BC$ were completely
different; only the ends had to agree.

## Associativity is worth money

Mathematically the bracketing is a free choice. Computationally it is not, and the gap
is enormous. Multiplying an $m\times k$ by a $k\times n$ costs $mnk$ scalar
multiplications — one per term of each of the $mn$ sums, each sum having $k$ terms.

Take $A$ of shape $3\times50$, $B$ of shape $50\times2$, $C$ of shape $2\times40$.

$$(AB)C: \quad 3\cdot50\cdot2 = 300 \;\text{ then }\; 3\cdot2\cdot40 = 240 \quad\Rightarrow\quad 540$$
$$A(BC): \quad 50\cdot2\cdot40 = 4000 \;\text{ then }\; 3\cdot50\cdot40 = 6000 \quad\Rightarrow\quad 10000$$

Eighteen times the work for a bit-for-bit identical answer, because the second route
inflates a $50\times2$ and a $2\times40$ into a $50\times40$ before ever touching the
small matrix $A$. The general problem of choosing the cheapest bracketing over a long
chain is a classic dynamic-programming exercise; the point here is only that
associativity is what makes the question askable at all.

## The square of a sum is not what you remember

$(A+B)^2$ means $(A+B)(A+B)$. The distributive law does hold — it comes straight from
the definition, since every entry of the product is linear in each factor separately —
so expand honestly:

$$(A+B)(A+B) = A^2 + AB + BA + B^2$$

and stop. Collecting $AB + BA$ into $2AB$ is the step that requires commutativity, and
it is not available.

### Worked: the same expansion, twice, with numbers

$$A = \begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix} \qquad B = \begin{bmatrix} 1 & 0 \\ 1 & 1 \end{bmatrix} \qquad A + B = \begin{bmatrix} 2 & 1 \\ 1 & 2 \end{bmatrix}$$
$$(A+B)^2 = \begin{bmatrix} 2\cdot2 + 1\cdot1 & 2\cdot1 + 1\cdot2 \\ 1\cdot2 + 2\cdot1 & 1\cdot1 + 2\cdot2 \end{bmatrix} = \begin{bmatrix} 5 & 4 \\ 4 & 5 \end{bmatrix}$$

Now the pieces:

$$A^2 = \begin{bmatrix} 1 & 2 \\ 0 & 1 \end{bmatrix} \quad B^2 = \begin{bmatrix} 1 & 0 \\ 2 & 1 \end{bmatrix} \quad AB = \begin{bmatrix} 2 & 1 \\ 1 & 1 \end{bmatrix} \quad BA = \begin{bmatrix} 1 & 1 \\ 1 & 2 \end{bmatrix}$$

Adding the four:

$$A^2 + AB + BA + B^2 = \begin{bmatrix} 1+2+1+1 & 2+1+1+0 \\ 0+1+1+2 & 1+1+2+1 \end{bmatrix} = \begin{bmatrix} 5 & 4 \\ 4 & 5 \end{bmatrix}$$

which matches. The remembered formula does not:

$$A^2 + 2AB + B^2 = \begin{bmatrix} 1+4+1 & 2+2+0 \\ 0+2+2 & 1+2+1 \end{bmatrix} = \begin{bmatrix} 6 & 4 \\ 4 & 4 \end{bmatrix}$$

Two of the four entries are wrong. Notice *why* — $AB \neq BA$ here by exactly the
amount that the two answers differ, $AB - BA = \begin{bmatrix} 1 & 0 \\ 0 & -1 \end{bmatrix}$,
and adding that to the wrong answer recovers the right one. The discrepancy is the
commutator, and it is the thing you were silently assuming to be zero.

## Transposition reverses the order

$$(AB)^{\mathsf{T}} = B^{\mathsf{T}} A^{\mathsf{T}}$$

Take it in indices. By definition of the transpose, the $(i,j)$ entry of
$(AB)^{\mathsf{T}}$ is the $(j,i)$ entry of $AB$:

$$((AB)^{\mathsf{T}})_{ij} = (AB)_{ji} = \sum_{k} a_{jk} b_{ki}$$

Rewrite each factor with its own transpose: $a_{jk} = (A^{\mathsf{T}})_{kj}$ and
$b_{ki} = (B^{\mathsf{T}})_{ik}$. Substituting, and then reordering the two numbers
inside the sum — they are scalars, and scalars commute —

$$\sum_{k} (A^{\mathsf{T}})_{kj} (B^{\mathsf{T}})_{ik} = \sum_{k} (B^{\mathsf{T}})_{ik} (A^{\mathsf{T}})_{kj} = (B^{\mathsf{T}} A^{\mathsf{T}})_{ij}$$

The reversal is forced by the index $k$: it has to stay glued between the two factors,
and after the transpose it has moved from the second slot of $A$ and the first slot of
$B$ to the first slot of $A^{\mathsf{T}}$ and the second slot of $B^{\mathsf{T}}$. The
only way to put it back in the middle is to swap the factors.

The shapes say the same thing without any algebra. If $A$ is $m\times k$ and $B$ is
$k\times n$, then $(AB)^{\mathsf{T}}$ is $n\times m$. And $B^{\mathsf{T}}A^{\mathsf{T}}$
is $(n\times k)(k\times m)$, which is $n\times m$ — it fits. Whereas
$A^{\mathsf{T}}B^{\mathsf{T}}$ is $(k\times m)(n\times k)$, which does not even exist
unless $m = n$, and is the wrong shape when it does. The wrong rule is usually not
merely false; it is not type-correct.

## The other move that is gone: cancelling

With numbers, $ab = ac$ and $a \neq 0$ give $b = c$. With matrices it fails, and the
counterexample is small:

$$A = \begin{bmatrix} 1 & 0 \\ 0 & 0 \end{bmatrix} \quad B = \begin{bmatrix} 1 & 2 \\ 3 & 4 \end{bmatrix} \quad C = \begin{bmatrix} 1 & 2 \\ 5 & 6 \end{bmatrix}$$
$$AB = \begin{bmatrix} 1 & 2 \\ 0 & 0 \end{bmatrix} = AC \qquad \text{yet} \qquad B \neq C$$

$A$ is not the zero matrix, and the products are equal anyway, because $A$ throws away
the second row of whatever it multiplies and the two matrices differ only there.
Cancellation needs $A$ to be *invertible*, not merely non-zero — a distinction that has
no counterpart in the real numbers, where the only non-invertible number is zero. Module
2 gives you the test for it.

## Where these stop

Associativity never fails for real or complex matrices of compatible shape; that one is
safe. Distribution never fails. Transposition reversal never fails.

Every other reflex you have from school arithmetic is suspect until checked, and the
three that bite hardest are commuting factors, collecting $AB + BA$ into $2AB$, and
cancelling a common left factor. Two of them appear in the same line whenever anyone
expands a binomial in a hurry.

There is one more caveat, and it belongs to the machine rather than to the mathematics.
$(AB)C$ and $A(BC)$ are equal as matrices of real numbers and are *not* generally equal
as arrays of floating-point numbers, because the two routes round in different places.
The next reading is about what to do with that.
''',
                },
                {
                    "title": "When two computed matrices count as equal",
                    "minutes": 12,
                    "body": r'''
The lab asks you to write `a.equals(b, tol=1e-9)` rather than `a == b`, and to make
`==` call it with a default. That looks like a fussy detail of the interface. It is not:
it is the first place in this course where the mathematics and the machine disagree, and
the disagreement never goes away afterwards.

The question is simple to state. You compute $AB$ two different ways and want to know
whether you got the same matrix. Why can you not just compare the entries?

## What a `float` actually holds

A Python `float` is an IEEE 754 double: a sign, an 11-bit exponent, and a 53-bit
significand. Fifty-three bits is about sixteen decimal digits, and the crucial word is
*about* — the spacing between representable numbers is proportional to their size, not
fixed. Near $1$ the gap to the next double is $2^{-52} \approx 2.22\times10^{-16}$; near
$10^{6}$ it is about $1.16\times10^{-10}$; near $10^{16}$ it is $2$.

Half that relative gap is the unit roundoff,
$u = 2^{-53} \approx 1.11\times 10^{-16}$, and it is the whole budget you have. Every
elementary operation obeys

$$\mathrm{fl}(a \circ b) = (a \circ b)(1 + \delta), \qquad |\delta| \le u$$

so each individual multiplication and each individual addition is as good as it could
possibly be. The trouble is never one operation. It is what happens when you chain
thousands of them, which is precisely what a matrix product does.

The famous symptom is that $0.1 + 0.2$ does not equal $0.3$. Neither $0.1$ nor $0.2$ nor
$0.3$ is representable in binary at all — each is stored as the nearest double — and the
rounded sum of the first two lands one step away from the rounded value of the third.
The difference is $5.55\times10^{-17}$, which is not a bug and cannot be fixed by
choosing better code. Writing `x == y` on floats is asking whether two computations
rounded identically, which is a much stronger question than whether they agree.

## Where the error lives in a matrix product

Each entry of $AB$ is a dot product of length $k$:

$$(AB)_{ij} = \sum_{n=1}^{k} a_{in}b_{nj}$$

That is $k$ multiplications and $k-1$ additions, each rounding. Accumulating the
standard bound over them gives, to first order,

$$| \mathrm{fl}((AB)_{ij}) - (AB)_{ij} | \;\le\; k\,u \sum_{n=1}^{k} |a_{in}| \, |b_{nj}|$$

Read the right-hand side carefully, because it explains everything that follows. The
error is bounded by a term proportional to the sum of the **magnitudes** of the
products — not to the magnitude of the answer. When the terms all have the same sign the
two are comparable and the relative error stays near $ku$. When the terms cancel, the
answer is small while the sum of magnitudes is not, and the relative error can be
arbitrarily bad.

### Worked: three numbers, two orders, two answers

Add $10^{16}$, $-10^{16}$ and $1$. Exactly, the answer is $1$ whatever order you choose.
In doubles, the spacing near $10^{16}$ is $2$, so $10^{16} + 1$ has to round, and it
rounds down to $10^{16}$:

$$(10^{16} + 1) - 10^{16} \;\to\; 10^{16} - 10^{16} = 0$$
$$(10^{16} - 10^{16}) + 1 \;\to\; 0 + 1 = 1$$

Two orders, two answers, and one of them has lost the entire quantity of interest. This
is not a contrived example dressed up: it is exactly the inner loop of a matrix
multiply, where the order of accumulation is chosen by whoever wrote the loop. It is
also the reason $(AB)C$ and $A(BC)$ — which the previous reading proved equal — come
back as different arrays from a computer.

### Worked: the tolerance that is too tight

Let $A$ and $B$ be $3\times3$ with entries of size around $10^{6}$. Each entry of the
product is a sum of three terms of size around $10^{12}$, so the bound above is roughly

$$3 \times 1.11\times10^{-16} \times 3\times10^{12} \;\approx\; 1.0\times10^{-3}$$

An absolute tolerance of $10^{-9}$ will therefore reject a product that is as accurate
as double precision permits. Nothing is wrong with the code; the tolerance is asking for
thirteen more digits than the format has. Compare relatively instead — the relative
error is about $3.3\times10^{-16}$, comfortably at the noise floor — and the same
computation passes.

### Worked: the tolerance that is too loose

Now the other end. Let the entries be around $10^{-6}$, so the entries of the product are
around $10^{-12}$. An absolute tolerance of $10^{-9}$ now declares *every* such matrix
equal to every other, and equal to the zero matrix as well. A test that always passes is
worse than no test, because it is reported as a pass.

The standard fix is a mixed criterion, absolute for quantities near zero and relative
elsewhere:

$$|x - y| \le \varepsilon_{\text{abs}} + \varepsilon_{\text{rel}}\,|y|$$

with $\varepsilon_{\text{rel}}$ a modest multiple of $ku$ and $\varepsilon_{\text{abs}}$
set by the scale below which you genuinely do not care. The lab keeps a single absolute
tolerance because everything it tests is of order one, where the two criteria coincide.
Say that to yourself as you write it, so that the day the entries are not of order one
you remember which assumption you made.

## Two consequences for the interface

The first is that shape has to be checked before any entry is. Two matrices of different
shapes are not nearly equal or approximately equal; the question does not arise, and the
answer is `False` rather than an exception, because "are these the same?" is a
perfectly reasonable thing to ask about two objects that turn out not to be. The same
goes for comparing a `Matrix` against a string: the honest answer is `False`, not a
`TypeError` thrown at whoever asked.

The second is that this equality is not an equivalence relation. Reflexive, yes;
symmetric, yes; transitive, **no**. With a tolerance of $1$, the numbers $0$ and $1$ are
equal, $1$ and $2$ are equal, and $0$ and $2$ are not. Nothing can be done about that,
and it has a practical edge: an object whose equality is approximate cannot sensibly be
a dictionary key or a set member, because hashing needs exact equality to work. That is
why the lab defines `__eq__` and stops there, and why defining `__hash__` alongside it
would be a mistake rather than an omission.

## The mistake, and why it is tempting

The mistake is `if a == b` on computed floats, and it is tempting because it is *true*
often enough to look right. Small integer matrices multiply exactly — every product and
every partial sum is an integer well under $2^{53}$, so nothing rounds, and the test
passes. You write the check, the tests are green, and the assumption ships. It fails the
first time a division or an irrational number enters, which in this course is the
Gram-Schmidt module, several weeks after the decision was made.

The second mistake is subtler: choosing a tolerance by tuning it until the test passes.
That converts the check into a record of what your code currently does. A tolerance
should come from the arithmetic — how many terms, at what scale, with how much
cancellation — and be written down with its reason.

## Where a tolerance stops helping

It stops at conditioning. Some problems amplify small perturbations of the input into
large changes in the output, and no tolerance on the comparison at the end tells you
that has happened. Two matrices can agree to fifteen digits and behave completely
differently:

$$\begin{bmatrix} 1 & 0 \\ 0 & 10^{-15} \end{bmatrix} \quad\text{and}\quad \begin{bmatrix} 1 & 0 \\ 0 & 0 \end{bmatrix}$$

are equal under any tolerance looser than $10^{-15}$, yet one is invertible and one is
not, and their inverses are as far apart as two matrices can get. Entrywise closeness is
not closeness of the maps. The right measurement is the condition number, and the last
module of this course is where it arrives, alongside a least-squares engine that reports
it rather than hiding it.

Until then, one habit is enough: never compare computed floats with `==`, and always be
able to say where your tolerance came from.
''',
                },
            ],
            "derive": [
                {
                    "title": "The product rule, forced by composition",
                    "minutes": 14,
                    "vars": ["a_11", "a_12", "a_21", "a_22",
                             "b_11", "b_12", "b_21", "b_22", "x", "y"],
                    "brief": r'''
$A$ and $B$ are both $2\times2$. Write their entries $a_{ij}$ and $b_{ij}$, first index
the row and second the column, and let $v = (x, y)$.

Nothing below assumes any rule for multiplying two matrices — that is the thing being
derived. One fact is assumed, and it is the definition of how a matrix acts on a
vector: the first component of $A$ applied to $(p, q)$ is $a_{11}p + a_{12}q$, and the
second is $a_{21}p + a_{22}q$.

Push $v$ through $B$, then through $A$, and read the rule off the coefficients.
''',
                    "steps": [
                        {
                            "prompt": "Apply $B$ to $v = (x, y)$. What is the **first** component of $Bv$?",
                            "answer": "b_{11} x + b_{12} y",
                            "hint": "Row $1$ of $B$ against the two entries of $v$: the left entry of that row multiplies $x$, the right entry multiplies $y$.",
                        },
                        {
                            "prompt": "And the **second** component of $Bv$?",
                            "answer": "b_{21} x + b_{22} y",
                            "hint": "The same again with row $2$. Remember the convention: the first index of an entry is the row it lives in, so both entries of row $2$ start with a $2$.",
                        },
                        {
                            "prompt": "Now push that vector through $A$. Write the **first** component of $A(Bv)$ in terms of the $a$'s, the $b$'s, $x$ and $y$. You may leave the brackets unexpanded.",
                            "answer": "a_{11}(b_{11} x + b_{12} y) + a_{12}(b_{21} x + b_{22} y)",
                            "hint": "You are applying $A$ to the vector $(p, q)$ whose components you wrote in the last two steps. Substitute them into $a_{11}p + a_{12}q$.",
                            "deconstruct": [
                                "The vector coming out of $B$ is $p = b_{11}x + b_{12}y$ and $q = b_{21}x + b_{22}y$.",
                                "The first component of $A$ acting on $(p, q)$ is $a_{11}p + a_{12}q$ \u2014 that is the definition, nothing more.",
                                "Substitute the two expressions for $p$ and $q$ and stop. No multiplication rule for matrices has been used anywhere.",
                            ],
                        },
                        {
                            "prompt": "Expand that and collect the terms. What multiplies $x$?",
                            "answer": "a_{11} b_{11} + a_{12} b_{21}",
                            "hint": "Two of the four expanded terms carry an $x$: one from each bracket.",
                            "deconstruct": [
                                "Expanding gives $a_{11}b_{11}x + a_{11}b_{12}y + a_{12}b_{21}x + a_{12}b_{22}y$.",
                                "The first and third terms carry $x$; factor it out.",
                                "What is left in front of $x$ is row $1$ of $A$ against column $1$ of $B$ \u2014 which is exactly what the multiplication rule will claim for $(AB)_{11}$.",
                            ],
                        },
                        {
                            "prompt": "From the same expression: what multiplies $y$?",
                            "answer": "a_{11} b_{12} + a_{12} b_{22}",
                            "hint": "The other two terms. This one should come out as row $1$ of $A$ against column $2$ of $B$.",
                        },
                        {
                            "prompt": "Repeat the whole thing for the **second** component of $A(Bv)$, which is $a_{21}p + a_{22}q$. What multiplies $x$ there?",
                            "answer": "a_{21} b_{11} + a_{22} b_{21}",
                            "hint": "Same substitution, same collection, but starting from row $2$ of $A$. The column of $B$ is fixed by which variable you are collecting \u2014 $x$ picks out column $1$.",
                        },
                    ],
                    "closing": r'''
The composite map is linear, so its first component has to be *some* number times $x$
plus *some* number times $y$. Those numbers are forced, and you have just computed them.
Assembling all four:

$$AB = \begin{bmatrix} a_{11}b_{11} + a_{12}b_{21} & a_{11}b_{12} + a_{12}b_{22} \\ a_{21}b_{11} + a_{22}b_{21} & a_{21}b_{12} + a_{22}b_{22} \end{bmatrix}$$

Every entry is a row of $A$ against a column of $B$, and in general

$$(AB)_{ij} = \sum_{k} a_{ik} b_{kj}$$

Two things fall out for free. The index $k$ ran over the columns of $A$ and the rows of
$B$ at the same time, so those counts must agree — that is the shape rule
$(m\times k)(k\times n) \to (m\times n)$, and it is a fact about composition rather than
a convention. And the rule is not symmetric in $A$ and $B$: $A$ contributes rows, $B$
contributes columns, and swapping them asks a different question. That asymmetry is the
whole of why $AB \neq BA$.
''',
                },
                {
                    "title": "Associativity, one bracket at a time",
                    "minutes": 13,
                    "vars": ["u_1", "u_2", "v_1", "v_2", "a_11", "a_12", "a_21", "a_22"],
                    "brief": r'''
Let $u$ be a $1\times2$ row, $A$ a $2\times2$ matrix and $v$ a $2\times1$ column:

$$u = \begin{bmatrix} u_1 & u_2 \end{bmatrix} \qquad A = \begin{bmatrix} a_{11} & a_{12} \\ a_{21} & a_{22} \end{bmatrix} \qquad v = \begin{bmatrix} v_1 \\ v_2 \end{bmatrix}$$

The chain $uAv$ has shapes $(1\times2)(2\times2)(2\times1)$, so it comes out $1\times1$ —
a single number. There are two ways to bracket it, and the claim is that they agree.

Compute both, all the way to the bottom, and compare what you get.
''',
                    "steps": [
                        {
                            "prompt": "Take the left bracketing first. $uA$ is a $1\\times2$ row. What is its **first** entry?",
                            "answer": "u_1 a_{11} + u_2 a_{21}",
                            "hint": "A row times a matrix: the row runs along, the column of $A$ runs down. For entry $1$ you need column $1$ of $A$, which is $a_{11}$ above $a_{21}$.",
                        },
                        {
                            "prompt": "And the **second** entry of $uA$?",
                            "answer": "u_1 a_{12} + u_2 a_{22}",
                            "hint": "Column $2$ of $A$ this time: $a_{12}$ above $a_{22}$.",
                        },
                        {
                            "prompt": "Multiply that row by $v$. Write $(uA)v$ in full, in terms of $u_1, u_2, v_1, v_2$ and the entries of $A$.",
                            "answer": "(u_1 a_{11} + u_2 a_{21}) v_1 + (u_1 a_{12} + u_2 a_{22}) v_2",
                            "hint": "A $1\\times2$ row against a $2\\times1$ column is one dot product: first entry times $v_1$, plus second entry times $v_2$.",
                            "deconstruct": [
                                "The row you have is $(u_1a_{11} + u_2a_{21},\\; u_1a_{12} + u_2a_{22})$.",
                                "Dotting it with $(v_1, v_2)$ multiplies the first entry by $v_1$ and the second by $v_2$, then adds.",
                                "Expanded, that is four terms: $u_1a_{11}v_1 + u_2a_{21}v_1 + u_1a_{12}v_2 + u_2a_{22}v_2$.",
                            ],
                        },
                        {
                            "prompt": "Now start again from the right. $Av$ is a $2\\times1$ column. What is its **first** entry?",
                            "answer": "a_{11} v_1 + a_{12} v_2",
                            "hint": "Row $1$ of $A$ against the column $v$. This is a row of $A$, not a column \u2014 the indices come out the other way up from step 1.",
                        },
                        {
                            "prompt": "And the **second** entry of $Av$?",
                            "answer": "a_{21} v_1 + a_{22} v_2",
                            "hint": "Row $2$ of $A$ against $v$.",
                        },
                        {
                            "prompt": "Finish the right bracketing: write $u(Av)$ in full.",
                            "answer": "u_1(a_{11} v_1 + a_{12} v_2) + u_2(a_{21} v_1 + a_{22} v_2)",
                            "hint": "The row $u$ against the column you just built: $u_1$ times its first entry plus $u_2$ times its second.",
                        },
                    ],
                    "closing": r'''
Expand the two final expressions and put them side by side:

$$(uA)v = u_1a_{11}v_1 + u_2a_{21}v_1 + u_1a_{12}v_2 + u_2a_{22}v_2$$
$$u(Av) = u_1a_{11}v_1 + u_1a_{12}v_2 + u_2a_{21}v_1 + u_2a_{22}v_2$$

The same four terms, $u_i a_{ij} v_j$ for each of the four choices of $(i,j)$, listed in
a different order. That is the whole content of associativity: both bracketings are
instructions for summing over every path from $v$ through $A$ to $u$, and they differ
only in the order the paths are visited. In general

$$((AB)C)_{ij} = \sum_{k}\sum_{l} a_{ik}b_{kl}c_{lj} = (A(BC))_{ij}$$

and the exchange of the two sums is legal because they are finite.

Notice what associativity does **not** give you. The number $uAv$ is unchanged by moving
the bracket, but nothing here says $uAv = vAu$ — that is not even a legal product, since
$v$ is a column. Reordering the factors and re-bracketing them are different moves, and
only one of them is safe.

This particular chain, with $u$ the transpose of $v$, is the quadratic form
$v^{\mathsf{T}}Av$. It is worth recognising now: it is what the least-squares module at
the end of the course minimises.
''',
                },
                {
                    "title": "Exactly which matrices a shear will commute with",
                    "minutes": 14,
                    "vars": ["a", "b", "c", "d"],
                    "brief": r'''
$$N = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix} \qquad B = \begin{bmatrix} a & b \\ c & d \end{bmatrix}$$

$N$ is the map that sends $(x, y)$ to $(y, 0)$, and $B$ is completely arbitrary. Both
$NB$ and $BN$ exist and both are $2\times2$, so for once the two orders are directly
comparable.

The previous readings said they usually differ. This derivation says exactly how much,
and therefore exactly which $B$ escape. Work out both products, subtract, and read the
condition off the difference.
''',
                    "steps": [
                        {
                            "prompt": "What is $(NB)_{11}$ — row $1$ of $N$ against column $1$ of $B$?",
                            "answer": "c",
                            "hint": "Row $1$ of $N$ is $(0, 1)$ and column $1$ of $B$ is $a$ above $c$. The zero kills one of the two terms.",
                        },
                        {
                            "prompt": "What is $(NB)_{12}$?",
                            "answer": "d",
                            "hint": "Same row of $N$, column $2$ of $B$. Multiplying by $N$ on the left has lifted the bottom row of $B$ into the top row.",
                        },
                        {
                            "prompt": "Now the other order. What is $(BN)_{12}$ — row $1$ of $B$ against column $2$ of $N$?",
                            "answer": "a",
                            "hint": "Row $1$ of $B$ is $(a, b)$ and column $2$ of $N$ is $1$ above $0$. Multiplying by $N$ on the right pushes the left column of $B$ into the right column.",
                        },
                        {
                            "prompt": "What is $(BN)_{22}$?",
                            "answer": "c",
                            "hint": "Row $2$ of $B$ is $(c, d)$, against the same column $2$ of $N$.",
                        },
                        {
                            "prompt": "Subtract. What is the $(1,2)$ entry of the commutator $NB - BN$?",
                            "answer": "d - a",
                            "hint": "You have both pieces already: $(NB)_{12}$ from step 2 and $(BN)_{12}$ from step 3.",
                        },
                        {
                            "prompt": "Row $2$ of $N$ is all zeros, so the whole bottom row of $NB$ is zero. Given that, what is the $(2,2)$ entry of $NB - BN$?",
                            "answer": "-c",
                            "hint": "$(NB)_{22} = 0$, and you computed $(BN)_{22}$ in step 4. Subtract in that order.",
                            "deconstruct": [
                                "$(NB)_{22} = 0\\cdot b + 0\\cdot d = 0$, because row $2$ of $N$ is $(0, 0)$.",
                                "$(BN)_{22} = c\\cdot 1 + d\\cdot 0 = c$, from step 4.",
                                "The commutator entry is $(NB)_{22} - (BN)_{22} = 0 - c$.",
                            ],
                        },
                    ],
                    "closing": r'''
The two remaining entries go the same way: $(NB)_{11} - (BN)_{11} = c - 0 = c$, and the
$(2,1)$ entry is $0 - 0 = 0$. So

$$NB - BN = \begin{bmatrix} c & d - a \\ 0 & -c \end{bmatrix}$$

Set that to the zero matrix and the condition is not a vague "usually not". It is
precise: $c = 0$ and $d = a$. In other words $B$ must look like

$$B = \begin{bmatrix} a & b \\ 0 & a \end{bmatrix} = a I + b N$$

$N$ commutes with exactly the matrices built out of $I$ and $N$ — its own polynomials —
and with nothing else. Out of the four free parameters in $B$, two are spent buying
commutativity.

That is the shape of the general answer, and it is worth carrying forward. Commuting is
not a mild condition that most pairs happen to satisfy; it is a codimension-two
restriction even in the smallest interesting case, and the matrices that satisfy it are
the ones that are, in a sense the eigenvalue modules will make exact, *built from the
same material*.

One more thing to keep. $N \neq 0$, but $N^2 = 0$: applying "take the $y$ component and
put it in the $x$ slot" twice leaves nothing. A non-zero matrix that squares to zero is
the counterexample that kills cancellation, and it is this one.
''',
                },
            ],
            "numeric": [
                {
                    "title": "One entry of a product",
                    "minutes": 5,
                    "brief": r'''
The first rung. One entry, one dot product, three terms — nothing to rearrange and
nothing to derive.

The only thing this question can catch you on is which row and which column, so read
the subscript before you start multiplying.
''',
                    "prompt": "What is the $(2,1)$ entry of $AB$?",
                    "note": "That is row $2$, column $1$. Give a plain number.",
                    "figure": r'''
$$A = \begin{bmatrix} 2 & -1 & 4 \\ 0 & 3 & 5 \end{bmatrix} \qquad B = \begin{bmatrix} 1 & 2 \\ -2 & 0 \\ 3 & 1 \end{bmatrix}$$
$A$ is $2\times3$, $B$ is $3\times2$, and the inner dimensions agree, so $AB$ is $2\times2$.
''',
                    "given": [
                        {"label": "Shape of $A$", "value": "$2\\times3$"},
                        {"label": "Shape of $B$", "value": "$3\\times2$"},
                        {"label": "Entry wanted", "value": "row $2$, column $1$"},
                    ],
                    "aside": "Row $2$ of $A$ reads across the bottom. Column $1$ of $B$ reads down the left.",
                    "answer": 9.0,
                    "tol": 0.001,
                    "unit": "",
                    "hint": "Row $2$ of $A$ is $(0, 3, 5)$ and column $1$ of $B$ is $(1, -2, 3)$. Multiply them term by term and add.",
                    "wrong": "If you got $16$, you used row $1$ of $A$ instead of row $2$ \u2014 that is the $(1,1)$ entry. If you got $5$, you took column $2$ of $B$ instead of column $1$.",
                    "why": r'''
$(AB)_{21} = 0\cdot 1 + 3\cdot(-2) + 5\cdot 3 = 0 - 6 + 15 = 9$.
The whole product is $AB = \begin{bmatrix} 16 & 8 \\ 9 & 5 \end{bmatrix}$, and you needed one quarter of that work.
Notice that the $3$ shared by the two shapes is the *number of terms in the sum*: it is why the dot product had three products in it and why it appears nowhere in the answer's shape.
''',
                },
                {
                    "title": "The trace of a product, without forming the product",
                    "minutes": 7,
                    "brief": r'''
The trace of a square matrix is the sum of its diagonal entries,
$\operatorname{tr}(M) = \sum_i m_{ii}$.

Applying the rule rather than just evaluating it: the trace only asks for the diagonal,
so of the four dot products in a $2\times2$ product you need exactly two. Doing the
other two is not wrong, it is just work you were not asked for.
''',
                    "prompt": "What is $\\operatorname{tr}(AB)$?",
                    "note": "A plain number. Watch the signs.",
                    "figure": r'''
$$A = \begin{bmatrix} 2 & 0 & -1 \\ 1 & 3 & 4 \end{bmatrix} \qquad B = \begin{bmatrix} 1 & 2 \\ 0 & -3 \\ 5 & 1 \end{bmatrix}$$
$AB$ is $2\times2$, so it has a diagonal and therefore a trace.
''',
                    "given": [
                        {"label": "Shape of $AB$", "value": "$2\\times2$"},
                        {"label": "Wanted", "value": "$(AB)_{11} + (AB)_{22}$"},
                    ],
                    "aside": "Two dot products, not four. Row $1$ against column $1$, and row $2$ against column $2$.",
                    "answer": -6.0,
                    "tol": 0.001,
                    "unit": "",
                    "hint": "$(AB)_{11}$ is row $1$ of $A$, which is $(2, 0, -1)$, against column $1$ of $B$, which is $(1, 0, 5)$. Then do the same with the second row and the second column.",
                    "wrong": "If you got $6$, a sign slipped: the term $(-1)\\cdot 5$ in the first diagonal entry is negative, and so is $3\\cdot(-3)$ in the second. If you got $-3$, you stopped after one of the two entries.",
                    "why": r'''
$(AB)_{11} = 2\cdot 1 + 0\cdot 0 + (-1)\cdot 5 = 2 + 0 - 5 = -3$ and $(AB)_{22} = 1\cdot 2 + 3\cdot(-3) + 4\cdot 1 = 2 - 9 + 4 = -3$, so the trace is $-6$.
Now do something that looks impossible. $BA$ is $3\times3$, a completely different matrix of a completely different size, and its diagonal is $(BA)_{11} = 1\cdot2 + 2\cdot1 = 4$, $(BA)_{22} = 0\cdot0 + (-3)\cdot3 = -9$ and $(BA)_{33} = 5\cdot(-1) + 1\cdot4 = -1$.
Those add to $-6$ as well. That is not a coincidence: $\operatorname{tr}(AB) = \sum_i \sum_k a_{ik}b_{ki} = \operatorname{tr}(BA)$, because the double sum is symmetric under swapping the two letters even though the products are not.
It is the one number about $AB$ that survives reversing the order, and it is the reason the trace turns up wherever a quantity has to be independent of the basis you chose.
''',
                },
                {
                    "title": "The only companion a shear will accept",
                    "minutes": 9,
                    "brief": r'''
Now the value has to be derived before it can be computed.

You are given a shear $A$ and half of a second matrix $B$. The bottom row of $B$ is
unknown. Fill it in so that the two matrices commute, then compute with the result.

The derivation on the commutator of a shear is the tool; this is where it earns its
keep.
''',
                    "prompt": "Choose $c$ and $d$ so that $AB = BA$, then report the $(1,2)$ entry of $AB$.",
                    "note": "One number: the top-right entry of the product, once $B$ has been completed.",
                    "figure": r'''
$$A = \begin{bmatrix} 1 & 2 \\ 0 & 1 \end{bmatrix} \qquad B = \begin{bmatrix} 4 & 7 \\ c & d \end{bmatrix}$$
$A$ is a shear: it sends $(x, y)$ to $(x + 2y,\; y)$. The entries $c$ and $d$ are yours to choose, and exactly one choice makes the two matrices commute.
''',
                    "given": [
                        {"label": "Top row of $B$", "value": "$4$ and $7$, fixed"},
                        {"label": "Bottom row of $B$", "value": "$c$ and $d$, to be found"},
                        {"label": "Condition", "value": "$AB = BA$"},
                    ],
                    "aside": "Write $A = I + 2N$ with $N$ the shear from the derivation. $I$ commutes with everything, so only the $N$ part can cause trouble.",
                    "answer": 15.0,
                    "tol": 0.001,
                    "unit": "",
                    "hint": "$AB - BA = 2(NB - BN)$, and the derivation gives that commutator as $\\begin{bmatrix} c & d - 4 \\\\ 0 & -c \\end{bmatrix}$. Setting it to zero pins both unknowns.",
                    "wrong": "If you got $21$, you set $c = 0$ but left $d$ at $7$; check $AB$ against $BA$ for that $B$ and they differ. If you got $7$, that is the $(1,2)$ entry of $B$ rather than of $AB$.",
                    "why": r'''
Write $A = I + 2N$. Then $AB - BA = 2(NB - BN)$, which the derivation evaluated as $\begin{bmatrix} c & d - a \\ 0 & -c \end{bmatrix}$ with $a = 4$ here.
That vanishes only when $c = 0$ and $d = 4$, so $B = \begin{bmatrix} 4 & 7 \\ 0 & 4 \end{bmatrix}$, which is $4I + 7N$ \u2014 built from the same two pieces as $A$.
Then $(AB)_{12} = 1\cdot 7 + 2\cdot 4 = 15$, and the whole product is $\begin{bmatrix} 4 & 15 \\ 0 & 4 \end{bmatrix}$.
Check the other order: $(BA)_{12} = 4\cdot 2 + 7\cdot 1 = 15$ as well, and the rest of $BA$ matches too. Two matrices that commute, arrived at by construction rather than by luck.
''',
                },
                {
                    "title": "Where to put the brackets",
                    "minutes": 8,
                    "brief": r'''
Associativity says the two bracketings of $ABC$ give the same matrix. It says nothing
whatever about what they cost.

Multiplying an $m\times k$ by a $k\times n$ takes $mnk$ scalar multiplications: there
are $mn$ entries to fill and each is a sum of $k$ products. Cost both routes through
the chain below and report the cheaper total.
''',
                    "prompt": "How many scalar multiplications does the cheaper bracketing take in total?",
                    "note": "Count both products along the route and add them. A whole number.",
                    "figure": r'''
$$A:\; 3\times 50 \qquad B:\; 50\times 2 \qquad C:\; 2\times 40$$
The chain $ABC$ is legal: $50$ meets $50$, and $2$ meets $2$. The answer is a $3\times40$ matrix either way. The two routes are $(AB)C$ and $A(BC)$.
''',
                    "given": [
                        {"label": "Cost of $(m\\times k)(k\\times n)$", "value": "$mnk$ multiplications"},
                        {"label": "Route 1", "value": "$(AB)C$"},
                        {"label": "Route 2", "value": "$A(BC)$"},
                    ],
                    "aside": "The intermediate matrix is what differs: one route builds a $3\\times2$, the other builds a $50\\times40$.",
                    "answer": 540.0,
                    "tol": 0.5,
                    "unit": "multiplications",
                    "hint": "Cost of a single product is (rows of the left factor) $\\times$ (columns of the right factor) $\\times$ (the inner dimension they share). Do that twice for each route.",
                    "wrong": "If you got $10000$ you costed $A(BC)$, which is the expensive route. If you got $300$ or $240$ you costed only one of the two products on the cheap route and forgot to add the other.",
                    "why": r'''
Route 1: $AB$ costs $3\cdot50\cdot2 = 300$ and leaves a $3\times2$; then $(AB)C$ costs $3\cdot2\cdot40 = 240$. Total $540$.
Route 2: $BC$ costs $50\cdot2\cdot40 = 4000$ and leaves a $50\times40$; then $A(BC)$ costs $3\cdot50\cdot40 = 6000$. Total $10000$.
Eighteen and a half times the work for a bit-for-bit identical answer. The expensive route inflates a thin $50\times2$ and a thin $2\times40$ into a fat $50\times40$ before the small matrix $A$ is ever touched, and every one of those $2000$ entries then has to be multiplied through.
The general problem \u2014 bracket a chain of $n$ matrices as cheaply as possible \u2014 is the textbook dynamic-programming exercise. The point here is only that associativity is what makes the question askable: if the two routes gave different answers there would be nothing to choose between.
''',
                },
            ],
            "blanks": {
                "title": "A product and its transpose, line by line",
                "minutes": 9,
                "caption": "a 2x3 against a 3x2, then turned on its side",
                "lang": "text",
                "brief": r'''
Every entry below is one dot product: a row of $A$ read across, a column of $B$ read
down, multiplied term by term and added. Four entries, three terms each.

Then the product gets transposed, and the last line asks you to name the same matrix a
second way — which is where the reversal rule
$(AB)^{\mathsf{T}} = B^{\mathsf{T}}A^{\mathsf{T}}$ has to be got right rather than
guessed.
''',
                "listing": """A is 2x3 and B is 3x2

         [  2  -1   0 ]              [  1   4 ]
    A =  [  3   5  -2 ]         B =  [ -2   0 ]
                                     [  6   1 ]

  the inner dimensions are 3 and 3, they agree, so AB has shape ___

  row 1 of A, column 1 of B:
       (AB) row 1 col 1  =  2*1  +  (-1)*(-2)  +  0*6
                         =  ___

  row 1 of A, column 2 of B:
       (AB) row 1 col 2  =  2*4  +  (-1)*0     +  0*1
                         =  8

  row 2 of A, column 1 of B:
       (AB) row 2 col 1  =  3*1  +  5*(-2)     +  (-2)*6
                         =  ___

  row 2 of A, column 2 of B:
       (AB) row 2 col 2  =  3*4  +  5*0        +  (-2)*1
                         =  10

                               [   4    8 ]
                        AB  =  [ -19   10 ]

  transpose it: row i becomes column i

                               [   4   ___ ]
                     (AB)^T =  [   8    10 ]

  and the same matrix, named without ever forming AB first:

                     (AB)^T =  ___
""",
                "blanks": [
                    {
                        "prompt": "The inner dimensions cancel and the outer ones survive. What shape is AB?",
                        "hole": "?",
                        "opts": ["2x2", "3x3", "2x3", "3x2"],
                        "a": 0,
                        "why": "$(2\\times3)(3\\times2) \\to 2\\times2$. The shared $3$ is the number of terms in each "
                               "dot product, so it controls how much work an entry takes and then disappears from "
                               "the shape entirely. The shape $3\\times3$ is what $BA$ comes out as \u2014 a real "
                               "matrix, and a different one.",
                    },
                    {
                        "prompt": "2*1 + (-1)*(-2) + 0*6. What is the total?",
                        "hole": "?",
                        "opts": ["0", "4", "2", "-2"],
                        "a": 1,
                        "why": "$2 + 2 + 0 = 4$. The middle term is a product of two negatives and so is $+2$; "
                               "reading it as $-2$ gives $0$, which is the single most common slip in a hand-computed "
                               "product. The final term vanishes because the entry of $A$ is zero, not because the "
                               "entry of $B$ is small.",
                    },
                    {
                        "prompt": "3*1 + 5*(-2) + (-2)*6. What is the total?",
                        "hole": "?",
                        "opts": ["25", "-1", "-19", "19"],
                        "a": 2,
                        "why": "$3 - 10 - 12 = -19$. Adding the magnitudes instead of the signed values gives $25$; "
                               "dropping the last term gives $-7$. It is worth writing the three products out before "
                               "adding anything, precisely because two of them are negative.",
                    },
                    {
                        "prompt": "Transposing swaps rows and columns. What sits in row 1, column 2 of (AB)^T?",
                        "hole": "?",
                        "opts": ["8", "10", "-19", "4"],
                        "a": 2,
                        "why": "Row $1$, column $2$ of $(AB)^{\\mathsf{T}}$ is row $2$, column $1$ of $AB$, which is "
                               "$-19$. Transposing is a relabelling and moves no arithmetic: every number in $AB$ "
                               "appears once in $(AB)^{\\mathsf{T}}$, in the mirrored position. The value $8$ is the "
                               "one that was already there before the swap.",
                    },
                    {
                        "prompt": "The reversal rule. Which product equals (AB)^T?",
                        "hole": "?",
                        "opts": ["B^T A^T", "A^T B^T", "A B", "B A"],
                        "a": 0,
                        "why": "$(AB)^{\\mathsf{T}} = B^{\\mathsf{T}}A^{\\mathsf{T}}$. The shapes settle it on their "
                               "own: $B^{\\mathsf{T}}$ is $2\\times3$ and $A^{\\mathsf{T}}$ is $3\\times2$, so the "
                               "product is $2\\times2$ and fits. Keeping the original order gives "
                               "$A^{\\mathsf{T}}B^{\\mathsf{T}}$, which is $(3\\times2)(2\\times3)$ \u2014 defined, but "
                               "$3\\times3$, so it is not even the right size to be the answer.",
                    },
                ],
            },
            "quiz": {
                "title": "Shapes, order and the rules that survive",
                "minutes": 9,
                "questions": [
                    {
                        "q": "$A$ is $4\\times3$ and $B$ is $3\\times5$. What shape is $AB$?",
                        "opts": [
                            "$3\\times3$",
                            "$4\\times5$",
                            "$5\\times4$",
                            "$AB$ is not defined",
                        ],
                        "a": 1,
                        "why": r'''
The inner dimensions — the $3$ columns of $A$ and the $3$ rows of $B$ — have to agree,
and they do. That shared $3$ is the length of every dot product and then vanishes; the
outer numbers survive, giving $4\times5$. A result of $5\times4$ would be
$(AB)^{\mathsf{T}}$, which is a different matrix.
''',
                    },
                    {
                        "q": "$A$ is $2\\times3$ and $B$ is $3\\times2$. Which statement is true?",
                        "opts": [
                            "$AB$ is defined but $BA$ is not",
                            "$AB$ is $2\\times2$ and $BA$ is $3\\times3$",
                            "$AB$ and $BA$ are both $2\\times2$, and they are equal",
                            "Neither product is defined",
                        ],
                        "a": 1,
                        "why": r'''
Both products exist here, because the inner dimensions agree in both directions:
$(2\times3)(3\times2)$ gives $2\times2$, and $(3\times2)(2\times3)$ gives $3\times3$.
They cannot possibly be equal — they are not even the same size. This is the cleanest
demonstration that $AB$ and $BA$ are separate questions rather than two spellings of one.
''',
                    },
                    {
                        "q": "What is the $(i,j)$ entry of $AB$?",
                        "opts": [
                            "the product $a_{ij} b_{ij}$",
                            "column $i$ of $A$ against row $j$ of $B$",
                            "row $i$ of $A$ against column $j$ of $B$",
                            "row $j$ of $A$ against column $i$ of $B$",
                        ],
                        "a": 2,
                        "why": r'''
$(AB)_{ij} = \sum_k a_{ik}b_{kj}$: the first index stays with the row of the left
factor, the second with the column of the right factor, and $k$ runs along both at once.
Multiplying entrywise is a real operation — the Hadamard product — but it does not
compose linear maps, which is the only reason matrices are multiplied at all. Swapping
$i$ and $j$ computes an entry of $(AB)^{\mathsf{T}}$ instead.
''',
                    },
                    {
                        "q": "Which of these holds for **every** pair or triple of matrices whose shapes allow the products?",
                        "opts": [
                            "$AB = BA$",
                            "$(A+B)^2 = A^2 + 2AB + B^2$",
                            "$(AB)^{\\mathsf{T}} = A^{\\mathsf{T}} B^{\\mathsf{T}}$",
                            "$(AB)C = A(BC)$",
                        ],
                        "a": 3,
                        "why": r'''
Associativity is the one that never fails: both sides are the matrix of "do $C$, then
$B$, then $A$", and composing three functions has no bracket in it to move. Commuting
the factors fails in general; collecting $AB + BA$ into $2AB$ fails for exactly the same
reason, so the binomial expansion is $A^2 + AB + BA + B^2$; and transposing a product
reverses it, $(AB)^{\mathsf{T}} = B^{\mathsf{T}}A^{\mathsf{T}}$, which the shapes insist
on even before the algebra does.
''',
                    },
                    {
                        "q": "Two $2\\times2$ matrices, neither of them the zero matrix, multiply to give the zero matrix. Possible?",
                        "opts": [
                            r"Yes — $\begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}$ multiplied by itself is the zero matrix",
                            "No — if $AB = 0$ then $A = 0$ or $B = 0$, just as with numbers",
                            "Only if one of the two is the identity",
                            "Only if both of them are diagonal",
                        ],
                        "a": 0,
                        "why": r'''
Call it $N$. Then $(N^2)_{11} = 0\cdot0 + 1\cdot0 = 0$ and $(N^2)_{12} = 0\cdot1 + 1\cdot0 = 0$,
and the bottom row of $N$ was zero already, so $N^2 = 0$ while $N \neq 0$. Read as a map,
$N$ takes the $y$ component and puts it in the $x$ slot; do that twice and nothing is
left. Matrices have zero divisors and the real numbers do not, which is precisely why
you cannot divide both sides of a matrix equation by a common factor.
''',
                    },
                    {
                        "q": "$AB = AC$, and $A$ is not the zero matrix. Must $B = C$?",
                        "opts": [
                            "Yes — cancel $A$ from both sides",
                            "Only when $B$ and $C$ are square",
                            "No — cancelling needs $A$ to be invertible, not merely non-zero",
                            "No — cancelling needs $A$ to be symmetric",
                        ],
                        "a": 2,
                        "why": r'''
Take $A = \begin{bmatrix} 1 & 0 \\ 0 & 0 \end{bmatrix}$, which keeps the first row of
whatever it multiplies and throws the second away. Any two matrices that share a first
row therefore give the same product, so $AB = AC$ with $B \neq C$ is easy to arrange.
Being non-zero is not enough: you need to be able to undo $A$. In the real numbers the
only non-invertible number is zero, which is why the habit transfers so badly. Module 2
supplies the test.
''',
                    },
                    {
                        "q": "Why does `equals` take a tolerance instead of comparing entries with `==`?",
                        "opts": [
                            "because comparing floats exactly is slower than comparing them approximately",
                            "because each entry of a product is a chain of roundings, so two correct routes rarely land on the same value",
                            "because Python cannot compare two floats with `==`",
                            "because matrices of different shapes have to come out equal",
                        ],
                        "a": 1,
                        "why": r'''
Every entry of $AB$ is $k$ multiplications and $k-1$ additions, each rounded to the
nearest double, so two honest routes to the same matrix generally differ in the last
few bits — and $(AB)C$ against $A(BC)$ is exactly such a pair. Exact comparison is not
slow; it is asking a stricter question than the one you meant. Different shapes compare
*unequal*, and always should.
''',
                    },
                ],
            },
            "lab": {
                "title": "A Matrix type over lists of lists",
                "runtime": "python",
                "minutes": 40,
                "brief": r'''
Build a `Matrix` class storing rows as a list of lists of floats in
`self.rows`. Nothing else in the course is allowed to reach past that attribute.

## Construction

`Matrix(rows)` copies and converts to `float`. It raises `ValueError` for an
empty matrix, an empty row, rows of differing length, or a non-numeric entry
(booleans count as non-numeric here — `True` is not a number worth storing).

## The interface

- `shape` — a **property** giving `(number_of_rows, number_of_columns)`
- `Matrix.identity(n)` and `Matrix.zeros(rows, cols)` — **classmethods**;
  a non-positive dimension raises `ValueError`
- `m[i, j]` — entry access via a tuple index
- `a + b`, `a - b` — entrywise; mismatched shapes raise `ValueError`
- `a * b` — matrix product when `b` is a `Matrix`, scaling when it is a number;
  a shape mismatch raises `ValueError`
- `2 * a` — scaling from the left as well (`__rmul__`)
- `a.transpose()` — a new `Matrix`, rows and columns exchanged
- `a.equals(b, tol=1e-9)` — same shape and every entry within `tol`
- `a == b` — `equals` with the default tolerance; `False` against a non-Matrix
- `str(a)` — one line per row, entries formatted with `:g` and joined by two
  spaces, so `str(Matrix.identity(2))` is `"1  0\n0  1"`

```text
Matrix([[1, 2], [3, 4]]) * Matrix([[5, 6], [7, 8]])  ->  [[19, 22], [43, 50]]
Matrix([[1, 2, 3], [4, 5, 6]]).transpose().shape     ->  (3, 2)
```
''',
                "files": [{"name": "main.py", "content": r'''
class Matrix:
    """A dense matrix stored as a list of lists of floats."""

    def __init__(self, rows):
        # validate, convert to float, store in self.rows
        pass

    @property
    def shape(self):
        """(rows, columns)."""
        # your code here

    @classmethod
    def identity(cls, n):
        """The n-by-n identity."""
        # your code here

    @classmethod
    def zeros(cls, rows, cols):
        """An all-zero matrix of the given shape."""
        # your code here

    def __getitem__(self, index):
        """Entry access with a (row, column) tuple."""
        # your code here

    def __add__(self, other):
        # your code here
        pass

    def __sub__(self, other):
        # your code here
        pass

    def __mul__(self, other):
        """Matrix product with a Matrix, scaling with a number."""
        # your code here

    def __rmul__(self, scalar):
        # your code here
        pass

    def transpose(self):
        """A new Matrix with rows and columns exchanged."""
        # your code here

    def equals(self, other, tol=1e-9):
        """Same shape and every entry within tol."""
        # your code here

    def __eq__(self, other):
        # your code here
        pass

    def __repr__(self):
        return f"Matrix({self.rows!r})"

    def __str__(self):
        # your code here
        pass


a = Matrix([[1, 2], [3, 4]])
b = Matrix([[5, 6], [7, 8]])
print(a * b)
print(Matrix.identity(3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
class Matrix:
    """A dense matrix stored as a list of lists of floats."""

    def __init__(self, rows):
        if not isinstance(rows, (list, tuple)) or len(rows) == 0:
            raise ValueError("a matrix needs at least one row")
        data = []
        width = None
        for row in rows:
            if not isinstance(row, (list, tuple)) or len(row) == 0:
                raise ValueError("every row must be a non-empty sequence")
            if width is None:
                width = len(row)
            elif len(row) != width:
                raise ValueError("all rows must have the same length")
            converted = []
            for value in row:
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    raise ValueError("entries must be numbers")
                converted.append(float(value))
            data.append(converted)
        self.rows = data

    @property
    def shape(self):
        """(rows, columns)."""
        return (len(self.rows), len(self.rows[0]))

    @classmethod
    def identity(cls, n):
        """The n-by-n identity."""
        if n < 1:
            raise ValueError("n must be positive")
        return cls([[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)])

    @classmethod
    def zeros(cls, rows, cols):
        """An all-zero matrix of the given shape."""
        if rows < 1 or cols < 1:
            raise ValueError("both dimensions must be positive")
        return cls([[0.0] * cols for _ in range(rows)])

    def __getitem__(self, index):
        """Entry access with a (row, column) tuple."""
        i, j = index
        return self.rows[i][j]

    def __add__(self, other):
        if not isinstance(other, Matrix) or other.shape != self.shape:
            raise ValueError("addition needs two matrices of the same shape")
        return Matrix([[x + y for x, y in zip(rx, ry)]
                       for rx, ry in zip(self.rows, other.rows)])

    def __sub__(self, other):
        if not isinstance(other, Matrix) or other.shape != self.shape:
            raise ValueError("subtraction needs two matrices of the same shape")
        return Matrix([[x - y for x, y in zip(rx, ry)]
                       for rx, ry in zip(self.rows, other.rows)])

    def __mul__(self, other):
        """Matrix product with a Matrix, scaling with a number."""
        if isinstance(other, Matrix):
            rows, inner = self.shape
            other_rows, cols = other.shape
            if inner != other_rows:
                raise ValueError("inner dimensions must agree")
            product = []
            for i in range(rows):
                row = []
                for j in range(cols):
                    row.append(sum(self.rows[i][k] * other.rows[k][j]
                                   for k in range(inner)))
                product.append(row)
            return Matrix(product)
        if isinstance(other, bool) or not isinstance(other, (int, float)):
            raise ValueError("can only multiply by a Matrix or a number")
        return Matrix([[x * float(other) for x in row] for row in self.rows])

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def transpose(self):
        """A new Matrix with rows and columns exchanged."""
        rows, cols = self.shape
        return Matrix([[self.rows[i][j] for i in range(rows)] for j in range(cols)])

    def equals(self, other, tol=1e-9):
        """Same shape and every entry within tol."""
        if not isinstance(other, Matrix) or other.shape != self.shape:
            return False
        for rx, ry in zip(self.rows, other.rows):
            for x, y in zip(rx, ry):
                if abs(x - y) > tol:
                    return False
        return True

    def __eq__(self, other):
        return self.equals(other)

    def __repr__(self):
        return f"Matrix({self.rows!r})"

    def __str__(self):
        return "\n".join("  ".join(f"{value:g}" for value in row)
                         for row in self.rows)


a = Matrix([[1, 2], [3, 4]])
b = Matrix([[5, 6], [7, 8]])
print(a * b)
print(Matrix.identity(3))
'''}],
                "hints": [
                    "Do the validation in one pass in `__init__`: track the width of the first row, compare every later row against it, and convert entries with `float(value)` as you go.",
                    "`shape` is decorated with `@property`, so it is read as `m.shape` with no brackets; `identity` and `zeros` are `@classmethod` and build with `cls(...)` so subclasses keep working.",
                    "`__mul__` branches on `isinstance(other, Matrix)`. The product entry is `sum(self.rows[i][k] * other.rows[k][j] for k in range(inner))` — one loop over the shared inner dimension.",
                    "`__rmul__` only ever sees a scalar on the left, so it can simply delegate: `return self.__mul__(scalar)`.",
                ],
                "tests": [
                    {"name": "Construction, shape and entry access", "code": r'''
_m = Matrix([[1, 2, 3], [4, 5, 6]])
assert _m.shape == (2, 3), f"shape gave {_m.shape!r}, expected (2, 3)"
assert _m[0, 0] == 1.0 and _m[1, 2] == 6.0, f"Entry access gave {_m[0, 0]!r} and {_m[1, 2]!r}"
assert isinstance(_m[0, 0], float), "Entries should be stored as floats"
_src = [[1, 2], [3, 4]]
_copy = Matrix(_src)
_src[0][0] = 99
assert _copy[0, 0] == 1.0, "Matrix must copy its input, not alias it"
'''},
                    {"name": "Malformed input is refused", "code": r'''
for _bad in [[], [[]], [[1, 2], [3]], [[1, 2], []], "not a matrix", [[1, "a"]], [[1, None]]]:
    try:
        Matrix(_bad)
        assert False, f"Matrix({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "identity and zeros", "code": r'''
_i = Matrix.identity(3)
assert _i.shape == (3, 3), f"identity(3).shape is {_i.shape!r}"
for _r in range(3):
    for _c in range(3):
        _want = 1.0 if _r == _c else 0.0
        assert _i[_r, _c] == _want, f"identity(3)[{_r}, {_c}] is {_i[_r, _c]!r}, expected {_want}"
_z = Matrix.zeros(2, 4)
assert _z.shape == (2, 4), f"zeros(2, 4).shape is {_z.shape!r}"
assert all(_z[_r, _c] == 0.0 for _r in range(2) for _c in range(4)), "zeros must be all zero"
for _args in [(0,), (-2,)]:
    try:
        Matrix.identity(*_args)
        assert False, f"Matrix.identity{_args!r} should raise ValueError"
    except ValueError:
        pass
try:
    Matrix.zeros(2, 0)
    assert False, "Matrix.zeros(2, 0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Addition and subtraction", "code": r'''
_a = Matrix([[1, 2], [3, 4]])
_b = Matrix([[5, 6], [7, 8]])
assert (_a + _b).equals(Matrix([[6, 8], [10, 12]])), f"a + b gave {(_a + _b).rows!r}"
assert (_a - _b).equals(Matrix([[-4, -4], [-4, -4]])), f"a - b gave {(_a - _b).rows!r}"
assert _a.equals(Matrix([[1, 2], [3, 4]])), "Addition must not mutate its operands"
for _op in ("+", "-"):
    try:
        _a + Matrix([[1, 2, 3], [4, 5, 6]]) if _op == "+" else _a - Matrix([[1, 2, 3], [4, 5, 6]])
        assert False, f"Mismatched shapes under {_op} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Matrix and scalar multiplication", "code": r'''
_a = Matrix([[1, 2], [3, 4]])
_b = Matrix([[5, 6], [7, 8]])
assert (_a * _b).equals(Matrix([[19, 22], [43, 50]])), f"a * b gave {(_a * _b).rows!r}"
assert (_b * _a).equals(Matrix([[23, 34], [31, 46]])), \
    f"b * a gave {(_b * _a).rows!r}; the product is not commutative"
_c = Matrix([[1, 2, 3], [4, 5, 6]])
_d = Matrix([[7, 8], [9, 10], [11, 12]])
_p = _c * _d
assert _p.shape == (2, 2), f"(2x3)(3x2) should be 2x2, got {_p.shape!r}"
assert _p.equals(Matrix([[58, 64], [139, 154]])), f"Product gave {_p.rows!r}"
assert (_a * 2).equals(Matrix([[2, 4], [6, 8]])), f"a * 2 gave {(_a * 2).rows!r}"
assert (2 * _a).equals(Matrix([[2, 4], [6, 8]])), "2 * a needs __rmul__"
try:
    _c * _a
    assert False, "(2x3) * (2x2) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Identity acts as the unit", "code": r'''
_c = Matrix([[1, 2, 3], [4, 5, 6]])
assert (_c * Matrix.identity(3)).equals(_c), "A * I should be A"
assert (Matrix.identity(2) * _c).equals(_c), "I * A should be A"
_a = Matrix([[1, 2], [3, 4]])
_b = Matrix([[5, 6], [7, 8]])
_e = Matrix([[2, 0], [1, 3]])
assert ((_a * _b) * _e).equals(_a * (_b * _e)), "Matrix multiplication must be associative"
'''},
                    {"name": "Transpose and its product rule", "code": r'''
_c = Matrix([[1, 2, 3], [4, 5, 6]])
_t = _c.transpose()
assert _t.shape == (3, 2), f"transpose().shape is {_t.shape!r}, expected (3, 2)"
assert _t.equals(Matrix([[1, 4], [2, 5], [3, 6]])), f"transpose gave {_t.rows!r}"
assert _t.transpose().equals(_c), "Transposing twice returns the original"
_d = Matrix([[7, 8], [9, 10], [11, 12]])
assert (_c * _d).transpose().equals(_d.transpose() * _c.transpose()), \
    "(AB)^T should equal B^T A^T"
'''},
                    {"name": "Equality with a tolerance, and str", "code": r'''
_a = Matrix([[1.0, 2.0]])
_b = Matrix([[1.0 + 1e-12, 2.0]])
assert _a.equals(_b), "Entries within 1e-9 should compare equal"
assert not _a.equals(_b, tol=1e-15), "A tighter tolerance should reject them"
assert _a == _b, "== should use the default tolerance"
assert not (_a == Matrix([[1.0, 2.0, 3.0]])), "Different shapes are never equal"
assert not (_a == "not a matrix"), "Comparing against a non-Matrix must return False, not raise"
_s = str(Matrix.identity(2))
assert _s == "1  0\n0  1", f"str(identity(2)) gave {_s!r}, expected '1  0\\n0  1'"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Gaussian elimination, rank and determinant",
            "summary": "One algorithm that solves systems, measures rank and computes determinants.",
            "concepts": [
                "The three elementary row operations preserve the solution set",
                "Row echelon form: pivots move strictly right as you move down",
                "Partial pivoting picks the largest available pivot and bounds the growth of round-off",
                "Without pivoting a tiny pivot destroys accuracy even when the matrix is far from singular",
                "Rank is the number of pivots — equivalently the dimension of the column space",
                "The determinant is the product of the pivots, negated once per row interchange",
                "A square system is solvable for every right-hand side exactly when it has full rank",
            ],
            "read": [
                {
                    "title": "What elimination is allowed to do",
                    "minutes": 15,
                    "body": r'''
Three equations in three unknowns:

$$\begin{matrix} 2x &+& y &-& z &=& 8 \\ -3x &-& y &+& 2z &=& -11 \\ -2x &+& y &+& 2z &=& -3 \end{matrix}$$

The method taught at school is substitution: solve the first equation for $x$, push
that expression into the other two, repeat. It works. It also degrades fast — every
substitution copies a whole expression into two places, and by the fourth unknown you
are managing a page of algebra whose only structure is the order you happened to write
it in. At $n = 20$ it is unusable, and $n = 20$ is a small system.

What is wanted instead is a procedure with no decisions in it beyond bookkeeping: a
fixed sequence of moves that turns any system into one you can read the answer off.
The design problem is entirely in the word *allowed*. Any move at all turns the system
into a different system. The question is which moves turn it into a different system
with **the same solution set**.

## Three moves, and why they are safe

Write the system as a list of equations and allow exactly three operations on that
list.

1. **Swap** two equations.
2. **Scale** an equation by a non-zero constant $c$.
3. **Add** a multiple of one equation to a different equation.

Each has to be justified, and the justification is the same in all three cases: the
operation is *reversible*, and reversibility is what forces the solution sets to match.

Take the third and hardest one. Equations $E_i$ and $E_j$ are replaced by $E_i$ and
$E_j + cE_i$. Suppose $v$ solves the old system. Then $E_i(v)$ holds and $E_j(v)$
holds, so certainly $E_j(v) + cE_i(v)$ holds — that is just adding two true numerical
statements. So $v$ solves the new system, and every old solution survives.

The other direction is the one people skip, and it is the one that actually matters.
Suppose $v$ solves the *new* system, so $E_i(v)$ holds and $(E_j + cE_i)(v)$ holds.
Subtract $c$ times the first from the second: $E_j(v)$ holds. So $v$ solves the old
system too. No solutions were created.

Both inclusions hold, so the sets are equal. Notice exactly what made the argument
work in the second direction: the inverse move — subtract $c$ times $E_i$ — is itself
one of the three legal operations. That is the whole content of the theorem. An
irreversible move can only lose or invent solutions, and that is precisely why
operation 2 excludes $c = 0$: scaling an equation to $0 = 0$ throws its information
away and cannot be undone, and the resulting system generally has more solutions than
the one you started with.

## Where you are trying to get to

The target shape is **row echelon form**. Strip the unknowns off and write the system
as a matrix of coefficients with the right-hand side carried alongside; the operations
above become operations on rows. A matrix is in row echelon form when

- every all-zero row sits below every non-zero row, and
- in each non-zero row the first non-zero entry — its **pivot** — is strictly to the
  right of the pivot in the row above.

The staircase that produces is what makes back-substitution possible: the last pivot
row involves one unknown beyond the pivot column at most, so you can solve it, and
then each row above adds exactly one new unknown.

The algorithm to get there is short. Look down the current column from the current
pivot row. If every entry is zero, that column carries no pivot — move right without
moving down. Otherwise bring a non-zero entry to the pivot row, subtract the right
multiple of that row from every row beneath it to clear the column, and move down and
right.

## Worked: the system above

$$\begin{bmatrix} 2 & 1 & -1 \\ -3 & -1 & 2 \\ -2 & 1 & 2 \end{bmatrix} \qquad b = \begin{bmatrix} 8 \\ -11 \\ -3 \end{bmatrix}$$

The first pivot is $2$. The multiplier for row $2$ is $m_{21} = -3/2$, so row $2$
becomes row $2$ minus $(-3/2)$ times row $1$ — that is, row $2$ *plus* $1.5$ times
row $1$:

$$(-3 + 3,\; -1 + 1.5,\; 2 - 1.5 \;|\; -11 + 12) = (0,\; 0.5,\; 0.5 \;|\; 1)$$

For row $3$, $m_{31} = -2/2 = -1$, so row $3$ plus row $1$:

$$(-2 + 2,\; 1 + 1,\; 2 - 1 \;|\; -3 + 8) = (0,\; 2,\; 1 \;|\; 5)$$

The second pivot is $0.5$, and $m_{32} = 2/0.5 = 4$. Row $3$ minus $4$ times row $2$:

$$(0,\; 2 - 2,\; 1 - 2 \;|\; 5 - 4) = (0,\; 0,\; -1 \;|\; 1)$$

Echelon form reached, with pivots $2$, $0.5$ and $-1$. Back-substitute from the
bottom. The last row says $-z = 1$, so $z = -1$. The second says
$0.5y + 0.5(-1) = 1$, so $0.5y = 1.5$ and $y = 3$. The first says
$2x + 3 - (-1) = 8$, so $2x = 4$ and $x = 2$.

Check it against the original third equation: $-2(2) + 3 + 2(-1) = -4 + 3 - 2 = -3$.
Correct. Three pivots in three columns, one solution.

## Worked: the case that is not a unique solution

Here is the situation people mishandle, because the algorithm does not break — it
just stops producing pivots.

$$\begin{bmatrix} 1 & 1 & 2 \\ 2 & 2 & 5 \\ 3 & 3 & 8 \end{bmatrix} \qquad b = \begin{bmatrix} 3 \\ 8 \\ 13 \end{bmatrix}$$

Pivot $1$. Row $2$ minus $2$ times row $1$ gives $(0, 0, 1 \;|\; 2)$. Row $3$ minus
$3$ times row $1$ gives $(0, 0, 2 \;|\; 4)$.

Now look at column $2$ from row $2$ down: both entries are $0$. There is no pivot
there and nothing to do about it. Move right without moving down. Column $3$ has $1$
in row $2$; that is the second pivot. Row $3$ minus $2$ times row $2$ gives
$(0, 0, 0 \;|\; 0)$.

$$\begin{bmatrix} 1 & 1 & 2 \\ 0 & 0 & 1 \\ 0 & 0 & 0 \end{bmatrix} \qquad b = \begin{bmatrix} 3 \\ 2 \\ 0 \end{bmatrix}$$

Two pivots, so the rank is $2$. The last row reads $0 = 0$, which is true and carries
no information. Column $2$ has no pivot, so $y$ is a **free variable**: pick it, and
everything else follows. Row $2$ gives $z = 2$. Row $1$ gives $x + y + 4 = 3$, so
$x = -1 - y$. The solution set is a line, written with $y = t$ as the parameter:

$$(x,\; y,\; z) = (-1,\; 0,\; 2) + t\,(-1,\; 1,\; 0), \qquad t \in \mathbf{R}$$

Every point on it satisfies all three original equations, and nothing off it does.

Now change one number: make the third right-hand side $14$ instead of $13$. Every
elimination step is identical, because the coefficient matrix has not moved, but the
right-hand side now finishes as $(3, 2, 1)$ and the last row reads $0 = 1$. That is
false, so no $v$ satisfies it, and the system has no solutions at all.

That is the whole trichotomy, and it is decided by two counts. A zero row of
coefficients with a **non-zero** right-hand side means no solutions. Otherwise there
are solutions, and there is exactly one when every column carries a pivot, and
infinitely many when some column does not.

## The mistake

The tempting wrong move is to operate on **columns**. Rows are equations; columns are
unknowns. Adding twice column $1$ to column $3$ is a perfectly well-defined matrix
operation, it changes the rank not at all, and it destroys the answer — because the
new system's third unknown is no longer the old system's $z$. Column operations are
legitimate tools elsewhere; inside a solve they are not.

The second common slip is subtler. When a row has been cleared to all zeros, people
read that as "no solution" and stop. It is the *augmented* entry that decides:
$0 = 0$ is a redundant equation and costs you nothing but a pivot, while $0 = 1$ is
a contradiction. The two look identical if you only kept the coefficients.

## Where it stops

Everything above is exact arithmetic. The theorem "these three operations preserve
the solution set" is true over the rationals, over the reals, over any field — and it
is only approximately true in floating point, because the multiplier $m_{ij}$ and the
subtraction that uses it are both rounded. That is not a small caveat: it is possible
to run the algorithm above, make no mistakes, and get an answer with no correct digits
at all. Which of the available rows you promote to the pivot position turns out to
decide whether that happens, and that is the next reading.

One more limit worth naming now. Row echelon form is **not unique** — scale any row
by $2$ and it is still in echelon form. What *is* unique is the set of pivot columns,
and therefore the rank. Reduced row echelon form, where every pivot is $1$ and is the
only non-zero entry in its column, is unique, which is why theory quotes it and
software rarely computes it.
''',
                },
                {
                    "title": "The pivot you choose decides the answer you get",
                    "minutes": 14,
                    "body": r'''
Here is a system a child could solve:

$$\begin{matrix} 0.0001x &+& y &=& 1 \\ x &+& y &=& 2 \end{matrix}$$

Subtract: $0.9999x = -1 + 2$, so $x \approx 1.0001$ and $y \approx 0.9999$. The
coefficient matrix is nowhere near singular — its determinant is $0.0001 - 1 = -0.9999$,
about as far from zero as a matrix with entries of size $1$ ever gets. Nothing is
delicate here.

Run the elimination of the previous reading on it, in the obvious order, keeping three
significant figures at every step — a stand-in for what a real machine does with $16$.
The answer comes back $x = 0$. Not slightly wrong — wrong by the whole of itself, from
an algorithm that made no mistakes on a problem that was not hard.

## Three significant figures, honestly

The first pivot is $0.0001$. The multiplier is

$$m = \frac{1}{0.0001} = 10000$$

Row $2$ becomes row $2$ minus $10000$ times row $1$. The coefficient of $y$:

$$1 - 10000 \times 1 = -9999 \;\rightarrow\; -1.00 \times 10^{4}$$

Three significant figures cannot hold $-9999$, so it is stored as $-10000$. The
right-hand side:

$$2 - 10000 \times 1 = -9998 \;\rightarrow\; -1.00 \times 10^{4}$$

Also $-10000$. Now back-substitute:

$$y = \frac{-10000}{-10000} = 1.00 \qquad x = \frac{1 - 1.00}{0.0001} = \frac{0}{0.0001} = 0$$

The computed $y$ is right to three figures. The computed $x$ is $0$ and the true value
is $1.0001$.

## What actually went wrong

It is tempting to blame the small pivot for being small, as if dividing by $0.0001$
were the sin. It is not. Look at where the information went.

The two numbers $-9999$ and $-9998$ differ by $1$, and that difference is the entire
content of the original second equation. Everything else in those two numbers came
from row $1$, multiplied up by $10000$. Rounding to three figures kept the $10000$ and
threw away the $1$. The second equation was still in the system on paper and no longer
in the system numerically.

Then the back-substitution amplified what was left. The step $x = (1 - y)/0.0001$
multiplies the error in $y$ by $10000$. An error of $10^{-4}$ in $y$ — which is all
three-figure rounding permits — becomes an error of $1$ in $x$, and $1$ is the size
of the answer.

So the mechanism is: a multiplier much larger than $1$ inflates row $1$ until it
swamps row $2$, the rounding then discards row $2$'s own data, and the division by
the tiny pivot magnifies whatever error survives. Every stage of that chain is driven
by the same quantity, $|m| = |a_{21}/a_{11}|$.

## Partial pivoting

The fix follows directly. Before eliminating in a column, look down that column from
the pivot row to the bottom, find the entry of largest absolute value, and swap its
row into the pivot position. Then every multiplier is

$$|m_{ij}| = \left|\frac{a_{ij}}{a_{ii}}\right| \leq 1$$

because the denominator was chosen to be the largest of them. No row can be inflated
before it is subtracted, and no entry of the working matrix can grow by more than a
factor of $2$ in a single elimination step.

The cost is one scan per column and a row interchange — $O(n^2)$ comparisons against
the $O(n^3)$ arithmetic the algorithm was already doing. It is free, and it is why
every production solver does it unconditionally.

## Worked: the same system, rows swapped

Column $1$ holds $0.0001$ and $1$. The larger is $1$, so swap. One interchange, which
will matter for the determinant later:

$$\begin{matrix} x &+& y &=& 2 \\ 0.0001x &+& y &=& 1 \end{matrix}$$

Now $m = 0.0001/1 = 0.0001$. The coefficient of $y$ in the new second row:

$$1 - 0.0001 \times 1 = 0.9999 \;\rightarrow\; 1.00$$

The right-hand side:

$$1 - 0.0001 \times 2 = 0.9998 \;\rightarrow\; 1.00$$

So $y = 1.00/1.00 = 1.00$, and back-substitution gives $x = 2 - 1.00 = 1.00$.

Both are correct to three significant figures. The rounding still happened — $0.9999$
still got flattened to $1.00$ — but this time it discarded a part of the answer that
was below the precision anyone asked for, instead of discarding an entire equation.
And the back-substitution divides by $1$, not by $0.0001$, so nothing is amplified on
the way out.

## Worked: where partial pivoting still fails

Now the case people get wrong, which is believing the rule is a guarantee. Multiply
the first equation of the original system through by $10^5$. That is a legal
operation — it changes no solution — and it is what happens when someone measures a
quantity in microns instead of metres.

$$\begin{matrix} 10x &+& 100000y &=& 100000 \\ x &+& y &=& 2 \end{matrix}$$

Look down column $1$: the entries are $10$ and $1$. The largest is $10$, already in
the pivot row, so partial pivoting declines to swap and reports itself satisfied. The
multiplier is $m = 1/10 = 0.1$, comfortably below $1$. Everything looks healthy.

The coefficient of $y$ in the new second row:

$$1 - 0.1 \times 100000 = 1 - 10000 = -9999 \;\rightarrow\; -1.00 \times 10^{4}$$

and the right-hand side:

$$2 - 0.1 \times 100000 = -9998 \;\rightarrow\; -1.00 \times 10^{4}$$

Identical to the disaster above. $y = 1.00$, and $x = (100000 - 100000 \times 1.00)/10 = 0$
again.

The multiplier being small was never the point; what matters is whether $m$ times
row $1$ is large compared with row $2$, and scaling row $1$ up by $10^5$ arranged that
while keeping $|m| < 1$. **Partial pivoting is not invariant under row scaling.** The
usual repair is *scaled* partial pivoting: divide each candidate entry by the largest
absolute entry in its own row before comparing, so the comparison asks which row is
most dominated by this column rather than which entry is biggest. On the system above
that picks row $2$, and the answer comes out right.

## How you would notice

None of this is visible from the answer. A solver that returns $x = 0$ returns it with
the same composure as a solver that returns $x = 1.0001$, and there is no warning flag
in the arithmetic. So it is worth knowing the one cheap check that does catch it: put
the computed $\hat{x}$ back into the original system and look at what is left over.

$$r = b - A\hat{x}$$

For the unpivoted answer $\hat{x} = (0,\; 1)$:

$$A\hat{x} = (0.0001 \times 0 + 1,\; 0 + 1) = (1,\; 1) \qquad r = (1,\; 2) - (1,\; 1) = (0,\; 1)$$

The second component of the residual is $1$, the same size as the right-hand side
itself. The computed vector does not come close to satisfying the second equation, and
nothing subtle is needed to see it.

For the pivoted answer $\hat{x} = (1,\; 1)$:

$$A\hat{x} = (0.0001 + 1,\; 1 + 1) = (1.0001,\; 2) \qquad r = (-0.0001,\; 0)$$

Down at the level of the rounding, which is as good as three significant figures allow.

Computing a residual costs one matrix-vector product, $O(n^2)$, against the $O(n^3)$
of the solve — free, in other words, and worth doing every time. But be exact about
what it proves. A small residual says $\hat{x}$ solves a system *near* the one you
asked about; it does not say $\hat{x}$ is near the true $x$. When $A$ is
ill-conditioned those two statements come apart, and you can have a residual at
machine precision alongside a solution with no correct digits. Separating them is the
job of the condition number, at the end of this course.

## The mistake, and the honest limit

The mistake, stated plainly: pivoting only when the pivot is exactly zero. A great
deal of hand-written elimination code contains `if a[i][i] == 0: swap`. That code is
correct in exact arithmetic and nearly worthless in floating point, because the
dangerous case is not the zero pivot — which announces itself — but the pivot that is
merely small relative to what lies beneath it, which does not. The zero-pivot test
catches the one case you would have noticed anyway.

And the limit. Partial pivoting bounds the *multipliers* by $1$; it does not bound the
*entries*. Each elimination step can double an entry, so after $n-1$ steps the growth
factor can in principle reach $2^{n-1}$, and Wilkinson's matrix — $1$s on the diagonal,
$-1$s below it, $1$s in the last column — attains exactly that. For $n = 60$ that is a
factor of $10^{17}$ and every digit is gone. Such matrices essentially never arise from
real problems, and half a century of practice has found the strategy reliable, but
"reliable in practice" is what it is, not a theorem. Complete pivoting, which searches
the entire remaining submatrix, has a provable bound; it is rarely used because the
search costs $O(n^3)$ comparisons and buys nothing on the problems anyone actually
solves.
''',
                },
                {
                    "title": "The determinant is the product of the pivots",
                    "minutes": 15,
                    "body": r'''
You have a square system and you want one number that tells you whether it has a
unique solution. The definition most people meet first is cofactor expansion: pick a
row, multiply each entry by the determinant of the matrix left when its row and column
are deleted, alternate the signs, add.

That definition is correct and it is a disaster as a method. Expanding a determinant
of order $n$ this way costs about $n!$ multiplications. For $n = 20$ that is
$2.4 \times 10^{18}$ operations — decades on a fast machine — while the elimination of
the previous two readings does the whole solve in about $n^3/3 \approx 2700$. So the
question is not what the determinant *is*, but whether the work you were already doing
computes it.

It does, and almost for free: it is the product of the pivots, with a sign.

## What the determinant has to be

Rather than start from the $n!$-term formula, start from the three properties that
pin it down. For $n\times n$ matrices there is exactly one function $\det$ of the rows
with:

1. **Multilinearity.** $\det$ is linear in each row separately, the others held fixed.
   In particular, scaling one row by $c$ scales $\det$ by $c$.
2. **Alternating.** If two rows are equal, $\det = 0$.
3. **Normalisation.** $\det I = 1$.

Every fact below comes out of those three, and the uniqueness is what lets us compute
by any route we like.

## What each row operation does to it

**Swapping two rows negates the determinant.** Let $A$ have rows $r$ and $s$ in
positions $i$ and $j$. Build a matrix with $r + s$ in *both* positions; by property 2
its determinant is $0$. Expand by multilinearity in those two slots:

$$0 = \det(r, r) + \det(r, s) + \det(s, r) + \det(s, s)$$

The first and last terms are $0$ by property 2 again, so
$\det(r, s) = -\det(s, r)$. That is the swap rule, and it came from nothing but
linearity and the vanishing-on-repeats condition.

**Adding a multiple of one row to another leaves the determinant alone.** Replace
row $j$ by $r_j + c\,r_i$. Linearity in slot $j$ splits it:

$$\det(\ldots, r_j + c\,r_i, \ldots) = \det(\ldots, r_j, \ldots) + c\det(\ldots, r_i, \ldots)$$

The second determinant has $r_i$ in two different slots, so it is $0$. What is left is
the original. This is the operation elimination spends nearly all of its time on, and
it costs the determinant nothing.

**Scaling a row by $c$ scales the determinant by $c$** — that is property 1 stated
directly.

## Therefore: the product of the pivots

Run elimination on $A$. The only two operations used are row interchanges and
adding multiples of rows, so if $s$ interchanges were performed and $U$ is the
resulting echelon form,

$$\det A = (-1)^{s} \det U$$

$U$ is upper triangular. Its determinant is the product of its diagonal — expand
along the first column, which has one non-zero entry, then repeat — so

$$\det A = (-1)^{s}\,u_{11}u_{22}\cdots u_{nn}$$

The diagonal entries of $U$ are the pivots. The determinant costs one extra
multiplication per column on top of the elimination you were doing anyway: $n$
operations bolted onto $n^3/3$.

And it delivers the theorem you wanted, because the elimination stalls in a column
exactly when no pivot can be found there, which leaves a zero on the diagonal and
sends the product to zero. So $\det A \neq 0$, full rank $n$, and "a unique solution
for every $b$" are three statements of one fact.

## Worked: three by three, no interchange

$$A = \begin{bmatrix} 4 & 3 & 2 \\ 1 & 5 & 7 \\ 2 & 2 & 9 \end{bmatrix}$$

Column $1$ holds $4, 1, 2$; the largest is already on top, so no swap. Multipliers
$m_{21} = 1/4 = 0.25$ and $m_{31} = 2/4 = 0.5$:

$$r_2 \rightarrow (0,\; 5 - 0.25(3),\; 7 - 0.25(2)) = (0,\; 4.25,\; 6.5)$$
$$r_3 \rightarrow (0,\; 2 - 0.5(3),\; 9 - 0.5(2)) = (0,\; 0.5,\; 8)$$

Column $2$ below the pivot row holds $4.25$ and $0.5$; the larger is in place, so
again no swap. $m_{32} = 0.5/4.25 = 2/17$:

$$r_3 \rightarrow \left(0,\; 0,\; 8 - \tfrac{2}{17}(6.5)\right) = \left(0,\; 0,\; 8 - \tfrac{13}{17}\right) = \left(0,\; 0,\; \tfrac{123}{17}\right)$$

No interchanges, so the sign is $+1$ and

$$\det A = 4 \times 4.25 \times \frac{123}{17} = 17 \times \frac{123}{17} = 123$$

Cross-check by cofactors along the first row:
$4(45 - 14) - 3(9 - 14) + 2(2 - 10) = 124 + 15 - 16 = 123$. Agreed.

## Worked: the one people get wrong

$$B = \begin{bmatrix} 0 & 1 & 2 \\ 1 & 0 & 3 \\ 2 & 3 & 0 \end{bmatrix}$$

The $(1,1)$ entry is $0$, so an interchange is forced whatever your pivoting policy.
The largest entry of column $1$ is $2$ in row $3$; swap rows $1$ and $3$. **That is
one interchange — write it down now, because this is the step that gets lost.**

$$\begin{bmatrix} 2 & 3 & 0 \\ 1 & 0 & 3 \\ 0 & 1 & 2 \end{bmatrix}$$

$m_{21} = 1/2 = 0.5$, giving row $2$ as $(0,\; 0 - 1.5,\; 3 - 0) = (0,\; -1.5,\; 3)$.
$m_{31} = 0/2 = 0$, so row $3$ is untouched: $(0,\; 1,\; 2)$.

Column $2$ below the pivot row holds $-1.5$ and $1$. Compare *absolute values*:
$|-1.5| > |1|$, so no second interchange. This is the second place people slip — a
negative pivot is a perfectly good pivot, and $-1.5$ is bigger than $1$ in the sense
that matters. $m_{32} = 1/(-1.5) = -2/3$:

$$r_3 \rightarrow \left(0,\; 0,\; 2 - \left(-\tfrac{2}{3}\right)(3)\right) = (0,\; 0,\; 2 + 2) = (0,\; 0,\; 4)$$

The pivots are $2$, $-1.5$ and $4$, product $-12$. One interchange, so the sign is
$(-1)^1 = -1$:

$$\det B = -1 \times (-12) = 12$$

Cofactors again: $0(0 - 9) - 1(0 - 6) + 2(3 - 0) = 6 + 6 = 12$. Agreed. Drop the
interchange and you get $-12$ — the right magnitude with the wrong sign, which is the
single most common defect in hand-written determinant code and the reason the routine
must return the swap count rather than discard it.

## The mistake

The determinant is linear in each row *separately*. It is not linear in the matrix,
and $\det(A + B) = \det A + \det B$ is false. Take $A = B = I$ in two dimensions:
$\det(2I) = 4$ while $\det I + \det I = 2$. The temptation is real because property 1
has the word "linear" in it and the qualifier "in each row, the others held fixed" is
easy to drop. The correct multiplicative statement is
$\det(AB) = \det A \, \det B$, which addition never satisfies.

The companion slip appears when people normalise pivots to $1$ as they go, which is
tidy and makes back-substitution trivial. Every such normalisation *divides* the
determinant by the pivot, and if you do not multiply it back you will report $\det = 1$
for every non-singular matrix you meet.

## Where it stops

The determinant answers "is this matrix singular?" exactly, and answers "is this
matrix nearly singular?" not at all. Consider $0.1\,I$ of order $100$: a perfectly
behaved matrix that any solver handles to full precision. Its determinant is
$10^{-100}$, which underflows to zero in double precision. Meanwhile
$\det(2I_{100}) = 2^{100} \approx 10^{30}$, and that matrix is no better conditioned
than the other. The determinant scales like the $n$th power of the entries, so its
magnitude says far more about the units you measured in than about the health of the
system.

The quantity that does answer the real question is the condition number, and reaching
it needs singular values rather than pivots. That is where this course ends. Until
then, treat $\det A = 0$ as a fact and $\det A \approx 0$ as an opinion — the working
test for a near-singular matrix is a pivot that has collapsed relative to the entries
around it, which is exactly what a tolerance on the pivot magnitude is checking for.
''',
                },
            ],
            "derive": [
                {
                    "title": "Elimination on a general 2x2, and where the determinant comes from",
                    "minutes": 14,
                    "vars": ["a_11", "a_12", "a_21", "a_22", "b_1", "b_2", "x_1", "x_2", "m"],
                    "brief": r'''
Run the algorithm once with letters instead of numbers and it stops being an algorithm
and becomes a formula. The system is

$$\begin{matrix} a_{11}x_1 &+& a_{12}x_2 &=& b_1 \\ a_{21}x_1 &+& a_{22}x_2 &=& b_2 \end{matrix}$$

with $a_{11} \neq 0$, so no interchange is needed. Eliminate $x_1$ from the second
equation, back-substitute, and watch what shows up underneath both answers.

Nothing is assumed here except the three row operations. Write $m$ for the multiplier
if it helps, but give every answer in terms of the $a$'s and $b$'s.
''',
                    "steps": [
                        {
                            "prompt": "Row $2$ is replaced by row $2$ minus $m$ times row $1$. What must $m$ be, if the $x_1$ term is to vanish?",
                            "answer": r"\frac{a_{21}}{a_{11}}",
                            "hint": "The $x_1$ coefficient of the new row $2$ is $a_{21} - m\\,a_{11}$. Set that to zero and solve for $m$.",
                        },
                        {
                            "prompt": "With that $m$, what is the coefficient of $x_2$ in the new row $2$?",
                            "answer": r"a_{22} - \frac{a_{21} a_{12}}{a_{11}}",
                            "hint": "It is $a_{22} - m\\,a_{12}$. Substitute the $m$ you just found and leave it as it stands.",
                            "deconstruct": [
                                "The whole of row $2$ becomes $(a_{21} - m\\,a_{11},\\; a_{22} - m\\,a_{12} \\;|\\; b_2 - m\\,b_1)$.",
                                "Only the middle slot is wanted here, so it is $a_{22} - m\\,a_{12}$.",
                                "Now put $m = a_{21}/a_{11}$ into that. Do not clear the fraction yet — the next steps are easier if you leave it.",
                            ],
                        },
                        {
                            "prompt": "And the right-hand side of the new row $2$?",
                            "answer": r"b_2 - \frac{a_{21} b_1}{a_{11}}",
                            "hint": "The right-hand side rides along through the same operation: $b_2 - m\\,b_1$, with the same $m$.",
                        },
                        {
                            "prompt": "The new row $2$ now reads (coefficient) $x_2 =$ (right-hand side). Solve it for $x_2$, and clear the fractions so that no $a_{11}$ is left in a denominator inside another fraction.",
                            "answer": r"\frac{a_{11} b_2 - a_{21} b_1}{a_{11} a_{22} - a_{12} a_{21}}",
                            "hint": "Divide the last two answers. Then multiply the top and the bottom of the result by $a_{11}$.",
                            "deconstruct": [
                                "You have $x_2 = \\left(b_2 - \\frac{a_{21}b_1}{a_{11}}\\right) \\div \\left(a_{22} - \\frac{a_{21}a_{12}}{a_{11}}\\right)$.",
                                "Multiply the numerator and the denominator of that quotient by $a_{11}$. The numerator becomes $a_{11}b_2 - a_{21}b_1$.",
                                "The denominator becomes $a_{11}a_{22} - a_{21}a_{12}$, and every fraction inside a fraction has gone.",
                            ],
                        },
                        {
                            "prompt": "Back-substitute into row $1$, which still reads $a_{11}x_1 + a_{12}x_2 = b_1$, and solve for $x_1$. Give it over the same denominator.",
                            "answer": r"\frac{a_{22} b_1 - a_{12} b_2}{a_{11} a_{22} - a_{12} a_{21}}",
                            "hint": "$x_1 = (b_1 - a_{12}x_2)/a_{11}$. Substitute the $x_2$ you found, put the numerator over one denominator, and an $a_{11}$ will cancel.",
                            "deconstruct": [
                                "$x_1 = \\dfrac{b_1 - a_{12}x_2}{a_{11}}$, and $x_2 = \\dfrac{a_{11}b_2 - a_{21}b_1}{D}$ where $D = a_{11}a_{22} - a_{12}a_{21}$.",
                                "The numerator is $b_1 - \\dfrac{a_{12}(a_{11}b_2 - a_{21}b_1)}{D} = \\dfrac{b_1 D - a_{12}a_{11}b_2 + a_{12}a_{21}b_1}{D}$.",
                                "Expand $b_1 D = a_{11}a_{22}b_1 - a_{12}a_{21}b_1$. The two $a_{12}a_{21}b_1$ terms cancel, leaving $a_{11}(a_{22}b_1 - a_{12}b_2)$ over $D$ — then divide by $a_{11}$.",
                            ],
                        },
                        {
                            "prompt": "Both answers carry the same denominator. Write it down: it is the number that decides whether this system has a unique solution at all.",
                            "answer": r"a_{11} a_{22} - a_{12} a_{21}",
                            "hint": "Read it off the bottom of either of the last two answers.",
                        },
                    ],
                    "closing": r'''
The elimination produced, with no cleverness anywhere,

$$x_1 = \frac{a_{22}b_1 - a_{12}b_2}{a_{11}a_{22} - a_{12}a_{21}} \qquad x_2 = \frac{a_{11}b_2 - a_{21}b_1}{a_{11}a_{22} - a_{12}a_{21}}$$

and the shared denominator $a_{11}a_{22} - a_{12}a_{21}$ is the determinant of the
coefficient matrix. It was not defined into existence; it is what the algorithm leaves
at the bottom of the fraction, and that is the honest reason a zero determinant means
trouble. Nothing is being divided by zero metaphorically — the second pivot really is
zero and the division really does not happen.

Two things are worth pinning down before moving on.

First, the derivation assumed $a_{11} \neq 0$. If it is zero the first step is illegal,
and the fix is an interchange: swap the rows and run the same argument, which negates
the determinant on both the top and the bottom of every fraction and so changes no
answer. That is why the formula holds for every non-singular matrix even though its
derivation did not.

Second, the numerators are determinants too. $a_{22}b_1 - a_{12}b_2$ is the determinant
of the coefficient matrix with its first column replaced by $b$, and
$a_{11}b_2 - a_{21}b_1$ is the same with the second column replaced. That pattern is
Cramer's rule, and it generalises to every $n$. It is also, at $n$ determinants of
order $n$, one of the most expensive ways ever devised to solve a linear system, and
you should never compute with it — but seeing it fall out of two lines of elimination
is worth more than being handed it.
''',
                },
                {
                    "title": "How far a small pivot can throw the answer",
                    "minutes": 13,
                    "vars": ["epsilon", "x", "y"],
                    "brief": r'''
$$\begin{matrix} \epsilon x &+& y &=& 1 \\ x &+& y &=& 2 \end{matrix}$$

with $\epsilon$ small and positive. The determinant is $\epsilon - 1$, close to $-1$,
so the system is in no way delicate.

Everything below is **exact**: no rounding, no floating point. The point of doing it
exactly is to have the true answers in hand, so that when the rounding is put back in
the closing there is something to compare against. Take $\epsilon$ as the pivot in the
first column, which is what an unpivoted elimination does.
''',
                    "steps": [
                        {
                            "prompt": "Row $2$ becomes row $2$ minus $m$ times row $1$. What is $m$?",
                            "answer": r"\frac{1}{\epsilon}",
                            "hint": "The $x$ coefficients are $1$ on top of $\\epsilon$. The multiplier is the entry being cleared divided by the pivot.",
                        },
                        {
                            "prompt": "What is the coefficient of $y$ in the new row $2$?",
                            "answer": r"1 - \frac{1}{\epsilon}",
                            "hint": "It is $1 - m \\times 1$, and you have just written $m$.",
                        },
                        {
                            "prompt": "And its right-hand side?",
                            "answer": r"2 - \frac{1}{\epsilon}",
                            "hint": "$2 - m \\times 1$, the same $m$ again.",
                        },
                        {
                            "prompt": "Divide to get $y$ exactly, and tidy it so that neither the numerator nor the denominator contains a fraction.",
                            "answer": r"\frac{1 - 2\epsilon}{1 - \epsilon}",
                            "hint": "Multiply the top and the bottom of $(2 - 1/\\epsilon)\\,/\\,(1 - 1/\\epsilon)$ by $\\epsilon$, then tidy the signs.",
                            "deconstruct": [
                                "$y = \\dfrac{2 - 1/\\epsilon}{1 - 1/\\epsilon}$. Multiply top and bottom by $\\epsilon$.",
                                "That gives $y = \\dfrac{2\\epsilon - 1}{\\epsilon - 1}$.",
                                "Multiplying top and bottom by $-1$ leaves $\\dfrac{1 - 2\\epsilon}{1 - \\epsilon}$, which is the same number written without a leading minus.",
                            ],
                        },
                        {
                            "prompt": "Back-substitute into row $1$, which still reads $\\epsilon x + y = 1$, and give $x$ exactly.",
                            "answer": r"\frac{1}{1 - \epsilon}",
                            "hint": "$x = (1 - y)/\\epsilon$. Put $1 - y$ over the single denominator $1 - \\epsilon$ first; the numerator will turn out to have an $\\epsilon$ in it that cancels the one outside.",
                            "deconstruct": [
                                "$1 - y = 1 - \\dfrac{1 - 2\\epsilon}{1 - \\epsilon} = \\dfrac{(1 - \\epsilon) - (1 - 2\\epsilon)}{1 - \\epsilon}$.",
                                "The numerator simplifies to $\\epsilon$, so $1 - y = \\dfrac{\\epsilon}{1 - \\epsilon}$.",
                                "Dividing by $\\epsilon$ cancels it: $x = \\dfrac{1}{1 - \\epsilon}$, which tends to $1$ as $\\epsilon$ tends to $0$.",
                            ],
                        },
                        {
                            "prompt": "Start again with the rows interchanged, so the pivot is $1$ and the multiplier is $\\epsilon$. What is the coefficient of $y$ in the eliminated second row now?",
                            "answer": r"1 - \epsilon",
                            "hint": "The second row is now $\\epsilon x + y = 1$ and the pivot row is $x + y = 2$. The multiplier is $\\epsilon/1$, so the $y$ coefficient is $1 - \\epsilon \\times 1$.",
                        },
                    ],
                    "closing": r'''
The exact answers are

$$x = \frac{1}{1 - \epsilon} \qquad y = \frac{1 - 2\epsilon}{1 - \epsilon}$$

Both are close to $1$ for small $\epsilon$, both are perfectly well behaved, and the
route taken to reach them made no difference whatsoever — in exact arithmetic.

Now put the rounding back. Take $\epsilon = 10^{-4}$ and three significant figures.
Unpivoted, the two numbers you derived in the middle steps are
$1 - 10^{4} = -9999$ and $2 - 10^{4} = -9998$. Three figures cannot tell those apart:
both are stored as $-1.00\times10^{4}$. Their ratio is $1.00$, so the computed $y$ is
$1$ — fine — but then $x = (1 - 1)/10^{-4} = 0$, against a true value of $1.0001$. Every
digit is wrong.

Look at what the algebra says about why. The difference between those two quantities is
exactly $1$, and that $1$ is the *entire* contribution of the second equation; the rest
of both numbers is row $1$ scaled by $m = 1/\epsilon$. Rounding keeps the large common
part and deletes the difference. The second equation is still on the page and is no
longer in the computation.

With the interchange, the same two quantities are $1 - \epsilon = 0.9999$ and
$1 - 2\epsilon = 0.9998$, which round to $1.00$ and $1.00$. Rounding has again lost the
difference between them, and this time it does not matter, because that difference is
a $10^{-4}$ correction to an answer of size $1$ rather than the answer itself. The
back-substitution then divides by $1$ instead of by $\epsilon$, so nothing is amplified
on the way out, and $x = 2 - 1.00 = 1.00$ is right.

The general statement is the one to carry: what governs the damage is not the size of
the pivot but the size of the multiplier $m$. Partial pivoting exists to force
$|m| \leq 1$, and it does so by the cheapest possible means — comparing $n$ numbers and
swapping two rows.
''',
                },
                {
                    "title": "The 3x3 determinant, read off the pivots",
                    "minutes": 16,
                    "vars": ["a_11", "a_12", "a_13", "a_21", "a_22", "a_23",
                             "a_31", "a_32", "a_33", "m_2", "p_2", "p_3"],
                    "brief": r'''
$$A = \begin{bmatrix} a_{11} & a_{12} & a_{13} \\ a_{21} & a_{22} & a_{23} \\ a_{31} & a_{32} & a_{33} \end{bmatrix}$$

Assume $a_{11} \neq 0$ and that no interchange is needed anywhere, so the sign is $+1$
throughout. Elimination will be run to completion in letters. The claim to be tested
is that the product of the three pivots is the determinant — and since the six-term
formula for a $3\times3$ determinant is usually handed over with no explanation, this
is where it comes from.

Clear column $1$ first: row $2$ minus $(a_{21}/a_{11})$ times row $1$, and row $3$
minus $(a_{31}/a_{11})$ times row $1$. The first four steps ask for the four entries
that survive in the bottom-right $2\times2$ block.
''',
                    "steps": [
                        {
                            "prompt": "After the first sweep, what is the entry in row $2$, column $2$?",
                            "answer": r"a_{22} - \frac{a_{21} a_{12}}{a_{11}}",
                            "hint": "Row $2$ loses $(a_{21}/a_{11})$ times row $1$, so the column-$2$ entry loses $(a_{21}/a_{11})\\,a_{12}$.",
                        },
                        {
                            "prompt": "And row $2$, column $3$?",
                            "answer": r"a_{23} - \frac{a_{21} a_{13}}{a_{11}}",
                            "hint": "Same multiplier, next column along: subtract $(a_{21}/a_{11})\\,a_{13}$.",
                        },
                        {
                            "prompt": "Row $3$, column $2$?",
                            "answer": r"a_{32} - \frac{a_{31} a_{12}}{a_{11}}",
                            "hint": "Row $3$ uses the multiplier $a_{31}/a_{11}$, so every entry of row $1$ it subtracts is scaled by that instead.",
                        },
                        {
                            "prompt": "Row $3$, column $3$?",
                            "answer": r"a_{33} - \frac{a_{31} a_{13}}{a_{11}}",
                            "hint": "The multiplier $a_{31}/a_{11}$ again, against $a_{13}$ this time.",
                        },
                        {
                            "prompt": "Second sweep. The multiplier $m_2$ is the row-$3$ column-$2$ entry divided by the row-$2$ column-$2$ entry. Write $m_2$ with no fraction inside a fraction — multiply top and bottom by $a_{11}$.",
                            "answer": r"\frac{a_{11} a_{32} - a_{31} a_{12}}{a_{11} a_{22} - a_{21} a_{12}}",
                            "hint": "Divide the third answer by the first, then multiply the numerator and the denominator of the result by $a_{11}$.",
                            "deconstruct": [
                                "$m_2 = \\left(a_{32} - \\dfrac{a_{31}a_{12}}{a_{11}}\\right) \\div \\left(a_{22} - \\dfrac{a_{21}a_{12}}{a_{11}}\\right)$.",
                                "Multiply the top by $a_{11}$: it becomes $a_{11}a_{32} - a_{31}a_{12}$.",
                                "Multiply the bottom by $a_{11}$ as well: $a_{11}a_{22} - a_{21}a_{12}$. Since both were scaled by the same factor the quotient is unchanged.",
                            ],
                        },
                        {
                            "prompt": "The three pivots are $a_{11}$, then $p_2$, then $p_3$, with $p_2$ and $p_3$ as given below. Multiply them together and expand. Six terms, all of degree three.",
                            "given": r'''
$$p_2 = a_{22} - \frac{a_{21}a_{12}}{a_{11}} \qquad p_3 = \left(a_{33} - \frac{a_{31}a_{13}}{a_{11}}\right) - m_2\left(a_{23} - \frac{a_{21}a_{13}}{a_{11}}\right)$$
''',
                            "answer": r"a_{11} a_{22} a_{33} + a_{12} a_{23} a_{31} + a_{13} a_{21} a_{32} - a_{13} a_{22} a_{31} - a_{11} a_{23} a_{32} - a_{12} a_{21} a_{33}",
                            "hint": "Take the $a_{11}$ into $p_2$ first: $a_{11}p_2 = a_{11}a_{22} - a_{21}a_{12}$. Then multiply that by $p_3$ and watch the $a_{11}$ denominators cancel.",
                            "deconstruct": [
                                "$a_{11}p_2 = a_{11}a_{22} - a_{12}a_{21}$, which is the denominator of $m_2$. So in the product $a_{11}p_2p_3$ the second term of $p_3$ loses its denominator entirely.",
                                "$a_{11}p_2p_3 = (a_{11}a_{22} - a_{12}a_{21})\\left(a_{33} - \\dfrac{a_{31}a_{13}}{a_{11}}\\right) - (a_{11}a_{32} - a_{31}a_{12})\\left(a_{23} - \\dfrac{a_{21}a_{13}}{a_{11}}\\right)$.",
                                "Expand each bracket. The first gives $a_{11}a_{22}a_{33} - a_{13}a_{22}a_{31} - a_{12}a_{21}a_{33} + \\dfrac{a_{12}a_{21}a_{13}a_{31}}{a_{11}}$; the second gives $a_{11}a_{23}a_{32} - a_{13}a_{21}a_{32} - a_{12}a_{23}a_{31} + \\dfrac{a_{12}a_{31}a_{21}a_{13}}{a_{11}}$. Subtract: the two awkward fractions are identical and cancel.",
                            ],
                        },
                    ],
                    "closing": r'''
The product of the pivots is

$$a_{11}a_{22}a_{33} + a_{12}a_{23}a_{31} + a_{13}a_{21}a_{32} - a_{13}a_{22}a_{31} - a_{11}a_{23}a_{32} - a_{12}a_{21}a_{33}$$

which is the $3\times3$ determinant, six terms, three with a plus and three with a
minus. Elimination did not approximate it or find a shortcut to it; the determinant
*is* what elimination leaves on the diagonal.

Notice the $a_{11}$ bookkeeping. Every intermediate entry carried a division by
$a_{11}$, and every one of those divisions cancelled by the end — the two fractional
terms in the last expansion were identical and subtracted away. That cancellation is
not luck. Each pivot is a ratio of determinants: $p_2 = \det A_2 / \det A_1$ where
$A_k$ is the top-left $k\times k$ block, and in general $p_k = \det A_k / \det A_{k-1}$,
so the product telescopes down to $\det A_n$. The $a_{11}$s had to cancel because they
are the $\det A_1$ in the denominator of $p_2$ and the numerator of nothing else.

Two limits on what has been shown. The derivation assumed $a_{11} \neq 0$ and, at the
second sweep, that $p_2 \neq 0$ — leading principal minors that do not vanish. When one
does, an interchange is required, and each interchange multiplies the answer by $-1$;
that is the $(-1)^s$ factor in the general statement, and it is why the routine you
write in the lab has to return the swap count alongside the echelon form.

The other limit is practical. This expansion is fine to look at and wrong to compute
with beyond $n = 3$: the number of terms is $n!$, while elimination reaches the same
number in about $n^3/3$ operations. Order $20$ is the difference between microseconds
and geological time. Derive the formula once, then never use it.
''',
                },
            ],
            "numeric": [
                {
                    "title": "A determinant by elimination",
                    "minutes": 6,
                    "brief": r'''
The first rung: run the algorithm and multiply the diagonal. No rearranging, no
choosing, nothing to set up.

The only thing that can catch you is the sign. Partial pivoting will ask for two row
interchanges here, and each one flips it.
''',
                    "prompt": "What is $\\det A$?",
                    "note": "A plain number. Track the interchanges as you go.",
                    "figure": r'''
$$A = \begin{bmatrix} 2 & 1 & -1 \\ 4 & 3 & 1 \\ -2 & 5 & 3 \end{bmatrix}$$
Eliminate with partial pivoting — at each column, promote the row whose entry in that column is largest in absolute value — then multiply the pivots and apply $(-1)^{s}$ for $s$ interchanges.
''',
                    "given": [
                        {"label": "Rule", "value": "$\\det A = (-1)^{s} u_{11}u_{22}u_{33}$"},
                        {"label": "$s$", "value": "the number of row interchanges"},
                    ],
                    "aside": "Column $1$ holds $2$, $4$ and $-2$. The pivot is not the entry already sitting on the diagonal.",
                    "answer": -32.0,
                    "tol": 0.001,
                    "unit": "",
                    "hint": "Swap row $2$ up first. After clearing column $1$ the remaining entries in column $2$ are $-0.5$ and $6.5$, so a second interchange is needed.",
                    "wrong": "If you got $32$ you lost a sign somewhere — but note that two interchanges cancel, so the sign here is $+1$ and the minus comes from a negative pivot. If you got $-16$ or $-64$ you have a factor-of-two slip in one of the multipliers.",
                    "why": r'''
Column $1$ holds $2, 4, -2$; the largest in absolute value is $4$, so rows $1$ and $2$ swap. That is one interchange.
With $4$ as the pivot, $m_{21} = 2/4 = 0.5$ turns row $2$ into $(0,\; 1 - 1.5,\; -1 - 0.5) = (0,\; -0.5,\; -1.5)$, and $m_{31} = -2/4 = -0.5$ turns row $3$ into $(0,\; 5 + 1.5,\; 3 + 0.5) = (0,\; 6.5,\; 3.5)$.
Column $2$ below the pivot row holds $-0.5$ and $6.5$; the larger is $6.5$, so rows $2$ and $3$ swap. That is a second interchange.
Then $m_{32} = -0.5/6.5 = -1/13$, and the last pivot is $-1.5 + (1/13)(3.5) = -1.5 + 3.5/13 = -16/13$.
Two interchanges give $(-1)^2 = +1$, so $\det A = 4 \times 6.5 \times (-16/13) = 26 \times (-16/13) = -32$.
Cofactors confirm it: $2(9 - 5) - 1(12 + 2) + (-1)(20 + 6) = 8 - 14 - 26 = -32$.
''',
                },
                {
                    "title": "Counting the pivots",
                    "minutes": 7,
                    "brief": r'''
Applying the rule rather than evaluating it. Rank is not read off the shape of the
matrix and it is not the number of rows — it is the number of pivots the elimination
actually produces, which you only know once you have run it.

The matrix below is $3\times4$, so the rank is at most $3$. Find out what it really is.
''',
                    "prompt": "What is $\\operatorname{rank} A$?",
                    "note": "A whole number.",
                    "figure": r'''
$$A = \begin{bmatrix} 1 & 2 & -1 & 3 \\ 2 & 1 & 3 & 1 \\ 4 & 5 & 1 & 7 \end{bmatrix}$$
Eliminate to row echelon form and count the rows that are not entirely zero.
''',
                    "given": [
                        {"label": "Shape", "value": "$3\\times4$"},
                        {"label": "Upper bound", "value": "$\\operatorname{rank} A \\leq \\min(3, 4) = 3$"},
                    ],
                    "aside": "Look at the three rows before you start eliminating. One of them is not carrying any information the other two do not already have.",
                    "answer": 2.0,
                    "tol": 0.4,
                    "unit": "",
                    "hint": "Try $2 \\times$ row $1$ plus row $2$ and compare it with row $3$.",
                    "wrong": "If you answered $3$ you counted rows rather than pivots — the third row disappears entirely during elimination. If you answered $4$ you counted columns, and a $3\\times4$ matrix cannot have rank $4$.",
                    "why": r'''
Row $3$ is $2$ times row $1$ plus row $2$: $2(1, 2, -1, 3) + (2, 1, 3, 1) = (4, 5, 1, 7)$. So it is a combination of the other two and contributes no pivot.
The elimination confirms it. With partial pivoting, column $1$ promotes row $3$ (entry $4$), giving pivot row $(4, 5, 1, 7)$.
Then $m = 2/4 = 0.5$ sends $(2, 1, 3, 1)$ to $(0,\; -1.5,\; 2.5,\; -2.5)$, and $m = 1/4 = 0.25$ sends $(1, 2, -1, 3)$ to $(0,\; 0.75,\; -1.25,\; 1.25)$.
In column $2$ the pivot is $-1.5$, and $m = 0.75/(-1.5) = -0.5$ sends the last row to $(0,\; 0,\; -1.25 + 1.25,\; 1.25 - 1.25) = (0, 0, 0, 0)$.
Two pivots, so $\operatorname{rank} A = 2$. Because the matrix is $3\times4$ with rank $2$, the system $Ax = b$ has $4 - 2 = 2$ free variables whenever it is consistent, and it is not consistent for every $b$ — the rank is short of the $3$ rows.
''',
                },
                {
                    "title": "What the row operations did to it",
                    "minutes": 8,
                    "brief": r'''
Now the value has to be derived before it can be computed. You are not given the
matrix and cannot compute anything directly; you are given one number about it and a
list of things done to it.

Each of the three elementary operations has a known effect on the determinant, and
the three effects are different. Get those three rules right and the arithmetic is one
multiplication.
''',
                    "prompt": "What is $\\det B$?",
                    "note": "A plain number, sign included.",
                    "figure": r'''
$A$ is a $3\times3$ matrix with $\det A = 7$. Its entries are not given and are not needed. The matrix $B$ is built from $A$ by performing, in this order:

1. interchange rows $1$ and $3$
2. multiply row $2$ by $5$
3. add $4$ times row $1$ to row $3$
''',
                    "given": [
                        {"label": "$\\det A$", "value": "$7$"},
                        {"label": "Operations", "value": "one interchange, one scaling by $5$, one row addition"},
                    ],
                    "aside": "Two of the three operations change the determinant and one does not. Decide which is which before multiplying anything.",
                    "answer": -35.0,
                    "tol": 0.001,
                    "unit": "",
                    "hint": "An interchange multiplies the determinant by $-1$. Scaling a row by $c$ multiplies it by $c$. Adding a multiple of one row to a different row multiplies it by $1$.",
                    "wrong": "If you got $35$ you applied the scaling but not the sign from the interchange. If you got $-140$ you also multiplied by the $4$ from the row addition — that operation leaves the determinant untouched, whatever the multiple.",
                    "why": r'''
Take the operations one at a time and multiply the effects.
The interchange of rows $1$ and $3$ negates the determinant: $7 \rightarrow -7$. This follows from the alternating property — build a matrix with $r + s$ in both slots, expand by linearity, and the two surviving terms give $\det(r, s) = -\det(s, r)$.
Multiplying row $2$ by $5$ scales the determinant by $5$, because $\det$ is linear in each row separately: $-7 \rightarrow -35$.
Adding $4$ times row $1$ to row $3$ changes nothing. Linearity in row $3$ splits it into the original determinant plus $4$ times a determinant with row $1$ appearing in two places, and that second one is zero: $-35 \rightarrow -35$.
So $\det B = -35$. This is exactly why elimination is a cheap way to a determinant: the operation it performs thousands of times is the free one, and only the interchanges have to be counted.
''',
                },
                {
                    "title": "Tuning a matrix until it breaks",
                    "minutes": 9,
                    "brief": r'''
The last rung: the number you need is not in the question, and finding it means
setting up an equation of your own.

One entry of the matrix is unknown. For most values of it the matrix is invertible and
$Ax = b$ has exactly one solution for every $b$. For exactly one value it does not.
Find that value.
''',
                    "prompt": "For which value of $t$ is $A$ singular?",
                    "note": "One number. Singular means $\\det A = 0$, equivalently rank below $3$.",
                    "figure": r'''
$$A = \begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\ 7 & 8 & t \end{bmatrix}$$
Treat $t$ as an unknown, compute $\det A$ as a function of it, and solve.
''',
                    "given": [
                        {"label": "Unknown", "value": "the $(3,3)$ entry, $t$"},
                        {"label": "Condition", "value": "$\\det A = 0$"},
                    ],
                    "aside": "$\\det A$ is linear in row $3$, so it is a first-degree polynomial in $t$ — there is exactly one root.",
                    "answer": 9.0,
                    "tol": 0.001,
                    "unit": "",
                    "hint": "Expand along the bottom row, or eliminate: after clearing column $1$ with the pivot $1$, row $2$ becomes $(0, -3, -6)$ and row $3$ becomes $(0, -6, t - 21)$.",
                    "wrong": "If you got $6$ you may have set the third pivot's numerator to zero after a sign slip — check that clearing column $2$ subtracts $2$ times row $2$, not $2$ times row $1$. If you got $-9$ the sign of the $-3t$ term went astray.",
                    "why": r'''
Expanding along the bottom row: $\det A = 7(2 \cdot 6 - 3 \cdot 5) - 8(1 \cdot 6 - 3 \cdot 4) + t(1 \cdot 5 - 2 \cdot 4) = 7(-3) - 8(-6) + t(-3) = -21 + 48 - 3t = 27 - 3t$.
So $\det A = 0$ exactly when $t = 9$.
Elimination says the same thing and shows where it comes from. With pivot $1$, row $2$ becomes $(0,\; 5 - 8,\; 6 - 12) = (0, -3, -6)$ and row $3$ becomes $(0,\; 8 - 14,\; t - 21) = (0, -6, t - 21)$.
Then $m_{32} = -6/-3 = 2$, and the third pivot is $(t - 21) - 2(-6) = t - 9$. The determinant is $1 \times (-3) \times (t - 9) = 27 - 3t$, matching.
At $t = 9$ the matrix is the famous $\begin{bmatrix} 1 & 2 & 3 \\ 4 & 5 & 6 \\ 7 & 8 & 9 \end{bmatrix}$, whose rows are in arithmetic progression: row $1$ plus row $3$ equals twice row $2$, so the third pivot vanishes and the rank drops to $2$.
Note what the elimination gives you that the expansion does not — the third pivot is $t - 9$, so it tells you not only where the matrix breaks but how close to broken it is at any other $t$.
''',
                },
            ],
            "blanks": {
                "title": "One solve, every line of it",
                "minutes": 10,
                "caption": "elimination with partial pivoting on a 3x3 system, then the determinant",
                "lang": "text",
                "brief": r'''
The same routine you are about to write in the lab, run once by hand on paper. Every
line is either a choice of pivot, a multiplier, an entry after subtraction, or a
back-substituted unknown.

The last two holes are the ones the code usually gets wrong: the sign contributed by
the interchanges, and remembering to apply it at all.
''',
                "listing": """solve A x = b by elimination with partial pivoting

                 [  1   2  -1  |   2 ]
       A | b  =  [  4  -1   5  |  17 ]
                 [  2   3   1  |  11 ]

  column 1: the candidates are 1, 4, 2.  the largest in absolute value
            is 4, which sits in row ___, so that row is promoted.
            swaps = 1

                 [  4  -1   5  |  17 ]
                 [  1   2  -1  |   2 ]
                 [  2   3   1  |  11 ]

      m21 = 1 / 4 = ___
      row2 <- row2 - m21 * row1  =  [ 0   2.25  -2.25 | -2.25 ]

      m31 = 2 / 4 = 0.5
      row3 <- row3 - m31 * row1  =  [ 0   ___    -1.5  |  2.5  ]

  column 2: below the pivot row the candidates are 2.25 and 3.5.
            the larger is 3.5, so rows 2 and 3 are interchanged.
            swaps = 2

                 [  4  -1     5     |  17   ]
                 [  0   3.5  -1.5   |   2.5 ]
                 [  0   2.25 -2.25  |  -2.25]

      m32 = 2.25 / 3.5 = 9/14
      row3 <- row3 - m32 * row2  =  [ 0  0  -9/7 | -27/7 ]

  echelon form reached.  pivots: 4, 3.5, -9/7

  back-substitution, from the bottom row up

      -9/7 * x3  =  -27/7                  ->   x3 = ___
      3.5 * x2 - 1.5 * x3  =  2.5          ->   x2 = 2
      4 * x1 - 1 * x2 + 5 * x3  =  17      ->   x1 = 1

  determinant = (sign from 2 interchanges) * (product of the pivots)

      sign  =  ___
      det A =  sign * 4 * 3.5 * (-9/7)  =  ___
""",
                "blanks": [
                    {
                        "prompt": "Column 1 holds 1, 4 and 2. Which row is promoted to the pivot position?",
                        "hole": "?",
                        "opts": ["row 1", "row 2", "row 3", "no interchange is needed"],
                        "a": 1,
                        "why": "The entry $4$ sits in row $2$, so row $2$ is swapped into the pivot position. "
                               "Leaving row $1$ where it is would be legal arithmetic and poor numerics: the "
                               "multipliers would then be $4$ and $2$ rather than $0.25$ and $0.5$, and every one "
                               "of them larger than $1$ inflates the pivot row before subtracting it.",
                    },
                    {
                        "prompt": "The multiplier m21 is the entry being cleared divided by the pivot: 1 divided by 4.",
                        "hole": "?",
                        "opts": ["0.25", "4", "0.5", "-0.25"],
                        "a": 0,
                        "why": "$m_{21} = 1/4 = 0.25$. The pivot goes underneath: it is (entry to clear) over "
                               "(pivot), not the other way up. Inverting it gives $4$, and the sign is positive "
                               "because both entries are — the minus sign in the update $r_2 - m\\,r_1$ belongs to "
                               "the operation, not to the multiplier.",
                    },
                    {
                        "prompt": "row3 - 0.5 * row1 in column 2: the entries are 3 and -1.",
                        "hole": "?",
                        "opts": ["3.5", "2.5", "1.5", "2.0"],
                        "a": 0,
                        "why": "$3 - 0.5 \\times (-1) = 3 + 0.5 = 3.5$. The pivot row's entry is negative, so "
                               "subtracting a multiple of it *increases* the result. Reading the subtraction as "
                               "$3 - 0.5$ gives $2.5$ and is the commonest arithmetic slip in a hand elimination; "
                               "it also happens to be the answer that hides the second interchange, since $2.5$ is "
                               "still larger than $2.25$.",
                    },
                    {
                        "prompt": "The bottom row now reads (-9/7) x3 = -27/7.",
                        "hole": "?",
                        "opts": ["3", "-3", "1", "27/7"],
                        "a": 0,
                        "why": "$x_3 = (-27/7) \\div (-9/7) = 27/9 = 3$. Two negatives divide to a positive, and "
                               "the sevenths cancel. Answering $-3$ keeps a minus sign that has already been used "
                               "twice; answering $27/7$ forgets to divide by the pivot at all.",
                    },
                    {
                        "prompt": "Two interchanges were performed. What sign does that contribute?",
                        "hole": "?",
                        "opts": ["+1", "-1", "+2", "-2"],
                        "a": 0,
                        "why": "The sign is $(-1)^{s}$ with $s = 2$, so $(-1)^2 = +1$. Interchanges do not "
                               "accumulate additively — each one negates the determinant, so an even number of "
                               "them cancels out entirely. Only the parity of the swap count matters, which is why "
                               "the routine can return a plain integer rather than the permutation itself.",
                    },
                    {
                        "prompt": "sign * 4 * 3.5 * (-9/7). What is the determinant?",
                        "hole": "?",
                        "opts": ["-18", "18", "-14", "14"],
                        "a": 0,
                        "why": "$4 \\times 3.5 = 14$, and $14 \\times (-9/7) = -18$, with the sign $+1$ leaving it "
                               "alone. The value $18$ would follow from miscounting the interchanges as odd, and "
                               "$14$ from stopping after two pivots. Cofactor expansion along the top row of the "
                               "original matrix agrees: $1(-1 - 15) - 2(4 - 10) + (-1)(12 + 2) = -16 + 12 - 14 = -18$.",
                    },
                ],
            },
            "quiz": {
                "title": "Operations, pivots and what the determinant is worth",
                "minutes": 10,
                "questions": [
                    {
                        "q": "Which of these operations on a system of equations can change its solution set?",
                        "opts": [
                            "interchanging two equations",
                            "multiplying an equation through by $-3$",
                            "multiplying an equation through by $0$",
                            "adding $5$ times one equation to a different equation",
                        ],
                        "a": 2,
                        "why": r'''
Multiplying by zero is the one that breaks. It turns the equation into $0 = 0$, which
is true for every $v$, so information is destroyed and the solution set generally grows.
The test that separates it from the others is reversibility: an interchange is undone by
the same interchange, a scaling by $-3$ is undone by scaling by $-1/3$, and adding
$5E_i$ to $E_j$ is undone by subtracting it — but nothing recovers an equation that has
been multiplied by zero. That is exactly why the second row operation carries the
condition $c \neq 0$.
''',
                    },
                    {
                        "q": "A $3\\times5$ coefficient matrix eliminates to echelon form with pivots in columns $1$ and $4$, and the system $Ax = b$ turns out to be consistent. How many free variables does the solution have?",
                        "opts": ["$1$", "$2$", "$3$", "$5$"],
                        "a": 2,
                        "why": r'''
Every column without a pivot is a free variable. There are $5$ columns and $2$ pivots,
so columns $2$, $3$ and $5$ are free: three parameters, and the solution set is a
three-dimensional affine subspace of $\mathbf{R}^{5}$. The count is
(columns) minus (rank), never (rows) minus (rank) — the rows here number $3$, and one of
them eliminated to a zero row, which is what let the rank fall to $2$ in the first place.
''',
                    },
                    {
                        "q": "During elimination a row of the coefficient matrix becomes entirely zero while its entry in the augmented column is $-2$. What follows?",
                        "opts": [
                            "the system has no solutions",
                            "the system has infinitely many solutions",
                            "the system has a unique solution, and $-2$ is one of its components",
                            "an arithmetic error has been made, since this cannot happen",
                        ],
                        "a": 0,
                        "why": r'''
That row states $0x_1 + 0x_2 + \cdots = -2$, which no vector satisfies, so the system is
inconsistent and the solution set is empty. Everything hinges on the augmented entry: had
it been $0$ the row would read $0 = 0$, a redundant equation that costs a pivot and
typically leaves infinitely many solutions. The situation is entirely normal and signals
that $b$ lies outside the column space of $A$ — it happens for most right-hand sides
whenever the rank is below the number of rows.
''',
                    },
                    {
                        "q": "Why do production solvers interchange rows even when the current pivot is not zero?",
                        "opts": [
                            "to keep the determinant positive",
                            "because a pivot that is small relative to the entries below it produces large multipliers, and those destroy the rows being updated",
                            "because echelon form requires the diagonal to be decreasing",
                            "to reduce the operation count from $n^3/3$ to $n^2$",
                        ],
                        "a": 1,
                        "why": r'''
The multiplier is $m = a_{ij}/a_{ii}$. Let it exceed $1$ and the pivot row, scaled up, can
swamp the row being updated, so that rounding discards the updated row's own contribution
— the classic case computes $1 - 10^{4}$ and $2 - 10^{4}$, stores both as $-10^{4}$, and
loses the entire second equation. Choosing the largest available entry forces
$|m| \leq 1$ and stops that. Interchanges also flip the sign of the determinant, so they
certainly do not keep it positive; echelon form makes no demand on the size of the pivots;
and the cost stays $n^3/3$, since the scan is only $O(n^2)$ comparisons.
''',
                    },
                    {
                        "q": "Elimination on a $4\\times4$ matrix required $3$ row interchanges and produced pivots $2$, $-1$, $5$ and $0.5$. What is the determinant?",
                        "opts": ["$5$", "$-5$", "$6.5$", "$-6.5$"],
                        "a": 0,
                        "why": r'''
The pivots multiply to $2 \times (-1) \times 5 \times 0.5 = -5$, and three interchanges
contribute $(-1)^3 = -1$, so $\det A = (-1)(-5) = 5$. Two separate minus signs are in
play and both are easy to drop: keeping the negative pivot but ignoring the interchanges
gives $-5$, and adding the pivots instead of multiplying them gives $6.5$. Only the
parity of the interchange count matters, so a fourth swap would have flipped the answer
back to $-5$.
''',
                    },
                    {
                        "q": "Which of these identities is true for all square $A$ and $B$ of the same size?",
                        "opts": [
                            "$\\det(A + B) = \\det A + \\det B$",
                            "$\\det(AB) = \\det A \\, \\det B$",
                            "$\\det(cA) = c \\det A$ for every scalar $c$",
                            "$\\det(A^{\\mathsf{T}}) = -\\det A$",
                        ],
                        "a": 1,
                        "why": r'''
The determinant is multiplicative over products, and that is the identity worth
remembering. It is emphatically not additive: with $A = B = I$ in two dimensions,
$\det(A + B) = \det(2I) = 4$ while $\det A + \det B = 2$. The same example kills the
scaling claim, since $cA$ scales all $n$ rows and multiplies the determinant by $c^{n}$,
not by $c$. And transposing changes nothing at all — $\det(A^{\mathsf{T}}) = \det A$ —
which is why row operations and column operations have identical effects on it.
''',
                    },
                    {
                        "q": "A computed determinant comes out as $3 \\times 10^{-14}$. What does that tell you about the matrix?",
                        "opts": [
                            "it is definitely singular, since the value is within rounding error of zero",
                            "it is definitely non-singular, since the value is not exactly zero",
                            "very little on its own — the magnitude depends on the scale of the entries, so a nearly singular matrix has to be identified some other way",
                            "it is well conditioned, because a small determinant means small round-off",
                        ],
                        "a": 2,
                        "why": r'''
The determinant scales like the $n$th power of the entries, so its magnitude reports the
units as much as the health of the matrix. The matrix $0.1\,I$ of order $100$ has
determinant $10^{-100}$ and is as well behaved as anything ever gets, while $2I_{100}$ has
determinant $10^{30}$ and is no better. Calling $3 \times 10^{-14}$ singular or
non-singular are both unfounded for the same reason. The working diagnostic during
elimination is a pivot that has collapsed relative to the entries around it; the rigorous
one is the condition number, which needs singular values and arrives at the end of this
course.
''',
                    },
                ],
            },
            "lab": {
                "title": "Elimination with partial pivoting",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Work on plain lists of lists of numbers. Every function validates that its
argument is a non-empty rectangular matrix and raises `ValueError` otherwise.

**`forward_eliminate(a, tol=1e-12)`** — returns `(u, swaps)`: a *new* matrix in
row echelon form and the number of row interchanges performed. For each column
in turn, pick the row at or below the current pivot row with the largest
absolute entry in that column. If that entry is no bigger than `tol`, the column
carries no pivot — leave it and move on without advancing the pivot row.
Otherwise swap it into place, eliminate below it, and advance.

```text
forward_eliminate([[1, 2], [2, 4]])          ->  ([[2.0, 4.0], [0.0, 0.0]], 1)
forward_eliminate([[0, 0, 1], [0, 2, 3], [1, 4, 5]])
                                             ->  ([[1, 4, 5], [0, 2, 3], [0, 0, 1]], 1)
```

**`determinant(a)`** — square matrices only, otherwise `ValueError`. The product
of the diagonal of the echelon form, negated once per swap.

```text
determinant([[1, 2], [3, 4]])              ->  -2.0
determinant([[4, 3, 2], [1, 5, 7], [2, 2, 9]])  ->  123.0
determinant([[2, 0, 1], [1, 3, 2], [1, 1, 1]])  ->  0.0
```

**`rank(a, tol=1e-9)`** — how many rows of the echelon form are not entirely
zero (to within `tol`).

**`solve(a, b)`** — the unique solution of a square system, by eliminating on
the augmented matrix and then back-substituting. Raise `ValueError` when `a` is
not square, when `len(b)` does not match, or when any diagonal entry of the
reduced augmented matrix is at most `1e-12` in absolute value — that last case
is the singular system, and returning a wrong answer would be worse than
raising.

```text
solve([[2, 1], [1, 3]], [3, 5])  ->  [0.8, 1.4]
solve([[0, 1], [1, 0]], [1, 2])  ->  [2.0, 1.0]
```
''',
                "files": [{"name": "main.py", "content": r'''
def shape(a):
    """(rows, cols) after checking a is a non-empty rectangular matrix."""
    # your code here


def forward_eliminate(a, tol=1e-12):
    """(row echelon form, number of row swaps) with partial pivoting."""
    # your code here


def determinant(a):
    """Determinant of a square matrix, by elimination."""
    # your code here


def rank(a, tol=1e-9):
    """Number of non-zero rows in the row echelon form."""
    # your code here


def solve(a, b):
    """Unique solution of a square system; ValueError when singular."""
    # your code here


print(determinant([[4, 3, 2], [1, 5, 7], [2, 2, 9]]))
print(solve([[2, 1], [1, 3]], [3, 5]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def shape(a):
    """(rows, cols) after checking a is a non-empty rectangular matrix."""
    if not isinstance(a, list) or not a:
        raise ValueError("matrix must be a non-empty list of rows")
    cols = None
    for row in a:
        if not isinstance(row, list) or not row:
            raise ValueError("every row must be a non-empty list")
        if cols is None:
            cols = len(row)
        elif len(row) != cols:
            raise ValueError("all rows must have the same length")
    return (len(a), cols)


def forward_eliminate(a, tol=1e-12):
    """(row echelon form, number of row swaps) with partial pivoting."""
    rows, cols = shape(a)
    u = [[float(x) for x in row] for row in a]
    swaps = 0
    pivot = 0
    for col in range(cols):
        if pivot >= rows:
            break
        best = pivot
        for r in range(pivot + 1, rows):
            if abs(u[r][col]) > abs(u[best][col]):
                best = r
        if abs(u[best][col]) <= tol:
            continue
        if best != pivot:
            u[pivot], u[best] = u[best], u[pivot]
            swaps += 1
        for r in range(pivot + 1, rows):
            factor = u[r][col] / u[pivot][col]
            if factor != 0.0:
                for c in range(col, cols):
                    u[r][c] -= factor * u[pivot][c]
            u[r][col] = 0.0
        pivot += 1
    return (u, swaps)


def determinant(a):
    """Determinant of a square matrix, by elimination."""
    rows, cols = shape(a)
    if rows != cols:
        raise ValueError("determinant needs a square matrix")
    u, swaps = forward_eliminate(a)
    value = -1.0 if swaps % 2 else 1.0
    for i in range(rows):
        value *= u[i][i]
    return value


def rank(a, tol=1e-9):
    """Number of non-zero rows in the row echelon form."""
    u, _ = forward_eliminate(a)
    count = 0
    for row in u:
        if any(abs(x) > tol for x in row):
            count += 1
    return count


def solve(a, b):
    """Unique solution of a square system; ValueError when singular."""
    rows, cols = shape(a)
    if rows != cols:
        raise ValueError("solve needs a square matrix")
    if len(b) != rows:
        raise ValueError("b must have one entry per row")
    augmented = [[float(x) for x in a[i]] + [float(b[i])] for i in range(rows)]
    u, _ = forward_eliminate(augmented)
    for i in range(rows):
        if abs(u[i][i]) <= 1e-12:
            raise ValueError("matrix is singular")
    x = [0.0] * rows
    for i in range(rows - 1, -1, -1):
        total = u[i][cols]
        for j in range(i + 1, rows):
            total -= u[i][j] * x[j]
        x[i] = total / u[i][i]
    return x


print(determinant([[4, 3, 2], [1, 5, 7], [2, 2, 9]]))
print(solve([[2, 1], [1, 3]], [3, 5]))
'''}],
                "hints": [
                    "Copy the input before touching it: `u = [[float(x) for x in row] for row in a]`. Every one of these routines must leave its argument untouched.",
                    "Track the pivot row separately from the column index. A column with no usable pivot advances `col` but not `pivot` — that is exactly what makes the routine work on non-square and rank-deficient matrices.",
                    "After eliminating, assign `u[r][col] = 0.0` outright rather than trusting the subtraction to give a clean zero.",
                    "`solve` eliminates on the augmented matrix `A | b`, so the right-hand side rides along through the swaps for free; then back-substitute from the bottom row upwards.",
                ],
                "tests": [
                    {"name": "shape validates and reports", "code": r'''
assert shape([[1, 2, 3], [4, 5, 6]]) == (2, 3), f"Got {shape([[1, 2, 3], [4, 5, 6]])!r}"
assert shape([[7]]) == (1, 1), "A 1x1 matrix is still a matrix"
for _bad in [[], [[]], [[1, 2], [3]], "nope", [[1, 2], 3]]:
    try:
        shape(_bad)
        assert False, f"shape({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Echelon form and swap counting", "code": r'''
_u, _s = forward_eliminate([[1, 2], [2, 4]])
assert _s == 1, f"Partial pivoting should swap the larger row up; swaps was {_s}"
assert abs(_u[0][0] - 2.0) < 1e-12 and abs(_u[0][1] - 4.0) < 1e-12, f"First row is {_u[0]!r}"
assert all(abs(x) < 1e-12 for x in _u[1]), f"Second row should be zero, got {_u[1]!r}"
_a = [[0, 0, 1], [0, 2, 3], [1, 4, 5]]
_u, _s = forward_eliminate(_a)
assert _a == [[0, 0, 1], [0, 2, 3], [1, 4, 5]], "forward_eliminate must not mutate its argument"
for _i in range(3):
    for _j in range(_i):
        assert abs(_u[_i][_j]) < 1e-12, f"Entry ({_i}, {_j}) below the diagonal is {_u[_i][_j]!r}"
_u, _s = forward_eliminate([[0, 0], [0, 0]])
assert _s == 0 and all(abs(x) < 1e-12 for row in _u for x in row), f"Zero matrix gave {(_u, _s)!r}"
'''},
                    {"name": "Determinants", "code": r'''
for _name, _a, _want in [("2x2", [[1, 2], [3, 4]], -2.0),
                         ("3x3", [[4, 3, 2], [1, 5, 7], [2, 2, 9]], 123.0),
                         ("singular", [[2, 0, 1], [1, 3, 2], [1, 1, 1]], 0.0),
                         ("identity", [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1.0),
                         ("1x1", [[7]], 7.0),
                         ("swap", [[0, 1], [1, 0]], -1.0),
                         ("4x4", [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 13], [1, 0, 0, 1]], 4.0)]:
    _got = determinant(_a)
    assert abs(_got - _want) < 1e-9, f"determinant of the {_name} case gave {_got!r}, expected {_want}"
try:
    determinant([[1, 2, 3], [4, 5, 6]])
    assert False, "determinant of a non-square matrix should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Rank counts the pivots", "code": r'''
for _name, _a, _want in [("dependent rows", [[1, 2], [2, 4]], 1),
                         ("full 2x2", [[1, 2], [3, 4]], 2),
                         ("magic-ish 3x3", [[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2),
                         ("zero matrix", [[0, 0, 0], [0, 0, 0]], 0),
                         ("wide", [[1, 2, 3], [4, 5, 6]], 2),
                         ("tall", [[1, 2], [3, 4], [5, 6]], 2),
                         ("1x1 zero", [[0]], 0)]:
    _got = rank(_a)
    assert _got == _want, f"rank of the {_name} case gave {_got!r}, expected {_want}"
'''},
                    {"name": "Solving square systems", "code": r'''
_x = solve([[2, 1], [1, 3]], [3, 5])
assert abs(_x[0] - 0.8) < 1e-12 and abs(_x[1] - 1.4) < 1e-12, f"solve gave {_x!r}, expected [0.8, 1.4]"
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_x = solve(_a, [1, 2, 3])
for _row, _rhs in zip(_a, [1, 2, 3]):
    _lhs = sum(_c * _v for _c, _v in zip(_row, _x))
    assert abs(_lhs - _rhs) < 1e-9, f"Solution does not satisfy the system: {_lhs!r} vs {_rhs}"
assert abs(_x[0] - 6.0 / 41.0) < 1e-12, f"x[0] is {_x[0]!r}, expected 6/41"
_x = solve([[5]], [10])
assert abs(_x[0] - 2.0) < 1e-12, f"A 1x1 system gave {_x!r}, expected [2.0]"
'''},
                    {"name": "Pivoting handles a zero leading entry", "code": r'''
_x = solve([[0, 1], [1, 0]], [1, 2])
assert abs(_x[0] - 2.0) < 1e-12 and abs(_x[1] - 1.0) < 1e-12, \
    f"solve gave {_x!r}, expected [2.0, 1.0] — the first pivot must be swapped in"
_a = [[1e-14, 1.0], [1.0, 1.0]]
_x = solve(_a, [1.0, 2.0])
for _row, _rhs in zip(_a, [1.0, 2.0]):
    _lhs = _row[0] * _x[0] + _row[1] * _x[1]
    assert abs(_lhs - _rhs) < 1e-8, \
        f"A tiny leading pivot wrecked the accuracy: {_lhs!r} vs {_rhs} — pivot on the largest entry"
'''},
                    {"name": "Singular and malformed systems are refused", "code": r'''
try:
    solve([[1, 2], [2, 4]], [1, 2])
    assert False, "A singular system should raise ValueError, not return a wrong answer"
except ValueError:
    pass
try:
    solve([[1, 2, 3], [4, 5, 6]], [1, 2])
    assert False, "A non-square system should raise ValueError"
except ValueError:
    pass
try:
    solve([[1, 2], [3, 4]], [1, 2, 3])
    assert False, "A mismatched right-hand side should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "LU factorisation and reuse",
            "summary": "Doing the elimination once and spending the result many times.",
            "concepts": [
                "Elimination is a factorisation: PA = LU with L unit lower triangular",
                "The multipliers you would have discarded are exactly the entries of L",
                "Factorising costs O(n^3); each later solve costs only O(n^2)",
                "det(A) = det(P)^-1 * product of the diagonal of U, and det(P) is the swap parity",
                "Forward substitution on Pb, then back substitution on U, gives x",
                "The inverse is n solves against the columns of the identity — never how you should solve Ax = b",
                "A zero pivot in exact arithmetic means singular; in floating point it means a tolerance test",
            ],
            "read": [
                {
                    "title": "The elimination was a factorisation all along",
                    "minutes": 14,
                    "body": r'''
You solved $Ax = b$ this morning. This afternoon the same $A$ comes back with a
different $b$: a new load on the same structure, the next column of the identity because
somebody wants an inverse, one more step of an iteration that changes nothing but the
right-hand side. Running the elimination again costs exactly what it cost the first
time, and that should annoy you, because the elimination barely looked at $b$. It chose
its pivots by comparing entries of $A$. It computed its multipliers from entries of $A$.
The right-hand side was carried along, updated at every step, and never once consulted.

So the work splits in two. One part depends on $A$ alone and could in principle be done
once and kept; the other depends on $b$ and has to be redone. This module is about
writing the first part down. It turns out to be a pair of triangular matrices, and the
surprise is that you have been computing them all along and throwing them away.

## One row operation, written as a matrix

Elimination does one thing over and over: replace row $r$ by row $r$ minus $m$ times row
$k$, with $r > k$. Write $e_i$ for the $i$th standard basis column. Then
$e_r e_k^{\mathsf{T}}$ is the matrix that is zero everywhere except for a single $1$ in
position $(r,k)$, and

$$E = I - m\,e_r e_k^{\mathsf{T}}$$

is the identity with $-m$ dropped into position $(r,k)$. For $n = 3$, $r = 3$, $k = 1$:

$$E = \begin{bmatrix} 1 & 0 & 0 \\ 0 & 1 & 0 \\ -m & 0 & 1 \end{bmatrix}$$

Multiply $E$ into $A$. Row $i$ of $EA$ is row $i$ of $E$ against the columns of $A$, so
rows $1$ and $2$ come through untouched and row $3$ becomes $-m$ times row $1$ plus row
$3$. That is the row operation exactly, and every step of the elimination is a left
multiplication by one of these.

## Undoing it costs one sign and nothing else

Here is the fact the whole factorisation rests on. Multiply $E$ by the same matrix with
the sign of $m$ flipped:

$$(I - m\,e_r e_k^{\mathsf{T}})(I + m\,e_r e_k^{\mathsf{T}}) = I - m^{2}\,e_r\,(e_k^{\mathsf{T}} e_r)\,e_k^{\mathsf{T}}$$

The middle factor $e_k^{\mathsf{T}} e_r$ is a $1\times1$ matrix — a number — and it is
the dot product of two *different* standard basis vectors, so it is $0$. The quadratic
term vanishes completely and

$$E^{-1} = I + m\,e_r e_k^{\mathsf{T}}$$

The inverse of an elimination step is the same step with a plus sign. No fractions, no
arithmetic, nothing to compute. That is what makes everything below cheap, and it is
also the reason the entries of $L$ turn out to be the multipliers themselves rather than
their negatives — a sign error waiting for anyone who reasons "$L$ records what was
done, and what was done was a subtraction".

## The product of the inverses does not mix

Now take a whole column at once. Clearing column $k$ means subtracting multiples of the
pivot row from every row beneath it, so

$$L_k = I - \sum_{r > k} m_{rk}\,e_r e_k^{\mathsf{T}}, \qquad L_k^{-1} = I + \sum_{r > k} m_{rk}\,e_r e_k^{\mathsf{T}}$$

— the same cancellation works term by term, because $e_k^{\mathsf{T}} e_r = 0$ for every
$r > k$. Running the elimination to the end is

$$L_{n-1}\cdots L_2 L_1 A = U$$

with $U$ upper triangular, and therefore

$$A = L_1^{-1} L_2^{-1} \cdots L_{n-1}^{-1}\,U$$

That product of inverses is the object we are after. Multiply two of them, with $k < j$:

$$\left(I + \sum_{r>k} m_{rk} e_r e_k^{\mathsf{T}}\right)\left(I + \sum_{s>j} m_{sj} e_s e_j^{\mathsf{T}}\right) = I + \sum_{r>k} m_{rk} e_r e_k^{\mathsf{T}} + \sum_{s>j} m_{sj} e_s e_j^{\mathsf{T}} + \sum_{r,s} m_{rk}m_{sj}\, e_r\,(e_k^{\mathsf{T}} e_s)\,e_j^{\mathsf{T}}$$

Every $s$ in the second sum satisfies $s > j > k$, so $e_k^{\mathsf{T}} e_s = 0$ every
time and the cross term disappears. The product is nothing but the two sums laid on top
of one another. Repeat across all the factors:

$$L = L_1^{-1} L_2^{-1}\cdots L_{n-1}^{-1} = I + \sum_{k}\sum_{r>k} m_{rk}\,e_r e_k^{\mathsf{T}}$$

In words: **$L$ is the unit lower triangular matrix whose $(r,k)$ entry is the multiplier
that cleared position $(r,k)$.** Not a transformed multiplier, not a combination of
several — the number itself, sitting in the position of the entry it killed. Assembling
$L$ costs zero operations, because the elimination has already computed every entry of
it and would otherwise throw them away.

That is the theorem. **If the elimination runs to the end without an interchange, then
$A = LU$**, with $L$ holding the multipliers and $U$ the echelon form.

## A factorisation you can check by hand

Take

$$A = \begin{bmatrix} 2 & 1 & 1 \\ 4 & -6 & 0 \\ -2 & 7 & 2 \end{bmatrix}$$

and eliminate using the diagonal entries as pivots. Column $1$, pivot $2$:

$$m_{21} = \frac{4}{2} = 2, \qquad \text{row}_2 - 2\,\text{row}_1 = (0,\; -6 - 2,\; 0 - 2) = (0,\; -8,\; -2)$$

$$m_{31} = \frac{-2}{2} = -1, \qquad \text{row}_3 + 1\,\text{row}_1 = (0,\; 7 + 1,\; 2 + 1) = (0,\; 8,\; 3)$$

Column $2$, pivot $-8$:

$$m_{32} = \frac{8}{-8} = -1, \qquad \text{row}_3 + 1\,\text{row}_2 = (0,\; 0,\; 3 - 2) = (0,\; 0,\; 1)$$

Three multipliers — $2$, $-1$, $-1$ — and an echelon form. Write each multiplier where it
belongs:

$$L = \begin{bmatrix} 1 & 0 & 0 \\ 2 & 1 & 0 \\ -1 & -1 & 1 \end{bmatrix} \qquad U = \begin{bmatrix} 2 & 1 & 1 \\ 0 & -8 & -2 \\ 0 & 0 & 1 \end{bmatrix}$$

Check it, one row at a time. Row $2$ of $LU$ is
$2(2,1,1) + 1(0,-8,-2) = (4,\; 2-8,\; 2-2) = (4,-6,0)$. Row $3$ is
$-1(2,1,1) - 1(0,-8,-2) + 1(0,0,1) = (-2,\; -1+8,\; -1+2+1) = (-2,7,2)$. Both are rows of
$A$, and nothing was computed that the elimination had not already computed.

## The case where $A = LU$ does not exist

Now

$$B = \begin{bmatrix} 1 & 2 & 3 \\ 2 & 4 & 1 \\ 3 & 5 & 2 \end{bmatrix}$$

with $\det B = 1(8-5) - 2(4-3) + 3(10-12) = 3 - 2 - 6 = -5$, so $B$ is invertible, and
every one of its entries is nonzero. Eliminate. Column $1$, pivot $1$: $m_{21} = 2$ sends
row $2$ to $(0,\; 4-4,\; 1-6) = (0, 0, -5)$, and $m_{31} = 3$ sends row $3$ to
$(0,\; 5-6,\; 2-9) = (0, -1, -7)$.

Column $2$ now holds a $0$ in the pivot position with a nonzero entry below it. No choice
of multipliers rescues this, and you can see the impossibility without the algorithm.
Suppose $B = LU$ with $L$ unit lower triangular. Matching entries in order forces
$u_{11} = 1$, $u_{12} = 2$, $u_{13} = 3$; then $l_{21}u_{11} = 2$ gives $l_{21} = 2$;
then $l_{21}u_{12} + u_{22} = 4$ gives $4 + u_{22} = 4$, so $u_{22} = 0$; then
$l_{31}u_{11} = 3$ gives $l_{31} = 3$. The $(3,2)$ entry of $LU$ is now
$l_{31}u_{12} + l_{32}u_{22} = 3 \cdot 2 + l_{32}\cdot 0 = 6$, whatever $l_{32}$ is, and
$B$ has $5$ in that position. There is no factorisation.

The criterion behind this is worth keeping: **if every leading principal submatrix of
$A$ is nonsingular then $A = LU$ exists with $L$ unit lower triangular, and is unique;
and if $A$ itself is nonsingular while some leading principal submatrix is not, then no
such factorisation exists.** (The two-way version needs $A$ nonsingular: the zero matrix
factors as $I \cdot 0$ and has singular blocks everywhere.) Here the
leading $2\times2$ block is $\begin{bmatrix}1&2\\2&4\end{bmatrix}$
with determinant $0$ — which is the vanished second pivot, because the product of the
first $k$ pivots is the determinant of the leading $k\times k$ block. Invertibility of
$A$ says nothing about those blocks, and neither does having no zero entries.

Interchange rows $2$ and $3$ and the obstruction is gone. The new second row is
$(0,-1,-7)$, the third is $(0,0,-5)$, and no further elimination is needed:

$$U = \begin{bmatrix} 1 & 2 & 3 \\ 0 & -1 & -7 \\ 0 & 0 & -5 \end{bmatrix}, \qquad \det B = (-1)^{1}(1)(-1)(-5) = -5$$

which agrees with the cofactor value.

## The mistake: leaving the multipliers behind

Here is the part that is genuinely easy to get wrong, and that the lab's tests will
catch. When you interchange rows $2$ and $3$ of the working matrix, you must interchange
rows $2$ and $3$ of the multipliers already stored as well.

The stored multipliers are $m_{21} = 2$, belonging to the original row $2$, and
$m_{31} = 3$, belonging to the original row $3$. The interchange moves the original row
$3$ into slot $2$ and the original row $2$ into slot $3$, so they travel with their rows:

$$L = \begin{bmatrix} 1 & 0 & 0 \\ 3 & 1 & 0 \\ 2 & 0 & 1 \end{bmatrix}$$

and $PB$ lists the rows of $B$ in the order $1, 3, 2$ — the lab's zero-based `perm` for
this is `[0, 2, 1]` — giving $(1,2,3)$, $(3,5,2)$, $(2,4,1)$. Check: row $2$ of $LU$ is
$3(1,2,3) + (0,-1,-7) = (3,\; 6-1,\; 9-7) = (3,5,2)$, and row $3$ is
$2(1,2,3) + 0(0,-1,-7) + (0,0,-5) = (2,\; 4,\; 6-5) = (2,4,1)$. Both correct.

Leave the multipliers where they sat and you get

$$L' = \begin{bmatrix} 1 & 0 & 0 \\ 2 & 1 & 0 \\ 3 & 0 & 1 \end{bmatrix}$$

whose second row against $U$ gives $2(1,2,3) + (0,-1,-7) = (2, 3, -1)$ — a vector that is
not a row of $B$ at all, nor of any permutation of it. The temptation is real: the
multipliers sitting below the current column look like scratch work, unfinished, part of
a calculation still in progress. They are not. Each is a completed record of an operation
performed on a specific row, and when that row moves, its record moves with it.

## Where this stops

Two limits, stated plainly.

$A = LU$ is not available for every invertible matrix — $B$ was the counterexample, and
the leading-minor criterion says exactly which matrices are excluded. $PA = LU$ *is*
available for every square $A$, because at each column you can always promote a nonzero
entry into the pivot position if one exists, and if none exists the column below the
pivot is already clear and the elimination moves on with a zero pivot and a singular
matrix. So the version with a permutation is universal and the version without it is not.

And the interchange is not optional when the pivot is merely small rather than exactly
zero. The previous module showed a $2\times2$ in which a pivot of $10^{-4}$ destroyed
every correct digit; nothing about factoring rather than solving changes that, because
$L$ and $U$ are built by exactly the same arithmetic on exactly the same numbers. Partial
pivoting is part of the factorisation, not a decoration on it, and the permutation it
produces has to be carried along and applied — which is where the next reading starts.
'''},
                {
                    "title": "Spending the factors: two triangular passes",
                    "minutes": 13,
                    "body": r'''
Once $PA = LU$ is in hand, what do you actually own? Not a solution — there is no $b$
anywhere in the factorisation. What you own is every question about $A$ that does not
mention $b$, already answered. It is worth being exact about which questions those are
and what each one now costs, because the answer is the reason anybody bothers.

## The system splits into two triangular ones

Start from $Ax = b$ and multiply through by $P$. Reordering the equations of a system is
the one operation that certainly changes nothing about its solutions, so

$$Ax = b \Leftrightarrow PAx = Pb \Leftrightarrow LUx = Pb$$

Now name the middle of that product. Let $y = Ux$. Then $Ly = Pb$, and two triangular
systems are solved one after the other.

**Forward, on $L$.** The first row of $L$ is $(1, 0, \dots, 0)$, so $y_1 = (Pb)_1$ with no
work at all. Row $i$ reads $l_{i1}y_1 + \cdots + l_{i,i-1}y_{i-1} + y_i = (Pb)_i$, and
every $y$ on the left except $y_i$ is already known, so

$$y_i = (Pb)_i - \sum_{j<i} l_{ij}\,y_j$$

There is no division anywhere, because the diagonal of $L$ is all ones. And note where
the permutation goes: onto $b$, and onto nothing else. $L$ and $U$ are already the
factors of the *permuted* matrix; permuting them again would apply the reordering twice.

**Backward, on $U$.** The last row reads $u_{nn}x_n = y_n$, so $x_n = y_n/u_{nn}$, and
working upwards

$$x_i = \frac{1}{u_{ii}}\left(y_i - \sum_{j>i} u_{ij}\,x_j\right)$$

Here there is a division at every row, by a pivot. That is the only place a pivot can
hurt you, and it is why the pivots were chosen large in the first place.

## Counting the work

Count a multiply-and-subtract as one operation, and a division as one operation.

Forward substitution: row $i$ needs $i-1$ of them, so the pass costs
$0 + 1 + \cdots + (n-1) = n(n-1)/2$.

Back substitution: row $i$ needs $n-i$ multiply-subtracts and one division, so the pass
costs $n(n-1)/2 + n = n(n+1)/2$.

A solve is therefore

$$\frac{n(n-1)}{2} + \frac{n(n+1)}{2} = \frac{n^{2} - n + n^{2} + n}{2} = n^{2}$$

operations. Exactly $n^{2}$ — not approximately, not to leading order.

The factorisation is a different order of magnitude. Clearing column $k$ takes $n-k$
divisions, one per multiplier, and then updates $n-k$ rows across the $n-k$ columns to
the right of the pivot, which is $(n-k)^{2}$ multiply-subtracts. Summing over the
columns,

$$\sum_{k=1}^{n-1}(n-k)^{2} = \sum_{j=1}^{n-1} j^{2} = \frac{(n-1)n(2n-1)}{6} \approx \frac{n^{3}}{3}$$

plus $n(n-1)/2 \approx n^{2}/2$ divisions, a lower order that drops out for large $n$. So
the factorisation is $n^{3}/3$, a solve is $n^{2}$, and the ratio between them is $n/3$.

Put a number on that. At $n = 1200$ one factorisation costs what $400$ solves cost. If
four hundred right-hand sides arrive, factoring once and solving four hundred times costs
about *two* eliminations; re-eliminating from scratch each time costs four hundred. The
factor of two hundred is the whole content of this module.

## The determinant, sign and all

The determinant of a triangular matrix is the product of its diagonal. Expand an upper
triangular matrix along its first column: only the $(1,1)$ entry is nonzero there, so a
single term survives, and its minor is again upper triangular with one row and one column
fewer. Induction finishes it, and the same argument along the first row handles lower
triangular.

So $\det L = 1$, because $L$ is unit lower triangular, and
$\det U = u_{11}u_{22}\cdots u_{nn}$. Take determinants across $PA = LU$:

$$\det(P)\,\det(A) = \det(L)\,\det(U) = u_{11}u_{22}\cdots u_{nn}$$

A single interchange negates a determinant, so $s$ of them give $\det P = (-1)^{s}$. And
$(-1)^{s}$ is its own reciprocal, so dividing and multiplying are the same move:

$$\det A = (-1)^{s}\,u_{11}u_{22}\cdots u_{nn}$$

This is how every serious library computes a determinant, and it costs $n^{3}/3$ — against
$n!$ terms for the cofactor expansion. At $n = 20$ that is about $2700$ operations against
$2.4\times10^{18}$.

## One factorisation, two right-hand sides

Take the factors built in the previous reading,

$$L = \begin{bmatrix} 1 & 0 & 0 \\ 2 & 1 & 0 \\ -1 & -1 & 1 \end{bmatrix} \qquad U = \begin{bmatrix} 2 & 1 & 1 \\ 0 & -8 & -2 \\ 0 & 0 & 1 \end{bmatrix}$$

with $P = I$, and solve first with $b = (5, -2, 9)$.

Forward:

$$y_1 = 5, \qquad y_2 = -2 - 2(5) = -12, \qquad y_3 = 9 - (-1)(5) - (-1)(-12) = 9 + 5 - 12 = 2$$

Backward:

$$x_3 = \frac{2}{1} = 2, \qquad x_2 = \frac{-12 - (-2)(2)}{-8} = \frac{-8}{-8} = 1, \qquad x_1 = \frac{5 - 1(1) - 1(2)}{2} = \frac{2}{2} = 1$$

So $x = (1, 1, 2)$. Substituting into $A$: $2 + 1 + 2 = 5$, $4 - 6 + 0 = -2$,
$-2 + 7 + 4 = 9$. Correct.

Now $b = (1, 0, 0)$, with **no new factorisation**.

Forward:

$$y_1 = 1, \qquad y_2 = 0 - 2(1) = -2, \qquad y_3 = 0 - (-1)(1) - (-1)(-2) = 1 - 2 = -1$$

Backward:

$$x_3 = -1, \qquad x_2 = \frac{-2 - (-2)(-1)}{-8} = \frac{-4}{-8} = 0.5, \qquad x_1 = \frac{1 - 1(0.5) - 1(-1)}{2} = \frac{1.5}{2} = 0.75$$

So $x = (0.75,\; 0.5,\; -1)$, and because $b$ was the first column of $I$, this is the
first column of $A^{-1}$. Cofactors confirm it: $\det A = 2(-8)(1) = -16$, the cofactors
along the first row of $A$ are $-12$, $-8$ and $16$, and
$(-12, -8, 16)/(-16) = (0.75, 0.5, -1)$.

The second solve did nine operations. So did the factorisation, roughly — $n = 3$ is far
too small for the asymptotics to bite. At $n = 1000$ the second solve would cost about a
three-hundredth of the first, and that is the shape of the thing.

## The mistake: permuting the factors

The commonest failure in a first implementation of `lu_solve` is not an arithmetic slip.
It is applying the permutation in the wrong place — reordering the rows of $L$, or of
$U$, or reordering $x$ at the end — and it is tempting because $P$ arrived attached to
$A$, so it feels like part of the matrix rather than part of the right-hand side.

Trace what it costs. Suppose $P$ swaps rows $1$ and $2$, and you solve $Ly = b$ instead of
$Ly = Pb$. Then row $1$ of the triangular system, which belongs to the equation that was
originally row $2$ of $A$, is being fed $b_1$. Every subsequent $y$ inherits the error,
and the returned $x$ solves a system whose coefficient rows and right-hand-side entries
have been paired up wrongly. It will not be close, and — this is the part that costs an
afternoon — nothing in the arithmetic complains: no division by zero, no exception, just a
confident wrong vector. The only way to catch it is to substitute $x$ back into the
original $A$, which is why the lab's tests do exactly that.

## Where this stops

The count $n^{2}$ per solve assumed that $L$ and $U$ are dense — that you touch every
entry below and above the diagonal. Most large systems in practice are sparse, and for
those the factorisation costs far less than $n^{3}/3$, but only if the elimination order
is chosen to stop $L$ and $U$ filling in with nonzeros that $A$ never had. Partial
pivoting chooses that order on numerical grounds alone and can be exactly the wrong
choice for sparsity, so sparse solvers trade the two off against each other. That is a
different subject; what carries over unchanged is the split between work that depends on
$A$ and work that depends on $b$.

The determinant formula, meanwhile, is exact but almost useless as a test. Multiply a
healthy $100\times100$ matrix by $0.1$ and its determinant is divided by $10^{100}$
while the matrix stays exactly as invertible as it was — same pivots up to the scaling,
same solutions up to the scaling, same everything. Scale by $10^{-4}$ instead and the
product of the pivots falls below the smallest positive double and is computed as $0$.
So $\det A = 0$ means singular in exact arithmetic, but a *computed* determinant that is
small, or even zero, means nothing at all. The next reading is about the test that
replaces it.
'''},
                {
                    "title": "The inverse you should not compute, and the pivot you cannot trust",
                    "minutes": 12,
                    "body": r'''
The lab asks you to write `inverse`. This reading tells you never to use it to solve a
system. Both are right, and the reason is arithmetic rather than taste — so it is worth
doing the count instead of repeating the slogan.

There is a second slogan in the neighbourhood that is worse: "the pivot was not zero, so
the matrix is invertible, so the answer is fine". The first two clauses are about
mathematics and the third is about floating point, and the step between them is not
valid. Both halves of this reading are about the gap.

## The inverse is $n$ solves

The definition gives the algorithm. $A A^{-1} = I$ says that column $j$ of $A^{-1}$ is
the vector $x$ with $Ax = e_j$. So: factor once, then solve $n$ times, once against each
column of the identity, and stack the answers as columns.

Do it on the lab's example. $A = \begin{bmatrix}4&7\\2&6\end{bmatrix}$
needs no interchange, since $|4| > |2|$. One multiplier, $m_{21} = 2/4 = 0.5$, sends row
$2$ to $(0,\; 6 - 0.5\cdot 7) = (0,\; 2.5)$, so

$$L = \begin{bmatrix} 1 & 0 \\ 0.5 & 1 \end{bmatrix}, \qquad U = \begin{bmatrix} 4 & 7 \\ 0 & 2.5 \end{bmatrix}, \qquad \det A = 4(2.5) = 10$$

Solve against $e_1 = (1,0)$. Forward: $y_1 = 1$, $y_2 = 0 - 0.5(1) = -0.5$. Backward:
$x_2 = -0.5/2.5 = -0.2$, then $x_1 = (1 - 7(-0.2))/4 = (1 + 1.4)/4 = 0.6$. First column:
$(0.6, -0.2)$.

Solve against $e_2 = (0,1)$. Forward: $y_1 = 0$, $y_2 = 1 - 0.5(0) = 1$. Backward:
$x_2 = 1/2.5 = 0.4$, then $x_1 = (0 - 7(0.4))/4 = -2.8/4 = -0.7$. Second column:
$(-0.7, 0.4)$.

$$A^{-1} = \begin{bmatrix} 0.6 & -0.7 \\ -0.2 & 0.4 \end{bmatrix}$$

Check: $4(0.6) + 7(-0.2) = 2.4 - 1.4 = 1$ and $4(-0.7) + 7(0.4) = -2.8 + 2.8 = 0$. Two
solves and one factorisation, exactly as promised. Notice that each column came out of
the *same* $L$ and $U$ — that is the reuse this module is about, and `inverse` is its
purest demonstration.

## What it costs, and what it fails to buy

Now the arithmetic that condemns it as a way to solve $Ax = b$. A solve costs $n^{2}$ and
the factorisation costs $n^{3}/3$, so

$$\text{cost of } A^{-1} \;=\; \frac{n^{3}}{3} \;+\; n\cdot n^{2} \;=\; \frac{4n^{3}}{3}$$

The first term is the one factorisation and the second is the $n$ solves. Four times the
cost of just factoring. And once you have $A^{-1}$, computing $A^{-1}b$ is
a matrix-vector product: $n^{2}$ operations — precisely the cost of the forward and back
passes you were trying to avoid. So the inverse charges four times as much up front and
then charges the same per right-hand side. There is no regime, no number of right-hand
sides, in which it wins.

It is also less accurate, and that argument survives even if the cost did not. Every
entry of $A^{-1}$ is the output of a full solve and carries its own rounding error;
multiplying by it commits a fresh round of error on top of errors the triangular passes
never made. The rule is short: compute the inverse when you genuinely need its entries —
a covariance matrix, an explicit formula someone else will read — which is rare. To solve
a system, solve the system.

## The pivot test, and the scale nobody supplied

Now the second half. In exact arithmetic singularity is decidable: if at some column
every entry from the pivot row down is zero, there is no pivot, a column of $U$ is short
and $A$ is singular. In floating point that almost never happens. Rounding leaves
$3\times10^{-17}$ where mathematics has $0$, so a test for exact equality would certify
every singular matrix as invertible. The code therefore tests
$|\text{pivot}| \le \tau$ — and everything now depends on $\tau$.

The lab's default is $\tau = 10^{-12}$, an absolute threshold, and an absolute threshold
is wrong in both directions.

**Wrong in one direction.** Take the same
$A = \begin{bmatrix}4&7\\2&6\end{bmatrix}$ and scale it by
$10^{-13}$. Its pivots become $4\times10^{-13}$ and $2.5\times10^{-13}$, both below
$10^{-12}$, so `lu_decompose` raises `ValueError: matrix is singular`. But the matrix is
not singular by any margin: its determinant is $10\times10^{-26} = 10^{-25}$, its inverse
is $10^{13}$ times the inverse computed above, every entry of which is comfortably inside
double precision, and the solution of $Ax = b$ is as accurate as before. Nothing has
happened except a change of units — grams instead of kilotonnes — and the routine has
declared the problem unsolvable.

**Wrong in the other.** Take

$$C = \begin{bmatrix} 10^{8} & 2\times10^{8} \\ 2\times10^{8} & 4\times10^{8} + 1 \end{bmatrix}$$

Partial pivoting interchanges the rows, since $|2\times10^{8}| > |10^{8}|$, so the pivot
is $2\times10^{8}$ and $m_{21} = 0.5$. The second row becomes
$(0,\; 2\times10^{8} - 0.5(4\times10^{8} + 1)) = (0,\; -0.5)$, so the second pivot is
$-0.5$. That clears $\tau = 10^{-12}$ by eleven orders of magnitude and the routine
reports no difficulty whatsoever. The determinant checks out —
$(-1)^{1}(2\times10^{8})(-0.5) = 10^{8}$, which is what cofactors give. Yet the second
pivot is $10^{-9}$ times the size of the entries around it, and

$$C^{-1} = \begin{bmatrix} 4 + 10^{-8} & -2 \\ -2 & 1 \end{bmatrix}$$

Measure both by their largest row sum of absolute values: $C$ gives
$6\times10^{8}$ and $C^{-1}$ gives $6$, so their product — the condition number in that
norm — is about $3.6\times10^{9}$. With a machine epsilon of $2.2\times10^{-16}$
that is a relative error in $x$ of up to $8\times10^{-7}$: roughly six correct digits out
of sixteen, on a problem the pivot test called healthy.

The repair for the first failure is easy — compare the pivot to the size of the matrix
rather than to $1$, testing $|\text{pivot}| \le \tau\,\max_{ij}|a_{ij}|$, which is
invariant under a change of units. The repair for the second is not a threshold at all.

## The mistake, and why it is tempting

The mistake is reading a passed pivot test as a statement about accuracy. It is a
statement about invertibility, and only that.

It is tempting because in exact arithmetic the two questions really are the same one:
$\det A \neq 0$ if and only if $Ax = b$ has a unique solution, full stop, no gradations.
Floating point pulls them apart. Invertibility stays a yes-or-no property of the matrix;
accuracy becomes a continuous property of the matrix *and* the arithmetic, and the second
can be arbitrarily bad while the first is comfortably true. $C$ above is invertible and
always will be. It is also, at double precision, a matrix that discards ten of your
sixteen digits.

## Where this stops

Everything said here about $\tau$ is a stopgap. The honest quantity is the condition
number $\kappa(A)$ — the size of $A$ times the size of $A^{-1}$, measured in any matching
pair of matrix norms — which bounds how much a relative perturbation of
the data, including the rounding committed while reading $A$ into memory, can change
the solution, and predicts a loss of about $\log_{10}\kappa$ decimal digits. It cannot be
read off the pivots: matrices exist whose pivots are all of order $1$ and whose condition
number is enormous, and the smallest pivot is a lower bound on trouble rather than a
measure of it. Computing $\kappa$ honestly needs the singular values, which arrive in the
last module of this course.

Two things carry forward until then. A tolerance test tells you whether the factorisation
could be completed, not whether its output is worth anything. And the residual — the
largest entry of $Ax - b$ for the $x$ you computed — is cheap, one matrix-vector product
at $n^{2}$ operations on top of a solve that cost the same, so there is never a good
reason not to compute it and look.
'''},
            ],
            "derive": [
                {
                    "title": "The multipliers you were about to throw away",
                    "minutes": 15,
                    "vars": ["a_11", "a_12", "a_13", "a_21", "a_22", "a_23",
                             "a_31", "a_32", "a_33", "m_21", "m_31", "m_32", "u_22"],
                    "brief": r'''
The claim of this module is that $L$ needs no arithmetic: its entries are the
multipliers, each one sitting in the position of the entry it cleared. That is easy to
assert and easy to believe wrongly, so run it symbolically on a $3\times3$ and watch it
close.

$$A = \begin{bmatrix} a_{11} & a_{12} & a_{13} \\ a_{21} & a_{22} & a_{23} \\ a_{31} & a_{32} & a_{33} \end{bmatrix}$$

with $a_{11} \neq 0$ and a second pivot that is also nonzero, so no interchange is
needed. Clear column $1$, then column $2$, and keep every multiplier.

Give every answer in terms of the entries $a_{ij}$ — not in terms of $m_{21}$, $m_{31}$
or $u_{22}$, which are names for things you are being asked to write out.
''',
                    "steps": [
                        {
                            "prompt": "Row $3$ is replaced by row $3$ minus $m_{31}$ times row $1$, and the $(3,1)$ entry must vanish. What is $m_{31}$?",
                            "answer": r"\frac{a_{31}}{a_{11}}",
                            "hint": r"The new $(3,1)$ entry is $a_{31} - m_{31}a_{11}$. Set it to zero.",
                        },
                        {
                            "prompt": "With that $m_{31}$, what sits in position $(3,2)$ after the operation? Leave the fraction as it stands.",
                            "answer": r"a_{32} - \frac{a_{31} a_{12}}{a_{11}}",
                            "hint": r"The whole row becomes $(a_{31} - m_{31}a_{11},\; a_{32} - m_{31}a_{12},\; a_{33} - m_{31}a_{13})$. Take the middle slot and substitute $m_{31}$.",
                            "deconstruct": [
                                r"Every entry of row $3$ is hit by the same operation: $a_{3j} \mapsto a_{3j} - m_{31}a_{1j}$.",
                                r"For $j = 2$ that is $a_{32} - m_{31}a_{12}$.",
                                r"Now put $m_{31} = a_{31}/a_{11}$ into it. Do not clear the fraction — the next steps are tidier if you leave it.",
                            ],
                        },
                        {
                            "prompt": "Row $2$ was cleared the same way, with $m_{21} = a_{21}/a_{11}$. What sits in position $(2,2)$ afterwards? This entry is the second pivot $u_{22}$.",
                            "answer": r"a_{22} - \frac{a_{21} a_{12}}{a_{11}}",
                            "hint": r"Same operation, one row up: $a_{22} - m_{21}a_{12}$ with $m_{21} = a_{21}/a_{11}$.",
                        },
                        {
                            "prompt": "$m_{32}$ is the entry from the $(3,2)$ slot divided by the pivot $u_{22}$. Write it as a single fraction with no fraction inside it.",
                            "answer": r"\frac{a_{11} a_{32} - a_{31} a_{12}}{a_{11} a_{22} - a_{21} a_{12}}",
                            "hint": r"Divide the second answer by the third, then multiply the top and the bottom of the result by $a_{11}$.",
                            "deconstruct": [
                                r"$m_{32} = \left(a_{32} - \dfrac{a_{31}a_{12}}{a_{11}}\right) \div \left(a_{22} - \dfrac{a_{21}a_{12}}{a_{11}}\right)$.",
                                r"Multiply the numerator and the denominator of that quotient by $a_{11}$.",
                                r"The top becomes $a_{11}a_{32} - a_{31}a_{12}$ and the bottom becomes $a_{11}a_{22} - a_{21}a_{12}$, and no fraction is left inside a fraction.",
                            ],
                        },
                        {
                            "prompt": "Now test the claim. $L$ is asserted to be $\\begin{bmatrix} 1 & 0 & 0 \\\\ m_{21} & 1 & 0 \\\\ m_{31} & m_{32} & 1 \\end{bmatrix}$. Multiply row $3$ of $L$ by column $1$ of $U$, which is $(a_{11}, 0, 0)$, and simplify.",
                            "answer": r"a_{31}",
                            "hint": r"The product is $m_{31}a_{11} + m_{32}\cdot 0 + 1 \cdot 0$, and $m_{31} = a_{31}/a_{11}$.",
                        },
                        {
                            "prompt": "The real test. Column $2$ of $U$ is $(a_{12},\\; u_{22},\\; 0)$. Multiply row $3$ of $L$ by it — that is $m_{31}a_{12} + m_{32}u_{22}$ — and simplify completely.",
                            "answer": r"a_{32}",
                            "hint": r"Notice that $u_{22} = (a_{11}a_{22} - a_{21}a_{12})/a_{11}$, which is exactly the denominator of $m_{32}$ divided by $a_{11}$. The product $m_{32}u_{22}$ therefore collapses.",
                            "deconstruct": [
                                r"Write $u_{22} = a_{22} - \dfrac{a_{21}a_{12}}{a_{11}} = \dfrac{a_{11}a_{22} - a_{21}a_{12}}{a_{11}}$.",
                                r"Then $m_{32}u_{22} = \dfrac{a_{11}a_{32} - a_{31}a_{12}}{a_{11}a_{22} - a_{21}a_{12}} \cdot \dfrac{a_{11}a_{22} - a_{21}a_{12}}{a_{11}} = \dfrac{a_{11}a_{32} - a_{31}a_{12}}{a_{11}}$.",
                                r"Add $m_{31}a_{12} = \dfrac{a_{31}a_{12}}{a_{11}}$. The two $a_{31}a_{12}$ terms cancel and $a_{11}a_{32}/a_{11}$ is left.",
                            ],
                        },
                    ],
                    "closing": r'''
Every entry of the product came back as the entry of $A$ it started from, and the only
numbers used were multipliers the elimination had already computed. Nothing in the check
needed the values of the $a_{ij}$, so it holds for every $3\times3$ whose first two
pivots are nonzero.

The general statement is the one proved in the first reading. Each elimination step is
$E = I - m\,e_r e_k^{\mathsf{T}}$, its inverse is the same matrix with $+m$, and the
product of all the inverses has no cross terms because $e_k^{\mathsf{T}} e_s = 0$
whenever $s > k$. So

$$A = LU, \qquad L_{rk} = m_{rk} \;\; (r > k), \qquad L_{rr} = 1$$

There is a practical consequence worth noticing. $L$ has $n(n-1)/2$ entries below its
diagonal and $U$ has $n(n+1)/2$ on and above, which is $n^{2}$ numbers between them —
exactly as many as $A$ had. Every serious implementation therefore overwrites $A$ in
place: $U$ occupies the upper triangle, the multipliers occupy the lower one, and the
unit diagonal of $L$ is never stored because it is always the same. The factorisation is
free in memory as well as in arithmetic.

The one thing that is *not* free is the bookkeeping when a row is interchanged. The
multipliers already stored belong to specific rows, so they travel with those rows —
which is why the lab's `lu_decompose` swaps `l`, `u` and `perm` together on every
interchange, and why filling the diagonal of `l` with ones is left until the very end.
''',
                },
                {
                    "title": "What one more right-hand side costs",
                    "minutes": 14,
                    "vars": ["n", "m"],
                    "brief": r'''
"Factor once, solve many times" is only worth saying if the second thing is much cheaper
than the first. Count the operations and find out how much cheaper, and where the
crossover sits.

Count a multiply-and-subtract as one operation, and a division as one operation.
Everything below is a leading-order count in $n$ — the point is which power of $n$ each
stage costs, not the constant in front of the $n^{2}$ term.

Write $n$ for the size of the matrix and $m$ for the number of right-hand sides.
''',
                    "steps": [
                        {
                            "prompt": "Forward substitution on $Ly = c$: row $i$ needs $i-1$ multiply-subtracts and no division, because $L$ has ones on its diagonal. Add that over $i = 1$ to $n$.",
                            "answer": r"\frac{n(n-1)}{2}",
                            "hint": r"You are adding $0 + 1 + 2 + \cdots + (n-1)$.",
                        },
                        {
                            "prompt": "Back substitution on $Ux = y$: row $i$ needs $n-i$ multiply-subtracts and one division. Give the total for the whole pass.",
                            "answer": r"\frac{n(n+1)}{2}",
                            "hint": r"The multiply-subtracts add to the same triangular number as before. Then add one division per row.",
                            "deconstruct": [
                                r"$\sum_{i=1}^{n}(n-i) = (n-1) + (n-2) + \cdots + 0 = \dfrac{n(n-1)}{2}$.",
                                r"There are $n$ divisions, one per row.",
                                r"$\dfrac{n(n-1)}{2} + n = \dfrac{n^{2} - n + 2n}{2} = \dfrac{n(n+1)}{2}$.",
                            ],
                        },
                        {
                            "prompt": "Add the two passes. What does one solve cost, once the factors exist?",
                            "answer": r"n^{2}",
                            "hint": r"$\dfrac{n(n-1)}{2} + \dfrac{n(n+1)}{2}$ — put them over the common denominator and the linear terms cancel.",
                        },
                        {
                            "prompt": "The factorisation: clearing column $k$ costs $(n-k)^{2}$ multiply-subtracts, and summing over $k = 1$ to $n-1$ gives $(n-1)n(2n-1)/6$. Keep only the leading term in $n$.",
                            "answer": r"\frac{n^{3}}{3}",
                            "hint": r"Expand $(n-1)n(2n-1)$: the highest power is $2n^{3}$, over $6$.",
                        },
                        {
                            "prompt": "Now the whole job. What does it cost to factorise once and then solve $m$ right-hand sides, to leading order?",
                            "answer": r"\frac{n^{3}}{3} + m n^{2}",
                            "hint": r"One factorisation, then $m$ copies of the cost you found for a single solve.",
                        },
                        {
                            "prompt": "And the alternative: running a fresh elimination from scratch for each of the $m$ right-hand sides. To leading order, what does that cost?",
                            "answer": r"\frac{m n^{3}}{3}",
                            "hint": r"Each of the $m$ runs pays the full factorisation cost again; the $n^{2}$ of carrying the right-hand side along is a lower order and drops out.",
                        },
                        {
                            "prompt": "Divide the second by the first and let $m$ grow without bound. What does the saving tend to?",
                            "answer": r"\frac{n}{3}",
                            "hint": r"Divide the top and the bottom by $m$. The bottom becomes $n^{3}/(3m) + n^{2}$, whose first term vanishes as $m$ grows.",
                            "deconstruct": [
                                r"The ratio is $\dfrac{m n^{3}/3}{n^{3}/3 + m n^{2}}$.",
                                r"Divide the numerator and the denominator by $m$: $\dfrac{n^{3}/3}{n^{3}/(3m) + n^{2}}$.",
                                r"As $m \to \infty$ the term $n^{3}/(3m)$ goes to $0$, leaving $\dfrac{n^{3}/3}{n^{2}} = \dfrac{n}{3}$.",
                            ],
                        },
                    ],
                    "closing": r'''
So the ceiling on the saving is $n/3$, and it is reached once $m$ is large. The
crossover is at $m = n/3$: that is the number of right-hand sides whose solves cost the
same as one factorisation, so at $m = n/3$ the LU route costs two eliminations and the
naive route costs $n/3$ of them.

At $n = 300$, one factorisation buys $100$ solves. At $n = 3000$, it buys $1000$. The
saving grows with the problem, which is the opposite of how most algorithmic tricks
behave and the reason this one is not optional at scale.

Two cautions on the count.

It is asymptotic. At $n = 3$ the factorisation costs $5$ multiply-subtracts and $3$
divisions while a solve costs $9$ operations — the solve is *more* expensive, and every
statement above is false. The $n^{3}$ term does not dominate until $n$ is comfortably
into the tens.

And it counts arithmetic, not time. On real hardware the factorisation moves $n^{2}$
numbers through cache while doing $n^{3}/3$ operations on them, so it is compute-bound
and runs near peak speed; a triangular solve does $n^{2}$ operations on $n^{2}$ numbers
and is entirely limited by memory bandwidth. The measured ratio is therefore worse than
$n/3$, often by a factor of several. The conclusion survives anyway, because a factor of
several is not a factor of $n/3$.
''',
                },
                {
                    "title": "The determinant, and the sign nobody remembers",
                    "minutes": 11,
                    "vars": ["s", "u_11", "u_22", "u_33", "d"],
                    "brief": r'''
A determinant computed from the definition costs $n!$ terms. Computed from a
factorisation it costs one multiplication per row, on top of an elimination you were
going to run anyway. Everything needed is already sitting in $PA = LU$; the only work is
taking determinants of both sides and not losing the sign.

Take $A$ to be $3\times3$, factored as $PA = LU$ with $L$ unit lower triangular, $U$
upper triangular with diagonal $u_{11}, u_{22}, u_{33}$, and $P$ the product of $s$ row
interchanges.
''',
                    "steps": [
                        {
                            "prompt": "$L$ is unit lower triangular. Expanding along its first row leaves one surviving term at every stage, and the surviving entries are the diagonal. What is $\\det L$?",
                            "answer": r"1",
                            "hint": r"The diagonal of a *unit* lower triangular matrix is all ones, and the determinant of a triangular matrix is the product of its diagonal.",
                        },
                        {
                            "prompt": "Same argument down the first column of $U$. What is $\\det U$?",
                            "answer": r"u_{11} u_{22} u_{33}",
                            "hint": r"Only the $(1,1)$ entry of the first column is nonzero, so one term survives and its minor is again upper triangular. Induct.",
                        },
                        {
                            "prompt": "$P$ is the identity with $s$ row interchanges applied, and each interchange negates a determinant. Starting from $\\det I = 1$, what is $\\det P$?",
                            "answer": r"(-1)^{s}",
                            "hint": r"Each swap multiplies the running value by $-1$, and there are $s$ of them.",
                        },
                        {
                            "prompt": "Take determinants of both sides of $PA = LU$ and solve for $\\det A$. Use that $(-1)^{s}$ is its own reciprocal, so dividing by it and multiplying by it are the same move.",
                            "answer": r"(-1)^{s} u_{11} u_{22} u_{33}",
                            "hint": r"$\det P \cdot \det A = \det L \cdot \det U$. Substitute the three values you have and divide.",
                            "deconstruct": [
                                r"Determinants are multiplicative: $\det(PA) = \det P \, \det A$ and $\det(LU) = \det L \, \det U$.",
                                r"That gives $(-1)^{s}\det A = 1 \cdot u_{11}u_{22}u_{33}$.",
                                r"Divide by $(-1)^{s}$. Since $(-1)^{s}(-1)^{s} = 1$, dividing by it is multiplying by it.",
                            ],
                        },
                        {
                            "prompt": "A run on a particular $3\\times3$ made two interchanges and left pivots $u_{11} = 5$, $u_{22} = -2$, $u_{33} = 1.5$. What is $\\det A$?",
                            "answer": r"-15",
                            "hint": r"$(-1)^{2} = +1$, so the sign leaves the product alone. Then multiply the three pivots.",
                        },
                        {
                            "prompt": "Someone factorises the same matrix in a different pivot order and needs three interchanges, so their $U$ is not yours. What must the product of their three pivots be?",
                            "answer": r"15",
                            "hint": r"$\det A$ is a property of $A$ and does not depend on how it was factored. With $s = 3$ the sign is $-1$, so the pivot product must have the opposite sign to the determinant.",
                            "deconstruct": [
                                r"Whatever the pivot order, $\det A = (-1)^{s}\,u_{11}u_{22}u_{33}$ must give the same number.",
                                r"So $-15 = (-1)^{3}\,u_{11}u_{22}u_{33} = -\,u_{11}u_{22}u_{33}$.",
                                r"Therefore the product of their pivots is $15$.",
                            ],
                        },
                    ],
                    "closing": r'''
The last step is the one worth keeping. $U$ is not unique — change the pivoting rule and
you get different pivots, a different $L$ and a different permutation — but
$(-1)^{s}\prod u_{ii}$ is the same number every time, because it equals something that
depends only on $A$. That is a useful check on an implementation: factor a matrix twice
with two different pivot rules and compare the determinants, not the factors.

It also explains why `lu_decompose` returns `sign` at all. The permutation itself is not
needed for the determinant; only its parity is, and parity is one float. Two interchanges
cancel exactly, so the count can be thrown away as soon as it has been reduced to
$\pm 1$.

Where this stops being useful: as a test for singularity, almost immediately. The
determinant scales like the $n$th power of the matrix. Multiply a healthy $100 \times
100$ matrix by $0.5$ and its determinant is divided by $2^{100} \approx 1.3\times10^{30}$
while the matrix is exactly as invertible as it was. A computed determinant of
$10^{-300}$ tells you nothing, and one of $0$ may only mean that the product underflowed.
The pivots are the thing to look at, and even they only answer the yes-or-no question —
which is the subject of the third reading.
''',
                },
            ],
            "numeric": [
                {
                    "title": "A determinant read off the factors",
                    "minutes": 5,
                    "brief": r'''
The first rung, and there is nothing to run: the factorisation has already been done and
handed to you. Apply the formula.

Two of the three matrices below contribute nothing at all to the answer. Work out which
before you multiply anything.
''',
                    "prompt": "What is $\\det A$?",
                    "note": "A plain number, sign included.",
                    "figure": r'''
A routine returned this factorisation of a $3\times3$ matrix $A$, having performed **one** row interchange along the way.

$$L = \begin{bmatrix} 1 & 0 & 0 \\ 0.5 & 1 & 0 \\ -0.25 & 2 & 1 \end{bmatrix} \qquad U = \begin{bmatrix} 3 & 2 & -1 \\ 0 & -4 & 5 \\ 0 & 0 & 2 \end{bmatrix}$$

$A$ itself is not given, and is not needed.
''',
                    "given": [
                        {"label": "Rule", "value": "$\\det A = (-1)^{s} u_{11}u_{22}u_{33}$"},
                        {"label": "$s$", "value": "$1$ interchange"},
                    ],
                    "aside": "$L$ is unit lower triangular, so its determinant is fixed at $1$ no matter what its entries are. The off-diagonal entries of $U$ never enter either.",
                    "answer": 24.0,
                    "tol": 0.001,
                    "unit": "",
                    "hint": "Multiply the diagonal of $U$, then apply $(-1)^{s}$ with $s = 1$.",
                    "wrong": "If you got $-24$ you multiplied the diagonal of $U$ correctly and then forgot that a single interchange flips the sign. If you got $48$ or $12$ you have multiplied in an off-diagonal entry of $L$ — no entry of $L$ can affect the answer, however large, because $\\det L = 1$ regardless.",
                    "why": r'''
$\det L = 1$, because $L$ is triangular with a diagonal of ones and the determinant of a triangular matrix is the product of its diagonal. The entries $0.5$, $-0.25$ and $2$ are irrelevant to the determinant, however large they get.
$\det U = 3 \times (-4) \times 2 = -24$, by the same rule applied to the other triangle.
$\det P = (-1)^{1} = -1$ for one interchange.
Taking determinants across $PA = LU$ gives $\det P \, \det A = \det L \, \det U$, so $-\det A = -24$ and $\det A = 24$.
It is worth seeing that the sign is not decoration. The factorisation is of $PA$, not of $A$; $PA$ genuinely has determinant $-24$, and $A$ genuinely has determinant $24$, and the two differ because one row swap was performed.
''',
                },
                {
                    "title": "One entry of L, after the rows have moved",
                    "minutes": 8,
                    "brief": r'''
Now run the algorithm yourself. Partial pivoting on this matrix asks for two
interchanges, and the second one happens *after* both first-column multipliers have
already been computed and stored.

The question is about where one of those stored multipliers ends up. That is the whole
difficulty, and it is the difficulty the lab's tests are built around.
''',
                    "prompt": "What is $l_{31}$, the entry of $L$ in row $3$, column $1$?",
                    "note": "A plain number. Rows and columns are numbered from $1$.",
                    "figure": r'''
$$A = \begin{bmatrix} 1 & 3 & 2 \\ 5 & 2 & 7 \\ 3 & 8 & 4 \end{bmatrix}$$
Factor $A$ as $PA = LU$ with partial pivoting: at each column, promote the row whose entry in that column is largest in absolute value, then eliminate below it. Store each multiplier in the position of the entry it clears.
''',
                    "given": [
                        {"label": "Convention", "value": "$L$ is unit lower triangular; $L_{rk}$ is the multiplier that cleared position $(r,k)$"},
                        {"label": "Pivot rule", "value": "largest absolute value in the column, at or below the diagonal"},
                    ],
                    "aside": "There are two interchanges. Both first-column multipliers are computed before the second one happens, so both of them are affected by it.",
                    "answer": 0.2,
                    "tol": 0.005,
                    "unit": "",
                    "hint": "Column $1$ promotes row $2$. Column $2$ then compares $2.6$ against $6.8$ and promotes again — and when rows swap, the multipliers already sitting in those rows swap with them.",
                    "wrong": "If you got $0.6$ you computed the multipliers correctly and then left them in place through the second interchange; that is the single commonest bug in an LU implementation. If you got $3$ or $5$ you inverted a multiplier — it is (entry to clear) over (pivot), not the other way up.",
                    "why": r'''
Column $1$ holds $1$, $5$, $3$; the largest in absolute value is $5$ in row $2$, so rows $1$ and $2$ are interchanged. The working matrix is now $(5,2,7)$, $(1,3,2)$, $(3,8,4)$.
$m_{21} = 1/5 = 0.2$ turns $(1,3,2)$ into $(0,\; 3 - 0.4,\; 2 - 1.4) = (0,\; 2.6,\; 0.6)$.
$m_{31} = 3/5 = 0.6$ turns $(3,8,4)$ into $(0,\; 8 - 1.2,\; 4 - 4.2) = (0,\; 6.8,\; -0.2)$.
Column $2$, below the pivot row, holds $2.6$ and $6.8$. The larger is $6.8$, so rows $2$ and $3$ are interchanged — and the multipliers travel with their rows. The multiplier $0.6$ belonged to the row that has moved up into slot $2$, and the multiplier $0.2$ belonged to the row that has moved down into slot $3$. So $l_{21} = 0.6$ and $l_{31} = 0.2$.
The rest of the run: $m_{32} = 2.6/6.8 = 13/34$, and the last pivot is $0.6 - (13/34)(-0.2) = 0.6 + 2.6/34 = 23/34$. The factors are
$$L = \begin{bmatrix} 1 & 0 & 0 \\ 0.6 & 1 & 0 \\ 0.2 & 13/34 & 1 \end{bmatrix} \qquad U = \begin{bmatrix} 5 & 2 & 7 \\ 0 & 6.8 & -0.2 \\ 0 & 0 & 23/34 \end{bmatrix}$$
with the rows of $A$ in the order $2, 3, 1$ and two interchanges. Check the determinant: $(-1)^{2} \times 5 \times 6.8 \times 23/34 = 34 \times 23/34 = 23$, and cofactors on $A$ give $1(8 - 56) - 3(20 - 21) + 2(40 - 6) = -48 + 3 + 68 = 23$.
''',
                },
                {
                    "title": "Solving from the factors, permutation and all",
                    "minutes": 9,
                    "brief": r'''
The factorisation from the previous question, now spent. The right-hand side is the
first column of the identity, so the answer you produce is the first column of
$A^{-1}$ — which is exactly what `inverse` does, one column at a time.

Everything here is triangular. There is no elimination left to do, only a forward pass
and a backward pass, and one decision about where the permutation is applied.
''',
                    "prompt": "What is $x_1$, the first entry of the solution?",
                    "note": "A number to three decimal places or better.",
                    "figure": r'''
For $A = \begin{bmatrix} 1 & 3 & 2 \\ 5 & 2 & 7 \\ 3 & 8 & 4 \end{bmatrix}$ the factorisation with partial pivoting is

$$L = \begin{bmatrix} 1 & 0 & 0 \\ 0.6 & 1 & 0 \\ 0.2 & 13/34 & 1 \end{bmatrix} \qquad U = \begin{bmatrix} 5 & 2 & 7 \\ 0 & 6.8 & -0.2 \\ 0 & 0 & 23/34 \end{bmatrix}$$

with $P$ putting the rows of $A$ in the order $2, 3, 1$. Solve $Ax = b$ for $b = (1, 0, 0)$.
''',
                    "given": [
                        {"label": "$b$", "value": "$(1,\\; 0,\\; 0)$"},
                        {"label": "Row order under $P$", "value": "$2,\\; 3,\\; 1$"},
                        {"label": "Method", "value": "$Ly = Pb$ forward, then $Ux = y$ backward"},
                    ],
                    "aside": "The permutation is applied to $b$ and to nothing else. $L$ and $U$ are already the factors of the reordered matrix.",
                    "answer": -2.0869565,
                    "tol": 0.002,
                    "unit": "",
                    "hint": "$Pb$ lists the entries of $b$ in the order $2, 3, 1$, which is $(0, 0, 1)$ — so the forward pass starts from zero and stays there until the last row.",
                    "wrong": "If you got $0.174$ you solved $Ly = b$ instead of $Ly = Pb$; the arithmetic is flawless and the answer belongs to a different system. If you got $1.478$ or $0.043$ you have reported $x_3$ or $x_2$ instead of $x_1$.",
                    "why": r'''
The permutation puts the entries of $b$ in the order $2, 3, 1$, so $Pb = (0,\; 0,\; 1)$.
Forward substitution on $L$: $y_1 = 0$; $y_2 = 0 - 0.6(0) = 0$; $y_3 = 1 - 0.2(0) - (13/34)(0) = 1$.
Back substitution on $U$: $x_3 = 1 \div (23/34) = 34/23 \approx 1.478$.
Then $x_2 = \dfrac{0 - (-0.2)(34/23)}{6.8} = \dfrac{6.8/23}{6.8} = \dfrac{1}{23} \approx 0.043$.
Then $x_1 = \dfrac{0 - 2(1/23) - 7(34/23)}{5} = \dfrac{(-2 - 238)/23}{5} = \dfrac{-240/23}{5} = -\dfrac{48}{23} \approx -2.087$.
Substituting back into the original $A$: row $1$ gives $-48/23 + 3/23 + 68/23 = 23/23 = 1$; row $2$ gives $(-240 + 2 + 238)/23 = 0$; row $3$ gives $(-144 + 8 + 136)/23 = 0$. So $Ax = (1,0,0)$, as required.
Because $b$ was the first column of $I$, the vector $(-48/23,\; 1/23,\; 34/23)$ is the first column of $A^{-1}$. Cofactors along the first row of $A$ are $-48$, $1$ and $34$, and $\det A = 23$, which is the same thing.
''',
                },
                {
                    "title": "The price of an inverse you did not need",
                    "minutes": 10,
                    "brief": r'''
The last rung: the number you need is not in the question. You are given one timing and
have to derive the cost ratio before anything can be multiplied.

Nothing here requires a matrix. It requires knowing what a factorisation costs, what a
solve costs, and how many solves an inverse is.
''',
                    "prompt": "How long does forming the full inverse take, in total?",
                    "note": "A time in seconds, to two decimal places.",
                    "figure": r'''
Factorising a dense $1000 \times 1000$ matrix as $PA = LU$ takes $1.20$ seconds on a particular machine.

On the same machine, with the same code, the inverse is formed the way the lab forms it: **one** factorisation, followed by **one solve against each column of the identity**. Estimate the total wall-clock time, counting only arithmetic and using the leading-order operation counts.
''',
                    "given": [
                        {"label": "Factorisation", "value": "$n^{3}/3$ operations, measured at $1.20$ s"},
                        {"label": "One solve", "value": "$n^{2}$ operations"},
                        {"label": "$n$", "value": "$1000$"},
                    ],
                    "aside": "Work in units of factorisations rather than in seconds. How many factorisations' worth of arithmetic is $n$ solves?",
                    "answer": 4.8,
                    "tol": 0.05,
                    "unit": "s",
                    "hint": "One solve is $n^{2}$, so $n$ solves are $n^{3}$ — and the factorisation was $n^{3}/3$.",
                    "wrong": "If you got $1.20$ you treated the solves as free; they are not, they are three times the factorisation. If you got $2.40$ you counted the solves as costing one factorisation rather than three. If you got about $1200$ you charged a full factorisation for each of the $1000$ solves, which is what the naive routine does and what LU exists to avoid.",
                    "why": r'''
One triangular solve costs $n^{2}$ operations: $n(n-1)/2$ in the forward pass and $n(n+1)/2$ in the backward pass.
The inverse needs $n$ of them, one per column of the identity, so the solves alone cost $n \times n^{2} = n^{3}$ operations.
The factorisation costs $n^{3}/3$ operations and takes $1.20$ s, so one second buys $n^{3}/3.6$ operations. The solves are $n^{3}$, which is exactly $3$ times $n^{3}/3$, hence $3 \times 1.20 = 3.60$ s.
Total: $1.20 + 3.60 = 4.80$ s. In operation counts that is $n^{3}/3 + n^{3} = 4n^{3}/3$, four times the cost of the factorisation on its own.
The moral is in the comparison, not the number. Having spent $4.80$ s on $A^{-1}$, computing $A^{-1}b$ for a right-hand side costs a matrix-vector product, $n^{2}$ operations — precisely the same as the two triangular passes would have cost using $L$ and $U$ directly. The inverse charged four times as much and then charged the same rate afterwards, so there is no number of right-hand sides that makes it pay.
''',
                },
            ],
            "blanks": {
                "title": "Two triangular passes, every line of them",
                "minutes": 10,
                "caption": "forward substitution on L, then back substitution on U, with the permutation applied to b",
                "lang": "text",
                "brief": r'''
The factorisation below already exists — this is the cheap half, the part you are
allowed to do again and again for a new right-hand side without touching $A$.

Two things decide whether it comes out right. The permutation goes on $b$ and on nothing
else, and the signs in $L$ are as likely to be negative as positive, so every
subtraction has to be read rather than skimmed.
''',
                "listing": """solve A x = b, given a factorisation that already exists

                 [  2   4  -2 ]                 [  -6 ]
       A     =   [  4   9  -3 ]        b    =   [ -10 ]
                 [ -2  -3   7 ]                 [  20 ]

  partial pivoting put the rows of A in the order 2, 3, 1
  and produced, after two interchanges,

                 [  1     0     0 ]             [  4   9    -3   ]
       L     =   [ -0.5   1     0 ]     U   =   [  0   1.5   5.5 ]
                 [  0.5  -1/3   1 ]             [  0   0     4/3 ]

  step 0: apply the permutation, to b and to nothing else.
          the rows came out in the order 2, 3, 1, so P b lists
          the entries of b in that same order.

          P b  =  [ ___ ,   20 ,   -6 ]

  step 1: forward substitution on  L y = P b.
          no divisions anywhere: the diagonal of L is all ones.

          y1  =  -10
          y2  =  20 - (-0.5)*(-10)                =  ___
          y3  =  -6 - 0.5*(-10) - (-1/3)*(15)     =  ___

  step 2: back substitution on  U x = y.
          one division per row, by the pivot on the diagonal.

          x3  =  4 / (4/3)                        =  ___
          x2  =  (15 - 5.5*3) / 1.5               =  ___
          x1  =  (-10 - 9*(-1) - (-3)*3) / 4      =  ___

  check:  substitute back into the original A, not into L or U

          row 1:   2*2  +  4*(-1)   +  (-2)*3  =   -6
          row 2:   4*2  +  9*(-1)   +  (-3)*3  =  -10
          row 3:  -2*2  + (-3)*(-1) +   7*3    =   20
""",
                "blanks": [
                    {
                        "prompt": "P lists the entries of b in the order 2, 3, 1. What comes first?",
                        "hole": "?",
                        "opts": ["-10", "-6", "20", "whichever is largest, 20"],
                        "a": 0,
                        "why": r"The ordering is $2, 3, 1$, so the first entry of $Pb$ is $b_2 = -10$. "
                               r"Starting from $b_1 = -6$ is solving $Ly = b$ rather than $Ly = Pb$, which "
                               r"pairs each triangular equation with the wrong right-hand-side entry and "
                               r"returns a confident wrong vector with no error raised. Nothing about $Pb$ "
                               r"depends on the sizes of the entries — the ordering came from the pivoting, "
                               r"which looked at $A$ and never at $b$.",
                    },
                    {
                        "prompt": "y2 = 20 - (-0.5)*(-10). What is it?",
                        "hole": "?",
                        "opts": ["15", "25", "5", "20"],
                        "a": 0,
                        "why": r"$(-0.5)(-10) = +5$, so $y_2 = 20 - 5 = 15$. Reading the product as $-5$ and "
                               r"then subtracting gives $25$, and it is the commonest slip in a hand-run "
                               r"forward pass, because two minus signs meet — one belonging to the entry of "
                               r"$L$ and one to the entry of $Pb$ — and the subtraction in the formula is a "
                               r"third. The value $20$ would follow from treating the entry of $L$ as zero.",
                    },
                    {
                        "prompt": "y3 = -6 - 0.5*(-10) - (-1/3)*(15). What is it?",
                        "hole": "?",
                        "opts": ["4", "-6", "-16", "-1"],
                        "a": 0,
                        "why": r"$-6 - (-5) - (-5) = -6 + 5 + 5 = 4$. Both products are negative and both are "
                               r"being subtracted, so both raise the running total. Getting $-16$ means both "
                               r"signs were dropped and the products were subtracted as positives; getting "
                               r"$-6$ means the two corrections were taken as cancelling, which they do not — "
                               r"they happen to be equal in size but they have the same sign.",
                    },
                    {
                        "prompt": "x3 = 4 divided by the last pivot, 4/3. What is it?",
                        "hole": "?",
                        "opts": ["3", "5.333", "1", "0.75"],
                        "a": 0,
                        "why": r"$4 \div \frac{4}{3} = 4 \times \frac{3}{4} = 3$. Dividing by a fraction less "
                               r"than $1$ makes the result larger than $4$ only if that fraction is less than "
                               r"$1$ — here $4/3 > 1$, so the result shrinks. Multiplying by $4/3$ instead of "
                               r"dividing gives $5.333$; taking the pivot as $4$ gives $1$.",
                    },
                    {
                        "prompt": "x2 = (15 - 5.5*3) / 1.5. What is it?",
                        "hole": "?",
                        "opts": ["-1", "-1.5", "21", "1"],
                        "a": 0,
                        "why": r"$15 - 16.5 = -1.5$, and $-1.5 \div 1.5 = -1$. Stopping at $-1.5$ forgets the "
                               r"division by the pivot, which is the step that distinguishes back substitution "
                               r"from the forward pass — $U$ has no unit diagonal to make the division "
                               r"unnecessary. Adding rather than subtracting the known term gives $21$.",
                    },
                    {
                        "prompt": "x1 = (-10 - 9*(-1) - (-3)*3) / 4. What is it?",
                        "hole": "?",
                        "opts": ["2", "8", "-2.5", "-7"],
                        "a": 0,
                        "why": r"$-10 + 9 + 9 = 8$, and $8 \div 4 = 2$. The pivot here is $u_{11} = 4$, not the "
                               r"$1$ from the diagonal of $L$; forgetting to divide leaves $8$. Getting $-7$ "
                               r"means both known terms were subtracted as positives. Substituting "
                               r"$x = (2, -1, 3)$ into the original $A$ reproduces $b = (-6, -10, 20)$ exactly, "
                               r"which is the only check worth trusting.",
                    },
                ],
            },
            "quiz": {
                "title": "Factors, permutations and what each one costs",
                "minutes": 10,
                "questions": [
                    {
                        "q": "Where do the entries below the diagonal of $L$ come from?",
                        "opts": [
                            "they are the multipliers used in the elimination, each in the position of the entry it cleared",
                            "they are the negatives of those multipliers, because the operation performed was a subtraction",
                            "they are the reciprocals of the pivots",
                            "they are the entries of $A$ below the diagonal, copied across unchanged",
                        ],
                        "a": 0,
                        "why": r"Each elimination step is $E = I - m\,e_r e_k^{\mathsf{T}}$, and its inverse is "
                               r"$I + m\,e_r e_k^{\mathsf{T}}$ — the same matrix with the sign flipped, because "
                               r"$e_k^{\mathsf{T}}e_r = 0$ kills the quadratic term. $L$ is built from the "
                               r"*inverses*, so it carries $+m$. Reasoning that $L$ records what was done, and "
                               r"what was done was a subtraction, is exactly the trap: $L$ records how to undo "
                               r"what was done. Nothing is computed to build $L$ — the multipliers already exist "
                               r"and would otherwise be discarded.",
                    },
                    {
                        "q": "$A$ is a square matrix and $\\det A \\neq 0$. Which factorisation is guaranteed to exist?",
                        "opts": [
                            "$PA = LU$ for some permutation matrix $P$",
                            "$A = LU$ with no permutation, since $A$ is invertible",
                            "$A = LU$, provided no entry of $A$ is zero",
                            "neither, unless $A$ is symmetric",
                        ],
                        "a": 0,
                        "why": r"For a nonsingular $A$, the factorisation $A = LU$ exists exactly when every "
                               r"leading principal submatrix of $A$ is nonsingular — and invertibility of $A$ "
                               r"says nothing about those blocks. The "
                               r"matrix $\begin{bmatrix} 1 & 2 & 3 \\ 2 & 4 & 1 \\ 3 & 5 & 2 \end{bmatrix}$ has "
                               r"determinant $-5$ and not a single zero entry, yet its leading $2\times2$ block "
                               r"is singular, the second pivot vanishes, and no $LU$ factorisation exists. With "
                               r"a permutation it always does: at every column either some nonzero entry can be "
                               r"promoted into the pivot position, or the column below is already clear.",
                    },
                    {
                        "q": "$A$ is $600\\times600$ and $200$ right-hand sides arrive one after another. Roughly how much cheaper is factoring once than re-eliminating each time?",
                        "opts": [
                            "about $100$ times cheaper",
                            "about twice as cheap",
                            "about $200$ times cheaper",
                            "not at all — the same arithmetic happens either way",
                        ],
                        "a": 0,
                        "why": r"A factorisation is $n^{3}/3 = 7.2\times10^{7}$ operations and a solve is "
                               r"$n^{2} = 3.6\times10^{5}$. Two hundred solves therefore cost $7.2\times10^{7}$ — "
                               r"exactly one factorisation — so the LU route costs two factorisations while "
                               r"re-eliminating costs two hundred. That is a factor of $100$. Answering $200$ "
                               r"assumes the solves are free, which they are not at this $m$: the crossover "
                               r"$m = n/3$ is precisely $200$ here, so the solves cost as much as the "
                               r"factorisation. The saving does approach $n/3 = 200$, but only as $m$ grows well "
                               r"past $200$.",
                    },
                    {
                        "q": "In $PA = LU$, where is the permutation applied when solving $Ax = b$?",
                        "opts": [
                            "to the right-hand side, before the forward pass",
                            "to the rows of $L$ and $U$, once they have been computed",
                            "to the solution $x$, after the back pass",
                            "nowhere — $P$ is bookkeeping and can be dropped",
                        ],
                        "a": 0,
                        "why": r"$PA = LU$ gives $LUx = Pb$, so the reordering belongs to $b$. $L$ and $U$ are "
                               r"already the factors of the permuted matrix, so permuting them applies the "
                               r"reordering a second time; permuting $x$ reorders the unknowns, which is a "
                               r"different and equally wrong operation. Dropping $P$ pairs each triangular "
                               r"equation with the wrong entry of $b$ — no division by zero, no exception, just "
                               r"a wrong vector, which is why the residual $Ax - b$ has to be computed against "
                               r"the original $A$.",
                    },
                    {
                        "q": "A factorisation of a $4\\times4$ matrix made three interchanges and produced pivots $2$, $-1$, $5$ and $3$. What is $\\det A$?",
                        "opts": ["$30$", "$-30$", "$-1$", "$9$"],
                        "a": 0,
                        "why": r"$\det A = (-1)^{s}\,u_{11}u_{22}u_{33}u_{44}$. The pivot product is "
                               r"$2 \times (-1) \times 5 \times 3 = -30$, and $(-1)^{3} = -1$, so "
                               r"$\det A = 30$. Reporting $-30$ is the pivot product of $PA$, which is a "
                               r"genuinely different matrix from $A$ — three row swaps apart. Only the parity "
                               r"of the swap count matters, so two interchanges would have left the answer at "
                               r"$-30$ and four would too.",
                    },
                    {
                        "q": "Partway through a factorisation the largest available pivot in a column is $4\\times10^{-17}$, while the entries of $A$ are of order $1$. What is the best reading?",
                        "opts": [
                            "$A$ is numerically singular: whatever its exact rank, nothing computed from this factorisation will carry meaningful digits",
                            "$A$ is exactly singular, so $Ax = b$ has no solution",
                            "the factorisation is sound, because the pivot is not exactly zero",
                            "$A$ is singular only if every entry below the pivot is exactly zero",
                        ],
                        "a": 0,
                        "why": r"A quantity of $4\times10^{-17}$ against entries of order $1$ is what rounding "
                               r"leaves behind when the exact value is $0$, so the computed numbers cannot "
                               r"decide whether the exact matrix is singular. What they can decide is that "
                               r"dividing by that pivot multiplies every earlier rounding error by $10^{17}$, "
                               r"which destroys the answer either way. Note also that a singular system does "
                               r"not automatically have no solution — if $b$ lies in the column space it has "
                               r"infinitely many — so exact singularity would not justify that conclusion "
                               r"either.",
                    },
                    {
                        "q": "You need $x = A^{-1}b$ for a single $b$, with $A$ dense and $n$ large. What should you do?",
                        "opts": [
                            "factor once and run the two triangular passes, never forming $A^{-1}$",
                            "form $A^{-1}$ and multiply, since a matrix-vector product is cheaper than a triangular solve",
                            "form $A^{-1}$ by cofactors, which avoids the rounding that elimination introduces",
                            "either — forming $A^{-1}$ reuses the same factorisation, so it costs nothing extra",
                        ],
                        "a": 0,
                        "why": r"Forming $A^{-1}$ is $n$ solves at $n^{2}$ each, so $n^{3}$ operations on top of "
                               r"the $n^{3}/3$ for the factorisation: $4n^{3}/3$, four times the cost of just "
                               r"factoring. The reuse is real — each of those solves is cheap — but there are "
                               r"$n$ of them. And $A^{-1}b$ is then $n^{2}$, precisely what the forward and back "
                               r"passes would have cost, so nothing is recovered afterwards. Cofactors are "
                               r"worse still at $n!$ terms, and they do not avoid rounding: every entry is a "
                               r"sum of products of floating-point numbers.",
                    },
                ],
            },
            "lab": {
                "title": "PA = LU, and what the factors buy you",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
**`lu_decompose(a, tol=1e-12)`** — returns `(l, u, perm, sign)` for a square
`a`, where

- `l` is unit lower triangular (ones on the diagonal, multipliers below),
- `u` is upper triangular,
- `perm` is a list of the original row indices in their new order, so
  `[a[perm[i]] for i in range(n)] == l @ u`,
- `sign` is `1.0` or `-1.0`, the determinant of the permutation.

Choose each pivot by partial pivoting. When the best available pivot is no
bigger than `tol` the matrix is singular — raise `ValueError`. A non-square
argument also raises.

```text
lu_decompose([[4, 3, 2], [1, 5, 7], [2, 2, 9]])
  l -> [[1, 0, 0], [0.25, 1, 0], [0.5, 0.11764705882352941, 1]]
  u -> [[4, 3, 2], [0, 4.25, 6.5], [0, 0, 7.235294117647059]]
  perm -> [0, 1, 2],  sign -> 1.0
```

**`det_from_lu(u, sign)`** — `sign` times the product of the diagonal of `u`.

**`lu_solve(l, u, perm, b)`** — forward substitution for `y` (remembering that
row `i` of the permuted system uses `b[perm[i]]`), then back substitution for
`x`. A right-hand side of the wrong length raises `ValueError`.

**`inverse(a)`** — factor once, then solve against each column of the identity
and assemble the columns into the result.

```text
inverse([[4, 7], [2, 6]])  ->  [[0.6, -0.7], [-0.2, 0.4]]
```
''',
                "files": [{"name": "main.py", "content": r'''
def square_size(a):
    """n after checking a is a non-empty square matrix."""
    # your code here


def lu_decompose(a, tol=1e-12):
    """(l, u, perm, sign) with PA = LU and partial pivoting."""
    # your code here


def det_from_lu(u, sign):
    """Determinant read off an LU factorisation."""
    # your code here


def lu_solve(l, u, perm, b):
    """Solve A x = b from the factors of A."""
    # your code here


def inverse(a):
    """The inverse of a, one solve per column of the identity."""
    # your code here


print(lu_decompose([[4, 3, 2], [1, 5, 7], [2, 2, 9]]))
print(inverse([[4, 7], [2, 6]]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def square_size(a):
    """n after checking a is a non-empty square matrix."""
    if not isinstance(a, list) or not a:
        raise ValueError("matrix must be a non-empty list of rows")
    n = len(a)
    for row in a:
        if not isinstance(row, list) or len(row) != n:
            raise ValueError("matrix must be square")
    return n


def lu_decompose(a, tol=1e-12):
    """(l, u, perm, sign) with PA = LU and partial pivoting."""
    n = square_size(a)
    u = [[float(x) for x in row] for row in a]
    l = [[0.0] * n for _ in range(n)]
    perm = list(range(n))
    sign = 1.0
    for col in range(n):
        best = col
        for r in range(col + 1, n):
            if abs(u[r][col]) > abs(u[best][col]):
                best = r
        if abs(u[best][col]) <= tol:
            raise ValueError("matrix is singular")
        if best != col:
            u[col], u[best] = u[best], u[col]
            l[col], l[best] = l[best], l[col]
            perm[col], perm[best] = perm[best], perm[col]
            sign = -sign
        for r in range(col + 1, n):
            factor = u[r][col] / u[col][col]
            l[r][col] = factor
            for c in range(col, n):
                u[r][c] -= factor * u[col][c]
            u[r][col] = 0.0
    for i in range(n):
        l[i][i] = 1.0
    return (l, u, perm, sign)


def det_from_lu(u, sign):
    """Determinant read off an LU factorisation."""
    value = float(sign)
    for i in range(len(u)):
        value *= u[i][i]
    return value


def lu_solve(l, u, perm, b):
    """Solve A x = b from the factors of A."""
    n = len(l)
    if len(b) != n:
        raise ValueError("b must have one entry per row")
    y = [0.0] * n
    for i in range(n):
        total = float(b[perm[i]])
        for j in range(i):
            total -= l[i][j] * y[j]
        y[i] = total
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        total = y[i]
        for j in range(i + 1, n):
            total -= u[i][j] * x[j]
        x[i] = total / u[i][i]
    return x


def inverse(a):
    """The inverse of a, one solve per column of the identity."""
    n = square_size(a)
    l, u, perm, _ = lu_decompose(a)
    columns = []
    for j in range(n):
        unit = [1.0 if i == j else 0.0 for i in range(n)]
        columns.append(lu_solve(l, u, perm, unit))
    return [[columns[j][i] for j in range(n)] for i in range(n)]


print(lu_decompose([[4, 3, 2], [1, 5, 7], [2, 2, 9]]))
print(inverse([[4, 7], [2, 6]]))
'''}],
                "hints": [
                    "Swap rows of `l`, of `u` and of `perm` together, and flip `sign` each time. Filling the diagonal of `l` with ones at the very end keeps the swap logic simple.",
                    "The multiplier `factor = u[r][col] / u[col][col]` is stored in `l[r][col]` and then used to eliminate — nothing is thrown away, which is the whole point of LU.",
                    "In `lu_solve`, the permutation is applied to the right-hand side, not to the factors: row `i` starts from `b[perm[i]]`.",
                    "`inverse` calls `lu_decompose` exactly once and `lu_solve` n times. The solve for column j returns a *column* of the inverse, so transpose the collected list at the end.",
                ],
                "tests": [
                    {"name": "The factors have the right shape", "code": r'''
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_l, _u, _perm, _sign = lu_decompose(_a)
assert sorted(_perm) == [0, 1, 2], f"perm should be a permutation of 0..2, got {_perm!r}"
assert _sign in (1.0, -1.0), f"sign was {_sign!r}, expected 1.0 or -1.0"
for _i in range(3):
    assert abs(_l[_i][_i] - 1.0) < 1e-12, f"l[{_i}][{_i}] is {_l[_i][_i]!r}, expected 1.0 (unit diagonal)"
    for _j in range(_i + 1, 3):
        assert abs(_l[_i][_j]) < 1e-12, f"l[{_i}][{_j}] is {_l[_i][_j]!r}; l must be lower triangular"
        assert abs(_u[_j][_i]) < 1e-12, f"u[{_j}][{_i}] is {_u[_j][_i]!r}; u must be upper triangular"
assert _a == [[4, 3, 2], [1, 5, 7], [2, 2, 9]], "lu_decompose must not mutate its argument"
'''},
                    {"name": "L times U reproduces the permuted matrix", "code": r'''
def _mm(x, y):
    return [[sum(x[i][k] * y[k][j] for k in range(len(y))) for j in range(len(y[0]))]
            for i in range(len(x))]
for _a in [[[4, 3, 2], [1, 5, 7], [2, 2, 9]],
           [[0, 1], [1, 0]],
           [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
           [[2, 1, 1, 0], [4, 3, 3, 1], [8, 7, 9, 5], [6, 7, 9, 8]]]:
    _l, _u, _perm, _sign = lu_decompose(_a)
    _lu = _mm(_l, _u)
    for _i in range(len(_a)):
        for _j in range(len(_a)):
            _want = float(_a[_perm[_i]][_j])
            assert abs(_lu[_i][_j] - _want) < 1e-9, \
                f"(LU)[{_i}][{_j}] is {_lu[_i][_j]!r}, but row perm[{_i}] of A has {_want!r} there"
'''},
                    {"name": "Determinant from the factors", "code": r'''
for _name, _a, _want in [("3x3", [[4, 3, 2], [1, 5, 7], [2, 2, 9]], 123.0),
                         ("2x2", [[1, 2], [3, 4]], -2.0),
                         ("swap", [[0, 1], [1, 0]], -1.0),
                         ("identity", [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1.0),
                         ("1x1", [[7]], 7.0),
                         ("2x2 det 10", [[4, 7], [2, 6]], 10.0)]:
    _l, _u, _perm, _sign = lu_decompose(_a)
    _got = det_from_lu(_u, _sign)
    assert abs(_got - _want) < 1e-9, f"det of the {_name} case gave {_got!r}, expected {_want}"
'''},
                    {"name": "Singular and non-square input", "code": r'''
for _bad in [[[1, 2], [2, 4]], [[0, 0], [0, 0]], [[1, 2, 3], [4, 5, 6], [7, 8, 9]]]:
    try:
        lu_decompose(_bad)
        assert False, f"lu_decompose({_bad!r}) should raise ValueError — it is singular"
    except ValueError:
        pass
for _bad in [[[1, 2, 3], [4, 5, 6]], [], [[1, 2], [3]]]:
    try:
        lu_decompose(_bad)
        assert False, f"lu_decompose({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Solving from the factors", "code": r'''
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_l, _u, _perm, _sign = lu_decompose(_a)
_x = lu_solve(_l, _u, _perm, [1, 2, 3])
for _row, _rhs in zip(_a, [1, 2, 3]):
    _lhs = sum(_c * _v for _c, _v in zip(_row, _x))
    assert abs(_lhs - _rhs) < 1e-9, f"Solution does not satisfy the system: {_lhs!r} vs {_rhs}"
assert abs(_x[0] - 6.0 / 41.0) < 1e-12, f"x[0] is {_x[0]!r}, expected 6/41"
_l2, _u2, _p2, _s2 = lu_decompose([[0, 1], [1, 0]])
_x = lu_solve(_l2, _u2, _p2, [1, 2])
assert abs(_x[0] - 2.0) < 1e-12 and abs(_x[1] - 1.0) < 1e-12, \
    f"Got {_x!r}, expected [2.0, 1.0] — the permutation must be applied to b"
try:
    lu_solve(_l, _u, _perm, [1, 2])
    assert False, "A right-hand side of the wrong length should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The factors are reusable", "code": r'''
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_l, _u, _perm, _sign = lu_decompose(_a)
for _b in ([1, 0, 0], [0, 1, 0], [1, 2, 3], [-4, 7, 0.5]):
    _x = lu_solve(_l, _u, _perm, _b)
    for _row, _rhs in zip(_a, _b):
        _lhs = sum(_c * _v for _c, _v in zip(_row, _x))
        assert abs(_lhs - _rhs) < 1e-9, \
            f"Re-solving with b={_b!r} failed: {_lhs!r} vs {_rhs} — the factors must survive a solve"
'''},
                    {"name": "The inverse", "code": r'''
_inv = inverse([[4, 7], [2, 6]])
_want = [[0.6, -0.7], [-0.2, 0.4]]
for _i in range(2):
    for _j in range(2):
        assert abs(_inv[_i][_j] - _want[_i][_j]) < 1e-12, \
            f"inverse[{_i}][{_j}] is {_inv[_i][_j]!r}, expected {_want[_i][_j]!r}"
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_inv = inverse(_a)
_prod = [[sum(_a[i][k] * _inv[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
for _i in range(3):
    for _j in range(3):
        _target = 1.0 if _i == _j else 0.0
        assert abs(_prod[_i][_j] - _target) < 1e-9, \
            f"(A A^-1)[{_i}][{_j}] is {_prod[_i][_j]!r}, expected {_target}"
assert abs(inverse([[4]])[0][0] - 0.25) < 1e-12, f"inverse([[4]]) gave {inverse([[4]])!r}"
try:
    inverse([[1, 2], [2, 4]])
    assert False, "inverse of a singular matrix should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Vector spaces, span and the complete solution of Ax = b",
            "summary": "What elimination was really telling you: which right-hand sides are reachable, and how many solutions each one has.",
            "concepts": [
                "A subspace is closed under addition and scaling, so every subspace contains the zero vector",
                "The column space is the set of reachable right-hand sides: Ax = b is solvable exactly when b is a combination of the columns of A",
                "The null space collects every x with Ax = 0; it is a subspace of the input space, and it is trivial exactly when the columns are independent",
                "Reduced row echelon form sorts the columns into pivot columns and free columns, and each free column contributes one special solution",
                "The complete solution is one particular solution plus the entire null space, so a linear system has none, exactly one, or infinitely many solutions — never exactly two",
            ],
            "quiz": {
                "title": "Reachable right-hand sides, and how many solutions",
                "minutes": 8,
                "questions": [
                    {
                        "q": "`Ax = b` has no solution at all. What does that say about `b`?",
                        "opts": [
                            "`b` lies outside the column space of `A`",
                            "`b` is the zero vector",
                            "`A` has a non-trivial null space",
                            "`A` is not square",
                        ],
                        "a": 0,
                        "why": r"""
`Ax` is a combination of the columns of `A` with the entries of `x` as weights, so
the reachable right-hand sides are exactly the column space and nothing else.
A right-hand side outside it cannot be hit, however clever the solver.
The zero right-hand side is always solvable by `x = 0`. A non-trivial null space
changes *how many* solutions a reachable `b` has, not whether it is reachable at
all. Squareness is neither necessary nor sufficient: plenty of square systems are
unsolvable, and plenty of rectangular ones are fine.
""",
                    },
                    {
                        "q": "You find two different solutions `x1` and `x2` of the same system `Ax = b`. How many solutions does it have?",
                        "opts": [
                            "Exactly two",
                            "Infinitely many, because `x1 + t(x1 - x2)` solves it for every real `t`",
                            "Three, once you count `x1 - x2` as well",
                            "It depends on whether `A` is square",
                        ],
                        "a": 1,
                        "why": r"""
`A(x1 - x2) = b - b = 0`, so the difference sits in the null space — and a null
space is a subspace, so every scalar multiple of that difference is in it too.
Adding those multiples to `x1` gives a whole line of solutions. This is why the
count is only ever zero, one, or infinite: two distinct solutions immediately
manufacture infinitely many. Note that `x1 - x2` is itself a solution only when
`b = 0`, and squareness has nothing to do with it.
""",
                    },
                    {
                        "q": "Which of these sets is a subspace of R^3?",
                        "opts": [
                            "The non-negative octant, `x >= 0` and `y >= 0` and `z >= 0`",
                            "The offset plane `x + y + z = 1`",
                            "The plane `x + y + z = 0`",
                            "The set where `xyz = 0`",
                        ],
                        "a": 2,
                        "why": r"""
A subspace must be closed under addition and under scaling by any real number,
which forces it to contain the origin. The plane through the origin passes every
test: add two vectors whose coordinates sum to zero and the sum still does.
The offset plane misses the origin, so scaling by 0 escapes it. The octant is
closed under addition but not under multiplication by -1. The set where some
coordinate vanishes is the union of the three coordinate planes: it holds
`(1, 1, 0)` and `(0, 0, 1)` but not their sum `(1, 1, 1)`.
""",
                    },
                    {
                        "q": "A 3-by-5 matrix `A` has 2 pivots, and `Ax = b` is known to be consistent. What does the solution set look like?",
                        "opts": [
                            "A single vector",
                            "One particular solution plus any combination of 2 special solutions",
                            "One particular solution plus any combination of 3 special solutions",
                            "Empty, because there are more columns than rows",
                        ],
                        "a": 2,
                        "why": r"""
Five columns and two pivots leave three free columns, and each free column gives
one special solution; together they are a basis of a three-dimensional null space.
The complete solution is a particular solution plus that null space, so it is a
three-parameter family — in R^5, a translated 3-dimensional flat. The count of
special solutions is the number of *free* columns, not of pivots. It cannot be a
single vector unless there are no free columns at all, and it cannot be empty
because consistency was given.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Independence, basis, dimension and the four subspaces",
            "summary": "Counting the degrees of freedom hidden in a matrix, and the four subspaces that account for every one of them.",
            "concepts": [
                "Vectors are independent when the only combination giving zero is the trivial one — that is, when the matrix holding them has a trivial null space",
                "A basis is independent and spanning; every basis of a space has the same size, and that size is the dimension",
                "Rank counts the pivots, and it is simultaneously the dimension of the column space and of the row space",
                "Rank plus nullity equals the number of columns: every column is either a pivot or a free variable, and there is no third option",
                "The four subspaces pair off at right angles: row space against null space inside R^n, column space against left null space inside R^m",
            ],
            "quiz": {
                "title": "Counting dimensions",
                "minutes": 8,
                "questions": [
                    {
                        "q": "`A` is 4-by-7 with rank 3. What is the dimension of its null space?",
                        "opts": ["3", "7", "4", "0"],
                        "a": 2,
                        "why": r"""
Rank plus nullity equals the number of *columns*, which is 7 here, so the nullity
is `7 - 3 = 4`. Each of the four free columns supplies one special solution, and
those four vectors are a basis of the null space. The value 3 is the rank itself —
the dimension of the column space, living over in R^4. A nullity of 0 would mean
seven independent columns in a 4-dimensional space, which is impossible.
""",
                    },
                    {
                        "q": "What is always true of the row space and the column space of the same matrix?",
                        "opts": [
                            "They have equal dimension, even though they usually sit in different spaces",
                            "They contain the same vectors whenever `A` is square",
                            "The row space has dimension equal to the number of rows",
                            "The column space is always the larger of the two",
                        ],
                        "a": 0,
                        "why": r"""
Row rank equals column rank — one of the genuinely surprising facts in the
subject. Elimination leaves the row space untouched and exposes the pivots, and
the same pivot count measures both spaces. They are equal in *dimension*, not as
sets: for a 4-by-7 matrix one lives in R^7 and the other in R^4, so neither
contains the other. And the row space fills up the row count only when the rows
happen to be independent, which rank-deficient matrices are precisely the
counterexample to.
""",
                    },
                    {
                        "q": "You are handed five vectors in R^4. What can be said with no further information?",
                        "opts": [
                            "They span R^4",
                            "They are dependent",
                            "They are independent as long as none of them is zero",
                            "They form a basis of R^4",
                        ],
                        "a": 1,
                        "why": r"""
Stack them as the columns of a 4-by-5 matrix: it has at most 4 pivots, so at least
one column is free, so a non-trivial combination gives zero. Any `n + 1` vectors
in R^n are dependent, whatever they are. They may or may not span R^4 — five
copies of the same vector span a line — so they certainly need not be a basis, and
being non-zero rules nothing out, since two copies of one non-zero vector are
already dependent.
""",
                    },
                    {
                        "q": "Why is the null space of `A` orthogonal to the row space of `A`?",
                        "opts": [
                            "Because `A^T A` is symmetric",
                            "Because elimination preserves angles",
                            "Because both have dimension n/2",
                            "Because `Ax = 0` says exactly that `x` is perpendicular to every row of `A`",
                        ],
                        "a": 3,
                        "why": r"""
Entry `i` of `Ax` is the dot product of row `i` with `x`. Setting the whole
product to zero says `x` meets every row at a right angle, and therefore every
combination of the rows — which is the row space. That is the entire argument.
Their dimensions add to `n` by rank plus nullity, but they are almost never equal.
Elimination does *not* preserve angles (it is not an orthogonal operation), and
the symmetry of `A^T A` is a different fact about a different matrix.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M6
        {
            "title": "Linear transformations and change of basis",
            "summary": "The same map written in two languages, and the matrix that translates between them.",
            "concepts": [
                "A map is linear when it respects addition and scaling; its matrix is what it does to the basis vectors, recorded as columns",
                "Rotation, reflection, scaling, shear and projection are all read straight off their action on a basis",
                "Translation is not linear because it moves the origin, which is why graphics carries an extra coordinate and works with 4-by-4 matrices",
                "Changing basis conjugates the matrix: B = S^-1 A S, and similar matrices are one map seen from two seats",
                "|det A| is the factor by which areas and volumes are scaled, and the sign of det A records whether orientation survived",
            ],
            "quiz": {
                "title": "Same map, different coordinates",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What sits in the columns of the matrix of a linear map `T`?",
                        "opts": [
                            "The eigenvectors of `T`",
                            "The images of the basis vectors, `T(e1)`, `T(e2)`, ..., written in the output basis",
                            "The input basis vectors, unchanged",
                            "The rows of the inverse map",
                        ],
                        "a": 1,
                        "why": r"""
Linearity gives `T(x) = x1 T(e1) + x2 T(e2) + ...`, so knowing where the basis
vectors land determines the map everywhere; stacking those images as columns
*is* the matrix. This is the fastest way to write down a rotation or a reflection:
draw where `e1` and `e2` go and read off two columns. Eigenvectors need not even
exist over the reals, and the identity is the only map whose columns are the
input basis unchanged.
""",
                    },
                    {
                        "q": "Which map of the plane is **not** linear?",
                        "opts": [
                            "`(x, y) -> (2x, 3y)`",
                            "`(x, y) -> (y, x)`",
                            "`(x, y) -> (x + 1, y)`",
                            "`(x, y) -> (0, 0)`",
                        ],
                        "a": 2,
                        "why": r"""
A linear map must send the origin to the origin, and a translation by one unit
does not: it fails both `T(0) = 0` and `T(2x) = 2T(x)`. Scaling the axes
separately, swapping the coordinates (a reflection in the diagonal) and collapsing
everything to zero are all linear. Translation being non-linear is exactly why a
graphics pipeline stores a point as `(x, y, z, 1)` and uses one size-larger
matrix: in that extra coordinate, a translation becomes a shear, and can finally
be composed with the rest by multiplication.
""",
                    },
                    {
                        "q": "`A` and `B = S^-1 A S` are similar. What do they have in common?",
                        "opts": [
                            "Determinant, trace, rank and characteristic polynomial",
                            "Their entries, up to a permutation",
                            "Their eigenvectors, written with the same numbers",
                            "Nothing in general, since `S` may be any invertible matrix",
                        ],
                        "a": 0,
                        "why": r"""
Similar matrices are the same linear map described in two bases, so everything
intrinsic to the map survives: `det(S^-1 A S) = det A` because determinants
multiply, the trace survives because it is invariant under cyclic reordering, and
the characteristic polynomial — hence the eigenvalues — is unchanged. What does
*not* survive is coordinates: an eigenvector `v` of `A` appears as `S^-1 v` for
`B`. The entries themselves can look completely different, which is the point of
choosing a better basis in the first place.
""",
                    },
                    {
                        "q": "A 2-by-2 matrix `M` has `det M = -3`. What does `M` do to the unit square?",
                        "opts": [
                            "Shrinks its area to one third",
                            "Maps it to a parallelogram of area 3, with orientation reversed",
                            "Maps it to a parallelogram of area 3, preserving orientation",
                            "Collapses it onto a line segment",
                        ],
                        "a": 1,
                        "why": r"""
The absolute value of the determinant is the area scale factor, so the unit square
becomes a parallelogram of area 3 — it grows, not shrinks. The minus sign is the
orientation flip: a reflection is folded into the map, so a counter-clockwise
circuit of the square comes out clockwise. Collapse onto a segment is what a
determinant of exactly zero means, and that is the same condition as singularity —
the map has thrown away a dimension and cannot be undone.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M7
        {
            "title": "Orthogonality and eigenstructure",
            "summary": "Orthonormal bases, the QR factorisation, and iterating towards an eigenvector.",
            "concepts": [
                "The dot product measures both length and angle; orthogonal means dot product zero",
                "Gram-Schmidt subtracts the projection onto everything already accepted",
                "A residual that vanishes signals linear dependence, not bad luck",
                "QR: the orthonormalised columns form Q, and R[i][j] is the projection of column j onto q_i",
                "Q^T Q = I, so an orthogonal change of basis preserves lengths and cannot amplify error",
                "Power iteration converges to the dominant eigenvector at rate |lambda_2 / lambda_1|",
                "The Rayleigh quotient v^T A v is the best eigenvalue estimate for a given v",
            ],
            "lab": {
                "title": "Gram-Schmidt, QR and the power method",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
**`dot(u, v)`** and **`norm(v)`** — the usual definitions; mismatched lengths
raise `ValueError`.

**`matvec(a, v)`** — the matrix-vector product, `ValueError` on a shape
mismatch.

**`gram_schmidt(vectors, tol=1e-10)`** — orthonormalise a list of vectors, in
order. For each input vector, subtract its projection onto every basis vector
already accepted, then normalise what is left. A residual whose norm is at most
`tol` means the vector lay in the span of the earlier ones — raise `ValueError`.
An empty list also raises.

```text
gram_schmidt([[3.0, 0.0], [0.0, -2.0]])  ->  [[1.0, 0.0], [0.0, -1.0]]
gram_schmidt([[1, 2], [2, 4]])           ->  ValueError
```

**`qr(a)`** — for `a` with at least as many rows as columns and full column
rank, return `(q, r)` where `q` has the orthonormalised columns of `a` and
`r[i][j] = dot(q_i, a_j)` for `i <= j`, zero below. Because each `r[i][i]` is
the length of a residual, the diagonal of `R` comes out positive.

```text
qr([[12, -51], [6, 167], [-4, 24]])  ->  r = [[14, 21], [0, 175]]
```

**`power_method(a, tol=1e-10, max_iter=1000)`** — returns
`(eigenvalue, eigenvector, iterations)`. Start from the unit vector with every
component `1/sqrt(n)`. Each step forms `w = A v`, takes the Rayleigh quotient
`v . w` as the new eigenvalue estimate, and replaces `v` by `w / norm(w)`.
Stop once two consecutive estimates differ by at most `tol`. Return the
eigenvector scaled so its largest-magnitude component is positive. A non-square
matrix, a collapse to the zero vector, or exhausting `max_iter` all raise
`ValueError`.

```text
power_method([[4.0, 1.0], [2.0, 3.0]])  ->  (5.0, [0.7071..., 0.7071...], 2)
power_method([[3.0, 0.0], [0.0, -7.0]]) ->  (-7.0, [0.0, 1.0], ...)
```
''',
                "files": [{"name": "main.py", "content": r'''
import math


def dot(u, v):
    """Dot product of two equal-length vectors."""
    # your code here


def norm(v):
    """Euclidean length."""
    # your code here


def matvec(a, v):
    """Matrix times vector."""
    # your code here


def gram_schmidt(vectors, tol=1e-10):
    """Orthonormalise a list of vectors; ValueError if they are dependent."""
    # your code here


def qr(a):
    """(q, r) with orthonormal columns in q and upper triangular r."""
    # your code here


def power_method(a, tol=1e-10, max_iter=1000):
    """(dominant eigenvalue, unit eigenvector, iterations used)."""
    # your code here


print(gram_schmidt([[1.0, 1.0], [1.0, 0.0]]))
print(qr([[12.0, -51.0], [6.0, 167.0], [-4.0, 24.0]])[1])
print(power_method([[4.0, 1.0], [2.0, 3.0]]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math


def dot(u, v):
    """Dot product of two equal-length vectors."""
    if len(u) != len(v):
        raise ValueError("vectors must have the same length")
    return sum(float(x) * float(y) for x, y in zip(u, v))


def norm(v):
    """Euclidean length."""
    return math.sqrt(dot(v, v))


def matvec(a, v):
    """Matrix times vector."""
    if not a or len(a[0]) != len(v):
        raise ValueError("column count must match the vector length")
    return [dot(row, v) for row in a]


def gram_schmidt(vectors, tol=1e-10):
    """Orthonormalise a list of vectors; ValueError if they are dependent."""
    if not vectors:
        raise ValueError("need at least one vector")
    basis = []
    for vector in vectors:
        residual = [float(x) for x in vector]
        for q in basis:
            projection = dot(q, residual)
            residual = [r - projection * qi for r, qi in zip(residual, q)]
        length = norm(residual)
        if length <= tol:
            raise ValueError("vectors are linearly dependent")
        basis.append([r / length for r in residual])
    return basis


def qr(a):
    """(q, r) with orthonormal columns in q and upper triangular r."""
    if not a or not a[0]:
        raise ValueError("matrix must be non-empty")
    rows = len(a)
    cols = len(a[0])
    if rows < cols:
        raise ValueError("need at least as many rows as columns")
    columns = [[float(a[i][j]) for i in range(rows)] for j in range(cols)]
    basis = gram_schmidt(columns)
    q = [[basis[j][i] for j in range(cols)] for i in range(rows)]
    r = [[0.0] * cols for _ in range(cols)]
    for i in range(cols):
        for j in range(i, cols):
            r[i][j] = dot(basis[i], columns[j])
    return (q, r)


def power_method(a, tol=1e-10, max_iter=1000):
    """(dominant eigenvalue, unit eigenvector, iterations used)."""
    if not a:
        raise ValueError("matrix must be non-empty")
    n = len(a)
    for row in a:
        if len(row) != n:
            raise ValueError("power_method needs a square matrix")
    v = [1.0 / math.sqrt(n)] * n
    value = 0.0
    used = 0
    converged = False
    for step in range(1, max_iter + 1):
        w = matvec(a, v)
        length = norm(w)
        if length <= 1e-300:
            raise ValueError("iteration collapsed to the zero vector")
        estimate = dot(v, w)
        v = [x / length for x in w]
        used = step
        if step > 1 and abs(estimate - value) <= tol:
            value = estimate
            converged = True
            break
        value = estimate
    if not converged:
        raise ValueError("power method did not converge")
    biggest = 0
    for i in range(n):
        if abs(v[i]) > abs(v[biggest]):
            biggest = i
    if v[biggest] < 0:
        v = [-x for x in v]
    return (value, v, used)


print(gram_schmidt([[1.0, 1.0], [1.0, 0.0]]))
print(qr([[12.0, -51.0], [6.0, 167.0], [-4.0, 24.0]])[1])
print(power_method([[4.0, 1.0], [2.0, 3.0]]))
'''}],
                "hints": [
                    "Gram-Schmidt is one loop with an inner loop: for every already-accepted `q`, compute `dot(q, residual)` and subtract that multiple of `q` from the residual.",
                    "Work with the *columns* of `a` in `qr`. Building the column list first, orthonormalising it, and only then stitching `q` back together as rows keeps the indices straight.",
                    "`r[i][j] = dot(basis[i], columns[j])` uses the ORIGINAL columns, not the orthonormalised ones — that is what makes `q @ r` reproduce `a`.",
                    "In `power_method`, compute the Rayleigh quotient with the *old* unit vector (`dot(v, w)`) before replacing `v`; compare consecutive estimates, and only fix the sign of the final eigenvector.",
                ],
                "tests": [
                    {"name": "dot, norm and matvec", "code": r'''
assert dot([1, 2, 3], [4, 5, 6]) == 32.0, f"dot gave {dot([1, 2, 3], [4, 5, 6])!r}, expected 32"
assert abs(norm([3, 4]) - 5.0) < 1e-12, f"norm([3, 4]) gave {norm([3, 4])!r}, expected 5.0"
assert norm([0.0, 0.0]) == 0.0, "The zero vector has length 0"
assert matvec([[1, 2], [3, 4]], [1, 1]) == [3.0, 7.0], \
    f"matvec gave {matvec([[1, 2], [3, 4]], [1, 1])!r}, expected [3.0, 7.0]"
assert matvec([[1, 2, 3], [4, 5, 6]], [1, 0, -1]) == [-2.0, -2.0], \
    f"matvec gave {matvec([[1, 2, 3], [4, 5, 6]], [1, 0, -1])!r}"
for _args in [([1, 2], [1, 2, 3]),]:
    try:
        dot(*_args)
        assert False, f"dot{_args!r} should raise ValueError"
    except ValueError:
        pass
try:
    matvec([[1, 2], [3, 4]], [1, 2, 3])
    assert False, "matvec with a mismatched vector should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Gram-Schmidt produces an orthonormal set", "code": r'''
_b = gram_schmidt([[3.0, 0.0], [0.0, -2.0]])
assert abs(_b[0][0] - 1.0) < 1e-12 and abs(_b[0][1]) < 1e-12, f"First vector is {_b[0]!r}"
assert abs(_b[1][1] + 1.0) < 1e-12, f"Second vector is {_b[1]!r}; normalising must not flip the sign"
_b = gram_schmidt([[1.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 1.0]])
for _i in range(3):
    assert abs(norm(_b[_i]) - 1.0) < 1e-12, f"Vector {_i} has length {norm(_b[_i])!r}, expected 1"
    for _j in range(_i + 1, 3):
        assert abs(dot(_b[_i], _b[_j])) < 1e-12, \
            f"Vectors {_i} and {_j} have dot product {dot(_b[_i], _b[_j])!r}, expected 0"
'''},
                    {"name": "Gram-Schmidt detects dependence", "code": r'''
for _bad in [[[1.0, 2.0], [2.0, 4.0]],
             [[1.0, 0.0], [0.0, 1.0], [3.0, 4.0]],
             [[0.0, 0.0], [1.0, 0.0]]]:
    try:
        gram_schmidt(_bad)
        assert False, f"gram_schmidt({_bad!r}) should raise ValueError"
    except ValueError:
        pass
try:
    gram_schmidt([])
    assert False, "gram_schmidt([]) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "QR reproduces the matrix", "code": r'''
def _mm(x, y):
    return [[sum(x[i][k] * y[k][j] for k in range(len(y))) for j in range(len(y[0]))]
            for i in range(len(x))]
_a = [[12.0, -51.0], [6.0, 167.0], [-4.0, 24.0]]
_q, _r = qr(_a)
assert len(_q) == 3 and len(_q[0]) == 2, f"q has shape {(len(_q), len(_q[0]))!r}, expected (3, 2)"
assert len(_r) == 2 and len(_r[0]) == 2, f"r has shape {(len(_r), len(_r[0]))!r}, expected (2, 2)"
_prod = _mm(_q, _r)
for _i in range(3):
    for _j in range(2):
        assert abs(_prod[_i][_j] - _a[_i][_j]) < 1e-9, \
            f"(QR)[{_i}][{_j}] is {_prod[_i][_j]!r}, expected {_a[_i][_j]!r}"
assert abs(_r[0][0] - 14.0) < 1e-9 and abs(_r[0][1] - 21.0) < 1e-9 and abs(_r[1][1] - 175.0) < 1e-9, \
    f"r came out as {_r!r}, expected [[14, 21], [0, 175]]"
assert abs(_r[1][0]) < 1e-12, f"r[1][0] is {_r[1][0]!r}; R must be upper triangular"
'''},
                    {"name": "Q has orthonormal columns", "code": r'''
def _mm(x, y):
    return [[sum(x[i][k] * y[k][j] for k in range(len(y))) for j in range(len(y[0]))]
            for i in range(len(x))]
_a = [[1.0, 1.0], [1.0, 2.0], [1.0, 3.0], [1.0, 4.0]]
_q, _r = qr(_a)
_qt = [[_q[i][j] for i in range(4)] for j in range(2)]
_gram = _mm(_qt, _q)
for _i in range(2):
    for _j in range(2):
        _want = 1.0 if _i == _j else 0.0
        assert abs(_gram[_i][_j] - _want) < 1e-12, \
            f"(Q^T Q)[{_i}][{_j}] is {_gram[_i][_j]!r}, expected {_want}"
assert abs(_r[0][0] - 2.0) < 1e-12 and abs(_r[0][1] - 5.0) < 1e-12, f"r is {_r!r}"
assert abs(_r[1][1] - math.sqrt(5.0)) < 1e-12, f"r[1][1] is {_r[1][1]!r}, expected sqrt(5)"
assert all(_r[_i][_i] > 0 for _i in range(2)), "Gram-Schmidt gives a positive diagonal in R"
try:
    qr([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert False, "A wide matrix has dependent columns; qr should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Power method finds the dominant eigenpair", "code": r'''
_value, _vector, _steps = power_method([[4.0, 1.0], [2.0, 3.0]])
assert abs(_value - 5.0) < 1e-8, f"Dominant eigenvalue came out as {_value!r}, expected 5.0"
_r2 = math.sqrt(0.5)
assert abs(_vector[0] - _r2) < 1e-6 and abs(_vector[1] - _r2) < 1e-6, \
    f"Eigenvector is {_vector!r}, expected about [{_r2!r}, {_r2!r}]"
assert _steps >= 1, f"iterations came back as {_steps!r}"
_value, _vector, _ = power_method([[2.0, 1.0], [1.0, 2.0]])
assert abs(_value - 3.0) < 1e-8, f"Symmetric case gave {_value!r}, expected 3.0"
_value, _vector, _ = power_method([[6.0, 2.0, 1.0], [2.0, 3.0, 1.0], [1.0, 1.0, 1.0]])
assert abs(_value - 7.287992138960425) < 1e-6, f"3x3 case gave {_value!r}, expected 7.28799213896"
_residual = [x - _value * y for x, y in zip(matvec([[6.0, 2.0, 1.0], [2.0, 3.0, 1.0], [1.0, 1.0, 1.0]], _vector), _vector)]
assert norm(_residual) < 1e-5, f"A v - lambda v has norm {norm(_residual)!r}, expected about 0"
'''},
                    {"name": "Eigenvalue sign, scaling and refusal", "code": r'''
_value, _vector, _ = power_method([[3.0, 0.0], [0.0, -7.0]])
assert abs(_value + 7.0) < 1e-6, f"Dominance is by magnitude: got {_value!r}, expected -7.0"
assert abs(abs(_vector[1]) - 1.0) < 1e-5, f"Eigenvector is {_vector!r}, expected about [0, 1]"
_biggest = 0 if abs(_vector[0]) > abs(_vector[1]) else 1
assert _vector[_biggest] > 0, f"The largest component of {_vector!r} should be positive"
assert abs(norm(_vector) - 1.0) < 1e-9, f"The eigenvector should be a unit vector; norm is {norm(_vector)!r}"
_value, _vector, _ = power_method([[1.0, 0.0], [0.0, 1.0]])
assert abs(_value - 1.0) < 1e-9, f"The identity has eigenvalue 1; got {_value!r}"
try:
    power_method([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert False, "power_method on a non-square matrix should raise ValueError"
except ValueError:
    pass
try:
    power_method([[2.0, 1.0], [1.0, 2.0]], tol=1e-16, max_iter=1)
    assert False, "Exhausting max_iter without converging should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M8
        {
            "title": "Projection, least squares and the normal equations",
            "summary": "When Ax = b has no solution, the honest answer is the closest one — and closest means orthogonal.",
            "concepts": [
                "The projection of b onto a subspace is the point of that subspace nearest b, and the error b - p is orthogonal to everything in it",
                "P = A(A^T A)^-1 A^T projects onto the column space; P^2 = P and P^T = P, and its only eigenvalues are 0 and 1",
                "The normal equations A^T A x = A^T b say precisely that the residual is orthogonal to every column of A",
                "With orthonormal columns the normal equations collapse to x = Q^T b, which is what makes QR worth computing",
                "Forming A^T A squares the condition number, so the numerically sound route to a fit runs through QR, not through the normal equations",
            ],
            "quiz": {
                "title": "Closest, not exact",
                "minutes": 8,
                "questions": [
                    {
                        "q": "`Ax = b` is inconsistent. What does the least-squares solution `xhat` achieve?",
                        "opts": [
                            "It makes `A xhat` the orthogonal projection of `b` onto the column space of `A`",
                            "It makes `A xhat` equal to `b` after all",
                            "It finds the vector of the null space closest to `b`",
                            "It makes the residual as large as possible, so the failure is visible",
                        ],
                        "a": 0,
                        "why": r"""
Least squares minimises the length of `b - Ax`. Every candidate `Ax` lies in the
column space, so the best possible one is the point of that space nearest `b` —
its orthogonal projection — and the leftover residual is perpendicular to the
column space. Hitting `b` exactly is impossible by assumption, which is what
inconsistent means. The null space is a subspace of the *inputs* and lives in a
different space from `b` entirely.
""",
                    },
                    {
                        "q": "Why must the residual be orthogonal to every column of `A` at the minimum?",
                        "opts": [
                            "Because `A` has full rank",
                            "Because the residual is always zero at a minimum",
                            "Because `A^T (b - Ax) = 0` is the normal equation written out: one dot product per column",
                            "Because orthogonal vectors have the smallest norm",
                        ],
                        "a": 2,
                        "why": r"""
Multiply the normal equations `A^T A x = A^T b` out and they read
`A^T (b - Ax) = 0` — row `i` of that is the dot product of column `i` of `A` with
the residual. Geometrically it is obvious: if the residual still had a component
along some column, you could move a little way along that column and get strictly
closer, so you were not at the minimum. A residual of zero would mean the system
was consistent, and full rank guarantees a *unique* minimiser without being the
reason orthogonality holds.
""",
                    },
                    {
                        "q": "A tall matrix `Q` has orthonormal columns. What is the least-squares solution of `Q x = b`?",
                        "opts": ["`x = b`", "`x = Q b`", "`x = Q^T b`", "Undefined, because `Q` is not square"],
                        "a": 2,
                        "why": r"""
Orthonormal columns mean `Q^T Q = I`, so the normal equations `Q^T Q x = Q^T b`
collapse straight to `x = Q^T b` — no system left to solve, just one matrix-vector
product, and no inverse anywhere. `Q b` does not even have a defined shape when
`Q` is tall, and `x = b` mixes up the coefficient vector with the data. Least
squares is perfectly well defined for a tall matrix; that is the case it exists
for.
""",
                    },
                    {
                        "q": "Why fit through a QR factorisation rather than by forming `A^T A` and solving?",
                        "opts": [
                            "Because `A^T A` is not symmetric",
                            "Because the normal equations have no solution when `A` is tall",
                            "Because QR needs fewer arithmetic operations",
                            "Because the condition number of `A^T A` is the square of the condition number of `A`, so roughly twice as many digits are lost",
                        ],
                        "a": 3,
                        "why": r"""
Squaring the matrix squares its conditioning: a design matrix with condition
number `1e8` gives a Gram matrix at `1e16`, and in double precision there is
nothing left. QR multiplies by an orthogonal matrix instead, which cannot amplify
error at all, so the fit inherits the conditioning of `A` rather than of `A^T A`.
Speed is not the argument — QR costs roughly twice the flops. And `A^T A` is
symmetric, in fact positive definite whenever the columns are independent, which
is exactly when the normal equations do have their unique solution.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M9
        {
            "title": "Eigenvalues, the characteristic polynomial and diagonalisation",
            "summary": "The algebra behind the iteration: which directions a matrix merely stretches, and what knowing them buys you.",
            "concepts": [
                "Av = lambda v with v non-zero: an eigenvector is a direction the map stretches without turning",
                "det(A - lambda I) = 0 is the characteristic equation; the trace is the sum of the eigenvalues and the determinant is their product",
                "Eigenvectors belonging to distinct eigenvalues are independent, so n of them give A = S Lambda S^-1",
                "Diagonalisation makes powers cheap — A^k = S Lambda^k S^-1 — so long-run behaviour is decided by the largest |lambda|, which is why power iteration converges to it",
                "A defective matrix has too few independent eigenvectors to diagonalise, and a real matrix may have no real eigenvector at all: a rotation turns everything",
            ],
            "quiz": {
                "title": "Eigenvalues on paper",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What are the eigenvalues of `[[2, 1], [1, 2]]`?",
                        "opts": ["2 and 2", "3 and 1", "2 and 1", "4 and 0"],
                        "a": 1,
                        "why": r"""
`det(A - lambda I) = (2 - lambda)^2 - 1 = lambda^2 - 4 lambda + 3`, which factors
as `(lambda - 3)(lambda - 1)`. Both checks agree: the eigenvalues sum to the trace
4 and multiply to the determinant 3. The eigenvectors are `(1, 1)` for 3 and
`(1, -1)` for 1 — the symmetric matrix hands you an orthogonal pair, as it always
does. Reading the diagonal and calling it 2 and 2 ignores the off-diagonal
coupling entirely, and 4 and 0 is the pair for `[[2, 2], [2, 2]]`.
""",
                    },
                    {
                        "q": "A 2-by-2 matrix has trace 7 and determinant 12. What are its eigenvalues?",
                        "opts": ["7 and 12", "1 and 6", "3 and 4", "-3 and -4"],
                        "a": 2,
                        "why": r"""
For 2-by-2 the characteristic polynomial is `lambda^2 - (trace) lambda + det`,
here `lambda^2 - 7 lambda + 12 = (lambda - 3)(lambda - 4)`. The two conditions —
sum 7, product 12 — pin the pair down without ever writing the matrix. The pair
1 and 6 sums correctly but multiplies to 6, and a negative pair would give a
negative trace. This shortcut is the fastest sanity check there is on a computed
eigenpair.
""",
                    },
                    {
                        "q": "Which of these matrices cannot be diagonalised?",
                        "opts": ["`[[1, 1], [0, 1]]`", "`[[2, 0], [0, 3]]`", "`[[0, 1], [1, 0]]`", "`[[2, 1], [1, 2]]`"],
                        "a": 0,
                        "why": r"""
The shear has the repeated eigenvalue 1, but solving `(A - I)v = 0` gives only
multiples of `(1, 0)`: a one-dimensional eigenspace where two dimensions are
needed. That is a defective matrix, and no `S` exists. Note that a repeated
eigenvalue is not by itself the problem — the identity repeats its eigenvalue and
is already diagonal. The other two are symmetric, and a symmetric matrix is always
diagonalisable, by an orthogonal `S` at that.
""",
                    },
                    {
                        "q": "What are the real eigenvectors of the quarter-turn `[[0, -1], [1, 0]]`?",
                        "opts": [
                            "`(1, 0)` and `(0, 1)`, with eigenvalues 0 and 1",
                            "Every vector, since a rotation preserves length",
                            "There are none; the eigenvalues are `i` and `-i`",
                            "`(1, 1)`, with eigenvalue 1",
                        ],
                        "a": 2,
                        "why": r"""
An eigenvector is a direction the map does not turn, and a quarter-turn turns
every direction, so there is nothing for it to be. The algebra agrees:
`det(A - lambda I) = lambda^2 + 1`, whose roots are `i` and `-i`, with complex
eigenvectors `(1, -i)` and `(1, i)`. Preserving length is a statement about the
norm, not about direction. This is the standard demonstration that a perfectly
ordinary real matrix can force you into complex arithmetic — the arithmetic that
rotations, oscillations and quantum states all live in.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M10
        {
            "title": "Symmetric matrices, the spectral theorem and quadratic forms",
            "summary": "The best-behaved matrices there are: real eigenvalues, orthogonal eigenvectors, and a definiteness test you can actually run.",
            "concepts": [
                "The spectral theorem: a real symmetric matrix has real eigenvalues and an orthonormal eigenbasis, so A = Q Lambda Q^T",
                "The complex analogue swaps transpose for conjugate transpose — Hermitian matrices have real eigenvalues, unitary matrices preserve length",
                "A quadratic form x^T A x is a landscape whose curvature along each eigenvector is that eigenvalue",
                "Positive definite means x^T A x > 0 for every non-zero x, equivalently every eigenvalue positive, equivalently every pivot positive",
                "A^T A is symmetric and positive semidefinite for any A, and positive definite exactly when the columns of A are independent",
            ],
            "quiz": {
                "title": "Symmetry, definiteness and curvature",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What does symmetry of a real matrix `A` guarantee?",
                        "opts": [
                            "Distinct eigenvalues",
                            "Positive eigenvalues",
                            "That `A` is invertible",
                            "Real eigenvalues and an orthonormal basis of eigenvectors",
                        ],
                        "a": 3,
                        "why": r"""
That is the spectral theorem: `A = Q Lambda Q^T` with `Q` orthogonal and `Lambda`
real. It holds even when eigenvalues repeat — a repeat simply means an eigenspace
of dimension greater than one, inside which any orthonormal basis will serve, so
distinctness is not promised and is not needed. Symmetry says nothing about sign:
`[[1, 2], [2, 1]]` is symmetric with eigenvalues 3 and -1, and the zero matrix is
symmetric and not invertible.
""",
                    },
                    {
                        "q": "For a symmetric `A`, which condition is **not** equivalent to positive definiteness?",
                        "opts": [
                            "Every entry of `A` is positive",
                            "Every eigenvalue of `A` is positive",
                            "Every pivot of elimination on `A` is positive",
                            "`x^T A x > 0` for every non-zero `x`",
                        ],
                        "a": 0,
                        "why": r"""
Entries are not the test, in either direction. `[[1, 2], [2, 1]]` has every entry
positive yet eigenvalues 3 and -1, so the form goes negative along `(1, -1)`; and
`[[2, -1], [-1, 2]]` has a negative entry and is positive definite. The other
three really are the same statement in three languages — the energy definition,
the eigenvalue test, and the pivot test that falls out of elimination for free,
which is why Cholesky doubles as a definiteness check.
""",
                    },
                    {
                        "q": "What is true of `A^T A` for an arbitrary m-by-n matrix `A`?",
                        "opts": [
                            "It equals `A A^T`",
                            "It is always invertible",
                            "It is symmetric and positive semidefinite, and positive definite exactly when the columns of `A` are independent",
                            "It is symmetric only when `A` is square",
                        ],
                        "a": 2,
                        "why": r"""
Symmetry is immediate: transposing `A^T A` gives `A^T A` back, whatever the shape.
And `x^T A^T A x = (Ax) . (Ax) = ||Ax||^2`, which is never negative and is zero
exactly when `x` is in the null space of `A` — so the form is strictly positive
precisely when that null space is trivial, meaning independent columns. That is
also the exact condition for the normal equations to be solvable. `A A^T` is a
different, m-by-m matrix with the same non-zero eigenvalues but a different size.
""",
                    },
                    {
                        "q": "Over the complex numbers, which pair of matrix classes plays the roles that symmetric and orthogonal play over the reals?",
                        "opts": [
                            "Hermitian and unitary",
                            "Upper triangular and diagonal",
                            "Symmetric and orthogonal, unchanged",
                            "Positive definite and singular",
                        ],
                        "a": 0,
                        "why": r"""
The complex inner product conjugates one side so that `v . v` comes out real and
non-negative, and every definition follows that conjugation: Hermitian means `A`
equals its conjugate transpose, unitary means `U* U = I`. Hermitian matrices have
real eigenvalues and an orthonormal eigenbasis, exactly as symmetric ones do, and
unitary matrices preserve length, exactly as orthogonal ones do. Plain symmetry
without conjugation loses the guarantee of real eigenvalues, which is why quantum
mechanics states its observables as Hermitian and its gates as unitary.
""",
                    },
                ],
            },
        },
        # ------------------------------------------------------------ M11
        {
            "title": "Singular values: the SVD, the pseudoinverse and conditioning",
            "summary": "Every matrix, however awkward, is a rotation then a stretch then a rotation — and that is where conditioning is written down.",
            "concepts": [
                "A = U Sigma V^T exists for every matrix of every shape and rank, with sigma_1 >= sigma_2 >= ... >= 0",
                "The right singular vectors are the eigenvectors of A^T A and the singular values are the square roots of its eigenvalues",
                "The count of non-zero singular values is the rank, and it is the numerically honest rank: a tiny sigma is a column that nearly does not count",
                "The condition number sigma_max / sigma_min bounds how far a relative error in b is amplified in x, and squaring A into A^T A squares it",
                "The pseudoinverse A+ = V Sigma+ U^T inverts what can be inverted and ignores the rest, and truncating after k terms is the best rank-k approximation there is",
            ],
            "quiz": {
                "title": "Reading a matrix by its singular values",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Which matrices have a singular value decomposition?",
                        "opts": [
                            "Only square ones",
                            "Only symmetric ones",
                            "Only matrices of full rank",
                            "Every real matrix, of any shape and any rank",
                        ],
                        "a": 3,
                        "why": r"""
The SVD asks for nothing: no squareness, no independence, no symmetry. That is
precisely its advantage over diagonalisation, which needs a square matrix with a
full set of independent eigenvectors and fails on the defective ones. A rank-2
matrix of shape 7-by-3 has an SVD with `sigma_3 = 0`, and the zeros are
informative rather than an obstacle — they are how the decomposition reports the
rank.
""",
                    },
                    {
                        "q": "Where do the singular values of `A` come from?",
                        "opts": [
                            "The square roots of the eigenvalues of `A^T A`, which are never negative",
                            "The eigenvalues of `A` itself, sorted by size",
                            "The diagonal entries of `A`",
                            "The pivots produced by elimination",
                        ],
                        "a": 0,
                        "why": r"""
`A^T A` is symmetric positive semidefinite, so its eigenvalues are real and at
least zero, and their square roots are the singular values. For a symmetric
positive definite matrix these coincide with the eigenvalues of `A`, but in
general they are unrelated: `[[0, 5], [0, 0]]` has both eigenvalues zero and
singular values 5 and 0. This is also the reason the capstone gets a condition
number out of power iteration on `A^T A` alone — no full SVD required.
""",
                    },
                    {
                        "q": "The condition number of `A` is about `1e6` and the entries of `b` are known to 10 significant digits. How many digits of `x` can you trust?",
                        "opts": ["About 10 — conditioning affects speed, not accuracy", "About 4", "About 16", "None"],
                        "a": 1,
                        "why": r"""
A relative perturbation in the data is amplified by up to the condition number, so
roughly `log10(1e6) = 6` digits are lost and about 4 survive. Conditioning is a
property of the problem, not of the algorithm: a perfect solver cannot recover
digits the problem has destroyed. It is also why forming the normal equations
hurts here — `A^T A` would carry a condition number near `1e12`, leaving nothing
of a 10-digit input, while QR on `A` keeps those four digits.
""",
                    },
                    {
                        "q": "You keep only the `k` largest singular values and discard the rest. What have you built?",
                        "opts": [
                            "A random rank-k matrix",
                            "The inverse of `A` restricted to k dimensions",
                            "Nothing useful unless `A` is symmetric",
                            "The best rank-k approximation of `A` in the Frobenius and spectral norms",
                        ],
                        "a": 3,
                        "why": r"""
This is the Eckart-Young theorem: no rank-k matrix comes closer to `A`, and the
error left behind is measured exactly by the singular values you threw away. It is
the mathematics under image compression, latent semantic indexing and principal
component analysis, all of which are the same truncation applied to different
data. Symmetry is not required — the SVD never requires it — and truncation
approximates `A`, it does not invert it.
""",
                    },
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — least-squares engine with conditioning diagnostics",
        "runtime": "python",
        "minutes": 280,
        "brief": r'''
One library, `linalg.py`, that fits a model to data and tells you how much to
trust the fit. `main.py` is a demo that fits a polynomial and prints the report.

## Building blocks

- `shape(a)` — `(rows, cols)`, raising `ValueError` for anything that is not a
  non-empty rectangular list of lists
- `transpose(a)`, `dot(u, v)`, `norm(v)`, `matvec(a, v)`, `matmul(a, b)` —
  each validating its shapes
- `rank(a, tol=1e-9)` — by elimination with partial pivoting
- `qr(a, tol=1e-12)` — modified Gram-Schmidt; `ValueError` when the columns are
  dependent or when there are fewer rows than columns
- `solve_upper(r, y)` — back substitution; `ValueError` on a zero diagonal
- `lu_decompose(m, tol=1e-14)` and `lu_solve(l, u, perm, b)` — as in lab 3

## Eigenvalue diagnostics

- `power_method(m, tol=1e-12, max_iter=20000)` — the dominant eigenvalue of a
  symmetric `m` by Rayleigh-quotient iteration. Seed the start vector with
  `random.Random(7)` so runs are reproducible.
- `inverse_power(m, tol=1e-12, max_iter=500)` — the *smallest* eigenvalue, by
  running the same iteration against `lu_solve` on the factors of `m`. The
  convergence rate is `lambda_min / lambda_2`, which is fast precisely when the
  matrix is ill conditioned.
- `condition_number(a)` — `sqrt(lambda_max / lambda_min)` of `A^T A`, which is
  the ratio of the largest to the smallest singular value of `A`. Return
  `math.inf` when `A^T A` is singular.

## Fitting

- `vandermonde(xs, degree)` — the design matrix whose row for `x` is
  `[1, x, x^2, ..., x^degree]`. A negative degree, or fewer points than
  `degree + 1`, raises `ValueError`.
- `least_squares(a, b, tol=1e-9)` — returns a `Fit` dataclass with fields
  `coefficients`, `residual_norm`, `rank`, `condition`, in that order. Solve via
  `QR`: the normal equations squared the condition number, and you have just
  built the tool to measure that. Raise `ValueError` when `b` is the wrong
  length, when there are fewer rows than columns, or when the design matrix is
  rank deficient — a fit nobody can interpret is worse than no fit.
- `fit_report(fit)` — a string of `len(coefficients) + 4` lines: the header
  `coefficients:`, one `  cI = value` line per coefficient, then lines starting
  `rank`, `condition` and `residual norm`.

```text
xs = [0, 1, 2, 3, 4],  ys = 2 - 3x + x^2,  degree 2
  coefficients -> [2.0, -3.0, 1.0]
  residual_norm -> about 0
  rank -> 3,  condition -> 27.112831810
```
''',
        "deliverables": [
            "`linalg.py` — the whole engine, importable with no output and no side effects",
            "`main.py` — a demo fitting a polynomial to sample data and printing the report",
            "A QR-based `least_squares` that never forms the normal equations",
            "Rank detection that refuses a rank-deficient design matrix instead of returning noise",
            "A `condition_number` built from power and inverse-power iteration on `A^T A`",
            "`fit_report` — a fixed-shape summary of coefficients, rank, conditioning and residual",
        ],
        "constraints": [
            "Standard library only — `math`, `random` and `dataclasses` are enough",
            "`linalg.py` must define names only; importing it must print nothing",
            "Every RNG is seeded with `random.Random(7)`, so two runs agree exactly",
            "No routine may mutate the matrix or vector it is given",
            "The whole demo must finish in well under a second",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "All automated checks pass, including the exact-fit, over-determined and rank-deficient cases."},
            {"criterion": "Numerical judgement", "weight": 25,
             "evidence": "Least squares goes through QR rather than the normal equations, and pivoting is used wherever elimination is."},
            {"criterion": "Diagnostics", "weight": 15,
             "evidence": "Reported rank and condition number match independent references to at least six significant figures."},
            {"criterion": "Validation", "weight": 12,
             "evidence": "Ragged matrices, mismatched right-hand sides, singular systems and negative degrees all raise ValueError."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "Docstrings on every public routine, no dead code, no debug prints left in linalg.py."},
        ],
        "hints": [
            "Write `shape` first and call it from everywhere else — one validation routine, used seven times, is the difference between a library and a pile of functions.",
            "Modified Gram-Schmidt subtracts each projection from the working vector immediately, so later projections see the already-reduced residual. It costs the same as the classical version and is far more stable.",
            "`least_squares` reduces to `solve_upper(r, matvec(transpose(q), b))`: multiplying by Q^T is an orthogonal change of basis, so it cannot amplify the error.",
            "`inverse_power` is just `power_method` with `A^-1` in place of `A`, and `A^-1 v` is spelt `lu_solve(l, u, perm, v)` — factor once, outside the loop.",
        ],
        "files": [
            {"name": "linalg.py", "content": r'''
import math
import random
from dataclasses import dataclass


@dataclass
class Fit:
    coefficients: list
    residual_norm: float
    rank: int
    condition: float


def shape(a):
    """(rows, cols) after validating a is a non-empty rectangular matrix."""
    # your code here


def transpose(a):
    # your code here
    pass


def dot(u, v):
    # your code here
    pass


def norm(v):
    # your code here
    pass


def matvec(a, v):
    # your code here
    pass


def matmul(a, b):
    # your code here
    pass


def rank(a, tol=1e-9):
    """Number of pivots found by elimination with partial pivoting."""
    # your code here


def qr(a, tol=1e-12):
    """(q, r) by modified Gram-Schmidt on the columns of a."""
    # your code here


def solve_upper(r, y):
    """Back substitution against an upper triangular matrix."""
    # your code here


def lu_decompose(m, tol=1e-14):
    """(l, u, perm, sign) with PA = LU."""
    # your code here


def lu_solve(l, u, perm, b):
    """Solve from LU factors."""
    # your code here


def power_method(m, tol=1e-12, max_iter=20000):
    """Dominant eigenvalue of a symmetric matrix."""
    # your code here


def inverse_power(m, tol=1e-12, max_iter=500):
    """Smallest eigenvalue of a symmetric matrix."""
    # your code here


def condition_number(a):
    """Ratio of the largest to the smallest singular value of a."""
    # your code here


def vandermonde(xs, degree):
    """Polynomial design matrix with rows [1, x, ..., x**degree]."""
    # your code here


def least_squares(a, b, tol=1e-9):
    """Least-squares fit via QR, returned as a Fit."""
    # your code here


def fit_report(fit):
    """A fixed-shape textual summary of a Fit."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from linalg import vandermonde, least_squares, fit_report

xs = [0, 1, 2, 3, 4, 5, 6]
ys = [2.0, 0.1, -1.8, -1.9, 0.2, 4.1, 10.0]

fit = least_squares(vandermonde(xs, 2), ys)
print(fit_report(fit))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "linalg.py", "content": r'''
import math
import random
from dataclasses import dataclass


@dataclass
class Fit:
    coefficients: list
    residual_norm: float
    rank: int
    condition: float


def shape(a):
    """(rows, cols) after validating a is a non-empty rectangular matrix."""
    if not isinstance(a, list) or not a:
        raise ValueError("matrix must be a non-empty list of rows")
    cols = None
    for row in a:
        if not isinstance(row, list) or not row:
            raise ValueError("every row must be a non-empty list")
        if cols is None:
            cols = len(row)
        elif len(row) != cols:
            raise ValueError("all rows must have the same length")
    return (len(a), cols)


def transpose(a):
    """A new matrix with rows and columns exchanged."""
    rows, cols = shape(a)
    return [[float(a[i][j]) for i in range(rows)] for j in range(cols)]


def dot(u, v):
    """Dot product of two equal-length vectors."""
    if len(u) != len(v):
        raise ValueError("vectors must have the same length")
    return sum(float(x) * float(y) for x, y in zip(u, v))


def norm(v):
    """Euclidean length of a vector."""
    return math.sqrt(dot(v, v))


def matvec(a, v):
    """Matrix times vector."""
    rows, cols = shape(a)
    if len(v) != cols:
        raise ValueError("vector length must match the column count")
    return [dot(row, v) for row in a]


def matmul(a, b):
    """Matrix product."""
    ar, ac = shape(a)
    br, bc = shape(b)
    if ac != br:
        raise ValueError("inner dimensions must agree")
    bt = transpose(b)
    return [[dot(a[i], bt[j]) for j in range(bc)] for i in range(ar)]


def rank(a, tol=1e-9):
    """Number of pivots found by elimination with partial pivoting."""
    rows, cols = shape(a)
    u = [[float(x) for x in row] for row in a]
    pivot = 0
    for col in range(cols):
        if pivot >= rows:
            break
        best = pivot
        for r in range(pivot + 1, rows):
            if abs(u[r][col]) > abs(u[best][col]):
                best = r
        if abs(u[best][col]) <= tol:
            continue
        u[pivot], u[best] = u[best], u[pivot]
        for r in range(pivot + 1, rows):
            factor = u[r][col] / u[pivot][col]
            for c in range(col, cols):
                u[r][c] -= factor * u[pivot][c]
            u[r][col] = 0.0
        pivot += 1
    return pivot


def qr(a, tol=1e-12):
    """(q, r) by modified Gram-Schmidt on the columns of a."""
    rows, cols = shape(a)
    if rows < cols:
        raise ValueError("need at least as many rows as columns")
    columns = transpose(a)
    basis = []
    r = [[0.0] * cols for _ in range(cols)]
    for j in range(cols):
        residual = list(columns[j])
        for i, q in enumerate(basis):
            r[i][j] = dot(q, residual)
            residual = [x - r[i][j] * qi for x, qi in zip(residual, q)]
        length = norm(residual)
        if length <= tol:
            raise ValueError("columns are linearly dependent")
        r[j][j] = length
        basis.append([x / length for x in residual])
    q = [[basis[j][i] for j in range(cols)] for i in range(rows)]
    return (q, r)


def solve_upper(r, y):
    """Back substitution against an upper triangular matrix."""
    n, cols = shape(r)
    if n != cols:
        raise ValueError("solve_upper needs a square triangular matrix")
    if len(y) != n:
        raise ValueError("right-hand side length must match")
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if r[i][i] == 0.0:
            raise ValueError("triangular matrix is singular")
        total = float(y[i])
        for j in range(i + 1, n):
            total -= r[i][j] * x[j]
        x[i] = total / r[i][i]
    return x


def lu_decompose(m, tol=1e-14):
    """(l, u, perm, sign) with PA = LU."""
    n, cols = shape(m)
    if n != cols:
        raise ValueError("lu_decompose needs a square matrix")
    u = [[float(x) for x in row] for row in m]
    lower = [[0.0] * n for _ in range(n)]
    perm = list(range(n))
    sign = 1.0
    for col in range(n):
        best = col
        for r in range(col + 1, n):
            if abs(u[r][col]) > abs(u[best][col]):
                best = r
        if abs(u[best][col]) <= tol:
            raise ValueError("matrix is singular")
        if best != col:
            u[col], u[best] = u[best], u[col]
            lower[col], lower[best] = lower[best], lower[col]
            perm[col], perm[best] = perm[best], perm[col]
            sign = -sign
        for r in range(col + 1, n):
            factor = u[r][col] / u[col][col]
            lower[r][col] = factor
            for c in range(col, n):
                u[r][c] -= factor * u[col][c]
            u[r][col] = 0.0
    for i in range(n):
        lower[i][i] = 1.0
    return (lower, u, perm, sign)


def lu_solve(l, u, perm, b):
    """Solve from LU factors."""
    n = len(l)
    if len(b) != n:
        raise ValueError("b must have one entry per row")
    y = [0.0] * n
    for i in range(n):
        total = float(b[perm[i]])
        for j in range(i):
            total -= l[i][j] * y[j]
        y[i] = total
    return solve_upper(u, y)


def _seeded_unit(n):
    """A reproducible starting vector that is unlikely to be deficient."""
    rng = random.Random(7)
    v = [rng.random() + 0.5 for _ in range(n)]
    length = norm(v)
    return [x / length for x in v]


def power_method(m, tol=1e-12, max_iter=20000):
    """Dominant eigenvalue of a symmetric matrix."""
    n, cols = shape(m)
    if n != cols:
        raise ValueError("power_method needs a square matrix")
    v = _seeded_unit(n)
    value = 0.0
    for step in range(1, max_iter + 1):
        w = matvec(m, v)
        length = norm(w)
        if length <= 1e-300:
            return 0.0
        estimate = dot(v, w)
        v = [x / length for x in w]
        if step > 1 and abs(estimate - value) <= tol * (1.0 + abs(estimate)):
            return estimate
        value = estimate
    raise ValueError("power method did not converge")


def inverse_power(m, tol=1e-12, max_iter=500):
    """Smallest eigenvalue of a symmetric matrix."""
    n, cols = shape(m)
    lower, u, perm, _ = lu_decompose(m)
    v = _seeded_unit(n)
    value = 0.0
    for step in range(1, max_iter + 1):
        w = lu_solve(lower, u, perm, v)
        length = norm(w)
        if length <= 1e-300:
            raise ValueError("inverse iteration collapsed")
        v = [x / length for x in w]
        estimate = dot(v, matvec(m, v))
        if step > 1 and abs(estimate - value) <= tol * (1.0 + abs(estimate)):
            return estimate
        value = estimate
    raise ValueError("inverse power method did not converge")


def condition_number(a):
    """Ratio of the largest to the smallest singular value of a."""
    gram = matmul(transpose(a), a)
    top = power_method(gram)
    if top <= 0.0:
        return math.inf
    try:
        low = inverse_power(gram)
    except ValueError:
        return math.inf
    if low <= 0.0:
        return math.inf
    return math.sqrt(top / low)


def vandermonde(xs, degree):
    """Polynomial design matrix with rows [1, x, ..., x**degree]."""
    if degree < 0:
        raise ValueError("degree must not be negative")
    if len(xs) < degree + 1:
        raise ValueError("need at least degree + 1 sample points")
    return [[float(x) ** k for k in range(degree + 1)] for x in xs]


def least_squares(a, b, tol=1e-9):
    """Least-squares fit via QR, returned as a Fit."""
    rows, cols = shape(a)
    if len(b) != rows:
        raise ValueError("b must have one entry per row")
    if rows < cols:
        raise ValueError("an underdetermined system has no unique least-squares fit")
    found = rank(a, tol)
    if found < cols:
        raise ValueError("design matrix is rank deficient")
    q, r = qr(a)
    coefficients = solve_upper(r, matvec(transpose(q), b))
    predicted = matvec(a, coefficients)
    residual = [float(bi) - pi for bi, pi in zip(b, predicted)]
    return Fit(coefficients, norm(residual), found, condition_number(a))


def fit_report(fit):
    """A fixed-shape textual summary of a Fit."""
    lines = ["coefficients:"]
    for i, c in enumerate(fit.coefficients):
        lines.append(f"  c{i} = {c:.10g}")
    lines.append(f"rank          = {fit.rank}")
    lines.append(f"condition     = {fit.condition:.4e}")
    lines.append(f"residual norm = {fit.residual_norm:.4e}")
    return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from linalg import vandermonde, least_squares, fit_report

xs = [0, 1, 2, 3, 4, 5, 6]
ys = [2.0, 0.1, -1.8, -1.9, 0.2, 4.1, 10.0]

fit = least_squares(vandermonde(xs, 2), ys)
print(fit_report(fit))

exact = least_squares(vandermonde([0, 1, 2, 3, 4], 2), [2.0, 0.0, 0.0, 2.0, 6.0])
print()
print("exact quadratic:", [round(c, 12) for c in exact.coefficients])
'''},
        ],
        "tests": [
            {"name": "Shapes and products", "code": r'''
from linalg import shape, transpose, dot, norm, matvec, matmul
assert shape([[1, 2, 3], [4, 5, 6]]) == (2, 3), f"shape gave {shape([[1, 2, 3], [4, 5, 6]])!r}"
assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1.0, 4.0], [2.0, 5.0], [3.0, 6.0]], \
    f"transpose gave {transpose([[1, 2, 3], [4, 5, 6]])!r}"
assert dot([1, 2, 3], [4, 5, 6]) == 32.0, f"dot gave {dot([1, 2, 3], [4, 5, 6])!r}, expected 32"
assert abs(norm([3, 4]) - 5.0) < 1e-12, f"norm([3, 4]) gave {norm([3, 4])!r}"
assert matvec([[1, 2], [3, 4]], [1, 1]) == [3.0, 7.0], f"matvec gave {matvec([[1, 2], [3, 4]], [1, 1])!r}"
assert matmul([[1, 2, 3], [4, 5, 6]], [[7, 8], [9, 10], [11, 12]]) == [[58.0, 64.0], [139.0, 154.0]], \
    f"matmul gave {matmul([[1, 2, 3], [4, 5, 6]], [[7, 8], [9, 10], [11, 12]])!r}"
for _bad in [[], [[]], [[1, 2], [3]], "nope"]:
    try:
        shape(_bad)
        assert False, f"shape({_bad!r}) should raise ValueError"
    except ValueError:
        pass
try:
    matmul([[1, 2]], [[1, 2]])
    assert False, "matmul with mismatched inner dimensions should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Rank by elimination", "code": r'''
from linalg import rank
for _name, _a, _want in [("dependent", [[1, 2], [2, 4]], 1),
                         ("full", [[1, 2], [3, 4]], 2),
                         ("3x3 rank 2", [[1, 2, 3], [4, 5, 6], [7, 8, 9]], 2),
                         ("zeros", [[0, 0, 0], [0, 0, 0]], 0),
                         ("tall dependent", [[1, 2], [2, 4], [3, 6]], 1),
                         ("vandermonde", [[1, 0, 0], [1, 1, 1], [1, 2, 4], [1, 3, 9], [1, 4, 16]], 3)]:
    _got = rank(_a)
    assert _got == _want, f"rank of the {_name} case gave {_got!r}, expected {_want}"
'''},
            {"name": "QR factorisation", "code": r'''
from linalg import qr, matmul, transpose
_a = [[12.0, -51.0], [6.0, 167.0], [-4.0, 24.0]]
_q, _r = qr(_a)
_prod = matmul(_q, _r)
for _i in range(3):
    for _j in range(2):
        assert abs(_prod[_i][_j] - _a[_i][_j]) < 1e-9, \
            f"(QR)[{_i}][{_j}] is {_prod[_i][_j]!r}, expected {_a[_i][_j]!r}"
assert abs(_r[0][0] - 14.0) < 1e-9 and abs(_r[0][1] - 21.0) < 1e-9 and abs(_r[1][1] - 175.0) < 1e-9, \
    f"R came out as {_r!r}, expected [[14, 21], [0, 175]]"
_gram = matmul(transpose(_q), _q)
for _i in range(2):
    for _j in range(2):
        _want = 1.0 if _i == _j else 0.0
        assert abs(_gram[_i][_j] - _want) < 1e-12, f"(Q^T Q)[{_i}][{_j}] is {_gram[_i][_j]!r}"
for _bad in [[[1.0, 2.0], [2.0, 4.0]], [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]]:
    try:
        qr(_bad)
        assert False, f"qr({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Triangular and LU solves", "code": r'''
from linalg import solve_upper, lu_decompose, lu_solve, matmul
_x = solve_upper([[2.0, 1.0], [0.0, 4.0]], [4.0, 8.0])
assert abs(_x[1] - 2.0) < 1e-12 and abs(_x[0] - 1.0) < 1e-12, f"solve_upper gave {_x!r}, expected [1.0, 2.0]"
try:
    solve_upper([[0.0, 1.0], [0.0, 1.0]], [1.0, 1.0])
    assert False, "A zero on the diagonal should raise ValueError"
except ValueError:
    pass
_a = [[4, 3, 2], [1, 5, 7], [2, 2, 9]]
_l, _u, _perm, _sign = lu_decompose(_a)
_lu = matmul(_l, _u)
for _i in range(3):
    for _j in range(3):
        assert abs(_lu[_i][_j] - float(_a[_perm[_i]][_j])) < 1e-9, \
            f"(LU)[{_i}][{_j}] is {_lu[_i][_j]!r}, expected {float(_a[_perm[_i]][_j])!r}"
_x = lu_solve(_l, _u, _perm, [1, 2, 3])
assert abs(_x[0] - 6.0 / 41.0) < 1e-12, f"lu_solve gave {_x!r}; x[0] should be 6/41"
try:
    lu_decompose([[1, 2], [2, 4]])
    assert False, "lu_decompose of a singular matrix should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Power and inverse-power iteration", "code": r'''
from linalg import power_method, inverse_power
assert abs(power_method([[2.0, 1.0], [1.0, 2.0]]) - 3.0) < 1e-8, \
    f"power_method gave {power_method([[2.0, 1.0], [1.0, 2.0]])!r}, expected 3.0"
assert abs(inverse_power([[2.0, 1.0], [1.0, 2.0]]) - 1.0) < 1e-8, \
    f"inverse_power gave {inverse_power([[2.0, 1.0], [1.0, 2.0]])!r}, expected 1.0"
_m = [[6.0, 2.0, 1.0], [2.0, 3.0, 1.0], [1.0, 1.0, 1.0]]
assert abs(power_method(_m) - 7.287992138960425) < 1e-7, \
    f"power_method on the 3x3 case gave {power_method(_m)!r}, expected 7.28799213896"
assert abs(inverse_power(_m) - 0.5789333856910526) < 1e-7, \
    f"inverse_power on the 3x3 case gave {inverse_power(_m)!r}, expected 0.57893338569"
try:
    power_method([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
    assert False, "power_method on a non-square matrix should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Condition numbers", "code": r'''
import math as _m
from linalg import condition_number, vandermonde
assert abs(condition_number([[1.0, 0.0], [0.0, 1.0]]) - 1.0) < 1e-9, \
    f"The identity is perfectly conditioned; got {condition_number([[1.0, 0.0], [0.0, 1.0]])!r}"
_got = condition_number([[1.0, 0.0], [0.0, 2.0]])
assert abs(_got - 2.0) < 1e-8, f"diag(1, 2) has condition 2; got {_got!r}"
for _name, _a, _want in [("degree 1 on 1..4", vandermonde([1, 2, 3, 4], 1), 7.468739725928093),
                         ("degree 2 on 0..4", vandermonde([0, 1, 2, 3, 4], 2), 27.112831810234862),
                         ("degree 3 on 0..5", vandermonde([0, 1, 2, 3, 4, 5], 3), 324.4683163832041),
                         ("tall 3x2", [[12.0, -51.0], [6.0, 167.0], [-4.0, 24.0]], 12.681142753501145)]:
    _got = condition_number(_a)
    assert abs(_got - _want) / _want < 1e-6, \
        f"condition_number of the {_name} case gave {_got!r}, expected {_want!r}"
'''},
            {"name": "The Vandermonde design matrix", "code": r'''
from linalg import vandermonde
assert vandermonde([1, 2, 3], 2) == [[1.0, 1.0, 1.0], [1.0, 2.0, 4.0], [1.0, 3.0, 9.0]], \
    f"vandermonde gave {vandermonde([1, 2, 3], 2)!r}"
assert vandermonde([5, 6], 0) == [[1.0], [1.0]], f"Degree 0 gave {vandermonde([5, 6], 0)!r}"
for _args in [([1, 2, 3], -1), ([1, 2], 2)]:
    try:
        vandermonde(*_args)
        assert False, f"vandermonde{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "An exactly representable fit", "code": r'''
from linalg import vandermonde, least_squares, Fit
_xs = [0, 1, 2, 3, 4]
_ys = [2.0 - 3.0 * x + x * x for x in _xs]
_fit = least_squares(vandermonde(_xs, 2), _ys)
assert isinstance(_fit, Fit), f"least_squares returned {type(_fit).__name__}, expected Fit"
for _i, _want in enumerate([2.0, -3.0, 1.0]):
    assert abs(_fit.coefficients[_i] - _want) < 1e-9, \
        f"coefficient {_i} is {_fit.coefficients[_i]!r}, expected {_want}"
assert _fit.residual_norm < 1e-9, f"An exact fit should have residual ~0; got {_fit.residual_norm!r}"
assert _fit.rank == 3, f"rank came back as {_fit.rank!r}, expected 3"
assert abs(_fit.condition - 27.112831810234862) / 27.112831810234862 < 1e-6, \
    f"condition came back as {_fit.condition!r}, expected about 27.1128318102"
'''},
            {"name": "An over-determined fit against the closed form", "code": r'''
import math as _m
from linalg import vandermonde, least_squares
_fit = least_squares(vandermonde([1, 2, 3, 4], 1), [2, 4, 5, 8])
assert abs(_fit.coefficients[0] - 0.0) < 1e-9, \
    f"intercept is {_fit.coefficients[0]!r}, expected 0.0"
assert abs(_fit.coefficients[1] - 1.9) < 1e-9, \
    f"slope is {_fit.coefficients[1]!r}, expected 1.9"
assert abs(_fit.residual_norm - _m.sqrt(0.7)) < 1e-9, \
    f"residual norm is {_fit.residual_norm!r}, expected sqrt(0.7) = {_m.sqrt(0.7)!r}"
assert _fit.rank == 2, f"rank came back as {_fit.rank!r}, expected 2"
'''},
            {"name": "Bad fits are refused, not fudged", "code": r'''
from linalg import least_squares
try:
    least_squares([[1, 2], [2, 4], [3, 6]], [1, 2, 3])
    assert False, "A rank-deficient design matrix should raise ValueError"
except ValueError:
    pass
try:
    least_squares([[1, 0], [0, 1], [1, 1]], [1, 2])
    assert False, "A right-hand side of the wrong length should raise ValueError"
except ValueError:
    pass
try:
    least_squares([[1, 2, 3], [4, 5, 6]], [1, 2])
    assert False, "Fewer rows than columns should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The fit report", "code": r'''
from linalg import vandermonde, least_squares, fit_report
_fit = least_squares(vandermonde([1, 2, 3, 4], 1), [2, 4, 5, 8])
_rep = fit_report(_fit)
assert isinstance(_rep, str), "fit_report returns a string, it does not print"
_lines = _rep.split("\n")
assert len(_lines) == 6, f"Expected 6 lines for a 2-coefficient fit, got {len(_lines)}: {_lines!r}"
assert _lines[0].startswith("coefficients:"), f"First line was {_lines[0]!r}"
assert _lines[1].strip().startswith("c0 ="), f"Second line was {_lines[1]!r}"
assert _lines[2].strip().startswith("c1 ="), f"Third line was {_lines[2]!r}"
assert "1.9" in _lines[2], f"The slope should appear in {_lines[2]!r}"
assert _lines[3].startswith("rank"), f"Line 4 was {_lines[3]!r}"
assert _lines[3].rstrip().endswith("2"), f"The rank line should end with 2; got {_lines[3]!r}"
assert _lines[4].startswith("condition"), f"Line 5 was {_lines[4]!r}"
assert _lines[5].startswith("residual norm"), f"Line 6 was {_lines[5]!r}"
'''},
            {"name": "linalg.py is import-clean, pure and fast", "code": r'''
import time as _t
_src = open("linalg.py").read()
assert "print(" not in _src, "linalg.py defines routines; the printing belongs in main.py"
for _banned in ("numpy", "scipy"):
    assert _banned not in _src, f"linalg.py must not reach for {_banned}"
assert "random.Random(7)" in _src, "Seed the RNG with random.Random(7) so runs are reproducible"
from linalg import vandermonde, least_squares, rank, qr
_a = vandermonde([0, 1, 2, 3, 4], 2)
_before = [row[:] for row in _a]
least_squares(_a, [1.0, 2.0, 3.0, 4.0, 6.0])
rank(_a)
qr(_a)
assert _a == _before, "No routine may mutate the matrix it is given"
_start = _t.time()
for _ in range(5):
    least_squares(vandermonde([0, 1, 2, 3, 4, 5, 6], 3), [1.0, 2.0, 3.0, 4.0, 6.0, 9.0, 13.0])
_elapsed = _t.time() - _start
assert _elapsed < 5.0, f"Five fits took {_elapsed:.2f}s, which is far too slow"
'''},
        ],
    },
}
