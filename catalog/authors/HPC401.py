"""HPC401 — High-Performance & Parallel Computing. Author module."""

COURSE = {
    "id": "HPC401",
    "title": "High-Performance & Parallel Computing",
    "year": 4,
    "level": "Advanced",
    "prereqs": ["CE201", "CS301"],
    "stack": ["C/OpenMP (reference)", "Python"],
    "credits": 10,
    "hours": 150,
    "icon": "║",
    "summary": (
        "Performance engineering treated as a measurement discipline rather than a "
        "collection of tricks. You build a timing harness and a memory-traffic model, "
        "derive work and span for parallel primitives, enumerate every interleaving of "
        "a racy counter to prove the race exists, and count the messages a ring "
        "allreduce actually sends against its lower bound."
    ),
    "outcomes": [
        "Measure a kernel honestly: repeat, take the minimum, and report what varied",
        "Predict the memory traffic of a loop nest and explain the speedup blocking buys",
        "Derive work, span and parallelism for a task DAG and check them against an implementation",
        "Implement a work-efficient parallel scan and validate it against the sequential result",
        "Enumerate the interleavings of a small concurrent program and exhibit the race witness",
        "Cost a collective operation in messages and bytes against its theoretical bound",
        "Attribute a measured speedup to a serial fraction using Amdahl's law",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone optimisation study (60%).",
    "reading": [
        "Hennessy & Patterson, *Computer Architecture: A Quantitative Approach*, 6th ed. — chapters 1-2 and appendix B",
        "Williams, Waterman & Patterson, 'Roofline: An Insightful Visual Performance Model for Multicore Architectures', *CACM* 52(4), 2009",
        "Blelloch, 'Prefix Sums and Their Applications', CMU-CS-90-190, 1990",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Measurement and the memory hierarchy",
            "summary": "Time it before you touch it, then explain the number with a traffic model.",
            "concepts": [
                "Minimum-of-repeats beats the mean: the fastest run is the least perturbed one",
                "Timer resolution, warm-up effects, and why a single run tells you nothing",
                "The memory hierarchy: registers, L1/L2/L3, DRAM, and their bandwidth gap",
                "Loop nests have a working set; the ijk triple loop streams B once per row of A",
                "Cache blocking (tiling) trades a larger index space for a resident working set",
                "Arithmetic intensity = flops per byte moved; the roofline it implies",
                "Blocking changes the accumulation *order* of a sum, so verify equality deliberately",
            ],
            "read": [
                {
                    "title": "Time it honestly, then bill the bytes",
                    "minutes": 14,
                    "body": r'''
Take a kernel you have written, a matrix multiply say, and run it once with a stopwatch
around it. It reports 57 milliseconds. Run it again: 41. Again: 120. Again: 38. Nothing
in the code changed, and the number wandered over a factor of three. Whichever of those
four you write in your lab book, you are about to draw a conclusion from noise, and the
first job of this course is to stop you doing that.

## Where the spread comes from, and which way it points

Your process does not own the machine. Between one reading of the clock and the next, a
timer interrupt fires, the operating system runs somebody else for a quantum, a page your
matrix lives on is faulted in for the first time, the caches are still full of whatever
ran before you, and the core may still be climbing out of a low-power clock state. Every
one of those events has the same sign: none makes your code finish sooner, and each adds
time on top of what the kernel needed.

That observation decides how to summarise repeated runs. If every disturbance adds a
non-negative amount to a fixed true cost, the least disturbed run is the one with the
smallest reading, and that reading is the closest you can get to the kernel's own cost.
The mean, by contrast, is the true cost plus the *average* disturbance, which is a property
of what else your laptop was doing that afternoon, not of your code.

Here is that argument as a model you can run: a true cost fixed at 10 ms, and up to three
interruptions per run, each stealing between half a millisecond and four.

```python
import random

rng = random.Random(1)
TRUE_COST = 10.0          # milliseconds the kernel needs when nothing interferes


def one_run():
    stolen = 0.0
    for _ in range(3):                      # up to three interruptions per run
        if rng.random() < 0.5:
            stolen += rng.uniform(0.5, 4.0)
    return TRUE_COST + stolen


samples = [one_run() for _ in range(7)]
print("runs:", [round(s, 2) for s in samples])
print("mean:", round(sum(samples) / len(samples), 2))
print("min: ", round(min(samples), 2))
```

The mean lands near 13.8 ms, almost four milliseconds above the truth, because every
interruption that fired is in it. The minimum, 10.59 ms, is the one run that dodged all but
one small interruption. Even the minimum is not the true cost: it is the *least perturbed*
run, not an unperturbed one, and more repeats make it likelier that one run gets through
clean. That is the whole design of the lab's `time_best`: call the function `repeats`
times with `time.perf_counter()` read immediately before and after each call, and keep
the smallest difference. Nothing else goes inside the timed region; building the input,
printing, and the comparison that picks the best so far all sit outside it, because
anything inside is billed to the kernel.

The mistake people make is to reach for the mean because it feels statistically
respectable: it uses every sample, and it is what every physics practical taught you to
compute. That is the right summary when errors are symmetric, as likely low as high.
Timing errors are not: they have a hard floor at zero and a long tail upward, and a
summary designed for a bell curve is the wrong tool for a distribution that is all tail.

Two more things a single run cannot tell you. The first call of anything is usually the
slowest, paying for page faults and cold caches that later calls inherit warm, so the
minimum also discards the warm-up. And the clock has a resolution: the browser sandbox
this course runs in coarsens timers to around a millisecond, so a kernel that takes 200
microseconds reads as 0 or 1 ms, and the fix, which the capstone's harness uses, is to
time enough repetitions to span many ticks and divide.

## The number needs a model

Suppose the best of five for the naive multiply at $n = 64$ is 40 ms and for the blocked
one is 12 ms. A speedup of 3.3, believed on what grounds? A measurement without a model is
an anecdote: it says what happened once, on one machine. To *explain* it you need to know
what the machine was doing, and for a loop over matrices that was mostly waiting for memory.

A core can retire a multiply-add every cycle, from registers that answer in that same
cycle. Behind them sits L1, tens of kilobytes, four or so cycles away; then L2, a few
hundred kilobytes, around a dozen; then L3, megabytes shared between cores, forty-odd; and
then DRAM, gigabytes of it, two hundred cycles or more away and delivering perhaps one
double per several cycles per core. The arithmetic is not the expensive part of a matrix
multiply. The expensive part is every operand fetched across the slowest of those
boundaries, so the question to ask of a loop nest is not how many flops it does but how
many bytes it moves.

## Counting what the triple loop moves

```text
for i in range(n):
    for j in range(n):
        total = 0.0
        for p in range(n):
            total += a[i][p] * b[p][j]
        out[i][j] = total
```

Fix `i` and `j`. The inner loop reads row `i` of `A`, all $n$ elements, and column `j` of
`B`, another $n$. Now make one assumption about the cache: it holds a row of `A` and not a
great deal more. Then row `i` is fetched when `j` is 0 and is still there for every later
`j`, because nothing else from `A` is touched until `i` changes, so `A` costs $n$ elements
per `i`, $n^2$ over the run. Column `j` of `B` is different. Between its use at $(i, j)$
and its next use at $(i+1, j)$ the loop walks every *other* column of `B`, the whole
matrix, $n^2$ elements, which by assumption does not fit. Column `j` is gone when the loop
comes back for it, so `B` is streamed afresh for every $(i, j)$ pair: $n$
elements each time, $n^2$ pairs, $n^3$ in all. The output is written once, $n^2$ more.
Multiply by the element size and the naive kernel's bill is

$$\text{traffic}_{\text{naive}}(n) = e\,(n^3 + 2n^2)$$

elements of $e$ bytes. At $n = 64$ that is $262144 + 8192 = 270336$ elements, or
2,162,688 bytes. The cubic term is `B`, and it is 97% of the total.

## Tiling, and the bill it pays instead

Cut all three matrices into square tiles of side $b$. The tile of `A` at row-block `ii`,
column-block `kk`, times the tile of `B` at row-block `kk`, column-block `jj`, contributes
to the tile of `out` at `ii`, `jj`. Once those two input tiles are in the cache, $2b^2$
elements, every one of the $b^3$ multiply-adds between them finds both operands there. The
loop nest becomes `ii`, `kk`, `jj` stepping by $b$, with the same `i`, `p`, `j` loops
inside each tile triple, restricted to the tile.

There are $(n/b)^3$ tile triples and each brings in two tiles, so the inputs cost
$(n/b)^3 \cdot 2b^2 = 2n^3/b$ elements, and the output is written once as before:

$$\text{traffic}_{\text{blocked}}(n, b) = e\left(\frac{2n^3}{b} + n^2\right)$$

At $n = 64$, $b = 16$: $2 \cdot 262144 / 16 = 32768$, plus $4096$, is $36864$ elements,
or 294,912 bytes. The naive bill was 2,162,688, so the model predicts $7.33$ times less
traffic. Run the shape across several tile sizes:

```python
def traffic_naive(n, elem_bytes=8):
    return elem_bytes * (n ** 3 + 2 * n ** 2)


def traffic_blocked(n, block, elem_bytes=8):
    return elem_bytes * (2 * n ** 3 // block + n ** 2)


print(f"naive at n=64: {traffic_naive(64)} bytes")
for block in (1, 2, 4, 16, 64):
    t = traffic_blocked(64, block)
    print(f"block {block:>2}: {t:>8} bytes   naive/blocked = {traffic_naive(64) / t:.3f}")
```

Two lines of that table are worth staring at. A block of 1 moves 4,227,072 bytes, nearly
twice the naive figure, and that is the model being honest rather than broken: the naive
loop got the reuse of one row of `A` for free, and a one-element tile throws that away,
fetching `a[i][p]` again for every `j`. A block of 2 comes out at 1.015, no better than
naive, because the tile term $2n^3/b$ equals $n^3$ there; what tiling gained on `B` it gave
back on `A`. The saving is not in tiling as such but in the factor $1/b$, and only $b > 2$
comes out ahead.

How large? The two tiles must stay resident, so $2b^2 e$ bytes must fit comfortably in
the cache level you are targeting: a 32 KB L1 with 8-byte doubles allows $b \approx 45$,
and 32 is the customary choice, leaving room for the output tile. Push $b$ past that and
the tiles no longer stay resident, the assumption the count rests on fails, and the
traffic climbs back towards the naive figure. That is where this model stops holding, and
the first thing to suspect when a measured curve has a minimum where the model has none.

The model leaves things out on purpose, and you should know which. It charges the output
once, though under the `ii, kk, jj` order the output tile is revisited for every `kk`,
another $n^3/b$ term of the same shape. It counts elements, though DRAM delivers 64-byte
lines, so walking a column of a row-major `B` costs a line per element and the real naive
loop is worse than $n^3$. Its job is not to predict milliseconds but the *shape* of the
cost, a cubic term divided by $b$, so that when the measurement disagrees you know which
assumption to go and check.

## Arithmetic intensity and the roofline

Count the flops as well: one multiply and one add per term, $2n^3$ in all. Divide by the
bytes moved and you have the kernel's *arithmetic intensity*, flops per byte: $524288 /
2162688 = 0.242$ for the naive kernel at $n = 64$, and $524288 / 294912 = 1.778$, exactly
$16/9$, for the blocked one at $b = 16$.

Why that ratio matters comes straight from the hierarchy. A machine with DRAM bandwidth
$\beta$ bytes per second cannot move $M$ bytes in under $M / \beta$ seconds, so a kernel
doing $F$ flops on those bytes cannot exceed $F / (M/\beta) = \beta \cdot I$ flops per
second, where $I = F/M$ is its intensity; nor can it exceed the core's peak $\pi$. Both
ceilings apply at once:

$$\text{attainable} = \min\left(\pi,\; \beta \cdot I\right)$$

Plotted against $I$ on log axes that is a sloped line meeting a flat one, the roofline.
The corner, at $I = \pi/\beta$, is the ridge point, and a kernel to its left is bound by
memory however fast the arithmetic is.

```python
PEAK = 50.0          # GFLOP/s the cores can retire
BANDWIDTH = 10.0     # GB/s DRAM can deliver
FLOPS = 2 * 64 ** 3  # one multiply and one add per term at n = 64


def roofline(intensity):
    return min(PEAK, BANDWIDTH * intensity)


print(f"ridge point: {PEAK / BANDWIDTH:.1f} flop/byte")
for name, nbytes in (("naive", 2162688), ("blocked 16", 294912), ("blocked 64", 98304)):
    ai = FLOPS / nbytes
    print(f"{name:<11} {ai:.4f} flop/byte -> at most {roofline(ai):.2f} GFLOP/s")
```

On that machine the ridge is at 5 flop/byte. The naive kernel, at 0.24, is capped at
2.4 GFLOP/s by the memory line, and a core twice as fast would not move that number.
Blocking at 16 lifts it to 17.8, and a tile the size of the whole matrix crosses the ridge
and hits the compute roof. Blocking does not make the arithmetic faster; it slides the
kernel right along the roofline until the roof it hits is the arithmetic.

## Keeping the answer exactly the same

Blocking reorders the loops. It must not reorder the additions. `out[i][j]` is a sum
over $p$ from $0$ to $n-1$, and floating-point addition is not associative: $(x + y) + z$
and $x + (y + z)$ can differ in the last bit. If the tiled kernel adds each term straight
into `out[i][j]`, with $p$ ascending inside every `kk` tile and the tiles taken in
ascending order, the sequence of additions is the naive one exactly,
$((0 + t_0) + t_1) + t_2 \ldots$, and since $0.0 + t_0$ is $t_0$ without rounding, starting
from a zero costs nothing.

The tempting rewrite is to copy the naive inner loop into the tile as it stands: sum the
tile's terms into a local `partial` and add `partial` to `out[i][j]` afterwards. It reads
naturally and it is wrong in the last bits, because $(t_0 + t_1 + t_2 + t_3) + (t_4 +
\ldots + t_7)$ has its parentheses in different places from the running sum.

```python
import random


def matmul_naive(a, b):
    n, k, m = len(a), len(b), len(b[0])
    out = [[0.0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            total = 0.0
            for p in range(k):
                total += a[i][p] * b[p][j]
            out[i][j] = total
    return out


def matmul_tile_partials(a, b, block):
    """Tiled, but each tile is summed into its own partial first."""
    n, k, m = len(a), len(b), len(b[0])
    out = [[0.0] * m for _ in range(n)]
    for ii in range(0, n, block):
        for kk in range(0, k, block):
            for jj in range(0, m, block):
                for i in range(ii, min(ii + block, n)):
                    for j in range(jj, min(jj + block, m)):
                        partial = 0.0
                        for p in range(kk, min(kk + block, k)):
                            partial += a[i][p] * b[p][j]
                        out[i][j] += partial
    return out


rng = random.Random(7)
N = 16
A = [[rng.uniform(-1.0, 1.0) for _ in range(N)] for _ in range(N)]
B = [[rng.uniform(-1.0, 1.0) for _ in range(N)] for _ in range(N)]
want = matmul_naive(A, B)
got = matmul_tile_partials(A, B, 4)
differ = sum(1 for i in range(N) for j in range(N) if want[i][j] != got[i][j])
worst = max(abs(want[i][j] - got[i][j]) for i in range(N) for j in range(N))
print("elements that differ:", differ, "of", N * N)
print("largest difference:", worst)
```

More than half the elements differ, by under $10^{-15}$. Nobody would notice in a plot,
and that is the danger: a result that is *almost* the same cannot serve as a check,
because you can no longer tell a reordered sum from a small indexing bug. The lab compares
the two results with `==` on the lists, equality and not tolerance, on purpose.

## What you are about to build

The lab, *Blocked matrix multiply and its traffic model*, asks for the harness, both
kernels and the model beside them: `time_best` reporting the minimum of repeats,
`matmul_naive` and `matmul_blocked` agreeing bit for bit for every tile size, including
ones that do not divide $n$, and `traffic_naive`, `traffic_blocked` and
`arithmetic_intensity` reproducing 2,162,688, 294,912 and 1.7778 to the byte and the
fourth decimal. The timings you see in the browser will be small and noisy, and that is
fine; the model is where the exact numbers live.
''',
                },
            ],
            "quiz": {
                "title": "What the number means",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"Five timed runs of the same kernel on the same input give 41, 38, 57, 39 and 120 ms. Which single number belongs in the report?",
                        "opts": [
                            "The mean, 59 ms, because it accounts for every run and is what a user sees on average",
                            "The median, 41 ms, because it is robust to the one outlier at 120 ms",
                            "The minimum, 38 ms, because interference only ever adds time to a run",
                            "The last run, 39 ms, because by then the caches are warm and the earlier runs are not",
                        ],
                        "a": 2,
                        "whys": [
                            r"The mean is the true cost plus the average interruption, and that average describes what else the machine was doing, not the kernel; 59 ms is over half again the fastest observed run, all of it noise.",
                            r"Robustness to outliers is the right instinct but the wrong statistic: every run is an outlier upward to some degree, and the median still carries whatever interference the middle run suffered.",
                            r"Perturbations have a floor at zero and no ceiling, so the least perturbed run is the smallest reading.",
                            r"Warm-up is real, which is why the first run is often slow, but nothing makes the last run special: the 120 ms run could as easily have been the fifth as the third.",
                        ],
                        "why": r"""
Every interruption a run suffers adds to its time and none subtracts, so the run with
the smallest reading is the one that was disturbed least, and 38 ms is the closest
you can get to the kernel's own cost from these five. The mean feels more rigorous
because it uses every sample, but it is designed for symmetric errors, and timing
errors are all tail on one side. The median is closer to right and still wrong for
the same reason. That is why the lab's `time_best` keeps the minimum.
""",
                    },
                    {
                        "q": r"In the traffic model for the `i, j, p` triple loop, `A` is charged $n^2$ element loads and `B` is charged $n^3$, though both matrices are the same size. What justifies the difference?",
                        "opts": [
                            "Row $i$ of `A` stays resident across every $j$, but column $j$ of `B` is walked afresh for each $(i, j)$ pair",
                            "`A` is the left operand and is fetched into registers, while `B` is the right operand and must come from DRAM",
                            "A column of `B` costs $n$ times a row of `A` on any hardware, because columns are strided in memory",
                            "The loop reads `B` inside the loop over `A`, so the model charges the inner operand for every outer iteration",
                        ],
                        "a": 0,
                        "whys": [
                            r"Between two uses of row $i$ nothing else from `A` is touched; between two uses of column $j$ the loop walks the whole of `B`.",
                            r"Left and right have no meaning to the cache: both operands are fetched by address, and the asymmetry is entirely in the order the loop revisits them.",
                            r"Striding costs cache lines, not the element count this model uses; that is a real effect the model deliberately ignores, and it is not the reason for the $n^3$.",
                            r"Both operands are read in the innermost loop, once per term; what differs is what the cache still holds when each is read the next time.",
                        ],
                        "why": r"""
The model assumes the cache holds about one row of `A`. Row $i$ is used for every $j$
in turn with nothing from `A` in between, so it is loaded once per $i$: $n^2$ total.
Column $j$ of `B` is used at $(i, j)$ and next at $(i+1, j)$, and in between the loop
has walked all the other columns, the whole matrix, which does not fit. So column $j$
is streamed again for every pair, $n$ elements times $n^2$ pairs. Column striding
makes the real cost even higher, but through cache lines, which this model does not
count.
""",
                    },
                    {
                        "q": r"For $n = 8$ the model gives `traffic_naive(8)` as 5120 bytes and `traffic_blocked(8, 2)` as 4608, a saving of barely 10%, where $n = 64$ with $b = 16$ saved a factor of 7.3. Why does a block of 2 do so little?",
                        "opts": [
                            "Blocking only pays once the matrix is larger than the cache, and an 8 by 8 matrix of doubles already fits in L1 with room to spare",
                            "At $b = 2$ the tile term $2n^3/b$ equals the naive $n^3$: the gain on `B` is cancelled by re-fetching `A`",
                            "The $n^2$ output term dominates at small $n$, and no amount of tiling can reduce the output traffic",
                            "Tiles of side 2 spend most of their loads on tile boundaries, which the model charges as extra traffic",
                        ],
                        "a": 1,
                        "whys": [
                            r"The model has no cache size in it at all; it assumes one row and one tile stay resident whatever $n$ is, so fitting in L1 cannot be what it is expressing.",
                            r"$2 \cdot 512 / 2 = 512 = 8^3$: the cubic terms are identical, and the whole 10% is the $2n^2$ becoming $n^2$.",
                            r"The output term did shrink, from $2n^2$ to $n^2$, and that is the entire saving; the cubic terms are what failed to move.",
                            r"The model has no notion of boundaries; it charges $2b^2$ per tile triple regardless, and the clamping with `min` in the lab changes nothing in the count.",
                        ],
                        "why": r"""
Write the two bills out: naive is $n^3 + 2n^2 = 512 + 128 = 640$ elements, blocked at
$b = 2$ is $2n^3/b + n^2 = 512 + 64 = 576$. The cubic terms are equal, because
fetching two $2 \times 2$ tiles per tile triple costs exactly what streaming `B` cost
before, while giving up the row reuse of `A` the naive loop had for free. Only $b > 2$
makes $2n^3/b$ smaller than $n^3$, and $b = 1$ is worse than not tiling at all. The
saving is the $1/b$, not the act of tiling.
""",
                    },
                    {
                        "q": r"Your blocked kernel agrees with the naive one to within $10^{-15}$ on every element but not exactly, and the lab's equality test fails. Which change to the tiled inner loops is the most likely cause?",
                        "opts": [
                            "Each tile's terms are summed into a local partial before being added to `out[i][j]`, which regroups the reduction",
                            "The product `a[i][p] * b[p][j]` was written the other way round, and floating-point multiplication is not commutative",
                            "The output was initialised to `0.0` and accumulated into, and `0.0 + x` rounds differently from starting at `x`",
                            "The tile bounds were clamped with `min` at the matrix edge, and the partial tiles along that edge are computed at reduced precision",
                        ],
                        "a": 0,
                        "whys": [
                            r"$(t_0 + \ldots + t_3) + (t_4 + \ldots + t_7)$ is a different sequence of roundings from the running sum, and different in the last bit is different.",
                            r"IEEE multiplication is exactly commutative; $x \cdot y$ and $y \cdot x$ round to the same double, so operand order in a product cannot be the cause.",
                            r"$0.0 + x$ is $x$ exactly for every finite double; a running sum started from zero follows the naive sequence bit for bit.",
                            r"Clamping changes which indices a tile covers, never the arithmetic performed on them; every term is still a double product added to a double.",
                        ],
                        "why": r"""
Floating-point addition is not associative, so what has to match is the sequence of
additions, not the set of terms. Accumulating every term directly into `out[i][j]` with
$p$ ascending reproduces the naive running sum exactly; a per-tile partial groups the
terms differently and the last bits move. Multiplication order and a zero start are
both exact, and clamping affects only which elements a tile touches. The lab compares
with `==` because a difference of $10^{-15}$ is the fingerprint of this rewrite.
""",
                    },
                    {
                        "q": r"A machine has a 40 GFLOP/s peak and 8 GB/s of DRAM bandwidth. A kernel with an arithmetic intensity of 1.78 flop/byte measures 14 GFLOP/s on it. The cores are replaced with ones twice as fast, 80 GFLOP/s peak, and nothing else changes. What happens to the kernel?",
                        "opts": [
                            "It roughly doubles to 28 GFLOP/s, since the arithmetic that was taking the time now runs twice as quickly",
                            r"It stays at about 14 GFLOP/s: $8 \times 1.78 = 14.2$ is the memory ceiling and it was already there",
                            "It rises to 40 GFLOP/s, because the old peak was the ceiling and the new peak is well clear of it",
                            "It slows down, because faster cores issue loads faster than the same DRAM can serve them",
                        ],
                        "a": 1,
                        "whys": [
                            r"The arithmetic was not taking the time; at 1.78 flop/byte the kernel spends its time waiting on 8 GB/s of memory, and faster cores wait faster.",
                            r"The ridge point is $40/8 = 5$ flop/byte and the kernel sits well left of it, on the sloped part of the roofline where only bandwidth or intensity moves the number.",
                            r"The old peak was never the ceiling: $8 \times 1.78$ is 14.2, which is where the kernel measured, so it was bandwidth-bound already.",
                            r"Cores that issue loads faster do not make DRAM deliver fewer bytes per second; the kernel is limited by bandwidth, and bandwidth is unchanged, so the throughput is too.",
                        ],
                        "why": r"""
Attainable throughput is $\min(\pi, \beta I)$. With $\beta = 8$ GB/s and $I = 1.78$
the memory ceiling is 14.2 GFLOP/s, and the measurement sits on it, so the kernel is
bound by bandwidth, not by the cores. Doubling $\pi$ raises the flat roof from 40 to 80
and leaves the sloped part untouched, so the kernel does not move. To use those faster
cores the intensity must rise past the new ridge at 10 flop/byte, which in this module
means a larger tile, not a faster chip.
""",
                    },
                    {
                        "q": r"`traffic_blocked(64, 1)` returns 4,227,072 bytes, nearly twice `traffic_naive(64)`. What is the model saying about a tile of one element?",
                        "opts": [
                            "The model breaks down at $b = 1$, and the lab should special-case that block size to return the naive figure instead",
                            "Tiny tiles thrash the cache's replacement policy, and the model is charging for that thrashing",
                            "A one-element tile re-fetches `a[i][p]` for every `j`, giving up the row reuse the naive loop had for free",
                            "The output term doubles at $b = 1$ because each element of `out` is written once per tile it belongs to",
                        ],
                        "a": 2,
                        "whys": [
                            r"The model is right at $b = 1$, and that is the point: a tiling that discards the reuse the plain loop already had really does move more, and hiding that would hide a true prediction.",
                            r"There is no replacement policy in the model; it counts what each tile triple fetches under the assumption that the tiles fit, and at $b = 1$ they do, trivially.",
                            r"$(n/b)^3 \cdot 2b^2 = 2n^3$ at $b = 1$: both operands are streamed for every term, where the naive loop streamed only `B`.",
                            r"The output is charged $n^2$ at every $b$ in this model, including 1; the extra $2n^3$ comes entirely from the two input tiles.",
                        ],
                        "why": r"""
The tile term is $2n^3/b$, and at $b = 1$ it is $2n^3$: every term now fetches both of
its operands, where the naive loop fetched only the `B` element and found the `A`
element still in cache from the previous $j$. Tiling is not free; it trades the
naive loop's one kind of reuse for a different kind that only pays once $b$ exceeds
2. The lab's test asserts this figure deliberately, so that a `traffic_blocked` that
quietly clamps or special-cases small blocks is caught.
""",
                    },
                ],
            },
            "lab": {
                "title": "Blocked matrix multiply and its traffic model",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Nothing in this course is allowed to be believed without a measurement and a
model that agrees with it. This lab builds both.

## The harness

**`time_best(fn, repeats=5)`** calls `fn()` `repeats` times and returns
`(last_result, best_seconds)` — the *minimum* elapsed time, using
`time.perf_counter()`. `repeats` below 1 raises `ValueError`.

## The kernels

Matrices are lists of rows of floats.

**`matmul_naive(a, b)`** — the textbook `i, j, k` triple loop. For each output
element accumulate `total += a[i][p] * b[p][j]` for `p` ascending, then store.
Mismatched inner dimensions raise `ValueError`; an empty `a` gives `[]`.

**`matmul_blocked(a, b, block)`** — the same product, computed over tiles.
Loop `ii`, `kk`, `jj` in steps of `block`, then the three inner loops inside the
tile, accumulating into `out[i][j]`. `block` below 1 raises `ValueError`; a
`block` that does not divide the matrix must still work (clamp the tile end with
`min`).

Because both versions accumulate over `p` in ascending order, they must agree
**exactly** — not approximately. If your results differ in the last bits you
have reordered the sum somewhere.

## The model

Count elements moved between DRAM and cache, assuming one row of `A` and one
tile stay resident.

```text
traffic_naive(n)          ->  elem_bytes * (n**3 + 2 * n**2)
traffic_blocked(n, block) ->  elem_bytes * (2 * n**3 // block + n**2)
```

`traffic_blocked` raises `ValueError` unless `block >= 1` and `block` divides
`n` — the model is only stated for the exact case.

**`arithmetic_intensity(n, block, elem_bytes=8)`** returns the blocked kernel's
flops per byte, counting `2 * n**3` flops (one multiply and one add per term).

```text
traffic_naive(64)            -> 2162688 bytes
traffic_blocked(64, 16)      ->  294912 bytes   (7.33x less)
arithmetic_intensity(64, 16) -> 1.7778 flop/byte
```
''',
                "files": [{"name": "main.py", "content": r'''
import random
import time


def time_best(fn, repeats=5):
    """Run fn repeats times; return (last result, best elapsed seconds)."""
    # your code here


def matmul_naive(a, b):
    """Textbook i, j, k triple loop."""
    # your code here


def matmul_blocked(a, b, block):
    """The same product, accumulated tile by tile."""
    # your code here


def traffic_naive(n, elem_bytes=8):
    """Modelled bytes moved by the naive n x n kernel."""
    # your code here


def traffic_blocked(n, block, elem_bytes=8):
    """Modelled bytes moved by the blocked n x n kernel."""
    # your code here


def arithmetic_intensity(n, block, elem_bytes=8):
    """Flops per byte for the blocked kernel."""
    # your code here


rng = random.Random(7)
N = 32
A = [[rng.uniform(-1.0, 1.0) for _ in range(N)] for _ in range(N)]
B = [[rng.uniform(-1.0, 1.0) for _ in range(N)] for _ in range(N)]

naive, t_naive = time_best(lambda: matmul_naive(A, B), 3)
blocked, t_blocked = time_best(lambda: matmul_blocked(A, B, 8), 3)
print("identical:", naive == blocked)
print(f"traffic ratio at n=64, b=16: {traffic_naive(64) / traffic_blocked(64, 16):.3f}")
print(f"arithmetic intensity: {arithmetic_intensity(64, 16):.4f} flop/byte")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import random
import time


def time_best(fn, repeats=5):
    """Run fn repeats times; return (last result, best elapsed seconds)."""
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    best = None
    result = None
    for _ in range(repeats):
        start = time.perf_counter()
        result = fn()
        elapsed = time.perf_counter() - start
        if best is None or elapsed < best:
            best = elapsed
    return result, best


def matmul_naive(a, b):
    """Textbook i, j, k triple loop."""
    n = len(a)
    if n == 0:
        return []
    k = len(a[0])
    if len(b) != k:
        raise ValueError(f"inner dimensions disagree: {k} vs {len(b)}")
    m = len(b[0])
    out = [[0.0] * m for _ in range(n)]
    for i in range(n):
        row = a[i]
        out_i = out[i]
        for j in range(m):
            total = 0.0
            for p in range(k):
                total += row[p] * b[p][j]
            out_i[j] = total
    return out


def matmul_blocked(a, b, block):
    """The same product, accumulated tile by tile."""
    if block < 1:
        raise ValueError("block must be at least 1")
    n = len(a)
    if n == 0:
        return []
    k = len(a[0])
    if len(b) != k:
        raise ValueError(f"inner dimensions disagree: {k} vs {len(b)}")
    m = len(b[0])
    out = [[0.0] * m for _ in range(n)]
    for ii in range(0, n, block):
        i_end = min(ii + block, n)
        for kk in range(0, k, block):
            k_end = min(kk + block, k)
            for jj in range(0, m, block):
                j_end = min(jj + block, m)
                for i in range(ii, i_end):
                    row = a[i]
                    out_i = out[i]
                    for p in range(kk, k_end):
                        aip = row[p]
                        b_p = b[p]
                        for j in range(jj, j_end):
                            out_i[j] += aip * b_p[j]
    return out


def traffic_naive(n, elem_bytes=8):
    """Modelled bytes moved by the naive n x n kernel."""
    return elem_bytes * (n ** 3 + 2 * n * n)


def traffic_blocked(n, block, elem_bytes=8):
    """Modelled bytes moved by the blocked n x n kernel."""
    if block < 1:
        raise ValueError("block must be at least 1")
    if n % block:
        raise ValueError(f"block {block} does not divide n={n}")
    return elem_bytes * (2 * n ** 3 // block + n * n)


def arithmetic_intensity(n, block, elem_bytes=8):
    """Flops per byte for the blocked kernel."""
    return 2 * n ** 3 / traffic_blocked(n, block, elem_bytes)


rng = random.Random(7)
N = 32
A = [[rng.uniform(-1.0, 1.0) for _ in range(N)] for _ in range(N)]
B = [[rng.uniform(-1.0, 1.0) for _ in range(N)] for _ in range(N)]

naive, t_naive = time_best(lambda: matmul_naive(A, B), 3)
blocked, t_blocked = time_best(lambda: matmul_blocked(A, B, 8), 3)
print("identical:", naive == blocked)
print(f"traffic ratio at n=64, b=16: {traffic_naive(64) / traffic_blocked(64, 16):.3f}")
print(f"arithmetic intensity: {arithmetic_intensity(64, 16):.4f} flop/byte")
'''}],
                "hints": [
                    "`time_best` needs `start = time.perf_counter()` immediately before the call and the subtraction immediately after — nothing else between them.",
                    "The blocked loops are `for ii in range(0, n, block)` with `i_end = min(ii + block, n)`; the inner `for i in range(ii, i_end)` then never runs off the end.",
                    "Keep `kk` outside `jj`. That way `p` still ascends 0, 1, 2, ... across the whole reduction, so the floating-point sum matches the naive one bit for bit.",
                    "The traffic model is arithmetic, not a loop: `n**3 + 2*n**2` elements for the naive kernel, `2*n**3//block + n**2` for the blocked one.",
                ],
                "tests": [
                    {"name": "time_best repeats and reports the minimum", "code": r'''
_calls = []
def _work():
    _calls.append(1)
    return sum(range(1000))
_r, _s = time_best(_work, 4)
assert len(_calls) == 4, f"time_best called fn {len(_calls)} times, expected 4"
assert _r == 499500, f"time_best returned {_r!r}, expected the function result 499500"
assert isinstance(_s, float) and _s >= 0.0, f"elapsed was {_s!r}, expected a non-negative float"
try:
    time_best(_work, 0)
    assert False, "time_best(fn, 0) should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "matmul_naive computes the product", "code": r'''
_got = matmul_naive([[1.0, 2.0], [3.0, 4.0]], [[5.0, 6.0], [7.0, 8.0]])
assert _got == [[19.0, 22.0], [43.0, 50.0]], f"2x2 product gave {_got!r}"
_got = matmul_naive([[1.0, 2.0, 3.0]], [[1.0], [2.0], [3.0]])
assert _got == [[14.0]], f"1x3 by 3x1 gave {_got!r}, expected [[14.0]]"
assert matmul_naive([], []) == [], "An empty left matrix gives []"
'''},
                    {"name": "matmul_blocked agrees exactly for every block size", "code": r'''
import random as _random
_rng = _random.Random(11)
_a = [[_rng.uniform(-1.0, 1.0) for _ in range(7)] for _ in range(7)]
_b = [[_rng.uniform(-1.0, 1.0) for _ in range(7)] for _ in range(7)]
_want = matmul_naive(_a, _b)
for _blk in (1, 2, 3, 7, 9):
    _got = matmul_blocked(_a, _b, _blk)
    assert _got == _want, f"matmul_blocked(a, b, {_blk}) differs from the naive product"
_a32 = [[_rng.uniform(-1.0, 1.0) for _ in range(32)] for _ in range(32)]
_b32 = [[_rng.uniform(-1.0, 1.0) for _ in range(32)] for _ in range(32)]
assert matmul_blocked(_a32, _b32, 8) == matmul_naive(_a32, _b32), \
    "At n=32 the blocked result must be bit-for-bit identical, not merely close"
'''},
                    {"name": "Both kernels reject bad shapes", "code": r'''
try:
    matmul_naive([[1.0, 2.0]], [[1.0, 2.0]])
    assert False, "matmul_naive should raise ValueError when the inner dimensions disagree"
except ValueError:
    pass
try:
    matmul_blocked([[1.0, 2.0]], [[1.0, 2.0]], 2)
    assert False, "matmul_blocked should raise ValueError when the inner dimensions disagree"
except ValueError:
    pass
for _bad in (0, -4):
    try:
        matmul_blocked([[1.0]], [[1.0]], _bad)
        assert False, f"matmul_blocked with block={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The traffic model matches the derivation", "code": r'''
assert traffic_naive(64) == 2162688, f"traffic_naive(64) gave {traffic_naive(64)!r}, expected 2162688"
assert traffic_naive(8) == 5120, f"traffic_naive(8) gave {traffic_naive(8)!r}, expected 5120"
assert traffic_naive(8, 4) == 2560, f"traffic_naive(8, 4) gave {traffic_naive(8, 4)!r}, expected 2560"
assert traffic_blocked(64, 16) == 294912, \
    f"traffic_blocked(64, 16) gave {traffic_blocked(64, 16)!r}, expected 294912"
assert traffic_blocked(8, 2) == 4608, \
    f"traffic_blocked(8, 2) gave {traffic_blocked(8, 2)!r}, expected 4608"
assert traffic_blocked(64, 1) == 4227072, \
    f"traffic_blocked(64, 1) gave {traffic_blocked(64, 1)!r}, expected 4227072 (a tile of one element moves more than no tiling at all)"
'''},
                    {"name": "traffic_blocked refuses a block that does not divide n", "code": r'''
for _bad in (0, -2):
    try:
        traffic_blocked(64, _bad)
        assert False, f"traffic_blocked(64, {_bad}) should raise ValueError"
    except ValueError:
        pass
try:
    traffic_blocked(64, 7)
    assert False, "traffic_blocked(64, 7) should raise ValueError — 7 does not divide 64"
except ValueError:
    pass
'''},
                    {"name": "Arithmetic intensity and the reported ratio", "code": r'''
_ai = arithmetic_intensity(64, 16)
assert abs(_ai - 16 / 9) < 1e-12, f"arithmetic_intensity(64, 16) gave {_ai!r}, expected 1.7777777777777777"
_ratio = traffic_naive(64) / traffic_blocked(64, 16)
assert abs(_ratio - 22 / 3) < 1e-12, f"traffic ratio was {_ratio!r}, expected 7.333333333333333"
assert "identical: True" in _out, "main.py should report that the two kernels agree exactly"
assert "1.7778 flop/byte" in _out, "main.py should print the arithmetic intensity to 4 decimals"
'''},
                    {"name": "matmul_blocked does its own loops", "code": r'''
_src = open("main.py").read()
_start = _src.index("def matmul_blocked")
_rest = _src[_start:]
_end = _rest.find(chr(10) + "def ", 1)
_body = _rest if _end == -1 else _rest[:_end]
assert "matmul_naive" not in _body, "matmul_blocked must run its own tiled loop nest, not delegate to matmul_naive"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Work, span and the parallel scan",
            "summary": "Cost a computation as a DAG, then build the work-efficient scan.",
            "concepts": [
                "A parallel computation is a DAG: work T1 = total nodes, span T-infinity = longest path",
                "Parallelism = T1 / T-infinity; it caps the speedup no matter how many workers you buy",
                "Brent's theorem: T_p <= T1/p + T-infinity, so p beyond the parallelism is wasted",
                "Tree reduction: n-1 operations in ceil(log2 n) depth, for any associative operator",
                "A naive scan is O(n log n) work; Blelloch's up-sweep/down-sweep is O(n), hence 'work-efficient'",
                "The identity element is what lets you pad to a power of two without changing the answer",
                "Associativity is required; commutativity is not — the reduction order must stay left to right",
            ],
            "read": [
                {
                    "title": "Work, span, and the scan that wastes neither",
                    "minutes": 14,
                    "body": r'''
Eight numbers on a whiteboard, and eight people who can each do one addition per minute.
One person adds them in seven minutes: seven additions, one after another. Eight people
pair the numbers up and add four pairs in the first minute, two in the second, one in the
third. Three minutes. But count the additions: four, then two, then one, is still seven.
Nobody did less work. The work was the same and it was *spread*, and the thing that
shrank was something else, which needs its own name.

## The DAG, and its two numbers

Write each addition as a node and draw an edge from every node to the node that consumes
its result. Reduction of eight numbers gives this:

```text
level 1:   (x0+x1)   (x2+x3)   (x4+x5)   (x6+x7)        4 nodes
level 2:      (  +  )             (  +  )              2 nodes
level 3:               (    +    )                     1 node
```

The **work** $T_1$ is the number of nodes, seven, and it is what one worker takes: the
subscript is the worker count. The **span** $T_\infty$ is the length of the longest path
from an input to the result, three, and it is what infinitely many workers would take,
because no worker can start a node before the node it depends on has finished. Every
parallel computation has this shape once you look at it as data dependencies rather than
as code, and the two numbers between them say most of what there is to say about it.

Work does not care how the tree is shaped. Every addition merges two values into one, and
getting from $n$ values down to one takes exactly $n - 1$ merges, however you pair them.
Span does care. Pair adjacent elements and carry an odd leftover to the next level, and
five elements go to three, then two, then one: four additions in three levels. A hundred
elements take 99 additions in seven levels, because $2^7 = 128$ is the first power of two
at or above 100: the span of a balanced tree is $\lceil \log_2 n \rceil$.

The ratio $T_1 / T_\infty$ is the **parallelism**. It is the average width of the DAG,
and therefore the largest number of workers that could be kept busy on average. For the
tree on eight numbers it is $7/3 \approx 2.33$: give it three workers and one of them will
spend most of the time idle, because level 3 has one node in it.

## Brent's bound, derived rather than quoted

Now give the DAG $p$ workers and a greedy scheduler: at each step, every node whose inputs
are ready runs if a worker is free. How long does it take? Sort the steps into two kinds.
A step is *complete* if all $p$ workers were busy; it consumed $p$ units of work, so there
can be at most $T_1 / p$ complete steps. A step is *incomplete* if some worker sat idle;
that can only happen because every ready node was already running, and then every node at
the head of the longest remaining path ran, so the remaining span fell by one. There can
be at most $T_\infty$ incomplete steps. Add the two kinds:

$$T_p \;\le\; \frac{T_1}{p} + T_\infty$$

That is Brent's bound, and it is an upper bound on a greedy schedule, not a prediction.
The floor is $\max(T_1/p,\, T_\infty)$, because the work has to be done and the longest
path has to be walked. For the scan you will build on eight elements, work 14 and span 6,
four workers give at most $14/4 + 6 = 9.5$ steps, against a floor of 6.

```python
def brent_bound(work, span, workers):
    return work / workers + span


work, span = 2046, 20        # the Blelloch DAG for 1000 elements, padded to 1024
print(f"parallelism: {work / span:.1f}")
for p in (1, 2, 8, 32, 102, 1024):
    bound = brent_bound(work, span, p)
    print(f"{p:>5} workers: at most {bound:>7.1f} steps, "
          f"speedup at least {work / bound:5.1f}x")
```

Read the table from the bottom. A thousand and twenty-four workers guarantee at most 22
steps; a hundred and two guarantee about 40. Ten times the hardware for a factor of under two,
and the span of 20 is where it stops, forever. Once $p$ passes the parallelism, the
$T_1/p$ term is smaller than $T_\infty$ and further workers are buying almost nothing.
The mistake people make is to read a speedup curve as a hardware problem, and to keep
adding cores; the curve was drawn by the DAG before any core was bought.

## Prefix sums, and a scan that costs too much

A **scan** turns a list into its running totals. The exclusive form, which the lab uses,
puts at position $i$ the fold of everything strictly before it, so `[1, 2, 3, 4]` scans to
`[0, 1, 3, 6]`. Sequentially it is one loop with an accumulator, $n - 1$ additions and a
span of $n - 1$: no parallelism at all. Every element depends on the one before it.

The first parallel scan most people invent breaks that chain by having every element add
the element a stride to its left, doubling the stride each level:

```python
def hillis_steele(values):
    """Inclusive scan: every element adds the one `stride` to its left."""
    buf = list(values)
    work = span = 0
    stride = 1
    while stride < len(buf):
        buf = [buf[i] + buf[i - stride] if i >= stride else buf[i]
               for i in range(len(buf))]
        work += len(buf) - stride
        span += 1
        stride *= 2
    return buf, work, span


result, work, span = hillis_steele([1, 2, 3, 4, 5, 6, 7, 8])
print("inclusive scan:", result, "work:", work, "span:", span)
for n in (8, 1024, 1 << 20):
    lg = n.bit_length() - 1
    print(f"n={n:>8}: Hillis-Steele work {n * lg - (n - 1):>10}   "
          f"Blelloch work {2 * (n - 1):>8}   spans {lg} vs {2 * lg}")
```

Three levels for eight elements, a span of $\log_2 n$, which is as short as a scan can be.
But look at the work: each level does nearly $n$ additions, so the total is about
$n \log_2 n$, and at a million elements that is twenty million additions for a job the
sequential loop does in one million. Ten workers running this are slower than one worker
running the loop. A parallel algorithm that does asymptotically more work than the
sequential one is not *work-efficient*, and it means the parallelism you paid for is
being spent on redundant additions.

## Blelloch's scan, traced

The fix is to do the reduction tree in place and then send prefix information back down
the same tree. Take `[1, 2, 3, 4, 5, 6, 7, 8]`. The **up-sweep** is the tree from the top
of this reading, written into the buffer at the right-hand slot of each pair. With
`stride` doubling from 1, every index $i$ of the form $2s - 1, 4s - 1, \ldots$ does
`buf[i] = buf[i - stride] + buf[i]`:

```text
start:      [1, 2, 3, 4, 5, 6, 7, 8]
stride 1:   [1, 3, 3, 7, 5, 11, 7, 15]     four additions
stride 2:   [1, 3, 3, 10, 5, 11, 7, 26]    two additions
stride 4:   [1, 3, 3, 10, 5, 11, 7, 36]    one addition: the total
```

Slot 7 holds the sum of everything, slot 3 the sum of the first four, slot 5 the sum of
elements 4 and 5, and so on: each right-hand slot holds the sum of the subtree it roots.
Now overwrite the last slot with the identity, 0, and run the **down-sweep** with the
stride halving. At each node the left child receives the parent's value and the parent
receives the *old* left child added to the parent's value:

```text
zero the root:  [1, 3, 3, 10, 5, 11, 7, 0]
stride 4:       [1, 3, 3, 0, 5, 11, 7, 10]       left <- 0, right <- 10 + 0
stride 2:       [1, 0, 3, 3, 5, 10, 7, 21]       two nodes
stride 1:       [0, 1, 3, 6, 10, 15, 21, 28]     four nodes
```

That last line is the exclusive scan of 1 to 8. Why it works is one invariant: at every
moment of the down-sweep, a node's slot holds the sum of everything to the *left of its
whole subtree*. The root's subtree is everything, so it starts at 0. A left child has
nothing to its left beyond what its parent had, so it inherits the parent's value. A right
child has, to its left, everything the parent had plus the left sibling's subtree, and the
left sibling's subtree sum is exactly what the up-sweep left in that slot, which is why it
has to be read before it is overwritten. Get that order wrong, writing the left child
before saving it, and the right child receives the parent twice.

Count the DAG. The up-sweep does $4 + 2 + 1 = 7$ additions in three levels; the down-sweep
does $1 + 2 + 4 = 7$ in three more. For a buffer of $m$ elements, a power of two, that is
$2(m - 1)$ work and $2 \log_2 m$ span. The work is twice the sequential loop's, a constant
factor, and the span is only twice Hillis-Steele's. That is the trade, and it is a good
one wherever workers are scarcer than elements.

For a length that is not a power of two, pad. The identity is the element that changes
nothing when combined, so appending it to the input changes no prefix, and the scan of the
padded buffer, trimmed back to $n$, is the scan of the original. A thousand elements pad to
1024: work $2 \cdot 1023 = 2046$, span 20, parallelism 102.3, which are the numbers the
lab's `scan_cost` and your instrumented `blelloch_scan` must agree on exactly.

## Where the trade reverses

Work-efficient is not a synonym for faster. Put both scans on a machine with as many
workers as elements: a GPU with 4096 threads on 4096 elements. Then $T_1 / p$ is a few
steps for either algorithm and the span decides, and Hillis-Steele's span of 12 beats
Blelloch's 24. The choice depends on whether $p$ or $n$ is the scarce resource, and the
DAG, not the algorithm's reputation, is what tells you. In practice large scans are done in
three phases, each worker scanning a contiguous chunk sequentially, a small parallel scan
of the chunk totals, and a second sequential pass to add the offsets in, which keeps the
work at about $2n$ and the memory traffic of module 1 in mind.

The DAG model has its own limits. It charges every node one unit, but a level in a real
implementation is a barrier where every worker waits for the slowest, and a barrier costs
more than an addition. It ignores where the data lives, and a scan moves every element
twice, so on real hardware it is bandwidth-bound long before it is span-bound. Brent's
bound tells you what the dependencies allow; it does not promise the machine will get
there.

## Associative, but not necessarily commutative

The tree needs one property of the operator: associativity, so that $(x + y) + z$ equals
$x + (y + z)$ and the grouping the tree imposes does not change the answer. It does not
need commutativity, provided every node combines its *left* input with its *right* input
in that order. The lab checks this with string concatenation, which is associative but
not commutative:

```python
def tree(values, op):
    level = list(values)
    while len(level) > 1:
        nxt = [op(level[i], level[i + 1]) for i in range(0, len(level) - 1, 2)]
        if len(level) % 2:
            nxt.append(level[-1])
        level = nxt
    return level[0]


def tree_swapped(values, op):
    """The same tree, but every node applies op to (right, left)."""
    level = list(values)
    while len(level) > 1:
        nxt = [op(level[i + 1], level[i]) for i in range(0, len(level) - 1, 2)]
        if len(level) % 2:
            nxt.append(level[-1])
        level = nxt
    return level[0]


def fold(values, op, identity):
    acc = identity
    for v in values:
        acc = op(acc, v)
    return acc


concat = lambda x, y: x + y
words = ["par", "allel", "is", "m"]
print("fold:        ", fold(words, concat, ""))
print("tree:        ", tree(words, concat))
print("tree swapped:", tree_swapped(words, concat))

floats = [1e16, 1.0, -1e16, 1.0]
print("fold of floats:", fold(floats, concat, 0.0))
print("tree of floats:", tree(floats, concat))
```

The swapped tree spells `misallelpar`, and integer addition would never have told you the
tree was swapping its operands. The last two lines show the other edge. Floating-point
addition is *not* associative: the fold computes $((10^{16} + 1) - 10^{16}) + 1$, where
$10^{16} + 1$ rounds to $10^{16}$, and gets 1.0; the tree computes $(10^{16} + 1) +
(-10^{16} + 1)$ and gets 0.0. Neither is wrong; they are different roundings of the same
sum. So the lab's demand that `blelloch_scan` equal `sequential_scan` *exactly* is a
demand you can only make of integers, or of any operator that is associative on the nose.
For floats the honest check is a tolerance, and a tree sum is often the more accurate of
the two.

The identity is the other thing to be careful with. `max` with identity 0 is fine on the
lab's non-negative data; on `[-3, -1, -4]` the padding and the leading 0 of the exclusive
scan are both wrong, because 0 is not the identity of `max` over the reals. The identity
of `max` is $-\infty$, and an operator without an identity, or with one you have guessed,
cannot be padded or scanned this way at all.

## What you are about to build

The lab, *Blelloch scan as a task DAG*, runs everything sequentially and counts. You
write `next_power_of_two`, then `reduce_tree` returning its value with its own work and
span, `sequential_scan` as the reference, and `blelloch_scan` with the up-sweep and
down-sweep instrumented so that `scan_cost` reproduces its counts exactly at every $n$;
then `parallelism` and `brent_bound` to read the numbers off. The result on 1000 random
integers must equal the sequential scan, and the stats must read work 2046 and span 20.
''',
                },
            ],
            "quiz": {
                "title": "Counting the DAG",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"A DAG has work 1000 and span 50. Brent's bound for 8 workers is $1000/8 + 50 = 175$ steps; a colleague says the answer is $1000/8 = 125$. Who is right about how long a greedy schedule takes?",
                        "opts": [
                            "125 is right: eight workers divide the work eight ways, and the span is already covered inside that",
                            "Neither is a time: 175 is a ceiling on any greedy schedule and 125 a floor, and the run lands somewhere between",
                            "175 is right, and it is the exact time, because Brent's bound is tight for every DAG once the worker count is fixed",
                            "50 is right: with more workers than the span the longest path is all that is left to wait for",
                        ],
                        "a": 1,
                        "whys": [
                            r"Dividing the work assumes eight nodes are always ready to run, and a DAG with a span of 50 has moments when fewer are, so 125 cannot be reached in general; it is only the lower bound.",
                            r"Complete steps are at most $T_1/p$, incomplete ones at most $T_\infty$, so the sum bounds the schedule from above; $\max(T_1/p, T_\infty)$ bounds it from below.",
                            r"The derivation counts complete and incomplete steps separately and adds their maxima, which double-counts steps that are both near the end; the bound is rarely met exactly.",
                            r"Eight workers are far fewer than the parallelism of $1000/50 = 20$, so the work term dominates here and the span is not the binding constraint yet.",
                        ],
                        "why": r"""
Brent's argument sorts the steps of a greedy schedule into complete ones, at most
$T_1/p$ of them, and incomplete ones, at most $T_\infty$, and adds the two maxima. That
gives a ceiling of 175, not a prediction. The floor is $\max(1000/8, 50) = 125$, since
the work must be done and the longest path must be walked. Where the run actually
lands depends on the DAG's shape, and with a parallelism of 20 against 8 workers it
will sit closer to the floor than the ceiling.
""",
                    },
                    {
                        "q": r"`reduce_tree(range(1, 101))` reports work 99 and span 7. Which of the two numbers is fixed by $n$ alone, and which depends on how the tree is shaped?",
                        "opts": [
                            "Both are fixed by $n$: any tree over 100 leaves has 99 internal nodes and 7 levels",
                            r"Work is fixed at $n - 1$ for any pairing; span is $\lceil \log_2 n \rceil$ only when the pairing is balanced",
                            r"Span is fixed at $\lceil \log_2 n \rceil$ by the number of leaves; work varies with how many odd leftovers get carried",
                            "Neither is fixed: a cleverer pairing of the leaves can reduce both the work and the span at once",
                        ],
                        "a": 1,
                        "whys": [
                            r"A chain that adds one element at a time also has 99 nodes and is a valid tree, with a span of 99; the level count is a property of the pairing, not of $n$.",
                            r"Every addition merges two values into one, so $n - 1$ of them are needed and no more; the level count is what balancing buys.",
                            r"A carried leftover costs no addition, so carrying changes nothing about the work; it is the depth that the carry can lengthen, by putting a leaf a level lower.",
                            r"Fewer than $n - 1$ merges cannot get $n$ values down to one, so work has a hard floor that is already met; only the span has room to move.",
                        ],
                        "why": r"""
Getting from $n$ values to one takes exactly $n - 1$ binary merges however they are
arranged, so 99 is fixed. The span is the depth of the tree, and a balanced pairing
gives $\lceil \log_2 100 \rceil = 7$ while a chain gives 99; the tree's shape is what
the lab's `reduce_tree` controls by pairing adjacent elements and carrying the odd one.
Work is the sequential cost and span is the parallel one, and only the second is yours
to improve.
""",
                    },
                    {
                        "q": r"A GPU with 4096 threads scans 4096 elements. Hillis-Steele costs about 49152 work with span 12; Blelloch costs 8190 work with span 24. Which finishes first on this machine?",
                        "opts": [
                            "Blelloch, because it does a sixth of the additions and additions are what take the time",
                            "Blelloch, because the extra work of Hillis-Steele turns into extra span once every thread is busy",
                            "Hillis-Steele, because with a thread per element the span is what remains, and its span is half",
                            r"They tie, because Brent's bound gives $T_1/p + T_\infty = 2\log_2 n$ for both of them",
                        ],
                        "a": 2,
                        "whys": [
                            r"Work is what one worker pays; with 4096 workers the $T_1/p$ term is 12 steps for Hillis-Steele and 2 for Blelloch, and the spans of 12 and 24 dominate both.",
                            r"With $p = n$ every level of Hillis-Steele still runs in one step, since no thread has more than one node per level; the extra work costs nothing extra in time here.",
                            r"$49152/4096 + 12 = 24$ against $8190/4096 + 24 \approx 26$: when workers are not scarce, the shorter DAG wins.",
                            r"The bounds are 24 and about 26, close but not equal, and more to the point Hillis-Steele's is met exactly because each level runs in one step.",
                        ],
                        "why": r"""
Work-efficient means cheaper for a worker count well below $n$. With a thread per
element, $T_1/p$ is small for both algorithms and the span decides: Hillis-Steele's
$\log_2 n = 12$ levels each run in one step, so it finishes in 12, while Blelloch needs
24. Brent's bound says the same: $12 + 12 = 24$ against $2 + 24 = 26$. Blelloch is the
right choice when elements outnumber workers, which is the usual case on a CPU, and the
DAG tells you which case you are in.
""",
                    },
                    {
                        "q": r"`blelloch_scan([3, 1, 4, 1, 5], max, 0)` pads to eight slots with 0 and correctly returns `[0, 3, 3, 4, 4]`. On which input would the same call return a wrong answer?",
                        "opts": [
                            "An input of exactly eight elements, because then nothing is padded and the overwrite of the last slot destroys a real value that the down-sweep still needs",
                            "An input containing negative numbers, because 0 is not the identity of `max` there and the padding and the first slot are both wrong",
                            "An input with repeated values, because `max` cannot separate the copies and the down-sweep counts one of them twice",
                            "An input of one element, because a single element has no pair for the up-sweep to combine",
                        ],
                        "a": 1,
                        "whys": [
                            r"The overwrite of the last slot happens at every size; the up-sweep has already folded that slot's value into the tree, and the exclusive scan never needs the total itself.",
                            r"`max(-3, 0)` is 0, so a padded 0 and a leading 0 both claim a value that was never in the input.",
                            r"The down-sweep passes values, not counts, and `max` of a value with itself is that value; duplicates are exactly the case an idempotent operator handles best.",
                            r"One element pads to one slot, the up-sweep does nothing, the last slot becomes the identity, and `[0]` is the correct exclusive scan of a single element.",
                        ],
                        "why": r"""
Padding with the identity is safe only if the identity really is one: an element that
leaves every value unchanged when combined. For `max` over all the reals that is
$-\infty$, and 0 only plays the part when every input is non-negative. Feed the scan
`[-3, -1, -4]` and it reports 0 as the running maximum before the first element, and
the padding slots contribute 0 to prefixes that should never see it. The other options
describe cases the algorithm handles as designed: the last slot is safely overwritten,
duplicates are harmless under `max`, and one element scans to `[identity]`.
""",
                    },
                    {
                        "q": r"The lab tests `reduce_tree(['a', 'b', 'c', 'd', 'e'], add, '')` and requires exactly `'abcde'`. What property of your implementation does that test check that a sum of integers could not?",
                        "opts": [
                            "That the tree combines each left neighbour with its right neighbour and never swaps them, since concatenation is not commutative",
                            "That strings take a separate code path from numbers, since `operator.add` behaves differently on the two types",
                            "That the operator is commutative, since a tree is free to combine its leaves in whatever order the levels dictate",
                            "That the odd leftover element is combined before any of the pairs, so that it ends up at the front of the result rather than at the back",
                        ],
                        "a": 0,
                        "whys": [
                            r"With integers a swapped node still sums correctly, so only an order-sensitive operator can expose a tree that computes `op(right, left)`.",
                            r"The point of passing `op` is that the tree has one code path for every associative operator; a special case for strings would defeat it.",
                            r"The tree needs associativity and nothing more; commutativity is precisely what concatenation lacks, and the test passes anyway when the operand order is kept.",
                            r"The leftover is carried unchanged to the next level and combined as the right operand when its turn comes; combining it first would produce `'eabcd'`.",
                        ],
                        "why": r"""
A reduction tree relies on associativity, which lets it regroup the parentheses, and
must not rely on commutativity, which would let it reorder the operands. Integer
addition has both, so a tree that quietly computes `op(right, left)` at every node
still sums correctly and the bug is invisible. String concatenation is associative but
not commutative, so the same bug spells `edcba` or worse, and the test catches it. The
same discipline is what lets the scan work for matrix products and other ordered
operators.
""",
                    },
                    {
                        "q": r"Two students compare `blelloch_scan` against `sequential_scan` on a list of random floats and find the results differ in the fifteenth significant digit. One says it is a bug. Is it?",
                        "opts": [
                            "Yes: the exclusive scan is defined so that the two agree exactly, and any difference at all means an index in the down-sweep is off by one",
                            "Yes: the down-sweep must apply the operator with its operands swapped when the values are floats",
                            "No: the padding contributes a rounding error at the far end of the buffer, which is expected and harmless",
                            "No: float addition is not associative, so the tree's grouping rounds differently, and exactness is a claim about integers",
                        ],
                        "a": 3,
                        "whys": [
                            r"An off-by-one produces differences of the size of the elements, not $10^{-15}$; a last-digit disagreement is the signature of regrouped additions, not of a wrong index.",
                            r"Swapping operands changes nothing for addition and would break the scan for every non-commutative operator; float rounding comes from grouping, which swapping does not touch.",
                            r"Adding 0.0 is exact for every finite double, so the padding contributes no rounding at all; the difference comes from the real elements being grouped differently.",
                            r"$(10^{16} + 1) - 10^{16}$ and $10^{16} + (1 - 10^{16})$ differ by exactly one, and a fifteenth-digit gap is the same effect at ordinary magnitudes.",
                        ],
                        "why": r"""
The tree and the loop add the same numbers in different groupings, and floating-point
addition is only approximately associative, so their results can differ in the last
bits. Neither is more correct; the tree sum is often the more accurate. The lab can
demand equality because it scans integers, where addition is exactly associative. On
floats the honest test is a tolerance, and a difference far larger than the last few
digits, not a difference in them, is what an indexing bug looks like.
""",
                    },
                ],
            },
            "lab": {
                "title": "Blelloch scan as a task DAG",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Everything here is executed sequentially. The point is not to run in parallel —
it is to *count* the DAG a parallel machine would execute, and to prove the
clever algorithm returns exactly what the obvious one does.

**`next_power_of_two(n)`** — the smallest power of two at least `n`; `1` for
`n <= 1`.

**`reduce_tree(values, op=operator.add, identity=0)`** — pairwise tree
reduction. Returns `(value, stats)` where `stats` is
`{"work": ..., "span": ...}`: `work` counts applications of `op`, `span` counts
levels. An odd element at the end of a level is carried to the next level
unchanged. Empty input returns `(identity, {"work": 0, "span": 0})`.

```text
reduce_tree(range(1, 101))                       -> (5050, {work: 99, span: 7})
reduce_tree(["a","b","c","d","e"], add, "")      -> ("abcde", {work: 4, span: 3})
```

**`sequential_scan(values, op, identity)`** — the reference **exclusive** scan:
element `i` is the fold of everything strictly before it.

```text
sequential_scan([1, 2, 3, 4])  ->  [0, 1, 3, 6]
```

**`blelloch_scan(values, op=operator.add, identity=0)`** — the work-efficient
exclusive scan, returning `(result, stats)`. Pad to `next_power_of_two(len)`
with `identity`, run the up-sweep (stride doubling, `buf[i] = op(buf[i-stride],
buf[i])`), overwrite the last slot with `identity`, then the down-sweep (stride
halving: the left child takes the parent's value, the parent takes
`op(old_left, parent)`). Count one unit of `work` per `op`, one unit of `span`
per stride level. Trim the padding before returning.

**`scan_cost(n)`** — the closed form for that DAG, `{"work": 2*(m-1),
"span": 2*log2(m)}` for `m = next_power_of_two(n)`. Your instrumented
`blelloch_scan` must reproduce it exactly.

**`parallelism(stats)`** — `work / span`, and `0.0` when `span` is 0.

**`brent_bound(stats, workers)`** — `work/workers + span`. Fewer than 1 worker
raises `ValueError`.

```text
n = 8   -> work 14, span 6, parallelism 2.3333, brent(4) = 9.5
n = 1000-> work 2046, span 20, parallelism 102.3
```
''',
                "files": [{"name": "main.py", "content": r'''
import operator
import random


def next_power_of_two(n):
    """Smallest power of two that is at least n."""
    # your code here


def reduce_tree(values, op=operator.add, identity=0):
    """(value, {"work": ..., "span": ...}) for a pairwise tree reduction."""
    # your code here


def sequential_scan(values, op=operator.add, identity=0):
    """The reference exclusive scan."""
    # your code here


def blelloch_scan(values, op=operator.add, identity=0):
    """(exclusive scan, {"work": ..., "span": ...}) via up-sweep and down-sweep."""
    # your code here


def scan_cost(n):
    """Closed-form {"work": ..., "span": ...} for the Blelloch DAG on n elements."""
    # your code here


def parallelism(stats):
    """work / span, or 0.0 when there is no work to do."""
    # your code here


def brent_bound(stats, workers):
    """Brent's bound on the time with this many workers."""
    # your code here


rng = random.Random(7)
data = [rng.randrange(0, 20) for _ in range(1000)]
total, red_stats = reduce_tree(data)
scan, scan_stats = blelloch_scan(data)
print("sum:", total, red_stats)
print("scan:", scan_stats, "parallelism:", round(parallelism(scan_stats), 3))
print("matches sequential:", scan == sequential_scan(data))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import operator
import random


def next_power_of_two(n):
    """Smallest power of two that is at least n."""
    if n <= 1:
        return 1
    size = 1
    while size < n:
        size *= 2
    return size


def reduce_tree(values, op=operator.add, identity=0):
    """(value, {"work": ..., "span": ...}) for a pairwise tree reduction."""
    level = list(values)
    if not level:
        return identity, {"work": 0, "span": 0}
    work = 0
    span = 0
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level) - 1, 2):
            nxt.append(op(level[i], level[i + 1]))
            work += 1
        if len(level) % 2:
            nxt.append(level[-1])
        level = nxt
        span += 1
    return level[0], {"work": work, "span": span}


def sequential_scan(values, op=operator.add, identity=0):
    """The reference exclusive scan."""
    out = []
    acc = identity
    for value in values:
        out.append(acc)
        acc = op(acc, value)
    return out


def blelloch_scan(values, op=operator.add, identity=0):
    """(exclusive scan, {"work": ..., "span": ...}) via up-sweep and down-sweep."""
    n = len(values)
    if n == 0:
        return [], {"work": 0, "span": 0}
    size = next_power_of_two(n)
    buf = list(values) + [identity] * (size - n)
    work = 0
    span = 0
    stride = 1
    while stride < size:
        for i in range(stride * 2 - 1, size, stride * 2):
            buf[i] = op(buf[i - stride], buf[i])
            work += 1
        span += 1
        stride *= 2
    buf[size - 1] = identity
    stride = size // 2
    while stride >= 1:
        for i in range(stride * 2 - 1, size, stride * 2):
            left = buf[i - stride]
            buf[i - stride] = buf[i]
            buf[i] = op(left, buf[i])
            work += 1
        span += 1
        stride //= 2
    return buf[:n], {"work": work, "span": span}


def scan_cost(n):
    """Closed-form {"work": ..., "span": ...} for the Blelloch DAG on n elements."""
    if n <= 0:
        return {"work": 0, "span": 0}
    size = next_power_of_two(n)
    return {"work": 2 * (size - 1), "span": 2 * size.bit_length() - 2}


def parallelism(stats):
    """work / span, or 0.0 when there is no work to do."""
    if stats["span"] == 0:
        return 0.0
    return stats["work"] / stats["span"]


def brent_bound(stats, workers):
    """Brent's bound on the time with this many workers."""
    if workers < 1:
        raise ValueError("workers must be at least 1")
    return stats["work"] / workers + stats["span"]


rng = random.Random(7)
data = [rng.randrange(0, 20) for _ in range(1000)]
total, red_stats = reduce_tree(data)
scan, scan_stats = blelloch_scan(data)
print("sum:", total, red_stats)
print("scan:", scan_stats, "parallelism:", round(parallelism(scan_stats), 3))
print("matches sequential:", scan == sequential_scan(data))
'''}],
                "hints": [
                    "In `reduce_tree`, build the next level with `range(0, len(level) - 1, 2)` and then append the odd survivor with `if len(level) % 2`.",
                    "The up-sweep index pattern is `for i in range(stride * 2 - 1, size, stride * 2)` with `stride` doubling from 1 while `stride < size`.",
                    "The down-sweep is the same index pattern with `stride` halving from `size // 2`. Save the left child first: `left = buf[i - stride]`, then `buf[i - stride] = buf[i]`, then `buf[i] = op(left, buf[i])`.",
                    "`size.bit_length()` gives log2(size) + 1 for an exact power of two, so the span is `2 * size.bit_length() - 2`.",
                ],
                "tests": [
                    {"name": "next_power_of_two", "code": r'''
_want = {0: 1, 1: 1, 2: 2, 3: 4, 5: 8, 8: 8, 9: 16, 1000: 1024}
for _n, _w in _want.items():
    _got = next_power_of_two(_n)
    assert _got == _w, f"next_power_of_two({_n}) gave {_got!r}, expected {_w}"
'''},
                    {"name": "reduce_tree counts its own DAG", "code": r'''
_v, _s = reduce_tree(range(1, 101))
assert _v == 5050, f"reduce_tree(range(1, 101)) summed to {_v!r}, expected 5050"
assert _s == {"work": 99, "span": 7}, f"stats were {_s!r}, expected work 99 and span 7"
_v, _s = reduce_tree([1, 2, 3, 4, 5])
assert (_v, _s) == (15, {"work": 4, "span": 3}), f"Got {(_v, _s)!r}, expected (15, work 4, span 3)"
assert reduce_tree([], operator.add, 0) == (0, {"work": 0, "span": 0}), "Empty input returns the identity"
assert reduce_tree([42]) == (42, {"work": 0, "span": 0}), "One element needs no operation at all"
'''},
                    {"name": "reduce_tree keeps the operands in order", "code": r'''
_v, _s = reduce_tree(["a", "b", "c", "d", "e"], operator.add, "")
assert _v == "abcde", f"String concatenation gave {_v!r} — the tree must not reorder operands"
assert _s == {"work": 4, "span": 3}, f"stats were {_s!r}, expected work 4 and span 3"
'''},
                    {"name": "sequential_scan is exclusive", "code": r'''
assert sequential_scan([1, 2, 3, 4]) == [0, 1, 3, 6], f"Got {sequential_scan([1, 2, 3, 4])!r}"
assert sequential_scan([]) == [], "Empty input scans to []"
assert sequential_scan([9]) == [0], "A single element scans to just the identity"
assert sequential_scan([3, 1, 4, 1, 5], max, 0) == [0, 3, 3, 4, 4], \
    f"Running maximum gave {sequential_scan([3, 1, 4, 1, 5], max, 0)!r}"
'''},
                    {"name": "blelloch_scan matches the sequential reference", "code": r'''
import random as _random
_rng = _random.Random(13)
for _ in range(60):
    _n = _rng.randrange(0, 40)
    _v = [_rng.randrange(-20, 20) for _ in range(_n)]
    _got, _stats = blelloch_scan(_v)
    assert _got == sequential_scan(_v), f"Length {_n}: got {_got!r}, expected {sequential_scan(_v)!r}"
assert blelloch_scan([]) == ([], {"work": 0, "span": 0}), "Empty input"
assert blelloch_scan([9])[0] == [0], "One element scans to [identity]"
assert blelloch_scan([3, 1, 4, 1, 5], max, 0)[0] == [0, 3, 3, 4, 4], \
    "The scan must work for any associative operator with an identity"
'''},
                    {"name": "The instrumented DAG matches the closed form", "code": r'''
for _n in (1, 2, 3, 5, 8, 16, 100, 1000):
    _stats = blelloch_scan(list(range(_n)))[1]
    _want = scan_cost(_n)
    assert _stats == _want, f"n={_n}: measured {_stats!r} but scan_cost says {_want!r}"
assert scan_cost(8) == {"work": 14, "span": 6}, f"scan_cost(8) gave {scan_cost(8)!r}"
assert scan_cost(1000) == {"work": 2046, "span": 20}, f"scan_cost(1000) gave {scan_cost(1000)!r}"
assert scan_cost(0) == {"work": 0, "span": 0}, "n=0 costs nothing"
'''},
                    {"name": "parallelism and Brent's bound", "code": r'''
assert abs(parallelism({"work": 14, "span": 6}) - 7 / 3) < 1e-12, \
    f"parallelism gave {parallelism({'work': 14, 'span': 6})!r}, expected 2.3333333333333335"
assert parallelism({"work": 30, "span": 8}) == 3.75, "n=16 has parallelism 3.75"
assert parallelism({"work": 0, "span": 0}) == 0.0, "No span means no parallelism to report"
assert brent_bound({"work": 14, "span": 6}, 4) == 9.5, \
    f"brent_bound gave {brent_bound({'work': 14, 'span': 6}, 4)!r}, expected 9.5"
try:
    brent_bound({"work": 14, "span": 6}, 0)
    assert False, "brent_bound with 0 workers should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The demo run agrees with the reference", "code": r'''
assert "matches sequential: True" in _out, \
    "main.py should confirm the Blelloch scan equals the sequential scan"
assert "'work': 2046" in _out or '"work": 2046' in _out, \
    "main.py should print the measured scan stats for the 1000-element run"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Coordination, races and interleaving",
            "summary": "Enumerate every schedule of a small program and exhibit the losing one.",
            "concepts": [
                "A data race is a property of the *program*, not of the run that happened to expose it",
                "Read-modify-write is three operations; only their atomic composition is safe",
                "Sequential consistency: an execution is some interleaving of each thread's program order",
                "The state space of p threads of k steps has (pk)! / (k!)^p interleavings",
                "Mutual exclusion removes schedules; a blocked thread simply has no enabled transition",
                "Systematic exploration (model checking) beats stress testing: it either finds the bug or proves its absence",
                "Deadlock is a reachable state with no enabled transition and unfinished threads",
            ],
            "read": [
                {
                    "title": "Every schedule, not the one you saw",
                    "minutes": 14,
                    "body": r'''
Two bank tellers share one ledger card. It reads 0. Each has a customer depositing one
pound, and each does the same three things: read the card, add one on a notepad, write the
total back on the card. Teller A reads 0 and writes 1. Teller B reads 1 and writes 2. Two
pounds, as it should be. Now let B read the card a moment *before* A writes to it. B reads
0, A writes 1, B adds one to the 0 on the notepad and writes 1. Two deposits, one pound
recorded, and nobody did anything wrong at their own desk.

That is `counter += 1` on two threads. The one line of source is three operations on the
machine, `load`, `inc`, `store`, and between any two of them the other thread may do
anything at all.

## Program order, and the schedule

Each thread's operations happen in the order its program lists them: a thread never
stores before it has loaded. What is not fixed is how the two threads' sequences are
merged. The hardware, or the operating system, chooses at every step which thread
executes its next operation, and the resulting sequence of thread ids is the **schedule**.
The assumption that every run of the program *is* some such merge, with each thread's own
order intact, is called sequential consistency, and it is the model this whole module
works in.

The lab's machine makes the state explicit: the shared `counter`, one program counter per
thread, one private register per thread, and the owner of a single lock. A `load` copies
the counter into the thread's register, `inc` adds one to the register, `store` copies the
register back to the counter. Nothing else exists, and that austerity is deliberate,
because it makes every state writable down and every schedule countable.

## How many schedules there are

Two threads of three operations make a schedule six steps long, and a schedule is fully
described by saying which three of the six positions belong to thread 0; thread 1 gets the
rest and both keep their internal order. That is $\binom{6}{3} = 20$. In general, $p$
threads of $k$ steps each fill $pk$ positions, and dividing the $(pk)!$ orderings by the
$k!$ internal orderings of each thread, which are not free, gives

$$\frac{(pk)!}{(k!)^p}$$

schedules. Run the numbers:

```python
from math import factorial


def interleavings(threads, steps):
    return factorial(threads * steps) // factorial(steps) ** threads


for p, k in ((2, 3), (3, 3), (2, 5), (4, 3), (10, 3)):
    print(f"{p:>2} threads x {k} steps: {interleavings(p, k):>28,} schedules")
```

Twenty for the two-teller program, 1680 for three tellers, and past a handful of threads
a number with no name. That growth is the reason this module keeps its programs tiny, and
also the reason the last section of this reading exists.

## The witness

Here is the schedule the lab's `find_race` returns for two naive threads, replayed with
the whole state printed at every step:

```python
NAIVE = ("load", "inc", "store")


def replay(schedule, counter=0):
    regs = [0, 0]
    pcs = [0, 0]
    for tid in schedule:
        op = NAIVE[pcs[tid]]
        if op == "load":
            regs[tid] = counter
        elif op == "inc":
            regs[tid] += 1
        else:
            counter = regs[tid]
        pcs[tid] += 1
        print(f"thread {tid} {op:<5} -> counter={counter} registers={regs}")
    return counter


print("final:", replay((0, 0, 1, 0, 1, 1)))
```

Thread 0 loads 0 and increments its register to 1. Thread 1 loads, and what it loads is
still 0, because thread 0 has not stored yet. Thread 0 stores its 1. Thread 1 increments
the 0 it holds and stores 1 on top of the 1 already there. The final counter is 1, and the
schedule is the proof: six thread ids that anyone can replay and get the same wrong
answer. That is what a **witness** is, and it is worth more than any number of failing
test runs, because it is reproducible and it says exactly where the two threads crossed.

## How many schedules lose

```python
from itertools import permutations

NAIVE = ("load", "inc", "store")


def replay(schedule, counter=0):
    regs = [0, 0]
    pcs = [0, 0]
    for tid in schedule:
        op = NAIVE[pcs[tid]]
        if op == "load":
            regs[tid] = counter
        elif op == "inc":
            regs[tid] += 1
        else:
            counter = regs[tid]
        pcs[tid] += 1
    return counter


schedules = sorted(set(permutations((0, 0, 0, 1, 1, 1))))
finals = [replay(s) for s in schedules]
print("schedules:", len(schedules))
print("that keep both increments:", finals.count(2))
print("that lose one:", finals.count(1))
print("the two that keep both:", [s for s, f in zip(schedules, finals) if f == 2])
```

Eighteen of the twenty schedules lose an increment. The only two that do not are the ones
where one thread runs all three operations before the other starts, and it is easy to see
why: the second thread's `load` must come after the first thread's `store` for its
increment to build on the other one, and with three operations each that leaves no room
for any overlap at all.

So the counter is wrong in ninety percent of its schedules, and yet the same program, run
on a real machine a million times, will very likely report 2 a million times. That is the
mistake this module is built around, and it is a tempting one because the evidence looks
overwhelming. A real scheduler does not flip a coin after every instruction. It gives a
thread the core for a quantum of several milliseconds, and `load, inc, store` takes a few
nanoseconds, so the window in which the other thread must land is a million times smaller
than the time between switches. The schedules that actually occur are almost always the
two serial ones. Model that:

```python
import random

NAIVE = ("load", "inc", "store")
rng = random.Random(3)


def replay(schedule, counter=0):
    regs = [0, 0]
    pcs = [0, 0]
    for tid in schedule:
        op = NAIVE[pcs[tid]]
        if op == "load":
            regs[tid] = counter
        elif op == "inc":
            regs[tid] += 1
        else:
            counter = regs[tid]
        pcs[tid] += 1
    return counter


def scheduler_run(switch_probability):
    """After each step the scheduler switches thread with this probability."""
    pcs = [0, 0]
    tid = 0
    schedule = []
    while len(schedule) < 6:
        if pcs[tid] == 3 or rng.random() < switch_probability:
            tid = 1 - tid
        if pcs[tid] < 3:
            schedule.append(tid)
            pcs[tid] += 1
    return tuple(schedule)


for q in (0.5, 0.05, 0.001):
    lost = sum(1 for _ in range(10000) if replay(scheduler_run(q)) == 1)
    print(f"switch probability {q:<6}: lost an increment in {lost:>5} of 10000 runs")
```

At a switch probability of one in a thousand, still far more frequent than a real
scheduler, the loss shows up eighteen times in ten thousand runs. Stress testing does not
find this bug; it finds it when a server is under load at three in the morning, once a
week, and never on the developer's laptop. A data race is a property of the *program*: of
the set of schedules its code permits. It is not a property of any run, and a run that
went well is not evidence that the set is safe.

## What a lock removes

Wrap the three operations in `lock` and `unlock`. In the lab's machine `lock` is enabled
only when the lock is free or already this thread's, and `unlock` only for the owner. A
thread whose next operation is a `lock` it cannot take has *no enabled transition*. It is
not an error and it is not a deadlock; it is an absence. The explorer tries the other
threads instead, and when the owner eventually unlocks, the waiting thread's transition
reappears.

Count what is left. After whichever thread locks first, the other thread cannot move until
the `unlock`, so the only decision in the whole schedule is who goes first: two schedules
for two threads, $3! = 6$ for three, $p!$ in general. Notice what the lock did. It did not
fix the arithmetic; `load`, `inc` and `store` are the same three operations. It deleted
eighteen of the twenty schedules, and the two survivors were the two that were already
correct. Mutual exclusion is subtraction from the schedule space, and the lab's
`count_schedules` measures exactly that subtraction: 20 to 2.

## Deadlock, precisely

A **deadlock** is a reachable state in which no thread has an enabled transition and at
least one thread is unfinished. Compare that with waiting: a waiting thread has no enabled
transition, but somebody else does, and that somebody will eventually unlock. In a
deadlock, nobody does.

The lab's machine can reach one. Give both threads the program `("lock", "load", "inc",
"store")`, with the `unlock` forgotten. Thread 0 takes the lock, runs to the end and
finishes, still holding it. Thread 1's next operation is `lock`, which is not enabled;
thread 0 has nothing left. No transition, an unfinished thread: deadlock. The explorer
abandons that path, because a schedule that does not complete is not a result and must
not be counted as one. The classic two-lock deadlock, where each thread holds one lock and
waits for the other's, has the same definition and the same shape; it needs two locks,
which is why this machine has only one.

## Proof, and where the proof stops

`find_race([LOCKED, LOCKED], 2)` returns `None`, and that is a different kind of statement
from a passing test. The explorer walked every schedule the model permits and none of them
reached a counter other than 2. Within the model that is a proof of absence, and for the
naive program the same walk produces a witness. Systematic exploration, which is what a
model checker does, either finds the bug or shows there is none to find; stress testing can
only ever do the first.

The proof is over the model, and the model stops holding in three places you should know.
First, the numbers from earlier: four threads of three steps have 369,600 schedules, and
ten threads have $4 \times 10^{24}$. Many of those schedules reach the same state, and real
checkers explore states rather than schedules, prune interleavings of operations that
cannot affect each other, and still run out of memory on programs of modest size. The lab
enumerates schedules because it is transparent, not because it scales.

Second, sequential consistency is a promise real hardware does not make. An x86 core keeps
its stores in a buffer and lets a later load run ahead of them, and ARM cores reorder far
more freely, so a two-thread program can exhibit outcomes that no interleaving of program
order produces. What restores order is a fence, and a lock's acquire and release are fences,
which is why the argument that the locked program has one outcome survives the trip to real
silicon: everything the counter touches sits between two fences.

Third, the granularity. `counter += 1` in the model is three atomic steps; on a real
machine it is however many the compiler emitted, and the `lock` operation the model hands
out for free is itself a read-modify-write that the hardware must make atomic with a
special instruction. The model is right about the shape of the bug and silent about how
many places it can hide.

## What you are about to build

The lab, *A deterministic interleaving explorer*, is this machine and this walk. `step`
applies one operation for one thread and returns `None` when that thread cannot move, which
covers both a finished thread and a blocked one. `schedules` walks the tree of choices,
thread ids in ascending order so that the enumeration is deterministic, yielding every
complete schedule with its final counter and abandoning any path that deadlocks.
`outcomes`, `count_schedules`, `run_schedule` and `find_race` read the results off. With the
ascending order, the first losing schedule the walk meets is `(0, 0, 1, 0, 1, 1)`, the one
replayed above, and the tests hold you to it.
''',
                },
            ],
            "quiz": {
                "title": "The schedules you did not see",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"Two threads of three steps have 20 schedules and three threads of three steps have 1680. Where do those two numbers come from?",
                        "opts": [
                            "From choosing which positions in the schedule each thread's steps occupy, with each thread's own order kept: $6!/(3!)^2$ and $9!/(3!)^3$",
                            "From every step being a two-way or three-way choice of which thread runs next, $2^6 = 64$ and $3^9 = 19683$, less the schedules that would deadlock",
                            "From all orderings of the six or nine operations, $6! = 720$ and $9! = 362880$, divided by the number of threads",
                            r"From the product of the threads' step counts, $3 \times 3$ and $3 \times 3 \times 3$, times the ways of ordering the threads",
                        ],
                        "a": 0,
                        "whys": [
                            r"A schedule is a multiset permutation: the $(pk)!$ orderings, divided by the $k!$ internal orderings of each thread that program order forbids.",
                            r"The naive program cannot deadlock, and the sequences removed from $2^6$ are the ones that step a thread more than three times, which is a counting error rather than a deadlock.",
                            r"$720/2 = 360$ and $362880/3$ are nowhere near 20 and 1680; dividing by the thread count does not remove the $3!$ orderings within each thread that program order fixes.",
                            r"$9 \times 2 = 18$ and $27 \times 6 = 162$: multiplying step counts describes a state grid, not the number of paths through it.",
                        ],
                        "why": r"""
A schedule is a sequence of thread ids in which thread $t$ appears exactly $k$ times,
and the order of each thread's own steps is not a choice, it is program order. So count
the $(pk)!$ orderings of all steps and divide out the $k!$ orderings inside each of the
$p$ threads: $720/36 = 20$ and $362880/216 = 1680$. The powers $2^6$ and $3^9$ count
sequences without the constraint that each thread takes exactly three steps, and
nothing in the naive program deadlocks, so nothing is removed for that reason.
""",
                    },
                    {
                        "q": r"""Two naive threads start with the counter at 5 and run the schedule below. What is the final counter?

```text
(1, 1, 0, 0, 0, 1)
```
""",
                        "opts": [
                            "5, because each thread's store writes back a value another thread has already overwritten",
                            "7, because both threads load, both increment, and both stores land on the counter",
                            "6, because thread 1 loaded 5 before thread 0 stored 6, so its own store writes 6 over 6",
                            "The schedule is infeasible, because thread 1 takes a step after it has already finished",
                        ],
                        "a": 2,
                        "whys": [
                            r"A store always writes the register, which holds a loaded value plus one, so no schedule can leave the counter at its starting value: at least one increment always lands.",
                            r"Both stores do land, but thread 1's register holds $5 + 1$, loaded before thread 0 stored, so the second store writes 6, not 7; a store cannot add, only copy.",
                            r"Thread 1: load 5, inc to 6. Thread 0: load 5, inc, store 6. Thread 1: store 6. One increment lost.",
                            r"Thread 1 appears three times in the schedule, exactly its program length, and its steps are `load`, `inc` and finally `store`; every step is enabled when it comes.",
                        ],
                        "why": r"""
Replay it: thread 1 loads 5 and increments its register to 6; thread 0 loads 5, since
nothing has been stored yet, increments to 6 and stores 6; thread 1 then stores the 6 it
has been holding. Both stores land, but they carry the same number, because both loads
saw 5. The counter cannot stay at 5, since a store always writes a loaded value plus
one, and it cannot reach 7 unless one load sees the other thread's store. The schedule
is feasible: each thread is stepped exactly three times.
""",
                    },
                    {
                        "q": r"A test harness runs two increment threads against a shared counter ten thousand times and the final value is 2 every single time. What has been shown?",
                        "opts": [
                            "That the program has no data race, since ten thousand runs would have exposed one",
                            "That the race is theoretical on this machine, because its scheduler evidently never preempts a thread between the load and the store",
                            "Almost nothing about the program: most of its schedules lose an increment, and the scheduler's long quantum never landed in one",
                            "That the counter is safe on this machine, and becomes unsafe only on hardware with more cores",
                        ],
                        "a": 2,
                        "whys": [
                            r"Eighteen of the program's twenty schedules lose an increment; what ten thousand runs sampled is the scheduler's habits, not the program's set of schedules.",
                            r"Schedulers do preempt inside increments, rarely; at one switch per thousand steps the model loses eighteen in ten thousand, and a rare bug under load is the dangerous kind.",
                            r"Three instructions take nanoseconds and a quantum takes milliseconds, so the serial schedules are nearly all that ever run, and they are the two that happen to be correct.",
                            r"Core count changes how often the race window is hit, not whether the losing schedules exist; a single core with preemption reaches all twenty of them.",
                        ],
                        "why": r"""
A data race is a property of the program's schedule space, and eighteen of these
twenty schedules lose an increment. A real scheduler runs each thread for milliseconds
while the three operations take nanoseconds, so the schedules that occur are almost
always the two serial ones, which are exactly the two correct ones. The test measured
the scheduler, not the program. Enumerating the schedules, as the lab does, finds the
witness in the second schedule it tries.
""",
                    },
                    {
                        "q": r"With both threads running `LOCKED`, the explorer finds exactly 2 complete schedules rather than the 252 that two five-step threads could interleave into. What removed the other 250?",
                        "opts": [
                            "The lock turns the five operations into one atomic step per thread, so there are only two steps left to order",
                            "The explorer treats any schedule in which a thread would have to block as a deadlock, and discards it without counting it as a result",
                            "Once one thread holds the lock the other has no enabled transition until the unlock, so the only choice left is who locks first",
                            "The lock pins both threads to one core, and a single core cannot interleave two threads at all",
                        ],
                        "a": 2,
                        "whys": [
                            r"All five operations still execute one at a time and the explorer still steps them individually; what the lock changes is which thread is allowed to take the next step.",
                            r"Blocking is not deadlock: a blocked thread is skipped for now and stepped later once the owner unlocks, and every one of the two surviving schedules includes such a wait.",
                            r"After the first `lock`, the other thread's `lock` is disabled at every step until `unlock`, so the schedule is forced apart from its first entry.",
                            r"Cores are not in the model, and a single core with preemption reaches every interleaving; it is the lock's semantics, not the hardware, that forbids the others.",
                        ],
                        "why": r"""
A thread whose next operation is a `lock` it cannot take has no enabled transition, so
the explorer cannot choose it. After the first thread locks, every step until its
`unlock` has exactly one enabled thread, and after the unlock the other thread runs
alone. The single free choice is who locks first, hence $2! = 2$, and $3! = 6$ for three
threads. The operations are unchanged and are still stepped one at a time; the lock
subtracted schedules rather than altering arithmetic.
""",
                    },
                    {
                        "q": r"Which of these states of the lab's machine is a deadlock, by the definition the explorer uses to abandon a path?",
                        "opts": [
                            "Thread 0 holds the lock and is at `inc`; thread 1 is at `lock` and cannot take it",
                            "Thread 0 holds the lock and has run off the end of its program; thread 1 is at `lock`",
                            "Both threads have run off the end of their programs, and the lock is still held by thread 0",
                            "Thread 0 is at `unlock` while thread 1 holds the lock; thread 1 is at `store`",
                        ],
                        "a": 1,
                        "whys": [
                            r"Thread 1 is waiting, but thread 0 has an enabled `inc` and will reach its `unlock`; a state where someone can move is not a deadlock.",
                            r"No thread can move and one is unfinished: nobody will ever release the lock thread 1 needs.",
                            r"No transition is enabled, but every thread is finished, so this is a completed schedule with a leaked lock, not an abandoned one.",
                            r"Thread 0's `unlock` is disabled since it is not the owner, but thread 1 has an enabled `store` and will go on to unlock; the state is a wait, not a deadlock.",
                        ],
                        "why": r"""
A deadlock is a reachable state with no enabled transition for any thread and at least
one thread unfinished. Thread 0 finished while holding the lock, so thread 1's `lock`
will never become enabled and nothing else can happen: that path is abandoned. In the
other states either some thread can still move, which is merely waiting, or every
thread is finished, which is a complete schedule whatever the lock's owner says.
""",
                    },
                    {
                        "q": r"`find_race([LOCKED, LOCKED], 2)` returns `None`. What kind of claim is that?",
                        "opts": [
                            "A statistical one: the explorer sampled a large number of schedules and the losing one was not among those it happened to try",
                            "A claim about two threads only, which says nothing about whether three locked threads can still race",
                            "A claim that the locked program has no schedule in which any thread ever has to wait for the lock",
                            "A proof within the model: every complete schedule the machine permits was walked and none reached a value other than 2",
                        ],
                        "a": 3,
                        "whys": [
                            r"The walk is exhaustive, not sampled; `schedules` yields every feasible complete interleaving, and `None` means the losing schedule does not exist in the model.",
                            r"The reasoning behind the result, that a held lock disables the other threads until release, applies to any number of threads, and the lab confirms it at three.",
                            r"Both surviving schedules contain a wait; the lock's job is to make the second thread wait, and waiting is what removes the losing interleavings.",
                            r"Exhaustive enumeration either produces a witness or establishes that there is none to produce.",
                        ],
                        "why": r"""
`schedules` is an exhaustive walk of the model's schedule space, so `find_race`
returning `None` means no feasible complete schedule reaches a value other than 2: a
proof of absence within the model, the thing a stress test can never provide. The
proof is only as good as the model, which assumes sequential consistency and treats
`lock` as atomic, so on real hardware it holds because a lock's acquire and release
are fences. Within those terms it is a proof, not a sample.
""",
                    },
                ],
            },
            "lab": {
                "title": "A deterministic interleaving explorer",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
A tiny abstract machine: one shared `counter`, one private register per thread,
and a single lock. A *program* is a tuple of operation names.

```text
NAIVE  = ("load", "inc", "store")
LOCKED = ("lock", "load", "inc", "store", "unlock")
```

A **state** is `(counter, pcs, regs, owner)` — the shared counter, one program
counter and one register per thread, and the lock owner (`FREE`, which is `-1`,
when nobody holds it). `initial_state` and `is_finished` are given.

**`step(programs, state, tid)`** returns the state after thread `tid` executes
its next operation, or `None` when that thread cannot proceed — it has finished,
or it is waiting on the lock. `"load"` copies the counter into the register,
`"inc"` adds one to the register, `"store"` copies the register back,
`"lock"` succeeds only when the lock is free or already this thread's,
`"unlock"` succeeds only for the owner. An unknown operation name raises
`ValueError`. States are immutable — build a new tuple.

**`schedules(programs, counter=0)`** — a generator yielding `(schedule, final)`
for every feasible complete interleaving, where `schedule` is a tuple of thread
ids. Explore thread ids in ascending order so the enumeration is deterministic.
Abandon any path that reaches a state with no enabled transition and unfinished
threads (that is a deadlock, not a result).

**`outcomes(programs, counter=0)`** — the sorted distinct final counters.

**`count_schedules(programs, counter=0)`** — how many complete interleavings there are.

**`run_schedule(programs, schedule, counter=0)`** — replay one schedule and
return the final counter. Raise `ValueError` if a step is not enabled, and again
if the schedule ends before every thread has finished.

**`find_race(programs, expected, counter=0)`** — the first schedule whose final
counter is not `expected`, or `None` when every schedule agrees.

```text
outcomes([NAIVE, NAIVE])          -> [1, 2]      count_schedules -> 20
outcomes([NAIVE, NAIVE, NAIVE])   -> [1, 2, 3]   count_schedules -> 1680
outcomes([LOCKED, LOCKED])        -> [2]         count_schedules -> 2
find_race([NAIVE, NAIVE], 2)      -> (0, 0, 1, 0, 1, 1)
```

The last line is the whole lesson: two threads, three instructions each, and a
schedule that loses an increment.
''',
                "files": [{"name": "main.py", "content": r'''
NAIVE = ("load", "inc", "store")
LOCKED = ("lock", "load", "inc", "store", "unlock")
FREE = -1


def initial_state(programs, counter=0):
    """Fresh state: given counter, every pc at 0, every register 0, lock free."""
    return (counter, (0,) * len(programs), (0,) * len(programs), FREE)


def is_finished(programs, state):
    """True when every thread has run off the end of its program."""
    return all(pc == len(p) for pc, p in zip(state[1], programs))


def step(programs, state, tid):
    """State after thread tid runs one operation, or None when it cannot."""
    # your code here


def schedules(programs, counter=0):
    """Yield (schedule, final counter) for every feasible complete interleaving."""
    # your code here


def outcomes(programs, counter=0):
    """Sorted distinct final counter values."""
    # your code here


def count_schedules(programs, counter=0):
    """How many complete interleavings exist."""
    # your code here


def run_schedule(programs, schedule, counter=0):
    """Replay one schedule; ValueError when it is not a complete feasible one."""
    # your code here


def find_race(programs, expected, counter=0):
    """First schedule whose result is not expected, or None."""
    # your code here


print("naive outcomes:", outcomes([NAIVE, NAIVE]), count_schedules([NAIVE, NAIVE]))
print("locked outcomes:", outcomes([LOCKED, LOCKED]), count_schedules([LOCKED, LOCKED]))
print("race witness:", find_race([NAIVE, NAIVE], 2))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
NAIVE = ("load", "inc", "store")
LOCKED = ("lock", "load", "inc", "store", "unlock")
FREE = -1


def initial_state(programs, counter=0):
    """Fresh state: given counter, every pc at 0, every register 0, lock free."""
    return (counter, (0,) * len(programs), (0,) * len(programs), FREE)


def is_finished(programs, state):
    """True when every thread has run off the end of its program."""
    return all(pc == len(p) for pc, p in zip(state[1], programs))


def step(programs, state, tid):
    """State after thread tid runs one operation, or None when it cannot."""
    counter, pcs, regs, owner = state
    pc = pcs[tid]
    if pc >= len(programs[tid]):
        return None
    op = programs[tid][pc]
    regs = list(regs)
    pcs = list(pcs)
    if op == "load":
        regs[tid] = counter
    elif op == "inc":
        regs[tid] = regs[tid] + 1
    elif op == "store":
        counter = regs[tid]
    elif op == "lock":
        if owner not in (FREE, tid):
            return None
        owner = tid
    elif op == "unlock":
        if owner != tid:
            return None
        owner = FREE
    else:
        raise ValueError(f"unknown operation {op!r}")
    pcs[tid] = pc + 1
    return (counter, tuple(pcs), tuple(regs), owner)


def schedules(programs, counter=0):
    """Yield (schedule, final counter) for every feasible complete interleaving."""
    prefix = []

    def walk(state):
        if is_finished(programs, state):
            yield (tuple(prefix), state[0])
            return
        for tid in range(len(programs)):
            nxt = step(programs, state, tid)
            if nxt is None:
                continue
            prefix.append(tid)
            yield from walk(nxt)
            prefix.pop()

    yield from walk(initial_state(programs, counter))


def outcomes(programs, counter=0):
    """Sorted distinct final counter values."""
    return sorted({final for _, final in schedules(programs, counter)})


def count_schedules(programs, counter=0):
    """How many complete interleavings exist."""
    return sum(1 for _ in schedules(programs, counter))


def run_schedule(programs, schedule, counter=0):
    """Replay one schedule; ValueError when it is not a complete feasible one."""
    state = initial_state(programs, counter)
    for tid in schedule:
        nxt = step(programs, state, tid)
        if nxt is None:
            raise ValueError(f"thread {tid} is not enabled at this point in the schedule")
        state = nxt
    if not is_finished(programs, state):
        raise ValueError("the schedule does not run every thread to completion")
    return state[0]


def find_race(programs, expected, counter=0):
    """First schedule whose result is not expected, or None."""
    for schedule, final in schedules(programs, counter):
        if final != expected:
            return schedule
    return None


print("naive outcomes:", outcomes([NAIVE, NAIVE]), count_schedules([NAIVE, NAIVE]))
print("locked outcomes:", outcomes([LOCKED, LOCKED]), count_schedules([LOCKED, LOCKED]))
print("race witness:", find_race([NAIVE, NAIVE], 2))
'''}],
                "hints": [
                    "`step` must not mutate the state it is handed: copy `pcs` and `regs` into lists, change one entry, and rebuild the tuples.",
                    "Waiting on a lock is not an error — it is simply an absence of a transition. Return `None` and let the caller try another thread.",
                    "Write `schedules` as a recursive generator over a shared `prefix` list: append the thread id, `yield from` the recursive call, then pop.",
                    "`find_race` needs no extra machinery — walk `schedules` in order and return the first schedule whose final counter differs from `expected`.",
                ],
                "tests": [
                    {"name": "step implements the three operations", "code": r'''
_p = [NAIVE]
_s = initial_state(_p, 5)
_s = step(_p, _s, 0)
assert _s[2][0] == 5, f"after load the register is {_s[2][0]!r}, expected the counter value 5"
_s = step(_p, _s, 0)
assert _s[2][0] == 6, f"after inc the register is {_s[2][0]!r}, expected 6"
_s = step(_p, _s, 0)
assert _s[0] == 6, f"after store the counter is {_s[0]!r}, expected 6"
assert is_finished(_p, _s), "the thread has run all three operations"
assert step(_p, _s, 0) is None, "a finished thread has no next step"
'''},
                    {"name": "step leaves the state it was given alone", "code": r'''
_p = [NAIVE, NAIVE]
_s0 = initial_state(_p)
_s1 = step(_p, _s0, 0)
assert _s0 == (0, (0, 0), (0, 0), FREE), f"step mutated the input state: it is now {_s0!r}"
assert _s1[1] == (1, 0), f"only thread 0 advanced; pcs are {_s1[1]!r}"
try:
    step([("frobnicate",)], initial_state([("frobnicate",)]), 0)
    assert False, "an unknown operation should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The lock blocks rather than fails", "code": r'''
_p = [LOCKED, LOCKED]
_s = step(_p, initial_state(_p), 0)
assert _s is not None and _s[3] == 0, f"thread 0 should own the lock, owner is {_s[3]!r}"
assert step(_p, _s, 1) is None, "thread 1 must have no enabled transition while the lock is held"
_s2 = _s
for _ in range(3):
    _s2 = step(_p, _s2, 0)
_s2 = step(_p, _s2, 0)
assert _s2[3] == FREE, f"after unlock the owner is {_s2[3]!r}, expected FREE"
assert step(_p, _s2, 1) is not None, "with the lock free thread 1 can proceed"
'''},
                    {"name": "The naive counter loses increments", "code": r'''
assert outcomes([NAIVE, NAIVE]) == [1, 2], f"Got {outcomes([NAIVE, NAIVE])!r}, expected [1, 2]"
assert count_schedules([NAIVE, NAIVE]) == 20, \
    f"Got {count_schedules([NAIVE, NAIVE])!r} interleavings, expected 20"
assert outcomes([NAIVE, NAIVE, NAIVE]) == [1, 2, 3], f"Got {outcomes([NAIVE] * 3)!r}"
assert count_schedules([NAIVE, NAIVE, NAIVE]) == 1680, \
    f"Got {count_schedules([NAIVE] * 3)!r} interleavings, expected 1680"
assert outcomes([NAIVE], 10) == [11], "One thread on its own always adds exactly one"
'''},
                    {"name": "The lock removes every losing schedule", "code": r'''
assert outcomes([LOCKED, LOCKED]) == [2], f"Got {outcomes([LOCKED, LOCKED])!r}, expected [2]"
assert count_schedules([LOCKED, LOCKED]) == 2, \
    f"Got {count_schedules([LOCKED, LOCKED])!r} interleavings, expected 2"
assert outcomes([LOCKED, LOCKED, LOCKED]) == [3], f"Got {outcomes([LOCKED] * 3)!r}, expected [3]"
assert count_schedules([LOCKED, LOCKED, LOCKED]) == 6, \
    f"Got {count_schedules([LOCKED] * 3)!r} interleavings, expected 6"
assert outcomes([NAIVE, LOCKED]) == [1, 2], "One unlocked thread is enough to reintroduce the race"
'''},
                    {"name": "find_race produces a replayable witness", "code": r'''
_w = find_race([NAIVE, NAIVE], 2)
assert _w == (0, 0, 1, 0, 1, 1), f"Got witness {_w!r}, expected (0, 0, 1, 0, 1, 1)"
assert run_schedule([NAIVE, NAIVE], _w) == 1, \
    f"replaying the witness gave {run_schedule([NAIVE, NAIVE], _w)!r}, expected 1"
assert find_race([LOCKED, LOCKED], 2) is None, "the locked version has no losing schedule"
assert find_race([NAIVE], 1) is None, "a single thread cannot race with itself"
'''},
                    {"name": "run_schedule rejects impossible schedules", "code": r'''
assert run_schedule([NAIVE, NAIVE], (0, 0, 0, 1, 1, 1)) == 2, "the serial schedule adds both increments"
try:
    run_schedule([NAIVE, NAIVE], (0, 0, 0, 0))
    assert False, "a schedule that steps a finished thread should raise ValueError"
except ValueError:
    pass
try:
    run_schedule([NAIVE, NAIVE], (0, 0, 0))
    assert False, "a schedule that stops early should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Message passing and collective cost",
            "summary": "Build ring allreduce and a binomial broadcast, then audit the wire.",
            "concepts": [
                "Distributed memory has no shared address space: every datum moves by an explicit message",
                "The alpha-beta model: time = latency + bytes / bandwidth, per message",
                "Ring allreduce = reduce-scatter then allgather, 2(p-1) rounds of n/p elements each",
                "Its bandwidth cost 2(p-1)n/p per rank is optimal and independent of p as p grows",
                "Binomial-tree broadcast: p-1 messages in ceil(log2 p) rounds",
                "Latency-bound versus bandwidth-bound collectives, and why small messages need a different algorithm",
                "Instrumenting a simulated world is how you audit an implementation against its bound",
            ],
            "read": [
                {
                    "title": "What the wire has to carry",
                    "minutes": 14,
                    "body": r'''
Four machines have each trained on a quarter of the data and each holds a gradient: a
vector of eight numbers. Every one of them needs the *sum* of all four vectors before it
can take the next step. There is no shared memory. Machine 2 cannot look at machine 0's
vector; if it wants those numbers, machine 0 has to put them on the wire, and every byte on
the wire costs time. The question of this module is how few bytes, and how few messages,
that sum can be had for, and then whether the code you wrote sends that few.

## What a message costs

Watch a single message go. Before the first byte moves there is a fixed price: the sender
assembles a header, the network card is told, the receiver's card raises an interrupt, the
receiver copies the payload out. Call that $\alpha$, the latency, and it is paid once per
message whatever the message holds. Then the bytes flow, at whatever rate the link
sustains, $\beta$ bytes per second, so $m$ bytes take $m/\beta$ more. That gives the
alpha-beta model, which is the whole of the cost model this module uses:

$$T(m) = \alpha + \frac{m}{\beta}$$

```python
ALPHA = 1e-6         # seconds to get any message started
BETA = 10e9          # bytes per second once it is flowing


def message_time(nbytes):
    return ALPHA + nbytes / BETA


for nbytes in (8, 1024, 1 << 20):
    t = message_time(nbytes)
    print(f"{nbytes:>8} bytes: {t * 1e6:8.2f} us, of which latency is {ALPHA / t * 100:5.1f}%")
```

An eight-byte message is all latency: the bytes themselves take under a nanosecond. A
megabyte is all bandwidth. The crossover, where $\alpha = m / \beta$, is at $m = \alpha
\beta$, ten kilobytes on this link, and every algorithm below has to be judged twice, once
for messages far below that and once for messages far above it. For a collective of many
messages the two prices separate cleanly: the number of *rounds* is paid in $\alpha$ and
the number of *bytes per rank* is paid in $1/\beta$.

## Two ways that are too expensive

The obvious plan is for every rank to send its whole vector to every other rank, and let
everybody add. Each of $p$ ranks sends $p - 1$ messages of $n$ elements, and receives as
many: $p(p-1)$ messages, and $(p-1)n$ elements out of every link. That grows with $p$ on
every single rank, so a thousand ranks send a thousand vectors each.

The second plan is to gather everything to rank 0, add there, and broadcast the sum. Count
the bytes and something interesting appears: rank 0 receives $(p-1)n$ elements and sends
$(p-1)n$ back, so the total crossing the network is $2(p-1)n$, which is far less than the
first plan. But all of it crosses *one* link, rank 0's, one message after another, while
the other $p - 1$ links carry a single message each and sit idle the rest of the time. The
total is fine; the distribution is the problem.

## The ring

Ring allreduce keeps that total and spreads it over every link at once. Cut every rank's
vector into $p$ chunks of $n/p$ elements. Arrange the ranks in a ring, each sending only
to the rank on its right. Then run two phases of $p - 1$ rounds each.

In **reduce-scatter** round $s$, rank $r$ sends chunk $(r - s) \bmod p$ to rank
$(r + 1) \bmod p$ and adds the chunk it receives into its own copy of that chunk. Chunk
$c$ is thereby passed around the ring picking up one rank's contribution per hop, and
after $p - 1$ hops it has visited everyone: rank $r$ ends the phase holding the complete
sum of chunk $(r + 1) \bmod p$, and nothing else complete. In **allgather** round $s$,
rank $r$ sends chunk $(r + 1 - s) \bmod p$ onward, the chunk it has most recently
completed or received, and overwrites its copy of whatever arrives. The finished chunks
travel round the ring once more and everyone ends with all of them. Trace it symbolically
on three ranks, one element per chunk, with the lettered elements standing for the
numbers:

```python
p = 3
bufs = [[f"{name}{c}" for c in range(p)] for name in "abc"]   # chunk c of each rank
messages = 0


def show(tag):
    for r in range(p):
        print(f"{tag:<23} rank {r}: {bufs[r]}")


show("start")
for stage in range(p - 1):
    outgoing = [bufs[r][(r - stage) % p] for r in range(p)]      # snapshot first
    for r in range(p):
        src = (r - 1) % p
        c = (src - stage) % p
        bufs[r][c] = bufs[r][c] + "+" + outgoing[src]
        messages += 1
    show(f"reduce-scatter round {stage}")
for stage in range(p - 1):
    outgoing = [bufs[r][(r + 1 - stage) % p] for r in range(p)]
    for r in range(p):
        src = (r - 1) % p
        c = (src + 1 - stage) % p
        bufs[r][c] = outgoing[src]
        messages += 1
    show(f"allgather round {stage}")
print("messages:", messages, "  elements:", messages, "  bytes at 8 each:", messages * 8)
print("bound 2(p-1)n elem_bytes:", 2 * (p - 1) * p * 8)
```

After the two reduce-scatter rounds, rank 0 holds `a1+c1+b1`, the complete chunk 1, rank 1
holds chunk 2 and rank 2 holds chunk 0, each with all three letters in it and each
different. The two allgather rounds then carry those three finished chunks round the ring,
and the last three lines are identical. Twelve messages, twelve elements, and the bound
printed under it is the same number.

Now the bill. Each rank sends one chunk per round for $2(p-1)$ rounds, so per rank the
bytes are

$$2(p-1)\,\frac{n}{p}\,e$$

and summed over $p$ ranks the total is $2(p-1)\,n\,e$, exactly the total the gather-to-root
plan had, now spread so that every link carries a $1/p$ share of it in every round. The
lab's figures follow: with $p = 4$, $n = 8$ and 8-byte elements, six rounds of four
messages make 24 messages, each of two elements, 48 elements, 384 bytes.

Look at the per-rank cost as $p$ grows. $2(p-1)n/p$ is $2n(1 - 1/p)$, which rises towards
$2n$ and never reaches it. On four ranks a rank sends $1.5n$ elements; on a thousand it
sends $1.998n$. That is the property that makes the ring the workhorse of large training
runs: adding ranks does not add to any rank's bandwidth bill.

## Why nothing does better, in bytes

Take any one chunk. Its sum needs contributions from all $p$ ranks, and no rank can
contribute without sending, so at least $p - 1$ chunk-sized messages must arrive
somewhere before that chunk's sum exists anywhere. Once it exists, $p - 1$ ranks do not
have it and each must receive it, which is at least $p - 1$ chunk-sized messages more.
That is $2(p-1)$ chunk transfers per chunk, $p$ chunks, and $2(p-1)n$ elements in total
that any allreduce must move, regardless of algorithm. The ring moves exactly that, and
the lab's test asserts the equality to the byte, because a ring that sends more has a
redundant message in it and a ring that sends fewer has a chunk that never got summed.
The rigorous version of this argument, with the per-rank bound and its conditions, is
Patarasuk and Yuan's 2009 paper, and it assumes the data cannot be compressed, which
sums of independent numbers cannot.

## The simulation mistake

The lab's `World` is not a network. It is a ledger: every `send` records one message and
its element count, every `barrier` closes a round, and the algorithm is the thing on
trial. Simulating a round has one trap, and the trace above dodged it with the line marked
*snapshot first*. Every rank in a round sends what it holds *at the start* of the round.
If the loop instead sends for rank 0, applies rank 0's message at rank 1, then sends for
rank 1, what rank 1 sends already contains rank 0's contribution, and rank 2 receives in
one round what a real network would need two rounds to deliver. The sums may come out
right by luck for some $p$ and wrong for others, and the message count is unaffected, so
the bound check does not catch it. It is tempting because it reads like one loop. Build
the outgoing list first, then apply it, and the simulation cannot outrun the wire.

## Broadcast, and the shape of the tree

Broadcasting a vector from a root is the other half of the module, and it separates the
two prices even more sharply. The linear plan has the root send to each of $p - 1$ ranks in
turn: $p - 1$ messages, $p - 1$ rounds, every one of them through the root's link. The
binomial tree keeps the message count and collapses the rounds. Work in ranks *relative*
to the root, so that the root is relative rank 0. In the round with `mask` equal to 1,
relative rank 0 sends to 1. With `mask` 2, ranks 0 and 1 send to 2 and 3. With `mask` 4,
ranks 0 to 3 send to 4 to 7:

```text
mask 1:   0 -> 1                                holders: 2
mask 2:   0 -> 2,  1 -> 3                       holders: 4
mask 4:   0 -> 4,  1 -> 5,  2 -> 6,  3 -> 7     holders: 8
```

Every rank that has the data sends in every round, so the number of holders doubles, and
$p$ ranks are reached in $\lceil \log_2 p \rceil$ rounds with $p - 1$ messages in all. For
a $p$ that is not a power of two, the last round's senders whose target would fall off the
end send nothing: five ranks take three rounds and four messages. A root other than 0
shifts the whole pattern by the root's rank, modulo $p$, which is what relative ranks are
for. The bytes are $(p - 1)\,n\,e$ either way; what the tree buys is $\alpha$, not
$1/\beta$, and for a small message that is everything.

## Where the ring stops being the answer

The ring's rounds are its weakness. It pays $2(p-1)$ latencies, and for a thousand ranks
that is two thousand of them before a single useful byte has moved. Compare a tree
allreduce, a reduction up a binomial tree followed by a broadcast down it, which pays
$2\lceil \log_2 p \rceil$ latencies but ships the *whole* vector at every hop:

```python
ALPHA = 1e-6
BETA = 10e9


def ring_allreduce_time(p, n, elem_bytes=8):
    chunk_bytes = n // p * elem_bytes
    return 2 * (p - 1) * (ALPHA + chunk_bytes / BETA)


def tree_allreduce_time(p, n, elem_bytes=8):
    """Reduce up a binomial tree, then broadcast down it: the whole vector per hop."""
    rounds = (p - 1).bit_length()
    return 2 * rounds * (ALPHA + n * elem_bytes / BETA)


P = 64
for n in (64, 65536, 1 << 22):
    ring = ring_allreduce_time(P, n) * 1e6
    tree = tree_allreduce_time(P, n) * 1e6
    print(f"n={n:>8} elements: ring {ring:>10.1f} us   tree {tree:>10.1f} us   "
          f"{'ring' if ring < tree else 'tree'} wins")
```

Sixty-four elements, one per chunk, and the ring is ten times slower than the tree: it is
paying 126 latencies for 126 eight-byte messages. Half a megabyte and the ring wins by
nearly three to one; thirty-two megabytes and it wins by six. The ring is bandwidth-optimal
and latency-poor, the tree is the reverse, and the honest answer to "which collective" is
"how big is the message", which is why every MPI implementation switches algorithm at a
size threshold. Below the ridge of $\alpha\beta$ bytes, count rounds; above it, count bytes.

The model itself has edges. It assumes every link is independent and full duplex, so that
all $p$ sends of a round proceed in parallel at full rate; on a real switch several ranks
share an uplink and contend. It assumes all ranks start each round together, so one slow
rank stalls the ring, which in practice is the dominant cost at scale. It ignores the
additions, $n/p$ of them per round, which is safe for a sum and not for an expensive
reduction. And it takes $\alpha$ and $\beta$ as constants when a real link's latency
depends on distance and its bandwidth on how many messages are in flight. What survives all
of that is the shape: rounds times $\alpha$ plus bytes over $\beta$, and an implementation
that is audited against both.

## What you are about to build

The lab, *A simulated MPI world*, is the ledger and two algorithms on trial. `World`
records every `send` and `barrier`, refuses a rank outside the world, a message to oneself
and a negative count, and reports `bytes_moved` as a property. `ring_allreduce` runs the
two phases above on chunked vectors and must hit 24 messages, 6 rounds and 384 bytes at
$p = 4$, $n = 8$, equal to `allreduce_bytes_bound`. `broadcast_tree` runs the mask
doubling from any root and must send $p - 1$ messages in `broadcast_rounds(p)` rounds. The
bounds are one line each; the accounting is what proves the algorithms meet them.
''',
                },
            ],
            "quiz": {
                "title": "Messages against the bound",
                "minutes": 8,
                "questions": [
                    {
                        "q": r"A ring allreduce on $n = 64$ elements is scaled from 4 ranks to 64. What happens to the number of elements each rank sends?",
                        "opts": [
                            "It grows in proportion to the rank count, because each rank must get its data to every other rank",
                            "It stays at exactly 96, because the ring's per-rank cost is independent of the number of ranks",
                            "It rises from 96 towards 128 without reaching it, because $2(p-1)n/p$ is under $2n$ for every $p$",
                            "It falls, because more ranks means smaller chunks and each rank sends one chunk per round",
                        ],
                        "a": 2,
                        "whys": [
                            r"Every rank does reach every other, but through the ring one chunk at a time, and the chunks shrink as $p$ grows; the per-rank total is $2n(1 - 1/p)$, not $(p-1)n$.",
                            r"Independent of $p$ is the limit, not the value: $2 \cdot 3 \cdot 16 = 96$ at four ranks and $2 \cdot 63 \cdot 1 = 126$ at sixty-four.",
                            r"$2(p-1)n/p = 2n(1 - 1/p)$ climbs from $1.5n$ at $p = 4$ towards $2n$ and stops there.",
                            r"Chunks shrink by $1/p$ but rounds grow as $p - 1$, and the product $(p-1)/p$ rises with $p$ rather than falling.",
                        ],
                        "why": r"""
Each rank sends one chunk of $n/p$ elements in each of $2(p-1)$ rounds, so its total is
$2(p-1)n/p = 2n(1 - 1/p)$: 96 elements at four ranks, 112 at eight, 126 at sixty-four,
approaching 128 and never reaching it. That bounded per-rank cost is what makes the ring
scale; the total across all ranks, $2(p-1)n$, does grow, but it is spread over $p$ links
so that no single link pays more than $2n$. The naive all-to-all plan is the one whose
per-rank cost grows with $p$.
""",
                    },
                    {
                        r"q": r"On a link with $\alpha = 1\ \mu s$ and $\beta = 10$ GB/s, a ring allreduce of one 8-byte element per rank across 1024 ranks takes about 2 ms. Why, and what would help?",
                        "opts": [
                            "It is bandwidth-bound: 2046 messages of 8 bytes saturate the link, so a faster link would help",
                            r"It is latency-bound: 2046 rounds each pay $\alpha$, so a tree collective with about 20 rounds would be a hundred times faster",
                            "The ring is bandwidth-optimal, so 2 ms is the floor for this problem and no algorithm can beat it",
                            "The barrier after each round serialises the ranks; removing the barriers would collapse the whole operation into a single round",
                        ],
                        "a": 1,
                        "whys": [
                            r"$2046 \times 8$ bytes at 10 GB/s is under two microseconds of transfer; the other 2044 microseconds are 2046 latencies, and a faster link would remove almost none of them.",
                            r"$2(p-1)$ rounds at a microsecond each is 2 ms with the bytes contributing nothing; $2\lceil\log_2 p\rceil = 20$ rounds cost 20 microseconds.",
                            r"Optimal in bytes is not optimal in time: the bound is on bandwidth, and at eight bytes bandwidth is not the cost being paid.",
                            r"The rounds are the algorithm's data dependencies, not an artefact of the barrier: a rank cannot forward a chunk it has not yet received, whatever the simulation does.",
                        ],
                        "why": r"""
Each of the $2(p-1) = 2046$ rounds costs $\alpha$ plus the time for 8 bytes, and the
bytes take under a nanosecond, so the whole 2 ms is latency. A tree allreduce pays
$2\lceil\log_2 1024\rceil = 20$ latencies and ships the whole vector at each hop, which
for one element is no penalty at all: 20 microseconds. The ring's bandwidth optimality
is real and irrelevant here, because below about $\alpha\beta = 10$ KB the rounds are
what cost, which is why MPI libraries switch algorithms on message size.
""",
                    },
                    {
                        "q": r"Gathering every vector to rank 0, adding there and broadcasting the sum moves exactly $2(p-1)n$ elements in total, the same as the ring. Why is the ring faster anyway?",
                        "opts": [
                            "Because the ring sends fewer bytes in total once the reduce-scatter has shrunk the chunks",
                            "Because the root plan needs $p - 1$ rounds and the ring needs $2(p-1)$, and more rounds means more chances for the messages to overlap",
                            "Because all of it crosses rank 0's single link in sequence, while the ring puts $1/p$ of the total on every link in every round",
                            "Because floats added on the root in a different order give a different sum on every rank",
                        ],
                        "a": 2,
                        "whys": [
                            r"The totals are equal by the question's own arithmetic, and the ring's chunks are not shrunk, they are portions of the same vector; the difference is where the bytes go, not how many.",
                            r"More rounds is a cost, not a benefit, and the ring pays it; what it buys is that in each round every link is busy rather than one.",
                            r"Same bytes, one link versus $p$ links: the root's link takes $2(p-1)n/\beta$ while each ring link takes $2(p-1)n/(p\beta)$.",
                            r"The root adds one sum and broadcasts it, so every rank receives the identical value; summation order is a precision question, not a speed one.",
                        ],
                        "why": r"""
Total bytes are the same; what differs is how many links carry them at once. In the
root plan every one of the $2(p-1)n$ elements passes through rank 0's link, one message
after another, so the time is $2(p-1)n/\beta$ on that link while the others idle. The
ring gives every rank $2(p-1)$ messages of $n/p$, so each link carries $2(p-1)n/p$ and
all $p$ of them work in parallel. That is the whole design: not fewer bytes, but no
bottleneck link.
""",
                    },
                    {
                        "q": r"A ring implementation sends and applies inside one loop over ranks: it records rank $r$'s send, immediately adds that chunk into rank $r + 1$'s buffer, then moves on to rank $r + 1$'s send. The message count matches the bound exactly, but for some world sizes the sums are wrong. Why?",
                        "opts": [
                            "Python lists are shared between the ranks, so adding in place at rank $r + 1$ also changes what rank $r$ still holds and sends later in the round",
                            "The modulo arithmetic that wraps the last rank back to the first fails unless sending and applying are done in separate loops",
                            "Rank $r + 1$ sends after absorbing rank $r$'s chunk for this round, so one round carries what a real network needs two rounds to deliver",
                            "Applying inside the loop doubles the number of additions, which the bound does not count but which corrupts the chunk sums",
                        ],
                        "a": 2,
                        "whys": [
                            r"Each rank's buffer is its own list copied from its input vector; sharing would be a different bug, and it would corrupt every world size rather than some.",
                            r"$(r + 1) \bmod p$ wraps correctly in either loop shape; wrapping is how the last rank's message reaches rank 0 in both.",
                            r"Sending what you hold at the start of the round is the rule; the snapshot enforces it.",
                            r"The number of additions is the same either way, one per received chunk; what changes is which values those additions see.",
                        ],
                        "why": r"""
In a real round every rank sends what it held when the round began, because the
messages are in flight simultaneously. A loop that applies rank 0's message at rank 1
before rank 1 sends lets rank 1 forward a chunk that already contains rank 0's
contribution, so rank 2 receives two hops' worth in one hop. Depending on $p$ that
double-counts or skips contributions, while the message count, which the bound checks,
is unchanged. Snapshot the outgoing chunks first, then apply them, and the simulation
cannot outrun the wire.
""",
                    },
                    {
                        r"q": r"Broadcasting a 1 MB buffer from rank 0 to seven other ranks with $\alpha = 1\ \mu s$ and $\beta = 10$ GB/s costs about 707 $\mu s$ linearly and about 303 $\mu s$ with a binomial tree. Both send seven messages. Where does the tree's saving come from?",
                        "opts": [
                            "The tree moves fewer bytes overall, because each intermediate rank forwards only the half of the buffer that its subtree has not yet seen",
                            "The tree lets the root send all seven messages simultaneously in a single round",
                            "The tree avoids the root's send buffer being copied seven times, which is where the linear plan spends its time",
                            "In every round every rank that already holds the buffer sends, so the holders double each round instead of growing by one",
                        ],
                        "a": 3,
                        "whys": [
                            r"Every one of the seven messages carries the whole megabyte in both plans; $(p-1)ne$ bytes is the same figure, and the saving is entirely in rounds.",
                            r"The root sends exactly once per round in the tree, to relative rank `mask`; it is the other holders sending in parallel that fills the round out.",
                            r"Copying a buffer is memory bandwidth, not network; the linear plan's 707 microseconds are seven sequential messages of 101 microseconds each.",
                            r"One, two, four, eight: three rounds of $\alpha + m/\beta$ against seven.",
                        ],
                        "why": r"""
Both plans send $p - 1 = 7$ messages of 1 MB, so the bytes are identical. The linear
plan sends them one after another from the root, seven rounds of about 101
microseconds. The tree has every rank that holds the buffer send in every round, so the
holders go 1, 2, 4, 8 and seven ranks are reached in $\lceil \log_2 8 \rceil = 3$ rounds
of the same 101 microseconds. The saving is in rounds, and it is the same saving whether
the message is one megabyte or eight bytes.
""",
                    },
                    {
                        "q": r"`allreduce_bytes_bound(4, 8)` is 384 while `broadcast_bytes_bound(4, 8)` is 192. Why does an allreduce cost exactly twice a broadcast in bytes?",
                        "opts": [
                            "Because every rank both sends and receives in an allreduce, whereas in a broadcast only the root sends",
                            "Because each of the $p$ chunks needs $p - 1$ arrivals to be summed and $p - 1$ departures to be shared: two broadcasts' worth",
                            "Because the ring carries the vector once around in each direction, forward to build the sum and backward to distribute the copies",
                            "Because the summed values are larger numbers than the inputs and take twice as many bytes to represent",
                        ],
                        "a": 1,
                        "whys": [
                            r"Who sends is not what the bound counts; a broadcast tree also has many senders, and the bound is about how many chunk transfers the result requires.",
                            r"Reduce-scatter is $(p-1)n$ elements and allgather is $(p-1)n$ more; each half moves what a broadcast of $n$ elements to $p - 1$ ranks moves.",
                            r"The ring sends in one direction throughout; the two phases are both clockwise, and direction has nothing to do with the byte count.",
                            r"An 8-byte double is 8 bytes whatever its value; `elem_bytes` is a constant, and sums of doubles are still doubles.",
                        ],
                        "why": r"""
An allreduce is two collectives. Reduce-scatter must bring $p - 1$ contributions to each
chunk from the other ranks, $(p-1)n$ elements, and allgather must then deliver each
finished chunk to the $p - 1$ ranks that lack it, another $(p-1)n$. A broadcast is only
the second of those: $(p-1)n$ elements to get one vector to everyone. So $2(p-1)ne$
against $(p-1)ne$, and at $p = 4$, $n = 8$ that is 384 against 192. Element size and
message direction never enter the count.
""",
                    },
                ],
            },
            "lab": {
                "title": "A simulated MPI world",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
A `World` is a message counter, not a network. Every algorithm you write must
declare each message it sends, and the tests compare the total against the
analytic bound.

## `World(size, elem_bytes=8)`

Attributes `size`, `elem_bytes`, `messages`, `elements`, `rounds`, and `log`
(a list of `(src, dst, count)`). A read-only property `bytes_moved` returns
`elements * elem_bytes`.

- `send(src, dst, count)` — record one message of `count` elements. Raise
  `ValueError` for a rank outside `range(size)`, for `src == dst`, or for a
  negative `count`.
- `barrier()` — bump `rounds` by one. Call it once per communication round.

`World(0)` and a non-positive `elem_bytes` raise `ValueError`.

## `ring_allreduce(world, vectors)`

`vectors` is one list per rank, all the same length `n`, with `n` divisible by
`world.size`. Return one summed vector per rank (all equal).

Split each vector into `p` chunks of `n // p`. Run `p - 1` **reduce-scatter**
rounds: in round `s`, rank `r` sends chunk `(r - s) % p` to rank `(r + 1) % p`
and adds the chunk it receives into its own copy. Then `p - 1` **allgather**
rounds: in round `s`, rank `r` sends chunk `(r + 1 - s) % p` onward and
overwrites the chunk it receives. Every rank sends in a round *before* any rank
applies what it received — snapshot the outgoing chunks first.

Wrong vector count, ragged lengths and an indivisible length all raise `ValueError`.

## `broadcast_tree(world, root, value)`

`value` is a list. Return a list of `world.size` copies. Work in ranks relative
to `root`: with `mask` doubling from 1 while `mask < p`, every relative rank
below `mask` sends to relative rank `rel + mask` when that is in range. One
`barrier()` per mask. An out-of-range `root` raises `ValueError`.

## The bounds

```text
allreduce_bytes_bound(p, n, elem_bytes=8)  ->  2 * (p - 1) * n * elem_bytes
broadcast_bytes_bound(p, n, elem_bytes=8)  ->  (p - 1) * n * elem_bytes
broadcast_rounds(p)                        ->  ceil(log2(p))
```

`p` below 1 raises `ValueError`. With `p = 4`, `n = 8` and 8-byte elements the
allreduce must send exactly 24 messages and 384 bytes — the bound, to the byte.
''',
                "files": [{"name": "main.py", "content": r'''
import random


class World:
    """A message counter standing in for an MPI communicator."""

    def __init__(self, size, elem_bytes=8):
        # your code here
        pass

    @property
    def bytes_moved(self):
        """elements * elem_bytes."""
        # your code here

    def send(self, src, dst, count):
        """Record one message of count elements from src to dst."""
        # your code here

    def barrier(self):
        """Mark the end of one communication round."""
        # your code here


def ring_allreduce(world, vectors):
    """Reduce-scatter then allgather; returns the summed vector for every rank."""
    # your code here


def broadcast_tree(world, root, value):
    """Binomial-tree broadcast; returns what every rank ends up holding."""
    # your code here


def allreduce_bytes_bound(p, n, elem_bytes=8):
    """Bytes a ring allreduce must move in total."""
    # your code here


def broadcast_bytes_bound(p, n, elem_bytes=8):
    """Bytes a broadcast must move in total."""
    # your code here


def broadcast_rounds(p):
    """ceil(log2(p)) rounds."""
    # your code here


rng = random.Random(7)
P, N = 4, 8
world = World(P)
vectors = [[rng.randrange(0, 10) for _ in range(N)] for _ in range(P)]
result = ring_allreduce(world, vectors)
print("all ranks agree:", all(r == result[0] for r in result))
print(f"messages: {world.messages}  bytes: {world.bytes_moved}  "
      f"bound: {allreduce_bytes_bound(P, N)}")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import random


class World:
    """A message counter standing in for an MPI communicator."""

    def __init__(self, size, elem_bytes=8):
        if size < 1:
            raise ValueError("world size must be at least 1")
        if elem_bytes < 1:
            raise ValueError("elem_bytes must be at least 1")
        self.size = size
        self.elem_bytes = elem_bytes
        self.messages = 0
        self.elements = 0
        self.rounds = 0
        self.log = []

    @property
    def bytes_moved(self):
        """elements * elem_bytes."""
        return self.elements * self.elem_bytes

    def send(self, src, dst, count):
        """Record one message of count elements from src to dst."""
        if not 0 <= src < self.size or not 0 <= dst < self.size:
            raise ValueError(f"rank out of range: {src} -> {dst}")
        if src == dst:
            raise ValueError("a rank must not send to itself")
        if count < 0:
            raise ValueError("count must not be negative")
        self.messages += 1
        self.elements += count
        self.log.append((src, dst, count))

    def barrier(self):
        """Mark the end of one communication round."""
        self.rounds += 1


def ring_allreduce(world, vectors):
    """Reduce-scatter then allgather; returns the summed vector for every rank."""
    p = world.size
    if len(vectors) != p:
        raise ValueError(f"expected {p} vectors, got {len(vectors)}")
    n = len(vectors[0])
    if any(len(v) != n for v in vectors):
        raise ValueError("every rank must contribute the same length")
    if n % p:
        raise ValueError(f"vector length {n} is not divisible by world size {p}")
    bufs = [list(v) for v in vectors]
    chunk = n // p
    for stage in range(p - 1):
        outgoing = []
        for r in range(p):
            c = (r - stage) % p
            outgoing.append(bufs[r][c * chunk:(c + 1) * chunk])
            world.send(r, (r + 1) % p, chunk)
        for r in range(p):
            src = (r - 1) % p
            base = ((src - stage) % p) * chunk
            piece = outgoing[src]
            for i in range(chunk):
                bufs[r][base + i] += piece[i]
        world.barrier()
    for stage in range(p - 1):
        outgoing = []
        for r in range(p):
            c = (r + 1 - stage) % p
            outgoing.append(bufs[r][c * chunk:(c + 1) * chunk])
            world.send(r, (r + 1) % p, chunk)
        for r in range(p):
            src = (r - 1) % p
            c = (src + 1 - stage) % p
            bufs[r][c * chunk:(c + 1) * chunk] = outgoing[src]
        world.barrier()
    return bufs


def broadcast_tree(world, root, value):
    """Binomial-tree broadcast; returns what every rank ends up holding."""
    p = world.size
    if not 0 <= root < p:
        raise ValueError(f"root {root} is not a rank in this world")
    count = len(value)
    held = [None] * p
    held[root] = list(value)
    mask = 1
    while mask < p:
        for rel in range(mask):
            dst_rel = rel + mask
            if dst_rel < p:
                src = (rel + root) % p
                dst = (dst_rel + root) % p
                world.send(src, dst, count)
                held[dst] = list(held[src])
        world.barrier()
        mask *= 2
    return held


def allreduce_bytes_bound(p, n, elem_bytes=8):
    """Bytes a ring allreduce must move in total."""
    if p < 1:
        raise ValueError("p must be at least 1")
    return 2 * (p - 1) * n * elem_bytes


def broadcast_bytes_bound(p, n, elem_bytes=8):
    """Bytes a broadcast must move in total."""
    if p < 1:
        raise ValueError("p must be at least 1")
    return (p - 1) * n * elem_bytes


def broadcast_rounds(p):
    """ceil(log2(p)) rounds."""
    if p < 1:
        raise ValueError("p must be at least 1")
    return (p - 1).bit_length()


rng = random.Random(7)
P, N = 4, 8
world = World(P)
vectors = [[rng.randrange(0, 10) for _ in range(N)] for _ in range(P)]
result = ring_allreduce(world, vectors)
print("all ranks agree:", all(r == result[0] for r in result))
print(f"messages: {world.messages}  bytes: {world.bytes_moved}  "
      f"bound: {allreduce_bytes_bound(P, N)}")
'''}],
                "hints": [
                    "`bytes_moved` is a `@property`, so it recomputes from `elements` every time you read it — never store it.",
                    "Snapshot before you apply: build the whole `outgoing` list for the round first, then run a second loop that adds or overwrites. Applying inside the send loop lets a rank forward data it only just received.",
                    "In reduce-scatter round `s`, rank `r` receives from `(r - 1) % p` the chunk that rank sent, which is `((r - 1 - s) % p)`. Index it from the sender, not from the receiver.",
                    "`(p - 1).bit_length()` is exactly ceil(log2(p)) for p >= 1, and gives 0 for a world of one.",
                ],
                "tests": [
                    {"name": "World validates and accounts", "code": r'''
_w = World(4)
assert (_w.messages, _w.elements, _w.bytes_moved, _w.rounds) == (0, 0, 0, 0), "a fresh world is quiet"
_w.send(0, 1, 5)
_w.send(1, 2, 3)
assert _w.messages == 2 and _w.elements == 8, f"Got {_w.messages} messages, {_w.elements} elements"
assert _w.bytes_moved == 64, f"bytes_moved gave {_w.bytes_moved!r}, expected 64"
assert _w.log == [(0, 1, 5), (1, 2, 3)], f"log is {_w.log!r}"
_w.barrier()
assert _w.rounds == 1, f"rounds is {_w.rounds!r}, expected 1"
assert World(4, 4).bytes_moved == 0 and World(2).elem_bytes == 8, "elem_bytes defaults to 8"
'''},
                    {"name": "World rejects impossible sends", "code": r'''
for _bad in (0, -3):
    try:
        World(_bad)
        assert False, f"World({_bad}) should raise ValueError"
    except ValueError:
        pass
try:
    World(4, 0)
    assert False, "World(4, 0) should raise ValueError"
except ValueError:
    pass
_w = World(3)
for _args in [(1, 1, 4), (0, 3, 4), (-1, 2, 4), (0, 1, -2)]:
    try:
        _w.send(*_args)
        assert False, f"send{_args!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "ring_allreduce sums every element", "code": r'''
import random as _random
for _p, _n in [(1, 4), (2, 4), (4, 8), (4, 4), (5, 10), (8, 16)]:
    _rng = _random.Random(3)
    _w = World(_p)
    _vecs = [[_rng.randrange(0, 10) for _ in range(_n)] for _ in range(_p)]
    _want = [sum(v[i] for v in _vecs) for i in range(_n)]
    _got = ring_allreduce(_w, _vecs)
    assert len(_got) == _p, f"p={_p}: got {len(_got)} results, expected {_p}"
    for _r, _res in enumerate(_got):
        assert _res == _want, f"p={_p} rank {_r} holds {_res!r}, expected {_want!r}"
'''},
                    {"name": "ring_allreduce hits the bandwidth bound exactly", "code": r'''
_w = World(4)
ring_allreduce(_w, [[1] * 8 for _ in range(4)])
assert _w.messages == 24, f"p=4 sent {_w.messages} messages, expected 2*p*(p-1) = 24"
assert _w.bytes_moved == 384, f"p=4 moved {_w.bytes_moved} bytes, expected 384"
assert _w.bytes_moved == allreduce_bytes_bound(4, 8), "the measurement must equal the bound"
assert _w.rounds == 6, f"p=4 used {_w.rounds} rounds, expected 2*(p-1) = 6"
_w1 = World(1)
assert ring_allreduce(_w1, [[1, 2, 3]]) == [[1, 2, 3]], "one rank needs no messages at all"
assert _w1.messages == 0 and allreduce_bytes_bound(1, 3) == 0, "and moves no bytes"
_w8 = World(8)
ring_allreduce(_w8, [[1] * 16 for _ in range(8)])
assert _w8.bytes_moved == allreduce_bytes_bound(8, 16) == 1792, \
    f"p=8 moved {_w8.bytes_moved} bytes, expected 1792"
'''},
                    {"name": "ring_allreduce rejects bad input", "code": r'''
try:
    ring_allreduce(World(4), [[1, 2, 3, 4]] * 3)
    assert False, "too few vectors should raise ValueError"
except ValueError:
    pass
try:
    ring_allreduce(World(2), [[1, 2], [1, 2, 3]])
    assert False, "ragged vectors should raise ValueError"
except ValueError:
    pass
try:
    ring_allreduce(World(4), [[1, 2, 3]] * 4)
    assert False, "a length not divisible by p should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "broadcast_tree reaches every rank once", "code": r'''
for _p in (1, 2, 3, 4, 5, 8):
    _w = World(_p)
    _held = broadcast_tree(_w, 0, [1.0, 2.0, 3.0])
    assert _held == [[1.0, 2.0, 3.0]] * _p, f"p={_p}: ranks hold {_held!r}"
    assert _w.messages == _p - 1, f"p={_p} sent {_w.messages} messages, expected {_p - 1}"
    assert _w.bytes_moved == broadcast_bytes_bound(_p, 3), \
        f"p={_p} moved {_w.bytes_moved} bytes, expected {broadcast_bytes_bound(_p, 3)}"
    assert _w.rounds == broadcast_rounds(_p), \
        f"p={_p} used {_w.rounds} rounds, expected {broadcast_rounds(_p)}"
_w = World(4)
_held = broadcast_tree(_w, 2, [7.0])
assert _held == [[7.0]] * 4, f"a non-zero root should still reach everyone: {_held!r}"
assert _w.messages == 3, f"root=2 sent {_w.messages} messages, expected 3"
try:
    broadcast_tree(World(4), 4, [1.0])
    assert False, "an out-of-range root should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "The closed-form bounds", "code": r'''
assert broadcast_rounds(1) == 0, "one rank needs no rounds"
for _p, _want in [(2, 1), (3, 2), (4, 2), (5, 3), (8, 3), (9, 4), (16, 4)]:
    assert broadcast_rounds(_p) == _want, f"broadcast_rounds({_p}) gave {broadcast_rounds(_p)!r}, expected {_want}"
assert allreduce_bytes_bound(4, 8) == 384 and broadcast_bytes_bound(4, 8) == 192, \
    "the allreduce moves exactly twice the bytes of the broadcast"
assert allreduce_bytes_bound(4, 8, 4) == 192, "elem_bytes scales the bound linearly"
for _fn in (allreduce_bytes_bound, broadcast_bytes_bound, broadcast_rounds):
    try:
        _fn(0, 8) if _fn is not broadcast_rounds else _fn(0)
        assert False, f"{_fn.__name__} should raise ValueError for p=0"
    except ValueError:
        pass
assert "all ranks agree: True" in _out, "main.py should report that every rank ends with the same vector"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — an optimisation study with an Amdahl account",
        "runtime": "python",
        "minutes": 240,
        "brief": r'''
You are handed a working but slow kernel and asked to make it fast *and* to say
exactly why each stage helped. `kernel.py` holds the logic and is what the
checks import; `main.py` is the study — it prints the speedup table and the
serial fraction the measurement implies.

## The kernel

A three-point weighted stencil applied `steps` times to a signal of `n` floats,
with the two end samples held fixed:

```text
y[0]   = x[0]
y[n-1] = x[n-1]
y[i]   = w0*x[i-1] + w1*x[i] + w2*x[i+1]      for 1 <= i <= n-2
```

`build_operator(n, weights)` and `stencil_v0` are **given**. `v0` rebuilds the
dense n x n operator matrix on every step and does a full matrix-vector product:
O(steps * n^2) time and O(steps * n^2) allocation.

## The stages

Each stage must return a result **bit-for-bit identical** to `stencil_v0`. That
is achievable, and it is the discipline the whole exercise rests on: keep the
three products in the order `w0*left + w1*centre + w2*right`, and adding the
exact zeros of the dense row changes nothing.

- **`stencil_v1`** — hoist the matrix build out of the step loop. Same
  arithmetic, one call to `build_operator` instead of `steps` calls.
- **`stencil_v2`** — drop the matrix. Touch only the three band entries, so the
  cost falls from O(n^2) to O(n) per step.
- **`stencil_v3`** — `v2` plus two allocated buffers swapped each step (no list
  is built inside the loop) and the three samples carried in local registers
  `a, b, c` so each element is read from the list once.

All four raise `ValueError` for `n < 2` or a negative `steps`, and return a copy
of the input for `steps == 0`.

## The analysis

- **`time_stages(x, weights, steps, repeats=1)`** — `{stage: best seconds}` for
  all four, minimum of `repeats` runs. `repeats < 1` raises `ValueError`.
- **`speedup_table(timings, baseline="v0")`** — a list of
  `{"stage", "seconds", "speedup"}` in `STAGES` order, `speedup = t_baseline / t_stage`.
  An unknown baseline raises `ValueError`.
- **`amdahl_speedup(serial_fraction, workers)`** — `1 / (s + (1-s)/w)`.
- **`serial_fraction_from_speedup(speedup, workers)`** — invert it:
  `(1/S - 1/w) / (1 - 1/w)`. `workers <= 1` cannot identify `s`, so raise
  `ValueError`; so does a non-positive speedup.
- **`max_speedup(serial_fraction)`** — `1/s`, and `inf` when `s` is 0.

A serial fraction outside `[0, 1]` or fewer than one worker raises `ValueError`.

## What the study should say

The interesting number is not the raw speedup. It is that once `v3` has removed
the O(n^2) term, whatever is left that does not shrink — the loop overhead, the
boundary handling, the buffer swap — is the serial fraction that caps everything
you do next.
''',
        "deliverables": [
            "`kernel.py` — `stencil_v1`, `v2`, `v3` returning results identical to `stencil_v0`",
            "`kernel.py` — the timing harness, the speedup table and the three Amdahl functions",
            "`main.py` — a study that prints a stage/seconds/speedup table for a real signal",
            "`main.py` — the serial fraction implied by the best measured speedup, and the ceiling it sets",
            "Input validation: `n < 2`, negative `steps`, bad baselines and impossible worker counts all raise `ValueError`",
            "Evidence that every stage is bit-for-bit equal to the supplied kernel, not merely close",
        ],
        "constraints": [
            "Standard library only; `time` and `random` are the only imports you need",
            "`kernel.py` must define names only — importing it must print nothing",
            "No stage may call another stage: each one is a self-contained implementation",
            "Only `stencil_v0` and `stencil_v1` may call `build_operator`; `v2` and `v3` must never build a matrix",
            "Timings come from `time.perf_counter` and report the minimum, never the mean",
        ],
        "rubric": [
            {"criterion": "Numerical fidelity", "weight": 30,
             "evidence": "Every stage returns exactly the same list as stencil_v0 for even, odd, minimal and zero-step cases."},
            {"criterion": "Optimisation quality", "weight": 25,
             "evidence": "v1 calls build_operator once; v2 and v3 never build a matrix and are measurably an order of magnitude faster than v0."},
            {"criterion": "Measurement method", "weight": 20,
             "evidence": "time_stages repeats and reports the minimum; the speedup table is derived from the baseline rather than hand-written."},
            {"criterion": "Amdahl analysis", "weight": 15,
             "evidence": "The forward and inverse laws round-trip, and main.py states the serial fraction and the ceiling it implies."},
            {"criterion": "Interface discipline", "weight": 10,
             "evidence": "kernel.py is import-clean, every documented ValueError is raised, and no stage delegates to another."},
        ],
        "hints": [
            "Start by copying `stencil_v0` into `stencil_v1` and moving the single `build_operator` line above the `for _ in range(steps)` loop. Nothing else changes.",
            "For `v2`, write the boundaries first (`nxt[0] = cur[0]`, `nxt[n-1] = cur[n-1]`) and then loop `for i in range(1, n - 1)`. Bind `w0, w1, w2 = weights` outside the step loop.",
            "For `v3`, allocate `cur` and `nxt` once, and end each step with `cur, nxt = nxt, cur`. Return `list(cur)` so the caller cannot see your scratch buffer.",
            "The register roll is `a = cur[0]; b = cur[1]`, then inside the loop `c = cur[i + 1]`, write the element, and finish with `a = b; b = c`.",
            "Invert Amdahl algebraically before you code it: from `S = 1/(s + (1-s)/w)` you get `1/S = s(1 - 1/w) + 1/w`, hence `s = (1/S - 1/w) / (1 - 1/w)`.",
        ],
        "files": [
            {"name": "kernel.py", "content": r'''
import random
import time

STAGES = ("v0", "v1", "v2", "v3")


def make_signal(n, seed=7):
    """A deterministic test signal of n samples in [-1, 1]."""
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(n)]


def build_operator(n, weights):
    """The dense n x n stencil matrix, with identity rows at both ends."""
    w0, w1, w2 = weights
    m = [[0.0] * n for _ in range(n)]
    m[0][0] = 1.0
    m[n - 1][n - 1] = 1.0
    for i in range(1, n - 1):
        m[i][i - 1] = w0
        m[i][i] = w1
        m[i][i + 1] = w2
    return m


def stencil_v0(x, weights, steps):
    """Supplied baseline: rebuild the dense operator every step."""
    n = len(x)
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    if steps < 0:
        raise ValueError("steps must not be negative")
    cur = list(x)
    for _ in range(steps):
        m = build_operator(n, weights)
        nxt = [0.0] * n
        for i in range(n):
            row = m[i]
            total = 0.0
            for j in range(n):
                total += row[j] * cur[j]
            nxt[i] = total
        cur = nxt
    return cur


def stencil_v1(x, weights, steps):
    """Stage 1: build the operator once."""
    # your code here


def stencil_v2(x, weights, steps):
    """Stage 2: touch only the band."""
    # your code here


def stencil_v3(x, weights, steps):
    """Stage 3: ping-pong buffers and rolling registers."""
    # your code here


STAGE_FUNCTIONS = {"v0": stencil_v0, "v1": stencil_v1,
                   "v2": stencil_v2, "v3": stencil_v3}


def time_stages(x, weights, steps, repeats=1):
    """{stage: best elapsed seconds} for every stage."""
    # your code here


def speedup_table(timings, baseline="v0"):
    """Rows of {"stage", "seconds", "speedup"} in STAGES order."""
    # your code here


def amdahl_speedup(serial_fraction, workers):
    """Amdahl's law: the speedup this serial fraction allows."""
    # your code here


def serial_fraction_from_speedup(speedup, workers):
    """The serial fraction a measured speedup implies."""
    # your code here


def max_speedup(serial_fraction):
    """The ceiling as the worker count goes to infinity."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from kernel import (STAGES, make_signal, stencil_v0, stencil_v1, stencil_v2,
                    stencil_v3, time_stages, speedup_table, amdahl_speedup,
                    serial_fraction_from_speedup, max_speedup)

WEIGHTS = (0.25, 0.5, 0.25)
STEPS = 6
SIGNAL = make_signal(200)

# 1. confirm every stage is bit-for-bit equal to stencil_v0
# 2. time the stages and print a stage / seconds / speedup table
# 3. print the serial fraction the best speedup implies, and its ceiling
print("study not written yet")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "kernel.py", "content": r'''
import random
import time

STAGES = ("v0", "v1", "v2", "v3")


def make_signal(n, seed=7):
    """A deterministic test signal of n samples in [-1, 1]."""
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    rng = random.Random(seed)
    return [rng.uniform(-1.0, 1.0) for _ in range(n)]


def build_operator(n, weights):
    """The dense n x n stencil matrix, with identity rows at both ends."""
    w0, w1, w2 = weights
    m = [[0.0] * n for _ in range(n)]
    m[0][0] = 1.0
    m[n - 1][n - 1] = 1.0
    for i in range(1, n - 1):
        m[i][i - 1] = w0
        m[i][i] = w1
        m[i][i + 1] = w2
    return m


def stencil_v0(x, weights, steps):
    """Supplied baseline: rebuild the dense operator every step."""
    n = len(x)
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    if steps < 0:
        raise ValueError("steps must not be negative")
    cur = list(x)
    for _ in range(steps):
        m = build_operator(n, weights)
        nxt = [0.0] * n
        for i in range(n):
            row = m[i]
            total = 0.0
            for j in range(n):
                total += row[j] * cur[j]
            nxt[i] = total
        cur = nxt
    return cur


def stencil_v1(x, weights, steps):
    """Stage 1: build the operator once."""
    n = len(x)
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    if steps < 0:
        raise ValueError("steps must not be negative")
    cur = list(x)
    if steps == 0:
        return cur
    m = build_operator(n, weights)
    for _ in range(steps):
        nxt = [0.0] * n
        for i in range(n):
            row = m[i]
            total = 0.0
            for j in range(n):
                total += row[j] * cur[j]
            nxt[i] = total
        cur = nxt
    return cur


def stencil_v2(x, weights, steps):
    """Stage 2: touch only the band."""
    n = len(x)
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    if steps < 0:
        raise ValueError("steps must not be negative")
    w0, w1, w2 = weights
    cur = list(x)
    for _ in range(steps):
        nxt = [0.0] * n
        nxt[0] = cur[0]
        nxt[n - 1] = cur[n - 1]
        for i in range(1, n - 1):
            nxt[i] = w0 * cur[i - 1] + w1 * cur[i] + w2 * cur[i + 1]
        cur = nxt
    return cur


def stencil_v3(x, weights, steps):
    """Stage 3: ping-pong buffers and rolling registers."""
    n = len(x)
    if n < 2:
        raise ValueError("a signal needs at least two samples")
    if steps < 0:
        raise ValueError("steps must not be negative")
    w0, w1, w2 = weights
    cur = list(x)
    nxt = list(x)
    for _ in range(steps):
        a = cur[0]
        b = cur[1]
        nxt[0] = a
        for i in range(1, n - 1):
            c = cur[i + 1]
            nxt[i] = w0 * a + w1 * b + w2 * c
            a = b
            b = c
        nxt[n - 1] = cur[n - 1]
        cur, nxt = nxt, cur
    return list(cur)


STAGE_FUNCTIONS = {"v0": stencil_v0, "v1": stencil_v1,
                   "v2": stencil_v2, "v3": stencil_v3}


MIN_SAMPLE = 0.005   # seconds; must clear the platform timer's resolution


def time_stages(x, weights, steps, repeats=1):
    """{stage: best per-call seconds} for every stage.

    A single call to a fast stage can finish inside one tick of the clock, and
    browser timers are deliberately coarse. Measuring that gives 0.0 seconds and
    an infinite speedup. So auto-range like timeit does: keep multiplying the
    number of calls until the batch takes longer than MIN_SAMPLE, then divide.
    """
    if repeats < 1:
        raise ValueError("repeats must be at least 1")
    timings = {}
    for name in STAGES:
        fn = STAGE_FUNCTIONS[name]
        best = None
        for _ in range(repeats):
            calls = 1
            while True:
                start = time.perf_counter()
                for _ in range(calls):
                    fn(x, weights, steps)
                elapsed = time.perf_counter() - start
                if elapsed >= MIN_SAMPLE or calls >= 8192:
                    break
                calls *= 4
            per_call = elapsed / calls
            if best is None or per_call < best:
                best = per_call
        timings[name] = best
    return timings


def speedup_table(timings, baseline="v0"):
    """Rows of {"stage", "seconds", "speedup"} in STAGES order."""
    if baseline not in timings:
        raise ValueError(f"no timing for baseline stage {baseline!r}")
    base = timings[baseline]
    rows = []
    for name in STAGES:
        if name in timings:
            seconds = timings[name]
            rows.append({"stage": name, "seconds": seconds,
                         "speedup": base / seconds if seconds > 0 else float("inf")})
    return rows


def amdahl_speedup(serial_fraction, workers):
    """Amdahl's law: the speedup this serial fraction allows."""
    if not 0.0 <= serial_fraction <= 1.0:
        raise ValueError("serial_fraction must lie in [0, 1]")
    if workers < 1:
        raise ValueError("workers must be at least 1")
    return 1.0 / (serial_fraction + (1.0 - serial_fraction) / workers)


def serial_fraction_from_speedup(speedup, workers):
    """The serial fraction a measured speedup implies."""
    if workers <= 1:
        raise ValueError("workers must exceed 1 to identify a serial fraction")
    if speedup <= 0:
        raise ValueError("speedup must be positive")
    return (1.0 / speedup - 1.0 / workers) / (1.0 - 1.0 / workers)


def max_speedup(serial_fraction):
    """The ceiling as the worker count goes to infinity."""
    if not 0.0 <= serial_fraction <= 1.0:
        raise ValueError("serial_fraction must lie in [0, 1]")
    if serial_fraction == 0.0:
        return float("inf")
    return 1.0 / serial_fraction
'''},
            {"name": "main.py", "content": r'''
from kernel import (STAGES, make_signal, stencil_v0, stencil_v1, stencil_v2,
                    stencil_v3, time_stages, speedup_table, amdahl_speedup,
                    serial_fraction_from_speedup, max_speedup)

WEIGHTS = (0.25, 0.5, 0.25)
STEPS = 6
SIGNAL = make_signal(200)

reference = stencil_v0(SIGNAL, WEIGHTS, STEPS)
identical = all(fn(SIGNAL, WEIGHTS, STEPS) == reference
                for fn in (stencil_v1, stencil_v2, stencil_v3))
print("all stages bit-identical:", identical)

timings = time_stages(SIGNAL, WEIGHTS, STEPS, repeats=3)
print(f"{'stage':<8}{'seconds':>12}{'speedup':>12}")
for row in speedup_table(timings):
    print(f"{row['stage']:<8}{row['seconds']:>12.6f}{row['speedup']:>12.2f}")

best = max(speedup_table(timings), key=lambda row: row["speedup"])
workers = 4
serial = serial_fraction_from_speedup(min(best["speedup"], float(workers)), workers)
serial = max(serial, 0.0)
print(f"implied serial fraction at {workers} workers: {serial:.4f}")
print(f"ceiling from that fraction: {max_speedup(serial):.2f}x")
print(f"predicted speedup at 64 workers: {amdahl_speedup(serial, 64):.2f}x")
'''},
        ],
        "tests": [
            {"name": "Every stage is bit-for-bit equal to the baseline", "code": r'''
import kernel as _kernel
_w = (0.25, 0.5, 0.25)
for _n, _steps in [(2, 3), (3, 4), (5, 0), (5, 1), (9, 7), (40, 5), (61, 2)]:
    _x = _kernel.make_signal(_n)
    _want = _kernel.stencil_v0(_x, _w, _steps)
    for _name in ("v1", "v2", "v3"):
        _got = _kernel.STAGE_FUNCTIONS[_name](_x, _w, _steps)
        assert _got == _want, f"stencil_{_name} differs from stencil_v0 at n={_n}, steps={_steps}"
'''},
            {"name": "Stages leave the input alone and copy the output", "code": r'''
import kernel as _kernel
_w = (0.3, 0.4, 0.3)
_x = _kernel.make_signal(12)
_before = list(_x)
for _name in ("v1", "v2", "v3"):
    _out1 = _kernel.STAGE_FUNCTIONS[_name](_x, _w, 5)
    assert _x == _before, f"stencil_{_name} modified the input signal in place"
    _out1[0] = 999.0
    _out2 = _kernel.STAGE_FUNCTIONS[_name](_x, _w, 5)
    assert _out2[0] != 999.0, f"stencil_{_name} handed back a buffer it still owns"
assert _kernel.stencil_v3(_x, _w, 0) == list(_x), "zero steps returns a copy of the input"
'''},
            {"name": "Stages validate their arguments", "code": r'''
import kernel as _kernel
_w = (0.25, 0.5, 0.25)
for _name in ("v0", "v1", "v2", "v3"):
    _fn = _kernel.STAGE_FUNCTIONS[_name]
    try:
        _fn([1.0], _w, 3)
        assert False, f"stencil_{_name} should raise ValueError for a one-sample signal"
    except ValueError:
        pass
    try:
        _fn([1.0, 2.0, 3.0], _w, -1)
        assert False, f"stencil_{_name} should raise ValueError for negative steps"
    except ValueError:
        pass
try:
    _kernel.make_signal(1)
    assert False, "make_signal(1) should raise ValueError"
except ValueError:
    pass
assert _kernel.make_signal(6) == _kernel.make_signal(6), "make_signal must be deterministic"
'''},
            {"name": "v1 builds the operator once; v2 and v3 never build it", "code": r'''
import kernel as _kernel
_w = (0.25, 0.5, 0.25)
_x = _kernel.make_signal(20)
_real = _kernel.build_operator
_calls = []
def _spy(n, weights):
    _calls.append(n)
    return _real(n, weights)
_kernel.build_operator = _spy
try:
    _calls.clear()
    _kernel.stencil_v0(_x, _w, 5)
    _v0_calls = len(_calls)
    _calls.clear()
    _kernel.stencil_v1(_x, _w, 5)
    _v1_calls = len(_calls)
    _calls.clear()
    _kernel.stencil_v2(_x, _w, 5)
    _kernel.stencil_v3(_x, _w, 5)
    _band_calls = len(_calls)
finally:
    _kernel.build_operator = _real
assert _v0_calls == 5, f"the baseline should build the matrix 5 times, it built it {_v0_calls}"
assert _v1_calls == 1, f"stencil_v1 built the matrix {_v1_calls} times, expected exactly 1"
assert _band_calls == 0, f"v2 and v3 built a matrix {_band_calls} times; they must touch only the band"
'''},
            {"name": "No stage delegates to another", "code": r'''
import inspect as _inspect
import kernel as _kernel
for _name in ("v1", "v2", "v3"):
    _src = _inspect.getsource(_kernel.STAGE_FUNCTIONS[_name])
    for _other in ("stencil_v0", "stencil_v1", "stencil_v2", "stencil_v3"):
        if _other.endswith(_name):
            continue
        assert _other not in _src, f"stencil_{_name} calls {_other} — each stage stands alone"
'''},
            {"name": "time_stages measures all four stages", "code": r'''
import kernel as _kernel
_w = (0.25, 0.5, 0.25)
_x = _kernel.make_signal(200)
_timings = _kernel.time_stages(_x, _w, 6)
assert set(_timings) == set(_kernel.STAGES), f"time_stages returned keys {sorted(_timings)!r}"
for _k, _v in _timings.items():
    assert isinstance(_v, float) and _v > 0.0, f"timing for {_k} was {_v!r}, expected a positive float"
try:
    _kernel.time_stages(_x, _w, 6, 0)
    assert False, "time_stages with repeats=0 should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The band stages really are an order of magnitude faster", "code": r'''
import kernel as _kernel
_w = (0.25, 0.5, 0.25)
_x = _kernel.make_signal(200)
_timings = _kernel.time_stages(_x, _w, 6, repeats=2)
_rows = {_r["stage"]: _r["speedup"] for _r in _kernel.speedup_table(_timings)}
assert _rows["v2"] > 5.0, f"v2 was only {_rows['v2']:.2f}x faster than v0 — it is still O(n^2)"
assert _rows["v3"] > 5.0, f"v3 was only {_rows['v3']:.2f}x faster than v0"
'''},
            {"name": "speedup_table shape and baseline", "code": r'''
import kernel as _kernel
_fake = {"v0": 0.8, "v1": 0.4, "v2": 0.1, "v3": 0.05}
_rows = _kernel.speedup_table(_fake)
assert [_r["stage"] for _r in _rows] == list(_kernel.STAGES), f"rows came back as {_rows!r}"
assert _rows[0]["speedup"] == 1.0, "the baseline row must have speedup 1.0"
assert abs(_rows[2]["speedup"] - 8.0) < 1e-12, f"v2 speedup was {_rows[2]['speedup']!r}, expected 8.0"
_rows2 = _kernel.speedup_table(_fake, baseline="v2")
assert abs(_rows2[0]["speedup"] - 0.125) < 1e-12, f"with baseline v2, v0 should be 0.125x"
try:
    _kernel.speedup_table(_fake, baseline="v9")
    assert False, "an unknown baseline should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Amdahl, forward", "code": r'''
import kernel as _kernel
_got = _kernel.amdahl_speedup(0.1, 8)
assert abs(_got - 80 / 17) < 1e-12, f"amdahl_speedup(0.1, 8) gave {_got!r}, expected 4.705882352941176"
assert _kernel.amdahl_speedup(0.0, 8) == 8.0, "a perfectly parallel program scales linearly"
assert _kernel.amdahl_speedup(1.0, 8) == 1.0, "a wholly serial program does not scale at all"
assert _kernel.amdahl_speedup(0.25, 1) == 1.0, "one worker is never faster than one worker"
for _bad in [(-0.1, 8), (1.5, 8), (0.5, 0)]:
    try:
        _kernel.amdahl_speedup(*_bad)
        assert False, f"amdahl_speedup{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "Amdahl, inverted", "code": r'''
import kernel as _kernel
_s = _kernel.serial_fraction_from_speedup(6.4, 16)
assert abs(_s - 0.1) < 1e-12, f"serial_fraction_from_speedup(6.4, 16) gave {_s!r}, expected 0.1"
for _sf, _wk in [(0.05, 8), (0.2, 32), (0.5, 4)]:
    _round = _kernel.serial_fraction_from_speedup(_kernel.amdahl_speedup(_sf, _wk), _wk)
    assert abs(_round - _sf) < 1e-9, f"round trip at s={_sf}, w={_wk} gave {_round!r}"
for _bad in [(4.0, 1), (4.0, 0), (0.0, 8), (-2.0, 8)]:
    try:
        _kernel.serial_fraction_from_speedup(*_bad)
        assert False, f"serial_fraction_from_speedup{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "max_speedup is the ceiling", "code": r'''
import kernel as _kernel
assert _kernel.max_speedup(0.05) == 20.0, f"max_speedup(0.05) gave {_kernel.max_speedup(0.05)!r}"
assert _kernel.max_speedup(1.0) == 1.0, "an entirely serial program has a ceiling of 1"
assert _kernel.max_speedup(0.0) == float("inf"), "no serial fraction means no ceiling"
try:
    _kernel.max_speedup(2.0)
    assert False, "max_speedup(2.0) should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "The study reports its findings", "code": r'''
assert "all stages bit-identical: True" in _out, \
    "main.py should confirm every stage matches stencil_v0 exactly"
for _word in ("stage", "seconds", "speedup"):
    assert _word in _out, f"the printed table should have a {_word!r} column"
assert "implied serial fraction" in _out, "main.py should report the serial fraction it inferred"
assert "ceiling" in _out, "main.py should state the ceiling that fraction implies"
_src = open("kernel.py").read()
assert "print(" not in _src, "kernel.py holds the logic; the printing belongs in main.py"
'''},
        ],
    },
}
