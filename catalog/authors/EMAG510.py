"""EMAG510 — Guided Waves and Waveguides.

Same authoring rules as CTRL510, which is the template for this file:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

The sandbox notices in this file were written against the actual draw functions in
src/studio.js. Every number quoted in a notice — a readout, a decibel level, a
degree — was evaluated from that code before it was written down.
"""

COURSE = {
    "id": "EMAG510",
    "title": "Guided Waves and Waveguides",
    "band": 5,
    "level": "Advanced",
    "prereqs": [],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 130,
    "icon": "◎",
    "summary": (
        "A signal on a wire is a wave. Once the wire is long compared with a wavelength "
        "there is no such thing as the voltage on it, only the voltage at a place and a "
        "time. This course builds that picture from the telegrapher equations, uses it to "
        "decide what a mismatched load does to a line, and then follows the same wave "
        "equation into a hollow metal pipe — where it produces cutoff, dispersion, and two "
        "velocities that are not equal to each other."
    ),
    "outcomes": [
        "Derive the telegrapher equations and read characteristic impedance and phase velocity straight off the per-unit-length parameters.",
        "Compute reflection coefficient, VSWR and input impedance for a terminated line, and design a quarter-wave transformer.",
        "Find the cutoff frequency of any TE or TM mode in a rectangular guide and identify the single-mode band.",
        "Separate phase velocity from group velocity, and predict how far a pulse spreads over a given run of guide.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that propagates a pulse through a length of rectangular guide and measures the delay and the spreading it suffers.",
    "reading": [
        "*Microwave Engineering*, Pozar — chapters 2 and 3 cover almost all of this course.",
        "*Fields and Waves in Communication Electronics*, Ramo, Whinnery & Van Duzer — for the separation of variables done slowly.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "The telegrapher equations and the lossless line",
            "summary": "Two coupled first-order equations in z and t. Everything a line does is in them.",
            "concepts": [
                "A line has inductance and capacitance *per unit length*, and no single lumped value of either.",
                "$\\partial V/\\partial z = -L\\,\\partial I/\\partial t$ and $\\partial I/\\partial z = -C\\,\\partial V/\\partial t$: KVL and KCL applied to a slice of length $dz$.",
                "Eliminating one variable gives the wave equation, whose speed is $1/\\sqrt{LC}$.",
                "Characteristic impedance $Z_0 = \\sqrt{L/C}$ is a ratio carried by a travelling wave, not a resistance you can measure with an ohmmeter.",
                "A ladder of discrete LC sections is a low-pass filter with a real cutoff; a line is the limit as the sections become infinitesimal and that cutoff goes to infinity.",
            ],
            "sandbox": {
                "title": "One LC section, and why a line is not one",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 20, "zeta": 0.7, "K": 1},
                "brief": r'''
A transmission line is usually drawn as a ladder of series inductors and shunt
capacitors. Cut one section out of that ladder and terminate it, and you get an
ordinary second-order low-pass: a corner at $\omega_n = 1/\sqrt{LC}$, a damping set by
the termination, and a gain $K$.

That is what these two plots show. The point of the sandbox is what the single
section gets *wrong* about a line — a real line is the limit in which each section
carries an infinitesimal $L$ and $C$, so its corner runs off to infinity and the flat
region is all there is.
''',
                "notice": [
                    "Take $\\zeta$ down to 0.05. The amber dot on the corner reads $20\\log_{10}(K/2\\zeta) = 20$ dB, twenty above the low-frequency gain. One lightly loaded section resonates; a line, which is a cascade of infinitely many infinitesimal ones, does not.",
                    "Now drag $\\zeta$ from 0.05 all the way to 1.5 and watch the phase plot. The curve crosses the dashed $-90°$ line at the corner every single time — the damping changes how abruptly it gets there and nothing else.",
                    "Raise $\\omega_n$ from 20 to 200. Both curves slide one decade to the right with their shapes untouched, because the corner is the only frequency scale the section has. Making $L$ and $C$ per section smaller is exactly this move, and a line is where it ends up.",
                ],
            },
            "derive": {
                "title": "From a slice of line to a wave",
                "minutes": 14,
                "vars": ["L", "C", "R", "G", "Z_0", "v_p", "z", "t", "omega", "d"],
                "brief": r'''
Take a slice of line of length $dz$. Its series inductance is $L\,dz$ and its shunt
capacitance is $C\,dz$, where $L$ and $C$ are per-unit-length quantities. KVL round
the slice and KCL at its far node give the telegrapher equations for a lossless line:

$$\frac{\partial V}{\partial z} = -L\frac{\partial I}{\partial t}, \qquad
  \frac{\partial I}{\partial z} = -C\frac{\partial V}{\partial t}$$

Everything below follows from those two.
''',
                "steps": [
                    {
                        "prompt": "Differentiate the first equation with respect to $z$ and the second with respect to $t$, then eliminate $I$. You get $\\partial^2 V/\\partial z^2 = \\kappa\\,\\partial^2 V/\\partial t^2$. Write the constant $\\kappa$.",
                        "answer": "L C",
                        "hint": "Each equation contributes one factor. Nothing else in the pair can carry units.",
                        "deconstruct": [
                            "$\\partial^2 V/\\partial z^2 = -L\\,\\partial^2 I/\\partial z \\partial t$.",
                            "Substituting $\\partial I/\\partial z = -C\\,\\partial V/\\partial t$ turns the right-hand side into $LC\\,\\partial^2 V/\\partial t^2$.",
                        ],
                    },
                    {
                        "prompt": "The wave equation $\\partial^2 V/\\partial z^2 = (1/v_p^2)\\,\\partial^2 V/\\partial t^2$ has solutions $V(z \\mp v_p t)$. Write the phase velocity $v_p$ in terms of $L$ and $C$.",
                        "given": "You just found that the constant in front of the time derivative is $LC$.",
                        "answer": "\\frac{1}{\\sqrt{L C}}",
                        "hint": "Match the two forms of the same equation: $1/v_p^2 = LC$.",
                        "deconstruct": [
                            "Comparing coefficients, $1/v_p^2 = LC$.",
                            "So $v_p^2 = 1/(LC)$, and the speed is its positive square root.",
                        ],
                    },
                    {
                        "prompt": "For a wave travelling in $+z$ only, substitute $V = f(t - z/v_p)$ into the first telegrapher equation and you find $V/I$ is a constant. Write that characteristic impedance $Z_0$ in terms of $L$ and $C$.",
                        "answer": "\\sqrt{\\frac{L}{C}}",
                        "hint": "It has units of ohms, so $L$ must be over $C$, and $v_p$ has already used up the product.",
                        "deconstruct": [
                            "With $V = f(t - z/v_p)$, $\\partial V/\\partial z = -(1/v_p)f'$ and $\\partial I/\\partial t = g'$ where $I = g(t - z/v_p)$.",
                            "The first equation then gives $f'/v_p = L g'$, so $V/I = L v_p = L/\\sqrt{LC} = \\sqrt{L/C}$.",
                        ],
                    },
                    {
                        "prompt": "In practice you measure $Z_0$ and $v_p$ and want the line parameters back. Write $C$ in terms of $Z_0$ and $v_p$.",
                        "answer": "\\frac{1}{Z_0 v_p}",
                        "hint": "Multiply $Z_0$ by $v_p$ and see which parameter cancels.",
                        "deconstruct": [
                            "$Z_0 v_p = \\sqrt{L/C}\\cdot 1/\\sqrt{LC} = 1/C$.",
                            "So $C = 1/(Z_0 v_p)$, and by the same trick $L = Z_0/v_p$.",
                        ],
                    },
                ],
                "closing": r'''
Two per-unit-length numbers, two derived ones, and a change of variables between
them. Note what never appeared: the length of the line. A line has a characteristic
impedance and a velocity before you have decided how long it is, which is why $Z_0$
is a property of the cross-section alone.
''',
            },
            "lab": {
                "title": "Simulate a line as a ladder of LC sections",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Four functions.

`characteristic_impedance(Ls, Cs)` and `section_delay(Ls, Cs)` return $\sqrt{L_s/C_s}$
and $\sqrt{L_s C_s}$ for one section of the ladder.

`ladder_cutoff(Ls, Cs)` returns $2/\sqrt{L_s C_s}$ in radians per second. That is the
frequency above which a constant-k LC ladder stops propagating altogether — take it
as given here; it is the discrete artefact that a real line does not have.

`simulate(Ls, Cs, N, dt, steps, v_in)` leapfrogs the ladder. There are `N + 1` node
voltages `v[0..N]` and `N` branch currents `i[0..N-1]`, where `i[k]` flows from node
`k` to node `k+1`. Node 0 is held at `v_in` by an ideal source and node `N` is open.
Each step, in this order:

```text
v[0] = v_in
record v[N]
i[k]  += (dt / Ls) * (v[k] - v[k+1])          for every k
v[k]  += (dt / Cs) * (i[k-1] - i[k])          for k = 1 .. N-1
v[N]  += (dt / Cs) * i[N-1]
```

Return the recorded `v[N]` values as a list of floats. Write the current and voltage
updates as whole-array numpy operations rather than Python loops if you can.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def characteristic_impedance(Ls, Cs):
    """Return sqrt(Ls / Cs), the impedance a travelling wave sees."""
    # TODO
    return 0.0


def section_delay(Ls, Cs):
    """Return sqrt(Ls * Cs), the time one section takes to pass the wave on."""
    # TODO
    return 0.0


def ladder_cutoff(Ls, Cs):
    """Return 2 / sqrt(Ls * Cs) rad/s, above which the ladder stops propagating."""
    # TODO
    return 0.0


def simulate(Ls, Cs, N, dt, steps, v_in):
    """Leapfrog the ladder and return the far-end voltage at every step."""
    v = np.zeros(N + 1)
    i = np.zeros(N)
    out = []
    # TODO: hold node 0 at v_in, record v[N], then advance the currents and voltages.
    return out


if __name__ == "__main__":
    Ls, Cs = 1.0, 0.25
    print("Z0 =", characteristic_impedance(Ls, Cs))
    print("delay per section =", section_delay(Ls, Cs))
    print("cutoff =", ladder_cutoff(Ls, Cs), "rad/s")
    ys = simulate(Ls, Cs, 20, 0.01, 4000, 1.0)
    if ys:
        print("peak far-end voltage:", round(max(ys), 4))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def characteristic_impedance(Ls, Cs):
    """Return sqrt(Ls / Cs), the impedance a travelling wave sees."""
    return float(np.sqrt(Ls / Cs))


def section_delay(Ls, Cs):
    """Return sqrt(Ls * Cs), the time one section takes to pass the wave on."""
    return float(np.sqrt(Ls * Cs))


def ladder_cutoff(Ls, Cs):
    """Return 2 / sqrt(Ls * Cs) rad/s, above which the ladder stops propagating."""
    return 2.0 / float(np.sqrt(Ls * Cs))


def simulate(Ls, Cs, N, dt, steps, v_in):
    """Leapfrog the ladder and return the far-end voltage at every step."""
    v = np.zeros(N + 1)
    i = np.zeros(N)
    out = []
    for _ in range(steps):
        v[0] = v_in
        out.append(float(v[N]))
        i += (dt / Ls) * (v[:-1] - v[1:])
        v[1:N] += (dt / Cs) * (i[:N - 1] - i[1:])
        v[N] += (dt / Cs) * i[N - 1]
    return out


if __name__ == "__main__":
    Ls, Cs = 1.0, 0.25
    print("Z0 =", characteristic_impedance(Ls, Cs))
    print("delay per section =", section_delay(Ls, Cs))
    print("cutoff =", ladder_cutoff(Ls, Cs), "rad/s")
    ys = simulate(Ls, Cs, 20, 0.01, 4000, 1.0)
    if ys:
        print("peak far-end voltage:", round(max(ys), 4))
'''}],
                "hints": [
                    "`np.sqrt` on two Python floats returns a numpy scalar; wrap it in `float()` so the checks compare cleanly.",
                    "`v[:-1] - v[1:]` is the voltage across every inductor at once, and it already has length `N`.",
                    "Record `v[N]` *before* the updates, so the first sample is the far end at rest.",
                    "The far end is open, so its capacitor is charged by `i[N-1]` alone with nothing draining it — that is why it gets its own line.",
                ],
                "tests": [
                    {"name": "characteristic impedance is the root of the L to C ratio", "code": r'''
_z = characteristic_impedance(1.0, 0.25)
assert abs(_z - 2.0) < 1e-12, f"sqrt(1.0/0.25) is 2.0, got {_z}"
_z50 = characteristic_impedance(1e-6, 400e-12)
assert abs(_z50 - 50.0) < 1e-9, \
    f"1 uH and 400 pF per section is a 50 ohm line, got {_z50}"
'''},
                    {"name": "one section delays by the root of the L C product", "code": r'''
_d = section_delay(1.0, 0.25)
assert abs(_d - 0.5) < 1e-12, f"sqrt(1.0*0.25) is 0.5, got {_d}"
assert abs(section_delay(4.0, 4.0) - 4.0) < 1e-12, \
    "the delay is the square root of the product, not the product"
'''},
                    {"name": "the ladder cutoff is two over the section delay", "code": r'''
_wc = ladder_cutoff(1.0, 0.25)
assert abs(_wc - 4.0) < 1e-12, f"2/sqrt(1.0*0.25) is 4.0 rad/s, got {_wc}"
_prod = ladder_cutoff(1e-6, 400e-12) * section_delay(1e-6, 400e-12)
assert abs(_prod - 2.0) < 1e-9, \
    f"cutoff times section delay is exactly 2 for any Ls and Cs, got {_prod}"
'''},
                    {"name": "the far end stays quiet until the wave gets there", "code": r'''
_ys = simulate(1.0, 0.25, 20, 0.01, 4000, 1.0)
assert len(_ys) == 4000, f"expected one sample per step, got {len(_ys)}"
assert abs(_ys[0]) < 1e-12, f"the far end starts at rest, got {_ys[0]}"
assert abs(_ys[500]) < 1e-6, \
    f"at t=5 the wave is only half way down 20 sections, so v[N] should still be ~0, got {_ys[500]}"
assert max(_ys[:900]) < 0.1, \
    "nothing should reach the far end before roughly N*sqrt(Ls*Cs) = 10"
'''},
                    {"name": "the step arrives one section delay per section", "code": r'''
import numpy as np
_ys = np.array(simulate(1.0, 0.25, 20, 0.01, 4000, 1.0))
assert _ys.max() > 0.5, "the step never arrived at all"
_t = int(np.argmax(_ys > 0.5)) * 0.01
assert abs(_t - 10.0) < 0.2, \
    f"20 sections at 0.5 each means arrival near t=10, got t={_t}"
'''},
                    {"name": "an open far end doubles the incident step", "code": r'''
_ys = simulate(1.0, 0.25, 20, 0.01, 4000, 1.0)
_peak = max(_ys)
assert 1.9 < _peak < 2.6, \
    f"an open circuit reflects with Gamma=+1, so v[N] should peak near 2, got {_peak:.4f}"
'''},
                    {"name": "a heavier line delivers the step later", "code": r'''
import numpy as np
_fast = np.array(simulate(1.0, 0.25, 20, 0.01, 4000, 1.0))
_slow = np.array(simulate(1.0, 1.00, 20, 0.01, 4000, 1.0))
assert _slow.max() > 0.5, "the slower line never delivered the step inside 4000 steps"
_tf = int(np.argmax(_fast > 0.5)) * 0.01
_ts = int(np.argmax(_slow > 0.5)) * 0.01
assert abs(_ts - 20.0) < 0.4, f"quadrupling Cs doubles the delay to about 20, got {_ts}"
assert _ts > _tf * 1.8, \
    f"more capacitance per section means a slower wave: {_ts} should be about twice {_tf}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Reflection, VSWR and matching",
            "summary": "A load that is not Z0 sends part of the wave back. Where that reflection sits depends on where you stand.",
            "concepts": [
                "The reflection coefficient $\\Gamma = (Z_L - Z_0)/(Z_L + Z_0)$ comes from one boundary condition at the load.",
                "Standing waves: the incident and reflected waves interfere, and the ratio of the envelope's maximum to its minimum is the VSWR.",
                "Return loss $-20\\log_{10}|\\Gamma|$ is the same statement in decibels, and $|\\Gamma|^2$ is the fraction of power sent back.",
                "Input impedance rotates with distance: $Z_{in} = Z_0(Z_L + jZ_0\\tan\\beta d)/(Z_0 + jZ_L\\tan\\beta d)$, with period $\\lambda/2$.",
                "A quarter-wave section of impedance $\\sqrt{Z_0 Z_L}$ matches a real load, and only at the one frequency where it is a quarter wave.",
            ],
            "sandbox": {
                "title": "A load, and where a length of line puts it",
                "visualiser": "smith",
                "minutes": 9,
                "initial": {"rl": 100, "xl": 60, "len": 0},
                "brief": r'''
The Smith chart is the complex $\Gamma$ plane with the impedance grid drawn on top of
it. The centre is a perfect match — here the chart is normalised to 50 Ω, so the
centre is 50 Ω exactly. The grey dot is the load. The coloured dot is what you see
after `len` wavelengths of lossless line, and the dashed circle is the path it takes.
''',
                "notice": [
                    "Set $R$ to 50 and $X$ to 0. Both dots collapse onto the centre, the dashed circle shrinks to a point, and the readout gives $|\\Gamma| = 0.000$ with a VSWR of 1.00:1. Now sweep the line length over its whole range: nothing moves at all. A matched load looks identical from every distance.",
                    "Set $R = 100$ and $X = 0$. The load sits on the real axis at $\\Gamma = +1/3$. Take the line length to 0.25 λ and the marker travels exactly half way round the circle to $\\Gamma = -1/3$, landing on the leftmost point of the drawn $r = 0.5$ circle — 25 Ω. A quarter wave turned 100 Ω into $50^2/100$.",
                    "Back to $R = 100$, $X = 60$, and sweep the length from 0 to 0.5 λ. The marker makes one complete revolution and returns to the load, but the readout underneath never changes: $|\\Gamma| = 0.483$, VSWR 2.87:1, throughout. Those belong to the load, and lossless line cannot touch them.",
                ],
            },
            "derive": {
                "title": "The reflection coefficient and the quarter-wave transformer",
                "minutes": 14,
                "vars": ["Z_L", "Z_0", "Z_1", "Z_in", "Gamma", "V_i", "V_r", "s", "d", "beta"],
                "brief": r'''
A line of impedance $Z_0$ ends in a load $Z_L$. Just to the left of the load the total
voltage is the sum of an incident and a reflected wave, and the total current is their
difference divided by $Z_0$, because the reflected wave travels the other way:

$$V = V_i + V_r, \qquad I = \frac{V_i - V_r}{Z_0}$$

The load imposes one condition: $V/I = Z_L$.
''',
                "steps": [
                    {
                        "prompt": "Impose $V/I = Z_L$ and solve for $\\Gamma = V_r/V_i$. Write $\\Gamma$ in terms of $Z_L$ and $Z_0$.",
                        "answer": "\\frac{Z_L - Z_0}{Z_L + Z_0}",
                        "hint": "Write $Z_L = Z_0 (V_i + V_r)/(V_i - V_r)$, then divide top and bottom by $V_i$ and solve.",
                        "deconstruct": [
                            "$Z_L(V_i - V_r)/Z_0 = V_i + V_r$.",
                            "Collect: $V_i(Z_L - Z_0) = V_r(Z_L + Z_0)$.",
                            "Divide to get the ratio.",
                        ],
                    },
                    {
                        "prompt": "Along the line the two waves interfere. Where they add the envelope reaches $|V_i|(1 + |\\Gamma|)$ and where they cancel it drops to $|V_i|(1 - |\\Gamma|)$. Write the standing wave ratio $s$ for a real $\\Gamma$ between 0 and 1.",
                        "answer": "\\frac{1 + \\Gamma}{1 - \\Gamma}",
                        "hint": "It is a ratio of the two envelope values, and $|V_i|$ cancels.",
                        "deconstruct": [
                            "The maximum is $|V_i|(1 + \\Gamma)$ and the minimum is $|V_i|(1 - \\Gamma)$.",
                            "Their ratio drops $|V_i|$ entirely.",
                        ],
                    },
                    {
                        "prompt": "Power in a travelling wave goes as the square of its amplitude. Write the fraction of incident power that comes back, in terms of $\\Gamma$.",
                        "answer": "\\Gamma^2",
                        "placeholder": "\\Gamma^{2}",
                        "hint": "The reflected amplitude is $\\Gamma$ times the incident one, and power is amplitude squared.",
                        "deconstruct": [
                            "$P_r/P_i = |V_r|^2/|V_i|^2$.",
                            "And $V_r = \\Gamma V_i$, so the ratio is $\\Gamma^2$ for real $\\Gamma$.",
                        ],
                    },
                    {
                        "prompt": "The input impedance a distance $d$ from the load is $Z_{in} = Z_0(Z_L + jZ_0\\tan\\beta d)/(Z_0 + jZ_L\\tan\\beta d)$. Let $\\beta d \\to \\pi/2$, so $\\tan\\beta d \\to \\infty$. Write the limiting $Z_{in}$.",
                        "given": "A quarter wavelength means $\\beta d = (2\\pi/\\lambda)(\\lambda/4) = \\pi/2$.",
                        "answer": "\\frac{Z_0^2}{Z_L}",
                        "placeholder": "\\frac{Z_0^{2}}{Z_L}",
                        "hint": "Divide top and bottom by $\\tan\\beta d$ before taking the limit; the terms without a tangent go to zero.",
                        "deconstruct": [
                            "Dividing through: $Z_{in} = Z_0(Z_L/\\tan\\beta d + jZ_0)/(Z_0/\\tan\\beta d + jZ_L)$.",
                            "As the tangent grows without bound both leading terms vanish, leaving $Z_0 \\cdot jZ_0/(jZ_L)$.",
                        ],
                    },
                    {
                        "prompt": "Now use that backwards. You want a quarter-wave section of unknown impedance $Z_1$ to make a real load $Z_L$ look like $Z_0$. Write $Z_1$.",
                        "answer": "\\sqrt{Z_0 Z_L}",
                        "hint": "The section transforms $Z_L$ into $Z_1^2/Z_L$, and you want that to equal $Z_0$.",
                        "deconstruct": [
                            "Set $Z_1^2/Z_L = Z_0$.",
                            "So $Z_1^2 = Z_0 Z_L$, and $Z_1$ is the geometric mean of the two.",
                        ],
                    },
                ],
                "closing": r'''
The quarter-wave transformer is the cheapest matching network there is and the least
forgiving: it is a quarter wave at one frequency only. Everything else in matching is
an attempt to buy bandwidth back, usually by cascading sections whose impedances step
gradually rather than jumping once.
''',
            },
            "lab": {
                "title": "Reflection, standing waves and a quarter-wave match",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Five functions, all of which accept complex impedances.

- `reflection(zl, z0)` returns $\Gamma = (Z_L - Z_0)/(Z_L + Z_0)$ as a complex number.
- `vswr(g)` returns $(1 + |\Gamma|)/(1 - |\Gamma|)$, and `float("inf")` when $|\Gamma| \ge 1$.
- `return_loss(g)` returns $-20\log_{10}|\Gamma|$ in dB, and `float("inf")` when $\Gamma$ is zero.
- `input_impedance(zl, z0, bl)` returns $Z_0(Z_L + jZ_0\tan\beta d)/(Z_0 + jZ_L\tan\beta d)$
  where `bl` is the electrical length $\beta d$ in radians.
- `quarter_wave(zl, z0)` returns the real section impedance $\sqrt{Z_0 Z_L}$.

Use Python's built-in `complex` and `1j`; `np.tan` and `np.log10` do the rest. Do not
special-case $\beta d = \pi/2$ — `np.tan` returns a very large finite number there and
the formula handles it correctly to well within the tolerances used here.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def reflection(zl, z0):
    """Return the complex reflection coefficient of load zl on a line of z0."""
    # TODO
    return 0.0


def vswr(g):
    """Return the voltage standing wave ratio for a reflection coefficient g."""
    # TODO: infinite when |g| reaches 1.
    return 0.0


def return_loss(g):
    """Return -20*log10(|g|) in dB, infinite for a perfect match."""
    # TODO
    return 0.0


def input_impedance(zl, z0, bl):
    """Return the impedance seen bl radians of lossless line back from zl."""
    # TODO
    return 0.0


def quarter_wave(zl, z0):
    """Return the section impedance that matches a real zl to a real z0."""
    # TODO
    return 0.0


if __name__ == "__main__":
    g = reflection(100.0, 50.0)
    print("Gamma =", g)
    print("VSWR =", vswr(g))
    print("return loss =", return_loss(g), "dB")
    print("quarter wave back:", input_impedance(100.0, 50.0, np.pi / 2))
    print("matching section for 200 ohm:", quarter_wave(200.0, 50.0))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def reflection(zl, z0):
    """Return the complex reflection coefficient of load zl on a line of z0."""
    zl = complex(zl)
    z0 = complex(z0)
    return (zl - z0) / (zl + z0)


def vswr(g):
    """Return the voltage standing wave ratio for a reflection coefficient g."""
    m = abs(complex(g))
    if m >= 1.0:
        return float("inf")
    return (1.0 + m) / (1.0 - m)


def return_loss(g):
    """Return -20*log10(|g|) in dB, infinite for a perfect match."""
    m = abs(complex(g))
    if m == 0.0:
        return float("inf")
    return float(-20.0 * np.log10(m))


def input_impedance(zl, z0, bl):
    """Return the impedance seen bl radians of lossless line back from zl."""
    zl = complex(zl)
    z0 = complex(z0)
    t = float(np.tan(bl))
    return z0 * (zl + 1j * z0 * t) / (z0 + 1j * zl * t)


def quarter_wave(zl, z0):
    """Return the section impedance that matches a real zl to a real z0."""
    return float(np.sqrt(float(z0) * float(zl)))


if __name__ == "__main__":
    g = reflection(100.0, 50.0)
    print("Gamma =", g)
    print("VSWR =", vswr(g))
    print("return loss =", return_loss(g), "dB")
    print("quarter wave back:", input_impedance(100.0, 50.0, np.pi / 2))
    print("matching section for 200 ohm:", quarter_wave(200.0, 50.0))
'''}],
                "hints": [
                    "Coerce both impedances with `complex()` first, or an integer argument will do integer division somewhere you did not expect.",
                    "`abs()` of a Python complex is its magnitude — you do not need numpy for that part.",
                    "`vswr` and `return_loss` take $\\Gamma$ itself, not an impedance, so they never need $Z_0$.",
                    "`np.tan(np.pi/2)` is about $1.6\\times10^{16}$, which is large enough that the general formula lands on $Z_0^2/Z_L$ to twelve digits.",
                ],
                "tests": [
                    {"name": "a doubled load reflects one third", "code": r'''
_g = reflection(100.0, 50.0)
assert abs(_g - (1.0 / 3.0)) < 1e-12, f"(100-50)/(100+50) is 1/3, got {_g}"
assert abs(reflection(50.0, 50.0)) < 1e-15, "a matched load reflects nothing"
assert abs(reflection(0.0, 50.0) + 1.0) < 1e-15, \
    "a short circuit inverts the wave, so Gamma is -1, not +1"
'''},
                    {"name": "standing wave ratio follows the reflection", "code": r'''
_s = vswr(1.0 / 3.0)
assert abs(_s - 2.0) < 1e-12, f"|Gamma| = 1/3 gives a VSWR of 2.00, got {_s}"
assert abs(vswr(0.0) - 1.0) < 1e-15, "no reflection means a flat line: VSWR is 1, not 0"
import math
assert math.isinf(vswr(-1.0)), "a total reflection gives an infinite VSWR"
'''},
                    {"name": "return loss is the reflection in decibels", "code": r'''
_rl = return_loss(0.1)
assert abs(_rl - 20.0) < 1e-12, f"|Gamma| = 0.1 is 20 dB of return loss, got {_rl}"
_rl3 = return_loss(1.0 / 3.0)
assert abs(_rl3 - 9.542425094393248) < 1e-9, \
    f"a VSWR of 2 is 9.54 dB of return loss, got {_rl3}"
'''},
                    {"name": "a quarter wave inverts the load about Z0", "code": r'''
import numpy as np
_z = input_impedance(100.0, 50.0, np.pi / 2)
assert abs(_z - 25.0) < 1e-6, f"50^2/100 is 25 ohm, got {_z}"
_zs = input_impedance(0.0, 50.0, np.pi / 2)
assert abs(_zs) > 1e6, "a quarter wave turns a short into an open, not into a short"
'''},
                    {"name": "a half wave gives the load straight back", "code": r'''
import numpy as np
_z = input_impedance(100.0 + 60.0j, 50.0, np.pi)
assert abs(_z - (100.0 + 60.0j)) < 1e-6, \
    f"the transformation repeats every half wavelength, so this is the load, got {_z}"
_z8 = input_impedance(100.0, 50.0, np.pi / 4)
assert abs(_z8 - (40.0 - 30.0j)) < 1e-9, \
    f"an eighth wave back from 100 ohm on a 50 ohm line is 40 - 30j, got {_z8}"
'''},
                    {"name": "the matching section is the geometric mean", "code": r'''
import numpy as np
_z1 = quarter_wave(200.0, 50.0)
assert abs(_z1 - 100.0) < 1e-12, f"sqrt(50*200) is 100 ohm, got {_z1}"
_seen = input_impedance(200.0, _z1, np.pi / 2)
assert abs(_seen - 50.0) < 1e-6, \
    f"through its own quarter wave the 200 ohm load should look like 50 ohm, got {_seen}"
assert abs(reflection(_seen, 50.0)) < 1e-8, "and therefore reflect nothing"
'''},
                    {"name": "a reactive load is handled too", "code": r'''
_g = reflection(100.0 + 60.0j, 50.0)
assert abs(abs(_g) - 0.48344231827156525) < 1e-12, \
    f"|Gamma| for 100 + 60j on 50 ohm is 0.4834, got {abs(_g)}"
assert abs(vswr(_g) - 2.8717844506887853) < 1e-9, \
    f"that is a VSWR of 2.87, got {vswr(_g)}"
assert abs(_g.imag) > 0.2, "a reactive load gives a complex Gamma, not a real one"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "TE and TM modes in a rectangular guide",
            "summary": "Close the conductor round the wave and the boundary conditions quantise it. Below cutoff, nothing propagates.",
            "concepts": [
                "A hollow guide has no second conductor, so it cannot carry a TEM wave: every mode has a longitudinal field component.",
                "Separation of variables plus $E_t = 0$ on the walls forces $k_x = m\\pi/a$ and $k_y = n\\pi/b$.",
                "Cutoff is where the transverse wavenumber uses up the whole of $k = \\omega/c$: $f_c = (c/2)\\sqrt{(m/a)^2 + (n/b)^2}$.",
                "Below cutoff $\\beta$ is imaginary: the mode does not travel, it decays, and no length of guide makes it propagate.",
                "With $a$ the broad wall, TE$_{10}$ has the lowest cutoff of all, and the usable band runs from it to the next mode up — for a guide with $a > 2b$ that is TE$_{20}$, at exactly twice the frequency.",
            ],
            "sandbox": {
                "title": "A reactive load is a mirror, and so is a guide below cutoff",
                "visualiser": "smith",
                "minutes": 8,
                "initial": {"rl": 2, "xl": 200, "len": 0},
                "brief": r'''
Read this chart as the mouth of a waveguide seen from its feed. The centre is the
feed impedance, and $R + jX$ is what the guide presents.

Above cutoff a mode's wave impedance is real, and power crosses into the guide. Below
cutoff the mode is evanescent: it stores energy and returns it, which on this chart is
a load with almost no resistive part at all.
''',
                "notice": [
                    "Start where it opens, $R = 2$, $X = 200$. The marker sits almost on the rim and the readout gives $|\\Gamma| = 0.995$, a VSWR of 425.04:1, and a return loss the readout rounds to 0.0 dB. Practically everything sent in comes straight back — that is a guide driven below its cutoff.",
                    "Now set $R = 75$ and $X = 0$, a purely real load like a mode well above cutoff. $|\\Gamma|$ drops to 0.200, VSWR to 1.50:1, return loss climbs to 14.0 dB. The same pipe is a component or a mirror depending only on which side of $f_c$ you drive it.",
                    "Go back to the reactive load and sweep the line length across its full range. The marker runs right round the rim on a dashed circle that nearly fills the chart, and never once moves inward. No length of lossless guide converts a reflection into a transfer of power.",
                ],
            },
            "derive": {
                "title": "Where the cutoff frequency comes from",
                "minutes": 15,
                "vars": ["a", "b", "c", "m", "n", "f", "f_c", "k_c", "k_x", "k_y", "omega", "beta"],
                "brief": r'''
Inside a rectangular guide of width $a$ and height $b$ the fields satisfy the
Helmholtz equation. Separating variables gives a transverse dependence built from
$\sin k_x x$ and $\cos k_y y$ terms, with

$$k_x^2 + k_y^2 + \beta^2 = k^2 = \frac{\omega^2}{c^2}$$

The walls are perfect conductors, so the tangential electric field vanishes on all
four of them.
''',
                "steps": [
                    {
                        "prompt": "For the TE$_{m0}$ family the transverse field goes as $\\sin k_x x$, which must vanish at both $x = 0$ and $x = a$. Write $k_x$ in terms of the integer $m$ and the width $a$.",
                        "answer": "\\frac{m \\pi}{a}",
                        "hint": "A sine vanishes at zero automatically. The second wall says $k_x a$ must be a whole number of half-cycles.",
                        "deconstruct": [
                            "$\\sin k_x a = 0$ requires $k_x a = m\\pi$ for integer $m$.",
                            "Divide by $a$.",
                        ],
                    },
                    {
                        "prompt": "The same argument in $y$ gives $k_y = n\\pi/b$. Write the transverse wavenumber $k_c = \\sqrt{k_x^2 + k_y^2}$ in terms of $m$, $n$, $a$ and $b$.",
                        "answer": "\\sqrt{\\frac{m^2 \\pi^2}{a^2} + \\frac{n^2 \\pi^2}{b^2}}",
                        "placeholder": "\\sqrt{\\frac{m^{2}\\pi^{2}}{a^{2}} + \\frac{n^{2}\\pi^{2}}{b^{2}}}",
                        "hint": "Substitute both quantised wavenumbers into the Pythagorean sum and leave it under the root.",
                        "deconstruct": [
                            "$k_x^2 = m^2\\pi^2/a^2$ and $k_y^2 = n^2\\pi^2/b^2$.",
                            "Add them and take the root.",
                        ],
                    },
                    {
                        "prompt": "Cutoff is where $\\beta = 0$, so the whole of $k$ is used up transversely: $\\omega_c/c = k_c$. For TE$_{10}$, with $m = 1$ and $n = 0$, write the cutoff frequency $f_c$ in terms of $c$ and $a$.",
                        "given": "Remember $\\omega = 2\\pi f$.",
                        "answer": "\\frac{c}{2 a}",
                        "hint": "With $n = 0$ the transverse wavenumber is just $\\pi/a$. Divide out the $2\\pi$ that turns $\\omega$ into $f$.",
                        "deconstruct": [
                            "$2\\pi f_c/c = \\pi/a$.",
                            "So $f_c = c/(2a)$ — the width is exactly half a free-space wavelength at cutoff.",
                        ],
                    },
                    {
                        "prompt": "Above cutoff the longitudinal wavenumber is what is left over. Write $\\beta$ in terms of $\\omega$, $c$ and $k_c$.",
                        "answer": "\\sqrt{\\frac{\\omega^2}{c^2} - k_c^2}",
                        "placeholder": "\\sqrt{\\frac{\\omega^{2}}{c^{2}} - k_c^{2}}",
                        "hint": "Rearrange the separation relation $k_c^2 + \\beta^2 = \\omega^2/c^2$.",
                        "deconstruct": [
                            "$\\beta^2 = \\omega^2/c^2 - k_c^2$.",
                            "Take the positive root. Below cutoff the bracket is negative, $\\beta$ is imaginary, and the mode decays instead of travelling.",
                        ],
                    },
                ],
                "closing": r'''
Notice that $\beta < \omega/c$ always, because $k_c$ takes a share of $k$ and only what
is left over goes along the axis. Two consequences, and they point opposite ways. The
guide wavelength $2\pi/\beta$ is *longer* than the free-space one, and since the phase
advances by less than $\omega/c$ radians per metre the phase pattern sweeps along the
axis *faster* than light. The energy does not: it follows the zig-zag and crawls. The
next module separates the two and puts numbers on both.
''',
            },
            "lab": {
                "title": "Mode table, cutoff and the single-mode band",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Work in SI throughout, with `C_LIGHT` as given in the starter.

- `cutoff(a, b, m, n)` returns $(c/2)\sqrt{(m/a)^2 + (n/b)^2}$ in hertz. The mode with
  $m = n = 0$ does not exist in a hollow guide; return `float("inf")` for it.
- `mode_table(a, b, mmax, nmax)` returns a list of `(fc, m, n)` tuples for every
  $0 \le m \le m_{max}$ and $0 \le n \le n_{max}$ except $(0, 0)$, sorted by `fc`.
- `single_mode_band(a, b)` returns `(f_lo, f_hi)`, the cutoff of the dominant mode and
  the cutoff of the next *distinct* one. Search up to $m, n \le 3$. Two modes count as
  distinct when their cutoffs differ by more than one part in $10^{12}$, so that a
  square guide's degenerate pair is not mistaken for a band edge.
- `beta(f, fc)` returns $(2\pi f/c)\sqrt{1 - (f_c/f)^2}$ above cutoff, and `0.0` at or
  below it.
- `alpha(f, fc)` returns $(2\pi f_c/c)\sqrt{1 - (f/f_c)^2}$ nepers per metre below
  cutoff, and `0.0` at or above it.
- `guide_wavelength(f, fc)` returns $2\pi/\beta$, or `float("inf")` below cutoff.

The default guide in `main.py` is WR-90: 22.86 mm by 10.16 mm, the standard X-band
part.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

C_LIGHT = 2.99792458e8
WR90 = (0.02286, 0.01016)


def cutoff(a, b, m, n):
    """Cutoff frequency in Hz of the (m, n) mode in an a-by-b guide."""
    # TODO: the (0, 0) mode does not exist.
    return 0.0


def mode_table(a, b, mmax, nmax):
    """Every mode up to (mmax, nmax) as (fc, m, n), sorted by cutoff."""
    # TODO
    return []


def single_mode_band(a, b):
    """(f_lo, f_hi): dominant cutoff, and the next distinct cutoff above it."""
    # TODO
    return (0.0, 0.0)


def beta(f, fc):
    """Longitudinal wavenumber in rad/m, zero at or below cutoff."""
    # TODO
    return 0.0


def alpha(f, fc):
    """Evanescent decay in nepers/m below cutoff, zero at or above it."""
    # TODO
    return 0.0


def guide_wavelength(f, fc):
    """2*pi/beta in metres, infinite at or below cutoff."""
    # TODO
    return 0.0


if __name__ == "__main__":
    a, b = WR90
    for fc, m, n in mode_table(a, b, 2, 2)[:4]:
        print(f"TE{m}{n}: {fc / 1e9:.3f} GHz")
    print("band:", tuple(round(f / 1e9, 3) for f in single_mode_band(a, b)), "GHz")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

C_LIGHT = 2.99792458e8
WR90 = (0.02286, 0.01016)


def cutoff(a, b, m, n):
    """Cutoff frequency in Hz of the (m, n) mode in an a-by-b guide."""
    if m == 0 and n == 0:
        return float("inf")
    return 0.5 * C_LIGHT * float(np.sqrt((m / a) ** 2 + (n / b) ** 2))


def mode_table(a, b, mmax, nmax):
    """Every mode up to (mmax, nmax) as (fc, m, n), sorted by cutoff."""
    rows = []
    for m in range(mmax + 1):
        for n in range(nmax + 1):
            if m == 0 and n == 0:
                continue
            rows.append((cutoff(a, b, m, n), m, n))
    rows.sort()
    return rows


def single_mode_band(a, b):
    """(f_lo, f_hi): dominant cutoff, and the next distinct cutoff above it."""
    rows = mode_table(a, b, 3, 3)
    lo = rows[0][0]
    for fc, _m, _n in rows:
        if fc > lo * (1.0 + 1e-12):
            return (lo, fc)
    return (lo, float("inf"))


def beta(f, fc):
    """Longitudinal wavenumber in rad/m, zero at or below cutoff."""
    if f <= fc:
        return 0.0
    return 2.0 * np.pi * f / C_LIGHT * float(np.sqrt(1.0 - (fc / f) ** 2))


def alpha(f, fc):
    """Evanescent decay in nepers/m below cutoff, zero at or above it."""
    if f >= fc:
        return 0.0
    return 2.0 * np.pi * fc / C_LIGHT * float(np.sqrt(1.0 - (f / fc) ** 2))


def guide_wavelength(f, fc):
    """2*pi/beta in metres, infinite at or below cutoff."""
    b = beta(f, fc)
    if b <= 0.0:
        return float("inf")
    return 2.0 * np.pi / b


if __name__ == "__main__":
    a, b = WR90
    for fc, m, n in mode_table(a, b, 2, 2)[:4]:
        print(f"TE{m}{n}: {fc / 1e9:.3f} GHz")
    print("band:", tuple(round(f / 1e9, 3) for f in single_mode_band(a, b)), "GHz")
'''}],
                "hints": [
                    "`rows.sort()` on a list of tuples sorts by the first element, which is exactly the cutoff ordering you want.",
                    "For a guide with $a > b$ the dominant mode is always TE$_{10}$, so `rows[0]` is it — but write the search anyway, because a square guide breaks the assumption.",
                    "`beta` and `alpha` are the same square root with the arguments swapped; each is zero wherever the other is real.",
                    "Guide wavelength comes out *longer* than free space, not shorter. If yours is shorter, you have the ratio $f_c/f$ upside down.",
                ],
                "tests": [
                    {"name": "the dominant cutoff of WR-90 is 6.557 GHz", "code": r'''
_fc = cutoff(0.02286, 0.01016, 1, 0)
assert abs(_fc - 6.5571403762e9) < 1e3, \
    f"c/(2a) with a = 22.86 mm is 6.5571 GHz, got {_fc / 1e9:.4f} GHz"
assert cutoff(0.02286, 0.01016, 0, 0) == float("inf"), \
    "there is no TE00 mode in a hollow guide"
'''},
                    {"name": "the second and third modes sit where they should", "code": r'''
_a, _b = 0.02286, 0.01016
assert abs(cutoff(_a, _b, 2, 0) - 1.3114280752e10) < 1e3, \
    "TE20 has exactly twice the cutoff of TE10"
assert abs(cutoff(_a, _b, 0, 1) - 1.4753565846e10) < 1e3, \
    "TE01 is set by the height b, so c/(2b) = 14.75 GHz"
'''},
                    {"name": "the mode table is complete and ordered", "code": r'''
_t = mode_table(0.02286, 0.01016, 2, 2)
assert len(_t) == 8, f"3 by 3 modes minus the (0,0) that does not exist is 8, got {len(_t)}"
assert [(m, n) for _f, m, n in _t[:3]] == [(1, 0), (2, 0), (0, 1)], \
    f"the first three should be TE10, TE20, TE01, got {[(m, n) for _f, m, n in _t[:3]]}"
assert all(_t[i][0] <= _t[i + 1][0] for i in range(len(_t) - 1)), \
    "the table must come back sorted by cutoff"
'''},
                    {"name": "the single-mode band runs from TE10 to TE20", "code": r'''
_lo, _hi = single_mode_band(0.02286, 0.01016)
assert abs(_lo - 6.5571403762e9) < 1e3, f"the band starts at the TE10 cutoff, got {_lo}"
assert abs(_hi - 1.3114280752e10) < 1e3, f"and ends where TE20 appears, got {_hi}"
assert _hi > _lo, "the upper edge must be above the lower one"
'''},
                    {"name": "a square guide has a degenerate pair, not a band edge", "code": r'''
_lo, _hi = single_mode_band(0.02, 0.02)
assert abs(cutoff(0.02, 0.02, 1, 0) - cutoff(0.02, 0.02, 0, 1)) < 1.0, \
    "in a square guide TE10 and TE01 are degenerate"
assert _hi > _lo * 1.2, \
    f"the degenerate partner is not a band edge, so f_hi should be well above f_lo, got {_lo} and {_hi}"
'''},
                    {"name": "the axial wavenumber is below the free-space one", "code": r'''
_fc = 6.5571403762e9
_b = beta(10e9, _fc)
assert abs(_b - 158.2382563130) < 1e-6, f"beta at 10 GHz should be 158.24 rad/m, got {_b}"
assert _b < 2 * 3.141592653589793 * 10e9 / 2.99792458e8, \
    "beta must be below the free-space wavenumber, since k_c takes a share of k"
assert beta(5e9, _fc) == 0.0, "nothing propagates below cutoff"
'''},
                    {"name": "below cutoff the mode decays instead", "code": r'''
_fc = 6.5571403762e9
_al = alpha(4e9, _fc)
assert abs(_al - 108.8954160181) < 1e-6, \
    f"at 4 GHz the decay should be 108.9 Np/m, got {_al}"
assert alpha(10e9, _fc) == 0.0, "above cutoff there is no evanescent decay"
assert alpha(1e9, _fc) > _al, "the further below cutoff, the faster the decay"
'''},
                    {"name": "the guide wavelength is longer than free space", "code": r'''
_fc = 6.5571403762e9
_lg = guide_wavelength(10e9, _fc)
assert abs(_lg - 0.03970711921111) < 1e-9, \
    f"2*pi/beta at 10 GHz is 39.71 mm, got {_lg * 1e3:.3f} mm"
assert _lg > 2.99792458e8 / 10e9, \
    "the guide wavelength exceeds the 29.98 mm free-space wavelength at the same frequency"
assert guide_wavelength(5e9, _fc) == float("inf"), \
    "below cutoff there is no wavelength along the guide at all"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Dispersion, phase velocity and group velocity",
            "summary": "In a guide the two velocities are different, one is faster than light, and only the other carries anything.",
            "concepts": [
                "$\\beta(\\omega)$ is not proportional to $\\omega$ in a guide, and that is the whole definition of dispersion.",
                "Phase velocity $\\omega/\\beta$ exceeds $c$ at every frequency in the band, not only near cutoff, and grows without bound as cutoff is approached; it carries no information, and violates nothing.",
                "Group velocity $d\\omega/d\\beta$ is the speed of the envelope and stays below $c$ at every frequency.",
                "$v_p v_g = c^2$ exactly, for every hollow guide and every mode.",
                "Different frequencies in one pulse arrive at different times, so a wide-band pulse spreads — and the spreading grows with length and with proximity to cutoff.",
            ],
            "sandbox": {
                "title": "Phase slope is group delay",
                "visualiser": "bode",
                "minutes": 8,
                "initial": {"wn": 20, "zeta": 0.15, "K": 1},
                "brief": r'''
Group delay is $-d\phi/d\omega$: the steeper the phase curve, the longer the envelope
is held up. A guide near cutoff has a phase that bends sharply with frequency, and
that bend is what spreads a pulse.

This second-order section is the simplest system with a phase that bends. Read the
bottom plot as a dispersion curve.
''',
                "notice": [
                    "With $\\zeta = 0.15$ the phase goes from about $-11°$ at $\\omega_n/2$ to about $-169°$ at $2\\omega_n$ — almost the whole 180° inside a factor of four in frequency. Set $\\zeta = 1.5$ and over exactly the same span it moves only from about $-63°$ to about $-117°$. Both curves still run the full 180° between zero and infinite frequency; what changes is how much of it they spend near the corner, and it is that slope which sets the delay.",
                    "Look at the magnitude plot far above the corner. With $\\omega_n = 20$ it reads about $-40$ dB at $\\omega = 200$ and about $-80$ dB at $\\omega = 2000$: 40 dB per decade, which is the two-pole roll-off. A guide below cutoff rejects by a different mechanism entirely — its attenuation is exponential in the *length* of guide rather than a power law in frequency, so the rejection is set by how far you go rather than by how far past a corner you are.",
                    "Raise $K$ from 1 to 10. The magnitude curve lifts bodily by 20 dB and the phase curve does not move at all. Flat gain delays nothing; only a frequency-dependent *phase* does.",
                ],
            },
            "derive": {
                "title": "Two velocities from one dispersion relation",
                "minutes": 15,
                "vars": ["omega", "omega_c", "c", "v_p", "v_g", "beta", "d", "t_g", "lambda_g", "f"],
                "brief": r'''
From the last module, the dispersion relation of any hollow-guide mode is

$$\beta(\omega) = \frac{\sqrt{\omega^2 - \omega_c^2}}{c}$$

where $\omega_c = 2\pi f_c$. Everything about how a pulse travels is in the shape of
that curve.
''',
                "steps": [
                    {
                        "prompt": "Phase velocity is $v_p = \\omega/\\beta$. Write it in terms of $\\omega$, $\\omega_c$ and $c$.",
                        "answer": "\\frac{c \\omega}{\\sqrt{\\omega^2 - \\omega_c^2}}",
                        "placeholder": "\\frac{c\\omega}{\\sqrt{\\omega^{2} - \\omega_c^{2}}}",
                        "hint": "Divide $\\omega$ by the whole expression for $\\beta$; the $c$ in the denominator of $\\beta$ moves up to the numerator.",
                        "deconstruct": [
                            "$v_p = \\omega \\div \\left(\\sqrt{\\omega^2 - \\omega_c^2}/c\\right)$.",
                            "Dividing by a fraction multiplies by its reciprocal.",
                        ],
                    },
                    {
                        "prompt": "Differentiate $\\beta$ with respect to $\\omega$. Write $d\\beta/d\\omega$.",
                        "answer": "\\frac{\\omega}{c \\sqrt{\\omega^2 - \\omega_c^2}}",
                        "placeholder": "\\frac{\\omega}{c\\sqrt{\\omega^{2} - \\omega_c^{2}}}",
                        "hint": "Chain rule on $\\sqrt{u}$ with $u = \\omega^2 - \\omega_c^2$: the derivative is $u'/(2\\sqrt{u})$, and $u' = 2\\omega$.",
                        "deconstruct": [
                            "$\\frac{d}{d\\omega}\\sqrt{\\omega^2 - \\omega_c^2} = \\frac{2\\omega}{2\\sqrt{\\omega^2 - \\omega_c^2}}$.",
                            "The constant $1/c$ carries through unchanged.",
                        ],
                    },
                    {
                        "prompt": "Group velocity is $v_g = d\\omega/d\\beta$, the reciprocal of what you just wrote. Write $v_g$.",
                        "answer": "\\frac{c \\sqrt{\\omega^2 - \\omega_c^2}}{\\omega}",
                        "placeholder": "\\frac{c\\sqrt{\\omega^{2} - \\omega_c^{2}}}{\\omega}",
                        "hint": "Turn the previous answer upside down.",
                        "deconstruct": [
                            "$v_g = 1 \\div \\frac{\\omega}{c\\sqrt{\\omega^2 - \\omega_c^2}}$.",
                            "Which is the same fraction inverted.",
                        ],
                    },
                    {
                        "prompt": "Multiply the two velocities together. Write $v_p v_g$.",
                        "answer": "c^2",
                        "placeholder": "c^{2}",
                        "hint": "The two square roots cancel, and so does $\\omega$.",
                        "deconstruct": [
                            "$v_p v_g = \\frac{c\\omega}{\\sqrt{\\cdot}}\\cdot\\frac{c\\sqrt{\\cdot}}{\\omega}$.",
                            "Everything but the two factors of $c$ cancels, and the result does not depend on frequency at all.",
                        ],
                    },
                    {
                        "prompt": "The guide wavelength is $\\lambda_g = 2\\pi/\\beta$. Write it in terms of $\\omega$, $\\omega_c$ and $c$.",
                        "answer": "\\frac{2 \\pi c}{\\sqrt{\\omega^2 - \\omega_c^2}}",
                        "placeholder": "\\frac{2\\pi c}{\\sqrt{\\omega^{2} - \\omega_c^{2}}}",
                        "hint": "Substitute the dispersion relation into $2\\pi/\\beta$ and tidy.",
                        "deconstruct": [
                            "$\\lambda_g = 2\\pi \\div \\frac{\\sqrt{\\omega^2 - \\omega_c^2}}{c}$.",
                            "As $\\omega$ approaches $\\omega_c$ the denominator goes to zero and $\\lambda_g$ grows without limit.",
                        ],
                    },
                ],
                "closing": r'''
$v_p v_g = c^2$ says the two velocities sit either side of $c$ and move apart together.
Near cutoff the phase pattern sweeps along the axis arbitrarily fast while the energy
barely crawls. Nothing overtakes light, because the phase pattern is not a thing that
can carry a message — only the envelope is, and it moves at $v_g$.
''',
            },
            "lab": {
                "title": "Measure the two velocities, and the delay spread they cause",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Six functions, all in SI, all above cutoff unless stated.

- `beta(f, fc)` returns $(2\pi f/c)\sqrt{1 - (f_c/f)^2}$, or `0.0` at or below cutoff.
- `phase_velocity(f, fc)` returns $c/\sqrt{1 - (f_c/f)^2}$, or `float("inf")` at or
  below cutoff.
- `group_velocity(f, fc)` returns $c\sqrt{1 - (f_c/f)^2}$, or `0.0` at or below cutoff.
- `group_velocity_numeric(f, fc, df)` estimates $d\omega/d\beta$ by a central
  difference: $2\pi \cdot 2 \cdot df$ divided by $\beta(f + df) - \beta(f - df)$.
  Return `float("inf")` if that denominator comes out as zero, so a half-finished
  `beta` gives a wrong answer rather than a crash.
- `group_delay(f, fc, length)` returns `length / group_velocity(f, fc)`.
- `delay_spread(f_lo, f_hi, fc, length)` returns the absolute difference between the
  group delays at the two band edges. That number is the pulse smearing a run of guide
  imposes on a signal occupying that band.

The point of `group_velocity_numeric` is to check your own algebra: it should agree
with the closed form to about ten significant figures.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

C_LIGHT = 2.99792458e8
WR90_FC = 6.5571403762e9


def beta(f, fc):
    """Longitudinal wavenumber in rad/m, zero at or below cutoff."""
    # TODO
    return 0.0


def phase_velocity(f, fc):
    """Speed of the phase pattern along the axis, in m/s."""
    # TODO
    return 0.0


def group_velocity(f, fc):
    """Speed of the envelope along the axis, in m/s."""
    # TODO
    return 0.0


def group_velocity_numeric(f, fc, df):
    """Central-difference estimate of d(omega)/d(beta) at f."""
    # TODO: guard against a zero denominator.
    return 0.0


def group_delay(f, fc, length):
    """Time for the envelope to cross `length` metres of guide."""
    # TODO
    return 0.0


def delay_spread(f_lo, f_hi, fc, length):
    """How much later the low edge of a band arrives than the high edge."""
    # TODO
    return 0.0


if __name__ == "__main__":
    print("vp at 10 GHz:", phase_velocity(10e9, WR90_FC))
    print("vg at 10 GHz:", group_velocity(10e9, WR90_FC))
    print("spread 8-12 GHz over 10 m:", delay_spread(8e9, 12e9, WR90_FC, 10.0), "s")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

C_LIGHT = 2.99792458e8
WR90_FC = 6.5571403762e9


def beta(f, fc):
    """Longitudinal wavenumber in rad/m, zero at or below cutoff."""
    if f <= fc:
        return 0.0
    return 2.0 * np.pi * f / C_LIGHT * float(np.sqrt(1.0 - (fc / f) ** 2))


def phase_velocity(f, fc):
    """Speed of the phase pattern along the axis, in m/s."""
    if f <= fc:
        return float("inf")
    return C_LIGHT / float(np.sqrt(1.0 - (fc / f) ** 2))


def group_velocity(f, fc):
    """Speed of the envelope along the axis, in m/s."""
    if f <= fc:
        return 0.0
    return C_LIGHT * float(np.sqrt(1.0 - (fc / f) ** 2))


def group_velocity_numeric(f, fc, df):
    """Central-difference estimate of d(omega)/d(beta) at f."""
    db = beta(f + df, fc) - beta(f - df, fc)
    if db == 0.0:
        return float("inf")
    return 2.0 * np.pi * (2.0 * df) / db


def group_delay(f, fc, length):
    """Time for the envelope to cross `length` metres of guide."""
    vg = group_velocity(f, fc)
    if vg <= 0.0:
        return float("inf")
    return length / vg


def delay_spread(f_lo, f_hi, fc, length):
    """How much later the low edge of a band arrives than the high edge."""
    return abs(group_delay(f_lo, fc, length) - group_delay(f_hi, fc, length))


if __name__ == "__main__":
    print("vp at 10 GHz:", phase_velocity(10e9, WR90_FC))
    print("vg at 10 GHz:", group_velocity(10e9, WR90_FC))
    print("spread 8-12 GHz over 10 m:", delay_spread(8e9, 12e9, WR90_FC, 10.0), "s")
'''}],
                "hints": [
                    "Write the factor $\\sqrt{1 - (f_c/f)^2}$ once and reuse it — the phase velocity divides by it and the group velocity multiplies by it.",
                    "`group_velocity_numeric` needs `df` small compared with `f` but not so small that the two betas round to the same float. With `f` at 10 GHz, `df` of 1 kHz gives about ten good digits.",
                    "A group velocity of zero would make `group_delay` divide by zero, so return infinity there instead.",
                    "`delay_spread` should be positive: the *lower* frequency is the slower one, because it sits nearer cutoff.",
                ],
                "tests": [
                    {"name": "the phase pattern outruns light", "code": r'''
_vp = phase_velocity(10e9, 6.5571403762e9)
assert abs(_vp - 3.9707119211e8) < 1e2, \
    f"c over sqrt(1 - (6.557/10)^2) is 3.9707e8 m/s, got {_vp:.6e}"
assert _vp > 2.99792458e8, \
    "the phase velocity in a guide is always above c, which is allowed because it carries nothing"
'''},
                    {"name": "the envelope does not", "code": r'''
_vg = group_velocity(10e9, 6.5571403762e9)
assert abs(_vg - 2.2634610533e8) < 1e2, \
    f"c times sqrt(1 - (6.557/10)^2) is 2.2635e8 m/s, got {_vg:.6e}"
assert _vg < 2.99792458e8, "the group velocity must stay below c"
assert group_velocity(6.0e9, 6.5571403762e9) == 0.0, \
    "below cutoff nothing travels, so the group velocity is zero"
'''},
                    {"name": "the product of the two velocities is c squared", "code": r'''
_fc = 6.5571403762e9
for _f in (7e9, 10e9, 12e9, 40e9):
    _p = phase_velocity(_f, _fc) * group_velocity(_f, _fc)
    assert abs(_p / (2.99792458e8 ** 2) - 1.0) < 1e-12, \
        f"vp*vg should equal c^2 at every frequency; at {_f / 1e9} GHz it was {_p:.6e}"
'''},
                    {"name": "the numeric derivative agrees with the algebra", "code": r'''
_fc = 6.5571403762e9
_num = group_velocity_numeric(10e9, _fc, 1e3)
_ana = group_velocity(10e9, _fc)
assert _ana > 0.0, "group_velocity must be finished before this check means anything"
assert abs(_num - _ana) / _ana < 1e-8, \
    f"the central difference should reproduce the closed form: {_num:.10e} against {_ana:.10e}"
assert abs(_num - 2.2634610534e8) < 1e2, \
    f"and it should land on 2.2635e8 m/s, got {_num:.6e}"
'''},
                    {"name": "beta is what the derivative is taken of", "code": r'''
_fc = 6.5571403762e9
_b = beta(10e9, _fc)
assert abs(_b - 158.2382563130) < 1e-6, f"beta at 10 GHz is 158.24 rad/m, got {_b}"
assert beta(6e9, _fc) == 0.0, "there is no real beta below cutoff"
assert beta(12e9, _fc) > _b, "beta rises with frequency, and faster than linearly near cutoff"
'''},
                    {"name": "delay grows as cutoff is approached", "code": r'''
_fc = 6.5571403762e9
_t10 = group_delay(10e9, _fc, 10.0)
assert abs(_t10 - 4.41801284e-8) < 1e-14, \
    f"10 m at 2.2635e8 m/s takes 44.18 ns, got {_t10 * 1e9:.4f} ns"
assert group_delay(7e9, _fc, 10.0) > 2.0 * _t10, \
    "at 7 GHz, just above cutoff, the same 10 m should take more than twice as long"
'''},
                    {"name": "a wide band smears across a long run", "code": r'''
_fc = 6.5571403762e9
_s = delay_spread(8e9, 12e9, _fc, 10.0)
assert abs(_s - 1.839803e-8) < 1e-13, \
    f"8 to 12 GHz over 10 m spreads by 18.40 ns, got {_s * 1e9:.4f} ns"
assert _s > 0.0, "the two edges of the band do not arrive together"
assert abs(delay_spread(8e9, 12e9, _fc, 1.0) * 10.0 - _s) < 1e-15, \
    "the spread is proportional to length, so ten times the guide is ten times the smear"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Push a pulse through a waveguide and measure what it costs",
        "runtime": "python",
        "minutes": 115,
        "brief": r'''
Everything so far has been a formula. This is the formula applied to a signal.

You are given a probe waveform in `guide.py`: a Gaussian-envelope burst at a carrier
you choose, sampled at 80 GS/s over 4096 samples, plus a small seeded noise floor so
the numbers are not suspiciously clean. Build the machinery that carries it down a run
of WR-90 and then measure the two things a link designer actually cares about — when
it arrives, and how much wider it is when it does.

Build:

1. `mode_table(a, b, mmax, nmax)` and `single_mode_band(a, b)`, as in module 3, so you
   can state which band the guide is usable over before you use it.
2. `transfer(freqs, fc, length)` — the complex frequency response of `length` metres
   of guide, as a numpy array the same shape as `freqs`. Above cutoff it is
   $e^{-j\beta \ell}$ with $\beta = (2\pi f/c)\sqrt{1 - (f_c/f)^2}$; at or below cutoff
   it is the real attenuation $e^{-\alpha \ell}$ with
   $\alpha = (2\pi f_c/c)\sqrt{1 - (f/f_c)^2}$.
3. `propagate(x, fs, fc, length)` — real signal in, real signal out, via
   `np.fft.rfft`, a multiply by `transfer` evaluated at `np.fft.rfftfreq`, and
   `np.fft.irfft` with `n=x.size`.
4. `energy_centroid(x, fs)` and `rms_width(x, fs)` — the mean and the standard
   deviation of time under the weight $x^2$.

## Suggested order

Get `transfer` right first and check it by hand at a single frequency: its magnitude
must be exactly 1 above cutoff, because a lossless guide moves energy without taking
any. Then `propagate` is four lines, and the two measurement functions are three each.

## The one trap

The FFT convolves circularly. The probe sits 5 ns into a 51.2 ns window, so anything
delayed by more than about 45 ns wraps round to the start and your centroid becomes
nonsense. Keep the runs short enough that it does not — a few metres of WR-90 at 10 GHz
delays by a few nanoseconds per metre, so this is a real constraint, not a hypothetical.
''',
        "deliverables": [
            "`mode_table` and `single_mode_band`, giving the usable band of the guide before any signal is sent down it.",
            "`transfer(freqs, fc, length)` returning a complex numpy array: unit magnitude above cutoff, real exponential decay below it.",
            "`propagate(x, fs, fc, length)` moving a real waveform through the guide by rfft, multiply, irfft — no loops over samples.",
            "`energy_centroid` and `rms_width`, both weighted by $x^2$, used to measure arrival time and pulse width.",
            "A comment at the top of `main.py` naming the carrier and the run length you chose, and the group delay you expect at that carrier.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy and no signal-processing package.",
            "`transfer` must be vectorised over the frequency array; no Python loop over bins.",
            "The magnitude of the response above cutoff must be exactly 1 to floating-point precision. A guide with perfect walls is lossless.",
            "Do not divide by `f` without guarding the zero-frequency bin, which `np.fft.rfftfreq` always includes.",
            "Keep the run short enough that the delayed pulse stays inside the 51.2 ns window.",
        ],
        "rubric": [
            {"criterion": "Mode analysis", "weight": 20,
             "evidence": "The mode table is complete and sorted, and the single-mode band of WR-90 comes out as 6.557 to 13.114 GHz including the degenerate case of a square guide."},
            {"criterion": "Transfer function", "weight": 30,
             "evidence": "Magnitude is exactly 1 above cutoff and matches the analytic exponential below it, with the zero-frequency bin handled rather than producing a NaN."},
            {"criterion": "Propagation", "weight": 30,
             "evidence": "A burst propagated through the guide is delayed by the group delay to within one per cent, energy is conserved above cutoff, and two runs in series equal one run of the combined length."},
            {"criterion": "Measurement", "weight": 20,
             "evidence": "The centroid and RMS width are computed under an energy weighting and show the pulse widening monotonically with the length of guide it has crossed."},
        ],
        "hints": [
            "`np.fft.rfftfreq(n, 1.0/fs)` gives the frequencies of the bins `np.fft.rfft` returns, in the same order and length.",
            "Build the propagating and the evanescent branches separately with a boolean mask, and substitute a safe dummy frequency into the branch you are about to discard so no division by zero ever happens.",
            "`np.exp(-1j * b * length)` has magnitude 1 for real `b`, which is the lossless condition you are asked to preserve exactly.",
            "For the centroid, the time axis is `np.arange(x.size) / fs` and the weight is `x * x`. Both measurement functions are the same two lines with a different final step.",
            "Check `propagate(x, fs, fc, 0.0)` returns the input back: at zero length the transfer function is all ones and the round trip through the FFT should be exact to about 1e-15.",
        ],
        "files": [
            {"name": "guide.py", "ro": True, "content": r'''
"""The guide, the sampling setup and the probe waveform. Do not edit."""
import numpy as np

C_LIGHT = 2.99792458e8
WR90 = (0.02286, 0.01016)   # a, b in metres — standard X-band guide
FS = 80e9                   # sampling rate, samples per second
NSAMP = 4096                # 51.2 ns of record


def probe(f0, seed=11, fs=FS, n=NSAMP, t0=5e-9, width=0.4e-9):
    """A Gaussian burst at carrier f0, sitting t0 into the record, plus noise.

    The noise is small (1e-4 RMS against a unit envelope) and seeded, so every run
    of the checks sees exactly the same waveform.
    """
    t = np.arange(n) / fs
    envelope = np.exp(-((t - t0) ** 2) / (2.0 * width * width))
    rng = np.random.default_rng(seed)
    return envelope * np.cos(2.0 * np.pi * f0 * t) + 1e-4 * rng.standard_normal(n)
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from guide import C_LIGHT, WR90, FS, NSAMP, probe

# Link chosen:
#   carrier      -> TODO, and why it sits inside the single-mode band
#   run length   -> TODO
#   expected group delay at that carrier -> TODO


def cutoff(a, b, m, n):
    """Cutoff frequency in Hz of the (m, n) mode; infinite for (0, 0)."""
    # TODO
    return 0.0


def mode_table(a, b, mmax, nmax):
    """Every mode up to (mmax, nmax) as (fc, m, n), sorted by cutoff."""
    # TODO
    return []


def single_mode_band(a, b):
    """(f_lo, f_hi): dominant cutoff, and the next distinct cutoff above it."""
    # TODO
    return (0.0, 0.0)


def transfer(freqs, fc, length):
    """Complex response of `length` metres of guide at each frequency in `freqs`."""
    # TODO: propagating above cutoff, evanescent at or below it.
    return np.zeros(np.asarray(freqs, dtype=float).shape, dtype=complex)


def propagate(x, fs, fc, length):
    """Send a real waveform through the guide and return what comes out."""
    # TODO: rfft, multiply by transfer at rfftfreq, irfft back.
    return np.zeros(np.asarray(x, dtype=float).shape)


def energy_centroid(x, fs):
    """Mean arrival time of the energy in x, in seconds."""
    # TODO
    return 0.0


def rms_width(x, fs):
    """Standard deviation of arrival time, weighted by energy, in seconds."""
    # TODO
    return 0.0


if __name__ == "__main__":
    a, b = WR90
    lo, hi = single_mode_band(a, b)
    print(f"single-mode band: {lo / 1e9:.3f} to {hi / 1e9:.3f} GHz")
    x = probe(10e9)
    y = propagate(x, FS, lo, 2.0)
    print("delay:", (energy_centroid(y, FS) - energy_centroid(x, FS)) * 1e9, "ns")
    print("width in:", rms_width(x, FS) * 1e12, "ps")
    print("width out:", rms_width(y, FS) * 1e12, "ps")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from guide import C_LIGHT, WR90, FS, NSAMP, probe

# Link chosen:
#   carrier      -> 10 GHz, comfortably inside the 6.557-13.114 GHz single-mode band
#                   of WR-90 and far enough above cutoff that vg is a sane 0.755 c
#   run length   -> 2 m, which delays the burst by 8.8 ns and leaves the pulse well
#                   inside the 51.2 ns record instead of wrapping round it
#   expected group delay at that carrier -> 2 / (c * sqrt(1 - (6.5571/10)^2))
#                                        =  8.836 ns


def cutoff(a, b, m, n):
    """Cutoff frequency in Hz of the (m, n) mode; infinite for (0, 0)."""
    if m == 0 and n == 0:
        return float("inf")
    return 0.5 * C_LIGHT * float(np.sqrt((m / a) ** 2 + (n / b) ** 2))


def mode_table(a, b, mmax, nmax):
    """Every mode up to (mmax, nmax) as (fc, m, n), sorted by cutoff."""
    rows = []
    for m in range(mmax + 1):
        for n in range(nmax + 1):
            if m == 0 and n == 0:
                continue
            rows.append((cutoff(a, b, m, n), m, n))
    rows.sort()
    return rows


def single_mode_band(a, b):
    """(f_lo, f_hi): dominant cutoff, and the next distinct cutoff above it."""
    rows = mode_table(a, b, 3, 3)
    lo = rows[0][0]
    for fc, _m, _n in rows:
        if fc > lo * (1.0 + 1e-12):
            return (lo, fc)
    return (lo, float("inf"))


def transfer(freqs, fc, length):
    """Complex response of `length` metres of guide at each frequency in `freqs`."""
    f = np.asarray(freqs, dtype=float)
    H = np.zeros(f.shape, dtype=complex)
    above = f > fc

    # substitute a harmless frequency into the branch that is about to be discarded,
    # so neither the division nor the square root ever sees an invalid argument
    fa = np.where(above, f, 2.0 * fc)
    b = 2.0 * np.pi * fa / C_LIGHT * np.sqrt(np.maximum(1.0 - (fc / fa) ** 2, 0.0))
    H[above] = np.exp(-1j * b[above] * length)

    fb = np.where(above, 0.0, f)
    al = 2.0 * np.pi * fc / C_LIGHT * np.sqrt(np.maximum(1.0 - (fb / fc) ** 2, 0.0))
    H[~above] = np.exp(-al[~above] * length)
    return H


def propagate(x, fs, fc, length):
    """Send a real waveform through the guide and return what comes out."""
    x = np.asarray(x, dtype=float)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(x.size, 1.0 / fs)
    return np.fft.irfft(X * transfer(f, fc, length), n=x.size)


def energy_centroid(x, fs):
    """Mean arrival time of the energy in x, in seconds."""
    x = np.asarray(x, dtype=float)
    w = x * x
    total = float(w.sum())
    if total <= 0.0:
        return 0.0
    t = np.arange(x.size) / fs
    return float((t * w).sum() / total)


def rms_width(x, fs):
    """Standard deviation of arrival time, weighted by energy, in seconds."""
    x = np.asarray(x, dtype=float)
    w = x * x
    total = float(w.sum())
    if total <= 0.0:
        return 0.0
    t = np.arange(x.size) / fs
    mu = (t * w).sum() / total
    return float(np.sqrt((((t - mu) ** 2) * w).sum() / total))


if __name__ == "__main__":
    a, b = WR90
    lo, hi = single_mode_band(a, b)
    print(f"single-mode band: {lo / 1e9:.3f} to {hi / 1e9:.3f} GHz")
    x = probe(10e9)
    y = propagate(x, FS, lo, 2.0)
    print("delay:", (energy_centroid(y, FS) - energy_centroid(x, FS)) * 1e9, "ns")
    print("width in:", rms_width(x, FS) * 1e12, "ps")
    print("width out:", rms_width(y, FS) * 1e12, "ps")
'''},
        ],
        "tests": [
            {"name": "the usable band of WR-90 is found before anything is sent", "code": r'''
from guide import WR90
_lo, _hi = single_mode_band(*WR90)
assert abs(_lo - 6.5571403762e9) < 1e3, \
    f"the band opens at the TE10 cutoff of 6.5571 GHz, got {_lo / 1e9:.4f} GHz"
assert abs(_hi - 1.3114280752e10) < 1e3, \
    f"and closes where TE20 arrives at 13.114 GHz, got {_hi / 1e9:.4f} GHz"
_t = mode_table(*WR90, 2, 2)
assert [(m, n) for _f, m, n in _t[:3]] == [(1, 0), (2, 0), (0, 1)], \
    f"the three lowest modes are TE10, TE20, TE01 in that order, got {[(m, n) for _f, m, n in _t[:3]]}"
'''},
            {"name": "a lossless guide passes what it passes without loss", "code": r'''
import numpy as np
_fc = 6.5571403762e9
_H = transfer(np.array([7e9, 10e9, 12e9, 30e9]), _fc, 2.0)
assert _H.shape == (4,), f"transfer should be shaped like its input, got {_H.shape}"
for _h, _f in zip(_H, [7e9, 10e9, 12e9, 30e9]):
    assert abs(abs(_h) - 1.0) < 1e-12, \
        f"above cutoff the magnitude must be exactly 1; at {_f / 1e9} GHz it was {abs(_h)}"
assert abs(_H[1] - np.exp(-1j * 158.2382563130 * 2.0)) < 1e-6, \
    "the phase must be -beta*length, with beta = 158.238 rad/m at 10 GHz"
'''},
            {"name": "below cutoff the guide is a wall, and DC is handled", "code": r'''
import numpy as np
_fc = 6.5571403762e9
_H = transfer(np.array([0.0, 4e9]), _fc, 0.05)
assert np.all(np.isfinite(_H)), \
    "the zero-frequency bin must not produce a NaN — guard the division by f"
assert abs(_H[1].imag) < 1e-15, "an evanescent mode has no phase progression, only decay"
assert abs(abs(_H[1]) - 0.0043188298) < 1e-8, \
    f"5 cm at 4 GHz should attenuate to 0.00432, got {abs(_H[1]):.7f}"
assert abs(abs(_H[0]) - 0.0010370501) < 1e-8, \
    f"and DC, furthest below cutoff, to 0.00104, got {abs(_H[0]):.7f}"
'''},
            {"name": "zero length changes nothing", "code": r'''
import numpy as np
from guide import FS, probe
_x = probe(10e9)
_y = propagate(_x, FS, 6.5571403762e9, 0.0)
assert np.asarray(_y).shape == _x.shape, f"the output must match the input length, got {np.asarray(_y).shape}"
assert np.abs(np.asarray(_y) - _x).max() < 1e-12, \
    "with no guide at all, rfft then irfft should hand the waveform straight back"
'''},
            {"name": "the burst arrives at the group velocity", "code": r'''
import numpy as np
from guide import FS, probe, C_LIGHT
_fc = 6.5571403762e9
_x = probe(10e9)
_y = propagate(_x, FS, _fc, 2.0)
_t_in = energy_centroid(_x, FS)
_t_out = energy_centroid(_y, FS)
assert abs(_t_in - 5.0e-9) < 5e-11, \
    f"the probe sits 5 ns into the record, so its centroid should be there, got {_t_in * 1e9:.4f} ns"
_vg = C_LIGHT * np.sqrt(1.0 - (_fc / 10e9) ** 2)
_want = 2.0 / _vg
_got = _t_out - _t_in
assert abs(_got - _want) / _want < 0.01, \
    f"2 m at vg = 2.263e8 m/s is 8.836 ns of delay, measured {_got * 1e9:.4f} ns"
'''},
            {"name": "no energy is lost inside the band", "code": r'''
import numpy as np
from guide import FS, probe
_x = np.asarray(probe(10e9), dtype=float)
_y = np.asarray(propagate(_x, FS, 6.5571403762e9, 2.0), dtype=float)
_ein = float((_x * _x).sum())
_eout = float((_y * _y).sum())
assert _ein > 1.0, "the probe should carry real energy before anything is propagated"
assert abs(_eout / _ein - 1.0) < 1e-3, \
    f"a lossless guide conserves energy above cutoff: in {_ein:.4f}, out {_eout:.4f}"
'''},
            {"name": "the pulse widens the further it goes", "code": r'''
import numpy as np
from guide import FS, probe
_fc = 6.5571403762e9
_x = probe(10e9)
_w0 = rms_width(_x, FS)
_w1 = rms_width(propagate(_x, FS, _fc, 1.0), FS)
_w3 = rms_width(propagate(_x, FS, _fc, 3.0), FS)
assert abs(_w0 - 2.8441955603e-10) < 1e-13, \
    f"the undisturbed burst is 284.4 ps wide by this measure, got {_w0 * 1e12:.2f} ps"
assert _w1 > _w0, f"one metre should already widen it: {_w1 * 1e12:.2f} against {_w0 * 1e12:.2f} ps"
assert _w3 > _w1 * 1.2, \
    f"three metres should widen it substantially more: {_w3 * 1e12:.2f} against {_w1 * 1e12:.2f} ps"
'''},
            {"name": "two runs in series equal one long run", "code": r'''
import numpy as np
from guide import FS, probe
_fc = 6.5571403762e9
_x = probe(10e9)
_one = np.asarray(propagate(_x, FS, _fc, 2.0), dtype=float)
_two = np.asarray(propagate(propagate(_x, FS, _fc, 1.0), FS, _fc, 1.0), dtype=float)
assert np.abs(_one).max() > 0.1, "the propagated burst should not be empty"
assert np.abs(_one - _two).max() < 1e-6, \
    "a guide is linear and time-invariant, so 1 m twice must equal 2 m once"
'''},
            {"name": "driving below cutoff gets almost nothing through", "code": r'''
import numpy as np
from guide import FS, probe
_fc = 6.5571403762e9
_x = np.asarray(probe(4e9), dtype=float)
_y = np.asarray(propagate(_x, FS, _fc, 0.05), dtype=float)
_ratio = float((_y * _y).sum()) / float((_x * _x).sum())
assert _ratio < 1e-4, \
    f"5 cm of guide below cutoff should reject the burst, but {_ratio:.3e} of the energy got through"
assert _ratio > 1e-7, \
    "some energy must survive: the probe's noise floor is broadband and part of it lies above cutoff"
'''},
        ],
    },
}
