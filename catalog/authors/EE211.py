"""EE211 — Signals and Systems.

A second-year course. It assumes the first year of the programme and nothing more:
DC and AC circuit analysis, phasors and impedance, complex numbers and calculus,
Boolean algebra, elementary Python, and fields. Everything above that line is built
here.

Authoring rules, same as the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * every expected number in a test or a notice was produced by running the code,
    the circuit solver or the visualiser, never assumed
  * build checks are JavaScript against the circuit API, and they measure what the
    circuit does rather than compare it with the reference drawing
"""

COURSE = {
    "id": "EE211",
    "title": "Signals and Systems",
    "band": 2,
    "level": "Intermediate",
    "prereqs": ["EE102", "EE111"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◊",
    "summary": (
        "First year taught you to analyse a circuit at one frequency at a time. This "
        "course replaces that with a single description that covers every frequency at "
        "once. Two assumptions — linearity and time invariance — are enough to prove "
        "that a system's response to one impulse determines its response to everything, "
        "and that the awkward integral joining the two becomes an ordinary multiplication "
        "once both signals are written as spectra. Along the way the course settles what "
        "a spectrum actually is for a periodic signal and for an aperiodic one, and what "
        "sampling does to it, which is the point at which a signal stops being electrical "
        "and starts being a list of numbers."
    ),
    "outcomes": [
        "Decide whether a given system is linear, whether it is time invariant, and say which test it fails.",
        "Convolve two signals by hand and in code, and explain why the impulse response is a complete description of an LTI system.",
        "Compute the Fourier coefficients of a periodic signal, read its line spectrum, and relate the rate at which the harmonics decay to the smoothness of the waveform.",
        "Predict the frequency a sampled component will appear at, choose a sample rate that avoids aliasing, and specify the analogue filter that has to come first.",
        "Write the transfer function of a circuit from its impedances, read its Bode plot, and use $Y = HX$ instead of solving a differential equation.",
        "Apply the shift, scaling, modulation and differentiation properties of the transform, and say what each one does to a magnitude spectrum and to a phase spectrum.",
        "Design a band-pass to a centre frequency and a $Q$, and measure both back off the response without knowing any component value.",
        "Read a difference equation, find its impulse response, and decide from its coefficients alone whether it is stable.",
        "Say what a finite record does to a spectrum — where the bins are, why a tone leaks, and what a window trades for what — and specify the filter that has to follow a converter on the way back out.",
    ],
    "assessment": (
        "Ten quizzes; four circuits designed and measured in the schematic editor; three "
        "guided derivations; four Python labs checked by execution; a symbol drill, two "
        "numeric problems, two fill-the-equation exercises and one slider design run "
        "against the real model; and a capstone that builds a working spectrum analyser "
        "and uses it to demonstrate the convolution theorem on a signal it has sampled "
        "itself."
    ),
    "reading": [
        "*Signals and Systems*, Oppenheim, Willsky & Nawab — chapters 1 to 4, which is this course in its canonical order.",
        "*The Scientist and Engineer's Guide to Digital Signal Processing*, Smith — free online, and unusually good on what a spectrum looks like in practice.",
        "*The Art of Electronics*, Horowitz & Hill — appendix on Fourier and the section on filters, for the engineering rather than the mathematics.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Linearity, time invariance and the impulse response",
            "summary": "Two assumptions, and everything a system will ever do collapses into one list of numbers.",
            "concepts": [
                "A **system** is a rule that turns one signal into another: $y = S\\left\\{x\\right\\}$. An amplifier, a filter, a length of cable and a control loop are all systems in this sense.",
                "A system is **linear** when scaling the input scales the output by the same factor, and when the response to a sum of inputs is the sum of the responses: $S\\left\\{a x_1 + b x_2\\right\\} = a\\,S\\left\\{x_1\\right\\} + b\\,S\\left\\{x_2\\right\\}$.",
                "A straight-line graph is not the test. $y = 2x + 3$ plots as a straight line and is **not** linear, because doubling $x$ does not double $y$. Squaring, rectifying and clipping fail as well.",
                "A system is **time invariant** when delaying the input only delays the output: if $x(t) \\to y(t)$ then $x(t - t_0) \\to y(t - t_0)$, with the same shape. A circuit whose component values are being changed as it runs is not.",
                "**LTI** means both. Every resistor, capacitor and inductor network from EE102 is LTI, provided nothing saturates and no switch moves.",
                "The **unit impulse** $\\delta[n]$ is 1 at $n = 0$ and zero everywhere else; in continuous time $\\delta(t)$ is the limit of a pulse of unit area as it becomes infinitely narrow. The output it produces is the **impulse response** $h$.",
                "Any signal is a sum of shifted, scaled impulses: $x[n] = \\sum_k x[k]\\,\\delta[n-k]$. Time invariance says each of those impulses produces $h$, shifted; linearity says the outputs add. So $y[n] = \\sum_k x[k]\\,h[n-k]$ — the **convolution** $y = x * h$.",
                "That is the central result of the module: for an LTI system, $h$ is a complete description. Measure it once and you can predict the response to anything.",
                "Convolution is commutative and associative, so two systems in cascade have impulse response $h_1 * h_2$ and the order they are wired in does not matter — provided the second stage does not load the first, because a stage's impulse response belongs to the stage *and its load*.",
                "Two finite responses of $N$ and $M$ samples convolve to $N + M - 1$ samples.",
                "A system is **causal** when $h[n] = 0$ for $n < 0$: no output before the input arrives. It is **BIBO stable** when $\\sum_n |h[n]|$ is finite, and that sum is exactly the largest output an input bounded by 1 can produce — which is not the same as $\\sum_n h[n]$, the gain it applies to a constant.",
            ],
            "read": [
                {
                    "title": "Two questions to ask a system",
                    "minutes": 10,
                    "body": r'''
Put a signal generator on the bench, connect its output to a box, and connect the box's
output to an oscilloscope. Whatever is inside the box — an amplifier, a filter, a length
of cable, a loudspeaker and a microphone facing each other across a room — the same
description fits: one signal goes in, another comes out. That is all the word **system**
means here, and the box does not have to be electrical. A car's suspension is a system
with the road profile as its input and the seat's motion as its output. A savings account
is a system whose input is your deposits.

The trouble is that the description is too wide to be useful. There are infinitely many
signals you could put in, and knowing what the box did to a hundred of them tells you
nothing about the hundred and first. To get anywhere you have to narrow the class of
boxes, and the whole of this course rests on narrowing it with exactly two questions.

## The first question: does superposition hold?

Feed in $x_1$ and record the output $y_1$. Feed in $x_2$ and record $y_2$. Now feed in
$x_1 + x_2$. If what comes out is $y_1 + y_2$ — every time, for every pair of inputs —
and if scaling an input scales its output by the same factor, the system is **linear**.
Both halves are needed, and they are usually written as one statement:

$$S\left\{a x_1 + b x_2\right\} = a\,S\left\{x_1\right\} + b\,S\left\{x_2\right\}$$

Read it as a promise about experiments, not as algebra. It says you may take any input
apart into pieces, push the pieces through separately, and add the results — and the
answer will be the same as if you had pushed the whole thing through at once. Everything
in the first year quietly depended on that promise. Superposition in a resistive network,
phasor analysis one frequency at a time, Thévenin equivalents: none of them is legal
without it.

## The mistake almost everybody makes once

"Linear" sounds like "plots as a straight line", and those are not the same thing. This is
worth dwelling on, because the confusion is nearly universal and it is imported directly
from school mathematics, where $y = mx + c$ is *called* a linear function.

Take a real instrumentation amplifier with a gain of 3 and a 1 V offset:

$$y = 3x + 1$$

Its graph is as straight as a graph gets. Test it anyway.

```
input      output
-----      ------
2 V        3*2 + 1  =  7 V
5 V        3*5 + 1  = 16 V

now put in the sum of those two inputs:

7 V        3*7 + 1  = 22 V

but the sum of the two outputs is

           7 + 16   = 23 V
```

Twenty-two against twenty-three. The system is not linear, and the missing volt is the
offset: it should have appeared twice, once for each input, and it appeared once. The
scaling test fails just as plainly — put in zero and you get 1 V out, which no linear
system can do, because $S\left\{0 \cdot x\right\} = 0 \cdot S\left\{x\right\} = 0$.

The technical name for $3x + 1$ is **affine**, and the practical response is not despair
but subtraction. Measure the offset, take it off, and what remains is genuinely linear
and every tool in this course applies to it. That is what the "null" or "tare" button on
an instrument is doing, and it is why an offset is an annoyance rather than a disaster.

Three other everyday circuits fail the test outright, and they are worth recognising on
sight. **Squaring**, $y = x^2$, because doubling the input quadruples the output — the
square-law detector, the mixer core, the RMS-to-DC converter. **Rectifying**, $y = |x|$,
because $|x_1 + x_2| \ne |x_1| + |x_2|$ whenever the two have opposite signs. And
**clipping**, which is what every amplifier does eventually: linear up to the rails, and
flat thereafter.

## The second question: does the answer depend on when you ask?

Now a different experiment. Feed in $x(t)$, record $y(t)$. Wait ten seconds and feed in
exactly the same signal again. If the output is the same waveform, ten seconds later —
same shape, same size, only shifted — the system is **time invariant**:

$$x(t - t_0) \to y(t - t_0)\quad\text{for every } t_0$$

The physical content is that the box has no calendar. Nothing inside it is being changed
while it runs, and nothing about it depends on the absolute time on the wall clock.

Here is a system that is perfectly linear and fails this test. Let the gain rise steadily
with time: $y[n] = n\,x[n]$, an amplifier whose volume control is being turned up at a
constant rate. Linearity is untouched — at each instant the output is a fixed multiple of
the input, so sums and scalings pass straight through. But send in a single click at
$n = 2$:

```
x = 0, 0, 1, 0, 0, ...        a click at n = 2
y = 0, 0, 2, 0, 0, ...        because y[2] = 2 * 1

now send the same click one sample later, at n = 3:

x = 0, 0, 0, 1, 0, ...
y = 0, 0, 0, 3, 0, ...        because y[3] = 3 * 1

a delayed copy of the first output would have been

    0, 0, 0, 2, 0, ...        height 2, not 3
```

Delaying the input by one sample did not simply delay the output; it changed its height
from 2 to 3. Not time invariant. And this is not a contrived example — it is the mixer,
$y(t) = x(t)\cos(2\pi f_0 t)$, which is the same thing with a sinusoid instead of a ramp
and which is the single most useful non-time-invariant circuit ever built. Radio does not
work without it, and none of the machinery in the rest of this course applies to it.

The two tests are independent, which is the point of asking them separately. The offset
amplifier $3x + 1$ *is* time invariant and is not linear: delay the input and $3x + 1$
arrives delayed by the same amount, unchanged in shape. The ramping gain $n\,x[n]$ *is*
linear and is not time invariant. A rectifier fails both. A plain delay, $y(t) = x(t-3)$,
passes both and is about as simple as a system gets.

## What passing both is worth

A system that is linear and time invariant is called **LTI**, and the abbreviation is
worth the ink because of what the next reading proves: for such a system, one single
measurement — the response to one sharp tap — determines the response to every input
that will ever be applied. Nothing narrower than LTI supports that claim, and nothing
wider is needed for most of electronics.

The good news is how much hardware qualifies. Every network of resistors, capacitors and
inductors is LTI. So is a transmission line, an antenna, the acoustics of a concert hall,
the mechanical response of a bridge, and a well-behaved feedback loop. In each case the
governing equation is a linear differential equation with constant coefficients, and those
two adjectives are the two tests in another language: *linear* gives superposition,
*constant coefficients* gives time invariance.

## Where this stops holding

Every real box is LTI only over a range, and it is worth knowing which edge you are near.

- **Amplitude.** Push any amplifier hard enough and it clips. Beyond that point
  superposition is gone, and a measurement made below the limit stops predicting anything
  above it. This is why a data sheet quotes a maximum output swing, and why distortion is
  measured as the appearance of frequencies that were not in the input — something no
  linear system can do.
- **Rate.** An op-amp has a slew-rate limit: past a certain volts-per-microsecond the
  output is a straight ramp no matter what the input asks for. That is a limit on the
  *derivative* rather than on the size, so a signal can be well inside the voltage rails
  and still leave the linear region.
- **Devices that are curved by design.** Diodes and transistors are non-linear, which is
  what makes them useful. EE201 handles them by linearising about an operating point:
  small signals ride on a bias, and *for those small signals* the device is LTI again.
  The technique is exactly a decision about how near the edge you are willing to stand.
- **Things that change while they run.** Switched-mode converters, sample-and-holds,
  automatic gain control, anything with a relay in it. These are linear but not time
  invariant, and they need the tools of EE241 and CTRL520 rather than these.

Everything from here to the end of the course assumes both tests pass. Knowing when they
do not is not a footnote — it is the difference between a prediction and a guess.
''',
                },
                {
                    "title": "Why one measurement is enough",
                    "minutes": 13,
                    "body": r'''
Someone hands you a sealed box with an input and an output and asks you to say what it
will do to any signal they choose. Without any assumptions this is hopeless. You could
sweep a sine through it at every frequency, but that leaves every amplitude untested; you
could try every amplitude too, and still not have covered signals that are not sines. The
space of possible inputs has no finite list you could work through in a lifetime.

Assume the box is LTI and the job collapses to a single measurement. That is what this
reading is about, and the argument is short enough to hold in your head, which is why it
is worth following rather than memorising.

## The sharpest possible tap

In discrete time the tool is easy to define. The **unit impulse** $\delta[n]$ is 1 at
$n = 0$ and 0 at every other sample: a single spike of height 1 with silence either side.
Nothing subtle is going on: it is a list of numbers, $\dots, 0, 0, 1, 0, 0, \dots$

In continuous time it takes more care. You cannot have a signal that is non-zero at one
instant only and still carries any effect, so $\delta(t)$ is defined as a limit: take a
rectangular pulse of width $\varepsilon$ and height $1/\varepsilon$, so its **area is 1**
whatever $\varepsilon$ is, and let $\varepsilon \to 0$. The height runs away to infinity
and the area stays at one. The quantity that survives the limit is the area, which is why
$\delta(t)$ carries units of one-over-time.

Physically it is a hammer blow on a bell, a spark gap fired into an antenna, a starter
pistol in a concert hall, an electrostatic discharge onto a circuit board. In each case
the tap is short compared with anything the system does in response, which is the only
property that actually matters.

Whatever comes out is the **impulse response**, written $h[n]$ or $h(t)$. It is one
waveform. Record it.

## Every signal is a stack of impulses

Here is the identity that does the work. Any discrete signal can be written as

$$x[n] = \sum_{k} x[k]\,\delta[n-k]$$

This is not a theorem and nothing has been assumed to get it. It says: the signal
$x = \left\{3, 1, 4\right\}$ is three impulses — one of height 3 at $n = 0$, one of
height 1 at $n = 1$, one of height 4 at $n = 2$ — added together. Written out,

$$x[n] = 3\,\delta[n] + 1\,\delta[n-1] + 4\,\delta[n-2]$$

Check it sample by sample if it looks like sleight of hand. At $n = 1$ the first term is
zero because $\delta[1] = 0$, the second is $1 \times \delta[0] = 1$, and the third is
zero because $\delta[-1] = 0$. Total: 1, which is what $x[1]$ was. The sum is a machine
for picking out one sample at a time, and it is called the **sifting** property.

## Two assumptions, and the sum falls out

Now push that decomposition through the box and use the two properties in turn.

*Linearity* says the box's response to a sum is the sum of its responses, and that a
scaled input gives a scaled output. So

$$y[n] = S\left\{\sum_k x[k]\,\delta[n-k]\right\} = \sum_k x[k]\;S\left\{\delta[n-k]\right\}$$

The weights $x[k]$ are constants as far as the system is concerned, so they come outside.

*Time invariance* says the response to a delayed impulse is the delayed impulse response:
$S\left\{\delta[n-k]\right\} = h[n-k]$. This is the step that fails for the mixer and for
the ramping gain of the previous reading — for those, each shifted impulse gets a
different response and the argument stops here. Substituting,

$$y[n] = \sum_k x[k]\,h[n-k]$$

which is called the **convolution** of $x$ and $h$, written $y = x * h$. Two lines, two
assumptions, and the entire behaviour of the box is now a single list of numbers plus one
operation.

## Worked: two samples in, three samples out

An LTI system is tapped once and its response is measured as
$h = \left\{1, -1, 4\right\}$ at $n = 0, 1, 2$. What does it do to the input
$x = \left\{2, 3\right\}$?

Take the decomposition literally. The input is an impulse of height 2 at $n = 0$ plus one
of height 3 at $n = 1$. The first produces $2h$; the second produces $3h$, delayed by one
sample. Lay them out and add columns:

```
n            0     1     2     3

2 * h      2.0  -2.0   8.0
3 * h,
 delayed          3.0  -3.0  12.0
           ----------------------
y          2.0   1.0   5.0  12.0
```

Four samples, from a two-sample input and a three-sample response, and that is the
general rule: $N + M - 1$. The first output sample appears when the leading edge of $x$
meets the leading edge of $h$; the last when the trailing edge of one meets the trailing
edge of the other; count the positions in between and you get $2 + 3 - 1 = 4$.

There is a cheap arithmetic check worth doing every time. The sum of the output samples
must equal the sum of the input samples times the sum of $h$:

```
sum(x) = 2 + 3          =  5
sum(h) = 1 - 1 + 4      =  4
sum(y) = 2 + 1 + 5 + 12 = 20   =  5 * 4    correct
```

It works because $\sum h$ is the system's gain for a constant input, and a check that
takes five seconds catches most sign slips.

## Worked: a circuit whose answer you already know

Take an RC low-pass: $R = 10\,\text{k}\Omega$ in series, $C = 100\,\text{nF}$ to ground,
output across the capacitor. Its time constant is
$\tau = RC = 10^{4} \times 10^{-7} = 10^{-3}$ s, one millisecond.

Its impulse response is the voltage left on the capacitor by a tap that delivers unit
area, decaying away through the resistor:

$$h(t) = \frac{1}{\tau}e^{-t/\tau}\quad (t \ge 0)$$

That $1/\tau$ out front is not decoration. The area under $h$ is
$\int_0^\infty \frac{1}{\tau}e^{-t/\tau}\,dt = 1$, and the area under the impulse response
*is* the gain the system applies to a constant — which had better be 1 for a filter that
passes DC untouched. If you ever write down an impulse response and its area is not the
gain you expect, the scale factor is where the error is.

Now convolve it with a 5 V step switched on at $t = 0$. In continuous time the sum becomes
an integral, and because the input is constant it slides straight out:

```
y(t) = integral from s = 0 to s = t of  x(t - s) h(s) ds
     = 5 * integral from 0 to t of (1/tau) e^(-s/tau) ds
     = 5 * [ 1 - e^(-t/tau) ]

at t = 1 ms = 1 tau :   5 * (1 - 0.36788) = 5 * 0.63212 = 3.1606 V
at t = 3 ms = 3 tau :   5 * (1 - 0.04979) = 5 * 0.95021 = 4.7511 V
```

That is the RC charging curve from the first year, and it has just been produced by a
method that never mentioned capacitors. The convolution did not know it was a circuit.
Feed the same $h$ a speech waveform or a burst of noise and the same integral answers
that too, which is precisely what one differential equation solved by hand cannot do.

## The flip, and the mistake it causes

Look again at the index inside the sum: $h[n-k]$, not $h[k]$. As $k$ runs forward, the
argument of $h$ runs *backwards*. Drawn as a picture, one sequence is reversed and slid
past the other, and at each position you multiply the overlapping samples and add.

The tempting error is to drop the reversal and compute $\sum_k x[k]\,h[k]$ — multiply the
two sequences term by term and add. That is a real and useful operation, called
**correlation**, and it answers a different question: how much does $x$ resemble $h$?
Convolution answers: what does the system do to $x$? Radar uses the first, filtering uses
the second, and the two agree only when $h$ is symmetric.

The reversal is not a convention someone chose. It is bookkeeping: the output *now* is
built from the input's recent past, weighted by how long ago each piece arrived, and
$h[0]$ weights the sample that arrived this instant while $h[5]$ weights the one from five
samples ago. Write $y[3]$ out longhand and the reversal is obvious:

$$y[3] = x[0]h[3] + x[1]h[2] + x[2]h[1] + x[3]h[0]$$

The indices in each product add to 3. That is the pattern to check against when you are
unsure, and it is why the practical advice is to write the two sequences on strips of
paper and slide one past the other rather than to trust index arithmetic done in the head.

One consequence falls out of it immediately. Because the indices in each product add to
$n$, nothing in the arithmetic distinguishes $x$ from $h$, so

$$x * h = h * x$$

Convolution is commutative. Which of the two signals is "the system" and which is "the
input" is a matter of what you plugged into what, not a property of the sum.

## Where this stops

- **Nothing here survives non-linearity.** A clipping amplifier has no impulse response
  at all in this sense, because the response to a big tap is not a scaled copy of the
  response to a small one. Measure $h$ with a 1 V tap and it will not predict the
  behaviour under a 10 V input.
- **A time-varying system has an $h$ that depends on when you tapped it**, written
  $h(t, \tau)$ — two arguments, not one, and no convolution. All the compression the
  method buys comes from collapsing those two arguments into their difference.
- **A true impulse cannot be generated.** Real measurements use a step and differentiate
  the result, or a swept sine, or a maximum-length noise sequence — all of which recover
  the same $h$ with far more energy delivered and far better noise performance. The theory
  needs the impulse; the laboratory rarely uses one.
- **The sum has to converge.** For an infinitely long $h$, $y[n]$ is an infinite series,
  and whether it adds up to anything at all is the stability question the next reading
  takes up.
''',
                },
                {
                    "title": "Causality, stability, and the price of a cascade",
                    "minutes": 10,
                    "body": r'''
The impulse response is a complete description of an LTI system, so every question you
could ask about the system has to be answerable from $h$ alone. Two of those questions
decide whether the thing can be built at all, and a third decides whether you may treat
two boxes wired together as one.

## Causality: no output before the input

A system is **causal** when $h[n] = 0$ for all $n < 0$. In words: tap it at $n = 0$ and
nothing comes out beforehand. Every physical system running in real time is causal, and
the condition looks so obvious that it seems not to need stating.

It needs stating because the moment a signal is a file rather than a wire, causality stops
being compulsory. An audio editor filtering a recording already holds the whole waveform,
including the parts that have not been "heard" yet, so it can use a symmetric $h$ with
taps on both sides of zero. That is worth doing: a symmetric $h$ has exactly zero phase
distortion, which no causal filter can achieve. The cost is that the filter cannot run
live. This is the real trade — latency against phase — and it is why studio processing and
live processing use different filters for the same job.

The condition also has teeth in design. Ask for a brick-wall low-pass with a perfectly
flat passband and an infinitely steep edge, and you will find its impulse response is a
$\text{sinc}$ that extends forever in *both* directions. It is not causal, so it cannot be
built, and every practical filter is a compromise reached from that impossibility.

## Stability: bounded in, bounded out

A system is **BIBO stable** when every input that stays inside some finite bound produces
an output that stays inside some finite bound. The test on $h$ is one sum:

$$\sum_{n} |h[n]| < \infty$$

The argument is three steps. Start from the convolution, bound the size of a sum by the
sum of the sizes, then bound every input sample by $B$:

$$|y[n]| = \left|\sum_k h[k]\,x[n-k]\right| \le \sum_k |h[k]|\,|x[n-k]| \le B\sum_k |h[k]|$$

So if the sum is finite the output is bounded — and bounded by a specific number, not just
by "some number". That number deserves a name: $\sum |h|$ is the **worst-case gain** of
the system.

## Worked: the bound is reached, not merely respected

An inequality is only interesting if something attains it. This one does. Take the
three-tap system $h = \left\{1, -2, 3\right\}$, so $\sum|h| = 1 + 2 + 3 = 6$.

To make $y[2]$ as large as possible, choose each input sample to carry the same sign as
the coefficient of $h$ it is going to meet. Looking at
$y[2] = x[0]h[2] + x[1]h[1] + x[2]h[0]$, the signs wanted are $+$, $-$, $+$:

```
x = { 1, -1, 1 }        every sample inside the bound B = 1

y[2] = x[0]h[2] + x[1]h[1] + x[2]h[0]
     = (1)(3) + (-1)(-2) + (1)(1)
     =   3    +     2    +   1     =  6
```

Six, from an input that never exceeds one. So $\sum|h|$ is not a loose bound to be
improved on later; it is the exact peak gain, and anyone who knows $h$ can always extract
it.

Notice how different this is from the gain the same system applies to a constant,
$\sum h = 1 - 2 + 3 = 2$. A system can be gentle with the signals you expect and violent
with one that happens to match its coefficients. That gap is why digital filters are
designed with headroom, and why an overflow shows up in a filter that had been running
happily for months.

## Worked: every sample finite, the sum infinite

Now the trap. Take the accumulator, $y[n] = y[n-1] + x[n]$, whose impulse response is

$$h[n] = 1 \quad \text{for every } n \ge 0$$

Every sample of $h$ is 1. Nothing anywhere is infinite, nothing grows, and the response to
a single tap is as tame as a response can be. But

$$\sum_n |h[n]| = 1 + 1 + 1 + \dots = \infty$$

and the system is not BIBO stable. The demonstration takes one line: feed in a constant
1 V, an input as bounded as they come, and the output is $1, 2, 3, 4, \dots$, which passes
any bound you care to name.

This is the whole content of the stability test and the place people go wrong. Stability is
a statement about the *sum*, never about individual samples. An infinite sum of finite
terms is exactly what instability looks like from the inside, and inspecting $h$ sample by
sample will never reveal it. Compare with $h[n] = (0.9)^n$: those samples decay so slowly
that the first fifty look much like the accumulator's, yet $\sum |h| = 1/(1 - 0.9) = 10$,
which is finite, so the system is stable and the worst any input bounded by 1 can do is 10.

A real integrator built from an op-amp does not in fact run off to infinity — it stops at
the supply rail. But it stops by clipping, which is to say by ceasing to be linear, and at
that point none of the theory in this module applies to it any more. "Saved by saturation"
is not stability.

## Cascades: the order does not matter

Wire the output of one LTI system into the input of another. Convolution is associative,
so the pair is a single LTI system with impulse response $h_1 * h_2$; and it is
commutative, so $h_1 * h_2 = h_2 * h_1$ and the order the two boxes are wired in makes no
difference to the result.

That last claim is startling enough to be worth checking on a case. Let
$h_1 = \left\{1, -1\right\}$, a difference — it subtracts the previous sample from the
current one. Let $h_2 = \left\{1, 1, 1\right\}$, a running sum over three samples.

```
h1 * h2, laid out as before:

n            0     1     2     3

 1 * h2      1     1     1
-1 * h2,
  delayed         -1    -1    -1
           ----------------------
             1     0     0    -1
```

The cascade is $\left\{1, 0, 0, -1\right\}$, which is the system $y[n] = x[n] - x[n-3]$.
Do it the other way round — the running sum first, the difference after — and the same
four numbers come out, because the columns being added are the same products taken in a
different order.

## And then it does matter

The algebra is exact, and it describes the systems *as they are wired*, which is not the
same thing as the systems as you measured them separately. Connecting the second box
changes the first one if the second draws anything from it.

Take a divider of two 10 kΩ resistors, measured on its own: it halves, so
$h_1 = 0.5\,\delta$. Take a second divider, this one two 100 kΩ resistors, also halving,
so $h_2 = 0.5\,\delta$. The cascade rule predicts a quarter — 2.5 V from a 10 V supply.
What the circuit actually does:

```
the second stage seen as a load     100k + 100k               = 200 k
in parallel with the lower 10k      (10 * 200)/(10 + 200)     = 9.524 k
so the first stage now gives        10 * 9.524/(10 + 9.524)   = 4.878 V
and the second stage halves that    4.878 * 0.5               = 2.439 V
```

2.439 V rather than 2.5 V — two and a half per cent low, because the second stage's 200 kΩ
is twenty times the first stage's 10 kΩ and so barely disturbs it. Bring the two
impedances closer together and the discrepancy grows fast; one of the numeric exercises
below asks you to put a figure on the case where they are equal.

Nothing here contradicts the cascade rule. $h_1 * h_2$ is still exactly the impulse
response of the pair — but $h_1$ has to be the impulse response of the first stage *with
the second one attached*, and that is not what you measured with its output hanging open.
The engineering fix is the one every analogue designer reaches for: put a buffer between
the stages, so the second draws no current and the two measurements you made separately
are the two that actually apply. Then, and only then, is the design a matter of
multiplying gains.

## Where all of this stops

- **BIBO stability is about the input–output relation only.** A system can be BIBO stable
  and still have something inside it growing without bound, as long as that something
  never reaches the output. CTRL510 separates the two ideas and needs both.
- **The borderline cases are genuinely borderline.** The accumulator fails the test, yet
  fed a signal with zero average it behaves perfectly well for as long as you care to
  watch. "Unstable" means *some* bounded input breaks it, not every one.
- **Everything above assumes LTI.** For a non-linear system, whether the output stays
  bounded can depend on the size of the input as well as on the system, and there is no
  single $h$ to test. That is why a limiter can make a loop that would otherwise diverge
  settle into a steady oscillation instead — a useful behaviour this theory cannot see at
  all.
''',
                },
            ],
            "sandbox": {
                "title": "One system, and the shape of what comes out of it",
                "visualiser": "pole-step",
                "minutes": 8,
                "initial": {"zeta": 0.35, "wn": 4},
                "brief": r'''
An LTI system's whole behaviour is one waveform, and this is a family of them to push on
before any algebra is done to them.

The **right-hand** plot is the response to a step switched on at $t = 0$ — which, because
a step is a running total of impulses, is the running total of the impulse response. The
dashed line is the value it is heading for. The **left-hand** plot shows where the
system's two poles sit; poles are the subject of module 4, and for now they are only a
picture of the same information.

Two sliders: the damping $\zeta$, which decides the *shape*, and the natural frequency
$\omega_n$, which decides the *pace*. The caption underneath reports the overshoot and
the settling time it measures.
''',
                "notice": [
                    "It opens at $\\zeta = 0.35$, $\\omega_n = 4$ rad/s. The caption reports 30.9% overshoot and settling in about 2.86 s, and it says the two poles sit at 70° from the negative real axis. The response goes past its final value, comes back, and converges — three numbers describing one curve, all of them readable off the impulse response if you had it instead.",
                    "Drag $\\zeta$ down to 0. The poles land exactly on the vertical axis, the curve oscillates between 0 and 2 forever, and the caption's settling time reads *Infinity*, which is the honest answer. This is the boundary case of the stability test: the response never grows, but it never dies away either, so the sum of $|h|$ does not converge and the system is not BIBO stable.",
                    "Now take $\\zeta$ up to 1.00. The caption changes to \"critically damped\" and the overshoot is gone entirely — the fastest approach that never crosses the line. Push on to 1.60 and the two poles separate along the real axis, at $-1.40$ and $-11.40$ rad/s. The response is now the sum of two decaying exponentials, and the slower one, with its time constant of 0.71 s, is what you actually wait for.",
                    "Put $\\zeta$ back to 0.35 and raise $\\omega_n$ from 4 to 8. The curve on screen does not change shape at all: the overshoot is still 30.9%, but the settling time has halved from 2.86 s to 1.43 s and the numbers along the time axis have halved with it. $\\zeta$ is the shape and $\\omega_n$ is the clock, and they are independent — which is the same separation module 4 will make between the corner frequency of a filter and its damping.",
                    "Whatever you do to either slider, the curve ends on the dashed line at 1. That final value is the area under the impulse response, and it is the gain the system applies to a constant. The journey there is everything else in $h$.",
                ],
            },
            "quiz": {
                "title": "Which systems are LTI, and what follows",
                "minutes": 10,
                "questions": [
                    {
                        "q": "Which of these systems is linear but **not** time invariant?",
                        "opts": [
                            "$y(t) = x(t)\\cos(2\\pi f_0 t)$ — the input multiplied by a fixed sinusoid",
                            "$y(t) = x(t)^2$ — the input through a square-law detector",
                            "$y(t) = x(t - 3)$ — the input delayed by three seconds",
                            "$y(t) = |x(t)|$ — the input through a full-wave rectifier",
                        ],
                        "a": 0,
                        "why": r'''
Multiplying by a sinusoid is linear — scale the input and the output scales, add two
inputs and the outputs add — but it is not time invariant, because the sinusoid is
fixed to the clock rather than to the signal. Delay the input by a quarter of the
sinusoid's period and the output is not simply delayed; it is a different waveform.
That is the mixer, the one useful non-time-invariant circuit in the whole of radio.
Squaring and taking a modulus both fail linearity; a pure delay is LTI.
''',
                    },
                    {
                        "q": "An amplifier is measured as $y = 2x + 3$: a gain of two with a 3 V offset. Is it linear?",
                        "opts": [
                            "yes — its input–output graph is a straight line",
                            "yes, provided the offset is small compared with the signal",
                            "no — the response to zero input is not zero, so scaling fails",
                            "no — the offset means it fails time invariance as well as linearity",
                        ],
                        "a": 2,
                        "why": r'''
No. Put in $x = 0$ and you get 3 V out; put in twice any input and you do not get twice
the output. "Linear" in this course is the algebraic property, not the shape of the
graph, and the two part company exactly here — the technical name for $2x + 3$ is
*affine*. Answering "it fails time invariance as well" is wrong for a different reason worth
being clear about: this amplifier *is* time invariant, because delaying the input delays $2x + 3$ by the same amount. The
two tests are independent and a system can fail either one alone. The practical fix is
the one every instrumentation engineer uses: subtract the offset first, and what is left
is genuinely linear and can be treated with everything in this course.
''',
                    },
                    {
                        "q": "An LTI system has impulse response $h = \\left\\{1, 1, 1\\right\\}$ for $n = 0, 1, 2$. The input is $x = \\left\\{1, 2\\right\\}$. What is the output?",
                        "opts": [
                            "$\\left\\{1, 2, 1\\right\\}$",
                            "$\\left\\{1, 2, 3, 2\\right\\}$",
                            "$\\left\\{2, 3, 3, 1\\right\\}$",
                            "$\\left\\{1, 3, 3, 2\\right\\}$",
                        ],
                        "a": 3,
                        "why": r'''
Convolve: the input is one impulse of height 1 at $n = 0$ and one of height 2 at
$n = 1$, so the output is $h$ plus $2h$ delayed by one sample —
$\left\{1,1,1\right\} + \left\{0,2,2,2\right\} = \left\{1,3,3,2\right\}$. Four samples,
as $2 + 3 - 1 = 4$ requires.
The answer $\left\{2,3,3,1\right\}$ is the same numbers convolved the wrong way round in
the index, which is worth guarding against: line the two sequences up and slide one past
the other rather than trusting the arithmetic in your head.
''',
                    },
                    {
                        "q": "A 5-sample signal is fed through an LTI system whose impulse response is 8 samples long. How many samples does the output have?",
                        "opts": ["5", "8", "12", "40"],
                        "a": 2,
                        "why": r'''
$5 + 8 - 1 = 12$. The first output sample appears when the first input sample meets the
first sample of $h$, and the last when the last input sample meets the last of $h$;
count the positions and you get $N + M - 1$. The answer 40 multiplies the lengths, which
counts the multiplications the convolution performs rather than the samples it produces
— a useful number, but a different one.
''',
                    },
                    {
                        "q": "Why does knowing $h$ alone let you predict an LTI system's response to *any* input?",
                        "opts": [
                            "because $h$ contains the system's gain and its bandwidth, and nothing else matters",
                            "because every input can be written as a sum of shifted impulses, and LTI forces the output to be the same sum of shifted copies of $h$",
                            "because $h$ is measured with the largest possible input, so smaller ones are covered",
                            "it does not — a second measurement with a step input is always needed",
                        ],
                        "a": 1,
                        "why": r'''
The decomposition is the whole argument. Write $x[n] = \sum_k x[k]\delta[n-k]$: that is
an identity, true of any signal. Time invariance says the impulse at $k$ produces
$h[n-k]$; linearity says the pieces add with the same weights $x[k]$. Convolution is
what is left. Note what is *not* assumed — nothing about the size of the input, which
is why saturation is fatal: an amplifier that clips is no longer linear and its measured
$h$ stops predicting anything.
''',
                    },
                    {
                        "q": "Two systems have impulse responses $h_1[n] = (0.5)^n$ and $h_2[n] = (1.1)^n$ for $n \\ge 0$. Which is BIBO stable?",
                        "opts": [
                            "both, because both responses are finite at every sample",
                            "neither, because both go on forever",
                            "$h_1$ only",
                            "$h_2$ only, because it is the one that grows",
                        ],
                        "a": 2,
                        "why": r'''
Stability is about the **sum** $\sum|h[n]|$, not about any individual sample.
$\sum (0.5)^n = 2$, finite, so $h_1$ is stable — and that 2 is a real number you can
use: no input bounded by 1 V can ever produce more than 2 V out. $\sum (1.1)^n$
diverges, so a bounded input can drive $h_2$'s output arbitrarily large. Every sample of
$h_2$ is finite, which is exactly the trap in "both, because both responses are finite at every
sample": an infinite sum of finite terms
is what instability looks like.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "Two tests, six systems",
                    "minutes": 9,
                    "caption": "one system per line, and the two questions asked of each",
                    "lang": "text",
                    "brief": r'''
The two tests are independent, so a system has to be put through both. Four of these six
fail exactly one of them, which is the point of the drill: reading "not LTI" off a system
is no use unless you can say *which* property went.

Work along a row rather than down a column, and for each verdict do the experiment in your
head — scale and add for linearity, delay the input and compare for time invariance.
''',
                    "listing": """  system                        linear?   time invariant?
 --------------------------------------------------------
  y(t) = 3 x(t)                 yes       ___

  y(t) = 3 x(t) + 1             ___       yes

  y(t) = t x(t)                 yes       ___

  y(t) = x(2t)                  ___       no

  y[n] = x[n] * x[n-1]          ___       yes

  y[n] = x[-n]                  yes       ___
""",
                    "blanks": [
                        {
                            "prompt": "A plain gain of three: delay the input, and is the output the same waveform delayed?",
                            "hole": "?",
                            "opts": ["yes", "no"],
                            "a": 0,
                            "why": "Nothing inside a fixed gain refers to the clock, so a delayed input gives $3x(t - t_0)$, which is exactly the old output delayed. This is the simplest LTI system there is: its impulse response is $3\\delta(t)$.",
                        },
                        {
                            "prompt": "Gain of three with a 1 V offset added. Does superposition survive?",
                            "hole": "?",
                            "opts": ["yes", "no"],
                            "a": 1,
                            "why": "It does not. Put in zero and 1 V comes out, and no linear system can produce an output from no input. Add two inputs and the offset appears once instead of twice: $3(x_1 + x_2) + 1$ is one volt short of $(3x_1 + 1) + (3x_2 + 1)$. The graph is a straight line and the system is *affine*, not linear.",
                        },
                        {
                            "prompt": "A gain that rises steadily with time. Delay the input by one second — does the output just shift?",
                            "hole": "?",
                            "opts": ["yes", "no"],
                            "a": 1,
                            "why": "No. A click at $t = 2$ comes out with height 2; the same click at $t = 3$ comes out with height 3, where a shifted copy of the first output would still have height 2. The gain is tied to the clock rather than to the signal, which is exactly what a mixer does with a cosine in place of the ramp.",
                        },
                        {
                            "prompt": "Time compression, $x(2t)$: the signal played at double speed. Does scaling and adding still work?",
                            "hole": "?",
                            "opts": ["yes", "no"],
                            "a": 0,
                            "why": "Yes. Compressing the time axis does not touch amplitudes, so doubling the input doubles the output and the response to a sum is the sum of the responses. It is time invariance that this one fails: delaying the input gives $x(2t - t_0)$ while a delayed output would be $x(2t - 2t_0)$, and those are different signals.",
                        },
                        {
                            "prompt": "The current sample multiplied by the previous one. Linear?",
                            "hole": "?",
                            "opts": ["yes", "no"],
                            "a": 1,
                            "why": "No — this is squaring in disguise. Double the input and the output goes up by four, because both factors doubled. Multiplying a signal by a *constant* is linear; multiplying it by another signal, including a delayed copy of itself, is not.",
                        },
                        {
                            "prompt": "Time reversal, $y[n] = x[-n]$. Delay the input by one sample and compare.",
                            "hole": "?",
                            "opts": ["yes", "no"],
                            "a": 1,
                            "why": "No. Delaying the input gives $x[-n-1]$, but the delayed output is $x[-(n-1)] = x[1-n]$ — a delay at the input becomes an *advance* at the output, because the axis has been flipped. Reversal is perfectly linear, and it is the standard example of a linear system that is neither time invariant nor causal.",
                        },
                    ],
                },
                {
                    "title": "One convolution, line by line",
                    "minutes": 8,
                    "caption": "a three-sample system meeting a two-sample input",
                    "lang": "text",
                    "brief": r'''
The arithmetic, done in full and with two pieces missing. The system was measured once
with an impulse; everything else on the sheet follows from that one measurement and the
convolution sum.

The last line is the check worth doing every time: the samples of the output must add up
to the samples of the input added up, times the samples of $h$ added up. If that fails,
a sign or an index has gone astray somewhere above it.
''',
                    "listing": """  h = { 1.00, -0.50, 0.25 }        the system, measured once with an impulse
  x = { 4.00,  2.00 }              the input

  y runs from n = 0 to n = ___

  y[0] = x[0]h[0]                                  = ___
  y[1] = x[0]h[1] + x[1]h[0]                       = ___
  y[2] = x[0]h[2] + x[1]___                        = ___
  y[3] = x[1]h[2]                                  = ___

  check   sum(y) = sum(x) * sum(h) = 6.00 * ___    = 4.50
""",
                    "blanks": [
                        {
                            "prompt": "Two samples in, three in the impulse response. Where does the output end?",
                            "hole": "?",
                            "opts": ["2", "3", "4", "5"],
                            "a": 1,
                            "why": "The output is $2 + 3 - 1 = 4$ samples long, and a run of four samples starting at $n = 0$ ends at $n = 3$. The off-by-one is worth being careful about: the *length* is 4 and the *last index* is 3.",
                        },
                        {
                            "prompt": "The first output sample: 4.00 times 1.00.",
                            "hole": "?",
                            "opts": ["1.00", "4.00", "0.25", "6.00"],
                            "a": 1,
                            "why": "$y[0] = 4.00 \\times 1.00 = 4.00$. Only one product can contribute, because there is no earlier input sample and no earlier sample of $h$ — which is why the first output sample is always $x[0]h[0]$ and is the easiest place to catch a scaling error.",
                        },
                        {
                            "prompt": "$4.00 \\times (-0.50) + 2.00 \\times 1.00$.",
                            "hole": "?",
                            "opts": ["2.00", "0.00", "-2.00", "4.00"],
                            "a": 1,
                            "why": "$-2.00 + 2.00 = 0.00$. The two contributions cancel exactly, which is a real feature of this system rather than an accident of the arithmetic: it is what makes the output settle back towards zero after the input stops.",
                        },
                        {
                            "prompt": "Which sample of $h$ does $x[1]$ meet in the line for $y[2]$?",
                            "hole": "?",
                            "opts": ["h[0]", "h[1]", "h[2]", "x[0]"],
                            "a": 1,
                            "why": "The indices in every product have to add up to the output index. For $y[2]$, $x[1]$ must meet $h[1]$, because $1 + 1 = 2$. That rule is the whole content of the reversal in $h[n-k]$, and checking it is faster than re-deriving the sum.",
                        },
                        {
                            "prompt": "$4.00 \\times 0.25 + 2.00 \\times (-0.50)$.",
                            "hole": "?",
                            "opts": ["1.00", "0.00", "-1.00", "0.50"],
                            "a": 1,
                            "why": "$1.00 - 1.00 = 0.00$. Two zeros in a row in the middle of an output is unusual enough to be worth a second look, and here it is genuine — the check on the last line confirms it.",
                        },
                        {
                            "prompt": "The tail: $2.00 \\times 0.25$.",
                            "hole": "?",
                            "opts": ["0.25", "0.50", "2.00", "0.00"],
                            "a": 1,
                            "why": "$y[3] = 0.50$. The last output sample is always $x[N-1]h[M-1]$, the trailing edge of one meeting the trailing edge of the other, and like the first sample it is a single product with nothing else to add to it.",
                        },
                        {
                            "prompt": "The sum of the three samples of $h$.",
                            "hole": "?",
                            "opts": ["0.75", "1.75", "1.25", "0.25"],
                            "a": 0,
                            "why": "$1.00 - 0.50 + 0.25 = 0.75$, and $6.00 \\times 0.75 = 4.50$, which is $4.00 + 0.00 + 0.00 + 0.50$. That sum is the gain the system applies to a constant input, and using it as a check costs a few seconds and catches most sign slips.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "One sample of the output",
                    "minutes": 5,
                    "brief": r'''
The mechanical one, to get the index arithmetic under your fingers before anything is
built on top of it. One system, one input, one sample of the answer.

There is no need to work out the whole output. The convolution sum gives each sample
independently of every other, and that is worth exploiting.
''',
                    "prompt": "What is $y[2]$, the third sample of the output?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "figure": r'''
An LTI system is tapped once with an impulse and its response is recorded as
$h = \left\{2, 5, -1\right\}$ at $n = 0, 1, 2$, and zero at every other sample.

It is then driven with the two-sample input $x = \left\{3, 1\right\}$ volts, the 3 V
sample arriving at $n = 0$ and the 1 V sample at $n = 1$.
''',
                    "given": [
                        {"label": "Impulse response $h$", "value": "2, 5, −1  (at $n = 0, 1, 2$)"},
                        {"label": "Input $x$", "value": "3 V, 1 V  (at $n = 0, 1$)"},
                        {"label": "Wanted", "value": "$y[2]$"},
                    ],
                    "aside": "Every product in $y[n]$ has indices that add to $n$. For $y[2]$ that "
                             "leaves $x[0]h[2]$ and $x[1]h[1]$, and nothing else — there is no "
                             "$x[2]$ to pair with $h[0]$.",
                    "answer": 2.0,
                    "tol": 0.02,
                    "unit": "V",
                    "hint": "Write $y[2] = x[0]h[2] + x[1]h[1] + x[2]h[0]$ and cross out the term whose "
                            "input sample does not exist. Two products remain.",
                    "wrong": "If you got 14, you paired $x[0]$ with $h[1]$ and $x[1]$ with $h[2]$ — "
                             "the slide went one position too far. If you got 5, you used only the "
                             "$x[1]h[1]$ term and dropped the contribution the 3 V sample is still "
                             "making two samples later.",
                    "why": r'''
```
y[2] = x[0]h[2] + x[1]h[1]
     = 3 * (-1)  +  1 * 5
     =   -3      +    5      =  2.00 V
```

Two products, because $x$ has only two samples: the 3 V sample from two steps ago is now
meeting the tail of $h$, and the 1 V sample from one step ago is meeting its middle.

The full output, if you worked it all out, is
$y = \left\{6, 17, 2, -1\right\}$ — four samples, as $2 + 3 - 1 = 4$ requires. The check
holds too: $\sum x = 4$ and $\sum h = 6$, so $\sum y$ must be 24, and
$6 + 17 + 2 - 1 = 24$.
''',
                },
                {
                    "title": "The largest output this system can be made to give",
                    "minutes": 7,
                    "brief": r'''
A different kind of question about the same object. Not "what does this input do", but
"how bad can it get" — which is the question you ask when sizing a signal path so that
nothing further down it ever clips.

The answer is a single sum, and the trap is picking the wrong one.
''',
                    "prompt": "The input is guaranteed never to exceed 1 V in magnitude. What is the largest output magnitude the system can produce?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "figure": r'''
An LTI system's impulse response is measured and found to be a decaying alternation:

```
n         0      1      2      3      4      5     ...
h[n]   1.000 -0.750  0.563 -0.422  0.316 -0.237    ...
```

which is $h[n] = (-0.75)^n$ for $n \ge 0$, and zero for $n < 0$. It goes on forever,
halving in size roughly every two and a half samples but never quite reaching zero.
''',
                    "given": [
                        {"label": "Impulse response", "value": "$h[n] = (-0.75)^n$, $n \\ge 0$"},
                        {"label": "Input bound", "value": "$|x[n]| \\le 1$ V for every $n$"},
                        {"label": "Wanted", "value": "the peak output magnitude"},
                    ],
                    "aside": "Every sample of $h$ is smaller than the one before it, and the whole "
                             "response is bounded by 1. Neither of those facts is the answer — "
                             "the bound comes from a sum, not from a single sample.",
                    "answer": 4.0,
                    "tol": 0.03,
                    "unit": "V",
                    "hint": "The worst-case gain is $\\sum_n |h[n]|$. Taking the absolute value first "
                            "removes the alternating sign, and what is left is an ordinary geometric "
                            "series with ratio 0.75.",
                    "wrong": "If you got 0.57, you summed $h$ rather than $|h|$: that is "
                             "$1/(1 + 0.75)$, the gain this system applies to a *constant* input, and "
                             "it is the smallest thing the system does rather than the largest. If you "
                             "got 1.00, that is the biggest single sample of $h$, which would be the "
                             "answer only if the system had no memory at all.",
                    "why": r'''
The bound is $\sum_n |h[n]|$, and the absolute value turns the alternation into a plain
geometric series:

```
sum |h| = 1 + 0.75 + 0.75^2 + 0.75^3 + ...
        = 1 / (1 - 0.75)
        = 4.00 V
```

It is not a pessimistic bound that no real input reaches. Choose
$x[n-k] = \text{sign}(h[k])$ — that is, the alternating input $+1, -1, +1, -1, \dots$
volts, which is perfectly legal since every sample sits inside the 1 V limit — and every
product in the convolution sum comes out positive. The output then really is 4.00 V.

Set that against what the same system does to a steady 1 V:

```
sum h   = 1 - 0.75 + 0.75^2 - 0.75^3 + ...
        = 1 / (1 + 0.75)
        = 0.571 V
```

A factor of seven between the gentlest input and the harshest, from one impulse response.
This is why a filter that has behaved for months can overflow the first time it meets a
signal shaped like its own coefficients, and why $\sum|h|$ rather than $\sum h$ is the
number to size a signal path with.
''',
                },
                {
                    "title": "Two halvers, and what they actually do",
                    "minutes": 8,
                    "brief": r'''
A resistive divider has no memory: whatever goes in comes out scaled, instantly. Its
impulse response is therefore a single impulse, $h = K\delta$, and $K$ is the divider
ratio. Two of them in a row should be $h_1 * h_2 = K_1K_2\delta$ — cascade two systems
and the impulse responses convolve.

Each of the two dividers below halves. Predict the output, then work out what the circuit
actually does, and account for the difference.
''',
                    "prompt": "What voltage does the probe read?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 10000},
                            {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 10000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "p3", "kind": "R", "x": 12, "y": 4, "rot": 0, "value": 10000},
                            {"id": "p4", "kind": "R", "x": 15, "y": 6, "rot": 1, "value": 10000},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 9},
                            {"id": "o0", "kind": "OUT", "x": 17, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [9, 4], "b": [11, 4]},
                            {"a": [13, 4], "b": [15, 4]},
                            {"a": [15, 4], "b": [15, 5]},
                            {"a": [15, 7], "b": [15, 9]},
                            {"a": [15, 4], "b": [17, 4]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "10.0 V"},
                        {"label": "Every resistor", "value": "10.0 kΩ"},
                        {"label": "First stage on its own", "value": "halves — $K_1 = 0.5$"},
                        {"label": "Second stage on its own", "value": "halves — $K_2 = 0.5$"},
                    ],
                    "aside": "The second stage is not a voltmeter. It is 20 kΩ hanging on the "
                             "middle node, in parallel with the 10 kΩ that was already there.",
                    "answer": 2.0,
                    "tol": 0.03,
                    "unit": "V",
                    "check": r'''
return c.vout();
''',
                    "hint": "Work from the right. Replace the second divider by the resistance it "
                            "presents to the node it hangs on — the two resistors are in series as "
                            "far as that node is concerned — then solve the first divider with that "
                            "load in parallel with its lower resistor.",
                    "wrong": "If you got 2.50, you multiplied the two unloaded ratios: that is the "
                             "cascade rule applied to impulse responses that were measured with "
                             "nothing attached, and the second stage is very much attached. If you got "
                             "5.00, that is the middle node before the second divider halves it.",
                    "why": r'''
```
the second stage, seen from the middle node   10k + 10k               =  20.0 kohm
in parallel with the lower resistor           (10 * 20)/(10 + 20)     =   6.667 kohm
so the middle node sits at                    10 * 6.667/(10 + 6.667) =   4.00 V
and the second divider halves that            4.00 * 0.5              =   2.00 V
```

2.00 V, not the 2.50 V the two ratios multiplied together predict — a fifth of the signal
lost to a mistake in bookkeeping rather than in arithmetic.

Nothing here breaks the cascade rule. $h_1 * h_2$ is still exactly the impulse response of
the pair; the error is in which $h_1$ was used. Measured with its output open the first
divider halves, but with 20 kΩ hanging on it the same divider gives
$6.667/16.667 = 0.4$, and $0.4 \times 0.5 = 0.2$, which is the 2.00 V the solver reports.
The impulse response of a stage is a property of the stage *and its load*.

Two ways out, and both are used in practice. Make the second stage's impedance much larger
than the first's — ten times is usually enough to push the error under one per cent — or
put a buffer between them, which is the whole reason unity-gain buffers exist in a
catalogue of amplifiers that could just as easily have gain.
''',
                },
                {
                    "title": "A system you were never allowed to tap",
                    "minutes": 10,
                    "brief": r'''
The hardest of the four, and the most realistic. A true impulse is difficult to generate
and dangerous to apply, so an impulse response is often measured indirectly: drive the
system with a step, record where the output goes, and recover $h$ from what you get.

That recovery is the first half of this question. The second half is an ordinary
convolution, once you have something to convolve with.
''',
                    "prompt": "What is $y[3]$, the fourth sample of the output?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "figure": r'''
An LTI system is driven with a unit step — the input is 0 before $n = 0$ and exactly 1
from $n = 0$ onwards — and its output, the **step response** $s[n]$, is recorded:

```
n        0     1     2     3     4     5     6    ...
s[n]   0.40  1.00  1.30  1.20  1.20  1.20  1.20   ...
```

It settles at 1.20 and stays there.

The same system is then driven with a three-sample burst,
$x = \left\{2, -1, 4\right\}$ volts at $n = 0, 1, 2$, and zero afterwards.
''',
                    "given": [
                        {"label": "Step response $s$", "value": "0.40, 1.00, 1.30, 1.20, 1.20, …"},
                        {"label": "Input $x$", "value": "2 V, −1 V, 4 V at $n = 0, 1, 2$"},
                        {"label": "Wanted", "value": "$y[3]$"},
                    ],
                    "aside": "A step is the running total of impulses, so the step response is the "
                             "running total of the impulse response. Undo a running total by taking "
                             "differences.",
                    "answer": 1.9,
                    "tol": 0.03,
                    "unit": "V",
                    "hint": "First recover $h$: $h[0] = s[0]$ and $h[n] = s[n] - s[n-1]$ afterwards. "
                            "The step response stops changing after $n = 3$, so $h$ has exactly four "
                            "non-zero samples. Then $y[3] = x[0]h[3] + x[1]h[2] + x[2]h[1]$.",
                    "wrong": "If you got 5.10, you convolved with $s$ instead of $h$ — the step "
                             "response is not the impulse response. If you got 2.10, you have $h$ "
                             "right but dropped its last sample: $h[3]$ is negative and small, and it "
                             "is the one that is easy to miss.",
                    "why": r'''
The step response is the running total of the impulse response, so differencing recovers
$h$:

```
h[0] = s[0]                = 0.40
h[1] = s[1] - s[0] = 1.00 - 0.40 =  0.60
h[2] = s[2] - s[1] = 1.30 - 1.00 =  0.30
h[3] = s[3] - s[2] = 1.20 - 1.30 = -0.10
h[4] = s[4] - s[3] = 1.20 - 1.20 =  0.00      and zero from here on
```

Four non-zero samples, and their sum is $0.40 + 0.60 + 0.30 - 0.10 = 1.20$, which is where
the step response settled — as it had to be, since the sum of $h$ is the gain applied to a
constant.

Now convolve, taking only the products whose indices add to 3:

```
y[3] = x[0]h[3] + x[1]h[2] + x[2]h[1]
     = 2*(-0.10) + (-1)*(0.30) + 4*(0.60)
     =   -0.20   +    -0.30    +   2.40      =  1.90 V
```

There is no $x[3]$, so no $x[3]h[0]$ term. The whole output is
$y = \left\{0.80, 0.80, 1.60, 1.90, 1.30, -0.40\right\}$: six samples, as $3 + 4 - 1 = 6$
requires, and summing to $6.00 = 5 \times 1.20$.

Worth noticing is that little negative $h[3]$. It is what the step response's dip from
1.30 back to 1.20 means — a slight overshoot before settling — and it is the sort of
detail that a step measurement makes visible and a hand-waved "first-order-ish" model
throws away.
''',
                },
            ],
            "derive": {
                "title": "The impulse response of the simplest recursion, and its two gains",
                "minutes": 14,
                "vars": ["a", "b", "n", "N", "S", "G"],
                "brief": r'''
One line of code, $y[n] = a\,y[n-1] + x[n]$: keep a fraction $a$ of what you had and add
what has just arrived. It is a running average, a leaky integrator, an RC low-pass in
software, and the whole of module 8 in embryo.

It is also the shortest system with an *infinitely long* impulse response, which makes it
the right place to see the two gains of the previous reading part company. Everything
below is a geometric series and nothing else.
''',
                "steps": [
                    {
                        "prompt": "Drive it with an impulse: $x[0] = 1$ and $x[n] = 0$ afterwards, starting from $y[-1] = 0$. Write $h[n]$ for $n \\ge 0$ as a formula in $a$ and $n$.",
                        "given": "$h[0] = a \\cdot 0 + 1 = 1$, and after that the input is gone, so each sample is $a$ times the one before.",
                        "answer": "a^{n}",
                        "hint": "Start at 1 and multiply by $a$ once per sample: $1$, $a$, $a^2$, $a^3$, and so on.",
                        "deconstruct": [
                            "$h[0] = 1$ because the impulse arrives and there is nothing stored yet.",
                            "$h[1] = a \\cdot h[0] = a$, $h[2] = a \\cdot h[1] = a^2$: each step multiplies by $a$ again.",
                        ],
                    },
                    {
                        "prompt": "Write the sum of the first $N$ samples, $h[0] + h[1] + \\dots + h[N-1]$, in closed form in $a$ and $N$.",
                        "given": "The standard geometric sum. If $S = 1 + a + a^2 + \\dots + a^{N-1}$, then $aS$ is the same series shifted along by one term.",
                        "answer": "\\frac{1-a^{N}}{1-a}",
                        "hint": "Subtract $aS$ from $S$. Everything cancels except the first term of one and the last term of the other, leaving $S(1-a) = 1 - a^N$.",
                        "deconstruct": [
                            "$S = 1 + a + a^2 + \\dots + a^{N-1}$ and $aS = a + a^2 + \\dots + a^{N}$.",
                            "$S - aS = 1 - a^{N}$, so $S(1 - a) = 1 - a^{N}$; divide.",
                        ],
                    },
                    {
                        "prompt": "Now let the record run forever. For $|a| < 1$, write the limit of that sum as $N \\to \\infty$.",
                        "given": "$a^{N} \\to 0$ when $|a| < 1$, and does not when $|a| \\ge 1$.",
                        "answer": "\\frac{1}{1-a}",
                        "hint": "Only one term in the numerator survives the limit.",
                        "deconstruct": [
                            "$|a| < 1$ makes $a^{N}$ shrink towards zero as $N$ grows.",
                            "The numerator tends to $1 - 0 = 1$ and the denominator does not depend on $N$.",
                        ],
                    },
                    {
                        "prompt": "Take a negative coefficient, $a = -b$ with $0 < b < 1$, so the impulse response alternates in sign. The worst-case gain is the sum of the *magnitudes*, $|h[0]| + |h[1]| + \\dots$, and every magnitude is $b^n$. Write that sum in terms of $b$.",
                        "given": "$|(-b)^{n}| = b^{n}$, so the magnitudes are an ordinary geometric series with ratio $b$.",
                        "answer": "\\frac{1}{1-b}",
                        "hint": "It is the previous result with the sign of the ratio removed — the same series, now with every term positive.",
                        "deconstruct": [
                            "Taking magnitudes turns $1, -b, b^{2}, -b^{3}, \\dots$ into $1, b, b^{2}, b^{3}, \\dots$",
                            "That is the sum of the previous step with $b$ in place of $a$.",
                        ],
                    },
                    {
                        "prompt": "And the gain the same system applies to a constant input is the sum of $h$ itself, signs and all. Write it in terms of $b$.",
                        "given": "Substitute $a = -b$ into the limit you found two steps ago.",
                        "answer": "\\frac{1}{1+b}",
                        "hint": "$1 - a$ with $a = -b$ becomes $1 + b$. Nothing else changes.",
                        "deconstruct": [
                            "The sum with signs is $1/(1 - a)$ from the earlier step.",
                            "Putting $a = -b$ gives $1/(1 - (-b)) = 1/(1 + b)$.",
                        ],
                    },
                ],
                "closing": r'''
Two formulas that look almost the same and mean very different things. Put $b = 0.6$ into
both: the worst-case gain is $1/(1 - 0.6) = 2.5$, and the gain applied to a constant is
$1/(1 + 0.6) = 0.625$. A factor of four, from one impulse response.

The stability condition is now readable straight off the algebra. The sums exist only when
$|a| < 1$; at $|a| = 1$ the geometric series does not converge and the system is the
accumulator, unstable by the BIBO test; beyond it the impulse response grows and nothing
converges at all. Module 8 draws that boundary as a circle on the $z$-plane and calls
$|a|$ the radius of the pole, but it is this series that puts it there.

One more thing worth carrying forward. Nothing above needed the input, only $h$ — which is
the whole promise of module 1 delivered on the smallest possible example.
''',
            },
            "lab": {
                "title": "Convolution, and the gain hiding in an impulse response",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Three functions. Together they take an LTI system apart.

- `convolve(x, h)` returns the output of a system with impulse response `h` when the
  input is `x`. The result has `len(x) + len(h) - 1` samples. Write the double loop
  — `y[i + j] += x[i] * h[j]` — rather than reaching for a library, because the index
  arithmetic is the thing worth owning.
- `iir_impulse_response(a, n)` returns the first `n` samples of the impulse response
  of the recursive system $y[n] = a\,y[n-1] + x[n]$. Drive it with the impulse
  $x = 1, 0, 0, \dots$ and record $y$ at each step. You should recover $a^n$, which is
  a good check that the recursion is written correctly.
- `bibo_gain(h)` returns $\sum_n |h[n]|$ — the largest output an input bounded by 1
  can ever produce.

Plain lists throughout; NumPy is not needed and not wanted here.
''',
                "files": [{"name": "main.py", "content": r'''
"""Convolution: an LTI system's whole behaviour, from one list of numbers."""


def convolve(x, h):
    """Output of an LTI system with impulse response `h`, driven by `x`.

    The result has len(x) + len(h) - 1 samples.
    """
    # TODO: make a list of zeros of the right length, then accumulate
    #       y[i + j] += x[i] * h[j] over every pair of indices.
    return []


def iir_impulse_response(a, n):
    """First `n` samples of h for the system y[k] = a*y[k-1] + x[k]."""
    # TODO: run the recursion with x = 1 at k = 0 and x = 0 afterwards,
    #       appending y at every step. Start from y = 0.
    return []


def bibo_gain(h):
    """The largest output an input bounded by 1 can produce: the sum of |h|."""
    # TODO: one sum of absolute values.
    return 0.0


if __name__ == "__main__":
    print("{1,2} through {1,1,1}:", convolve([1.0, 2.0], [1.0, 1.0, 1.0]))
    h = iir_impulse_response(0.5, 6)
    print("impulse response of y = 0.5 y[-1] + x:", h)
    print("its gain from a bounded input:", bibo_gain(iir_impulse_response(0.5, 60)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Convolution: an LTI system's whole behaviour, from one list of numbers.

Checked against hand-worked examples: {1,2} * {1,1,1} = {1,3,3,2}, and the
recursion y[k] = 0.5 y[k-1] + x[k] gives h = 1, 0.5, 0.25, ... whose absolute
sum tends to 1/(1 - 0.5) = 2.
"""


def convolve(x, h):
    """Output of an LTI system with impulse response `h`, driven by `x`.

    The result has len(x) + len(h) - 1 samples.
    """
    y = [0.0] * (len(x) + len(h) - 1)
    for i, xv in enumerate(x):
        for j, hv in enumerate(h):
            y[i + j] += xv * hv
    return y


def iir_impulse_response(a, n):
    """First `n` samples of h for the system y[k] = a*y[k-1] + x[k]."""
    h = []
    y = 0.0
    for k in range(n):
        x = 1.0 if k == 0 else 0.0
        y = a * y + x
        h.append(y)
    return h


def bibo_gain(h):
    """The largest output an input bounded by 1 can produce: the sum of |h|."""
    return sum(abs(v) for v in h)


if __name__ == "__main__":
    print("{1,2} through {1,1,1}:", convolve([1.0, 2.0], [1.0, 1.0, 1.0]))
    h = iir_impulse_response(0.5, 6)
    print("impulse response of y = 0.5 y[-1] + x:", h)
    print("its gain from a bounded input:", bibo_gain(iir_impulse_response(0.5, 60)))
'''}],
                "hints": [
                    "`convolve` needs its output list allocated *before* the loops, because the inner statement adds into a slot rather than appending to the end.",
                    "In `iir_impulse_response` the state is one number. Set `y = 0.0` before the loop, and inside it compute `y = a * y + x` with `x` equal to 1 only on the first pass.",
                    "If your impulse response comes out as $1, 1, 1, \\dots$ you are feeding in a step rather than an impulse: the input is 1 at $k = 0$ **and zero at every later step**.",
                    "`bibo_gain` is `sum(abs(v) for v in h)`. For $h[n] = a^n$ it should come out near $1/(1-a)$ once `n` is large enough.",
                ],
                "tests": [
                    {"name": "a two-sample input through a three-sample response", "code": r'''
y = convolve([1.0, 2.0], [1.0, 1.0, 1.0])
assert len(y) == 4, f"2 + 3 - 1 is 4 samples, got {len(y)}"
assert all(abs(a - b) < 1e-12 for a, b in zip(y, [1.0, 3.0, 3.0, 2.0])), \
    f"expected [1, 3, 3, 2], got {y}"
'''},
                    {"name": "convolution is commutative", "code": r'''
a = convolve([1.0, 2.0, 3.0], [1.0, -1.0, 4.0])
b = convolve([1.0, -1.0, 4.0], [1.0, 2.0, 3.0])
want = [1.0, 1.0, 5.0, 5.0, 12.0]
assert len(a) == 5 and len(b) == 5, \
    f"3 + 3 - 1 is 5 samples either way round, got {len(a)} and {len(b)}"
assert all(abs(v - w) < 1e-12 for v, w in zip(a, want)), f"expected {want}, got {a}"
assert all(abs(v - w) < 1e-12 for v, w in zip(a, b)), \
    f"x * h and h * x must agree: {a} against {b}"
'''},
                    {"name": "the recursion's impulse response is a geometric decay", "code": r'''
h = iir_impulse_response(0.5, 6)
assert len(h) == 6, f"asked for 6 samples, got {len(h)}"
want = [1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125]
assert all(abs(a - b) < 1e-12 for a, b in zip(h, want)), \
    f"h[k] should be 0.5**k, so {want}; got {h}"
'''},
                    {"name": "a step through that system settles at 2", "code": r'''
h = iir_impulse_response(0.5, 10)
y = convolve([1.0] * 10, h)
assert abs(y[9] - 1.998046875) < 1e-9, \
    f"ten samples of step in, the output is the sum of the first ten h, 1.998046875, got {y[9]}"
assert y[0] == 1.0, f"the first output sample is just h[0], got {y[0]}"
'''},
                    {"name": "the sum of |h| is the worst-case gain", "code": r'''
g = bibo_gain([1.0, -2.0, 3.0])
assert abs(g - 6.0) < 1e-12, f"|1| + |-2| + |3| is 6, got {g}"
slow = bibo_gain(iir_impulse_response(0.8, 200))
assert abs(slow - 5.0) < 1e-6, \
    f"sum of 0.8**n tends to 1/(1 - 0.8) = 5, got {slow}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "The Fourier series and the spectrum of a periodic signal",
            "summary": "A repeating waveform is a sum of sinusoids at multiples of one frequency, and the list of their sizes is its spectrum.",
            "concepts": [
                "A signal is **periodic** with period $T$ when $x(t + T) = x(t)$ for all $t$. Its **fundamental frequency** is $f_0 = 1/T$, and $\\omega_0 = 2\\pi/T$.",
                "Fourier's claim: any such signal (with mild conditions that every real waveform satisfies) is a sum of sinusoids at $f_0$ and its integer multiples — the **harmonics**. Nothing at any other frequency ever appears.",
                "Trigonometric form: $x(t) = \\frac{a_0}{2} + \\sum_{n=1}^{\\infty}\\left[a_n\\cos(n\\omega_0 t) + b_n\\sin(n\\omega_0 t)\\right]$, where $a_0/2$ is the mean value of the signal.",
                "**Analysis**: $a_n = \\frac{2}{T}\\int_T x(t)\\cos(n\\omega_0 t)\\,dt$ and $b_n = \\frac{2}{T}\\int_T x(t)\\sin(n\\omega_0 t)\\,dt$. These work because harmonics are **orthogonal**: over a whole period, the product of two different harmonics integrates to zero, so the integral picks out one coefficient and discards the rest.",
                "Complex form, which is the one used from module 3 onwards: $c_n = \\frac{1}{T}\\int_T x(t)e^{-jn\\omega_0 t}\\,dt$ and $x(t) = \\sum_{n=-\\infty}^{\\infty} c_n e^{jn\\omega_0 t}$. For a real signal $c_{-n} = c_n^{*}$, so the negative frequencies carry no new information — they are the bookkeeping that keeps the sum real.",
                "The **line spectrum** plots $|c_n|$ against frequency. A periodic signal's spectrum is a set of isolated lines at $0, f_0, 2f_0, \\dots$ and is exactly zero in between.",
                "Symmetry saves work. A signal odd about $t = 0$ has only sine terms; an even one has only cosine terms; one with half-wave symmetry has only odd harmonics.",
                "The square wave of amplitude $A$, odd about the origin, has $b_n = 4A/(n\\pi)$ for odd $n$ and nothing else. Its harmonics decay as $1/n$.",
                "Smoothness sets the decay rate. A jump in the signal gives coefficients falling as $1/n$; a kink — continuous but with a jump in the slope, like a triangle wave — gives $1/n^2$. Sharp edges are expensive in bandwidth, and that is a statement about every digital signal ever transmitted.",
                "Truncating the series at $N$ harmonics overshoots each jump by about 9% of the jump height, however large $N$ is. Adding harmonics narrows the ripple but never shrinks it: this is the **Gibbs phenomenon**.",
                "**Parseval's theorem**: the mean square of the signal equals $\\left(\\frac{a_0}{2}\\right)^2 + \\sum_n \\frac{a_n^2 + b_n^2}{2}$. Power adds across harmonics even though amplitudes do not, which is why a spectrum is usually drawn as power.",
            ],
            "read": [
                {
                    "title": "Why a repeating waveform is nothing but harmonics",
                    "minutes": 12,
                    "body": r'''
Put a 1 kHz square wave on a function generator and feed it into a filter so narrow that
it passes one frequency and almost nothing else. Sweep that filter slowly upwards from
zero and write down what the meter on its output says.

At 1 kHz the meter jumps. Between there and 3 kHz — at 1.4 kHz, at 2 kHz, at 2.7 kHz —
it reads nothing at all. At 3 kHz it jumps again, to about a third of the first reading.
Nothing at 4 kHz. Something at 5 kHz, about a fifth of the first. The signal is not made
of a *band* of frequencies. It is made of a picket fence of them, standing at exact
multiples of the rate at which the waveform repeats, and the axis between them is empty.

That is an experiment, not a theorem. This reading is the theorem, and it comes in two
halves: an argument that fixes which frequencies are even allowed to be there, and a
trick that says how much of each there is.

## Half one: only multiples can survive

A signal is **periodic** with period $T$ when $x(t + T) = x(t)$ for every $t$, and its
**fundamental frequency** is $f_0 = 1/T$. Suppose such a signal really is a sum of
sinusoids. Ask what a component at some frequency $f$ would have to do to belong to that
sum.

After $T$ seconds the whole signal is obliged to be exactly what it was. So every
component in it must come back to exactly what *it* was — the components are independent,
and nothing else in the sum can cover for one that has drifted. A sinusoid returns to
itself after $T$ seconds only if $T$ contains a whole number of its cycles.

Try a component at 1.5 kHz inside a signal that repeats every 1 ms:

$$\sin\!\left(2\pi \cdot 1500\,(t + 0.001)\right) = \sin\!\left(2\pi\cdot 1500\,t + 3\pi\right) = -\sin\!\left(2\pi \cdot 1500\, t\right)$$

It comes back *inverted*. One millisecond later this component is the negative of what it
was, and no arrangement of the other components repairs that, because each of them has
also come back to something. A signal containing a 1.5 kHz term is not a 1 ms-periodic
signal; it is a 2 ms-periodic one.

The frequencies that survive are exactly those whose phase advances by a whole number of
turns in $T$ seconds: $f = n/T = nf_0$. The candidate list is therefore settled before any
integration happens — a constant, then $f_0$, $2f_0$, $3f_0$, and so on forever. These are
the **harmonics**, and the only question left is how much of each is present.

That question has an answer for every waveform you will meet on a bench. The conditions
are mild — Dirichlet's: over one period the signal must have finitely many maxima, minima
and jumps, and $\int_T |x|\,dt$ must be finite — and constructing a periodic signal that
fails them takes deliberate effort.

## Half two: how orthogonality picks out one coefficient

Write the sum with unknown weights:

$$x(t) = \frac{a_0}{2} + \sum_{n=1}^{\infty}\left[a_n\cos(n\omega_0 t) + b_n\sin(n\omega_0 t)\right], \qquad \omega_0 = \frac{2\pi}{T}$$

Both a cosine and a sine appear at each harmonic because a component at $nf_0$ has an
amplitude *and* a phase, and $\cos$ and $\sin$ together span every phase at that
frequency.

To get one weight out, multiply the whole series by the harmonic you are hunting and
average over exactly one period. The reason that works is a trigonometric identity you
have had since school:

$$\cos(m\omega_0 t)\cos(n\omega_0 t) = \tfrac{1}{2}\left[\cos\left((m-n)\omega_0 t\right) + \cos\left((m+n)\omega_0 t\right)\right]$$

Both cosines on the right sit at harmonic frequencies, so each completes a whole number of
cycles in $T$ and averages to zero — *unless* $m = n$, when the first becomes $\cos 0 = 1$
and averages to $\tfrac{1}{2}$. Every term in the infinite sum is annihilated except the
one you multiplied by, and that one survives at half strength. Undo the half and you have
the **analysis formula**:

$$a_n = \frac{2}{T}\int_T x(t)\cos(n\omega_0 t)\,dt, \qquad b_n = \frac{2}{T}\int_T x(t)\sin(n\omega_0 t)\,dt$$

Two things are worth pinning down while they are still visible. The factor $2/T$ is not a
convention; it is the $\tfrac{1}{2}$ from the identity being cancelled. And the odd-looking
$a_0/2$ in the series exists so that $n = 0$ obeys the same analysis formula as everything
else: $a_0 = (2/T)\int_T x\,dt$ is *twice* the mean, so the constant term in the series has
to be $a_0/2$, which is the mean. This is the most common factor-of-two error in the
subject.

## Worked example one: the square wave

Take the waveform from the bench: $x(t) = +5$ V for $0 < t < T/2$ and $-5$ V for
$T/2 < t < T$, with $T = 1$ ms, so $f_0 = 1$ kHz and $\omega_0 T = 2\pi$.

Two shortcuts first. The mean over a period is zero, so $a_0 = 0$. The waveform is odd
about $t = 0$, so every $a_n$ is zero as well — an odd function times an even one,
integrated over a symmetric interval, gives zero every time. Only the $b_n$ are left, and
only they need work.

```
b_n = (2/T) [ INT(0 .. T/2) (+5) sin(n w0 t) dt + INT(T/2 .. T) (-5) sin(n w0 t) dt ]

with   INT sin(n w0 t) dt = -cos(n w0 t) / (n w0)

first piece    (+5) * [ 1 - cos(n pi) ] / (n w0)  =  (5 / n w0) (1 - cos n pi)
second piece   (-5) * [ cos(n pi) - 1 ] / (n w0)  =  (5 / n w0) (1 - cos n pi)

b_n = (2/T) * (10 / (n w0)) * (1 - cos n pi)
    = (20 / (2 pi n)) * (1 - cos n pi)            using w0 T = 2 pi
    = (10 / (n pi)) * (1 - cos n pi)
```

Now read the factor $1 - \cos n\pi$. For even $n$ it is $1 - 1 = 0$: **the even harmonics
are simply not there.** For odd $n$ it is $1 - (-1) = 2$, leaving $b_n = 20/(n\pi)$ —
which is $4A/(n\pi)$ with $A = 5$ V, the standard result.

```
b_1 = 20 / (1 pi) = 6.3662 V        b_5 = 20 / (5 pi) = 1.2732 V
b_3 = 20 / (3 pi) = 2.1221 V        b_7 = 20 / (7 pi) = 0.9095 V
```

There is the bench measurement, predicted: a line at 1 kHz, nothing at 2 kHz, a line at
3 kHz one third the size, nothing at 4 kHz, a line at 5 kHz one fifth the size.

It is worth checking that the sum does what it claims. At $t = T/4$ every odd harmonic is
at a peak, $\sin(n\pi/2) = +1, -1, +1, -1, \dots$, and the true waveform is $+5$ V:

```
one term      6.3662
two terms     6.3662 - 2.1221 = 4.2441
three terms   4.2441 + 1.2732 = 5.5174
four terms    5.5174 - 0.9095 = 4.6079
five terms    4.6079 + 0.7074 = 5.3153
```

Closing in on 5 V, alternately over and under, and slowly. That slowness is the subject of
the next reading.

## Worked example two: a pulse train, where the shortcuts run out

The square wave is symmetric in level and in time, which hides half the machinery. Take
instead a pulse train: $x(t) = 4$ V for $|t| < 0.125$ ms and 0 V through the rest of a
$T = 1$ ms period. The pulse is 0.25 ms wide — a **duty cycle** of $D = \tau/T = 0.25$ —
and it is centred on $t = 0$, which makes the waveform even. Even means every $b_n$
vanishes and the series is all cosines.

The mean is no longer zero, so the constant term has to be computed:

```
a_0 / 2 = (1/T) INT(T) x dt = (area of one pulse) / T
        = 4 V * 0.25 ms / 1 ms
        = 1.00 V
```

which is only the average of a signal that sits at 4 V a quarter of the time. For the
rest, the integral runs over the pulse alone, because $x$ is zero everywhere else:

```
a_n = (2/T) INT(-tau/2 .. +tau/2) 4 cos(n w0 t) dt
    = (8/T) * [ sin(n w0 t) / (n w0) ] evaluated across the pulse
    = (8/T) * 2 sin(n w0 tau / 2) / (n w0)
    = (16 / (2 pi n)) * sin(n pi tau / T)         using w0 T = 2 pi
    = (8 / (n pi)) * sin(n pi / 4)                with tau/T = 0.25
```

and the numbers come straight out of it:

```
n    sin(n pi/4)     a_n
1      0.7071      (8/1pi)(+0.7071) = +1.8006 V
2      1.0000      (8/2pi)(+1.0000) = +1.2732 V
3      0.7071      (8/3pi)(+0.7071) = +0.6002 V
4      0.0000                        =  0      V
5     -0.7071      (8/5pi)(-0.7071) = -0.3601 V
6     -1.0000      (8/6pi)(-1.0000) = -0.4244 V
```

Three things here that the square wave could not show you. The even harmonics are present
now — it is half-wave symmetry, not evenness, that kills those, and this waveform has
none. Every fourth harmonic is missing exactly: the 4th harmonic fits precisely one whole
cycle inside a pulse a quarter of a period wide, and a whole cycle of a cosine integrates
to zero over the interval it fits into, so it collects nothing at all. And the
coefficients go negative, which is not a negative amplitude but a phase of $180°$ — the
5th harmonic is a cosine turned upside down.

## The mistake, and why it is tempting

Two of them, both about the picture rather than the algebra.

The first is reading a spectrum as continuous: "there is a bit of energy around 1.5 kHz".
It is tempting because a real spectrum analyser draws exactly that — a smear with a peak
on it, not a line. The analyser is not lying and neither is the theory. It has a *finite
record*, which is a different signal from an eternally repeating one, and module 9 is
about the difference. For a genuinely periodic signal the spectrum is exactly zero between
the lines, and the argument in the first section is the reason.

The second is putting the constant into the series as $a_0$ rather than $a_0/2$, which
doubles the DC level. It is tempting because $a_0$ comes from the same formula as every
other $a_n$, so it looks as though it should enter the sum the same way. It does not, and
the $2/T$ in front of the analysis integral is exactly why.

## Where this stops holding

At a jump the series does not converge to the waveform. Look at the square wave at
$t = 0$: every term is $\sin 0 = 0$, so the series returns 0 V at an instant when the
waveform is $\pm 5$ V. That is not an error in the coefficients; it is what the equality
means. The series converges to the **midpoint** of a jump, and it converges *in the mean
square* — a statement about total error across a period, not about any single instant.
Where that distinction gets expensive is the Gibbs overshoot in the next reading.

More seriously, the whole construction assumes a signal that repeats forever. A tone burst
does not. A one-second recording of a 1 kHz sine is not a 1 kHz sine: it is a sine
multiplied by a one-second rectangle, and it is not periodic at all. Let the period stretch
towards infinity and the lines crowd together until they merge into a continuum — the sum
becomes an integral and the Fourier *series* becomes the Fourier *transform*, which is
module 3. Everything computed here survives that move. It simply stops being a list and
starts being a curve.
''',
                },
                {
                    "title": "Reading a spectrum: symmetry, decay, power, and the overshoot that never leaves",
                    "minutes": 12,
                    "body": r'''
A 1 kHz square wave goes into one end of a cable and comes out of the other with its
corners rounded off and a ripple running along its flat tops. Nothing was broken. The
cable passes frequencies up to about 5 kHz and rejects what is above, and the previous
reading says what that means: of the picket fence standing at 1, 3, 5, 7, 9 kHz and
onwards, three lines got through and the rest did not.

This reading is about the four things you can read off that picket fence without
reconstructing the waveform at all — which lines are present, how fast they shrink, how
much of the signal each one carries, and what happens when you cut the fence off.

## Which lines are present: three symmetries, and only two of them are real

Before computing any integral, three checks are worth a minute.

**Even**, $x(-t) = x(t)$: cosine terms only. Each $b_n$ integrates an even function against
an odd one over a symmetric interval, and gets zero every time.

**Odd**, $x(-t) = -x(t)$: sine terms only, by the same argument with the roles swapped.

**Half-wave**, $x(t + T/2) = -x(t)$ — the second half of the period is the first half
turned upside down: *odd* harmonics only. That one is worth seeing properly. Harmonic $2k$
obeys

$$\cos\!\left(2k\omega_0(t + T/2)\right) = \cos\!\left(2k\omega_0 t + 2k\pi\right) = \cos(2k\omega_0 t)$$

An even harmonic comes back **unchanged** after half a period. It is constitutionally
incapable of flipping sign when the signal does, so if the signal insists on flipping,
every even harmonic has to be absent.

Now the part most treatments skip. The first two symmetries are properties of *where you
put $t = 0$*, not of the waveform. Slide the time origin and an odd square wave becomes an
even one: the sines turn into cosines and back again. What does not move is the size of
each line, $\sqrt{a_n^2 + b_n^2}$. Half-wave symmetry is different in kind — it compares
the waveform with itself rather than with your clock, and no choice of origin creates or
destroys it. So "odd harmonics only" is a fact about the signal; "sines only" is a fact
about your bookkeeping.

## How fast they shrink: smoothness, one integration by parts at a time

Integrate the analysis formula by parts once. Everything in sight is periodic, so the
boundary terms at the two ends of the period cancel, and what is left is the same integral
with $x$ replaced by $x'$ and a factor of $1/(n\omega_0)$ pulled out the front. If $x$ is
continuous you may do it again, and again, for as long as the derivatives stay continuous.

Each pass costs the coefficients a factor of $n$:

* a waveform that **jumps** cannot be integrated by parts even once, so its coefficients
  fall as $1/n$;
* one that is continuous but whose **slope** jumps survives a single pass — $1/n^2$;
* every further derivative that stays continuous buys another factor of $1/n$.

Put a square wave and a triangle wave of the same amplitude side by side. Both are odd,
both have half-wave symmetry, so both contain exactly the same frequencies: odd multiples
of $f_0$. Containing a frequency and containing much of it are different things.

```
n      square  4/(n pi)      triangle  8/(n^2 pi^2)     relative to the fundamental
1        1.2732                0.8106                  1/1     vs    1/1
3        0.4244                0.0901                  1/3     vs    1/9
5        0.2546                0.0324                  1/5     vs    1/25
7        0.1819                0.0165                  1/7     vs    1/49
```

This is why sharp edges are expensive. A digital link alternating ones and zeros at
1 Gbit/s is transmitting a 500 MHz square wave, and its third harmonic — still a third of
the fundamental — sits at 1.5 GHz. The bandwidth a channel needs is set by the edges, not
by the bit rate.

## How much each line carries: Parseval

Amplitudes at different frequencies never add. Powers do. That is **Parseval's theorem**:

$$\overline{x^2} = \left(\frac{a_0}{2}\right)^{2} + \sum_{n=1}^{\infty}\frac{a_n^{2} + b_n^{2}}{2}$$

The mean square of the whole signal is the mean square of its DC term plus the mean square
of each harmonic, and the mean square of a sinusoid of peak amplitude $b$ is $b^2/2$.

**Worked example.** $x(t) = 3 + 4\cos(\omega_0 t) - 2\sin(3\omega_0 t)$ volts. No integral
is needed here: the signal is already written as a series, so the coefficients can simply
be read off — $a_0/2 = 3$, $a_1 = 4$, $b_3 = -2$, and every other coefficient is zero.

```
mean square = 3^2  +  4^2 / 2  +  (-2)^2 / 2
            = 9    +  8        +  2            = 19 V^2

RMS = sqrt(19) = 4.359 V
```

Notice what is *not* halved: the DC term. The $\tfrac{1}{2}$ on the harmonics is the
average of $\cos^2$ over a cycle, and a constant has no $\cos^2$ to average. Notice too
what has vanished from the calculation entirely — the phases. Change the sign of the third
harmonic, or slide it by any angle you like, and the waveform on a scope changes
completely while this number does not move at all.

**A second example, and a budget.** For a square wave of amplitude $A$ the mean square
needs no series at all: $x^2(t) = A^2$ at every instant, so $\overline{x^2} = A^2$. The
$n$th harmonic carries $b_n^2/2 = 8A^2/(n^2\pi^2)$, so the *fraction* of the total in each
harmonic is $8/(n^2\pi^2)$, independent of amplitude:

```
harmonic     its share      running total
   1st        81.06%           81.06%
   3rd         9.01%           90.06%
   5th         3.24%           93.31%
   7th         1.65%           94.96%
   9th         1.00%           95.96%
```

Which explains the cable. Cutting off above 5 kHz kept 93.3% of the power and still made a
visible mess of the waveform, because the missing 6.7% is precisely the part that was
building the edges. Reaching 99% of the power takes harmonics up to the **41st** — 41 kHz
for a 1 kHz square wave. Power converges quickly. Shape does not.

## Cutting the fence off: Gibbs

Keep the first $N$ harmonics and throw the rest away, which is what every real filter,
channel and reconstruction does. Near a jump, the partial sum overshoots. Here is the peak
of that partial sum for a square wave running between $-1$ and $+1$:

```
N = 9 harmonics       peak = 1.1823
N = 21                peak = 1.1797
N = 99                peak = 1.1790
N = 999               peak = 1.17898
```

It is not converging to 1. It is converging to 1.17898 — an overshoot of 0.179 on a jump
of height 2, about **8.95% of the jump**, forever, whatever $N$ is. What does shrink is the
*width* of the ripple: it is squeezed in towards the discontinuity as $N$ grows, so the
area under the error, and with it the mean-square error, does go to zero. Mean-square
convergence and pointwise convergence are different promises, and the series only ever made
the first one.

## The mistake, and why it is tempting

Adding amplitudes. Given harmonics of 3 V and 4 V, the answer "7 V, or $7/\sqrt{2}$ RMS"
is almost irresistible, because for a single sinusoid the RMS really is $A/\sqrt{2}$ and
the $\sqrt{2}$ starts to feel like a property of the arithmetic rather than of the
sinusoid. It is a property of the sinusoid. Two harmonics of 3 V and 4 V have RMS
$\sqrt{3^2/2 + 4^2/2} = \sqrt{12.5} = 3.54$ V, and nothing justifies adding them: they are
at different frequencies, so whatever alignment they have at one instant they have lost a
few cycles later.

The second version of the same mistake is expecting more harmonics to fix the overshoot.
That is tempting because every other kind of numerical error does shrink when you use more
terms. This one does not, it is not a numerical artefact, and no amount of computing power
touches it.

## Where this stops holding

**Parseval throws phase away, and phase is most of the waveform.** Take the square wave's
coefficients and randomise every phase while keeping every magnitude. The power spectrum is
identical, the RMS is identical, and on a scope you get something that looks like noise.
Any measurement made from a magnitude spectrum alone is blind to this — occasionally that
is exactly what you want, which is why a spectrum analyser is useful on a signal whose
timing you do not control, and occasionally it is a trap.

**The decay rules describe ideal waveforms.** A real square wave has a finite rise time
$t_r$, so it does not truly jump, and its coefficients only fall as $1/n$ up to about
$f = 1/(\pi t_r)$ before steepening towards $1/n^2$. For a 100 ns edge that knee sits
around 3 MHz: below it the signal behaves like the ideal square wave of this reading, and
above it there is far less energy present than the $1/n$ law predicts. That knee, and not
the bit rate, is what an emissions test ends up measuring.

**And the cure for Gibbs is not more terms but gentler ones.** Rather than cutting the
series off abruptly, taper the last coefficients down towards zero. The overshoot largely
disappears, at the price of blurring the very edge you were trying to reproduce. That
trade, made properly and with names attached, is the window design of module 9.
''',
                },
            ],
            "quiz": {
                "title": "Harmonics, symmetry and decay",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A periodic signal has a period of 2 ms. Which frequencies may appear in its spectrum?",
                        "opts": [
                            "any frequency from 0 to 500 Hz",
                            "500 Hz only",
                            "0, 500, 1000, 1500 Hz and so on",
                            "any frequency above 500 Hz",
                        ],
                        "a": 2,
                        "why": r'''
$f_0 = 1/T = 500$ Hz, and a periodic signal contains only the fundamental, its integer
multiples, and a possible DC term. The spectrum is a picket fence of lines, not a
continuous band — that is what makes it a *series* rather than a transform. "Any frequency from 0 to 500 Hz" is the answer for an aperiodic signal, which is
module 3, and the difference between the
two pictures is the single most useful thing to keep straight in this course.
''',
                    },
                    {
                        "q": "A signal is even about $t = 0$, that is $x(-t) = x(t)$. What does its Fourier series contain?",
                        "opts": [
                            "cosine terms only (plus a possible DC term)",
                            "sine terms only",
                            "odd harmonics only",
                            "no useful simplification follows from evenness",
                        ],
                        "a": 0,
                        "why": r'''
Cosine is even and sine is odd, so an even signal can be built entirely from cosines;
formally, $b_n$ integrates an even function against an odd one over a symmetric interval
and gets zero every time. This is worth exploiting before touching an integral, because
it halves the work. Answering "odd harmonics only" confuses two different symmetries: *half-wave* symmetry,
$x(t + T/2) = -x(t)$, is the one that kills the even harmonics, and the square wave has
both properties at once.
''',
                    },
                    {
                        "q": "A square wave and a triangle wave have the same period and the same amplitude. How do their harmonics compare?",
                        "opts": [
                            "identical, because they contain the same frequencies",
                            "the triangle's decay faster, because its waveform has no jump",
                            "the square's decay faster, because it spends its time at two fixed levels",
                            "neither decays — both series go on with equal terms forever",
                        ],
                        "a": 1,
                        "why": r'''
The square wave jumps, so its coefficients fall only as $1/n$; the triangle is continuous
and only its slope jumps, so its coefficients fall as $1/n^2$. Both contain the same set
of frequencies — odd multiples of $f_0$ — which is what makes "identical, because they contain the same frequencies"
tempting, but
containing a frequency and containing much of it are different things. The rule
generalises: each extra derivative that stays continuous buys another factor of $1/n$.
''',
                    },
                    {
                        "q": "You reconstruct a square wave from its first 99 harmonics and then from its first 999. What happens to the overshoot at each jump?",
                        "opts": [
                            "it halves each time the harmonic count is multiplied by ten",
                            "it disappears entirely once enough harmonics are included",
                            "it grows, because more harmonics means more ripple",
                            "it stays at about 9% of the jump, but is squeezed into a narrower region",
                        ],
                        "a": 3,
                        "why": r'''
This is Gibbs. The overshoot converges to about 8.95% of the jump height and stays there
no matter how many terms are added; what does shrink is its width, so the *energy* in the
ripple goes to zero even though its height does not. For a square wave running between
$-1$ and $+1$ the jump is 2, so the partial sum peaks near 1.179 — a number you will
compute in this module's lab. It is not a numerical error and it cannot be tuned away.
''',
                    },
                    {
                        "q": "A signal has just two harmonics, of amplitudes 3 V and 4 V. What is its RMS value?",
                        "opts": ["$7/\\sqrt{2}$ V", "5 V", "$5/\\sqrt{2}$ V", "7 V"],
                        "a": 2,
                        "why": r'''
By Parseval the mean squares add: $\frac{3^2}{2} + \frac{4^2}{2} = 12.5$, so the RMS is
$\sqrt{12.5} = 5/\sqrt{2} \approx 3.54$ V. Amplitudes never add unless the components are
at the same frequency and in phase, which harmonics by definition are not. Note also what
is *absent* from the calculation: the phases of the two harmonics. Change them and the
waveform looks completely different while its RMS value does not move at all.
''',
                    },
                    {
                        "q": "Why does multiplying $x(t)$ by $\\cos(n\\omega_0 t)$ and integrating over one period return $a_n$ and nothing else?",
                        "opts": [
                            "because the integral of any product over a period is zero unless the two factors are identical",
                            "because harmonics are orthogonal: over a whole period, any two different harmonics multiply to something that integrates to zero",
                            "because the cosine is normalised to unit area",
                            "because the higher harmonics are too small to matter",
                        ],
                        "a": 1,
                        "why": r'''
Orthogonality is the mechanism, and it is worth seeing once: $\cos(m\omega_0 t)\cos(n\omega_0 t)$
expands to half the sum of two cosines at frequencies $(m-n)\omega_0$ and $(m+n)\omega_0$,
and any whole number of cycles of a cosine integrates to zero — unless $m = n$, when the
first term becomes a constant $1/2$. That surviving constant is where the factor $2/T$ in
the analysis formula comes from. "The integral of any product over a period is zero unless the two factors are
identical" is too strong: many different products integrate to something non-zero; it is the harmonic relationship that makes them vanish.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "A signal already written as a series",
                    "minutes": 8,
                    "caption": "no integration required — every coefficient is on the page",
                    "lang": "text",
                    "brief": r'''
Most Fourier work is spent computing coefficients. This one is not: the signal arrives
already written as a sum of harmonics, so the coefficients can be read straight off it,
and the only skill being drilled is matching each term to its slot and then turning the
list into a power.

Watch the two places where the arithmetic differs from what a first guess would do: the
DC term is not halved, and nothing at all lives at $2f_0$.
''',
                    "listing": """  x(t) = 3 + 4 cos(w0 t) - 2 sin(3 w0 t)   volts,   T = 1 ms

  fundamental      f0 = 1/T                            = ___ kHz
  DC term          a0/2                                = ___ V
  at   f0          a1 = ___ V    b1 = 0 V              amplitude 4 V
  at 2 f0          a2 = 0 V      b2 = 0 V              amplitude ___ V
  at 3 f0          a3 = 0 V      b3 = ___ V            amplitude 2 V

  mean square      (a0/2)^2 + (a1^2 + b1^2)/2 + (a3^2 + b3^2)/2
                 = 9        + ___             + 2      = 19 V^2

  RMS              sqrt(19)                            = ___ V
""",
                    "blanks": [
                        {
                            "prompt": "The period is 1 ms. What is the fundamental frequency, in kHz?",
                            "hole": "f0",
                            "opts": ["0.5", "1", "2", "3"],
                            "a": 1,
                            "why": "$f_0 = 1/T = 1/(1\\text{ ms}) = 1$ kHz. Every frequency in this signal is a whole multiple of it, so the terms sit at 1 kHz and 3 kHz and nowhere else.",
                        },
                        {
                            "prompt": "The constant term of the series. What DC level does this signal sit on?",
                            "hole": "V",
                            "opts": ["1.5", "3", "4", "6"],
                            "a": 1,
                            "why": "3 V — the constant written in the signal *is* the mean value, and the mean value is what $a_0/2$ denotes. The 1.5 V answer comes from halving it a second time: $a_0$ itself is 6 V here, and it is $a_0/2$ that enters the series.",
                        },
                        {
                            "prompt": "The cosine coefficient at the fundamental.",
                            "hole": "a1",
                            "opts": ["2", "3", "4", "8"],
                            "a": 2,
                            "why": "$a_1 = 4$ V, read directly off the $4\\cos(\\omega_0 t)$ term. With $b_1 = 0$ the component at 1 kHz is a pure cosine of amplitude $\\sqrt{a_1^2 + b_1^2} = 4$ V and phase zero.",
                        },
                        {
                            "prompt": "How big is the component at 2 kHz?",
                            "hole": "V",
                            "opts": ["0", "2", "4", "it cannot be determined from what is given"],
                            "a": 0,
                            "why": "Zero. A harmonic is present only if the series contains a term at that frequency, and this one jumps straight from $f_0$ to $3f_0$. A line spectrum with a gap in it is completely normal — a square wave has a gap at every even harmonic.",
                        },
                        {
                            "prompt": "The sine coefficient at the third harmonic. Mind the sign.",
                            "hole": "b3",
                            "opts": ["2", "-2", "-1", "6"],
                            "a": 1,
                            "why": "$b_3 = -2$ V. The minus sign is a phase, not a negative size: $-2\\sin(3\\omega_0 t)$ is a 2 V sinusoid turned upside down. It matters for the waveform and, as the next line shows, not at all for the power.",
                        },
                        {
                            "prompt": "The fundamental's contribution to the mean square: $(a_1^2 + b_1^2)/2$ with $a_1 = 4$ and $b_1 = 0$.",
                            "hole": "V^2",
                            "opts": ["4", "8", "16", "2"],
                            "a": 1,
                            "why": "$(4^2 + 0)/2 = 8$ V². The halving is the average of $\\cos^2$ over a cycle, which is why a 4 V peak sinusoid contributes 8 V² and not 16. The same halving is what the DC term does *not* get.",
                        },
                        {
                            "prompt": "The RMS value: the square root of 19.",
                            "hole": "V",
                            "opts": ["3.08", "4.36", "4.50", "9.00"],
                            "a": 1,
                            "why": "$\\sqrt{19} = 4.359$ V. Compare it with the temptation to add: $3 + 4 + 2 = 9$ V, or $9/\\sqrt{2} = 6.36$ V. Neither is anywhere near, because components at different frequencies do not line up, and power rather than amplitude is what adds across a spectrum.",
                        },
                    ],
                },
                {
                    "title": "Which terms survive, before any integral",
                    "minutes": 9,
                    "caption": "five waveforms, and what a symmetry check alone can tell you",
                    "lang": "text",
                    "brief": r'''
A symmetry check costs a few seconds and can halve or quarter the work — or, better, tell
you that a coefficient you were about to spend ten minutes on is zero.

Three separate properties are in play and they are easy to run together. Evenness and
oddness are about $t = 0$, so they depend on where you started your clock. Half-wave
symmetry, $x(t + T/2) = -x(t)$, is about the waveform itself and does not care about the
clock. And the decay rate is about smoothness — a jump gives $1/n$, a kink gives $1/n^2$.

Every waveform below has its mean stated, so the DC term is never in doubt.
''',
                    "listing": """  waveform, one period described                          its series contains
 -------------------------------------------------------------------------------
  square, +A then -A, odd about t = 0                     ___

  the same square wave lifted to run from 0 to 2A         ___

  triangle, even about t = 0, mean zero                   ___

  pulse train 0 to A, 25% duty, even about t = 0          ___

  sawtooth ramp, odd about t = 0, mean zero               ___
""",
                    "blanks": [
                        {
                            "prompt": "The plain square wave: odd, mean zero, and its second half is the first half inverted.",
                            "hole": "?",
                            "opts": [
                                "cosine terms at odd harmonics only",
                                "sine terms at every harmonic",
                                "sine terms at odd harmonics only",
                                "a DC term plus sine terms at every harmonic",
                            ],
                            "a": 2,
                            "why": "Odd about $t = 0$ removes every cosine, and half-wave symmetry removes every even harmonic, leaving sines at $f_0, 3f_0, 5f_0, \\dots$ with $b_n = 4A/(n\\pi)$. Two independent symmetries, each killing a different half of the table.",
                        },
                        {
                            "prompt": "Now add a constant so the same waveform runs between 0 and $2A$ instead of $-A$ and $+A$. What changes?",
                            "hole": "?",
                            "opts": [
                                "the same sine terms, unchanged",
                                "the same sine terms, plus a DC term of $A$",
                                "cosine terms plus a DC term of $A$",
                                "sine terms at every harmonic now, plus a DC term of $A$",
                            ],
                            "a": 1,
                            "why": "Adding a constant adds a constant: $a_0/2 = A$ appears and nothing else moves. The AC part of the waveform is untouched, so its harmonics are untouched — which is worth remembering whenever a scope shows a waveform sitting on an offset and you are only interested in the shape.",
                        },
                        {
                            "prompt": "A triangle wave, even about the origin, mean zero. Which terms, and how fast do they fall?",
                            "hole": "?",
                            "opts": [
                                "cosine terms at odd harmonics only, falling as $1/n$",
                                "sine terms at odd harmonics only, falling as $1/n^{2}$",
                                "cosine terms at every harmonic, falling as $1/n^{2}$",
                                "cosine terms at odd harmonics only, falling as $1/n^{2}$",
                            ],
                            "a": 3,
                            "why": "Even kills the sines, half-wave symmetry kills the even harmonics, and the waveform is continuous with a jump only in its *slope*, which buys one extra factor of $1/n$ over the square wave. Same frequencies as the square wave, very different sizes: the third harmonic is a ninth of the fundamental rather than a third.",
                        },
                        {
                            "prompt": "A pulse train, 0 V for three quarters of the period and $A$ for the other quarter, centred on $t = 0$.",
                            "hole": "?",
                            "opts": [
                                "a DC term of $A/2$ and cosine terms at every harmonic",
                                "cosine terms at odd harmonics only",
                                "a DC term of $A/4$ and cosine terms at every harmonic except multiples of four",
                                "sine terms at every harmonic, with no DC term",
                            ],
                            "a": 2,
                            "why": "Even, so cosines only; the mean is $A \\times 0.25 = A/4$; and there is no half-wave symmetry at all, so the even harmonics are present. What *is* missing is every fourth one, because $a_n \\propto \\sin(n\\pi/4)$ vanishes when $n$ is a multiple of 4 — the harmonic that fits a whole number of cycles inside the pulse collects nothing from it.",
                        },
                        {
                            "prompt": "A sawtooth ramping steadily up and dropping vertically back, odd about the origin, mean zero.",
                            "hole": "?",
                            "opts": [
                                "sine terms at every harmonic, falling as $1/n$",
                                "sine terms at odd harmonics only, falling as $1/n$",
                                "sine terms at every harmonic, falling as $1/n^{2}$",
                                "cosine terms at every harmonic, falling as $1/n$",
                            ],
                            "a": 0,
                            "why": "Odd, so sines only. But shift a sawtooth by half a period and you get the same ramp displaced, not the ramp inverted — there is no half-wave symmetry, so the even harmonics stay. And it jumps once per period, so the coefficients fall as $1/n$, which is why a sawtooth is the standard test signal for anything that has to cope with wide bandwidth.",
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "One harmonic of a square wave",
                    "minutes": 4,
                    "brief": r'''
The mechanical one. A single coefficient of the best-known waveform in the subject, so
that the formula is under your fingers before anything is built on top of it.

Nothing here needs an integral: the square wave's coefficients were derived in the reading
and the result is $b_n = 4A/(n\pi)$ for odd $n$, zero for even $n$.
''',
                    "prompt": "What is the peak amplitude of the component at 3 kHz?",
                    "note": "Give the answer in volts, to three significant figures.",
                    "figure": r'''
A function generator produces a square wave that switches between $+5$ V and $-5$ V,
spending equal time at each, and repeats every 1 ms.

```text
   +5 V     +-------+       +-------+
            |       |       |       |
    0 V  - -|- - - -|- - - -|- - - -|- - - -
            |       |       |       |
   -5 V   --+       +-------+       +-------

            0      0.5     1.0     1.5      t in ms
```
''',
                    "given": [
                        {"label": "Amplitude $A$", "value": "5 V"},
                        {"label": "Period $T$", "value": "1 ms"},
                        {"label": "Wanted", "value": "the amplitude of the 3 kHz component"},
                    ],
                    "aside": "3 kHz is the third harmonic of a 1 kHz fundamental, and 3 is odd, so "
                             "there is something there to find. Had the question asked about 2 kHz "
                             "the answer would have been zero.",
                    "answer": 2.1221,
                    "tol": 0.02,
                    "unit": "V",
                    "hint": "$f_0 = 1/T = 1$ kHz, so 3 kHz is $n = 3$. Then $b_n = 4A/(n\\pi)$ with "
                            "$A = 5$ V.",
                    "wrong": "If you got 6.37, that is the fundamental — $n$ was left out of the "
                             "denominator. If you got 1.67, that is $A/3$: the amplitude was divided "
                             "by the harmonic number but the factor $4/\\pi$ was dropped, and that "
                             "factor multiplies the answer by 1.27.",
                    "why": r'''
```
f0  = 1 / 1 ms = 1 kHz,  so 3 kHz is the third harmonic, n = 3

b_3 = 4 A / (n pi)
    = 4 * 5 / (3 * 3.14159)
    = 20 / 9.4248
    = 2.122 V
```

Worth noticing how large that still is. The third harmonic of a square wave is a third of
the fundamental, which is 33% of it — a long way from negligible, and the reason a square
wave sent through a 5 kHz channel comes out visibly deformed rather than slightly rounded.

For the same waveform $b_1 = 6.366$ V, $b_5 = 1.273$ V and $b_7 = 0.909$ V, with nothing
whatever at 2, 4 or 6 kHz.
''',
                },
                {
                    "title": "The power a five-harmonic channel leaves behind",
                    "minutes": 7,
                    "brief": r'''
A different question about the same waveform, and one that a coefficient on its own cannot
answer: not *how big* is a harmonic, but *how much of the signal* is in it.

Two facts do the whole job. A square wave's mean square is easy without any series at all,
because $x^2$ is the same number at every instant. And the $n$th harmonic's share of the
mean square is $b_n^2/2$.
''',
                    "prompt": "What percentage of the signal's total power lies above the fifth harmonic?",
                    "note": "Give the answer as a percentage, to three significant figures.",
                    "figure": r'''
A 2 V amplitude square wave — switching between $+2$ V and $-2$ V — at 500 Hz is sent
through a channel that passes everything up to 2.6 kHz and rejects everything above.

The harmonics that get through are therefore the ones at 500 Hz, 1.5 kHz and 2.5 kHz; the
7th at 3.5 kHz and everything beyond it is stopped. The question is what fraction of the
signal's power was in the part that did not arrive.
''',
                    "given": [
                        {"label": "Amplitude $A$", "value": "2 V"},
                        {"label": "Fundamental", "value": "500 Hz"},
                        {"label": "Harmonics passed", "value": "$n = 1, 3, 5$"},
                        {"label": "Wanted", "value": "the percentage of total power in $n \\ge 7$"},
                    ],
                    "aside": "The amplitude is given so that both sides of the sum can be written "
                             "down, but watch what happens to it: it appears in the total and in "
                             "every harmonic alike, so it cancels and the answer is the same for "
                             "every square wave ever made.",
                    "answer": 6.694,
                    "tol": 0.15,
                    "unit": "%",
                    "hint": "Total mean square is $A^2$, because $|x| = A$ at every instant. Harmonic "
                            "$n$ carries $b_n^2/2 = 8A^2/(n^2\\pi^2)$. Divide, add up $n = 1, 3, 5$, "
                            "and subtract from 1.",
                    "wrong": "If you got 18.9%, you counted everything above the *fundamental* rather "
                             "than everything above the fifth. If you got 3.24%, that is the fifth "
                             "harmonic's own share, which is inside the channel rather than outside "
                             "it. If you got 0.0669, the answer is right but it is a fraction, and "
                             "the question asked for a percentage.",
                    "why": r'''
```
total power        mean of x^2 = A^2 = 4.00 V^2      (|x| = 2 V at every instant)

harmonic n         b_n = 4A/(n pi),  power = b_n^2 / 2 = 8 A^2 / (n^2 pi^2)
fraction of total  = 8 / (n^2 pi^2)                    -- the A^2 cancels

  n = 1     8 / (1 * 9.8696) = 0.81057     81.06%
  n = 3     8 / (9 * 9.8696) = 0.09006      9.01%
  n = 5     8 / (25 * 9.8696) = 0.03242     3.24%
                                          -------
  through the channel                      93.31%
  left behind                               6.69%
```

So the channel delivered 93.3% of the power and still made a mess of the waveform. That is
the lesson worth taking out of the arithmetic: power converges quickly and shape does not,
because the missing 6.7% is entirely concentrated in the fast wiggles that build the edges.

Push it further and it gets worse rather than better. Getting to 99% of the power needs
harmonics up to the 41st — 20.5 kHz for this 500 Hz waveform. A signal defined by its
edges is expensive in bandwidth, and no clever coding changes that; it is a property of
the waveform.
''',
                },
                {
                    "title": "A pulse train, where the standard result does not apply",
                    "minutes": 9,
                    "brief": r'''
The square wave is a special case in two ways at once: its duty cycle is exactly 50% and
its two levels are symmetric about zero. Change either and the coefficient formula changes
with it, so this one has to come from the analysis integral.

It is a short integral. The waveform is zero everywhere except across one narrow pulse, so
the integral over the period collapses to an integral over the pulse.
''',
                    "prompt": "What is the peak amplitude of the component at 3 kHz?",
                    "note": "Give the answer in volts, to three significant figures.",
                    "figure": r'''
A pulse train of 0.25 ms pulses, 4 V high, repeating every 1 ms — a duty cycle of 25%.
The pulse is centred on $t = 0$, so the waveform is even, and it rests at 0 V between
pulses.

```text
   4 V        +---+               +---+               +---+
              |   |               |   |               |   |
   0 V  ------+   +---------------+   +---------------+   +------

      one pulse spans t = -0.125 ms to +0.125 ms, the next spans
      0.875 ms to 1.125 ms, and so on for ever:
      T = 1.00 ms,   tau = 0.25 ms,   duty cycle D = tau/T = 0.25
```
''',
                    "given": [
                        {"label": "Pulse height $A$", "value": "4 V"},
                        {"label": "Period $T$", "value": "1 ms"},
                        {"label": "Pulse width $\\tau$", "value": "0.25 ms  ($D = 0.25$)"},
                        {"label": "Wanted", "value": "the amplitude of the 3 kHz component"},
                    ],
                    "aside": "The waveform is even about $t = 0$, so every $b_n$ is zero and the "
                             "amplitude at $nf_0$ is just $|a_n|$. Nothing here is odd, and nothing "
                             "here has half-wave symmetry, so the even harmonics are present too.",
                    "answer": 0.6002,
                    "tol": 0.008,
                    "unit": "V",
                    "hint": "$a_n = \\frac{2}{T}\\int_{-\\tau/2}^{+\\tau/2} A\\cos(n\\omega_0 t)\\,dt$. "
                            "Doing the integral and using $\\omega_0 T = 2\\pi$ gives "
                            "$a_n = \\frac{2A}{n\\pi}\\sin(n\\pi D)$.",
                    "wrong": "If you got 0.849, the $\\sin(n\\pi D)$ factor was dropped and only "
                             "$2A/(n\\pi)$ was used — that is the answer only where the sine happens "
                             "to be 1, which for this waveform means $n = 2$ and not $n = 3$. If you "
                             "got 1.00, that is the DC level $AD$. If you got 1.80, that is the "
                             "fundamental rather than the third harmonic.",
                    "why": r'''
```
f0 = 1 kHz, so 3 kHz is n = 3, and D = tau/T = 0.25

a_n = (2/T) INT(-tau/2 .. +tau/2) 4 cos(n w0 t) dt
    = (2 A / (n pi)) sin(n pi D)

a_3 = (2 * 4 / (3 pi)) * sin(3 pi * 0.25)
    = (8 / 9.4248) * sin(135 degrees)
    = 0.84883 * 0.70711
    = 0.600 V
```

Two checks on that. The DC term is $AD = 4 \times 0.25 = 1.00$ V, which is just the average
of a signal that sits at 4 V a quarter of the time — no integral needed, and a good way to
catch a factor-of-two slip in the rest of the working.

And the fourth harmonic is exactly zero, because $\sin(4\pi \times 0.25) = \sin\pi = 0$.
The 4 kHz harmonic fits exactly one whole cycle inside a 0.25 ms pulse, and a whole cycle
of a cosine integrates to nothing over the interval it fits into. Narrow the pulse and
those nulls move outwards; widen it to half the period and the first null lands on $n = 2$,
killing every even harmonic — which is the square wave, recovered as a special case.
''',
                },
                {
                    "title": "What a first-order filter leaves of the third harmonic",
                    "minutes": 10,
                    "brief": r'''
The hardest of the four, and the one that finally joins this module to the last one. A
periodic signal is a set of harmonics; a linear filter multiplies each harmonic
independently by $|H|$ at that harmonic's frequency; so the output's spectrum is the
input's spectrum scaled line by line.

Three separate results have to be combined: which frequency the third harmonic sits at,
how big it is at the input, and what the network does at that frequency. Take them one at
a time and none of them is hard.
''',
                    "prompt": "What is the peak amplitude of the third harmonic at the output?",
                    "note": "Give the answer in millivolts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                            {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 12000},
                            {"id": "p3", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-8},
                            {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                            {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 4], "b": [11, 4]},
                        ],
                    },
                    "check": r'''
const src = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
const A = src.value;                          /* square-wave amplitude, read off the source */
const H3 = c.gain(3000) / A;                  /* |H| at the third harmonic, 3 kHz */
return (4 * A / (3 * Math.PI)) * H3 * 1000;   /* b_3 through the filter, in millivolts */
''',
                    "given": [
                        {"label": "Source", "value": "square wave, $\\pm 5$ V, 1 kHz"},
                        {"label": "$R$", "value": "12 kΩ"},
                        {"label": "$C$", "value": "10 nF"},
                        {"label": "Wanted", "value": "the 3 kHz component at the probe, in mV"},
                    ],
                    "aside": "The generator symbol is drawn as a source of 5 V because that is the "
                             "square wave's amplitude, not because it is a sinusoid. Superposition "
                             "is what makes this legal: each harmonic can be pushed through the "
                             "filter on its own and the results added.",
                    "answer": 858.0,
                    "tol": 8.0,
                    "unit": "mV",
                    "hint": "Three steps. The third harmonic of a 1 kHz square wave is at 3 kHz with "
                            "amplitude $4A/(3\\pi)$. The corner of the filter is "
                            "$f_c = 1/(2\\pi RC)$. A first-order low-pass has "
                            "$|H| = 1/\\sqrt{1 + (f/f_c)^2}$, and the output amplitude is the input "
                            "amplitude times that.",
                    "wrong": "If you got 2122, the filter was left out — that is the third harmonic "
                             "at the input. If you got 5083, that is the *fundamental* at the output, "
                             "which is the other component in this circuit and not the one asked "
                             "for. If you got 1694, the filter was evaluated at 1 kHz rather than at "
                             "the harmonic's own frequency of 3 kHz.",
                    "why": r'''
```
step 1   the harmonic
         f0 = 1 kHz, so the third harmonic is at 3 kHz
         b_3 = 4A/(3 pi) = 4*5/(3 pi) = 2.1221 V

step 2   the filter
         fc = 1/(2 pi R C) = 1/(2 pi * 12e3 * 10e-9) = 1326.3 Hz
         |H(3 kHz)| = 1/sqrt(1 + (3000/1326.3)^2)
                    = 1/sqrt(1 + 5.1164)
                    = 1/2.4731 = 0.40434

step 3   multiply
         2.1221 V * 0.40434 = 0.8580 V = 858 mV
```

Now do the same for the fundamental and the picture becomes interesting. At 1 kHz the
filter passes $|H| = 0.79847$, so the 6.366 V fundamental arrives at 5.083 V. At the input
the third harmonic was $1/3$ of the fundamental — 33.3%. At the output it is
$0.858/5.083 = 0.169$, or 16.9%. The filter has halved the ratio.

Halved, and no better than that, from a component that is already 7.9 dB down at 3 kHz.
This is the honest limit of one pole: to knock the third harmonic down hard you have to
bring the corner down, and the fundamental is only a factor of three away, so it comes down
with it. Separating harmonics that are this close together needs a steeper skirt than a
single $R$ and $C$ can produce, which is what the second pole of module 4 is for.
''',
                },
            ],
            "tune": {
                "title": "A filter that keeps the fundamental and not the third harmonic",
                "minutes": 9,
                "brief": r'''
A 1 kHz square wave arrives where a 1 kHz sine wave was wanted. Its fundamental is the
signal; its third harmonic, at 3 kHz and a third the size, is the largest thing standing
in the way. One corner frequency has to serve both requirements.

They pull in opposite directions, and this time they pull hard, because the two
frequencies are only a factor of three apart. Push the corner down to kill the harmonic
and the fundamental starts coming down with it; lift it to protect the fundamental and the
harmonic walks straight through. Work out both bounds on paper before touching a slider:

  * keeping at least 85% of the amplitude at 1 kHz puts a **lower** bound on $f_c$;
  * putting 3 kHz at least 5 dB down puts an **upper** one.

The window between them is real but narrow. Finding out how narrow is most of the point of
the exercise.
''',
                "prompt": "Keep at least 85% of the 1 kHz fundamental, and put the 3 kHz third harmonic at least 5 dB down.",
                "note": "One corner frequency, two requirements, and only a factor of three between them.",
                "model": "rc-lowpass",
                "initial": {"r": 10000, "c": 100},
                "constants": {"fsig": 1000, "fnoise": 3000},
                "constraints": [
                    {"k": "keep", "label": "≥ 0.85 of the fundamental kept at 1 kHz", "min": 0.85},
                    {"k": "reject", "label": "≤ −5 dB at the third harmonic, 3 kHz", "max": -5.0},
                ],
            },
            "derive": {
                "title": "Where the power in a square wave actually sits",
                "minutes": 13,
                "vars": ["A", "n", "P", "b"],
                "brief": r'''
The square wave's coefficients are known: $b_n = 4A/(n\pi)$ for odd $n$, nothing for even.
Parseval turns that list into a budget — how much of the signal each harmonic is actually
carrying — and the budget explains why a square wave survives a narrow channel as a
recognisable waveform but not as a clean one.

Then the same equation read backwards does something unexpected. Parseval is an equality,
and both of its sides are known independently here, so it pins down the value of an
infinite sum that has nothing to do with electronics.

Nothing below needs an integral. It is the coefficient formula, the definition of mean
square, and algebra.
''',
                "steps": [
                    {
                        "prompt": "A sinusoid of peak amplitude $b$ has mean square $b^2/2$. Using $b_n = 4A/(n\\pi)$, write the power $P_n$ carried by the $n$th harmonic (for odd $n$) in terms of $A$ and $n$.",
                        "given": "$P_n = b_n^2/2$, and $b_n = \\dfrac{4A}{n\\pi}$.",
                        "answer": "\\frac{8A^{2}}{n^{2}\\pi^{2}}",
                        "hint": "Square $4A/(n\\pi)$ first — that gives $16A^2/(n^2\\pi^2)$ — and then halve it.",
                        "deconstruct": [
                            "$b_n^2 = (4A)^2/(n\\pi)^2 = 16A^2/(n^2\\pi^2)$.",
                            "Halving turns the 16 into an 8, and nothing else changes.",
                        ],
                    },
                    {
                        "prompt": "Now the signal itself, with no series involved. The square wave sits at $+A$ or $-A$ at every instant, so $x^2(t)$ is the same number the whole time. Write the mean square of $x$ in terms of $A$.",
                        "given": "The mean of a quantity that never changes is that quantity.",
                        "answer": "A^{2}",
                        "hint": "Square $+A$ and square $-A$. Both give the same thing, so the average over a period is that thing.",
                        "deconstruct": [
                            "$x(t)$ is $+A$ for half the period and $-A$ for the other half.",
                            "$x^2(t) = A^2$ throughout, so its mean is $A^2$ — this is also why the RMS value of a square wave is $A$ rather than $A/\\sqrt{2}$.",
                        ],
                    },
                    {
                        "prompt": "Parseval says those two agree: the harmonic powers add up to the mean square of the signal. Write the fraction of the total power carried by the fundamental alone, $P_1$ divided by the total.",
                        "given": "$P_1$ is the first result at $n = 1$; the total is the second result.",
                        "answer": "\\frac{8}{\\pi^{2}}",
                        "hint": "Divide $8A^2/\\pi^2$ by $A^2$. The amplitude cancels, which is why this fraction is the same for every square wave.",
                        "deconstruct": [
                            "At $n = 1$, $P_1 = 8A^2/\\pi^2$.",
                            "Dividing by the total $A^2$ leaves $8/\\pi^2$, a pure number — about 0.8106.",
                        ],
                    },
                    {
                        "prompt": "The fractions must add to 1 over all the odd harmonics: $\\sum_{n\\,\\mathrm{odd}} 8/(n^2\\pi^2) = 1$. Write the value that forces on the sum $\\sum_{n\\,\\mathrm{odd}} 1/n^2$, that is $1 + \\tfrac{1}{9} + \\tfrac{1}{25} + \\dots$",
                        "given": "The factor $8/\\pi^2$ does not depend on $n$, so it comes outside the sum.",
                        "answer": "\\frac{\\pi^{2}}{8}",
                        "hint": "If (a constant) times (the sum) equals 1, the sum is the reciprocal of the constant.",
                        "deconstruct": [
                            "$\\dfrac{8}{\\pi^2}\\sum_{n\\,\\mathrm{odd}}\\dfrac{1}{n^2} = 1$.",
                            "Multiply both sides by $\\pi^2/8$.",
                        ],
                    },
                    {
                        "prompt": "Back to something measurable. Write the RMS value of the fundamental alone, in terms of $A$.",
                        "given": "The fundamental is a sinusoid of peak amplitude $4A/\\pi$, and a sinusoid's RMS value is its peak divided by $\\sqrt{2}$.",
                        "answer": "\\frac{2\\sqrt{2}A}{\\pi}",
                        "hint": "$\\dfrac{4A}{\\pi\\sqrt{2}}$ is correct but untidy; multiply top and bottom by $\\sqrt{2}$ to clear the root out of the denominator.",
                        "deconstruct": [
                            "Peak is $4A/\\pi$, so the RMS is $4A/(\\pi\\sqrt{2})$.",
                            "$4/\\sqrt{2} = 2\\sqrt{2}$, giving $2\\sqrt{2}A/\\pi \\approx 0.900A$.",
                        ],
                    },
                ],
                "closing": r'''
Put numbers on it. The fundamental carries $8/\pi^2 = 0.8106$ of the power — 81.06% of it.
The third adds $8/(9\pi^2) = 0.0901$, taking the running total to 90.06%; the fifth adds
3.24% for 93.31%. Ninety-three percent of the power of a square wave sits in three
sinusoids. Getting to 99% takes every harmonic out to the 41st.

The last step is the same statement in a form a meter can check. The fundamental's RMS is
$0.900A$ against the whole waveform's $A$, and $0.900^2 = 0.8106$ — the same 81% arrived at
from the other direction, which is a good sign the algebra held.

The sum in the fourth step is worth a second look, because nothing about it is electrical.
$\sum_{n\,\mathrm{odd}} 1/n^2 = \pi^2/8 = 1.2337$, deduced from the mean square of a
voltage waveform. It agrees with Euler's $\sum_{\mathrm{all}\,n} 1/n^2 = \pi^2/6$: the even
terms are $\sum 1/(2k)^2 = \tfrac14 \cdot \pi^2/6 = \pi^2/24$, and
$\pi^2/6 - \pi^2/24 = \pi^2/8$. Parseval is an equality, and an equality can always be read
in whichever direction is more useful.
''',
            },
            "lab": {
                "title": "Building a square wave out of sines",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
The square wave, from its coefficients to its spectrum to the Gibbs overshoot. NumPy is
imported for you; work with arrays rather than loops where you can.

The signal is a square wave of amplitude 1, odd about $t = 0$, with a fundamental of
1 Hz. Its coefficients are $b_n = 4/(n\pi)$ for odd $n$ and zero for even $n$.

- `square_coeffs(N)` returns a NumPy array of the first `N` coefficients,
  $b_1$ through $b_N$, including the zeros at the even harmonics.
- `synthesise(coeffs, t)` returns $\sum_n b_n \sin(2\pi n t)$ evaluated at every time in
  the array `t`, where `coeffs[0]` is $b_1$. The fundamental is 1 Hz, so harmonic $n$ is
  at $n$ Hz.
- `mean_square(coeffs)` returns the mean square value of that sum, which by Parseval is
  $\sum_n b_n^2/2$. For the exact square wave of amplitude 1 the answer is 1, and your
  partial sums should climb towards it.

Keeping the even coefficients as explicit zeros costs nothing and keeps the index
arithmetic honest: `coeffs[n - 1]` is always $b_n$.
''',
                "files": [{"name": "main.py", "content": r'''
"""The Fourier series of a square wave, term by term."""

import numpy as np


def square_coeffs(N):
    """First N sine coefficients of a unit-amplitude square wave, b_1 .. b_N."""
    # TODO: b_n = 4 / (n * pi) for odd n, and 0 for even n.
    #       np.arange(1, N + 1) and np.where make this one expression.
    return np.zeros(N)


def synthesise(coeffs, t):
    """Sum of b_n sin(2 pi n t) over the given coefficients, evaluated at t."""
    # TODO: accumulate one harmonic at a time; coeffs[i] is b_(i+1).
    return np.zeros_like(np.asarray(t, dtype=float))


def mean_square(coeffs):
    """Mean square value of that sum, by Parseval: the sum of b_n^2 / 2."""
    # TODO: one sum, then a division by two. Return a float.
    return 0.0


if __name__ == "__main__":
    b = square_coeffs(9)
    print("b_1 .. b_9:", np.round(b, 6))
    t = np.linspace(0.0, 1.0, 9)
    print("nine harmonics over one period:", np.round(synthesise(b, t), 4))
    print("mean square with 9 harmonics:", mean_square(b))
    print("mean square with 99:", mean_square(square_coeffs(99)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The Fourier series of a square wave, term by term.

Numbers checked by running this file: b_1 = 1.2732395447351628 = 4/pi, the mean
square with 99 harmonics is 0.9959472877303109, and the partial sum with 99
harmonics peaks at 1.1790130793104294 near the jump — the Gibbs overshoot, about
9% of the jump height of 2.
"""

import numpy as np


def square_coeffs(N):
    """First N sine coefficients of a unit-amplitude square wave, b_1 .. b_N."""
    n = np.arange(1, N + 1)
    return np.where(n % 2 == 1, 4.0 / (n * np.pi), 0.0)


def synthesise(coeffs, t):
    """Sum of b_n sin(2 pi n t) over the given coefficients, evaluated at t."""
    t = np.asarray(t, dtype=float)
    out = np.zeros_like(t)
    for i, b in enumerate(coeffs):
        out = out + b * np.sin(2.0 * np.pi * (i + 1) * t)
    return out


def mean_square(coeffs):
    """Mean square value of that sum, by Parseval: the sum of b_n^2 / 2."""
    c = np.asarray(coeffs, dtype=float)
    return float(np.sum(c * c) / 2.0)


if __name__ == "__main__":
    b = square_coeffs(9)
    print("b_1 .. b_9:", np.round(b, 6))
    t = np.linspace(0.0, 1.0, 9)
    print("nine harmonics over one period:", np.round(synthesise(b, t), 4))
    print("mean square with 9 harmonics:", mean_square(b))
    print("mean square with 99:", mean_square(square_coeffs(99)))
'''}],
                "hints": [
                    "`np.arange(1, N + 1)` gives the harmonic numbers. `np.where(n % 2 == 1, 4.0 / (n * np.pi), 0.0)` then selects between the odd-harmonic value and zero without a loop.",
                    "In `synthesise`, `enumerate(coeffs)` gives `i` starting at 0, so the harmonic number is `i + 1`. Build the answer by adding one array to another; do not assign into `t`.",
                    "`mean_square` is `float(np.sum(c * c) / 2.0)`. If it comes out near 0.5 rather than near 1, the division by two has been applied twice.",
                    "To see Gibbs, evaluate `synthesise(square_coeffs(99), np.linspace(0, 0.5, 4001))` and take the maximum. It is close to 1.179, and it does not fall when you use more harmonics.",
                ],
                "tests": [
                    {"name": "the first five coefficients", "code": r'''
import numpy as np
b = square_coeffs(5)
assert len(b) == 5, f"asked for 5 coefficients, got {len(b)}"
want = [1.2732395447351628, 0.0, 0.4244131815783876, 0.0, 0.25464790894703254]
for k, (got, exp) in enumerate(zip(np.asarray(b, dtype=float), want), start=1):
    assert abs(got - exp) < 1e-12, f"b_{k} should be {exp}, got {got}"
'''},
                    {"name": "odd harmonics only, all the way up", "code": r'''
import numpy as np
b = np.asarray(square_coeffs(20), dtype=float)
for n in range(1, 21):
    if n % 2 == 0:
        assert abs(b[n - 1]) < 1e-15, f"b_{n} must be zero for an even harmonic, got {b[n - 1]}"
    else:
        assert abs(b[n - 1] - 4.0 / (n * np.pi)) < 1e-12, \
            f"b_{n} should be 4/({n}*pi), got {b[n - 1]}"
'''},
                    {"name": "one, three and five harmonics at the quarter period", "code": r'''
import numpy as np
t = np.array([0.25])
assert abs(float(synthesise(square_coeffs(1), t)[0]) - 1.2732395447351628) < 1e-9, \
    "one harmonic at t = 0.25 is just 4/pi"
assert abs(float(synthesise(square_coeffs(3), t)[0]) - 0.8488263631567752) < 1e-9, \
    "three harmonics give 4/pi (1 - 1/3)"
assert abs(float(synthesise(square_coeffs(5), t)[0]) - 1.1034742721038078) < 1e-9, \
    "five harmonics give 4/pi (1 - 1/3 + 1/5)"
'''},
                    {"name": "the Gibbs overshoot is there and does not go away", "code": r'''
import numpy as np
t = np.linspace(0.0, 0.5, 4001)
peak_99 = float(np.max(synthesise(square_coeffs(99), t)))
assert abs(peak_99 - 1.1790130793104294) < 1e-6, \
    f"99 harmonics should peak at about 1.17901, got {peak_99}"
peak_21 = float(np.max(synthesise(square_coeffs(21), t)))
assert peak_21 > 1.17, f"21 harmonics already overshoot to about 1.18, got {peak_21}"
assert abs(peak_99 - peak_21) < 0.01, \
    f"the overshoot must not shrink with more harmonics: {peak_21} then {peak_99}"
'''},
                    {"name": "Parseval: the power climbs towards 1", "code": r'''
p1 = mean_square(square_coeffs(1))
p9 = mean_square(square_coeffs(9))
p99 = mean_square(square_coeffs(99))
assert abs(p1 - 0.8105694691387023) < 1e-12, \
    f"the fundamental alone carries 8/pi^2 = 0.81057 of the power, got {p1}"
assert p1 < p9 < p99 < 1.0, f"partial sums must climb towards 1: {p1}, {p9}, {p99}"
assert abs(p99 - 0.9959472877303109) < 1e-12, \
    f"99 harmonics account for 0.99595 of the power, got {p99}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "The Fourier transform, sampling and Nyquist",
            "summary": "Let the period go to infinity and the lines become a continuum; then take samples, and the continuum starts repeating.",
            "concepts": [
                "Take a periodic signal and stretch its period. The harmonics at $n f_0$ crowd closer together as $f_0 = 1/T$ shrinks, and in the limit $T \\to \\infty$ — an aperiodic signal — the lines merge into a continuous function of frequency.",
                "That function is the **Fourier transform**: $X(f) = \\int_{-\\infty}^{\\infty} x(t)e^{-j2\\pi f t}\\,dt$, with the inverse $x(t) = \\int_{-\\infty}^{\\infty} X(f)e^{j2\\pi f t}\\,df$.",
                "$X(f)$ is complex: $|X(f)|$ is the magnitude spectrum and $\\angle X(f)$ the phase spectrum. For a real signal $X(-f) = X(f)^{*}$, so the magnitude is symmetric about zero and only positive frequencies are ever plotted.",
                "Compressing a signal in time stretches its spectrum in frequency, and vice versa: $x(at)$ transforms to $\\frac{1}{|a|}X(f/a)$. A short pulse is a wide spectrum; there is no such thing as a fast signal in a narrow band.",
                "The standard pair to memorise: a rectangular pulse of width $\\tau$ has transform $\\tau\\,\\mathrm{sinc}(f\\tau)$, whose first null sits at $f = 1/\\tau$. Halve the pulse width and the spectrum doubles in width.",
                "**Sampling** every $T_s$ seconds is, mathematically, multiplication by a train of impulses. That train has a spectrum which is itself a train of impulses spaced $f_s = 1/T_s$ apart, and multiplying in time convolves in frequency — so the signal's spectrum is **copied to every multiple of $f_s$**.",
                "If the signal contains anything above $f_s/2$, neighbouring copies overlap. The overlap is **aliasing**, and it is a permanent loss: after the samples exist there is no operation, analogue or digital, that can separate the two contributions.",
                "**Nyquist**: to represent a signal band-limited to $B$ you need $f_s > 2B$, strictly. At exactly $f_s = 2B$ the samples of a sinusoid at $B$ can all land on the zero crossings and record nothing at all.",
                "Where does a component land? A tone at $f$ appears in the sampled data at $f_a$, obtained by reducing $f$ modulo $f_s$ and then folding anything above $f_s/2$ back down: $f_a = f_s - (f \\bmod f_s)$ when that remainder exceeds $f_s/2$.",
                "The **anti-alias filter** therefore has to be analogue and has to come before the converter. Choosing it is a trade: a low corner protects the stopband but eats into the top of the wanted band, and a first-order filter usually cannot do both at once.",
                "Coming back out, the ideal reconstruction is a sum of sinc functions, one per sample. A real DAC holds each sample for $T_s$ instead, which multiplies the reconstructed spectrum by a $\\mathrm{sinc}(f/f_s)$ droop — about 3.9 dB down at the band edge if the band runs to $f_s/2$.",
            ],
            "read": [
                {
                    "title": "When the signal stops repeating, the lines become a curve",
                    "minutes": 12,
                    "body": r'''
Set a pulse generator to put out a 1 V pulse, 1 ms wide, once every 10 ms, and hang a
spectrum analyser on the output. What comes up on the screen is a picket fence. There is
a line at 100 Hz, another at 200 Hz, another at 300 Hz, and so on for as far as the
analyser will look — every multiple of $f_0 = 1/T = 100$ Hz, and nothing in between. The
heights of the lines are not equal: they rise and fall under a smooth curve which touches
zero at 1 kHz, again at 2 kHz, and at every kilohertz after that.

Everything so far is the previous module. A periodic signal has a **line spectrum**,
the lines sit at multiples of the repetition rate, and their heights are the Fourier
coefficients.

Now change one thing. Leave the pulse exactly as it is — same 1 V, same 1 ms — and slow
the repetition down, so the same pulse comes once every 100 ms instead of once every
10 ms. The fence gets ten times finer: lines every 10 Hz now, ten times as many of them.
Each line is a tenth as tall as it was. And the smooth curve they sit under has not moved
at all: still zero at 1 kHz, 2 kHz, 3 kHz.

That is the whole of this reading in one observation. Stretch the period and the lines
crowd together; the shape they trace out stays put. Push the period all the way to
infinity — which is to say, send the pulse **once** and never again — and the lines merge
into a continuous curve. An aperiodic signal does not have a line spectrum. It has a
spectrum at every frequency.

## The one thing that has to be fixed first

The lines shrink as they crowd, and if we take the limit carelessly everything goes to
zero and we learn nothing. The shrinking is not physics; it is bookkeeping. For the pulse
train above, the Fourier coefficient at DC is

$$c_0 = \frac{1}{T}\int_{-\tau/2}^{\tau/2} A\,dt = \frac{A\tau}{T}$$

the *duty cycle* times the height. Spread the same pulse over ten times the period and
each coefficient falls by ten, because a coefficient is an average over the period and
most of the period is now empty. Nothing about the pulse changed. The average changed,
because we averaged over more nothing.

So multiply it back out. Look at $T c_n$ rather than $c_n$:

```
T = 10 ms    c_0 = 1 V x 1 ms / 10 ms  = 0.1 V     T c_0 = 1e-3 V.s
T = 100 ms   c_0 = 1 V x 1 ms / 100 ms = 0.01 V    T c_0 = 1e-3 V.s
T = 1 s      c_0 = 1 V x 1 ms / 1 s    = 0.001 V   T c_0 = 1e-3 V.s
```

$T c_n$ does not move. It is the quantity with a limit, and that limit is the Fourier
transform.

## Taking the limit

The analysis equation for the series is

$$c_n = \frac{1}{T}\int_{-T/2}^{T/2} x(t)\,e^{-j2\pi n f_0 t}\,dt$$

Multiply both sides by $T$ and give the result a name, $X(nf_0) = T c_n$:

$$X(nf_0) = \int_{-T/2}^{T/2} x(t)\,e^{-j2\pi n f_0 t}\,dt$$

Now let $T \to \infty$. Three things happen at once. The limits of the integral run off to
$\pm\infty$. The spacing $f_0 = 1/T$ between neighbouring lines shrinks to nothing, so the
discrete index $nf_0$ becomes a continuous variable $f$. And the samples $X(nf_0)$, which
were the heights of a picket fence, become the values of a function defined for every $f$:

$$X(f) = \int_{-\infty}^{\infty} x(t)\,e^{-j2\pi f t}\,dt$$

The synthesis equation goes the same way. $x(t) = \sum_n c_n e^{j2\pi n f_0 t}$ becomes
$\sum_n X(nf_0)e^{j2\pi n f_0 t} f_0$ once $c_n$ is written as $X(nf_0)/T = X(nf_0)f_0$,
and a sum of values times a spacing, with the spacing going to zero, is an integral:

$$x(t) = \int_{-\infty}^{\infty} X(f)\,e^{j2\pi f t}\,df$$

Those two lines are the Fourier transform and its inverse. Nothing was assumed that the
series did not already assume; a period was stretched until it stopped being a period.

**The units moved, and it matters.** A Fourier coefficient $c_n$ is in volts: it is the
size of an actual sinusoid you could measure. $X(f)$ is in volts *per hertz* — volt-seconds
— because it came from a coefficient multiplied by a period. It is a **density**, and the
right question to ask of it is never "how many volts are there at 1 kHz" but "how many
volts are there between 999 Hz and 1001 Hz". For an aperiodic signal the answer to the
first question is always zero, because a single frequency is a band of zero width. That is
why an instrument quotes noise in $\mathrm{V}/\sqrt{\mathrm{Hz}}$, and why the vertical
axis of an FFT changes when you change the analysis bandwidth.

## Worked example: one rectangular pulse

Take the pulse on its own — height $A$, width $\tau$, centred on $t = 0$, and zero
everywhere else — and put it through the integral. Outside $\pm\tau/2$ the integrand is
zero, so the infinite limits collapse to finite ones:

```
X(f) = INT[-tau/2 .. tau/2]  A exp(-j2 pi f t) dt

     = A [ exp(-j2 pi f t) / (-j2 pi f) ]  from -tau/2 to +tau/2

     = A ( exp(+j pi f tau) - exp(-j pi f tau) ) / (j 2 pi f)

     = A ( 2j sin(pi f tau) ) / (j 2 pi f)          Euler

     = A sin(pi f tau) / (pi f)

     = A tau . sin(pi f tau) / (pi f tau)   =   A tau sinc(f tau)
```

where $\mathrm{sinc}(x) \equiv \sin(\pi x)/(\pi x)$. Put $A = 1$ V and $\tau = 1$ ms in it
and read off four values:

```
f = 0        sinc(0)   = 1        X = 1.000 ms.V  = 1000 uV/Hz
f = 500 Hz   sinc(0.5) = 0.6366   X = 0.6366 ms.V =  637 uV/Hz
f = 1 kHz    sinc(1)   = 0        X = 0            (the first null)
f = 1.5 kHz  sinc(1.5) = -0.2122  X = -0.2122 ms.V = -212 uV/Hz
```

Four things are worth taking from that column of numbers.

**$X(0)$ is the area under the signal.** Put $f = 0$ in the analysis equation and the
exponential becomes 1, leaving $\int x(t)\,dt$. Here that is $1\ \mathrm{V} \times
1\ \mathrm{ms} = 1$ mV/Hz, which is exactly what came out. It is the cheapest sanity check
there is on any transform you compute.

**The first null is at $1/\tau$.** $\sin(\pi f \tau)$ vanishes when $f\tau$ is a whole
number, so the nulls are at $1/\tau, 2/\tau, 3/\tau, \dots$ — 1 kHz, 2 kHz, 3 kHz for a
1 ms pulse. About 90% of the pulse's energy sits inside that first lobe, and the
remaining tenth is spread across the sidelobes.

**The value is negative between the first and second nulls**, and a negative $X$ is not a
negative amplitude — there is no such thing. It is a phase of $180^\circ$. $X(f)$ is
complex in general; here the pulse is even — symmetric about $t = 0$ — which is exactly
the condition for $X$ to come out purely real, so all the phase information has collapsed
into a sign.

**The sidelobes are not small.** At $f = 1.5/\tau$ the response is $0.2122$ of the peak,
which is $20\log_{10}(0.2122) = -13.5$ dB. The true first-sidelobe peak sits a little
lower in frequency, at $f\tau \approx 1.43$, and is 13.3 dB down. A rectangular pulse — or
a rectangular *window*, which is the same shape doing a different job — never gets you
more than about 13 dB away from the thing you were trying to leave behind. Module 9 spends
most of its time on that number.

## Worked example: a decaying exponential

The other shape you meet constantly is what a capacitor does when you stop charging it.
Let $x(t) = e^{-t/T_0}$ for $t \ge 0$ and zero before, with $T_0 = 1$ ms. The integral runs
from 0 rather than from $-\infty$:

```
X(f) = INT[0 .. inf]  exp(-t/T0) exp(-j2 pi f t) dt

     = INT[0 .. inf]  exp( -(1/T0 + j2 pi f) t ) dt

     = 1 / (1/T0 + j 2 pi f)                    the exponential dies at the top limit

     = T0 / (1 + j 2 pi f T0)
```

so $|X(f)| = T_0/\sqrt{1 + (2\pi f T_0)^2}$. Write $f_c = 1/(2\pi T_0) = 159.2$ Hz and it
becomes $T_0/\sqrt{1 + (f/f_c)^2}$, which should look extremely familiar:

```
f = 0        |X| = 1.000 ms.V              = 1000 uV/Hz
f = 159 Hz   |X| = 1 ms / sqrt(2)          =  707 uV/Hz     (-3 dB)
f = 1592 Hz  |X| = 1 ms / sqrt(1 + 100)    =   99.5 uV/Hz   (-20 dB)
```

That is the first-order low-pass roll-off, arrived at without a single impedance. It is not
a coincidence: the decaying exponential *is* the impulse response of an RC low-pass, and
module 4 will show that the transform of a system's impulse response is its frequency
response. The $-20$ dB per decade you learned to draw in the first year and the $1/f$ tail
of this integral are the same fact seen from two ends.

Compare the two examples for a moment. The exponential's spectrum falls off as $1/f$ for
ever, with no nulls; the pulse's falls off as $1/f$ too, but with nulls punched through it.
Both decay slowly, and both signals have a **discontinuity** — the pulse at its edges, the
exponential at $t = 0$. That is the general rule from the previous module in its aperiodic
form: how fast a spectrum dies is set by how smooth the waveform is, and a jump anywhere
buys you a $1/f$ tail everywhere.

## The mistake, and why it is tempting

Two conventions for $\mathrm{sinc}$ are in circulation. Signal processing writes
$\mathrm{sinc}(x) = \sin(\pi x)/(\pi x)$, which is what NumPy's `np.sinc` computes and what
this course uses; mathematics and most calculators write $\mathrm{sinc}(x) = \sin(x)/x$.
They differ by a factor of $\pi$ *inside* the function, which is the worst place for a
discrepancy to hide: both versions look right, both are smooth, both peak at 1. The visible
symptom is that the first null moves from $f = 1/\tau$ to $f = \pi/\tau$ — a factor of $\pi$
in a bandwidth, which is enough to specify the wrong filter and not enough to look obviously
insane. When you meet a sinc in a data sheet or a library call, find out where its first
null is before you believe anything else about it.

The other one is subtler and worth guarding against for the rest of the course: reading
$|X(f)|$ as an amplitude. It is not. It is an amplitude *density*, and the number attached
to it depends on the units of the time axis. Transform the same pulse with $t$ in
milliseconds instead of seconds and $X(0)$ comes out as 1 rather than 0.001. Nothing is
wrong; the density is now per kilohertz.

## Where this stops holding

The integral $\int |x(t)|\,dt$ has to converge for the derivation above to mean anything,
and for a great many of the signals we actually care about it does not. A constant. A step.
A pure sinusoid running from the beginning of time to the end of it. Each has infinite
area, and the analysis integral does not converge in the ordinary sense.

The engineering fix is to allow **impulses** in the frequency domain. A constant $A$ has
transform $A\delta(f)$; a cosine at $f_1$ has transform $\tfrac12\delta(f - f_1) +
\tfrac12\delta(f + f_1)$; a line spectrum is recovered as a comb of impulses, so the
Fourier series turns out to be a special case of the transform rather than a rival to it.
These are not functions, and treating them as if they were will eventually produce
nonsense. They are distributions, defined by what they do inside an integral, and the
rule that always holds is $\int \delta(f - f_1)G(f)\,df = G(f_1)$. Every manipulation in
the next reading is that rule applied to a comb.

There is one more limit, and it is the reason the next reading exists. A signal cannot be
both **time-limited** and **band-limited**. If $x(t)$ is exactly zero outside some
interval, $X(f)$ is non-zero out to arbitrarily high frequencies — the pulse above has
sidelobes for ever, and no amount of shaping removes them entirely. The converse holds
too: a strictly band-limited signal goes on for all time in both directions. Every real
measurement is time-limited, because it started and it will stop. So no real signal is
ever perfectly band-limited, the perfect anti-alias filter does not exist, and everything
in the next reading is a negotiation about how much of an unavoidable overlap you are
prepared to tolerate.
''',
                },
                {
                    "title": "Sampling: the copies, the fold, and the filter that has to come first",
                    "minutes": 13,
                    "body": r'''
An analogue-to-digital converter is a stroboscope. Every $T_s$ seconds it looks at the
input, records what it sees as a number, and closes its eye until the next tick. Between
one look and the next it has no idea what happened, and neither will anything downstream.
The samples are the whole of what survives.

That is the entire difficulty, and it is worth stating as a question rather than a formula:
given the list of numbers, **which input signals could have produced it?** If the answer is
"exactly one", nothing has been lost and the digital copy is as good as the original. If the
answer is "many", the converter has thrown away the information that told them apart, and no
processing afterwards can recover it, because the information is not there to recover.

The everyday example is a wagon wheel in a film. Twenty-four frames a second, a wheel with
twelve spokes, and the wheel turning at exactly two revolutions per second: every frame
catches a spoke in the same place, so on screen the wheel stands still. Turn slightly
slower and it crawls backwards. Nothing is wrong with the camera. The frames are simply
consistent with more than one wheel speed, and your eye picks the slowest one.

## Which sinusoids share a set of samples

The wheel argument can be done exactly, in two lines of trigonometry, and it is worth doing
because it needs no distributions and no diagrams. Sample a cosine of frequency $f$ at the
instants $t = nT_s$:

$$x[n] = \cos(2\pi f n T_s)$$

Now take a second cosine, at $f + k f_s$ for any whole number $k$, and sample it at exactly
the same instants. Since $f_s T_s = 1$:

$$\cos\big(2\pi (f + kf_s) nT_s\big) = \cos(2\pi f nT_s + 2\pi kn) = \cos(2\pi f nT_s)$$

because adding a whole number of turns to an angle changes nothing. **The two signals
produce identical samples**, every one of them, for ever. There is no cleverness that can
separate them afterwards.

The same trick catches a second family. Take $f_s - f$:

$$\cos\big(2\pi (f_s - f)nT_s\big) = \cos(2\pi n - 2\pi f nT_s) = \cos(2\pi f nT_s)$$

again identical. For a sine the same manipulation gives $-\sin(2\pi f nT_s)$: the same
frequency with its phase turned upside down, which is exactly the inversion the sandbox in
this module draws and warns you not to read as a sign error.

So the frequencies that share a set of samples with $f$ are $f + kf_s$ — the *wrapping*
family — and $kf_s - f$ — the *folding* family. Every one of them is an **alias** of $f$.

## The same thing, in numbers

Sample at $f_s = 8$ Sa/s and compare a 5 Hz cosine with a 3 Hz cosine. Note that
$3 = 8 - 5$, so these two are a folding pair:

```
n                    0       1       2       3       4       5       6       7       8
t = n/8  (s)     0.000   0.125   0.250   0.375   0.500   0.625   0.750   0.875   1.000

cos(2 pi 5 t)    1.000  -0.707   0.000   0.707  -1.000   0.707   0.000  -0.707   1.000
cos(2 pi 3 t)    1.000  -0.707   0.000   0.707  -1.000   0.707   0.000  -0.707   1.000
```

Not approximately equal. Equal, to every digit the arithmetic will produce. Handed that
row of numbers and told the sample rate, you cannot say which cosine was at the input, and
neither can any algorithm. By convention the sampled data is read as the alias that lands
between 0 and $f_s/2$, so a 5 Hz tone sampled at 8 Sa/s is reported as 3 Hz — permanently,
and with no warning attached.

## Why the spectrum repeats

The sample-by-sample argument tells you what happens to one sinusoid. The spectral picture
tells you what happens to everything at once, and it is the version worth carrying around.

Model the sampler as a multiplication by an impulse train, $p(t) = \sum_n \delta(t - nT_s)$,
so the sampled signal is $x_s(t) = x(t)p(t)$. The transform of the train is another train:

$$\sum_n \delta(t - nT_s) \;\longleftrightarrow\; \frac{1}{T_s}\sum_k \delta(f - kf_s)$$

Dense in time, sparse in frequency — the tighter you space the samples, the further apart
the spectral impulses sit. And multiplication in one domain is convolution in the other, so

$$X_s(f) = X(f) * \frac{1}{T_s}\sum_k \delta(f - kf_s)
        = \frac{1}{T_s}\sum_k X(f - kf_s)$$

Convolving anything with an impulse at $kf_s$ moves a copy of it there. So the spectrum of
the sampled signal is the spectrum of the original, **copied to every multiple of the
sample rate**, all of them scaled by $1/T_s$.

Now the condition writes itself. The copy centred at 0 occupies $-B$ to $+B$. The copy
centred at $f_s$ occupies $f_s - B$ to $f_s + B$. They stay clear of each other if
$f_s - B > B$, that is

$$f_s > 2B$$

Below that the copies overlap, and where they overlap the sampled data holds the sum of two
contributions that were at different frequencies before sampling and are at the same
frequency after it. That is **aliasing**, stated as a picture rather than as a trigonometric
accident.

## Why the inequality is strict

$f_s > 2B$, not $f_s \ge 2B$. The boundary case is not a technicality. Sample
$x(t) = \sin(2\pi \cdot 1000\,t)$ — a 1 kHz tone, $B = 1$ kHz — at exactly 2 kSa/s, so
$t = n/2000$:

```
x[n] = sin(2 pi 1000 n / 2000) = sin(pi n) = 0    for every n
```

Every sample is zero. The recorded data is silence, and the tone was full amplitude. Shift
the tone's phase by $90^\circ$ and every sample sits on a peak instead, alternating $+1, -1$.
Same frequency, same sample rate, wildly different data: at exactly $f_s = 2B$ the amplitude
that comes back depends on the phase, which means it is not determined. One tick above and
the ambiguity is gone.

## Worked example: choosing a rate and a filter together

The two decisions cannot be made separately, and this is the example that shows why.

Audio to be kept out to 20 kHz. The Nyquist rate is 40 kSa/s; CD sampling uses 44.1 kSa/s,
so $f_s/2 = 22.05$ kHz. Everything arriving at the converter above 22.05 kHz folds into the
band, so the analogue filter in front of it has to pass 20 kHz and stop 22.05 kHz. Call for
80 dB of rejection — a fair number if you want the folded rubbish below the noise floor of a
16-bit converter — and ask what filter does that.

```
transition band   20 kHz -> 22.05 kHz
ratio             22.05 / 20 = 1.1025          about 0.14 of an octave

one pole at 20 kHz, evaluated at 22.05 kHz:
   |H| = 1 / sqrt(1 + 1.1025^2) = 1/1.4884 = 0.672      ->  3.5 dB down

each further pole multiplies by another 1/1.1025 out here:
   dB per pole  = 20 log10(1.1025) = 0.85 dB
   poles needed = 80 / 0.85         = about 94
```

Ninety-four poles. Nobody builds that, and the ones who tried in the 1970s got filters
whose phase response ruined what their amplitude response protected.

The way out is to move the problem. Sample at four times the rate — 176.4 kSa/s — so
$f_s/2 = 88.2$ kHz, and the analogue filter now only has to get from 20 kHz to 88.2 kHz:

```
ratio        88.2 / 20 = 4.41                about 2.1 octaves
three poles at 20 kHz, evaluated at 88.2 kHz:
   |H| = 1 / sqrt(1 + 4.41^6) = 1 / 85.8    ->  38.7 dB down
```

Better, from a filter anyone can build out of one op-amp and six passives. The rest of the
rejection is done *after* the converter, in the digital domain, where a filter with a
transition band of a few hundred hertz costs arithmetic rather than components — and then
the sample rate is divided back down to 44.1 kSa/s. That is what "oversampling" on a
converter data sheet means, and this arithmetic is the whole reason it exists.

## The mistake people actually make

"Sample at twice the highest frequency you are interested in." It is repeated everywhere,
it sounds like the theorem, and it is wrong in a way that costs boards.

The theorem is about the highest frequency **present at the converter's input**, and the
input does not know what you are interested in. A 2 kHz sensor signal sampled at 20 kSa/s
is comfortably above the Nyquist rate for the sensor and completely unprotected against the
39 kHz ripple from the switching regulator two inches away: $39 \bmod 20 = 19$ kHz, which is
above $f_s/2 = 10$ kHz, so it folds to $20 - 19 = 1$ kHz and lands in the middle of the
wanted band. The measurement now has a 1 kHz component that no filter can remove, because
genuine 1 kHz signal and folded 39 kHz interference are the same numbers.

The reason the mistake is so tempting is that every other error in a signal chain is
recoverable. Gain that is wrong can be scaled. An offset can be subtracted. Noise can be
averaged down. Filtering done in the wrong place can usually be redone in the right one.
Aliasing is the one failure that destroys information rather than corrupting it, and the
anti-alias filter is the one component in the chain that has to be analogue, has to be
before the converter, and cannot be fixed in software afterwards.

## Where the rule stops holding

**Bandpass signals.** "Sample above twice the highest frequency" is a sufficient condition,
not a necessary one. What actually matters is that the copies do not overlap, and if a
signal occupies a narrow band that sits high up — 8 kHz to 12 kHz, say — the copies can be
made to interleave in the gaps. Here $B = 4$ kHz, and sampling at just 8 kSa/s puts the
band 8–12 kHz down onto 0–4 kHz with nothing else there to collide with. That is a third of
the rate the naive rule demands, and it is how a radio receiver digitises a 10.7 MHz
intermediate frequency without a 21.4 MSa/s converter. Two cautions come with it: the
converter's *analogue* input bandwidth must still reach the real frequency, and the sample
clock's jitter is judged against the real frequency too, not the sampled one.

**Coming back out.** The reconstruction that the theorem promises is a sum of sinc
functions, one centred on each sample. A sinc extends infinitely in both directions, so the
ideal reconstructor is non-causal and infinitely long — it cannot be built. A real DAC holds
each sample flat for $T_s$ instead, which is a convolution with a rectangular pulse of width
$T_s$, and by the previous reading that multiplies the spectrum by $\mathrm{sinc}(f/f_s)$.
At the band edge $f = f_s/2$ that factor is

```
sinc(0.5) = sin(pi/2) / (pi/2) = 2/pi = 0.6366   ->  3.92 dB down
```

the same $2/\pi$ that appeared halfway to the first null of the rectangular pulse, for
exactly the same reason. It is not an error, it is a known droop, and converters correct
for it with a gentle rising digital filter — or by oversampling, which pushes $f_s/2$ far
above the band edge and makes the droop negligible.

**Where the model itself gives out.** Real samplers have aperture time rather than
instantaneous impulses, clocks jitter, and the quantiser rounds. None of those is aliasing
and none is fixed by the anti-alias filter. Keep them separate in your head: aliasing is
about *when* you looked, quantisation is about *how precisely* you recorded what you saw,
and a converter with infinite resolution aliases exactly as badly as an 8-bit one.
''',
                },
            ],
            "numeric": [
                {
                    "title": "Where the first null lands",
                    "minutes": 4,
                    "brief": r'''
One rule, one unknown, to get the standard pair under your fingers before anything is
built on top of it. The width of a pulse and the width of its spectrum are locked
together; this asks for the second given the first.

Nothing here needs the integral to be done again.
''',
                    "prompt": "At what frequency does the spectrum of this pulse first fall to zero?",
                    "note": "Give the answer in kilohertz, to one decimal place.",
                    "figure": r'''
A single rectangular pulse is generated: 3.3 V high, **40 µs** wide, and zero everywhere
before and after it. It happens once and does not repeat.

Its transform is the standard pair $X(f) = A\tau\,\mathrm{sinc}(f\tau)$, with
$\mathrm{sinc}(x) = \sin(\pi x)/(\pi x)$.
''',
                    "given": [
                        {"label": "Pulse height $A$", "value": "3.3 V"},
                        {"label": "Pulse width $\\tau$", "value": "40 µs"},
                        {"label": "Wanted", "value": "the first null of $|X(f)|$"},
                    ],
                    "aside": "$\\mathrm{sinc}(x)$ is zero when $x$ is a whole number, and the argument "
                             "here is $f\\tau$. The height of the pulse cannot affect where a zero is.",
                    "answer": 25.0,
                    "tol": 0.2,
                    "unit": "kHz",
                    "hint": "Set $f\\tau = 1$ and solve for $f$. Keep the width in seconds: 40 µs is "
                            "$40 \\times 10^{-6}$ s.",
                    "wrong": "If you got 78.5, the sinc convention slipped: evaluating $\\sin(x)/x$ "
                             "with $x = f\\tau$ puts the first null at $\\pi/\\tau$ rather than at "
                             "$1/\\tau$. If you got 12.5, that is $1/(2\\tau)$ — half the null "
                             "frequency, which is where the response is still 64% of its peak.",
                    "why": r'''
```
first null:   f tau = 1
              f = 1 / tau
                = 1 / 40e-6 s
                = 25 000 Hz  =  25.0 kHz
```

The 3.3 V never enters it. Height scales the whole spectrum up and down together and moves
no zero anywhere; only the *width* sets the frequency axis. What the height does control is
$X(0) = A\tau = 3.3 \times 40\times10^{-6} = 132$ µV/Hz, the area under the pulse.

Worth noticing what the answer implies about a logic signal. A 40 µs pulse is slow by
digital standards and it already has significant content at 25 kHz and beyond — the
sidelobes at 37.5 kHz are only 13.5 dB down. Shorten the pulse to 40 ns, which is an
ordinary logic edge, and the same arithmetic puts the first null at 25 MHz. That is the
whole content of the phrase "fast edges radiate".
''',
                },
                {
                    "title": "Where the tone actually lands",
                    "minutes": 6,
                    "brief": r'''
Two steps rather than one: reduce modulo the sample rate, then decide whether the result
needs folding. Missing the second step is the single most common error in this module, and
the check against it is that the answer must always come out between 0 and $f_s/2$.
''',
                    "prompt": "At what frequency does this tone appear in the sampled data?",
                    "note": "Give the answer in kilohertz, to one decimal place.",
                    "figure": r'''
A converter runs at $f_s = 48$ kSa/s. Its anti-alias filter has been left off the board.

A pure sinusoid at **30 kHz** reaches its input at 1 V amplitude. Nothing else is present.
''',
                    "given": [
                        {"label": "Sample rate $f_s$", "value": "48 kSa/s"},
                        {"label": "Nyquist limit $f_s/2$", "value": "24 kHz"},
                        {"label": "Tone at the input", "value": "30 kHz, 1 V"},
                    ],
                    "aside": "Reduce modulo 48 first, then ask whether what is left exceeds 24. If it "
                             "does, subtract it from 48.",
                    "answer": 18.0,
                    "tol": 0.2,
                    "unit": "kHz",
                    "hint": "$30 \\bmod 48$ is just 30, since 30 is already less than 48. Now compare "
                            "30 with $f_s/2 = 24$.",
                    "wrong": "If you got 30, the fold was skipped: nothing above 24 kHz can appear in "
                             "data sampled at 48 kSa/s, because there is nowhere for it to be. If you "
                             "got 6, that is $30 - 24$ — folding about $f_s/2$ by subtracting it once "
                             "rather than reflecting about it, which is $f_s - f$.",
                    "why": r'''
```
f mod fs      = 30 mod 48 = 30 kHz
above fs/2 ?  = 30 > 24    yes, so it folds
appears at    = fs - 30 = 48 - 30 = 18.0 kHz
```

The amplitude is untouched — the folded tone arrives at the full 1 V it had at the input.
That is what makes aliasing so damaging: it does not attenuate the interference on its way
in, it merely relocates it, and it relocates it into the band you were trying to measure.

Two checks on the answer. It lies between 0 and $f_s/2$, as every alias must. And the
sample-by-sample argument agrees: $\cos(2\pi\cdot 30000\,nT_s)$ with $T_s = 1/48000$ is
$\cos(2\pi n \cdot 30/48) = \cos(2\pi n \cdot 0.625)$, and $0.625 = 1 - 0.375$, so every
sample equals $\cos(2\pi n \cdot 0.375)$ — a tone at $0.375 \times 48 = 18$ kHz.
''',
                },
                {
                    "title": "What the filter leaves of the interferer",
                    "minutes": 9,
                    "brief": r'''
A real anti-alias filter and a real interferer, on the same canvas. The switching
regulator on this board runs at 39 kHz, and some of it couples into the sensor input as a
250 mV sinusoid — that is the source drawn here. The converter samples at 20 kSa/s, so
$39 \bmod 20 = 19$ kHz, which folds to 1 kHz and lands in the middle of the wanted band.

The filter cannot stop it landing there. All it can do is make what lands small. The
question is how small.

Work out the corner from the two components before you do anything with the frequency.
''',
                    "prompt": "What amplitude does the 39 kHz interference have when it reaches the probe?",
                    "note": "Give the answer in millivolts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 0.25},
                            {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                            {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 6800},
                            {"id": "p3", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-8},
                            {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                            {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 4], "b": [11, 4]},
                        ],
                    },
                    "given": [
                        {"label": "Interference at the input", "value": "250 mV at 39 kHz"},
                        {"label": "Series resistor", "value": "6.8 kΩ"},
                        {"label": "Shunt capacitor", "value": "10 nF"},
                        {"label": "Converter", "value": "20 kSa/s"},
                    ],
                    "aside": "The probe is on the capacitor, so the network is the ordinary first-order "
                             "low-pass: $|H| = 1/\\sqrt{1 + (f/f_c)^2}$ with $f_c = 1/(2\\pi RC)$.",
                    # The prompt asks for an amplitude at one frequency rather than a node voltage, and
                    # both the corner and the source amplitude are read out of the drawn circuit, so a
                    # change to either component is re-measured rather than compared with a memory.
                    "check": "return c.gain(39000) * 1000;",
                    "answer": 14.98,
                    "tol": 0.15,
                    "unit": "mV",
                    "hint": "$f_c = 1/(2\\pi RC)$ with $R = 6.8$ kΩ and $C = 10$ nF comes to about "
                            "2.34 kHz. Then the ratio at 39 kHz, then multiply by the 250 mV that "
                            "arrived.",
                    "wrong": "If you got 250, the filter was applied at 1 kHz — the frequency the "
                             "interference *ends up* at — rather than at 39 kHz, where it actually "
                             "meets the filter. Filtering happens before sampling, so it is the real "
                             "frequency that is attenuated. If you got about 15.0 µV instead of mV, a "
                             "factor of a thousand slipped in the capacitor.",
                    "why": r'''
```
corner        fc = 1 / (2 pi R C)
                 = 1 / (2 pi x 6800 x 10e-9)
                 = 2340.5 Hz

ratio at 39 kHz  f/fc = 39000 / 2340.5 = 16.663
                 |H|  = 1 / sqrt(1 + 16.663^2)
                      = 1 / sqrt(278.66)
                      = 1 / 16.693  =  0.059906

amplitude        0.25 V x 0.059906 = 0.014976 V = 14.98 mV
```

So 250 mV of switching noise arrives at the converter as 15 mV, and then folds down to
1 kHz where it cannot be told from signal. Whether that is acceptable is a number, not an
opinion: against a 2 V full-scale input it is 0.75%, or about eight counts of a 10-bit
converter — visible, and far too big if this is a precision measurement.

The order of operations is the thing to take away. The filter acts at 39 kHz, where its
attenuation is 24.5 dB; the folding happens afterwards, in the sampler, and folding changes
frequency without changing amplitude. Reverse those two in your head and you conclude the
filter does nothing at all, because at 1 kHz it does not.

Improving it is a matter of moving the corner down, and the build in this module is exactly
that design problem with the constraint that the wanted band has to survive.
''',
                },
                {
                    "title": "The rate a bandpass signal actually needs",
                    "minutes": 11,
                    "brief": r'''
The last rung, and the first one where the familiar rule gives the wrong answer.

"Twice the highest frequency" is a sufficient condition, not a necessary one. What the
sampling theorem actually requires is that the copies of the spectrum, which land at every
multiple of $f_s$, do not overlap one another. For a signal sitting in a band well above
DC there is room for them to interleave, and the rate needed can be far lower than the
naive rule demands.

Sketch the axis from 0 to 24 kHz, mark the band and its mirror image at negative
frequencies, and slide copies along at spacing $f_s$ until nothing collides.
''',
                    "prompt": "What is the lowest sample rate at which this signal can be captured without aliasing?",
                    "note": "Give the answer in kSa/s, to one decimal place.",
                    "figure": r'''
A receiver's output is passed through a fixed analogue band-pass filter which leaves
**8 kHz to 12 kHz** and nothing else — below 8 kHz and above 12 kHz the filter's rejection
is total, and there is no content at DC.

The whole of that band must be recoverable from the samples. The sampled data is allowed to
place the band anywhere it likes between 0 and $f_s/2$; it does not have to appear at its
original frequency, only to be recoverable.
''',
                    "given": [
                        {"label": "Band occupied", "value": "8 kHz to 12 kHz"},
                        {"label": "Bandwidth $B$", "value": "4 kHz"},
                        {"label": "Highest frequency $f_h$", "value": "12 kHz"},
                        {"label": "Wanted", "value": "the minimum $f_s$"},
                    ],
                    "aside": "No sample rate can be below $2B$ — that much is forced, because the band "
                             "has to fit into $0 \\ldots f_s/2$ along with its negative-frequency "
                             "mirror. The question is whether $2B$ itself is achievable here.",
                    "answer": 8.0,
                    "tol": 0.1,
                    "unit": "kSa/s",
                    "hint": "Try $f_s = 8$ kSa/s and see where the band goes: subtract 8 kHz from every "
                            "frequency in it. Does what comes back fit between 0 and $f_s/2 = 4$ kHz "
                            "without meeting the copy coming the other way?",
                    "wrong": "If you got 24, that is $2f_h$ — the naive rule, which is safe and about "
                             "three times more converter than this signal needs. If you got 12, that is "
                             "$f_h$ itself, which is not a sampling rule at all. If you got 4, that is "
                             "$B$: a band of width 4 kHz still needs $2B$, because the negative-frequency "
                             "mirror has to fit into the baseband alongside it.",
                    "why": r'''
Check $f_s = 8$ kSa/s directly. Sampling copies the spectrum to every multiple of 8 kHz, so
take the copy shifted down by exactly one $f_s$:

```
band          8 kHz .... 12 kHz
copy at k=-1  8-8 = 0 ... 12-8 = 4 kHz

fs/2 = 4 kHz, so the copy occupies 0 ... 4 kHz  -- exactly the baseband, and no more

the mirror image at negative frequencies, -12 ... -8 kHz, shifts up by 8 to
-4 ... 0 kHz, which is the other half of the baseband and does not overlap
```

Nothing collides, so 8 kSa/s captures this signal completely, and the band comes back
occupying the whole of DC to 4 kHz with its frequency order preserved (8 kHz appears at DC,
12 kHz at 4 kHz). Since no rate below $2B = 8$ kSa/s can work — the band plus its mirror
needs $2B$ of room however it is placed — 8 kSa/s is the minimum.

This works so neatly because $f_h/B = 12/4 = 3$ is a whole number: the band sits in the
third slot of a ruler marked every 4 kHz, and the copies land in the slots either side of it
rather than on top of it. Shift the band to 9–13 kHz and $f_h/B = 3.25$, the copies no longer
line up with the slots, and the minimum rate rises to $2f_h/\lfloor f_h/B\rfloor =
2 \times 13/3 = 8.67$ kSa/s.

Three warnings come attached, and they are the reason nobody samples at exactly this rate in
practice. The band edges land exactly on DC and on $f_s/2$, both of which are the degenerate
cases this module keeps flagging, so a real design leaves a guard band and uses perhaps
10 kSa/s. The analogue front end of the converter must have a bandwidth reaching the true
12 kHz, not the 4 kHz you end up looking at — the sample-and-hold really is tracking a
12 kHz signal. And the clock's jitter is judged against 12 kHz too: a given timing error is
three times as damaging here as it would be for a baseband signal at 4 kHz.

This technique is called bandpass or harmonic sampling, and it is how a software radio
digitises a 10.7 MHz intermediate frequency with a converter running at a few tens of
megasamples per second instead of the 21.4 MSa/s the naive rule would demand — and, more
importantly, with a converter running slowly enough to have real resolution.
''',
                },
            ],
            "blanks": [
                {
                    "title": "Six tones, one converter",
                    "minutes": 8,
                    "caption": "reduce modulo the rate, then fold what is left",
                    "lang": "text",
                    "brief": r'''
The two-step rule, drilled until it is automatic: reduce the frequency modulo $f_s$, and
then, if what remains is above $f_s/2$, subtract it from $f_s$. Everything lands between 0
and $f_s/2$, always, so any answer outside that range is arithmetic rather than physics.

The rate is 48 kSa/s throughout, which puts the Nyquist limit at 24 kHz.
''',
                    "listing": """  sample rate  fs = 48 kSa/s          Nyquist limit  fs/2 = 24 kHz

  tone at f     f mod fs      above fs/2 ?      appears in the data at
 -----------------------------------------------------------------------
   10 kHz        10 kHz            no                  10 kHz

   30 kHz        30 kHz            yes                ___ kHz

   50 kHz       ___ kHz            no                   2 kHz

   70 kHz        22 kHz           ___                  22 kHz

   96 kHz         0 kHz            no                 ___ kHz

   24 kHz        24 kHz        the boundary           ___ kHz
""",
                    "blanks": [
                        {
                            "prompt": "30 kHz is already below the sample rate, but above 24 kHz. Where does it fold to?",
                            "hole": "kHz",
                            "opts": ["6", "18", "24", "30"],
                            "a": 1,
                            "why": "$f_s - f = 48 - 30 = 18$ kHz. The fold reflects about $f_s/2$, and reflecting 30 about 24 means going 6 kHz past it and coming back 6 kHz short: $24 - 6 = 18$. Subtracting $f_s/2$ instead gives 6 kHz, which is the standard slip — it treats the Nyquist line as a floor to subtract rather than as a mirror.",
                        },
                        {
                            "prompt": "50 kHz is above the sample rate. What is left after reducing modulo 48?",
                            "hole": "kHz",
                            "opts": ["2", "26", "46", "50"],
                            "a": 0,
                            "why": "$50 - 48 = 2$ kHz, and 2 is comfortably below 24, so no folding is needed and the tone appears at 2 kHz. A tone just above the sample rate aliases to a very low frequency — which is why interference near $f_s$ or any multiple of it is the worst kind to have on a board.",
                        },
                        {
                            "prompt": "70 kHz reduces to 22 kHz. Is 22 kHz above the Nyquist limit?",
                            "hole": "?",
                            "opts": ["yes", "no"],
                            "a": 1,
                            "why": "No: $22 < 24$, so nothing folds and 22 kHz is where it appears. Two tones 48 kHz apart are indistinguishable after sampling, so 70 kHz and 22 kHz produce identical data — and so does 118 kHz, and so on for ever.",
                        },
                        {
                            "prompt": "96 kHz is exactly twice the sample rate. Where does it appear?",
                            "hole": "kHz",
                            "opts": ["0", "24", "48", "96"],
                            "a": 0,
                            "why": "At 0 Hz. $96 = 2 \\times 48$, so every sample catches the waveform at the same point in its cycle and the recorded data is a constant — the tone has aliased to DC. It is the wagon wheel standing still, and it is why an interferer locked to the sample clock shows up as a mysterious offset rather than as a tone.",
                        },
                        {
                            "prompt": "24 kHz is exactly $f_s/2$. What frequency does the data show?",
                            "hole": "kHz",
                            "opts": ["0", "12", "24", "48"],
                            "a": 2,
                            "why": "24 kHz — but with an amplitude that depends entirely on the phase, which is the case the strict inequality $f_s > 2B$ exists to exclude. Sampling $\\sin(2\\pi \\cdot 24000\\,t)$ at 48 kSa/s gives all zeros; sampling $\\cos$ of the same frequency gives $+1, -1, +1, \\ldots$ at full amplitude. Same tone, same rate, and the recorded amplitude is anything between the two.",
                        },
                    ],
                },
                {
                    "title": "Sampling, line by line",
                    "minutes": 8,
                    "caption": "the five steps from a multiplication in time to a condition on the rate",
                    "lang": "text",
                    "brief": r'''
The derivation compressed to six lines, with the load-bearing pieces missing. It is worth
being able to reproduce, because every consequence in this module — the copies, the fold,
the strict inequality, the filter that must be analogue — is read off one of these lines.

The only theorem used is the one the whole course keeps returning to: what multiplication
does in one domain, convolution does in the other.
''',
                    "listing": """  sampling every Ts seconds                       fs = 1 / Ts

  1   xs(t) = x(t) . p(t),     p(t) = sum_n delta(t - n Ts)

  2   P(f)  = (1/Ts) sum_k delta(f - k ___)

  3   multiplying two signals in time   <->   ___ their spectra in frequency

  4   Xs(f) = (1/Ts) sum_k X(f - ___)

  5   the copy at 0 and the copy at fs stay clear of each other only if

          B  <  ___

  6   and what holds the input inside that limit is   ___
""",
                    "blanks": [
                        {
                            "prompt": "The impulse train in time transforms to an impulse train in frequency. What is the spacing of the frequency-domain one?",
                            "hole": "?",
                            "opts": ["fs/2", "fs", "2 fs", "1/fs"],
                            "a": 1,
                            "why": "$f_s = 1/T_s$. Impulses $T_s$ apart in time become impulses $1/T_s$ apart in frequency: dense in one domain is sparse in the other. Sample twice as often and the copies move twice as far apart, which is the whole mechanism by which a higher rate buys you room.",
                        },
                        {
                            "prompt": "Multiplication in time corresponds to which operation in frequency?",
                            "hole": "?",
                            "opts": ["adding", "convolving", "multiplying", "differentiating"],
                            "a": 1,
                            "why": "Convolving. This is the convolution theorem read in the direction the previous modules did not need: multiply two signals together and their spectra convolve. Everything peculiar about sampling follows from that one line.",
                        },
                        {
                            "prompt": "Convolving $X(f)$ with an impulse at $k f_s$ puts a copy of the spectrum where?",
                            "hole": "?",
                            "opts": ["fs/k", "k fs/2", "k fs", "fs"],
                            "a": 2,
                            "why": "At $kf_s$ — convolution with $\\delta(f - kf_s)$ is a shift by $kf_s$ and nothing else. The sum runs over every whole $k$, positive and negative, so the spectrum is replicated at 0, $\\pm f_s$, $\\pm 2f_s$ and so on for ever, all at $1/T_s$ of the original height.",
                        },
                        {
                            "prompt": "The copy centred at 0 reaches up to $B$; the copy centred at $f_s$ reaches down to $f_s - B$. What must $B$ stay below?",
                            "hole": "?",
                            "opts": ["fs/4", "fs/2", "fs", "2 fs"],
                            "a": 1,
                            "why": "$B < f_s/2$, which rearranges to $f_s > 2B$ — the sampling theorem, derived rather than quoted. The condition is that $f_s - B > B$: the bottom of the upper copy must stay above the top of the lower one. Equality is not good enough, as the tone sampled exactly at $f_s/2$ shows.",
                        },
                        {
                            "prompt": "Nothing guarantees the input obeys that limit. What makes it obey?",
                            "hole": "?",
                            "opts": [
                                "a digital low-pass applied to the samples",
                                "an analogue low-pass ahead of the converter",
                                "a notch filter at the sample rate",
                                "nothing — enough converter resolution removes the problem",
                            ],
                            "a": 1,
                            "why": "An analogue low-pass, before the converter. It is the only place the content above $f_s/2$ still exists as something separable: after the sampler it is superimposed on genuine signal at the same frequency and no filter can distinguish them. A notch at $f_s$ misses everything else that folds, and resolution is a different axis entirely — a converter with infinitely many bits aliases just as badly.",
                        },
                    ],
                },
            ],
            "derive": {
                "title": "The pulse and its spectrum, and the width one forces on the other",
                "minutes": 12,
                "vars": ["A", "f", "tau", "X"],
                "brief": r'''
The rectangular pulse is the one transform worth being able to produce from nothing. It is
the shape of a logic bit, of a radar burst, of a finite measurement record, and of the hold
a DAC applies on the way back out — so its spectrum turns up four times in this course under
four different names.

The pulse has height $A$, runs from $-\tau/2$ to $+\tau/2$, and is zero elsewhere. It is
**even**, so the $\sin$ half of $e^{-j2\pi ft} = \cos(2\pi ft) - j\sin(2\pi ft)$ integrates
to zero against it and the transform is the real integral

$$X(f) = \int_{-\tau/2}^{\tau/2} A\cos(2\pi f t)\,dt$$

Everything below is that integral and its consequences. Type a sine as `sin(...)` when you
enter an answer.
''',
                "steps": [
                    {
                        "prompt": "Evaluate the integral. The antiderivative of $\\cos(2\\pi f t)$ with respect to $t$ is $\\sin(2\\pi f t)/(2\\pi f)$. Write $X(f)$ in terms of $A$, $f$ and $\\tau$.",
                        "given": "$X(f) = A\\left[\\dfrac{\\sin(2\\pi f t)}{2\\pi f}\\right]_{-\\tau/2}^{+\\tau/2}$, and $\\sin$ is odd, so $\\sin(-\\theta) = -\\sin(\\theta)$.",
                        "answer": "\\frac{A sin(\\pi f \\tau)}{\\pi f}",
                        "hint": "At the upper limit the argument is $2\\pi f \\tau/2 = \\pi f \\tau$; at the lower limit it is $-\\pi f\\tau$. Subtracting a negative sine doubles it, and the 2 cancels the 2 in the denominator.",
                        "deconstruct": [
                            "Upper limit: $\\sin(\\pi f \\tau)/(2\\pi f)$. Lower limit: $\\sin(-\\pi f\\tau)/(2\\pi f) = -\\sin(\\pi f \\tau)/(2\\pi f)$.",
                            "Upper minus lower gives $2\\sin(\\pi f\\tau)/(2\\pi f)$, and the twos cancel.",
                        ],
                    },
                    {
                        "prompt": "What is $X(0)$? The expression is $0/0$ at $f = 0$, so use $\\sin\\theta \\to \\theta$ for small $\\theta$. Write the value in terms of $A$ and $\\tau$.",
                        "given": "For small $\\theta$, $\\sin\\theta \\approx \\theta$, so $\\sin(\\pi f \\tau) \\approx \\pi f \\tau$ as $f \\to 0$.",
                        "answer": "A\\tau",
                        "hint": "Replace $\\sin(\\pi f \\tau)$ by $\\pi f \\tau$ and cancel what is common to top and bottom.",
                        "deconstruct": [
                            "$\\dfrac{A \\cdot \\pi f \\tau}{\\pi f}$ — the $\\pi f$ cancels top and bottom.",
                            "What is left is $A\\tau$, which is the area under the pulse: height times width. That is $X(0)$ for any signal at all.",
                        ],
                    },
                    {
                        "prompt": "Where is the first null? Find the smallest positive $f$ at which $X(f) = 0$, in terms of $\\tau$.",
                        "given": "A fraction is zero when its numerator is, and $\\sin\\theta = 0$ at $\\theta = 0, \\pi, 2\\pi, \\ldots$",
                        "answer": "\\frac{1}{\\tau}",
                        "hint": "Set $\\pi f \\tau = \\pi$ and solve. The root at $\\theta = 0$ does not count, because there the denominator vanishes too and the value is $A\\tau$, not zero.",
                        "deconstruct": [
                            "$\\sin(\\pi f \\tau) = 0$ requires $\\pi f \\tau = n\\pi$ for a whole number $n$, so $f = n/\\tau$.",
                            "The smallest positive one is $n = 1$, giving $f = 1/\\tau$. The nulls after it are evenly spaced at $2/\\tau$, $3/\\tau$, and so on.",
                        ],
                    },
                    {
                        "prompt": "Halfway to that null, at $f = 1/(2\\tau)$, what is $X$? Write it in terms of $A$ and $\\tau$.",
                        "given": "$\\sin(\\pi/2) = 1$.",
                        "answer": "\\frac{2A\\tau}{\\pi}",
                        "hint": "The argument becomes $\\pi \\tau/(2\\tau) = \\pi/2$, so the numerator is just $A$. The denominator is $\\pi/(2\\tau)$, and dividing by a fraction inverts it.",
                        "deconstruct": [
                            "Numerator: $A\\sin(\\pi/2) = A$. Denominator: $\\pi f = \\pi/(2\\tau)$.",
                            "$A \\div \\dfrac{\\pi}{2\\tau} = \\dfrac{2A\\tau}{\\pi}$, which is $0.6366\\,A\\tau$ — the peak value reduced by $2/\\pi$.",
                        ],
                    },
                    {
                        "prompt": "Now halve the pulse width to $\\tau/2$, leaving the height at $A$. Where is the first null of the new spectrum, in terms of $\\tau$?",
                        "given": "The result of the third step holds for any width; substitute the new one.",
                        "answer": "\\frac{2}{\\tau}",
                        "hint": "The null is at one over the width, and the width is now $\\tau/2$.",
                        "deconstruct": [
                            "$f_{\\text{null}} = 1/(\\tau/2)$.",
                            "Dividing by a half doubles: $2/\\tau$. Half the pulse, twice the bandwidth, and $X(0)$ halves at the same time since the area halves.",
                        ],
                    },
                ],
                "closing": r'''
Put the five results together and the standard pair has been built from scratch:

$$X(f) = A\tau\,\frac{\sin(\pi f \tau)}{\pi f \tau} = A\tau\,\mathrm{sinc}(f\tau)$$

with a peak of $A\tau$ at DC, nulls every $1/\tau$, and the value $2A\tau/\pi$ at
$f = 1/(2\tau)$.

That last number is worth keeping. $2/\pi = 0.6366$ is $-3.92$ dB, and it comes back twice
wearing different clothes. Later in this module it is the depth of the droop a DAC's
zero-order hold puts on the band edge, because holding a sample for $T_s$ is a convolution
with a rectangular pulse of width $T_s$, and $f_s/2$ is exactly halfway to that pulse's
first null. In module 9 it is the worst-case loss a tone suffers for landing between two
DFT bins — a rectangular record is a rectangular pulse, and half a bin from centre is the
same halfway point.

The width relationship is the part to internalise. Step 5 halved the pulse and doubled the
bandwidth; the product of the two widths cannot be pushed below a fixed limit whatever
shape you choose, and the rectangle is a particularly clumsy way of spending it, given that
its sidelobes are only 13.3 dB down. A short pulse is a wide spectrum. There is no fast
signal in a narrow band, and there never will be.
''',
            },
            "sandbox": {
                "title": "What sampling does to a sine, and where the alias lands",
                "visualiser": "spectrum",
                "minutes": 10,
                "initial": {"fsig": 30, "fs": 200},
                "brief": r'''
Two panels, one signal. The **top** panel shows 100 ms of time: the faint grey curve is
the true continuous signal, the coloured dots are the samples taken at the chosen rate,
and — when the two disagree — an amber curve is drawn at the frequency the sampled data
will be read back as: the *other* sinusoid those same samples describe equally well.

Read the amber curve for its frequency rather than its sign. It is always drawn as
$\sin(2\pi f_a t)$, and folding a tone down through $f_s/2$ inverts the phase, so for a
folded tone the dots sit on the amber curve's mirror image rather than on the curve
itself. The frequency — which is the point — is right either way.

The **bottom** panel is the frequency axis, from 0 to 260 Hz. The dashed purple line
marks $f_s/2$, the Nyquist limit. The grey spike is the true signal frequency; the amber
spike, when it appears, is where the sampled data will claim the signal was.

Two sliders: the signal frequency, and the sample rate.
''',
                "notice": [
                    "It opens at 30 Hz sampled at 200 Hz, and there is no amber anywhere — neither a curve in the top panel nor a spike in the bottom one. The grey spike at 30 Hz sits well to the left of the dashed line at 100 Hz, and the dots, one every 5 ms, trace the grey curve without ambiguity.",
                    "Leave the rate at 200 Hz and drag the signal up to 230 Hz. The grey spike moves to the right of the dashed line, and an amber spike appears at 30 Hz: $230 - 200$, the remainder after reducing modulo the sample rate. In the top panel the amber curve is a slow 30 Hz wave, and every sample dot lies on it *and* on the fast grey curve at the same time. That is the whole of aliasing — the dots cannot tell you which curve they came from.",
                    "Now try 170 Hz, which reaches the same place by folding rather than by wrapping: $200 - 170$ is 30 again, and the amber spike does not move. The top panel does change, though. The dots now trace the amber curve *upside down*, because folding down through $f_s/2$ reverses the phase while the visualiser draws every alias with the same fixed phase. The frequency is what the picture is telling you; the sign is not.",
                    "Now set the signal to exactly 100 Hz, half the sample rate. Every dot sits on the zero line, because a sample every half period lands on a zero crossing each time; the grey curve is plainly not zero. The caption below still reports that nothing is lost, because it compares the folded frequency with the true one and here they agree — and the picture is the reason the sampling condition is written $f_s > 2B$ with a strict inequality rather than $f_s \\ge 2B$.",
                    "Put the signal back to 30 Hz and drag the sample rate down to 50 Hz. The dashed line moves left to 25 Hz, the 30 Hz spike is now to the right of it, and the alias appears at 20 Hz. Only six dots remain in the 100 ms window. Nothing about the signal changed: aliasing is a property of the pair, not of the signal alone.",
                ],
            },
            "quiz": {
                "title": "Spectra, sampling and where the tone went",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A rectangular pulse 1 ms wide is shortened to 0.25 ms. What happens to its spectrum?",
                        "opts": [
                            "it becomes four times narrower, with the first null moving from 1 kHz to 250 Hz",
                            "it becomes four times wider, with the first null moving from 1 kHz to 4 kHz",
                            "it is unchanged, because the pulse shape is the same",
                            "it shifts up by 3 kHz without changing shape",
                        ],
                        "a": 1,
                        "why": r'''
A pulse of width $\tau$ transforms to $\tau\,\mathrm{sinc}(f\tau)$, whose first null is at
$1/\tau$: 1 kHz becomes 4 kHz. Narrow in time is wide in frequency, always, and the
product of the two widths cannot be reduced below a fixed limit. This is why a fast
digital edge radiates over a huge span of frequencies, and why deliberately slowing
edges is the first thing tried when a board fails an emissions test.
''',
                    },
                    {
                        "q": "A 1.7 kHz sinusoid is sampled at 1 kSa/s. At what frequency will it appear in the sampled data?",
                        "opts": ["0.7 kHz", "1.7 kHz", "0.3 kHz", "0.5 kHz"],
                        "a": 2,
                        "why": r'''
Reduce modulo the sample rate: $1.7 \bmod 1 = 0.7$ kHz. That is above $f_s/2 = 0.5$ kHz,
so it folds: $1 - 0.7 = 0.3$ kHz. The answer 0.7 kHz is the common slip — stopping after
the modulo and forgetting the fold — and it is worth checking your arithmetic against the
rule that the result must always land between 0 and $f_s/2$. Nothing above 500 Hz can
appear in data sampled at 1 kSa/s, because there is nowhere for it to be.
''',
                    },
                    {
                        "q": "An anti-alias filter is placed after the ADC, in software, instead of before it. What does it achieve?",
                        "opts": [
                            "the same thing, provided the digital filter is sharper than the analogue one would have been",
                            "the same thing, but only if the sample rate is at least four times the bandwidth",
                            "nothing useful — the aliased content is already sitting on top of the signal and cannot be separated from it",
                            "it works, but adds a delay of one sample period",
                        ],
                        "a": 2,
                        "why": r'''
Nothing useful. Once the samples exist, the aliased component occupies exactly the same
frequency as genuine signal content at that frequency; no filter of any kind, however
sharp, can distinguish two things that are identical. This is the single most important
practical consequence in the module: the anti-alias filter is analogue, it comes first,
and it is one of the few parts of a signal chain where a mistake is unrecoverable rather
than merely inconvenient.
''',
                    },
                    {
                        "q": "A signal occupies DC to 4 kHz and must be sampled. Which statement is correct?",
                        "opts": [
                            "8 kSa/s is the theoretical minimum, and any real system uses a rate above it to leave room for a real filter",
                            "8 kSa/s is sufficient in principle and comfortable in practice",
                            "4 kSa/s suffices, because that matches the highest frequency present",
                            "16 kSa/s is the theoretical minimum, at four samples per cycle",
                        ],
                        "a": 0,
                        "why": r'''
The Nyquist rate is $2B = 8$ kSa/s, but it is a limit rather than a working choice: it
assumes a brick-wall filter with zero transition width, which does not exist. Real
designs sample at some multiple — 44.1 kSa/s for a 20 kHz audio band is the familiar
example, leaving over 2 kHz of transition band for the analogue filter to roll off in.
Calling 8 kSa/s *comfortable* is the textbook answer that forgets the filter has to
exist, and it is the reason so many first designs alias.
''',
                    },
                    {
                        "q": "Why does sampling copy the spectrum to every multiple of $f_s$?",
                        "opts": [
                            "because the sampler generates harmonics of its own clock, and each one carries a copy of the signal with it",
                            "because quantisation noise spreads evenly across every frequency the converter is able to represent",
                            "because the samples are discrete, and any discrete signal has a periodic spectrum by construction",
                            "because sampling multiplies by an impulse train, and multiplication in time is convolution in frequency",
                        ],
                        "a": 3,
                        "why": r'''
The mechanism is the one this course keeps returning to: multiplication in one domain is
convolution in the other. The impulse train's spectrum is another impulse train spaced
$f_s$ apart, and convolving a spectrum with an impulse at $kf_s$ simply moves a copy
there. "Any discrete signal has a periodic spectrum by construction" states a true fact —
the spectrum of a sampled signal is periodic — but offers it as its own explanation. Note that none of this involves quantisation: aliasing
happens even with a converter of infinite resolution.
''',
                    },
                    {
                        "q": "A converter samples at 20 kSa/s. Interference at 19 kHz reaches its input. Where does it end up?",
                        "opts": ["at 19 kHz, harmlessly outside the band", "at 1 kHz, in the middle of the wanted band", "at 10 kHz, exactly on the Nyquist line", "it is rejected automatically, because it is above $f_s/2$"],
                        "a": 1,
                        "why": r'''
$19 \bmod 20 = 19$ kHz, which exceeds $f_s/2 = 10$ kHz, so it folds to $20 - 19 = 1$ kHz
and lands squarely in the wanted band. Nothing is rejected automatically — that is the belief behind "rejected automatically, because it is above $f_s/2$", and
it is exactly backwards: frequencies above $f_s/2$ are not
discarded by the sampler, they are *relocated* by it. Interference close to a multiple of
the sample rate is the worst case, because it folds to a low frequency where the wanted
signal usually lives.
''',
                    },
                ],
            },
            "build": {
                "title": "The filter that has to come first",
                "minutes": 25,
                "brief": r'''
A converter on your board samples at **20 kSa/s**. The signal you care about occupies
**DC to 2 kHz**. Everything from 10 kHz upwards — $f_s/2$ and above — will fold down
into the sampled band and cannot be removed afterwards, so it has to be attenuated
*before* the converter.

Design the analogue filter that goes there. Drive it from the 1 V source on the canvas,
put the probe on its output, and meet both of these:

1. **Keep the band.** At 2 kHz the output must be at least $1/\sqrt{2}$ of its
   low-frequency value — no more than 3 dB of loss at the top of the wanted band.
2. **Kill what folds.** At 10 kHz the output must be down to **a third** of its
   low-frequency value or less, and it must keep falling above that.

The filter must also pass low frequencies essentially untouched: a network that
attenuates everything equally satisfies neither requirement in spirit and fails the
first check.

## Working out the window

For a single-pole low-pass with corner $f_c$, the amplitude ratio is
$1/\sqrt{1 + (f/f_c)^2}$. Requirement 1 puts a **lower** bound on $f_c$ and requirement 2
puts an **upper** one. Write both out before drawing anything; the design is any $f_c$
inside the window, and $f_c = 2.5$ kHz sits comfortably in the middle.

It is worth noticing how narrow that window is. Ask for a factor of ten at 10 kHz
instead of a factor of three and the two bounds cross — no single-pole filter can do it,
whatever values you choose. That is what module 4's second pole is for.

## Drawing it

Place parts from the toolbar and wire them with two clicks. Values accept `10n`, `6.4k`
and `1e-8` alike. The checks measure the response; any pair of values that meets both
requirements passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "OUT", "x": 5, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 6366},
                        {"id": "p3", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-8},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [9, 4], "b": [11, 4]},
                    ],
                },
                "checks": [
                    {"name": "the wanted band arrives at the probe essentially untouched", "code": r'''
c.assert(c.count('V') === 1, 'Drive the filter from exactly one source; found ' + c.count('V') + '.');
const vs = c.values('V')[0];
const dc = c.gain(10);
c.assert(dc > 0.98 * vs,
  'At 10 Hz the probe sees ' + (dc / vs * 100).toFixed(1) + '% of the source voltage. ' +
  'An anti-alias filter must pass the wanted band, not divide it down.');
'''},
                    {"name": "at 2 kHz the loss is no more than 3 dB", "code": r'''
const ref = c.gain(10);
const r = c.gain(2000) / ref;
c.assert(r >= 0.70,
  'At 2 kHz the output is ' + (r * 100).toFixed(1) + '% of its low-frequency value; the ' +
  'top of the wanted band may lose no more than 3 dB, so this needs at least 70.7%. ' +
  'Your corner frequency is too low.');
'''},
                    {"name": "at 10 kHz what would fold is down to a third", "code": r'''
const ref = c.gain(10);
const r = c.gain(10000) / ref;
c.assert(r <= 0.34,
  'At 10 kHz the output is still ' + (r * 100).toFixed(1) + '% of its low-frequency ' +
  'value, and everything there folds into the sampled band. It must be 33% or less, ' +
  'so this corner frequency is too high.');
'''},
                    {"name": "and it goes on falling above the Nyquist frequency", "code": r'''
const ref = c.gain(10);
const a = c.gain(10000) / ref;
const b = c.gain(100000) / ref;
c.assert(b < a, 'The response must keep falling above 10 kHz, not level off or rise: ' +
  (a * 100).toFixed(1) + '% at 10 kHz against ' + (b * 100).toFixed(1) + '% at 100 kHz.');
c.assert(b < 0.05, 'A decade above the Nyquist frequency the response should be well ' +
  'under 5% of the passband; measured ' + (b * 100).toFixed(2) + '%.');
'''},
                ],
                "hints": [
                    "Requirement 1: $1/\\sqrt{1 + (2000/f_c)^2} \\ge 1/\\sqrt{2}$ gives $f_c \\ge 2$ kHz.",
                    "Requirement 2: $1/\\sqrt{1 + (10000/f_c)^2} \\le 1/3$ gives $1 + (10000/f_c)^2 \\ge 9$, so $f_c \\le 10000/\\sqrt{8} \\approx 3.54$ kHz.",
                    "Pick $f_c = 2.5$ kHz, choose a round capacitor — 10 nF — and let $R = 1/(2\\pi f_c C)$ decide the resistor. That comes to about 6.37 kΩ.",
                    "The resistor goes in series from the source, the capacitor from the output node down to ground, and the probe sits on the node between them. Without a ground symbol nothing can be measured at all.",
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "The transfer function: convolution becomes multiplication",
            "summary": "Send a complex exponential into an LTI system and it comes back scaled. That one fact turns the hardest operation in module 1 into a product.",
            "concepts": [
                "Feed $e^{j\\omega t}$ into an LTI system and the output is $H(j\\omega)\\,e^{j\\omega t}$ — the same function, scaled by a complex number. Complex exponentials are the **eigenfunctions** of every LTI system, and no other family of signals has this property.",
                "That scale factor is the **transfer function**, and substituting into the convolution integral identifies it: $H(j\\omega) = \\int h(\\tau)e^{-j\\omega\\tau}\\,d\\tau$, the Fourier transform of the impulse response.",
                "Hence the **convolution theorem**: $y = h * x$ in time becomes $Y(j\\omega) = H(j\\omega)X(j\\omega)$ in frequency. The awkward operation of module 1 becomes a multiplication, one frequency at a time, and this is the reason engineers work in the frequency domain at all.",
                "$|H|$ scales each component and $\\angle H$ shifts it. Watch the sign: a **lag**, $\\angle H = -\\phi$, is a *delay* of $\\phi/\\omega$ seconds, so the delay is $-\\angle H/\\omega$. A system whose phase falls linearly with frequency therefore delays every component by the same time and does not distort the waveform; one whose phase bends does.",
                "For a circuit, $H(j\\omega)$ needs no new theory at all — it is the impedance divider from EE102 with $Z_R = R$, $Z_C = 1/(j\\omega C)$ and $Z_L = j\\omega L$.",
                "The RC low-pass has $H = \\frac{1}{1 + j\\omega RC}$: one pole, a corner at $\\omega = 1/RC$, a magnitude falling at 20 dB per decade beyond it, and exactly $-45^\\circ$ of phase at the corner.",
                "A series RLC with the output across the capacitor has $H = \\frac{1}{1 - \\omega^2 LC + j\\omega RC}$: two poles, a magnitude falling at 40 dB per decade, and $-90^\\circ$ at $\\omega_n$. Written in standard form the two parameters are $\\omega_n = 1/\\sqrt{LC}$ and $\\zeta = \\frac{R}{2}\\sqrt{C/L}$.",
                "$\\zeta$ decides the shape. Below about 0.707 the magnitude peaks before falling; at $\\zeta = 1/\\sqrt{2}$ the response is as flat as a two-pole filter can be and the $-3$ dB point coincides with $\\omega_n$; above that the corner softens and moves down.",
                "A **Bode plot** uses decibels against log frequency, which turns products into sums: cascade two systems and their dB curves add, as do their phase curves. That is the whole reason for the logarithmic axes.",
                "A periodic input passes through line by line: harmonic $n$ comes out multiplied by $H(jn\\omega_0)$. A square wave through a low-pass filter loses its high harmonics first, which is why it comes out with rounded corners — the same statement as module 2's remark that edges cost bandwidth.",
            ],
            "read": [
                {
                    "title": "The one input that comes out looking like itself",
                    "minutes": 15,
                    "body": r'''
Put a signal generator on the bench, wire it into a filter, and wire the filter into an
oscilloscope. Set the generator to a sine wave and sweep it slowly upwards while watching
the screen. Whatever is inside the filter — one resistor and one capacitor, or a crate of
them — the same thing happens at every frequency you stop at: **a sine wave goes in and a
sine wave comes out**. Same frequency. Different height, and sliding along the time axis
relative to the input, but unmistakably the same shape.

It is worth being surprised by that, because nothing else survives the trip. Put a square
wave in and what comes out has rounded corners and sagging tops — a different waveform.
Put a single sharp click in and out comes a smear that lasts far longer than the click
did. Of all the signals you could choose, the sinusoid is the one the box cannot deform.
It can only make it bigger or smaller and move it along a bit.

Every result in this module is a consequence of that one experimental fact, so the first
job is to understand why it happens.

## Why the exponential rather than the sine

The clean statement is not about sines but about complex exponentials, $e^{j\omega t}$.
Euler's formula makes the two versions equivalent — $\cos\omega t = \frac12(e^{j\omega t} +
e^{-j\omega t})$, so a real sinusoid is the sum of two complex exponentials — and the
exponential is the version worth working with because it has an algebraic property no
sinusoid has:

$$e^{j\omega(t - \tau)} = e^{j\omega t}\,e^{-j\omega \tau}$$

A shift in time turns into a *multiplication by a constant*. Try that with a cosine and
you get $\cos\omega t\cos\omega\tau + \sin\omega t\sin\omega\tau$, which is not $\cos\omega
t$ times anything. That single line of algebra is why the complex exponential is the test
signal of choice, and everything below is it being cashed in.

## Three lines, and the whole module falls out

Module 1 established that an LTI system is completely described by its impulse response
$h$, and that the output for any input is the convolution

$$y(t) = \int_{-\infty}^{\infty} h(\tau)\,x(t-\tau)\,d\tau$$

Now put $x(t) = e^{j\omega t}$ into it and turn the handle:

```
y(t) = integral over tau of  h(tau) * e^{jw(t - tau)} dtau

     = integral over tau of  h(tau) * e^{jwt} * e^{-jw tau} dtau      (split the exponential)

     = e^{jwt} * integral over tau of h(tau) e^{-jw tau} dtau          (e^{jwt} has no tau in it)

     = e^{jwt} * H(jw)
```

Look at what happened in the third line. The factor $e^{j\omega t}$ carries no $\tau$, so
it is a constant as far as that integral is concerned and it walks straight out through
the integral sign. What is left behind is a number — an ordinary complex number that
depends on $\omega$ and on $h$ but not at all on $t$:

$$H(j\omega) = \int_{-\infty}^{\infty} h(\tau)\,e^{-j\omega\tau}\,d\tau$$

So the output is the input multiplied by a constant. In goes $e^{j\omega t}$, out comes
$H(j\omega)e^{j\omega t}$: the same function of time, scaled. In the language of linear
algebra the complex exponentials are the **eigenfunctions** of every LTI system and
$H(j\omega)$ is the eigenvalue at that frequency, and the bench observation this reading
opened with is the physical form of that statement.

That integral, incidentally, is the Fourier transform of $h$. Module 3 built it as a tool
for describing signals; here it arrives from a completely different direction, as the
answer to "by how much does this box scale a complex exponential". The two are the same
integral, and $H$ is called the **transfer function**.

## From one frequency to all of them

One frequency is not enough on its own. What makes it enough is that an arbitrary input
can be written as a sum of exponentials — that is precisely what its spectrum $X(j\omega)$
is — and that the system is linear, so the pieces can be pushed through separately and
added at the far end. Each piece is scaled by $H$ at its own frequency, so the output
spectrum is

$$Y(j\omega) = H(j\omega)\,X(j\omega)$$

This is the **convolution theorem**, and it deserves a moment of attention because it is
the reason the frequency domain is worth entering. In the time domain, finding the output
means evaluating an integral in which every value of $y$ depends on the entire history of
$x$. In the frequency domain it means multiplying two numbers, and each frequency is
handled entirely on its own with no reference to any other. The single hardest operation
in module 1 has become the single easiest operation in arithmetic.

## $H$ is two numbers per frequency, and both of them matter

$H(j\omega)$ is complex, so at each frequency it carries a magnitude and an angle, and
they do different jobs. $|H|$ multiplies the amplitude. $\angle H$ adds to the phase —
which is to say it slides the component along the time axis.

Take the RC low-pass with $R = 12$ kΩ and $C = 10$ nF, and drive it with two tones at
once: 1 V at 1 kHz and 0.5 V at 3 kHz. The transfer function of that network is
$H = 1/(1 + j\omega RC)$, so:

```
RC       = 12e3 * 10e-9 = 1.2e-4 s
corner   fc = 1/(2 pi RC) = 1326.29 Hz

tone at 1 kHz
  wRC    = 2 pi * 1000 * 1.2e-4 = 0.75398
  |H|    = 1/sqrt(1 + 0.75398^2) = 1/sqrt(1.56849) = 1/1.25239 = 0.79847
  angle  = -atan(0.75398) = -37.02 degrees
  out    = 1.000 V * 0.79847 = 0.7985 V, lagging by 37.02 degrees

tone at 3 kHz
  wRC    = 2 pi * 3000 * 1.2e-4 = 2.26195
  |H|    = 1/sqrt(1 + 2.26195^2) = 1/sqrt(6.11640) = 1/2.47314 = 0.40434
  angle  = -atan(2.26195) = -66.15 degrees
  out    = 0.500 V * 0.40434 = 0.2022 V, lagging by 66.15 degrees
```

so the output waveform, written out in full, is

$$y(t) = 0.7985\sin(2\pi \cdot 1000\,t - 37.02^\circ) + 0.2022\sin(2\pi\cdot 3000\,t - 66.15^\circ)$$

Two multiplications and two additions, and there is no differential equation anywhere in
sight. Notice also what the filter has done to the *balance* of the two tones: at the
input the 3 kHz component was half the size of the 1 kHz one, and at the output it is
$0.2022/0.7985 = 0.253$ of it. That change of ratio is the entire point of a filter, and
the reason the word "filter" is used at all.

## Phase is not a delay, and the difference bites

Here is the mistake, and it is worth naming precisely because it is so easy to walk into.
A phase shift of $-37^\circ$ is *not* a time shift of $37$ of anything. Phase is measured
in fractions of a cycle, and a cycle is a different length of time at every frequency.
Converting to a time takes a division:

$$t_{\text{delay}} = \frac{-\angle H}{\omega}$$

The minus sign is there because a **lag** — a negative angle — is what a delay looks like.
Run the two tones above through it:

```
1 kHz:  angle = -37.02 deg = -0.64604 rad
        delay = 0.64604 / (2 pi * 1000) = 1.0282e-4 s = 102.82 us

3 kHz:  angle = -66.15 deg = -1.15453 rad
        delay = 1.15453 / (2 pi * 3000) = 6.1250e-5 s =  61.25 us
```

The two components of the same signal are delayed by *different times*: 102.8 µs and
61.2 µs, a difference of 41.6 µs. They arrive at the far end in a different relative
position from the one they started in, and a signal whose components have been shuffled
in time is a signal whose shape has changed. This is **phase distortion**, and it is why a
filter alters a waveform even in the band where its magnitude response is nearly flat.

The mistake is tempting because of how phase gets measured. On a scope you read the shift
between two traces in divisions of time and then convert it to degrees, so degrees start
to feel like time wearing a different hat. They are not. Divide by $\omega$, every time.

The reference case worth keeping in mind is the pure delay, $y(t) = x(t - T)$, whose
impulse response is $\delta(t-T)$ and whose transfer function is therefore

$$H(j\omega) = e^{-j\omega T}$$

Its magnitude is 1 at every frequency and its phase is $-\omega T$: a straight line
through the origin. Divide by $\omega$ and the delay comes out as $T$ at every frequency,
the same for all of them. **Linear phase means constant delay means no change of shape.**
Everything else — every filter with a curve in its phase response — moves the components
relative to one another. A first-order RC has a phase that bends hard near its corner, and
the 41.6 µs above is the price.

## Where this stops holding

$H(j\omega)$ is a smaller claim than it looks, and four boundaries are worth marking.

- **It requires LTI, and nothing less.** The three lines of algebra used the convolution
  integral, which exists only because the system is linear and time invariant. A mixer,
  a clipping amplifier, a rectifier, a switched-mode converter: none of them has a
  transfer function, and quoting one for them is not an approximation but a category
  error. What such circuits do — produce output frequencies that were not in the input —
  is exactly what $Y = HX$ forbids, because if $X$ is zero at some frequency then $Y$ is
  zero there too whatever $H$ does.

- **It is a steady-state statement.** $H$ describes what a system does to an exponential
  that has been running since $t = -\infty$. Switch a real generator on at $t = 0$ and
  there is a transient while the energy in the capacitors and inductors settles, and $H$
  says nothing about it directly. The transient is not a defect in the theory — feed the
  *whole* input, step and all, through $Y = HX$ and it appears — but it does mean that a
  circuit with initial charge on a capacitor is not described by $H$ alone.

- **The integral has to converge.** If $h$ grows rather than decays, $\int|h|\,d\tau$ is
  infinite and the Fourier transform of $h$ does not exist. An unstable system therefore
  has no transfer function in this sense, which is awkward given that instability is
  exactly the thing you most want to predict. The repair is the Laplace transform, which
  replaces $j\omega$ by a general complex $s$ and buys convergence at the cost of an extra
  dimension; that is where CTRL510 begins.

- **$H$ belongs to a stage together with its load.** The transfer function of a filter
  measured with nothing attached is not the transfer function it has when the next stage
  is drawing current from it. The next reading works an example where ignoring this moves
  a corner frequency by nearly a factor of two.
''',
                },
                {
                    "title": "From components to a curve, and back",
                    "minutes": 16,
                    "body": r'''
The last reading arrived at $H(j\omega) = \int h(\tau)e^{-j\omega\tau}d\tau$ and left it
there, which is fine as a definition and useless as a working method. Nobody analysing an
RC filter measures its impulse response and integrates. For a circuit there is a much
shorter route, and it is one you already know from the first year without having called
it by this name.

## Impedance is the eigenfunction property in disguise

Ask what a capacitor does to a complex exponential. Its defining relation is $i = C\,
dv/dt$, so with $v = V e^{j\omega t}$:

$$i = C\frac{d}{dt}\left(Ve^{j\omega t}\right) = j\omega C\,V e^{j\omega t}$$

Differentiating an exponential multiplies it by $j\omega$ — the same property from the
last reading, seen once more. The current is a complex exponential of the same frequency,
so the ratio of voltage to current is a plain complex number:

$$Z_C = \frac{V}{I} = \frac{1}{j\omega C}$$

and the same argument on $v = L\,di/dt$ gives $Z_L = j\omega L$, while a resistor gives
$Z_R = R$ with no frequency in it at all. **Impedance is what the eigenfunction property
looks like for one component.** Once each element has been replaced by its impedance, the
circuit is a resistive network with complex numbers in it, and $H$ is nothing but the
divider ratio you would have written in EE101.

## One pole, all the way through

Series resistor, shunt capacitor, output across the capacitor. The same current flows
through both, so voltage divides in proportion to impedance:

$$H(j\omega) = \frac{Z_C}{Z_R + Z_C} = \frac{\frac{1}{j\omega C}}{R + \frac{1}{j\omega C}}
 = \frac{1}{1 + j\omega RC}$$

Multiplying top and bottom by $j\omega C$ is the whole of the algebra. What is left is one
of the two or three most useful expressions in electronics, and it is worth reading rather
than memorising. At low frequency the $j\omega RC$ term is negligible, $H \to 1$, and
everything gets through. At high frequency it dominates, $H \to 1/(j\omega RC)$, which
falls off as $1/\omega$ — a factor of ten down for every factor of ten up in frequency.
The changeover is where the two terms are equal in size, $\omega RC = 1$, which defines
the **corner**:

$$\omega_c = \frac{1}{RC}, \qquad f_c = \frac{1}{2\pi RC}$$

Take $R = 4.7$ kΩ and $C = 10$ nF, so $RC = 4.7\times10^{-5}$ s and $f_c = 3386$ Hz, and
tabulate what the formula says:

```
f          f/fc      |H| = 1/sqrt(1+(f/fc)^2)   dB = 20 log10|H|   angle = -atan(f/fc)
--------------------------------------------------------------------------------------
  338.6 Hz  0.1       0.99504                     -0.04              -5.71 deg
 3386.3 Hz  1.0       0.70711                     -3.01             -45.00 deg
20000.0 Hz  5.9062    0.16694                    -15.55             -80.39 deg
33862.8 Hz 10.0       0.09950                    -20.04             -84.29 deg
```

Three things in that table are worth carrying away. At the corner the magnitude is
$1/\sqrt{2}$ and the phase is exactly $-45^\circ$ — this is the definition of the corner
and the reason it is also called the half-power point, since power goes as the square of
voltage and $(1/\sqrt2)^2 = 1/2$. A decade above the corner the magnitude is 0.0995, which
is a tenth to within half a per cent, so the straight-line approximation "one pole falls at
a factor of ten per decade" is not an approximation worth worrying about once you are a
decade out. And the phase is still $5.7^\circ$ short of $-90^\circ$ a decade above the
corner: a single pole approaches $-90^\circ$ but never reaches it.

## Why the axes are logarithmic

The **decibel** is $20\log_{10}|H|$ for a voltage ratio, and a Bode plot is that quantity
against $\log f$. The reason for both logarithms is one line of algebra: cascade two
stages and the transfer functions multiply, $H = H_1H_2$, so

$$20\log_{10}|H| = 20\log_{10}|H_1| + 20\log_{10}|H_2|$$

and $\angle H = \angle H_1 + \angle H_2$ as well, since the argument of a product is the
sum of the arguments. **Multiplication becomes addition, so responses can be sketched by
stacking simple pieces.** Put the filter above into an amplifier of gain 2 and the
arithmetic at 20 kHz is:

```
filter at 20 kHz     20 log10(0.16694)  =  -15.55 dB
amplifier, gain 2    20 log10(2)        =   +6.02 dB
                                           --------
cascade                                     -9.53 dB   ->  10^(-9.53/20) = 0.334
```

and 0.334 is indeed $0.16694 \times 2$. On the graph that is one curve slid up by 6 dB,
which is why an experienced eye reads a Bode plot faster than it reads the algebra.

A few conversions are worth knowing outright, because they turn up constantly: a factor
of 2 is 6.02 dB, a factor of 10 is 20 dB, $1/\sqrt2$ is $-3.01$ dB, and a slope of one
pole is $-20$ dB/decade, which is the same thing as $-6.02$ dB/octave.

## Two poles, and what the second one buys

Put an inductor in the series arm as well: source, then $R$ and $L$ in series, then $C$ to
ground with the output across it. Still a divider, still the same current everywhere:

$$H(j\omega) = \frac{\frac{1}{j\omega C}}{R + j\omega L + \frac{1}{j\omega C}}
= \frac{1}{1 - \omega^2 LC + j\omega RC}$$

The $-\omega^2 LC$ appears because $j\omega L \cdot j\omega C = j^2\omega^2 LC$ and
$j^2 = -1$. The module's derivation matches this against the standard form

$$H = \frac{1}{1 - (\omega/\omega_n)^2 + j2\zeta(\omega/\omega_n)},\qquad
\omega_n = \frac{1}{\sqrt{LC}},\qquad \zeta = \frac{R}{2}\sqrt{\frac{C}{L}}$$

which is worth doing because $\omega_n$ and $\zeta$ are the two numbers the shape of the
curve actually depends on. Three components, two numbers: the response cannot tell you
$L$, $C$ and $R$ separately, only these combinations of them.

Work one right through. Take $L = 100$ mH, $C = 100$ nF and $R = 1.5$ kΩ:

```
omega_n = 1/sqrt(LC) = 1/sqrt(0.1 * 100e-9) = 1/sqrt(1e-8) = 1e4 rad/s
f_n     = 1e4 / (2 pi) = 1591.5 Hz

zeta    = (R/2) sqrt(C/L) = 750 * sqrt(100e-9/0.1) = 750 * 1e-3 = 0.75

at f = 3 kHz:
  u     = f/f_n = 3000/1591.5 = 1.88496
  1-u^2 = 1 - 3.55306 = -2.55306
  2*zeta*u = 1.5 * 1.88496 = 2.82743
  |H|   = 1/sqrt(2.55306^2 + 2.82743^2) = 1/sqrt(14.5125) = 1/3.80953 = 0.26250
  dB    = -11.62
  angle = atan2(-2.82743, -2.55306) = -132.08 degrees
```

Now compare that against a *single* pole placed at the same 1591.5 Hz. At 3 kHz the
one-pole filter gives $1/\sqrt{1 + 1.885^2} = 0.4686$, or $-6.58$ dB; the two-pole gives
$0.2625$, or $-11.62$ dB. Five decibels of extra rejection less than an octave past the
corner. Go a full decade out, to 15.9 kHz, and the gap is far wider: one pole gives
$0.0995$, two poles give $0.00999$ — a tenth against a hundredth, which is the 20 against
40 dB per decade the module keeps repeating.

Notice the phase too. At 3 kHz the second-order filter is already at $-132^\circ$, past
the $-90^\circ$ that a first-order filter can never exceed, and heading for $-180^\circ$.
Each pole contributes up to $90^\circ$ of lag, and that accumulating lag is exactly what
makes a feedback loop with too many poles in it oscillate — which is CTRL510's subject and
the reason this material is a prerequisite for it.

## What $\zeta$ does to the shape

$\omega_n$ sets where the action is; $\zeta$ sets what the action looks like. Keep $L$ and
$C$ as above, so $\omega_n$ is pinned at $10^4$ rad/s, and change only the resistor:

```
R = 200 ohm    zeta = 0.10   peak of 5.025 (+14.02 dB) at 1575.6 Hz, -3 dB at 2455 Hz
R = 1.5 kohm   zeta = 0.75   no peak,                                -3 dB at 1495 Hz
R = 3.0 kohm   zeta = 1.50   no peak, soft rounded corner,           -3 dB at  596 Hz
```

At $\zeta = 0.1$ the output near resonance is five times the input. That is not a mistake
in the arithmetic: at $\omega_n$ the inductor and capacitor impedances cancel exactly, the
loop is left with only its 200 Ω, and the large circulating current develops a voltage
across the capacitor several times bigger than the source. The exact height at $\omega_n$
is $1/2\zeta$, and the true peak, which sits slightly below $\omega_n$ at
$\omega_n\sqrt{1-2\zeta^2}$, is $1/(2\zeta\sqrt{1-\zeta^2})$ — for $\zeta = 0.1$ that is
5.000 and 5.025 respectively, near enough the same thing that $1/2\zeta$ is the number
worth remembering.

The peak appears for any $\zeta < 1/\sqrt2 \approx 0.707$ and vanishes above it.
$\zeta = 1/\sqrt2$ is the flattest a two-pole response can be made — the **maximally flat**
or Butterworth case — and it is the one the build in this module asks for.

## The mistake: assuming the corner is at $\omega_n$

For a single pole there is only one frequency in the problem, so "the corner", "the
$-3$ dB point" and "the pole frequency" are three names for one number. That habit
transfers to second-order systems, where it is wrong, and the table above shows how wrong:
with $\omega_n$ fixed at 1591.5 Hz throughout, the $-3$ dB point moves from 2455 Hz down to
596 Hz — a factor of four — purely by changing the resistor. Read $\omega_n$ off the $-3$
dB point of a lightly damped filter and you will be 54% high.

What does not move is the phase. At $\omega = \omega_n$ the real part of the denominator
is $1 - 1 = 0$ whatever $\zeta$ is, so $H = 1/(j2\zeta)$ and the phase is exactly
$-90^\circ$ — every time, at every damping. That is why the sandbox in this module keeps
pointing at the phase crossing: on a measured response it is the trustworthy way to find
$\omega_n$, and the build's fifth check uses it for precisely that reason.

## Where this stops holding

**Cascading is not multiplication unless the stages are isolated.** This is the one that
costs real designs real performance. Take two identical RC low-passes, $R = 10$ kΩ and
$C = 10$ nF, each with a corner at 1591.5 Hz on its own, and wire the output of the first
straight into the input of the second. The tempting answer is
$H = H_1H_2 = 1/(1 + j\omega RC)^2$, which would put the $-3$ dB point where each stage is
$1.5$ dB down, at 1024 Hz. Solve the actual two-node circuit and the denominator is

$$1 + j\omega(R_1C_1 + R_2C_2 + R_1C_2) - \omega^2R_1C_1R_2C_2 = 1 + 3j\omega RC -
\omega^2R^2C^2$$

The extra $R_1C_2$ cross term is the second capacitor being charged through the first
resistor, and it makes the middle coefficient $3RC$ where the naive product would have
given $2RC$. In standard form that is $\omega_n = 1/RC$ and $\zeta = 1.5$, and the real
corner is at **596 Hz**, not 1024 Hz. At 1024 Hz the circuit passes 0.496 of the input,
not the 0.707 predicted. Nearly a factor of two of error in the corner, from a mistake
that involves no arithmetic at all.

Two standard repairs: make the second stage's impedance ten times the first's, which pushes
the error under a per cent, or put a unity-gain buffer between them, which is the entire
reason a buffer is a product you can buy.

**Real components are not their symbols.** An inductor of 100 mH built out of wire has a
few ohms of winding resistance in series with it, and that resistance adds directly to the
$R$ in $\zeta = \frac{R}{2}\sqrt{C/L}$. In the $\zeta = 0.1$ example above the whole loop
resistance was 200 Ω, so a 10 Ω winding is a 5% error in $\zeta$ and in the height of the
peak; try to build a $\zeta = 0.01$ filter from that inductor and the winding resistance
is most of your damping. Above a few megahertz a capacitor's own series inductance turns
it into an inductor, and $Z_C = 1/(j\omega C)$ stops describing it altogether.

**And all of it assumes LTI and steady state**, for the reasons the previous reading set
out. $H$ is a complete description of a linear time-invariant box driven by something that
has settled — which covers most of electronics, and not the interesting parts of the rest.
''',
                },
            ],
            "sandbox": {
                "title": "Reading a second-order transfer function off its Bode plot",
                "visualiser": "bode",
                "minutes": 10,
                "initial": {"wn": 20, "zeta": 0.7, "K": 1},
                "brief": r'''
The system on display is $H(j\omega) = \dfrac{K}{1 - (\omega/\omega_n)^2 + j2\zeta(\omega/\omega_n)}$
— the standard second-order low-pass, and the transfer function of the series RLC you are
about to design.

The **top** panel is $20\log_{10}|H|$ in decibels against $\omega$ on a logarithmic axis
from 0.1 to 2000 rad/s; the dashed line marks 0 dB and the amber dot marks the response
exactly at $\omega = \omega_n$. The **bottom** panel is the phase in degrees, with its
dashed line at $-90^\circ$.

Three sliders: the corner $\omega_n$, the damping $\zeta$, and the gain $K$.
''',
                "notice": [
                    "It opens at $\\omega_n = 20$, $\\zeta = 0.7$, $K = 1$. The magnitude is flat at 0 dB across the left of the plot, and the amber dot sits about 2.9 dB below that flat line — $20\\log_{10}(1/1.4)$, which is as near the $-3$ dB point as makes no difference. At this damping the corner and the half-power frequency are the same thing.",
                    "Drag $\\zeta$ down to 0.1. A peak grows just before the corner and the amber dot climbs to about $+14$ dB, since it tracks $20\\log_{10}(K/2\\zeta)$. The caption reports the true peak, marginally higher again, because the maximum sits a little below $\\omega_n$ rather than exactly on it. Take $\\zeta$ up to 1.5 instead and the peak is gone, the dot drops to $-9.5$ dB, and the curve rounds off long before the corner.",
                    "Whatever you do to $\\zeta$, the phase curve crosses its dashed $-90^\\circ$ line at exactly $\\omega = \\omega_n$. That is worth trusting: the magnitude corner moves with damping, the phase crossing does not, which makes it the reliable way to read $\\omega_n$ off a measurement.",
                    "Now move $K$ from 1 to 10. The whole magnitude curve lifts by 20 dB and its shape is untouched — and the phase panel does not move at all. Gain and dynamics are independent; $K$ is what a divider or an amplifier in front of the filter would change.",
                    "Put $K$ back to 1 and $\\zeta$ back to 0.7, then read the slope past the corner. At $\\omega = 200$, ten times $\\omega_n$, the magnitude is $-40$ dB; at $\\omega = 2000$, the right-hand edge, it has reached $-80$ dB, which is the bottom of the frame. Forty decibels per decade, twice the slope of the single-pole filter from EE102, because there are two poles rather than one. Leave $K$ at 10 by mistake and both readings are 20 dB higher — the slope is the same, which is the point of the previous paragraph.",
                ],
            },
            "quiz": {
                "title": "Transfer functions, and what they replace",
                "minutes": 10,
                "questions": [
                    {
                        "q": "Why is $e^{j\\omega t}$ singled out as the signal to test an LTI system with?",
                        "opts": [
                            "because it is the only signal for which the convolution integral converges",
                            "because it comes out of an LTI system unchanged except for a complex scale factor, so the system's whole effect is one number per frequency",
                            "because real circuits are driven by sinusoids in practice",
                            "because its Fourier transform is the simplest to compute",
                        ],
                        "a": 1,
                        "why": r'''
It is an eigenfunction: in goes $e^{j\omega t}$, out comes $H(j\omega)e^{j\omega t}$, the
same shape at the same frequency. No other family of inputs behaves this way, and it is
what reduces a convolution to a multiplication. "Real circuits are driven by sinusoids in practice" is true and beside the point:
sinusoids are convenient in the laboratory, but the mathematical privilege belongs to the
complex exponential, of which a sinusoid is a sum of two.
''',
                    },
                    {
                        "q": "A signal with spectrum $X$ is fed through a system with impulse response $h$. Which pair of statements is correct?",
                        "opts": [
                            "$y = h * x$ in time, and $Y = H * X$ in frequency",
                            "$y = hx$ in time, and $Y = HX$ in frequency",
                            "$y = h * x$ in time, and $Y = HX$ in frequency",
                            "$y = hx$ in time, and $Y = H * X$ in frequency",
                        ],
                        "a": 2,
                        "why": r'''
Convolution in one domain is multiplication in the other, and the direction matters:
filtering convolves in time and multiplies in frequency. The pairing runs the other way
too, and module 3 used it — sampling *multiplies* in time by an impulse train, which
*convolves* the spectrum with an impulse train and so copies it. One theorem, two
readings.
''',
                    },
                    {
                        "q": "An RC low-pass has a corner at 1 kHz. What is the phase of its output at 1 kHz, and what is its magnitude a decade above?",
                        "opts": [
                            "$-90^\\circ$, and a tenth",
                            "$-45^\\circ$, and a tenth",
                            "$-45^\\circ$, and a hundredth",
                            "$-45^\\circ$, and a half",
                        ],
                        "a": 1,
                        "why": r'''
At the corner of a single pole, $\omega RC = 1$, so $H = 1/(1 + j)$: magnitude
$1/\sqrt{2}$ and phase $-45^\circ$. A decade past the corner the $j\omega RC$ term
dominates and the magnitude is one tenth — 20 dB per decade, one pole. The answer
$-90^\circ$ belongs to a *second*-order filter at its corner, or to a first-order one far
above it, where the phase asymptotes to $-90^\circ$ without ever quite arriving.
''',
                    },
                    {
                        "q": "A series RLC low-pass is built with $\\zeta = 0.3$. What does its magnitude response look like?",
                        "opts": [
                            "flat, then falling at 20 dB per decade",
                            "flat all the way, because $\\zeta$ only affects phase",
                            "monotonically falling with a soft corner well below $\\omega_n$",
                            "flat, then peaking above the low-frequency level near $\\omega_n$, then falling at 40 dB per decade",
                        ],
                        "a": 3,
                        "why": r'''
Any $\zeta$ below $1/\sqrt{2} \approx 0.707$ gives a peak, and at $\zeta = 0.3$ it is
about $1/(2\zeta\sqrt{1-\zeta^2}) = 1.75$, or $+4.9$ dB above the flat region. Beyond it
the two poles give 40 dB per decade. A monotonic fall with a soft corner describes the *over*damped case, $\zeta > 1$
— the two errors are mirror images, and the sandbox is the fastest way to stop confusing
them.
''',
                    },
                    {
                        "q": "A 1 kHz square wave is passed through a low-pass filter with a corner at 1.5 kHz. What comes out?",
                        "opts": [
                            "a square wave of reduced amplitude but the same shape",
                            "a rounded waveform: the fundamental survives nearly intact while the third, fifth and higher harmonics are progressively attenuated",
                            "nothing, since a square wave contains no 1 kHz component",
                            "a triangle wave, because the filter integrates",
                        ],
                        "a": 1,
                        "why": r'''
The filter multiplies the line spectrum harmonic by harmonic. The 1 kHz fundamental sits
below the corner and gets through; the third harmonic at 3 kHz is already a factor of
$1/\sqrt{1+4} = 0.45$ down, the fifth more so, and it is those harmonics that build the
sharp corners. Losing them rounds the edges. Note what the filter cannot do: it never
introduces a frequency the input did not contain, which is the defining privilege of a
linear system.
''',
                    },
                    {
                        "q": "Two filters are cascaded, the second not loading the first. On a Bode plot, how do their responses combine?",
                        "opts": [
                            "the decibel curves add, and so do the phase curves",
                            "the decibel curves multiply",
                            "the decibel curves add, but the phases must be combined as a vector sum",
                            "only the lower of the two corner frequencies has any effect",
                        ],
                        "a": 0,
                        "why": r'''
Cascading multiplies the transfer functions, $H = H_1H_2$; taking the logarithm turns
that product into a sum of decibels, and the argument of a product is the sum of the
arguments, so the phases add too. This is the entire justification for the logarithmic
axes: it lets a designer sketch a complicated response by adding simple pieces. The
caveat is in the question — "not loading the first" — because a second stage that draws
current changes the first stage's response, and then $H \ne H_1H_2$.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "From the components to the two numbers",
                    "minutes": 8,
                    "caption": "four networks, and the transfer functions they have",
                    "lang": "text",
                    "brief": r'''
No integrals. Every line below is the impedance divider from EE102 with $Z_R = R$,
$Z_C = 1/(j\omega C)$ and $Z_L = j\omega L$ substituted in and the fractions cleared, and
the point of writing them side by side is to see how little changes between them.

The last two lines are the pay-off: the same second-order expression matched term by term
against the standard form, which is where $\omega_n$ and $\zeta$ come from. Watch the
units — one of these is in radians per second and one of them has no units at all.
''',
                    "listing": """  network                                       H(jw) = Vout/Vin
 ------------------------------------------------------------------------------
  R in series, C to ground, probe on C    <->   1 / (1 + ___)

  C in series, R to ground, probe on R    <->   ___

  R and L in series, C to ground          <->   1 / (___ + j w R C)

  the same, in standard form              <->   1 / (1 - (w/wn)^2 + j 2 zeta (w/wn))

       so      wn = ___              and          zeta = ___
""",
                    "blanks": [
                        {
                            "prompt": "The low-pass. Multiply top and bottom of $\\dfrac{1/j\\omega C}{R + 1/j\\omega C}$ by $j\\omega C$ and read off what the denominator becomes.",
                            "hole": "?",
                            "opts": ["w R C", "j w R C", "j w / (R C)", "j w R / C"],
                            "a": 1,
                            "why": "$R \\cdot j\\omega C = j\\omega RC$. The $j$ has to survive, because without it the denominator is real and the filter shifts no phase — and a low-pass that does not lag is not something any capacitor has ever built. At $\\omega RC = 1$ the denominator is $1 + j$, whose magnitude is $\\sqrt2$ and whose angle is $45^\\circ$: the corner, and the $-45^\\circ$ that goes with it.",
                        },
                        {
                            "prompt": "Same two components, swapped over: the capacitor is now in the series arm and the output is taken across the resistor.",
                            "hole": "?",
                            "opts": [
                                "1 / (1 + j w R C)",
                                "j w R C",
                                "j w R C / (1 + j w R C)",
                                "R / (R + j w C)",
                            ],
                            "a": 2,
                            "why": "The divider puts the probed element on top, so the numerator is $R$ rather than $1/j\\omega C$; clearing the fraction the same way gives $j\\omega RC/(1 + j\\omega RC)$. The denominator is identical to the low-pass, so the corner is in the same place — the two responses are complements, and they cross at $1/\\sqrt2$ where each is $-3$ dB. A bare $j\\omega RC$ with no denominator is the *differentiator*, which is what this network approximates only well below the corner.",
                        },
                        {
                            "prompt": "Add an inductor to the series arm. The extra impedance is $j\\omega L$, and clearing the fraction multiplies it by $j\\omega C$.",
                            "hole": "?",
                            "opts": ["1 + w^2 L C", "1 - w^2 L C", "1 - w L C", "1 - w^2 L / C"],
                            "a": 1,
                            "why": "$j\\omega L \\cdot j\\omega C = j^2\\omega^2 LC = -\\omega^2 LC$, and it is the minus sign — nothing else — that makes a second-order response different in kind from two first-order ones. It lets the real part of the denominator reach **zero**, at $\\omega^2 LC = 1$, and everything resonant about this circuit happens there.",
                        },
                        {
                            "prompt": "Match the $\\omega^2$ terms: $(\\omega/\\omega_n)^2$ against $\\omega^2 LC$.",
                            "hole": "?",
                            "opts": ["1 / (L C)", "1 / sqrt(L C)", "sqrt(L C)", "1 / (2 pi sqrt(L C))"],
                            "a": 1,
                            "why": "$1/\\omega_n^2 = LC$, so $\\omega_n = 1/\\sqrt{LC}$ — an *angular* frequency, in radians per second. With $L = 100$ mH and $C = 100$ nF that is $10^4$ rad/s, which is 1591.5 Hz and not 10 000 Hz; $1/(2\\pi\\sqrt{LC})$ is that same corner expressed in hertz, and mixing the two up is the most common way this calculation goes wrong by a factor of $2\\pi$.",
                        },
                        {
                            "prompt": "Now the imaginary terms: $2\\zeta(\\omega/\\omega_n)$ against $\\omega RC$, with $\\omega_n = 1/\\sqrt{LC}$ already known.",
                            "hole": "?",
                            "opts": [
                                "(R/2) sqrt(C/L)",
                                "(R/2) sqrt(L/C)",
                                "R sqrt(C/L)",
                                "2 R sqrt(C/L)",
                            ],
                            "a": 0,
                            "why": "The $\\omega$ cancels, leaving $2\\zeta = RC\\omega_n = RC/\\sqrt{LC} = R\\sqrt{C/L}$, so $\\zeta = \\frac{R}{2}\\sqrt{C/L}$. It is dimensionless, and it is the only one of the two numbers the resistor appears in — which is what lets a design fix the corner with $L$ and $C$ and then set the shape with $R$ without disturbing it. Inverting the fraction to $\\sqrt{L/C}$ gives a $\\zeta$ that rises when the inductor grows, and a bigger inductor stores more energy per cycle and damps *less*.",
                        },
                    ],
                },
                {
                    "title": "Decibels, and the arithmetic a Bode plot exists for",
                    "minutes": 7,
                    "caption": "five quantities every one of which is quoted in dB in practice",
                    "lang": "text",
                    "brief": r'''
A decibel is $20\log_{10}$ of a voltage ratio. That is the whole definition, and the
factor of 20 rather than 10 is because the ratio being quoted is a voltage and the decibel
was defined on power, which goes as voltage squared.

The reason to work in them is that a cascade multiplies transfer functions, and logarithms
turn a product into a sum. Every line below is a number you will end up quoting from
memory, so it is worth getting them fixed now rather than reaching for a calculator each
time.
''',
                    "listing": """  quantity                                                        in decibels
 --------------------------------------------------------------------------------
  a voltage ratio of 1/sqrt(2)                                     ___

  a voltage ratio of 100                                           ___

  one pole, a decade above its corner                              ___

  two poles, an octave above the corner                            ___

  a stage at -15.5 dB driving an amplifier of gain 2               ___
""",
                    "blanks": [
                        {
                            "prompt": "The half-power point, where every corner frequency in this course is defined.",
                            "hole": "?",
                            "opts": ["-0.5 dB", "-1.5 dB", "-3.01 dB", "-6.02 dB"],
                            "a": 2,
                            "why": "$20\\log_{10}(0.70711) = -3.01$ dB. It is called the half-power point because power goes as the square of voltage and $(1/\\sqrt2)^2 = 1/2$ — the same physical point, quoted as $-3$ dB whether the instrument is measuring volts or watts, which is the whole convenience of the definition.",
                            "whys": [
                                "That is a ratio of 0.944, which is a hair off flat rather than the half-power point.",
                                "That is $2^{-1/4} = 0.841$, which is what *each* of two cascaded stages is down when the pair together reaches $-3$ dB. A useful number, and not this one.",
                                "$20\\log_{10}(0.70711) = -3.01$ dB. It is called the half-power point because power goes as the square of voltage and $(1/\\sqrt2)^2 = 1/2$ — the same physical point, quoted as $-3$ dB whether the instrument is measuring volts or watts, which is the whole convenience of the definition.",
                                "$-6.02$ dB is a ratio of one half in *voltage*, which is a quarter of the power. Confusing it with the half-power point is the commonest decibel error there is, and it comes from forgetting whether the 10 or the 20 applies.",
                            ],
                        },
                        {
                            "prompt": "An amplifier that turns 10 mV into 1 V.",
                            "hole": "?",
                            "opts": ["+10 dB", "+20 dB", "+40 dB", "+100 dB"],
                            "a": 2,
                            "why": "$20\\log_{10}(100) = 40$ dB. Every factor of ten in voltage is 20 dB, so a factor of a hundred is two of them added — which is the sense in which decibels count powers of ten rather than sizes.",
                            "whys": [
                                "That is the *power* decibel value of a ratio of 10, and two errors have been made that partly cancel. Voltage ratios take the factor of 20.",
                                "$+20$ dB is a ratio of ten, not a hundred. One decade of gain short.",
                                "$20\\log_{10}(100) = 40$ dB. Every factor of ten in voltage is 20 dB, so a factor of a hundred is two of them added — which is the sense in which decibels count powers of ten rather than sizes.",
                                "That would be a ratio of $10^5$. Reading the number 100 straight into the decibel column is the arithmetic slipping out of the calculation altogether.",
                            ],
                        },
                        {
                            "prompt": "Far past the corner a single pole falls as $1/\\omega$. What has ten times the frequency cost?",
                            "hole": "?",
                            "opts": ["-6 dB", "-10 dB", "-20 dB", "-40 dB"],
                            "a": 2,
                            "why": "A decade past the corner $|H| \\to f_c/f = 0.1$, and $20\\log_{10}(0.1) = -20$ dB. This is the asymptote rather than the exact value: the true magnitude a decade out is $1/\\sqrt{101} = 0.0995$, or $-20.04$ dB, so the straight line is wrong by four hundredths of a decibel and nobody has ever cared.",
                            "whys": [
                                "$-6$ dB is one pole per *octave*, a factor of two in frequency, not a factor of ten.",
                                "$-10$ dB is a factor of ten in power, which would be the right answer if the quantity plotted were watts. On a voltage Bode plot the factor is 20.",
                                "A decade past the corner $|H| \\to f_c/f = 0.1$, and $20\\log_{10}(0.1) = -20$ dB. This is the asymptote rather than the exact value: the true magnitude a decade out is $1/\\sqrt{101} = 0.0995$, or $-20.04$ dB, so the straight line is wrong by four hundredths of a decibel and nobody has ever cared.",
                                "$-40$ dB per decade belongs to *two* poles. One pole gives half of it, and the difference between the two slopes is the entire argument for the second-order filter this module builds.",
                            ],
                        },
                        {
                            "prompt": "An octave is a factor of two in frequency, and $\\log_{10} 2 = 0.301$ of a decade.",
                            "hole": "?",
                            "opts": ["-6.02 dB", "-12.04 dB", "-20 dB", "-40 dB"],
                            "a": 1,
                            "why": "Two poles fall at 40 dB per decade, and an octave is $0.301$ of a decade, so $40 \\times 0.301 = 12.04$ dB per octave. The pair of numbers worth memorising is that one pole is 20 dB/decade or 6 dB/octave, and every further pole adds another of each.",
                            "whys": [
                                "That is one pole per octave. Two poles double it.",
                                "Two poles fall at 40 dB per decade, and an octave is $0.301$ of a decade, so $40 \\times 0.301 = 12.04$ dB per octave. The pair of numbers worth memorising is that one pole is 20 dB/decade or 6 dB/octave, and every further pole adds another of each.",
                                "$-20$ dB is one pole per decade — right slope, wrong number of poles and wrong interval, which is two errors rather than one.",
                                "$-40$ dB is what two poles give over a full decade. An octave is less than a third of a decade, so the fall over it is correspondingly smaller.",
                            ],
                        },
                        {
                            "prompt": "The cascade, which is the reason for using decibels at all.",
                            "hole": "?",
                            "opts": ["-31.0 dB", "-21.5 dB", "-9.5 dB", "-12.5 dB"],
                            "a": 2,
                            "why": "Gain of 2 is $+6.02$ dB, and cascading adds: $-15.5 + 6.02 = -9.5$ dB, a ratio of 0.334. Adding is legitimate only because the stages multiply, and they multiply only if the amplifier does not load the filter — which is exactly what an amplifier with a high input impedance is for.",
                            "whys": [
                                "That is $-15.5$ doubled, which is what happens if the *decibel* figure is multiplied by the gain rather than the ratio it stands for. Doubling a decibel value squares the ratio.",
                                "That is $-15.5 - 6.02$: the amplifier has been cascaded in with the wrong sign, turning a gain of two into an attenuation of two.",
                                "Gain of 2 is $+6.02$ dB, and cascading adds: $-15.5 + 6.02 = -9.5$ dB, a ratio of 0.334. Adding is legitimate only because the stages multiply, and they multiply only if the amplifier does not load the filter — which is exactly what an amplifier with a high input impedance is for.",
                                "That is $-15.5 + 3.0$: the gain of two was converted with $10\\log_{10}$, the power convention, giving 3 dB instead of the 6 that a voltage ratio takes. The same factor has to be used on both stages.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "One pole, one frequency, in decibels",
                    "minutes": 5,
                    "brief": r'''
The mechanical one. A single $R$ and a single $C$, and a single number wanted, so that the
sequence — corner first, then the ratio, then the logarithm — is under your fingers before
anything harder is stacked on top of it.

Nothing here needs the impulse response, the convolution integral or the transfer function
written as an integral. It is $H = 1/(1 + j\omega RC)$ and a calculator.
''',
                    "prompt": "What is the response of this filter at 20 kHz, expressed in decibels?",
                    "note": "Give the answer in dB, to two decimal places. It is negative.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                            {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 4700},
                            {"id": "p3", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-8},
                            {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                            {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 4], "b": [11, 4]},
                        ],
                    },
                    # The source is 1 V, so the probed magnitude is |H| directly; dividing by
                    # the source value anyway means the answer survives someone editing it.
                    "check": r'''
return 20 * Math.log10(c.gain(20000) / c.values('V')[0]);
''',
                    "given": [
                        {"label": "$R$", "value": "4.7 kΩ"},
                        {"label": "$C$", "value": "10 nF"},
                        {"label": "Source", "value": "1 V sinusoid at 20 kHz"},
                        {"label": "Wanted", "value": "$20\\log_{10}|H|$ at 20 kHz"},
                    ],
                    "aside": "20 kHz is not a decade above the corner, so the $-20$ dB asymptote is "
                             "not the answer. Work out where the corner actually is first.",
                    "answer": -15.55,
                    "tol": 0.1,
                    "unit": "dB",
                    "hint": "$f_c = 1/(2\\pi RC)$, then $|H| = 1/\\sqrt{1 + (f/f_c)^2}$, then "
                            "$20\\log_{10}$ of that. Three steps, in that order.",
                    "wrong": "If you got $+15.55$, the ratio went in upside down — a passive low-pass "
                             "cannot have positive gain at any frequency. If you got $-7.77$, the "
                             "logarithm was multiplied by 10 rather than 20, which is the power "
                             "convention applied to a voltage. If you got $-2.75$, the corner was "
                             "taken as $1/RC$ in hertz instead of $1/(2\\pi RC)$, which puts it at "
                             "21.3 kHz and leaves 20 kHz sitting below it.",
                    "why": r'''
```
corner        fc = 1/(2 pi R C)
                 = 1/(2 pi * 4700 * 10e-9)
                 = 3386.3 Hz

ratio         f/fc = 20000 / 3386.3 = 5.9062
              |H|  = 1/sqrt(1 + 5.9062^2)
                   = 1/sqrt(35.883)
                   = 1/5.9902 = 0.16694

decibels      20 log10(0.16694) = -15.55 dB
```

Worth checking against the asymptote, because that is how the number gets sanity-checked
in practice. 20 kHz is $\log_{10}(5.9062) = 0.771$ of a decade above the corner, and one
pole falls at 20 dB per decade, so the straight-line estimate is $-15.43$ dB. The exact
answer is $-15.55$ dB: a tenth of a decibel apart, and that gap closes fast — by a full
decade out the asymptote is wrong by only 0.04 dB.

The other direction is worth a moment too. At 20 kHz this filter passes 16.7% of what
arrives, which sounds like a lot of rejection until you compare it with what the same
components have to do to a signal at 40 kHz: $|H|$ there is 0.0844, smaller by only a
factor of two. One pole is a gentle thing, and a requirement written as "reject everything above
20 kHz" cannot be met with one.
''',
                },
                {
                    "title": "The voltage that comes out larger than it went in",
                    "minutes": 8,
                    "brief": r'''
A passive network made of a resistor, an inductor and a capacitor, driven by a 1 V source.
Nothing in it can generate energy. Ask what the probe reads when the source is set to the
circuit's natural frequency $\omega_n = 1/\sqrt{LC}$, and the honest first guess — that a
passive filter cannot give back more than it was given — turns out to be wrong.

Two steps: find $\zeta$ from the components, then evaluate the standard form at
$\omega = \omega_n$, where it collapses to something very short.
''',
                    "prompt": "The source is set to $f_n = \\omega_n/2\\pi$. What amplitude appears at the probe?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                            {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1000},
                            {"id": "p3", "kind": "L", "x": 10, "y": 4, "rot": 0, "value": 0.1},
                            {"id": "p4", "kind": "C", "x": 13, "y": 6, "rot": 1, "value": 1e-8},
                            {"id": "p5", "kind": "GND", "x": 13, "y": 9},
                            {"id": "p6", "kind": "OUT", "x": 15, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [13, 4], "b": [13, 5]},
                            {"a": [13, 7], "b": [13, 9]},
                            {"a": [13, 4], "b": [15, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [11, 4], "b": [13, 4]},
                        ],
                    },
                    # omega_n is computed from the L and C actually on the canvas rather than
                    # from a number repeated out of the prompt, so the check follows the drawing.
                    "check": r'''
const L = c.values('L')[0];
const C = c.values('C')[0];
return c.gain(1 / (2 * Math.PI * Math.sqrt(L * C)));
''',
                    "given": [
                        {"label": "$R$", "value": "1.0 kΩ"},
                        {"label": "$L$", "value": "100 mH"},
                        {"label": "$C$", "value": "10 nF"},
                        {"label": "Source", "value": "1.0 V, at $f_n$"},
                    ],
                    "aside": "At $\\omega = \\omega_n$ the real part of the denominator, "
                             "$1 - (\\omega/\\omega_n)^2$, is exactly zero. Whatever is left is "
                             "purely imaginary, and its size is the whole answer.",
                    "answer": 3.16,
                    "tol": 0.03,
                    "unit": "V",
                    "hint": "$\\omega_n = 1/\\sqrt{LC}$ and $\\zeta = \\frac{R}{2}\\sqrt{C/L}$. Put "
                            "$\\omega = \\omega_n$ into $H = 1/(1 - (\\omega/\\omega_n)^2 + "
                            "j2\\zeta(\\omega/\\omega_n))$ and almost everything cancels.",
                    "wrong": "If you got 1.00, the assumption was that a passive network cannot "
                             "exceed its input — true of the *energy* over a cycle, and not true of "
                             "the voltage at one node. If you got 0.71, $f_n$ was treated as the "
                             "$-3$ dB point, which it is only when $\\zeta = 1/\\sqrt2$ and this "
                             "circuit is nowhere near that. If you got 0.32, the answer came out as "
                             "$2\\zeta$ rather than $1/2\\zeta$.",
                    "why": r'''
```
natural frequency   wn   = 1/sqrt(L C) = 1/sqrt(0.1 * 10e-9)
                         = 1/sqrt(1e-9) = 31623 rad/s   ->  fn = 5032.9 Hz

damping             zeta = (R/2) sqrt(C/L)
                         = 500 * sqrt(10e-9 / 0.1)
                         = 500 * 3.1623e-4 = 0.15811

at w = wn           1 - (w/wn)^2 = 0, so  H = 1/(j 2 zeta)
                    |H| = 1/(2 * 0.15811) = 3.1623

output              1.0 V * 3.1623 = 3.16 V
```

Three times the source, out of three passive components. The physical account is worth
having: at $\omega_n$ the inductor's $+j\omega L = +j3162$ Ω and the capacitor's
$-j/(\omega C) = -j3162$ Ω cancel exactly, so the loop is left with nothing but its 1 kΩ
resistor. The current is therefore $1\ \text{V}/1\ \text{k}\Omega = 1$ mA, and that
milliamp flowing through 3162 Ω of capacitive reactance develops 3.16 V across it. The
inductor carries an equal and opposite 3.16 V, the two cancel in the loop, and no energy
has been created — it is being passed back and forth between $L$ and $C$ many times per
cycle while the source only tops up the losses.

That factor, $1/2\zeta$, is the circuit's **$Q$**, and module 7 is about what it is good
for and what it costs. Two footnotes for now. The number is exact at $\omega_n$ but it is
not quite the peak: the true maximum is $1/(2\zeta\sqrt{1-\zeta^2}) = 3.20$, at
4905 Hz, about 2.5% below $\omega_n$. And 3.16 V across a capacitor rated for the 1 V
supply is how a resonant circuit destroys a component that looked comfortably specified.
''',
                },
                {
                    "title": "Which harmonic arrives first",
                    "minutes": 10,
                    "brief": r'''
Back to one pole; the circuit is the easy part here. What is new is the quantity being
asked for, which is a time rather than a voltage, and which the magnitude response knows
nothing about.

A 1 kHz square wave is applied to the filter below. Its fundamental sits at 1 kHz and its
third harmonic at 3 kHz, and each is shifted in phase by a different amount on the way
through. Phase is not time, so a division is needed before the two can be compared.
''',
                    "prompt": "By how much longer is the fundamental delayed than the third harmonic?",
                    "note": "Give the answer in microseconds, to one decimal place.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                            {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 12000},
                            {"id": "p3", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-8},
                            {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                            {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 4], "b": [11, 4]},
                        ],
                    },
                    # Phase delay at each harmonic, -angle/omega, differenced; measured off the
                    # solver's own phase so the sign convention is the app's rather than mine.
                    "check": r'''
const delay = function (f) { return -c.phase(f) * (Math.PI / 180) / (2 * Math.PI * f); };
return (delay(1000) - delay(3000)) * 1e6;
''',
                    "given": [
                        {"label": "$R$", "value": "12 kΩ"},
                        {"label": "$C$", "value": "10 nF"},
                        {"label": "Input", "value": "square wave, 1 kHz"},
                        {"label": "Wanted", "value": "$t_1 - t_3$, in µs"},
                    ],
                    "aside": "The delay a phase shift represents is $-\\angle H/\\omega$. The "
                             "amplitude of the square wave never enters this calculation, and "
                             "neither do the Fourier coefficients — only the two frequencies do.",
                    "answer": 41.6,
                    "tol": 0.4,
                    "unit": "µs",
                    "hint": "Find $\\angle H$ at 1 kHz and at 3 kHz from "
                            "$\\angle H = -\\arctan(f/f_c)$, convert each to radians, divide each "
                            "by its own $\\omega = 2\\pi f$, and subtract.",
                    "wrong": "If you got 29.1, that is the difference in *degrees*, 66.15 − 37.02, "
                             "reported without ever being turned into a time. If you got a negative "
                             "number, the third harmonic was taken to be delayed more because its "
                             "phase shift is larger — larger in angle, smaller in time, and the "
                             "whole point of the question. If you got 40.5, you divided the "
                             "difference in phase by the difference in frequency, which is a real "
                             "and useful quantity called the group delay and is not what was asked.",
                    "why": r'''
```
corner       fc = 1/(2 pi * 12e3 * 10e-9) = 1326.29 Hz

fundamental, 1 kHz
   angle  = -atan(1000/1326.29) = -37.02 deg = -0.64604 rad
   delay  = 0.64604 / (2 pi * 1000) = 102.82 us

third harmonic, 3 kHz
   angle  = -atan(3000/1326.29) = -66.15 deg = -1.15453 rad
   delay  = 1.15453 / (2 pi * 3000) =  61.25 us

difference   102.82 - 61.25 = 41.6 us
```

The harmonic with the *larger* phase shift is delayed by the *smaller* time, and that
inversion is what makes the question worth asking. A first-order low-pass has a phase that
flattens out towards $-90^\circ$; once the angle has stopped growing, dividing by an
$\omega$ that keeps growing sends the delay towards zero.

Put it in terms of the waveform. The fundamental's period is 1000 µs and the third
harmonic's is 333 µs, so the fundamental slips back by a tenth of its own cycle and the
harmonic by nearly a fifth of its own — but measured on the same clock, they have moved
apart by 41.6 µs, which is an eighth of the harmonic's period. They were lined up crest to
crest at the input and they are not at the output. The square wave that comes out is not
merely a rounded version of the one that went in; its parts have been shuffled.

The alternative measure named in the note above is the **group delay**,
$-d\angle H/d\omega$, which is what matters when the signal is a modulated packet rather
than a set of harmonics. Approximated across this interval it is 40.5 µs, close to the
41.6 µs here only because the two frequencies are close together on a logarithmic axis;
the two quantities agree exactly only for a system with genuinely linear phase, which is
to say a pure delay.
''',
                },
                {
                    "title": "Two poles against the third harmonic",
                    "minutes": 12,
                    "brief": r'''
The last rung, and the one that pays off the module. Module 2 sent a 1 kHz square wave
through a single-pole filter and found that the third harmonic came out at 16.9% of the
fundamental, against 33.3% at the input — halved, and no better than halved, because one
pole is not steep enough to separate two frequencies that are only a factor of three
apart.

Here is the same problem given a second pole. Four separate results have to be assembled:
the frequency of the harmonic, its amplitude at the input, $\omega_n$ and $\zeta$ from the
three components, and the second-order magnitude at that frequency.
''',
                    "prompt": "What is the amplitude of the third harmonic where it reaches the probe?",
                    "note": "Give the answer in millivolts, to the nearest millivolt.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 2},
                            {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                            {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1500},
                            {"id": "p3", "kind": "L", "x": 10, "y": 4, "rot": 0, "value": 0.1},
                            {"id": "p4", "kind": "C", "x": 13, "y": 6, "rot": 1, "value": 1e-7},
                            {"id": "p5", "kind": "GND", "x": 13, "y": 9},
                            {"id": "p6", "kind": "OUT", "x": 15, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [13, 4], "b": [13, 5]},
                            {"a": [13, 7], "b": [13, 9]},
                            {"a": [13, 4], "b": [15, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [11, 4], "b": [13, 4]},
                        ],
                    },
                    # The square wave's amplitude is read off the source symbol, and |H| at 3 kHz
                    # is measured rather than recomputed, so the answer tracks the drawing.
                    "check": r'''
const A = c.values('V')[0];        /* the square wave's amplitude, off the source symbol */
const H3 = c.gain(3000) / A;       /* |H| at the third harmonic */
return (4 * A / (3 * Math.PI)) * H3 * 1000;
''',
                    "given": [
                        {"label": "Source", "value": "square wave, $\\pm 2$ V, 1 kHz"},
                        {"label": "$R$", "value": "1.5 kΩ"},
                        {"label": "$L$", "value": "100 mH"},
                        {"label": "$C$", "value": "100 nF"},
                    ],
                    "aside": "The generator is drawn as a 2 V source because 2 V is the square "
                             "wave's amplitude, not because it is a sinusoid. Superposition is what "
                             "licenses pushing one harmonic through on its own.",
                    "answer": 222.8,
                    "tol": 2.0,
                    "unit": "mV",
                    "hint": "The third harmonic of a square wave of amplitude $A$ is $4A/(3\\pi)$ at "
                            "$3f_0$. Then $\\omega_n = 1/\\sqrt{LC}$, $\\zeta = "
                            "\\frac{R}{2}\\sqrt{C/L}$, and $|H| = 1/\\sqrt{(1-u^2)^2 + (2\\zeta "
                            "u)^2}$ with $u = \\omega/\\omega_n$. Multiply the two.",
                    "wrong": "If you got 849, the filter was left out entirely — that is the third "
                             "harmonic as it arrives. If you got 398, a first-order magnitude was "
                             "used where the circuit has two poles: $1/\\sqrt{1+u^2}$ instead of the "
                             "full expression. If you got 758, $|H|$ was evaluated at 1 kHz instead "
                             "of at the harmonic's own 3 kHz. If you got 2270, that is the "
                             "fundamental at the output rather than the third harmonic.",
                    "why": r'''
```
the harmonic       f3 = 3 kHz,  b3 = 4A/(3 pi) = 8/(3 pi) = 0.84883 V

the filter         wn   = 1/sqrt(0.1 * 100e-9) = 1/sqrt(1e-8) = 1e4 rad/s
                   fn   = 1591.5 Hz
                   zeta = (1500/2) * sqrt(100e-9/0.1) = 750 * 1e-3 = 0.75

at 3 kHz           u        = 3000/1591.5 = 1.88496
                   1 - u^2  = 1 - 3.55306 = -2.55306
                   2 zeta u = 1.5 * 1.88496 = 2.82743
                   |H|      = 1/sqrt(2.55306^2 + 2.82743^2)
                            = 1/sqrt(14.5125) = 1/3.80953 = 0.26250

multiply           0.84883 V * 0.26250 = 0.22282 V = 222.8 mV
```

Now run the fundamental through the same filter to see what has been bought. At 1 kHz,
$u = 0.6283$, and the same expression gives $|H| = 0.89280$, so the 2.5465 V fundamental
arrives at 2.2735 V. The ratio of third harmonic to fundamental is $222.8/2273.5 = 9.8\%$
at the output, against $33.3\%$ at the input.

Set the three numbers side by side:

```
                                    third harmonic / fundamental
   at the input                                33.3%
   after module 2's one pole                   16.9%
   after this module's two poles                9.8%
```

The second pole roughly halves it again, and it does so while the fundamental is still
being passed at 89% rather than the 79.8% the single-pole filter managed. Better
rejection *and* less damage to the wanted signal, from adding one component — which is the
argument for higher-order filters in a sentence, and the reason the build in this module
asks for two poles rather than one.

One warning about how far that argument goes. The improvement came from the response
falling at 40 dB per decade instead of 20, and 3 kHz is only 1.9 times $\omega_n$, where
the asymptotic slope has barely taken hold. Doubling the order again would help less than
this step did, and every extra pole adds phase lag — 132° here already, against the 66°
of the single-pole filter at the same frequency — which is precisely the kind of shuffling
the previous question measured.
''',
                },
            ],
            "derive": {
                "title": "Where $\\omega_n$ and $\\zeta$ come from",
                "minutes": 14,
                "vars": ["omega", "L", "C", "R", "j", "omega_n", "zeta", "H"],
                "brief": r'''
A resistor, an inductor and a capacitor in series across a source, with the output taken
across the capacitor. This is the circuit you are about to build, and the aim is to get
from three component values to the two numbers — $\omega_n$ and $\zeta$ — that the Bode
plot is drawn from.

No new theory is needed. It is the impedance divider from EE102, written out and tidied.
''',
                "steps": [
                    {
                        "prompt": "Write the impedance of the capacitor at angular frequency $\\omega$.",
                        "answer": "\\frac{1}{j\\omega C}",
                        "hint": "The current through a capacitor is $C\\,dv/dt$, and differentiating $e^{j\\omega t}$ multiplies by $j\\omega$.",
                        "deconstruct": [
                            "$i = C\\frac{dv}{dt}$ becomes $I = j\\omega C V$ for a complex exponential.",
                            "Impedance is $V/I$, so it is the reciprocal of $j\\omega C$.",
                        ],
                    },
                    {
                        "prompt": "The three parts carry the same current, so this is an impedance divider. Write $H = V_{out}/V_{in}$ as the capacitor's impedance over the total, without simplifying.",
                        "given": "The three impedances are $R$, $j\\omega L$ and the one you just wrote.",
                        "answer": "\\frac{\\frac{1}{j\\omega C}}{R + j\\omega L + \\frac{1}{j\\omega C}}",
                        "hint": "Exactly the resistive divider of EE101 with impedances in place of resistances: the part you measure across goes on top, the whole series chain underneath.",
                        "deconstruct": [
                            "In a series chain the same current flows, so voltages split in proportion to impedance.",
                            "The output is across the capacitor, so its impedance is the numerator.",
                        ],
                    },
                    {
                        "prompt": "Multiply top and bottom by $j\\omega C$ and write the tidied $H$.",
                        "answer": "\\frac{1}{1 - \\omega^{2} L C + j \\omega R C}",
                        "hint": "The numerator becomes 1. In the denominator, $j\\omega L \\cdot j\\omega C = j^2\\omega^2 LC = -\\omega^2 LC$.",
                        "deconstruct": [
                            "$\\frac{1}{j\\omega C}\\cdot j\\omega C = 1$, which clears the fraction on top.",
                            "$R\\cdot j\\omega C = j\\omega RC$, and $j\\omega L\\cdot j\\omega C = -\\omega^2 LC$ because $j^2 = -1$.",
                        ],
                    },
                    {
                        "prompt": "The standard form is $H = \\dfrac{1}{1 - (\\omega/\\omega_n)^2 + j2\\zeta(\\omega/\\omega_n)}$. Matching the $\\omega^2$ terms, write $\\omega_n$ in terms of $L$ and $C$.",
                        "answer": "\\frac{1}{\\sqrt{L C}}",
                        "hint": "You need $\\omega^2/\\omega_n^2 = \\omega^2 LC$, so $\\omega_n^2 = 1/(LC)$.",
                        "deconstruct": [
                            "Compare $(\\omega/\\omega_n)^2$ with $\\omega^2 LC$: they must be equal for all $\\omega$.",
                            "So $1/\\omega_n^2 = LC$, and take the positive square root.",
                        ],
                    },
                    {
                        "prompt": "Now match the imaginary terms and write $\\zeta$ in terms of $R$, $L$ and $C$.",
                        "given": "You need $2\\zeta\\,\\omega/\\omega_n = \\omega R C$, with $\\omega_n = 1/\\sqrt{LC}$.",
                        "answer": "\\frac{R}{2}\\sqrt{\\frac{C}{L}}",
                        "hint": "The $\\omega$ cancels, leaving $2\\zeta = RC\\omega_n = RC/\\sqrt{LC}$. Simplify $C/\\sqrt{LC}$.",
                        "deconstruct": [
                            "Divide both sides by $\\omega$: $2\\zeta/\\omega_n = RC$, so $2\\zeta = RC\\omega_n$.",
                            "Substitute $\\omega_n = 1/\\sqrt{LC}$: $2\\zeta = RC/\\sqrt{LC} = R\\sqrt{C/L}$.",
                        ],
                    },
                ],
                "closing": r'''
Two component-value formulas, and every feature of the Bode plot follows from them.
Notice that $\zeta$ depends on $R$ but $\omega_n$ does not: you can move the corner with
$L$ and $C$ and then set the damping with the resistor alone, without disturbing it.

For the maximally flat design, $\zeta = 1/\sqrt{2}$ gives $R = \sqrt{2L/C}$ — a number
you will now type into the schematic editor.
''',
            },
            "build": {
                "title": "Two poles, and the decade that pays for them",
                "minutes": 30,
                "brief": r'''
The single-pole filter of module 3 could not reach a factor of ten at ten times the band
edge. This one can reach a factor of a hundred, because it has two poles.

Build a **series RLC low-pass** — resistor and inductor in series from the source, output
taken across a capacitor to ground — with the following measured behaviour. A 1 µF
capacitor and a ground are already on the canvas; connect the source to it through the
two parts that are missing, and put the probe on the output node. You may change the
capacitor if you prefer; only the measurements count.

1. **Unity at DC.** At 1 Hz the output must be within 2% of the input.
2. **Corner at 1 kHz.** The frequency at which the output falls to $1/\sqrt{2}$ of its
   low-frequency value must be 1 kHz, within 5%.
3. **Flat below it.** Nowhere between 10 Hz and 900 Hz may the response rise more than
   2% above its low-frequency value. No resonant peak.
4. **Forty decibels per decade.** At 10 kHz the output must be about **one hundredth** of
   its low-frequency value, within 25%.
5. **Ninety degrees at the corner.** The output must lag the input by $90^\circ$ at
   1 kHz, within about six degrees.

## What the requirements are really saying

The derivation gives $\omega_n = 1/\sqrt{LC}$ and $\zeta = \frac{R}{2}\sqrt{C/L}$.
Requirement 5 pins $\omega_n$, because the phase passes through $-90^\circ$ at
$\omega = \omega_n$ for **any** damping. Requirement 2 then says the $-3$ dB point sits at
$\omega_n$ as well, and that happens at exactly one value of $\zeta$. Requirements 3 and 4
are the same statement seen from two other directions, and a design that satisfies 2 and 5
will satisfy them.

So: choose $L$ from $\omega_n = 2\pi \times 1000$ and the capacitor you are using, then
choose $R$ from the damping. Round numbers are not expected — type what the algebra gives.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "C", "x": 13, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p3", "kind": "GND", "x": 13, "y": 9},
                        {"id": "p4", "kind": "OUT", "x": 15, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 4], "b": [15, 4]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "C", "x": 13, "y": 6, "rot": 1, "value": 1e-6},
                        {"id": "p3", "kind": "GND", "x": 13, "y": 9},
                        {"id": "p4", "kind": "OUT", "x": 15, "y": 4},
                        {"id": "p5", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 225.0790790392765},
                        {"id": "p6", "kind": "L", "x": 10, "y": 4, "rot": 0, "value": 0.025330295910584444},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 4], "b": [15, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [11, 4], "b": [13, 4]},
                    ],
                },
                "checks": [
                    {"name": "one source, and the output follows it at DC", "code": r'''
c.assert(c.count('V') === 1, 'Drive the filter from exactly one source; found ' + c.count('V') + '.');
const vs = c.values('V')[0];
const dc = c.gain(1);
c.close(dc, vs, 0.02,
  'the output at 1 Hz — at low frequency the inductor is a short and the capacitor an ' +
  'open, so the whole input should appear at the probe');
'''},
                    {"name": "the corner is at 1 kHz", "code": r'''
c.close(c.corner(10, 1e6), 1000, 0.05,
  'the frequency where the output falls to 1/sqrt(2) of its low-frequency value');
'''},
                    {"name": "the passband is flat — no resonant peak", "code": r'''
const ref = c.gain(10);
const vs = c.values('V')[0];
c.assert(ref > 0.5 * vs,
  'At 10 Hz the probe reads ' + (ref / vs * 100).toFixed(1) + '% of the source voltage. ' +
  'Almost nothing is reaching the output node, so there is no passband to measure — ' +
  'check that the source is wired through to it.');
let worst = 0, at = 0;
for (let i = 0; i <= 30; i++) {
  const f = Math.pow(10, 1 + i / 30 * Math.log10(90));
  const r = c.gain(f) / ref;
  if (r > worst) { worst = r; at = f; }
}
c.assert(worst <= 1.02,
  'The response peaks to ' + worst.toFixed(3) + ' times its low-frequency value near ' +
  at.toFixed(0) + ' Hz. That is a resonance: the damping is too low, so the resistor is ' +
  'too small.');
'''},
                    {"name": "two poles: a hundredfold cut a decade past the corner", "code": r'''
const ref = c.gain(10);
const r = c.gain(10000) / ref;
c.close(r, 0.01, 0.25,
  'the response at 10 kHz relative to the passband — two poles give 40 dB per decade, ' +
  'so ten times past a 1 kHz corner should be about one hundredth');
'''},
                    {"name": "the output lags by 90 degrees at the corner", "code": r'''
c.close(c.phase(1000), -90, 0.07,
  'the phase at 1 kHz — it passes through -90 degrees exactly at omega_n, so this ' +
  'measures whether your natural frequency is where you meant it to be');
'''},
                ],
                "hints": [
                    "$\\omega_n = 2\\pi \\times 1000 = 6283.2$ rad/s. With $C = 1$ µF, $L = 1/(\\omega_n^2 C)$, which comes to about 25.3 mH.",
                    "Requirements 2 and 3 together mean the maximally flat case, $\\zeta = 1/\\sqrt{2}$. From the derivation, $R = 2\\zeta\\sqrt{L/C} = \\sqrt{2L/C}$.",
                    "With $L = 25.33$ mH and $C = 1$ µF that gives $R \\approx 225$ Ω. Type `25.33m` for the inductor and `225` for the resistor.",
                    "If the passband check reports a peak, the resistance is too low — damping rises with $R$. If the corner is in the wrong place, it is $L$ or $C$ that needs changing, not $R$.",
                    "Order does not matter: resistor then inductor, or inductor then resistor, gives the same series impedance. What does matter is that the output is taken across the capacitor and the probe sits on that node.",
                ],
            },
        },

        # ---- M5 -----------------------------------------------------------
        {
            "title": "The signals themselves: size, symmetry and the operations that reshape them",
            "summary": "Four modules of systems, and the objects they act on have been taken on trust. Three things used loosely so far are about to be needed exactly.",
            "concepts": [
                "Notation first, because it is load-bearing. $x(t)$ is a continuous-time signal and $t$ is a real number; $x[n]$ is a discrete-time signal and $n$ is an integer. The square brackets are not decoration — they are the reason module 1 could write a convolution as a sum in one line and an integral in the next.",
                "Three operations act on the **argument** rather than on the value. $x(t - t_0)$ is a **delay** by $t_0$; $x(-t)$ is a **reflection**; $x(at)$ with $a > 1$ is a **compression** towards the origin. Only the first of these is something an LTI system may do.",
                "Combined arguments are read by solving, not by pattern matching. $x(2t - 6)$ is non-zero wherever $x$ is, so if $x$ lives on $0 \\le u \\le 1$ then $0 \\le 2t - 6 \\le 1$, giving $3 \\le t \\le 3.5$: compressed by two **and delayed by 3, not by 6**. Write the argument, set it to each landmark, solve for $t$.",
                "**Even** means $x(-t) = x(t)$ and **odd** means $x(-t) = -x(t)$. Almost no signal is either, but every signal is the sum of one of each, uniquely: $x_e = \\frac12[x(t) + x(-t)]$ and $x_o = \\frac12[x(t) - x(-t)]$. Module 2's symmetry shortcuts were this decomposition used without being named.",
                "**Energy** is $E = \\int_{-\\infty}^{\\infty}|x(t)|^2dt$ and **average power** is $P = \\lim_{T\\to\\infty}\\frac{1}{2T}\\int_{-T}^{T}|x(t)|^2dt$. A signal with finite non-zero energy has zero average power, and one with finite non-zero power has infinite energy — so a pulse is an *energy signal* and a periodic waveform is a *power signal*, and the two are described with different quantities for that reason.",
                "For a periodic signal the limit is unnecessary: average over one period. A sinusoid of amplitude $A$ has $P = A^2/2$; a rectangular pulse train of amplitude $A$ and duty cycle $D$ has $P = A^2 D$. RMS is $\\sqrt{P}$ in both cases, which is where $A/\\sqrt2$ came from in EE102.",
                "Mean square adds over components at *different* frequencies and does not add over amplitudes: for $x = V_0 + A\\cos\\omega t$, $P = V_0^2 + A^2/2$, because the cross term averages to zero. RMS values are therefore combined in quadrature, never by addition.",
                "\"Power\" here is a mean square in volts squared — watts only if you agree to divide by one ohm. That convention is why a power ratio is $10\\log_{10}$ and an amplitude ratio is $20\\log_{10}$: they are the same decibel, counted once on a squared quantity and once on an unsquared one.",
                "The signals everything else is assembled from: the unit step $u(t)$, the unit impulse $\\delta(t)$ with unit area and zero width, the real exponential $e^{-t/\\tau}$, and the complex exponential $e^{j2\\pi ft}$. $\\int_{-\\infty}^{t}\\delta(\\tau)d\\tau = u(t)$, and $\\delta$ is the derivative of $u$ in the same generalised sense.",
                "The impulse's **sifting property**: $\\int x(t)\\,\\delta(t - t_0)\\,dt = x(t_0)$. It picks one value out of a whole signal, and it is the continuous-time form of the decomposition module 1 used to get convolution. It is also the only reason a thing that is not a function is worth defining.",
                "An impulse with a scaled argument is not the impulse it looks like: $\\delta(at - b) = \\frac{1}{|a|}\\delta(t - b/a)$. The area, not the height, is what an impulse carries, and squeezing the argument squeezes the area too.",
                "Periodicity is automatic in continuous time and not in discrete time. $\\cos(\\Omega n)$ repeats only when $\\Omega/2\\pi$ is rational: $\\cos(\\pi n/4)$ has period 8, while $\\cos(n)$ is bounded, well behaved, and never repeats.",
                "Discrete-time frequency lives on a circle. $e^{j(\\Omega + 2\\pi)n} = e^{j\\Omega n}$ for every integer $n$, so two frequencies $2\\pi$ apart are the *same sequence* — not similar, identical. That is module 3's aliasing seen from the sequence's side instead of the sampler's, and it is why a discrete-time frequency axis is only ever drawn over one $2\\pi$ span.",
            ],
            "read": [
                {
                    "title": "What a signal is, and the things you may do to its argument",
                    "minutes": 12,
                    "body": r'''
Put a probe on a node of a working circuit and leave it there. At every instant the
probe has a number to report: the potential of that node with respect to ground, in
volts. That correspondence — one number for every moment — is the whole of what the
word **signal** means here. It need not be a voltage. The height of the road under a
car's wheel is a signal; so is the pressure at a microphone, the temperature in a
furnace, the count of photons arriving at a detector. What they have in common is the
structure, a value indexed by time, and that is the only thing any of the mathematics
in this course actually uses.

Four modules have gone by on what *systems* do to signals, and the signals themselves
have been handled loosely. That was affordable while everything in sight was a sinusoid.
It stops being affordable the first time a question asks where a delayed, reversed,
compressed copy of a pulse has ended up on the axis — because the answer is routinely
not the number written in the formula, and the gap between the two is the subject of
half this reading.

## Two kinds of time, and why the brackets differ

A continuous-time signal is written $x(t)$ with round brackets, and $t$ ranges over the
real numbers: there is a value at $t = 1$, at $t = 1.5$, and at $t = 1.500001$. A
discrete-time signal is written $x[n]$ with square brackets, and $n$ ranges over the
integers only. There is no value at $n = 1.5$ — not an unknown value, not a value that
needs interpolating, simply nothing there. $x[n]$ is a list.

The notation is worth respecting because it silently selects which operations are legal.
Integration belongs to round brackets and summation to square ones, which is why module 1
could write the convolution as an integral for $x(t)$ and as a sum for $x[n]$ and treat
the two as the same statement. When a sampler turns one into the other, in module 3,
the change of bracket *is* the change of world.

## Operations on the value, and operations on the argument

Two quite different things can be done to a signal, and it is easy to run them together
because both are written by putting something next to $x$.

Operating on the **value** is the harmless kind: $3x(t)$ multiplies every reading by
three, $x(t) + 2$ lifts the whole trace by two volts, $x_1(t) + x_2(t)$ adds two traces
sample for sample. Nothing moves along the time axis; only the vertical scale changes.

Operating on the **argument** moves the signal along the axis, and this is where the
mistakes live. There are three primitive moves:

- **Delay.** $y(t) = x(t - t_0)$ with $t_0 > 0$. The value $y$ has at time $t$ is the
  value $x$ had at the earlier time $t - t_0$, so the picture slides to the *right* by
  $t_0$. The minus sign producing a rightward shift is the single most persistent
  irritation in the subject, and the only cure is to stop reading the sign and start
  asking the question the definition asks: *which old time does this new time point at?*
- **Reflection.** $y(t) = x(-t)$. The value at $+3$ is the value $x$ had at $-3$: the
  trace is flipped about the vertical axis, played backwards.
- **Scaling.** $y(t) = x(at)$. With $a = 2$ the value at $t = 1$ is the value $x$ had at
  $t = 2$, so events that happened late now happen early: the signal is **compressed**
  towards the origin and runs twice as fast. With $a = \tfrac12$ it is stretched.

Only the first is something an LTI system can do to a signal. Hold on to that; it comes
back at the end.

## The rule that never fails

Real questions do not present one primitive at a time. They present $x(2t - 6)$ or
$x(4 - 3t)$, and the temptation is to read off "compressed by 2, delayed by 6". That is
wrong, and it is wrong in a way that arithmetic will not rescue.

Go back to the definition. $y(t) = x(g(t))$ says: *the value $y$ takes at time $t$ is the
value $x$ takes at time $g(t)$.* So if you know something about $x$ at some argument
value $u$ — that it starts there, or peaks there, or ends there — then $y$ does the same
thing at whatever $t$ makes $g(t) = u$. That is a one-line procedure:

> Write down the argument. Set it equal to each landmark of $x$. Solve for $t$.

Nothing about it can go wrong, it does not care how many operations are combined, and it
does not require you to decide what order they were applied in.

Take a concrete $x$, a trapezoid, so there are four landmarks to track:

```
x(u):   0            for u < 0
        2u           for 0 <= u <= 1        rises to 2 V
        2            for 1 <= u <= 3        flat top
        2(4 - u)     for 3 <= u <= 4        falls back to 0
        0            for u > 4

landmarks at u = 0, 1, 3, 4
```

Now find where $y(t) = x(2t + 1)$ lives.

```
argument u = 2t + 1

u = 0   ->   2t + 1 = 0   ->   t = -0.5      the foot of the rise
u = 1   ->   2t + 1 = 1   ->   t =  0        the top of the rise
u = 3   ->   2t + 1 = 3   ->   t =  1        the start of the fall
u = 4   ->   2t + 1 = 4   ->   t =  1.5      back to zero

y is non-zero on  -0.5 <= t <= 1.5,  a width of 2
x was non-zero on     0 <= u <= 4,   a width of 4
```

The width halved, which is what compression by two must do. And the signal moved
**left by 0.5**, not left by 1. Follow the centre: $x$ was centred on $u = 2$;
compressing by two puts that centre at $t = 1$; and the finished $y$ is centred on
$t = 0.5$, so the shift after the compression was half a second, not a whole one. The
factorisation says the same thing, $2t + 1 = 2\left(t + \tfrac12\right)$, and the number
that appears in the shift is the one *outside* the scaling.

## The mistake, and why it is tempting

The mistake is to read the constant in the argument as the shift. It is tempting because
it is *correct whenever there is no scaling*: for $x(t - 3)$ the shift really is 3, and
that case is met a hundred times before the first compressed one. It is also tempting
because "compress by 2, then advance by 1" is a perfectly good English sentence
describing a perfectly good pair of operations. It just describes a different signal:
compressing first gives $x(2t)$, and advancing *that* by 1 gives
$x(2(t + 1)) = x(2t + 2)$, which is not the $x(2t + 1)$ on the page.

The two orders give different answers, and there is no convention that settles which one
a formula means, because the formula does not mean either: it means *substitute*. Solving
for $t$ sidesteps the whole question. Do it even when it seems unnecessary; it costs one
line.

Reflection makes the point sharply, because the landmarks come out reversed:

```
same trapezoid x, landmarks at u = 0, 1, 3, 4
y(t) = x(1 - t)

u = 0   ->   1 - t = 0   ->   t =  1
u = 1   ->   1 - t = 1   ->   t =  0
u = 3   ->   1 - t = 3   ->   t = -2
u = 4   ->   1 - t = 4   ->   t = -3

y is non-zero on  -3 <= t <= 1,  width 4 (unchanged, there is no scaling)
```

The *last* landmark of $x$ became the *first* landmark of $y$. The rise that took one
second at the start of $x$ is now a fall taking one second at the end of $y$. Sketching
this by "flipping and then shifting by 1" gets the width right and the position wrong
about half the time; solving four small equations gets it right every time.

## Even, odd, and the split that always exists

A signal is **even** if $x(-t) = x(t)$ — reflecting changes nothing, like $\cos$ or a
Gaussian or any function of $|t|$. It is **odd** if $x(-t) = -x(t)$, like $\sin$ or $t$
or $t^3$; an odd signal must pass through zero at the origin, since $x(0) = -x(0)$.

Almost nothing you measure is either. What makes the idea useful is that *every* signal
is the sum of one even and one odd part, in exactly one way. Suppose it were true, and
write $x(t) = x_e(t) + x_o(t)$. Reflect both sides and use the two definitions:

$$x(-t) = x_e(-t) + x_o(-t) = x_e(t) - x_o(t)$$

Two equations, two unknowns. Add them and the odd parts cancel; subtract them and the
even parts cancel:

$$x_e(t) = \tfrac12\left[x(t) + x(-t)\right], \qquad
  x_o(t) = \tfrac12\left[x(t) - x(-t)\right]$$

The derivation also proves the uniqueness, because at no point was there a choice: given
$x$, those two expressions are forced. Check that they are what they claim to be by
reflecting them — $x_e(-t)$ swaps the two terms of the bracket and gives $x_e(t)$ back;
$x_o(-t)$ swaps them and picks up a minus sign.

A three-sample example, small enough to do in the margin. Let $x[n]$ be $1, 3, 2$ at
$n = 0, 1, 2$ and zero everywhere else.

```
n            -2    -1     0     1     2
x[n]          0     0     1     3     2
x[-n]         2     3     1     0     0

x_e[n] = (x[n] + x[-n]) / 2
              1    1.5    1    1.5    1

x_o[n] = (x[n] - x[-n]) / 2
             -1   -1.5    0    1.5    1

check the sum at n = 1:   1.5 + 1.5 = 3   the original value
check the sum at n = -1:  1.5 - 1.5 = 0   the original value
```

Note what happened to the *length*. A three-sample signal produced two five-sample
signals: the decomposition manufactures a mirror image on the other side of the origin,
and the two mirror images cancel when the parts are added back. That is why the split is
free of information — nothing was added, it was only rearranged — and it shows up
numerically in the energies, which add:

```
energy of x     1^2 + 3^2 + 2^2                         = 14
energy of x_e   1^2 + 1.5^2 + 1^2 + 1.5^2 + 1^2         =  7.5
energy of x_o   1^2 + 1.5^2 + 0   + 1.5^2 + 1^2         =  6.5
                                                   7.5 +  6.5 = 14
```

The cross terms vanished, and they vanished for a reason worth naming: the product of an
even signal and an odd one is odd, and an odd signal integrated (or summed) symmetrically
about the origin gives zero. That single fact is what module 2's symmetry shortcuts were
made of — a signal with even symmetry has no sine terms in its Fourier series because
every one of those integrals is an odd function integrated over a symmetric interval.

## Where this stops holding

**Scaling and reflection are not things a system may do.** An LTI system, by definition,
responds to a delayed input with a delayed output, and nothing in the definition permits
$x(2t)$ or $x(-t)$. Time scaling changes the frequency content — a signal compressed by
two has every component doubled in frequency — and no linear time-invariant system can
move energy from one frequency to another. That is why a tape machine played back fast is
not a filter, and why the operations of this reading belong to the description of signals
rather than to the catalogue of circuits.

**Reflection needs the whole signal.** $y(t) = x(-t)$ at $t = -5$ requires $x(5)$, which
has not happened yet. It is buildable off-line, on a recording, and not in real time.
Anything you can do to a stored file, you cannot necessarily do to a wire.

**$a = 0$ is not a scaling.** $x(0 \cdot t) = x(0)$ is a constant, and every landmark
maps to every $t$ at once. The solve-for-$t$ procedure reports this correctly by giving
an equation with no solution or with all solutions, which is more useful than a rule that
quietly returns nonsense.

**In discrete time, scaling loses samples.** $x[2n]$ is defined — it is every second
sample — but it is not reversible, and $x[n/2]$ is undefined at odd $n$ until you decide
what to put there. Compression and stretching in continuous time are inverses of each
other; in discrete time they are decimation and interpolation, they are not inverses,
and choosing what to put in the gaps is a design decision that module 10 makes explicitly.
''',
                },
                {
                    "title": "How big is a signal, and why one number will not do",
                    "minutes": 13,
                    "body": r'''
Two signals arrive at a connector. One is a single 5 V spike lasting two milliseconds;
the other is a 5 V amplitude sine that has been running for a week. Which is bigger?

The question has no answer until you say what "bigger" is for. If the connector feeds a
resistor and you want to know how hot it gets, the sine wins by an enormous margin. If
you want to know whether the input stage clips, they are identical. If you want to know
how much charge is delivered, or how loud it sounds, or whether an ADC saturates, you are
asking three more different questions. So the subject keeps several measures of size and
is careful about which one is being quoted, and the careful part is what this reading is.

## Start with the resistor

Put $v(t)$ across a resistor $R$. The instantaneous power dissipated is

$$p(t) = \frac{v^2(t)}{R}$$

and the total heat delivered over all time is the integral of that. Everything else
follows from those two lines, so it is worth noticing what they contain: the square, and
the division by $R$.

The square is not negotiable. Power does not care about the sign of the voltage, and a
signal that spends half its time at $+5$ V and half at $-5$ V has an average voltage of
zero while heating the resistor perfectly well. Any measure of size that could return
zero for a signal that is plainly there is useless, and averaging $v$ rather than $v^2$
is exactly that measure.

The $R$ *is* negotiable, and the convention is to drop it. Signals in this course get
their size quoted as though they were driving one ohm, which turns volts-squared-seconds
into joules and volts-squared into watts by fiat. It is a convention, not physics, and it
survives because every real answer is proportional to $1/R$ anyway: work in $\mathrm{V}^2$
and divide by the actual resistance at the end, once, when someone asks for a number in
watts.

## Energy: for signals that end

$$E = \int_{-\infty}^{\infty} |x(t)|^2\,dt$$

The modulus is there so the definition still works for the complex signals of module 4.
The units are volts squared times seconds. Two examples, both worth being able to write
down without thinking.

A rectangular pulse of height $A$ and width $T$:

```
E = integral of A^2 over a stretch of length T
  = A^2 T

A = 5 V, T = 2 ms:
E = 25 * 0.002 = 0.05 V^2 s        (into 50 ohm, that is 1.0 mJ)
```

A decaying exponential, $x(t) = A e^{-t/\tau}$ for $t \ge 0$:

```
x^2(t) = A^2 e^{-2t/tau}

E = integral from 0 to infinity of A^2 e^{-2t/tau} dt
  = A^2 * [ -(tau/2) e^{-2t/tau} ] from 0 to infinity
  = A^2 * tau/2

A = 5 V, tau = 2 ms:
E = 25 * 0.002 / 2 = 0.025 V^2 s   (into 50 ohm, 0.5 mJ)
```

Note the factor of two, and note where it came from: squaring an exponential halves its
time constant. The exponential has the same peak as the rectangle and the same
characteristic duration, and carries exactly half the energy — a decent sanity check on
any energy calculation is to compare it with the rectangle that would enclose it.

## Power: for signals that do not end

Now the sine that has been running for a week. Its energy integral diverges: an infinite
number of finite lumps. That is not a defect in the signal, it is a defect in the
question, and the repair is to ask for energy *per unit time* instead:

$$P = \lim_{T\to\infty}\frac{1}{2T}\int_{-T}^{T}|x(t)|^2\,dt$$

For a periodic signal the limit is a formality, because every period contributes the same
amount and the average over $N$ periods equals the average over one. So in practice

$$P = \frac{1}{T_0}\int_{T_0}|x(t)|^2\,dt$$

and no limits are involved. That mean square is the number a **true-RMS voltmeter**
computes, and its square root is the **RMS value**:

$$x_{\mathrm{rms}} = \sqrt{P}$$

For a sinusoid $A\cos\omega t$, use $\cos^2\theta = \tfrac12(1 + \cos 2\theta)$: the mean
of $\cos^2$ over a whole period is $\tfrac12$, because the $\cos 2\theta$ term averages
to nothing. So $P = A^2/2$ and the RMS is $A/\sqrt2$, which is where the mains figure of
230 V RMS from a 325 V peak comes from and where the $\sqrt2$ in EE102's phasor arithmetic
came from.

For a rectangular pulse train of amplitude $A$ and duty cycle $D$, the square takes the
value $A^2$ for a fraction $D$ of every period and zero for the rest, so $P = A^2D$ and
the RMS is $A\sqrt{D}$. At $D = 0.5$ that is $A/\sqrt2$ as well — the same number as the
sinusoid, arrived at for an entirely unrelated reason, which is a coincidence worth
noticing precisely so it is not mistaken for a rule.

The two classes are exclusive, and that is a theorem rather than a habit. A signal with
finite non-zero energy has $P = 0$, because a finite numerator divided by $2T \to \infty$
goes to zero. A signal with finite non-zero power has infinite energy, because it keeps
contributing forever. So one number is always right and the other is always $0$ or
$\infty$: quote the energy of a pulse and the power of a waveform, and the ugly answers
disappear.

## The mistake: adding sizes

Here is the calculation people get wrong, and it is the one that matters most in practice
because real signals are sums.

A sensor output is a 2.5 V DC level with a 4 V amplitude sine riding on it:

$$v(t) = 2.5 + 4\cos(2\pi \cdot 1000\,t)$$

What does a true-RMS meter read? The tempting answer is $2.5 + 4/\sqrt2 = 5.33$ V — the
DC value plus the RMS of the sine. It is wrong. Square the signal first, and see what
happens to the three terms:

```
v^2 = 2.5^2  +  2 * 2.5 * 4 cos(wt)  +  16 cos^2(wt)
    = 6.25   +  20 cos(wt)           +  16 cos^2(wt)

average of each term over one period:

  6.25                 ->  6.25       a constant averages to itself
  20 cos(wt)           ->  0          a full cycle of a cosine has zero mean
  16 cos^2(wt)         ->  8          because the mean of cos^2 is 1/2

mean square  P = 6.25 + 8 = 14.25 V^2
RMS          = sqrt(14.25) = 3.775 V
```

3.775 V, not 5.33 V. The middle term is the whole story: the **cross term averaged to
zero**, and it did so because the two components sit at different frequencies — one at DC
and one at 1 kHz — and the product of two sinusoids at different frequencies has no DC
content. That is orthogonality, and it is the same property that lets module 2 compute
one Fourier coefficient at a time without the others interfering.

So mean squares add, and RMS values combine in quadrature:

$$x_{\mathrm{rms}} = \sqrt{x_{1,\mathrm{rms}}^2 + x_{2,\mathrm{rms}}^2 + \cdots}$$

with one condition attached, which is that the components must be at different
frequencies. Two components at the *same* frequency do not add this way at all — they add
as phasors, amplitude and phase together, and $4\cos\omega t + 4\cos(\omega t + \pi)$ is
zero, not $\sqrt{8+8}$.

The other half of the mistake is dividing by $\sqrt2$ out of habit. $A/\sqrt2$ is the RMS
of a *sinusoid*. A square wave that swings $\pm A$ has RMS $A$ exactly — it is at
magnitude $A$ the whole time, so its mean square is $A^2$ and there is nothing to
average down. A triangle wave has $A/\sqrt3$. The ratio of peak to RMS is the **crest
factor**, and it is a property of the shape: 1 for a square wave, $\sqrt2 = 1.414$ for a
sine, and $1/\sqrt{D}$ for a pulse train, which for a 30% duty cycle is 1.83. Instruments
quote a maximum crest factor for exactly this reason, and a cheap "RMS" meter that is
really an averaging meter scaled by $1.11$ is telling you the truth only for sines.

## Two decibels, or one

Both of these appear constantly:

$$10\log_{10}\frac{P_2}{P_1}\qquad\text{and}\qquad 20\log_{10}\frac{V_2}{V_1}$$

and they are the same formula, not two conventions to memorise. A decibel is defined on
*power* ratios. If the two voltages are measured across the same resistance then
$P \propto V^2$, so

$$10\log_{10}\frac{P_2}{P_1} = 10\log_{10}\frac{V_2^2}{V_1^2} = 20\log_{10}\frac{V_2}{V_1}$$

The 20 is the 10 with the square brought out through the logarithm. Check it once with
numbers: a voltage ratio of 2 is $20\log_{10}2 = 6.02$ dB, and the corresponding power
ratio of 4 is $10\log_{10}4 = 6.02$ dB. Same answer, as it must be. The one place this
goes wrong is when the two voltages are *not* across the same resistance, which is exactly
the situation an impedance-matched RF measurement avoids by construction and a
general-purpose amplifier measurement does not.

## Where these ideas stop

**The limit may not exist.** Speech, music, and the output of anything switching on and
off have no meaningful infinite-time average power; the answer depends on how long you
watch. In practice a *short-term* power is computed over a window of a few tens of
milliseconds and quoted as a function of time, which is what a level meter displays and
what module 9's spectrogram does with a spectrum. The stationarity that the definition
assumes is an assumption about the signal, and it is often false.

**Some signals are neither.** $x(t) = t$ has infinite energy and infinite average power.
So does $e^{t}$. The two classes cover everything encountered in practice and do not cover
everything that can be written down, and a signal that grows without bound is outside
both.

**Discrete time replaces the integrals with sums** — $E = \sum_n |x[n]|^2$ — with one
consequence worth knowing: the answer is in volts squared per *sample*, not per second,
so converting to a physical energy needs the sample rate. Forgetting the sample interval
is the standard way a correct DSP calculation produces an answer that is wrong by a
factor of $f_s$.

**And the one-ohm convention is only a convention.** The moment a real answer is wanted
in watts, put the resistance back. A 3.775 V RMS signal into 50 Ω is 285 mW; into 8 Ω it
is 1.78 W; into an open circuit it is nothing at all.
''',
                },
                {
                    "title": "The four signals everything is built from, and what discrete time does to them",
                    "minutes": 12,
                    "body": r'''
There is a small vocabulary of signals that the rest of the subject is written in. Not
because real waveforms look like them — real waveforms look like nothing in particular —
but because everything else can be assembled out of them, and because the systems in this
course happen to have simple answers when they are the input. Four are enough.

## The step, the exponential, and the one that stays itself

The **unit step** $u(t)$ is 0 before $t = 0$ and 1 after it. Physically it is a switch
closing: the moment power is applied, the moment a signal is connected. Its value exactly
at $t = 0$ is a matter of taste and never affects an integral, so it is left undefined
about as often as it is set to $\tfrac12$.

The step's job is mostly to truncate. Multiplying by $u(t)$ is how you say "and nothing
before this instant", which is how a one-sided signal gets written in one line:
$x(t) = e^{-t/\tau}u(t)$ is the decaying exponential that starts at the origin, rather
than the two-sided thing that was already enormous in the distant past.

The **real exponential** $e^{-t/\tau}$ is not a convention, it is what first-order
circuits do. A capacitor $C$ discharging through a resistor $R$ obeys
$C\,dv/dt = -v/R$, and the only function whose derivative is a constant multiple of
itself is the exponential; $\tau = RC$ falls out as the constant. Every RC and RL
transient in the first year was this function, and $\tau$ is the time to fall to $1/e$,
about 37%, of where it started.

The **complex exponential** $e^{j2\pi f t}$ is the one that looks like an abstraction and
is not. Module 4 showed why it earns its place: put it into an LTI system and what comes
out is the same function multiplied by a complex number. It is the only input with that
property, which is what makes $Y = HX$ possible, and it is the reason the whole course is
written in exponentials rather than in sines and cosines even though every physical signal
is real.

## The impulse, which is not a function

The fourth is $\delta(t)$, and it needs building rather than defining.

Take a rectangle of width $\Delta$ and height $1/\Delta$, centred on the origin. Its area
is 1 whatever $\Delta$ is. Now shrink $\Delta$: the pulse gets narrower and taller, the
area stays at 1, and in the limit there is something of zero width, infinite height and
unit area. That object is the **unit impulse**.

It is not a function — no function is zero everywhere except at one point and still
integrates to 1 — and the honest way to think of it is as a *rule for integrating*
rather than as a graph. Everything it is ever used for happens inside an integral, and
inside an integral it is perfectly well behaved.

Here is the rule, derived from the rectangle. Multiply the narrow rectangle by a smooth
$x(t)$ and integrate:

```
integral of x(t) * (1/D) over the interval [t0 - D/2, t0 + D/2]

   = (1/D) * (area of x over an interval of width D)
   = (1/D) * D * (average of x over that interval)
   = average of x over that interval

as D shrinks, x barely changes across the interval, and the average
becomes the value at the centre:

   -> x(t0)
```

That is the **sifting property**:

$$\int_{-\infty}^{\infty} x(t)\,\delta(t - t_0)\,dt = x(t_0)$$

One number out of an entire signal. Notice what the derivation needed: that $x$ be
continuous at $t_0$. Sift at a point where $x$ jumps and the answer depends on how you
took the limit, which is the mathematical trace of the fact that no real impulse has zero
width.

Two worked examples, the second less innocent than the first.

```
integral of (t^2 + 1) delta(t - 3) dt

  the impulse sits at t = 3, so evaluate the other factor there:
  3^2 + 1 = 10
```

```
integral of x(t) delta(2t - 6) dt

  substitute u = 2t - 6,  so  t = (u + 6)/2  and  dt = du/2:

  = integral of x((u + 6)/2) delta(u) du/2
  = (1/2) * x(3)

  so delta(2t - 6) is NOT delta(t - 3): it is (1/2) delta(t - 3)
```

In general $\delta(at - b) = \frac{1}{|a|}\delta(t - b/a)$. The scaling factor is there
because an impulse is defined by its *area*, and compressing the time axis by $a$
compresses the area by $a$ too. Nothing analogous happens to an ordinary function —
$\cos(2t)$ has the same amplitude as $\cos(t)$ — which is why this is the first place
that treating $\delta$ as if it were a function produces a wrong answer.

A physical version, so the object stops feeling like a trick. Dump a charge $q$ into a
capacitor $C$ in a time far shorter than anything else in the circuit. The current is
$i(t) = q\,\delta(t)$, and the capacitor voltage is the integral of $i/C$, so it steps
by $q/C$ and stays there:

```
q = 30 uC into C = 10 uF     ->   step of 30e-6 / 10e-6 = 3.0 V

modelled as a real pulse instead:
  30 uC delivered in 1 us  =  30 A for 1 us
```

Thirty amps. The impulse is the idealisation of something violent and brief, and the
model is good precisely when the "brief" is short compared with every time constant in
the circuit — which is the same condition that made the average of $x$ across the pulse
equal to its centre value.

The step and the impulse are each other's calculus:
$\int_{-\infty}^{t}\delta(\lambda)\,d\lambda = u(t)$, and $\delta$ is the derivative of
$u$ in the same generalised sense. A step has zero slope everywhere except at the jump,
where it has infinite slope for no time at all and unit area under that slope. This is
not a coincidence to be memorised; it is the reason a circuit's step response and its
impulse response carry the same information, and why measuring either one determines the
other.

## The mistakes people make with $\delta$

The first is asking what $\delta(0)$ *is*. The question has no answer, because $\delta$
has no values; it has integrals. If a calculation ever needs the height of an impulse,
something has gone wrong upstream.

The second is $\delta(2t) = \delta(t)$, addressed above. The habit comes from ordinary
functions, where compressing the argument leaves the height alone.

The third is dimensional. $\delta(t)$ has units of one over time — it must, since
$\int\delta\,dt = 1$ is dimensionless. So a current impulse of "strength 30 µC" is
$30\times10^{-6}\,\delta(t)$ amps, with the $\delta$ carrying the $\mathrm{s}^{-1}$. Data
sheets and simulators are usually careful about this and hand-written notes usually are
not.

## Discrete time changes two things

Everything above transfers to sequences unchanged, except in two places, and both
surprises are pleasant once they are expected.

**Periodicity is no longer automatic.** $\cos(\omega t)$ repeats for any $\omega$
whatever; $\cos(\Omega n)$ need not repeat at all. It repeats with period $N$ only if
$\Omega N$ is a whole number of turns:

$$\Omega N = 2\pi m \quad\text{for some integers } N > 0, m
\qquad\Longleftrightarrow\qquad \frac{\Omega}{2\pi} = \frac{m}{N}$$

So the condition is that $\Omega/2\pi$ be **rational**, and when it is, the period is the
smallest $N$ that clears the fraction.

```
Omega = 3 pi / 5      N = 2 pi m / Omega = 10m/3     m = 3 gives N = 10
                      check: cos(3 pi * 10 / 5) = cos(6 pi), a whole number of turns

Omega = 7 pi / 4      N = 2 pi m / Omega = 8m/7      m = 7 gives N = 8

Omega = 1             N = 2 pi m, never an integer   not periodic, ever
```

$\cos(n)$ is bounded, smooth to look at, and completely non-repeating. Nothing physical
is wrong with it; it simply has no period, and any argument that assumed one — a Fourier
series, a DFT of one "period" — does not apply to it.

**Frequency lives on a circle.** For every integer $n$,

$$e^{j(\Omega + 2\pi)n} = e^{j\Omega n}e^{j2\pi n} = e^{j\Omega n}$$

because $e^{j2\pi n} = 1$ whenever $n$ is an integer. Two discrete-time frequencies
$2\pi$ apart are not similar sequences, they are the *same* sequence, value for value.
Take the second example above:

```
cos(7 pi n / 4) = cos(2 pi n - pi n / 4) = cos(pi n / 4)
```

which is why its period came out as 8 — it *is* the $\Omega = \pi/4$ sequence, and the
$7\pi/4$ label made it look like the faster of the two. In continuous time
$\cos(7\pi t/4)$ really is seven times the faster signal. In discrete time the
distinction does not exist, and no measurement made on the sequence can recover it.

That is module 3's aliasing stated without mentioning a sampler. It also explains a fact
about discrete-time frequency that otherwise looks arbitrary: the *highest* frequency is
$\Omega = \pi$, where the sequence is $e^{j\pi n} = (-1)^n$, alternating every sample.
Push $\Omega$ past $\pi$ and the sequence starts getting slower again, because $\Omega$
and $\Omega - 2\pi$ are the same thing and the second is heading back towards zero. There
is nowhere further to go.

## Where this stops holding

**The impulse is a distribution, and the licence is limited.** $\delta(t)$ makes sense
inside an integral against a continuous function. Products of impulses,
$\delta(t)^2$, and $\delta$ evaluated at a discontinuity of $x$ are all outside the
theory. Engineering practice stays inside it by only ever letting an impulse meet a
smooth signal or a linear system.

**No real generator produces one.** Every physical approximation has finite width and
therefore finite bandwidth, and it acts as an impulse only for systems slow enough not to
notice. Hit a 10 MHz circuit with a 100 ns "impulse" and you are measuring the pulse, not
the circuit. The practical test is the one already used above: is the pulse short compared
with the fastest time constant that matters?

**In discrete time none of this subtlety exists.** $\delta[n]$ is an ordinary sequence —
1 at $n = 0$ and 0 elsewhere — with a finite value, no limiting process, and no
distributional apology needed. The sifting property becomes
$\sum_n x[n]\delta[n - n_0] = x[n_0]$ and is obvious by inspection. That asymmetry is
worth naming, because it is the reason the discrete-time development of this course is
in every respect the easier one, and the reason simulations of continuous systems are so
often carried out on their sampled versions.
''',
                },
            ],
            "match": {
                "title": "What each element puts on a wire",
                "minutes": 6,
                "brief": r'''
A signal in this course is a voltage somewhere in a circuit, and every schematic you
will read states, in symbols, where its signals come from and what happens to them.
Six of those symbols carry the whole vocabulary: two that *make* a signal, three that
*act* on one, and one that says what a signal is measured against.

There are seven labels and six symbols, so one label belongs to a symbol that is not
drawn. Finding which is part of the exercise.
''',
                "prompt": "Pick a label, then tap the symbol it describes.",
                "labels": [
                    "Produces the waveform written beside it, whatever is connected across it",
                    "Forces the current written beside it, and takes whatever voltage the rest of the circuit has to give it",
                    "Scales the signal and does nothing else to it — no memory, no delay, no change of shape",
                    "Carries a current proportional to how fast the voltage across it is changing",
                    "Develops a voltage proportional to how fast the current through it is changing",
                    "The node every signal is quoted against, because a signal is a difference and this is its other end",
                    "Interrupts the path on command — the thing that turns a constant into a step",
                ],
                "items": [
                    {"sym": "V", "a": 0, "why": "An ideal voltage source. The signal it puts on the "
                     "wire is an input to the analysis, not a result of it — which is exactly "
                     "the licence that lets you write $x(t)$ and then ask what the circuit does "
                     "with it. A real source has an internal resistance and the distinction "
                     "matters, but not until you draw the load."},
                    {"sym": "I", "a": 1, "why": "An ideal current source: the dual of the voltage "
                     "source, and just as much a definition of an input. Photodiodes and current "
                     "mirrors are modelled this way, and the signal you would probe is then the "
                     "voltage that current produces across whatever it flows through."},
                    {"sym": "R", "a": 2, "why": "A resistor is the only **memoryless** element "
                     "here: its output at this instant depends on its input at this instant and "
                     "nothing else. In the language of module 1 its impulse response is a scaled "
                     "impulse, so a network of resistors alone behaves identically at every "
                     "frequency."},
                    {"sym": "C", "a": 3, "why": "A capacitor: $i = C\\,dv/dt$. It responds to how "
                     "fast the signal is moving, not to where it is, which is why it passes "
                     "high frequencies and blocks DC — and why the differentiator built in "
                     "the next module is a capacitor with a resistor after it."},
                    {"sym": "L", "a": 4, "why": "An inductor: $v = L\\,di/dt$. The same sentence "
                     "as the capacitor with current and voltage exchanged, which is what makes "
                     "the two duals of each other and why every filter has a version built from "
                     "either."},
                    {"sym": "GND", "a": 5, "why": "Ground. A signal is a potential *difference*, "
                     "so writing $x(t)$ without saying what it is measured against is meaningless; "
                     "this symbol is that statement. It is a nomination, not a place, and every "
                     "voltage on the schematic silently ends ‘… relative to here’."},
                ],
            },
            "quiz": {
                "title": "Reading a signal before doing anything to it",
                "minutes": 10,
                "questions": [
                    {
                        "q": "$x(t)$ is non-zero only for $0 \\le t \\le 1$. For which $t$ is $x(2t - 6)$ non-zero?",
                        "opts": [
                            "$3 \\le t \\le 3.5$",
                            "$6 \\le t \\le 6.5$",
                            "$6 \\le t \\le 7$",
                            "$1.5 \\le t \\le 2$",
                        ],
                        "a": 0,
                        "why": r'''
Set the argument to each end of the interval and solve: $2t - 6 = 0$ gives $t = 3$, and
$2t - 6 = 1$ gives $t = 3.5$. The signal is half as wide, as compression by two
requires, and it starts at 3 rather than at 6. Reading the 6 straight off as the delay
is the standard slip: $x(2t-6)$ is $x(2(t-3))$, and the shift that appears in the answer
is the one written *outside* the compression. Landing on $6 \le t \le 6.5$ means the
compression and the shift were applied in the other order, which is a different signal.
''',
                    },
                    {
                        "q": "A 5 V amplitude sinusoid has been running since the beginning of time and will not stop. What are its energy and its average power?",
                        "opts": [
                            "energy 25, power 12.5",
                            "infinite energy, average power 12.5",
                            "energy 12.5, infinite power",
                            "infinite energy, average power 25",
                        ],
                        "a": 1,
                        "why": r'''
$\int|x|^2dt$ over an infinite interval of a signal that never decays is infinite, so
the energy is not a useful number here. The average power is, and for a sinusoid it is
$A^2/2 = 12.5$ — which is $5^2/2$, and the reason RMS is $A/\sqrt2$. This is the whole
point of having two measures of size: an energy signal has zero average power, a power
signal has infinite energy, and quoting the wrong one gives you a zero or an infinity
instead of a number.
''',
                    },
                    {
                        "q": "Which of these discrete-time signals is periodic?",
                        "opts": ["$\\cos(n)$", "$\\cos(2n)$", "$\\cos(\\pi n/4)$", "$\\cos(n/2)$"],
                        "a": 2,
                        "why": r'''
$x[n] = \cos(\Omega n)$ repeats only if some whole number of samples spans a whole
number of cycles — that is, if $\Omega/2\pi$ is rational. For $\Omega = \pi/4$ it is
$1/8$, so the signal repeats every 8 samples. For $\Omega = 1$ or $2$ or $1/2$ the ratio
contains a $\pi$ in the denominator and is irrational, so the sequence never exactly
repeats, however long you wait. It is still bounded and still perfectly well behaved;
it just has no period, which is a discrete-time possibility with no continuous-time
counterpart.
''',
                    },
                    {
                        "q": "$x(t) = e^{-t}$ for $t \\ge 0$ and zero for $t < 0$. Is it even, odd, or neither?",
                        "opts": [
                            "even, because it never goes negative",
                            "odd, because it is zero on one side of the origin",
                            "neither — and being one-sided, it has no even/odd decomposition",
                            "neither — but it still splits uniquely, with even part $\\tfrac12 e^{-|t|}$",
                        ],
                        "a": 3,
                        "why": r'''
Reflect it and you get a signal living on $t \le 0$, which is neither the original nor
its negative — so it is neither even nor odd. The decomposition still works, because it
always works: $x_e = \frac12[x(t) + x(-t)] = \frac12 e^{-|t|}$, a two-sided decaying
exponential, and $x_o$ is the same shape with its left half inverted. Every signal has
exactly one such pair, which is what makes the symmetry arguments of module 2 safe to
use rather than lucky.
''',
                    },
                    {
                        "q": "What is $\\int_{-\\infty}^{\\infty} x(t)\\,\\delta(t - 3)\\,dt$?",
                        "opts": ["$x(3)$", "$3$", "$\\delta(3)$", "the area under $x$ up to $t = 3$"],
                        "a": 0,
                        "why": r'''
The sifting property. The impulse is zero everywhere except at $t = 3$ and has unit
area, so the integral collects the value of $x$ at that one instant and discards
everything else — one number out of a whole signal. Answering with the area under $x$
up to 3 is the integral of $x$ against a *step*, which is a different and equally
useful operation, and the difference between the two is exactly the difference between
$u$ and its derivative. Sifting is what lets module 1 write any signal as a sum of
shifted impulses in the first place.
''',
                    },
                    {
                        "q": "How do the sequences $\\cos(0.2\\pi n)$ and $\\cos(2.2\\pi n)$ compare, sample for sample?",
                        "opts": [
                            "identical at every $n$",
                            "the second oscillates eleven times faster",
                            "they differ by a fixed phase",
                            "the second is periodic and the first is not",
                        ],
                        "a": 0,
                        "why": r'''
$\cos(2.2\pi n) = \cos(0.2\pi n + 2\pi n)$, and $2\pi n$ is a whole number of turns for
every integer $n$, so the two sequences agree at every sample — not approximately,
exactly. In continuous time $\cos(2.2\pi t)$ really would be eleven times the faster
signal; sampling destroys that distinction, and no measurement made on the sequence can
recover it. This is aliasing stated without mentioning a sampler, and it is why the
discrete-time frequency axis only needs one $2\pi$ span.
''',
                    },
                ],
            },
            "numeric": [
                {
                    "title": "The energy in a single pulse",
                    "minutes": 5,
                    "brief": r'''
A piezoelectric sensor is struck once. Its output is a single rectangular pulse: 3 V
while the strike lasts, zero before and after, 4 ms from edge to edge. Nothing repeats,
so there is no period to average over and no average power worth quoting — the signal
ends, and the number that describes it is its **energy**.

One rule, one integral, and the integral is a rectangle.
''',
                    "prompt": "What is the energy of this pulse?",
                    "note": "Answer in V²s — the one-ohm convention, so no resistance is involved. Three significant figures.",
                    "figure": r'''
```
   3 V             +--------------+
                   |              |
   0 V   ----------+              +-----------------
                   0              4                  ms

   a single pulse: nothing before it, nothing after it
```

The whole signal is drawn. There is no continuation off either side of the picture.
''',
                    "given": [
                        {"label": "Pulse height", "value": "3.00 V"},
                        {"label": "Pulse width", "value": "4.00 ms"},
                        {"label": "Everywhere else", "value": "0 V"},
                    ],
                    "aside": "Energy is the integral of the *square*, so the height enters twice and "
                             "the width once. Doubling the height quadruples the answer; doubling "
                             "the width only doubles it.",
                    "answer": 0.036,
                    "tol": 0.0005,
                    "unit": "V²s",
                    "hint": "$x^2(t)$ is $9$ V² for 4 ms and zero elsewhere, so the integral is the "
                            "area of one rectangle: $9 \\times 0.004$.",
                    "wrong": "0.012 is $3 \\times 0.004$ — the area under the signal rather than "
                             "under its square, which is a charge-like quantity and not an energy. "
                             "36 is the same calculation with the width left in milliseconds; the "
                             "seconds in V²s have to be seconds.",
                    "why": r'''
```
x^2(t) = 3^2 = 9 V^2   for 0 <= t <= 4 ms,  zero elsewhere

E = 9 V^2 * 0.004 s = 0.036 V^2 s
```

Into a real load the joules follow by dividing once: 0.036/50 = 0.72 mJ into 50 Ω, or
4.5 mJ into 8 Ω. The V²s figure is the property of the *signal*; the joules are a
property of the signal and the load together, which is exactly why the two are kept
apart.

Ask for this pulse's average power and the answer is zero. Spread 0.036 V²s over all of
time and you get nothing per second — which is not a failure of the calculation but the
theorem doing its job: a signal with finite energy has zero average power, and the
useful number for it is the one just computed.
''',
                },
                {
                    "title": "The RMS value of a pulse train",
                    "minutes": 7,
                    "brief": r'''
A logic output drives a load with a rectangular wave: 4 V while it is high, 0 V while
it is low, high for 3 ms out of every 10 ms. Somebody has to size the resistor that
dissipates it, and for that the number wanted is not the amplitude and not the mean —
it is the **RMS**, the square root of the mean square, because power goes as the square
of the voltage and the mean of a square is not the square of a mean.
''',
                    "prompt": "What is the RMS value of this waveform?",
                    "note": "Three significant figures is plenty. The signal is periodic, so one period is enough to average over.",
                    "figure": r'''
```
   4 V       +------+             +------+             +------+
             |      |             |      |             |      |
   0 V ------+      +-------------+      +-------------+      +------
             0      3            10     13            20     23     ms
             |<-3ms->|
             |<------- 10 ms period ------>|
```

High for 3 ms, low for 7 ms, forever. Nothing about the *order* of the high and low
parts matters to the answer — only how much of the period is spent at each level.
''',
                    "given": [
                        {"label": "High level", "value": "4.00 V"},
                        {"label": "Low level", "value": "0 V"},
                        {"label": "Time high", "value": "3.00 ms"},
                        {"label": "Period", "value": "10.0 ms"},
                    ],
                    "aside": "The mean of this waveform is 1.2 V and its amplitude is 4 V. The answer "
                             "is neither, and it lies between them — which is true of every "
                             "waveform that is not a constant.",
                    "answer": 2.1908902300206643,
                    "tol": 0.02,
                    "unit": "V",
                    "hint": "Average the *square* over one period: the square is $16$ for 3 ms and $0$ "
                            "for 7 ms, so the mean square is $16 \\times 0.3$. Then take the root.",
                    "wrong": "Two usual slips: averaging the voltage (1.2 V) instead of its square, "
                             "and dividing the amplitude by $\\sqrt2$, which is the answer for a "
                             "sinusoid and for nothing else.",
                    "why": "The mean square is $A^2 D = 16 \\times 0.3 = 4.8$ V², so the RMS is "
                           "$\\sqrt{4.8} = 2.191$ V. In general a pulse train of amplitude $A$ and "
                           "duty cycle $D$ has RMS $A\\sqrt{D}$, which is worth carrying: at 50% duty "
                           "it is $A/\\sqrt2$, the same factor as a sinusoid, by coincidence rather "
                           "than for any shared reason. Note also what the answer does not depend on "
                           "— the period. Make it 10 µs or 10 s and the RMS is unchanged, "
                           "because only the fraction of time at each level entered the calculation.",
                },
                {
                    "title": "One value of the even part",
                    "minutes": 8,
                    "brief": r'''
A one-sided decaying exponential — the discharge of a capacitor, switched on at $t = 0$:

$$x(t) = 4e^{-t/2}\;\text{for } t \ge 0, \qquad x(t) = 0 \;\text{for } t < 0$$

with $t$ in seconds. It is neither even nor odd, which is the ordinary case. It still
splits into an even part and an odd part, uniquely, and this question asks for one value
of the even one — at a time where the original signal is not even present.
''',
                    "prompt": "What is $x_e(-3)$, the even part evaluated at $t = -3$ s?",
                    "note": "Answer in volts, three significant figures. $e^{-1.5} = 0.22313$.",
                    "figure": r'''
```
   4 V |    *
       |     *
       |       *
       |          *
       |              *  *  *
   0 V |__________________________*___*___*____
      -3    0    1    2    3    4    5    6      t (s)

       nothing at all to the left of the origin
```

The even part is $x_e(t) = \tfrac12\left[x(t) + x(-t)\right]$, and the odd part is the
same with a minus sign. Only one of the two terms in that bracket is non-zero here.
''',
                    "given": [
                        {"label": "Amplitude", "value": "4.00 V"},
                        {"label": "Time constant", "value": "2.00 s"},
                        {"label": "Signal for $t < 0$", "value": "0 V"},
                        {"label": "Asked at", "value": "$t = -3$ s"},
                    ],
                    "aside": "The reflected copy is what puts something at negative time. Half of "
                             "the original and half of its mirror image is the entire content of "
                             "the decomposition.",
                    "answer": 0.44626032029685964,
                    "tol": 0.005,
                    "unit": "V",
                    "hint": "Write out $x_e(-3) = \\tfrac12[x(-3) + x(3)]$. One of those two is zero "
                            "by the definition of the signal; the other is $4e^{-3/2}$.",
                    "wrong": "0 comes from evaluating $x$ itself at $-3$ and stopping — but the "
                             "question asks about $x_e$, which is a different signal and is non-zero "
                             "on both sides of the origin. 0.893 is $x(3)$ without the factor of a "
                             "half. 2.00 is $\\tfrac12 x(0)$, the value at the origin rather than at "
                             "$-3$.",
                    "why": r'''
```
x_e(-3) = (1/2) [ x(-3) + x(-(-3)) ]
        = (1/2) [ x(-3) + x(3) ]

x(-3) = 0                    the signal does not exist before t = 0
x(3)  = 4 e^(-3/2)
      = 4 * 0.22313 = 0.89252 V

x_e(-3) = 0.89252 / 2 = 0.44626 V
```

Two things are worth taking from this. The first is that $x_e(3)$ is the *same* number,
0.44626 V, because that is what even means — so the decomposition has manufactured a
mirror image on the left-hand side out of nothing but the right-hand side.

The second is that the manufactured half cancels when the parts are added back.
$x_o(-3) = \tfrac12[x(-3) - x(3)] = -0.44626$ V, and
$x_e(-3) + x_o(-3) = 0$, which is $x(-3)$ — exactly as required. Nothing was created:
$\tfrac12 e^{-|t|}$-shaped symmetry on one side and its negative on the other, summing to
the original one-sided signal and to nothing at all where the original was silent.
''',
                },
                {
                    "title": "What an AC-coupled meter reads",
                    "minutes": 9,
                    "brief": r'''
A sensor output is measured with a true-RMS voltmeter. The signal is a DC level with two
harmonically unrelated tones riding on it:

$$v(t) = 2.5 + 4\cos(2\pi \cdot 1000\,t) + 1.5\cos(2\pi\cdot 3000\,t + 0.7)$$

The meter is switched to **AC** coupling, which puts a capacitor in series with its input
and removes the DC term before anything is measured. Both tones are far above the meter's
coupling corner, so they arrive intact.

Mean squares add over components at different frequencies. Amplitudes do not.
''',
                    "prompt": "What does the meter read?",
                    "note": "Answer in volts RMS, three significant figures. The 0.7 rad phase is given to be used or discarded on purpose.",
                    "figure": r'''
```
  component            amplitude      frequency      passed by AC coupling?
 ---------------------------------------------------------------------------
  DC offset             2.5 V             0 Hz            no  - blocked
  fundamental           4.0 V          1000 Hz            yes
  third tone            1.5 V          3000 Hz            yes   (phase 0.7 rad)
```

A true-RMS meter computes $\sqrt{\overline{v^2}}$ on whatever reaches it — no assumption
about the waveform's shape, which is what separates it from an averaging meter.
''',
                    "given": [
                        {"label": "DC term", "value": "2.50 V (blocked)"},
                        {"label": "Tone 1", "value": "4.00 V amplitude at 1 kHz"},
                        {"label": "Tone 2", "value": "1.50 V amplitude at 3 kHz"},
                        {"label": "Coupling", "value": "AC — DC removed"},
                    ],
                    "aside": "Each sinusoid contributes its own mean square, $A^2/2$, and the cross "
                             "terms average to zero because the two tones sit at different "
                             "frequencies. That is the only reason the sum is this simple.",
                    "answer": 3.020761493398643,
                    "tol": 0.02,
                    "unit": "V",
                    "hint": "Add the mean squares of the two tones — $4^2/2$ and $1.5^2/2$ — and "
                            "take the root. The DC term contributes nothing because it never "
                            "reaches the meter.",
                    "wrong": "3.92 is the DC-coupled reading, with $2.5^2$ included. 3.89 is "
                             "$4/\\sqrt2 + 1.5/\\sqrt2$, RMS values added instead of combined in "
                             "quadrature — always too large, and the error grows as the two get "
                             "closer in size. 5.5 is the peak-to-peak reasoning of adding the two "
                             "amplitudes, which is a bound on the waveform rather than a mean.",
                    "why": r'''
```
tone 1 mean square    4.0^2 / 2   =  8.000 V^2
tone 2 mean square    1.5^2 / 2   =  1.125 V^2
DC                    blocked     =  0

total mean square                 =  9.125 V^2
RMS = sqrt(9.125)                 =  3.021 V
```

The phase 0.7 rad never entered. It cannot: shifting one component in time changes
nothing about how much of it there is, and the cross term it appears in averages to zero
whatever its phase. That is worth trusting, because the phase between two components of a
real signal is usually unknown and the RMS is usually still exactly computable.

Switch the meter back to DC coupling and it reads
$\sqrt{2.5^2 + 8 + 1.125} = \sqrt{15.375} = 3.921$ V. The difference between the two
readings, 3.921 against 3.021, is entirely the 2.5 V offset — and note that it is not the
difference of the readings, 0.90 V, that the offset is worth. Quadrature addition means
the largest component dominates and the smaller ones add less than their face value,
which is why an interferer 20 dB down on a signal disturbs an RMS measurement by about
half a per cent rather than by ten.
''',
                },
                {
                    "title": "The power a square wave actually delivers",
                    "minutes": 11,
                    "brief": r'''
A gate driver puts out a symmetric square wave that swings between $+6$ V and $-6$ V with
equal time at each level. It is fed into the attenuator drawn below and the last resistor,
4.7 kΩ, is the load whose dissipation somebody has to check.

The source symbol is marked with 6 V: that is the level the wave sits at while it is high,
and by symmetry it sits at exactly the negative of that while it is low. The network is
purely resistive, so it scales both levels by the same factor and does nothing else —
no shape change, no delay, no frequency dependence.

Two things have to be right. The attenuation, which is not the product of the two
divider ratios, because each stage loads the one before it. And the RMS of the waveform,
which is not the amplitude over root two.
''',
                    "prompt": "What average power does the 4.7 kΩ load resistor dissipate?",
                    "note": "Answer in milliwatts, three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "p1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 1000},
                            {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 3300},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "p3", "kind": "R", "x": 12, "y": 4, "rot": 0, "value": 2200},
                            {"id": "p4", "kind": "R", "x": 15, "y": 6, "rot": 1, "value": 4700},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 9},
                            {"id": "o0", "kind": "OUT", "x": 17, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [9, 4], "b": [11, 4]},
                            {"a": [13, 4], "b": [15, 4]},
                            {"a": [15, 4], "b": [15, 5]},
                            {"a": [15, 7], "b": [15, 9]},
                            {"a": [15, 4], "b": [17, 4]},
                        ],
                    },
                    "given": [
                        {"label": "Square wave", "value": "±6.00 V, 50% duty"},
                        {"label": "Series resistors", "value": "1.00 kΩ then 2.20 kΩ"},
                        {"label": "Shunt resistors", "value": "3.30 kΩ then 4.70 kΩ"},
                        {"label": "Probe", "value": "across the 4.70 kΩ load"},
                    ],
                    "aside": "The solver is drawn with a 6 V source because that is the wave's high "
                             "level. Every node voltage it reports is the level that node sits at "
                             "while the wave is high; the low half is the negative of it.",
                    "answer": 1.6950805637683695,
                    "tol": 0.02,
                    "unit": "mW",
                    "check": r'''
const R = c.values('R');
const vrms = Math.abs(c.vout());   /* symmetric square wave: RMS equals the level */
return 1000 * vrms * vrms / R[3];
''',
                    "hint": "Work from the right. The second stage presents $2.2 + 4.7 = 6.9$ kΩ to "
                            "the middle node; put that in parallel with the 3.3 kΩ already there and "
                            "solve the first divider. Then take the second divider's share of what is "
                            "left. Finally: for a symmetric square wave the RMS *is* the level, so "
                            "$P = V^2/R$ with no factor of a half anywhere.",
                    "wrong": "0.848 mW is the same calculation with the level divided by $\\sqrt2$ — "
                             "the sinusoid's RMS applied to a waveform that is not one, and it halves "
                             "the power. 2.09 mW comes from multiplying the two unloaded divider "
                             "ratios, $0.767 \\times 0.681$, which ignores that the second stage "
                             "loads the first. 2.49 mW is the power in the whole right-hand branch, "
                             "the 2.20 kΩ included, rather than in the load alone.",
                    "why": r'''
```
the second stage, seen from the middle node   2.2k + 4.7k              =  6.900 kohm
in parallel with the 3.3k already there       (3.3*6.9)/(3.3+6.9)      =  2.2324 kohm
middle node, high half of the wave            6 * 2.2324/(1 + 2.2324)  =  4.1438 V
the second divider's share                    4.1438 * 4.7/6.9         =  2.8226 V

so the load sees a square wave of +/- 2.8226 V

RMS of a symmetric square wave                                          =  2.8226 V
P = V_rms^2 / R                               2.8226^2 / 4700          =  1.6951 mW
```

Both traps are worth restating. Cascading the two unloaded ratios gives
$0.7674 \times 0.6812 = 0.5228$ and a level of 3.14 V — 11% high, because the second
stage's 6.9 kΩ is very much hanging on the middle node while the first divider works.
And a square wave's RMS equals its amplitude: it is at magnitude 2.8226 V for the entire
period, so there is nothing to average down and $P = V^2/R$ applies directly, with no
half.

Sanity check the size of the answer without any of the arithmetic. The load has 2.82 V
across it and is 4.7 kΩ, so it carries about 0.6 mA, and 2.82 V × 0.6 mA is about
1.7 mW. Good enough to catch a factor of two, which is precisely the error the $\sqrt2$
would have introduced.
''',
                },
            ],
            "blanks": {
                "title": "Where a transformed signal actually lives",
                "minutes": 8,
                "caption": "one landmark at a time, and no guessing about order",
                "lang": "text",
                "brief": r'''
The reading claimed that a combined argument is read by solving rather than by pattern
matching. This is that claim reduced to six holes.

$x$ is known only by where it is non-zero — no shape is needed, and none is given. Put
the argument equal to each end of that interval, solve for $t$, and let the answers land
where they land. Notice on the way through that they do not come out in the order you
wrote them.
''',
                "listing": """
  x(u) is non-zero only for      2 <= u <= 6

  y(t) = x(4 - 2t).   Where is y non-zero?

  set the argument to each end of x's interval and solve for t

      4 - 2t = 2     ->    t = ___
      4 - 2t = 6     ->    t = ___

  the larger landmark of x produced the smaller t, so read them back in order

      y is non-zero for      ___ <= t <= ___

  its width is ___ times the width of x

  and factorising the argument, 4 - 2t = -2(t - 2), the shift is a

      ___
""",
                "blanks": [
                    {
                        "prompt": "Solve $4 - 2t = 2$.",
                        "hole": "?",
                        "opts": ["1", "-1", "3", "-3"],
                        "a": 0,
                        "why": "$4 - 2t = 2$ gives $2t = 2$, so $t = 1$. This is where $y$ has the value $x$ had at $u = 2$ — the *left* end of $x$'s interval, arriving at the *right* end of $y$'s.",
                        "whys": [
                            "$4 - 2t = 2$ gives $2t = 2$, so $t = 1$. This is where $y$ has the value $x$ had at $u = 2$ — the *left* end of $x$'s interval, arriving at the *right* end of $y$'s.",
                            "That is the answer to the other equation, $4 - 2t = 6$. Easy to swap, and swapping them is harmless here only because the next step sorts the pair — it is not harmless when the two landmarks mean different things, such as the start and the end of a ramp.",
                            "That is $4 - t = 2$ — the compression by two has been dropped. The factor multiplying $t$ has to divide the whole of the right-hand side, not part of it.",
                            "A sign has gone astray: substituting $t = -3$ gives an argument of $4 + 6 = 10$, which is outside $x$ altogether, so $y(-3)$ is zero.",
                        ],
                    },
                    {
                        "prompt": "Solve $4 - 2t = 6$.",
                        "hole": "?",
                        "opts": ["-1", "5", "1", "-5"],
                        "a": 0,
                        "why": "$4 - 2t = 6$ gives $-2t = 2$, so $t = -1$. The right-hand end of $x$ maps to the left-hand end of $y$, which is the reflection showing itself.",
                        "whys": [
                            "$4 - 2t = 6$ gives $-2t = 2$, so $t = -1$. The right-hand end of $x$ maps to the left-hand end of $y$, which is the reflection showing itself.",
                            "That solves $2t - 4 = 6$, which is the argument with its sign flipped. The minus in $4 - 2t$ is the reflection, and dropping it removes the very feature that makes this exercise worth doing.",
                            "That is the solution to the other equation, $4 - 2t = 2$. Both are needed, but this one has to come from the landmark at $u = 6$.",
                            "Check it: $4 - 2(-5) = 14$, nowhere near the interval $x$ occupies.",
                        ],
                    },
                    {
                        "prompt": "The lower end of $y$'s interval.",
                        "hole": "?",
                        "opts": ["-1", "1", "2", "-3"],
                        "a": 0,
                        "why": "The two solutions were $1$ and $-1$, so the interval runs from $-1$ to $1$. The smaller of the two is the lower end whichever landmark it came from — that is the whole reason for solving rather than substituting positions.",
                        "whys": [
                            "The two solutions were $1$ and $-1$, so the interval runs from $-1$ to $1$. The smaller of the two is the lower end whichever landmark it came from — that is the whole reason for solving rather than substituting positions.",
                            "That is the upper end. Writing the two answers down in the order the equations were solved puts them backwards here, which is exactly the trap a reflection sets.",
                            "That is the lower end of $x$, not of $y$. Nothing about $y$'s interval has to overlap $x$'s.",
                            "Neither equation produced $-3$; substituting it gives an argument of 10.",
                        ],
                    },
                    {
                        "prompt": "The upper end of $y$'s interval.",
                        "hole": "?",
                        "opts": ["1", "-1", "6", "3"],
                        "a": 0,
                        "why": "$t = 1$, the larger of the two solutions. So $y$ is non-zero on $-1 \\le t \\le 1$, an interval of width 2.",
                        "whys": [
                            "$t = 1$, the larger of the two solutions. So $y$ is non-zero on $-1 \\le t \\le 1$, an interval of width 2.",
                            "That is the lower end. The pair has to be written smallest first for the inequality to say anything.",
                            "That is a landmark of $x$, read straight off without being transformed. The argument value 6 and the time value 6 are different things and the notation deliberately keeps them apart by calling one $u$ and one $t$.",
                            "Nothing here produces 3. Substituting $t = 3$ gives an argument of $-2$, outside $x$.",
                        ],
                    },
                    {
                        "prompt": "Compare the two widths.",
                        "hole": "?",
                        "opts": ["1/2", "2", "1", "1/4"],
                        "a": 0,
                        "why": "$x$ occupied 4 units of argument and $y$ occupies 2 units of time, so the width is halved — which is what a factor of 2 multiplying $t$ must do, and the reflection contributes nothing to it because flipping a signal does not change how long it lasts.",
                        "whys": [
                            "$x$ occupied 4 units of argument and $y$ occupies 2 units of time, so the width is halved — which is what a factor of 2 multiplying $t$ must do, and the reflection contributes nothing to it because flipping a signal does not change how long it lasts.",
                            "Doubling is what $x(t/2)$ does. A coefficient *larger* than one on $t$ makes the signal run faster and therefore finish sooner; it is the reciprocal that scales the duration.",
                            "An unchanged width would mean the argument's coefficient was $\\pm 1$. It is $-2$, and only the sign of that is free of consequence for the width.",
                            "A quarter would need a coefficient of 4. The 4 in this argument is the constant, not the multiplier — which is the confusion the whole exercise exists to break.",
                        ],
                    },
                    {
                        "prompt": "$4 - 2t = -2(t - 2)$. What shift does that reveal?",
                        "hole": "?",
                        "opts": [
                            "delay of 2",
                            "delay of 4",
                            "advance of 2",
                            "advance of 4",
                        ],
                        "a": 0,
                        "why": "Written as $-2(t - 2)$ the argument is a reflection-and-compression applied to $t - 2$, and $t - 2$ is a delay of 2. Check it against the interval: $x(-2t)$ would be non-zero on $-3 \\le t \\le -1$, and shifting that right by 2 gives $-1 \\le t \\le 1$, the answer already obtained.",
                        "whys": [
                            "Written as $-2(t - 2)$ the argument is a reflection-and-compression applied to $t - 2$, and $t - 2$ is a delay of 2. Check it against the interval: $x(-2t)$ would be non-zero on $-3 \\le t \\le -1$, and shifting that right by 2 gives $-1 \\le t \\le 1$, the answer already obtained.",
                            "4 is the constant as it appears before the argument is factorised, and it is the number the eye reaches for. Factorising divides it by the coefficient of $t$, which is the entire content of this line.",
                            "The sign is inverted. An advance of 2 would put the signal at $-3 \\le t \\le -1$, which is where $x(-2t)$ sits before any shift at all.",
                            "Both the size and the direction are wrong — this is the raw constant read off with the sign flipped as well.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "From the definition to $A\\sqrt{D}$, and to the square wave",
                "minutes": 12,
                "vars": ["V_H", "V_L", "D", "T", "A", "P"],
                "brief": r'''
A two-level periodic waveform: it sits at $V_H$ for a fraction $D$ of every period $T$
and at $V_L$ for the remaining $1 - D$. Almost every digital signal, every PWM drive and
every switching converter node is this waveform.

Its mean square can be written down without an integral sign, because the square takes
only two values and the "integral" is two rectangles. Do that, and three standard results
fall out of the same expression — which is the point of deriving it rather than
remembering three formulas.
''',
                "steps": [
                    {
                        "prompt": "Over one period the waveform squared is $V_H^2$ for a time $DT$ and $V_L^2$ for a time $(1-D)T$. Write the total area under $x^2(t)$ across one period.",
                        "given": "Area under a constant is the constant times the width, and the two stretches do not overlap.",
                        "answer": "V_H^2 D T + V_L^2 (1 - D) T",
                        "placeholder": "V_H^2 \\cdot (\\ldots) + V_L^2 \\cdot (\\ldots)",
                        "hint": "Two rectangles: height $V_H^2$ with width $DT$, and height $V_L^2$ with width $(1-D)T$.",
                        "deconstruct": [
                            "The high stretch lasts $DT$ and contributes $V_H^2 \\cdot DT$.",
                            "The low stretch lasts $T - DT = (1-D)T$ and contributes $V_L^2(1-D)T$.",
                        ],
                    },
                    {
                        "prompt": "The mean square $P$ is that area divided by the period. Write $P$.",
                        "answer": "V_H^2 D + V_L^2 (1 - D)",
                        "hint": "Every term carries a factor $T$, so the period cancels completely.",
                        "deconstruct": [
                            "Divide each term by $T$.",
                            "Nothing depending on $T$ survives — which is the statement that only the *fractions* of the period matter, not its length.",
                        ],
                    },
                    {
                        "prompt": "Write the RMS value.",
                        "answer": "\\sqrt{V_H^2 D + V_L^2 (1 - D)}",
                        "hint": "RMS is the square root of the mean square. There is nothing to simplify yet.",
                        "deconstruct": [
                            "$x_{rms} = \\sqrt{P}$ by definition.",
                            "Substitute the $P$ from the previous step, unchanged.",
                        ],
                    },
                    {
                        "prompt": "Now the pulse train of the numeric exercise: it rests at zero, so put $V_L = 0$ and $V_H = A$, and simplify.",
                        "answer": "A \\sqrt{D}",
                        "placeholder": "A \\cdot \\ldots",
                        "hint": "The second term vanishes entirely, leaving $\\sqrt{A^2D}$.",
                        "deconstruct": [
                            "$V_L = 0$ kills the $(1-D)$ term whatever $D$ is.",
                            "$\\sqrt{A^2 D} = A\\sqrt{D}$ for positive $A$.",
                        ],
                    },
                    {
                        "prompt": "And the symmetric square wave: $V_H = A$, $V_L = -A$, $D = \\frac12$. Evaluate.",
                        "given": "Squaring removes the sign, so both terms have the same height.",
                        "answer": "A",
                        "hint": "$A^2\\cdot\\frac12 + (-A)^2\\cdot\\frac12 = A^2$, and the root of that is the amplitude itself.",
                        "deconstruct": [
                            "$(-A)^2 = A^2$, so both stretches contribute the same height.",
                            "The two halves sum to $A^2$ regardless of the duty cycle, and $\\sqrt{A^2} = A$.",
                        ],
                    },
                ],
                "closing": r'''
Three results from one line. A pulse train that rests at zero has RMS $A\sqrt{D}$; at
$D = 0.5$ that is $A/\sqrt2$, the same number as a sinusoid and for no shared reason.
A square wave that swings symmetrically about zero has RMS equal to its **amplitude** —
no $\sqrt2$ anywhere, because the waveform is at full magnitude the whole time and there
is nothing to average down.

That last result is the one to carry into the circuit problem at the end of this module,
where a $\pm 6$ V square wave is attenuated and the power it delivers is asked for. Divide
by $\sqrt2$ there out of habit and the answer comes out at half of what the resistor
actually dissipates.
''',
            },
            "tune": {
                "title": "Attenuate a square wave to 2.00 V RMS, and pay for it twice",
                "minutes": 9,
                "brief": r'''
An instrument's input stage accepts 2.00 V RMS and no more. What it is being fed is a
symmetric square wave swinging $\pm 12$ V — a logic-level signal, or a switching node,
or a comparator output. A two-resistor divider is the whole of the fix, and it is
resistive, so it scales every level by the same ratio and the RMS scales with it.

The first thing to get right is the number to divide down from. A $\pm12$ V square wave
is **12 V RMS**, not $12/\sqrt2 = 8.49$ V: it sits at full magnitude the entire time.
Design for 8.49 V and everything downstream sees 41% more than it was promised.

Then two constraints pull against each other, as they always do in a divider. The ratio
fixes the output and says nothing about the current; the current is set by how large the
two resistors are together. Draw too much and the source sags and the divider wastes
power. Draw too little and the node becomes a high-impedance antenna for every
interferer in the room, and the input's own bias current starts to matter.
''',
                "prompt": "Deliver 2.00 V RMS from a ±12 V square wave, drawing between 0.20 and 0.50 mA.",
                "note": "The model is driven with 12 V, which is both the amplitude and the RMS of this waveform. Both current bounds must hold at once.",
                "model": "divider",
                "initial": {"r1": 2200, "r2": 2200},
                "constants": {"vin": 12},
                "plotKey": "vout",
                "constraints": [
                    {"k": "vout", "label": "Vout = 2.00 V RMS ± 0.02", "eq": 2.00, "tol": 0.02},
                    {"k": "i", "label": "I ≤ 0.50 mA", "max": 0.50},
                    {"k": "i", "label": "I ≥ 0.20 mA", "min": 0.20},
                ],
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Delay, scaling and modulation: the transform's working properties",
            "summary": "Six lines of algebra that between them cover most of what anyone ever does to a spectrum, and one of which you can build out of two components.",
            "concepts": [
                "The transform is linear: $a x_1 + b x_2 \\leftrightarrow a X_1 + b X_2$, straight from the integral. That is why a spectrum can be assembled from pieces, and why every property below can be applied to one term of a sum without disturbing the others.",
                "**Time shift.** $x(t - t_0) \\leftrightarrow X(f)\\,e^{-j2\\pi f t_0}$. The magnitude spectrum is *completely unchanged*; the phase gains a term linear in frequency, of slope $-2\\pi t_0$. A delay is invisible on a magnitude plot, which is worth remembering before concluding that two measurements agree.",
                "The converse is the useful half: a system whose phase falls **linearly** with frequency delays every component by the same time and so passes the waveform's shape intact. Where the phase bends, components arrive at different times and the waveform spreads. The delay at frequency $f$ is $-\\frac{1}{2\\pi}\\frac{d\\angle H}{df}$, the **group delay**.",
                "**Frequency shift.** $x(t)e^{j2\\pi f_c t} \\leftrightarrow X(f - f_c)$: multiplying by a complex exponential slides the whole spectrum along the axis. Multiplying by a real cosine, which is what a mixer actually does, gives $\\frac12[X(f - f_c) + X(f + f_c)]$ — two copies at half height, one at each of $\\pm f_c$.",
                "So a baseband signal occupying $0$ to $B$ becomes, after modulation onto $f_c$, a band running from $f_c - B$ to $f_c + B$: **twice as wide** as it started, which is the price of the double sideband. It is the same theorem module 3 used for sampling, with an impulse train replaced by a single sinusoid — there the spectrum was copied to every multiple of $f_s$, here to one pair of frequencies.",
                "**Scaling.** $x(at) \\leftrightarrow \\frac{1}{|a|}X(f/a)$. Compress in time and the spectrum stretches *and* shrinks in height, and both halves are needed: the value at zero frequency is $X(0) = \\int x\\,dt$, and squeezing the signal into a shorter time leaves less area under it. Playing a recording at double speed is exactly this — an octave up, and less energy at every hertz.",
                "**Differentiation.** $\\frac{dx}{dt} \\leftrightarrow j2\\pi f\\,X(f)$. Differentiating multiplies every component by its own frequency and rotates it by $+90^\\circ$. That is why a differentiator amplifies noise: broadband noise has content everywhere, and the gain grows without limit as you go up. Integration is the reciprocal, $1/(j2\\pi f)$, and correspondingly smooths.",
                "**Duality.** The forward and inverse transforms differ only in the sign of the exponent, so every pair read backwards is another pair. A rectangle in time gives a $\\mathrm{sinc}$ in frequency; therefore a $\\mathrm{sinc}$ in time gives a rectangle in frequency — and the rectangle in frequency is the ideal brick-wall filter, whose impulse response is consequently infinitely long and starts before $t = 0$. Brick walls are unbuildable, and duality is the shortest proof of it.",
                "**Parseval, for energy signals**: $\\int|x(t)|^2dt = \\int|X(f)|^2df$. Energy counted in time equals energy counted in frequency, so $|X(f)|^2$ is an **energy spectral density** in joules per hertz. Module 2's version of the same statement was about power, because a periodic signal has no finite energy to count.",
                "And the pair this course keeps returning to: convolution in one domain is multiplication in the other, in both directions. Module 3 used it one way round to explain sampling; module 4 used it the other way round to replace a convolution with a product. Every property above is a special case of taking that seriously.",
            ],
            "read": [
                {
                    "title": "A delay, and the straight line it draws on a phase plot",
                    "minutes": 13,
                    "body": r'''
Two identical amplifiers sit on the bench. Between the second one and the analyser
somebody has left three hundred metres of coaxial cable coiled under the desk. Sweep
both with a network analyser, plot the magnitude of the response, and the two traces lie
on top of each other — flat, equal, to within the thickness of the pen. Nothing in that
measurement can tell you the cable is there.

Put a pulse through instead and the difference is obvious. Signal travels down that
cable at about two thirds of the speed of light, so

```
delay  =  300 m / (0.66 * 3e8 m/s)  =  1.52 us
```

and the second output arrives a microsecond and a half after the first. The delay is
real, it is measurable, it matters, and the magnitude plot has no room for it anywhere.
That is the fact this section is about: whatever a delay does to a spectrum, it does
nothing at all to the magnitude.

## Where the exponential comes from

Let $y(t) = x(t - t_0)$ — the same signal, starting $t_0$ later. Put it into the
transform and change variable to $u = t - t_0$, so that $t = u + t_0$ and $dt = du$. The
limits are $\pm\infty$ either way, so they do not move:

$$Y(f) = \int_{-\infty}^{\infty} x(t - t_0)\,e^{-j2\pi f t}\,dt
      = \int_{-\infty}^{\infty} x(u)\,e^{-j2\pi f (u + t_0)}\,du$$

Split the exponential into $e^{-j2\pi f u}\,e^{-j2\pi f t_0}$. The second factor does not
contain $u$, so it comes straight out of the integral, and what is left is the transform
of $x$:

$$Y(f) = e^{-j2\pi f t_0}\,X(f)$$

That is the whole derivation — one substitution and one factor lifted out. What it says
is worth more than how it was got. $|e^{-j\theta}| = 1$ for every real $\theta$, so

$$|Y(f)| = |X(f)| \qquad\text{and}\qquad \angle Y(f) = \angle X(f) - 2\pi f t_0$$

The magnitude spectrum is untouched, bin for bin. All of the delay has gone into the
phase, as a term that is **linear in frequency**, with slope $-2\pi t_0$ radians per
hertz, or $-360\,t_0$ degrees per hertz.

## Worked example: two milliseconds

Take $t_0 = 2.00$ ms. The slope is $-360 \times 0.002 = -0.720$ degrees per hertz, and
the phase contributed at a few frequencies is:

```
slope         -360 * t0  =  -360 * 0.002  =  -0.720 deg/Hz

  100 Hz      -0.720 * 100   =    -72.0 deg
  250 Hz      -0.720 * 250   =   -180.0 deg
  500 Hz      -0.720 * 500   =   -360.0 deg
 1000 Hz      -0.720 * 1000  =   -720.0 deg
 3000 Hz      -0.720 * 3000  =  -2160.0 deg
```

Two things in that column are worth stopping on.

The first is that at 500 Hz the delay is a whole cycle. Feed a steady 500 Hz sine into
this system and look at the output: it is a 500 Hz sine of the same amplitude, sitting at
the same place on the screen. Nothing you can measure with a single tone at 500 Hz
detects the delay. The same is true at 1 kHz, at 1.5 kHz, at every multiple of 500 Hz.
A single steady sinusoid is the worst possible probe for a delay, and that is not a
curiosity — it is the reason a network analyser reports phase in the first place.

The second is what an instrument does with $-2160^\circ$. Phase is plotted on an axis
that runs from $-180^\circ$ to $+180^\circ$, so every time the true line passes through a
multiple of $360^\circ$ the trace snaps back to the top and starts falling again. The
plot of a pure 2 ms delay is therefore a sawtooth with a tooth every 500 Hz, and it looks
like structure. It is not structure. It is one straight line cut into pieces by the plot
window, and anything you want to conclude from its slope has to be done on the unwrapped
version.

## The same delay is a different angle at every frequency

Read the column again and notice that the angle changes from line to line while the delay
does not. A delay is a fixed **time**, and a fixed time is a different fraction of a cycle
at every frequency: at 100 Hz, 2 ms is a fifth of a cycle; at 3 kHz it is six whole
cycles. The linear phase is exactly the statement that every component is turned by the
angle its own frequency demands, so that when they are added back up they line up where
they did before, just later.

Turn that around and it becomes the most useful sentence in the module. **A system whose
phase falls linearly with frequency delays the whole waveform and does not change its
shape.** A system whose phase does anything else moves the components by different times,
and the waveform that comes out is not the one that went in.

## Worked example: a constant phase shift is not a delay

Take a two-component signal — the first two terms of a square wave:

$$x(t) = \cos(2\pi\cdot 1000\,t) + \tfrac13\cos(2\pi\cdot 3000\,t)$$

Its peak is $1 + \tfrac13 = 1.3333$, at $t = 0$, where both cosines are at their maxima
together.

**System A** is a pure delay of 250 µs. The angles it applies are

```
1 kHz      -360 * 1000 * 250e-6  =   -90 deg
3 kHz      -360 * 3000 * 250e-6  =  -270 deg
```

Different angles, one time. The output is $x(t - 250\,\mu\text{s})$: same shape, same
peak of 1.3333, 250 µs later.

**System B** is a wideband $-90^\circ$ phase shifter — a Hilbert transformer, which is a
real device and sits inside every single-sideband transmitter. It turns *every* component
by $-90^\circ$, so the output is

$$y(t) = \sin(2\pi\cdot 1000\,t) + \tfrac13\sin(2\pi\cdot 3000\,t)$$

Its peak is not 1.3333. Write $\theta = 2\pi\cdot1000\,t$ and maximise
$\sin\theta + \tfrac13\sin3\theta$:

```
d/dtheta  =  cos(theta) + cos(3 theta)  =  2 cos(2 theta) cos(theta)  =  0

  theta =  45 deg    0.70711 + (1/3)(0.70711)  =  0.94281
  theta =  90 deg    1.00000 + (1/3)(-1.00000) =  0.66667
  theta = 135 deg    0.70711 + (1/3)(0.70711)  =  0.94281

peak      0.94281  against  1.33333     ratio 0.70711 = 1/sqrt(2)
```

Both systems have $|H(f)| = 1$ at every frequency. Both leave the magnitude spectrum
identical. One returns the waveform intact; the other cuts its peak by 29%, exactly a
factor of $\sqrt2$. If you sized a power amplifier's supply rail on B's output and then
fed it A's, it would clip — and the two signals are indistinguishable on a spectrum
analyser.

## Group delay: the delay a system actually applies

Real systems do not have perfectly straight phase. The thing to do with a curved phase
plot is to measure its slope where you care, and call that the delay there:

$$\tau_g(f) = -\frac{1}{2\pi}\,\frac{d\,\angle H(f)}{df}
            \qquad\text{or}\qquad
            \tau_g(f) = -\frac{1}{360}\,\frac{d\phi}{df}\ \ \text{with }\phi\text{ in degrees}$$

The justification is a first-order expansion. Over a band narrow enough that
$\phi(f) \approx \phi(f_0) + \phi'(f_0)(f - f_0)$, the linear part is a pure delay of
$-\phi'/2\pi$ and the constant part is a fixed rotation of the carrier. So a narrowband
packet comes out with its **envelope** delayed by $\tau_g$ and its carrier delayed by the
*phase* delay $-\phi/(2\pi f)$. Two different numbers, both meaningful, answering two
different questions.

## Worked example: what a first-order low-pass does at 1 kHz and 5 kHz

The RC low-pass from module 4, $R = 4.7$ kΩ and $C = 10$ nF, has
$H = 1/(1 + j2\pi fRC)$ and $\phi(f) = -\arctan(f/f_c)$ with $f_c = 1/(2\pi RC)$.
Differentiate the arctangent:

$$\frac{d\phi}{df} = -\frac{1/f_c}{1 + (f/f_c)^2}
\qquad\Longrightarrow\qquad
\tau_g(f) = \frac{1}{2\pi f_c}\cdot\frac{1}{1 + (f/f_c)^2} = \frac{RC}{1 + (2\pi f RC)^2}$$

With the numbers:

```
RC          4700 * 10e-9              =  47.00 us
fc          1/(2 pi * 47.00e-6)       =  3386.3 Hz

f = 0       47.00 / (1 + 0)           =  47.00 us
f = 1 kHz   47.00 / (1 + 0.29531^2)   =  47.00 / 1.08721  =  43.23 us
f = fc      47.00 / (1 + 1)           =  23.50 us
f = 5 kHz   47.00 / (1 + 1.47655^2)   =  47.00 / 3.18020  =  14.78 us
```

A 1 kHz component leaves 43.23 µs after it arrived; a 5 kHz component leaves 14.78 µs
after it arrived. They are smeared apart by 28.45 µs, which is about a seventh of a cycle
at 5 kHz. Nothing about the magnitude response says so.

The phase delay at 1 kHz is a different number again: $\phi = -16.45^\circ$, so
$-\phi/(360 f) = 16.45/(360\times 1000) = 45.70$ µs. Group delay 43.23 µs, phase delay
45.70 µs. Neither is wrong; they are answers to "when does the envelope arrive" and "how
far is the carrier rotated, expressed as a time".

## The mistake, and why it is tempting

Two, and they are related.

The first is concluding that two paths are equivalent because their magnitude responses
agree. Every measurement you are likely to take first is a magnitude measurement, and it
is the one that a specification is usually written in. The cable under the desk is
invisible to it. So is the difference between systems A and B above, which is the
difference between a clean waveform and one whose crest factor has changed by 3 dB.

The second is dividing the phase at one frequency by that frequency and calling the
result the delay. That is the *phase* delay, and for a pure delay it happens to equal the
group delay exactly: $\phi = -2\pi f t_0$ gives $-\phi/(2\pi f) = t_0$ and
$-\phi'/(2\pi) = t_0$, the same number by both routes. Every first example anyone meets
is a pure delay, so the distinction never announces itself, and then a filter with curved
phase turns up and the two numbers separate — as they did above, by 2.5 µs out of 45.

## Where the idea stops

The theorem holds for $t_0 < 0$ as happily as for $t_0 > 0$: $x(t + 1\,\text{ms})$ has
spectrum $X(f)e^{+j2\pi f\cdot 0.001}$, and there is nothing wrong with that pair. There
is a great deal wrong with a *system* that does it, because it would produce output before
the input arrived. The shift theorem is a statement about signals; causality is a
constraint on systems, and the two are separate. That gap is where module 1's causality
condition earns its keep.

Group delay is a **local** description and it is honest only while the signal's band is
narrow enough that the linear term dominates the expansion. Push a wideband pulse through
a filter whose group delay varies substantially across the pulse's own bandwidth and no
single number describes what happens: the pulse spreads, different parts of it arrive at
different times, and you need all of $H(f)$ rather than one derivative of its phase. The
low-pass above is already in that territory for anything wider than about a kilohertz.

Group delay can also come out negative — near a deep notch, or in a circuit with a
right-half-plane zero — and that is not a violation of anything. It means an interpolated
feature of the envelope, its peak, moved forward; the leading edge of the signal did not,
and no information arrived early.

And all of it assumes LTI. A limiter, a compressor, an automatic gain control or anything
that saturates has a "delay" that depends on the signal, and none of these statements
apply to it at all.
''',
                },
                {
                    "title": "Multiplying by a cosine: sidebands, mixers and the image",
                    "minutes": 13,
                    "body": r'''
Speech runs out of energy somewhere around 3.4 kHz. Suppose you wanted to radiate it
directly. An antenna has to be a serious fraction of a wavelength to radiate anything at
all, and at 3 kHz

```
wavelength    c / f  =  3e8 / 3000    =  100 km
quarter wave                          =   25 km
```

so the whip on the roof would be twenty-five kilometres tall. And if you solved that,
every talker in the world would still be sharing one band, on top of each other, with no
way to separate them.

Both problems have the same fix: move the band somewhere else, and move different
people's bands to different places. There is exactly one operation that slides a spectrum
along the frequency axis, and this section is about it.

## The complex version first, because it is one line

Multiply a signal by a complex exponential and transform:

$$\int_{-\infty}^{\infty} x(t)\,e^{j2\pi f_c t}\,e^{-j2\pi f t}\,dt
= \int_{-\infty}^{\infty} x(t)\,e^{-j2\pi (f - f_c) t}\,dt
= X(f - f_c)$$

Nothing happened except that two exponents were added. The spectrum is picked up and put
down $f_c$ higher, unchanged in shape and unchanged in height.

Notice what it is the mirror of. The previous section shifted in **time** and got a
multiplying exponential in **frequency**; this one multiplies by an exponential in time
and gets a shift in frequency. It is one theorem seen from either side, and that
symmetry is duality, which the next section makes explicit.

## The real version, which is what a multiplier actually does

$e^{j2\pi f_c t}$ is not a voltage and no oscillator produces one. What a mixer produces
is $x(t)\cos(2\pi f_c t)$, and Euler splits the cosine into two exponentials:

$$\cos(2\pi f_c t) = \tfrac12 e^{j2\pi f_c t} + \tfrac12 e^{-j2\pi f_c t}$$

Linearity then applies the shift theorem to each half separately:

$$x(t)\cos(2\pi f_c t) \;\longleftrightarrow\; \tfrac12 X(f - f_c) + \tfrac12 X(f + f_c)$$

**Two** copies, each at **half** height, one slid up to $+f_c$ and one down to $-f_c$.
The second copy is not an accounting nuisance. A real signal has $X(-f) = X^*(f)$, so its
negative-frequency half is a mirror carrying the same information; the copy landing at
$-f_c$ is what makes the sum come out real, and it is what a real multiplier is obliged to
produce.

## Worked example: one tone on one carrier

Take $x(t) = \cos(2\pi\cdot 3000\,t)$ — a 1 V, 3 kHz tone — and a carrier at 100 kHz.
Use the product-to-sum identity, which is the two-exponential expansion multiplied out:

```
cos(a) cos(b)  =  1/2 [ cos(a - b) + cos(a + b) ]

  a = 2 pi 3000 t,  b = 2 pi 100000 t

  output  =  0.5 cos(2 pi *  97000 t)  +  0.5 cos(2 pi * 103000 t)
```

Two lines, at 97 kHz and 103 kHz, each of amplitude 0.5 V. And **no line at 100 kHz** —
the carrier itself is absent from the output, which is why this is called double-sideband
*suppressed carrier*.

The power bookkeeping is worth doing once:

```
before      one tone, amplitude 1        mean square  =  1^2/2      =  0.500 V^2
after       two tones, amplitude 0.5     mean square  =  2 * 0.5^2/2 =  0.250 V^2
```

Modulation halves the power — a flat 3 dB, paid once, and it is the reason a demodulator
has to put a gain back in.

## Worked example: a whole band, and the width it costs

Now the real case. Telephone-grade speech occupies 300 Hz to 3.40 kHz. Put it on the
standard AM intermediate frequency of 455 kHz:

```
lower sideband    455 - 3.40  =  451.60 kHz   ... up to  455 - 0.30 = 454.70 kHz
upper sideband    455 + 0.30  =  455.30 kHz   ... up to  455 + 3.40 = 458.40 kHz

occupied span     458.40 - 451.60           =    6.80 kHz
information       3.40 - 0.30               =    3.10 kHz
```

Two things fall out. The lower sideband is **reversed**: the highest audio frequency lands
at the lowest radio frequency, because the copy at $-f_c$ has been folded up around zero.
And the occupied band is 6.80 kHz wide although the information is only 3.10 kHz wide —
partly the doubling, and partly the 600 Hz hole sitting around 455 kHz where the missing
audio below 300 Hz would have been. That hole is inside the occupied band, cannot be sold
to anybody else, and is why occupied bandwidth is always measured edge to edge.

Spending 6.80 kHz to carry 3.10 kHz is the argument for single sideband: filter one copy
away, transmit 3.10 kHz, and make the receiver supply the carrier it no longer gets.

## Worked example: the image, which is the theorem running downwards

The same multiplication moves a band *down* as easily as up, and that is how every
receiver built since about 1920 works: multiply everything the antenna delivers by a local
oscillator, and keep whatever lands on a fixed intermediate frequency where the selective
filtering can be done once and properly.

Tune to a station at 98.1 MHz with an IF of 10.7 MHz, and put the local oscillator above
the signal:

```
LO        98.1 + 10.7  =  108.8 MHz

products at | f_RF - f_LO | = 10.7 MHz:

     | f - 108.8 | = 10.7    ->    f = 98.1 MHz    (the wanted station)
                              or   f = 119.5 MHz   (the image)

separation   119.5 - 98.1  =  21.4 MHz  =  2 * f_IF
```

Anything at 119.5 MHz comes down to exactly 10.7 MHz too, lands on top of the wanted
signal, and no filter *after* the mixer can ever separate them again — they are at the
same frequency. So the rejection has to happen **before** the mixer, and the only thing
that makes it feasible is that the image is $2f_{IF}$ away rather than one channel away.
That is the whole reason for choosing a high intermediate frequency: it buys the
preselector 21.4 MHz of room to work in.

## Getting the signal back out

Multiply by the carrier a second time. With $y(t) = A\cos(2\pi f_m t)\cos(2\pi f_c t)$,

$$y(t)\cos(2\pi f_c t) = A\cos(2\pi f_m t)\cos^2(2\pi f_c t)
= \tfrac{A}{2}\cos(2\pi f_m t) + \tfrac{A}{2}\cos(2\pi f_m t)\cos(2\pi\cdot 2f_c\,t)$$

using $\cos^2\theta = \tfrac12(1 + \cos 2\theta)$. The first term is the original signal
back, at **half** its original amplitude; the second sits up around $2f_c$ and a low-pass
disposes of it. The derivation exercise in this module walks the whole path.

The half matters, and so does what happens if the local copy is not in phase. Multiply
instead by $\cos(2\pi f_c t + \theta)$ and the baseband term becomes
$\tfrac{A}{2}\cos\theta\cos(2\pi f_m t)$: at $\theta = 30^\circ$ that is a loss of
1.25 dB, and at $\theta = 90^\circ$ the output is **exactly zero**. That quadrature null
is not a fault to be engineered away — it is what lets two entirely independent signals
share one carrier, one on the cosine and one on the sine, which is what every digital
radio in the building is doing right now.

## The mistake, and why it is tempting

Expecting the modulated signal to be the same width as the baseband one. "Shifting" sounds
like sliding a picture sideways, and for the complex-exponential version that is precisely
right: one copy, same width, same height. The doubling comes entirely from the second copy
that a *real* cosine drags in, and that copy exists because a real signal's spectrum has a
negative-frequency half which is not empty. Anyone who has only ever drawn one-sided
spectra has never seen the half that is about to be folded up onto the carrier, and the
factor of two arrives as a surprise.

The second mistake is expecting to find the carrier in the output. It is not there. Classic
broadcast AM adds it back deliberately so that a cheap envelope detector will work, and
pays for the convenience: at 100% tone modulation two thirds of the transmitted power is
in a carrier that carries no information whatever.

## Where the idea stops

A real mixer does not multiply by a sinusoid. The good ones **switch**, which is
multiplication by a square wave, and module 2 already gave that square wave's spectrum:
$\frac{4}{\pi}\left[\cos\omega_c t - \frac13\cos 3\omega_c t + \frac15\cos 5\omega_c t -
\cdots\right]$. So a switching mixer also brings signals near $3f_{LO}$ down to the same
IF, 9.5 dB weaker, and near $5f_{LO}$, 14.0 dB weaker. Those harmonic responses are as
real as the image and the preselector has to deal with them too.

A diode or transistor mixer is not even bilinear — it is a nonlinearity being used for
its second-order term — so it produces components at $m f_1 \pm n f_2$ for many small
integers, and the third-order two-tone products land *inside* the wanted channel where no
filter can reach them. That is intermodulation, it is a whole subject, and none of it is
described by this theorem, which assumes an ideal multiplier and gets exactly two outputs.

And if $f_c < B$ the two copies overlap. The sidebands fold onto each other, the sum is
not invertible, and no filter afterwards can undo it. That is module 3's aliasing
condition wearing narrowband clothes: the same theorem, the same failure, and the same
cure — leave enough room before you copy.
''',
                },
                {
                    "title": "Stretching, differentiating, and reading the table backwards",
                    "minutes": 13,
                    "body": r'''
Play a recording at double speed. Everybody notices the first thing that happens: it goes
up an octave, and every frequency in it doubles. Almost nobody notices the second thing,
which is that it also gets quieter — not quieter overall, but quieter *per hertz*, because
the same amount of signal is now spread across twice as much frequency axis. The scaling
theorem is those two facts written together, and the second half is the one people drop.

## Scaling, derived

Let $y(t) = x(at)$ with $a > 0$, and substitute $u = at$, so $t = u/a$ and $dt = du/a$:

$$Y(f) = \int_{-\infty}^{\infty} x(at)\,e^{-j2\pi f t}\,dt
= \frac{1}{a}\int_{-\infty}^{\infty} x(u)\,e^{-j2\pi (f/a) u}\,du
= \frac{1}{a}\,X\!\left(\frac{f}{a}\right)$$

For $a < 0$ the substitution also reverses the limits of integration, and putting them
back the right way round supplies a second minus sign, so the general statement carries
$|a|$:

$$x(at) \;\longleftrightarrow\; \frac{1}{|a|}\,X\!\left(\frac{f}{a}\right)$$

The $1/|a|$ is not bookkeeping, and there is a one-line check that fixes it in place.
Setting $f = 0$ in the definition gives $X(0) = \int x(t)\,dt$ — the value at DC is the
area under the signal. Squeeze the signal into a quarter of the time without changing its
height and there is a quarter of the area left. The height of the spectrum at DC must fall
by four, and by continuity so must everything near it.

## Worked example: a pulse, played back four times faster

A 2.00 V rectangular pulse, 200 µs wide. Module 3 established that its transform is
$A\tau\,\mathrm{sinc}(f\tau)$, with peak $A\tau$ and nulls every $1/\tau$.

```
original          A = 2.00 V,  tau = 200 us

  X(0)            A tau      =  2.00 * 200e-6   =  4.00e-4 V s   ( = 400 uV s )
  first null      1/tau      =  1/200e-6        =  5.00 kHz
  energy          A^2 tau    =  4.00 * 200e-6   =  8.00e-4 V^2 s

played at a = 4   width becomes 200/4 = 50.0 us

  by the theorem  X_new(0)   =  (1/4) * 4.00e-4 =  1.00e-4 V s
  directly        A tau'     =  2.00 * 50.0e-6  =  1.00e-4 V s     agrees
  first null      X(f/4) = 0 first at f/4 = 5.00 kHz  ->  f = 20.0 kHz
  directly        1/50.0e-6                          =  20.0 kHz   agrees
  energy          A^2 tau'   =  4.00 * 50.0e-6  =  2.00e-4 V^2 s   ( a quarter )
```

Four times the bandwidth for a quarter of the energy. That is the reciprocal-spreading
rule of module 3 with the bookkeeping attached: there is no operation in the time domain
that makes a signal short *and* narrow, and speeding it up buys bandwidth at the exact
rate the theorem charges.

## Differentiation, and the noise it lifts out of nowhere

Write the signal as its own inverse transform, $x(t) = \int X(f)e^{j2\pi f t}df$, and
differentiate under the integral sign. Each component's $e^{j2\pi f t}$ brings down a
factor $j2\pi f$ and nothing else changes:

$$\frac{dx}{dt} \;\longleftrightarrow\; j2\pi f\,X(f)$$

A gain equal to the frequency, and a rotation of exactly $+90^\circ$ at every frequency.
Both halves of that are measurable, and the build in this module measures them.

The consequence people meet the hard way: take a strain-gauge output carrying 100 mV of
real signal at 100 Hz, plus 1 mV of mains-harmonic pickup at 20 kHz. The interferer is
40 dB down and nobody would give it a second thought. Now differentiate, which is what you
do if what you actually want is a rate of change.

```
signal       0.100 V at    100 Hz   ->  0.100 * 2 pi * 100    =    62.83 V/s
interferer   0.001 V at  20.0 kHz   ->  0.001 * 2 pi * 20000  =   125.66 V/s

before       20 log10(0.001/0.100)  =  -40.0 dB
after        20 log10(125.66/62.83) =   +6.02 dB
```

The interferer is now twice the signal. A 46 dB swing, and the differentiator did not
generate a single new frequency — it is perfectly linear, one of the operations for which
$S\{ax_1 + bx_2\} = aS\{x_1\} + bS\{x_2\}$ is obvious. It simply weights by $f$, and
broadband noise has content at every $f$ there is.

This is why every practical differentiator is band-limited somewhere, and it is why the
CR high-pass in this module's build stops differentiating above its corner. That levelling
off is not a defect of the circuit. It is the noise gain being capped.

Integration is the reciprocal, $1/(j2\pi f)$: divide by frequency, rotate $-90^\circ$,
smooth rather than sharpen. It has the mirror-image pathology — the gain grows without
limit as $f \to 0$, so any DC offset at the input integrates into a ramp that eventually
finds a supply rail. Both operations misbehave at one end of the axis, and the ends are
opposite ones.

## Duality, and why brick walls are unbuildable

The forward and inverse transforms differ only in the sign of the exponent. So every pair,
read backwards, is another pair. Module 3 established that a rectangle in time gives a
$\mathrm{sinc}$ in frequency; duality therefore hands over, for free, that a
$\mathrm{sinc}$ in time gives a rectangle in frequency.

A rectangle in frequency is the ideal brick-wall filter — flat to $B$, zero above it,
nothing in between. Its impulse response is consequently a sinc, and a sinc is two-sided
and never ends. Take $B = 4$ kHz:

```
h(t)  =  2B sinc(2B t)  =  8000 sinc(8000 t)

  zero crossings every   1/8000  =  125 us,  in both directions
  h(t) is non-zero for every t < 0
```

The output at any instant would depend on input that has not arrived. By module 1's
definition the filter is not causal, and no arrangement of components will produce it. Note
which objections do *not* apply: the sinc's energy is finite (Parseval, below, makes it the
area of the rectangle), and its peak is finite too. Causality is the whole of the
obstruction.

What gets built instead is a truncation. Keep the sinc out to, say, ten zero crossings
either side — $\pm 1.25$ ms — and then shift the whole thing right by 1.25 ms so that
nothing survives at negative time. It is now causal, and it costs a fixed 1.25 ms of
latency. Halve the width of the transition band and you need twice as many crossings and
twice the latency. Sharpness is bought with delay, at a published exchange rate, and
duality is where the rate comes from.

Some functions are their own duals, which is worth knowing because they are the ones that
turn up when a problem is symmetric in the two domains: the Gaussian is one, and the
impulse train of module 3's sampling is another.

## Parseval, and what the squared magnitude is

$$\int_{-\infty}^{\infty} |x(t)|^2\,dt = \int_{-\infty}^{\infty} |X(f)|^2\,df$$

Energy counted in time equals energy counted in frequency. That makes $|X(f)|^2$ an
**energy spectral density** in V²s per hertz — which is exactly what a spectrum analyser
is reporting when it quotes a number per hertz rather than per bin.

Back to the pulse, by both routes:

```
time side        E  =  A^2 tau           =  4.00 * 200e-6      =  8.00e-4 V^2 s

frequency side   X(f) = A tau sinc(f tau),  and  integral of sinc^2(f tau) df = 1/tau

                 E  =  (A tau)^2 * (1/tau)  =  A^2 tau         =  8.00e-4 V^2 s
```

Same number, by a completely different road. Which is what makes the next question easy to
ask: how much of that energy is inside the main lobe, $|f| < 1/\tau = 5.00$ kHz? The
integral of $\mathrm{sinc}^2$ over $\pm1$ is 0.9028, so:

```
inside the main lobe      |f| < 5 kHz    90.3 % of the energy
out to the third null     |f| < 15 kHz   96.6 %
```

Band-limit a 200 µs pulse to 5 kHz and nine tenths of it survives. The missing tenth is
not lost quietly — it is exactly what puts the overshoot and ringing on the pulse's edges,
which is module 2's Gibbs behaviour arriving from the aperiodic side.

## The mistake, and why it is tempting

Applying Parseval as written to a periodic signal. A steady sine wave has infinite energy;
both integrals diverge; the statement is true and useless. Module 2's version — average
power equals the sum of the squared Fourier coefficients — is the one that applies to
periodic signals, and it counts power rather than energy. The trap is that both are called
Parseval's theorem, they look almost identical written down, and the difference between
them is which class of signal you are holding.

The other one is dropping the $1/|a|$ in scaling. It survives being ignored for a long time
because spectra are almost always plotted with an auto-scaled vertical axis, on which the
height is invisible and only the shape is read. It stops surviving the moment two spectra
have to be compared, or a level has to be predicted.

## Where these ideas stop

The scaling theorem scales the **whole** signal, argument and all. Speeding recorded audio
up with pitch correction is not this operation — it is not even LTI, and no transform pair
describes it, which is why it needs an algorithm rather than a formula.

The differentiation pair requires that $dx/dt$ have a transform at all. The derivative of a
step is an impulse, which is not a function; the pair survives only because the impulse is
defined by what it does inside an integral, and module 5 spent a page on exactly that.
More sharply: $j2\pi f$ grows without bound, so the transform of a derivative can fail to
exist even when $X(f)$ is perfectly well behaved. Differentiation is the one property on
this list that can take a signal outside the class it started in.

And Parseval as stated needs finite energy. A measured spectrum computed from a finite
record is not $X(f)$ either — it is $X(f)$ convolved with the transform of the record's
own window, which is the subject of module 9 and the reason a tone in a real analyser is
never one line.
''',
                },
            ],
            "build": {
                "title": "A differentiator, which is $j2\\pi f$ made of two components",
                "minutes": 25,
                "brief": r'''
$\dfrac{dx}{dt} \leftrightarrow j2\pi f\,X(f)$ says that a differentiator has a gain
proportional to frequency and a phase of exactly $+90^\circ$ at every frequency. Both
halves of that are measurable, so build one.

A capacitor in series from the source with a resistor from the output node to ground —
a **CR high-pass** — has $H = \dfrac{j\omega RC}{1 + j\omega RC}$. Well below its corner
the denominator is 1 and what is left is $j\omega RC$: gain proportional to frequency,
phase $+90^\circ$. It differentiates, and it does so only in the band where that
approximation holds.

Meet all four of these, with the probe on the output node:

1. **Nothing at DC.** At 1 Hz the output must be below 2% of the source. A derivative of
   a constant is zero and the circuit has to agree.
2. **Gain proportional to frequency.** Doubling from 100 Hz to 200 Hz, and again from
   200 Hz to 400 Hz, must each double the output, within 5%.
3. **A quarter turn of phase.** At 100 Hz the output must lead the input by more than
   $80^\circ$.
4. **Big enough to be worth having.** At 100 Hz the output must be at least 1% of the
   input.

## Where the window is

Requirements 2 and 3 both push the corner frequency **up**, away from the band being
differentiated, because the approximation $H \approx j\omega RC$ only holds for
$f \ll f_c$. Requirement 4 pushes it **down**, because the gain in that band is
$f/f_c$ and a corner at a megahertz leaves nothing at the output. Work both bounds out
before drawing: they meet at roughly a factor of ten, and $f_c = 5$ kHz sits in the
middle of it.

That tension is the whole character of a passive differentiator: it is accurate only
where it is small, and the more accurate you make it the less signal you have left.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "OUT", "x": 11, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [11, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "C", "x": 6, "y": 4, "rot": 0, "value": 1e-8},
                        {"id": "p3", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 3183.0989},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [9, 4], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [9, 4], "b": [11, 4]},
                    ],
                },
                "checks": [
                    {"name": "one source, and a constant produces nothing", "code": r'''
c.assert(c.count('V') === 1, 'Drive the network from exactly one source; found ' + c.count('V') + '.');
const vs = c.values('V')[0];
const low = c.gain(1) / vs;
c.assert(low < 0.02,
  'At 1 Hz the probe still sees ' + (low * 100).toFixed(1) + '% of the source. The ' +
  'derivative of something that is barely changing is nearly zero, so a differentiator ' +
  'has to block DC — the capacitor belongs in series with the signal, not across it.');
'''},
                    {"name": "the output is proportional to frequency", "code": r'''
const g1 = c.gain(100), g2 = c.gain(200), g3 = c.gain(400);
const r1 = g2 / g1, r2 = g3 / g2;
c.assert(r1 > 1.9 && r1 < 2.1,
  'Going from 100 Hz to 200 Hz multiplied the output by ' + r1.toFixed(3) + '. ' +
  'Differentiation multiplies by frequency, so doubling the frequency must double the ' +
  'output; a ratio well under 2 means the corner is inside the band being differentiated.');
c.assert(r2 > 1.9 && r2 < 2.1,
  'Going from 200 Hz to 400 Hz multiplied the output by ' + r2.toFixed(3) + ' rather ' +
  'than 2. The proportionality has to hold across the whole band, and it fails at the ' +
  'top of it first.');
'''},
                    {"name": "and it leads by close to a quarter turn", "code": r'''
const p = c.phase(100);
c.assert(p > 80 && p < 90.001,
  'At 100 Hz the output leads by ' + p.toFixed(1) + ' degrees. Multiplying a spectrum ' +
  'by j is a +90 degree rotation, and a single-pole high-pass approaches it from below ' +
  '— so anything under 80 degrees means the corner has been put too close to 100 Hz.');
'''},
                    {"name": "large enough to be worth building", "code": r'''
const vs = c.values('V')[0];
const g = c.gain(100) / vs;
c.assert(g >= 0.01,
  'At 100 Hz the output is only ' + (g * 100).toFixed(3) + '% of the input. The gain in ' +
  'the differentiating band is f/fc, so pushing the corner ever higher buys accuracy ' +
  'with signal you no longer have. Keep it at or below about 10 kHz.');
'''},
                ],
                "hints": [
                    "The capacitor goes in series from the source and the resistor from the output node to ground. Swap them and you have a low-pass, which integrates instead.",
                    "Requirement 2 is the binding one at the bottom: the ratio $g(400)/g(200)$ is $2\\sqrt{1+(200/f_c)^2}/\\sqrt{1+(400/f_c)^2}$, and holding it above 1.9 needs $f_c \\gtrsim 1$ kHz.",
                    "Requirement 4 is the binding one at the top: $|H(100)| \\approx 100/f_c \\ge 0.01$ needs $f_c \\le 10$ kHz.",
                    "Take $f_c = 5$ kHz, choose a round capacitor — 10 nF — and let $R = 1/(2\\pi f_c C)$ decide the resistor. That is about 3.18 kΩ.",
                    "Without a ground the phase and the gain both mean nothing, and the checks will say so before they say anything about the filter.",
                ],
            },
            "quiz": {
                "title": "What each property actually predicts",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A signal is delayed by 2 ms. What happens to its spectrum?",
                        "opts": [
                            "the magnitude is scaled by 1/0.002 and the phase is untouched",
                            "the whole spectrum shifts up by 500 Hz",
                            "the magnitude is unchanged and the phase gains a term proportional to frequency",
                            "nothing at all — a delay is not visible in the frequency domain",
                        ],
                        "a": 2,
                        "why": r'''
$x(t - t_0) \leftrightarrow X(f)e^{-j2\pi f t_0}$, and $|e^{-j\theta}| = 1$, so the
magnitude spectrum is bit-for-bit identical. All of the delay is in the phase, as a
straight line of slope $-2\pi t_0$ — at 2 ms that is $-0.72^\circ$ per hertz. It is
genuinely invisible on a magnitude plot, which is a real trap when comparing two
measurements, but it is not invisible in the frequency domain: the phase plot shows it
plainly, and the slope of that plot *is* the delay.
''',
                    },
                    {
                        "q": "A signal occupying DC to 4 kHz multiplies a 1 MHz cosine. What band does the result occupy?",
                        "opts": [
                            "996 kHz to 1004 kHz — 8 kHz wide",
                            "1000 kHz to 1004 kHz — still 4 kHz wide",
                            "DC to 4 kHz, unchanged, plus a spike at 1 MHz",
                            "1 MHz alone, since the carrier dominates",
                        ],
                        "a": 0,
                        "why": r'''
Multiplying by a cosine copies the spectrum to $+f_c$ and $-f_c$ at half height. The
copy at $+1$ MHz brings the baseband's *negative* frequencies with it, which for a real
signal are the mirror of its positive ones — so the result runs from $f_c - B$ to
$f_c + B$ and is twice as wide as the baseband. Expecting it to stay 4 kHz wide is the
common error, and it is the difference between double-sideband and single-sideband
transmission: getting the bandwidth back down to $B$ takes an extra filter, which is
exactly why anyone bothers with single sideband.
''',
                    },
                    {
                        "q": "A recorded pulse is played back at twice the speed. What happens to its spectrum?",
                        "opts": [
                            "twice as wide and twice as tall",
                            "unchanged in shape, shifted up by an octave",
                            "half as wide and twice as tall",
                            "twice as wide and half as tall",
                        ],
                        "a": 3,
                        "why": r'''
$x(2t) \leftrightarrow \frac12 X(f/2)$: the frequency axis stretches by two and the
height falls by two. Both happen, and the second is easy to forget — the energy has to
go somewhere, and playing the pulse in half the time leaves half as much of it. This is
the reciprocal-spreading rule of module 3 stated as an equation: the product of a
signal's duration and its bandwidth cannot be reduced, so anything that shortens a
signal widens its spectrum.
''',
                    },
                    {
                        "q": "Why does a differentiator amplify noise?",
                        "opts": [
                            "because differentiation is a non-linear operation and generates harmonics",
                            "because it multiplies each component by $j2\\pi f$, so the gain grows without limit with frequency",
                            "because the capacitor in it adds thermal noise of its own",
                            "because it inverts the phase, and inverted noise adds rather than cancels",
                        ],
                        "a": 1,
                        "why": r'''
The gain *is* the frequency. Broadband noise has content at every frequency and the
differentiator gives the highest of it the largest gain, so the output is dominated by
whatever was fastest and least wanted. Differentiation is perfectly linear — it is one
of the operations $S\{ax_1+bx_2\} = aS\{x_1\}+bS\{x_2\}$ obviously holds for — so
nothing new appears at any new frequency. Practical differentiators are always
band-limited for this reason: past some frequency they are made to stop.
''',
                    },
                    {
                        "q": "The ideal brick-wall low-pass has a $\\mathrm{sinc}$ impulse response. Why can it not be built?",
                        "opts": [
                            "because the sinc has infinite energy",
                            "because no real component has a perfectly flat response",
                            "because the sinc extends to $t < 0$, so the output would depend on input that has not arrived",
                            "because the sinc's peak is infinite",
                        ],
                        "a": 2,
                        "why": r'''
Causality. Duality says a rectangle in frequency is a sinc in time, and a sinc is
two-sided and never ends — so $h(t) \ne 0$ for $t < 0$, and by module 1's definition the
filter is not causal. It would have to respond before the input arrived. The sinc's
energy is finite (Parseval: it equals the area of the rectangle) and its peak is finite,
so neither of those is the obstruction. The practical consequence is that every real
sharp filter is a truncated, delayed approximation, and the sharper you want it the
longer you must wait.
''',
                    },
                    {
                        "q": "A pulse is measured to carry 2 nJ, computed by integrating $|x(t)|^2$ in time. What is $\\int_{-\\infty}^{\\infty}|X(f)|^2\\,df$?",
                        "opts": ["4 nJ, because the spectrum is two-sided", "1 nJ", "2 nJ", "it depends on the pulse shape"],
                        "a": 2,
                        "why": r'''
Parseval: the two integrals are equal, for every signal, with no shape-dependent factor.
The two-sided worry is already handled — the integral over $f$ runs from $-\infty$ to
$+\infty$ and the negative frequencies are exactly where the missing half lives, so
nothing has to be doubled. Restricting to positive $f$ *would* give 1 nJ, which is why
the single-sided convention always comes with a factor of two attached. The quantity
$|X(f)|^2$ is the energy spectral density, and it is what a spectrum analyser is really
plotting when it says dBm per hertz.
''',
                    },
                ],
            },
            "blanks": {
                "title": "The table of properties, with the right-hand column missing",
                "minutes": 9,
                "caption": "one operation per line, and what it does to the spectrum",
                "lang": "text",
                "brief": r'''
Six lines. Every one of them turns an operation on a signal into an operation on its
spectrum, and between them they cover most of what anyone does to a signal on purpose.

Nothing is executed here. Fill the right-hand column and then read the table as a
sentence about which operations are cheap in which domain — because that is the only
reason to keep it in your head.
''',
                "listing": """  time domain                          frequency domain
 ---------------------------------------------------------------
  x(t)                          <->    X(f)

  x(t - t0)                     <->    X(f) * ___

  x(t) * cos(2 pi fc t)         <->    ___

  x(a t),  with a > 1           <->    ___

  dx/dt                         <->    ___ * X(f)

  x(t) convolved with h(t)      <->    ___
""",
                "blanks": [
                    {
                        "prompt": "A delay leaves the magnitude alone. What does it multiply the spectrum by?",
                        "hole": "?",
                        "opts": ["exp(+j 2 pi f t0)", "exp(-j 2 pi f t0)", "1 / (j 2 pi f t0)", "t0"],
                        "a": 1,
                        "why": "A delay of $t_0$ multiplies by $e^{-j2\\pi f t_0}$ — unit magnitude, so the magnitude spectrum does not move, and a phase falling linearly at $-2\\pi t_0$ radians per hertz.",
                        "whys": [
                            "The sign is inverted, and that turns a delay into an advance: the output would come out before the input went in. The sign is worth fixing in your memory by the physics rather than by the formula.",
                            "A delay of $t_0$ multiplies by $e^{-j2\\pi f t_0}$ — unit magnitude, so the magnitude spectrum does not move, and a phase falling linearly at $-2\\pi t_0$ radians per hertz.",
                            "That is what *integration* multiplies by, up to a constant, and it changes the magnitude at every frequency. A delay must not change any magnitude at all.",
                            "A constant scale factor would change every component by the same amount and shift nothing in time. A delay has to depend on frequency, because a fixed time is a different fraction of a cycle at each one.",
                        ],
                    },
                    {
                        "prompt": "A real cosine, not a complex exponential. How many copies, and how tall?",
                        "hole": "?",
                        "opts": ["X(f - fc)", "2 X(f - fc)", "[X(f - fc) + X(f + fc)] / 2", "X(f) cos(2 pi fc f)"],
                        "a": 2,
                        "why": "$\\cos = \\frac12(e^{j\\omega_c t} + e^{-j\\omega_c t})$, so the spectrum is copied to $+f_c$ **and** $-f_c$, each at half height. Both copies are needed for the result to come out real.",
                        "whys": [
                            "One copy at $+f_c$ is what multiplying by $e^{j2\\pi f_ct}$ gives. That is a perfectly good operation, but its output is complex — a real mixer cannot produce it, and a real signal's spectrum must have the conjugate symmetry that the second copy supplies.",
                            "Doubling the height is backwards: the cosine splits its energy between two frequencies, so each copy is *half* the original, not twice it.",
                            "$\\cos = \\frac12(e^{j\\omega_c t} + e^{-j\\omega_c t})$, so the spectrum is copied to $+f_c$ **and** $-f_c$, each at half height. Both copies are needed for the result to come out real.",
                            "Multiplying the spectrum by a cosine *of frequency* is not an operation this table contains — it would be what happens if you multiplied in the wrong domain, and it is worth noticing that the argument written there is dimensionally nonsense.",
                        ],
                    },
                    {
                        "prompt": "Speeding a signal up stretches its spectrum. What happens to the height?",
                        "hole": "?",
                        "opts": ["X(f/a) / a", "a X(f/a)", "X(a f)", "X(f) / a"],
                        "a": 0,
                        "why": "$x(at) \\leftrightarrow \\frac{1}{|a|}X(f/a)$: wider by $a$ and shorter by $a$. The height must fall, because the signal now lasts a shorter time and there is less of it to transform.",
                        "whys": [
                            "$x(at) \\leftrightarrow \\frac{1}{|a|}X(f/a)$: wider by $a$ and shorter by $a$. The height must fall, because the signal now lasts a shorter time and there is less of it to transform.",
                            "The stretch is right and the height is upside down. Check it at $f = 0$: $X(0)$ is the area under $x$, and compressing the signal in time reduces that area, so the value at DC must go down.",
                            "$X(af)$ compresses the spectrum instead of stretching it, which is the answer for *slowing the signal down*. Compressing in one domain always stretches the other; nothing gets narrower in both.",
                            "A pure scale factor with no change of shape would mean the spectrum's width was independent of how fast the signal ran, and a pulse played back a thousand times faster would occupy the same band. It does not.",
                        ],
                    },
                    {
                        "prompt": "Differentiation, as a multiplier on each component.",
                        "hole": "?",
                        "opts": ["2 pi f", "1 / (j 2 pi f)", "-j 2 pi f", "j 2 pi f"],
                        "a": 3,
                        "why": "$j2\\pi f$: a gain equal to the frequency and a rotation of $+90^\\circ$. Both halves are measurable, and the build in this module measures them.",
                        "whys": [
                            "The magnitude is right and the rotation is missing. Differentiating a cosine gives a *negative sine* — a quarter cycle of shift — and dropping the $j$ throws that away, leaving a formula that cannot tell a differentiator from a plain rising-gain amplifier.",
                            "That is integration, the inverse operation. It divides rather than multiplies, so it suppresses the high frequencies a differentiator amplifies, and its $-90^\\circ$ is the mirror image.",
                            "The magnitude is right and the rotation goes the wrong way — this would be an operation that *lags* by a quarter cycle while amplifying with frequency, which is not something a derivative does.",
                            "$j2\\pi f$: a gain equal to the frequency and a rotation of $+90^\\circ$. Both halves are measurable, and the build in this module measures them.",
                        ],
                    },
                    {
                        "prompt": "The result module 4 was built on.",
                        "hole": "?",
                        "opts": ["H(f) convolved with X(f)", "H(f) X(f)", "H(f) + X(f)", "X(f) / H(f)"],
                        "a": 1,
                        "why": "Convolution in time is multiplication in frequency. It is what makes the frequency domain worth entering at all, and reading the table upwards shows the same theorem running the other way — module 3's sampling multiplied in time and convolved in frequency.",
                        "whys": [
                            "That is the theorem applied to itself: convolution in *one* domain becomes multiplication in the other, never convolution in both. If it did, nothing would have been gained by transforming.",
                            "Convolution in time is multiplication in frequency. It is what makes the frequency domain worth entering at all, and reading the table upwards shows the same theorem running the other way — module 3's sampling multiplied in time and convolved in frequency.",
                            "Addition in frequency corresponds to addition in time, which is the linearity line at the top of the table rather than this one. Two filters in cascade multiply; two signals arriving together add.",
                            "Division in frequency is deconvolution — a real and occasionally useful operation, and the reason a measured response can sometimes be divided out. It is not what a filter does to a signal.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "How far a delay turns one component",
                    "minutes": 4,
                    "brief": r'''
The mechanical one, so that the conversion between a delay and an angle is under your
fingers before anything is stacked on top of it.

An ideal delay line: whatever goes in comes out $1.50$ ms later, unchanged in amplitude.
$|H(f)| = 1$ at every frequency, so the entire description of this system is its phase.
''',
                    "prompt": "By how many degrees does the 400 Hz component of the output lag the input?",
                    "note": "In degrees, unwrapped — report the whole lag, not the angle a plot window would show. One decimal place is plenty.",
                    "figure": r'''
```
            +-------------------+
   x(t) --->|  delay  1.50 ms   |---> y(t) = x(t - 1.50 ms)
            +-------------------+

   The same 1.50 ms for every frequency in x. Nothing is attenuated:
   |H(f)| = 1 everywhere, and all of the system is in the phase.
```

One component of $x$ is a 400 Hz sinusoid. The question is about that component alone.
''',
                    "given": [
                        {"label": "Delay", "value": "1.50 ms"},
                        {"label": "Component", "value": "400 Hz"},
                        {"label": "Magnitude response", "value": "1 at every frequency"},
                    ],
                    "aside": "A delay is a fixed time, not a fixed angle. The 400 Hz component and "
                             "the 4 kHz component are held for the same 1.50 ms and turned by "
                             "angles ten times apart.",
                    "answer": 216.0,
                    "tol": 0.5,
                    "unit": "degrees",
                    "hint": "A delay contributes a phase of $-2\\pi f t_0$ radians, which is "
                            "$-360\\,f t_0$ degrees. The lag is the size of that.",
                    "wrong": "0.600 is the shift expressed in *cycles*. It is the right fraction "
                             "and one multiplication short of the answer. 144 is what an instrument "
                             "would plot, because $-216^\\circ$ and $+144^\\circ$ are the same "
                             "angle once the trace has wrapped; the component is still 216° behind. "
                             "21.6 comes from reading 1.50 ms as 0.150 ms.",
                    "why": r'''
```
phase slope     -360 * t0        =  -360 * 1.50e-3   =  -0.540 deg/Hz
at 400 Hz       -0.540 * 400                         =  -216.0 deg

lag             |-216.0|                             =   216.0 deg
```

Worth a sanity check in the time domain, because it takes three seconds and catches sign
errors and factor-of-ten errors together. One cycle of 400 Hz lasts $1/400 = 2.50$ ms, and
$1.50/2.50 = 0.600$ of a cycle. Six tenths of $360^\circ$ is $216^\circ$.

Now run the same arithmetic at 666.7 Hz, where one cycle lasts exactly 1.50 ms. The lag
comes out at $360^\circ$ — a full turn, which is no turn at all. Put a steady 666.7 Hz
sine into this delay line and the output is indistinguishable from the input: same
amplitude, same phase, sitting in the same place on the screen. The delay has not gone
anywhere; it is simply invisible to a probe that only ever sends one frequency at a time.
That is the whole argument for measuring phase across a sweep rather than at a point, and
for unwrapping the result before believing its slope.
''',
                },
                {
                    "title": "The width a voice takes up once it is on a carrier",
                    "minutes": 6,
                    "brief": r'''
An ideal multiplier, a speech signal, and the standard AM intermediate frequency. Nothing
here needs an integral: the modulation property says where each edge of the baseband ends
up, and the rest is arithmetic on four numbers.

The trap is deciding *which* four numbers. A band that runs from 300 Hz to 3.40 kHz has a
width of 3.10 kHz and a top edge of 3.40 kHz, and only one of those two belongs in this
calculation.
''',
                    "prompt": "What is the width of the band occupied by y — lowest frequency present to highest?",
                    "note": "In kilohertz. Count the positive-frequency side only; the negative-frequency half is its mirror and is not a second occupancy.",
                    "figure": r'''
```
                x(t) ---->[   X   ]----> y(t)
                              ^
                              |
                   cos(2 pi * 455 000 * t)

   x(t) holds 300 Hz to 3.40 kHz and nothing outside that.
   The multiplier is ideal: y is the product, with nothing added and nothing lost.

   the spectrum of y, sketched on a positive-frequency axis:

           ####                       ####
        ########                   ########
   -----+--------+--------|--------+--------+------------> f
        a        b     455 kHz     c        d

   wanted:  d - a
```
''',
                    "given": [
                        {"label": "Baseband", "value": "300 Hz to 3.40 kHz"},
                        {"label": "Carrier", "value": "455 kHz"},
                        {"label": "Operation", "value": "ideal multiplication, $x(t)\\cos(2\\pi f_c t)$"},
                    ],
                    "aside": "There is no line at 455 kHz. An ideal multiplier suppresses the "
                             "carrier; broadcast AM has one only because it is added back on "
                             "purpose.",
                    "answer": 6.8,
                    "tol": 0.05,
                    "unit": "kHz",
                    "hint": "Each edge of the baseband appears twice, at $455 - f$ and at "
                            "$455 + f$. Write all four, then take the outermost pair.",
                    "wrong": "3.40 kHz is the baseband left where it was — a shift that does not "
                             "change the width is the complex-exponential version, not what a real "
                             "cosine does. 6.20 kHz doubles the *information* bandwidth of "
                             "3.10 kHz; the edges of the occupied band are set by the top of the "
                             "baseband, not by its width. 3.10 kHz is what single sideband would "
                             "occupy after one copy had been filtered away.",
                    "why": r'''
```
lower sideband   455 - 3.40  =  451.60 kHz   up to   455 - 0.30  =  454.70 kHz
upper sideband   455 + 0.30  =  455.30 kHz   up to   455 + 3.40  =  458.40 kHz

occupied         458.40 - 451.60                                 =    6.80 kHz
information      3.40 - 0.30                                     =    3.10 kHz
```

Two features of that block are worth naming.

The lower sideband is **reversed**. The highest audio frequency, 3.40 kHz, lands at the
*lowest* radio frequency, 451.60 kHz, because that copy came from the negative-frequency
half of the spectrum and was folded up around zero. Feed it to a receiver that expects the
upper sideband and the speech comes out inside out.

And there is a 600 Hz hole in the middle, from 454.70 to 455.30 kHz, where the audio below
300 Hz would have been if there had been any. It is inside the occupied band, it cannot be
allocated to anybody else, and it is why occupied bandwidth is quoted edge to edge rather
than as a sum of the parts that carry something.

Spending 6.80 kHz to deliver 3.10 kHz of information is a ratio of 2.19, and that ratio is
the entire commercial argument for single sideband: filter one copy away, occupy
3.10 kHz, and make the receiver regenerate the carrier it is no longer sent.
''',
                },
                {
                    "title": "The differentiator at the frequency where it stops being one",
                    "minutes": 8,
                    "brief": r'''
The CR high-pass below is the circuit this module's build asks for: well under its corner
it has $H \approx j2\pi f RC$, a gain proportional to frequency and a phase of $+90^\circ$,
which is $j2\pi f$ built out of two components.

This question is asked at 5.00 kHz, which is not well under its corner. Work out what the
circuit actually does there, and then compare it with what the differentiator formula
claims.
''',
                    "prompt": "The source is a 1.00 V sinusoid at 5.00 kHz. What amplitude appears at the probe?",
                    "note": "In volts, three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                            {"id": "p2", "kind": "C", "x": 6, "y": 4, "rot": 0, "value": 1e-8},
                            {"id": "p3", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 3300},
                            {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                            {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [9, 4], "b": [11, 4]},
                        ],
                    },
                    # The source is 1 V, so the probed magnitude is |H| directly; dividing by
                    # the source value anyway keeps the answer honest if the drawing is edited.
                    "check": r'''
return c.gain(5000) / c.values('V')[0];
''',
                    "given": [
                        {"label": "$C$", "value": "10 nF, in series with the signal"},
                        {"label": "$R$", "value": "3.3 kΩ, output node to ground"},
                        {"label": "Source", "value": "1.00 V sinusoid at 5.00 kHz"},
                        {"label": "Probe", "value": "the junction of $C$ and $R$"},
                    ],
                    "aside": "The differentiator approximation predicts a gain of 1.04 at this "
                             "frequency. One resistor and one capacitor cannot produce more "
                             "voltage than they were given, so the approximation has already "
                             "failed before you finish reading it.",
                    "answer": 0.7197,
                    "tol": 0.004,
                    "unit": "V",
                    "hint": "$f_c = 1/(2\\pi RC)$ first. Then the exact high-pass magnitude, "
                            "$|H| = (f/f_c)/\\sqrt{1 + (f/f_c)^2}$ — the denominator is the part "
                            "the differentiator approximation throws away.",
                    "wrong": "1.04 V is $2\\pi f RC$, the differentiator formula used past the "
                             "point where it holds; it claims a passive network amplifies. 0.707 V "
                             "assumes 5.00 kHz is the corner, and the corner is at 4.82 kHz. "
                             "0.694 V is $1/\\sqrt{1 + (f/f_c)^2}$, the low-pass — the answer you "
                             "get with the two components swapped, which integrates instead.",
                    "why": r'''
```
corner        fc = 1/(2 pi R C) = 1/(2 pi * 3300 * 10e-9)  =  4822.9 Hz

ratio         f/fc = 5000 / 4822.9                         =  1.03672

exact         |H| = 1.03672 / sqrt(1 + 1.03672^2)
                  = 1.03672 / sqrt(2.07480)
                  = 1.03672 / 1.44042                      =  0.71974

so the probe sees                                              0.720 V
```

Set that against the approximation the circuit was built to embody. $2\pi f RC = f/f_c =
1.0367$, so the ideal differentiator says 1.04 V out of a 1.00 V source — 44% high, and
physically impossible into the bargain. The denominator that the approximation drops,
$\sqrt{1 + (f/f_c)^2}$, is exactly what stops a passive network from doing that.

The approximation is not bad everywhere; it is bad *here*. At 200 Hz the same two
expressions give 0.041433 and 0.041469, which differ by 0.086%. The error is
$\sqrt{1 + (f/f_c)^2}$ and it grows from nothing: negligible a decade below the corner,
1% at $f = f_c/7$, 44% at the corner itself.

The phase tells the same story from the other side. The exact phase here is $+43.97^\circ$,
not the $+90^\circ$ a derivative demands. A differentiator that turns its input by 44
degrees instead of 90 is not differentiating, whatever its magnitude plot looks like — and
that is the constraint the build's third check enforces.
''',
                },
                {
                    "title": "How long the low-pass holds a 1 kHz component",
                    "minutes": 9,
                    "brief": r'''
The same filter module 4 measured in decibels, asked a different question. A magnitude
response says how much of each component survives. It says nothing whatever about *when*
each one leaves, and that is the number wanted here.

The delay a filter applies at a frequency is the local slope of its phase:
$\tau_g = -\frac{1}{2\pi}\,d\phi/df$ with $\phi$ in radians. For this filter
$\phi(f) = -\arctan(f/f_c)$, so the differentiation is one line of calculus and the rest
is arithmetic.
''',
                    "prompt": "What is the group delay of this filter at 1.00 kHz?",
                    "note": "In microseconds, three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                            {"id": "p2", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 4700},
                            {"id": "p3", "kind": "C", "x": 9, "y": 6, "rot": 1, "value": 1e-8},
                            {"id": "p4", "kind": "GND", "x": 9, "y": 9},
                            {"id": "p5", "kind": "OUT", "x": 11, "y": 4},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [9, 4], "b": [11, 4]},
                        ],
                    },
                    # Group delay is the slope of the measured phase, so the check measures a
                    # slope: a symmetric difference 0.5 Hz either side of 1 kHz, converted from
                    # degrees per hertz to seconds and then to microseconds. Nothing about the
                    # component values is repeated here.
                    "check": r'''
const f = 1000, d = 0.5;
const slope = (c.phase(f + d) - c.phase(f - d)) / (2 * d);   /* degrees per Hz */
return -1e6 * slope / 360;
''',
                    "given": [
                        {"label": "$R$", "value": "4.7 kΩ"},
                        {"label": "$C$", "value": "10 nF"},
                        {"label": "Frequency", "value": "1.00 kHz"},
                        {"label": "Wanted", "value": "$-\\dfrac{1}{2\\pi}\\dfrac{d\\phi}{df}$ at that frequency"},
                    ],
                    "aside": "The time constant is 47.0 µs and the group delay at DC is exactly "
                             "that. The question is asked at 1 kHz, which is nearly a third of the "
                             "way to the corner, and the group delay of a single pole is not "
                             "constant.",
                    "answer": 43.23,
                    "tol": 0.15,
                    "unit": "µs",
                    "hint": "$\\dfrac{d}{df}\\arctan(f/f_c) = \\dfrac{1/f_c}{1 + (f/f_c)^2}$, which "
                            "gives $\\tau_g = \\dfrac{RC}{1 + (2\\pi f RC)^2}$. Then substitute.",
                    "wrong": "47.0 µs is $RC$ — the group delay at DC, which is where the "
                             "denominator is 1. 45.7 µs is the *phase* delay $-\\phi/(2\\pi f)$ at "
                             "1 kHz: a real quantity, correctly computed, and the answer to a "
                             "different question. 23.5 µs is the value at the corner frequency "
                             "rather than at 1 kHz.",
                    "why": r'''
```
RC            4700 * 10e-9                          =  47.000 us
2 pi f RC     2 pi * 1000 * 47.0e-6                 =   0.29531

tau_g         RC / (1 + 0.29531^2)
              47.000 / (1 + 0.087208)
              47.000 / 1.087208                     =  43.230 us
```

Three numbers from the same filter, none of them interchangeable.

**Group delay, 43.23 µs.** How long the *envelope* of a narrowband signal centred on
1 kHz is held. This is the one that matters when a waveform has to survive with its shape
intact.

**Phase delay, 45.70 µs.** The phase at 1 kHz is $-\arctan(0.29531) = -16.45^\circ$, and
$16.45/(360 \times 1000)$ is 45.70 µs. This is how far the *carrier* is rotated, expressed
as a time. For a pure delay line the two numbers are identical; here they are 2.5 µs apart,
and that gap is the definition of dispersion.

**Time constant, 47.00 µs.** The group delay at DC, and the number a step response would
hand you. It is the largest of the three, because a single pole's group delay only ever
falls with frequency.

Run the same expression at 5 kHz and it gives 14.78 µs. So a 1 kHz component leaves this
filter 43.23 µs after it arrived and a 5 kHz component 14.78 µs after — smeared apart by
28.45 µs, roughly a seventh of a cycle at 5 kHz. The magnitude response, which module 4
measured to two decimals, contains not one word about it.
''',
                },
                {
                    "title": "A recording sped up, then put on a carrier",
                    "minutes": 10,
                    "brief": r'''
Three properties in a row, and each one changes a different thing about the spectrum. None
of the steps is hard on its own; the work is keeping track of which quantity each stage
acts on, and noticing that one of the numbers you are given is not needed at all.

A rectangular pulse of width $\tau$ has spectrum $A\tau\,\mathrm{sinc}(f\tau)$, with its
first null at $f = 1/\tau$. That is the only transform pair required.
''',
                    "prompt": "What is the frequency of the first null of the modulated signal's spectrum above the carrier?",
                    "note": "In kilohertz, to the nearest kilohertz.",
                    "figure": r'''
```
   stage 1    a single rectangular pulse, recorded

                 2.00 V  +--------------+
                         |              |
                 0 V  ---+              +---------
                         0            200 us

   stage 2    the same recording played back at 4.00 x speed
              (nothing else is changed: same height, same shape)

   stage 3    the playback multiplies a carrier

                 v(t) ---->[   X   ]----> y(t)
                               ^
                               |
                    cos(2 pi * 1.500e6 * t)
```

The pulse is the whole signal. Nothing repeats, so the spectrum is a continuous curve with
nulls, not a set of lines.
''',
                    "given": [
                        {"label": "Pulse", "value": "2.00 V high, 200 µs wide"},
                        {"label": "Playback", "value": "4.00 × speed"},
                        {"label": "Carrier", "value": "1.500 MHz"},
                        {"label": "Wanted", "value": "first null of $|Y(f)|$ above 1.500 MHz"},
                    ],
                    "aside": "The pulse height is given and is not needed. Scaling changes the "
                             "height of the spectrum and modulation halves it, but neither moves a "
                             "null, and a null is what was asked for.",
                    "answer": 1520.0,
                    "tol": 1.0,
                    "unit": "kHz",
                    "hint": "In order: what does playing back at $a = 4$ do to the pulse *width*; "
                            "where does the first null of a pulse that width sit; and what does "
                            "multiplying by a cosine do to a feature at that frequency.",
                    "wrong": "1505 kHz is the answer with the speed-up left out — the original "
                             "200 µs pulse has its first null at 5.00 kHz. 20 kHz is the baseband "
                             "answer with the carrier left off. 1480 kHz is the first null *below* "
                             "the carrier: it is genuinely there, mirrored, and it is not what was "
                             "asked. 1.52 is the right number expressed in megahertz.",
                    "why": r'''
```
stage 2   scaling, a = 4       new width  =  200 us / 4        =   50.0 us

stage 3a  the null of a pulse  f_null     =  1 / 50.0e-6       =   20.0 kHz

stage 3b  modulation           X(f - fc) and X(f + fc), so every feature of the
                               baseband spectrum appears at fc +/- its own frequency

          first null above     1500 kHz + 20.0 kHz             = 1520 kHz
```

Checking it through the theorem rather than by feel is worth doing once. Scaling says
$x(4t) \leftrightarrow \tfrac14 X(f/4)$, so the new spectrum vanishes wherever
$X(f/4) = 0$, and the first of those is $f/4 = 5.00$ kHz, giving $f = 20.0$ kHz. The
same answer, and it arrives with the height attached: the peak has fallen from $A\tau =
400$ µV·s to 100 µV·s.

Then modulation puts a half-height copy at $1500 + 20 = 1520$ kHz and another at
$1500 - 20 = 1480$ kHz. Both nulls exist. The spectrum around the carrier is symmetric,
which is the geometry that makes double sideband double sideband.

The height is worth one more line, because it is the part the question deliberately does
not ask for. It has now been divided twice: by 4 for the speed-up and by 2 for the
modulation, so the peak of $|Y|$ is $400/8 = 50$ µV·s. Four times the bandwidth and an
eighth of the peak — and a null stayed a null through all of it, because a zero divided by
anything finite is still a zero. That is why nulls are what people measure: they are the
features that survive every gain in the chain.
''',
                },
            ],
            "derive": {
                "title": "One multiplier, two sidebands, and the half that comes back",
                "minutes": 14,
                "vars": ["A", "f_c", "f_m", "t", "B"],
                "brief": r'''
A single tone, $x(t) = A\cos(2\pi f_m t)$, multiplied by a carrier $\cos(2\pi f_c t)$ with
$f_c \gg f_m$. That is every mixer, every double-sideband transmitter and every
lock-in amplifier, and the whole of it comes out of one trigonometric identity used twice.

The identity is Euler's formula multiplied out:

$$\cos P \cos Q = \tfrac12\left[\cos(P - Q) + \cos(P + Q)\right]$$

Type a cosine as `cos(...)` when you enter an answer — without the backslash.
''',
                "steps": [
                    {
                        "prompt": "Apply the identity to $y(t) = A\\cos(2\\pi f_m t)\\cos(2\\pi f_c t)$ and write $y$ as a sum of two cosines of $t$.",
                        "given": "Take $P = 2\\pi f_c t$ and $Q = 2\\pi f_m t$, so that the difference term comes out at the lower frequency.",
                        "answer": "\\frac{A}{2}cos(2\\pi t(f_c - f_m)) + \\frac{A}{2}cos(2\\pi t(f_c + f_m))",
                        "placeholder": "\\ldots\\,cos(\\ldots) + \\ldots\\,cos(\\ldots)",
                        "hint": "The identity gives a factor of $\\tfrac12$, and the $A$ was already there. Both terms carry the same amplitude.",
                        "deconstruct": [
                            "$P - Q = 2\\pi f_c t - 2\\pi f_m t = 2\\pi t (f_c - f_m)$, and $P + Q = 2\\pi t (f_c + f_m)$.",
                            "Each cosine arrives with a factor $\\tfrac12$ from the identity, multiplied by the $A$ that was in front.",
                            "Nothing sits at $f_c$ itself: the carrier has been suppressed by the multiplication, not merely reduced.",
                        ],
                    },
                    {
                        "prompt": "Write the separation between the two frequencies present in $y$.",
                        "given": "The two lines sit either side of $f_c$, one below and one above.",
                        "answer": "2 f_m",
                        "hint": "$(f_c + f_m) - (f_c - f_m)$. The carrier cancels.",
                        "deconstruct": [
                            "Subtract the lower frequency from the higher one; the $f_c$ terms cancel.",
                            "What is left is $2f_m$ — the pair straddles the carrier symmetrically, at $\\pm f_m$ from it.",
                        ],
                    },
                    {
                        "prompt": "Now replace the single tone by a signal occupying every frequency from $0$ up to $B$. Write the total width of the band $y$ occupies.",
                        "given": "Every baseband component $f_m$ still produces its own pair at $f_c \\pm f_m$. Take the largest of them.",
                        "answer": "2 B",
                        "hint": "The extreme components are the ones at $f_m = B$; they land at $f_c - B$ and $f_c + B$, and everything else is between them.",
                        "deconstruct": [
                            "The lowest frequency present is $f_c - B$ and the highest is $f_c + B$.",
                            "The width is the difference, $2B$ — twice what the signal occupied before it was modulated.",
                        ],
                    },
                    {
                        "prompt": "Back to the single tone. Write the average power of $y$ — its mean square, in the one-ohm convention.",
                        "given": "Two sinusoids at different frequencies: the mean square of the sum is the sum of the mean squares, because the cross term averages to zero. A sinusoid of amplitude $V$ has mean square $V^2/2$.",
                        "answer": "\\frac{A^2}{4}",
                        "hint": "Each line has amplitude $A/2$, so each contributes $(A/2)^2/2$, and there are two of them.",
                        "deconstruct": [
                            "One line: $\\tfrac12 (A/2)^2 = A^2/8$.",
                            "Two lines at different frequencies: $A^2/8 + A^2/8 = A^2/4$.",
                            "The tone went in with mean square $A^2/2$, so modulation has cost exactly half the power — 3 dB, paid once.",
                        ],
                    },
                    {
                        "prompt": "Recover the signal: multiply $y$ by $\\cos(2\\pi f_c t)$ again and keep only the term that survives a low-pass filter. Write it.",
                        "given": "$\\cos^2\\theta = \\tfrac12(1 + \\cos 2\\theta)$, and everything the second cosine produces near $2f_c$ is removed by the filter.",
                        "answer": "\\frac{A}{2}cos(2\\pi f_m t)",
                        "placeholder": "\\ldots\\,cos(\\ldots)",
                        "hint": "$y\\cos(2\\pi f_c t) = A\\cos(2\\pi f_m t)\\cos^2(2\\pi f_c t)$. Substitute the identity and discard the half that carries $\\cos(2\\pi\\cdot 2f_c t)$.",
                        "deconstruct": [
                            "$y\\cos(2\\pi f_c t) = A\\cos(2\\pi f_m t)\\cdot\\tfrac12\\left[1 + \\cos(2\\pi \\cdot 2f_c t)\\right]$.",
                            "The first half is $\\tfrac{A}{2}\\cos(2\\pi f_m t)$, at baseband.",
                            "The second half sits around $2f_c$ and the low-pass removes it entirely.",
                        ],
                    },
                ],
                "closing": r'''
Five steps, and the whole of coherent modulation and demodulation is in them.

The signal comes back **halved**. It went in at amplitude $A$ and comes out at $A/2$, which
is why a demodulator is always followed by a gain of two — or, more honestly, why the
factor is folded into the gain of whatever comes next and nobody mentions it again.

The 3 dB of step 4 and the half of step 5 are the same fact counted twice, once in power
and once in amplitude. Multiplying by a cosine splits every component into two, and each
half is a half.

Two consequences the algebra hands over without being asked. If the local cosine is not in
phase — multiply by $\cos(2\pi f_c t + \theta)$ instead — the same expansion gives
$\tfrac{A}{2}\cos\theta\,\cos(2\pi f_m t)$, so the recovered signal falls off as
$\cos\theta$ and vanishes completely at $\theta = 90^\circ$. That quadrature null is the
reason coherent detection needs a phase-locked local oscillator, and it is also the reason
two independent signals can share one carrier, one on the cosine and one on the sine.

And step 3 is the number that gets paid for. Two hertz of spectrum for every hertz of
information, forever, unless one of the two sidebands is filtered away — at which point
the receiver has to reconstruct a carrier it was never sent, and the quadrature null above
says what happens if it gets the phase wrong.
''',
            },
        },

        # ---- M7 -----------------------------------------------------------
        {
            "title": "Selectivity: the band-pass, its bandwidth and $Q$",
            "summary": "EE102 met resonance, $Q$ and bandwidth in this circuit and quoted the results. Here they are put on module 4's $\\zeta$, proved rather than asserted, and pushed to the two consequences that only bite when the filter is narrow.",
            "concepts": [
                "Most of what follows is EE102 modules 7 and 8 re-derived rather than newly announced, and it is worth saying which parts those are. EE102 module 7 already established three probe placements on the series RLC: a low-pass across the capacitor, a high-pass across the inductor, a **band-pass** across the resistor with unity gain at $f_0$. The fourth placement — a **band-stop** across the inductor and capacitor together — is not new either: EE102 module 8's build \"A notch at 1 kHz\" is that same series loop with the probe on those same two nodes, described as a resistive divider with a series $L$–$C$ shunt rather than as a probe placement. What this module adds is not a circuit but what can be said about the family: all four written as one transfer function whose numerator alone changes, the proof of the bandwidth EE102 only quoted, the tie back to module 4's $\\zeta$, and two facts about narrow filters that EE102 never needed. Nothing in the circuit changes as the probe moves; only the numerator of $H$ does.",
                "Across the resistor: $H = \\dfrac{j\\omega RC}{1 - \\omega^2 LC + j\\omega RC}$, which in standard form is $\\dfrac{j2\\zeta(\\omega/\\omega_n)}{1 - (\\omega/\\omega_n)^2 + j2\\zeta(\\omega/\\omega_n)}$. At $\\omega = \\omega_n$ the two terms in the denominator that are not the $j2\\zeta$ one cancel exactly, so $H = 1$ — **unity gain at the centre, whatever the damping is**.",
                "Why that happens physically: at $\\omega_n$ the inductor's impedance $j\\omega L$ and the capacitor's $1/(j\\omega C)$ are equal in size and opposite in sign. In series they add to nothing, the circuit is momentarily just the resistor, and the whole source voltage appears across it.",
                "**Bandwidth** is the distance between the two frequencies where $|H|$ falls to $1/\\sqrt2$. EE102 module 7 gave the answer — $\\text{BW} = R/(2\\pi L)$, independent of the capacitor — from the bare assertion that the two half-power points are $R/L$ apart. Written with module 4's parameters that separation is $\\Delta\\omega = 2\\zeta\\omega_n$, and the derivation at the end of this module is where the assertion is finally discharged instead of taken on trust.",
                "**$Q$** is defined as $\\omega_n/\\Delta\\omega$, so $Q = \\dfrac{1}{2\\zeta} = \\dfrac{\\omega_n L}{R} = \\dfrac{1}{R}\\sqrt{\\dfrac{L}{C}}$. The two component forms and the relation $\\zeta = 1/(2Q)$ are EE102 module 7's; what is new is that this is the same $\\zeta$ you read off a Bode plot in module 4 and substituted into a transfer function. Low damping and high $Q$ are one condition, not two, and from here on the two names are interchangeable.",
                "The centre is the **geometric** mean of the two half-power frequencies, not the arithmetic one: $\\omega_1\\omega_2 = \\omega_n^2$, whereas their average is $\\omega_n\\sqrt{1+\\zeta^2}$. The arithmetic mean therefore sits high by a factor $\\sqrt{1 + 1/(4Q^2)}$, a fractional error of about $1/(8Q^2)$. For $Q = 50$ that factor is 1.00005 — the two means first differ in the fifth decimal place and nobody notices; for $Q = 1$ it is $\\sqrt{1.25} = 1.118$, nearly 12% high, and the arithmetic answer is simply wrong.",
                "Selectivity is slowness. The ringing after a disturbance decays by $1/e$ in $Q/\\pi$ cycles, so a 1 kHz filter with $Q = 100$ takes about 32 cycles — 32 ms — to settle. The rate it can follow is not the reciprocal of that settling time but the bandwidth this module has just derived: $\\Delta f = f_n/Q = 10$ Hz, and since a band-pass of that width passes an envelope only half as wide, modulation faster than about 5 Hz is smeared. (Equivalently: a 31.8 ms time constant is a low-pass corner of $1/(2\\pi \\times 0.0318) = 5$ Hz.) Narrow in frequency and slow in time are the same trade seen twice, and no choice of components escapes it.",
                "The **notch**, taken across the inductor and capacitor together, is $H = \\dfrac{1 - (\\omega/\\omega_n)^2}{1 - (\\omega/\\omega_n)^2 + j2\\zeta(\\omega/\\omega_n)}$. EE102 module 8 built this null already, and the same way up — a series $L$–$C$ branch shunting a divider is this series loop with the probe between the resistor and the pair, the same circuit under a different name. What is new here is only that it takes its place as the fourth member of one family, and that writing it as a transfer function shows why the null is exact — the numerator is zero at $\\omega_n$ for any $R$. Its width is set the same way, $\\Delta\\omega = 2\\zeta\\omega_n$, so a deep *and* narrow notch needs a small $R$, including whatever resistance the inductor brings with it.",
                "Which is the practical ceiling on $Q$, and it is EE102 module 8's rule about how deep a real notch goes seen from the other side. A real inductor has series resistance $R_s$ and its own $Q_L = \\omega L/R_s$, typically 50 to 200 at audio and RF; that resistance adds to yours, so no circuit built with it can be more selective than the inductor is — which is why the 40 dB notch quoted there needs component $Q$s in the hundreds. Quoting a design $Q$ higher than the components' own is the commonest way a filter fails to be the filter that was drawn.",
                "Reading $Q$ off a measurement needs no component values at all: find the peak, find the two frequencies either side where the response is 3 dB down, and divide. That is what EE102 module 7's lab did in code, and what the build below does on a circuit you have drawn. It is also how a $Q$ is quoted for a crystal, a cavity or a piece of ceramic, none of which have an $R$, an $L$ or a $C$ to point at.",
            ],
            "build": {
                "title": "A band-pass at 5 kHz with a $Q$ of 8",
                "minutes": 30,
                "brief": r'''
Same three components as module 4, same series chain, and the probe moved. The output
now comes off the **resistor** instead of the capacitor, and the low-pass becomes a
band-pass with unity gain at its centre.

Build one on the empty canvas — source, inductor, capacitor, resistor, ground, probe —
and meet all four of these:

1. **Nothing at DC.** At 10 Hz the output must be under 2% of the source. The capacitor
   in series sees to that.
2. **Nothing far above.** At 500 kHz the output must be under 2% of the source. The
   inductor in series sees to that.
3. **Centred at 5 kHz, and lossless there.** The peak of the response must sit within 5%
   of 5 kHz, and at the peak the output must be at least 95% of the input.
4. **$Q = 8$, within about a tenth.** Measured the way anyone measures it: the peak
   frequency divided by the distance between the two points where the response is
   $1/\sqrt2$ of the peak.

## Working the values out

Requirement 3 fixes $\omega_n = 2\pi \times 5000$, which fixes the product $LC$.
Requirement 4 fixes $Q = \omega_n L/R$, which then fixes $R$ once you have chosen $L$.
Two equations, three unknowns — so one component is yours to pick, and picking the
capacitor at a round value is the usual move.

Note what requirement 3's second half is telling you: a band-pass across the resistor
has a gain of exactly 1 at its centre *whatever* $R$ is. If your peak is not reaching
the input voltage, the probe is not on the resistor.

## Drawing it

The inductor and capacitor go in series from the source, in either order; the resistor
goes from that chain's far end down to ground; the probe sits on the node between them.
Values accept `101m`, `10n` and `398` alike.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "OUT", "x": 15, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [15, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "L", "x": 6, "y": 4, "rot": 0, "value": 0.10132118},
                        {"id": "p3", "kind": "C", "x": 10, "y": 4, "rot": 0, "value": 1e-8},
                        {"id": "p4", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 397.8874},
                        {"id": "p5", "kind": "GND", "x": 13, "y": 9},
                        {"id": "p6", "kind": "OUT", "x": 15, "y": 4},
                    ],
                    "wires": [
                        {"a": [3, 5], "b": [3, 4]},
                        {"a": [3, 4], "b": [5, 4]},
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [7, 4], "b": [9, 4]},
                        {"a": [11, 4], "b": [13, 4]},
                        {"a": [13, 4], "b": [13, 5]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 4], "b": [15, 4]},
                    ],
                },
                "checks": [
                    {"name": "one source, and DC does not reach the probe", "code": r'''
c.assert(c.count('V') === 1, 'Drive the filter from exactly one source; found ' + c.count('V') + '.');
const vs = c.values('V')[0];
const dc = c.gain(10) / vs;
c.assert(dc < 0.02,
  'At 10 Hz the probe sees ' + (dc * 100).toFixed(1) + '% of the source. A band-pass ' +
  'must reject DC, and the series capacitor is what does it — if the output is still ' +
  'following the source down here, the probe is on the wrong node or the capacitor is ' +
  'not in the series path.');
'''},
                    {"name": "and neither does anything far above the band", "code": r'''
const vs = c.values('V')[0];
const hi = c.gain(500000) / vs;
c.assert(hi < 0.02,
  'At 500 kHz the probe still sees ' + (hi * 100).toFixed(1) + '% of the source. Up ' +
  'here the inductor is the large impedance and should be dropping almost all of it; a ' +
  'response that stays flat means there is no inductor in the series path.');
'''},
                    {"name": "the peak sits at 5 kHz and loses nothing there", "code": r'''
const vs = c.values('V')[0];
let best = 0, fpk = 0;
for (let i = 0; i <= 200; i++) {
  const f = 1000 * Math.pow(25, i / 200);
  const g = c.gain(f);
  if (g > best) { best = g; fpk = f; }
}
c.close(fpk, 5000, 0.05, 'the frequency at which the response peaks');
c.assert(best > 0.95 * vs,
  'At its own peak the filter passes only ' + (best / vs * 100).toFixed(1) + '% of the ' +
  'input. Across the resistor the gain at the centre is exactly 1 for any R, because ' +
  'the inductor and capacitor cancel there — so this says the output is being taken ' +
  'across the wrong element.');
'''},
                    {"name": "the -3 dB points put Q at 8", "code": r'''
let best = 0, fpk = 0;
for (let i = 0; i <= 200; i++) {
  const f = 1000 * Math.pow(25, i / 200);
  const g = c.gain(f);
  if (g > best) { best = g; fpk = f; }
}
const half = best / Math.SQRT2;
let lo = 100, hi = fpk;
for (let i = 0; i < 60; i++) { const m = Math.sqrt(lo * hi); if (c.gain(m) < half) lo = m; else hi = m; }
const f1 = Math.sqrt(lo * hi);
lo = fpk; hi = 2e6;
for (let i = 0; i < 60; i++) { const m = Math.sqrt(lo * hi); if (c.gain(m) > half) lo = m; else hi = m; }
const f2 = Math.sqrt(lo * hi);
const Q = fpk / (f2 - f1);
c.close(Q, 8, 0.12,
  'the measured Q: the peak at ' + c.fmt(fpk, 'Hz') + ' divided by the ' +
  c.fmt(f2 - f1, 'Hz') + ' between the two half-power points. Q rises as R falls, ' +
  'because Q = omega_n L / R');
'''},
                ],
                "hints": [
                    "$\\omega_n = 2\\pi \\times 5000 = 31416$ rad/s, so $LC = 1/\\omega_n^2 = 1.013 \\times 10^{-9}$.",
                    "Choose $C = 10$ nF. Then $L = 1/(\\omega_n^2 C) \\approx 101$ mH.",
                    "$Q = \\omega_n L/R$, so $R = \\omega_n L/Q = 31416 \\times 0.1013 / 8 \\approx 398$ Ω.",
                    "If the peak is in the right place but the response is too broad, $R$ is too large — $Q$ and $R$ move in opposite directions. If the peak is in the wrong place, it is $L$ or $C$ that is wrong, and $R$ will not fix it.",
                    "The probe belongs on the node between the capacitor and the resistor, which is the top of the resistor. Put it anywhere else and you have built a different one of the four filters.",
                ],
            },
            "quiz": {
                "title": "Where the probe goes, and what $Q$ measures",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A resistor, an inductor and a capacitor are in series across a source. Where is the output taken to get a band-pass?",
                        "opts": [
                            "across the inductor",
                            "across the capacitor",
                            "across the resistor",
                            "across the inductor and the capacitor together",
                        ],
                        "a": 2,
                        "why": r'''
Across the resistor. At low frequency the capacitor's impedance is huge and takes almost
all the source voltage; at high frequency the inductor does; only near $\omega_n$, where
those two cancel each other, is the resistor left holding the whole of it. The other
three placements give the other three filters — capacitor a low-pass, inductor a
high-pass, the two of them together a notch — which is the tidiest demonstration in the
course that a transfer function is a property of a *measurement*, not of a circuit.
''',
                    },
                    {
                        "q": "A band-pass is centred at 10 MHz and its $-3$ dB bandwidth is 200 kHz. What is its $Q$?",
                        "opts": ["50", "0.02", "5", "2000"],
                        "a": 0,
                        "why": r'''
$Q = f_n/\Delta f = 10{,}000{,}000/200{,}000 = 50$. That is the whole definition, and it
needs no component values — which is why $Q$ is the number quoted for a crystal or a
cavity resonator, where there is no resistor to point at. A $Q$ of 50 also fixes the
damping, $\zeta = 1/(2Q) = 0.01$, and tells you the thing will ring for about
$Q/\pi \approx 16$ cycles after it is disturbed.
''',
                    },
                    {
                        "q": "The resistance in a series-RLC band-pass is doubled. What happens?",
                        "opts": [
                            "the centre frequency halves and the bandwidth is unchanged",
                            "the bandwidth doubles and the centre frequency stays put",
                            "the bandwidth halves and the centre frequency stays put",
                            "the peak gain halves; nothing else moves",
                        ],
                        "a": 1,
                        "why": r'''
$\omega_n = 1/\sqrt{LC}$ contains no $R$, so the centre cannot move. $\Delta\omega = R/L$
is proportional to $R$, so the bandwidth doubles and $Q$ halves. The peak gain does not
change either — it is exactly 1 for any $R$, because at the centre the inductor and
capacitor cancel and the resistor is alone with the source. That independence is what
makes the design easy: pick $L$ and $C$ for where, pick $R$ for how wide.
''',
                    },
                    {
                        "q": "A band-pass has its half-power points at 900 Hz and 1111.1 Hz. Where is its centre?",
                        "opts": [
                            "1005.6 Hz — halfway between them",
                            "1000 Hz — their geometric mean",
                            "211.1 Hz — their difference",
                            "not determined by those two numbers alone",
                        ],
                        "a": 1,
                        "why": r'''
$\omega_1\omega_2 = \omega_n^2$, so the centre is $\sqrt{900 \times 1111.1} = 1000$ Hz.
The arithmetic mean gives 1005.6, which is 0.6% out — invisible on a plot and quite
wrong if you are trying to hit a channel. The two means converge as $Q$ rises, which is
why the error goes unnoticed in narrowband work and bites immediately in broadband work:
this filter's $Q$ is $1000/211.1 = 4.7$, which is low, and the discrepancy is about
$1/(8Q^2)$ — 0.57% here, and nearly 12% by the time $Q$ has fallen to 1.
''',
                    },
                    {
                        "q": "A 1 kHz band-pass with $Q = 100$ is hit with a short burst. Roughly how long until its ringing has decayed by $1/e$?",
                        "opts": [
                            "about 1 ms — one cycle at the centre frequency",
                            "about 100 ms",
                            "about 32 ms",
                            "immediately, since a passive filter stores no energy",
                        ],
                        "a": 2,
                        "why": r'''
The envelope decays as $e^{-\zeta\omega_n t}$, so the $1/e$ point is at
$t = 1/(\zeta\omega_n)$, which is $Q/\pi$ cycles — about 32 cycles here, and at 1 kHz
that is 32 ms. This is the real cost of selectivity and it is not negotiable: a filter
narrow enough to isolate one 1 kHz tone from another 10 Hz away is also a filter that
takes tens of milliseconds to notice anything has happened. Every receiver design is
somewhere on this trade.
''',
                    },
                    {
                        "q": "Why can the notch taken across the inductor and capacitor together be perfectly deep?",
                        "opts": [
                            "because the resistor is chosen to cancel the reactance at that frequency",
                            "because the two reactances are equal and opposite at $\\omega_n$, so their series pair is a short circuit",
                            "because the inductor stores exactly as much energy as the capacitor dissipates",
                            "it cannot be — a passive notch is limited to about 40 dB",
                        ],
                        "a": 1,
                        "why": r'''
At $\omega_n$, $j\omega L$ and $1/(j\omega C)$ are equal in magnitude and opposite in
sign, so in series they sum to zero: the pair is, at that one frequency, a piece of wire.
The voltage across a piece of wire is zero, and no value of $R$ appears in that argument
— which is why the null is infinitely deep in principle. In practice it is limited by
the inductor's own series resistance, which does not cancel with anything, and 40 dB is
a fair figure for a real one; but that is a component limitation rather than a limit of
the topology.
''',
                    },
                ],
            },
            "derive": {
                "title": "Where the bandwidth comes from, and why $Q = 1/2\\zeta$",
                "minutes": 14,
                "vars": ["omega", "omega_n", "zeta", "x", "Q", "R", "L", "C", "B"],
                "brief": r'''
The band-pass magnitude, in normalised form with $x = \omega/\omega_n$:

$$|H| = \frac{2\zeta x}{\sqrt{(1-x^2)^2 + (2\zeta x)^2}}$$

It peaks at $x = 1$, where it equals 1. Find the two places where it has fallen to
$1/\sqrt2$ of that, subtract them, and the definition of $Q$ falls out with no
approximation anywhere.

This is the step EE102 module 7's derivation skipped. There the half-power points were
*stated* to be $R/L$ apart and the bandwidth followed in one line; here the two
frequencies are actually solved for, and $Q = 1/2\zeta$ — usually presented as something
to be memorised — arrives as arithmetic instead.
''',
                "steps": [
                    {
                        "prompt": "Set $|H| = 1/\\sqrt2$ and square both sides. After clearing the fraction you are left with a statement about $|1-x^{2}|$. Write what it must equal.",
                        "given": "$\\dfrac{(2\\zeta x)^2}{(1-x^2)^2+(2\\zeta x)^2} = \\dfrac12$",
                        "answer": "2 \\zeta x",
                        "hint": "Cross-multiplying gives $2(2\\zeta x)^2 = (1-x^2)^2 + (2\\zeta x)^2$, so one copy of $(2\\zeta x)^2$ survives on the left.",
                        "deconstruct": [
                            "Multiply both sides by the denominator and by 2.",
                            "Subtract $(2\\zeta x)^2$ from both sides: $(2\\zeta x)^2 = (1-x^2)^2$.",
                            "Take the positive square root of each side; $x$ and $\\zeta$ are both positive.",
                        ],
                    },
                    {
                        "prompt": "Above the centre, $1-x^{2}$ is negative, so the condition reads $x^{2} - 2\\zeta x - 1 = 0$. Write its positive root.",
                        "answer": "\\zeta + \\sqrt{1+\\zeta^{2}}",
                        "hint": "The quadratic formula with $a = 1$, $b = -2\\zeta$, $c = -1$. The discriminant is $4\\zeta^2 + 4$.",
                        "deconstruct": [
                            "$x = \\dfrac{2\\zeta \\pm \\sqrt{4\\zeta^2+4}}{2}$.",
                            "The square root simplifies to $2\\sqrt{\\zeta^2+1}$, and the 2s cancel.",
                            "Keep the root that is positive; the other one is negative because $\\sqrt{1+\\zeta^2} > \\zeta$.",
                        ],
                    },
                    {
                        "prompt": "Below the centre the condition reads $x^{2} + 2\\zeta x - 1 = 0$. Write its positive root.",
                        "answer": "-\\zeta + \\sqrt{1+\\zeta^{2}}",
                        "hint": "Only the sign of the $2\\zeta$ term has changed, so only the sign of the term outside the radical changes.",
                        "deconstruct": [
                            "$x = \\dfrac{-2\\zeta \\pm \\sqrt{4\\zeta^2+4}}{2}$.",
                            "Simplify as before and keep the positive root.",
                        ],
                    },
                    {
                        "prompt": "Subtract the lower root from the upper one and write the normalised bandwidth.",
                        "given": "Both roots share the same radical, which is the point of writing them this way.",
                        "answer": "2 \\zeta",
                        "hint": "The radicals cancel exactly, leaving twice the term outside them.",
                        "deconstruct": [
                            "$(\\zeta + \\sqrt{1+\\zeta^2}) - (-\\zeta + \\sqrt{1+\\zeta^2})$.",
                            "The square roots are identical and subtract to zero.",
                        ],
                    },
                    {
                        "prompt": "$Q$ is defined as the centre divided by the bandwidth, and in these normalised units the centre is at $x = 1$. Write $Q$ in terms of $\\zeta$.",
                        "answer": "\\frac{1}{2\\zeta}",
                        "hint": "Divide 1 by the answer you just wrote.",
                        "deconstruct": [
                            "$Q = \\dfrac{x_{centre}}{x_2 - x_1}$ and $x_{centre} = 1$.",
                            "So $Q$ is the reciprocal of $2\\zeta$.",
                        ],
                    },
                    {
                        "prompt": "Module 4 found $\\zeta = \\frac{R}{2}\\sqrt{C/L}$ for this circuit. Substitute it and write $Q$ in terms of $R$, $L$ and $C$.",
                        "answer": "\\frac{1}{R}\\sqrt{\\frac{L}{C}}",
                        "hint": "$2\\zeta = R\\sqrt{C/L}$, and the reciprocal of a square root is the square root of the reciprocal.",
                        "deconstruct": [
                            "$Q = \\dfrac{1}{R\\sqrt{C/L}}$.",
                            "$\\dfrac{1}{\\sqrt{C/L}} = \\sqrt{L/C}$.",
                        ],
                    },
                ],
                "closing": r'''
Three readings of one number. $Q = 1/2\zeta$ ties it to the damping of module 4;
$Q = \frac1R\sqrt{L/C}$ ties it to the components; and $Q = \omega_n/\Delta\omega$ —
which is where it started — ties it to two frequencies you can read off a measured
curve without knowing any of the others.

That last form is the one that survives outside this circuit. A crystal, a cavity, a
tuning fork and a length of transmission line all have a $Q$, and none of them has an
$R$, an $L$ or a $C$ to substitute.
''',
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "A system written as a recursion: difference equations, FIR and IIR",
            "summary": "Nobody hands you an impulse response. They hand you a rule relating this output sample to the last few, and everything else has to be worked out from it.",
            "concepts": [
                "Module 1 started from $h$ and convolved. Real discrete-time systems arrive the other way round, as a **difference equation**: $y[n] = \\sum_{k\\ge0} b_k\\,x[n-k] + \\sum_{k\\ge1} a_k\\,y[n-k]$. It is the discrete counterpart of the differential equations EE111 solved, and the only description a piece of code actually contains.",
                "**FIR** — finite impulse response — means every $a_k$ is zero: the output depends on a finite window of the input and on nothing it has produced itself. Its impulse response is the coefficient list, read straight off: the four-point moving average $y[n]=\\frac14\\sum_{k=0}^{3}x[n-k]$ has $h = \\{0.25, 0.25, 0.25, 0.25\\}$ and stops.",
                "**IIR** — infinite impulse response — means at least one $a_k$ is not zero. Output feeds back into output, so $h$ never ends. $y[n] = a\\,y[n-1] + x[n]$ has $h[n] = a^n$ for $n \\ge 0$: infinitely many non-zero samples out of two coefficients, which is the whole economic argument for feedback.",
                "The recursion is only an LTI system under **initial rest** — every stored value zero before the input arrives. With a non-zero starting state the output has a component that does not scale when the input is scaled, and linearity fails exactly as it did for the $2x + 3$ amplifier in module 1.",
                "Finding $h$ numerically: set $x = \\{1, 0, 0, \\dots\\}$ and run the recursion. Finding it in closed form: set $x = 0$, try $y[n] = \\lambda^n$, and divide through. For $y[n] = a\\,y[n-1]$ that gives $\\lambda = a$ immediately, and $h[n] = a^n$ follows.",
                "Second order, the interesting case: $y[n] = 2r\\cos\\theta\\,y[n-1] - r^2 y[n-2] + x[n]$ has characteristic equation $\\lambda^2 - 2r\\cos\\theta\\,\\lambda + r^2 = 0$ and roots $\\lambda = re^{\\pm j\\theta}$ — a conjugate pair at radius $r$ and angle $\\theta$. Its impulse response is $h[n] = r^n\\,\\frac{\\sin((n+1)\\theta)}{\\sin\\theta}$: an oscillation at $\\theta$ radians per sample inside an envelope that shrinks by a factor $r$ every sample.",
                "**Stability is a radius.** $h$ is a sum of terms $\\lambda^n$, so $\\sum_n|h[n]|$ converges exactly when every root satisfies $|\\lambda| < 1$. On the circle the response never settles; outside it, every sample is larger than the last. Compare module 1, where the same question was answered by looking at $h$ directly — this answers it from the coefficients, before $h$ has been computed at all.",
                "The angle sets the frequency and the radius sets the duration, and they do not interact. $\\theta$ is in **radians per sample**, so the fastest oscillation any sequence can carry is $\\theta = \\pi$ — one sign change per sample, half a cycle. That is module 3's Nyquist limit arriving from the algebra rather than from a sampler.",
                "**DC gain** is what a constant input settles to. Put $x[n]=1$ into $y[n]=a\\,y[n-1]+x[n]$ and let $y[n]=y[n-1]=G$: then $G = 1/(1-a)$. It must equal $\\sum_n h[n] = \\sum_n a^n$, and it does — the gain at zero frequency is the sum of the impulse response, which is module 1's statement about $\\sum|h|$ with the absolute value removed.",
                "The trade. An FIR of length $N$ costs $N$ multiplies per output sample, stores nothing, and cannot possibly be unstable. An IIR reaches the same sharpness with a handful of coefficients but carries state, and a coefficient rounded the wrong way can move a root from inside the circle to outside it — a failure mode that has no FIR equivalent and that fixed-point arithmetic makes real.",
                "Every simulation of an analogue circuit is one of these. Discretise $\\tau\\dot y + y = x$ at step $T$ and you get $y[n] = \\frac{\\tau}{\\tau+T}y[n-1] + \\frac{T}{\\tau+T}x[n]$: an IIR filter with a root at $\\tau/(\\tau+T)$, always inside the unit circle, and a DC gain of exactly 1.",
            ],
            "sandbox": {
                "title": "A root's radius and angle, and the response they produce",
                "visualiser": "z-plane",
                "minutes": 10,
                "initial": {"r": 0.9, "th": 0.4},
                "brief": r'''
The **left** panel is the complex plane with the unit circle drawn on it, and the two
dots are the characteristic roots of a second-order recursion — a conjugate pair at
radius $r$ and angle $\pm\theta$. The **right** panel is the impulse response those
roots produce, sample by sample.

The picture plots $h[n] = r^n\cos(\theta n)$, which is the cosine member of the family;
the recursion in the concepts produces the sine member,
$r^n\sin((n+1)\theta)/\sin\theta$. The difference between them is not confined to the
first few samples: $\sin((n+1)\theta)/\sin\theta = \cos(n\theta) + \cot\theta\,\sin(n\theta)$,
which is the same oscillation scaled by $1/\sin\theta$ — a factor of 2.57 at the opening
$\theta = 0.4$ — and shifted in phase by $\pi/2 - \theta$, at every $n$. That shift is
1.17 radians at the opening angle, and since one sample advances the phase by $\theta$ it puts
the sine member's first peak about 2.9 samples after the cosine member's, not one. The auto-scaled vertical
axis hides the scaling, and the envelope and the oscillation rate, which are what this
sandbox is about, are genuinely identical.

Two sliders: the radius and the angle. Watch which one changes the frequency and which
one changes how long the thing lasts.
''',
                "notice": [
                    "It opens at $r = 0.90$, $\\theta = 0.40$. Both dots sit nine tenths of the way out to the circle, one above the real axis and one below. On the right, each sample's envelope is 90% of the last, and one full oscillation takes $2\\pi/0.4 \\approx 16$ samples. The caption reports 44 samples to fall to 1% — that is $\\log(0.01)/\\log(0.9)$, and it is a number you can compute before looking.",
                    "Drag the radius down to 0.50 and leave the angle alone. The oscillation is at exactly the same rate — count the samples between zero crossings and nothing has changed — but it is gone in 7 samples instead of 44. The angle sets the frequency, the radius sets the duration, and neither touches the other.",
                    "Put the radius back to 0.90 and take the angle to 0. The two dots merge on the positive real axis, the oscillation disappears entirely, and what is left is $0.9^n$: the plain geometric decay of the first-order recursion $y[n] = 0.9\\,y[n-1] + x[n]$. Every sample has the same sign.",
                    "Now take the angle to 3.14, as near $\\pi$ as the slider reaches. The dots land on the negative real axis and the response alternates sign on every single sample — half a cycle per sample, which is the fastest a sequence can oscillate. There is nothing beyond it: a faster oscillation, sampled, is some slower one in disguise, which is module 3's Nyquist limit stated without mentioning a converter.",
                    "Finally push the radius to 1.00. The colour changes, the envelope stops shrinking, and the caption says marginally stable — it rings forever and settles at nothing. One notch further, at 1.05, every sample is larger than the last. Nothing gradual happens at the boundary: 0.99 decays, 1.01 diverges, and the whole of stability for these systems is which side of that line the dots are on.",
                ],
            },
            "quiz": {
                "title": "Reading a recursion",
                "minutes": 10,
                "questions": [
                    {
                        "q": "$y[n] = 0.5\\,y[n-1] + x[n]$ is driven by an impulse, from rest. What is $h[3]$?",
                        "opts": ["0.5", "0.125", "1.5", "0"],
                        "a": 1,
                        "why": r'''
Run it: $h[0] = 1$, then each sample is half the last, so $h[3] = 0.5^3 = 0.125$. The
general term is $a^n$, and it never reaches zero — that is what "infinite impulse
response" means, and it is produced here by exactly two coefficients. Answering 0
assumes the response ends when the input does, which is true of an FIR and false of
anything with feedback.
''',
                    },
                    {
                        "q": "Which of these systems is guaranteed stable no matter what its coefficients are?",
                        "opts": [
                            "$y[n] = b_0x[n] + b_1x[n-1] + b_2x[n-2]$",
                            "$y[n] = x[n] + a_1y[n-1]$",
                            "$y[n] = x[n] + a_1y[n-1] + a_2y[n-2]$",
                            "none of them — stability always depends on the numbers",
                        ],
                        "a": 0,
                        "why": r'''
The one with no feedback. An FIR's impulse response is its coefficient list, which is
finite, so $\sum|h[n]|$ is a finite sum of finite numbers whatever those numbers are.
Both recursive forms can be made to diverge — $a_1 = 1.1$ does it for the first-order
one — because their responses go on forever and a sum of infinitely many terms needs
them to shrink. This guarantee is the single strongest argument for FIR filters, and it
is why they are used where a divergence would be dangerous rather than merely wrong.
''',
                    },
                    {
                        "q": "A second-order recursion has characteristic roots at $0.95e^{\\pm j0.3}$. What does its impulse response look like?",
                        "opts": [
                            "a decaying oscillation, about 21 samples per cycle, taking roughly 90 samples to fall to 1%",
                            "a growing oscillation, since both roots are close to 1",
                            "a monotonic decay with no oscillation at all",
                            "an oscillation of constant amplitude",
                        ],
                        "a": 0,
                        "why": r'''
The angle gives the rate — $2\pi/0.3 \approx 21$ samples per cycle — and the radius
gives the envelope, $0.95^n$, which reaches 1% after $\log(0.01)/\log(0.95) \approx 90$
samples. Both roots are inside the unit circle, so it decays; a complex pair means it
oscillates on the way. A monotonic decay would need real roots, which is $\theta = 0$,
and a constant amplitude would need $|\lambda|$ exactly 1.
''',
                    },
                    {
                        "q": "What is the DC gain of $y[n] = 0.8\\,y[n-1] + x[n]$?",
                        "opts": ["0.8", "1.25", "1", "5"],
                        "a": 3,
                        "why": r'''
Feed in a constant 1 and let it settle: $G = 0.8G + 1$, so $G = 1/(1 - 0.8) = 5$. The
same number is $\sum_n 0.8^n$, the sum of the impulse response, which is what the gain
at zero frequency has to be — every sample of the input is contributing its own copy of
$h$ and they all overlap. The value 1.25 is $1/0.8$, which is the answer to a different
and less useful question, and it is the slip to watch for: the denominator is $1-a$,
not $a$.
''',
                    },
                    {
                        "q": "A first-order low-pass with $\\tau = 1$ ms is simulated at a step of $T = 0.1$ ms as $y[n] = \\frac{\\tau}{\\tau+T}y[n-1] + \\frac{T}{\\tau+T}x[n]$. Where is its root, and what is its DC gain?",
                        "opts": [
                            "root at 0.909, DC gain 1",
                            "root at 0.1, DC gain 10",
                            "root at 1.1, DC gain 1",
                            "root at 0.909, DC gain 11",
                        ],
                        "a": 0,
                        "why": r'''
$\tau/(\tau+T) = 1/1.1 = 0.909$, comfortably inside the unit circle, so the simulation
is stable — as it must be, since the circuit it models is. The DC gain is
$\frac{T/(\tau+T)}{1 - \tau/(\tau+T)} = \frac{0.1/1.1}{0.1/1.1} = 1$, again as it must
be, because at DC a capacitor is an open circuit and the whole input appears at the
output. Shrinking the step pushes the root towards 1 and the simulation towards the
continuous system; it never pushes it past 1, which is why this particular discretisation
cannot be made unstable by choosing a bad step.
''',
                    },
                    {
                        "q": "Why does a recursion only describe an LTI system if it starts from rest?",
                        "opts": [
                            "because a non-zero starting state makes the system time-varying",
                            "because the stored values would otherwise be counted twice in the convolution sum",
                            "because a non-zero starting state adds an output component that does not scale with the input, so superposition fails",
                            "it does not — initial conditions are a detail that averages out",
                        ],
                        "a": 2,
                        "why": r'''
Double the input and the part of the output that came from the input doubles, while the
part that came from the stored state does not — so the total is not double, and
linearity is broken. It is the same failure as the amplifier with a 3 V offset in
module 1, arriving from a different direction. The system is still perfectly time
invariant, and the fix is the same one instrumentation always uses: work with the
difference from the resting state, which is genuinely linear.
''',
                    },
                ],
            },
            "derive": {
                "title": "From a recursion to its impulse response, and to its gain",
                "minutes": 12,
                "vars": ["a", "n", "h", "y", "x", "G"],
                "brief": r'''
The system is $y[n] = a\,y[n-1] + x[n]$, at rest before $n = 0$. Two coefficients, and
from them the impulse response, the stability condition and the DC gain — all by
substitution, with no transform of any kind.

The last two steps arrive at the same expression from opposite ends. That is not an
accident and it is worth noticing when it happens.
''',
                "steps": [
                    {
                        "prompt": "Drive it with the unit impulse. At $n = 0$ the stored $y[-1]$ is zero and the input is 1, so $h[0] = 1$. Write $h[1]$.",
                        "given": "At $n = 1$ the input is already back to zero, so the only contribution is $a$ times what is stored.",
                        "answer": "a",
                        "hint": "$h[1] = a\\,h[0] + x[1]$, and $x[1] = 0$.",
                        "deconstruct": [
                            "Substitute $n = 1$ into the recursion.",
                            "$h[0]$ is 1 and $x[1]$ is 0, so only the feedback term survives.",
                        ],
                    },
                    {
                        "prompt": "Now write $h[2]$.",
                        "answer": "a^{2}",
                        "hint": "Same step again: multiply what is stored by $a$, and the input is still zero.",
                        "deconstruct": [
                            "$h[2] = a\\,h[1]$.",
                            "And $h[1]$ was $a$.",
                        ],
                    },
                    {
                        "prompt": "Write the general term $h[n]$ for $n \\ge 0$.",
                        "answer": "a^{n}",
                        "hint": "Every step multiplies by one more factor of $a$, starting from $h[0] = 1$.",
                        "deconstruct": [
                            "The sequence is $1, a, a^2, a^3, \\dots$",
                            "Which is a geometric sequence with ratio $a$ and first term 1.",
                        ],
                    },
                    {
                        "prompt": "Module 1 defined the worst-case gain as $\\sum_{n\\ge0}|h[n]|$. Take $0 < a < 1$ and write that sum in closed form.",
                        "answer": "\\frac{1}{1-a}",
                        "hint": "A geometric series with first term 1 and ratio $a$ sums to $1/(1-a)$ when $|a| < 1$, and diverges otherwise.",
                        "deconstruct": [
                            "$S = 1 + a + a^2 + \\dots$",
                            "So $aS = a + a^2 + \\dots = S - 1$.",
                            "Rearranging, $S(1 - a) = 1$.",
                        ],
                    },
                    {
                        "prompt": "Now get a number for the same system a completely different way. Put a constant $x[n] = 1$ in, let it settle so that $y[n] = y[n-1] = G$, and solve the recursion for $G$.",
                        "given": "$G = a\\,G + 1$",
                        "answer": "\\frac{1}{1-a}",
                        "hint": "Collect the $G$ terms on one side; no series is needed and no impulse response is used.",
                        "deconstruct": [
                            "$G - aG = 1$.",
                            "$G(1 - a) = 1$.",
                        ],
                    },
                ],
                "closing": r'''
The two routes agree, and they had to. A constant input is a sum of one shifted impulse
per sample, all of them of height 1, so the settled output is every sample of $h$ added
together — which is the series of the previous step with the absolute value dropped.
For a positive $a$ they are the same sum; for a negative $a$ the DC gain is smaller than
the worst-case gain, because the alternating terms partly cancel at DC and do not
cancel at all for the input that maximises the output.

And the stability condition falls out of the same series: it converges only for
$|a| < 1$. That is the unit circle in the sandbox, with the angle set to zero.
''',
            },
            "lab": {
                "title": "Two ways to build a filter, and the one that can blow up",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Four functions. Two of them run a filter, two of them predict what it will do before
it is run.

- `fir(b, x)` — output of $y[n] = \sum_k b_k\,x[n-k]$, from rest. Treat $x[n]$ as zero
  for $n < 0$, and return a list the **same length as `x`** (not the convolution length
  of module 1 — a real filter produces one output sample per input sample and the tail
  is simply not computed).
- `iir2(b0, a1, a2, x)` — output of $y[n] = b_0x[n] + a_1y[n-1] + a_2y[n-2]$, from rest.
  Two stored numbers, updated in the right order each pass.
- `roots_magnitude(a1, a2)` — the magnitude of the larger characteristic root of
  $\lambda^2 - a_1\lambda - a_2 = 0$. When the discriminant $a_1^2 + 4a_2$ is negative
  the roots are a conjugate pair and the magnitude is $\sqrt{-a_2}$; otherwise take the
  larger of the two real roots in absolute value. Returns a float — under 1 means
  stable.
- `dc_gain(b0, a1, a2)` — the settled output for a constant input of 1, which is
  $b_0/(1 - a_1 - a_2)$.

Plain lists and the `math` module; NumPy is not needed. The last test checks the thing
the whole module is about: that the gain you predicted from three coefficients is the
number the recursion actually settles at.
''',
                "files": [{"name": "main.py", "content": r'''
"""A filter written as coefficients, run, and predicted."""

import math


def fir(b, x):
    """y[n] = sum_k b[k] * x[n-k], from rest. Same length as x."""
    # TODO: for each n, sum b[k] * x[n-k] over the k that stay in range.
    return []


def iir2(b0, a1, a2, x):
    """y[n] = b0*x[n] + a1*y[n-1] + a2*y[n-2], from rest. Same length as x."""
    # TODO: keep two stored numbers, and update them in the right order:
    #       the older one takes the value of the newer BEFORE the newer is replaced.
    return []


def roots_magnitude(a1, a2):
    """Magnitude of the larger root of lambda**2 - a1*lambda - a2 = 0."""
    # TODO: discriminant a1*a1 + 4*a2. Negative -> conjugate pair, magnitude
    #       sqrt(-a2). Otherwise two real roots; return the larger |root|.
    return 0.0


def dc_gain(b0, a1, a2):
    """Settled output for a constant input of 1."""
    # TODO: one line.
    return 0.0


if __name__ == "__main__":
    print("moving average, impulse in:", fir([0.25] * 4, [1.0] + [0.0] * 5))
    r, th = 0.9, 0.4
    a1, a2 = 2 * r * math.cos(th), -r * r
    print("resonator coefficients:", a1, a2)
    print("its root magnitude:", roots_magnitude(a1, a2))
    print("its DC gain:", dc_gain(1.0, a1, a2))
    print("first six samples:", iir2(1.0, a1, a2, [1.0] + [0.0] * 5))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""A filter written as coefficients, run, and predicted.

Numbers below came out of running this file. With r = 0.9 and theta = 0.4 the
coefficients are a1 = 1.6579097892051933 and a2 = -0.81; the root magnitude comes
back as exactly 0.9, the DC gain as 6.5750451312685385, and summing 401 samples of
the impulse response gives 6.575045131268541 — the same number to within floating
point, which is the point of the exercise.
"""

import math


def fir(b, x):
    """y[n] = sum_k b[k] * x[n-k], from rest. Same length as x."""
    y = []
    for n in range(len(x)):
        acc = 0.0
        for k, bk in enumerate(b):
            if n - k >= 0:
                acc += bk * x[n - k]
        y.append(acc)
    return y


def iir2(b0, a1, a2, x):
    """y[n] = b0*x[n] + a1*y[n-1] + a2*y[n-2], from rest. Same length as x."""
    y = []
    y1 = 0.0
    y2 = 0.0
    for xn in x:
        yn = b0 * xn + a1 * y1 + a2 * y2
        y.append(yn)
        y2 = y1
        y1 = yn
    return y


def roots_magnitude(a1, a2):
    """Magnitude of the larger root of lambda**2 - a1*lambda - a2 = 0."""
    d = a1 * a1 + 4.0 * a2
    if d < 0:
        return math.sqrt(-a2)
    r = math.sqrt(d)
    return max(abs((a1 + r) / 2.0), abs((a1 - r) / 2.0))


def dc_gain(b0, a1, a2):
    """Settled output for a constant input of 1."""
    return b0 / (1.0 - a1 - a2)


if __name__ == "__main__":
    print("moving average, impulse in:", fir([0.25] * 4, [1.0] + [0.0] * 5))
    r, th = 0.9, 0.4
    a1, a2 = 2 * r * math.cos(th), -r * r
    print("resonator coefficients:", a1, a2)
    print("its root magnitude:", roots_magnitude(a1, a2))
    print("its DC gain:", dc_gain(1.0, a1, a2))
    print("first six samples:", iir2(1.0, a1, a2, [1.0] + [0.0] * 5))
'''}],
                "hints": [
                    "In `fir`, guard the index: `if n - k >= 0`. Without it, `x[n - k]` with a negative index silently reads from the end of the list and the first few output samples come out wrong in a way that is hard to see.",
                    "In `iir2` the update order is the whole exercise. Compute `yn` first, then `y2 = y1`, then `y1 = yn`. Doing the two assignments the other way round loses `y1` and turns the second-order filter into a first-order one.",
                    "`roots_magnitude` needs the negative-discriminant branch. For a conjugate pair $\\lambda = \\alpha \\pm j\\beta$ the magnitude squared is $\\alpha^2+\\beta^2$, which works out to $-a_2$ — so `math.sqrt(-a2)`, and note this is only reachable when $a_2$ is negative.",
                    "`dc_gain` is `b0 / (1 - a1 - a2)`. If it comes out negative or enormous, check the sign convention: the recursion here *adds* the feedback terms, so the denominator subtracts them.",
                    "To convince yourself the last test is not a coincidence, change `r` and `th` and check that `sum(iir2(...))` still lands on `dc_gain(...)` for any pair inside the unit circle.",
                ],
                "tests": [
                    {"name": "a three-tap FIR, computed by hand", "code": r'''
y = fir([1.0, -2.0, 3.0], [1.0, 2.0, 3.0, 4.0])
assert len(y) == 4, f"an FIR returns one sample per input sample, so 4; got {len(y)}"
want = [1.0, 0.0, 2.0, 4.0]
assert all(abs(a - b) < 1e-12 for a, b in zip(y, want)), f"expected {want}, got {y}"
'''},
                    {"name": "the moving average, on an impulse and on a step", "code": r'''
h = fir([0.25] * 4, [1.0] + [0.0] * 5)
want = [0.25, 0.25, 0.25, 0.25, 0.0, 0.0]
assert all(abs(a - b) < 1e-12 for a, b in zip(h, want)), \
    f"an FIR's impulse response is its coefficient list: {want}; got {h}"
s = fir([0.25] * 4, [1.0] * 6)
want_s = [0.25, 0.5, 0.75, 1.0, 1.0, 1.0]
assert all(abs(a - b) < 1e-12 for a, b in zip(s, want_s)), \
    f"a step should ramp up over four samples then hold at 1: {want_s}; got {s}"
'''},
                    {"name": "the second-order resonator matches its closed form", "code": r'''
import math
r, th = 0.9, 0.4
a1, a2 = 2 * r * math.cos(th), -r * r
h = iir2(1.0, a1, a2, [1.0] + [0.0] * 11)
assert len(h) == 12, f"same length as the input, so 12; got {len(h)}"
want = [r ** n * math.sin((n + 1) * th) / math.sin(th) for n in range(12)]
worst = max(abs(a - b) for a, b in zip(h, want))
assert worst < 1e-9, \
    f"h[n] should be r**n sin((n+1)theta)/sin(theta); worst disagreement {worst}"
assert abs(h[0] - 1.0) < 1e-12, f"h[0] is just b0 times the impulse, so 1.0; got {h[0]}"
'''},
                    {"name": "the root magnitude, from the coefficients alone", "code": r'''
import math
r, th = 0.9, 0.4
a1, a2 = 2 * r * math.cos(th), -r * r
assert abs(roots_magnitude(a1, a2) - 0.9) < 1e-12, \
    f"a conjugate pair at radius 0.9 has magnitude 0.9; got {roots_magnitude(a1, a2)}"
assert abs(roots_magnitude(1.5, -0.5) - 1.0) < 1e-12, \
    "real roots at 1.0 and 0.5: the larger magnitude is 1.0"
assert abs(roots_magnitude(1.9, -0.95) - math.sqrt(0.95)) < 1e-12, \
    "a1**2 + 4*a2 is negative here, so the magnitude is sqrt(0.95)"
assert abs(roots_magnitude(0.0, 1.21) - 1.1) < 1e-12, \
    "roots at +-1.1: outside the unit circle, and this one must report it"
'''},
                    {"name": "the predicted DC gain is the one the recursion settles at", "code": r'''
import math
r, th = 0.9, 0.4
a1, a2 = 2 * r * math.cos(th), -r * r
g = dc_gain(1.0, a1, a2)
assert abs(g - 6.5750451312685385) < 1e-9, f"1/(1 - a1 - a2) is 6.57505; got {g}"
h = iir2(1.0, a1, a2, [1.0] + [0.0] * 400)
assert abs(sum(h) - g) < 1e-9, \
    f"the DC gain is the sum of the impulse response: predicted {g}, summed {sum(h)}"
assert abs(dc_gain(1.0, 0.5, 0.0) - 2.0) < 1e-12, \
    "the first-order case: 1/(1 - 0.5) = 2"
'''},
                    {"name": "a root outside the circle, and a response that runs away", "code": r'''
assert roots_magnitude(0.0, 1.21) > 1.0, "this pair sits outside the unit circle"
h = iir2(1.0, 0.0, 1.21, [1.0] + [0.0] * 40)
assert abs(h[40]) > abs(h[20]) > abs(h[0]), \
    f"an unstable recursion must grow: |h[0]| = {abs(h[0])}, |h[20]| = {abs(h[20])}, |h[40]| = {abs(h[40])}"
assert abs(h[40]) > 40.0, f"1.21**20 is about 45; got |h[40]| = {abs(h[40])}"
stable = iir2(1.0, 0.0, -0.81, [1.0] + [0.0] * 40)
assert abs(stable[40]) < abs(stable[20]), \
    "the same recursion with the root inside the circle must decay instead"
'''},
                ],
            },
        },

        # ---- M9 -----------------------------------------------------------
        {
            "title": "The DFT in practice: bins, resolution, leakage and windows",
            "summary": "The transform a computer can actually compute differs from the one module 3 defined in two ways, and every surprise in a measured spectrum comes from one of them.",
            "concepts": [
                "A machine never has $X(f)$. It has $N$ samples and returns $N$ numbers: $X[k] = \\sum_{n=0}^{N-1}x[n]e^{-j2\\pi kn/N}$, the **DFT**. Two things separate it from module 3's integral — the record is finite, and the frequency axis is a grid rather than a continuum — and between them they explain every unexpected thing a spectrum analyser has ever shown you.",
                "The grid: bin $k$ sits at $f_k = k\\,f_s/N$. So the spacing is $\\Delta f = f_s/N = 1/T_{rec}$, where $T_{rec} = N/f_s$ is the **length of the record in seconds**. Resolution is bought with time and with nothing else: double the sample rate while keeping the record the same duration and $N$ doubles too, leaving $\\Delta f$ exactly where it was.",
                "Sample rate buys **bandwidth**; record length buys **resolution**. They are separate purchases and confusing them is the most expensive mistake in practical spectrum work — you cannot resolve two tones 1 Hz apart in a 100 ms record no matter how fast the converter runs.",
                "For a real input only $k = 0 \\dots N/2$ carry new information; the rest are the conjugate mirror. That is why a single-sided amplitude spectrum divides by $N$ and then doubles every bin except DC and, for even $N$, the one at $f_s/2$ — those two have no partner to reclaim.",
                "Taking $N$ samples is multiplying the signal by a **rectangular window** $T_{rec}$ long. By the multiplication-convolution pair of module 6, the true spectrum is therefore *convolved* with that rectangle's transform — a $\\mathrm{sinc}$ whose nulls are spaced exactly $1/T_{rec}$, one bin, apart.",
                "If the tone sits exactly on a bin, every one of that $\\mathrm{sinc}$'s nulls lands on another bin centre and the result is one clean line with zeros beside it. This is the only circumstance in which the DFT of a sinusoid looks like a single line, and test signals are chosen to arrange it — a whole number of cycles in the record.",
                "If it does not, the nulls fall between the bins and every bin picks up something. That is **spectral leakage**. Nothing has gone wrong: the DFT is faithfully reporting the spectrum of what it was actually given, which is a sinusoid switched on and off at the ends of the record.",
                "Worst case is a tone halfway between two bins, where the peak reads about 36% low — **scalloping loss**, tending to $2/\\pi$ for a long record. A measurement that reports amplitude from a single bin can therefore be nearly 4 dB wrong for no reason but the arithmetic of where the tone happened to fall.",
                "A **window** other than the rectangle trades main-lobe width against sidelobe height. The Hann window $w[n] = \\frac12\\left(1 - \\cos\\frac{2\\pi n}{N-1}\\right)$ tapers the record to zero at both ends: its sidelobes are about 31 dB down instead of 13, so a small tone beside a large one becomes visible, but its main lobe is twice as wide, so two tones close together stop being separable. There is no window that is best; there is a window that suits what you are looking for.",
                "Windows cost amplitude. Hann's mean value is about $\\frac12$, so a windowed sinusoid's peak bin reads about half — divide by the window's mean (its **coherent gain**) to get volts back. It also *reduces* scalloping loss, from 36% to about 15%, which is often the real reason to use one.",
                "**Zero padding is not resolution.** Appending zeros raises $N$ without lengthening the record, so $f_s/N$ shrinks while $1/T_{rec}$ does not. What you get is the same underlying curve sampled on a finer grid — a smoother picture and an easier peak to locate — and two tones that were unresolved stay exactly as unresolved as they were. The only cure for resolution is more time.",
            ],
            "sandbox": {
                "title": "The record is 100 ms long, whatever the sample rate",
                "visualiser": "spectrum",
                "minutes": 10,
                "initial": {"fsig": 40, "fs": 200},
                "brief": r'''
Same two panels as module 3, read for a different purpose. The **top** panel is a fixed
window of 100 ms — treat it as the whole record a DFT would be handed — and the dots are
the samples in it. The **bottom** panel is the frequency axis those samples span, with
the dashed line at $f_s/2$.

The question this time is not where a tone lands but **what a DFT of this record could
tell them apart by**. That number is $\Delta f = 1/T_{rec}$, and since the window here
is always 100 ms long, it is always 10 Hz — no matter what either slider is set to.

Move the sample rate and count dots.
''',
                "notice": [
                    "It opens at 40 Hz sampled at 200 Hz: a dot every 5 ms across the 100 ms window, so 20 sample intervals in the record. A DFT of it would have bins 10 Hz apart, and 40 Hz falls on the fourth of them exactly — four whole cycles fit in the record, which is the condition for a clean single line.",
                    "Drag the sample rate to 400 Hz. Twice as many dots, and the window is still 100 ms wide. $N$ has doubled and $f_s$ has doubled, so $\\Delta f = f_s/N$ is unchanged at 10 Hz. What did change is the top of the frequency axis: the dashed Nyquist line moves out to 200 Hz. Sample rate bought bandwidth and bought no resolution at all.",
                    "Now drop the rate to 100 Hz. Half as many dots, the Nyquist line comes in to 50 Hz, and the bin spacing is *still* 10 Hz. The 40 Hz tone is now uncomfortably close to the edge of what can be represented, but it is no harder to distinguish from a 50 Hz tone than it was before.",
                    "Put the rate back to 200 and set the signal to 45 Hz. This picture does not change much — the visualiser draws an ideal line, because it knows the true frequency. A DFT does not: 45 Hz sits exactly halfway between bin 4 and bin 5, no whole number of cycles fits the record, and the transform would put energy in every bin and report a peak about 36% low. The gap between the clean line drawn here and what a finite record actually returns is the subject of this module.",
                    "Finally, 130 Hz at 200 Hz sampling. The alias appears at 70 Hz, exactly as in module 3 — and 70 is a multiple of 10, so it lands cleanly on bin 7. Aliasing *moves* a tone to the wrong bin; leakage *smears* it across all of them. They are different failures, they have different cures, and a spectrum showing both at once is why reading one takes practice.",
                ],
            },
            "quiz": {
                "title": "What a finite record can and cannot tell you",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A 100 ms record is captured at 10 kSa/s. What is the spacing between DFT bins?",
                        "opts": ["100 Hz", "10 Hz", "5 kHz", "10 kHz"],
                        "a": 1,
                        "why": r'''
$N = 0.1 \times 10{,}000 = 1000$ samples, so $\Delta f = f_s/N = 10{,}000/1000 = 10$ Hz
— which is also, and more memorably, $1/T_{rec} = 1/0.1\,\mathrm{s}$. Reach for the
second form: it says outright that the answer depends on the duration of the record and
on nothing else. The 5 kHz is $f_s/2$, the top of the axis rather than the spacing along
it, and confusing the two is the same confusion as mistaking bandwidth for resolution.
''',
                    },
                    {
                        "q": "You double the sample rate and keep the record the same length in seconds. What happens to the frequency resolution?",
                        "opts": [
                            "it halves — the bins get closer together",
                            "it doubles — the bins get further apart",
                            "it is unchanged; what you gain is bandwidth",
                            "it improves by $\\sqrt2$, as the noise averages down",
                        ],
                        "a": 2,
                        "why": r'''
Doubling $f_s$ over the same duration doubles $N$ as well, and $\Delta f = f_s/N$ is
unchanged. You get twice as many bins covering twice the frequency range, at the same
spacing. This is worth having as a reflex, because a converter that runs faster is
usually the easiest thing to buy and it is precisely the thing that does not help: to
resolve two close tones the only lever is a longer record.
''',
                    },
                    {
                        "q": "A 137 Hz tone is captured in a 100 ms record. What does its DFT look like?",
                        "opts": [
                            "a single clean line at 137 Hz",
                            "a single clean line at 140 Hz, the nearest bin",
                            "a peak near 140 Hz with non-zero content in every other bin, and a peak amplitude reading low",
                            "nothing — 137 is not representable, so the tone is lost",
                        ],
                        "a": 2,
                        "why": r'''
The bins are 10 Hz apart and there is none at 137, so no whole number of cycles fits the
record. The rectangular window's $\mathrm{sinc}$ nulls miss every bin centre and energy
appears everywhere — leakage — with the largest bin near 140 Hz reading below the true
amplitude. Nothing is broken: the record contains a sinusoid that starts and stops, and
that really does have a broad spectrum. Choosing a record length that holds a whole
number of cycles is what makes the clean answer possible, which is why test signals are
specified that way.
''',
                    },
                    {
                        "q": "Why does a tone sitting exactly on a bin produce a single line with zeros beside it?",
                        "opts": [
                            "because the DFT rounds each tone to its nearest bin",
                            "because the rectangular window's transform has nulls exactly one bin apart, and they land on every other bin centre",
                            "because leakage only affects frequencies above $f_s/4$",
                            "because an integer number of cycles has no spectrum outside its own frequency",
                        ],
                        "a": 1,
                        "why": r'''
Truncation convolves the spectrum with a $\mathrm{sinc}$ whose nulls are spaced
$1/T_{rec}$ — exactly the bin spacing. Centre that $\mathrm{sinc}$ on a bin and every
other bin sits on one of its zeros. Move it half a bin and every other bin sits near a
peak instead. Note the truncated sinusoid *does* have content at other frequencies; the
DFT simply samples the resulting curve at the points where it happens to vanish, which
is a much more fragile piece of good luck than it looks.
''',
                    },
                    {
                        "q": "What does applying a Hann window buy, and what does it cost?",
                        "opts": [
                            "buys about 18 dB of sidelobe suppression; costs a main lobe twice as wide, so close tones become harder to separate",
                            "buys resolution; costs computation",
                            "buys amplitude accuracy at no cost at all",
                            "buys noise rejection; costs nothing but a scale factor",
                        ],
                        "a": 0,
                        "why": r'''
The rectangle's first sidelobe is about 13 dB down and Hann's is about 31, so a small
tone next to a large one stops being buried — that is the purchase. The bill is a main
lobe twice as wide, so two tones one bin apart, which a rectangle would just about
separate, merge into one. There is also a factor of two in amplitude to divide out, and
scalloping loss falls from 36% to about 15%, which is often the real motive. No window
is best at everything; choosing one is choosing which failure you would rather have.
''',
                    },
                    {
                        "q": "A 1000-sample record is zero-padded to 4000 samples before transforming. What improves?",
                        "opts": [
                            "the resolution — two tones one bin apart can now be separated",
                            "the signal-to-noise ratio, by a factor of four",
                            "nothing whatever; zero padding is a no-op",
                            "the picture, which is now interpolated onto a four-times-finer grid, making the peak easier to locate",
                        ],
                        "a": 3,
                        "why": r'''
Zero padding raises $N$ without lengthening the record, so $f_s/N$ shrinks while
$1/T_{rec}$ — the width of the underlying $\mathrm{sinc}$ — does not. You are sampling
the same curve at more points: the display is smoother, the peak is easier to find and
interpolate, and the accuracy with which you can *estimate* a single tone's frequency
genuinely improves. What does not improve is the ability to tell two tones apart, since
the lobes doing the obscuring are exactly as wide as they were. It is not a no-op, but
it is not resolution.
''',
                    },
                ],
            },
            "numeric": {
                "title": "How far is the tone from the nearest bin?",
                "minutes": 7,
                "brief": r'''
A data logger captures **4096 samples at 48 kSa/s** and transforms the lot. Somewhere in
the record is a tone known to be at exactly 1000.00 Hz, and the question before reading
any amplitude off the result is whether that tone lands on a bin or between two.

Work out the bin spacing, find the nearest bin centre, and report the distance.
''',
                "prompt": "How far, in hertz, is the 1000.00 Hz tone from the centre of the nearest bin?",
                "note": "A positive number: the distance, not the signed offset. Two decimal places is plenty.",
                "figure": r'''
```
  bin      83        84        85        86        87
  Hz    972.66    984.38    996.09   1007.81   1019.53
                               ^
                               |
                            1000.00 Hz sits here
```

The bins are evenly spaced and the tone is not on one of them. That gap is what decides
whether the peak amplitude can be trusted.
''',
                "given": [
                    {"label": "Record length", "value": "4096 samples"},
                    {"label": "Sample rate", "value": "48.0 kSa/s"},
                    {"label": "Tone", "value": "1000.00 Hz"},
                ],
                "aside": "4096 samples at 48 kSa/s is a record 85.33 ms long, and 1000 Hz puts "
                         "85.33 cycles in it — the same fraction, which is not a coincidence: "
                         "the offset in bins and the fractional part of the cycle count are the "
                         "same number.",
                "answer": 3.90625,
                "tol": 0.05,
                "unit": "Hz",
                "hint": "$\\Delta f = f_s/N = 48000/4096$. Divide 1000 by that to find which bin "
                        "the tone falls between, then multiply the nearest whole bin index back "
                        "up and subtract.",
                "wrong": "If you got about 7.8, you rounded the bin index the wrong way; if you "
                         "got 11.7, you reported the bin spacing itself rather than the distance "
                         "to a bin.",
                "why": "$\\Delta f = 48000/4096 = 11.71875$ Hz. $1000/11.71875 = 85.333$, so the "
                       "tone sits a third of a bin above bin 85, whose centre is "
                       "$85 \\times 11.71875 = 996.09375$ Hz. The distance is "
                       "$1000 - 996.09375 = 3.90625$ Hz, which is $0.333$ of a bin — far "
                       "enough off-centre for the peak bin to read several per cent low and for "
                       "the neighbouring bins to be full of leakage. The fix costs nothing: "
                       "take 4080 samples instead of 4096. That is $48 \\times 85$, exactly 85 "
                       "cycles of 1000 Hz, and the tone lands dead on bin 85.",
            },
            "lab": {
                "title": "Leakage, and what a window costs to fix it",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Three functions, and then a measurement that shows why anyone bothers with windows.

- `dft_bin(x, k)` — one bin of the DFT, from the definition:
  $X[k] = \sum_{n=0}^{N-1}x[n]\,e^{-j2\pi kn/N}$, returned as a `complex`.
  `cmath.exp` does the exponential.
- `hann(n)` — the Hann window as a NumPy array of length `n`:
  $w[k] = \frac12\left(1 - \cos\frac{2\pi k}{n-1}\right)$ for $k = 0 \dots n-1$. It is
  zero at both ends and 1 in the middle.
- `peak_amplitude(x, w)` — multiply `x` by `w` sample by sample, scan bins
  $k = 0 \dots N/2$ for the largest $|X[k]|$, and scale that back to volts by
  $\dfrac{2}{N\,\overline{w}}$, where $\overline{w}$ is the mean of the window. Return a
  float.

That scale factor is doing two jobs. The $2/N$ is module 3's single-sided convention —
half the amplitude lives in the negative-frequency bin you are not looking at. The
$1/\overline{w}$ undoes the window's **coherent gain**, because tapering the record to
zero at both ends removes signal along with the leakage. It is correct for a sinusoid
somewhere in the middle of the band, which is all this lab measures.

Then run it three ways on a 1 V sinusoid in a 100-sample record: with exactly 10 cycles
in the record, with 10.5, and with 10.5 under a Hann window. Three numbers, and the
whole subject is in the gap between them.
''',
                "files": [{"name": "main.py", "content": r'''
"""Leakage: what a finite record does to a sinusoid that does not fit it."""

import cmath
import math

import numpy as np


def dft_bin(x, k):
    """One bin: X[k] = sum_n x[n] exp(-2j pi k n / N), as a complex."""
    # TODO: one loop over n, accumulating into a complex zero.
    return 0j


def hann(n):
    """The Hann window, length n: 0.5 (1 - cos(2 pi k / (n - 1)))."""
    # TODO: np.arange(n), then one expression. It must start and end at zero.
    return np.zeros(n)


def peak_amplitude(x, w):
    """Largest bin of the windowed record, scaled back to volts.

    Multiply x by w, scan k = 0 .. N//2 for the largest |dft_bin|, and return
    2 * that / (N * mean(w)).
    """
    # TODO: window, scan, scale.
    return 0.0


if __name__ == "__main__":
    N = 100
    k = np.arange(N)
    rect = np.ones(N)
    for cycles in (10.0, 10.5):
        x = np.sin(2 * np.pi * cycles * k / N)
        print(f"{cycles} cycles, rectangular:", peak_amplitude(x, rect))
    x = np.sin(2 * np.pi * 10.5 * k / N)
    print("10.5 cycles, Hann:", peak_amplitude(x, hann(N)))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Leakage: what a finite record does to a sinusoid that does not fit it.

Every number below came out of running this file, with N = 100.

    10 cycles,   rectangular  -> 0.9999999999999993   (exact, to floating point)
    10.5 cycles, rectangular  -> 0.6498861611437414   (35% low: scalloping loss)
    10.5 cycles, Hann         -> 0.8516654273879164   (15% low)
    10 cycles,   Hann         -> 0.9999806807021769   (the correction is honest)
    mean(hann(100))           -> 0.495

The rectangular half-bin figure tends to 2/pi = 0.6366 as the record lengthens;
at N = 100 it has not quite got there.
"""

import cmath
import math

import numpy as np


def dft_bin(x, k):
    """One bin: X[k] = sum_n x[n] exp(-2j pi k n / N), as a complex."""
    N = len(x)
    total = 0j
    for n, xn in enumerate(x):
        total += xn * cmath.exp(-2j * math.pi * k * n / N)
    return total


def hann(n):
    """The Hann window, length n: 0.5 (1 - cos(2 pi k / (n - 1)))."""
    k = np.arange(n)
    return 0.5 * (1.0 - np.cos(2.0 * np.pi * k / (n - 1)))


def peak_amplitude(x, w):
    """Largest bin of the windowed record, scaled back to volts."""
    x = np.asarray(x, dtype=float)
    w = np.asarray(w, dtype=float)
    xw = list(x * w)
    N = len(xw)
    best = 0.0
    for k in range(N // 2 + 1):
        m = abs(dft_bin(xw, k))
        if m > best:
            best = m
    return float(2.0 * best / (N * float(np.mean(w))))


if __name__ == "__main__":
    N = 100
    k = np.arange(N)
    rect = np.ones(N)
    for cycles in (10.0, 10.5):
        x = np.sin(2 * np.pi * cycles * k / N)
        print(f"{cycles} cycles, rectangular:", peak_amplitude(x, rect))
    x = np.sin(2 * np.pi * 10.5 * k / N)
    print("10.5 cycles, Hann:", peak_amplitude(x, hann(N)))
'''}],
                "hints": [
                    "`dft_bin` accumulates into `0j` so the sum stays complex when every sample is real. The exponent is `-2j * math.pi * k * n / N` — note `k * n`, not `k + n`.",
                    "`hann` divides by `n - 1`, not by `n`. With `n` the window never quite reaches zero at the far end, and the symmetry the window depends on is broken.",
                    "In `peak_amplitude`, convert the windowed array to a plain list before handing it to `dft_bin` if your loop indexes it — either works, but mixing NumPy scalars and `complex` is where the confusing type errors come from.",
                    "The mean of `hann(100)` is 0.495, not 0.5 — the $n-1$ in the denominator makes the window very slightly asymmetric about its centre in the mean. Use the actual mean rather than a hard-coded one half.",
                    "If the on-bin rectangular case comes out at 0.5 rather than 1.0, the factor of two for the single-sided convention is missing; if it comes out at 50, the division by $N$ is.",
                ],
                "tests": [
                    {"name": "one bin, against a hand-worked four-point transform", "code": r'''
x = [1.0, 2.0, 3.0, 4.0]
want = [10 + 0j, -2 + 2j, -2 + 0j, -2 - 2j]
for k, exp in enumerate(want):
    got = complex(dft_bin(x, k))
    assert abs(got - exp) < 1e-9, f"X[{k}] should be {exp}, got {got}"
d = [1.0, 0.0, 0.0, 0.0]
assert all(abs(complex(dft_bin(d, k)) - 1) < 1e-12 for k in range(4)), \
    "an impulse has every bin equal to 1"
'''},
                    {"name": "the Hann window is a taper to zero at both ends", "code": r'''
import numpy as np
w = np.asarray(hann(8), dtype=float)
assert len(w) == 8, f"asked for 8 points, got {len(w)}"
assert abs(w[0]) < 1e-15 and abs(w[7]) < 1e-15, \
    f"the Hann window starts and ends at exactly zero; got {w[0]} and {w[7]}"
assert abs(w[1] - 0.1882550990706332) < 1e-12, f"w[1] should be 0.18826, got {w[1]}"
assert abs(w[3] - 0.9504844339512095) < 1e-12, f"w[3] should be 0.95048, got {w[3]}"
assert all(abs(w[i] - w[7 - i]) < 1e-12 for i in range(4)), \
    f"the window must be symmetric about its centre: {list(w)}"
m = float(np.mean(np.asarray(hann(100), dtype=float)))
assert abs(m - 0.495) < 1e-12, f"mean(hann(100)) is 0.495; got {m}"
'''},
                    {"name": "a tone on a bin reads its true amplitude", "code": r'''
import numpy as np
N = 100
k = np.arange(N)
rect = np.ones(N)
a = peak_amplitude(np.sin(2 * np.pi * 10 * k / N), rect)
assert abs(a - 1.0) < 1e-9, \
    f"ten whole cycles in the record: the peak must read 1.0 exactly, got {a}"
a3 = peak_amplitude(3.0 * np.sin(2 * np.pi * 20 * k / N), rect)
assert abs(a3 - 3.0) < 1e-9, f"a 3 V tone must read 3.0, got {a3}"
'''},
                    {"name": "half a bin off, and the peak reads low", "code": r'''
import numpy as np
N = 100
k = np.arange(N)
rect = np.ones(N)
a = peak_amplitude(np.sin(2 * np.pi * 10.5 * k / N), rect)
assert abs(a - 0.6498861611437414) < 1e-9, \
    f"a half-bin offset costs about 35% of the amplitude; expected 0.64989, got {a}"
assert a < 0.7, "this is scalloping loss and it must be a large effect, not a rounding one"
'''},
                    {"name": "the window buys most of it back", "code": r'''
import numpy as np
N = 100
k = np.arange(N)
w = hann(N)
half = peak_amplitude(np.sin(2 * np.pi * 10.5 * k / N), w)
assert abs(half - 0.8516654273879164) < 1e-9, \
    f"the same half-bin tone under a Hann window should read 0.85167, got {half}"
onbin = peak_amplitude(np.sin(2 * np.pi * 10 * k / N), w)
assert abs(onbin - 0.9999806807021769) < 1e-9, \
    f"and an on-bin tone must still read ~1.0 once coherent gain is divided out, got {onbin}"
assert half > 0.6498861611437414, \
    "the whole point is that the window reads closer to the truth than the rectangle did"
'''},
                ],
            },
        },

        # ---- M10 ----------------------------------------------------------
        {
            "title": "Reconstruction: from a list of numbers back to a waveform",
            "summary": "Module 3 was the outward journey. Coming back is not automatic, and the filter that makes it work is chosen the same way the anti-alias filter was — backwards.",
            "concepts": [
                "Sampling turned a waveform into numbers and copied its spectrum to every multiple of $f_s$. **Reconstruction** is the return trip, and the two operations are not symmetric: sampling happens whether you like it or not, while nothing turns a list of numbers back into a waveform until something interpolates between them.",
                "In the frequency domain the job is stated in one line: keep the copy around DC and discard every other one. That is a low-pass filter with its cutoff somewhere between $B$ and $f_s - B$, and if $f_s > 2B$ there is somewhere for it to go.",
                "In the time domain the ideal filter is the $\\mathrm{sinc}$ of module 6's duality argument, and the result is the **Shannon interpolation formula**: $x(t) = \\sum_n x[n]\\,\\mathrm{sinc}\\!\\left(\\frac{t - nT_s}{T_s}\\right)$. Each term is 1 at its own sample instant and exactly zero at every other one, which is why the sum passes precisely through every sample and does something non-trivial in between.",
                "It cannot be built, for the reason module 6 gave: each $\\mathrm{sinc}$ extends infinitely in both directions, so the output at any instant depends on samples that have not been taken. Every real reconstruction is a truncated, delayed approximation of it, and the better the approximation the longer the delay.",
                "What a converter actually does is hold each sample for a full period — a **zero-order hold**. Its impulse response is a rectangle of width $T_s$, so by the standard pair of module 3 its frequency response is $T_s\\,\\mathrm{sinc}(f/f_s)$: a flat $T_s$ at DC — a constant gain that normalises away and is usually divided out, leaving $\\mathrm{sinc}(f/f_s)$ — with nulls exactly at every multiple of $f_s$.",
                "That $\\mathrm{sinc}$ is a real error in the passband — the **hold droop**. At $f_s/2$ it is $2/\\pi = 0.637$, which is $-3.92$ dB, and at a tenth of $f_s$ it is already $-0.14$ dB. It is corrected by pre-emphasising the digital signal with the inverse shape, or by living with it, and neither choice does anything about the images.",
                "The images sit at $kf_s \\pm f$ for every integer $k \\ge 1$, and the nearest one to a wanted signal at $f$ is at $f_s - f$. The hold attenuates both, and the ratio it leaves behind is clean: $\\mathrm{sinc}((f_s-f)/f_s)\\big/\\mathrm{sinc}(f/f_s) = f/(f_s - f)$, because the two sines are equal. A tone at $0.4f_s$ therefore comes out with its first image at exactly two thirds of its own amplitude. The hold is not a filter.",
                "So a **reconstruction filter** goes after the converter, and choosing it is the anti-alias problem run backwards: keep everything up to $B$, kill everything from $f_s - B$ upwards. The two constraints pull in opposite directions exactly as they did in module 3, and the window between them is the same shape.",
                "**Oversampling is what makes it easy.** At $f_s = 2.5B$ the first image is at $1.5B$, half an octave above the band edge, and no first-order filter can separate them. At $f_s = 8B$ it is at $7B$, nearly three octaves up, and one pole is plenty. Running a converter four times faster than it needs to be is cheaper than building the filter it would otherwise need, which is the whole reason cheap converters run fast.",
                "The same argument explains why the number quoted for a converter is a sample rate rather than a bandwidth. A 192 kSa/s audio converter is not carrying 96 kHz of music; it is carrying the same 20 kHz with the images pushed far enough away that a gentle analogue filter — one whose phase stays nearly linear across the band — is enough to remove them.",
            ],
            "tune": {
                "title": "The filter after the converter",
                "minutes": 10,
                "brief": r'''
A converter runs at **48 kSa/s** and reproduces a signal occupying DC to **3 kHz**. Two
things are leaving it: the signal you want, and the first image at
$f_s - B = 45$ kHz. One low-pass filter has to keep the first and remove the second.

That is one corner frequency and two requirements pulling opposite ways — the same
shape of problem as module 3's anti-alias filter, with the roles of "before" and "after"
exchanged. Move the corner too low and the top of the wanted band is attenuated; too
high and the image walks straight through and sits in the output as a spurious tone at
45 kHz — inaudible where it stands, which is exactly why it survives unnoticed until
something downstream mixes with it and puts it somewhere much less convenient.

Two sliders and one filter. Find the window, and notice how narrow it is: a factor of
fifteen in frequency between the two requirements leaves about 13% of room in the corner
frequency, because a single pole only rolls off at 20 dB per decade. That narrowness is
the argument for oversampling, stated as a slider you cannot quite move freely.
''',
                "prompt": "Keep 95% of the signal at 3 kHz, and put the 45 kHz image at least 13 dB down.",
                "note": "Both constraints must hold at once. There is a window, and it is narrower than it looks.",
                "model": "rc-lowpass",
                "initial": {"r": 1000, "c": 100},
                "constants": {"fsig": 3000, "fnoise": 45000},
                "constraints": [
                    {"k": "keep", "label": "≥ 0.95 of the wanted band kept at 3 kHz", "min": 0.95},
                    {"k": "reject", "label": "≤ −13 dB on the first image at 45 kHz", "max": -13.0},
                ],
            },
            "quiz": {
                "title": "Getting the waveform back",
                "minutes": 10,
                "questions": [
                    {
                        "q": "A converter running at 48 kSa/s reproduces a 20 kHz tone. Where is the lowest-frequency image at its output?",
                        "opts": ["68 kHz", "28 kHz", "24 kHz", "96 kHz"],
                        "a": 1,
                        "why": r'''
The images sit at $kf_s \pm f$: $48 - 20 = 28$ kHz, then 68, then 76, then 116. The
lowest is 28 kHz, only half an octave above the tone it belongs to. The zero-order hold
does attenuate it — $\mathrm{sinc}(28/48) = 0.53$, about 5.6 dB — but it attenuates the
wanted 20 kHz by $\mathrm{sinc}(20/48) = 0.74$ as well, so what leaves the converter is
an image at $20/28 = 71\%$ of the signal's own amplitude. Something else has to remove
it. The 24 kHz is $f_s/2$, which is where images *fold about*, not where this one lands.
''',
                    },
                    {
                        "q": "By how much does a zero-order hold attenuate the signal at exactly half the sample rate?",
                        "opts": [
                            "3.01 dB — a factor of $1/\\sqrt2$",
                            "6.02 dB — a factor of a half",
                            "not at all; a hold has a flat response",
                            "3.92 dB — a factor of $2/\\pi$",
                        ],
                        "a": 3,
                        "why": r'''
The hold's response is $\mathrm{sinc}(f/f_s)$, and at $f = f_s/2$ that is
$\sin(\pi/2)/(\pi/2) = 2/\pi = 0.6366$, which is $-3.92$ dB. It is close enough to 3 dB
to be mistaken for it and it is not the same number, and it comes from a completely
different mechanism — this is the transform of a rectangle, not the response of a pole.
At a tenth of $f_s$ the droop is only 0.14 dB, which is why oversampled converters can
often ignore it entirely.
''',
                    },
                    {
                        "q": "Why can the ideal reconstruction — a sum of $\\mathrm{sinc}$ functions — not be implemented?",
                        "opts": [
                            "because each sinc extends to $t = \\pm\\infty$, so the output now would depend on samples not yet taken",
                            "because summing infinitely many terms takes infinite arithmetic",
                            "because a sinc has infinite energy",
                            "because the samples are quantised, so the sum is only approximate anyway",
                        ],
                        "a": 0,
                        "why": r'''
Causality, exactly as for the brick-wall filter of module 6 — and it is the same filter,
which is the point. The sum being infinite is a nuisance rather than an obstruction: the
terms decay, so truncating them costs accuracy you can quantify. Quantisation is a
separate and much smaller error. What cannot be arranged at any price is knowing a
future sample, and the practical answer is to accept a delay: reconstruct sample $n$
using samples up to $n + m$, and hand the result over $m$ periods late.
''',
                    },
                    {
                        "q": "A 20 kHz band is reproduced first at 44.1 kSa/s and then at 176.4 kSa/s. What changes for the reconstruction filter?",
                        "opts": [
                            "nothing — the filter only has to pass 20 kHz either way",
                            "the first image moves from 24.1 kHz to 156.4 kHz, so a gentle filter replaces a very steep one",
                            "the droop at the band edge gets worse, so the filter has more to correct",
                            "the filter must be four times sharper, to match the four-times-higher rate",
                        ],
                        "a": 1,
                        "why": r'''
At 44.1 kSa/s the first image is at $44.1 - 20 = 24.1$ kHz — about a quarter of an
octave above the band edge, which demands a filter of enormous order and a phase
response to match. At 176.4 kSa/s it is at 156.4 kHz, nearly three octaves up, where a
single pole placed well above 20 kHz will do. The droop gets *better* too, since 20 kHz
is now a much smaller fraction of $f_s$: the hold droop at the 20 kHz band edge is
$\mathrm{sinc}(20/44.1) = 0.694$, or 3.17 dB, and it becomes
$\mathrm{sinc}(20/176.4) = 0.979$, or 0.18 dB. (The 3.92 dB figure quoted in the concepts
is the droop at $f_s/2$ — 22.05 kHz here — not at the band edge.) Oversampling buys both,
and this is why it is nearly universal.
''',
                    },
                    {
                        "q": "The reconstruction filter is implemented digitally, before the converter, rather than in analogue afterwards. What does it achieve?",
                        "opts": [
                            "the same thing, and more cheaply",
                            "the same thing, provided the digital filter has linear phase",
                            "nothing useful — the images are created by the conversion itself, so a filter upstream of it never sees them",
                            "it works, but adds a delay of one sample period",
                        ],
                        "a": 2,
                        "why": r'''
Nothing useful, and this is module 3's anti-alias question reflected. There, the damage
was done *at* the converter and a filter afterwards was too late; here, the images are
created *by* the converter and a filter before it is too early. The rule that covers
both: a filter can only act on what it can see, and each converter is a wall with a
different side to be on. The one genuinely useful thing a digital filter here can do is
inverse-sinc pre-emphasis, which corrects the droop — a passband error, not an image.
''',
                    },
                    {
                        "q": "A 1 kHz sine is reproduced by a zero-order hold at 8 kSa/s and viewed on a scope before any filtering. What do you see?",
                        "opts": [
                            "a clean 1 kHz sine — the hold interpolates it",
                            "a 1 kHz sine with visible noise on it",
                            "a staircase: eight flat steps per cycle, each 125 µs long",
                            "nothing recognisable, since 8 kSa/s is too slow for 1 kHz",
                        ],
                        "a": 2,
                        "why": r'''
A staircase, with a step every $T_s = 125$ µs and eight of them per cycle. The steps are
not noise and not an artefact of the scope: they are the images, drawn in the time
domain. Everything that makes the trace look unlike a sine is energy at $8 \pm 1$ kHz
and above, and running it through the reconstruction filter removes exactly that and
leaves the sine. Sampling at 8 kSa/s is entirely adequate for 1 kHz — the Nyquist
condition is satisfied with room to spare, and the staircase is a reconstruction problem
rather than a sampling one.
''',
                    },
                ],
            },
            "blanks": {
                "title": "The return trip, written out",
                "minutes": 9,
                "caption": "from samples to a waveform, and what a real converter does instead",
                "lang": "text",
                "brief": r'''
Five holes, and between them the whole of reconstruction: the ideal interpolation, the
property that makes it work, what a real converter substitutes for it, what that costs
in the passband, and what is left over to be filtered off.

Nothing is executed. Fill the holes and read it as a sentence about why every converter
has an analogue filter bolted to its output.
''',
                "listing": """Sampling every Ts seconds went one way. This is the way back.

  ideal:   x(t) = sum over n of  x[n] * ___

           each of those terms is 1 at its own sample instant,
           and ___ at every other sample instant

  real:    a converter holds each sample for Ts, so its response is

                    H(f) = ___

           whose value at f = fs/2, taken relative to its own
           value at DC, is ___

  left over: the copies that the analogue filter has to remove sit at

                    f = ___
""",
                "blanks": [
                    {
                        "prompt": "What is each sample multiplied by, to fill in the time between the samples?",
                        "hole": "?",
                        "opts": ["sinc(t/Ts)", "exp(-(t - n*Ts)/Ts)", "sinc((t - n*Ts)/Ts)", "cos(2*pi*n*t/Ts)"],
                        "a": 2,
                        "why": "One sinc per sample, **centred on that sample**: $\\mathrm{sinc}((t - nT_s)/T_s)$. It is the impulse response of the ideal low-pass, which is the filter the frequency-domain argument asks for.",
                        "whys": [
                            "The shape is right but it is not moved: every term would then be centred at the origin, and the sum would be one large sinc rather than an interpolation through the samples. The $n T_s$ is what puts each term where its sample is.",
                            "A decaying exponential is what an RC does, and it is one-sided, so it cannot be 1 at its own sample and zero at the others. Reconstructing with it gives a recognisable but distorted waveform — which is roughly what a badly designed output stage produces.",
                            "One sinc per sample, **centred on that sample**: $\\mathrm{sinc}((t - nT_s)/T_s)$. It is the impulse response of the ideal low-pass, which is the filter the frequency-domain argument asks for.",
                            "A cosine at a frequency that depends on the sample index is not an interpolation of anything; it would synthesise a different signal for every sample and none of them the right one.",
                        ],
                    },
                    {
                        "prompt": "What makes the sum pass exactly through every sample?",
                        "hole": "?",
                        "opts": ["also 1", "exactly zero", "one half", "as small as possible but not zero"],
                        "a": 1,
                        "why": "Exactly zero. $\\mathrm{sinc}(m)$ is zero for every non-zero integer $m$, so at $t = nT_s$ every term except the $n$th vanishes and the sum is $x[n]$ — no approximation, no residual.",
                        "whys": [
                            "If every term were 1 at every sample instant the sum would be the total of all the samples at every instant, which is a constant and carries no signal at all.",
                            "Exactly zero. $\\mathrm{sinc}(m)$ is zero for every non-zero integer $m$, so at $t = nT_s$ every term except the $n$th vanishes and the sum is $x[n]$ — no approximation, no residual.",
                            "A half would leave every sample contaminated by half of every other sample, and the reconstruction would not pass through the data it was built from.",
                            "‘Small’ would make the interpolation approximate, and it is not — it is exact. That exactness is what the sinc is chosen for, and it is what a truncated practical version gives up.",
                        ],
                    },
                    {
                        "prompt": "The impulse response of the hold is a rectangle Ts wide. What is its transform?",
                        "hole": "?",
                        "opts": ["Ts * sinc(f * Ts * Ts)", "1/(1 + j*2*pi*f*Ts)", "Ts, at every f", "Ts * sinc(f/fs)"],
                        "a": 3,
                        "why": "A rectangle of width $\\tau$ transforms to $\\tau\\,\\mathrm{sinc}(f\\tau)$, and here $\\tau = T_s = 1/f_s$ — so $T_s\\,\\mathrm{sinc}(f/f_s)$, with nulls at every multiple of $f_s$.",
                        "whys": [
                            "The argument is wrong dimensionally: $f\\tau$ is the dimensionless quantity the sinc takes, and $f\\tau^2$ has units of time and cannot be what goes inside it.",
                            "That is a single-pole low-pass, which is what a smoothing capacitor would give. A hold is not a pole: it is an exact rectangle in time, and its response has nulls, which no single pole ever does.",
                            "A flat response is what an ideal impulse would give — a converter that emitted a zero-width spike per sample. Real converters hold, and holding is what introduces the droop.",
                            "A rectangle of width $\\tau$ transforms to $\\tau\\,\\mathrm{sinc}(f\\tau)$, and here $\\tau = T_s = 1/f_s$ — so $T_s\\,\\mathrm{sinc}(f/f_s)$, with nulls at every multiple of $f_s$.",
                        ],
                    },
                    {
                        "prompt": "Evaluate that response at half the sample rate, as a fraction of what it is at DC.",
                        "hole": "?",
                        "opts": ["2/pi, or -3.92 dB", "1/sqrt(2), or -3.01 dB", "1/2, or -6.02 dB", "1 - the hold is flat there"],
                        "a": 0,
                        "why": "The $T_s$ out in front cancels in the ratio, leaving $\\mathrm{sinc}(1/2) = \\sin(\\pi/2)/(\\pi/2) = 2/\\pi = 0.637$, which is $-3.92$ dB. It is a passband error and it is corrected digitally if it is corrected at all.",
                        "whys": [
                            "The $T_s$ out in front cancels in the ratio, leaving $\\mathrm{sinc}(1/2) = \\sin(\\pi/2)/(\\pi/2) = 2/\\pi = 0.637$, which is $-3.92$ dB. It is a passband error and it is corrected digitally if it is corrected at all.",
                            "That is the half-power point of a pole, and the numerical closeness is a trap: 0.707 and 0.637 look alike on a plot and come from unrelated mechanisms. Nothing here has a corner frequency.",
                            "A half would be the value if the response fell linearly to zero at $f_s$; it does not, and the sinc is above the straight line everywhere between.",
                            "Flat is what an ideal impulse train would give. The whole reason for talking about the hold separately is that it is not flat.",
                        ],
                    },
                    {
                        "prompt": "Where are the copies the analogue filter still has to remove?",
                        "hole": "?",
                        "opts": ["at f/k for every integer k", "at fs/2 only", "at k*fs +- f, for every integer k >= 1", "at k*f for every integer k"],
                        "a": 2,
                        "why": "Sampling copied the spectrum to every multiple of $f_s$, so a component at $f$ appears again at $f_s \\pm f$, $2f_s \\pm f$, and so on. The nearest and largest is at $f_s - f$, and it is the one that sets the filter.",
                        "whys": [
                            "Dividing the frequency is not something either sampling or holding does. Nothing in this chain produces sub-harmonics.",
                            "$f_s/2$ is the line the images fold about, not a place any of them sits. A signal at $f_s/2$ exactly would have its image on top of itself, which is the degenerate case the strict Nyquist inequality excludes.",
                            "Sampling copied the spectrum to every multiple of $f_s$, so a component at $f$ appears again at $f_s \\pm f$, $2f_s \\pm f$, and so on. The nearest and largest is at $f_s - f$, and it is the one that sets the filter.",
                            "Integer multiples of $f$ are harmonics, and harmonics come from non-linearity. Everything in this module is linear, and a linear system never creates a frequency its input did not contain.",
                        ],
                    },
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A spectrum analyser, and the convolution theorem measured on its output",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Build the instrument this course has been describing, then use it to check the course's
central claim on data it produced itself.

Five functions, each small. Together they take a list of samples and tell you what
frequencies are in it, predict where an out-of-band tone will land, and demonstrate that
convolving two signals in time multiplies their spectra.

- `dft(x)` — the discrete Fourier transform from the definition,
  $X[k] = \sum_{n=0}^{N-1} x[n]\,e^{-j2\pi kn/N}$, returned as a list of `complex` of the
  same length as `x`. Write the sum out; the point is to know what the answer means.
- `amplitude_spectrum(x, fs)` — return `(freqs, amps)`, the single-sided spectrum.
  `freqs[k]` is $k f_s/N$ for $k = 0 \dots N/2$, and `amps[k]` is scaled so that a
  sinusoid of amplitude $A$ reads $A$: divide $|X[k]|$ by $N$, then double every bin
  except DC and, when $N$ is even, the one at $f_s/2$.
- `alias_of(f, fs)` — the frequency a tone at `f` will appear at after sampling at `fs`:
  reduce modulo `fs`, then fold anything above `fs/2` back down.
- `convolve(x, h)` — as in module 1, returning `len(x) + len(h) - 1` samples.
- `response_at(h, f, fs)` — the transfer function of an FIR filter with impulse response
  `h`, evaluated at frequency `f`, as a `complex`:
  $H = \sum_n h[n]\,e^{-j2\pi f n/f_s}$.

The last two are what make the demonstration possible: filter a sinusoid by convolution,
measure the amplitude of the result with your own analyser, and compare it with
$|H|$ computed directly. If the convolution theorem is true they agree to the last digit
your arithmetic can carry.

`cmath.exp` handles complex exponentials; `numpy` is available and useful for generating
test signals, but `numpy.fft` is not the exercise.
''',
        "deliverables": [
            "`dft` computing the transform from its definition, agreeing with hand-worked four-point cases.",
            "`amplitude_spectrum` returning frequencies in hertz and amplitudes scaled so a 3 V sinusoid reads 3 V.",
            "`alias_of` predicting the observed frequency of any tone, in band or out of it, including the folding above $f_s/2$.",
            "`convolve` and `response_at`, and a demonstration in `__main__` that filtering by convolution and multiplying spectra give the same answer.",
        ],
        "constraints": [
            "NumPy and the standard library only. `numpy.fft` defeats the purpose of the first deliverable, so write the sum yourself.",
            "`dft` must return a sequence of `complex` of the same length as its input, not magnitudes.",
            "Amplitudes are single-sided and scaled to volts: a 3 V sinusoid in the middle of the band must read 3.0, not 1.5 and not $3N/2$.",
            "`alias_of` must return a value between 0 and `fs/2` for every input, including frequencies well above the sample rate.",
        ],
        "rubric": [
            {"criterion": "The transform is the definition, not a library call",
             "weight": 25,
             "evidence": "`dft` implements the sum over n of x[n] exp(-2 pi j k n / N) and reproduces the four-point cases [1,2,3,4] -> [10, -2+2j, -2, -2-2j] and delta -> all ones."},
            {"criterion": "The spectrum is scaled and labelled correctly",
             "weight": 25,
             "evidence": "`amplitude_spectrum` returns frequencies in hertz with spacing fs/N, and a two-tone test signal of 3 V at 50 Hz and 1 V at 120 Hz reads 3.0 and 1.0 in the right bins with nothing elsewhere."},
            {"criterion": "Aliasing is predicted before it is measured",
             "weight": 20,
             "evidence": "`alias_of` folds correctly for tones below, at and far above the Nyquist frequency, and its prediction for a 1.7 kHz tone sampled at 1 kSa/s matches the peak the analyser actually finds."},
            {"criterion": "The convolution theorem is demonstrated, not asserted",
             "weight": 30,
             "evidence": "The DFT of a convolution equals the product of the zero-padded DFTs to numerical precision, and the amplitude the analyser measures at the output of an FIR filter matches |response_at| at that frequency."},
        ],
        "files": [
            {"name": "main.py", "content": r'''
"""A spectrum analyser, written from the definitions.

Fill in the five functions. Every one of them is a few lines; the difficulty is
entirely in getting the indices and the scaling right.
"""

import cmath
import math

import numpy as np


def dft(x):
    """Discrete Fourier transform: X[k] = sum_n x[n] exp(-2 pi j k n / N).

    Returns a list of `complex`, the same length as `x`.
    """
    # TODO: two loops, or one loop over k with a sum inside.
    return []


def amplitude_spectrum(x, fs):
    """Single-sided amplitude spectrum of `x` sampled at `fs`.

    Returns (freqs, amps) where freqs[k] = k * fs / N for k = 0 .. N // 2, and
    amps[k] is scaled so a sinusoid of amplitude A reads A.
    """
    # TODO: call dft, keep the first N // 2 + 1 bins, divide by N, and double
    #       every bin except DC and (for even N) the one at fs / 2.
    return [], []


def alias_of(f, fs):
    """The frequency a tone at `f` appears at once sampled at `fs`."""
    # TODO: reduce modulo fs, then fold anything above fs / 2 back down.
    return 0.0


def convolve(x, h):
    """Output of an LTI system with impulse response `h`, driven by `x`."""
    # TODO: as in module 1 — len(x) + len(h) - 1 samples.
    return []


def response_at(h, f, fs):
    """Transfer function of the FIR filter `h` at frequency `f`, as a complex."""
    # TODO: sum h[n] * cmath.exp(-2j * pi * f * n / fs) over n.
    return 0j


if __name__ == "__main__":
    fs = 1000.0
    n = np.arange(200)

    x = list(3.0 * np.sin(2 * np.pi * 50 * n / fs) + np.cos(2 * np.pi * 120 * n / fs))
    freqs, amps = amplitude_spectrum(x, fs)
    if amps:
        peaks = [(f, a) for f, a in zip(freqs, amps) if a > 0.1]
        print("peaks found:", [(round(f, 1), round(a, 3)) for f, a in peaks])

    print("1.7 kHz sampled at 1 kSa/s should appear at", alias_of(1700.0, fs), "Hz")

    h = [0.25] * 4
    y = convolve(list(np.cos(2 * np.pi * 100 * n / fs)), h)
    print("moving average at 100 Hz:", abs(response_at(h, 100.0, fs)))
'''}
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""A spectrum analyser, written from the definitions.

Every number quoted below came out of running this file.

    dft([1, 2, 3, 4])                 -> [10, -2+2j, -2, -2-2j]
    two tones, 3 V at 50 Hz and 1 V at 120 Hz, 200 samples at 1 kSa/s
                                      -> 3.000 in bin 10, 1.000 in bin 24,
                                         nothing above 1.3e-14 anywhere else
    alias_of(1700, 1000)              -> 300.0, and the analyser finds its peak there
    a 4-point moving average at 100 Hz -> |H| = 0.7694208842938134, and the measured
                                         amplitude of the filtered sinusoid agrees to
                                         within 1e-12
"""

import cmath
import math

import numpy as np


def dft(x):
    """Discrete Fourier transform: X[k] = sum_n x[n] exp(-2 pi j k n / N).

    Returns a list of `complex`, the same length as `x`.
    """
    N = len(x)
    out = []
    for k in range(N):
        total = 0j
        for n, xn in enumerate(x):
            total += xn * cmath.exp(-2j * math.pi * k * n / N)
        out.append(total)
    return out


def amplitude_spectrum(x, fs):
    """Single-sided amplitude spectrum of `x` sampled at `fs`.

    Returns (freqs, amps) where freqs[k] = k * fs / N for k = 0 .. N // 2, and
    amps[k] is scaled so a sinusoid of amplitude A reads A.
    """
    N = len(x)
    X = dft(x)
    half = N // 2
    freqs = [k * fs / N for k in range(half + 1)]
    amps = []
    for k in range(half + 1):
        m = abs(X[k]) / N
        at_nyquist = (N % 2 == 0) and (k == half)
        if k != 0 and not at_nyquist:
            m *= 2.0
        amps.append(m)
    return freqs, amps


def alias_of(f, fs):
    """The frequency a tone at `f` appears at once sampled at `fs`."""
    fa = f % fs
    if fa > fs / 2.0:
        fa = fs - fa
    return fa


def convolve(x, h):
    """Output of an LTI system with impulse response `h`, driven by `x`."""
    y = [0.0] * (len(x) + len(h) - 1)
    for i, xv in enumerate(x):
        for j, hv in enumerate(h):
            y[i + j] += xv * hv
    return y


def response_at(h, f, fs):
    """Transfer function of the FIR filter `h` at frequency `f`, as a complex."""
    total = 0j
    for n, hn in enumerate(h):
        total += hn * cmath.exp(-2j * math.pi * f * n / fs)
    return total


if __name__ == "__main__":
    fs = 1000.0
    n = np.arange(200)

    x = list(3.0 * np.sin(2 * np.pi * 50 * n / fs) + np.cos(2 * np.pi * 120 * n / fs))
    freqs, amps = amplitude_spectrum(x, fs)
    if amps:
        peaks = [(f, a) for f, a in zip(freqs, amps) if a > 0.1]
        print("peaks found:", [(round(f, 1), round(a, 3)) for f, a in peaks])

    print("1.7 kHz sampled at 1 kSa/s should appear at", alias_of(1700.0, fs), "Hz")

    h = [0.25] * 4
    y = convolve(list(np.cos(2 * np.pi * 100 * n / fs)), h)
    print("moving average at 100 Hz:", abs(response_at(h, 100.0, fs)))
'''}
        ],
        "hints": [
            "`dft` is two nested loops. Accumulate into a `0j` so the sum stays complex even when every sample is real.",
            "The scaling in `amplitude_spectrum` is the part everyone gets wrong. Divide by `N` first; then double, because a real sinusoid puts half its amplitude in the positive-frequency bin and half in the negative one you are discarding. DC has no partner, and neither does the bin at $f_s/2$ when `N` is even.",
            "`alias_of` is two lines: `fa = f % fs`, then fold if `fa > fs / 2`. Check it against the module 3 sandbox — 170 Hz sampled at 200 Hz must come back as 30.",
            "For the convolution theorem, both sequences have to be the same length as the result before transforming: pad `x` and `h` with zeros out to `len(x) + len(h) - 1`, then compare `dft` of the convolution with the elementwise product.",
            "To measure the amplitude at the output of a filter, throw away the first `len(h) - 1` samples — that is the transient — and analyse a block containing a whole number of cycles, or the energy leaks into neighbouring bins.",
        ],
        "tests": [
            {"name": "the transform matches hand-worked four-point cases", "code": r'''
X = dft([1.0, 2.0, 3.0, 4.0])
assert len(X) == 4, f"the DFT has as many bins as samples, got {len(X)}"
want = [10 + 0j, -2 + 2j, -2 + 0j, -2 - 2j]
for k, (got, exp) in enumerate(zip(X, want)):
    assert abs(complex(got) - exp) < 1e-9, f"X[{k}] should be {exp}, got {got}"
D = dft([1.0, 0.0, 0.0, 0.0])
assert all(abs(complex(v) - 1) < 1e-12 for v in D), \
    f"an impulse transforms to all ones, got {D}"
'''},
            {"name": "a two-tone signal reads back in volts", "code": r'''
import numpy as np
fs = 1000.0
n = np.arange(200)
x = list(3.0 * np.sin(2 * np.pi * 50 * n / fs) + 1.0 * np.cos(2 * np.pi * 120 * n / fs))
freqs, amps = amplitude_spectrum(x, fs)
assert len(freqs) == 101, f"200 samples give bins 0..100, so 101 of them; got {len(freqs)}"
assert abs(freqs[1] - 5.0) < 1e-12, f"the bin spacing is fs/N = 5 Hz, got {freqs[1]}"
assert abs(freqs[10] - 50.0) < 1e-12, f"bin 10 should be 50 Hz, got {freqs[10]}"
assert abs(amps[10] - 3.0) < 1e-9, f"the 3 V tone must read 3.0, got {amps[10]}"
assert abs(amps[24] - 1.0) < 1e-9, f"the 1 V tone must read 1.0, got {amps[24]}"
rest = max(amps[k] for k in range(len(amps)) if k not in (10, 24))
assert rest < 1e-9, f"nothing else should be present, but a bin holds {rest}"
'''},
            {"name": "the folding rule, in band and far out of it", "code": r'''
cases = [(30.0, 200.0, 30.0), (170.0, 200.0, 30.0), (100.0, 200.0, 100.0),
         (250.0, 200.0, 50.0), (400.0, 200.0, 0.0), (1700.0, 1000.0, 300.0),
         (600.0, 1000.0, 400.0)]
for f, fs, want in cases:
    got = alias_of(f, fs)
    assert abs(got - want) < 1e-9, f"{f} Hz sampled at {fs} should appear at {want}, got {got}"
    assert -1e-9 <= got <= fs / 2 + 1e-9, f"an alias must land in 0..fs/2, got {got}"
'''},
            {"name": "the analyser sees the alias the rule predicted", "code": r'''
import numpy as np
fs = 1000.0
n = np.arange(200)
x = list(np.sin(2 * np.pi * 1700 * n / fs))
freqs, amps = amplitude_spectrum(x, fs)
peak = max(range(len(amps)), key=lambda k: amps[k])
assert abs(freqs[peak] - alias_of(1700.0, fs)) < 1e-9, \
    f"the peak is at {freqs[peak]} Hz but alias_of predicted {alias_of(1700.0, fs)}"
assert abs(amps[peak] - 1.0) < 1e-9, \
    f"aliasing moves a tone without shrinking it, so the peak should read 1.0, got {amps[peak]}"
'''},
            {"name": "convolution in time is multiplication in frequency", "code": r'''
x = [1.0, -2.0, 3.0, 0.5]
h = [0.5, 0.25, -1.0]
y = convolve(x, h)
assert len(y) == 6, f"4 + 3 - 1 is 6 samples, got {len(y)}"
want = [0.5, -0.75, 0.0, 3.0, -2.875, -0.5]
assert all(abs(a - b) < 1e-12 for a, b in zip(y, want)), f"expected {want}, got {y}"
L = len(y)
X = dft(x + [0.0] * (L - len(x)))
H = dft(h + [0.0] * (L - len(h)))
Y = dft(y)
err = max(abs(complex(Y[k]) - complex(X[k]) * complex(H[k])) for k in range(L))
assert err < 1e-9, f"DFT(x * h) should equal DFT(x) DFT(h); largest disagreement {err}"
'''},
            {"name": "the measured filter response matches the computed one", "code": r'''
import numpy as np
fs = 1000.0
h = [0.25] * 4
assert abs(response_at(h, 0.0, fs) - 1.0) < 1e-12, \
    f"a four-point average has unity gain at DC, got {response_at(h, 0.0, fs)}"
assert abs(response_at(h, 250.0, fs)) < 1e-12, \
    f"it puts a null at fs/4 = 250 Hz, got {abs(response_at(h, 250.0, fs))}"
predicted = abs(response_at(h, 100.0, fs))
assert abs(predicted - 0.7694208842938134) < 1e-9, \
    f"|H| at 100 Hz should be 0.76942, got {predicted}"
n = np.arange(400)
y = convolve(list(np.cos(2 * np.pi * 100 * n / fs)), h)
block = y[3:303]
freqs, amps = amplitude_spectrum(block, fs)
k = amps.index(max(amps))
assert abs(freqs[k] - 100.0) < 1e-9, f"the output is still at 100 Hz, measured {freqs[k]}"
assert abs(amps[k] - predicted) < 1e-9, \
    f"measured amplitude {amps[k]} against computed |H| {predicted}"
'''},
        ],
    },
}
