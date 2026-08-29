"""EMAG530 — Optical Waveguides and Photonics.

Same authoring rules as CTRL510, which is the reference course:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only; no scipy, no photonics packages
  * seed every RNG, and every expected value must be one that was computed

Two visualisers carry the course. `smith` is used for the interface modules because
a dielectric boundary is an impedance mismatch and nothing more: the wave impedance
of a medium is eta_0/n, so an index step is a load, total internal reflection is the
rim of the chart, and a guided mode is a transverse round trip that closes. `bode`
is used for the dispersion and budget modules, where the link really is a low-pass
filter and the dashed 0 dB line really is the receiver sensitivity.
"""

COURSE = {
    "id": "EMAG530",
    "title": "Optical Waveguides and Photonics",
    "band": 5,
    "level": "Expert",
    "prereqs": ["EMAG510"],
    "stack": ["Python", "NumPy"],
    "credits": 12,
    "hours": 150,
    "icon": "◎",
    "summary": (
        "A fibre is a dielectric waveguide, and every number a link engineer quotes — "
        "numerical aperture, cutoff, effective index, dispersion, margin — comes from "
        "solving Maxwell's equations in a slab and then admitting how much of the answer "
        "survives contact with a real cable. This course derives the slab eigenvalue "
        "equation from total internal reflection, solves it numerically, and follows the "
        "consequences out to the point where you have to say how far and how fast a link "
        "will actually run."
    ),
    "outcomes": [
        "Derive the critical angle, the numerical aperture and the acceptance cone from Snell's law, and compute the Fresnel loss at an end face.",
        "State and solve the symmetric slab eigenvalue equation numerically, and read the single-mode condition off the normalised frequency V.",
        "Separate modal from chromatic dispersion, combine them in quadrature, and convert a pulse spread into a bit rate.",
        "Build a link loss budget from attenuation, splices, connectors and margin, and decide whether a given link is loss-limited or dispersion-limited.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that sizes a single-mode link end to end and names the effect that limits it.",
    "reading": [
        "*Fiber-Optic Communication Systems*, Agrawal — chapters 2 and 5.",
        "*Optical Waveguide Theory*, Snyder & Love — for the slab eigenvalue equation done properly.",
        "*Fundamentals of Photonics*, Saleh & Teich — chapter 8 for the ray picture alongside the modal one.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Total internal reflection and the numerical aperture",
            "summary": "Guiding is one inequality on an angle. Everything a data sheet says about coupling follows from it.",
            "concepts": [
                "Snell's law at the core–cladding boundary, and the critical angle $\\theta_c = \\arcsin(n_2/n_1)$ as the point where the refracted ray runs along the interface.",
                "The acceptance cone: $n_0\\sin\\theta_a = \\sqrt{n_1^2 - n_2^2}$, and the definition $\\mathrm{NA} = n_0\\sin\\theta_a$.",
                "The relative index difference $\\Delta = (n_1-n_2)/n_1$, and why $\\mathrm{NA} \\approx n_1\\sqrt{2\\Delta}$ for the weakly guiding fibres that are actually manufactured.",
                "A dielectric boundary is an impedance step: the wave impedance is $\\eta_0/n$, so an index ratio *is* a normalised load.",
                "Fresnel reflection at normal incidence — 3.5 per cent per bare silica–air face, which is a real term in a real budget.",
                "Why total internal reflection is lossless in magnitude but not in phase, and why that phase is the whole story in module 2.",
            ],
            "sandbox": {
                "title": "An index step is a mismatched load",
                "visualiser": "smith",
                "minutes": 9,
                "initial": {"rl": 73, "xl": 0, "len": 0},
                "brief": r'''
The wave impedance of a dielectric is $\eta = \eta_0/n$, so putting medium 2 against
medium 1 presents a normalised load of $n_1/n_2$. Read the centre of the chart as the
core itself and the load as whatever is on the far side of the boundary.

The chart opens at $R = 73\ \Omega$, which is $1.46 \times 50\ \Omega$ — a silica end
face looking into air.
''',
                "notice": [
                    "The readout gives $|\\Gamma| = 0.187$ and 14.6 dB return loss. Square the reflection coefficient and you have 3.5 per cent of the power coming straight back out of a bare fibre facet — the number every connector data sheet is quietly fighting.",
                    "Drag load $R$ down to 50 $\\Omega$. The dot collapses onto the centre and $|\\Gamma|$ reads zero: that is index-matching gel, chosen so the two media present the same wave impedance.",
                    "Now set load $R$ to its minimum and push load $X$ to +200 $\\Omega$. The dot climbs to the rim, where $|\\Gamma| = 0.995$ and 99 per cent of the power returns. A purely reactive load would reflect all of it and keep only the phase, and the last 1 per cent is only the $R = 2\\ \\Omega$ the slider cannot dial away — that is exactly what an interface does beyond the critical angle.",
                    "Move the line-length slider anywhere you like. The dot travels clockwise around the dashed circle and the reported $|\\Gamma|$ never changes. Propagation moves the phase of a reflection and never its magnitude, which is why you cannot fix a mismatch by adding fibre.",
                ],
            },
            "derive": {
                "title": "From Snell's law to the numerical aperture",
                "minutes": 14,
                "vars": ["n_0", "n_1", "n_2", "theta_c", "theta_a", "NA", "Delta", "R"],
                "brief": r'''
A step-index guide: core index $n_1$, cladding index $n_2 < n_1$, surrounded by a
launch medium of index $n_0$. A ray enters the flat end face at $\theta_a$ from the
axis, refracts, and then meets the core–cladding boundary at some angle.

We want the largest $\theta_a$ that still leaves the ray trapped.
''',
                "steps": [
                    {
                        "prompt": "At the core–cladding boundary the refracted ray grazes along the interface when the transmission angle reaches 90°. Write $\\sin\\theta_c$ in terms of $n_1$ and $n_2$.",
                        "given": "Snell's law across that boundary reads $n_1\\sin\\theta_c = n_2\\sin 90°$.",
                        "answer": "\\frac{n_2}{n_1}",
                        "hint": "Put $\\sin 90° = 1$ and divide through by $n_1$.",
                        "deconstruct": [
                            "$n_1\\sin\\theta_c = n_2 \\cdot 1$.",
                            "Divide both sides by $n_1$.",
                        ],
                    },
                    {
                        "prompt": "A ray entering at $\\theta_a$ refracts to $\\theta_r$ inside the core, and hits the boundary at $90° - \\theta_r$. Setting that equal to $\\theta_c$ gives the worst ray that still guides. Write $n_0\\sin\\theta_a$ in terms of $n_1$ and $n_2$.",
                        "given": "At the end face, $n_0\\sin\\theta_a = n_1\\sin\\theta_r$, and $\\sin\\theta_r = \\cos\\theta_c$.",
                        "answer": "\\sqrt{n_1^2 - n_2^2}",
                        "hint": "$\\cos\\theta_c = \\sqrt{1 - \\sin^2\\theta_c}$, and you already have $\\sin\\theta_c$.",
                        "deconstruct": [
                            "$\\cos\\theta_c = \\sqrt{1 - (n_2/n_1)^2}$.",
                            "So $n_0\\sin\\theta_a = n_1\\sqrt{1 - n_2^2/n_1^2}$.",
                            "Take the $n_1$ inside the root, where it becomes $n_1^2$.",
                        ],
                    },
                    {
                        "prompt": "That quantity is the definition of the numerical aperture. Manufactured fibre is weakly guiding, so with $\\Delta = (n_1-n_2)/n_1$ and $n_1 + n_2 \\approx 2n_1$, write $\\mathrm{NA}$ in terms of $n_1$ and $\\Delta$.",
                        "answer": "n_1\\sqrt{2\\Delta}",
                        "hint": "Factor the difference of two squares first: $n_1^2 - n_2^2 = (n_1-n_2)(n_1+n_2)$.",
                        "deconstruct": [
                            "$n_1 - n_2 = n_1\\Delta$ by the definition of $\\Delta$.",
                            "$n_1 + n_2 \\approx 2n_1$ when the two indices differ by well under a per cent.",
                            "So $n_1^2 - n_2^2 \\approx 2n_1^2\\Delta$, and the square root of that is $n_1\\sqrt{2\\Delta}$.",
                        ],
                    },
                    {
                        "prompt": "None of that light gets in until it crosses the end face. Write the fraction $R$ of power reflected at normal incidence between the launch medium $n_0$ and the core $n_1$.",
                        "given": "The field reflection coefficient at normal incidence is $(\\eta_1 - \\eta_0)/(\\eta_1 + \\eta_0)$ with $\\eta = \\eta_0/n$, and power goes as the square of it.",
                        "answer": "\\frac{(n_1 - n_0)^2}{(n_1 + n_0)^2}",
                        "hint": "Substituting $\\eta = \\eta_0/n$ turns the impedance ratio into an index ratio with the sign flipped; then square it.",
                        "deconstruct": [
                            "$\\eta_1 - \\eta_0 = \\eta_0(1/n_1 - 1/n_0)$, and the common factor cancels in the ratio.",
                            "That leaves $(n_0 - n_1)/(n_0 + n_1)$ for the field.",
                            "Power is the square, and squaring kills the sign, so either ordering gives the same $R$.",
                        ],
                    },
                ],
                "closing": r'''
Two results worth holding on to. The numerical aperture depends only on the index
*difference*, not on either index alone, which is why a 1 per cent change in $\Delta$
matters far more than a 1 per cent change in $n_1$. And $R$ is symmetric in the two
indices, so a fibre facet loses the same 3.5 per cent whether the light is going in
or coming out.
''',
            },
            "lab": {
                "title": "The acceptance cone and the end face",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Five functions, all of them one line once you have the derivation in front of you.

- `critical_angle(n1, n2)` — radians from the boundary normal.
- `numerical_aperture(n1, n2)` — the NA of a step-index guide.
- `acceptance_angle(n1, n2, n0)` — the half-angle of the launch cone, in radians.
- `fresnel_normal(na, nb)` — the *power* fraction reflected at normal incidence.
- `single_mode_half_width(lam0, n1, n2)` — the largest slab half-width $a$ that still
  carries one mode per polarisation, which is $\lambda_0/(4\,\mathrm{NA})$. Module 2
  derives that bound; here just use it.

Work in radians throughout. `np.arcsin` returns `nan` for an argument above 1 rather
than raising, which can happen for a large NA launched from air, so clip the argument
into $[-1, 1]$ before calling it and the failure becomes a saturated angle instead of
a silent `nan`.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def critical_angle(n1, n2):
    """Smallest angle from the boundary normal that is totally internally reflected."""
    # TODO: Snell's law with the refracted ray at 90 degrees.
    return 0.0


def numerical_aperture(n1, n2):
    """NA of a step-index guide with core n1 and cladding n2."""
    # TODO
    return 0.0


def acceptance_angle(n1, n2, n0=1.0):
    """Half-angle of the cone that couples into the guide, in radians."""
    # TODO: NA = n0 * sin(theta_a). Clip before arcsin.
    return 0.0


def fresnel_normal(na, nb):
    """Fraction of power reflected at normal incidence between two media."""
    # TODO
    return 0.0


def single_mode_half_width(lam0, n1, n2):
    """Largest slab half-width carrying one mode per polarisation."""
    # TODO
    return 0.0


if __name__ == "__main__":
    n1, n2 = 1.48, 1.46
    print("critical angle:", round(critical_angle(n1, n2), 6), "rad")
    print("NA:", round(numerical_aperture(n1, n2), 6))
    print("acceptance half-angle:", round(np.degrees(acceptance_angle(n1, n2)), 3), "deg")
    print("bare facet reflects:", round(100 * fresnel_normal(1.46, 1.0), 3), "per cent")
    print("single-mode half-width at 1550 nm:",
          round(1e6 * single_mode_half_width(1.55e-6, n1, n2), 4), "um")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def critical_angle(n1, n2):
    """Smallest angle from the boundary normal that is totally internally reflected."""
    return float(np.arcsin(np.clip(n2 / n1, -1.0, 1.0)))


def numerical_aperture(n1, n2):
    """NA of a step-index guide with core n1 and cladding n2."""
    return float(np.sqrt(n1 * n1 - n2 * n2))


def acceptance_angle(n1, n2, n0=1.0):
    """Half-angle of the cone that couples into the guide, in radians."""
    s = numerical_aperture(n1, n2) / n0
    return float(np.arcsin(np.clip(s, -1.0, 1.0)))


def fresnel_normal(na, nb):
    """Fraction of power reflected at normal incidence between two media."""
    return float(((na - nb) / (na + nb)) ** 2)


def single_mode_half_width(lam0, n1, n2):
    """Largest slab half-width carrying one mode per polarisation."""
    return float(lam0 / (4.0 * numerical_aperture(n1, n2)))


if __name__ == "__main__":
    n1, n2 = 1.48, 1.46
    print("critical angle:", round(critical_angle(n1, n2), 6), "rad")
    print("NA:", round(numerical_aperture(n1, n2), 6))
    print("acceptance half-angle:", round(np.degrees(acceptance_angle(n1, n2)), 3), "deg")
    print("bare facet reflects:", round(100 * fresnel_normal(1.46, 1.0), 3), "per cent")
    print("single-mode half-width at 1550 nm:",
          round(1e6 * single_mode_half_width(1.55e-6, n1, n2), 4), "um")
'''}],
                "hints": [
                    "`np.arcsin(n2 / n1)` is the critical angle, and it is measured from the normal, not from the interface.",
                    "The NA is `np.sqrt(n1**2 - n2**2)` — the difference of the squares, never the difference of the indices.",
                    "`fresnel_normal` squares a ratio, so it does not care which index you pass first. Check that your version agrees.",
                ],
                "tests": [
                    {"name": "a bigger index step lowers the critical angle", "code": r'''
_a = critical_angle(1.48, 1.46)
assert abs(_a - 1.406211640313002) < 1e-9, \
    f"arcsin(1.46/1.48) is 1.406212 rad measured from the normal, got {_a}"
_b = critical_angle(1.48, 1.40)
assert _b < _a, \
    "rays beyond theta_c are the trapped ones, so a bigger index step lowers theta_c and widens the guided range"
'''},
                    {"name": "the numerical aperture uses the difference of squares", "code": r'''
_na = numerical_aperture(1.48, 1.46)
assert abs(_na - 0.2424871130596432) < 1e-12, \
    f"NA = sqrt(1.48^2 - 1.46^2) = 0.2424871, got {_na} — did you subtract the indices instead?"
assert abs(numerical_aperture(1.46, 1.46)) < 1e-15, \
    "with no index step there is no guiding and the NA is zero"
'''},
                    {"name": "the acceptance cone matches the NA it came from", "code": r'''
import numpy as np
_th = acceptance_angle(1.48, 1.46, 1.0)
assert abs(_th - 0.24492865843840209) < 1e-9, \
    f"arcsin(NA) is 0.2449287 rad, about 14.03 degrees, got {_th}"
assert abs(np.sin(_th) - numerical_aperture(1.48, 1.46)) < 1e-12, \
    "NA is by definition n0*sin(theta_a), so the sine must reproduce it exactly"
_dense = acceptance_angle(1.48, 1.46, 1.45)
assert abs(_dense - 0.16802195847270013) < 1e-9, \
    f"launching from n0 = 1.45 narrows the cone to 0.168 rad, got {_dense}"
'''},
                    {"name": "a bare facet returns three and a half per cent", "code": r'''
_r = fresnel_normal(1.46, 1.0)
assert abs(_r - 0.034965959415691715) < 1e-12, \
    f"((1.46-1)/(1.46+1))^2 = 0.0349660, got {_r} — this is power, so it is squared"
assert abs(fresnel_normal(1.0, 1.46) - _r) < 1e-15, \
    "squaring kills the sign, so the reflectance cannot depend on which index comes first"
assert abs(fresnel_normal(1.46, 1.46)) < 1e-15, \
    "matched media present no impedance step and reflect nothing"
'''},
                    {"name": "the single-mode bound rules out the guide we started with", "code": r'''
_a = single_mode_half_width(1.55e-6, 1.48, 1.46)
assert abs(_a - 1.5980230665069973e-06) < 1e-14, \
    f"lambda/(4*NA) = 1.598 um at 1550 nm, got {_a}"
assert _a < 2.0e-6, \
    "a 2 um half-width slab is above the bound, so it is not single-mode at 1550 nm"
assert single_mode_half_width(1.31e-6, 1.48, 1.46) < _a, \
    "a shorter wavelength needs a narrower core to stay single-mode"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "The slab waveguide eigenvalue equation",
            "summary": "Only some angles survive a round trip across the guide. Those are the modes, and finding them is a root-finding problem.",
            "concepts": [
                "Transverse resonance: a mode is a transverse round trip whose total phase — two wall reflections plus the crossing — is a multiple of $2\\pi$.",
                "The transverse wavenumbers $\\kappa = k_0\\sqrt{n_1^2 - n_e^2}$ in the core and $\\gamma = k_0\\sqrt{n_e^2 - n_2^2}$ in the cladding, and the constraint $\\kappa^2 + \\gamma^2 = k_0^2(n_1^2-n_2^2)$.",
                "The symmetric slab eigenvalue equation $u\\tan(u - m\\pi/2) = w$, with $u = \\kappa a$, $w = \\gamma a$, $u^2 + w^2 = V^2$.",
                "The normalised frequency $V = k_0 a\\,\\mathrm{NA}$, and cutoff at $V = m\\pi/2$ — so the mode count is $\\lfloor 2V/\\pi \\rfloor + 1$ and the fundamental mode never cuts off.",
                "The normalised guide index $b = (w/V)^2$, and recovering $n_e$ from it.",
                "Why the circular step-index fibre has the same structure with cutoff at $V = 2.405$, the first zero of $J_0$.",
            ],
            "sandbox": {
                "title": "A mode is a round trip that closes",
                "visualiser": "smith",
                "minutes": 10,
                "initial": {"rl": 2, "xl": 120, "len": 0},
                "brief": r'''
Look across the guide rather than along it. The core is a short transmission line
whose two ends are the core–cladding walls, and beyond the critical angle each wall
is a near-perfect reflector with a phase.

The chart opens on a nearly reactive load: $R$ at its minimum, $X$ at 120 $\Omega$.
The line-length slider is now the transverse crossing, not distance down the fibre.
''',
                "notice": [
                    "The readout gives $|\\Gamma| = 0.988$ and a VSWR near 169:1, so about 98 per cent of the power returns from the wall. The missing 2 per cent is the residual $R = 2\\ \\Omega$ the slider cannot go below; a real wall beyond the critical angle is purely reactive, returning all of it and keeping only the phase.",
                    "Take the line length from 0 to 0.5 $\\lambda$. The accent dot makes exactly one full circuit and lands back on the grey load dot: half a wavelength of line is $360°$ of *round-trip* phase, because the wave crosses it twice. A guided mode exists only at the transverse angles where that circuit closes.",
                    "Stop at 0.25 $\\lambda$. The dot is now diametrically opposite the load, which is the same as inverting the normalised impedance. That inversion is the quarter-wave transformer, and it is how an anti-reflection coating on an end face is designed.",
                    "Raise load $R$ towards 50 $\\Omega$ with $X$ still at 120. The dashed circle shrinks from 0.988 to 0.768: the wall is now letting power through. A leaky wall cannot support a mode, which is the whole reason guiding needs total internal reflection rather than merely strong reflection.",
                ],
            },
            "derive": {
                "title": "Normalised frequency and the single-mode condition",
                "minutes": 16,
                "vars": ["k_0", "n_1", "n_2", "n_e", "kappa", "gamma", "a", "V", "b",
                         "lambda_0", "NA", "beta"],
                "brief": r'''
A symmetric slab: core index $n_1$ over $-a < x < a$, cladding $n_2$ on both sides.
A guided mode propagates as $e^{-j\beta z}$ with $\beta = k_0 n_e$, where $k_0 =
2\pi/\lambda_0$ and $n_e$ is the effective index. Guiding requires $n_2 < n_e < n_1$.

Inside the core the field oscillates across $x$ with transverse wavenumber $\kappa$;
outside it decays with rate $\gamma$.
''',
                "steps": [
                    {
                        "prompt": "The wave equation in the core requires $\\kappa^2 + \\beta^2 = k_0^2 n_1^2$. Write $\\kappa$ in terms of $k_0$, $n_1$ and $n_e$.",
                        "answer": "k_0\\sqrt{n_1^2 - n_e^2}",
                        "hint": "Substitute $\\beta = k_0 n_e$, then take $k_0^2$ outside the root.",
                        "deconstruct": [
                            "$\\kappa^2 = k_0^2 n_1^2 - \\beta^2 = k_0^2 n_1^2 - k_0^2 n_e^2$.",
                            "Factor $k_0^2$ out and take the positive root.",
                        ],
                    },
                    {
                        "prompt": "In the cladding the same equation holds with $n_2$, but the field decays instead of oscillating, so $\\beta^2 - k_0^2 n_2^2 = \\gamma^2$. Write $\\gamma$ in terms of $k_0$, $n_e$ and $n_2$.",
                        "answer": "k_0\\sqrt{n_e^2 - n_2^2}",
                        "hint": "Identical algebra, with the subtraction the other way round. That ordering is what makes $\\gamma$ real only when $n_e > n_2$.",
                        "deconstruct": [
                            "$\\gamma^2 = k_0^2 n_e^2 - k_0^2 n_2^2$.",
                            "A real $\\gamma$ requires $n_e > n_2$ — otherwise the field radiates instead of decaying.",
                        ],
                    },
                    {
                        "prompt": "Add the squares of those two. The effective index cancels. Write $\\kappa^2 + \\gamma^2$ in terms of $k_0$, $n_1$ and $n_2$.",
                        "answer": "k_0^2 \\cdot (n_1^2 - n_2^2)",
                        "hint": "The $n_e^2$ terms appear with opposite signs.",
                        "deconstruct": [
                            "$\\kappa^2 = k_0^2(n_1^2 - n_e^2)$ and $\\gamma^2 = k_0^2(n_e^2 - n_2^2)$.",
                            "Adding them cancels $k_0^2 n_e^2$ entirely.",
                        ],
                    },
                    {
                        "prompt": "Multiplying by $a^2$ gives $u^2 + w^2 = V^2$ with $u = \\kappa a$, $w = \\gamma a$ and $V = k_0 a\\,\\mathrm{NA}$. The slab stays single-mode while $V < \\pi/2$. Write the largest half-width $a$ that satisfies that, in terms of $\\lambda_0$ and $\\mathrm{NA}$.",
                        "answer": "\\frac{\\lambda_0}{4 \\cdot NA}",
                        "hint": "Put $k_0 = 2\\pi/\\lambda_0$ into $V = k_0 a\\,\\mathrm{NA} = \\pi/2$ and solve for $a$. The $\\pi$ cancels.",
                        "deconstruct": [
                            "$V = (2\\pi/\\lambda_0)\\, a\\,\\mathrm{NA}$.",
                            "Setting that to $\\pi/2$ gives $2 a\\,\\mathrm{NA}/\\lambda_0 = 1/2$.",
                            "So $a = \\lambda_0/(4\\,\\mathrm{NA})$.",
                        ],
                    },
                    {
                        "prompt": "The normalised guide index is defined as $b = (w/V)^2$, which runs from 0 at cutoff to 1 far above it. Write $\\gamma$ in terms of $b$, $V$ and $a$.",
                        "answer": "\\frac{\\sqrt{b} \\cdot V}{a}",
                        "hint": "Invert the definition to get $w$, then remember $w$ is just $\\gamma a$.",
                        "deconstruct": [
                            "$b = (w/V)^2$ gives $w = V\\sqrt{b}$.",
                            "And $w = \\gamma a$, so divide by $a$.",
                        ],
                    },
                ],
                "closing": r'''
$V$ is the only parameter that matters. Two slabs with the same $V$ have the same
mode count, the same $b$ for every mode, and the same field shapes once you measure
$x$ in units of $a$ — which is why every textbook plots $b$ against $V$ and never
against wavelength. The eigenvalue equation itself, $u\tan(u - m\pi/2) = w$, has no
closed form, so the next step is numerical.
''',
            },
            "lab": {
                "title": "Solve the slab eigenvalue equation",
                "runtime": "python",
                "minutes": 38,
                "brief": r'''
Four functions.

- `v_number(a, lam0, n1, n2)` — the normalised frequency $V = (2\pi a/\lambda_0)\,\mathrm{NA}$.
- `mode_count(V)` — mode $m$ exists when $V > m\pi/2$, so the count is
  $\lfloor 2V/\pi \rfloor + 1$. The fundamental mode never cuts off.
- `solve_u(V, m)` — the transverse phase $u = \kappa a$ of mode $m$, found by
  bisection on

  ```text
  f(u) = sqrt(V**2 - u**2) - u * tan(u - m*pi/2)
  ```

  on the interval $(m\pi/2,\ \min((m{+}1)\pi/2,\ V))$. At the left end $\tan$ is zero
  so $f > 0$; at the right end either the root term vanishes or $\tan$ blows up, so
  $f < 0$. Step in from both ends by a small epsilon and bisect 200 times.
- `effective_index(u, V, n1, n2)` — from $w = \sqrt{V^2 - u^2}$ and $b = (w/V)^2$,
  return $n_e = \sqrt{n_2^2 + b\,(n_1^2 - n_2^2)}$.

Do not try to be clever with `np.tan` near its poles. Bisection never evaluates the
endpoints, so bracketing is all the protection you need.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def v_number(a, lam0, n1, n2):
    """Normalised frequency of a symmetric slab of half-width a."""
    # TODO
    return 0.0


def mode_count(V):
    """How many TE modes a symmetric slab of this V supports."""
    # TODO: mode m exists while V > m*pi/2.
    return 0


def solve_u(V, m):
    """Transverse phase kappa*a of mode m, by bisection on the eigenvalue equation."""
    # TODO: bracket on (m*pi/2, min((m+1)*pi/2, V)) and bisect.
    return 0.0


def effective_index(u, V, n1, n2):
    """Effective index of the mode whose transverse phase is u."""
    # TODO: w = sqrt(V**2 - u**2), b = (w/V)**2, then unnormalise.
    return 0.0


if __name__ == "__main__":
    V = v_number(2e-6, 1.55e-6, 1.48, 1.46)
    print("V =", round(V, 6), "->", mode_count(V), "modes")
    for m in range(max(mode_count(V), 0)):
        u = solve_u(V, m)
        print("  m =", m, " u =", round(u, 6),
              " n_e =", round(effective_index(u, V, 1.48, 1.46), 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def v_number(a, lam0, n1, n2):
    """Normalised frequency of a symmetric slab of half-width a."""
    na = np.sqrt(n1 * n1 - n2 * n2)
    return float(2.0 * np.pi * a * na / lam0)


def mode_count(V):
    """How many TE modes a symmetric slab of this V supports."""
    if V <= 0.0:
        return 0
    return int(np.floor(2.0 * V / np.pi)) + 1


def _residual(u, V, m):
    root = np.sqrt(max(V * V - u * u, 0.0))
    return float(root - u * np.tan(u - m * np.pi / 2.0))


def solve_u(V, m):
    """Transverse phase kappa*a of mode m, by bisection on the eigenvalue equation."""
    lo = m * np.pi / 2.0
    hi = min((m + 1) * np.pi / 2.0, V)
    if hi <= lo:
        return 0.0
    eps = 1e-12
    a, b = lo + eps, hi - eps
    fa = _residual(a, V, m)
    for _ in range(200):
        mid = 0.5 * (a + b)
        fm = _residual(mid, V, m)
        if (fa > 0.0) == (fm > 0.0):
            a, fa = mid, fm
        else:
            b = mid
    return float(0.5 * (a + b))


def effective_index(u, V, n1, n2):
    """Effective index of the mode whose transverse phase is u."""
    w = np.sqrt(max(V * V - u * u, 0.0))
    b = (w / V) ** 2
    return float(np.sqrt(n2 * n2 + b * (n1 * n1 - n2 * n2)))


if __name__ == "__main__":
    V = v_number(2e-6, 1.55e-6, 1.48, 1.46)
    print("V =", round(V, 6), "->", mode_count(V), "modes")
    for m in range(max(mode_count(V), 0)):
        u = solve_u(V, m)
        print("  m =", m, " u =", round(u, 6),
              " n_e =", round(effective_index(u, V, 1.48, 1.46), 6))
'''}],
                "hints": [
                    "`mode_count` is `int(np.floor(2*V/np.pi)) + 1` — the `+1` is the fundamental mode, which exists for any $V > 0$.",
                    "Bisection needs the two endpoint signs to differ. Evaluate `f` at `lo + 1e-12` and confirm it is positive before you start.",
                    "`effective_index` never calls `tan`. Once you have `u`, the rest is the constraint $u^2 + w^2 = V^2$ and the definition of $b$.",
                ],
                "tests": [
                    {"name": "modes appear one at a time at V = m*pi/2", "code": r'''
assert mode_count(1.0) == 1, "the fundamental mode has no cutoff, so V = 1 already guides one mode"
assert mode_count(1.5707) == 1, "just below pi/2 there is still only the fundamental mode"
assert mode_count(1.5709) == 2, "the first higher mode turns on the moment V passes pi/2"
assert mode_count(2.0) == 2, f"V = 2 supports 2 modes, got {mode_count(2.0)}"
assert mode_count(5.0) == 4, f"V = 5 supports 4 modes, got {mode_count(5.0)}"
'''},
                    {"name": "the normalised frequency of the guide from module 1", "code": r'''
_V = v_number(2e-6, 1.55e-6, 1.48, 1.46)
assert abs(_V - 1.965924472202252) < 1e-12, \
    f"V = 2*pi*a*NA/lambda = 1.9659245, got {_V}"
assert mode_count(_V) == 2, \
    "V = 1.966 is above pi/2, so this guide is not single-mode at 1550 nm"
'''},
                    {"name": "the fundamental root is where it should be", "code": r'''
_u = solve_u(2.0, 0)
assert abs(_u - 1.0298665293222586) < 1e-9, \
    f"the m = 0 root of u*tan(u) = sqrt(4 - u^2) is 1.0298665, got {_u}"
_u1 = solve_u(2.0, 1)
assert abs(_u1 - 1.895494267033981) < 1e-9, \
    f"the m = 1 root is 1.8954943, got {_u1}"
assert _u < _u1, "higher-order modes always sit at larger u"
'''},
                    {"name": "every root satisfies the eigenvalue equation", "code": r'''
import numpy as np
_V = 5.0
for _m in range(4):
    _u = solve_u(_V, _m)
    _w = np.sqrt(_V * _V - _u * _u)
    _res = _u * np.tan(_u - _m * np.pi / 2.0) - _w
    assert abs(_res) < 1e-8, \
        f"mode {_m}: u*tan(u - m*pi/2) should equal w, residual was {_res:.3e}"
    assert _m * np.pi / 2.0 < _u < min((_m + 1) * np.pi / 2.0, _V), \
        f"mode {_m}: u = {_u} escaped its bracketing interval"
'''},
                    {"name": "effective indices lie between cladding and core", "code": r'''
_V = 2.0
_ne = [effective_index(solve_u(_V, _m), _V, 1.48, 1.46) for _m in range(2)]
assert abs(_ne[0] - 1.474723299977725) < 1e-9, \
    f"the fundamental mode of V = 2 has n_e = 1.4747233, got {_ne[0]}"
assert abs(_ne[1] - 1.4620480128263664) < 1e-9, \
    f"the first higher mode has n_e = 1.4620480, got {_ne[1]}"
for _n in _ne:
    assert 1.46 < _n < 1.48, \
        f"a guided mode must have n2 < n_e < n1, got {_n}"
assert _ne[0] > _ne[1], \
    "higher-order modes are less tightly bound, so their effective index is lower"
'''},
                    {"name": "the fundamental mode tightens as V grows", "code": r'''
_a = effective_index(solve_u(1.0, 0), 1.0, 1.48, 1.46)
_b = effective_index(solve_u(5.0, 0), 5.0, 1.48, 1.46)
assert abs(_a - 1.4691088067779687) < 1e-9, f"V = 1 gives n_e = 1.4691088, got {_a}"
assert abs(_b - 1.4786431755209428) < 1e-9, f"V = 5 gives n_e = 1.4786432, got {_b}"
assert _b > _a, \
    "a larger V binds the fundamental mode harder, pushing n_e towards n1"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Modal and chromatic dispersion",
            "summary": "Different paths and different colours arrive at different times. The pulse widens, and the bit rate follows.",
            "concepts": [
                "Modal dispersion in a step-index multimode guide: the extreme ray travels $n_1/n_2$ times further, giving $\\Delta\\tau/L = n_1(n_1-n_2)/(c\\,n_2) \\approx n_1\\Delta/c$.",
                "Why single-mode fibre has no modal term at all — there is only one path — and why that is the entire reason long-haul fibre is single-mode.",
                "Chromatic dispersion as a coefficient: $\\Delta\\tau = D\\,L\\,\\Delta\\lambda$, with $D$ in ps/(nm·km) and the zero near 1310 nm for standard fibre.",
                "Material and waveguide dispersion as the two contributions to $D$, and how shifting the waveguide term moves the zero.",
                "Independent broadening mechanisms add in quadrature, so the largest one dominates fast.",
                "The rule of thumb $B_{max} = 1/(2\\Delta\\tau)$, and the bandwidth–length product that follows from it.",
            ],
            "sandbox": {
                "title": "A link is a low-pass filter",
                "visualiser": "bode",
                "minutes": 9,
                "initial": {"wn": 20, "zeta": 0.9, "K": 1},
                "brief": r'''
Modulate the optical power, detect it, and plot the received amplitude against
modulation frequency. Pulse spreading is a low-pass: the wider the spread, the lower
the corner. Read $\omega$ here as modulation frequency in whatever units suit the
link, and $\omega_n$ as the corner — the frequency where the phase passes $-90°$. It
is not the 3 dB point: at $\zeta = 0.9$, the damping the chart opens on, the magnitude
at $\omega_n$ is already 5.1 dB down and the 3 dB point sits back at $0.75\,\omega_n$.

Two poles, because a real link has at least two independent band limits — the fibre
and the receiver front end.
''',
                "notice": [
                    "At $\\omega = \\omega_n$ the phase plot reads exactly $-90°$, whatever $\\zeta$ or $K$ you choose. That crossing is what defines the corner; changing the damping tilts the curve around it but never moves it.",
                    "With $K = 1$ the magnitude starts at 0 dB and is 80 dB down two decades above the corner. Forty decibels per decade is the signature of two poles, and it is why a link that is 20 per cent too long is not 20 per cent worse.",
                    "Drop $\\zeta$ to 0.05. The amber dot at the corner climbs to +20 dB and a sharp resonant peak appears. An under-damped channel rings, and ringing in a receiver is intersymbol interference by another name.",
                    "Raise $K$ and watch the phase plot: it does not move at all. Gain and bandwidth are independent here, which is exactly why the power budget and the rise-time budget are computed as separate calculations.",
                ],
            },
            "derive": {
                "title": "From ray paths to a bit rate",
                "minutes": 16,
                "vars": ["L", "n_1", "n_2", "c", "D", "W", "tau_m", "tau_c", "tau_t",
                         "B", "Delta"],
                "brief": r'''
A step-index multimode guide of length $L$. The axial ray goes straight down the
middle; the extreme guided ray bounces at the critical angle. Both travel at speed
$c/n_1$ inside the core, but they cover different distances.

Take the source spectral width to be $W$ and the chromatic dispersion coefficient to
be $D$.
''',
                "steps": [
                    {
                        "prompt": "The extreme ray meets the wall at $\\theta_c$ from the normal, so its path length is $L/\\sin\\theta_c$. Write its transit time in terms of $L$, $n_1$, $n_2$ and $c$.",
                        "given": "Recall $\\sin\\theta_c = n_2/n_1$, and the speed inside the core is $c/n_1$.",
                        "answer": "\\frac{L \\cdot n_1^2}{c \\cdot n_2}",
                        "hint": "Path length is $L n_1/n_2$; multiply by $n_1/c$ to turn distance into time.",
                        "deconstruct": [
                            "$L/\\sin\\theta_c = L n_1/n_2$.",
                            "Time is distance divided by $c/n_1$, which is distance times $n_1/c$.",
                        ],
                    },
                    {
                        "prompt": "The axial ray takes $L n_1/c$. Write the spread $\\tau_m$ between the two, in terms of $L$, $n_1$, $n_2$ and $c$.",
                        "answer": "\\frac{L \\cdot n_1 \\cdot (n_1 - n_2)}{c \\cdot n_2}",
                        "hint": "Subtract, then take out the common factor $L n_1/c$.",
                        "deconstruct": [
                            "$\\tau_m = L n_1^2/(c n_2) - L n_1/c$.",
                            "Factor out $L n_1/c$ to get $(n_1/n_2 - 1)$.",
                            "Put that over the common denominator $n_2$.",
                        ],
                    },
                    {
                        "prompt": "Weakly guiding fibre has $n_2 \\approx n_1$ in the denominator. With $\\Delta = (n_1-n_2)/n_1$, write $\\tau_m$ in terms of $L$, $n_1$, $\\Delta$ and $c$.",
                        "answer": "\\frac{L \\cdot n_1 \\cdot \\Delta}{c}",
                        "hint": "Replace $n_1 - n_2$ by $n_1\\Delta$ and cancel one factor of $n_1$ against the $n_2$ in the denominator.",
                        "deconstruct": [
                            "$L n_1(n_1-n_2)/(c n_2) = L n_1 \\cdot n_1\\Delta/(c n_2)$.",
                            "With $n_2 \\approx n_1$ the ratio $n_1/n_2$ is 1.",
                        ],
                    },
                    {
                        "prompt": "Chromatic dispersion is quoted as a coefficient: delay per unit length per unit spectral width. Write the chromatic spread $\\tau_c$ in terms of $D$, $L$ and $W$.",
                        "answer": "D \\cdot L \\cdot W",
                        "hint": "Read the units of $D$ — ps per nm per km — and multiply until only picoseconds are left.",
                        "deconstruct": [
                            "$D$ has units of time per length per wavelength.",
                            "Multiply by a length and a spectral width and only time survives.",
                        ],
                    },
                    {
                        "prompt": "Modal and chromatic spreading come from unrelated physics, so they add as independent widths. Write the total $\\tau_t$ in terms of $\\tau_m$ and $\\tau_c$.",
                        "answer": "\\sqrt{\\tau_m^2 + \\tau_c^2}",
                        "hint": "Independent variances add; standard deviations do not.",
                        "deconstruct": [
                            "Each mechanism contributes a variance $\\tau^2$.",
                            "Variances of independent contributions add, so the widths combine in quadrature.",
                        ],
                    },
                    {
                        "prompt": "The usual engineering rule allows a pulse to spread over at most half a bit period. Write the maximum bit rate $B$ in terms of $\\tau_t$.",
                        "answer": "\\frac{1}{2 \\cdot \\tau_t}",
                        "hint": "The bit period is $1/B$; require $\\tau_t$ to be at most half of it.",
                        "deconstruct": [
                            "$\\tau_t \\le (1/B)/2$.",
                            "Rearranging for $B$ gives the bound.",
                        ],
                    },
                ],
                "closing": r'''
Put numbers in and the hierarchy is brutal. A 1 km step-index multimode fibre with
$n_1 = 1.48$ and $n_2 = 1.46$ spreads a pulse by 67.6 ns, while chromatic dispersion
over the same kilometre with a 1 nm source contributes 17 ps — four thousand times
smaller. In quadrature the chromatic term is invisible. Kill the modal term by going
single-mode and the roles reverse completely, which is the subject of the capstone.
''',
            },
            "lab": {
                "title": "Pulse spreading and the bit rate it allows",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Engineering units throughout: lengths in km, spectral widths in nm, dispersion
coefficients in ps/(nm·km), and every spread returned in **picoseconds**.

- `modal_spread_ps(n1, n2, l_km)` — the ray-path spread you derived. Convert: the
  length is in km, so multiply by `1e3` for metres and by `1e12` for picoseconds.
- `chromatic_spread_ps(d_ps, l_km, w_nm)` — the three units already cancel, so this
  is a product. Return a non-negative width even when $D$ is negative, as it is
  below the dispersion zero.
- `total_spread_ps(t_modal, t_chromatic)` — in quadrature.
- `max_bitrate(tau_ps)` — bits per second, from a spread in picoseconds. Return
  `float("inf")` for a spread of zero rather than dividing by it.

`C_LIGHT` is already defined for you.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np

C_LIGHT = 2.99792458e8   # m/s


def modal_spread_ps(n1, n2, l_km):
    """Ray-path spread of a step-index multimode guide, in picoseconds."""
    # TODO
    return 0.0


def chromatic_spread_ps(d_ps, l_km, w_nm):
    """Spread from a dispersion coefficient in ps/(nm km), in picoseconds."""
    # TODO
    return 0.0


def total_spread_ps(t_modal, t_chromatic):
    """Combine two independent spreads."""
    # TODO
    return 0.0


def max_bitrate(tau_ps):
    """Largest bit rate, in bits per second, for a spread of tau_ps picoseconds."""
    # TODO: guard the zero-spread case.
    return 0.0


if __name__ == "__main__":
    tm = modal_spread_ps(1.48, 1.46, 1.0)
    tc = chromatic_spread_ps(17.0, 1.0, 1.0)
    tt = total_spread_ps(tm, tc)
    print("modal:", round(tm, 3), "ps")
    print("chromatic:", round(tc, 3), "ps")
    print("total:", round(tt, 3), "ps")
    print("bit rate:", round(max_bitrate(tt) / 1e6, 3), "Mb/s over 1 km")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np

C_LIGHT = 2.99792458e8   # m/s


def modal_spread_ps(n1, n2, l_km):
    """Ray-path spread of a step-index multimode guide, in picoseconds."""
    seconds = (l_km * 1e3) * n1 * (n1 - n2) / (C_LIGHT * n2)
    return float(seconds * 1e12)


def chromatic_spread_ps(d_ps, l_km, w_nm):
    """Spread from a dispersion coefficient in ps/(nm km), in picoseconds."""
    return float(abs(d_ps) * l_km * w_nm)


def total_spread_ps(t_modal, t_chromatic):
    """Combine two independent spreads."""
    return float(np.hypot(t_modal, t_chromatic))


def max_bitrate(tau_ps):
    """Largest bit rate, in bits per second, for a spread of tau_ps picoseconds."""
    if tau_ps <= 0.0:
        return float("inf")
    return float(1.0 / (2.0 * tau_ps * 1e-12))


if __name__ == "__main__":
    tm = modal_spread_ps(1.48, 1.46, 1.0)
    tc = chromatic_spread_ps(17.0, 1.0, 1.0)
    tt = total_spread_ps(tm, tc)
    print("modal:", round(tm, 3), "ps")
    print("chromatic:", round(tc, 3), "ps")
    print("total:", round(tt, 3), "ps")
    print("bit rate:", round(max_bitrate(tt) / 1e6, 3), "Mb/s over 1 km")
'''}],
                "hints": [
                    "`modal_spread_ps` needs two conversions, not one: km to m on the way in, and seconds to ps on the way out.",
                    "`np.hypot(a, b)` is the quadrature sum, and it is more careful about overflow than writing the square root yourself.",
                    "In `max_bitrate` the factor is `2 * tau * 1e-12`. Check the answer against a spread of 850 ps, which should give about 588 Mb/s.",
                ],
                "tests": [
                    {"name": "modal spread is 67.6 ns per kilometre", "code": r'''
_t = modal_spread_ps(1.48, 1.46, 1.0)
assert abs(_t - 67626.69327305007) < 1e-6, \
    f"L*n1*(n1-n2)/(c*n2) is 67626.693 ps over 1 km, got {_t} — check the km and ps conversions"
assert abs(modal_spread_ps(1.48, 1.46, 0.5) - 33813.346636525035) < 1e-6, \
    "modal spread is strictly proportional to length"
assert abs(modal_spread_ps(1.46, 1.46, 1.0)) < 1e-12, \
    "with no index step there is only one path, so there is no modal spread"
'''},
                    {"name": "chromatic spread is a product of its three units", "code": r'''
_t = chromatic_spread_ps(17.0, 50.0, 1.0)
assert abs(_t - 850.0) < 1e-9, \
    f"17 ps/(nm km) over 50 km with a 1 nm source is 850 ps, got {_t}"
assert abs(chromatic_spread_ps(-17.0, 50.0, 1.0) - 850.0) < 1e-9, \
    "below the dispersion zero D is negative, but a pulse width is not"
assert abs(chromatic_spread_ps(17.0, 50.0, 0.1) - 85.0) < 1e-9, \
    "a ten times narrower source gives a ten times smaller spread"
'''},
                    {"name": "independent spreads add in quadrature", "code": r'''
assert abs(total_spread_ps(3.0, 4.0) - 5.0) < 1e-12, \
    f"quadrature of 3 and 4 is 5, got {total_spread_ps(3.0, 4.0)} — not 7"
_t = total_spread_ps(67626.69327305007, 17.0)
assert abs(_t - 67626.69540978027) < 1e-6, \
    f"expected 67626.6954 ps, got {_t}"
assert _t > 67626.69327305007, \
    "adding a second broadening mechanism can only widen the pulse"
'''},
                    {"name": "a spread converts to a bit rate", "code": r'''
import math
_b = max_bitrate(850.0)
assert abs(_b - 588235294.117647) < 1.0, \
    f"1/(2*850 ps) is 588.2 Mb/s, got {_b}"
assert abs(max_bitrate(67626.69327305007) - 7393530.214189182) < 1e-3, \
    "a 67.6 ns spread allows only 7.39 Mb/s"
assert math.isinf(max_bitrate(0.0)), \
    "a pulse that does not spread imposes no bit rate limit, and must not divide by zero"
'''},
                    {"name": "modal dispersion buries the chromatic term", "code": r'''
_tm = modal_spread_ps(1.48, 1.46, 1.0)
_tc = chromatic_spread_ps(17.0, 1.0, 1.0)
assert _tm > 1000.0 * _tc, \
    f"over 1 km of step-index multimode the modal term is ~4000x larger, got {_tm/_tc:.1f}x"
_ratio = max_bitrate(total_spread_ps(_tm, _tc)) / max_bitrate(_tm)
assert abs(_ratio - 1.0) < 1e-4, \
    "in quadrature the chromatic term changes the achievable bit rate by well under 0.01 per cent"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "The loss budget of a link",
            "summary": "Add up every decibel between the laser and the detector, and see what is left.",
            "concepts": [
                "Decibels turn a chain of multiplications into a sum, which is the only reason budgets are tractable by hand.",
                "dBm as an absolute power reference: 0 dBm is 1 mW, and a receiver sensitivity is a dBm number.",
                "The terms: fibre attenuation $\\alpha L$, splice loss, connector loss, and a system margin for ageing, repairs and temperature.",
                "Fresnel loss at an air gap in a connector — two interfaces, about 0.31 dB — and how index-matching gel removes it.",
                "Rearranging the budget for reach rather than margin, which is the form a designer actually needs.",
                "Loss-limited versus dispersion-limited: the reach is the smaller of the two, and knowing which one binds tells you what to fix.",
            ],
            "sandbox": {
                "title": "Margin as the gap above the sensitivity line",
                "visualiser": "bode",
                "minutes": 9,
                "initial": {"wn": 8, "zeta": 0.7, "K": 6},
                "brief": r'''
Same filter, read differently. Take the magnitude curve as received signal level and
the dashed 0 dB line as the receiver sensitivity. Everything above the line works;
everything below it does not.

$K$ now stands for the launched power relative to sensitivity, so the vertical gap at
low frequency is the power margin in decibels, and the frequency where the curve
crosses the line is the fastest the link can run.
''',
                "notice": [
                    "$K = 6$ puts the low-frequency magnitude at $20\\log_{10} 6 = 15.6$ dB above the dashed line. That gap is the whole power budget: subtract fibre, splices, connectors and ageing from it and whatever remains is your margin.",
                    "Lower $K$ to 1. The curve now starts exactly on the dashed line, so the margin is zero before the link has done anything at all — the state a budget with no margin term actually describes.",
                    "Read where the curve crosses the dashed line. At $K = 6$ and $\\zeta = 0.7$ that happens near $2.4\\,\\omega_n$; at $K = 1$ it collapses to $0.2\\,\\omega_n$. Adding fibre lowers $K$, so the same link runs slower as it gets longer — reach and bit rate are the same trade seen twice.",
                    "Push $\\zeta$ down to 0.05. The amber dot at the corner jumps to 35.6 dB above the dashed line — 20 dB above the 15.6 dB the curve started at — and the crossing moves out only slightly, to about $2.6\\,\\omega_n$. A resonant peak buys a little bandwidth on paper and pays for it with overshoot in the eye diagram.",
                ],
            },
            "derive": {
                "title": "Rearranging a budget for reach",
                "minutes": 14,
                "vars": ["P_t", "P_r", "S", "M", "alpha", "L", "N_c", "A_c", "N_s",
                         "A_s", "n_1", "n_g", "R"],
                "brief": r'''
Every term below is in decibels, so the arithmetic is addition. A transmitter
launches $P_t$ dBm into a fibre of attenuation $\alpha$ dB/km and length $L$ km. The
route has $N_c$ connectors at $A_c$ dB each and $N_s$ splices at $A_s$ dB each. The
receiver needs at least $S$ dBm to work.
''',
                "steps": [
                    {
                        "prompt": "Write the total loss between transmitter and receiver in terms of $\\alpha$, $L$, $N_c$, $A_c$, $N_s$ and $A_s$.",
                        "answer": "\\alpha \\cdot L + N_c \\cdot A_c + N_s \\cdot A_s",
                        "hint": "Decibels add. Each category is a count times a per-item loss.",
                        "deconstruct": [
                            "The fibre contributes $\\alpha$ dB for every kilometre.",
                            "Each connector and each splice contributes its own fixed number of decibels.",
                        ],
                    },
                    {
                        "prompt": "The margin $M$ is what is left after the received power has cleared the sensitivity. Write $M$ in terms of $P_t$, $S$ and the loss terms.",
                        "answer": "P_t - S - \\alpha \\cdot L - N_c \\cdot A_c - N_s \\cdot A_s",
                        "hint": "The received power is $P_t$ minus the total loss; the margin is that minus $S$.",
                        "deconstruct": [
                            "$P_r = P_t - (\\alpha L + N_c A_c + N_s A_s)$.",
                            "$M = P_r - S$, and subtracting a bracket flips every sign inside it.",
                        ],
                    },
                    {
                        "prompt": "A designer knows the margin they want and asks how far they can go. Solve the same relation for $L$.",
                        "answer": "\\frac{P_t - S - N_c \\cdot A_c - N_s \\cdot A_s - M}{\\alpha}",
                        "hint": "Isolate the $\\alpha L$ term on one side and divide.",
                        "deconstruct": [
                            "From the previous step, $\\alpha L = P_t - S - N_c A_c - N_s A_s - M$.",
                            "Divide through by $\\alpha$.",
                        ],
                    },
                    {
                        "prompt": "One connector term deserves a closer look. A gap of index $n_g$ between two fibre ends of index $n_1$ reflects at each face. Write the power reflectance $R$ of one such face.",
                        "answer": "\\frac{(n_1 - n_g)^2}{(n_1 + n_g)^2}",
                        "hint": "The same normal-incidence result as module 1, with the gap material in place of air.",
                        "deconstruct": [
                            "The field coefficient is $(n_1 - n_g)/(n_1 + n_g)$.",
                            "Power is its square.",
                        ],
                    },
                    {
                        "prompt": "The light crosses two such faces on its way through the gap, and each passes a fraction $1 - R$. Write the transmitted power fraction in terms of $R$.",
                        "answer": "(1 - R)^2",
                        "hint": "Two independent interfaces in series multiply their transmissions.",
                        "deconstruct": [
                            "The first face passes $1 - R$ of the incident power.",
                            "The second face passes $1 - R$ of what reaches it.",
                            "Ignoring the multiple bounces inside the gap, the product is $(1-R)^2$.",
                        ],
                    },
                ],
                "closing": r'''
With $n_1 = 1.46$ and an air gap, $R = 0.035$ and the pair of faces passes 0.9313 of
the power, which is 0.31 dB. Fill the gap with gel at $n_g = 1.30$ and the same
calculation gives 0.029 dB — a factor of ten, for a substance whose only job is to
have roughly the right index. That is the whole argument for index matching, and it
is the same argument as moving the load to the centre of the Smith chart.
''',
            },
            "lab": {
                "title": "Build a link budget and invert it",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Four functions, all in decibels except the first, which turns indices into decibels.

- `gap_loss_db(n_core, n_gap)` — the loss of a two-face gap, $-10\log_{10}(1-R)^2$
  with $R$ from the derivation. Zero when the indices match.
- `total_loss_db(alpha_db_km, l_km, n_conn, conn_db, n_splice, splice_db)` — the sum.
- `power_margin_db(p_tx_dbm, sens_dbm, loss_db)` — what is left, which may be
  negative for a link that does not close.
- `max_reach_km(p_tx_dbm, sens_dbm, alpha_db_km, fixed_db, margin_db)` — the same
  relation solved for length, where `fixed_db` is the total of all the
  length-independent losses. Return `float("inf")` if the attenuation is zero or
  negative rather than dividing by it.

Use `np.log10`.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def gap_loss_db(n_core, n_gap):
    """Loss in dB of a gap of index n_gap between two fibre ends of index n_core."""
    # TODO: Fresnel at each of the two faces, then convert to dB.
    return 0.0


def total_loss_db(alpha_db_km, l_km, n_conn, conn_db, n_splice, splice_db):
    """Total loss between transmitter and receiver, in dB."""
    # TODO
    return 0.0


def power_margin_db(p_tx_dbm, sens_dbm, loss_db):
    """Decibels left over once the receiver has what it needs."""
    # TODO
    return 0.0


def max_reach_km(p_tx_dbm, sens_dbm, alpha_db_km, fixed_db, margin_db):
    """Longest fibre length that still leaves the requested margin."""
    # TODO: guard a non-positive attenuation.
    return 0.0


if __name__ == "__main__":
    loss = total_loss_db(0.25, 80.0, 2, 0.5, 8, 0.05)
    print("air gap costs:", round(gap_loss_db(1.46, 1.0), 4), "dB")
    print("total loss over 80 km:", round(loss, 3), "dB")
    print("margin from 0 dBm into a -28 dBm receiver:",
          round(power_margin_db(0.0, -28.0, loss), 3), "dB")
    print("reach with 3 dB margin:",
          round(max_reach_km(0.0, -28.0, 0.25, 1.4, 3.0), 3), "km")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def gap_loss_db(n_core, n_gap):
    """Loss in dB of a gap of index n_gap between two fibre ends of index n_core."""
    r = ((n_core - n_gap) / (n_core + n_gap)) ** 2
    return float(-10.0 * np.log10((1.0 - r) ** 2))


def total_loss_db(alpha_db_km, l_km, n_conn, conn_db, n_splice, splice_db):
    """Total loss between transmitter and receiver, in dB."""
    return float(alpha_db_km * l_km + n_conn * conn_db + n_splice * splice_db)


def power_margin_db(p_tx_dbm, sens_dbm, loss_db):
    """Decibels left over once the receiver has what it needs."""
    return float(p_tx_dbm - sens_dbm - loss_db)


def max_reach_km(p_tx_dbm, sens_dbm, alpha_db_km, fixed_db, margin_db):
    """Longest fibre length that still leaves the requested margin."""
    if alpha_db_km <= 0.0:
        return float("inf")
    budget = p_tx_dbm - sens_dbm - fixed_db - margin_db
    return float(budget / alpha_db_km)


if __name__ == "__main__":
    loss = total_loss_db(0.25, 80.0, 2, 0.5, 8, 0.05)
    print("air gap costs:", round(gap_loss_db(1.46, 1.0), 4), "dB")
    print("total loss over 80 km:", round(loss, 3), "dB")
    print("margin from 0 dBm into a -28 dBm receiver:",
          round(power_margin_db(0.0, -28.0, loss), 3), "dB")
    print("reach with 3 dB margin:",
          round(max_reach_km(0.0, -28.0, 0.25, 1.4, 3.0), 3), "km")
'''}],
                "hints": [
                    "`gap_loss_db` needs the square on $(1-R)$ because the light crosses two faces, and the minus sign because a loss is quoted positive.",
                    "`power_margin_db` is a subtraction of dBm values, and the answer is in dB — the units differ on purpose.",
                    "In `max_reach_km`, `fixed_db` already contains the connectors and splices, so do not add them again.",
                ],
                "tests": [
                    {"name": "an air gap costs about a third of a decibel", "code": r'''
_g = gap_loss_db(1.46, 1.0)
assert abs(_g - 0.30914734188717535) < 1e-12, \
    f"two silica-air faces cost 0.30915 dB, got {_g} — did you forget the second face?"
assert abs(gap_loss_db(1.46, 1.46)) < 1e-12, \
    "a perfectly matched gap has no Fresnel loss at all"
_gel = gap_loss_db(1.46, 1.30)
assert abs(_gel - 0.029239294223983338) < 1e-12, \
    f"gel at n = 1.30 costs 0.02924 dB, got {_gel}"
assert _gel < _g / 10.0, \
    "index-matching gel should cut the Fresnel loss by better than a factor of ten"
'''},
                    {"name": "the budget adds its terms in decibels", "code": r'''
_l = total_loss_db(0.25, 80.0, 2, 0.5, 8, 0.05)
assert abs(_l - 21.4) < 1e-12, \
    f"0.25*80 + 2*0.5 + 8*0.05 = 21.4 dB, got {_l}"
_l2 = total_loss_db(0.25, 160.0, 2, 0.5, 8, 0.05)
assert abs((_l2 - _l) - 20.0) < 1e-12, \
    "doubling an 80 km span adds exactly alpha*80 = 20 dB and nothing else"
'''},
                    {"name": "margin is what survives the budget", "code": r'''
_m = power_margin_db(0.0, -28.0, 21.4)
assert abs(_m - 6.6) < 1e-9, \
    f"0 dBm into a -28 dBm receiver through 21.4 dB leaves 6.6 dB, got {_m}"
_bad = power_margin_db(0.0, -28.0, 35.0)
assert abs(_bad - (-7.0)) < 1e-9, \
    f"a link that overspends its budget has a negative margin, got {_bad}"
assert _bad < 0.0, "this link does not close, and the sign must say so"
'''},
                    {"name": "the budget inverts to a reach", "code": r'''
import math
_r = max_reach_km(0.0, -28.0, 0.25, 1.4, 3.0)
assert abs(_r - 94.4) < 1e-9, \
    f"(28 - 1.4 - 3)/0.25 = 94.4 km, got {_r}"
_r2 = max_reach_km(0.0, -28.0, 0.35, 1.4, 3.0)
assert abs(_r2 - 67.42857142857143) < 1e-9, \
    f"a lossier fibre shortens the reach to 67.43 km, got {_r2}"
assert max_reach_km(0.0, -28.0, 0.25, 1.4, 6.0) < _r, \
    "asking for more margin must shorten the reach"
assert math.isinf(max_reach_km(0.0, -28.0, 0.0, 1.4, 3.0)), \
    "a lossless fibre imposes no reach limit, and must not divide by zero"
'''},
                    {"name": "reach and margin are the same equation twice", "code": r'''
_fixed = 2 * 0.5 + 8 * 0.05
_L = max_reach_km(0.0, -28.0, 0.25, _fixed, 3.0)
assert _L > 90.0, f"expected a reach above 90 km before checking consistency, got {_L}"
_m = power_margin_db(0.0, -28.0, total_loss_db(0.25, _L, 2, 0.5, 8, 0.05))
assert abs(_m - 3.0) < 1e-9, \
    f"at exactly the maximum reach the margin must be the 3 dB you asked for, got {_m}"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "Size a single-mode link and name what limits it",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
A fibre specification and a link specification arrive together. Decide whether the
fibre is single-mode at the operating wavelength, work out how far the link can run
before it runs out of power, work out how far it can run before dispersion closes the
eye, and report the smaller of the two along with which effect binds.

The circular step-index fibre cuts off at $V = 2.405$, the first zero of $J_0$, rather
than at the slab's $\pi/2$. The definition of $V$ is unchanged: $V = 2\pi a\,
\mathrm{NA}/\lambda_0$ with $a$ the core **radius**.

Five functions, four of them recycled from earlier modules.

1. `numerical_aperture(n1, n2)`.
2. `v_number(a, lam0, n1, n2)`, then `single_mode(V)`, which is `V < 2.405`.
3. `loss_limited_km(p_tx_dbm, sens_dbm, alpha_db_km, fixed_db, margin_db)`.
4. `dispersion_limited_km(bitrate, d_ps, w_nm)` — the length at which the chromatic
   spread $D L W$ picoseconds reaches half a bit period. Watch the units: with $D$ in
   ps/(nm·km) and $W$ in nm, the spread is in ps, so
   $L = 1/(2 B D W \times 10^{-12})$.
5. `design_link(spec)` — takes one of the dictionaries from `fibre.py` and returns a
   dictionary with these exact keys:

   ```text
   na              float
   v               float
   single_mode     bool
   loss_km         float
   dispersion_km   float
   reach_km        float     the smaller of the two limits
   limited_by      str       "loss" or "dispersion"
   ```

## Suggested order

Build `numerical_aperture`, `v_number` and `single_mode` first and confirm the
supplied fibre really is single-mode; the two reach calculations are independent of
each other and of the mode analysis, so they can be written in either order;
`design_link` is then only assembly and one comparison.

Ties do not occur in the supplied specifications, but decide the tie rule anyway and
write it down: if the two limits are equal, report `"loss"`.
''',
        "deliverables": [
            "`numerical_aperture`, `v_number` and `single_mode` working together, and correctly rejecting a multimode fibre as well as accepting the single-mode one.",
            "`loss_limited_km` implementing the budget from module 4, with the length-independent losses supplied as a single `fixed_db` term.",
            "`dispersion_limited_km` implementing the half-bit-period rule from module 3, with the ps/(nm·km) unit conversion done explicitly rather than absorbed into a magic constant.",
            "`design_link` returning all seven keys, with `reach_km` the smaller of the two limits and `limited_by` naming which one it was.",
            "A short comment at the top of `main.py` stating, for the 10 Gb/s specification, which effect limits the link and what single change would move that limit furthest.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy, no photonics package.",
            "Do not edit `fibre.py`; the checks read the same numbers from it.",
            "Every length is in kilometres, every spectral width in nanometres, every dispersion coefficient in ps/(nm·km). Convert at the boundary, not in the middle of an expression.",
            "`design_link` must not mutate the specification dictionary it is given.",
        ],
        "rubric": [
            {"criterion": "Mode analysis", "weight": 25,
             "evidence": "NA and V are computed from the core radius and wavelength, and the single-mode verdict is correct for both the supplied single-mode fibre and a 25 um multimode one."},
            {"criterion": "Loss-limited reach", "weight": 25,
             "evidence": "The budget inverts to a length that reproduces the requested margin when fed back through a forward loss calculation, and shortens when attenuation or margin rises."},
            {"criterion": "Dispersion-limited reach", "weight": 25,
             "evidence": "The half-bit-period rule is applied with the ps/(nm km) conversion correct, giving 29.41 km at 10 Gb/s and scaling inversely with bit rate."},
            {"criterion": "Design verdict", "weight": 25,
             "evidence": "design_link returns every key, takes the smaller of the two limits, and names the binding effect correctly for both the 10 Gb/s and the 1 Gb/s specification."},
        ],
        "hints": [
            "`v_number` is the same line as in module 2, but $a$ is now a radius rather than a half-width — the formula does not change, only the name of the thing you pass in.",
            "For the dispersion limit, write the conversion as an explicit `* 1e-12` on the spread rather than folding it into the constant; you will be able to read the units back later.",
            "`design_link` should call the other four functions rather than repeating their arithmetic. If a check on `reach_km` fails while the two limit checks pass, the bug is in the comparison, not the physics.",
            "Copy the spec with `dict(spec)` if you want to add derived values to it, so the original is left alone.",
        ],
        "files": [
            {"name": "fibre.py", "ro": True, "content": r'''
"""Fibre and link specifications. Do not edit — the checks read these numbers."""


def spec_10g():
    """A standard single-mode fibre carrying 10 Gb/s at 1550 nm."""
    return {
        "name": "10G metro span",
        "n1": 1.4682,          # core index
        "n2": 1.4629,          # cladding index
        "a": 4.1e-6,           # core radius, m
        "lam0": 1.55e-6,       # operating wavelength, m
        "bitrate": 1.0e10,     # bit/s
        "d_ps": 17.0,          # dispersion coefficient, ps/(nm km)
        "w_nm": 0.1,           # source spectral width, nm
        "p_tx_dbm": 1.0,       # launched power
        "sens_dbm": -22.0,     # receiver sensitivity
        "alpha_db_km": 0.25,   # fibre attenuation
        "fixed_db": 1.3,       # connectors and splices together
        "margin_db": 3.0,      # system margin
    }


def spec_1g():
    """The same physical route, run ten times slower."""
    s = spec_10g()
    s["name"] = "1G access span"
    s["bitrate"] = 1.0e9
    return s
'''},
            {"name": "main.py", "content": r'''
import numpy as np
from fibre import spec_10g, spec_1g

# The 10 Gb/s link is limited by TODO, and the single change that would move
# that limit furthest is TODO.

SINGLE_MODE_V = 2.405


def numerical_aperture(n1, n2):
    """NA of a step-index fibre."""
    # TODO
    return 0.0


def v_number(a, lam0, n1, n2):
    """Normalised frequency, with a the core radius."""
    # TODO
    return 0.0


def single_mode(V):
    """True when only the fundamental mode propagates."""
    # TODO
    return False


def loss_limited_km(p_tx_dbm, sens_dbm, alpha_db_km, fixed_db, margin_db):
    """Longest span the power budget allows."""
    # TODO: guard a non-positive attenuation.
    return 0.0


def dispersion_limited_km(bitrate, d_ps, w_nm):
    """Longest span before the chromatic spread reaches half a bit period."""
    # TODO: guard a zero dispersion coefficient or spectral width.
    return 0.0


def design_link(spec):
    """Return na, v, single_mode, loss_km, dispersion_km, reach_km, limited_by."""
    # TODO
    return {}


if __name__ == "__main__":
    for s in (spec_10g(), spec_1g()):
        d = design_link(s)
        print(s["name"], "->", d)
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
from fibre import spec_10g, spec_1g

# The 10 Gb/s link is limited by dispersion at 29.4 km against a 74.8 km loss
# limit, and the single change that would move that limit furthest is a narrower
# source: the dispersion limit goes inversely with spectral width, so a 0.01 nm
# laser pushes it from 29.4 km to 294 km, while a lower-loss fibre moves only the
# 74.8 km term and buys nothing at all. Note what that does to the verdict — with
# the dispersion limit out at 294 km the link becomes loss-limited, so the reach
# itself only goes from 29.4 km to 74.8 km, and the next thing to fix is loss.

SINGLE_MODE_V = 2.405


def numerical_aperture(n1, n2):
    """NA of a step-index fibre."""
    return float(np.sqrt(n1 * n1 - n2 * n2))


def v_number(a, lam0, n1, n2):
    """Normalised frequency, with a the core radius."""
    return float(2.0 * np.pi * a * numerical_aperture(n1, n2) / lam0)


def single_mode(V):
    """True when only the fundamental mode propagates."""
    return bool(V < SINGLE_MODE_V)


def loss_limited_km(p_tx_dbm, sens_dbm, alpha_db_km, fixed_db, margin_db):
    """Longest span the power budget allows."""
    if alpha_db_km <= 0.0:
        return float("inf")
    return float((p_tx_dbm - sens_dbm - fixed_db - margin_db) / alpha_db_km)


def dispersion_limited_km(bitrate, d_ps, w_nm):
    """Longest span before the chromatic spread reaches half a bit period."""
    per_km_s = abs(d_ps) * abs(w_nm) * 1e-12
    if bitrate <= 0.0 or per_km_s <= 0.0:
        return float("inf")
    return float(1.0 / (2.0 * bitrate * per_km_s))


def design_link(spec):
    """Return na, v, single_mode, loss_km, dispersion_km, reach_km, limited_by."""
    s = dict(spec)
    na = numerical_aperture(s["n1"], s["n2"])
    v = v_number(s["a"], s["lam0"], s["n1"], s["n2"])
    loss_km = loss_limited_km(s["p_tx_dbm"], s["sens_dbm"], s["alpha_db_km"],
                              s["fixed_db"], s["margin_db"])
    disp_km = dispersion_limited_km(s["bitrate"], s["d_ps"], s["w_nm"])
    if loss_km <= disp_km:
        reach, why = loss_km, "loss"
    else:
        reach, why = disp_km, "dispersion"
    return {
        "na": na,
        "v": v,
        "single_mode": single_mode(v),
        "loss_km": loss_km,
        "dispersion_km": disp_km,
        "reach_km": reach,
        "limited_by": why,
    }


if __name__ == "__main__":
    for s in (spec_10g(), spec_1g()):
        d = design_link(s)
        print(s["name"], "->", d)
'''},
        ],
        "tests": [
            {"name": "the supplied fibre really is single-mode", "code": r'''
from fibre import spec_10g
_s = spec_10g()
_na = numerical_aperture(_s["n1"], _s["n2"])
assert abs(_na - 0.12463879813284287) < 1e-12, \
    f"NA = sqrt(1.4682^2 - 1.4629^2) = 0.1246388, got {_na}"
_v = v_number(_s["a"], _s["lam0"], _s["n1"], _s["n2"])
assert abs(_v - 2.071501630351279) < 1e-9, \
    f"V = 2*pi*a*NA/lambda = 2.0715016, got {_v}"
assert single_mode(_v) is True or single_mode(_v) == True, \
    "V = 2.07 is below the 2.405 cutoff, so this fibre carries one mode"
'''},
            {"name": "a fat core is correctly rejected", "code": r'''
_v = v_number(25e-6, 1.31e-6, 1.48, 1.46)
assert abs(_v - 29.076173014441707) < 1e-9, \
    f"a 25 um radius at 1310 nm gives V = 29.076, got {_v}"
assert not single_mode(_v), \
    "V = 29 is far above 2.405 — this is a multimode fibre and must be reported as one"
'''},
            {"name": "the loss budget allows 74.8 km", "code": r'''
import math
from fibre import spec_10g
_s = spec_10g()
_l = loss_limited_km(_s["p_tx_dbm"], _s["sens_dbm"], _s["alpha_db_km"],
                     _s["fixed_db"], _s["margin_db"])
assert abs(_l - 74.8) < 1e-9, \
    f"(1 - (-22) - 1.3 - 3)/0.25 = 74.8 km, got {_l}"
_worse = loss_limited_km(_s["p_tx_dbm"], _s["sens_dbm"], 0.35,
                         _s["fixed_db"], _s["margin_db"])
assert _worse < _l, "a lossier fibre must give a shorter loss-limited span"
assert math.isinf(loss_limited_km(1.0, -22.0, 0.0, 1.3, 3.0)), \
    "zero attenuation removes the loss limit, and must not divide by zero"
'''},
            {"name": "dispersion allows 29.4 km at 10 Gb/s", "code": r'''
from fibre import spec_10g
_s = spec_10g()
_d = dispersion_limited_km(_s["bitrate"], _s["d_ps"], _s["w_nm"])
assert abs(_d - 29.41176470588235) < 1e-9, \
    f"1/(2 * 1e10 * 17 * 0.1 * 1e-12) = 29.4118 km, got {_d} — check the ps conversion"
_slow = dispersion_limited_km(1.0e9, _s["d_ps"], _s["w_nm"])
assert abs(_slow - 294.11764705882354) < 1e-9, \
    f"ten times slower is ten times further: 294.118 km, got {_slow}"
assert abs(dispersion_limited_km(1.0e10, -17.0, 0.1) - _d) < 1e-9, \
    "a negative dispersion coefficient spreads a pulse just as much as a positive one"
'''},
            {"name": "the 10 Gb/s link is dispersion-limited", "code": r'''
from fibre import spec_10g
_d = design_link(spec_10g())
for _k in ("na", "v", "single_mode", "loss_km", "dispersion_km", "reach_km", "limited_by"):
    assert _k in _d, f"design_link must return the key {_k!r}; got {sorted(_d)}"
assert _d["limited_by"] == "dispersion", \
    f"29.4 km of dispersion beats 74.8 km of loss, so the verdict is 'dispersion', got {_d['limited_by']!r}"
assert abs(_d["reach_km"] - 29.41176470588235) < 1e-9, \
    f"reach must be the smaller limit, 29.4118 km, got {_d['reach_km']}"
assert _d["single_mode"], "the supplied fibre is single-mode at 1550 nm"
'''},
            {"name": "the same route at 1 Gb/s becomes loss-limited", "code": r'''
from fibre import spec_1g
_d = design_link(spec_1g())
assert _d["limited_by"] == "loss", \
    f"at 1 Gb/s dispersion allows 294 km and loss only 74.8, got {_d['limited_by']!r}"
assert abs(_d["reach_km"] - 74.8) < 1e-9, \
    f"reach must be the smaller limit, 74.8 km, got {_d['reach_km']}"
assert _d["reach_km"] <= _d["loss_km"] + 1e-12 and _d["reach_km"] <= _d["dispersion_km"] + 1e-12, \
    "the reach can never exceed either individual limit"
'''},
            {"name": "the specification is not modified in place", "code": r'''
from fibre import spec_10g
_s = spec_10g()
_before = dict(_s)
_d = design_link(_s)
assert "reach_km" in _d and _d["reach_km"] > 0.0, \
    f"design_link must return a positive reach_km before this check means anything; got {sorted(_d)}"
assert _s == _before, \
    "design_link must not mutate the specification it was handed; copy it first"
'''},
        ],
    },
}
