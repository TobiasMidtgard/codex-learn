"""EE102 — Circuit Analysis II: Alternating Current.

A first-year course. It assumes school mathematics — trigonometry, a little
calculus notation, and nothing else — and it assumes EE101, which means Ohm's law
and a divider with steady voltages. Everything else is defined where it is used.

Authoring rules, same as the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * every expected number here was produced by running the code, not assumed
"""

COURSE = {
    "id": "EE102",
    "title": "Circuit Analysis II — Alternating Current",
    "band": 1,
    "level": "Beginner",
    "prereqs": ["EE101"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 120,
    "icon": "◉",
    "summary": (
        "In EE101 the voltages stood still. Here they move: every source is a sinusoid, "
        "and the two components that ignored a steady voltage — the capacitor and the "
        "inductor — start to matter more than the resistors. The course builds the "
        "vocabulary first (peak, RMS, phase, angular frequency), then the one idea that "
        "makes alternating current no harder than direct current: impedance, a resistance "
        "that depends on frequency. By the end you can look at a resistor and a capacitor "
        "and say, without simulating anything, which frequencies get through."
    ),
    "outcomes": [
        "Describe a sinusoid by its amplitude, frequency, angular frequency and phase, and convert between peak and RMS.",
        "State the impedance of a resistor, a capacitor and an inductor, and use it in a divider exactly as you used resistance.",
        "Explain, in terms of reactance rather than slogans, why a capacitor blocks direct current and passes alternating current.",
        "Find the corner frequency of a first-order RC or RL circuit, and predict the response a decade either side of it.",
        "Combine impedances in series and in parallel, and say which resistance actually sets a node's time constant.",
        "Classify any first-order circuit by inspection, and design a band-pass from two stages without letting one load the other.",
        "Place a resonance, choose its Q, and convert freely between Q, damping and −3 dB bandwidth.",
        "Separate real, reactive and apparent power, and size the capacitor that corrects an inductive load's power factor.",
        "Reduce a network to its Thévenin equivalent and choose the load that takes the most power from it.",
        "Measure a filter you did not build: sweep it, find its −3 dB point, and infer a component value from the measurement.",
    ],
    "assessment": "A quiz in every module; eight circuits drawn and measured in the schematic editor; four guided derivations; two design targets hit with sliders; six short Python labs; and a capstone that identifies three unknown filters from their responses alone.",
    "reading": [
        "*The Art of Electronics*, Horowitz & Hill — chapter 1, sections on capacitors and RC circuits.",
        "*Fundamentals of Electric Circuits*, Alexander & Sadiku — chapters 9 and 10 for phasors and impedance.",
        "Any oscilloscope manual, for the difference between the peak, peak-to-peak and RMS readings it offers.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Sinusoids, RMS and average power",
            "summary": "Before any circuit: how to describe a voltage that will not sit still, and how to say how big it is.",
            "concepts": [
                "A sinusoid is written $v(t) = V_p \\sin(2\\pi f t + \\phi)$. $V_p$ is the **amplitude** or peak value in volts, $f$ is the **frequency** in hertz (cycles per second), and $\\phi$ is the **phase** in radians.",
                "The **period** $T$ is the time for one complete cycle, in seconds, and $T = 1/f$. A 50 Hz wave has a period of 20 ms.",
                "**Angular frequency** $\\omega = 2\\pi f$ is the same fact in radians per second. It exists because $\\sin$ takes an angle, not a count of cycles. Almost every mistake in this course is a missing $2\\pi$.",
                "The **average** of a sinusoid over a whole cycle is exactly zero — the positive half cancels the negative half — so the average says nothing about how big the wave is.",
                "The **RMS** value is the root of the mean of the square: square the waveform, average that over a whole cycle, take the square root. For a sinusoid, and only for a sinusoid, $V_{rms} = V_p/\\sqrt{2} \\approx 0.707\\,V_p$.",
                "RMS is defined that way so that the average power in a resistor is $P = V_{rms}^2/R$, the same formula direct current uses. An RMS volt heats a resistor exactly as a steady volt does.",
            ],
            "read": [
                {
                    "title": "The four numbers that pin down a moving voltage",
                    "minutes": 11,
                    "body": r'''
A battery has one number written on it. Nine volts, and if you come back in an hour it
is still nine volts. Everything EE101 did rested quietly on that: a voltage was a
number, a current was a number, and no equation ever had to mention time.

Put an oscilloscope across a wall socket and the number is gone. What is on the screen
instead is a curve, sweeping up to a crest, back down through zero, on to a trough,
and round again — fifty times every second, and it was doing it before you plugged the
probe in. There is no single voltage to quote. There is a *shape*, and the first job
of this course is to find the small set of numbers that pin the shape down completely.

## Why this shape and not some other wiggle

A generator is a coil of wire turning in a magnetic field. The voltage it produces is
proportional to the *rate* at which the magnetic flux threading the coil changes; the
flux itself follows the cosine of the shaft angle; so the voltage follows the sine.
Nobody chose the shape. Take anything going round a circle at a steady rate, watch its
height, and you are watching a sinusoid — it is the shadow of uniform circular motion.
Hold that picture, because every piece of vocabulary in this module comes straight out
of it. "Angular frequency" is how fast the point goes round. "Phase" is where on the
circle it was when you started your stopwatch. "Amplitude" is the radius.

There is a second reason the shape earns a whole course, and it has nothing to do with
generators. Differentiate a sine and you get a cosine: the same shape, the same
frequency, shifted along. Integrate it and the same thing happens. Add two sinusoids
of the same frequency and — however you scale or shift them — the sum is another
sinusoid of that frequency. Nothing else survives all of that. Push a square wave
through a capacitor and what comes out is not a square wave; push a sinusoid through
any arrangement of resistors, capacitors and inductors and what comes out is a
sinusoid of *exactly the same frequency*, differing only in size and in timing.

Two numbers, then — a size ratio and a timing shift — say everything a linear circuit
does to a sinusoid at one frequency. That single fact is why the next nine modules can
work one frequency at a time and never write down a differential equation.

## Four numbers, and there is no fifth

$$v(t) = V_p\sin(2\pi f t + \phi) + V_{dc}$$

- $V_p$, the **amplitude** or **peak**, in volts: the height of the crest above the
  centre line.
- $f$, the **frequency**, in hertz: complete cycles per second.
- $\phi$, the **phase**, in radians: where in its cycle the wave is at $t = 0$.
- $V_{dc}$, the **offset**: the level the whole wave rides on. Usually zero, and taken
  as zero for the rest of this section.

That is the entire list. There is no other adjustment you can make to a sinusoid
without turning it into some other waveform.

Two derived quantities come up so often they get names of their own. The **period**
$T = 1/f$ is the time for one complete cycle, in seconds — it is what an instrument
actually measures, because a scope can time the gap between two crests but cannot
count cycles for a whole second. And the **peak-to-peak** value $V_{pp} = 2V_p$ is the
full swing from trough to crest, which is what a scope's automatic measurement panel
usually reports, because trough-to-crest is a subtraction it can do on what is already
on screen. If a number arrives from an instrument, check which of the two it is before
it goes into anything.

## The angle, and the $2\pi$ that everybody drops

Here is the detail that causes more wrong answers in this course than every other
mistake combined. **Sine does not take seconds.** It takes an angle. Writing
$\sin(50t)$ for a 50 Hz wave is not a slightly loose notation, it is a different wave
at a different frequency, and a calculator will happily give you a number for it.

One cycle is $2\pi$ radians. If there are $f$ cycles in a second, the angle advances by
$2\pi f$ radians every second, so at time $t$ the angle inside the sine is $2\pi f t$.
That coefficient is used so constantly that it is given its own symbol and its own
name:

$$\omega = 2\pi f \qquad\text{so}\qquad v(t) = V_p\sin(\omega t + \phi)$$

$\omega$ is the **angular frequency**, in radians per second. It is not a new physical
quantity — it is the same fact as $f$, counted in a different unit, in the way that a
speed can be in km/h or m/s. For the European mains, $\omega = 2\pi \times 50 = 314.16$
rad/s, so in one millisecond the wave advances $0.314$ rad, which is $18^\circ$: a
twentieth of a cycle, exactly as it should be for 1 ms out of a 20 ms period.

Both forms appear everywhere. $f$ is what the front panel of a signal generator says;
$\omega$ is what the algebra wants, because every formula from module 2 onwards has an
$\omega$ in it. Convert once, at the start, and stay in $\omega$.

## Worked: what is the mains voltage 3 milliseconds in?

European mains, taken as a clean 325 V peak sinusoid at 50 Hz, with the clock started
at an upward zero crossing so $\phi = 0$. What is the instantaneous voltage at
$t = 3.0$ ms?

```
f     = 50 Hz            T = 1/50 = 0.020 s = 20 ms
omega = 2*pi*50                            = 314.159 rad/s

angle at t = 3.0 ms   = 314.159 * 0.0030   = 0.94248 rad
                      = 0.94248 * 180/pi   = 54.0 degrees

v(3 ms)               = 325 * sin(0.94248)
                      = 325 * 0.80902
                      = 262.9 V
```

Check it against the picture before believing it. 3 ms out of a 20 ms period is
$3/20$ of a cycle, and $3/20$ of $360^\circ$ is $54^\circ$ — the two routes agree. The
crest is at $90^\circ$, which is 5 ms in, so at 3 ms the wave should be well up the
rise but not yet at the top. 262.9 V out of 325 V is exactly that.

Two wrong answers are worth having seen. Feed $0.003$ straight into the sine, forgetting
$\omega$ altogether, and you get $325 \times 0.003 = 0.975$ V — a thousand times too
small, and it does not *look* absurd sitting on a page, which is precisely what makes
it dangerous. Leave the calculator in degree mode and $\sin(0.94248^\circ) = 0.01645$
gives 5.35 V. Neither is caught by anything except the sanity check above.

## Phase: the same wave, arriving early or late

Phase answers "where in its cycle was the wave when my clock read zero?". Because sine
repeats every $2\pi$, a phase only ever means anything modulo $2\pi$ — and, more
importantly, a phase quoted for a single isolated wave is a statement about when you
chose to start the clock, not about the wave. Phase becomes physical only as a
*difference* between two waves of the same frequency.

To turn a phase into a time, factor $\omega$ out of the argument:

$$\sin(\omega t + \phi) = \sin\!\left(\omega\left(t + \frac{\phi}{\omega}\right)\right)$$

A phase of $\phi$ is the same wave shifted **earlier** by $\phi/\omega$ seconds. A
positive $\phi$ therefore *leads* — it has already got further round the circle — and a
negative $\phi$ *lags*. Equivalently, and often more usefully, a phase is a fraction of
a cycle: $\phi$ radians is $\phi/2\pi$ of a period, and $\theta$ degrees is
$\theta/360$ of a period.

## Worked: a 35 degree lag, in microseconds

A 400 Hz tone goes into an amplifier and comes out $35^\circ$ behind what went in. How
much later, in time, is the output?

```
T      = 1/400                     = 2.500 ms
phi    = -35 deg = -35*pi/180      = -0.61087 rad
omega  = 2*pi*400                  = 2513.27 rad/s

delay  = |phi| / omega
       = 0.61087 / 2513.27         = 2.4306e-4 s
                                   = 243.1 us

cross-check as a fraction of a cycle:
       (35/360) * 2.500 ms = 0.09722 * 2500 us = 243.1 us
```

Now change one thing. Feed the same amplifier a 4 kHz tone and suppose it still lags by
$35^\circ$; the delay is now $24.3\,\mu\text{s}$, ten times smaller, for the same phase.
**A phase is not a time.** It is a fraction of a cycle, and the same fraction is a
different number of seconds at every frequency. Two waves a quarter cycle apart are
5 ms apart at 50 Hz and 250 ns apart at 1 MHz. This is exactly why filter behaviour is
quoted in degrees rather than in seconds: the degrees stay put across a sweep while the
seconds move.

## The mistakes that actually happen

- **The missing $2\pi$.** Tempting because $f$ is the number printed on the generator
  and $\omega$ is not. If an answer comes out about 6.3 times too big or too small, this
  is why.
- **Degrees where radians belong.** Every formula in this course is in radians. The only
  place degrees survive is as a human-readable phase, and they have to be converted
  before they meet an $\omega$.
- **Peak taken for peak-to-peak.** An instrument that says 8.4 V is describing a wave
  whose amplitude is 4.2 V. Everything downstream is wrong by a factor of two if this
  is missed, and a factor of four once it reaches a power.
- **Treating phase as absolute.** "This wave has a phase of $30^\circ$" is meaningless
  on its own. "This wave lags that one by $30^\circ$" is a measurement.

## Where this description stops holding

Real waveforms are frequently not sinusoids at all: the square wave out of a logic
gate, the triangle in a sweep generator, the chopped-up mains inside a switching power
supply. Nothing above applies to them directly, and the $\sqrt2$ of the next unit
applies to them least of all.

What rescues the situation is Fourier's result: **any periodic waveform is a sum of
sinusoids** at whole-number multiples of its own repetition rate. A square wave is a
fundamental plus a third harmonic plus a fifth, and so on. Because every component in
this course is linear, superposition holds — work out what the circuit does to each
sinusoid separately and add the answers. So "one frequency at a time" is not a
restriction on what can be analysed; it is the *method*, and the sandbox in this module
shows the first half of it, a single wave standing as a single line on a frequency
axis.

Two limits are real, though. A waveform that never repeats — a switch-on transient, a
pulse, noise — is not a sum of harmonics of anything, and needs the Fourier or Laplace
*transform* rather than a series; that is a later course. And superposition itself
fails the moment a component is non-linear: a diode fed one frequency generates
frequencies that were never applied to it, which is how a radio receiver mixes and how
a distorting amplifier ruins a signal. Everything in EE102 is R, L and C, and all three
are linear.

Finally, all of this describes a **steady state**: the wave has been running long
enough that whatever the circuit did when it was first switched on has died away.
Module 4 puts a number on how long that takes.
''',
                },
                {
                    "title": "How big is a wave that is never the same size twice?",
                    "minutes": 12,
                    "body": r'''
Two electric heaters, identical, 20 Ω each. One is wired to a 100 V battery. The other
is wired to a generator producing a sinusoid that swings between $+100$ V and $-100$ V.
Which one gets hotter, and by how much?

The question is not rhetorical and the answer is not obvious. The alternating supply
reaches 100 V, but it is only there for an instant twice a cycle; the rest of the time
it is somewhere between, and half the time it is negative. Yet "negative" cannot mean
"cooling" — reverse the leads on the battery heater and it heats just the same. So we
need a rule for collapsing a whole waveform down to one number that says how big it is,
and the rule has to be built for the job rather than borrowed.

## The obvious measure, and why it is useless

Take the plain average over a whole cycle. For any sinusoid it is exactly zero: the
wave spends as long below the centre line as above it, by the same amounts, and the two
halves cancel. Zero for a 1 V wave, zero for a 1000 V wave, zero for the wave feeding
our heater. A measure that returns the same answer for every sinusoid ever generated
distinguishes nothing, and it is plainly not describing the heat.

You will still meet the figure **0.637** attached to the word "average", and it is
worth knowing where it belongs so it does not get used by accident. Rectify the wave
first — flip its negative half upwards — and the average of what is left is
$2/\pi = 0.6366$ times the peak. That is a genuine quantity, and cheap multimeters are
built around it, as the end of this unit explains. But it is the average of a
*different waveform*, not of the original one.

## Building the right measure out of the requirement

Rather than guessing at a formula, write down what we want the number to do and let
the algebra produce it.

At any single instant the resistor does not know or care that its voltage is moving.
Ohm's law holds instant by instant, so the power at that instant is

$$p(t) = \frac{v(t)^2}{R}$$

The heat produced over a cycle is the average of that. Since $R$ is a constant, it
comes outside the averaging:

$$P_{avg} = \frac{\langle v^2 \rangle}{R}$$

where $\langle\;\rangle$ means "average over one whole cycle". Now the demand: we want
a single voltage figure $V_{rms}$ such that the familiar direct-current formula
$P = V_{rms}^2/R$ gives that same average power. Comparing the two lines, there is only
one possible definition:

$$V_{rms} = \sqrt{\langle v^2 \rangle}$$

Read it backwards and the name falls out: take the **r**oot of the **m**ean of the
**s**quare. And notice what the squaring does for us for free. A square is never
negative, so nothing cancels — the negative half of the wave contributes exactly as
much as the positive half, which is what the physics said it should. RMS is not a
clever trick someone thought of; it is the only measure that could have worked.

## Where the $\sqrt2$ comes from

For the particular case of a sinusoid, $v = V_p \sin(\omega t)$, do the averaging with
the double-angle identity $\sin^2\theta = \frac{1}{2}(1 - \cos 2\theta)$:

$$v^2 = V_p^2\sin^2(\omega t) = \frac{V_p^2}{2}\left(1 - \cos 2\omega t\right)$$

The second term is itself a sinusoid — at twice the frequency — so over a whole cycle
its average is zero, by the same cancellation that made the plain average useless. All
that survives is the constant:

$$\langle v^2\rangle = \frac{V_p^2}{2} \qquad\Rightarrow\qquad V_{rms} = \frac{V_p}{\sqrt2} \approx 0.7071\,V_p$$

There is a picture for that $\tfrac12$. Plot $\sin^2$ and it is a hump that never goes
below zero, oscillating between 0 and 1, and symmetric about the value $\tfrac12$ — it
spends as much time above half-height as below. Its mean is $\tfrac12$, so the mean
square is half the peak square, and the root of that is the peak over $\sqrt2$.

Back to the two heaters. The alternating one is 100 V peak, so 70.7 V RMS, and it
delivers $70.7^2/20 = 250$ W against the battery's $100^2/20 = 500$ W. Exactly half.

## Worked: a 60 W lamp on a 230 V supply

The socket is labelled 230 V, which — as with every mains figure anywhere in the world
— is an RMS value. The lamp is an old filament type, so treat it as a plain resistor.

```
V_rms  = 230 V                P = 60 W

I_rms  = P / V_rms            = 60 / 230          = 0.26087 A
R      = V_rms / I_rms        = 230 / 0.26087     = 881.7 ohm
         (or straight from    R = V_rms^2 / P = 52900/60 = 881.7 ohm)

V_p    = sqrt(2) * 230        = 325.27 V
I_p    = sqrt(2) * 0.26087    = 0.36892 A

peak instantaneous power = V_p * I_p
                         = 325.27 * 0.36892        = 120.0 W
```

Three things in that block are worth more than the arithmetic.

The **325 V** is not a curiosity. Every part of the lamp fitting has to insulate against
325 V, not 230 V; and if you rectify that supply into a smoothing capacitor, the
capacitor charges towards 325 V, which is the figure the electrolytic has to be rated
for. Designing to 230 V is how equipment fails.

The **120 W** is exactly twice the average — that is general, not a coincidence of these
numbers, since $V_pI_p = 2V_{rms}I_{rms}$ for a resistive load. The instantaneous power
in the lamp swings between 0 and 120 W, a hundred times a second, and averages 60 W. A
filament has enough thermal mass to smooth that out. A cheap LED lamp does not, which
is why some of them visibly flicker at 100 Hz.

And the **RMS current** of 0.261 A is what a fuse or a cable rating is about, because a
fuse is a piece of wire that melts when enough heat goes into it — the same average
power calculation as the lamp's.

## Waveforms that are not sinusoids

The $\sqrt2$ is a property of the sine *shape*, and applying it by reflex to anything
else is the single most common error with RMS. Run the definition instead — square,
average, root — and everything behaves:

- **Square wave**, $\pm V_p$: the square of it is a constant $V_p^2$, whichever half of
  the cycle you are in. The mean of a constant is that constant, and the root of it is
  $V_p$. So $V_{rms} = V_p$. A $\pm5$ V square wave is 5 V RMS, not 3.54 V.
- **Triangle or sawtooth**, peak $V_p$: the mean square works out at $V_p^2/3$, so
  $V_{rms} = V_p/\sqrt3 = 0.577\,V_p$.
- **A steady voltage**: it is already its own RMS. 4 V DC is 4 V RMS.

The ratio $V_p/V_{rms}$ is called the **crest factor** — 1.414 for a sine, 1.000 for a
square, 1.732 for a triangle, and much larger for a spiky waveform. Instruments quote
the largest crest factor they can measure honestly.

## Worked: a ripple sitting on a level

A supply rail sits at 4.0 V with a substantial 6.0 V peak ripple on it:
$v(t) = 4.0 + 6.0\sin(\omega t)$, driving a 20 Ω resistive load. What average power
does the load take?

```
v(t)  = 4.0 + 6.0 sin(wt)

v^2   = 16 + 48 sin(wt) + 36 sin^2(wt)

average each term over one whole cycle:
    <16>              = 16                  a constant averages to itself
    <48 sin(wt)>      = 0                   a sinusoid averages to zero
    <36 sin^2(wt)>    = 36/2 = 18           the half from the section above

<v^2> = 16 + 0 + 18   = 34 V^2
V_rms = sqrt(34)      = 5.831 V
P     = 34 / 20       = 1.700 W
```

The tempting route is to say the DC part is 4 V RMS, the sinusoidal part is
$6/\sqrt2 = 4.243$ V RMS, and the total is $4 + 4.243 = 8.243$ V — which gives 3.40 W,
exactly double the truth. **RMS values do not add.** Mean squares add, because power
adds; and since RMS is the root of a mean square, RMS values combine in quadrature:

$$V_{rms} = \sqrt{V_1^2 + V_2^2}$$

for a DC level plus a sinusoid, or for any two components at different frequencies.
Check it here: $\sqrt{4^2 + 4.243^2} = \sqrt{16 + 18} = \sqrt{34} = 5.831$ V, the same
answer. Think of the two contributions as the sides of a right-angled triangle and the
total as the hypotenuse — never end to end.

The cross term vanished because $\langle\sin\rangle = 0$, and that is what makes the
quadrature rule work. It survives whenever the two components are at *different*
frequencies. Two sinusoids at the *same* frequency do not combine this way, because
their cross term does not average to zero; that case needs phase, which is module 2.

## Where RMS stops doing what you want

**It needs a resistor.** $P = V_{rms}^2/R$ was derived from $p = v^2/R$ holding at
every instant, which is true of a resistor and of nothing else. Put a capacitor or an
inductor in the circuit and the current is no longer in step with the voltage; there
are then instants where $v$ and $i$ have opposite signs and energy flows *back* out of
the component. Multiply RMS volts by RMS amps in that situation and you get the
**apparent** power, in volt-amperes, which is larger than the real power in watts. The
ratio between them is the power factor, and module 8 is about nothing else.

**It says nothing about shape or timing.** Squaring destroys the sign and averaging
destroys the position, so a wave and the same wave delayed have identical RMS values,
and so do waveforms that look nothing alike. That is a feature when you want heat and a
problem when you want to know what a signal is.

**Cheap meters do not measure it.** An average-responding multimeter rectifies the
input, averages that, and multiplies by the fixed **form factor**
$0.7071/0.6366 = 1.1107$ that turns a rectified average into an RMS value *for a
sine*, and only for a sine. Give it a
$\pm5$ V square wave and the rectified average is 5.000 V, so it displays
$5.000 \times 1.1107 = 5.55$ V where the truth is 5.00 V — 11% high, with no warning.
On the spiky current drawn by a rectifier the error is far worse. A meter that says
**true RMS** on the front squares, averages and roots the actual samples, which is
precisely what you are about to write in this module's lab.
''',
                },
            ],
            "sandbox": {
                "title": "One frequency, two ways of drawing it",
                "visualiser": "spectrum",
                "minutes": 8,
                "initial": {"fsig": 20, "fs": 200},
                "brief": r'''
The upper panel is a sinusoid against time, over a window of 100 ms. The lower panel
is the same wave against frequency: a single vertical line at the frequency of the
wave, and a dashed line at half the sample rate.

The dots are samples — the values a digital instrument would actually record. Ignore
them for now if you like; the two panels are the point.
''',
                "notice": [
                    "The window is 100 ms wide. At 20 Hz you count two complete cycles across it; set the frequency to 50 Hz and you count five, because the period is one over the frequency and nothing else.",
                    "The lower panel is one spike, at whatever the frequency slider says. A pure sinusoid is a single frequency and nothing else, which is exactly why the rest of this course can work at one frequency at a time.",
                    "The dots are 21 samples taken across the window at 200 Hz. Push the signal frequency past the dashed line at half the sample rate and an amber wave appears, at the lower frequency those samples have folded down to. Set the frequency to 220 Hz and the amber wave runs exactly through the dots: 21 samples that cannot tell 220 Hz from 20 Hz. That is aliasing, it belongs to a later course, and for now it is a reminder that a measurement is only as good as its sample rate.",
                ],
            },
            "quiz": {
                "title": "Describing a wave",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A voltage completes one full cycle every 20 ms. What is its frequency?",
                        "opts": ["20 Hz", "50 Hz", "0.02 Hz", "200 Hz"],
                        "a": 1,
                        "why": r'''
Frequency is one over the period: $f = 1/T = 1/0.020 = 50$ Hz. The trap is reading
the number 20 off the question and answering 20 Hz — that is the period in
milliseconds, not a frequency at all. Keep the units in the arithmetic and the
mistake becomes impossible: 1/(20 ms) is 50 per second.
''',
                    },
                    {
                        "q": "The mains supply in Europe runs at 50 Hz. What is its angular frequency $\\omega$?",
                        "opts": ["50 rad/s", "314 rad/s", "3.14 rad/s", "0.02 rad/s"],
                        "a": 1,
                        "why": r'''
$\omega = 2\pi f = 2\pi \times 50 = 314.16$ rad/s. Frequency counts cycles per
second; angular frequency counts radians per second, and there are $2\pi$ radians in
a cycle. The reason to bother is that $\sin$ takes an angle: you must write
$\sin(2\pi f t)$ or $\sin(\omega t)$, never $\sin(f t)$. A missing factor of $2\pi$
is the single most common error in this course.
''',
                    },
                    {
                        "q": "Why is the plain average of a sinusoid a useless measure of how big it is?",
                        "opts": [
                            "Because averaging is only defined for steady voltages",
                            "Because the average is 0.637 of the peak, which is hard to remember",
                            "Because over a whole cycle the positive and negative halves cancel exactly, giving zero",
                            "Because the average depends on where you start measuring",
                        ],
                        "a": 2,
                        "why": r'''
Over a complete cycle a sinusoid spends as long below zero as above, by the same
amounts, so the mean is exactly zero — for a 1 V wave and for a 1000 V wave alike.
A measure that returns zero for every sinusoid distinguishes nothing. The figure
0.637 is real but it belongs to the *rectified* wave, the one with its negative half
flipped upwards, which is a different waveform. Squaring before averaging is what
fixes this: a square is never negative, so nothing cancels.
''',
                    },
                    {
                        "q": "A 10 V peak sinusoid is applied across a 100 Ω resistor. What average power does the resistor dissipate?",
                        "opts": ["1 W", "0.5 W", "0.707 W", "0.1 W"],
                        "a": 1,
                        "why": r'''
Use the RMS value, not the peak: $V_{rms} = 10/\sqrt{2} = 7.071$ V, and
$P = V_{rms}^2/R = 50/100 = 0.5$ W. Putting the peak into the power formula gives
$100/100 = 1$ W, exactly twice the truth, and that is the whole reason RMS exists —
it is defined so that the direct-current power formula keeps working. The peak power
does momentarily reach 1 W, at the instants the wave is at its crest, but the
resistor's heating follows the average.
''',
                    },
                    {
                        "q": "A mains socket is labelled 230 V. That is an RMS figure. What is the peak voltage?",
                        "opts": ["230 V", "325 V", "163 V", "460 V"],
                        "a": 1,
                        "why": r'''
$V_p = \sqrt{2}\,V_{rms} = 1.414 \times 230 = 325$ V. RMS is always the smaller
number for a sinusoid, so dividing by $\sqrt{2}$ instead of multiplying (giving
163 V) has the relationship upside down. This is not a formality: the insulation and
the voltage rating of anything connected to that socket has to survive 325 V, not
230 V.
''',
                    },
                    {
                        "q": "A square wave switches instantly between +5 V and −5 V, spending equal time at each. What is its RMS value?",
                        "opts": ["5 V", "3.54 V", "0 V", "2.5 V"],
                        "a": 0,
                        "why": r'''
RMS is defined by the squaring, not by a fixed factor. Square this waveform and you
get a constant 25 V², whichever half of the cycle you are in; the mean of 25 is 25,
and the root of that is 5 V. The answer 3.54 V comes from applying $V_p/\sqrt{2}$ out
of habit, but that factor is a property of the *sine* shape alone. Zero is the plain
average, which cancels here exactly as it does for a sinusoid — which is why nobody
uses it.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "From the front panel to $v(t)$",
                    "minutes": 8,
                    "lang": "text",
                    "caption": "A generator's three settings, turned into the wave they produce.",
                    "brief": r'''
A signal generator has three knobs on it and produces one equation. This is the
translation, done slowly once so it can be done quickly afterwards.

Every angle below is in radians, because that is what $\sin$ takes.
''',
                    "listing": r'''
generator:   amplitude 2.0 V peak      frequency 250 Hz      phase 0

    v(t) = 2.0 * sin( ___ * t )        the coefficient of t, in rad/s

    period                       T  =  ___

    at t = 1.0 ms, the angle inside the sine  =  ___ rad

    at t = 1.0 ms, the output                 =  ___ V


now turn the phase knob to -90 degrees, everything else unchanged:

    at t = 0, the output                      =  ___ V

    the whole wave has moved later by         =  ___
''',
                    "blanks": [
                        {
                            "prompt": "The coefficient of $t$",
                            "hole": "omega",
                            "opts": ["250", "1570.8", "0.0040", "500"],
                            "a": 1,
                            "why": r'''
The coefficient of $t$ is $\omega = 2\pi f = 2\pi \times 250 = 1570.8$ rad/s, not the
250 printed on the panel. Sine takes an angle, and a cycle is $2\pi$ radians, so the
angle has to advance $2\pi$ times faster than the cycle count does. Writing
$\sin(250t)$ describes a wave of about 40 Hz instead.
''',
                        },
                        {
                            "prompt": "The period",
                            "hole": "T",
                            "opts": ["4.0 ms", "0.64 ms", "250 ms", "0.25 s"],
                            "a": 0,
                            "why": r'''
$T = 1/f = 1/250 = 0.0040$ s, which is 4.0 ms. The period is one over the frequency,
not one over $\omega$: 0.64 ms is $1/\omega$, which is a real time — how long the wave
takes to advance a single radian — but a whole cycle takes $2\pi$ of those.
''',
                        },
                        {
                            "prompt": "The angle inside the sine at $t = 1.0$ ms",
                            "hole": "angle",
                            "opts": ["0.25", "1.571", "250", "6.283"],
                            "a": 1,
                            "why": r'''
$\omega t = 1570.8 \times 0.0010 = 1.5708$ rad, which is $\pi/2$ — a quarter turn. It
had to be: 1.0 ms is a quarter of the 4.0 ms period, and a quarter of a cycle is a
quarter of $2\pi$. The value 6.283 is $2\pi$ itself, a whole cycle, which is where the
wave gets to at $t = 4$ ms.
''',
                        },
                        {
                            "prompt": "The output at $t = 1.0$ ms",
                            "hole": "v",
                            "opts": ["0.0", "1.41", "2.0", "-2.0"],
                            "a": 2,
                            "why": r'''
$v = 2.0\sin(\pi/2) = 2.0 \times 1 = 2.0$ V. A quarter cycle after an upward zero
crossing the wave is exactly at its crest, so the answer is the full amplitude. The
value 1.41 is $2.0/\sqrt2$, the RMS of this wave — a perfectly real number, and not
what the wave is doing at any particular instant.
''',
                        },
                        {
                            "prompt": "The output at $t = 0$ with a phase of $-90^\\circ$",
                            "hole": "v0",
                            "opts": ["0.0", "2.0", "-2.0", "-1.41"],
                            "a": 2,
                            "why": r'''
$v(0) = 2.0\sin(-\pi/2) = 2.0 \times (-1) = -2.0$ V. A phase of $-90^\circ$ starts the
wave a quarter of a cycle *before* the upward zero crossing, which is the bottom of the
trough. Nothing about the wave's size has changed — only where in its cycle it happens
to be when the clock starts.
''',
                        },
                        {
                            "prompt": "How much later the wave now happens",
                            "hole": "shift",
                            "opts": ["1.0 ms, a quarter of a period", "90 ms", "4.0 ms, a whole period", "0.25 ms"],
                            "a": 0,
                            "why": r'''
A phase $\phi$ shifts the wave by $\phi/\omega$ in time, so
$(\pi/2)/1570.8 = 1.0$ ms — and a negative phase means later. The quick route avoids
the arithmetic altogether: $90^\circ$ is a quarter of $360^\circ$, so the shift is a
quarter of the period, and the period is 4.0 ms. Note that the answer is a time only
because a frequency was given; the same $-90^\circ$ at 250 kHz would be 1.0 µs.
''',
                        },
                    ],
                },
                {
                    "title": "Root, mean, square — in that order, backwards",
                    "minutes": 8,
                    "lang": "text",
                    "caption": "The definition applied to a waveform the sqrt(2) does not fit.",
                    "brief": r'''
"RMS" is read outwards but computed inwards: **s**quare first, then take the **m**ean,
then take the **r**oot. Run those three steps on a square wave, where the familiar
$1/\sqrt2$ has no business being, and then on a sinusoid for comparison.
''',
                    "listing": r'''
waveform:   +3 V for half of every cycle,  -3 V for the other half

    step 1   square every value        every entry becomes  ___  V^2

    step 2   average over one cycle    the mean square is   ___  V^2

    step 3   take the square root      V_rms =              ___  V


    the same three steps on  3*sin(wt)  give   V_rms =      ___  V

    average power the square wave puts into 12 ohms  =      ___  W
''',
                    "blanks": [
                        {
                            "prompt": "Every squared value",
                            "hole": "sq",
                            "opts": ["9", "+9 then -9", "3"],
                            "a": 0,
                            "why": r'''
$(+3)^2 = 9$ and $(-3)^2 = 9$ as well. That is the whole reason the definition squares
before it averages: the sign disappears, so the negative half of the wave stops
cancelling the positive half and starts contributing to the heat, which is what it
physically does.
''',
                        },
                        {
                            "prompt": "The mean of those squares",
                            "hole": "mean",
                            "opts": ["0", "9", "4.5"],
                            "a": 1,
                            "why": r'''
The squared waveform is a constant 9 V², and the mean of a constant is that constant.
The tempting 4.5 comes from halving out of habit — but the halving in
$V_{rms} = V_p/\sqrt2$ came from averaging $\sin^2$, and there is no $\sin^2$ here.
''',
                        },
                        {
                            "prompt": "The root of the mean square",
                            "hole": "rms",
                            "opts": ["2.12", "3.00", "9.00"],
                            "a": 1,
                            "why": r'''
$\sqrt9 = 3.00$ V. A square wave's RMS value equals its peak — its crest factor is
exactly 1 — because it is at full amplitude the whole time. Answering 2.12 means
$3/\sqrt2$ was applied by reflex, and that factor belongs to the sine shape alone.
''',
                        },
                        {
                            "prompt": "The RMS of $3\\sin(\\omega t)$",
                            "hole": "sine",
                            "opts": ["3.00", "2.12", "1.50"],
                            "a": 1,
                            "why": r'''
Here the shortcut is the right one: $3/\sqrt2 = 2.121$ V. Same peak, same frequency,
and exactly half the heating of the square wave — because a sinusoid is at its peak for
only an instant, while a square wave is there for the whole half cycle.
''',
                        },
                        {
                            "prompt": "Average power from the square wave into 12 Ω",
                            "hole": "p",
                            "opts": ["0.75", "0.375", "1.50"],
                            "a": 0,
                            "why": r'''
$P = V_{rms}^2/R = 9/12 = 0.75$ W. Note that the mean square, 9 V², is exactly the
number the power formula wants — the square root in step 3 and the squaring in the
power formula undo one another, so for a power calculation you never needed the root at
all. Using 2.12 V here instead would give 0.375 W, half the truth.
''',
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "Read the size off the screen",
                    "minutes": 5,
                    "brief": r'''
An oscilloscope measures what it can see, which is not always what you want. Its
automatic panel reports the full swing of the trace, because trough-to-crest is a
subtraction it can do on the pixels in front of it.
''',
                    "prompt": "What is the RMS value of this waveform?",
                    "note": "Answer in volts, to three significant figures.",
                    "figure": r'''
A clean sinusoid on the screen, centred on the zero line with no offset. The scope's
automatic measurement panel reads `Vpp 8.40 V` · `Vmax +4.20 V` · `Vmin −4.20 V` ·
`freq 1.00 kHz`. Nothing has been done to the signal; that is simply what the
instrument chose to report about it.
''',
                    "given": [
                        {"label": "Waveform", "value": "sinusoid, no DC offset"},
                        {"label": "Peak-to-peak", "value": "8.40 V"},
                        {"label": "Frequency", "value": "1.00 kHz"},
                    ],
                    "aside": "The frequency is on the panel because a real instrument shows it. Nothing "
                             "in this question needs it \u2014 the RMS of a sinusoid does not depend on how "
                             "fast the sinusoid is going.",
                    "answer": 2.97,
                    "tol": 0.02,
                    "unit": "V",
                    "hint": "Two steps, in this order: get the amplitude from the full swing, then apply "
                            "the factor that belongs to the sine shape.",
                    "wrong": "5.94 V is $V_{pp}/\\sqrt2$ \u2014 the halving was skipped. 4.20 V is the "
                             "amplitude itself, with the $\\sqrt2$ skipped. 8.40 V is the panel reading "
                             "copied out unchanged.",
                    "why": "$V_p = V_{pp}/2 = 8.40/2 = 4.20$ V, and $V_{rms} = 4.20/\\sqrt2 = 2.970$ V. "
                           "The two divisions are easy to run together and lose one of: peak-to-peak is a "
                           "fact about the picture on the screen, and the $\\sqrt2$ is a fact about the "
                           "sine shape. Both are needed, and neither substitutes for the other.",
                },
                {
                    "title": "How long until it reaches six volts?",
                    "minutes": 7,
                    "brief": r'''
Nothing here is a formula to remember. Invert the sine to get the angle, then turn the
angle into a time — which is the only thing $\omega$ is for.
''',
                    "prompt": "How long after $t = 0$ does the voltage first reach $+6.0$ V?",
                    "note": "Answer in milliseconds, to three significant figures.",
                    "figure": r'''
$$v(t) = 12\sin(2\pi \times 60\,t)\;\text{volts},\qquad t\;\text{in seconds}$$

At $t = 0$ the wave is at zero and rising.
''',
                    "given": [
                        {"label": "Amplitude", "value": "12 V peak"},
                        {"label": "Frequency", "value": "60 Hz"},
                        {"label": "Phase", "value": "0"},
                        {"label": "Target", "value": "+6.0 V, first crossing"},
                    ],
                    "aside": "6.0 V is half of 12 V, and the sine reaches a half at 30\u00b0. A twelfth of a "
                             "cycle \u2014 which is a useful sanity check on whatever the calculator says.",
                    "answer": 1.389,
                    "tol": 0.01,
                    "unit": "ms",
                    "hint": "Solve $\\sin\\theta = 0.5$ for the smallest positive $\\theta$ in radians, then "
                            "divide by $\\omega$.",
                    "wrong": "8.73 ms is $\\theta/f$ with the $2\\pi$ missing. 79.6 ms is $30/\\omega$, the "
                             "angle left in degrees where radians were required. 4.17 ms is a quarter of "
                             "the period, which is when the wave reaches its *peak*, not half of it.",
                    "why": "$\\omega = 2\\pi \\times 60 = 376.99$ rad/s. The wave reaches 6.0 V when "
                           "$\\sin(\\omega t) = 6/12 = 0.5$, so $\\omega t = \\pi/6 = 0.5236$ rad, and "
                           "$t = 0.5236/376.99 = 1.389\\times10^{-3}$ s. The cross-check is cleaner than "
                           "the arithmetic: $\\pi/6$ is one twelfth of a full turn, and the period is "
                           "$1/60 = 16.67$ ms, so the answer is $16.67/12 = 1.389$ ms exactly. Note that "
                           "the wave is at half its height only a twelfth of the way into the cycle \u2014 a "
                           "sinusoid climbs fastest through zero and slowest near its crest.",
                },
                {
                    "title": "A ripple sitting on a level",
                    "minutes": 9,
                    "brief": r'''
A poorly smoothed supply, feeding a resistive load. There are two things on the rail at
once, and only one of them is a sinusoid.
''',
                    "prompt": "What average power does the 33 Ω load dissipate?",
                    "note": "Answer in watts, to three significant figures.",
                    "figure": r'''
$$v(t) = 2.5 + 7.0\sin(2\pi \times 100\,t)\;\text{volts}$$

A steady 2.5 V with a large sinusoidal ripple riding on it, across a 33 Ω resistor.
''',
                    "given": [
                        {"label": "Steady part", "value": "2.5 V"},
                        {"label": "Ripple", "value": "7.0 V peak, 100 Hz"},
                        {"label": "Load", "value": "33 Ω, purely resistive"},
                    ],
                    "aside": "Square the whole expression before averaging anything. The cross term "
                             "contains a bare $\\sin(\\omega t)$, and a sinusoid averages to zero over a "
                             "whole cycle \u2014 which is the only reason the two parts can be treated "
                             "separately at all.",
                    "answer": 0.932,
                    "tol": 0.008,
                    "unit": "W",
                    "hint": "Find the mean square of the whole waveform first. The power formula wants "
                            "$V_{rms}^2$, so the square root and the squaring cancel and you never need "
                            "the RMS value itself.",
                    "wrong": "1.68 W comes from adding the two RMS values, $2.5 + 4.95 = 7.45$ V, before "
                             "squaring \u2014 RMS values combine in quadrature, never end to end. 0.742 W "
                             "ignores the steady part; 0.189 W ignores the ripple.",
                    "why": "Squaring gives $v^2 = 6.25 + 35\\sin(\\omega t) + 49\\sin^2(\\omega t)$. "
                           "Averaged over a cycle the middle term vanishes and the last one halves, so "
                           "$\\langle v^2\\rangle = 6.25 + 24.5 = 30.75$ V², and "
                           "$P = 30.75/33 = 0.9318$ W. Equivalently "
                           "$V_{rms} = \\sqrt{2.5^2 + (7.0/\\sqrt2)^2} = \\sqrt{30.75} = 5.545$ V, the "
                           "quadrature rule, which is the same arithmetic wearing a different hat. Note "
                           "how much of the heat the ripple is responsible for: 0.742 W of the 0.932 W, "
                           "on an RMS value only about twice the steady level — because power goes as "
                           "the square, doubling a contribution's RMS value quadruples what it "
                           "dissipates.",
                },
                {
                    "title": "Which resistor gets hot?",
                    "minutes": 9,
                    "brief": r'''
The source is alternating, so every voltage and current in this circuit is moving. It
makes no difference at all to the method: with nothing but resistors in the network,
RMS volts and RMS amps obey Ohm's law and the divider exactly as steady ones did in
EE101, and the power they give is the average power. That equivalence is the entire
reason RMS is defined the way it is.
''',
                    "prompt": "What average power does the 680 Ω resistor dissipate?",
                    "note": "Answer in milliwatts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 24},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 680},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "r2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 220},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "24 V RMS, sinusoidal"},
                        {"label": "Series resistor", "value": "680 Ω"},
                        {"label": "Shunt resistor", "value": "220 Ω"},
                    ],
                    "aside": "The probe sits at the junction, so the divider gives you the voltage across "
                             "the 220 Ω directly. The 680 Ω has whatever is left of the source.",
                    "answer": 483.6,
                    "tol": 3.0,
                    "unit": "mW",
                    # Everything is read off the drawn circuit: the source value, both resistances
                    # and the solved junction voltage. Editing any component moves the measured
                    # answer rather than quietly leaving this check agreeing with a stale number.
                    "check": r'''
var R = c.values('R'), vs = c.values('V')[0];
var vj = c.vout();
c.assert(Math.abs(vj) < Math.abs(vs),
  "the junction of a plain divider cannot sit above the source: measured " + vj.toPrecision(4));
return 1000 * (vs - vj) * (vs - vj) / R[0];
''',
                    "hint": "Get the current first: the two resistors are in series, so one current runs "
                            "through both. Then $P = I_{rms}^2 R$ needs nothing else.",
                    "wrong": "847.1 mW is $V_s^2/R_1$ \u2014 the whole source put across the 680 Ω, which "
                             "would only be true if the 220 Ω were not in the circuit. 156.4 mW is the "
                             "power in the *other* resistor.",
                    "why": "In series the resistances add: $680 + 220 = 900$ Ω, so "
                           "$I_{rms} = 24/900 = 26.67$ mA. Then "
                           "$P_1 = I_{rms}^2 R_1 = (0.02667)^2 \\times 680 = 0.4836$ W = 483.6 mW. By the "
                           "other route, the junction sits at $24 \\times 220/900 = 5.867$ V, so the "
                           "680 Ω has $24 - 5.867 = 18.13$ V across it and "
                           "$18.13^2/680 = 483.6$ mW. As a check on both: the 220 Ω takes "
                           "$5.867^2/220 = 156.4$ mW, and $483.6 + 156.4 = 640.0$ mW, which is exactly "
                           "$24 \\times 0.02667$ \u2014 the power the source delivers. Nothing here used "
                           "the frequency, because a resistive network has no frequency in it.",
                },
                {
                    "title": "The current the source has to supply",
                    "minutes": 11,
                    "brief": r'''
Three resistors now, and the quantity asked for is neither a node voltage nor an RMS
one. Work it out in the units the circuit is stated in, and convert at the very end.
''',
                    "prompt": "What is the peak current drawn from the source?",
                    "note": "Answer in milliamps, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 24},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 470},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "r2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1000},
                            {"id": "r3", "kind": "R", "x": 12, "y": 4, "rot": 1, "value": 1500},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                            {"a": [12, 5], "b": [12, 7]},
                            {"a": [12, 7], "b": [9, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "24 V RMS, sinusoidal"},
                        {"label": "Series resistor", "value": "470 Ω"},
                        {"label": "First shunt", "value": "1.00 kΩ"},
                        {"label": "Second shunt", "value": "1.50 kΩ"},
                    ],
                    "aside": "Both shunt resistors have the same node above them and ground below them, "
                             "so they are in parallel however far apart they are drawn.",
                    "answer": 31.72,
                    "tol": 0.3,
                    "unit": "mA",
                    # The current is recovered from the drop across the series resistor rather than
                    # from a constant, so all three resistances and the source value come off the
                    # schematic. The final root-two is the only thing the prompt adds to the circuit.
                    "check": r'''
var R = c.values('R'), vs = c.values('V')[0];
c.assert(c.count('R') === 3, "this question is about all three resistors");
var irms = (vs - c.vout()) / R[0];
return 1000 * irms * Math.SQRT2;
''',
                    "hint": "Collapse the two shunt resistors into one, add the series resistor, and you "
                            "have the resistance the source actually sees. That gives an RMS current; the "
                            "question asked for a peak.",
                    "wrong": "22.43 mA is the RMS current \u2014 correct as far as it goes, but the question "
                             "asked for the peak. 23.09 mA uses only the 1.00 kΩ shunt and forgets the "
                             "1.50 kΩ. 15.86 mA has the $\\sqrt2$ upside down, dividing where it should "
                             "multiply.",
                    "why": "The shunt pair is $1000 \\times 1500/2500 = 600$ Ω, and the source therefore "
                           "sees $470 + 600 = 1070$ Ω. So $I_{rms} = 24/1070 = 22.43$ mA, and the peak "
                           "is $\\sqrt2$ times that: $22.43 \\times 1.4142 = 31.72$ mA. The order matters "
                           "less than the discipline of staying in one system: do the whole circuit in "
                           "RMS, where Ohm's law works unchanged, and apply the $\\sqrt2$ once, at the "
                           "end, to the single quantity the question asked about. Converting the source "
                           "to its peak at the start gives the same answer here, but on any question "
                           "involving power it will not.",
                },
            ],
            "derive": {
                "title": "Where the root two comes from",
                "minutes": 12,
                "vars": ["V_p", "V_rms", "omega", "t", "R", "P"],
                "brief": r'''
$V_{rms} = V_p/\sqrt2$ is quoted so often that it starts to look like a definition. It
is not. The definition is "the root of the mean of the square", and the $\sqrt2$ is
what that definition produces when the waveform happens to be a sine.

Four steps get from one to the other, and no integral is needed. The only fact used
about averaging is the one that made the plain average useless in the first place: over
a whole cycle, any sinusoid averages to zero.

Write $\omega$ for the angular frequency and $R$ for a plain resistance.
''',
                "steps": [
                    {
                        "prompt": "A voltage $v = V_p\\sin(\\omega t)$ sits across a resistance $R$. Write the *instantaneous* power $p$ dissipated in it, in terms of $V_p$, $\\omega$, $t$ and $R$.",
                        "answer": "\\frac{V_p^2 \\sin(\\omega t)^2}{R}",
                        "placeholder": "\\frac{\\ldots}{R}",
                        "hint": "A resistor does not know its voltage is moving. At every frozen instant $p = v^2/R$; substitute $v$ and square it.",
                        "deconstruct": [
                            "At one instant the resistor has $v$ across it and passes $v/R$ through it.",
                            "Power is voltage times current, so $p = v \\cdot v/R = v^2/R$.",
                            "Now put $v = V_p\\sin(\\omega t)$ into that and square the whole thing, amplitude included.",
                        ],
                    },
                    {
                        "prompt": "Use $\\sin^2\\theta = \\frac{1}{2}(1 - \\cos 2\\theta)$ with $\\theta = \\omega t$ to rewrite $p$ with no square left on the sine.",
                        "given": "The identity turns a squared sine into a constant plus a cosine at twice the frequency.",
                        "answer": "\\frac{V_p^2}{2R}(1 - \\cos(2 \\omega t))",
                        "placeholder": "\\frac{\\ldots}{2R}(1 - \\ldots)",
                        "hint": "Substitute, then gather the constants in front. The bracket should contain a 1 and a cosine and nothing else.",
                        "deconstruct": [
                            "Substituting gives $\\dfrac{V_p^2}{R} \\cdot \\dfrac{1}{2}(1 - \\cos 2\\omega t)$.",
                            "Pull the two constants together into a single $V_p^2/(2R)$ out front.",
                            "Read what this says physically: the power is a fixed level with a cosine at $2\\omega$ swinging about it, which is why a filament lamp on 50 Hz mains is heated at 100 Hz.",
                        ],
                    },
                    {
                        "prompt": "Average over one whole cycle. The cosine term is a sinusoid, so its average is zero. Write the average power $P$.",
                        "answer": "\\frac{V_p^2}{2R}",
                        "placeholder": "\\frac{\\ldots}{2R}",
                        "hint": "Only the constant term survives the averaging, and the constant is everything outside the bracket times the 1 inside it.",
                        "deconstruct": [
                            "The average of a sum is the sum of the averages, so take the two terms separately.",
                            "$\\langle 1 \\rangle = 1$, because a constant averages to itself.",
                            "$\\langle \\cos 2\\omega t \\rangle = 0$ over a whole cycle, so the bracket averages to 1 and only the prefactor is left.",
                        ],
                    },
                    {
                        "prompt": "RMS is *defined* so that $P = V_{rms}^2/R$ holds. Set that equal to the $P$ you just wrote and give $V_{rms}$ in terms of $V_p$.",
                        "answer": "\\frac{V_p}{\\sqrt{2}}",
                        "placeholder": "\\frac{V_p}{\\ldots}",
                        "hint": "The $R$ appears on both sides and cancels, leaving $V_{rms}^2 = V_p^2/2$. Take the positive root.",
                        "deconstruct": [
                            "$\\dfrac{V_{rms}^2}{R} = \\dfrac{V_p^2}{2R}$.",
                            "Multiply both sides by $R$: $V_{rms}^2 = V_p^2/2$.",
                            "Root both sides, taking the positive one, since an RMS value is never negative.",
                        ],
                    },
                ],
                "closing": r'''
Look at what was actually used. Ohm's law at an instant, one trigonometric identity,
and the fact that a sinusoid averages to zero over a whole cycle. No integral appeared,
because the identity did the integrating for us — it converted the squared sine into
something whose average could simply be read off.

More importantly, look at what was *not* used. Nothing above depends on $\omega$, so
the $\sqrt2$ is the same at 50 Hz and at 50 MHz. Nothing depends on $R$; it cancelled.
And nothing depends on where the clock was started, because a phase would have gone in
as $\cos(2\omega t + 2\phi)$ and still averaged to zero.

What everything *does* depend on is the shape. The $\tfrac12$ came out of
$\sin^2\theta$ and belongs to the sine and to nothing else. Run the same three
steps — square, average, root — on a square wave and the squared waveform is a
constant, so the mean square is $V_p^2$ and the RMS is $V_p$ itself. On a triangle the
mean square works out at $V_p^2/3$. The procedure is universal; the $\sqrt2$ is a
special case, and treating it as the definition is the mistake this derivation exists
to prevent.
''',
            },
            "lab": {
                "title": "Measure RMS from samples",
                "runtime": "python",
                "minutes": 25,
                "brief": r'''
An instrument does not know any formulae. It takes samples and computes.

Write three small functions.

`sample(vp, f, fs, n, phase=0.0)` returns `n` samples of
$v(t) = V_p\sin(2\pi f t + \phi)$, taken at `fs` samples per second, as a NumPy
array. Sample `k` is taken at time $t = k/f_s$, so the first sample is at $t = 0$.

`rms(v)` returns the root of the mean of the square of an array — square every
sample, take the mean, take the square root. Do not use the $\sqrt{2}$ shortcut: the
point is that this definition works for any waveform.

`average_power(v, r)` returns the average power a resistance `r` would dissipate
with that waveform across it.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def sample(vp, f, fs, n, phase=0.0):
    """n samples of vp*sin(2*pi*f*t + phase), taken at fs samples per second."""
    # TODO: build the time array first, then the waveform.
    return np.zeros(n)


def rms(v):
    """Root of the mean of the square. No sqrt(2) shortcuts."""
    # TODO
    return 0.0


def average_power(v, r):
    """Average power dissipated in a resistance r by the waveform v."""
    # TODO
    return 0.0


if __name__ == "__main__":
    v = sample(10.0, 50.0, 10000.0, 10000)
    print("peak:", round(float(np.max(v)), 4))
    print("rms:", round(rms(v), 6))
    print("average power into 100 ohms:", round(average_power(v, 100.0), 6), "W")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def sample(vp, f, fs, n, phase=0.0):
    """n samples of vp*sin(2*pi*f*t + phase), taken at fs samples per second."""
    t = np.arange(n) / float(fs)
    return vp * np.sin(2.0 * np.pi * f * t + phase)


def rms(v):
    """Root of the mean of the square. No sqrt(2) shortcuts."""
    v = np.asarray(v, dtype=float)
    return float(np.sqrt(np.mean(v * v)))


def average_power(v, r):
    """Average power dissipated in a resistance r by the waveform v."""
    return rms(v) ** 2 / float(r)


if __name__ == "__main__":
    v = sample(10.0, 50.0, 10000.0, 10000)
    print("peak:", round(float(np.max(v)), 4))
    print("rms:", round(rms(v), 6))
    print("average power into 100 ohms:", round(average_power(v, 100.0), 6), "W")
'''}],
                "hints": [
                    "`np.arange(n) / fs` is the time array: sample `k` sits at $t = k/f_s$.",
                    "`np.mean(v * v)` is the mean of the square; the elementwise product is what you want, not a dot product.",
                    "`average_power` can call `rms` — it is $V_{rms}^2/R$, and reusing the function you just wrote is the whole point of having written it.",
                ],
                "tests": [
                    {"name": "the waveform starts at zero and peaks a quarter-cycle later", "code": r'''
import numpy as np
_v = sample(10.0, 50.0, 10000.0, 10000)
assert len(_v) == 10000, f"expected 10000 samples, got {len(_v)}"
assert abs(_v[0]) < 1e-12, f"sin(0) is 0, so the first sample should be 0, got {_v[0]}"
assert abs(_v[50] - 10.0) < 1e-9, \
    f"a quarter of a 20 ms period is 5 ms, which is sample 50, and there the wave is at its peak; got {_v[50]}"
'''},
                    {"name": "the RMS of a sinusoid is the peak over root two", "code": r'''
import numpy as np
_v = sample(10.0, 50.0, 10000.0, 10000)
_r = rms(_v)
assert abs(_r - 10.0 / np.sqrt(2)) < 1e-9, \
    f"50 whole cycles of a 10 V peak sine should give 7.0710678 V rms, got {_r}"
'''},
                    {"name": "the RMS of a steady voltage is that voltage", "code": r'''
import numpy as np
_r = rms(np.full(500, 4.0))
assert abs(_r - 4.0) < 1e-12, \
    f"a steady 4 V is already 4 V rms — the sqrt(2) belongs to the sine shape alone; got {_r}"
'''},
                    {"name": "the RMS of a square wave is its peak", "code": r'''
import numpy as np
_sq = np.array([5.0] * 100 + [-5.0] * 100)
_r = rms(_sq)
assert abs(_r - 5.0) < 1e-12, \
    f"squaring gives a constant 25, so the rms is 5; got {_r} (3.54 would mean a sqrt(2) was applied out of habit)"
'''},
                    {"name": "phase does not change the RMS", "code": r'''
import numpy as np
_a = rms(sample(3.0, 50.0, 10000.0, 10000, phase=0.0))
_b = rms(sample(3.0, 50.0, 10000.0, 10000, phase=1.234))
assert abs(_a - 3.0 / np.sqrt(2)) < 1e-9, f"a 3 V peak sine is 2.1213 V rms, got {_a}"
assert abs(_a - _b) < 1e-9, f"shifting a wave in time cannot change its size: {_a} vs {_b}"
'''},
                    {"name": "average power uses the RMS, not the peak", "code": r'''
import numpy as np
_p = average_power(sample(10.0, 50.0, 10000.0, 10000), 100.0)
assert abs(_p - 0.5) < 1e-9, \
    f"10 V peak into 100 ohms averages 0.5 W; 1.0 W would mean the peak went into the formula. Got {_p}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Phasors and impedance",
            "summary": "One idea replaces all of the calculus: at a fixed frequency, a capacitor and an inductor are just resistances that depend on frequency.",
            "concepts": [
                "In a resistor the current and the voltage rise and fall together — they are **in phase**. In a capacitor the current reaches its peak a quarter of a cycle *before* the voltage does; in an inductor, a quarter of a cycle *after*.",
                "A **phasor** is a complex number that carries the amplitude and the phase of a sinusoid at one fixed frequency. It is a bookkeeping device: it lets you add two sinusoids of the same frequency by adding two complex numbers.",
                "The $j$ below is the square root of −1 — electrical engineering writes $j$ because $i$ already means current. Two facts about it carry this whole course: the number $a + jb$ has **magnitude** $\\sqrt{a^2 + b^2}$, and multiplying by $j$ advances a phasor by a quarter of a cycle. EE111 develops the algebra properly; nothing here needs more than those two.",
                "**Impedance** $Z$ is the ratio of voltage phasor to current phasor, measured in ohms. It is complex: its magnitude says how much the component resists, its angle says how far the current is shifted from the voltage.",
                "$Z_R = R$, $Z_C = \\dfrac{1}{j\\omega C}$ with magnitude $\\dfrac{1}{\\omega C}$, and $Z_L = j\\omega L$ with magnitude $\\omega L$.",
                "A capacitor's magnitude $1/(\\omega C)$ grows without bound as the frequency falls to zero, so at DC it is an open circuit — it blocks. It falls towards zero as frequency rises, so at high frequency it is nearly a wire.",
                "An inductor is the mirror image: $\\omega L$ is zero at DC, so it is a plain wire there, and large at high frequency.",
                "Impedances in series add, exactly as resistances do — but as complex numbers, so a 100 Ω resistor in series with 100 Ω of reactance gives $|Z| = \\sqrt{100^2 + 100^2} = 141$ Ω, not 200 Ω.",
                "**Reactance** is the part of the impedance that shifts the phase. It stores energy and hands it back; it dissipates nothing. Only resistance turns electrical energy into heat.",
            ],
            "read": [
                {
                    "title": "What the two new components are actually doing",
                    "minutes": 12,
                    "body": r'''
Every component in EE101 was a resistor, and a resistor has an opinion about exactly one
thing: how much current flows for a given voltage. Put six volts across a 3 kΩ resistor
and 2 mA flows — now, in an hour, and it makes no difference whatever how the six volts
came to be there.

The capacitor and the inductor are not like that. Neither of them has any opinion about
voltage at all. What each responds to is *change*, and that one difference is the whole
of this module. Reactance, phase, impedance, the $j$ that turns up in the next reading —
all of it is bookkeeping laid on top of two derivatives.

## A capacitor is two plates that never touch

Physically it is two conductors held close together and kept apart by an insulator: two
strips of aluminium foil with a film of plastic between them, rolled up. There is no
conducting path from one plate to the other. That is not a defect to be worked around;
it is the component.

Drive current into the top plate and the charge has nowhere to go, so it accumulates.
The charge $q$ that piles up and the voltage $v$ that appears between the plates are in
strict proportion, and the constant of proportionality is what "capacitance" names:

$$q = C\,v$$

$C$ is in farads, which is coulombs per volt. A farad is enormous; real parts run from
picofarads to millifarads, and the ones marked in whole farads are a specialised part
with a different construction entirely.

Now the step that matters. Current is not charge, it is the *rate* at which charge
arrives — amps are coulombs per second. So differentiate both sides:

$$i = \frac{dq}{dt} = C\,\frac{dv}{dt}$$

The current in the wire leading to a capacitor is proportional to the **slope** of the
voltage across it. Not to the voltage. To the slope.

Two consequences fall straight out, and they are the two facts everybody quotes about
capacitors without usually knowing where they come from. If the voltage is steady, its
slope is zero, so the current is zero — at DC an ideal capacitor is an open circuit,
a break in the wire, and no steady current ever passes through one. And if the voltage
changes quickly, the slope is large and so is the current — a fast enough signal goes
through as though the capacitor were not there. "Blocks DC, passes AC" is not a slogan
to memorise. It is $dv/dt$, read out loud.

## What that derivative does to a sinusoid

Put a sinusoid across it and turn the handle. With $v(t) = V_p\sin(\omega t)$, the slope
of a sine is a cosine scaled by whatever multiplies $t$ inside it:

$$i(t) = C\,\frac{d}{dt}\Big[V_p\sin(\omega t)\Big] = \omega C\,V_p\cos(\omega t)$$

Read three separate facts off that line.

**The frequency has not changed.** A cosine at $\omega$ is still a wave at $\omega$. The
capacitor did not distort the shape or move the frequency; nothing linear ever does.

**The amplitude is $\omega C V_p$.** Bigger capacitor, bigger current. Higher frequency,
bigger current — because the same voltage swing is being achieved in less time, so the
slope is steeper.

**The wave has shifted.** A cosine is a sine that already happened: $\cos\theta =
\sin(\theta + 90^\circ)$. So the current reaches its crest a quarter of a cycle *before*
the voltage reaches its own. The current **leads**.

That last one is worth a second of physical picture rather than a second of trigonometry.
The current into a capacitor is largest when the voltage is climbing fastest, and a
sinusoid climbs fastest as it passes through zero. It is smallest — zero, in fact — at
the crest, where the voltage is momentarily flat. So the current peaks at the instants
the voltage is at zero, and vanishes at the instants the voltage is at its peak. Draw
the two waves on the same axes and the quarter-cycle offset is unmissable.

Because both waves have the same frequency, the ratio of their amplitudes is a single
number, and it has units of volts per amp. That number is the **reactance**:

$$X_C = \frac{V_p}{I_p} = \frac{V_p}{\omega C V_p} = \frac{1}{\omega C}$$

Ohms. Not because a capacitor is a resistor — it dissipates nothing, and the third
reading in this module is about how deep that distinction runs — but because it is the
ratio of a voltage to a current, and every such ratio is measured in ohms.

```
worked example 1
  C = 100 nF          f = 2.00 kHz          v(t) = 5.0 sin(wt) volts

  w   = 2*pi*2000                            = 12566.37 rad/s
  Ip  = w*C*Vp = 12566.37 * 100e-9 * 5.0     = 6.2832e-3 A   = 6.283 mA peak
  Xc  = Vp/Ip  = 5.0 / 6.2832e-3             = 795.77 ohm

  cross-check straight from the formula
  Xc  = 1/(w*C) = 1/(12566.37 * 100e-9)      = 795.77 ohm     agrees
```

Now drop the frequency by a factor of ten, to 200 Hz, and change nothing else. $\omega$
falls to 1256.6 rad/s, so $X_C$ rises to 7957.7 Ω and the peak current falls to
0.6283 mA. Ten times less current for the same voltage. That is the capacitor beginning
to look like the open circuit it becomes at zero frequency, and it is the entire
mechanism behind every filter in this course.

## The inductor is the same sentence with the words swapped

An inductor is a coil of wire, usually round a lump of iron or ferrite. Current through
the coil sets up a magnetic field; the field threading the coil is the **flux linkage**
$\lambda$, and it is proportional to the current that made it, $\lambda = L\,i$, with $L$
in henries. Faraday's law says a changing flux linkage produces a voltage:

$$v = \frac{d\lambda}{dt} = L\,\frac{di}{dt}$$

Compare that with $i = C\,dv/dt$ and you have the whole of the inductor for free, by
swapping the words "voltage" and "current" everywhere. A steady current means zero
$di/dt$ and therefore zero volts: at DC an ideal inductor is a plain wire, which ought
to be reassuring, since that is what it is made of. Drive it with $i(t) = I_p\sin(\omega
t)$ and the voltage is $\omega L\,I_p\cos(\omega t)$ — same frequency, amplitude
$\omega L I_p$, and this time it is the *voltage* that arrives a quarter cycle early. The
current **lags**.

$$X_L = \omega L$$

```
worked example 2
  L = 47 mH           f = 1.00 kHz          i(t) = 30 mA peak

  w   = 2*pi*1000                            = 6283.19 rad/s
  Xl  = w*L = 6283.19 * 0.047                = 295.31 ohm
  Vp  = Ip*Xl = 0.030 * 295.31               = 8.859 V peak

same coil, same current, at 10.0 kHz instead
  Xl  = 6283.19*10 * 0.047                   = 2953.1 ohm
  Vp  = 0.030 * 2953.1                       = 88.59 V peak
```

Ten times the frequency, ten times the voltage needed to push the same current. The
inductor is the mirror of the capacitor at both ends: a wire where the capacitor is a
break, and a break where the capacitor is a wire.

## The two mistakes, and why both are tempting

**Writing $1/(fC)$ instead of $1/(\omega C)$.** This is the most expensive error in the
course and it costs a factor of $2\pi = 6.283$ every time. It is tempting because every
number you are given is in hertz: the front panel of the generator says hertz, the data
sheet says hertz, the specification says hertz. But $\sin$ takes an *angle*, and the
angle advances $2\pi$ radians per cycle, so the formula wants radians per second. A
220 nF capacitor at 3.50 kHz has a reactance of 207 Ω; do it with $f$ and you get
1299 Ω, and every voltage downstream is wrong by six.

**Mixing up which one leads.** Both components shift by a quarter cycle and only the
sign differs, so there is nothing in the shape of the answer to catch you. The
traditional mnemonic is *CIVIL*: in **C**, **I** comes before **V**; in **L**, **V**
comes before **I**. Mnemonics are fragile, so keep a physical anchor beside it: a
capacitor has to be *charged* before it has any voltage on it, so the current has to
happen first. There is no way round that ordering, and it will still be there when you
have forgotten which vowel went where.

## Where this stops being true

Everything above described an *ideal* capacitor and an *ideal* inductor. Real ones agree
over a useful range and then stop.

**A real capacitor eventually becomes an inductor.** Its plates and leads are metal, and
metal has inductance — a few nanohenries for a surface-mount part, tens for one with
wire legs. That inductance is in series with the capacitance, so the two resonate. Take
100 nF with 5 nH of parasitic inductance:

```
f_self = 1/(2*pi*sqrt(L*C)) = 1/(2*pi*sqrt(5e-9 * 100e-9)) = 7.12 MHz
```

Below 7 MHz the part behaves as the formula says and its reactance falls with frequency.
Above it, the reactance *rises* again, because what you now have is a small inductor with
a capacitor in the way. "A capacitor is a short circuit at high frequency" has a ceiling,
and the ceiling is printed on the data sheet as the self-resonant frequency.

**A real inductor is partly a resistor.** It is metres of thin wire, and thin wire has
resistance. Give that 47 mH coil a fairly ordinary 20 Ω of winding resistance and ask
where the two contributions are equal: $\omega L = 20$ gives $f = 20/(2\pi \times 0.047)
= 67.7$ Hz. Below about 68 Hz that component is more resistor than inductor, and the
neat $X_L = \omega L$ picture describes only part of what it does. The repair is the
same in both cases — draw the parasitic element explicitly, as a real component in
series or in parallel, and analyse the network you now have. That is exactly what the
next reading's machinery makes easy.

**Neither formula survives a waveform that is not a sinusoid.** $X_C = 1/(\omega C)$
needs one $\omega$ to put in it. A square wave has no single $\omega$, so it has no
single reactance, and pushing one through a capacitor gives a shape that is not a square
wave at all. The fix is Fourier's: decompose the waveform into sinusoids, treat each at
its own frequency, and add the results back up. Every technique in this course is
secretly a technique for one component of that sum.

**And none of it survives a nonlinear component.** A diode's current is an exponential
function of its voltage, not a proportional one, so there is no ratio to call an
impedance. Everything here assumes a component whose response scales with its drive.
''',
                },
                {
                    "title": "Phasors: the arithmetic that replaces the calculus",
                    "minutes": 14,
                    "body": r'''
The last reading left an awkward situation. Every component now obeys a different kind of
rule: the resistor a proportion, the capacitor a derivative of voltage, the inductor a
derivative of current. Wire three of them into a loop, apply Kirchhoff's voltage law, and
what you have written down is a differential equation. For the very simplest circuit that
is a nuisance. For anything with two loops it is a research project.

This reading gets rid of the calculus entirely. Not by approximating it — by noticing
that at a single frequency there is nothing left for it to do.

## Only two things can happen to a sinusoid

Take a network of resistors, capacitors and inductors, drive it with $V_p\sin(\omega t)$,
and wait for it to settle. Whatever comes out is a sinusoid at exactly $\omega$. It
cannot be anything else: differentiating a sinusoid gives a sinusoid at the same
frequency, integrating one does too, and adding two of them gives a third. Those three
operations are all a linear circuit can perform, so the frequency is untouchable.

Only two things about the wave *can* change: how big it is, and when in its cycle it
happens. Two numbers. And there is already a mathematical object that carries exactly two
numbers and knows how to add and multiply them — a complex number.

So: at one fixed frequency, represent the sinusoid $V_p\sin(\omega t + \phi)$ by the
single complex number of magnitude $V_p$ and angle $\phi$. That is a **phasor**. The
$\omega t$ is not written down, because every phasor in the circuit shares it; think of
the whole diagram spinning at $\omega$, and the phasor as the still photograph you get by
spinning your head at the same rate. The frequency has not been forgotten — it comes back
the moment a component impedance is written, and you cannot mix phasors from two
different frequencies on one diagram.

The immediate payoff is that adding two sinusoids stops being trigonometry.

```
add   3 sin(wt)   and   4 sin(wt + 90 deg)

as phasors      3 + j0        and        0 + j4
sum             3 + j4
magnitude       sqrt(3^2 + 4^2)                    = 5
angle           atan(4/3)                          = 53.13 deg

so the sum is   5 sin(wt + 53.13 deg)
```

That result is not obvious from the waves themselves — two crests of 3 V and 4 V give a
crest of 5 V, not 7 V, because they never happen at the same instant. It is completely
obvious from the picture of two arrows at right angles. Notice also that the answer is
still a sinusoid at $\omega$, exactly as promised.

## Differentiation becomes multiplication

Here is the step that pays for the whole apparatus. Differentiate
$v(t) = V_p\sin(\omega t + \phi)$:

$$\frac{dv}{dt} = \omega V_p\cos(\omega t + \phi) = \omega V_p \sin(\omega t + \phi + 90^\circ)$$

In phasor terms: the magnitude was multiplied by $\omega$, and the angle had $90^\circ$
added. Multiplying a complex number by $j$ leaves its magnitude alone and adds $90^\circ$
to its angle — that is what $j$ *does*, geometrically. So multiplying by $\omega$ and
turning by a quarter cycle is exactly multiplying by $j\omega$:

$$\frac{d}{dt} \;\longrightarrow\; \times\, j\omega$$

Calculus, replaced by one multiplication. Now feed the two component laws through it.

For a capacitor, $i = C\,dv/dt$ becomes $I = j\omega C\,V$ in phasors, so

$$Z_C \equiv \frac{V}{I} = \frac{1}{j\omega C}$$

For an inductor, $v = L\,di/dt$ becomes $V = j\omega L\,I$, so $Z_L = j\omega L$. And for
a resistor nothing changed at all: $Z_R = R$, a real number with no angle, which is
precisely the statement that a resistor shifts nothing.

That ratio of voltage phasor to current phasor is the **impedance**. It is measured in
ohms, and it does the job resistance did in EE101 — with the difference that it is
complex, so it carries the phase shift as well as the size. Its magnitude tells you how
many volts per amp; its angle tells you how far the current is displaced from the voltage.

One piece of housekeeping, because the form with $j$ underneath is awkward to add.
Multiply top and bottom by $j$ and use $j \times j = -1$:

$$\frac{1}{j\omega C} = \frac{j}{j^2\omega C} = \frac{j}{-\omega C} = -\,\frac{j}{\omega C}$$

So a capacitor contributes $-jX_C$ with $X_C = 1/(\omega C)$, and an inductor contributes
$+jX_L$ with $X_L = \omega L$. The minus sign on the capacitor is the quarter cycle
*backwards* from the last reading, in its final notation.

## Series impedances add, and that is the whole method

Kirchhoff's voltage law says the voltages round a loop sum to zero, and it is still true
of phasors, because phasors are what the voltages are. Two components carrying the same
current therefore have $V = (Z_1 + Z_2)I$, so impedances in series add. Exactly as
resistances did — as complex numbers.

```
worked example 1   R = 1.00 k in series with C = 100 nF, across 6.00 V rms at 1.20 kHz

  w    = 2*pi*1200                                = 7539.82 rad/s
  Xc   = 1/(w*C) = 1/(7539.82 * 100e-9)           = 1326.29 ohm
  Z    = 1000 - j1326.29 ohm

  |Z|  = sqrt(1000^2 + 1326.29^2)
       = sqrt(1.0000e6 + 1.7590e6) = sqrt(2.7590e6)   = 1661.04 ohm
  angle= atan(-1326.29/1000)                          = -52.98 deg

  I    = 6.00 / 1661.04                               = 3.6122 mA rms
  V_R  = 3.6122e-3 * 1000                             = 3.6122 V rms
  V_C  = 3.6122e-3 * 1326.29                          = 4.7908 V rms
```

Three things in that block deserve to be looked at rather than skimmed.

The impedance magnitude is 1661 Ω, not $1000 + 1326 = 2326$ Ω. The two oppositions are at
right angles and never reach their maxima together.

The two voltmeter readings are 3.61 V and 4.79 V, which sum to **8.40 V** across a
**6.00 V** source. Nothing is wrong. Add them as phasors and
$\sqrt{3.6122^2 + 4.7908^2} = 6.000$ V exactly, which is Kirchhoff's law being obeyed to
the letter. Meters read magnitudes, and magnitudes are not what the law is about.

The angle is $-53^\circ$, meaning the impedance's angle; the current, being $V/Z$, is
displaced the other way and *leads* the source voltage by $53^\circ$. Converted to time:
the period is $1/1200 = 833.3\ \mu$s, and $53/360$ of that is 123 µs. The current in that
circuit reaches its crest 123 microseconds before the source does.

```
worked example 2   R = 220 in series with L = 22 mH, across 3.00 V rms at 2.00 kHz

  w    = 2*pi*2000                                = 12566.37 rad/s
  Xl   = w*L = 12566.37 * 0.022                   = 276.46 ohm
  Z    = 220 + j276.46 ohm

  |Z|  = sqrt(220^2 + 276.46^2) = sqrt(1.2483e5)  = 353.31 ohm
  angle= atan(276.46/220)                         = +51.49 deg

  I    = 3.00 / 353.31                            = 8.4910 mA rms
  V_R  = 8.4910e-3 * 220                          = 1.8680 V rms
  V_L  = 8.4910e-3 * 276.46                       = 2.3474 V rms

  check   sqrt(1.8680^2 + 2.3474^2) = 3.000 V     back to the source
```

Same arithmetic, opposite sign. The angle is now positive, so the current *lags*, and the
meter readings again overshoot: 1.87 + 2.35 = 4.22 V from a 3.00 V source.

## The mistake, which is always the same mistake

Adding magnitudes. Two 100 Ω oppositions in series give 141 Ω, not 200 Ω; two voltmeter
readings of 8 V and 6 V across a series pair come from a 10 V source, not a 14 V one; and
a capacitor's 1326 Ω does not simply pile on top of a resistor's 1000 Ω.

It is tempting for an honest reason: for two years everything you added was a real
number, and for two years adding the sizes *was* adding the quantities. The habit is not
wrong, it is out of date. The repair is mechanical — never add two impedances or two
voltages without writing both in $a + jb$ form first, add the real parts and the
imaginary parts separately, and take the magnitude at the very end, once, if a magnitude
is what was asked for. Do the whole problem in rectangular form and convert at the exit.

A secondary version of the same error is dropping the minus sign on the capacitor. It
matters as soon as a circuit contains both a capacitor and an inductor: their
contributions have opposite signs and *subtract*, which is the mechanism behind resonance
and behind several results later in this course that look impossible.

## Where phasors stop working

**One frequency at a time.** A phasor has no frequency written on it, so two phasors from
different frequencies cannot be added, compared, or put on the same diagram. If a signal
is a mixture, split it, solve each frequency separately, and add the resulting *waveforms*
in the time domain. That is Fourier analysis, and it is the reason a course that only ever
handles one sinusoid is nevertheless a course about real signals.

**Steady state only.** The phasor answer is what remains after everything transient has
died away. Switch a real RC circuit on and there is an exponential settling term that no
phasor knows anything about; the phasor tells you where the circuit ends up, not how it
got there. Generalising $j\omega$ to a complex $s = \sigma + j\omega$ recovers the missing
exponential — that is the Laplace transform, and $j\omega$ is the special case sitting on
its imaginary axis. Later courses live there.

**Linear, time-invariant components only.** A diode, a saturating transformer core, a
transistor being switched — none of them has an impedance, because none of them has a
fixed ratio of voltage to current. Where the technique is used on such parts, it is used
on a *small-signal* approximation valid near one operating point, and the approximation
has to be re-derived if the operating point moves.

**Circuits small compared with a wavelength.** Everything above assumed a node has one
voltage, the same everywhere along it. A signal travels about 15 cm per nanosecond along
a track on a circuit board — roughly half the speed of light in vacuum, because the
board's dielectric slows it — so at 1 GHz the wavelength is about 15 cm, and a 4 cm track
is a full quarter of it with visibly different voltages at its two ends. At that point a
wire is no longer a wire; it is a transmission line with an impedance of its own. That
has a course to itself.
''',
                },
                {
                    "title": "Reactance is not resistance, and the difference is heat",
                    "minutes": 10,
                    "body": r'''
Reactance is measured in ohms. It appears in Ohm's law in the place where resistance used
to go. It combines with resistance by Pythagoras into a single number that has ohms
written after it. Everything about the notation invites you to treat the two as the same
kind of thing.

They are not the same kind of thing, and the difference is not subtle: one of them gets
hot and the other does not. This reading is about why, and about the one formula that the
confusion produces.

## Instantaneous power, taken seriously

Power is voltage times current, at each instant: $p(t) = v(t)\,i(t)$. Everything follows
from taking that product honestly for each of the two cases.

**In a resistor** the voltage and the current are in phase. With
$v = V_p\sin(\omega t)$ and $i = I_p\sin(\omega t)$,

$$p(t) = V_p I_p \sin^2(\omega t)$$

A square is never negative. Whenever the voltage is negative the current is negative too,
and the product of two negatives is positive, so $p(t)$ is a hump that touches zero twice
per cycle and is otherwise positive. Energy flows one way only: into the resistor, out as
heat. The average of $\sin^2$ over a whole cycle is exactly $\tfrac12$, so the average
power is $V_p I_p/2$, which is $V_{rms}I_{rms}$ — the result module 1 arrived at from the
other direction.

**In a capacitor** the current leads by a quarter cycle, so with
$v = V_p\sin(\omega t)$ the current is $i = I_p\cos(\omega t)$ and

$$p(t) = V_p I_p \sin(\omega t)\cos(\omega t) = \frac{V_p I_p}{2}\sin(2\omega t)$$

That is a sinusoid, at **twice** the frequency, centred on zero. For a quarter of every
cycle the product is positive and the capacitor is drawing energy in; for the next
quarter it is negative and the capacitor is pushing exactly the same energy back out into
the circuit. Averaged over a cycle: zero. Not "small". Not "usually negligible". Exactly
zero, for an ideal capacitor, at any frequency and any amplitude.

The energy is not destroyed and it is not created. It is stored in the electric field
between the plates, $E = \tfrac12 C v^2$, and returned.

```
worked example 1   how much energy is sloshing, and how often

  C = 100 nF, driven at 5.0 V peak, 2.00 kHz     (the capacitor from reading 1)
  Ip = w*C*Vp = 6.2832 mA peak

  peak stored energy      E = 0.5*C*Vp^2 = 0.5*100e-9*25       = 1.25 uJ
  peak instantaneous power  Vp*Ip/2 = 5.0*6.2832e-3/2          = 15.708 mW

  energy moved in one quarter cycle
      integral of (Vp*Ip/2)*sin(2wt) from 0 to T/4
      = (Vp*Ip/2)/w = 0.015708/12566.37                        = 1.25 uJ
```

The two routes agree, as they must: the energy that flows in during a quarter cycle is
the energy the field holds at the crest. That 1.25 µJ goes in and comes back out 4000
times a second — twice per cycle — and the meter measuring average power reads zero
throughout.

## One current, two components, and only one of them gets warm

Go back to the series pair from the last reading: 1.00 kΩ and 100 nF, 6.00 V RMS at
1.20 kHz, carrying 3.6122 mA. There is one loop, so that is the current in *both*
components — identical electrons, identical amps, identical everything. Yet the resistor
turns 13.05 mW into heat and the capacitor turns nothing into anything. Point an infrared
camera at the board and one of the two parts is visible and the other is not. Reactance
and resistance are not two sizes of the same thing; they are two different things that
happen to share a unit.

Push that further by swapping the resistor for an ideal inductor with 1000 Ω of reactance
at this frequency — that is 132.6 mH — so that the *size* of the opposition in the circuit
is unchanged and only its nature has altered.

```
  Z    = j1000 - j1326.29                        = -j326.29 ohm      (they subtract)
  |Z|  = 326.29 ohm
  I    = 6.00/326.29                             = 18.389 mA rms
  V_L  = 18.389e-3 * 1000                        = 18.389 V rms
  V_C  = 18.389e-3 * 1326.29                     = 24.389 V rms

  average power dissipated anywhere in the circuit                   = 0 W
```

Five times the current of the resistive version, two meter readings far larger than the
6 V source, and not one milliwatt consumed anywhere. The minus sign is doing all of the
work: a capacitor's reactance is negative and an inductor's is positive, so the two
subtract instead of combining, and 1326 Ω of one against 1000 Ω of the other leaves only
326 Ω of opposition standing. What the pair is physically doing is passing the same packet
of energy back and forth — out of the capacitor's electric field into the inductor's
magnetic field and back again, 2400 times a second at this frequency, twice per cycle —
while the source merely makes up the mismatch. Module 7 gives that arrangement its name
and its arithmetic. Here it is worth having as proof that current and power have come
apart: you cannot look at an ammeter and infer a single watt.

## The formula this produces, and why it is wrong

Here is the error, which is close to universal on first exposure. The circuit is a
resistor and a capacitor in series; the impedance magnitude is $|Z|$; so surely

$$P = \frac{V^2}{|Z|}\quad\text{— the resistor formula, with } |Z| \text{ in place of } R$$

It has the right units. It reduces correctly when the capacitor is absent. It is wrong,
and here is the size of the error, on the circuit from the previous reading.

```
worked example 2   R = 1.00 k with C = 100 nF in series, 6.00 V rms at 1.20 kHz

  from before      |Z| = 1661.04 ohm      I = 3.6122 mA rms      angle = -52.98 deg

  the wrong answer       V^2/|Z| = 36.0/1661.04                 = 21.673 mW
  the right answer       I^2 * R = (3.6122e-3)^2 * 1000         = 13.048 mW

  what the wrong number actually is
       V * I  =  6.00 * 3.6122e-3                               = 21.673 mVA
```

The wrong formula is off by 40%, and — more interestingly — it is not meaningless. It is
the product of the voltmeter reading and the ammeter reading, and that has a name:
**apparent power**, in volt-amps rather than watts. It is what the wiring, the fuse and
the transformer have to be sized for, because they carry the whole current whatever its
phase. It is simply not what the circuit consumes.

The ratio of the two is the **power factor**, here $13.048/21.673 = 0.602$, which is
$\cos 52.98^\circ$ — the cosine of the impedance angle, exactly. Module 9 takes that
apart properly. For now the working rule is the safe one:

> Average power is dissipated only in resistance. Find the current, square it, multiply
> by the resistance — never by the impedance magnitude.

## Where the ideal stops

Real components dissipate a little, and the amount is specified rather than left to
chance.

A capacitor's loss is quoted as a **dissipation factor** $D$ (or as its reciprocal, $Q$),
and it is modelled by putting a small resistance — the equivalent series resistance, ESR
— in series with the ideal part, with $\mathrm{ESR} = D \times X_C$. Take a decent film
capacitor, $D = 0.001$, and run worked example 1 again with the loss included:

```
  Xc  = 795.77 ohm          ESR = 0.001 * 795.77                = 0.7958 ohm
  Irms = 6.2832 mA / sqrt(2)                                    = 4.4429 mA

  power actually dissipated   Irms^2 * ESR                      = 15.71 uW
  reactive power sloshing     Vrms * Irms = 3.5355 * 4.4429e-3  = 15.71 mVAr
```

Fifteen microwatts against fifteen millivolt-amps: a thousand to one, which is $D$ again,
as it had to be. For that part, at that frequency, "an ideal capacitor dissipates nothing"
is accurate to a tenth of a percent.

It is not always so comfortable. An aluminium electrolytic can have an ESR of 0.1 Ω or
worse, and a switching power supply may push 2 A rms of ripple current through it; then
$I^2R = 4 \times 0.1 = 0.4$ W is being dissipated inside a component with no heatsink and
a liquid electrolyte. Capacitors dying of ESR is one of the most common failure modes in
consumer electronics, and it is this paragraph, not a mystery.

Inductors are worse, because their loss is a plain resistance you can measure with a
meter, plus core losses that rise with frequency. An inductor's $Q = \omega L/R$ is rarely
better than a few hundred and is often below fifty — the ideal-inductor approximation is
useful, but nothing like as good as the ideal-capacitor one.

Finally, the honest limit of the headline claim. "Reactive current is free" is true of the
component and false of everything leading to it. The current that flows in and out of a
capacitor is real current in real copper, and that copper has resistance; a load drawing
its current at a large phase angle makes the supply cables run hot for no delivered power
at all. Utilities charge industrial customers for it. That is module 9, and it begins
precisely where this reading ends.
''',
                },
            ],
            "quiz": {
                "title": "Reactance and impedance",
                "minutes": 9,
                "questions": [
                    {
                        "q": "What is the magnitude of the impedance of a 1 µF capacitor at 1 kHz?",
                        "opts": ["1000 Ω", "159 Ω", "6.28 Ω", "0.159 Ω"],
                        "a": 1,
                        "why": r'''
$|Z_C| = 1/(\omega C) = 1/(2\pi \times 1000 \times 10^{-6}) = 159.2$ Ω. The answer
1000 Ω comes from writing $1/(fC)$ and forgetting that the formula wants angular
frequency: $\omega$, not $f$. That single factor of $2\pi$ is worth a factor of 6.28
in every capacitor calculation you will ever do, so it is worth writing $\omega$
explicitly until it becomes automatic.
''',
                    },
                    {
                        "q": "What does an ideal capacitor look like to a steady, unchanging voltage?",
                        "opts": [
                            "A short circuit — a plain wire",
                            "A resistance equal to $1/C$",
                            "An open circuit — a break in the wire",
                            "It depends on the voltage",
                        ],
                        "a": 2,
                        "why": r'''
At DC the frequency is zero, so $|Z_C| = 1/(\omega C)$ is infinite: an open circuit.
No steady current flows through a capacitor, ever. Notice this is a statement about
current *through* it, not charge stored on it — the plates do charge up, and then the
current stops. The short-circuit answer describes what a capacitor becomes at *high*
frequency, which is the opposite end of the same formula.
''',
                    },
                    {
                        "q": "And what does an ideal inductor look like to a steady, unchanging voltage?",
                        "opts": [
                            "An open circuit",
                            "A short circuit — a plain wire",
                            "A resistance equal to $L$",
                            "A source of voltage",
                        ],
                        "a": 1,
                        "why": r'''
$|Z_L| = \omega L$, and at $\omega = 0$ that is zero: a wire. An inductor is a coil
of wire, so this should be reassuring rather than surprising — with nothing changing,
there is nothing for the magnetic field to oppose. It is the exact mirror of the
capacitor, which is worth holding on to: whatever a capacitor does at one end of the
frequency range, an inductor does at the other.
''',
                    },
                    {
                        "q": "In a capacitor, how does the current relate in time to the voltage across it?",
                        "opts": [
                            "The current lags the voltage by a quarter of a cycle",
                            "The current leads the voltage by a quarter of a cycle",
                            "They peak at the same instant",
                            "The current is always zero",
                        ],
                        "a": 1,
                        "why": r'''
The current into a capacitor is largest when the voltage is changing fastest, which
for a sinusoid is when the voltage is passing through zero — a quarter cycle, or 90°,
*before* the voltage reaches its peak. So the current leads. The lagging answer is
the inductor, and mixing the two up is so common that it has a mnemonic: in a
capacitor, C, the current I leads; in an inductor, L, the current I lags.
''',
                    },
                    {
                        "q": "A 100 Ω resistor is in series with a capacitor whose reactance at this frequency is also 100 Ω. What is the magnitude of the total impedance?",
                        "opts": ["200 Ω", "141 Ω", "100 Ω", "0 Ω"],
                        "a": 1,
                        "why": r'''
Impedances in series add, but as complex numbers: $Z = 100 - j100$, and its magnitude
is $\sqrt{100^2 + 100^2} = 141$ Ω. Adding the magnitudes to get 200 Ω is the standard
error, and it fails because the two contributions are at right angles to one another —
the resistor's voltage and the capacitor's voltage peak a quarter cycle apart, so
they never add up at their full values at the same instant.
''',
                    },
                    {
                        "q": "How much average power does an ideal capacitor dissipate?",
                        "opts": [
                            "None — it stores energy and returns it",
                            "$V_{rms}^2/|Z_C|$, the same as a resistor of that size",
                            "Half of what a resistor of the same magnitude would",
                            "It depends on the frequency",
                        ],
                        "a": 0,
                        "why": r'''
None. Over each cycle an ideal capacitor draws energy in and pushes exactly the same
energy back out, because its current and voltage are a quarter cycle apart: for a
quarter of the time the product is positive, for the next quarter it is negative, and
the average is zero. That is the real distinction between resistance and reactance —
both impede current, but only resistance turns the energy into heat. A real capacitor
has a little loss, and it is modelled by adding a small resistance, never by treating
the reactance as one.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "One component at a time, then both together",
                    "minutes": 8,
                    "lang": "text",
                    "caption": "Three components, one frequency, and the series sum of two of them.",
                    "brief": r'''
Impedance is worth doing slowly once. Pick a frequency, work out what each component is
worth at that frequency, and only then start combining things.

Everything below is at one fixed frequency, 2.00 kHz. Angles are what make this different
from EE101, so keep track of where the $j$ is and what sign it carries.
''',
                    "listing": r'''
at f = 2.00 kHz:      omega  =  ___ rad/s


    R = 470 ohm                 Z_R  =  ___

    C = 220 nF                 |Z_C| =  ___ ohm

    L = 33 mH                  |Z_L| =  ___ ohm


the resistor and the capacitor, in series:

    Z   =  470  ___  ohm

    |Z| =  ___ ohm
''',
                    "blanks": [
                        {
                            "prompt": "The angular frequency",
                            "hole": "omega",
                            "opts": ["2000", "12566", "6283", "0.0005"],
                            "a": 1,
                            "why": r'''
$\omega = 2\pi f = 2\pi \times 2000 = 12566$ rad/s. The 2000 on the front panel counts
cycles; $\omega$ counts radians, and there are $2\pi$ of those per cycle. The value
6283 is $2\pi \times 1000$ — right formula, wrong frequency — and 0.0005 s is the
period $T$, a time rather than a rate.
''',
                        },
                        {
                            "prompt": "The impedance of the resistor",
                            "hole": "zr",
                            "opts": ["470 Ω, with no $j$ in it", "$j470$ Ω", "$-j470$ Ω", "$470/\\omega$ Ω"],
                            "a": 0,
                            "why": r'''
$Z_R = R = 470$ Ω, real, at every frequency. A resistor's current and voltage peak at
the same instant, so there is no quarter-cycle shift to record and therefore no $j$.
This is the reference against which the other two are read: anything with a $j$ in it
shifts the phase, and anything without one does not.
''',
                        },
                        {
                            "prompt": "The magnitude of the capacitor's impedance",
                            "hole": "zc",
                            "opts": ["361.7", "2272", "0.002765", "723.4"],
                            "a": 0,
                            "why": r'''
$|Z_C| = 1/(\omega C) = 1/(12566 \times 220\times10^{-9}) = 361.7$ Ω. The value 2272 Ω
is $1/(fC)$ with the $2\pi$ left out, which overstates the reactance by 6.28 every
time. The small number 0.002765 is $\omega C$ itself — the susceptance in siemens, one
reciprocal short of an answer in ohms.
''',
                        },
                        {
                            "prompt": "The magnitude of the inductor's impedance",
                            "hole": "zl",
                            "opts": ["0.0024", "414.7", "66.0", "4.82"],
                            "a": 1,
                            "why": r'''
$|Z_L| = \omega L = 12566 \times 0.033 = 414.7$ Ω. Multiply, do not divide: the
inductor is the mirror of the capacitor, so where the capacitor has $\omega$ underneath
the inductor has it on top. The value 66.0 Ω is $fL$ with the $2\pi$ left out, and
0.0024 is one over the right answer — which is what putting $\omega L$ underneath, as
though it were a capacitor, would give you.
''',
                        },
                        {
                            "prompt": "The imaginary part of the series pair",
                            "hole": "jpart",
                            "opts": ["$+\\,j361.7$", "$-\\,j361.7$", "$+\\,361.7$", "$-\\,j414.7$"],
                            "a": 1,
                            "why": r'''
$Z = R + 1/(j\omega C) = 470 - j361.7$ Ω. The minus sign is the capacitor's
quarter-cycle written down: $1/j = -j$, so the reactance sits on the negative imaginary
axis. Writing $+j361.7$ describes an inductor of the same reactance instead, and the
difference shows up the moment the circuit contains one of each, because then the two
subtract. Dropping the $j$ altogether — writing $470 + 361.7$ — is the mistake this
whole module exists to prevent.
''',
                        },
                        {
                            "prompt": "The magnitude of the series pair",
                            "hole": "zmag",
                            "opts": ["831.7", "593.1", "108.3", "470"],
                            "a": 1,
                            "why": r'''
$|Z| = \sqrt{470^2 + 361.7^2} = \sqrt{220900 + 130827} = 593.1$ Ω. Adding the two
sizes gives 831.7 Ω and is the standard error; subtracting them gives 108.3 Ω and is
the same error with a sign attached to it. Neither is a legal operation on quantities
a quarter cycle apart. A useful sanity check: the answer must be larger than either
part on its own and smaller than their sum, so anything outside 470 to 832 is wrong
before you look at the arithmetic.
''',
                        },
                    ],
                },
                {
                    "title": "Backwards, from two meter readings to a component value",
                    "minutes": 9,
                    "lang": "text",
                    "caption": "An unknown capacitor identified from a voltmeter and nothing else.",
                    "brief": r'''
Most real measurement runs this way round: you can read voltages easily, currents with
more trouble, and component values not at all. A resistor, an unknown capacitor and two
meter readings are enough to pin the capacitor down exactly.

Work down the listing in order — each line is the input to the next. The one step that
is not EE101 is the first.
''',
                    "listing": r'''
source        5.00 V rms sinusoid at 2.00 kHz
in series     R = 1.50 kohm   and   C = unknown

    voltmeter across R reads             3.00 V rms

    voltmeter across C therefore reads   ___ V rms

    current round the loop               ___ mA rms

    reactance of the capacitor           ___ ohm

    the capacitor                        ___ nF

    the current leads the source by      ___
''',
                    "blanks": [
                        {
                            "prompt": "The voltage across the capacitor",
                            "hole": "vc",
                            "opts": ["2.00", "4.00", "8.00", "5.83"],
                            "a": 1,
                            "why": r'''
$V_C = \sqrt{5.00^2 - 3.00^2} = \sqrt{25 - 9} = 4.00$ V. The resistor's voltage and the
capacitor's voltage are a quarter cycle apart, so the three magnitudes make a right
triangle with the source as the hypotenuse — the 3-4-5 triangle, which turns up
constantly in this course. Subtracting to get 2.00 V assumes the readings add end to
end, and 8.00 V is the same assumption with a plus sign. The interesting wrong answer is
5.83 V, which is $\sqrt{5.00^2 + 3.00^2}$: quadrature, correctly, but with the source
treated as one of the two legs instead of the hypotenuse. The source is the sum of the
other two, so it is always the longest side.
''',
                        },
                        {
                            "prompt": "The current in the loop",
                            "hole": "i",
                            "opts": ["2.00", "3.33", "2.67", "0.500"],
                            "a": 0,
                            "why": r'''
One loop means one current, and the resistor is the component whose law you can use
without knowing anything else: $I = V_R/R = 3.00/1500 = 2.00$ mA rms. Using the source
voltage here instead gives 3.33 mA, which would be the current if the capacitor were
not there — the whole point of the exercise is that it is.
''',
                        },
                        {
                            "prompt": "The reactance of the capacitor",
                            "hole": "xc",
                            "opts": ["2000", "1500", "2500", "1330"],
                            "a": 0,
                            "why": r'''
The same current flows in the capacitor, so $X_C = V_C/I = 4.00/0.00200 = 2000$ Ω.
Reactance is a ratio of a voltage to a current exactly as resistance is; what it does
*not* share with resistance is any claim on the power, which stays entirely in the
1.50 kΩ. The value 2500 Ω is $|Z|$, the whole loop — correct for the pair, not for the
capacitor alone.
''',
                        },
                        {
                            "prompt": "The capacitance",
                            "hole": "cap",
                            "opts": ["39.8", "6.33", "250", "125"],
                            "a": 0,
                            "why": r'''
$X_C = 1/(\omega C)$ rearranges to $C = 1/(\omega X_C) = 1/(12566 \times 2000) =
3.98\times10^{-8}$ F, which is 39.8 nF. The nearest standard part is 39 nF, and a
measurement this crude would not tell it from 40. All three wrong answers are the same
error in different doses: 250 nF is $1/(f X_C)$ with the $2\pi$ left out entirely,
125 nF is $1/(2 f X_C)$ with only the $\pi$ dropped, and 6.33 nF is
$1/(2\pi\,\omega X_C)$ — the $2\pi$ applied once more than it should be, on a value of
$\omega$ that already contains it.
''',
                        },
                        {
                            "prompt": "The phase of the current relative to the source",
                            "hole": "phi",
                            "opts": ["36.9°", "53.1°", "90°", "45°"],
                            "a": 1,
                            "why": r'''
The impedance is $1500 - j2000$, whose angle is $-\arctan(2000/1500) = -53.1^\circ$, so
the current leads the source voltage by $53.1^\circ$. The complementary angle
$36.9^\circ$ is the one you get by putting the triangle's sides the other way up —
$\arctan(R/X_C)$ — and it is the angle between the current and the *capacitor's*
voltage, not the source's. A quick check that does not need a calculator: $X_C$ is
larger than $R$, so the capacitor dominates, so the angle must be past halfway to the
$90^\circ$ of a pure capacitor. Anything under $45^\circ$ is therefore wrong.
''',
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "One component, one frequency",
                    "minutes": 4,
                    "brief": r'''
The mechanical one, to get the formula under your fingers before anything is built on top
of it. A single capacitor, a single frequency, and one substitution.

There is exactly one trap, and it is a factor of 6.28.
''',
                    "prompt": "What is the magnitude of this capacitor's impedance at 3.50 kHz?",
                    "note": "Give the answer in ohms, to four significant figures.",
                    "figure": r'''
A 220 nF capacitor, on its own, with a signal generator set to a 3.50 kHz sinusoid
connected across it. Nothing else is in the circuit.
''',
                    "given": [
                        {"label": "Capacitance", "value": "220 nF"},
                        {"label": "Frequency", "value": "3.50 kHz"},
                    ],
                    "aside": "The amplitude of the generator is deliberately not given, because the "
                             "answer does not depend on it. Impedance is a ratio, and the ratio is the "
                             "same at 1 mV as at 100 V.",
                    "answer": 206.7,
                    "tol": 1.0,
                    "unit": "Ω",
                    "hint": "$|Z_C| = 1/(\\omega C)$, and $\\omega = 2\\pi f$. Do the $2\\pi$ first, as a "
                            "separate step, and write the units down.",
                    "wrong": "1299 Ω is $1/(fC)$ — the $2\\pi$ was left out, which is the single most "
                             "common error in this course. 0.004838 is $\\omega C$, the susceptance in "
                             "siemens, one reciprocal short of an answer in ohms.",
                    "why": r'''
$\omega = 2\pi \times 3500 = 21991$ rad/s, and

```
|Zc| = 1/(w*C) = 1/(21991 * 220e-9) = 1/(4.8381e-3) = 206.7 ohm
```

Two sanity checks are worth building into the habit. The first is the direction: 220 nF
is a fairly large capacitor and 3.5 kHz is a fairly high frequency, so a couple of
hundred ohms is a reasonable size — anything in the megohms would mean a mistake of
several decades. The second is the scaling: halve the frequency and the answer must
double, because $\omega$ is underneath. At 1.75 kHz this capacitor is 413.4 Ω, and at
7 kHz it is 103.3 Ω.
''',
                },
                {
                    "title": "Two components that do not add up",
                    "minutes": 6,
                    "brief": r'''
A resistor and a capacitor in series, and the question is what the source sees. One
number, but not the one the arithmetic of EE101 would give you.

Work out the capacitor's reactance at the stated frequency first, then combine. The
combining step is the whole exercise.
''',
                    "prompt": "What is the magnitude of the total impedance the source sees at 1.50 kHz?",
                    "note": "Give the answer in ohms, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 8},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 2200},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 9, "y": 4, "rot": 1, "value": 4.7e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "8.00 V RMS, 1.50 kHz"},
                        {"label": "Resistor", "value": "2.20 kΩ"},
                        {"label": "Capacitor", "value": "47 nF"},
                    ],
                    "aside": "The two components carry the same current, because there is only one loop. "
                             "That is what lets their impedances be added at all — and the addition is "
                             "the complex one.",
                    "answer": 3152.0,
                    "tol": 15.0,
                    "unit": "Ω",
                    # Nothing is restated from the drawing. The probe sits across the capacitor, so
                    # the solved node voltage and the capacitor's own value give the loop current,
                    # and the source value divided by that current is the impedance asked for.
                    "check": r'''
var f = 1500, w = 2 * Math.PI * f;
c.assert(c.count('R') === 1 && c.count('C') === 1, "one resistor and one capacitor in series");
var C = c.values('C')[0], vs = c.values('V')[0];
var i = c.gain(f) * w * C;
return vs / i;
''',
                    "hint": "$X_C = 1/(\\omega C)$ gives one number and the resistor gives another. They "
                            "do not add; they combine by Pythagoras, because they are a quarter cycle "
                            "apart.",
                    "wrong": "4458 Ω is $2200 + 2258$, the two sizes added end to end, which is the "
                             "EE101 reflex. 14350 Ω is the whole calculation done correctly but with "
                             "$1/(fC)$ in place of $1/(\\omega C)$. 2258 Ω is the capacitor alone.",
                    "why": r'''
```
w    = 2*pi*1500                          = 9424.8 rad/s
Xc   = 1/(w*C) = 1/(9424.8 * 47e-9)       = 2257.5 ohm
Z    = 2200 - j2257.5 ohm
|Z|  = sqrt(2200^2 + 2257.5^2)
     = sqrt(4.8400e6 + 5.0963e6)          = 3152 ohm
```

The two contributions here are almost equal — 2200 Ω and 2258 Ω — which makes this the
clearest possible case for why the magnitudes cannot be added. Adding them gives 4458 Ω;
the truth is 3152 Ω, which is about $\sqrt2$ times either one on its own. Two equal
oppositions a quarter cycle apart never sum to twice one of them; they sum to 1.414 times
it, because that is the diagonal of a square.

The rest of the circuit follows once you have that number, and it is worth an extra
minute. The current is $8.00/3152 = 2.538$ mA RMS, so the resistor has
$2.538\ \text{mA} \times 2200 = 5.583$ V across it and the capacitor has
$2.538\ \text{mA} \times 2257.5 = 5.729$ V. Those two sum to 11.31 V on a pair of
meters, from an 8.00 V source; as phasors,
$\sqrt{5.583^2 + 5.729^2} = 8.00$ V, and Kirchhoff sleeps soundly.
''',
                },
                {
                    "title": "The reading that is larger than the source",
                    "minutes": 8,
                    "brief": r'''
An inductor this time, and the question asks for a voltage rather than an impedance, so
there is a division in the middle: find the current first, then use it.

Look at the answer when you have it, and then at the source voltage.
''',
                    "prompt": "What does an RMS voltmeter connected across the inductor read?",
                    "note": "Give the answer in volts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 470},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "l1", "kind": "L", "x": 9, "y": 4, "rot": 1, "value": 0.1},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "10.0 V RMS, 1.00 kHz"},
                        {"label": "Resistor", "value": "470 Ω"},
                        {"label": "Inductor", "value": "100 mH, ideal"},
                    ],
                    "aside": "The probe sits between the two components, and the inductor runs from there "
                             "to ground, so the probed voltage is the inductor's voltage. Everything in "
                             "the circuit is RMS, so the answer comes out RMS with no conversion.",
                    "answer": 8.008,
                    "tol": 0.05,
                    "unit": "V",
                    # The whole answer comes off the solve: the node the probe marks is the inductor's
                    # own voltage, so re-valuing any component moves this number rather than leaving
                    # it agreeing with a stale one. The assert re-derives the source from the measured
                    # inductor voltage, which fails loudly if the topology is edited.
                    "check": r'''
var f = 1000, w = 2 * Math.PI * f;
var R = c.values('R')[0], L = c.values('L')[0], vs = c.values('V')[0];
var vl = c.gain(f);
var i = vl / (w * L);
c.close(Math.sqrt(Math.pow(i * R, 2) + vl * vl), vs, 0.01,
  "the resistor and inductor voltages should recombine to the source in quadrature");
return vl;
''',
                    "hint": "$X_L = \\omega L$, then $|Z| = \\sqrt{R^2 + X_L^2}$ gives the current, then "
                            "the inductor's own voltage is that current times $X_L$.",
                    "wrong": "10.0 V is the source copied out unchanged. 5.99 V is the voltage across the "
                             "*resistor*. 2.08 V comes from writing $X_L = fL$ and leaving out the "
                             "$2\\pi$, which shrinks the inductor's reactance by 6.28 and hands almost "
                             "all of the source to the resistor.",
                    "why": r'''
```
w    = 2*pi*1000                             = 6283.2 rad/s
Xl   = w*L = 6283.2 * 0.100                  = 628.32 ohm
|Z|  = sqrt(470^2 + 628.32^2)
     = sqrt(2.2090e5 + 3.9478e5)             = 784.66 ohm
I    = 10.0/784.66                           = 12.744 mA rms
V_L  = 12.744e-3 * 628.32                    = 8.008 V rms
```

Now the part worth stopping for. The resistor's voltage is
$12.744\ \text{mA} \times 470 = 5.990$ V, so the two meters read 8.008 V and 5.990 V —
which come to 14.0 V between them, from a 10.0 V source. Nothing has gone wrong and
nothing is being created. The two voltages peak a quarter of a cycle apart, so at the
instant the inductor is at 8.0 V the resistor is at 0 V and vice versa; the phasor sum is
$\sqrt{8.008^2 + 5.990^2} = 10.00$ V, exactly the source, which is Kirchhoff's voltage law
holding to four figures.

There is a practical warning in that. A meter reading larger than the supply is normal in
an AC circuit and is not evidence of a fault — but the insulation, and the voltage rating
of the part, has to survive the reading rather than the supply. Module 7 pushes this much
further: with an inductor and a capacitor together the individual voltages can exceed the
source by a factor of fifty.
''',
                },
                {
                    "title": "Driven by a current instead",
                    "minutes": 11,
                    "brief": r'''
The hardest one in this module, and nothing in it is new — it is four separate steps, each
of which you have already done once, with no step signposted.

Two things are different from the questions above. The source sets the *current* rather
than the voltage, so the impedance is a multiplier rather than a divisor. And the source
is quoted as a peak while the answer is wanted as an RMS value, so module 1 has one last
thing to contribute.
''',
                    "prompt": "What is the RMS voltage across the resistor and capacitor together — that is, at the probe?",
                    "note": "Give the answer in volts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "is", "kind": "I", "x": 3, "y": 5, "rot": 1, "value": 0.003},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "out", "kind": "OUT", "x": 4, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 1200},
                            {"id": "c1", "kind": "C", "x": 9, "y": 4, "rot": 1, "value": 3.3e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "3.00 mA peak, 2.50 kHz"},
                        {"label": "Resistor", "value": "1.20 kΩ"},
                        {"label": "Capacitor", "value": "33 nF"},
                    ],
                    "aside": "A current source pushes the same current whatever is in its way, so there is "
                             "no division to do at the start: the current is given, and the impedance "
                             "turns it into a voltage.",
                    "answer": 4.819,
                    "tol": 0.03,
                    "unit": "V",
                    # Everything is measured: the solver is driven by the current source drawn on the
                    # schematic, and the probe sits on the node above the pair, so the AC magnitude
                    # there is the peak voltage across the combination. Only the peak-to-RMS step
                    # comes from the prompt.
                    "check": r'''
var f = 2500;
c.assert(c.count('I') === 1 && c.count('V') === 0, "a current source drives this one, not a voltage source");
return c.gain(f) / Math.SQRT2;
''',
                    "hint": "Reactance, then Pythagoras, then Ohm's law the other way round — a current "
                            "times an impedance is a voltage — and only then the $\\sqrt2$.",
                    "wrong": "6.82 V is the peak voltage across the pair — correct as far as it goes, "
                             "with the final conversion missing. 2.55 V is the RMS voltage across the "
                             "resistor alone, with the capacitor's 1929 Ω dropped. 6.64 V has the two "
                             "oppositions added end to end instead of in quadrature.",
                    "why": r'''
```
w     = 2*pi*2500                            = 15708 rad/s
Xc    = 1/(w*C) = 1/(15708 * 33e-9)          = 1929.2 ohm
|Z|   = sqrt(1200^2 + 1929.2^2)
      = sqrt(1.4400e6 + 3.7218e6)            = 2271.9 ohm
V_pk  = I_pk * |Z| = 3.00e-3 * 2271.9        = 6.8158 V peak
V_rms = 6.8158/sqrt(2)                       = 4.819 V rms
```

Three details are worth naming, because each of them is a place people lose the question
rather than the arithmetic.

The impedance multiplies here rather than divides. With a voltage source you divide by
$|Z|$ to get a current; with a current source you multiply by it to get a voltage. Same
law, read in the other direction.

The peak-to-RMS conversion belongs at the very end, applied once, to the single quantity
that was asked for. Converting the source to RMS at the start gives the same answer on
this question, and will not on one that asks about power — do the circuit in one system
and convert at the exit.

And the capacitor is carrying more of the voltage than the resistor is: 1929 Ω against
1200 Ω, so 5.79 V peak across the capacitor and 3.60 V peak across the resistor. Yet the
total is 6.82 V peak, not 9.39 V. If that still looks wrong, it is the same right triangle
as everywhere else in this module, and it is worth drawing until it does not.
''',
                },
            ],
            "build": {
                "title": "A capacitor that blocks DC and passes AC",
                "minutes": 22,
                "brief": r'''
The claim from the concepts, drawn and measured.

You are given a source, a ground, a load resistor and a probe, wired straight
through — whatever the source does, the probe sees. Break that connection with a
capacitor so that the circuit becomes a **coupling network**: a steady voltage is
stopped completely, and a fast enough signal gets through untouched.

The circuit must do three things.

1. **Nothing at DC.** With the source held at a steady voltage, the probe reads zero.
2. **Everything well above 1 kHz.** At 500 kHz the probe reads the full source
   amplitude.
3. **Exactly 70.7% at 1 kHz.** That is the corner: the frequency where the capacitor's
   reactance equals the resistance, and the output has fallen to $1/\sqrt{2}$ of the
   amplitude it has in the pass band.

Point 3 fixes the *product* of the resistance and the capacitance, not either one on
its own: $f_c = 1/(2\pi R C)$. Any pair with the right product passes, so choose a
resistance you like and work out the capacitance, or the other way round.

The source value is used both as its steady level and as its amplitude when the
checks sweep frequency, so the exact number you give it does not matter — every check
compares the output against the source rather than against a fixed voltage.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [9, 3]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "C", "x": 7, "y": 3, "rot": 0, "value": 1.6e-7},
                        {"id": "p3", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [6, 3]},
                        {"a": [8, 3], "b": [9, 3]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "checks": [
                    {"name": "no steady voltage reaches the output", "code": r'''
c.assert(Math.abs(c.vout()) < 1e-6,
  "at DC the probe reads " + c.fmt(c.vout(), "V") +
  " — a steady voltage is still getting through, so nothing is blocking it");
'''},
                    {"name": "the full amplitude gets through at 500 kHz", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(c.gain(500000), vs, 0.02,
  "far above the corner the capacitor's reactance is negligible and the output should equal the source");
'''},
                    {"name": "the output is 70.7% of the source at 1 kHz", "code": r'''
var vs = Math.abs(c.values("V")[0]);
c.close(c.gain(1000) / vs, 0.70711, 0.03,
  "1 kHz is meant to be the corner, where the reactance equals the resistance");
'''},
                    {"name": "the output leads the input by 90 degrees far below the corner", "code": r'''
var d = c.phase(10) - c.phase(500000);
while (d > 180) d -= 360;
while (d < -180) d += 360;
c.close(Math.abs(d), 90, 0.03,
  "two decades below the corner the capacitor dominates, and its current leads its voltage by a quarter cycle");
'''},
                ],
                "hints": [
                    "The capacitor goes in series, between the source and the output node — it has to be the only path the signal can take. A capacitor to ground would do the opposite job.",
                    "Delete the long wire between the source and the probe, then place the capacitor in the gap and wire both of its pins.",
                    "$f_c = 1/(2\\pi R C)$, so with the 1 kΩ resistor already there you need $C = 1/(2\\pi \\times 1000 \\times 1000) = 159$ nF. 160 nF is within the tolerance.",
                    "Click a part to edit its value. Values accept engineering suffixes, so 160n is 160 nF.",
                ],
            },
            "derive": {
                "title": "From a quarter-cycle shift to an impedance in ohms",
                "minutes": 13,
                "vars": ["R", "C", "omega", "V_p", "I_p", "j"],
                "brief": r'''
Five steps take the capacitor from the derivative it obeys to a number you can put in
Ohm's law, and then combine it with a resistor.

The first step is handed to you: differentiating $v(t) = V_p\sin(\omega t)$ and
multiplying by $C$ gives the current $i(t) = \omega C\,V_p\cos(\omega t)$. Everything
after that is algebra.

Write $j$ for the square root of $-1$ and leave it as a symbol. Nothing below needs you
to square it.
''',
                "steps": [
                    {
                        "prompt": "Read the peak current $I_p$ off that expression, in terms of $V_p$, $\\omega$ and $C$.",
                        "given": "$i(t) = \\omega C\\,V_p\\cos(\\omega t)$, and $\\cos$ swings between $-1$ and $+1$.",
                        "answer": "\\omega C V_p",
                        "placeholder": "\\omega \\ldots",
                        "hint": "A cosine reaches 1 once per cycle, so the peak of the whole expression is whatever multiplies the cosine.",
                        "deconstruct": [
                            "The amplitude of $A\\cos(\\omega t)$ is $A$.",
                            "Here $A$ is everything in front of the cosine: $\\omega$, $C$ and $V_p$ multiplied together.",
                        ],
                    },
                    {
                        "prompt": "The reactance $X_C$ is the ratio of peak voltage to peak current. Write it in terms of $\\omega$ and $C$ alone.",
                        "answer": "\\frac{1}{\\omega C}",
                        "hint": "Divide $V_p$ by what you just wrote. The $V_p$ cancels, which is why the answer is a property of the component and not of the signal.",
                        "deconstruct": [
                            "$X_C = V_p / I_p = V_p / (\\omega C V_p)$.",
                            "The $V_p$ on the top and the bottom cancel.",
                        ],
                    },
                    {
                        "prompt": "A resistor $R$ is in series with the capacitor. Impedances in series add, and the capacitor contributes $-jX_C$. Write the total impedance $Z$ in terms of $R$, $\\omega$, $C$ and $j$.",
                        "given": "The minus sign records the quarter cycle: the capacitor's current arrives *before* its voltage.",
                        "answer": "R - \\frac{j}{\\omega C}",
                        "placeholder": "R - \\ldots",
                        "hint": "Substitute the reactance you found into $Z = R - jX_C$. Nothing has to be multiplied out.",
                        "deconstruct": [
                            "$Z = Z_R + Z_C$ because the two carry the same current.",
                            "$Z_R = R$, and $Z_C = -jX_C$ with $X_C$ from the previous step.",
                        ],
                    },
                    {
                        "prompt": "Write the magnitude $|Z|$ in terms of $R$, $\\omega$ and $C$, with no $j$ in it.",
                        "given": "The magnitude of $a + jb$ is $\\sqrt{a^2 + b^2}$.",
                        "answer": "\\sqrt{R^2 + \\frac{1}{\\omega^2 C^2}}",
                        "placeholder": "\\sqrt{R^2 + \\ldots}",
                        "hint": "The real part is $R$ and the imaginary part is $-1/(\\omega C)$. Squaring kills the sign.",
                        "deconstruct": [
                            "$a = R$, so $a^2 = R^2$.",
                            "$b = -1/(\\omega C)$, so $b^2 = 1/(\\omega^2 C^2)$ — the minus disappears when squared.",
                        ],
                    },
                    {
                        "prompt": "At one particular angular frequency the two contributions are the same size. Solve $1/(\\omega C) = R$ for that $\\omega$.",
                        "answer": "\\frac{1}{R C}",
                        "hint": "Multiply both sides by $\\omega$, then divide by $R$.",
                        "deconstruct": [
                            "$1/(\\omega C) = R$ gives $1 = \\omega C R$.",
                            "Divide both sides by $RC$.",
                        ],
                    },
                ],
                "closing": r'''
Two results, and they are the two the rest of the course leans on.

The magnitude $|Z| = \sqrt{R^2 + 1/(\omega^2C^2)}$ is a resistance that depends on
frequency: enormous as $\omega \to 0$, and settling down to plain $R$ as $\omega$ grows,
because the reactance term shrinks away and leaves the resistor holding everything.

And $\omega = 1/(RC)$ is the frequency at which the two halves are equal — the hinge
between those two behaviours. Divide by $2\pi$ and it is $f_c = 1/(2\pi RC)$, the
**corner frequency**, which module 4 spends its whole length on. Notice that it dropped
out of an impedance calculation with no filter mentioned anywhere: the corner is not an
extra fact about RC circuits, it is the point where the two terms in this square root
change places.
''',
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Impedances in series and in parallel",
            "summary": "Kirchhoff's two laws survive the move to alternating current unchanged — provided what you add is phasors and not magnitudes.",
            "concepts": [
                "Both laws from EE101 hold for phasors exactly as written: the phasor voltages round a loop sum to zero, and the phasor currents into a node sum to zero. What does **not** survive is the same sentence with the word *magnitudes* in it — two voltages a quarter cycle apart never reach their peaks together, so their sizes do not add.",
                "Impedances in series add as complex numbers: $Z = Z_1 + Z_2$. A 300 Ω resistor in series with 400 Ω of reactance is $\\sqrt{300^2 + 400^2} = 500$ Ω, and a 10 V source across the pair puts 6 V on one and 8 V on the other — which sum to 14 V on the meter and to exactly 10 V as phasors.",
                "In parallel it is easier to work with **admittance** $Y = 1/Z$, in siemens, because admittances in parallel simply add. $Y = G + jB$ splits into a **conductance** $G$ and a **susceptance** $B$ the same way $Z$ splits into resistance and reactance, and $B$ is positive for a capacitor ($B = \\omega C$) and negative for an inductor.",
                "A resistor and a capacitor in parallel come to $Z = \\dfrac{R}{1 + j\\omega R C}$: magnitude $R$ at low frequency, falling towards zero at high frequency, bending at $f = 1/(2\\pi R C)$.",
                "Put that pair in the bottom leg of a divider and the corner is not where you would guess. The response is $\\dfrac{R_2}{R_1+R_2}\\cdot\\dfrac{1}{1 + j\\omega (R_1 \\parallel R_2) C}$ — the capacitor is charged through **both** resistors at once, so the corner is set by $R_1 \\parallel R_2$ and never by $R_2$ alone. Whatever drives a node is part of that node's time constant.",
            ],
            "read": [
                {
                    "title": "Two laws that survive, and one habit that does not",
                    "minutes": 16,
                    "body": r'''
A 5.00 V RMS generator at 1.20 kHz drives a single loop: a 220 Ω resistor, a 47 mH
inductor and a 330 nF capacitor, one after another and back to the generator. Put an
RMS voltmeter across each component in turn and it reads 4.89 V, then 7.87 V, then
8.93 V. Those three numbers come to 21.7 V between them.

The supply is five volts. There are three passive components in the loop and nothing
anywhere in it that could amplify. So either one of the meters is lying, or Kirchhoff's
voltage law has stopped working, or the word *add* has quietly been used for an
operation that is not addition.

It is the third one, and unpicking it is most of this module.

## The laws themselves do not budge

Both of Kirchhoff's laws are conservation statements, and neither of them mentions
sinusoids, frequency or time.

**The current law** says the currents flowing into any node sum to zero. That is
conservation of charge plus a definition: a junction of wires has no volume to store
charge in, so whatever arrives in a given instant leaves in the same instant.

**The voltage law** says the voltages around any closed loop sum to zero. That is the
statement that "the potential here" is a single number. Walk round a loop adding rises
and subtracting drops and you must arrive back at the value you started with, or the
starting point would have two different potentials at once.

Neither claim has any room in it for a frequency, and neither is weakened by anything
in this course. Both hold **at every instant**, including in the loop above. At the
moment the generator happens to be at $+3.14$ V, the three component voltages at that
same moment are three numbers that sum to $+3.14$ V. Ten microseconds later they are
three different numbers summing to whatever the generator is doing then. Nothing is
broken and nothing needs repairing.

What the meters report is not any of those instants. A meter reports the RMS value: one
number distilled from a whole cycle, constructed in module 1 to be deliberately blind to
*when* in the cycle anything happened. Three waves can each be 8 V big and never once be
big at the same moment. Their sizes are simply not the kind of thing that adds.

The everyday version: walk 3 km east, then 4 km north. You have walked 7 km and you are
5 km from where you started. Nobody finds that paradoxical, because everyone knows
distance walked and displacement are different quantities and only one of them is a
straight sum. A voltmeter measures something much closer to distance walked. Kirchhoff's
law is about the displacement.

## Adding at an angle

Module 1 supplied the picture that makes the right operation obvious. A sinusoid at a
fixed frequency is the height of a point going round a circle at a steady rate: the
radius is the amplitude, and where the point sits when you start the clock is the phase.
If two sinusoids have **the same frequency** their two points go round together, locked,
so the angle between them never changes. The pair can therefore be drawn as two arrows
frozen in place, and the sum of the two waves is the arrow you get by laying them tip to
tail.

That frozen arrow is the **phasor**, and Kirchhoff's laws restated for phasors are:

- the phasor voltages round a loop sum to zero;
- the phasor currents into a node sum to zero.

Both are exactly as true as the instantaneous versions, because a phasor sum *is* the
instantaneous sum — carried out once, for every instant at once. Only the word "sum" has
been repaired. It now means adding arrows, and arrows at an angle do not add like
lengths.

## Why impedances in series add

The series rule is worth deriving rather than remembering, because the derivation states
its own conditions.

Take two components in a loop carrying the same phasor current $I$. They do carry the
same current: there is no junction between them, so there is nowhere else for charge to
go. Each obeys its own version of Ohm's law,

$$V_1 = Z_1 I \qquad\text{and}\qquad V_2 = Z_2 I$$

and Kirchhoff's voltage law for phasors gives the source voltage as $V = V_1 + V_2$, so

$$V = Z_1 I + Z_2 I = (Z_1 + Z_2)\,I .$$

The source cannot tell the pair from a single impedance $Z = Z_1 + Z_2$. Three
ingredients went into that: one shared current, a linear law for each part, and a single
frequency so the arrows keep their relative angles. Remove any one of them and the rule
goes with it.

Notice what the derivation does not say. It says the *complex numbers* add. It says
nothing whatever about their magnitudes, and $|Z_1 + Z_2|$ equals $|Z_1| + |Z_2|$ only
in the special case where both point the same way.

## Worked example: a resistor and an inductor

1.50 kΩ in series with 120 mH, driven by 12.0 V RMS at 2.00 kHz.

```
w   = 2*pi*2000                          = 12566 rad/s
X_L = w*L = 12566 * 0.120                = 1508.0 ohm
Z   = 1500 + j1508.0 ohm
|Z| = sqrt(1500^2 + 1508.0^2)
    = sqrt(2.2500e6 + 2.2740e6)          = 2127.0 ohm
ang = atan(1508.0/1500)                  = 45.15 degrees
I   = 12.0/2127.0                        = 5.6419 mA rms
V_R = 5.6419e-3 * 1500                   = 8.4628 V rms
V_L = 5.6419e-3 * 1508.0                 = 8.5077 V rms
```

The two meter readings come to 16.97 V from a 12.0 V generator. As phasors,
$\sqrt{8.4628^2 + 8.5077^2} = 12.000$ V, which is the source to five figures. The two
components are almost exactly matched in size here, and that is why the naive sum
overshoots so badly: two equal oppositions a quarter cycle apart combine to $\sqrt2$
times one of them, never to twice one of them. $\sqrt2$ is the diagonal of a square, and
this is the square.

The angle deserves a moment as well. 45.15° says the loop current lags the source
voltage by just over an eighth of a cycle, which at 2.00 kHz is 63 µs. That number is
invisible to every meter in the drawer, and it is the entire reason the magnitudes did
not add.

## Worked example: three in series, two of them fighting

Same method, one more component, and now a sign carries weight. 220 Ω, 47 mH and 330 nF
in series across 5.00 V RMS at 1.20 kHz — the circuit whose meters opened this page.

```
w    = 2*pi*1200                         = 7539.8 rad/s
X_L  = w*L = 7539.8 * 0.047              = 354.37 ohm
X_C  = 1/(w*C) = 1/(7539.8 * 330e-9)     = 401.91 ohm
Z    = 220 + j354.37 - j401.91
     = 220 - j47.535 ohm
|Z|  = sqrt(220^2 + 47.535^2)
     = sqrt(48400 + 2259.6)              = 225.08 ohm
I    = 5.00/225.08                       = 22.215 mA rms
V_R  = 22.215e-3 * 220                   = 4.8872 V rms
V_L  = 22.215e-3 * 354.37                = 7.8722 V rms
V_C  = 22.215e-3 * 401.91                = 8.9282 V rms
```

There are the three readings. The inductor and the capacitor are each carrying more
voltage than the supply, and between them they account for 16.80 V of the 21.69 V the
meters total.

Now do the sum properly. The inductor's voltage points at $+90°$ and the capacitor's at
$-90°$, so they are 180° apart and in the sum they *subtract*, leaving
$|V_L - V_C| = 1.056$ V. That small remainder is at right angles to the resistor's
4.887 V, and

$$\sqrt{4.887^2 + 1.056^2} = 5.000\ \text{V},$$

which is the supply exactly. Kirchhoff never wobbled. The 8.93 V and the 7.87 V are both
real and both present at the same time; when the capacitor's voltage is at its most
negative the inductor's is near its most positive, and the generator is only ever asked
for what is left over after they have cancelled.

There is a practical consequence in that, not just a curiosity. The capacitor in this
loop must be rated for 8.93 V RMS although the supply is 5.00 V — 79% more than the
number on the front of the generator. Choosing parts by the supply voltage is how that
capacitor fails. Module 7 makes the effect far larger on purpose.

## The mistake, and why it keeps happening

The error is adding the magnitudes: $220 + 354 + 402 = 976$ Ω where the truth is 225 Ω,
wrong by more than a factor of four. It is not carelessness. Three separate things make
it attractive.

**Every circuit you have met so far behaved that way.** In EE101 series resistances do
genuinely add as sizes, because every resistor's arrow points along the same axis and
there is no angle between any two of them. The rule you learned was the special case of
a more general one, and nothing in the special case announced that it was special.

**The instrument hides the evidence.** A voltmeter shows 8.93 V and no angle at all. Two
readings look like two plain numbers, and two plain numbers invite arithmetic.

**The English is genuinely ambiguous.** "Impedances add in series" is a true sentence. It
is a claim about complex numbers, and reading "add" as an instruction to your calculator
turns it into a different claim that happens to be false.

One near miss is worth naming too, because it looks sophisticated: writing
$|Z| = \sqrt{R^2 + X_L^2 + X_C^2}$. On the circuit above that gives 579.2 Ω, against a
true 225.1 Ω. The shape is right and the answer is wrong, because it treats $X_L$ and
$X_C$ as two independent directions when they are one direction with two signs. Combine
the reactances first, signs included, and only then reach for Pythagoras. One square root
per circuit, taken at the end.

## Where this stops working

Phasor addition is not general arithmetic. It rests on assumptions, and each assumption
names a place where it fails.

**One frequency at a time.** Two arrows can only be frozen relative to one another if
their points go round at the same rate. Put a 50 Hz component and a 1 kHz component in
the same loop and there is no fixed angle between them; the phasor sum means nothing.
The repair is superposition — solve the circuit once per frequency and add the resulting
*waveforms* — and it comes with a pleasant surprise. Sinusoids at different frequencies
are orthogonal over a long window, so their RMS values combine in quadrature,
$V_{rms} = \sqrt{V_{1,rms}^2 + V_{2,rms}^2}$, whatever their phases happen to be.
Quadrature again, arrived at for a completely different reason.

**Linear components only.** $V = ZI$ is an assumption, not a law of nature. A diode, a
transistor, an iron-cored inductor driven into saturation: none of these has an impedance
at all, because none of them scales its response in proportion to the drive. Feed a
sinusoid in and what comes out is not a sinusoid, so there is nothing to draw an arrow
for.

**Ideal components only.** The 120 mH inductor above is a few hundred turns of copper,
and copper has resistance — say 12 Ω of it. Series is exactly the right way to account
for that, which is the useful half of the news: the winding resistance simply joins the
1500 Ω, giving $Z = 1512 + j1508$ and $|Z| = 2135.4$ Ω instead of 2127.0 Ω. The unhelpful
half is that no schematic shows it, so a measurement 0.4% off the calculation is not
necessarily a measurement error.

**Nothing magnetically coupled.** Two inductors sharing a magnetic field are not two
independent impedances in series. The current in one induces a voltage in the other, and
$Z_1 + Z_2$ has no term for it. That arrangement is a transformer, and it needs a mutual
inductance the series rule does not contain.
''',
                },
                {
                    "title": "Parallel: work in siemens, and ask what the node can see",
                    "minutes": 16,
                    "body": r'''
Series was one loop and one shared current. Parallel is the other primitive: two
components with both of their ends in common, so they share a *voltage* and the current
divides between them.

The same kind of surprise waits there, in the other coordinate. A node is held at 3.00 V
RMS, 2.00 kHz. Hanging off it, both going to ground, are a 1.00 kΩ resistor and a 100 nF
capacitor. Clip a current probe round each branch and you read 3.00 mA and 3.77 mA. Clip
it round the single wire feeding the node and you read 4.82 mA.

6.77 mA leaves in two directions and 4.82 mA arrives. This time it is Kirchhoff's
*current* law that appears to be in trouble, and the resolution is the one from the
previous unit: 3.00 mA and 3.77 mA are the sizes of two currents that peak a quarter
cycle apart.

## The natural variable for a node is not impedance

Run the series derivation again with the roles swapped. Both components have the same
phasor voltage $V$ across them, because both of their ends are common. Each carries
$I_k = V/Z_k$. Kirchhoff's current law says the total is the sum:

$$I = \frac{V}{Z_1} + \frac{V}{Z_2} = V\left(\frac{1}{Z_1} + \frac{1}{Z_2}\right)$$

so the pair behaves as a single impedance $Z$ with $1/Z = 1/Z_1 + 1/Z_2$. You can stop
there and reach for product over sum, and for exactly two components that is often
quickest. But the equation is pointing at which quantity is natural here, and it is worth
taking the hint.

Define the **admittance** $Y = 1/Z$, measured in **siemens** (S), the reciprocal of the
ohm. The line above is then simply

$$Y = Y_1 + Y_2 .$$

Parallel admittances add, exactly as series impedances add, and for the mirror-image
reason. Impedance is what a *loop* wants, because a loop shares a current. Admittance is
what a *node* wants, because a node shares a voltage. Choosing the wrong one is not
wrong, only laborious: three components in parallel is a nest of reciprocals in ohms and
a single addition in siemens.

Admittance splits the way impedance does. Where $Z = R + jX$ has a resistance and a
**reactance**, $Y = G + jB$ has a **conductance** $G$ and a **susceptance** $B$, both in
siemens. Component by component:

- a resistor: $Y = 1/R = G$, real, no angle, at every frequency;
- a capacitor: $Y = j\omega C$, so $B = +\omega C$ — and this is the friendlier form of
  the two, a multiplication where $Z_C$ needed a reciprocal;
- an inductor: $Y = 1/(j\omega L) = -j/(\omega L)$, so $B = -1/(\omega L)$.

Two sign notes save a great deal of trouble later. A capacitor has *negative* reactance
and *positive* susceptance, and the inductor is the other way round; the reciprocal flips
the sign because $1/j = -j$. And $G$ is not $1/R$ the moment anything else is in parallel
with the resistor — $G$ means $\operatorname{Re}(Y)$, and the real part of a reciprocal is
not the reciprocal of the real part. Module 9 charges for that one.

## Worked example: a resistor and a capacitor in parallel

1.00 kΩ across 100 nF at 2.00 kHz, with 3.00 V RMS on the node.

```
w    = 2*pi*2000                          = 12566 rad/s
G    = 1/1000                             = 1.0000e-3 S
B    = w*C = 12566 * 100e-9               = 1.2566e-3 S
Y    = 1.0000e-3 + j1.2566e-3 S
|Y|  = sqrt(1.0000e-6 + 1.5791e-6)
     = sqrt(2.5791e-6)                    = 1.6060e-3 S
|Z|  = 1/1.6060e-3                        = 622.68 ohm
ang  = -atan(1.2566/1.0000)               = -51.49 degrees
```

The angle on $Z$ is minus the angle on $Y$, because inverting a complex number reflects
it across the real axis. Now the three probe readings from the top of the page:

```
I_R  = 3.00 * 1.0000e-3                   = 3.0000 mA rms
I_C  = 3.00 * 1.2566e-3                   = 3.7699 mA rms
|I|  = 3.00 * 1.6060e-3                   = 4.8179 mA rms
```

and $\sqrt{3.000^2 + 3.770^2} = 4.818$ mA, so the current law is intact and it was the
arithmetic that needed fixing, not the physics.

The closed form is worth having as well. Product over sum, with $Z_C = 1/(j\omega C)$ and
top and bottom then multiplied by $j\omega C$:

$$Z = \frac{R \cdot \dfrac{1}{j\omega C}}{R + \dfrac{1}{j\omega C}}
    = \frac{R}{1 + j\omega R C}$$

Check it against the arithmetic above: $\omega R C = 1.2566$, so
$|Z| = 1000/\sqrt{1 + 1.2566^2} = 1000/1.6060 = 622.68$ Ω. Same number, one line.

And now *read* the closed form instead of only using it. At low frequency
$\omega RC \ll 1$ and $Z \to R$: the capacitor might as well not be fitted. At high
frequency the 1 is negligible and $|Z| \to 1/(\omega C)$: the resistor might as well not
be fitted. The two behaviours cross where $\omega R C = 1$, that is at

$$f = \frac{1}{2\pi R C} = \frac{1}{2\pi \times 1000 \times 100\times10^{-9}}
    = 1592\ \text{Hz}.$$

That is the corner formula the next module builds a filter out of, and it has arrived
here with no filter in sight — out of nothing but two components sharing two nodes.

## The mistake: product over sum, done on the magnitudes

Almost everyone, at least once, evaluates the parallel combination like this:

```
|Z| =? |Z_R| * |Z_C| / (|Z_R| + |Z_C|)
    = 1000 * 795.77 / 1795.77             = 443.14 ohm
```

against a true 622.68 Ω, which is 29% low. The formula is right and the arithmetic is
right; what is wrong is that product over sum is an operation on complex numbers, and
the magnitudes were substituted before the sum in the denominator was taken.
$|Z_1 + Z_2| \ne |Z_1| + |Z_2|$, here as everywhere else in the course.

A useful pair of bounds is hiding in that failure. For a resistance $R$ in parallel with
a reactance of size $X$, the true magnitude is $RX/\sqrt{R^2 + X^2}$, which always sits
between the magnitude-based product over sum, $RX/(R + X)$, and the smaller of $R$ and
$X$ taken alone. Above: between 443 Ω and 796 Ω, and 623 Ω is comfortably inside. Two
numbers you can get in your head bracket the answer, which is the sort of check worth
doing before trusting a calculator you have already mis-typed once.

## The divider that is charged through both of its resistors

Now the result this module exists for.

A divider: $R_1$ from the source down to the output node, $R_2$ from the output node to
ground. Connect a capacitor across $R_2$ — across the *lower* resistor, touching nothing
but the output node and the ground rail. Where is the corner frequency?

The reflex answer is $1/(2\pi R_2 C)$, because $R_2$ is the resistor the capacitor is
connected across. It is wrong every time, and the error grows with $R_2$.

Combine $R_2$ with the capacitor first, using the closed form above, then divide:

$$Z_2 = \frac{R_2}{1 + j\omega R_2 C}, \qquad
H = \frac{Z_2}{R_1 + Z_2} = \frac{R_2}{R_1 + R_2 + j\omega R_1 R_2 C}$$

and dividing top and bottom by $R_1 + R_2$ puts it in the standard first-order shape:

$$H = \frac{K}{1 + j\omega\tau}, \qquad
K = \frac{R_2}{R_1 + R_2}, \qquad
\tau = \frac{R_1 R_2}{R_1 + R_2}\,C = (R_1 \parallel R_2)\,C .$$

The time constant contains **both** resistors, combined in parallel. The guided
derivation later in this module walks those lines one at a time; the line to carry away
is the last one.

## Worked example: what that error costs

$R_1 = 4.70$ kΩ, $R_2 = 2.20$ kΩ, $C = 22$ nF.

```
K       = 2200/6900                           = 0.31884
R1||R2  = 4700*2200/6900 = 10.340e6/6900      = 1498.6 ohm
tau     = 1498.6 * 22e-9                      = 32.968 us
f_c     = 1/(2*pi*32.968e-6)                  = 4827.5 Hz

the reflex answer:
f_c?    = 1/(2*pi*2200*22e-9)                 = 3288.3 Hz
```

The reflex is 31.9% low, and the ratio of the two is not an accident:

$$\frac{f_{\text{reflex}}}{f_{\text{true}}} = \frac{R_1 \parallel R_2}{R_2}
= \frac{R_1}{R_1 + R_2},$$

so the fractional error is exactly $R_2/(R_1+R_2)$ — the divider's own low-frequency
gain. The mistake is nearly harmless when $R_1 \ll R_2$ and severe when $R_1 \gg R_2$:
with 3 kΩ on top and 100 Ω below you would be out by 3%; with 3 kΩ on top and 10 kΩ
below, out by 77%.

## Why the reflex is tempting, and the fix that generalises

The capacitor is *drawn* touching $R_2$ and not touching $R_1$, and a schematic is a
picture, so the eye supplies a story: this capacitor belongs to that resistor. Current
does not read pictures. Stand at the capacitor's own two terminals and ask what paths
exist for charging it. Downwards there is $R_2$ to ground. Upwards there is $R_1$ to the
source — and a voltage source, from the capacitor's point of view, is a fixed potential
that will supply whatever current is asked of it, which for the purpose of charging is
indistinguishable from a wire to ground. Two paths, in parallel, so $R_1 \parallel R_2$.

That procedure is the general one, and it is the thing to keep:

> The time constant of a node is its capacitance times the resistance seen looking out of
> that node with every independent source turned off — voltage sources replaced by short
> circuits, current sources by open circuits.

Turning the sources off is not a trick for getting the right number. It is the statement
that you are asking about the circuit's *own* response rather than about what happens to
be driving it. The resistance you get has a name, and module 10 supplies it.

## Where this stops working

**One capacitor, one node.** With two capacitors on two different nodes there is no
longer an independent time constant per node to compute: charging one changes the voltage
the other is charging towards, and the two responses mix. The circuit gets two corners
and they are not at $1/(2\pi R_a C_a)$ and $1/(2\pi R_b C_b)$. Module 5 puts a number on
what cascading costs.

**The source has a resistance too.** A signal generator with 600 Ω of output resistance
puts that 600 Ω in series with $R_1$ as far as the capacitor is concerned, so the
resistance that matters becomes $(R_1 + 600) \parallel R_2$. On the divider above that
moves 1498.6 Ω to 1554.7 Ω and drags the corner from 4828 Hz down to 4653 Hz — 3.6% from
a resistance nobody drew.

**Parallel is not always smaller.** Two resistors in parallel always come to less than
either one. It is tempting to promote that to a rule, and it is false. Put an inductor in
parallel with a capacitor: their susceptances have opposite signs, so at the frequency
where $\omega C = 1/(\omega L)$ they cancel exactly. $Y = 0$, and the combination's
impedance is infinite while neither branch is doing anything remarkable on its own. A
100 mH inductor across a 1 µF capacitor does it at 503 Hz. That is module 8, and nothing
but the sign of a susceptance makes it possible.

**Real sources are not shorts at every frequency.** "A voltage source is a short" is a
small-signal statement about an ideal part. Above a few megahertz the inductance of the
lead running to your bench supply is a larger impedance than the supply's own output
resistance, and the charging path you counted on is not there any more. That is why
decoupling capacitors exist, and why they are fitted next to the chip rather than next to
the power supply.
''',
                },
            ],
            "quiz": {
                "title": "Adding things that peak at different times",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A 300 Ω resistor is in series with an inductor whose reactance at this frequency is 400 Ω. What is the magnitude of the total impedance?",
                        "opts": ["700 Ω", "500 Ω", "100 Ω", "350 Ω"],
                        "a": 1,
                        "why": r'''
$Z = 300 + j400$, and $|Z| = \sqrt{300^2 + 400^2} = 500$ Ω. Adding the magnitudes
to get 700 Ω is the reflex left over from direct current, and it is wrong for the
same reason every time: the resistor's voltage and the inductor's voltage are a
quarter cycle apart, so the pair never reaches 700 Ω worth of opposition at any
instant. The 3-4-5 triangle turns up constantly in this course; it is worth
recognising on sight.
''',
                    },
                    {
                        "q": "Two impedances are connected in parallel. Which statement is always true?",
                        "opts": [
                            "Their admittances add",
                            "Their impedances add",
                            "The magnitude of the combination is smaller than either one alone",
                            "The combination is always more resistive than either one alone",
                        ],
                        "a": 0,
                        "why": r'''
$Y = Y_1 + Y_2$, always — that is what parallel means, because the two branches
share a voltage and their currents add. Impedances adding is the *series* rule.
The two claims about the combination are worth pausing on, because they fail in
different ways. "Smaller than either one alone" is true for two resistors — 100 Ω
beside 100 Ω gives 50 Ω — but it is not true in general: an inductor in parallel with
a capacitor has a combined impedance that runs off to infinity at one frequency while
each branch stays finite. "More resistive than either one alone" is not true even for
two resistors: 50 Ω is *less* resistance than either branch, and all three sit at
0°, so the combination is equally resistive and never more. For $L$ in parallel with
$C$ it is worse still — the combination has no resistive part at all, so it is not
"more resistive" than anything. Two susceptances of opposite sign can cancel, and a
sum that cancels is exactly what a sum of positive conductances can never do.
''',
                    },
                    {
                        "q": "A 1 kΩ resistor is in parallel with a capacitor whose reactance at this frequency is also 1 kΩ. What is the magnitude of the combination?",
                        "opts": ["2 kΩ", "1 kΩ", "707 Ω", "500 Ω"],
                        "a": 2,
                        "why": r'''
Work in admittance. The resistor contributes $10^{-3}$ S, the capacitor contributes
$j\,10^{-3}$ S, and those are at right angles, so $|Y| = \sqrt{2}\times10^{-3}$ S and
$|Z| = 1/|Y| = 707$ Ω. The answer 500 Ω is what you would get if both branches
were resistors — the arithmetic that halves two equal resistances. Reactance does
not cooperate that fully, so the combination stays larger than 500 Ω.
''',
                    },
                    {
                        "q": "A divider has a 3 kΩ resistor on top and a 1 kΩ resistor below, with a capacitor connected across the lower resistor. Which resistance sets the corner frequency?",
                        "opts": [
                            "1 kΩ — the resistor the capacitor is connected across",
                            "3 kΩ — the resistor above it",
                            "4 kΩ — the two in series",
                            "750 Ω — the two in parallel",
                        ],
                        "a": 3,
                        "why": r'''
750 Ω, the parallel combination. Look at it from the capacitor's terminals: to
charge, current can arrive through the 1 kΩ to ground *or* through the 3 kΩ
to the source, and as far as the capacitor is concerned a source is a short to
somewhere. Two paths in parallel is $3000 \times 1000/4000 = 750$ Ω, so the corner
is at $1/(2\pi \times 750 \times C)$. Using the 1 kΩ alone puts the corner at
$0.75$ of that — 25% too low. In general the mistaken corner is a fraction
$R_1/(R_1 + R_2)$ of the true one, so the mistake gets worse the *larger* the lower
resistor is: keep the 3 kΩ on top and a 10 kΩ below would put the corner 77% too
low, while a 100 Ω below would be out by only 3%.
''',
                    },
                    {
                        "q": "A resistor and a capacitor are in series across a 10 V RMS source. A voltmeter reads 8 V across the resistor. What does it read across the capacitor?",
                        "opts": ["2 V", "6 V", "8 V", "18 V"],
                        "a": 1,
                        "why": r'''
6 V. Kirchhoff's voltage law holds for the phasors, and the resistor's voltage and the
capacitor's voltage are exactly 90° apart, so the three magnitudes form a right
triangle: $\sqrt{10^2 - 8^2} = 6$. Subtracting to get 2 V assumes the two readings add
along a line, which is the whole habit this module is meant to break. As a check,
$8^2 + 6^2 = 100$, and the source is the hypotenuse because it is the sum.
''',
                    },
                    {
                        "q": "Can the voltage measured across one component of a series AC circuit exceed the source voltage?",
                        "opts": [
                            "No — Kirchhoff's voltage law forbids it",
                            "Yes, but only if the circuit contains something that amplifies",
                            "Yes — with both an inductor and a capacitor present, their voltages are opposite in sign and each can be larger than the source",
                            "Only if the source is a current source",
                        ],
                        "a": 2,
                        "why": r'''
Yes, and it is not a violation of anything. An inductor's voltage and a capacitor's
voltage are 180° apart, so in the phasor sum they subtract; if each is 30 V and
they differ by 1 V, the source only has to supply that 1 V. Both meters read 30 across
a 1 V supply. No energy is being created — the two components are passing the same
energy back and forth between them. A later module puts a number on how large that
multiplication gets, and it can easily reach fifty.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "A parallel pair, done in siemens",
                    "minutes": 9,
                    "lang": "text",
                    "caption": "Two components sharing two nodes, worked in admittance from end to end.",
                    "brief": r'''
Impedance is the loop's variable and admittance is the node's. This one is done entirely
in siemens: conductance and susceptance, added, and only inverted at the very end.

Microsiemens (µS) are used throughout so the numbers stay readable — 1 µS is
$10^{-6}$ S, and a 1 MΩ resistor is exactly 1 µS.
''',
                    "listing": r'''
at f = 4.00 kHz:      omega =  ___ rad/s


    R = 3.30 kohm                    G  =  ___ uS

    C = 15 nF                        B  =  ___ uS


both in parallel, on a node held at 6.00 V rms:

    |Y| =  ___ uS

    |Z| =  ___ ohm

    the current in the capacitor branch  =  ___ mA
''',
                    "blanks": [
                        {
                            "prompt": "The angular frequency",
                            "hole": "omega",
                            "opts": ["25133", "4000", "12566", "0.00025"],
                            "a": 0,
                            "why": r'''
$\omega = 2\pi f = 2\pi \times 4000 = 25133$ rad/s. The value 4000 is the frequency
itself, in cycles per second rather than radians per second; 12566 is $2\pi \times 2000$,
the right formula on the wrong frequency; and 0.00025 s is the period $T = 1/f$, which is
a time and not a rate at all. Every reactance and every susceptance below is built on
this number, so an error here propagates through the whole listing.
''',
                        },
                        {
                            "prompt": "The conductance of the resistor",
                            "hole": "g",
                            "opts": ["303.0", "3300", "0.0003030", "330.0"],
                            "a": 0,
                            "why": r'''
$G = 1/R = 1/3300 = 3.030\times10^{-4}$ S, and the listing asks for microsiemens, so
303.0 µS. The value 0.0003030 is the same quantity in siemens — right physics, wrong
unit, and the sort of slip that survives all the way to a final answer that is out by a
million. 3300 is the resistance copied across without inverting anything. A resistor's
admittance is real at every frequency, so $\omega$ plays no part in this line.
''',
                        },
                        {
                            "prompt": "The susceptance of the capacitor",
                            "hole": "b",
                            "opts": ["377.0", "2653", "60.00", "0.3770"],
                            "a": 0,
                            "why": r'''
$B = \omega C = 25133 \times 15\times10^{-9} = 3.770\times10^{-4}$ S $= 377.0$ µS.
Multiply — do not invert. Susceptance is the form in which a capacitor is *easy*, which
is a large part of why admittance is worth the change of variable. The value 2653 is
$X_C = 1/(\omega C)$ in ohms, the reactance rather than the susceptance; 60.00 µS is
$fC$ with the $2\pi$ left out; and 0.3770 is the answer in millisiemens.
''',
                        },
                        {
                            "prompt": "The magnitude of the combined admittance",
                            "hole": "ymag",
                            "opts": ["483.7", "680.0", "73.96", "168.0"],
                            "a": 0,
                            "why": r'''
$Y = 303.0 + j377.0$ µS, so $|Y| = \sqrt{303.0^2 + 377.0^2} = 483.7$ µS. The two parts
add as complex numbers — that is what "in parallel" means — but their sizes do not, so
680.0 µS is the same reflex the series case punishes, transplanted into siemens. 73.96 µS
is the difference, which would be right only if the two susceptances had opposite signs,
and one of these is a resistor with no sign at all. 168.0 µS is product over sum applied
to two conductances, which is the rule for two *resistances* in parallel used one level
too late: conductances in parallel simply add.
''',
                        },
                        {
                            "prompt": "The magnitude of the combined impedance",
                            "hole": "zmag",
                            "opts": ["2067", "1471", "2653", "5953"],
                            "a": 0,
                            "why": r'''
$|Z| = 1/|Y| = 1/(483.7\times10^{-6}) = 2067$ Ω. Invert once, at the end, after the
addition — inverting each branch first and then trying to combine is how the reciprocals
pile up. The value 1471 Ω is product over sum done on the magnitudes,
$3300 \times 2653/5953$, which is the standard parallel error and always understates;
2653 Ω is the capacitor's reactance alone; 5953 Ω is the two magnitudes added, an
operation with no meaning in a parallel circuit even when the arithmetic is legal.
A quick sanity check: the answer must be below both 3300 Ω and 2653 Ω, and above the
1471 Ω that product-over-sum-on-magnitudes gives.
''',
                        },
                        {
                            "prompt": "The current in the capacitor branch",
                            "hole": "ic",
                            "opts": ["2.262", "1.818", "2.902", "4.080"],
                            "a": 0,
                            "why": r'''
Both branches see the whole 6.00 V, because that is what parallel means, so the
capacitor's current is $V B = 6.00 \times 377.0\times10^{-6} = 2.262$ mA. The value 1.818
mA is the resistor's branch, $6.00 \times 303.0$ µS; 2.902 mA is the total current the
node draws, $6.00 \times 483.7$ µS; and 4.080 mA is the two branch readings added on a
meter, which is 41% more current than actually flows in the feed. Check the real
relation: $\sqrt{1.818^2 + 2.262^2} = 2.902$ mA.
''',
                        },
                    ],
                },
                {
                    "title": "Which resistance charges the capacitor",
                    "minutes": 10,
                    "lang": "text",
                    "caption": "A loaded divider, from four component values to a corner frequency.",
                    "brief": r'''
The claim that costs people the most marks in this module, walked through with numbers
rather than symbols. A capacitor sits across the lower resistor of a divider; the
question is which resistance decides how fast it charges.

Work down the listing in order. The interesting line is the second one.
''',
                    "listing": r'''
divider:      R1 = 8.20 kohm   from the source to the output node
              R2 = 3.30 kohm   from the output node to ground
              C  = 10 nF       connected across R2

    low-frequency gain, Vout/Vin        =  ___

    resistance the capacitor sees       =  ___ ohm

    time constant                       =  ___ us

    corner frequency                    =  ___ Hz

    using R2 alone would put the corner    ___

    gain one decade above the corner    =  ___
''',
                    "blanks": [
                        {
                            "prompt": "The gain well below the corner",
                            "hole": "k",
                            "opts": ["0.2870", "0.7130", "0.4024", "0.5000"],
                            "a": 0,
                            "why": r'''
Far below the corner the capacitor is effectively an open circuit, so the two resistors
divide on their own: $K = R_2/(R_1+R_2) = 3300/11500 = 0.2870$. The value 0.7130 is
$R_1/(R_1+R_2)$, the fraction that lands on the *upper* resistor — which is the voltage
you would measure across $R_1$, not at the output node. 0.4024 is $R_2/R_1$, the ratio of
the two resistors rather than the divider ratio; it is the same number only when one of
them is negligible.
''',
                        },
                        {
                            "prompt": "The resistance that sets the time constant",
                            "hole": "rsee",
                            "opts": ["2353", "3300", "8200", "11500"],
                            "a": 0,
                            "why": r'''
$R_1 \parallel R_2 = 8200 \times 3300/11500 = 2353$ Ω. Look out of the capacitor's own
terminals with the source turned off: downwards there is 3300 Ω to ground, upwards there
is 8200 Ω to a voltage source, and a voltage source seen from a capacitor is a short to
somewhere. Two paths, in parallel. Answering 3300 Ω is the reflex — the resistor the
capacitor is physically connected across — and it is the whole point of this exercise
that being connected across something confers no special status. 11500 Ω treats the two
resistors as a series pair, which is what the *source* sees, not what the capacitor sees.
''',
                        },
                        {
                            "prompt": "The time constant",
                            "hole": "tau",
                            "opts": ["23.53", "33.00", "82.00", "115.0"],
                            "a": 0,
                            "why": r'''
$\tau = (R_1 \parallel R_2)\,C = 2353 \times 10\times10^{-9} = 2.353\times10^{-5}$ s,
which is 23.53 µs. Each of the other values is the same multiplication done with a
different resistance: 33.00 µs uses $R_2$, 82.00 µs uses $R_1$, and 115.0 µs uses the two
in series. Keeping the units visible helps here — ohms times farads really does come out
in seconds, and 2353 Ω × 10 nF is $2.353\times10^3 \times 10^{-8}$, so the exponent
lands on $10^{-5}$ with no guesswork.
''',
                        },
                        {
                            "prompt": "The corner frequency",
                            "hole": "fc",
                            "opts": ["6764", "4823", "1941", "1384"],
                            "a": 0,
                            "why": r'''
$f_c = 1/(2\pi\tau) = 1/(2\pi \times 23.53\times10^{-6}) = 6764$ Hz. The other three are
the corners belonging to the three wrong time constants: 4823 Hz from $R_2$ alone,
1941 Hz from $R_1$ alone, 1384 Hz from the two in series. Note that the true corner is
the *highest* of the four, which is the general case — a parallel combination is smaller
than either resistance, so it always gives the fastest charging and therefore the
highest corner.
''',
                        },
                        {
                            "prompt": "What the reflex answer does to the corner",
                            "hole": "err",
                            "opts": [
                                "28.7% too low",
                                "28.7% too high",
                                "71.3% too low",
                                "exactly right — $R_2$ is the resistor it is across",
                            ],
                            "a": 0,
                            "why": r'''
4823 Hz against a true 6764 Hz is low by 28.7%. The fraction is worth memorising because
it is not arbitrary: $f_{\text{reflex}}/f_{\text{true}} = R_1/(R_1+R_2) = 0.713$, so the
shortfall is $R_2/(R_1+R_2)$ — the divider's own low-frequency gain, 0.2870, which is the
first number in this listing. A divider that attenuates a little has a small error; a
divider that attenuates hardly at all, meaning $R_2 \gg R_1$, has an error approaching
100%. Being 71.3% low would need the ratio the other way up, and the reflex can never
give an answer that is too high, because $R_1 \parallel R_2$ is always smaller than $R_2$.
''',
                        },
                        {
                            "prompt": "The gain a decade above the corner",
                            "hole": "gdec",
                            "opts": ["0.02855", "0.2028", "0.1435", "0.0002870"],
                            "a": 0,
                            "why": r'''
A first-order response falls at 20 dB per decade above the corner, so a decade up the
gain is about a tenth of $K$: $0.2870/\sqrt{1 + 10^2} = 0.2870/10.05 = 0.02855$. The
useful habit is that the roll-off multiplies the *low-frequency gain*, so a divider that
started at 0.2870 rather than 1 ends up ten times smaller everywhere, not at 0.1. The
value 0.2028 is $K/\sqrt2$, which is the gain exactly *at* the corner; 0.1435 is $K/2$,
which is 6 dB down and belongs nowhere in particular; 0.0002870 is $K/1000$, three
decades of roll-off rather than one.
''',
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "Two reactances that nearly cancel",
                    "minutes": 7,
                    "brief": r'''
One loop, three components, one current. The only new step compared with module 2 is
that there are now two reactances rather than one, and they point in opposite
directions.

Do them one at a time, combine them with their signs, and only then reach for the square
root.
''',
                    "prompt": "What is the magnitude of the impedance the source sees at 2.40 kHz?",
                    "note": "Give the answer in ohms, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 330},
                            {"id": "l1", "kind": "L", "x": 9, "y": 3, "rot": 0, "value": 0.068},
                            {"id": "out", "kind": "OUT", "x": 11, "y": 3, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 11, "y": 4, "rot": 1, "value": 6.8e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [8, 3]},
                            {"a": [10, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 7]},
                            {"a": [11, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "6.00 V RMS, 2.40 kHz"},
                        {"label": "Resistor", "value": "330 Ω"},
                        {"label": "Inductor", "value": "68 mH, ideal"},
                        {"label": "Capacitor", "value": "68 nF"},
                    ],
                    "aside": "There is one loop, so one current passes through all three components. "
                             "The probe sits between the inductor and the capacitor, which makes the "
                             "probed voltage the capacitor's own.",
                    "answer": 333.8,
                    "tol": 2.0,
                    "unit": "Ω",
                    # The capacitor's value and the source value both come off the drawing, and the
                    # loop current is recovered from the solved node voltage rather than restated, so
                    # re-valuing any part moves this number instead of leaving it stale.
                    "check": r'''
var f = 2400, w = 2 * Math.PI * f;
c.assert(c.count('R') === 1 && c.count('L') === 1 && c.count('C') === 1,
  "one of each, all in series");
var C = c.values('C')[0], vs = c.values('V')[0];
var i = c.gain(f) * w * C;
return vs / i;
''',
                    "hint": r"$X_L = \omega L$ and $X_C = 1/(\omega C)$. They pull in opposite directions, so combine them — with their signs — into one net reactance before you go anywhere near Pythagoras.",
                    "wrong": r"2331 Ω is $330 + 1025 + 975$, the three magnitudes laid end to end. "
                             r"1453 Ω is $\sqrt{330^2 + 1025^2 + 975^2}$ — quadrature applied to all "
                             r"three at once, which treats the inductor and the capacitor as "
                             r"independent directions when they are one direction with two signs. "
                             r"1025 Ω is the inductor alone.",
                    "why": r'''
```
w    = 2*pi*2400                            = 15080 rad/s
X_L  = w*L = 15080 * 0.068                  = 1025.4 ohm
X_C  = 1/(w*C) = 1/(15080 * 68e-9)          = 975.21 ohm
X    = X_L - X_C = 1025.4 - 975.21          = 50.202 ohm
|Z|  = sqrt(330^2 + 50.202^2)
     = sqrt(108900 + 2520.2)                = 333.80 ohm
```

Two components each worth about a kilohm leave 50 Ω between them, and the impedance the
source sees is 334 Ω — barely more than the resistor on its own. That is the whole
lesson of a signed reactance in one line.

It is worth carrying on for a moment, because the loop is more interesting than the
question asked. The current is $6.00/333.80 = 17.975$ mA, so the meters read

```
V_R = 17.975e-3 * 330                       = 5.9318 V rms
V_L = 17.975e-3 * 1025.4                    = 18.432 V rms
V_C = 17.975e-3 * 975.21                    = 17.529 V rms
```

The capacitor is sitting at 17.5 V RMS with 6.00 V going in — very nearly three times the
supply — and the inductor is worse. Neither is a fault. The two are 180° apart and cancel
to $|18.432 - 17.529| = 0.903$ V, and $\sqrt{5.9318^2 + 0.903^2} = 6.000$ V, which is the
source. A capacitor rated at 10 V in this loop would fail, and no meter on the source
would have warned you. Module 7 gives that multiplication a name and a formula.
''',
                },
                {
                    "title": "A current source and two branches",
                    "minutes": 8,
                    "brief": r'''
The parallel case, and the source pushes a fixed current rather than holding a fixed
voltage — so the impedance multiplies rather than divides, and there is no divider to do.

Admittances add. Do the whole of this one in siemens and invert once, at the end.
''',
                    "prompt": "What RMS voltage appears at the probe?",
                    "note": "Give the answer in volts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "is", "kind": "I", "x": 3, "y": 5, "rot": 1, "value": 0.002},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "out", "kind": "OUT", "x": 5, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 7, "y": 4, "rot": 1, "value": 2200},
                            {"id": "c1", "kind": "C", "x": 10, "y": 4, "rot": 1, "value": 3.3e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [10, 3]},
                            {"a": [7, 5], "b": [7, 7]},
                            {"a": [7, 7], "b": [3, 7]},
                            {"a": [10, 5], "b": [10, 7]},
                            {"a": [10, 7], "b": [7, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "2.00 mA RMS, 1.60 kHz"},
                        {"label": "Resistor", "value": "2.20 kΩ"},
                        {"label": "Capacitor", "value": "33 nF"},
                    ],
                    "aside": "The resistor and the capacitor have both of their ends in common — the "
                             "probed node above and the ground rail below — so they are in parallel "
                             "however far apart they are drawn.",
                    "answer": 3.554,
                    "tol": 0.02,
                    "unit": "V",
                    # Nothing is restated: the solver is driven by the current source on the drawing
                    # and the probe sits on the only node above ground, so the AC magnitude there is
                    # the answer in the units the source is quoted in.
                    "check": r'''
var f = 1600;
c.assert(c.count('I') === 1 && c.count('V') === 0,
  "a current source drives this one, not a voltage source");
c.assert(c.count('R') === 1 && c.count('C') === 1, "one resistor and one capacitor in parallel");
return c.gain(f);
''',
                    "hint": r"$G = 1/R$ and $B = \omega C$ are the two admittances. Add them in quadrature, invert to get $|Z|$, and multiply by the 2.00 mA.",
                    "wrong": r"4.400 V is $2.00\ \text{mA} \times 2200$ — the capacitor left out "
                             r"altogether. 6.029 V is the capacitor's 3014 Ω on its own. 2.544 V comes "
                             r"from $1/(G+B)$, the conductance and the susceptance added as plain "
                             r"numbers; it is the same value as product over sum done on the two "
                             r"magnitudes, which is why the error feels so reasonable from either "
                             r"direction.",
                    "why": r'''
```
w    = 2*pi*1600                            = 10053 rad/s
G    = 1/2200                               = 454.55e-6 S
B    = w*C = 10053 * 33e-9                  = 331.75e-6 S
|Y|  = sqrt(454.55^2 + 331.75^2) e-6        = 562.74e-6 S
|Z|  = 1/562.74e-6                          = 1777.0 ohm
V    = 2.00e-3 * 1777.0                     = 3.554 V rms
```

Three details are worth pulling out.

The impedance multiplies here. With a voltage source you divide by $|Z|$ to get a
current; with a current source you multiply by it to get a voltage. Same law, read from
the other end.

The answer is smaller than the resistor's own 2.20 kΩ, and it has to be — adding a second
path can only make it easier for current to leave the node, so $|Y|$ can only grow and
$|Z|$ can only shrink. That is a genuine rule for a resistor in parallel with anything
passive, and it is the sanity check to run before believing an answer.

And the branch currents show the current law doing exactly what it did in the reading.
$I_R = 3.554/2200 = 1.615$ mA and $I_C = 3.554 \times 331.75\ \mu\text{S} = 1.179$ mA.
Two meters would report 2.794 mA leaving a node fed with 2.000 mA; as phasors,
$\sqrt{1.615^2 + 1.179^2} = 2.000$ mA, and nothing has gone missing.
''',
                },
                {
                    "title": "Where this divider's corner really is",
                    "minutes": 9,
                    "brief": r'''
A plain resistive divider with a capacitor across the lower resistor. Below the corner it
divides as the two resistors say; above it, the output falls at 20 dB per decade.

The only question is which resistance sets the corner, and the drawing is designed to
make the wrong answer look obvious.
''',
                    "prompt": "What is the −3 dB corner frequency of this network?",
                    "note": "Give the answer in hertz, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                            {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 4700},
                            {"id": "p3", "kind": "R", "x": 8, "y": 4, "rot": 1, "value": 2200},
                            {"id": "p4", "kind": "OUT", "x": 8, "y": 3, "rot": 0, "value": 0},
                            {"id": "p5", "kind": "C", "x": 11, "y": 4, "rot": 1, "value": 2.2e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [4, 3]},
                            {"a": [6, 3], "b": [8, 3]},
                            {"a": [8, 5], "b": [8, 6]},
                            {"a": [8, 6], "b": [3, 6]},
                            {"a": [8, 3], "b": [11, 3]},
                            {"a": [11, 5], "b": [11, 6]},
                            {"a": [11, 6], "b": [8, 6]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V, swept"},
                        {"label": "Upper resistor", "value": "4.70 kΩ"},
                        {"label": "Lower resistor", "value": "2.20 kΩ"},
                        {"label": "Capacitor", "value": "22 nF, across the lower resistor"},
                    ],
                    "aside": "Well below the corner the capacitor is an open circuit and the output sits "
                             "at $2200/6900 = 0.3188$ of the source. The corner is the frequency at which "
                             "the output has fallen to $1/\\sqrt2$ of that.",
                    "answer": 4828.0,
                    "tol": 30.0,
                    "unit": "Hz",
                    # The corner is measured from the solved response by bisection rather than computed
                    # from a formula, so this check would catch a diagram whose capacitor is across the
                    # wrong resistor as readily as one whose value is wrong. The DC assert reads both
                    # resistances off the drawing.
                    "check": r'''
c.assert(c.count('R') === 2 && c.count('C') === 1, "two resistors and one capacitor");
var R = c.values('R');
c.close(c.vout(), R[1] / (R[0] + R[1]), 0.02,
  "at DC the capacitor is open, so the two resistors should divide on their own");
return c.corner(10, 1e6);
''',
                    "hint": r"Look out of the capacitor's terminals with the source turned off. Down to ground there is one resistor; up to the source there is another, and a voltage source is a short as far as charging is concerned.",
                    "wrong": r"3288 Hz uses the 2.20 kΩ alone, which is the resistor the capacitor is "
                             r"drawn across and is the answer this circuit is built to tempt. 1539 Hz "
                             r"uses the 4.70 kΩ alone. 1048 Hz uses the two in series — the resistance "
                             r"the *source* sees, which is a different question.",
                    "why": r'''
```
R1||R2 = 4700*2200/6900 = 10.340e6/6900     = 1498.6 ohm
tau    = 1498.6 * 22e-9                     = 32.968 us
f_c    = 1/(2*pi*32.968e-6)                 = 4828 Hz
```

Both resistors charge the capacitor, so both belong in the time constant, and they belong
there in parallel because they are two separate paths out of the same node. The reflex
answer of 3288 Hz is 31.9% low.

That shortfall is not a coincidence you have to remember separately:

$$\frac{f_{\text{reflex}}}{f_{\text{true}}}
= \frac{R_1 \parallel R_2}{R_2} = \frac{R_1}{R_1 + R_2} = \frac{4700}{6900} = 0.6812$$

so the error is $R_2/(R_1+R_2) = 0.3188$, which is the divider's own low-frequency gain —
the same 0.3188 the response sits at below the corner. A heavily attenuating divider has
a small error and a barely attenuating one has a large error, which is the opposite of
most people's intuition and worth checking once against a circuit you can measure.
''',
                },
                {
                    "title": "The current in one of two parallel branches",
                    "minutes": 11,
                    "brief": r'''
Two stages now, and the quantity asked for is a branch current rather than a node
voltage — so there is one more step after the divider is done.

The 1.50 kΩ and the inductor share both of their ends. Collapse that pair into a single
impedance first; what is left is a two-element divider of the kind module 2 finished on.
''',
                    "prompt": "What RMS current flows in the inductor?",
                    "note": "Give the answer in milliamps, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 470},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "r2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1500},
                            {"id": "l1", "kind": "L", "x": 12, "y": 4, "rot": 1, "value": 0.12},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                            {"a": [12, 5], "b": [12, 7]},
                            {"a": [12, 7], "b": [9, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "10.0 V RMS, 1.00 kHz"},
                        {"label": "Series resistor", "value": "470 Ω"},
                        {"label": "Shunt resistor", "value": "1.50 kΩ"},
                        {"label": "Inductor", "value": "120 mH, ideal"},
                    ],
                    "aside": "The probe sits on the node the two shunt branches share, so the probed "
                             "voltage is the voltage across the inductor as well as across the 1.50 kΩ.",
                    "answer": 9.123,
                    "tol": 0.06,
                    "unit": "mA",
                    # The inductor's own value and the solved voltage on its node are both read from
                    # the circuit; only the frequency comes from the prompt. Ohm's law for an inductor
                    # then gives the branch current directly, so no intermediate constant is trusted.
                    "check": r'''
var f = 1000, w = 2 * Math.PI * f;
c.assert(c.count('L') === 1 && c.count('R') === 2, "two resistors and one inductor");
var L = c.values('L')[0];
return 1000 * c.gain(f) / (w * L);
''',
                    "hint": r"Add $1/1500$ and $-j/(\omega L)$ to get the admittance of the shunt pair, invert it, add the 470 Ω, and divide. The inductor's current is then its own voltage over its own reactance.",
                    "wrong": r"13.26 mA is $10.0/X_L$ — the whole source across the inductor, which "
                             r"would need the 470 Ω to be a wire. 4.586 mA is the current in the "
                             r"1.50 kΩ instead. 10.21 mA is the total current the source supplies, "
                             r"which is neither branch.",
                    "why": r'''
```
w     = 2*pi*1000                            = 6283.2 rad/s
X_L   = w*L = 6283.2 * 0.120                 = 753.98 ohm

the shunt pair, in siemens:
G     = 1/1500                               = 666.67e-6 S
B     = -1/X_L = -1/753.98                   = -1326.3e-6 S
|Y2|  = sqrt(666.67^2 + 1326.3^2) e-6        = 1484.4e-6 S
|Z2|  = 1/1484.4e-6                          = 673.67 ohm
Z2    = 302.55 + j601.90 ohm

the divider:
Z     = 470 + Z2 = 772.55 + j601.90 ohm
|Z|   = sqrt(772.55^2 + 601.90^2)            = 979.35 ohm
Vout  = 10.0 * 673.67/979.35                 = 6.8787 V rms
I_L   = 6.8787/753.98                        = 9.1232 mA rms
```

The one step that cannot be short-circuited is the rectangular form of $Z_2$. The
magnitude 673.67 Ω is not enough on its own, because the 470 Ω has to be added to the
*real part* and the imaginary part left alone; adding 470 to 673.67 and calling the
result the total impedance gives 1144 Ω instead of 979 Ω. Converting an admittance back
to a rectangular impedance is $Z = \bar{Y}/|Y|^2$, which is where 302.55 and 601.90 come
from.

Once the node voltage is known, the last step is the easiest in the problem and the one
most often skipped: the inductor has 6.8787 V across it and 753.98 Ω of reactance, so it
carries 9.123 mA and nothing else in the circuit enters into it.

As a check, the 1.50 kΩ carries $6.8787/1500 = 4.586$ mA, and the two branch currents are
90° apart, so the source must be supplying
$\sqrt{9.123^2 + 4.586^2} = 10.21$ mA — which is $10.0/979.35$, as it should be. Two
meters on the branches would total 13.71 mA.
''',
                },
                {
                    "title": "A capacitor across each resistor",
                    "minutes": 13,
                    "brief": r'''
The hardest one in this module, and it is a circuit you will meet on a bench rather than
only on paper: an oscilloscope probe, with the resistances scaled down but the ratio
kept. The resistor in the probe body and the scope's own input resistance form a
1-in-11 divider, and each of them has a capacitance across it that nobody chose — the
cable and the scope's input below, a trimmer above.

Each resistor with its capacitor is a parallel pair. The two pairs are then a divider.
Nothing here is new; there is simply nothing signposted.
''',
                    "prompt": "With 1.00 V RMS going in, what does the probe read at 20.0 kHz?",
                    "note": "Give the answer in millivolts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                            {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "p2", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 100000},
                            {"id": "p3", "kind": "C", "x": 6, "y": 1, "rot": 0, "value": 1e-10},
                            {"id": "p4", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "p5", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 10000},
                            {"id": "p6", "kind": "C", "x": 12, "y": 4, "rot": 1, "value": 4.7e-10},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [5, 3], "b": [5, 1]},
                            {"a": [7, 1], "b": [7, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [12, 5], "b": [12, 7]},
                            {"a": [12, 7], "b": [9, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V RMS, 20.0 kHz"},
                        {"label": "Upper resistor", "value": "100 kΩ"},
                        {"label": "Across it", "value": "100 pF"},
                        {"label": "Lower resistor", "value": "10.0 kΩ"},
                        {"label": "Across it", "value": "470 pF"},
                    ],
                    "aside": "At DC the two capacitors are open circuits and the divider gives "
                             "$10/110 = 0.0909$. Far above both corners the resistors are irrelevant and "
                             "the two capacitors divide instead, giving $C_1/(C_1+C_2) = 0.1754$. "
                             "20.0 kHz is in between.",
                    "answer": 122.3,
                    "tol": 1.0,
                    "unit": "mV",
                    # Both parallel pairs, the divider between them and the source amplitude all come
                    # from the drawing; the check states only the frequency. Swapping either capacitor
                    # or mis-wiring one of them moves this number immediately.
                    "check": r'''
var f = 20000;
c.assert(c.count('R') === 2 && c.count('C') === 2, "two resistors, each with a capacitor across it");
return 1000 * c.gain(f) / c.values('V')[0];
''',
                    "hint": r"Each pair is $Z = R/(1 + j\omega R C)$. Get both as complex numbers, then $H = Z_2/(Z_1+Z_2)$. Take the magnitude once, at the very end.",
                    "wrong": r"90.91 mV is the DC answer, $R_2/(R_1+R_2)$, which is what the divider "
                             r"gives only well below both corners. 175.4 mV is $C_1/(C_1+C_2)$, the "
                             r"ratio it settles at far above both. 80.09 mV is the answer with the "
                             r"upper capacitor left out — a real mistake, because that capacitor is a "
                             r"trimmer and is easy to forget.",
                    "why": r'''
```
w      = 2*pi*20000                          = 125660 rad/s

upper pair:  w*R1*C1 = 125660 * 100e3 * 100e-12   = 1.2566
   Z1 = 100e3/(1 + j1.2566)                  = 38773 - j48723 ohm

lower pair:  w*R2*C2 = 125660 * 10e3 * 470e-12    = 0.59062
   Z2 = 10e3/(1 + j0.59062)                  = 7413.8 - j4378.7 ohm

Z1 + Z2                                      = 46186 - j53102 ohm
|Z2|    = sqrt(7413.8^2 + 4378.7^2)          = 8610.4 ohm
|Z1+Z2| = sqrt(46186^2 + 53102^2)            = 70378 ohm
|H|     = 8610.4/70378                       = 0.12235
Vout    = 1.00 * 0.12235                     = 122.3 mV rms
```

The rectangular form is not optional. Taking $|Z_1|$ and $|Z_2|$ first and dividing
$8610.4/(62268 + 8610.4)$ gives 121.5 mV, which is close enough to look right and is
arrived at by an operation that is not allowed; on a differently proportioned probe the
same shortcut is out by a factor of two.

Now the engineering. A divider like this is frequency-independent — a genuine 1-in-11 at
every frequency — exactly when the two time constants match, $R_1C_1 = R_2C_2$. Here
$R_1C_1 = 10.0$ µs and $R_2C_2 = 4.70$ µs, so they do not, and the upper branch's
impedance starts falling first. That lets *more* through as frequency rises: 90.91 mV at
DC, 122.3 mV at 20 kHz, and 175.4 mV a long way up. The probe is **over-compensated**, and
a square wave through it comes out with its corners overshot.

The cure is the trimmer. $C_1$ would need to be $R_2C_2/R_1 = 4.70\times10^{-6}/10^5 =
47$ pF, and adjusting it until a square wave looks square is exactly what the little
screw on a scope probe is for. Left as it is, the scope multiplies by 11 to undo a
division that is no longer 11, and reports a 1.00 V signal at 20 kHz as 1.35 V — a 35%
error with no warning anywhere on the screen.
''',
                },
            ],
            "build": {
                "title": "A divider that stops dividing",
                "minutes": 24,
                "brief": r'''
The claim from the concepts, drawn and measured.

You are given a plain resistive divider: 3 kΩ on top, 1 kΩ below, the probe on
the junction. It gives a quarter of the source at every frequency, because there is
nothing in it that knows what frequency is.

Add a **capacitor across the lower resistor** so that the divider keeps working at low
frequency and gives up above a kilohertz.

1. **At DC nothing changes.** The probe still reads a quarter of the source, because
   the capacitor is an open circuit there and the two resistors divide on their own.
2. **The corner sits at 1 kHz**, within 5%.
3. **It rolls off at 20 dB per decade** — a decade above the corner the output is
   about a tenth of its low-frequency value.
4. **Two decades up there is essentially nothing left.**

The trap is the one the concepts named. The corner is *not* at
$1/(2\pi R_2 C)$; it is at $1/(2\pi (R_1 \parallel R_2) C)$, because the capacitor is
charged through both resistors at once. Work out that parallel resistance first and
the capacitance follows.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 3000},
                        {"id": "p3", "kind": "R", "x": 8, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "OUT", "x": 8, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [8, 3]},
                        {"a": [8, 5], "b": [8, 6]},
                        {"a": [8, 6], "b": [3, 6]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 3000},
                        {"id": "p3", "kind": "R", "x": 8, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "OUT", "x": 8, "y": 3, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "C", "x": 11, "y": 4, "rot": 1, "value": 2.12e-7},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [8, 3]},
                        {"a": [8, 5], "b": [8, 6]},
                        {"a": [8, 6], "b": [3, 6]},
                        {"a": [8, 3], "b": [11, 3]},
                        {"a": [11, 5], "b": [11, 6]},
                        {"a": [11, 6], "b": [8, 6]},
                    ],
                },
                "checks": [
                    {"name": "at DC the divider still gives a quarter of the source", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(Math.abs(c.vout()), 0.25 * vs, 0.02,
  "with the capacitor open at DC the two resistors should divide exactly as they did before");
'''},
                    {"name": "the corner is at 1 kHz", "code": r'''
var fc = c.corner(10, 1e6);
c.close(fc, 1000, 0.05,
  "the corner measured from the response is " + c.fmt(fc, "Hz") +
  " — check which resistance the capacitor is actually charged through");
'''},
                    {"name": "it rolls off at 20 dB per decade", "code": r'''
var ratio = c.gain(10000) / c.gain(10);
c.close(ratio, 0.0995, 0.08,
  "a decade above a first-order corner the output should be about a tenth of the low-frequency value");
'''},
                    {"name": "two decades up there is essentially nothing left", "code": r'''
var vs = Math.abs(c.values("V")[0]);
var g = c.gain(100000) / vs;
c.assert(g < 0.005,
  "40 dB down from a quarter is about 0.0025 of the source; measured " + g.toPrecision(3) +
  " — a capacitor across the wrong resistor does the opposite of this");
'''},
                ],
                "hints": [
                    "The capacitor goes from the probe node down to the ground rail, in parallel with the 1 kΩ. Across the 3 kΩ instead and you get a filter that passes *high* frequencies.",
                    "The resistance that matters is $R_1 \\parallel R_2 = 3000 \\times 1000 / 4000 = 750$ Ω.",
                    "So $C = 1/(2\\pi \\times 750 \\times 1000) = 212$ nF. Values accept engineering suffixes, so 212n is enough.",
                    "If the corner check reports something near a megahertz, the response is flat — one of the capacitor's pins is not wired to anything.",
                ],
            },
            "derive": {
                "title": "Where the corner of a loaded divider really is",
                "minutes": 13,
                "vars": ["R_1", "R_2", "C", "omega", "j"],
                "brief": r'''
A divider: $R_1$ from the source to the output node, $R_2$ from the output node to
ground, and a capacitor $C$ across $R_2$. Four steps take it from two component
impedances to a corner frequency, and the answer is not the one most people write
down.

Write $j$ for the square root of $-1$ and leave it as a symbol throughout; nothing
below needs you to square it.
''',
                "steps": [
                    {
                        "prompt": "Write the impedance of the capacitor at angular frequency $\\omega$.",
                        "answer": "\\frac{1}{j\\omega C}",
                        "hint": "This is the definition from the impedance module. Note it is $\\omega$, not $f$.",
                        "deconstruct": [
                            "The capacitor's impedance has magnitude $1/(\\omega C)$.",
                            "Its angle is $-90^\\circ$, and dividing by $j$ is what turns a quarter cycle backwards.",
                        ],
                    },
                    {
                        "prompt": "$R_2$ and the capacitor are in parallel. Combine them into a single impedance $Z_2$, written as a fraction whose denominator begins with 1.",
                        "given": "Parallel means $Z_2 = \\dfrac{Z_a Z_b}{Z_a + Z_b}$.",
                        "answer": "\\frac{R_2}{1 + j\\omega R_2 C}",
                        "placeholder": "\\frac{R_2}{1 + \\ldots}",
                        "hint": "Form the product over the sum, then multiply the top and the bottom by $j\\omega C$ to clear the fraction inside the fraction.",
                        "deconstruct": [
                            "Product over sum gives $\\dfrac{R_2 \\cdot 1/(j\\omega C)}{R_2 + 1/(j\\omega C)}$.",
                            "Multiply top and bottom by $j\\omega C$: the top becomes $R_2$ and the bottom becomes $j\\omega R_2 C + 1$.",
                        ],
                    },
                    {
                        "prompt": "Now the divider. Write $H = \\dfrac{Z_2}{R_1 + Z_2}$ as a single fraction in $R_1$, $R_2$, $C$ and $\\omega$, with no fraction left inside it.",
                        "answer": "\\frac{R_2}{R_1 + R_2 + j\\omega R_1 R_2 C}",
                        "hint": "Substitute what you just found, then multiply the top and the bottom of the whole thing by $1 + j\\omega R_2 C$.",
                        "deconstruct": [
                            "Substituting gives $\\dfrac{R_2/(1+j\\omega R_2 C)}{R_1 + R_2/(1+j\\omega R_2 C)}$.",
                            "Multiplying top and bottom by $1 + j\\omega R_2 C$ leaves $\\dfrac{R_2}{R_1(1 + j\\omega R_2 C) + R_2}$.",
                            "Expanding the bracket gives $R_1 + R_2 + j\\omega R_1 R_2 C$ underneath.",
                        ],
                    },
                    {
                        "prompt": "Divide the top and the bottom by $R_1 + R_2$. The result has the shape $K/(1 + j\\omega\\tau)$. Write $\\tau$.",
                        "answer": "\\frac{R_1 R_2 C}{R_1 + R_2}",
                        "hint": "Everything multiplying $j\\omega$ in the denominator is the time constant.",
                        "deconstruct": [
                            "After dividing, the constant term underneath is 1 and the low-frequency gain is $K = R_2/(R_1+R_2)$.",
                            "What is left multiplying $j\\omega$ is $R_1 R_2 C/(R_1 + R_2)$.",
                        ],
                    },
                ],
                "closing": r'''
$\tau = \dfrac{R_1 R_2}{R_1 + R_2}\,C$, and the fraction in front of $C$ is exactly
$R_1 \parallel R_2$. So the corner is at $f_c = 1/(2\pi (R_1 \parallel R_2) C)$ and the
resistor the capacitor is *connected across* has no special standing at all — both
resistors charge it.

The general form of that statement is worth carrying forward: the time constant of a
node is its capacitance times the resistance seen looking out of it with the sources
turned off. A later module gives that resistance its proper name.
''',
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "The series RC filter and its corner frequency",
            "summary": "A resistor and a capacitor in series make a divider whose ratio depends on frequency. One number describes the whole thing.",
            "concepts": [
                "A divider works with impedances exactly as it worked with resistances in EE101: $V_{out}/V_{in} = Z_2/(Z_1 + Z_2)$, where $Z_2$ is the impedance the output is measured across.",
                "Resistor first, capacitor to ground, output across the capacitor: $H = \\dfrac{1}{1 + j\\omega R C}$. This is a **low-pass** filter — low frequencies pass, high ones do not.",
                "Its magnitude is $|H| = \\dfrac{1}{\\sqrt{1 + (f/f_c)^2}}$, where the **corner frequency** is $f_c = \\dfrac{1}{2\\pi R C}$.",
                "At the corner, $|H| = 1/\\sqrt{2} = 0.707$ and the phase is exactly −45°. In decibels that is $20\\log_{10}(0.707) = -3.01$ dB, which is why it is called the −3 dB point.",
                "A decade above the corner the output is a tenth; two decades, a hundredth. A first-order filter rolls off at **20 dB per decade**, and no first-order filter rolls off faster.",
                "The **time constant** $\\tau = RC$ is the same fact in the time domain: $f_c = 1/(2\\pi\\tau)$. Charge the capacitor through the resistor and it reaches 63% of its final voltage after one $\\tau$.",
                "Only the product $RC$ sets the corner. 1 kΩ with 1 µF and 1 MΩ with 1 nF are the same filter — but not the same circuit, because the impedance level decides how heavily it loads whatever drives it.",
            ],
            "read": [
                {
                    "title": "A divider that answers differently at every frequency",
                    "minutes": 13,
                    "body": r'''
Two components and a probe. A resistor from the source to a middle node, a capacitor
from that middle node down to the ground rail, and the output taken at the middle. It is
the divider EE101 built out of two resistors, with the lower one swapped — and that one
swap turns a fixed ratio into a machine that sorts signals by how fast they move.

Before any impedance appears it is worth being clear about why such a thing can possibly
work, because nothing in the circuit measures a frequency. The capacitor does not know
what a hertz is. Neither does the resistor. What the pair has between them is a *speed
limit*, and a signal is sorted by whether it is asking for something faster than that
limit.

## What the capacitor is actually doing

A capacitor stores charge, and its voltage is that charge divided by its capacitance,
$v = q/C$. To change the voltage across it you have to move charge onto it or off it,
and in this circuit the only route in or out is through the resistor. That is the entire
mechanism; everything below is bookkeeping on it.

Suppose that at some instant the output sits at $v$ while the source sits at $v_{in}$.
The resistor then has $v_{in} - v$ across it, so it passes

$$i = \frac{v_{in} - v}{R}$$

There is nowhere else for that current to go, so all of it lands on the capacitor and
changes its voltage at a rate $dv/dt = i/C$. Put the two together:

$$\frac{dv}{dt} = \frac{v_{in} - v}{RC}$$

Read that as a sentence rather than as an equation. *The output chases the input, and
the speed of the chase is proportional to how far behind it currently is.* The constant
of proportionality is $1/RC$. The left-hand side is volts per second and the top of the
right-hand side is volts, so $RC$ has to be a time — ohms times farads really do
multiply out to seconds — and it is the only time anywhere in the circuit.

Now drive the input with a sinusoid and ask whether the output can keep up.

- A **slow** wave. The input creeps upward over many milliseconds while $RC$ is a few
  microseconds. The gap $v_{in} - v$ never gets a chance to open, because any gap is
  closed almost at once. The two curves lie on top of one another and the output is the
  input.
- A **fast** wave. The input has swung up, come back through zero and gone negative
  before the output has travelled any distance at all. The output still chases — it
  always chases — but it gets only a little way before the target reverses and it has to
  turn round. Double the frequency and it gets half as far. What comes out is a small
  wobble on an almost flat line.

The hinge between those two behaviours is where the time the wave allows, some fraction
of its period, becomes comparable with $RC$. That is what a corner frequency is, and you
could estimate one to within a factor of two from this paragraph alone. The rest of this
unit turns "comparable with" into a number.

## The same statement, as a divider

The chasing picture is right, but it is hard to compute with. Module 2 supplied the
shortcut: at one frequency, replace each component by an impedance and the whole
apparatus of EE101 comes back unchanged. The resistor's impedance is $R$. The
capacitor's is

$$Z_C = \frac{1}{j\omega C}$$

and the divider rule is the one from EE101 with $Z$ in place of $R$:

$$H = \frac{V_{out}}{V_{in}} = \frac{Z_C}{R + Z_C} = \frac{1/(j\omega C)}{R + 1/(j\omega C)}$$

Multiply the top and the bottom by $j\omega C$ to clear the fraction inside the
fraction, and the whole thing collapses:

$$H = \frac{1}{1 + j\omega R C}$$

That is the filter, complete. One expression, valid at every frequency, and the $RC$
from the chasing argument is sitting in it exactly where you would expect: multiplied by
$\omega$, so that what matters is neither $\omega$ nor $RC$ but their product.

Two sanity checks before going on. At $\omega = 0$ — a steady voltage — $H = 1$: the
capacitor is an open circuit, no current flows, nothing is dropped across the resistor,
and the output equals the input. As $\omega \to \infty$, $H \to 0$: the capacitor's
reactance shrinks towards nothing and holds the output node down. Both match the
picture, which is the least a formula should do.

## The size of it

$H$ is a complex number and it carries two facts: how much the output shrinks, and how
far it lags. Take the size first. The denominator is $1 + j\omega RC$, whose magnitude is
$\sqrt{1 + (\omega RC)^2}$, so

$$|H| = \frac{1}{\sqrt{1 + (\omega R C)^2}}$$

The dimensionless group $\omega RC$ is doing all the work. When it is much less than 1
the square root is 1 and nothing happens. When it is much greater than 1 the square root
is $\omega RC$ and $|H| \approx 1/(\omega RC)$, which halves every time the frequency
doubles.

The interesting frequency is the one where that group equals exactly 1:

$$\omega_c R C = 1 \quad\Longrightarrow\quad \omega_c = \frac{1}{RC} \quad\Longrightarrow\quad f_c = \frac{1}{2\pi R C}$$

That $2\pi$ is not decoration. $\omega_c = 1/RC$ is in radians per second; $f_c$ is in
cycles per second; the two differ by the number of radians in a cycle. Almost every
wrong corner frequency in this course is $1/RC$ quoted in hertz.

Written in terms of the corner, the magnitude loses its component values altogether:

$$|H| = \frac{1}{\sqrt{1 + (f/f_c)^2}}$$

Every first-order low-pass ever built has that curve. Only its horizontal position
changes.

## Why 0.707 and not a half

At $f = f_c$, $|H| = 1/\sqrt2 = 0.7071$. It is worth knowing why that number rather than
$0.5$: the corner is defined as the **half-power** point, and power in a resistance goes
as the *square* of voltage. Half the power is therefore $\sqrt{0.5} = 0.707$ of the
voltage. Answering 0.5 means a statement about power has been taken as a statement about
amplitude, which is precisely the trap the definition sets.

The phase at the corner is $-45^\circ$. At that frequency $R$ and $1/(\omega C)$ are the
same size, so the real and imaginary parts of the denominator are equal and the angle
splits the difference exactly.

## Worked: 8.2 kΩ and 10 nF, at three frequencies

A 2.00 V RMS source drives $R = 8.2$ kΩ into $C = 10$ nF, with the probe on the
capacitor. Where is the corner, and what does a meter on the output read at 500 Hz, at
the corner, and at 20 kHz?

```
RC    = 8200 * 10e-9                     = 8.2000e-5 s
f_c   = 1/(2*pi*8.2e-5)                  = 1940.9 Hz

at 500 Hz:
  f/f_c = 500/1940.9                     = 0.25761
  |H|   = 1/sqrt(1 + 0.25761^2)
        = 1/sqrt(1.06636)                = 0.96838
  Vout  = 2.00 * 0.96838                 = 1.9368 V rms
  phase = -atan(0.25761)                 = -14.45 deg

at 1940.9 Hz:
  f/f_c                                  = 1 (by definition)
  |H|   = 1/sqrt(2)                      = 0.70711
  Vout  = 2.00 * 0.70711                 = 1.4142 V rms
  phase                                  = -45.00 deg

at 20 kHz:
  f/f_c = 20000/1940.9                   = 10.304
  |H|   = 1/sqrt(1 + 106.18)
        = 1/10.353                       = 0.096592
  Vout  = 2.00 * 0.096592                = 0.19318 V rms
  phase = -atan(10.304)                  = -84.46 deg
```

Each of the three is worth a moment. At 500 Hz — a quarter of the way to the corner —
the filter has taken 3% off. It is not "doing nothing" below the corner; it is doing
very little, and how little falls away as the *square* of the ratio, which is why the
pass band looks so flat. At 20 kHz, which is 10.3 times the corner, the output is very
nearly $1/10.3$ of the input: once you are well past the corner the response is simply
$f_c/f$ and the square root stops earning its keep.

## Decibels, decades and two straight lines

Ratios that span six orders of magnitude are unreadable as fractions, so they are quoted
in decibels: $20\log_{10}|H|$. The 20 rather than 10 is because $|H|$ is a voltage ratio
while decibels are defined on power. In that notation $0.7071$ becomes $-3.01$ dB, which
is where "the −3 dB point" comes from, and the $0.096592$ above becomes $-20.30$ dB.

Well above the corner $|H| \approx f_c/f$, so a factor of ten in frequency is a factor of
ten down in amplitude, and that is $-20$ dB. This is the famous **20 dB per decade**, and
it is the fastest a single resistor and capacitor can ever roll off: one energy store,
one power of $f$ in the denominator. It also gives the cheapest possible sketch of the
response — a horizontal line at 0 dB below the corner, a line sloping at −20 dB/decade
above it, and the two meeting at $f_c$. The true curve hugs both asymptotes and passes
3 dB below their meeting point. That meeting is the corner, and it is where the name
comes from.

## Worked: backwards, from a single measurement

You are handed a sealed box and told only that it contains an R and a C arranged as a
low-pass. Feeding it 1.00 V RMS at 3.00 kHz gives 0.400 V RMS out. Where is the corner,
and what are the components?

```
|H|         = 0.400/1.00                 = 0.4000
1/|H|^2     = 1/0.1600                   = 6.2500
(f/f_c)^2   = 6.2500 - 1                 = 5.2500
f/f_c       = sqrt(5.2500)               = 2.2913
f_c         = 3000/2.2913                = 1309.3 Hz

RC          = 1/(2*pi*1309.3)            = 1.2156e-4 s
with C = 100 nF:   R = 1.2156e-4/1e-7    = 1215.6 ohm
```

Note carefully what the measurement can and cannot tell you. It pins the *product* $RC$
down exactly; it says nothing whatever about the individual values. A 1.22 kΩ with 100 nF
and a 122 kΩ with 1 nF would both have produced 0.400 V at 3 kHz. To separate them you
would have to hang a load on the output and see which one sags — the impedance level is
invisible to a measurement made with a perfect meter.

## The mistakes that actually happen

- **The missing $2\pi$.** $1/RC$ is an angular frequency in radians per second. Quote it
  as a corner in hertz and you are out by 6.28 — and the wrong answer often looks tidier
  than the right one, which is what makes it stick. In the worked example above,
  $1/RC = 12\,195$ rad/s against a corner of 1941 Hz.
- **Taking the corner to be where the output halves.** It is where the *power* halves.
  The half-amplitude point is further out, at $f = \sqrt3\,f_c$, which is 73% above the
  corner.
- **Reading the corner as a wall.** Nothing is blocked. At ten times the corner a tenth
  of the signal is still there, so a 100 mV interferer sitting on top of a 1 mV
  measurement is still 10 mV after the filter — ten times larger than the thing you were
  trying to measure. "Filtered out" is a statement that needs a number attached.
- **Adding the two impedances as plain numbers.** $|Z_C|/(R + |Z_C|)$ is not the divider.
  At the corner it gives 0.5 instead of 0.707, and it is wrong at every other frequency
  too. The resistor and the capacitor are at right angles to one another, and they
  combine only through the square root.

## Where this stops holding

Three assumptions are hiding inside $H = 1/(1 + j\omega RC)$, and all three break in
ordinary use.

**The source is ideal.** Whatever drives the filter has an output resistance of its own,
and it sits in series with $R$, so the corner is really at $1/(2\pi(R_s + R)C)$. With
$R = 100$ Ω and a signal generator's usual 50 Ω, the real corner is a third below the one
written on the drawing.

**Nothing is connected to the output.** Hang a load $R_L$ across the capacitor and two
things change at once. The low-frequency gain drops to $R_L/(R + R_L)$, and the capacitor
now charges through $R \parallel R_L$, which is *smaller* than $R$, so the corner moves
**up**. Module 3 worked that case through in full; the habit to carry away is that a
capacitor's time constant is set by the resistance seen looking out of its own terminals
with the sources turned off, never by the resistor it happens to be drawn beside.

**The components are ideal.** A real capacitor has a few tens of milliohms of series
resistance and a nanohenry or two of series inductance. Above its self-resonance — a few
megahertz for a small ceramic, and often well below one for a large electrolytic — it
stops behaving as a capacitor at all and its
impedance starts *rising*, so the attenuation stops improving and eventually goes
backwards. This is why a filter that measures beautifully across the audio band can pass
a fast switching spike almost untouched.

And one limit that is not a defect but a law: 20 dB per decade is the most that a single
storage element can do. If a specification demands 60 dB of rejection one octave above
the pass band, no choice of $R$ and $C$ reaches it. Module 5 puts two of these in a row
and shows what that costs; anything sharper than that needs inductors or amplifiers, and
a course of its own.
''',
                },
                {
                    "title": "The same two components, timed with a stopwatch",
                    "minutes": 12,
                    "body": r'''
Switch a 5 V supply onto the input of an RC low-pass and watch the output on a scope. It
does not step. It leans over and climbs, fast at first and then more and more slowly,
approaching 5 V without there being any particular moment at which it arrives.
Everything in the previous unit was about sinusoids in the steady state. This is the same
two components asked a different question — and the answer contains the same $RC$.

That is not a coincidence and they are not two topics. A first-order filter has exactly
one number in it. Whether you call that number a corner frequency in hertz or a time
constant in seconds is a matter of which instrument happens to be in front of you.

## The equation, and the shape that solves it

The previous unit already wrote the equation down, out of nothing but Ohm's law and the
definition of capacitance:

$$\frac{dv}{dt} = \frac{V - v}{RC}$$

with $V$ the level the input has jumped to and $v$ the output. At the instant of the step
the capacitor is still empty, so the whole of $V$ appears across the resistor and the
current is $V/R$ — the largest it will ever be. As $v$ climbs, less voltage is left over
for the resistor, so less current flows, so the climb slows. The output is braked by its
own progress.

A quantity whose rate of change is proportional to its remaining distance approaches the
target exponentially. Writing $\tau = RC$, the solution that starts from an empty
capacitor is

$$v(t) = V\left(1 - e^{-t/\tau}\right)$$

and the gap still to be closed is

$$V - v(t) = V\,e^{-t/\tau}$$

The second form is the more useful of the two, because it has no offset in it. The gap
shrinks by a factor of $e = 2.71828$ every $\tau$ seconds, no matter how much of it is
left. That is the whole content of an exponential: the curve has no memory. Come back
after any delay you like, call the present voltage the new starting point, and what
happens next is identical.

## What $\tau$ actually is

Put $t = \tau$ into the solution: $v = V(1 - e^{-1}) = 0.632\,V$. So one time constant is
the time to cover 63.2% of the distance — not the time to charge, which is the commonest
thing people take it for. Continuing:

```
t = 1 tau     63.21% of the way there     36.79% of the gap left
t = 2 tau     86.47%                      13.53%
t = 3 tau     95.02%                       4.98%
t = 4 tau     98.17%                       1.83%
t = 5 tau     99.33%                       0.67%
```

"Five time constants and it has got there" is the working rule, and what it means
precisely is *got there to within 0.7%*. If the instrument downstream resolves 0.1% you
need $\ln(1000) = 6.9$ time constants; for one part in 4096, which is 12-bit resolution,
you need $\ln(4096) = 8.3$. The general statement is that covering a fraction $k$ of the
distance takes

$$t = \tau \ln\frac{1}{1-k}$$

and that is the form every settling-time specification is really written in.

The units deserve one line of reassurance, because $\tau = RC$ looks as though it ought to
come out in ohm-farads. An ohm is a volt per amp; a farad is a coulomb per volt;
multiplied, the volts cancel and you have coulombs per amp. An amp is a coulomb per
second. Seconds.

## Worked: 47 kΩ charging 2.2 µF

A 5.00 V step is applied through $R = 47$ kΩ to $C = 2.2$ µF. How long until the output
reaches 3.00 V, and where has it got to at 200 ms?

```
tau    = 47000 * 2.2e-6                  = 0.10340 s = 103.40 ms
i(0)   = 5.00/47000                      = 106.4 uA

to 3.00 V:
  k    = 3.00/5.00                       = 0.6000
  t    = tau * ln(1/(1 - 0.6000))
       = 0.10340 * ln(2.5000)
       = 0.10340 * 0.91629               = 0.094744 s = 94.74 ms

at t = 200 ms:
  t/tau = 0.2000/0.10340                 = 1.9342
  e^-1.9342                              = 0.14454
  v    = 5.00 * (1 - 0.14454)            = 4.2773 V
```

Check both against the table before believing them. 94.7 ms is a little under one time
constant, and one time constant gets you to 63.2%, or 3.16 V — so reaching 3.00 V a
fraction sooner is right. And 200 ms is a little under two time constants, where the
table says 86.5%, or 4.32 V; 4.277 V is just short of that, as it should be.

## Worked: from a rise time on a screen to a bandwidth

Instruments do not quote $\tau$. They quote a **rise time**: how long the output takes to
go from 10% to 90% of its final value. Those two levels are used because a scope can find
them on a trace, whereas 63.2% is a landmark of nothing.

Both come out of the same formula. Reaching 10% takes $\tau\ln(1/0.9) = 0.10536\,\tau$;
reaching 90% takes $\tau\ln(1/0.1) = 2.30259\,\tau$; the difference is

$$t_r = \tau \ln 9 = 2.1972\,\tau$$

Suppose a scope shows a 35.0 µs rise time on a filtered edge. What is the filter's corner
frequency?

```
tau   = 35.0e-6 / 2.1972                 = 15.929 us
f_c   = 1/(2*pi*15.929e-6)               = 9991 Hz   (call it 10.0 kHz)
```

Eliminate $\tau$ between the two relations and the pair collapses to a single constant:

$$t_r\,f_c = \frac{\ln 9}{2\pi} = 0.3497 \approx 0.35$$

This is the rule of thumb every hardware engineer carries: **rise time times bandwidth is
0.35**. A 100 MHz oscilloscope cannot display an edge faster than 3.5 ns whatever produced
it, and a signal with a 1 ns edge carries content out to roughly 350 MHz, so the wire it
travels on has to behave that far up. Both statements are this one line.

## The two views are one view

$$f_c = \frac{1}{2\pi R C} = \frac{1}{2\pi\tau} \qquad\Longleftrightarrow\qquad \tau = \frac{1}{2\pi f_c}$$

There is one number in this circuit, and the two descriptions are that number in
different units, exactly as $f$ and $\omega$ are. It has a consequence people sometimes
wish were otherwise: you cannot separately choose how much noise a filter removes and how
quickly it settles. Wanting a corner at 1 Hz to kill mains hum means accepting
$\tau = 159$ ms, which means waiting roughly 0.8 s before a reading can be trusted to 1%.
That trade is not a weakness of the RC filter; it is a property of first-order systems.
Better filters change the *shape* of the trade rather than escaping it.

## The mistakes that actually happen

- **"$\tau$ is the charging time."** It is the time to get 63% of the way. Nothing ever
  finishes charging — the exponential never reaches its target — which is why every
  settling specification has to name a tolerance along with a time.
- **Using $1/f_c$ as the rise time.** $1/f_c$ is $2\pi\tau = 6.28\,\tau$, nearly three
  times the true $2.20\,\tau$. The two quantities are related, but not by 1.
- **Assuming the capacitor charges through the resistor it is drawn across.** It charges
  through everything it can see with the sources turned off. In a divider that is
  $R_1 \parallel R_2$, and the true time constant is always shorter than the reflex
  answer, so the circuit is always faster than the wrong calculation predicts.
- **Forgetting where the current comes from at $t = 0$.** The initial current is $V/R$,
  and a real source has to be able to supply it. If it cannot, the output rises in a
  straight line at whatever rate the source can manage and none of the arithmetic above
  applies.

## Where this stops holding

**One storage element, and linear.** $v = V(1 - e^{-t/\tau})$ assumes exactly one
capacitor's worth of memory and a genuinely linear circuit. Two capacitors give a sum of
two exponentials, and the 0.35 rule becomes an approximation rather than an identity.
Cascade several stages and the rise times add roughly in quadrature,
$t_{r,\text{total}} \approx \sqrt{\textstyle\sum t_{r,i}^2}$, which is the form used to
budget a whole measurement chain from probe to display.

**Large signals.** An amplifier driving the filter has a maximum rate at which its own
output can move — its slew rate. While it is slew-limited the output is a straight ramp,
not an exponential, and none of this applies; the exponential resumes only once the
signal is small enough for the circuit to be linear again.

**Real dielectrics.** Discharge a film or electrolytic capacitor completely, disconnect
it, and its voltage creeps back up over the next several seconds. That is dielectric
absorption, and it makes a real capacitor behave like the main $RC$ with a family of much
slower ones hiding behind it. It is invisible in a filter and ruinous in a
sample-and-hold, which is where it is usually discovered.

**Leakage.** A real capacitor leaks, and so does a real probe. Push $R$ up into the tens
of megohms and the leakage current becomes comparable with the charging current, so the
output settles to something short of $V$ and the tail of the exponential stops describing
what the circuit does.
''',
                },
            ],
            "tune": {
                "title": "Keep the signal, lose the interference",
                "minutes": 9,
                "brief": r"""
A corner frequency is never chosen for its own sake. It is chosen because something
below it has to survive and something above it has to go, and the single number you
control has to satisfy both at once.

Here a 100 Hz measurement has to come through almost untouched, while 10 kHz of
switching noise riding on the same wire has to be knocked down by twenty decibels.
Move the corner too low and you flatten the signal; too high and the noise walks
straight through. There is a window, and finding it *is* the design.
""",
                "prompt": "Pass 100 Hz nearly untouched, and put 10 kHz at least 20 dB down.",
                "note": "One corner frequency, two requirements pulling opposite ways.",
                "model": "rc-lowpass",
                "initial": {"r": 1000, "c": 100},
                "constants": {"fsig": 100, "fnoise": 10000},
                "constraints": [
                    {"k": "keep", "label": "\u2265 0.95 of the signal kept at 100 Hz", "min": 0.95},
                    {"k": "reject", "label": "\u2264 \u221220 dB at 10 kHz", "max": -20.0},
                ],
            },
            "sandbox": {
                "title": "Reading a corner off a response curve",
                "visualiser": "bode",
                "minutes": 9,
                "initial": {"wn": 20, "zeta": 0.7, "K": 1},
                "brief": r'''
A **Bode plot**: magnitude in decibels on top, phase in degrees underneath, both
against frequency on a logarithmic axis. This is how every frequency response is
drawn, and reading one is a skill worth ten minutes on its own.

The plant here has two energy stores rather than the one in your RC filter, so the
numbers are doubled — that turns out to make the pattern easier to see, not harder.
The dashed lines mark 0 dB on top and −90° underneath, and the amber dot marks the
gain exactly at the corner.

The sliders are the corner ωₙ in radians per second, the **damping** ζ, which decides
how sharply the curve bends there and whether it overshoots, and K, a plain gain that
multiplies the output at every frequency alike.
''',
                "notice": [
                    "The phase curve crosses the dashed −90° line exactly at ω = ωₙ, whatever ζ is set to. When a magnitude curve bends too gently to place the corner by eye, the phase still tells you where it is.",
                    "The amber dot is the gain at the corner. Take ζ below 0.5 and it climbs above the dashed 0 dB line: at that one frequency the output is bigger than the input, with nothing in the circuit that could amplify. Passive components can do that; only the source supplies energy, and it has to top up nothing more than what the resistor turns into heat.",
                    "Raise K. The magnitude curve shifts bodily upwards and the phase curve does not move at all — a plain gain changes how much, never when.",
                    "Far above the corner the magnitude falls at 40 dB per decade and the phase settles at −180°, because there are two stores. The RC filter you are about to build has one, so it gets half of each: 20 dB per decade and −90°.",
                ],
            },
            "quiz": {
                "title": "Corners, decades and decibels",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A 10 kΩ resistor and a 10 nF capacitor form a low-pass filter. Where is its corner frequency?",
                        "opts": ["10 kHz", "1.59 kHz", "159 Hz", "100 kHz"],
                        "a": 1,
                        "why": r'''
$f_c = 1/(2\pi R C) = 1/(2\pi \times 10^4 \times 10^{-8}) = 1592$ Hz. The product $RC$
is $10^{-4}$ s, so $1/RC = 10\,000$ — and that is where 10 kHz comes from. But
$1/RC$ is an angular frequency in radians per second, not a frequency in hertz;
dividing by $2\pi$ converts it. Whenever an answer comes out as a suspiciously round
number, check whether a $2\pi$ went missing.
''',
                    },
                    {
                        "q": "At exactly the corner frequency, the output amplitude is what fraction of the input?",
                        "opts": ["0.5", "0.707", "0.9", "0.1"],
                        "a": 1,
                        "why": r'''
$1/\sqrt{2} = 0.707$. The corner is defined as the half-*power* point, and power goes
as the square of voltage, so half the power is $\sqrt{0.5} = 0.707$ of the voltage —
not half. In decibels, $20\log_{10}(0.707) = -3.01$, which is the −3 dB you will hear
quoted everywhere. Answering 0.5 means the half-power definition was taken as a
statement about voltage.
''',
                    },
                    {
                        "q": "In a series RC low-pass filter, which component is the output measured across?",
                        "opts": ["The resistor", "The capacitor", "Either — it makes no difference", "Both in turn"],
                        "a": 1,
                        "why": r'''
Across the capacitor. The output is the bottom half of a divider, so it is large when
the impedance you are measuring across is large: the capacitor's reactance
$1/(\omega C)$ is large at low frequency, so low frequencies come through — a
low-pass. Take the same two components and measure across the *resistor* instead and
you have a high-pass, with the same corner frequency. The components do not decide
which it is; where you put the probe does.
''',
                    },
                    {
                        "q": "A first-order low-pass filter has its corner at 1 kHz. Roughly what is the output at 10 kHz, as a fraction of the input?",
                        "opts": ["A half", "A tenth", "A hundredth", "Unchanged"],
                        "a": 1,
                        "why": r'''
A tenth, which is −20 dB. One decade above the corner, $|H| = 1/\sqrt{1 + 10^2}
= 0.0995$, near enough a tenth, and the pattern continues: a hundredth at 100 kHz.
That is what "20 dB per decade" means, and it is the fastest a single resistor and
capacitor can ever roll off. A hundredth at 10 kHz would need two such filters in
cascade.
''',
                    },
                    {
                        "q": "You double both the resistance and the capacitance. What happens to the corner frequency?",
                        "opts": ["It halves", "It quarters", "It doubles", "It is unchanged"],
                        "a": 1,
                        "why": r'''
The corner depends on the product $RC$, and doubling both quadruples the product, so
$f_c = 1/(2\pi RC)$ falls to a quarter of what it was. Answering "halves" is what
happens when only one of the two is doubled. This is worth internalising because it
runs both ways: to move a corner by a factor of ten you can change either component
by ten, or both by about three.
''',
                    },
                    {
                        "q": "You replace a 1 kΩ, 1 µF filter with a 1 MΩ, 1 nF filter. What have you changed?",
                        "opts": [
                            "The corner frequency has moved up by a factor of a thousand",
                            "Nothing at all — the two circuits are identical in every respect",
                            "The corner frequency is the same, but the new filter draws far less current from whatever drives it",
                            "The corner frequency is the same, and the new filter draws far more current",
                        ],
                        "a": 2,
                        "why": r'''
Both have $RC = 10^{-3}$ s, so both corner at 159 Hz. What changed is the impedance
level: the megohm version draws a thousand times less current from the source, which
is often exactly what you want — but it is also a thousand times more easily disturbed
by whatever you connect to its output, and by stray capacitance in the wiring. The
corner is set by the product; the practicality is set by the individual values.
''',
                    },
                ],
            },
            "build": {
                "title": "A low-pass filter with a 1 kHz corner",
                "minutes": 25,
                "brief": r'''
Build the filter the concepts describe, from a source, a ground and a probe.

You are given the source wired straight to the probe, and a ground rail along the
bottom. Add a resistor and a capacitor so that the circuit behaves like this.

1. **At DC the output equals the source.** No current flows in the resistor, because
   the capacitor is an open circuit, so there is no voltage dropped across the
   resistor at all.
2. **The corner sits at 1 kHz**, within 5%. That is the frequency where the output has
   fallen to 0.707 of its low-frequency value.
3. **It rolls off at 20 dB per decade** — at 10 kHz the output is about a tenth of
   what it is at 10 Hz.
4. **The phase at the corner is 45° of lag** relative to the low-frequency phase.

Only the product $RC$ is fixed by the corner, so any sensible pair works.
Something in the region of 1 kΩ to 100 kΩ for the resistor keeps the capacitor a
believable size.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [9, 3]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 1600},
                        {"id": "p3", "kind": "C", "x": 9, "y": 4, "rot": 1, "value": 1e-7},
                        {"id": "p4", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [9, 3]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "checks": [
                    {"name": "at DC the output equals the source", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(Math.abs(c.vout()), vs, 0.01,
  "with the capacitor open at DC no current flows, so nothing is dropped across the resistor");
'''},
                    {"name": "the corner is at 1 kHz", "code": r'''
var fc = c.corner(10, 1e6);
c.close(fc, 1000, 0.05,
  "the corner measured from the response is " + c.fmt(fc, "Hz") + "; adjust the R-C product");
'''},
                    {"name": "it rolls off at 20 dB per decade", "code": r'''
var ratio = c.gain(10000) / c.gain(10);
c.close(ratio, 0.0995, 0.08,
  "a decade above a first-order corner the output should be about a tenth of the pass-band value");
'''},
                    {"name": "the phase at the corner is 45 degrees of lag", "code": r'''
var d = c.phase(1000) - c.phase(1);
while (d > 180) d -= 360;
while (d < -180) d += 360;
c.close(Math.abs(d), 45, 0.06,
  "at the corner the reactance equals the resistance, which puts the output exactly 45 degrees behind");
'''},
                ],
                "hints": [
                    "The resistor goes in series between the source and the output node; the capacitor goes from the output node down to the ground rail.",
                    "Delete the wire between the source and the probe first, so there is somewhere to put the resistor.",
                    "You need $RC = 1/(2\\pi \\times 1000) = 1.59 \\times 10^{-4}$. For example 1.6 kΩ with 100 nF, or 16 kΩ with 10 nF.",
                    "If the corner check reports a huge frequency, the response is flat — the capacitor is probably not connected to ground.",
                ],
            },
            "blanks": [
                {
                    "title": "One filter, six numbers",
                    "minutes": 9,
                    "lang": "text",
                    "caption": "Two component values, and everything the filter does at one frequency.",
                    "brief": r'''
A resistor and a capacitor, and the six quantities anyone would want off them: where the
corner sits, how long the capacitor takes, and — at one chosen frequency — the
reactance, the gain, the gain in decibels and the phase.

Work down the listing in order. Every line after the first two uses the frequency
written above it, not the corner.
''',
                    "listing": r'''
R = 15 kohm     C = 10 nF     output taken across C


    corner frequency                     =  ___ Hz

    time constant                        =  ___ us


with the source set to 2.00 kHz:

    reactance of the capacitor           =  ___ ohm

    |Vout/Vin|                           =  ___

    the same gain in decibels            =  ___ dB

    the phase of the output              =  ___ deg
''',
                    "blanks": [
                        {
                            "prompt": "The corner frequency",
                            "hole": "fc",
                            "opts": ["1061", "6667", "106.1", "10610"],
                            "a": 0,
                            "why": r'''
$f_c = 1/(2\pi RC) = 1/(2\pi \times 15000 \times 10^{-8}) = 1061$ Hz. The value 6667 is
$1/RC$, which is $\omega_c$ in radians per second and not a frequency in hertz — it is
6.28 times too big and it is the single commonest wrong answer in this module. The other
two are the right formula on a capacitor off by a decade: 106.1 Hz would need 100 nF and
10610 Hz would need 1 nF.
''',
                        },
                        {
                            "prompt": "The time constant, in microseconds",
                            "hole": "tau",
                            "opts": ["150.0", "942.5", "15.00", "0.1500"],
                            "a": 0,
                            "why": r'''
$\tau = RC = 15000 \times 10^{-8} = 1.5\times10^{-4}$ s, and the listing asks for
microseconds, so 150.0. The value 942.5 is $2\pi RC$, which is the $2\pi$ applied in the
wrong place — it belongs between $\tau$ and $f_c$, not inside $\tau$ itself. 0.1500 is the
same quantity in milliseconds, right physics and wrong unit. Check it against the line
above: $1/(2\pi \times 150\ \mu\text{s}) = 1061$ Hz, so the first two answers have to be
consistent.
''',
                        },
                        {
                            "prompt": "The capacitor's reactance at 2.00 kHz",
                            "hole": "xc",
                            "opts": ["7958", "50000", "125.7", "15000"],
                            "a": 0,
                            "why": r'''
$X_C = 1/(\omega C) = 1/(2\pi \times 2000 \times 10^{-8}) = 7958$ Ω. The value 50000 Ω is
$1/(fC)$ with the $2\pi$ dropped. 125.7 is $\omega C$ in microsiemens — the susceptance
rather than the reactance, which is the same information the other way up and in the wrong
units for this line. 15000 Ω is the resistor. Note that $X_C$ is below $R$ here, which it
has to be: 2 kHz is above the corner, and above the corner the capacitor is the smaller
of the two.
''',
                        },
                        {
                            "prompt": "The magnitude of the gain at 2.00 kHz",
                            "hole": "h",
                            "opts": ["0.4687", "0.3466", "0.8834", "0.7071"],
                            "a": 0,
                            "why": r'''
$|H| = X_C/\sqrt{R^2 + X_C^2} = 7958/\sqrt{15000^2 + 7958^2} = 7958/16980 = 0.4687$, and
the same number comes out of $1/\sqrt{1 + (f/f_c)^2}$ with $f/f_c = 2000/1061 = 1.885$.
The value 0.3466 is $X_C/(R + X_C)$, the two impedances added as plain numbers — that is
the resistive divider reflex, and it always understates. 0.8834 is $R/\sqrt{R^2 + X_C^2}$,
the voltage across the *resistor* rather than the capacitor. 0.7071 is the gain at the
corner, and 2.00 kHz is not the corner.
''',
                        },
                        {
                            "prompt": "The gain in decibels",
                            "hole": "db",
                            "opts": ["-6.583", "-3.291", "-3.010", "+6.583"],
                            "a": 0,
                            "why": r'''
$20\log_{10}(0.4687) = -6.583$ dB. The value −3.291 is $10\log_{10}$ of the same ratio:
ten belongs to power ratios and twenty to voltage ratios, and using the wrong one halves
every decibel figure you produce. −3.010 dB is the value at the corner, which is where
the gain would be 0.7071. A positive 6.583 dB would mean the output was larger than the
input, which no arrangement of a resistor and a capacitor can manage.
''',
                        },
                        {
                            "prompt": "The phase of the output relative to the input",
                            "hole": "ph",
                            "opts": ["-62.05", "-45.00", "-27.95", "+62.05"],
                            "a": 0,
                            "why": r'''
The gain is $1/(1 + j\omega RC)$, so the phase is $-\arctan(\omega RC) = -\arctan(1.885)
= -62.05^\circ$. It is negative because the output lags: the capacitor cannot move until
charge has arrived through the resistor. −45.00° is the value at the corner. −27.95° is
$62.05 - 90$, which is the angle of the voltage across the *resistor* measured the wrong
way round — the resistor's voltage in fact **leads** by $+27.95^\circ$, and the two are
exactly 90° apart. A positive 62.05° would be the output arriving before the input.
''',
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "Where does this one corner?",
                    "minutes": 5,
                    "brief": r'''
The first rung, and deliberately mechanical: one formula, two numbers off the drawing,
one answer.

The only trap in it is the one that catches everybody once.
''',
                    "prompt": "What is the corner frequency of this filter?",
                    "note": "Give the answer in hertz, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 4700},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 10, "y": 4, "rot": 1, "value": 2.2e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 5], "b": [10, 7]},
                            {"a": [10, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V RMS, frequency swept"},
                        {"label": "Resistor", "value": "4.70 kΩ"},
                        {"label": "Capacitor", "value": "22 nF"},
                    ],
                    "aside": "The source amplitude is not needed. A corner frequency is a property of "
                             "the two components alone — it is the frequency at which the output has "
                             "fallen to 0.707 of whatever it was doing far below.",
                    "answer": 1539.2,
                    "tol": 5.0,
                    "unit": "Hz",
                    # Both values come off the drawing and the corner is measured from the swept
                    # response rather than recomputed, so re-valuing either part moves this number.
                    "check": r'''
c.assert(c.count('R') === 1 && c.count('C') === 1, "one resistor and one capacitor");
return c.corner(1, 1e7);
''',
                    "hint": r"$f_c = 1/(2\pi RC)$. Work out the product $RC$ first, in seconds, and only then divide.",
                    "wrong": r"9671 Hz is $1/RC$, which is $\omega_c$ in radians per second read as though "
                             r"it were hertz — the missing $2\pi$, and the wrong answer that looks tidier "
                             r"than the right one. 1.539 Hz is the same arithmetic with 22 µF in place of "
                             r"22 nF. 103.4 is the time constant in microseconds, which is a time and not "
                             r"a frequency at all.",
                    "why": r'''
```
RC   = 4700 * 22e-9                       = 1.0340e-4 s
f_c  = 1/(2*pi*1.0340e-4)
     = 1/6.4969e-4                        = 1539.2 Hz
```

Two checks worth making a habit. First, $RC$ came out at 103.4 µs, which is a plausible
time for a circuit of this size — kilohms with nanofarads land in the tens to hundreds of
microseconds, and therefore in the low kilohertz. Second, the answer is not a round
number. $1/RC$ would have been 9671, also not round, but the *reason* to distrust a tidy
answer is that the tidy ones usually come from formulas with something missing.

Nothing here depends on the 1.00 V. Halve the source and the output halves with it, so
the frequency at which the output is 0.707 of its low-frequency value does not move.
''',
                },
                {
                    "title": "How much survives at 6 kHz?",
                    "minutes": 7,
                    "brief": r'''
Second rung: the corner is now a stepping stone rather than the destination. Find it,
turn the frequency into a ratio, and put the ratio through the magnitude formula.

Two steps instead of one, and the second is where the square root has to be respected.
''',
                    "prompt": "What RMS voltage does a meter on the probe read at 6.00 kHz?",
                    "note": "Give the answer in volts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 2},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 10000},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 10, "y": 4, "rot": 1, "value": 4.7e-9},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 5], "b": [10, 7]},
                            {"a": [10, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "2.00 V RMS, 6.00 kHz"},
                        {"label": "Resistor", "value": "10.0 kΩ"},
                        {"label": "Capacitor", "value": "4.7 nF"},
                    ],
                    "aside": "The probe sits on the capacitor, so this is the low-pass output. 6 kHz is "
                             "above the corner but not far above it, which is the region where neither "
                             "asymptote is any use and the formula has to be evaluated properly.",
                    "answer": 0.9830,
                    "tol": 0.006,
                    "unit": "V",
                    # The source amplitude and both component values are read from the drawing by the
                    # solver, so the stated answer tracks any edit to the schematic.
                    "check": r'''
c.assert(c.count('V') === 1, "one voltage source, so the reading has something to be relative to");
return c.gain(6000);
''',
                    "hint": r"Find $f_c$ first, then $f/f_c$, then $|H| = 1/\sqrt{1 + (f/f_c)^2}$, and multiply by the source at the very end.",
                    "wrong": r"1.925 V is what you get with the $2\pi$ left out of the corner, which puts "
                             r"the ratio at 0.282 instead of 1.772. 0.7215 V is the divider done on the "
                             r"magnitudes, $X_C/(R + X_C)$, with the right angle between them ignored. "
                             r"1.414 V is the value at the corner, which is 3.39 kHz and not 6 kHz.",
                    "why": r'''
```
RC    = 10000 * 4.7e-9                    = 4.7000e-5 s
f_c   = 1/(2*pi*4.7e-5)                   = 3386.3 Hz

f/f_c = 6000/3386.3                       = 1.7719
|H|   = 1/sqrt(1 + 1.7719^2)
      = 1/sqrt(4.1395)
      = 1/2.0346                          = 0.49150
Vout  = 2.00 * 0.49150                    = 0.98301 V rms
```

Just under half the input, at a frequency just under twice the corner. That pairing is
worth remembering as a landmark: at twice the corner a first-order filter is at
$1/\sqrt5 = 0.447$, or −7.0 dB, and at four times it is at $1/\sqrt{17} = 0.243$. The
20 dB per decade slope has not properly established itself until three or four times the
corner.

The alternative route gives the same number and is sometimes quicker at a single
frequency:

```
X_C   = 1/(2*pi*6000*4.7e-9)              = 5643.5 ohm
|Z|   = sqrt(10000^2 + 5643.5^2)          = 11482 ohm
|H|   = 5643.5/11482                      = 0.49150
```

Note that the two impedances of 10.0 kΩ and 5.64 kΩ combine to 11.5 kΩ, not to 15.6 kΩ.
Anyone who adds them arithmetically gets 0.7215 V and has effectively drawn two resistors.
''',
                },
                {
                    "title": "The voltage the probe cannot see",
                    "minutes": 8,
                    "brief": r'''
Third rung, and the quantity asked for is not the one the probe measures. The resistor's
voltage is a *difference* between two nodes, and the two are not in step, so it cannot be
had by subtracting two meter readings.

There are two clean routes to it. Both are worked below.
''',
                    "prompt": "What RMS voltage would a meter placed across the resistor read at 800 Hz?",
                    "note": "Give the answer in volts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 2200},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 10, "y": 4, "rot": 1, "value": 6.8e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 5], "b": [10, 7]},
                            {"a": [10, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "5.00 V RMS, 800 Hz"},
                        {"label": "Resistor", "value": "2.20 kΩ"},
                        {"label": "Capacitor", "value": "68 nF"},
                    ],
                    "aside": "The probe is on the capacitor, as before. Neither end of the resistor is "
                             "the quantity being asked for: the answer is the difference across it, and "
                             "800 Hz is below this filter's corner, so most of the source is still on "
                             "the capacitor.",
                    "answer": 3.005,
                    "tol": 0.02,
                    "unit": "V",
                    # The check recovers the loop current from the solved capacitor voltage and the
                    # capacitor's own value, then applies Ohm's law with the resistor's own value.
                    # Nothing is restated from the prompt except the frequency.
                    "check": r'''
var f = 800, w = 2 * Math.PI * f;
c.assert(c.count('R') === 1 && c.count('C') === 1, "one resistor in series with one capacitor");
var C = c.values('C')[0], R = c.values('R')[0];
var i = c.gain(f) * w * C;
return i * R;
''',
                    "hint": r"The same current passes through both components. Get the capacitor's voltage first, turn it into a current with $I = V_C \omega C$, then apply Ohm's law to the resistor.",
                    "wrong": r"1.004 V is $5.00 - 3.996$, the two magnitudes subtracted as though they "
                             r"were in step. 3.996 V is the capacitor's voltage — the answer to the "
                             r"question the probe answers, not the one asked. 2.146 V is "
                             r"$5.00 \times R/(R + X_C)$, the divider done on magnitudes.",
                    "why": r'''
```
RC    = 2200 * 68e-9                      = 1.4960e-4 s
f_c   = 1/(2*pi*1.496e-4)                 = 1063.9 Hz
f/f_c = 800/1063.9                        = 0.75197

capacitor first:
  |H|  = 1/sqrt(1 + 0.75197^2)
       = 1/1.25119                        = 0.79924
  V_C  = 5.00 * 0.79924                   = 3.9962 V rms

then the current, and then the resistor:
  I    = V_C * w * C
       = 3.9962 * (2*pi*800) * 68e-9
       = 3.9962 * 3.41805e-4              = 1.3659 mA rms
  V_R  = 1.3659e-3 * 2200                 = 3.0050 V rms
```

The second route skips the current. The resistor's share of the divider is
$R/(R + 1/(j\omega C))$, whose magnitude is

$$\left|\frac{V_R}{V_{in}}\right| = \frac{f/f_c}{\sqrt{1 + (f/f_c)^2}} = \frac{0.75197}{1.25119} = 0.60100$$

so $V_R = 5.00 \times 0.60100 = 3.0050$ V. That expression is worth recognising: it is a
**high-pass**, with exactly the same corner. The same two components measured at the other
end give the complementary filter, which is what module 5 opens with.

Now the point of the exercise. The two readings are 3.9962 V and 3.0050 V, and they sum
to 7.00 V across a 5.00 V source. Nothing is wrong. The two voltages peak a quarter of a
cycle apart, so they combine in quadrature:

```
sqrt(3.9962^2 + 3.0050^2) = sqrt(15.970 + 9.030) = sqrt(25.000) = 5.000 V
```

Kirchhoff's voltage law holds exactly — as phasors, which is the only way it was ever
going to hold. Two meters cannot see the quarter cycle between them, and neither can
arithmetic done on their readings.
''',
                },
                {
                    "title": "A filter with something already hanging on it",
                    "minutes": 10,
                    "brief": r'''
The last rung, and the one that is real work. The output node has a second resistor on
it, so two things are different at once: the low-frequency gain is no longer 1, and the
capacitor no longer charges through the resistor above it alone.

Get those two numbers separately, then combine them. The order matters less than the
discipline of not merging them into one step.
''',
                    "prompt": "What RMS voltage does a meter on the probe read at 3.00 kHz?",
                    "note": "Give the answer in volts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 6800},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "r2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 2200},
                            {"id": "c1", "kind": "C", "x": 12, "y": 4, "rot": 1, "value": 3.3e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [12, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                            {"a": [12, 5], "b": [12, 7]},
                            {"a": [12, 7], "b": [9, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "10.0 V RMS, 3.00 kHz"},
                        {"label": "Upper resistor", "value": "6.80 kΩ"},
                        {"label": "Lower resistor", "value": "2.20 kΩ"},
                        {"label": "Capacitor", "value": "33 nF"},
                    ],
                    "aside": "The lower resistor and the capacitor share both of their ends — the probed "
                             "node above and the ground rail below — so they are in parallel however far "
                             "apart they are drawn. The capacitor is what a load would look like if the "
                             "load were a piece of coaxial cable.",
                    "answer": 1.699,
                    "tol": 0.012,
                    "unit": "V",
                    # All four values and the drive come off the schematic; the probe sits on the only
                    # node between the two resistors, so the AC magnitude there is the answer outright.
                    "check": r'''
c.assert(c.count('R') === 2 && c.count('C') === 1, "two resistors and one capacitor");
return c.gain(3000);
''',
                    "hint": r"Below the corner the capacitor is out of the picture and the two resistors divide on their own — that is $K$. The corner uses the resistance the capacitor *sees*, which is the two resistors in parallel.",
                    "wrong": r"2.444 V is the low-frequency gain with the capacitor ignored altogether — "
                             r"it would be right at 30 Hz and it is nowhere near right at 3 kHz. 1.442 V "
                             r"uses 2.20 kΩ alone for the time constant, which puts the corner at 2192 Hz "
                             r"instead of 2901 Hz and so over-attenuates. 2.301 V is the plain 6.8 kΩ "
                             r"low-pass with the lower resistor left out of the gain.",
                    "why": r'''
```
low-frequency gain:
  K     = R2/(R1 + R2) = 2200/9000        = 0.24444

the resistance the capacitor sees, sources off:
  R1||R2 = 6800*2200/9000                 = 1662.2 ohm
  tau    = 1662.2 * 33e-9                 = 54.853 us
  f_c    = 1/(2*pi*54.853e-6)             = 2901.5 Hz

then the usual first-order magnitude, scaled by K:
  f/f_c = 3000/2901.5                     = 1.0340
  |H|   = 0.24444/sqrt(1 + 1.0340^2)
        = 0.24444/1.43846                 = 0.16994
  Vout  = 10.0 * 0.16994                  = 1.6994 V rms
```

Three things to take from it.

**The shape is unchanged.** Loading a first-order low-pass does not make it something
else; it still has one corner and still rolls off at 20 dB per decade. What changes is the
flat part, which drops from 1 to $K$, and the position of the corner, which moves up.

**The corner moves the "wrong" way.** Adding a resistor to a node makes the circuit
*faster*, because a parallel combination is always smaller than either of its parts. Here
1662 Ω against the 6800 Ω an unloaded filter would have used, so the corner is at 2901 Hz
where the unloaded circuit would have cornered at 709 Hz. Anyone who expects an extra
component to slow things down has the sign of this backwards.

**The same answer, straight through the algebra.** For anyone who prefers not to split it
into $K$ and $f_c$:

```
w     = 2*pi*3000                         = 18850 rad/s
Y2    = 1/2200 + j*18850*33e-9
      = (454.55 + j622.04) uS
Z2    = 1/Y2                              = 765.8 - j1048.0 ohm
Z1+Z2 = 7565.8 - j1048.0                  |.| = 7638.1 ohm
|Z2|                                      = 1298.0 ohm
|H|   = 1298.0/7638.1                     = 0.16994
```

Same number, more arithmetic, and no insight into which resistor did what. The route
through $K$ and $f_c$ is worth the extra line of setup because it tells you what to change
when the answer is not the one you wanted.
''',
                },
            ],
            "derive": {
                "title": "How long the capacitor takes",
                "minutes": 12,
                "vars": ["V", "v", "t", "R", "C", "tau", "A", "e"],
                "brief": r'''
Module 2 derived the impedance and module 3 derived the corner of a loaded divider. Both
were frequency-domain arguments. This is the other half of the same circuit: the step
response, from Ohm's law to the exponential.

No differential equation is solved from scratch. The *shape* of the solution is handed to
you at step three and your job is to fit it to the circuit, which is how these are done
in practice anyway.

Write $V$ for the level the input steps to, $v$ for the output at time $t$, and $e$ for
the base of natural logarithms. The capacitor starts empty.
''',
                "steps": [
                    {
                        "prompt": "At an instant when the output has reached $v$, what current flows in the resistor? Write it in terms of $V$, $v$ and $R$.",
                        "answer": "\\frac{V - v}{R}",
                        "placeholder": "\\frac{\\ldots}{R}",
                        "hint": "One end of the resistor is held at $V$ by the source, the other sits at $v$. Ohm's law on the difference.",
                        "deconstruct": [
                            "The voltage across a component is the difference between its two ends, here $V - v$.",
                            "Ohm's law turns that voltage into a current by dividing by $R$.",
                        ],
                    },
                    {
                        "prompt": "That current has nowhere else to go, so all of it flows into the capacitor, where $i = C\\,dv/dt$. Write $dv/dt$ in terms of $V$, $v$, $R$ and $C$.",
                        "given": "Set the two expressions for the same current equal and divide through by $C$.",
                        "answer": "\\frac{V - v}{RC}",
                        "placeholder": "\\frac{\\ldots}{RC}",
                        "hint": "$C\\,dv/dt = (V - v)/R$, so the $C$ moves down to join the $R$.",
                        "deconstruct": [
                            "The resistor's current and the capacitor's current are the same current, because there is only one path.",
                            "So $C\\,dv/dt = (V - v)/R$.",
                            "Divide both sides by $C$; the two constants gather into a single product $RC$ underneath.",
                        ],
                    },
                    {
                        "prompt": "A quantity whose rate of change is proportional to its distance from a target approaches it exponentially, so try $v = V + A\\,e^{-t/(RC)}$. The capacitor starts empty, so $v = 0$ at $t = 0$. Write $A$.",
                        "given": "$e^0 = 1$, so at $t = 0$ the trial solution is just $V + A$.",
                        "answer": "-V",
                        "placeholder": "\\ldots\\,V",
                        "hint": "Put $t = 0$ into the trial solution, set the result to zero, and solve for $A$.",
                        "deconstruct": [
                            "At $t = 0$ the exponential equals 1, so $v(0) = V + A$.",
                            "An empty capacitor has no voltage across it, so $v(0) = 0$.",
                            "That forces $V + A = 0$.",
                        ],
                    },
                    {
                        "prompt": "Put that $A$ back into the trial solution and write $v(t)$ in terms of $V$, $t$, $R$ and $C$.",
                        "answer": "V\\left(1 - e^{-t/(RC)}\\right)",
                        "placeholder": "V(1 - \\ldots)",
                        "hint": "Substituting gives two terms, and both of them carry a $V$.",
                        "deconstruct": [
                            "Substituting $A = -V$ gives $v = V - V e^{-t/(RC)}$.",
                            "Take the common factor of $V$ outside a bracket.",
                        ],
                    },
                    {
                        "prompt": "Finally, write the *gap* still to be closed, $V - v(t)$, in terms of $V$, $t$, $R$ and $C$.",
                        "answer": "V e^{-t/(RC)}",
                        "placeholder": "V\\,\\ldots",
                        "hint": "Subtract what you just wrote from $V$. The 1 inside the bracket cancels the $V$ outside it.",
                        "deconstruct": [
                            "The gap is $V - V(1 - e^{-t/(RC)})$.",
                            "Expand the bracket: $V - V + V e^{-t/(RC)}$.",
                            "The first two terms cancel.",
                        ],
                    },
                ],
                "closing": r'''
The last line is the one to keep. **The gap decays exponentially, and nothing else does.**
The output itself is an exponential plus an offset, which is a clumsier object; the
distance still to travel is a clean $V e^{-t/RC}$, shrinking by a factor of $e$ every $RC$
seconds no matter where you start counting from.

That immediately gives every number quoted about RC circuits. After one $RC$ the gap is
$1/e = 36.8\%$ of what it was, so the output has covered 63.2%. After three it has covered
95.0%, after five 99.3%. Turned round, reaching a fraction $k$ of the way takes
$t = RC\ln\frac{1}{1-k}$, and the 10% to 90% rise time is
$RC(\ln 10 - \ln(10/9)) = RC\ln 9 = 2.197\,RC$.

Notice what did *not* appear anywhere above: $\omega$, $f$, and any mention of a sinusoid.
This derivation and the impedance derivation in module 2 describe the same two components
and never meet, yet both produce $RC$ and nothing else. That is the reason
$f_c = 1/(2\pi RC)$ and $\tau = RC$ are one fact rather than two, and it is why a
specification can be written in either language and translated freely: $\tau = 1/(2\pi f_c)$.

The step response also says something the frequency response hides. The current at
$t = 0$ is $V/R$, the largest it ever gets, and it is set by the resistor alone. Choose a
100 Ω resistor for a fast corner and a 10 V step will demand 100 mA from whatever is
driving it. The corner frequency does not care which of $R$ and $C$ you shrink; the source
very much does.
''',
            },
            "lab": {
                "title": "The response of the filter you just drew",
                "runtime": "python",
                "minutes": 25,
                "brief": r'''
The same filter, now as three lines of arithmetic.

`corner_hz(r, c)` returns $f_c = 1/(2\pi R C)$ in hertz.

`response(f, r, c)` returns the complex ratio $V_{out}/V_{in}$ of the low-pass
filter at frequency `f`. Written in terms of the corner it is

```text
H = 1 / (1 + 1j * (f / fc))
```

Python writes the imaginary unit as `1j`, and `abs(H)` gives the magnitude of a
complex number while `np.angle(H)` gives its angle in radians.

`gain_db(f, r, c)` returns the magnitude in decibels: $20\log_{10}|H|$.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def corner_hz(r, c):
    """The -3 dB frequency of an R-C low-pass, in hertz."""
    # TODO
    return 0.0


def response(f, r, c):
    """Complex Vout/Vin of the low-pass filter at frequency f."""
    # TODO
    return 0j


def gain_db(f, r, c):
    """Magnitude of the response in decibels."""
    # TODO
    return 0.0


if __name__ == "__main__":
    R, C = 1600.0, 1e-7
    fc = corner_hz(R, C)
    print("corner:", round(fc, 3), "Hz")
    print("gain at the corner:", round(abs(response(fc, R, C)), 6))
    print("dB at the corner:", round(gain_db(fc, R, C), 4))
    print("dB a decade up:", round(gain_db(10 * fc, R, C), 4))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def corner_hz(r, c):
    """The -3 dB frequency of an R-C low-pass, in hertz."""
    return 1.0 / (2.0 * np.pi * r * c)


def response(f, r, c):
    """Complex Vout/Vin of the low-pass filter at frequency f."""
    return 1.0 / (1.0 + 1j * (f / corner_hz(r, c)))


def gain_db(f, r, c):
    """Magnitude of the response in decibels."""
    return 20.0 * np.log10(abs(response(f, r, c)))


if __name__ == "__main__":
    R, C = 1600.0, 1e-7
    fc = corner_hz(R, C)
    print("corner:", round(fc, 3), "Hz")
    print("gain at the corner:", round(abs(response(fc, R, C)), 6))
    print("dB at the corner:", round(gain_db(fc, R, C), 4))
    print("dB a decade up:", round(gain_db(10 * fc, R, C), 4))
'''}],
                "hints": [
                    "`np.pi` is $\\pi$. The corner is one over $2\\pi RC$, so a bracket in the wrong place costs a factor of $4\\pi^2$.",
                    "`response` can call `corner_hz` — writing $f/f_c$ rather than $\\omega R C$ keeps the $2\\pi$ in exactly one place.",
                    "`abs()` on a Python complex number gives its magnitude, so `gain_db` is one call to `np.log10` away.",
                ],
                "tests": [
                    {"name": "the corner of a 1.6 kilohm, 100 nF filter", "code": r'''
_fc = corner_hz(1600.0, 1e-7)
assert abs(_fc - 994.7183943243459) < 1e-6, \
    f"1/(2*pi*1600*1e-7) is 994.718 Hz; got {_fc} (10000 would mean the 2*pi is missing)"
'''},
                    {"name": "only the product of R and C matters", "code": r'''
_a = corner_hz(1e3, 1e-6)
_b = corner_hz(1e6, 1e-9)
assert abs(_a - _b) < 1e-9, f"both have RC = 1 ms, so both corner at the same place: {_a} vs {_b}"
assert abs(_a - 159.15494309189535) < 1e-9, f"expected 159.155 Hz, got {_a}"
'''},
                    {"name": "the response is 0.707 and minus 45 degrees at the corner", "code": r'''
import numpy as np
_fc = corner_hz(1600.0, 1e-7)
_h = response(_fc, 1600.0, 1e-7)
assert abs(abs(_h) - 0.7071067811865475) < 1e-9, f"magnitude at the corner should be 1/sqrt(2), got {abs(_h)}"
assert abs(np.angle(_h) * 180 / np.pi + 45.0) < 1e-9, \
    f"phase at the corner should be -45 degrees, got {np.angle(_h) * 180 / np.pi}"
'''},
                    {"name": "at DC the filter passes everything", "code": r'''
_h = response(0.0, 1600.0, 1e-7)
assert abs(abs(_h) - 1.0) < 1e-12, f"a capacitor is open at DC, so H(0) = 1; got {abs(_h)}"
'''},
                    {"name": "the corner is minus 3 dB and a decade up is minus 20", "code": r'''
_fc = corner_hz(1600.0, 1e-7)
_at = gain_db(_fc, 1600.0, 1e-7)
_up = gain_db(10 * _fc, 1600.0, 1e-7)
assert abs(_at + 3.010299956639812) < 1e-9, f"the corner should be -3.01 dB, got {_at}"
assert abs(_up + 20.043213737826427) < 1e-9, f"a decade above should be -20.04 dB, got {_up}"
'''},
                ],
            },
        },

        # ---- M5 -----------------------------------------------------------
        {
            "title": "High-pass, band-pass, and what cascading costs",
            "summary": "The same resistor and capacitor, probed at the other end; then two filters in a row, and the reason the corners move when you join them.",
            "concepts": [
                "Take the low-pass apart and move the probe. Capacitor first, resistor to ground, output across the resistor: $H = \\dfrac{j\\omega R C}{1 + j\\omega R C}$, magnitude $\\dfrac{f/f_c}{\\sqrt{1 + (f/f_c)^2}}$ with the same corner $f_c = 1/(2\\pi R C)$. This is a **high-pass**. The components did not decide which filter it is; the probe did.",
                "Its phase runs the other way too: $+90°$ far below the corner, $+45°$ at it, $0°$ far above. Every first-order corner is worth 20 dB per decade and 90° of phase — the only question is which direction.",
                "You can read any first-order circuit without algebra. At DC replace each capacitor by an open circuit and each inductor by a wire; far above the corner do the opposite; then look at what the divider has become at each end. If it passes at the bottom and not at the top it is a low-pass, and the corner is where the reactance equals the resistance it works against.",
                "A **band-pass** is a high-pass and a low-pass in series with the high-pass corner well below the low-pass corner. Between the two corners the response is flat; below and above it falls at 20 dB per decade. The gap between the corners is the **bandwidth**.",
                "Two stages in series multiply their responses **only if the second draws no current from the first**. Wiring them together adds exactly one term, $C_2 R_1$, to the denominator, and the product survives while that term stays small beside the largest time constant already there. So the test is $C_2 \\ll C_1$, which is the impedance ratio *and* the corner separation together — never the impedance ratio on its own.",
                "That distinction decides how much margin you actually need. This module's band-pass has its corners two decades apart, and the spacing does most of the work: a second stage a hundred times the impedance of the first is wrong by 0.01% across the whole sweep, and even *equal* impedances are wrong by only about 1%, putting the corners at 97 Hz and 10.3 kHz against the 100 Hz and 10 kHz drawn. Push the corners together and the same ratios bite — two identical stages sharing one corner move the poles to $0.382/\\tau$ and $2.618/\\tau$, nothing like the pair you designed. Loading is not a small print detail, it is the reason cascaded filters are usually buffered: a buffer removes the $C_2 R_1$ term instead of leaving you to argue about how small it is.",
            ],
            "read": [
                {
                    "title": "Move the probe, and the filter changes",
                    "minutes": 12,
                    "body": r'''
Two components, one loop, one source. Module 4 put the meter across the capacitor and
called what it found a low-pass filter. Move the meter to the resistor — nothing
unsoldered, nothing re-valued, the same current still flowing round the same loop — and
the same circuit is a high-pass. It is worth being uncomfortable about that for a
paragraph before the algebra makes it look obvious, because it says what a filter
actually is. Not a property of a bag of components. A property of a bag of components
*and* a decision about which two points you are going to call the output.

## One current, and two voltages that cannot both be large

There is one loop, so there is one current, and it passes through the resistor and the
capacitor in turn. Each component turns that shared current into a voltage, and each does
it by a different rule.

The resistor's rule has no memory: $v_R = iR$, the same constant of proportionality at
every frequency, and the voltage is at its crest at the instant the current is. The
capacitor's rule is $v_C = q/C$, and the charge $q$ is the *accumulated* current, so what
matters is how long the current has been flowing in one direction before it turns round.
At a low frequency it flows the same way for a long time, piles up a lot of charge, and
develops a large voltage. At a high frequency it reverses before much has accumulated and
the voltage stays small. Module 2 compressed that whole story into one number — the
reactance $|Z_C| = 1/(\omega C)$, enormous at low frequency, negligible at high.

Now the constraint that makes this section work. Kirchhoff's voltage law says the two
component voltages must add up to the source. As phasors, with the quarter-cycle between
them respected — but the crude size argument survives that caveat intact: if the capacitor
is taking almost all of the source, there is almost nothing left for the resistor, and the
other way round. **The two voltages cannot both be large, and they cannot both be small.**

So of the two available outputs, one must fall as frequency rises and the other must rise.
Which is which is settled by the reactance. At DC the capacitor's reactance is infinite,
it takes the whole source, and the resistor is left with nothing. Far above the corner the
capacitor is nearly a piece of wire, it takes nothing, and the resistor sees the whole
source. That is a high-pass, described completely, without a formula anywhere in it. All
the formula will do is fill in the shape of the crossover between those two ends.

## The divider, written down

The impedance divider is the same one module 3 built, with the two impedances swapped
about so the resistor is the one being measured:

$$H(j\omega) = \frac{V_{out}}{V_{in}} = \frac{Z_R}{Z_R + Z_C} = \frac{R}{R + \dfrac{1}{j\omega C}}$$

Multiply top and bottom by $j\omega C$ — the single manipulation that turns this into
something readable:

$$H(j\omega) = \frac{j\omega R C}{1 + j\omega R C}$$

Compare it with the low-pass, $1/(1 + j\omega RC)$. Same denominator. The numerator has
gained a factor of $j\omega RC$, and that factor is doing everything: it vanishes at
$\omega = 0$, it grows in proportion to frequency while the denominator is still about 1,
and it eventually matches the denominator term for term, so the ratio settles at 1.

Write $x = f/f_c$ with $f_c = 1/(2\pi RC)$ and the two useful pieces fall out:

$$|H| = \frac{x}{\sqrt{1 + x^2}} \qquad \angle H = 90^\circ - \arctan x$$

At $x = 0.1$ the magnitude is $0.1/\sqrt{1.01} = 0.0995$, a tenth, and the phase is
$+84.3^\circ$. At $x = 1$ it is $1/\sqrt2 = 0.7071$ and $+45^\circ$. At $x = 10$ it is
$10/\sqrt{101} = 0.9950$ and $+5.7^\circ$. A decade below the corner the output is a tenth
of the input and a decade above it is within half a per cent of all of it — the same
20 dB per decade and the same 90° of phase as the low-pass, pointing the other way.

**The corner has not moved.** $f_c$ is still $1/(2\pi RC)$, and it has to be, because the
corner is the frequency at which the two impedances are equal in size, $|Z_C| = R$, and
that condition never mentions where the probe is. Moving the probe changes which half of
the divider you are looking at. It cannot change where the two halves are the same size.

## Choosing a coupling capacitor

The commonest use of a first-order high-pass is to pass a signal into an amplifier while
refusing to pass the steady voltage it is sitting on. The capacitor is in series, the
amplifier's input resistance is the resistor to ground, and the two together set a corner
that the wanted signal has to sit above.

Suppose the stage you are driving looks like 22 kΩ, and the specification is **no more
than 1 dB of loss at 40 Hz**.

```
1 dB down means |H| = 10^(-1/20)          = 0.89125
solve x/sqrt(1+x^2) = 0.89125 for x:
   x^2 = h^2/(1 - h^2) = 0.79432/0.20568  = 3.8622
   x                                      = 1.9652
so the corner must be at or below
   f_c = 40/1.9652                        = 20.354 Hz
C     = 1/(2*pi*22000*20.354)             = 3.5543e-7 F = 0.355 uF
```

There is no 0.355 µF capacitor, so the choice is between the two standard values either
side. Check both rather than guessing:

```
C = 0.33 uF:  RC  = 22000*3.3e-7          = 7.260 ms
              f_c = 1/(2*pi*7.26e-3)      = 21.922 Hz
              x   = 40/21.922             = 1.82464
              |H| = 1.82464/sqrt(1 + 3.32931)
                  = 1.82464/2.08070       = 0.87694   -> -1.14 dB   FAILS

C = 0.47 uF:  RC  = 22000*4.7e-7          = 10.34 ms
              f_c = 1/(2*pi*1.034e-2)     = 15.392 Hz
              x   = 40/15.392             = 2.59873
              |H| = 2.59873/sqrt(1 + 6.75338)
                  = 2.59873/2.78449       = 0.93329   -> -0.60 dB   PASSES
```

0.33 µF misses by 0.14 dB, which is inaudible and still outside the budget you were given;
0.47 µF has 0.4 dB in hand. Note how weak the dependence is — a 42% increase in
capacitance bought 0.54 dB. Below the corner the response is falling at 20 dB per decade,
but at 2.6 times the corner you are on the flat part, where large changes in $f_c$ buy
very little. That asymmetry is why coupling capacitors are usually specified with a corner
several times below the lowest wanted frequency and then forgotten about.

## One measurement, one unknown component

The same formula run backwards is how a component gets identified on a bench.

A high-pass has a 10.0 kΩ resistor and a capacitor of unknown value. Driven with 2.000 V
RMS at 500 Hz, a meter on the resistor reads 599.4 mV. What is the capacitor?

```
|H|   = 0.5994/2.000                      = 0.29972
x^2   = |H|^2/(1 - |H|^2)
      = 0.089832/0.910168                 = 0.098699
x                                         = 0.31416
f_c   = f/x = 500/0.31416                 = 1591.5 Hz
C     = 1/(2*pi*10000*1591.5)             = 1.0000e-8 F = 10.0 nF
```

Two things to notice. The step from $|H|$ to $x$ is where the square root has to be
undone properly: the tempting shortcut of reading $|H| \approx x$ because the output is
small is only good to a per cent or so here, and it gets worse fast — it would give
$f_c = 500/0.29972 = 1668$ Hz and a capacitor of 9.54 nF, a 5% error from a step that
looked free. And the measurement is at a frequency below the corner *on purpose*. Above
the corner the response is flat, so a reading there is nearly independent of $C$ and tells
you almost nothing; the sensitive place to measure is on the slope.

## The mistake, and why it is tempting

The mistake is believing the components choose the filter. It is tempting because in most
circuits you meet, they do — the output node is drawn on the right, and whatever sits
between it and ground is what you get, so "series capacitor, shunt resistor" and
"high-pass" arrive together often enough to fuse. The fusion breaks the first time you
meet the same two parts drawn the other way up, or a circuit where the interesting node is
in the middle of a chain rather than at the end.

A cheap habit stops it: before saying what a circuit does, say **where the probe is**, out
loud, and then ask what the probed node is connected to at DC and at high frequency. Two
sentences, and they cannot be got wrong the way a remembered pattern can.

The second mistake is arithmetic, and it is the one this course keeps coming back to. At
the corner the resistor has 0.707 of the source and the capacitor has 0.707 of it, and
those do not sum to 1.000. They sum in quadrature, because the two voltages peak a quarter
of a cycle apart: $\sqrt{0.7071^2 + 0.7071^2} = \sqrt{0.5 + 0.5} = 1.000$. Squares add
even when magnitudes do not, and that is exactly true at every frequency, not just at the
corner:

$$|H_{LP}|^2 + |H_{HP}|^2 = \frac{1}{1 + x^2} + \frac{x^2}{1 + x^2} = 1$$

Which is a nice thing to know for its own sake. The two outputs of an RC pair are
complementary in *power*: whatever fraction of the available power one of them is not
passing, the other one is.

## Where the idea stops holding

Everything above assumes two ideal components and a source that does not care what it is
driving. Three things break it in practice, in the order you meet them.

**The source has an output resistance**, and in a high-pass it is in series with the
capacitor, so it adds to $R$ in the loop and drags the corner *down*. Driving a 1 kΩ
high-pass from a source with 600 Ω of its own is a 1.6 kΩ circuit, and its corner is at
$1/(2\pi \times 1600C)$, a factor of 1.6 below where you drew it.

**The load is in parallel with the resistor**, and a parallel combination is always
smaller than either part, so a load raises the corner. Both effects are first-order and
neither is subtle; they are simply left out of the two-component picture, and module 3's
rule — the corner is set by the resistance the capacitor actually *sees* — is what puts
them back in.

**Real capacitors stop being capacitors.** Every one has some series resistance and some
series inductance from its own leads and plates. The inductance means that above a
self-resonant frequency the part is an inductor, and the "high-pass" starts falling again.
A 100 nF ceramic with 10 nH of lead inductance resonates at

```
f = 1/(2*pi*sqrt(1e-8 * 1e-7)) = 1/(2*pi*3.1623e-8) = 5.03 MHz
```

which is well inside the range of things people put audio through. And in a coupling
application where the load is small — a 10 µF electrolytic feeding an 8 Ω loudspeaker, say
— an equivalent series resistance of 1 Ω is 12% of the load and shows up as a flat loss
across the whole band, not as a corner at all. Neither effect is a reason to distrust
$j\omega RC/(1 + j\omega RC)$. They are a reason to know which of its assumptions you are
leaning on.
''',
                },
                {
                    "title": "Reading a circuit at the two ends of the frequency axis",
                    "minutes": 12,
                    "body": r'''
There is a way of answering "what does this circuit do" that takes about ten seconds, uses
no algebra, and is right nearly all of the time for a circuit with one capacitor or one
inductor in it. It is worth more than the transfer function, because you can do it while
someone is still drawing the circuit, and because it tells you what the algebra *should*
come out as, which is how you catch an algebra slip.

## Two substitutions

Everything rests on the two reactances and what they do at the ends of the frequency axis.

$$|Z_C| = \frac{1}{\omega C} \qquad |Z_L| = \omega L$$

At $\omega \to 0$ the capacitor's reactance goes to infinity and the inductor's goes to
zero. At $\omega \to \infty$ they swap. So:

| | at DC | far above the corner |
|---|---|---|
| capacitor | open circuit | short circuit (a wire) |
| inductor | short circuit (a wire) | open circuit |

Every entry is the other component's entry reversed, which is the fastest way to keep the
table straight. And both of them have a physical sentence behind them, which is better
than a remembered table. A capacitor is two plates that do not touch: no steady current
can cross the gap, so at DC it is a break in the wire. An inductor is a coil of wire: to a
current that is not changing it is exactly what it looks like, a piece of wire, because
there is nothing changing for the magnetic field to oppose.

## The procedure

Draw the circuit twice. In the first copy replace every reactive component by its DC
substitution; in the second, by its high-frequency one. In each copy the circuit is now
nothing but resistors, and you can read the gain from the probed node straight off. Then:

- gain 1 at DC, gain 0 up high: **low-pass**
- gain 0 at DC, gain 1 up high: **high-pass**
- 0 at both ends, something in the middle: **band-pass**
- nonzero at both ends, and unequal: a **shelf** — it changes level rather than switching
  off, and there is a corner at each end of the step
- 1 at both ends: either nothing is happening, or there is a **notch** somewhere in
  between that the two ends cannot see

Then the corner, which module 4 gave in the only form that generalises: the corner is
where the reactance equals **the resistance that reactive component actually works
against** — the resistance you would measure at its own two terminals with the sources
turned off. For a lone series resistor and shunt capacitor that is just $R$, and
$f_c = 1/(2\pi RC)$. For an inductor it is $\omega L = R$, so $f_c = R/(2\pi L)$: a ratio,
not a product, so an inductive circuit gets *faster* as the resistance rises while an RC
circuit gets slower.

## Worked: a circuit with no capacitor in it

A 470 Ω resistor in series from the source; a 10 mH inductor from the output node down to
ground; the probe on the inductor.

At DC the inductor is a wire, so the probe is wired to ground and the gain is 0. Far above
the corner the inductor is an open circuit, so no current flows, so nothing is dropped
across the resistor and the probe sees the whole source: gain 1. Nothing at the bottom,
everything at the top — **a high-pass**, built out of parts that contain no capacitor at
all. The corner is where $\omega L = R$:

```
f_c = R/(2*pi*L) = 470/(2*pi*0.01)
    = 470/0.062832                        = 7480.3 Hz
```

Check it at some frequency in between, say 2.00 kHz, using the same magnitude expression
as the RC high-pass, because it *is* the same expression:

```
x   = 2000/7480.3                         = 0.26737
|H| = 0.26737/sqrt(1 + 0.071487)
    = 0.26737/1.03513                     = 0.25830
```

and the same answer the long way, as a divider on impedances, to show they agree:

```
X_L = 2*pi*2000*0.01                      = 125.66 ohm
|Z| = sqrt(470^2 + 125.66^2)
    = sqrt(220900 + 15791)                = 486.51 ohm
|H| = 125.66/486.51                       = 0.25830
```

The inductor's 125.66 Ω and the resistor's 470 Ω combine to 486.51 Ω rather than to
595.66 Ω, for the same reason as always: the two voltages are a quarter of a cycle apart,
so the sizes add in quadrature.

## The band-pass

Put a high-pass and a low-pass in a row, with the high-pass corner well below the low-pass
corner, and the two ends of the frequency axis are both zero. Below $f_1$ the high-pass
section is switching off; above $f_2$ the low-pass section is; in between neither of them
is doing much and the signal goes through. Only one of the two is ever really working at
any given frequency, which is what makes a band-pass so easy to sketch.

Take $f_1 = 100$ Hz and $f_2 = 10$ kHz, and evaluate the product of the two first-order
magnitudes:

```
  f        high-pass    low-pass     product      dB
  20 Hz     0.19612      1.00000     0.19612    -14.15
 100 Hz     0.70711      0.99995     0.70707     -3.01
   1 kHz    0.99504      0.99504     0.99010     -0.09
  10 kHz    0.99995      0.70711     0.70707     -3.01
 100 kHz    1.00000      0.09950     0.09950    -20.04
   1 MHz    1.00000      0.01000     0.01000    -40.00
```

Two decades below the lower corner and two above the upper one, the response is 40 dB
down — a hundredth — because one section is rolling off at 20 dB per decade over two
decades and the other is doing nothing at all.

Look at the middle row. The best this filter ever manages is 0.99010, not 1. Each section
is still 0.5% down at the other's corner, and the two losses multiply. There is a tidy
closed form for it: the peak sits at the geometric mean $\sqrt{f_1 f_2}$ — here exactly
1 kHz — and its value is

$$|H|_{max} = \frac{f_2}{f_1 + f_2} = \frac{1}{1 + f_1/f_2}$$

which is $1/1.01 = 0.99010$. The wider apart the corners, the closer to 1 it gets.

## Where the -3 dB points really are

Here is a detail that catches people who have been designing filters for years. The
composite is 3 dB down **not** at 100 Hz and 10 kHz, because "3 dB down" means 3 dB below
the passband, and the passband is 0.99010 rather than 1. At 100 Hz the response is 0.70707,
which is $0.70707/0.99010 = 0.71414$ of the peak — that is 2.92 dB down, not 3.01.

The true $-3$ dB points of the cascade satisfy something clean. Writing $u = f^2$, the
squared magnitude is $u f_2^2/((f_1^2 + u)(f_2^2 + u))$, and setting that to half its
maximum gives a quadratic in $u$ whose two roots multiply to $(f_1f_2)^2$ and sum to
$f_1^2 + f_2^2 + 4f_1f_2$. So the two $-3$ dB frequencies $f_a$ and $f_b$ obey

$$f_a f_b = f_1 f_2 \qquad\text{and}\qquad f_b - f_a = f_1 + f_2$$

both exactly. For 100 Hz and 10 kHz that puts them at 98.06 Hz and 10198.06 Hz: a
bandwidth of 10.1 kHz, not 9.9 kHz, and each corner about 2% outside where it was drawn.
Nobody cares at two decades of separation. It matters enormously when the separation
shrinks, which is the next paragraph.

## Where this stops holding

Push the two corners together and "band-pass with corners at $f_1$ and $f_2$" stops being
a description of anything. Take $f_1 = 1$ kHz and $f_2 = 2$ kHz — an octave apart, which
still sounds like a filter specification a person might write down:

```
peak      = 1/(1 + 1000/2000)             = 0.66667   (-3.52 dB) at sqrt(2e6) = 1414 Hz
at 1 kHz  = 0.70711 * 0.89443             = 0.63246
          = 0.63246/0.66667 of the peak   = 0.94868   (-0.46 dB)
-3 dB pts:  f_b - f_a = 3000, f_a f_b = 2e6
          -> f_a = 561.6 Hz, f_b = 3561.6 Hz
```

The filter never gets within 3.5 dB of unity anywhere. Its nominal corners are less than
half a decibel down rather than three. Its actual bandwidth is 3.0 kHz — three times the
1 kHz band that was asked for. Every number in the specification has become misleading at
once, and the circuit is not faulty; the description was.

The rule that falls out of it: **two first-order sections describe a band-pass usefully
only when their corners are at least a decade apart.** Closer than that and you are
building a second-order filter and should describe it as one, with a centre frequency and
a $Q$ — which is modules 7 and 8.

Two other places where the ten-second reading gives out. It cannot see a **notch or a
resonance**, because those are things that happen strictly between the two ends, and the
substitutions only look at the ends; a series LC across a signal path looks like an open
circuit at DC and an open circuit up high and yet is a dead short at one frequency in the
middle. And it says nothing about **phase**, which is often the quantity that matters —
a circuit can be flat to a fraction of a decibel across a band and still be swinging its
output through 90° across that same band.
''',
                },
                {
                    "title": "What it costs to wire one filter onto the other",
                    "minutes": 13,
                    "body": r'''
A high-pass has a transfer function. A low-pass has a transfer function. Wire the output
of the first to the input of the second and the cascade's transfer function is the product
of the two — except that it is not, and the reason is worth more than the result.

## Multiplying is a claim about independence

$H_1$ was calculated for a high-pass with nothing hanging on its output. It says: apply
this input, get that output. The moment you connect a second circuit to that node, the
second circuit starts drawing current out of it, and current out of a node is exactly what
the first calculation assumed there was none of. The output of stage one is no longer what
$H_1$ says it is, so multiplying $H_1$ by $H_2$ is multiplying a number that has stopped
being true.

The picture to hold is not "two blocks in a signal chain". It is: **stage two's input
impedance is now a component in stage one's circuit**, sitting in parallel with whatever
stage one had at its output. That is why the loading question is not an approximation
issue but a topology issue.

## The one extra term

Take the module's band-pass: source, then $C_1$ in series, $R_1$ to ground — that is the
high-pass. Then $R_2$ in series to the output node, and $C_2$ from there to ground — that
is the low-pass. Writing $s = j\omega$, solving the two node equations gives

$$H(s) = \frac{s C_1 R_1}{s^2 C_1C_2R_1R_2 + s\,(C_1R_1 + C_2R_2 + C_2R_1) + 1}$$

The derivation unit in this module walks that algebra line by line. Compare it with what
you would have got by multiplying:

$$H_1 H_2 = \frac{sC_1R_1}{(1 + sC_1R_1)(1 + sC_2R_2)}
        = \frac{sC_1R_1}{s^2 C_1C_2R_1R_2 + s\,(C_1R_1 + C_2R_2) + 1}$$

The numerators are identical. The $s^2$ terms are identical. The whole of the difference is
**one extra term, $C_2R_1$, in the coefficient of $s$** — and there is a physical sentence
for it that saves the algebra entirely.

Ask what resistance each capacitor charges through, with the source shorted and the *other*
capacitor removed. $C_1$ sits between the source and the middle node, and with $C_2$ gone
no current can reach $R_2$, so $C_1$ charges through $R_1$ alone: $C_1R_1$. But $C_2$ sits
between the output and ground, and with $C_1$ gone its charging current has to come up
through $R_2$ *and then through $R_1$ to reach the ground rail*, so it charges through
$R_1 + R_2$: that is $C_2R_2 + C_2R_1$. Add the two and you have the $s$ coefficient
exactly. It is a general result for this kind of network — the coefficient of $s$ in the
denominator is the sum of every capacitor's time constant computed with all the others
open-circuited — and it is often the fastest honest route to a first-order estimate of a
messy circuit's bandwidth.

## What the extra term actually does

Two exact consequences, and they are more useful than any rule of thumb.

**The product of the two pole frequencies never changes.** The $s^2$ coefficient carries
all of the information about the product of the roots, and loading does not touch it. So
however badly the corners move, $f_a f_b = f_1 f_2$ always. Loading slides the two poles
apart along a hyperbola; it does not shift the band as a whole.

**The peak gain is exactly $\tau_1/(\tau_1 + \tau_2 + C_2R_1)$**, where $\tau_1 = C_1R_1$
and $\tau_2 = C_2R_2$. Divide top and bottom by $\tau_1$ and the third term becomes
$C_2R_1/C_1R_1 = C_2/C_1$:

$$|H|_{max} = \frac{1}{1 + \dfrac{\tau_2}{\tau_1} + \dfrac{C_2}{C_1}}
            \qquad\text{against the ideal}\qquad
            \frac{1}{1 + \dfrac{\tau_2}{\tau_1}}$$

There is the rule, derived rather than asserted: the entire penalty for wiring the stages
together is the capacitor ratio $C_2/C_1$, sitting in the denominator next to the corner
ratio $\tau_2/\tau_1 = f_1/f_2$ that was going to be there anyway. **The test is
$C_2 \ll C_1$.** Not $R_2 \gg R_1$, which is only part of it, because

$$\frac{C_2}{C_1} = \frac{\tau_2}{\tau_1}\cdot\frac{R_1}{R_2} = \frac{f_1}{f_2}\cdot\frac{R_1}{R_2}$$

The corner separation and the impedance ratio multiply. Widely spaced corners do half the
work for free, which is why the same impedance ratio can be perfectly safe in one design
and catastrophic in another.

## Three cases, with the numbers

**A light load.** The module's build: $R_1 = 1$ kΩ, $C_1 = 1.59$ µF, and a low-pass a
hundred times the impedance, $R_2 = 100$ kΩ with $C_2 = 159$ pF.

```
tau_1 = 1000 * 1.59e-6                    = 1.590 ms      -> f_1 = 100.1 Hz
tau_2 = 100000 * 1.59e-10                 = 15.90 us      -> f_2 = 10.01 kHz
C_2/C_1 = 1.59e-10/1.59e-6                = 1.0e-4
peak  = 1/(1 + 0.01 + 0.0001)             = 0.99000
ideal = 1/(1 + 0.01)                      = 0.99010
```

A relative error of 0.01% at the peak, and the lab in this module sweeps five decades and
finds nothing worse anywhere. Its $-3$ dB points land at 98.14 Hz and 10.21 kHz, against
the 98.06 Hz and 10.20 kHz the ideal product would have given.

**A load equal to the source.** $R_1 = R_2 = 4.7$ kΩ, $C_1 = 33$ nF, $C_2 = 3.3$ nF, so
the corners are one decade apart at 1026 Hz and 10.26 kHz.

```
tau_1 = 4700*33e-9                        = 155.1 us
tau_2 = 4700*3.3e-9                       = 15.51 us
C_2R_1 = 3.3e-9*4700                      = 15.51 us      <- as large as tau_2
C_2/C_1 = 3.3e-9/33e-9                    = 0.1

peak  = 1/(1 + 0.1 + 0.1)                 = 0.83333
ideal = 1/(1 + 0.1)                       = 0.90909      -> 8.3% low

denominator: a = tau_1*tau_2              = 2.4056e-9
             b = 155.1+15.51+15.51 us     = 186.12 us
poles = (-b +/- sqrt(b^2 - 4a))/(2a)
      = -5809 and -71559 rad/s
      -> 924.5 Hz and 11.39 kHz  (against 1026 Hz and 10.26 kHz drawn)
```

An 8% loss in the middle and 10% shifts in both corners, from a stage whose impedance
"matched" the one before it. Notice the invariant holding underneath all that movement.
Multiply the two real corners: $924.5 \times 11390 = 1.0530\times10^7$. Multiply the two
designed ones: $1026 \times 10261 = 1.0530\times10^7$. The poles moved apart; their
geometric mean did not budge.

**Two identical stages.** The case that gets people, because it looks like the obvious way
to make a filter sharper. Set $R_1 = R_2 = R$ and $C_1 = C_2 = C$, so both sections corner
at the same $f_c = 1/(2\pi\tau)$ with $\tau = RC$. Now $\tau_1 = \tau_2 = C_2R_1 = \tau$
and the denominator is $s^2\tau^2 + 3s\tau + 1$:

```
peak  = 1/(1 + 1 + 1)                     = 0.33333    (the ideal product says 0.5)
roots of  p^2 + 3p + 1 = 0  in p = s*tau:
      p = (-3 +/- sqrt(5))/2              = -0.38197, -2.61803
```

So two sections each cornering at 1 kHz produce a filter whose corners are at 382 Hz and
2618 Hz, with a peak of a third rather than a half. Those two numbers are $1/\varphi^2$
and $\varphi^2$ for the golden ratio, which is a curiosity rather than a fact you need,
but they are memorable and they are nothing like 1 and 1.

## The fix

Put a buffer between the stages — an op-amp wired as a follower is the usual one. Its
input draws essentially no current, so stage one sees no load; its output impedance is
milliohms, so in the extra term $C_2R_1$ the $R_1$ is replaced by something near zero and
the term is gone rather than merely small. That is a categorical improvement over arguing
about ratios, and it is why almost every multi-stage filter you meet in a real design has
active devices between its sections.

It is not free: a device, a supply rail, its own noise, its own finite bandwidth, and an
output impedance that stops being milliohms somewhere up the frequency axis. For a
two-section passive band-pass with corners two decades apart, a 10:1 or 100:1 impedance
step between stages is cheaper and entirely adequate — as the first case above shows.

## Where this stops holding

The clean single extra term belongs to *this* topology and two stages. Cascade three RC
sections and there are cross terms between every pair, not one; the $s$ coefficient becomes
a sum of five open-circuit time constants and the $s^2$ and $s^3$ coefficients pick up
their own corrections. The open-circuit sum is still exact for the $s$ coefficient, which
is what makes it worth knowing, but the rest of the denominator is not something you can
patch a product with.

And loading is not always a loss. The formulae above assume the second stage is a passive
RC network; if it contains an inductor, or an amplifier with gain, the extra term can have
either sign and the poles can move together rather than apart — which, taken deliberately,
is how a two-section network is turned into a resonator. That is module 7. Here the only
claim being made is the narrow one: **for two passive RC sections wired directly together,
the ideal product is wrong by exactly the capacitor ratio, and everything else follows from
that one number.**
''',
                },
            ],
            "quiz": {
                "title": "Which way round is it?",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A resistor and a capacitor are in series, and the output is measured across the resistor. What is this circuit?",
                        "opts": [
                            "A low-pass, cornering at $1/(2\\pi R C)$",
                            "A high-pass, cornering at $1/(2\\pi R C)$",
                            "A high-pass, cornering at $R/(2\\pi C)$",
                            "Neither — where the probe goes cannot change the response",
                        ],
                        "a": 1,
                        "why": r'''
A high-pass, with exactly the same corner as the low-pass built from the same two
components. At low frequency the capacitor's reactance is enormous and takes nearly
all of the source voltage, leaving nothing across the resistor; at high frequency it
is a wire and the resistor gets everything. The corner is still where the reactance
equals the resistance, which is still $1/(2\pi R C)$ — moving the probe changes which
half of the divider you are looking at, never where the two halves are equal.
''',
                    },
                    {
                        "q": "A first-order high-pass has its corner at 1 kHz. Roughly what fraction of the input appears at the output at 10 Hz?",
                        "opts": ["A tenth", "A hundredth", "A thousandth", "Almost all of it"],
                        "a": 1,
                        "why": r'''
A hundredth. 10 Hz is two decades below the corner, and a first-order filter changes
by a factor of ten per decade, so two decades is a factor of a hundred — which is
$-40$ dB. Exactly, $|H| = 0.01/\sqrt{1 + 0.01^2} = 0.00999995$. A thousandth would
need three decades, or a second-order filter over two.
''',
                    },
                    {
                        "q": "When reading a circuit by inspection, what should a capacitor and an inductor be replaced by at DC?",
                        "opts": [
                            "Capacitor: a short. Inductor: an open circuit.",
                            "Capacitor: an open circuit. Inductor: a short.",
                            "Both by an open circuit.",
                            "Both by a short.",
                        ],
                        "a": 1,
                        "why": r'''
At DC a capacitor's reactance $1/(\omega C)$ is infinite and an inductor's $\omega L$
is zero, so the capacitor is a break in the wire and the inductor is a piece of wire.
Far above the corner both statements reverse. Those four substitutions, plus a look at
what the divider has become at each end, will tell you what any first-order circuit
does before you write a single line of algebra — and they are quick enough to do while
someone is still describing the circuit to you.
''',
                    },
                    {
                        "q": "A high-pass and a low-pass are wired directly one after the other. When is the overall response simply the product of the two responses?",
                        "opts": [
                            "Always — cascaded blocks always multiply",
                            "Only when the second stage draws negligible current from the first",
                            "Only when the two corners are within a decade of each other",
                            "Only at frequencies between the two corners",
                        ],
                        "a": 1,
                        "why": r'''
Only when the second stage is a light enough load that the first stage's output is
what it would have been on its own. Multiplying responses is a statement about two
independent blocks, and two circuits soldered together are not independent — the
second one's input impedance sits in parallel with the first one's output and drags
the first one's corner about. The usual fix is to make the second stage's impedance
much larger, or to put a buffer between them so the question does not arise. How much
larger is "much" depends on how far apart the two corners are, and widely spaced
corners are the easy case, not the hard one — so "only when the two corners are within
a decade of each other" has the dependence backwards as well as being the wrong
condition.
''',
                    },
                    {
                        "q": "A band-pass has corners at 100 Hz and 10 kHz, one first-order section at each end. Roughly what does it do to a 1 MHz signal?",
                        "opts": [
                            "Passes it — 1 MHz is well above the high-pass corner",
                            "Attenuates it by about 40 dB",
                            "Attenuates it by about 100 dB",
                            "Passes it at 0.707 of the input",
                        ],
                        "a": 1,
                        "why": r'''
1 MHz is two decades above the 10 kHz corner, and the low-pass section rolls off at
20 dB per decade, so the signal comes out about a hundredth of its size: $-40$ dB. The
high-pass section is doing nothing up there — being above its corner is exactly the
condition for passing. Only one of the two sections is ever working at a given
frequency, which is what makes a band-pass easy to sketch.
''',
                    },
                    {
                        "q": "How does the phase of a first-order high-pass behave as the frequency rises through its corner?",
                        "opts": [
                            "From $+90°$ well below, through $+45°$ at the corner, to $0°$ well above",
                            "From $0°$ well below, through $-45°$ at the corner, to $-90°$ well above",
                            "It is $0°$ at every frequency",
                            "It is $+90°$ at every frequency",
                        ],
                        "a": 0,
                        "why": r'''
$H = j\omega RC/(1 + j\omega RC)$. Far below the corner the denominator is nearly 1 and
the numerator is nearly pure $j$, which is a quarter cycle of lead; far above, both the
numerator and the denominator are dominated by the same $j\omega RC$, so the ratio
tends to 1 and there is no shift at all. The
run from $0°$ down to $-90°$ belongs to the low-pass. Both cover 90°, in opposite
directions, which is the phase half of "20 dB per decade, whichever way it points".
''',
                    },
                ],
            },
            "build": {
                "title": "A band-pass from 100 Hz to 10 kHz",
                "minutes": 26,
                "brief": r'''
Half of this is already drawn.

You are given a high-pass: a 1.59 µF capacitor in series from the source, a 1 kΩ
resistor from that node to ground, and the probe wired straight across to the right.
Its corner is at $1/(2\pi \times 1000 \times 1.59\,\mu\text{F}) = 100$ Hz. Below that
frequency it stops things; above it, it passes everything, all the way up.

Add a low-pass stage after it so that the circuit becomes a band-pass with corners at
**100 Hz and 10 kHz**.

1. **Still nothing at DC**, as before.
2. **The middle of the band comes through nearly untouched** — at 1 kHz the output is
   about 99% of the source.
3. **The lower corner is at 100 Hz**: the output there is 0.707 of the mid-band level.
4. **The upper corner is at 10 kHz**, by the same measure.
5. **At 1 MHz almost nothing is left** — two decades past the upper corner.

One warning, which is the point of the exercise. The low-pass stage loads the
high-pass stage: wiring the two together adds a $C_2 R_1$ term to the denominator,
on top of the $C_1 R_1$ and $C_2 R_2$ each stage carries on its own. The formula
survives only while that extra term is small beside the largest of those — here
$C_1 R_1 = 1.59$ ms, the term that sets the 100 Hz corner — so what has to stay
small is $C_2$ beside $C_1$. Make the low-pass resistor **much larger** than the
1 kΩ and it is: a hundred times gives $C_2/C_1 = 10^{-4}$, and its capacitor then
follows from $C = 1/(2\pi R f_c)$. Going the other way is what breaks the design —
a low-pass resistor far *below* 1 kΩ needs a large $C_2$, and at 10 Ω the mid-band
has collapsed to about half.

Be clear about what the hundred times buys, because these two corners are two decades
apart and that spacing is already doing most of the work. Matching the first stage
exactly — 1 kΩ against 1 kΩ — gives $C_2/C_1 = 10^{-2}$, a mid-band of 0.98 and
corners at 97 Hz and 10.3 kHz, which passes every check below. A hundred times makes
the loading negligible rather than merely tolerable. It is when the two corners sit
close together that the impedance ratio has to carry the whole burden on its own.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "C", "x": 5, "y": 3, "rot": 0, "value": 1.59e-6},
                        {"id": "p3", "kind": "R", "x": 8, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "OUT", "x": 13, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [8, 3]},
                        {"a": [8, 3], "b": [13, 3]},
                        {"a": [8, 5], "b": [8, 6]},
                        {"a": [8, 6], "b": [3, 6]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "C", "x": 5, "y": 3, "rot": 0, "value": 1.59e-6},
                        {"id": "p3", "kind": "R", "x": 8, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "R", "x": 10, "y": 3, "rot": 0, "value": 100000},
                        {"id": "p5", "kind": "OUT", "x": 13, "y": 3, "rot": 0, "value": 0},
                        {"id": "p6", "kind": "C", "x": 13, "y": 4, "rot": 1, "value": 1.59e-10},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [8, 3]},
                        {"a": [8, 3], "b": [9, 3]},
                        {"a": [11, 3], "b": [13, 3]},
                        {"a": [8, 5], "b": [8, 6]},
                        {"a": [8, 6], "b": [3, 6]},
                        {"a": [13, 5], "b": [13, 6]},
                        {"a": [13, 6], "b": [8, 6]},
                    ],
                },
                "checks": [
                    {"name": "no steady voltage reaches the output", "code": r'''
c.assert(Math.abs(c.vout()) < 1e-6,
  "at DC the probe reads " + c.fmt(c.vout(), "V") + " — the series capacitor should stop it completely");
'''},
                    {"name": "the middle of the band comes through", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(c.gain(1000) / vs, 0.99, 0.05,
  "between two corners a decade away on each side, a band-pass should be almost flat and almost lossless");
'''},
                    {"name": "the lower corner is at 100 Hz", "code": r'''
var r = c.gain(100) / c.gain(1000);
c.close(r, 0.7071, 0.08,
  "at the lower corner the output should be 0.707 of the mid-band level; measured " + r.toPrecision(3));
'''},
                    {"name": "the upper corner is at 10 kHz", "code": r'''
var r = c.gain(10000) / c.gain(1000);
c.close(r, 0.7071, 0.08,
  "at the upper corner the output should be 0.707 of the mid-band level; measured " + r.toPrecision(3) +
  " — a value near 1 means there is no upper corner yet");
'''},
                    {"name": "at 1 MHz almost nothing is left", "code": r'''
var r = c.gain(1e6) / c.gain(1000);
c.assert(r < 0.02,
  "two decades above the upper corner a first-order roll-off should leave about a hundredth; measured " +
  r.toPrecision(3));
'''},
                ],
                "hints": [
                    "The low-pass stage is a resistor in series from the existing node to the probe, and a capacitor from the probe down to the ground rail.",
                    "Delete the long wire between the 1 kΩ node and the probe first, so there is somewhere to put the series resistor.",
                    "Use 100 kΩ — a hundred times the 1 kΩ. Then $C = 1/(2\\pi \\times 10^5 \\times 10^4) = 159$ pF, which is a ten-thousandth of the first stage's capacitor, and the loading error over the whole sweep is 0.01% — the figure this module's lab prints for exactly these values.",
                    "If the mid-band check reports about half, the low-pass resistor is far too small — around a hundredth of the 1 kΩ — and the second stage is dragging the first one down. Merely matching the first stage will not do that here: 1 kΩ against 1 kΩ still leaves the mid-band at 0.98 and every check passing, because the two corners are two decades apart.",
                ],
            },
            "blanks": {
                "title": "Reading a circuit without algebra",
                "minutes": 8,
                "lang": "text",
                "caption": "Fill in the substitutions, then the two circuits they let you classify.",
                "brief": r'''
Before any transfer function, there is a thirty-second reading that gets the answer
right almost every time: replace each reactive component by what it becomes at the two
extremes of frequency, and look at what is left.
''',
                "listing": r'''
                          at DC (f -> 0)          far above the corner

    capacitor                  ___                        ___

    inductor                   ___                        ___


    R in series, C to ground, probe across C   ->   a ___ filter

    C in series, R to ground, probe across R   ->   a ___ filter
''',
                "blanks": [
                    {
                        "prompt": "A capacitor at DC",
                        "hole": "capacitor, DC",
                        "opts": ["an open circuit", "a short circuit", "a 1 Ω resistor"],
                        "a": 0,
                        "why": r'''
$|Z_C| = 1/(\omega C)$, and at $\omega = 0$ that is infinite: a break in the wire.
Nothing steady flows through a capacitor, which is why the divider it sits in stops
dividing at DC.
''',
                    },
                    {
                        "prompt": "A capacitor far above the corner",
                        "hole": "capacitor, high f",
                        "opts": ["an open circuit", "a short circuit", "unchanged from its DC behaviour"],
                        "a": 1,
                        "why": r'''
$1/(\omega C)$ falls towards zero as the frequency rises, so a long way above the
corner the capacitor is indistinguishable from a piece of wire. That is the whole
mechanism behind a coupling capacitor: an open circuit to the steady level, a wire to
the signal.
''',
                    },
                    {
                        "prompt": "An inductor at DC",
                        "hole": "inductor, DC",
                        "opts": ["an open circuit", "a short circuit"],
                        "a": 1,
                        "why": r'''
$|Z_L| = \omega L$, which is zero at $\omega = 0$. An inductor is a coil of wire, and
to an unchanging current that is all it is — there is nothing changing for the
magnetic field to oppose.
''',
                    },
                    {
                        "prompt": "An inductor far above the corner",
                        "hole": "inductor, high f",
                        "opts": ["an open circuit", "a short circuit"],
                        "a": 0,
                        "why": r'''
$\omega L$ grows without bound, so at high enough frequency an inductor is effectively
a break in the circuit. Every entry in this little table is the capacitor's entry
reversed, which is the fastest way to remember all four.
''',
                    },
                    {
                        "prompt": "Resistor first, capacitor to ground, probe across the capacitor",
                        "hole": "R then C",
                        "opts": ["low-pass", "high-pass", "band-pass"],
                        "a": 0,
                        "why": r'''
At DC the capacitor is open, so no current flows, nothing is dropped across the
resistor, and the whole source reaches the probe. Far above the corner the capacitor
is a wire and the probe is shorted to ground. Passes low, stops high: a low-pass.
''',
                    },
                    {
                        "prompt": "Capacitor first, resistor to ground, probe across the resistor",
                        "hole": "C then R",
                        "opts": ["low-pass", "high-pass", "band-pass"],
                        "a": 1,
                        "why": r'''
The same two components with the probe moved. At DC the capacitor is an open circuit
and nothing reaches the resistor at all; far above the corner it is a wire and the
resistor sees the whole source. Passes high, stops low — and with the same corner
frequency, because the corner is where the reactance equals the resistance, and that
does not care where you put the probe.
''',
                    },
                ],
            },
            "numeric": [
                {
                    "title": "The same two parts, the other way up",
                    "minutes": 5,
                    "brief": r'''
The first rung, and deliberately mechanical: one formula, two numbers off the drawing, one
answer.

Look at where the probe is before you start. It is on the resistor, not the capacitor.
Then notice that it makes no difference at all to the number being asked for, and be able
to say why.
''',
                    "prompt": "What is the corner frequency of this filter?",
                    "note": "Give the answer in hertz, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 6, "y": 3, "rot": 0, "value": 1e-8},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 10, "y": 4, "rot": 1, "value": 15000},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 5], "b": [10, 7]},
                            {"a": [10, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V RMS, frequency swept"},
                        {"label": "Capacitor (in series)", "value": "10 nF"},
                        {"label": "Resistor (to ground)", "value": "15.0 kΩ"},
                    ],
                    "aside": "The capacitor is in series and the probe is across the resistor, so this "
                             "is a high-pass: nothing at DC, everything far above the corner. The corner "
                             "itself is the frequency at which the two impedances are the same size, and "
                             "that condition does not mention the probe.",
                    "answer": 1061.0,
                    "tol": 4.0,
                    "unit": "Hz",
                    # Measured rather than recomputed: the reference is the high-frequency asymptote,
                    # and the check bisects the swept response for the point 3 dB below it. Both
                    # component values come off the drawing, so re-valuing either part moves this.
                    "check": r'''
c.assert(c.count('R') === 1 && c.count('C') === 1, "one resistor and one capacitor");
var ref = c.gain(1e7), lo = 1e-2, hi = 1e7;
for (var i = 0; i < 100; i++) {
  var mid = Math.sqrt(lo * hi);
  if (c.gain(mid) < ref / Math.SQRT2) lo = mid; else hi = mid;
}
return Math.sqrt(lo * hi);
''',
                    "hint": r"$f_c = 1/(2\pi RC)$, exactly as for the low-pass built from the same two parts. Work out the product $RC$ in seconds first, and only then divide.",
                    "wrong": r"6667 Hz is $1/RC$, which is $\omega_c$ in radians per second read as though "
                             r"it were hertz — the missing $2\pi$ again. 106.1 Hz is the same arithmetic "
                             r"with 100 nF instead of 10 nF. 150 is the time constant in microseconds, "
                             r"which is a time and not a frequency at all.",
                    "why": r'''
```
RC   = 15000 * 1e-8                       = 1.5000e-4 s
f_c  = 1/(2*pi*1.5e-4)
     = 1/9.42478e-4                       = 1061.0 Hz
```

Worth one cross-check, because it is the definition rather than a formula. At 1061.0 Hz
the capacitor's reactance is

```
X_C = 1/(2*pi*1061.0*1e-8)
    = 1/6.66667e-5                        = 15000 ohm
```

which is the resistor exactly. That is what a corner *is*: the frequency where the two
halves of the divider are the same size. Both halves are therefore $1/\sqrt2$ of the
source at that frequency, and it makes no difference which of them you have chosen to
call the output — so a low-pass and a high-pass built from the same two components corner
at the same place, and the number above would be unchanged if the probe were moved onto
the capacitor.

The time constant is $RC = 150$ µs, which is the other way of quoting the same fact. A
150 µs circuit corners at 1.06 kHz; a 1.06 kHz corner has a 150 µs time constant. Neither
number is round, and that is normal — a tidy answer in this arithmetic usually means a
$2\pi$ went missing.
''',
                },
                {
                    "title": "What the meter reads below the corner",
                    "minutes": 7,
                    "brief": r'''
Second rung, two steps instead of one. The corner is now a stepping stone rather than the
destination: find it, turn the frequency into a ratio, and put the ratio through the
high-pass magnitude.

300 Hz is below the corner, which is the side of a high-pass where things are being thrown
away. Expect an answer well under the source.
''',
                    "prompt": "What RMS voltage does a meter on the probe read at 300 Hz?",
                    "note": "Give the answer in volts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 4},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 6, "y": 3, "rot": 0, "value": 4.7e-8},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 10, "y": 4, "rot": 1, "value": 3300},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 5], "b": [10, 7]},
                            {"a": [10, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "4.00 V RMS, 300 Hz"},
                        {"label": "Capacitor (in series)", "value": "47 nF"},
                        {"label": "Resistor (to ground)", "value": "3.30 kΩ"},
                    ],
                    "aside": "The magnitude of a first-order high-pass is $x/\\sqrt{1 + x^2}$ with "
                             "$x = f/f_c$ — the same denominator as the low-pass, with the ratio moved "
                             "into the numerator. At $x$ well below 1 it is very nearly $x$ itself, but "
                             "'very nearly' is doing real work here and the root has to be evaluated.",
                    "answer": 1.1224,
                    "tol": 0.006,
                    "unit": "V",
                    # The source amplitude and both component values are read off the drawing by the
                    # solver, so the stated answer tracks any edit to the schematic.
                    "check": r'''
c.assert(c.count('V') === 1, "one voltage source, so the reading has something to be relative to");
return c.gain(300);
''',
                    "hint": r"Find $f_c$, then $x = f/f_c$, then $|H| = x/\sqrt{1 + x^2}$, and multiply by the source only at the very end.",
                    "wrong": r"3.839 V is the voltage on the *capacitor* — the complementary low-pass "
                             r"output, and what the probe would read if it had been left where module 4 "
                             r"put it. 0.9049 V is the divider done on magnitudes, $R/(R + X_C)$, with "
                             r"the quarter cycle between them ignored. 0.1859 V comes from a corner of "
                             r"6447 Hz, which is $1/RC$ with the $2\pi$ left out. 2.828 V is $4/\sqrt2$, "
                             r"the value at the corner rather than at 300 Hz.",
                    "why": r'''
```
RC    = 3300 * 47e-9                      = 1.5510e-4 s
f_c   = 1/(2*pi*1.551e-4)                 = 1026.1 Hz

x     = 300/1026.1                        = 0.29236
x^2                                       = 0.085472
1 + x^2                                   = 1.085472
sqrt                                      = 1.041860
|H|   = 0.29236/1.041860                  = 0.28061
Vout  = 4.00 * 0.28061                    = 1.1224 V rms
```

The same number by the other route, which is sometimes quicker when only one frequency is
wanted and there is no reason to know where the corner is:

```
X_C   = 1/(2*pi*300*4.7e-8)               = 11288 ohm
|Z|   = sqrt(3300^2 + 11288^2)
      = sqrt(1.0890e7 + 1.2741e8)         = 11760 ohm
|H|   = 3300/11760                        = 0.28061
```

Note the impedances: 3.30 kΩ and 11.29 kΩ make 11.76 kΩ, not 14.59 kΩ. Adding them
arithmetically is the single commonest error in this course and it gives 0.9049 V here —
wrong by a factor of 0.8, which is small enough to look plausible and large enough to
matter.

Now the sanity check that costs nothing. 300 Hz is 0.292 of the corner, and a first-order
high-pass a decade below its corner passes about a tenth. We are only half a decade below,
so somewhere around a quarter to a third of the input is the expected size, and 0.281 sits
inside that. Had the answer come out at 3.8 V the shape of the filter would have been
wrong, not the arithmetic — and that is the error worth catching, because arithmetic slips
are small and conceptual ones are not.
''',
                },
                {
                    "title": "The current in the coil",
                    "minutes": 9,
                    "brief": r'''
Third rung, and two things change at once. There is no capacitor in this circuit — the
shunt element is an inductor — and the quantity asked for is a current, which no probe
reads directly.

Classify it first, at the two ends of the frequency axis, before touching a formula.
''',
                    "prompt": "What RMS current flows in the inductor at 4.00 kHz?",
                    "note": "Give the answer in milliamps, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 8},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 1200},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3, "rot": 0, "value": 0},
                            {"id": "l1", "kind": "L", "x": 10, "y": 4, "rot": 1, "value": 0.033},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 5], "b": [10, 7]},
                            {"a": [10, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "8.00 V RMS, 4.00 kHz"},
                        {"label": "Resistor (in series)", "value": "1.20 kΩ"},
                        {"label": "Inductor (to ground)", "value": "33 mH"},
                    ],
                    "aside": "There is one loop, so the inductor's current is also the resistor's current "
                             "and the source's current. That means there are two clean routes to it: "
                             "through the probed voltage and the inductor's reactance, or straight through "
                             "the magnitude of the whole loop impedance. Both are worked below.",
                    "answer": 5.484,
                    "tol": 0.02,
                    "unit": "mA",
                    # The inductance is read off the drawing and the probed voltage is solved, so the
                    # answer follows the schematic rather than a constant repeated from the prompt.
                    "check": r'''
c.assert(c.count('R') === 1 && c.count('L') === 1, "one resistor in series with one inductor");
var f = 4000;
return 1000 * c.gain(f) / (2 * Math.PI * f * c.values('L')[0]);
''',
                    "hint": r"$X_L = 2\pi f L$. Either get the inductor's voltage first and divide by $X_L$, or skip the voltage entirely and use $I = V_{in}/\sqrt{R^2 + X_L^2}$.",
                    "wrong": r"6.667 mA is $8/1200$, the resistor alone — the inductor treated as the "
                             r"short circuit it only is at DC. 9.646 mA is $8/829.4$, the inductor alone, "
                             r"with the resistor left out. 3.942 mA divides by $1200 + 829.4$, which adds "
                             r"a resistance and a reactance arithmetically; they are a quarter cycle "
                             r"apart and combine to 1459 Ω, not 2029 Ω.",
                    "why": r'''
Classify it first. At DC the inductor is a piece of wire, so the probe is tied to ground
and nothing gets through. Far above the corner the inductor is an open circuit, no current
flows, nothing is dropped across the resistor and the probe sees the whole source. Nothing
at the bottom, everything at the top: **a high-pass**, with no capacitor anywhere in it.
The corner is where the reactance equals the resistance it works against, $\omega L = R$:

```
f_c   = R/(2*pi*L) = 1200/(2*pi*0.033)
      = 1200/0.207345                     = 5787.5 Hz
```

Then the voltage, and then the current:

```
x     = 4000/5787.5                       = 0.69115
|H|   = 0.69115/sqrt(1 + 0.477689)
      = 0.69115/1.215602                  = 0.56857
V_L   = 8.00 * 0.56857                    = 4.5485 V rms

X_L   = 2*pi*4000*0.033                   = 829.38 ohm
I     = 4.5485/829.38                     = 5.484 mA rms
```

The short way, which never mentions the corner or the transfer function at all:

```
|Z|   = sqrt(1200^2 + 829.38^2)
      = sqrt(1.4400e6 + 6.8787e5)         = 1458.7 ohm
I     = 8.00/1458.7                       = 5.484 mA rms
```

Two things worth taking away. The second route is shorter *because* it is a series circuit
— one current, one impedance magnitude — and the first route is worth doing anyway,
because it is the one that still works when the network is not a single loop.

And notice the direction the corner moves in. For an RL circuit $f_c = R/(2\pi L)$ is a
**ratio**, so raising the resistance raises the corner and makes the circuit faster. For
an RC circuit $f_c = 1/(2\pi RC)$ is a reciprocal **product**, so raising the resistance
lowers the corner and makes the circuit slower. Same word, opposite dependence, and it is
the sign of that dependence that gets misremembered rather than the formula.
''',
                },
                {
                    "title": "The band-pass that was not",
                    "minutes": 12,
                    "brief": r'''
The last rung, and real work. Somebody designed this as a band-pass with corners at 1 kHz
and 10 kHz — the two sections are drawn with exactly those corners — and then wired the
second stage straight onto the first without asking what it would cost.

The two sections cannot be treated separately here, so the answer needs the whole
denominator. Take it in the order the concepts give it: the three time constants first,
then the two coefficients, then one evaluation.
''',
                    "prompt": "What RMS voltage does a meter on the probe read at 3.00 kHz?",
                    "note": "Give the answer in volts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 5, "y": 3, "rot": 0, "value": 1.59e-8},
                            {"id": "r1", "kind": "R", "x": 8, "y": 4, "rot": 1, "value": 10000},
                            {"id": "r2", "kind": "R", "x": 10, "y": 3, "rot": 0, "value": 1000},
                            {"id": "out", "kind": "OUT", "x": 13, "y": 3, "rot": 0, "value": 0},
                            {"id": "c2", "kind": "C", "x": 13, "y": 4, "rot": 1, "value": 1.59e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [4, 3]},
                            {"a": [6, 3], "b": [8, 3]},
                            {"a": [8, 3], "b": [9, 3]},
                            {"a": [11, 3], "b": [13, 3]},
                            {"a": [8, 5], "b": [8, 6]},
                            {"a": [8, 6], "b": [3, 6]},
                            {"a": [13, 5], "b": [13, 6]},
                            {"a": [13, 6], "b": [8, 6]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "5.00 V RMS, 3.00 kHz"},
                        {"label": "High-pass section", "value": "15.9 nF in series, 10.0 kΩ to ground"},
                        {"label": "Low-pass section", "value": "1.00 kΩ in series, 15.9 nF to ground"},
                        {"label": "Designed corners", "value": "1.001 kHz and 10.01 kHz"},
                    ],
                    "aside": "Each section, taken alone, corners where its own designer intended. Wired "
                             "together they do not, because the second stage's capacitor has to be charged "
                             "through the first stage's resistor as well as its own. The extra term that "
                             "puts in is $C_2R_1$, and here it is as large as the dominant time constant.",
                    "answer": 2.381,
                    "tol": 0.015,
                    "unit": "V",
                    # Four component values, the source amplitude and the topology all come from the
                    # drawing; the solver does the loading without being told about it, which is the
                    # point of checking this one against the solver rather than against the formula.
                    "check": r'''
c.assert(c.count('R') === 2 && c.count('C') === 2, "two resistors and two capacitors");
return c.gain(3000);
''',
                    "hint": r"$H = \dfrac{sC_1R_1}{s^2C_1C_2R_1R_2 + s(C_1R_1 + C_2R_2 + C_2R_1) + 1}$ with $s = j\omega$. Only $|H|$ is wanted, so evaluate the real and imaginary parts of the denominator separately and take the hypotenuse.",
                    "wrong": r"4.543 V is the product of the two section responses — the right answer for "
                             r"this pair of sections with a buffer between them, and the answer this "
                             r"question exists to discredit. 4.165 V has the loading term in as $C_2R_2$ "
                             r"a second time instead of $C_2R_1$, which is the near miss to watch for. "
                             r"0.4761 is the ratio rather than the voltage.",
                    "why": r'''
What the design intended, if the two stages had been independent:

```
f_1   = 1/(2*pi*10000*15.9e-9)            = 1000.97 Hz
f_2   = 1/(2*pi*1000*15.9e-9)             = 10009.7 Hz

high-pass at 3 kHz:  x = 3000/1000.97 = 2.99709 -> 0.94859
low-pass  at 3 kHz:  x = 3000/10009.7 = 0.29971 -> 0.95790
product                                   = 0.90866
Vout would be 5.00 * 0.90866              = 4.5433 V     <- wrong
```

What the circuit does. Three time constants, of which the third is the one the product
leaves out:

```
tau_1 = C1*R1 = 15.9e-9 * 10000           = 159.0 us
tau_2 = C2*R2 = 15.9e-9 * 1000            = 15.90 us
C2*R1 = 15.9e-9 * 10000                   = 159.0 us     <- the loading term
b     = 159.0 + 15.90 + 159.0 us          = 333.9 us
a     = tau_1 * tau_2                     = 2.5281e-9 s^2
```

Then one evaluation at $\omega = 2\pi \times 3000$:

```
w         = 18849.6 rad/s
w*tau_1   = 18849.6 * 1.590e-4            = 2.99708      (the numerator)
w^2       = 3.55306e8
w^2*a     = 3.55306e8 * 2.5281e-9         = 0.89825
1 - w^2*a                                 = 0.10175      (real part of the denominator)
w*b       = 18849.6 * 3.339e-4            = 6.29387      (imaginary part)
|den|     = sqrt(0.10175^2 + 6.29387^2)
          = sqrt(0.010353 + 39.6128)      = 6.29469
|H|       = 2.99708/6.29469               = 0.47613
Vout      = 5.00 * 0.47613                = 2.3806 V rms
```

Just over half of what the design predicted, at the frequency the design expected to be
its best. Three consequences, all of them readable off the same three time constants.

**The mid-band collapsed, by a factor you can write down.** The peak of a cascade like this
is $\tau_1/b$, and dividing top and bottom by $\tau_1$ makes it
$1/(1 + \tau_2/\tau_1 + C_2/C_1)$. Here $C_2 = C_1$, so that last term is 1 — the loading
penalty is as large as the whole rest of the expression:

```
peak = 1/(1 + 0.1 + 1.0) = 1/2.1          = 0.47619   at 1/(2*pi*sqrt(a)) = 3165 Hz
```

3.00 kHz is nearly at that peak, so 2.381 V is very close to the best this filter ever
manages anywhere.

**The corners moved a long way.** The denominator's roots are at

```
(-b +/- sqrt(b^2 - 4a))/(2a) = -3066.1 and -129009 rad/s
                             -> 488.0 Hz and 20.53 kHz
```

against the 1.001 kHz and 10.01 kHz drawn. The intended one-decade band is now more than
five octaves wide, and shallow.

**But the geometric mean did not move.** The $s^2$ coefficient is $\tau_1\tau_2$ with or
without the loading, and the product of the roots of $as^2 + bs + 1$ is $1/a$, so the two
corner frequencies always multiply to $f_1f_2$: $488.0 \times 20530 = 1.002\times10^7$,
and $1001 \times 10010 = 1.002\times10^7$. Loading slides the two poles apart along a
hyperbola. It never shifts the band sideways.

The cure was available and cheap. $C_2/C_1 = 1$ here because the second stage was built at
a *tenth* of the first stage's impedance. Build it at a hundred times instead — 100 kΩ with
159 pF, the same 10 kHz corner — and $C_2/C_1$ becomes $10^{-4}$, the loading term
disappears into the rounding, and the product formula is right to a hundredth of a per
cent. Nothing about the specification changed; only which of the many $(R, C)$ pairs
delivering a 10 kHz corner was chosen.
''',
                },
            ],
            "derive": {
                "title": "The denominator that multiplication misses",
                "minutes": 14,
                "vars": ["V_in", "V_a", "V_b", "s", "R_1", "R_2", "C_1", "C_2", "H"],
                "brief": r'''
Two node equations, and the term that separates a cascade from a product.

The circuit is the module's band-pass, wired directly with nothing between the stages: the
source drives $C_1$; $R_1$ runs from the middle node $a$ down to ground; $R_2$ carries on
from $a$ to the output node $b$; $C_2$ runs from $b$ down to ground.

Write $s$ for $j\omega$ throughout, so a capacitor $C$ is an admittance $sC$ and a
resistor $R$ is an admittance $1/R$. Nothing about the argument is specific to sinusoids —
$s$ is carried along as a symbol and only becomes $j\omega$ when you want a number.
''',
                "steps": [
                    {
                        "prompt": "Start at the output, where there is least to go wrong. Only two components touch node $b$: $R_2$ brings current in from node $a$, and $C_2$ takes it out to ground. Nothing else is connected, so those two currents are equal. Write $V_a$ in terms of $V_b$, $s$, $C_2$ and $R_2$.",
                        "given": "In through the resistor: $(V_a - V_b)/R_2$. Out through the capacitor: $V_b\\,sC_2$.",
                        "answer": "V_b(1 + s C_2 R_2)",
                        "placeholder": "V_b(1 + \\ldots)",
                        "hint": "Set the two currents equal, multiply both sides by $R_2$, then collect the $V_b$ terms on one side.",
                        "deconstruct": [
                            "$(V_a - V_b)/R_2 = V_b\\,sC_2$ is the whole of the node equation at $b$.",
                            "Multiplying by $R_2$ gives $V_a - V_b = V_b\\,sC_2R_2$.",
                            "Add $V_b$ to both sides and take it outside a bracket.",
                        ],
                    },
                    {
                        "prompt": "Now node $a$. Write the current arriving there through $C_1$, in terms of $V_{in}$, $V_a$, $s$ and $C_1$.",
                        "answer": "(V_{in} - V_a) s C_1",
                        "placeholder": "(\\ldots) s C_1",
                        "hint": "A capacitor's admittance is $sC$, and current is admittance times the voltage across the component.",
                        "deconstruct": [
                            "One end of $C_1$ is held at $V_{in}$ by the source; the other end is node $a$.",
                            "The voltage across it is therefore $V_{in} - V_a$.",
                            "Multiply by its admittance $sC_1$ to get the current.",
                        ],
                    },
                    {
                        "prompt": "That current has two ways out of node $a$: down through $R_1$ to ground, and onward through $R_2$ towards node $b$. Write the total current leaving, in terms of $V_a$, $V_b$, $R_1$ and $R_2$.",
                        "answer": "\\frac{V_a}{R_1} + \\frac{V_a - V_b}{R_2}",
                        "placeholder": "\\frac{V_a}{R_1} + \\ldots",
                        "hint": "Ohm's law twice. $R_1$ has the full $V_a$ across it because its far end is the ground rail; $R_2$ has only the difference between the two nodes.",
                        "deconstruct": [
                            "$R_1$ runs from $a$ to ground, so the voltage across it is $V_a - 0$.",
                            "$R_2$ runs from $a$ to $b$, so the voltage across it is $V_a - V_b$.",
                            "Divide each by its own resistance and add.",
                        ],
                    },
                    {
                        "prompt": "Set the arriving current equal to the leaving current, substitute $V_a = V_b(1 + sC_2R_2)$, and multiply every term by $R_1$. Everything now collects onto $V_b$, leaving $V_{in}\\,sC_1R_1 = V_b\\,D$. Write $D$, gathered by powers of $s$.",
                        "given": "Three terms carry $V_b$: $sC_1R_1(1 + sC_2R_2)$ from the capacitor's current, $(1 + sC_2R_2)$ from $R_1$, and $sC_2R_1$ from $R_2$ — that last because $V_a - V_b = V_b\\,sC_2R_2$, and multiplying it by $R_1/R_2$ cancels the $R_2$.",
                        "answer": "s^2 C_1 C_2 R_1 R_2 + s(C_1 R_1 + C_2 R_2 + C_2 R_1) + 1",
                        "placeholder": "s^2\\,\\ldots + s(\\ldots) + 1",
                        "hint": "Expand $sC_1R_1(1 + sC_2R_2)$ into $sC_1R_1 + s^2C_1C_2R_1R_2$, then add the other two terms and collect.",
                        "deconstruct": [
                            "The three $V_b$ terms are $sC_1R_1 + s^2C_1C_2R_1R_2$, then $1 + sC_2R_2$, then $sC_2R_1$.",
                            "There is exactly one $s^2$ term: $s^2C_1C_2R_1R_2$.",
                            "There are three terms in $s$: $sC_1R_1$, $sC_2R_2$ and $sC_2R_1$.",
                            "And one constant term, the 1 that came from $V_a/R_1$ after multiplying by $R_1$.",
                        ],
                    },
                    {
                        "prompt": "Finally, write the transfer function $H = V_b/V_{in}$.",
                        "answer": "\\frac{s C_1 R_1}{s^2 C_1 C_2 R_1 R_2 + s(C_1 R_1 + C_2 R_2 + C_2 R_1) + 1}",
                        "placeholder": "\\frac{s C_1 R_1}{\\ldots}",
                        "hint": "Divide both sides of $V_{in}\\,sC_1R_1 = V_b\\,D$ by $V_{in}D$.",
                        "deconstruct": [
                            "$V_b/V_{in}$ is what is wanted, so divide both sides by $V_{in}$.",
                            "Then divide both sides by $D$ to free $V_b/V_{in}$.",
                        ],
                    },
                ],
                "closing": r'''
Now set it beside the product of the two sections taken separately:

$$H_1H_2 = \frac{sC_1R_1}{(1 + sC_1R_1)(1 + sC_2R_2)}
        = \frac{sC_1R_1}{s^2C_1C_2R_1R_2 + s(C_1R_1 + C_2R_2) + 1}$$

The numerators agree. The $s^2$ terms agree. The entire disagreement is one term, $C_2R_1$,
in the coefficient of $s$ — and it came into the derivation at exactly one place, in step
four, out of the current that $R_2$ carries away from node $a$. That is the current the
first stage was not supposed to be supplying.

There is a way to write that term down without doing any of this. Ask what resistance each
capacitor charges through, with the source shorted and the *other* capacitor removed.
$C_1$ can only reach ground through $R_1$, so it contributes $C_1R_1$. $C_2$ has to get its
charging current up through $R_2$ and then through $R_1$, so it sees $R_1 + R_2$ and
contributes $C_2R_2 + C_2R_1$. Add them and you have the $s$ coefficient exactly. That rule
— the coefficient of $s$ is the sum of every capacitor's time constant computed with all
the others open-circuited — holds for any network of this kind, and it is usually the
fastest honest estimate of a messy circuit's bandwidth that does not involve a simulator.

Two consequences follow immediately from the shape of the denominator, and neither needs
the roots to be found.

**The product of the two corner frequencies is untouched.** Loading changes only the
coefficient of $s$, and for $as^2 + bs + 1$ the roots multiply to $1/a$. Whatever the
second stage does to the first, $f_af_b = f_1f_2$ exactly: the poles slide apart, they
never slide sideways.

**The mid-band gain is $\tau_1/(\tau_1 + \tau_2 + C_2R_1)$**, where $\tau_1 = C_1R_1$ and
$\tau_2 = C_2R_2$. Divide through by $\tau_1$ and the loading term becomes
$C_2R_1/C_1R_1 = C_2/C_1$, so the whole penalty for wiring the stages together is the ratio
of the two capacitors. That is the sentence to keep: **the test is $C_2 \ll C_1$**, and
since $C_2/C_1 = (f_1/f_2)(R_1/R_2)$ it is satisfied by separating the corners, by stepping
the impedance up, or by any mixture of the two.
''',
            },
            "lab": {
                "title": "What the cascade actually does",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Two filters in a row, computed twice: once by multiplying their responses as if they
were independent, and once properly. The difference is the loading.

Write $s = j2\pi f$ throughout — in Python, `s = 2j * np.pi * f`.

`highpass(f, r, c)` returns the complex response $\dfrac{sRC}{1 + sRC}$.

`lowpass(f, r, c)` returns $\dfrac{1}{1 + sRC}$.

`ideal(f, r1, c1, r2, c2)` returns the product of the two: the high-pass built from
`r1, c1` followed by the low-pass built from `r2, c2`, on the assumption that the
second stage draws nothing from the first.

`actual(f, r1, c1, r2, c2)` returns what the two really do when they are wired
directly together. Solving the two node equations gives

```text
H = s*C1*R1 / (s**2 * C1*C2*R1*R2 + s * (C1*R1 + C2*R2 + C2*R1) + 1)
```

which differs from the ideal product by exactly one term in the denominator: the
`C2*R1` that appears because the second stage's capacitor is charged through the first
stage's resistor as well as its own.

`worst_error(r1, c1, r2, c2, flo, fhi, n=400)` sweeps `n` frequencies spaced evenly in
the logarithm between `flo` and `fhi`, and returns the largest value of
`abs(1 - abs(actual)/abs(ideal))` over the sweep. That is the honest answer to "how
wrong is the multiplication here".
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def highpass(f, r, c):
    """Complex response of an R-C high-pass at frequency f."""
    # TODO: s = 2j*pi*f, then s*r*c / (1 + s*r*c)
    return 0j


def lowpass(f, r, c):
    """Complex response of an R-C low-pass at frequency f."""
    # TODO
    return 0j


def ideal(f, r1, c1, r2, c2):
    """The product of the two responses, assuming no loading."""
    # TODO
    return 0j


def actual(f, r1, c1, r2, c2):
    """What the two stages really do when wired directly together."""
    # TODO
    return 0j


def worst_error(r1, c1, r2, c2, flo, fhi, n=400):
    """Largest relative disagreement between ideal and actual over a log sweep."""
    # TODO: np.logspace over log10(flo) to log10(fhi)
    return 0.0


if __name__ == "__main__":
    R1, C1 = 1000.0, 1.59e-6
    for R2 in (100000.0, 1000.0, 100.0):
        C2 = 1.0 / (2 * np.pi * R2 * 10000.0)
        e = worst_error(R1, C1, R2, C2, 10.0, 1e6)
        print("R2 =", R2, "ohms -> worst error", round(100 * e, 2), "%")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def highpass(f, r, c):
    """Complex response of an R-C high-pass at frequency f."""
    s = 2j * np.pi * f
    return s * r * c / (1.0 + s * r * c)


def lowpass(f, r, c):
    """Complex response of an R-C low-pass at frequency f."""
    s = 2j * np.pi * f
    return 1.0 / (1.0 + s * r * c)


def ideal(f, r1, c1, r2, c2):
    """The product of the two responses, assuming no loading."""
    return highpass(f, r1, c1) * lowpass(f, r2, c2)


def actual(f, r1, c1, r2, c2):
    """What the two stages really do when wired directly together."""
    s = 2j * np.pi * f
    num = s * c1 * r1
    den = s * s * c1 * c2 * r1 * r2 + s * (c1 * r1 + c2 * r2 + c2 * r1) + 1.0
    return num / den


def worst_error(r1, c1, r2, c2, flo, fhi, n=400):
    """Largest relative disagreement between ideal and actual over a log sweep."""
    fs = np.logspace(np.log10(flo), np.log10(fhi), int(n))
    a = np.abs(actual(fs, r1, c1, r2, c2))
    b = np.abs(ideal(fs, r1, c1, r2, c2))
    return float(np.max(np.abs(1.0 - a / b)))


if __name__ == "__main__":
    R1, C1 = 1000.0, 1.59e-6
    for R2 in (100000.0, 1000.0, 100.0):
        C2 = 1.0 / (2 * np.pi * R2 * 10000.0)
        e = worst_error(R1, C1, R2, C2, 10.0, 1e6)
        print("R2 =", R2, "ohms -> worst error", round(100 * e, 2), "%")
'''}],
                "hints": [
                    "`2j * np.pi * f` is $s$. Writing `2 * np.pi * f * 1j` is the same thing; writing `2 * np.pi * f` is a real number and loses every phase in the lab.",
                    "All five functions work on a NumPy array of frequencies without any change, because every operation in them is elementwise — which is what makes `worst_error` a two-liner.",
                    "`np.logspace(np.log10(flo), np.log10(fhi), n)` gives the sweep. Spacing evenly in frequency instead would put almost every sample above the upper corner and miss the interesting part entirely.",
                ],
                "tests": [
                    {"name": "each stage is 0.707 at its own corner", "code": r'''
import numpy as np
_fc = 1.0 / (2 * np.pi * 1000.0 * 1.59e-6)
assert abs(abs(highpass(_fc, 1000.0, 1.59e-6)) - 0.7071067811865475) < 1e-9, \
    f"a high-pass is 1/sqrt(2) at its corner, got {abs(highpass(_fc, 1000.0, 1.59e-6))}"
assert abs(abs(lowpass(_fc, 1000.0, 1.59e-6)) - 0.7071067811865475) < 1e-9, \
    f"so is a low-pass, got {abs(lowpass(_fc, 1000.0, 1.59e-6))}"
'''},
                    {"name": "the two point in opposite directions", "code": r'''
import numpy as np
assert abs(highpass(1.0, 1000.0, 1.59e-6)) < 0.02, \
    f"a 100 Hz high-pass should be two decades down at 1 Hz, got {abs(highpass(1.0, 1000.0, 1.59e-6))}"
assert abs(abs(highpass(1e6, 1000.0, 1.59e-6)) - 1.0) < 0.001, \
    "far above its corner a high-pass should pass everything"
assert abs(abs(lowpass(1.0, 1000.0, 1.59e-6)) - 1.0) < 0.001, \
    "far below its corner a low-pass should pass everything"
assert abs(np.angle(highpass(1.0, 1000.0, 1.59e-6)) - np.pi / 2) < 0.02, \
    "well below its corner a high-pass leads by 90 degrees"
'''},
                    {"name": "the band-pass is flat in the middle and falls on both sides", "code": r'''
import numpy as np
_a = (1000.0, 1.59e-6, 100000.0, 1.59e-10)
_mid = abs(ideal(1000.0, *_a))
assert _mid > 0.98, f"between corners a decade away on each side the response should be near 1, got {_mid}"
assert abs(abs(ideal(100.0, *_a)) / _mid - 0.7071) < 0.02, "the lower corner should sit at 100 Hz"
assert abs(abs(ideal(10000.0, *_a)) / _mid - 0.7071) < 0.02, "the upper corner should sit at 10 kHz"
'''},
                    {"name": "a light second stage barely disturbs the first", "code": r'''
_e = worst_error(1000.0, 1.59e-6, 100000.0, 1.59e-10, 10.0, 1e6)
assert _e > 0.0, \
    "there is always some loading — a worst error of exactly zero means the two responses are not being compared"
assert _e < 0.001, \
    f"a hundred times the impedance and corners two decades apart put C2/C1 at 1e-4, so the product should be good to about 0.01%; got {100*_e:.4f}%"
'''},
                    {"name": "a heavy second stage does not", "code": r'''
import numpy as np
_r2 = 100.0
_c2 = 1.0 / (2 * np.pi * _r2 * 10000.0)
_e = worst_error(1000.0, 1.59e-6, _r2, _c2, 10.0, 1e6)
assert _e > 0.05, \
    f"with the second stage a tenth of the impedance of the first, multiplying the responses should be visibly wrong; got {100*_e:.2f}%"
'''},
                    {"name": "the only difference is the loading term", "code": r'''
import numpy as np
_f = np.array([50.0, 500.0, 5000.0])
_i = ideal(_f, 1000.0, 1.59e-6, 100000.0, 1.59e-10)
_a = actual(_f, 1000.0, 1.59e-6, 100000.0, 1.59e-10)
assert len(_a) == 3, "the functions should work on an array of frequencies without a loop"
assert np.all(np.abs(_a) <= np.abs(_i) + 1e-12), \
    "the extra term is a load, so the real cascade can never be larger than the ideal product"
'''},
                ],
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Inductors, RL circuits and the time constant",
            "summary": "The mirror image of the capacitor, and the same first-order behaviour seen in time rather than in frequency.",
            "concepts": [
                "An inductor is a coil of wire. It opposes a *change* in the current through it: $v = L\\,di/dt$, with $L$ in henries.",
                "So at DC an ideal inductor is a plain wire, and at high frequency it is nearly a break in the circuit — the exact opposite of a capacitor at both ends.",
                "A resistor and an inductor in series, with the output taken across the resistor, is a low-pass filter: $H = \\dfrac{R}{R + j\\omega L}$, with corner $f_c = \\dfrac{R}{2\\pi L}$.",
                "Its **time constant** is $\\tau = L/R$ seconds — note that it is a ratio, not a product, so a *larger* resistance makes an RL circuit faster while it makes an RC circuit slower.",
                "Switch a step of voltage onto a first-order circuit and the output moves towards its final value as $1 - e^{-t/\\tau}$: 63% of the way after one $\\tau$, 86% after two, 99.3% after five. In practice, five time constants is settled.",
                "The time constant and the corner frequency are two descriptions of one circuit: $f_c = 1/(2\\pi\\tau)$. A fast circuit in time is a wide one in frequency, always.",
                "A capacitor blocks DC because its reactance $1/(\\omega C)$ grows without bound as the frequency goes to zero — not because charge cannot cross the gap. Charge never crosses the gap at any frequency, yet alternating current flows in the wires all the same, because charge arriving on one plate pushes an equal charge off the other.",
            ],
            "read": [
                {
                    "title": "A coil of wire, and what it objects to",
                    "minutes": 13,
                    "body": r'''
Two components have carried the course this far. A resistor, which turns a voltage into a
current with no memory of anything. A capacitor, which stores charge on two plates that do
not touch. The third component is a coil of wire, and the honest first reaction to it is
that a coil of wire is a piece of wire. Put a meter across one and that is roughly what the
meter says: a few ohms, sometimes a fraction of one. Yet in a circuit it does something no
resistor and no capacitor does, and everything it does follows from a single sentence that
is worth arriving at properly rather than being handed.

## What the coil is storing

A current in a wire makes a magnetic field around it. Wind the wire into a coil and the
fields of the separate turns line up and add, so a hundred turns carrying a modest current
produce a field far stronger than the same current in a straight wire — and that field
passes back through every one of those hundred turns on its way round. The field is not
free. Setting it up costs energy taken from the circuit, and the coil holds that energy for
exactly as long as the current keeps flowing.

Now Faraday's observation: a magnetic field changing through a loop of wire induces a
voltage in that loop. The coil's own field threads its own turns, so if the current
changes, the field changes, and the coil induces a voltage **in itself**. Lenz's law
settles the direction: the induced voltage opposes the change that caused it. Push harder
to raise the current and the coil pushes back; ease off and the coil keeps pushing forward.

Give the total flux threading all the turns a name, $\lambda$, and for an ordinary coil in
air it is simply proportional to the current: $\lambda = Li$. The constant $L$ is the
**inductance**, and Faraday's law $v = d\lambda/dt$ then reads

$$v = L\,\frac{di}{dt}$$

The unit is the henry, and the definition falls straight out of that equation: one henry is
one volt across the coil for every amp per second of change, so a henry is a volt-second
per amp.

Read the formula as a sentence, because that is where the intuition lives. **The voltage
across an inductor is proportional to how fast its current is changing, and is zero
whenever that current is steady.** Notice what is absent from the right-hand side: the
current itself. Push 3 A through an ideal inductor and hold it there, and the voltage
across it is zero — not small, zero. The coil has no opinion about current. It has an
opinion about *change* in current.

If you want a mechanical picture, it is inertia. A force is needed to change a velocity,
not to maintain one; a mass in motion carries on when you stop pushing and needs a force to
be stopped. Current plays velocity, voltage plays force, inductance plays mass — and even
the energy matches: $\tfrac12 L i^2$ against $\tfrac12 m v^2$. The capacitor is the other
side of that analogy, storing $\tfrac12 C v^2$ and resisting a change of *voltage* in
exactly the way the inductor resists a change of current.

## Worked: what a ramp of current costs

Take a 47 mH coil and force its current up a straight line from 0 to 2.0 A over 5.0 ms.

```
di/dt = 2.0 A / 5.0e-3 s                  = 400 A/s
v     = L * di/dt = 0.047 * 400           = 18.8 V
```

Constant 18.8 V, held for the whole 5 ms, because the slope is constant. Nothing about that
voltage depends on how much current is flowing at the time — at 0.1 A and at 1.9 A the coil
demands the same 18.8 V, because it is climbing at the same rate.

At the end of the ramp the coil holds

```
W = 0.5 * L * i^2 = 0.5 * 0.047 * 2.0^2   = 0.094 J
```

and it is worth checking that against the energy the source actually delivered, because the
two calculations know nothing about each other. Power is $vi$; the voltage was a flat
18.8 V and the current averaged 1.0 A over the ramp, so the average power was 18.8 W for
5.0 ms:

```
E = 18.8 W * 5.0e-3 s                     = 0.094 J
```

The same number, which is the sign that $\tfrac12 Li^2$ is not a separate fact to remember
but a consequence of $v = L\,di/dt$.

## Worked: a sinusoid, and where $j\omega L$ comes from

Now the case the rest of this course is built on. Let the current be a sinusoid,
$i(t) = I_p\sin\omega t$. Differentiate:

$$v = L\frac{di}{dt} = \omega L\,I_p\cos\omega t$$

Two things fall out of that one line, and they are the whole of AC inductor behaviour.

The **amplitude** of the voltage is $\omega L$ times the amplitude of the current. So the
coil has a resistance-like quantity, $\omega L$ ohms, and unlike a real resistance it grows
in direct proportion to frequency. That is the **reactance** $X_L = \omega L$.

The **shape** is a cosine where the current was a sine, which is a quarter of a cycle
earlier. The voltage leads the current by 90°, and that quarter cycle is what the $j$
carries in $Z_L = j\omega L$. (For a capacitor it is the current that leads, by the same
quarter cycle. The old mnemonic *ELI the ICE man* packs both into five syllables: in an
inductor $L$, $E$ leads $I$; in a capacitor $C$, $I$ leads $E$.)

Numbers, on a 10 mH coil, at two frequencies two decades apart:

```
at 1 kHz:     |Z_L| = 2*pi*1000*0.010     = 62.83 ohm
at 100 kHz:   |Z_L| = 2*pi*100000*0.010   = 6283 ohm
```

and, for the contrast, a 10 nF capacitor over the same two frequencies:

```
at 1 kHz:     |Z_C| = 1/(2*pi*1000*1e-8)  = 15915 ohm
at 100 kHz:   |Z_C| = 1/(2*pi*1e5*1e-8)   = 159.2 ohm
```

One rises by a factor of a hundred, the other falls by a factor of a hundred, over exactly
the same span. That mirror is the reason the two components turn up together so often, and
the reason a circuit built from one can usually be rebuilt from the other with the roles of
the two ends of the frequency axis swapped.

One consistency check, to tie the reactance back to the differential equation it came from.
Drive that 10 mH coil at 1 kHz with a current of 0.5 A peak. Through the reactance, the
peak voltage is $62.83 \times 0.5 = 31.42$ V. Through $L\,di/dt$ directly, the steepest
slope of $0.5\sin(2\pi\cdot 1000\,t)$ is $0.5 \times 2\pi \times 1000 = 3142$ A/s, and
$0.010 \times 3142 = 31.42$ V. The same number, as it must be — the reactance is just
$L\,di/dt$ evaluated for a sinusoid and then never mentioned again.

## The two ends of the frequency axis

Both limits now follow without any more work.

At DC the current is not changing, $di/dt = 0$, and the voltage across the coil is zero. A
component with a voltage of zero across it whatever current flows is a piece of wire. So
**at DC an ideal inductor is a short circuit** — which is also what it looks like, and one
of the few times in electronics where the naive answer is the right one.

At high frequency $\omega L$ grows without bound, and a component that needs an unbounded
voltage to pass any current at all is a break in the circuit. So **far above the corner an
ideal inductor is an open circuit**.

Every entry there is the capacitor's entry reversed, and that is the fastest way to keep
all four straight: you only have to remember one row and the fact that the other is its
opposite.

## Worked: the inductive kick, and why relays get a diode

The equation has a consequence that is easy to state and startling to meet. Take a relay
coil, 200 mH and 80 Ω of winding, carrying a steady 150 mA from a 12 V supply. Now open the
switch feeding it.
Mechanical contacts part in something like 10 µs, so the current is being forced to zero in
that time:

```
di/dt = -0.150 A / 10e-6 s                = -15000 A/s
|v|   = 0.200 * 15000                     = 3000 V
```

Three thousand volts, from a 12 V supply, across a component that measured 80 Ω on the
meter. Nothing is being violated: the coil holds

```
W = 0.5 * 0.200 * 0.150^2                 = 2.25 mJ
```

of energy in its magnetic field, the switch has just removed the only path that energy had,
and $v = L\,di/dt$ says what happens to a coil whose current is taken away quickly. In
practice the contacts arc, and the arc *is* the circuit finding a path — which is why relay
contacts and the transistors that drive coils fail, and why a **freewheel diode** across the
coil is standard: it gives the current somewhere to keep flowing while the field collapses,
so $di/dt$ is set by the coil and the diode rather than by the switch.

## The mistake, and why it is tempting

The mistake is "an inductor resists current". It is tempting because reactance sounds like
resistance, because the impedance really does grow with frequency, and because the coil
really does fight you at the moment you try to start a current. But the DC case gives it
away: a steady current meets an ideal coil with no opposition whatever. The correct sentence
is that an inductor resists **a change in** current, and it is worth saying the extra three
words every time until they stop feeling optional, because every wrong answer in this
module traces back to dropping them.

The second is the arithmetic one this course keeps meeting: writing $fL$ where $\omega L$
belongs, which is out by $2\pi$ — a factor of 6.28, big enough to be badly wrong and small
enough to look plausible. A 10 mH coil at 1 kHz is 62.8 Ω, not 10 Ω.

## Where the picture stops holding

**A real coil has resistance, and at low frequency that is all it has.** A 10 mH choke
wound with enough wire to get 10 mH might have 8 Ω of winding resistance. At 1 kHz that
barely shows: $|Z| = \sqrt{8^2 + 62.83^2} = 63.34$ Ω against an ideal 62.83, less than 1%
high. At 100 Hz it dominates: $|Z| = \sqrt{8^2 + 6.283^2} = 10.17$ Ω against an ideal
6.28 Ω, 62% high. The crossover is where $\omega L = R$, at $8/(2\pi \times 0.010) = 127$ Hz,
and below that the component on your bench is mostly a resistor with a little inductance
attached. Capacitors have a parasitic resistance too, but it is usually a fraction of an
ohm; a coil's is unavoidable, because inductance is made of wire.

**A real coil has capacitance too, between adjacent turns, and above its self-resonant
frequency it is a capacitor.** Ten millihenries with 15 pF of winding capacitance resonates
at $1/(2\pi\sqrt{LC}) = 411$ kHz, and above that the "choke" you fitted to block high
frequencies is passing them.

**$L$ is only constant while the core is not saturated.** Wind the coil on iron or ferrite
to get more inductance from fewer turns and you inherit the core's limit: past a certain
current the material cannot be magnetised further, $\lambda = Li$ stops being a straight
line, and the effective $L$ collapses. The current then rises far faster than the equation
predicts, which is how switching supplies destroy their transistors.

**And the field goes outside the component.** A capacitor keeps its field between its
plates; a coil throws its field into the space around it, so two inductors near each other
are not two components but one four-terminal device with mutual inductance between them.
That is a nuisance in a filter and the entire operating principle of a transformer.

None of that makes $v = L\,di/dt$ wrong. It makes it a statement about an ideal element,
and knowing which of its assumptions a particular circuit is leaning on is most of what
separates a design that works from one that only simulates.
''',
                },
                {
                    "title": "Why the time constant is L over R",
                    "minutes": 14,
                    "body": r'''
A 5.00 V supply, a switch, a 470 Ω resistor and a 10 mH coil, all in one loop. Close the
switch.

Ohm's law says the current will be $5.00/470 = 10.638$ mA. The inductor says the current
was zero an instant ago and cannot jump, because a jump would mean an infinite $di/dt$ and
therefore an infinite voltage, and there is only 5 V available. Both statements are true.
The only question left is how long the disagreement takes to settle, and the answer to that
question is a single number that belongs to the circuit rather than to the source: the
**time constant**.

## Before any algebra, what has to happen

Kirchhoff's voltage law round the loop, with the coil obeying $v = L\,di/dt$:

$$V_s = iR + L\frac{di}{dt}$$

Read that at three moments without solving it.

**At the instant of closing**, $i = 0$, so the resistor has nothing across it and the whole
5 V is across the coil. That fixes the initial slope: $di/dt = V_s/L = 5.00/0.010 = 500$
amps per second. This is the fastest the current will ever climb.

**A while later**, some current is flowing, the resistor is taking $iR$ of the source, and
only $V_s - iR$ is left for the coil. Less voltage on the coil means a smaller $di/dt$. The
climb is slowing down, and it is slowing down *because* it has got somewhere.

**In the end**, when $i$ reaches $V_s/R$, there is nothing left for the coil at all,
$di/dt = 0$, and the current stops changing. The circuit has arrived.

So the shape is settled already: starts at its steepest, flattens as it approaches, arrives
asymptotically, never overshoots. That is the whole qualitative story, and it came out of
one equation read three times rather than solved once.

## The time constant, without solving anything

Here is the argument that says what the time constant *is*, and it is better than the one
that extracts it from an exponential, because it explains the shape of the formula rather
than just producing it.

The current starts with slope $V_s/L$ and is heading for $V_s/R$. Ask the obvious question:
if it kept its initial slope, when would it arrive?

```
t = (final value) / (initial slope)
  = (V_s/R) / (V_s/L)
  = L/R
```

The source voltage cancels — as it must, since doubling the supply doubles both the
destination and the speed of setting off. What is left is $L/R$, and that is the time
constant $\tau$. Geometrically: draw the tangent to the curve at the origin, see where it
crosses the final value, and read off the time. That construction works for every
first-order circuit, RL or RC, and for an RC circuit it hands you $RC$ by the identical
argument.

Check the units, because this is exactly the formula people write upside down. One henry is
one volt-second per amp; one ohm is one volt per amp; so H/Ω is a second, and H·Ω is not.

## Solving it properly

$$L\frac{di}{dt} = V_s - iR \quad\Longrightarrow\quad \frac{di}{\dfrac{V_s}{R} - i} = \frac{R}{L}\,dt$$

Integrate both sides from the moment of closing, with $i(0) = 0$:

$$-\ln\!\left(\frac{V_s/R - i}{V_s/R}\right) = \frac{R}{L}\,t$$

Exponentiate and rearrange, writing $\tau = L/R$:

$$i(t) = \frac{V_s}{R}\left(1 - e^{-t/\tau}\right)$$

and since the resistor's voltage is $iR$ and the coil gets whatever is left,

$$v_R(t) = V_s\left(1 - e^{-t/\tau}\right) \qquad v_L(t) = V_s\,e^{-t/\tau}$$

Those two add to $V_s$ at every instant, which is Kirchhoff's voltage law and a free check
on any arithmetic you do with them. The numbers everyone ends up carrying:

```
  t/tau     1 - e^(-t/tau)      e^(-t/tau)
    1          0.6321            0.3679
    2          0.8647            0.1353
    3          0.9502            0.0498
    4          0.9817            0.0183
    5          0.9933            0.0067
```

63% after one time constant, 95% after three, 99.3% after five — which is where the working
definition of "settled" comes from. The right-hand column is the same information seen from
the other side: it is the fraction of the *gap* still remaining, and it is also the fraction
of the source still sitting across the inductor.

## Worked: the 470 Ω circuit, 30 µs after the switch closes

```
tau   = L/R = 0.010/470                   = 2.1277e-5 s = 21.277 us
i_inf = 5.00/470                          = 10.638 mA

t/tau = 30e-6 / 2.1277e-5                 = 1.4100
e^-1.41                                   = 0.244143
1 - e^-1.41                               = 0.755857

v_R   = 5.00 * 0.755857                   = 3.7793 V
i     = 3.7793/470                        = 8.0410 mA
v_L   = 5.00 - 3.7793                     = 1.2207 V
```

and the check that costs nothing: $v_L$ should independently be
$V_s e^{-t/\tau} = 5.00 \times 0.244143 = 1.2207$ V. It is. If those two had disagreed, one
of the exponentials was evaluated wrongly.

Sanity, before moving on: 30 µs is about one and a half time constants, so the answer had
to land between the 63% and 86% rows of the table. 75.6% does.

## Worked: ten times the resistance, and the circuit gets ten times faster

Same coil, same supply, resistor changed to 4.7 kΩ.

```
tau   = 0.010/4700                        = 2.1277e-6 s = 2.128 us
i_inf = 5.00/4700                         = 1.0638 mA
```

At the same 30 µs mark, $t/\tau = 14.1$ and $e^{-14.1} = 7.5\times10^{-7}$: this circuit
passed its five-time-constant mark at 10.6 µs and has been settled for roughly twenty
microseconds. More resistance, and it got there sooner.

That is worth understanding rather than memorising, and the tangent argument explains it in
one line. The initial slope is $V_s/L$ — **the resistor is not in it**. So both circuits set
off at exactly the same 500 A/s. What the bigger resistor changed is the destination:
1.06 mA instead of 10.6 mA. Same starting speed, a tenth of the distance, a tenth of the
time.

Compare that with an RC circuit, where the resistor is in the path of the charge being
delivered to the capacitor — a bigger resistor is a narrower pipe and everything takes
longer. In an RL circuit the resistor is not filling anything. It is deciding how little
current is needed before the loop balances, and a larger resistance means a nearer target.

## The resistance is the one the coil actually sees

$\tau = L/R$ is a special case of a rule that survives circuits with more than one
resistor: the time constant is $L$ divided by the **Thévenin resistance at the inductor's
own two terminals**, measured with the sources suppressed — voltage sources replaced by
wires, current sources by breaks.

Take a source feeding a 1.5 kΩ resistor into a node; a 3.3 kΩ resistor from that node down
to ground; and a 47 mH coil from the same node down to ground.

```
short the source, look back from the coil's two terminals:
R_th  = 1500*3300/(1500+3300) = 4950000/4800    = 1031.25 ohm
tau   = L/R_th = 0.047/1031.25                  = 4.5576e-5 s = 45.58 us
f_c   = 1/(2*pi*4.5576e-5)                      = 3492 Hz
```

Look at what either resistor alone would have given: $0.047/1500 = 31.3$ µs, or
$0.047/3300 = 14.2$ µs. Neither is close, and both are *too small* — necessarily, because a
parallel combination is smaller than either of its parts and $R$ is downstairs in $L/R$.
That direction is a useful check even when you have not worked the number out yet.

## Time and frequency are one statement

Module 4 gave the same circuits a corner frequency. The two descriptions are the same fact:

$$f_c = \frac{1}{2\pi\tau}$$

For the 470 Ω circuit, $f_c = 1/(2\pi \times 2.1277\times10^{-5}) = 7480$ Hz, and by the
frequency-domain route $f_c = R/(2\pi L) = 470/0.06283 = 7480$ Hz. The same number twice.
The $2\pi$ is there because the pole sits at $\omega = 1/\tau$ radians per second while a
corner is quoted in cycles per second.

The practical version of that identity is the one used on a bench every day. The 10%-to-90%
**rise time** of a first-order step is

```
t_10 = tau * ln(1/0.9)   = 0.10536 * tau
t_90 = tau * ln(10)      = 2.30259 * tau
t_r  = t_90 - t_10 = tau * ln 9  = 2.1972 * tau
```

so for the 470 Ω circuit $t_r = 2.1972 \times 21.277\ \mu s = 46.75$ µs. Multiply by the
corner frequency:

```
t_r * f_c = 46.75e-6 * 7480                = 0.3497
```

Just under 0.35, and the source voltage, the resistance and the inductance have all
cancelled out of it. Measure a rise time on an oscilloscope, divide 0.35 by it, and you have
the bandwidth without owning a signal generator. "Fast in time is wide in frequency" is a
slogan; $t_r f_c = 0.35$ is the same slogan with a number attached.

## The mistake, and why it is tempting

The mistake is $\tau = LR$. It is tempting for a reason that has nothing to do with
inductors: $\tau = RC$ is a product, it was learned first, and the hand writes the shape it
learned. Both formulas are "the two component values combined", and only one of them is
combined by multiplying.

The defence is a magnitude check, which takes two seconds and catches it every time.
$L R = 0.010 \times 470 = 4.7$, and 4.7 seconds is a preposterous answer for a circuit made
of a small coil and a quarter-watt resistor — you could watch it settle. The real answer is
21 µs. When a time constant comes out in seconds for a circuit that fits in your hand,
something has been multiplied that should have been divided.

The related conceptual mistake is expecting more resistance to mean a slower circuit,
because everywhere else in a first course resistance is the thing that impedes. In an RL
circuit it is the thing that shortens the journey.

## Where this stops holding

**The coil's own winding resistance is part of $R$, whether you wanted it or not.** A 10 H
filter choke might have 200 Ω of wire in it. Feed a 100 Ω load through it and the time
constant is $10/300 = 33.3$ ms, not $10/100 = 100$ ms — and the steady output is only
$100/300$ of the supply, which is usually the more painful of the two surprises.

**Opening the switch is a different circuit, not the same one run backwards.** The formula
still holds; what changes is $R$, which becomes the resistance of the parting contacts —
effectively enormous. $\tau = L/R$ collapses towards zero, and $v_L = L\,di/dt$ goes the
other way, which is the three thousand volts of the previous reading. A freewheel diode
replaces that enormous $R$ with about an ohm, so the current decays over milliseconds
instead of microseconds and the coil never develops more than a diode drop.

**One exponential is a statement about one energy store.** Add a capacitor and there is no
single $\tau$: the response carries two exponents, they can be a complex pair, and a
complex pair means ringing rather than settling. That is what the sandbox in this module is
showing, and what the next module is about.

**And $L$ is constant only while the core is.** Past saturation the inductance falls, so
$\tau$ falls with it and the current climbs faster than the exponential predicts — a
runaway, not an approach. Every equation in this reading assumes a component whose $L$ does
not depend on the current flowing through it.
''',
                },
            ],
            "sandbox": {
                "title": "What a second energy store adds",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 8, "zeta": 0.25, "K": 1},
                "brief": r'''
Put an inductor and a capacitor in the same circuit and something appears that no
first-order filter can do: a peak.

This is a resistor, an inductor and a capacitor in series, with the output measured
across the capacitor. Its corner is $\omega_n = 1/\sqrt{LC}$, and the damping $\zeta$
falls as the resistance falls. You do not need to design one yet. The point is to see
what the second store buys, and what it costs.
''',
                "notice": [
                    "At ζ = 0.25 the amber dot — the gain exactly at the corner — sits about 6 dB above the dashed 0 dB line. The output is twice the input at that one frequency, with nothing in the circuit that could amplify: the inductor and the capacitor are handing energy back and forth, and the source only replaces what the resistor turns into heat.",
                    "Take ζ up to 1 and the peak is gone; the dot drops to 6 dB below the line, half the input. Damping is what a resistor does to a resonance.",
                    "Above the corner the magnitude falls at 40 dB per decade and the phase ends at −180°: each store contributes 20 dB per decade and 90° of lag, and the RC and RL filters you have built are simply the one-store version.",
                    "Slide ωₙ along. The whole picture translates sideways on the logarithmic axis with its shape unchanged — the same filter, tuned somewhere else.",
                ],
            },
            "quiz": {
                "title": "Inductors and time constants",
                "minutes": 8,
                "questions": [
                    {
                        "q": "What is the magnitude of the impedance of a 10 mH inductor at 1 kHz?",
                        "opts": ["10 Ω", "62.8 Ω", "0.0159 Ω", "6.28 Ω"],
                        "a": 1,
                        "why": r'''
$|Z_L| = \omega L = 2\pi \times 1000 \times 0.010 = 62.8$ Ω. Writing $fL$ instead of
$\omega L$ gives 10 Ω — the same missing $2\pi$ that turns up in every capacitor
calculation, and worth the same care. Notice the direction: raise the frequency and
an inductor impedes *more*, where a capacitor impedes less.
''',
                    },
                    {
                        "q": "What is the time constant of a 1 kΩ resistor in series with a 100 mH inductor?",
                        "opts": ["100 µs", "100 s", "10 µs", "0.1 s"],
                        "a": 0,
                        "why": r'''
$\tau = L/R = 0.1/1000 = 10^{-4}$ s, or 100 µs. It is a ratio, not a product, and
that is the part worth remembering: multiplying gives 100 s, which is absurd for a
circuit of this size and is the standard slip. It also means that increasing the
resistance makes an RL circuit *faster*, while increasing the resistance makes an RC
circuit slower.
''',
                    },
                    {
                        "q": "A step of voltage is applied to a first-order circuit. After one time constant, how far has the output moved towards its final value?",
                        "opts": ["37%", "50%", "63%", "100%"],
                        "a": 2,
                        "why": r'''
$1 - e^{-1} = 0.632$, so 63%. The figure 37% is $e^{-1}$ itself, which is how much of
the *gap* is still left — the same number seen from the other side, and the usual
confusion. Both are worth carrying: after one $\tau$ you are 63% of the way there and
37% short, and after five $\tau$ you are 99.3% there, which is why five time constants
is the working definition of settled.
''',
                    },
                    {
                        "q": "In a series RL circuit with the output taken across the resistor, what kind of filter do you have?",
                        "opts": [
                            "A low-pass, with corner $R/(2\\pi L)$",
                            "A high-pass, with corner $R/(2\\pi L)$",
                            "A low-pass, with corner $L/(2\\pi R)$",
                            "Neither — an inductor cannot filter",
                        ],
                        "a": 0,
                        "why": r'''
The divider is $R/(R + j\omega L)$. At DC the inductor is a wire and the whole source
appears across the resistor; at high frequency the inductor's $\omega L$ dominates
and almost nothing does. That is a low-pass, cornering where $\omega L = R$, which is
$f_c = R/(2\pi L)$. Putting $L$ over $R$ instead gives a corner in seconds rather
than hertz — that combination is the time constant, and $f_c = 1/(2\pi\tau)$.
''',
                    },
                    {
                        "q": "Which statement best explains why a capacitor blocks direct current but passes alternating current?",
                        "opts": [
                            "Charge cannot cross the insulating gap, so no current can pass at any frequency",
                            "Alternating current is small enough to leak across the gap, while direct current is not",
                            "Its reactance $1/(\\omega C)$ grows without bound as the frequency falls to zero, and shrinks as it rises",
                            "The capacitor discharges itself between cycles",
                        ],
                        "a": 2,
                        "why": r'''
The reactance is the answer. "Charge cannot cross the insulating gap, so no current
can pass" is a true statement with a false conclusion attached: charge really does not
cross the gap, at any frequency — yet
alternating current flows in the wires perfectly well, because charge arriving on one
plate pushes an equal charge off the other. Nothing leaks. What changes with frequency
is how much voltage it takes to push a given current in and out of the plates, and
that is exactly what $1/(\omega C)$ measures.
''',
                    },
                ],
            },
            "blanks": {
                "title": "The two stores, side by side",
                "minutes": 8,
                "lang": "text",
                "caption": "One column is filled in. Fill in the other, and the mirror does the rest.",
                "brief": r'''
Almost everything about an inductor is a capacitor fact with the two ends of the
frequency axis swapped. That is worth setting out once as a table, because the four
substitutions and the two time constants are what every question in this module is
really asking about, and getting one row backwards costs the whole answer.

The left column is the capacitor, already known. Fill in the right.
''',
                "listing": r'''
                          R and C                     R and L

    impedance             1/(jwC)                     ___

    at DC                 an open circuit             ___

    well above f_c        a short circuit             ___

    time constant         tau = R C                   tau = ___

    raise R and the
    circuit gets          ___                         ___

    corner frequency      f_c = 1/(2 pi R C)          f_c = ___
''',
                "blanks": [
                    {
                        "prompt": "The impedance of an inductor",
                        "hole": "impedance of L",
                        "opts": ["$j\\omega L$", "$1/(j\\omega L)$", "$j\\omega/L$", "$L/(j\\omega)$"],
                        "a": 0,
                        "why": r'''
$v = L\,di/dt$, and for $i = I_p\sin\omega t$ that differentiates to
$\omega L\,I_p\cos\omega t$: the voltage amplitude is $\omega L$ times the current
amplitude, and the cosine is a quarter cycle ahead of the sine. Those two facts are
the magnitude and the $j$ of $Z_L = j\omega L$. The reciprocal form is the capacitor's,
and writing it here is the single commonest way to get an inductor question exactly
upside down.
''',
                    },
                    {
                        "prompt": "An inductor at DC",
                        "hole": "inductor at DC",
                        "opts": ["an open circuit", "a short circuit (a plain wire)", "a resistance of $L$ ohms"],
                        "a": 1,
                        "why": r'''
At DC the current is not changing, so $di/dt = 0$, so the voltage across the coil is
zero whatever current flows — and a component with no voltage across it is a piece of
wire, which is also what it looks like. This is one of the few places in electronics
where the naive answer is the right one.
''',
                    },
                    {
                        "prompt": "An inductor well above the corner",
                        "hole": "inductor at high f",
                        "opts": ["an open circuit", "a short circuit (a plain wire)"],
                        "a": 0,
                        "why": r'''
$|Z_L| = \omega L$ grows without bound as the frequency rises, and a component that
needs an unbounded voltage to pass any current is a break in the circuit. Every entry
in this table is the capacitor's entry reversed, so remembering one row and the word
"opposite" is enough for all four.
''',
                    },
                    {
                        "prompt": "The time constant of a series R-L circuit",
                        "hole": "tau for RL",
                        "opts": ["$LR$", "$L/R$", "$R/L$"],
                        "a": 1,
                        "why": r'''
A ratio, not a product. The quickest argument: the current sets off with slope
$V_s/L$ and is heading for $V_s/R$, so at its initial slope it would arrive after
$(V_s/R)/(V_s/L) = L/R$. The units agree — a henry is a volt-second per amp and an
ohm is a volt per amp, so H/Ω is a second and H·Ω is nothing. And the magnitude check
catches the slip every time: 10 mH with 470 Ω gives 21 µs one way round and 4.7
seconds the other, and 4.7 seconds is absurd for a circuit you can hold in your hand.
''',
                    },
                    {
                        "prompt": "Raise $R$ in an R-C circuit and it gets",
                        "hole": "RC vs R",
                        "opts": ["faster", "slower", "neither — $R$ does not affect the speed"],
                        "a": 1,
                        "why": r'''
$\tau = RC$, so more resistance is more time. Physically the resistor is in the path
of the charge going onto the capacitor: a bigger resistor is a narrower pipe, and
filling takes longer.
''',
                    },
                    {
                        "prompt": "Raise $R$ in an R-L circuit and it gets",
                        "hole": "RL vs R",
                        "opts": ["faster", "slower", "neither — $R$ does not affect the speed"],
                        "a": 0,
                        "why": r'''
$\tau = L/R$, so more resistance is less time — the opposite of the R-C case, and the
part that gets misremembered rather than the formula itself. The reason is that the
resistor is not in the path of anything being filled. The current's initial slope is
$V_s/L$, which does not mention $R$ at all; what a bigger resistor changes is the
destination, $V_s/R$, bringing it nearer. Same starting speed, shorter journey, less
time.
''',
                    },
                    {
                        "prompt": "The corner frequency of a series R-L circuit",
                        "hole": "f_c for RL",
                        "opts": ["$1/(2\\pi R L)$", "$L/(2\\pi R)$", "$R/(2\\pi L)$"],
                        "a": 2,
                        "why": r'''
The corner is where the reactance equals the resistance it works against, $\omega L = R$,
which rearranges to $f_c = R/(2\pi L)$. It is also $1/(2\pi\tau)$ with $\tau = L/R$,
which is the same statement — a time constant and a corner frequency are two ways of
quoting one circuit. Putting $L$ over $R$ instead gives a quantity in seconds, which
is the time constant wearing a frequency's label.
''',
                    },
                ],
            },
            "numeric": [
                {
                    "title": "A ratio, not a product",
                    "minutes": 5,
                    "brief": r'''
The first rung, and deliberately mechanical: two numbers off the drawing, one rule, one
answer.

The only decision to make is which way up the rule goes, and that is the whole point of
starting here. Sanity-check the size of what you get before writing it down — a circuit
made of a small coil and a quarter-watt resistor does not have a time constant you could
watch.
''',
                    "prompt": "What is the time constant of this circuit?",
                    "note": "Give the answer in microseconds, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "l1", "kind": "L", "x": 6, "y": 3, "rot": 0, "value": 0.033},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 10, "y": 4, "rot": 1, "value": 680},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 5], "b": [10, 7]},
                            {"a": [10, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Inductor (in series)", "value": "33 mH"},
                        {"label": "Resistor (to ground)", "value": "680 Ω"},
                    ],
                    "aside": "The time constant belongs to the circuit, not to the source, so nothing "
                             "about the supply appears in the answer. Note also that it does not depend "
                             "on where the probe is: moving it onto the inductor would turn this into a "
                             "high-pass without changing the number being asked for.",
                    "answer": 48.53,
                    "tol": 0.15,
                    "unit": "µs",
                    # Measured rather than restated: the check sweeps the drawn circuit for its
                    # -3 dB point and converts, so both component values have to be read off the
                    # schematic and any edit to either moves the expected answer.
                    "check": r'''
c.assert(c.count('R') === 1 && c.count('L') === 1, "one resistor and one inductor");
var fc = c.corner(1, 1e7);
return 1e6 / (2 * Math.PI * fc);
''',
                    "hint": r"$\tau = L/R$, in seconds, with $L$ in henries and $R$ in ohms. Convert 33 mH to 0.033 H before dividing, then convert the answer to microseconds at the very end.",
                    "wrong": r"22.44 is $LR$, the product — and read as seconds it says this circuit "
                             r"takes most of a minute to settle, which is a good enough reason on its "
                             r"own to know it is wrong. 20 606 is $1/\tau$, the pole in radians per "
                             r"second. 3280 is the corner frequency in hertz, which is the same fact "
                             r"about the same circuit but is not a time.",
                    "why": r'''
```
L     = 33 mH                             = 0.033 H
tau   = L/R = 0.033/680                   = 4.8529e-5 s
                                          = 48.53 us
```

That is the whole calculation. What is worth spending the rest of the time on is why it is
a ratio, because the formula on its own will not stop your hand writing $LR$.

The current in this loop sets off with slope $V_s/L$ — the resistor does not appear in
that, because at the instant of switch-on there is no current yet and so no voltage across
the resistor at all. It is heading for a final value of $V_s/R$. If it kept its initial
slope it would arrive after

```
t = (V_s/R) / (V_s/L) = L/R
```

and the supply voltage cancels, which is why the time constant is a property of the two
components alone. Geometrically that is the tangent at the origin, extended until it
crosses the final level.

Two checks on the answer. The units: a henry is a volt-second per amp and an ohm is a volt
per amp, so henries over ohms is seconds, while henries times ohms is nothing at all. And
the size: 48.5 µs is a plausible number for a small coil and a small resistor, where 22.4
seconds is not.

The same fact stated in frequency is $f_c = 1/(2\pi\tau) = 1/(2\pi \times 4.8529\times10^{-5})
= 3280$ Hz, which is also $R/(2\pi L) = 680/0.2073$. Either description will do; they are
the same circuit.
''',
                },
                {
                    "title": "Thirty microseconds after the switch closes",
                    "minutes": 8,
                    "brief": r'''
Second rung, and now the time constant is a stepping stone rather than the destination.
The source is switched on at $t = 0$ with the current in the coil at zero, and the question
is what the resistor has across it a little later.

Three steps: the time constant, the number of time constants that have elapsed, and the
exponential. Do them in that order and keep each intermediate value — the last one is
worth checking against the inductor's share.
''',
                    "prompt": "What is the voltage across the resistor 30.0 µs after the source is switched on?",
                    "note": "Give the answer in volts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "l1", "kind": "L", "x": 6, "y": 3, "rot": 0, "value": 0.01},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 10, "y": 4, "rot": 1, "value": 470},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 5], "b": [10, 7]},
                            {"a": [10, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "5.00 V, switched on at t = 0"},
                        {"label": "Inductor (in series)", "value": "10 mH, no current at t = 0"},
                        {"label": "Resistor (to ground)", "value": "470 Ω"},
                        {"label": "Time", "value": "30.0 µs after switch-on"},
                    ],
                    "aside": "$v_R(t) = V_s(1 - e^{-t/\\tau})$ and $v_L(t) = V_s e^{-t/\\tau}$. They add "
                             "to $V_s$ at every instant, which is Kirchhoff's voltage law and a free "
                             "check on the arithmetic: work out one, subtract, and confirm the other "
                             "from its own formula.",
                    "answer": 3.779,
                    "tol": 0.012,
                    "unit": "V",
                    # The check reads the source amplitude off the schematic and measures the time
                    # constant from the swept -3 dB point rather than assuming L/R, so the stated
                    # answer follows the drawing rather than a constant repeated from the prompt.
                    "check": r'''
c.assert(c.count('V') === 1, "one voltage source, so the step has a size");
var vs = Math.abs(c.values('V')[0]);
var tau = 1 / (2 * Math.PI * c.corner(1, 1e7));
return vs * (1 - Math.exp(-30e-6 / tau));
''',
                    "hint": r"$\tau = L/R$ first. Then $t/\tau$ — a pure number, so make sure both are in the same units before dividing. Then $1 - e^{-t/\tau}$, and only then multiply by the 5.00 V.",
                    "wrong": r"1.221 V is the voltage across the *inductor* at that moment, "
                             r"$V_se^{-t/\tau}$ — the right exponential subtracted from the wrong end. "
                             r"5.000 V is the final value, reached only after several time constants. "
                             r"3.160 V is the answer at $t = \tau$ rather than at 30 µs, which is 1.41 "
                             r"time constants. Anything in the microvolts — 32 µV, say — comes from "
                             r"$\tau = LR = 4.7$ s, against which 30 µs is indistinguishable from the "
                             r"instant of switch-on.",
                    "why": r'''
```
tau   = L/R = 0.010/470                   = 2.1277e-5 s = 21.277 us
t/tau = 30.0e-6/2.1277e-5                 = 1.4100

e^-1.41                                   = 0.244143
1 - e^-1.41                               = 0.755857
v_R   = 5.00 * 0.755857                   = 3.7793 V
```

Now the check the aside asked for. The inductor should have the rest of the source across
it, $5.00 - 3.7793 = 1.2207$ V, and its own formula says
$V_se^{-t/\tau} = 5.00 \times 0.244143 = 1.2207$ V. They agree, so the exponential was
evaluated once and used twice consistently.

Two things worth reading off the result.

**The current.** $i = v_R/R = 3.7793/470 = 8.041$ mA, against a final value of
$5.00/470 = 10.638$ mA. It is 75.6% of the way there, the same 75.6% as the voltage,
because in a series circuit the resistor's voltage is just the current with a constant
attached.

**The size.** 30 µs is a little under one and a half time constants, so the answer had to
fall between the one-tau figure of 63.2% and the two-tau figure of 86.5%. It does, and that
bracket is worth forming before doing the arithmetic rather than after — it catches a
misplaced decimal in $\tau$ instantly, which is the error that actually happens here.
''',
                },
                {
                    "title": "The resistance the coil actually sees",
                    "minutes": 10,
                    "brief": r'''
Third rung. There are two resistors now, and the question is which one sets the speed.

Neither, on its own. The rule that survives is $\tau = L/R_{th}$, where $R_{th}$ is the
resistance measured at the inductor's own two terminals with the source suppressed — a
voltage source replaced by a wire, because that is what a perfect voltage source is to any
signal you might apply. Suppress it, look back from the coil, and see what is there.
''',
                    "prompt": "What is the corner frequency of this circuit?",
                    "note": "Give the answer in hertz, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 1500},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "r2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 3300},
                            {"id": "l1", "kind": "L", "x": 12, "y": 4, "rot": 1, "value": 0.047},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                            {"a": [12, 5], "b": [12, 7]},
                            {"a": [12, 7], "b": [9, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V, frequency swept"},
                        {"label": "Resistor in series", "value": "1.50 kΩ"},
                        {"label": "Resistor to ground", "value": "3.30 kΩ"},
                        {"label": "Inductor to ground", "value": "47 mH"},
                    ],
                    "aside": "Classify it before computing anything. At DC the coil is a wire and shorts "
                             "the probe to ground; far above the corner the coil is an open circuit and "
                             "the two resistors are a plain divider. Nothing at the bottom, something at "
                             "the top — a high-pass, whose corner is quoted 3 dB below that high-frequency "
                             "level rather than below 1.",
                    "answer": 3492.0,
                    "tol": 4.0,
                    "unit": "Hz",
                    # A high-pass, so the reference is the high-frequency asymptote and not gain(lo):
                    # the check reads that asymptote off the drawn circuit and bisects the swept
                    # response for the point 3 dB below it.
                    "check": r'''
c.assert(c.count('R') === 2 && c.count('L') === 1, "two resistors and one inductor");
var ref = c.gain(1e9), lo = 1, hi = 1e7;
for (var i = 0; i < 120; i++) {
  var mid = Math.sqrt(lo * hi);
  if (c.gain(mid) < ref / Math.SQRT2) lo = mid; else hi = mid;
}
return Math.sqrt(lo * hi);
''',
                    "hint": r"Short the source in your head. The coil's top terminal now reaches ground two ways — through the 1.5 kΩ and through the 3.3 kΩ — so those two are in parallel as far as the coil is concerned. Then $\tau = L/R_{th}$ and $f_c = 1/(2\pi\tau)$.",
                    "wrong": r"5079 Hz uses the 1.50 kΩ alone and 11 175 Hz uses the 3.30 kΩ alone. "
                             r"Both are too high, and necessarily so: a parallel pair is smaller than "
                             r"either of its parts, and $R$ is downstairs in $\tau = L/R$, so dropping "
                             r"one resistor always makes the circuit look faster than it is. 16 254 Hz "
                             r"uses the series sum 4.80 kΩ, which is the right rule for a *current* "
                             r"source — one that suppresses to an open circuit — and the wrong one here.",
                    "why": r'''
Suppress the source — a voltage source becomes a wire — and look back into the circuit from
the inductor's two terminals. The bottom one is on ground. The top one reaches ground
through the 3.30 kΩ directly, and *also* through the 1.50 kΩ and then along the shorted
source. Two paths, so a parallel combination:

```
R_th  = 1500*3300/(1500 + 3300)
      = 4950000/4800                      = 1031.25 ohm
tau   = L/R_th = 0.047/1031.25            = 4.5576e-5 s = 45.58 us
f_c   = 1/(2*pi*4.5576e-5)                = 3492 Hz
```

or, in one step and without the detour through time,
$f_c = R_{th}/(2\pi L) = 1031.25/0.29531 = 3492$ Hz.

The same number the long way, as a check, by writing the transfer function out. The probed
node sees the source through $R_1$, and to ground through $R_2$ in parallel with $j\omega L$:

```
H     = Z_p/(R_1 + Z_p)  with  Z_p = R_2 || jwL

multiply out and divide through by R_1R_2:

H     = (jwL/R_1) / (1 + jwL*(1/R_1 + 1/R_2))
      = (jwL/R_1) / (1 + jwL/R_th)
```

The pole sits where $\omega L = R_{th}$, which is the corner just computed, and the
high-frequency gain is $R_{th}/R_1 = 1031.25/1500 = 0.6875$, which is also
$R_2/(R_1 + R_2) = 3300/4800$. Both routes agree, which they must, because "the resistance
the coil sees" is not a separate rule — it is what falls out of the algebra every time.

Finally, a check on the *direction* of the answer, which is available before any arithmetic
is done. Either resistor taken alone gives a shorter time constant and therefore a higher
corner:

```
R_1 alone:  tau = 0.047/1500 = 31.33 us  ->  f_c = 5079 Hz
R_2 alone:  tau = 0.047/3300 = 14.24 us  ->  f_c = 11175 Hz
```

The true time constant, 45.58 µs, is longer than both, and the true corner, 3492 Hz, is
lower than both. It has to be: a parallel combination is smaller than either resistor in
it, and a smaller $R$ in $\tau = L/R$ means a longer $\tau$ and a lower corner. Getting a
figure between the two single-resistor estimates would mean the parallel formula had been
inverted somewhere, and that is worth knowing before you have finished the calculation
rather than after.
''',
                },
                {
                    "title": "A source that pushes current instead of voltage",
                    "minutes": 13,
                    "brief": r'''
The last rung, and real work. The source is a current source: it forces 5.00 mA RMS through
itself no matter what voltage that takes, which is the opposite bargain from the voltage
sources everywhere else in this course.

That changes two things and leaves everything else alone. Suppressing a current source
means *opening* it, not shorting it, so the resistance the coil sees is different from what
the drawing might suggest at a glance. And there is no obvious "input voltage" to take a
ratio against, so the answer has to be built from the current outwards.

Work out what the circuit does at DC first. It is the anchor for everything else.
''',
                    "prompt": "What RMS voltage does a meter on the probe read at 8.00 kHz?",
                    "note": "Give the answer in volts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "is", "kind": "I", "x": 3, "y": 5, "rot": 1, "value": 0.005},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 1, "value": 2200},
                            {"id": "l1", "kind": "L", "x": 9, "y": 3, "rot": 0, "value": 0.1},
                            {"id": "out", "kind": "OUT", "x": 12, "y": 3, "rot": 0, "value": 0},
                            {"id": "r2", "kind": "R", "x": 12, "y": 4, "rot": 1, "value": 1000},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [6, 3]},
                            {"a": [6, 5], "b": [6, 7]},
                            {"a": [6, 7], "b": [3, 7]},
                            {"a": [6, 3], "b": [8, 3]},
                            {"a": [10, 3], "b": [12, 3]},
                            {"a": [12, 5], "b": [12, 7]},
                            {"a": [12, 7], "b": [6, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "5.00 mA RMS at 8.00 kHz, into the top rail"},
                        {"label": "Resistor at the source", "value": "2.20 kΩ to ground"},
                        {"label": "Inductor (in series)", "value": "100 mH"},
                        {"label": "Resistor at the probe", "value": "1.00 kΩ to ground"},
                    ],
                    "aside": "A perfect current source has infinite internal resistance, so suppressing "
                             "it leaves a break rather than a wire. With that break in place, trace the "
                             "coil's two terminals back to each other: the path runs through one "
                             "resistor and then the other, in series — not in parallel, which is the "
                             "answer the drawing tempts you into.",
                    "answer": 1.846,
                    "tol": 0.008,
                    "unit": "V",
                    # Solved rather than restated: the source current, both resistors and the
                    # inductance are all read off the schematic by the solver, so no constant from
                    # the prompt is being trusted here.
                    "check": r'''
c.assert(c.count('I') === 1, "one current source");
c.assert(c.count('R') === 2 && c.count('L') === 1, "two resistors and one inductor");
return c.gain(8000);
''',
                    "hint": r"Find the DC output first: at DC the coil is a wire, so the two resistors are in parallel and the source current divides between them. Then the corner, from $\tau = L/(R_1 + R_2)$. Then the low-pass magnitude $1/\sqrt{1 + x^2}$.",
                    "wrong": r"3.438 V is the DC output — the right circuit at the wrong frequency, and "
                             r"8 kHz is above the corner where the coil is already throwing most of it "
                             r"away. 5.000 V is $5.00$ mA sent entirely through the 1.00 kΩ, with the "
                             r"2.20 kΩ forgotten. 1.337 V divides by $3200 + 5026.5$, adding a "
                             r"resistance to a reactance arithmetically when they are a quarter cycle "
                             r"apart and combine to 5958.7 Ω. 0.4658 V uses $R_1\|R_2 = 687.5$ Ω as the "
                             r"resistance the coil sees, which is what suppressing a current source by "
                             r"shorting it — the voltage-source rule, misapplied — would give.",
                    "why": r'''
**At DC**, the coil is a plain wire, so the probe node and the source node are the same
node and the two resistors sit in parallel across the source:

```
R_1||R_2 = 2200*1000/3200                 = 687.5 ohm
V_dc     = 5.00e-3 * 687.5                = 3.4375 V
```

**The corner.** Open the current source — that is what suppressing one means — and walk
from the coil's left terminal to its right terminal the long way: up through nothing, down
$R_1$ to ground, along the ground rail, back up $R_2$. The two resistors are in *series*
from the coil's point of view, not in parallel:

```
R_th  = 2200 + 1000                       = 3200 ohm
f_c   = R_th/(2*pi*L) = 3200/(2*pi*0.1)
      = 3200/0.628319                     = 5093 Hz
```

**The answer.** It is a low-pass — the coil is a wire at DC and a break far above — so the
magnitude falls off as $1/\sqrt{1 + x^2}$ with $x = f/f_c$:

```
x     = 8000/5093.0                       = 1.5708
x^2                                       = 2.4674
1 + x^2                                   = 3.4674
sqrt                                      = 1.86210
|H|                                       = 0.537029
V_out = 3.4375 * 0.537029                 = 1.8460 V rms
```

The same number without ever mentioning the corner, straight from the impedances. The
current splits between $R_1$ and the series pair $j\omega L + R_2$, and only the second
branch reaches the probe:

```
X_L   = 2*pi*8000*0.1                     = 5026.5 ohm
V_out = I * R_1 * R_2 / sqrt((R_1+R_2)^2 + X_L^2)
      = 5.00e-3 * 2200 * 1000 / sqrt(3200^2 + 5026.5^2)
      = 11000 / sqrt(1.0240e7 + 2.5266e7)
      = 11000 / 5958.7                    = 1.8460 V rms
```

Both routes land on the same value, and the second one shows where the $R_1 + R_2$ came
from without any appeal to Thévenin: it is the real part of the denominator, and it is a
sum because the coil's current has to pass through both resistors in turn on its way round
the loop.

The trap here is worth naming, because it is the reason this rung exists. At DC the two
resistors are in *parallel* — that is a fact about how the source's current divides between
them. The resistance that sets the *time constant* is a different question about a different
pair of terminals, and from there the two resistors are in *series*. Both are true at once,
of the same drawing, and answering the second question with the first answer gives 687.5 Ω,
a corner of 1094 Hz and an output of 0.4658 V — a quarter of the right answer, with no
arithmetic slip anywhere in it.
''',
                },
            ],
            "derive": {
                "title": "Where L over R comes from when there are two resistors",
                "minutes": 14,
                "vars": ["V_in", "V_a", "s", "R_1", "R_2", "L", "H"],
                "brief": r'''
One node equation, and the pole it produces.

The circuit is the one from the third numeric unit: the source drives $R_1$; node $a$ sits
at the far end of it; $R_2$ runs from $a$ down to ground; and the inductor $L$ runs from
$a$ down to ground as well. The output is $V_a$.

Write $s$ for $j\omega$ throughout, so an inductor $L$ is an impedance $sL$ — and therefore
an admittance $1/(sL)$ — while a resistor $R$ is an admittance $1/R$. Nothing in the
argument is specific to sinusoids; $s$ is carried as a symbol and only becomes $j\omega$
when a number is wanted.

The aim is not the transfer function for its own sake. It is to watch $R_1 \| R_2$ appear
in the denominator without anyone having invoked a rule about it.
''',
                "steps": [
                    {
                        "prompt": "Start with what arrives at node $a$. Only $R_1$ brings current in, from the source. Write that current in terms of $V_{in}$, $V_a$ and $R_1$.",
                        "given": "One end of $R_1$ is held at $V_{in}$ by the source; the other end is node $a$.",
                        "answer": "\\frac{V_{in} - V_a}{R_1}",
                        "placeholder": "\\frac{\\ldots}{R_1}",
                        "hint": "Ohm's law. The voltage across $R_1$ is the difference between the voltages at its two ends, and the current is that difference divided by the resistance.",
                        "deconstruct": [
                            "The voltage across $R_1$ is $V_{in} - V_a$.",
                            "Divide by $R_1$ to turn a voltage across a resistor into a current through it.",
                        ],
                    },
                    {
                        "prompt": "Now what leaves node $a$. There are two ways down to ground: through $R_2$, and through the inductor. Write the total current leaving, in terms of $V_a$, $R_2$, $s$ and $L$.",
                        "given": "Both components have their far end on the ground rail, so each has the full $V_a$ across it. The inductor's admittance is $1/(sL)$.",
                        "answer": "\\frac{V_a}{R_2} + \\frac{V_a}{s L}",
                        "placeholder": "\\frac{V_a}{R_2} + \\ldots",
                        "hint": "Current is admittance times the voltage across the component. Do it twice and add.",
                        "deconstruct": [
                            "Through $R_2$: admittance $1/R_2$ times $V_a$.",
                            "Through the inductor: admittance $1/(sL)$ times $V_a$.",
                            "Nothing else touches node $a$, so those two are the whole of the outgoing current.",
                        ],
                    },
                    {
                        "prompt": "Set arriving equal to leaving, and solve for $H = V_a/V_{in}$. Clear the fractions — multiplying every term by $sLR_1R_2$ does it in one move — and give $H$ as a single ratio.",
                        "given": "The equation to rearrange is $\\dfrac{V_{in} - V_a}{R_1} = \\dfrac{V_a}{R_2} + \\dfrac{V_a}{sL}$.",
                        "answer": "\\frac{s L R_2}{s L (R_1 + R_2) + R_1 R_2}",
                        "placeholder": "\\frac{s L R_2}{\\ldots}",
                        "hint": "After clearing fractions the left side is $sLR_2(V_{in} - V_a)$ and the right side is $sLR_1V_a + R_1R_2V_a$. Collect every $V_a$ on one side and divide.",
                        "deconstruct": [
                            "Multiplying through by $sLR_1R_2$ gives $sLR_2(V_{in} - V_a) = sLR_1V_a + R_1R_2V_a$.",
                            "Expand the left side and move its $V_a$ term across: $sLR_2V_{in} = V_a(sLR_2 + sLR_1 + R_1R_2)$.",
                            "The two $sL$ terms collect into $sL(R_1 + R_2)$.",
                            "Divide both sides by $V_{in}$ and by the bracket.",
                        ],
                    },
                    {
                        "prompt": "A first-order response is standardly written with a 1 as the constant term of the denominator, $\\dfrac{\\text{something}}{1 + s\\tau}$. Divide top and bottom by $R_1R_2$ and read off $\\tau$, in terms of $L$, $R_1$ and $R_2$.",
                        "answer": "\\frac{L (R_1 + R_2)}{R_1 R_2}",
                        "placeholder": "\\frac{L\\,(\\ldots)}{\\ldots}",
                        "hint": "After dividing, the coefficient of $s$ in the denominator is $L(R_1+R_2)/(R_1R_2)$, and that coefficient is the time constant.",
                        "deconstruct": [
                            "Dividing the denominator by $R_1R_2$ turns it into $1 + sL(R_1 + R_2)/(R_1R_2)$.",
                            "Whatever multiplies $s$ there is $\\tau$, because the denominator has to read $1 + s\\tau$.",
                        ],
                    },
                    {
                        "prompt": "Finally, the gain a long way above the corner. Let $s \\to \\infty$ in the expression from step three — the $R_1R_2$ term becomes negligible beside $sL(R_1+R_2)$ — and write what is left.",
                        "answer": "\\frac{R_2}{R_1 + R_2}",
                        "placeholder": "\\frac{R_2}{\\ldots}",
                        "hint": "Drop the constant term from the denominator and cancel the $sL$ that now appears top and bottom.",
                        "deconstruct": [
                            "For large $s$ the denominator is dominated by $sL(R_1 + R_2)$.",
                            "So $H \\to sLR_2 / (sL(R_1 + R_2))$.",
                            "The $sL$ cancels.",
                        ],
                    },
                ],
                "closing": r'''
Look at what step four produced:

$$\tau = \frac{L(R_1 + R_2)}{R_1R_2} = \frac{L}{\dfrac{R_1R_2}{R_1 + R_2}} = \frac{L}{R_1 \| R_2}$$

Nobody invoked a rule about parallel resistance. Two node currents were added and the
fractions were cleared, and $R_1 \| R_2$ arrived on its own, downstairs, exactly where
$\tau = L/R$ says a resistance belongs. That is what "the resistance the inductor sees"
means: not a mnemonic laid on top of the algebra, but a name for the thing the algebra
keeps producing.

The reason it comes out as a parallel combination is visible in step two. The two outgoing
paths were *added as admittances*, because both hang off the same node, and adding
admittances is what "in parallel" means. The inductor is looking back into a node with two
conductances on it, and it cannot tell them apart.

Two consequences worth carrying forward.

**Suppressing the source is not an extra assumption; it is what the algebra already did.**
$V_{in}$ appears in exactly one place, the numerator, and never in the denominator. The
pole — and therefore the time constant, and therefore the corner — cannot depend on the
source at all. Setting the source to zero to find $R_{th}$ is a shortcut for reading the
denominator, not a separate physical claim.

**And the same denominator would have appeared with the probe anywhere.** Move the output
to some other node in this circuit and the numerator changes; $1 + s\tau$ does not. That is
why a circuit has *a* time constant rather than one per measurement, and it is the same
observation module 5 made about a corner not moving when the probe does — seen this time
from the algebra rather than from the impedances.

One last exercise in reading the result rather than deriving it. Put the numbers from the
third numeric unit in: $L = 47$ mH, $R_1 = 1.5$ kΩ, $R_2 = 3.3$ kΩ.

$$\tau = \frac{0.047 \times 4800}{1500 \times 3300} = \frac{225.6}{4.95\times10^6} = 45.58\ \mu s$$

which is $L$ over 1031.25 Ω, and $f_c = 1/(2\pi\tau) = 3492$ Hz. The high-frequency gain
from step five is $3300/4800 = 0.6875$, so this is a high-pass that never quite reaches 1 —
and the reason it does not is $R_1$ and $R_2$ acting as an ordinary resistive divider once
the coil has taken itself out of the circuit.
''',
            },
            "build": {
                "title": "An RL circuit with a 100 µs time constant",
                "minutes": 25,
                "brief": r'''
Same first-order behaviour, different pair of components, and this time the
specification is written in the time domain.

You are given a source, a ground and a 1 kΩ load resistor wired directly across the
source, with the probe on the resistor. Insert an inductor in series so that the
circuit has a **time constant of 100 µs**.

What that must produce:

1. **At DC the output still equals the source**, because an ideal inductor is a plain
   wire to a steady voltage.
2. **A step reaches 63% of its final value after 100 µs.** That is what a time
   constant of 100 µs means.
3. **The corner sits at 1591.5 Hz**, which is the same statement in frequency:
   $f_c = 1/(2\pi\tau)$.
4. **It rolls off at 20 dB per decade** above the corner, like every first-order
   circuit.

$\tau = L/R$, so the resistor you were given and the time constant you were asked for
fix the inductance between them. You may change the resistor if you prefer, provided
the ratio comes out right.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [9, 3]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "L", "x": 5, "y": 3, "rot": 0, "value": 0.1},
                        {"id": "p3", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1000},
                        {"id": "p4", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [9, 3]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 6], "b": [3, 6]},
                    ],
                },
                "checks": [
                    {"name": "at DC the output equals the source", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(Math.abs(c.vout()), vs, 0.01,
  "an ideal inductor is a plain wire at DC, so the whole source should appear across the resistor");
'''},
                    {"name": "a step reaches 63% after 100 microseconds", "code": r'''
var s = c.step(1e-3);
var last = Math.abs(s.v[s.v.length - 1]);
c.assert(last > 1e-9, "the output never rises at all — check that the source reaches the resistor");
var i = 0;
while (i < s.t.length - 1 && s.t[i] < 1e-4) i++;
c.close(Math.abs(s.v[i]) / last, 0.632, 0.06,
  "after one time constant a first-order step should be 63% of the way to its final value");
'''},
                    {"name": "the corner is at 1591.5 Hz", "code": r'''
var fc = c.corner(10, 1e6);
c.close(fc, 1591.55, 0.05,
  "measured corner " + c.fmt(fc, "Hz") + "; a 100 microsecond time constant corners at 1/(2*pi*tau)");
'''},
                    {"name": "it rolls off at 20 dB per decade", "code": r'''
var ratio = c.gain(15915) / c.gain(10);
c.close(ratio, 0.0995, 0.08,
  "a decade above a first-order corner the output should be about a tenth of the pass-band value");
'''},
                ],
                "hints": [
                    "The inductor goes in series between the source and the top of the resistor, exactly where the resistor went in the RC filter.",
                    "Delete the wire from the source to the probe first, then place the inductor in the gap.",
                    "$\\tau = L/R$, so with 1 kΩ you need $L = \\tau R = 10^{-4} \\times 1000 = 0.1$ H.",
                    "If the step check says the output never rises, one of the inductor's pins is not wired to anything.",
                ],
            },
            "lab": {
                "title": "The RL step, by formula and by simulation",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
The circuit you just drew, checked two ways.

`tau(r, l)` returns the time constant $L/R$ in seconds.

`resistor_voltage(r, l, vs, t)` returns the analytic answer: the voltage across the
resistor at time `t` after a step of `vs` volts is applied, which is
$v_s\left(1 - e^{-t/\tau}\right)$. `t` may be a NumPy array, and if you use
`np.exp` it will work for both an array and a single number without any extra effort.

`simulate(r, l, vs, dt, n)` gets the same answer without the formula. The inductor
obeys $L\,di/dt = v_s - iR$, so step the current forward:

```text
i_next = i + dt * (vs - i * r) / l
```

Start from `i = 0`, record the resistor voltage `i * r` **before** each update, and
return a list of `n` values. Then compare the two: they should agree.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def tau(r, l):
    """The time constant of a series R-L circuit, in seconds."""
    # TODO
    return 0.0


def resistor_voltage(r, l, vs, t):
    """Analytic voltage across the resistor, t seconds after a step of vs volts."""
    # TODO
    return 0.0


def simulate(r, l, vs, dt, n):
    """Forward Euler on the inductor current; return n resistor voltages."""
    i = 0.0
    out = []
    # TODO: record i * r, then advance the current by one step, n times.
    return out


if __name__ == "__main__":
    R, L, VS = 1000.0, 0.1, 5.0
    print("tau:", tau(R, L), "s")
    print("analytic at one tau:", round(float(resistor_voltage(R, L, VS, tau(R, L))), 6))
    vs_sim = simulate(R, L, VS, 1e-6, 500)
    print("simulated at one tau:", round(vs_sim[100], 6) if len(vs_sim) > 100 else None)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def tau(r, l):
    """The time constant of a series R-L circuit, in seconds."""
    return float(l) / float(r)


def resistor_voltage(r, l, vs, t):
    """Analytic voltage across the resistor, t seconds after a step of vs volts."""
    return vs * (1.0 - np.exp(-np.asarray(t, dtype=float) / tau(r, l)))


def simulate(r, l, vs, dt, n):
    """Forward Euler on the inductor current; return n resistor voltages."""
    i = 0.0
    out = []
    for _ in range(n):
        out.append(i * r)
        i = i + dt * (vs - i * r) / l
    return out


if __name__ == "__main__":
    R, L, VS = 1000.0, 0.1, 5.0
    print("tau:", tau(R, L), "s")
    print("analytic at one tau:", round(float(resistor_voltage(R, L, VS, tau(R, L))), 6))
    vs_sim = simulate(R, L, VS, 1e-6, 500)
    print("simulated at one tau:", round(vs_sim[100], 6) if len(vs_sim) > 100 else None)
'''}],
                "hints": [
                    "`tau` is a ratio: inductance over resistance. If the number comes out enormous, they are the wrong way round.",
                    "`np.exp` accepts an array, so `resistor_voltage` needs no loop and no `if`.",
                    "In `simulate`, append first and update afterwards — otherwise the first entry is already one step in and the response appears to start above zero.",
                ],
                "tests": [
                    {"name": "the time constant is a ratio, not a product", "code": r'''
_t = tau(1000.0, 0.1)
assert abs(_t - 1e-4) < 1e-15, f"L/R = 0.1/1000 = 100 microseconds; got {_t}"
_t2 = tau(2000.0, 0.1)
assert _t2 < _t, "more resistance makes an R-L circuit faster, not slower"
'''},
                    {"name": "the analytic step is 63% after one tau and 99.3% after five", "code": r'''
import numpy as np
_v1 = float(resistor_voltage(1000.0, 0.1, 5.0, 1e-4))
_v5 = float(resistor_voltage(1000.0, 0.1, 5.0, 5e-4))
assert abs(_v1 - 3.160602794142788) < 1e-9, f"one tau should give 0.6321*5 = 3.1606 V, got {_v1}"
assert abs(_v5 - 4.966310265004573) < 1e-9, f"five taus should give 4.9663 V, got {_v5}"
'''},
                    {"name": "the analytic step handles an array of times", "code": r'''
import numpy as np
_v = resistor_voltage(1000.0, 0.1, 5.0, np.array([0.0, 1e-4, 1e9]))
assert len(_v) == 3, f"expected three values back, got {_v}"
assert abs(_v[0]) < 1e-12, f"at t = 0 the current is still zero, so the resistor sees 0 V; got {_v[0]}"
assert abs(_v[2] - 5.0) < 1e-9, f"long afterwards the inductor is a wire and the resistor sees all 5 V; got {_v[2]}"
'''},
                    {"name": "the simulation starts at zero and has the right length", "code": r'''
_s = simulate(1000.0, 0.1, 5.0, 1e-6, 500)
assert len(_s) == 500, f"expected 500 samples, got {len(_s)}"
assert abs(_s[0]) < 1e-15, f"the current starts at zero, so the first sample is 0 V; got {_s[0]}"
'''},
                    {"name": "the simulation agrees with the formula", "code": r'''
import numpy as np
_s = simulate(1000.0, 0.1, 5.0, 1e-6, 500)
_want = float(resistor_voltage(1000.0, 0.1, 5.0, 100 * 1e-6))
assert abs(_s[100] - _want) / _want < 0.01, \
    f"at one tau the simulation gives {_s[100]:.6f} and the formula {_want:.6f} — they should agree to 1%"
assert abs(_s[-1] - 5.0) < 0.05, f"after 500 microseconds it should be close to 5 V, got {_s[-1]}"
'''},
                ],
            },
        },
        # ---- M7 -----------------------------------------------------------
        {
            "title": "Series resonance, Q and bandwidth",
            "summary": "Put both energy stores in one loop and their reactances cancel at a single frequency. Everything sharp in electronics starts here.",
            "concepts": [
                "In a series $R$–$L$–$C$ loop the two reactances have opposite signs — $+\\omega L$ and $-1/(\\omega C)$ — so at one frequency they cancel exactly. That is **resonance**: $\\omega_0 = \\dfrac{1}{\\sqrt{LC}}$, or $f_0 = \\dfrac{1}{2\\pi\\sqrt{LC}}$. There the impedance is not merely small, it is exactly $R$, and the current is at its largest.",
                "One circuit, three filters, depending on where the probe goes. Across the resistor it is a **band-pass**, unity gain at $f_0$ and falling on both sides. Across the capacitor it is a second-order low-pass; across the inductor, a second-order high-pass. Both of those roll off at 40 dB per decade, because there are two energy stores.",
                "$Q = \\dfrac{\\omega_0 L}{R} = \\dfrac{1}{R}\\sqrt{\\dfrac{L}{C}}$ is the **quality factor**: the reactance at resonance divided by the resistance. It is the one number that says how sharp the circuit is, and a resonator is usually described by $f_0$ and $Q$ rather than by its three components.",
                "The −3 dB **bandwidth** of the band-pass is $\\text{BW} = f_0/Q$ in hertz — equivalently $R/(2\\pi L)$, which is the same statement with the resistance made visible. Damping and quality are one quantity seen twice: $\\zeta = 1/(2Q)$, so the $\\zeta = 0.05$ that made the Bode sandbox peak sharply is a $Q$ of 10.",
                "At resonance the voltage across the inductor and the voltage across the capacitor are each **$Q$ times the source**, and exactly opposite, so they cancel in the loop and the source never sees them. A 10 V drive into a $Q$ of 50 puts 500 V across the capacitor. This is how resonance is useful, and it is also how a low-voltage circuit destroys a component rated for the supply.",
            ],
            "read": [
                {
                    "title": "Two reactances that cancel",
                    "minutes": 14,
                    "body": r'''
Two components in this course have been called opposites, and so far that has been a
statement about the two ends of the frequency axis: a capacitor blocks at DC and passes
high frequencies, an inductor does the reverse. Put both in the same loop and the
opposition stops being a remark about the extremes. It becomes a subtraction that
happens at every frequency, and at exactly one frequency the subtraction comes out
zero.

## Fix the current, and ask what each component demands

A series loop has one current in it. Whatever that current is, it is the same current
in the resistor, in the inductor and in the capacitor, because a series loop offers
nowhere else to go. So the honest way to read one is to fix the current and ask what
voltage each component demands in return.

Let the current be $i(t) = I_p\sin\omega t$.

The **resistor** demands $v_R = I_p R\sin\omega t$ — in step with the current, always,
because a resistor has no memory of anything.

The **inductor** demands $v_L = L\,\dfrac{di}{dt} = \omega L\,I_p\cos\omega t$. A cosine
is a sine shifted a quarter of a cycle earlier, so the coil's voltage arrives *before*
the current it belongs to. It has to: the coil objects to the current changing, and the
current changes fastest as it sweeps through zero, a quarter cycle before it reaches
its peak.

The **capacitor** demands
$v_C = \dfrac{1}{C}\displaystyle\int i\,dt = -\dfrac{I_p}{\omega C}\cos\omega t$ — the
same cosine with a minus sign, which is a quarter of a cycle *later*. It has to as
well: charge must arrive before there is any voltage to show for it, so the capacitor's
voltage lags behind the current that delivered it.

Now count quarters. A quarter cycle early and a quarter cycle late are half a cycle
apart. **In a series loop the inductor's voltage and the capacitor's voltage are exactly
antiphase, at every frequency, always.** When one is at its positive peak the other is
at its negative peak. They do not merely differ in size; they point in opposite
directions round the loop, and Kirchhoff's voltage law adds them with that sign — which
is to say it subtracts them.

That is the whole mechanism. Everything below is bookkeeping.

## Where the subtraction comes out zero

The two sizes are the reactances already met. $X_L = \omega L$ rises in proportion to
frequency, from zero. $X_C = 1/(\omega C)$ falls as the reciprocal of frequency, from
unbounded. One curve climbing and one falling cross exactly once, and at the crossing
the two demands are equal — and because they oppose, equal means cancelled:

$$\omega_0 L = \frac{1}{\omega_0 C} \quad\Longrightarrow\quad \omega_0^2 = \frac{1}{LC}
\quad\Longrightarrow\quad \omega_0 = \frac{1}{\sqrt{LC}}, \qquad
f_0 = \frac{1}{2\pi\sqrt{LC}}$$

Written as impedances it is one line. Series impedances add; the inductor contributes
$j\omega L$ and the capacitor $\dfrac{1}{j\omega C} = -\dfrac{j}{\omega C}$, so

$$Z = R + j\left(\omega L - \frac{1}{\omega C}\right)$$

and the bracket is the net demand of the two stores together. Below $f_0$ it is
negative and the loop behaves capacitively; above $f_0$ it is positive and the loop
behaves inductively; at $f_0$ it is zero and **the loop is indistinguishable from a
plain resistor of $R$ ohms** — with two components inside it that between them store
energy and dissipate none.

Two things are worth noticing in that formula for $f_0$. The resistance is not in it:
$R$ does not move the resonance, only sharpens or blunts it, which is the next reading.
And $L$ and $C$ appear only as a product, so a hundredfold increase in one can be paid
for by a hundredfold decrease in the other with the resonance left exactly where it
was. That freedom is what makes a resonator designable — the product $LC$ says *where*,
and the ratio $L/C$ says everything else.

## The mechanical picture, if you want one

A mass on a spring. Push it at the wrong rate and your effort goes into fighting either
the spring or the mass; push at its natural rate and the spring hands its energy to the
mass and the mass hands it straight back, and all you supply is the friction. The
inductor is the mass — it resists a change of current the way a mass resists a change
of velocity. The capacitor is the spring. The resistor is the friction, and it is the
only element in the loop that takes energy out for good.

At resonance the two stores pass one packet of energy back and forth twice per cycle.
The source never has to supply that packet again; it only replaces what the resistor
has turned into heat. That is the physical reason the impedance comes out as exactly
$R$ and nothing more.

## Worked: 10 mH, 100 nF and 10 Ω, driven at 1.00 V rms

Where the resonance is:

```
LC        = 1.0e-2 * 1.0e-7                = 1.0e-9
sqrt(LC)                                   = 3.16228e-5
w_0       = 1/sqrt(LC)                     = 31623 rad/s
f_0       = 31623/6.28319                  = 5032.9 Hz
```

What the components are doing there:

```
X_L       = w_0 L     = 31623 * 0.010      = 316.23 ohm
X_C       = 1/(w_0 C) = 1/(31623 * 1e-7)   = 316.23 ohm
X         = X_L - X_C                      = 0
|Z|       = sqrt(R^2 + X^2) = R            = 10.00 ohm
I         = 1.00/10.00                     = 100.0 mA
```

Two 316 Ω obstacles in the loop, and the current behaves as though neither were there.
Now step off resonance by a fifth in each direction and watch what that costs:

```
at 4.00 kHz:  w = 25133 rad/s
  X_L = 25133 * 0.010                      = 251.33 ohm
  X_C = 1/(25133 * 1e-7)                   = 397.89 ohm
  X   = 251.33 - 397.89                    = -146.56 ohm
  |Z| = sqrt(10^2 + 146.56^2)              = 146.90 ohm
  I   = 1.00/146.90                        = 6.807 mA

at 6.00 kHz:  w = 37699 rad/s
  X_L = 37699 * 0.010                      = 376.99 ohm
  X_C = 1/(37699 * 1e-7)                   = 265.26 ohm
  X   = 376.99 - 265.26                    = 111.73 ohm
  |Z| = sqrt(10^2 + 111.73^2)              = 112.18 ohm
  I   = 1.00/112.18                        = 8.914 mA
```

A move of about a fifth off resonance cuts the current by a factor of fifteen going down
and eleven going up. The two are not equal, and the reason is worth having early: a
resonator is symmetric in frequency *ratios*, not in hertz. The partner of 4.00 kHz is
not 6.00 kHz but $5032.9^2/4000 = 6332$ Hz, and at that frequency
$X_L = 397.89$ and $X_C = 251.33$ — the same pair of numbers as at 4 kHz with their
roles swapped, so the same $|Z|$ and the same 6.807 mA. Notice also
that the resistor barely appears in either off-resonance answer — $\sqrt{10^2 + 146.56^2}$
is 146.90, which is 146.56 with a rounding error attached. Away from resonance the loop
is its reactance; at resonance the loop is its resistance; and the transition between
those two regimes is the entire subject.

## One loop, three filters

The current is common to all three components, so once you know the current you know
every voltage in the circuit. Which means one series R–L–C loop is three different
filters depending only on where you put the probe.

**Across the resistor**: $H = \dfrac{R}{R + jX}$. At $f_0$, $X = 0$ and $H = 1$ exactly,
with no phase shift. Far below, $X \to -\infty$; far above, $X \to +\infty$; either way
$|H| \to 0$. A **band-pass**, unity gain at the centre and skirts falling at 20 dB per
decade on both sides.

**Across the capacitor**: at DC the capacitor is an open circuit and takes the whole
source, so $|H| \to 1$. Far above resonance $|H| \to 1/(\omega^2 LC)$, which falls at
40 dB per decade. A second-order **low-pass**.

**Across the inductor**: the mirror image, a second-order **high-pass**, zero at DC and
unity far above.

All three share the same $f_0$ and the same sharpness, because they share the same
denominator $R + jX$ — the poles belong to the loop, not to the probe. Only the
numerator changes.

And here is the fact that makes resonance useful rather than merely tidy. At $f_0$ the
current is $V_s/R$, so

$$|V_L| = \frac{V_s}{R}\,\omega_0 L, \qquad |V_C| = \frac{V_s}{R}\cdot\frac{1}{\omega_0 C}$$

and both of those are $V_s$ multiplied by (reactance at resonance)/(resistance). For the
worked circuit that factor is $316.23/10 = 31.6$: a 1.00 V source produces 31.6 V across
the capacitor and 31.6 V across the inductor. They are antiphase, so round the loop they
cancel and the source sees only the 1.00 V across the resistor. Nothing is amplifying.
The two stores are trading the same energy, and the multiplier has a name — $Q$ — which
is the next reading.

## Worked: putting a resonance on 455 kHz

Design goes the other way: the frequency is given and a component has to be found. A
220 µH coil is on the shelf; what capacitor puts its resonance on the 455 kHz
intermediate frequency that every superheterodyne radio ever built runs at?

```
w_0   = 2*pi*455000                        = 2.85885e6 rad/s
w_0^2                                      = 8.17302e12
C     = 1/(w_0^2 L) = 1/(8.17302e12 * 2.2e-4)
      = 1/1.79806e9                        = 5.5615e-10 F
                                           = 556.2 pF
```

No such capacitor exists as a standard part. The nearest E12 value is 560 pF, so put
that in and ask what you actually got:

```
LC    = 2.2e-4 * 5.6e-10                   = 1.2320e-13
sqrt(LC)                                   = 3.50999e-7
f_0   = 1/(2*pi*3.50999e-7)                = 453.4 kHz
```

1.6 kHz low, or 0.35%. Two things follow. First, the error in frequency is *half* the
error in capacitance — 560 pF is 0.69% above 556.2 pF, and $f_0$ depends on
$1/\sqrt{C}$, so the frequency moved by half of that. A square root halves every
fractional error, which is the one piece of good news in resonator design. Second,
0.35% sounds harmless and often is not: a 455 kHz filter sharp enough to be worth
building has a bandwidth of a few kilohertz, so being 1.6 kHz off centre can be a
serious fraction of the passband. That is why real resonators have a trimmer capacitor
or an adjustable core, and why the next reading is about the quantity that decides how
much that 1.6 kHz matters.

## The mistake, and why it is tempting

The mistake is adding the two reactances instead of subtracting them:
$|Z| = \sqrt{R^2 + (X_L + X_C)^2}$.

It is tempting for an excellent reason: *series impedances add* is true, drilled, and
the rule you are supposed to reach for. The trap is that it is a statement about complex
numbers. Adding $+jX_L$ to $-jX_C$ **is** the addition — and performed on the
magnitudes it comes out as a subtraction. The minus sign was never optional; it was
carried in the $j$ from the moment the capacitor's quarter-cycle lag was written down.

The damage is not subtle. For the worked circuit at resonance, adding gives
$X_L + X_C = 632.5$ Ω and a current of 1.58 mA where the truth is 100.0 mA. The factor
between them is 63.2, which is not a coincidence: it is twice the 31.6 that keeps
turning up, and the reading after this one explains why.

The related conceptual slip is to say that at resonance the impedance is zero. It is
$R$, and $R$ is never zero, because every real loop contains wire, a coil wound from
wire, and a source that is not perfect. If the impedance genuinely were zero the current
would be unbounded and the question would have no answer.

The third is to conclude that because the two reactances cancel, the two components can
be ignored. They cancel *in the loop*, as seen by the source. Each of them individually
still has 31.6 times the source voltage across it, and a capacitor does not care that
its voltage is cancelled somewhere else — it only cares whether it is above its rating.

## Where this stops holding

**The $R$ in every formula here is the whole loop's resistance, not the resistor you
drew.** The coil is wound from wire and brings its own few ohms; the capacitor has an
equivalent series resistance; the source has an output resistance. At resonance those
are the only things left, so they are the only things that matter, and a resonator
whose drawn resistor is 2 Ω may well behave like one with 6 Ω. The next reading treats
that as its main practical problem rather than a footnote.

**A real capacitor is an inductor above its own self-resonance, and a real coil is a
capacitor above its.** Every component has stray inductance in its leads and stray
capacitance between its turns, so the neat story of one rising curve and one falling
curve crossing exactly once is true only across the band where both parts still are
what the label says. A 100 nF ceramic capacitor with 8 nH of lead inductance is already
inductive above about 5.6 MHz, and using it as a capacitor there does the opposite of
what the schematic says.

**This is *series* resonance, and the parallel arrangement inverts every conclusion.**
Put the same $L$ and $C$ side by side rather than end to end and the impedance goes to a
*maximum* at the same $f_0$, the current from the source goes to a *minimum*, and the
large circulating current is inside the loop rather than through the source. Same
formula for $f_0$, opposite consequences everywhere else. That is the next module, and
the fastest way to get a resonance question wrong is to answer it with the other
topology's rules.

**And all of it assumes $L$ and $C$ are constants.** A ferrite core saturates, so a
coil's inductance falls once the current is large enough; a class-2 ceramic capacitor
loses a good fraction of its capacitance under a DC bias. Either effect moves $f_0$ as
the drive level changes, and a resonance whose frequency depends on how hard you drive
it is no longer a linear circuit at all — the transfer function you computed is a
description of one operating point rather than of the circuit.

**Finally, lumped elements assume the circuit is small compared with a wavelength.** At
455 kHz a wavelength is 660 m and a circuit board is a point. At 4.55 GHz a wavelength
is 66 mm, the wires between the components are a significant fraction of one, and the
resonance you get is not the resonance you designed — it is the resonance of the coil,
the capacitor and the loop of wire holding them together.
''',
                },
                {
                    "title": "Q: how sharp, how wide, and the voltage that comes from nowhere",
                    "minutes": 15,
                    "body": r'''
The previous reading found where a series loop resonates and showed that the resistance
does not appear in the answer. This one is about what the resistance *does* decide,
which turns out to be everything else: how narrow the resonance is, how much of the
neighbouring spectrum gets through with it, how long it rings, and how much voltage
appears across two components that no source in the circuit ever produced.

All of that is one dimensionless number.

## Two definitions of Q, and why they agree

The first definition is a ratio of energies, and it is the one that generalises to
tuning forks, quartz crystals and church bells:

$$Q = 2\pi \times \frac{\text{energy stored in the resonator}}
{\text{energy lost per cycle}}$$

Work that out for a series loop driven at resonance, carrying a current of amplitude
$I_p$. The stored energy is constant: at the instant the current peaks it is all in the
inductor, $\tfrac12 L I_p^2$; a quarter cycle later the current is zero and the same
energy sits in the capacitor as $\tfrac12 C V_{C,p}^2$. The energy lost is the resistor's
average power times the period.

```
stored              W    = (1/2) L I_p^2
lost per cycle      W_d  = (I_p^2 R/2) * T = I_p^2 R/(2 f_0)

Q = 2*pi * W/W_d
  = 2*pi * (1/2) L I_p^2 * 2 f_0/(I_p^2 R)
  = 2*pi f_0 L/R
  = w_0 L/R
```

The amplitude cancels, which it must — $Q$ is a property of the circuit, not of how hard
it is being driven. And what is left is the second definition, the practical one: **the
reactance at resonance divided by the resistance it works against**. A loop with 316 Ω
of reactance and 10 Ω of loss has a $Q$ of 31.6, and it takes 31.6 cycles for the stored
energy to fall by a factor of $e^{2\pi}$.

## Three ways to write the same thing

$$Q = \frac{\omega_0 L}{R} = \frac{1}{\omega_0 C R} = \frac{1}{R}\sqrt{\frac{L}{C}}$$

The first two are equal because $\omega_0 L = 1/(\omega_0 C)$ — that is what resonance
*means*. The third comes from substituting $\omega_0 = 1/\sqrt{LC}$, and it is the most
useful of the three because it contains no frequency at all:

```
R = 10 ohm, L = 10 mH, C = 100 nF

Q = w_0 L/R      = 31623 * 0.010/10          = 31.62
Q = 1/(w_0 C R)  = 1/(31623 * 1e-7 * 10)     = 31.62
Q = (1/R)sqrt(L/C) = (1/10) * sqrt(1e5)      = 31.62
```

The quantity $\sqrt{L/C}$ has units of ohms and turns up constantly; it is the
**characteristic impedance** of the resonator, the value both reactances take at
resonance. Here it is 316.2 Ω. So $Q$ is simply that impedance divided by the loop
resistance, and everything about designing a resonator is choosing those two numbers:
$LC$ puts the resonance somewhere, $\sqrt{L/C}$ against $R$ decides how sharp it is.

## Worked: the half-power points, exactly

The band-pass output — taken across the resistor — is at half power where its magnitude
falls to $1/\sqrt2$ of the peak. Since $H = R/(R + jX)$, that happens where the
reactance's magnitude equals the resistance:

```
half power where       |X| = R,    i.e.   wL - 1/(wC) = +/- R

multiply by w/L:       w^2 -/+ (R/L) w - 1/(LC) = 0

positive roots:        w = -/+ R/(2L) + sqrt( (R/2L)^2 + 1/(LC) )
```

The square root is the same in both, so the two roots differ by exactly $R/L$. No
approximation was made and no assumption about $Q$ was needed:

$$\text{BW} = \frac{R}{L}\ \text{rad/s} = \frac{R}{2\pi L}\ \text{Hz}
= \frac{\omega_0}{Q} = \frac{f_0}{Q}$$

Numbers, for the same circuit:

```
BW  = R/(2*pi*L) = 10/0.0628319              = 159.15 Hz
    = f_0/Q      = 5032.9/31.623             = 159.15 Hz

and the two edges, exactly:
R/(2L)                                       = 500 rad/s
sqrt(500^2 + 1e9)                            = 31626.729 rad/s
w_1 = 31626.729 - 500 = 31126.729  ->  f_1   = 4953.973 Hz
w_2 = 31626.729 + 500 = 32126.729  ->  f_2   = 5113.128 Hz

f_2 - f_1                                    = 159.155 Hz
sqrt(f_1 * f_2)                              = 5032.92 Hz
(f_1 + f_2)/2                                = 5033.55 Hz
```

Read the last two lines carefully, because they are the part that is usually stated
wrongly. The resonant frequency is the **geometric** mean of the half-power
frequencies, not the arithmetic mean. The arithmetic mean of the two edges is
$f_0\sqrt{1 + 1/(4Q^2)}$, always a little above $f_0$: at a $Q$ of 31.6 that is 0.0125%,
or 0.63 Hz, and nobody would ever notice; at a $Q$ of 4 it is 0.78%; at a $Q$ of 2 it is
3.1% and plainly visible on a sweep. The band is symmetric on a logarithmic frequency
axis, which is the axis a Bode plot uses and the axis frequency ratios actually live on.

The form $\text{BW} = R/(2\pi L)$ is worth keeping separately, because the capacitance
has vanished from it. To narrow a filter without moving it, lower $R$ or raise $L$; then
choose $C$ to put $f_0$ back where it was. The bandwidth and the centre frequency are
adjustable independently, which is not obvious from $f_0/Q$.

## ζ and Q are one quantity seen twice

$$\zeta = \frac{1}{2Q} = \frac{R}{2}\sqrt{\frac{C}{L}}$$

Multiply the expressions for $\zeta$ and $Q$ together and everything cancels but the
$\tfrac12$, which is the whole content of the identity. So the $\zeta = 0.05$ that made
the Bode sandbox peak sharply is a $Q$ of 10; $\zeta = 1$, critical damping, is a $Q$ of
0.5; and $\zeta = 0.707$ — the flattest response with no peak — is a $Q$ of $1/\sqrt2$.
Control engineering counts damping, calls small numbers dangerous and designs for
$\zeta \approx 0.7$. Radio counts quality, calls large numbers desirable and pays money
for $Q = 200$. It is the same circuit; only the goal differs.

## Worked: a voltage no source in the circuit produces

At resonance the loop is purely resistive, so $I = V_s/R$, and each reactance then has
$I$ times its own $X_0 = \sqrt{L/C}$ across it:

$$|V_L| = |V_C| = \frac{V_s}{R}\sqrt{\frac{L}{C}} = Q\,V_s$$

```
L = 1.0 mH, C = 100 nF, R = 2.5 ohm, drive 1.00 V rms

f_0 = 1/(2*pi*sqrt(1e-3 * 1e-7)) = 1/(2*pi*1e-5)   = 15915 Hz
X_0 = sqrt(L/C) = sqrt(1e4)                        = 100.0 ohm
Q   = X_0/R = 100/2.5                              = 40.0
I   = 1.00/2.5                                     = 400 mA
V_L = V_C = 0.400 * 100                            = 40.0 V
```

Forty volts across the capacitor from a one-volt source, with nothing in the circuit
capable of gain. Drive the same loop from 10 V and the capacitor sees 400 V. This is
simultaneously the reason resonance is useful — it is free voltage step-up, and it is
how a crystal radio drives a high-impedance earpiece from microwatts — and the reason
resonant circuits destroy components rated comfortably above the supply. A capacitor
chosen for a 12 V rail because 12 V was the largest number on the schematic is not a
sensible choice in a loop with a $Q$ of 40.

The energy view says the same thing without any arithmetic: the source pushes a small
amount of energy in on every cycle and the two stores keep almost all of it, so the
amount circulating builds up until what leaks out through $R$ each cycle equals what
comes in. High $Q$ means low leakage, which means a large circulating amplitude. There
is no free energy anywhere; there is a slow accumulation, and it takes roughly $Q$
cycles to reach the steady state — 40 cycles here, or about 2.5 ms.

## The resistance you did not draw

Now the practical problem, which is the difference between a resonator on paper and one
on a bench. Coils are made of wire, and wire has resistance. Manufacturers quote a coil
by its own $Q$ at a stated frequency, which is exactly a statement about that
resistance.

```
a 1.0 mH coil specified Q = 60 at 15.9 kHz carries
r     = w_0 L/60 = 100/60                          = 1.667 ohm

put it in the loop above:
R_tot = 2.5 + 1.667                                = 4.167 ohm
Q     = 100/4.167                                  = 24.0     (designed: 40)
V_C   = 1.00 * 24.0                                = 24.0 V   (expected: 40 V)
BW    = f_0/Q = 15915/24.0                         = 663 Hz   (expected: 398 Hz)
```

Nothing was miscalculated and nothing failed. A resistance that was never drawn was in
the loop all along, and because at resonance the resistance is the *only* thing left, a
resistance you forgot is not a small correction — it is a direct multiplier on every
number that matters. The upper bound is worth stating plainly: **the loop's $Q$ can
never exceed the $Q$ of its worst component.** Wiring a coil of $Q = 60$ into a circuit
and hoping for 200 is not optimism, it is arithmetic that does not work.

## Where the peak actually is

One more piece of small print, because it is the sort of thing that looks like an error
when a simulator disagrees with you by 6%. The band-pass output across the resistor
peaks exactly at $f_0$. The *capacitor's* voltage does not.

```
|V_C/V_s| peaks at   w = w_0 sqrt(1 - 1/(2Q^2))
peak value           = Q/sqrt(1 - 1/(4Q^2))

Q = 40:   peak at 0.99984 w_0,  value 40.003   (40.000 at w_0)
Q = 2:    peak at 0.93541 w_0,  value  2.066   ( 2.000 at w_0)
```

At a $Q$ of 40 the discrepancy is one part in six thousand and can be ignored for ever.
At a $Q$ of 2 the true peak sits 6.5% below $f_0$ and is 3.3% higher than $Q$. And below
$Q = 1/\sqrt2 = 0.707$ — that is $\zeta > 0.707$ — the square root turns negative and
there is no peak at all: the response falls monotonically from DC and the circuit has
stopped being a resonator in any useful sense. Every "at resonance the capacitor sees
$Q$ times the source" statement in this module is therefore a high-$Q$ statement,
excellent above about 10 and worth checking below about 3.

## Worked: how much Q does a job actually need

Selectivity is where $Q$ gets specified rather than merely measured. The band-pass
magnitude, with $u = f/f_0$, is

$$|H| = \frac{1}{\sqrt{1 + Q^2\left(u - \dfrac{1}{u}\right)^2}}$$

Suppose a receiver tuned to 1.000 MHz has to suppress an interferer at 1.020 MHz — 2%
away — by at least 20 dB.

```
u = 1.02:   u - 1/u = 1.02 - 0.98039           = 0.03961

20 dB down means |H| = 0.1:
  1 + Q^2 * 0.03961^2 = 100
  Q^2 = 99/0.0015689                           = 63100
  Q                                            = 251
```

A $Q$ of 251 is at the edge of what an LC circuit does — it needs a good coil, no
loading and a trimmer — and this is why a broadcast receiver does not select stations
with a single tuned circuit. It is also why quartz crystals, whose $Q$ runs into the
tens of thousands, exist as components at all. Turning "reject the adjacent channel"
into a number is the useful move here; the number then tells you honestly whether the
technology you had in mind can do it.

## The mistake, and why it is tempting

The mistake is $\text{BW} = f_0 \times Q$.

It is tempting because $Q$ is called quality, more quality sounds like more of
everything, and because both formulas are "the two numbers combined" with only the
operation to choose. The defence takes two seconds: at any $Q$ above 1, multiplying
gives a bandwidth *wider than the centre frequency itself*, which would mean a filter
that passes DC and everything up to twice its own resonance. For the worked circuit it
claims 159 kHz of bandwidth around a 5 kHz resonance. Anything of that shape should be
rejected before the pen leaves the paper.

The second mistake is quieter and survives longer: assuming the −3 dB points sit at
$f_0 \pm \text{BW}/2$. They are $\text{BW}$ apart, exactly, and their *geometric* mean
is $f_0$. Their arithmetic mean sits slightly above $f_0$, at $f_0\sqrt{1 + 1/(4Q^2)}$ —
0.01% at $Q = 30$, 0.8% at $Q = 4$, 3% at $Q = 2$, and by then enough to make a low-$Q$
design miss its stopband on the low side while overshooting on the high side.

The third is using the resistor on the schematic as $R$. That is the previous section,
and it is the one that actually costs people working days.

## Where this stops holding

**A coil's resistance is not constant with frequency.** Skin effect confines current to
the surface of the wire and proximity effect crowds it further, so a coil's $r$ climbs
roughly as $\sqrt{f}$ over a wide range. $Q = \omega_0 L/r$ therefore does *not* rise
for ever with frequency: every coil has a frequency where its own $Q$ peaks and falls
away past it, and the datasheet curve is the only honest source for where that is.

**Loaded $Q$ is not unloaded $Q$.** Connect anything to the resonator — the next stage,
a detector, an oscilloscope probe — and its resistance joins the loop. The $Q$ you can
measure with nothing attached is an upper bound on the $Q$ you get in service, and in a
filter the loading is usually deliberate: you *choose* how heavily to load it in order
to buy the bandwidth you need.

**$\text{BW} = f_0/Q$ is a statement about the band-pass output.** The low-pass output
across the capacitor and the high-pass output across the inductor have the same poles
and the same $Q$, but their −3 dB frequencies are elsewhere entirely — for the low-pass
across the capacitor it sits at
$\omega_0\sqrt{1 - 2\zeta^2 + \sqrt{2 - 4\zeta^2 + 4\zeta^4}}$, which is $1.554\,\omega_0$
for a lightly damped loop and drops to exactly $\omega_0$ only at $\zeta = 1/\sqrt2$.
A high-$Q$ low-pass is −3 dB more than half an octave above its resonance, nowhere near
the narrow band the same circuit shows across the resistor. Quoting "the bandwidth" without saying
which output is being measured is how two people compute different correct answers to
the same question.

**High $Q$ means high sensitivity to tolerance.** A $Q$ of 100 buys a bandwidth of 1% of
$f_0$; a ±5% capacitor moves $f_0$ by ±2.5%, which is two and a half bandwidths. The
resonance can therefore land entirely outside its own passband, and no amount of care
with the algebra prevents it. Above a certain $Q$ a trimmer stops being a refinement and
becomes the only way the circuit works at all.

**And the whole treatment assumes linearity.** Everything here — superposition,
impedance, a transfer function that does not depend on amplitude — needs $L$ and $C$
constant. A saturating core or a biased class-2 ceramic makes $f_0$ a function of drive
level, and then the resonance is a different resonance at every amplitude.
''',
                },
            ],
            "tune": {
                "title": "A resonator that is sharp but not lethal",
                "minutes": 10,
                "brief": r"""
Three sliders, three numbers that depend on all of them. $L$ and $C$ between them set
where the resonance sits; $R$ sets how sharp it is; and the peak gain — the factor by
which the voltage across the reactances exceeds the source — follows from the sharpness
whether you wanted it to or not.

The brief is a real one. The resonance has to land on a 1 kHz signal, and it has to be
selective enough to reject anything a few percent away, which means a high $Q$. But
the capacitor in the box is rated at thirty times the drive voltage, so $Q$ cannot run
away either. There is a window; find it.
""",
                "prompt": "Resonate within 5% of 1 kHz, with a Q of at least 20 but a peak no higher than 30.",
                "note": "ζ and Q are the same fact: ζ = 1/(2Q), so 'Q of at least 20' is 'ζ of at most 0.025'.",
                "model": "rlc",
                "initial": {"r": 100, "l": 100, "c": 2.5},
                "constraints": [
                    {"k": "fn", "label": "resonance between 950 Hz and 1.05 kHz", "min": 950.0, "max": 1050.0},
                    {"k": "zeta", "label": "\u03b6 \u2264 0.025, which is a Q of 20 or better", "max": 0.025},
                    {"k": "peak", "label": "peak gain \u2264 30, or the capacitor does not survive", "max": 30.0},
                ],
            },
            "quiz": {
                "title": "Sharpness, and what it costs",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A 10 mH inductor and a 100 nF capacitor are in series. At what frequency do their reactances cancel?",
                        "opts": ["5.03 kHz", "1.59 kHz", "31.6 kHz", "503 Hz"],
                        "a": 0,
                        "why": r'''
$f_0 = 1/(2\pi\sqrt{LC})$, and $LC = 10^{-2} \times 10^{-7} = 10^{-9}$, whose square
root is $3.16\times10^{-5}$. So $f_0 = 1/(2\pi \times 3.16\times10^{-5}) = 5033$ Hz.
The figure 31.6 kHz is $\omega_0 = 1/\sqrt{LC}$ left in radians per second and never
converted — the same missing $2\pi$ that turns up in every corner frequency in this
course.
''',
                    },
                    {
                        "q": "At the resonance of a series RLC circuit, what is the impedance?",
                        "opts": [
                            "At a maximum, equal to $\\omega_0 L$",
                            "At a minimum, equal to $R$",
                            "Exactly zero",
                            "Purely reactive",
                        ],
                        "a": 1,
                        "why": r'''
Exactly $R$, and that is the smallest it gets at any frequency. The inductive and
capacitive reactances are equal and opposite, so they vanish from the sum and leave
the resistance alone — which is why the current peaks there. It is not zero: with no
resistance at all the current would be unbounded, and every real circuit has some.
The maximum-impedance answer describes the *parallel* arrangement, which is the next
module and is the mirror image of this one in almost every respect.
''',
                    },
                    {
                        "q": "A series RLC has R = 10 Ω, L = 10 mH and C = 100 nF. What is its Q?",
                        "opts": ["3.16", "31.6", "316", "0.0316"],
                        "a": 1,
                        "why": r'''
$Q = \dfrac{1}{R}\sqrt{\dfrac{L}{C}} = \dfrac{1}{10}\sqrt{\dfrac{10^{-2}}{10^{-7}}}
= \dfrac{1}{10}\sqrt{10^5} = 31.6$. The same number comes out of $\omega_0 L/R$:
$31623 \times 0.01/10 = 31.6$. Note that $Q$ rises as $R$ falls — the resistance is the
only thing in the loop that loses energy, so less of it means the oscillation is
better sustained and the peak is sharper.
''',
                    },
                    {
                        "q": "That circuit is driven at its resonance by a 1 V RMS source. What voltage appears across the capacitor?",
                        "opts": ["1 V", "0.707 V", "31.6 V", "0 V"],
                        "a": 2,
                        "why": r'''
$Q$ times the source, so 31.6 V. At resonance the whole source appears across the
resistor, so the current is $1/R$; that current through the capacitor's reactance
$1/(\omega_0 C) = 316$ Ω gives 31.6 V. The inductor has the same 31.6 V across it,
pointing the other way, so the two cancel in Kirchhoff's loop and the source is none
the wiser. Nothing is amplifying: the two components are trading the same energy back
and forth, and the source only replaces what the resistor turns into heat.
''',
                    },
                    {
                        "q": "A band-pass has $f_0 = 5$ kHz and $Q = 31.6$. What is its −3 dB bandwidth?",
                        "opts": ["158 Hz", "1.58 kHz", "5 kHz", "31.6 Hz"],
                        "a": 0,
                        "why": r'''
$\text{BW} = f_0/Q = 5000/31.6 = 158$ Hz — that is what a high $Q$ buys you, a window
about 3% wide centred on the resonance. Multiplying instead of dividing gives 158 kHz,
which would be wider than the resonant frequency itself and should be rejected on
sight. The same bandwidth can be read straight off the components as $R/(2\pi L)$,
with no need to work out $Q$ at all.
''',
                    },
                    {
                        "q": "Damping ζ and quality factor Q describe the same property. How are they related?",
                        "opts": ["$\\zeta = 2Q$", "$\\zeta = 1/(2Q)$", "$\\zeta = Q$", "$\\zeta = Q/2$"],
                        "a": 1,
                        "why": r'''
$\zeta = 1/(2Q)$. For a series RLC, $\zeta = \frac{R}{2}\sqrt{C/L}$ and
$Q = \frac{1}{R}\sqrt{L/C}$, and multiplying those two gives exactly $\frac{1}{2}$.
So $\zeta = 0.5$ is $Q = 1$, and the critically damped $\zeta = 1$ is $Q = 0.5$.
Control engineering counts damping and calls small numbers dangerous; radio counts
quality and calls large numbers desirable. Same circuit, opposite priorities.
''',
                    },
                ],
            },
            "blanks": {
                "title": "One loop, in eight lines",
                "minutes": 9,
                "lang": "text",
                "caption": "Everything this module does to a series R-L-C loop, on one page.",
                "brief": r'''
A series resonator is one circuit with a small number of facts attached to it, and the
facts are all consequences of a single line — the impedance with both reactances
collected under one $j$. Fill that line in first and the rest follow.

Three of the blanks are places where a sign, a direction or a which-way-up is the whole
answer, and they are the three that get written backwards.
''',
                "listing": r'''
    series R-L-C, one loop, driven at angular frequency w

        X_L = w L        X_C = 1/(w C)        w_0 = 1/sqrt(LC)


    total impedance         Z    = R + j( ___ )

    resonance is where      ___                    ->   w_0 = 1/sqrt(LC)

    impedance at w_0        |Z|  = ___

    output across R         a ___ filter

    quality factor          Q    = w_0 L/R = (1/R) sqrt( ___ )

    -3 dB bandwidth         BW   = ___                  (in hertz)

    across C at w_0         V_C  = ___
''',
                "blanks": [
                    {
                        "prompt": "The two reactances, collected into one bracket",
                        "hole": "net reactance",
                        "opts": ["$X_L + X_C$", "$X_L - X_C$", "$X_L X_C$", "$X_C - X_L$"],
                        "a": 1,
                        "why": r'''
$Z_L = j\omega L$ and $Z_C = \dfrac{1}{j\omega C} = -\dfrac{j}{\omega C}$. Series
impedances add, so the two go in with the signs they have: $+jX_L$ and $-jX_C$, which
under one $j$ is $X_L - X_C$. Adding the magnitudes is the single commonest way to get
resonance wrong, and it is tempting precisely because "impedances in series add" is
correct — the addition is of complex numbers, and it comes out as a subtraction of the
magnitudes. The order matters too: writing $X_C - X_L$ flips the sign of the reactance,
which reverses the phase everywhere and turns a lagging circuit into a leading one.
''',
                    },
                    {
                        "prompt": "The condition that defines resonance",
                        "hole": "resonance condition",
                        "opts": ["$X_L = R$", "$X_L = X_C$", "$X_L + X_C = R$", "$X_C = R$"],
                        "a": 1,
                        "why": r'''
The bracket vanishes when the two reactances are equal, and because they enter with
opposite signs, equal means cancelled. $\omega L = 1/(\omega C)$ rearranges to
$\omega^2 = 1/(LC)$. Note what is *not* in the condition: the resistance. $R$ has no
say in where the resonance is, only in how sharp it is. Setting a reactance equal to
$R$ is the definition of a *corner* frequency in a first-order filter, which is a
different circuit answering a different question.
''',
                    },
                    {
                        "prompt": "The magnitude of the impedance at resonance",
                        "hole": "|Z| at w_0",
                        "opts": ["$0$", "$R$", "$\\sqrt{R^2 + X_L^2}$", "unbounded"],
                        "a": 1,
                        "why": r'''
$|Z| = \sqrt{R^2 + X^2}$ and $X = 0$ there, so $|Z| = R$ — the smallest it takes at any
frequency, which is why the current peaks. It is not zero: a real loop always contains
the resistance of the wire, the coil and the source, and if it genuinely were zero the
current would be unbounded. Nor is it unbounded — that is the *parallel* arrangement,
which is the mirror image of this one and the next module's subject.
''',
                    },
                    {
                        "prompt": "What the output across the resistor does",
                        "hole": "filter type",
                        "opts": ["low-pass", "high-pass", "band-pass", "band-stop"],
                        "a": 2,
                        "why": r'''
$H = R/(R + jX)$, which is 1 exactly at $f_0$ and falls on both sides as $|X|$ grows —
the capacitor blocks below, the inductor blocks above. A band-pass with unity gain at
the centre. Move the probe and the same loop gives you the other answers: across the
capacitor it is a second-order low-pass, across the inductor a second-order high-pass.
The poles belong to the loop, so all three share $f_0$ and $Q$; only the numerator
changes.
''',
                    },
                    {
                        "prompt": "What is under the square root in $Q$",
                        "hole": "L over C",
                        "opts": ["$C/L$", "$LC$", "$L/C$", "$1/(LC)$"],
                        "a": 2,
                        "why": r'''
Substitute $\omega_0 = 1/\sqrt{LC}$ into $Q = \omega_0 L/R$ and the $L$ over
$\sqrt{LC}$ simplifies to $\sqrt{L/C}$. That quantity is in ohms — it is the value both
reactances take at resonance, the resonator's characteristic impedance — so $Q$ is a
ratio of two resistances and comes out dimensionless, which is the check that catches
the upside-down version. $\sqrt{C/L}$ is in siemens and turns up in the damping,
$\zeta = \frac{R}{2}\sqrt{C/L}$, where it belongs the other way up because $\zeta$ and
$Q$ are reciprocal.
''',
                    },
                    {
                        "prompt": "The −3 dB bandwidth of the band-pass, in hertz",
                        "hole": "bandwidth",
                        "opts": ["$f_0 Q$", "$Q/f_0$", "$f_0/Q$", "$2\\pi f_0/Q$"],
                        "a": 2,
                        "why": r'''
$\text{BW} = f_0/Q$, equivalently $R/(2\pi L)$ straight from the components. Multiplying
instead of dividing is the mistake, and it fails a size check instantly: at any $Q$
above 1 it claims a bandwidth wider than the resonant frequency itself, which would be a
filter passing everything from DC to twice its own centre. $Q/f_0$ is in seconds and is
not a bandwidth at all, and the version with the $2\pi$ is the bandwidth in radians per
second wearing a hertz label.
''',
                    },
                    {
                        "prompt": "The voltage across the capacitor at resonance",
                        "hole": "V_C at w_0",
                        "opts": ["$V_s/Q$", "$V_s$", "$Q\\,V_s$", "$Q^2 V_s$"],
                        "a": 2,
                        "why": r'''
At resonance the loop is purely resistive, so $I = V_s/R$, and that current through the
capacitor's reactance $\sqrt{L/C}$ gives $V_s\sqrt{L/C}/R = Q V_s$. The inductor has the
same magnitude across it, pointing the other way, so the two cancel round the loop and
the source only ever sees the $V_s$ across the resistor. Nothing is amplifying — the two
stores are trading one packet of energy and the source replaces only what the resistor
turns into heat — but the voltage is entirely real, and a $Q$ of 40 puts 400 V on a
capacitor fed from 10 V.
''',
                    },
                ],
            },
            "numeric": [
                {
                    "title": "Where the two reactances cross",
                    "minutes": 5,
                    "brief": r'''
The first rung, and deliberately mechanical: two values off the drawing, one rule, one
answer.

The resistor is drawn and labelled, and it is not needed. That is the point of starting
here — the resonance is set by the two energy stores alone, and a formula that reached
for $R$ would be the wrong formula.
''',
                    "prompt": "At what frequency does this loop resonate?",
                    "note": "Give the answer in hertz, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "l1", "kind": "L", "x": 6, "y": 3, "rot": 0, "value": 0.033},
                            {"id": "c1", "kind": "C", "x": 9, "y": 3, "rot": 0, "value": 6.8e-8},
                            {"id": "out", "kind": "OUT", "x": 12, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 12, "y": 4, "rot": 1, "value": 47},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [8, 3]},
                            {"a": [10, 3], "b": [12, 3]},
                            {"a": [12, 5], "b": [12, 7]},
                            {"a": [12, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V RMS, frequency swept"},
                        {"label": "Inductor (in series)", "value": "33 mH"},
                        {"label": "Capacitor (in series)", "value": "68 nF"},
                        {"label": "Resistor (to ground)", "value": "47 Ω"},
                    ],
                    "aside": "Convert both components to base units before doing anything else. "
                             "33 mH is 0.033 H and 68 nF is 6.8e-8 F, and the product of those two "
                             "is a number near 1e-9 — if the square root you take is not of order "
                             "1e-5, a prefix has been dropped.",
                    "answer": 3360.0,
                    "tol": 3.0,
                    "unit": "Hz",
                    # Measured rather than restated: the check bisects the drawn circuit for the
                    # frequency where the band-pass output is exactly in phase with the source,
                    # which is what resonance means, so both component values have to come off the
                    # schematic and any edit to either moves the expected answer.
                    "check": r'''
c.assert(c.count('L') === 1 && c.count('C') === 1, "one inductor and one capacitor in the loop");
var lo = 1, hi = 1e7;
for (var i = 0; i < 200; i++) {
  var mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > 0) lo = mid; else hi = mid;
}
return Math.sqrt(lo * hi);
''',
                    "hint": r"$f_0 = 1/(2\pi\sqrt{LC})$. Work out $LC$ first, then its square root, then multiply by $2\pi$, and take the reciprocal last — doing the reciprocal early is where the brackets go wrong.",
                    "wrong": r"21 110 is $\omega_0 = 1/\sqrt{LC}$ left in radians per second, the "
                             r"missing $2\pi$ that turns up in every frequency in this course. "
                             r"70.9 MHz is $1/(2\pi LC)$ with the square root forgotten, and a "
                             r"megahertz answer from a 33 mH coil should be rejected on sight. "
                             r"0.1062 Hz converts the inductor to henries but leaves the capacitor "
                             r"in nanofarads. 226.7 Hz is $R/(2\pi L)$, which is a real property of "
                             r"this circuit — its bandwidth — but not the frequency it is centred "
                             r"on, and the giveaway is that it used the resistor.",
                    "why": r'''
```
LC        = 0.033 * 6.8e-8                 = 2.244e-9
sqrt(LC)                                   = 4.73709e-5
2*pi*sqrt(LC)                              = 2.97637e-4
f_0       = 1/2.97637e-4                   = 3359.8 Hz
```

That is the whole calculation, and the reason it does not mention the 47 Ω is worth a
moment. Resonance is the frequency where the inductor's demand and the capacitor's
demand are equal and opposite:

```
w L = 1/(w C)   ->   w^2 = 1/(LC)   ->   w_0 = 1/sqrt(LC)
```

Nothing in that argument refers to the rest of the loop. The resistor decides how sharp
the resonance is and how much current flows there, but not where it is.

For the record, here is what the resistor *does* set, since the drawing gives you the
numbers anyway:

```
w_0       = 1/4.73709e-5                   = 21110 rad/s
X_0       = w_0 L = 21110*0.033            = 696.6 ohm
   (also  sqrt(L/C) = sqrt(0.033/6.8e-8) = sqrt(485294) = 696.6)
Q         = X_0/R = 696.6/47               = 14.82
BW        = f_0/Q = 3359.8/14.82           = 226.7 Hz
   (also  R/(2*pi*L) = 47/0.207345         = 226.7 Hz)
```

So this loop passes a band about 227 Hz wide centred on 3.36 kHz, and at the centre the
696 Ω of inductive reactance and the 696 Ω of capacitive reactance are both present and
both invisible to the source.
''',
                },
                {
                    "title": "The impedance that is only a resistor",
                    "minutes": 7,
                    "brief": r'''
Second rung. The source is set exactly to the resonant frequency, so the two reactances
have cancelled and the loop is purely resistive. That is not a simplification you are
being offered; it is the definition of the frequency you have been put at.

The one decision to make is which resistance. There are two resistors in this drawing
and one of them is not a design choice — it is the resistance of the wire the coil is
wound from, which the manufacturer supplies whether you wanted it or not.
''',
                    "prompt": "What RMS current flows in the loop with the source at the resonant frequency?",
                    "note": "Give the answer in milliamps, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "l1", "kind": "L", "x": 6, "y": 3, "rot": 0, "value": 0.015},
                            {"id": "rw", "kind": "R", "x": 9, "y": 3, "rot": 0, "value": 12},
                            {"id": "c1", "kind": "C", "x": 12, "y": 3, "rot": 0, "value": 4.7e-8},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 3, "rot": 0, "value": 0},
                            {"id": "rl", "kind": "R", "x": 15, "y": 4, "rot": 1, "value": 68},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [8, 3]},
                            {"a": [10, 3], "b": [11, 3]},
                            {"a": [13, 3], "b": [15, 3]},
                            {"a": [15, 5], "b": [15, 7]},
                            {"a": [15, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "6.00 V RMS, at the resonant frequency"},
                        {"label": "Inductor", "value": "15 mH"},
                        {"label": "The coil's winding resistance", "value": "12 Ω, in series with it"},
                        {"label": "Capacitor", "value": "47 nF"},
                        {"label": "Load resistor (to ground)", "value": "68 Ω"},
                    ],
                    "aside": "The resonant frequency itself is not needed for this answer, which is "
                             "worth noticing rather than being annoyed by: at resonance the current "
                             "is $V_s/R$ whatever $f_0$ happens to be, because the reactances have "
                             "removed themselves from the sum. Work $f_0$ out anyway as a check on "
                             "the rest of the drawing.",
                    "answer": 75.0,
                    "tol": 0.2,
                    "unit": "mA",
                    # Solved rather than restated: the check bisects for the resonance of the drawn
                    # circuit, reads the voltage across the resistor the probe sits on, and divides
                    # by the value of that resistor as the netlist reports it.
                    "check": r'''
c.assert(c.count('R') === 2 && c.count('L') === 1 && c.count('C') === 1,
         "two resistances, one coil, one capacitor");
var lo = 1, hi = 1e7;
for (var i = 0; i < 200; i++) {
  var mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > 0) lo = mid; else hi = mid;
}
var f0 = Math.sqrt(lo * hi), out = c.outNode();
var probed = c.net.parts.filter(function (p) {
  return p.kind === 'R' && ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
});
c.assert(probed.length === 1, "one resistor between the probe and ground");
return 1000 * c.gain(f0) / probed[0].value;
''',
                    "hint": r"At $f_0$ the bracket in $Z = R + j(\omega L - 1/(\omega C))$ is zero, so $|Z|$ is just the resistance — and the loop's resistance is everything the current has to pass through on its way round, not only the resistor labelled as the load.",
                    "wrong": r"88.2 mA is $6.00/68$, the coil's 12 Ω left out; it is the answer you "
                             r"get by reading the schematic as though the winding resistance were "
                             r"decoration. 500 mA is $6.00/12$, the two resistors swapped. 10.52 mA "
                             r"divides by $\sqrt{80^2 + 564.9^2}$, keeping the reactance in the sum "
                             r"instead of cancelling it — that is the current at some frequency, but "
                             r"not at this one. 0.0750 is the right answer left in amps.",
                    "why": r'''
At resonance the inductor's reactance and the capacitor's reactance are equal and
opposite, so they leave the sum entirely and the loop is a plain resistance. That
resistance is everything in series round the loop:

```
R_tot = 12 + 68                            = 80 ohm
I     = 6.00/80                            = 75.0 mA
```

Everything else in the drawing is a check rather than a step, and it is worth doing
because it shows what the two "cancelled" components are actually up to:

```
sqrt(LC)  = sqrt(0.015 * 4.7e-8) = sqrt(7.05e-10)  = 2.65518e-5
f_0       = 1/(2*pi*2.65518e-5)                    = 5994 Hz
X_0       = sqrt(L/C) = sqrt(0.015/4.7e-8)         = 564.9 ohm
Q         = X_0/R_tot = 564.9/80                   = 7.06

across the 68 ohm   = 0.0750 * 68                  = 5.10 V
across the 12 ohm   = 0.0750 * 12                  = 0.90 V
across the coil     = 0.0750 * 564.9               = 42.4 V
across the capacitor                               = 42.4 V
```

The two resistive drops add to 6.00 V, which is Kirchhoff's voltage law and a free check
on the arithmetic. The two reactive drops are each seven times the source and they add
to nothing, because they are antiphase — that is the same cancellation that let you
divide by 80 in the first place, seen from the other end.

The trap this rung exists for is the 12 Ω. Away from resonance it is negligible: at
1 kHz the loop's impedance is over three kilohms and twelve ohms is a rounding error. At
resonance it is 15% of everything that is left, and it takes 15% off the current, the
$Q$ and the voltage across both stores. **A resistance that can be ignored everywhere
else cannot be ignored at resonance, because at resonance the resistance is all there
is.** That is the single most useful sentence in this module.
''',
                },
                {
                    "title": "What the capacitor actually sees",
                    "minutes": 9,
                    "brief": r'''
Third rung, and the first one where the answer is bigger than the source.

Three steps: find the resonance, find the reactance there, and find the current. Keep
every intermediate value — the last two multiply, and there is a second route to the
same answer that makes a good check.

Before working it out, guess the order of magnitude. Then compare.
''',
                    "prompt": "With the source at the circuit's resonant frequency, what RMS voltage appears across the capacitor?",
                    "note": "Give the answer in volts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 3},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 8.2},
                            {"id": "l1", "kind": "L", "x": 9, "y": 3, "rot": 0, "value": 0.022},
                            {"id": "out", "kind": "OUT", "x": 12, "y": 3, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 12, "y": 4, "rot": 1, "value": 3.3e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [8, 3]},
                            {"a": [10, 3], "b": [12, 3]},
                            {"a": [12, 5], "b": [12, 7]},
                            {"a": [12, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "3.00 V RMS, at the resonant frequency"},
                        {"label": "Resistor (in series)", "value": "8.2 Ω — the whole loop's loss"},
                        {"label": "Inductor (in series)", "value": "22 mH"},
                        {"label": "Capacitor (to ground)", "value": "33 nF"},
                    ],
                    "aside": "The probe sits between the inductor and the capacitor, so it reads the "
                             "capacitor's voltage with respect to ground. The inductor has the same "
                             "magnitude across it and the opposite sign, and the two together "
                             "contribute nothing to the loop — which is why the current can be "
                             "worked out from the resistor alone.",
                    "answer": 298.7,
                    "tol": 0.8,
                    "unit": "V",
                    # Solved rather than restated: the check finds resonance as the frequency where
                    # the capacitor voltage lags the source by exactly a quarter cycle -- which is
                    # what a purely resistive loop current does to it -- and reads the magnitude
                    # there off the solved circuit.
                    "check": r'''
c.assert(c.count('R') === 1 && c.count('L') === 1 && c.count('C') === 1, "one of each");
var lo = 1, hi = 1e7;
for (var i = 0; i < 200; i++) {
  var mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > -90) lo = mid; else hi = mid;
}
return c.gain(Math.sqrt(lo * hi));
''',
                    "hint": r"$f_0 = 1/(2\pi\sqrt{LC})$, then $X_C = 1/(\omega_0 C)$ — which is also $\sqrt{L/C}$, and that form skips the frequency entirely. The current at resonance is $V_s/R$, and $V_C$ is that current times $X_C$.",
                    "wrong": r"3.000 V is the answer for the output taken across the *resistor*, "
                             r"where the gain really is 1 at resonance; across a reactance it is not. "
                             r"47.54 V uses $Q = f_0 L/R$ with the frequency in hertz where "
                             r"$\omega_0 L/R$ wanted radians per second — the missing $2\pi$ again, "
                             r"and it is out by exactly that factor. 0.03013 V divides by $Q$ "
                             r"instead of multiplying. 211.2 V is the right answer converted from "
                             r"RMS to peak in the wrong direction, or the right answer with a stray "
                             r"$\sqrt{2}$ in it.",
                    "why": r'''
```
sqrt(LC)  = sqrt(0.022 * 3.3e-8) = sqrt(7.26e-10)  = 2.69444e-5
w_0       = 1/2.69444e-5                           = 37113 rad/s
f_0       = 37113/6.28319                          = 5906.8 Hz

X_0       = w_0 L = 37113 * 0.022                  = 816.5 ohm
   (also  sqrt(L/C) = sqrt(0.022/3.3e-8) = sqrt(666667) = 816.5)

I         = V_s/R = 3.00/8.2                       = 365.85 mA
V_C       = I * X_0 = 0.36585 * 816.5              = 298.7 V
```

The second route, which is worth doing because it uses none of the same intermediate
numbers except $X_0$:

```
Q         = X_0/R = 816.5/8.2                      = 99.57
V_C       = Q * V_s = 99.57 * 3.00                 = 298.7 V
```

**Three volts in, very nearly three hundred volts across a capacitor.** Nothing in this
circuit has gain. The source pushes 366 mA round a loop whose only obstacle is 8.2 Ω,
and that current through 816 Ω of capacitive reactance is 299 V — while the inductor,
carrying the same current through the same 816 Ω, has 299 V across it the other way up.
The two cancel in Kirchhoff's loop and the source sees only the 3.00 V across the
resistor. Sum the phasors and it balances exactly; sum the magnitudes and you get 601 V
out of a 3 V source, which is the reason phasors are not optional.

Two practical consequences.

**The capacitor has to survive it.** 299 V RMS is 423 V peak. A part rated at 50 V —
entirely sensible-looking on a schematic whose only source says 3 V — fails here, and
it fails as soon as the circuit is tuned rather than at switch-on, which makes it look
like a mystery instead of an oversight.

**And a $Q$ of 100 is a claim about the loop, not about the drawing.** 8.2 Ω is stated
here to be the whole loop's loss. In a real build the coil alone would have to be better
than that: a 22 mH inductor at 5.9 kHz with $Q_{coil} = 100$ has
$816.5/100 = 8.2$ Ω of winding resistance all by itself, so the external resistor would
have to be zero and everything else perfect. Ask for $Q = 100$ from a wound coil and you
are asking for a good one.
''',
                },
                {
                    "title": "Every resistance in the loop counts",
                    "minutes": 11,
                    "brief": r'''
Fourth rung. A real measurement, with a real source and a real coil.

The source is not ideal: 50 Ω of output resistance, which is what a signal generator
has. The coil is not ideal: 6.8 Ω of winding. And the resonator is feeding a 100 Ω load
rather than an open circuit. All three of those are in the same loop, and the question
is how wide the resulting band-pass is.

Work out the resonance first — it is not the answer, but it is half of one route to it,
and it tells you at a glance whether anything else has gone wrong.
''',
                    "prompt": "What is the −3 dB bandwidth of this band-pass?",
                    "note": "Give the answer in hertz, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "rs", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 50},
                            {"id": "l1", "kind": "L", "x": 9, "y": 3, "rot": 0, "value": 0.0047},
                            {"id": "rw", "kind": "R", "x": 12, "y": 3, "rot": 0, "value": 6.8},
                            {"id": "c1", "kind": "C", "x": 15, "y": 4, "rot": 1, "value": 1e-8},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 5, "rot": 0, "value": 0},
                            {"id": "rl", "kind": "R", "x": 15, "y": 6, "rot": 1, "value": 100},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [8, 3]},
                            {"a": [10, 3], "b": [11, 3]},
                            {"a": [13, 3], "b": [15, 3]},
                            {"a": [15, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V RMS behind 50 Ω of output resistance"},
                        {"label": "Inductor", "value": "4.7 mH"},
                        {"label": "The coil's winding resistance", "value": "6.8 Ω, in series with it"},
                        {"label": "Capacitor", "value": "10 nF"},
                        {"label": "Load (across which the output is taken)", "value": "100 Ω to ground"},
                    ],
                    "aside": "Bandwidth is $f_0/Q$, and it is also $R/(2\\pi L)$ with no capacitance "
                             "in it at all. The second form is quicker here and is the one that makes "
                             "the trap visible: there is only one $R$ in it, and it is the whole "
                             "loop's, because in a series loop the current meets every resistance in "
                             "turn.",
                    "answer": 5310.0,
                    "tol": 8.0,
                    "unit": "Hz",
                    # Measured, not restated: the check finds resonance from the phase, then bisects
                    # the swept response on each side for the points 3 dB below the peak and returns
                    # the gap. Nothing in it names a component value.
                    "check": r'''
c.assert(c.count('R') === 3 && c.count('L') === 1 && c.count('C') === 1,
         "three resistances in one loop with a coil and a capacitor");
var lo = 1, hi = 1e8;
for (var i = 0; i < 200; i++) {
  var m = Math.sqrt(lo * hi);
  if (c.phase(m) > 0) lo = m; else hi = m;
}
var f0 = Math.sqrt(lo * hi), target = c.gain(f0) / Math.SQRT2;
function edge(inside, outside) {
  for (var i = 0; i < 200; i++) {
    var m = Math.sqrt(inside * outside);
    if (c.gain(m) > target) inside = m; else outside = m;
  }
  return Math.sqrt(inside * outside);
}
return edge(f0, f0 * 1000) - edge(f0, f0 / 1000);
''',
                    "hint": r"Add every resistance the loop current passes through, then $\text{BW} = R_{tot}/(2\pi L)$. If you would rather go the long way, $f_0 = 1/(2\pi\sqrt{LC})$ and $Q = \sqrt{L/C}/R_{tot}$ give the same number as $f_0/Q$.",
                    "wrong": r"3386 Hz uses the 100 Ω load alone, which is the resistance the probe "
                             r"is across rather than the resistance the current goes through. "
                             r"5079 Hz keeps the source resistance but drops the coil's 6.8 Ω. "
                             r"230.3 Hz uses the winding resistance alone. 101.5 kHz is $f_0 Q$ "
                             r"instead of $f_0/Q$ — wider than the resonant frequency itself, which "
                             r"is impossible for any $Q$ above 1 and should be caught without "
                             r"checking the algebra.",
                    "why": r'''
Every one of the three resistances is in series with the loop current, so they add:

```
R_tot = 50 + 6.8 + 100                            = 156.8 ohm
BW    = R_tot/(2*pi*L) = 156.8/(2*pi*0.0047)
      = 156.8/0.0295310                           = 5310 Hz
```

The long way round, as a check:

```
sqrt(LC)  = sqrt(0.0047 * 1e-8) = sqrt(4.7e-11)   = 6.85565e-6
f_0       = 1/(2*pi*6.85565e-6)                   = 23215 Hz
X_0       = sqrt(L/C) = sqrt(470000)              = 685.6 ohm
Q         = X_0/R_tot = 685.6/156.8               = 4.372
f_0/Q     = 23215/4.372                           = 5310 Hz
```

A $Q$ of 4.4, from a circuit whose designer, counting only the 100 Ω load, would have
expected $685.6/100 = 6.9$ and a bandwidth of 3386 Hz. More than a third of the loop's
loss is in parts nobody chose.

Two things this circuit shows that a tidier one hides.

**The gain at the centre is not 1.** The probe is across the 100 Ω, and at resonance the
loop is a 156.8 Ω divider, so the peak is $100/156.8 = 0.638$, or −3.9 dB. The band-pass
across "the resistor" has unity gain only when the resistor *is* the whole loop
resistance. Here the −3 dB points are measured 3 dB below 0.638, not below 1.

**At this $Q$ the band is visibly lopsided in hertz.** The exact half-power frequencies
come from $\omega = \pm R/(2L) + \sqrt{(R/2L)^2 + 1/(LC)}$:

```
R/(2L)                                            = 16681 rad/s
sqrt(16681^2 + 1/(LC)) = sqrt(2.7825e8 + 2.12766e10)
                                                  = 146816 rad/s
w_1 = 146816 - 16681 = 130135   ->   f_1          = 20711.6 Hz
w_2 = 146816 + 16681 = 163497   ->   f_2          = 26021.3 Hz

f_2 - f_1                                         = 5309.7 Hz
sqrt(f_1 * f_2)                                   = 23215 Hz
(f_1 + f_2)/2                                     = 23366 Hz
```

$f_0$ is the **geometric** mean of the two edges, 2504 Hz above the lower one and
2806 Hz below the upper one. The arithmetic midpoint sits 151 Hz high. At a $Q$ of 30
that gap is a fraction of a hertz and nobody would ever notice; at 4.4 it is real, and
placing the edges at $f_0 \pm \text{BW}/2$ would put both of them in the wrong place.
The two edges are exactly $\text{BW}$ apart either way — that part is not an
approximation.
''',
                },
                {
                    "title": "A resonance used to reject",
                    "minutes": 13,
                    "brief": r'''
The last rung, and the topology is new. The inductor and the capacitor are still in
series with each other, but the pair is now a branch to ground hanging off a divider
rather than the path the output current takes.

Think about what that does before computing anything. At the frequency where the branch
resonates, its impedance collapses to the coil's few ohms and it shorts the output to
ground; far away in either direction it is a large reactance and the output is nearly
the whole source. This is a **trap**, or a notch — a resonance used to remove one
frequency rather than to select it.

The question is not at the notch. It is a little to one side of it, where you have to
carry the reactance and the resistance together.
''',
                    "prompt": "What RMS voltage does a meter on the probe read with the source at 4.50 kHz?",
                    "note": "Give the answer in millivolts, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 1000},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "l1", "kind": "L", "x": 9, "y": 4, "rot": 1, "value": 0.1},
                            {"id": "rw", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 15},
                            {"id": "c1", "kind": "C", "x": 9, "y": 8, "rot": 1, "value": 1e-8},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 9]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 9], "b": [3, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V RMS at 4.50 kHz"},
                        {"label": "Series resistor", "value": "1.00 kΩ"},
                        {"label": "Trap: inductor", "value": "100 mH"},
                        {"label": "Trap: the coil's winding resistance", "value": "15 Ω"},
                        {"label": "Trap: capacitor", "value": "10 nF"},
                    ],
                    "aside": "The branch is a single impedance $Z_b = r + j(\\omega L - 1/(\\omega C))$, "
                             "and once you have it the circuit is the divider from the first week of "
                             "EE101 with complex numbers in it: $V_{out} = V_s\\,|Z_b|/|R_1 + Z_b|$. "
                             "Add the real parts to the real parts and leave the imaginary part "
                             "alone; the magnitude comes at the very end, once per bracket.",
                    "answer": 573.0,
                    "tol": 1.5,
                    "unit": "mV",
                    # Solved rather than restated: the solver builds the branch impedance from the
                    # drawn L, C and winding resistance and divides it against the drawn series
                    # resistor. The only constant here is the 4.50 kHz, which is the question.
                    "check": r'''
c.assert(c.count('R') === 2 && c.count('L') === 1 && c.count('C') === 1,
         "a series resistor, and a coil with its resistance and a capacitor in the branch");
return 1000 * c.gain(4500);
''',
                    "hint": r"Find the branch's reactance at 4.50 kHz — $\omega L$ minus $1/(\omega C)$, and it comes out negative because 4.50 kHz is below the trap's resonance. Then $|Z_b| = \sqrt{r^2 + X^2}$, and $|Z_{tot}| = \sqrt{(R_1 + r)^2 + X^2}$. Divide.",
                    "wrong": r"14.78 mV is the output *at* the trap frequency, where the reactance "
                             r"really has vanished — the right answer to a question about 5.03 kHz "
                             r"rather than 4.50 kHz. 415.0 mV divides by $R_1 + |Z_b|$, adding a "
                             r"resistance to an impedance magnitude arithmetically when only the "
                             r"real parts may be added that way. 1000 mV treats the branch as an "
                             r"open circuit, "
                             r"which is what it is at DC but not at 4.5 kHz. 0.5730 is the right "
                             r"answer left in volts.",
                    "why": r'''
Where the trap sits, first, because everything else is read relative to it:

```
sqrt(LC)  = sqrt(0.1 * 1e-8) = sqrt(1e-9)          = 3.16228e-5
f_trap    = 1/(2*pi*3.16228e-5)                    = 5032.9 Hz
```

So 4.50 kHz is below it, and below resonance a series L-C branch is net capacitive:

```
w         = 2*pi*4500                              = 28274 rad/s
X_L       = 28274 * 0.1                            = 2827.4 ohm
X_C       = 1/(28274 * 1e-8)                       = 3536.8 ohm
X         = X_L - X_C                              = -709.3 ohm
```

Now the branch as one impedance, and the divider:

```
Z_b       = 15 - j709.3
|Z_b|     = sqrt(15^2 + 709.3^2) = sqrt(503393)    = 709.50 ohm

Z_tot     = 1000 + 15 - j709.3 = 1015 - j709.3
|Z_tot|   = sqrt(1015^2 + 709.3^2) = sqrt(1533393) = 1238.3 ohm

|V_out|   = 1.00 * 709.50/1238.30                  = 0.5730 V
                                                   = 573.0 mV
```

Notice how little the 15 Ω changed: $\sqrt{15^2 + 709.3^2}$ is 709.50 against a bare
709.34. Off resonance the winding resistance is a rounding error, exactly as it was in
the second rung of this ladder. Its moment comes at the notch itself:

```
at 5032.9 Hz:  X = 0, so Z_b is 15 ohm and nothing else
|V_out| = 1.00 * 15/(1000 + 15)                    = 14.78 mV
                                                   = -36.6 dB
```

**The depth of the notch is set entirely by the coil's resistance.** A perfect coil
would short the output to ground completely; a lossy one leaves $r/(R_1 + r)$ behind.
That is the practical reason traps are built with the best inductor available, and the
reason a notch measured 20 dB shallower than designed is a coil problem rather than a
tuning problem.

Its width, on the other hand, is set by $R_1$. The output is 3 dB below its
far-from-notch value where the branch's reactance magnitude equals the series resistor:

```
wL - 1/(wC) = -1000  ->  f = 4299.7 Hz
wL - 1/(wC) = +1000  ->  f = 5891.2 Hz
width                                              = 1591.5 Hz
   (also  R_1/(2*pi*L) = 1000/0.628319 = 1591.5 Hz)
```

which is the same $R/(2\pi L)$ that gave the bandwidth of a series band-pass, with $R_1$
playing the part the loop resistance played there. 4.50 kHz is 533 Hz below the notch,
comfortably inside that 1592 Hz window, which is why the reading came out at 573 mV
rather than near a volt — and having that number in mind before doing the arithmetic is
what turns a wrong answer into an obviously wrong answer.
''',
                },
            ],
            "derive": {
                "title": "From two reactances to a bandwidth",
                "minutes": 13,
                "vars": ["R", "L", "C", "omega", "omega_0", "Q", "j"],
                "brief": r'''
A resistor, an inductor and a capacitor in one loop, driven at angular frequency
$\omega$. Four steps take that to a resonant frequency, a quality factor and a
bandwidth.

As before, $j$ is the square root of $-1$ and stays a symbol throughout.
''',
                "steps": [
                    {
                        "prompt": "Write the total impedance of the loop, with both reactances collected into a single bracket multiplied by $j$.",
                        "answer": "R + j\\left(\\omega L - \\frac{1}{\\omega C}\\right)",
                        "hint": "Series impedances add. The inductor contributes $j\\omega L$ and the capacitor $1/(j\\omega C)$, which is $-j/(\\omega C)$.",
                        "deconstruct": [
                            "$Z = R + j\\omega L + \\dfrac{1}{j\\omega C}$.",
                            "Multiplying the last term above and below by $j$ turns it into $-\\dfrac{j}{\\omega C}$.",
                            "Now both reactances carry a $j$ and can be gathered into one bracket.",
                        ],
                    },
                    {
                        "prompt": "At resonance the bracket vanishes. Solve $\\omega L = 1/(\\omega C)$ for the resonant $\\omega_0$.",
                        "answer": "\\frac{1}{\\sqrt{LC}}",
                        "placeholder": "\\sqrt{\\ldots}",
                        "hint": "Multiply both sides by $\\omega$ and divide by $L$; you are left with $\\omega^2 = 1/(LC)$.",
                        "deconstruct": [
                            "$\\omega L = 1/(\\omega C)$ becomes $\\omega^2 L C = 1$.",
                            "So $\\omega^2 = 1/(LC)$, and the positive root is the answer.",
                        ],
                    },
                    {
                        "prompt": "The quality factor is the reactance at resonance divided by the resistance, $Q = \\omega_0 L / R$. Substitute $\\omega_0$ and write $Q$ in terms of $R$, $L$ and $C$ only.",
                        "answer": "\\frac{1}{R}\\sqrt{\\frac{L}{C}}",
                        "hint": "$\\dfrac{L}{\\sqrt{LC}}$ simplifies — divide top and bottom by $\\sqrt{L}$.",
                        "deconstruct": [
                            "$Q = \\dfrac{L}{R\\sqrt{LC}}$.",
                            "$\\dfrac{L}{\\sqrt{LC}} = \\sqrt{\\dfrac{L^2}{LC}} = \\sqrt{\\dfrac{L}{C}}$.",
                        ],
                    },
                    {
                        "prompt": "The output across the resistor is at half power where the bracket's magnitude equals $R$, and the two frequencies that satisfy that are $R/L$ apart in radians per second. Write that bandwidth in terms of $\\omega_0$ and $Q$.",
                        "answer": "\\frac{\\omega_0}{Q}",
                        "hint": "You have $Q = \\omega_0 L/R$. Rearrange it for $R/L$.",
                        "deconstruct": [
                            "$Q = \\omega_0 L / R$ rearranges to $R/L = \\omega_0/Q$.",
                            "And $R/L$ was the bandwidth, so the bandwidth is $\\omega_0/Q$.",
                        ],
                    },
                ],
                "closing": r'''
$\text{BW} = \omega_0/Q$, and dividing both sides by $2\pi$ says the same thing in
hertz: $f_0/Q$. Notice what did *not* appear anywhere — the source. The resonant
frequency, the quality factor and the bandwidth are properties of the three components
alone, which is why a resonator can be specified and built before anyone decides what
will drive it.

One consequence worth keeping: $\text{BW} = R/(2\pi L)$ contains no capacitance at all.
To make a filter narrower at a fixed frequency you lower $R$ or raise $L$, and then
$C$ follows to put the resonance back where it was.
''',
            },
            "lab": {
                "title": "Measuring Q instead of computing it",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
$Q$ has two definitions that have to agree: one from the components, one from the
shape of the measured response. Write both and check them against each other.

`f0_hz(l, c)` returns $f_0 = 1/(2\pi\sqrt{LC})$ in hertz.

`q_factor(r, l, c)` returns $Q = \frac{1}{R}\sqrt{L/C}$.

`response(f, r, l, c)` returns the complex $V_{out}/V_{in}$ of the series loop with the
output taken across the resistor:

```text
H = r / (r + 1j * (2*pi*f*l - 1/(2*pi*f*c)))
```

`bandwidth_hz(r, l, c)` returns the −3 dB bandwidth **measured from that response**,
not from a formula. The magnitude is 1 at $f_0$ and falls monotonically on each side,
so bisect for the frequency where it crosses $1/\sqrt{2}$ below $f_0$, bisect again for
the one above, and return the difference. Bisecting in the logarithm of the frequency
converges in far fewer steps than bisecting in the frequency itself; a hundred
iterations is more than enough either way.

If the two definitions of $Q$ do not agree to six figures, one of them is wrong.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def f0_hz(l, c):
    """The resonant frequency of an L-C pair, in hertz."""
    # TODO
    return 0.0


def q_factor(r, l, c):
    """Q from the components."""
    # TODO
    return 0.0


def response(f, r, l, c):
    """Complex Vout/Vin of the series loop, output across the resistor."""
    # TODO
    return 0j


def bandwidth_hz(r, l, c):
    """The -3 dB bandwidth, found by bisecting the measured response on each side."""
    # TODO: locate the 1/sqrt(2) crossing below f0 and above f0, subtract.
    return 0.0


if __name__ == "__main__":
    R, L, C = 10.0, 1e-2, 1e-7
    f0 = f0_hz(L, C)
    print("f0:", round(f0, 3), "Hz")
    print("Q from components:", round(q_factor(R, L, C), 6))
    print("gain at f0:", round(abs(response(f0, R, L, C)), 9))
    bw = bandwidth_hz(R, L, C)
    print("measured bandwidth:", round(bw, 6), "Hz")
    print("Q from the measurement:", round(f0 / bw, 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def f0_hz(l, c):
    """The resonant frequency of an L-C pair, in hertz."""
    return 1.0 / (2.0 * np.pi * np.sqrt(float(l) * float(c)))


def q_factor(r, l, c):
    """Q from the components."""
    return np.sqrt(float(l) / float(c)) / float(r)


def response(f, r, l, c):
    """Complex Vout/Vin of the series loop, output across the resistor."""
    w = 2.0 * np.pi * f
    return r / (r + 1j * (w * l - 1.0 / (w * c)))


def _cross(r, l, c, lo, hi):
    """Bisect in log frequency for the point where |H| falls to 1/sqrt(2)."""
    target = 1.0 / np.sqrt(2.0)
    for _ in range(100):
        mid = np.sqrt(lo * hi)
        if abs(response(mid, r, l, c)) > target:
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


def bandwidth_hz(r, l, c):
    """The -3 dB bandwidth, found by bisecting the measured response on each side."""
    f0 = f0_hz(l, c)
    below = _cross(r, l, c, f0 / 1000.0, f0)
    above = _cross(r, l, c, f0 * 1000.0, f0)
    return above - below


if __name__ == "__main__":
    R, L, C = 10.0, 1e-2, 1e-7
    f0 = f0_hz(L, C)
    print("f0:", round(f0, 3), "Hz")
    print("Q from components:", round(q_factor(R, L, C), 6))
    print("gain at f0:", round(abs(response(f0, R, L, C)), 9))
    bw = bandwidth_hz(R, L, C)
    print("measured bandwidth:", round(bw, 6), "Hz")
    print("Q from the measurement:", round(f0 / bw, 6))
'''}],
                "hints": [
                    "`np.sqrt(l * c)` sits inside the $2\\pi$, not outside it: $f_0 = 1/(2\\pi\\sqrt{LC})$, so a misplaced bracket costs a factor of $\\sqrt{LC}$ squared.",
                    "In `response`, the imaginary part is the *difference* of the two reactances. If the magnitude never reaches 1 anywhere, they are being added instead of subtracted.",
                    "One bisection routine serves both sides if you pass it the two ends the right way round: the end nearest $f_0$ is the one where the response is still above the target.",
                ],
                "tests": [
                    {"name": "the resonant frequency of 10 mH and 100 nF", "code": r'''
_f = f0_hz(1e-2, 1e-7)
assert abs(_f - 5032.921210448704) < 1e-6, \
    f"1/(2*pi*sqrt(1e-9)) is 5032.921 Hz; got {_f} (31623 would mean the answer is still in rad/s)"
'''},
                    {"name": "Q from the components", "code": r'''
_q = q_factor(10.0, 1e-2, 1e-7)
assert abs(_q - 31.622776601683793) < 1e-9, f"(1/10)*sqrt(1e-2/1e-7) is 31.6228; got {_q}"
_q2 = q_factor(20.0, 1e-2, 1e-7)
assert _q2 < _q, "more resistance means a lower Q — the resistor is the only thing losing energy"
'''},
                    {"name": "the band-pass has unity gain exactly at resonance", "code": r'''
import numpy as np
_f = f0_hz(1e-2, 1e-7)
_h = response(_f, 10.0, 1e-2, 1e-7)
assert abs(abs(_h) - 1.0) < 1e-9, \
    f"at resonance the reactances cancel and the resistor sees the whole source; got {abs(_h)}"
assert abs(np.angle(_h)) < 1e-9, f"and there is no phase shift there either; got {np.angle(_h)}"
assert abs(response(_f / 100.0, 10.0, 1e-2, 1e-7)) < 0.01, "far below resonance the capacitor blocks"
assert abs(response(_f * 100.0, 10.0, 1e-2, 1e-7)) < 0.01, "far above it the inductor does"
'''},
                    {"name": "the measured bandwidth agrees with f0 over Q", "code": r'''
_f = f0_hz(1e-2, 1e-7)
_bw = bandwidth_hz(10.0, 1e-2, 1e-7)
_want = _f / q_factor(10.0, 1e-2, 1e-7)
assert abs(_bw - _want) / _want < 1e-6, \
    f"the measured bandwidth is {_bw:.6f} Hz and f0/Q is {_want:.6f} Hz — these are the same quantity"
assert abs(_bw - 159.15494309189535) < 1e-3, \
    f"R/(2*pi*L) = 10/(2*pi*0.01) = 159.155 Hz, got {_bw}"
'''},
                    {"name": "and again for a much blunter circuit", "code": r'''
_bw = bandwidth_hz(100.0, 1e-2, 1e-7)
assert abs(_bw - 1591.5494309189535) / 1591.5494309189535 < 1e-5, \
    f"ten times the resistance is ten times the bandwidth: 1591.55 Hz expected, got {_bw}"
_f = f0_hz(1e-2, 1e-7)
assert abs(_bw - _f / q_factor(100.0, 1e-2, 1e-7)) / _bw < 1e-6, \
    "the two definitions of Q must agree at low Q as well as at high Q"
'''},
                ],
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "The parallel tank and the notch",
            "summary": "The same two components wired the other way round do the opposite thing: instead of a short at one frequency, an open circuit.",
            "concepts": [
                "An inductor and a capacitor **in parallel** resonate at the same $f_0 = 1/(2\\pi\\sqrt{LC})$, but there they present a very *large* impedance — infinite if the components were lossless. The two branch currents are equal and opposite, so they cancel at the terminals and circulate inside the loop instead. That circulating current is why it is called a **tank**.",
                "Fed from a source resistance $R$, a tank has $Q = R\\sqrt{C/L} = \\dfrac{R}{\\omega_0 L}$ — the reciprocal of the series expression. In a series resonator less resistance is sharper; in a parallel one, more resistance is sharper. Both statements say the same thing: sharpness improves as the loss falls.",
                "Away from resonance a tank looks like whichever branch conducts more easily: capacitive above $f_0$, inductive below. Only at $f_0$ do the two susceptances cancel exactly.",
                "The mirror arrangement is a series $L$–$C$ branch used as a shunt. At $f_0$ it is nearly a short circuit to ground, so a divider built with it in the lower leg loses its output entirely at that one frequency: a **notch**, or band-stop. Everywhere else the branch is high impedance and the signal passes.",
                "How deep a real notch goes is decided by loss, chiefly the inductor's winding resistance, which stops the branch ever being a perfect short. The depth is the notch's loaded $Q$ divided by the coil's own $Q$, so a notch that is both deep *and* narrow needs component $Q$s in the hundreds; the resonant frequency, by contrast, depends only on $L$ and $C$ and not on any resistance in the circuit.",
                "There are four ways to wire two components and only two behaviours. A series $L$\u2013$C$ is a short at $f_0$, so it notches when used as a shunt to ground and passes a band when used in the signal path; a parallel tank is an open at $f_0$, so it does the opposite of each. A tank sitting **in** the signal path is called a **trap**, and it is a notch.",
                "A tank fed from a resistance $R$ has $\\text{BW} = 1/(2\\pi R C)$ in hertz \u2014 no inductance in it \u2014 exactly mirroring the series resonator's $R/(2\\pi L)$, which has no capacitance in it. A smaller $R$ sharpens a series resonance and blunts a parallel one; the fixed point is that less **loss** is always sharper, and which resistor counts as loss depends on whether it sits inside the resonant loop or across it.",
            ],
            "read": [
                {
                    "title": "Two currents that cancel",
                    "minutes": 14,
                    "body": r'''
## Two components, one pair of terminals

An inductor and a capacitor connected across the same two nodes is not a circuit that
looks like it is hiding anything. There is no third component, no loop to go round, no
divider to divide. Yet this arrangement is what sits inside every radio front end, every
oscillator, and the output of every switching converter, and the reason is one sentence
that sounds impossible the first time you read it: at one frequency the current flowing
in at the terminals is zero while the current going round inside the pair is large.

Start from what the two branches have in common. They are in parallel, which means they
share a voltage — that is the definition, not a consequence — so impose

$$v(t) = V_p \sin \omega t$$

on both and ask each component separately what current it takes. There is no need for
phasors yet; the two defining relations are enough.

A capacitor's current is set by how fast its voltage is changing:

$$i_C = C\frac{dv}{dt} = \omega C V_p \cos \omega t$$

An inductor is the other way round. Voltage does not set its current, it *changes* its
current, so the current is the running total of the voltage applied so far:

$$i_L = \frac{1}{L}\int v\,dt = -\frac{V_p}{\omega L}\cos \omega t$$

Both currents come out as cosines when the applied voltage is a sine, which is the 90°
shift you already know about. What matters here is that they come out as cosines of
*opposite sign*. At the instant the voltage is rising fastest through zero, the capacitor
is taking its largest positive current, because that is when its voltage is changing
fastest. The inductor at that same instant is at its most negative current, because it has
just spent an entire negative half-cycle being pushed backwards and has not yet been
pushed forwards again.

Add them, because that is what the terminals see:

$$i(t) = i_C + i_L = V_p\left(\omega C - \frac{1}{\omega L}\right)\cos \omega t$$

## The frequency where the bracket empties

Nothing in that line is an approximation, and nothing in it assumed a small signal or a
particular size of component. The terminal current is a cosine of amplitude
$V_p\,(\omega C - 1/(\omega L))$, and there is one frequency at which the bracket is exactly
zero:

$$\omega C = \frac{1}{\omega L} \quad\Rightarrow\quad \omega^2 = \frac{1}{LC}
\quad\Rightarrow\quad \omega_0 = \frac{1}{\sqrt{LC}}, \qquad
f_0 = \frac{1}{2\pi\sqrt{LC}}$$

That is the same expression, character for character, as the series resonance of the
previous module — and the behaviour it produces is the opposite one. In series the two
reactances cancelled in a sum of *voltages*, and the loop's impedance collapsed to $R$.
Here they cancel in a sum of *currents*, and the pair's impedance does not collapse, it
runs away. Zero current for a non-zero applied voltage is infinite impedance.

Said in admittance, which is the variable that suits a node the way impedance suits a
loop:

$$Y = j\omega C + \frac{1}{j\omega L} = j\left(\omega C - \frac{1}{\omega L}\right)$$

The capacitor contributes a positive susceptance, the inductor a negative one, and at
$\omega_0$ they annihilate. $Y = 0$ means $Z = 1/Y$ is unbounded. The pair is called a
**tank**, and at $f_0$ it is, to the rest of the circuit, a break in the wire.

## Where the current actually went

The bracket being zero says the *sum* is zero. It says nothing whatever about the two
terms, and the two terms are not small. At $\omega_0$,

$$\omega_0 C = \frac{C}{\sqrt{LC}} = \sqrt{\frac{C}{L}}, \qquad
\frac{1}{\omega_0 L} = \frac{\sqrt{LC}}{L} = \sqrt{\frac{C}{L}}$$

so both branches carry the same amplitude, $V_p\sqrt{C/L}$. It is worth naming the
reciprocal of that root, because it turns up in every formula from here on:

$$X_0 = \sqrt{\frac{L}{C}} = \omega_0 L = \frac{1}{\omega_0 C}$$

$X_0$ is the reactance of *either* component at resonance — they are equal there, which is
what resonance means — and each branch carries $V_p/X_0$. The two are equal in size and
opposite in sign at every instant, so what leaves the capacitor arrives at the inductor
and never troubles the terminals at all. The current circulates. That is the image the
name is built on: a tank of water sloshing from one end to the other, with nothing spilling
out.

You can watch the energy do it. The capacitor holds $\tfrac12 C v^2$ and the inductor
holds $\tfrac12 L i_L^2$, and at resonance $i_L = -V_p\sqrt{C/L}\,\cos\omega_0 t$, so

$$W = \tfrac12 C V_p^2 \sin^2\omega_0 t + \tfrac12 L \frac{C V_p^2}{L}\cos^2\omega_0 t
= \tfrac12 C V_p^2 \left(\sin^2 + \cos^2\right) = \tfrac12 C V_p^2$$

The total stored energy is *constant*. It moves from the electric field of the capacitor
into the magnetic field of the inductor and back, twice per cycle, and at no point does the
total change. A source that supplies energy at a constant rate of zero is a source
supplying no current, which is the same fact arriving from the other direction.

## A tank with numbers in it

Take a coil and a capacitor from the top of the AM broadcast band: $L = 47\,\mu\text{H}$ and
$C = 220$ pF, fed from a 1 V source through a 10 kΩ resistor, with the probe on the tank.

```
LC        = 47e-6 * 220e-12                      = 1.0340e-14
sqrt(LC)                                         = 1.01686e-7
f_0       = 1/(2*pi*1.01686e-7)                  = 1.5652 MHz
X_0       = sqrt(L/C) = sqrt(47e-6 / 220e-12)
          = sqrt(213636)                         = 462.21 ohm
```

At 1.5652 MHz the tank is an open circuit, so no current flows in the 10 kΩ, so nothing is
dropped across it and the probe reads the full 1.000 V. Meanwhile each branch of the tank
is carrying

```
I_circ    = V/X_0 = 1.000/462.21                 = 2.1635 mA
```

2.16 mA going round and round, and zero coming out of the source. The stored energy is
$\tfrac12 C V_p^2$, which for 220 pF at a 1 V peak is 110 pJ, handed back and forth
3.1 million times a second.

Now the sharpness. Away from $f_0$ the tank has an admittance $B = \omega C - 1/(\omega L)$
and the circuit is a divider of $R$ against $1/(jB)$:

$$\left|\frac{V_{out}}{V_{in}}\right| = \left|\frac{1}{1 + jRB}\right|
= \frac{1}{\sqrt{1 + (RB)^2}}$$

which is 1 at $f_0$ and falls to $1/\sqrt2$ where $|RB| = 1$, that is where
$|B| = 1/R$. Solve $\omega C - 1/(\omega L) = \pm 1/R$ — multiply by $\omega$ and you have
two quadratics whose positive roots are the two half-power frequencies — and the two roots
differ by exactly $1/(RC)$ in radians per second, with no approximation and at any
sharpness. So

$$\text{BW} = \frac{1}{2\pi R C}, \qquad
Q = \frac{f_0}{\text{BW}} = 2\pi f_0 R C = \omega_0 R C = R\sqrt{\frac{C}{L}} = \frac{R}{X_0}$$

```
Q         = R/X_0 = 10000/462.21                 = 21.635
          = R*sqrt(C/L) = 1e4*sqrt(220e-12/47e-6)  (same number)
BW        = f_0/Q = 1.5652e6/21.635              = 72.34 kHz
          = 1/(2*pi*1e4*220e-12)                   (same number)
```

And to see it fall off, take the source down to 1.400 MHz, a tenth below the resonance:

```
w         = 2*pi*1.4e6                           = 8.79646e6 rad/s
w*C       = 8.79646e6 * 220e-12                  = 1.93522e-3 S
1/(w*L)   = 1/(8.79646e6 * 47e-6)                = 2.41877e-3 S
B         = 1.93522e-3 - 2.41877e-3              = -4.83547e-4 S
R*B       = 1e4 * -4.83547e-4                    = -4.8355
|H|       = 1/sqrt(1 + 4.8355^2)                 = 0.20252
V_out                                            = 203 mV
```

A negative $B$ means the inductive branch is winning, which it must below resonance: the
coil's susceptance $1/(\omega L)$ is large at low frequencies and the capacitor's
$\omega C$ is small. Above $f_0$ the sign flips and the tank looks capacitive. It is an
open circuit only in the narrow window around $f_0$, and that window is 72 kHz wide.

## The coil is not ideal, and it is the coil that spoils it

An infinite impedance is a statement about components that do not exist. A real inductor is
a length of wire, and wire has resistance; a 47 µH air-cored coil at 1.5 MHz might show
3 Ω. Put that in series with the inductance and the tank stops being infinite, because
the branch can no longer be a perfect negative of the other one.

The clean way to handle it is to ask what parallel resistor would waste energy at the same
rate as the series one, at this frequency. A branch of $r$ in series with reactance $X_0$
has admittance $1/(r + jX_0) = (r - jX_0)/(r^2 + X_0^2)$, whose real part is
$r/(r^2 + X_0^2)$; the parallel resistance with that conductance is

$$R_p = \frac{r^2 + X_0^2}{r} \approx \frac{X_0^2}{r} = Q_0^2\, r,
\qquad Q_0 \equiv \frac{X_0}{r}$$

$Q_0$ is the **component $Q$** — the coil's own quality, nothing to do with the circuit it
is put in. For our coil:

```
Q_0       = X_0/r = 462.21/3                     = 154.07
R_p       = (3^2 + 462.21^2)/3 = 213645/3        = 71215 ohm
```

So the tank is not an open circuit; it is a 71 kΩ resistor at resonance. Rerun the divider
with that in it:

```
peak      = R_p/(R + R_p) = 71215/81215          = 0.8769  ->  877 mV
R || R_p  = 1e4 * 71215/81215                    = 8768.7 ohm
Q_loaded  = (R || R_p)/X_0 = 8768.7/462.21       = 18.97
BW        = f_0/Q_loaded = 1.5652e6/18.97        = 82.50 kHz
```

Three numbers moved and all three moved the way loss always moves things: the peak fell
from 1.000 V to 877 mV, the $Q$ fell from 21.6 to 19.0, and the bandwidth grew from 72.3
kHz to 82.5 kHz. Loss makes a resonator blunter, never sharper. The circulating current
fell too, to $0.877/462.21 = 1.897$ mA, and the source now has to supply
$0.123/10000 = 12.3$ µA to keep it going — a current 154 times smaller than the one
circulating, which is $Q_0$ again and not a coincidence.

## The mistake

The formula that catches people is $Q = R\sqrt{C/L}$, because the series resonator of the
previous module had $Q = \frac{1}{R}\sqrt{L/C}$ and the two are exact reciprocals. Carry
the series habit across and you conclude that a smaller resistance makes a parallel tank
sharper, which is backwards, and the mistake is tempting because "less resistance, less
loss" is a reliable instinct everywhere else.

The instinct is fine; it is the geometry that changed. In a series resonator the resistance
is *in* the loop, so the current that resonates has to fight through it, and less of it
means less loss. In a parallel tank the resistance is *across* the loop, an escape route
for a current that would otherwise stay inside, and a larger resistance is a worse escape
route. Both cases obey the one definition that never changes:

$$Q = 2\pi \times \frac{\text{energy stored}}{\text{energy lost per cycle}}$$

Ask which way a given resistor drains the store, and the direction of the dependence comes
out on its own. It is worth doing that rather than memorising two formulae that differ by
being upside down, because at three in the morning the memorised pair is exactly what
inverts.

## Where this stops being true

**A coil resonates on its own.** Every winding has capacitance between its turns, and that
stray capacitance forms a tank with the inductance whether you wanted one or not. Above
its self-resonant frequency an inductor *is* a capacitor, and adding an external $C$ moves
nothing where you expect. Data sheets quote the self-resonant frequency; a design must sit
comfortably below it.

**With enough loss, even the frequency moves.** Everything above put the peak at
$\omega_0 = 1/\sqrt{LC}$. For a lossy coil in parallel with a capacitor, the frequency at
which the combination is purely resistive is

$$\omega_p = \sqrt{\frac{1}{LC} - \frac{r^2}{L^2}} = \omega_0\sqrt{1 - \frac{1}{Q_0^2}}$$

For $Q_0 = 154$ that is 0.99998 of $\omega_0$ — 33 Hz out of 1.5652 MHz, unmeasurable.
For $Q_0 = 3$, which is about all a small lossy ferrite-cored coil manages, it is 5.7% low, and for
$Q_0 = 2$ it is 13% low. The rule "resonance depends only on $L$ and $C$" is a
high-$Q$ rule, and it is safe precisely because anything worth calling a resonator has a
high $Q$.

**Whatever you connect next is part of the tank.** $Q$ was computed from the resistance
across the tank, and an oscilloscope probe is 1 MΩ in parallel with about 15 pF. The
megohm barely matters beside 71 kΩ; the 15 pF sits directly across a 220 pF capacitor and
moves $f_0$ down by 3%. Measuring a tank changes it, and the correction is arithmetic, not
apology: add the probe's capacitance to $C$ before comparing with the prediction.
''',
                },
                {
                    "title": "A short circuit that exists at one frequency",
                    "minutes": 15,
                    "body": r'''
## The other way to wire the same two parts

Take the inductor and the capacitor apart and reconnect them end to end instead of side by
side. Nothing about either component has changed. What has changed is which quantity they
are forced to share: in parallel they shared a voltage and their currents added, and in
series they share a *current* and their voltages add.

That single swap inverts everything. With the same current $i$ through both, the inductor
develops $j\omega L\, i$ and the capacitor develops $-j i/(\omega C)$, and the branch's
total impedance is

$$Z = j\omega L + \frac{1}{j\omega C} = j\left(\omega L - \frac{1}{\omega C}\right)$$

a purely imaginary number with one term growing with frequency and the other shrinking.
They are equal at

$$\omega_0 L = \frac{1}{\omega_0 C} \quad\Rightarrow\quad
\omega_0 = \frac{1}{\sqrt{LC}}, \qquad f_0 = \frac{1}{2\pi\sqrt{LC}}$$

which is the same frequency as before — of course it is, it is the same two components —
but now the two voltages cancel instead of the two currents, and instead of an infinite
impedance you get zero. The inductor's voltage and the capacitor's voltage are each
$X_0 = \sqrt{L/C}$ times the current, they are 180° apart, and they subtract to nothing.
The branch is a short circuit that exists at exactly one frequency, and is a very poor
conductor everywhere else.

## Hanging it off a divider

A short circuit on its own is not a filter. Make it one by putting the branch in the lower
leg of a divider: a resistor $R$ from the source down to the output node, and the series
$L$–$C$ from that node to ground. The transfer function is the divider you have written a
dozen times, with $Z$ in the bottom leg:

$$H(j\omega) = \frac{Z}{R + Z}
= \frac{jX}{R + jX}, \qquad X \equiv \omega L - \frac{1}{\omega C}$$

Read it at the three places worth reading it at. Far below $f_0$, the capacitor dominates
and $|X|$ is huge, so $H \to 1$ and the signal passes untouched. Far above, the inductor
dominates, $|X|$ is huge again, and $H \to 1$ once more. At $f_0$, $X = 0$ and so is the
output. Two flat passbands and a hole in the middle: a **notch**, or band-stop.

The hole is what makes it worth building. Almost every filter in this course has been a
statement about a whole half of the frequency axis — keep the low end, throw away the high
end. A notch is a statement about one frequency. When a measurement is being ruined by 50
Hz picked up from the mains, or a receiver is being blocked by a single strong transmitter
next door in the band, the useful signal is on both sides of the offender and a low-pass
would throw away half of what you came for.

## How wide the hole is

Take the ideal case first, $r = 0$, because it is exactly solvable and the answer is
prettier than the approximation usually quoted for it. From $H = jX/(R + jX)$,

$$|H|^2 = \frac{X^2}{R^2 + X^2}$$

The half-power points are where that equals $\tfrac12$, which needs $X^2 = R^2$, that is
$|X| = R$. Substituting $X = \omega L - 1/(\omega C)$ and multiplying through by $\omega$
turns each sign into a quadratic:

$$LC\,\omega^2 \mp RC\,\omega - 1 = 0 \quad\Rightarrow\quad
\omega = \frac{\pm RC + \sqrt{R^2C^2 + 4LC}}{2LC}$$

The positive root of each is one edge of the notch, and subtracting them the square roots
cancel and leave

$$\text{BW} = \omega_{hi} - \omega_{lo} = \frac{2RC}{2LC} = \frac{R}{L}
\,\text{rad/s} = \frac{R}{2\pi L}\,\text{Hz}$$

with no approximation and no assumption that the notch is narrow. Two more facts fall out
of the same pair of roots. Call the square root they share $S$ and multiply them: the
numerator is a difference of two squares, $S^2 - R^2C^2 = 4LC$, so the product is
$4LC/(4L^2C^2) = 1/(LC) = \omega_0^2$. The notch is therefore centred on $f_0$
*geometrically*, not arithmetically — it always looks symmetric on a logarithmic
frequency axis and never on a linear one. And dividing,

$$Q = \frac{\omega_0}{\text{BW}} = \frac{\omega_0 L}{R} = \frac{1}{R}\sqrt{\frac{L}{C}}$$

which is the *series* expression for $Q$, with $R$ being whatever resistance the resonant
branch has to push its current through. That is the reverse of the tank, where more
resistance meant a sharper peak, and both are the same statement about loss: the resonating
current here runs through $R$, so a smaller $R$ wastes less of it.

## A notch at 1 kHz, worked through

$R = 1.00$ kΩ on top, and a branch of $L = 100$ mH and $C = 253$ nF to ground. Real coils
have resistance, so give this one 15 Ω of winding resistance $r$, in series inside the
branch where it belongs.

```
LC        = 0.1 * 253e-9                        = 2.5300e-8
sqrt(LC)                                        = 1.59060e-4
f_0       = 1/(2*pi*1.59060e-4)                 = 1000.6 Hz
X_0       = sqrt(L/C) = sqrt(0.1/2.53e-7)
          = sqrt(395257)                        = 628.69 ohm
```

At $f_0$ the two reactances cancel and the branch is not zero ohms, it is $r$: 15 Ω. The
divider is then 15 Ω under 1000 Ω, so

```
depth     = r/(R + r) = 15/1015                 = 0.014778
in dB     = 20*log10(0.014778)                  = -36.61 dB
```

The width, from the formula above, and the two edges from the quadratics:

```
BW        = R/(2*pi*L) = 1000/0.62832           = 1591.5 Hz
f_lo                                            = 482.7 Hz
f_hi                                            = 2074.2 Hz
check     sqrt(482.7 * 2074.2)                  = 1000.6 Hz = f_0
Q         = f_0/BW = 1000.6/1591.5              = 0.629
```

A $Q$ below one is a legitimate answer and it says something true: with only 629 Ω of
reactance to work with and a whole kilohm of source resistance in the loop, this notch is
deep but very wide. A decade either side of it the signal is barely dented, but an octave
either side it is still down by a third:

```
at 500 Hz:  X = 314.16 - 1258.15               = -943.98 ohm
            |H| = sqrt(15^2 + 943.98^2)
                  / sqrt(1015^2 + 943.98^2)     = 0.681
at 2 kHz:   X = 1256.64 - 314.53                = 942.10 ohm
            |H|                                 = 0.680
at 100 Hz:  X = 62.83 - 6290.71                 = -6227.9 ohm
            |H|                                 = 0.987
```

The 15 Ω moves the −3 dB edges a little as well — the half-power condition with loss
present is $X^2 = (R+r)^2 - 2r^2$ rather than $X^2 = R^2$, which puts them at 478 Hz and
2093 Hz and widens the notch to 1615 Hz. A 1.5% correction from a resistance that changed
the depth by 36 dB is a fair summary of how the two properties divide the work: $r$ owns
the depth, $R$ and $L$ own the width.

## How deep, and what that costs

Depth is where a real notch disappoints people, so it is worth having the relation in a
form you can use before buying anything. The depth ratio is $r/(R+r) \approx r/R$. Write
each of those two resistances as a reactance over a $Q$ — the coil's own $Q_0$ for $r$,
the notch's loaded $Q$ for $R$:

$$r = \frac{X_0}{Q_0}, \qquad R = \frac{X_0}{Q}$$

and the $X_0$ cancels:

$$\text{depth} \approx \frac{Q}{Q_0}$$

The notch goes down by the ratio of the two qualities and by nothing else. Everything you
might want to adjust — the frequency, the inductance, the source resistance — has already
been absorbed into those two numbers.

Use it as a design tool. Suppose the requirement is a notch at 1.00 kHz, at least 30 dB
deep, no more than 200 Hz wide.

```
Q         = f_0/BW = 1000/200                   = 5.0
depth     = 10^(-30/20)                         = 0.031623
Q_0       = Q/depth = 5.0/0.031623              = 158.1
```

So before choosing a single component value you already know the answer turns on one
question: can you get a coil with a $Q$ of 160 at 1 kHz? That is a real specification and
not a comfortable one — it means a ferrite pot core or similar, not a moulded choke out of
a drawer. Only then pick the inductance, and the rest follows:

```
choose L                                        = 100 mH
X_0       = 2*pi*1000*0.1                       = 628.32 ohm
R         = X_0/Q = 628.32/5                    = 125.66 ohm
C         = 1/(w_0^2 L) = 1/(3.9478e7 * 0.1)    = 253.30 nF
r         = X_0/Q_0 = 628.32/158.1              = 3.974 ohm
depth     = 3.974/(125.66 + 3.974)              = 0.030653  ->  -30.27 dB
BW        = R/(2*pi*L) = 125.66/0.62832         = 200.0 Hz
```

Both targets met, with the depth 0.27 dB better than asked because the approximation
$r/(R+r)\approx r/R$ was slightly pessimistic. Notice that $L$ was genuinely free: taking
$L = 10$ mH instead would give $R = 12.57$ Ω, $C = 2.533$ µF and a coil resistance
requirement of 0.397 Ω, which is the same filter built out of components that are ten
times harder to realise. Deep narrow notches want large inductances, and that is why the
mains-frequency ones are usually built without an inductor at all.

## Four ways to wire two components

The tank and the notch are two of four arrangements, and the other two are worth having in
the same table because on a schematic they are one wire apart.

| $L$ and $C$ | in the signal path | as a shunt to ground |
|---|---|---|
| **in series** | short at $f_0$ — **band-pass** | short at $f_0$ — **notch** |
| **in parallel** | open at $f_0$ — **notch (a trap)** | open at $f_0$ — **band-pass** |

The entry nobody expects is the parallel pair sitting **in** the path: a *tank* placed in
series with the signal is a notch, because at $f_0$ it is a break in the wire and nothing
gets past. It is
called a **trap**, and it is how an antenna feed rejects a local transmitter. Take
$L = 10$ mH and $C = 100$ nF as the trap, feeding a 4.7 kΩ load from a 10 V source:

```
f_0       = 1/(2*pi*sqrt(0.01*1e-7))            = 5032.9 Hz
at 4 kHz: w = 2*pi*4000                         = 25133 rad/s
          B = w*C - 1/(w*L)
            = 2.51327e-3 - 3.97887e-3           = -1.46560e-3 S
          |Z_trap| = 1/|B|                      = 682.3 ohm (inductive)
          |Z_tot| = sqrt(4700^2 + 682.3^2)      = 4749.3 ohm
          V_out = 10 * 4700/4749.3              = 9.896 V
at f_0:   Z_trap -> infinity, V_out             -> 0
```

Every entry in the table is the same two components and the same $f_0$. What decides
whether you get a peak or a hole is not the components but the pair of questions: are they
sharing a current or a voltage, and are they in the path or across it.

## The mistake

The one that costs an afternoon is building the tank when you meant the branch. On a
schematic "an inductor and a capacitor between the output node and ground" describes both
arrangements, and the difference is whether the two parts sit one above the other or side
by side. Wire them side by side and at $f_0$ the output node is held up rather than pulled
down: instead of a notch you have built a band-pass with a peak precisely where you wanted
silence. It is tempting because both drawings have the same parts, the same values, the
same two nodes named, and because the resonant frequency you calculated is correct for
either one. The symptom is unmistakable once you know it — the response is *inverted*
about the frequency you were aiming at — and it is worth checking the drawing before
checking the arithmetic.

The second one is expecting the depth to follow from $L$ and $C$. It does not; $L$ and $C$
place the notch and nothing more. Depth is $Q/Q_0$, a statement about the components'
quality, and a notch that measures 20 dB when you wanted 40 is telling you about the coil
you bought, not about the frequency you chose.

## Where this stops being true

**The coil resonates with itself above the notch.** The stray capacitance across the
winding forms a tank with the inductance, so a real branch is a short at $f_0$ and then,
higher up, an *open* at the coil's own self-resonance. Above that the two capacitances
take over, the branch is a capacitor again, and its impedance falls with frequency —
so the upper passband is not the flat plateau the ideal analysis promises but a hump
near the self-resonance followed by a slow sag. It never rises above unity: the branch
is passive, so its impedance has a non-negative real part, so $|Z| \le |R + Z|$ at every
frequency and a passive divider can only ever divide.

**The source resistance is a component.** $R$ set the width, and in a real system part of
$R$ is whatever is driving the filter. Drive the 1 kHz notch above from something with
600 Ω of its own output impedance and you have added 600 Ω to $R$ without touching a
single part: the width goes from 1592 Hz to 2547 Hz, and the depth from −36.6 dB to
−40.6 dB, because 15 Ω is now being divided against 1615 Ω instead of 1015 Ω. The extra
4 dB is not a gift — it is the same fact as the extra 60% of width, which is the half you
did not want. Passive filters are only specified together with the impedances on both
ends of them.

**Below a few hundred hertz the inductor stops being reasonable.** The 1 kHz design above
already wanted 100 mH; a 50 Hz notch of the same $Q$, driven from the same 126 Ω, wants
2 H, which is heavy, expensive,
microphonic, and picks up the very hum it was bought to remove. Mains notches are therefore
built from resistors and capacitors in a twin-T network, or with an op-amp made to imitate
an inductor. Both are outside this course, and both are answers to a question this module
poses precisely: the $LC$ notch is right whenever the inductor is reasonable, and the
frequency is what decides whether it is.
''',
                },
            ],
            "quiz": {
                "title": "Tanks, notches and where the current goes",
                "minutes": 9,
                "questions": [
                    {
                        "q": "An ideal inductor and capacitor in parallel, at their resonant frequency, present what impedance?",
                        "opts": [
                            "Zero",
                            "The inductor's reactance, $\\omega_0 L$",
                            "A very large impedance — infinite for ideal components",
                            "Exactly the source resistance",
                        ],
                        "a": 2,
                        "why": r'''
Infinite, for ideal components. In admittance the two branches contribute
$+j\omega C$ and $-j/(\omega L)$, which cancel exactly at $\omega_0$; zero admittance
is infinite impedance. The zero answer is the *series* arrangement of the same two
components, which is worth keeping straight because the two circuits look almost
identical on a schematic and do opposite things.
''',
                    },
                    {
                        "q": "At that frequency, what are the two branch currents doing?",
                        "opts": [
                            "Both are zero",
                            "They are equal in magnitude and opposite in phase, so they cancel at the terminals and circulate around the loop",
                            "They add to twice the current the source supplies",
                            "They are 45° apart",
                        ],
                        "a": 1,
                        "why": r'''
They are equal and opposite, and they can be very much larger than anything the source
supplies. Energy sloshes from the inductor's magnetic field into the capacitor's
electric field and back, once per half cycle, with the source only topping up what the
loss consumes. If both were zero there would be no stored energy and nothing resonant
about it; the point is that a large current exists inside a loop that draws almost
nothing from outside.
''',
                    },
                    {
                        "q": "A series L–C branch is connected from the output node of a divider down to ground. What does that circuit do at the branch's resonant frequency?",
                        "opts": [
                            "Passes the signal untouched",
                            "Doubles the signal",
                            "Removes it — the branch is nearly a short to ground there",
                            "Shifts its phase by 90° and nothing else",
                        ],
                        "a": 2,
                        "why": r'''
It removes it. In series the two reactances cancel to leave almost nothing, so the
branch is a near short to ground at that one frequency and the output collapses. A
decade either side the branch is high impedance again — capacitive below, inductive
above — and the signal passes. That is a notch filter, and it is how a stubborn
interfering tone gets removed without touching the rest of the band.
''',
                    },
                    {
                        "q": "A notch built from L = 100 mH and C = 253 nF sits at 1 kHz. Which change moves the notch to a lower frequency?",
                        "opts": [
                            "Increasing the series resistor",
                            "Decreasing the capacitance",
                            "Increasing the inductance",
                            "Decreasing both L and C together",
                        ],
                        "a": 2,
                        "why": r'''
$f_0 = 1/(2\pi\sqrt{LC})$, so anything that increases the product $LC$ lowers the
resonance: more inductance does it, and so would more capacitance. Decreasing either
one raises it, and decreasing both raises it faster. The resistor does not appear in
the expression at all — it sets how deep and how wide the notch is, never where it
sits.
''',
                    },
                    {
                        "q": "What limits how deep a real notch can be?",
                        "opts": [
                            "The amplitude of the source",
                            "Loss in the components — chiefly the inductor's winding resistance, which stops the branch being a perfect short",
                            "The number of samples the instrument takes",
                            "Nothing — a notch built from a real L and C is infinitely deep",
                        ],
                        "a": 1,
                        "why": r'''
Loss. A real inductor is a resistance in series with an inductance, and at resonance
that resistance is all that is left of the shunt branch, so the notch bottoms out at
the divider ratio that resistance produces rather than at zero. Depth is therefore a
statement about component quality; a 40 dB notch needs component $Q$s in the hundreds.
The source amplitude cancels out of the ratio entirely, and the resonant frequency
itself is untouched by any of this.
''',
                    },
                    {
                        "q": "Well above its resonant frequency, a parallel L–C tank behaves like which single component?",
                        "opts": ["An inductor", "A capacitor", "A resistor", "An open circuit"],
                        "a": 1,
                        "why": r'''
Like a capacitor. Above resonance the capacitor's admittance $\omega C$ has grown and
the inductor's $1/(\omega L)$ has shrunk, so the capacitive branch carries almost all
of the current and dominates the parallel combination. Below resonance the same
argument runs the other way and the tank looks inductive. It is an open circuit only
in the immediate neighbourhood of $f_0$, which is precisely the narrow window that
makes it useful.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "A tank, one frequency at a time",
                    "minutes": 10,
                    "lang": "text",
                    "caption": "Two branches across one node, worked in siemens from the components to the resonance.",
                    "brief": r'''
A parallel pair is a node's problem, so it is done in admittance: susceptance for each
branch, added with its sign, and inverted once at the very end.

Microsiemens throughout, because the numbers stay readable that way — 1 µS is
$10^{-6}$ S. Signs are carried, and they are the whole point: a capacitor's susceptance
is positive, an inductor's is negative, and the resonance is where they annihilate.
''',
                    "listing": r'''
L = 10 mH,  C = 100 nF,  in parallel


at f = 4.00 kHz:      omega  =  ___ rad/s


    the inductor                  B_L  =  ___ uS

    the capacitor                 B_C  =  ___ uS

    the two together              B    =  ___ uS

    so the pair looks             ___

    and its impedance is  |Z|  =  ___ ohm


the frequency where B is zero:    f_0  =  ___ Hz
''',
                    "blanks": [
                        {
                            "prompt": "The angular frequency",
                            "hole": "omega",
                            "opts": ["25133", "4000", "12566", "0.00025"],
                            "a": 0,
                            "why": r'''
$\omega = 2\pi f = 2\pi \times 4000 = 25133$ rad/s. 4000 is the frequency in cycles per
second, which is what the front panel of a generator shows and not what goes into a
reactance; 12566 is $2\pi \times 2000$; and 0.00025 s is the period $T = 1/f$, a time
rather than a rate. Every line below is built on this number.
''',
                        },
                        {
                            "prompt": "The susceptance of the inductor",
                            "hole": "bl",
                            "opts": ["-3979", "+3979", "-251.3", "-0.003979"],
                            "a": 0,
                            "why": r'''
$B_L = -1/(\omega L) = -1/(25133 \times 0.01) = -1/251.33 = -3.9789\times10^{-4}$ S,
which is $-3979$ µS. The sign is not decoration: it is what allows the two branches to
cancel later, and dropping it makes the resonance impossible to find. The value $-251.3$
is $X_L = \omega L$ in ohms — a reactance, not a susceptance, and the reciprocal of what
was asked for. $-0.003979$ is the right quantity in siemens rather than microsiemens.
''',
                        },
                        {
                            "prompt": "The susceptance of the capacitor",
                            "hole": "bc",
                            "opts": ["+2513", "-2513", "+398.0", "+0.002513"],
                            "a": 0,
                            "why": r'''
$B_C = \omega C = 25133 \times 10^{-7} = 2.5133\times10^{-4}$ S $= +2513$ µS. Multiply,
do not invert — susceptance is the form in which a capacitor is easy, which is most of
why admittance is worth the change of variable. The value $+398.0$ is
$X_C = 1/(\omega C)$ in ohms, and $+0.002513$ is millisiemens rather than microsiemens.
''',
                        },
                        {
                            "prompt": "The two susceptances together",
                            "hole": "b",
                            "opts": ["-1466", "+6492", "-6492", "+1466"],
                            "a": 0,
                            "why": r'''
Parallel branches add their admittances, signs included:
$2513 - 3979 = -1466$ µS. The value $\pm 6492$ adds the two magnitudes, which is the
same reflex the series case punishes and is worse here, because a sum that can cancel is
exactly what this circuit is for. The sign of the answer is negative, which is a fact
about the circuit and not about the arithmetic: below resonance the coil wins.
''',
                        },
                        {
                            "prompt": "What the pair looks like at 4 kHz",
                            "hole": "kind",
                            "opts": ["inductive", "capacitive", "purely resistive"],
                            "a": 0,
                            "why": r'''
Inductive. A negative susceptance is an inductive one, and here the coil's $1/(\omega L)$
is still larger than the capacitor's $\omega C$ because 4 kHz is below the resonance. Push
the frequency up past $f_0$ and $\omega C$ overtakes, the sign flips, and the same two
components look capacitive. Purely resistive is what the pair never is: two ideal
reactances have no real part between them at any frequency, and at $f_0$ they have no
imaginary part either, which is why the impedance there is unbounded rather than real.
''',
                        },
                        {
                            "prompt": "The magnitude of the pair's impedance",
                            "hole": "zmag",
                            "opts": ["682.3", "154.0", "251.3", "397.9"],
                            "a": 0,
                            "why": r'''
$|Z| = 1/|B| = 1/(1466\times10^{-6}) = 682.3$ Ω. Invert once, at the end, after the
addition. The value 154.0 Ω is $1/6492$ µS, the answer that follows from adding the
magnitudes instead of the signed susceptances, and note that it is *smaller* than either
branch — which is what parallel resistors do and what parallel reactances of opposite
sign never do. 251.3 Ω and 397.9 Ω are the two branches' own reactances; the combination
is larger than both, and will keep growing as the frequency approaches $f_0$.
''',
                        },
                        {
                            "prompt": "The resonant frequency",
                            "hole": "f0",
                            "opts": ["5033", "31623", "4000", "1.59e8"],
                            "a": 0,
                            "why": r'''
$LC = 0.01 \times 10^{-7} = 10^{-9}$, $\sqrt{LC} = 3.1623\times10^{-5}$, and
$f_0 = 1/(2\pi \times 3.1623\times10^{-5}) = 5033$ Hz. The value 31623 is
$\omega_0 = 1/\sqrt{LC}$ in radians per second, the missing $2\pi$ that turns up in every
frequency in this course. 4000 Hz is where the rest of the listing was worked, which is a
choice about the source and not a property of the components. $1.59\times10^8$ is
$1/(2\pi LC)$ with the square root forgotten, and a coil and capacitor this size cannot
resonate anywhere near 159 MHz.
''',
                        },
                    ],
                },
                {
                    "title": "How deep the notch goes, and why",
                    "minutes": 10,
                    "lang": "text",
                    "caption": "A series L-C branch used as a shunt leg, from four component values to a depth in decibels.",
                    "brief": r'''
The 1 kHz notch, with a coil that is not ideal. The two $Q$s in this listing are different
quantities and it is worth keeping them apart: $Q_0$ belongs to the coil and describes how
good the component is, while the loaded $Q$ belongs to the filter and describes how narrow
the notch is. The depth is the ratio of the two.
''',
                    "listing": r'''
R = 1.00 kohm feeding the node,  and to ground:
L = 100 mH  in series with  r = 8 ohm  in series with  C = 253 nF


    f_0 = 1/(2*pi*sqrt(LC))                     =  ___ Hz

    X_0 = sqrt(L/C)                             =  ___ ohm

    the coil's own quality  Q_0 = X_0/r         =  ___

    the notch's loaded  Q = X_0/(R + r)         =  ___

    depth  = r/(R + r)                          =  ___

    in decibels                                 =  ___ dB
''',
                    "blanks": [
                        {
                            "prompt": "The notch frequency",
                            "hole": "f0",
                            "opts": ["1001", "6287", "0.0316"],
                            "a": 0,
                            "why": r'''
$LC = 0.1 \times 2.53\times10^{-7} = 2.53\times10^{-8}$, whose square root is
$1.5906\times10^{-4}$, so $f_0 = 1/(2\pi \times 1.5906\times10^{-4}) = 1001$ Hz. The
value 6287 is $\omega_0$ in radians per second; 0.0316 Hz is what comes out if the
capacitance is left in nanofarads, and a millihertz answer from parts this size should be
rejected on sight. Neither $R$ nor $r$ appears — resistance never moves a resonance.
''',
                        },
                        {
                            "prompt": "The reactance of either component at resonance",
                            "hole": "x0",
                            "opts": ["628.7", "395257", "0.001591", "1257"],
                            "a": 0,
                            "why": r'''
$X_0 = \sqrt{L/C} = \sqrt{0.1/2.53\times10^{-7}} = \sqrt{395257} = 628.7$ Ω. The check is
that $\omega_0 L = 6287 \times 0.1$ gives the same 628.7 Ω, as does $1/(\omega_0 C)$ —
they are equal at resonance, and that is what resonance means. 395257 is $L/C$ with the
root not taken; 0.001591 S is $\sqrt{C/L}$, the susceptance rather than the reactance;
and 1257 is the two reactances added rather than either one of them, a sum that is
meaningless here because they point in opposite directions.
''',
                        },
                        {
                            "prompt": "The coil's own quality factor",
                            "hole": "q0",
                            "opts": ["78.59", "0.01272", "5030"],
                            "a": 0,
                            "why": r'''
$Q_0 = X_0/r = 628.7/8 = 78.59$. This number describes the inductor and nothing else —
it would be the same if the coil were soldered into a different circuit, and it is the
figure a data sheet quotes, at a stated frequency, because $X_0$ and $r$ both change with
frequency. 0.01272 is $r/X_0$, the ratio the right way up but inverted; 5030 is
$X_0 \times r$, a product with no meaning.
''',
                        },
                        {
                            "prompt": "The loaded quality factor of the notch",
                            "hole": "ql",
                            "opts": ["0.6237", "1.603", "78.59"],
                            "a": 0,
                            "why": r'''
$Q = X_0/(R + r) = 628.7/1008 = 0.6237$. The resonating current has to push through
everything in its loop, and the 1 kΩ feeding the node is in that loop, so it dwarfs the
coil's 8 Ω and sets the width almost single-handedly: $\text{BW} = f_0/Q = 1604$ Hz, a
notch wider than the frequency it sits at. 1.603 is the reciprocal, which is the
bandwidth in units of $f_0$ rather than the $Q$; 78.59 is the coil's own $Q$, which
describes the part and not the filter.
''',
                        },
                        {
                            "prompt": "The depth, as a ratio",
                            "hole": "depth",
                            "opts": ["0.007937", "0.9921", "126.0"],
                            "a": 0,
                            "why": r'''
At $f_0$ the two reactances have cancelled and the whole branch is just $r$, so the
divider is 8 Ω under 1000 Ω: $8/1008 = 0.007937$. Confirm it against the general rule —
depth $= Q/Q_0 = 0.6237/78.59 = 0.007937$, the same number, which is worth doing because
that rule is the one you can use before any component is chosen. 0.9921 is
$R/(R+r)$, the fraction that is *lost* rather than the fraction that survives; 126.0 is
$R/r$, the depth upside down.
''',
                        },
                        {
                            "prompt": "The same depth in decibels",
                            "hole": "db",
                            "opts": ["-42.01", "+42.01", "-21.00", "-84.02"],
                            "a": 0,
                            "why": r'''
$20\log_{10}(0.007937) = -42.01$ dB. It is a voltage ratio, so the multiplier is 20, not
10; $-21.00$ dB is the same ratio put through $10\log_{10}$, which is the rule for
powers and halves every answer. The sign is negative because the output is smaller than
the input, and $+42.01$ dB would be a filter with gain in it. $-84.02$ dB is the figure
doubled, which is what you get by applying the decibel conversion twice.
''',
                        },
                    ],
                },
            ],
            "build": {
                "title": "A notch at 1 kHz",
                "minutes": 24,
                "brief": r'''
Remove one frequency and leave the rest alone.

You are given a source, a 1 kΩ resistor in series, the probe on the far side of it,
and a ground rail waiting underneath. As it stands the resistor does nothing — no
current flows in it, so the probe reads the source at every frequency.

Add a **series inductor and capacitor from the probe node down to the ground rail** so
that the circuit becomes a notch at 1 kHz.

1. **At DC nothing is lost.** The capacitor is an open circuit, so the shunt branch
   draws no current and the probe reads the whole source.
2. **At 1 kHz there is essentially nothing left** — under 3% of the source.
3. **A decade either side the signal is untouched**: at 100 Hz and at 10 kHz the probe
   reads at least 90% of the source.
4. **The notch is narrow.** At 500 Hz and at 2 kHz more than half the signal is already
   back.

Only the product $LC$ fixes the frequency: $f_0 = 1/(2\pi\sqrt{LC})$. Choose an
inductance you like and the capacitance follows. Around 100 mH keeps the capacitor a
believable size.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 1000},
                        {"id": "p3", "kind": "OUT", "x": 8, "y": 3, "rot": 0, "value": 0},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [8, 3]},
                        {"a": [8, 7], "b": [3, 7]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 1000},
                        {"id": "p3", "kind": "OUT", "x": 8, "y": 3, "rot": 0, "value": 0},
                        {"id": "p4", "kind": "L", "x": 8, "y": 4, "rot": 1, "value": 0.1},
                        {"id": "p5", "kind": "C", "x": 8, "y": 6, "rot": 1, "value": 2.53e-7},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [8, 3]},
                        {"a": [8, 7], "b": [3, 7]},
                    ],
                },
                "checks": [
                    {"name": "at DC the whole source reaches the output", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(Math.abs(c.vout()), vs, 0.01,
  "the capacitor is an open circuit at DC, so no current flows in the series resistor and nothing is dropped across it");
'''},
                    {"name": "at 1 kHz there is essentially nothing left", "code": r'''
var vs = Math.abs(c.values("V")[0]);
var g = c.gain(1000) / vs;
c.assert(g < 0.03,
  "the shunt branch should be a near short to ground at 1 kHz; measured " + g.toPrecision(3) +
  " of the source, so the resonance is not landing there");
'''},
                    {"name": "a decade either side the signal is untouched", "code": r'''
var vs = Math.abs(c.values("V")[0]);
var lo = c.gain(100) / vs, hi = c.gain(10000) / vs;
c.assert(lo > 0.9, "at 100 Hz the branch should be high impedance; measured " + lo.toPrecision(3));
c.assert(hi > 0.9, "at 10 kHz it should be high impedance again; measured " + hi.toPrecision(3));
'''},
                    {"name": "the notch is narrow", "code": r'''
var vs = Math.abs(c.values("V")[0]);
var a = c.gain(500) / vs, b = c.gain(2000) / vs;
c.assert(a > 0.5 && b > 0.5,
  "an octave either side of the notch more than half the signal should be back; measured " +
  a.toPrecision(3) + " at 500 Hz and " + b.toPrecision(3) + " at 2 kHz");
'''},
                ],
                "hints": [
                    "The inductor and the capacitor go one above the other, in a single branch from the probe node down to the ground rail. Side by side in parallel would give a circuit that does the opposite.",
                    "$LC = 1/(2\\pi f_0)^2 = 2.53\\times10^{-8}$. With $L = 100$ mH that makes $C = 253$ nF.",
                    "Click a part to change its value; engineering suffixes work, so 253n and 100m are enough.",
                    "If the output is near zero everywhere *except* at 1 kHz, the inductor and the capacitor are across one another rather than one above the other. That arrangement is a tank, and it does exactly the opposite job.",
                ],
            },
            "numeric": [
                {
                    "title": "Where does this notch sit?",
                    "minutes": 7,
                    "brief": r"""
    The same circuit with different parts in it. The resistor is there to give the divider
    something to divide against; it plays no part at all in the answer, which is worth
    proving to yourself by looking for it in the formula.
    """,
                    "prompt": "At what frequency does the output of this network fall to nearly zero?",
                    "note": "Answer in hertz, to the nearest ten.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "r", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 2200},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3},
                            {"id": "l", "kind": "L", "x": 10, "y": 4, "rot": 1, "value": 0.047},
                            {"id": "c", "kind": "C", "x": 10, "y": 6, "rot": 1, "value": 2.2e-7},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Series resistor", "value": "2.20 k\u03a9"},
                        {"label": "Inductor", "value": "47 mH"},
                        {"label": "Capacitor", "value": "220 nF"},
                        {"label": "Source", "value": "1 V, swept"},
                    ],
                    "aside": "The shunt branch is a series L-C. Its impedance is smallest where the two "
                             "reactances cancel, and that is the only place the output can collapse.",
                    "answer": 1565.0,
                    "tol": 20.0,
                    "unit": "Hz",
                    # The prompt asks where the output collapses, so the check looks for
                    # exactly that rather than restating $1/(2\pi\sqrt{LC})$: the magnitude
                    # falls monotonically to the notch and rises monotonically after it, so a
                    # ternary search on log f over five decades lands on the minimum. Nothing
                    # here names L, C or R, so editing any of them moves the measured answer.
                    "check": r'''
    var lo = Math.log(10), hi = Math.log(1e6);
    for (var i = 0; i < 60; i++) {
      var a = lo + (hi - lo) / 3, b = hi - (hi - lo) / 3;
      if (c.gain(Math.exp(a)) < c.gain(Math.exp(b))) hi = b; else lo = a;
    }
    var f0 = Math.exp((lo + hi) / 2);
    c.assert(c.gain(f0) < 0.05 * c.gain(10),
      "the response has no notch in it: the smallest output found was " + c.gain(f0).toPrecision(3));
    return f0;
    ''',
                    "hint": "$f_0 = 1/(2\\pi\\sqrt{LC})$, and $LC = 0.047 \\times 2.2\\times10^{-7}$.",
                    "wrong": "If the answer came out near 9800, the $2\\pi$ is missing and the figure is "
                             "$\\omega_0$ in radians per second. If the resistor appears anywhere in your "
                             "working, it should not.",
                    "why": "$LC = 1.034\\times10^{-8}$, whose square root is $1.0169\\times10^{-4}$, so "
                           "$f_0 = 1/(2\\pi \\times 1.0169\\times10^{-4}) = 1565$ Hz. The resistor sets how "
                           "deep and how wide the notch is \u2014 a larger one makes the divider bite harder "
                           "against the shunt branch \u2014 but it cannot move it, because the branch's "
                           "impedance reaches its minimum where $\\omega L = 1/(\\omega C)$ regardless of "
                           "what is upstream.",
                },
                {
                    "title": "How deep does it actually go?",
                    "minutes": 8,
                    "brief": r'''
Second rung, and the first one with a real component in it. The coil in this notch has its
winding resistance drawn as a separate resistor inside the shunt branch, which is exactly
where it lives in a real one — you cannot buy the inductance without it.

At the notch frequency the two reactances cancel, and the question is what is left. Work
out what the branch's impedance is *there*, then it is a divider like any other.
''',
                    "prompt": "What voltage does the probe read at the notch frequency?",
                    "note": "Give the answer in millivolts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 11, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 2200},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3, "rot": 0, "value": 0},
                            {"id": "l1", "kind": "L", "x": 10, "y": 4, "rot": 1, "value": 0.068},
                            {"id": "rw", "kind": "R", "x": 10, "y": 6, "rot": 1, "value": 12},
                            {"id": "c1", "kind": "C", "x": 10, "y": 8, "rot": 1, "value": 1e-7},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 9], "b": [3, 11]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 9], "b": [3, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "6.00 V RMS, at the notch frequency"},
                        {"label": "Feed resistor", "value": "2.20 k\u03a9"},
                        {"label": "Inductor", "value": "68 mH"},
                        {"label": "The coil's winding resistance", "value": "12 \u03a9, in series with it"},
                        {"label": "Capacitor", "value": "100 nF"},
                    ],
                    "aside": "The notch frequency is not needed for the answer, which is worth noticing "
                             "rather than resenting: at resonance the branch is its resistance whatever "
                             "that frequency turns out to be. Work it out anyway as a check on the "
                             "drawing \u2014 it should land near 1.9 kHz.",
                    "answer": 32.55,
                    "tol": 0.25,
                    "unit": "mV",
                    # Measured, not restated: the check hunts the drawn circuit for the frequency
                    # where the output is smallest and reports the voltage there, so neither the
                    # notch frequency nor the divider ratio is taken from the prompt.
                    "check": r'''
c.assert(c.count('L') === 1 && c.count('C') === 1 && c.count('R') === 2,
         "one coil, one capacitor, and two resistances");
var lo = Math.log(10), hi = Math.log(1e6);
for (var i = 0; i < 200; i++) {
  var a = lo + (hi - lo) / 3, b = hi - (hi - lo) / 3;
  if (c.gain(Math.exp(a)) < c.gain(Math.exp(b))) hi = b; else lo = a;
}
var f0 = Math.exp((lo + hi) / 2);
c.assert(c.gain(f0) < 0.05 * c.gain(10),
  "there is no notch in this response: the smallest output found was " + c.gain(f0).toPrecision(3));
return 1000 * c.gain(f0);
''',
                    "hint": "At $f_0$ the inductor's $+\\omega L$ and the capacitor's $-1/(\\omega C)$ "
                            "add to zero, so the whole shunt branch reduces to the one thing in it that "
                            "is not a reactance. Then it is a two-resistor divider.",
                    "wrong": "2106 mV puts the coil's reactance at resonance, 824.6 \u03a9, into the "
                             "divider as though the capacitor were not there to cancel it. 5.42 mV is "
                             "the right ratio applied to a 1 V source instead of the 6 V drawn. "
                             "0.0326 is the answer left in volts. And 32.7 mV divides by the 2.20 "
                             "k\u03a9 alone instead of by the whole loop \u2014 that one is only 0.5% "
                             "out, because 12 \u03a9 beside 2200 \u03a9 barely matters, and it is worth "
                             "knowing which approximations are free.",
                    "why": r'''
```
LC        = 0.068 * 1e-7                       = 6.8000e-9
sqrt(LC)                                       = 8.24621e-5
f_0       = 1/(2*pi*8.24621e-5)                = 1930.0 Hz
```

At 1930 Hz the branch's two reactances are equal and opposite:

```
X_0       = sqrt(L/C) = sqrt(0.068/1e-7)
          = sqrt(680000)                       = 824.62 ohm
w_0 L     = 12127 * 0.068                      = 824.62 ohm
1/(w_0 C) = 1/(12127 * 1e-7)                   = 824.62 ohm
```

so they cancel out of the branch entirely and what is left is the 12 Ω of wire the coil
is wound from. The circuit at that one frequency is a plain resistive divider:

```
V_out     = 6.00 * 12/(2200 + 12)
          = 6.00 * 0.0054250                   = 32.55 mV
```

Two things follow that are worth carrying forward. The first is the depth in decibels,
$20\log_{10}(0.005425) = -45.3$ dB, and that number is a statement about the *coil*: put
a better one in, with 4 Ω instead of 12 Ω, and the notch goes to −54.8 dB with nothing
else changed. The second is that this notch is not narrow. Its loaded $Q$ is
$X_0/(R + r) = 824.6/2212 = 0.373$, so the −3 dB width is $f_0/Q = 5177$ Hz, wider than
the frequency it sits at. Depth and narrowness are bought separately, and here we have
one of them.
''',
                },
                {
                    "title": "How wide is the peak?",
                    "minutes": 9,
                    "brief": r'''
Third rung. The tank the other way up: fed through a resistor, so at resonance it is an
open circuit and the whole source arrives at the probe, and either side of resonance it
loads the node down.

The question is not where the peak is but how wide it is, which needs two steps rather
than one — a $Q$ before a bandwidth — and needs the right $Q$ of the two on offer.
''',
                    "prompt": "What is the \u22123 dB bandwidth of this circuit's response?",
                    "note": "Give the answer in hertz, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 47000},
                            {"id": "out", "kind": "OUT", "x": 8, "y": 3, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 8, "y": 5, "rot": 1, "value": 4.7e-8},
                            {"id": "l1", "kind": "L", "x": 11, "y": 5, "rot": 1, "value": 0.022},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [4, 3]},
                            {"a": [6, 3], "b": [8, 3]},
                            {"a": [8, 3], "b": [8, 4]},
                            {"a": [8, 6], "b": [8, 7]},
                            {"a": [8, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 4]},
                            {"a": [11, 6], "b": [11, 7]},
                            {"a": [3, 7], "b": [8, 7]},
                            {"a": [8, 7], "b": [11, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 V, frequency swept"},
                        {"label": "Feed resistor", "value": "47.0 k\u03a9"},
                        {"label": "Capacitor", "value": "47 nF"},
                        {"label": "Inductor", "value": "22 mH"},
                    ],
                    "aside": "Two quantities are wanted on the way: the centre frequency, and the $Q$ "
                             "of a tank fed from a resistance. The second is not the series formula "
                             "from the previous module \u2014 it is that formula turned upside down.",
                    "answer": 72.05,
                    "tol": 0.6,
                    "unit": "Hz",
                    # Measured end to end: the check finds the peak of the drawn circuit's response
                    # by ternary search on log f, then bisects outwards on each side for the two
                    # frequencies where the output has fallen to 1/sqrt(2) of it, and returns the
                    # difference. No component value is named anywhere in it.
                    "check": r'''
var lo = Math.log(1), hi = Math.log(1e7);
for (var i = 0; i < 300; i++) {
  var a = lo + (hi - lo) / 3, b = hi - (hi - lo) / 3;
  if (c.gain(Math.exp(a)) > c.gain(Math.exp(b))) hi = b; else lo = a;
}
var f0 = Math.exp((lo + hi) / 2), pk = c.gain(f0), t = pk / Math.SQRT2;
var a = f0, b = f0 * 100, m;
for (var i = 0; i < 200; i++) { m = Math.sqrt(a * b); if (c.gain(m) > t) a = m; else b = m; }
var fhi = Math.sqrt(a * b);
a = f0 / 100; b = f0;
for (var i = 0; i < 200; i++) { m = Math.sqrt(a * b); if (c.gain(m) > t) b = m; else a = m; }
var flo = Math.sqrt(a * b);
c.assert(pk > 5 * c.gain(f0 / 10),
  "the response has no peak to measure: it is " + pk.toPrecision(3) + " at its largest");
return fhi - flo;
''',
                    "hint": "$\\text{BW} = f_0/Q$, and for a tank fed from a resistance "
                            "$Q = R\\sqrt{C/L} = R/X_0$. Both roads end in the same place: "
                            "$\\text{BW} = 1/(2\\pi R C)$, which uses no inductance at all.",
                    "wrong": "340 kHz is $R/(2\\pi L)$, the *series* bandwidth, which is what you get "
                             "by using $Q = X_0/R$ instead of $Q = R/X_0$; it is 4700 times too wide "
                             "and a bandwidth seventy times larger than the centre frequency should "
                             "stop you. 4950 Hz is the centre frequency rather than the width. 453 is "
                             "the bandwidth in radians per second, $1/(RC)$, with the $2\\pi$ left in.",
                    "why": r'''
```
LC        = 0.022 * 4.7e-8                     = 1.0340e-9
sqrt(LC)                                       = 3.21559e-5
f_0       = 1/(2*pi*3.21559e-5)                = 4949.5 Hz
X_0       = sqrt(L/C) = sqrt(0.022/4.7e-8)
          = sqrt(468085)                       = 684.17 ohm
Q         = R/X_0 = 47000/684.17               = 68.697
BW        = f_0/Q = 4949.5/68.697              = 72.05 Hz
```

Every one of those steps has a shortcut that skips the one before it, and they are worth
collecting because they are the same fact wearing different clothes:

```
Q         = R*sqrt(C/L) = 47000*sqrt(4.7e-8/0.022)   = 68.697
BW        = 1/(2*pi*R*C) = 1/(2*pi*47000*4.7e-8)     = 72.05 Hz
```

The second one is the useful one. A tank's bandwidth in hertz is $1/(2\pi R C)$ and the
inductance is nowhere in it — exactly mirroring the series resonator, whose bandwidth
$R/(2\pi L)$ contains no capacitance. To narrow this response at a fixed centre frequency
you raise $R$ or lower $C$, and then $L$ follows to put $f_0$ back where it was.

For the record, the two edges are not symmetric about 4949.5 Hz in hertz. They are at
4913.6 Hz and 4985.6 Hz, whose *product* is $f_0^2$; the peak sits at their geometric
mean, which is why a swept response looks symmetric on a log axis and slightly lopsided
on a linear one. At a $Q$ of 69 the lopsidedness is 0.1% and invisible. At a $Q$ of 2 it
is not.
''',
                },
                {
                    "title": "The current that never leaves the loop",
                    "minutes": 10,
                    "brief": r'''
Fourth rung, and the source has changed. A current source pushes its stated current
whatever stands in the way, so there is nothing to divide at the start: the impedance
turns the current into a voltage rather than the other way round.

At resonance the two reactive branches cancel each other and the node sees only the
resistor. What is asked for is not that node's voltage but the current in one branch,
which is a different quantity and much the larger one.
''',
                    "prompt": "What RMS current flows in the inductor at the resonant frequency?",
                    "note": "Give the answer in milliamps, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "is", "kind": "I", "x": 3, "y": 5, "rot": 1, "value": 1e-3},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                            {"id": "out", "kind": "OUT", "x": 5, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 7, "y": 5, "rot": 1, "value": 10000},
                            {"id": "l1", "kind": "L", "x": 10, "y": 5, "rot": 1, "value": 0.01},
                            {"id": "c1", "kind": "C", "x": 13, "y": 5, "rot": 1, "value": 1e-7},
                        ],
                        "wires": [
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [5, 3], "b": [7, 3]},
                            {"a": [7, 3], "b": [7, 4]},
                            {"a": [7, 6], "b": [7, 7]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 3], "b": [10, 4]},
                            {"a": [10, 6], "b": [10, 7]},
                            {"a": [10, 3], "b": [13, 3]},
                            {"a": [13, 3], "b": [13, 4]},
                            {"a": [13, 6], "b": [13, 7]},
                            {"a": [3, 7], "b": [7, 7]},
                            {"a": [7, 7], "b": [10, 7]},
                            {"a": [10, 7], "b": [13, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "1.00 mA RMS, at the resonant frequency"},
                        {"label": "Resistor", "value": "10.0 k\u03a9"},
                        {"label": "Inductor", "value": "10 mH"},
                        {"label": "Capacitor", "value": "100 nF"},
                    ],
                    "aside": "Three steps, none of them long: what the node's impedance is at "
                             "resonance, what voltage that puts on the node, and what current that "
                             "voltage drives through the coil's reactance. The resonant frequency is "
                             "needed this time, because the reactance depends on it.",
                    "answer": 31.62,
                    "tol": 0.25,
                    "unit": "mA",
                    # The node voltage is solved for rather than assumed: the check finds the peak of
                    # the drawn circuit's response, reads the voltage there, and divides by the
                    # inductor's reactance computed from the value the netlist reports.
                    "check": r'''
c.assert(c.count('I') === 1 && c.count('V') === 0, "a current source drives this one");
var lo = Math.log(10), hi = Math.log(1e7);
for (var i = 0; i < 300; i++) {
  var a = lo + (hi - lo) / 3, b = hi - (hi - lo) / 3;
  if (c.gain(Math.exp(a)) > c.gain(Math.exp(b))) hi = b; else lo = a;
}
var f0 = Math.exp((lo + hi) / 2);
return 1000 * c.gain(f0) / (2 * Math.PI * f0 * c.values('L')[0]);
''',
                    "hint": "At $f_0$ the two susceptances cancel, so the node's admittance is just "
                            "$1/R$ and its voltage is $I R$. The coil then carries $V/X_0$ with "
                            "$X_0 = \\omega_0 L = \\sqrt{L/C}$.",
                    "wrong": "1.00 mA assumes the coil carries what the source supplies, which would "
                             "be true if the coil were the only branch. 10.0 mA is the resistor's "
                             "branch, $V/R$. 0.0316 is the right answer left in amps. 63.2 mA adds "
                             "the coil's current to the capacitor's, and those two are exactly "
                             "opposite in phase, so adding them gives zero, not double.",
                    "why": r'''
```
LC        = 0.01 * 1e-7                        = 1.0000e-9
sqrt(LC)                                       = 3.16228e-5
f_0       = 1/(2*pi*3.16228e-5)                = 5032.9 Hz
w_0       = 1/3.16228e-5                       = 31623 rad/s
```

At $f_0$ the inductor's susceptance $-1/(\omega_0 L)$ and the capacitor's $+\omega_0 C$
are equal and opposite, so the only admittance the source can see is the resistor's:

```
V_node    = I * R = 1.00e-3 * 10000            = 10.00 V rms
X_0       = w_0 * L = 31623 * 0.01             = 316.23 ohm
   (also  sqrt(L/C) = sqrt(0.01/1e-7) = sqrt(100000) = 316.23)
I_L       = V/X_0 = 10.00/316.23               = 31.62 mA
```

One milliamp in, 31.6 mA going round. The capacitor carries the same 31.6 mA in the
opposite direction — $V \omega_0 C = 10.00 \times 31623 \times 10^{-7}$ is the same
number — and the two cancel at the node so completely that the source never learns they
exist.

The multiplication factor is $Q$, and you can see it in the arithmetic without doing any
more of it:

```
Q         = R/X_0 = 10000/316.23               = 31.62
I_L       = Q * I_source = 31.62 * 1.00 mA     = 31.62 mA
```

That is worth remembering for the reason resonance is always worth watching: a $Q$ of 30
in a circuit fed a milliamp puts thirty milliamps through a coil, and a $Q$ of 300 puts
three hundred. Components in a resonant loop are sized for the circulating current, not
for the supply current, and the two can differ by two orders of magnitude.
''',
                },
                {
                    "title": "What gets past the trap",
                    "minutes": 12,
                    "brief": r'''
The hardest one here, and nothing in it is new — it is four steps you have each done
once, with none of them signposted.

The tank has moved into the signal path rather than hanging off it, which turns it from a
peak into a hole: at $f_0$ it is an open circuit and nothing reaches the load. This
question asks about a frequency that is not $f_0$, so the tank is neither open nor
negligible, and its impedance has to be worked out properly and then combined with the
load. What is wanted at the end is a power.
''',
                    "prompt": "How much average power does the 4.70 k\u03a9 load dissipate at 4.00 kHz?",
                    "note": "Give the answer in milliwatts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                            {"id": "l1", "kind": "L", "x": 7, "y": 2, "rot": 0, "value": 0.01},
                            {"id": "c1", "kind": "C", "x": 7, "y": 4, "rot": 0, "value": 1e-7},
                            {"id": "out", "kind": "OUT", "x": 10, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 10, "y": 5, "rot": 1, "value": 4700},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [3, 2]},
                            {"a": [3, 2], "b": [6, 2]},
                            {"a": [3, 3], "b": [3, 4]},
                            {"a": [3, 4], "b": [6, 4]},
                            {"a": [8, 2], "b": [10, 2]},
                            {"a": [10, 2], "b": [10, 3]},
                            {"a": [8, 4], "b": [10, 4]},
                            {"a": [10, 4], "b": [10, 3]},
                            {"a": [10, 6], "b": [10, 7]},
                            {"a": [10, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "10.0 V RMS at 4.00 kHz"},
                        {"label": "Trap inductor", "value": "10 mH"},
                        {"label": "Trap capacitor", "value": "100 nF, across it"},
                        {"label": "Load", "value": "4.70 k\u03a9 to ground"},
                    ],
                    "aside": "The trap is two branches in parallel, so add their susceptances \u2014 "
                             "with signs \u2014 and invert once. What comes out is a pure reactance, "
                             "and a reactance in series with a resistance combines by Pythagoras, "
                             "never by addition.",
                    "answer": 20.84,
                    "tol": 0.2,
                    "unit": "mW",
                    # Solved rather than restated: the check reads the probed voltage across the load
                    # at the stated frequency and turns it into a power with the resistance the
                    # netlist reports, so both the trap's impedance and the divider come from the
                    # drawing.
                    "check": r'''
c.assert(c.count('R') === 1 && c.count('L') === 1 && c.count('C') === 1,
         "one load resistor, one coil, one capacitor");
var R = c.values('R')[0], v = c.gain(4000);
return 1000 * v * v / R;
''',
                    "hint": "Find the trap's susceptance $B = \\omega C - 1/(\\omega L)$ at 4 kHz "
                            "first; its impedance is $1/|B|$ and it is a reactance, not a resistance. "
                            "Then $|Z_{tot}| = \\sqrt{R^2 + X^2}$, then $I = V/|Z_{tot}|$, then "
                            "$P = I^2 R$.",
                    "wrong": "21.3 mW is $V^2/R$ with the trap ignored altogether, which is what the "
                             "circuit does far from $f_0$ but not here. 21.3 mW also arrives from "
                             "treating the coil and capacitor as though they were in *series* in the "
                             "path \u2014 the two errors happen to land on the same number, and both "
                             "miss the same 2%. 29.1 mW subtracts 682 \u03a9 from 4700 \u03a9 instead "
                             "of combining them at right angles. 0.0208 is the answer in watts.",
                    "why": r'''
The trap is an inductor and a capacitor in parallel, so work in susceptance and keep the
signs:

```
w         = 2*pi*4000                          = 25133 rad/s
w*C       = 25133 * 1e-7                       = 2.51327e-3 S
1/(w*L)   = 1/(25133 * 0.01)                   = 3.97887e-3 S
B         = 2.51327e-3 - 3.97887e-3            = -1.46560e-3 S
|Z_trap|  = 1/1.46560e-3                       = 682.31 ohm
```

Negative susceptance means the coil is still winning, which it must: the trap's resonance
is at

```
f_0       = 1/(2*pi*sqrt(0.01*1e-7))           = 5032.9 Hz
```

and 4 kHz is below it. So the trap is 682 Ω of *inductive* reactance sitting in series
with the 4.70 kΩ load, and reactance and resistance combine at right angles:

```
|Z_tot|   = sqrt(4700^2 + 682.31^2)
          = sqrt(22090000 + 465547)            = 4749.3 ohm
I         = 10.00/4749.3                       = 2.1056 mA rms
P         = I^2 * R = (2.1056e-3)^2 * 4700     = 20.84 mW
```

As a cross-check, the voltage the probe reads is $I R = 2.1056 \times 4.700 = 9.896$ V,
and $9.896^2/4700$ is the same 20.84 mW. The trap has cost the load 2% of its power at
4 kHz, which is the point of a trap: it is meant to be almost invisible everywhere except
in the small neighbourhood it was built for. At 5032.9 Hz the same circuit delivers a
power of order $10^{-9}$ mW, while at 1 kHz and at 20 kHz alike it delivers 21.27 mW,
which is the 21.28 mW of an unobstructed divider to within a rounding.
''',
                },
            ],
            "derive": {
                "title": "How wide the notch is, exactly",
                "minutes": 15,
                "vars": ["R", "L", "C", "X", "omega", "omega_0", "Q", "j"],
                "brief": r'''
A resistor $R$ from the source down to the output node, and a series $L$–$C$ branch from
that node to ground: the notch. Take the components as ideal, so the branch has no
resistance of its own.

Seven steps take that to a bandwidth, and the reward for doing it exactly rather than in
the usual narrow-band approximation is that the answer turns out to be exact — the two
half-power frequencies are $R/L$ apart in radians per second at *any* $Q$, not only a
high one.

As before, $j$ is the square root of $-1$ and stays a symbol throughout. $X$ is a name
for the branch's reactance once you have it.
''',
                "steps": [
                    {
                        "prompt": "Write the impedance of the series $L$\u2013$C$ branch, with both reactances collected into a single bracket multiplied by $j$.",
                        "answer": "j\\left(\\omega L - \\frac{1}{\\omega C}\\right)",
                        "hint": "Series impedances add. The inductor contributes $j\\omega L$ and the capacitor $1/(j\\omega C)$, and multiplying that second term above and below by $j$ turns it into $-j/(\\omega C)$.",
                        "deconstruct": [
                            "$Z = j\\omega L + \\dfrac{1}{j\\omega C}$.",
                            "$\\dfrac{1}{j} = -j$, so the capacitor's term is $-\\dfrac{j}{\\omega C}$.",
                            "Both terms now carry a $j$ and can be gathered into one bracket.",
                        ],
                    },
                    {
                        "prompt": "The output is the node between $R$ and that branch. Write the transfer function $V_{out}/V_{in}$ of the divider, leaving the bracket written out.",
                        "answer": "\\frac{j\\left(\\omega L - \\frac{1}{\\omega C}\\right)}{R + j\\left(\\omega L - \\frac{1}{\\omega C}\\right)}",
                        "placeholder": "\\frac{Z}{\\ldots}",
                        "hint": "A divider is the lower impedance over the sum of the two. Nothing about that changes when the impedances are complex.",
                        "deconstruct": [
                            "The lower leg is the branch $Z$ from the step above; the upper leg is $R$.",
                            "$\\dfrac{V_{out}}{V_{in}} = \\dfrac{Z}{R + Z}$.",
                            "Substitute $Z$ into both places it appears.",
                        ],
                    },
                    {
                        "prompt": "Call the bracket $X$, so the branch is $jX$. Write $|H|^2$ in terms of $R$ and $X$ alone.",
                        "answer": "\\frac{X^2}{R^2 + X^2}",
                        "hint": "The magnitude of a complex fraction is the magnitude of the top over the magnitude of the bottom, and $|R + jX| = \\sqrt{R^2 + X^2}$. Square the whole thing and the roots disappear.",
                        "deconstruct": [
                            "$|jX| = |X|$ and $|R + jX| = \\sqrt{R^2 + X^2}$.",
                            "So $|H| = \\dfrac{|X|}{\\sqrt{R^2 + X^2}}$.",
                            "Squaring both sides removes the root and the absolute value at once.",
                        ],
                    },
                    {
                        "prompt": "The half-power points are where $|H|^2 = \\tfrac12$. Solve that for $X^2$.",
                        "answer": "R^2",
                        "hint": "Cross-multiply: $2X^2 = R^2 + X^2$.",
                        "deconstruct": [
                            "$\\dfrac{X^2}{R^2 + X^2} = \\dfrac12$ gives $2X^2 = R^2 + X^2$.",
                            "Subtract $X^2$ from both sides.",
                        ],
                    },
                    {
                        "prompt": "Take the upper edge, where $X = +R$. Substitute $X = \\omega L - 1/(\\omega C)$, multiply through by $\\omega$ to clear the fraction, and write the positive root of the quadratic in $\\omega$ that results.",
                        "answer": "\\frac{RC + \\sqrt{R^2C^2 + 4LC}}{2LC}",
                        "placeholder": "\\frac{\\ldots + \\sqrt{\\ldots}}{2LC}",
                        "hint": "Multiplying $\\omega L - 1/(\\omega C) = R$ by $\\omega$ and then by $C$ gives $LC\\omega^2 - RC\\omega - 1 = 0$. Then it is the ordinary quadratic formula with $a = LC$, $b = -RC$, $c = -1$.",
                        "deconstruct": [
                            "$\\omega^2 L - \\dfrac{1}{C} = R\\omega$, and multiplying by $C$: $LC\\omega^2 - RC\\omega - 1 = 0$.",
                            "$\\omega = \\dfrac{RC \\pm \\sqrt{R^2C^2 + 4LC}}{2LC}$.",
                            "The discriminant exceeds $RC$, so only the $+$ root is positive.",
                        ],
                    },
                    {
                        "prompt": "The lower edge comes from $X = -R$ and is the same expression with the sign of the $RC$ term flipped. Subtract the two roots to get the bandwidth in radians per second.",
                        "answer": "\\frac{R}{L}",
                        "hint": "The two square roots are identical, so they cancel in the subtraction and only the $RC$ terms survive.",
                        "deconstruct": [
                            "$\\omega_{hi} - \\omega_{lo} = \\dfrac{(RC + S) - (-RC + S)}{2LC}$ where $S$ is the common square root.",
                            "The numerator is $2RC$.",
                            "$\\dfrac{2RC}{2LC}$ cancels to $\\dfrac{R}{L}$.",
                        ],
                    },
                    {
                        "prompt": "The $Q$ of a resonance is its centre frequency divided by its bandwidth. With $\\omega_0 = 1/\\sqrt{LC}$, write $Q$ in terms of $R$, $L$ and $C$ only.",
                        "answer": "\\frac{1}{R}\\sqrt{\\frac{L}{C}}",
                        "hint": "$Q = \\omega_0/(R/L) = \\omega_0 L/R$, and $\\dfrac{L}{\\sqrt{LC}}$ simplifies \u2014 divide top and bottom by $\\sqrt{L}$.",
                        "deconstruct": [
                            "$Q = \\dfrac{\\omega_0}{R/L} = \\dfrac{\\omega_0 L}{R} = \\dfrac{L}{R\\sqrt{LC}}$.",
                            "$\\dfrac{L}{\\sqrt{LC}} = \\sqrt{\\dfrac{L^2}{LC}} = \\sqrt{\\dfrac{L}{C}}$.",
                        ],
                    },
                ],
                "closing": r'''
Three results came out of that, and only one of them was asked for.

$\text{BW} = R/L$ rad/s, or $R/(2\pi L)$ hertz, with no approximation anywhere in the
derivation — no assumption that the notch is narrow, no expansion about $\omega_0$. Most
textbooks reach this by writing $X \approx 2L\,\Delta\omega$ near resonance, which is a
first-order approximation and is only good for high $Q$. The exact route was no longer
and it gives an answer you can trust at $Q = 0.6$, which is where the notch in this
module's own reading unit sits.

The product of the two roots is $\dfrac{(RC + S)(-RC + S)}{4L^2C^2} = \dfrac{S^2 - R^2C^2}{4L^2C^2} = \dfrac{4LC}{4L^2C^2} = \dfrac{1}{LC} = \omega_0^2$.
So $\sqrt{\omega_{lo}\,\omega_{hi}} = \omega_0$ exactly: the notch is centred on its
resonance *geometrically*. Its edges are equally spaced from $f_0$ in ratio, never in
hertz, which is why a swept response looks symmetric on a logarithmic axis and lopsided
on a linear one.

And $Q = \frac{1}{R}\sqrt{L/C}$ is the series expression, not the parallel one, even
though this circuit's $R$ is a shunt-feeding resistor rather than something inside the
branch. The reason is that from the resonating branch's point of view, $R$ *is* in
series with it: the current that resonates leaves the branch, goes up through $R$ to the
source, and comes back. Ask which loop the resonant current takes and every $Q$ formula
in this course tells you which way up it goes.
'''
            },
        },

        # ---- M9 -----------------------------------------------------------
        {
            "title": "Real power, reactive power and the power factor",
            "summary": "Volts times amps stopped being watts the moment the current stopped peaking with the voltage. Three quantities now, and only one of them does work.",
            "concepts": [
                "Instantaneous power is $p(t) = v(t)\\,i(t)$, always. For a sinusoidal voltage and a current lagging it by $\\phi$, the average of that product over a cycle is $P = V_{rms} I_{rms} \\cos\\phi$ watts. The factor $\\cos\\phi$ is the **power factor**, and it is 1 for a resistor and 0 for a perfect reactance.",
                "Three quantities, three units, deliberately different so that nobody confuses them. **Apparent power** $S = V_{rms} I_{rms}$ in volt-amperes is what the cable and the transformer must be sized for. **Real power** $P = S\\cos\\phi$ in watts is what the meter bills and what actually does work. **Reactive power** $Q = S\\sin\\phi$ in VAR is the part that flows in and back out each cycle and does none.",
                "They form a right triangle, $S^2 = P^2 + Q^2$. Nothing is destroyed in the reactive part — it is carried twice down the same wire and paid for once, and it still heats that wire on the way.",
                "A motor is a resistance in series with an inductance, so its current lags and its power factor is well under one. Putting a capacitor **in parallel** with it lets the capacitor and the inductor exchange their reactive energy locally instead of dragging it back and forth to the supply. The supply current falls, the cable runs cooler, and the real power the motor consumes is completely unchanged. That is **power factor correction**.",
                "The correction is exact at one frequency only. The capacitor's susceptance $\\omega C$ rises with frequency while the inductor's $1/(\\omega L)$ falls, so a network corrected at 50 Hz is capacitive above it and inductive below.",
            ],
            "read": [
                {
                    "title": "Volts times amps, and where the watts went",
                    "minutes": 15,
                    "body": r'''
## The one definition that never stops being true

A wattmeter has two pairs of terminals. One pair goes across the load and watches the
voltage; the other goes in series with it and watches the current. Inside, the instrument
does exactly one thing: it multiplies the two, instant by instant, and averages the
product. That is the whole of power measurement, and it is worth fixing in mind before
any formula arrives, because every formula in this module is a special case of it and
none of them replaces it.

$$p(t) = v(t)\,i(t)$$

Power is a rate, and it is instantaneous. At the moment the voltage across a lamp is
200 V and the current through it is 4 A, that lamp is converting 800 joules every second,
and if either number changes a microsecond later then so does the rate. What anyone
actually wants, though, is not $p$ at an instant but its average over a cycle, because
that average is what heats the filament, turns the shaft, and runs up the meter. Give it
a name — **real power**, symbol $P$, unit the watt — and the job of this module is to
compute it without integrating anything.

In EE101 there was nothing to compute. A steady 9 V driving a steady 3 mA is 27 mW, now
and at teatime, and $P = VI$ was a definition rather than an average. The moment both
factors start moving, the product starts moving too, and it moves in a way that is not
obvious.

## Start with the case that behaves

Put $v(t) = V_p\sin\omega t$ across a resistor. Ohm's law holds at every instant, so the
current is $i(t) = (V_p/R)\sin\omega t$ — the same shape, in step, no shift. Multiply:

$$p(t) = \frac{V_p^2}{R}\sin^2\omega t
       = \frac{V_p^2}{2R}\bigl(1 - \cos 2\omega t\bigr)$$

using $\sin^2\theta = \tfrac12(1-\cos 2\theta)$. Three things are worth reading off that
line, and the third is the one people miss.

It is never negative. $\sin^2$ cannot be, so a resistor takes energy from the source
during every part of every cycle and gives none of it back. Energy goes in one direction
only, which is exactly what "dissipation" means.

It pulsates, at **twice** the supply frequency. The power goes to zero when the voltage
does, at both zero crossings, and peaks at both crests. A 1 kW element on a 50 Hz supply
is not delivering a steady kilowatt; it is delivering 2 kW a hundred times a second and
nothing in between. That is why transformers and motors hum at 100 Hz on a 50 Hz supply
rather than at 50 Hz — the magnetic forces inside them follow $B^2$, and a square averages
the sign away — and why a neon indicator waved about in a dark room draws a dotted line
rather than a continuous one.

Its average is $V_p^2/2R$, because the cosine averages to zero over a whole cycle. That
average is the entire reason RMS was defined the way it was in Module 1: writing
$V_{rms} = V_p/\sqrt{2}$ turns $V_p^2/2R$ into $V_{rms}^2/R$, the same expression direct
current uses.

```
a 1 kW heater on 230 V rms
R         = 230^2 / 1000                       = 52.9 ohm
V_p       = 230 * sqrt(2)                      = 325.27 V
I_p       = 325.27 / 52.9                      = 6.1488 A
p_peak    = V_p * I_p                          = 2000.0 W
p_avg     = 230^2 / 52.9                       = 1000.0 W
```

Zero to two kilowatts, a hundred times a second, averaging one. The element's thermal
mass does the smoothing, and nobody notices.

## Now let the current arrive late

Everything above rested on the current being in step with the voltage. Put an inductance
in the circuit and it is not. Keep the voltage as the reference and write the current as
lagging it by an angle $\phi$:

$$v(t) = V_p\sin\omega t, \qquad i(t) = I_p\sin(\omega t - \phi)$$

Multiply, and use $\sin A\sin B = \tfrac12[\cos(A-B) - \cos(A+B)]$ with $A = \omega t$ and
$B = \omega t - \phi$:

$$p(t) = \frac{V_p I_p}{2}\bigl[\cos\phi - \cos(2\omega t - \phi)\bigr]
       = V_{rms}I_{rms}\bigl[\cos\phi - \cos(2\omega t - \phi)\bigr]$$

Nothing has been approximated and no small angle assumed. The instantaneous power is a
constant plus a sinusoid at twice the frequency, and the two parts have completely
different jobs.

The constant is $V_{rms}I_{rms}\cos\phi$. It does not average away, so it *is* the
average. That is the real power:

$$P = V_{rms}I_{rms}\cos\phi$$

The oscillating part has amplitude $V_{rms}I_{rms}$ — notice, with no $\cos\phi$ in it —
and averages to exactly zero over a cycle. It contributes nothing to $P$ and never will.

The interesting consequence is what happens when the constant term is smaller than the
oscillation, which is whenever $\cos\phi < 1$: the bracket goes negative for part of every
cycle, and negative $p$ means energy flowing *out of the load and back into the supply*.
At $\phi = 90°$ the constant term vanishes altogether and $p(t)$ is a pure double-frequency
sinusoid, equally positive and negative — a perfect reactance takes energy in for a
quarter cycle and hands every joule back in the next.

## Three quantities, three units, on purpose

Once $\cos\phi$ is loose in the world, the product of the two meter readings stops being
the watts and needs its own name.

**Apparent power** $S = V_{rms}I_{rms}$, in **volt-amperes**. This is what the cable, the
switchgear and the transformer must be sized for, because none of them cares about timing:
the current that flows is the current that heats them.

**Real power** $P = S\cos\phi$, in **watts**. The average of $vi$; the part that turns into
heat, torque or light; the number on the energy bill.

**Reactive power** $Q = S\sin\phi$, in **volt-amperes reactive**, VAR. To see what it is
the amplitude *of*, expand the cosine in $p(t)$ and sort the terms:

$$p(t) = P\bigl(1 - \cos 2\omega t\bigr) - Q\sin 2\omega t$$

The first term is a pulsation that is never negative and averages to $P$ — that is the
resistor's behaviour from earlier, unchanged. The second is a pure oscillation, as positive
as it is negative, averaging to exactly zero, and $Q$ is its amplitude. Energy borrowed each
cycle and returned each cycle. It is not a loss and it is not "wasted power"; nothing is
destroyed by it. But the current that carries it is completely real, and it heats every
metre of wire it passes through on both journeys.

$\cos\phi$ has its own name too: the **power factor**, the fraction of the volt-amperes
that turn out to be watts. It is 1 for a resistor, 0 for an ideal reactance, and something
between for everything else. Because $P = S\cos\phi$ and $Q = S\sin\phi$,

$$S^2 = P^2 + Q^2$$

which is the **power triangle**: $P$ along the bottom, $Q$ up the side, $S$ the hypotenuse,
$\phi$ the angle at the origin. It is Pythagoras because sine and cosine are, not because
anything is being added at right angles in the physical world.

### Worked, from two meter readings

A load on a 230 V RMS supply draws 10 A RMS at a power factor of 0.8, lagging.

```
phi       = arccos(0.8)                        = 36.870 deg
S         = 230 * 10                           = 2300 VA
P         = 2300 * 0.8                         = 1840 W
Q         = 2300 * sin(36.870 deg) = 2300*0.6  = 1380 VAR
check     sqrt(1840^2 + 1380^2)
          = sqrt(3385600 + 1904400)            = 2300 VA
```

Now put those into $p(t) = 2300[\,0.8 - \cos(2\omega t - \phi)\,]$ and watch it move. The
bracket runs between $0.8-1$ and $0.8+1$, so

```
p_min     = 2300 * (-0.2)                      = -460 W
p_max     = 2300 * (1.8)                       = +4140 W
p_avg                                          = 1840 W
```

The load hands 460 W back to the generator at the worst moment, and it is doing so for
20.5% of the time — the bracket is negative whenever $\cos(2\omega t - \phi)$ exceeds 0.8,
which is $2\times 36.87°$ out of every $360°$ of the doubled angle. Meanwhile the meter,
which averages, reads a placid 1840 W.

### Worked, from a circuit

Take the load apart: 40 Ω in series with 100 mH, on the same 230 V, 50 Hz supply. This is
the first model anyone writes down for a small motor — the resistance of the windings and
the inductance of the magnetic circuit.

```
w         = 2*pi*50                            = 314.159 rad/s
X_L       = w * L = 314.159 * 0.1              = 31.4159 ohm
|Z|       = sqrt(40^2 + 31.4159^2)
          = sqrt(1600 + 986.960)               = 50.8622 ohm
phi       = atan(31.4159/40) = atan(0.785398)  = 38.146 deg
I         = 230 / 50.8622                      = 4.52202 A rms
```

The current is one number and it flows through both components, so take the powers one
component at a time:

```
P         = I^2 * R = 20.4487 * 40             = 817.95 W
Q         = I^2 * X_L = 20.4487 * 31.4159      = 642.42 VAR
S         = 230 * 4.52202                      = 1040.07 VA
check     sqrt(817.95^2 + 642.42^2)            = 1040.07 VA
pf        = 817.95 / 1040.07                   = 0.7864
          = cos(38.146 deg) = 40/50.8622       = 0.7864
```

Every route to the power factor agrees, and they must: $\cos\phi$, $R/|Z|$ and $P/S$ are
three spellings of one ratio. Note the shape of the arithmetic — the resistance took all
the watts and the reactance took all the VAR, with no cross terms. That is general for a
series pair and it is the quickest hand check there is.

## The mistake, and why it is tempting

Multiplying the voltmeter reading by the ammeter reading and calling the result watts.
Here it gives 1040 W for a load that dissipates 818 W — a 27% overstatement that no amount
of care with the instruments will remove.

It is tempting because it is *true* in the two places most people learned it. It is true
for direct current, where there is no phase to have. It is true for any resistor at any
frequency, because $\phi = 0$ there. And volts times amps has the right units, which is
the sort of thing that stops people looking further. The volt-ampere exists as a separate
unit precisely so the error announces itself: a figure quoted in VA is a warning that
nobody has yet asked when the current peaks.

The second mistake is subtler and costs more. Two loads on one supply do **not** have
their apparent powers added. Watts add to watts and VAR add to VAR, because $P$ and $Q$ are
the two rectangular components of one quantity — $S = P + jQ$, and components add. But
$S$ itself is a *magnitude*, and magnitudes only add when they point the same way. Put the
1 kW heater from earlier in parallel with the motor above:

```
P_total   = 1000 + 817.95                      = 1817.95 W
Q_total   = 0 + 642.42                         = 642.42 VAR
S_total   = sqrt(1817.95^2 + 642.42^2)         = 1928.12 VA
I_total   = 1928.12 / 230                      = 8.3831 A rms
```

Adding the apparent powers gives $1000 + 1040.07 = 2040$ VA, and adding the currents gives
$4.348 + 4.522 = 8.870$ A. Both are about 5.8% too big, and both would have you buy a
larger cable than the installation needs.

## Where this stops holding

Everything above assumed one sinusoid. If the current is not a sinusoid, the derivation
that produced $\cos\phi$ has nothing to stand on, and $\cos\phi$ is no longer the power
factor.

The definitions that survive are the honest ones: $P$ is still the average of $vi$, and
$S$ is still $V_{rms}I_{rms}$ with both measured properly. Their ratio $P/S$ is still the
power factor, and it is still the number that says how much copper you are paying for. But
it is no longer a cosine of anything.

Take a rectifier that draws a square-wave current, in phase with the voltage — the
idealised behaviour of a full bridge feeding a large smoothing inductor. There is no
phase shift anywhere. Feed it from 230 V RMS and let the square wave be 10 A tall:

```
V_rms     = 230                                (sinusoid)
I_rms     = 10                                 (square wave: rms = peak)
S         = 230 * 10                           = 2300 VA
P         = avg of v*i = V_p*I_p * (2/pi)
          = 325.27 * 10 * 0.63662              = 2070.7 W
pf        = 2070.7 / 2300 = 2*sqrt(2)/pi       = 0.9003
```

A power factor of 0.900 with a phase shift of exactly zero. The missing 10% is
**distortion**: the current contains harmonics that the voltage has nothing to pair with,
so they carry current without carrying power. The triangle becomes
$S^2 = P^2 + Q^2 + D^2$, with $D$ the distortion term, and no capacitor can cancel a $D$ —
correction across such a load does nothing at all, which surprises people who have only
met the sinusoidal case.

Two smaller limits, worth knowing before you meet them. Three-phase changes the
bookkeeping: the three phases' pulsations are 120° apart and cancel, so the total
instantaneous power of a balanced three-phase load is genuinely constant, and the familiar
$P = \sqrt{3}\,V_L I_L\cos\phi$ carries a $\sqrt3$ that comes from line-to-line versus
line-to-neutral voltages, not from any new physics. And the sign of $Q$ is a convention: a
lagging (inductive) load is taken as absorbing positive VAR, which makes a capacitor a
*source* of them. That convention is what the next reading is built on.
''',
                },
                {
                    "title": "Making the current smaller without doing less work",
                    "minutes": 14,
                    "body": r'''
## What the supply is complaining about

The motor in the last section did 818 W of work and drew 4.522 A to do it. A resistor
doing the same 818 W on the same 230 V would have drawn $818/230 = 3.556$ A.

Resolve the motor's current into two pieces, one in step with the voltage and one a
quarter cycle behind it:

```
I cos(phi) = 4.5220 * 0.78644                  = 3.5563 A rms
I sin(phi) = 4.5220 * 0.61766                  = 2.7930 A rms
```

The first is the part that does the work, and it is exactly the 3.556 A the resistor
drew — it has to be, since both deliver the same 818 W at the same 230 V. The second does
none. It goes down the cable, into the motor's magnetic field, back out of the magnetic
field, and back up the cable, twice per cycle, for ever. The two are a quarter cycle
apart, so the total is $\sqrt{3.5563^2 + 2.7930^2} = 4.5220$ A and not the 6.35 A they
would come to if they were ever in the wire at the same instant.

Nobody at the load end minds much. The motor gets its 818 W and turns. The complaint comes
from everything between the generator and the load, because all of that was sized on
current:

- the cable heats as $I^2R$, and $I$ is the whole 4.522 A, not the 3.556 A that does work;
- the transformer is rated in volt-amperes rather than watts, because its windings heat on
  the current through them regardless of what that current is doing at the far end;
- the switchgear, the fuse and the meter are all rated in amps.

At 4.522 A instead of 3.556 A the cable dissipates $(4.522/3.556)^2 = 1.617$ times as much
— 62% more heat in the copper for exactly the same work delivered. That is the entire
economic case, and it is why large consumers are billed on kVA, or surcharged for a power
factor below about 0.95, while a domestic meter that only counts kWh ignores the whole
question.

## The idea: keep the sloshing local

The reactive current exists because the inductor's magnetic field has to be built up and
torn down a hundred times a second, and the energy for that is currently being fetched
from the generator each time. But the energy does not care where it comes from. If
something *next to the motor* could hold that energy and hand it over on demand, the
current in the long cable would never carry it.

A capacitor is that something, and the reason it works is a matter of timing. A capacitor
stores energy in an electric field, which is largest when its **voltage** is largest. An
inductor stores energy in a magnetic field, which is largest when its **current** is
largest. In an AC circuit those two moments are a quarter cycle apart — and they are apart
in the right direction. When the inductor wants energy, the capacitor is at the point in
its cycle where it has energy to give; a quarter cycle later, when the inductor's field
collapses, the capacitor is ready to take it back.

Formally, in the language of Module 3: a capacitor's susceptance is $+\omega C$ and an
inductor's is $-1/(\omega L)$. Opposite signs, so they can cancel. Physically: the two
components pass energy back and forth between themselves and the supply never learns it is
happening.

That picture makes a prediction worth checking, because if it is right the two stores must
be the same size. Take the corrected motor worked below. Its own branch current is
unchanged by the correction — still 4.522 A RMS through the 100 mH — and the capacitor is
38.655 µF across the full 230 V RMS. How many joules is each one holding at its own worst
moment?

```
I_p       = 4.52202 * sqrt(2)                  = 6.3951 A
W_L       = 0.5 * L * I_p^2 = 0.5*0.1*40.897   = 2.0449 J
V_p       = 230 * sqrt(2)                      = 325.27 V
W_C       = 0.5 * C * V_p^2
          = 0.5 * 3.8655e-5 * 105800           = 2.0449 J
```

The same 2.04 joules, and not by luck: substituting $C = L/(R^2+\omega^2L^2)$ and
$I_{rms}^2 = V^2/(R^2+\omega^2L^2)$ turns both expressions into $L I_{rms}^2$ exactly. The
capacitor is sized to hold precisely what the coil needs, and the pair shuttles those two
joules between them a hundred times a second while the supply carries none of it.

## Why it goes in parallel, and what happens if you forget

Across the load, not in line with it. The reason is simple and it is about what the load is
allowed to notice.

A capacitor in **parallel** shares the load's terminals. The voltage across the motor is
unchanged, so the current through the motor is unchanged, so its torque, speed, losses and
818 W are all exactly what they were. Nothing about the motor is altered. All that changes
is where its reactive current is sourced from: the capacitor a metre away rather than the
generator a kilometre away. The supply current is the *sum* of two branch currents that
partly cancel, and the sum is smaller than either would suggest.

A capacitor in **series** is a different circuit entirely. It cancels reactance in the
loop, which does drive the phase angle to zero, but it does so by changing the current and
the voltage the motor sees. The size needed is the one that makes $1/\omega C = \omega L$:

```
C_series  = 1/(w^2 L) = 1/(314.159^2 * 0.1)    = 101.32 uF
```

and the result is series resonance at the supply frequency. The loop impedance collapses
from 50.86 Ω to the bare 40 Ω:

```
I         = 230/40                             = 5.750 A rms
P         = 5.75^2 * 40                        = 1322.5 W
V_L       = 5.75 * 31.4159                     = 180.6 V across the coil
V_C                                            = 180.6 V across the capacitor
```

The current went *up*, not down, and the motor is now taking 1322 W instead of 818 W and
will overheat. The 181 V across the coil and the 181 V across the capacitor stay below the
supply here only because this load's $X_L/R$ is less than one; wind the coil a little
larger and those two voltages climb past 230 V, which is the series-resonance voltage
magnification of Module 7 arriving uninvited. None of this is a subtle failure mode. If a
correction capacitor is ever in series with the load, something has been wired wrong.

## Sizing it, two ways that must agree

**From the power triangle.** The load draws $Q_L$ VAR of lagging reactive power. A
capacitor across the same voltage supplies leading VAR, in the amount

$$Q_C = \frac{V^2}{X_C} = \omega C V^2$$

so setting $Q_C = Q_L$ and solving for $C$ gives $C = Q_L/(\omega V^2)$.

**From the admittance.** Everything in parallel adds its admittance, so write the motor's
and demand that the total be real. That is the derivation in this module, and it lands on

$$C = \frac{L}{R^2 + \omega^2 L^2}$$

The two are the same statement. $Q_L = I^2\omega L$ and $I = V/\sqrt{R^2+\omega^2L^2}$, so
$Q_L/(\omega V^2) = L/(R^2+\omega^2L^2)$ identically — no approximation, no special case.
Use whichever set of numbers you have: a nameplate gives you $P$ and the power factor, a
model gives you $R$ and $L$.

### Worked: the motor, corrected to unity

```
Q_L       = 642.42 VAR         (from the previous reading)
C         = 642.42 / (314.159 * 230^2)
          = 642.42 / 16619027                  = 3.8655e-5 F = 38.655 uF
cross-check
C         = L/(R^2 + w^2L^2) = 0.1/2586.96     = 3.8655e-5 F
```

What the supply now sees is a pure resistance, and it is not $R$:

```
R_eq      = (R^2 + w^2 L^2)/R = 2586.96/40     = 64.674 ohm
I_new     = 230 / 64.674                       = 3.5563 A rms
P         = 230 * 3.5563                       = 817.95 W   (unchanged)
```

The current fell by 21.4%, from 4.522 A to 3.556 A. The heat in the cable fell by
$1 - (3.556/4.522)^2 = 38.2\%$. And the work done fell by nothing at all, which is the
whole point: $P$ is identical to the last decimal place, because the motor's terminal
voltage never moved and neither did its current.

Notice also that $R_{eq} = 64.674\ \Omega$ is *larger* than the 40 Ω winding resistance.
That is not a mistake. The corrected load draws less current at the same voltage, so it
must look like a bigger resistance, even though the resistance that turns energy into heat
is still 40 Ω sitting where it always was.

### Worked: corrected to 0.95, which is what actually gets installed

Utilities generally ask for 0.95, not 1.0, and the reason is in the arithmetic. To move
from $\phi_1$ to $\phi_2$ at constant $P$:

$$Q_C = P\bigl(\tan\phi_1 - \tan\phi_2\bigr)$$

```
tan(phi_1) = X_L/R = 31.4159/40                = 0.78540
phi_2      = arccos(0.95)                      = 18.195 deg
tan(phi_2)                                     = 0.32868
Q_C        = 817.95 * (0.78540 - 0.32868)
           = 817.95 * 0.45672                  = 373.57 VAR
C          = 373.57/(314.159 * 52900)          = 2.2478e-5 F = 22.48 uF
```

and the load that results:

```
Q_left    = 642.42 - 373.57                    = 268.85 VAR
S         = sqrt(817.95^2 + 268.85^2)          = 861.00 VA
I         = 861.00/230                         = 3.7435 A rms
pf        = 817.95/861.00                      = 0.9500
```

22.5 µF buys the trip from 0.786 to 0.950 and takes 0.779 A off the cable. The remaining
16.2 µF — nearly as much again — buys the trip from 0.950 to 1.000 and takes off a further
0.187 A. The last stretch costs the most and returns the least, which is what a triangle
whose height is shrinking towards zero always does, and it is why the standard stops short
of unity.

## The mistake, and why it is tempting

That correcting the power factor saves the load energy. It does not. $P$ is unchanged, by
construction, and a domestic kWh meter measures $P$ — fit a capacitor to your fridge and
the bill does not move by a penny. What falls is the current, and therefore the losses in
*somebody else's* copper, plus the kVA capacity you are renting.

The phrasing is what does it: "improving the power factor" sounds like improving an
efficiency, and the word "reactive power" sounds like power going somewhere and being lost.
Neither survives contact with the definitions. An ideal reactance dissipates exactly zero.
The only real loss anywhere in this story is $I^2R$ in the wires, and correction attacks it
by shrinking $I$, never by making the load frugal.

The second mistake is over-correction — fitting more capacitance because if some is good,
more must be better. The supply current as a function of $C$ is a V, not a slope: it falls
to a minimum at the correcting value and climbs again beyond it, symmetrically. Exactly
double the correct capacitance puts you precisely back where you started:

```
C = 38.655 uF  ->  I = 3.5563 A,  pf = 1.000
C = 77.311 uF  ->  I = 4.5220 A,  pf = 0.786 leading
```

The same current and the same power factor as the uncorrected motor, with the current now
*leading* instead of lagging, and a room full of capacitors to show for it.

## Where this stops holding

**At any other frequency.** The cancellation is a coincidence arranged at one $\omega$, and
the two susceptances move in opposite directions: $\omega C$ rises with frequency,
$1/(\omega L)$ falls. The same corrected motor, if the supply were 60 Hz or if you asked
about the third harmonic:

```
f = 50 Hz    pf = 1.000
f = 60 Hz    pf = 0.988   (capacitive)
f = 150 Hz   pf = 0.138   (strongly capacitive)
```

**And that turns into a hazard rather than a curiosity.** A correction capacitor sits in parallel
with the supply's own leakage inductance, and a capacitor in parallel with an inductance is
the tank of Module 8. If that parallel resonance lands near a harmonic the installation
actually produces — the 5th at 250 Hz and the 7th at 350 Hz are the usual suspects — the
harmonic current is amplified rather than absorbed, and capacitors fail. The standard fix
is a small series reactor that detunes the tank below the 5th harmonic, which is why
industrial correction is sold as capacitor-plus-choke rather than as a bare capacitor.

**When the load is not linear.** As the previous reading showed, a rectifier can have a
power factor of 0.9 with no phase shift at all. The deficit there is distortion, there is
no lagging current to cancel, and a capacitor across it achieves nothing while still
drawing its own leading current. Correction assumes the load's current is a sinusoid at the
supply frequency. Check that before sizing anything.

**When the load changes.** A motor's reactive demand is dominated by its magnetising
current, which is roughly constant, but its $P$ varies enormously with mechanical load, so
a capacitor sized at full load over-corrects at no load. And an induction motor switched off
with capacitors still connected can self-excite from them and keep generating for some
seconds after it is disconnected — the terminals stay live, and re-closing onto them out of
phase is destructive. That is why individually-corrected motors have their capacitance
capped below the machine's own magnetising VAR.

**And the model itself.** Series $R$ and $L$ is one line of a much longer story about
what a motor is. It is enough to size a capacitor and it is not enough to predict a
starting current.
''',
                },
            ],
            "quiz": {
                "title": "Watts, volt-amperes and VAR",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A load draws 10 A RMS from a 230 V RMS supply at a power factor of 0.8. What real power does it consume?",
                        "opts": ["2300 W", "1840 W", "1380 W", "184 W"],
                        "a": 1,
                        "why": r'''
$P = V_{rms} I_{rms} \cos\phi = 230 \times 10 \times 0.8 = 1840$ W. The 2300 figure is
the *apparent* power in volt-amperes — the product of the two readings with no regard
for when each one peaks — and it is the number the wiring has to survive rather than
the number the load turns into work. Quoting it in watts is the single most common
error in this subject, which is why volt-amperes has its own name.
''',
                    },
                    {
                        "q": "For that same load, what apparent power must the supply and its cabling be rated for?",
                        "opts": ["1840 VA", "2300 VA", "2875 VA", "460 VA"],
                        "a": 1,
                        "why": r'''
$S = V_{rms} I_{rms} = 2300$ VA. The cable does not care about phase: 10 A flows in it
and heats it as $I^2R$ whatever those amps are doing at the far end. That is the whole
economic argument for correcting a power factor — a poor one makes you buy and cool
more copper for the same delivered work. Dividing by the power factor instead of
multiplying gives 2875 VA, which has the relationship upside down.
''',
                    },
                    {
                        "q": "Reactive power is measured in VAR. What is it?",
                        "opts": [
                            "Power lost as heat in the reactance",
                            "Energy that flows into the load and back out again each cycle, doing no net work",
                            "The power delivered to the load's resistance",
                            "An artefact of the measurement, with no physical meaning",
                        ],
                        "a": 1,
                        "why": r'''
It is energy borrowed and returned. During part of each cycle the inductor's magnetic
field is being built up out of energy from the supply; during another part that field
collapses and gives the energy back. Averaged over the cycle it is exactly zero work,
which is why it is not measured in watts. An ideal reactance dissipates nothing at all
— only resistance turns energy into heat — but the current carrying that borrowed
energy is entirely real and heats every wire it passes through.
''',
                    },
                    {
                        "q": "A capacitor is connected in parallel with an inductive load to correct its power factor. What happens to the real power the load consumes?",
                        "opts": [
                            "It rises in proportion to the improvement",
                            "It falls",
                            "It is unchanged — what falls is the current drawn from the supply",
                            "It falls to zero",
                        ],
                        "a": 2,
                        "why": r'''
Unchanged. The load still sees the same voltage across it and still does the same job;
nothing about the motor has been altered. What changes is where the reactive current
comes from — the capacitor next to it rather than the generator down the road — so the
current in the supply cable falls and the losses in that cable fall with it. A
correction that reduced the real power would be reducing the work being done, which is
the opposite of the intention.
''',
                    },
                    {
                        "q": "A load is corrected to a power factor of exactly 1 at 50 Hz. What is its power factor at 150 Hz?",
                        "opts": [
                            "Still 1 — correction is a property of the load, not of the frequency",
                            "Not 1 — the capacitor's susceptance triples while the inductor's falls to a third, so the cancellation only holds where it was designed",
                            "0.8, because the correction was designed for 0.8",
                            "0 — the capacitor is a short circuit at any higher frequency",
                        ],
                        "a": 1,
                        "why": r'''
The two susceptances move in opposite directions with frequency, so they can only be
made equal at one point. At three times the design frequency the capacitor's $\omega C$
is three times larger and the inductor's $1/(\omega L)$ is three times smaller, and the
network is strongly capacitive. This is not a defect — supplies run at one frequency —
but it is why a correction capacitor cannot be specified without naming the frequency,
and why harmonics on a supply complicate the whole business.
''',
                    },
                    {
                        "q": "An ideal capacitor has 230 V RMS across it and draws 2 A RMS. How much real power does it consume?",
                        "opts": ["460 W", "0 W", "325 W", "230 W"],
                        "a": 1,
                        "why": r'''
None. Its current leads its voltage by exactly 90°, so $\cos\phi = 0$ and
$P = 230 \times 2 \times 0 = 0$ W. It draws 460 VA of apparent power, all of it
reactive: 460 VAR. The 460 W answer is the trap the units exist to prevent — volts
times amps is watts only when the two peak together. A real capacitor does dissipate a
little, and that little is modelled by adding a small resistance beside it, never by
pretending the reactance is one.
''',
                    },
                ],
            },
            "blanks": [
                {
                    "title": "One motor, three powers",
                    "minutes": 10,
                    "lang": "text",
                    "caption": "From two components and a supply to the full power triangle, one line at a time.",
                    "brief": r'''
The load is the usual first model of a small motor: 40 Ω of winding resistance in series
with 100 mH of inductance, across a 230 V RMS, 50 Hz supply.

Series, so there is one current and it flows through both components. Work that out first
and every power below is a multiplication.
''',
                    "listing": r'''
R = 40 ohm  in series with  L = 100 mH,  on 230 V rms at 50 Hz


    omega = 2*pi*50                       =  314.16 rad/s

    X_L   = omega * L                     =  ___ ohm

    |Z|   = ___                           =  50.862 ohm

    I     = 230 / 50.862                  =  ___ A rms

    P     = I^2 * R                       =  ___ W

    Q     = I^2 * ___                     =  642.42 VAR

    S     = 230 * 4.5220                  =  ___ VA

    pf    = P / S                         =  ___

    and the current ___ the voltage
''',
                    "blanks": [
                        {
                            "prompt": "The inductor's reactance at 50 Hz",
                            "hole": "xl",
                            "opts": ["31.416", "5.000", "0.031831", "62.832"],
                            "a": 0,
                            "why": r'''
$X_L = \omega L = 314.16 \times 0.1 = 31.416$ Ω. Multiply by $\omega$, not by $f$: 5.000 is
$fL$, the version of this calculation with the $2\pi$ dropped, and it is the single most
common slip in the whole course. 0.031831 is $1/(\omega L)$, which is the susceptance in
siemens and belongs to the parallel case. 62.832 is $2\omega L$.
''',
                        },
                        {
                            "prompt": "How the resistance and the reactance combine",
                            "hole": "zexpr",
                            "opts": ["sqrt(R^2 + X_L^2)", "R + X_L", "sqrt(R^2 - X_L^2)", "R * X_L / (R + X_L)"],
                            "a": 0,
                            "why": r'''
$|Z| = \sqrt{R^2 + X_L^2} = \sqrt{1600 + 986.96} = \sqrt{2586.96} = 50.862$ Ω. Adding them
gives 71.4 Ω, which is what you would get if the resistor's voltage and the coil's voltage
peaked at the same moment — they do not, they are a quarter cycle apart, and the sum of two
quarter-cycle-apart sinusoids is found by Pythagoras. Subtracting under the root is what
you would do to a reactance of the *opposite* sign, and there is only one reactance here.
The product-over-sum form is for two resistances in parallel and has nothing to do with
this circuit.
''',
                        },
                        {
                            "prompt": "The RMS current",
                            "hole": "i",
                            "opts": ["4.5220", "5.7500", "6.3951", "7.3212"],
                            "a": 0,
                            "why": r'''
$I = V/|Z| = 230/50.862 = 4.5220$ A RMS. 5.7500 is $230/R$, the current if the inductance
were not there — always larger, because adding a reactance can only increase $|Z|$.
6.3951 is the *peak* current, $\sqrt2$ times the answer, and mixing peak into a chain of
RMS calculations corrupts every power below it. 7.3212 is $230/31.416$, the current if the
resistance were not there.
''',
                        },
                        {
                            "prompt": "The real power",
                            "hole": "p",
                            "opts": ["817.95", "1040.07", "642.42", "1322.50"],
                            "a": 0,
                            "why": r'''
$P = I^2 R = 20.4487 \times 40 = 817.95$ W. Only the resistance dissipates, so only $R$
appears here — the reactance is not in this line at all. 1040.07 is the apparent power in
volt-amperes, $V I$ with no regard for phase, and quoting it in watts overstates the load's
consumption by 27%. 642.42 is the reactive power. 1322.50 is $230^2/40$, which uses the
supply voltage rather than the resistor's own 180.88 V and so pretends the coil drops
nothing.
''',
                        },
                        {
                            "prompt": "What multiplies $I^2$ to give the reactive power",
                            "hole": "qterm",
                            "opts": ["X_L", "R", "|Z|", "R + X_L"],
                            "a": 0,
                            "why": r'''
$Q = I^2 X_L = 20.4487 \times 31.416 = 642.42$ VAR. The pattern is worth keeping: in a
series pair the same current flows in both parts, the resistance takes all the watts and
the reactance takes all the VAR, with no cross terms anywhere. Using $R$ would just repeat
$P$; using $|Z|$ gives $I^2|Z| = S$, the hypotenuse rather than a side; and $R + X_L$ is the
addition that Pythagoras already ruled out two lines above.
''',
                        },
                        {
                            "prompt": "The apparent power",
                            "hole": "s",
                            "opts": ["1040.07", "817.95", "1460.37", "1470.88"],
                            "a": 0,
                            "why": r'''
$S = V_{rms}I_{rms} = 230 \times 4.5220 = 1040.07$ VA, and the triangle closes:
$\sqrt{817.95^2 + 642.42^2} = 1040.07$. This is the number the cable and the transformer
are sized on, because the current that flows is the current that heats them whatever it is
doing at the far end. 817.95 is the real power, which is smaller; 1460.37 is $P + Q$ added
arithmetically, and $P$ and $Q$ never add that way; 1470.88 pairs the peak voltage with the
RMS current, and a volt-ampere is a product of two RMS values.
''',
                        },
                        {
                            "prompt": "The power factor",
                            "hole": "pf",
                            "opts": ["0.7864", "1.2715", "0.6177", "0.3932"],
                            "a": 0,
                            "why": r'''
$P/S = 817.95/1040.07 = 0.7864$, and every other route agrees: $\cos 38.146° = 0.7864$ and
$R/|Z| = 40/50.862 = 0.7864$. A power factor is a fraction of the volt-amperes that turned
out to be watts, so it can never exceed 1 — 1.2715 is $S/P$, the ratio upside down, and its
being greater than one is the signal. 0.6177 is $Q/S = \sin\phi$, sometimes called the
reactive factor and never the power factor. 0.3932 is half the right answer, and halving a
cosine is not the same as halving the angle inside it.
''',
                        },
                        {
                            "prompt": "The timing of the current relative to the voltage",
                            "hole": "sense",
                            "opts": ["lags", "leads", "is in phase with"],
                            "a": 0,
                            "why": r'''
It lags. An inductor opposes a change in its current, so the current is always behind: in a
series $R$–$L$ the current reaches its crest $\phi = 38.1°$ of a cycle — about 2.1 ms at
50 Hz — after the voltage does. A leading current is what a capacitive load gives, and
in-phase is the resistor-only case, $\phi = 0$, which would have made the power factor 1 and
this entire module unnecessary. Which way round it goes matters for what you do next: a
lagging load is corrected with a capacitor, and a leading one would need the opposite.
''',
                        },
                    ],
                },
                {
                    "title": "Sizing the capacitor that corrects it",
                    "minutes": 9,
                    "lang": "text",
                    "caption": "The same motor again, and the seven lines that turn its reactive power into a capacitance.",
                    "brief": r'''
Same motor: 40 Ω and 100 mH on 230 V RMS at 50 Hz, drawing 817.95 W and 642.42 VAR. The
job is a capacitance, in parallel, that leaves the watts alone and cancels the VAR at
50 Hz.

Two routes are laid out here and they must land on the same number, which is the point of
doing both.
''',
                    "listing": r'''
correcting the motor to unity power factor at 50 Hz


    reactive power to be cancelled      Q_C  =  ___ VAR

    the capacitor sits across           V    =  ___ V rms

    Q_C = omega * C * V^2   so   C = Q_C / ___

    C   = 642.42 / (314.16 * 52900)          =  ___ uF

    check: C = L/(R^2 + omega^2 L^2) = 0.1 / ___   = 38.655 uF

    the supply current becomes    I = P / V  =  ___ A rms

    and the real power the motor draws        =  ___
''',
                    "blanks": [
                        {
                            "prompt": "How much reactive power the capacitor has to supply",
                            "hole": "qc",
                            "opts": ["642.42", "817.95", "1040.07", "222.12"],
                            "a": 0,
                            "why": r'''
All of it: 642.42 VAR, the motor's own reactive power, because the target is unity. The
capacitor supplies leading VAR and the motor absorbs lagging VAR, and unity power factor is
the condition that the two are equal. 817.95 W is the real power, which the capacitor
neither supplies nor should; 1040.07 VA is the hypotenuse; 222.12 is $S - P$, a hypotenuse minus a side, which
is not the other side.
''',
                        },
                        {
                            "prompt": "The voltage across the capacitor",
                            "hole": "v",
                            "opts": ["230", "180.88", "142.06", "325.27"],
                            "a": 0,
                            "why": r'''
230 V RMS — the full supply voltage, because a parallel capacitor is across the load's
terminals and the load's terminals are the supply. 180.88 V and 142.06 V are the voltages
across the resistance and across the inductance *inside* the model, and neither is
available at any pair of terminals you can reach: the junction between $R$ and $L$ is
notional. Sizing on 142.06 V gives 101.3 µF, 2.6 times too much — and, by an unkind
coincidence, exactly the value that would resonate with the coil if it were ever put in
series. 325.27 V is the
peak, and every other quantity in this listing is RMS.
''',
                        },
                        {
                            "prompt": "What divides $Q_C$ to give the capacitance",
                            "hole": "denom",
                            "opts": ["omega * V^2", "omega * V", "V^2", "omega^2 * V"],
                            "a": 0,
                            "why": r'''
$Q_C = V^2/X_C$ and $X_C = 1/(\omega C)$, so $Q_C = \omega C V^2$ and
$C = Q_C/(\omega V^2)$. Both factors have to be there: dropping the $\omega$ leaves an
answer in the wrong units altogether, and dropping one power of $V$ leaves you dividing VAR
by volts, which is amps. The check is dimensional — VAR is volt-amps, and
$\text{V}\cdot\text{A}/(\text{rad s}^{-1}\cdot\text{V}^2) = \text{A}/(\text{V}\,\text{s}^{-1})
= \text{F}$.
''',
                        },
                        {
                            "prompt": "The capacitance, in microfarads",
                            "hole": "c",
                            "opts": ["38.655", "0.038655", "3865.5", "19.328"],
                            "a": 0,
                            "why": r'''
$642.42/(314.16 \times 52900) = 642.42/1.6619\times10^{7} = 3.8655\times10^{-5}$ F, which is
38.655 µF — call it 38.7 µF, and the part you would actually fit is a 40 µF motor-run
capacitor. 0.038655 is the same capacitance in millifarads, a prefix out of place. 3865.5 is
a hundred times too large. 19.328 is what comes of squaring the peak voltage instead of the
RMS one: the peak is $\sqrt2$ times larger, its square is twice as large, and the
capacitance comes out exactly half.
''',
                        },
                        {
                            "prompt": "The denominator of the cross-check",
                            "hole": "denom2",
                            "opts": ["2586.96", "1600", "986.96", "50.862"],
                            "a": 0,
                            "why": r'''
$R^2 + \omega^2L^2 = 1600 + 986.96 = 2586.96$, so $C = 0.1/2586.96 = 3.8655\times10^{-5}$ F
— the same answer the power triangle gave, to every digit, because the two expressions are
algebraically identical rather than merely close. 1600 is $R^2$ alone and 986.96 is
$\omega^2L^2$ alone; each on its own would be right only in a limit the circuit is not in.
50.862 is $|Z|$, and this denominator is $|Z|^2$.
''',
                        },
                        {
                            "prompt": "The supply current once the capacitor is fitted",
                            "hole": "inew",
                            "opts": ["3.5563", "4.5220", "0.9657", "5.7500"],
                            "a": 0,
                            "why": r'''
At unity power factor all the volt-amperes are watts, so $I = P/V = 817.95/230 = 3.5563$ A
RMS. The same number arrives from the corrected impedance:
$R_{eq} = (R^2+\omega^2L^2)/R = 64.674$ Ω and $230/64.674 = 3.5563$ A. 4.5220 A is what the
supply delivered *before* correction, and 0.9657 A is the difference between the two, which
is the reactive current the capacitor now provides locally. 5.7500 A is $230/R$, which is
the series-resonance disaster from putting the capacitor in the wrong place.
''',
                        },
                        {
                            "prompt": "What happens to the motor's real power",
                            "hole": "punchanged",
                            "opts": ["817.95 W, unchanged", "642.42 W", "1040.07 W", "0 W"],
                            "a": 0,
                            "why": r'''
Unchanged, at 817.95 W. The motor's terminal voltage is what it always was and so is the
current through it; the capacitor has not touched the machine, only changed where its
reactive current is fetched from. This is the whole design constraint — a correction that
reduced $P$ would be reducing the work done, which is the opposite of the intention — and
it is why fitting a capacitor does nothing to a bill that counts kilowatt-hours. What falls
is the current in the supply cable, and therefore the $I^2R$ heat in somebody else's
copper.
''',
                        },
                    ],
                },
            ],
            "build": {
                "title": "Correct the power factor of a motor",
                "minutes": 26,
                "brief": r'''
A 50 Hz supply, 40 Ω of line resistance between it and the load, and a load that is a
40 Ω resistance in series with a 100 mH inductance — the usual first model of a small
motor. The probe sits on the load.

As drawn, the current the supply delivers lags the voltage across the load, and the
line has to carry more current than the work requires. **Add a capacitor in parallel
with the load** so that at 50 Hz the supply sees a purely resistive load.

1. **At DC nothing changes.** The inductor is a wire and the capacitor an open circuit,
   so the two 40 Ω resistances divide and the probe reads half the source. If this
   check fails, the capacitor has been put in series rather than in parallel.
2. **At 50 Hz the load is purely resistive** — no phase shift between the probed
   voltage and the source, within a few degrees. That is unity power factor: the
   supply current is in phase with the supply voltage.
3. **At 50 Hz the probe reads 61.8% of the source**, which is what the corrected load
   impedance of 64.7 Ω gives against the 40 Ω line. Getting there confirms the
   capacitance and not merely its presence.
4. **Well above 50 Hz the network is now capacitive**, phase well past $-45°$ at
   500 Hz, because the correction was only ever exact at one frequency.

The capacitance you need is $C = \dfrac{L}{R^2 + \omega^2 L^2}$, which the derivation in
this module works out; it comes to about 38.7 µF here.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 40},
                        {"id": "p3", "kind": "OUT", "x": 8, "y": 3, "rot": 0, "value": 0},
                        {"id": "p4", "kind": "R", "x": 8, "y": 4, "rot": 1, "value": 40},
                        {"id": "p5", "kind": "L", "x": 8, "y": 6, "rot": 1, "value": 0.1},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [8, 3]},
                        {"a": [8, 7], "b": [3, 7]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 40},
                        {"id": "p3", "kind": "OUT", "x": 8, "y": 3, "rot": 0, "value": 0},
                        {"id": "p4", "kind": "R", "x": 8, "y": 4, "rot": 1, "value": 40},
                        {"id": "p5", "kind": "L", "x": 8, "y": 6, "rot": 1, "value": 0.1},
                        {"id": "p6", "kind": "C", "x": 12, "y": 5, "rot": 1, "value": 3.87e-5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [8, 3]},
                        {"a": [8, 7], "b": [3, 7]},
                        {"a": [8, 3], "b": [12, 3]},
                        {"a": [12, 3], "b": [12, 4]},
                        {"a": [12, 6], "b": [12, 7]},
                        {"a": [12, 7], "b": [8, 7]},
                    ],
                },
                "checks": [
                    {"name": "at DC the two resistances still divide in half", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(Math.abs(c.vout()), 0.5 * vs, 0.02,
  "the inductor is a wire at DC and the capacitor an open circuit, so two equal resistances should share the source");
'''},
                    {"name": "at 50 Hz the supply sees a purely resistive load", "code": r'''
var p = c.phase(50);
c.assert(Math.abs(p) < 3,
  "the probed voltage is " + p.toPrecision(3) + " degrees from the source; at unity power factor " +
  "the load impedance is real and that angle goes to zero");
'''},
                    {"name": "at 50 Hz the load takes 61.8% of the supply", "code": r'''
var vs = Math.abs(c.values("V")[0]);
c.close(c.gain(50) / vs, 0.6178, 0.02,
  "a corrected load of 64.7 ohms against 40 ohms of line gives 0.618; a different figure means a different capacitance");
'''},
                    {"name": "well above 50 Hz the network is capacitive", "code": r'''
var p = c.phase(500);
c.assert(p < -45,
  "at 500 Hz the added capacitor should dominate and the phase should be strongly negative; measured " +
  p.toPrecision(3) + " degrees");
'''},
                ],
                "hints": [
                    "The capacitor goes from the probe node down to the ground rail, alongside the motor rather than in line with it. In series it would block the direct current and the first check would fail immediately.",
                    "$\\omega = 2\\pi \\times 50 = 314.16$ rad/s, so $\\omega L = 31.4$ Ω and $R^2 + \\omega^2L^2 = 1600 + 987 = 2587$.",
                    "$C = L/2587 = 0.1/2587 = 3.87\\times10^{-5}$ F. Type 38.7u.",
                    "If the phase at 50 Hz has gone from positive to strongly negative, the capacitor is too large — you have over-corrected past the cancellation rather than landing on it.",
                ],
            },
            "numeric": [
                {
                    "title": "How much of it is real",
                    "minutes": 7,
                    "brief": r'''
First rung, and the only new idea is the last line of arithmetic. A coil and a resistor in
series across a 50 Hz supply, with the probe across the resistor.

Find the impedance the way Module 3 did, and the power factor is one division away — no
current, no watts, no volt-amperes needed.
''',
                    "prompt": "What is the power factor of this load at 50 Hz?",
                    "note": "A ratio, so it has no unit. Three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 230},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                            {"id": "l1", "kind": "L", "x": 6, "y": 3, "rot": 0, "value": 0.1},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 40},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "230 V RMS at 50.0 Hz"},
                        {"label": "Inductor", "value": "100 mH"},
                        {"label": "Resistor", "value": "40.0 Ω"},
                    ],
                    "aside": "The power factor is $\\cos\\phi$, and $\\phi$ is the angle of the "
                             "impedance. For a series pair that angle has a cosine you can write "
                             "down without a calculator's inverse trig: it is the adjacent side "
                             "over the hypotenuse.",
                    "answer": 0.786,
                    "tol": 0.004,
                    "unit": "",
                    # Solved, not restated: the check reads the resistor's voltage out of the AC
                    # solution, turns it into a current and a real power with the resistance the
                    # netlist reports, and divides by the volt-amperes the source delivers.
                    "check": r'''
c.assert(c.count('R') === 1 && c.count('L') === 1, "one resistor and one coil in series");
var Vs = Math.abs(c.values('V')[0]);
var R = c.values('R')[0];
var vr = c.gain(50);
var I = vr / R;
return (vr * vr / R) / (Vs * I);
''',
                    "hint": "$X_L = \\omega L$ with $\\omega = 2\\pi f$, then "
                            "$|Z| = \\sqrt{R^2 + X_L^2}$, then $\\cos\\phi = R/|Z|$.",
                    "wrong": "0.618 is $X_L/|Z| = \\sin\\phi$, the reactive factor, which is the "
                             "other side of the same triangle. 1.27 is $|Z|/R$ — a power factor "
                             "greater than one is impossible, and that is the check that catches it. "
                             "0.560 comes from $R/(R+X_L)$, adding a resistance to a reactance "
                             "instead of combining them by Pythagoras. 1.00 is the answer for a "
                             "resistor on its own, which is what the circuit would be if the coil "
                             "were a short.",
                    "why": r'''
```
w         = 2*pi*50                            = 314.159 rad/s
X_L       = w*L = 314.159 * 0.1                = 31.4159 ohm
|Z|       = sqrt(40^2 + 31.4159^2)
          = sqrt(1600 + 986.960)               = 50.8622 ohm
pf        = cos(phi) = R/|Z| = 40/50.8622      = 0.7864
```

That is the whole calculation, but it is worth seeing the same number arrive the long way,
because the long way is what the definition actually says:

```
I         = 230/50.8622                        = 4.5220 A rms
P         = I^2 * R = 20.4487 * 40             = 817.95 W
S         = 230 * 4.5220                       = 1040.07 VA
pf        = P/S = 817.95/1040.07               = 0.7864
```

$\cos\phi$, $R/|Z|$ and $P/S$ are three spellings of one ratio, and which one you reach for
depends only on what you happen to have been given.

There is a third reading available here, and it is the one the probe is showing you. The
resistor's voltage is $I R = 4.5220 \times 40 = 180.88$ V, and $180.88/230 = 0.7864$. In a
series pair the fraction of the supply voltage that lands on the resistance *is* the power
factor — the same triangle, scaled by the current. The remaining 142.06 V is across the
coil, and $\sqrt{180.88^2 + 142.06^2} = 230.0$ V, which is the reminder that the two
voltages do not add to the supply and never did.

The angle itself, if you want it, is $\arctan(31.4159/40) = 38.15°$, so the current crests
about 2.1 ms after the voltage on a 20 ms cycle. Nothing later in this module needs the
angle; everything needs its cosine.
''',
                },
                {
                    "title": "The watts behind two meter readings",
                    "minutes": 8,
                    "brief": r'''
Second rung. Same shape of circuit, different reactance and a different question: not the
ratio this time but the watts themselves.

A capacitor instead of a coil, so the current now *leads*. It makes no difference to the
power — $\cos\phi$ does not care about the sign of $\phi$ — which is a fact worth
noticing rather than being told.
''',
                    "prompt": "How much real power does this circuit dissipate at 60 Hz?",
                    "note": "Give the answer in watts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 120},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                            {"id": "c1", "kind": "C", "x": 6, "y": 3, "rot": 0, "value": 2e-5},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 100},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "120 V RMS at 60.0 Hz"},
                        {"label": "Capacitor", "value": "20.0 µF"},
                        {"label": "Resistor", "value": "100 Ω"},
                    ],
                    "aside": "Only the resistor dissipates. So the shortest route is to find the "
                             "one current in the loop and use $I^2R$ — or, equivalently, to "
                             "read the resistor's own voltage and use $V^2/R$ with that voltage "
                             "rather than the supply's.",
                    "answer": 52.2,
                    "tol": 0.4,
                    "unit": "W",
                    # The probed voltage is the resistor's own, so the power falls out of it and the
                    # resistance the netlist reports; both the reactance and the divider are the
                    # solver's work rather than a repeated constant.
                    "check": r'''
c.assert(c.count('R') === 1 && c.count('C') === 1, "one resistor and one capacitor in series");
var R = c.values('R')[0];
var v = c.gain(60);
return v * v / R;
''',
                    "hint": "$X_C = 1/(\\omega C)$, then $|Z| = \\sqrt{R^2 + X_C^2}$, then "
                            "$I = V/|Z|$, then $P = I^2 R$. The capacitor takes no power at all, so "
                            "it appears in $|Z|$ and nowhere else.",
                    "wrong": "144 W is $V^2/R$ using the supply's 120 V instead of the resistor's "
                             "own 72.2 V, and it ignores everything the capacitor does. 86.7 is "
                             "the apparent power $V I$, in volt-amperes rather than watts. 69.2 is "
                             "the reactive power in VAR, which the capacitor handles and never "
                             "dissipates. "
                             "26.6 W follows from $|Z| = R + X_C = 232.6$ Ω, the addition Pythagoras "
                             "forbids, which makes the current too small.",
                    "why": r'''
```
w         = 2*pi*60                            = 376.991 rad/s
w*C       = 376.991 * 2e-5                     = 7.53982e-3 S
X_C       = 1/7.53982e-3                       = 132.629 ohm
|Z|       = sqrt(100^2 + 132.629^2)
          = sqrt(10000 + 17590.5)              = 166.104 ohm
I         = 120/166.104                        = 0.72244 A rms
P         = I^2 * R = 0.521919 * 100           = 52.19 W
```

The probe confirms it from the other end: the resistor's voltage is
$0.72244 \times 100 = 72.244$ V, and $72.244^2/100 = 52.19$ W. Two routes, one answer, and
if they had disagreed the error would be in $|Z|$.

The rest of the triangle, since the numbers are on the table:

```
S         = 120 * 0.72244                      = 86.69 VA
Q         = I^2 * X_C = 0.521919 * 132.629     = 69.22 VAR
check     sqrt(52.19^2 + 69.22^2)              = 86.69 VA
pf        = 52.19/86.69 = 100/166.104          = 0.602
```

A power factor of 0.602, and this time the current *leads* the voltage — the capacitor's
reactance enters $|Z|$ with the opposite sign, $\phi = -53.0°$ rather than $+38.1°$. The
sign changes nothing about the power, because $\cos(-53°) = \cos(53°)$. It changes
everything about the cure: a load like this one is already leading, and hanging more
capacitance on it would make matters worse rather than better.

Worth noticing how much of the supply's volt-amperes this circuit is wasting the use of.
86.69 VA of cable and switchgear are being occupied to deliver 52.19 W of heat. That is
what a bad power factor buys you, and the fact that the reactance here is a capacitor
rather than a coil makes no difference to the bill for the copper.
''',
                },
                {
                    "title": "Sized in volt-amperes, not in watts",
                    "minutes": 9,
                    "brief": r'''
Third rung, and two things change at once. The two components are now in *parallel*, which
means admittance rather than impedance, and the source is a current source rather than a
voltage source — 400 Hz, because that is what an aircraft's supply runs at and a 400 Hz
load is where a coil this small starts to matter.

A current source fixes the current whatever the load does, so there is nothing to divide.
The impedance turns the current into a voltage, and the voltage is what the probe reads.
''',
                    "prompt": "What apparent power does the source deliver at 400 Hz?",
                    "note": "Give the answer in volt-amperes, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "is", "kind": "I", "x": 3, "y": 5, "rot": 1, "value": 2},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                            {"id": "out", "kind": "OUT", "x": 5, "y": 3, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 7, "y": 5, "rot": 1, "value": 50},
                            {"id": "l1", "kind": "L", "x": 10, "y": 5, "rot": 1, "value": 0.02},
                        ],
                        "wires": [
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [5, 3], "b": [7, 3]},
                            {"a": [7, 3], "b": [7, 4]},
                            {"a": [7, 6], "b": [7, 7]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 3], "b": [10, 4]},
                            {"a": [10, 6], "b": [10, 7]},
                            {"a": [3, 7], "b": [7, 7]},
                            {"a": [7, 7], "b": [10, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "2.00 A RMS at 400 Hz"},
                        {"label": "Resistor", "value": "50.0 Ω"},
                        {"label": "Inductor", "value": "20.0 mH"},
                    ],
                    "aside": "Parallel branches share a voltage, so add conductance and susceptance "
                             "— with signs — and invert once at the end. The apparent power "
                             "is then the product of two magnitudes and needs no angle at all.",
                    "answer": 142.0,
                    "tol": 1.0,
                    "unit": "VA",
                    # The node voltage comes from the solver, and the source current is read off the
                    # netlist rather than restated, so a change to either part of the drawing moves
                    # the checked value.
                    "check": r'''
c.assert(c.count('I') === 1 && c.count('V') === 0, "a current source drives this one");
return c.gain(400) * Math.abs(c.values('I')[0]);
''',
                    "hint": "$G = 1/R$ and $B_L = -1/(\\omega L)$; $|Y| = \\sqrt{G^2 + B_L^2}$ and "
                            "$|Z| = 1/|Y|$. Then $|V| = I|Z|$ and $S = |V| \\times I$.",
                    "wrong": "200 VA is what the resistor alone would give, $|Z| = 50$ Ω and "
                             "$V = 100$ V, with the coil left out of the admittance. 100.5 W is the "
                             "*real* power — a genuine quantity, and a smaller one, but not what "
                             "the source has to be rated for. 401 VA adds the two branch impedances "
                             "as though they were in series. 70.9 is the node voltage in volts, one "
                             "multiplication short of an answer.",
                    "why": r'''
Parallel, so work in siemens and keep the signs:

```
w         = 2*pi*400                           = 2513.27 rad/s
X_L       = w*L = 2513.27 * 0.02               = 50.2655 ohm
G         = 1/50                               = 20.0000 mS
B_L       = -1/50.2655                         = -19.8944 mS
|Y|       = sqrt(20.0000^2 + 19.8944^2) mS     = 28.2097 mS
|Z|       = 1/28.2097e-3                       = 35.4488 ohm
```

The two branches are almost equally conductive at 400 Hz, which is a way of saying the coil
is drawing almost as much current as the resistor. Now the source:

```
|V|       = I * |Z| = 2.00 * 35.4488           = 70.898 V rms
S         = |V| * I = 70.898 * 2.00            = 141.80 VA
```

And the split, which is where the point is:

```
P         = |V|^2/R = 5026.5/50                = 100.53 W
Q         = |V|^2/X_L = 5026.5/50.2655         = 100.00 VAR
check     sqrt(100.53^2 + 100.00^2)            = 141.80 VA
pf        = 100.53/141.80                      = 0.709
```

141.8 VA of supply capacity for 100.5 W of work. Notice that $P$ and $Q$ are nearly equal
here, which is exactly what a power factor near $1/\sqrt2$ means — $\phi$ is close to 45°,
and at 45° the two sides of the triangle are the same length.

The branch currents make the same point in amps. The resistor takes
$70.898/50 = 1.418$ A and the coil takes $70.898/50.2655 = 1.410$ A, which sum
arithmetically to 2.828 A while the source supplies only 2.000 A. They do not add up
because they are a quarter cycle apart: $\sqrt{1.418^2 + 1.410^2} = 2.000$ A. The coil's
1.41 A is doing no work whatever, and it is 70% of the current the supply has to be able to
deliver.
''',
                },
                {
                    "title": "What the poor power factor costs the cable",
                    "minutes": 11,
                    "brief": r'''
Fourth rung, and now there is a cable in the way. 2 Ω of line resistance stands between
the supply and a motor modelled, as usual, as 40 Ω in series with 100 mH. The probe sits
at the motor's terminals, where the cable ends.

The question is not about the motor. It is about the heat in the wire feeding it, which is
the quantity the whole of power factor correction exists to reduce.
''',
                    "prompt": "How much power does the 2.00 Ω line resistance dissipate at 50 Hz?",
                    "note": "Give the answer in watts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 230},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                            {"id": "rline", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 2},
                            {"id": "out", "kind": "OUT", "x": 8, "y": 3, "rot": 0, "value": 0},
                            {"id": "rm", "kind": "R", "x": 8, "y": 4, "rot": 1, "value": 40},
                            {"id": "lm", "kind": "L", "x": 8, "y": 6, "rot": 1, "value": 0.1},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [4, 3]},
                            {"a": [6, 3], "b": [8, 3]},
                            {"a": [8, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "230 V RMS at 50.0 Hz"},
                        {"label": "Line resistance", "value": "2.00 Ω"},
                        {"label": "Motor winding", "value": "40.0 Ω"},
                        {"label": "Motor inductance", "value": "100 mH"},
                    ],
                    "aside": "Everything is in one loop, so there is one current. The two "
                             "resistances add — they are resistances, and in series — and "
                             "the reactance joins them at right angles. The line dissipates $I^2$ "
                             "times its own 2 Ω and nothing else.",
                    "answer": 38.5,
                    "tol": 0.3,
                    "unit": "W",
                    # The check never assumes the loop is series: it reads the probed voltage as a
                    # complex number, subtracts it from the source, and applies Ohm's law to the line
                    # resistor alone, so the answer is the solver's and not a re-run of the prompt.
                    "check": r'''
var Vs = Math.abs(c.values('V')[0]);
var Rl = c.net.parts.filter(function (p) { return p.id === 'rline'; })[0].value;
var g = c.gain(50), ph = c.phase(50) * Math.PI / 180;
var ix = (Vs - g * Math.cos(ph)) / Rl;
var iy = -g * Math.sin(ph) / Rl;
return (ix * ix + iy * iy) * Rl;
''',
                    "hint": "$|Z_{tot}| = \\sqrt{(2+40)^2 + (\\omega L)^2}$, then $I = 230/|Z_{tot}|$, "
                            "then $P_{line} = I^2 \\times 2$.",
                    "wrong": "23.8 W is what this line dissipates once the motor has been corrected, "
                             "which is the saving the module is about and not what the circuit as "
                             "drawn does. 769 W is the motor's own dissipation in its 40 Ω. "
                             "40.9 W leaves the 2 Ω out of $|Z_{tot}|$ before finding the "
                             "current, so the current comes out too big. 19.2 is $I^2$ with the "
                             "final multiplication by 2 Ω forgotten.",
                    "why": r'''
One loop, one current, so add the two resistances and put the reactance at right angles to
the total:

```
w         = 2*pi*50                            = 314.159 rad/s
X_L       = 31.4159 ohm
R_tot     = 2 + 40                             = 42 ohm
|Z_tot|   = sqrt(42^2 + 31.4159^2)
          = sqrt(1764 + 986.960)               = 52.4496 ohm
I         = 230/52.4496                        = 4.38516 A rms
I^2                                            = 19.2296 A^2
P_line    = 19.2296 * 2                        = 38.46 W
```

The motor takes $19.2296 \times 40 = 769.19$ W out of the $19.2296 \times 42 = 807.65$ W the
supply delivers, so 4.8% of everything sent down the cable is being spent heating the cable.

Now the part that makes the number mean something. Fit the correcting capacitor — 38.7 µF,
from this module's derivation — across the motor's terminals, and the load stops being
$40 + j31.4$ and becomes a pure 64.674 Ω:

```
I         = 230/(2 + 64.674)                   = 3.44962 A rms
P_line    = 3.44962^2 * 2 = 11.8999 * 2        = 23.80 W
```

The line loss falls from 38.46 W to 23.80 W — a saving of 14.66 W, 38% of what the cable was
wasting — and the motor keeps doing its job untouched. In fact it does a hair more of it:
because less voltage is now being dropped in the cable, the motor's terminals rise from
223.04 V to 223.10 V and its dissipation rises from 769.19 W to 769.61 W. Four tenths of a
watt, in the direction nobody complains about.

Scale that thought up. A factory drawing hundreds of amps at 0.79 rather than 1.00 is
paying the same 62% surcharge on every metre of copper between it and the transformer, and
on the transformer, and it is doing so continuously. A capacitor is a cheap thing to buy
once.
''',
                },
                {
                    "title": "The reactive power of a whole installation",
                    "minutes": 12,
                    "brief": r'''
The hardest one here, and nothing in it is new. Two loads share a supply now — a 35
Ω heater and the same motor as before — and half an ohm of cable feeds both. The
probe sits where the cable ends, on the busbar the two loads hang from.

Nothing asked for is a node voltage. What is wanted is the *reactive* power the installation
draws through that cable: the part of the volt-amperes that is being carried down and back
each cycle, and that a capacitor could cancel.

Four steps, none of them signposted: what the two branches look like together, what the
supply current is with the cable included, what voltage the busbar sits at, and which part
of the power is reactive.
''',
                    "prompt": "What reactive power do the two loads together draw at 50 Hz?",
                    "note": "Give the answer in VAR, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 230},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9, "rot": 0, "value": 0},
                            {"id": "rline", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 0.5},
                            {"id": "out", "kind": "OUT", "x": 8, "y": 3, "rot": 0, "value": 0},
                            {"id": "rh", "kind": "R", "x": 8, "y": 5, "rot": 1, "value": 35},
                            {"id": "rm", "kind": "R", "x": 12, "y": 4, "rot": 1, "value": 40},
                            {"id": "lm", "kind": "L", "x": 12, "y": 6, "rot": 1, "value": 0.1},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [4, 3]},
                            {"a": [6, 3], "b": [8, 3]},
                            {"a": [8, 3], "b": [8, 4]},
                            {"a": [8, 6], "b": [8, 7]},
                            {"a": [8, 7], "b": [3, 7]},
                            {"a": [8, 3], "b": [12, 3]},
                            {"a": [12, 7], "b": [8, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "230 V RMS at 50.0 Hz"},
                        {"label": "Line resistance", "value": "0.500 Ω"},
                        {"label": "Heater", "value": "35.0 Ω"},
                        {"label": "Motor", "value": "40.0 Ω in series with 100 mH"},
                    ],
                    "aside": "The two loads are in parallel, so combine them in admittance and "
                             "invert once. The half-ohm is in series with the result and is a pure "
                             "resistance, so it changes the current but adds nothing to the reactive "
                             "part — which is a shortcut worth spotting, and a cross-check "
                             "worth using even if you do not.",
                    "answer": 615.0,
                    "tol": 5.0,
                    "unit": "VAR",
                    # Nothing here is restated from the prompt: the probe's complex voltage and the
                    # current through the named line resistor give S = V I*, and the check returns
                    # its imaginary part, which is the reactive power the load actually draws.
                    "check": r'''
c.assert(c.count('R') === 3 && c.count('L') === 1, "a line resistance, a heater and a motor");
var Vs = Math.abs(c.values('V')[0]);
var Rl = c.net.parts.filter(function (p) { return p.id === 'rline'; })[0].value;
var g = c.gain(50), ph = c.phase(50) * Math.PI / 180;
var vx = g * Math.cos(ph), vy = g * Math.sin(ph);
var ix = (Vs - vx) / Rl, iy = -vy / Rl;
return vy * ix - vx * iy;
''',
                    "hint": "A resistor has no reactive power at all, so all of the answer belongs to "
                            "the motor. Find the busbar voltage first, then the motor's own branch "
                            "current, then $Q = I_{motor}^2 \\, \\omega L$.",
                    "wrong": "642 VAR is the motor's reactive power on a full 230 V, which is what "
                             "it would draw if the cable dropped nothing; the busbar actually sits at "
                             "225.0 V. 2230 is the real power, in watts. 2313 is the apparent "
                             "power in volt-amperes, the hypotenuse rather than the side. 83.3 "
                             "is $S - P$, a hypotenuse minus a side, which is the subtraction that "
                             "$S^2 = P^2 + Q^2$ exists to forbid.",
                    "why": r'''
Two branches on one node, so combine them in siemens:

```
w         = 2*pi*50, X_L = 31.4159 ohm
heater    Y_h = 1/35                           = 28.5714 mS
motor     Y_m = (40 - j31.4159)/2586.96
              = 15.4622 - j12.1440 mS
together  Y   = 44.0336 - j12.1440 mS
          |Y| = 45.6775 mS
Z_load    = 1/Y = 21.1047 + j5.8204 ohm
          |Z_load|                             = 21.8926 ohm
```

Then the cable, which is in series with all of that:

```
Z_tot     = 0.5 + 21.1047 + j5.8204
          = 21.6047 + j5.8204
|Z_tot|   = sqrt(466.76 + 33.877)              = 22.3750 ohm
I         = 230/22.3750                        = 10.2793 A rms
I^2                                            = 105.664 A^2
Q_load    = I^2 * Im(Z_load) = 105.664 * 5.8204 = 615.0 VAR
```

The cross-check is the one worth doing, because it goes through completely different
numbers and has to land on the same answer. The busbar voltage is
$I \times |Z_{load}| = 10.2793 \times 21.8926 = 225.04$ V, so the motor's own branch carries

```
|Y_m|     = sqrt(15.4622^2 + 12.1440^2) mS     = 19.6610 mS
I_motor   = 225.04 * 19.6610e-3                = 4.4245 A rms
Q         = I_motor^2 * X_L = 19.5764 * 31.4159 = 615.0 VAR
```

Identical, and it shows where the reactive power lives: all of it is the motor's. The heater
is a resistance and a resistance has no reactive power at all — not a small amount, not a
negative amount, none. Reactive powers add like watts do, so the installation's $Q$ is
whatever the reactive loads bring and nothing else.

The rest of the picture, for scale:

```
P_load    = I^2 * 21.1047                      = 2230.0 W
   of which heater  225.04^2/35                = 1447.0 W
   and motor        4.4245^2 * 40              = 783.1 W
S_load    = sqrt(2230.0^2 + 615.0^2)           = 2313.3 VA
pf                                             = 0.964
P_line    = 105.664 * 0.5                      = 52.83 W
```

A power factor of 0.964, which is respectable, and it got that way without anybody
correcting anything: the heater's 1447 W of purely resistive load has diluted the motor's
615 VAR. That is worth remembering the next time a nameplate power factor looks
suspiciously good — a power factor is a property of an installation at a moment, not of a
machine, and it moves every time something is switched on.
''',
                },
            ],
            "derive": {
                "title": "How much capacitance corrects a motor",
                "minutes": 12,
                "vars": ["R", "L", "C", "omega", "j"],
                "brief": r'''
A motor modelled as a resistance $R$ in series with an inductance $L$, running at
angular frequency $\omega$. A capacitor $C$ goes in parallel with it, and the job is to
choose $C$ so that the supply sees no reactance at all.

Because the capacitor is in *parallel*, the natural currency is admittance rather than
impedance: things in parallel add their admittances, and the condition for unity power
factor is that the total admittance is real.
''',
                "steps": [
                    {
                        "prompt": "Write the impedance of the motor at angular frequency $\\omega$.",
                        "answer": "R + j\\omega L",
                        "hint": "Two components in series: their impedances add.",
                        "deconstruct": [
                            "The resistance contributes $R$.",
                            "The inductance contributes $j\\omega L$.",
                        ],
                    },
                    {
                        "prompt": "Invert it to get the motor's admittance, and rationalise so that the denominator is real.",
                        "given": "Multiply above and below by the complex conjugate of the denominator.",
                        "answer": "\\frac{R - j\\omega L}{R^2 + \\omega^2 L^2}",
                        "placeholder": "\\frac{\\ldots}{R^2 + \\ldots}",
                        "hint": "The conjugate of $R + j\\omega L$ is $R - j\\omega L$, and multiplying the two gives $R^2 + \\omega^2 L^2$ with no $j$ left in it.",
                        "deconstruct": [
                            "$Y = \\dfrac{1}{R + j\\omega L}$.",
                            "Multiply top and bottom by $R - j\\omega L$.",
                            "The bottom becomes $R^2 - (j\\omega L)^2 = R^2 + \\omega^2 L^2$.",
                        ],
                    },
                    {
                        "prompt": "The capacitor in parallel adds $j\\omega C$ to that admittance. Write what $\\omega C$ must equal for the total to have no imaginary part.",
                        "answer": "\\frac{\\omega L}{R^2 + \\omega^2 L^2}",
                        "hint": "The motor's admittance carries a negative imaginary part. The capacitor has to supply exactly the same amount with the opposite sign.",
                        "deconstruct": [
                            "The imaginary part of the motor's admittance is $-\\dfrac{\\omega L}{R^2 + \\omega^2 L^2}$.",
                            "Adding $j\\omega C$ makes the total imaginary part $\\omega C - \\dfrac{\\omega L}{R^2+\\omega^2L^2}$.",
                            "Setting that to zero gives the answer.",
                        ],
                    },
                    {
                        "prompt": "Divide through by $\\omega$ and write $C$.",
                        "answer": "\\frac{L}{R^2 + \\omega^2 L^2}",
                        "hint": "One factor of $\\omega$ cancels top and bottom on the left-hand side only.",
                        "deconstruct": [
                            "$\\omega C = \\dfrac{\\omega L}{R^2 + \\omega^2 L^2}$.",
                            "Dividing both sides by $\\omega$ removes it from the numerator on the right.",
                        ],
                    },
                ],
                "closing": r'''
$C = \dfrac{L}{R^2 + \omega^2 L^2}$. Put the build's numbers in — $R = 40$ Ω,
$L = 100$ mH, $\omega = 2\pi \times 50 = 314.16$ rad/s — and the denominator is
$1600 + 987 = 2587$, giving $C = 38.7$ µF.

Two things fall out of the shape of that expression. It contains $\omega$, so the
answer is only right at the frequency you put in. And as $R \to 0$ it becomes
$C = 1/(\omega^2 L)$, which is the condition $\omega = 1/\sqrt{LC}$ rearranged: correct
a lossless inductor and you have simply built a parallel resonant tank at the supply
frequency.
''',
            },
            "lab": {
                "title": "The power triangle from two waveforms",
                "runtime": "python",
                "minutes": 26,
                "brief": r'''
An instrument that measures power has two inputs and no knowledge of any formula. It
samples the voltage, samples the current, and multiplies. Everything else follows.

`wave` is given; you do not need to change it. It produces whole cycles of a sinusoid
so that every average below is exact.

`rms(x)` returns the root of the mean of the square of an array.

`real_power(v, i)` returns the average of the product $v(t)\,i(t)$ — the watts.

`apparent_power(v, i)` returns $V_{rms} I_{rms}$ — the volt-amperes.

`power_factor(v, i)` returns the ratio of the two, which is $\cos\phi$ for sinusoids and
is still meaningful when they are not.

`reactive_power(v, i)` returns $\sqrt{S^2 - P^2}$ — the VAR. Guard the square root: a
purely resistive load can leave $S^2 - P^2$ a hair below zero in floating point, and
`np.sqrt` of that is a NaN that propagates into everything downstream.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def wave(peak, f, fs, n, phase=0.0):
    """n samples of peak*sin(2*pi*f*t + phase) at fs samples per second. Given."""
    t = np.arange(n) / float(fs)
    return peak * np.sin(2.0 * np.pi * f * t + phase)


def rms(x):
    """Root of the mean of the square."""
    # TODO
    return 0.0


def real_power(v, i):
    """Average of the instantaneous product, in watts."""
    # TODO
    return 0.0


def apparent_power(v, i):
    """RMS volts times RMS amps, in volt-amperes."""
    # TODO
    return 0.0


def power_factor(v, i):
    """Real power over apparent power."""
    # TODO
    return 0.0


def reactive_power(v, i):
    """sqrt(S**2 - P**2), in VAR. Never let the root go negative."""
    # TODO
    return 0.0


if __name__ == "__main__":
    V = wave(230.0 * np.sqrt(2), 50.0, 20000.0, 20000)
    I = wave(10.0, 50.0, 20000.0, 20000, phase=-np.arccos(0.8))
    print("P:", round(real_power(V, I), 3), "W")
    print("S:", round(apparent_power(V, I), 3), "VA")
    print("Q:", round(reactive_power(V, I), 3), "VAR")
    print("power factor:", round(power_factor(V, I), 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def wave(peak, f, fs, n, phase=0.0):
    """n samples of peak*sin(2*pi*f*t + phase) at fs samples per second. Given."""
    t = np.arange(n) / float(fs)
    return peak * np.sin(2.0 * np.pi * f * t + phase)


def rms(x):
    """Root of the mean of the square."""
    x = np.asarray(x, dtype=float)
    return float(np.sqrt(np.mean(x * x)))


def real_power(v, i):
    """Average of the instantaneous product, in watts."""
    v = np.asarray(v, dtype=float)
    i = np.asarray(i, dtype=float)
    return float(np.mean(v * i))


def apparent_power(v, i):
    """RMS volts times RMS amps, in volt-amperes."""
    return rms(v) * rms(i)


def power_factor(v, i):
    """Real power over apparent power."""
    s = apparent_power(v, i)
    return float(real_power(v, i) / s) if s else 0.0


def reactive_power(v, i):
    """sqrt(S**2 - P**2), in VAR. Never let the root go negative."""
    s = apparent_power(v, i)
    p = real_power(v, i)
    return float(np.sqrt(max(s * s - p * p, 0.0)))


if __name__ == "__main__":
    V = wave(230.0 * np.sqrt(2), 50.0, 20000.0, 20000)
    I = wave(10.0, 50.0, 20000.0, 20000, phase=-np.arccos(0.8))
    print("P:", round(real_power(V, I), 3), "W")
    print("S:", round(apparent_power(V, I), 3), "VA")
    print("Q:", round(reactive_power(V, I), 3), "VAR")
    print("power factor:", round(power_factor(V, I), 6))
'''}],
                "hints": [
                    "`np.mean(v * i)` is the whole of `real_power` — the elementwise product, not a dot product, and no factor of two anywhere. The half in $V_pI_p/2$ appears on its own once the average is taken.",
                    "`apparent_power` should call `rms` twice rather than repeating it, and `power_factor` should call both of the functions above it.",
                    "In `reactive_power`, `max(s*s - p*p, 0.0)` before the square root. For a purely resistive load the two are equal in exact arithmetic and differ in the last bit in floating point.",
                ],
                "tests": [
                    {"name": "a resistive load: everything is real power", "code": r'''
_v = wave(10.0, 50.0, 10000.0, 10000)
_i = wave(2.0, 50.0, 10000.0, 10000)
assert abs(real_power(_v, _i) - 10.0) < 1e-9, \
    f"10 V peak and 2 A peak in phase averages Vp*Ip/2 = 10 W; got {real_power(_v, _i)}"
assert abs(apparent_power(_v, _i) - 10.0) < 1e-9, f"S is also 10 VA here; got {apparent_power(_v, _i)}"
assert abs(power_factor(_v, _i) - 1.0) < 1e-9, "a resistive load has a power factor of exactly 1"
assert reactive_power(_v, _i) < 1e-6, \
    f"and no reactive power at all; got {reactive_power(_v, _i)} (a NaN here means the square root went negative)"
'''},
                    {"name": "a purely reactive load: no real power at all", "code": r'''
import numpy as np
_v = wave(10.0, 50.0, 10000.0, 10000)
_i = wave(2.0, 50.0, 10000.0, 10000, phase=-np.pi / 2)
assert abs(real_power(_v, _i)) < 1e-9, \
    f"a quarter cycle apart, the product is positive as often as it is negative; got {real_power(_v, _i)}"
assert abs(power_factor(_v, _i)) < 1e-9, "cos(90 degrees) is zero"
assert abs(reactive_power(_v, _i) - 10.0) < 1e-9, \
    f"all 10 VA of it is reactive; got {reactive_power(_v, _i)}"
'''},
                    {"name": "sixty degrees of lag halves the power", "code": r'''
import numpy as np
_v = wave(10.0, 50.0, 10000.0, 10000)
_i = wave(2.0, 50.0, 10000.0, 10000, phase=-np.pi / 3)
assert abs(power_factor(_v, _i) - 0.5) < 1e-9, f"cos(60 degrees) is 0.5; got {power_factor(_v, _i)}"
assert abs(real_power(_v, _i) - 5.0) < 1e-9, f"half of 10 VA is 5 W; got {real_power(_v, _i)}"
assert abs(reactive_power(_v, _i) - 8.660254037844387) < 1e-9, \
    f"10*sin(60 degrees) = 8.6603 VAR; got {reactive_power(_v, _i)}"
'''},
                    {"name": "the triangle closes", "code": r'''
import numpy as np
_v = wave(325.269, 50.0, 20000.0, 20000)
_i = wave(10.0, 50.0, 20000.0, 20000, phase=-np.arccos(0.8))
_p, _s, _q = real_power(_v, _i), apparent_power(_v, _i), reactive_power(_v, _i)
assert abs(_p * _p + _q * _q - _s * _s) / (_s * _s) < 1e-9, \
    f"S^2 should equal P^2 + Q^2: {_s*_s:.3f} against {_p*_p + _q*_q:.3f}"
assert abs(power_factor(_v, _i) - 0.8) < 1e-6, f"the current was built with a lag of arccos(0.8); got {power_factor(_v, _i)}"
assert abs(_p - 1301.076) < 0.05, f"230 V rms and 10 A peak at 0.8 gives 1301.08 W; got {_p}"
'''},
                    {"name": "rms works on shapes that are not sinusoids", "code": r'''
import numpy as np
assert abs(rms(np.full(64, 3.0)) - 3.0) < 1e-12, "a steady 3 V is 3 V rms"
_sq = np.array([4.0] * 50 + [-4.0] * 50)
assert abs(rms(_sq) - 4.0) < 1e-12, f"a square wave's rms is its peak; got {rms(_sq)}"
_p = real_power(_sq, _sq / 8.0)
assert abs(_p - 2.0) < 1e-12, \
    f"a square wave into 8 ohms dissipates 16/8 = 2 W, and the definition should handle it; got {_p}"
'''},
                ],
            },
        },

        # ---- M10 ----------------------------------------------------------
        {
            "title": "Thévenin, Norton and the conjugate match",
            "summary": "Any linear network, however tangled, is one source and one impedance. What you connect to it decides how much of its power you get.",
            "concepts": [
                "**Thévenin's theorem.** Any network of sources and impedances, seen from two terminals, behaves exactly like a single voltage phasor $V_{th}$ in series with a single impedance $Z_{th}$. $V_{th}$ is the voltage across the open terminals; $Z_{th}$ is what you measure looking back in with every independent source zeroed — voltage sources replaced by a short, current sources by a break.",
                "**Norton's theorem** is the same statement turned inside out: a current source $I_n = V_{th}/Z_{th}$ in parallel with that same $Z_{th}$. Neither is an approximation. Both are exact for any linear network, at one frequency at a time.",
                "The Thévenin impedance of a divider is its two resistors *in parallel*, because zeroing the source shorts the top one to ground. That is the same $R_1 \\parallel R_2$ that set the corner frequency earlier in this course — the time constant of a node is always its capacitance times the resistance seen looking out of it.",
                "Driving a load $Z_L$ from a source $Z_{th} = R_{th} + jX_{th}$, the power in the load is greatest when $Z_L = R_{th} - jX_{th}$: the **complex conjugate**. Cancel the reactance first, so that the current is not being wasted pushing energy in and out, then match the resistance.",
                "At that match, exactly half the power leaving the source ends up in the load and the other half heats $R_{th}$. That is a ceiling on delivered power, not a target for efficiency: a mains supply is deliberately far from matched, because a 50% efficient power station is unthinkable, while an antenna or a sensor with nothing to spare is matched on purpose.",
                "A **source transformation** turns a voltage source $V$ with $Z$ in series into a current source $V/Z$ with the *same* $Z$ in parallel, and back again. The impedance never changes value in the move. Applied repeatedly it collapses a ladder from the far end without a single simultaneous equation.",
                "Equivalence is a promise about the **terminals only**. A network, its Thévenin form and its Norton form agree on every terminal voltage and current for every load, and disagree wildly about the currents and the dissipation inside. Never size a heatsink or estimate a battery’s life from an equivalent.",
            ],
            "read": [
                {
                    "title": "Two numbers behind any pair of terminals",
                    "minutes": 15,
                    "body": r'''
## The box you are not allowed to open

On the bench is a sealed box with two terminals sticking out of it. Inside could be a
single cell and a resistor; it could be a rectifier, a transformer and eleven resistors;
it could be the output of a circuit you designed last week and have already forgotten.
You are not allowed to open it. You are allowed to connect things to the terminals and
measure.

Here is the surprising claim this module rests on. Provided everything inside is
**linear** — resistors, capacitors, inductors, and sources that do not depend on the load
— no experiment you can perform at those two terminals can distinguish that box from a
single voltage source in series with a single impedance. Not a good approximation of it.
The same, exactly, for every load you will ever hang on it.

That is Thévenin's theorem, and it is the most labour-saving result in circuit analysis.
Eleven resistors become two numbers, and every question about what the box does when you
connect something to it is answered by a divider.

## The experiment that shows it

Take the box and hang a variable resistor across the terminals. Start with the resistor
very large — almost nothing flows — and work down, writing the terminal voltage $V$ and
the terminal current $I$ at each setting. Plot $V$ against $I$.

You get a straight line. Every time, for every box, as long as everything inside obeys
linear laws. It slopes downward: the more current you draw, the lower the terminal
voltage sags.

A straight line has two numbers in it, and both of them mean something.

$$V = V_{oc} - I R_{th}$$

The intercept $V_{oc}$ is where the line meets the voltage axis, at $I = 0$: the voltage
across the terminals with nothing connected. The **open-circuit voltage**. The slope is
$-R_{th}$, and the minus sign says the sag is proportional to the current drawn. Read the
equation aloud and it describes a perfect source $V_{oc}$ with a resistance $R_{th}$ in
series with it, because that is exactly what such a thing would measure.

So the equivalent is not a modelling choice or a convenient fiction. It is a restatement
of the measured line, and the line is straight because the box is linear.

## Why the line is straight

Superposition is the reason, and it is worth spending a paragraph on because it is also
the exact condition under which the theorem fails.

Drive the terminals with an external current source of $I$ amps, pushed in at the top
terminal, and ask for the terminal voltage. Superposition says: solve once with the
internal sources active and $I$ set to zero, solve again with $I$ active and every
internal source set to zero, and add. The first solve gives the open-circuit voltage,
because $I = 0$ is precisely the open-circuit condition. The second is a passive network
being driven by a current, so its answer is $-I R_{th}$, where $R_{th}$ is whatever
resistance the passive network presents. Add them and you have the straight line above,
with no assumption beyond superposition itself.

That also tells you how to compute the two numbers without doing the experiment:

**$V_{th}$ is the open-circuit voltage.** Take the terminals off, solve the network as it
stands, read the voltage where the terminals were.

**$Z_{th}$ is what the network looks like with every independent source zeroed.** Zero a
voltage source by replacing it with a short, because an ideal voltage source has no
internal impedance and a zero-volt one is a piece of wire. Zero a current source by
replacing it with a break, because an ideal current source has infinite internal
impedance and a zero-amp one passes nothing. Then reduce what remains with the series and
parallel rules.

## Worked all the way through: a T-network

A 12 V supply feeds a 1.00 kΩ resistor into a node $A$. From $A$, a 1.50 kΩ resistor runs
to ground, and a 200 Ω resistor runs out to the terminals. Three resistors, one supply,
and a question: what will a 470 Ω load see?

Start with the open-circuit voltage. With nothing connected, no current can flow in the
200 Ω resistor, so it drops nothing at all and the terminal voltage is whatever $A$ is at.
$A$ is the junction of an ordinary divider:

```
V_th   = 12 * 1500/(1000 + 1500)             = 7.200 V
```

The 200 Ω has not disappeared. It carries no current *while the terminals are open*, which
is a different statement, and it will matter in a moment.

Now the impedance. Short the 12 V supply. The 1.00 kΩ, which used to run from the supply to
$A$, now runs from ground to $A$ — so it sits in parallel with the 1.50 kΩ, which already
did. Reduce that pair, then walk out through the 200 Ω, which is in series with everything
behind it:

```
1000 || 1500 = 1000*1500/2500                = 600.0 ohm
R_th   = 200 + 600                           = 800.0 ohm
```

Two numbers, and the box is now a 7.200 V source behind 800 Ω. Hang the 470 Ω load on it:

```
I_L    = 7.200/(800 + 470) = 7.200/1270      = 5.6693 mA
V_L    = 5.6693e-3 * 470                     = 2.6646 V
```

Worth checking against the original network, because the first time you do this it does
not feel like it can be right. Solve the real circuit with the load in place. The load and
the 200 Ω are in series, and that pair is in parallel with the 1.50 kΩ:

```
200 + 470                                    = 670.0 ohm
1500 || 670 = 1500*670/2170                  = 463.13 ohm
V_A    = 12 * 463.13/(1000 + 463.13)         = 3.7984 V
V_L    = 3.7984 * 470/670                    = 2.6646 V
```

The same 2.6646 V, from a completely different piece of arithmetic. And the second
calculation has to be redone from scratch for every new load, while the first has to be
redone for none of them: change the load to 1.2 kΩ and $7.200 \times 1200/2000 = 4.320$ V
follows in one line.

## The same idea when the numbers are complex

Nothing above used the fact that the components were resistors. Replace resistance by
impedance and every step survives, one frequency at a time.

A 5.00 V RMS source at 1.00 kHz feeds a 1.00 kΩ resistor, and a 100 nF capacitor runs from
the junction to ground. The terminals are that junction — this is the low-pass filter of
Module 4, being asked a new question: what does it look like to whatever comes next?

```
omega  = 2*pi*1000                           = 6283.2 rad/s
X_C    = 1/(omega*C) = 1/(6283.2 * 100e-9)   = 1591.5 ohm
Z_C    = -j1591.5 ohm
```

The open-circuit voltage is the divider, done with impedances:

$$V_{th} = V_s\,\frac{Z_C}{R + Z_C} = \frac{V_s}{1 + j\omega RC}$$

```
omega*R*C = 6283.2 * 1000 * 100e-9           = 0.62832
1 + j0.62832  has magnitude sqrt(1.39479)    = 1.18101
|V_th| = 5.00/1.18101                        = 4.2337 V rms
angle  = -arctan(0.62832)                    = -32.14 deg
```

For the impedance, short the source. The resistor now runs from the junction to ground,
in parallel with the capacitor that was already there:

$$Z_{th} = R \parallel Z_C = \frac{R}{1 + j\omega RC}$$

```
Z_th   = 1000/(1 + j0.62832)
       = 1000*(1 - j0.62832)/1.39479
       = 717.0 - j450.5 ohm
|Z_th| = sqrt(717.0^2 + 450.5^2)             = 846.7 ohm
```

Notice the two expressions share a denominator, so $V_{th} = V_s Z_{th}/R$ — a coincidence
of this particular topology, not a general rule, but a useful arithmetic check.

Now put a 1.00 kΩ load across those terminals and predict what it gets:

```
Z_th + R_L = 1717.0 - j450.5,  magnitude    = 1775.1 ohm
its angle  = arctan(-450.5/1717.0)          = -14.70 deg
|V_L|  = 4.2337 * 1000/1775.1               = 2.3851 V rms
angle  = -32.14 - (-14.70)                  = -17.44 deg
```

Solve the loaded three-component circuit directly and you get 2.3851 V at $-17.44°$. Two
things in that answer are worth pausing on. The load has cost more than half the output —
2.385 V where 4.234 V was on offer — because the 1.00 kΩ load is comparable to the 847 Ω
the filter presents. And the phase shift has *shrunk*, from $-32.1°$ to $-17.4°$, because
the load resistance has diluted the capacitive part of $Z_{th}$. Loading a filter does not
just make it smaller; it moves its corner. With $Z_{th}$ in hand you could see that coming
without solving anything.

## The mistake, and why it is tempting

Almost every wrong $Z_{th}$ comes from the same place: **zeroing a source is replacing it,
not deleting it.** People reach for the eraser, take the 12 V supply off the drawing
altogether, and are left with a 1.00 kΩ resistor dangling from $A$ with nothing on its far
end. It then carries no current, so it contributes nothing, and $R_{th}$ comes out as
$200 + 1500 = 1700$ Ω instead of 800 Ω. That is more than double, and every prediction
built on it is wrong.

It is tempting because "turn the source off" sounds like "take it out", and because for a
*current* source taking it out is exactly right. The way not to get caught is to stop
memorising the pair of rules and re-derive them from one sentence each time: an ideal
voltage source with zero volts across it behaves like a wire; an ideal current source with
zero amps through it behaves like a gap. Set the value to zero, keep the component.

The second most common error is subtler. Having found $V_{th}$, people compute $Z_{th}$
without removing the load, which quietly includes the load in the source impedance and
then divides by it a second time. $Z_{th}$ is a property of the box alone. The load is
never part of it.

## Where this stops working

**Linearity is the whole condition.** A network containing a diode, a transistor, or
anything whose behaviour depends on how hard you drive it has no straight $V$–$I$ line, so
it has no Thévenin equivalent. What replaces it is a *small-signal* equivalent: linearise
about an operating point and the theorem applies to small departures from it, which is how
every transistor amplifier you will meet is analysed.

**One frequency at a time.** $Z_{th}$ above was $717 - j450$ Ω at 1 kHz and is something
else at 2 kHz. For a network of resistors alone the number is the same everywhere; the
moment a reactance appears, the equivalent is a snapshot. A broadband claim needs the
whole function $Z_{th}(\omega)$, not a number.

**The equivalent gets the terminals right and the inside wrong.** This one catches people
out badly. In the worked T-network with its 470 Ω load, the equivalent says the source
delivers $7.200 \times 5.6693\,\text{mA} = 40.8$ mW. The real circuit's 12 V supply is
delivering $(12 - 3.7984)/1000 = 8.2016$ mA, which is $12 \times 8.2016\,\text{mA} = 98.4$
mW. Both are correct about the load's 15.1 mW. Neither the internal currents nor the
internal dissipation of a Thévenin equivalent has anything to do with the real network's,
and using one to size a heatsink or estimate a battery's life is a real mistake with real
smoke at the end of it.

**Dependent sources need more care.** A source controlled by a voltage or current
elsewhere in the network is still linear, so the equivalent exists — but you cannot zero
it, because it is not independent. The method that still works is to apply a test source
at the terminals and measure what flows, which is the technique the next module of any
electronics course leans on constantly, and the one the resistance question in this
module's ladder walks through.
''',
                },
                {
                    "title": "Norton, and moving a source about",
                    "minutes": 14,
                    "body": r'''
## The same box, described the other way round

The Thévenin equivalent is a voltage source with something in series. There is a second
description of the identical box: a **current** source with something in parallel. It is
Norton's theorem, it is not an alternative theory, and it contains exactly the same
information.

The quickest way to see that they are the same is to ask each of them the two questions
that pin a straight line down.

Short the terminals of a Thévenin equivalent. The whole $V_{th}$ appears across $Z_{th}$,
so the current that flows out is $V_{th}/Z_{th}$. Open the terminals of a Norton
equivalent and all of $I_n$ has to go through $Z_n$, so the voltage that appears is
$I_n Z_n$. Match the two boxes at both ends of the line:

$$I_n = \frac{V_{th}}{Z_{th}}, \qquad Z_n = Z_{th}, \qquad V_{th} = I_n Z_n$$

The impedance is the *same number* in both descriptions — that is the part people
misremember, and there is no scaling factor lurking anywhere. The source changes its
character; the impedance does not move.

So a box has three equally complete descriptions: the pair $(V_{th}, Z_{th})$, the pair
$(I_n, Z_n)$, and the two measurements $V_{oc}$ and $I_{sc}$ that you could actually make
on the bench. Any one gives the other two, and $Z_{th} = V_{oc}/I_{sc}$ is the cleanest
laboratory definition of the impedance there is, because it needs no access to the inside
at all.

The Norton form is not merely the Thévenin form written backwards. For some devices it is
the natural description and the Thévenin form is the awkward one. A photodiode delivers a
current proportional to the light falling on it, very nearly regardless of the voltage
across it, with a large shunt resistance beside it: that is a Norton source as it stands,
and forcing it into Thévenin form gives an enormous voltage behind an enormous resistance,
correct and impossible to think with. The same goes for a transistor's collector, a
current-mirror output, and a current-output digital-to-analogue converter. Choose the form
that matches the physics and the arithmetic gets shorter.

## Source transformation: an algebra you perform on the drawing

The equivalence is more useful as a *move* than as a fact. Anywhere in a schematic you
find a voltage source with an impedance in series, you may cross it out and draw a current
source of $V/Z$ with that same $Z$ in parallel — and the rest of the circuit cannot tell.
Anywhere you find a current source with an impedance in parallel, you may go the other
way.

Why bother? Because parallel things combine, and after a transformation two impedances
that were nowhere near each other often end up in parallel. Repeat, and a ladder collapses
from the far end without a single simultaneous equation.

Take the T-network from the previous reading: 12 V behind 1.00 kΩ into node $A$, 1.50 kΩ
from $A$ to ground, 200 Ω from $A$ out to the terminals.

```
12 V behind 1.00 k        ->  12/1000 = 12.000 mA  beside 1.00 k
1.00 k now parallel 1.50 k ->  1000*1500/2500 = 600.0 ohm, current unchanged
12.000 mA beside 600 ohm  ->  12.000e-3 * 600 = 7.200 V  behind 600 ohm
add the 200 ohm in series ->  7.200 V behind 800.0 ohm
```

Four lines, no algebra, and it lands on the 7.200 V and 800 Ω that the open-circuit and
zeroed-source method produced. Each step is a legal move rather than a calculation, which
is why this route is much harder to get wrong on a long ladder.

## Worked: two supplies feeding one node

Source transformation earns its keep when there is more than one source, because current
sources in parallel simply add and voltage sources in series with different resistances do
not.

A 9.00 V supply behind 1.00 kΩ and a 5.00 V supply behind 2.00 kΩ both feed the same node,
where a 470 Ω load sits. Nodal analysis would handle it, but watch the transformation do it
without writing an equation:

```
9.00 V behind 1.00 k      ->  9.000 mA beside 1.00 k
5.00 V behind 2.00 k      ->  2.500 mA beside 2.00 k
two current sources in parallel  ->  9.000 + 2.500 = 11.500 mA
two resistances in parallel      ->  1000*2000/3000 = 666.67 ohm

so  I_n = 11.500 mA,  Z_n = 666.67 ohm
    V_th = 11.500e-3 * 666.67                = 7.6667 V
```

The load now follows in one line:

```
I_L  = 7.6667/(666.67 + 470) = 7.6667/1136.67 = 6.7449 mA
V_L  = 6.7449e-3 * 470                        = 3.1701 V
```

And the confirmation, by the node equation you did not have to write:

```
(9 - V)/1000 + (5 - V)/2000 = V/470

multiply through by 2000:
2*(9 - V) + (5 - V) = 2000*V/470 = 4.25532*V
18 - 2*V + 5 - V                 = 4.25532*V
23                               = 7.25532*V
V = 23/7.25532                   = 3.1701 V
```

The same number. Note also what the equivalent tells you at a glance and the node equation
does not: the two supplies together behave like a single 7.667 V supply behind 667 Ω, so a
load much larger than 667 Ω will see nearly 7.667 V and a load much smaller will see almost
none of it. That is the kind of thing you want to know before choosing a load, not after.

## Two measurements, and no theory at all

Everything above assumed you could see inside the box. Very often you cannot, and it turns
out you do not need to. Measure the open-circuit voltage with a meter that draws almost
nothing; measure the short-circuit current with an ammeter straight across the terminals;
divide one by the other.

For the T-network we happen to know what is inside, so both readings can be predicted
rather than taken — which is the only way to check that the method gives the right answer
at all:

```
V_oc   = 12.0 * 1500/2500                     = 7.200 V

now short the terminals, which puts R3 across R2:
1500 || 200 = 1500*200/1700                   = 176.47 ohm
V_A    = 12.0 * 176.47/(1000 + 176.47)        = 1.8000 V
I_sc   = 1.8000/200                           = 9.000 mA

Z_th   = V_oc/I_sc = 7.200/9.000e-3           = 800.0 ohm
```

and the box has been characterised without a schematic, a component value, or a single
equation about its insides. That is the practical reason these theorems are taught at all:
the network you most often need to reduce is one you did not design.

Two cautions, both of which have cost people an afternoon. A voltmeter that draws
appreciable current is not measuring $V_{oc}$, it is measuring a loaded terminal — put a
10 MΩ meter on a network whose $Z_{th}$ is 10 MΩ and it reads exactly half the truth, with
no indication on the display that anything is wrong. And short-circuiting a real source to
find $I_{sc}$ is defensible only when the source can survive it, which a bench supply, a
battery and a mains transformer cannot. The safe alternative is to load it with a known
resistor $R_L$, read the terminal voltage $V_L$, and solve

$$Z_{th} = R_L\,\frac{V_{oc} - V_L}{V_L}$$

which is the same information with nothing pushed to a limit. With $R_L = 470$ Ω on the
T-network, $V_L$ would read 2.6646 V and $470 \times (7.200 - 2.6646)/2.6646 = 800.0$ Ω
comes straight back out.

## What stays the same, and what does not

Two things are preserved by a source transformation and by the Thévenin–Norton equivalence,
and everything else is fair game.

Preserved: the terminal voltage and the terminal current, for every possible load, at the
frequency you did the arithmetic at.

Not preserved: everything inside. Leave the terminals of the T-network open and count the
watts three ways. The real circuit draws $12/2500 = 4.80$ mA through its two resistors and
burns $12 \times 4.80\,\text{mA} = 57.6$ mW. Its Thévenin equivalent draws nothing at all
and burns zero. Its Norton equivalent pushes all $9.00$ mA through 800 Ω and burns
$(9.00\,\text{mA})^2 \times 800 = 64.8$ mW. Three different answers, all correct, because
none of them was ever a claim about the inside of the box. The equivalents agree with each
other and with reality on the only thing they promised: the terminals, where all three give
7.200 V and no current.

This is not a defect to be worked around. It is what "equivalent at the terminals" means,
and stating it plainly is cheaper than discovering it when a thermal calculation comes out
wrong by a factor of two.

## The mistake, and why it is tempting

The common error in a source transformation is to change the impedance along with the
source: to halve it, or double it, or take its reciprocal, on a vague feeling that turning
a voltage source into a current source must do *something* to the resistor beside it. It
does not. $Z_n = Z_{th}$, exactly, always. The feeling comes from the fact that the
source's number genuinely does change — 12 V becomes 12 mA — so the eye expects the other
number to move as well. The defence is to notice that the impedance is the one symbol that
appears unaltered on both sides of the equivalence, and that it has to be, because it is
the slope of a line that neither description is allowed to change.

The second error is transforming across a node whose voltage the question asks about. The
move is legal and the arithmetic comes out right, but the answer has become unobtainable,
because the node was consumed on the way. If a question asks for the voltage at node $A$,
do not open by absorbing node $A$.

A smaller one, worth naming because it produces a sign error rather than a wrong
magnitude: the direction of $I_n$. A Norton source drives its whole current through its
own parallel impedance when the terminals are open, and the voltage that appears must be
the $V_{th}$ the other description promised, with the same polarity. Draw the arrow so
that the open-circuit test reproduces $V_{th}$ and the sign looks after itself.

## Where the transformation stops

**An ideal source with nothing in series or parallel cannot be transformed.** A perfect
voltage source alone has $Z_{th} = 0$, so its Norton current would be $V/0$ — undefined,
and rightly so, because no finite current source in parallel with anything can hold a node
at a fixed voltage against every load. Symmetrically, an ideal current source alone has
$Z_{th} = \infty$ and no Thévenin voltage exists. In practice every real source has
*something* in series or parallel, and the transformation needs you to find it and use it.

**The impedance has to be genuinely in series or in parallel.** A resistor that merely
looks adjacent on the drawing, but has a third connection tapped off between it and the
source, is not in series with that source, and transforming across it changes the circuit.
The test is whether the same current necessarily flows through both — not whether they are
drawn next to each other.

**The collapsed nodes stop existing.** After transforming the T-network you can no longer
ask what voltage node $A$ sits at, because there is no longer an $A$: it has been absorbed.
If the question is about an internal node, do the reduction from the other end, or do not
do it at all.

**And, as ever, one frequency at a time.** $I_n = V_{th}/Z_{th}$ is a complex division, so
the Norton current has a phase of its own, generally different from the Thévenin voltage's.
Converting between the two forms at a single frequency is exact; carrying one form's number
to a different frequency is not.
''',
                },
                {
                    "title": "What the load should be",
                    "minutes": 16,
                    "body": r'''
## Turning the knob

You have a source you cannot change — a photodiode, a piezo pickup, a thermocouple, an
antenna, the output of somebody else's box — and you get to choose the one thing hanging on
it. Somewhere in that choice there is the most power you will ever get out. This reading is
about where it is, how much it is, and the very large number of situations in which
deliberately missing it is the right engineering.

Model the source as the previous readings say you may: a voltage $V$ behind a resistance
$R_{th}$, with the reactance dealt with separately later. Put a resistance $R_L$ across it
and turn the knob.

## Both ends of the range give you nothing

Turn $R_L$ all the way up, to an open circuit. The terminal voltage is the largest it will
ever be — the full $V$ — and the current is zero, so the power is zero. All voltage, no
current.

Turn $R_L$ all the way down, to a short. The current is the largest it will ever be,
$V/R_{th}$, and the voltage across the load is zero, so the power is zero again. All
current, no voltage.

Power is a product, both factors are being traded against each other, and both extremes
kill it. There is a maximum in between, and it is not at either end of anyone's intuition.

## Finding it

One loop, two resistances in series, so one current:

$$I = \frac{V}{R_{th} + R_L}, \qquad P_L = I^2 R_L = \frac{V^2 R_L}{(R_{th} + R_L)^2}$$

Differentiate with respect to $R_L$ and set it to zero. By the quotient rule the numerator
of $dP/dR_L$ is

$$V^2\left[(R_{th} + R_L)^2 - R_L \cdot 2(R_{th} + R_L)\right]
 = V^2 (R_{th} + R_L)\left[R_{th} - R_L\right]$$

which vanishes when $R_L = R_{th}$. Substituting back,

$$P_{max} = \frac{V^2 R_{th}}{(2R_{th})^2} = \frac{V^2}{4R_{th}}$$

and since the two resistances are equal and carry the same current, the source's own
resistance is dissipating exactly the same amount. Half in, half out.

## Worked: a table for the T-network

The network from the earlier readings reduced to $V_{th} = 7.200$ V behind
$R_{th} = 800$ Ω. Here is what a load actually gets, in milliwatts, at seven settings a
factor of two apart:

```
R_L (ohm)    I = 7.200/(800+R_L)      P = I^2 * R_L
   100          8.000 mA                 6.400 mW
   200          7.200 mA                10.368 mW
   400          6.000 mA                14.400 mW
   800          4.500 mA                16.200 mW
  1600          3.000 mA                14.400 mW
  3200          1.800 mA                10.368 mW
  6400          1.000 mA                 6.400 mW
```

and the formula agrees: $P_{max} = 7.200^2/(4 \times 800) = 51.84/3200 = 16.200$ mW.

Read down the table and then back up it. It is symmetric — not about $R_L$, but about the
*ratio* $R_L/R_{th}$. A load of half the source resistance and a load of twice it receive
the identical 14.400 mW, which is $8/9$ of the maximum, or 0.51 dB down. A factor of four
either way still leaves you 64% of it. This flatness is the practical headline of the whole
subject: getting a match roughly right is nearly as good as getting it exactly right, and
anyone quoting resistances to four figures for a power match is polishing something that
does not shine.

The flatness has a limit, though. A load a factor of eight out — 100 Ω against 800 Ω — has
dropped to 6.400 mW, 40% of what was available, which is 4 dB. Order of magnitude matters;
the last 20% does not.

## Alternating current: two jobs, in this order

Now let the source impedance be complex, $Z_{th} = R_{th} + jX_{th}$, and let the load be
$Z_L = R_L + jX_L$. The current magnitude in the loop is

$$|I| = \frac{|V|}{\sqrt{(R_{th}+R_L)^2 + (X_{th}+X_L)^2}}$$

and the power in the load is still $|I|^2 R_L$, because only resistance dissipates.

Look at where $X_L$ appears: in the denominator, added to $X_{th}$, and nowhere else. It
can only make $|I|$ smaller — unless it is chosen to *cancel* $X_{th}$, in which case the
sum is zero and the denominator is as small as it can be. So the first job is settled
before any thought about resistance: choose $X_L = -X_{th}$. A reactance in the loop makes
current slosh energy in and out without ever dissipating it, and the price is paid in
$|Z|$, which throttles the current that could have been doing work.

With the reactances cancelled, what remains is the purely resistive problem already solved,
so $R_L = R_{th}$. Together:

$$Z_L = R_{th} - jX_{th} = Z_{th}^{*}$$

the **complex conjugate**. And $P_{max} = |V|^2/(4R_{th})$, with $R_{th}$ the *real part* —
the reactance has vanished from the answer entirely, which it should, since it has been
cancelled.

## Worked: three loads on the same source

A 5.00 V RMS source at 2.00 kHz sits behind 100 Ω and 20.0 mH.

```
omega  = 2*pi*2000                            = 12566 rad/s
X_L    = omega * L = 12566 * 0.0200           = 251.33 ohm
Z_th   = 100 + j251.33 ohm
|Z_th| = sqrt(100^2 + 251.33^2)               = 270.49 ohm
```

**(a) A 100 Ω resistor, matching the real part and nothing else.**

```
Z_loop = 200 + j251.33,  |Z| = sqrt(40000 + 63165) = 321.19 ohm
I      = 5.00/321.19                          = 15.567 mA
P      = I^2 * 100                            = 24.233 mW
```

**(b) A 270.49 Ω resistor — the best a single resistor can do.**

Repeat the maximisation with the reactance stuck in the loop: $P = V^2 R_L /
[(R_{th}+R_L)^2 + X_{th}^2]$, and $dP/dR_L = 0$ now gives $R_L^2 = R_{th}^2 + X_{th}^2$,
that is $R_L = |Z_{th}|$. Not $R_{th}$.

```
Z_loop = 370.49 + j251.33, |Z| = 447.69 ohm
I      = 5.00/447.69                          = 11.169 mA
P      = I^2 * 270.49                         = 33.739 mW
```

**(c) 100 Ω in series with a capacitor that cancels the coil — the conjugate.**

```
C      = 1/(omega^2 * L) = 1/(12566^2 * 0.02) = 316.6 nF
X_C    = 1/(omega*C)                          = 251.33 ohm, and it cancels X_L
Z_loop = 200 + j0                             = 200 ohm
I      = 5.00/200                             = 25.000 mA
P      = I^2 * 100                            = 62.500 mW
```

Line the three up. The conjugate gives 2.58 times the power of the naive real-part match
and 1.85 times the best that any resistor alone can manage — 4.1 dB and 2.7 dB
respectively, bought with one capacitor.

There is a detail in (b) worth keeping. The load voltage there is
$11.169\,\text{mA} \times 270.49 = 3.021$ V, while at the conjugate match it is only
$25.000\,\text{mA} \times 100 = 2.500$ V. The arrangement with the **larger voltage across
the load** delivers **less power to it**. If you have been quietly using "biggest output
voltage" as a proxy for "most power", this is the example that breaks the habit.

## Finding the match without knowing what is inside

The whole procedure can be run from outside the box, which is worth knowing, because that
is usually where you are standing.

Measure the open-circuit voltage. Then put a variable resistor across the terminals and
turn it until the terminal voltage falls to exactly half of that. At that setting the load
and the source resistance are dividing the voltage equally, so they are equal, and you have
found $R_{th}$ by adjustment rather than by analysis. On the T-network: $V_{oc} = 7.200$ V,
and the load that brings the terminals to 3.600 V is 800 Ω — the same 800 Ω that shorting
the supply and reducing the network gave.

With a complex $Z_{th}$ there is one more knob, and the order matters. Put a variable
reactance in series with the load and adjust it for maximum delivered power first: the best
reactance does not depend on the load resistance at all, so that adjustment is finished the
moment it is made. Only then set the resistance by the half-voltage test, which is
meaningful only once the loop is real. Doing it in the other order also converges, but it
has to be iterated, because the best resistance is $\sqrt{R_{th}^2 + X_{net}^2}$ and moves
every time the leftover reactance does.

The half-voltage test carries the same caveat as everything else here: it is a statement
about a *linear* source. Load a battery until its terminal voltage halves and you have not
measured its internal resistance; you have measured the chemistry giving up.

## The mistake people actually make

Two of them, and they pull in opposite directions.

The first is matching the *magnitude* when a conjugate was available. Case (b) is not a
blunder — it is genuinely optimal if the load must be a bare resistor — but reaching for
$|Z_L| = |Z_{th}|$ when you are free to add a capacitor leaves most of the available power
on the table. The tempting part is that $|Z|$ is the number that appears in Ohm's law for
magnitudes, so it is the number in front of you.

The second, and much more expensive, is believing that matching is what you should always
be doing. It is a phrase everyone has heard — "impedance matching" — and datasheets do
quote output impedances, so it is easy to conclude that an amplifier should be matched to
its loudspeaker. It should not, and no amplifier ever built has been. A power amplifier is
designed with an output impedance of a small fraction of an ohm into an 8 Ω speaker.
Matching it at 8 Ω would burn half the output stage's power inside the amplifier, halve the
sensible power rating, and destroy the damping that keeps the cone from continuing to move
after the signal has stopped.

The distinction to hold on to: **maximum power transfer is what you do when the source
impedance is fixed by physics and cannot be lowered.** An antenna, a piezo crystal, a
photodiode, a transistor's output at radio frequencies — for these, an unmatched load does
not buy you efficiency, it buys you less signal, and there was not much to begin with. When
you *can* choose the source impedance, make it small. Then the load takes nearly all the
voltage, the source burns almost nothing, and the efficiency is high precisely because you
are nowhere near a match.

## Where it stops holding

**Efficiency is 50% at the match, and that is often unacceptable.** A power station matched
to the national grid would burn half its output in its own windings. A battery matched to
its load would halve its run time and cook itself. Anywhere energy is expensive or heat is
awkward, the design target is a low source impedance and a load far above it.

**On a transmission line, "matching" means something else.** Above the frequency where a
cable's length is a noticeable fraction of a wavelength, the thing you match to is the
line's characteristic impedance, which is a real number set by the cable's geometry and is
not a Thévenin resistance you could measure with an ohmmeter. The purpose there is to stop
reflections — a mismatch sends part of the wave back down the cable — and the tolerances
are far tighter than the flat power curve above would suggest, because reflections, not
watts, are what is being controlled.

**Noise matching is a different optimum.** A low-noise amplifier has a source impedance at
which its noise figure is best, and it is generally not the conjugate of its input
impedance. Designing the front end of a radio means choosing which of the two to hit, and
usually compromising.

**A non-linear source has no fixed $R_{th}$ to match.** A solar panel's $V$–$I$ curve is
nowhere near a straight line, so there is no single Thévenin resistance; the maximum power
point moves with illumination and temperature, and the answer is a tracking algorithm that
hunts for it continuously rather than a resistor chosen once.

**And the match is a single-frequency statement.** The capacitor in case (c) cancels 20 mH
at 2 kHz and at no other frequency. An octave down, the coil's reactance has halved to
125.7 Ω while the capacitor's has doubled to 502.7 Ω, so instead of cancelling they leave
377 Ω of net capacitive reactance in the loop and the delivered power falls away — which is
exactly what the build in this module asks you to observe rather than take on trust.
''',
                },
            ],
            "numeric": [
                {
                    "title": "The voltage with nothing attached",
                    "minutes": 6,
                    "brief": r'''
First rung, and it is deliberately one step. The Thévenin voltage of a network is defined
as the voltage across its terminals with *nothing connected there* — so there is no load to
account for, no current leaving the junction, and the divider you already know is undisturbed.
''',
                    "prompt": "What is the Thévenin voltage of this network at the probe?",
                    "note": "Give the answer in volts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 15},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 2200},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "r2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 3300},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "15.0 V"},
                        {"label": "Series resistor", "value": "2.20 kΩ"},
                        {"label": "Shunt resistor", "value": "3.30 kΩ"},
                    ],
                    "aside": "The probe is the terminal pair, and nothing is attached to it. That is the "
                             "whole content of the word *open-circuit*: no current is being drawn, so the "
                             "divider is carrying only its own current.",
                    "answer": 9.0,
                    "tol": 0.06,
                    "unit": "V",
                    # The probe sits on the open terminals, so the solved node voltage there is the
                    # definition of V_th with nothing restated from the prompt.
                    "check": r'''
c.assert(c.count('R') === 2, "two resistors and nothing on the terminals");
return c.vout();
''',
                    "hint": "One divider: the shunt resistor's share of the supply is "
                            "$V_s R_2/(R_1 + R_2)$.",
                    "wrong": "6.00 V is $15 \\times 2200/5500$, the *series* resistor's share — the ratio "
                             "upside down, and the two always add to the supply, so seeing 6.00 and 9.00 "
                             "on the same page is a hint that one of them is the other one's complement. "
                             "15.0 V is the supply itself, which the terminals would show only if the "
                             "2.20 kΩ were a piece of wire. 7.50 V is half the supply, correct for two "
                             "equal resistors and for no other pair.",
                    "why": r'''
```
R1 + R2   = 2200 + 3300                        = 5500 ohm
V_th      = 15.0 * 3300/5500                   = 9.000 V
```

Nothing subtler is going on, and that is the point of stating it as a Thévenin voltage
rather than as a divider output: the definition of $V_{th}$ is *the open-circuit voltage*,
and open-circuit means the junction is free to sit wherever the divider puts it.

The moment anything is connected there the number changes, and it changes by an amount the
divider alone cannot tell you. That is the next rung.

One thing to file away for the rung after that: the current circulating here is
$15.0/5500 = 2.727$ mA, and it flows whether or not anything is connected. A divider used
as a reference voltage is burning that current continuously, which is why the resistor
values in a battery-powered design are chosen large and the loading problem that follows
is worse.
''',
                },
                {
                    "title": "What the load does to it",
                    "minutes": 9,
                    "brief": r'''
Same network, with a 1.00 kΩ load hung on the terminals. The junction cannot stay at 9.00 V
any more, because the load is drawing current and the source has resistance of its own.

Two routes get you there. Reduce the network to $V_{th}$ and $R_{th}$ and treat what is
left as one loop; or work out the parallel combination and redo the divider from scratch.
Do it whichever way you like, but notice which of the two you would rather repeat for a
second load value.
''',
                    "prompt": "What current flows in the 1.00 kΩ load?",
                    "note": "Give the answer in milliamps, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 15},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 2200},
                            {"id": "out", "kind": "OUT", "x": 9, "y": 3, "rot": 0, "value": 0},
                            {"id": "r2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 3300},
                            {"id": "rl", "kind": "R", "x": 12, "y": 4, "rot": 1, "value": 1000},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                            {"a": [12, 5], "b": [12, 7]},
                            {"a": [12, 7], "b": [9, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "15.0 V"},
                        {"label": "Series resistor", "value": "2.20 kΩ"},
                        {"label": "Shunt resistor", "value": "3.30 kΩ"},
                        {"label": "Load", "value": "1.00 kΩ"},
                    ],
                    "aside": "The probe sits on the terminals, so it is reading the load's own voltage. "
                             "Ohm's law turns that into the load current in one step, whichever route you "
                             "took to get the voltage.",
                    "answer": 3.879,
                    "tol": 0.03,
                    "unit": "mA",
                    # Solved rather than restated: the probe reads the loaded terminal voltage out of
                    # the DC solution and the load resistance comes from the netlist, so editing any
                    # component moves the measured answer.
                    "check": r'''
c.assert(c.count('R') === 3, "two resistors in the source network and one load");
var RL = c.values('R')[2];
return 1000 * c.vout() / RL;
''',
                    "hint": "$R_{th}$ is the two source resistors in parallel, because shorting the supply "
                            "puts them both between the junction and ground. Then one loop: "
                            "$I = V_{th}/(R_{th} + R_L)$.",
                    "wrong": "9.00 mA is $V_{th}/R_L$ with the source's own 1320 Ω left out — the answer "
                             "you get by believing the junction stays at 9.00 V once it is loaded. "
                             "6.82 mA is $V_{th}/R_{th}$, the short-circuit current, which is what would "
                             "flow if the load were a piece of wire. 2.727 mA is the current the "
                             "unloaded divider draws from the supply, which is a real current in this "
                             "circuit but not the one in the load.",
                    "why": r'''
By the equivalent:

```
V_th   = 15.0 * 3300/5500                      = 9.000 V
R_th   = 2200 || 3300 = 2200*3300/5500         = 1320.0 ohm
I_L    = 9.000/(1320 + 1000) = 9.000/2320      = 3.8793 mA
V_L    = 3.8793e-3 * 1000                      = 3.8793 V
```

And from scratch, with no equivalent anywhere in it:

```
3300 || 1000 = 3300*1000/4300                  = 767.44 ohm
V_L    = 15.0 * 767.44/(2200 + 767.44)         = 3.8793 V
I_L    = 3.8793/1000                           = 3.8793 mA
```

Same answer, and the second route is not much longer — for *one* load. Ask for a second
value and the first route reuses 9.000 V and 1320 Ω unchanged while the second starts
again from the parallel combination. That asymmetry is the entire practical case for
Thévenin.

Look at what the load has cost: the terminals were offering 9.000 V and are delivering
3.879 V, a drop of 57%. A 1.00 kΩ load is small compared with the 1320 Ω the network
presents, and a load smaller than the source impedance always takes most of the voltage
away. Had the load been 13.2 kΩ — ten times $R_{th}$ — the terminal voltage would have been
$9.000 \times 13200/14520 = 8.182$ V, only 9% down.

This is the reason a divider makes a poor reference for anything that draws current, and
the reason the first question to ask about any voltage on a schematic is what impedance is
behind it.
''',
                },
                {
                    "title": "Looking back in",
                    "minutes": 11,
                    "brief": r'''
A different network, and a different question: not what it produces, but what it *is*, as
seen from the terminals.

The network in question is a 12.0 V supply feeding a 1.00 kΩ resistor into a node, with a
1.50 kΩ resistor from that node to ground and a 200 Ω resistor running out to the
terminals. What is drawn below is that network **with its supply already zeroed** — the
ideal 12 V source replaced by the short circuit it becomes when its value is set to zero —
and a 1.00 V test source applied at the terminals so that the resistance can be measured
rather than argued about.

An ohmmeter does exactly this: it applies a known voltage and reports the ratio of that
voltage to the current it draws.
''',
                    "prompt": "What Thévenin resistance does this network present at its terminals?",
                    "note": "Give the answer in ohms, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vt", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "out", "kind": "OUT", "x": 4, "y": 3, "rot": 0, "value": 0},
                            {"id": "r3", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 200},
                            {"id": "r1", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 12, "y": 4, "rot": 1, "value": 1500},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                            {"a": [12, 5], "b": [12, 7]},
                            {"a": [12, 7], "b": [9, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Test source", "value": "1.00 V, applied at the terminals"},
                        {"label": "Series resistor out to the terminals", "value": "200 Ω"},
                        {"label": "The supply's own resistor, far end now shorted to ground", "value": "1.00 kΩ"},
                        {"label": "The shunt resistor", "value": "1.50 kΩ"},
                    ],
                    "aside": "Two resistors now run from the inner node to ground: the 1.50 kΩ that always "
                             "did, and the 1.00 kΩ whose far end used to be the 12 V supply and is now the "
                             "short that replaced it.",
                    "answer": 800.0,
                    "tol": 5.0,
                    "unit": "Ω",
                    # The resistance is measured, not asserted: the solver reports the current the test
                    # source has to supply, and the ratio of the source's own value to that current is
                    # the definition of the resistance seen at the terminals.
                    "check": r'''
c.assert(c.count('V') === 1 && c.count('R') === 3, "one test source and three resistors");
var i = Math.abs(c.dc().currents['vt']);
c.assert(i > 0, "the test source is delivering no current, so nothing is connected to it");
return c.values('V')[0] / i;
''',
                    "hint": "Work inwards from the terminals. The 200 Ω is in series with whatever is "
                            "behind it; behind it, two resistors run from the same node to the same "
                            "ground.",
                    "wrong": "1.70 kΩ is $200 + 1500$, which is what you get by *deleting* the 12 V supply "
                             "instead of shorting it — with a gap where it was, the 1.00 kΩ dangles and "
                             "carries nothing. 2.70 kΩ adds all three resistors in series, which no "
                             "arrangement of this network justifies. 150 Ω is $200 \\parallel 600$, the "
                             "answer with the series and parallel steps swapped: the 200 Ω is the only "
                             "path out to the terminals, so it cannot be in parallel with anything.",
                    "why": r'''
Working inwards from the terminals:

```
1000 || 1500 = 1000*1500/2500                  = 600.0 ohm
R_th   = 200 + 600                             = 800.0 ohm
```

and the measurement the schematic performs confirms it:

```
I_test = 1.00/800.0                            = 1.250 mA
R_th   = 1.00/1.250e-3                         = 800.0 ohm
```

The 1.00 kΩ is in parallel with the 1.50 kΩ *because the supply was replaced by a short*.
Its far end used to be held at 12 V; now it is held at 0 V, and a resistor between the
inner node and ground is a resistor between the inner node and ground regardless of which
piece of copper is doing the holding. That is the single step this question exists to
drill, and getting it wrong gives 1.70 kΩ, which is more than twice the right answer.

Notice what did not appear anywhere above: the 12 V. $R_{th}$ is a property of the passive
network, and the supply could have been 12 V or 1200 V without moving it. The supply's
value belongs to the *other* number, and for completeness that one is

```
V_th   = 12.0 * 1500/(1000 + 1500)             = 7.200 V
```

because with the terminals open the 200 Ω carries no current and drops nothing. So the
whole network, from outside, is 7.200 V behind 800 Ω — and the equivalent Norton
description is $7.200/800 = 9.00$ mA beside the same 800 Ω. The next rung spends that
equivalent.
''',
                },
                {
                    "title": "The most it can give",
                    "minutes": 11,
                    "brief": r'''
The same network as the rung before — 12.0 V behind 1.00 kΩ into a node, 1.50 kΩ from that
node to ground, 200 Ω out to the terminals — now with a load fitted, and the load has been
chosen to be exactly the 800 Ω the terminals present.

So this is the maximum-power case, and there are two ways to the answer: reduce to the
equivalent and use $V_{th}^2/(4R_{th})$, or solve the four-resistor circuit as drawn and
compute $V_L^2/R_L$. They must agree, and it is worth confirming that they do.
''',
                    "prompt": "How much power does the 800 Ω load dissipate?",
                    "note": "Give the answer in milliwatts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 9, "y": 4, "rot": 1, "value": 1500},
                            {"id": "r3", "kind": "R", "x": 12, "y": 3, "rot": 0, "value": 200},
                            {"id": "out", "kind": "OUT", "x": 14, "y": 3, "rot": 0, "value": 0},
                            {"id": "rl", "kind": "R", "x": 14, "y": 4, "rot": 1, "value": 800},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [11, 3]},
                            {"a": [9, 5], "b": [9, 7]},
                            {"a": [9, 7], "b": [3, 7]},
                            {"a": [13, 3], "b": [14, 3]},
                            {"a": [14, 5], "b": [14, 7]},
                            {"a": [14, 7], "b": [9, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V"},
                        {"label": "Supply's series resistor", "value": "1.00 kΩ"},
                        {"label": "Shunt resistor", "value": "1.50 kΩ"},
                        {"label": "Resistor out to the terminals", "value": "200 Ω"},
                        {"label": "Load", "value": "800 Ω"},
                    ],
                    "aside": "The probe reads the load's own voltage, so $P = V_L^2/R_L$ finishes the job "
                             "from there. Whether you find $V_L$ through the equivalent or by collapsing "
                             "the four resistors makes no difference to the answer.",
                    "answer": 16.2,
                    "tol": 0.15,
                    "unit": "mW",
                    # Wholly solver-driven: the load voltage comes from the DC solution and the load
                    # resistance from the netlist, so no constant from the prompt is repeated here.
                    "check": r'''
c.assert(c.count('R') === 4, "three resistors in the source network and one load");
var RL = c.values('R')[3];
var v = c.vout();
return 1000 * v * v / RL;
''',
                    "hint": "$V_{th} = 7.200$ V and $R_{th} = 800$ Ω from the previous rung. With "
                            "$R_L = R_{th}$ the load takes exactly half of $V_{th}$.",
                    "wrong": "64.8 mW is $V_{th}^2/R_{th}$ — the power that would flow if the whole 7.200 V "
                             "landed on the load, which ignores that the source resistance is taking half "
                             "of it. 32.4 mW is the *total* power leaving the equivalent source, of which "
                             "the load gets half and the 800 Ω of source resistance gets the other half. "
                             "90.0 mW is what the real 12 V supply is delivering, most of which never "
                             "reaches the terminals at all.",
                    "why": r'''
Through the equivalent:

```
V_th   = 12.0 * 1500/2500                      = 7.200 V
R_th   = 200 + (1000 || 1500) = 200 + 600      = 800.0 ohm
R_L = R_th, so the load takes half of V_th:
V_L    = 7.200/2                               = 3.600 V
P_L    = 3.600^2/800                           = 16.200 mW
```

and the closed form agrees, as it must:

```
P_max  = V_th^2/(4 R_th) = 51.84/3200          = 16.200 mW
```

Now the same thing from the drawn circuit, with no equivalent used anywhere:

```
200 + 800                                      = 1000 ohm
1500 || 1000 = 1500*1000/2500                  = 600.0 ohm
V_A    = 12.0 * 600/(1000 + 600)               = 4.500 V
V_L    = 4.500 * 800/1000                      = 3.600 V
P_L    = 3.600^2/800                           = 16.200 mW
```

Two routes, one answer. The equivalent is not doing anything the circuit does not already
do; it is doing it in fewer steps and in a form you can reuse.

The part worth sitting with is the efficiency. The 12 V supply is delivering
$(12.0 - 4.500)/1000 = 7.500$ mA, so it is producing $12.0 \times 7.500\,\text{mA} = 90.0$
mW. The load receives 16.2 mW of that: **18%**. Maximum power transfer has been achieved
and 82% of the energy is heating resistors nobody wanted heated. Both statements are true
at once, and they are not in conflict — the first is about the best a load can do against a
*fixed* network, the second is about how wasteful that network was to begin with. If you
are allowed to redesign the network, drop the 1.00 kΩ and the whole picture improves. If
you are not, 16.2 mW is the ceiling and no load beats it.
''',
                },
                {
                    "title": "Where the match happens",
                    "minutes": 13,
                    "brief": r'''
The last rung, and it asks for a frequency rather than a voltage.

A 5.00 V RMS source sits behind 100 Ω of resistance and 20.0 mH of inductance — that pair
is the source impedance, and you cannot change it. The load is a 100 Ω resistor with a
330 nF capacitor in series, and it is already fitted.

At most frequencies the coil and the capacitor are pulling in opposite directions and only
partly cancelling, so the loop carries reactance and the current is smaller than the
resistances alone would allow. At exactly one frequency they cancel completely, the loop
is purely resistive, and — since the two resistances are equal — the conjugate match is
satisfied in both of its parts at once.
''',
                    "prompt": "At what frequency does the load take the most power?",
                    "note": "Give the answer in hertz, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "vs", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                            {"id": "rs", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 100},
                            {"id": "ls", "kind": "L", "x": 9, "y": 3, "rot": 0, "value": 0.02},
                            {"id": "cl", "kind": "C", "x": 12, "y": 3, "rot": 0, "value": 3.3e-7},
                            {"id": "out", "kind": "OUT", "x": 14, "y": 3, "rot": 0, "value": 0},
                            {"id": "rl", "kind": "R", "x": 14, "y": 4, "rot": 1, "value": 100},
                        ],
                        "wires": [
                            {"a": [3, 6], "b": [3, 7]},
                            {"a": [3, 4], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [8, 3]},
                            {"a": [10, 3], "b": [11, 3]},
                            {"a": [13, 3], "b": [14, 3]},
                            {"a": [14, 5], "b": [14, 7]},
                            {"a": [14, 7], "b": [3, 7]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "5.00 V RMS behind 100 Ω"},
                        {"label": "Source inductance", "value": "20.0 mH"},
                        {"label": "Load capacitor", "value": "330 nF"},
                        {"label": "Load resistor", "value": "100 Ω"},
                    ],
                    "aside": "Only one condition has to be solved for. The resistances are already equal, "
                             "so the frequency is fixed entirely by the requirement that the two "
                             "reactances cancel: $\\omega L = 1/(\\omega C)$.",
                    "answer": 1959.1,
                    "tol": 12.0,
                    "unit": "Hz",
                    # Measured, not asserted: the check sweeps the solver's own response and finds the
                    # frequency at which the probed load voltage peaks, by ternary search in log f.
                    # Nothing about L, C or the resonance formula appears in it.
                    "check": r'''
c.assert(c.count('L') === 1 && c.count('C') === 1, "one reactance on each side of the loop");
var lo = Math.log(100), hi = Math.log(1e5);
for (var i = 0; i < 120; i++) {
  var a = lo + (hi - lo) / 3, b = hi - (hi - lo) / 3;
  if (c.gain(Math.exp(a)) < c.gain(Math.exp(b))) lo = a; else hi = b;
}
return Math.exp((lo + hi) / 2);
''',
                    "hint": "Set $\\omega L = 1/(\\omega C)$ and solve for $\\omega$, which gives "
                            "$\\omega = 1/\\sqrt{LC}$. Then remember what divides $\\omega$ to give $f$.",
                    "wrong": "12.3 kHz is $\\omega_0$ in radians per second reported as a frequency — the "
                             "missing $2\\pi$, which module 1 warned would be the most common slip in "
                             "this course. 4.82 kHz is $1/(2\\pi R_L C)$, the corner of the load's own "
                             "resistor and capacitor, which is a real frequency in this circuit and not "
                             "the one asked for. 796 Hz is where the coil's reactance equals 100 Ω, so "
                             "it is where the source impedance's angle passes 45° — also real, also not "
                             "the maximum.",
                    "why": r'''
The reactances cancel when $\omega L = 1/(\omega C)$, so $\omega^2 = 1/(LC)$:

```
L*C       = 0.0200 * 330e-9                    = 6.6000e-9
sqrt(L*C)                                      = 8.12404e-5
omega_0   = 1/8.12404e-5                       = 12309.1 rad/s
f_0       = 12309.1/(2*pi)                     = 1959.1 Hz
```

Check it by evaluating both reactances there:

```
X_L       = 12309.1 * 0.0200                   = 246.18 ohm
X_C       = 1/(12309.1 * 330e-9)               = 246.18 ohm
X_loop    = 246.18 - 246.18                    = 0.00 ohm
```

so the loop impedance is $100 + 100 = 200$ Ω, purely real, and

```
I         = 5.00/200                           = 25.000 mA
V_L       = 25.000e-3 * 100                    = 2.500 V rms
P_L       = 0.025^2 * 100                      = 62.500 mW
```

which is $V^2/(4R_{th}) = 25.0/400 = 62.5$ mW, the ceiling for this source.

Two things about that number are worth noticing.

The load is receiving exactly half the source voltage, 2.500 V out of 5.00 V. That is what
a match looks like on a voltmeter, and it is the check the build in this module uses,
because it needs no wattmeter.

And the match is narrow in the way a series resonance always is. Drop to 1.00 kHz and
$X_L = 125.7$ Ω while $X_C = 482.3$ Ω, leaving $-356.6$ Ω uncancelled; the loop impedance
becomes $\sqrt{200^2 + 356.6^2} = 408.9$ Ω, the current falls to 12.23 mA, and the load
receives $0.01223^2 \times 100 = 14.96$ mW — under a quarter of what it gets at the match,
for a frequency change of less than a factor of two. The resistive maximum in the earlier
reading was flat; this one is not, because it is a series resonance, and its sharpness is
set by the $Q$ of Module 7 rather than by the power curve. Here
$Q = \omega_0 L/R_{loop} = 246.18/200 = 1.23$, which is a low $Q$ by resonator standards
and is still enough to lose three quarters of the power in just under an octave.
''',
                },
            ],
            "blanks": [
                {
                    "title": "A network reduced to two numbers",
                    "minutes": 11,
                    "lang": "text",
                    "caption": "One T-network, all the way from three resistors to what a load will see.",
                    "brief": r'''
The network is 12.0 V feeding a 1.00 kΩ resistor into a node $A$; a 1.50 kΩ resistor from
$A$ to ground; a 200 Ω resistor from $A$ out to the terminals. A 470 Ω load is going on
those terminals.

Fill it in a line at a time. The one line that is not arithmetic is the one that decides
the whole answer.
''',
                    "listing": r'''
12 V -> R1 = 1.00 k -> node A,   R2 = 1.50 k from A to ground,
                                 R3 = 200 ohm from A out to the terminals


  open circuit first: no current in R3, so R3 drops nothing

      V_th  = 12.0 * 1500/(1000 + 1500)     =  ___ V

  now zero the supply.  An ideal voltage source with zero volts across it is ___

  so R1 runs from A to ground alongside R2, which makes them ___

      R_th  = 200 + 1000*1500/2500          =  ___ ohm

  hang the 470 ohm load on the terminals

      I_L   = 7.200/(800 + 470)             =  ___ mA

      V_L   = 5.6693e-3 * 470               =  ___ V

  and for contrast, what the real 12 V supply is doing meanwhile

      V_A   = 12.0 * 463.13/(1000 + 463.13) =  3.7984 V

      I_src = (12.0 - 3.7984)/1000          =  ___ mA
''',
                    "blanks": [
                        {
                            "prompt": "The open-circuit voltage",
                            "hole": "vth",
                            "opts": ["7.200", "4.800", "12.000", "2.400"],
                            "a": 0,
                            "why": r'''
$12.0 \times 1500/2500 = 7.200$ V. The 200 Ω is still in the circuit, but with the
terminals open no current can flow through it, so it drops nothing and the terminal voltage
is whatever node $A$ sits at. 4.800 V is the 1.00 kΩ's share, the divider ratio inverted —
and note that 4.800 and 7.200 add to 12.0, which is the quickest way to spot that you have
taken the wrong one. 12.000 V is the supply itself, which the terminals would show only if
R1 were a wire. 2.400 V would be right if the 200 Ω were carrying enough current to drop
4.8 V, and it is carrying none.
''',
                        },
                        {
                            "prompt": "What replaces the supply when it is zeroed",
                            "hole": "zero",
                            "opts": ["a short circuit", "an open circuit", "a 12 ohm resistor",
                                     "left in place, unchanged"],
                            "a": 0,
                            "why": r'''
A short circuit. An ideal voltage source has zero internal impedance — that is what makes
it ideal — so setting its value to zero leaves a piece of wire. Replacing it with an open
circuit is the rule for a *current* source, whose ideal internal impedance is infinite, and
using it here strands R1 with a dead end and gives $R_{th} = 1700$ Ω instead of 800 Ω.
Turning it into a resistor of the same numerical value confuses volts with ohms. And
leaving it in place would make $R_{th}$ depend on the supply voltage, which it cannot,
because a resistance is a property of the passive network.
''',
                        },
                        {
                            "prompt": "How R1 and R2 then sit relative to each other",
                            "hole": "combo",
                            "opts": ["in parallel", "in series", "in series with R3", "shorted out"],
                            "a": 0,
                            "why": r'''
In parallel. Both now run from node $A$ to ground: R2 always did, and R1's far end has just
been tied to ground by the short that replaced the supply. Two components between the same
pair of nodes are in parallel by definition. Calling them series gives 2.50 kΩ and then
2.70 kΩ for $R_{th}$, which is over three times the right answer. They are not shorted out
either — a short *across* a resistor removes it, and this short is at the far end of one of
them, which is a different thing entirely.
''',
                        },
                        {
                            "prompt": "The Thévenin resistance",
                            "hole": "rth",
                            "opts": ["800.0", "600.0", "1700.0", "2700.0"],
                            "a": 0,
                            "why": r'''
$1000 \parallel 1500 = 600$ Ω, and the 200 Ω is in series with all of it on the way out to
the terminals, so $R_{th} = 800$ Ω. 600.0 is the parallel pair with the 200 Ω forgotten,
which is easy to do because the 200 Ω does nothing at all in the open-circuit voltage
calculation and it is tempting to assume it does nothing here either. 1700.0 comes from
opening the supply instead of shorting it. 2700.0 is all three in series.
''',
                        },
                        {
                            "prompt": "The load current",
                            "hole": "il",
                            "opts": ["5.6693", "9.0000", "15.319", "2.6646"],
                            "a": 0,
                            "why": r'''
$7.200/1270 = 5.6693$ mA. One loop, two resistances in series, Ohm's law. 9.0000 mA is
$V_{th}/R_{th}$, the short-circuit current — what flows when the load is a piece of wire —
and it is the Norton current of this network, a useful number but not this one. 15.319 mA
is $7.200/470$, the load on an ideal source with no $R_{th}$ at all. 2.6646 is the load
*voltage* in volts, which is the line below.
''',
                        },
                        {
                            "prompt": "The load voltage",
                            "hole": "vl",
                            "opts": ["2.6646", "7.2000", "3.7984", "4.5354"],
                            "a": 0,
                            "why": r'''
$5.6693\,\text{mA} \times 470 = 2.6646$ V. 7.2000 V is the open-circuit value, which the
terminals stopped showing the moment a load was attached — a 470 Ω load against an 800 Ω
source impedance takes barely a third of what was on offer. 3.7984 V is node $A$'s voltage
in the loaded circuit, which is a real voltage but is on the far side of the 200 Ω from the
load. 4.5354 V is the drop across $R_{th}$, the part of $V_{th}$ the load does *not* get,
and $2.6646 + 4.5354 = 7.200$ as it must.
''',
                        },
                        {
                            "prompt": "The current the 12 V supply is really delivering",
                            "hole": "isrc",
                            "opts": ["8.2016", "5.6693", "4.8000", "12.000"],
                            "a": 0,
                            "why": r'''
$(12.0 - 3.7984)/1000 = 8.2016$ mA, which is *not* the 5.6693 mA the equivalent's internal
loop carries. The equivalent was only ever a promise about the terminals; the real supply
is also feeding the 1.50 kΩ, which the equivalent has absorbed and can no longer see.
5.6693 mA is the load current, correct for the load and wrong for the supply. 4.8000 mA is
what the supply draws with the terminals open, $12.0/2500$, and connecting a load can only
increase it. 12.000 mA would be $12.0/1000$, the current if node $A$ were held at ground.
''',
                        },
                    ],
                },
                {
                    "title": "Sizing a conjugate match",
                    "minutes": 10,
                    "lang": "text",
                    "caption": "From a source impedance to the component that cancels it, and the watts that follow.",
                    "brief": r'''
A 5.00 V RMS source sits behind 100 Ω and 20.0 mH. The job is to design the load that takes
the most power from it at 2.00 kHz.

Two decisions, in order: cancel the reactance, then match the resistance. The arithmetic
below does them in that order, and the last line is the one that tells you what matching
costs.
''',
                    "listing": r'''
source: 5.00 V rms behind  R_s = 100 ohm  and  L = 20.0 mH,  matched at 2.00 kHz


    omega    = 2*pi*2000                        =  12566 rad/s

    X_L      = omega * L                        =  ___ ohm

    Z_th     = 100 + j251.33 ohm

  the load that takes the most power from it is  ___

  its reactance is negative, so the load is a resistor and a capacitor in series

    C        = 1/(omega * 251.33)               =  ___ nF

    Z_loop   = (100 + 100) + j(251.33 - 251.33) =  ___ ohm

    I        = 5.00/200                         =  ___ mA

    P_load   = I^2 * 100                        =  ___ mW

    P_source = I^2 * ___                        =  62.500 mW
''',
                    "blanks": [
                        {
                            "prompt": "The coil's reactance at 2.00 kHz",
                            "hole": "xl",
                            "opts": ["251.33", "40.000", "125.66", "0.0039789"],
                            "a": 0,
                            "why": r'''
$X_L = \omega L = 12566 \times 0.0200 = 251.33$ Ω. 40.000 is $fL$, the version with the
$2\pi$ left out. 125.66 is $\omega L$ with the inductance taken as 10 mH, or equivalently
$X_L/2$. 0.0039789 is $1/(\omega L)$ in siemens, which is the susceptance and belongs to a
parallel calculation, not this one.
''',
                        },
                        {
                            "prompt": "The load impedance that takes the most power",
                            "hole": "zl",
                            "opts": ["100 - j251.33 ohm", "100 + j251.33 ohm", "270.49 ohm",
                                     "-100 - j251.33 ohm"],
                            "a": 0,
                            "why": r'''
The complex conjugate: same real part, opposite sign on the reactance. Repeating the source
impedance exactly puts $200 + j502.7$ Ω in the loop, whose large reactance throttles the
current without dissipating anything. A plain 270.49 Ω resistor is the best a single
resistor can do — it is $|Z_{th}|$, and it delivers 33.7 mW against the conjugate's
62.5 mW — but it is not the maximum when a capacitor is allowed. A negative resistance is
not a passive component and would be a source, not a load.
''',
                        },
                        {
                            "prompt": "The capacitor that cancels the coil at 2.00 kHz",
                            "hole": "cval",
                            "opts": ["316.6", "1989", "50.39", "633.3"],
                            "a": 0,
                            "why": r'''
$C = 1/(\omega X_C) = 1/(12566 \times 251.33) = 3.166 \times 10^{-7}$ F, which is 316.6 nF.
Equivalently $C = 1/(\omega^2 L)$, the form worth remembering because it shows the matching
capacitor shrinking as the square of the frequency: double the frequency and a quarter of
the capacitance cancels the same coil. 1989 nF is $1/(f X_C)$, the missing $2\pi$, and it is
$2\pi$ times too large. 50.39 nF is the same slip in the other direction, an extra $2\pi$
from $1/(2\pi\omega X_C)$. 633.3 nF is the capacitor that would cancel a 10 mH coil, which
is what you get by halving $X_L$ somewhere along the way.
''',
                        },
                        {
                            "prompt": "The loop impedance once the reactances cancel",
                            "hole": "zloop",
                            "opts": ["200", "100", "447.69", "200 + j502.65"],
                            "a": 0,
                            "why": r'''
200 Ω, purely real: the two 100 Ω resistances in series, with the reactance gone. That is
what the match *is* — the loop behaves as though neither the coil nor the capacitor were
there. 100 Ω counts only one of the two resistances, and the source's own is as real as the
load's. 447.69 Ω is the loop impedance for a 270.49 Ω resistive load with the coil still
uncancelled. $200 + j502.65$ is the loop with a load that duplicates the source impedance
instead of conjugating it.
''',
                        },
                        {
                            "prompt": "The loop current",
                            "hole": "iloop",
                            "opts": ["25.000", "50.000", "15.567", "11.169"],
                            "a": 0,
                            "why": r'''
$5.00/200 = 25.000$ mA. 50.000 mA is $5.00/100$, the current if only one of the two
resistances were counted. 15.567 mA is the current with a bare 100 Ω load and the coil left
uncancelled, and 11.169 mA is the current with the best resistive load — both smaller,
which is the whole reason the capacitor is there.
''',
                        },
                        {
                            "prompt": "The power in the load",
                            "hole": "pload",
                            "opts": ["62.500", "125.00", "24.233", "33.739"],
                            "a": 0,
                            "why": r'''
$(0.025)^2 \times 100 = 62.500$ mW, which agrees with $|V|^2/(4R_{th}) = 25.0/400$.
125.00 mW is the *total* the source delivers, $5.00 \times 25.0$ mA, of which the load gets
half. 24.233 mW is what a bare 100 Ω load receives with the coil uncancelled, and 33.739 mW
is what the best purely resistive load receives — the two numbers the capacitor was bought
to beat.
''',
                        },
                        {
                            "prompt": "What multiplies $I^2$ to give the power lost inside the source",
                            "hole": "rint",
                            "opts": ["100", "251.33", "200", "270.49"],
                            "a": 0,
                            "why": r'''
The source's own 100 Ω, giving the same 62.500 mW as the load. That equality is the
definition of the matched condition and the reason its efficiency is exactly 50%. 251.33 Ω
is the coil's reactance, and a reactance dissipates nothing at all — no power term ever
multiplies $I^2$ by a reactance. 200 Ω is the whole loop and would count the load's
dissipation as well. 270.49 Ω is $|Z_{th}|$, a magnitude that mixes resistance and
reactance and so cannot appear in a power calculation either.
''',
                        },
                    ],
                },
            ],
            "quiz": {
                "title": "One source, one impedance",
                "minutes": 9,
                "questions": [
                    {
                        "q": "How do you find the Thévenin impedance of a network?",
                        "opts": [
                            "Take the impedance of its largest component",
                            "Look into the terminals with every independent source zeroed — voltage sources shorted, current sources opened",
                            "Add up every impedance in the network",
                            "Take the load impedance that draws the most power",
                        ],
                        "a": 1,
                        "why": r'''
Zero the sources and look back in. A voltage source holds its terminals at a fixed
difference no matter what, so as far as a small change is concerned it is a short; a
current source holds its current no matter what, so it is a break. What remains is a
passive network you can reduce with the series and parallel rules you already have.
Note that zeroing means *replacing*, not deleting: leaving a gap where a voltage source
was gives a completely different answer.
''',
                    },
                    {
                        "q": "A 12 V supply feeds a divider of 3 kΩ on top and 1 kΩ below. What is the Thévenin equivalent at the junction?",
                        "opts": [
                            "3 V in series with 4 kΩ",
                            "3 V in series with 750 Ω",
                            "12 V in series with 750 Ω",
                            "9 V in series with 3 kΩ",
                        ],
                        "a": 1,
                        "why": r'''
The open-circuit voltage is $12 \times 1000/4000 = 3$ V. For the impedance, short the
12 V supply: the 3 kΩ now runs from the junction to ground alongside the 1 kΩ, so
$Z_{th} = 3000 \parallel 1000 = 750$ Ω. Adding them to get 4 kΩ is the series answer
and describes a different circuit entirely. That 750 Ω is exactly the resistance that
set the corner frequency when a capacitor was hung on this node earlier in the course,
and it is not a coincidence.
''',
                    },
                    {
                        "q": "A source has a Thévenin impedance of $50 + j30$ Ω. Which load takes the most power from it?",
                        "opts": ["$50 + j30$ Ω", "$50 - j30$ Ω", "$50$ Ω", "An open circuit"],
                        "a": 1,
                        "why": r'''
The complex conjugate, $50 - j30$ Ω. The load's reactance has to be equal and opposite
so that the two cancel and the loop is purely resistive; then the resistances match.
Repeating the source impedance exactly gives $100 + j60$ in the loop, whose reactance
wastes current on energy that comes straight back. A plain 50 Ω is better than that but
still leaves $+j30$ uncancelled. And an open circuit takes no power at all, however
large the voltage across it.
''',
                    },
                    {
                        "q": "At the conjugate match, what fraction of the power leaving the source ends up in the load?",
                        "opts": ["All of it", "Three quarters", "A half", "It depends on the reactance"],
                        "a": 2,
                        "why": r'''
Half. The load resistance equals the source resistance and carries the same current, so
the two dissipate equally. This is the point people find unsatisfying, and it is worth
being precise about what it says: matching maximises the *power delivered*, not the
*efficiency*. If you can choose the source impedance, make it small and take almost all
of the power at high efficiency. Matching is what you do when the source impedance is
fixed by physics and the only free choice is the load.
''',
                    },
                    {
                        "q": "Why is a mains power supply deliberately not matched to its load?",
                        "opts": [
                            "Because matching is only defined for direct current",
                            "Because a matched source burns half the power in its own impedance, and efficiency matters far more than the last decibel of delivered power",
                            "Because a matched source would oscillate",
                            "Because the load impedance is unknown",
                        ],
                        "a": 1,
                        "why": r'''
Because half of everything generated would be lost in the generator and the cables. A
supply is built with the lowest source impedance it can manage, so that its terminal
voltage barely sags however much current is drawn, and it operates nowhere near the
matched condition. Matching is for sources whose impedance cannot be lowered — an
antenna, a piezo sensor, a transistor's output at radio frequencies — where the
alternative is not more efficiency but less signal.
''',
                    },
                    {
                        "q": "In a Thévenin calculation, zeroing an ideal voltage source means what?",
                        "opts": [
                            "Removing it and leaving a gap",
                            "Replacing it with a short circuit",
                            "Replacing it with a resistor of the same numerical value",
                            "Setting the frequency to zero",
                        ],
                        "a": 1,
                        "why": r'''
Replace it with a short. An ideal voltage source has zero internal impedance — that is
what makes it ideal — so with its voltage set to zero it is a piece of wire. Leaving a
gap is what you do to a *current* source, whose ideal internal impedance is infinite.
Getting these two the wrong way round is the classic error, and it is worth
re-deriving from the definition each time rather than memorising: zero the value, keep
the internal impedance.
''',
                    },
                ],
            },
            "build": {
                "title": "Match a source to its load",
                "minutes": 26,
                "brief": r'''
A signal source whose internal impedance you cannot change: 50 Ω of resistance with
10 mH of inductance in series with it. The load is a resistor, and it is currently
200 Ω, wired straight on.

Rearrange it so that the load takes the greatest possible power at **1 kHz**. That
means both halves of a conjugate match: cancel the source's reactance with a **series
capacitor**, and set the load resistance equal to the source's.

1. **Nothing steady gets through**, because a capacitor is now in series.
2. **At 1 kHz the load takes exactly half the source voltage.** Equal resistances
   sharing a loop with no reactance left in it — that is what a match looks like on a
   voltmeter.
3. **At 1 kHz there is no phase shift**, within a few degrees: the source is delivering
   into something purely real.
4. **At 100 Hz far less arrives.** The match holds at one frequency, and the
   uncancelled capacitive reactance takes over below it.

To cancel $\omega L$ at 1 kHz you need $1/(\omega C) = \omega L$, which is
$C = 1/(\omega^2 L)$.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 50},
                        {"id": "p3", "kind": "L", "x": 8, "y": 3, "rot": 0, "value": 0.01},
                        {"id": "p4", "kind": "OUT", "x": 14, "y": 3, "rot": 0, "value": 0},
                        {"id": "p5", "kind": "R", "x": 14, "y": 4, "rot": 1, "value": 200},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [7, 3]},
                        {"a": [9, 3], "b": [14, 3]},
                        {"a": [14, 5], "b": [14, 6]},
                        {"a": [14, 6], "b": [3, 6]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 5, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 7, "rot": 0, "value": 0},
                        {"id": "p2", "kind": "R", "x": 5, "y": 3, "rot": 0, "value": 50},
                        {"id": "p3", "kind": "L", "x": 8, "y": 3, "rot": 0, "value": 0.01},
                        {"id": "p4", "kind": "C", "x": 11, "y": 3, "rot": 0, "value": 2.53e-6},
                        {"id": "p5", "kind": "OUT", "x": 14, "y": 3, "rot": 0, "value": 0},
                        {"id": "p6", "kind": "R", "x": 14, "y": 4, "rot": 1, "value": 50},
                    ],
                    "wires": [
                        {"a": [3, 6], "b": [3, 7]},
                        {"a": [3, 4], "b": [3, 3]},
                        {"a": [3, 3], "b": [4, 3]},
                        {"a": [6, 3], "b": [7, 3]},
                        {"a": [9, 3], "b": [10, 3]},
                        {"a": [12, 3], "b": [14, 3]},
                        {"a": [14, 5], "b": [14, 6]},
                        {"a": [14, 6], "b": [3, 6]},
                    ],
                },
                "checks": [
                    {"name": "no steady voltage reaches the load", "code": r'''
c.assert(Math.abs(c.vout()) < 1e-6,
  "the probe reads " + c.fmt(c.vout(), "V") + " at DC — a series capacitor should stop it completely");
'''},
                    {"name": "at 1 kHz the load takes half the source", "code": r'''
c.assert(c.count("V") === 1, "use exactly one voltage source, so the checks know what to compare against");
var vs = Math.abs(c.values("V")[0]);
c.close(c.gain(1000) / vs, 0.5, 0.02,
  "with the reactance cancelled and the resistances equal, the loop is two identical resistors sharing the source");
'''},
                    {"name": "at 1 kHz the source sees no reactance", "code": r'''
var p = c.phase(1000);
c.assert(Math.abs(p) < 5,
  "measured " + p.toPrecision(3) + " degrees of shift; at the match the loop impedance is purely real");
'''},
                    {"name": "the match holds at one frequency only", "code": r'''
var vs = Math.abs(c.values("V")[0]);
var g = c.gain(100) / vs;
c.assert(g < 0.1,
  "a decade below the match the capacitor's reactance is enormous and little should arrive; measured " +
  g.toPrecision(3));
'''},
                ],
                "hints": [
                    "Two changes are needed, not one: a capacitor in series with the loop, and the load resistor brought down to 50 Ω.",
                    "Delete the long wire between the inductor and the probe, then place the capacitor in the gap and wire both of its pins.",
                    "$\\omega = 2\\pi \\times 1000 = 6283$ rad/s, so $\\omega L = 62.8$ Ω, and $C = 1/(\\omega^2 L) = 2.53$ µF.",
                    "If the gain at 1 kHz comes out well above a half, the load resistor is still larger than the source resistance — which delivers a bigger voltage and less power.",
                ],
            },
            "derive": {
                "title": "Why the matched load is the equal one",
                "minutes": 12,
                "vars": ["V", "R_th", "R_L", "P"],
                "brief": r'''
Take the reactance as already cancelled, so what is left is a real source $V$ (RMS)
behind a resistance $R_{th}$, driving a load resistance $R_L$. The question is which
$R_L$ takes the most power, and the answer is not the obvious one — the largest load
gets the largest *voltage*, and the smallest gets the largest *current*, and neither of
those is power.
''',
                "steps": [
                    {
                        "prompt": "Write the RMS current in the loop.",
                        "answer": "\\frac{V}{R_{th} + R_L}",
                        "hint": "One loop, two resistances in series, Ohm's law.",
                        "deconstruct": [
                            "The two resistances are in series, so the loop resistance is $R_{th} + R_L$.",
                            "Ohm's law gives the current directly.",
                        ],
                    },
                    {
                        "prompt": "Write the power dissipated in the load, in terms of $V$, $R_{th}$ and $R_L$.",
                        "given": "The power in a resistance carrying an RMS current $I$ is $I^2 R$.",
                        "answer": "\\frac{V^2 R_L}{(R_{th} + R_L)^2}",
                        "placeholder": "\\frac{\\ldots}{(R_{th} + R_L)^2}",
                        "hint": "Square the current you just wrote and multiply by $R_L$.",
                        "deconstruct": [
                            "$I^2 = \\dfrac{V^2}{(R_{th}+R_L)^2}$.",
                            "Multiplying by $R_L$ gives the power in the load.",
                        ],
                    },
                    {
                        "prompt": "Differentiate that with respect to $R_L$ and set the result to zero. Which $R_L$ comes out?",
                        "answer": "R_{th}",
                        "hint": "By the quotient rule the numerator of $dP/dR_L$ is $V^2\\left[(R_{th}+R_L)^2 - R_L \\cdot 2(R_{th}+R_L)\\right]$. Cancel one factor of $(R_{th}+R_L)$ and solve.",
                        "deconstruct": [
                            "The quotient rule leaves $(R_{th}+R_L)^2 - 2R_L(R_{th}+R_L)$ on top.",
                            "Dividing by $(R_{th}+R_L)$ leaves $R_{th} + R_L - 2R_L = R_{th} - R_L$.",
                            "That is zero exactly when the two resistances are equal.",
                        ],
                    },
                    {
                        "prompt": "Substitute that back in. What power does the load receive at the match?",
                        "answer": "\\frac{V^2}{4 R_{th}}",
                        "hint": "Put $R_L = R_{th}$ into the power expression and simplify the denominator, which becomes $(2R_{th})^2$.",
                        "deconstruct": [
                            "$P = \\dfrac{V^2 R_{th}}{(2R_{th})^2} = \\dfrac{V^2 R_{th}}{4R_{th}^2}$.",
                            "One factor of $R_{th}$ cancels.",
                        ],
                    },
                ],
                "closing": r'''
$P_{max} = V^2/(4R_{th})$, and the source resistance dissipates exactly the same,
because it carries the same current and has the same resistance. Half the total, and
no arrangement of a passive load does better.

The curve around that maximum is remarkably flat, which is the practical part. At
$R_L = 2R_{th}$ or $R_L = R_{th}/2$ the load still receives $8/9$ of the maximum — half
a decibel down. Getting a match roughly right is usually enough; the reason radio
engineers pursue it to a fraction of an ohm is reflections on a transmission line, and
that is a subject for a later course.
''',
            },
        },

    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Identify three filters you cannot open",
        "runtime": "python",
        "minutes": 100,
        "brief": r'''
Three sealed boxes sit on the bench. Each contains one first-order filter — a
resistor and a capacitor, nothing else — and you cannot see inside any of them.

What you *can* do is drive a box with a sinusoid of your choosing and capture the
waveform that comes out. `bench.py` does exactly that and no more: give it a box name
and a frequency, and it hands back a captured waveform. The input is always 1 V peak.

From that alone, work out for each box whether it is a low-pass or a high-pass, where
its corner frequency is, and what resistor it must contain if the capacitor is 10 nF.

## What the bench gives you

`capture(name, f)` returns a NumPy array: 8 complete cycles of the output, at 256
samples per cycle, whatever the frequency. Because it is always a whole number of
cycles, the RMS of that array is an exact measure of the output size, so you never
have to worry about where the capture starts or stops.

The generator is not perfectly pure — there is about 5% of a third harmonic riding on
the drive, which is normal, and the box filters that harmonic at its own frequency
like any other. It shifts every corner you measure about 0.2% low. Do not try to
remove it; the tolerances allow for it.

## Suggested order

Get `rms` working first and check it against a waveform you already know. Then
`amplitude`, which is one line on top of it. Then `classify`, which needs only two
measurements. `find_corner` is last, and it is a bisection: the same bisection you
would run to find any crossing, in the logarithm of the frequency rather than the
frequency itself, because a filter's response is a straight line on a log axis and
nothing like one on a linear axis.

One trap is worth naming in advance. The corner is 0.707 of the **pass-band** level,
so you have to measure that level somewhere the filter is genuinely doing nothing. If
you read it at the edge of your search bracket, the response there has already begun
to sag, your target comes out low, and the corner you report moves whenever you change
the bracket. Read the pass band a couple of decades outside the bracket instead.
''',
        "deliverables": [
            "`rms(v)`, the root of the mean of the square of a captured waveform, working for any waveform rather than only for a sinusoid.",
            "`amplitude(name, f)`, the RMS of one capture from a named box at one frequency.",
            "`classify(name)`, returning the string `\"low-pass\"` or `\"high-pass\"`, decided by measurement at two well-separated frequencies rather than by any knowledge of what is in the box.",
            "`find_corner(name, f_lo, f_hi)`, returning the −3 dB frequency in hertz, found by bisecting on the measured response between the two bounds, and correct for either kind of filter.",
            "`resistor_for(fc, c)`, returning the resistance a filter of that corner frequency must contain given its capacitance.",
            "A comment at the top of `main.py` recording the corner frequency you measured for each of the three boxes and the resistor value each implies for a 10 nF capacitor.",
        ],
        "constraints": [
            "NumPy and the standard library only.",
            "`find_corner` must locate the crossing from measurements. Fitting a straight line to a formula you assumed, or returning a constant, is not measuring.",
            "Nothing may import the internals of `bench.py`: `capture` is the whole interface, and reading `_FILTERS` defeats the exercise.",
            "The corner is defined against the pass band, not against 1 V — measure the pass-band level rather than assuming the filter has unity gain there, and measure it well clear of the corner.",
        ],
        "rubric": [
            {"criterion": "RMS from samples", "weight": 20,
             "evidence": "`rms` computes the root mean square from the array itself and returns the correct value for a sinusoid, a steady level and a square wave alike."},
            {"criterion": "Classification by measurement", "weight": 20,
             "evidence": "`classify` returns the right kind for all three boxes, decided by comparing measured amplitudes far below and far above the corner."},
            {"criterion": "Corner by bisection", "weight": 35,
             "evidence": "`find_corner` returns each box's corner to within 2%, works for both the low-pass and the high-pass boxes, and locates the crossing relative to the measured pass band."},
            {"criterion": "From measurement to component", "weight": 15,
             "evidence": "`resistor_for` inverts the corner formula correctly, and the header comment records a measured corner and an implied resistance for each box."},
            {"criterion": "Robustness", "weight": 10,
             "evidence": "The bisection converges from wide bounds, does not depend on the number of samples in a capture, and gives the same answer when the search bounds are changed."},
        ],
        "hints": [
            "The RMS of one capture is all the amplitude information you need: because the capture is always a whole number of cycles, `np.sqrt(np.mean(v * v))` is exact.",
            "For `classify`, measure at 10 Hz and at 200 kHz. Whichever end is larger is the pass band, and that says which kind of filter it is.",
            "Bisect in the logarithm: the midpoint of `lo` and `hi` should be `np.sqrt(lo * hi)`, not `(lo + hi) / 2`. Sixty iterations is plenty.",
            "One bisection can serve both kinds. Work out which end is the pass band first, then at each midpoint ask whether the measurement is still above the target, and move whichever bound is on the pass-band side.",
            "Take the pass-band reading two decades outside the bracket — `f_lo / 100` for a low-pass, `f_hi * 100` for a high-pass. Reading it at the bracket edge makes the answer drift as the bracket changes, which is exactly what one of the checks looks for.",
            "`resistor_for` is the corner formula rearranged: $R = 1/(2\\pi f_c C)$.",
        ],
        "files": [
            {"name": "bench.py", "ro": True, "content": r'''
"""The sealed bench. Do not edit, and do not read the filter table.

`capture(name, f)` drives box `name` with a 1 V peak sinusoid at `f` hertz and
returns the waveform that comes out: CYCLES complete cycles, SAMPLES_PER_CYCLE
samples in each, so the array is always a whole number of periods long.

The generator produces about 5% of a third harmonic alongside the fundamental. The
box filters that harmonic too, at its own frequency, exactly as it would in reality.
"""
import numpy as np

SAMPLES_PER_CYCLE = 256
CYCLES = 8
HARMONIC = 0.05

_FILTERS = {
    "A": ("low", 1200.0),
    "B": ("high", 3400.0),
    "C": ("low", 480.0),
}

BOXES = tuple(sorted(_FILTERS))


def _gain_phase(kind, fc, f):
    x = f / fc
    h = 1.0 / (1.0 + 1j * x) if kind == "low" else (1j * x) / (1.0 + 1j * x)
    return abs(h), float(np.angle(h))


def capture(name, f):
    """One captured output waveform for a 1 V peak input at f hertz."""
    if name not in _FILTERS:
        raise KeyError("no such box: %r (try one of %s)" % (name, ", ".join(BOXES)))
    if f <= 0:
        raise ValueError("frequency must be positive")
    kind, fc = _FILTERS[name]
    n = SAMPLES_PER_CYCLE * CYCLES
    t = np.arange(n) / (SAMPLES_PER_CYCLE * float(f))
    w = 2.0 * np.pi * f
    a1, p1 = _gain_phase(kind, fc, f)
    a3, p3 = _gain_phase(kind, fc, 3.0 * f)
    return a1 * np.sin(w * t + p1) + HARMONIC * a3 * np.sin(3.0 * w * t + p3)


def sample_rate(f):
    """The rate the capture was taken at, in samples per second."""
    return SAMPLES_PER_CYCLE * float(f)
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from bench import capture

# Measured corners, and the resistor each implies with a 10 nF capacitor:
#   box A -> TODO Hz, TODO ohms
#   box B -> TODO Hz, TODO ohms
#   box C -> TODO Hz, TODO ohms


def rms(v):
    """Root of the mean of the square of a captured waveform."""
    # TODO
    return 0.0


def amplitude(name, f):
    """The RMS of one capture from box `name` at frequency `f`."""
    # TODO
    return 0.0


def classify(name):
    """Return "low-pass" or "high-pass", decided by measurement."""
    # TODO: compare the amplitude far below and far above any plausible corner.
    return "unknown"


def find_corner(name, f_lo=10.0, f_hi=200000.0):
    """The -3 dB frequency in hertz, found by bisection on the measured response."""
    # TODO: pass-band level first, then bisect in the logarithm of the frequency.
    return 0.0


def resistor_for(fc, c):
    """The resistance a first-order filter of corner fc must contain, given c."""
    # TODO
    return 0.0


if __name__ == "__main__":
    for box in ("A", "B", "C"):
        fc = find_corner(box)
        print(box, classify(box), round(fc, 1), "Hz ->",
              round(resistor_for(fc, 1e-8), 1), "ohms")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from bench import capture

# Measured corners, and the resistor each implies with a 10 nF capacitor:
#   box A -> 1197.6 Hz, 13289 ohms   (low-pass)
#   box B -> 3393.2 Hz,  4690 ohms   (high-pass)
#   box C ->  479.0 Hz, 33224 ohms   (low-pass)
# All three read about 0.2% low, which is the third harmonic sitting in the
# pass-band reading and lifting the target very slightly.


def rms(v):
    """Root of the mean of the square of a captured waveform."""
    v = np.asarray(v, dtype=float)
    return float(np.sqrt(np.mean(v * v)))


def amplitude(name, f):
    """The RMS of one capture from box `name` at frequency `f`."""
    return rms(capture(name, f))


def classify(name):
    """Return "low-pass" or "high-pass", decided by measurement."""
    return "low-pass" if amplitude(name, 10.0) > amplitude(name, 200000.0) else "high-pass"


def find_corner(name, f_lo=10.0, f_hi=200000.0):
    """The -3 dB frequency in hertz, found by bisection on the measured response."""
    lo, hi = float(f_lo), float(f_hi)
    low_side_passes = amplitude(name, lo) > amplitude(name, hi)
    # Read the pass-band level two decades outside the bracket, not at its edge:
    # at the edge the response has usually already begun to sag, and the target
    # then drifts with wherever the bracket happens to start.
    band_f = lo / 100.0 if low_side_passes else hi * 100.0
    target = amplitude(name, band_f) / np.sqrt(2.0)
    for _ in range(60):
        mid = float(np.sqrt(lo * hi))
        in_band = amplitude(name, mid) > target
        if in_band == low_side_passes:
            lo = mid
        else:
            hi = mid
    return float(np.sqrt(lo * hi))


def resistor_for(fc, c):
    """The resistance a first-order filter of corner fc must contain, given c."""
    return 1.0 / (2.0 * np.pi * float(fc) * float(c))


if __name__ == "__main__":
    for box in ("A", "B", "C"):
        fc = find_corner(box)
        print(box, classify(box), round(fc, 1), "Hz ->",
              round(resistor_for(fc, 1e-8), 1), "ohms")
'''},
        ],
        "tests": [
            {"name": "rms is computed from the samples, not from a shortcut", "code": r'''
import numpy as np
_t = np.arange(2048) / 2048.0
_sine = 3.0 * np.sin(2 * np.pi * 4 * _t)
assert abs(rms(_sine) - 3.0 / np.sqrt(2)) < 1e-9, \
    f"four whole cycles of a 3 V peak sine is 2.1213 V rms, got {rms(_sine)}"
assert abs(rms(np.full(64, 2.5)) - 2.5) < 1e-12, \
    f"a steady 2.5 V is 2.5 V rms — no sqrt(2) belongs here; got {rms(np.full(64, 2.5))}"
_sq = np.array([4.0] * 50 + [-4.0] * 50)
assert abs(rms(_sq) - 4.0) < 1e-12, f"a square wave's rms is its peak, got {rms(_sq)}"
'''},
            {"name": "amplitude reads the pass band and the stop band apart", "code": r'''
_pass = amplitude("A", 10.0)
_stop = amplitude("A", 200000.0)
assert abs(_pass - 0.7071) < 0.01, \
    f"box A passes a 1 V peak almost untouched at 10 Hz, which is 0.707 V rms; got {_pass}"
assert _stop < 0.01, f"box A should be far into its stop band at 200 kHz; got {_stop}"
'''},
            {"name": "every box is classified correctly", "code": r'''
assert classify("A") == "low-pass", f'box A passes low frequencies; classify said {classify("A")!r}'
assert classify("B") == "high-pass", f'box B passes high frequencies; classify said {classify("B")!r}'
assert classify("C") == "low-pass", f'box C passes low frequencies; classify said {classify("C")!r}'
'''},
            {"name": "the corner of the low-pass box is found", "code": r'''
_fc = find_corner("A")
assert abs(_fc - 1200.0) / 1200.0 < 0.02, \
    f"box A corners at 1200 Hz; the bisection returned {_fc:.1f} Hz"
'''},
            {"name": "the same routine finds the high-pass corner", "code": r'''
_fc = find_corner("B")
assert abs(_fc - 3400.0) / 3400.0 < 0.02, \
    f"box B corners at 3400 Hz; the bisection returned {_fc:.1f} Hz. One bisection must handle both kinds"
'''},
            {"name": "and a third box, so nothing is hard-coded", "code": r'''
_fc = find_corner("C")
assert abs(_fc - 480.0) / 480.0 < 0.02, \
    f"box C corners at 480 Hz; the bisection returned {_fc:.1f} Hz"
'''},
            {"name": "the answer does not depend on the search bounds", "code": r'''
_wide = find_corner("A", 1.0, 1000000.0)
_tight = find_corner("A", 200.0, 20000.0)
assert abs(_wide - _tight) / _tight < 0.01, \
    f"widening the bracket changed the answer: {_wide:.1f} vs {_tight:.1f} Hz"
'''},
            {"name": "the corner is where the response is 0.707 of the pass band", "code": r'''
import numpy as np
_fc = find_corner("B")
_band = amplitude("B", 200000.0)
_here = amplitude("B", _fc)
assert abs(_here / _band - 1 / np.sqrt(2)) < 0.02, \
    f"at the corner the output should be 0.707 of the pass band, measured {_here / _band:.4f}"
'''},
            {"name": "the resistor follows from the corner", "code": r'''
import numpy as np
_r = resistor_for(1200.0, 1e-8)
assert abs(_r - 13262.911924324612) < 1e-6, \
    f"R = 1/(2*pi*1200*1e-8) = 13262.9 ohms, got {_r}"
_r2 = resistor_for(find_corner("C"), 1e-8)
assert abs(_r2 - 33157.3) / 33157.3 < 0.03, \
    f"box C at 480 Hz with 10 nF implies about 33.2 kilohms, got {_r2:.1f}"
'''},
        ],
    },
}
