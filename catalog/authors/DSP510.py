"""DSP510 — Multirate Signal Processing.

Same authoring rules as CTRL510, which is the template for this file:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

Every numeric threshold in a test below was produced by running the reference
solution, not estimated.
"""

COURSE = {
    "id": "DSP510",
    "title": "Multirate Signal Processing",
    "band": 3,
    "level": "Advanced",
    "prereqs": [],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◊",
    "summary": (
        "A sample rate is a choice, not a property of the signal, and changing it is "
        "the cheapest way to make a signal processing system affordable. This course "
        "builds rate change from the sampling theorem up: what decimation destroys, "
        "what interpolation invents, how polyphase decomposition removes the arithmetic "
        "that was never needed, and how the two operations combine into conversion by "
        "an arbitrary rational factor."
    ),
    "outcomes": [
        "Predict exactly where a component lands after decimation by M, and specify the anti-alias filter that prevents it.",
        "Explain zero insertion as a spectral operation, and size the anti-image filter that follows it.",
        "Decompose an FIR filter into polyphase branches and apply the noble identities to move filtering across a rate change.",
        "Build a rational rate converter L/M whose cost per output sample is one branch, not one filter.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that converts 44.1 kHz audio to 48 kHz with a polyphase commutator.",
    "reading": [
        "*Multirate Systems and Filter Banks*, Vaidyanathan — chapters 4 and 5 are the canonical treatment.",
        "*Multirate Signal Processing for Communication Systems*, harris — for the engineering view of the commutator.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Decimation and the folding it causes",
            "summary": "Keeping one sample in M is resampling at a lower rate. Anything above the new Nyquist limit does not disappear — it moves.",
            "concepts": [
                "Downsampling by `M` takes `y[n] = x[nM]`. Nothing is computed and nothing is filtered; samples are simply discarded.",
                "In frequency this stretches the spectrum by `M` and superimposes `M` shifted copies — the copies are the aliases.",
                "A component at normalised frequency $\\omega$ lands at $M\\omega$ modulo $2\\pi$, folded about $\\pi$.",
                "The anti-alias filter must therefore stop everything above $\\pi/M$ *before* the discard, not after.",
                "Filtering costs arithmetic that is then thrown away: the direct form computes `M-1` outputs out of every `M` only to discard them.",
            ],
            "read": [
                {
                    "title": "Where the 9 kHz went",
                    "minutes": 15,
                    "body": r'''
On the bench: a 48 kHz converter, and a generator putting two equal tones into it, one
at 1 kHz and one at 9 kHz. The stage downstream wants the stream at 12 kHz, so every
fourth sample is kept and the other three are dropped.

Play the result back at 12 kHz and there are still two tones. One of them is at 1 kHz,
where it was. The other is at 3 kHz, at the same amplitude as the tone that went in,
and nothing anywhere in the chain generated 3 kHz.

## The answer is already in the samples

No spectrum is needed to find it, because keeping every fourth sample means the values
that survive are the ones at indices $n = 4k$. Write those values out. A 9 kHz tone with
phase $\varphi$ is $\cos(2\pi \cdot 9000\,n/48000 + \varphi)$, and at $n = 4k$ that
argument is $2\pi(0.75)k + \varphi$.

Cosine has period $2\pi$ and is even, so subtract a whole turn per sample and flip the
sign of what is left:

$$\cos\!\big(2\pi(0.75)k + \varphi\big)
 = \cos\!\big(2\pi k - 2\pi(0.25)k + \varphi\big)
 = \cos\!\big(2\pi(0.25)k - \varphi\big)$$

and $0.25$ cycles per sample at 12 kHz is 3 kHz. The surviving samples of the 9 kHz tone
are, number for number, the samples of a 3 kHz tone with its phase turned round.

```python
import math

fs = 48000.0        # the rate the converter runs at
M = 4               # keep one sample in four
phi = 0.4           # the phase of the 9 kHz tone, in radians

kept = [math.cos(2 * math.pi * 9000.0 * (M * k) / fs + phi) for k in range(8)]
alias = [math.cos(2 * math.pi * 3000.0 * k / (fs / M) - phi) for k in range(8)]

print("every 4th sample of 9 kHz:", [round(v, 6) for v in kept])
print("3 kHz sampled at 12 kHz:  ", [round(v, 6) for v in alias])
print("same to within 1e-12:", max(abs(a - b) for a, b in zip(kept, alias)) < 1e-12)
```

Both lines print `[0.921061, 0.389418, -0.921061, -0.389418, ...]` and the comparison
prints `True`. Nothing was approximated and nothing leaked through a filter: the two
sequences are the same list of floats. That is what makes the 3 kHz tone impossible to
remove afterwards — it is not an artefact sitting on top of the wanted signal, it is
the whole of what the stream now contains at that frequency.

The minus sign in front of $\varphi$ is worth keeping. A folded component arrives with
its phase conjugated, which is why an aliased chirp sweeps the wrong way and why an
aliased transient looks time-reversed around its peak.

## From one tone to the rule

Redo that step with symbols instead of 9000. A component at $f_0$ in a sequence at
$f_s$ has normalised frequency $\omega = 2\pi f_0/f_s$ radians per sample, so the
sequence is $\cos(\omega n + \varphi)$. Keep one sample in $M$ and the surviving indices
are $n = kM$, giving $\cos(M\omega\, k + \varphi)$: the new sequence carries normalised
frequency $M\omega$.

Two facts about $\cos$ then finish it. Its period in $\omega$ is $2\pi$, so $M\omega$ is
read modulo $2\pi$; and it is even, so anything landing between $\pi$ and $2\pi$ is
reported at $2\pi$ minus itself, with the phase negated. Stretch by $M$, wrap at
$2\pi$, fold at $\pi$ — in that order, and none of the three steps is optional.

The bench numbers go through it in one line. $\omega = 2\pi(9000/48000) = 0.375\pi$;
$M\omega = 1.5\pi$, which is under $2\pi$ so the wrap does nothing; the fold gives
$2\pi - 1.5\pi = 0.5\pi$, and $0.5\pi$ radians per sample at 12 kHz is 3 kHz. The
derive unit *Where a component lands after decimation by M* walks the same journey
with $f_0$, $f_s$ and $M$ left as symbols and ends on the two numbers that matter.

Notice what the fold does to the map from input frequency to output frequency: it is
two-to-one. A 3 kHz tone and a 9 kHz tone both land at 3 kHz, and once they are in the
same sequence no operation can tell you how much of what you are looking at came from
which. The sandbox *A tone, a sample rate, and where the tone ends up* makes that
concrete — sweep the tone upward and watch the alias walk down to meet it, turn round
at the fold point, and walk back.

## Buying the band back

Since the loss happens at the moment of discarding, the only defence is upstream of it.
The decimated sequence can represent frequencies up to $f_s/2M$ — 6 kHz here — so
anything above that must be gone before the discard. In radians per sample of the
*original* sequence, where $f_s/2$ is $\pi$, the frequency $f_s/2M$ is $\pi/M$. That is
the entire specification of an anti-alias filter: stop by $\pi/M$.

Real filters do not stop anywhere; they roll off. The lab's `decimate` asks for a
cutoff of `0.45/M` cycles per sample rather than `0.5/M`, which at $M = 4$ and 48 kHz
is 5.4 kHz, leaving 600 Hz of room below the 6 kHz limit for the roll-off to happen in.
Whether 600 Hz is enough depends on how many taps you are willing to pay for, and the
question has an arithmetic answer:

```python
import math


def design_lowpass(numtaps, fc):
    """The lab's filter, in lists instead of arrays. fc is in cycles per sample."""
    if numtaps % 2 == 0:
        numtaps += 1
    h = []
    for i in range(numtaps):
        n = i - (numtaps - 1) / 2.0
        ideal = 2.0 * fc if n == 0.0 else math.sin(2.0 * math.pi * fc * n) / (math.pi * n)
        window = 0.54 - 0.46 * math.cos(2.0 * math.pi * i / (numtaps - 1))
        h.append(ideal * window)
    total = sum(h)
    return [v / total for v in h]


def gain_db(h, f):
    """20 log10 |H(f)| with f in cycles per sample."""
    re = sum(v * math.cos(2.0 * math.pi * f * i) for i, v in enumerate(h))
    im = sum(v * math.sin(2.0 * math.pi * f * i) for i, v in enumerate(h))
    return 20.0 * math.log10(math.hypot(re, im))


h = design_lowpass(101, 0.45 / 4)
print("taps:", len(h), " dc gain:", round(sum(h), 9))
for hz in (1000, 4000, 5400, 6000, 6600, 9000):
    print(f"{hz:6d} Hz {gain_db(h, hz / 48000.0):8.2f} dB")
```

The table it prints is the design, honestly stated: `0.00 dB` at 1 kHz and 4 kHz,
`-6.02 dB` at 5400 Hz, `-29.70 dB` at 6000 Hz, `-62.39 dB` at 6600 Hz and `-88.17 dB`
at 9 kHz.

Two of those readings do work. The $-6.02$ dB at the stated cutoff is not a failure: a
windowed sinc puts its half-amplitude point at the cutoff, with the transition band
straddling it, so `fc` names the middle of the slope rather than the end of the
passband. And $-29.70$ dB at 6 kHz says the 101-tap design has not finished rolling off
by the time it reaches the new Nyquist limit. A component sitting exactly at 6 kHz is
attenuated to about 3% and then folds onto itself. It is small, it is real, and it is
the price of 101 taps rather than 301.

## The measurement, end to end

Put the bench signal through both routes and read the two bins that matter. At 12 kHz a
240-sample block has bins 50 Hz apart, so 1 kHz is bin 20 exactly and 3 kHz is bin 60
exactly — no window and no leakage to argue about.

```python
import math


def design_lowpass(numtaps, fc):
    if numtaps % 2 == 0:
        numtaps += 1
    h = []
    for i in range(numtaps):
        n = i - (numtaps - 1) / 2.0
        ideal = 2.0 * fc if n == 0.0 else math.sin(2.0 * math.pi * fc * n) / (math.pi * n)
        window = 0.54 - 0.46 * math.cos(2.0 * math.pi * i / (numtaps - 1))
        h.append(ideal * window)
    total = sum(h)
    return [v / total for v in h]


def convolve(x, h):
    y = [0.0] * (len(x) + len(h) - 1)
    for i, xi in enumerate(x):
        for j, hj in enumerate(h):
            y[i + j] += xi * hj
    return y


def bin_amplitude(block, k):
    """Amplitude of the cosine that sits exactly in bin k of a length-N DFT."""
    N = len(block)
    re = sum(v * math.cos(2.0 * math.pi * k * i / N) for i, v in enumerate(block))
    im = sum(v * math.sin(2.0 * math.pi * k * i / N) for i, v in enumerate(block))
    return 2.0 * math.hypot(re, im) / N


fs = 48000.0
x = [math.cos(2 * math.pi * 1000.0 * i / fs) + math.cos(2 * math.pi * 9000.0 * i / fs)
     for i in range(1600)]

naive = x[::4]
guarded = convolve(x, design_lowpass(101, 0.45 / 4))[::4]

for name, y in (("discarded  ", naive), ("filtered   ", guarded)):
    block = y[60:300]            # 240 samples at 12 kHz, so the bins are 50 Hz apart
    print(name, "1 kHz (bin 20):", round(bin_amplitude(block, 20), 6),
          "  3 kHz (bin 60):", round(bin_amplitude(block, 60), 6))
```

Discarding alone gives `1.0` in bin 20 and `1.0` in bin 60: the 9 kHz tone arrives at
3 kHz at its original amplitude, undiminished. Filtering first gives `1.000049` in
bin 20 and `3.9e-05` in bin 60, and that second figure is $20\log_{10}(3.9\times10^{-5})
= -88$ dB, the same number the response table printed for 9 kHz. The alias did not
vanish; it was attenuated by a filter whose behaviour at 9 kHz you can look up before
you run anything.

## The mistake that costs the most

The tempting belief is that a lower sample rate *removes* what it cannot represent —
that 9 kHz has nowhere to go in a 12 kHz stream, so it goes away. It is tempting
because every other lossy operation in signal processing behaves that way, and because
the failure leaves no trace to contradict it: the output has the right length, the right
level, no clipping and no gap. What actually happens is relocation at full amplitude
into the middle of the band you were keeping, which is why `naive_decimate` exists in
the lab alongside `decimate` and why one of the checks insists its output peak stays
above 0.9. A test that only confirmed the good path would let you believe the bad one
was harmless.

The neighbouring confusion is worth separating out. Downsampling itself performs no
arithmetic — it is a selection, `x[::M]`, with no multiply and no add. The averaging
people associate with decimation is the anti-alias filter in front of it, a separate
block you chose. Keeping the two apart is what makes module 3 possible at all.

## Where this stops holding

The rule "stop everything above $\pi/M$" is the baseband case, and it is a sufficient
condition rather than a necessary one. What decimation actually requires is that no two
components land on top of each other, and a signal occupying a single band between
$k f_s/2M$ and $(k+1) f_s/2M$ for some integer $k$ already satisfies that. Such a signal
can be decimated by $M$ with a *bandpass* filter in front, and it lands at baseband
deliberately — this is bandpass sampling, and radio receivers live on it. The lowpass
at $\pi/M$ is the right answer when you know nothing about where the energy is.

The other limit is structural. Downsampling is not time-invariant: delay the input by
one sample and a different set of samples survives, so the output is a different
sequence rather than the old one delayed. There is no transfer function for it on its
own, and that is exactly why the noble identities in module 3 have to be stated as
conditions rather than assumed.

## What you are about to build

The lab *Decimate a signal without destroying it* asks for three functions:
`design_lowpass(numtaps, fc)` — the windowed sinc above, normalised so `sum(h)` is 1 so
that a constant passes through untouched; `naive_decimate(x, M)`, which is one slice;
and `decimate(x, M, numtaps=101)`, which filters at `0.45/M` and then takes every `M`-th
sample of the **full** convolution. Slicing `x` rather than the convolution is the error
the length check is there to catch. The checks then measure what this reading measured:
a tone at 0.02 cycles per sample comes through near amplitude 1, a tone at 0.20 comes
through below 0.02, and the same 0.20 tone through `naive_decimate` still peaks above
0.9, because it folded rather than left.
''',
                },
            ],
            "sandbox": {
                "title": "A tone, a sample rate, and where the tone ends up",
                "visualiser": "spectrum",
                "minutes": 8,
                "initial": {"fsig": 30, "fs": 200},
                "brief": r'''
Decimation is nothing more than sampling an already-sampled signal at a lower rate,
so the whole of it is visible in one picture: a tone, a rate, and the frequency the
samples actually imply.

The dots are what the system keeps. The pale curve is the truth. When the two stop
agreeing, an amber curve appears — that is the alias, the tone a listener downstream
would swear was there.
''',
                "notice": [
                    "Hold the tone at 30 Hz and drop the sample rate from 200 Hz to 50 Hz — a decimation by 4. Work out the new Nyquist limit before you move the slider, then check: 30 Hz is above 25 Hz, and the alias lands at 20 Hz.",
                    "Now set the tone to 90 Hz and the rate to 100 Hz. The alias appears at 10 Hz: $f_s - f_0$. That is the folding rule, and it is exactly what decimation by 2 from a 200 Hz rate would do to a 90 Hz component.",
                    "Sweep the tone slowly upward with the rate fixed at 200 Hz. The alias walks *down* as the tone walks up, meets it at 100 Hz, and turns round. Every alias frequency is claimed by two different input frequencies, which is why the loss is irreversible.",
                ],
            },
            "derive": {
                "title": "Where a component lands after decimation by M",
                "minutes": 12,
                "vars": ["f_0", "f_s", "f_2", "M", "N", "omega"],
                "brief": r'''
A signal is sampled at $f_s$ and contains a single tone at $f_0$, with
$f_0 < f_s/2$ so nothing is aliased yet. It is then decimated by an integer factor
$M$: every $M$-th sample is kept and the rest are discarded, with no filtering.

Work out where the tone ends up.
''',
                "steps": [
                    {
                        "prompt": "First, in the original sequence. Write the normalised angular frequency $\\omega$ of the tone in radians per sample, in terms of $f_0$ and $f_s$.",
                        "answer": "\\frac{2\\pi f_0}{f_s}",
                        "hint": "One cycle is $2\\pi$ radians, and the tone completes $f_0/f_s$ cycles between one sample and the next.",
                        "deconstruct": [
                            "Cycles per sample is $f_0/f_s$.",
                            "Radians per sample is $2\\pi$ times that.",
                        ],
                    },
                    {
                        "prompt": "After keeping one sample in $M$, the sequence carries a new sample rate $f_2$. Write it in terms of $f_s$ and $M$.",
                        "answer": "\\frac{f_s}{M}",
                        "hint": "The samples are the same distance apart in time as before; there are simply $M$ times fewer of them per second.",
                        "deconstruct": [
                            "The spacing between kept samples is $M/f_s$ seconds.",
                            "The rate is the reciprocal of the spacing.",
                        ],
                    },
                    {
                        "prompt": "Write the Nyquist limit of the decimated sequence — the highest frequency it can represent — in terms of $f_s$ and $M$.",
                        "answer": "\\frac{f_s}{2 M}",
                        "hint": "Half the new rate, and you already have the new rate.",
                        "deconstruct": [
                            "The new rate is $f_s/M$.",
                            "Nyquist is half of whatever the rate is.",
                        ],
                    },
                    {
                        "prompt": "Now suppose $f_0$ sits above that limit but below $f_2$. It folds about $f_2$. Write the apparent frequency in the decimated sequence, in terms of $f_s$, $M$ and $f_0$.",
                        "given": "The folding rule for a component between $f_2/2$ and $f_2$ is: apparent frequency $= f_2 - f_0$.",
                        "answer": "\\frac{f_s}{M} - f_0",
                        "hint": "Substitute the $f_2$ you found into the folding rule given above.",
                        "deconstruct": [
                            "The rule is $f_2 - f_0$.",
                            "And $f_2 = f_s/M$.",
                        ],
                    },
                    {
                        "prompt": "To stop that happening, a filter must run before the discard. Write its cutoff in normalised angular frequency, in terms of $M$.",
                        "answer": "\\frac{\\pi}{M}",
                        "hint": "The new Nyquist limit is $f_s/2M$; express that as radians per sample of the *original* sequence, where $f_s/2$ maps to $\\pi$.",
                        "deconstruct": [
                            "In the original sequence, $f_s/2$ is $\\pi$ radians per sample.",
                            "So $f_s/2M$ is $\\pi/M$.",
                        ],
                    },
                ],
                "closing": r'''
Two numbers came out of this and they are the whole of decimation: the new rate is
$f_s/M$, and the filter in front of it must stop at $\pi/M$. Everything after this
module is about paying less for that filter.
''',
            },
            "quiz": {
                "title": "Where a component lands after decimation",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A signal contains a component at normalised frequency $\\omega = 0.6\\pi$. It is decimated by $M = 4$ with no filter. Where does that component appear?",
                        "opts": ["$0.4\\pi$", "$0.6\\pi$", "$2.4\\pi$", "$0.15\\pi$"],
                        "a": 0,
                        "why": r"""
Decimation *stretches* the frequency axis by $M$: the component moves to
$M\omega = 2.4\pi$, and frequency is only defined modulo $2\pi$, so it reappears at
$2.4\pi - 2\pi = 0.4\pi$. It has not been removed and it has not been attenuated —
it has been *relocated*, into the middle of the band you were trying to keep. Dividing
by $M$ instead of multiplying is the natural guess, because the sample *rate* went
down; the frequency measured in radians per sample goes up for exactly that reason.
""",
                    },
                    {
                        "q": "What arithmetic does the downsampling operation $y[n] = x[nM]$ itself perform?",
                        "opts": [
                            "None — it selects samples and discards the rest",
                            "It averages each block of $M$ samples",
                            "It low-pass filters, then selects",
                            "It interpolates between the kept samples",
                        ],
                        "a": 0,
                        "why": r"""
Downsampling is pure selection: no multiply, no add, nothing computed. That is worth
being precise about, because the *decimator* people build does average — but the
averaging is the anti-alias filter in front, a separate block that you chose and can
change. Conflating the two is what leads to "decimation lost my signal" when the real
story is that no filter was ever put there. Keeping them apart is also what makes
polyphase possible in module 3.
""",
                    },
                    {
                        "q": "Before decimating by $M$, where must the anti-alias filter cut off?",
                        "opts": ["$\\pi/M$", "$\\pi M$", "$\\pi/2M$", "$\\pi$ — no filter is needed"],
                        "a": 0,
                        "why": r"""
After the stretch by $M$, anything originally above $\pi/M$ lands above $\pi$ and
folds. So the filter has to have removed it beforehand: cutoff $\pi/M$, which is the
new Nyquist limit referred back to the old rate. $\pi/2M$ is a factor of two too
conservative and throws away half the band you paid for; $\pi M$ is beyond $\pi$ and
therefore meaningless.
""",
                    },
                    {
                        "q": "A component sits above $\\pi/M$ and you decimate without filtering. What happens to it?",
                        "opts": [
                            "It folds down and lands somewhere inside the kept band",
                            "It is removed, because the new rate cannot represent it",
                            "It is attenuated in proportion to how far above the limit it is",
                            "Nothing — it stays where it was",
                        ],
                        "a": 0,
                        "why": r"""
Folding, not deletion. This is the single most expensive misconception in resampling,
because it makes the failure invisible: the output has the right length, the right
level, and a spurious component sitting in the middle of the wanted band which no
later processing can separate out. There is no gentle roll-off either — the fold is
exact and full amplitude. The only defence is the filter in front, which is why it is
not optional.
""",
                    },
                    {
                        "q": "Is downsampling a time-invariant operation?",
                        "opts": [
                            "No — delaying the input by one sample does not simply delay the output",
                            "Yes, like any LTI block",
                            "Yes, provided the anti-alias filter is linear phase",
                            "Only when $M$ is a power of two",
                        ],
                        "a": 0,
                        "why": r"""
Shift the input by one sample and a *different* set of samples survives, giving an
output that is not the old output delayed — it is a different signal. Downsampling is
periodically time-varying with period $M$, which is why you cannot describe it with a
transfer function on its own and why the noble identities in module 3 are worth
stating carefully: they say exactly when a filter may be moved across a rate change,
and the answer is not "always". Linear phase and powers of two change nothing here.
""",
                    },
                ],
            },
            "lab": {
                "title": "Decimate a signal without destroying it",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Three functions.

`design_lowpass(numtaps, fc)` returns a linear-phase FIR lowpass as a NumPy array.
Build it as a windowed sinc:

```text
n    = arange(numtaps) - (numtaps - 1)/2
h    = 2*fc * sinc(2*fc*n)                     # np.sinc(x) = sin(pi x)/(pi x)
w    = 0.54 - 0.46*cos(2*pi*arange(numtaps)/(numtaps - 1))    # Hamming
h    = h * w
h    = h / sum(h)                              # unit gain at DC
```

`fc` is a cutoff in **cycles per sample**, so 0.5 is Nyquist. Force `numtaps` odd
if it is even, so the filter has a whole-sample delay.

`naive_decimate(x, M)` keeps every `M`-th sample and does nothing else.

`decimate(x, M, numtaps=101)` filters first with a cutoff of `0.45/M` — the 0.45
rather than 0.5 leaves a tenth of the band as a transition region — and then keeps
every `M`-th sample of the **full** convolution `np.convolve(x, h)`.

The two decimators exist side by side so the checks can show you the difference.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def design_lowpass(numtaps, fc):
    """Windowed-sinc lowpass, unit gain at DC. fc is in cycles per sample."""
    if numtaps % 2 == 0:
        numtaps += 1
    # TODO: ideal response, Hamming window, then normalise so sum(h) == 1.
    return np.zeros(numtaps)


def naive_decimate(x, M):
    """Keep every M-th sample. No filtering at all."""
    x = np.asarray(x, dtype=float)
    # TODO: one slice.
    return x


def decimate(x, M, numtaps=101):
    """Anti-alias filter at 0.45/M, then keep every M-th sample."""
    x = np.asarray(x, dtype=float)
    # TODO: design the filter, convolve, then slice.
    return x


if __name__ == "__main__":
    h = design_lowpass(101, 0.1)
    print("taps:", len(h), "dc gain:", round(float(np.sum(h)), 6))
    n = np.arange(1200)
    slow = np.sin(2 * np.pi * 0.02 * n)
    fast = np.sin(2 * np.pi * 0.20 * n)
    print("slow tone after decimate:", round(float(np.max(np.abs(decimate(slow, 4)[60:-60]))), 4))
    print("fast tone after decimate:", round(float(np.max(np.abs(decimate(fast, 4)[60:-60]))), 4))
    print("fast tone after naive   :", round(float(np.max(np.abs(naive_decimate(fast, 4)))), 4))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def design_lowpass(numtaps, fc):
    """Windowed-sinc lowpass, unit gain at DC. fc is in cycles per sample."""
    if numtaps % 2 == 0:
        numtaps += 1
    n = np.arange(numtaps) - (numtaps - 1) / 2.0
    h = 2.0 * fc * np.sinc(2.0 * fc * n)
    w = 0.54 - 0.46 * np.cos(2.0 * np.pi * np.arange(numtaps) / (numtaps - 1))
    h = h * w
    return h / float(np.sum(h))


def naive_decimate(x, M):
    """Keep every M-th sample. No filtering at all."""
    x = np.asarray(x, dtype=float)
    return x[::M]


def decimate(x, M, numtaps=101):
    """Anti-alias filter at 0.45/M, then keep every M-th sample."""
    x = np.asarray(x, dtype=float)
    h = design_lowpass(numtaps, 0.45 / M)
    return np.convolve(x, h)[::M]


if __name__ == "__main__":
    h = design_lowpass(101, 0.1)
    print("taps:", len(h), "dc gain:", round(float(np.sum(h)), 6))
    n = np.arange(1200)
    slow = np.sin(2 * np.pi * 0.02 * n)
    fast = np.sin(2 * np.pi * 0.20 * n)
    print("slow tone after decimate:", round(float(np.max(np.abs(decimate(slow, 4)[60:-60]))), 4))
    print("fast tone after decimate:", round(float(np.max(np.abs(decimate(fast, 4)[60:-60]))), 4))
    print("fast tone after naive   :", round(float(np.max(np.abs(naive_decimate(fast, 4)))), 4))
'''}],
                "hints": [
                    "`np.sinc` already carries the $\\pi$: `np.sinc(x)` is $\\sin(\\pi x)/(\\pi x)$, so the ideal lowpass is `2*fc*np.sinc(2*fc*n)`.",
                    "Normalising by `sum(h)` rather than by an analytic constant makes the DC gain exactly one whatever the window does to it.",
                    "`np.convolve(x, h)` with no `mode` argument gives the full result, length `len(x)+len(h)-1`. Slice that, not `x`.",
                ],
                "tests": [
                    {"name": "the filter passes a constant untouched", "code": r'''
import numpy as np
_h = design_lowpass(101, 0.1)
assert len(_h) == 101, f"101 taps in, 101 taps out, got {len(_h)}"
assert abs(float(np.sum(_h)) - 1.0) < 1e-9, \
    f"sum(h) is the gain at DC and must be 1, got {float(np.sum(_h)):.6f} — divide by sum(h) at the end"
'''},
                    {"name": "the filter is symmetric, so its delay is the same at every frequency", "code": r'''
import numpy as np
_h = design_lowpass(101, 0.1)
assert float(np.max(np.abs(_h - _h[::-1]))) < 1e-12, \
    "a linear-phase FIR is symmetric about its centre tap — centre the sinc argument on (numtaps-1)/2"
'''},
                    {"name": "an even tap count is nudged to odd", "code": r'''
_h = design_lowpass(100, 0.1)
assert len(_h) == 101, \
    f"an even-length filter has a half-sample delay; nudge it to odd, got {len(_h)} taps"
'''},
                    {"name": "decimation returns one sample in M of the filtered signal", "code": r'''
import numpy as np
_x = np.zeros(1200)
_y = decimate(_x, 4, numtaps=101)
assert len(_y) == 325, \
    f"full convolution is 1200+101-1 = 1300 long, and one in four of that is 325, got {len(_y)} — did you slice x instead of the convolution?"
'''},
                    {"name": "a tone well below the new Nyquist limit survives", "code": r'''
import numpy as np
_n = np.arange(1200)
_x = np.sin(2 * np.pi * 0.02 * _n)
_y = decimate(_x, 4)
_amp = float(np.max(np.abs(_y[60:-60])))
assert 0.97 < _amp < 1.03, \
    f"0.02 cycles/sample becomes 0.08 after decimating by 4, well inside the passband, so the amplitude should stay near 1 — got {_amp:.4f}"
'''},
                    {"name": "a tone above the new Nyquist limit is removed rather than folded", "code": r'''
import numpy as np
_n = np.arange(1200)
_x = np.sin(2 * np.pi * 0.20 * _n)
_y = decimate(_x, 4)
_amp = float(np.max(np.abs(_y[60:-60])))
assert _amp < 0.02, \
    f"0.20 cycles/sample is above the post-decimation Nyquist limit of 0.125, so the anti-alias filter should have removed it — got {_amp:.4f}, which means it folded instead"
'''},
                    {"name": "throwing samples away without filtering aliases instead", "code": r'''
import numpy as np
_n = np.arange(1200)
_x = np.sin(2 * np.pi * 0.20 * _n)
_amp = float(np.max(np.abs(naive_decimate(_x, 4))))
assert _amp > 0.9, \
    f"unfiltered, that tone does not vanish — it reappears at full amplitude as an alias, so the peak should still be near 1, got {_amp:.4f}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Interpolation and the images it creates",
            "summary": "Inserting zeros changes the rate without changing the signal. The filter that follows is what turns the zeros into samples.",
            "concepts": [
                "Upsampling by `L` writes `x[n]` every `L`-th place and zero everywhere else. It adds no information and loses none.",
                "In frequency the spectrum is *compressed* by `L`, and $L-1$ extra copies — images — appear inside the new band.",
                "The anti-image filter has cutoff $\\pi/L$: the same number as the anti-alias filter, for a different reason.",
                "Zero insertion divides the mean signal power by `L`, so the filter needs a passband gain of `L` to preserve amplitude.",
                "Between the images, the filter is doing bandlimited interpolation — the zeros are replaced by the sinc-weighted sum of the neighbours.",
            ],
            "read": [
                {
                    "title": "Four tones where you sent one",
                    "minutes": 15,
                    "body": r'''
A telephone codec hands you speech at 8 kHz. The converter on the board runs at 32 kHz
and will not be persuaded otherwise, so the stream has to be brought up by a factor of
four. Write each sample down and follow it with three zeros: 128 samples become 512,
the same span of time now holds four times as many of them, and no sample that was
measured has been altered.

Send a 1 kHz tone through that and look at what comes out. A 512-sample block at 32 kHz
has bins 62.5 Hz apart, so 1 kHz is bin 16 exactly, 7 kHz is bin 112, 9 kHz is bin 144
and 15 kHz is bin 240 — every one of them an exact bin, with no window and no leakage to
argue about.

```python
import math


def bin_amplitude(block, k):
    N = len(block)
    re = sum(v * math.cos(2.0 * math.pi * k * i / N) for i, v in enumerate(block))
    im = sum(v * math.sin(2.0 * math.pi * k * i / N) for i, v in enumerate(block))
    return 2.0 * math.hypot(re, im) / N


L = 4
x = [math.cos(2 * math.pi * 1000.0 * j / 8000.0) for j in range(128)]

v = [0.0] * (len(x) * L)
v[::L] = x                              # zero insertion, and nothing else

# 512 samples at 32 kHz: the bins are 62.5 Hz apart
for hz in (1000, 5000, 7000, 9000, 15000):
    k = int(hz / 62.5)
    print(f"{hz:6d} Hz  bin {k:3d}  amplitude {bin_amplitude(v, k):.4f}")
```

One tone went in and four come out: `0.2500` at 1 kHz, `0.2500` at 7 kHz, `0.2500` at
9 kHz, `0.2500` at 15 kHz, and `0.0000` at 5 kHz where nothing lives. Played through the
converter that is a harsh metallic chord, not a 1 kHz tone, and the tone itself is a
quarter of the height it went in at.

## Why 7 kHz is in there

The three extra lines are not an error in the arithmetic and they are not noise. Ask
what the 32 kHz sequence would look like if the tone had been at 7 kHz instead. Its
samples at the positions where $v$ is non-zero, $n = 4k$, are

$$\cos\!\big(2\pi \cdot 7000 \cdot 4k/32000 + \psi\big) = \cos\!\big(2\pi(0.875)k + \psi\big)
 = \cos\!\big(2\pi(0.125)k - \psi\big)$$

by the same subtract-a-turn-and-flip step that folded the 9 kHz tone in the previous
module. And $2\pi(0.125)k$ is exactly the 1 kHz tone as the 8 kHz sequence recorded it.
So a 7 kHz tone at 32 kHz agrees with $v$ at every non-zero position, and the zeros in
between have no opinion about which of the two they belong to. The same holds at 9 kHz
and at 15 kHz.

That is the whole of imaging: zero insertion does not choose a signal. It produces a
sequence consistent with $L$ different tones at once, and the filter afterwards is what
picks one. Nothing was added to the signal that has to be subtracted again — the
alternatives were always there, and the earlier sequence had no way to express the
difference.

The compact statement is that inserting $L-1$ zeros leaves $V(\omega) = X(L\omega)$,
since the zeros contribute nothing to the transform sum and the surviving terms are
$x[k]e^{-j\omega kL}$. Reading $X$ at $L\omega$ compresses it into $[0, \pi/L]$ and, since
$X$ repeats every $2\pi$, plants a copy of it every $2\pi/L$ along the axis. The derive
unit *The gain and the images of an upsampler* does that solve step by step and lands on
the two image positions, $\omega_0/L$ and $(2\pi - \omega_0)/L$ — which for
$\omega_0 = 2\pi(0.125)$ and $L = 4$ are 1 kHz and 7 kHz at the 32 kHz rate.

## Where the quarter comes from

The `0.2500` is the second thing the block measured, and it has a shorter argument. Feed
in a constant 1.0 instead of a tone. Zero insertion turns it into `1, 0, 0, 0, 1, 0, 0,
0, ...`, whose mean is $1/4$. A filter's DC gain is $\sum_n h[n]$, and a filter with DC
gain 1 maps a mean of $1/4$ to a mean of $1/4$. So the output of a unit-gain
interpolation chain sits at a quarter of the input level, and the fix is one number:
give the filter $\sum_n h[n] = L$.

The energy did not go anywhere. Every measured sample is still present at its original
height, and there are now four times as many slots for it to be averaged over. On the
tone, the same factor shows up as four copies of amplitude $1/L$ rather than one copy of
amplitude 1 — and since the filter keeps one copy and discards three, the surviving
amplitude before compensation is $A/L$, which agrees with the DC argument.

## Specifying the filter, then measuring it

The baseband copy occupies $\omega < \pi/L$ and the nearest image begins above it, so any
cutoff in that neighbourhood separates them: $\pi/L$, which at $L = 4$ and 32 kHz is
4 kHz. The lab asks for `0.45/L` cycles per sample instead of `0.5/L`, which is 3.6 kHz,
buying 400 Hz of transition room below the boundary. The sandbox *What a higher rate
buys* walks up to that same boundary from the other side: raise the rate on a tone that
is already aliasing until the alias disappears, and the rate at which it goes is the rate
at which the nearest image stops landing inside the band you meant to keep.

Here is what 121 taps make of that specification:

```python
import math


def design_lowpass(numtaps, fc, gain=1.0):
    """The lab's filter: windowed sinc, scaled so that sum(h) is `gain`."""
    if numtaps % 2 == 0:
        numtaps += 1
    h = []
    for i in range(numtaps):
        n = i - (numtaps - 1) / 2.0
        ideal = 2.0 * fc if n == 0.0 else math.sin(2.0 * math.pi * fc * n) / (math.pi * n)
        window = 0.54 - 0.46 * math.cos(2.0 * math.pi * i / (numtaps - 1))
        h.append(ideal * window)
    scale = gain / sum(h)
    return [v * scale for v in h]


def gain_db(h, f, ref):
    re = sum(v * math.cos(2.0 * math.pi * f * i) for i, v in enumerate(h))
    im = sum(v * math.sin(2.0 * math.pi * f * i) for i, v in enumerate(h))
    return 20.0 * math.log10(math.hypot(re, im) / ref)


h = design_lowpass(121, 0.45 / 4, gain=4.0)
print("taps:", len(h), " dc gain:", round(sum(h), 6))
for hz in (1000, 3000, 3400, 3600, 4000, 4600, 7000):
    print(f"{hz:6d} Hz {gain_db(h, hz / 32000.0, 4.0):8.2f} dB")
```

It reports `dc gain: 4.0`, then `0.02 dB` at 3 kHz, `-1.40 dB` at 3400 Hz, `-6.01 dB`
at the stated cutoff of 3600 Hz, `-40.26 dB` at 4 kHz and `-57.35 dB` at 4600 Hz. The
readings in dB are taken against the passband gain of 4, so `0.02 dB` means the tone
comes out at the height it went in.

Now the two ends of the chain together, against the cheapest alternative to it — holding
each sample for four slots instead of stuffing zeros and filtering:

```python
import math


def design_lowpass(numtaps, fc, gain=1.0):
    if numtaps % 2 == 0:
        numtaps += 1
    h = []
    for i in range(numtaps):
        n = i - (numtaps - 1) / 2.0
        ideal = 2.0 * fc if n == 0.0 else math.sin(2.0 * math.pi * fc * n) / (math.pi * n)
        window = 0.54 - 0.46 * math.cos(2.0 * math.pi * i / (numtaps - 1))
        h.append(ideal * window)
    scale = gain / sum(h)
    return [v * scale for v in h]


def convolve(x, h):
    y = [0.0] * (len(x) + len(h) - 1)
    for i, xi in enumerate(x):
        for j, hj in enumerate(h):
            y[i + j] += xi * hj
    return y


def bin_amplitude(block, k):
    N = len(block)
    re = sum(v * math.cos(2.0 * math.pi * k * i / N) for i, v in enumerate(block))
    im = sum(v * math.sin(2.0 * math.pi * k * i / N) for i, v in enumerate(block))
    return 2.0 * math.hypot(re, im) / N


L = 4
x = [math.cos(2 * math.pi * 1000.0 * j / 8000.0) for j in range(256)]

stuffed = [0.0] * (len(x) * L)
stuffed[::L] = x
interpolated = convolve(stuffed, design_lowpass(121, 0.45 / L, gain=float(L)))

held = []
for value in x:
    held.extend([value] * L)            # sample and hold, the cheap alternative

for name, y in (("filtered", interpolated), ("held    ", held)):
    block = y[200:200 + 512]
    wanted = bin_amplitude(block, 16)
    image = bin_amplitude(block, 112)
    print(name, " 1 kHz:", round(wanted, 4),
          "  7 kHz image:", round(image, 4),
          f"  ({20 * math.log10(image / wanted):.1f} dB)")
```

The filtered route gives `1 kHz: 0.9999` and a 7 kHz image of `0.0008`, which is
`-62.0 dB`. Holding gives `1 kHz: 0.9761` and an image of `0.1508`, which is `-16.2 dB`.
The 0.25 has been paid back in both cases, so the level is not what separates them —
the difference is 46 dB of image, and 46 dB is the distance between inaudible and
unmistakable.

## The mistake, and why it is tempting

Look at the zero-stuffed waveform on a scope and it is indefensible: a spike, three
zeros, a spike, three zeros. It looks nothing like speech, and the first instinct is
that the zeros are wrong values which ought to be replaced by better guesses — repeat
the previous sample, or draw a straight line between neighbours. So people build the
hold and are surprised when the result sounds bright and gritty.

The measurement above says what happened. Repeating each sample four times is convolving
the zero-stuffed signal with a rectangle of four ones, which is a filter — a poor lowpass
whose response is a sinc. It droops across the passband, taking a 1 kHz tone to `0.9761`
where the design leaves it at `0.9999`, and its first null lands at 8 kHz rather than
inside the transition region, so the 7 kHz image
comes through only 16 dB down. Linear interpolation is the same story with a triangle
instead of a rectangle: better, still not a design. This is exactly what the blanks unit
*Interpolation, in four decisions* closes on, and it is why the zeros are correct — they
are the only insertion that asserts nothing, leaving the filter free to supply the one
bandlimited answer consistent with the samples you actually took.

The neighbouring slip is arithmetic rather than conceptual: applying the gain of $L$
twice, once by scaling `x` before the stuffing and once through the filter, or applying
it as $1/L$ because the level went down. The lab's constant-input check exists for that
— a DC input of 1 must come out at 1, and a mean near 0.25 or near 16 names which of the
two mistakes you made.

## Where this stops holding

Interpolation invents nothing. It evaluates the same bandlimited function on a finer
grid, so anything the 8 kHz sequence had already lost stays lost: if the codec aliased a
5 kHz component down to 3 kHz, upsampling to 32 kHz reproduces a 3 kHz component with
excellent fidelity. The rate went up and the information did not.

The response table also shows where the specification quietly stops being free.
Telephone speech runs to about 3.4 kHz, and 121 taps put that edge at `-1.40 dB` — an
audible tilt across the top of the band, caused by the transition region needing
somewhere to sit. Widening the passband towards 4 kHz makes the transition steeper and
the tap count larger, and tap count is arithmetic per sample at the *high* rate. That
tension is the reason module 3 exists.

Lastly, "bandlimited interpolation" is a promise about bandlimited signals. Feed a step
or a click through this chain and the output rings around the discontinuity, symmetric in
time, before the edge as well as after it. That ringing is not a defect in the filter; it
is what the bandlimited reconstruction of a step is. If the ringing is unacceptable the
answer is a different interpolation kernel with different guarantees, not more taps.

## What you are about to build

The lab *Interpolate by zero insertion and filtering* asks for `design_lowpass(numtaps,
fc, gain=1.0)` — the same windowed sinc as module 1, now scaled so `sum(h)` equals
`gain` rather than 1 — then `upsample(x, L)`, which allocates `len(x)*L` zeros and
writes `x` into every `L`-th slot, and `interpolate(x, L, numtaps=121)`, which upsamples
and convolves with a filter of cutoff `0.45/L` and gain `L`. Its last check is the
measurement above in miniature: a 0.2 cycles-per-sample tone upsampled by 3 puts its
image at 0.8/3, and that image has to be at least 40 dB down. Cutoff and gain are
independent, so a filter with the right cutoff and a gain of 1 passes the image check
and fails the amplitude one, which is the fastest way to find out which of the two you
left out.
''',
                },
            ],
            "quiz": {
                "title": "Zeros, images, and the gain that pays for them",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A 1 kHz tone recorded at 8 kHz is upsampled to 32 kHz by writing each sample followed by three zeros, and nothing else is done to it. A 512-point DFT of the result is taken. What does it show?",
                        "opts": [
                            "Four equal lines, at 1, 7, 9 and 15 kHz, each a quarter of the amplitude that went in",
                            "One line at 1 kHz, at the amplitude the tone went in with",
                            "Four lines at 1, 2, 3 and 4 kHz, spaced by the tone's own frequency, because the zeros carry the harmonics that a burst of one sample in four generates",
                            "One line at 4 kHz, the tone carried up the axis by the same factor of four that the rate went up by",
                        ],
                        "a": 0,
                        "why": r"""
Zero insertion produces a sequence that is consistent with $L$ different tones at once:
at the positions where the sequence is non-zero, a 7 kHz tone at 32 kHz gives exactly the
numbers a 1 kHz tone at 8 kHz gave, and so do 9 kHz and 15 kHz. Nothing chose between
them yet, so all four are present, each carrying $1/L$ of the amplitude because the same
total is now spread over four times as many samples. The tone does not move up the axis —
that happens under decimation, where the frequency in radians per sample is multiplied by
$M$; here it is divided by $L$, and the copies appear above it.
""",
                    },
                    {
                        "q": "The anti-image filter after an upsampler by $L$ is given a DC gain of $L$ rather than 1. What is that paying for?",
                        "opts": [
                            "Nothing was lost, so no gain is needed; the factor of $L$ compensates for the taps the window attenuates",
                            "The same total now sits in $L$ times as many samples, so a unit-gain filter returns it $L$ times too small",
                            "The energy carried off by the $L-1$ samples that the upsampler discarded from each group before the filter ran",
                            "The rate went up by $L$, and a filter's gain has to track the rate it runs at",
                        ],
                        "a": 1,
                        "why": r"""
Feed in a constant 1.0 and zero insertion makes it `1, 0, 0, 0, 1, 0, 0, 0, ...`, whose
mean is $1/L$. A filter's DC gain is $\sum_n h[n]$, so a unit-gain filter maps that mean
of $1/L$ straight through and the output sits at a quarter of the input level for $L=4$.
Setting $\sum_n h[n] = L$ restores it. Note what is *not* happening: an upsampler
discards nothing and loses no energy — every measured sample survives at its original
height, with more slots to average it over. That is also why the correction
is a multiplication by $L$ and never by $L^2$ or by $1/L$.
""",
                    },
                    {
                        "q": "Instead of stuffing zeros and filtering, each input sample is repeated $L$ times. In filtering terms, what has been built?",
                        "opts": [
                            "No filter at all — repetition copies values and computes nothing, so the spectrum is untouched",
                            "An ideal lowpass at $\\pi/L$, arrived at by a cheaper route than convolution",
                            "Convolution of the zero-stuffed signal with a rectangle of $L$ ones, whose response is a sinc",
                            "A first-order difference, because consecutive output samples are equal and their difference is zero",
                        ],
                        "a": 2,
                        "why": r"""
Holding a sample for $L$ slots is exactly convolving the zero-stuffed sequence with $L$
ones, and that rectangle has a sinc magnitude response. It is a filter, and being a poor
one is the problem rather than the alternative: measured on a 1 kHz tone taken from 8 kHz
to 32 kHz, it drops the tone from 0.9999 to 0.9761 and leaves the 7 kHz image only 16.2 dB
down, against 62 dB for the 121-tap design. The result sounds bright and gritty, which is
the images rather than distortion. Repetition is sometimes enough — it is what a
zero-order-hold DAC does — but it is a design decision with a measurable cost, not a
shortcut past one.
""",
                    },
                    {
                        "q": "An interpolator taking 8 kHz to 32 kHz is built with its lowpass cutting at 8 kHz rather than at 4 kHz. What reaches the output?",
                        "opts": [
                            "The wanted band only, because 8 kHz is above anything an 8 kHz input was able to carry in the first place",
                            "The wanted band at half amplitude, because a filter twice as wide passes twice as much of the noise floor",
                            "Nothing above 4 kHz at all, since the input had no energy up there to be passed on",
                            "The wanted band plus the image at 8 kHz minus the tone, which moves down the axis as the tone moves up",
                        ],
                        "a": 3,
                        "why": r"""
The first image sits at $2\pi/L$ minus the tone, which at these rates is 8 kHz minus the
tone's frequency: 7 kHz for a 1 kHz input, 6 kHz for a 2 kHz input. A cutoff at 8 kHz
passes all of it. The reasoning that feels safest is the one about the input's own
Nyquist limit, and it is a units error: 4 kHz was the ceiling of the 8 kHz sequence, but
the sequence being filtered runs at 32 kHz and the copies were planted after the rate
changed. The mirror movement is the giveaway on a spectrum analyser — sweep the input
tone upward and the image walks down to meet it.
""",
                    },
                    {
                        "q": "Does interpolation add information to the signal?",
                        "opts": [
                            "Yes — the filter estimates each missing value from the neighbours around it, which is more than the input stated",
                            "Only when the input was oversampled to start with, so that there is headroom for the new samples to describe",
                            "No — it evaluates the same bandlimited function on a finer grid of sample instants",
                            "Yes, in proportion to $L$: the output carries $L$ times as many samples",
                        ],
                        "a": 2,
                        "why": r"""
The filter does compute the intermediate values from the neighbours, and that is what
makes the first reading tempting — but those values were already determined. A
bandlimited function is fixed everywhere by its samples, so the interpolator is reading
off a function that was decided the moment the input was recorded, not choosing between
possibilities. The practical consequence is worth carrying: whatever the earlier rate
lost stays lost. If a component aliased down to 3 kHz before you got the file, upsampling
reproduces a 3 kHz component beautifully, and the rate has gone up while the information
has not.
""",
                    },
                    {
                        "q": "A component of the 8 kHz input sits at 3.9 kHz, close to that sequence's own limit. It is interpolated by 4 with the lab's filter, whose cutoff is at 3.6 kHz. What happens to it?",
                        "opts": [
                            "It comes through untouched: the cutoff is set at the 32 kHz rate, so 3.9 kHz is far inside the passband",
                            "It is attenuated, because the transition region has to sit somewhere and the top of the band is where it was put",
                            "It folds to 4.1 kHz, mirrored about the cutoff, in the way a component above the limit folds when a rate is reduced",
                            "It is reproduced once in each of the four images, at a quarter of its amplitude in each",
                        ],
                        "a": 1,
                        "why": r"""
The cutoff of `0.45/L` rather than `0.5/L` buys transition room by taking it out of the
top of the signal band, and the response table shows the bill: `-1.40 dB` at 3400 Hz and
`-6.01 dB` at 3600 Hz, so a 3.9 kHz component is well down the slope. Nothing folds — a
filter attenuates, and folding needs a rate change downward, which is module 1's
operation and not this one. Widening the passband towards 4 kHz is allowed, and it is
paid for in taps: a steeper transition costs a longer filter, and every one of those taps
runs at the high rate. That is the pressure module 3 relieves.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "What a higher rate buys",
                "visualiser": "spectrum",
                "minutes": 7,
                "initial": {"fsig": 90, "fs": 100},
                "brief": r'''
The same picture as the previous module, driven the other way. Start from a tone that
is already aliasing and raise the sample rate until it stops.

That extra headroom is exactly what an upsampler manufactures. What the picture does
not show is that upsampling fills the new headroom with images, which is the entire
job of the filter that follows it.
''',
                "notice": [
                    "The opening state is 90 Hz sampled at 100 Hz, and the amber alias sits at 10 Hz. Raise the rate to 200 Hz: the alias disappears and the dots trace the true wave.",
                    "Step the rate 100, 200, 300, 400 with the tone fixed. Each step is an upsample by an integer factor, and each one moves the tone to a smaller fraction of the band without changing the tone.",
                    "Now go the other way from 400 Hz down. The frequency at which the alias reappears is the same frequency where an interpolator's image would first fall inside the band you care about.",
                ],
            },
            "derive": {
                "title": "The gain and the images of an upsampler",
                "minutes": 12,
                "vars": ["L", "f_s", "omega", "omega_0", "k", "N"],
                "brief": r'''
Take a sequence $x[n]$ at rate $f_s$ containing a tone at normalised angular
frequency $\omega_0$. Build $v[n]$ by inserting $L-1$ zeros after every sample, so
that $v[nL] = x[n]$ and $v$ is zero at every other index.

Because the zeros contribute nothing to the sum, the transform of $v$ is
$V(\omega) = X(L\omega)$ — the same function, read $L$ times faster.
''',
                "steps": [
                    {
                        "prompt": "Write the sample rate of $v$ in terms of $L$ and $f_s$.",
                        "answer": "L f_s",
                        "hint": "The same span of time now holds $L$ times as many samples.",
                        "deconstruct": [
                            "One input sample became $L$ output samples.",
                            "The duration did not change, so the rate multiplied by $L$.",
                        ],
                    },
                    {
                        "prompt": "$V(\\omega) = X(L\\omega)$, so the tone appears wherever $L\\omega$ equals $\\omega_0$. Write that $\\omega$.",
                        "answer": "\\frac{\\omega_0}{L}",
                        "hint": "Solve $L\\omega = \\omega_0$ for $\\omega$. Nothing more.",
                        "deconstruct": [
                            "The peak of $X$ is at argument $\\omega_0$.",
                            "So the peak of $X(L\\omega)$ is where $L\\omega = \\omega_0$.",
                        ],
                    },
                    {
                        "prompt": "$X$ also repeats every $2\\pi$, so $X(L\\omega)$ has a peak wherever $L\\omega = 2\\pi - \\omega_0$ as well. Write that $\\omega$ — the first image.",
                        "answer": "\\frac{2\\pi - \\omega_0}{L}",
                        "hint": "Same solve as before, with $2\\pi - \\omega_0$ on the right instead of $\\omega_0$.",
                        "deconstruct": [
                            "The negative-frequency copy of the tone sits at $2\\pi - \\omega_0$ in $X$.",
                            "Divide by $L$ to find where it lands in $V$.",
                        ],
                    },
                    {
                        "prompt": "Every image lies above $\\omega_0/L$ and below $2\\pi$. Write the cutoff, in normalised angular frequency, of a filter that keeps the first copy and rejects every image, in terms of $L$.",
                        "answer": "\\frac{\\pi}{L}",
                        "hint": "The original band ran from $0$ to $\\pi$; after the compression by $L$ it runs from $0$ to $\\pi/L$.",
                        "deconstruct": [
                            "The whole baseband copy occupies $\\omega < \\pi/L$.",
                            "The nearest image starts just above $\\pi/L$.",
                        ],
                    },
                    {
                        "prompt": "The zeros carry no energy, so the interpolated signal comes out $L$ times too small unless the filter compensates. Write the DC gain $\\sum_n h[n]$ the filter needs.",
                        "answer": "L",
                        "hint": "One input sample in every $L$ output positions is non-zero, so the running average of $v$ is $1/L$ of the average of $x$.",
                        "deconstruct": [
                            "The mean of $v$ is the mean of $x$ divided by $L$.",
                            "To restore it, the filter must have DC gain $L$.",
                        ],
                    },
                ],
                "closing": r'''
Note that $\pi/L$ and a gain of $L$ are the only two specifications an interpolation
filter has. Everything else — length, window, ripple — is a cost decision, not a
correctness one.
''',
            },
            "blanks": {
                "title": "Interpolation, in four decisions",
                "minutes": 9,
                "caption": "interpolate.py — zero-stuff, filter, restore the level",
                "lang": "python",
                "brief": r"""
Upsampling is three lines and every one of them has a trap in it. Fill the holes, then
read the result: *put the samples where they belong, remove the copies that creates,
and put back the level the zeros took away.*
""",
                "listing": """import numpy as np
from scipy.signal import lfilter

# Interpolate x by L: zero-stuff, then filter.
y        = np.zeros(len(x) * L)
y[::L]   = ___                    # what goes in the non-zero slots
y        = lfilter(h, 1, y)       # h is a unit-DC-gain low-pass
y        = y * ___                # restore the level the zeros cost us

# the anti-image filter's cutoff, in radians per sample at the HIGH rate
wc = ___

# repeating each sample instead of zero-stuffing would be the same as
# filtering the zero-stuffed signal with ___
""",
                "blanks": [
                    {
                        "prompt": "Every L-th slot gets a real sample. Which one?",
                        "hole": "?",
                        "opts": ["x", "x * L", "x / L", "np.repeat(x, L)"],
                        "a": 0,
                        "why": "The original samples, unscaled. Zero insertion does not change any sample it keeps — the level correction is a separate step, and doing it here as well would apply it twice.",
                        "whys": [
                            "The original samples, unscaled. Zero insertion does not change any sample it keeps — the level correction is a separate step, and doing it here as well would apply it twice.",
                            "The scaling is real but it belongs after the filter, and putting it here as well multiplies the output by $L$ twice over.",
                            "Dividing goes the wrong way: the zeros already pulled the average down by $L$, so the correction multiplies.",
                            "That is sample-and-hold, not zero insertion, and it is the mistake the last blank is about — it leaves the images in, shaped by a sinc.",
                        ],
                    },
                    {
                        "prompt": "Three samples in four are now zero. What did that cost the level?",
                        "hole": "?",
                        "opts": ["L", "1 / L", "L ** 2", "1 — nothing was lost"],
                        "a": 0,
                        "why": "Zero-stuffing keeps the *energy* of each surviving sample but spreads it over $L$ times as many slots, so a unit-DC-gain filter returns a signal $L$ times too small. Multiplying by $L$ puts it back. Equivalently: give the filter a DC gain of $L$ and skip this line.",
                        "whys": [
                            "Zero-stuffing keeps the *energy* of each surviving sample but spreads it over $L$ times as many slots, so a unit-DC-gain filter returns a signal $L$ times too small. Multiplying by $L$ puts it back. Equivalently: give the filter a DC gain of $L$ and skip this line.",
                            "That is the direction of the loss, not the correction — it makes the output $L^2$ times too small.",
                            "Over-corrects by a factor of $L$. The zeros cost one factor of $L$, not two: the sample count went up by $L$ and each original sample still appears exactly once.",
                            "Something was: the mean of the zero-stuffed signal is $1/L$ of the original mean, because the same total is now spread over $L$ times as many samples.",
                        ],
                    },
                    {
                        "prompt": "Zero insertion creates L−1 extra copies of the spectrum. Where must the filter cut?",
                        "hole": "?",
                        "opts": ["np.pi / L", "np.pi * L", "np.pi / (2 * L)", "np.pi"],
                        "a": 0,
                        "why": "The compressed spectrum occupies up to $\\pi/L$ and the first image begins just above it, so $\\pi/L$ is exactly the boundary between what you keep and what you must remove. It is the same number as the anti-alias cutoff for decimation by $L$ — the two problems are mirror images.",
                        "whys": [
                            "The compressed spectrum occupies up to $\\pi/L$ and the first image begins just above it, so $\\pi/L$ is exactly the boundary between what you keep and what you must remove. It is the same number as the anti-alias cutoff for decimation by $L$ — the two problems are mirror images.",
                            "Above $\\pi$, which is not a frequency: at the high rate the axis still only runs to $\\pi$.",
                            "A factor of two too tight. It removes the images, but it also removes the top half of the signal you were interpolating.",
                            "Passes everything, so all $L-1$ images survive and the output is the zero-stuffed signal itself — audibly a harsh, bright copy of the original.",
                        ],
                    },
                    {
                        "prompt": "Sample-and-hold is not filter-free. What filter is it?",
                        "hole": "?",
                        "opts": [
                            "a length-L rectangular window",
                            "an ideal low-pass at pi/L",
                            "no filter at all",
                            "a first-order difference",
                        ],
                        "a": 0,
                        "why": "Holding each sample for $L$ slots is convolution with a rectangle of length $L$ — a zero-order hold. Its response is a sinc, which droops across the passband and leaves the images attenuated but present. It is cheap and it is sometimes enough; what it is not is equivalent to interpolation.",
                        "whys": [
                            "Holding each sample for $L$ slots is convolution with a rectangle of length $L$ — a zero-order hold. Its response is a sinc, which droops across the passband and leaves the images attenuated but present. It is cheap and it is sometimes enough; what it is not is equivalent to interpolation.",
                            "That is what you *wanted*; the rectangle is what you got. The gap between them is the sinc droop in the passband and the image leakage above it.",
                            "Repetition is a linear time-invariant operation on the zero-stuffed signal, so it certainly is a filter — that is precisely why it changes the spectrum.",
                            "A difference is a high-pass; holding is emphatically a low-pass. The sign of the error would be the opposite of what you hear.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Interpolate by zero insertion and filtering",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
`design_lowpass(numtaps, fc, gain=1.0)` is the same windowed sinc as the previous
lab, with one addition: normalise so that `sum(h) == gain` rather than `1`.

`upsample(x, L)` returns an array of length `len(x)*L` whose every `L`-th entry is
the corresponding entry of `x` and whose other entries are zero.

`interpolate(x, L, numtaps=121)` upsamples, then convolves with a lowpass of cutoff
`0.45/L` and gain `L`, returning the full convolution.

The last check measures the first image directly with an FFT and insists it is at
least 40 dB down. The reference solution puts it at roughly 66 dB down; without the
gain of `L` the amplitude check fails first, and without the filter the image is not
attenuated at all.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def design_lowpass(numtaps, fc, gain=1.0):
    """Windowed-sinc lowpass whose DC gain is `gain`. fc is in cycles per sample."""
    if numtaps % 2 == 0:
        numtaps += 1
    # TODO: ideal response, Hamming window, then scale so sum(h) == gain.
    return np.zeros(numtaps)


def upsample(x, L):
    """Insert L-1 zeros after every sample. Length becomes len(x)*L."""
    x = np.asarray(x, dtype=float)
    # TODO: allocate the zeros, then write x into every L-th slot.
    return x


def interpolate(x, L, numtaps=121):
    """Upsample by L, then remove the images with a lowpass of gain L."""
    x = np.asarray(x, dtype=float)
    # TODO: upsample, design at cutoff 0.45/L with gain L, convolve.
    return x


if __name__ == "__main__":
    print("upsample:", upsample([1.0, 2.0, 3.0], 3).tolist())
    h = design_lowpass(121, 0.15, gain=3.0)
    print("dc gain:", round(float(np.sum(h)), 6))
    n = np.arange(600)
    y = interpolate(np.sin(2 * np.pi * 0.05 * n), 4)
    print("interpolated peak:", round(float(np.max(np.abs(y[200:-200]))), 4))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def design_lowpass(numtaps, fc, gain=1.0):
    """Windowed-sinc lowpass whose DC gain is `gain`. fc is in cycles per sample."""
    if numtaps % 2 == 0:
        numtaps += 1
    n = np.arange(numtaps) - (numtaps - 1) / 2.0
    h = 2.0 * fc * np.sinc(2.0 * fc * n)
    w = 0.54 - 0.46 * np.cos(2.0 * np.pi * np.arange(numtaps) / (numtaps - 1))
    h = h * w
    return h * (gain / float(np.sum(h)))


def upsample(x, L):
    """Insert L-1 zeros after every sample. Length becomes len(x)*L."""
    x = np.asarray(x, dtype=float)
    out = np.zeros(len(x) * L)
    out[::L] = x
    return out


def interpolate(x, L, numtaps=121):
    """Upsample by L, then remove the images with a lowpass of gain L."""
    x = np.asarray(x, dtype=float)
    h = design_lowpass(numtaps, 0.45 / L, gain=float(L))
    return np.convolve(upsample(x, L), h)


if __name__ == "__main__":
    print("upsample:", upsample([1.0, 2.0, 3.0], 3).tolist())
    h = design_lowpass(121, 0.15, gain=3.0)
    print("dc gain:", round(float(np.sum(h)), 6))
    n = np.arange(600)
    y = interpolate(np.sin(2 * np.pi * 0.05 * n), 4)
    print("interpolated peak:", round(float(np.max(np.abs(y[200:-200]))), 4))
'''}],
                "hints": [
                    "`out = np.zeros(len(x)*L)` then `out[::L] = x` is the whole of `upsample`.",
                    "The gain scaling is one multiplication: `h * (gain / h.sum())`.",
                    "Cutoff and gain are independent choices, and the lab asks for `0.45/L` and `L` respectively — a filter with the right cutoff and a gain of 1 will pass the image check and fail the amplitude check.",
                ],
                "tests": [
                    {"name": "zero insertion puts the samples where they belong", "code": r'''
import numpy as np
_v = upsample([1.0, 2.0, 3.0], 3)
assert len(_v) == 9, f"three samples upsampled by three is nine samples, got {len(_v)}"
assert np.allclose(_v, [1, 0, 0, 2, 0, 0, 3, 0, 0]), \
    f"the samples go first in each group of L, with the zeros after them, got {_v.tolist()}"
'''},
                    {"name": "the filter carries the gain it was asked for", "code": r'''
import numpy as np
_h = design_lowpass(121, 0.15, gain=3.0)
assert abs(float(np.sum(_h)) - 3.0) < 1e-9, \
    f"sum(h) is the DC gain and was asked to be 3, got {float(np.sum(_h)):.6f}"
_h1 = design_lowpass(121, 0.15)
assert abs(float(np.sum(_h1)) - 1.0) < 1e-9, \
    f"the default gain is 1, got {float(np.sum(_h1)):.6f}"
'''},
                    {"name": "a constant interpolates to the same constant", "code": r'''
import numpy as np
_y = interpolate(np.ones(400), 3)
_mid = _y[200:-200]
assert float(np.max(np.abs(_mid - 1.0))) < 0.01, \
    f"a DC input must come out at the same level: without the gain of L it lands near 1/L, got {float(np.mean(_mid)):.4f}"
'''},
                    {"name": "a tone keeps its amplitude through interpolation", "code": r'''
import numpy as np
_n = np.arange(600)
_y = interpolate(np.sin(2 * np.pi * 0.05 * _n), 4)
_amp = float(np.max(np.abs(_y[200:-200])))
assert 0.97 < _amp < 1.03, \
    f"interpolation adds no energy and removes none from the baseband copy, so the peak should stay near 1, got {_amp:.4f}"
'''},
                    {"name": "the output is as long as the full convolution", "code": r'''
import numpy as np
_y = interpolate(np.zeros(600), 4, numtaps=121)
assert len(_y) == 600 * 4 + 121 - 1, \
    f"expected len(x)*L + numtaps - 1 = 2520, got {len(_y)} — return the full convolution, not a trimmed one"
'''},
                    {"name": "the first image is pushed at least 40 dB down", "code": r'''
import numpy as np
_n = np.arange(600)
_y = interpolate(np.sin(2 * np.pi * 0.2 * _n), 3)
_seg = _y[300:300 + 1024] * np.hanning(1024)
_Y = np.abs(np.fft.rfft(_seg))
_fr = np.fft.rfftfreq(1024, d=1.0)
_peak = _Y[int(np.argmin(np.abs(_fr - 0.2 / 3)))]
_image = _Y[int(np.argmin(np.abs(_fr - 0.8 / 3)))]
_db = 20.0 * np.log10(_image / _peak)
assert _db < -40.0, \
    f"the image of a 0.2 tone upsampled by 3 sits at 0.8/3 and must be filtered out; it is only {_db:.1f} dB down, so the anti-image filter is missing or its cutoff is too high"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Polyphase decomposition and the noble identities",
            "summary": "The arithmetic a decimator throws away can be identified in advance and never done. That is all polyphase is.",
            "concepts": [
                "$H(z) = \\sum_{m=0}^{M-1} z^{-m} E_m(z^M)$, where $e_m[n] = h[nM + m]$ — the taps dealt out into `M` hands.",
                "Noble identity, decimation: downsampling by `M` then $G(z)$ is identical to $G(z^M)$ then downsampling.",
                "Noble identity, interpolation: $G(z)$ then upsampling by `L` is identical to upsampling then $G(z^L)$.",
                "Applying the identities moves every filter to the *slow* side of the rate change, where each tap runs `M` times less often.",
                "The saving is a factor of `M` in multiplications and nothing at all in output — the two structures are exactly equal, sample for sample.",
            ],
            "read": [
                {
                    "title": "The three quarters of the arithmetic nobody wanted",
                    "minutes": 16,
                    "body": r'''
Put a counter on the multiplier in module 1's decimator. It runs at 48 kHz, its filter
has 101 taps, and it keeps one output in four. Every input sample costs 101 multiplies,
so the counter climbs by 4,848,000 every second — and three quarters of those products
end up in outputs that `[::4]` discards before anyone sees them. Three point six million
multiplies per second are being performed and then binned.

That is not an inefficiency to be shaved. The outputs being discarded are known in
advance, by index, before a single sample arrives, and the arithmetic that produces them
can be identified and never started.

## Which taps reach an output that survives

Take a six-tap filter and $M = 2$, so the surviving outputs are the even-numbered ones.
The convolution is $y[n] = \sum_k h[k]\,x[n-k]$, and at $n = 2m$ that is

$$y[2m] = h_0x[2m] + h_1x[2m{-}1] + h_2x[2m{-}2] + h_3x[2m{-}3] + h_4x[2m{-}4] + h_5x[2m{-}5]$$

Now sort the six terms by the parity of the input index they reach. The terms
$h_0, h_2, h_4$ touch $x$ at even indices; $h_1, h_3, h_5$ touch it at odd ones. Regroup
on that and nothing has been changed except the order of an addition:

$$y[2m] = \big(h_0x[2m] + h_2x[2m{-}2] + h_4x[2m{-}4]\big)
        + \big(h_1x[2m{-}1] + h_3x[2m{-}3] + h_5x[2m{-}5]\big)$$

Read the first bracket on its own. It is a three-tap convolution of the taps
$h_0, h_2, h_4$ with the sequence of even-indexed input samples — a filter running on
its own stream, at the output rate. The second bracket is a three-tap convolution of
$h_1, h_3, h_5$ with the odd-indexed samples. Two short filters, each stepping once per
output, and their sum is the output.

Nothing was approximated to get there. The regrouping is the associative law, and every
one of the six products in the original line appears once in the rearranged one:

```python
import math

h = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
x = [1.0, -2.0, 3.0, 0.0, 4.0, -1.0, 2.0, 5.0]
M = 2
mults = {"direct": 0, "branch": 0}


def tap(j, seq):
    return seq[j] if 0 <= j < len(seq) else 0.0


# the direct route: every output, then throw M-1 of every M away
full = []
for n in range(len(x) + len(h) - 1):
    acc = 0.0
    for k, hk in enumerate(h):
        acc += hk * tap(n - k, x)
        mults["direct"] += 1
    full.append(acc)
direct = full[::M]

# the branch route: only the outputs that survive, and only the taps that reach them
P = (len(x) + len(h) - 1 + M - 1) // M
branch = [0.0] * P
for m in range(M):
    e = h[m::M]
    for p in range(P):
        acc = 0.0
        for k, ek in enumerate(e):
            acc += ek * tap((p - k) * M - m, x)
            mults["branch"] += 1
        branch[p] += acc

print("branch 0 taps:", h[0::M], " branch 1 taps:", h[1::M])
print("direct then discard:", [round(v, 6) for v in direct])
print("one branch at a time:", [round(v, 6) for v in branch])
print("multiplies:", mults["direct"], "direct,", mults["branch"], "polyphase,",
      "for", len(direct), "output samples")
```

Both routes print `[1.0, 2.0, 10.0, 15.0, 32.0, 24.0, 30.0]`, and the counters read
`78 direct, 42 polyphase, for 7 output samples`. The branch taps are `[1.0, 3.0, 5.0]`
and `[2.0, 4.0, 6.0]` — the prototype dealt out like a pack of cards, each tap in exactly
one hand.

## The same thing in $z$

With $M$ branches instead of two, sort by the remainder on division by $M$: branch $m$
holds $e_m[n] = h[nM + m]$. Split the exponent as $z^{-(nM+m)} = z^{-nM}z^{-m}$ and the
$z^{-m}$ leaves the inner sum, since it has no $n$ in it:

$$H(z) = \sum_{m=0}^{M-1} z^{-m} E_m(z^M), \qquad E_m(z) = \sum_n h[nM+m]\,z^{-n}$$

The derive unit *Splitting a filter into M branches* takes those two steps in order and
then adds the third one. It is worth noticing what $E_m(z^M)$ means as a sequence: the
branch taps with $M-1$ zeros wedged between each pair, which is the same zero insertion
module 2 was about. The sandbox *What z to the M does to a pole* is showing the same
substitution acting on a pole rather than on a tap list — one pole at radius $r$ becomes
$M$ poles at radius $r^{1/M}$, and $r^{1/M} < 1$ exactly when $r < 1$.

## Why the filter may be moved at all

The 42 against 78 above came from noticing which products survive. The identity that
licenses doing it as a block diagram move is worth deriving rather than quoting, because
its shape is the whole content.

Ask what one sample of delay means on each side of a downsampler. Let $G(z) = z^{-1}$.
Downsample first and then delay: the result at index $n$ is $x[(n-1)M] = x[nM - M]$.
Delay first and then downsample: delaying by $M$ gives $v[n] = x[n-M]$, and downsampling
gives $v[nM] = x[nM - M]$. The same sequence. One output-sample delay on the slow side is
$M$ input-sample delays on the fast side, and no other number works.

Any FIR $G(z) = \sum_k g[k]z^{-k}$ is a weighted sum of delays, and both routes are
linear, so the result extends term by term: **$\downarrow M$ then $G(z)$ is
$G(z^M)$ then $\downarrow M$**. Read it in the direction that saves work — a filter
already sitting in the form $G(z^M)$ on the fast side may be moved to the slow side and
becomes $G(z)$ there, running once per output instead of once per input.

That is exactly the form each polyphase term is in. $H(z)$ before a downsampler is
$\sum_m z^{-m}E_m(z^M)$ before it; each $E_m(z^M)$ moves through and lands as $E_m(z)$;
the $z^{-m}$ stays behind on the fast side, where a delay costs no multiplier. Those $M$
delays feeding $M$ branches through a downsampler are the commutator: input sample $n$ is
handed to branch $(-n) \bmod M$, each branch fires once per output, and the $M$ branch
outputs are added.

Count the cost. Each branch holds $N/M$ taps and runs once per output, so an output costs
$N$ multiplies. The direct form costs $N$ per *input*, which is $NM$ per output. For the
bench decimator that is 101 × 12000 = 1,212,000 multiplies per second against 4,848,000 —
the factor of four that was going in the bin.

The upsampling identity is the mirror image and derives the same way: $G(z)$ then
$\uparrow L$ is $\uparrow L$ then $G(z^L)$, because a delay of one sample before the
zero-stuffing becomes a delay of $L$ afterwards. So an interpolator's filter can be
pulled back to the low rate, where each branch convolves the *input* directly and the
branch outputs are interleaved rather than summed. No array of zeros is ever built, and
none of the multiplications by zero that filled the direct route are performed.

## What a single branch is, and is not

```python
import math


def design_lowpass(numtaps, fc):
    if numtaps % 2 == 0:
        numtaps += 1
    h = []
    for i in range(numtaps):
        n = i - (numtaps - 1) / 2.0
        ideal = 2.0 * fc if n == 0.0 else math.sin(2.0 * math.pi * fc * n) / (math.pi * n)
        window = 0.54 - 0.46 * math.cos(2.0 * math.pi * i / (numtaps - 1))
        h.append(ideal * window)
    total = sum(h)
    return [v / total for v in h]


def response(taps, theta):
    """Complex frequency response at theta radians per sample."""
    re = sum(v * math.cos(theta * i) for i, v in enumerate(taps))
    im = -sum(v * math.sin(theta * i) for i, v in enumerate(taps))
    return complex(re, im)


M = 4
h = design_lowpass(101, 0.45 / M)
branches = [h[m::M] for m in range(M)]
print("branch lengths:", [len(e) for e in branches])

for hz in (1000, 6000, 9000):
    w = 2.0 * math.pi * hz / 48000.0
    whole = response(h, w)
    rebuilt = sum(complex(math.cos(-w * m), math.sin(-w * m)) * response(e, M * w)
                  for m, e in enumerate(branches))
    worst = max(abs(response(e, M * w)) for e in branches)
    print(f"{hz:5d} Hz  |H| {20 * math.log10(abs(whole)):7.2f} dB"
          f"   loudest branch {20 * math.log10(worst):6.2f} dB"
          f"   rebuilt error {abs(whole - rebuilt):.2e}")
```

It prints `branch lengths: [26, 25, 25, 25]` — 101 does not divide by 4, so one branch
carries an extra tap. Then, at the three frequencies module 1 measured:

```text
 1000 Hz  |H|    0.00 dB   loudest branch -12.03 dB   rebuilt error 2.78e-16
 6000 Hz  |H|  -29.70 dB   loudest branch -35.68 dB   rebuilt error 4.57e-16
 9000 Hz  |H|  -88.17 dB   loudest branch -12.03 dB   rebuilt error 7.64e-16
```

The `rebuilt error` column is the point of the exercise: $\sum_m e^{-jm\omega}E_m(e^{jM\omega})$
agrees with $H(e^{j\omega})$ to about $10^{-16}$, which is double-precision rounding and
nothing else. The decomposition is an identity, and the −29.70 dB and −88.17 dB are the
same numbers module 1's response table printed.

## The mistake, and why it is tempting

Look at the 9 kHz row again. The whole filter is 88 dB down there. The loudest of its
four branches is 12 dB down — the level a branch sits at across the entire band, because
each branch is close to a fractional-sample delay scaled by $1/M$.

That is what a 25-tap filter can do, and it is why the natural worry is wrong. The worry
is that splitting a 101-tap filter into four 25-tap filters must degrade it, since a
25-tap lowpass has a far worse stopband than a 101-tap one. It is tempting because the
premise is true: a 25-tap lowpass really is a much worse filter. The error is treating a
branch as a filter with a job of its own. No branch attenuates anything. The 88 dB of
stopband exists only in the sum, built by cancellation between four sequences that are
each near full amplitude at 9 kHz and in opposing phase. Take one branch out and you do
not get a slightly worse decimator, you get an unrecognisable one.

The consequence for debugging is worth holding on to: if a polyphase implementation
sounds wrong, the branch coefficients are almost never at fault. The phase alignment is —
which sample feeds which branch, and which output slot a branch result lands in. The
lab's checks are built around that: it compares against the direct route with a tolerance
of `1e-9` and tells you that any difference is a phase-alignment error, because the
algebra leaves no other possibility.

## Where this stops holding

The identity is exact in arithmetic, not in floating point. The branch route adds the
products in a different order, so the last bits differ — which is why the lab's tolerance
is `1e-9` rather than zero, and why a check written as `==` would fail on correct code.

The noble identity is a statement about a filter that has the form $G(z^M)$, and it is
false for one that does not. Moving $G(z)$ unchanged across a downsampler gives a
different system: it filters at the wrong rate, and the error is not small. The identity
also needs linearity and time-invariance on the block being moved, so a limiter, a
quantiser or a gain that follows the signal cannot be pushed across a rate change at all.

The saving is in multiplies per second and in nothing else. All $N$ taps are still
stored, so memory is unchanged; the group delay is still the prototype's $(N-1)/2$
samples at the fast rate, so latency is unchanged; and linear-phase tap symmetry, which
halves the multiplier count on its own, does not survive the split — each branch on its
own is asymmetric, and recovering that saving means folding taps across branches by hand.

Recursive filters are the honest gap. Everything above splits a polynomial, so it applies
to the numerator of an IIR filter and not to its feedback path, which cannot be run at
the low rate without first being rewritten so that its denominator is a polynomial in
$z^M$. That rewrite is possible and it costs extra numerator taps, which is a large part
of why production decimators are FIR.

## What you are about to build

The lab *Polyphase decimation and interpolation* asks for three functions.
`polyphase_split(h, M)` is one slice per branch, `h[m::M]`, and the check that catches a
wrong one is that the branch lengths must sum to `len(h)` for every $M$ — ten taps over
three branches is 4, 3, 3, matching the `[26, 25, 25, 25]` above.

`polyphase_decimate(x, h, M)` must equal `np.convolve(x, h)[::M]` exactly, without ever
computing a discarded output: build the phase sequence $u_m[p] = x[pM - m]$, convolve it
with branch $m$, and accumulate. `polyphase_interpolate(x, h, L)` must equal
`np.convolve(upsample(x, L), h)` without building the zero-stuffed array: convolve each
branch with `x` and interleave, since `conv(e_p, x)` already *is* the sequence of output
samples at positions $p, p+L, p+2L, \dots$. Both output lengths follow from the
convolutions they must match — `ceil((len(x)+len(h)-1)/M)` and `len(x)*L + len(h) - 1` —
and both are checked, because an off-by-one in the length is the same defect as an
off-by-one in the phase, caught one step earlier.
''',
                },
            ],
            "sandbox": {
                "title": "What z to the M does to a pole",
                "visualiser": "z-plane",
                "minutes": 8,
                "initial": {"r": 0.85, "th": 0.6},
                "brief": r'''
The noble identities replace $G(z)$ with $G(z^M)$. That substitution is not a small
one: a single pole at radius $r$ and angle $\theta$ becomes $M$ poles at radius
$r^{1/M}$ and angles $(\theta + 2\pi k)/M$.

Radius $r^{1/M}$ is closer to the unit circle than $r$, and this sandbox shows what
being closer to the circle costs. Move the radius and read the impulse response.
''',
                "notice": [
                    "Set the radius to 0.5 and note how fast the response dies. Now set it to $0.5^{1/2} \\approx 0.707$ — the same pole after $z \\to z^2$. The response takes about twice as many samples to fall as far, which is exactly the $M$-fold interpolation in the impulse response that $G(z^M)$ performs.",
                    "Push the radius past 1. The response grows without bound and the markers turn amber. This is why $G(z^M)$ is stable exactly when $G(z)$ is: $r^{1/M} < 1$ and $r < 1$ say the same thing.",
                    "Hold the radius and sweep the angle from 0 to $\\pi$. The oscillation in the response speeds up; at $\\theta = \\pi$ the response alternates sign every sample. Under $z \\to z^M$ that angle becomes $\\pi/M$, which is the cutoff every filter in this course has been given.",
                ],
            },
            "derive": {
                "title": "Splitting a filter into M branches",
                "minutes": 14,
                "vars": ["z", "n", "m", "M", "N", "h", "E"],
                "brief": r'''
Take an FIR filter $H(z) = \sum_{n=0}^{N-1} h[n] z^{-n}$ with $N$ taps, and sort the
taps by the remainder of their index on division by $M$. Every tap belongs to exactly
one of the $M$ classes, so nothing is lost and nothing is counted twice:

$$H(z) = \sum_{m=0}^{M-1} \ \sum_{n} h[nM + m]\, z^{-(nM+m)}$$
''',
                "steps": [
                    {
                        "prompt": "Branch $m$ is the subsequence $e_m[n] = h[?]$. Write that index in terms of $n$, $M$ and $m$.",
                        "answer": "n M + m",
                        "hint": "The taps whose index leaves remainder $m$ on division by $M$ are $m$, $m+M$, $m+2M$, and so on.",
                        "deconstruct": [
                            "The first tap of the branch is $h[m]$.",
                            "Each subsequent one is $M$ further along.",
                        ],
                    },
                    {
                        "prompt": "Pull the common factor out of the inner sum, so that it becomes a polynomial in $z^{-M}$ multiplied by one delay. Write that delay factor as a power of $z$.",
                        "answer": "z^{-m}",
                        "hint": "$z^{-(nM+m)} = z^{-nM} \\cdot z^{-m}$, and only the second factor is free of $n$.",
                        "deconstruct": [
                            "Split the exponent: $-(nM+m) = -nM - m$.",
                            "The $z^{-m}$ does not depend on $n$, so it comes out of the sum.",
                        ],
                    },
                    {
                        "prompt": "A filter of $N$ taps splits into $M$ branches of equal size when $M$ divides $N$. Write the number of taps in one branch.",
                        "answer": "\\frac{N}{M}",
                        "hint": "Every tap goes to exactly one branch, and the branches are the same size.",
                        "deconstruct": [
                            "There are $N$ taps in total.",
                            "They are shared equally between $M$ branches.",
                        ],
                    },
                    {
                        "prompt": "Now the noble identity. Downsampling by $M$ and then applying $G(z)$ gives the same sequence as applying $G$ first and then downsampling — provided $G$ is evaluated at a different argument. Write that argument in terms of $z$ and $M$.",
                        "answer": "z^{M}",
                        "hint": "One sample of delay after the downsampler is $M$ samples of delay before it.",
                        "deconstruct": [
                            "A delay of one output sample corresponds to $M$ input samples.",
                            "So $z^{-1}$ on the slow side is $z^{-M}$ on the fast side, and $G(z)$ becomes $G(z^M)$.",
                        ],
                    },
                ],
                "closing": r'''
Put the two together. $H(z)$ before a downsampler is $\sum_m z^{-m} E_m(z^M)$ before
the downsampler; the noble identity pulls each $E_m(z^M)$ through it and leaves
$E_m(z)$ on the slow side. Each branch of $N/M$ taps now runs once per *output*
sample instead of once per input sample, and the total is $N$ multiplications per
output rather than $N$ per input.
''',
            },
            "quiz": {
                "title": "Polyphase, and what it is allowed to move",
                "minutes": 7,
                "questions": [
                    {
                        "q": "In $H(z) = \\sum_{m} z^{-m}E_m(z^M)$, what is the impulse response of branch $E_m$?",
                        "opts": ["$h[nM + m]$", "$h[n + m]$", "$h[nM]$ for every $m$", "$h[m]$"],
                        "a": 0,
                        "why": r"""
Every $M$-th tap, starting at offset $m$. The decomposition is nothing more than
dealing the taps of $h$ into $M$ piles like a pack of cards, so the branches together
contain each tap exactly once and no arithmetic has been invented or lost. Seeing it
as a re-indexing rather than a transformation is what makes the noble identities
obvious rather than magical.
""",
                    },
                    {
                        "q": "The noble identity for decimation says that downsampling by $M$ followed by $G(z)$ is identical to:",
                        "opts": [
                            "$G(z^M)$ followed by downsampling by $M$",
                            "$G(z)$ followed by downsampling by $M$",
                            "$G(z^{1/M})$ followed by downsampling by $M$",
                            "downsampling by $M$ followed by $G(z^M)$",
                        ],
                        "a": 0,
                        "why": r"""
Moving a filter to the *fast* side of a downsampler requires upsampling its impulse
response — inserting $M-1$ zeros between every tap, which is what $z \to z^M$ means.
Leaving $G(z)$ unchanged is the tempting move and it is simply a different system:
filtering at the high rate with the low-rate coefficients is not the same operation.
The identity is exact, not an approximation, and it is the whole reason polyphase
costs nothing in accuracy.
""",
                    },
                    {
                        "q": "A length-120 filter feeds a decimator by $M = 4$. What does polyphase save?",
                        "opts": [
                            "Three quarters of the multiplications — the ones whose results were discarded",
                            "Three quarters of the memory",
                            "Nothing; it is a different way of writing the same cost",
                            "Half the multiplications, whatever $M$ is",
                        ],
                        "a": 0,
                        "why": r"""
The direct form computes an output for every input sample and then throws three in
four away. Polyphase identifies those in advance and never computes them, so the
multiply rate drops by exactly $M$ — 120 multiplies per output either way, but per
*input* it falls from 120 to 30. The taps all still have to be stored, so memory is
unchanged; and the saving is $M$, not a fixed half.
""",
                    },
                    {
                        "q": "Does a polyphase decimator produce a different output from the direct implementation?",
                        "opts": [
                            "No — it is an algebraic identity, sample for sample",
                            "Yes, slightly, because the branches are shorter",
                            "Yes — it has less delay",
                            "Only if the filter is not linear phase",
                        ],
                        "a": 0,
                        "why": r"""
Identical, sample for sample, in exact arithmetic. That is what makes it worth doing:
it is a restructuring of the same sum, not an approximation you trade accuracy for.
In floating point the two differ in the last bits because the additions happen in a
different order, which is a rounding artefact and not a design decision. Linear phase
is unrelated — it buys tap symmetry, a separate and stackable saving.
""",
                    },
                    {
                        "q": "In a polyphase decimator by $M$, the branch filters run at which rate?",
                        "opts": ["The low output rate", "The high input rate", "$M$ times the input rate", "Each branch at a different rate"],
                        "a": 0,
                        "why": r"""
That is the point of the whole exercise. The commutator hands each branch one input in
$M$, so every branch sees the *output* rate, and the hardware clock for the multipliers
drops by $M$. If the branches still ran at the input rate you would have reorganised
the arithmetic without saving any of it — which is exactly what happens if you apply
the noble identity in the wrong direction.
""",
                    },
                ],
            },
            "lab": {
                "title": "Polyphase decimation and interpolation",
                "runtime": "python",
                "minutes": 36,
                "brief": r'''
`design_lowpass` is provided; the work here is the decomposition.

`polyphase_split(h, M)` returns a list of `M` NumPy arrays, branch `m` being
`h[m::M]`. Branches differ in length by at most one when `M` does not divide `len(h)`.

`polyphase_decimate(x, h, M)` must return exactly `np.convolve(x, h)[::M]` — same
length, same values to floating-point noise — without ever computing the outputs it
would discard. The identity to implement is

```text
y[n] = sum over m of ( sum over k of e_m[k] * x[(n-k)*M - m] )
```

with `x[j] = 0` for `j < 0`. Read that as: for each branch, build the phase sequence
`u_m[p] = x[p*M - m]`, convolve it with `e_m`, and add the results.

`polyphase_interpolate(x, h, L)` must return exactly `np.convolve(upsample(x, L), h)`
without ever building the zero-stuffed array. Here

```text
y[n*L + p] = sum over k of e_p[k] * x[n - k]
```

so each branch is convolved with `x` directly and the results are interleaved. The
output length is `len(x)*L + len(h) - 1`.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def design_lowpass(numtaps, fc, gain=1.0):
    """Provided. Windowed-sinc lowpass whose DC gain is `gain`."""
    if numtaps % 2 == 0:
        numtaps += 1
    n = np.arange(numtaps) - (numtaps - 1) / 2.0
    h = 2.0 * fc * np.sinc(2.0 * fc * n)
    w = 0.54 - 0.46 * np.cos(2.0 * np.pi * np.arange(numtaps) / (numtaps - 1))
    h = h * w
    return h * (gain / float(np.sum(h)))


def polyphase_split(h, M):
    """Return M branches, branch m being every M-th tap starting at index m."""
    h = np.asarray(h, dtype=float)
    # TODO: one slice per branch.
    return []


def polyphase_decimate(x, h, M):
    """Equal to np.convolve(x, h)[::M], computed one branch at a time."""
    x = np.asarray(x, dtype=float)
    h = np.asarray(h, dtype=float)
    # TODO: build u_m[p] = x[p*M - m], convolve with branch m, accumulate.
    return np.zeros(0)


def polyphase_interpolate(x, h, L):
    """Equal to np.convolve(upsample(x, L), h), computed one branch at a time."""
    x = np.asarray(x, dtype=float)
    h = np.asarray(h, dtype=float)
    # TODO: convolve each branch with x and interleave the results.
    return np.zeros(0)


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    x = np.asarray(rng.standard_normal(200))
    h = design_lowpass(41, 0.15)
    print("branch lengths:", [len(b) for b in polyphase_split(h, 3)])
    a = polyphase_decimate(x, h, 3)
    b = np.convolve(x, h)[::3]
    print("decimate matches direct:", len(a) == len(b))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def design_lowpass(numtaps, fc, gain=1.0):
    """Provided. Windowed-sinc lowpass whose DC gain is `gain`."""
    if numtaps % 2 == 0:
        numtaps += 1
    n = np.arange(numtaps) - (numtaps - 1) / 2.0
    h = 2.0 * fc * np.sinc(2.0 * fc * n)
    w = 0.54 - 0.46 * np.cos(2.0 * np.pi * np.arange(numtaps) / (numtaps - 1))
    h = h * w
    return h * (gain / float(np.sum(h)))


def polyphase_split(h, M):
    """Return M branches, branch m being every M-th tap starting at index m."""
    h = np.asarray(h, dtype=float)
    return [h[m::M].copy() for m in range(M)]


def polyphase_decimate(x, h, M):
    """Equal to np.convolve(x, h)[::M], computed one branch at a time."""
    x = np.asarray(x, dtype=float)
    h = np.asarray(h, dtype=float)
    full = len(x) + len(h) - 1
    P = (full + M - 1) // M
    xe = np.concatenate([np.zeros(M - 1), x])      # xe[j] = x[j - (M-1)]
    y = np.zeros(P)
    for m, e in enumerate(polyphase_split(h, M)):
        idx = np.arange(P) * M - m + (M - 1)
        u = np.zeros(P)
        good = (idx >= 0) & (idx < len(xe))
        u[good] = xe[idx[good]]
        y += np.convolve(e, u)[:P]
    return y


def polyphase_interpolate(x, h, L):
    """Equal to np.convolve(upsample(x, L), h), computed one branch at a time."""
    x = np.asarray(x, dtype=float)
    h = np.asarray(h, dtype=float)
    total = len(x) * L + len(h) - 1
    y = np.zeros(total)
    for p, e in enumerate(polyphase_split(h, L)):
        c = np.convolve(e, x)
        idx = np.arange(len(c)) * L + p
        good = idx < total
        y[idx[good]] = c[good]
    return y


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    x = np.asarray(rng.standard_normal(200))
    h = design_lowpass(41, 0.15)
    print("branch lengths:", [len(b) for b in polyphase_split(h, 3)])
    a = polyphase_decimate(x, h, 3)
    b = np.convolve(x, h)[::3]
    print("decimate matches direct:", len(a) == len(b))
'''}],
                "hints": [
                    "`h[m::M]` is the whole of one branch; `polyphase_split` is a list comprehension over `range(M)`.",
                    "In `polyphase_decimate` the number of outputs is `ceil((len(x)+len(h)-1)/M)`; build the phase sequence with fancy indexing and mask out the indices that fall before the start of `x`.",
                    "In `polyphase_interpolate`, `np.convolve(e_p, x)` is already the sequence of output samples at positions `p, p+L, p+2L, ...` — you only have to write it into the right slots.",
                    "Both functions must match the direct route exactly, so compare against `np.convolve` while you are debugging rather than eyeballing a plot.",
                ],
                "tests": [
                    {"name": "the branches deal the taps out in turn", "code": r'''
import numpy as np
_b = polyphase_split(np.arange(10.0), 3)
assert len(_b) == 3, f"M branches for M=3 means three arrays, got {len(_b)}"
assert [len(z) for z in _b] == [4, 3, 3], \
    f"ten taps over three branches is 4, 3, 3 — got {[len(z) for z in _b]}"
assert np.allclose(_b[0], [0, 3, 6, 9]), \
    f"branch 0 is every third tap starting at index 0, got {np.asarray(_b[0]).tolist()}"
assert np.allclose(_b[2], [2, 5, 8]), \
    f"branch 2 starts at index 2, got {np.asarray(_b[2]).tolist()}"
'''},
                    {"name": "every tap ends up in exactly one branch", "code": r'''
import numpy as np
_h = design_lowpass(41, 0.15)
for _M in (2, 3, 4, 5, 7):
    _b = polyphase_split(_h, _M)
    assert sum(len(z) for z in _b) == len(_h), \
        f"the branches must partition the filter: M={_M} loses or duplicates taps"
'''},
                    {"name": "polyphase decimation matches the direct route", "code": r'''
import numpy as np
_rng = np.random.default_rng(7)
_x = np.asarray(_rng.standard_normal(200))
_h = design_lowpass(41, 0.15)
for _M in (2, 3, 4, 5):
    _a = polyphase_decimate(_x, _h, _M)
    _b = np.convolve(_x, _h)[::_M]
    assert len(_a) == len(_b), \
        f"M={_M}: expected {len(_b)} outputs, got {len(_a)} — the count is ceil((len(x)+len(h)-1)/M)"
    assert float(np.max(np.abs(_a - _b))) < 1e-9, \
        f"M={_M}: the two structures are algebraically identical, so any difference is a phase-alignment error in the branch indexing"
'''},
                    {"name": "polyphase interpolation matches the direct route", "code": r'''
import numpy as np
_rng = np.random.default_rng(3)
_x = np.asarray(_rng.standard_normal(60))
for _L in (2, 3, 4, 5):
    _h = design_lowpass(31, 0.45 / _L, gain=float(_L))
    _v = np.zeros(len(_x) * _L)
    _v[::_L] = _x
    _b = np.convolve(_v, _h)
    _a = polyphase_interpolate(_x, _h, _L)
    assert len(_a) == len(_b), \
        f"L={_L}: expected len(x)*L + len(h) - 1 = {len(_b)} outputs, got {len(_a)}"
    assert float(np.max(np.abs(_a - _b))) < 1e-9, \
        f"L={_L}: interleaving the branch convolutions must reproduce the zero-stuffed convolution exactly — check which branch writes to which output slot"
'''},
                    {"name": "the decimator still removes what it should", "code": r'''
import numpy as np
_n = np.arange(1200)
_h = design_lowpass(101, 0.45 / 4)
_fast = polyphase_decimate(np.sin(2 * np.pi * 0.2 * _n), _h, 4)
_slow = polyphase_decimate(np.sin(2 * np.pi * 0.02 * _n), _h, 4)
assert float(np.max(np.abs(_fast[60:-60]))) < 0.02, \
    "restructuring the arithmetic must not change the answer: the out-of-band tone should still be gone"
assert 0.97 < float(np.max(np.abs(_slow[60:-60]))) < 1.03, \
    "and the in-band tone should still come through at full amplitude"
'''},
                    {"name": "the interpolator preserves amplitude", "code": r'''
import numpy as np
_n = np.arange(600)
_h = design_lowpass(121, 0.45 / 4, gain=4.0)
_y = polyphase_interpolate(np.sin(2 * np.pi * 0.05 * _n), _h, 4)
_amp = float(np.max(np.abs(_y[200:-200])))
assert 0.97 < _amp < 1.03, \
    f"the branch gains together carry the filter's DC gain of L, so the tone should stay near 1, got {_amp:.4f}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Conversion by a rational factor",
            "summary": "Interpolate by L, decimate by M, and let one filter do both jobs. The order matters and the cutoff is the tighter of the two.",
            "concepts": [
                "Any ratio of two sample rates is rational, so $L/M$ covers every conversion that will ever be asked for.",
                "Upsampling must come first: decimating first would throw away band that the upsampler could not put back.",
                "The two filters sit back to back at the same rate and collapse into one, with cutoff $\\pi/\\max(L, M)$ and gain $L$.",
                "$L$ and $M$ come from the rates divided by their greatest common divisor: 44.1 kHz to 48 kHz is 160 over 147.",
                "The intermediate rate $L f_s$ is never realised in a polyphase implementation — it exists only in the algebra.",
            ],
            "read": [
                {
                    "title": "One output in 160 lands on a sample you have",
                    "minutes": 16,
                    "body": r'''
A 44.1 kHz master has to go into a 48 kHz desk, and both are locked to the same house
clock, so the rates are exact. In one second 44,100 samples arrive and 48,000 have to
leave. Neither number divides the other, so almost every output sample is wanted at an
instant when nothing was measured.

How often is an output instant also an input instant? Output $k$ falls at $k/48000$
seconds and input $p$ at $p/44100$, so they coincide when $44100\,k = 48000\,p$:

```python
from math import gcd

f_in, f_out = 44100, 48000
fine = f_in * f_out // gcd(f_in, f_out)          # the finest grid holding both
print("finest grid:", fine, "Hz")
print("L =", fine // f_in, "  M =", fine // f_out)

# output instant k lands on an input instant when k/f_out == p/f_in for whole p
hits = [k for k in range(400) if (k * f_in) % f_out == 0]
print("output instants that fall on an input sample:", hits)
```

It prints `finest grid: 7056000 Hz`, `L = 160   M = 147`, and
`output instants that fall on an input sample: [0, 160, 320]`. One output in 160 lands on
a number you were given. The other 159 have to be worked out.

## Where $L$ and $M$ come from

The two grids are irregular against each other, but both sit inside a third one. The
input instants are multiples of $1/44100$ and the output instants are multiples of
$1/48000$, so both are multiples of the *least common multiple* of the two rates —
$\text{lcm}(44100, 48000) = 7{,}056{,}000$ Hz, which is what the block computed. Every
input instant is a point of that fine grid, one in every $7056000/44100 = 160$; every
output instant is a point of it too, one in every $7056000/48000 = 147$.

That reading gives the recipe rather than assuming it. Put the signal on the fine grid —
which is upsampling by $L = 160$, since the input samples are already 160 fine-grid
points apart. Fill in the fine-grid values the signal must have had, which is what the
lowpass does. Then read off every 147th of them, which is downsampling by $M = 147$. The
recipe is not a convention; it is the only grid on which both sets of instants exist at
once, and $L$ and $M$ are the two spacings measured on it.

It also settles the order, which is where the most expensive bug in resampling lives.
Downsampling first would mean reading every 147th *input* sample before the fine grid is
built. For the reverse conversion, 48 kHz down to 44.1 kHz with $M = 160$, that leaves
300 samples per second, whose Nyquist limit is 150 Hz. Everything in the recording above
150 Hz would be gone before the interpolator ran, and interpolation invents nothing, so
no later stage can bring it back. The blanks unit *48 kHz to 44.1 kHz, decision by
decision* opens on that choice for the same reason.

## One filter, and which constraint binds

The chain would have two filters back to back — the anti-image filter after the upsampler
and the anti-alias filter before the downsampler — both running at 7.056 MHz. Two lowpass
filters in cascade are one lowpass filter with the tighter cutoff, so the pair collapses
to a single filter that must satisfy both bounds: $\pi/L$ for the images, $\pi/M$ for the
aliases, and therefore $\pi/\max(L, M)$.

Turn that into hertz and something tidy falls out. The filter runs at $Lf_{in}$, so a
cutoff of $\pi/\max(L,M)$ is $Lf_{in}/(2\max(L,M))$. If $L > M$ that is $f_{in}/2$; if
$M > L$ it is $Lf_{in}/(2M) = f_{out}/2$. The combined cutoff is always **half of
whichever rate is lower** — 22.05 kHz for 44.1 kHz to 48 kHz, and 22.05 kHz again for the
conversion back, because 44.1 kHz is the lower rate in both directions. The sandbox
*Which of the two limits binds* is that sentence made movable: fix the tone and drop the
output rate, and headroom that had already been granted is revoked.

The gain follows from module 2 with nothing added. Zero insertion left the signal $L$
times too small; discarding samples changes no amplitude at all. So the combined filter
needs $\sum_n h[n] = L$, not $M$ and not $L/M$. The derive unit *Specifying the one filter
that does both jobs* walks the output rate, the intermediate rate, the binding cutoff and
the gain in that order.

## The commutator, derived

Written literally, the chain is: $v[n] = \sum_p x[p]\,h[n - pL]$ — the zero-stuffed
convolution, in which every term with $n - pL$ outside the filter contributes nothing —
followed by $y[k] = v[kM]$. Substitute:

$$y[k] = \sum_p x[p]\, h[kM - pL]$$

Now write $kM = qL + \varphi$ with $0 \le \varphi < L$, which is exactly
`q, phase = divmod(k*M, L)`. Then $kM - pL = \varphi + (q - p)L$, and putting $j = q - p$
so that $p = q - j$:

$$y[k] = \sum_j h[\varphi + jL]\; x[q - j] = \sum_j e_\varphi[j]\, x[q-j]$$

Every output sample is one branch of the filter dotted with one window of the input. The
7.056 MHz stream never appears, because $v$ was substituted away rather than computed:
the only quantities left in the final line are input samples and prototype taps.

The two indices do different jobs. $q$ says which input samples the window covers, and it
advances by roughly $M/L$ per output. $\varphi$ says which branch to use, and it walks:

```python
L, M = 3, 2
print("L =", L, " M =", M)
for k in range(7):
    q, phase = divmod(k * M, L)
    print(f"  output {k}: branch {phase}, input window ending at {q}")

L, M = 160, 147
print("L =", L, " M =", M)
print("  branches used by the first ten outputs:",
      [divmod(k * M, L)[1] for k in range(10)])
print("  the branch index advances by M =", M, "modulo L =", L)
```

For 3 and 2 the branches run `0, 2, 1, 0, 2, 1, 0` while the window advances
`0, 0, 1, 2, 2, 3, 4` — two branches fire for every one input sample consumed, which is
the ratio $L/M$ appearing as a rhythm. For 160 and 147 the first ten branches are
`[0, 147, 134, 121, 108, 95, 82, 69, 56, 43]`: the index advances by $M$ modulo $L$, and
since $147 = 160 - 13$ that reads on the page as a walk backwards in steps of 13. It
returns to branch 0 after 160 outputs, which is the same period the first block found —
the outputs that land on an input instant are the ones the commutator serves from
branch 0.

## The whole thing, in numbers

```python
import math


def design_lowpass(numtaps, fc, gain=1.0):
    if numtaps % 2 == 0:
        numtaps += 1
    h = []
    for i in range(numtaps):
        n = i - (numtaps - 1) / 2.0
        ideal = 2.0 * fc if n == 0.0 else math.sin(2.0 * math.pi * fc * n) / (math.pi * n)
        window = 0.54 - 0.46 * math.cos(2.0 * math.pi * i / (numtaps - 1))
        h.append(ideal * window)
    scale = gain / sum(h)
    return [v * scale for v in h]


L, M = 3, 2
N = 20 * max(L, M) + 1                     # the lab's rule: 61 taps here
h = design_lowpass(N, 0.45 / max(L, M), gain=float(L))
x = [math.sin(2 * math.pi * 0.07 * j) + 0.3 * math.cos(2 * math.pi * 0.19 * j)
     for j in range(40)]

# the literal route: build the zero-stuffed stream, convolve, keep every M-th
v = [0.0] * (len(x) * L)
v[::L] = x
full = [0.0] * (len(v) + len(h) - 1)
literal_mults = 0
for i, vi in enumerate(v):
    for j, hj in enumerate(h):
        full[i + j] += vi * hj
        literal_mults += 1
literal = full[::M]

# the commutator: one branch of h per output, and no stuffed array anywhere
T = -(-len(h) // L)                        # taps per branch, rounded up
E = [[h[p + j * L] if p + j * L < len(h) else 0.0 for j in range(T)] for p in range(L)]
K = -(-((len(x) - 1) * L + len(h)) // M)
pad = [0.0] * T + x + [0.0] * T
commutated = []
commutator_mults = 0
for k in range(K):
    q, phase = divmod(k * M, L)
    acc = 0.0
    for j in range(T):
        acc += E[phase][j] * pad[q + T - j]
        commutator_mults += 1
    commutated.append(acc)

print("outputs:", len(literal), "literal,", len(commutated), "commutator")
worst = max(abs(a - b) for a, b in zip(commutated, literal))
print("largest disagreement:", f"{worst:.2e}")
print("multiplies:", literal_mults, "literal,", commutator_mults, "commutator")
print("taps per branch:", T, "against a prototype of", len(h))
```

It reports `90 literal, 89 commutator`, a largest disagreement of `4.44e-16`, and
`7320 literal, 1869 commutator` multiplies over a prototype of 61 taps split into
branches of 21. The disagreement is double-precision rounding; the two routes are the
same sum in a different order.

The one-sample difference in length is real and worth understanding rather than patching.
The literal route convolves a zero-stuffed array whose tail is zeros, so it emits one
last output built entirely from them. The commutator's count,
$K = \lceil((n-1)L + N)/M\rceil$, stops at the final output for which the filter has seen
any input, which is the honest boundary. The capstone states that formula and compares on
the overlap for exactly this reason.

Scale the count up. At $L = 160$, $M = 147$ and 32 taps per phase, the prototype is 5120
taps. The literal route would convolve a 7.056 MHz stream with all of them —
$5120 \times 7{,}056{,}000 = 3.6 \times 10^{10}$ multiplies a second — and then discard
146 of every 147 results. The commutator does 32 per output at 48 kHz, which is
1,536,000 a second. The ratio is 23,520, and $160 \times 147$ is 23,520: the saving is
$L$ from never multiplying by a zero and $M$ from never computing a discarded output.

## The mistake, and why it is tempting

The cutoff is where careful people go wrong, and the reason is that the wrong answer
works. Setting the cutoff to $\pi/L$ is correct whenever $L > M$ — which is what 44.1 kHz
to 48 kHz is — so a converter built that way passes every test on the way up. Turn it
round to run 48 kHz into 44.1 kHz, where $M = 160$ is the larger, and $\pi/L = \pi/147$
becomes the looser bound: everything between 22.05 kHz and 24 kHz survives the filter and
folds into the audio band on the way through the decimator. The lab checks both degenerate
directions, `L = 1` and `M = 1`, because each of them alone lets a `min` written where a
`max` belongs go unnoticed.

The second one is `rate_ratio` itself. The output rate is $f_{in}L/M$, so $L$ has to be
built from $f_{out}$ and $M$ from $f_{in}$ — `(f_out//g, f_in//g)`. Writing them in the
order they appear in the argument list inverts the conversion, and 44.1 kHz to 48 kHz
becomes 48 kHz to 44.1 kHz, which is a plausible-looking file of the wrong length.

## Where this stops holding

Everything above assumes the two clocks are exactly nominal and locked together. Put the
player on one crystal and the recorder on another, both specified to ±50 ppm, and the
true ratio is not 160/147 — it is 160/147 times something near one that drifts with
temperature. A fixed commutator then produces output samples at the wrong long-run rate,
and the buffer between it and the recorder empties or fills, a sample at a time, until
something clicks. Fixing that means measuring the ratio continuously and moving the
branch phase by a fractional amount rather than by whole steps of $M$, which is
asynchronous rate conversion and a different structure — a Farrow interpolator rather
than a fixed bank.

Rationality is also a statement about existence rather than cost. Every ratio of two
integers is rational, so $L/M$ covers every conversion — but 44,100 to 44,101 has a
greatest common divisor of 1, giving $L = 44101$ and $M = 44100$, a bank of 44,101
branches and a prototype of well over a million taps. The structure is correct and
unbuildable, which is again the boundary where the asynchronous methods take over.

Lastly, the latency is the prototype's and not the branch's. A 5120-tap filter at
7.056 MHz has a group delay of 2559.5 fine-grid samples, about 363 microseconds. Each
output costs 32 multiplies, and none of that arithmetic reduces the delay by a sample —
cheapness and promptness are separate specifications here, and only one of them was
bought.

## What you are about to build

The lab *A rational rate converter, written literally* builds the version this reading
substituted away, so that the capstone has something correct to be measured against.
`rate_ratio(f_in, f_out)` reduces with `math.gcd`; `resample(x, L, M, numtaps=None)`
upsamples by `L`, filters at `0.45/max(L, M)` with gain `L`, and keeps every `M`-th
sample of the full convolution, with `numtaps` defaulting to `20*max(L, M) + 1`. Its
checks include both degenerate cases and a spectral one — with `L = 4, M = 1` the three
images have to be at least 50 dB down, which fails immediately if the cutoff used
`min(L, M)`.

The capstone *44.1 kHz to 48 kHz with a polyphase commutator* is the version derived
here: `divmod(k*M, L)`, one branch of 32 taps per output, no intermediate array anywhere,
and an equality check against the literal route to `1e-9` at both 5/3 and 160/147. A phase
error that a small ratio hides shows up at 160/147, where the commutator wraps 147 places
at a time.
''',
                },
            ],
            "quiz": {
                "title": "Two rates, one grid, one filter",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A converter takes 32 kHz to 44.1 kHz. At what rate does the single combined filter conceptually run?",
                        "opts": [
                            "44.1 kHz, the output rate, because that is the grid the samples it produces have to live on",
                            "14.112 MHz, the lowest rate whose instants include every input instant and every output instant",
                            "32 kHz, the input rate, because that is where the samples the filter has to read actually come from",
                            "76.1 kHz, the two rates added together, since both sets of instants have to be representable",
                        ],
                        "a": 1,
                        "why": r"""
The input instants are multiples of $1/32000$ and the output instants are multiples of
$1/44100$, and the finest grid containing both is $\text{lcm}(32000, 44100) =
14{,}112{,}000$ Hz. That gives $L = 14112000/32000 = 441$ and $M = 14112000/44100 = 320$,
and it is the only grid on which the two sets of instants exist at once — which is why
the recipe is upsample, filter, downsample rather than something cleverer. The filter is
placed between the two rate changes, so neither the input rate nor the output rate is
where it sits. In a polyphase implementation that 14.112 MHz stream is never built; it
survives only as the arithmetic that fixes $L$ and $M$.
""",
                    },
                    {
                        "q": "Going from 48 kHz to 44.1 kHz, $L = 147$ and $M = 160$. A converter is built that decimates by 160 first and interpolates by 147 afterwards. What comes out?",
                        "opts": [
                            "The right rate and the right band, but 160 times too quiet, because the decimator divided the level",
                            "The same result as the correct order, because 147 and 160 share no common factor",
                            "A signal band-limited to about 150 Hz and then stretched back over the audio range",
                            "The right band at the right level, with the interpolation images left in, since the filter that removes them now runs first",
                        ],
                        "a": 2,
                        "why": r"""
Decimating 48 kHz by 160 leaves 300 samples per second, whose Nyquist limit is 150 Hz.
Everything above that is gone at that instant, and interpolating by 147 afterwards raises
the rate without restoring any of it — the output has the right length, the right level
and almost none of the recording. Coprimality is a real property of 147 and 160 and it
has nothing to do with the question: these two stages do not commute in either case,
because one of them destroys band and the other cannot create it. Discarding samples also
scales nothing, so the level is not what changed.
""",
                    },
                    {
                        "q": "The combined filter's cutoff is $\\pi/\\max(L, M)$ in normalised terms. Expressed in hertz, what is that?",
                        "opts": [
                            "Half the input rate, whichever direction the conversion runs in",
                            "Half the intermediate rate, since that is the rate the filter is running at",
                            "Half of whichever of the input and output rates is the lower one",
                            "Half the output rate, since that is the grid the result has to be representable on",
                        ],
                        "a": 2,
                        "why": r"""
The filter runs at $Lf_{in}$, so a cutoff of $\pi/\max(L,M)$ is
$Lf_{in}/(2\max(L,M))$. When $L > M$ that reduces to $f_{in}/2$; when $M > L$ it reduces
to $Lf_{in}/(2M)$, which is $f_{out}/2$. Either way it is half the lower of the two
rates — 22.05 kHz both for 44.1 kHz into 48 kHz and for the return trip. Half the input
rate and half the output rate are each right in one direction and wrong in the other,
which is exactly why a converter built on one of them passes its tests going up and folds
22 kHz of content into the audio band coming down.
""",
                    },
                    {
                        "q": "The combined filter is given a DC gain of $L$, rather than $M$ or $L/M$. What decides that?",
                        "opts": [
                            "The overall rate change is $L/M$, and the gain has to match it so that power per second is preserved",
                            "Zero insertion divided the level by $L$, while discarding samples does not change any level at all",
                            "The downsampler multiplies the level by $M$ on the way out, so one factor of $L$ cancels against it",
                            "Here $L$ happens to exceed $M$, and the compensation always follows whichever of the two is larger",
                        ],
                        "a": 1,
                        "why": r"""
Only one of the two rate changes touches amplitude. Zero insertion spreads the same total
over $L$ times as many samples, so the mean falls by $L$ and a unit-gain filter passes
that reduced mean straight through; keeping one sample in $M$ takes values that were
already correct and drops the others, changing no level at all. So the compensation is
$L$ regardless of which of $L$ and $M$ is larger, and regardless of whether the
conversion raises or lowers the rate. The lab's constant-input check is the fastest way to
see it: a DC input of 1 that comes out near $1/L$ names the missing gain immediately.
""",
                    },
                    {
                        "q": "At $L = 160$, $M = 147$ with a 5120-tap prototype, how many multiplications does one output sample cost in the commutator form?",
                        "opts": [
                            "147, one for each input sample the window advances over between outputs",
                            "5120, the whole prototype, because every tap contributes something to every output",
                            "32 — the prototype split $L$ ways gives branches of that length",
                            "160, one tap taken from each of the 160 branches in turn",
                        ],
                        "a": 2,
                        "why": r"""
The prototype splits into $L = 160$ branches of $5120/160 = 32$ taps, and
`q, phase = divmod(k*M, L)` picks exactly one of them per output. Every tap does still
contribute to *some* output, which is what makes the 5120 reading tempting — but not to
this one: the taps a given output touches are the ones whose index is congruent to
$\varphi$ modulo $L$, and the rest line up against input positions that are zero in the
stuffed stream. At 48 kHz that is 1,536,000 multiplies a second against the literal
route's $3.6\times10^{10}$, a ratio of 23,520, which is $L$ times $M$.
""",
                    },
                    {
                        "q": "A 44.1 kHz player and a 48 kHz recorder run on separate crystals rather than a shared house clock. What does that break in a fixed 160/147 converter?",
                        "opts": [
                            "The stopband, because the images move along the axis as the true rates drift away from nominal",
                            "The gain, because the compensation of $L$ was derived from the nominal rates",
                            "Nothing: 160/147 is an exact ratio, so the conversion stays exact whatever the crystals do",
                            "The buffer, because the true ratio is only near 160/147 rather than equal to it",
                        ],
                        "a": 3,
                        "why": r"""
Two crystals specified to ±50 ppm give a true ratio of 160/147 multiplied by something
near one that wanders with temperature. The converter keeps producing exactly 160 outputs
per 147 inputs, so the long-run rate is wrong by a few parts per million, and the buffer
between the converter and the recorder fills or empties by one sample every few seconds
until it clicks. The exactness of 160/147 is not in doubt — that is what makes this
tempting to dismiss — but it is exact about the wrong quantity. The repair is to measure
the ratio continuously and move the branch phase by a fractional amount, which is
asynchronous conversion and a different structure.
""",
                    },
                ],
            },
            "sandbox": {
                "title": "Which of the two limits binds",
                "visualiser": "spectrum",
                "minutes": 7,
                "initial": {"fsig": 60, "fs": 160},
                "brief": r'''
A rational converter has two constraints on one filter. The anti-image constraint
says stop by $\pi/L$; the anti-alias constraint says stop by $\pi/M$. Only the
smaller of the two has any effect, and the smaller one is set by the larger of $L$
and $M$.

Read the picture as the output side of the converter: the rate slider is the output
rate, and the tone is the highest component you intend to keep.
''',
                "notice": [
                    "Set the rate to 160 Hz and raise the tone from 60 Hz. It aliases the moment it passes 80 Hz. That is the anti-alias constraint, and it is the one that binds when $M > L$ — the output rate is the lower one.",
                    "Now drop the rate to 100 Hz with the tone at 60 Hz. The alias appears at 40 Hz even though the tone was perfectly safe at 160 Hz. Reducing the rate revoked headroom that had already been granted.",
                    "Set the tone to 20 Hz and sweep the rate across the whole range. Nothing ever aliases. When the band you care about is well inside both limits, the choice of $L$ and $M$ stops being a correctness question and becomes purely a cost one.",
                ],
            },
            "derive": {
                "title": "Specifying the one filter that does both jobs",
                "minutes": 13,
                "vars": ["f_s", "L", "M", "N", "K"],
                "brief": r'''
Convert a sequence at rate $f_s$ to a new rate by upsampling by $L$, filtering, and
downsampling by $M$. Both filters — anti-image and anti-alias — would run at the same
intermediate rate, so they are replaced by a single filter.
''',
                "steps": [
                    {
                        "prompt": "Write the output sample rate in terms of $f_s$, $L$ and $M$.",
                        "answer": "\\frac{L f_s}{M}",
                        "hint": "Upsampling multiplies the rate by $L$; downsampling divides it by $M$.",
                        "deconstruct": [
                            "After the upsampler the rate is $L f_s$.",
                            "After the downsampler it is that divided by $M$.",
                        ],
                    },
                    {
                        "prompt": "Write the rate at which the single combined filter conceptually runs.",
                        "answer": "L f_s",
                        "hint": "It sits between the upsampler and the downsampler.",
                        "deconstruct": [
                            "The upsampler has already multiplied the rate by $L$.",
                            "The downsampler has not yet divided it.",
                        ],
                    },
                    {
                        "prompt": "The filter must stop images (cutoff $\\pi/L$) and stop aliases (cutoff $\\pi/M$). For $L = 4$ and $M = 3$, write the cutoff that satisfies both, in normalised angular frequency.",
                        "answer": "\\frac{\\pi}{4}",
                        "hint": "Two upper bounds on the same number; only the smaller one matters.",
                        "deconstruct": [
                            "The bounds are $\\pi/4$ and $\\pi/3$.",
                            "The smaller bound is the binding one.",
                        ],
                    },
                    {
                        "prompt": "Write the DC gain the combined filter needs.",
                        "answer": "L",
                        "hint": "The downsampler changes no amplitudes at all; only the upsampler's zeros have to be paid for.",
                        "deconstruct": [
                            "Zero insertion divided the signal level by $L$.",
                            "Discarding samples divides nothing.",
                        ],
                    },
                    {
                        "prompt": "In the polyphase form, each output sample is produced by exactly one branch of the $N$-tap filter. Write the number of multiplications per output sample, in terms of $N$ and $L$.",
                        "answer": "\\frac{N}{L}",
                        "hint": "The filter is split into $L$ branches by the upsampler, and the downsampler chooses which one to use.",
                        "deconstruct": [
                            "There are $L$ branches, sharing $N$ taps equally.",
                            "One output sample uses one branch.",
                        ],
                    },
                ],
                "closing": r'''
For 44.1 kHz to 48 kHz, $L = 160$ and $M = 147$. The literal reading of that says
build a 7.056 MHz intermediate signal; the polyphase reading says run a 32-tap branch
48000 times a second. Same output, four orders of magnitude apart in cost.
''',
            },
            "blanks": {
                "title": "48 kHz to 44.1 kHz, decision by decision",
                "minutes": 9,
                "caption": "resample.py — the four choices that define a rational converter",
                "lang": "python",
                "brief": r"""
The most common resampling job in the world, and every one of its four decisions is a
place people go wrong. Fill them in and the recipe reads itself.
""",
                "listing": """from math import gcd

# 48 kHz  ->  44.1 kHz
g = gcd(48000, 44100)             # 300
L = 44100 // g                    # 147
M = 48000 // g                    # 160

# 1. ___ by L  (write each sample, then L-1 zeros)
# 2. one low-pass filter, running at the ___ rate,
#       with cutoff   wc = ___
# 3. ___ by M  (keep one sample in M, discard the rest)
""",
                "blanks": [
                    {
                        "prompt": "Which operation has to come first?",
                        "hole": "?",
                        "opts": ["upsample", "downsample", "filter", "delay"],
                        "a": 0,
                        "why": "Upsampling first, always. Decimating by 160 before interpolating by 147 would band-limit the signal to $\\pi/160$ and then stretch that back out — the audio above about 150 Hz would already be gone, and no later stage can recover it.",
                        "whys": [
                            "Upsampling first, always. Decimating by 160 before interpolating by 147 would band-limit the signal to $\\pi/160$ and then stretch that back out — the audio above about 150 Hz would already be gone, and no later stage can recover it.",
                            "This is the order that destroys the signal: decimating first throws away band that the interpolation afterwards cannot bring back. It is the single most common bug in a rate converter, and it is silent — the output is the right length and the right level.",
                            "The filter has a job to do, but it cannot do it until the zeros exist: it is what turns them into samples.",
                            "A delay changes nothing about the rate and is not part of the conversion.",
                        ],
                    },
                    {
                        "prompt": "The two rate changes are 147 up and 160 down. What rate does the filter see?",
                        "hole": "?",
                        "opts": ["high (147 x 48 kHz)", "input (48 kHz)", "output (44.1 kHz)", "the lower of the two"],
                        "a": 0,
                        "why": "It sits between the two stages, so it runs at $L$ times the input rate — 7.056 MHz here. That is a large number, and it is exactly why polyphase from module 3 matters: the structure lets the multipliers run at the output rate instead while computing the same result.",
                        "whys": [
                            "It sits between the two stages, so it runs at $L$ times the input rate — 7.056 MHz here. That is a large number, and it is exactly why polyphase from module 3 matters: the structure lets the multipliers run at the output rate instead while computing the same result.",
                            "The upsampler has already raised the rate before the filter is reached; at the input rate the zeros have not been inserted yet.",
                            "The decimator has not run yet, so the output rate does not exist at this point in the chain.",
                            "Neither of the original rates: the intermediate rate is higher than both, by construction.",
                        ],
                    },
                    {
                        "prompt": "One filter, two jobs. Which cutoff satisfies both?",
                        "hole": "?",
                        "opts": ["min(pi/L, pi/M)", "pi / L", "pi / M", "pi / (L * M)"],
                        "a": 0,
                        "why": "It must suppress the interpolation images (which needs $\\pi/L$) and band-limit before the decimation (which needs $\\pi/M$). Whichever is tighter binds, and here $M > L$ so $\\pi/160$ wins — the output rate is the lower one, so it is the decimation that sets the limit.",
                        "whys": [
                            "It must suppress the interpolation images (which needs $\\pi/L$) and band-limit before the decimation (which needs $\\pi/M$). Whichever is tighter binds, and here $M > L$ so $\\pi/160$ wins — the output rate is the lower one, so it is the decimation that sets the limit.",
                            "Enough for the images, not enough for the decimation that follows. Going 48 kHz to 44.1 kHz this leaves everything between 22.05 kHz and 24 kHz to fold back into the audio band.",
                            "Right in this particular direction, but only by accident: reverse the conversion to 44.1 into 48 kHz and it becomes the looser of the two and lets the images through.",
                            "Far tighter than either job needs, and it throws away almost the entire signal.",
                        ],
                    },
                    {
                        "prompt": "And the last step.",
                        "hole": "?",
                        "opts": ["downsample", "upsample", "filter", "delay"],
                        "a": 0,
                        "why": "Keep one sample in $M$. By now the filter has removed everything above $\\pi/M$, so there is nothing left to fold and the selection is safe — which is the entire reason the filter had to come first.",
                        "whys": [
                            "Keep one sample in $M$. By now the filter has removed everything above $\\pi/M$, so there is nothing left to fold and the selection is safe — which is the entire reason the filter had to come first.",
                            "Already done, in step 1. Doing it twice gives a rate of $L^2/M$ times the input, which is not the conversion asked for.",
                            "One filter is enough: the two filters the naive chain would use sit back to back at the same rate and collapse into a single one, which is what step 2 already is.",
                            "A delay does not change the rate.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "A rational rate converter, written literally",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
This lab builds the converter the obvious way, so that the capstone has something
correct to be measured against.

`rate_ratio(f_in, f_out)` returns `(L, M)` in lowest terms, such that
`f_out = f_in * L / M`. Use `math.gcd`.

`design_lowpass(numtaps, fc, gain=1.0)` is the same windowed sinc as before.

`resample(x, L, M, numtaps=None)` upsamples by `L`, filters with cutoff
`0.45/max(L, M)` and gain `L`, then keeps every `M`-th sample of the full
convolution. When `numtaps` is `None`, use `20*max(L, M) + 1`.

The two degenerate cases are worth checking by hand before you run anything:
`L = 1` reduces to the decimator of module 1, and `M = 1` reduces to the
interpolator of module 2.
''',
                "files": [{"name": "main.py", "content": r'''
import math

import numpy as np


def rate_ratio(f_in, f_out):
    """Return (L, M) in lowest terms with f_out == f_in * L / M."""
    # TODO: divide both rates by their greatest common divisor.
    return (1, 1)


def design_lowpass(numtaps, fc, gain=1.0):
    """Windowed-sinc lowpass whose DC gain is `gain`."""
    if numtaps % 2 == 0:
        numtaps += 1
    # TODO: as in the earlier labs.
    return np.zeros(numtaps)


def upsample(x, L):
    """Insert L-1 zeros after every sample."""
    x = np.asarray(x, dtype=float)
    # TODO
    return x


def resample(x, L, M, numtaps=None):
    """Upsample by L, filter, downsample by M."""
    x = np.asarray(x, dtype=float)
    if numtaps is None:
        numtaps = 20 * max(L, M) + 1
    # TODO: cutoff 0.45/max(L, M), gain L, full convolution, then every M-th sample.
    return x


if __name__ == "__main__":
    print("44.1k -> 48k:", rate_ratio(44100, 48000))
    n = np.arange(600)
    y = resample(np.sin(2 * np.pi * 0.05 * n), 3, 2)
    print("out samples:", len(y))
    print("peak:", round(float(np.max(np.abs(y[200:-200]))), 4) if len(y) > 400 else None)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

import numpy as np


def rate_ratio(f_in, f_out):
    """Return (L, M) in lowest terms with f_out == f_in * L / M."""
    a, b = int(f_in), int(f_out)
    g = math.gcd(a, b)
    return (b // g, a // g)


def design_lowpass(numtaps, fc, gain=1.0):
    """Windowed-sinc lowpass whose DC gain is `gain`."""
    if numtaps % 2 == 0:
        numtaps += 1
    n = np.arange(numtaps) - (numtaps - 1) / 2.0
    h = 2.0 * fc * np.sinc(2.0 * fc * n)
    w = 0.54 - 0.46 * np.cos(2.0 * np.pi * np.arange(numtaps) / (numtaps - 1))
    h = h * w
    return h * (gain / float(np.sum(h)))


def upsample(x, L):
    """Insert L-1 zeros after every sample."""
    x = np.asarray(x, dtype=float)
    out = np.zeros(len(x) * L)
    out[::L] = x
    return out


def resample(x, L, M, numtaps=None):
    """Upsample by L, filter, downsample by M."""
    x = np.asarray(x, dtype=float)
    if numtaps is None:
        numtaps = 20 * max(L, M) + 1
    h = design_lowpass(numtaps, 0.45 / max(L, M), gain=float(L))
    return np.convolve(upsample(x, L), h)[::M]


if __name__ == "__main__":
    print("44.1k -> 48k:", rate_ratio(44100, 48000))
    n = np.arange(600)
    y = resample(np.sin(2 * np.pi * 0.05 * n), 3, 2)
    print("out samples:", len(y))
    print("peak:", round(float(np.max(np.abs(y[200:-200]))), 4) if len(y) > 400 else None)
'''}],
                "hints": [
                    "`g = math.gcd(f_in, f_out)` and then `L = f_out//g`, `M = f_in//g` — note which way round they go, because the output rate is `f_in * L / M`.",
                    "`max(L, M)` appears once, in the cutoff. Get it the wrong way round and one of the two degenerate cases still passes, which is why both are checked.",
                    "The gain is `L` and never `M`: a downsampler does not scale anything.",
                ],
                "tests": [
                    {"name": "the ratio comes out in lowest terms", "code": r'''
assert rate_ratio(44100, 48000) == (160, 147), \
    f"48000/44100 reduces to 160/147, got {rate_ratio(44100, 48000)}"
assert rate_ratio(48000, 44100) == (147, 160), \
    f"the reverse conversion swaps L and M, got {rate_ratio(48000, 44100)}"
assert rate_ratio(8000, 8000) == (1, 1), \
    f"equal rates need no conversion at all, got {rate_ratio(8000, 8000)}"
assert rate_ratio(8000, 24000) == (3, 1), \
    f"a whole-number increase is pure interpolation: L=3, M=1, got {rate_ratio(8000, 24000)}"
'''},
                    {"name": "the output has the length the ratio implies", "code": r'''
import numpy as np
_y = resample(np.zeros(600), 3, 2)
assert len(_y) == 930, \
    f"600 samples upsampled by 3 is 1800, convolved with 61 taps is 1860, one in two of that is 930 — got {len(_y)}"
'''},
                    {"name": "a constant survives the round trip", "code": r'''
import numpy as np
_y = resample(np.ones(600), 3, 2)
_mid = _y[300:-300]
assert float(np.max(np.abs(_mid - 1.0))) < 0.01, \
    f"a DC input must come out at the same level; a mean of about 1/L means the filter gain was left at 1, got {float(np.mean(_mid)):.4f}"
'''},
                    {"name": "a tone keeps its amplitude and lands at the right frequency", "code": r'''
import numpy as np
_n = np.arange(600)
_y = resample(np.sin(2 * np.pi * 0.05 * _n), 3, 2)
_amp = float(np.max(np.abs(_y[200:-200])))
assert 0.95 < _amp < 1.05, \
    f"rate conversion is not supposed to change amplitude, got {_amp:.4f}"
_seg = _y[200:200 + 512] * np.hanning(512)
_Y = np.abs(np.fft.rfft(_seg))
_fr = np.fft.rfftfreq(512, d=1.0)
_peak = float(_fr[int(np.argmax(_Y))])
assert abs(_peak - 0.05 / 1.5) < 0.005, \
    f"0.05 cycles/sample at 1.5 times the rate is 0.0333 cycles/sample, got {_peak:.4f}"
'''},
                    {"name": "with L = 1 it is the decimator of module 1", "code": r'''
import numpy as np
_n = np.arange(600)
_y = resample(np.sin(2 * np.pi * 0.2 * _n), 1, 4)
_amp = float(np.max(np.abs(_y[40:-40])))
assert _amp < 0.02, \
    f"L=1, M=4 is pure decimation, and 0.2 cycles/sample is above the new Nyquist limit of 0.125, so it must be filtered out — got {_amp:.4f}"
'''},
                    {"name": "with M = 1 it is the interpolator of module 2", "code": r'''
import numpy as np
_n = np.arange(600)
_y = resample(np.sin(2 * np.pi * 0.05 * _n), 4, 1)
assert len(_y) == 2480, f"600*4 + 81 - 1 = 2480 samples expected, got {len(_y)}"
_seg = _y[300:300 + 1024] * np.hanning(1024)
_Y = np.abs(np.fft.rfft(_seg))
_fr = np.fft.rfftfreq(1024, d=1.0)
_peak = _Y[int(np.argmin(np.abs(_fr - 0.0125)))]
_far = _Y[np.abs(_fr - 0.0125) > 0.01]
_db = 20.0 * np.log10(float(np.max(_far)) / float(_peak))
assert _db < -50.0, \
    f"L=4, M=1 is pure interpolation and the three images must be at least 50 dB down; the worst is {_db:.1f} dB, so the cutoff is using min(L,M) or no filter at all"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "44.1 kHz to 48 kHz with a polyphase commutator",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
The conversion every studio does. $L = 160$, $M = 147$, and the literal
implementation asks for a 7.056 MHz intermediate signal — 160 samples of which 159
are zero, convolved with a 5120-tap filter, before 146 out of every 147 results are
thrown away.

Build the version that does none of that.

The identity you are implementing is exact, not approximate. With
$v[n] = \sum_p x[p]\, h[n - pL]$ and $y[k] = v[kM]$,

```text
y[k] = sum over j of  h[phase + j*L] * x[q - j]
       where  q, phase = divmod(k*M, L)
```

so each output sample reads one branch of the filter — 32 taps, not 5120 — and one
window of the input. The branch index walks around the $L$ phases in steps of $M$,
which is the commutator.

## Suggested order

`rate_ratio` and `design_filter` first, then `polyphase_branches`, then `resample`.
The checks are ordered the same way, and the exactness check against the literal
route will tell you immediately whether your phase arithmetic is right.

## Output length

Return exactly

```text
K = ceil( ((len(x) - 1) * L + N) / M )
```

samples, where `N = len(h)`. That is every output for which the filter has seen any
input at all; the literal route produces up to one more, from the trailing zeros of
the zero-stuffed array, and the checks compare on the overlap.
''',
        "deliverables": [
            "`rate_ratio(f_in, f_out)` returning `(L, M)` in lowest terms, correct for 44.1 kHz to 48 kHz and for the reverse.",
            "`design_filter(L, M, taps_per_phase)` returning a length `taps_per_phase * L` linear-phase lowpass with cutoff `0.5/max(L, M)` cycles per sample and DC gain `L`.",
            "`polyphase_branches(h, L)` returning an `(L, T)` array whose row `p` is `h[p::L]`, zero-padded to a common length `T`.",
            "`resample(x, L, M, h)` implementing the commutator: no zero-stuffed intermediate array anywhere, and one branch of arithmetic per output sample.",
            "A short comment at the top of `main.py` stating the filter length you chose, the passband edge it gives in hertz, and why that is enough for audio.",
        ],
        "constraints": [
            "NumPy and the standard library only.",
            "`resample` must never allocate an array of length `len(x) * L`, and must never call `np.convolve` on one.",
            "The filter is designed once and passed in; `resample` does not design its own.",
            "The polyphase output must equal the literal upsample-filter-downsample result to within 1e-9 on every sample they share, not merely sound the same.",
        ],
        "rubric": [
            {"criterion": "Ratio and filter specification", "weight": 20,
             "evidence": "rate_ratio reduces correctly in both directions, and the prototype filter has length taps_per_phase*L, symmetric taps, and a DC gain equal to L rather than 1."},
            {"criterion": "Polyphase decomposition", "weight": 20,
             "evidence": "polyphase_branches returns an (L, T) array whose rows are the interleaved tap sets, zero-padded, and whose entries together account for every tap of the prototype exactly once."},
            {"criterion": "Exactness of the commutator", "weight": 35,
             "evidence": "The polyphase output matches the literal upsample-filter-downsample result to within 1e-9 on the samples they share, both for a small ratio and for the full 160/147 conversion."},
            {"criterion": "Signal quality of the conversion", "weight": 25,
             "evidence": "A 1 kHz tone converts with its amplitude within a few percent and its frequency within a bin, and every conversion product outside the tone is at least 60 dB below it."},
        ],
        "hints": [
            "`q, phase = divmod(k * M, L)` is the whole of the commutator: `phase` selects the branch, `q` selects the input window.",
            "Pad the input with `T` zeros at each end and index it as `xp[q + 1 : q + T + 1]`, so that the branch dot product never falls off either edge.",
            "The branch taps must be reversed before the dot product — `y[k]` sums `E[phase, j] * x[q - j]`, and `j` counts backwards through the input window.",
            "`taps_per_phase = 32` gives `N = 5120`, a Hamming transition width of about 2.3 kHz either side of 22.05 kHz, and a stopband around 53 dB — enough for the 60 dB check because the images land far outside the transition.",
        ],
        "files": [
            {"name": "rates.py", "ro": True, "content": r'''
"""Fixed parameters of the conversion. Do not edit — the checks rely on these."""

FS_IN = 44100
FS_OUT = 48000
TAPS_PER_PHASE = 32
'''},
            {"name": "main.py", "content": r'''
import math

import numpy as np

from rates import FS_IN, FS_OUT, TAPS_PER_PHASE

# Filter length chosen: TODO taps, giving a passband edge of TODO Hz, because TODO.


def rate_ratio(f_in, f_out):
    """Return (L, M) in lowest terms with f_out == f_in * L / M."""
    # TODO
    return (1, 1)


def design_filter(L, M, taps_per_phase=TAPS_PER_PHASE):
    """Length taps_per_phase*L windowed sinc, cutoff 0.5/max(L,M), DC gain L."""
    N = taps_per_phase * L
    # TODO: ideal response, Hamming window, scale so sum(h) == L.
    return np.zeros(N)


def polyphase_branches(h, L):
    """Return an (L, T) array whose row p is h[p::L], zero-padded to length T."""
    h = np.asarray(h, dtype=float)
    T = int(math.ceil(len(h) / float(L)))
    # TODO: fill the rows.
    return np.zeros((L, T))


def n_out(n_in, L, M, numtaps):
    """Provided. Number of output samples the converter produces."""
    return int(math.ceil(((n_in - 1) * L + numtaps) / float(M)))


def resample(x, L, M, h):
    """Commutator form. One branch of h per output sample, no intermediate array."""
    x = np.asarray(x, dtype=float)
    # TODO: for each k, q, phase = divmod(k*M, L); dot the reversed branch with the
    # input window ending at q.
    return np.zeros(0)


if __name__ == "__main__":
    L, M = rate_ratio(FS_IN, FS_OUT)
    print("L, M =", L, M)
    h = design_filter(L, M)
    print("taps:", len(h), "dc gain:", round(float(np.sum(h)), 4))
    n = np.arange(4410)
    y = resample(np.sin(2 * np.pi * 1000.0 * n / FS_IN), L, M, h)
    print("out samples:", len(y))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import math

import numpy as np

from rates import FS_IN, FS_OUT, TAPS_PER_PHASE

# Filter length chosen: 32 taps per phase, so 32*160 = 5120 taps in the prototype.
# The cutoff is 0.5/160 cycles per sample at the 7.056 MHz intermediate rate, which
# is 22050 Hz — the input Nyquist limit. A 5120-tap Hamming design has a transition
# width of about 3.3/N in normalised frequency, roughly 2.3 kHz here, so the
# passband is flat to about 19.8 kHz and the stopband starts by about 24.3 kHz.
# That covers the audio band and leaves the nearest image, at 43.1 kHz, more than
# 50 dB down.


def rate_ratio(f_in, f_out):
    """Return (L, M) in lowest terms with f_out == f_in * L / M."""
    a, b = int(f_in), int(f_out)
    g = math.gcd(a, b)
    return (b // g, a // g)


def design_filter(L, M, taps_per_phase=TAPS_PER_PHASE):
    """Length taps_per_phase*L windowed sinc, cutoff 0.5/max(L,M), DC gain L."""
    N = taps_per_phase * L
    fc = 0.5 / max(L, M)
    n = np.arange(N) - (N - 1) / 2.0
    h = 2.0 * fc * np.sinc(2.0 * fc * n)
    w = 0.54 - 0.46 * np.cos(2.0 * np.pi * np.arange(N) / (N - 1))
    h = h * w
    return h * (float(L) / float(np.sum(h)))


def polyphase_branches(h, L):
    """Return an (L, T) array whose row p is h[p::L], zero-padded to length T."""
    h = np.asarray(h, dtype=float)
    T = int(math.ceil(len(h) / float(L)))
    E = np.zeros((L, T))
    for p in range(L):
        b = h[p::L]
        E[p, :len(b)] = b
    return E


def n_out(n_in, L, M, numtaps):
    """Provided. Number of output samples the converter produces."""
    return int(math.ceil(((n_in - 1) * L + numtaps) / float(M)))


def resample(x, L, M, h):
    """Commutator form. One branch of h per output sample, no intermediate array."""
    x = np.asarray(x, dtype=float)
    E = polyphase_branches(h, L)
    T = E.shape[1]
    K = n_out(len(x), L, M, len(h))
    xp = np.concatenate([np.zeros(T), x, np.zeros(T)])
    rev = E[:, ::-1]
    y = np.zeros(K)
    for k in range(K):
        q, phase = divmod(k * M, L)
        y[k] = float(np.dot(rev[phase], xp[q + 1:q + T + 1]))
    return y


if __name__ == "__main__":
    L, M = rate_ratio(FS_IN, FS_OUT)
    print("L, M =", L, M)
    h = design_filter(L, M)
    print("taps:", len(h), "dc gain:", round(float(np.sum(h)), 4))
    n = np.arange(4410)
    y = resample(np.sin(2 * np.pi * 1000.0 * n / FS_IN), L, M, h)
    print("out samples:", len(y))
'''},
        ],
        "tests": [
            {"name": "44.1 kHz to 48 kHz is 160 over 147", "code": r'''
from rates import FS_IN, FS_OUT
assert rate_ratio(FS_IN, FS_OUT) == (160, 147), \
    f"48000/44100 reduces to 160/147, got {rate_ratio(FS_IN, FS_OUT)}"
assert rate_ratio(FS_OUT, FS_IN) == (147, 160), \
    f"the reverse conversion swaps the pair, got {rate_ratio(FS_OUT, FS_IN)}"
assert rate_ratio(8000, 16000) == (2, 1), \
    f"doubling a rate is L=2, M=1, got {rate_ratio(8000, 16000)}"
'''},
            {"name": "the prototype filter has the length, symmetry and gain asked for", "code": r'''
import numpy as np
_h = design_filter(160, 147, 32)
assert len(_h) == 5120, f"32 taps per phase times 160 phases is 5120, got {len(_h)}"
assert abs(float(np.sum(_h)) - 160.0) < 1e-6, \
    f"the DC gain must be L = 160 to pay for the zero insertion, got {float(np.sum(_h)):.4f}"
assert float(np.max(np.abs(_h - _h[::-1]))) < 1e-12, \
    "a linear-phase design is symmetric about its centre — centre the sinc argument on (N-1)/2"
_h2 = design_filter(4, 3, 8)
assert abs(float(np.sum(_h2)) - 4.0) < 1e-9, \
    f"the gain is L for any ratio, not just this one, got {float(np.sum(_h2)):.6f}"
'''},
            {"name": "the branches partition the prototype", "code": r'''
import numpy as np
_h = design_filter(160, 147, 32)
_E = polyphase_branches(_h, 160)
assert _E.shape == (160, 32), f"expected a (160, 32) array of branches, got {_E.shape}"
assert abs(float(np.sum(_E)) - float(np.sum(_h))) < 1e-9, \
    "every tap belongs to exactly one branch, so the branch array and the prototype must sum to the same number"
assert np.allclose(_E[0], _h[0::160]), \
    "row p of the branch array is h[p::L] — row 0 does not match"
assert np.allclose(_E[7], _h[7::160]), \
    "row p of the branch array is h[p::L] — row 7 does not match"
'''},
            {"name": "the commutator equals the literal route for a small ratio", "code": r'''
import numpy as np
_rng = np.random.default_rng(11)
_x = np.asarray(_rng.standard_normal(120))
_L, _M = 5, 3
_h = design_filter(_L, _M, 8)
_v = np.zeros(len(_x) * _L)
_v[::_L] = _x
_ref = np.convolve(_v, _h)[::_M]
_got = resample(_x, _L, _M, _h)
assert len(_got) == n_out(len(_x), _L, _M, len(_h)), \
    f"expected {n_out(len(_x), _L, _M, len(_h))} outputs, got {len(_got)}"
assert len(_got) <= len(_ref), "the commutator cannot produce more samples than the literal route"
assert float(np.max(np.abs(_got - _ref[:len(_got)]))) < 1e-9, \
    "the two structures are algebraically identical; any difference is an off-by-one in the phase or in the input window"
'''},
            {"name": "the commutator equals the literal route at 160 over 147", "code": r'''
import numpy as np
_rng = np.random.default_rng(5)
_x = np.asarray(_rng.standard_normal(200))
_h = design_filter(160, 147, 32)
_v = np.zeros(len(_x) * 160)
_v[::160] = _x
_ref = np.convolve(_v, _h)[::147]
_got = resample(_x, 160, 147, _h)
assert float(np.max(np.abs(_got - _ref[:len(_got)]))) < 1e-9, \
    "a phase error that a ratio of 5/3 hides will show up at 160/147, where the commutator wraps 147 phases at a time"
'''},
            {"name": "a 1 kHz tone arrives at 48 kHz intact", "code": r'''
import numpy as np
from rates import FS_IN, FS_OUT
_L, _M = 160, 147
_h = design_filter(_L, _M, 32)
_n = np.arange(8820)
_y = resample(np.sin(2 * np.pi * 1000.0 * _n / FS_IN), _L, _M, _h)
assert len(_y) == 9634, f"0.2 s at 48 kHz plus the filter tail is 9634 samples, got {len(_y)}"
_amp = float(np.max(np.abs(_y[1000:-1000])))
assert 0.97 < _amp < 1.03, \
    f"conversion changes the rate, not the amplitude; a peak near 1/L means the filter gain was left at 1, got {_amp:.4f}"
_seg = _y[1000:1000 + 4096] * np.hanning(4096)
_Y = np.abs(np.fft.rfft(_seg))
_fr = np.fft.rfftfreq(4096, d=1.0 / FS_OUT)
_pk = float(_fr[int(np.argmax(_Y))])
assert abs(_pk - 1000.0) < 30.0, \
    f"a 1 kHz tone is still a 1 kHz tone after conversion, got {_pk:.1f} Hz"
'''},
            {"name": "conversion products are at least 60 dB down", "code": r'''
import numpy as np
from rates import FS_IN, FS_OUT
_h = design_filter(160, 147, 32)
_n = np.arange(8820)
_y = resample(np.sin(2 * np.pi * 1000.0 * _n / FS_IN), 160, 147, _h)
_seg = _y[1000:1000 + 4096] * np.hanning(4096)
_Y = np.abs(np.fft.rfft(_seg))
_fr = np.fft.rfftfreq(4096, d=1.0 / FS_OUT)
_peak = float(np.max(_Y))
_away = _Y[np.abs(_fr - 1000.0) > 200.0]
_db = 20.0 * np.log10(float(np.max(_away)) / _peak)
assert _db < -60.0, \
    f"every image and alias must be at least 60 dB below the tone; the worst is {_db:.1f} dB, which means the cutoff or the window is wrong"
'''},
            {"name": "the cost is one branch per output, not one filter", "code": r'''
import numpy as np
_rng = np.random.default_rng(1)
_x = np.asarray(_rng.standard_normal(20000))
_h = design_filter(160, 147, 32)
_y = resample(_x, 160, 147, _h)
assert len(_y) == 21803, f"expected 21803 output samples, got {len(_y)}"
assert float(np.max(np.abs(_y))) < 1e6, "the output should be finite and of the same order as the input"
_E = polyphase_branches(_h, 160)
assert _E.shape[1] * _E.shape[0] == len(_h), \
    "one output sample costs E.shape[1] = 32 multiplications, not len(h) = 5120 — that ratio of 160 is the whole point of the structure"
'''},
        ],
    },
}
