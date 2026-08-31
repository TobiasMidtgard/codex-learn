"""EE231 — Transforms and Linear Algebra.

A second-year course. It assumes EE111: complex numbers, phasors, differentiation and
integration, and a first sight of simultaneous equations as a matrix. It also assumes
EE102-level AC circuit analysis — impedance, the divider rule applied to impedances,
inductors, and the corner frequency of an RC. Both are first-year courses; nothing
above them is used.

Authoring rules, same as the rest of the catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * every expected number in this file was produced by running the code or the
    circuit solver, never assumed
  * build checks are JavaScript against the circuit API and measure what the
    circuit does, so an equally correct alternative topology passes
"""

COURSE = {
    "id": "EE231",
    "title": "Transforms and Linear Algebra",
    "band": 2,
    "level": "Intermediate",
    "prereqs": ["EE111"],
    "stack": ["Python", "NumPy", "SymPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◈",
    "summary": (
        "Phasors answer one question — what a circuit does to a sinusoid that has been "
        "running forever. The Laplace transform answers all the others: what happens at "
        "the instant a switch closes, how fast the answer arrives, whether it rings on "
        "the way. It does so by turning calculus into algebra, and the algebra it "
        "produces is linear algebra. This course develops both halves together, and ends "
        "by pulling a circuit model out of measured data with least squares."
    ),
    "outcomes": [
        "Transform a signal or a circuit into the s-domain, solve there, and interpret the answer back in time.",
        "Find the poles and zeros of a transfer function and predict the shape of the response from their positions alone.",
        "Split a rational transfer function into partial fractions and invert it term by term.",
        "Write a resistor network as a matrix equation, say what that matrix means as a linear map, and solve it.",
        "Compute eigenvalues and connect them to the poles of the same system written as a transfer function.",
        "Fit a model to measured data by least squares, and judge from the residuals whether the model was the right one.",
        "Carry initial conditions through the transform, so that a switched circuit is solved by algebra rather than by a differential equation.",
        "Read overshoot, peak time and settling time off a second-order response, and turn a specification written in those terms into pole positions.",
        "Eliminate a matrix by hand, say what its rank and nullspace mean about the circuit it came from, and recognise a badly conditioned one.",
        "Build a transfer function from a matrix of admittances, and say which part of it belongs to the network and which to the probe.",
    ],
    "assessment": (
        "Ten quizzes, four circuits designed and measured in the schematic editor, six "
        "guided derivations checked symbolically, two filters tuned to a written "
        "specification, six Python labs checked by execution, a symbol drill, a transient "
        "worked to a number, a page of elimination with holes in it, and a capstone that "
        "identifies an unknown second-order circuit from its measured step response."
    ),
    "reading": [
        "*Fundamentals of Electric Circuits*, Alexander & Sadiku — chapters 15 and 16 for the Laplace treatment of circuits.",
        "*Introduction to Linear Algebra*, Strang — chapters 1 to 4 and 6, for maps, least squares and eigenvalues in that order.",
        "*Signals and Systems*, Oppenheim & Willsky — chapter 9, for the transform on its own terms.",
        "MIT OCW 18.06, Strang's lectures, freely available — lecture 15 is the least squares one.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "The Laplace transform",
            "summary": "One integral turns differentiation into multiplication by s, and a differential equation into ordinary algebra.",
            "concepts": [
                "The Laplace transform of $f(t)$ is $F(s) = \\int_0^{\\infty} f(t)e^{-st}\\,dt$, with $s = \\sigma + j\\omega$ a complex number. The lower limit is 0: the transform knows nothing about the past.",
                "$s$ is a generalised frequency. Setting $\\sigma = 0$ recovers the Fourier transform, which is why phasors are the special case of this that you already know.",
                "The transform is **linear**: $\\mathcal{L}\\{af + bg\\} = aF + bG$. Every technique in the course rests on that one property.",
                "Differentiation becomes multiplication: $\\mathcal{L}\\{f'\\} = sF(s) - f(0)$. The initial condition is not an afterthought — it is carried inside the algebra.",
                "Integration becomes division: $\\mathcal{L}\\{\\int_0^t f\\} = F(s)/s$. A unit step is the integral of an impulse, so $\\mathcal{L}\\{1\\} = 1/s$.",
                "The standard pairs worth knowing by heart: $1 \\leftrightarrow 1/s$, $e^{-at} \\leftrightarrow 1/(s+a)$, $\\sin\\omega t \\leftrightarrow \\omega/(s^2+\\omega^2)$, $\\cos\\omega t \\leftrightarrow s/(s^2+\\omega^2)$, $te^{-at} \\leftrightarrow 1/(s+a)^2$.",
                "Components have s-domain impedances: $Z_R = R$, $Z_L = sL$, $Z_C = 1/(sC)$. Every series and parallel rule from EE101 works unchanged with these, and now covers switch-on as well as steady state.",
                "The final value theorem, $\\lim_{t\\to\\infty} f(t) = \\lim_{s\\to 0} sF(s)$, is only valid when the response actually settles — apply it to an oscillator and it returns a confident wrong answer.",
            ],
            "read": [
                {
                    "title": "Why anybody would turn a signal into a function of $s$",
                    "minutes": 13,
                    "body": r'''
A resistor has a resistance. A capacitor does not. What a capacitor has instead is a
rule relating the current through it to the *rate of change* of the voltage across it,
$i = C\,dv/dt$, and an inductor carries the mirror image of that rule,
$v = L\,di/dt$. The moment either part appears in a circuit, Kirchhoff's laws stop
producing simultaneous equations in numbers and start producing simultaneous equations
in derivatives.

That is the entire difficulty, and it is worth being precise about where it lives.
Nothing about the *circuit* got harder. Three parts in a loop are still three parts in
a loop, and the same two conservation laws still apply to them. What got harder is the
algebra, because the unknown is no longer a number but a function, and the equation
constrains that function's slope as well as its value.

EE111 dealt with this one equation at a time: separate the variables, or find an
integrating factor, integrate, and then pin down the constant of integration with the
initial condition. It works. It does not scale. Two energy-storing parts give a second
order equation, three give a third, and a circuit with an inductor, a capacitor and
four resistors will have you solving a system of coupled differential equations by
hand before you have learned anything at all about the circuit.

The Laplace transform is the way out, and the idea behind it is smaller than its
reputation.

## The one function differentiation leaves alone

Differentiate almost anything and you get something of a different shape. A sine
becomes a cosine, $t^3$ becomes $3t^2$. There is exactly one family of functions that
comes back as itself, multiplied by a constant:

$$\frac{d}{dt}e^{st} = s\,e^{st}$$

For an exponential, differentiation *is* multiplication by a number. If a signal could
be written as a combination of exponentials, then every derivative in every equation
describing it would collapse into a multiplication, and the differential equation would
become an ordinary algebraic one.

The immediate objection is that most signals are not exponentials. The answer is that
$s$ is allowed to be complex, $s = \sigma + j\omega$, and

$$e^{st} = e^{\sigma t}\big(\cos\omega t + j\sin\omega t\big)$$

which is a sinusoid inside an exponential envelope. Choose $\sigma = 0$ and you have a
pure sinusoid; choose $\omega = 0$ and you have a plain decaying or growing
exponential; choose $s = 0$ and you have a constant. Choose both non-zero and you have
a ringing transient that dies away — which is, as it happens, precisely what a
disturbed circuit does. The family is far richer than "exponential" suggests, and it
is exactly wide enough to describe everything a linear circuit can do.

## The transform is the recipe for that combination

$$F(s) = \int_0^{\infty} f(t)\,e^{-st}\,dt$$

Read the integral as a matched filter. You are multiplying your signal by a probe
exponential $e^{-st}$ and adding up the result over all time. Where the probe is close
to something the signal actually contains, the product keeps the same sign and the
integral piles up; where it is not, the product oscillates and cancels itself. $F(s)$
is a score, for each $s$, of how much of that exponential the signal is made of.

Three details of the definition earn their keep.

The kernel is $e^{-st}$, with a minus sign, and it is there for convergence. The
integrand must die away as $t$ grows or the integral means nothing, and the minus sign
is what makes $e^{-st}$ shrink for $s$ to the right of the origin.

The lower limit is $0$, not $-\infty$. The transform is deliberately blind to the past.
Circuits are analysed from the instant something happens — a switch closes, a supply
comes up — and everything that came before is compressed into a single number per
energy-storing part: the voltage a capacitor already holds, the current an inductor
already carries. That is a feature, and module 4 is about cashing it in.

$F(s)$ is a function of a complex variable, and it is not a signal. It has different
units from $f(t)$: the integral multiplies by $dt$, so if $f$ is in volts then $F$ is
in volt-seconds. Nobody plots $F(s)$ against time, because there is no time left in it.

## Worked: the transform of a step, straight from the definition

Take $f(t) = 1$ for $t \ge 0$ — a supply that comes up at $t = 0$ and stays up. There
is no table to look this up in yet, so do the integral.

```text
F(s) = integral from 0 to infinity of  1 * e^(-s t) dt

antiderivative of e^(-s t)  =  -e^(-s t) / s

           [ -e^(-s t) / s ]  from t = 0 to t = infinity

at t -> infinity :   e^(-s t) -> 0   provided Re(s) > 0
at t = 0         :   -e^(0)/s  =  -1/s

F(s) = 0 - (-1/s) = 1/s
```

So $\mathcal{L}\{1\} = 1/s$, and the qualification attached to it is not decoration.
The integral only converges for $\mathrm{Re}(s) > 0$; that half-plane is called the
**region of convergence**, and its boundary here is the imaginary axis, with the
transform's single pole sitting on that boundary at the origin.

## Worked: the transform of a decaying exponential

Now $f(t) = e^{-at}$, a quantity falling towards zero at rate $a$.

```text
F(s) = integral from 0 to infinity of  e^(-a t) * e^(-s t) dt
     = integral from 0 to infinity of  e^(-(s + a) t) dt
```

which is the previous integral with $s$ replaced by $s + a$, so

$$F(s) = \frac{1}{s+a}, \qquad \mathrm{Re}(s) > -a$$

Look at what the answer is telling you. A signal that decays at rate $a$ produced a
fraction whose denominator vanishes at $s = -a$. That value of $s$ is called a **pole**,
and its position on the real axis *is* the decay rate. Every subsequent module in this
course is, in one way or another, about that correspondence.

## Linearity, and cosine for free

The transform is an integral, and integrals are linear, so

$$\mathcal{L}\{af + bg\} = aF(s) + bG(s)$$

That single property is doing more work than any other line in the module: it is why a
signal can be broken into pieces, why a fraction can be split into partial fractions
and inverted term by term, and why superposition survives the trip into the $s$-domain
and back.

Use it now, with Euler's formula, to get a pair that would be tedious to integrate
directly. $\cos\omega t = \tfrac12\big(e^{j\omega t} + e^{-j\omega t}\big)$, and each
half is the exponential you just transformed, with $a = -j\omega$ and $a = +j\omega$:

```text
L{cos w t} = 1/2 * [ 1/(s - jw)  +  1/(s + jw) ]

common denominator (s - jw)(s + jw) = s^2 + w^2

numerator      (s + jw) + (s - jw)  = 2s

           = 1/2 * 2s / (s^2 + w^2)
           = s / (s^2 + w^2)
```

The $j$s cancel, as they must — a real signal cannot have a complex transform at real
$s$. The same route with a minus sign in the middle gives
$\mathcal{L}\{\sin\omega t\} = \omega/(s^2+\omega^2)$.

## The rule the whole method rests on

Transform a derivative, integrating by parts with $u = e^{-st}$ and $dv = f'(t)\,dt$:

```text
integral from 0 to inf of  f'(t) e^(-s t) dt

  = [ f(t) e^(-s t) ]  from 0 to inf   +  s * integral of f(t) e^(-s t) dt

at t -> infinity :   f(t) e^(-s t) -> 0     (inside the region of convergence)
at t = 0         :   f(0) * 1 = f(0)

  = ( 0 - f(0) )  +  s F(s)
```

$$\mathcal{L}\{f'\} = sF(s) - f(0)$$

Differentiation has become multiplication by $s$, exactly as promised, with one extra
term. Integrating instead of differentiating runs the same argument backwards and gives
$\mathcal{L}\{\int_0^t f\} = F(s)/s$ — division by $s$. Note that a unit step is the
running integral of an impulse, and $\mathcal{L}\{\delta(t)\} = 1$, so
$\mathcal{L}\{1\} = 1/s$ falls out of the integration rule as well as out of the direct
integral. The table is consistent with itself, which is a good sign.

## Worked, with numbers: a capacitor that was not empty

A 9 V supply is connected at $t = 0$ through $R = 2.2\ \mathrm{k}\Omega$ to a
$C = 100$ nF capacitor that is already sitting at 3 V. What does the capacitor voltage
do?

Kirchhoff's current law at the capacitor node says the current arriving through the
resistor is the current the capacitor swallows:

$$C\frac{dv}{dt} = \frac{9 - v}{R} \qquad\Longrightarrow\qquad RC\frac{dv}{dt} + v = 9$$

Transform both sides. The left-hand side needs linearity and the derivative rule; the
right-hand side is a step, which you transformed above.

```text
RC = 2200 * 100e-9 = 2.2e-4 s = 220 us        v(0) = 3 V

  RC ( s V(s) - v(0) ) + V(s) = 9/s

  V(s) ( 1 + s RC )           = 9/s + RC * 3

  V(s) = ----9----   +   --3 RC--
          s(1 + sRC)      1 + sRC
```

Both terms need dividing through by $RC$ so that the denominators read $s + 1/\tau$
with $\tau = RC = 220\ \mu$s and $1/\tau = 4545\ \mathrm{rad/s}$:

```text
  3 RC / (1 + s RC)   =   3 / (s + 1/tau)

  9 / (s (1 + s RC))  =   9/s  -  9 / (s + 1/tau)     (split; module 2 does this
                                                       properly, by residues)

  V(s) = 9/s  -  9/(s + 1/tau)  +  3/(s + 1/tau)
       = 9/s  -  6/(s + 4545)
```

Two table entries invert that: $1/s \to 1$ and $1/(s+a) \to e^{-at}$.

$$v(t) = 9 - 6\,e^{-t/\tau}\ \mathrm{V}, \qquad \tau = 220\ \mu\mathrm{s}$$

Check it at both ends before trusting it. At $t = 0$ the exponential is 1 and
$v = 9 - 6 = 3$ V, which is where the capacitor started. As $t \to \infty$ the
exponential dies and $v \to 9$ V, which is the supply. Now put a number in the middle,
say $t = 300\ \mu$s:

```text
t / tau       = 300e-6 / 220e-6      = 1.3636
e^(-1.3636)                          = 0.25573
v(300 us)     = 9 - 6 * 0.25573      = 9 - 1.5344   = 7.466 V
```

There was no calculus in any of that. There was one derivative rule, one table lookup
twice, and school algebra in between. Notice in particular where the 3 V went: it
entered through the $-f(0)$ term of the derivative rule, travelled through the algebra
as an ordinary additive term, and came out having changed the *size* of the exponential
from 9 to 6 without moving the pole at all. The circuit still settles with the same
220 µs time constant it would have had from empty.

## The mistake people actually make

Dropping the $-f(0)$.

It is tempting for two reasons. The first is that "differentiation becomes
multiplication by $s$" is the slogan, and $sF(s)$ is the pretty half of the rule; the
initial condition looks like an administrative detail bolted on afterwards. The second
is that most worked problems start from rest, so $f(0) = 0$ and the term genuinely
vanishes — which means you can drop it for weeks and never be corrected, right up to
the first problem where a capacitor was charged.

The symptom is distinctive and worth memorising: an answer that *settles* to the right
value but *starts* at the wrong one. In the worked example above, dropping the 3 V
gives $v(t) = 9(1 - e^{-t/\tau})$, which is correct at infinity, correct in its time
constant, and wrong at every finite time.

A second, rarer error: assuming $\mathcal{L}\{f\cdot g\} = F(s)G(s)$. It is not.
Multiplication in one domain is convolution in the other, and the product of two
transforms corresponds to a convolution in time — which is a genuinely useful fact, and
the reason a transfer function multiplied by an input transform gives the output.

## Where this stops holding

- **Signals that outrun every exponential.** $e^{t^2}$ has no Laplace transform at any
  $s$, because no probe decays fast enough to make the integral converge. This is not a
  practical worry for circuits, but the region of convergence becomes essential the
  moment the transform is allowed to run from $-\infty$: there, the same algebraic
  $F(s)$ can belong to two different signals, told apart only by which region of $s$
  it converges in. The one-sided transform above sidesteps that by insisting the
  signal is zero before $t = 0$.
- **Anything before $t = 0$.** The transform is one-sided by construction. A signal
  that has been running forever is the Fourier transform's business, and the Fourier
  transform is this one evaluated on the line $\sigma = 0$.
- **Anything nonlinear or time-varying.** Linearity is what the whole apparatus is
  built on. A diode, a transistor driven beyond its small-signal range, a resistor
  whose value changes as it heats — none of these transform, and no amount of algebra
  rescues them. EE201 handles the first two by linearising about an operating point,
  which is the standard trick: transform the small deviations, not the signal itself.
- **Distributed structures.** A metre of coaxial cable is not a lumped $L$ and $C$; its
  transfer function contains $e^{-s\ell/v}$, which is not a ratio of polynomials, and
  the pole-and-zero language of the next module does not describe it. EMAG510 is where
  that begins.
''',
                },
                {
                    "title": "Impedance in $s$, and reading a circuit off its poles",
                    "minutes": 11,
                    "body": r'''
The previous unit transformed a *signal*. This one transforms a *circuit*, and it is
where the method stops being an exercise in integration and starts being faster than
what it replaces.

You have met most of this already without the letter $s$. In EE102 a capacitor driven
by a sinusoid was given an impedance $1/(j\omega C)$: a number, in ohms, that behaves
in Ohm's law exactly as a resistance does, except that it is complex and depends on
frequency. The derivation there assumed the sinusoid had been running forever, which is
why phasors say nothing about switch-on. The generalisation is almost embarrassingly
small — replace $j\omega$ by $s$ — but the thing it buys is large, because $s$ covers
decaying and growing exponentials as well as steady sinusoids, and a switched circuit
is full of those.

## Where $sL$ and $1/(sC)$ come from

Take the inductor's defining rule and transform it, using the derivative rule from the
previous unit:

$$v = L\frac{di}{dt} \qquad\Longrightarrow\qquad V(s) = sL\,I(s) - L\,i(0)$$

If the inductor starts with no current, the second term is zero and what is left is
$V(s) = (sL)\,I(s)$: voltage equals current times something. That something is the
**impedance** $Z_L = sL$. The capacitor runs the same way from $i = C\,dv/dt$:

$$I(s) = sC\,V(s) - C\,v(0) \qquad\Longrightarrow\qquad Z_C = \frac{1}{sC}$$

again for a part that starts empty. A resistor has nothing to transform, so
$Z_R = R$ unchanged.

Two things about those initial-condition terms. They are not being ignored — they are
being *postponed*. $L\,i(0)$ and $C\,v(0)$ have the units of a voltage source and a
current source respectively, and module 4 puts them back on the schematic as exactly
that. For now, assume everything starts at rest, which is what "the circuit is at rest
before the switch closes" means when a question says it.

## Everything you already know survives

This is the payoff, and it is worth stating plainly. Impedances in $s$ obey Ohm's law,
so *every* consequence of Ohm's law comes with them unchanged:

- impedances in series add: $Z = Z_1 + Z_2$
- impedances in parallel combine as $Z_1Z_2/(Z_1+Z_2)$
- the divider rule holds: $V_{out} = V_{in}\,Z_2/(Z_1+Z_2)$
- Kirchhoff's laws, node equations, Thévenin and Norton — all of it

The only change is that the quantities being added and divided are now ratios of
polynomials in $s$ rather than numbers. You are doing EE101 with fractions.

## Worked: an RC low-pass, with numbers

$R = 4.7\ \mathrm{k}\Omega$ in series with $C = 33$ nF, output across the capacitor, a
5 V step applied at $t = 0$ to a circuit at rest.

```text
Z_R = 4700              Z_C = 1/(sC) = 1/(33e-9 s)

divider:   H(s) = Vout/Vin = Z_C / (Z_R + Z_C)
                           = [1/(sC)] / [R + 1/(sC)]

multiply top and bottom by sC:

           H(s) = 1 / (1 + s R C)

R C = 4700 * 33e-9 = 1.551e-4 s = 155.1 us
```

$H(s)$ is the **transfer function**: what the circuit does, with no mention of what you
are going to feed it. Its denominator vanishes at $1 + sRC = 0$, that is at
$s = -1/(RC) = -6447$ rad/s, and that single pole is everything the circuit has to say
about itself.

Now choose an input. A 5 V step has transform $5/s$, so

```text
Vout(s) = H(s) * Vin(s) = ----------5----------
                            s (1 + 1.551e-4 s)

split (module 2 does this by residues; the shape is standard):

        = 5/s  -  5/(s + 6447)

invert, term by term:

vout(t) = 5 ( 1 - e^(-t / 155.1us) )   volts
```

Two numbers out of it, to see that it is a real answer and not a shape:

```text
at t = 100 us :  t/tau = 100/155.1 = 0.64475
                 e^(-0.64475) = 0.52480
                 vout = 5 * (1 - 0.52480) = 5 * 0.47520 = 2.376 V

at t = 155.1 us (one time constant):
                 e^(-1) = 0.36788
                 vout = 5 * 0.63212 = 3.161 V
```

Notice which pole did which job. The pole at $s = 0$ came from the *input* — it is the
step's own pole — and it produced the constant 5 that the output settles at. The pole
at $-6447$ came from the *circuit*, and it produced the decaying exponential. That
split holds for every linear circuit: input poles give the part of the response that
persists, circuit poles give the part that dies away.

## Poles, zeros, and why they are the whole story

Write a transfer function as a ratio of polynomials, $H(s) = N(s)/D(s)$. The roots of
$D$ are the **poles**; the roots of $N$ are the **zeros**. Zeros shape how much of each
frequency gets through. Poles decide what the circuit does when left alone, and they do
it through one fact: a simple pole at $s = p$ contributes a term $A\,e^{pt}$ to the
response, and nothing else.

Since $p = \sigma + j\omega$, that term is $A e^{\sigma t}e^{j\omega t}$, so

- the **real part** $\sigma$ is the decay rate. It is negative for a circuit that
  settles, and its size is speed: a pole at $-6447$ rad/s decays with a time constant of
  $1/6447 = 155\ \mu$s. A pole in the right half-plane, $\sigma > 0$, grows without
  bound, which is what instability means.
- the **imaginary part** $\omega$ is the ringing rate, in radians per second. It says
  nothing at all about how long the response lasts.

Poles are also, always, in radians per second, never in hertz. A pole at $-6447$ rad/s
belongs to a corner frequency of $6447/2\pi = 1026$ Hz, and confusing the two is a
factor of 6.28 that has ruined a great many otherwise correct answers.

## Worked: a series RLC, and its response read off two numbers

$L = 0.1$ H, $R = 100\ \Omega$, $C = 2.5\ \mu$F in series, output taken across the
capacitor. Same divider, one more impedance in the chain:

```text
H(s) =        Z_C
        ---------------------
         Z_L + Z_R + Z_C

     =          1/(sC)
        ---------------------
         sL + R + 1/(sC)

multiply top and bottom by sC:

H(s) = -----------1------------
        s^2 L C + s R C + 1
```

Compare that with the standard second-order form
$H = \omega_n^2/(s^2 + 2\zeta\omega_n s + \omega_n^2)$. To match it, divide top and
bottom by $LC$, which turns the denominator into $s^2 + (R/L)s + 1/(LC)$ and lets the
two coefficients be read straight off:

```text
wn = 1 / sqrt(L C) = 1 / sqrt(0.1 * 2.5e-6)
                   = 1 / sqrt(2.5e-7)
                   = 1 / 5e-4               = 2000 rad/s   (318.3 Hz)

2 zeta wn = R / L  = 100 / 0.1              = 1000
zeta      = 1000 / (2 * 2000)               = 0.25

poles at  s = -zeta*wn  +/-  j*wn*sqrt(1 - zeta^2)
          = -500  +/-  j * 2000 * sqrt(0.9375)
          = -500  +/-  j 1936.5
```

Everything the circuit does when you step it is now readable off those two numbers,
without inverting anything:

```text
decay envelope    e^(-500 t),  so a 1/500 = 2 ms envelope time constant
settles (to 2%)   about 4 envelope time constants        = 8 ms
ringing period    2 pi / 1936.5                          = 3.245 ms
cycles of ring    8 ms / 3.245 ms                        = about 2.5
```

So: it overshoots, rings for roughly two and a half visible cycles at 308 Hz, and is
done in about 8 ms. That prediction cost four divisions. The sandbox in this module is
the same statement made draggable. Its $\omega_n$ slider stops at 12 rad/s, which costs
nothing: $\omega_n$ sets only the clock on the time axis and $\zeta$ sets the shape. Put
$\zeta = 0.25$ into it and the curve is the one just described, running slowly.

## The final value theorem, and the way it lies

Sometimes the only thing wanted is where the response ends up, and there is a shortcut
that skips the inversion entirely:

$$\lim_{t\to\infty}f(t) = \lim_{s\to 0}sF(s)$$

For the RC above, $sV_{out}(s) = 5/(1 + 1.551\!\times\!10^{-4}s)$, which at $s = 0$ is
5 V — correct, and obtained without a single exponential. For the RLC stepped from
rest, $sV_{out}(s) = H(s)$, and $H(0) = 1$, so the capacitor ends up at the full input
value. Also correct, and it explains why: at DC the inductor is a short and the
capacitor an open, so the whole source appears across the capacitor.

The theorem has a precondition, and it is the kind that does not announce itself.
Every pole of $sF(s)$ must have a strictly negative real part — the response has to
actually settle. Apply it to $F(s) = \omega/(s^2+\omega^2)$, the transform of a sine
that oscillates forever, and $sF(s) = s\omega/(s^2+\omega^2)$ evaluates to 0 at $s = 0$.
The theorem returns "it settles at zero", confidently, about a signal that never
settles at anything. Apply it to an unstable circuit and it will likewise report a
tidy finite number for a voltage heading off to the rails.

The check is quick, so do it: factor the denominator, look at the poles, and only then
use the shortcut.

## The mistakes people actually make

**Using $H(s)$ as if it were the answer.** The transfer function is the circuit; the
response is $H(s)$ times the transform of whatever you applied. Forgetting the input's
$1/s$ turns a step response into an impulse response, and the two look nothing alike —
one settles at a constant, the other returns to zero. It is tempting because $H(s)$ is
the thing you worked hard to derive, and because for the impulse, uniquely, the two
coincide.

**Reading the imaginary part as the speed.** Poles at $-3 \pm j100$ look dramatic and
poles at $-0.5 \pm j2$ look tame, and the second pair takes six times longer to die
away. Height above the axis is how fast it wiggles; distance to the left of it is how
fast it stops.

**Applying the divider rule to a loaded output.** $V_{out} = V_{in}Z_2/(Z_1+Z_2)$
assumes the same current flows through both impedances. Hang anything on the output
node that draws current — including the next stage's input impedance — and the rule is
simply false. In the $s$-domain this bites more often than in DC, because the thing
loading the node is frequently a capacitor that looked harmless at low frequency.

## Where this stops holding

- **A circuit that did not start at rest.** Everything above dropped $L\,i(0)$ and
  $C\,v(0)$. Module 4 restores them as sources sitting alongside the impedances, and
  nothing else in the method changes.
- **Anything nonlinear.** An impedance is a linear relation between $V(s)$ and $I(s)$;
  a diode has no such relation. Small-signal linearisation about an operating point is
  the standard escape, and it is why EE201 spends so long on bias points.
- **Parts that are not really lumped.** Above a few hundred MHz a wire has inductance
  along its length and capacitance to everything near it, and the tidy
  three-impedance chain above stops describing the board you built. RFIC510 and
  EMAG510 take that up.
- **The poles are not the *whole* story about gain.** They fix the shape of the
  transient exactly, but the size of each term — the residue $A$ multiplying
  $e^{pt}$ — depends on the zeros and on the input. Module 2 computes those residues,
  and it is the piece this unit deliberately left out.
''',
                },
            ],
            "sandbox": {
                "title": "Where the poles are, and what the circuit does",
                "visualiser": "pole-step",
                "minutes": 9,
                "initial": {"zeta": 0.5, "wn": 4},
                "brief": r'''
Solving a circuit with Laplace gives a fraction in $s$. The roots of its denominator
are called the **poles**, and they are the whole story: from their positions alone you
can say whether the response overshoots, how long it rings and how quickly it settles,
without ever inverting the transform.

The left-hand plot is the complex $s$-plane, with $\sigma$ across and $j\omega$ up.
The two dots are the poles of a standard second-order system

$$H(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

whose roots sit at $s = -\zeta\omega_n \pm j\omega_n\sqrt{1-\zeta^2}$. The right-hand
plot is the step response those two poles produce, with a dashed line at the final
value of 1.

Move the sliders and watch the two pictures move together. This pairing is the single
most useful mental image in the rest of the degree.
''',
                "notice": [
                    "It opens at $\\zeta = 0.5$, $\\omega_n = 4$. Both poles sit at a real part of $-2$, one above the horizontal axis and one the same distance below it, and the plot labels the height $\\omega_d = 3.46$. On the right the curve climbs past the dashed line to about 1.16, dips below, and settles. The readout underneath reports 16.3% overshoot and settling in about 2 s.",
                    "Drag $\\zeta$ down to 0. The two dots slide onto the vertical axis, at $\\pm j4$, and the step response never settles at all — it swings between 0 and 2 for as long as the plot runs. The real part of a pole *is* the decay rate, so with no real part there is no decay.",
                    "Now take $\\zeta$ up to 1.6. The dots change colour, drop onto the horizontal axis, and the label changes to 'both poles real'. They separate, one drifting in towards about $-1.4$ and the other out to about $-11.4$. The response no longer overshoots — and it is so sluggish that by the right-hand edge of the plot it has only reached about 0.92, still short of the dashed line. That near pole is what makes it slow.",
                    "Put $\\zeta$ back to 0.5 and drag $\\omega_n$ from 4 up to 12. The pair slides outwards along the same straight ray, keeping its angle of 60° from the negative real axis. The step curve keeps its exact shape while the numbers along the time axis shrink by a factor of three: the angle sets the shape, the distance from the origin sets the speed.",
                ],
            },
            "blanks": [
                {
                    "title": "The table, and the rules that do the work",
                    "minutes": 9,
                    "caption": "every entry below is for a signal that is zero before t = 0",
                    "lang": "text",
                    "brief": r'''
This is the sheet you will reach for in every remaining module of the course, so it is
worth filling in by hand once rather than photographing.

The pairs are the easy half — they are looked up. The rules underneath are where the
method lives: they are what let a differential equation become a polynomial, and a
capacitor become something Ohm's law can handle.
''',
                    "listing": """PAIRS

    f(t)                    F(s)                    the integral converges for
    ----------------------------------------------------------------------------
    delta(t)                1                       every s
    1     (a unit step)     1/s                     Re(s) > ___
    e^(-a t)                ___                     Re(s) > -a
    t                       1/s^2                   Re(s) > 0
    t e^(-a t)              1/(s + a)^2             Re(s) > -a
    sin(w t)                w / (s^2 + w^2)         Re(s) > 0
    cos(w t)                ___                     Re(s) > 0

RULES

    a f(t) + b g(t)         a F(s) + b G(s)
    df/dt                   ___
    integral of f, 0 to t   F(s) / s

IMPEDANCES, for a part that starts at rest

    resistor R              R
    inductor L              s L
    capacitor C             ___

ENDPOINTS, when the response actually settles

    f at 0+                 limit as s -> infinity of   s F(s)
    f at infinity           limit as s -> 0 of          ___
""",
                    "blanks": [
                        {
                            "prompt": "The half-plane in which the step's integral converges.",
                            "hole": "?",
                            "opts": ["0", "-1", "1", "-infinity"],
                            "a": 0,
                            "why": "The integrand is $e^{-st}$, which dies away only when $\\mathrm{Re}(s) > 0$. So the transform of a step exists strictly to the right of the imaginary axis, and its pole sits exactly on the boundary at $s = 0$ — which is the general pattern: the region of convergence is the half-plane to the right of the rightmost pole.",
                            "whys": [
                                "The integrand is $e^{-st}$, which dies away only when $\\mathrm{Re}(s) > 0$. So the transform of a step exists strictly to the right of the imaginary axis, and its pole sits exactly on the boundary at $s = 0$ — which is the general pattern: the region of convergence is the half-plane to the right of the rightmost pole.",
                                "$-1$ would be the boundary for $e^{+t}$, a signal that grows. A step neither grows nor decays, so its boundary sits at zero and not to the left of it.",
                                "1 is too strict. At $s = 0.5$, say, $e^{-0.5t}$ still decays and the integral still converges to $1/0.5 = 2$; nothing goes wrong until $\\mathrm{Re}(s)$ actually reaches zero.",
                                "Convergence everywhere is what an impulse gets, because the integral collapses at $t = 0$ before $e^{-st}$ has had any chance to misbehave. A step lasts forever, so it is fussier.",
                            ],
                        },
                        {
                            "prompt": "The transform of a decaying exponential.",
                            "hole": "?",
                            "opts": ["1/(s + a)", "1/(s - a)", "a/(s + a)", "1/(s^2 + a^2)"],
                            "a": 0,
                            "why": "$\\int_0^\\infty e^{-at}e^{-st}dt = \\int_0^\\infty e^{-(s+a)t}dt = 1/(s+a)$ — the step's integral with $s$ replaced by $s+a$. The pole is at $s = -a$, on the negative real axis, and its distance from the origin is the decay rate.",
                            "whys": [
                                "$\\int_0^\\infty e^{-at}e^{-st}dt = \\int_0^\\infty e^{-(s+a)t}dt = 1/(s+a)$ — the step's integral with $s$ replaced by $s+a$. The pole is at $s = -a$, on the negative real axis, and its distance from the origin is the decay rate.",
                                "$1/(s-a)$ is the transform of $e^{+at}$, a signal that grows without bound. Its pole is in the right half-plane, which is precisely the signature of instability.",
                                "An extra $a$ on top would make the transform of $e^{-at}$ depend on the rate twice over. Check it at $a = 0$: the signal becomes a step and the answer has to collapse to $1/s$, which $a/(s+a)$ does not.",
                                "$1/(s^2+a^2)$ has poles at $\\pm ja$, on the imaginary axis, so it belongs to something that oscillates forever rather than decays. It is $(1/a)\\sin at$.",
                            ],
                        },
                        {
                            "prompt": "The transform of a cosine.",
                            "hole": "?",
                            "opts": ["s / (s^2 + w^2)", "w / (s^2 + w^2)", "1 / (s^2 + w^2)", "s / (s^2 - w^2)"],
                            "a": 0,
                            "why": "Write $\\cos\\omega t = \\tfrac12(e^{j\\omega t} + e^{-j\\omega t})$, transform each half with the exponential pair, and put them over the common denominator $s^2+\\omega^2$: the numerators add to $2s$ and the half cancels it to $s$. The $s$ on top is a zero at the origin, and it is what distinguishes cosine from sine — a cosine starts at 1 rather than 0.",
                            "whys": [
                                "Write $\\cos\\omega t = \\tfrac12(e^{j\\omega t} + e^{-j\\omega t})$, transform each half with the exponential pair, and put them over the common denominator $s^2+\\omega^2$: the numerators add to $2s$ and the half cancels it to $s$. The $s$ on top is a zero at the origin, and it is what distinguishes cosine from sine — a cosine starts at 1 rather than 0.",
                                "$\\omega$ on top is the sine, printed two lines above. The two pairs share a denominator and are told apart entirely by their numerator, which is the one thing worth memorising about them.",
                                "A bare 1 on top gives $(1/\\omega)\\sin\\omega t$ — the right shape, scaled wrongly. The initial-value theorem catches it in a line: $sF(s) \\to 0$ as $s \\to \\infty$, but a cosine starts at 1.",
                                "$s^2 - \\omega^2$ factorises into $(s-\\omega)(s+\\omega)$, giving real poles at $\\pm\\omega$ and a hyperbolic cosine, which grows. Nothing oscillates unless the poles are off the real axis.",
                            ],
                        },
                        {
                            "prompt": "What differentiation becomes.",
                            "hole": "?",
                            "opts": ["s F(s) - f(0)", "s F(s)", "s F(s) + f(0)", "F(s) / s"],
                            "a": 0,
                            "why": "Integration by parts gives $[f e^{-st}]_0^\\infty + sF(s)$, and the boundary term is $0 - f(0)$. That $-f(0)$ is how an initial condition enters the algebra, and it is the single most commonly dropped term in the subject: leave it out and the answer settles correctly but starts in the wrong place.",
                            "whys": [
                                "Integration by parts gives $[f e^{-st}]_0^\\infty + sF(s)$, and the boundary term is $0 - f(0)$. That $-f(0)$ is how an initial condition enters the algebra, and it is the single most commonly dropped term in the subject: leave it out and the answer settles correctly but starts in the wrong place.",
                                "$sF(s)$ alone is the rule with the initial condition silently set to zero. It is right for a circuit starting from rest and wrong for every other one, which is exactly why it survives so long undetected.",
                                "A plus sign would make a charged capacitor start *below* where it really does. Sanity-check the sign on the simplest case: $f(t) = 1$, $f' = 0$, $F = 1/s$, so the rule must give $s(1/s) - 1 = 0$, and only the minus does.",
                                "$F(s)/s$ is the *integration* rule. The two are mirror images, and the way to keep them apart is dimensional: differentiating makes a signal change faster, and multiplying by $s$ makes the transform grow at large $s$.",
                            ],
                        },
                        {
                            "prompt": "The impedance of a capacitor in the $s$-domain.",
                            "hole": "?",
                            "opts": ["1/(sC)", "sC", "C/s", "1/(s^2 C)"],
                            "a": 0,
                            "why": "$i = C\\,dv/dt$ transforms to $I = sCV$ for a capacitor starting empty, and impedance is $V/I$, so $Z_C = 1/(sC)$. Set $s = j\\omega$ and it becomes the $1/(j\\omega C)$ from EE102, as it must — the phasor result is this one restricted to the imaginary axis.",
                            "whys": [
                                "$i = C\\,dv/dt$ transforms to $I = sCV$ for a capacitor starting empty, and impedance is $V/I$, so $Z_C = 1/(sC)$. Set $s = j\\omega$ and it becomes the $1/(j\\omega C)$ from EE102, as it must — the phasor result is this one restricted to the imaginary axis.",
                                "$sC$ is the *admittance*, the reciprocal. It is the more convenient quantity for node equations and the wrong one for a divider, so it is worth writing down which of the two you are holding.",
                                "$C/s$ has the capacitance on top, so doubling the capacitance would double the impedance. A bigger capacitor passes current more easily, not less.",
                                "$1/(s^2C)$ is the impedance of nothing. A quick check: impedance must fall as $1/s$ for a capacitor and rise as $s$ for an inductor, so that a series LC has a $1/s$ and an $s$ to combine into the $s^2$ of a second-order denominator.",
                            ],
                        },
                        {
                            "prompt": "The quantity whose limit at $s = 0$ is the final value.",
                            "hole": "?",
                            "opts": ["s F(s)", "F(s)", "F(s) / s", "s^2 F(s)"],
                            "a": 0,
                            "why": "$sF(s)$, and the multiplication by $s$ is the whole trick: a settling response has a pole at the origin carrying its steady part, and the $s$ cancels it so that something finite is left to evaluate. The precondition is that every remaining pole of $sF(s)$ sits strictly in the left half-plane — apply it to a sine, which never settles, and it reports 0 with complete confidence.",
                            "whys": [
                                "$sF(s)$, and the multiplication by $s$ is the whole trick: a settling response has a pole at the origin carrying its steady part, and the $s$ cancels it so that something finite is left to evaluate. The precondition is that every remaining pole of $sF(s)$ sits strictly in the left half-plane — apply it to a sine, which never settles, and it reports 0 with complete confidence.",
                                "$F(s)$ on its own diverges at $s = 0$ for any response that settles anywhere but zero, because the settling value is carried by a pole at the origin. Try it on $F = 1/s$: the answer is infinite, and the signal is a 1 V step.",
                                "Dividing by $s$ goes the wrong way — it adds a pole at the origin instead of cancelling one, which is the transform of integrating the signal rather than reading its endpoint.",
                                "$s^2F(s)$ over-cancels. On $F = 1/s$ it gives 0, and the step it describes settles at 1. Only one factor of $s$ is wanted, matching the one pole the input contributed.",
                            ],
                        },
                    ],
                },
                {
                    "title": "An RL circuit solved in $s$, line by line",
                    "minutes": 9,
                    "caption": "a 12 V step into 240 Ω in series with 60 mH, output across the resistor",
                    "lang": "text",
                    "brief": r'''
The RC in this module's guided derivation is done with letters. This one is the same
method with numbers in it from the first line, and an inductor instead of a capacitor,
so that nothing is being remembered by shape.

Everything below is the divider rule from EE101 with impedances that contain $s$.
Nothing is executed; this is arithmetic you are choosing.
''',
                    "listing": """A 12 V step is applied at t = 0 to a 240 ohm resistor in series with a
60 mH inductor, at rest beforehand.  The output is across the resistor.

    impedances     Z_R = 240                 Z_L = ___

    divider        V_R(s) = V_in(s) * Z_R / (Z_R + Z_L)

    the input      V_in(s) = ___

    substitute                       2880
                   V_R(s) = -------------------------
                                s (240 + 0.06 s)

    divide top and                    12
    bottom by 240  V_R(s) = -------------------------
                                s (1 + ___ * s)

    the pole       the circuit's pole sits at s = ___ rad/s

    invert         v_R(t) = 12 (1 - e^(-t/tau))  volts,   tau = 250 us

    a number       v_R at t = 250 us  =  ___ V
""",
                    "blanks": [
                        {
                            "prompt": "The inductor's impedance, with $L = 60$ mH.",
                            "hole": "?",
                            "opts": ["0.06 s", "0.06 / s", "60 s", "s / 0.06"],
                            "a": 0,
                            "why": "$Z_L = sL$, and $L = 60\\ \\mathrm{mH} = 0.06$ H, so $Z_L = 0.06s$. It rises with $s$: an inductor obstructs fast changes and lets slow ones through, which is the opposite of what the capacitor does.",
                            "whys": [
                                "$Z_L = sL$, and $L = 60\\ \\mathrm{mH} = 0.06$ H, so $Z_L = 0.06s$. It rises with $s$: an inductor obstructs fast changes and lets slow ones through, which is the opposite of what the capacitor does.",
                                "$0.06/s$ is the shape of a *capacitor's* impedance, falling as $s$ grows. Swapping the two is the commonest slip on this line, and the consequence is a circuit that filters the wrong way round.",
                                "60 is the inductance in millihenries. Base units before anything else: 60 mH is 0.06 H, and the factor of a thousand would move the pole from 4000 rad/s to 4 rad/s.",
                                "$s/0.06$ divides by the inductance instead of multiplying, so a bigger inductor would obstruct less. It also has the wrong units: impedance is $sL$, in ohms when $L$ is in henries.",
                            ],
                        },
                        {
                            "prompt": "The transform of the input.",
                            "hole": "?",
                            "opts": ["12 / s", "12", "12 s", "1 / s"],
                            "a": 0,
                            "why": "A 12 V step is 12 times the unit step, and $\\mathcal{L}\\{1\\} = 1/s$, so by linearity $V_{in}(s) = 12/s$. This is the step the transfer function does not contain: $Z_R/(Z_R+Z_L)$ is the circuit, $12/s$ is what you chose to apply to it.",
                            "whys": [
                                "A 12 V step is 12 times the unit step, and $\\mathcal{L}\\{1\\} = 1/s$, so by linearity $V_{in}(s) = 12/s$. This is the step the transfer function does not contain: $Z_R/(Z_R+Z_L)$ is the circuit, $12/s$ is what you chose to apply to it.",
                                "A bare 12 is the transform of a 12 V *impulse*, not a step — and an impulse response returns to zero instead of settling at 12 V. Leaving the input untransformed is the standard way to produce it by accident.",
                                "$12s$ grows without bound at large $s$, which by the initial-value theorem would mean a signal that is infinite the instant it starts. Multiplying by $s$ is differentiating; the step is the *integral* of an impulse, so it divides.",
                                "$1/s$ is the unit step, with the 12 V dropped. Linearity means the 12 rides along untouched, so it must appear somewhere — and if it is missing here it will be missing from the final answer too.",
                            ],
                        },
                        {
                            "prompt": "The coefficient of $s$ once the bracket has been normalised.",
                            "hole": "?",
                            "opts": ["0.00025", "0.06", "4000", "0.25"],
                            "a": 0,
                            "why": "Dividing $240 + 0.06s$ by 240 gives $1 + (0.06/240)s = 1 + 0.00025s$. That coefficient is the time constant in seconds: $\\tau = L/R = 0.06/240 = 250\\ \\mu$s. Normalising the constant term to 1 is worth doing every time, because the coefficient of $s$ then reads off as $\\tau$ with no further work.",
                            "whys": [
                                "Dividing $240 + 0.06s$ by 240 gives $1 + (0.06/240)s = 1 + 0.00025s$. That coefficient is the time constant in seconds: $\\tau = L/R = 0.06/240 = 250\\ \\mu$s. Normalising the constant term to 1 is worth doing every time, because the coefficient of $s$ then reads off as $\\tau$ with no further work.",
                                "0.06 is the inductance, left undivided. The whole point of the step is that both terms in the bracket are divided by 240, not just the first.",
                                "4000 is $R/L$, which is $1/\\tau$ — the pole magnitude rather than the time constant. It is the reciprocal of the wanted number, and the two are easy to swap because both are called \"the\" characteristic number of the circuit.",
                                "0.25 is 250 µs read as though the microseconds were milliseconds. The arithmetic $0.06/240$ genuinely gives $2.5\\times10^{-4}$, and a factor of a thousand here moves the answer at 250 µs from 7.59 V to essentially zero.",
                            ],
                        },
                        {
                            "prompt": "Where the pole sits.",
                            "hole": "?",
                            "opts": ["-4000", "-0.00025", "+4000", "-240"],
                            "a": 0,
                            "why": "The denominator $1 + 0.00025s$ vanishes at $s = -1/0.00025 = -4000$ rad/s, which is $-R/L$. Negative and real: the response decays without ringing, at a rate of 4000 nepers per second, which is the 250 µs time constant said the other way round.",
                            "whys": [
                                "The denominator $1 + 0.00025s$ vanishes at $s = -1/0.00025 = -4000$ rad/s, which is $-R/L$. Negative and real: the response decays without ringing, at a rate of 4000 nepers per second, which is the 250 µs time constant said the other way round.",
                                "$-0.00025$ is the time constant with a minus sign in front, not the pole. A pole is a value of $s$, and $s$ has units of inverse seconds — so anything measured in seconds cannot be one.",
                                "A pole in the right half-plane means $e^{+4000t}$, a response that doubles every 173 µs until something breaks. A resistor and an inductor cannot produce that; passive parts only dissipate.",
                                "$-240$ is the resistance with a sign attached. Ohms are not radians per second: the pole is $R/L$, and it needs both parts, which is why the same 240 Ω with a 6 mH inductor would put the pole ten times further out.",
                            ],
                        },
                        {
                            "prompt": "The output one time constant in.",
                            "hole": "?",
                            "opts": ["7.59", "4.41", "12.0", "0.632"],
                            "a": 0,
                            "why": "$v_R = 12(1 - e^{-1}) = 12 \\times 0.6321 = 7.585$ V. One time constant closes 63.2% of whatever gap remains, always — the number is a property of $e$, not of this circuit, which is why it is worth knowing to three figures.",
                            "whys": [
                                "$v_R = 12(1 - e^{-1}) = 12 \\times 0.6321 = 7.585$ V. One time constant closes 63.2% of whatever gap remains, always — the number is a property of $e$, not of this circuit, which is why it is worth knowing to three figures.",
                                "4.41 V is $12e^{-1}$, which is the part still *missing* rather than the part arrived. It is also the voltage across the inductor at that instant, and the two add to 12 V as Kirchhoff insists.",
                                "12.0 V is the final value, reached only as $t \\to \\infty$. At one time constant the response is well short of it; four or five are needed before the remainder stops mattering.",
                                "0.632 is the fraction, not the voltage. It still has to be multiplied by the 12 V the response is heading for.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "Where does this circuit's pole sit?",
                    "minutes": 5,
                    "brief": r'''
The mechanical one, to get the routine under your fingers. One rule, one unknown, and
the only thing that can go wrong is a unit.

The output is across the capacitor, the circuit is at rest before the step, and you are
not being asked for a voltage at all — you are being asked where the denominator of the
circuit's transfer function vanishes.
''',
                    "prompt": "This circuit has a single pole, on the negative real axis. How far is it from the origin?",
                    "note": "Give the magnitude in rad/s, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 4700},
                            {"id": "c", "kind": "C", "x": 11, "y": 6, "rot": 1, "value": 33e-9},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [11, 3], "b": [15, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "5.00 V step at t = 0"},
                        {"label": "R", "value": "4.70 kΩ"},
                        {"label": "C", "value": "33.0 nF"},
                        {"label": "State before the step", "value": "at rest"},
                    ],
                    "aside": "The divider rule with $Z_C = 1/(sC)$ gives $H(s) = 1/(1+sRC)$. A pole is a "
                             "value of $s$ that makes a denominator vanish.",
                    # The -3 dB corner of a one-pole response IS the pole magnitude, so this
                    # measures the schematic rather than repeating its labels: c.corner bisects
                    # on the swept response and the 2*pi converts hertz to rad/s.
                    "check": "return 2 * Math.PI * c.corner(1, 1e6);",
                    "answer": 6447.0,
                    "tol": 25.0,
                    "unit": "rad/s",
                    "hint": "$1 + sRC = 0$ at $s = -1/(RC)$, so the magnitude is $1/(RC)$. Put both values "
                            "into base units before dividing.",
                    "wrong": "If you got 1026, that is the same pole quoted in hertz — poles are always in "
                             "rad/s, and dividing by $2\\pi$ is one conversion too many. If you got "
                             "$1.55\\times10^{-4}$, that is the time constant in seconds, and the pole "
                             "magnitude is its reciprocal.",
                    "why": r'''
```
R C          = 4700 * 33e-9        = 1.551e-4 s   (155.1 us)

H(s)         = 1 / (1 + s R C)

denominator zero when  s = -1/(R C)

|pole|       = 1 / 1.551e-4        = 6447 rad/s
```
The same number describes three things at once, and it is worth seeing that they are
one fact rather than three. It is the reciprocal of the 155.1 µs time constant, so the
step response has fallen to $1/e$ of its gap in that time. It is the corner of the
frequency response, $6447/2\pi = 1026$ Hz, where the output is 3 dB down. And it is the
distance from the origin at which the denominator of $H(s)$ vanishes. Distance from the
imaginary axis is speed — that is the sentence to carry into the rest of the course.
''',
                },
                {
                    "title": "The current a step eventually drives through an inductor",
                    "minutes": 6,
                    "brief": r'''
A step, an inductor, and a question about the far end of the response rather than the
near end. There is a shortcut for exactly this — the final value theorem — and using it
here means you never have to invert anything.

Write the loop current as $I(s) = V_{in}(s)/(Z_R + Z_L)$, then take $\lim_{s\to0}sI(s)$.
Note before you start which quantity the prompt is asking for: it is a current, and
there is no node in this circuit whose voltage is it.
''',
                    "prompt": "What current does the circuit settle at, long after the supply is connected?",
                    "note": "Give the answer in milliamps, to the nearest milliamp.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 24},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "l", "kind": "L", "x": 8, "y": 3, "rot": 0, "value": 0.05},
                            {"id": "r", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 150},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [11, 3], "b": [15, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "24.0 V step at t = 0"},
                        {"label": "L", "value": "50.0 mH"},
                        {"label": "R", "value": "150 Ω"},
                        {"label": "Current in L before the step", "value": "zero"},
                    ],
                    "aside": "$sI(s)$ with $I(s) = 24/\\big(s(R + sL)\\big)$ is $24/(R+sL)$, and you are "
                             "asked for its value at $s = 0$. Watch what happens to the inductance when "
                             "you put $s = 0$ in.",
                    # The prompt asks for a current, which is no node of this circuit, so both
                    # factors are read out of the DC solve: the drop the resistor ends up with,
                    # and the resistance it has. Editing either part moves the measured number.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.kind === 'R'; })[0];
return 1000 * Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value;
''',
                    "answer": 160.0,
                    "tol": 2.0,
                    "unit": "mA",
                    "hint": "Put $s = 0$ into $24/(R + sL)$. The $sL$ term disappears, and what is left is "
                            "Ohm's law on the resistor alone.",
                    "wrong": "If you went looking for a reactance $\\omega L$, there is no $\\omega$ here — a "
                             "step is not a sinusoid, and the whole reason for using $s$ rather than "
                             "$j\\omega$ is that it covers inputs which are not sinusoids. If you got 0.16, "
                             "that is the answer in amperes and the prompt asked for milliamps.",
                    "why": r'''
```
I(s)      = Vin(s) / (Z_R + Z_L)  =  (24/s) / (150 + 0.05 s)

s I(s)    = 24 / (150 + 0.05 s)

at s = 0  = 24 / 150             = 0.160 A   = 160 mA
```
The inductance vanished from the answer, and that is the physics rather than an
accident of the algebra: an inductor opposes *change*, and once nothing is changing it
is a piece of wire. What the 50 mH does control is how long "eventually" takes. The
pole sits at $s = -R/L = -150/0.05 = -3000$ rad/s, a time constant of 333 µs, so the
current is within 2% of its final value after about 1.3 ms. Ten times the inductance
would give the same 160 mA ten times more slowly.

Before using the theorem, check its precondition: the only pole of $sI(s)$ is at
$-3000$, comfortably in the left half-plane, so the response really does settle and the
shortcut is legitimate.
''',
                },
                {
                    "title": "A transform evaluated where the lab evaluates it",
                    "minutes": 8,
                    "brief": r'''
No circuit this time — a signal, and the transform of it. The lab in this module
computes $\int_0^\infty f(t)e^{-st}\,dt$ numerically at real values of $s$; this is the
same number obtained the other way, from linearity and three table entries.

Three terms, three pairs, one sum. Keep track of the units as you go: $f$ is in volts
and $F$ is in volt-seconds, because the integral carries a $dt$.
''',
                    "prompt": "What is $V(s)$ at $s = 2\\ \\mathrm{s}^{-1}$?",
                    "note": "Give the answer in volt-seconds, to four significant figures.",
                    "figure": "A signal is zero for $t < 0$ and, for $t \\ge 0$, is "
                              "$v(t) = 3 - 2e^{-5t} + 4t\\,e^{-5t}$ volts, with $t$ in seconds. "
                              "It is fed to nothing; the question is about the signal alone.",
                    "given": [
                        {"label": "Signal, for $t \\ge 0$", "value": "$3 - 2e^{-5t} + 4te^{-5t}$ V"},
                        {"label": "Where to evaluate the transform", "value": "$s = 2\\ \\mathrm{s}^{-1}$"},
                        {"label": "Pairs you need", "value": "$1 \\to 1/s$, $e^{-at} \\to 1/(s+a)$, $te^{-at} \\to 1/(s+a)^2$"},
                    ],
                    "aside": "Linearity lets you transform the three terms separately and add, keeping each "
                             "constant out in front. Nothing here needs an integral to be done by hand.",
                    "answer": 1.2959,
                    "tol": 0.004,
                    "unit": "V·s",
                    "hint": "$V(s) = 3/s - 2/(s+5) + 4/(s+5)^2$. Now put $s = 2$ into it, so that every "
                            "$(s+5)$ becomes a 7.",
                    "wrong": "If you got 1.7857, the $te^{-5t}$ term was transformed as another "
                             "$1/(s+5)$ — the extra factor of $t$ squares the denominator, it does not "
                             "leave it alone. If you got 1.8673, the middle term was added rather than "
                             "subtracted; the signal starts at $3 - 2 = 1$ V, not at 5 V, and the sign has "
                             "to survive the transform.",
                    "why": r'''
```
term by term, with linearity keeping the constants outside:

    3            ->   3/s
   -2 e^(-5t)    ->  -2/(s + 5)
   +4 t e^(-5t)  ->  +4/(s + 5)^2

V(s) = 3/s  -  2/(s+5)  +  4/(s+5)^2

at s = 2, every (s + 5) is 7:

    3/2                    =  1.500000
   -2/7                    = -0.285714
   +4/49                   = +0.081633
                             ----------
    V(2)                   =  1.295918  V.s
```
Two things worth taking from the arithmetic. The first is that the three poles are at
$s = 0$, $s = -5$ and $s = -5$ again, and none of them is anywhere near $s = 2$ — which
is why the transform is a perfectly ordinary finite number there. Evaluating a
transform at a real, positive $s$ is not a strange thing to do; it is exactly what the
defining integral does, and what the lab's trapezium rule computes.

The second is a free sanity check. The final value theorem says
$\lim_{s\to0}sV(s) = 3$, and the signal is indeed $3 - 2e^{-5t} + 4te^{-5t} \to 3$ V.
The initial value theorem says $\lim_{s\to\infty}sV(s) = 3 - 2 = 1$, and $v(0) = 1$ V.
Both endpoints agree, which is strong evidence that the three terms were transformed
correctly before any number was substituted.
''',
                },
                {
                    "title": "How long until the output is nearly there?",
                    "minutes": 11,
                    "brief": r'''
The real work. Three passive parts, a step, and a question that no single formula
answers.

The capacitor is not charging through the 6.8 kΩ, and it is not charging through the
3.3 kΩ either. To find the pole you have to ask what resistance the capacitor *sees*,
which means turning the supply off — replacing it by a short, because an ideal voltage
source holds its terminals at a fixed difference — and looking back from the
capacitor's terminals into what remains.

So there are three separate things to work out before the question can be answered:
where the output finally settles, how fast it gets there, and then the time at which it
has covered 90% of the distance.
''',
                    "prompt": "How long after the supply is connected does the probe first reach 90% of its final value?",
                    "note": "Give the answer in milliseconds, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 6800},
                            {"id": "r2", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 3300},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "c", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 220e-9},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 18, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [11, 3], "b": [15, 3]},
                            {"a": [15, 3], "b": [15, 5]},
                            {"a": [15, 7], "b": [15, 9]},
                            {"a": [11, 3], "b": [18, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "10.0 V step at t = 0"},
                        {"label": "R1, supply to the node", "value": "6.80 kΩ"},
                        {"label": "R2, node to ground", "value": "3.30 kΩ"},
                        {"label": "C, node to ground", "value": "220 nF"},
                        {"label": "Charge on C before the step", "value": "none"},
                    ],
                    "aside": "Thévenin the source and the two resistors first, as seen from the capacitor's "
                             "terminals. The open-circuit voltage of that equivalent is the final value, and "
                             "its resistance is what sets the pole.",
                    # Neither quantity is repeated from the labels: the final value comes from a
                    # DC solve of the drawn circuit, and the pole magnitude is bisected out of its
                    # swept response, which for one pole is the -3 dB corner. The inversion of
                    # v(t) = vf(1 - e^{-wt}) is then the one line of algebra the prompt asks for.
                    "check": r'''
const vf = c.vout();                          /* where the probe finally settles */
const w = 2 * Math.PI * c.corner(1, 1e6);     /* pole magnitude, rad/s */
const target = 0.9 * vf;
return -1000 * Math.log(1 - target / vf) / w; /* t in ms */
''',
                    "answer": 1.125,
                    "tol": 0.015,
                    "unit": "ms",
                    "hint": "Final value: the two resistors divide the 10 V, because the capacitor is an "
                            "open circuit once everything has stopped changing. Pole: the capacitor sees "
                            "$R_1 \\parallel R_2$ with the supply shorted. Then $0.9 = 1 - e^{-t/\\tau}$ "
                            "gives $t = \\tau\\ln 10$.",
                    "wrong": "If you got 3.44 ms, the capacitor was charged through the 6.8 kΩ alone — but "
                             "the 3.3 kΩ is a second path to ground for the same charge, and two paths are "
                             "quicker than one. If you got 1.67 ms, only the 3.3 kΩ was counted. If you got "
                             "5.12 ms, the two resistors were added in series, which is what they look like "
                             "on the drawing but not what the capacitor sees.",
                    "why": r'''
```
final value.  At DC the capacitor is an open circuit, so the node is a
plain divider:

    Vf   = 10 * 3300 / (6800 + 3300)  =  10 * 0.32673  =  3.2673 V

the pole.  Turn the 10 V source off (short it) and look back from the
capacitor.  R1 and R2 are then both from the node to ground, in parallel:

    Rth  = 6800 * 3300 / 10100        =  2221.8 ohm
    tau  = Rth * C = 2221.8 * 220e-9  =  4.8879e-4 s   = 488.8 us
    pole = -1/tau                     = -2045.9 rad/s

the time.  v(t) = Vf (1 - e^(-t/tau)), and 90% means the exponential has
fallen to 0.1:

    0.9  = 1 - e^(-t/tau)
    0.1  = e^(-t/tau)
    t    = tau * ln(10) = 4.8879e-4 * 2.30259  = 1.1255e-3 s

                                              t = 1.125 ms
```
Three separate facts had to be assembled, and only the last of them was about the
question actually asked. It is worth noticing that the 90% time did not depend on the
supply voltage or on the final value at all — the $V_f$ cancelled out of the ratio, so
the same circuit fed from 3 V or from 30 V reaches 90% of wherever it is going at
exactly the same instant. Everything about *when* is in the pole; everything about
*how far* is in the DC divider. Those two questions separate cleanly, and keeping them
apart is most of what makes a transient tractable.

One more reading of the same result: $\ln 10 = 2.303$, so 90% always takes about 2.3
time constants, just as 63.2% always takes exactly one and 99% takes 4.6. Those three
multiples are worth carrying around.
''',
                },
            ],
            "build": {
                "title": "One pole, put where the specification wants it",
                "minutes": 22,
                "brief": r'''
The numeric questions in this module analysed circuits somebody else drew. This one
runs the other way: here is a specification, produce a circuit that meets it.

## The specification

From a 1 V source, build a passive network with a probe on its output node such that

- **the DC output is exactly half the input**, 0.500 V, and
- **the circuit's single pole sits at 2000 rad/s**, which is 318.3 Hz.

Those are two independent requirements and they need two independent parts to satisfy
them, plus a third to have anything to talk about. A bare RC gives you the pole but a
DC gain of 1; a bare resistive divider gives you the gain but no pole at all.

## The idea you need

Put a divider on the node and hang a capacitor off it. At DC the capacitor is an open
circuit, so the two resistors set the output on their own:

$$V_{out}(0) = V_{in}\frac{R_2}{R_1+R_2}$$

The pole is set by what the capacitor *sees*, which is not either resistor by itself.
Turn the source off — short it, since an ideal voltage source holds a fixed difference
across its terminals — and both resistors run from the output node to ground, in
parallel. So

$$\omega_p = \frac{1}{(R_1\parallel R_2)\,C}$$

That is the same Thévenin argument the last numeric question used, run backwards.

## What is on the canvas

A 1 V source and its ground, and nothing else. Add two resistors, a capacitor, a
second ground and a probe. Leave the source at 1 V: the checks read the probe voltage
directly and compare it to the source's own value, so a different amplitude will still
pass the gain test but the numbers on your own working will stop matching the brief.

## How it is measured

Nothing compares your drawing to a reference. The checks solve whatever you built and
read three things off it: its DC output, the frequency at which the response is 3 dB
down — which for a single pole *is* the pole magnitude, once converted from hertz to
rad/s — and the ratio of the gains one and two decades above that corner, which must be
10 and not 100. Any set of values that meets the specification passes; there is a whole
one-parameter family of them, and picking a sensible member of it is part of the job.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 10},
                    ],
                    "wires": [
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [3, 6], "b": [3, 3]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 10},
                        {"id": "p2", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 2000},
                        {"id": "p3", "kind": "R", "x": 11, "y": 6, "rot": 1, "value": 2000},
                        {"id": "p4", "kind": "GND", "x": 11, "y": 9},
                        {"id": "p5", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 5e-7},
                        {"id": "p6", "kind": "GND", "x": 15, "y": 9},
                        {"id": "p7", "kind": "OUT", "x": 18, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [3, 6], "b": [3, 3]},
                        {"a": [3, 3], "b": [7, 3]},
                        {"a": [9, 3], "b": [11, 3]},
                        {"a": [11, 3], "b": [11, 5]},
                        {"a": [11, 7], "b": [11, 9]},
                        {"a": [11, 3], "b": [15, 3]},
                        {"a": [15, 3], "b": [15, 5]},
                        {"a": [15, 7], "b": [15, 9]},
                        {"a": [11, 3], "b": [18, 3]},
                    ],
                },
                "checks": [
                    {"name": "one source, still at 1 V", "code": r'''
c.assert(c.count('V') === 1,
  'Use exactly one voltage source, so that "the gain" means one thing. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 1, 0.001,
  'the source amplitude — leave it at 1 V so the probe voltage reads directly as the gain');
'''},
                    {"name": "the DC output is half the input", "code": r'''
const vin = c.values('V')[0];
c.close(c.vout() / vin, 0.5, 0.02,
  'the DC output as a fraction of the input — at DC the capacitor is an open circuit, so this is ' +
  'the resistive divider on its own');
'''},
                    {"name": "the pole sits at 2000 rad/s", "code": r'''
const w = 2 * Math.PI * c.corner(1, 1e6);
c.close(w, 2000, 0.03,
  'the pole magnitude, measured as the -3 dB corner of the swept response and converted to rad/s');
'''},
                    {"name": "one pole, not two", "code": r'''
const a = c.gain(3183.0988618379064);    /* a decade above the corner  */
const b = c.gain(31830.988618379065);    /* two decades above it       */
c.assert(b > 0, 'The response died to nothing above the corner; check where the probe is.');
c.close(a / b, 10, 0.05,
  'the ratio of the gains one and two decades above the corner — a single pole gives 10, a pair gives 100');
'''},
                ],
                "hints": [
                    "The order is source, then a resistor across to the output node, then a second resistor from that node to ground. The capacitor goes from the same node to ground, and the probe sits on the node.",
                    "The DC requirement is the divider rule: $R_2/(R_1+R_2) = 0.5$ means $R_1 = R_2$. Any equal pair will do; 2 kΩ each keeps the currents sensible.",
                    "With $R_1 = R_2 = 2$ kΩ the capacitor sees $R_1 \\parallel R_2 = 1$ kΩ. Then $C = 1/(\\omega_p R_{th}) = 1/(2000 \\times 1000) = 500$ nF. Type `500n` in the value box.",
                    "If the DC check passes but the corner is too high, the capacitor is too small — the pole moves out as $C$ falls, and it moves as $1/C$, so a corner twice too high needs twice the capacitance.",
                    "If the pole is right but the DC output is 1.00 V, the second resistor is missing and you have built a plain RC. The whole input appears at the output at DC when there is nothing pulling the node down.",
                ],
            },
            "derive": {
                "title": "An RC circuit solved in the s-domain",
                "minutes": 14,
                "vars": ["s", "R", "C", "t", "A", "B", "V_in", "V_c", "tau"],
                "brief": r'''
A resistor $R$ in series with a capacitor $C$, with the output taken across the
capacitor and a 1 V step applied at $t = 0$.

In EE111 this needed a first-order differential equation, an integrating factor and a
constant of integration. Here it needs the divider rule you already know from EE101,
applied to impedances that happen to contain $s$. Use $Z_R = R$ and $Z_C = 1/(sC)$.
''',
                "steps": [
                    {
                        "prompt": "Apply the divider rule with impedances. Write $V_c(s)$ as a multiple of $V_{in}(s)$, in terms of $s$, $R$, $C$ and $V_{in}$.",
                        "given": "The divider is $V_c = V_{in} \\, Z_C / (Z_R + Z_C)$, with $Z_C = 1/(sC)$.",
                        "answer": "\\frac{V_in}{1 + sRC}",
                        "hint": "Put $1/(sC)$ over $R + 1/(sC)$, then multiply top and bottom by $sC$ to clear the inner fraction.",
                        "deconstruct": [
                            "The ratio is $\\dfrac{1/(sC)}{R + 1/(sC)}$.",
                            "Multiplying top and bottom by $sC$ gives $\\dfrac{1}{sRC + 1}$.",
                            "That whole thing multiplies $V_{in}$.",
                        ],
                    },
                    {
                        "prompt": "The input is a 1 V step, so $V_{in}(s) = 1/s$. Substitute it and write $V_c(s)$ in terms of $s$, $R$ and $C$ only.",
                        "answer": "\\frac{1}{s(1 + sRC)}",
                        "hint": "You are multiplying the previous answer by $1/s$. Nothing cancels.",
                        "deconstruct": [
                            "The step contributes a factor $1/s$.",
                            "So the circuit's own fraction picks up an extra pole at $s = 0$, which is the input's pole, not the circuit's.",
                        ],
                    },
                    {
                        "prompt": "Split it: $V_c(s) = \\dfrac{A}{s} + \\dfrac{B}{1 + sRC}$. Multiply both sides by $s$, then set $s = 0$. What is $A$?",
                        "answer": "1",
                        "hint": "Multiplying by $s$ leaves $\\dfrac{1}{1+sRC}$ on the left. Now put $s = 0$ into that.",
                        "deconstruct": [
                            "$s \\cdot V_c(s) = \\dfrac{1}{1+sRC}$, and the second term picks up a factor $s$ which kills it at $s=0$.",
                            "At $s = 0$ the surviving expression is $1/1$.",
                        ],
                    },
                    {
                        "prompt": "Now multiply both sides by $(1 + sRC)$ and set $s = -1/(RC)$, which is where that factor vanishes. What is $B$?",
                        "answer": "-RC",
                        "hint": "The left-hand side becomes $1/s$. Evaluate it at $s = -1/(RC)$.",
                        "deconstruct": [
                            "$(1+sRC)\\,V_c(s) = \\dfrac{1}{s}$, and the $A/s$ term picks up the factor $(1+sRC)$, which is zero at this $s$.",
                            "So $B = 1/s$ evaluated at $s = -1/(RC)$, which is $-RC$.",
                        ],
                    },
                    {
                        "prompt": "The second term is now $\\dfrac{-RC}{1 + sRC}$. Divide top and bottom by $RC$ so it reads $\\dfrac{-1}{s + a}$, and write $a$ in terms of $R$ and $C$.",
                        "answer": "\\frac{1}{RC}",
                        "hint": "Dividing $1 + sRC$ by $RC$ gives $s + 1/(RC)$.",
                        "deconstruct": [
                            "$\\dfrac{-RC}{1+sRC} = \\dfrac{-RC/(RC)}{(1+sRC)/(RC)} = \\dfrac{-1}{s + 1/(RC)}$.",
                            "So the pole sits at $s = -1/(RC)$ and $a = 1/(RC)$.",
                        ],
                    },
                    {
                        "prompt": "Using $1/s \\to 1$ and $1/(s+a) \\to e^{-at}$, the answer is $v_c(t) = 1 - e^{-t/\\tau}$. Write the time constant $\\tau$ in terms of $R$ and $C$.",
                        "answer": "R C",
                        "hint": "$\\tau = 1/a$, and you have just written $a$.",
                        "deconstruct": [
                            "The pole is at $-1/(RC)$, so the decaying exponential is $e^{-t/(RC)}$.",
                            "Comparing with $e^{-t/\\tau}$ gives $\\tau = RC$.",
                        ],
                    },
                ],
                "closing": r'''
Six lines of algebra and no calculus at all. Notice where each piece came from: the
pole at $s = 0$ was the *input's*, and it produced the constant 1 that the output
settles at. The pole at $-1/(RC)$ was the *circuit's*, and it produced the decaying
exponential. That separation — input poles give the steady part, circuit poles give
the transient — holds for every linear circuit you will ever meet.
''',
            },
            "lab": {
                "title": "Computing the transform, rather than looking it up",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
A table of transforms is easy to distrust because nothing in it looks computed. So
compute it. The Laplace transform is a definite integral, and a definite integral is a
sum you can evaluate numerically.

- `laplace(f, s, tmax, n)` approximates $\int_0^{t_{max}} f(t)e^{-st}\,dt$ by the
  trapezium rule on `n` evenly spaced samples between 0 and `tmax`, and returns the
  result. `s` may be complex, and then so is the answer. `f` is a function that takes
  a NumPy array of times and returns an array of values.
- `rc_step_voltage(R, C, t)` returns the capacitor voltage of a series RC driven by a
  1 V step — the closed form you derived a moment ago. `t` may be an array.
- `settling_time(R, C, frac)` returns the time at which that voltage first reaches
  `frac` of its final value.

## The trapezium rule, in two lines

With samples $y_0 \dots y_{n-1}$ spaced $h$ apart, the trapezium estimate of the
integral is

```text
h * (sum(y) - 0.5 * (y[0] + y[-1]))
```

which is the plain sum with the two end samples counted half. Build the array `y` as
`f(t) * np.exp(-s * t)` and that line finishes the function.

`tmax` is finite but the integral is not, so the answer is only right when the
integrand has decayed to nothing by `tmax`. Every call in the checks has been given a
`tmax` where it has. This is worth remembering: the transform of something that does
not decay — a pure sinusoid, a step — does not converge for real $s \le 0$, and the
region of $s$ where it does converge is exactly the half-plane to the right of the
rightmost pole.
''',
                "files": [{"name": "main.py", "content": r'''
"""The Laplace transform as an integral you can actually evaluate."""

import numpy as np


def laplace(f, s, tmax=40.0, n=200001):
    """Trapezium-rule estimate of the integral of f(t) exp(-s t) from 0 to tmax."""
    # TODO: build the time grid with np.linspace, form y = f(t) * np.exp(-s * t),
    #       and return h * (sum(y) - 0.5 * (y[0] + y[-1])).
    return 0.0


def rc_step_voltage(R, C, t):
    """Capacitor voltage of a series RC driven by a 1 V step at t = 0."""
    # TODO: 1 - exp(-t / RC).
    return 0.0


def settling_time(R, C, frac):
    """Time at which the capacitor first reaches `frac` of its final value."""
    # TODO: solve frac = 1 - exp(-t / RC) for t.
    return 0.0


if __name__ == "__main__":
    print("L{1} at s=2 should be 0.5:", laplace(lambda t: np.ones_like(t), 2.0))
    print("L{exp(-3t)} at s=1 should be 0.25:", laplace(lambda t: np.exp(-3 * t), 1.0))
    print("a 1 k with 1 uF reaches 63.2% after", settling_time(1000.0, 1e-6, 0.632), "s")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The Laplace transform as an integral you can actually evaluate.

Every number quoted in the checks was produced by running this file:
    L{1}(2)        -> 0.5000000067   (exact 0.5)
    L{exp(-3t)}(1) -> 0.2500000133   (exact 0.25)
    L{cos 2t}(1)   -> 0.2000000033   (exact 0.2)
    L{exp(-t)}(1+2j) -> 0.2500000067 - 0.2499999933j, which is 1/(2+2j) to 7e-9
"""

import numpy as np


def laplace(f, s, tmax=40.0, n=200001):
    """Trapezium-rule estimate of the integral of f(t) exp(-s t) from 0 to tmax."""
    t = np.linspace(0.0, tmax, n)
    h = t[1] - t[0]
    y = f(t) * np.exp(-s * t)
    return h * (np.sum(y) - 0.5 * (y[0] + y[-1]))


def rc_step_voltage(R, C, t):
    """Capacitor voltage of a series RC driven by a 1 V step at t = 0."""
    return 1.0 - np.exp(-np.asarray(t, dtype=float) / (R * C))


def settling_time(R, C, frac):
    """Time at which the capacitor first reaches `frac` of its final value."""
    return -R * C * np.log(1.0 - frac)


if __name__ == "__main__":
    print("L{1} at s=2 should be 0.5:", laplace(lambda t: np.ones_like(t), 2.0))
    print("L{exp(-3t)} at s=1 should be 0.25:", laplace(lambda t: np.exp(-3 * t), 1.0))
    print("a 1 k with 1 uF reaches 63.2% after", settling_time(1000.0, 1e-6, 0.632), "s")
'''}],
                "hints": [
                    "`t = np.linspace(0.0, tmax, n)` and `h = t[1] - t[0]`. Do not compute `h` as `tmax / n` — with `n` samples there are only `n - 1` gaps.",
                    "`y = f(t) * np.exp(-s * t)` works unchanged for complex `s`, because NumPy promotes the array to complex on its own.",
                    "`rc_step_voltage` is the closed form from the derivation: `1 - np.exp(-t / (R * C))`. Wrap `t` with `np.asarray(t, dtype=float)` so it works for a single number and for an array.",
                    "For `settling_time`, rearrange $\\text{frac} = 1 - e^{-t/RC}$ to $t = -RC\\ln(1-\\text{frac})$.",
                    "If a transform comes out far too small, check `tmax`: the integrand must have decayed to nothing by then, or you have integrated only part of it.",
                ],
                "tests": [
                    {"name": "the transform of a constant is 1/s", "code": r'''
got = laplace(lambda t: np.ones_like(t), 2.0)
assert abs(got - 0.5) < 1e-6, f"L{{1}} at s=2 is 1/2 = 0.5, got {got}"
got = laplace(lambda t: np.ones_like(t), 5.0)
assert abs(got - 0.2) < 1e-6, f"L{{1}} at s=5 is 1/5 = 0.2, got {got}"
'''},
                    {"name": "the transform of a decaying exponential is 1/(s+a)", "code": r'''
got = laplace(lambda t: np.exp(-3.0 * t), 1.0)
assert abs(got - 0.25) < 1e-6, f"L{{exp(-3t)}} at s=1 is 1/4 = 0.25, got {got}"
got = laplace(lambda t: np.exp(-0.5 * t), 2.0)
assert abs(got - 0.4) < 1e-6, f"L{{exp(-t/2)}} at s=2 is 1/2.5 = 0.4, got {got}"
'''},
                    {"name": "the sine and cosine pairs come out right", "code": r'''
got = laplace(lambda t: np.cos(2.0 * t), 1.0)
assert abs(got - 0.2) < 1e-6, f"L{{cos 2t}} at s=1 is 1/(1+4) = 0.2, got {got}"
got = laplace(lambda t: np.sin(3.0 * t), 2.0)
assert abs(got - 3.0 / 13.0) < 1e-6, \
    f"L{{sin 3t}} at s=2 is 3/(4+9) = 0.23077, got {got}"
'''},
                    {"name": "a complex s gives a complex answer", "code": r'''
got = laplace(lambda t: np.exp(-t), 1.0 + 2.0j)
want = 1.0 / (2.0 + 2.0j)
assert abs(got - want) < 1e-6, \
    f"L{{exp(-t)}} at s=1+2j is 1/(2+2j) = {want}, got {got}"
assert abs(got.imag + 0.25) < 1e-6, \
    "the imaginary part should be -0.25; a real answer means exp(-s*t) was never complex"
'''},
                    {"name": "the RC step response and its time constant", "code": r'''
v = rc_step_voltage(1000.0, 1e-6, 1e-3)
assert abs(v - 0.6321205588285577) < 1e-9, \
    f"after one time constant the capacitor is at 1 - 1/e = 0.63212, got {v}"
tt = settling_time(1000.0, 1e-6, 0.99)
assert abs(tt - 0.004605170185988091) < 1e-9, \
    f"99% takes RC*ln(100) = 4.6052 ms, got {tt} s"
assert abs(settling_time(1000.0, 1e-6, 0.6321205588285577) - 1e-3) < 1e-12, \
    "63.2% must come back as exactly one time constant"
'''},
                    {"name": "transforming the step response recovers 1/(s(1+sRC))", "code": r'''
s = 2000.0
got = laplace(lambda t: rc_step_voltage(1000.0, 1e-6, t), s, tmax=0.05, n=200001)
want = 1.0 / (s * (1.0 + s * 1e-3))
assert abs(got - want) < 1e-9, \
    f"the transform of the step response should be 1/(s(1+sRC)) = {want}, got {got}"
'''},
                ],
            },
            "quiz": {
                "title": "The transform, its rules and its poles",
                "minutes": 9,
                "questions": [
                    {
                        "q": "The Laplace transform of $f(t)$ is defined as:",
                        "opts": [
                            "$\\int_0^{\\infty} f(t)e^{st}\\,dt$",
                            "$\\int_{-\\infty}^{\\infty} f(t)e^{-j\\omega t}\\,dt$",
                            "$\\int_0^{\\infty} f(t)e^{-st}\\,dt$",
                            "$\\sum_{n=0}^{\\infty} f(nT)z^{-n}$",
                        ],
                        "a": 2,
                        "why": r'''
The kernel is $e^{-st}$, with a minus sign, and the integral runs from 0, not from
$-\infty$. The version with $e^{+st}$ has the sign wrong, and with it the convergence: it makes the
integral diverge for every ordinary signal. The integral from $-\infty$ with kernel
$e^{-j\omega t}$ is the **Fourier** transform,
which is this one restricted to $s = j\omega$ — a genuinely useful thing to notice
rather than a trap, because it is why phasors are a special case of what you are
learning. The sum in powers of $z^{-n}$ is the z-transform, for sampled signals.
''',
                    },
                    {
                        "q": "With $F(s) = \\mathcal{L}\\{f(t)\\}$, the transform of $\\dfrac{df}{dt}$ is:",
                        "opts": ["$sF(s) - f(0)$", "$sF(s)$", "$F(s)/s$", "$sF(s) + f(0)$"],
                        "a": 0,
                        "why": r'''
$sF(s) - f(0)$. The $-f(0)$ falls out of integrating by parts, and dropping it is the
single most common error in the whole subject — it silently assumes every capacitor
starts empty and every inductor starts with no current. When a question says
"the capacitor is initially charged to 2 V", that 2 V enters the algebra through
exactly this term and nowhere else. $F(s)/s$ is the *integration* rule.
''',
                    },
                    {
                        "q": "A 1 V step is applied at $t=0$ to a series RC with the output taken across the capacitor. What is $V_c(s)$?",
                        "opts": [
                            "$\\dfrac{1}{1+sRC}$",
                            "$\\dfrac{s}{1+sRC}$",
                            "$\\dfrac{RC}{1+sRC}$",
                            "$\\dfrac{1}{s(1+sRC)}$",
                        ],
                        "a": 3,
                        "why": r'''
Two factors multiply: the circuit's transfer function $1/(1+sRC)$ and the input's own
transform $1/s$. $1/(1+sRC)$ on its own is the transfer function — which is what you get by forgetting
that the step also has to be transformed. That distinction matters: the
transfer function belongs to the circuit and never changes, while the $1/s$ belongs to
the signal you chose to apply.
''',
                    },
                    {
                        "q": "Four systems have the pole pairs below. Which one's response takes longest to die away?",
                        "opts": [
                            "$-5 \\pm j50$",
                            "$-0.5 \\pm j2$",
                            "$-20$ (twice)",
                            "$-3 \\pm j100$",
                        ],
                        "a": 1,
                        "why": r'''
Decay is governed by the **real part** alone: the envelope is $e^{\sigma t}$, so the
pole closest to the imaginary axis, here $\sigma = -0.5$, lingers longest. The
imaginary part sets how fast the response *oscillates*, not how fast it dies, which is why $-3 \pm j100$ — the most dramatic-looking pair, ringing at 100 rad/s —
actually settles six times faster than $-0.5 \pm j2$. Distance from the imaginary axis is speed; height
above it is ringing.
''',
                    },
                    {
                        "q": "The final value theorem gives $\\lim_{t\\to\\infty} f(t) = \\lim_{s\\to 0} sF(s)$. For $F(s) = \\dfrac{10}{s(s+4)}$, what is the final value?",
                        "opts": ["0", "10", "2.5", "40"],
                        "a": 2,
                        "why": r'''
$sF(s) = 10/(s+4)$, and at $s = 0$ that is $10/4 = 2.5$. Cancelling the $s$ first is
the whole technique. A warning that costs marks every year: the theorem is only valid
when the response really does settle, which means every pole of $sF(s)$ must have a
negative real part. Apply it to $F(s) = \omega/(s^2+\omega^2)$, a sine that never
settles, and it returns 0 with complete confidence.
''',
                    },
                    {
                        "q": "Applying the transform to a linear differential equation with constant coefficients turns it into:",
                        "opts": [
                            "an algebraic equation in $s$",
                            "a difference equation in $n$",
                            "a nonlinear equation",
                            "an integral equation",
                        ],
                        "a": 0,
                        "why": r'''
That is the entire point of the exercise. Each derivative becomes a factor of $s$, so
an $n$-th order differential equation becomes an $n$-th degree polynomial equation —
which you solve by rearranging, exactly as in school algebra, and then invert. The
price is that you must be able to get back: that is what partial fractions, in the
next module, are for. Difference equations and the z-transform belong to sampled
systems, which arrive in a later course.
''',
                    },
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Poles, zeros and partial fractions",
            "summary": "A transfer function is a fraction. Its roots on top and bottom decide everything, and splitting it apart puts the answer back into the time domain.",
            "concepts": [
                "A **transfer function** $H(s) = V_{out}(s)/V_{in}(s)$ is a ratio of polynomials in $s$, determined entirely by the circuit and not at all by the input.",
                "The roots of the denominator are the **poles**; the roots of the numerator are the **zeros**. A pole is a value of $s$ at which $H$ blows up, a zero one at which it vanishes.",
                "Each pole $p_i$ contributes a term $k_i e^{p_i t}$ to the response. The system is stable exactly when every pole has a negative real part.",
                "Complex poles always arrive in conjugate pairs for a real circuit, and a pair $\\sigma \\pm j\\omega_d$ contributes a decaying oscillation $e^{\\sigma t}\\sin(\\omega_d t + \\phi)$, never a complex voltage.",
                "**Partial fractions**: for distinct poles, $H(s) = \\sum_i \\dfrac{k_i}{s - p_i}$, and the residue is $k_i = \\dfrac{N(p_i)}{D'(p_i)}$ — the numerator over the derivative of the denominator, both evaluated at the pole.",
                "A repeated pole needs an extra term: $1/(s+a)^2$ inverts to $te^{-at}$, not to a plain exponential.",
                "The standard second-order form $H(s) = \\dfrac{K\\omega_n^2}{s^2 + 2\\zeta\\omega_n s + \\omega_n^2}$ has poles at $-\\zeta\\omega_n \\pm j\\omega_n\\sqrt{1-\\zeta^2}$: $\\omega_n$ is their distance from the origin and $\\zeta$ is the cosine of their angle from the negative real axis.",
                "On a Bode plot each pole bends the gain down by 20 dB/decade and the phase by 90°; at $\\omega = \\omega_n$ a second-order pole pair gives a gain of exactly $K/(2\\zeta)$ and a phase of exactly $-90°$, whatever the damping.",
            ],
            "read": [
                {
                    "title": "The circuit's own frequencies, and where they live",
                    "minutes": 15,
                    "body": r'''
Strike a bell and it rings at its own pitch. Strike it harder and it rings louder at
the same pitch; strike it with a hammer rather than a fingernail and the mixture of
overtones changes, but not one of the frequencies present belongs to the hammer. The
pitches belong to the bell.

A circuit behaves the same way, and this module is about where those pitches are
written down. Close a switch on a loop containing a resistor, an inductor and a
capacitor and the capacitor voltage overshoots, comes back, overshoots less, and
settles. Change the supply from 5 V to 50 V and every feature of that curve is ten
times taller and happens at exactly the same instants. Feed the loop a ramp instead of
a step and the settled part is different, but the wobble decorating it decays at the
same rate and rings at the same frequency as before. Those rates and frequencies are
the circuit's **natural modes**, and they survive every change of input because they
were never a property of the input.

## Every RLC network is a fraction

Module 1 gave each part an impedance in $s$: $Z_R = R$, $Z_L = sL$, $Z_C = 1/(sC)$.
With those in hand a circuit is analysed exactly as in EE101 — series impedances add,
parallel ones combine reciprocally, the divider rule divides — except that every
quantity is now a function of $s$ instead of a number.

Do that to any network of resistors, capacitors and inductors and the answer is always
the same kind of object:

$$H(s) \;=\; \frac{V_{out}(s)}{V_{in}(s)} \;=\; \frac{N(s)}{D(s)}
  \;=\; \frac{b_m s^m + \cdots + b_1 s + b_0}{a_n s^n + \cdots + a_1 s + a_0}$$

a ratio of two polynomials with real coefficients. It could not come out as anything
else. Impedances are built from $R$, $sL$ and $1/(sC)$; adding, multiplying and
dividing such things yields rational functions and nothing more exotic. There is no
$\sin s$ and no $e^{s}$ here; those belong to structures the last section of this unit
names, and none of them is a lumped RLC network.

Two properties of $H(s)$ are worth separating, because they are easy to blur together.
The first: $H$ depends on the components and the wiring and on nothing else. Feed the
circuit a step, a sinusoid, or a recording of a violin, and $H$ is the same function.
The second: $H$ is not a signal. It is the operator that turns one signal into another,
and in the $s$-domain that operation is a plain multiplication,
$V_{out}(s) = H(s)\,V_{in}(s)$. The same statement in the time domain is a convolution,
which is most of the reason nobody works in the time domain if they can avoid it.

## What a pole actually is

The **poles** are the roots of $D(s)$; the **zeros** are the roots of $N(s)$. As a
definition that is vocabulary and nothing more. What earns it a place is what happens
at those values of $s$.

Suppose $D(p) = 0$. Look at $V_{out}(s) = H(s)V_{in}(s)$ at $s = p$: the denominator
has vanished, so a perfectly finite output is compatible with an input of zero, because
$0/0$ is not the contradiction that $1/0$ is. Read that as a statement about the
circuit and it says: at $s = p$ this circuit can hold up a response with nothing
driving it. That is the bell's pitch. The response it holds up is $e^{pt}$, since
$e^{pt}$ is the signal whose transform has a pole at $p$ — so a pole is not a number
the algebra happens to throw out, it is a motion the circuit is capable of on its own.

A zero is the mirror image. At $s = z$ the numerator vanishes, so a non-zero input
produces no output at all: drive the circuit with $e^{zt}$ and nothing comes out. That
sounds like a curiosity until you notice that every high-pass filter has a zero at
$s = 0$, and $e^{0t}$ is a constant. "A zero at the origin" and "DC does not get
through" are the same sentence.

## Worked: one pole and one zero

Take a capacitor in series with the signal path and a resistor to ground, output across
the resistor, with $C = 100$ nF and $R = 4.7\ \mathrm{k}\Omega$. The divider rule
applies unchanged, with the resistor as the lower leg.

```text
H(s) = R / ( R + 1/(sC) )

multiply top and bottom by sC:

H(s) = sRC / ( 1 + sRC )

R C  = 4700 * 100e-9              = 4.7e-4 s

zero:  numerator  sRC = 0    at  s = 0
pole:  denominator 1 + sRC = 0    at  s = -1/RC = -2128 rad/s
```

The two roots already tell you what the circuit does, before any plotting. Put
$s = j\omega$ and walk $\omega$ up from zero. At $\omega = 0$ the numerator is zero, so
nothing gets through. As $\omega$ grows the numerator grows in proportion, and while
$\omega RC$ is still small compared with 1 the denominator barely changes, so the gain
rises linearly with frequency. Once $\omega RC$ is large, numerator and denominator are
both dominated by the same $sRC$ term and the gain flattens out at 1. The changeover
happens where $\omega RC = 1$ — that is, at the pole magnitude.

Three numbers make the shape concrete.

```text
at f = 100 Hz  :  w R C = 2*pi*100  * 4.7e-4    = 0.29531
                  |H|   = 0.29531 / sqrt(1 + 0.29531^2)
                        = 0.29531 / 1.04269     = 0.2832
                  phase = 90 - atan(0.29531)    = +73.5 degrees

at f = 338.6 Hz:  w R C = 2*pi*338.6 * 4.7e-4   = 1.0000
                  |H|   = 1 / sqrt(2)           = 0.7071
                  phase = 90 - atan(1)          = +45.0 degrees

at f = 1000 Hz :  w R C = 2*pi*1000 * 4.7e-4    = 2.9531
                  |H|   = 2.9531 / sqrt(1 + 2.9531^2)
                        = 2.9531 / 3.1180       = 0.9472
                  phase = 90 - atan(2.9531)     = +18.7 degrees
```

The middle row is the pole, quoted in hertz: $2128/2\pi = 338.6$ Hz. For a single pole
the three descriptions — the pole magnitude, the reciprocal of the time constant, and
the frequency at which the gain has fallen to $1/\sqrt2$ of its far value — are one
number wearing three hats. Hold on to the fact that this coincidence is a property of
*one* pole, because it is about to stop being true.

## Worked: a pair of poles

Now a resistor, an inductor and a capacitor in series across the source, output taken
across the capacitor, with $L = 0.1$ H, $R = 100\ \Omega$ and $C = 2.5\ \mu$F. The same
divider rule, with three impedances in the loop instead of two.

```text
H(s) = (1/(sC)) / ( R + sL + 1/(sC) )

multiply top and bottom by sC:

H(s) = 1 / ( s^2 LC + s RC + 1 )

L C  = 0.1 * 2.5e-6    = 2.5e-7
R C  = 100 * 2.5e-6    = 2.5e-4

H(s) = 1 / ( 2.5e-7 s^2 + 2.5e-4 s + 1 )

divide top and bottom by LC = 2.5e-7, so the s^2 coefficient becomes 1:

     1 / 2.5e-7 = 4e6         2.5e-4 / 2.5e-7 = 1000

H(s) = 4e6 / ( s^2 + 1000 s + 4e6 )
```

That last line is the **standard second-order form**, with the two numbers a designer
actually uses readable straight off it:

$$H(s) = \frac{K\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}
\quad\Longrightarrow\quad
\omega_n^2 = 4\times10^{6},\qquad 2\zeta\omega_n = 1000$$

so $\omega_n = 2000$ rad/s and $\zeta = 1000/(2\times2000) = 0.25$, with $K = 1$
because the numerator came out equal to $\omega_n^2$. Now the poles:

```text
s = [ -1000 +/- sqrt(1000^2 - 4 * 4e6) ] / 2
  = [ -1000 +/- sqrt(1e6 - 1.6e7)      ] / 2
  = [ -1000 +/- sqrt(-1.5e7)           ] / 2
  = [ -1000 +/- j 3872.98              ] / 2
  = -500 +/- j 1936.49
```

No real number squares to $-1.5\times10^{7}$, and that is the entire content of the
word *underdamped*: the loop has too little resistance to dissipate the energy sloshing
between $L$ and $C$ before it has sloshed back, so the response oscillates on its way
down.

## The s-plane is a map, and it repays learning to read

Plot those two poles on the complex plane — real part across, imaginary part up — and
every feature of the response can be read off geometrically.

- **Distance to the left of the imaginary axis is decay rate.** The real part is $-500$,
  so both modes carry $e^{-500t}$: a time constant of 2 ms, and the ringing is under 2%
  of its starting size after about four of those. Further left is faster.
- **Height above the axis is ringing frequency.** The imaginary part is 1936 rad/s, so
  the response wobbles at $1936/2\pi = 308$ Hz. This is $\omega_d$, the *damped* natural
  frequency, and it is not $\omega_n$.
- **Distance from the origin is $\omega_n$.** Check it:
  $\sqrt{500^2 + 1936.49^2} = \sqrt{2.5\times10^{5} + 3.75\times10^{6}}
  = \sqrt{4\times10^{6}} = 2000$. A pole pair slides around a circle of radius
  $\omega_n$ as the damping changes, and leaves that circle only if $L$ or $C$ changes.
- **Angle from the negative real axis is the damping.** The cosine of that angle is
  $500/2000 = 0.25$, which is $\zeta$ exactly. Poles on the negative real axis have
  $\zeta \ge 1$ and never ring; poles on the imaginary axis have $\zeta = 0$ and ring
  forever.

There is one more thing the picture gives, and it is the reason to draw it at all.
Since $H(s) = 4\times10^{6}/\big((s-p_1)(s-p_2)\big)$, evaluating at $s = j\omega$ and
taking magnitudes turns the algebra into a measurement with a ruler:

$$|H(j\omega)| = \frac{4\times10^{6}}{|j\omega - p_1|\;\cdot\;|j\omega - p_2|}$$

the numerator constant divided by the product of the distances from the test point on
the imaginary axis to each pole. (Zeros, where there are any, contribute their
distances on top.) Try it twice.

```text
at w = 0  -- the test point sits at the origin:

   distance to -500 + j1936.49 = sqrt(500^2 + 1936.49^2)  = 2000
   distance to -500 - j1936.49 =                            2000
   |H| = 4e6 / (2000 * 2000)   = 1.000        <- the DC gain

at w = 2000 -- the test point sits at j2000:

   to -500 + j1936.49 : |500 + j 63.51|  = sqrt(250000 +     4033) =  504.02
   to -500 - j1936.49 : |500 + j3936.49| = sqrt(250000 + 15495970) = 3968.12
   |H| = 4e6 / (504.02 * 3968.12) = 4e6 / 2.000e6 = 2.000
```

The second of those is resonance, arrived at without touching a frequency-response
formula. The test point has slid up close to one pole, that distance has collapsed from
2000 to 504, and the gain has risen in the same proportion. A gain of two, out of a box
containing nothing but a resistor, an inductor and a capacitor. And $1/(2\zeta) = 2$,
which is the general result for the gain at $\omega_n$ — you have just derived it with
a ruler.

## The mistake people actually make

Treating $\omega_n$ as the corner frequency.

It is tempting because of the worked example before last, where the pole magnitude, the
reciprocal time constant and the $-3$ dB point genuinely were the same number. That
coincidence belongs to a single pole and does not survive a second one. For the circuit
above, with $\zeta = 0.25$, there are three different frequencies, and they are worth
seeing side by side:

```text
peak of |H|       w = wn sqrt(1 - 2 zeta^2) = 2000 * 0.93541 = 1871 rad/s, |H| = 2.066
phase = -90 deg   w = wn                    =                  2000 rad/s, |H| = 2.000
|H| = 1/sqrt(2)   w                         =                  2969 rad/s, |H| = 0.707
```

Three answers to three different questions, spread over a factor of 1.6 in frequency.
$\omega_n$ is not where the peak is and not where the response is 3 dB down. It is
where the phase passes through exactly $-90°$, whatever $\zeta$ happens to be, which is
why the build exercise in this module uses phase rather than gain to pin it down.

The related slip is quoting $\omega_n$ as the ringing frequency. The ringing happens at
$\omega_d = \omega_n\sqrt{1-\zeta^2} = 1936$ rad/s here — only 3% below $\omega_n$,
small enough to hide inside rounding, and that is exactly what makes it dangerous. At
$\zeta = 0.7$ the same gap is 29%, so an answer that was invisibly wrong becomes
visibly wrong with nothing changed but the resistor.

## Where this stops holding

- **Pole-zero cancellation.** If $N$ and $D$ share a factor it cancels on paper and the
  mode disappears from $H$. It has not disappeared from the circuit. Some internal node
  still moves at that frequency; the cancellation says only that this input cannot
  excite it, or this output cannot see it. If the cancelled mode is an unstable one you
  have hidden a fire rather than put it out, and controllability and observability in
  CTRL510 are the language for saying so properly.
- **Zeros in the right half-plane.** A pole with a positive real part means
  $e^{+\sigma t}$ and the circuit is unstable. A *zero* with a positive real part is
  perfectly stable and merely strange: the step response sets off in the wrong direction
  before turning round. Stability is decided by the poles alone; the zeros decide shape.
- **Anything with a delay in it.** A metre of cable delays a signal, and a delay of $T$
  seconds transforms to $e^{-sT}$ — a function with no roots at all, and therefore no
  poles and no zeros to draw. The rational picture is an approximation there, and saying
  how good an approximation is the business of EMAG510.
- **Anything nonlinear or time-varying.** A transfer function exists only because
  superposition does. A diode, a saturating amplifier or a switching converter has no
  $H(s)$. What it has is a small-signal $H(s)$ about one operating point, which is a
  different and considerably weaker claim.
''',
                },
                {
                    "title": "Splitting the fraction, and getting back to time",
                    "minutes": 14,
                    "body": r'''
Solving a circuit in the $s$-domain produces a fraction. That is progress, but it is
not an answer: nobody has ever plugged a fraction into an oscilloscope. The remaining
job is to turn $V_{out}(s)$ back into $v_{out}(t)$, and the honest way to do it is a
contour integral in the complex plane that this course will never ask you to perform.

The other way works, is exact, and is what everybody actually does. It rests on one
observation: the table of transforms in module 1 is short, but every entry in it is a
*simple* fraction — $1/s$, $1/(s+a)$, $1/(s+a)^2$, $\omega/(s^2+\omega^2)$. If a
complicated fraction can be rewritten as a sum of simple ones, linearity inverts it term
by term and the short table is suddenly enough.

That rewriting is called **partial fractions**. This unit is about doing it, about what
each term means physically, and about the three situations in which the recipe changes.

## What the terms are

Consider the shape of the problem. A circuit with $n$ energy-storing parts has a
denominator of degree $n$, so $n$ poles; drive it with a step and the input contributes
a pole of its own at $s = 0$. The claim of partial fractions is that

$$\frac{N(s)}{(s-p_1)(s-p_2)\cdots(s-p_n)} = \frac{k_1}{s-p_1} + \frac{k_2}{s-p_2}
  + \cdots + \frac{k_n}{s-p_n}$$

whenever the poles are distinct and the numerator's degree is below the denominator's.
Each $k_i$ is the **residue** at $p_i$.

Invert term by term and you have $\sum_i k_i e^{p_i t}$. So the decomposition is not
algebraic housekeeping. It is the statement that the response is a sum of the circuit's
natural modes, one per pole, with the residues recording how much of each mode this
particular input managed to excite. The poles were fixed by the components; the
residues are where the input and the initial conditions get their say.

Two arguments for why the split must be possible. Counting: the left-hand side is
determined by the $n$ numbers in $N$, and the right-hand side has $n$ unknown residues,
so the books balance. Construction: put the right-hand side over a common denominator
and you get $D(s)$ underneath and a polynomial of degree $n-1$ on top, whose $n$
coefficients can be matched term by term against $N$. Matching coefficients is a
perfectly good way to find the residues; it is just slower than what follows.

## The cover-up rule, and the formula it turns into

To get $k_1$, multiply both sides by $(s - p_1)$:

$$\frac{N(s)}{(s-p_2)\cdots(s-p_n)} = k_1 + (s-p_1)\left[\frac{k_2}{s-p_2} + \cdots\right]$$

and then set $s = p_1$. Every term in the bracket is multiplied by zero and disappears,
leaving

$$k_1 = \left.\frac{N(s)}{(s-p_2)\cdots(s-p_n)}\right|_{s=p_1}$$

which is the whole of the fraction with the factor $(s-p_1)$ struck out, evaluated at
that pole. Hence the name: cover up the factor belonging to the pole you want, and
evaluate what is left there.

When the denominator has not been factorised, the same quantity is written

$$k_i = \frac{N(p_i)}{D'(p_i)}$$

— the numerator over the *derivative* of the denominator. That is not a second rule.
Write $D(s) = (s-p_i)Q(s)$; then $D'(s) = Q(s) + (s-p_i)Q'(s)$, and at $s = p_i$ the
second term dies, so $D'(p_i) = Q(p_i)$, which is precisely the covered-up denominator.
The derivative form is the one to use in code, because `np.polyder` and `np.polyval` do
it without anyone having to factorise anything — which is exactly what the lab in this
module builds.

## Worked: two real poles

Take the series RLC of the build exercise but with a much larger resistor: $L = 0.1$ H,
$C = 2.5\ \mu$F, $R = 500\ \Omega$, output across the capacitor, fed a 1 V step from
rest.

```text
H(s) = 4e6 / ( s^2 + (R/L) s + 1/(LC) )       [previous unit, same divider rule]

R/L    = 500 / 0.1        = 5000
1/(LC) = 1 / 2.5e-7       = 4e6

H(s) = 4e6 / ( s^2 + 5000 s + 4e6 )

wn        = sqrt(4e6)             = 2000 rad/s   (L and C unchanged, so wn is too)
2 zeta wn = 5000  ->  zeta        = 1.25         (overdamped: greater than 1)

factorise:  s = [ -5000 +/- sqrt(5000^2 - 4*4e6) ] / 2
              = [ -5000 +/- sqrt(2.5e7 - 1.6e7)  ] / 2
              = [ -5000 +/- 3000                 ] / 2
              = -1000   and   -4000
```

Both poles are real and negative, which is what $\zeta > 1$ means: enough resistance to
dissipate the energy before it can slosh back, so nothing rings. Now apply the step,
$V_{in}(s) = 1/s$.

```text
V(s) = H(s) * 1/s = 4e6 / ( s (s + 1000) (s + 4000) )

three distinct poles: 0, -1000, -4000.  Cover up each in turn.

k0  (at s = 0)     = 4e6 / ( (0 + 1000)(0 + 4000) )
                   = 4e6 / 4e6                       =  1

k1  (at s = -1000) = 4e6 / ( (-1000)(-1000 + 4000) )
                   = 4e6 / ( -1000 * 3000 )
                   = 4e6 / -3e6                      = -1.33333

k2  (at s = -4000) = 4e6 / ( (-4000)(-4000 + 1000) )
                   = 4e6 / ( -4000 * -3000 )
                   = 4e6 / 1.2e7                     = +0.33333
```

Invert with two table entries, $1/s \to 1$ and $1/(s+a) \to e^{-at}$:

$$v(t) = 1 - \tfrac{4}{3}e^{-1000t} + \tfrac{1}{3}e^{-4000t}\ \ \mathrm{volts}$$

Check both ends before believing it. At $t = 0$ the three terms give
$1 - 4/3 + 1/3 = 0$, and the capacitor started empty. As $t \to \infty$ both
exponentials die and $v \to 1$ V, the supply, as it must since a capacitor is an open
circuit once nothing is changing. Then a point in the middle, at $t = 1$ ms:

```text
e^(-1000 * 1e-3) = e^-1  = 0.367879
e^(-4000 * 1e-3) = e^-4  = 0.018316

v(1 ms) = 1 - 1.333333 * 0.367879 + 0.333333 * 0.018316
        = 1 - 0.490506           + 0.006105
        = 0.5156 V
```

Notice what the two residues are doing. The fast pole at $-4000$ carries a residue four
times smaller than the slow one, and has vanished by $t = 1$ ms in any case; nearly all
of the visible response is the $-1000$ term. That is the **dominant pole** idea, and it
is why a designer will often analyse a third-order circuit as though it were
first-order and be right to three figures.

## Worked: a complex pair

Put the resistor back to $100\ \Omega$ — the circuit the build exercise asks for — and
run exactly the same procedure. Now $\zeta = 0.25$ and the poles are complex.

```text
H(s) = 4e6 / ( s^2 + 1000 s + 4e6 )
poles:  s = -500 +/- j 1936.4917

step response:  V(s) = 4e6 / ( s (s^2 + 1000 s + 4e6) )
                     = 4e6 / D(s),    D(s)  = s^3 + 1000 s^2 + 4e6 s
                                      D'(s) = 3 s^2 + 2000 s + 4e6
```

The residue at $s = 0$ is $4\times10^{6}/D'(0) = 4\times10^{6}/4\times10^{6} = 1$, the
same 1 V the response eventually settles at. For the pair, take
$p = -500 + j1936.4917$ and grind through $D'(p)$.

```text
p^2    = (-500)^2 + 2(-500)(j1936.4917) + (j1936.4917)^2
       = 250000 - j 1936491.7 - 3750000
       = -3500000 - j 1936491.7

3 p^2  = -10500000 - j 5809475.0
2000 p =  -1000000 + j 3872983.4
+ 4e6  =    4000000
         ---------------------------
D'(p)  =  -7500000 - j 1936491.6

|D'(p)|^2 = 7.5e6^2 + 1936491.6^2 = 5.625e13 + 0.375e13 = 6.0e13

k = 4e6 / D'(p) = 4e6 * ( -7.5e6 + j 1936491.6 ) / 6.0e13
                = ( -3.0e13 + j 7.746e12 ) / 6.0e13
                = -0.5 + j 0.129099
```

A complex residue is not a problem, and it is certainly not something to take the
modulus of and move on. Its partner at the conjugate pole is the conjugate residue,
$\bar k = -0.5 - j0.129099$ — always, for a circuit made of real components — and the
two terms are meant to be added together before anything is read off:

$$k e^{pt} + \bar k e^{\bar p t} = 2|k|\,e^{\sigma t}\cos(\omega_d t + \angle k)$$

which is the identity $z + \bar z = 2\,\mathrm{Re}(z)$ wearing exponential clothes. Here
$|k| = \sqrt{0.5^2 + 0.129099^2} = 0.516398$, so $2|k| = 1.032796$, and
$\angle k = 180° - \arctan(0.129099/0.5) = 180° - 14.48° = 165.52°$, which is
$2.8889$ rad — second quadrant, because the real part is negative. So

$$v(t) = 1 + 1.032796\,e^{-500t}\cos(1936.49\,t + 2.8889)\ \ \mathrm{volts}$$

Check $t = 0$: $\cos(2.8889) = -0.96825$, so the second term is
$1.032796\times(-0.96825) = -1.00000$ and $v(0) = 0$. The capacitor started empty, so
that is right — and it is a check the arithmetic could easily have failed.

The same answer is more often written with the cosine expanded into a sine and a cosine
about $t = 0$:

$$v(t) = 1 - e^{-\zeta\omega_n t}\left[\cos\omega_d t
   + \frac{\zeta}{\sqrt{1-\zeta^{2}}}\,\sin\omega_d t\right]$$

which with $\zeta = 0.25$ has $\zeta/\sqrt{1-\zeta^2} = 0.25/0.968246 = 0.258199$. Put
$t = 1$ ms through it:

```text
wd t           = 1936.4917 * 1e-3   =  1.9364917 rad
cos(1.9364917)                      = -0.357599
sin(1.9364917)                      = +0.933875
bracket        = -0.357599 + 0.258199 * 0.933875
               = -0.357599 + 0.241126        = -0.116473
e^(-500 * 1e-3) = e^-0.5             =  0.606531

v(1 ms) = 1 - 0.606531 * (-0.116473) = 1 + 0.070645 = 1.0706 V
```

1.07 V out of a 1 V step. The overshoot is the complex pair made visible — and the same
circuit with $R = 500\ \Omega$ was at 0.5156 V at that instant and still climbing. One
resistor changed, two completely different responses, and the fraction predicted both
without a differential equation being solved anywhere.

## Three audits that cost nothing

A sign error in a residue produces an answer that is wrong in a way no plot makes
obvious, so it is worth auditing every expansion.

- **The residues sum to the coefficient of $s^{n-1}$ in the numerator.** When the
  numerator's degree is at least two below the denominator's that coefficient is zero,
  so the residues must sum to exactly zero. Both worked examples pass:
  $1 - 4/3 + 1/3 = 0$ for the real case, and $1 + 2\,\mathrm{Re}(k) = 1 - 1 = 0$ for the
  complex one.
- **The initial value.** $\lim_{s\to\infty}sF(s)$ must equal your $f(t)$ at $t = 0$.
  That is the residue-sum check said in transform language, and it caught the phase of
  the complex residue above.
- **The final value.** $\lim_{s\to0}sF(s)$ must equal what your $f(t)$ tends to,
  provided every remaining pole is strictly in the left half-plane. For both step
  responses it returns 1 V, matching the constant term — which is the residue at the
  input's own pole, not the circuit's.

## The mistakes people actually make

The expensive one is taking the modulus of a complex residue and dropping the angle. It
is tempting because the modulus is the part that looks like an amplitude, and
$2|k|e^{\sigma t}$ has both the right size and the right envelope. It is nevertheless
the wrong signal: dropping $\angle k$ above turns $v(0) = 0$ into
$v(0) = 1 + 1.0328 = 2.03$, a capacitor that arrives already charged to twice the
supply. The angle is not a decoration on the amplitude — it is where the cosine starts.

The second is applying the recipe to a fraction whose numerator degree is not below its
denominator's. $\dfrac{s^2+3s+1}{s^2+3s+2}$ has no expansion of the form above, because
every term on the right tends to zero at large $s$ while the left-hand side tends to 1.
Divide first: it is $1 - \dfrac{1}{(s+1)(s+2)}$, and the constant 1 inverts to an
impulse $\delta(t)$. A genuine impulse in a circuit's response means a direct path from
input to output with no storage in the way — a wire, or a capacitor straight across.

The third is using $k_i = N(p_i)/D'(p_i)$ on a repeated pole. It divides by zero, which
is at least loud. A pole of multiplicity two needs two terms,
$\dfrac{A}{(s+a)^2} + \dfrac{B}{s+a}$, inverting to $Ate^{-at} + Be^{-at}$; the extra
factor of $t$ is why a critically damped circuit sets off more slowly than the plain
exponential you might expect.

## Where this stops holding

- **Repeated poles**, as above. In a real circuit they are a measure-zero accident, since
  no two components are ever matched that exactly, but they are common in idealised
  design problems and critical damping is defined by one.
- **Nearly repeated poles**, which are far worse than exactly repeated ones. The
  residues carry a factor $1/(p_1-p_2)$, so as the poles approach each other they blow
  up to enormous values of opposite sign that then almost cancel. Arithmetically valid;
  numerically a catastrophe. The condition number in module 7 is the vocabulary for the
  same failure written as a matrix.
- **Improper fractions**, which need a polynomial division before anything else.
- **Anything that is not a ratio of polynomials.** A delay contributes $e^{-sT}$, which
  cannot be split into partial fractions because there are no poles to split it around.
  Numerical inversion, or a rational approximation to the delay, is the only route.
''',
                },
            ],
            "blanks": [
                {
                    "title": "Three components to two numbers, line by line",
                    "minutes": 9,
                    "caption": "a series RLC across a step: L = 40 mH, R = 640 Ω, C = 250 nF, output across the capacitor",
                    "lang": "text",
                    "brief": r'''
The guided derivation in this module does this with letters. Here it is with numbers in
it from the second line, so that nothing is being remembered by the shape of a formula.

Every step is the divider rule with $s$-domain impedances, followed by school algebra.
Nothing is executed; the arithmetic is yours to choose.
''',
                    "listing": """    impedances      Z_R = 640        Z_L = 0.04 s        Z_C = 1/(2.5e-7 s)

    divider         H(s) = Z_C / (Z_R + Z_L + Z_C)

    clear the                          1
    inner fraction  H(s) = -------------------------------
                             s^2 LC  +  s RC  +  1

    the products    L C = 0.04 * 2.5e-7 = ___          R C = 640 * 2.5e-7 = 1.6e-4

    divide top and                    1e8
    bottom by LC    H(s) = -------------------------------
                             s^2  +  ___ s  +  1e8

    standard form   H(s) = K wn^2 / ( s^2 + 2 zeta wn s + wn^2 )

    natural freq    wn   = sqrt(1e8)                   = ___ rad/s

    damping         zeta = (coefficient of s) / (2 wn) = ___

    the poles       s    = -zeta wn  +/-  j wn sqrt(1 - zeta^2)
                         = ___

    a free check    |s| = sqrt(8000^2 + 6000^2) = 10000 = wn, as it must be
""",
                    "blanks": [
                        {
                            "prompt": "The product $LC$, in base units.",
                            "hole": "?",
                            "opts": ["1e-8", "1e-2", "1e-5", "1e-11"],
                            "a": 0,
                            "why": "$0.04 \\times 2.5\\times10^{-7} = 10^{-8}$. Both values must be in henries and farads before they are multiplied: 40 mH is 0.04 H and 250 nF is $2.5\\times10^{-7}$ F. $LC$ has units of seconds squared, which is the clue that $1/\\sqrt{LC}$ is a frequency.",
                            "whys": [
                                "$0.04 \\times 2.5\\times10^{-7} = 10^{-8}$. Both values must be in henries and farads before they are multiplied: 40 mH is 0.04 H and 250 nF is $2.5\\times10^{-7}$ F. $LC$ has units of seconds squared, which is the clue that $1/\\sqrt{LC}$ is a frequency.",
                                "$10^{-2}$ is $L$ on its own, near enough — the capacitance never entered. Both parts have to appear, which is why $\\omega_n$ moves when either one is changed.",
                                "$10^{-5}$ is what you get by multiplying 40 by 250 and then losing count of the prefixes. Millis and nanos together are $10^{-3}\\times10^{-9} = 10^{-12}$, so $40 \\times 250 \\times 10^{-12} = 10^{-8}$.",
                                "$10^{-11}$ is a thousand times too small, which would put $\\omega_n$ at 316 krad/s instead of 10 krad/s — a factor of 31.6, since the square root halves the error in the exponent.",
                            ],
                        },
                        {
                            "prompt": "The coefficient of $s$ after dividing through by $LC$.",
                            "hole": "?",
                            "opts": ["16000", "1.6e-4", "640", "1.6e12"],
                            "a": 0,
                            "why": "$RC/LC = R/L = 640/0.04 = 16000$. Dividing by $LC$ has to be done to every term, and on the $s$ term the capacitance cancels, leaving $R/L$ — which is worth remembering as a shortcut in its own right, since $2\\zeta\\omega_n = R/L$ for every series RLC.",
                            "whys": [
                                "$RC/LC = R/L = 640/0.04 = 16000$. Dividing by $LC$ has to be done to every term, and on the $s$ term the capacitance cancels, leaving $R/L$ — which is worth remembering as a shortcut in its own right, since $2\\zeta\\omega_n = R/L$ for every series RLC.",
                                "$1.6\\times10^{-4}$ is $RC$, left undivided. The whole point of the step is that the constant term became 1 and then $10^{8}$; the middle term is divided by the same $LC$.",
                                "640 is the resistance in ohms. Ohms are not radians per second, and a coefficient sitting beside $s$ in a denominator whose other terms are $s^2$ and $10^{8}$ has to be a rate.",
                                "$1.6\\times10^{12}$ divides by $LC$ twice over. A useful guard: the three denominator coefficients are $1$, $2\\zeta\\omega_n$ and $\\omega_n^2$, so the middle one must be of the same order as $\\sqrt{10^{8}} = 10^{4}$ unless the damping is extreme.",
                            ],
                        },
                        {
                            "prompt": "The natural frequency.",
                            "hole": "?",
                            "opts": ["10000", "1e8", "1592", "100"],
                            "a": 0,
                            "why": "$\\omega_n = \\sqrt{10^{8}} = 10^{4}$ rad/s. Equivalently $1/\\sqrt{LC} = 1/\\sqrt{10^{-8}} = 1/10^{-4}$, which is the same statement with the square root taken before the reciprocal instead of after.",
                            "whys": [
                                "$\\omega_n = \\sqrt{10^{8}} = 10^{4}$ rad/s. Equivalently $1/\\sqrt{LC} = 1/\\sqrt{10^{-8}} = 1/10^{-4}$, which is the same statement with the square root taken before the reciprocal instead of after.",
                                "$10^{8}$ is $\\omega_n^2$, the constant term itself. The standard form calls that term $\\omega_n^2$ precisely so that the square root is the last thing you do, and skipping it is the commonest slip on this line.",
                                "1592 is $\\omega_n$ converted to hertz, $10^{4}/2\\pi$. Poles and natural frequencies are quoted in rad/s throughout; hertz appears only when a measurement is being described.",
                                "100 is the square root of $10^{4}$, so the square root has been taken twice. Check against $1/\\sqrt{LC}$: with $LC = 10^{-8}$ the answer cannot be smaller than a few thousand.",
                            ],
                        },
                        {
                            "prompt": "The damping ratio.",
                            "hole": "?",
                            "opts": ["0.8", "1.6", "8000", "0.625"],
                            "a": 0,
                            "why": "$\\zeta = 16000/(2 \\times 10000) = 0.8$. It is dimensionless, and being below 1 it says the poles are complex and the response still overshoots — but only just: at $\\zeta = 0.8$ the overshoot is 1.5% of the step, and the one after it is 0.02%, which is nothing.",
                            "whys": [
                                "$\\zeta = 16000/(2 \\times 10000) = 0.8$. It is dimensionless, and being below 1 it says the poles are complex and the response still overshoots — but only just: at $\\zeta = 0.8$ the overshoot is 1.5% of the step, and the one after it is 0.02%, which is nothing.",
                                "1.6 is $16000/\\omega_n$ with the factor of 2 forgotten. The form is $2\\zeta\\omega_n s$, so the coefficient carries a 2 that has to come back out; leaving it in would report an overdamped circuit that in fact overshoots.",
                                "8000 is $\\zeta\\omega_n$, the real part of the pole — a rate in rad/s, not a ratio. It is a useful number, but it is $\\sigma$ and not $\\zeta$.",
                                "0.625 is $10000/16000$, the ratio the other way up with the 2 also mislaid. A quick guard: $\\zeta$ is the cosine of the pole angle, so anything above 1 means real poles and no ringing at all.",
                            ],
                        },
                        {
                            "prompt": "The pair of poles.",
                            "hole": "?",
                            "opts": [
                                "-8000 +/- j6000",
                                "-6000 +/- j8000",
                                "-8000 +/- j10000",
                                "-0.8 +/- j0.6",
                            ],
                            "a": 0,
                            "why": "Real part $-\\zeta\\omega_n = -0.8 \\times 10000 = -8000$; imaginary part $\\omega_n\\sqrt{1-\\zeta^2} = 10000\\sqrt{0.36} = 6000$. So the modes decay as $e^{-8000t}$ while ringing at 6000 rad/s, and $\\sqrt{8000^2+6000^2} = 10000 = \\omega_n$ closes the loop.",
                            "whys": [
                                "Real part $-\\zeta\\omega_n = -0.8 \\times 10000 = -8000$; imaginary part $\\omega_n\\sqrt{1-\\zeta^2} = 10000\\sqrt{0.36} = 6000$. So the modes decay as $e^{-8000t}$ while ringing at 6000 rad/s, and $\\sqrt{8000^2+6000^2} = 10000 = \\omega_n$ closes the loop.",
                                "$-6000 \\pm j8000$ has the two parts swapped, and it describes a far more lightly damped circuit: $\\zeta$ would be $6000/10000 = 0.6$. The larger of the two always belongs to the real part when $\\zeta > 1/\\sqrt2$.",
                                "$-8000 \\pm j10000$ uses $\\omega_n$ itself as the imaginary part. That would put the poles $\\sqrt{8000^2+10000^2} = 12806$ from the origin, and the distance from the origin has to come back as exactly $\\omega_n$.",
                                "$-0.8 \\pm j0.6$ is the pole pair of a circuit normalised to $\\omega_n = 1$, which is a genuinely useful object — but the $\\omega_n$ has to be multiplied back in before the answer is in rad/s.",
                            ],
                        },
                    ],
                },
                {
                    "title": "A complex pair, split and put back together",
                    "minutes": 10,
                    "caption": "H(s) = 250000 / (s^2 + 600 s + 250000), inverted by residues",
                    "lang": "text",
                    "brief": r'''
The real-pole case is arithmetic you can do in your head once you have seen it. The
complex case is where people stop, because a residue comes out as a complex number and
it is not obvious what to do with it.

The answer is that you do nothing with it on its own. Complex poles arrive in conjugate
pairs, their residues do too, and the two terms are added before anything is read off.
This is that addition, one line at a time.
''',
                    "listing": """    the fraction    H(s) = 250000 / ( s^2 + 600 s + 250000 )

    the poles       s = [ -600 +/- sqrt(360000 - 1000000) ] / 2
                      = [ -600 +/- j 800 ] / 2
                      = -300 +/- j 400

    in standard     wn   = sqrt(250000)      = 500 rad/s
    form            zeta = 600 / (2 * 500)   = ___

    residues        k = N(p) / D'(p),    D'(s) = 2 s + 600

    at p =          D'(p) = 2(-300 + j400) + 600
    -300 + j400           = ___

                    k     = 250000 / (j 800)
                          = ___

    the other pole  its residue is the conjugate: k* = +j 312.5

    add the pair    k e^(pt) + k* e^(p* t) = 2 |k| e^(-300 t) cos(400 t + arg k)

                    2 |k|   = ___
                    arg k   = ___

    time domain     h(t) = 625 e^(-300 t) cos(400 t - 90 deg)
                         = 625 e^(-300 t) sin(400 t)

    check at t = 0  h(0) = 0, as the numerator being two degrees below demands
""",
                    "blanks": [
                        {
                            "prompt": "The damping ratio of this pair.",
                            "hole": "?",
                            "opts": ["0.6", "1.2", "300", "0.75"],
                            "a": 0,
                            "why": "$2\\zeta\\omega_n = 600$ and $\\omega_n = 500$, so $\\zeta = 600/1000 = 0.6$. Check it against the geometry: the real part is 300 and the distance from the origin is $\\sqrt{300^2+400^2} = 500$, so the cosine of the pole angle is $300/500 = 0.6$ as well.",
                            "whys": [
                                "$2\\zeta\\omega_n = 600$ and $\\omega_n = 500$, so $\\zeta = 600/1000 = 0.6$. Check it against the geometry: the real part is 300 and the distance from the origin is $\\sqrt{300^2+400^2} = 500$, so the cosine of the pole angle is $300/500 = 0.6$ as well.",
                                "1.2 is $600/500$ with the factor of 2 dropped, and it would say the circuit is overdamped — which cannot be right, since the poles just came out complex.",
                                "300 is $\\zeta\\omega_n$, the real part of the pole. It has units of rad/s and $\\zeta$ has none, so the two can never be the same number by accident.",
                                "0.75 is $300/400$, the tangent of the pole angle rather than its cosine. The hypotenuse is what $\\zeta$ is measured against, because that hypotenuse is $\\omega_n$.",
                            ],
                        },
                        {
                            "prompt": "The derivative of the denominator, evaluated at the pole.",
                            "hole": "?",
                            "opts": ["j 800", "-600 + j 800", "j 400", "600 + j 800"],
                            "a": 0,
                            "why": "$2(-300 + j400) = -600 + j800$, and adding the 600 cancels the real part exactly, leaving $j800$. That cancellation is not luck: $D'(p) = 2p + 2\\zeta\\omega_n$ and $\\mathrm{Re}(p) = -\\zeta\\omega_n$, so the real parts always destroy each other and $D'(p)$ is always purely imaginary, equal to $2j\\omega_d$.",
                            "whys": [
                                "$2(-300 + j400) = -600 + j800$, and adding the 600 cancels the real part exactly, leaving $j800$. That cancellation is not luck: $D'(p) = 2p + 2\\zeta\\omega_n$ and $\\mathrm{Re}(p) = -\\zeta\\omega_n$, so the real parts always destroy each other and $D'(p)$ is always purely imaginary, equal to $2j\\omega_d$.",
                                "$-600 + j800$ is $2p$ with the $+600$ from the derivative never added. $D'(s) = 2s + 600$ has two terms and both of them are evaluated.",
                                "$j400$ is $\\omega_d$ rather than $2\\omega_d$. The factor of 2 comes from differentiating $s^2$, and losing it would double every residue and double the whole response.",
                                "$600 + j800$ has the sign of the real part of the pole flipped, so the two 600s add instead of cancelling. That would leave a residue with a real part, and the response would start at a non-zero value.",
                            ],
                        },
                        {
                            "prompt": "The residue at that pole.",
                            "hole": "?",
                            "opts": ["-j 312.5", "+j 312.5", "312.5", "-j 625"],
                            "a": 0,
                            "why": "$250000/(j800)$: multiply top and bottom by $-j$ to get $-j\\,250000/800 = -j312.5$. Dividing by $j$ is multiplying by $-j$, which is a rotation of $-90°$ — the reason this particular response comes out as a sine rather than a cosine.",
                            "whys": [
                                "$250000/(j800)$: multiply top and bottom by $-j$ to get $-j\\,250000/800 = -j312.5$. Dividing by $j$ is multiplying by $-j$, which is a rotation of $-90°$ — the reason this particular response comes out as a sine rather than a cosine.",
                                "$+j312.5$ is the residue at the *other* pole, $-300 - j400$. Getting them the wrong way round flips the sign of the whole sinusoid, so the response would start by going negative.",
                                "312.5 is the magnitude with the direction thrown away. A residue whose angle has been discarded gives a response that starts at the wrong value — here it would make $h(0) = 625$ instead of 0.",
                                "$-j625$ is twice the residue: the doubling belongs to the pairing step further down, where $k$ and $k^*$ are added, not to the residue itself.",
                            ],
                        },
                        {
                            "prompt": "Twice the magnitude of the residue.",
                            "hole": "?",
                            "opts": ["625", "312.5", "1250", "500"],
                            "a": 0,
                            "why": "$|{-j312.5}| = 312.5$, so $2|k| = 625$. There is a shortcut worth having: for the standard second-order form the amplitude always works out to $\\omega_n^2/\\omega_d$, which here is $250000/400 = 625$.",
                            "whys": [
                                "$|{-j312.5}| = 312.5$, so $2|k| = 625$. There is a shortcut worth having: for the standard second-order form the amplitude always works out to $\\omega_n^2/\\omega_d$, which here is $250000/400 = 625$.",
                                "312.5 is $|k|$ without the doubling. The 2 comes from adding a number to its own conjugate, $z + \\bar z = 2\\mathrm{Re}(z)$, and it applies to every complex pair.",
                                "1250 doubles twice. Sanity-check it against the initial slope: $h'(0)$ must be $\\omega_n^2 = 250000$, and $625 \\times 400 = 250000$ exactly, while 1250 would give twice that.",
                                "500 is $\\omega_n$, which is not an amplitude at all. The amplitude of this pair is $\\omega_n^2/\\omega_d$, and the two coincide only when $\\omega_d = \\omega_n$, that is at zero damping.",
                            ],
                        },
                        {
                            "prompt": "The angle of the residue.",
                            "hole": "?",
                            "opts": ["-90 degrees", "+90 degrees", "0 degrees", "180 degrees"],
                            "a": 0,
                            "why": "$-j312.5$ points straight down the imaginary axis, so its angle is $-90°$. Feeding that into $\\cos(\\omega_d t + \\angle k)$ gives $\\cos(400t - 90°) = \\sin 400t$, and the sine is what makes $h(0) = 0$ — which it has to be, because the numerator is two degrees below the denominator.",
                            "whys": [
                                "$-j312.5$ points straight down the imaginary axis, so its angle is $-90°$. Feeding that into $\\cos(\\omega_d t + \\angle k)$ gives $\\cos(400t - 90°) = \\sin 400t$, and the sine is what makes $h(0) = 0$ — which it has to be, because the numerator is two degrees below the denominator.",
                                "$+90°$ would give $\\cos(400t + 90°) = -\\sin 400t$, the same shape upside down. It is the angle of the conjugate residue, so this is the same slip as taking the wrong pole of the pair.",
                                "$0°$ is the angle of a real, positive residue, which would make the response a pure cosine starting at 625. Nothing with an $s^{-2}$ tail can start anywhere but zero.",
                                "$180°$ is a real, negative residue: a cosine starting at $-625$. The residue here has no real part at all, so its angle must be a quarter turn, not a half one.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "How much damping does this loop have?",
                    "minutes": 5,
                    "brief": r'''
The mechanical one, to get the routine under your fingers. Three components, one
formula, one number out, and the only thing that can really go wrong is a prefix.

Nothing here is asked about a voltage. $\zeta$ is a pure ratio: it has no units, and the
supply could be 1 V or 100 V without changing it.
''',
                    "prompt": "What is the damping ratio $\\zeta$ of this circuit?",
                    "note": "Give the ratio itself, dimensionless, to three decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "l", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.02},
                            {"id": "r", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 40},
                            {"id": "c", "kind": "C", "x": 13, "y": 7, "rot": 1, "value": 5e-7},
                            {"id": "g1", "kind": "GND", "x": 13, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [5, 5]},
                            {"a": [7, 5], "b": [9, 5]},
                            {"a": [11, 5], "b": [13, 5]},
                            {"a": [13, 5], "b": [13, 6]},
                            {"a": [13, 8], "b": [13, 10]},
                            {"a": [13, 5], "b": [15, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "1.00 V"},
                        {"label": "L", "value": "20.0 mH"},
                        {"label": "R", "value": "40.0 Ω"},
                        {"label": "C", "value": "500 nF"},
                        {"label": "Output", "value": "across the capacitor"},
                    ],
                    "aside": "$\\zeta = \\tfrac{R}{2}\\sqrt{C/L}$, which the guided derivation in this module "
                             "builds out of the divider rule. Put every value in ohms, henries and farads "
                             "before the square root.",
                    # Measured, not restated: the phase of a second-order pair is exactly -90 degrees at
                    # its natural frequency whatever the damping, so bisecting on phase finds wn, and the
                    # gain there is 1/(2 zeta). Both readings come off the swept schematic.
                    "check": r'''
let lo = 1, hi = 1e6;
for (let i = 0; i < 80; i++) {
  const mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > -90) lo = mid; else hi = mid;
}
const fn = Math.sqrt(lo * hi);          /* the natural frequency, in Hz */
return c.values('V')[0] / (2 * c.gain(fn));
''',
                    "answer": 0.1,
                    "tol": 0.003,
                    "unit": "",
                    "hint": "$C/L = 5\\times10^{-7}/0.02$. Take the square root of that first, then multiply "
                            "by half the resistance.",
                    "wrong": "If you got 4000, the ratio inside the square root is upside down. "
                             "$\\sqrt{L/C} = 200\\ \\Omega$ is the characteristic impedance of the pair, and "
                             "$\\zeta$ is the resistance measured *against* that 200 Ω — so it divides, "
                             "rather than multiplying. If you got 0.2, the factor of two is missing. If you "
                             "got 100, the millihenries and nanofarads went in as the bare numbers 20 and "
                             "500.",
                    "why": r'''
```
base units first:   L = 0.02 H      C = 5e-7 F      R = 40 ohm

C / L        = 5e-7 / 0.02          = 2.5e-5
sqrt(C / L)  = sqrt(2.5e-5)         = 5.0e-3     (siemens, i.e. 1/200 ohm)

zeta = (R/2) * sqrt(C/L)
     = 20 * 5.0e-3                  = 0.100
```
Two things follow from that number without any more work. It is below 1, so the poles
are a complex pair and the step response overshoots and rings. And it is small, so the
gain at the natural frequency is $1/(2\zeta) = 5$ — the circuit multiplies a sinusoid at
$\omega_n = 1/\sqrt{LC} = 10\,000$ rad/s by five, out of three passive parts.

Notice what $\zeta$ is made of. $\sqrt{L/C} = 200\ \Omega$ is a resistance built out of
the two storage elements alone, called the characteristic impedance of the pair, and
$\zeta = R/(2\sqrt{L/C}) = 40/400$. Damping is not a property of the resistor; it is the
resistor compared with that 200 Ω. Double $L$ and halve $C$ and the resistor has not
moved, but the damping has halved.
''',
                },
                {
                    "title": "One residue out of a fraction",
                    "minutes": 7,
                    "brief": r'''
No circuit here — a transfer function, and one number extracted from it. This is the
step everyone gets wrong once, and it is worth getting wrong on paper rather than
halfway through a lab.

Two routes reach the same answer. Cover up the factor belonging to the pole you want
and evaluate the rest at that pole; or use $k = N(p)/D'(p)$, multiplying the denominator
out first. Doing it both ways takes a minute and is its own check.
''',
                    "prompt": "What is the residue of $H(s)$ at the pole $s = -4$?",
                    "note": "Give the residue itself, including its sign, to two decimal places.",
                    "figure": "$H(s) = \\dfrac{20(s+1)}{(s+4)(s+10)}$, the transfer function of some "
                              "circuit whose details do not matter here. Its poles are at $s = -4$ and "
                              "$s = -10$, and it has a single zero at $s = -1$.",
                    "given": [
                        {"label": "Numerator", "value": "$N(s) = 20(s+1)$"},
                        {"label": "Denominator", "value": "$D(s) = (s+4)(s+10) = s^2 + 14s + 40$"},
                        {"label": "The pole asked about", "value": "$s = -4$"},
                        {"label": "Residue formula", "value": "$k_i = N(p_i)/D'(p_i)$"},
                    ],
                    "aside": "Covering up $(s+4)$ leaves $20(s+1)/(s+10)$, to be evaluated at $s = -4$. "
                             "Every $s$ in that expression becomes $-4$, including the ones inside the "
                             "brackets.",
                    "answer": -10.0,
                    "tol": 0.05,
                    "unit": "",
                    "hint": "$N(-4) = 20(-4+1) = -60$. $D'(s) = 2s + 14$, so $D'(-4) = 6$. Divide.",
                    "wrong": "If you got $+10$, the sign was lost somewhere: $-4+1$ is $-3$, not $3$. If you "
                             "got 30, that is the residue at the *other* pole, $s = -10$. If you got $-60$, "
                             "the numerator was evaluated and then never divided by anything.",
                    "why": r'''
```
cover-up route:

    strike out (s + 4), evaluate the rest at s = -4

    k = 20(s + 1) / (s + 10)   at s = -4
      = 20(-4 + 1) / (-4 + 10)
      = 20 * (-3) / 6
      = -60 / 6                          = -10

derivative route:

    D(s)  = (s + 4)(s + 10) = s^2 + 14 s + 40
    D'(s) = 2 s + 14
    D'(-4) = -8 + 14                     = 6

    N(-4) = 20(-4 + 1)                   = -60

    k = N(-4) / D'(-4) = -60 / 6         = -10
```
A negative residue is not an error and not a warning sign. It means this mode enters the
response with a minus in front of it: $h(t) = -10e^{-4t} + 30e^{-10t}$, which starts at
$-10 + 30 = +20$ and passes through zero on its way down.

That 20 is the free check. When the numerator is exactly one degree below the
denominator, the residues must sum to the numerator's leading coefficient — here 20 —
and $-10 + 30 = 20$. (When the gap is two degrees or more, the sum is zero instead,
which is the version the lab's tests use.) Work out both residues even when you were
asked for one: the sum costs nothing and catches a dropped sign immediately.
''',
                },
                {
                    "title": "Where the response is largest",
                    "minutes": 9,
                    "brief": r'''
A step up. The question sounds as though it is asking for the natural frequency, and it
is not — it is asking where the gain actually peaks, which is a different frequency, and
in hertz rather than rad/s.

Three things have to happen in order: get $\omega_n$ and $\zeta$ from the components, put
them into the expression for the peak, and convert. Each of the three is a place to lose
a factor, so write down units at every line.

For the record, the peak of $|H(j\omega)|$ for the standard second-order low-pass sits at
$\omega_p = \omega_n\sqrt{1-2\zeta^2}$, which exists only while $\zeta < 1/\sqrt2$.
''',
                    "prompt": "At what frequency is the output voltage largest?",
                    "note": "Give the answer in hertz, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "l", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.1},
                            {"id": "r", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 300},
                            {"id": "c", "kind": "C", "x": 13, "y": 7, "rot": 1, "value": 4e-7},
                            {"id": "g1", "kind": "GND", "x": 13, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [5, 5]},
                            {"a": [7, 5], "b": [9, 5]},
                            {"a": [11, 5], "b": [13, 5]},
                            {"a": [13, 5], "b": [13, 6]},
                            {"a": [13, 8], "b": [13, 10]},
                            {"a": [13, 5], "b": [15, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Drive", "value": "1.00 V sinusoid, swept in frequency"},
                        {"label": "L", "value": "100 mH"},
                        {"label": "R", "value": "300 Ω"},
                        {"label": "C", "value": "400 nF"},
                        {"label": "Output", "value": "across the capacitor"},
                    ],
                    "aside": "$\\omega_n = 1/\\sqrt{LC}$ and $\\zeta = \\tfrac{R}{2}\\sqrt{C/L}$ first. The "
                             "peak is at $\\omega_n\\sqrt{1-2\\zeta^2}$, and the answer wanted is in hertz.",
                    # Nothing is restated from the labels: this hunts the maximum of the measured
                    # response by ternary search on log frequency, so it finds whatever peak the drawn
                    # circuit actually has, wherever the components put it.
                    "check": r'''
let lo = 10, hi = 10000;
for (let i = 0; i < 120; i++) {
  const step = (Math.log(hi) - Math.log(lo)) / 3;
  const a = Math.exp(Math.log(lo) + step);
  const b = Math.exp(Math.log(lo) + 2 * step);
  if (c.gain(a) < c.gain(b)) lo = a; else hi = b;
}
return Math.sqrt(lo * hi);
''',
                    "answer": 720.6,
                    "tol": 1.5,
                    "unit": "Hz",
                    "hint": "$LC = 4\\times10^{-8}$ so $\\omega_n = 5000$ rad/s, and "
                            "$\\sqrt{C/L} = 0.002$ so $\\zeta = 0.3$. Then $1 - 2\\zeta^2 = 0.82$, and "
                            "divide the result by $2\\pi$ at the very end.",
                    "wrong": "If you got 795.8, that is $\\omega_n$ in hertz — the peak is *below* the "
                             "natural frequency, always, for any damping that has a peak at all. If you got "
                             "4528, the conversion to hertz never happened; that number is $\\omega_p$ in "
                             "rad/s. If you got 5000, both slips at once.",
                    "why": r'''
```
components -> the two numbers:

    L C          = 0.1 * 4e-7        = 4e-8
    wn           = 1 / sqrt(4e-8)    = 1 / 2e-4       = 5000 rad/s

    C / L        = 4e-7 / 0.1        = 4e-6
    sqrt(C/L)                        = 2.0e-3
    zeta         = (300/2) * 2.0e-3  = 150 * 2.0e-3   = 0.300

the peak:

    1 - 2 zeta^2 = 1 - 2*0.09        = 0.82
    sqrt(0.82)                       = 0.905539
    w_p          = 5000 * 0.905539   = 4527.69 rad/s

into hertz:

    f_p          = 4527.69 / (2 pi)                   = 720.6 Hz
```
Three frequencies live near each other in this circuit and it is worth writing all three
down once, because confusing them is the standard way to lose marks and hours:

```
peak of |H|          f =  720.6 Hz  (w = 4528 rad/s)   |H| = 1.747
phase exactly -90    f =  795.8 Hz  (w = 5000 rad/s)   |H| = 1.667 = 1/(2 zeta)
gain down to 1/sqrt2 f = 1156.8 Hz  (w = 7268 rad/s)   |H| = 0.7071
```

The peak always sits below $\omega_n$, and it slides further below as the damping rises
until, at $\zeta = 1/\sqrt2 = 0.707$, the square root $\sqrt{1-2\zeta^2}$ reaches zero and
the peak arrives at DC — which is to say, there is no peak any more, and the response
falls monotonically from its DC value. That is the flattest a second-order low-pass can
be without sagging, and it is why $\zeta = 0.707$ has a name: the Butterworth response.

The height of the peak, for completeness, is $1/(2\zeta\sqrt{1-\zeta^2}) = 1.747$, a
little above the 1.667 you get at $\omega_n$ itself. At light damping the two are almost
identical, which is why the distinction is so easy to go on not noticing.
''',
                },
                {
                    "title": "Two RC sections that will not leave each other alone",
                    "minutes": 12,
                    "brief": r'''
The real work, and the one where the obvious answer is wrong.

Two identical RC low-passes, one after the other. Each on its own has a pole at
$-1/(RC) = -1000$ rad/s, so the temptation is to say the pair has poles at $-1000$ and
$-1000$ and move on. It does not, and the reason is visible on the drawing: the second
resistor is connected across the first capacitor, so the first section is not charging
into an open circuit. It is loaded.

The way through is a pair of node equations rather than two applications of the divider
rule. Get the denominator as a quadratic in $s$, then find its roots. You are asked for
the one that decides how long the output takes to settle, which is the one nearest the
imaginary axis.
''',
                    "prompt": "The output settles as a sum of two decaying exponentials. How far from the origin is the pole belonging to the slower of the two?",
                    "note": "Give the magnitude in rad/s, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "r1", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 10000},
                            {"id": "c1", "kind": "C", "x": 9, "y": 7, "rot": 1, "value": 1e-7},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 10},
                            {"id": "r2", "kind": "R", "x": 12, "y": 5, "rot": 0, "value": 10000},
                            {"id": "c2", "kind": "C", "x": 15, "y": 7, "rot": 1, "value": 1e-7},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 17, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [5, 5]},
                            {"a": [7, 5], "b": [9, 5]},
                            {"a": [9, 5], "b": [9, 6]},
                            {"a": [9, 8], "b": [9, 10]},
                            {"a": [9, 5], "b": [11, 5]},
                            {"a": [13, 5], "b": [15, 5]},
                            {"a": [15, 5], "b": [15, 6]},
                            {"a": [15, 8], "b": [15, 10]},
                            {"a": [15, 5], "b": [17, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "1.00 V step at t = 0"},
                        {"label": "R1, R2", "value": "10.0 kΩ each"},
                        {"label": "C1, C2", "value": "100 nF each"},
                        {"label": "State before the step", "value": "both capacitors empty"},
                        {"label": "Output", "value": "across C2"},
                    ],
                    "aside": "Write KCL at both capacitor nodes with $Z_C = 1/(sC)$, eliminate the middle "
                             "node, and the denominator comes out as "
                             "$s^2R_1C_1R_2C_2 + s(R_1C_1 + R_2C_2 + R_1C_2) + 1$. The third term in that "
                             "bracket is the loading, and it is the whole story.",
                    # The denominator is recovered from a single measured point rather than restated:
                    # 1/H at s = j w is (1 - a2 w^2) + j a1 w for this topology, so the magnitude and
                    # phase the solver reports at 300 Hz give a1 and a2, and the quadratic gives the
                    # roots. Change any component and the measured coefficients change with it.
                    "check": r'''
const V = c.values('V')[0];
const f = 300, w = 2 * Math.PI * f;
const g = c.gain(f) / V;                 /* |H| at 300 Hz */
const ph = c.phase(f) * Math.PI / 180;   /* arg H, radians */
const re = Math.cos(ph) / g;             /* 1/H = (1 - a2 w^2) + j a1 w */
const im = -Math.sin(ph) / g;
const a1 = im / w;
const a2 = (1 - re) / (w * w);
const d = Math.sqrt(a1 * a1 - 4 * a2);
return Math.abs((-a1 + d) / (2 * a2));   /* the root nearer the origin */
''',
                    "answer": 382.0,
                    "tol": 3.0,
                    "unit": "rad/s",
                    "hint": "$R_1C_1 = R_2C_2 = R_1C_2 = 10^{-3}$ s, so the denominator is "
                            "$10^{-6}s^2 + 3\\times10^{-3}s + 1$. Solve it with the quadratic formula and "
                            "take the root of smaller magnitude.",
                    "wrong": "If you got 1000, the two sections were treated as independent — that is the "
                             "answer for two RC stages with a buffer between them, and there is no buffer "
                             "here. If you got 2618, that is the *fast* pole, the other root of the same "
                             "quadratic. If you got 3000, that is the sum of the two pole magnitudes, which "
                             "is the coefficient ratio $a_1/a_2$ and not a pole.",
                    "why": r'''
```
KCL at the two capacitor nodes, with A the middle node and B the output:

    at B:   (A - B)/R2 = B * s C2          ->   A = B (1 + s R2 C2)
    at A:   (Vin - A)/R1 = A * s C1 + (A - B)/R2

substituting A and collecting B:

    H(s) = B/Vin = --------------------------------------------------
                    s^2 R1 C1 R2 C2  +  s (R1C1 + R2C2 + R1C2)  +  1

the three time products, all equal here:

    R1 C1 = 10e3 * 100e-9 = 1e-3        R2 C2 = 1e-3        R1 C2 = 1e-3

    a2 = 1e-3 * 1e-3      = 1e-6
    a1 = 1e-3 + 1e-3 + 1e-3 = 3e-3

    1e-6 s^2 + 3e-3 s + 1 = 0

    s = [ -3e-3 +/- sqrt(9e-6 - 4e-6) ] / (2 * 1e-6)
      = [ -3e-3 +/- sqrt(5e-6)        ] / 2e-6
      = [ -3e-3 +/- 2.23607e-3        ] / 2e-6

    s = -0.76393e-3 / 2e-6  = -381.97   <- the slow one, and the answer
    s = -5.23607e-3 / 2e-6  = -2618.03

check:  product 381.97 * 2618.03 = 1.000e6 = 1/a2       sum 3000 = a1/a2
```
The interesting quantity is $R_1C_2$, the cross term. Suppose the two sections were
separated by a buffer, so that the first one never noticed the second: then $a_1$ would
be $R_1C_1 + R_2C_2 = 2\times10^{-3}$, the discriminant $a_1^2 - 4a_2$ would be exactly
zero, and both poles would sit on top of each other at $-1000$ rad/s. Loading adds the
third millisecond to $a_1$, which prises that repeated root apart — one pole moving in
towards the origin, the other out away from it, with their product pinned at $10^{6}$
because $a_2$ never changed.

So loading did not just slow the circuit down; it made it lopsided. The slow pole at
$-382$ carries a time constant of $1/381.97 = 2.62$ ms, against the 1 ms a naive cascade
predicts — and since it is the slow pole that is still visible once the fast one has
gone, the circuit takes about two and a half times as long to settle as the arithmetic
of two independent sections would suggest. Cascading filters and hoping the stages will
not notice each other is one of the most reliable ways to build something slower than
the specification, and it is why op-amp buffers appear between passive stages.

(For the curious: the two roots are $1000/\varphi^2$ and $1000\varphi^2$ with
$\varphi = 1.618$ the golden ratio, which is what a quadratic with coefficients 1, 3, 1
always produces. It has no significance at all, and it is a memorable way to keep hold
of 382 and 2618.)
''',
                },
            ],
            "sandbox": {
                "title": "The same poles, seen in frequency",
                "visualiser": "bode",
                "minutes": 9,
                "initial": {"wn": 20, "zeta": 0.25, "K": 1},
                "brief": r'''
Module 1 looked at poles through the step response. This is the same pole pair seen
the other way, by sweeping a sinusoid across frequency and recording what comes out.

The upper plot is $20\log_{10}|H(j\omega)|$ in decibels; the lower is the phase in
degrees. Both use a logarithmic frequency axis, which is why a factor of ten always
occupies the same width. The dashed line on the upper plot marks 0 dB — output equal
to input — and the dashed line on the lower marks $-90°$. The amber dot marks the
gain at $\omega = \omega_n$.

The sliders are the same $\omega_n$ and $\zeta$ as before, plus a gain $K$ that
multiplies the whole response.
''',
                "notice": [
                    "It opens at $\\omega_n = 20$, $\\zeta = 0.25$, $K = 1$. The gain is flat at 0 dB across the left of the plot, bulges up to about $+6.3$ dB just before $\\omega = 20$, then falls away steeply. The amber dot sits at $+6.0$ dB, which is $K/(2\\zeta) = 2$ expressed in decibels — the resonant *peak* and the value *at* $\\omega_n$ are close but not identical.",
                    "Read the lower plot. The phase leaves 0° on the far left and crosses the dashed $-90°$ line exactly at $\\omega = 20$, then flattens out at $-180°$ on the right. That final $-180°$ is the fingerprint of two poles; a single pole can never get past $-90°$.",
                    "Raise $\\zeta$ to 1. The bulge vanishes completely and the amber dot drops to $-6.0$ dB, which is $1/(2 \\times 1)$ in decibels. The phase still passes through $-90°$ at $\\omega = 20$, but the whole swing from 0° to $-180°$ is now spread over far more of the frequency axis — the crossing sits in the same place, the approach to it is gentler.",
                    "Put $\\zeta$ back to 0.25 and read the roll-off on the upper plot: about $-40$ dB at $\\omega = 200$, and the curve reaches the bottom of the frame, $-80$ dB, at $\\omega = 2000$. Two decades, 80 dB — that is 40 dB per decade, which is what two poles do. Now drag $K$ up to 10 and the whole gain curve lifts by 20 dB while the phase curve does not move at all.",
                ],
            },
            "derive": {
                "title": "From R, L and C to $\\omega_n$ and $\\zeta$",
                "minutes": 14,
                "vars": ["s", "R", "L", "C", "omega_n", "zeta", "K", "V_in", "V_out"],
                "brief": r'''
A resistor, an inductor and a capacitor all in series across a source, with the output
taken across the capacitor. This is the circuit you are about to build.

The aim is to get from the three component values to the two numbers that actually
describe the behaviour — $\omega_n$ and $\zeta$ — so that a design specification
written in those terms can be turned into parts.

Use $Z_R = R$, $Z_L = sL$ and $Z_C = 1/(sC)$, and remember that in series the same
current flows through all three, so the ordinary divider rule applies.
''',
                "steps": [
                    {
                        "prompt": "Write $H(s) = V_{out}/V_{in}$ as an impedance divider, leaving $Z_C$ as $1/(sC)$ for now.",
                        "answer": "\\frac{\\frac{1}{sC}}{R + sL + \\frac{1}{sC}}",
                        "hint": "The output impedance goes on top, the total series impedance on the bottom.",
                        "deconstruct": [
                            "In series the three impedances add: $Z_{total} = R + sL + 1/(sC)$.",
                            "The output is across $C$ alone, so the ratio is $Z_C/Z_{total}$.",
                        ],
                    },
                    {
                        "prompt": "Multiply top and bottom by $sC$ to clear the inner fraction, and write $H(s)$ as a single ratio of polynomials in $s$.",
                        "answer": "\\frac{1}{s^2 LC + sRC + 1}",
                        "hint": "$sC \\times 1/(sC) = 1$ on top; on the bottom every term picks up a factor $sC$.",
                        "deconstruct": [
                            "Top: $sC \\cdot \\dfrac{1}{sC} = 1$.",
                            "Bottom: $sC(R + sL + 1/(sC)) = sRC + s^2LC + 1$.",
                        ],
                    },
                    {
                        "prompt": "Divide top and bottom by $LC$ to reach the standard form $\\dfrac{K\\omega_n^2}{s^2 + 2\\zeta\\omega_n s + \\omega_n^2}$. Comparing the constant terms gives $\\omega_n^2 = 1/(LC)$. Write $\\omega_n$ itself.",
                        "answer": "\\frac{1}{\\sqrt{LC}}",
                        "hint": "Take the positive square root of $1/(LC)$.",
                        "deconstruct": [
                            "After dividing through, the constant term of the denominator is $1/(LC)$.",
                            "The standard form calls that constant term $\\omega_n^2$.",
                        ],
                    },
                    {
                        "prompt": "Comparing the $s$ coefficients gives $2\\zeta\\omega_n = R/L$. Substitute your $\\omega_n$ and write $\\zeta$ in terms of $R$, $L$ and $C$.",
                        "answer": "\\frac{R}{2}\\sqrt{\\frac{C}{L}}",
                        "hint": "$\\zeta = \\dfrac{R}{2L\\omega_n} = \\dfrac{R\\sqrt{LC}}{2L}$, and $\\sqrt{LC}/L = \\sqrt{C/L}$.",
                        "deconstruct": [
                            "From $2\\zeta\\omega_n = R/L$, $\\zeta = \\dfrac{R}{2L\\omega_n}$.",
                            "Substituting $\\omega_n = 1/\\sqrt{LC}$ gives $\\zeta = \\dfrac{R\\sqrt{LC}}{2L}$.",
                            "And $\\dfrac{\\sqrt{LC}}{L} = \\sqrt{\\dfrac{C}{L}}$.",
                        ],
                    },
                    {
                        "prompt": "Now design. With $L = 0.1$ H and $C = 2.5\\ \\mu$F, $\\omega_n$ comes to 2000 rad/s. What resistance, in ohms, gives $\\zeta = 0.25$?",
                        "answer": "100",
                        "hint": "Rearrange to $R = 2\\zeta\\sqrt{L/C}$, then put the numbers in. $\\sqrt{0.1/2.5\\times10^{-6}} = 200$.",
                        "deconstruct": [
                            "$\\zeta = \\dfrac{R}{2}\\sqrt{\\dfrac{C}{L}}$ rearranges to $R = 2\\zeta\\sqrt{\\dfrac{L}{C}}$.",
                            "$L/C = 0.1/2.5\\times10^{-6} = 40000$, whose square root is 200.",
                            "So $R = 2 \\times 0.25 \\times 200$.",
                        ],
                    },
                ],
                "closing": r'''
Two things are worth keeping. First, $\zeta$ depends on the *ratio* $C/L$, so you can
slide both up together without changing the shape of the response — only its speed.
Second, $\sqrt{L/C}$ has units of ohms and is called the characteristic impedance of
the pair; damping is just the resistance measured against it. Those numbers, 0.1 H,
2.5 µF and 100 Ω, are the ones the build exercise asks you to reach.
''',
            },
            "build": {
                "title": "Placing a pole pair with real components",
                "minutes": 26,
                "brief": r'''
Build a second-order low-pass filter whose poles sit exactly where you want them.

The specification, in the language of module 1:

- a **natural frequency** $\omega_n = 2000$ rad/s, which is 318.3 Hz
- a **damping ratio** $\zeta = 0.25$
- a **gain of 1** well below the corner, so the filter passes low frequencies untouched

The first two of those put the poles at $s = -500 \pm j1936$; the third fixes the
height of the response, not where the poles sit.

## What is on the canvas

A 1 V source, its ground, and a 0.1 H inductor already wired to the source's positive
terminal. Add a resistor, a capacitor, a second ground and a probe to finish a series
RLC with the **output taken across the capacitor**. Set the two values you add so that
the specification is met. Two relations give both, $\omega_n = 1/\sqrt{LC}$ and
$\zeta = \tfrac{R}{2}\sqrt{C/L}$; the guided derivation in this module builds them from
the divider rule if you want to see where they come from before using them.

The source is set to 1 V because the checks read the probe voltage directly and treat
it as the gain — leave it at 1 V, or every gain measurement comes out scaled.

## How this is measured

The checks sweep the finished circuit and read three things off it, none of which
cares how you laid the drawing out:

- the gain at 1 Hz, far below the corner, which must be 1
- the **phase** at 318.3 Hz, which must be $-90°$ — a second-order pole pair passes
  through exactly $-90°$ at $\omega_n$ whatever the damping, so this measurement pins
  $\omega_n$ on its own
- the **gain** at 318.3 Hz, which must be $1/(2\zeta) = 2$ — and that pins $\zeta$

A fourth check reads the gain a decade and two decades above the corner and confirms
they differ by a factor of 100. That is the 40 dB/decade of two poles; a plain RC
would give a factor of 10 and fail.

Changing the inductor is allowed. Any $L$, $R$ and $C$ that put the poles in the right
place will pass — but with $L$ fixed at 0.1 H there is exactly one answer, and it is
the one you computed in the derivation.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.1},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.1},
                        {"id": "p3", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 100},
                        {"id": "p4", "kind": "C", "x": 13, "y": 7, "rot": 1, "value": 2.5e-6},
                        {"id": "p5", "kind": "GND", "x": 13, "y": 10},
                        {"id": "p6", "kind": "OUT", "x": 15, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [11, 5], "b": [13, 5]},
                        {"a": [13, 5], "b": [13, 6]},
                        {"a": [13, 8], "b": [13, 10]},
                        {"a": [13, 5], "b": [15, 5]},
                    ],
                },
                "checks": [
                    {"name": "one 1 V source drives the filter", "code": r'''
c.assert(c.count('V') === 1,
  'Use exactly one voltage source, so that "the gain" means one thing. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 1, 0.001,
  'the source amplitude — the checks read the probe voltage as the gain, so the input must be 1 V');
'''},
                    {"name": "low frequencies pass through untouched", "code": r'''
c.close(c.gain(1), 1.0, 0.02,
  'the gain at 1 Hz, far below the corner — a passive low-pass should hand the input straight over');
'''},
                    {"name": "the phase is -90 degrees at 318.3 Hz, so the natural frequency is 2000 rad/s", "code": r'''
const ph = c.phase(318.30988618379064);
c.assert(Math.abs(ph + 90) <= 3,
  'A second-order pole pair passes through exactly -90 degrees at its natural frequency. ' +
  'At 318.3 Hz this circuit is at ' + ph.toFixed(1) + ' degrees, so its natural frequency is not 2000 rad/s.');
'''},
                    {"name": "the gain at that frequency is 2, so the damping ratio is 0.25", "code": r'''
c.close(c.gain(318.30988618379064), 2.0, 0.04,
  'the gain at the natural frequency, which for this form is 1/(2*zeta)');
'''},
                    {"name": "the roll-off is 40 dB per decade, so there really are two poles", "code": r'''
const a = c.gain(3183.0988618379064);
const b = c.gain(31830.988618379065);
c.assert(b > 0, 'The response died to nothing; check the output is taken across the capacitor.');
c.close(a / b, 100, 0.05,
  'the ratio of the gains one and two decades above the corner — two poles give 100, a single RC only 10');
'''},
                ],
                "hints": [
                    "The order round the loop is source, inductor, resistor, capacitor, ground, with the probe on the node between the resistor and the capacitor.",
                    "$\\omega_n = 1/\\sqrt{LC}$. With $L = 0.1$ H and $\\omega_n = 2000$ rad/s, $C = 1/(\\omega_n^2 L) = 2.5\\ \\mu$F. Type `2.5u` in the value box.",
                    "$\\zeta = \\dfrac{R}{2}\\sqrt{C/L}$. With those values $\\sqrt{C/L} = 0.005$, so $\\zeta = 0.0025R$ and $\\zeta = 0.25$ needs $R = 100$ Ω.",
                    "If the phase check passes but the gain at the corner is too small, $\\omega_n$ is right and the resistor is too large — the damping is what the resistor sets.",
                    "If the low-frequency gain is not 1, the probe is probably on the wrong node. Across the capacitor the inductor is a short and the capacitor an open at DC, so the whole input appears at the output.",
                ],
            },
            "lab": {
                "title": "Partial fractions by residue, and the response they give",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
A transfer function arrives as two coefficient lists, highest power first, exactly as
`numpy.roots` and `numpy.polyval` expect. `[1.0, 4.0, 3.0]` means $s^2 + 4s + 3$.

Write four functions.

- `poles(den)` returns the roots of the denominator.
- `residues(num, den)` returns the residue at each pole, in the same order as `poles`
  returns them. For distinct poles the residue is
  $k_i = N(p_i)/D'(p_i)$ — numerator over the *derivative* of the denominator, both
  evaluated at the pole. `np.polyder` differentiates a coefficient list.
- `impulse_response(num, den, t)` returns $\sum_i k_i e^{p_i t}$ evaluated on the array
  `t`, as **real** numbers.
- `dc_gain(num, den)` returns $H(0)$.

## Why the answer is real

The poles of a real circuit come in conjugate pairs, and so do their residues. Add the
two terms of a pair and the imaginary parts cancel exactly, leaving a decaying
sinusoid. Numerically they cancel to about $10^{-16}$ rather than to zero, so take
`.real` at the end — and if you find yourself taking `abs()` instead, stop: that would
turn a legitimate negative voltage into a positive one.

The residue formula only holds for **distinct** poles. Repeated poles need an extra
term in $te^{-at}$, and the formula divides by zero if you try it, which at least
fails loudly.
''',
                "files": [{"name": "main.py", "content": r'''
"""Partial fractions by the residue formula, and the time response they encode."""

import numpy as np


def poles(den):
    """Roots of the denominator polynomial, highest power first."""
    # TODO: np.roots does this in one call.
    return np.array([])


def residues(num, den):
    """Residue at each pole, in the same order as poles(den)."""
    # TODO: for each pole p, np.polyval(num, p) / np.polyval(np.polyder(den), p).
    return np.array([])


def impulse_response(num, den, t):
    """Sum of k_i exp(p_i t) over the poles, returned as real numbers."""
    # TODO: accumulate into a complex array, then return its .real part.
    return np.zeros(np.asarray(t, dtype=float).shape)


def dc_gain(num, den):
    """H(0) — the gain the system settles to."""
    # TODO: evaluate both polynomials at s = 0.
    return 0.0


if __name__ == "__main__":
    num, den = [6.0], [1.0, 4.0, 3.0]
    print("poles:", poles(den))
    print("residues:", residues(num, den))
    print("h(0.5):", impulse_response(num, den, np.array([0.5])))
    print("dc gain:", dc_gain(num, den))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Partial fractions by the residue formula, and the time response they encode.

Verified by running this file:
    6/((s+1)(s+3)) -> poles -3, -1 with residues -3, +3, so h(t) = 3e^-t - 3e^-3t
    h(0.5) = 1.1502014986926108, which is 3*exp(-0.5) - 3*exp(-1.5) exactly
    4/(s^2+2s+5) -> poles -1 +/- 2j, residues -/+ j, so h(t) = 2 e^-t sin 2t
    h(0.5) = 1.0207559030891455 = 2*exp(-0.5)*sin(1)
"""

import numpy as np


def poles(den):
    """Roots of the denominator polynomial, highest power first."""
    return np.roots(den)


def residues(num, den):
    """Residue at each pole, in the same order as poles(den)."""
    dden = np.polyder(den)
    return np.array([np.polyval(num, p) / np.polyval(dden, p) for p in poles(den)])


def impulse_response(num, den, t):
    """Sum of k_i exp(p_i t) over the poles, returned as real numbers."""
    t = np.asarray(t, dtype=float)
    y = np.zeros(t.shape, dtype=complex)
    for k, p in zip(residues(num, den), poles(den)):
        y = y + k * np.exp(p * t)
    return y.real


def dc_gain(num, den):
    """H(0) — the gain the system settles to."""
    return np.polyval(num, 0.0) / np.polyval(den, 0.0)


if __name__ == "__main__":
    num, den = [6.0], [1.0, 4.0, 3.0]
    print("poles:", poles(den))
    print("residues:", residues(num, den))
    print("h(0.5):", impulse_response(num, den, np.array([0.5])))
    print("dc gain:", dc_gain(num, den))
'''}],
                "hints": [
                    "`poles` is `np.roots(den)` and nothing else.",
                    "`np.polyder(den)` returns the coefficient list of $D'(s)$; then `np.polyval(dden, p)` evaluates it at the pole. A list comprehension over the poles gives the residues in one line.",
                    "In `impulse_response`, start with `y = np.zeros(t.shape, dtype=complex)` — starting with a real array silently discards every imaginary part as you add to it.",
                    "`dc_gain` is `np.polyval(num, 0.0) / np.polyval(den, 0.0)`, which for a plain coefficient list is just the last entry of each.",
                    "A useful self-check: when the numerator's degree is at least two below the denominator's, the impulse response must start at exactly 0, because the residues sum to zero.",
                ],
                "tests": [
                    {"name": "a single real pole", "code": r'''
p = poles([1.0, 2.0])
assert len(p) == 1, f"s + 2 has one root, got {len(p)}"
assert abs(p[0] + 2.0) < 1e-12, f"the root of s + 2 is -2, got {p[0]}"
k = residues([1.0], [1.0, 2.0])
assert abs(k[0] - 1.0) < 1e-12, f"1/(s+2) has residue 1, got {k[0]}"
'''},
                    {"name": "two real poles, and residues that cancel at t = 0", "code": r'''
num, den = [6.0], [1.0, 4.0, 3.0]
p = np.sort(np.real(poles(den)))
assert abs(p[0] + 3.0) < 1e-9 and abs(p[1] + 1.0) < 1e-9, \
    f"s^2+4s+3 factorises as (s+1)(s+3), got roots {p}"
k = residues(num, den)
assert abs(np.sum(k)) < 1e-9, \
    f"with the numerator two degrees below, the residues must sum to 0, got {np.sum(k)}"
h0 = impulse_response(num, den, np.array([0.0]))[0]
assert abs(h0) < 1e-9, f"h(0) must therefore be 0, got {h0}"
'''},
                    {"name": "the impulse response matches the closed form", "code": r'''
got = impulse_response([6.0], [1.0, 4.0, 3.0], np.array([0.5]))[0]
want = 3.0 * np.exp(-0.5) - 3.0 * np.exp(-1.5)
assert abs(got - want) < 1e-9, \
    f"h(t) = 3exp(-t) - 3exp(-3t), so h(0.5) = {want}, got {got}"
got2 = impulse_response([6.0], [1.0, 4.0, 3.0], np.array([0.0, 0.5, 2.0]))
assert got2.shape == (3,), f"an array of times must give an array of values, got shape {got2.shape}"
'''},
                    {"name": "a complex pair gives a real decaying sinusoid", "code": r'''
num, den = [4.0], [1.0, 2.0, 5.0]
p = poles(den)
assert abs(abs(p[0].imag) - 2.0) < 1e-9, \
    f"s^2+2s+5 has roots -1 +/- 2j, got {p}"
got = impulse_response(num, den, np.array([0.5]))[0]
want = 2.0 * np.exp(-0.5) * np.sin(1.0)
assert abs(got - want) < 1e-9, \
    f"this pair gives h(t) = 2 exp(-t) sin(2t), so h(0.5) = {want}, got {got}"
assert np.imag(got) == 0.0 or isinstance(got, float) or got.imag == 0.0, \
    "the answer must be real, not a complex number with a tiny imaginary part"
'''},
                    {"name": "the DC gain, and the transform read back out of the response", "code": r'''
assert abs(dc_gain([6.0], [1.0, 4.0, 3.0]) - 2.0) < 1e-12, "6/3 = 2"
assert abs(dc_gain([1.0], [2.5e-07, 0.00025, 1.0]) - 1.0) < 1e-12, \
    "the RLC filter of the build exercise has a DC gain of 1"
t = np.linspace(0.0, 30.0, 300001)
y = impulse_response([6.0], [1.0, 4.0, 3.0], t) * np.exp(-2.0 * t)
h = t[1] - t[0]
area = h * (np.sum(y) - 0.5 * (y[0] + y[-1]))
assert abs(area - 0.4) < 1e-6, \
    f"transforming h(t) back at s=2 must return H(2) = 6/15 = 0.4, got {area}"
'''},
                ],
            },
            "quiz": {
                "title": "Reading a transfer function",
                "minutes": 9,
                "questions": [
                    {
                        "q": "$H(s) = \\dfrac{s+2}{(s+1)(s+5)}$. Its zeros and poles are:",
                        "opts": [
                            "a zero at $-1$ and $-5$, a pole at $-2$",
                            "a zero at $-2$, poles at $-1$ and $-5$",
                            "a zero at $+2$, poles at $+1$ and $+5$",
                            "poles at $-2$ and $-1$, a zero at $-5$",
                        ],
                        "a": 1,
                        "why": r'''
Zeros come from the **numerator**, poles from the **denominator**, and each is the
value of $s$ that makes its own factor vanish — so $s+2$ gives a zero at $-2$, not at
$+2$. Reading $s+2$ as a zero at $+2$ is the sign error that catches everyone once: the root
of $s + a$ is $-a$. Getting the zeros and poles the wrong way round inverts the
system: it would rise with frequency instead of falling.
''',
                    },
                    {
                        "q": "A system has poles at $-1$ and $-20$. Which term dominates the late part of the step response?",
                        "opts": [
                            "the $e^{-20t}$ term, because 20 is the larger number",
                            "both equally, because both poles are real",
                            "neither — the zero decides",
                            "the $e^{-t}$ term",
                        ],
                        "a": 3,
                        "why": r'''
$e^{-20t}$ has fallen to under a thousandth of its starting value by $t = 0.35$, while
$e^{-t}$ is still at 70% then. The **slow** pole — the one closest to the imaginary
axis — is the one still visible when everything else has gone, and it is what a
designer means by "the dominant pole". Reaching for the bigger number is the reflex worth unlearning: in the s-plane it is distance from the *imaginary axis*
that sets the speed, so the pole nearest that axis is the slow one and therefore the
one that matters. (Distance from the origin is a different measurement, and a pair like
$-1 \pm j100$ is far from the origin while still decaying slowly.)
''',
                    },
                    {
                        "q": "In $\\dfrac{6}{(s+1)(s+3)} = \\dfrac{A}{s+1} + \\dfrac{B}{s+3}$, what is $A$?",
                        "opts": ["3", "6", "$-3$", "2"],
                        "a": 0,
                        "why": r'''
Cover up the $(s+1)$ factor and evaluate what is left at $s = -1$: $6/(-1+3) = 3$.
(The residue formula $N(p)/D'(p)$ says the same thing: $D' = 2s+4$, which is 2 at
$s=-1$, and $6/2 = 3$.) $-3$ is the residue at the *other* pole — the two must sum to
zero here, because the numerator is two degrees below the denominator, and that is a
free check on your arithmetic.
''',
                    },
                    {
                        "q": "What does $\\dfrac{1}{(s+a)^2}$ invert to?",
                        "opts": ["$e^{-at}$", "$2e^{-at}$", "$te^{-at}$", "$\\tfrac{1}{2}t^2e^{-at}$"],
                        "a": 2,
                        "why": r'''
$te^{-at}$. A repeated pole is the one case the simple residue formula cannot handle —
it would divide by $D'(p)$, which is zero at a repeated root. Physically the extra
factor of $t$ is why a critically damped circuit rises more slowly at first than the
plain exponential you might expect: the response is a product of a rising ramp and a
falling exponential. The $\tfrac{1}{2}t^2$ form belongs to a pole repeated three times.
''',
                    },
                    {
                        "q": "For $H(s) = \\dfrac{K\\omega_n^2}{s^2+2\\zeta\\omega_n s + \\omega_n^2}$, what is $|H(j\\omega_n)|$?",
                        "opts": ["$K$", "$K/\\sqrt{2}$", "$2\\zeta K$", "$K/(2\\zeta)$"],
                        "a": 3,
                        "why": r'''
At $s = j\omega_n$ the terms $s^2$ and $\omega_n^2$ cancel exactly, leaving only
$2\zeta\omega_n \cdot j\omega_n$ on the bottom, so $|H| = K/(2\zeta)$ and the phase is
exactly $-90°$. $K/\sqrt{2}$ is the tempting one: $\omega_n$ is *not* the $-3$ dB point
unless $\zeta$ happens to be $1/\sqrt{2}$. With $\zeta = 0.25$ the gain there is 2 —
a gain of *two*, above the input, from a circuit containing nothing but a resistor, an
inductor and a capacitor.
''',
                    },
                    {
                        "q": "Where are the poles of a system with $\\omega_n = 2000$ rad/s and $\\zeta = 0.25$?",
                        "opts": [
                            "$-2000 \\pm j500$",
                            "$-500 \\pm j1936$",
                            "$-500 \\pm j2000$",
                            "$\\pm j2000$",
                        ],
                        "a": 1,
                        "why": r'''
The real part is $-\zeta\omega_n = -500$ and the imaginary part is
$\omega_n\sqrt{1-\zeta^2} = 2000\sqrt{0.9375} = 1936$. $-500 \pm j2000$ is the common slip of using $\omega_n$ itself as the imaginary
part — an easy mistake to forgive, since at
$\zeta = 0.25$ the difference is only 3%, but one that grows fast as the damping does.
A useful check: the poles must be exactly $\omega_n = 2000$ from the origin, and
$\sqrt{500^2 + 1936^2} = 2000$.
''',
                    },
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Shifting, scaling and signals that arrive late",
            "summary": "Four properties turn a short table of pairs into every transform you will need, and one of them produces something that is not a ratio of polynomials at all.",
            "concepts": [
                "**Time shift**: delaying a signal multiplies its transform by an exponential, $\\mathcal{L}\\{f(t-a)u(t-a)\\} = e^{-as}F(s)$ for $a \\ge 0$. The $u(t-a)$ is not decoration — without it the shifted signal would have a tail hanging back into $t < 0$, which the one-sided transform cannot see.",
                "Every piecewise-constant waveform is a sum of shifted steps. A pulse of height 1 lasting from 0 to $T$ is $u(t) - u(t-T)$, so its transform is $\\dfrac{1 - e^{-sT}}{s}$; a staircase whose steps fall at multiples of $T$ is a polynomial in $e^{-sT}$ over $s$.",
                "**Frequency shift**: $\\mathcal{L}\\{e^{-at}f(t)\\} = F(s+a)$. Multiplying a signal by a decaying exponential slides every pole a distance $a$ to the left, which is exactly what damping does to an oscillation.",
                "**Scaling**: $\\mathcal{L}\\{f(t/a)\\} = aF(as)$ for $a > 0$. A first-order circuit therefore has only one response shape; $RC$ decides how far that shape is stretched along the time axis and nothing else about it.",
                "**Multiplying by $t$** is differentiating in $s$: $\\mathcal{L}\\{tf(t)\\} = -dF/ds$. It is where a repeated pole comes from — $1/(s+a)^2 \\leftrightarrow te^{-at}$ — and the factor of $t$ out front is why a critically damped circuit settles more slowly than its exponent alone suggests.",
                "A switched input needs no new machinery, only linearity and time-invariance: the response to $u(t) - u(t-T)$ is the step response minus that same step response delayed by $T$. Every pulse problem in this module is that one sentence followed by arithmetic.",
                "$e^{-sT}$ is not a ratio of polynomials, so a pure delay has no poles and no zeros anywhere. Its magnitude is exactly 1 at every frequency and its phase is $-\\omega T$ — which is why no arrangement of R, L and C produces one, and why a real delay is either a length of cable or an approximation.",
            ],
            "read": [
                {
                    "title": "Signals that arrive late, and the factor that says so",
                    "minutes": 14,
                    "body": r'''
Everything the course has transformed so far begins at $t = 0$ and then keeps going: a
step that never comes back down, an exponential that decays forever, a sinusoid with
neither a beginning nor an end. Nothing on a bench behaves like that. A gate driver
puts out a pulse 200 ns wide and then stops. A length of coax hands over what it was
given four microseconds ago. A test waveform is three levels in a row, each held for a
different length of time.

None of that needs a new transform, and none of it needs a new integral. It needs one
property, and the property is small enough to derive in four lines.

## What "later" looks like to the integral

Take a signal $f(t)$ that is zero for $t < 0$, and slide the whole thing $a$ seconds to
the right, with $a \ge 0$. Call the slid version $g$. Whatever $f$ was doing at time
$t$, $g$ does at time $t + a$, so $g(t) = f(t-a)$ — and because $f$ was zero for
negative arguments, $g$ is zero everywhere before $t = a$.

Put $g$ into the defining integral and substitute $\lambda = t - a$, so that
$t = \lambda + a$ and $dt = d\lambda$:

$$G(s) = \int_0^{\infty} f(t-a)\,e^{-st}\,dt
       = \int_{-a}^{\infty} f(\lambda)\,e^{-s(\lambda + a)}\,d\lambda$$

The lower limit came down to $-a$ because $t = 0$ is $\lambda = -a$. But $f$ is zero
across the whole stretch from $-a$ to $0$, so that piece of the integral contributes
nothing and the limit can be pushed back up to zero. And $e^{-sa}$ does not depend on
$\lambda$, so it comes outside:

$$G(s) = e^{-as}\int_0^{\infty} f(\lambda)e^{-s\lambda}\,d\lambda = e^{-as}F(s)$$

A delay in time is a multiplication by $e^{-as}$ in $s$. That is the whole rule, and
notice how little it cost: one substitution and one observation about where $f$ is
zero.

Two things in that derivation are worth keeping. First, the sign. The factor is
$e^{-as}$ with $a > 0$, so it *shrinks* as $s$ runs out along the real axis; a positive
exponent would belong to a signal that had already started before the origin, which the
one-sided transform cannot represent at all. That is less a limitation of the method
than a statement about causality: nothing arrives before it is sent. Second, the
derivation leaned on $f$ being zero before the origin. That assumption is not
decoration. It is the entire content of the $u(t-a)$ the rule is always written with.

## The gate is doing real work

Written out in full:

$$\mathcal{L}\{f(t-a)\,u(t-a)\} = e^{-as}F(s), \qquad a \ge 0$$

The $u(t-a)$ says: this signal is *nothing at all* until $t = a$, and from that instant
on it is $f$, running from $f$'s own beginning.

Here is the mistake it prevents, and it is worth doing once with numbers because
everybody makes it once. Take $f(t) = t$, transform $1/s^2$. Two quite different
signals can both be described in English as "the ramp, delayed by 2 seconds":

```text
A:   (t - 2) u(t - 2)     zero until t = 2, then climbs from 0
B:   t u(t - 2)           zero until t = 2, then JUMPS to 2 and climbs on from there
```

$A$ is the ramp itself, moved. $B$ is the ramp with a piece cut off the front, so it
arrives already two units high. The two differ by a step of height 2 at $t = 2$, and
their transforms must differ by that step's transform:

```text
A:   L{(t-2) u(t-2)} = e^(-2s) / s^2            the rule, applied to f(t) = t

B:   write t = (t - 2) + 2, so
         t u(t-2) = (t-2) u(t-2) + 2 u(t-2)
     L{B} = e^(-2s)/s^2  +  2 e^(-2s)/s
          = e^(-2s) ( 1/s^2 + 2/s )
```

Writing $e^{-2s}/s^2$ for $B$ — that is, multiplying the transform by $e^{-as}$ without
first checking that the signal really is $f$ starting over — is the standard slip, and
it is tempting because the rule looks like a licence to attach $e^{-as}$ to anything
that happens late. Nothing warns you afterwards either: the answer you get is a
perfectly respectable transform of a perfectly respectable signal. It is simply not the
signal on the page.

## Every switching waveform is a sum of steps

With the delay rule in hand, piecewise-constant inputs stop being a separate topic. A
step is $u(t) \leftrightarrow 1/s$; every other change of level is a step with a height
and a start time; and the transform is linear, so you add them up.

A pulse of height $V$ starting at 0 and ending at $T$ is a step up and the identical
step down, $T$ later:

$$v(t) = V\,u(t) - V\,u(t-T) \qquad\Longrightarrow\qquad V(s) = \frac{V\left(1 - e^{-sT}\right)}{s}$$

### Worked: a 3 V pulse, 2 ms wide

```text
height V = 3 V,   width T = 2 ms = 2e-3 s

decompose:   v(t) = 3 u(t) - 3 u(t - 2e-3)

transform:   V(s) = 3/s - 3 e^(-0.002 s)/s
                  = 3 (1 - e^(-0.002 s)) / s
```

A transform is hard to check by eye, so use the one value of $s$ that means something
physical. At $s = 0$ the defining integral collapses to $\int_0^\infty v(t)\,dt$ — the
*area* under the signal, which for this rectangle is $3\ \mathrm{V} \times 2\ \mathrm{ms}
= 6$ mV·s. The expression looks like $0/0$ there, so expand the exponential first:

```text
e^(-sT)      = 1 - sT + (1/2)(sT)^2 - ...
1 - e^(-sT)  =     sT - (1/2)s^2T^2 + ...

V(s) = 3 ( sT - (1/2)s^2 T^2 + ... ) / s
     = 3 ( T  - (1/2)s  T^2 + ... )

at s = 0:   V(0) = 3T = 3 * 2e-3 = 6e-3 volt-seconds
```

which is the area, as it had to be. That check costs half a minute and catches a
dropped factor of $s$ or a flipped sign every time.

## Worked: a pulse through an RC low-pass

This is the calculation the rule was invented for. A 10 kΩ resistor in series with a
22 nF capacitor, output taken across the capacitor, driven from rest by a 5 V pulse
400 µs wide.

```text
the circuit:   H(s) = 1 / (1 + s R C)
               tau  = R C = 10e3 * 22e-9 = 2.20e-4 s = 220 us

the input:     Vin(s) = 5 (1 - e^(-sT)) / s          with T = 400 us

the output:    Vout(s) = H(s) Vin(s)

                          5                          5
                = ----------------  -  e^(-sT) ----------------
                   s (1 + s tau)                 s (1 + s tau)
```

The two terms are the *same function of $s$*; the second is the first with a delay
factor in front of it. So invert the first once, and the second is that same time
function shifted by $T$ and gated:

```text
first term   ->  5 (1 - e^(-t/tau))                    for t >= 0
second term  ->  5 (1 - e^(-(t-T)/tau)) u(t - T)       for t >= T

so
    0 <= t < T :  v(t) = 5 (1 - e^(-t/tau))
    t >= T     :  v(t) = 5 (1 - e^(-t/tau)) - 5 (1 - e^(-(t-T)/tau))
                       = 5 ( e^(-(t-T)/tau) - e^(-t/tau) )
```

Look at what happened on that last line: the two 5s and the two 1s cancelled. The
charging curve and the discharging curve are the same curve, so once the pulse has
ended what remains is a pure decay with nothing constant in it.

Three values, worked all the way through:

```text
tau = 220 us

t = 400 us  (the falling edge, approached from below):
    t/tau = 400/220 = 1.81818     e^(-1.81818) = 0.16232
    v = 5 (1 - 0.16232) = 5 * 0.83768 = 4.1884 V

t = 500 us  (100 us after the edge):
    (t-T)/tau = 100/220 = 0.454545    e^(-0.454545) = 0.63474
    t/tau     = 500/220 = 2.27273     e^(-2.27273) = 0.10303
    v = 5 (0.63474 - 0.10303) = 5 * 0.53171 = 2.6585 V

t = 800 us:
    (t-T)/tau = 400/220 = 1.81818     e^(-1.81818) = 0.16232
    t/tau     = 800/220 = 3.63636     e^(-3.63636) = 0.026348
    v = 5 (0.16232 - 0.026348) = 5 * 0.135972 = 0.6799 V
```

The output peaks at 4.19 V, not 5 V, because the pulse ended before the capacitor had
finished charging; then it decays from there with the same 220 µs constant it charged
with. The peak is fixed by $T/\tau$ and nothing else: 1.82 time constants of charging
covers 83.8% of the gap. Halve the pulse width and the peak drops to
$5(1 - e^{-0.909}) = 2.99$ V. That ratio is the number worth carrying around — a pulse
much longer than $\tau$ comes through with its flat top intact, a pulse much shorter
barely registers, and everything interesting happens where $T/\tau$ is near 1.

## Where the rule stops

$e^{-sT}$ is not a ratio of polynomials, and nothing you can do to it makes it one.
That has consequences much larger than they look.

A finite network of resistors, inductors and capacitors always has a transfer function
that *is* a ratio of polynomials in $s$, because every impedance is $R$, $sL$ or
$1/(sC)$ and every combination rule is addition, multiplication and division of those.
So no arrangement of passive parts, however clever, is a delay. A real delay is a
physical length of something — cable, an acoustic path, fibre, a shift register clocked
at a known rate — and everything else is an approximation.

The usual approximation is Padé's, which matches the exponential's series as far as one
pole and one zero can:

$$e^{-sT} \approx \frac{1 - sT/2}{1 + sT/2}$$

Its magnitude is exactly 1 at every frequency, like the real thing, because numerator
and denominator are mirror images across the imaginary axis. Its phase is where it
parts company:

```text
T = 1 ms

f = 100 Hz:   wT = 2*pi*100*1e-3 = 0.6283 rad
              true delay :  -wT           = -36.0 deg
              Pade       :  -2 atan(wT/2) = -34.9 deg

f = 300 Hz:   wT = 1.885 rad
              true delay :  -108.0 deg
              Pade       :   -86.6 deg
```

Good to about a degree while $\omega T$ is small; useless by the time the delay costs a
third of a cycle. That is the honest position: the approximation buys you a pole and a
zero you can put into a controller design, and it buys them only near DC.

The second consequence is about feedback. A pure delay contributes phase lag
$-\omega T$ that grows without limit as frequency rises, and contributes no attenuation
at all to hold it back. Poles at least pay for their phase with roll-off; a delay does
not. That is why dead time is the hardest thing in a control loop and why turning the
gain down is so often the only fix available.

The third is where the next transform comes from. If a signal is only looked at every
$T$ seconds, one sample of delay is exactly $e^{-sT}$ — and giving that awkward factor
a name of its own, $z = e^{sT}$, turns a discrete system back into ratios of
polynomials, in $z$ this time. The $z$-transform is this module's delay factor,
promoted to a variable.
''',
                },
                {
                    "title": "Damping is a shift, and every first-order curve is one curve",
                    "minutes": 13,
                    "body": r'''
The delay rule moved a signal along the time axis and paid for it with a factor in $s$.
The two rules in this unit work the other pairing: one multiplies the signal and
*shifts* the transform, the other stretches the time axis and stretches $s$ the
opposite way. Between them they account for most of what a table of pairs would
otherwise have to list one line at a time.

## Multiplying by an envelope

Start from the picture. Take any signal and multiply it, instant by instant, by
$e^{-at}$ with $a > 0$. Nothing about its shape in time is rearranged — no part of it
arrives earlier or later than it did — but the whole thing is squeezed inside a
decaying envelope. A sinusoid becomes a ringing that dies away. A constant becomes a
decay. A decay becomes a faster decay. This is what a resistor does to an LC loop, what
friction does to a pendulum, and what every real oscillation eventually does.

The transform makes short work of it:

$$\mathcal{L}\{e^{-at}f(t)\} = \int_0^\infty f(t)\,e^{-at}e^{-st}\,dt
 = \int_0^\infty f(t)\,e^{-(s+a)t}\,dt = F(s+a)$$

The two exponentials merged and $s$ became $s + a$. There is no trick in it: the
transform's kernel is itself an exponential, so multiplying the signal by another
exponential only changes which exponential you were testing against.

### What it does to the poles

Replacing $s$ by $s+a$ moves every root. If $D(s)$ vanished at $s = p$, then $D(s+a)$
vanishes where $s + a = p$, which is at $s = p - a$. Every pole slides a distance $a$ to
the **left**. And left is the direction of decay — a pole's real part is the exponential
rate of the term it contributes — so the picture and the algebra are saying the same
thing in two languages.

## Completing the square is this rule, read backwards

You will meet the rule far more often backwards than forwards. A denominator with no
real roots cannot be factorised into the simple pairs of module 2; completing the
square turns it into a shifted version of something you already know.

```text
F(s) = 10 / (s^2 + 6s + 34)

the discriminant is 36 - 136 < 0, so there are no real roots.
complete the square instead:

    s^2 + 6s + 34 = (s^2 + 6s + 9) + 25
                  = (s + 3)^2 + 5^2

so   F(s) = 10 / ( (s+3)^2 + 5^2 )

compare with the sine pair      w / (s^2 + w^2)  <->  sin(w t)
at w = 5 that reads             5 / (s^2 + 25)   <->  sin 5t

    F(s) = 2 * [ 5 / ((s+3)^2 + 25) ]

which is the sine transform with s replaced by s + 3, doubled.
Read the shift rule right to left:

    f(t) = 2 e^(-3t) sin 5t
```

Two values, so that it is a number and not just a shape:

```text
t = 0.2 s:   e^(-0.6) = 0.548812     sin(1.0 rad) = 0.841471
             f = 2 * 0.548812 * 0.841471 = 0.9236

t = 0.5 s:   e^(-1.5) = 0.223130     sin(2.5 rad) = 0.598472
             f = 2 * 0.223130 * 0.598472 = 0.2671
```

The signal rings at 5 rad/s inside an envelope that has fallen to $e^{-1.5} = 0.22$ by
half a second. Both facts were readable off the poles at $-3 \pm j5$ before any of the
arithmetic: the imaginary part is the ringing frequency, the real part is the decay
rate.

### The mistake, and what it actually costs

Everything in $F$ gets shifted, the numerator included. The sine escapes this because
its numerator is a bare $\omega$ with no $s$ in it; the cosine does not:

$$\mathcal{L}\{e^{-4t}\cos 3t\} = \frac{s+4}{(s+4)^2 + 9}
\qquad\text{not}\qquad \frac{s}{(s+4)^2 + 9}$$

The version with the bare $s$ on top is the standard slip, and it is tempting because
the denominator is where all the visible work happened. It is not a harmless one. Split
the wrong expression and see what signal it actually describes:

```text
      s              (s + 4) - 4              s + 4              4     3
-------------  =  ---------------  =  ---------------  -  --- * ---------------
 (s+4)^2 + 9        (s+4)^2 + 9         (s+4)^2 + 9        3     (s+4)^2 + 9

  ->  e^(-4t) ( cos 3t - (4/3) sin 3t )

amplitude of that combination = sqrt(1 + (4/3)^2) = 5/3 = 1.667
phase                          = atan(4/3)        = 53.1 degrees
```

So the slip returns a damped cosine 67% too large and 53° out of phase. What makes it
hard to catch is that the obvious sanity check passes: both signals equal 1 at $t = 0$,
so the initial-value theorem gives the same answer for each. The check that does catch
it is the initial *slope*, $f'(0^+) = \lim_{s\to\infty} s\left(sF(s) - f(0)\right)$,
which is $-4$ for the correct transform and $-8$ for the wrong one. The real signal
leaves the origin at $-4$ per second, because that is the envelope's rate and the
cosine is momentarily flat.

## Where a circuit's damping comes from

Series RLC, $R = 100\ \Omega$, $L = 50$ mH, $C = 0.5$ µF, output across the capacitor.
Divider rule with the $s$-domain impedances:

```text
H(s) = (1/(sC)) / ( R + sL + 1/(sC) )

multiply top and bottom by sC:

H(s) = 1 / ( 1 + sRC + s^2 LC )
     = (1/(LC)) / ( s^2 + (R/L)s + 1/(LC) )

1/(LC) = 1 / (50e-3 * 0.5e-6) = 1 / 2.5e-8 = 4.0e7
R/L    = 100 / 50e-3                       = 2000

H(s) = 4.0e7 / ( s^2 + 2000 s + 4.0e7 )

complete the square:
    s^2 + 2000 s + 4.0e7 = (s + 1000)^2 + (4.0e7 - 1.0e6)
                         = (s + 1000)^2 + 3.9e7
    sqrt(3.9e7) = 6245.0

poles at   s = -1000 +/- j 6245.0
```

Read that as a shift. With no resistor the denominator would be $s^2 + 4.0\times10^7$,
poles at $\pm j\,6324.6$, and the circuit would ring at 6324.6 rad/s forever. The
resistor's contribution is $R/L = 2000$, and completing the square splits it in half:
$\alpha = R/(2L) = 1000$ becomes the leftward shift, and what it takes out of the
constant term drags the ringing frequency down from 6324.6 to 6245.0 rad/s — a drop of
1.26%. The pole magnitude is unchanged, $\sqrt{1000^2 + 6245^2} = 6324.6$: adding
damping swings the pole pair round a circle rather than moving it outward.

## The other rule in the family: multiplying by $t$

Differentiating the defining integral with respect to $s$ brings a factor of $-t$ down
from the exponent:

$$\frac{dF}{ds} = \int_0^\infty f(t)\,(-t)e^{-st}\,dt = -\mathcal{L}\{t f(t)\}$$

so $\mathcal{L}\{t f(t)\} = -dF/ds$. Applied to $e^{-at}$, whose transform is
$1/(s+a)$, it gives $-\frac{d}{ds}(s+a)^{-1} = (s+a)^{-2}$. That is where a repeated
pole comes from and what it means: $1/(s+a)^2$ and $t e^{-at}$ are the same object seen
from the two sides, and the factor of $t$ is why a critically damped response takes
longer to settle than its exponent alone suggests.

## Stretching: the scaling rule

Now change the *speed* of a signal instead of its size. Substituting $\lambda = t/a$,
with $a > 0$:

$$\mathcal{L}\{f(t/a)\} = \int_0^\infty f(t/a)e^{-st}dt
 = \int_0^\infty f(\lambda)e^{-sa\lambda}\,a\,d\lambda = a\,F(as)$$

Slowing a signal down by a factor $a$ compresses its transform toward the origin by the
same factor, and multiplies it by $a$ to keep the area right.

The consequence for circuits is larger than the algebra suggests. A first-order
low-pass has

$$H(s) = \frac{1}{1 + s\tau}$$

and $\tau$ appears only ever multiplied by $s$. So $H$ is not a family of functions
indexed by $\tau$ — it is one function of the single combination $s\tau$. Its step
response is $1 - e^{-t/\tau}$: one curve, plotted against $t/\tau$, valid for every RC
and every RL low-pass ever built. There is no second shape to learn. $\tau$ decides
only how far that one curve is stretched along the time axis.

### Worked: designing once, then denormalising

This is why filter tables are printed with a corner at 1 rad/s. Design the shape once,
then scale it to where you need it.

```text
wanted: a first-order low-pass rolling off at 4.50 kHz

tau = 1 / (2 pi f_c) = 1 / (2 * pi * 4500) = 3.5368e-5 s = 35.368 us

pick the capacitor first, since capacitors come in fewer values:
    C = 2.2 nF
    R = tau / C = 3.5368e-5 / 2.2e-9 = 16076 ohm

nearest standard value: 16 kohm
    tau  = 16e3 * 2.2e-9 = 3.520e-5 s
    f_c  = 1 / (2 pi * 3.520e-5) = 4522 Hz     0.5% high
```

And because only the product matters, $(16\ \mathrm{k}\Omega,\ 2.2\ \mathrm{nF})$,
$(160\ \mathrm{k}\Omega,\ 220\ \mathrm{pF})$ and
$(1.6\ \mathrm{k}\Omega,\ 22\ \mathrm{nF})$ all give the same response curve, to the
last decimal place. What separates them is not the transfer function at all — it is
impedance level: how much current the source is asked to supply, how much the stray
capacitance of the board matters, and how much Johnson noise the resistor makes.
Scaling says the transfer function cannot choose between them, so something outside the
transfer function has to.

## Where these stop

Scaling has exactly one knob because a first-order system has exactly one parameter.
A second-order system has two, $\omega_n$ and $\zeta$, and scaling stretches only the
first. So there is a whole one-parameter family of *shapes*, indexed by $\zeta$, each of
which can then be stretched to any speed. That is why module 5 talks about overshoot as
a function of $\zeta$ alone: overshoot is precisely the part of the answer that scaling
cannot touch, and $\omega_n$ is precisely the part it can.

The frequency-shift rule stops being *damping* the moment $a$ stops being real. The
algebra is untouched — $\mathcal{L}\{e^{j\omega_0 t}f(t)\} = F(s - j\omega_0)$ — but now
the poles slide sideways rather than left, and a signal that decayed still decays at
the same rate while acquiring a carrier. Sideways is modulation, not damping: it is
what a mixer does to a spectrum, and it is how a low-pass prototype is turned into a
band-pass centred on $\omega_0$. Same substitution, different direction, and none of
the intuition about envelopes survives the change.
''',
                },
            ],
            "blanks": [
                {
                    "title": "Waveforms assembled out of steps",
                    "minutes": 9,
                    "caption": "u(.) is the unit step; every waveform here is zero before t = 0",
                    "lang": "text",
                    "brief": r'''
Any waveform made of flat sections and vertical edges is a sum of steps, and nothing
else. Find the steps — where each one starts and how tall it is — and the transform
falls out of a table entry plus one delay factor each.

The two ramps at the bottom are the pair worth slowing down for. They are both "the
ramp, delayed", in English, and they are not the same signal.
''',
                    "listing": """WRITE IT AS STEPS FIRST, THEN TRANSFORM ONE STEP AT A TIME

  1  a pulse: 1 V from t = 0 to t = T, nothing after

         f(t) = u(t) - u(t - T)
         F(s) = ___

  2  a step that arrives late: nothing until t = 2T, then 3 V and stays

         f(t) = 3 u(t - 2T)
         F(s) = ___

  3  a staircase: 2 V from 0 to T, then 5 V from T onwards

         f(t) = 2 u(t) + ___ u(t - T)
         F(s) = (2 + 3 e^(-sT)) / s

  4  a ramp that starts late: flat zero until T, then climbs at 1 V/s

         f(t) = (t - T) u(t - T)
         F(s) = ___

  5  the same ramp WITHOUT the shift: already T volts high when it switches on

         f(t) = t u(t - T)
         F(s) = e^(-sT) ( 1/s^2 + ___ )
""",
                    "blanks": [
                        {
                            "prompt": "The transform of a pulse of height 1 and width T.",
                            "hole": "?",
                            "opts": ["(1 - e^(-sT)) / s", "(1 + e^(-sT)) / s", "e^(-sT) / s", "(1 - e^(-sT)) / s^2"],
                            "a": 0,
                            "why": "Transform the two steps separately — $1/s$ and $e^{-sT}/s$ — and subtract, leaving a common $1/s$ outside. The minus sign is the falling edge, and dropping it is the same error as forgetting the pulse ever ends.",
                            "whys": [
                                "Transform the two steps separately — $1/s$ and $e^{-sT}/s$ — and subtract, leaving a common $1/s$ outside. The minus sign is the falling edge, and dropping it is the same error as forgetting the pulse ever ends.",
                                "A plus sign describes a waveform that steps up at $t=0$ and steps up *again* at $t=T$, ending at 2 V forever. The final value theorem separates the two in one line: $\\lim_{s\\to0} sF(s)$ is 0 for the pulse and 2 for this.",
                                "$e^{-sT}/s$ on its own is the falling edge with the rising edge missing — a step that begins at $T$, not a pulse that ends there.",
                                "The extra $s$ underneath integrates the pulse into a ramp-and-hold. Check it at $s \\to 0$: this expression blows up, and a pulse has a perfectly finite area of $T$.",
                            ],
                        },
                        {
                            "prompt": "The transform of a 3 V step that begins at t = 2T.",
                            "hole": "?",
                            "opts": ["3 e^(-2sT) / s", "3 e^(-sT) / s", "3 e^(-2sT)", "3 / (s + 2T)"],
                            "a": 0,
                            "why": "Height scales the transform by 3 because the transform is linear; the delay of $2T$ multiplies it by $e^{-as}$ with $a = 2T$. The delay lives entirely in the exponent and never touches the $1/s$.",
                            "whys": [
                                "Height scales the transform by 3 because the transform is linear; the delay of $2T$ multiplies it by $e^{-as}$ with $a = 2T$. The delay lives entirely in the exponent and never touches the $1/s$.",
                                "That is a delay of $T$, not $2T$. The whole delay goes into the exponent, so doubling the wait doubles the exponent rather than squaring or halving anything.",
                                "Without the $1/s$ this is $3\\delta(t-2T)$, an impulse of area 3 at $t = 2T$ — the *derivative* of the step wanted, not the step.",
                                "A time cannot be added to $s$: $s$ has units of 1/second, so $s + 2T$ adds seconds to reciprocal seconds. Delays appear in exponents, never in denominators.",
                            ],
                        },
                        {
                            "prompt": "The height of the second step in the staircase.",
                            "hole": "?",
                            "opts": ["3", "5", "2", "-3"],
                            "a": 0,
                            "why": "The steps are cumulative, so the second one carries the *change* in level, not the new level: from 2 V to 5 V is a step of 3. Check just after $T$: $2 + 3 = 5$ V, as drawn.",
                            "whys": [
                                "The steps are cumulative, so the second one carries the *change* in level, not the new level: from 2 V to 5 V is a step of 3. Check just after $T$: $2 + 3 = 5$ V, as drawn.",
                                "5 is the level reached, not the step taken. The first step has not gone anywhere — it is still holding 2 V — so adding 5 to it gives 7 V after $T$.",
                                "2 would put the waveform at 4 V after $T$. It is the height of the first step, reused; the second edge is a different size.",
                                "A negative step takes the waveform down to $-1$ V. The staircase climbs, so the sign is wrong before the size is.",
                            ],
                        },
                        {
                            "prompt": "The transform of a ramp that begins climbing from zero at t = T.",
                            "hole": "?",
                            "opts": ["e^(-sT) / s^2", "e^(-sT) / s", "1/s^2 - T/s", "(1 - e^(-sT)) / s^2"],
                            "a": 0,
                            "why": "This one is the delay rule applied cleanly: the signal is $f(t-T)u(t-T)$ with $f(t) = t$ and $F(s) = 1/s^2$, so it picks up $e^{-sT}$ and nothing else changes. It is the ramp itself, moved — no piece has been cut off the front.",
                            "whys": [
                                "This one is the delay rule applied cleanly: the signal is $f(t-T)u(t-T)$ with $f(t) = t$ and $F(s) = 1/s^2$, so it picks up $e^{-sT}$ and nothing else changes. It is the ramp itself, moved — no piece has been cut off the front.",
                                "$e^{-sT}/s$ is a delayed *step*, which is flat after it arrives. A ramp keeps climbing, and the second power underneath is what says so.",
                                "This has no delay factor in it at all, so whatever it describes starts at $t = 0$. Subtracting $T/s$ shifts a ramp *down* by a constant rather than shifting it late, which makes it negative for $t < T$ — and the one-sided transform cannot represent that anyway.",
                                "The bracket says two things are happening, one at $t=0$ and one at $t=T$. Here nothing at all happens at the origin.",
                            ],
                        },
                        {
                            "prompt": "The extra term needed for the ramp that is already T volts high when it switches on.",
                            "hole": "?",
                            "opts": ["T/s", "T/s^2", "T", "1/(sT)"],
                            "a": 0,
                            "why": "Write $t = (t-T) + T$, so $t\\,u(t-T) = (t-T)u(t-T) + T\\,u(t-T)$: a clean delayed ramp *plus a step of height $T$*. The step contributes $T/s$, and the shared $e^{-sT}$ has already been taken outside. That extra step is the vertical jump this waveform has and the previous one does not.",
                            "whys": [
                                "Write $t = (t-T) + T$, so $t\\,u(t-T) = (t-T)u(t-T) + T\\,u(t-T)$: a clean delayed ramp *plus a step of height $T$*. The step contributes $T/s$, and the shared $e^{-sT}$ has already been taken outside. That extra step is the vertical jump this waveform has and the previous one does not.",
                                "$T/s^2$ would be a second ramp, climbing at $T$ volts per second on top of the first. The jump at $t = T$ is instantaneous, and an instantaneous change of level is a step.",
                                "A bare $T$ is an impulse of area $T$ — infinitely tall and infinitely brief. The waveform does jump, but it jumps to a finite height and stays there.",
                                "Dividing by $T$ rather than multiplying makes the correction *shrink* as the switch-on is pushed later. The later it switches on, the further up the ramp it starts, so the correction has to grow.",
                            ],
                        },
                    ],
                },
                {
                    "title": "A pulse through an RC, line by line",
                    "minutes": 10,
                    "caption": "2.2 kΩ and 100 nF, output across the capacitor, driven by a 5 V pulse 400 µs wide",
                    "lang": "text",
                    "brief": r'''
The reading unit worked this calculation with a 10 kΩ resistor and a 22 nF capacitor.
The parts below are different — 2.2 kΩ and 100 nF — and every number in the answer is
the same, because the product is the same. That is the scaling rule doing its work in
public, and it is worth noticing before you start filling anything in.

Fill the holes in the order they appear. Each one only needs the line above it.
''',
                    "listing": """R = 2.2 k, C = 100 n, output across C, circuit at rest at t = 0.
input: 5 V from t = 0 to t = 400 us, then 0 V.

  1  the circuit

         H(s) = 1 / (1 + s R C)
         tau  = R C = 2.2e3 * 100e-9 = ___

  2  the input, as two steps

         vin(t) = 5 u(t) - 5 u(t - 400us)
         Vin(s) = ___

  3  the output transform

         Vout(s) = H(s) Vin(s)

                             5                            5
                   = ----------------  -  e^(-sT) ----------------
                      s (1 + s tau)                s (1 + s tau)

  4  invert the first term with the standard pair

         5 / (s (1 + s tau))              ->  5 (1 - e^(-t/tau))      t >= 0

  5  invert the second: the same function of time, delayed and gated

         e^(-sT) * 5 / (s (1 + s tau))    ->  ___                     t >= 400us

  6  subtract, for t >= 400 us, and watch the constants cancel

         v(t) = 5 ( ___ )

  7  and two values off that

         v(400us) = 5 (1 - 0.16232)         = ___
         v(500us) = 5 (0.63474 - 0.10303)   = 2.659 V
""",
                    "blanks": [
                        {
                            "prompt": "The time constant.",
                            "hole": "?",
                            "opts": ["220 us", "22 us", "2.2 ms", "220 ms"],
                            "a": 0,
                            "why": "$2.2\\times10^{3} \\times 100\\times10^{-9} = 2.2\\times10^{-4}$ s. Group the powers of ten before the digits: $10^3 \\times 10^{-9} = 10^{-6}$, and $2.2 \\times 100 = 220$, so $220\\times10^{-6}$ s. The pulse is 400 µs, so $T/\\tau = 1.82$ — the capacitor gets most of the way up and no further.",
                            "whys": [
                                "$2.2\\times10^{3} \\times 100\\times10^{-9} = 2.2\\times10^{-4}$ s. Group the powers of ten before the digits: $10^3 \\times 10^{-9} = 10^{-6}$, and $2.2 \\times 100 = 220$, so $220\\times10^{-6}$ s. The pulse is 400 µs, so $T/\\tau = 1.82$ — the capacitor gets most of the way up and no further.",
                                "22 µs is a factor of ten short, which is the usual result of counting the nano prefix as $10^{-8}$. It would make the pulse eighteen time constants long and the output an almost perfect copy of the input.",
                                "2.2 ms is a factor of ten too large — the digits of the resistor kept, the exponent of the capacitor mislaid. It would make the pulse a fifth of a time constant and the output a barely visible 0.9 V bump.",
                                "220 ms is a thousand times too long. A quick order-of-magnitude guard: kilohms times nanofarads always land in microseconds, whatever the digits are.",
                            ],
                        },
                        {
                            "prompt": "The transform of the input pulse.",
                            "hole": "?",
                            "opts": [
                                "5 (1 - e^(-400us s)) / s",
                                "5 (1 + e^(-400us s)) / s",
                                "5 e^(-400us s) / s",
                                "5 / (s (1 + 400us s))",
                            ],
                            "a": 0,
                            "why": "Two steps of height 5, the second delayed by 400 µs and subtracted. Each transforms to $5/s$, and the delayed one carries $e^{-sT}$ with $T = 400$ µs.",
                            "whys": [
                                "Two steps of height 5, the second delayed by 400 µs and subtracted. Each transforms to $5/s$, and the delayed one carries $e^{-sT}$ with $T = 400$ µs.",
                                "Adding rather than subtracting describes an input that steps up twice and finishes at 10 V. The area check settles it: a pulse has area $5 \\times 400\\ \\mu\\mathrm{s} = 2$ mV·s, and this expression has none of that — its $s \\to 0$ limit is infinite.",
                                "One exponential and no 1 is the falling edge on its own, with no rising edge to precede it: a step that starts 400 µs late and stays up.",
                                "This is the *circuit's* denominator wearing the pulse width instead of the time constant. The input knows nothing about $R$ and $C$; keeping the two fractions separate is what makes the method work.",
                            ],
                        },
                        {
                            "prompt": "The inverse of the delayed term.",
                            "hole": "?",
                            "opts": [
                                "5 (1 - e^(-(t - 400us)/tau))",
                                "5 (1 - e^(-t/tau)) e^(-400us/tau)",
                                "5 e^(-(t - 400us)/tau)",
                                "5 (1 - e^(-t/tau - 400us))",
                            ],
                            "a": 0,
                            "why": "The delay factor $e^{-sT}$ does one thing and one thing only: it takes the time function the rest of the term inverts to and starts it $T$ later. So the same charging curve appears again, with its clock reset to $t = 400$ µs, and gated off before then.",
                            "whys": [
                                "The delay factor $e^{-sT}$ does one thing and one thing only: it takes the time function the rest of the term inverts to and starts it $T$ later. So the same charging curve appears again, with its clock reset to $t = 400$ µs, and gated off before then.",
                                "This treats $e^{-sT}$ as a constant multiplier, which is what would happen if the factor were $e^{-aT}$ with no $s$ in it. A factor containing $s$ acts on *when*, not on *how much*.",
                                "Dropping the 1 turns a delayed charging curve into a delayed decay. The two terms of this problem are identical in form; only their start times differ.",
                                "Subtracting 400 µs inside the exponent alongside $t/\\tau$ mixes a pure time with a dimensionless ratio. Whatever is shifted has to be shifted before the division by $\\tau$, not after.",
                            ],
                        },
                        {
                            "prompt": "What is left inside the bracket once the two terms are subtracted.",
                            "hole": "?",
                            "opts": [
                                "e^(-(t - 400us)/tau) - e^(-t/tau)",
                                "1 - e^(-(t - 400us)/tau)",
                                "e^(-t/tau) - e^(-(t - 400us)/tau)",
                                "2 - e^(-t/tau) - e^(-(t - 400us)/tau)",
                            ],
                            "a": 0,
                            "why": "$(1 - e^{-t/\\tau}) - (1 - e^{-(t-T)/\\tau})$: the two 1s cancel and the second exponential changes sign. What survives has no constant term, which is the algebra saying that once the pulse is over the output decays to zero rather than settling anywhere.",
                            "whys": [
                                "$(1 - e^{-t/\\tau}) - (1 - e^{-(t-T)/\\tau})$: the two 1s cancel and the second exponential changes sign. What survives has no constant term, which is the algebra saying that once the pulse is over the output decays to zero rather than settling anywhere.",
                                "Keeping a 1 leaves the output heading for 5 V long after the input has gone away. A passive RC with a dead source cannot hold a voltage.",
                                "The order is reversed, so every value comes out negative. Sanity check at $t$ just past 400 µs: the two exponents are nearly $T/\\tau$ and 0, so the term with the *smaller* exponent — the delayed one — is the larger, and it must come first.",
                                "Two 1s were added rather than cancelled. At $t$ far beyond the pulse both exponentials vanish and this leaves 2, so the output would settle at 10 V from a 5 V pulse.",
                            ],
                        },
                        {
                            "prompt": "The output at the instant the pulse ends.",
                            "hole": "?",
                            "opts": ["4.188 V", "5.000 V", "3.161 V", "0.812 V"],
                            "a": 0,
                            "why": "$5 \\times (1 - 0.16232) = 5 \\times 0.83768 = 4.1884$ V. The pulse lasted $400/220 = 1.82$ time constants, which covers 83.8% of the gap to 5 V — so the flat top of the input comes out as a curve that never quite arrives, and this is the peak of the whole response.",
                            "whys": [
                                "$5 \\times (1 - 0.16232) = 5 \\times 0.83768 = 4.1884$ V. The pulse lasted $400/220 = 1.82$ time constants, which covers 83.8% of the gap to 5 V — so the flat top of the input comes out as a curve that never quite arrives, and this is the peak of the whole response.",
                                "5.000 V is what an infinitely long pulse would reach. This one stops at 1.82 time constants, and the remaining 16.2% of the gap is exactly the $e^{-1.81818}$ term.",
                                "3.161 V is $5(1 - e^{-1})$, the value after *one* time constant. The pulse is 1.82 of them long, so the capacitor gets further than that.",
                                "0.812 V is $5 \\times 0.16232$ — the exponential itself rather than what is left after subtracting it from 1. It is the size of the shortfall, not the output.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "How far a cable pushes the phase",
                    "minutes": 4,
                    "brief": r'''
The mechanical one. A pure delay has no poles, no zeros and no attenuation, so there is
only one thing left for it to do to a sinusoid, and one line of arithmetic that says how
much of it.

Work in degrees throughout if you like — the conversion from radians is the only place
a factor of $2\pi$ can go missing.
''',
                    "prompt": "By how many degrees does the far end of the cable lag the near end at 25.0 kHz?",
                    "note": "A lag, so report the size of it as a positive number of degrees.",
                    "figure": r'''
A length of coaxial cable, short enough that its loss is negligible at these
frequencies. Whatever goes in at the near end comes out at the far end **4.20 µs
later**, at the same amplitude and otherwise unaltered. Its transfer function is
therefore $H(s) = e^{-sT}$ with $T = 4.20\ \mu$s, and nothing else.
''',
                    "given": [
                        {"label": "Delay T", "value": "4.20 µs"},
                        {"label": "Frequency", "value": "25.0 kHz"},
                        {"label": "Amplitude", "value": "unchanged — a pure delay attenuates nothing"},
                    ],
                    "aside": "At $s = j\\omega$ the transfer function is $e^{-j\\omega T}$, whose magnitude is 1 "
                             "and whose angle is $-\\omega T$ radians.",
                    "answer": 37.8,
                    "tol": 0.2,
                    "unit": "°",
                    "hint": "How many cycles of a 25.0 kHz sinusoid fit into 4.20 µs? Multiply that fraction "
                            "of a cycle by 360.",
                    "wrong": "If you got 0.660, the answer is still in radians — 0.6597 rad — and needs "
                             "$\\times 180/\\pi$. If you got 0.105, that is the delay expressed in cycles, "
                             "which is the right idea one step short of the finish.",
                    "why": r'''
```
in radians:
    w   = 2 pi f = 2 pi * 25.0e3      = 1.5708e5 rad/s
    w T = 1.5708e5 * 4.20e-6          = 0.65973 rad
    in degrees: 0.65973 * 180 / pi    = 37.8 deg

or without ever leaving degrees:
    360 * f * T = 360 * 25.0e3 * 4.20e-6 = 360 * 0.105 = 37.8 deg
```
The second line is the one to remember, because it says what is really going on: the
delay is 0.105 of a cycle at this frequency, and 0.105 of a turn is 37.8°.

Now push the frequency and watch the trouble arrive. The lag is proportional to
frequency with nothing to hold it back, so at $f = 1/(2T) = 119$ kHz it is exactly
180° — the cable inverts — and at 238 kHz it is a full 360° and the output is back in
step with the input while being a whole cycle behind it. A pole can never do this: its
phase saturates at 90°, and it pays for what phase it does contribute with roll-off. A
delay contributes unbounded phase at unit gain, which is precisely why dead time in a
feedback loop is so much worse than a slow pole.
''',
                },
                {
                    "title": "Same shape, three and a half times as fast",
                    "minutes": 6,
                    "brief": r'''
The scaling rule says a first-order low-pass has exactly one response shape, and that
$\tau$ decides only how far it is stretched along the time axis. So "make it faster
without changing anything else" is a well-posed instruction with a single-number
answer.

Read the two values off the schematic. The capacitor is being kept; only the resistor
moves.
''',
                    "prompt": "The copy must have the same response shape with the time axis compressed by 3.50, using the same capacitor. What resistance does it need?",
                    "note": "Answer in kilohms, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 22000},
                            {"id": "c", "kind": "C", "x": 11, "y": 6, "rot": 1, "value": 4.7e-9},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [11, 3], "b": [15, 3]},
                        ],
                    },
                    "given": [
                        {"label": "R, as drawn", "value": "22.0 kΩ"},
                        {"label": "C, as drawn and kept", "value": "4.70 nF"},
                        {"label": "Required", "value": "the same curve, 3.50× faster"},
                    ],
                    "aside": "Only the product $RC$ appears in $H(s) = 1/(1+sRC)$, so it is the only thing a "
                             "specification about speed can constrain — and with $C$ pinned there is exactly "
                             "one resistor that satisfies it.",
                    # Measured rather than restated: the corner is found by bisecting the swept
                    # response of the drawn circuit, turned into a time constant, and divided by
                    # 3.50 and the drawn capacitor. Change either part on the schematic and the
                    # number this returns moves with it.
                    "check": r'''
const f0 = c.corner(1, 1e7);            /* the drawn filter's -3 dB point, swept and bisected */
const tau = 1 / (2 * Math.PI * f0);     /* which is its time constant */
const C = c.values('C')[0];             /* the capacitor, which the copy keeps */
return tau / (3.5 * C) / 1000;          /* kilohms for the faster copy */
''',
                    "answer": 6.286,
                    "tol": 0.05,
                    "unit": "kΩ",
                    "hint": "Work out $\\tau = RC$ for the circuit as drawn, divide it by 3.50, then divide "
                            "that by the same capacitor.",
                    "wrong": "If you got 77.0 kΩ the factor went the wrong way — multiplying $\\tau$ by 3.50 "
                             "makes the filter slower, not faster. If you got 6286 you answered in ohms; the "
                             "note asks for kilohms.",
                    "why": r'''
```
as drawn:
    tau = R C = 22.0e3 * 4.70e-9 = 1.034e-4 s = 103.4 us
    f_c = 1 / (2 pi tau)         = 1539 Hz

"the same curve, 3.50x faster" compresses the time axis by 3.50:
    tau_new = 103.4 us / 3.50    = 29.543 us

C is kept, so
    R_new = tau_new / C = 2.9543e-5 / 4.70e-9 = 6286 ohm = 6.29 kohm

the short road, and a check on the long one:
    R_new = R / 3.50 = 22.0e3 / 3.50 = 6286 ohm
    f_c,new = 1539 * 3.50 = 5387 Hz
```
The resistor divides by exactly the factor the time axis was compressed by, because
$\tau$ is linear in $R$ — that is the whole of it. What is worth noticing is the
question the scaling rule refuses to answer. Nothing here said *which* member of the
family to build: the same $\tau$ comes out of a tenth of this resistance with ten times
the capacitance, and the two circuits have transfer functions that are identical
expression for expression — and a transfer function is all the specification gave you.
The choice between them is made on grounds
the transfer function cannot see — how much current the source must supply, how much
stray capacitance matters, how much noise the resistor makes.
''',
                },
                {
                    "title": "A pulse that ends before the capacitor is full",
                    "minutes": 8,
                    "brief": r'''
Now both terms of the delay rule earn their keep. The input is a pulse, so the output
transform has two pieces: the ordinary charging response, and the same response again,
delayed by the pulse width and subtracted.

Before the falling edge the second piece has not switched on and the circuit is doing
nothing unusual. The question is about a moment after it, when both are live.
''',
                    "prompt": "What is the probe voltage at t = 250 µs?",
                    "note": "The pulse is over by then. Work out the time constant first, then the height the output had reached when the pulse ended.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 4},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 15000},
                            {"id": "c", "kind": "C", "x": 11, "y": 6, "rot": 1, "value": 6.8e-9},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [11, 3], "b": [15, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "4.00 V from t = 0 to t = 150 µs, then 0 V"},
                        {"label": "R", "value": "15.0 kΩ"},
                        {"label": "C", "value": "6.80 nF"},
                        {"label": "Output", "value": "across the capacitor, circuit at rest at t = 0"},
                    ],
                    "aside": "The schematic draws the pulse's amplitude as an ordinary source, because the "
                             "amplitude is the only thing about it the solver needs: the response to "
                             "$u(t) - u(t-T)$ is the step response minus the same step response delayed by $T$, "
                             "which is the rule this module is about.",
                    # Superposition, measured: one transient run gives the step response of this
                    # schematic, and the pulse response is that curve minus itself delayed by the
                    # pulse width. Both readings come off the same run, so the integrator's error
                    # largely cancels between them.
                    "check": r'''
const T = 150e-6, tq = 250e-6;
const run = c.step(tq);                  /* the step response of this very circuit */
const h = run.t[1] - run.t[0];
const k = Math.round((tq - T) / h);      /* the sample at t = tq - T */
return run.v[run.v.length - 1] - run.v[k];
''',
                    "answer": 1.156,
                    "tol": 0.01,
                    "unit": "V",
                    "hint": "For $t \\ge T$ the two terms give $v(t) = 4\\left(e^{-(t-T)/\\tau} - e^{-t/\\tau}\\right)$. "
                            "Both exponents, and both exponentials, before you subtract anything.",
                    "wrong": "If you got 3.66 V you used the charging formula alone and ignored the falling "
                             "edge — that is the voltage the capacitor would have reached had the pulse never "
                             "stopped. If you got −1.156 V the two exponents were swapped: at $t = 250$ µs the "
                             "delayed term is the *larger* of the two, because its clock started later, so it "
                             "is the one that comes first.",
                    "why": r'''
```
tau = 15.0e3 * 6.80e-9 = 1.020e-4 s = 102 us

while the pulse is on (0 <= t < 150 us):
    v(t) = 4 (1 - e^(-t/tau))
    at the falling edge, t/tau = 150/102 = 1.47059,  e^- = 0.22979
    v(150us) = 4 (1 - 0.22979) = 4 * 0.77021 = 3.081 V

after it (t >= 150 us), the two shifted steps combine:
    v(t) = 4 ( e^(-(t-T)/tau) - e^(-t/tau) )

at t = 250 us:
    (t-T)/tau = 100/102 = 0.98039     e^(-0.98039) = 0.375164
    t/tau     = 250/102 = 2.45098     e^(-2.45098) = 0.086209
    v = 4 (0.375164 - 0.086209) = 4 * 0.288955 = 1.156 V
```
A second route, worth doing because it is a genuine check and not a restatement. Once
the source is gone the circuit is a charged capacitor emptying into a resistor, so it
simply decays from 3.081 V with the same 102 µs constant:

```
v = 3.081 * e^(-100/102) = 3.081 * 0.375164 = 1.156 V
```

Both roads agree, and the reason they must is the cancellation in the first one: the
two 1s went, and what was left had no constant term, which is precisely a pure decay
from wherever the pulse left it. The peak matters more than the number asked for.
$T/\tau = 1.47$, so the flat top of a 4 V pulse comes out 3.08 V high and rounded. Make
the pulse a tenth as wide, $T = 15$ µs, and the peak falls to
$4(1 - e^{-0.1471}) = 0.547$ V — at that point the filter has stopped passing the
pulse's height and started reporting its *area*.
''',
                },
                {
                    "title": "The kick a pulse leaves behind",
                    "minutes": 11,
                    "brief": r'''
The hardest of the four, and the one where the arithmetic pays for itself with something
you would not have guessed.

The probe is on the inductor this time, not the resistor, so the step response is a
decay rather than a rise: at the instant the supply appears the inductor carries no
current, so all of the supply is across it, and it hands the voltage over to the
resistor as the current builds. Then the pulse ends, and the second, inverted copy of
that response arrives on top of the first.

You are asked for a time rather than a voltage, so the last step is a logarithm.
''',
                    "prompt": "The pulse ends at t = 60.0 µs and the probe is driven sharply negative. How long after that does it come back up to −1.00 V?",
                    "note": "Measure from the falling edge, not from t = 0. Answer in microseconds.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 6},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 470},
                            {"id": "l", "kind": "L", "x": 11, "y": 6, "rot": 1, "value": 0.022},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 9]},
                            {"a": [11, 3], "b": [15, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "6.00 V from t = 0 to t = 60.0 µs, then 0 V"},
                        {"label": "R", "value": "470 Ω"},
                        {"label": "L", "value": "22.0 mH"},
                        {"label": "Output", "value": "across the inductor, circuit at rest at t = 0"},
                    ],
                    "aside": "$\\tau = L/R$ for an RL circuit, not $LR$. The step response measured across the "
                             "inductor is $V e^{-t/\\tau}$; across the resistor it would be $V(1 - e^{-t/\\tau})$, "
                             "and the two add to $V$ at every instant because they are the two halves of one "
                             "divider.",
                    # One transient run gives the step response; the pulse response is that curve
                    # minus itself delayed by the pulse width, and the crossing is found by scanning
                    # for the sign change and interpolating between the two samples that bracket it.
                    # The sample at the delayed index is never the run's own t = 0 entry, which
                    # carries the pre-switch value rather than the post-switch one.
                    "check": r'''
const T = 60e-6, level = -1.0;
const run = c.step(150e-6);              /* the step response of this schematic */
const h = run.t[1] - run.t[0];
const k = Math.round(T / h);             /* how many samples the falling edge is worth */
const pulse = function (i) { return run.v[i] - run.v[i - k]; };
for (let i = k + 2; i < run.t.length; i++) {
  const a = pulse(i - 1), b = pulse(i);
  if (a < level && b >= level) {
    const t = run.t[i - 1] + (level - a) / (b - a) * h;
    return (t - T) * 1e6;                /* microseconds after the falling edge */
  }
}
throw new Error('the probe never came back up to -1.00 V');
''',
                    "answer": 68.65,
                    "tol": 0.3,
                    "unit": "µs",
                    "hint": "Find the probe voltage the instant after the edge first: it is the step response "
                            "at $t = T$ minus the full 6 V that the second, delayed step subtracts. Then it is "
                            "a plain decay from there.",
                    "wrong": "If you got 83.9 µs you decayed from −6 V instead of from −4.33 V — the inductor "
                             "had already given up most of its voltage by the time the pulse ended, so the kick "
                             "is smaller than the supply. If you got 128.7 µs the answer is measured from "
                             "$t = 0$; the question asks how long after the edge. If you got 46.8 µs you "
                             "stopped after one time constant, which leaves the probe at "
                             "$-4.335/e = -1.59$ V rather than at $-1.00$ V.",
                    "why": r'''
```
tau = L / R = 22.0e-3 / 470 = 4.6809e-5 s = 46.81 us

step response, measured across the inductor:
    s(t) = 6 e^(-t/tau)

the pulse is a step up and a step down 60 us later, so for t >= 60 us
    v(t) = 6 e^(-t/tau)  -  6 e^(-(t - 60us)/tau)

at the falling edge itself, t = 60 us:
    T/tau = 60/46.81 = 1.28182       e^(-1.28182) = 0.27753
    v = 6 (0.27753 - 1) = -4.335 V

collect the two terms into one decay, writing u = t - 60us:
    v = 6 e^(-u/tau) ( e^(-T/tau) - 1 ) = -4.335 e^(-u/tau)

set that to -1.00 V:
    e^(-u/tau) = 1.00 / 4.335 = 0.23068
    u = tau * ln(4.335) = 46.809 us * 1.46667 = 68.65 us
```
Read the third line again. The probe sits 4.34 V **below ground**, out of a circuit
whose only supply is +6 V and which contains no source of negative voltage at all. The
inductor is holding the current it had built up, and the only path for that current is
back through the resistor to the now-zero source, which puts the resistor's drop on the
wrong side of the probe. This is the inductive kick that destroys switches, in miniature
and slowed down enough to measure. Make the pulse longer and it gets worse: at
$T = 200$ µs the current is nearly fully established, $e^{-T/\tau}$ is 0.0139, and the
kick is $-5.92$ V, almost the full supply — inverted.

The other thing worth extracting is why the answer is a logarithm at all. The two terms
of the delay rule combined into a single exponential with a *coefficient* set by the
pulse width, $-6(1 - e^{-T/\tau})$, and a *rate* that has nothing to do with the pulse
width at all. Pulse width sets how far the kick goes; the circuit alone sets how fast it
comes back.
''',
                },
            ],
            "tune": {
                "title": "One time constant, more than one pair of parts",
                "minutes": 8,
                "brief": r'''
The scaling rule says a first-order response has exactly one shape. Stretch the time
axis and you have every RC low-pass that has ever been built; there is no second
family, no other curve.

So the only thing a choice of R and C decides is $\tau = RC$, and any two pairs with
the same product are, as far as the response is concerned, the same circuit. The
readout gives the corner frequency and the time constant along with what the filter
does at 100 Hz and at 10 kHz; only the time constant is being asked for here, and you
should watch the other three while you hunt for it.

Hit the time constant. Then move both sliders — one up, one down — and watch what does
and does not change.
''',
                "prompt": "Set R and C so the time constant reads 2.20 ms.",
                "note": "One constraint and two sliders, so there is a whole family of answers. Find two of them.",
                "model": "rc-lowpass",
                "initial": {"r": 1000, "c": 100},
                "constraints": [
                    {"k": "tau", "label": "time constant = 2.20 ms ± 0.03", "eq": 2.20, "tol": 0.03},
                ],
            },
            "build": {
                "title": "The same curve, out of a different pair of parts",
                "minutes": 18,
                "brief": r'''
The scaling rule says a first-order low-pass has one response shape and one number that
stretches it. Everything else about the choice of parts is invisible to the transfer
function — which means a specification written as a transfer function cannot pin the
parts down, and something outside it has to.

Here is that situation, made concrete.

## The specification

Build a first-order low-pass with

- a **time constant of 220 µs**, which puts the corner at
  $f_c = 1/(2\pi \times 220\ \mu\mathrm{s}) = 723.4$ Hz
- a **gain of 1** well below the corner, so low frequencies pass untouched
- exactly **one resistor and one capacitor**, so that it really is one pole
- and a **resistor of at least 100 kΩ**

The first three are what a filter table would give you. The fourth is the constraint
that does the work here: it is the reason there is anything to think about, because the
first three alone are satisfied by an infinite family of part pairs and this one picks
out a corner of it.

## What is on the canvas

A 1 V source, its ground, and a 2.2 kΩ resistor already wired to the source. That
resistor is a perfectly good member of the family — with 100 nF beside it the time
constant is exactly right — and it is not allowed, because it is two orders of
magnitude below the floor. Change it, and add the capacitor, a second ground and a
probe to finish an RC low-pass with the **output taken across the capacitor**.

Leave the source at 1 V: the checks read the probe voltage directly and treat it as the
gain.

## How this is measured

Nothing compares your drawing with a reference. The checks sweep whatever you built and
read four things off it — the gain far below the corner, the −3 dB point found by
bisection, the ratio of the gains one and two decades above it, and the count of parts —
plus one look at the resistor value itself, which is the one part of the specification
that is *not* a property of the response. Any pair that satisfies all of it passes, and
there are many.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 10},
                        {"id": "p2", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 2200},
                    ],
                    "wires": [
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [3, 6], "b": [3, 3]},
                        {"a": [3, 3], "b": [7, 3]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 10},
                        {"id": "p2", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 220000},
                        {"id": "p3", "kind": "C", "x": 11, "y": 6, "rot": 1, "value": 1e-9},
                        {"id": "p4", "kind": "GND", "x": 11, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 15, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [3, 6], "b": [3, 3]},
                        {"a": [3, 3], "b": [7, 3]},
                        {"a": [9, 3], "b": [11, 3]},
                        {"a": [11, 3], "b": [11, 5]},
                        {"a": [11, 7], "b": [11, 9]},
                        {"a": [11, 3], "b": [15, 3]},
                    ],
                },
                "checks": [
                    {"name": "one 1 V source drives the filter", "code": r'''
c.assert(c.count('V') === 1,
  'Use exactly one voltage source, so that "the gain" means one thing. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 1, 0.001,
  'the source amplitude — the checks read the probe voltage as the gain, so the input must be 1 V');
'''},
                    {"name": "exactly one resistor and one capacitor, so it really is one pole", "code": r'''
c.assert(c.count('R') === 1,
  'A first-order low-pass has one resistor. Found ' + c.count('R') + '.');
c.assert(c.count('C') === 1,
  'A first-order low-pass has one capacitor. Found ' + c.count('C') + '.');
c.assert(c.count('L') === 0,
  'No inductors: an inductor would add a second energy store and a second pole.');
'''},
                    {"name": "low frequencies pass through untouched", "code": r'''
c.close(c.gain(1), 1.0, 0.02,
  'the gain at 1 Hz, far below the corner — across the capacitor a passive RC hands the input straight over');
'''},
                    {"name": "the corner is at 723.4 Hz, so the time constant is 220 us", "code": r'''
const fc = c.corner(1, 1e7);
c.close(fc, 723.4322, 0.03,
  'the -3 dB point, found by bisecting the swept response; 1/(2*pi*220us) = 723.4 Hz');
'''},
                    {"name": "the roll-off is 20 dB per decade, so there is exactly one pole", "code": r'''
const a = c.gain(7234.322);
const b = c.gain(72343.22);
c.assert(b > 0, 'The response died to nothing; check the output is taken across the capacitor.');
c.close(a / b, 9.9504, 0.03,
  'the ratio of the gains one and two decades above the corner — one pole gives about 10, two would give 100');
'''},
                    {"name": "the resistor is at least 100 kohm", "code": r'''
const rs = c.values('R');
c.assert(rs.length > 0, 'There is no resistor to measure.');
const smallest = Math.min.apply(null, rs);
c.assert(smallest >= 100e3,
  'The specification puts a floor of 100 kohm on the resistor, and the smallest one here is ' +
  c.fmt(smallest, 'ohm') + '. The response cannot tell you this — only the parts list can.');
'''},
                ],
                "hints": [
                    "The layout is source, resistor, capacitor, ground, with the probe on the node between the resistor and the capacitor — the same shape as the numeric questions in this module.",
                    "$\\tau = RC = 220\\ \\mu$s with $R \\ge 100$ kΩ means $C = \\tau/R \\le 2.2$ nF. Pick the resistor first and let the capacitor follow.",
                    "220 kΩ with 1 nF is the tidiest pair: $2.2\\times10^{5} \\times 1\\times10^{-9} = 2.2\\times10^{-4}$ s. Type `220k` and `1n` into the value boxes.",
                    "It is not the only answer. 470 kΩ with 470 pF gives $\\tau = 220.9$ µs and a corner of 720.5 Hz, which is inside the 3% the check allows.",
                    "If the corner check fails but the shape checks pass, the product is wrong rather than the topology — recompute $RC$ and compare it with 220 µs before moving anything on the canvas.",
                    "If the low-frequency gain comes out near zero, the probe is across the resistor rather than the capacitor, and you have built a high-pass.",
                ],
            },
            "derive": {
                "title": "The transform of a signal that switches",
                "minutes": 13,
                "vars": ["s", "t", "T", "a", "V", "e", "omega", "F"],
                "brief": r'''
The table of pairs in module 1 covers signals that start at $t=0$ and keep going. Real
inputs do neither: they arrive late, they stop, and they are often the sum of several
that do both.

Two rules cover all of it. The **delay** rule says a shift in time is a multiplication
by $e^{-as}$; the **frequency-shift** rule says a multiplication in time by $e^{-at}$
is a shift in $s$. They look like each other on purpose, and confusing them is the
standard way to turn a low-pass into a delay line on paper.
''',
                "steps": [
                    {
                        "prompt": "The unit step has $\\mathcal{L}\\{u(t)\\} = 1/s$. A pulse of height 1 that starts at $t = 0$ and ends at $t = T$ is $u(t) - u(t-T)$. Write its transform in terms of $s$ and $T$.",
                        "given": "The delay rule is $\\mathcal{L}\\{f(t-a)u(t-a)\\} = e^{-as}F(s)$.",
                        "answer": "\\frac{1 - e^{-sT}}{s}",
                        "hint": "Transform the two steps separately. The second is the first delayed by $T$, so it picks up a factor $e^{-sT}$ and nothing else changes.",
                        "deconstruct": [
                            "$\\mathcal{L}\\{u(t)\\} = 1/s$.",
                            "$\\mathcal{L}\\{u(t-T)\\} = e^{-sT}/s$ — the same transform, multiplied by the delay factor.",
                            "Subtracting them leaves a common $1/s$ outside.",
                        ],
                    },
                    {
                        "prompt": "Now a staircase: 1 V from $0$ to $T$, then 2 V from $T$ to $2T$, then nothing at all. Write it as a sum of steps and give its transform in terms of $s$ and $T$.",
                        "answer": "\\frac{1 + e^{-sT} - 2e^{-2sT}}{s}",
                        "hint": "One step of height 1 at $t=0$, a second step of height 1 at $t=T$ to climb from 1 V to 2 V, and a step of height $-2$ at $t=2T$ to come back down to nothing.",
                        "deconstruct": [
                            "The signal is $u(t) + u(t-T) - 2u(t-2T)$. Check it just after $T$: $1+1 = 2$. Check it just after $2T$: $1+1-2 = 0$.",
                            "Each step contributes $1/s$ multiplied by its own delay factor, and a delay of $2T$ gives $e^{-2sT}$.",
                            "So the transform is $\\dfrac{1}{s} + \\dfrac{e^{-sT}}{s} - \\dfrac{2e^{-2sT}}{s}$.",
                        ],
                    },
                    {
                        "prompt": "The frequency-shift rule is $\\mathcal{L}\\{e^{-at}f(t)\\} = F(s+a)$. The transform of $\\cos\\omega t$ is $\\dfrac{s}{s^2+\\omega^2}$. Write the transform of $e^{-at}\\cos\\omega t$.",
                        "answer": "\\frac{s+a}{(s+a)^2 + \\omega^2}",
                        "hint": "Replace every $s$ by $s+a$ — the one on top as well as the ones underneath.",
                        "deconstruct": [
                            "$F(s) = \\dfrac{s}{s^2+\\omega^2}$, so $F(s+a)$ is that expression with $s+a$ written wherever $s$ stood.",
                            "The poles move from $\\pm j\\omega$ to $-a \\pm j\\omega$: the same ringing frequency, now decaying at $a$ per second.",
                        ],
                    },
                    {
                        "prompt": "Multiplying by $t$ is differentiating in $s$: $\\mathcal{L}\\{t f(t)\\} = -\\dfrac{dF}{ds}$. With $f(t) = e^{-at}$ and $F(s) = \\dfrac{1}{s+a}$, write $\\mathcal{L}\\{te^{-at}\\}$.",
                        "answer": "\\frac{1}{(s+a)^2}",
                        "hint": "$\\dfrac{d}{ds}(s+a)^{-1} = -(s+a)^{-2}$, and the rule puts a minus sign in front of that.",
                        "deconstruct": [
                            "Differentiating $1/(s+a)$ gives $-1/(s+a)^2$.",
                            "The rule negates it, so the two minus signs cancel.",
                            "This is where the repeated pole of module 2 comes from: $1/(s+a)^2$ and $te^{-at}$ are the same object seen from the two sides.",
                        ],
                    },
                    {
                        "prompt": "Back to the pulse, now of height $V$ and width $T$, whose transform is $\\dfrac{V(1 - e^{-sT})}{s}$. The area under a signal is its transform evaluated at $s = 0$. Using $e^{-sT} = 1 - sT + \\tfrac{1}{2}s^2T^2 - \\dots$, write that area.",
                        "answer": "V T",
                        "hint": "The leading term of $1 - e^{-sT}$ is $sT$, and that $s$ cancels the one underneath before you set $s = 0$.",
                        "deconstruct": [
                            "$1 - e^{-sT} = sT - \\tfrac{1}{2}s^2T^2 + \\dots$",
                            "Dividing by $s$ leaves $T - \\tfrac{1}{2}sT^2 + \\dots$, and at $s = 0$ only $T$ survives.",
                            "Multiplying by the height gives the area of a rectangle, which is what it had to be.",
                        ],
                    },
                ],
                "closing": r'''
Notice what happened to the pulse. Its transform is $(1-e^{-sT})/s$, which is not a
ratio of polynomials, so it has no poles — and a signal with no poles cannot be
produced by any finite network of R, L and C. That is not a technicality. It is the
reason a delay line is a physical length of something, why an ideal sample-and-hold
cannot be built out of passives, and why control engineers treat dead time as the
hardest thing in the loop: there is no pole to move.
''',
            },
            "quiz": {
                "title": "Four properties and what they move",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A signal $f(t)$ has transform $F(s)$. The same signal, held back so that it begins at $t = 3$ instead of $t = 0$, has transform:",
                        "opts": [
                            "$e^{-3s}F(s)$",
                            "$e^{3s}F(s)$",
                            "$F(s+3)$",
                            "$F(s)e^{-3t}$",
                        ],
                        "a": 0,
                        "why": r'''
A delay in time is a multiplication by $e^{-as}$ in $s$, with the sign that makes the
factor *shrink* as $s$ grows. The version with $e^{+3s}$ describes a signal that starts
three seconds *before* the origin, which the one-sided transform cannot represent and
whose integral does not converge. $F(s+3)$ is the frequency-shift rule and belongs to
multiplying by $e^{-3t}$ — an entirely different operation, and the one this is most
often confused with. And no transform can contain $t$: the variable has been integrated
away.
''',
                    },
                    {
                        "q": "A rectangular pulse of height 2 V, starting at $t = 0$ and lasting 5 ms, has transform:",
                        "opts": [
                            "$\\dfrac{2}{s}$",
                            "$2e^{-0.005s}$",
                            "$\\dfrac{2\\left(1 - e^{-0.005s}\\right)}{s}$",
                            "$\\dfrac{2}{s + 0.005}$",
                        ],
                        "a": 2,
                        "why": r'''
The pulse is $2u(t) - 2u(t-0.005)$: a step up, and the identical step down 5 ms later.
Transform each and subtract. A free check: the final value theorem gives
$\lim_{s\to0} sF(s) = 2(1 - e^{0}) = 0$, and a pulse does end at zero. $2/s$ on its own
is the step that never comes back down, which is the error of transforming the rising
edge and forgetting the falling one. $2/(s+0.005)$ is a decaying exponential with a
200 s time constant, nothing like a pulse.
''',
                    },
                    {
                        "q": "$\\mathcal{L}\\{\\sin 3t\\} = \\dfrac{3}{s^2+9}$. What is $\\mathcal{L}\\{e^{-4t}\\sin 3t\\}$?",
                        "opts": [
                            "$\\dfrac{3}{s^2+9} + \\dfrac{1}{s+4}$",
                            "$\\dfrac{3}{(s+4)^2+9}$",
                            "$\\dfrac{3e^{-4s}}{s^2+9}$",
                            "$\\dfrac{3}{s^2+25}$",
                        ],
                        "a": 1,
                        "why": r'''
The frequency-shift rule replaces $s$ by $s+4$ everywhere in the transform. The poles
move from $\pm j3$ to $-4 \pm j3$: the same ringing frequency, now inside a decaying
envelope, which is exactly what multiplying by $e^{-4t}$ does to the waveform.
Multiplying by $e^{-4s}$ instead would *delay* the sine rather than damp it. Adding the
two transforms would be the answer to $\sin 3t + e^{-4t}$, a sum, not a product. And
$3/(s^2+25)$ comes from adding 16 to the 9, which no rule permits — it would be a sine
at 5 rad/s with no decay at all.
''',
                    },
                    {
                        "q": "A block delays its input by $T$ and does nothing else, so its transfer function is $e^{-sT}$. What does it do to a sinusoid of frequency $\\omega$?",
                        "opts": [
                            "attenuates it by $1/(\\omega T)$",
                            "leaves the phase alone and scales the amplitude by $e^{-\\omega T}$",
                            "nothing at all, because $e^{-sT}$ has no poles",
                            "leaves the amplitude alone and subtracts $\\omega T$ from the phase",
                        ],
                        "a": 3,
                        "why": r'''
At $s = j\omega$, $\left|e^{-j\omega T}\right| = 1$ exactly and the angle is $-\omega T$:
a delay is all phase and no magnitude, and the phase falls without limit as frequency
rises. Having no poles is not the same as having no effect — it means only that the
block cannot be built from a finite number of Rs, Ls and Cs. In a feedback loop that
unbounded phase lag is usually the thing that makes the loop unstable, so it is the
opposite of harmless.
''',
                    },
                    {
                        "q": "Two RC low-pass filters: one is 1 kΩ with 1 µF, the other 10 kΩ with 0.1 µF. Their step responses:",
                        "opts": [
                            "differ by a factor of 10 in height",
                            "differ by a factor of 10 in speed",
                            "are identical",
                            "cannot be compared without knowing the source",
                        ],
                        "a": 2,
                        "why": r'''
Both have $RC = 1$ ms, and the scaling rule says the response is one universal shape
stretched by $\tau$ — so with the same $\tau$ the two curves lie on top of each other.
The height is set by the DC gain, which is 1 for any passive RC low-pass, so nothing
differs there either. What *does* differ is what the source is asked to supply: the
10 kΩ version draws a tenth of the current, which is exactly why real designs move
along this family rather than staying put.
''',
                    },
                    {
                        "q": "$\\mathcal{L}\\{t f(t)\\} = -\\dfrac{dF}{ds}$. Applying it to $f(t) = e^{-at}$, whose transform is $\\dfrac{1}{s+a}$, gives:",
                        "opts": [
                            "$\\dfrac{1}{(s+a)^2}$",
                            "$-\\dfrac{1}{(s+a)^2}$",
                            "$\\dfrac{a}{(s+a)^2}$",
                            "$\\dfrac{1}{s(s+a)}$",
                        ],
                        "a": 0,
                        "why": r'''
$\dfrac{d}{ds}(s+a)^{-1} = -(s+a)^{-2}$, and the rule carries a minus sign of its own,
so the two cancel and the result is positive. There is a sanity check that needs no
algebra: $te^{-at}$ is positive for every $t > 0$, so its transform must be positive for
large real $s$, which rules out the negative version on inspection. This pair,
$1/(s+a)^2 \leftrightarrow te^{-at}$, is the repeated pole of module 2 arriving from the
other direction. The extra factor of $a$ would break the units.
''',
                    },
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Circuits in the s-domain, with the energy already there",
            "summary": "A capacitor that starts charged and an inductor that starts carrying current are not special cases. Each becomes an impedance and a source, and after that it is divider rules again.",
            "concepts": [
                "A capacitor obeys $i = C\\,dv/dt$, so $I(s) = sCV(s) - Cv(0^-)$. Rearranged for voltage, that reads as an impedance $1/(sC)$ **in series with a step source $v(0^-)/s$** — the stored charge enters the circuit as a source, not as a correction applied afterwards.",
                "An inductor obeys $v = L\\,di/dt$, so $V(s) = sLI(s) - Li(0^-)$: an impedance $sL$ **in series with a source of $L\\,i(0^-)$**, pointing the way the current was already flowing. That constant has units of volt-seconds, which is what an s-domain voltage is, so it is not divided by $s$.",
                "Once every element is an impedance plus a source, everything from EE101 applies unchanged — series and parallel, the divider rule, node equations — and no differential equation is ever written down.",
                "The response splits into the **zero-input** part, driven by the initial energy with the input switched off, and the **zero-state** part, driven by the input with the initial energy set to zero. They add, because the circuit is linear, and both contain the same poles: initial conditions change the residues, never the pole positions.",
                "$v_C$ and $i_L$ cannot jump, because a jump would demand infinite current or infinite voltage. That is why $0^-$ is the right instant to read them at, and it is what makes the initial-condition sources well defined: everything else in the circuit may jump, and usually does.",
            ],
            "read": [
                {
                    "title": "The circuit was already doing something",
                    "minutes": 14,
                    "body": r'''
Every worked example so far in this course has started the circuit from rest: no charge
on any capacitor, no current in any inductor, everything sitting at zero until an input
arrives. That is a convenient fiction, and it is almost never the situation in front of
you.

Real switching problems look like this. A supply has been connected for minutes. Every
capacitor has settled to some voltage, every inductor is carrying some steady current,
and *then* something changes — a relay closes, a load is thrown across the output, a
regulator's input collapses. The question is what happens next, and "next" begins from
a circuit that is already holding energy.

The good news is that this needs no new theory. It needs one term in one rule you
already have, and a way of drawing that term so it stops being an afterthought.

## What a part remembers

A resistor has no memory. Put a voltage across it and a current flows; take the voltage
away and the current stops, instantly and completely. Nothing about a resistor at noon
tells you anything about it at one o'clock.

A capacitor is different, and it is worth being precise about why. What a capacitor
physically holds is charge — electrons piled onto one plate and missing from the other.
That pile cannot be moved instantly, because moving it takes current and current takes
time. The voltage across the part is the pile divided by the capacitance, $v = q/C$, so
the voltage is a running record of everything that has flowed through the part since it
was last empty. That is what memory means here, and it is the whole reason capacitors
are useful.

An inductor holds the mirror image. What it physically holds is magnetic flux, wound
through its core by the current in the winding: $\lambda = Li$. Flux cannot be changed
instantly either, because changing it induces a voltage that opposes the change, and
the size of that voltage is $v = L\,di/dt$ — which is infinite if you insist on an
instant.

Those two sentences are the reason the whole subject is tractable. Between them they
say that **$v_C$ and $i_L$ cannot jump**. Every other quantity in a switched circuit
may jump and usually does: currents through capacitors, voltages across inductors,
voltages at every resistive node. Two numbers survive the switch unchanged, and they
are the only two you need to carry across it.

## The term that was there all along

Module 1 derived the derivative rule and then, in most of the examples, threw half of
it away:

$$\mathcal{L}\{f'(t)\} = sF(s) - f(0^-)$$

The $-f(0^-)$ is where the memory lives. Apply it to a capacitor, whose defining
equation is $i = C\,dv/dt$:

$$I(s) = C\big(sV(s) - v(0^-)\big) = sC\,V(s) - C\,v(0^-)$$

Now solve that for the voltage instead, because voltage is what a schematic is drawn in
terms of:

$$V(s) = \frac{I(s)}{sC} + \frac{v(0^-)}{s}$$

Read the right-hand side as a circuit. The first term is a current flowing through an
impedance $1/(sC)$ — the ordinary capacitor you already know. The second term is a
voltage that is there whatever the current does. A constant $v(0^-)$ transforms to
$v(0^-)/s$, so that second term is **a step source of $v(0^-)$ volts, in series with an
empty capacitor**.

That is not an analogy. In the $s$-domain a capacitor charged to 2 V *is* a 2 V battery
wired in series with an uncharged one, and every rule you have — series, parallel, the
divider, node equations — applies to the pair without amendment.

The inductor runs the same argument on $v = L\,di/dt$:

$$V(s) = L\big(sI(s) - i(0^-)\big) = sL\,I(s) - L\,i(0^-)$$

so an inductor already carrying $i(0^-)$ is **an impedance $sL$ in series with a source
of $L\,i(0^-)$**, pointing so as to keep the current going the way it was already
going. Note what is *not* there: no division by $s$. The units settle it. $L\,i(0^-)$ is
in webers, a weber is a volt-second, and a volt-second is exactly what an $s$-domain
voltage is measured in. Dividing by $s$ as well would describe flux that keeps being
applied for ever, rather than flux that was already present at the starting line.

## Reading the two numbers off the circuit

Before any of that can be used, $v_C(0^-)$ and $i_L(0^-)$ have to come from somewhere.
Almost always they come from the *previous* arrangement of the same circuit, and almost
always that arrangement has been sitting still long enough to settle. "Settled" has a
precise consequence: nothing is changing, so every derivative is zero, so

- $v_L = L\,di/dt = 0$ — an inductor with no voltage across it is **a short circuit**
- $i_C = C\,dv/dt = 0$ — a capacitor with no current through it is **an open circuit**

Redraw the pre-switch circuit with those two substitutions and what is left is
resistors and sources: a DC problem from your first week. Solve it, read off the
inductor currents and the capacitor voltages, and those numbers are your initial
conditions. Nothing else about the past matters, which is exactly what the transform's
lower limit of $0$ promised in module 1.

The superscript on $0^-$ is doing real work. It means *just before* the switch moves,
and it is the right instant precisely because $v_C$ and $i_L$ cannot jump: what they are
at $0^-$ they are still at $0^+$. Everything else in the circuit is different on the two
sides of the switch, so reading anything else at $0^-$ and using it afterwards is simply
wrong.

## Worked: a capacitor that was already at 5 V

A 15 V supply is connected at $t = 0$ through $R = 2.0\ \mathrm{k}\Omega$ to a
$C = 220$ nF capacitor that is already sitting at 5 V. What does the capacitor voltage
do?

Redraw first. The capacitor becomes $1/(sC)$ in series with a 5 V step source, i.e.
$5/s$. The supply is a 15 V step, i.e. $15/s$. That leaves one loop with two sources in
it, and the loop current is the net driving voltage over the total impedance:

```text
tau = R C = 2000 * 220e-9 = 4.4e-4 s = 440 us

         (15/s) - (5/s)          10/s
I(s) = ------------------  =  ------------
        R + 1/(sC)            R + 1/(sC)

multiply top and bottom by sC:

              10 C            2.2e-6
I(s) = --------------  =  --------------
         1 + s R C          1 + s(4.4e-4)
```

The capacitor node sits one impedance and one source above ground, so

```text
V_c(s) = 5/s  +  I(s)/(sC)

              5        10
       =    ---  +  ------------
              s      s (1 + sRC)

split the second term (module 2 does this by residues):

       10                10          10 R C
   ------------   =     ---   -   ------------
    s (1 + sRC)          s         1 + s R C

divide the last fraction, top and bottom, by RC:

       10 R C              10
   ------------   =   --------------
    1 + s R C          s + 1/tau

so   V_c(s) = 15/s  -  10/(s + 1/tau)
```

Two table entries invert that, $1/s \to 1$ and $1/(s+a) \to e^{-at}$:

$$v_c(t) = 15 - 10\,e^{-t/\tau}\ \mathrm{V}, \qquad \tau = 440\ \mu\mathrm{s}$$

Check both ends before trusting it. At $t = 0$ the exponential is 1 and $v = 5$ V, which
is where the capacitor started. As $t \to \infty$ it dies and $v \to 15$ V, the supply.
Now a number in the middle, at $t = 300\ \mu$s:

```text
t / tau      = 300e-6 / 440e-6      = 0.68182
e^(-0.68182)                        = 0.50570
v(300 us)    = 15 - 10 * 0.50570    = 15 - 5.0570   = 9.943 V

and the current at that instant, for a second opinion:
i = (15 - 9.943) / 2000 = 5.057 / 2000 = 2.528 mA
i = (10 / 2000) * 0.50570 = 5.000 mA * 0.50570 = 2.528 mA     agrees
```

Notice what the initial 5 V did and did not do. It changed the *size* of the exponential
term, from 15 to 10. It did not move the pole, which is still at $-1/(RC)$, so the
circuit still settles with the same 440 µs time constant it would have had from empty.

## Worked: an inductor that will not stop

A relay coil, $L = 100$ mH, has been carrying 0.25 A. At $t = 0$ the drive transistor
turns off and the only path left for the coil current is a 470 Ω flyback resistor across
the coil. What happens?

The coil becomes $sL$ in series with a source of $L\,i(0^-)$:

```text
L i(0-) = 0.100 * 0.25 = 0.025 V.s        (25 mWb; a weber IS a volt-second)

one loop, one source, two impedances in series:

            L i(0-)          0.025             0.25
I(s) = ---------------  =  -------------  =  ----------
          s L + R           0.1 s + 470       s + 4700

tau = L / R = 0.100 / 470 = 2.128e-4 s = 212.8 us,  and 1/tau = 4700 /s
```

One table entry inverts it: $i(t) = 0.25\,e^{-t/\tau}$, and the resistor therefore sees

$$v_R(t) = i(t)R = 117.5\,e^{-t/\tau}\ \mathrm{V}$$

Stop at $t = 0^+$ for a moment. **117.5 V**, from a coil that an instant earlier had
essentially nothing across it — it was settled, so it was a short.
Nobody applied 117.5 V; the inductor manufactured it, because its
current was 0.25 A and it was going to stay 0.25 A for at least an instant whatever
that cost, and 0.25 A through 470 Ω costs 117.5 V. That is the entire physics of the
inductive kick, and it is why every relay in every piece of equipment has a diode across
it. Put 47 kΩ there instead of 470 Ω and the same coil produces 11.75 kV.

A number further along, at $t = 400\ \mu$s:

```text
t / tau     = 400e-6 / 212.8e-6      = 1.8800
e^(-1.88)                            = 0.15259
i(400 us)   = 0.25 * 0.15259         = 38.15 mA
v_R         = 0.03815 * 470          = 17.93 V
```

and an energy check, because it costs one line: the coil started with
$\tfrac12 Li^2 = 0.5 \times 0.1 \times 0.25^2 = 3.125$ mJ, and all of it ends up in the
resistor, which is why the flyback resistor gets warm and the coil does not.

## The mistake people actually make

**Dividing $L\,i(0^-)$ by $s$.** This is by far the most common, and it is tempting for
a good reason: the capacitor's initial-condition source *is* divided by $s$, so the two
rules look as though they ought to match. They do not, and the asymmetry is not
arbitrary. The capacitor rule is solved for a *voltage*, so a constant initial voltage
appears and constants transform to $1/s$; the inductor rule leaves $L\,i(0^-)$ as it
comes out of $\mathcal{L}\{f'\} = sF - f(0^-)$, already in $s$-domain units. If you are
ever unsure, do the units. Amps times henries is volt-seconds; volt-seconds is what
$V(s)$ is measured in; dividing by $s$ would give volt-seconds-squared, which is not a
voltage in any domain.

Two smaller ones, both worth naming. **Reading the initial condition at $0^+$** instead
of $0^-$: harmless for $v_C$ and $i_L$, because those two are equal on both sides, and
fatal for anything else, because everything else jumps. And **getting the polarity of
the inductor's source backwards**, which turns a decay into a growth and is caught in
one line by asking whether the answer starts where the circuit actually was.

## Where this stops holding

- **A loop of capacitors and voltage sources.** Two capacitors charged to different
  voltages, connected face to face by a switch, cannot both keep their voltage — the
  loop equation forbids it. The model responds with an impulse of current, infinitely
  large and infinitely brief, and $v_C$ *does* jump. Real parts survive this because
  real wires have resistance and real capacitors have series resistance; the ideal model
  simply reports that something has been left out. The dual case is a cutset of
  inductors and current sources, where $i_L$ jumps and an impulsive voltage appears.
- **A switch that opens on an inductor with nowhere to go.** Set $R \to \infty$ in the
  worked example and the model predicts infinite voltage. What actually happens is an
  arc across the switch contacts, which is a nonlinear conductor the transform knows
  nothing about — and which is why the contacts erode.
- **"Settled" that is not actually settled.** The whole $0^-$ procedure assumes the
  previous arrangement had time to reach steady state. If the switch moves after two
  time constants rather than twenty, the initial conditions are whatever the *previous*
  transient had reached, and you have to solve that one first.
- **Nonlinear parts.** A diode, a saturating core, a transistor outside its
  small-signal range: none of these transform. EE201 handles them by linearising about
  an operating point and transforming the deviations, which is a different, careful
  claim.
''',
                },
                {
                    "title": "Zero-input, zero-state, and the shortcut that skips the algebra",
                    "minutes": 12,
                    "body": r'''
Once the initial conditions have been turned into ordinary sources, a switched circuit
contains two kinds of driving: the input you applied, and the energy that was already
in the storage elements. The circuit is linear. Linear means superposition, and
superposition means those two can be dealt with one at a time and added.

That is worth stating carefully, because it produces the two names that everything in
this module is filed under, and because there is a *second* split of the same response
that uses similar words and means something else entirely.

## The split that superposition gives you

Kill the initial-condition sources — set every $v_C(0^-)$ and $i_L(0^-)$ to zero — and
solve. What you get is the **zero-state response**: what the input does to a circuit
that starts empty. It is the response every transfer function in modules 1 to 3
describes, because a transfer function is defined with the initial conditions set to
zero.

Now put the initial conditions back and kill the input instead. What you get is the
**zero-input response**: what the stored energy does on its own, with nothing driving
the circuit. It always decays (in a circuit with resistance in it), because there is a
fixed amount of energy and the resistors are spending it.

Add them. The sum is the complete response, exactly, with no correction term, for any
linear circuit and any input.

The other split you will meet cuts the same response a different way. The **forced**
response is the part whose shape comes from the *input's* poles — a step in gives a
constant, a sinusoid in gives a sinusoid at the same frequency. The **natural** response
is the part whose shape comes from the *circuit's* own poles — the exponentials and
ringing that the circuit would produce if left alone. These are not the same two pieces
under different names, and the difference matters:

> The zero-state response usually contains natural terms too. Drive an empty RC with a
> step and the answer is $V(1 - e^{-t/\tau})$: the constant is forced, the exponential
> is natural, and both came out of the zero-state calculation with no initial energy
> anywhere.

So: zero-input/zero-state splits by *where the energy came from*; natural/forced splits
by *whose poles set the shape*. Both are useful. Confusing them produces the belief that
a circuit starting from rest has no transient, which the nearest oscilloscope disproves.

## Initial conditions never move a pole

Look at where the two source terms sit in the algebra. Solving any linear circuit in the
$s$-domain ends with

$$X(s) = \frac{N(s)}{D(s)}, \qquad
  N \ \text{from the sources}, \qquad D \ \text{from the impedances}$$

and the initial-condition sources contribute to the numerator only. They cannot touch
the denominator, because the denominator is built from the impedances — $R$, $sL$,
$1/(sC)$ — and those do not know how much energy is stored in anything.

The consequence is worth memorising, because it makes half the questions in this module
answerable without algebra: **initial conditions change the residues, never the poles.**
The time constants of a switched circuit, the frequency it rings at, whether it rings at
all: none of these depend on what was stored. What was stored decides only how big each
term is.

## Worked: the two halves, added

A 20 V supply feeds $R_1 = 10\ \mathrm{k}\Omega$ into a node; $R_2 = 15\ \mathrm{k}\Omega$
runs from that node to ground, and so does $C = 47$ nF. The capacitor is holding 3 V when
the supply is connected at $t = 0$. Find the node voltage.

First reduce what the capacitor can see. With the capacitor lifted out, the rest is a
Thévenin source:

```text
V_th = 20 * R2/(R1+R2) = 20 * 15/25            = 12.00 V
R_th = R1 || R2 = (10k * 15k)/(25k)            = 6.000 kohm
tau  = R_th * C = 6000 * 47e-9 = 2.82e-4 s     = 282 us
```

That 6 kΩ is the number people get wrong, and the reason to do this step explicitly:
the capacitor does not charge through $R_1$, it charges through $R_1$ **in parallel with**
$R_2$, because from the capacitor's terminals the supply is a short to ground and both
resistors lead there.

**Zero-state**, with the initial 3 V deleted: an empty capacitor charging to 12 V.

$$v_{zs}(t) = 12\left(1 - e^{-t/\tau}\right)$$

**Zero-input**, with the 20 V supply shorted out: a capacitor holding 3 V, discharging
into the same 6 kΩ.

$$v_{zi}(t) = 3\,e^{-t/\tau}$$

Add, at $t = 500\ \mu$s:

```text
t / tau      = 500e-6 / 282e-6       = 1.77305
e^(-1.77305)                         = 0.169814

zero-state:  12 * (1 - 0.169814)     = 12 * 0.830186   =  9.9622 V
zero-input:   3 * 0.169814                             =  0.5094 V
                                                         ---------
total                                                     10.4717 V
```

and the same thing collected into one line, which is what you would actually write:

$$v(t) = 12 - 9\,e^{-t/\tau} \quad\Longrightarrow\quad v(500\ \mu\mathrm{s}) = 12 - 9(0.169814) = 10.47\ \mathrm{V}$$

Both halves carry the same $e^{-t/\tau}$, with the same 282 µs, because both are shaped
by the one pole this circuit has. Only their sizes differ, and the sizes are what the
initial condition set.

## The shortcut, and where it comes from

For a first-order circuit the collected form above is always available, and it is worth
having as a formula because it removes the algebra entirely:

$$x(t) = x(\infty) + \big(x(0^+) - x(\infty)\big)e^{-t/\tau}$$

It is not a new result. It is what $A/s + B/(s+1/\tau)$ inverts to, with $A$ named
$x(\infty)$ by the final value theorem and $A + B$ named $x(0^+)$ by putting $t = 0$ into
the answer. Three numbers, and you are done:

1. $x(0^+)$ — from the pre-switch circuit, using the fact that $v_C$ and $i_L$ cannot
   jump.
2. $x(\infty)$ — from the post-switch circuit re-settled: $L$ back to a short, $C$ back
   to an open.
3. $\tau$ — from the resistance the storage element sees **with every independent
   source zeroed** (voltage sources shorted, current sources opened), times $C$, or
   divided into $L$.

$x$ can be any voltage or current in the circuit, not just the one across the storage
element, because every quantity in a one-pole circuit decays with the same $\tau$.

## Worked: a supply that steps down, twice over

$L = 50$ mH in series with $R = 100\ \Omega$, fed from a supply that has been at 12 V
long enough to settle. At $t = 0$ the supply drops to 5 V. Find the current at
$t = 300\ \mu$s.

By the shortcut:

```text
i(0-) : settled, so the inductor is a short  ->  12 / 100    = 0.120 A
i(inf): re-settled at the new supply         ->   5 / 100    = 0.050 A
tau   : the coil sees 100 ohm (the supply is a short to it)  = 0.05/100 = 500 us

i(t)  = 0.050 + (0.120 - 0.050) e^(-t/500us)  =  0.050 + 0.070 e^(-t/500us)

at t = 300 us :  t/tau = 0.600,  e^(-0.6) = 0.54881
i = 0.050 + 0.070 * 0.54881 = 0.050 + 0.038417 = 0.08842 A = 88.42 mA
```

Now the same problem the long way, to see that the shortcut is not a separate technique.
The coil is $sL$ in series with a source $L\,i(0^-) = 0.05 \times 0.12 = 6$ mV·s, and the
new supply is a 5 V step:

```text
        5/s + L i(0-)          5/s + 0.006          5 + 0.006 s
I(s) = ---------------  =  ----------------  =  -------------------
           s L + R           0.05 s + 100        s (0.05 s + 100)

divide top and bottom by 0.05 to make the pole readable:

           100 + 0.12 s            A          B
I(s) = -------------------  =     ---  +  ----------
         s ( s + 2000 )            s       s + 2000

A = (100 + 0.12*0)      / (0 + 2000)      = 100/2000    = 0.05
B = (100 + 0.12*(-2000))/ (-2000)         = -140/-2000  = 0.07

i(t) = 0.05 + 0.07 e^(-2000 t),   and 1/2000 s = 500 us
```

Identical, term for term. The residues $0.05$ and $0.07$ are the shortcut's
$x(\infty)$ and $x(0^+) - x(\infty)$, and the pole at $-2000$ is its $-1/\tau$. What the
shortcut buys is that you never wrote the fraction down; what the algebra buys is that
it keeps working when there are two poles and no shortcut exists.

One more reading, free: the voltage across the coil at $t = 300\ \mu$s is
$5 - iR = 5 - 8.842 = -3.842$ V. Negative, because the current is still falling and the
coil is fighting it. Check it the other way round, against
$v_L = L\,di/dt$: differentiating gives $di/dt = -140\,e^{-t/\tau}$, and
$0.05 \times (-140) \times 0.54881 = -3.842$ V. The same number, which is a good sign
that the residues are right.

## The mistake people actually make

**Using the wrong resistance in $\tau$.** In the worked Thévenin example, $\tau$ is
$(R_1\parallel R_2)C$ and not $R_1C$, and the reason is that $\tau$ is a property of the
circuit *with the sources killed*, not of the path the charging current appears to take.
It is tempting because the charging current does visibly come through $R_1$, and because
$\tau = RC$ is usually met in a circuit that only has one resistor. The symptom is an
answer with the right start and the right finish and the wrong speed — 470 µs instead of
282 µs here, a factor of $1{+}R_1/R_2$ out.

**Applying the shortcut to a second-order circuit.** With two storage elements there are
two poles, two exponentials and generally no single $\tau$; the formula silently returns
a plausible-looking single exponential that is not the response. The tell is easy: count
the capacitors and inductors that cannot be combined into one. If there are two, you are
in module 5's territory and the algebra is compulsory.

## Where this stops holding

- **Inputs that are not constant after the switch.** $x(\infty)$ only exists if the
  circuit settles. Drive it with a sinusoid and the forced response is a sinusoid, so
  the shortcut's second number does not exist — though the *split* into zero-input and
  zero-state survives perfectly well, because that only needed linearity.
- **Circuits without resistance.** An LC loop with initial energy has poles on the
  imaginary axis, and the zero-input response is a sinusoid that never decays. Nothing
  above is wrong, but "it always dies away" is, and the final value theorem will hand
  you a confident wrong answer if you ask it.
- **Nonlinear or time-varying parts.** Superposition is the load-bearing assumption in
  every line of this unit. A circuit containing a diode does not obey it, and neither
  the split nor the shortcut means anything there.
''',
                },
            ],
            "match": {
                "title": "What each symbol becomes once the switch has closed",
                "minutes": 6,
                "brief": r'''
Redrawing a schematic in the s-domain is a mechanical step, and it is the step where
the initial conditions either enter the algebra or get lost. Every symbol on the canvas
becomes an impedance, and two of them bring a source with them.
''',
                "prompt": "Pick a label, then tap the symbol it turns into.",
                "labels": [
                    "Impedance $sL$, in series with a source of $L\\,i(0^-)$ volt-seconds pushing the way the current was already going",
                    "Impedance $1/(sC)$, in series with a step source $v(0^-)/s$",
                    "Impedance $R$ — it stores nothing, so nothing is added",
                    "The reference node: no row and no column, because its voltage is already known",
                    "Whatever it was doing, transformed — a step of $V_0$ becomes $V_0/s$",
                    "It fixes a current whatever the voltage does, so it stamps straight into the right-hand side",
                ],
                "items": [
                    {"sym": "L", "a": 0, "why": "An inductor. $\\mathcal{L}\\{L\\,di/dt\\} = sLI(s) - Li(0^-)$, and that "
                     "subtracted constant is a source in series with the impedance. Its polarity aids the current "
                     "that was already flowing — an inductor's whole character is that it will not let its "
                     "current change, and the source is that refusal written as algebra."},
                    {"sym": "C", "a": 1, "why": "A capacitor. Solving $I(s) = sCV(s) - Cv(0^-)$ for $V$ gives "
                     "$V = I/(sC) + v(0^-)/s$: the familiar impedance, plus the initial voltage as a step source. "
                     "A capacitor charged to 2 V behaves, in the s-domain, exactly as though a 2 V battery were "
                     "wired in series with an empty one."},
                    {"sym": "R", "a": 2, "why": "A resistor. $Z_R = R$ at every frequency and at every instant — "
                     "it has no memory, so there is no initial condition to carry and nothing extra to draw. "
                     "Resistors are where energy leaves the circuit, which is why they set the damping and never "
                     "the natural frequency."},
                    {"sym": "GND", "a": 3, "why": "Ground. It is the node every other voltage is quoted against, "
                     "so its value is not an unknown, and a known value gets no equation. That is why an "
                     "$n$-node circuit has $n-1$ rows in its matrix, and why forgetting to place a ground makes "
                     "the whole system singular."},
                    {"sym": "V", "a": 4, "why": "A voltage source. It is a signal, so it is transformed like any "
                     "other signal: a step of $V_0$ becomes $V_0/s$, a ramp $V_0/s^2$, a pulse "
                     "$V_0(1-e^{-sT})/s$. Its pole is the input's pole, and it produces the steady part of the "
                     "answer rather than the transient."},
                ],
            },
            "blanks": [
                {
                    "title": "Redrawing the circuit, element by element",
                    "minutes": 8,
                    "caption": "the substitution table, and the two readings it needs before it can be used",
                    "lang": "text",
                    "brief": r'''
Redrawing is mechanical, and it is the step where the initial conditions either enter
the algebra or vanish from it. Two of the five lines below carry a source; two of them
are readings taken *before* the switch, off a circuit that has been left alone.

The units are the fastest check on the two source lines. An $s$-domain voltage is
measured in volt-seconds, so anything sitting in the same place as one had better be
volt-seconds too.
''',
                    "listing": """REDRAWING FOR t > 0.  Read v_C(0-) and i_L(0-) first; they are the only two
numbers that survive the switch.

  resistor  R                    ->   Z = R        and nothing else is added

  capacitor C, sitting at v0     ->   Z = 1/(sC)   in series with  ___

  inductor  L, carrying i0       ->   Z = sL       in series with  ___

  the input, a step of V0        ->   ___

  ------------------------------------------------------------------------
  taking the two readings, off a circuit left settled for a long time:

      nothing is changing, so v_L = L di/dt = 0, which makes the inductor
      ___ ;  the current through it is then set by the resistors alone

      nothing is changing, so the capacitor's current is ___ ;  it holds
      whatever voltage the resistive divider around it puts on it
""",
                    "blanks": [
                        {
                            "prompt": "What the capacitor's stored voltage becomes in the redrawn circuit.",
                            "hole": "?",
                            "opts": [
                                "a voltage source of v0/s",
                                "a voltage source of v0",
                                "a voltage source of C v0",
                                "a voltage source of v0/s^2",
                            ],
                            "a": 0,
                            "why": "Solving $I(s) = sCV(s) - Cv_0$ for the voltage gives $V = I/(sC) + v_0/s$. The stored voltage is a *constant* in time, and the transform of a constant $v_0$ is $v_0/s$, so that is what appears in series with the impedance.",
                            "whys": [
                                "Solving $I(s) = sCV(s) - Cv_0$ for the voltage gives $V = I/(sC) + v_0/s$. The stored voltage is a *constant* in time, and the transform of a constant $v_0$ is $v_0/s$, so that is what appears in series with the impedance.",
                                "A bare $v_0$ in the $s$-domain is volts, not volt-seconds, so it does not belong beside $I/(sC)$. In time it would be an impulse of area $v_0$ — a spike, not a level that stays.",
                                "$Cv_0$ is the stored *charge*, in coulombs. It is the term that appears when the capacitor rule is written for current, $I = sCV - Cv_0$, and it becomes a current source in the Norton form of the same model — not a voltage.",
                                "$v_0/s^2$ is the transform of a ramp $v_0 t$. The stored voltage does not climb once the switch moves; it starts at $v_0$ and is then pushed around by the rest of the circuit.",
                            ],
                        },
                        {
                            "prompt": "What the inductor's stored current becomes, in series with sL.",
                            "hole": "?",
                            "opts": [
                                "a voltage source of L i0",
                                "a voltage source of L i0 / s",
                                "a voltage source of i0 / (sL)",
                                "a current source of i0",
                            ],
                            "a": 0,
                            "why": "$\\mathcal{L}\\{L\\,di/dt\\} = sLI(s) - Li_0$, so the source is the constant $Li_0$ with no further division by $s$. Check the units: henries times amps is webers, a weber is a volt-second, and volt-seconds is exactly what an $s$-domain voltage is measured in.",
                            "whys": [
                                "$\\mathcal{L}\\{L\\,di/dt\\} = sLI(s) - Li_0$, so the source is the constant $Li_0$ with no further division by $s$. Check the units: henries times amps is webers, a weber is a volt-second, and volt-seconds is exactly what an $s$-domain voltage is measured in.",
                                "This is the commonest error in the module, and it comes from expecting the inductor rule to look like the capacitor rule. It does not: the capacitor's $v_0$ is a genuine time-domain constant that has to be transformed, while $Li_0$ falls out of the derivative rule already in the $s$-domain. Dividing again gives volt-seconds-squared, which is not a voltage in any domain.",
                                "Dividing by the impedance turns a voltage into a current, so this is dimensionally a current and cannot sit in series as a voltage source. It is also the wrong size by a factor of $sL$ twice over.",
                                "A current source of $i_0$ *is* the right model — but in **parallel** with $sL$, not in series. That is the Norton form of the same element, and it is the one to reach for when the surrounding circuit is easier to attack by node equations. In series, a current source would simply fix the loop current and ignore the rest of the circuit.",
                            ],
                        },
                        {
                            "prompt": "What a step input of V0 volts becomes.",
                            "hole": "?",
                            "opts": ["V0 / s", "V0", "V0 s", "V0 / s^2"],
                            "a": 0,
                            "why": "A source is a signal, and signals are transformed rather than substituted: $\\mathcal{L}\\{V_0\\} = V_0/s$. Its pole at $s = 0$ is the *input's* pole, and it is the one that produces the constant the response settles at.",
                            "whys": [
                                "A source is a signal, and signals are transformed rather than substituted: $\\mathcal{L}\\{V_0\\} = V_0/s$. Its pole at $s = 0$ is the *input's* pole, and it is the one that produces the constant the response settles at.",
                                "Leaving it as $V_0$ describes an impulse of area $V_0$ — a supply that appears and disappears in zero time. The final value theorem tells them apart at a glance: $\\lim_{s\\to0}sF(s)$ is $V_0$ for the step and $0$ for this.",
                                "Multiplying by $s$ differentiates, and the derivative of a step is an impulse. That is the switch-on edge with the supply that follows it thrown away.",
                                "$V_0/s^2$ is a ramp climbing at $V_0$ volts per second. A step arrives once and then holds still.",
                            ],
                        },
                        {
                            "prompt": "What a settled inductor is, at t = 0-.",
                            "hole": "?",
                            "opts": ["a short circuit", "an open circuit", "a current source of i0", "a resistor of value L"],
                            "a": 0,
                            "why": "Settled means nothing is changing, so $di/dt = 0$, so $v_L = L\\,di/dt = 0$. An element with zero volts across it and current flowing freely through it is a short. That is what lets you redraw the pre-switch circuit as pure resistors and read the current straight off.",
                            "whys": [
                                "Settled means nothing is changing, so $di/dt = 0$, so $v_L = L\\,di/dt = 0$. An element with zero volts across it and current flowing freely through it is a short. That is what lets you redraw the pre-switch circuit as pure resistors and read the current straight off.",
                                "That is the capacitor's steady-state behaviour, not the inductor's. Making the inductor an open would say no current flows through it at all, and the whole point of reading $i_L(0^-)$ is that a settled inductor is usually carrying a great deal of current.",
                                "True in the $t > 0$ model, and circular here: $i_0$ is precisely the number being looked for, so substituting it does not advance anything.",
                                "Henries are not ohms. An inductor opposes *change* in current and is indifferent to steady current, which is why its steady-state behaviour has no resistance in it at all.",
                            ],
                        },
                        {
                            "prompt": "The current through a settled capacitor, at t = 0-.",
                            "hole": "?",
                            "opts": ["zero", "v0 / R", "C v0", "whatever the resistors will supply"],
                            "a": 0,
                            "why": "$i_C = C\\,dv/dt$, and settled means $dv/dt = 0$. No current, whatever the voltage across it — which is the definition of an open circuit, and is why a settled capacitor's voltage is just the resistive divider around it.",
                            "whys": [
                                "$i_C = C\\,dv/dt$, and settled means $dv/dt = 0$. No current, whatever the voltage across it — which is the definition of an open circuit, and is why a settled capacitor's voltage is just the resistive divider around it.",
                                "That is the current at $t = 0^+$ in a circuit where the capacitor has just been connected across a resistor — a real quantity, but on the far side of the switch. Before the switch, nothing is moving.",
                                "$Cv_0$ is the stored charge in coulombs, not a current in amps. Charge is what a current has to move; the two differ by a division by time.",
                                "A capacitor's current does become whatever the rest of the circuit will supply, but only at an instant when its voltage is being *forced to change*. Long after a switch, nothing is forcing anything.",
                            ],
                        },
                    ],
                },
                {
                    "title": "A supply that steps down, line by line",
                    "minutes": 10,
                    "caption": "L = 120 mH in series with R = 300 Ω; the supply drops from 9 V to 3 V at t = 0",
                    "lang": "text",
                    "brief": r'''
Nothing is switched on here and nothing is switched off. A supply that was already
running simply changes value, which means the current neither starts at zero nor ends
at zero, and both ends of the exponential have to be worked out.

Fill the holes in order. Two of them are the initial condition and the source it turns
into; two are the pole and the time constant, which are the same fact written twice;
the last is the answer.
''',
                    "listing": """AN INDUCTOR THAT WAS ALREADY CARRYING CURRENT

  1  read the initial condition at t = 0-, with the coil settled and so a short

         i(0-) = 9 V / 300 ohm = ___ mA

  2  redraw for t > 0 : the coil is sL in series with a source of L i(0-)

         L i(0-) = 0.120 * 0.030 = ___ mV.s        (henry-amps are volt-seconds)

  3  KVL round the one loop, with the new 3 V supply transformed to 3/s :

         3/s + L i(0-)  =  I(s) ( sL + R )

                   3 + 0.0036 s              25 + 0.03 s
         I(s) = ---------------------- = ----------------------
                 s ( 0.120 s + 300 )        s ( s + ___ )

  4  split it by residues, one term per pole :

         I(s) = 0.010/s  +  0.020/(s + 2500)

  5  invert term by term, and read the time constant off the pole :

         i(t) = 10 mA + 20 mA * e^(-t/tau),      tau = ___ us

  6  evaluate one time constant after the step, at t = 400 us :

         i = 10 + 20 * 0.3679 = ___ mA
""",
                    "blanks": [
                        {
                            "prompt": "The current the coil was already carrying, in mA.",
                            "hole": "?",
                            "opts": ["30", "3", "300", "0.03"],
                            "a": 0,
                            "why": "A settled inductor has no voltage across it, so the whole 9 V appears across the 300 Ω and $i = 9/300 = 0.030$ A. The listing asks for milliamps, so 30.",
                            "whys": [
                                "A settled inductor has no voltage across it, so the whole 9 V appears across the 300 Ω and $i = 9/300 = 0.030$ A. The listing asks for milliamps, so 30.",
                                "3 mA would need 900 Ω, or 0.9 V across the 300 Ω. Neither is in the circuit.",
                                "300 mA is 0.3 A, which through 300 Ω would need 90 V. The resistance has been divided into the supply the wrong way round.",
                                "0.030 is the current in amps and the answer is right, but the line is written in milliamps and the two differ by a factor of a thousand. A step 4 built on 0.030 mA gives a final current of 10 µA.",
                            ],
                        },
                        {
                            "prompt": "The size of the inductor's initial-condition source, in mV.s.",
                            "hole": "?",
                            "opts": ["3.6", "0.36", "36", "3.6/s"],
                            "a": 0,
                            "why": "$L\\,i(0^-) = 0.120\\ \\mathrm{H} \\times 0.030\\ \\mathrm{A} = 3.6\\times10^{-3}$ V·s, which is 3.6 mV·s. Henry-amps are webers and a weber is a volt-second, so this really is an $s$-domain voltage as it stands.",
                            "whys": [
                                "$L\\,i(0^-) = 0.120\\ \\mathrm{H} \\times 0.030\\ \\mathrm{A} = 3.6\\times10^{-3}$ V·s, which is 3.6 mV·s. Henry-amps are webers and a weber is a volt-second, so this really is an $s$-domain voltage as it stands.",
                                "A factor of ten out. $0.120 \\times 0.030$ is $3.6\\times10^{-3}$, and $3.6\\times10^{-3}$ volt-seconds is 3.6 millivolt-seconds, not 0.36.",
                                "36 mV·s would be $0.120 \\times 0.30$ — the current taken as 300 mA rather than 30 mA. It propagates: step 4's second residue would come out ten times too large and the current would start at 210 mA.",
                                "The division by $s$ is the standard trap, and it is the capacitor's rule borrowed by an inductor. $Li_0$ arrives already in the $s$-domain out of $\\mathcal{L}\\{f'\\} = sF - f(0^-)$; dividing again gives volt-seconds-squared.",
                            ],
                        },
                        {
                            "prompt": "The pole's position, after dividing top and bottom by 0.120.",
                            "hole": "?",
                            "opts": ["2500", "300", "0.0004", "3600"],
                            "a": 0,
                            "why": "$300 / 0.120 = 2500$, so the denominator reads $s(s + 2500)$ and the pole sits at $s = -2500$ per second. The same division fixes the numerator: $3/0.120 = 25$ and $0.0036/0.120 = 0.03$, which is the form printed on the right.",
                            "whys": [
                                "$300 / 0.120 = 2500$, so the denominator reads $s(s + 2500)$ and the pole sits at $s = -2500$ per second. The same division fixes the numerator: $3/0.120 = 25$ and $0.0036/0.120 = 0.03$, which is the form printed on the right.",
                                "300 is $R$ in ohms, and the whole point of the division is to strip $L$ out of the $s$ coefficient so the pole can be read directly. A pole is in reciprocal seconds; ohms are not.",
                                "0.0004 s is the time constant, which is $1/2500$. It belongs in the exponential, not in the denominator beside $s$ — the two are reciprocals, and putting the wrong one here makes the current settle in nanoseconds.",
                                "3600 has the numerator's $0.0036$ in it, which plays no part in where the pole is. Pole positions come from the denominator alone; the numerator only decides how big each term is.",
                            ],
                        },
                        {
                            "prompt": "The time constant, in microseconds.",
                            "hole": "?",
                            "opts": ["400", "2500", "40", "250"],
                            "a": 0,
                            "why": "$\\tau = 1/2500 = 4\\times10^{-4}$ s $= 400\\ \\mu$s, and the direct route agrees: $\\tau = L/R = 0.120/300 = 400\\ \\mu$s. That the two agree is the check that the division in step 3 was done right.",
                            "whys": [
                                "$\\tau = 1/2500 = 4\\times10^{-4}$ s $= 400\\ \\mu$s, and the direct route agrees: $\\tau = L/R = 0.120/300 = 400\\ \\mu$s. That the two agree is the check that the division in step 3 was done right.",
                                "2500 is the pole, in reciprocal seconds. Its reciprocal is the time constant; quoting it as a time makes the transient last 2.5 milliseconds per microsecond asked for.",
                                "A factor of ten out: $1/2500$ is $4\\times10^{-4}$, not $4\\times10^{-5}$. It is worth checking against $L/R$ every time, precisely because a decade slip here is invisible in the algebra and obvious on a scope.",
                                "250 µs is $L/R$ with $R$ and $L$ swapped somewhere, or $1/4000$. Neither 4000 nor 250 appears anywhere in this circuit.",
                            ],
                        },
                        {
                            "prompt": "The current one time constant after the step, in mA.",
                            "hole": "?",
                            "opts": ["17.36", "27.36", "7.36", "10.00"],
                            "a": 0,
                            "why": "$i = 10 + 20 e^{-1} = 10 + 20(0.3679) = 10 + 7.36 = 17.36$ mA. The other reading of the same number: the current has 20 mA of gap to close between 30 mA and 10 mA, one time constant closes 63.2% of any gap, and $30 - 0.632\\times20 = 17.36$ mA.",
                            "whys": [
                                "$i = 10 + 20 e^{-1} = 10 + 20(0.3679) = 10 + 7.36 = 17.36$ mA. The other reading of the same number: the current has 20 mA of gap to close between 30 mA and 10 mA, one time constant closes 63.2% of any gap, and $30 - 0.632\\times20 = 17.36$ mA.",
                                "27.36 mA is the starting 30 mA barely moved, and it comes from adding the decayed term to $i(0^-)$ rather than to $i(\\infty)$. The constant term in the inverted transform is always the final value.",
                                "7.36 mA is the exponential term on its own, with the settled 10 mA left out. It would mean the current ends up below where the new supply can hold it, which the circuit has no way to do.",
                                "10.00 mA is the final value, reached after several time constants rather than one. At $t = \\tau$ the transient still has 36.8% of its original size left.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "What the circuit had settled to before anything moved",
                    "minutes": 6,
                    "brief": r'''
Every switching problem starts here, and this step is pure bookkeeping: find the two
numbers that will survive the switch.

The circuit below has been connected, untouched, for several minutes. Nothing is
changing, so every derivative in it is zero — and that single fact collapses both
energy-storing parts into things you have been able to analyse since your first week.
An inductor with no voltage across it is a piece of wire. A capacitor with no current
through it is a gap.

Redraw it with those two substitutions and what is left is a supply and two resistors.
''',
                    "prompt": "What voltage is the capacitor holding, just before anything is switched?",
                    "note": "Nothing is changing. Replace the inductor and the capacitor with what each becomes in steady state, then read the remaining circuit.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 7, "y": 3, "rot": 0, "value": 4700},
                            {"id": "l", "kind": "L", "x": 11, "y": 3, "rot": 0, "value": 0.033},
                            {"id": "r2", "kind": "R", "x": 15, "y": 6, "rot": 1, "value": 3300},
                            {"id": "g1", "kind": "GND", "x": 15, "y": 10},
                            {"id": "c", "kind": "C", "x": 19, "y": 6, "rot": 1, "value": 220e-9},
                            {"id": "g2", "kind": "GND", "x": 19, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 22, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [6, 3]},
                            {"a": [8, 3], "b": [10, 3]},
                            {"a": [12, 3], "b": [15, 3]},
                            {"a": [15, 3], "b": [15, 5]},
                            {"a": [15, 7], "b": [15, 10]},
                            {"a": [15, 3], "b": [19, 3]},
                            {"a": [19, 3], "b": [19, 5]},
                            {"a": [19, 7], "b": [19, 10]},
                            {"a": [19, 3], "b": [22, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V, connected long enough to settle"},
                        {"label": "R1", "value": "4.70 kΩ"},
                        {"label": "L", "value": "33 mH"},
                        {"label": "R2", "value": "3.30 kΩ"},
                        {"label": "C", "value": "220 nF"},
                    ],
                    "aside": "The inductance and the capacitance do not appear in the answer at all. In "
                             "steady state neither part has any say in the voltages — they only decide how "
                             "long it takes to get there, and nothing here is going anywhere.",
                    # c.dc() puts a capacitor in as an open and an inductor as a zero-volt source,
                    # which is exactly the pair of substitutions the question is about. The probe
                    # sits on the capacitor's top plate, so reading it is reading v_C(0-).
                    "check": r'''
return c.vout();
''',
                    "answer": 4.95,
                    "tol": 0.05,
                    "unit": "V",
                    "hint": "The inductor is a short, so R1 and R2 are simply in series across the supply. "
                            "The capacitor is an open, so it draws nothing and just sits at whatever the "
                            "divider gives it.",
                    "wrong": "If you got 7.05 V you took the drop across R1 rather than the voltage on R2. "
                             "If you got 12 V you treated the inductor as an open and left R2 with nothing "
                             "across it — a settled inductor is the opposite, a short.",
                    "why": "Settled means nothing changes, so $v_L = L\\,di/dt = 0$ (the inductor is a short) "
                           "and $i_C = C\\,dv/dt = 0$ (the capacitor is an open). What is left is 4.70 kΩ and "
                           "3.30 kΩ in series across 12 V, carrying "
                           "$12/8000 = 1.50\\ \\mathrm{mA}$, and the capacitor sits on top of R2 at "
                           "$1.50\\ \\mathrm{mA} \\times 3.30\\ \\mathrm{k}\\Omega = 4.95$ V. Those two "
                           "numbers — 4.95 V on the capacitor and 1.50 mA through the inductor — are the "
                           "complete summary of everything that happened before $t = 0$. Whatever moves "
                           "next, they are what the circuit starts from, because they are the only two "
                           "quantities in it that cannot jump.",
                },
                {
                    "title": "A capacitor that was not empty",
                    "minutes": 8,
                    "brief": r'''
Every worked example so far has started from rest. Bench circuits rarely do: a
capacitor holds its charge, a switch closes onto a circuit that was already doing
something, and the response starts from wherever it happened to be.

The schematic below has that stored charge already drawn in, using the substitution
the matching exercise just went through: a capacitor sitting at $v(0^-)$ is an *empty*
capacitor in series with a source of $v(0^-)$. The 4 V source beneath the capacitor is
therefore not a second supply — it is the charge that was left on it, drawn as a part.

Nothing about the method changes. The pole is the same, the time constant is the same;
only the size of the exponential term moves.
''',
                    "prompt": "What is the probe voltage 0.50 ms after the supply is connected?",
                    "note": "The capacitor itself starts empty; the 4 V in series with it is the charge it was left holding, and that charge has not gone anywhere. Work out the time constant first.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 1000},
                            {"id": "c", "kind": "C", "x": 11, "y": 6, "rot": 1, "value": 5e-7},
                            {"id": "v0", "kind": "V", "x": 11, "y": 9, "rot": 1, "value": 4},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 11},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [11, 3]},
                            {"a": [11, 3], "b": [11, 5]},
                            {"a": [11, 7], "b": [11, 8]},
                            {"a": [11, 10], "b": [11, 11]},
                            {"a": [11, 3], "b": [15, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "10.0 V, connected at t = 0"},
                        {"label": "R", "value": "1.00 kΩ"},
                        {"label": "C", "value": "500 nF"},
                        {"label": "Charge left on C, drawn as the source in series with it", "value": "4.00 V"},
                    ],
                    "aside": "The schematic already carries the substitution: an empty $1/(sC)$ in series with a "
                             "source that is $4/s$ once transformed. The divider rule then gives the answer with no "
                             "calculus. The first-order form "
                             "$v(t) = V_f + (V_0 - V_f)e^{-t/\\tau}$ is the same result, already inverted.",
                    # Solved rather than asserted: the transient below is run by
                    # tools/verify_numeric.mjs on this very schematic, and it reads the probe at
                    # the instant the prompt asks about. No component value is repeated here, so
                    # editing R, C or either source moves the measured number and the gate says so.
                    "check": r'''
const run = c.step(0.5e-3);          /* 0.50 ms, the instant the prompt asks about */
return run.v[run.v.length - 1];      /* the probe voltage at the end of that run */
''',
                    "answer": 7.793,
                    "tol": 0.05,
                    "unit": "V",
                    "hint": "$\\tau = RC$, the final value is 10 V and the starting value is 4 V. Then "
                            "$v(t) = 10 + (4 - 10)e^{-t/\\tau}$, and the time asked for is exactly one $\\tau$.",
                    "wrong": "If you got 6.32 V you started the capacitor from empty. The initial charge does not "
                             "wash out of the answer — it sets where the exponential begins.",
                    "why": "$\\tau = 1\\,\\mathrm{k}\\Omega \\times 500\\,\\mathrm{nF} = 0.5$ ms, so 0.50 ms is exactly "
                           "one time constant. $v = 10 + (4-10)e^{-1} = 10 - 6 \\times 0.3679 = 7.79$ V. The same "
                           "number the other way round: the gap between start and finish is 6 V, one time constant "
                           "closes 63.2% of any gap, and $4 + 0.632 \\times 6 = 7.79$ V. Notice what the initial "
                           "charge did and did not do — it changed the size of the exponential term, not the "
                           "pole, so the circuit still settles with the same 0.5 ms time constant it would have had "
                           "from empty.",
                },
                {
                    "title": "The kick a coil gives when its path is taken away",
                    "minutes": 10,
                    "brief": r'''
A relay coil has been carrying 0.30 A downwards, from the top node through the winding
to ground. At $t = 0$ the drive is removed and the only path left for that current is
the 110 Ω resistor sitting across the coil.

The coil has been drawn in its **Norton** form, which is the other way of writing the
same substitution the matching exercise went through. Solving $V(s) = sLI(s) - Li(0^-)$
for the current instead of the voltage gives $I = V/(sL) + i(0^-)/s$: an empty inductor
with a **step current source in parallel**, rather than an impedance with a voltage
source in series. The two are the same element; use whichever suits the surrounding
circuit, and here parallel suits it, because everything in this circuit is in parallel.

The source is drawn taking 0.30 A *down* out of the top node, which is the direction the
coil's current was already going. That direction is the whole question. The current has
to keep flowing, the only thing left to flow through is the resistor, and a resistor
carrying current upwards from ground has its top end below ground.
''',
                    "prompt": "What is the probe voltage 500 µs after the drive is removed?",
                    "note": "Work out the time constant first, then the voltage at the instant the switch opens. Watch the sign: the answer is not positive.",
                    "diagram": {
                        "parts": [
                            {"id": "i0", "kind": "I", "x": 3, "y": 6, "rot": 1, "value": 0.30},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "l", "kind": "L", "x": 8, "y": 6, "rot": 1, "value": 0.022},
                            {"id": "g1", "kind": "GND", "x": 8, "y": 9},
                            {"id": "r", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 110},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 16, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 3], "b": [8, 3]},
                            {"a": [8, 3], "b": [8, 5]},
                            {"a": [8, 7], "b": [8, 9]},
                            {"a": [8, 3], "b": [13, 3]},
                            {"a": [13, 3], "b": [13, 5]},
                            {"a": [13, 7], "b": [13, 9]},
                            {"a": [13, 3], "b": [16, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Coil current already flowing, drawn as the parallel source", "value": "0.300 A, downwards"},
                        {"label": "L", "value": "22 mH"},
                        {"label": "R", "value": "110 Ω"},
                        {"label": "Instant asked about", "value": "t = 500 µs"},
                    ],
                    "aside": "$\\tau = L/R$ for an inductor, not $L \\times R$ and not $RC$. The check on it "
                             "is dimensional: henries over ohms is $\\mathrm{V\\,s/A} \\div \\mathrm{V/A}$, "
                             "which is seconds.",
                    # Solved rather than asserted: the transient is run on this very schematic, and
                    # the probe is read at the instant the prompt names. The current source is the
                    # Norton form of the coil's initial current, so no initial condition is hidden
                    # from the solver — it starts every inductor at zero, as the model requires.
                    "check": r'''
const run = c.step(500e-6);          /* 500 us after the drive is removed */
return run.v[run.v.length - 1];      /* the probe voltage at the end of that run */
''',
                    "answer": -2.709,
                    "tol": 0.05,
                    "unit": "V",
                    "hint": "$\\tau = L/R = 22\\,\\mathrm{mH}/110\\,\\Omega = 200\\ \\mu$s, so 500 µs is 2.5 "
                            "time constants. At $t = 0^+$ the resistor is carrying the coil's 0.30 A, and it "
                            "is carrying it upwards from ground.",
                    "wrong": "If you got +2.709 V you have the size right and the direction wrong. The "
                             "current did not reverse when the drive was removed — that is precisely what an "
                             "inductor will not do — so it is still flowing down through the coil, which "
                             "means up through the resistor, which puts the top of the resistor below "
                             "ground. If you got −33 V you either stopped at $t = 0^+$ and never let it "
                             "decay, or took $\\tau$ as $L \\times R = 2.42$ s rather than "
                             "$L/R = 200\\ \\mu$s — which makes 500 µs no time at all, so both mistakes "
                             "land on the same number.",
                    "why": "$\\tau = L/R = 0.022/110 = 200\\ \\mu$s. At the instant the drive is removed the "
                           "coil is still carrying 0.300 A and the resistor is the only path, so the "
                           "resistor carries 0.300 A and develops $0.300 \\times 110 = 33.0$ V — with its "
                           "*grounded* end positive, because the current is entering there. The probed node "
                           "therefore starts at $-33.0$ V and decays: "
                           "$v(t) = -33.0\\,e^{-t/\\tau}$. At 500 µs that is $t/\\tau = 2.5$, "
                           "$e^{-2.5} = 0.0821$, and $-33.0 \\times 0.0821 = -2.71$ V. The size of the "
                           "initial spike is worth dwelling on: nobody applied 33 V, and a moment earlier "
                           "the coil had almost nothing across it. It manufactured the voltage because its "
                           "current was 0.300 A and it was going to stay 0.300 A for at least an instant "
                           "whatever that cost. Replace the 110 Ω with 11 kΩ and the same coil produces "
                           "3.3 kV — which is what happens across a switch contact that opens on a coil "
                           "with no resistor across it at all, and why such contacts erode.",
                },
                {
                    "title": "A charged capacitor in a network that has more than one resistor",
                    "minutes": 12,
                    "brief": r'''
Everything so far has had one resistor, so there was never a question about which
resistance set the time constant. Here there are two, and they do different jobs: one
of them sets where the response ends up, and both of them together set how fast it gets
there.

The capacitor was left holding 8 V by whatever the circuit was doing before, and that
charge is drawn in the schematic as a source in series with an empty capacitor — the
same substitution as before. At $t = 0$ the 12 V supply is connected.

The quantity asked for is not a node voltage. Get the node voltage first, then take one
more step.
''',
                    "prompt": "What current is the supply pushing through R1, 0.30 ms after it is connected?",
                    "note": "Answer in milliamps. The time constant is not R1 C — work out what resistance the capacitor actually sees.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 4700},
                            {"id": "r2", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 3300},
                            {"id": "g1", "kind": "GND", "x": 12, "y": 10},
                            {"id": "c", "kind": "C", "x": 16, "y": 6, "rot": 1, "value": 1e-7},
                            {"id": "v0", "kind": "V", "x": 16, "y": 9, "rot": 1, "value": 8},
                            {"id": "g2", "kind": "GND", "x": 16, "y": 11},
                            {"id": "out", "kind": "OUT", "x": 20, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [12, 3], "b": [12, 5]},
                            {"a": [12, 7], "b": [12, 10]},
                            {"a": [12, 3], "b": [16, 3]},
                            {"a": [16, 3], "b": [16, 5]},
                            {"a": [16, 7], "b": [16, 8]},
                            {"a": [16, 10], "b": [16, 11]},
                            {"a": [16, 3], "b": [20, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V, connected at t = 0"},
                        {"label": "R1", "value": "4.70 kΩ"},
                        {"label": "R2", "value": "3.30 kΩ"},
                        {"label": "C", "value": "100 nF"},
                        {"label": "Charge left on C, drawn as the source under it", "value": "8.00 V"},
                        {"label": "Instant asked about", "value": "t = 0.30 ms"},
                    ],
                    "aside": "Three numbers finish a first-order problem: where it starts, where it ends, "
                             "and how fast. The start is the capacitor's 8 V, because $v_C$ cannot jump. "
                             "The end is the divider, because a settled capacitor draws nothing. The speed "
                             "is $R_{th}C$ with the supply shorted, which is what puts R1 and R2 in "
                             "parallel.",
                    # The transient is run on the schematic and the probe gives the capacitor node.
                    # The current is then one subtraction and one division, with both constants read
                    # off the drawn parts rather than repeated here, so editing either moves the
                    # measured answer and the gate says so.
                    "check": r'''
const run = c.step(0.30e-3);
const va  = run.v[run.v.length - 1];                 /* the capacitor node at 0.30 ms */
const sup = c.net.parts.filter(function (p) { return p.id === 'v';  })[0].value;
const r1  = c.net.parts.filter(function (p) { return p.id === 'r1'; })[0].value;
return (sup - va) / r1 * 1000;                       /* volts over ohms, in mA */
''',
                    "answer": 1.362,
                    "tol": 0.015,
                    "unit": "mA",
                    "hint": "Lift the capacitor out and Thévenise what it sees: $V_{th}$ is the divider "
                            "output, $R_{th}$ is R1 in parallel with R2. Then "
                            "$v = V_{th} + (8 - V_{th})e^{-t/\\tau}$, and the current through R1 is "
                            "$(12 - v)/R_1$.",
                    "wrong": "If you got 1.16 mA you used $\\tau = R_1C = 470\\ \\mu$s instead of "
                             "$R_{th}C = 194\\ \\mu$s, so your capacitor is still far more charged than it "
                             "really is and the supply is delivering less. If you got 1.72 mA you started "
                             "the capacitor from empty and ignored the 8 V it was holding. If you got "
                             "1.50 mA you used the settled value, and 0.30 ms is only about 1.5 time "
                             "constants in — the response is not finished. And if you got 0.001362, that "
                             "is the right current in amps, asked for in milliamps.",
                    "why": "Thévenise what the capacitor sees. $V_{th} = 12 \\times 3300/8000 = 4.95$ V and "
                           "$R_{th} = 4700 \\parallel 3300 = 4700 \\times 3300 / 8000 = 1.939\\ \\mathrm{k}\\Omega$, "
                           "so $\\tau = 1938.75 \\times 100\\ \\mathrm{nF} = 193.9\\ \\mu$s. The capacitor "
                           "starts at 8 V and heads for 4.95 V, so "
                           "$v(t) = 4.95 + 3.05\\,e^{-t/\\tau}$. At $t = 0.30$ ms, "
                           "$t/\\tau = 1.5474$ and $e^{-1.5474} = 0.2128$, giving "
                           "$v = 4.95 + 3.05 \\times 0.2128 = 5.599$ V. The supply then pushes "
                           "$(12 - 5.599)/4700 = 6.401/4700 = 1.362$ mA through R1. Note that the "
                           "capacitor is *discharging* here even though a supply has just been connected — "
                           "8 V was above the 4.95 V the divider can hold, so the charge has somewhere to "
                           "go and both resistors are helping it get there. That is why $R_{th}$ is the "
                           "parallel pair and not R1 alone: from the capacitor's terminals, the supply is a "
                           "short to ground and both resistors lead back to it.",
                },
            ],
            "build": {
                "title": "A response that starts where you tell it to",
                "minutes": 20,
                "brief": r'''
Reading a schematic that already has the initial condition drawn in is the easy half.
This is the other half: given a response, draw the circuit that produces it, initial
condition included.

## The specification

Build a first-order circuit, driven from the 10 V supply already on the canvas, whose
probe voltage

- **starts at 4.0 V** at the instant the supply is connected, rather than at zero
- **settles at 10 V**
- has a **time constant of 250 µs**, so that one $\tau$ after switch-on it is at
  $4 + 0.632 \times 6 = 7.79$ V
- uses exactly **one resistor and one capacitor**, so that it really is one pole
- and uses a **resistor of at least 2 kΩ**, so the supply is never asked for more than
  a few milliamps at the switching instant

The first three describe the response. The fourth says it must be first order. The fifth
is the one that does the work, because the first four are satisfied by an infinite
family of part pairs and this picks out a corner of it: with $\tau = RC$ fixed at 250 µs,
a floor on $R$ is a ceiling on $C$.

## What is on the canvas

A 10 V supply, its ground, and a 470 Ω resistor already wired to the supply. That
resistor is a perfectly respectable member of the RC family — with 532 nF beside it the
time constant is right — and it is not allowed, because it is below the floor and would
draw 13 mA from the supply at $t = 0^+$.

Everything else is missing, including the initial condition. **A capacitor sitting at
$v(0^-)$ is an empty capacitor in series with a step source of $v(0^-)$**, so the 4 V
start is not a property you can dial in on the capacitor — it is a part you have to
place. Add it, in series with the capacitor, on the ground side.

## How this is measured

Nothing compares your drawing with a reference. The checks run a transient on whatever
you built and read the probe at three times — an instant after switch-on, one time
constant later, and long after everything has settled — plus a count of parts and one
look at the resistor value, which is the only line of the specification that is not a
property of the response. Any circuit that behaves as specified passes, and there are
many.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 10},
                        {"id": "p2", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 470},
                    ],
                    "wires": [
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [3, 6], "b": [3, 3]},
                        {"a": [3, 3], "b": [7, 3]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 10},
                        {"id": "p2", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 2500},
                        {"id": "p3", "kind": "C", "x": 12, "y": 6, "rot": 1, "value": 1e-7},
                        {"id": "p4", "kind": "V", "x": 12, "y": 9, "rot": 1, "value": 4},
                        {"id": "p5", "kind": "GND", "x": 12, "y": 11},
                        {"id": "p6", "kind": "OUT", "x": 16, "y": 3},
                    ],
                    "wires": [
                        {"a": [3, 8], "b": [3, 10]},
                        {"a": [3, 6], "b": [3, 3]},
                        {"a": [3, 3], "b": [7, 3]},
                        {"a": [9, 3], "b": [12, 3]},
                        {"a": [12, 3], "b": [12, 5]},
                        {"a": [12, 7], "b": [12, 8]},
                        {"a": [12, 10], "b": [12, 11]},
                        {"a": [12, 3], "b": [16, 3]},
                    ],
                },
                "checks": [
                    {
                        "name": "the response starts at 4 V, not at zero",
                        "code": r'''
const r = c.step(1e-6);
c.close(r.v[r.v.length - 1], 4, 0.02,
  'an instant after switch-on the probe should already be at 4 V');
''',
                    },
                    {
                        "name": "it settles at the supply",
                        "code": r'''
const r = c.step(5e-3);
c.close(r.v[r.v.length - 1], 10, 0.01,
  'after twenty time constants the probe should have reached 10 V');
''',
                    },
                    {
                        "name": "one time constant is 250 us",
                        "code": r'''
const r = c.step(250e-6);
c.close(r.v[r.v.length - 1], 7.7927, 0.015,
  'at t = 250 us the probe should have closed 63.2% of the gap from 4 V to 10 V');
''',
                    },
                    {
                        "name": "exactly one resistor and one capacitor",
                        "code": r'''
c.assert(c.count('R') === 1, 'one resistor, no more and no fewer — the response has one pole');
c.assert(c.count('C') === 1, 'one capacitor, no more and no fewer');
''',
                    },
                    {
                        "name": "the resistor is at least 2 kohm",
                        "code": r'''
const r = c.values('R')[0];
c.assert(r >= 2000, 'the resistor is ' + c.fmt(r, 'ohm') +
  ', and the specification puts a floor of 2 kohm on it');
''',
                    },
                ],
                "hints": [
                    "Three parts and a probe are missing: a resistor of the right size, a capacitor, and "
                    "the source that represents its initial charge. The second ground goes under the "
                    "source, not under the capacitor.",
                    "$\\tau = RC = 250\\ \\mu$s with $R \\ge 2\\ \\mathrm{k}\\Omega$ forces "
                    "$C \\le 125$ nF. 2.5 kΩ with 100 nF is the roundest pair; 5 kΩ with 50 nF and "
                    "25 kΩ with 10 nF pass just as well.",
                    "If the response starts at zero rather than at 4 V, the initial-condition source is "
                    "missing or is shorted out. It has to be in series with the capacitor — between the "
                    "capacitor's bottom plate and ground — so that the capacitor node sits 4 V above "
                    "ground before any charging has happened.",
                    "If it starts at zero and settles at 14 V, the source has gone in series with the "
                    "supply instead. There it adds to the drive and changes where the response ends; in "
                    "the right position it changes only where the response begins, and the supply still "
                    "decides where it finishes.",
                ],
            },
            "derive": {
                "title": "The general first-order answer, initial condition and all",
                "minutes": 14,
                "vars": ["s", "R", "C", "t", "e", "V_s", "V_0", "I", "V_c", "A", "B"],
                "brief": r'''
Module 1 solved a series RC driven by a step, starting from empty. This is the same
circuit with the two restrictions lifted: the supply is a step of $V_s$ rather than 1 V,
and the capacitor already holds $V_0$.

Redrawn for $t > 0$ it is one loop containing $R$, an impedance $1/(sC)$, and **two**
sources: the supply $V_s/s$ driving forwards and the initial charge $V_0/s$ pushing
back. Take the output across the capacitor pair — that is, across the impedance *and*
its source together, which is where a voltmeter on the real capacitor would sit.

Six lines of algebra produce a formula worth carrying: every first-order circuit in this
course is an instance of it.
''',
                "steps": [
                    {
                        "prompt": "Write the loop current $I(s)$, in terms of $s$, $R$, $C$, $V_s$ and $V_0$.",
                        "given": "One loop. The net driving voltage is $V_s/s - V_0/s$; the total impedance is $R + 1/(sC)$.",
                        "answer": "\\frac{C(V_s - V_0)}{1 + sRC}",
                        "hint": "Put $(V_s - V_0)/s$ over $R + 1/(sC)$, then multiply top and bottom by $sC$ to clear the inner fraction.",
                        "deconstruct": [
                            "The ratio is $\\dfrac{(V_s - V_0)/s}{R + 1/(sC)}$.",
                            "Multiplying top and bottom by $sC$ turns the numerator into $C(V_s - V_0)$ and the denominator into $sRC + 1$.",
                            "The $s$ underneath has cancelled, which is the first sign this is not a pure step response.",
                        ],
                    },
                    {
                        "prompt": "The capacitor node is one impedance and one source above ground: $V_c = I/(sC) + V_0/s$. Substitute and write $V_c(s)$.",
                        "answer": "\\frac{V_s - V_0}{s(1 + sRC)} + \\frac{V_0}{s}",
                        "hint": "Dividing the previous answer by $sC$ cancels the $C$ and leaves an $s$ in the denominator. Leave the two terms separate for now.",
                        "deconstruct": [
                            "$\\dfrac{1}{sC} \\cdot \\dfrac{C(V_s - V_0)}{1 + sRC} = \\dfrac{V_s - V_0}{s(1 + sRC)}$.",
                            "Add the initial-condition source, which is $V_0/s$ and is not divided by anything else.",
                        ],
                    },
                    {
                        "prompt": "Split the first term: $\\dfrac{V_s - V_0}{s(1 + sRC)} = \\dfrac{A}{s} + \\dfrac{B}{1 + sRC}$. Multiply both sides by $s$, set $s = 0$, and give $A$.",
                        "answer": "V_s - V_0",
                        "hint": "Multiplying by $s$ leaves $\\dfrac{V_s - V_0}{1 + sRC}$ on the left, and the $B$ term picks up a factor $s$ that kills it at $s = 0$.",
                        "deconstruct": [
                            "$s \\cdot \\dfrac{V_s - V_0}{s(1+sRC)} = \\dfrac{V_s - V_0}{1+sRC}$.",
                            "At $s = 0$ the denominator is 1, so what survives is the numerator.",
                        ],
                    },
                    {
                        "prompt": "Now multiply both sides by $(1 + sRC)$ and set $s = -1/(RC)$, where that factor vanishes. Give $B$.",
                        "answer": "-RC(V_s - V_0)",
                        "hint": "The left-hand side becomes $\\dfrac{V_s - V_0}{s}$. Evaluate it at $s = -1/(RC)$.",
                        "deconstruct": [
                            "$(1+sRC) \\cdot \\dfrac{V_s - V_0}{s(1+sRC)} = \\dfrac{V_s - V_0}{s}$, and the $A/s$ term picks up the factor $(1+sRC)$, which is zero at this $s$.",
                            "Substituting $s = -1/(RC)$ gives $(V_s - V_0)$ divided by $-1/(RC)$, which is $-RC(V_s-V_0)$.",
                        ],
                    },
                    {
                        "prompt": "Put $A$ and $B$ back, add the $V_0/s$ from step 2, and collect. Write $V_c(s)$ with denominators $s$ and $s + 1/(RC)$ only.",
                        "given": "Dividing $\\dfrac{-RC(V_s-V_0)}{1+sRC}$ top and bottom by $RC$ turns the denominator into $s + 1/(RC)$.",
                        "answer": "\\frac{V_s}{s} - \\frac{V_s - V_0}{s + 1/(RC)}",
                        "hint": "The two terms sitting over $s$ are $(V_s - V_0)/s$ and $V_0/s$. They add to something simpler than either.",
                        "deconstruct": [
                            "$\\dfrac{V_s - V_0}{s} + \\dfrac{V_0}{s} = \\dfrac{V_s}{s}$ — the initial condition has vanished from this term entirely.",
                            "$\\dfrac{-RC(V_s-V_0)}{1+sRC} = \\dfrac{-(V_s-V_0)}{s + 1/(RC)}$ after dividing through by $RC$.",
                            "So the pole is at $s = -1/(RC)$ whatever $V_0$ is, and $V_0$ only appears in that term's numerator.",
                        ],
                    },
                    {
                        "prompt": "Invert term by term, using $1/s \\to 1$ and $1/(s+a) \\to e^{-at}$. Write $v_c(t)$ in terms of $V_s$, $V_0$, $t$, $R$ and $C$.",
                        "answer": "V_s - (V_s - V_0)e^{-t/(RC)}",
                        "hint": "The first term is a constant. The second is a decaying exponential whose rate is the pole position with the sign flipped.",
                        "deconstruct": [
                            "$\\dfrac{V_s}{s} \\to V_s$, a constant.",
                            "$\\dfrac{V_s - V_0}{s + 1/(RC)} \\to (V_s - V_0)e^{-t/(RC)}$, and it is being subtracted.",
                            "Check both ends: at $t = 0$ this gives $V_s - (V_s - V_0) = V_0$, and as $t \\to \\infty$ it gives $V_s$.",
                        ],
                    },
                ],
                "closing": r'''
Compare that with the shortcut from the reading:
$x(t) = x(\infty) + \big(x(0^+) - x(\infty)\big)e^{-t/\tau}$. It is the same formula.
$V_s$ is $x(\infty)$, $V_0$ is $x(0^+)$, and $-(V_s - V_0)$ is
$x(0^+) - x(\infty)$ with the sign folded in.

Two things are worth taking away from where each symbol ended up. The pole is at
$-1/(RC)$ and $V_0$ is nowhere near it — the initial charge sets the *size* of the
exponential and never its rate, which is the general fact that initial conditions move
residues and not poles. And setting $V_0 = 0$ collapses everything to
$V_s(1 - e^{-t/RC})$, the module 1 answer, which is the check that no step above quietly
lost a term.
''',
            },
            "quiz": {
                "title": "Stored energy, and where it enters the algebra",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A capacitor $C$ holding $v_0$ volts at $t = 0^-$ appears in the s-domain as:",
                        "opts": [
                            "an impedance $1/(sC)$ alone; the initial voltage is added to the answer at the end",
                            "an impedance $sC$ in series with a source $Cv_0$",
                            "a short circuit",
                            "an impedance $1/(sC)$ in series with a voltage source $v_0/s$",
                        ],
                        "a": 3,
                        "why": r'''
$I(s) = sCV(s) - Cv_0$ rearranges to $V = I/(sC) + v_0/s$: the impedance you already
know, plus the initial voltage entering as a source, because the transform of a
constant $v_0$ is $v_0/s$. Adding the initial voltage to the finished answer instead is
the habit the transform exists to remove — the initial condition is one of the things
*driving* the response, so it has to be present while the algebra is done, not bolted
on afterwards. $sC$ is the admittance rather than the impedance. And a charged
capacitor is not a short — a short holds its terminals at zero, while this one holds
them at $v_0$ — but it is not an open circuit either: $1/(sC)$ falls away as $s$ grows,
so at the switching instant the pair behaves as a source of $v_0$ with nothing in
series to stop current flowing. That is why the unit above draws 6 mA at $t = 0^+$
rather than none.
''',
                    },
                    {
                        "q": "An inductor $L$ carrying $i_0$ amps at $t = 0^-$ appears as:",
                        "opts": [
                            "an impedance $sL$ in series with a voltage source $Li_0$",
                            "an impedance $sL$ in series with a voltage source $Li_0/s$",
                            "an impedance $1/(sL)$ in parallel with a current source $i_0$",
                            "an impedance $sL$ alone",
                        ],
                        "a": 0,
                        "why": r'''
$\mathcal{L}\{L\,di/dt\} = sLI(s) - Li_0$, so the source is the constant $Li_0$ with no
further division by $s$. The units settle it: $L i_0$ is webers, which is volt-seconds,
and volt-seconds is exactly what an s-domain voltage is measured in. Dividing by $s$ as
well would describe a flux that keeps on being applied rather than one that was already
there. Dropping the term entirely is the same error as dropping $f(0)$ from the
derivative rule, and it silently asserts that the inductor started empty.
''',
                    },
                    {
                        "q": "A circuit has been sitting undisturbed for a long time before a switch moves. Just before it moves:",
                        "opts": [
                            "both are open circuits",
                            "the inductor is an open circuit and the capacitor a short circuit",
                            "the inductor is a short circuit and the capacitor an open circuit",
                            "both are short circuits",
                        ],
                        "a": 2,
                        "why": r'''
Undisturbed for a long time means nothing is changing, so $v_L = L\,di/dt = 0$ — an
inductor with no voltage across it is a short — and $i_C = C\,dv/dt = 0$ — a capacitor
with no current through it is an open. That is the whole of the first step of any
switching problem: redraw with those two substitutions, solve the resistive circuit, and
read off $i_L(0^-)$ and $v_C(0^-)$. Those two numbers are all you need, because they are
the two quantities that cannot jump when the switch moves.
''',
                    },
                    {
                        "q": "Which of these may jump discontinuously at the instant a switch closes?",
                        "opts": [
                            "the current through a capacitor",
                            "the voltage across a capacitor",
                            "the current through an inductor",
                            "the energy stored in an inductor",
                        ],
                        "a": 0,
                        "why": r'''
A capacitor's current jumps routinely — to whatever the rest of the circuit will supply
at that instant, which is why the current into a discharged capacitor at switch-on is
limited only by the series resistance. Its *voltage* cannot jump, because
$i = C\,dv/dt$ would demand infinite current. An inductor is the mirror image: its
current cannot jump, and since the stored energy is $\tfrac{1}{2}Li^2$, the energy
cannot jump either.
''',
                    },
                    {
                        "q": "A circuit has an initially charged capacitor *and* a step input applied at $t=0$. The total response is:",
                        "opts": [
                            "the response to the step only, since the initial charge decays away",
                            "the response to the initial charge plus the response to the step, each worked out with the other set to zero",
                            "the product of the two responses",
                            "not obtainable without solving the differential equation directly",
                        ],
                        "a": 1,
                        "why": r'''
Superposition, which is available because the circuit is linear and the initial
condition has been turned into an ordinary source. The first piece is the
**zero-input** response and the second the **zero-state** response, and the two are
added. Both contain the same exponentials, because both are shaped by the same poles —
the initial charge changes the *size* of each term and never its time constant. Saying
the initial charge decays away is true eventually and useless at $t=0$, which is
precisely the region the transform was brought in to handle.
''',
                    },
                ],
            },
        },

        # ---- M5 -----------------------------------------------------------
        {
            "title": "The second-order step response",
            "summary": "Complete the square and the transform hands back a decaying sinusoid. Differentiate that once and out come the overshoot and the peak time a specification is written in.",
            "concepts": [
                "For $\\zeta < 1$ the denominator has no real roots, so completing the square is the way in: $s^2 + 2\\zeta\\omega_n s + \\omega_n^2 = (s + \\zeta\\omega_n)^2 + \\omega_d^2$ with $\\omega_d = \\omega_n\\sqrt{1-\\zeta^2}$. The step response is then $y(t) = 1 - e^{-\\zeta\\omega_n t}\\left(\\cos\\omega_d t + \\frac{\\zeta}{\\sqrt{1-\\zeta^2}}\\sin\\omega_d t\\right)$.",
                "Three regimes, three shapes. $\\zeta < 1$ rings at $\\omega_d$ inside an envelope $e^{-\\zeta\\omega_n t}$; $\\zeta = 1$ is a repeated pole and gives $1 - (1+\\omega_n t)e^{-\\omega_n t}$, the fastest response with no overshoot at all; $\\zeta > 1$ has two real poles and is dominated by the slower of them.",
                "**Overshoot depends on $\\zeta$ alone**: $M_p = e^{-\\pi\\zeta/\\sqrt{1-\\zeta^2}}$, which is 16.3% at $\\zeta = 0.5$, 9.5% at $\\zeta = 0.6$ and 4.3% at $\\zeta = 0.707$. Making a circuit faster does not make it ring more — $\\omega_n$ is nowhere in that formula.",
                "The other three numbers a specification uses: the peak arrives at $t_p = \\pi/\\omega_d$; the response first reaches its final value at $t_r = (\\pi - \\arccos\\zeta)/\\omega_d$; and it settles inside 2% after roughly $t_s = 4/(\\zeta\\omega_n)$, because the envelope is $e^{-\\zeta\\omega_n t}$ and $e^{-4} = 0.018$.",
                "So a specification is a region of the s-plane. A maximum overshoot is a maximum angle from the negative real axis, since $\\zeta = \\cos\\theta$; a maximum settling time is a vertical line the poles must sit to the left of; a maximum peak time is a minimum height above the real axis. Designing to a specification means putting the pair in the region where all of them hold.",
            ],
            "read": [
                {
                    "title": "Why a circuit overshoots, and what sets how far",
                    "minutes": 14,
                    "body": r'''
An RC circuit charging towards 5 V never reaches 5.1 V. It cannot. The only thing
pushing charge onto the capacitor is the difference between the supply voltage and the
voltage already on the plate, and once that difference has gone to zero the pushing
stops. The approach is one-sided, always from below, and it slows down exactly as it
runs out of reason to continue.

Put an inductor in the same path — the same supply, the same capacitor, the same
resistor — and the capacitor voltage goes to 6.86 V before it comes back. It is worth
being clear that this is not an artefact of anything. No energy has been created; the
circuit contains nothing but three passive parts and a 5 V supply. Something in the
circuit is nevertheless capable of driving the output past the supply that feeds it,
and the whole of this module is downstream of understanding what.

## Two stores, and the one that will not stop

A capacitor's state is its voltage. Its defining rule, $i = C\,dv/dt$, says that
changing that voltage requires current, and a finite current can only change it at a
finite rate — so $v_C$ cannot jump. An inductor's state is its current, and its rule
$v = L\,di/dt$ says the mirror image: a finite voltage can only change the current at a
finite rate, so $i_L$ cannot jump either.

In an RC circuit there is one state, so there is one thing that has to be told where to
go and one exponential to take it there. In an RLC circuit there are two, and they are
coupled: the current sets how fast the voltage rises, and the voltage sets how fast the
current falls. That coupling is the whole story.

Follow it once around the loop. At switch-on the capacitor is empty, so almost all of
the supply appears across the inductor, and the current climbs. The climbing current
charges the capacitor. As the capacitor fills, less voltage is left over for the
inductor, so the current stops climbing — but it is still *there*, and it is still
pushing charge in. At the instant the capacitor reaches 5 V there is nothing left across
the inductor at all, so the current has stopped growing, and it is at that moment
running at 27.7 mA. That current cannot go to zero instantly; the inductor will not let
it. So charge keeps arriving at a capacitor that is already full, and the voltage goes
past the supply.

The mechanical picture is the same one and is worth carrying: a mass on a spring with a
damper. The spring is the capacitor (it stores displacement), the mass is the inductor
(it stores momentum), and the damper is the resistor. Release the mass and it does not
creep to its new resting place; it arrives with speed and overshoots, and the damper is
the only thing that stops it doing so forever.

## The equation the loop writes down

Round the series loop, with $v_s$ the supply and $v$ the capacitor voltage,

$$L\frac{di}{dt} + Ri + v = v_s,\qquad i = C\frac{dv}{dt}$$

Substituting the second into the first gives one equation in one unknown:

$$LC\,\ddot v + RC\,\dot v + v = v_s
\qquad\Longleftrightarrow\qquad
\ddot v + \frac{R}{L}\dot v + \frac{1}{LC}v = \frac{1}{LC}v_s$$

Every second-order system in engineering is written in one standard form so that results
proved once can be reused everywhere:

$$\ddot y + 2\zeta\omega_n\dot y + \omega_n^2 y = \omega_n^2 u$$

Comparing coefficients term by term is the entire derivation of the two numbers this
module is about:

$$\omega_n = \frac{1}{\sqrt{LC}},
\qquad 2\zeta\omega_n = \frac{R}{L}
\ \Longrightarrow\ \zeta = \frac{R}{2}\sqrt{\frac{C}{L}}$$

The same two numbers drop out of the $s$-domain in one line, which is the route to
prefer once you trust it. The divider rule with impedances gives

$$H(s) = \frac{1/sC}{R + sL + 1/sC} = \frac{1}{LCs^2 + RCs + 1}
       = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$$

## What the two numbers actually are

$\omega_n$ is the frequency at which $L$ and $C$ would trade energy back and forth if the
resistor were not there — the loop's own frequency, set by the storage elements alone.

$\zeta$ is subtler and it is where the marks go. Notice that

$$\zeta = \frac{R}{2\sqrt{L/C}} = \frac{R}{2Z_0},
\qquad Z_0 \equiv \sqrt{L/C}$$

$Z_0$ is a resistance built out of the two *storage* elements, called the characteristic
impedance of the pair. Damping is not a property of the resistor. It is the resistor
measured against $Z_0$. A 60 Ω resistor is heavy damping in a loop whose $Z_0$ is 20 Ω
and barely any at all in one whose $Z_0$ is 2 kΩ, and the resistor cannot tell which it
is in.

## Three shapes, and the poles behind them

The denominator's roots are

$$s = -\zeta\omega_n \pm \omega_n\sqrt{\zeta^2 - 1}$$

and the sign of $\zeta^2 - 1$ is what decides the shape of everything that follows.

- $\zeta < 1$ — **underdamped.** The square root is imaginary, the roots are a complex
  pair at $-\sigma \pm j\omega_d$ with $\sigma = \zeta\omega_n$ and
  $\omega_d = \omega_n\sqrt{1-\zeta^2}$, and the response rings at $\omega_d$ inside an
  envelope $e^{-\sigma t}$.
- $\zeta = 1$ — **critically damped.** One repeated real root at $-\omega_n$. No
  overshoot, and the fastest approach available without any.
- $\zeta > 1$ — **overdamped.** Two real roots, one of them slow. The slow one dominates
  and the circuit crawls.

Note that both roots always sit the same distance $\omega_n$ from the origin while
$\zeta < 1$: increasing the damping slides the pair around a circle of radius $\omega_n$
towards the negative real axis, where the two halves meet at $\zeta = 1$ and then split
apart along it.

## The response itself

For the underdamped case, completing the square in the denominator matches it to the
standard sine and cosine transform pairs, and the guided derivation in this module works
that through. The result is the one line worth carrying:

$$y(t) = V\left[1 - e^{-\sigma t}\left(\cos\omega_d t
        + \frac{\zeta}{\sqrt{1-\zeta^2}}\sin\omega_d t\right)\right]$$

$V$ is the final value; the bracket starts at 1 and decays.

## Worked: 5 V into 10 mH, 60 Ω and 1 µF

Everything above, on real parts. Get the two numbers first, always.

```
wn    = 1/sqrt(L C)   = 1/sqrt(0.01 * 1e-6) = 1/1.0e-4      = 10 000 rad/s
                                                            = 1591.5 Hz
Z0    = sqrt(L/C)     = sqrt(0.01/1e-6) = sqrt(10 000)       = 100.0 ohm
zeta  = R/(2 Z0)      = 60/200                               = 0.3000
sigma = zeta * wn     = 0.3 * 10000                          = 3000 /s
wd    = wn sqrt(1-zeta^2)  = 10000 * sqrt(0.91)
                           = 10000 * 0.9539392               = 9539.39 rad/s
B     = zeta/sqrt(1-zeta^2) = 0.3/0.9539392                  = 0.314485
```

Take one instant, $t = 0.20$ ms, all the way through:

```
sigma t = 3000 * 2.0e-4  = 0.600000     e^(-0.600000) = 0.548812
wd t    = 9539.39 * 2.0e-4 = 1.907878 rad = 109.31 degrees
          cos(1.907878) = -0.330735
          sin(1.907878) = +0.943724

bracket = -0.330735 + 0.314485 * 0.943724
        = -0.330735 + 0.296785                        = -0.033950

y       = 5 * (1 - 0.548812 * (-0.033950))
        = 5 * (1 + 0.018632)                          = 5.0932 V
```

Two-tenths of a millisecond in and the output is already above the 5 V supply. Now the
peak. It arrives when the derivative first returns to zero, which the derivation shows is
at $t_p = \pi/\omega_d$:

```
tp   = pi/wd = 3.141593/9539.39                       = 3.29328e-4 s
                                                      = 0.32933 ms

at that instant wd t = pi exactly, so cos = -1 and sin = 0:

e^(-sigma tp) = e^(-3000 * 3.29328e-4) = e^(-0.987985) = 0.372326
y(tp)  = 5 * (1 - 0.372326 * (-1)) = 5 * 1.372326     = 6.8616 V
```

The excess over the final value is $0.372326 \times 5 = 1.8616$ V, or **37.23%** — and
that fraction, $e^{-\sigma t_p}$, has both $\omega_n$'s cancelled out of it and depends on
$\zeta$ alone.

The later extrema are free, because each half-cycle multiplies the envelope by the same
factor:

```
n   t = n pi/wd     y            excess
1   0.32933 ms      6.8616 V     +37.23 %
2   0.65866 ms      4.3069 V     -13.86 %
3   0.98798 ms      5.2581 V      +5.16 %
4   1.31731 ms      4.9039 V      -1.92 %
5   1.64664 ms      5.0358 V      +0.72 %
```

Each excess is $0.37233$ times the one before it. Four visible excursions and the thing
is inside 1%.

## Worked: the same L and C, three different resistors

$\zeta = R/(2Z_0) = R/200$ here, so the resistor alone moves the damping and $\omega_n$
never moves at all.

```
R = 60 ohm   zeta = 0.30   underdamped   peaks at 6.86 V
R = 200 ohm  zeta = 1.00   critical      no overshoot
R = 400 ohm  zeta = 2.00   overdamped    no overshoot
```

The critical case has a repeated pole, so its step response carries a $te^{-\omega_n t}$
term as well as a plain exponential:

```
y(t) = 5 [ 1 - (1 + wn t) e^(-wn t) ]

at t = 0.40 ms :  wn t = 10000 * 4.0e-4                 = 4.000000
                  e^(-4) = 0.018316
                  (1 + 4) * 0.018316                    = 0.091578
                  y = 5 * (1 - 0.091578)                = 4.5421 V
```

and it enters the 2% band — reaches 4.90 V and stays there — when
$(1+x)e^{-x} = 0.02$, at $x = \omega_n t = 5.8339$, so at $t = 0.583$ ms.

The overdamped case has real poles at
$\omega_n(-\zeta \pm \sqrt{\zeta^2-1}) = 10^4(-2 \pm \sqrt3)$, that is $-2679.5$ and
$-37320.5$. The fast one is gone in 27 µs; the slow one has a time constant of
$1/2679.5 = 373$ µs and it is what you actually watch. It enters the 2% band at 1.488 ms.

Line those three up:

```
R = 60 ohm    zeta = 0.30   inside 2% from 1.123 ms   (after ringing to 6.86 V)
R = 200 ohm   zeta = 1.00   inside 2% from 0.583 ms
R = 400 ohm   zeta = 2.00   inside 2% from 1.488 ms
```

Settling is worst at *both* ends. Too little damping and it rings for a long time; too
much and the slow real pole drags. The minimum sits a little below critical, which is
why real designs cluster around $\zeta = 0.6$ to $0.7$ rather than at either extreme.

## The mistake people actually make

**Believing a bigger step overshoots more.** It is a tempting mistake because a bigger
step obviously produces a bigger excess *in volts* — 10 V in gives 3.72 V of excess here
instead of 1.86 V. But the circuit is linear, so doubling the input doubles the final
value too, and the *fraction* is untouched. Overshoot is a percentage for exactly this
reason.

**Reading the damping off the resistor.** $\zeta$ is $R/(2Z_0)$, and $Z_0$ moves when $L$
or $C$ moves. Change $C$ from 1 µF to 100 nF in the worked example above and $Z_0$ goes
from 100 Ω to 316 Ω, so the same 60 Ω resistor now gives $\zeta = 0.095$ and 74%
overshoot. The resistor did not move. Nothing about the resistor changed.

**Treating $t_s = 4/(\zeta\omega_n)$ as exact.** It is the *envelope* crossing 2%, and the
response only touches its envelope at the peaks. Here the envelope estimate says 1.333 ms
and the response actually stops leaving the band at 1.123 ms. The estimate is good to
within a fraction of a ring period, which is all anyone needs it for, but do not quote it
to four figures off a scope.

**Confusing $\omega_n$ with the frequency you can see.** The ringing you measure is at
$\omega_d$, not $\omega_n$. At $\zeta = 0.3$ they differ by 5%, which hides inside the
noise; at $\zeta = 0.8$ they differ by 40%, and identifying $\omega_n$ from a ringing
period without correcting for $\zeta$ puts the poles in the wrong place.

## Where this stops holding

- **Two poles, and no zeros.** Everything above describes
  $\omega_n^2/(s^2+2\zeta\omega_n s+\omega_n^2)$ and nothing else. Move the probe to the
  resistor of the same loop and the transfer function grows a zero at the origin, its
  final value becomes zero, and the word "overshoot" stops meaning anything. A zero in
  the left half-plane near the poles increases the overshoot beyond what $\zeta$ predicts;
  a zero in the right half-plane makes the response set off in the *wrong direction*
  first. Neither is covered by $M_p = e^{-\pi\zeta/\sqrt{1-\zeta^2}}$.
- **$\zeta \ge 1$.** There is no peak, so $t_p$ and $M_p$ do not exist —
  $\sqrt{1-\zeta^2}$ is not real, and a calculator returning NaN is telling you something
  true.
- **More than two energy stores.** Three independent storage elements give three poles,
  and the neat picture survives only as an approximation: if one complex pair sits much
  closer to the imaginary axis than everything else, it dominates and the second-order
  numbers are close. "Much closer" conventionally means a factor of about five. Nearer
  than that and the extra poles show up as a response that settles more slowly than
  $4/(\zeta\omega_n)$ promised.
- **Anything that saturates.** An amplifier that clips, or an inductor whose core
  saturates at 30 mA when the ringing wants 34, is not linear, and superposition — which
  is what let us write one transfer function at all — has gone.
''',
                },
                {
                    "title": "A specification is a region of the s-plane",
                    "minutes": 13,
                    "body": r'''
A specification arrives written in the language of an oscilloscope. *Settled to within
2% in under 2 ms. No more than 10% overshoot.* It does not mention $L$, or $R$, or a
pole, or $s$. Somebody still has to turn it into three component values, and somebody
else — often the same person a fortnight later — has to look at a measured curve and say
whether it was met.

Both directions are the same short piece of geometry, run forwards and backwards. This
unit is that geometry.

## The four numbers, and where each comes from

Differentiating the underdamped step response once and setting the result to zero
produces every number a specification is written in. The derivation unit in this module
does the algebra; these are its results.

$$M_p = e^{-\pi\zeta/\sqrt{1-\zeta^2}}
\qquad t_p = \frac{\pi}{\omega_d}
\qquad t_r = \frac{\pi - \arccos\zeta}{\omega_d}
\qquad t_s \approx \frac{4}{\zeta\omega_n}$$

$M_p$ is the fractional overshoot, measured against the **final value**. $t_p$ is when
the peak arrives. $t_r$ is when the response first reaches its final value on the way up.
$t_s$ is when the ringing has shrunk inside a 2% band, and it is approximate because it
is really a statement about the envelope $e^{-\zeta\omega_n t}$ and $e^{-4} = 0.0183$.

Look at what each one depends on, because that is the useful part:

```
Mp   depends on   zeta                only
tp   depends on   wd                  only
ts   depends on   zeta * wn = sigma   only
tr   depends on   both
```

## The pole as a point, and the four numbers as its coordinates

An underdamped pair sits at $s = -\sigma \pm j\omega_d$. Give that point polar
coordinates measured from the negative real axis and everything lines up:

- its **distance from the origin** is
  $\sqrt{\sigma^2+\omega_d^2} = \omega_n$;
- its **distance from the imaginary axis** is $\sigma = \zeta\omega_n$;
- its **height above the real axis** is $\omega_d$;
- and the **angle** $\theta$ between it and the negative real axis has
  $\cos\theta = \sigma/\omega_n = \zeta$.

That last line is the one to memorise. $\zeta$ is a cosine of an angle, so the whole
overshoot question is a question about direction, not distance. Slide a pole pair
straight out from the origin along a fixed ray and the response gets faster in exactly
the same proportion at every point, with an identically shaped curve — because $\zeta$
has not changed. That is the scaling property of module 3 seen in the plane.

## Each constraint carves out a region

```
"overshoot at most 10%"     ->  zeta >= 0.5912  ->  theta <= 53.76 deg
                                a WEDGE around the negative real axis

"settled within T"          ->  sigma >= 4/T
                                the half-plane LEFT of a vertical line

"peak no later than T"      ->  wd >= pi/T
                                ABOVE a horizontal line (and its mirror below)

"natural frequency 450-550 Hz"
                            ->  an ANNULUS between two circles centred on
                                the origin
```

A design carrying several of these at once has to land the pair where all the regions
overlap. Two of them, an overshoot limit and a settling limit, are the usual pair, and
they intersect in a wedge with its tip chopped off — unbounded, so there is always room,
and the only question is how far out you are willing to go.

## Worked: from a specification to three components

*No more than 10% overshoot; inside a 2% band within 2.0 ms. Series R-L-C, output taken
across the capacitor, and the parts bin has 1 µF capacitors in it.*

Take the constraints one at a time. Each fixes one coordinate.

```
overshoot -> damping

    Mp = 0.10 :  ln 0.10 = -2.302585 = -pi zeta/sqrt(1-zeta^2)
    so  zeta/sqrt(1-zeta^2) = 2.302585/pi          = 0.732936
    and zeta = 0.732936/sqrt(1 + 0.732936^2)
             = 0.732936/sqrt(1.537195)             = 0.5912

    take zeta = 0.600, a little inside the limit   (Mp = 9.478 %)

settling -> the real part

    ts = 4/(zeta wn) <= 2.0e-3  ->  sigma = zeta wn >= 2000 /s
    take sigma = 2000 exactly

the two together

    wn = sigma/zeta = 2000/0.600                   = 3333.3 rad/s
                                                   = 530.5 Hz
    wd = wn sqrt(1 - 0.36) = 3333.3 * 0.800        = 2666.7 rad/s
    poles at -2000 +/- j2666.7
```

Only now do components appear, and they appear in the order the two numbers dictate:
$\omega_n$ fixes the *product* $LC$, and $\zeta$ then fixes $R$.

```
LC = 1/wn^2 = 1/(3333.3^2)                         = 9.000e-8
with C = 1e-6 F :  L = 9.000e-8/1e-6               = 0.0900 H = 90 mH

Z0 = sqrt(L/C) = sqrt(0.09/1e-6) = sqrt(90 000)    = 300.0 ohm
R  = 2 zeta Z0 = 2 * 0.600 * 300.0                 = 360.0 ohm
```

and the check, which costs nothing and catches a slipped factor:

```
Mp = exp(-pi * 0.6/0.8) = exp(-2.356194)           = 0.09478 -> 9.48 %   ok
ts = 4/2000                                        = 2.000 ms           ok
tp = pi/2666.7                                     = 1.178 ms
```

Note what was free and what was not. $LC$ was pinned, but the *split* between $L$ and
$C$ was not: 100 nF and 0.9 H would have hit the same specification, with $Z_0$ three
times higher and $R$ three times higher to match. Choosing $C$ large and $L$ small keeps
$Z_0$ low, which keeps the resistor small — usually what you want, since a 0.9 H inductor
is a heavy, expensive, lossy object and a 90 mH one is merely awkward.

## Worked: from a measured curve back to the poles

The other direction, which is what a bench actually hands you. A scope shows a step
response settling at 4.00 V, with a first peak of 4.60 V arriving 0.50 ms after the edge.

```
overshoot, against the FINAL value, not the input

    Mp = (4.60 - 4.00)/4.00                        = 0.1500

damping, by inverting the overshoot formula

    ln Mp = -1.897120
    k  = -ln(Mp)/pi = 1.897120/3.141593            = 0.603872
    zeta = k/sqrt(1 + k^2)
         = 0.603872/sqrt(1.364662)
         = 0.603872/1.168188                       = 0.516931

    sqrt(1 - zeta^2) = sqrt(0.732781)              = 0.856027

the ringing frequency, from the peak time

    wd = pi/tp = 3.141593/5.00e-4                  = 6283.19 rad/s

and the natural frequency, corrected for the damping

    wn = wd/sqrt(1-zeta^2) = 6283.19/0.856027      = 7339.9 rad/s
                                                   = 1168.2 Hz
    sigma = zeta wn = 0.516931 * 7339.9            = 3794.2 /s

    poles at -3794 +/- j6283
```

Two readings off a screen and the model is complete. Everything else follows without
touching the circuit again: it should be inside 2% by $4/3794.2 = 1.05$ ms, and if you
want the components, pick a capacitor and the rest is forced.

```
with C = 100 nF :
    L = 1/(wn^2 C) = 1/(7339.9^2 * 1e-7) = 1/5.3875 = 0.18562 H = 186 mH
    R = 2 sigma L = 2 * 3794.2 * 0.18562             = 1408.5 ohm
```

That is the identification problem, done by hand on two numbers. The capstone of this
course does the same job by least squares on the whole curve, which is more robust to a
noisy trace but is not doing anything conceptually different.

## The mistake people actually make

**Measuring the overshoot against the wrong baseline.** The denominator of $M_p$ is the
final value of the *response*, not the input, and not zero. The temptation is strongest
when there is a divider in front of the circuit: drive a network through a 1 kΩ resistor
into a 1.5 kΩ shunt and the response settles at $0.6\times$ the supply, so a peak of
9.85 V after a 15 V step is a 9.5% overshoot of a 9 V final value. Measured against the
15 V that was applied, the same trace would not look like an overshoot at all — it never
reaches 15 V. Read the flat part of the trace first, always.

**Believing a faster circuit rings less.** $\omega_n$ does not appear in $M_p$. Scaling
every impedance to make the circuit ten times faster moves the poles ten times further
from the origin along the same ray, and the curve is the identical shape drawn on a
compressed time axis. If a prototype rings too much, the fix is the angle — which means
$R$ against $Z_0$ — and nothing else will do it.

**Reading a settling specification as a bandwidth specification.** They constrain
different coordinates. "Settled in 2 ms" is a constraint on $\sigma$, the *horizontal*
position, and says nothing about $\omega_n$ on its own; "corner at 500 Hz" is roughly a
constraint on $|s|$. A design can meet either while badly missing the other.

## Where this stops holding

- **Zeros.** All four formulas assume a numerator that is a constant. A zero at $-z$
  reasonably close to the pole pair adds overshoot on top of what $\zeta$ predicts, and a
  zero in the right half-plane makes the response dip the wrong way before it rises —
  behaviour no value of $\zeta$ produces. If a measured curve dips first, do not fit
  $\zeta$ to it.
- **Extra poles.** With a third pole at $-p$, the second-order numbers hold to within a
  few per cent while $p \gtrsim 5\sigma$, and progressively worse as it comes closer. The
  usual symptom is a settling time longer than predicted with the overshoot roughly
  right.
- **$\zeta \ge 1$.** No peak, so $M_p$ and $t_p$ do not exist and the wedge picture
  degenerates onto the real axis. Settling is then set by the slower of the two real
  poles, and $4/(\zeta\omega_n)$ overestimates how good things are.
- **The 2% band is a convention, not a law.** A 5% band gives $t_s \approx 3/\sigma$ and
  a 1% band $t_s \approx 4.6/\sigma$. A specification that says "settling time" without
  naming a band has not said anything yet, and the difference between the 2% and 1%
  answers is 15% of the number — enough to fail a test that would otherwise have passed.
''',
                },
            ],
            "blanks": [
                {
                    "title": "The standard form, and the four numbers read off it",
                    "minutes": 8,
                    "caption": "the second-order sheet: what each symbol is, and which coordinate of the pole it names",
                    "lang": "text",
                    "brief": r'''
Everything in this module is a consequence of one transfer function and one pole pair,
and it is worth having the whole sheet in front of you once with the gaps filled in
deliberately rather than copied.

Two of the blanks are the formulas themselves. The rest are the geometry — which
coordinate of the pole each formula is really talking about — and that is the half that
makes a specification translatable.
''',
                    "listing": """STANDARD SECOND-ORDER LOW-PASS

              wn^2
  H(s) = ------------------------ ,   0 < zeta < 1   (underdamped)
         s^2 + 2 zeta wn s + wn^2

  poles:   s = -sigma +/- j wd      with   sigma = zeta wn
                                           wd    = wn * ___

  step response, for a step of size V:

      y(t) = V [ 1 - e^(-sigma t) ( cos wd t + B sin wd t ) ]
      where B = ___

  ------------------------------------------------------------------------
  THE FOUR NUMBERS A SPECIFICATION IS WRITTEN IN

      overshoot     Mp  = exp( ___ )
      peak time     tp  = ___
      2% settling   ts ~= 4 / ___

  ------------------------------------------------------------------------
  WHAT EACH ONE IS SAYING ABOUT THE POLE

      the pole's distance from the origin is wn
      the pole's distance from the imaginary axis is sigma
      the pole's height above the real axis is wd

      the angle theta between the pole and the negative real axis
      satisfies  cos theta = ___

      so an overshoot limit is a limit on the ___ of that pole
""",
                    "blanks": [
                        {
                            "prompt": "The damped ringing frequency, in terms of wn and zeta.",
                            "hole": "?",
                            "opts": [
                                "sqrt(1 - zeta^2)",
                                "sqrt(1 + zeta^2)",
                                "sqrt(zeta^2 - 1)",
                                "(1 - zeta^2)",
                            ],
                            "a": 0,
                            "why": "$\\omega_d = \\omega_n\\sqrt{1-\\zeta^2}$. It comes straight out of completing the square: $(s+\\zeta\\omega_n)^2 + \\omega_d^2$ has to reproduce the constant term $\\omega_n^2$, and $(s+\\zeta\\omega_n)^2$ already supplies $\\zeta^2\\omega_n^2$ of it. Geometrically it is the height of the pole above the real axis, and it is always *below* $\\omega_n$ — the circuit rings more slowly than its undamped frequency.",
                            "whys": [
                                "$\\omega_d = \\omega_n\\sqrt{1-\\zeta^2}$. It comes straight out of completing the square: $(s+\\zeta\\omega_n)^2 + \\omega_d^2$ has to reproduce the constant term $\\omega_n^2$, and $(s+\\zeta\\omega_n)^2$ already supplies $\\zeta^2\\omega_n^2$ of it. Geometrically it is the height of the pole above the real axis, and it is always *below* $\\omega_n$ — the circuit rings more slowly than its undamped frequency.",
                                "This would make the ringing faster than the undamped frequency, which is backwards: damping can only slow the exchange of energy down. It also never becomes zero, so it would predict ringing at $\\zeta = 1$, where the response has no oscillation in it at all.",
                                "$\\sqrt{\\zeta^2-1}$ is real only for $\\zeta > 1$, and it is exactly the right expression *there* — it is the half-separation of the two real poles in the overdamped case. In the underdamped case it is imaginary, which is the algebra's way of saying the poles have left the real axis.",
                                "Dimensionally this is fine but numerically it is the square of the right thing, and it makes $\\omega_d$ collapse far too fast: at $\\zeta = 0.6$ it gives $0.64\\,\\omega_n$ where the truth is $0.80\\,\\omega_n$. The square root is what keeps the pole on a circle of radius $\\omega_n$.",
                            ],
                        },
                        {
                            "prompt": "The coefficient B on the sine term of the step response.",
                            "hole": "?",
                            "opts": [
                                "zeta/sqrt(1-zeta^2)",
                                "sqrt(1-zeta^2)/zeta",
                                "zeta",
                                "1/zeta",
                            ],
                            "a": 0,
                            "why": "$B = \\sigma/\\omega_d = \\zeta\\omega_n/(\\omega_n\\sqrt{1-\\zeta^2})$, and the $\\omega_n$ cancels. It is fixed by the fact that a second-order step response leaves the origin with zero slope: differentiating $1 - e^{-\\sigma t}(\\cos + B\\sin)$ at $t = 0$ gives $\\sigma - B\\omega_d$, and that has to vanish.",
                            "whys": [
                                "$B = \\sigma/\\omega_d = \\zeta\\omega_n/(\\omega_n\\sqrt{1-\\zeta^2})$, and the $\\omega_n$ cancels. It is fixed by the fact that a second-order step response leaves the origin with zero slope: differentiating $1 - e^{-\\sigma t}(\\cos + B\\sin)$ at $t = 0$ gives $\\sigma - B\\omega_d$, and that has to vanish.",
                                "This is the reciprocal, $\\omega_d/\\sigma$, which is the tangent of the pole angle rather than its cotangent. It blows up as $\\zeta \\to 0$, whereas the true $B$ goes to zero there — and it must, because an undamped circuit rings as a pure cosine with no sine term at all.",
                                "A bare $\\zeta$ is right to within a per cent for very light damping, since $\\sqrt{1-\\zeta^2} \\approx 1$ there, and that is exactly why the slip survives: it is half a per cent low at $\\zeta = 0.1$ and 13% low at $\\zeta = 0.5$.",
                                "This diverges as the damping goes to zero, which is the wrong direction, and it is not even dimensionless in the way the cosine's coefficient of 1 forces $B$ to be comparable with.",
                            ],
                        },
                        {
                            "prompt": "The exponent in the overshoot formula.",
                            "hole": "?",
                            "opts": [
                                "-pi zeta / sqrt(1-zeta^2)",
                                "-pi zeta",
                                "-pi zeta wn",
                                "-zeta / sqrt(1-zeta^2)",
                            ],
                            "a": 0,
                            "why": "$M_p = e^{-\\sigma t_p}$ with $t_p = \\pi/\\omega_d$, so the exponent is $-\\zeta\\omega_n \\cdot \\pi/(\\omega_n\\sqrt{1-\\zeta^2})$ and the $\\omega_n$ cancels. That cancellation is the headline result of the module: overshoot depends on the damping and on nothing else.",
                            "whys": [
                                "$M_p = e^{-\\sigma t_p}$ with $t_p = \\pi/\\omega_d$, so the exponent is $-\\zeta\\omega_n \\cdot \\pi/(\\omega_n\\sqrt{1-\\zeta^2})$ and the $\\omega_n$ cancels. That cancellation is the headline result of the module: overshoot depends on the damping and on nothing else.",
                                "Close, and it is the right answer in the limit of light damping — but it drops the correction that makes the overshoot vanish as $\\zeta \\to 1$. At $\\zeta = 0.5$ it predicts 21% where the truth is 16.3%, and at $\\zeta = 0.9$ it predicts 6% where the truth is 0.15%.",
                                "Any $\\omega_n$ in this exponent is a red flag, and not only because the units are wrong. It would say that a circuit rings further past its target simply for being fast, and the scaling property says the opposite: rescaling time cannot change the shape of a curve.",
                                "Losing the $\\pi$ makes the overshoot far too large — 73% instead of 37% at $\\zeta = 0.3$. The $\\pi$ arrives from the peak time, because the peak is half a ring period after the start.",
                            ],
                        },
                        {
                            "prompt": "The time at which the response peaks.",
                            "hole": "?",
                            "opts": ["pi/wd", "pi/wn", "2 pi/wd", "1/wd"],
                            "a": 0,
                            "why": "The derivative simplifies to a constant times $e^{-\\sigma t}\\sin\\omega_d t$, and an exponential is never zero, so the peak is at the sine's first positive zero: $\\omega_d t = \\pi$. Half a ring period, not a whole one.",
                            "whys": [
                                "The derivative simplifies to a constant times $e^{-\\sigma t}\\sin\\omega_d t$, and an exponential is never zero, so the peak is at the sine's first positive zero: $\\omega_d t = \\pi$. Half a ring period, not a whole one.",
                                "The response rings at $\\omega_d$, not at $\\omega_n$, so this arrives too early — by 5% at $\\zeta = 0.3$ and by 40% at $\\zeta = 0.8$. Using $\\omega_n$ here is the standard way of putting an identified pole in the wrong place.",
                                "$2\\pi/\\omega_d$ is a full ring period, which lands on the first *trough* rather than the first peak. On the worked circuit in this module that is 0.659 ms, where the response is 4.31 V — below its final value, not above it.",
                                "Dropping the $\\pi$ has no justification in the algebra and gives a time about three times too early, when the response is still climbing steeply.",
                            ],
                        },
                        {
                            "prompt": "What goes underneath the 4 in the settling-time estimate.",
                            "hole": "?",
                            "opts": ["zeta wn", "wn", "wd", "zeta"],
                            "a": 0,
                            "why": "The ringing lives inside an envelope $e^{-\\zeta\\omega_n t}$, and $e^{-4} = 0.0183$, just under 2%. So the settling estimate is four time constants of that envelope, and $\\zeta\\omega_n$ — the real part of the pole, its distance from the imaginary axis — is what the time constant is built from.",
                            "whys": [
                                "The ringing lives inside an envelope $e^{-\\zeta\\omega_n t}$, and $e^{-4} = 0.0183$, just under 2%. So the settling estimate is four time constants of that envelope, and $\\zeta\\omega_n$ — the real part of the pole, its distance from the imaginary axis — is what the time constant is built from.",
                                "$\\omega_n$ is the pole's distance from the *origin*, and two pole pairs at the same distance from the origin can settle ten times apart: at $\\omega_n = 1000$ rad/s, $\\zeta = 0.1$ takes 40 ms and $\\zeta = 0.9$ takes 4.4 ms.",
                                "$\\omega_d$ decides how fast the response rings, which is a different question from how fast the ringing dies. A pair at $-1 \\pm j100$ oscillates furiously and takes four seconds to settle.",
                                "$\\zeta$ alone is dimensionless, so $4/\\zeta$ is not a time at all. The units are the fastest check available on any of these formulas and they cost nothing to run.",
                            ],
                        },
                        {
                            "prompt": "The cosine of the angle between the pole and the negative real axis.",
                            "hole": "?",
                            "opts": ["zeta", "wd/wn", "zeta wn", "sqrt(1-zeta^2)"],
                            "a": 0,
                            "why": "The pole sits at $-\\zeta\\omega_n \\pm j\\omega_d$, at distance $\\omega_n$ from the origin, so the adjacent side of the triangle is $\\zeta\\omega_n$ and the hypotenuse is $\\omega_n$: the cosine is $\\zeta$. That single fact is what turns an overshoot specification into a wedge in the s-plane.",
                            "whys": [
                                "The pole sits at $-\\zeta\\omega_n \\pm j\\omega_d$, at distance $\\omega_n$ from the origin, so the adjacent side of the triangle is $\\zeta\\omega_n$ and the hypotenuse is $\\omega_n$: the cosine is $\\zeta$. That single fact is what turns an overshoot specification into a wedge in the s-plane.",
                                "$\\omega_d/\\omega_n$ is the opposite side over the hypotenuse, so it is the *sine* of that angle, not the cosine. It equals $\\sqrt{1-\\zeta^2}$, which is the same quantity written the other way round.",
                                "This is the length of the adjacent side, not a ratio, so it has units of rad/s and cannot be a cosine of anything. Dividing it by $\\omega_n$ is the missing step.",
                                "This is the sine of the angle again, in its other spelling. If you reached for it, you have the triangle right and the two sides swapped — worth fixing carefully, because it flips the direction of every specification: a *maximum* overshoot is a *maximum* angle and therefore a *minimum* $\\zeta$.",
                            ],
                        },
                        {
                            "prompt": "Which feature of the pole an overshoot limit constrains.",
                            "hole": "?",
                            "opts": [
                                "angle",
                                "distance from the origin",
                                "distance from the imaginary axis",
                                "height above the real axis",
                            ],
                            "a": 0,
                            "why": "Overshoot depends on $\\zeta$ alone and $\\zeta = \\cos\\theta$, so the constraint is purely directional: the poles must lie inside a wedge of half-angle $\\arccos\\zeta_{\\min}$ around the negative real axis, and they may sit anywhere along it. Ten per cent overshoot is a wedge of 53.8°.",
                            "whys": [
                                "Overshoot depends on $\\zeta$ alone and $\\zeta = \\cos\\theta$, so the constraint is purely directional: the poles must lie inside a wedge of half-angle $\\arccos\\zeta_{\\min}$ around the negative real axis, and they may sit anywhere along it. Ten per cent overshoot is a wedge of 53.8°.",
                                "Distance from the origin is $\\omega_n$, and a bound on it is a circle. That constrains how *fast* the circuit is and says nothing whatever about the shape of the response — which is the whole content of the fact that $\\omega_n$ does not appear in $M_p$.",
                                "Distance from the imaginary axis is $\\sigma = \\zeta\\omega_n$, and a bound on it is a vertical line. That is a settling-time specification, and it is a different constraint: a pole pair can sit far to the left, settling quickly, and still ring badly on the way.",
                                "Height above the real axis is $\\omega_d$, and a bound on it is a horizontal line. That is a peak-time specification — and note the sense reverses, since $t_p = \\pi/\\omega_d$ means a *maximum* peak time forces a *minimum* height.",
                            ],
                        },
                    ],
                },
                {
                    "title": "A specification turned into two components, line by line",
                    "minutes": 10,
                    "caption": "overshoot no more than 4.3%, settled inside 2% within 2.0 ms, and a 1 µF capacitor to build it around",
                    "lang": "text",
                    "brief": r'''
The design direction, worked in the order the algebra forces. Each behavioural number
fixes one coordinate of the pole pair, and only then do component values appear —
$\omega_n$ pins the *product* $LC$, and $\zeta$ pins $R$ against whatever $L$ and $C$ you
then chose.

The numbers here are deliberately round: 4.3% overshoot is $\zeta = 1/\sqrt2$ exactly,
which puts the poles on a 45° line, so $\sigma$ and $\omega_d$ come out equal and every
check can be done in your head.
''',
                    "listing": """SPEC   overshoot no more than 4.3 %
       settled inside a 2 % band within 2.0 ms
       series R-L-C, output across C, and C is fixed at 1 uF

  1. overshoot -> damping

         Mp = exp(-pi zeta/sqrt(1-zeta^2)) = 0.0432 = e^(-pi)
         which happens when the exponent is exactly -pi, i.e. when
         zeta = sqrt(1-zeta^2).   So   zeta = ___

  2. settling -> the real part of the pole

         ts = 4/(zeta wn) = 2.0e-3 s     so   sigma = zeta wn = ___ /s

  3. the two together fix the pole pair

         wn = sigma/zeta = 2000/0.7071                    = 2828 rad/s
         wd = wn sqrt(1-zeta^2) = 2828 * 0.7071           = 2000 rad/s
         so the poles sit at ___

  4. wn -> the product L C

         wn = 1/sqrt(LC)   ->   LC = 1/wn^2 = 1/8.00e6    = 1.25e-7
         with C = 1e-6 F this makes   L = ___

  5. zeta -> the resistor, measured against Z0 = sqrt(L/C)

         Z0 = sqrt(0.125/1e-6) = sqrt(125 000)            = ___
         R  = 2 zeta Z0 = 2 * 0.7071 * that               = 500 ohm

  6. check, in the time domain, before anything is soldered

         tp = pi/wd = 3.141593/2000                       = ___
""",
                    "blanks": [
                        {
                            "prompt": "The damping ratio that gives exactly 4.3% overshoot.",
                            "hole": "?",
                            "opts": ["0.7071", "0.5000", "0.0432", "1.4142"],
                            "a": 0,
                            "why": "Setting $\\zeta = \\sqrt{1-\\zeta^2}$ gives $2\\zeta^2 = 1$, so $\\zeta = 1/\\sqrt2 = 0.7071$, and the exponent collapses to $-\\pi$: $M_p = e^{-\\pi} = 0.0432$. This is the Butterworth value, and it is also the damping at which the frequency response stops having a peak — the two facts are the same fact seen from two domains.",
                            "whys": [
                                "Setting $\\zeta = \\sqrt{1-\\zeta^2}$ gives $2\\zeta^2 = 1$, so $\\zeta = 1/\\sqrt2 = 0.7071$, and the exponent collapses to $-\\pi$: $M_p = e^{-\\pi} = 0.0432$. This is the Butterworth value, and it is also the damping at which the frequency response stops having a peak — the two facts are the same fact seen from two domains.",
                                "$\\zeta = 0.5$ is a livelier response: 16.3% overshoot, close to four times the budget here. It is a perfectly usable design point, and a common one where speed matters more than flatness, but it is not this specification.",
                                "0.0432 is the overshoot itself, not the damping that produces it. They are related by an exponential and are never numerically close: a $\\zeta$ of 0.0432 would overshoot by 87%.",
                                "$\\sqrt2$ is the reciprocal, and it is greater than 1, so it describes an *overdamped* circuit with two real poles and no overshoot at all. It would meet the overshoot half of the specification and miss the settling half badly.",
                            ],
                        },
                        {
                            "prompt": "The real part sigma, from the settling requirement.",
                            "hole": "?",
                            "opts": ["2000", "500", "2828", "8000"],
                            "a": 0,
                            "why": "$t_s = 4/\\sigma$, so $\\sigma = 4/t_s = 4/0.002 = 2000$ s$^{-1}$. This is a constraint on the pole's distance from the imaginary axis and on nothing else — it does not care what the damping is, only where the envelope's time constant lands.",
                            "whys": [
                                "$t_s = 4/\\sigma$, so $\\sigma = 4/t_s = 4/0.002 = 2000$ s$^{-1}$. This is a constraint on the pole's distance from the imaginary axis and on nothing else — it does not care what the damping is, only where the envelope's time constant lands.",
                                "500 is $1/t_s$ with the factor of 4 left out, which would be the reciprocal of the settling time treated as a time constant. Four time constants is what gets the envelope down to 1.8%.",
                                "2828 is $\\omega_n$, the answer to the next line rather than this one. $\\omega_n$ is the pole's distance from the origin; $\\sigma$ is its distance from the imaginary axis, and they differ by exactly the factor $\\zeta$.",
                                "8000 is $4/t_s$ with the milliseconds mishandled — $4/(0.5\\times10^{-3})$ rather than $4/(2.0\\times10^{-3})$, or a factor of 4 applied twice. Writing the seconds out in full is the cheapest guard against it.",
                            ],
                        },
                        {
                            "prompt": "Where the pole pair sits.",
                            "hole": "?",
                            "opts": [
                                "-2000 +/- j2000",
                                "-2828 +/- j2000",
                                "-2000 +/- j2828",
                                "-1414 +/- j1414",
                            ],
                            "a": 0,
                            "why": "$\\sigma = 2000$ and $\\omega_d = 2000$, so the pair sits on the 45° lines through the origin — which is exactly what $\\zeta = \\cos 45° = 0.7071$ says. Its distance from the origin is $\\sqrt{2000^2+2000^2} = 2828 = \\omega_n$, as it must be.",
                            "whys": [
                                "$\\sigma = 2000$ and $\\omega_d = 2000$, so the pair sits on the 45° lines through the origin — which is exactly what $\\zeta = \\cos 45° = 0.7071$ says. Its distance from the origin is $\\sqrt{2000^2+2000^2} = 2828 = \\omega_n$, as it must be.",
                                "This puts $\\omega_n$ on the real axis, but $\\omega_n$ is the *distance from the origin*, not a coordinate. A pole at $-2828 \\pm j2000$ has $\\omega_n = 3464$ and $\\zeta = 0.816$, which is a different circuit.",
                                "This has the two coordinates swapped, which puts $\\zeta$ at $2000/3464 = 0.577$ instead of 0.707 and gives 10.8% overshoot — it fails the specification, and it fails it in the direction that is easy not to notice on a scope.",
                                "$-1414 \\pm j1414$ is on the correct 45° ray, so its damping is right and its overshoot would be exactly 4.3%. It is simply too close to the origin: $\\sigma = 1414$ gives $t_s = 2.83$ ms, missing the settling requirement by 40%.",
                            ],
                        },
                        {
                            "prompt": "The inductance, once C has been chosen.",
                            "hole": "?",
                            "opts": ["125 mH", "1.25 H", "12.5 mH", "125 uH"],
                            "a": 0,
                            "why": "$LC = 1.25\\times10^{-7}$ and $C = 1\\times10^{-6}$ F, so $L = 1.25\\times10^{-7}/10^{-6} = 0.125$ H. Only the product is fixed by the specification; the split is a free choice, and it is what sets $Z_0$ and therefore the size of the resistor.",
                            "whys": [
                                "$LC = 1.25\\times10^{-7}$ and $C = 1\\times10^{-6}$ F, so $L = 1.25\\times10^{-7}/10^{-6} = 0.125$ H. Only the product is fixed by the specification; the split is a free choice, and it is what sets $Z_0$ and therefore the size of the resistor.",
                                "1.25 H is the value that would pair with a 100 nF capacitor, ten times smaller. It meets the same specification — with $Z_0$ ten times higher at 3.54 kΩ and a 5 kΩ resistor to match — but it is a physically large and lossy component to reach for when a 1 µF capacitor is on the bench.",
                                "12.5 mH is a factor of ten low, which would put $\\omega_n$ at 8944 rad/s: the circuit would settle in 0.63 ms instead of 2.0 ms. Fast is not automatically better — a bandwidth you did not ask for collects noise you did not want.",
                                "125 µH is out by a factor of a thousand, the usual cost of carrying millis and micros in your head instead of on the paper. Put every value into henries and farads before dividing.",
                            ],
                        },
                        {
                            "prompt": "The characteristic impedance Z0 of the L-C pair.",
                            "hole": "?",
                            "opts": ["353.6 ohm", "125 000 ohm", "0.0028 ohm", "500 ohm"],
                            "a": 0,
                            "why": "$Z_0 = \\sqrt{L/C} = \\sqrt{0.125/10^{-6}} = \\sqrt{125\\,000} = 353.6\\ \\Omega$. It is the resistance the two storage elements define between them, and the resistor is only ever meaningful measured against it: $\\zeta = R/(2Z_0)$.",
                            "whys": [
                                "$Z_0 = \\sqrt{L/C} = \\sqrt{0.125/10^{-6}} = \\sqrt{125\\,000} = 353.6\\ \\Omega$. It is the resistance the two storage elements define between them, and the resistor is only ever meaningful measured against it: $\\zeta = R/(2Z_0)$.",
                                "125 000 is $L/C$ before the square root, and it is not an impedance — $L/C$ has units of ohms squared, which is the clue that the root is still owed.",
                                "0.0028 S is $\\sqrt{C/L}$, the reciprocal, in siemens. It is the form that appears in $\\zeta = (R/2)\\sqrt{C/L}$, where it multiplies rather than divides; both spellings are correct as long as the resistor ends up on the right side of the fraction.",
                                "500 Ω is the answer to the next line, the resistor itself. The resistor is twice $\\zeta$ times $Z_0$, and with $\\zeta$ close to 0.7 those two numbers are close enough to be swapped without the arithmetic looking wrong.",
                            ],
                        },
                        {
                            "prompt": "When the peak arrives.",
                            "hole": "?",
                            "opts": ["1.571 ms", "1.111 ms", "3.142 ms", "2.000 ms"],
                            "a": 0,
                            "why": "$t_p = \\pi/\\omega_d = 3.141593/2000 = 1.571$ ms. Worth writing down even when nobody asked for it: it says the single excursion above the final value is over well before the 2.0 ms the specification allows for settling, which is the sanity check that the design is not merely arithmetically consistent but actually behaves.",
                            "whys": [
                                "$t_p = \\pi/\\omega_d = 3.141593/2000 = 1.571$ ms. Worth writing down even when nobody asked for it: it says the single excursion above the final value is over well before the 2.0 ms the specification allows for settling, which is the sanity check that the design is not merely arithmetically consistent but actually behaves.",
                                "1.111 ms is $\\pi/\\omega_n = 3.141593/2828$, using the undamped frequency where the damped one belongs. Here that is 29% early; the response is still climbing at that instant.",
                                "3.142 ms is $2\\pi/\\omega_d$, a whole ring period rather than half of one, and it lands on the first trough — below the final value, not above it. There is barely a trough to find in a design this well damped.",
                                "2.000 ms is the settling time, which is the requirement rather than a consequence. The peak has to come first, and by a good margin, or the response would still be well outside the band when the clock ran out.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "How far past its target does this one go?",
                    "minutes": 6,
                    "brief": r'''
The mechanical one. Three components, two formulas, one number out, and the only real
opportunity to go wrong is a prefix.

Note what the question does *not* need. Not the supply voltage, not the final value, not
$\omega_n$. Overshoot is a fraction, and the fraction depends on the damping and on
nothing else — which is worth feeling once on real numbers rather than taking on trust.
''',
                    "prompt": "By what percentage does the step response overshoot its final value?",
                    "note": "Give the percentage, to one decimal place — so 12.3, not 0.123.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 5},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "l", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.01},
                            {"id": "r", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 60},
                            {"id": "c", "kind": "C", "x": 13, "y": 7, "rot": 1, "value": 1e-6},
                            {"id": "g1", "kind": "GND", "x": 13, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [5, 5]},
                            {"a": [7, 5], "b": [9, 5]},
                            {"a": [11, 5], "b": [13, 5]},
                            {"a": [13, 5], "b": [13, 6]},
                            {"a": [13, 8], "b": [13, 10]},
                            {"a": [13, 5], "b": [15, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "5.00 V, stepped on at t = 0"},
                        {"label": "L", "value": "10.0 mH"},
                        {"label": "R", "value": "60.0 Ω"},
                        {"label": "C", "value": "1.00 µF"},
                        {"label": "Output", "value": "across the capacitor"},
                    ],
                    "aside": "$\\zeta = \\tfrac{R}{2}\\sqrt{C/L}$ first, then "
                             "$M_p = e^{-\\pi\\zeta/\\sqrt{1-\\zeta^2}}$, then multiply by 100. Put "
                             "every value into ohms, henries and farads before the square root.",
                    # Nothing restated: the natural frequency is found as the point where the measured
                    # phase is exactly -90 degrees (true for any damping), and the gain there is the
                    # final value over 2 zeta, so both numbers come off the swept schematic.
                    "check": r'''
let lo = 1, hi = 1e6;
for (let i = 0; i < 100; i++) {
  const mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > -90) lo = mid; else hi = mid;
}
const fn = Math.sqrt(lo * hi);                 /* phase is -90 exactly at wn */
const z  = c.vout() / (2 * c.gain(fn));        /* |H(wn)| = H(0) / (2 zeta)  */
return 100 * Math.exp(-Math.PI * z / Math.sqrt(1 - z * z));
''',
                    "answer": 37.2,
                    "tol": 0.4,
                    "unit": "%",
                    "hint": "$C/L = 10^{-6}/10^{-2} = 10^{-4}$, whose square root is $10^{-2}$. Half the "
                            "resistance is 30. The exponent is then $-\\pi(0.3)/\\sqrt{0.91}$.",
                    "wrong": "If you got 0.372, that is the fraction and the question asked for a "
                             "percentage. If you got 30.0, you multiplied $\\zeta$ by 100 and stopped one "
                             "formula early. If you got 73.0, the $\\pi$ is missing from the exponent — "
                             "it comes from the peak time, $t_p = \\pi/\\omega_d$, so leaving it out is "
                             "the same as evaluating the envelope one radian in instead of half a ring "
                             "period in. And if your calculator refused to take a square root at all, "
                             "the ratio inside the first one went in upside down: "
                             "$(R/2)\\sqrt{L/C} = 3000$, not 0.3. $\\sqrt{L/C} = 100\\ \\Omega$ is the "
                             "characteristic impedance of the pair, and $\\zeta$ measures the resistor "
                             "*against* it — so it divides rather than multiplying.",
                    "why": r'''
```
base units first:  L = 0.01 H     R = 60 ohm     C = 1e-6 F

C/L            = 1e-6/0.01                  = 1.0e-4
sqrt(C/L)                                   = 1.0e-2
zeta = (R/2) sqrt(C/L) = 30 * 1.0e-2        = 0.3000

1 - zeta^2     = 1 - 0.09                   = 0.9100
sqrt(0.91)                                  = 0.953939

exponent = -pi * 0.3 / 0.953939
         = -0.942478 / 0.953939             = -0.987985
Mp       = e^(-0.987985)                    = 0.372326  ->  37.23 %
```
So the 5 V supply drives the capacitor to $5 \times 1.37233 = 6.862$ V before it turns
round. A passive network of three components, and the output goes 1.86 V above the
supply that feeds it — which it can do because the inductor's current cannot stop at the
instant the capacitor arrives at 5 V, so charge keeps arriving after the pushing has
stopped.

Two things this number is deliberately independent of. The supply: at 10 V the excess
would be 3.72 V instead of 1.86 V, and 37.23% either way, because the circuit is linear.
And $\omega_n$, which is $10^4$ rad/s here and cancels out of the exponent entirely.
Make this circuit ten times faster by scaling $L$ and $C$ and the same curve comes back
drawn on a compressed time axis, overshooting by exactly as much.
''',
                },
                {
                    "title": "When does the ringing reach its highest point?",
                    "minutes": 8,
                    "brief": r'''
The same machinery, one step further along, and now the answer is a time rather than a
ratio — so the units matter and so does which of the two frequencies you divide by.

Two frequencies live in this circuit and they are not the same. $\omega_n$ is set by $L$
and $C$ alone; $\omega_d$ is what the circuit visibly rings at, and it is always the
slower of the two. The peak time is $\pi/\omega_d$.

As before, the supply voltage is on the schematic and plays no part in the answer.
''',
                    "prompt": "How long after the step does the output reach its highest value?",
                    "note": "Answer in milliseconds, to three decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 2},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "l", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.25},
                            {"id": "r", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 400},
                            {"id": "c", "kind": "C", "x": 13, "y": 7, "rot": 1, "value": 1e-6},
                            {"id": "g1", "kind": "GND", "x": 13, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [5, 5]},
                            {"a": [7, 5], "b": [9, 5]},
                            {"a": [11, 5], "b": [13, 5]},
                            {"a": [13, 5], "b": [13, 6]},
                            {"a": [13, 8], "b": [13, 10]},
                            {"a": [13, 5], "b": [15, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "2.00 V, stepped on at t = 0"},
                        {"label": "L", "value": "250 mH"},
                        {"label": "R", "value": "400 Ω"},
                        {"label": "C", "value": "1.00 µF"},
                        {"label": "Output", "value": "across the capacitor"},
                    ],
                    "aside": "Three numbers in order: $\\omega_n = 1/\\sqrt{LC}$, then "
                             "$\\zeta = \\tfrac{R}{2}\\sqrt{C/L}$, then "
                             "$\\omega_d = \\omega_n\\sqrt{1-\\zeta^2}$. The peak is at $\\pi/\\omega_d$, "
                             "and the answer is wanted in milliseconds.",
                    "check": r'''
let lo = 1, hi = 1e6;
for (let i = 0; i < 100; i++) {
  const mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > -90) lo = mid; else hi = mid;
}
const fn = Math.sqrt(lo * hi);
const z  = c.vout() / (2 * c.gain(fn));
const wd = 2 * Math.PI * fn * Math.sqrt(1 - z * z);
return 1000 * Math.PI / wd;                    /* the peak time, in ms */
''',
                    "answer": 1.714,
                    "tol": 0.02,
                    "unit": "ms",
                    "hint": "$LC = 0.25 \\times 10^{-6} = 2.5\\times10^{-7}$, so $\\omega_n = 2000$ rad/s. "
                            "$\\sqrt{C/L} = \\sqrt{4\\times10^{-6}} = 2\\times10^{-3}$, so $\\zeta = 0.4$. "
                            "Then $\\sqrt{1-0.16} = 0.9165$.",
                    "wrong": "If you got 1.571 ms you divided $\\pi$ by $\\omega_n$ rather than "
                             "$\\omega_d$ — an 8% error here, but a 40% error in a circuit damped at "
                             "$\\zeta = 0.8$, so it is worth breaking the habit on the easy case. If you "
                             "got 3.428 ms you used $2\\pi/\\omega_d$, a whole ring period, which lands on "
                             "the first trough instead of the first peak. If you got 0.0017, that is the "
                             "right time in seconds.",
                    "why": r'''
```
LC        = 0.25 * 1e-6                     = 2.5e-7
sqrt(LC)                                    = 5.0e-4
wn        = 1/5.0e-4                        = 2000 rad/s   (318.31 Hz)

C/L       = 1e-6/0.25                       = 4.0e-6
sqrt(C/L)                                   = 2.0e-3
zeta      = (400/2) * 2.0e-3 = 200 * 2.0e-3 = 0.4000

1 - zeta^2                                  = 0.8400
sqrt(0.84)                                  = 0.916515
wd        = 2000 * 0.916515                 = 1833.03 rad/s

tp        = pi/wd = 3.141593/1833.03        = 1.71388e-3 s
                                            = 1.714 ms
```
The gap between $\omega_n = 2000$ and $\omega_d = 1833$ is the whole point of the
question. It is only 8% here, which is exactly why the mistake survives: at light
damping the two are close enough that using the wrong one still gives a plausible
answer, and by the time the damping is heavy enough for the error to be obvious the
habit is set.

Two free readings from the same three numbers. The overshoot is
$e^{-\pi(0.4)/0.916515} = e^{-1.371} = 0.2538$, so the output peaks at
$2 \times 1.2538 = 2.508$ V. And $\sigma = \zeta\omega_n = 800$ s$^{-1}$, so the ringing
is inside 2% after roughly $4/800 = 5.0$ ms. The extrema fall every $t_p$ — peak at
1.71 ms, trough at 3.43 ms, second peak at 5.14 ms — so the settling estimate lands just
before the second peak, which is where a curve with 25% overshoot has decayed to about
1.6% and is indeed nearly done.
''',
                },
                {
                    "title": "The highest voltage this output actually reaches",
                    "minutes": 8,
                    "brief": r'''
The overshoot formula gives a fraction. A fraction of what, exactly, is the question
this unit exists to make you answer, because the answer is not "of the input" and it is
not "of anything you can read off the formula".

Get $\zeta$, get $M_p$, and then find the number the percentage is a percentage *of*. In
this circuit the last part is easy — but it will not be in the next one, and it is worth
having the habit before it matters.
''',
                    "prompt": "What is the highest voltage the output reaches?",
                    "note": "Answer in volts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "l", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.04},
                            {"id": "r", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 200},
                            {"id": "c", "kind": "C", "x": 13, "y": 7, "rot": 1, "value": 1e-6},
                            {"id": "g1", "kind": "GND", "x": 13, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [5, 5]},
                            {"a": [7, 5], "b": [9, 5]},
                            {"a": [11, 5], "b": [13, 5]},
                            {"a": [13, 5], "b": [13, 6]},
                            {"a": [13, 8], "b": [13, 10]},
                            {"a": [13, 5], "b": [15, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V, stepped on at t = 0"},
                        {"label": "L", "value": "40.0 mH"},
                        {"label": "R", "value": "200 Ω"},
                        {"label": "C", "value": "1.00 µF"},
                        {"label": "Output", "value": "across the capacitor"},
                    ],
                    "aside": "$M_p$ is a fraction of the value the response *settles at*. Work out where "
                             "this circuit settles — a settled capacitor is an open, a settled inductor a "
                             "short — and then add $M_p$ of it.",
                    "check": r'''
let lo = 1, hi = 1e6;
for (let i = 0; i < 100; i++) {
  const mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > -90) lo = mid; else hi = mid;
}
const fn = Math.sqrt(lo * hi);
const vf = c.vout();                           /* where the response settles */
const z  = vf / (2 * c.gain(fn));
return vf * (1 + Math.exp(-Math.PI * z / Math.sqrt(1 - z * z)));
''',
                    "answer": 13.96,
                    "tol": 0.06,
                    "unit": "V",
                    "hint": "$\\sqrt{C/L} = \\sqrt{2.5\\times10^{-5}} = 5\\times10^{-3}$, so "
                            "$\\zeta = 100 \\times 5\\times10^{-3} = 0.5$, which is the standard 16.3% "
                            "case. The final value is the whole supply, because at DC the inductor is a "
                            "short and the capacitor an open.",
                    "wrong": "If you got 1.96 V you gave the excess rather than the peak — the question "
                             "asks how high it goes, not how far past. If you got 12.0 V you found the "
                             "final value and stopped. If you got 12.16 V you added the overshoot as "
                             "though 16.3% meant 0.163 volts; it is 16.3% *of 12 V*, which is 1.96 V. "
                             "One free check on any answer here: an underdamped second-order step "
                             "response peaks somewhere between its final value and twice it, since "
                             "$M_p$ runs from 0 at $\\zeta = 1$ up towards 1 as $\\zeta \\to 0$. "
                             "Anything outside 12 to 24 V is wrong before you look at why.",
                    "why": r'''
```
C/L        = 1e-6/0.04                      = 2.5e-5
sqrt(C/L)                                   = 5.0e-3
zeta       = (200/2) * 5.0e-3 = 100 * 5e-3  = 0.5000

1 - zeta^2 = 0.7500        sqrt(0.75)       = 0.866025
exponent   = -pi * 0.5/0.866025 = -1.813799
Mp         = e^(-1.813799)                  = 0.163034   -> 16.30 %

final value: at DC the inductor is a short and the capacitor an open,
so the whole 12 V appears across C                       = 12.000 V

peak       = 12.000 * (1 + 0.163034)
           = 12.000 * 1.163034                           = 13.956 V
```
$\zeta = 0.5$ and 16.3% is the pair worth knowing by heart, alongside $\zeta = 0.707$
with 4.3% and $\zeta = 0.6$ with 9.5%. Three numbers cover most of the designs anyone
actually builds.

The final value deserves the extra line it got. Here it is the entire supply, because
nothing in the loop draws steady current once the capacitor has stopped charging — no
current means no drop across either the resistor or the inductor. Put a second resistor
from the output node to ground and that stops being true immediately: the loop then
carries a steady current, the resistor drops some of the supply, and the response settles
below 12 V with the overshoot computed against the smaller number. That is the next
question in this ladder.

For the record, this peak arrives at $t_p = \pi/\omega_d$ with $\omega_n = 5000$ rad/s
and $\omega_d = 4330$ rad/s, so 0.726 ms after the edge, and the response is inside 2%
by about $4/2500 = 1.6$ ms.
''',
                },
                {
                    "title": "An overshoot measured against something that is not the supply",
                    "minutes": 12,
                    "brief": r'''
The real work, and the one where two separate habits both have to be broken at once.

The LC branch is no longer fed straight from the supply. There is a divider in front of
it, and that changes two things independently: where the response ends up, and how
heavily it is damped. Neither of them is the number written on the source.

The quantity asked for is the *excess* — how far above its final value the output goes,
in volts. Getting it right requires the final value and the damping, and the wrong
resistance will spoil the second even when the first is right.
''',
                    "prompt": "By how many volts does the output rise above the value it eventually settles at?",
                    "note": "Answer in volts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 15},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 1500},
                            {"id": "g1", "kind": "GND", "x": 12, "y": 10},
                            {"id": "l", "kind": "L", "x": 16, "y": 3, "rot": 0, "value": 0.1},
                            {"id": "c", "kind": "C", "x": 20, "y": 6, "rot": 1, "value": 4e-7},
                            {"id": "g2", "kind": "GND", "x": 20, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 23, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [12, 3], "b": [12, 5]},
                            {"a": [12, 7], "b": [12, 10]},
                            {"a": [12, 3], "b": [15, 3]},
                            {"a": [17, 3], "b": [20, 3]},
                            {"a": [20, 3], "b": [20, 5]},
                            {"a": [20, 7], "b": [20, 10]},
                            {"a": [20, 3], "b": [23, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "15.0 V, stepped on at t = 0"},
                        {"label": "R1", "value": "1.00 kΩ"},
                        {"label": "R2", "value": "1.50 kΩ"},
                        {"label": "L", "value": "100 mH"},
                        {"label": "C", "value": "400 nF"},
                        {"label": "Output", "value": "across the capacitor"},
                    ],
                    "aside": "Lift the L-C branch out and Thévenise what it sees: $V_{th}$ is the divider "
                             "output, and $R_{th}$ is R1 in parallel with R2, because from the branch's "
                             "terminals the supply is a short to ground. Then it is an ordinary series "
                             "R-L-C driven by $V_{th}$ through $R_{th}$.",
                    "check": r'''
let lo = 1, hi = 1e6;
for (let i = 0; i < 100; i++) {
  const mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > -90) lo = mid; else hi = mid;
}
const fn = Math.sqrt(lo * hi);
const vf = c.vout();                           /* the divider output, not the supply */
const z  = vf / (2 * c.gain(fn));              /* |H(wn)| = H(0)/(2 zeta) either way  */
return vf * Math.exp(-Math.PI * z / Math.sqrt(1 - z * z));
''',
                    "answer": 0.853,
                    "tol": 0.008,
                    "unit": "V",
                    "hint": "$V_{th} = 15 \\times 1500/2500 = 9$ V and "
                            "$R_{th} = 1000\\times1500/2500 = 600\\ \\Omega$. Then "
                            "$\\sqrt{C/L} = \\sqrt{4\\times10^{-6}} = 2\\times10^{-3}$, so "
                            "$\\zeta = 300 \\times 2\\times10^{-3}$, which is one of the three values "
                            "worth knowing by heart.",
                    "wrong": "If you got 1.42 V the damping is right and the baseline is wrong: that is "
                             "9.478% of the 15 V supply instead of 9.478% of the 9 V the output settles "
                             "at. If you got 9.85 V you gave the peak rather than the excess. And if you "
                             "got zero — or a calculator refusing to take the square root of a negative "
                             "number — you used R1 = 1 kΩ as the damping resistance, which gives "
                             "$\\zeta = 1$ exactly: critically damped, no overshoot at all. That answer is "
                             "internally consistent and completely wrong, which is what makes it "
                             "dangerous.",
                    "why": r'''
```
step 1 -- what the L-C branch is actually driven by

  V_th = 15 * R2/(R1+R2) = 15 * 1500/2500          = 9.000 V
  R_th = R1 || R2 = 1000*1500/2500                 = 600.0 ohm

step 2 -- the two numbers, from R_th and the storage pair

  LC        = 0.1 * 4e-7                           = 4.0e-8
  wn        = 1/sqrt(4.0e-8) = 1/2.0e-4            = 5000 rad/s
  C/L       = 4e-7/0.1                             = 4.0e-6
  sqrt(C/L)                                        = 2.0e-3
  zeta      = (600/2) * 2.0e-3 = 300 * 2.0e-3      = 0.6000

step 3 -- the overshoot, and what it is a fraction of

  1 - zeta^2 = 0.6400      sqrt(0.64)              = 0.800000
  exponent   = -pi * 0.6/0.8                       = -2.356194
  Mp         = e^(-2.356194)                       = 0.094780  -> 9.478 %

  excess     = 9.000 * 0.094780                    = 0.8530 V
  (so the output peaks at 9.853 V, from a 15 V supply)
```
Two independent traps, and it is worth separating them because they fail differently.

**The final value.** At DC the inductor is a short and the capacitor an open, so no
current flows in the L-C branch and the output sits at whatever the divider puts on
node A: 9 V, not 15 V. Using 15 V gives 1.42 V, an answer 67% too large that looks
entirely reasonable on its own.

**The damping resistance.** $\zeta$ is set by the resistance the L-C branch *sees*, and
from its two terminals the supply is a short to ground — so R1 and R2 are in parallel,
not in series and not R1 alone. Using R1 = 1 kΩ gives $\zeta = 1.000$, exactly critical
damping, and predicts no overshoot whatsoever. Using R1 + R2 = 2.5 kΩ gives
$\zeta = 2.5$, overdamped, and predicts the same nothing. Both are the kind of wrong
answer that never announces itself, because a smooth non-overshooting curve is a
perfectly believable thing for a circuit to do.

The check on all of this is cheap: the answer must be somewhere between 0 and the final
value, and for any $\zeta$ between 0.4 and 0.8 it should be a few per cent to a quarter
of it. 0.85 V against 9 V is 9.5%, which sits comfortably in that range; 1.42 V against
9 V would be 15.8%, which corresponds to $\zeta = 0.506$ — and no combination of the two
resistors in this circuit produces 0.506.
''',
                },
            ],
            "tune": {
                "title": "A filter that may ring, but only so much",
                "minutes": 9,
                "brief": r'''
Here is a specification of the kind that actually arrives: *the step response may
overshoot by between 10% and 20%, and the natural frequency must land between 450 Hz
and 550 Hz.* Nothing in it mentions a resistor.

The first half is a statement about $\zeta$ and nothing else, because overshoot depends
on $\zeta$ alone: 20% overshoot is $\zeta = 0.456$ and 10% is $\zeta = 0.591$, so the
window is $0.456 \le \zeta \le 0.591$. The second half is a statement about $\omega_n$.
Between them they pin the poles into a small wedge of the s-plane.

Three sliders, two constraints — so there is a family of answers rather than one. That
is normal: the two behavioural numbers depend on $L$ and $C$ only through the product
$LC$, and on $R$ only through $R\sqrt{C/L}$.
''',
                "prompt": "Set R, L and C so that the damping and the natural frequency both land inside their windows.",
                "note": "ζ comes from the overshoot the specification allows; fₙ is given directly. Both must hold at once.",
                "model": "rlc",
                "initial": {"r": 100, "l": 100, "c": 2.5},
                "constraints": [
                    {"k": "zeta", "label": "0.456 ≤ ζ ≤ 0.591, which is an overshoot between 10% and 20%", "min": 0.456, "max": 0.591},
                    {"k": "fn", "label": "natural frequency between 450 Hz and 550 Hz", "min": 450, "max": 550},
                ],
            },
            "derive": {
                "title": "From the transform to the overshoot",
                "minutes": 15,
                "vars": ["s", "t", "zeta", "omega_n", "omega_d", "sigma", "B", "M_p", "y"],
                "brief": r'''
The partial fractions of module 2 needed the poles to be real, or at least needed you to
handle a complex pair one at a time and trust the imaginary parts to cancel. Completing
the square avoids all of that: it matches the denominator to the standard sine and
cosine pairs directly, and the answer comes out real from the start.

Write $\sigma = \zeta\omega_n$ throughout — it is the distance of the poles from the
imaginary axis, and it is the decay rate.
''',
                "steps": [
                    {
                        "prompt": "Complete the square: $s^2 + 2\\zeta\\omega_n s + \\omega_n^2 = (s + \\zeta\\omega_n)^2 + \\omega_d^2$. Write $\\omega_d^2$ in terms of $\\omega_n$ and $\\zeta$.",
                        "answer": "\\omega_n^2 (1 - \\zeta^2)",
                        "hint": "Expanding $(s+\\zeta\\omega_n)^2$ produces $\\zeta^2\\omega_n^2$ as its constant term. Whatever is left over of the original $\\omega_n^2$ is $\\omega_d^2$.",
                        "deconstruct": [
                            "$(s+\\zeta\\omega_n)^2 = s^2 + 2\\zeta\\omega_n s + \\zeta^2\\omega_n^2$, which matches the first two terms exactly.",
                            "So $\\omega_d^2 = \\omega_n^2 - \\zeta^2\\omega_n^2$.",
                            "Factor $\\omega_n^2$ out of that.",
                        ],
                    },
                    {
                        "prompt": "The step response is $Y(s) = \\dfrac{\\omega_n^2}{s\\left[(s+\\sigma)^2 + \\omega_d^2\\right]}$ with $\\sigma = \\zeta\\omega_n$. Multiply by $s$ and set $s = 0$ to get the residue at the origin.",
                        "answer": "1",
                        "hint": "You are evaluating $\\dfrac{\\omega_n^2}{\\sigma^2 + \\omega_d^2}$. Substitute both in terms of $\\omega_n$ and $\\zeta$.",
                        "deconstruct": [
                            "$\\sigma^2 = \\zeta^2\\omega_n^2$ and $\\omega_d^2 = \\omega_n^2(1-\\zeta^2)$.",
                            "Their sum is $\\zeta^2\\omega_n^2 + \\omega_n^2 - \\zeta^2\\omega_n^2 = \\omega_n^2$.",
                            "So the residue is $\\omega_n^2/\\omega_n^2$ — which is the final value of 1 that the dashed line in module 1 was drawn at.",
                        ],
                    },
                    {
                        "prompt": "So $y(t) = 1 - e^{-\\sigma t}\\left(\\cos\\omega_d t + B\\sin\\omega_d t\\right)$ for some constant $B$. A second-order step response leaves the origin with zero slope. Differentiate, set $t = 0$, and write $B$ in terms of $\\zeta$.",
                        "answer": "\\frac{\\zeta}{\\sqrt{1-\\zeta^2}}",
                        "hint": "Differentiating the product gives $\\sigma$ from the exponential and $-B\\omega_d$ from the bracket at $t=0$. Set the sum to zero, then substitute $\\sigma = \\zeta\\omega_n$ and $\\omega_d = \\omega_n\\sqrt{1-\\zeta^2}$.",
                        "deconstruct": [
                            "$\\dot y(0) = \\sigma - B\\omega_d$, so $B = \\sigma/\\omega_d$.",
                            "$\\dfrac{\\sigma}{\\omega_d} = \\dfrac{\\zeta\\omega_n}{\\omega_n\\sqrt{1-\\zeta^2}}$.",
                            "The $\\omega_n$ cancels, which is why the shape of the curve never depends on it.",
                        ],
                    },
                    {
                        "prompt": "Differentiating and simplifying gives $\\dot y(t) = \\dfrac{\\omega_n^2}{\\omega_d}e^{-\\sigma t}\\sin\\omega_d t$. The peak is the first $t > 0$ at which that vanishes. Write $t_p$ in terms of $\\omega_d$.",
                        "answer": "\\frac{\\pi}{\\omega_d}",
                        "hint": "An exponential is never zero, so the sine has to be. Its first positive zero is at an argument of $\\pi$.",
                        "deconstruct": [
                            "$\\sin\\omega_d t = 0$ when $\\omega_d t = 0, \\pi, 2\\pi, \\dots$",
                            "$t = 0$ is the start, not a peak, so the first one that counts is $\\omega_d t = \\pi$.",
                            "The later zeros are the smaller peaks and troughs of the ringing.",
                        ],
                    },
                    {
                        "prompt": "At $t = t_p$ the argument $\\omega_d t$ equals $\\pi$, so $\\cos = -1$ and $\\sin = 0$ and $y(t_p) = 1 + e^{-\\sigma t_p}$. The overshoot is therefore $M_p = e^{-\\sigma t_p}$. Write $\\ln M_p$ in terms of $\\zeta$ alone.",
                        "answer": "-\\frac{\\pi\\zeta}{\\sqrt{1-\\zeta^2}}",
                        "hint": "$\\ln M_p = -\\sigma t_p = -\\zeta\\omega_n \\cdot \\dfrac{\\pi}{\\omega_d}$, and $\\omega_d = \\omega_n\\sqrt{1-\\zeta^2}$.",
                        "deconstruct": [
                            "$\\sigma t_p = \\zeta\\omega_n \\cdot \\dfrac{\\pi}{\\omega_n\\sqrt{1-\\zeta^2}}$.",
                            "The $\\omega_n$ cancels again, leaving $\\dfrac{\\pi\\zeta}{\\sqrt{1-\\zeta^2}}$.",
                            "And $\\ln M_p$ is minus that, because $M_p$ is $e$ to the power of minus it.",
                        ],
                    },
                    {
                        "prompt": "Now design. A specification asks for $\\zeta = 0.5$ and a 2% settling time of 4 ms, using $t_s = 4/(\\zeta\\omega_n)$. What is $\\omega_n$, in rad/s?",
                        "answer": "2000",
                        "hint": "Rearrange to $\\omega_n = 4/(\\zeta t_s)$ and put the two numbers in.",
                        "deconstruct": [
                            "$t_s = \\dfrac{4}{\\zeta\\omega_n} = 0.004$ s.",
                            "So $\\zeta\\omega_n = 4/0.004 = 1000$.",
                            "With $\\zeta = 0.5$ that makes $\\omega_n = 2000$ — the same natural frequency as the filter built in module 2, though with twice its damping, reached from a time-domain specification instead of a pole position.",
                        ],
                    },
                ],
                "closing": r'''
Four numbers came out of one differentiation: the peak time, the overshoot, the settling
time and the value it settles to. Every one of them is a statement about where the two
poles sit, and none of them needed the response to be plotted.

That is worth holding on to, because it runs the other way as well. Someone hands you a
measured curve, you read the overshoot and the peak time off it, and those two numbers
give you $\zeta$ and $\omega_d$ and therefore the poles — which is the identification
problem the capstone asks you to automate.
''',
            },
            "quiz": {
                "title": "Reading a step response",
                "minutes": 9,
                "questions": [
                    {
                        "q": "The overshoot of a second-order step response depends on:",
                        "opts": [
                            "$\\omega_n$ only",
                            "$\\zeta$ only",
                            "both, about equally",
                            "the DC gain",
                        ],
                        "a": 1,
                        "why": r'''
$M_p = e^{-\pi\zeta/\sqrt{1-\zeta^2}}$ contains no $\omega_n$ at all. Changing $\omega_n$
scales the time axis and leaves the shape untouched — the scaling property again, in the
one place where it is most useful. The DC gain multiplies the whole curve, final value
included, so the *fraction* by which it overshoots is unchanged; a gain of 10 with 16%
overshoot peaks at 11.6, not at 10.16.
''',
                    },
                    {
                        "q": "A system has $\\zeta = 0.5$. Its step response overshoots by about:",
                        "opts": ["5%", "16%", "30%", "50%"],
                        "a": 1,
                        "why": r'''
$e^{-\pi(0.5)/\sqrt{0.75}} = e^{-1.814} = 0.163$, so 16.3%. Two neighbours worth knowing
by heart: $\zeta = 0.707$ gives 4.3%, which is the usual "acceptable" figure and also
the flattest frequency response; $\zeta = 0.6$ gives 9.5%, which is where a great many
designs are deliberately placed because it is close to the fastest settling for a given
overshoot budget. $\zeta = 0.5$ is a deliberately lively response, not a broken one.
''',
                    },
                    {
                        "q": "The 2% settling time of an underdamped second-order system is about:",
                        "opts": [
                            "$4/(\\zeta\\omega_n)$",
                            "$4/\\omega_n$",
                            "$4/\\omega_d$",
                            "$4\\zeta/\\omega_n$",
                        ],
                        "a": 0,
                        "why": r'''
The ringing sits inside an envelope $e^{-\zeta\omega_n t}$, and $e^{-4} = 0.018$, just
under 2% — so four envelope time constants is the estimate, and $\zeta\omega_n$ is the
real part of the pole. $\omega_d$ decides how fast the response *rings*, which is a
different question from how fast it dies; a pair at $-1 \pm j100$ oscillates furiously
and settles slowly. And multiplying by $\zeta$ rather than dividing would make heavier
damping settle more slowly, which is backwards until $\zeta$ approaches 1.
''',
                    },
                    {
                        "q": "Two systems both have $\\omega_n = 1000$ rad/s; one has $\\zeta = 0.1$ and the other $\\zeta = 0.9$. Which settles first?",
                        "opts": [
                            "the one with $\\zeta = 0.9$",
                            "the one with $\\zeta = 0.1$",
                            "both at the same time, since $\\omega_n$ is the same",
                            "it cannot be said without the DC gain",
                        ],
                        "a": 0,
                        "why": r'''
Settling goes as $4/(\zeta\omega_n)$: about 4.4 ms against about 40 ms, a factor of
nine. Equal $\omega_n$ means the two pole pairs are the same distance from the *origin*,
not the same distance from the imaginary axis, and it is the second distance that sets
the decay. Be careful not to read this as "more damping is always faster": past about
$\zeta = 1$ the two real poles separate, the slow one dominates, and settling gets worse
again. The minimum sits a little below critical damping.
''',
                    },
                    {
                        "q": "With $\\zeta = 1$ the two poles coincide at $-\\omega_n$. The step response is:",
                        "opts": [
                            "$1 - e^{-\\omega_n t}$",
                            "$1 - t e^{-\\omega_n t}$",
                            "$1 - (1 + \\omega_n t)e^{-\\omega_n t}$",
                            "$1 - \\cos\\omega_n t$",
                        ],
                        "a": 2,
                        "why": r'''
A repeated pole brings a $te^{-at}$ term with it as well as the plain exponential, and
the two combine into $(1 + \omega_n t)e^{-\omega_n t}$. Check both ends: it is 0 at
$t=0$, and differentiating gives $\omega_n^2 t e^{-\omega_n t}$, which is zero at
$t = 0$ — a second-order step response always leaves the origin flat. The single
exponential leaves the origin with a slope of $\omega_n$, which is the giveaway that it
belongs to a first-order circuit; $1 - te^{-\omega_n t}$ does not even start at zero.
''',
                    },
                    {
                        "q": "A specification says “no more than 10% overshoot”. In the s-plane that is:",
                        "opts": [
                            "a circle of radius $\\omega_n$ the poles must stay inside",
                            "a vertical line the poles must stay to the left of",
                            "a horizontal band the poles must stay inside",
                            "a wedge: the poles must lie within about 54° of the negative real axis",
                        ],
                        "a": 3,
                        "why": r'''
$\zeta$ is the cosine of the angle between the pole and the negative real axis, so a
*minimum* $\zeta$ is a *maximum* angle. Ten per cent overshoot needs $\zeta \ge 0.591$,
and $\arccos 0.591 = 53.8°$, so the poles must lie inside a wedge of that half-angle.
A vertical line is a real specification for a different thing: a settling time, which
fixes $\zeta\omega_n$ and so pushes the poles left. A horizontal pair of lines is nearly
a peak-time specification, but with the sense reversed — $t_p = \pi/\omega_d$, so a
*maximum* peak time forces the poles to sit at least $\pi/t_p$ *above* the real axis,
outside the band rather than inside it. A circle centred on the origin bounds
$\omega_n$, which on its own says nothing about the shape of the response at all. A
design carrying several of these at once has to find the region where they all hold.
''',
                    },
                ],
            },
        },

        # ---- M6 -----------------------------------------------------------
        {
            "title": "Matrices, linear maps and networks",
            "summary": "A matrix is not a table of numbers. It is what a linear map does to the basis vectors, and a resistor network is one.",
            "concepts": [
                "A map $T$ is **linear** when $T(av + bw) = aT(v) + bT(w)$. That single property is what makes superposition legal in circuits, and it is the only thing matrices describe.",
                "$Av$ is a **combination of the columns of $A$**, weighted by the entries of $v$. Reading a matrix–vector product column-wise rather than row-wise makes most of linear algebra obvious.",
                "The $j$-th column of the matrix of $T$ is $T(e_j)$, the image of the $j$-th basis vector. Feed a map the basis vectors one at a time and you have built its matrix.",
                "Matrix multiplication is composition: $ABv$ means do $B$, then do $A$. That is why it is associative and why it is not commutative.",
                "Nodal analysis writes KCL once per unknown node: $Gv = i$, where $v$ holds the node voltages and $i$ the currents injected from outside.",
                "$G$ is built by inspection. A resistor between nodes $a$ and $b$ adds its conductance $1/R$ to $G_{aa}$ and $G_{bb}$, and subtracts it from $G_{ab}$ and $G_{ba}$. Ground gets no row and no column, because its voltage is already known.",
                "$G$ is symmetric because a resistor conducts the same both ways, and it is diagonally dominant, which is why the equations are numerically well behaved.",
                "A node fixed by an ideal voltage source has its KCL row replaced by a single 1 and its known voltage on the right-hand side. A singular $G$ almost always means some node has no resistive path to ground.",
            ],
            "read": [
                {
                    "title": "Linearity, and where a matrix comes from",
                    "minutes": 13,
                    "body": r'''
Take any resistor network you like, with any number of supplies in it, and turn every
supply up by a factor of three. Every node voltage triples. Every branch current
triples. Nothing shifts, nothing saturates, nothing lags behind — the entire solution
scales with the input, exactly, and at every node simultaneously.

Now something slightly less obvious. Run the network with the first supply connected
and the second one replaced by a piece of wire, and write down the node voltages. Run
it again with the second supply connected and the first replaced by a piece of wire,
and write those down too. Add the two sets of numbers together entry by entry. What you
get is the answer the network gives with both supplies connected at once — again
exactly, not nearly.

Those two facts are the same fact, they are the reason this course spends five modules
on matrices, and the fact has a name.

## What "linear" actually says

A map $T$ that takes a vector and returns a vector is **linear** when

$$T(av + bw) = a\,T(v) + b\,T(w)$$

for every pair of vectors $v, w$ and every pair of numbers $a, b$. Scaling the input and
then mapping gives the same answer as mapping and then scaling; adding two inputs and
then mapping gives the same answer as mapping each and then adding. Scaling is the
first paragraph above and adding is the second.

The word is worth pinning down because ordinary English gets it wrong. $f(x) = 3x + 2$
draws a straight line on a graph and is *not* a linear map: $f(2 \times 1) = 8$, while
$2f(1) = 10$. The offset ruins it. A map with a constant term is **affine**, and affine
maps are not what matrices describe.

Why is a resistor network linear? Because the two rules it obeys are. Ohm's law says
the current through a resistor is $(v_a - v_b)/R$, which is a fixed number times a
difference of unknowns — no squares, no products of unknowns, no constant term.
Kirchhoff's current law says a sum of such currents is zero. A sum of linear things is
linear. That is the whole argument, and everything else you know about resistive
circuits — the divider rule, Thévenin, superposition, the fact that you can analyse a
network at all without simulating it — is a consequence of it.

## Worked: two supplies and one node, twice over

A 9 V supply feeds a node through 1 kΩ. A 3 V supply feeds the same node through
another 1 kΩ. A 2 kΩ resistor runs from that node to ground. Call the node voltage
$v_A$.

First the direct route. Kirchhoff at the node: what arrives through the two 1 kΩ
resistors leaves through the 2 kΩ.

```text
  (9 - vA)/1000  +  (3 - vA)/1000  =  vA/2000

multiply every term by 2000:

  2(9 - vA)  +  2(3 - vA)  =  vA
  18 - 2 vA  +  6 - 2 vA   =  vA
  24                        =  5 vA

  vA = 4.80 V
```

Now the superposition route, which is the same circuit solved as two easier circuits.
"Deactivate" a source means set its value to zero, and zero volts across a voltage
source is a short circuit — so the 3 V supply is replaced by a wire to ground, not
removed.

```text
3 V supply deactivated (shorted to ground):

  its 1 k now runs from the node to ground, alongside the 2 k

  1000 || 2000 = 1000 * 2000 / 3000 = 666.7 ohm

  vA1 = 9 * 666.7 / (1000 + 666.7) = 9 * 0.400 = 3.60 V

9 V supply deactivated, the same arithmetic mirrored:

  vA2 = 3 * 0.400 = 1.20 V

  vA = 3.60 + 1.20 = 4.80 V
```

Same 4.80 V, reached without ever writing the two supplies into one equation. That is
what linearity buys, and it is why superposition is legal rather than merely plausible.

## The mistake people actually make: superposing power

Everything in that calculation superposed, so it is tempting to superpose the next
thing you want as well. Take the power in the 2 kΩ resistor.

```text
with the 9 V supply alone :  3.60^2 / 2000  =  6.48 mW
with the 3 V supply alone :  1.20^2 / 2000  =  0.72 mW
                     sum  :                    7.20 mW

with both connected       :  4.80^2 / 2000  = 11.52 mW
```

Not close. Power is $v^2/R$, and squaring is not linear:
$(v_1 + v_2)^2 = v_1^2 + 2v_1v_2 + v_2^2$. The missing 4.32 mW is exactly the cross
term, $2 \times 3.60 \times 1.20 / 2000$. Voltages and currents superpose because they
are the unknowns of a linear system; powers and energies do not, because they are
quadratic in those unknowns. Compute every voltage by superposition if you like, then
compute the power once, from the total.

The other half of the same mistake is deactivating a source by deleting it. A voltage
source set to zero is a short; a *current* source set to zero is an open circuit. Get
those the wrong way round and the sub-circuits you solve are not sub-circuits of
anything.

## Feeding a map the basis vectors

Here is why linearity produces a rectangle of numbers rather than something worse.

Any vector can be taken apart into its components: $v = v_1e_1 + v_2e_2 + \dots +
v_ne_n$, where $e_j$ is the vector with a 1 in position $j$ and zeros elsewhere. Apply
a linear map to that decomposition and the definition lets you take it through the sum
one term at a time:

$$T(v) = v_1\,T(e_1) + v_2\,T(e_2) + \dots + v_n\,T(e_n)$$

Read what that says. To know $T$ on *every* vector — infinitely many of them — it is
enough to know $T$ on the $n$ basis vectors. Everything else is a weighted sum of those
$n$ answers. So write the $n$ answers down side by side as the columns of an array, and
you have stored the map completely:

$$A = \Big[\;T(e_1)\;\Big|\;T(e_2)\;\Big|\;\dots\;\Big|\;T(e_n)\;\Big]$$

and matrix–vector multiplication is defined to be exactly the weighted sum above:

$$Av = v_1a_1 + v_2a_2 + \dots + v_na_n$$

with $a_j$ the $j$-th column. That is the definition worth carrying. The row-by-row
recipe most people learn — dot the first row with $v$, then the second — computes the
same number and hides the meaning. Column-wise, half of linear algebra is already
obvious: the reachable outputs are the combinations of the columns, a matrix fails to
be invertible exactly when its columns fail to be independent, and multiplying by $e_j$
picks out column $j$ because it is the combination with weight 1 on that column and 0
on all the others.

## Worked: measuring the matrix of a circuit

Take the map seriously as something physical. Here is one. A network has two accessible
nodes plus ground; 1 kΩ runs from node 1 to ground, 1 kΩ from node 1 to node 2, and
1 kΩ from node 2 to ground. Define $T$ as: *given the two node voltages I want, tell me
the current I must inject at each node from outside to hold them there.* It is linear,
because Ohm and Kirchhoff are.

Feed it $e_1$, which here means 1 V at node 1 and 0 V at node 2, and account for every
resistor.

```text
node 1 held at 1 V, node 2 held at 0 V

  1 k from node 1 to ground :  1 V across it   ->  1 mA leaves node 1
  1 k from node 1 to node 2 :  1 V across it   ->  1 mA leaves node 1
                                                   and arrives at node 2
  1 k from node 2 to ground :  0 V across it   ->  no current

node 1:  2 mA leaves, so 2 mA must be injected     ->  +2 mA
node 2:  1 mA arrives and none leaves, so 1 mA
         must be taken away                        ->  -1 mA

first column = ( +2, -1 ) mA per volt = mS
```

The network is symmetric, so feeding it $e_2$ gives the mirror image, $(-1, +2)$. The
matrix of the map is therefore

$$G = \begin{pmatrix} 2 & -1 \\ -1 & 2\end{pmatrix}\ \mathrm{mS}$$

and nothing about how it was obtained required a formula to be remembered. Two
measurements, stacked as columns.

Now use it in the direction you normally want. Inject 3 mA at node 1 and nothing at
node 2; what are the voltages? That is $Gv = i$, and with the numbers in millisiemens,
volts and milliamps — which are consistent, since mS × V = mA — it reads

```text
   2 v1  -  v2  =  3
   - v1  + 2 v2 =  0

from the second equation :  v1 = 2 v2
substitute               :  4 v2 - v2 = 3   ->   v2 = 1.00 V,  v1 = 2.00 V
```

Check it against the circuit rather than against the algebra. At node 1: 2.00 V across
the 1 kΩ to ground is 2 mA out, and 1.00 V across the 1 kΩ bridge is 1 mA out; 3 mA
leaves, 3 mA was injected. At node 2: 1 mA arrives across the bridge and 1.00 V across
its 1 kΩ to ground sends 1 mA away. Both nodes balance.

## Multiplication is composition

If $B$ is the matrix of one map and $A$ of another, the matrix of "do $B$, then do $A$"
is the product $AB$ — and by the column rule, its $j$-th column is $A$ applied to the
$j$-th column of $B$. Nothing else needs remembering.

```text
A = [ 2  1 ]      B = [ 1  0 ]      v = [ 3 ]
    [ 0  3 ]          [ 2  1 ]          [ 1 ]

step by step:  Bv = 3*(1,2) + 1*(0,1) = (3, 7)
               A(Bv) = 3*(2,0) + 7*(1,3) = (6+7, 0+21) = (13, 21)

as one matrix:  AB column 1 = A*(1,2) = 1*(2,0) + 2*(1,3) = (4, 6)
                AB column 2 = A*(0,1) = 0*(2,0) + 1*(1,3) = (1, 3)

                AB = [ 4  1 ]   and   AB*v = (12+1, 18+3) = (13, 21)
                     [ 6  3 ]
```

The two routes agree, which is what associativity means. Now swap the order:

```text
BA column 1 = B*(2,0) = 2*(1,2) = (2, 4)
BA column 2 = B*(1,3) = 1*(1,2) + 3*(0,1) = (1, 5)

BA = [ 2  1 ]      BA*v = (6+1, 12+5) = (7, 17)
     [ 4  5 ]
```

$(7, 17)$ is not $(13, 21)$. Matrix multiplication does not commute, and the reason is
not algebraic pedantry: stretching a thing and then shearing it is a different
operation from shearing it and then stretching it. In circuit terms, a stage that loads
its predecessor and a stage that does not are different circuits when you swap them.

## Where linearity stops holding

- **Diodes and transistors.** A diode's current is $I_S(e^{v/V_T} - 1)$. Double the
  voltage and the current does not double, it squares-and-then-some, and superposition
  gives an answer that is not merely inaccurate but meaningless. The standard rescue is
  to linearise: fix an operating point, and treat only the small deviations about it as
  a linear problem. That is what EE201 does, and it is why a transistor amplifier has a
  "small-signal model" made entirely of resistors and controlled sources.
- **Power, energy, and anything else quadratic.** Covered above, but worth repeating
  because it is the failure that survives longest: the quantities that superpose are
  the ones the linear equations solve for, and nothing else.
- **Components whose value moves.** A resistor that heats up as you drive it, a lamp
  filament, a thermistor doing its job — the value depends on the answer, so the
  equations are no longer linear in the unknowns even though they look it.
- **Maps with no finite matrix.** Linearity does not require finitely many dimensions.
  Differentiation is a perfectly good linear map on functions: $(af + bg)' = af' + bg'$.
  It just has no $n \times n$ array, because there is no finite basis to feed it. That
  particular linear map is the one module 1 turned into multiplication by $s$, which is
  the closest thing to a matrix it has — and the reason the transform and this half of
  the course keep meeting.
''',
                },
                {
                    "title": "The conductance matrix, and why the circuit writes it for you",
                    "minutes": 14,
                    "body": r'''
The previous unit showed that a linear map has a matrix, and got one out of a network
by measurement: hold the node voltages at the basis vectors, one at a time, and record
what current that takes. It works, and the lab at the end of this module does exactly
that. But nobody analyses a circuit that way, because the matrix can be read straight
off the schematic, in one pass, without solving anything. This unit derives that rule
and then takes it seriously enough to say when it fails.

## One law, written once per node

Pick a node. Kirchhoff's current law says charge does not pile up there, so the current
leaving through every branch attached to it must equal the current arriving from
outside — from a current source, or from nowhere at all, in which case the total is
zero.

Write it for node $a$. Every resistor attached to it has a conductance
$g = 1/R$ and leads to some other node $b$, possibly ground. The current leaving node
$a$ through that resistor is $g_{ab}(v_a - v_b)$: Ohm's law, with the reference
direction pointing away from $a$. Sum over every neighbour and set the total equal to
the current $i_a$ injected from outside:

$$\sum_b g_{ab}\,(v_a - v_b) = i_a$$

Now do one line of algebra — the line that produces the whole method. Split the bracket
and gather the unknowns:

$$\Bigg(\sum_b g_{ab}\Bigg)v_a \;-\; \sum_b g_{ab}\,v_b \;=\; i_a$$

That is one row of a matrix equation $Gv = i$, and reading the coefficients off it
gives the rule people usually meet as an unmotivated recipe:

- $G_{aa}$, the coefficient of the node's own voltage, is the **sum of every
  conductance touching node $a$** — including any that lead to ground.
- $G_{ab}$, the coefficient of a neighbour's voltage, is **minus the conductance
  joining $a$ to $b$**, and zero if no resistor joins them directly.

Equivalently, and more usefully when you are writing it down: take each resistor in
turn, add its $g$ to both diagonal entries $G_{aa}$ and $G_{bb}$, and subtract it from
both off-diagonal entries $G_{ab}$ and $G_{ba}$. Do that for every resistor and the
matrix is finished. This is the **stamping rule**, and it is nothing more than the
equation above, transposed from "one row at a time" to "one component at a time".

## Why ground gets no row and no column

Ground is a node like any other, so why does it not get an equation?

Take the column first. Ground's voltage is 0 by definition, so the term $g_{a0}v_0$ is
zero and contributes nothing to any row. A resistor from node $a$ to ground therefore
adds to $G_{aa}$ and to nothing else — it is the one case where the stamping rule adds
to a diagonal without subtracting from an off-diagonal, and it is where most sign
errors live.

The row is more interesting. Add up the KCL equations of *all* the nodes, ground
included. Every resistor appears twice, once at each end, with opposite signs, so the
sum is $0 = 0$: the equations are not independent, and one of them carries no
information the others do not already have. There is a matching degeneracy in the
unknowns, because adding the same constant to every node voltage in the circuit changes
no branch current and so satisfies the same equations. Delete ground's row and its
column and both problems go away at once — one redundant equation removed, one
arbitrary constant pinned. Choosing a ground node is not bookkeeping; it is the step
that makes the system solvable.

## Worked: three nodes and a current source

A 4 mA source injects into node 1. From node 1: 2 kΩ to ground, and 1 kΩ across to node
2. From node 2: 2 kΩ to ground, and 1 kΩ across to node 3. From node 3: 1 kΩ to ground.

Work in millisiemens, because 1 kΩ is 1 mS and the numbers stay small. Stamp each
resistor in turn:

```text
2 k, node 1 to ground  (0.5 mS) :  G11 += 0.5
1 k, node 1 to node 2  (1.0 mS) :  G11 += 1.0   G22 += 1.0
                                   G12 -= 1.0   G21 -= 1.0
2 k, node 2 to ground  (0.5 mS) :  G22 += 0.5
1 k, node 2 to node 3  (1.0 mS) :  G22 += 1.0   G33 += 1.0
                                   G23 -= 1.0   G32 -= 1.0
1 k, node 3 to ground  (1.0 mS) :  G33 += 1.0

        [ 1.5  -1.0   0.0 ]        [ v1 ]     [ 4 ]
   G =  [-1.0   2.5  -1.0 ]  mS,   [ v2 ]  =  [ 0 ]  mA
        [ 0.0  -1.0   2.0 ]        [ v3 ]     [ 0 ]
```

Nodes 2 and 3 have nothing injected into them, so their rows read 0 — which is the
usual case. The right-hand side is where sources live, and most nodes have none.

Solve it from the bottom, where the row is shortest:

```text
row 3 :  -v2 + 2 v3 = 0                ->  v2 = 2 v3
row 2 :  -v1 + 2.5 v2 - v3 = 0
         -v1 + 5 v3 - v3 = 0           ->  v1 = 4 v3
row 1 :  1.5 v1 - v2 = 4
         6 v3 - 2 v3 = 4               ->  v3 = 1.00 V

         v2 = 2.00 V,  v1 = 4.00 V
```

Check it against the circuit, not against the algebra. Node 3: 1.00 V across its 1 kΩ
to ground draws 1 mA, and (2.00 − 1.00) V across the 1 kΩ bridge delivers exactly
1 mA. Node 2: 2 mA arrives from node 1, 1 mA leaves to ground through 2 kΩ, 1 mA leaves
to node 3. Node 1: 4.00 V across 2 kΩ is 2 mA to ground plus 2 mA across the bridge —
4 mA, which is what the source injects.

Two free consequences. The source sees $4.00\ \mathrm{V} / 4\ \mathrm{mA} = 1$ kΩ. And
the total power dissipated is $4.00\ \mathrm{V} \times 4\ \mathrm{mA} = 16$ mW; adding
the resistors up one at a time gives $8 + 4 + 2 + 1 + 1 = 16$ mW, which is the same
number, as it must be.

## Worked: a voltage source, and the row it replaces

Now drive the same kind of ladder with an ideal 12 V source instead: node 1 is held at
12 V, 1 kΩ runs from node 1 to node 2, 2 kΩ from node 2 to ground, 1 kΩ from node 2 to
node 3, and 1 kΩ from node 3 to ground.

The trouble is that node 1's KCL row is now useless to you: whatever current the source
has to supply, it supplies, so the row constrains nothing you were trying to find. What
you know instead is the voltage. So throw the row away and write the thing you do know
in its place — a 1 on the diagonal, zeros elsewhere, and the known voltage on the right.

```text
stamped, before any replacement (mS, and 12 V is not yet used):

        [  1.0  -1.0   0.0 ]        [ v1 ]     [ i1 ]
   G =  [ -1.0   2.5  -1.0 ]        [ v2 ]  =  [  0 ]
        [  0.0  -1.0   2.0 ]        [ v3 ]     [  0 ]

row 1 replaced by "v1 = 12":

        [  1.0   0.0   0.0 ]        [ v1 ]     [ 12 ]   <- volts
        [ -1.0   2.5  -1.0 ]        [ v2 ]  =  [  0 ]   <- milliamps
        [  0.0  -1.0   2.0 ]        [ v3 ]     [  0 ]

row 2 :  -12 + 2.5 v2 - v3 = 0     ->  2.5 v2 - v3 = 12
row 3 :        -v2 + 2 v3  = 0     ->  v2 = 2 v3

         5 v3 - v3 = 12   ->  v3 = 3.00 V,  v2 = 6.00 V
```

The source current follows from Ohm's law on the one resistor it feeds:
$(12 - 6)/1\,\mathrm{k}\Omega = 6$ mA, so the network presents $12/6 = 2$ kΩ. Series
and parallel agree: $1\,\mathrm{k} + \big(2\,\mathrm{k} \parallel (1\,\mathrm{k} +
1\,\mathrm{k})\big) = 1 + 1 = 2$ kΩ.

Notice what the replacement cost. The stamped matrix was symmetric; after the
substitution row 1 reads $[1, 0, 0]$ while column 1 still holds the $-1$ from the
resistor, and the symmetry is gone. There is a tidier route that keeps it: since $v_1$
is known, move its contribution to the other side of the equation. In row 2 the term
$-1\ \mathrm{mS} \times 12\ \mathrm{V} = -12$ mA is a known number, so send it right
and delete node 1 from the system entirely:

```text
        [ 2.5  -1.0 ] [ v2 ]  =  [ 12 ]  mA
        [-1.0   2.0 ] [ v3 ]     [  0 ]

determinant = 5.0 - 1.0 = 4.0
v2 = (2.0*12 + 1.0*0)/4.0 = 6.00 V      v3 = (1.0*12 + 2.5*0)/4.0 = 3.00 V
```

Same answer, smaller system, symmetry intact. A known voltage behaves exactly like a
current source of $gE$ injected into each node the source reaches through a conductance
$g$ — which is Norton's theorem, arriving here as a line of algebra rather than as a
theorem.

## What symmetry and singularity are telling you

$G$ comes out symmetric, $G_{ab} = G_{ba}$, and the reason is physical rather than
algebraic: a resistor conducts equally in both directions, so it stamps the same $-g$
into both off-diagonal slots. Symmetry is worth using — it halves the writing, and it
is a free check on a matrix you have just built by hand. It also fails the moment you
add a part with a preferred direction, which is the first sign that a transistor is not
going to fit in this framework unmodified.

The diagonal is a sum of positive conductances, and each off-diagonal entry in a row is
one of the terms of that same sum, negated. So the diagonal entry is at least as large
as everything else in its row put together, and strictly larger at any node with a
resistor to ground. That is **diagonal dominance**, and it is why elimination on a
conductance matrix never needs a row exchange — module 7 shows what happens to matrices
that do.

There is a sharper statement available, and it explains the failure case. For any
vector of node voltages,

$$v^{\mathsf T}Gv = \sum_{\text{resistors}} g\,(v_a - v_b)^2$$

which is the total power the network dissipates at those voltages. Every term is a
square times a positive conductance, so it is never negative; and it is zero only if
every resistor has equal voltages at its two ends. If every node has some resistive
path back to ground, that forces all the voltages to zero, the quantity is strictly
positive for every other $v$, and $G$ is invertible: the circuit has exactly one
answer. If some node does *not* have a path to ground — dangling, or reached only
through capacitors, which are open at DC — then you can raise that node's voltage
freely at no cost in power, $v^{\mathsf T}Gv$ is zero for a non-zero $v$, and $G$ is
singular. "Singular matrix" and "floating node" are the same sentence in two languages,
and the schematic editor's *under-determined* message is the third.

## The mistakes people actually make

**Adding the off-diagonal instead of subtracting it.** By far the most common. It is
tempting because the resistor is *there*, and everything else about stamping is
addition. The algebra that says otherwise is the split of $g(v_a - v_b)$: the
neighbour's voltage arrives with a minus sign because the current depends on the
*difference*. The symptom is distinctive — node voltages that come out larger than any
supply, or negative in a circuit with no negative supply — and the check is free, since
every row of a correct $G$ sums to the conductance from that node to ground, and to
exactly zero for a node with no ground connection at all.

**Forgetting that a resistor to ground touches only the diagonal.** The rule is usually
memorised as "add to two diagonals, subtract from two off-diagonals", which is right
three times out of four; ground has no row and no column to receive its half. Miss it
and you have quietly deleted every path to ground, which makes the matrix singular and
the solver complain about a circuit that looks fine on the screen.

**Putting resistances in the matrix.** $G$ is built from $1/R$, and "the sum of the
resistances at the node" is a plausible-sounding rule that is simply a different
quantity. The tell is that two resistors meeting at a node act like a *parallel*
combination as far as that node is concerned, and parallel combination adds
conductances. If the units of an entry are not siemens, the row is not KCL.

## Where this stops holding

- **Capacitors and inductors.** They do not have a conductance, so $G$ becomes the
  admittance matrix $Y(s) = G + sC + \Gamma/s$, with the same stamping rule and the
  same symmetry, but entries that are functions of $s$ rather than numbers. Everything
  structural above survives; module 10 builds a transfer function out of exactly that.
- **Dependent sources and transistors.** A voltage-controlled current source stamps a
  conductance into a row belonging to one pair of nodes from a voltage belonging to
  another, so the matrix is no longer symmetric, diagonal dominance is gone, and with
  it the guarantee that the circuit has a unique well-behaved answer. That is not a
  defect of the method — a circuit with enough feedback really can latch or oscillate,
  and the matrix is reporting it.
- **A voltage source that does not touch ground.** The row-replacement trick needs the
  source to fix one node's voltage outright. A source floating between two unknown
  nodes fixes only their difference, and needs either a supernode — one KCL equation
  written around both nodes at once, plus the difference as a second equation — or the
  modified nodal analysis the app's own solver uses, which adds the source's unknown
  current to the vector and grows the matrix by a row and a column. Read `MNA.dc` in
  `src/circuit.js`; it is thirty lines, and it is the stamping rule above plus that one
  extension.
- **Anything nonlinear.** There is no constant $G$ at all. What a simulator does is
  guess the voltages, linearise every nonlinear part about that guess, solve the
  resulting linear system by exactly the machinery in this module, and repeat until the
  guess stops moving. Nodal analysis does not go away; it gets called a few dozen times
  instead of once.
''',
                },
            ],
            "blanks": [
                {
                    "title": "Stamping a conductance matrix",
                    "minutes": 9,
                    "caption": "three unknown nodes, four resistors, worked in millisiemens",
                    "lang": "text",
                    "brief": r'''
A network with three unknown nodes. Node 1 has a 4 kΩ resistor to ground and a 1 kΩ
across to node 2. Node 2 has a 2 kΩ across to node 3. Node 3 has a 500 Ω to ground.
Nothing else. There is no resistor directly between nodes 1 and 3.

Work in millisiemens, so 1 kΩ is 1 mS, 2 kΩ is 0.5 mS, 4 kΩ is 0.25 mS and 500 Ω is
2 mS. Take each resistor in turn: its conductance is added to the diagonal entry of
each node it touches, and subtracted from the two off-diagonal entries joining them —
with ground getting neither, because it has no row and no column.

Nothing is executed here. This is the matrix you would write by hand before reaching
for a solver.
''',
                    "listing": """resistors        1 -- gnd : 4 k      = 0.25 mS
                 1 -- 2   : 1 k      = 1.00 mS
                 2 -- 3   : 2 k      = 0.50 mS
                 3 -- gnd : 500 R    = 2.00 mS


        [ G11  G12  G13 ]     [ ___    ___    ___  ]
   G =  [ G21  G22  G23 ]  =  [ ___    ___   -0.50 ]  mS
        [ G31  G32  G33 ]     [  0    -0.50   ___  ]


check:  every row of G sums to the conductance from that node to ground
        row 1 -> 0.25       row 2 -> 0.00       row 3 -> 2.00
""",
                    "blanks": [
                        {
                            "prompt": "$G_{11}$ — the diagonal entry for node 1.",
                            "hole": "?",
                            "opts": ["1.25", "0.75", "1.00", "5.00"],
                            "a": 0,
                            "why": "Two resistors touch node 1: the 4 kΩ to ground (0.25 mS) and the 1 kΩ across to node 2 (1.00 mS). The diagonal is their sum, $0.25 + 1.00 = 1.25$ mS. A resistor to ground counts in the diagonal exactly like any other — what it does not get is a column.",
                            "whys": [
                                "Two resistors touch node 1: the 4 kΩ to ground (0.25 mS) and the 1 kΩ across to node 2 (1.00 mS). The diagonal is their sum, $0.25 + 1.00 = 1.25$ mS. A resistor to ground counts in the diagonal exactly like any other — what it does not get is a column.",
                                "0.75 is $1.00 - 0.25$: the two conductances subtracted rather than added. Subtraction is what happens to the *off*-diagonal entries; the diagonal only ever accumulates.",
                                "1.00 counts the bridge to node 2 and forgets the resistor to ground. That is the commonest stamping slip, and it is the one that makes the matrix singular by quietly disconnecting the circuit from ground.",
                                "5.00 mS is $1/(4\\,\\mathrm{k}) + 1/(1\\,\\mathrm{k})$ worked out as if the values were in ohms — $0.25 + 1$ read off a calculator that was handed 4 and 1 rather than 4000 and 1000. Check the units of an entry: siemens, or the row is not KCL.",
                            ],
                        },
                        {
                            "prompt": "$G_{12}$ — the entry coupling node 1 to node 2.",
                            "hole": "?",
                            "opts": ["-1.00", "1.00", "-0.25", "0.00"],
                            "a": 0,
                            "why": "The 1 kΩ joining nodes 1 and 2 is 1.00 mS, and the off-diagonal entry is *minus* the shared conductance. The minus is not a convention: node 1's KCL contains $g(v_1 - v_2)$, and splitting that bracket sends $v_2$ across with a negative coefficient.",
                            "whys": [
                                "The 1 kΩ joining nodes 1 and 2 is 1.00 mS, and the off-diagonal entry is *minus* the shared conductance. The minus is not a convention: node 1's KCL contains $g(v_1 - v_2)$, and splitting that bracket sends $v_2$ across with a negative coefficient.",
                                "The magnitude is right and the sign is not. This is the single most common error in building $G$, and it is tempting because everything else about stamping is addition. The symptom is node voltages that come out above every supply in the circuit.",
                                "$-0.25$ mS is the 4 kΩ to ground, which does not join nodes 1 and 2 and so belongs to no off-diagonal entry at all.",
                                "Zero would be right if no resistor ran directly between the two nodes. One does — the 1 kΩ — and it is the only thing that couples them.",
                            ],
                        },
                        {
                            "prompt": "$G_{13}$ — the entry coupling node 1 to node 3.",
                            "hole": "?",
                            "opts": ["0.00", "-0.50", "-1.50", "0.25"],
                            "a": 0,
                            "why": "No resistor runs directly between nodes 1 and 3, so nothing was ever stamped into that slot and it stays zero. Nodes 1 and 3 do affect each other — through node 2 — but that influence lives in the *solution* of the system, not in a single entry of the matrix. $G$ records direct connections only, which is why a large network gives a mostly-empty matrix.",
                            "whys": [
                                "No resistor runs directly between nodes 1 and 3, so nothing was ever stamped into that slot and it stays zero. Nodes 1 and 3 do affect each other — through node 2 — but that influence lives in the *solution* of the system, not in a single entry of the matrix. $G$ records direct connections only, which is why a large network gives a mostly-empty matrix.",
                                "$-0.50$ mS is the 2 kΩ between nodes 2 and 3. It belongs in $G_{23}$ and $G_{32}$, and nowhere near node 1.",
                                "$-1.50$ mS is the two bridging conductances added together, as though the path from node 1 to node 3 were a single component. Series conductances do not add — and in any case the matrix never describes a path, only a part.",
                                "$+0.25$ mS is the resistor from node 1 to ground, in the wrong slot and with the wrong sign. Ground has no column, so nothing that touches it can appear off the diagonal.",
                            ],
                        },
                        {
                            "prompt": "$G_{21}$ — the entry coupling node 2 back to node 1.",
                            "hole": "?",
                            "opts": ["-1.00", "1.00", "-0.50", "0.00"],
                            "a": 0,
                            "why": "The same $-1.00$ mS as $G_{12}$. One resistor stamps both entries, because it conducts the same in both directions, and that is where the symmetry of $G$ comes from. Writing the upper triangle and mirroring it is legitimate for a resistor network, and it is the fastest hand check you have.",
                            "whys": [
                                "The same $-1.00$ mS as $G_{12}$. One resistor stamps both entries, because it conducts the same in both directions, and that is where the symmetry of $G$ comes from. Writing the upper triangle and mirroring it is legitimate for a resistor network, and it is the fastest hand check you have.",
                                "The magnitude is right and the sign is not, exactly as before — and if you wrote $+1.00$ here after writing $-1.00$ above, the asymmetry is the giveaway.",
                                "$-0.50$ mS is the 2 kΩ between nodes 2 and 3, which does not touch node 1.",
                                "Zero would say nodes 1 and 2 are not directly joined. The 1 kΩ joins them, and the matrix has to say so twice.",
                            ],
                        },
                        {
                            "prompt": "$G_{22}$ — the diagonal entry for node 2.",
                            "hole": "?",
                            "opts": ["1.50", "0.50", "3.50", "2.00"],
                            "a": 0,
                            "why": "Node 2 is touched by the 1 kΩ to node 1 (1.00 mS) and the 2 kΩ to node 3 (0.50 mS), and by nothing else: $1.50$ mS. It has no resistor to ground, and the consequence shows up in the check line — row 2 sums to exactly zero, because $1.50 - 1.00 - 0.50 = 0$.",
                            "whys": [
                                "Node 2 is touched by the 1 kΩ to node 1 (1.00 mS) and the 2 kΩ to node 3 (0.50 mS), and by nothing else: $1.50$ mS. It has no resistor to ground, and the consequence shows up in the check line — row 2 sums to exactly zero, because $1.50 - 1.00 - 0.50 = 0$.",
                                "0.50 mS counts only the 2 kΩ to node 3. The 1 kΩ arriving from node 1 touches node 2 just as much, and every resistor at a node adds to that node's diagonal.",
                                "3.50 mS has swept in the 2 mS of the 500 Ω resistor, which hangs off node 3 and ground. A resistor stamps only the two nodes it is wired to.",
                                "2.00 mS is the conductance of the 500 Ω resistor on its own — the right number for a different node.",
                            ],
                        },
                        {
                            "prompt": "$G_{33}$ — the diagonal entry for node 3.",
                            "hole": "?",
                            "opts": ["2.50", "2.00", "1.50", "0.50"],
                            "a": 0,
                            "why": "The 2 kΩ across to node 2 (0.50 mS) plus the 500 Ω to ground (2.00 mS) gives $2.50$ mS. The check line confirms it: row 3 is $0 - 0.50 + 2.50 = 2.00$ mS, which is exactly the conductance from node 3 to ground, as every row of a correctly stamped $G$ must be.",
                            "whys": [
                                "The 2 kΩ across to node 2 (0.50 mS) plus the 500 Ω to ground (2.00 mS) gives $2.50$ mS. The check line confirms it: row 3 is $0 - 0.50 + 2.50 = 2.00$ mS, which is exactly the conductance from node 3 to ground, as every row of a correctly stamped $G$ must be.",
                                "2.00 mS is the 500 Ω alone, with the bridge to node 2 left out — the mirror image of forgetting the ground resistor, and just as easy to do.",
                                "1.50 mS is $2.00 - 0.50$: the two conductances subtracted. Only the off-diagonal entries carry a minus sign.",
                                "0.50 mS is the bridge alone, with the path to ground dropped. Do that at every node and the matrix becomes singular, because you have described a circuit with no return path.",
                            ],
                        },
                    ],
                },
                {
                    "title": "A product, read as a combination of columns",
                    "minutes": 8,
                    "caption": "the same product three ways, and the order that changes the answer",
                    "lang": "text",
                    "brief": r'''
$Av$ is $v_1$ times the first column of $A$ plus $v_2$ times the second, and the matrix
of a composition is the outer map applied to each column of the inner one. Both claims
are worked here on the same pair of $2\times2$ matrices, so the three routes have to
agree — and then the order is swapped, and they stop agreeing.

Fill in the columns as combinations, not as rows dotted with vectors. The arithmetic is
identical; the reading is not.
''',
                    "listing": """A = [ 2  1 ]      B = [ 1  0 ]      v = [ 3 ]
    [ 0  3 ]          [ 2  1 ]          [ 1 ]


one map at a time
   B v   =  3 * [1]  +  1 * [0]   =  [ ___ ]
                [2]         [1]      [ ___ ]

   A(Bv) =  3 * [2]  +  7 * [1]   =  [ ___ ]
                [0]         [3]      [ ___ ]


as one matrix:  each column of AB is A applied to that column of B
   AB col 1 = A*[1] = 1*[2] + 2*[1] = [ ___ ]
                [2]     [0]     [3]   [ ___ ]

   AB col 2 = A*[0] = 0*[2] + 1*[1] = [1]
                [1]     [0]     [3]   [3]

   AB = [ 4  1 ]        AB v = ( 13, 21 )   -- agrees, as it must
        [ 6  3 ]


the other order
   BA col 1 = B*[2] = [2]      BA col 2 = B*[1] = [1]
                [0]   [4]                   [3]   [5]

   BA v = ( 7, 17 )   -- a different map entirely
""",
                    "blanks": [
                        {
                            "prompt": "First entry of $Bv$.",
                            "hole": "?",
                            "opts": ["3", "5", "2", "1"],
                            "a": 0,
                            "why": "$3 \\times 1 + 1 \\times 0 = 3$. Read as columns: three copies of $(1,2)$ and one copy of $(0,1)$, and only the first contributes anything to the top entry.",
                            "whys": [
                                "$3 \\times 1 + 1 \\times 0 = 3$. Read as columns: three copies of $(1,2)$ and one copy of $(0,1)$, and only the first contributes anything to the top entry.",
                                "5 is $3 + 2$, which mixes the first column's two entries together. Each entry of the answer collects only its own row from every column.",
                                "2 is the lower entry of the first column, taken without its weight of 3 and put in the wrong row.",
                                "1 is the first column's top entry with the weight of 3 not applied. The weights are the entries of $v$, and every one of them multiplies a whole column.",
                            ],
                        },
                        {
                            "prompt": "Second entry of $Bv$.",
                            "hole": "?",
                            "opts": ["7", "6", "3", "9"],
                            "a": 0,
                            "why": "$3 \\times 2 + 1 \\times 1 = 7$. Both columns reach the bottom entry here, which is what makes it the interesting one to check.",
                            "whys": [
                                "$3 \\times 2 + 1 \\times 1 = 7$. Both columns reach the bottom entry here, which is what makes it the interesting one to check.",
                                "6 is $3 \\times 2$ with the second column left out. It is a whole column, and it is weighted by 1 rather than by 0.",
                                "3 is the weight rather than the result — the number multiplying the first column, copied into the answer.",
                                "9 is $3 \\times (2 + 1)$: the two columns' lower entries added first and then weighted by 3. Each column carries its own weight.",
                            ],
                        },
                        {
                            "prompt": "First entry of $A(Bv)$.",
                            "hole": "?",
                            "opts": ["13", "9", "6", "21"],
                            "a": 0,
                            "why": "$Bv = (3, 7)$, so $A(Bv) = 3(2,0) + 7(1,3)$, and the top entry is $6 + 7 = 13$. The vector fed to $A$ is the *output* of $B$, which is what \"do $B$ first\" means.",
                            "whys": [
                                "$Bv = (3, 7)$, so $A(Bv) = 3(2,0) + 7(1,3)$, and the top entry is $6 + 7 = 13$. The vector fed to $A$ is the *output* of $B$, which is what \"do $B$ first\" means.",
                                "9 is $3 \\times 2 + 1 \\times 3$: $A$ applied to the original $v$ rather than to $Bv$. $B$ has to run first, and it changed $(3,1)$ into $(3,7)$.",
                                "6 is $3 \\times 2$ with the second column dropped — the weight of 7 belongs to it.",
                                "21 is the lower entry of the answer, $7 \\times 3$, which is the second column's contribution to the other row.",
                            ],
                        },
                        {
                            "prompt": "Second entry of $A(Bv)$.",
                            "hole": "?",
                            "opts": ["21", "13", "7", "28"],
                            "a": 0,
                            "why": "$3 \\times 0 + 7 \\times 3 = 21$. The first column of $A$ has a zero in that row, so the whole of the bottom entry comes from the second column.",
                            "whys": [
                                "$3 \\times 0 + 7 \\times 3 = 21$. The first column of $A$ has a zero in that row, so the whole of the bottom entry comes from the second column.",
                                "13 is the top entry of the same answer.",
                                "7 is the weight, not the result: it still has to multiply the 3 sitting in the second column.",
                                "28 is $7 \\times (3 + 1)$, which has pulled the 1 from the top of the second column down into the bottom row. Entries do not move between rows.",
                            ],
                        },
                        {
                            "prompt": "First entry of the first column of $AB$.",
                            "hole": "?",
                            "opts": ["4", "2", "5", "6"],
                            "a": 0,
                            "why": "The first column of $B$ is $(1,2)$, and $A(1,2) = 1(2,0) + 2(1,3) = (4, 6)$, so the top entry is 4. The composite matrix is built one column at a time, and each column is just the outer map applied to a vector — no new rule.",
                            "whys": [
                                "The first column of $B$ is $(1,2)$, and $A(1,2) = 1(2,0) + 2(1,3) = (4, 6)$, so the top entry is 4. The composite matrix is built one column at a time, and each column is just the outer map applied to a vector — no new rule.",
                                "2 is $A$'s own top-left entry, copied straight through as though composing two maps meant multiplying corresponding entries. It does not — that operation is not composition and has no meaning here.",
                                "5 is $2 + 3$, the two diagonal entries of $A$ added. Nothing in the product ever adds entries from different rows.",
                                "6 is the *lower* entry of this column. $A(1,2)$ has 4 on top and 6 below; the 6 comes from $2 \\times 3$, since $A$'s first column contributes nothing to that row.",
                            ],
                        },
                        {
                            "prompt": "Second entry of the first column of $AB$.",
                            "hole": "?",
                            "opts": ["6", "4", "2", "0"],
                            "a": 0,
                            "why": "$1 \\times 0 + 2 \\times 3 = 6$. Together with the 4 above it, that column is $(4,6)$ — and multiplying the finished $AB$ by $v$ returns $(13,21)$, the same answer the step-by-step route gave. Two agreeing routes is what associativity buys you.",
                            "whys": [
                                "$1 \\times 0 + 2 \\times 3 = 6$. Together with the 4 above it, that column is $(4,6)$ — and multiplying the finished $AB$ by $v$ returns $(13,21)$, the same answer the step-by-step route gave. Two agreeing routes is what associativity buys you.",
                                "4 is the entry above this one, from the row where $A$'s first column does contribute.",
                                "2 is the weight taken from $B$'s column without the 3 it multiplies.",
                                "0 is $A$'s lower-left entry on its own. It is genuinely zero, but the second column of $A$ also reaches this row, and it carries a weight of 2.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "One unknown node, two supplies",
                    "minutes": 6,
                    "brief": r'''
The mechanical rung. One node whose voltage you do not know, so one equation: KCL at
that node. Everything else in the circuit is either ground or held at a known voltage by
a supply.

This is not a divider — two sources feed the same node, and neither of them alone
decides the answer. Write down what leaves the node and what arrives, and set the two
equal.
''',
                    "prompt": "What voltage does the probed node sit at?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 4, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 7},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 2000},
                            {"id": "v2", "kind": "V", "x": 3, "y": 12, "rot": 1, "value": 5},
                            {"id": "g1", "kind": "GND", "x": 3, "y": 15},
                            {"id": "r2", "kind": "R", "x": 6, "y": 11, "rot": 0, "value": 3000},
                            {"id": "r3", "kind": "R", "x": 14, "y": 6, "rot": 1, "value": 1200},
                            {"id": "g2", "kind": "GND", "x": 14, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 17, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 7]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [11, 3]},
                            {"a": [3, 13], "b": [3, 15]},
                            {"a": [3, 11], "b": [5, 11]},
                            {"a": [7, 11], "b": [11, 11]},
                            {"a": [11, 11], "b": [11, 3]},
                            {"a": [11, 3], "b": [17, 3]},
                            {"a": [14, 3], "b": [14, 5]},
                            {"a": [14, 7], "b": [14, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Upper supply", "value": "10.0 V, through 2.00 kΩ"},
                        {"label": "Lower supply", "value": "5.00 V, through 3.00 kΩ"},
                        {"label": "To ground", "value": "1.20 kΩ"},
                    ],
                    "aside": "Both supplies are measured from the same ground, so the node has exactly one "
                             "unknown voltage and there is exactly one equation to write.",
                    "check": "return c.vout();",
                    "answer": 4.0,
                    "tol": 0.05,
                    "unit": "V",
                    "hint": "Currents arriving: $(10 - v)/2000$ and $(5 - v)/3000$. Current leaving: "
                            "$v/1200$. Multiplying every term by 6000 clears all three denominators at once.",
                    "wrong": "If you got 8.00 V, you have left the 1.20 kΩ to ground out of the equation; "
                             "it carries 3.33 mA, ten times what the lower supply contributes, so dropping "
                             "it moves the answer a long way. If you got 3.00 V or 1.00 V, that is the "
                             "circuit solved with one supply acting and the other shorted — one half of a "
                             "superposition, and the two halves have to be added.",
                    "why": r'''
```
KCL at the node:   arriving = leaving

  (10 - v)/2000  +  (5 - v)/3000  =  v/1200

multiply through by 6000:

  3(10 - v)  +  2(5 - v)  =  5 v
  30 - 3v    +  10 - 2v   =  5 v
  40                      = 10 v

  v = 4.00 V
```
The same thing as a $1\times1$ matrix equation, which is what this is:
$G = 1/2 + 1/3 + 1/1.2 = 1.667$ mS is the total conductance at the node, and
$i = 10/2 + 5/3 = 6.667$ mA is what the two supplies inject once you convert each of
them to its Norton equivalent. Then $v = i/G = 6.667/1.667 = 4.00$ V.

Worth checking the direction of every current afterwards, because it is free: 4.00 V is
below both supplies, so both of them deliver — 3.00 mA through the 2 kΩ and 0.33 mA
through the 3 kΩ, and 3.33 mA leaves through the 1.2 kΩ. Had the node come out above
5 V, the lower supply would have been *absorbing* current rather than supplying it,
which is perfectly legal and catches people out.
''',
                },
                {
                    "title": "Two unknown nodes, and a current in the middle",
                    "minutes": 8,
                    "brief": r'''
Two nodes you do not know, so a $2\times2$ system. The rung where the matrix starts
earning its keep.

The quantity asked for is not a node voltage. No probe reads it, and no single divider
gives it: you have to solve for both node voltages first and then take the difference
across one resistor. Getting into the habit of asking "which unknown is this, and is it
one of the ones I am solving for?" before starting is worth more than any shortcut.
''',
                    "prompt": "How much current flows through the 4.00 kΩ resistor that joins the two unknown nodes?",
                    "note": "Give the magnitude in milliamps, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 9},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 3000},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 6000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "r3", "kind": "R", "x": 13, "y": 3, "rot": 0, "value": 4000},
                            {"id": "r4", "kind": "R", "x": 17, "y": 6, "rot": 1, "value": 2000},
                            {"id": "g2", "kind": "GND", "x": 17, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 20, "y": 3},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [9, 3]},
                            {"a": [9, 3], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [14, 3], "b": [17, 3]},
                            {"a": [17, 3], "b": [17, 5]},
                            {"a": [17, 7], "b": [17, 9]},
                            {"a": [17, 3], "b": [20, 3]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "9.00 V"},
                        {"label": "Supply to node A", "value": "3.00 kΩ"},
                        {"label": "Node A to ground", "value": "6.00 kΩ"},
                        {"label": "Node A to node B", "value": "4.00 kΩ"},
                        {"label": "Node B to ground", "value": "2.00 kΩ (probed)"},
                    ],
                    "aside": "Two KCL rows, two unknowns. The supply node is not one of them — it is held "
                             "at 9.00 V and its row is replaced by that known value.",
                    # The resistor is found by id and its own value is read back out of the
                    # netlist, so a diagram edited to a different value cannot leave this
                    # check quietly agreeing with a stale answer.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r3'; })[0];
return 1000 * Math.abs(d.v[r.n1] - d.v[r.n2]) / r.value;
''',
                    "answer": 0.75,
                    "tol": 0.01,
                    "unit": "mA",
                    "hint": "Write KCL at node A and at node B. Node B's row is short — only two resistors "
                            "touch it — so solve that one for $v_A$ in terms of $v_B$ and substitute.",
                    "wrong": "If you got 1.50 mA, that is the current the supply delivers, which splits at "
                             "node A between the 6 kΩ to ground and the branch you were asked about. If you "
                             "got 2.25 mA, you have used the full 9 V across the 4 kΩ rather than the "
                             "difference between the two node voltages.",
                    "why": r'''
```
KCL at A, with the supply node held at 9 V   (multiply by 12000)

  (vA - 9)/3000 + vA/6000 + (vA - vB)/4000 = 0
  4(vA - 9)     + 2 vA    + 3(vA - vB)     = 0
  9 vA - 3 vB = 36                ->   3 vA -  vB = 12

KCL at B                                     (multiply by 4000)

  (vB - vA)/4000 + vB/2000 = 0
  (vB - vA)      + 2 vB    = 0    ->   vA = 3 vB

substitute:   9 vB - vB = 12   ->   vB = 1.50 V,   vA = 4.50 V

current through the 4 k :   (4.50 - 1.50)/4000 = 0.750 mA
```
In matrix form the same pair reads

$$\begin{pmatrix} 0.750 & -0.250 \\ -0.250 & 0.750 \end{pmatrix}
\begin{pmatrix} v_A \\ v_B\end{pmatrix} =
\begin{pmatrix} 3.00 \\ 0 \end{pmatrix}$$

in millisiemens and milliamps, where the 3.00 mA on the right is the known 9 V acting
through the 3 kΩ conductance — the source eliminated rather than given a row of its own,
which keeps the matrix symmetric. That symmetry is not a coincidence of these values:
the two nodes are joined by one resistor, and one resistor stamps the same $-0.250$ mS
into both off-diagonal slots.

This particular network is also a plain ladder, so you can check the whole thing by
series and parallel: $4\,\mathrm{k} + 2\,\mathrm{k} = 6\,\mathrm{k}$, in parallel with
the 6 kΩ gives 3 kΩ, plus the 3 kΩ in series is 6 kΩ, so the supply delivers
$9/6\,\mathrm{k} = 1.50$ mA and node A sits at $9 - 1.50 \times 3 = 4.50$ V. Half of
that 1.50 mA goes to ground and half continues, which is the 0.750 mA. Take the check
while it is available — the next rung has no such shortcut.
''',
                },
                {
                    "title": "A bridge, and the resistance it presents",
                    "minutes": 10,
                    "brief": r'''
Five resistors, and not one pair of them is in series or in parallel with another. Every
resistor's current depends on every other resistor's current, so there is no order in
which to collapse the network, and the reduction technique that has worked since EE101
has simply run out.

What has not run out is nodal analysis. Two unknown nodes, two KCL rows, and then one
division. The quantity asked for is a resistance, and no resistor in the circuit has
that value.
''',
                    "prompt": "What resistance does the 10.0 V supply see?",
                    "note": "Give the answer in kilohms, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 9, "rot": 1, "value": 10},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 12},
                            {"id": "r1", "kind": "R", "x": 7, "y": 5, "rot": 0, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 11, "y": 8, "rot": 1, "value": 2000},
                            {"id": "g1", "kind": "GND", "x": 11, "y": 11},
                            {"id": "r5", "kind": "R", "x": 14, "y": 5, "rot": 0, "value": 5000},
                            {"id": "r4", "kind": "R", "x": 18, "y": 8, "rot": 1, "value": 4000},
                            {"id": "g2", "kind": "GND", "x": 18, "y": 11},
                            {"id": "r3", "kind": "R", "x": 10, "y": 2, "rot": 0, "value": 3000},
                        ],
                        "wires": [
                            {"a": [3, 10], "b": [3, 12]},
                            {"a": [3, 8], "b": [3, 5]},
                            {"a": [3, 5], "b": [6, 5]},
                            {"a": [8, 5], "b": [11, 5]},
                            {"a": [11, 5], "b": [11, 7]},
                            {"a": [11, 9], "b": [11, 11]},
                            {"a": [11, 5], "b": [13, 5]},
                            {"a": [15, 5], "b": [18, 5]},
                            {"a": [18, 5], "b": [18, 7]},
                            {"a": [18, 9], "b": [18, 11]},
                            {"a": [3, 5], "b": [3, 2]},
                            {"a": [3, 2], "b": [9, 2]},
                            {"a": [11, 2], "b": [18, 2]},
                            {"a": [18, 2], "b": [18, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "10.0 V"},
                        {"label": "Supply to node A", "value": "1.00 kΩ"},
                        {"label": "Node A to ground", "value": "2.00 kΩ"},
                        {"label": "Supply to node B (over the top)", "value": "3.00 kΩ"},
                        {"label": "Node B to ground", "value": "4.00 kΩ"},
                        {"label": "Node A to node B (the bridge)", "value": "5.00 kΩ"},
                    ],
                    "aside": "The resistance a source sees is the voltage it holds divided by the current it "
                             "delivers, and the current it delivers is the sum of what leaves through every "
                             "resistor attached to it.",
                    # Both the supply voltage and its current come out of the solve, so the
                    # division is the definition of resistance rather than a restatement of
                    # numbers that also appear in the diagram.
                    "check": r'''
const d = c.dc();
const ids = Object.keys(d.currents);
c.assert(ids.length === 1, 'one source, so "the supply current" means one thing');
return c.values('V')[0] / Math.abs(d.currents[ids[0]]) / 1000;
''',
                    "answer": 2.095,
                    "tol": 0.02,
                    "unit": "kΩ",
                    "hint": "Solve for $v_A$ and $v_B$ first. Then the supply's current is what leaves it "
                            "through the 1 kΩ plus what leaves through the 3 kΩ, and the resistance is "
                            "10 V divided by that total.",
                    "wrong": "If you got 2.10 kΩ, you have left the 5 kΩ bridge out and reduced two "
                             "independent arms: $(1+2)\\parallel(3+4) = 3\\parallel 7 = 2.10$ kΩ. That is "
                             "the correct answer for a *balanced* bridge, where the two middle nodes "
                             "happen to sit at the same voltage and the bridge carries nothing; this one "
                             "is not balanced. If you got 2.92 kΩ, you have divided 10 V by the 3.42 mA "
                             "leaving through the 1 kΩ alone and missed the second path out of the supply.",
                    "why": r'''
```
KCL at A                                      (multiply by 10000)

  (vA - 10)/1000 + vA/2000 + (vA - vB)/5000 = 0
  10(vA - 10)    + 5 vA    + 2(vA - vB)     = 0
                                              ->  17 vA -  2 vB = 100

KCL at B                                      (multiply by 60000)

  (vB - 10)/3000 + vB/4000 + (vB - vA)/5000 = 0
  20(vB - 10)    + 15 vB   + 12(vB - vA)    = 0
                                              ->  47 vB - 12 vA = 200

from the first :  vA = (100 + 2 vB)/17
substitute     :  799 vB - 1200 - 24 vB = 3400
                  775 vB = 4600           ->  vB = 5.9355 V
                                              vA = 6.5806 V

supply current :  (10 - 6.5806)/1000 + (10 - 5.9355)/3000
               =   3.4194 mA          +  1.3548 mA
               =   4.7742 mA

resistance     :  10.0 / 4.7742e-3 = 2094.6 ohm = 2.095 k
```
Two things are worth noticing about that answer. It is smaller than the 2.10 kΩ the same
four arms would present with the bridge removed, and it has to be: adding a resistor
between two points that were at different voltages opens a new path for current, and
more current at the same voltage means less resistance. And 5.9355 V is *not* the same
as 6.5806 V, which is the whole reason the bridge carries anything at all —
$(6.5806 - 5.9355)/5000 = 129\ \mu$A flows through it, from A to B. Set the four arms so
that those two voltages match and the bridge carries nothing, the network really does
reduce by series and parallel, and you have a Wheatstone bridge at balance: the standard
way to measure a resistance to five figures using nothing but a null detector.
''',
                },
                {
                    "title": "Three unknown nodes, two supplies, and a power",
                    "minutes": 12,
                    "brief": r'''
The full-sized version. Three unknown node voltages, so a $3\times3$ system; two
supplies, at different voltages, in different parts of the network; and a quantity that
is quadratic in the unknowns, so it cannot be superposed and has to be computed once,
at the end, from the finished answer.

One of the two supplies is doing something worth noticing on the way past. Work out the
node voltages before deciding which way any current flows.
''',
                    "prompt": "How much power does the 2.00 kΩ resistor between the first and second unknown nodes dissipate?",
                    "note": "Give the answer in milliwatts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 7, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 10},
                            {"id": "r1", "kind": "R", "x": 6, "y": 3, "rot": 0, "value": 1000},
                            {"id": "r5", "kind": "R", "x": 10, "y": 6, "rot": 1, "value": 6000},
                            {"id": "g1", "kind": "GND", "x": 10, "y": 9},
                            {"id": "r2", "kind": "R", "x": 13, "y": 3, "rot": 0, "value": 2000},
                            {"id": "r6", "kind": "R", "x": 17, "y": 6, "rot": 1, "value": 4000},
                            {"id": "v2", "kind": "V", "x": 17, "y": 9, "rot": 1, "value": 5},
                            {"id": "g2", "kind": "GND", "x": 17, "y": 12},
                            {"id": "r3", "kind": "R", "x": 20, "y": 3, "rot": 0, "value": 3000},
                            {"id": "r4", "kind": "R", "x": 24, "y": 6, "rot": 1, "value": 5000},
                            {"id": "g3", "kind": "GND", "x": 24, "y": 9},
                        ],
                        "wires": [
                            {"a": [3, 8], "b": [3, 10]},
                            {"a": [3, 6], "b": [3, 3]},
                            {"a": [3, 3], "b": [5, 3]},
                            {"a": [7, 3], "b": [10, 3]},
                            {"a": [10, 3], "b": [10, 5]},
                            {"a": [10, 7], "b": [10, 9]},
                            {"a": [10, 3], "b": [12, 3]},
                            {"a": [14, 3], "b": [17, 3]},
                            {"a": [17, 3], "b": [17, 5]},
                            {"a": [17, 7], "b": [17, 8]},
                            {"a": [17, 10], "b": [17, 12]},
                            {"a": [17, 3], "b": [19, 3]},
                            {"a": [21, 3], "b": [24, 3]},
                            {"a": [24, 3], "b": [24, 5]},
                            {"a": [24, 7], "b": [24, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Left supply", "value": "12.0 V, through 1.00 kΩ to node A"},
                        {"label": "Node A to ground", "value": "6.00 kΩ"},
                        {"label": "Node A to node B", "value": "2.00 kΩ"},
                        {"label": "Node B to the 5.00 V supply", "value": "4.00 kΩ"},
                        {"label": "Node B to node C", "value": "3.00 kΩ"},
                        {"label": "Node C to ground", "value": "5.00 kΩ"},
                    ],
                    "aside": "Both supplies are ideal and both are referenced to the same ground, so each "
                             "of them fixes one node outright and neither adds an unknown. Three nodes are "
                             "left over, and they need three equations.",
                    # Power belongs to no node, so the check takes the drop across the named
                    # resistor and that resistor's own value out of the solved circuit.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r2'; })[0];
const u = d.v[r.n1] - d.v[r.n2];
return 1000 * u * u / r.value;
''',
                    "answer": 3.168,
                    "tol": 0.03,
                    "unit": "mW",
                    "hint": "Node C's row involves only $v_B$ and $v_C$, so use it to eliminate $v_C$ "
                            "immediately. That leaves two equations in $v_A$ and $v_B$, and the power only "
                            "needs those two.",
                    "wrong": "If you got 72.0 mW, you have put the whole 12 V across the 2.00 kΩ; only "
                             "the difference between the two node voltages, 2.52 V, appears across it. If "
                             "you got 2.52, that is the voltage across it and not yet a power. And if you "
                             "worked the circuit twice, once per supply, and added the two powers, the "
                             "answer is wrong for a reason worth carrying: power is quadratic in the node "
                             "voltages, so only the voltages superpose.",
                    "why": r'''
```
KCL at A, node held nowhere, supply at 12 V   (multiply by 6000)

  (vA - 12)/1000 + vA/6000 + (vA - vB)/2000 = 0
  6(vA - 12)     + vA      + 3(vA - vB)     = 0    ->  10 vA -  3 vB        = 72

KCL at B, with the 5 V supply on the far side of the 4 k   (multiply by 12000)

  (vB - vA)/2000 + (vB - 5)/4000 + (vB - vC)/3000 = 0
  6(vB - vA)     + 3(vB - 5)     + 4(vB - vC)     = 0
                                                   -> -6 vA + 13 vB - 4 vC = 15

KCL at C                                       (multiply by 15000)

  (vC - vB)/3000 + vC/5000 = 0
  5(vC - vB)     + 3 vC    = 0                     ->         -5 vB + 8 vC =  0

from C  :  vC = 0.625 vB
into B  :  -6 vA + 13 vB - 2.5 vB = 15    ->  -6 vA + 10.5 vB = 15
from A  :  vA = 7.2 + 0.3 vB
        :  -43.2 - 1.8 vB + 10.5 vB = 15  ->   8.7 vB = 58.2

  vB = 6.6897 V      vA = 9.2069 V      vC = 4.1810 V

current through the 2 k :  (9.2069 - 6.6897)/2000 = 1.2586 mA
power                   :  (1.2586e-3)^2 * 2000   = 3.168 mW
```
Now the thing worth having noticed. Node B sits at 6.69 V, which is *above* the 5.00 V
supply attached to it through the 4 kΩ. Current therefore flows from node B into that
supply — 0.422 mA of it — and the supply is absorbing power rather than delivering it.
Nothing is wrong; an ideal voltage source holds its voltage and takes whatever current
that requires, in either direction, and a real one in this position would be charging.
The solver reports the same thing, as a positive current where the 12 V supply's is
negative.

The other trap is the one the wrong-answer note names. Superposition would have you
solve the circuit twice, once per supply, and add — and for $v_A$, $v_B$ and $v_C$ that
is perfectly correct. It is not correct for the power, because
$(v_1 + v_2)^2 \neq v_1^2 + v_2^2$. Superpose the voltages if you like, then square
once, at the end.
''',
                },
            ],
            "build": {
                "title": "A matched 600 Ω attenuator",
                "minutes": 28,
                "brief": r'''
Two specifications at once, which is what makes this a linear-systems problem rather
than an arithmetic one.

A 10 V source drives a network of resistors, which drives a 600 Ω load. The load and
its ground are already on the canvas, with the probe on it. Add resistors between the
source and the load so that:

- the **load voltage is exactly 5.00 V**, and
- the **source sees a resistance of 600 Ω**, so it delivers 16.67 mA.

Either condition alone is easy. Together they are not: a single 600 Ω resistor in
series gives 5 V at the load, but the source then sees 1200 Ω and delivers only
8.33 mA. Satisfying one specification breaks the other, and you have to solve for both
together.

## What is being measured

- the probe voltage, which must be 5.00 V
- the current out of the source, which must be $10/600 = 16.67$ mA. Since the source
  is ideal and sits at a fixed 10 V, that current *is* the input resistance: measuring
  16.67 mA is measuring 600 Ω, with nothing else needed.
- that the 600 Ω load is still running from the probed node to ground. A network that
  meets both numbers with the load disconnected has met neither, because the load is
  half of what determines them.

## Where to start

Two unknowns, two conditions. Call the resistor you put in series $R_s$ and the one
you put across the load $R_p$. Write down what the input resistance is in terms of
them, write down what fraction of 10 V reaches the load, set both equal to their
targets, and solve the pair.

More than one topology works. A series resistor and a shunt across the load is the
smallest answer; the symmetric three-resistor arrangement used in telephone practice —
a series resistor, a shunt to ground, and a second series resistor — also works, and
the checks accept either, because they measure the circuit rather than compare it to a
picture.

This part has a name. It is a 6 dB pad, matched to 600 Ω, and 600 Ω attenuators like
it sat in every audio and telephone rack for most of a century.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p5", "kind": "R", "x": 13, "y": 7, "rot": 1, "value": 600},
                        {"id": "p6", "kind": "GND", "x": 13, "y": 10},
                        {"id": "p7", "kind": "OUT", "x": 15, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [13, 5], "b": [13, 6]},
                        {"a": [13, 8], "b": [13, 10]},
                        {"a": [13, 5], "b": [15, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 200},
                        {"id": "p3", "kind": "R", "x": 7, "y": 7, "rot": 1, "value": 800},
                        {"id": "p4", "kind": "GND", "x": 7, "y": 10},
                        {"id": "p8", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 200},
                        {"id": "p5", "kind": "R", "x": 13, "y": 7, "rot": 1, "value": 600},
                        {"id": "p6", "kind": "GND", "x": 13, "y": 10},
                        {"id": "p7", "kind": "OUT", "x": 15, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [7, 6]},
                        {"a": [7, 8], "b": [7, 10]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [11, 5], "b": [13, 5]},
                        {"a": [13, 5], "b": [13, 6]},
                        {"a": [13, 8], "b": [13, 10]},
                        {"a": [13, 5], "b": [15, 5]},
                    ],
                },
                "checks": [
                    {"name": "one 10 V source drives the network", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source; found ' + c.count('V') + '.');
c.close(c.values('V')[0], 10, 0.001, 'the supply voltage');
'''},
                    {"name": "the 600 Ω load is still across the probed node", "code": r'''
const out = c.outNode();
c.assert(c.net.parts.some(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 600) <= 6 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
}), 'The 600 Ohm load must run from the probed node to ground. Both specifications ' +
   'depend on it being connected, so a design that meets them with the load removed ' +
   'has not met them at all.');
'''},
                    {"name": "the load receives 5.00 V", "code": r'''
c.close(c.vout(), 5.0, 0.01,
  'the voltage at the load — half the supply, which is 6 dB of attenuation');
'''},
                    {"name": "the source sees 600 Ω, so it delivers 16.67 mA", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
const i = Math.abs(cur[ids[0]]);
const rin = 10.0 / i;
c.close(i, 10.0 / 600.0, 0.02,
  'the current out of the 10 V source, which is 10/600 = 16.67 mA when the input ' +
  'resistance is 600 Ohm — this circuit presents ' +
  (i > 0 ? rin.toFixed(0) + ' Ohm' : 'an open circuit'));
'''},
                ],
                "hints": [
                    "Take the series-plus-shunt answer first. With $R_s$ in series and $R_p$ across the 600 Ω load, the load node sees $R_p$ in parallel with 600; call that $X$.",
                    "The input resistance is $R_s + X$ and it must be 600. The load voltage is $10X/(R_s+X)$ and it must be 5, so $X$ is exactly half the total: $X = 300$ and therefore $R_s = 300$.",
                    "Then solve $1/300 = 1/R_p + 1/600$ for $R_p$, which gives 600 Ω. So a 300 Ω series resistor and a 600 Ω shunt resistor across the load.",
                    "For the symmetric three-resistor version instead, use 200 Ω in series, 800 Ω to ground, then 200 Ω in series into the load. Check it: $600 + 200 = 800$, in parallel with 800 gives 400, plus 200 gives 600.",
                    "If the voltage is right but the current is wrong, you have solved one equation and not the other — a plain 600 Ω series resistor is exactly that failure.",
                ],
            },
            "derive": {
                "title": "Reciprocity, out of a symmetric matrix",
                "minutes": 14,
                "vars": ["G_a", "G_b", "G_c", "i_1", "i_2", "v_1", "v_2"],
                "brief": r'''
Two accessible nodes and a ground. A conductance $G_a$ runs from node 1 to ground, $G_b$
from node 1 across to node 2, and $G_c$ from node 2 to ground — the plain T, which is
what most two-port resistive networks reduce to. Currents $i_1$ and $i_2$ are injected
at the two nodes from outside.

Build $Gv = i$, invert it, and then ask a question that has no obvious answer: drive
node 1 and measure node 2; then drive node 2 with the same current and measure node 1.
Should those two voltages be equal? There is nothing symmetric about the network — $G_a$
and $G_c$ are different components — so there is no reason from the picture to expect
it.

For a $2\times2$ matrix, $\begin{pmatrix}p & q\\ r & s\end{pmatrix}^{-1} =
\dfrac{1}{ps-qr}\begin{pmatrix}s & -q\\ -r & p\end{pmatrix}$.
''',
                "steps": [
                    {
                        "prompt": "Write KCL at node 1: the current leaving through $G_a$ plus the current leaving through $G_b$ equals $i_1$. Collect the terms and give the coefficient of $v_1$.",
                        "answer": "G_a + G_b",
                        "placeholder": "a sum of two conductances",
                        "hint": "The two currents leaving node 1 are $G_a(v_1 - 0)$ and $G_b(v_1 - v_2)$. Expand both brackets and gather everything multiplying $v_1$.",
                        "deconstruct": [
                            "$G_a v_1 + G_b(v_1 - v_2) = i_1$.",
                            "Expanding: $G_a v_1 + G_b v_1 - G_b v_2 = i_1$.",
                            "The two terms in $v_1$ combine, which is the diagonal entry $G_{11}$ — every conductance touching node 1, including the one that goes to ground.",
                        ],
                    },
                    {
                        "prompt": "From the same row, give the coefficient of $v_2$.",
                        "answer": "-G_b",
                        "placeholder": "one conductance, with a sign",
                        "hint": "Only $G_b$ involves $v_2$ at all, and it arrived inside the bracket $G_b(v_1 - v_2)$.",
                        "deconstruct": [
                            "$G_a$ leads to ground, whose voltage is zero, so it contributes nothing to any column but its own diagonal.",
                            "Expanding $G_b(v_1 - v_2)$ leaves $-G_b v_2$.",
                            "The minus sign is the whole content of the off-diagonal rule, and it is there because current depends on a *difference* of voltages.",
                        ],
                    },
                    {
                        "prompt": "Node 2's row is the mirror image, so $G = \\begin{pmatrix} G_a + G_b & -G_b \\\\ -G_b & G_b + G_c\\end{pmatrix}$. Expand its determinant and simplify.",
                        "answer": "G_a G_b + G_a G_c + G_b G_c",
                        "placeholder": "three products, all of them positive",
                        "hint": "$(G_a+G_b)(G_b+G_c) - (-G_b)(-G_b)$. Multiply the first bracket out, then subtract $G_b^2$.",
                        "deconstruct": [
                            "$(G_a+G_b)(G_b+G_c) = G_aG_b + G_aG_c + G_b^2 + G_bG_c$.",
                            "The product of the two off-diagonal entries is $(-G_b)(-G_b) = G_b^2$, and it is subtracted.",
                            "The $G_b^2$ terms cancel, leaving three products — one for each pair of conductances, and every one positive, which is why this matrix is never singular unless a conductance is zero.",
                        ],
                    },
                    {
                        "prompt": "Drive node 1 only, so $i = (i_1,\\ 0)$. Use the inverse formula from the brief to write $v_2$ in terms of $G_a$, $G_b$, $G_c$ and $i_1$.",
                        "answer": "\\frac{G_b i_1}{G_a G_b + G_a G_c + G_b G_c}",
                        "placeholder": "a single conductance over the determinant, times i_1",
                        "hint": "$v = G^{-1}i$. The second row of $G^{-1}$ is $\\frac{1}{D}(-(-G_b),\\ G_a+G_b) = \\frac{1}{D}(G_b,\\ G_a+G_b)$, and the second entry of $i$ is zero, so only the first survives.",
                        "deconstruct": [
                            "Swapping the diagonal and negating the off-diagonal turns $G$ into $\\begin{pmatrix} G_b+G_c & G_b \\\\ G_b & G_a+G_b\\end{pmatrix}$, all over the determinant.",
                            "Multiplying that by $(i_1,\\ 0)$ keeps only the first column.",
                            "The second entry of the first column is $G_b$, so $v_2 = G_b i_1 / D$.",
                        ],
                    },
                    {
                        "prompt": "Now drive node 2 instead, with $i = (0,\\ i_2)$, and write $v_1$.",
                        "answer": "\\frac{G_b i_2}{G_a G_b + G_a G_c + G_b G_c}",
                        "placeholder": "the same shape as the previous answer",
                        "hint": "This time only the second column of the inverse survives. Its first entry is the off-diagonal one — and the inverse of a symmetric matrix is symmetric, so it is the same $G_b$ you met a moment ago.",
                        "deconstruct": [
                            "$(0,\\ i_2)$ selects the second column of the inverse, $\\frac{1}{D}(G_b,\\ G_a+G_b)$.",
                            "Its first entry is $G_b$, so $v_1 = G_b i_2 / D$.",
                            "Compare with the previous step. The transfer resistance $v_2/i_1$ and the transfer resistance $v_1/i_2$ are the same number, $G_b/D$, even though $G_a \\neq G_c$.",
                        ],
                    },
                    {
                        "prompt": "Put numbers in: $G_a = 1$ mS, $G_b = 2$ mS, $G_c = 1$ mS, and 3 mA injected at node 1 alone. What is $v_2$, in volts?",
                        "answer": "1.2",
                        "placeholder": "a number, in volts",
                        "hint": "Work the determinant first, in $(\\mathrm{mS})^2$: $1\\cdot 2 + 1\\cdot 1 + 2\\cdot 1$. Then $v_2 = G_b i_1 / D$, and mS times mA over $(\\mathrm{mS})^2$ is volts.",
                        "deconstruct": [
                            "$D = 2 + 1 + 2 = 5\\ (\\mathrm{mS})^2$.",
                            "$G_b i_1 = 2 \\times 3 = 6$, in mS·mA.",
                            "$v_2 = 6/5 = 1.2$ V — and the same 3 mA injected at node 2 instead would put 1.2 V on node 1, which is the result this derivation was built to reach.",
                        ],
                    },
                ],
                "closing": r'''
That equality has a name — **reciprocity** — and the derivation above proves it only for
the T. The general statement is one line of linear algebra: $G$ is symmetric because a
resistor conducts the same in both directions, the inverse of a symmetric matrix is
symmetric, and the transfer resistance from node $j$ to node $k$ is the $(k,j)$ entry of
$G^{-1}$. Symmetric matrix, symmetric inverse, and the two measurements agree — for a
network of any size, with any topology, without solving it.

It is worth knowing how easy that is to lose. Add one transistor, or any other
controlled source, and the matrix stops being symmetric: a controlled source stamps a
conductance into a row belonging to one pair of nodes from a voltage belonging to
another, with nothing to balance it on the other side of the diagonal. Reciprocity then
fails, and it fails in a useful direction — an amplifier that passed signal backwards as
readily as forwards would be no use at all. Isolation is exactly the absence of the
symmetry proved above.

The measurement is also a genuine laboratory technique. Injecting a known current at one
node and reading the voltage at another gives you one entry of $G^{-1}$ directly, and
reciprocity says you may take it from whichever of the two nodes is easier to reach.
''',
            },
            "lab": {
                "title": "Building a matrix out of a map, and a network out of a matrix",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
This lab makes one claim concrete: **a matrix is what a linear map does to the basis
vectors, and nothing else**. Once you believe that, you never have to remember how to
assemble a conductance matrix again, because you can always recover it by asking the
circuit what it does.

- `as_matrix(f, n)` takes a linear function `f` from $\mathbb{R}^n$ to $\mathbb{R}^n$
  and returns its $n\times n$ matrix. Apply `f` to each standard basis vector in turn
  and stack the results as **columns**.
- `injected(v, resistors, n)` is a physical map. Given the node voltages `v` for nodes
  $1 \dots n$ (ground is node 0 and always 0 V), it returns the current that must be
  injected at each node from outside to hold those voltages. Each resistor `(a, b, R)`
  carries $(v_a - v_b)/R$ from `a` to `b`; that current leaves node `a` and arrives at
  node `b`, so add it to entry `a` and subtract it from entry `b`, skipping node 0.
- `solve_network(n, resistors, fixed)` solves the circuit. Build the matrix with
  `as_matrix`, replace the row of each node in `fixed` with a 1 on its diagonal and the
  known voltage on the right, solve with `np.linalg.solve`, and return the voltages
  with 0.0 prepended for ground.

The pleasing part is the third check: `injected` *is* a linear map, so running it
through `as_matrix` hands you the conductance matrix $G$ — the one the textbook builds
by the stamping rule — without you ever writing the stamping rule down.

## On indexing

Nodes are numbered from 1, arrays from 0, so node `k` lives at index `k - 1`. Ground is
node 0 and has no entry at all: `if a:` is false exactly when `a` is 0, which is the
whole guard you need.
''',
                "files": [{"name": "main.py", "content": r'''
"""A matrix is what a linear map does to the basis vectors."""

import numpy as np


def as_matrix(f, n):
    """The n-by-n matrix of the linear map f, built column by column."""
    # TODO: for each j, apply f to the j-th standard basis vector; those are the columns.
    return np.zeros((n, n))


def injected(v, resistors, n):
    """Currents that must be injected at nodes 1..n to hold the voltages v."""
    # TODO: prepend 0.0 for ground, then for each (a, b, R) add (v[a]-v[b])/R
    #       to entry a and subtract it from entry b, skipping node 0.
    return np.zeros(n)


def solve_network(n, resistors, fixed):
    """Node voltages, with 0.0 first for ground. `fixed` is {node: volts}."""
    # TODO: build G with as_matrix, replace the fixed rows, and solve.
    return np.zeros(n + 1)


if __name__ == "__main__":
    pad = [(1, 2, 200.0), (2, 0, 800.0), (2, 3, 200.0), (3, 0, 600.0)]
    v = solve_network(3, pad, {1: 10.0})
    print("node voltages:", v)
    print("supply current:", injected(v[1:], pad, 3)[0], "A")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""A matrix is what a linear map does to the basis vectors.

Verified by running this file on the attenuator from the build exercise:
    node voltages [0, 10, 6.666666666666667, 5.0]
    supply current 0.016666666666666666 A, so the input resistance is exactly 600 ohms
"""

import numpy as np


def as_matrix(f, n):
    """The n-by-n matrix of the linear map f, built column by column."""
    cols = []
    for j in range(n):
        e = np.zeros(n)
        e[j] = 1.0
        cols.append(np.asarray(f(e), dtype=float))
    return np.column_stack(cols)


def injected(v, resistors, n):
    """Currents that must be injected at nodes 1..n to hold the voltages v."""
    out = np.zeros(n)
    volts = np.concatenate(([0.0], np.asarray(v, dtype=float)))
    for (a, b, R) in resistors:
        cur = (volts[a] - volts[b]) / R
        if a:
            out[a - 1] += cur
        if b:
            out[b - 1] -= cur
    return out


def solve_network(n, resistors, fixed):
    """Node voltages, with 0.0 first for ground. `fixed` is {node: volts}."""
    G = as_matrix(lambda v: injected(v, resistors, n), n)
    rhs = np.zeros(n)
    for node, volts in fixed.items():
        G[node - 1, :] = 0.0
        G[node - 1, node - 1] = 1.0
        rhs[node - 1] = float(volts)
    return np.concatenate(([0.0], np.linalg.solve(G, rhs)))


if __name__ == "__main__":
    pad = [(1, 2, 200.0), (2, 0, 800.0), (2, 3, 200.0), (3, 0, 600.0)]
    v = solve_network(3, pad, {1: 10.0})
    print("node voltages:", v)
    print("supply current:", injected(v[1:], pad, 3)[0], "A")
'''}],
                "hints": [
                    "In `as_matrix`, make `e = np.zeros(n)` fresh inside the loop and set `e[j] = 1.0`. Reusing one array and clearing it works too, but a fresh one is harder to get wrong.",
                    "`np.column_stack(cols)` assembles a list of vectors as columns. `np.array(cols)` would stack them as *rows*, which gives you the transpose — for a symmetric $G$ the tests would still pass, so check it on the rotation instead.",
                    "In `injected`, `volts = np.concatenate(([0.0], v))` puts ground at index 0 so that `volts[a]` reads naturally for any node number including 0.",
                    "`if a:` is False only when `a == 0`, which is exactly the ground case you want to skip. Write both guards, one for each end of the resistor.",
                    "In `solve_network`, replace the fixed rows *after* building `G`, never before — the stamping has to see the whole network first.",
                ],
                "tests": [
                    {"name": "the matrix of a rotation", "code": r'''
M = as_matrix(lambda v: np.array([-v[1], v[0]]), 2)
assert M.shape == (2, 2), f"expected a 2x2 matrix, got shape {M.shape}"
want = np.array([[0.0, -1.0], [1.0, 0.0]])
assert np.allclose(M, want), \
    f"a quarter turn anticlockwise has matrix [[0,-1],[1,0]], got\n{M}\n" \
    "(if you got its transpose, the images were stacked as rows instead of columns)"
'''},
                    {"name": "injected currents obey Ohm's law", "code": r'''
i = injected([12.0], [(1, 0, 3000.0)], 1)
assert abs(i[0] - 0.004) < 1e-12, \
    f"holding one node at 12 V through 3 k to ground needs 4 mA injected, got {i[0]}"
i2 = injected([9.0, 3.0], [(1, 2, 20000.0), (2, 0, 10000.0)], 2)
assert abs(i2[0] - 0.0003) < 1e-12, f"node 1 injects (9-3)/20k = 300 uA, got {i2[0]}"
assert abs(i2[1] - 0.0) < 1e-12, \
    f"node 2 is in balance here: 300 uA in through 20k, 300 uA out through 10k, got {i2[1]}"
'''},
                    {"name": "the map recovers the conductance matrix", "code": r'''
res = [(1, 2, 20000.0), (2, 0, 10000.0)]
G = as_matrix(lambda v: injected(v, res, 2), 2)
want = np.array([[5e-05, -5e-05], [-5e-05, 1.5e-04]])
assert np.allclose(G, want), \
    f"the conductance matrix should be\n{want}\ngot\n{G}"
assert np.allclose(G, G.T), "a resistor network always gives a symmetric matrix"
'''},
                    {"name": "the attenuator from the build exercise", "code": r'''
pad = [(1, 2, 200.0), (2, 0, 800.0), (2, 3, 200.0), (3, 0, 600.0)]
v = solve_network(3, pad, {1: 10.0})
assert len(v) == 4, f"three unknown nodes plus ground is four voltages, got {len(v)}"
assert abs(v[0]) < 1e-12, "node 0 is ground and must be exactly 0 V"
assert abs(v[1] - 10.0) < 1e-9, f"node 1 is held at 10 V by the source, got {v[1]}"
assert abs(v[2] - 6.666666666666667) < 1e-9, f"the middle node sits at 6.667 V, got {v[2]}"
assert abs(v[3] - 5.0) < 1e-9, f"the load must see 5.00 V, got {v[3]}"
isup = injected(v[1:], pad, 3)[0]
assert abs(isup - 0.016666666666666666) < 1e-12, \
    f"10 V into 600 ohms is 16.667 mA, got {isup} A"
'''},
                    {"name": "a ladder, and KCL at every free node", "code": r'''
lad = [(1, 2, 1000.0), (2, 0, 1000.0), (2, 3, 1000.0), (3, 0, 1000.0)]
v = solve_network(3, lad, {1: 10.0})
assert abs(v[2] - 4.0) < 1e-9, f"node 2 should sit at 4 V, got {v[2]}"
assert abs(v[3] - 2.0) < 1e-9, f"node 3 should sit at 2 V, got {v[3]}"
i = injected(v[1:], lad, 3)
assert abs(i[1]) < 1e-12 and abs(i[2]) < 1e-12, \
    f"nothing is injected at nodes 2 and 3, so KCL must balance there; got {i}"
assert abs(i[0] - 0.006) < 1e-12, f"the supply delivers 6 mA, got {i[0]}"
'''},
                ],
            },
            "quiz": {
                "title": "Maps, matrices and node equations",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The clearest way to read the product $Av$ is:",
                        "opts": [
                            "as a lookup in a table of numbers",
                            "as a rotation of $v$, always",
                            "as a system of equations with no meaning on its own",
                            "as a combination of the columns of $A$, weighted by the entries of $v$",

                        ],
                        "a": 3,
                        "why": r'''
$Av = v_1a_1 + v_2a_2 + \dots$, where $a_j$ is the $j$-th column. Every later idea gets
easier from this reading: the column space is the set of reachable outputs, a singular
matrix is one whose columns fail to span, and the matrix of a composition is the second
map applied to the first one's columns. Rotations are one particular family of linear
maps, not what matrices are.
''',
                    },
                    {
                        "q": "How do you find the $j$-th column of the matrix of a linear map $T$?",
                        "opts": [
                            "apply $T$ to the vector of all ones",
                            "compute $T(e_j)$, the image of the $j$-th basis vector",
                            "take the $j$-th row of the inverse",
                            "take the $j$-th eigenvector",
                        ],
                        "a": 1,
                        "why": r'''
$Ae_j$ selects column $j$ exactly, so if $A$ is to represent $T$ then column $j$ must
be $T(e_j)$. This is the entire recipe for turning a map into a matrix, and it is what
the lab does. Applying $T$ to the vector of all ones discards the information: it gives one
vector, the sum of all the columns, from which the individual columns cannot be
recovered.
''',
                    },
                    {
                        "q": "Nodal analysis of a resistor network with $n$ unknown node voltages produces:",
                        "opts": [
                            "$n$ nonlinear equations",
                            "one equation for each resistor",
                            "$n$ linear equations, one per node, each of them KCL at that node",
                            "$n$ linear equations, one per loop, each of them KVL round that loop",
                        ],
                        "a": 2,
                        "why": r'''
One unknown per node, one equation per node, and each equation says that the currents
leaving that node sum to zero — Kirchhoff's current law. They are linear because Ohm's
law is. The loop-based alternative, one KVL equation per loop, is mesh analysis, which is a real method
but a different one, with one unknown per loop instead. Counting equations against
unknowns before starting is the cheapest way to catch a mistake in the setup.
''',
                    },
                    {
                        "q": "Why is the conductance matrix $G$ symmetric?",
                        "opts": [
                            "because a resistor conducts equally in both directions, so what it contributes to $G_{ab}$ it also contributes to $G_{ba}$",
                            "because every network is a ladder",
                            "because the supply is ideal",
                            "because conductance is a positive number",
                        ],
                        "a": 0,
                        "why": r'''
The stamping rule subtracts the same $1/R$ from $G_{ab}$ and from $G_{ba}$, and it does
so because the component itself has no preferred direction. Symmetry is therefore a
statement about the physics, and it is worth using: it halves the work of writing the
matrix down, and it fails the moment you add a component that *does* have a direction,
such as a transistor or a dependent source.
''',
                    },
                    {
                        "q": "Your solver reports that $G$ is singular. The most likely cause is:",
                        "opts": [
                            "too many resistors in the network",
                            "resistor values that are too large",
                            "a negative resistor value",
                            "a node with no resistive path to ground, so nothing determines its voltage",
                        ],
                        "a": 3,
                        "why": r'''
A floating node — one connected only through capacitors, or left dangling, or attached
to a section that is itself isolated — has no equation that pins it, so infinitely many
voltage vectors satisfy the system and the matrix has no inverse. It is the same
failure the schematic editor reports as "under-determined". Very large resistances make
the matrix badly *conditioned*, which is a numerical accuracy problem, not the same
thing as singular.
''',
                    },
                ],
            },
        },

        # ---- M7 -----------------------------------------------------------
        {
            "title": "Elimination, rank and the equations with no answer",
            "summary": "Solving $Gv = i$ is elimination, and everything that can go wrong announces itself as a pivot that is zero or nearly so. What the matrix is saying then is that the circuit does not decide the answer.",
            "concepts": [
                "**Elimination** subtracts multiples of one row from the rows below it until the matrix is upper triangular, after which back-substitution reads the unknowns off from the bottom up. The entry used to clear a column is its **pivot**.",
                "The determinant is the product of the pivots, with a sign flip for every row exchange. So $\\det G = 0$ is not a separate fact to be checked — it is what elimination *finds*, in the form of a column no row exchange can supply a pivot for.",
                "**Rank** is the number of pivots. For an $n \\times n$ matrix, rank $n$ means the columns are independent and $Gv = i$ has exactly one solution for every $i$; anything less means it has none or infinitely many, and which of those depends on $i$.",
                "The **nullspace** is the set of $v$ with $Gv = 0$. A non-zero member is a pattern of node voltages that drives no current anywhere, so no measurement can tell it from zero — which is exactly what a section of circuit with no resistive path to ground is, written in the language of the matrix.",
                "Nearly singular is a different illness from singular. A matrix can be invertible and still turn a 0.1% error in the data into a 50% error in the answer; the **condition number** measures how much, and mixing a 1 Ω with a 10 MΩ in one network is how you earn a bad one. **Partial pivoting** — always eliminating with the largest available entry in the column — is the cheap defence, and it is why library solvers do it without being asked.",
            ],
            "read": [
                {
                    "title": "Elimination is what you already do to a circuit",
                    "minutes": 15,
                    "body": r'''
Three unknown node voltages, and the way anybody actually finds them: not by inverting a
matrix, but by picking a node, writing Kirchhoff's current law there, rearranging that
one equation so it says what the node's voltage is in terms of its neighbours, and
substituting the result into every other equation the node appears in. After that
substitution the node is gone. What is left is a smaller circuit with one fewer unknown,
and you do the same thing again, until a single unknown remains and can be divided out —
after which you walk back up the chain filling in the ones you removed.

That procedure has a name in linear algebra, and the claim here is stronger than "it
resembles Gaussian elimination". It **is** Gaussian elimination, step for step. Every
number you divide by along the way is a conductance, and the matrix left behind on the
nodes that remain is the conductance matrix of a real circuit — one you could build out
of components and measure.

## One step, written out

Node $k$'s row of $Gv = i$ says that the currents leaving node $k$ balance whatever is
injected there:

$$G_{kk}v_k + \sum_{j \ne k} G_{kj}v_j = i_k$$

The diagonal entry $G_{kk}$ is the sum of every conductance touching node $k$. The
off-diagonal $G_{kj}$ is $-g_{kj}$, the negated conductance of the resistor joining $k$
to $j$, and it is zero when no resistor joins them. Solve that row for $v_k$:

$$v_k = \frac{1}{G_{kk}}\Big(i_k - \sum_{j \ne k}G_{kj}v_j\Big)$$

and take any other row $l$. It contains one term in $v_k$, namely $G_{lk}v_k$.
Substituting turns that term into $\frac{G_{lk}}{G_{kk}}\big(i_k - \sum_j
G_{kj}v_j\big)$, so after gathering, row $l$'s coefficient of $v_j$ has changed from
$G_{lj}$ to

$$G_{lj} - \frac{G_{lk}G_{kj}}{G_{kk}}$$

and its right-hand side from $i_l$ to $i_l - \frac{G_{lk}}{G_{kk}}i_k$. Both are the same
operation applied to the whole augmented row: *row $l$ minus $(G_{lk}/G_{kk})$ times row
$k$*. The number everything was divided by, $G_{kk}$, is the **pivot** — and here it is
not an abstraction. It is the total conductance seen at the node being removed.

## What the step does to the circuit

Look at when the correction $-G_{lk}G_{kj}/G_{kk}$ can be non-zero. It needs both
$G_{lk}$ and $G_{kj}$ non-zero, so node $k$ has to touch both $l$ and $j$. And since
$G_{lk} = -g_{lk}$ and $G_{kj} = -g_{kj}$, the correction is

$$-\frac{g_{lk}\,g_{kj}}{G_{kk}}$$

a *negative* number added to the $(l,j)$ entry — which is exactly what stamping a new
resistor between $l$ and $j$ would do. So elimination does not delete a node. It
**replaces it with a resistor between every pair of its neighbours**, each new
conductance being the product of the two conductances that met at the removed node,
divided by the total conductance there.

That is a statement about circuits, not a metaphor for the algebra. Unsolder the node,
solder in the new resistors, and every node you kept sits at exactly the voltage it did
before.

## Worked example: a ladder, eliminated from the far end

A 1 kΩ from node 1 to ground; 500 Ω from node 1 to node 2; 1 kΩ from node 2 to ground;
500 Ω from node 2 to node 3; 500 Ω from node 3 to ground. Eight milliamps are injected at
node 1 and nowhere else. Working in millisiemens and milliamps means the voltages come
out in volts with no conversions anywhere.

```
G (mS)                 i (mA)        where each diagonal comes from

[  3  -2   0 ]         [ 8 ]         node 1:  1 + 2     = 3
[ -2   5  -2 ]         [ 0 ]         node 2:  2 + 1 + 2 = 5
[  0  -2   4 ]         [ 0 ]         node 3:  2 + 2     = 4
```

Eliminate node 3 first. It is the far end of the ladder, its row is short, and nothing
says elimination has to start at the top left. Its pivot is 4 mS. The only other row
containing $v_3$ is row 2, whose entry is $-2$, so the multiplier is $-2/4 = -0.5$:

```
G[2][2] : 5 - (-2)(-2)/4 = 5 - 1 = 4 mS
rhs     : 0 - (-0.5)(0)          = 0
```

Check that against the circuit rather than trusting the arithmetic. Node 2 reached node 3
through 500 Ω, and node 3 reached ground through 500 Ω, so what node 2 now sees in that
direction is 1 kΩ — one millisiemens where two used to be. $5 - 2 + 1 = 4$. The matrix
and the soldering iron agree.

Now eliminate node 2, whose pivot is the 4 mS just produced. Row 1's entry is $-2$, so
the multiplier is again $-0.5$:

```
G[1][1] : 3 - (-2)(-2)/4 = 3 - 1 = 2 mS
rhs     : 8 - (-0.5)(0)          = 8 mA
```

And again in the circuit: of node 2's 4 mS, two go back to node 1, leaving 2 mS — 500 Ω —
to ground. Node 1 reaches that through its own 500 Ω, so the whole branch is 1 kΩ, one
millisiemens, and with node 1's own 1 kΩ that is 2 mS in total.

```
v1 = 8 mA / 2 mS = 4.00 V

back-substitute
row 2:  -2 v1 + 4 v2 = 0   ->  v2 = 2(4.00)/4 = 2.00 V
row 3:  -2 v2 + 4 v3 = 0   ->  v3 = 2(2.00)/4 = 1.00 V
```

Take the free check. At node 2, in from node 1 is $(4.00-2.00)/500 = 4.00$ mA; out to
ground is $2.00/1000 = 2.00$ mA and out to node 3 is $(2.00-1.00)/500 = 2.00$ mA. Four in,
four out. At node 1, the injected 8.00 mA leaves as 4.00 mA to ground and 4.00 mA to node
2. Nothing is left over anywhere.

The determinant is the product of the pivots: $4 \times 4 \times 2 = 32$ mS³. Eliminate
the same matrix top-down instead and the pivots are $3$, $11/3$ and $32/11$ — three
different numbers whose product is also 32, because the determinant does not care in
which order you removed the nodes.

## Worked example: the resistors a removed node leaves behind

Three terminals and one internal node, joined to terminal 1 by 1 kΩ, to terminal 2 by
1 kΩ and to terminal 3 by 2 kΩ, with nothing injected at the internal node and nothing
else touching it. One elimination step removes it.

```
G_1 = 1 mS   G_2 = 1 mS   G_3 = 0.5 mS
pivot = 1 + 1 + 0.5 = 2.5 mS

between 1 and 2 :  (1)(1)/2.5   = 0.400 mS  ->  2.50 kΩ
between 1 and 3 :  (1)(0.5)/2.5 = 0.200 mS  ->  5.00 kΩ
between 2 and 3 :  (1)(0.5)/2.5 = 0.200 mS  ->  5.00 kΩ
```

Those three resistors are the star-to-delta transformation, and it fell out of one
elimination step rather than being looked up. The textbook form agrees:
$R_{12} = (R_1R_2 + R_2R_3 + R_3R_1)/R_3 = (1 + 2 + 2)/2 = 2.50$ kΩ, and the same
numerator over $R_2$ and over $R_1$ gives 5.00 kΩ twice.

The diagonal moves too, and moves consistently. Terminal 1's diagonal loses
$G_1^2/2.5 = 0.4$ mS, so the 1 mS that used to run to the internal node is replaced by
$0.400 + 0.200 = 0.600$ mS — precisely the two new resistors leaving terminal 1. Nothing
went to ground that was not there before, which is what has to happen if the reduced
matrix is to be an honest conductance matrix.

Count what that step cost: one node removed, three resistors created. A node with $n$
neighbours leaves $n(n-1)/2$ behind. That is **fill-in**, and on a netlist with twenty
thousand nodes it is the difference between a simulation that runs and one that does not.

## The mistakes

**The sign of the multiplier.** In a conductance matrix every off-diagonal entry is
negative, so every multiplier is negative, so every elimination step *adds* a multiple of
the pivot row. "Subtract the multiplier times the pivot row" and "add half of the pivot
row" describe the same operation here, and the second is what your hand wants to write. Keep
doing it as subtraction of a signed multiplier anyway: the moment you carry the sign in
your head instead of on the paper, you will lose it on the first matrix that is not a
plain conductance matrix — and a full MNA matrix, with its $\pm 1$ entries for voltage
sources, is exactly that.

**Leaving the right-hand side behind.** The multiplier applies to the augmented row,
$i$ included. Forget it and you have an upper-triangular matrix belonging to your problem
and a right-hand side belonging to a different one. Nothing in the shape of the result
complains: back-substitution runs, numbers come out, and the determinant and the rank are
both still correct, because they depend only on $G$. Only the voltages are wrong. This is
why the lab in this module eliminates `np.column_stack([A, b])` in one pass instead of
eliminating `A` and trying to replay the operations onto `b` afterwards.

**Reading the determinant off the original diagonal.** For the ladder that gives
$3 \times 5 \times 4 = 60$ against the true 32. Product-of-the-diagonal is a fact about
*triangular* matrices, and elimination is the thing that makes a matrix triangular.

## Where this stops

**At a zero pivot.** Dividing by $G_{kk}$ needs $G_{kk} \ne 0$, and the repair is a row
exchange: find a row lower down with a non-zero entry in this column and swap it up. A
connected network's conductance matrix never needs one, because every diagonal entry is a
sum of positive conductances — but a full MNA matrix has rows whose diagonal entry is
structurally zero, and elimination without exchanges falls over on the first of them. And
if *no* remaining row has a usable entry in that column, no exchange helps and there is no
pivot to be had at all. That case is the next reading.

**At a nearly zero pivot.** A pivot of $10^{-9}$ does not stop anything. It multiplies
every rounding error already in the row by $10^{9}$ and hands back an answer with the
usual number of digits. Choosing the largest available entry in the column instead —
partial pivoting — costs one comparison per column, and it is the reading after next.

**At scale.** A SPICE netlist has tens of thousands of nodes, each touching three or four
others, so $G$ is huge and almost entirely zero. Dense elimination is $O(n^3)$ and out of
the question; what makes circuit simulation possible is that a good elimination *order*
keeps the fill-in small. Eliminate the low-degree nodes first and few new resistors
appear — that is minimum-degree ordering, and it is inside every sparse LU library there
is. Where even that is not enough, elimination is abandoned altogether for an iterative
method that never forms the factors.
''',
                },
                {
                    "title": "The circuit that cannot make up its mind",
                    "minutes": 14,
                    "body": r'''
> The circuit is under-determined — usually a node connected to nothing, or two voltage
> sources in a loop.

That is the schematic editor's own message, and it is worth reading as a physical
statement rather than an error to be cleared. Something has been asked of the circuit
that the circuit does not decide.

## What "no answer" means for a circuit

Put a node in a schematic whose only connection is a capacitor, and ask for the DC
operating point. At DC no current flows through a capacitor, so nothing in the circuit
constrains that node's voltage at all. Leave it charged to 3 V and it stays at 3 V. Leave
it at $-40$ V and it stays there. The circuit is not broken; the question has no answer,
because the quantity being asked about is not determined by anything in the drawing.

The matrix says so plainly. Node $k$'s row of $Gv = i$ is the KCL at node $k$, and if
every conductance touching node $k$ is zero, that row is all zeros and reads
$0 = i_k$ — either $0 = 0$, true whatever $v_k$ is, or $0 = \text{something}$, which no
$v$ can satisfy. Two different failures, and which one you get depends on the
right-hand side.

## Rank is the count of pivots

Run elimination and count the columns that produced a usable pivot. That count is the
**rank**. For an $n \times n$ matrix:

- rank $n$: every column has a pivot, the determinant (their product) is non-zero, and
  $Gv = i$ has exactly one solution for every $i$;
- rank $< n$: at least one column ran out of pivot, the determinant is zero, and $Gv = i$
  has either no solution or infinitely many.

Nothing here needs a separate determinant calculation. Elimination *finds* the
singularity, in the honest form of a column with nothing in it to divide by.

## The nullspace, in the circuit

The **nullspace** is the set of $v$ with $Gv = 0$. Read that as a circuit statement: a
set of node voltages that drives no current through any component. If a non-zero $v$ does
that, then adding any multiple of it to a solution gives another solution, and no meter
anywhere in the circuit can tell the two apart.

Two nodes joined to each other by 1 kΩ and to nothing else, plus a third node with 2 kΩ
to ground:

```
G (mS)
[  1  -1    0  ]
[ -1   1    0  ]
[  0   0   0.5 ]
```

Column 1's pivot is 1. The multiplier for row 2 is $-1/1 = -1$, so row 2 gains a whole
copy of row 1:

```
[  1  -1    0  ]
[  0   0    0  ]
[  0   0   0.5 ]
```

Column 2 now has nothing at or below the row we are working on. There is no pivot in it,
no row exchange can produce one, and the column is simply passed over. Column 3 supplies a
pivot of 0.5. Two pivots, so rank 2 — and the determinant is zero, because the eliminated
matrix carries a zero on its diagonal exactly where the missing pivot should have been.

The nullspace is spanned by $v = (1, 1, 0)$:

```
row 1 :  (1)(1) + (-1)(1) + 0     = 0
row 2 : (-1)(1) +  (1)(1) + 0     = 0
row 3 :       0 +       0 + (0.5)(0) = 0
```

Physically: lift both island nodes by the same amount. The 1 kΩ between them sees the
same difference across it as before — none — so it carries nothing, and nothing else
touches them. The island's absolute potential is invisible to the circuit.

### Which failure, and why the source decides

**Nothing injected into the island**, $i = (0,\,0,\,i_3)$. The eliminated row 2 reads
$0 = 0$: true. There are infinitely many solutions, $v = (t,\,t,\,0)$ plus the particular
one, for every real $t$. Node 3 is untouched by any of this and sits at $i_3/0.5$
regardless — a rank-deficient matrix does not spoil the parts of the circuit that are
determined.

**One milliamp injected at node 1**, $i = (1,\,0,\,0)$. Row 2 becomes $0 = 0 + 1$, which
is false. There is no solution at all. And that is the physics rather than an artefact:
you are pushing a milliamp of charge into a region with no path out of it. There is no
steady state to find. On whatever stray capacitance the island has, its voltage ramps at
$dv/dt = i/C$ and keeps ramping until something breaks down.

Both failures came out of the same missing pivot, which is precisely why $\det G = 0$
cannot tell you which of them you have. It says the columns are dependent. Whether the
right-hand side happens to lie in the space those columns span is a separate question.

## The near miss, with numbers

Give node 2 a 10 MΩ to ground — a leakage path, or a deliberate bleed resistor. Node 3
never had anything to do with the trouble, so set it aside and look at the island alone,
where 10 MΩ is $10^{-4}$ mS:

```
G (mS)                     det = (1)(1.0001) - (-1)(-1)
[  1     -1      ]             = 1.0001 - 1
[ -1      1.0001 ]             = 1.0e-4 mS^2
```

Now the matrix is invertible. Elimination gives pivots 1 and $10^{-4}$, rank 2, and a
determinant that is not zero — merely ten thousand times smaller than the entries that
produced it. Inverting a matrix in millisiemens gives one in kilohms:

```
G^-1 = (1 / 1.0e-4) [ 1.0001   1 ]  =  [ 10001  10000 ] kΩ
                    [ 1        1 ]     [ 10000  10000 ]
```

Inject one microamp at node 1:

```
v1 = 10001 kΩ * 1 uA = 10.001 V
v2 = 10000 kΩ * 1 uA = 10.000 V
```

Confirm it in the circuit. The microamp has only one route to ground — through the
10 MΩ — and $1\,\mu\text{A} \times 10\,\text{M}\Omega = 10.000$ V. Getting there it also
crosses the 1 kΩ, which drops $1\,\mu\text{A} \times 1\,\text{k}\Omega = 1$ mV, putting
node 1 one millivolt above node 2. Both node voltages are enormous compared with anything
in the drive, and the direction they went in is the old nullspace vector: the pair rose
together, $(1,1)$, with a millivolt of structure riding on top.

Singular is the limit of this. Push the 10 MΩ towards infinity and the answer runs off to
infinity along $(1,1)$; the singular case is not a different phenomenon but the endpoint
of a continuous one. It also cuts the other way: a real capacitor leaks through
gigaohms, so a real circuit is never exactly singular, only appallingly conditioned. The
build in this module puts a deliberate 10 kΩ where that leakage would otherwise be, and
the difference between 10 kΩ and "whatever the leakage happens to be today" is the
difference between an input node at 0.00 V and an input node wherever the last transient
left it.

## The mistakes

**Reading $\det G = 0$ as "no solution".** It means no *unique* solution: none or
infinitely many, and the right-hand side chooses. The temptation is that "no solution" is
the memorable failure of simultaneous equations — two parallel lines, drawn in every
textbook — while "the same line twice" is the forgettable one; and that from outside, a
solver reports an error in both cases.

**Expecting a singular matrix to contain a zero row.** $\begin{pmatrix}1&2\\2&4
\end{pmatrix}$ has no zero row and no inverse. The island above has no zero row either:
both of its rows are full of entries, and it is singular because they sum to zero, not
because either is empty. Hunting for the empty row finds only the easiest case.

**Assuming the fault must be a missing wire.** In practice the usual causes are a
capacitor as a node's only connection at DC, and an open switch isolating a section. And
there is a second disease with the same symptom that this reading does not cover: two
ideal voltage sources wired in a loop. Every node there has a fine path to ground and the
conductance matrix is perfectly healthy; the dependency is between the two extra rows that
MNA adds for the sources, not between the node rows.

## Where this stops

**Rank is a yes-or-no about exact arithmetic, and floating point has no exact zeros.**
Elimination on the 10 MΩ network above produced a pivot of $10^{-4}$ mS, not 0. Halve the
leakage and it is $5\times10^{-5}$. Nothing in the numbers marks the place where "small"
becomes "zero", and no threshold is the correct one — which is why
`numpy.linalg.matrix_rank` takes a tolerance, why its default is proportional to the
largest singular value rather than an absolute number, and why the honest tool near the
boundary is the singular value decomposition rather than elimination. Elimination answers
"is there a pivot". The SVD answers "how far is this matrix from one that has no pivot",
which is usually the question you actually had.

**Rank deficiency is not always a fault to be repaired.** A floating section can be the
design: an isolated supply, a transformer secondary, a differential pair where only the
difference is ever used. The fix there is not to add a resistor until the matrix behaves.
It is to supply the missing physical statement — a ground reference — because the
matrix was right, and there genuinely was no answer until you said where zero was.

**And full rank on its own promises nothing about accuracy.** A matrix can have every
pivot it needs and still sit one part in a million away from one that does not. That is a
different illness with a different name and a different cure, and it is the next reading.
''',
                },
                {
                    "title": "Nearly singular, and what it costs",
                    "minutes": 14,
                    "body": r'''
A 1 Ω current-sense resistor and a 10 MΩ bias divider on the same board is not an exotic
circuit; it is Tuesday. Nothing about it is wrong. The ammeter works, the divider works,
and every voltage in it is perfectly well defined. What suffers is the *arithmetic* done
about it, and the damage is quiet: the answer comes back with the usual number of digits
and no warning attached to any of them.

## The question conditioning answers

You solve $Gv = i$. The data is never exact — the resistors have tolerances, the source
was measured, the numbers were rounded on the way in — so what you actually solved was

$$G(v + \delta v) = i + \delta i$$

Subtract the two, and because $G$ is linear, $G\,\delta v = \delta i$, so
$\delta v = G^{-1}\delta i$ and

$$\|\delta v\| \le \|G^{-1}\|\,\|\delta i\|$$

That is an absolute bound, and absolute bounds are not much use: a large error inside a
large answer may not matter at all. Make it relative. From $i = Gv$ we also have
$\|i\| \le \|G\|\,\|v\|$, hence $1/\|v\| \le \|G\|/\|i\|$, and multiplying the two
inequalities together:

$$\frac{\|\delta v\|}{\|v\|} \;\le\; \|G\|\,\|G^{-1}\|\;\frac{\|\delta i\|}{\|i\|}$$

Everything the matrix contributes has collected into a single factor. That factor is the
**condition number**

$$\kappa(G) = \|G\|\,\|G^{-1}\|$$

and it is the worst-case amplification from relative error in the data to relative error
in the answer. It is never below 1. A $\kappa$ of $10^{6}$ means an error in the sixth
digit of the data is entitled to reach the first digit of the answer.

For a symmetric matrix measured in the 2-norm, $\|G\| = \lambda_{\max}$ and
$\|G^{-1}\| = 1/\lambda_{\min}$ — a conductance matrix has real, positive eigenvalues —
so the whole thing reduces to a ratio you can compute:

$$\kappa_2(G) = \frac{\lambda_{\max}}{\lambda_{\min}}$$

## Worked example: one small resistor is enough

Node A has a 1 Ω to ground and reaches node B through 1 kΩ; node B has its own 1 kΩ to
ground. In millisiemens:

```
G (mS)                 G_AA = 1000 + 1 = 1001
[ 1001   -1 ]          G_BB =    1 + 1 =    2
[   -1    2 ]          G_AB =           -1
```

The eigenvalues come out of the trace and the determinant without touching an
eigenvector, because for a $2\times2$ they are the sum and the product:

```
trace = 1001 + 2          = 1003 mS
det   = (1001)(2) - (-1)^2 = 2001 mS^2

lambda^2 - 1003 lambda + 2001 = 0

disc  = 1003^2 - 4(2001) = 1006009 - 8004 = 998005
sqrt  = 999.002002

lmax  = (1003 + 999.002002)/2 = 1001.001001 mS
lmin  = (1003 - 999.002002)/2 =    1.998999 mS

kappa = 1001.001001 / 1.998999 = 500.75
```

Check the pair before going on: their product is $1001.001 \times 1.998999 = 2001$, the
determinant, and their sum is 1003, the trace. Both agree, so neither root was
mistyped.

A thousand-to-one spread in resistance bought a condition number of about five hundred,
and that is not a coincidence of these numbers: $\lambda_{\max}$ is essentially the
largest diagonal entry and $\lambda_{\min}$ essentially the smallest, so
$\kappa \approx 1001/2$.

Now what it costs, in volts. Drive the network with

```
i  = ( 1.000, 0.001 ) mA      ->   v = ( 1.000, 1.000 ) mV
```

(check it: $1001(0.001) - 1(0.001) = 1.000$ mA and $-1(0.001) + 2(0.001) = 0.001$ mA, so
that really is the solution). Now change the second current by one microamp — a change of
0.1% in the size of $i$ — and solve again:

```
i  = ( 1.000, 0.002 ) mA

v  = (1/2001) [ 2     1    ] ( 1.000 )  =  (1/2001) ( 2.002 )
              [ 1  1001    ] ( 0.002 )              ( 3.002 )

   = ( 1.00050, 1.50025 ) mV
```

Node B moved from 1.000 mV to 1.500 mV. A tenth of a percent in the data, fifty percent
in the answer. Node A barely noticed, moving by 0.05%, which is the other half of the
lesson: the amplification is not spread evenly, and the component that suffers is the one
belonging to the small eigenvalue. Measured as whole vectors this perturbation was
amplified by 354, against a bound of 500.75; a $\delta i$ pointed exactly along the small
eigenvector achieves the full 500.75 and nothing achieves more.

## Worked example: a healthy problem an algorithm can still ruin

$$\begin{pmatrix} 0.0001 & 1 \\ 1 & 1 \end{pmatrix}
\begin{pmatrix} x_1 \\ x_2 \end{pmatrix} =
\begin{pmatrix} 1 \\ 2 \end{pmatrix}$$

The exact answer is $x_1 = 1.00010001$, $x_2 = 0.99989999$, and this matrix has
$\kappa_2 = 2.62$ — about as well conditioned as a matrix gets. Eliminate it without
exchanging rows, carrying three significant figures the way a short float or a slide rule
would:

```
multiplier = 1 / 0.0001 = 10000

row2 := row2 - 10000 * row1
   coefficient : 1 - 10000(1) = -9999  ->  -1.00e4   (3 s.f.)
   rhs         : 2 - 10000(1) = -9998  ->  -1.00e4

x2 = -1.00e4 / -1.00e4 = 1.00
x1 = (1 - 1.00) / 0.0001 = 0.00          <- the true value is 1.00
```

Both of the original right-hand side entries were annihilated: beside 10000 they were
insignificant, and rounding threw them away. Then $x_1$ was reconstructed by dividing what
was left — pure rounding error — by 0.0001, multiplying it by $10^4$ on the way out.

Exchange the rows first, which is what **partial pivoting** does: take the largest
available entry in the column as the pivot, here the 1 rather than the 0.0001.

```
[ 1       1 ] [x1]   [2]
[ 0.0001  1 ] [x2] = [1]

multiplier = 0.0001 / 1 = 0.0001

row2 := row2 - 0.0001 * row1
   coefficient : 1 - 0.0001 = 0.9999   ->  1.00
   rhs         : 1 - 0.0002 = 0.9998   ->  1.00

x2 = 1.00
x1 = 2 - 1.00 = 1.00                     <- right to three figures
```

Same matrix, same three digits, two answers, one of them worthless. The *problem* was
never ill-conditioned — $\kappa = 2.62$ promised a good answer was available — and the
algorithm threw it away. Choosing the larger pivot keeps every multiplier at or below 1
in magnitude, which is what stops the pivot row from swamping the rows it is subtracted
from. That single comparison per column is why library solvers pivot without being asked,
and why the lab in this module makes you write it.

## The mistake people make

Reading a small determinant as ill-conditioning. It is the natural extrapolation from
"$\det = 0$ means singular", and it is wrong, because the determinant carries units and a
scale while the condition number does not.

Take the ladder from the first reading, whose determinant was 32 with conductances written
in millisiemens. Write the identical circuit in siemens — same resistors, same board, a
different unit on the page — and every entry shrinks by $10^{3}$, so the determinant of a
$3\times3$ shrinks by $10^{9}$:

```
in mS :  det = 32          kappa = 5.75
in S  :  det = 3.2e-8      kappa = 5.75
```

Nothing happened to the circuit and nothing happened to $\kappa$, because $\kappa$ is a
ratio of two eigenvalues of the same matrix and a common factor cancels out of it. A
determinant of $10^{-30}$ can belong to a beautifully conditioned matrix and a determinant
of $10^{30}$ to a hopeless one.

The companion mistake is treating a badly conditioned answer as a *wrong* answer. It is
not. It is the exact answer to a problem very slightly different from the one you posed —
which, since your resistors have tolerances, may well be the better problem of the two.
What you have lost is not correctness but significant figures, and the honest response is
to quote fewer of them.

## Where this stops, and what replaces it

**$\kappa$ is a worst case over every possible right-hand side.** A $\delta i$ that happens
to point in the same direction as $i$ itself is amplified by exactly 1, whatever $\kappa$
says, because $G^{-1}$ is applied to both and the ratio survives untouched. Whether your
data error lands in the bad direction is a question about your problem, not about your
matrix. Read $\kappa$ as the size of the disaster available, not the size of the disaster.

**Much of a bad $\kappa$ can simply be scaled away.** A large part of it in circuit
matrices is an artefact of using one unit for every node. Scaling rows and columns so the
diagonal entries are comparable — equilibration — is a change of variables rather than an
approximation, and it can turn $10^{6}$ into $10^{2}$ for nothing. Changing the
formulation does the same kind of work: the same network written in mesh currents produces
a *resistance* matrix instead of a conductance matrix, with a different spread of entries
and a condition number that has to be computed rather than guessed at — but knowing that
the choice exists is half of the remedy.

**Iterative refinement buys back digits.** With the factors already computed, form the
residual $r = i - G\hat{v}$ in higher precision, solve $G\delta = r$ using those same
factors, and add $\delta$ to $\hat{v}$. The expensive part of the work is already done, so
this is nearly free, and it recovers most of what a moderate $\kappa$ took — until
$\kappa$ is large enough that the residual itself is noise, at which point there is
nothing left to recover.

**And when the matrix really is on the edge, elimination is the wrong tool.** It gives a
yes-or-no about pivots. The singular value decomposition gives the distance to the nearest
singular matrix, and lets you set aside the directions that cannot be distinguished from
zero rather than dividing by them. That is the same machinery that makes least squares
work on data which does not determine every parameter — which is exactly where this course
goes next.
''',
                },
            ],
            "build": {
                "title": "The node with no equation",
                "minutes": 22,
                "brief": r'''
On the canvas: a 1 V source, and a 100 nF capacitor with the probe on its far side. That
far node touches nothing else at all.

Ask the schematic editor for a DC answer and it refuses, and the refusal is the whole
point of this exercise. At DC a capacitor has zero admittance, so the row of $G$
belonging to that node is entirely zeros: the matrix is singular, its rank is one short,
and its nullspace contains "lift that node by a volt". Nothing in the circuit decides
where the node sits, so nothing in the mathematics does either.

## What to add

One resistor, from the probed node to a new ground, and choose it so that the network's
corner frequency is **159.15 Hz**. The capacitor may be changed if you prefer a different
pair; only the product matters.

Notice what this circuit is. Signal in through a capacitor, resistor to ground — it is
the coupling network at the input of every AC-coupled amplifier ever built, and the
resistor is there for exactly the reason above. Leave it out on a real board and the
input node drifts to wherever leakage takes it.

## What is measured

- that a DC operating point exists at all, and that it puts the probe at 0.00 V. The
  starting circuit fails this one by refusing to solve.
- the gain at 1 Hz, which must be under 0.01: the capacitor blocks the rail.
- the gain at 10 kHz, which must be 1: well above the corner, the capacitor is a short
  and the signal passes untouched.
- the gain and the phase at 159.15 Hz, which must be $1/\sqrt{2}$ and $+45°$. The
  positive sign is what makes it a high-pass rather than a low-pass, and a lead rather
  than a lag.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "C", "x": 6, "y": 5, "rot": 0, "value": 1e-7},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "C", "x": 6, "y": 5, "rot": 0, "value": 1e-7},
                        {"id": "p3", "kind": "OUT", "x": 9, "y": 5},
                        {"id": "p4", "kind": "R", "x": 9, "y": 7, "rot": 1, "value": 10000},
                        {"id": "p5", "kind": "GND", "x": 9, "y": 10},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [9, 5], "b": [9, 6]},
                        {"a": [9, 8], "b": [9, 10]},
                    ],
                },
                "checks": [
                    {"name": "one 1 V source drives the network", "code": r'''
c.assert(c.count('V') === 1,
  'Use exactly one voltage source, so that "the gain" means one thing. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 1, 0.001,
  'the source amplitude — the checks read the probe voltage as the gain, so the input must be 1 V');
'''},
                    {"name": "the DC operating point exists, and the probe sits at 0 V", "code": r'''
const v = c.vout();
c.assert(Math.abs(v) < 1e-6,
  'The probed node must settle at 0 V DC: no steady current can flow through a capacitor, so ' +
  'whatever resistance you put to ground has no volt drop across it. Measured ' + v.toFixed(4) + ' V. ' +
  'A resistor to the source instead of to ground would fix the matrix and give the wrong answer here.');
'''},
                    {"name": "the rail is blocked: almost nothing gets through at 1 Hz", "code": r'''
const g = c.gain(1);
c.assert(g < 0.01,
  'At 1 Hz, far below the corner, a high-pass should pass almost nothing. Measured a gain of ' +
  g.toFixed(4) + '.');
'''},
                    {"name": "the signal is passed: the gain is 1 at 10 kHz", "code": r'''
c.close(c.gain(10000), 1.0, 0.02,
  'the gain at 10 kHz, far above the corner, where the capacitor is effectively a short');
'''},
                    {"name": "the corner sits at 159.15 Hz, and the phase leads by 45 degrees", "code": r'''
c.close(c.gain(159.15494309189535), 0.7071067811865476, 0.03,
  'the gain at 159.15 Hz, which is 1/sqrt(2) when the corner is there');
const ph = c.phase(159.15494309189535);
c.assert(Math.abs(ph - 45) <= 3,
  'A first-order high-pass leads by exactly 45 degrees at its corner. This circuit is at ' +
  ph.toFixed(1) + ' degrees — a lag of 45 would mean the probe is on the wrong side of the pair.');
'''},
                ],
                "hints": [
                    "The resistor goes from the probed node to ground, and it needs a ground symbol of its own — a resistor with one end in mid-air leaves the matrix exactly as singular as it was.",
                    "The corner of an RC pair is $f_c = 1/(2\\pi RC)$, whichever component the output is taken across. With $C = 100$ nF and $f_c = 159.15$ Hz, $R = 1/(2\\pi f_c C) = 10$ kΩ.",
                    "If the DC check passes but the 1 Hz gain is 1, the resistor is connected to the source rather than to ground: the node now has an equation, but the equation says 'follow the rail'.",
                    "If every check throws the same message about the circuit being under-determined, the ground is missing or is not actually touching the resistor's lower pin.",
                    "Type `10k` in the resistor's value box. The editor understands the engineering suffixes, and the label it draws afterwards is what the checks measure.",
                ],
            },
            "blanks": {
                "title": "Eliminating a conductance matrix by hand",
                "minutes": 9,
                "caption": "three nodes, four resistors, all of them 1 kΩ",
                "lang": "text",
                "brief": r'''
Three unknown nodes: node 1 joined to node 2, node 2 joined to node 3 and to ground,
node 3 joined to ground. Every resistor is 1 kΩ, so every conductance is 1 mS and the
matrix comes out in whole numbers.

Work down the columns. At each step the multiplier is the entry you want to remove
divided by the pivot above it, and you subtract that multiple of the pivot row.

Nothing is executed here — this is arithmetic you are choosing, not code.
''',
                "listing": """G (mS)             rhs
[  1  -1   0 ]     [ i1 ]
[ -1   3  -1 ]     [  0 ]
[  0  -1   2 ]     [  0 ]

column 1.  pivot = 1, sitting at G[1][1].
   row2 := row2 - (___) * row1          row3 already has a 0 in column 1

[  1  -1    0 ]
[  0  ___  -1 ]
[  0  -1    2 ]

column 2.  pivot = the entry that step just produced.
   row3 := row3 - (___) * row2

[  1  -1    0  ]
[  0   2   -1  ]
[  0   0   ___ ]

det G = the product of the pivots = ___ mS^3        rank = ___
""",
                "blanks": [
                    {
                        "prompt": "The multiplier that clears the $-1$ under the first pivot.",
                        "hole": "?",
                        "opts": ["-1", "1", "3", "-3"],
                        "a": 0,
                        "why": "The multiplier is the entry being removed divided by the pivot: $-1/1 = -1$. Subtracting $-1$ times row 1 means *adding* row 1, which is what turns $[-1, 3, -1]$ into $[0, 2, -1]$.",
                        "whys": [
                            "The multiplier is the entry being removed divided by the pivot: $-1/1 = -1$. Subtracting $-1$ times row 1 means *adding* row 1, which is what turns $[-1, 3, -1]$ into $[0, 2, -1]$.",
                            "Subtracting one times row 1 would give $[-1-1, 3+1, -1] = [-2, 4, -1]$, which has made the entry you were trying to remove twice as large. The sign of the multiplier follows the sign of the entry.",
                            "3 is the diagonal entry of the row being changed, not the ratio of anything. Multipliers come from the column you are clearing.",
                            "$-3$ is three times the correct multiplier, not twice it: subtracting $-3$ times row 1 adds three copies of it, and row 2 would become $[2, 0, -1]$ — a new non-zero entry in the column that was supposed to end up empty. Merely doubling it, at $-2$, would give $[1, 1, -1]$, which is wrong too and is not on offer.",
                        ],
                    },
                    {
                        "prompt": "What the middle entry of row 2 becomes.",
                        "hole": "?",
                        "opts": ["2", "4", "3", "-2"],
                        "a": 0,
                        "why": "Adding row 1 to row 2 gives $3 + (-1) = 2$. That 2 is the second pivot, and it is smaller than the 3 it replaced — elimination on a conductance matrix always shrinks the diagonal, which is the algebraic shadow of the fact that adding a path to ground can only ever help.",
                        "whys": [
                            "Adding row 1 to row 2 gives $3 + (-1) = 2$. That 2 is the second pivot, and it is smaller than the 3 it replaced — elimination on a conductance matrix always shrinks the diagonal, which is the algebraic shadow of the fact that adding a path to ground can only ever help.",
                            "4 is what you get from subtracting row 1 instead of adding it, which is the wrong sign of multiplier carried forward.",
                            "3 is the entry before the step. If nothing changed, the elimination did nothing — but the whole row was altered, including this entry.",
                            "A negative diagonal entry is impossible in a conductance matrix: the diagonal is a sum of conductances, all positive, and elimination cannot drive it below zero while the network stays connected to ground.",
                        ],
                    },
                    {
                        "prompt": "The multiplier for the second column.",
                        "hole": "?",
                        "opts": ["-0.5", "0.5", "-1", "-2"],
                        "a": 0,
                        "why": "The entry to remove is $-1$ and the pivot is 2, so the multiplier is $-1/2 = -0.5$. Subtracting $-0.5$ times row 2 adds half of it, and $-1 + 1 = 0$ as required.",
                        "whys": [
                            "The entry to remove is $-1$ and the pivot is 2, so the multiplier is $-1/2 = -0.5$. Subtracting $-0.5$ times row 2 adds half of it, and $-1 + 1 = 0$ as required.",
                            "With $+0.5$ the entry becomes $-1 - 1 = -2$ instead of 0 — the correction has been applied in the wrong direction, which is the same sign slip as before.",
                            "$-1$ would be right if the pivot were 1. It is 2, and dividing by the pivot is the step that is easiest to skip.",
                            "$-2$ inverts the ratio: pivot over entry rather than entry over pivot. It leaves $-1 + 4 = 3$ in a place that has to be zero.",
                        ],
                    },
                    {
                        "prompt": "The third pivot.",
                        "hole": "?",
                        "opts": ["1.5", "2.5", "2", "1"],
                        "a": 0,
                        "why": "Row 3 was $[0, -1, 2]$; adding half of $[0, 2, -1]$ gives $[0, 0, 2 - 0.5] = [0, 0, 1.5]$. Every pivot here came out positive, which is what guarantees the elimination never needed a row exchange.",
                        "whys": [
                            "Row 3 was $[0, -1, 2]$; adding half of $[0, 2, -1]$ gives $[0, 0, 2 - 0.5] = [0, 0, 1.5]$. Every pivot here came out positive, which is what guarantees the elimination never needed a row exchange.",
                            "2.5 comes from subtracting the half instead of adding it. The multiplier is $-0.5$, so the step *adds* half of row 2, and the third entry of row 2 is $-1$: adding half of it reduces the 2 to 1.5. Subtracting it instead raises the 2 to 2.5.",
                            "2 is the entry before the step. Column 2 was cleared, but the third column changed at the same time; every entry to the right of the pivot moves.",
                            "1 is what a multiplier of $-1$ gives: that step *adds* the whole of row 2 rather than half of it, and $2 + (-1) = 1$. It also leaves $-1 + 2 = 1$ in the column that was supposed to be cleared, which is the giveaway. Subtracting the whole of row 2 instead would raise the 2 to 3.",
                        ],
                    },
                    {
                        "prompt": "The determinant, as the product of the three pivots.",
                        "hole": "?",
                        "opts": ["3", "6", "2", "0"],
                        "a": 0,
                        "why": "$1 \\times 2 \\times 1.5 = 3$, and there were no row exchanges, so there is no sign to flip. It is not zero, which is the useful part: this network has exactly one set of node voltages for any set of injected currents.",
                        "whys": [
                            "$1 \\times 2 \\times 1.5 = 3$, and there were no row exchanges, so there is no sign to flip. It is not zero, which is the useful part: this network has exactly one set of node voltages for any set of injected currents.",
                            "6 is the product of the *original* diagonal, $1 \\times 3 \\times 2$. That shortcut is only correct for a triangular matrix, and this one was not triangular until the elimination made it so.",
                            "2 is one of the pivots rather than the product of all three.",
                            "Zero would mean the network was singular. It is not: every node here has a resistive path to ground, node 1 reaching it through node 2.",
                        ],
                    },
                    {
                        "prompt": "The rank.",
                        "hole": "?",
                        "opts": ["3", "2", "1", "0"],
                        "a": 0,
                        "why": "Three non-zero pivots, so rank 3 — full rank for a $3\\times3$. The nullspace therefore contains nothing but the zero vector: there is no non-trivial pattern of node voltages that draws no current, which is another way of saying the circuit determines its own answer.",
                        "whys": [
                            "Three non-zero pivots, so rank 3 — full rank for a $3\\times3$. The nullspace therefore contains nothing but the zero vector: there is no non-trivial pattern of node voltages that draws no current, which is another way of saying the circuit determines its own answer.",
                            "Rank 2 would mean one pivot came out zero, and the determinant would then have to be zero as well — the two answers have to agree with each other, which is a free check.",
                            "Rank 1 would leave a two-dimensional nullspace: two independent ways to float the circuit. A single resistor bridging two otherwise isolated nodes does that; this network does not.",
                            "Rank 0 is the zero matrix, which would be a circuit with no components in it at all.",
                        ],
                    },
                ],
            },
            "numeric": [
                {
                    "title": "The determinant of a network, from its two pivots",
                    "minutes": 5,
                    "brief": r'''
The mechanical rung. Two unknown nodes, so a $2\times2$ matrix, and one rule to apply to
it.

There is no source in the drawing, and that is deliberate rather than an omission. $G$ is
a property of the network alone — it is built out of the resistors and the way they are
joined, and nothing else. A source would appear on the *right-hand side* of $Gv = i$, and
it would change the answer to "what are the node voltages" without changing a single
entry of the matrix.

Write the two rows. The diagonal entry of a node is the sum of every conductance touching
it; the off-diagonal is minus the conductance joining the two nodes. Then take the
determinant, either as $ad - bc$ or as the product of the two pivots — they are the same
number, and getting both is a free check on your arithmetic.
''',
                    "prompt": "What is the determinant of this network's conductance matrix?",
                    "note": "Work in millisiemens, so the answer is in mS². Give it to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "ra", "kind": "R", "x": 4, "y": 6, "rot": 1, "value": 1000},
                            {"id": "g0", "kind": "GND", "x": 4, "y": 9},
                            {"id": "rb", "kind": "R", "x": 8, "y": 3, "rot": 0, "value": 500},
                            {"id": "rc", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 250},
                            {"id": "g1", "kind": "GND", "x": 12, "y": 9},
                        ],
                        "wires": [
                            {"a": [4, 3], "b": [4, 5]},
                            {"a": [4, 7], "b": [4, 9]},
                            {"a": [4, 3], "b": [7, 3]},
                            {"a": [9, 3], "b": [12, 3]},
                            {"a": [12, 3], "b": [12, 5]},
                            {"a": [12, 7], "b": [12, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Left node to ground", "value": "1.00 kΩ"},
                        {"label": "Left node to right node", "value": "500 Ω"},
                        {"label": "Right node to ground", "value": "250 Ω"},
                        {"label": "Sources", "value": "none — $G$ does not depend on them"},
                    ],
                    "aside": "1 kΩ is 1 mS, 500 Ω is 2 mS, 250 Ω is 4 mS. Keeping conductances in "
                             "millisiemens throughout means node voltages come out in volts when "
                             "currents are in milliamps.",
                    # G is rebuilt here from the resistors in the netlist rather than from the
                    # numbers in the prompt, so editing a value in the diagram without re-working
                    # the answer makes this gate fail rather than pass quietly.
                    "check": r'''
const n = c.nodeCount() - 1;
c.assert(n === 2, 'this question is about a 2x2 matrix; the drawing has ' + n + ' unknown nodes');
const G = [[0, 0], [0, 0]];
c.net.parts.forEach(function (p) {
  if (p.kind !== 'R') return;
  const g = 1000 / p.value;                    /* millisiemens */
  if (p.n1 > 0) G[p.n1 - 1][p.n1 - 1] += g;
  if (p.n2 > 0) G[p.n2 - 1][p.n2 - 1] += g;
  if (p.n1 > 0 && p.n2 > 0) { G[p.n1 - 1][p.n2 - 1] -= g; G[p.n2 - 1][p.n1 - 1] -= g; }
});
return G[0][0] * G[1][1] - G[0][1] * G[1][0];
''',
                    "answer": 14.0,
                    "tol": 0.1,
                    "unit": "mS²",
                    "hint": "The left node touches 1 mS and 2 mS, so its diagonal is 3. The right node "
                            "touches 2 mS and 4 mS, so its diagonal is 6. The only resistor joining them "
                            "is the 500 Ω, so both off-diagonal entries are $-2$.",
                    "wrong": "If you got 18, you have multiplied the diagonal and forgotten to subtract the "
                             "product of the off-diagonals — the one place the shared 500 Ω enters twice. "
                             "If you got 4, the 500 Ω has been left out of the matrix altogether, leaving "
                             "$\\mathrm{diag}(1, 4)$: it belongs in *both* diagonals as well as in both "
                             "off-diagonal slots. And if you got $1.4\\times10^{-5}$, that is the same "
                             "matrix written in siemens — right, but not the unit the question asked for.",
                    "why": r'''
```
conductances:  1 kΩ = 1 mS,  500 Ω = 2 mS,  250 Ω = 4 mS

G (mS)              left node  : 1 + 2 = 3
[  3  -2 ]          right node : 2 + 4 = 6
[ -2   6 ]          link       : -2 in both off-diagonal slots

det = (3)(6) - (-2)(-2) = 18 - 4 = 14 mS^2
```
Now the same number as the product of the pivots, which is what elimination actually
computes. The first pivot is 3. The multiplier for the second row is $-2/3$, so that row
gains two thirds of the first:

```
second pivot = 6 - (-2)(-2)/3 = 6 - 4/3 = 14/3 mS

det = 3 * 14/3 = 14 mS^2
```

That second pivot is worth a sentence, because it is a resistance you could measure.
$14/3 = 4.667$ mS is what the right-hand node sees *after the left node has been absorbed*:
its own 250 Ω to ground is 4 mS, and the 500 Ω link in series with the left node's 1 kΩ is
1.5 kΩ, which is 0.667 mS. $4 + 0.667 = 4.667$. Elimination did not produce an abstract
number; it produced the conductance of the reduced circuit.

Track the units while you are here, because they matter later. Two pivots were multiplied,
so the determinant is in mS²; an $n \times n$ conductance matrix has a determinant in mSⁿ.
That is exactly why the size of a determinant means nothing on its own — rewrite this same
network in siemens and 14 becomes $1.4\times10^{-5}$ without a single resistor moving.
''',
                },
                {
                    "title": "Two nodes, and a bridge that stops you cheating",
                    "minutes": 8,
                    "brief": r'''
Two unknown nodes, so one elimination step and one back-substitution.

Look at the shape before you start. The supply reaches node A through one resistor *and*
node B through another, with a third resistor bridging the two. That second feed is what
stops this being a ladder: you cannot collapse it with series and parallel from the far
end, because node B is fed from two directions at once. Write both KCL rows, eliminate,
substitute back.

The supply node itself is not an unknown — it is held at 12.0 V — so it does not get a row.
Its effect appears as a known current $V/R$ injected at each node it reaches.
''',
                    "prompt": "What voltage does the probed node sit at?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 10, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 13},
                            {"id": "r1", "kind": "R", "x": 7, "y": 6, "rot": 0, "value": 2000},
                            {"id": "r2", "kind": "R", "x": 10, "y": 8, "rot": 1, "value": 4000},
                            {"id": "g1", "kind": "GND", "x": 10, "y": 11},
                            {"id": "r3", "kind": "R", "x": 13, "y": 6, "rot": 0, "value": 2000},
                            {"id": "r4", "kind": "R", "x": 10, "y": 2, "rot": 0, "value": 6000},
                            {"id": "r5", "kind": "R", "x": 16, "y": 8, "rot": 1, "value": 3000},
                            {"id": "g2", "kind": "GND", "x": 16, "y": 11},
                            {"id": "out", "kind": "OUT", "x": 19, "y": 6},
                        ],
                        "wires": [
                            {"a": [3, 11], "b": [3, 13]},
                            {"a": [3, 9], "b": [3, 2]},
                            {"a": [3, 6], "b": [6, 6]},
                            {"a": [8, 6], "b": [10, 6]},
                            {"a": [10, 6], "b": [10, 7]},
                            {"a": [10, 9], "b": [10, 11]},
                            {"a": [10, 6], "b": [12, 6]},
                            {"a": [14, 6], "b": [16, 6]},
                            {"a": [16, 6], "b": [16, 7]},
                            {"a": [16, 9], "b": [16, 11]},
                            {"a": [3, 2], "b": [9, 2]},
                            {"a": [11, 2], "b": [16, 2]},
                            {"a": [16, 2], "b": [16, 6]},
                            {"a": [16, 6], "b": [19, 6]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "12.0 V"},
                        {"label": "Supply to node A", "value": "2.00 kΩ"},
                        {"label": "Node A to ground", "value": "4.00 kΩ"},
                        {"label": "Node A to node B", "value": "2.00 kΩ"},
                        {"label": "Supply to node B", "value": "6.00 kΩ (the upper path)"},
                        {"label": "Node B to ground", "value": "3.00 kΩ (probed)"},
                    ],
                    "aside": "In millisiemens: 2 kΩ is 0.5, 3 kΩ is 1/3, 4 kΩ is 0.25, 6 kΩ is 1/6. Both "
                             "injected currents are $12/R$ for the resistor that reaches the node from the "
                             "supply.",
                    "check": "return c.vout();",
                    "answer": 5.5,
                    "tol": 0.05,
                    "unit": "V",
                    "hint": "Node A's diagonal is $0.5 + 0.25 + 0.5 = 1.25$ mS and node B's is "
                            "$0.5 + 1/6 + 1/3 = 1.00$ mS. The injected currents are $12/2 = 6$ mA at A and "
                            "$12/6 = 2$ mA at B.",
                    "wrong": "If you got 3.79 V, you have dropped the upper 6 kΩ feed and solved the plain "
                             "ladder that is left — that path delivers 1.08 mA into node B and lifts it by "
                             "more than a volt and a half. If you got 7.00 V, that is node A rather than "
                             "node B; the probe sits on the far side of the 2 kΩ link.",
                    "why": r'''
```
G (mS)                  i (mA)

[ 1.25  -0.50 ]         [ 6.00 ]      A: 0.5 + 0.25 + 0.5 = 1.25,  i = 12/2 = 6
[ -0.50  1.00 ]         [ 2.00 ]      B: 0.5 + 1/6 + 1/3  = 1.00,  i = 12/6 = 2

eliminate node A.  multiplier = -0.50 / 1.25 = -0.40
   row2 := row2 + 0.40 * row1

   coefficient : 1.00 - (-0.50)(-0.50)/1.25 = 1.00 - 0.20 = 0.80
   rhs         : 2.00 + 0.40 (6.00)                       = 4.40

   vB = 4.40 / 0.80 = 5.50 V

back-substitute into row 1
   1.25 vA - 0.50 (5.50) = 6.00   ->   vA = 8.75 / 1.25 = 7.00 V
```
Check it with KCL rather than trusting the elimination. At node A, in from the supply is
$(12.0-7.00)/2\,\mathrm{k} = 2.50$ mA; out is $7.00/4\,\mathrm{k} = 1.75$ mA to ground and
$(7.00-5.50)/2\,\mathrm{k} = 0.750$ mA to node B, which is 2.50 mA. At node B, in is
$(12.0-5.50)/6\,\mathrm{k} = 1.083$ mA from the supply plus that 0.750 mA from node A, and
out is $5.50/3\,\mathrm{k} = 1.833$ mA. Both balance.

The second pivot, 0.80 mS, is again a real conductance: it is what node B sees once node A
has been absorbed into the network around it. And the determinant, $1.25 \times 0.80 = 1.00$
mS², is the same 1.00 you get from $1.25 \times 1.00 - 0.25$ — the pivots and the $ad-bc$
rule agreeing, as they must.

One thing to notice about the bridge. Without the upper 6 kΩ this is a ladder and series
and parallel would finish it: $2\,\mathrm{k} + 3\,\mathrm{k} = 5\,\mathrm{k}$ in parallel
with 4 kΩ, and so on. With it, node B is fed from two directions and no sequence of series
and parallel steps reduces the network. Elimination does not care either way, which is the
argument for learning it: the method that works on the easy circuit is the same one that
works on the one that has no shortcut.
''',
                },
                {
                    "title": "What resistance does this bridge present?",
                    "minutes": 10,
                    "brief": r'''
Three unknown nodes, and the quantity asked for is not any of their voltages.

The resistance a network presents at node $A$ is one entry of $G^{-1}$ — the entry
$(G^{-1})_{AA}$ — because $v = G^{-1}i$ says that injecting one amp at $A$ and nowhere else
puts $(G^{-1})_{AA}$ volts on $A$. Cramer's rule turns that entry into a ratio of two
determinants: the determinant of $G$ with node $A$'s row and column struck out, over the
determinant of the whole of $G$. Two eliminations, one division.

The other route is to hold the source node at 12.0 V, solve for the two middle nodes, add
up the current the supply has to deliver, and divide. Either works. Doing both is the
check.

This is a bridge and it is **not** balanced — $1/4 \neq 3/5$ — so the resistor across the
middle carries current and no series-parallel argument will finish the job.
''',
                    "prompt": "What resistance does the network present to the source, between node A and ground?",
                    "note": "Give the answer in kilohms, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "rab", "kind": "R", "x": 7, "y": 5, "rot": 1, "value": 1000},
                            {"id": "rac", "kind": "R", "x": 13, "y": 5, "rot": 1, "value": 3000},
                            {"id": "rbc", "kind": "R", "x": 10, "y": 7, "rot": 0, "value": 1000},
                            {"id": "rbg", "kind": "R", "x": 7, "y": 9, "rot": 1, "value": 4000},
                            {"id": "g1", "kind": "GND", "x": 7, "y": 12},
                            {"id": "rcg", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 5000},
                            {"id": "g2", "kind": "GND", "x": 13, "y": 12},
                        ],
                        "wires": [
                            {"a": [3, 5], "b": [3, 3]},
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 3], "b": [13, 3]},
                            {"a": [7, 3], "b": [7, 4]},
                            {"a": [13, 3], "b": [13, 4]},
                            {"a": [7, 6], "b": [7, 7]},
                            {"a": [13, 6], "b": [13, 7]},
                            {"a": [7, 7], "b": [9, 7]},
                            {"a": [11, 7], "b": [13, 7]},
                            {"a": [7, 7], "b": [7, 8]},
                            {"a": [7, 10], "b": [7, 12]},
                            {"a": [13, 7], "b": [13, 8]},
                            {"a": [13, 10], "b": [13, 12]},
                        ],
                    },
                    "given": [
                        {"label": "Source", "value": "12.0 V, straight onto node A (the top rail)"},
                        {"label": "A to B (left arm)", "value": "1.00 kΩ"},
                        {"label": "A to C (right arm)", "value": "3.00 kΩ"},
                        {"label": "B to C (the bridge)", "value": "1.00 kΩ"},
                        {"label": "B to ground", "value": "4.00 kΩ"},
                        {"label": "C to ground", "value": "5.00 kΩ"},
                    ],
                    "aside": "Node A is held by the source, so it does not get a row of its own; the two "
                             "unknowns are B and C, and the source contributes $12/R$ milliamps to each of "
                             "their right-hand sides.",
                    # The resistance is neither a node voltage nor a branch current, so the check
                    # reads the source's own value and the current the solver reports through it.
                    # Both come out of the netlist, so a diagram edited anywhere changes this number.
                    "check": r'''
const d = c.dc();
const v = c.net.parts.filter(function (p) { return p.kind === 'V'; })[0];
return Math.abs(v.value / d.currents[v.id]) / 1000;
''',
                    "answer": 3.0,
                    "tol": 0.05,
                    "unit": "kΩ",
                    "hint": "With node A at 12.0 V: node B's row is $2.25 v_B - v_C = 12$ and node C's is "
                            "$-v_B + 1.533 v_C = 4$, both in millisiemens and milliamps. Solve those, then "
                            "add the two currents the supply pushes into the arms.",
                    "wrong": "If you got 3.08 kΩ, that is $(1+4)\\parallel(3+5) = 5\\parallel8$ — the "
                             "network with the bridging resistor deleted, which is only correct when the "
                             "bridge is balanced, and this one is not ($1/4 \\ne 3/5$). If you got "
                             "2.97 kΩ, that is the opposite extreme, $(1\\parallel3) + (4\\parallel5)$, "
                             "which treats the bridge as a short. The true answer lies between those two, "
                             "as it must. And if you got 4.00, that is the supply current in milliamps "
                             "rather than the resistance in kilohms.",
                    "why": r'''
```
with node A held at 12 V, the two unknown rows are

[ 2.2500  -1.0000 ]  [vB]   [ 12.000 ]     B: 1 + 1 + 0.25   = 2.2500 mS,  i = 12/1 = 12
[ -1.0000  1.5333 ]  [vC] = [  4.000 ]     C: 1/3 + 1 + 0.2  = 1.5333 mS,  i = 12/3 =  4

eliminate B.  multiplier = -1.0000/2.2500 = -0.44444

   coefficient : 1.5333 - (1)(1)/2.2500 = 1.5333 - 0.4444 = 1.0889
   rhs         : 4.000 + 0.44444 (12.000)                 = 9.3333

   vC = 9.3333 / 1.0889 = 8.5714 V
   vB = (12.000 + 8.5714) / 2.2500 = 9.1429 V

current the supply delivers, down both arms

   through the 1 k :  (12.000 - 9.1429)/1 k = 2.8571 mA
   through the 3 k :  (12.000 - 8.5714)/3 k = 1.1429 mA
                                              -------
                                              4.0000 mA

   R = 12.000 V / 4.0000 mA = 3.00 kΩ
```
Now the other route, which uses no source at all. Write the full $3\times3$ $G$ for nodes
A, B and C, in millisiemens:

$$G = \begin{pmatrix} 1.3333 & -1 & -0.3333 \\ -1 & 2.25 & -1 \\ -0.3333 & -1 & 1.5333
\end{pmatrix}$$

Its determinant is $49/60 = 0.81667$ mS³. Strike out node A's row and column and you are
left with $\begin{pmatrix}2.25 & -1\\ -1 & 1.5333\end{pmatrix}$, whose determinant is
$49/20 = 2.45$ mS². Cramer's rule gives the diagonal entry of the inverse as the ratio:

$$R_{AA} = (G^{-1})_{AA} = \frac{2.45}{0.81667} = 3.00\ \mathrm{k\Omega}$$

Two entirely different computations, the same three kilohms, and the second one never
mentioned the 12 V — because the resistance a network presents is a property of the
network, exactly as its matrix is.

There is a third route, and it is the derivation in this module run backwards. Turn the
triangle A–B–C into a star: with $R_{AB}=1$, $R_{BC}=1$ and $R_{CA}=3$ summing to 5 kΩ,

```
star leg at A : (1)(3)/5 = 0.60 kΩ        star leg at B : (1)(1)/5 = 0.20 kΩ
star leg at C : (1)(3)/5 = 0.60 kΩ
```

and the bridge has become a plain series-parallel network: $0.20 + 4 = 4.2$ kΩ down one
side, $0.60 + 5 = 5.6$ kΩ down the other, in parallel giving $4.2 \parallel 5.6 = 2.4$ kΩ,
plus the 0.60 kΩ leg at A. That is 3.00 kΩ again. Choosing the right node to eliminate is
what turns a circuit with no shortcut into one that has nothing but shortcuts.

The bridge is what makes the elimination necessary. Delete the middle 1 kΩ and the two
arms become $5\,\mathrm{k} \parallel 8\,\mathrm{k} = 3.08\,\mathrm{k\Omega}$; short it and
they become $(1 \parallel 3) + (4 \parallel 5) = 0.75 + 2.22 = 2.97\,\mathrm{k\Omega}$.
The true 3.00 kΩ has to lie between those two, and it does — about three quarters of the
way from the open value towards the shorted one, which is another way of saying that the
bridge resistor is doing real work. It carries 0.571 mA, from B to C, against a total
supply current of 4.00 mA.
''',
                },
                {
                    "title": "How badly conditioned is a 1 Ω next to a 10 kΩ?",
                    "minutes": 11,
                    "brief": r'''
A different quantity, and the one this module is really about. Not what the circuit does —
what the *arithmetic about it* is worth.

Two unknown nodes again, so a symmetric $2\times2$ conductance matrix. Its condition
number in the 2-norm is $\lambda_{\max}/\lambda_{\min}$, and for a $2\times2$ you never
need an eigenvector to get there: the two eigenvalues sum to the trace and multiply to the
determinant, so they are the roots of

$$\lambda^2 - (\mathrm{tr}\,G)\,\lambda + \det G = 0$$

No source is drawn, for the same reason as before — $\kappa$ is a property of the matrix,
and the matrix is a property of the network.

One warning, and it is the module's own subject turned on the question. The two roots here
are separated by four orders of magnitude, so the small one comes out of
$(\mathrm{tr} - \sqrt{\ \cdot\ })/2$ as the difference of two nearly equal numbers, and
every digit you were careless with disappears into it. Take the *large* root from the
quadratic formula, where the two terms add rather than cancel, and get the small one from
$\lambda_{\min} = \det G / \lambda_{\max}$.
''',
                    "prompt": "What is the 2-norm condition number of this network's conductance matrix?",
                    "note": "A pure number, with no units. Give it to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "ra", "kind": "R", "x": 5, "y": 6, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 5, "y": 9},
                            {"id": "rb", "kind": "R", "x": 9, "y": 3, "rot": 0, "value": 10000},
                            {"id": "rc", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 10000},
                            {"id": "g1", "kind": "GND", "x": 13, "y": 9},
                        ],
                        "wires": [
                            {"a": [5, 3], "b": [5, 5]},
                            {"a": [5, 7], "b": [5, 9]},
                            {"a": [5, 3], "b": [8, 3]},
                            {"a": [10, 3], "b": [13, 3]},
                            {"a": [13, 3], "b": [13, 5]},
                            {"a": [13, 7], "b": [13, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Node A to ground", "value": "1.00 Ω (a current-sense resistor)"},
                        {"label": "Node A to node B", "value": "10.0 kΩ"},
                        {"label": "Node B to ground", "value": "10.0 kΩ"},
                        {"label": "Sources", "value": "none — $\\kappa$ does not depend on them"},
                    ],
                    "aside": "1.00 Ω is 1000 mS and 10.0 kΩ is 0.100 mS. Build $G$ in millisiemens, take "
                             "its trace and its determinant, get $\\lambda_{\\max}$ from the quadratic and "
                             "$\\lambda_{\\min}$ from $\\det G/\\lambda_{\\max}$.",
                    # The eigenvalues of a symmetric 2x2 in closed form, from a matrix rebuilt
                    # out of the netlist. Returning the ratio directly means the gate is checking
                    # the number the prompt asks for and not a stand-in for it.
                    "check": r'''
const n = c.nodeCount() - 1;
c.assert(n === 2, 'this question is about a 2x2 matrix; the drawing has ' + n + ' unknown nodes');
const G = [[0, 0], [0, 0]];
c.net.parts.forEach(function (p) {
  if (p.kind !== 'R') return;
  const g = 1000 / p.value;                    /* millisiemens */
  if (p.n1 > 0) G[p.n1 - 1][p.n1 - 1] += g;
  if (p.n2 > 0) G[p.n2 - 1][p.n2 - 1] += g;
  if (p.n1 > 0 && p.n2 > 0) { G[p.n1 - 1][p.n2 - 1] -= g; G[p.n2 - 1][p.n1 - 1] -= g; }
});
const tr = G[0][0] + G[1][1];
const det = G[0][0] * G[1][1] - G[0][1] * G[1][0];
const disc = Math.sqrt(tr * tr - 4 * det);
return (tr + disc) / (tr - disc);
''',
                    "answer": 5000.75,
                    "tol": 30.0,
                    "unit": "",
                    "hint": "The trace is $1000.1 + 0.2 = 1000.3$ mS and the determinant is "
                            "$(1000.1)(0.2) - 0.01 = 200.01$ mS². The discriminant is "
                            "$1000.3^2 - 4(200.01) = 999800.05$, whose square root is 999.9000. *Add* it "
                            "to the trace to get $\\lambda_{\\max}$; do not subtract it to get "
                            "$\\lambda_{\\min}$.",
                    "wrong": "If you got 10000, that is the ratio of the largest resistance to the "
                             "smallest, which is a rough guide and not the answer — node B's diagonal is "
                             "0.2 mS, not 0.1, because two 10 kΩ resistors touch it. If you got 200, that "
                             "is the determinant. If you got about 6670, you took the square root of "
                             "999800 as 1000, which is wrong by one part in ten thousand and moves the "
                             "answer by a third — that failure is the subject of the question, and the "
                             "discussion below works it through. If you got something near 1, the two "
                             "roots have been divided the wrong way round; $\\kappa$ is never below 1.",
                    "why": r'''
```
G (mS)                    node A : 1000 + 0.1 = 1000.1     (1 Ω is 1000 mS)
[ 1000.1   -0.1 ]         node B :  0.1 + 0.1 =    0.2     (10 kΩ is 0.1 mS)
[   -0.1    0.2 ]         link   :               -0.1

trace = 1000.3            det = (1000.1)(0.2) - (0.1)^2 = 200.02 - 0.01 = 200.01

lambda^2 - 1000.3 lambda + 200.01 = 0

disc = 1000.3^2 - 4(200.01) = 1000600.09 - 800.04 = 999800.05
sqrt(999800.05)                                   =    999.900020

lmax = (1000.3 + 999.900020)/2 = 1000.10001 mS        <- the terms ADD here
lmin = 200.01 / 1000.10001     =    0.19998999 mS     <- and this one cannot cancel

kappa = 1000.10001 / 0.19998999 = 5000.75
```
The middle two lines are the whole reason this question exists. Taking the small root the
obvious way, as $(1000.3 - 999.900020)/2$, subtracts two numbers that differ by one part
in 2500, so between three and four digits of accuracy vanish in the subtraction. Watch
what that costs. Suppose you look at $\sqrt{999800.05}$, think "that is nearly a million,
so the root is nearly a thousand", and use 1000:

```
error in the root : (1000 - 999.90002)/999.90002 = 0.0100 %

lmax  = (1000.3 + 1000)/2 = 1000.15    against a true 1000.10   -> 0.005% high
lmin  = (1000.3 - 1000)/2 =    0.150   against a true 0.19999   ->    25% low
kappa =  1000.15 / 0.150  =    6668    against a true 5000.75   ->    33% high
```

One part in ten thousand going in, one part in three going out: the subtraction amplified
the error by a factor of about 3300. Getting $\lambda_{\min}$ from
$\det G/\lambda_{\max}$ instead uses a division, which cannot cancel anything, and the
same crude root of 999.9 then gives $\lambda_{\max} = 1000.10$ and
$\lambda_{\min} = 200.01/1000.10 = 0.199990$, correct in every digit shown. That
rearrangement is worth remembering for any quadratic whose roots are far apart — and note
what has just happened, which is that the disease the question is measuring turned up
inside the measurement.

Equivalently, and with one fewer step: $\kappa = \lambda_{\max}^2/\det G =
1000.10001^2/200.01 = 1000200.03/200.01 = 5000.75$.

Notice how nearly the eigenvalues are the diagonal entries — 1000.10001 against 1000.1,
and 0.19999 against 0.2. That is not luck. The off-diagonal entry is 0.1 mS against a
diagonal spread of four orders of magnitude, so the matrix is very nearly diagonal, and for
a nearly diagonal matrix $\kappa$ is nearly the ratio of the largest diagonal entry to the
smallest. That is the rule of thumb worth carrying: **the condition number of a conductance
matrix is roughly the spread of the total conductances at its nodes** — not of the resistor
values, which is why a 10 000-to-1 spread of resistances produced a $\kappa$ of 5000 rather
than 10 000.

What does 5000 cost? $\log_{10} 5000.75 = 3.70$, so up to about 3.7 decimal digits can be
lost between the data and the answer. Double precision starts with roughly 16 of them, so
this matrix is still nothing to worry about in software — which is the honest conclusion,
and worth reaching deliberately rather than assuming a big-looking number means trouble. It
is $\kappa$ of $10^{10}$ and above, on a 16-digit machine, that should make you stop and
reformulate. What it *does* cost is the four digits you just watched the naive root
calculation throw away, and a hand calculation carrying six figures is much closer to that
edge than a computer is.
''',
                },
                {
                    "title": "Three nodes, two sources, and the power in one resistor",
                    "minutes": 14,
                    "brief": r'''
The hard rung, and it stacks up everything at once.

Three unknown nodes, so a $3\times3$ to eliminate. Two sources of different kinds: a 12.0 V
rail at one end, and at the other a chip that draws a constant 1.00 mA out of node C no
matter what node C is doing. And the quantity asked for is neither a node voltage nor a
branch current but a power, which means you need two node voltages, their difference, and
then a resistance.

Set up $Gv = i$ carefully before touching any arithmetic. Every node gets a row. The
voltage source is *not* a node of the system — it is eliminated into the right-hand side as
a known injected current $12/R_1$ at node A. The current source *is* on the right-hand
side, with a sign: it takes current away from node C, so node C's entry is negative.

One of the node voltages comes out below ground. That is not a mistake, and working out
which one before you solve is a good use of thirty seconds.
''',
                    "prompt": "How much power does the 4.00 kΩ resistor between node B and node C dissipate?",
                    "note": "Give the answer in milliwatts, to three significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 8, "rot": 1, "value": 12},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 11},
                            {"id": "r1", "kind": "R", "x": 6, "y": 4, "rot": 0, "value": 3000},
                            {"id": "r2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 6000},
                            {"id": "g1", "kind": "GND", "x": 9, "y": 9},
                            {"id": "r3", "kind": "R", "x": 12, "y": 4, "rot": 0, "value": 2000},
                            {"id": "r4", "kind": "R", "x": 15, "y": 6, "rot": 1, "value": 4000},
                            {"id": "g2", "kind": "GND", "x": 15, "y": 9},
                            {"id": "r5", "kind": "R", "x": 18, "y": 4, "rot": 0, "value": 4000},
                            {"id": "r6", "kind": "R", "x": 21, "y": 6, "rot": 1, "value": 4000},
                            {"id": "g3", "kind": "GND", "x": 21, "y": 9},
                            {"id": "i1", "kind": "I", "x": 25, "y": 6, "rot": 1, "value": 0.001},
                            {"id": "g4", "kind": "GND", "x": 25, "y": 9},
                            {"id": "out", "kind": "OUT", "x": 21, "y": 2},
                        ],
                        "wires": [
                            {"a": [3, 9], "b": [3, 11]},
                            {"a": [3, 7], "b": [3, 4]},
                            {"a": [3, 4], "b": [5, 4]},
                            {"a": [7, 4], "b": [9, 4]},
                            {"a": [9, 4], "b": [9, 5]},
                            {"a": [9, 7], "b": [9, 9]},
                            {"a": [9, 4], "b": [11, 4]},
                            {"a": [13, 4], "b": [15, 4]},
                            {"a": [15, 4], "b": [15, 5]},
                            {"a": [15, 7], "b": [15, 9]},
                            {"a": [15, 4], "b": [17, 4]},
                            {"a": [19, 4], "b": [21, 4]},
                            {"a": [21, 4], "b": [21, 5]},
                            {"a": [21, 7], "b": [21, 9]},
                            {"a": [21, 4], "b": [25, 4]},
                            {"a": [25, 4], "b": [25, 5]},
                            {"a": [25, 7], "b": [25, 9]},
                            {"a": [21, 4], "b": [21, 2]},
                        ],
                    },
                    "given": [
                        {"label": "Rail", "value": "12.0 V"},
                        {"label": "Rail to node A", "value": "3.00 kΩ"},
                        {"label": "Node A to ground", "value": "6.00 kΩ"},
                        {"label": "Node A to node B", "value": "2.00 kΩ"},
                        {"label": "Node B to ground", "value": "4.00 kΩ"},
                        {"label": "Node B to node C", "value": "4.00 kΩ"},
                        {"label": "Node C to ground", "value": "4.00 kΩ"},
                        {"label": "Load on node C", "value": "1.00 mA drawn to ground, constant"},
                    ],
                    "aside": "In millisiemens the three diagonals are $1/3 + 1/6 + 1/2 = 1$, "
                             "$1/2 + 1/4 + 1/4 = 1$ and $1/4 + 1/4 = 0.5$. The right-hand side is "
                             "$(4,\\ 0,\\ -1)$ milliamps: 4 mA pushed in at A by the rail, nothing at B, "
                             "1 mA taken out at C.",
                    # Power is not a node of this circuit, so the check takes the drop across r5 out
                    # of the solve and squares it over the resistance the netlist reports. Squaring
                    # also makes it independent of which way round the drop is taken.
                    "check": r'''
const d = c.dc();
const r = c.net.parts.filter(function (p) { return p.id === 'r5'; })[0];
const drop = d.v[r.n1] - d.v[r.n2];
return drop * drop / r.value * 1000;
''',
                    "answer": 2.56,
                    "tol": 0.03,
                    "unit": "mW",
                    "hint": "Eliminate node A first: its row is $v_A - 0.5 v_B = 4$. Then node B, then "
                            "read $v_C$ off the bottom and substitute back up. The power you want is "
                            "$(v_B - v_C)^2 / 4\\,\\mathrm{k\\Omega}$.",
                    "wrong": "If you got 1.44 mW you have used $v_B$ alone, $2.40^2/4\\,\\mathrm{k}$, as "
                             "though node C sat at ground — but the load has pulled it below ground, so "
                             "the drop across the resistor is larger than $v_B$, not smaller. If you got "
                             "0.640 mW you have the right two voltages and have subtracted them as "
                             "$2.40 - 0.80 = 1.60$, losing the minus sign on $v_C$; the drop is 3.20 V, "
                             "not 1.60 V. If you got 2560, that is the same answer in microwatts.",
                    "why": r'''
```
G (mS)                         i (mA)

[  1.00  -0.50   0    ]        [  4.00 ]   A: 1/3 + 1/6 + 1/2 = 1.00,  i = 12/3 = 4
[ -0.50   1.00  -0.25 ]        [  0    ]   B: 1/2 + 1/4 + 1/4 = 1.00
[  0     -0.25   0.50 ]        [ -1.00 ]   C: 1/4 + 1/4       = 0.50,  i = -1 (drawn out)

eliminate A.  multiplier = -0.50/1.00 = -0.50
   row2 : 1.00 - (0.50)(0.50)/1.00 = 0.75      rhs : 0 + 0.50(4.00) = 2.00

[  1.00  -0.50   0    ]        [  4.00 ]
[  0      0.75  -0.25 ]        [  2.00 ]
[  0     -0.25   0.50 ]        [ -1.00 ]

eliminate B.  multiplier = -0.25/0.75 = -1/3
   row3 : 0.50 - (0.25)(0.25)/0.75 = 0.50 - 1/12 = 5/12    rhs : -1.00 + (1/3)(2.00) = -1/3

   vC = (-1/3) / (5/12) = -0.800 V
   vB = (2.00 + 0.25(-0.800)) / 0.75 = 1.80 / 0.75 = 2.40 V
   vA = (4.00 + 0.50(2.40)) / 1.00                 = 5.20 V

power in the 4 kΩ between B and C

   drop = 2.40 - (-0.800) = 3.20 V
   P    = 3.20^2 / 4000   = 10.24 / 4000 = 2.56e-3 W = 2.56 mW
```
Node C came out at $-0.800$ V, and that is the answer to the thirty seconds of thought
suggested at the start. The chip demands a milliamp whatever happens. The rest of the
circuit can only supply so much through the 4 kΩ chain, and the shortfall is made up by
pulling node C below ground so that current runs *backwards* up through its own 4 kΩ to
ground: $0.800/4\,\mathrm{k} = 0.200$ mA arrives that way, and $(2.40+0.800)/4\,\mathrm{k}
= 0.800$ mA comes from node B, which is the milliamp the chip wanted. An ideal current
source produces whatever voltage its demand costs, and here the cost is a negative rail
the circuit never had.

Check the whole solution with KCL before believing the power. At node A: in
$(12.0-5.20)/3\,\mathrm{k} = 2.267$ mA; out $5.20/6\,\mathrm{k} = 0.867$ mA and
$(5.20-2.40)/2\,\mathrm{k} = 1.400$ mA, total 2.267 mA. At node B: in 1.400 mA; out
$2.40/4\,\mathrm{k} = 0.600$ mA and 0.800 mA to node C, total 1.400 mA. At node C: in
0.800 mA from B and 0.200 mA up from ground, out 1.00 mA to the chip. Every node balances.

The determinant, as a by-product, is the product of the three pivots:
$1.00 \times 0.75 \times 5/12 = 0.3125$ mS³. Every pivot positive and none of them small
compared with the entries around them, which is the shape of a matrix that will give you
all the digits you ask for.

Last thing worth taking from this one. Superposition would also have worked: solve with
the rail alone and the chip removed, solve with the chip alone and the rail shorted, add
the two sets of node voltages. It is two $3\times3$ solves instead of one, and the power
would then still have to be computed at the end from the *summed* voltages — you cannot
add the two powers, because power is not linear in the sources. That is the trap
superposition sets, and it is why doing the elimination once with both sources in the
right-hand side is both less work and less dangerous.
''',
                },
            ],
            "derive": {
                "title": "Eliminating a node, and the resistors it leaves behind",
                "minutes": 15,
                "vars": ["G_1", "G_2", "G_3", "R_1", "R_2", "R_3", "v_0", "v_1", "v_2", "v_3", "i_1"],
                "brief": r'''
A star. One internal node, numbered 0, joined to terminal 1 by a conductance $G_1$, to
terminal 2 by $G_2$ and to terminal 3 by $G_3$. Nothing else touches node 0, and nothing
is injected there — it is the junction in the middle of a Y, and no wire from the outside
world reaches it.

Nobody wants that node in their equations. It is not a terminal, nothing is measured
there, and it costs a row and a column. So eliminate it, and watch what the elimination
leaves behind in its place.

Write $i_1$ for the current pushed into terminal 1 from outside, so that
$i_1 = G_1(v_1 - v_0)$: what goes in at the terminal must go down the branch.

The claim this derivation ends at is that the three terminals are joined afterwards by a
triangle of resistors, and that the triangle is the star-to-delta transformation you may
have met as a formula with no argument attached.
''',
                "steps": [
                    {
                        "prompt": "Write KCL at node 0: the three currents leaving it through $G_1$, $G_2$ and $G_3$ sum to zero, because nothing is injected there. Solve for $v_0$.",
                        "answer": "\\frac{G_1 v_1 + G_2 v_2 + G_3 v_3}{G_1 + G_2 + G_3}",
                        "placeholder": "a weighted average of the three terminal voltages",
                        "hint": "The current leaving node 0 through $G_1$ is $G_1(v_0 - v_1)$, and similarly for the other two. Add the three, set the sum to zero, and gather the $v_0$ terms on one side.",
                        "deconstruct": [
                            "$G_1(v_0-v_1) + G_2(v_0-v_2) + G_3(v_0-v_3) = 0$.",
                            "Expanding and collecting: $(G_1+G_2+G_3)v_0 = G_1v_1 + G_2v_2 + G_3v_3$.",
                            "So $v_0$ is the conductance-weighted average of its neighbours. The divisor $G_1+G_2+G_3$ is the total conductance at node 0 — the pivot, and the only thing this whole procedure needs to be non-zero.",
                        ],
                    },
                    {
                        "prompt": "Now substitute that into $i_1 = G_1(v_1 - v_0)$ and collect terms. Give the coefficient of $v_1$.",
                        "answer": "\\frac{G_1(G_2 + G_3)}{G_1 + G_2 + G_3}",
                        "placeholder": "G_1 times something, over the pivot",
                        "hint": "Substituting gives $i_1 = G_1 v_1 - \\dfrac{G_1(G_1v_1+G_2v_2+G_3v_3)}{G_1+G_2+G_3}$. The $v_1$ terms are $G_1$ and $-G_1^2/(G_1+G_2+G_3)$; put them over the common denominator.",
                        "deconstruct": [
                            "$G_1 - \\dfrac{G_1^2}{G_1+G_2+G_3} = \\dfrac{G_1(G_1+G_2+G_3) - G_1^2}{G_1+G_2+G_3}$.",
                            "The $G_1^2$ terms cancel in the numerator.",
                            "What is left is $G_1(G_2+G_3)$ over the pivot — smaller than the $G_1$ it replaced, which it has to be: eliminating a node can only ever reduce the conductance a terminal appears to have.",
                        ],
                    },
                    {
                        "prompt": "From the same expression, give the coefficient of $v_2$.",
                        "answer": "-\\frac{G_1 G_2}{G_1 + G_2 + G_3}",
                        "placeholder": "a product of two conductances over the pivot, with a sign",
                        "hint": "Only one term in $i_1$ contains $v_2$: the $-G_1G_2v_2/(G_1+G_2+G_3)$ that came out of the substitution. Terminal 2 was not connected to terminal 1 before the elimination at all.",
                        "deconstruct": [
                            "Before eliminating, $i_1$ did not involve $v_2$ — there was no resistor between the two terminals.",
                            "After substituting, the single term $-G_1 G_2 v_2/(G_1+G_2+G_3)$ appears.",
                            "It is negative, and an off-diagonal entry of a conductance matrix is minus the conductance joining the pair. So a conductance $G_1G_2/(G_1+G_2+G_3)$ now runs directly from terminal 1 to terminal 2, and this is fill-in: a resistor that was not in the circuit before.",
                        ],
                    },
                    {
                        "prompt": "That new conductance is $G_{12} = G_1G_2/(G_1+G_2+G_3)$. Rewrite it as a resistance in terms of the three star resistances $R_1 = 1/G_1$, $R_2 = 1/G_2$ and $R_3 = 1/G_3$. Give $R_{12} = 1/G_{12}$.",
                        "answer": "\\frac{R_1 R_2 + R_2 R_3 + R_3 R_1}{R_3}",
                        "placeholder": "three products over one resistance",
                        "hint": "Put the denominator over a common denominator first: $1/R_1 + 1/R_2 + 1/R_3 = (R_2R_3 + R_1R_3 + R_1R_2)/(R_1R_2R_3)$. Then $G_{12} = \\dfrac{1}{R_1R_2}\\cdot\\dfrac{R_1R_2R_3}{R_1R_2+R_2R_3+R_3R_1}$.",
                        "deconstruct": [
                            "$G_1G_2 = 1/(R_1R_2)$, and the pivot is $(R_2R_3+R_1R_3+R_1R_2)/(R_1R_2R_3)$.",
                            "Dividing one by the other, the $R_1R_2$ cancels and leaves $G_{12} = R_3/(R_1R_2+R_2R_3+R_3R_1)$.",
                            "Invert: $R_{12} = (R_1R_2+R_2R_3+R_3R_1)/R_3$. The same numerator serves all three sides of the triangle, divided by the resistance of the *opposite* star leg — which is the only part of the standard formula anyone ever gets backwards.",
                        ],
                    },
                    {
                        "prompt": "Put numbers in. With $R_1 = R_2 = 1$ kΩ and $R_3 = 2$ kΩ, what is $R_{12}$ in kilohms?",
                        "answer": "2.5",
                        "placeholder": "a number, in kilohms",
                        "hint": "The numerator is $R_1R_2 + R_2R_3 + R_3R_1 = (1)(1) + (1)(2) + (2)(1)$, in kΩ². Divide by $R_3 = 2$ kΩ.",
                        "deconstruct": [
                            "Numerator: $1 + 2 + 2 = 5$ kΩ².",
                            "$R_{12} = 5/2 = 2.5$ kΩ.",
                            "As a check by the conductance route: $G_1 = G_2 = 1$ mS, $G_3 = 0.5$ mS, pivot $= 2.5$ mS, $G_{12} = (1)(1)/2.5 = 0.4$ mS, and $1/0.4 = 2.5$ kΩ. The other two sides are $5/R_2 = 5$ kΩ and $5/R_1 = 5$ kΩ.",
                        ],
                    },
                    {
                        "prompt": "Remove the third leg entirely — let $R_3 \\to \\infty$, so terminal 3 is no longer connected to anything. What does $R_{12}$ become?",
                        "answer": "R_1 + R_2",
                        "placeholder": "the simplest thing it could possibly be",
                        "hint": "Split the fraction: $\\dfrac{R_1R_2 + R_3(R_1+R_2)}{R_3} = \\dfrac{R_1R_2}{R_3} + R_1 + R_2$, and let $R_3$ grow.",
                        "deconstruct": [
                            "Group the numerator as $R_1R_2 + R_3(R_1+R_2)$.",
                            "Dividing by $R_3$ gives $R_1R_2/R_3 + R_1 + R_2$, and the first term vanishes as $R_3\\to\\infty$.",
                            "So the delta collapses to the two remaining legs in series, which is what the circuit says without any algebra at all: with terminal 3 disconnected, the only path from 1 to 2 runs through both legs. A limit that lands on something obvious is the cheapest check a derivation offers.",
                        ],
                    },
                ],
                "closing": r'''
That is one Gaussian elimination step, written out in circuit language. The pivot was the
total conductance at the node being removed; the fill-in was three new resistors where
there had been none; and the formula that came out is the star-to-delta transformation,
which is usually presented as something to memorise.

Two things are worth carrying away from having derived it rather than looked it up.

The first is that the transformation is *exact*, and now you can see why: nothing was
approximated at any step, only substituted. Every terminal voltage and every terminal
current is identical before and after, so no measurement made from outside can tell the
star from the delta. That is what "eliminating a variable" means, and it is why a solver
may reorder and remove nodes freely without changing your answer.

The second is the cost. One node with three neighbours became three resistors. A node with
$n$ neighbours becomes $n(n-1)/2$, so removing a node that touches twenty others leaves 190
new entries where there were twenty. Repeat that a few thousand times on a real netlist and
a sparse matrix turns dense, and the simulation that should have taken a second takes an
afternoon. Choosing which node to eliminate next — cheapest first, by degree — is the whole
of sparse-matrix ordering, and it is the direct descendant of the observation in step 3
that a removed node leaves resistors behind.

Running the transformation backwards, delta to star, is the same algebra rearranged:
$R_1 = R_{12}R_{31}/(R_{12}+R_{23}+R_{31})$. It is worth checking once on the numbers
above, where it returns 1 kΩ, 1 kΩ and 2 kΩ as it must. The pair together are what let you
reduce an unbalanced bridge by hand: replace the triangle of three resistors with a star,
and what is left collapses under series and parallel. Elimination and the series-parallel
rules are not rivals — the second is what the first leaves behind once the awkward node has
gone.
''',
            },
            "lab": {
                "title": "Elimination, and the two ways it fails",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Write elimination yourself, once, so that the failures are recognisable when a library
reports them.

- `row_echelon(A)` returns `(U, swaps)`: the matrix after elimination with **partial
  pivoting**, and the number of row exchanges that took. Work along the columns keeping
  a separate row counter, so a column with no usable pivot can be passed over without
  losing your place.
- `pivots(A)` returns the pivot values — the first entry of each non-zero row of `U`.
- `determinant(A)` returns $(-1)^{\text{swaps}}$ times the product of the diagonal of `U`.
- `rank(A)` returns the number of pivots.
- `solve(A, b)` eliminates on the augmented matrix and back-substitutes, and raises
  `ValueError` if `A` is singular rather than returning a number nobody should trust.

`numpy.linalg.solve` and `numpy.linalg.det` are not the exercise; use them to check
yourself afterwards if you like, but the checks ask for the pivots and the swap count,
which no library hands back.

## Partial pivoting, in one line

At column `c`, with the next free row `r`:

```text
k = r + int(np.argmax(np.abs(U[r:, c])))
```

is the row holding the largest entry available in that column. If it is not `r`, swap
the two rows and count it. If the largest entry available is *zero*, there is no pivot
in this column at all: zero the column, leave `r` where it is, and move to the next
column. That branch is the whole of rank detection.

## Why the largest

Dividing by a pivot multiplies every rounding error already in the row by
$1/\text{pivot}$. A pivot of $10^{-14}$ next to entries of order 1 therefore turns
noise into signal, and the answer comes back confidently wrong rather than obviously
wrong. Choosing the largest entry available bounds every multiplier by 1, and that
single line is most of what separates a working solver from a demonstration.
''',
                "files": [{"name": "main.py", "content": r'''
"""Elimination with partial pivoting: the pivots, the determinant and the rank."""

import numpy as np


def row_echelon(A, tol=1e-12):
    """Upper-triangular form by elimination with partial pivoting.

    Returns (U, swaps): the eliminated matrix, and how many row exchanges it took.
    """
    U = np.array(A, dtype=float)
    # TODO: walk the columns with a separate row counter r. At column c, find the
    #       largest |U[i, c]| for i >= r; if it is below tol, zero the column and
    #       carry on without advancing r; otherwise swap it up, count the swap,
    #       clear everything beneath it, and advance r.
    return U, 0


def pivots(A, tol=1e-12):
    """The pivot values: the first non-negligible entry of each non-zero row of U."""
    # TODO: eliminate, then for each row take its first entry with |value| > tol.
    return []


def determinant(A, tol=1e-12):
    """(-1)**swaps times the product of the diagonal of U."""
    # TODO: np.prod(np.diag(U)), with the sign from the swap count.
    return 0.0


def rank(A, tol=1e-12):
    """The number of pivots."""
    # TODO: one line, once pivots works.
    return 0


def solve(A, b, tol=1e-12):
    """Solve A x = b by elimination and back substitution."""
    # TODO: refuse a singular A with ValueError; otherwise eliminate on the
    #       augmented matrix np.column_stack([A, b]) and back-substitute.
    return np.zeros(np.asarray(A).shape[0])


if __name__ == "__main__":
    G = [[1.0, -1.0, 0.0], [-1.0, 3.0, -1.0], [0.0, -1.0, 2.0]]
    print("U, swaps:", row_echelon(G))
    print("pivots:", pivots(G))
    print("det:", determinant(G), " rank:", rank(G))
    print("solve:", solve(G, [1.0, 0.0, 0.0]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Elimination with partial pivoting: the pivots, the determinant and the rank.

Verified by running this file on the network of the blanks exercise:
    U has diagonal 1, 2, 1.5 and needed no row exchanges
    det = 3.0 exactly, rank 3
    solve(G, [1, 0, 0]) -> [1.6666667, 0.6666667, 0.3333333], which is
    np.linalg.solve to 3e-16
"""

import numpy as np


def row_echelon(A, tol=1e-12):
    """Upper-triangular form by elimination with partial pivoting.

    Returns (U, swaps): the eliminated matrix, and how many row exchanges it took.
    """
    U = np.array(A, dtype=float)
    n, m = U.shape
    swaps = 0
    r = 0
    for c in range(m):
        if r >= n:
            break
        k = r + int(np.argmax(np.abs(U[r:, c])))
        if abs(U[k, c]) <= tol:
            U[r:, c] = 0.0
            continue
        if k != r:
            U[[r, k]] = U[[k, r]]
            swaps += 1
        for i in range(r + 1, n):
            f = U[i, c] / U[r, c]
            U[i, c:] = U[i, c:] - f * U[r, c:]
        r += 1
    return U, swaps


def pivots(A, tol=1e-12):
    """The pivot values: the first non-negligible entry of each non-zero row of U."""
    U, _ = row_echelon(A, tol)
    out = []
    for row in U:
        nz = np.nonzero(np.abs(row) > tol)[0]
        if len(nz):
            out.append(float(row[nz[0]]))
    return out


def determinant(A, tol=1e-12):
    """(-1)**swaps times the product of the diagonal of U."""
    U, swaps = row_echelon(A, tol)
    return float((-1.0) ** swaps * np.prod(np.diag(U)))


def rank(A, tol=1e-12):
    """The number of pivots."""
    return len(pivots(A, tol))


def solve(A, b, tol=1e-12):
    """Solve A x = b by elimination and back substitution."""
    A = np.asarray(A, dtype=float)
    n = A.shape[0]
    if rank(A, tol) < n:
        raise ValueError("the matrix is singular: no unique solution")
    U, _ = row_echelon(np.column_stack([A, np.asarray(b, dtype=float)]), tol)
    x = np.zeros(n)
    for i in range(n - 1, -1, -1):
        x[i] = (U[i, n] - U[i, i + 1:n] @ x[i + 1:n]) / U[i, i]
    return x


if __name__ == "__main__":
    G = [[1.0, -1.0, 0.0], [-1.0, 3.0, -1.0], [0.0, -1.0, 2.0]]
    print("U, swaps:", row_echelon(G))
    print("pivots:", pivots(G))
    print("det:", determinant(G), " rank:", rank(G))
    print("solve:", solve(G, [1.0, 0.0, 0.0]))
'''}],
                "hints": [
                    "`U = np.array(A, dtype=float)` makes a copy, which matters: eliminating in place on the caller's list would destroy the matrix they passed in.",
                    "`U[[r, k]] = U[[k, r]]` swaps two rows of a NumPy array in one statement. Doing it with a temporary variable works too; doing it with `U[r] = U[k]; U[k] = U[r]` does not.",
                    "Eliminate from column `c` rightwards — `U[i, c:] -= f * U[r, c:]` — not from column 0. The entries to the left are already zero, and touching them only puts rounding dust back into them.",
                    "In `solve`, the augmented matrix has one extra column, so the right-hand side is `U[i, n]` and the coefficients are `U[i, i+1:n]`. Eliminate the augmented matrix in one pass rather than eliminating `A` and trying to replay the operations on `b`.",
                    "For `rank`, count the pivots rather than the non-zero diagonal entries: for a square matrix of full rank they agree, and for a singular one they do not, which is the case that matters.",
                ],
                "tests": [
                    {"name": "elimination reaches upper triangular form", "code": r'''
G = [[1.0, -1.0, 0.0], [-1.0, 3.0, -1.0], [0.0, -1.0, 2.0]]
U, swaps = row_echelon(G)
assert swaps == 0, f"the largest entry already tops each column here, so no exchanges; got {swaps}"
want = np.array([[1.0, -1.0, 0.0], [0.0, 2.0, -1.0], [0.0, 0.0, 1.5]])
assert np.allclose(U, want), f"expected\n{want}\ngot\n{U}"
assert np.allclose(np.array(G), [[1.0, -1.0, 0.0], [-1.0, 3.0, -1.0], [0.0, -1.0, 2.0]]), \
    "the input matrix must not be modified; make a copy before eliminating"
'''},
                    {"name": "a swap is forced, and it flips the sign of the determinant", "code": r'''
U, swaps = row_echelon([[0.0, 1.0], [1.0, 0.0]])
assert swaps == 1, f"a zero in the pivot position forces exactly one exchange, got {swaps}"
d = determinant([[0.0, 1.0], [1.0, 0.0]])
assert abs(d + 1.0) < 1e-12, f"swapping two rows negates the determinant, so this is -1, got {d}"
d2 = determinant([[0.0, 2.0], [3.0, 4.0]])
assert abs(d2 + 6.0) < 1e-12, f"0*4 - 2*3 = -6, got {d2}"
'''},
                    {"name": "the pivots, the determinant and the rank of a network matrix", "code": r'''
G = [[1.0, -1.0, 0.0], [-1.0, 3.0, -1.0], [0.0, -1.0, 2.0]]
p = pivots(G)
assert len(p) == 3, f"a full-rank 3x3 has three pivots, got {len(p)}"
assert np.allclose(p, [1.0, 2.0, 1.5]), f"the pivots are 1, 2 and 1.5, got {p}"
assert abs(determinant(G) - 3.0) < 1e-12, \
    f"the determinant is the product of the pivots, 3, got {determinant(G)}"
assert rank(G) == 3, f"rank 3, got {rank(G)}"
lad = [[2.0, -1.0, 0.0], [-1.0, 3.0, -1.0], [0.0, -1.0, 2.0]]
assert abs(determinant(lad) - 8.0) < 1e-9, f"this one has determinant 8, got {determinant(lad)}"
'''},
                    {"name": "a floating section is singular, and solve says so", "code": r'''
F = [[1.0, -1.0, 0.0], [-1.0, 1.0, 0.0], [0.0, 0.0, 2.0]]
assert rank(F) == 2, \
    f"two nodes joined only to each other contribute one pivot between them, so rank 2; got {rank(F)}"
assert abs(determinant(F)) < 1e-12, f"a singular matrix has determinant 0, got {determinant(F)}"
try:
    solve(F, [1.0, 0.0, 0.0])
    raise AssertionError("solve must raise ValueError on a singular matrix, not return a number")
except ValueError:
    pass
'''},
                    {"name": "solving, including a system that needs the exchange", "code": r'''
G = [[1.0, -1.0, 0.0], [-1.0, 3.0, -1.0], [0.0, -1.0, 2.0]]
x = solve(G, [1.0, 0.0, 0.0])
assert np.allclose(x, [5.0 / 3.0, 2.0 / 3.0, 1.0 / 3.0]), \
    f"expected [1.6667, 0.6667, 0.3333] volts for 1 mA into node 1, got {x}"
assert np.allclose(x, np.linalg.solve(np.array(G), np.array([1.0, 0.0, 0.0]))), \
    "and it must agree with the library solver"
y = solve([[0.0, 1.0, 1.0], [2.0, 1.0, -1.0], [1.0, -1.0, 1.0]], [3.0, 2.0, 1.0])
assert np.allclose(y, [1.0, 1.5, 1.5]), \
    f"this one has a zero where the first pivot should be, so it needs the exchange; expected [1, 1.5, 1.5], got {y}"
'''},
                ],
            },
            "quiz": {
                "title": "Pivots, rank and singular circuits",
                "minutes": 8,
                "questions": [
                    {
                        "q": "In Gaussian elimination, a **pivot** is:",
                        "opts": [
                            "the largest entry anywhere in the matrix",
                            "the entry used to clear the entries beneath it in its column",
                            "the last entry on the diagonal",
                            "the right-hand side of the equation",
                        ],
                        "a": 1,
                        "why": r'''
Each pivot is the entry that does the work for one column: every row below has a
multiple of the pivot row subtracted from it so that the column ends up empty
underneath. Everything else in elimination is bookkeeping around that one operation.
Partial pivoting chooses the largest entry *available in that column*, which is a
different and much weaker claim than the largest in the matrix.
''',
                    },
                    {
                        "q": "$\\det A = 0$ tells you that:",
                        "opts": [
                            "$A$ has a zero row somewhere",
                            "$Ax = b$ has exactly one solution and it is zero",
                            "the columns of $A$ are dependent, so $Ax = b$ has either no solution or infinitely many",
                            "the matrix is too small to be solved",
                        ],
                        "a": 2,
                        "why": r'''
A zero determinant means elimination reaches a column with no usable pivot, which means
some column of $A$ is a combination of the others. Which of the two failures you get
depends on $b$: if $b$ happens to lie in the column space there are infinitely many
answers, and otherwise none. A zero row is one way to be singular and not the only one —
$\begin{bmatrix}1&2\\2&4\end{bmatrix}$ has no zero row and no inverse. And $Ax=0$ always
has $x=0$ among its solutions; singularity is exactly the case where it has others too.
''',
                    },
                    {
                        "q": "The nullspace of a conductance matrix $G$ contains a non-zero vector. In the circuit that means:",
                        "opts": [
                            "a resistor has been given a negative value",
                            "the supply voltage is too small",
                            "there are more resistors than nodes",
                            "there is a pattern of node voltages that drives no current anywhere, so no measurement can tell it from zero",
                        ],
                        "a": 3,
                        "why": r'''
$Gv = 0$ with $v \ne 0$ says precisely that: set the node voltages to that pattern and
not one microamp flows. The usual cause is a section of the circuit with no resistive
path to ground — you can lift the whole section to any potential you like and nothing
in the circuit objects. It is the same failure the schematic editor reports as
"under-determined", stated in the language of the matrix, and adding one resistor to
ground removes it.
''',
                    },
                    {
                        "q": "Partial pivoting means:",
                        "opts": [
                            "swapping rows so that the largest available entry in the column becomes the pivot",
                            "solving only part of the system and estimating the rest",
                            "discarding entries that are small",
                            "dividing every row by its largest entry before starting",
                        ],
                        "a": 0,
                        "why": r'''
The aim is accuracy rather than correctness: exact arithmetic would not need it at all.
Dividing by a small pivot multiplies whatever rounding error is already in the row by a
large factor, and the answer comes back wrong without looking wrong. Choosing the
largest available entry keeps every multiplier at or below 1 in magnitude, which bounds
the damage. Dividing each row by its largest entry is *scaling*, a real technique and a
different one, sometimes used alongside pivoting rather than instead of it.
''',
                    },
                    {
                        "q": "A network puts a 1 Ω resistor and a 10 MΩ resistor in the same conductance matrix. That matrix is:",
                        "opts": [
                            "singular",
                            "not symmetric",
                            "invertible, but badly conditioned — small errors in the data become large errors in the answer",
                            "guaranteed to give the wrong answer",
                        ],
                        "a": 2,
                        "why": r'''
Conditioning and singularity are different diseases with different treatments. A badly
conditioned matrix still has exactly one answer; it is an answer that moves a long way
when the data moves a little, so the digits at the end of it mean less than they appear
to. Symmetry is untouched — a resistor still conducts equally both ways whatever its
value. And the answer is not *wrong*: it is the exact answer to a problem very slightly
different from the one you posed, which is the honest way to describe every floating
point result.
''',
                    },
                ],
            },
        },

        # ---- M8 -----------------------------------------------------------
        {
            "title": "Orthogonality and projection",
            "summary": "When an equation has no answer, the best available substitute is the closest thing to one — and closest turns out to mean at a right angle. That is the whole of least squares, before any formula.",
            "concepts": [
                "The inner product $a^\\top b = \\sum_i a_i b_i$ measures how much of $b$ points along $a$, and $a \\perp b$ means exactly $a^\\top b = 0$. Length is the same operation applied to one vector: $\\|a\\| = \\sqrt{a^\\top a}$.",
                "**Projection onto a line**: the closest point of the line through $a$ to a vector $b$ is $p = \\hat{x}a$ with $\\hat{x} = \\dfrac{a^\\top b}{a^\\top a}$. Minimising the distance and making the residual perpendicular are the same condition, reached by differentiating or by drawing a right angle.",
                "**Projection onto a subspace** is that argument run once per column. The residual must be perpendicular to every column of $A$, which is the single statement $A^\\top(b - A\\hat{x}) = 0$ — the normal equations, arrived at without ever mentioning least squares.",
                "Orthogonal vectors are automatically independent, and with an **orthonormal** basis every coefficient is a single dot product and no system needs solving at all. Gram–Schmidt manufactures one by subtracting off, from each new vector, its projections onto the ones already accepted.",
                "For a symmetric matrix — and a conductance matrix is symmetric — the nullspace and the column space are orthogonal complements. What the map destroys is perpendicular to everything it can reach, so the floating pattern of node voltages from the previous module is at right angles to every current distribution the network can actually produce.",
            ],
            "read": [
                {
                    "title": "How much of one vector lies along another",
                    "minutes": 15,
                    "body": r'''
Two lists of numbers of the same length. Call one of them $a$ — a *shape*, a pattern you
already know the system can produce. Call the other $b$ — what you actually measured. The
question this module is built on is how much of $a$ is present in $b$, and how much of
$b$ is left over that no amount of $a$ can account for.

Take that picture literally before taking it algebraically. Draw the line through the
origin in the direction of $a$. Draw $b$ as an arrow from the origin pointing somewhere
off that line. Now drop $b$ onto the line the way a post drops a shadow at noon: straight
down, square on. What lands on the line is the part of $b$ that the direction $a$ can
explain. The arrow from that shadow back up to $b$ is the part it cannot.

That is the whole of least squares. Everything after it is the same picture with more
directions to work with. What has to be built first is a way of saying "square on" when
the vectors have five entries, or fifty, and cannot be drawn.

## Length, because length is what will be minimised

Start with one vector and Pythagoras. In the plane, $(3, 4)$ has length
$\sqrt{3^2 + 4^2} = 5$. In three dimensions the same argument runs twice — once flat,
once vertical — and gives $\sqrt{x^2+y^2+z^2}$. Nothing in it cares how many times it is
repeated, so in $n$ dimensions

$$\|a\| = \sqrt{a_1^2 + a_2^2 + \cdots + a_n^2}$$

It is worth naming the thing under the square root, because it is what the algebra
actually handles:

$$\|a\|^2 = a^\top a = \sum_i a_i^2$$

Read $a^\top a$ as a $1\times n$ row times an $n\times 1$ column, which is a $1\times1$
matrix — an ordinary number. Let the two vectors differ and you have the **inner
product**:

$$a^\top b = \sum_i a_i b_i$$

So far this is a definition and nothing more. It has not been shown to mean anything.

## The angle is not put in; it comes out

Here is where it earns its keep. Take the triangle whose sides are $a$, $b$ and $b - a$,
and write the law of cosines for the angle $\theta$ between $a$ and $b$:

$$\|b - a\|^2 = \|a\|^2 + \|b\|^2 - 2\|a\|\,\|b\|\cos\theta$$

Now expand that same left-hand side using nothing but the definition:

$$\|b-a\|^2 = (b-a)^\top(b-a) = b^\top b - 2\,a^\top b + a^\top a$$

Set the two against each other. $\|a\|^2$ and $\|b\|^2$ appear on both sides and cancel,
and what survives is

$$a^\top b = \|a\|\,\|b\|\cos\theta$$

Nobody defined the inner product in order to measure angles. It was defined as a sum of
products, and the angle fell out. Which makes the next line worth what it costs:

$$a^\top b = 0 \quad\Longleftrightarrow\quad \cos\theta = 0 \quad\Longleftrightarrow\quad a \perp b$$

Perpendicularity in any number of dimensions is one arithmetic test. $(1,2)$ and $(2,-1)$
pass it: $2 - 2 = 0$. So do $(1,1,1,1)$ and $(1,-1,1,-1)$. Neither pair had to be drawn,
and the second pair lives in a space nobody can draw.

## The closest point of a line

Back to the shadow. The candidates are the points $xa$, one for every scalar $x$; the one
wanted is the one nearest $b$. Two arguments find it, and they turn out to be the same
argument.

**The right angle.** At the closest point the leftover $e = b - xa$ has to be
perpendicular to the line. If it leaned, some part of it would point along $a$, and
sliding a little way in that direction would get closer — so leaning is proof you are not
there yet. Perpendicular means $a^\top(b - xa) = 0$, that is

$$a^\top b - x\,a^\top a = 0 \qquad\Longrightarrow\qquad \hat{x} = \frac{a^\top b}{a^\top a}$$

**The calculus.** Minimise $\|b - xa\|^2 = b^\top b - 2x\,a^\top b + x^2\,a^\top a$. It is
a quadratic in one variable with a positive coefficient on $x^2$, so it opens upwards and
has exactly one stationary point, a minimum. Its derivative is
$-2\,a^\top b + 2x\,a^\top a$, and setting that to zero returns the same $\hat{x}$. The
derivation unit in this module walks that route line by line. Having both matters: the
geometry and the algebra are not two facts that happen to agree, they are one fact seen
from two sides.

The projected point is $p = \hat{x}a$ and the leftover, the **residual**, is $e = b - p$.
Notice what $\hat{x}$ is: a *coefficient*, the number of copies of $a$ you need. It is the
length of the projection only in the special case $\|a\| = 1$.

## Worked example: one resistor, three measurements

A resistor is measured three times. At 1.0, 2.0 and 3.0 mA the voltage across it reads
2.1, 3.9 and 6.3 V. Ohm's law says $V = RI$ with no constant term, so the model is a line
forced through the origin: the vector of currents is the shape $a$, the vector of voltages
is the measurement $b$, and $R$ is the coefficient.

```
a = ( 1.0, 2.0, 3.0 ) mA          b = ( 2.1, 3.9, 6.3 ) V

a'b = 1.0(2.1) + 2.0(3.9) + 3.0(6.3)
    = 2.1 + 7.8 + 18.9                       = 28.8
a'a = 1.0^2 + 2.0^2 + 3.0^2
    = 1 + 4 + 9                              = 14.0

R = 28.8 / 14.0                              = 2.0571 kohm
```

The units work out: volts times milliamps over milliamps squared is volts per milliamp,
which is kilohms. Now the fitted voltages and what is left over:

```
p = R a = ( 2.0571, 4.1143, 6.1714 ) V
e = b - p = ( 0.0429, -0.2143, 0.1286 ) V
```

And the check that costs nothing and catches everything:

```
a'e = 1.0(0.0429) + 2.0(-0.2143) + 3.0(0.1286)
    = 0.0429 - 0.4286 + 0.3857                = 0.0000
```

Zero, as it must be. The residual is perpendicular to the currents. If it were not, some
other resistance would fit better.

The size of the leftover is $\|e\| = \sqrt{0.0429^2 + 0.2143^2 + 0.1286^2} = 0.254$ V.
There is a shortcut for it, and it is Pythagoras applied to the right triangle whose legs
are $p$ and $e$ and whose hypotenuse is $b$: since $\|b\|^2 = \|p\|^2 + \|e\|^2$ and
$\|p\|^2 = \hat{x}^2 a^\top a = (a^\top b)^2/a^\top a$,

$$\|e\|^2 = \|b\|^2 - \frac{(a^\top b)^2}{a^\top a}$$

```
|b|^2 = 2.1^2 + 3.9^2 + 6.3^2 = 4.41 + 15.21 + 39.69 = 59.31
(a'b)^2 / a'a = 28.8^2 / 14.0 = 829.44 / 14.0        = 59.246
|e|^2 = 59.31 - 59.246                               = 0.0643
|e|  = 0.254 V
```

which agrees with the direct sum. Both routes are worth having: on a long vector the
shortcut is one subtraction instead of $n$, and on any vector the two disagreeing is
immediate proof that a number was mistyped.

## Worked example: an average is a projection

Four readings of a supply that should be constant: 5.10, 4.86, 5.22 and 4.98 V. The shape
here is $a = (1,1,1,1)$ — "the same value at every reading" — and the coefficient is that
value.

```
a'b = 5.10 + 4.86 + 5.22 + 4.98                = 20.16
a'a = 1 + 1 + 1 + 1                            = 4

x^ = 20.16 / 4                                 = 5.04 V
```

The projection of a vector onto the line of all-ones is its mean. That is not a
coincidence dressed up in notation; it is the reason the mean is the summary anyone
reaches for. It is the single constant that comes closest, in the sum-of-squares sense, to
the whole record.

The residuals are the deviations from the mean:

```
e = ( 0.06, -0.18, 0.18, -0.06 ) V
sum of e = 0.06 - 0.18 + 0.18 - 0.06           = 0.00
```

Everyone learns that deviations from a mean sum to zero and most people file it as an
arithmetic curiosity. It is the orthogonality condition. "Sum of the residuals is zero" is
literally $a^\top e = 0$ with $a$ the all-ones vector, and it holds *because* the mean is
the projection, not the other way round.

## The mistakes

**Dividing by the wrong thing.** $\hat{x} = a^\top b / a^\top a$, not $a^\top b/\|a\|$
and not $a^\top b/b^\top b$. Dividing by the length rather than the length squared is the
tempting one, because "normalise by the size of $a$" sounds like something you do once.
There is a test that settles it in ten seconds. Replace $a$ by $2a$: the line is exactly
the same line, so the projected point $p$ must not move.

```
correct:   x^ = (2a)'b / (2a)'(2a) = 2(a'b) / 4(a'a) = x^/2
           p  = (x^/2)(2a) = x^ a                     -- unmoved, as required

wrong:     x^ = (2a)'b / |2a| = 2(a'b) / 2|a|        = unchanged
           p  = x^ (2a) = 2 (x^ a)                    -- the point jumped
```

A formula that makes the closest point of a line depend on how you chose to name the
direction is not measuring anything. Run that test once, on paper, and the right version
stays fixed.

**Reading $a^\top b = 0$ as "one of them is zero".** It says the two are at a right angle.
$(1,2)^\top(2,-1) = 0$ with neither vector anywhere near zero.

**Reporting $\hat{x}$ when the length of the projection was asked for.** They differ by a
factor of $\|a\|$. In the resistor example $\hat{x} = 2.06$ and $\|p\| = 2.06\times3.74 =
7.70$ V, and only one of those is a voltage.

## Where this stops

**When the entries have different units.** $\|b\|^2 = \sum b_i^2$ silently adds the
squares of every entry, which is meaningful only if they are the same kind of quantity. A
vector holding a voltage and a current has no length worth the name, and "closest" applied
to it means whatever the choice of units happened to make it mean. Rescale the volts to
millivolts and the answer moves. The repair is a weighted inner product,
$a^\top W b$ with a positive diagonal $W$, chosen so that the weighted entries are
comparable — and the natural choice of weight is one over the variance of that
measurement, so that noisy readings count for less. The numeric units at the end of this
module show a resistor network doing precisely that weighting, in hardware, without being
asked.

**When the vectors are complex.** Phasors are complex, and for them $a^\top a$ is not a
length. Take $a = (1, j)$: the plain sum of squares gives $1 + j^2 = 0$, so a non-zero
vector would have zero length. The fix is to conjugate one side, $a^{H}b = \sum
\overline{a_i}b_i$, after which $a^{H}a = \sum|a_i|^2$ is real and positive. Every
statement in this module survives the change with $\top$ replaced by $H$; nothing else has
to move. It is worth knowing before the first time you project one phasor onto another,
because the plain transpose does not announce that it has failed — it returns a number,
and the number is wrong.

**When "closest" is not what you want.** Least squares punishes a residual by its square,
so one reading that is out by ten counts as much as a hundred that are out by one. If a
measurement can be *wrong* rather than merely noisy — a probe that slipped, a digit
transcribed badly — the projection will swing towards it, and it will swing hardest
precisely when the outlier is worst. That is not a flaw in the algebra, it is the
definition of distance you chose. Minimising $\sum|e_i|$ instead gives an estimator that
shrugs off outliers, at the price of every clean thing in this module: no right angle, no
formula, no single dot product, and a minimisation that has to be done numerically.
''',
                },
                {
                    "title": "From a line to a subspace: the normal equations",
                    "minutes": 16,
                    "body": r'''
One direction was enough to fit a resistance. It is not enough to fit anything with two
knobs on it — a battery with an internal resistance, a signal with a DC offset, a decay
with an unknown starting amplitude. For those you get several shapes to mix, and the set
of things you can build out of them is no longer a line.

Write the shapes as the columns of a matrix $A$. Then $Ax$ — with $x$ the vector of
coefficients — is exactly a mixture: $x_1$ of the first column, plus $x_2$ of the second,
and so on. The set of every possible $Ax$ is the **column space** of $A$: a plane if there
are two independent columns, a three-dimensional slab if there are three. It lives inside
the $m$-dimensional space that the measurements live in, where $m$ is the number of
measurements, and if $m$ is bigger than the number of columns then it is a *thin* set. A
plane in five dimensions is a very small place, and a measured $b$ has no reason
whatsoever to land on it.

That is the situation this whole subject exists for: $Ax = b$ with more equations than
unknowns, and no solution. Not "a hard solution" — none. The honest response is to stop
asking for $b$ and ask instead for the point of the column space nearest to $b$.

## One right angle per column

The picture is the shadow again, but now $b$ drops onto a plane rather than a line, and
"straight down" means perpendicular to the whole plane. A vector is perpendicular to a
plane exactly when it is perpendicular to everything that spans it, and the columns of $A$
span it. So the residual $e = b - A\hat{x}$ has to satisfy one equation per column:

$$a_1^\top(b - A\hat{x}) = 0, \qquad a_2^\top(b - A\hat{x}) = 0, \qquad \dots$$

Stacking those rows is exactly what left-multiplying by $A^\top$ does, because the rows of
$A^\top$ are the columns of $A$. So the whole set is one statement:

$$A^\top(b - A\hat{x}) = 0 \qquad\Longrightarrow\qquad A^\top A\,\hat{x} = A^\top b$$

Those are the **normal equations**, and "normal" here is the old word for perpendicular,
not for ordinary. Nothing was minimised to get them and the phrase "least squares" was
never used. They came from one sentence: the leftover must be square on to every shape you
were allowed to use.

Look at what $A^\top A$ is. Its $(i,j)$ entry is $a_i^\top a_j$ — the inner product of
column $i$ with column $j$. It is the table of every pairing between the shapes, it is
symmetric because $a_i^\top a_j = a_j^\top a_i$, and its diagonal holds the squared lengths
of the columns, all positive. It is $n \times n$, where $n$ is the number of unknowns, so
it is small even when $b$ has ten thousand entries. Tall skinny problem in, small square
system out.

## Worked example: a battery with an internal resistance

A two-terminal part — a resistor with a small fixed offset in series with it — is driven
by a current source, and the terminal voltage is recorded at four settings. At 0, 1, 2 and
3 mA it reads 1.0, 3.1, 4.9 and 7.2 V. The model is $V = c + d\,I$, so the two shapes are
the all-ones column, which carries the offset, and the column of currents, which carries
the resistance.

```
        [ 1  0 ]              [ 1.0 ]
A   =   [ 1  1 ]        b  =  [ 3.1 ]
        [ 1  2 ]              [ 4.9 ]
        [ 1  3 ]              [ 7.2 ]

A'A = [ 4   6 ]   4 = 1+1+1+1,  6 = 0+1+2+3,  14 = 0+1+4+9
      [ 6  14 ]

A'b = [ 16.2 ]    16.2 = 1.0+3.1+4.9+7.2
      [ 34.5 ]    34.5 = 0(1.0)+1(3.1)+2(4.9)+3(7.2) = 0+3.1+9.8+21.6
```

A $2\times2$ system, solved by Cramer or by one elimination step:

```
det = 4(14) - 6(6) = 56 - 36                 = 20

c = ( 16.2(14) - 6(34.5) ) / 20 = ( 226.8 - 207.0 ) / 20 = 19.8/20  = 0.99 V
d = ( 4(34.5) - 6(16.2) ) / 20  = ( 138.0 - 97.2 ) / 20  = 40.8/20  = 2.04 V/mA
```

So an offset of 0.99 V and a slope of 2.04 V/mA, which is 2.04 kΩ. Fit and residuals:

```
fitted  = ( 0.99, 3.03, 5.07, 7.11 ) V
e = b - A x^ = ( 0.01, 0.07, -0.17, 0.09 ) V
```

Two checks, one per column, and they are the normal equations read back:

```
ones' e = 0.01 + 0.07 - 0.17 + 0.09                  = 0.00
I'    e = 0(0.01) + 1(0.07) + 2(-0.17) + 3(0.09)
        = 0.07 - 0.34 + 0.27                         = 0.00
```

Both zero. The residuals sum to zero *and* they have no trend against current — which is
the useful reading of orthogonality here. Any leftover trend against $I$ would mean the
slope had more to give, and the fit would not be finished.

## Worked example: the projection matrix, in full

Substituting $\hat{x} = (A^\top A)^{-1}A^\top b$ back into $p = A\hat{x}$ gives the matrix
that takes any measurement straight to its shadow:

$$P = A(A^\top A)^{-1}A^\top$$

Take three points at $x = 0, 1, 2$ with the same two columns as before, so
$A = \begin{bmatrix}1&0\\1&1\\1&2\end{bmatrix}$.

```
A'A   = [ 3  3 ]      det = 3(5) - 3(3) = 6
        [ 3  5 ]

(A'A)^-1 = (1/6) [  5  -3 ]
                 [ -3   3 ]

P = A (A'A)^-1 A' = (1/6) [  5   2  -1 ]
                          [  2   2   2 ]
                          [ -1   2   5 ]
```

Three things about that matrix are worth more than the arithmetic that produced it.

It is **symmetric**. Every projection matrix is, and it falls straight out of the formula:
transposing $A(A^\top A)^{-1}A^\top$ gives itself back, because $A^\top A$ is symmetric and
so is its inverse.

It is **idempotent**: $P^2 = P$. Once you are on the plane, projecting again does nothing,
which is the algebraic form of the sentence "the shadow of a shadow is the shadow".

Its **trace is the rank**: $(5 + 2 + 5)/6 = 2$, and there are two independent columns. A
projection matrix has eigenvalues 1 on the subspace and 0 off it, and the trace counts the
ones.

Try it on $b = (1, 2, 6)$, a badly bent set of readings:

```
P b = (1/6) ( 5+4-6, 2+4+12, -1+4+30 ) = (1/6)( 3, 18, 33 ) = ( 0.5, 3.0, 5.5 )
e   = b - Pb = ( 0.5, -1.0, 0.5 )

check:  ones' e = 0.5 - 1.0 + 0.5           = 0
        x'    e = 0(0.5) + 1(-1.0) + 2(0.5) = 0
```

The fit is $0.5 + 2.5x$, and the same numbers come out of the normal equations
$\begin{bmatrix}3&3\\3&5\end{bmatrix}\hat{x} = \begin{bmatrix}9\\14\end{bmatrix}$, whose
solution is $\hat{x} = (0.5, 2.5)$. The matrix $I - P$ is a projection too — onto
everything perpendicular to the plane — and it is what produced $e$ directly.

## The mistakes

**Cancelling $A^\top$.** Given $A^\top A\hat{x} = A^\top b$ the hand wants to strike the
$A^\top$ off both sides and write $A\hat{x} = b$. It is desperately tempting, because on
square invertible matrices that is legal. It is wrong here for the reason the whole
problem exists: $A$ is tall, $A^\top$ is wide, and a wide matrix has a nullspace. $A^\top$
sends many different vectors to the same place, and $b$ and $A\hat x$ are two of them —
they differ by exactly $e$, which $A^\top$ kills. If you *could* cancel, $Ax = b$ would
have a solution and none of this would be needed.

**Assuming a small residual means a good model.** The residual is short whenever the
column space happens to lie near $b$, and adding a column can only shorten it, never
lengthen it — including a column of pure noise. Four points and four independent columns
give a residual of exactly zero and a model that has learned nothing. What tells you
something is the *shape* of the residual:
if it is orthogonal to every column but still visibly patterned — all positive in the
middle, all negative at the ends — then a shape is missing from $A$, and the leftover is
telling you which.

**Reading $\hat{x}$ as the truth about the system.** It is the best mix of the columns you
supplied. A slope fitted to four points between 0 and 3 mA describes the source between 0
and 3 mA. Nothing in the algebra objects to evaluating that line at 3 A, and nothing in the
algebra knows that the resistor will be glowing.

## Where this stops

**When the columns are dependent.** If one shape is a combination of the others, $A^\top A$
is singular, there is no unique $\hat{x}$, and the normal equations have infinitely many
solutions. The projection $p$ is still perfectly well defined — the nearest point of the
column space does not care how you describe that space — but the *coefficients* are not.
Give the fit an intercept, a temperature in Celsius and the *same* temperature in
Fahrenheit, and you will see it: $F = 1.8C + 32$, so the third column is a combination of
the first two, and any amount you add to the Celsius coefficient can be paid for out of
the other two. The fitted line is unmoved and unarguable; the three numbers describing it
mean nothing individually. The usual repair
is to pick the shortest $\hat{x}$ among all the minimisers, which is what the pseudoinverse
and every `lstsq` routine return.

**When the columns are nearly dependent.** This is the practical version, and it is worse
than the clean singular case because nothing fails. Forming $A^\top A$ squares the
conditioning: a matrix that a careful method would handle to nine digits becomes one that
loses eighteen. The standard demonstration is

$$A = \begin{bmatrix} 1 & 1 \\ \varepsilon & 0 \\ 0 & \varepsilon\end{bmatrix},
\qquad A^\top A = \begin{bmatrix} 1 + \varepsilon^2 & 1 \\ 1 & 1 + \varepsilon^2\end{bmatrix}$$

with $\varepsilon = 10^{-9}$. The columns of $A$ are plainly independent. But
$\varepsilon^2 = 10^{-18}$, and $1 + 10^{-18}$ rounds to exactly $1$ in double precision,
so the computed $A^\top A$ is $\begin{bmatrix}1&1\\1&1\end{bmatrix}$ — singular, with a
determinant of zero, for a problem that was never singular at all. This is why numerical
libraries do not form $A^\top A$. They factor $A$ itself, by QR or by SVD, and the next
reading builds the QR route out of Gram–Schmidt.

**When the model is not linear in its parameters.** $V = c + dI$ is linear in $c$ and $d$,
which is all that is required; $V = c + dI + eI^2$ is linear in its parameters too, and
fits with a third column of $I^2$. But $V = c\,e^{-t/\tau}$ is not linear in $\tau$, and no
amount of stacking columns makes it so. Taking logs turns it into a linear fit in $\ln c$
and $1/\tau$ — and quietly changes what is being minimised, because equal errors in $\ln V$
are not equal errors in $V$. The small values then count for far more than they should.
That is a real decision with a real cost, not a technicality, and it is worth making on
purpose.
''',
                },
                {
                    "title": "Orthonormal bases, and what a network cannot reach",
                    "minutes": 15,
                    "body": r'''
The normal equations turned a projection into a small square system. That is a good deal,
but there is a better one available whenever you are willing to prepare the columns first:
if the shapes are perpendicular to each other, there is no system left to solve at all.

## Coefficients for free

Suppose $q_1, \dots, q_n$ are **orthonormal** — mutually perpendicular and each of length
one, so $q_i^\top q_j$ is 1 when $i = j$ and 0 otherwise. Ask for the projection of $b$
onto their span. The normal equations still apply, but $Q^\top Q = I$, so

$$Q^\top Q\,\hat{x} = Q^\top b \qquad\Longrightarrow\qquad \hat{x} = Q^\top b$$

Every coefficient is one dot product. $\hat{x}_i = q_i^\top b$, computed without reference
to any of the others, and

$$p = (q_1^\top b)\,q_1 + (q_2^\top b)\,q_2 + \cdots$$

Each term is the projection onto one direction, and they simply add. This is why
orthogonal bases are worth building: the Fourier series is exactly this sentence with
sinusoids as the $q_i$, and the reason a Fourier coefficient is one integral rather than
the solution of an infinite system is that $\int \sin m\omega t\,\sin n\omega t\,dt$
vanishes for $m \ne n$.

## Gram–Schmidt: subtract off what is already covered

Given independent columns that are *not* perpendicular, make them so. Take them one at a
time; each new vector keeps only the part of itself that the ones already accepted could
not reach.

Take the two columns from the previous reading, $a_1 = (1,1,1)$ and $a_2 = (0,1,2)$.

```
step 1.  normalise the first
         |a1| = sqrt(3),   q1 = (1,1,1)/sqrt(3)

step 2.  how much of a2 lies along q1
         q1'a2 = (0 + 1 + 2)/sqrt(3) = 3/sqrt(3) = sqrt(3)

step 3.  subtract that much off
         (q1'a2) q1 = sqrt(3) * (1,1,1)/sqrt(3) = (1,1,1)
         w = a2 - (1,1,1) = (-1, 0, 1)

step 4.  normalise what is left
         |w| = sqrt(2),   q2 = (-1,0,1)/sqrt(2)

check:   q1'q2 = (-1 + 0 + 1)/sqrt(6) = 0
```

Now redo the fit of $b = (1,2,6)$ with no matrix inverted anywhere:

```
q1'b = (1 + 2 + 6)/sqrt(3) = 9/sqrt(3)  = 5.1962
q2'b = (-1 + 0 + 6)/sqrt(2) = 5/sqrt(2) = 3.5355

p = 5.1962 * (1,1,1)/sqrt(3)  +  3.5355 * (-1,0,1)/sqrt(2)
  = 3.0 (1,1,1)              +  2.5 (-1,0,1)
  = ( 3.0, 3.0, 3.0 ) + ( -2.5, 0, 2.5 )
  = ( 0.5, 3.0, 5.5 )
```

The same projection the $3\times3$ matrix $P$ produced in the previous reading, from two
dot products.

Step 3 has a name in another vocabulary. The second column was $(0,1,2)$ — the sample
positions — and what got subtracted was their mean. **Gram–Schmidt on a straight-line fit
is centring the $x$ values.** That is why fitting $y = \alpha + \beta(x - \bar{x})$ is
better behaved than fitting $y = c + dx$: with $x$ values 1000, 1001, 1002, 1003 the
matrix $A^\top A$ has a condition number of about $8\times10^{11}$; subtract the mean and
the same fit has a condition number of 1.25, because the two columns are now perpendicular
and $A^\top A$ is diagonal. Same line, same residuals, twelve digits of accuracy
recovered by one subtraction.

## QR, which is Gram–Schmidt with the bookkeeping kept

Every step above subtracted a known multiple of an accepted vector and then divided by a
known length. Record those numbers and you have factored the matrix:

$$A = QR, \qquad R = \begin{bmatrix} q_1^\top a_1 & q_1^\top a_2 \\ 0 & q_2^\top a_2\end{bmatrix}
= \begin{bmatrix} \sqrt{3} & \sqrt{3} \\ 0 & \sqrt{2}\end{bmatrix}$$

$R$ is upper triangular because $q_2$ was built after $a_1$ was finished with, so it is
perpendicular to it and $q_2^\top a_1 = 0$. Least squares then reads

$$A^\top A\hat{x} = A^\top b \;\longrightarrow\; R^\top R\hat{x} = R^\top Q^\top b \;\longrightarrow\; R\hat{x} = Q^\top b$$

— one back-substitution, and $A^\top A$ never formed. On our numbers,
$\sqrt{2}\,d = 5/\sqrt{2}$ gives $d = 2.5$, then $\sqrt{3}\,c + \sqrt{3}(2.5) = 9/\sqrt{3}
= 3\sqrt{3}$ gives $c = 0.5$. This is what a library routine does when you ask it to solve
an overdetermined system, and it is why the answer it gives is better than the one you get
by typing the normal equations in yourself.

## Symmetric matrices, and the currents a network cannot be given

Now the circuit payoff, and it is the reason this module sits where it does.

For *any* matrix, the nullspace is perpendicular to the row space. That is not a theorem so
much as a restatement: $Gv = 0$ says every row of $G$, dotted with $v$, gives zero. And a
conductance matrix is **symmetric** — a resistor conducts equally in both directions, so
$G_{ij} = G_{ji}$ — which means its rows are its columns. Therefore

$$\mathcal{N}(G) \perp \mathcal{C}(G)$$

for a conductance matrix: what the network destroys is at right angles to everything it can
produce. Their dimensions add to $n$ — rank plus nullity — and they are perpendicular, so
between them they account for the whole space with no overlap. They are orthogonal
complements.

Make it concrete with the smallest floating network there is. Two nodes joined by a 1 kΩ
resistor and nothing else — no path to ground from either of them.

```
G (mS) = [  1  -1 ]        i (mA) = the currents injected at the two nodes
         [ -1   1 ]

nullspace    : span{ (1, 1) }   -- lift both nodes together, no current moves
column space : span{ (1,-1) }   -- whatever it does, it takes in at one node
                                   and gives out at the other
```

Those two lines are perpendicular, as promised. Now read them as physics.

The nullspace says the common level of the island is undetermined: raise both nodes by a
volt and every current is unchanged, so no measurement can tell you where the island sits.
That is the singular circuit from the previous module, and the direction it is singular in
is $(1,1)$.

The column space says something the previous module could not: $Gv = i$ has a solution
**only if $i$ is perpendicular to $(1,1)$**, that is only if $i_1 + i_2 = 0$. And that is
Kirchhoff's current law for the island as a whole. Push 2 mA into node 1 and take 2 mA out
of node 2 and the network copes:

```
i = ( 2, -2 ) mA        v = ( 1, -1 ) V solves it, and so does ( 1, -1 ) + c(1, 1)
                        check: G v = ( 1+1, -1-1 ) = ( 2, -2 ) mA
```

Two volts across a 1 kΩ carries 2 mA, which is the whole of the physics. The difference is
pinned; the common level is not.

Now push 2 mA into node 1 and take nothing out anywhere: $i = (2, 0)$, and
$\mathbf{1}^\top i = 2 \ne 0$. There is no solution, and there had better not be — charge
would be piling up on an island with nowhere to go, and no DC steady state exists. Split
that demand into its two orthogonal halves:

```
( 2, 0 ) = ( 1, -1 ) + ( 1, 1 )    mA
           reachable    unreachable
```

The projection onto the column space is the 1 mA circulation the resistor can carry; the
rest is net charge, and it is precisely the part the network has no answer to. The
least-squares solution of $Gv = i$ satisfies the first half exactly and abandons the
second, which is the most sensible thing anyone could ask of it.

## The mistakes

**Using $q^\top b$ as a coefficient without normalising.** The clean formula needs unit
vectors. With $\|q\| = 2$ the correct coefficient is $q^\top b/4$, and using $q^\top b$
overstates it fourfold. The formula looks identical either way, which is what makes it
easy to ship.

**Believing $QQ^\top = I$.** For a *square* orthogonal matrix it is. For the tall thin $Q$
that comes out of Gram–Schmidt on two columns of a three-entry space, $Q^\top Q = I_2$ but
$QQ^\top$ is the $3\times3$ projection matrix $P$ from the previous reading — it flattens
$\mathbb{R}^3$ onto a plane, and no flattening is the identity. Which of the two is the
identity depends on which product you wrote, and that is genuinely easy to get backwards.

**Trusting classical Gram–Schmidt on nearly dependent columns.** Each subtraction leaves a
short vector that is mostly rounding error, and the vectors that follow inherit it. The
columns come out visibly non-orthogonal — dot products of $10^{-8}$ where zero was
expected. Modified Gram–Schmidt, which subtracts each projection as soon as it is
available rather than all at once, is the same arithmetic in a different order and holds up
far better; Householder reflections are better still, and are what a library actually uses.

## Where this stops

**Non-symmetric matrices.** Drop symmetry and the nullspace and the column space can sit at
any angle, and can even coincide. $N = \begin{bmatrix}0&1\\0&0\end{bmatrix}$ has nullspace
$\mathrm{span}\{(1,0)\}$ and column space $\mathrm{span}\{(1,0)\}$ — the same line, so what
the map destroys is exactly what it produces. The tidy statement above is a fact about
symmetric matrices, and a conductance matrix earns it by being one. A full MNA matrix, with
its $\pm 1$ rows for voltage sources, is *not* symmetric, and none of this applies to it
unchanged.

**Complex matrices.** For phasors, "symmetric" is the wrong condition; the one that buys
the orthogonal complement is **Hermitian**, $G^{H} = G$. An impedance matrix at a real
frequency is complex symmetric but usually not Hermitian, so the perpendicularity above is
a DC statement. It generalises, but it generalises to the conjugate transpose, and it is
worth checking which one you have before relying on it.

**Everything here assumes the columns are independent.** Gram–Schmidt on a dependent set
produces a $w$ of length zero at the offending step, and the normalisation divides by it. In
exact arithmetic that is the signal to discard the vector and move on — it detects
dependence rather than being defeated by it. In floating point the length comes out as
$10^{-16}$ instead of zero, dividing by it produces a unit vector made entirely of noise,
and the algorithm carries on confidently. Deciding where the cutoff goes is not something
the algebra can settle for you; it is a judgement about how big your measurement errors
were.
''',
                },
            ],
            "sandbox": {
                "title": "A map that flattens the plane",
                "visualiser": "phase-portrait",
                "minutes": 9,
                "initial": {"a11": -1, "a12": -1, "a21": -1, "a22": -1},
                "brief": r'''
The short lines are the vector $Ax$ drawn at each point $x$ — the map itself, sampled
on a grid — and the coloured curves follow those arrows from a ring of starting points.
The readout underneath reports the trace and the determinant.

Watch what happens to the plane when the determinant is zero. The columns of $A$ stop
being independent, the image collapses onto a line, and a whole direction gets sent to
nothing at all. Those two lines — what the map can reach, and what it destroys — are the
column space and the nullspace, and this is the one picture in which you can see both at
once.
''',
                "notice": [
                    "It opens with all four entries at $-1$, and the readout says det = 0.00. Every arrow on the grid points along the same 45° line, whichever point it is drawn at. Both columns of $A$ are $(-1,-1)$, so every possible output is a multiple of that one vector: the column space is a line, and the map cannot produce anything off it.",
                    "Follow the curves. Each one slides straight along that 45° direction and then stops dead on the anti-diagonal $x_1 + x_2 = 0$. Those points are where the arrows have zero length — the nullspace — and the matrix sends every one of them to the origin. Here the two lines are exactly perpendicular, because the matrix is symmetric.",
                    "Break the symmetry: leave $a_{11}$ and $a_{12}$ at $-1$ and set both $a_{21}$ and $a_{22}$ to $-2$. The determinant still reads 0.00 and the curves still finish on the same anti-diagonal, but they now arrive at a slant instead of square on. The column space has tilted to the direction $(1,2)$ while the nullspace stayed put, and a projection *along* the column space onto the nullspace is oblique the moment the matrix stops being symmetric.",
                    "Now make it non-singular: put $a_{21}$ and $a_{22}$ back to $-1$, then drag $a_{12}$ to 0. The readout reads det = 1.00, and every curve runs all the way in to the origin instead of stopping short. Nothing is destroyed any more — the only vector sent to zero is zero itself — so there is no line of survivors left for the trajectories to land on.",
                ],
            },
            "blanks": [
                {
                    "title": "Building the normal equations by hand",
                    "minutes": 8,
                    "caption": "three points, two columns, one small square system",
                    "lang": "text",
                    "brief": r'''
Fit $y = c + dx$ to three points. The two shapes are the all-ones column, which carries
the constant, and the column of $x$ values, which carries the slope.

Every entry of $A^\top A$ is one column dotted with another, and every entry of $A^\top b$
is one column dotted with the measurement. Nothing else is involved: no inverse, no
formula to look up, just inner products.

Nothing is executed here — this is arithmetic you are choosing.
''',
                    "listing": """data      x = ( 0,  1,  2 )          model:  y = c + d x
          y = ( 1,  2,  6 )

              [ 1  0 ]                  [ 1 ]
      A   =   [ 1  1 ]         b   =    [ 2 ]
              [ 1  2 ]                  [ 6 ]

      A'A = [  3   ___ ]        A'b = [ ___ ]
            [  3    5  ]              [  14 ]

normal equations
              3 c + 3 d =  9
              3 c + 5 d = 14

      subtract the first from the second:   2 d = 5,   d = ___
      back-substitute:                             c = ___

residual  e = b - A x^   =  ( 0.5, ___ , 0.5 )

check     ones' e = 0          x' e = 0          |e| = sqrt( ___ )
""",
                    "blanks": [
                        {
                            "prompt": "The top-right entry of $A^\\top A$.",
                            "hole": "?",
                            "opts": ["3", "5", "0", "6"],
                            "a": 0,
                            "why": "It is the first column dotted with the second: $1(0) + 1(1) + 1(2) = 3$. It has to match the 3 already printed below the diagonal, because $A^\\top A$ is symmetric for every $A$ — the $(i,j)$ entry and the $(j,i)$ entry are both $a_i^\\top a_j$.",
                            "whys": [
                                "It is the first column dotted with the second: $1(0) + 1(1) + 1(2) = 3$. It has to match the 3 already printed below the diagonal, because $A^\\top A$ is symmetric for every $A$ — the $(i,j)$ entry and the $(j,i)$ entry are both $a_i^\\top a_j$.",
                                "5 is the second column dotted with itself, $0 + 1 + 4$, which is the bottom-right entry. The off-diagonal pairs two *different* columns.",
                                "Zero would say the two columns are perpendicular. They are not: the $x$ values $0, 1, 2$ have a non-zero sum, and that sum is precisely the inner product with the all-ones column. Centring them — using $-1, 0, 1$ instead — would make this entry zero, which is the whole point of centring.",
                                "6 is $0 + 1 + 2 + 3$, the sum of one $x$ value too many. There are three points here, not four.",
                            ],
                        },
                        {
                            "prompt": "The top entry of $A^\\top b$.",
                            "hole": "?",
                            "opts": ["9", "14", "3", "4.5"],
                            "a": 0,
                            "why": "The all-ones column dotted with $b$ is just the sum of the measurements: $1 + 2 + 6 = 9$. Every entry of $A^\\top b$ is one shape dotted with the data, and the shape here is \"the same amount at every point\".",
                            "whys": [
                                "The all-ones column dotted with $b$ is just the sum of the measurements: $1 + 2 + 6 = 9$. Every entry of $A^\\top b$ is one shape dotted with the data, and the shape here is \"the same amount at every point\".",
                                "14 is the entry below it, $x^\\top b = 0(1) + 1(2) + 2(6)$. That one weights the measurements by their $x$ value; this one does not weight them at all.",
                                "3 is the number of measurements, which is the top-left entry of $A^\\top A$, not anything to do with $b$.",
                                "4.5 is half of 9. The factor of two that appears when you differentiate $\\|b - Ax\\|^2$ divides out of both sides of the normal equations and never reaches them.",
                            ],
                        },
                        {
                            "prompt": "The slope $d$.",
                            "hole": "?",
                            "opts": ["2.5", "2", "5", "1.5"],
                            "a": 0,
                            "why": "$2d = 5$ gives $d = 2.5$. Sanity-check it against the data: the points rise by 1 then by 4, so a slope somewhere between those two is what a compromise ought to look like.",
                            "whys": [
                                "$2d = 5$ gives $d = 2.5$. Sanity-check it against the data: the points rise by 1 then by 4, so a slope somewhere between those two is what a compromise ought to look like.",
                                "2 is what $2d = 5$ gives if the 2 in front of $d$ is quietly dropped and the 5 rounded down. Substitute it back: $3c + 3(2) = 9$ makes $c = 1$, and then $3(1) + 5(2) = 13$, not 14. Both equations have to hold at once.",
                                "5 is the right-hand side of the reduced equation, not the unknown. There is still a division by the 2 in front of $d$ to do.",
                                "1.5 solves $2d = 3$, which would be the reduced equation if the two right-hand sides had been subtracted the wrong way round.",
                            ],
                        },
                        {
                            "prompt": "The intercept $c$.",
                            "hole": "?",
                            "opts": ["0.5", "1", "0", "-0.5"],
                            "a": 0,
                            "why": "Back into the first equation: $3c + 3(2.5) = 9$, so $3c = 1.5$ and $c = 0.5$. The fitted line is $y = 0.5 + 2.5x$, which passes below the first point and below the last one, and above the middle one.",
                            "whys": [
                                "Back into the first equation: $3c + 3(2.5) = 9$, so $3c = 1.5$ and $c = 0.5$. The fitted line is $y = 0.5 + 2.5x$, which passes below the first point and below the last one, and above the middle one.",
                                "1 is the first measured value, $y$ at $x = 0$. A least-squares line is not required to pass through any data point, and here it does not: the fit at $x = 0$ is 0.5, half a unit below the reading.",
                                "Zero would mean the line goes through the origin, which is what you would get if the all-ones column had been left out of $A$ altogether.",
                                "$-0.5$ has the sign wrong: $3c = 9 - 7.5$ is $+1.5$, not $-1.5$.",
                            ],
                        },
                        {
                            "prompt": "The middle entry of the residual.",
                            "hole": "?",
                            "opts": ["-1", "1", "-0.5", "2"],
                            "a": 0,
                            "why": "The fit at $x = 1$ is $0.5 + 2.5 = 3.0$, and the reading was 2, so the residual is $2 - 3 = -1$. It is the largest of the three and it is the only negative one, which is what has to happen if the three are to sum to zero.",
                            "whys": [
                                "The fit at $x = 1$ is $0.5 + 2.5 = 3.0$, and the reading was 2, so the residual is $2 - 3 = -1$. It is the largest of the three and it is the only negative one, which is what has to happen if the three are to sum to zero.",
                                "$+1$ is the residual with its sign reversed — fit minus data rather than data minus fit. The convention matters here because the two orthogonality checks are written for $e = b - A\\hat{x}$.",
                                "$-0.5$ is the size of the other two residuals. If all three were $\\pm 0.5$ they could not sum to zero with two of them positive.",
                                "2 is the measured value itself, not what is left after the fit has been subtracted.",
                            ],
                        },
                        {
                            "prompt": "The number under the square root in $\\|e\\|$.",
                            "hole": "?",
                            "opts": ["1.5", "1", "2.25", "0.75"],
                            "a": 0,
                            "why": "$0.5^2 + (-1)^2 + 0.5^2 = 0.25 + 1 + 0.25 = 1.5$, so $\\|e\\| = 1.22$. That sum of squares is the quantity least squares minimises; no other $c$ and $d$ make it smaller, which is exactly what the two zero checks above certify.",
                            "whys": [
                                "$0.5^2 + (-1)^2 + 0.5^2 = 0.25 + 1 + 0.25 = 1.5$, so $\\|e\\| = 1.22$. That sum of squares is the quantity least squares minimises; no other $c$ and $d$ make it smaller, which is exactly what the two zero checks above certify.",
                                "1 is the square of the middle residual on its own. The other two are small but not zero, and they contribute a quarter each.",
                                "2.25 is $(0.5 + 1 + 0.5)^2$ — the residuals added first and squared afterwards. Squaring is what makes signs irrelevant, so it has to happen to each one before they are added; done the other way, the $-1$ would partly cancel the two positives.",
                                "0.75 leaves the middle residual out and counts something else twice. Every entry of $e$ appears exactly once in the sum.",
                            ],
                        },
                    ],
                },
                {
                    "title": "Gram–Schmidt on two columns",
                    "minutes": 8,
                    "caption": "the same two columns, made perpendicular",
                    "lang": "text",
                    "brief": r'''
The same two shapes as the previous drill, orthogonalised. Each new vector keeps only the
part of itself that the vectors already accepted could not reach.

Watch the two places a $\sqrt{3}$ could go and only one of them is right. $q_1$ is the
*normalised* first column, so the coefficient $q_1^\top a_2$ multiplies $q_1$ and not
$a_1$ — and the two normalisations then cancel.
''',
                    "listing": """a1 = ( 1, 1, 1 )                a2 = ( 0, 1, 2 )

step 1   normalise the first
         |a1| = sqrt(1 + 1 + 1) = sqrt(3)
         q1   = ( 1, 1, 1 ) / sqrt(3)

step 2   how much of a2 lies along q1
         q1' a2 = ( 0 + 1 + 2 ) / sqrt(3) = ___

step 3   subtract that much off
         (q1' a2) q1 =  ___ * ( 1, 1, 1 )

         w = a2 - (q1' a2) q1 = ( ___ , 0, 1 )

step 4   normalise what is left
         |w| = ___
         q2  = ( -1, 0, 1 ) / |w|

check    q1' q2 = ___
""",
                    "blanks": [
                        {
                            "prompt": "The coefficient $q_1^\\top a_2$.",
                            "hole": "?",
                            "opts": ["$\\sqrt{3}$", "3", "$3/2$", "1"],
                            "a": 0,
                            "why": "$3/\\sqrt{3} = \\sqrt{3} \\approx 1.732$. Rationalising a fraction like this one is worth doing immediately rather than at the end, because the $\\sqrt{3}$ is about to meet the $1/\\sqrt{3}$ inside $q_1$ and cancel with it.",
                            "whys": [
                                "$3/\\sqrt{3} = \\sqrt{3} \\approx 1.732$. Rationalising a fraction like this one is worth doing immediately rather than at the end, because the $\\sqrt{3}$ is about to meet the $1/\\sqrt{3}$ inside $q_1$ and cancel with it.",
                                "3 is $a_1^\\top a_2$, the inner product with the *unnormalised* first column. Dividing it by $\\|a_1\\| = \\sqrt{3}$ is the whole difference between $a_1$ and $q_1$.",
                                "$3/2$ divides by 2 rather than by $\\sqrt{3}$ — a length of 2 would belong to a vector like $(1,1,1,1)$, not to this one.",
                                "1 is the number of copies of $(1,1,1)$ that get subtracted at the next step, which is a different quantity: it is this coefficient multiplied by the $1/\\sqrt{3}$ that sits inside $q_1$.",
                            ],
                        },
                        {
                            "prompt": "How many copies of $(1,1,1)$ get subtracted.",
                            "hole": "?",
                            "opts": ["1", "$\\sqrt{3}$", "3", "$1/\\sqrt{3}$"],
                            "a": 0,
                            "why": "$(q_1^\\top a_2)\\,q_1 = \\sqrt{3} \\times (1,1,1)/\\sqrt{3} = 1 \\times (1,1,1)$. The two square roots cancel, and what is subtracted is the mean of $(0,1,2)$ at every position — which is what makes this step identical to centring the $x$ values.",
                            "whys": [
                                "$(q_1^\\top a_2)\\,q_1 = \\sqrt{3} \\times (1,1,1)/\\sqrt{3} = 1 \\times (1,1,1)$. The two square roots cancel, and what is subtracted is the mean of $(0,1,2)$ at every position — which is what makes this step identical to centring the $x$ values.",
                                "$\\sqrt{3}$ is the coefficient that multiplies $q_1$, not the one that multiplies $(1,1,1)$. Using it here normalises once and forgets to normalise the second time, which overstates the subtraction by a factor of $\\sqrt{3}$.",
                                "3 normalises neither time. It would subtract $(3,3,3)$ from $(0,1,2)$ and leave $(-3,-2,-1)$, which is not perpendicular to $(1,1,1)$ at all — its inner product is $-6$.",
                                "$1/\\sqrt{3}$ has the normalisation upside down. A quick test: whatever is subtracted must leave something perpendicular to $(1,1,1)$, so its entries must sum to $0 + 1 + 2 = 3$ spread equally — one each.",
                            ],
                        },
                        {
                            "prompt": "The first entry of $w$.",
                            "hole": "?",
                            "opts": ["-1", "1", "0", "-2"],
                            "a": 0,
                            "why": "$0 - 1 = -1$, and the other two are $1 - 1 = 0$ and $2 - 1 = 1$. The whole vector is $(-1, 0, 1)$, whose entries sum to zero — the visible sign that it is perpendicular to $(1,1,1)$.",
                            "whys": [
                                "$0 - 1 = -1$, and the other two are $1 - 1 = 0$ and $2 - 1 = 1$. The whole vector is $(-1, 0, 1)$, whose entries sum to zero — the visible sign that it is perpendicular to $(1,1,1)$.",
                                "$+1$ is the third entry, not the first. $a_2$ runs $0, 1, 2$ and one is taken off each, so the result runs $-1, 0, 1$.",
                                "0 is the middle entry. If the first entry were also zero the vector would sum to 1 rather than 0, and it would not be perpendicular to the all-ones column.",
                                "$-2$ would come from subtracting two copies of $(1,1,1)$. One is what the previous step produced.",
                            ],
                        },
                        {
                            "prompt": "The length of $w$.",
                            "hole": "?",
                            "opts": ["$\\sqrt{2}$", "2", "$\\sqrt{3}$", "1"],
                            "a": 0,
                            "why": "$\\sqrt{(-1)^2 + 0^2 + 1^2} = \\sqrt{2} \\approx 1.414$. That number is the second diagonal entry of $R$ in the factorisation $A = QR$, so it is not thrown away: it is what the back-substitution divides by.",
                            "whys": [
                                "$\\sqrt{(-1)^2 + 0^2 + 1^2} = \\sqrt{2} \\approx 1.414$. That number is the second diagonal entry of $R$ in the factorisation $A = QR$, so it is not thrown away: it is what the back-substitution divides by.",
                                "2 is the sum of the squares before the square root. It is $\\|w\\|^2$, and it is the thing you divide by when projecting onto $w$ directly rather than normalising first.",
                                "$\\sqrt{3}$ was the length of $a_1$. The vector left after the subtraction is shorter than $a_2$ was and has nothing to do with $a_1$'s length.",
                                "1 would say $w$ is already a unit vector and needs no scaling. Its two non-zero entries are each of size 1, so its length is larger than either.",
                            ],
                        },
                        {
                            "prompt": "The check $q_1^\\top q_2$.",
                            "hole": "?",
                            "opts": ["0", "1", "$1/\\sqrt{6}$", "$-1/\\sqrt{6}$"],
                            "a": 0,
                            "why": "$(-1 + 0 + 1)/\\sqrt{6} = 0$. It could not have come out otherwise: $w$ was built by removing everything that lay along $q_1$, so what remains has no component there. Running this check anyway is cheap and it is how you find out that a subtraction went in with the wrong sign.",
                            "whys": [
                                "$(-1 + 0 + 1)/\\sqrt{6} = 0$. It could not have come out otherwise: $w$ was built by removing everything that lay along $q_1$, so what remains has no component there. Running this check anyway is cheap and it is how you find out that a subtraction went in with the wrong sign.",
                                "1 is what $q_1^\\top q_1$ gives — each vector has unit length, so dotted with itself it returns 1. Dotted with the other one it must return 0, and those two facts together are the definition of orthonormal.",
                                "$1/\\sqrt{6}$ is the product of the two normalising constants, $1/\\sqrt{3}$ times $1/\\sqrt{2}$. It multiplies the bracket $(-1 + 0 + 1)$, and that bracket is zero, so the constant never gets a chance to matter.",
                                "A negative value is no better than a positive one here. Any non-zero answer would mean the subtraction in step 3 had removed the wrong amount.",
                            ],
                        },
                    ],
                },
            ],
            "numeric": [
                {
                    "title": "A resistance out of four readings",
                    "minutes": 5,
                    "brief": r'''
The mechanical rung: one shape, one unknown, one formula.

A resistor is driven by a current source and the voltage across it read four times. Ohm's
law has no constant term, so the model is $V = RI$ — a line forced through the origin.
That makes the vector of currents the single shape $a$, the vector of voltages the
measurement $b$, and $R$ the coefficient $\hat{x} = a^\top b / a^\top a$.

Four equations, one unknown, and no exact solution: no single $R$ reproduces all four
readings. The projection is the best available substitute.
''',
                    "prompt": "What resistance does the least-squares fit through the origin give?",
                    "note": "Work in milliamps and volts, so the answer comes out in kilohms. Give it to three decimal places.",
                    "figure": r'''
Four readings from one resistor, taken with a current source and a voltmeter:

```
    I (mA)    0.50    1.50    2.50    3.50
    V (V)     1.10    3.20    5.10    7.30
```

so $a = (0.50,\ 1.50,\ 2.50,\ 3.50)$ mA and $b = (1.10,\ 3.20,\ 5.10,\ 7.30)$ V.
''',
                    "given": [
                        {"label": "Model", "value": "$V = RI$, no offset term"},
                        {"label": "Shape $a$", "value": "the four currents, in mA"},
                        {"label": "Measurement $b$", "value": "the four voltages, in V"},
                        {"label": "Rule", "value": "$\\hat{x} = \\dfrac{a^\\top b}{a^\\top a}$"},
                    ],
                    "aside": "The units carry themselves: $a^\\top b$ is in V·mA and $a^\\top a$ in mA², so the "
                             "quotient is V/mA, which is kΩ. Staying in milliamps and volts throughout means no "
                             "conversion anywhere.",
                    "answer": 2.079,
                    "tol": 0.004,
                    "unit": "kΩ",
                    "hint": "$a^\\top b = 0.50(1.10) + 1.50(3.20) + 2.50(5.10) + 3.50(7.30)$ and "
                            "$a^\\top a = 0.25 + 2.25 + 6.25 + 12.25$.",
                    "wrong": "2.088 kΩ is total voltage over total current, $16.70/8.00$. That is what you get by "
                             "adding the columns instead of projecting, and it counts a reading taken at 0.5 mA "
                             "as heavily as one taken at 3.5 mA. 2.115 kΩ is the average of the four separate "
                             "ratios $V/I$, which is worse still: it counts the *small* currents most, because "
                             "a fixed voltage error divided by a small current looks like an enormous "
                             "resistance error.",
                    "why": r'''
```
a'b = 0.50(1.10) + 1.50(3.20) + 2.50(5.10) + 3.50(7.30)
    = 0.55 + 4.80 + 12.75 + 25.55                        = 43.65   V*mA

a'a = 0.50^2 + 1.50^2 + 2.50^2 + 3.50^2
    = 0.25 + 2.25 + 6.25 + 12.25                         = 21.00   mA^2

R = 43.65 / 21.00                                        = 2.0786  kohm
```

The fitted voltages and what is left over:

```
p = R a = ( 1.0393, 3.1179, 5.1964, 7.2750 ) V
e = b - p = ( 0.0607, 0.0821, -0.0964, 0.0250 ) V
```

Now the check, which is the only thing that certifies the answer:

```
a'e = 0.50(0.0607) + 1.50(0.0821) + 2.50(-0.0964) + 3.50(0.0250)
    = 0.0304 + 0.1232 - 0.2411 + 0.0875                  = 0.0000
```

Zero, so the residual is perpendicular to the current vector and no other $R$ fits better.

One detail here is worth more than the answer. The residuals do **not** sum to zero — they
add to $+0.071$ V. That is not a mistake. Residuals summing to zero is what you get when
the all-ones column is one of the shapes, and here it is not: the model was forced through
the origin, so the only thing guaranteed to vanish is the *current-weighted* sum
$a^\top e$. Fit an offset as well and both sums vanish, because then there are two shapes
and two right angles to satisfy. Which quantities come out orthogonal to the residual is
decided entirely by which columns you put in $A$.

And the reason the plain ratio $\sum V/\sum I$ is a different number: least squares
through the origin weights each reading by its current. Written out,
$\hat{x} = \sum I_kV_k / \sum I_k^2$ is a weighted average of the individual ratios
$V_k/I_k$ with weights $I_k^2$. The 3.5 mA reading carries 49 times the weight of the
0.5 mA one — which is right, because the same 10 mV of meter error is a 20 Ω error at
0.5 mA and a 3 Ω error at 3.5 mA.
''',
                },
                {
                    "title": "How far outside the circuit's reach is this reading?",
                    "minutes": 7,
                    "brief": r'''
A step up: same one shape, but the quantity asked for is the *leftover* rather than the
coefficient.

A network is driven by a single source. Linearity then fixes the ratios between its node
voltages once and for all: turn the source up and every node scales together, so the whole
vector of node voltages is always some multiple of one fixed pattern. For this network that
pattern is $2 : 3 : 6$.

A meter says otherwise. Something is wrong — a resistor out of tolerance, a probe on the
wrong pad, a soldering fault. Before working out what, it is worth knowing how far the
reading is from anything the circuit could have produced, because a small distance means a
noisy meter and a large one means a different circuit.
''',
                    "prompt": "How far is the measured vector from the closest set of node voltages this network can produce?",
                    "note": "That is the length of the residual, in volts. Give it to three decimal places.",
                    "figure": r'''
The pattern the network can produce, for any setting of its one source:

$$a = (2,\ 3,\ 6) \qquad\text{so the node voltages are always}\ x\,(2, 3, 6)\ \text{volts}$$

What the meter read at the three nodes:

$$b = (2.20,\ 3.00,\ 7.20)\ \text{V}$$

No value of $x$ produces that. The question is how far away from it the nearest one is.
''',
                    "given": [
                        {"label": "Reachable set", "value": "every multiple of $a = (2, 3, 6)$"},
                        {"label": "Measured", "value": "$b = (2.20, 3.00, 7.20)$ V"},
                        {"label": "Closest point", "value": "$p = \\hat{x}a$ with $\\hat{x} = a^\\top b/a^\\top a$"},
                        {"label": "Wanted", "value": "$\\|b - p\\|$, in volts"},
                    ],
                    "aside": "$\\|e\\|^2 = \\|b\\|^2 - (a^\\top b)^2/a^\\top a$ is Pythagoras on the right "
                             "triangle whose legs are $p$ and $e$. It is one subtraction instead of squaring "
                             "three residuals, and computing it both ways is a free check.",
                    "answer": 0.549,
                    "tol": 0.005,
                    "unit": "V",
                    "hint": "$a^\\top b = 4.40 + 9.00 + 43.20$ and $a^\\top a = 4 + 9 + 36 = 49$. Then either "
                            "form the three residuals and take the root of their squares, or use the "
                            "Pythagoras shortcut.",
                    "wrong": "0.632 V comes from scaling the pattern so that the *third* node matches exactly — "
                             "$x = 7.20/6 = 1.2$ — which forces one residual to zero and makes the other two "
                             "carry everything. 0.671 V is the same mistake made on the first node, or "
                             "equivalently the average of the three ratios $b_i/a_i$. Both are legitimate "
                             "estimates of $x$; neither is the closest point, which is what was asked. And "
                             "0.301 V is $\\|e\\|^2$ with the square root forgotten.",
                    "why": r'''
```
a'b = 2(2.20) + 3(3.00) + 6(7.20)
    = 4.40 + 9.00 + 43.20                    = 56.60
a'a = 4 + 9 + 36                             = 49.00

x^  = 56.60 / 49.00                          = 1.15510

p   = x^ a = ( 2.31020, 3.46531, 6.93061 ) V
e   = b - p = ( -0.11020, -0.46531, 0.26939 ) V
```

Direct, then by the shortcut, and the two must agree:

```
direct: square each residual and add

        0.11020^2 = 0.012145
        0.46531^2 = 0.216510
        0.26939^2 = 0.072570
                                             = 0.301225
|e| = sqrt(0.301225)                         = 0.5488 V

shortcut
        |b|^2 = 2.20^2 + 3.00^2 + 7.20^2
              = 4.84 + 9.00 + 51.84          = 65.68
        (a'b)^2 / a'a = 56.60^2 / 49.00
              = 3203.56 / 49.00              = 65.3788
        |e|^2 = 65.68 - 65.3788              = 0.3012
```

Same number. And the orthogonality check:

```
a'e = 2(-0.11020) + 3(-0.46531) + 6(0.26939)
    = -0.22041 - 1.39592 + 1.61633           = 0.00000
```

Now read the residual rather than just its length. The three entries are $-0.110$, $-0.465$
and $+0.269$ V: the middle node is far the worst, and it is low while the third is high.
That is a shape, not noise — a genuinely noisy meter would scatter the three about equally.
Somewhere between the second and third nodes, the network is not the network you drew.

The reason the "match one node exactly" shortcuts land close but not closest is worth
knowing, because it decides what a residual can and cannot detect. Near its minimum the
squared distance is a quadratic with zero slope, so a scale factor 4% away from $\hat{x}$
costs only a fraction of a percent in $\|e\|$. Getting $\hat{x}$ slightly wrong barely
moves the residual; the residual is a sensitive instrument for detecting a wrong *model*
and a blunt one for detecting a slightly wrong *coefficient*.
''',
                },
                {
                    "title": "Three supplies, one node, and the average they settle on",
                    "minutes": 8,
                    "brief": r'''
Now a circuit that performs a projection without being asked.

Three supplies, each reaching the same node through its own resistor, and no other path
from that node to anywhere. Each supply is trying to hold the node at its own voltage and
none of them can. What the node settles at is the single value that comes closest to all
three — but "closest" is weighted, because a supply behind 1 kΩ pushes harder than one
behind 3 kΩ.

Write KCL at the node and you will find you have written the normal equation. The shape is
the all-ones column, the measurement is the vector of supply voltages, and the weights are
the conductances.
''',
                    "prompt": "What voltage does the probed node settle at?",
                    "note": "Give the answer in volts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 14, "rot": 1, "value": 6},
                            {"id": "v2", "kind": "V", "x": 8, "y": 14, "rot": 1, "value": 9},
                            {"id": "v3", "kind": "V", "x": 13, "y": 14, "rot": 1, "value": 3},
                            {"id": "g1", "kind": "GND", "x": 3, "y": 17},
                            {"id": "g2", "kind": "GND", "x": 8, "y": 17},
                            {"id": "g3", "kind": "GND", "x": 13, "y": 17},
                            {"id": "r1", "kind": "R", "x": 3, "y": 10, "rot": 1, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 8, "y": 10, "rot": 1, "value": 2000},
                            {"id": "r3", "kind": "R", "x": 13, "y": 10, "rot": 1, "value": 3000},
                            {"id": "out", "kind": "OUT", "x": 16, "y": 9},
                        ],
                        "wires": [
                            {"a": [3, 15], "b": [3, 17]},
                            {"a": [8, 15], "b": [8, 17]},
                            {"a": [13, 15], "b": [13, 17]},
                            {"a": [3, 13], "b": [3, 11]},
                            {"a": [8, 13], "b": [8, 11]},
                            {"a": [13, 13], "b": [13, 11]},
                            {"a": [3, 9], "b": [13, 9]},
                            {"a": [13, 9], "b": [16, 9]},
                        ],
                    },
                    "given": [
                        {"label": "Left branch", "value": "6.00 V behind 1.00 kΩ"},
                        {"label": "Middle branch", "value": "9.00 V behind 2.00 kΩ"},
                        {"label": "Right branch", "value": "3.00 V behind 3.00 kΩ"},
                        {"label": "Other paths from the node", "value": "none — the three branches are all of it"},
                    ],
                    "aside": "In millisiemens the three weights are $1$, $0.5$ and $1/3$. Keeping conductances "
                             "in mS and voltages in V puts the currents in mA, and the answer stays in volts.",
                    "check": r'''
const rs = c.net.parts.filter(function (p) { return p.kind === 'R'; });
c.assert(rs.length === 3, 'this question is about three branches; the drawing has ' + rs.length);
return c.vout();
''',
                    "answer": 6.27,
                    "tol": 0.02,
                    "unit": "V",
                    "hint": "KCL at the node: $(6-v)/1\\mathrm{k} + (9-v)/2\\mathrm{k} + (3-v)/3\\mathrm{k} = 0$. "
                            "Gather the $v$ terms and it reads $v\\sum g_k = \\sum g_kV_k$.",
                    "wrong": "6.00 V is the plain average of 6, 9 and 3 — the answer only if all three resistors "
                             "were equal. 5.50 V is $(6(1) + 9(2) + 3(3))/(1+2+3)$: the *resistances* used as "
                             "weights instead of the conductances, which gets the direction of the dependence "
                             "backwards. A bigger resistor means a weaker pull, so the weight has to fall as "
                             "$R$ rises. 7.00 V is what is left if the 3 V branch is dropped altogether.",
                    "why": r'''
```
conductances    g1 = 1/1k   = 1.0000 mS
                g2 = 1/2k   = 0.5000 mS
                g3 = 1/3k   = 0.3333 mS
                sum         = 1.8333 mS      ( = 11/6 )

weighted sum    g1 V1 + g2 V2 + g3 V3
              = 1.0(6) + 0.5(9) + (1/3)(3)
              = 6.0 + 4.5 + 1.0             = 11.5 mA

v = 11.5 / 1.8333                           = 6.2727 V   ( = 69/11 )
```

Confirm it with KCL, which is the only thing that makes it true:

```
(6.00 - 6.2727)/1k  = -0.2727 mA
(9.00 - 6.2727)/2k  = +1.3636 mA
(3.00 - 6.2727)/3k  = -1.0909 mA
                      ---------
                        0.0000 mA
```

Now look at what that sum *is*. Each term is $g_k(V_k - v)$: a weight times a residual.
KCL says $\sum_k g_k(V_k - v) = 0$, and that is exactly the weighted normal equation
$a^\top W(b - va) = 0$ with $a$ the all-ones column, $b = (6, 9, 3)$ and
$W = \mathrm{diag}(g_1, g_2, g_3)$. The node voltage is the weighted least-squares fit of a
single constant to the three supply voltages, and the branch currents are the weighted
residuals. A circuit does not know any of this; it simply cannot do anything else.

Two things follow that are worth carrying away.

The weights are conductances, so the branch with the *smallest* resistor has the loudest
vote. Here the plain average is 6.00 V and the weighted one is 6.27 V. The 6 V supply has
the heaviest weight and the 9 V supply the second heaviest, while the 3 V supply — the one
that would pull the answer down hardest — is behind the largest resistor and is discounted
to a third of the first branch's say. Down-weighting the low reading raises the answer.

And the currents are the residuals. The 9 V branch, furthest above the settled value,
delivers the most: 1.36 mA. The 3 V branch is 3.27 V *below* the node, so its current is
negative — it is absorbing 1.09 mA, being charged by the other two. A branch whose supply
happens to sit at the answer would carry no current at all. That is the physical reading of
a zero residual, and it is why this circuit is a fair picture of a projection rather than
an analogy for one.
''',
                },
                {
                    "title": "Where the fitted line says the cell gives up",
                    "minutes": 10,
                    "brief": r'''
Two shapes now, so a $2\times2$ normal system, and the quantity asked for is neither
coefficient.

A cell is loaded at five currents and its terminal voltage recorded. The model is the
usual one, an ideal EMF behind a series resistance:

$$V = E - R\,I$$

which is linear in $E$ and $R$, so it fits with two columns: the all-ones column carrying
$E$, and the column of currents carrying $-R$. Fit both, then ask the fitted line a
question neither coefficient answers on its own — at what current does it reach zero?

Work the currents in **amps**, not milliamps, so the slope comes out in ohms.
''',
                    "prompt": "According to the fit, at what current does the terminal voltage fall to zero?",
                    "note": "Give the answer in amps, to three significant figures.",
                    "figure": r'''
Five measurements on one cell:

```
    I (mA)    0      100     200     300     400
    V (V)     9.02   8.79    8.62    8.39    8.18
```

In amps, the two columns of $A$ are $(1,1,1,1,1)$ and $(0,\ 0.1,\ 0.2,\ 0.3,\ 0.4)$, and
$b$ is the voltage column. The fitted line is $V = E + mI$, with $m$ negative; the
short-circuit current the model predicts is $I_{\mathrm{sc}} = E/(-m)$.
''',
                    "given": [
                        {"label": "Model", "value": "$V = E - RI$, two unknowns"},
                        {"label": "Columns of $A$", "value": "ones, and the currents in amps"},
                        {"label": "Normal equations", "value": "$A^\\top A\\,\\hat{x} = A^\\top b$"},
                        {"label": "Wanted", "value": "$E/R$, in amps"},
                    ],
                    "aside": "$A^\\top A$ is $\\begin{bmatrix} n & \\sum I \\\\ \\sum I & \\sum I^2\\end{bmatrix}$ "
                             "and $A^\\top b$ is $(\\sum V,\\ \\sum IV)$. Five sums, and the $2\\times2$ system "
                             "is written.",
                    "answer": 4.33,
                    "tol": 0.02,
                    "unit": "A",
                    "hint": "$\\sum I = 1.00$, $\\sum I^2 = 0.30$, $\\sum V = 43.00$, $\\sum IV = 8.392$. The "
                            "determinant of $A^\\top A$ is $5(0.30) - 1.00^2 = 0.50$.",
                    "wrong": "4.30 A is the line through the first and last readings only: slope $-2.10$ Ω, "
                             "intercept 9.02 V, and $9.02/2.10 = 4.30$ A. It is a reasonable estimate that "
                             "throws away three measurements and lets the two noisiest points set the whole "
                             "answer. 4335 is the same correct answer left in milliamps. And 2.08 is the "
                             "fitted resistance in ohms rather than the current.",
                    "why": r'''
```
n = 5      sum I  = 0 + 0.1 + 0.2 + 0.3 + 0.4               = 1.000  A
           sum I^2 = 0 + 0.01 + 0.04 + 0.09 + 0.16          = 0.300  A^2
           sum V  = 9.02+8.79+8.62+8.39+8.18                = 43.000 V
           sum IV = 0 + 0.879 + 1.724 + 2.517 + 3.272       = 8.392  V*A

A'A = [ 5.00   1.00 ]        A'b = [ 43.000 ]
      [ 1.00   0.30 ]              [  8.392 ]

det = 5.00(0.30) - 1.00(1.00) = 1.50 - 1.00                 = 0.500

E = ( 43.000(0.30) - 1.00(8.392) ) / 0.500
  = ( 12.900 - 8.392 ) / 0.500 = 4.508 / 0.500              = 9.016 V

m = ( 5.00(8.392) - 1.00(43.000) ) / 0.500
  = ( 41.960 - 43.000 ) / 0.500 = -1.040 / 0.500            = -2.080 V/A

R = 2.080 ohm

I_sc = E / R = 9.016 / 2.080                                = 4.335 A
```

Both orthogonality checks, one per column:

```
fit    = ( 9.016, 8.808, 8.600, 8.392, 8.184 ) V
e      = ( 0.004, -0.018, 0.020, -0.002, -0.004 ) V

ones' e = 0.004 - 0.018 + 0.020 - 0.002 - 0.004             = 0.000
I'    e = 0.1(-0.018) + 0.2(0.020) + 0.3(-0.002) + 0.4(-0.004)
        = -0.0018 + 0.0040 - 0.0006 - 0.0016                = 0.0000
```

Both vanish, so the fit is finished: there is no leftover offset and no leftover trend
against current. $\|e\| = 0.028$ V, which is about what a three-and-a-half digit meter
would give you, so the straight-line model is doing well over the range it was fed.

Over the range it was fed. The answer to the question actually asked is 4.33 A, and the
honest sentence to attach to it is that the fit says so and the cell almost certainly does
not. Every measurement was taken below 0.4 A and the answer sits at ten times the largest
of them. A real cell's internal resistance is not a constant out there — it rises as the
current does, the terminal voltage collapses faster than the line predicts, and the true
short-circuit current is lower. That is not a defect in least squares. Least squares
answered exactly the question it was given, which was "where does this straight line cross
zero", and the straight line was your idea. The projection has no opinion about the range
over which the model is true, and it will never develop one.
''',
                },
                {
                    "title": "The power a loaded summing node settles on",
                    "minutes": 12,
                    "brief": r'''
The hardest rung: the same three branches as before, with one resistor added, and the
quantity asked for is not a voltage at all.

The load resistor changes the problem in a way worth naming before you solve it. It is a
fourth branch, and its far end is at 0 V — so as far as the algebra is concerned it is a
fourth *measurement*, one that reads zero, with weight $g_L = 1/R_L$. Adding it pulls the
fitted constant towards zero by an amount that depends on how heavy that weight is. A
statistician would call that regularisation; an engineer calls it loading. They are the
same arithmetic.

Then the quantity. Each resistor dissipates $(\Delta V)^2/R$, that is $g$ times the square
of its residual, so the total heat is $\sum_k g_k(V_k - v)^2 + g_Lv^2$ — precisely the
weighted sum of squares that the projection minimises. The node settles where the circuit
runs coolest, and it does so without being told to.
''',
                    "prompt": "What is the total power dissipated in all four resistors?",
                    "note": "Give the answer in milliwatts, to two decimal places.",
                    "diagram": {
                        "parts": [
                            {"id": "v1", "kind": "V", "x": 3, "y": 14, "rot": 1, "value": 6},
                            {"id": "v2", "kind": "V", "x": 8, "y": 14, "rot": 1, "value": 9},
                            {"id": "v3", "kind": "V", "x": 13, "y": 14, "rot": 1, "value": 3},
                            {"id": "g1", "kind": "GND", "x": 3, "y": 17},
                            {"id": "g2", "kind": "GND", "x": 8, "y": 17},
                            {"id": "g3", "kind": "GND", "x": 13, "y": 17},
                            {"id": "r1", "kind": "R", "x": 3, "y": 10, "rot": 1, "value": 1000},
                            {"id": "r2", "kind": "R", "x": 8, "y": 10, "rot": 1, "value": 2000},
                            {"id": "r3", "kind": "R", "x": 13, "y": 10, "rot": 1, "value": 3000},
                            {"id": "out", "kind": "OUT", "x": 16, "y": 9},
                            {"id": "rl", "kind": "R", "x": 16, "y": 12, "rot": 1, "value": 4000},
                            {"id": "g4", "kind": "GND", "x": 16, "y": 16},
                        ],
                        "wires": [
                            {"a": [3, 15], "b": [3, 17]},
                            {"a": [8, 15], "b": [8, 17]},
                            {"a": [13, 15], "b": [13, 17]},
                            {"a": [3, 13], "b": [3, 11]},
                            {"a": [8, 13], "b": [8, 11]},
                            {"a": [13, 13], "b": [13, 11]},
                            {"a": [3, 9], "b": [13, 9]},
                            {"a": [13, 9], "b": [16, 9]},
                            {"a": [16, 9], "b": [16, 11]},
                            {"a": [16, 13], "b": [16, 16]},
                        ],
                    },
                    "given": [
                        {"label": "Left branch", "value": "6.00 V behind 1.00 kΩ"},
                        {"label": "Middle branch", "value": "9.00 V behind 2.00 kΩ"},
                        {"label": "Right branch", "value": "3.00 V behind 3.00 kΩ"},
                        {"label": "Load", "value": "4.00 kΩ from the probed node to ground"},
                        {"label": "Wanted", "value": "the heat in all four resistors together"},
                    ],
                    "aside": "The load's weight is $g_L = 0.25$ mS, which joins the other three in the "
                             "denominator but contributes nothing to the numerator, because the voltage it is "
                             "pulling towards is zero.",
                    "check": r'''
const d = c.dc();
const rs = c.net.parts.filter(function (p) { return p.kind === 'R'; });
c.assert(rs.length === 4, 'this question adds up four resistors; the drawing has ' + rs.length);
let p = 0;
rs.forEach(function (r) {
  const dv = d.v[r.n1] - d.v[r.n2];
  p += dv * dv / r.value;
});
return p * 1000;
''',
                    "answer": 16.02,
                    "tol": 0.05,
                    "unit": "mW",
                    "hint": "The node voltage is $\\sum g_kV_k$ over $\\sum g_k + g_L$: the numerator is the "
                            "same 11.5 mA as before, and the denominator gains 0.25 mS. Then add up "
                            "$(\\Delta V)^2/R$ across each of the four resistors.",
                    "wrong": "17.20 mW is the answer with the unloaded node voltage of 6.27 V kept and the "
                             "load's dissipation simply added on top. The load does not just dissipate; it "
                             "moves the node, and holding the node where it used to be would cost 1.18 mW of "
                             "extra heat that the circuit refuses to produce. 7.62 mW is the load on its own. "
                             "And 8.40 mW is the three source branches without the load's own share.",
                    "why": r'''
First the node, with the load's conductance in the denominator and nothing in the
numerator:

```
sum g  = 1.0000 + 0.5000 + 0.3333 = 1.8333 mS
g_L    = 1/4k                     = 0.2500 mS
total                             = 2.0833 mS   ( = 25/12 )

numerator, unchanged              = 11.5 mA

v = 11.5 / 2.0833                 = 5.5200 V
```

The unloaded node sat at 6.27 V. Adding a 4 kΩ path to ground has dragged it 0.75 V
towards zero, and the size of the drag is set by how $g_L$ compares with the other three
weights: 0.25 against 1.83, so the estimate shrinks by about an eighth.

Now the four heats:

```
1 kohm   (6.00 - 5.52) =  0.48 V    0.48^2/1000  = 0.2304 mW
2 kohm   (9.00 - 5.52) =  3.48 V    3.48^2/2000  = 6.0552 mW
3 kohm   (3.00 - 5.52) = -2.52 V    2.52^2/3000  = 2.1168 mW
4 kohm   (5.52 - 0.00) =  5.52 V    5.52^2/4000  = 7.6176 mW
                                                   ---------
                                                   16.0200 mW
```

Two independent checks are available and both are worth taking.

**The sources.** Branch currents are $0.48$, $1.74$ and $-0.84$ mA, and the load draws
$5.52/4\mathrm{k} = 1.38$ mA — which balances, since $0.48 + 1.74 - 0.84 = 1.38$. The power
each source *delivers* is its current times its voltage: $6(0.48) = 2.88$ mW,
$9(1.74) = 15.66$ mW and $3(-0.84) = -2.52$ mW, the last one negative because that supply
is being charged. Total delivered: $2.88 + 15.66 - 2.52 = 16.02$ mW, exactly the heat in
the resistors. Nothing is stored anywhere at DC, so it had to.

**The minimisation.** The total heat as a function of the node voltage is

$$P(v) = \sum_k g_k(V_k - v)^2 + g_Lv^2$$

a quadratic in $v$ opening upwards, whose derivative set to zero gives back exactly the
weighted normal equation. Its second derivative is $2G$, where $G = 2.0833$ mS is the
total conductance at the node including the load, so around the settled value $\hat{v}$

$$P(v) = P(\hat{v}) + G\,(v - \hat{v})^2$$

Move the node 0.10 V either way and the heat rises by
$2.0833\,\mathrm{mS} \times (0.10)^2 = 0.021$ mW, to 16.04 mW. Move it all the way back to
the unloaded 6.2727 V — a displacement of 0.7527 V — and it rises by
$2.0833 \times 0.7527^2 = 1.18$ mW, giving the 17.20 mW named above. The circuit sits at
the bottom of that parabola, and this is the minimum-heat principle: among all voltages
you could impose on the free node, the one the circuit adopts by itself is the one that
dissipates least. (There is a dual version, due to Thomson, that minimises over current
distributions instead.) A resistive network's DC solution is not merely *described* by a
least-squares problem — it is one.

One caution about the quadratic. Because it is flat at the bottom, a 2% error in the node
voltage — 0.11 V here — raises the power by only 0.025 mW, which is 0.16%. A power
measurement is a poor instrument for finding out whether your node voltage is right.
Measure the voltage.
''',
                },
            ],
            "derive": {
                "title": "The closest point, and the right angle that finds it",
                "minutes": 13,
                "vars": ["x", "p", "q", "m", "a", "b", "c"],
                "brief": r'''
Take a vector $b$ and a line through the origin in the direction $a$. Nothing on the
line is likely to equal $b$, so the question is which point of it comes closest.

To keep the algebra readable, name the three inner products that appear:

$$p = a^\top b, \qquad q = a^\top a, \qquad m = b^\top b$$

All three are ordinary numbers. The answer will be too.
''',
                "steps": [
                    {
                        "prompt": "The candidate is $xa$ for some scalar $x$. Expand the squared distance $\\|b - xa\\|^2 = (b - xa)^\\top(b - xa)$ in terms of $m$, $p$, $q$ and $x$.",
                        "answer": "m - 2 x p + x^2 q",
                        "hint": "Multiply it out as you would $(b-xa)^2$. The cross term appears twice, because $a^\\top b$ and $b^\\top a$ are the same number.",
                        "deconstruct": [
                            "$(b-xa)^\\top(b-xa) = b^\\top b - x\\,a^\\top b - x\\,b^\\top a + x^2 a^\\top a$.",
                            "The two middle terms are equal, so they combine into $-2xp$.",
                            "And the outer two are $m$ and $x^2q$.",
                        ],
                    },
                    {
                        "prompt": "That is a quadratic in one variable. Differentiate with respect to $x$, set the result to zero, and write $x$ in terms of $p$ and $q$.",
                        "answer": "\\frac{p}{q}",
                        "hint": "$\\dfrac{d}{dx}\\left(m - 2xp + x^2q\\right) = -2p + 2xq$.",
                        "deconstruct": [
                            "Setting $-2p + 2xq = 0$ gives $xq = p$.",
                            "And $q = a^\\top a$ is strictly positive unless $a$ is the zero vector, so dividing by it is safe.",
                        ],
                    },
                    {
                        "prompt": "Is that a minimum or a maximum? Write the second derivative of the squared distance with respect to $x$.",
                        "answer": "2q",
                        "hint": "Differentiate $-2p + 2xq$ once more.",
                        "deconstruct": [
                            "The first derivative is $-2p + 2xq$, whose derivative is $2q$.",
                            "$q = a^\\top a = \\|a\\|^2 > 0$, so the curve opens upwards and the stationary point is a minimum.",
                            "That is worth noticing: least squares has no local minima to get stuck in, which is not true of most fitting problems.",
                        ],
                    },
                    {
                        "prompt": "Now the geometry, without any calculus. Write the inner product of the residual with $a$, that is $a^\\top(b - xa)$, in terms of $p$, $q$ and $x$.",
                        "answer": "p - x q",
                        "hint": "$a^\\top b = p$ and $a^\\top(xa) = x\\,a^\\top a = xq$.",
                        "deconstruct": [
                            "$a^\\top(b - xa) = a^\\top b - x\\,a^\\top a$.",
                            "Which is $p - xq$, and it vanishes at exactly the $x$ found above.",
                            "So minimising the distance and making the residual perpendicular to $a$ are the same equation, reached two different ways.",
                        ],
                    },
                    {
                        "prompt": "Use it. Fit $y = cx$ — a line forced through the origin — to the three measurements $(1,2)$, $(2,3)$ and $(3,7)$, so that $a = (1,2,3)$ and $b = (2,3,7)$. Write $c$ as a fraction.",
                        "answer": "\\frac{29}{14}",
                        "hint": "$p = a^\\top b$ and $q = a^\\top a$; work both out and divide.",
                        "deconstruct": [
                            "$p = 1(2) + 2(3) + 3(7) = 2 + 6 + 21 = 29$.",
                            "$q = 1 + 4 + 9 = 14$.",
                            "So $c = p/q$, about 2.07 — steeper than the first two points alone would suggest, because the third point is furthest out and its residual therefore counts most heavily in the sum of squares.",
                        ],
                    },
                ],
                "closing": r'''
Everything in the next module is this, with $A$ in place of $a$. The residual has to be
perpendicular to every column at once, that condition is $A^\top(b - A\hat{x}) = 0$, and
rearranging it gives $A^\top A\hat{x} = A^\top b$.

Notice what has and has not happened. There is no new principle: the same right angle
that solves the one-dimensional problem solves the $n$-dimensional one. What changes is
that "divide by $q$" becomes "solve a small square system", because $A^\top A$ is a
matrix rather than a number — and it is invertible for exactly the same reason $q$ was
non-zero, namely that the columns of $A$ are independent.
''',
            },
            "quiz": {
                "title": "Right angles, and what they are good for",
                "minutes": 8,
                "questions": [
                    {
                        "q": "$a^\\top b = 0$ says that:",
                        "opts": [
                            "$a$ and $b$ are perpendicular",
                            "at least one of $a$ and $b$ is the zero vector",
                            "$a$ and $b$ are parallel",
                            "$a = -b$",
                        ],
                        "a": 0,
                        "why": r'''
$a^\top b = \|a\|\|b\|\cos\theta$, so the product vanishes when the angle is a right
angle — or, trivially, when one vector is zero, which is a special case rather than the
meaning. Parallel vectors give the *largest* possible product for their lengths, not
zero. $a = -b$ gives $-\|a\|^2$, as negative as it can be. In two dimensions $(1,2)$ and
$(2,-1)$ are perpendicular, and neither is zero.
''',
                    },
                    {
                        "q": "The projection of $b$ onto the line through $a$ is $p = \\hat{x}a$. What is $\\hat{x}$?",
                        "opts": [
                            "$\\dfrac{a^\\top b}{b^\\top b}$",
                            "$a^\\top b$",
                            "$\\dfrac{b^\\top b}{a^\\top b}$",
                            "$\\dfrac{a^\\top b}{a^\\top a}$",
                        ],
                        "a": 3,
                        "why": r'''
Two checks settle it without algebra. If $b$ is already perpendicular to $a$ the
projection must be zero, so $a^\top b$ has to sit on *top* — which rules out the version
with it underneath, and that version would divide by zero in exactly the case that
should give the simplest answer. And doubling $a$ must leave the projected point $p$
where it is, so $\hat{x}$ must halve: $a^\top b$ doubles while $a^\top a$ quadruples, and
of the three with $a^\top b$ on top only that pairing halves — a $b^\top b$ underneath
does not depend on $a$ at all, so that version doubles instead. (The fourth halves too,
but it was already ruled out by the perpendicular case.) $a^\top b$ on its own has the
wrong units — it grows with the
length of $a$, which the position of a point on the line cannot.
''',
                    },
                    {
                        "q": "Least squares chooses $\\hat{x}$ so that the residual $b - A\\hat{x}$ is:",
                        "opts": [
                            "zero",
                            "perpendicular to every column of $A$",
                            "as large as possible",
                            "parallel to $b$",
                        ],
                        "a": 1,
                        "why": r'''
If it could be made zero the equation would have an exact solution and none of this
would be needed; the whole subject exists because $b$ lies outside the column space.
Perpendicularity to every column is the condition that $A\hat{x}$ is the *closest* point
of that column space, and writing it down as $A^\top(b - A\hat{x}) = 0$ gives the normal
equations directly. The residual is what is left over after everything reachable has
been taken out, so being parallel to $b$ would mean nothing had been fitted at all.
''',
                    },
                    {
                        "q": "Gram–Schmidt turns an independent set of vectors into an orthonormal one by:",
                        "opts": [
                            "sorting them by length",
                            "discarding the ones that are nearly dependent",
                            "subtracting from each vector its projections onto the ones already accepted, then scaling to unit length",
                            "inverting the matrix whose columns they are",
                        ],
                        "a": 2,
                        "why": r'''
Each new vector keeps only the part of itself that the earlier ones could not reach,
which is by construction perpendicular to all of them. The dividend is that afterwards
every coefficient is a single dot product: with an orthonormal basis there is no system
left to solve. It also detects dependence rather than being defeated by it — a vector
that is a combination of the earlier ones has everything subtracted away, and what
remains is zero to within rounding, which is the signal to stop.
''',
                    },
                    {
                        "q": "$G$ is symmetric. Its nullspace and its column space are:",
                        "opts": [
                            "the same subspace",
                            "orthogonal complements of each other",
                            "unrelated",
                            "both the whole space",
                        ],
                        "a": 1,
                        "why": r'''
The nullspace is always perpendicular to the *row* space — that is just $Gv = 0$ read
one row at a time — and for a symmetric matrix the rows are the columns. So what the map
destroys is at right angles to everything it can produce. In the circuit: the pattern of
node voltages that draws no current is perpendicular to every current distribution the
network can support. For a non-symmetric matrix the two spaces can meet at any angle,
and can even overlap, which is why the symmetric case is worth naming.
''',
                    },
                ],
            },
        },

        # ---- M9 -----------------------------------------------------------
        {
            "title": "Eigenvalues and least squares",
            "summary": "The directions a matrix leaves alone are its poles in disguise; and when there are more measurements than unknowns, the best you can do is minimise what is left over.",
            "concepts": [
                "$Av = \\lambda v$ with $v \\ne 0$ says the map leaves the *direction* of $v$ alone and only stretches it. $\\lambda$ is the eigenvalue and $v$ the eigenvector.",
                "The eigenvalues are the roots of $\\det(A - \\lambda I) = 0$. For a $2\\times2$ matrix that polynomial is $\\lambda^2 - (\\text{trace})\\lambda + \\det$, which is often quicker than expanding.",
                "Write a circuit as $\\dot{x} = Ax$ and the eigenvalues of $A$ are exactly the poles of its transfer function. The same numbers, reached from two directions.",
                "So the stability rule is the same rule: every eigenvalue must have a strictly negative real part. Negative *magnitude* is not the test, and complex eigenvalues are ordinary.",
                "With more measurements than unknowns, $Ac = y$ generally has no solution. **Least squares** picks the $c$ that minimises $\\|Ac - y\\|^2$.",
                "The minimum occurs when the residual is perpendicular to every column of $A$, which is $A^\\top(Ac - y) = 0$, giving the **normal equations** $A^\\top A c = A^\\top y$.",
                "Fitting a polynomial is least squares with $A_{ij} = x_i^j$. Fitting an exponential decay is least squares on $\\ln v$, which turns $Ae^{-t/\\tau}$ into a straight line of slope $-1/\\tau$.",
                "The residuals are the diagnosis. Scatter about zero means noise, and the fit is as good as the data allows. A smooth trend in the residuals means the *model* is wrong, and no amount of extra data will fix it.",
                "An eigenvector is a **natural mode**: a pattern of node voltages and branch currents that decays without changing shape, so that the whole circuit's state is one number times a fixed shape. A general starting condition is a sum of modes, which is why a response is a sum of exponentials.",
                "$A^\\top A$ is symmetric and positive semi-definite, so its eigenvalues are real and non-negative, and they are the *stiffnesses* of the fit: moving the parameter vector a distance $\\delta$ along an eigenvector raises the sum of squares by exactly $\\lambda\\delta^2$. A small eigenvalue names a combination of parameters the data barely constrains.",
            ],
            "read": [
                {
                    "title": "The directions a network does not turn",
                    "minutes": 16,
                    "body": r'''
Two capacitors, a couple of resistors, and nothing driving the circuit. Charge both nodes
up, disconnect the supply, and watch. Both voltages fall towards zero — but not, in
general, in the same way. One node may drop quickly while the other *rises* for a moment,
fed through the resistor that joins them, before the two give up together. Whatever the
voltmeter shows is a mixture of two decaying exponentials, and the rates of those
exponentials are not written on any single component.

Except from certain starting points. Charge the two nodes to *particular* ratios and
something much simpler happens: the pattern shrinks towards zero without changing shape.
The ratio between the two node voltages stays fixed for all time, and the size of the
whole pattern decays as one clean exponential. Those special patterns are the network's
**natural modes**. The rates at which they decay are its **eigenvalues**, and the patterns
themselves are its **eigenvectors**.

Everything in this unit is a consequence of that picture. Including, at the end, the fact
that these numbers are the poles from the first half of this course, arrived at from a
completely different direction.

## A circuit with two modes you can see

Take the most symmetric two-node network there is. Node 1 and node 2 each carry a
capacitor $C$ to ground and a resistor $R$ to ground, and a third resistor, also $R$, joins
the two nodes. Nothing is driving it; the capacitors start with whatever charge you gave
them.

Write KCL at each node. The current out of node 1 is the current into its own resistor
plus the current into the middle resistor, and it all comes out of the capacitor:

$$C\frac{dv_1}{dt} = -\frac{v_1}{R} - \frac{v_1 - v_2}{R}, \qquad
  C\frac{dv_2}{dt} = -\frac{v_2}{R} - \frac{v_2 - v_1}{R}$$

Divide through by $C$ and collect the terms, and the pair becomes one matrix equation:

$$\frac{d}{dt}\begin{bmatrix} v_1 \\ v_2 \end{bmatrix}
 = \frac{1}{RC}\begin{bmatrix} -2 & 1 \\ 1 & -2 \end{bmatrix}
   \begin{bmatrix} v_1 \\ v_2 \end{bmatrix}
 \qquad\text{that is}\qquad \dot{x} = Ax$$

Put $R = 10\ \mathrm{k}\Omega$ and $C = 100$ nF, so $1/RC = 1000\ \mathrm{s^{-1}}$:

```
A = [ -2000   1000 ]   per second
    [  1000  -2000 ]
```

Now guess the two modes from the circuit rather than from the matrix, because here you
can.

**Both nodes at the same voltage.** The middle resistor has the same voltage at each end,
so it carries nothing at all — it might as well not be there. Each capacitor then
discharges through its own resistor alone, at $\tau = RC = 1$ ms. And because both sides
behave identically, the pattern $(1, 1)$ stays $(1,1)$ as it shrinks. So $(1,1)$ is a
mode, with rate $-1/RC = -1000\ \mathrm{s^{-1}}$.

**The nodes equal and opposite.** Take $(v, -v)$. The middle resistor now has $2v$ across
it and carries $2v/R$, on top of the $v/R$ leaving through the node's own resistor. Three
times as much current is leaving a capacitor holding the same charge, so it empties three
times as fast: rate $-3/RC = -3000\ \mathrm{s^{-1}}$, and by symmetry the pattern
$(1,-1)$ again holds its shape.

Check both against the matrix, which is the definition $Av = \lambda v$ doing its job:

```
A (1, 1)  = ( -2000 + 1000,  1000 - 2000 )  = ( -1000, -1000 )  = -1000 (1, 1)
A (1,-1)  = ( -2000 - 1000,  1000 + 2000 )  = ( -3000,  3000 )  = -3000 (1,-1)
```

Two directions the map does not turn. Every other direction it turns, because it stretches
these two by different amounts.

## Worked example: an arbitrary start, taken apart

Suppose you charge node 1 to 8 V and node 2 to 2 V, then let go. That is not a mode. But
it is a *sum* of modes, and finding the mixture is one small piece of algebra:

```
(8, 2) = a (1, 1) + b (1, -1)
         a + b = 8
         a - b = 2      so   a = 5,  b = 3
```

Each piece then decays at its own rate and they never interfere, because each keeps its
own shape:

$$v_1(t) = 5e^{-1000t} + 3e^{-3000t}, \qquad v_2(t) = 5e^{-1000t} - 3e^{-3000t}$$

At $t = 0.5$ ms the two exponentials are $e^{-0.5} = 0.60653$ and $e^{-1.5} = 0.22313$:

```
5 (0.60653) = 3.03265        3 (0.22313) = 0.66939

v1 = 3.03265 + 0.66939  = 3.7020 V
v2 = 3.03265 - 0.66939  = 2.3633 V
```

Notice what has happened by then. The gap between the nodes started at 6 V and is now
$2(0.669) = 1.34$ V: the difference has nearly gone, because the fast mode *is* the
difference and it decays three times as quickly. What is left is the slow mode, the two
nodes drifting down together at $\tau = 1$ ms. That is the general rule, and it is worth
carrying: after a few time constants of the fast mode, whatever remains looks like the
slowest mode alone. The slowest eigenvalue is what "settling time" means.

## Finding the modes when you cannot see them

Symmetry gave the answer that time. Usually there is none. So take the definition
seriously and see what it forces:

$$Av = \lambda v \quad\Longleftrightarrow\quad Av - \lambda v = 0
 \quad\Longleftrightarrow\quad (A - \lambda I)v = 0$$

The $I$ is not decoration — $A - \lambda$ is meaningless, a matrix minus a number, and
$\lambda I$ is what makes the subtraction legal.

Now read the last equation with the previous module in hand. It says the matrix
$A - \lambda I$ sends a **non-zero** vector to zero: it has a non-trivial nullspace. A
square matrix does that exactly when it is singular, and a square matrix is singular
exactly when its determinant vanishes. So:

$$\det(A - \lambda I) = 0$$

That is not a formula to memorise. It is the statement "there is a direction this map
crushes" written in the one notation that can be solved. For our network:

```
det [ -2000 - lam     1000      ]  =  (2000 + lam)^2 - 1000^2  =  0
    [   1000      -2000 - lam ]

(2000 + lam)^2 = 10^6    ->     2000 + lam = +/- 1000

lam = -1000    or    lam = -3000
```

the same two rates, this time without needing to notice anything clever about the circuit.

For a $2\times 2$ matrix the expansion is always the same, so it is worth doing once and
keeping:

$$\det\begin{bmatrix} a - \lambda & b \\ c & d - \lambda\end{bmatrix}
 = (a-\lambda)(d-\lambda) - bc
 = \lambda^2 - (a + d)\lambda + (ad - bc)$$

$$\boxed{\ \lambda^2 - (\operatorname{tr}A)\,\lambda + \det A = 0\ }$$

Two numbers off the matrix and you have the polynomial. It also gives two free checks on
any answer, because the roots of that quadratic sum to the trace and multiply to the
determinant: $-1000 + (-3000) = -4000 = \operatorname{tr}A$, and
$(-1000)(-3000) = 3\times10^6 = \det A$. Both hold.

## Worked example: an RLC, and the poles turning up again

Now a circuit with an inductor, because that is where the connection to the first half of
the course becomes visible. A source drives $L$, then $R$, then $C$ to ground, and the
output is across the capacitor. The state of this circuit is two numbers: the voltage on
the capacitor and the current in the inductor. Everything else follows from those two.

$$C\frac{dv_C}{dt} = i_L, \qquad L\frac{di_L}{dt} = v_{in} - Ri_L - v_C$$

The first is the capacitor's own law; the second is KVL round the loop. In matrix form,
with the input set to zero because eigenvalues are about what the circuit does on its own:

$$\frac{d}{dt}\begin{bmatrix} v_C \\ i_L \end{bmatrix}
 = \begin{bmatrix} 0 & 1/C \\ -1/L & -R/L \end{bmatrix}
   \begin{bmatrix} v_C \\ i_L \end{bmatrix}$$

Take $L = 20$ mH, $R = 80\ \Omega$, $C = 500$ nF:

```
1/C = 2e6        1/L = 50        R/L = 80 / 0.02 = 4000

A = [    0     2e6  ]
    [  -50   -4000  ]

trace = 0 + (-4000)              = -4000
det   = 0(-4000) - (2e6)(-50)    = +1e8

lam^2 + 4000 lam + 1e8 = 0
discriminant = 4000^2 - 4(1e8) = 1.6e7 - 4e8 = -3.84e8      (negative)
sqrt(3.84e8) = 19595.9

lam = ( -4000 +/- j 19595.9 ) / 2  =  -2000 +/- j 9798.0
```

Complex, in a conjugate pair, as they must be for a real matrix. Read them: the real part
$-2000\ \mathrm{s^{-1}}$ is an envelope decaying with $\tau = 0.5$ ms, and the imaginary
part $9798\ \mathrm{rad/s}$ is a ringing at $9798/2\pi = 1559$ Hz underneath it.

Now do the same circuit the way module 1 did it, with impedances and the divider rule:

$$\frac{V_C}{V_{in}} = \frac{1/sC}{sL + R + 1/sC} = \frac{1}{s^2LC + sRC + 1}$$

```
LC = 0.02 (5e-7) = 1e-8        RC = 80 (5e-7) = 4e-5

denominator:  1e-8 s^2 + 4e-5 s + 1  =  0
divide by 1e-8:      s^2 + 4000 s + 1e8  =  0
```

The identical polynomial. **The eigenvalues of the state matrix are the poles of the
transfer function.** They are not analogous, not related, not two things that happen to
agree on this example: they are the same roots of the same polynomial, reached once by
asking which patterns keep their shape and once by asking where the algebra blows up.
Which route you take is a matter of what you have in front of you — a schematic and a
probe point, or a set of state equations — and never a matter of which answer you get.

## The mistake, and why it is tempting

The commonest error is to read the eigenvalues off the diagonal. Here that would give
$0$ and $-4000$: one mode that never decays at all, and one that decays four times too
fast, with no ringing anywhere. Every part of that is wrong.

It is tempting for two reasons, and both contain a grain of truth. The first is that for a
diagonal — or triangular — matrix it is exactly right, and those are the examples anyone
meets first. The second is that $a_{11}$ genuinely is "the rate at which state 1 decays
*if nothing else is moving*", which is a true sentence about a circuit whose parts do not
talk to each other. The off-diagonal entries are precisely the fact that they do.

Look at what coupling does in the RC example. Both diagonal entries are $-2000$, and the
eigenvalues are $-1000$ and $-3000$: the coupling has pushed one mode slower and the other
faster, and moved neither of them a small amount. What it did not do is change their
average, because the trace is preserved: $-1000 - 3000 = -2000 - 2000$. The diagonal tells
you the *sum*, and nothing else.

The second mistake is about stability. Each mode contributes $e^{\lambda t}$, whose size
is $\left|e^{\lambda t}\right| = e^{(\operatorname{Re}\lambda)t}$, because the imaginary
part only rotates. So the test is the **real part**, strictly negative, for every
eigenvalue. Not the magnitude — a magnitude is never negative, so "all eigenvalues
negative" is not even a well-formed condition once they are complex, and complex
eigenvalues are the ordinary case for any circuit that can ring. Our RLC has
$|\lambda| = 10000$, which is a large positive number, and the circuit is perfectly
stable.

## Where this stops holding

**Repeated eigenvalues with only one eigenvector.** Take the same RLC and raise the
resistance to $R = 2\sqrt{L/C} = 2\sqrt{0.02/5\times10^{-7}} = 2(200) = 400\ \Omega$.
Then the discriminant vanishes and $\lambda = -10000$ twice. But there are not two
directions:

```
A - lam I  =  [  10000    2e6   ]      the rows are proportional: (-1/200)
              [    -50  -10000  ]      times the first row is the second

10000 v1 + 2e6 v2 = 0   ->   v2 = -0.005 v1   ->   one direction, (200, -1)
```

One eigenvalue, one line of eigenvectors, and a two-dimensional state space to fill. The
picture of "a sum of modes, each keeping its shape" simply fails here, and what fills the
gap is a solution of the form $t\,e^{\lambda t}$ — which is exactly the extra factor of
$t$ that shows up in the critically damped step response, and exactly the repeated-root
case of partial fractions from module 2. A matrix like this is called **defective**; it is
a measure-zero accident that you will nevertheless design your way onto, because critical
damping is a specification people write down.

**Non-linear circuits.** A diode or a transistor has no state matrix. What it has is a
*linearisation* about an operating point, and the eigenvalues of that describe only small
deviations from that point. Change the bias and you get a different matrix and different
eigenvalues; push the signal far enough and none of them apply.

**Time-varying circuits.** If $A$ changes with time — a switching converter, a gain being
ramped — then computing the eigenvalues at each instant and finding them all negative
proves nothing at all. There are standard examples of $\dot{x} = A(t)x$ with both
eigenvalues pinned at $-1$ for every $t$ whose solutions grow without bound. Eigenvalues
answer a question about a *constant* matrix, and silently give a wrong answer to any
other.

**Modes the transfer function cannot see.** The state matrix has one eigenvalue per energy
storage element. A transfer function from one particular input to one particular output
can have fewer poles than that, if a zero happens to sit exactly on a pole and cancel it.
The mode is still there, still ringing or still decaying — it is just invisible from that
pair of terminals. Which is the honest reason to prefer the matrix: it describes the
circuit, while the transfer function describes the circuit as seen through one probe.
''',
                },
                {
                    "title": "More measurements than unknowns, and the matrix you build to say so",
                    "minutes": 15,
                    "body": r'''
The previous module ended with a geometric fact: when $Ac = y$ has no solution, the best
available $c$ is the one that makes the residual $y - Ac$ perpendicular to every column of
$A$, and that condition written down is

$$A^\top A\,c = A^\top y$$

Nothing in this unit changes that. What this unit is about is the step before it, which is
the part nobody derives for you: **where $A$ comes from**. The normal equations are three
lines of arithmetic once you have the matrix. Deciding what its columns are is the
modelling, and it is where the answer is really decided.

## A column is a shape

Read $Ac$ as a recipe. Column 1 times $c_1$, plus column 2 times $c_2$, and so on: the fit
is a weighted sum of the columns, and the coefficients are what you are solving for. So
each column is a **shape** — a whole vector, one entry per measurement — that you are
proposing the data is partly made of, and $c_j$ is how much of it there is.

Fit $y = c_0 + c_1x$ to measurements at $x = x_1 \dots x_n$ and the two shapes are

$$a_0 = (1, 1, \dots, 1), \qquad a_1 = (x_1, x_2, \dots, x_n)$$

"the same amount everywhere" and "an amount proportional to $x$". Add a quadratic term and
the third shape is $(x_1^2, \dots, x_n^2)$. Nothing about that requires the model to be a
polynomial: a column can be $\sin\omega t$, or $1/x$, or the measured response of some
other circuit. The only requirement is the one people get backwards, so it is worth stating
flatly:

> The model must be linear in the **parameters**. It need not be linear in the variable.

$y = c_0 + c_1x + c_2x^2$ is a least-squares problem, because the unknowns $c_j$ enter as
multipliers of known columns. $y = c_0e^{-x/c_1}$ is not, because $c_1$ is inside the
exponential and no column can be built without knowing it first. That distinction is the
whole of what makes least squares easy, and the second half of this unit is about the
standard trick for getting a problem across the line.

## Worked example: three columns, five points

Fit $y = c_0 + c_1x + c_2x^2$ to

```
x     -2      -1       0       1       2
y      4.10    0.90    0.20    1.10    4.00
```

Choosing $x$ symmetric about zero is not laziness, it is the single most useful habit in
fitting, and the arithmetic is about to show why. The matrix and the sums:

```
       [ 1  -2   4 ]                sum 1     = 5      sum x^3 = 0
       [ 1  -1   1 ]                sum x     = 0      sum x^4 = 2(16) + 2(1) = 34
 A  =  [ 1   0   0 ]                sum x^2   = 4+1+0+1+4 = 10
       [ 1   1   1 ]
       [ 1   2   4 ]

              [  5   0  10 ]                       sum y    = 10.30
    A'A  =    [  0  10   0 ]          A'y  =       sum x y  =  0.00
              [ 10   0  34 ]                       sum x^2 y = 34.40
```

Every entry of $A^\top A$ is one column dotted with another, and $\sum x = \sum x^3 = 0$
because the odd powers cancel across a symmetric spread. So the middle row and column are
empty except on the diagonal, and the $3\times3$ system falls apart into a single equation
and a $2\times2$ pair:

```
10 c1 = 0                      ->  c1 = 0

 5 c0 + 10 c2 = 10.30          ->  c0 = 2.06 - 2 c2
10 c0 + 34 c2 = 34.40          ->  10(2.06 - 2 c2) + 34 c2 = 34.40
                                   20.6 + 14 c2 = 34.40
                                   c2 = 13.80 / 14 = 0.985714
                                   c0 = 2.06 - 1.971429 = 0.088571
```

The fitted curve is $y = 0.08857 + 0.98571x^2$. Check it by computing the fit at each
point and subtracting:

```
x       fit                            y       residual
-2      0.08857 + 4(0.98571) = 4.03143  4.10   +0.068571
-1      0.08857 + 0.98571    = 1.07429  0.90   -0.174286
 0      0.08857              = 0.08857  0.20   +0.111429
 1      1.07429                         1.10   +0.025714
 2      4.03143                         4.00   -0.031429
```

and then take the three checks that cost nothing, one per column, because that is what
"perpendicular to every column" means:

```
sum e         =  0.068571 - 0.174286 + 0.111429 + 0.025714 - 0.031429 = 0.000000
sum x e       = -2(0.068571) + 0.174286 + 0 + 0.025714 - 2(0.031429)  = 0.000000
sum x^2 e     =  4(0.068571) - 0.174286 + 0 + 0.025714 - 4(0.031429)  = 0.000000
```

Three zeros, three columns. If any one of them had come out non-zero, the coefficients are
wrong and the arithmetic can be re-done before anything is built on it. Do this every
time; it is a complete test of the answer that uses none of the working that produced it.

The first of those zeros is worth a second look, though, because it is the one that
teaches a bad habit: whenever $A$ has a column of ones, the residuals sum to zero *no
matter what the data was*. It is a check on your arithmetic and never evidence that the
model was right.

## Worked example: a decay, straightened out

Now the problem least squares cannot take as it stands. A capacitor discharges through a
known 47 kΩ resistor and five readings are taken:

```
t (ms)    0.00    2.00    4.00    6.00    8.00
v (V)     6.02    3.88    2.57    1.66    1.10
```

The model is $v = A e^{-t/\tau}$, and $\tau$ sits in the exponent where least squares
cannot reach it. Take logarithms of both sides:

$$\ln v = \ln A - \frac{t}{\tau}$$

and the right-hand side is a straight line in $t$ — with intercept $\ln A$ and slope
$-1/\tau$, both of which enter *linearly*. So fit a line to $\ln v$ against $t$, with the
usual two columns, and read $\tau$ off the slope at the end. Working in milliseconds
throughout:

```
t        0        2         4         6         8
ln v     1.795087 1.355835  0.943906  0.506818  0.095310

n = 5              sum t   = 20        sum t^2 = 0+4+16+36+64 = 120
sum(ln v) = 4.696956        sum(t ln v) = 10.290681

     [   5   20 ] [ b0 ]     [  4.696956 ]
     [  20  120 ] [ b1 ]  =  [ 10.290681 ]

det = 5(120) - 20(20) = 600 - 400 = 200

b1 = ( 5(10.290681) - 20(4.696956) ) / 200
   = ( 51.453405 - 93.939120 ) / 200  =  -42.485715 / 200  =  -0.2124286  per ms
b0 = ( 120(4.696956) - 20(10.290681) ) / 200
   = ( 563.634720 - 205.813620 ) / 200 = 357.821100 / 200   =   1.7891055
```

Then undo the transform:

```
tau =  -1 / b1  =  1 / 0.2124286     =  4.7075 ms
A   =  e^b0     =  e^1.7891055       =  5.9841 V
C   =  tau / R  =  4.7075e-3 / 47000 =  1.0016e-7 F  =  100.16 nF
```

A 100 nF part, measured to within a sixth of a percent from five readings taken with a
voltmeter and a stopwatch. Note that the fitted $A = 5.98$ V is not the first reading of
6.02 V, and should not be: the fit has no obligation to pass through any data point, and
insisting that it starts at the first sample would throw away the averaging that made the
answer good.

## What the logarithm costs

Straightening the model changed the problem, and it is worth knowing how.

Least squares minimises the sum of squared residuals **in whatever coordinates you hand
it**. After the transform those residuals are differences of logarithms, and a difference
of logs is a *ratio*:
$\ln v_i - \ln \hat{v}_i = \ln\!\left(v_i/\hat{v}_i\right)$. So the log fit weights every
reading by its relative error. A 1% error on the 1.10 V tail reading counts exactly as much
as a 1% error on the 6.02 V one — even though in volts it is a fifth of the size.

For a decay that is usually what you want, because a voltmeter's error tends to scale with
the reading and because the tail is where $\tau$ is most visible. But it is not the same
answer as minimising $\sum(v_i - Ae^{-t_i/\tau})^2$ directly, which would let the large
early readings dominate and would need an iterative solver. Two defensible questions, two
different numbers. The mistake is not choosing one; it is not noticing that you chose.

Two more consequences fall straight out of $\ln$:

* **A reading of zero or below destroys it.** Deep in the tail, noise makes readings
  straddle zero, and $\ln$ of a negative number is not available. The usual fix is to stop
  taking samples once the signal is down to a few times the noise, which is also where they
  stopped being informative.
* **An offset breaks it completely.** If the true signal is $Ae^{-t/\tau} + V_0$ with some
  small residual offset $V_0$ — an amplifier's input offset, a leakage floor — then
  $\ln(v)$ is not a straight line at all, and the fitted $\tau$ comes out wrong in a way no
  amount of extra data will reveal. Subtract a measured floor before taking logs, or fit
  the offset as a third parameter with a non-linear method.

## Where the normal equations stop being the right tool

$A^\top A$ is a beautiful object — square, symmetric, and invertible whenever the columns
of $A$ are independent — and it has one serious defect: forming it **squares the condition
number**. Module 7 gave the condition number as the factor by which a relative error in
the data can be amplified in the answer; here is what happens to it.

For the symmetric $x = (-2,-1,0,1,2)$ above, $\operatorname{cond}(A) = 4.44$ and
$\operatorname{cond}(A^\top A) = 19.68$, which is $4.44^2$. Move the same five points to
$x = (0,1,2,3,4)$ — the same spacing, the same data, only shifted — and
$\operatorname{cond}(A) = 27.1$ while $\operatorname{cond}(A^\top A) = 735$. Shifting the
origin cost a factor of 37 in conditioning and changed nothing about the fitted curve.
That is the real reason to centre your $x$ values, and it costs one subtraction.

Push the degree up and the effect stops being academic. A degree-10 polynomial fit on
un-centred data has an $A^\top A$ whose condition number exceeds $10^{16}$, which is all
the precision a double has: the normal equations return numerical noise, and they do it
silently. What replaces them is a factorisation that never forms $A^\top A$ at all — QR,
or the SVD — which is what `numpy.linalg.lstsq` uses and why it is the right default for
anything beyond a small, well-scaled problem. Solving the normal equations, as the lab in
this module does, is correct and instructive and fine for two or three well-scaled columns.
It is not what you should reach for at degree eight.

The other limit is statistical rather than numerical. Least squares is the right estimator
when the error lives in $y$ alone, and when the errors at different points are independent
and of similar size. If $x$ is measured too, the residual should be counted perpendicular
to the *line* rather than vertically, which is a different method (total least squares). If
some readings are noisier than others, they should count less, which is weighted least
squares — and you have already seen a circuit doing exactly that, in the summing node from
the previous module where the weights were conductances. The formula does not know any of
this. It answers the question it was given.
''',
                },
                {
                    "title": "Residuals, and which parameters you actually know",
                    "minutes": 13,
                    "body": r'''
A fit hands back numbers with a great many decimal places and no opinion at all about
whether it should have been asked. Two things it leaves behind will tell you: the vector of
residuals, and the eigenvalues of $A^\top A$. The first says whether the *model* was the
right shape. The second says which of the *parameters* the data actually pinned down. Both
are free, and neither is looked at often enough.

## Structure in the residuals is a missing column

A cell is measured under load. Six currents, six terminal voltages:

```
I (A)    0.00    0.20    0.40    0.60    0.80    1.00
V (V)    4.00    3.86    3.71    3.55    3.37    3.16
```

Fit $V = E - RI$: two columns, the ones column and the currents.

```
     [   6.0   3.0 ] [ E ]     [ 21.650 ]           sum I   = 3.0    sum I^2 = 2.2
     [   3.0   2.2 ] [-R ]  =  [ 10.242 ]           sum V   = 21.650
                                                    sum I V = 10.242
det = 6(2.2) - 9 = 13.2 - 9 = 4.2

E  = ( 2.2(21.650) - 3.0(10.242) ) / 4.2 = ( 47.630 - 30.726 ) / 4.2 = 4.02476 V
-R = ( 6.0(10.242) - 3.0(21.650) ) / 4.2 = ( 61.452 - 64.950 ) / 4.2 = -0.83286
```

so $E = 4.025$ V and $R = 0.833\ \Omega$. Residuals, in millivolts:

```
I         0.00     0.20     0.40     0.60     0.80     1.00
fit (V)   4.0248   3.8582   3.6916   3.5250   3.3585   3.1919
e (mV)   -24.76    +1.81   +18.38   +24.95   +11.52   -31.90
```

They sum to zero, as they always will with a ones column, and they are small — 25 mV out
of 4 V is half a percent. And they are useless as they stand, because the number that
matters is not their size but their **shape**. Plot them against $I$ and they trace a
smooth arch: down at both ends, up in the middle, one sign change on each side. Noise does
not do that. Noise gives you a sign sequence with no pattern; this one is
$-,+,+,+,+,-$ with a single hump, which is what a quadratic term looks like when you refuse
to fit one.

So fit one. Add a column of $I^2$:

```
V = 3.99679 - 0.62304 I - 0.20982 I^2

e (mV)   +3.21   -3.79   -4.00   +2.57   +5.93   -3.93
```

The residuals have dropped by a factor of five and the pattern is gone — the signs now run
$+,-,-,+,+,-$ with no arc in them. The extra column found something real: the cell's
internal resistance is not constant, it rises with current, and the $I^2$ term is the first
correction for it.

This is the whole diagnostic, and it survives in far more complicated settings. **A
residual plot with structure means a missing term. A residual plot without structure means
you are done, whatever the size of the residuals.** Collecting more data shrinks the random
part and leaves the pattern exactly where it was — which is the strongest thing that can be
said against "just take more readings".

## Two ways to count the leftover, and why the denominator matters

Adding a column can never make $\sum e_i^2$ larger. The old fit is still available to the
bigger model — set the new coefficient to zero — so the minimum can only come down. Which
means "the sum of squares went down" is not evidence for anything: a quadratic will always
beat a line, a cubic will always beat the quadratic, and a degree-5 polynomial through six
points fits them exactly and has learned nothing.

The honest summary divides by what is left over instead:

$$s = \sqrt{\frac{\sum_i e_i^2}{n - p}}$$

with $n$ measurements and $p$ fitted parameters. The idea behind $n - p$ is that
$p$ of the residuals are not free: the orthogonality conditions pin down $p$ linear
combinations of them exactly, so only $n - p$ of the $n$ numbers carry information.

```
                        sum e^2      n - p    s
straight line (p=2)     2.728e-3       4      26.11 mV
with an I^2 term (p=3)  9.786e-5       3       5.71 mV
```

The line's $s$ is over four times the quadratic's. That is a real improvement, because
the denominator was already charged for the extra parameter. Fit a fifth-degree polynomial
to the same six points and $\sum e^2$ becomes zero while $n - p$ becomes one — and the
formula stops meaning anything, which is the right behaviour for a model with nothing left
to check.

## The eigenvalues of $A^\top A$ are the stiffnesses of the fit

Now the two halves of this module meet. Write $c = \hat{c} + \delta$, where $\hat{c}$ is the
least-squares answer, and expand the sum of squares:

$$\|y - Ac\|^2 = \|y - A\hat{c}\|^2 + \delta^\top A^\top A\,\delta$$

The cross term vanishes — that is exactly the orthogonality condition doing its work — so
the sum of squares is its minimum plus a quadratic form in how far you moved. $A^\top A$ is
symmetric, so it has real eigenvalues and a full orthogonal set of eigenvectors, and along
an eigenvector the quadratic form is just $\lambda\|\delta\|^2$. Move a distance $\delta$
along the eigenvector of eigenvalue $\lambda$ and the sum of squares rises by exactly
$\lambda\delta^2$. The eigenvalues *are* the stiffnesses.

Take the quadratic fit from the previous unit, $A^\top A = \begin{bmatrix}5&0&10\\0&10&0\\10&0&34\end{bmatrix}$.
The middle row is decoupled, so one eigenvalue is 10 with eigenvector $(0,1,0)$; the rest
is the $2\times2$ block $\begin{bmatrix}5&10\\10&34\end{bmatrix}$, whose trace is 39 and
determinant $170 - 100 = 70$:

```
lam^2 - 39 lam + 70 = 0    disc = 1521 - 280 = 1241,  sqrt = 35.2278

lam = (39 +/- 35.2278)/2  =  37.114   and   1.886

so the three eigenvalues are   37.114,   10,   1.886        cond = 19.68
```

The eigenvector for the smallest one comes from $(5 - 1.886)v_0 + 10v_2 = 0$, that is
$v_2/v_0 = -3.114/10 = -0.3114$, giving the unit direction $(0.955, 0, -0.297)$. Read that
as a sentence: *raise the constant term by 1.00 and lower the $x^2$ coefficient by 0.311,
and the data barely notices.* Concretely, moving the parameter vector 0.3 units along that
direction raises $\sum e^2$ by $1.886(0.3)^2 = 0.170$; moving the same 0.3 units along the
stiff direction raises it by $37.114(0.3)^2 = 3.34$, twenty times as much.

So the constant and the curvature are individually poorly determined and their combination
is well determined. That is why a fitted curve can be trustworthy in the middle of the data
while its coefficients wobble: the wobbles are correlated, and they cancel where the
measurements are. It is also, exactly, why the condition number matters, since
$\operatorname{cond}(A^\top A) = \lambda_{\max}/\lambda_{\min}$ and a stiff direction next
to a sloppy one is what a large condition number *is*.

## Where the diagnosis stops

**Extrapolation.** The residuals report on the region the data covers, and say nothing
whatever about anywhere else. The cell above was measured to 1 A; the fitted line crosses
zero volts at $4.025/0.833 = 4.83$ A, and that number is a statement about a straight line,
not about a battery. The quadratic fit, which describes the measured range far better,
predicts a *different* short-circuit current — and it is not more trustworthy out there
either. A model validated on $[0, 1]$ has been validated on $[0,1]$.

**Outliers.** Squaring makes one bad reading enormously influential, and the fit moves
towards it. Worse, having moved, the fit leaves a residual at the bad point that is
*smaller* than the error which caused it, so the very reading you want to find is partly
camouflaged by its own effect on the answer. This is why the residual plot beats the
residual sum, and why robust alternatives exist that minimise $\sum|e_i|$ instead — no
closed form, but no single point can dominate.

**Correlated errors.** The $n - p$ counting, and most of what anyone says about how good a
fit is, assumes the errors at different points are independent. If your instrument drifts
slowly during the sweep, they are not: the errors are smooth in time, and smooth errors look
exactly like a missing term in the model. The residual plot cannot tell those two apart. A
second sweep, taken in the reverse order, can.
''',
                },
            ],
            "sandbox": {
                "title": "Trace, determinant, and the shape of the flow",
                "visualiser": "phase-portrait",
                "minutes": 9,
                "brief": r'''
Four sliders set the entries of a $2\times2$ matrix $A$; the panel draws the flow of
$\dot{x} = Ax$. It plots a grid of short ticks showing which way the state is moving at
each point — direction only, all the same length, so they say nothing about speed — and
eight trajectories released from a ring around the origin and followed forwards in time.
The dot in the middle is the origin, the one state that never moves.

The readout underneath reports the trace and the determinant and names the shape. Watch
those two numbers rather than the four entries: they are the coefficients of
$\lambda^2 - (\operatorname{tr}A)\lambda + \det A$, so they are all the eigenvalues depend
on, and completely different-looking matrices with the same pair behave identically.

It opens on $a_{11}=0$, $a_{12}=1$, $a_{21}=-2.25$, $a_{22}=-0.9$, which is the companion
matrix of $s^2 + 0.9s + 2.25$ — a second-order circuit with $\omega_n = 1.5$ and
$\zeta = 0.3$.
''',
                "initial": {"a11": 0, "a12": 1, "a21": -2.25, "a22": -0.9},
                "notice": [
                    "As it opens: trace $-0.9$, determinant $2.25$, discriminant negative, so the eigenvalues are a complex pair and every trajectory winds inwards to the dot. Count the turns before a curve reaches the middle — that ratio of ringing to decay is $\\zeta$, and nothing else about the matrix matters to it.",
                    "Slide $a_{22}$ up to exactly 0. The trace goes to zero, the readout switches to *a centre*, and the eight curves close into rings that circle forever without approaching the origin. Nudge $a_{22}$ to $+0.05$ and the same rings open into outward spirals that leave the frame. That knife edge is the eigenvalues crossing the imaginary axis, and it happens at trace $= 0$ regardless of what the other three entries are doing.",
                    "Put $a_{22}$ back to $-0.9$ and drag $a_{21}$ up through zero. With $a_{11}=0$ and $a_{12}=1$ the determinant is just $-a_{21}$, so the moment $a_{21}$ goes positive the determinant goes negative and the readout says *saddle*. Look at the tick field: it lines up into two straight through-lines crossing at the origin. Those are the two eigenvectors — the only directions the flow does not bend — and the trajectories come in along one and leave along the other.",
                    "Try $a_{21} = -0.75$ with $a_{22} = -2$. The eigenvalues are now $-0.5$ and $-1.5$, both real, and the picture stops spiralling: trajectories bend once and then run in almost straight, flattened onto the direction belonging to $-0.5$. That is the slowest mode outliving the other, which is what settling time means. The dividing line between this and a spiral is $\\operatorname{tr}^2 = 4\\det$, and neither picture is more stable than the other.",
                    "Set $a_{11} = -0.3$, $a_{12} = 0$, $a_{21} = 0$, $a_{22} = -0.9$: a diagonal matrix, where the eigenvalues really are the diagonal entries and the eigenvectors really are the axes. Now raise $a_{12}$ back to 1. The whole picture shears over — but the matrix is still triangular, so the eigenvalues have not moved at all, and the readout's trace and determinant confirm it. Only when $a_{21}$ leaves zero do the eigenvalues actually change. Reading the diagonal is not wrong because the picture looks tilted; it is wrong because $a_{12}a_{21}$ is not zero.",
                ],
            },
            "numeric": [
                {
                    "title": "Two rates out of a trace and a determinant",
                    "minutes": 5,
                    "brief": r'''
The mechanical rung, to get the routine under your fingers. One matrix, one quadratic, two
roots, and the only things that can really go wrong are a sign and a reciprocal.

A two-node RC network with nothing driving it has already been written as $\dot{x} = Ax$
for you. Each eigenvalue $\lambda$ is a decay rate in $\mathrm{s^{-1}}$, and the time
constant belonging to it is $\tau = -1/\lambda$. The *slower* mode is the one with the
smaller $|\lambda|$ — the eigenvalue nearer the imaginary axis — and it is the one that
decides how long the circuit takes to settle.
''',
                    "prompt": "What is the time constant of the slower of this network's two natural modes?",
                    "note": "Give the answer in milliseconds, to two decimal places.",
                    "figure": r'''
A two-node RC network with the supply removed, written as $\dot{x} = Ax$ with $x$ the two
node voltages and the entries of $A$ in $\mathrm{s^{-1}}$:

$$A = \begin{bmatrix} -600 & 200 \\ 300 & -700 \end{bmatrix}$$

Nothing drives it. The question is only how the charge already on the two capacitors leaks
away.
''',
                    "given": [
                        {"label": "Characteristic polynomial", "value": "$\\lambda^2 - (\\operatorname{tr}A)\\lambda + \\det A = 0$"},
                        {"label": "Trace", "value": "the sum of the diagonal entries"},
                        {"label": "Determinant", "value": "$a_{11}a_{22} - a_{12}a_{21}$"},
                        {"label": "Time constant", "value": "$\\tau = -1/\\lambda$"},
                    ],
                    "aside": "Both roots come out negative here, so both time constants are positive. Take the "
                             "one with the smaller magnitude of $\\lambda$, and remember the answer is wanted "
                             "in milliseconds while the matrix is in $\\mathrm{s^{-1}}$.",
                    "answer": 2.5,
                    "tol": 0.02,
                    "unit": "ms",
                    "hint": "Trace $= -600 + (-700)$ and $\\det = (-600)(-700) - (200)(300)$. Put both into "
                            "$\\lambda^2 - (\\operatorname{tr})\\lambda + \\det$ and use the quadratic formula; "
                            "the discriminant is a perfect square.",
                    "wrong": "1.11 ms is the other mode, the fast one. 1.67 ms is $1/600$ — the diagonal read "
                             "off as if it were the eigenvalues, which is right only for a matrix with nothing "
                             "off the diagonal and wrong here by a factor of 1.5. 1.54 ms averages the two "
                             "diagonal entries; that average is genuinely half the trace, but half the trace is "
                             "the average of the two eigenvalues, not either one of them. And if your roots "
                             "came out $+400$ and $+900$, the minus sign in front of the trace was dropped.",
                    "why": r'''
```
trace = -600 + (-700)                       = -1300
det   = (-600)(-700) - (200)(300)
      = 420000 - 60000                      = 360000

char.   lam^2 - (-1300) lam + 360000
      = lam^2 + 1300 lam + 360000  = 0

disc  = 1300^2 - 4(360000)
      = 1690000 - 1440000 = 250000          sqrt = 500

lam   = ( -1300 +/- 500 ) / 2               = -400   and   -900

tau   = -1/lam
      = 1/400 = 0.0025 s                    = 2.500 ms      <- slower
      = 1/900 = 0.001111 s                  = 1.111 ms
```

Take the two free checks before going any further: the roots must sum to the trace and
multiply to the determinant. $-400 - 900 = -1300$, and $(-400)(-900) = 360000$. Both hold,
so the arithmetic is sound.

Now look at what the coupling did. The diagonal entries are $-600$ and $-700$, and the
eigenvalues are $-400$ and $-900$. Neither eigenvalue is near either diagonal entry: the
off-diagonal terms have pushed one mode 33% slower and the other 29% faster, while leaving
the sum untouched — because the trace is $-1300$ either way. That is the general pattern.
Coupling spreads the rates apart around their average; it never moves the average.

The two modes are worth naming, since they are visible in the matrix once you look. For
$\lambda = -400$:

```
(A + 400 I) v = 0        [ -200   200 ] v = 0     ->   v = (1, 1)
                         [  300  -300 ]
```

both nodes at the same voltage, sagging together. For $\lambda = -900$:

```
(A + 900 I) v = 0        [  300   200 ] v = 0     ->   v = (2, -3)
                         [  300   200 ]
```

the two nodes on opposite sides of zero, driving current hard through whatever resistor
joins them, and dying 2.25 times as fast for it. Which is why the slow mode is the one
that decides settling: after 4 ms the fast mode is down to 2.7% of where it started while
the slow one still has a fifth of its amplitude, so whatever is left on the screen looks
like $(1,1)$ decaying at 2.5 ms.
''',
                },
                {
                    "title": "How fast does this loop ring?",
                    "minutes": 8,
                    "brief": r'''
A circuit rather than a matrix, and one step further: you have to *write* the state matrix
before you can take its trace and determinant.

The state of this circuit is two numbers, and choosing which two is the only real decision.
Take the capacitor voltage and the inductor current — the two quantities that cannot jump,
because each is proportional to stored energy. Then the capacitor's own law gives one
equation and KVL round the loop gives the other, and the pair is $\dot{x} = Ax + bv_{in}$.
Eigenvalues are about what the circuit does when left alone, so the input plays no part in
them.

The eigenvalues here come out complex. Their imaginary part is the angular frequency of
the ringing, in rad/s, and the question asks for it in hertz.
''',
                    "prompt": "At what frequency does this circuit ring after a step?",
                    "note": "Give the answer in hertz, to four significant figures.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "l", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.02},
                            {"id": "r", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 80},
                            {"id": "c", "kind": "C", "x": 13, "y": 7, "rot": 1, "value": 5e-7},
                            {"id": "g1", "kind": "GND", "x": 13, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 15, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [5, 5]},
                            {"a": [7, 5], "b": [9, 5]},
                            {"a": [11, 5], "b": [13, 5]},
                            {"a": [13, 5], "b": [13, 6]},
                            {"a": [13, 8], "b": [13, 10]},
                            {"a": [13, 5], "b": [15, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "1.00 V step"},
                        {"label": "L", "value": "20.0 mH"},
                        {"label": "R", "value": "80.0 Ω"},
                        {"label": "C", "value": "500 nF"},
                        {"label": "State", "value": "$x = (v_C,\\ i_L)$"},
                    ],
                    "aside": "With $x = (v_C, i_L)$ the state matrix is "
                             "$\\begin{bmatrix} 0 & 1/C \\\\ -1/L & -R/L\\end{bmatrix}$. Its trace is $-R/L$ "
                             "and its determinant is $1/(LC)$; put both in ohms, henries and farads.",
                    # Measured, not restated. The phase of a second-order low-pass is exactly -90 degrees at
                    # its natural frequency for any damping, so bisecting on phase finds fn off the swept
                    # schematic, and the gain there is 1/(2 zeta). The ringing frequency is then fn times
                    # sqrt(1 - zeta^2), and every input to it came from the drawn circuit.
                    "check": r'''
const V = c.values('V')[0];
let lo = 1, hi = 1e6;
for (let i = 0; i < 90; i++) {
  const mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > -90) lo = mid; else hi = mid;
}
const fn = Math.sqrt(lo * hi);            /* natural frequency, Hz */
const zeta = V / (2 * c.gain(fn));        /* |H| at fn is 1/(2 zeta) */
return fn * Math.sqrt(1 - zeta * zeta);   /* the damped, ringing frequency */
''',
                    "answer": 1559.4,
                    "tol": 1.5,
                    "unit": "Hz",
                    "hint": "$\\det A = 1/(LC) = 10^8$, so $\\omega_n = 10^4$ rad/s, and "
                            "$\\operatorname{tr}A = -R/L = -4000$, so the real part is $-2000$. The ringing "
                            "frequency is $\\sqrt{\\omega_n^2 - 2000^2}$, then divide by $2\\pi$.",
                    "wrong": "1592 Hz is $\\omega_n/2\\pi$, the *undamped* frequency. Damping always slows the "
                             "ringing, never speeds it up, so the answer has to come out below that — here by "
                             "2%, because $\\sqrt{1-\\zeta^2} = 0.98$. 9798 Hz is the right number left in "
                             "rad/s. 318.3 Hz converts the decay rate 2000 $\\mathrm{s^{-1}}$ to hertz, which "
                             "is not a frequency of anything: it is how fast the envelope shrinks, not how "
                             "fast the waveform crosses zero.",
                    "why": r'''
The two state equations, then the matrix:

```
C dvC/dt = iL                         ->   dvC/dt = iL / C
L diL/dt = vin - R iL - vC            ->   diL/dt = -vC/L - (R/L) iL + vin/L

1/C = 1/5e-7 = 2e6      1/L = 1/0.02 = 50      R/L = 80/0.02 = 4000

A = [    0     2e6  ]
    [  -50   -4000  ]
```

Trace and determinant, then the quadratic:

```
trace = 0 + (-4000)                        = -4000
det   = (0)(-4000) - (2e6)(-50)            = +1e8

lam^2 + 4000 lam + 1e8 = 0

disc  = 4000^2 - 4(1e8) = 1.6e7 - 4e8      = -3.84e8
sqrt(3.84e8)                               = 19595.9

lam   = ( -4000 +/- j 19595.9 ) / 2        = -2000 +/- j 9798.0
```

The ringing frequency is the imaginary part:

```
f = 9798.0 / (2 pi)                        = 1559.4 Hz
```

Read the pair rather than just the number you were asked for. The real part $-2000$
$\mathrm{s^{-1}}$ is an envelope with $\tau = 0.5$ ms, so the ring is more or less over
after 2 ms. In that time the waveform completes $1559.4 \times 2\ \mathrm{ms} = 3.1$
cycles — three visible bumps, which is exactly what $\zeta = 0.2$ looks like on a scope.

Two cross-checks, both worth the thirty seconds.

**Against the transfer function.** The divider rule with impedances gives
$V_C/V_{in} = 1/(s^2LC + sRC + 1)$. With $LC = 10^{-8}$ and $RC = 4\times10^{-5}$ that
denominator is $10^{-8}s^2 + 4\times10^{-5}s + 1$; multiply by $10^8$ and it is
$s^2 + 4000s + 10^8$, the identical polynomial. The eigenvalues of the state matrix are
the poles of the transfer function, and the two routes cannot disagree.

**Against $\omega_n$ and $\zeta$.** $\omega_n = 1/\sqrt{LC} = 10^4$ rad/s and
$\zeta = \tfrac{R}{2}\sqrt{C/L} = 40\sqrt{2.5\times10^{-5}} = 0.2$. Then
$\zeta\omega_n = 2000$ matches the real part, and
$\omega_n\sqrt{1-\zeta^2} = 10^4(0.9798) = 9798$ matches the imaginary part. Same numbers,
third route.

One thing that is *not* true, and is worth saying because it looks like it should be: the
ringing frequency is not $1/\sqrt{LC}$ with the resistor ignored. It is lower, by the
factor $\sqrt{1-\zeta^2}$. Here that factor is 0.98 and the difference is only 32 Hz, which
is why the approximation survives so long in practice — but at $\zeta = 0.7$ the same
factor is 0.71, and at $\zeta = 1$ the ringing frequency is zero and the circuit does not
ring at all.
''',
                },
                {
                    "title": "A capacitance out of five voltmeter readings",
                    "minutes": 9,
                    "brief": r'''
Now the other half of the module, and the trick that makes it apply.

A capacitor of unknown value discharges through a resistor you have measured. The model is
$v = Ae^{-t/\tau}$, and $\tau$ is inside the exponent where least squares cannot reach it —
no column of a design matrix can be built without knowing $\tau$ first, so the problem as
written is not a linear one.

Take logarithms and it becomes one. $\ln v = \ln A - t/\tau$ is a straight line in $t$, so
fit a line to $\ln v$ against $t$ with the usual two columns, and both parameters enter
linearly. The slope is $-1/\tau$. Then $\tau = RC$ gives the capacitance.

Work in milliseconds throughout and convert once at the end; it keeps the sums to a
sensible size.
''',
                    "prompt": "What capacitance do these five readings imply?",
                    "note": "Give the answer in nanofarads, to one decimal place.",
                    "figure": r'''
A charged capacitor is left to discharge through a measured $10.0\ \mathrm{k}\Omega$
resistor, and the voltage across it is read five times:

```
    t (ms)     0.00    3.00    6.00    9.00   12.00
    v (V)      5.04    2.61    1.38    0.72    0.38
```

The model is $v = Ae^{-t/\tau}$, with both $A$ and $\tau$ unknown, and $\tau = RC$.
''',
                    "given": [
                        {"label": "Model", "value": "$v = Ae^{-t/\\tau}$"},
                        {"label": "Linearised", "value": "$\\ln v = \\ln A - t/\\tau$"},
                        {"label": "Columns of $A$", "value": "ones, and the times in ms"},
                        {"label": "R", "value": "10.0 kΩ, measured"},
                        {"label": "Wanted", "value": "$C = \\tau/R$, in nF"},
                    ],
                    "aside": "The normal equations for a line are $\\begin{bmatrix} n & \\sum t \\\\ "
                             "\\sum t & \\sum t^2\\end{bmatrix}\\begin{bmatrix} b_0 \\\\ b_1 \\end{bmatrix} = "
                             "\\begin{bmatrix} \\sum y \\\\ \\sum ty\\end{bmatrix}$ with $y = \\ln v$. Keep "
                             "six decimal places on the logarithms; four is not enough here.",
                    "answer": 464.6,
                    "tol": 2.0,
                    "unit": "nF",
                    "hint": "$\\sum t = 30$, $\\sum t^2 = 270$ and the determinant of the $2\\times2$ is "
                            "$5(270) - 30^2 = 450$. Solve for the slope $b_1$ only — the intercept is not "
                            "needed for this question — then $\\tau = -1/b_1$ in ms.",
                    "wrong": "1142 nF comes from fitting a straight line to the raw voltages instead of their "
                             "logarithms and calling the crossing at $v = 0$ the time constant. An exponential "
                             "never crosses zero, which is the whole reason for the logarithm. 464552 nF is "
                             "the right fit with the milliseconds never turned into seconds — a factor of "
                             "$10^3$, so check the exponent before the digits. And 5.01 is not a capacitance "
                             "at all: it is $e^{b_0}$, the fitted starting voltage.",
                    "why": r'''
```
t          0.00      3.00      6.00      9.00     12.00
v          5.04      2.61      1.38      0.72      0.38
y = ln v   1.617406  0.959350  0.322083 -0.328504 -0.967584

n = 5            sum t   = 30            sum t^2 = 0+9+36+81+144 = 270
sum y   = 1.617406 + 0.959350 + 0.322083 - 0.328504 - 0.967584  =  1.602751
sum t y = 3(0.959350) + 6(0.322083) + 9(-0.328504) + 12(-0.967584)
        = 2.878050 + 1.932498 - 2.956536 - 11.611008            = -9.756996

    [   5    30 ] [ b0 ]     [  1.602751 ]
    [  30   270 ] [ b1 ]  =  [ -9.756996 ]

det = 5(270) - 30(30) = 1350 - 900 = 450

b1  = ( 5(-9.756996) - 30(1.602751) ) / 450
    = ( -48.784980 - 48.082530 ) / 450 = -96.867510 / 450 = -0.2152611  per ms

tau = -1/b1 = 1/0.2152611                                    = 4.6455 ms
C   = tau / R = 4.6455e-3 / 10000 = 4.6455e-7 F              = 464.6 nF
```

For completeness the intercept is
$b_0 = (270(1.602751) - 30(-9.756996))/450 = 725.4526/450 = 1.612117$, so the fitted
starting voltage is $e^{1.612117} = 5.013$ V against a first reading of 5.04 V. The fit is
not obliged to pass through any measurement and here it does not, which is the averaging
working: five readings have out-voted one.

Two remarks worth more than the number.

**On the nearest standard value.** 464.6 nF is almost certainly a part marked 470 nF, which
is 1.2% away — well inside the $\pm10\%$ such a part is usually sold at. Least squares has
given you a measurement, not a marking, and reporting it as "470 nF" throws away the
information that this particular part is on the low side of its tolerance band.

**On what the logarithm did to the weighting.** After the transform, the residual at each
point is $\ln(v_i/\hat{v}_i)$ — a *ratio*, not a difference. So the 0.38 V tail reading
carries exactly as much weight as the 5.04 V first one, and a 1 mV error at the tail counts
thirteen times as heavily as a 1 mV error at the start. For a decay measured with an
instrument whose error scales with the reading, that is the right thing. It is not the same
answer as minimising $\sum(v_i - Ae^{-t_i/\tau})^2$ directly, which would let the early
readings dominate and needs an iterative solver. Both are defensible; only one of them is
three lines of arithmetic.
''',
                },
                {
                    "title": "How much of the reading the straight line cannot account for",
                    "minutes": 10,
                    "brief": r'''
This one is not about the fitted parameters at all. It is about what is left over after
they have been subtracted, which is the part that tells you whether the model deserved to
be fitted.

Five readings from a cell under load, and the obvious model $V = E - RI$: two columns, the
ones column and the currents. Solve the $2\times2$ normal equations, subtract the fitted
line from each reading, and summarise the five leftovers with

$$s_{\mathrm{rms}} = \sqrt{\frac{1}{n}\sum_i e_i^2}$$

Do look at the five residuals individually before you square them. Their pattern is the
point of the exercise, and the single number is only the way of putting a size on it.
''',
                    "prompt": "What is the root-mean-square residual of the least-squares straight line through these readings?",
                    "note": "Give $\\sqrt{\\tfrac{1}{5}\\sum e_i^2}$ in millivolts, to two decimal places.",
                    "figure": r'''
Five readings from a cell, taken with an electronic load:

```
    I (A)     0.00    0.10    0.20    0.30    0.40
    V (V)    12.00   11.62   11.20   10.74   10.24
```

Fit $V = E - RI$ by least squares, then measure what the fit failed to account for.
''',
                    "given": [
                        {"label": "Model", "value": "$V = E - RI$, two parameters"},
                        {"label": "Columns", "value": "ones, and the currents in amps"},
                        {"label": "Residual", "value": "$e_i = V_i - \\hat{V}_i$, data minus fit"},
                        {"label": "Wanted", "value": "$\\sqrt{\\tfrac{1}{5}\\sum e_i^2}$, in mV"},
                    ],
                    "aside": "$\\sum I = 1.0$ and $\\sum I^2 = 0.30$, so the $2\\times2$ matrix is "
                             "$\\begin{bmatrix}5 & 1\\\\ 1 & 0.3\\end{bmatrix}$ and its determinant is 0.5. "
                             "The residuals come out as exact multiples of 20 mV, which is a sign the "
                             "arithmetic went in cleanly.",
                    "answer": 33.47,
                    "tol": 0.15,
                    "unit": "mV",
                    "hint": "$E$ and the slope first, from the normal equations. Then evaluate the line at each "
                            "of the five currents, subtract, square, add, divide by five, and take the root.",
                    "wrong": "74.83 mV is $\\|e\\|$ itself — the square root of the sum, with the division by "
                             "five left out. 43.20 mV divides by $n - p = 3$ instead of by $n$; that is a "
                             "perfectly good statistic and the one you would use to compare models, but it is "
                             "not what was asked for here. And 0 mV is what you get from noticing that the "
                             "residuals sum to zero and concluding they are all zero: they sum to zero because "
                             "$A$ has a column of ones, always, no matter how badly the model fits.",
                    "why": r'''
```
sums     n = 5        sum I = 1.00        sum I^2 = 0.30
         sum V = 12.00+11.62+11.20+10.74+10.24                = 55.80
         sum I V = 0.1(11.62) + 0.2(11.20) + 0.3(10.74) + 0.4(10.24)
                 = 1.162 + 2.240 + 3.222 + 4.096              = 10.720

    [  5     1.0 ] [  E ] = [ 55.800 ]        det = 5(0.30) - 1 = 0.50
    [  1.0   0.3 ] [ -R ]   [ 10.720 ]

 E  = ( 0.30(55.800) - 1.0(10.720) ) / 0.50 = (16.740 - 10.720)/0.50 = 12.040 V
-R  = ( 5(10.720) - 1.0(55.800) )   / 0.50 = (53.600 - 55.800)/0.50 = -4.400 V/A

fitted line     V = 12.040 - 4.400 I

I        0.00     0.10     0.20     0.30     0.40
fit     12.040   11.600   11.160   10.720   10.280
e (V)   -0.040   +0.020   +0.040   +0.020   -0.040

sum e   = 0.000                    sum I e = 0.000        (both, as they must)
sum e^2 = 0.0016 + 0.0004 + 0.0016 + 0.0004 + 0.0016      = 0.0056

s_rms = sqrt( 0.0056 / 5 ) = sqrt(0.00112) = 0.033466 V   = 33.47 mV
```

Now the part that matters. Line the residuals up in order:

```
   -40    +20    +40    +20    -40      mV
```

Symmetric, one hump, down at both ends. That is not noise. Noise gives a sign sequence with
no shape to it; this one is a parabola drawn in millivolts, and it is what a missing
quadratic term looks like when you insist on fitting a line. Note also that the two
orthogonality checks pass perfectly — $\sum e = 0$ and $\sum Ie = 0$ — which tells you the
*fit* is the best straight line there is, and tells you nothing whatever about whether a
straight line was the right thing to fit. Those checks certify the arithmetic, never the
model.

Add a column of $I^2$ and the picture closes:

```
V = 12.000 - 3.600 I - 2.000 I^2

I        0.00     0.10     0.20     0.30     0.40
fit     12.000   11.620   11.200   10.740   10.240
e         0        0        0        0        0
```

Exactly zero, to every decimal place in the data. The 33.47 mV was never noise at all: it
was one missing term, and the readings are a perfect quadratic. That will not happen with
real measurements, but the diagnostic that found it will.

Which raises the question of when to stop adding columns, since a big enough polynomial
fits any data exactly and has learned nothing. The honest summary divides by the degrees of
freedom, $s = \sqrt{\sum e_i^2/(n-p)}$: here that is 43.20 mV for the line and 0 for the
quadratic, and going further to a cubic would still give 0 while spending another degree of
freedom for nothing. Adding a column can never raise $\sum e^2$ — the old fit is still
available to the larger model — so a falling sum of squares is not evidence by itself. A
falling $s$, and a residual plot that loses its shape, is.
''',
                },
                {
                    "title": "Two resistors damping the same pair of poles",
                    "minutes": 12,
                    "brief": r'''
The hard rung. Two things make it harder than the earlier RLC, and both are worth naming
before you start.

The damping is in two places. There is a resistor in series with the inductor, and a second
one in parallel with the capacitor, and neither of the memorised formulas covers a circuit
with both. So there is no shortcut: write the two state equations, build the matrix, take
its trace and determinant.

And the quantity asked for is not a voltage, a current or a frequency. It is the rate at
which the ringing envelope shrinks — the magnitude of the real part of the eigenvalues, in
$\mathrm{s^{-1}}$. If the eigenvalues are $-\sigma \pm j\omega_d$, the answer is $\sigma$,
and the trace gives it directly without ever solving the quadratic.
''',
                    "prompt": "At what rate does this circuit's ringing envelope decay?",
                    "note": "Give the magnitude of the real part of the eigenvalues, in $\\mathrm{s^{-1}}$, to the nearest 10.",
                    "diagram": {
                        "parts": [
                            {"id": "v", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                            {"id": "g0", "kind": "GND", "x": 3, "y": 9},
                            {"id": "r1", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 200},
                            {"id": "l", "kind": "L", "x": 10, "y": 5, "rot": 0, "value": 0.05},
                            {"id": "c", "kind": "C", "x": 13, "y": 7, "rot": 1, "value": 2e-7},
                            {"id": "g1", "kind": "GND", "x": 13, "y": 10},
                            {"id": "r2", "kind": "R", "x": 16, "y": 7, "rot": 1, "value": 5000},
                            {"id": "g2", "kind": "GND", "x": 16, "y": 10},
                            {"id": "out", "kind": "OUT", "x": 18, "y": 5},
                        ],
                        "wires": [
                            {"a": [3, 7], "b": [3, 9]},
                            {"a": [3, 5], "b": [5, 5]},
                            {"a": [7, 5], "b": [9, 5]},
                            {"a": [11, 5], "b": [13, 5]},
                            {"a": [13, 5], "b": [13, 6]},
                            {"a": [13, 8], "b": [13, 10]},
                            {"a": [13, 5], "b": [16, 5]},
                            {"a": [16, 5], "b": [16, 6]},
                            {"a": [16, 8], "b": [16, 10]},
                            {"a": [16, 5], "b": [18, 5]},
                        ],
                    },
                    "given": [
                        {"label": "Supply", "value": "1.00 V step"},
                        {"label": "R1, in series with L", "value": "200 Ω"},
                        {"label": "L", "value": "50.0 mH"},
                        {"label": "C", "value": "200 nF"},
                        {"label": "R2, across C", "value": "5.00 kΩ"},
                        {"label": "State", "value": "$x = (v_C,\\ i_L)$, with $v_C$ the probed node"},
                    ],
                    "aside": "KCL at the output node says the inductor current splits between the capacitor "
                             "and $R_2$; KVL round the loop says the source drives $R_1$, $L$ and the node "
                             "voltage. The trace of the resulting matrix is $-(1/R_2C + R_1/L)$, and you only "
                             "need half of its magnitude.",
                    # Measured, not restated. Phase is exactly -90 degrees at wn for any second-order
                    # low-pass, so bisecting on phase finds wn; the DC solve gives H(0); and for
                    # H = K/(s^2 + 2 sigma s + wn^2) the ratio |H(j wn)| / H(0) is wn / (2 sigma). All three
                    # readings come off the drawn circuit, so editing any component moves the answer.
                    "check": r'''
const V = c.values('V')[0];
let lo = 1, hi = 1e6;
for (let i = 0; i < 90; i++) {
  const mid = Math.sqrt(lo * hi);
  if (c.phase(mid) > -90) lo = mid; else hi = mid;
}
const fn = Math.sqrt(lo * hi);
const wn = 2 * Math.PI * fn;
const h0 = c.vout() / V;                  /* DC gain, from a DC solve of the drawing */
const hn = c.gain(fn) / V;                /* |H| at the natural frequency */
return h0 * wn / (2 * hn);                /* = sigma */
''',
                    "answer": 2500.0,
                    "tol": 15.0,
                    "unit": "s⁻¹",
                    "hint": "$\\dot{v}_C = -v_C/(R_2C) + i_L/C$ and $\\dot{i}_L = -v_C/L - (R_1/L)i_L$. The "
                            "trace is the sum of those two diagonal entries, and $\\sigma$ is half its "
                            "magnitude.",
                    "wrong": "2000 $\\mathrm{s^{-1}}$ is $R_1/2L$: the series resistor's contribution alone, "
                             "which is the answer if $R_2$ is treated as infinite. 500 $\\mathrm{s^{-1}}$ is "
                             "$1/(2R_2C)$: the shunt resistor alone, the answer if $R_1$ were zero. The two "
                             "add, because the trace adds, and 2000 + 500 is the whole of the working. "
                             "5000 $\\mathrm{s^{-1}}$ is the magnitude of the trace itself, with the factor of "
                             "two forgotten. 5200 comes from putting $R_1 + R_2$ over $2L$, which mixes a "
                             "series resistance with a shunt one as though they were in the same branch.",
                    "why": r'''
Two equations. KCL at the output node: the inductor delivers $i_L$, and it goes into the
capacitor and into $R_2$. KVL round the source loop: the supply is spent across $R_1$, the
inductor and the node.

```
C dvC/dt = iL - vC/R2          ->   dvC/dt = -vC/(R2 C) + iL/C
L diL/dt = vin - R1 iL - vC    ->   diL/dt = -vC/L - (R1/L) iL + vin/L

1/(R2 C) = 1/(5000 * 2e-7) = 1/1e-3        = 1000
1/C      = 1/2e-7                          = 5e6
1/L      = 1/0.05                          = 20
R1/L     = 200/0.05                        = 4000

A = [ -1000    5e6  ]
    [   -20  -4000  ]
```

Everything asked for is in the trace:

```
trace = -1000 + (-4000)        = -5000
sigma = |trace| / 2            = 2500 s^-1
```

That is the answer. The rest is worth doing anyway, because it tells you whether the
circuit rings at all — a decay rate is only an *envelope* if there is something inside it:

```
det   = (-1000)(-4000) - (5e6)(-20)
      = 4e6 + 1e8                    = 1.04e8        so wn = 10198 rad/s

disc  = (-5000)^2 - 4(1.04e8)
      = 2.5e7 - 4.16e8               = -3.91e8       negative, so complex

lam   = -2500 +/- j 9886.9      ->    ringing at 1573.5 Hz under an envelope
                                      with tau = 1/2500 = 0.4 ms
```

$\zeta = \sigma/\omega_n = 2500/10198 = 0.245$, so a few visible cycles. Good.

## Why the two dampings add

The result $\sigma = \tfrac{1}{2}\left(\dfrac{R_1}{L} + \dfrac{1}{R_2C}\right)$ is the one
line to carry away from this question, and it is worth seeing why it has to be a sum.

$\sigma$ is half the trace, and the trace is a sum of diagonal entries. Each damping
element contributes to exactly one of them: $R_1$ is in series with the inductor and appears
only in the inductor's own equation, as $-R_1/L$; $R_2$ is across the capacitor and appears
only in the capacitor's equation, as $-1/(R_2C)$. Neither touches the other's row. So they
add, and they add as *rates* — never as resistances, and never as damping ratios.

Which explains why the two obvious wrong answers are the two obvious wrong answers. Take
$R_2 \to \infty$ and the shunt term vanishes, leaving the familiar series-RLC result
$\sigma = R_1/2L = 2000$. Take $R_1 \to 0$ and the series term vanishes, leaving the
parallel-RLC result $\sigma = 1/(2R_2C) = 500$. Each memorised formula is the general one
with the other resistor removed, and using either here loses a fifth or four fifths of the
damping.

Notice one more thing about the direction of each dependence, because it is the sort of
thing that gets inverted in a hurry. Raising $R_1$ damps the circuit **more** — it is in
series with the current, so a bigger value burns more of it. Raising $R_2$ damps it
**less** — it is across the node, so a bigger value steals less of the current, and in the
limit $R_2 \to \infty$ it does nothing at all. The two resistors pull in opposite
directions, and the arithmetic says so: $R_1$ is on top of its term and $R_2$ is underneath
its own.
''',
                },
            ],
            "blanks": {
                "title": "What centring the data does to $A^\\top A$",
                "minutes": 9,
                "caption": "the same fit, the same answer, and a matrix twelve times better behaved",
                "lang": "text",
                "brief": r'''
Both halves of this module in one page of arithmetic.

Four measurements at $x = 0, 1, 2, 3$, and a straight line to be fitted to them. Build
$A^\top A$, find its eigenvalues, and take the ratio of the largest to the smallest — that
ratio is the condition number, and it is how far a small error in the data can be
magnified on its way into the coefficients.

Then do the whole thing again with the $x$ values shifted so that they average zero.
Nothing about the fitted line changes: the same four points, the same straight line through
them, the same residuals. Only the *coordinates the coefficients are expressed in* have
moved. Watch what happens to the matrix.

Nothing is executed here — this is arithmetic you are choosing.
''',
                "listing": """data      x = ( 0, 1, 2, 3 )        model:  y = c0 + c1 x

              [ 1  0 ]
      A   =   [ 1  1 ]        columns: the ones column, and the x column
              [ 1  2 ]
              [ 1  3 ]

      A'A = [  4   ___ ]      off-diagonal = ones . x   = 0+1+2+3
            [  6   14  ]      bottom right = x . x      = 0+1+4+9

      trace = 4 + 14 = 18            det = 4(14) - 6(6) = ___

      lam^2 - 18 lam + 20 = 0        disc = 324 - 80 = 244,  sqrt = 15.6205

      lam = ( 18 +/- 15.6205 ) / 2 =  16.810   and   ___

      cond = 16.810 / 1.190                              = ___


centred   x' = x - mean(x) = ( -1.5, -0.5, 0.5, 1.5 )

      A'A = [  4    ___ ]      off-diagonal = ones . x'  = -1.5-0.5+0.5+1.5
            [  0     5  ]      bottom right = x' . x'    = 2.25+0.25+0.25+2.25

      already diagonal, so the eigenvalues are 4 and 5

      cond = 5 / 4                                       = ___
""",
                "blanks": [
                    {
                        "prompt": "The off-diagonal entry of $A^\\top A$, before centring.",
                        "hole": "?",
                        "opts": ["6", "4", "14", "3"],
                        "a": 0,
                        "why": "It is the ones column dotted with the $x$ column, which is just $\\sum x = 0+1+2+3 = 6$. It has to match the 6 already printed below the diagonal, because $A^\\top A$ is symmetric for every $A$.",
                        "whys": [
                            "It is the ones column dotted with the $x$ column, which is just $\\sum x = 0+1+2+3 = 6$. It has to match the 6 already printed below the diagonal, because $A^\\top A$ is symmetric for every $A$.",
                            "4 is the ones column dotted with itself, which is the number of measurements and sits at the top left.",
                            "14 is $\\sum x^2$, the bottom-right entry. The off-diagonal pairs two *different* columns, so it has one factor of $x$, not two.",
                            "3 is the largest $x$ value, not the sum of them. All four points contribute to every entry of $A^\\top A$.",
                        ],
                    },
                    {
                        "prompt": "The determinant, $4(14) - 6(6)$.",
                        "hole": "?",
                        "opts": ["20", "56", "92", "-20"],
                        "a": 0,
                        "why": "$56 - 36 = 20$. It is positive and it is small compared with the trace of 18, and those two facts together are what a badly conditioned $2\\times2$ looks like: the eigenvalues multiply to 20 and add to 18, so one of them has to be large and the other close to 1.",
                        "whys": [
                            "$56 - 36 = 20$. It is positive and it is small compared with the trace of 18, and those two facts together are what a badly conditioned $2\\times2$ looks like: the eigenvalues multiply to 20 and add to 18, so one of them has to be large and the other close to 1.",
                            "56 is $4 \\times 14$ with the off-diagonal product never subtracted. That would be the determinant only if the two columns were perpendicular, which is exactly what centring is about to arrange.",
                            "92 adds the two products instead of subtracting. A determinant of a $2\\times2$ is $ad - bc$; the sign is the whole content of it.",
                            "$-20$ has the subtraction the wrong way round. $A^\\top A$ can never have a negative determinant — it is positive semi-definite, so all its eigenvalues, and therefore their product, are $\\ge 0$.",
                        ],
                    },
                    {
                        "prompt": "The smaller eigenvalue, $(18 - 15.6205)/2$.",
                        "hole": "?",
                        "opts": ["1.190", "2.380", "1.500", "0.595"],
                        "a": 0,
                        "why": "$2.3795/2 = 1.190$. Check it against the determinant, which is free: $16.810 \\times 1.190 = 20.0$, and the two also add to 18. Both conditions hold, so the pair is right.",
                        "whys": [
                            "$2.3795/2 = 1.190$. Check it against the determinant, which is free: $16.810 \\times 1.190 = 20.0$, and the two also add to 18. Both conditions hold, so the pair is right.",
                            "2.380 is $18 - 15.6205$ with the division by two left out. Then the two eigenvalues would sum to 19.19 rather than to the trace of 18.",
                            "1.500 is what you get by rounding $\\sqrt{244}$ to 15 first. The eigenvalue is a difference of two nearly equal numbers, so it loses a digit for every digit you round away — which is itself a small illustration of what a large condition number does.",
                            "0.595 halves the answer a second time. Multiply it by 16.810 and you get 10, not the determinant of 20.",
                        ],
                    },
                    {
                        "prompt": "The condition number before centring.",
                        "hole": "?",
                        "opts": ["14.13", "20.0", "3.76", "1.19"],
                        "a": 0,
                        "why": "$16.810/1.190 = 14.13$. Read it as an amplification factor: a relative error of $10^{-6}$ in the data can come out as $1.4\\times10^{-5}$ in the coefficients. Harmless at this size, and it is not the point — the point is what it does when the columns get closer together.",
                        "whys": [
                            "$16.810/1.190 = 14.13$. Read it as an amplification factor: a relative error of $10^{-6}$ in the data can come out as $1.4\\times10^{-5}$ in the coefficients. Harmless at this size, and it is not the point — the point is what it does when the columns get closer together.",
                            "20.0 is the determinant, the *product* of the eigenvalues. The condition number is their ratio; the two are different questions and only one of them is scale-free.",
                            "3.76 is $\\sqrt{14.13}$, which is the condition number of $A$ itself. That is a meaningful number — $\\operatorname{cond}(A^\\top A) = \\operatorname{cond}(A)^2$ is exactly why forming the normal equations costs precision — but the drill asked about $A^\\top A$.",
                            "1.19 is the smaller eigenvalue on its own. A condition number is a ratio and can never be less than 1.",
                        ],
                    },
                    {
                        "prompt": "The off-diagonal entry after centring.",
                        "hole": "?",
                        "opts": ["0", "6", "3", "5"],
                        "a": 0,
                        "why": "$-1.5 - 0.5 + 0.5 + 1.5 = 0$. Subtracting the mean is precisely the operation that makes the $x$ column perpendicular to the ones column, because $\\sum(x_i - \\bar{x}) = 0$ is the definition of the mean rearranged. Two perpendicular columns give a diagonal $A^\\top A$ and two coefficients that no longer interfere with each other.",
                        "whys": [
                            "$-1.5 - 0.5 + 0.5 + 1.5 = 0$. Subtracting the mean is precisely the operation that makes the $x$ column perpendicular to the ones column, because $\\sum(x_i - \\bar{x}) = 0$ is the definition of the mean rearranged. Two perpendicular columns give a diagonal $A^\\top A$ and two coefficients that no longer interfere with each other.",
                            "6 is the uncentred sum. Shifting every $x$ down by the mean of 1.5 takes $\\sum x$ from 6 to $6 - 4(1.5) = 0$, which is the whole trick.",
                            "3 is $\\sum x$ halved. The four shifted values are $-1.5, -0.5, 0.5, 1.5$ and they cancel in pairs; nothing survives.",
                            "5 is $\\sum x'^2$, the bottom-right entry, already printed. That one is unaffected by sign because every term is squared.",
                        ],
                    },
                    {
                        "prompt": "The condition number after centring.",
                        "hole": "?",
                        "opts": ["1.25", "14.13", "0.80", "20.0"],
                        "a": 0,
                        "why": "A diagonal matrix has its diagonal for eigenvalues, so $5/4 = 1.25$ — down from 14.13 for one subtraction, with the fitted line, the residuals and every prediction left exactly where they were. Only the meaning of $c_0$ changed: it is now the height of the line at the *centre* of the data rather than at $x = 0$, which is also the coefficient you can actually determine from measurements taken around there.",
                        "whys": [
                            "A diagonal matrix has its diagonal for eigenvalues, so $5/4 = 1.25$ — down from 14.13 for one subtraction, with the fitted line, the residuals and every prediction left exactly where they were. Only the meaning of $c_0$ changed: it is now the height of the line at the *centre* of the data rather than at $x = 0$, which is also the coefficient you can actually determine from measurements taken around there.",
                            "14.13 was the uncentred figure. If centring left it unchanged the exercise would have no point; the whole reason to do it is that it moves.",
                            "0.80 is $4/5$, the ratio taken the other way up. A condition number is $\\lambda_{\\max}/\\lambda_{\\min}$ and is never below 1.",
                            "20.0 is the uncentred determinant. The centred determinant is $4 \\times 5 = 20$ as well, which is a nice illustration that the determinant is not what conditioning depends on: it is unchanged while the condition number falls by a factor of eleven.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "The characteristic polynomial, and the circuit it came from",
                "minutes": 13,
                "vars": ["s", "a", "b", "g", "h", "R", "L", "C"],
                "brief": r'''
Build the $2\times2$ eigenvalue rule from the definition, then point it at a series RLC and
watch the poles come out.

The eigenvalue is called $s$ here rather than $\lambda$, and not to save a keystroke: the
whole point of the last two steps is that the number you are solving for is the same $s$
that module 1 put into an impedance.

The general matrix is

$$A = \begin{bmatrix} a & b \\ g & h \end{bmatrix}$$

and the RLC, with state $x = (v_C, i_L)$, has

$$A = \begin{bmatrix} 0 & 1/C \\ -1/L & -R/L \end{bmatrix}$$
''',
                "steps": [
                    {
                        "prompt": "$Av = sv$ with $v \\ne 0$ is the same as $(A - sI)v = 0$, which needs $A - sI$ to be singular. Write $\\det(A - sI)$ for the general matrix, multiplied out as a polynomial in $s$.",
                        "answer": "s^2 - (a + h) s + a h - b g",
                        "hint": "$A - sI$ subtracts $s$ from each diagonal entry and leaves $b$ and $g$ alone. Then it is $(a-s)(h-s) - bg$.",
                        "deconstruct": [
                            "$A - sI = \\begin{bmatrix} a - s & b \\\\ g & h - s\\end{bmatrix}$ — the $I$ matters, because $s$ goes on the diagonal only.",
                            "Its determinant is $(a-s)(h-s) - bg = ah - as - hs + s^2 - bg$.",
                            "Collect: $s^2 - (a+h)s + (ah - bg)$, which is $s^2 - (\\operatorname{tr}A)s + \\det A$.",
                        ],
                    },
                    {
                        "prompt": "Now the circuit. Using that result, write the characteristic polynomial of $\\begin{bmatrix} 0 & 1/C \\\\ -1/L & -R/L\\end{bmatrix}$ in terms of $s$, $R$, $L$ and $C$.",
                        "answer": "s^2 + \\frac{R}{L} s + \\frac{1}{L C}",
                        "hint": "The trace is $0 + (-R/L)$ and the determinant is $(0)(-R/L) - (1/C)(-1/L)$. Mind the two minus signs in the determinant; they cancel.",
                        "deconstruct": [
                            "$\\operatorname{tr}A = -R/L$, so $-(\\operatorname{tr}A)s$ is $+\\frac{R}{L}s$.",
                            "$\\det A = 0 \\cdot (-R/L) - (1/C)(-1/L) = +\\frac{1}{LC}$, because a minus times a minus is a plus.",
                            "Assemble: $s^2 + \\frac{R}{L}s + \\frac{1}{LC}$ — which is the denominator of $1/(s^2LC + sRC + 1)$ after dividing through by $LC$.",
                        ],
                    },
                    {
                        "prompt": "Compare that with the standard form $s^2 + 2\\zeta\\omega_n s + \\omega_n^2$. Write $\\omega_n$ in terms of $L$ and $C$.",
                        "answer": "\\frac{1}{\\sqrt{L C}}",
                        "hint": "Match the constant terms: $\\omega_n^2 = 1/(LC)$.",
                        "deconstruct": [
                            "The constant term of the polynomial is $\\det A = 1/(LC)$, and in the standard form it is $\\omega_n^2$.",
                            "So $\\omega_n^2 = 1/(LC)$ and $\\omega_n = 1/\\sqrt{LC}$.",
                            "Note what it does not contain: $R$. The natural frequency belongs to the two energy-storage elements alone, and the resistor only decides how quickly the energy passing between them is lost.",
                        ],
                    },
                    {
                        "prompt": "The two roots coincide when the discriminant vanishes. Write the value of $R$ at which that happens, in terms of $L$ and $C$.",
                        "answer": "2 \\sqrt{\\frac{L}{C}}",
                        "hint": "Set $(R/L)^2 = 4/(LC)$ and solve for $R$.",
                        "deconstruct": [
                            "The discriminant of $s^2 + (R/L)s + 1/(LC)$ is $(R/L)^2 - 4/(LC)$.",
                            "Setting it to zero: $R^2/L^2 = 4/(LC)$, so $R^2 = 4L^2/(LC) = 4L/C$.",
                            "Hence $R = 2\\sqrt{L/C}$ — critical damping, $\\zeta = 1$, and the one case where the matrix has a repeated eigenvalue but only a single eigenvector.",
                        ],
                    },
                    {
                        "prompt": "Finally the eigenvector. Its first row reads $s\\,v_1 = v_2/C$, where $v_1$ is the capacitor voltage and $v_2$ the inductor current. Write the ratio $v_2/v_1$.",
                        "answer": "s C",
                        "hint": "Multiply both sides of $s v_1 = v_2/C$ by $C$.",
                        "deconstruct": [
                            "The first row of $Av = sv$ is $0\\cdot v_1 + (1/C)v_2 = s v_1$.",
                            "Rearranged, $v_2 = sC\\,v_1$, so the ratio is $sC$.",
                            "Which is the capacitor's own admittance $Y_C = sC$, evaluated at the pole. In a natural mode the current and the voltage of every element are related by that element's impedance at $s$ — the mode is the circuit obeying its own AC laws at a complex frequency instead of a real one.",
                        ],
                    },
                ],
                "closing": r'''
Two things are worth taking away from the shape of that, rather than from any one line.

The first is that $s^2 - (\operatorname{tr}A)s + \det A$ came out of nothing but "there is
a direction this map crushes". No circuit theory entered it, which is why the same
polynomial governs a mechanical resonance, a chemical rate pair, or a two-state control
loop. What the circuit supplied was the *entries*: $-R/L$ and $1/(LC)$, and with them the
fact that damping shows up in the trace and stored energy in the determinant.

The second is the last step. The eigenvector of the state matrix is not an abstract
direction — it is a ratio of a real current to a real voltage, and it equals the impedance
of the component joining them, evaluated at the eigenvalue. That is the seam where this
module joins module 1. The poles are the complex frequencies at which the circuit is
willing to sustain itself with nothing driving it, and the eigenvector is what it looks
like while it does.
''',
            },
            "lab": {
                "title": "Fitting a model to measurements",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Five short functions: two about eigenvalues, three about least squares.

- `design_matrix(x, deg)` returns the matrix whose column $j$ is $x^j$, for
  $j = 0 \dots \text{deg}$. Its first column is therefore all ones.
- `least_squares(A, y)` solves the normal equations $A^\top A c = A^\top y$ with
  `np.linalg.solve` and returns `c`.
- `fit_poly(x, y, deg)` puts the two together and returns the coefficients in
  **ascending** powers, so `[2.0, 3.0]` means $2 + 3x$.
- `time_constant(t, v)` fits a decaying exponential $v = Ae^{-t/\tau}$ by fitting a
  straight line to $\ln v$ and returns $\tau$. The slope of that line is $-1/\tau$.
- `eigenvalues(A)` returns the eigenvalues of `A` from `np.linalg.eigvals`, sorted by
  real part, smallest first.

## Why the normal equations and not the inverse

`A` is tall — more rows than columns — so it has no inverse and `np.linalg.solve(A, y)`
will refuse it outright. $A^\top A$, on the other hand, is square and (for independent
columns) invertible, and solving with it gives the vector that minimises the sum of the
squared residuals. That is the whole of least squares in one line of code and one line
of geometry: make the residual perpendicular to everything the columns of $A$ can
reach.

Use `np.linalg.solve` on the normal equations rather than forming an inverse. The two
are mathematically identical and the first is both faster and better behaved.
''',
                "files": [{"name": "main.py", "content": r'''
"""Eigenvalues, and fitting a model to more data than it has parameters."""

import numpy as np


def design_matrix(x, deg):
    """Matrix whose column j is x**j, for j = 0..deg."""
    # TODO: np.column_stack over a list comprehension of powers.
    return np.zeros((len(x), deg + 1))


def least_squares(A, y):
    """Solve the normal equations A^T A c = A^T y and return c."""
    # TODO: form both sides with the transpose, then np.linalg.solve.
    return np.zeros(np.asarray(A).shape[1])


def fit_poly(x, y, deg):
    """Least-squares polynomial coefficients, ascending powers."""
    # TODO: design_matrix, then least_squares.
    return np.zeros(deg + 1)


def time_constant(t, v):
    """Time constant of v = A exp(-t / tau), by fitting a line to log(v)."""
    # TODO: fit a straight line to np.log(v); the slope is -1/tau.
    return 0.0


def eigenvalues(A):
    """Eigenvalues of A, sorted by real part, smallest first."""
    # TODO: np.linalg.eigvals, then sort with np.argsort on the real parts.
    return np.array([])


if __name__ == "__main__":
    x = np.array([0.0, 1.0, 2.0, 3.0])
    print("fit of 2 + 3x:", fit_poly(x, 2.0 + 3.0 * x, 1))
    print("poles of the RLC as a state matrix:", eigenvalues([[0.0, 1.0], [-4e6, -1000.0]]))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Eigenvalues, and fitting a model to more data than it has parameters.

Verified by running this file:
    fit_poly on exact data for 2 + 3x returns [2. 3.]
    the state matrix [[0,1],[-4e6,-1000]] has eigenvalues -500 +/- 1936.4916731j,
    which are precisely the poles of the RLC filter built in module 2
"""

import numpy as np


def design_matrix(x, deg):
    """Matrix whose column j is x**j, for j = 0..deg."""
    x = np.asarray(x, dtype=float)
    return np.column_stack([x ** j for j in range(deg + 1)])


def least_squares(A, y):
    """Solve the normal equations A^T A c = A^T y and return c."""
    A = np.asarray(A, dtype=float)
    y = np.asarray(y, dtype=float)
    return np.linalg.solve(A.T @ A, A.T @ y)


def fit_poly(x, y, deg):
    """Least-squares polynomial coefficients, ascending powers."""
    return least_squares(design_matrix(x, deg), y)


def time_constant(t, v):
    """Time constant of v = A exp(-t / tau), by fitting a line to log(v)."""
    coeffs = fit_poly(t, np.log(np.asarray(v, dtype=float)), 1)
    return -1.0 / coeffs[1]


def eigenvalues(A):
    """Eigenvalues of A, sorted by real part, smallest first."""
    w = np.linalg.eigvals(np.asarray(A, dtype=float))
    return w[np.argsort(w.real)]


if __name__ == "__main__":
    x = np.array([0.0, 1.0, 2.0, 3.0])
    print("fit of 2 + 3x:", fit_poly(x, 2.0 + 3.0 * x, 1))
    print("poles of the RLC as a state matrix:", eigenvalues([[0.0, 1.0], [-4e6, -1000.0]]))
'''}],
                "hints": [
                    "`design_matrix` is `np.column_stack([x ** j for j in range(deg + 1)])` once `x` is a float array. Column 0 comes out as all ones because anything to the power 0 is 1.",
                    "In `least_squares`, `A.T @ A` and `A.T @ y` are the two sides; hand both to `np.linalg.solve`. Never call `np.linalg.inv`.",
                    "`time_constant` fits `np.log(v)` against `t` with `deg=1`. The result is `[ln A, -1/tau]`, so return `-1.0 / coeffs[1]`.",
                    "For `eigenvalues`, `np.argsort(w.real)` gives the order and `w[order]` applies it. Sorting the complex numbers directly is an error in NumPy, which is why the sort is on the real parts.",
                    "If a fit comes back wildly wrong, print `design_matrix(x, deg)` and look at it. A common slip is building the columns in descending powers, which returns the coefficients in the reverse order to the one the checks expect.",
                ],
                "tests": [
                    {"name": "the design matrix has a column of ones first", "code": r'''
A = design_matrix([0.0, 1.0, 2.0], 1)
want = np.array([[1.0, 0.0], [1.0, 1.0], [1.0, 2.0]])
assert A.shape == (3, 2), f"three points and degree 1 gives a 3x2 matrix, got {A.shape}"
assert np.allclose(A, want), f"expected\n{want}\ngot\n{A}"
B = design_matrix([2.0, 3.0], 2)
assert np.allclose(B, np.array([[1.0, 2.0, 4.0], [1.0, 3.0, 9.0]])), \
    f"columns must be x^0, x^1, x^2 in that order, got\n{B}"
'''},
                    {"name": "an exact fit is recovered exactly", "code": r'''
x = np.array([0.0, 1.0, 2.0, 3.0])
c = fit_poly(x, 2.0 + 3.0 * x, 1)
assert abs(c[0] - 2.0) < 1e-9 and abs(c[1] - 3.0) < 1e-9, \
    f"y = 2 + 3x should give [2, 3] in ascending order, got {c}"
q = fit_poly(np.array([-2.0, -1.0, 0.0, 1.0, 2.0]), np.array([4.0, 1.0, 0.0, 1.0, 4.0]), 2)
assert np.allclose(q, [0.0, 0.0, 1.0], atol=1e-9), \
    f"y = x^2 should give [0, 0, 1], got {q}"
'''},
                    {"name": "least squares balances errors it cannot remove", "code": r'''
x = np.array([0.0, 1.0, 2.0, 3.0])
y = 2.0 + 3.0 * x + np.array([1.0, -1.0, -1.0, 1.0])
c = fit_poly(x, y, 1)
assert abs(c[0] - 2.0) < 1e-9 and abs(c[1] - 3.0) < 1e-9, \
    f"these errors are balanced, so the fit should still be [2, 3], got {c}"
r = y - design_matrix(x, 1) @ c
assert abs(np.sum(r)) < 1e-9, f"the residual must be perpendicular to the ones column, got sum {np.sum(r)}"
assert abs(float(x @ r)) < 1e-9, f"and perpendicular to the x column, got {float(x @ r)}"
'''},
                    {"name": "a time constant out of measured decay", "code": r'''
t = np.array([0.0, 1e-3, 2e-3, 3e-3])
tau = time_constant(t, 5.0 * np.exp(-t / 0.002))
assert abs(tau - 0.002) < 1e-9, f"this data decays with tau = 2 ms, got {tau}"
t2 = np.linspace(0.0, 0.05, 11)
tau2 = time_constant(t2, 12.0 * np.exp(-t2 / 0.01))
assert abs(tau2 - 0.01) < 1e-9, f"and this one with tau = 10 ms, got {tau2}"
'''},
                    {"name": "eigenvalues, and the poles they turn out to be", "code": r'''
w = eigenvalues([[0.0, 1.0], [-3.0, -4.0]])
assert len(w) == 2, f"a 2x2 matrix has two eigenvalues, got {len(w)}"
assert abs(w[0].real + 3.0) < 1e-9 and abs(w[1].real + 1.0) < 1e-9, \
    f"lambda^2 + 4 lambda + 3 has roots -3 and -1, sorted that way, got {w}"
z = eigenvalues([[0.0, 1.0], [-4e6, -1000.0]])
assert abs(z[0].real + 500.0) < 1e-6, \
    f"the real part should be -zeta*wn = -500, got {z[0].real}"
assert abs(abs(z[0].imag) - 1936.4916731037085) < 1e-6, \
    f"the imaginary part should be wn*sqrt(1-zeta^2) = 1936.49, got {abs(z[0].imag)}"
'''},
                ],
            },
            "quiz": {
                "title": "Eigenvalues, fits and residuals",
                "minutes": 8,
                "questions": [
                    {
                        "q": "$Av = \\lambda v$ with $v \\ne 0$ says that:",
                        "opts": [
                            "the map leaves the direction of $v$ alone and only scales it",
                            "$v$ is in the null space of $A$",
                            "$A$ must be diagonal",
                            "$\\lambda$ is the determinant of $A$",
                        ],
                        "a": 0,
                        "why": r'''
An eigenvector is a direction the map does not turn. Everything else is consequence:
along that direction the matrix behaves like a single number, which is why writing a
system in its eigenvector coordinates decouples it into independent first-order pieces.
"$v$ is in the null space of $A$" is the special case $\lambda = 0$, not the
definition. The determinant is the
*product* of all the eigenvalues, and the trace is their sum.
''',
                    },
                    {
                        "q": "What are the eigenvalues of $A = \\begin{bmatrix}0 & 1\\\\ -3 & -4\\end{bmatrix}$?",
                        "opts": ["0 and $-4$", "$-2$ and $-2$", "$-1$ and $-3$", "1 and 3"],
                        "a": 2,
                        "why": r'''
The characteristic polynomial is $\lambda^2 - (\text{trace})\lambda + \det =
\lambda^2 + 4\lambda + 3$, whose roots are $-1$ and $-3$. Answering 0 and $-4$ reads the diagonal straight off, which is correct only for a
triangular matrix and wrong here. Notice what
this matrix is: the companion form of $\ddot{y}+4\dot{y}+3y=0$, and its eigenvalues are
exactly the poles of $1/(s^2+4s+3)$ from module 2.
''',
                    },
                    {
                        "q": "For $\\dot{x} = Ax$, the state returns to zero from every starting point exactly when:",
                        "opts": [
                            "every eigenvalue is negative in magnitude",
                            "every eigenvalue has a strictly negative real part",
                            "the trace of $A$ is zero",
                            "$A$ is invertible",
                        ],
                        "a": 1,
                        "why": r'''
Each eigenvalue contributes $e^{\lambda t}$, whose size is $e^{(\text{Re}\lambda)t}$,
so only the real part decides decay. "Negative in magnitude" is not even well formed — a magnitude is never negative, and eigenvalues are routinely complex. An invertible $A$ merely has no
zero eigenvalue, which does not stop the others sitting in the right half-plane; an
undamped oscillator has purely imaginary eigenvalues, a zero trace, and never settles.
''',
                    },
                    {
                        "q": "Least squares fits $Ac \\approx y$ when $A$ is tall by:",
                        "opts": [
                            "inverting $A$",
                            "minimising the largest single error",
                            "choosing $c$ to make the residual as large as possible",
                            "minimising the sum of the squared residuals, which gives $A^\\top A c = A^\\top y$",
                        ],
                        "a": 3,
                        "why": r'''
A tall $A$ has no inverse, which is precisely why the problem needs a different idea.
Minimising $\|Ac-y\|^2$ is a smooth problem with a closed-form answer: differentiate,
set to zero, and out come the normal equations. Geometrically, it projects $y$ onto the
column space of $A$ and leaves the residual perpendicular to it. Minimising the largest single error is a real and useful alternative criterion — but it is a different
method with no such formula.
''',
                    },
                    {
                        "q": "You fit a straight line to 50 measured (I, V) pairs. The residuals are small, but plotted against I they trace a smooth curve rather than scattering about zero. What does that tell you?",
                        "opts": [
                            "the model is wrong — a straight line cannot describe this data, and the mismatch is systematic rather than random",
                            "the measurements are too noisy",
                            "the fit is as good as it can be",
                            "the normal equations were solved incorrectly",
                        ],
                        "a": 0,
                        "why": r'''
Structure in the residuals is the signature of a missing term. Noise scatters; a real
physical effect the model omits — a component heating up, a diode drop, a small
nonlinearity — leaves a smooth pattern behind. Collecting more data will shrink the
random part and leave the pattern exactly where it is. Always plot the residuals: the
fitted parameters cannot tell you that the model itself was the wrong shape, and the
sum of squares alone cannot either.
''',
                    },
                ],
            },
        },
        # ---- M10 ----------------------------------------------------------
        {
            "title": "Network functions out of a matrix",
            "summary": "Nodal analysis in the s-domain gives a matrix of admittances. Its determinant is the characteristic polynomial — so the poles belong to the network, and only the numerator remembers where the probe was put.",
            "concepts": [
                "The stamping rule from the matrices module works unchanged in the s-domain, with $1/R$ replaced by an **admittance**: $Y_R = 1/R$, $Y_C = sC$, $Y_L = 1/(sL)$. The result is $Y(s)V(s) = I(s)$, whose entries are rational functions of $s$ rather than numbers.",
                "Cramer's rule divides every node voltage by $\\det Y(s)$, so **every node in the network has the same poles**. The poles are a property of the circuit; they do not depend on where you decided to put the probe, or on what you decided to drive it with.",
                "What the probe point changes is the numerator — the cofactor — and therefore the **zeros**. Move the output of a series RLC from across the capacitor to across the resistor and the two poles do not shift by a hair, but a zero appears at the origin and a low-pass becomes a band-pass.",
                "Clearing the fractions that $1/(sL)$ and $sC$ introduce turns $\\det Y(s)$ into an ordinary polynomial. Its roots are the poles, and its degree is the number of independent energy-storing components — which is why a purely resistive network has no poles and no transient at all.",
                "At one frequency this is arithmetic rather than algebra: substitute $s = j\\omega$, and $Y$ becomes a complex matrix to be solved once. An AC sweep is that solve repeated at every frequency point, which is exactly what a circuit simulator does and why its cost grows with the number of points and not with the algebra.",
            ],
            "build": {
                "title": "The same poles, a different probe",
                "minutes": 24,
                "brief": r'''
On the canvas: the 1 V source, the 0.1 H inductor and the 2.5 µF capacitor from the
filter built in module 2, wired in series and left unfinished.

Complete the loop with a **100 Ω resistor to ground, and take the output across the
resistor** rather than across the capacitor. Same three components, same values, same
$\det Y(s)$ — so the poles stay exactly where they were, at $-500 \pm j1936$. Only the
numerator changes, and with it everything about what the circuit is for.

## What you should expect to measure

- **nothing at DC.** The capacitor is in series with the signal path now, so the gain at
  1 Hz is essentially zero. The numerator has acquired a zero at the origin.
- **a gain of exactly 1 at 318.31 Hz**, with exactly zero phase shift. At $\omega_n$ the
  inductor's and capacitor's impedances cancel and the resistor is left facing the
  source alone, so the whole input appears across it. Not 0.707 of it, not 2 times it —
  exactly 1, and this holds for any damping.
- **a −3 dB bandwidth of 159.15 Hz**, from 248.53 Hz to 407.68 Hz. That width is $R/L$
  in rad/s, and the ratio of the centre frequency to it is $Q = 1/(2\zeta) = 2$.
- **a symmetric fall-off on a log axis.** A decade below the centre and a decade above
  it, the gain is the same number, and the skirts are 20 dB/decade in both directions
  rather than the 40 dB/decade of the low-pass. That is not one pole taking each side:
  at $\zeta = 0.25$ the poles are the complex pair $-500 \pm j1936$, and neither of them
  belongs to a side. Below resonance $|H| \approx \omega RC$, a rise supplied entirely
  by the zero at the origin; above it $|H| \approx R/(\omega L)$, which is the pair's
  $-40$ dB/decade net of that same zero's $+20$.

## Why this is the module's point in a schematic

The low-pass and this band-pass have identical denominators, because the denominator is
$\det Y(s)$ and $\det Y(s)$ knows nothing about the probe. Everything you can hear in the
difference between the two circuits lives in the numerator.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.1},
                        {"id": "p3", "kind": "C", "x": 10, "y": 5, "rot": 0, "value": 2.5e-6},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "L", "x": 6, "y": 5, "rot": 0, "value": 0.1},
                        {"id": "p3", "kind": "C", "x": 10, "y": 5, "rot": 0, "value": 2.5e-6},
                        {"id": "p4", "kind": "R", "x": 13, "y": 7, "rot": 1, "value": 100},
                        {"id": "p5", "kind": "GND", "x": 13, "y": 10},
                        {"id": "p6", "kind": "OUT", "x": 15, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [11, 5], "b": [13, 5]},
                        {"a": [13, 5], "b": [13, 6]},
                        {"a": [13, 8], "b": [13, 10]},
                        {"a": [13, 5], "b": [15, 5]},
                    ],
                },
                "checks": [
                    {"name": "one 1 V source drives the network", "code": r'''
c.assert(c.count('V') === 1,
  'Use exactly one voltage source, so that "the gain" means one thing. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 1, 0.001,
  'the source amplitude — the checks read the probe voltage as the gain, so the input must be 1 V');
'''},
                    {"name": "the zero at the origin: nothing gets through at DC", "code": r'''
const g = c.gain(1);
c.assert(g < 0.01,
  'A series capacitor puts a zero at the origin, so the gain at 1 Hz should be almost nothing. ' +
  'Measured ' + g.toFixed(4) + ' — a gain near 1 there means the probe is on the capacitor rather ' +
  'than on the resistor.');
'''},
                    {"name": "the gain is 1 and the phase 0 at 318.31 Hz", "code": r'''
c.close(c.gain(318.30988618379064), 1.0, 0.02,
  'the gain at the natural frequency, where the inductor and capacitor cancel and the resistor ' +
  'faces the source alone');
const ph = c.phase(318.30988618379064);
c.assert(Math.abs(ph) <= 3,
  'At resonance the circuit is purely resistive, so the output is exactly in phase with the input. ' +
  'Measured ' + ph.toFixed(1) + ' degrees.');
'''},
                    {"name": "the -3 dB bandwidth is 159.15 Hz, so Q is 2", "code": r'''
const lo = c.gain(248.5288490575785);
const hi = c.gain(407.68379214947385);
c.close(lo, 0.7071067811865476, 0.03,
  'the gain at 248.53 Hz, the lower -3 dB edge for a bandwidth of R/L');
c.close(hi, 0.7071067811865476, 0.03,
  'the gain at 407.68 Hz, the upper -3 dB edge');
'''},
                    {"name": "the fall-off is symmetric on a log axis: 20 dB/decade either way", "code": r'''
const below = c.gain(31.830988618379067);
const above = c.gain(3183.0988618379065);
c.assert(below < 0.1 && above < 0.1,
  'A decade either side of the centre the gain should be well down; measured ' +
  below.toFixed(4) + ' below and ' + above.toFixed(4) + ' above.');
c.close(below / above, 1.0, 0.05,
  'the ratio of the gains a decade below and a decade above the centre — a band-pass is symmetric ' +
  'on a logarithmic axis, and a low-pass is not remotely');
'''},
                ],
                "hints": [
                    "The order round the loop is source, inductor, capacitor, resistor, ground, with the probe on the node between the capacitor and the resistor.",
                    "Keep the inductor and capacitor at 0.1 H and 2.5 µF. Those two fix $\\omega_n = 1/\\sqrt{LC} = 2000$ rad/s, and the resistor alone sets the bandwidth.",
                    "The resistor is 100 Ω, the same value as the low-pass in module 2: $\\zeta = \\tfrac{R}{2}\\sqrt{C/L}$ has not changed, and neither has the denominator.",
                    "If the gain at 318 Hz comes out as 2 rather than 1, the probe is across the capacitor — that is the low-pass, and its peak at the natural frequency is $1/(2\\zeta)$.",
                    "If the gain at 1 Hz is 1 rather than 0, the resistor and capacitor have swapped places round the loop. The component nearest the ground end is the one you are measuring across.",
                ],
            },
            "derive": {
                "title": "The determinant is the characteristic polynomial",
                "minutes": 14,
                "vars": ["s", "L", "C", "R", "V_in", "H", "omega", "Y"],
                "brief": r'''
The circuit is the one from the build: a source at node 1, an inductor from node 1 to
node 2, a capacitor from node 2 to node 3, and a resistor from node 3 to ground, with
the output at node 3.

Node 1 is held by the source, so there are two unknowns and $Y$ is $2\times2$, indexed
by nodes 2 and 3. Stamp it the way you stamped $G$, with admittances in place of
conductances: $Y_R = 1/R$, $Y_C = sC$, $Y_L = 1/(sL)$.
''',
                "steps": [
                    {
                        "prompt": "Node 2 sits between the inductor and the capacitor. Its diagonal entry $y_{11}$ is the sum of the admittances touching it. Write it in terms of $s$, $L$ and $C$.",
                        "answer": "\\frac{1}{sL} + sC",
                        "hint": "Two components touch node 2: the inductor back to node 1 and the capacitor on to node 3. Add their admittances, not their impedances.",
                        "deconstruct": [
                            "The inductor's admittance is $1/(sL)$.",
                            "The capacitor's is $sC$.",
                            "The diagonal entry is always the sum of everything touching that node, whether or not the other end is grounded.",
                        ],
                    },
                    {
                        "prompt": "Write the off-diagonal entry $y_{12}$, which is minus the admittance shared between node 2 and node 3.",
                        "answer": "-sC",
                        "hint": "Only the capacitor bridges those two nodes, and the off-diagonal entry carries a minus sign.",
                        "deconstruct": [
                            "The one component between nodes 2 and 3 is the capacitor.",
                            "Its admittance is $sC$, and the stamping rule subtracts it from both off-diagonal positions.",
                            "So $y_{12} = y_{21} = -sC$, and $Y$ comes out symmetric exactly as $G$ did.",
                        ],
                    },
                    {
                        "prompt": "Node 3's diagonal entry is $sC + 1/R$. Write $\\det Y = y_{11}y_{22} - y_{12}y_{21}$ as a single fraction over $sLR$.",
                        "answer": "\\frac{s^2LC + sRC + 1}{sLR}",
                        "hint": "Expand the product first; the two $s^2C^2$ terms cancel, leaving $C/L + 1/(sLR) + sC/R$. Then put those three over the common denominator $sLR$.",
                        "deconstruct": [
                            "$\\left(\\frac{1}{sL} + sC\\right)\\left(sC + \\frac{1}{R}\\right) = \\frac{C}{L} + \\frac{1}{sLR} + s^2C^2 + \\frac{sC}{R}$.",
                            "Subtracting $y_{12}y_{21} = s^2C^2$ removes the only quadratic-in-$C$ term.",
                            "Over $sLR$: $\\frac{C}{L}$ becomes $sRC$, $\\frac{1}{sLR}$ becomes 1, and $\\frac{sC}{R}$ becomes $s^2LC$.",
                        ],
                    },
                    {
                        "prompt": "Cramer's rule gives $V_3 = \\dfrac{C\\,V_{in}/L}{\\det Y}$. Write $H(s) = V_3/V_{in}$ as a ratio of polynomials in $s$.",
                        "answer": "\\frac{sRC}{s^2LC + sRC + 1}",
                        "hint": "Dividing by the fraction from the previous step means multiplying by $sLR$. The $L$ cancels, leaving $sRC$ on top.",
                        "deconstruct": [
                            "$\\dfrac{C/L}{\\det Y} = \\dfrac{C}{L}\\cdot\\dfrac{sLR}{s^2LC + sRC + 1}$.",
                            "$\\dfrac{C}{L}\\cdot sLR = sRC$.",
                            "So the denominator is exactly the polynomial from the determinant, and the numerator is what the probe position contributed.",
                        ],
                    },
                    {
                        "prompt": "Compare it with the low-pass of module 2, $\\dfrac{1}{s^2LC+sRC+1}$: identical denominators, different numerators. With $L = 0.1$ H, $C = 2.5\\ \\mu$F and $R = 100\\ \\Omega$, at what angular frequency, in rad/s, is $|H|$ exactly 1?",
                        "answer": "2000",
                        "hint": "Put $s = j\\omega$. The denominator is $(1 - \\omega^2LC) + j\\omega RC$ and the numerator is $j\\omega RC$, so they agree in magnitude only when the real part of the denominator vanishes.",
                        "deconstruct": [
                            "$|H| = \\dfrac{\\omega RC}{\\sqrt{(1-\\omega^2LC)^2 + (\\omega RC)^2}}$, which equals 1 exactly when $1 - \\omega^2LC = 0$.",
                            "So $\\omega = 1/\\sqrt{LC} = 1/\\sqrt{0.1 \\times 2.5\\times10^{-6}}$.",
                            "$LC = 2.5\\times10^{-7}$, whose square root is $5\\times10^{-4}$ — and the answer is its reciprocal.",
                        ],
                    },
                ],
                "closing": r'''
Two things to take away. First, the denominator of every transfer function this network
can produce is $\det Y(s)$ cleared of its fractions — so a circuit has *its* poles, not
one set per measurement, and asking "where are the poles of the output across the
capacitor" is a slightly confused question.

Second, look at what $\det Y(s) = 0$ means physically. It is the value of $s$ at which
the matrix loses rank, so there is a non-zero $V$ with $Y(s)V = 0$: a set of node
voltages the network sustains with nothing driving it. That is what a natural frequency
*is*, and it is the same singularity the previous modules met at DC — the difference
being that here it happens at a particular complex $s$ rather than for the matrix as a
whole.
''',
            },
            "lab": {
                "title": "The AC sweep, one complex solve at a time",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
The matrices lab built a real conductance matrix out of resistors. This is the same
function with two lines changed, and the change turns it into a circuit simulator's
inner loop.

An element is a tuple `(kind, a, b, value)` with `kind` one of `'R'`, `'C'`, `'L'` and
nodes numbered from 1, with 0 for ground.

- `admittance(kind, value, w)` returns the complex admittance at angular frequency `w`:
  $1/R$, $j\omega C$, or $1/(j\omega L)$.
- `y_matrix(n, elements, w)` stamps them into an $n \times n$ **complex** array by
  exactly the rule you already know: add the admittance to both diagonal entries,
  subtract it from both off-diagonal entries, and skip node 0 throughout.
- `node_voltages(n, elements, fixed, w)` replaces the row of each fixed node with a 1 on
  its diagonal and its known voltage on the right, solves, and returns the voltages with
  0 prepended for ground.
- `response(n, elements, fixed, node, ws)` returns $|V_{\text{node}}|$ at each angular
  frequency in the array `ws`.

## The two lines that matter

`np.zeros((n, n))` becomes `np.zeros((n, n), dtype=complex)`, and the admittance of a
capacitor is `1j * w * value`. Everything else — the stamping, the fixed rows,
`np.linalg.solve` — is unchanged, because none of it ever cared whether the numbers were
real.

## What the checks are really asking

They run the *same three components* twice, wired as a low-pass and as a band-pass, and
compare both against the closed forms from the derivation. The low-pass peaks at 2 at
$\omega_n$ and the band-pass sits at exactly 1 there; the two are as different as
filters get, and they have the same denominator. If your solver reproduces both from one
piece of code, the claim of this module has been demonstrated rather than asserted.
''',
                "files": [{"name": "main.py", "content": r'''
"""An AC sweep: one complex matrix solve per frequency point."""

import numpy as np


def admittance(kind, value, w):
    """Complex admittance of one element at angular frequency w."""
    # TODO: 'R' -> 1/value, 'C' -> 1j*w*value, 'L' -> 1/(1j*w*value).
    return 0.0 + 0.0j


def y_matrix(n, elements, w):
    """The n x n complex admittance matrix, stamped element by element."""
    # TODO: start from np.zeros((n, n), dtype=complex); for each (kind, a, b, value)
    #       add its admittance to the diagonal of a and of b, and subtract it from
    #       both off-diagonal positions. Node 0 is ground and has no row or column.
    return np.zeros((n, n), dtype=complex)


def node_voltages(n, elements, fixed, w):
    """Node voltages at frequency w, with 0 first for ground. `fixed` is {node: volts}."""
    # TODO: build Y, replace each fixed node's row with a 1 on its diagonal and the
    #       known voltage on the right, solve, and prepend ground.
    return np.zeros(n + 1, dtype=complex)


def response(n, elements, fixed, node, ws):
    """|V| at `node` for each angular frequency in `ws`."""
    # TODO: one node_voltages call per frequency, taking the magnitude of the answer.
    return np.zeros(np.asarray(ws, dtype=float).shape)


if __name__ == "__main__":
    L, C, R = 0.1, 2.5e-6, 100.0
    low_pass = [("L", 1, 2, L), ("R", 2, 3, R), ("C", 3, 0, C)]
    band_pass = [("L", 1, 2, L), ("C", 2, 3, C), ("R", 3, 0, R)]
    ws = np.array([200.0, 2000.0, 20000.0])
    print("low-pass  |H|:", response(3, low_pass, {1: 1.0}, 3, ws))
    print("band-pass |H|:", response(3, band_pass, {1: 1.0}, 3, ws))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""An AC sweep: one complex matrix solve per frequency point.

Verified by running this file on the two circuits of this module, L = 0.1 H,
C = 2.5 uF, R = 100 ohms:
    low-pass  |H| at 200, 2000, 20000 rad/s -> 1.0088152, 2.0, 0.010088152
    band-pass |H| at the same three         -> 0.05044076, 1.0, 0.05044076
Both agree with the closed forms 1/(s^2LC+sRC+1) and sRC/(s^2LC+sRC+1) to 3e-16,
and the band-pass reaches exactly 1 at w = 2000 with zero phase.
"""

import numpy as np


def admittance(kind, value, w):
    """Complex admittance of one element at angular frequency w."""
    if kind == "R":
        return 1.0 / value
    if kind == "C":
        return 1j * w * value
    if kind == "L":
        return 1.0 / (1j * w * value)
    raise ValueError("unknown element kind " + str(kind))


def y_matrix(n, elements, w):
    """The n x n complex admittance matrix, stamped element by element."""
    Y = np.zeros((n, n), dtype=complex)
    for (kind, a, b, value) in elements:
        y = admittance(kind, value, w)
        if a:
            Y[a - 1, a - 1] += y
        if b:
            Y[b - 1, b - 1] += y
        if a and b:
            Y[a - 1, b - 1] -= y
            Y[b - 1, a - 1] -= y
    return Y


def node_voltages(n, elements, fixed, w):
    """Node voltages at frequency w, with 0 first for ground. `fixed` is {node: volts}."""
    Y = y_matrix(n, elements, w)
    rhs = np.zeros(n, dtype=complex)
    for node, volts in fixed.items():
        Y[node - 1, :] = 0.0
        Y[node - 1, node - 1] = 1.0
        rhs[node - 1] = complex(volts)
    return np.concatenate(([0.0 + 0.0j], np.linalg.solve(Y, rhs)))


def response(n, elements, fixed, node, ws):
    """|V| at `node` for each angular frequency in `ws`."""
    ws = np.asarray(ws, dtype=float)
    return np.array([abs(node_voltages(n, elements, fixed, w)[node]) for w in ws])


if __name__ == "__main__":
    L, C, R = 0.1, 2.5e-6, 100.0
    low_pass = [("L", 1, 2, L), ("R", 2, 3, R), ("C", 3, 0, C)]
    band_pass = [("L", 1, 2, L), ("C", 2, 3, C), ("R", 3, 0, R)]
    ws = np.array([200.0, 2000.0, 20000.0])
    print("low-pass  |H|:", response(3, low_pass, {1: 1.0}, 3, ws))
    print("band-pass |H|:", response(3, band_pass, {1: 1.0}, 3, ws))
'''}],
                "hints": [
                    "`1j` is Python's imaginary unit. `1j * w * value` is the capacitor; the inductor is the reciprocal of the same product with `value` being $L$, so it comes out negative imaginary.",
                    "The array must be created complex from the start: `np.zeros((n, n))` is real, and assigning a complex number into it discards the imaginary part with only a warning.",
                    "`if a:` and `if b:` are false exactly for node 0, which is the ground guard. The off-diagonal stamps need *both* ends to be real nodes, so guard them with `if a and b:`.",
                    "In `node_voltages`, replace the fixed rows after the whole matrix is stamped, never during — the stamping has to see every element before any row is overwritten.",
                    "If a sweep comes back flat at 1, check that the fixed node is the source node and that the element list actually reaches the node you are probing. A gap in the chain leaves a node connected to nothing, and the solver will say so.",
                ],
                "tests": [
                    {"name": "the three admittances", "code": r'''
assert abs(admittance('R', 100.0, 2000.0) - 0.01) < 1e-15, "a 100 ohm resistor is 10 mS at any frequency"
yc = admittance('C', 2.5e-6, 2000.0)
assert abs(yc - 0.005j) < 1e-15, f"j*w*C = j*2000*2.5e-6 = 0.005j, got {yc}"
yl = admittance('L', 0.1, 2000.0)
assert abs(yl + 0.005j) < 1e-15, f"1/(j*w*L) = 1/(200j) = -0.005j, got {yl}"
assert abs(admittance('C', 1e-6, 0.0)) < 1e-15, "a capacitor conducts nothing at DC"
'''},
                    {"name": "the stamp still builds the matrix it did for resistors", "code": r'''
Y = y_matrix(2, [('R', 1, 2, 20000.0), ('R', 2, 0, 10000.0)], 1000.0)
want = np.array([[5e-05, -5e-05], [-5e-05, 1.5e-04]])
assert Y.dtype == complex, f"the matrix must be complex, got dtype {Y.dtype}"
assert np.allclose(Y, want), f"a resistive network gives the same real matrix as before, expected\n{want}\ngot\n{Y}"
assert np.allclose(Y, Y.T), "and it is still symmetric"
'''},
                    {"name": "the low-pass matches its closed form", "code": r'''
L, C, R = 0.1, 2.5e-6, 100.0
lp = [('L', 1, 2, L), ('R', 2, 3, R), ('C', 3, 0, C)]
def exact_lp(w):
    s = 1j * w
    return abs(1.0 / (s * s * L * C + s * R * C + 1.0))
got = response(3, lp, {1: 1.0}, 3, [1.0, 200.0, 2000.0, 20000.0])
want = np.array([exact_lp(w) for w in [1.0, 200.0, 2000.0, 20000.0]])
assert np.allclose(got, want, rtol=1e-9), f"expected {want}, got {got}"
assert abs(got[2] - 2.0) < 1e-9, \
    f"at the natural frequency the low-pass peaks at 1/(2*zeta) = 2, got {got[2]}"
assert abs(got[0] - 1.0) < 1e-5, f"and it passes DC untouched, got {got[0]}"
'''},
                    {"name": "the band-pass has the same poles and a zero at the origin", "code": r'''
L, C, R = 0.1, 2.5e-6, 100.0
bp = [('L', 1, 2, L), ('C', 2, 3, C), ('R', 3, 0, R)]
v = node_voltages(3, bp, {1: 1.0}, 2000.0)
assert len(v) == 4, f"three nodes plus ground is four voltages, got {len(v)}"
assert abs(v[0]) < 1e-15, "node 0 is ground and must be exactly 0"
assert abs(v[3] - 1.0) < 1e-9, \
    f"at w = 2000 the reactances cancel and the whole input appears across R, so V3 = 1 + 0j; got {v[3]}"
lo = response(3, bp, {1: 1.0}, 3, [1.0])[0]
assert lo < 1e-3, f"a series capacitor blocks DC, so the gain at w = 1 should be tiny; got {lo}"
'''},
                    {"name": "the bandwidth is R/L, and the skirts are symmetric", "code": r'''
L, C, R = 0.1, 2.5e-6, 100.0
bp = [('L', 1, 2, L), ('C', 2, 3, C), ('R', 3, 0, R)]
edges = response(3, bp, {1: 1.0}, 3, [1561.5528128088303, 2561.5528128088303])
assert np.allclose(edges, 1.0 / np.sqrt(2.0), atol=1e-9), \
    f"the -3 dB edges sit at wn*(sqrt(1+z^2) -/+ z); expected 0.70711 at both, got {edges}"
assert abs((2561.5528128088303 - 1561.5528128088303) - R / L) < 1e-9, \
    "and their separation is R/L = 1000 rad/s"
skirts = response(3, bp, {1: 1.0}, 3, [200.0, 20000.0])
assert abs(skirts[0] - skirts[1]) < 1e-12, \
    f"a decade either side of the centre the gain is the same number; got {skirts}"
assert abs(skirts[0] - 0.050440760336032) < 1e-9, f"and that number is 0.05044, got {skirts[0]}"
'''},
                ],
            },
            "quiz": {
                "title": "Determinants, poles and where the probe goes",
                "minutes": 8,
                "questions": [
                    {
                        "q": "In s-domain nodal analysis the stamping rule uses:",
                        "opts": [
                            "impedances: $R$, $1/(sC)$ and $sL$",
                            "admittances: $1/R$, $sC$ and $1/(sL)$",
                            "the component values unchanged",
                            "resistances only, with the reactive parts added afterwards",
                        ],
                        "a": 1,
                        "why": r'''
Nodal analysis sums *currents* leaving a node, and current is admittance times voltage,
so admittances are what add up along a row. Impedances are what you use in a divider,
where the same current runs through everything and the voltages add instead. The two are
reciprocals, and using one where the other belongs is a reliable way to end up with a
high-pass when you wanted a low-pass — the shapes look plausible, which is what makes it
dangerous.
''',
                    },
                    {
                        "q": "$\\det Y(s) = 0$ at some particular value of $s$. That value is:",
                        "opts": [
                            "a zero of the transfer function",
                            "a frequency at which the circuit draws no current",
                            "a pole of every node voltage in the network",
                            "an arithmetic error",
                        ],
                        "a": 2,
                        "why": r'''
Cramer's rule divides every node voltage by $\det Y(s)$, so wherever the determinant
vanishes, every one of them blows up. It is not an error: it means $Y(s)$ has lost rank
at that $s$, so there is a non-zero set of node voltages satisfying $Y(s)V = 0$ — a
response the network can sustain with nothing driving it, which is precisely what a
natural frequency is. Zeros come from the *numerators*, which are cofactors and differ
from node to node.
''',
                    },
                    {
                        "q": "You move the probe of a series RLC from across the capacitor to across the resistor. The poles:",
                        "opts": [
                            "stay exactly where they were; only the zeros change",
                            "move, along with the zeros",
                            "move, while the zeros stay put",
                            "disappear, because the circuit is now resistive",
                        ],
                        "a": 0,
                        "why": r'''
The denominator of every transfer function this network can produce is $\det Y(s)$
cleared of fractions, and the determinant is built from the components and how they are
wired — not from where a probe was placed. What the probe changes is the cofactor on
top: across the capacitor the numerator is a constant and the circuit is a low-pass;
across the resistor it gains a factor of $s$, a zero at the origin, and the same two
poles now make a band-pass. Same poles, same ringing frequency, same settling time,
entirely different job.
''',
                    },
                    {
                        "q": "Clearing the fractions from $\\det Y(s)$ gives a polynomial. Its degree is:",
                        "opts": [
                            "the number of nodes",
                            "the number of resistors",
                            "always two",
                            "the number of independent energy-storing components",
                        ],
                        "a": 3,
                        "why": r'''
Each capacitor and inductor contributes one power of $s$, so the order of the network is
the count of them — "independent" because two capacitors in parallel are one capacitor,
and a loop made entirely of capacitors and voltage sources has one degree of freedom
fewer than it appears to. A purely resistive network has degree zero: no poles, no
transient, and an answer that appears the instant you apply the input. Resistors set
*where* the poles are, never how many there are.
''',
                    },
                    {
                        "q": "An AC sweep in a circuit simulator is:",
                        "opts": [
                            "a symbolic factorisation of $\\det Y(s)$",
                            "one complex matrix solve per frequency point, with $s = j\\omega$",
                            "a transient run with a sinusoid, repeated at each frequency",
                            "a table lookup against standard filter shapes",
                        ],
                        "a": 1,
                        "why": r'''
Substituting $s = j\omega$ turns the whole problem into complex arithmetic: build $Y$,
solve once, take the magnitude and angle of the node you care about, move to the next
point. A transient run with a sinusoid would also work and is enormously slower, because
at every frequency you would have to wait for the transient to die before the amplitude
meant anything. Symbolic factorisation is what you do by hand on a circuit that fits on
a page; nobody does it to a netlist with ten thousand nodes.
''',
                    },
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Identify an unknown circuit from its measured step response",
        "runtime": "python",
        "minutes": 260,
        "brief": r'''
Everything in this course pointing in one direction: someone hands you a black box and
a measurement, and you have to say what is inside it.

The box contains a series RLC low-pass — the circuit you built in module 2 — but with
unknown component values. The measurement is its step response, sampled at even
intervals. You have to recover $\omega_n$ and $\zeta$ from those samples, turn them
into component values, and state where the poles are.

## The idea that makes it a linear problem

The response satisfies

$$\ddot{y} + 2\zeta\omega_n\dot{y} + \omega_n^2 y = \omega_n^2 u$$

with $u = 1$ after the switch closes. Write $e = y - 1$, the error from the final
value, and the driving term disappears:

$$\ddot{e} + a\dot{e} + b e = 0, \qquad a = 2\zeta\omega_n,\quad b = \omega_n^2$$

Estimate $\dot{e}$ and $\ddot{e}$ from the samples by central differences,

```text
edot[i]  = (e[i+1] - e[i-1]) / (2h)
eddot[i] = (e[i+1] - 2 e[i] + e[i-1]) / h**2
```

and every interior sample then gives you one equation in the two unknowns $a$ and $b$:

$$\begin{bmatrix}\dot{e}_i & e_i\end{bmatrix}\begin{bmatrix}a\\b\end{bmatrix} = -\ddot{e}_i$$

Thousands of samples, two unknowns. That is a tall system with no exact solution, and
least squares is exactly the tool for it. Then $\omega_n = \sqrt{b}$ and
$\zeta = a/(2\omega_n)$.

## What you are given

`bench.py` is read-only and simulates the box. `bench.simulate(wn, zeta, t)` integrates
the differential equation with a fourth-order Runge–Kutta step and returns the samples
a measurement would produce. It is deliberately a *different* method from the closed
form you will write, so when the two agree that agreement means something.

## Suggested order

Get `rlc_model` and `component_values` working first — they are two lines each and they
let you check that your algebra from module 2 is right. Then `poles`, then
`step_samples`, and check it against `bench.simulate`; if those two disagree the fault
is in your closed form, not in the identification. Leave `identify` until last, and
test it on data you generated yourself with known values before trusting it on
anything else.

Only the standard library and NumPy. No `scipy`, no fitting library — the point is that
you can do this with a matrix and a solve.
''',
        "deliverables": [
            "`rlc_model(R, L, C)`, returning the pair $(\\omega_n, \\zeta)$ for a series RLC with the output across the capacitor, from the relations derived in module 2.",
            "`component_values(wn, zeta, L)`, the inverse design step: given the two behavioural numbers and a chosen inductor, return the resistance and capacitance that produce them.",
            "`poles(wn, zeta)`, returning the two complex poles $-\\zeta\\omega_n \\pm j\\omega_n\\sqrt{1-\\zeta^2}$ as a NumPy array.",
            "`step_samples(wn, zeta, t)`, the closed-form underdamped step response evaluated on an array of times, agreeing with the independent Runge–Kutta simulation in `bench.py` to better than $10^{-6}$.",
            "`identify(t, y)`, recovering $(\\omega_n, \\zeta)$ from uniformly sampled step-response data by central differences and a least-squares solve of the normal equations, to within 0.5% on clean data.",
        ],
        "constraints": [
            "NumPy and the standard library only. No scipy, no curve-fitting package, and no polynomial-fitting helper such as `numpy.polyfit` — build the design matrix and solve the normal equations yourself.",
            "Do not edit `bench.py`. It stands in for the instrument, and a solution that changes the instrument to suit the answer has proved nothing.",
            "`identify` may assume the samples are evenly spaced and that the step was applied at $t = 0$, but not that it already knows $\\omega_n$ or $\\zeta$ — no constants from the checks may appear in it.",
            "`step_samples` need only handle the underdamped case $0 < \\zeta < 1$.",
            "Every function must work for any values in range, not only the ones the checks happen to use.",
        ],
        "rubric": [
            {"criterion": "Model and inverse design", "weight": 20,
             "evidence": "rlc_model and component_values are exact inverses of each other, and reproduce the 100 Ω, 0.1 H, 2.5 µF filter from module 2 in both directions."},
            {"criterion": "Closed-form response", "weight": 25,
             "evidence": "step_samples matches the independent Runge–Kutta simulation across the whole record, and reproduces the textbook overshoot and time to peak for the damping used."},
            {"criterion": "Identification by least squares", "weight": 35,
             "evidence": "identify recovers ωn and ζ to within 0.5% on at least three different systems and two different sample spacings, using central differences and a solve of the normal equations rather than a fitting library."},
            {"criterion": "Poles and the round trip", "weight": 20,
             "evidence": "poles returns the correct conjugate pair, and identifying a simulated record then converting back through component_values returns the component values the record was generated from."},
        ],
        "hints": [
            "`component_values` is $C = 1/(\\omega_n^2 L)$ and $R = 2\\zeta\\sqrt{L/C}$. Compute $C$ first, then use it.",
            "In `step_samples`, let `wd = wn * np.sqrt(1 - zeta**2)`; the response is $1 - e^{-\\zeta\\omega_n t}\\left(\\cos\\omega_d t + \\frac{\\zeta}{\\sqrt{1-\\zeta^2}}\\sin\\omega_d t\\right)$.",
            "Central differences are only defined at interior samples, so all three arrays in `identify` must be trimmed to the same length: `e[1:-1]` pairs with differences built from `e[2:]` and `e[:-2]`.",
            "Build `A = np.column_stack([edot, e[1:-1]])` and solve `A.T @ A c = A.T @ (-eddot)`. Then `wn = np.sqrt(c[1])` and `zeta = c[0] / (2 * wn)`.",
            "If `identify` returns a plausible ωn but a ζ that is out by a factor of two, check whether you divided by $2\\omega_n$ or by $\\omega_n$ — the fitted coefficient is $2\\zeta\\omega_n$, not $\\zeta\\omega_n$.",
            "If it returns nonsense, print the first few entries of `edot` and `eddot`. The usual cause is dividing by `h` where the second difference needs `h**2`.",
        ],
        "files": [
            {"name": "bench.py", "ro": True, "content": r'''
"""The instrument. Do not edit.

`simulate` integrates

    y'' + 2 zeta wn y' + wn^2 y = wn^2,     y(0) = 0,  y'(0) = 0

with a fourth-order Runge-Kutta step and returns the samples an oscilloscope would
record. It is deliberately a different method from the closed form you are asked to
write, so that agreement between the two is evidence rather than a tautology.
"""

import numpy as np


def simulate(wn, zeta, t):
    """Step response sampled at the times in `t`, by RK4 on the state equations."""
    t = np.asarray(t, dtype=float)
    y = np.zeros(t.shape)
    state = np.array([0.0, 0.0])

    def deriv(s):
        return np.array([s[1], wn * wn * (1.0 - s[0]) - 2.0 * zeta * wn * s[1]])

    for k in range(1, len(t)):
        h = t[k] - t[k - 1]
        k1 = deriv(state)
        k2 = deriv(state + 0.5 * h * k1)
        k3 = deriv(state + 0.5 * h * k2)
        k4 = deriv(state + h * k3)
        state = state + (h / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
        y[k] = state[0]
    return y
'''},
            {"name": "main.py", "content": r'''
"""Identify an unknown series RLC from its measured step response."""

import numpy as np

import bench


def rlc_model(R, L, C):
    """Return (wn, zeta) for a series RLC with the output taken across C."""
    # TODO: wn = 1/sqrt(LC), zeta = (R/2) sqrt(C/L).
    return (0.0, 0.0)


def component_values(wn, zeta, L):
    """Return (R, C) that give this wn and zeta with the chosen inductor L."""
    # TODO: C from wn and L first, then R from zeta and the ratio L/C.
    return (0.0, 0.0)


def poles(wn, zeta):
    """The two closed-loop poles, as a NumPy array of complex numbers."""
    # TODO: -zeta*wn +/- j*wn*sqrt(1 - zeta**2).
    return np.array([])


def step_samples(wn, zeta, t):
    """Closed-form underdamped step response, evaluated on the array t."""
    # TODO: 1 - exp(-zeta wn t) (cos(wd t) + zeta/sqrt(1-zeta^2) sin(wd t)).
    return np.zeros(np.asarray(t, dtype=float).shape)


def identify(t, y):
    """Recover (wn, zeta) from evenly sampled step-response data."""
    # TODO: e = y - 1; central differences for edot and eddot; then least squares
    #       on [edot, e] c = -eddot, and read wn and zeta out of c.
    return (0.0, 0.0)


if __name__ == "__main__":
    t = np.linspace(0.0, 0.02, 4001)
    measured = bench.simulate(2000.0, 0.25, t)
    print("identified (wn, zeta):", identify(t, measured))
    print("poles:", poles(2000.0, 0.25))
    print("R, C for L = 0.1 H:", component_values(2000.0, 0.25, 0.1))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""Identify an unknown series RLC from its measured step response.

Verified by running this file:
    identify on bench.simulate(2000, 0.25) over 0..20 ms with 4001 samples returns
    wn = 1999.9895832701584, zeta = 0.25000078118388036 — five parts per million
    out on wn and three on zeta.
    The closed form and the Runge-Kutta simulation agree to 2.0e-13 over the record.
    component_values(2000, 0.25, 0.1) gives exactly (100.0, 2.5e-06).
"""

import numpy as np

import bench


def rlc_model(R, L, C):
    """Return (wn, zeta) for a series RLC with the output taken across C."""
    wn = 1.0 / np.sqrt(L * C)
    zeta = 0.5 * R * np.sqrt(C / L)
    return (wn, zeta)


def component_values(wn, zeta, L):
    """Return (R, C) that give this wn and zeta with the chosen inductor L."""
    C = 1.0 / (wn * wn * L)
    R = 2.0 * zeta * np.sqrt(L / C)
    return (R, C)


def poles(wn, zeta):
    """The two closed-loop poles, as a NumPy array of complex numbers."""
    wd = wn * np.sqrt(1.0 - zeta * zeta)
    return np.array([complex(-zeta * wn, wd), complex(-zeta * wn, -wd)])


def step_samples(wn, zeta, t):
    """Closed-form underdamped step response, evaluated on the array t."""
    t = np.asarray(t, dtype=float)
    root = np.sqrt(1.0 - zeta * zeta)
    wd = wn * root
    envelope = np.exp(-zeta * wn * t)
    return 1.0 - envelope * (np.cos(wd * t) + (zeta / root) * np.sin(wd * t))


def identify(t, y):
    """Recover (wn, zeta) from evenly sampled step-response data."""
    t = np.asarray(t, dtype=float)
    y = np.asarray(y, dtype=float)
    h = t[1] - t[0]
    e = y - 1.0

    edot = (e[2:] - e[:-2]) / (2.0 * h)
    eddot = (e[2:] - 2.0 * e[1:-1] + e[:-2]) / (h * h)

    A = np.column_stack([edot, e[1:-1]])
    rhs = -eddot
    c = np.linalg.solve(A.T @ A, A.T @ rhs)

    wn = np.sqrt(c[1])
    zeta = c[0] / (2.0 * wn)
    return (wn, zeta)


if __name__ == "__main__":
    t = np.linspace(0.0, 0.02, 4001)
    measured = bench.simulate(2000.0, 0.25, t)
    print("identified (wn, zeta):", identify(t, measured))
    print("poles:", poles(2000.0, 0.25))
    print("R, C for L = 0.1 H:", component_values(2000.0, 0.25, 0.1))
'''},
        ],
        "tests": [
            {"name": "the model and its inverse agree with module 2", "code": r'''
wn, zeta = rlc_model(100.0, 0.1, 2.5e-6)
assert abs(wn - 2000.0) < 1e-6, f"1/sqrt(0.1 * 2.5e-6) is 2000 rad/s, got {wn}"
assert abs(zeta - 0.25) < 1e-9, f"(R/2) sqrt(C/L) is 0.25 here, got {zeta}"
R, C = component_values(2000.0, 0.25, 0.1)
assert abs(R - 100.0) < 1e-6, f"the design step should return R = 100 ohms, got {R}"
assert abs(C - 2.5e-6) < 1e-12, f"and C = 2.5 uF, got {C}"
w2, z2 = rlc_model(R, 0.1, C)
assert abs(w2 - 2000.0) < 1e-6 and abs(z2 - 0.25) < 1e-9, \
    f"the two functions must be exact inverses; round trip gave ({w2}, {z2})"
'''},
            {"name": "the poles sit where the pole picture says", "code": r'''
p = poles(2000.0, 0.25)
assert len(p) == 2, f"a second-order system has two poles, got {len(p)}"
assert abs(p[0].real + 500.0) < 1e-9, f"the real part is -zeta*wn = -500, got {p[0].real}"
assert abs(abs(p[0].imag) - 1936.4916731037085) < 1e-6, \
    f"the imaginary part is wn*sqrt(1-zeta^2) = 1936.4917, got {abs(p[0].imag)}"
assert abs(p[0].imag + p[1].imag) < 1e-9, "the pair must be conjugate"
assert abs(abs(p[0]) - 2000.0) < 1e-9, \
    f"both poles are exactly wn from the origin, got {abs(p[0])}"
'''},
            {"name": "the closed form agrees with the instrument", "code": r'''
t = np.linspace(0.0, 0.01, 10001)
mine = step_samples(2000.0, 0.25, t)
theirs = bench.simulate(2000.0, 0.25, t)
err = float(np.max(np.abs(mine - theirs)))
assert err < 1e-6, \
    f"the closed form and the Runge-Kutta simulation must agree; largest gap {err}"
t2 = np.linspace(0.0, 0.05, 5001)
err2 = float(np.max(np.abs(step_samples(800.0, 0.6, t2) - bench.simulate(800.0, 0.6, t2))))
assert err2 < 1e-6, f"and again for a different, better damped system; largest gap {err2}"
'''},
            {"name": "the response has the overshoot the damping predicts", "code": r'''
t = np.linspace(0.0, 0.05, 50001)
y = step_samples(2000.0, 0.25, t)
assert abs(y[0]) < 1e-12, f"the response starts at 0, got {y[0]}"
assert abs(y[-1] - 1.0) < 1e-6, f"and settles at 1, got {y[-1]}"
want_peak = 1.0 + np.exp(-np.pi * 0.25 / np.sqrt(1.0 - 0.0625))
assert abs(float(np.max(y)) - want_peak) < 1e-4, \
    f"the overshoot should be exp(-pi zeta / sqrt(1-zeta^2)), peaking at {want_peak}, got {np.max(y)}"
t_peak = t[int(np.argmax(y))]
assert abs(t_peak - np.pi / 1936.4916731037085) < 2e-6, \
    f"the peak should arrive at pi/wd = 1.6223 ms, got {t_peak} s"
'''},
            {"name": "identification recovers the system it was given", "code": r'''
t = np.linspace(0.0, 0.02, 4001)
wn, zeta = identify(t, bench.simulate(2000.0, 0.25, t))
assert abs(wn - 2000.0) / 2000.0 < 0.005, f"expected wn near 2000 rad/s, got {wn}"
assert abs(zeta - 0.25) / 0.25 < 0.005, f"expected zeta near 0.25, got {zeta}"
'''},
            {"name": "it works on other systems and other sample spacings", "code": r'''
t2 = np.linspace(0.0, 0.03, 6001)
w2, z2 = identify(t2, bench.simulate(800.0, 0.6, t2))
assert abs(w2 - 800.0) / 800.0 < 0.005, f"expected wn near 800 rad/s, got {w2}"
assert abs(z2 - 0.6) / 0.6 < 0.005, f"expected zeta near 0.6, got {z2}"
t3 = np.linspace(0.0, 0.02, 1001)
assert abs((t3[1] - t3[0]) - 2e-05) < 1e-12, "this record is sampled every 20 us"
w3, z3 = identify(t3, bench.simulate(1500.0, 0.1, t3))
assert abs(w3 - 1500.0) / 1500.0 < 0.005, \
    f"expected wn near 1500 rad/s on the coarser 20 us grid, got {w3}"
assert abs(z3 - 0.1) / 0.1 < 0.005, \
    f"expected zeta near 0.1 on the coarser 20 us grid, got {z3}"
'''},
            {"name": "the whole round trip, from record back to components", "code": r'''
t = np.linspace(0.0, 0.02, 4001)
record = bench.simulate(2000.0, 0.25, t)
wn, zeta = identify(t, record)
R, C = component_values(wn, zeta, 0.1)
assert abs(R - 100.0) / 100.0 < 0.01, f"the box should come back as a 100 ohm resistor, got {R}"
assert abs(C - 2.5e-6) / 2.5e-6 < 0.01, f"and a 2.5 uF capacitor, got {C}"
p = poles(wn, zeta)
assert abs(p[0].real + 500.0) < 5.0, f"with poles near -500 +/- j1936, got {p[0]}"
'''},
        ],
    },
}
