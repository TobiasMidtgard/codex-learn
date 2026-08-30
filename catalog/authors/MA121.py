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
