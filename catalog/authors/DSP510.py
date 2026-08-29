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
