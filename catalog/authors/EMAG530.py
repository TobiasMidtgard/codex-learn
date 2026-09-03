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
            "read": [
                {
                    "title": "A fifty-millimetre disc on a card, and the meter facing the other way",
                    "minutes": 16,
                    "body": r'''
A metre of step-index multimode fibre lies on the bench with both ends cleaved square.
Core index 1.48, cladding 1.46. The source is launched into it deliberately badly —
overfilled, so that every angle the fibre will take is present at the input. A white
card stands 100.0 mm from the far end, normal to the axis.

On the card is a disc of light 50.0 mm across, and its edge is sharp. Slide the card out
to 200 mm and the disc is 100 mm across; the edge stays sharp. The fibre is not smearing
light into a haze. It is pouring it into a cone with a definite half-angle, and outside
that angle there is nothing.

Turn the experiment round and hold a power meter against the input face. Of 1.000 mW
arriving at the cleaved end, 0.9650 mW goes in and 0.0350 mW comes straight back out — a
return loss of 14.56 dB from a flat piece of glass with nothing on it and nothing wrong
with it.

The width of that cone and the size of that reflection are the two numbers a fibre data
sheet is quoting when it prints an NA and an end-face loss. Both come out of one
inequality on an angle.

## Reading the cone backwards

Half the disc is 25.0 mm at a range of 100.0 mm, so the half-angle in air is
$\arctan(0.2500) = 14.03°$. That much is a triangle. The question is why the fibre has
an edge to its cone at all, and what fixes where it falls.

Follow one ray in. It crosses the flat end face at $\theta_a$ from the axis and refracts
to $\theta_r$ inside the core, so $n_0\sin\theta_a = n_1\sin\theta_r$. It then runs down
the core and strikes the core–cladding wall — and it strikes it at $90° - \theta_r$ from
*that* wall's normal, because the wall is parallel to the axis while the end face is
perpendicular to it. That change of reference, from the axis to the wall's normal, is
the whole of the geometry here, and it is where a cosine goes missing if one is going to.

At the wall, Snell again: $n_1\sin(90° - \theta_r) = n_2\sin\theta_t$. As $\theta_r$
grows the left side shrinks and so does $\theta_t$; run it the other way and there is an
angle at which $\theta_t$ reaches $90°$ and the refracted ray lies flat along the
interface. Past it the equation has no real solution, the transmitted wave stops
carrying power away, and the reflection is total. That is the critical angle,
$\sin\theta_c = n_2/n_1$, and for 1.48 against 1.46 it is 1.406211640313002 rad, or
80.570° — measured from the normal, so a ray meeting the wall at 80.6° to its normal is
running only 9.4° off the fibre axis.

A ray survives when $90° - \theta_r \ge \theta_c$, which is $\sin\theta_r \le
\cos\theta_c$. Push that back out through the end face:

$$n_0\sin\theta_a \;\le\; n_1\cos\theta_c \;=\; n_1\sqrt{1 - \frac{n_2^2}{n_1^2}}
\;=\; \sqrt{n_1^2 - n_2^2}$$

The right-hand side contains no $n_0$ and no angle. It is a property of the fibre alone,
it is what $\mathrm{NA}$ names, and what it bounds is $\sin\theta_a$ rather than
$\theta_a$. That is why a data sheet quotes a number and not an angle: the angle depends
on what you launch through, and the number does not.

```python
import math

n0, n1, n2 = 1.0, 1.48, 1.46          # air, core, cladding

na = math.sqrt(n1 * n1 - n2 * n2)
theta_c = math.asin(n2 / n1)
theta_a = math.asin(na / n0)

print(f"NA                {na:.16f}")
print(f"critical angle    {theta_c:.15f} rad = {math.degrees(theta_c):.4f} deg")
print(f"acceptance cone   {theta_a:.10f} rad = {math.degrees(theta_a):.4f} deg")
print(f"disc 100.0 mm out {200.0 * math.tan(theta_a):.4f} mm across")

r = ((n2 - n0) / (n2 + n0)) ** 2      # the facet is cladding-grade silica against air
print(f"facet reflects    {100 * r:.4f} per cent")
print(f"return loss       {-10 * math.log10(r):.2f} dB")
print(f"one facet costs   {-10 * math.log10(1 - r):.5f} dB")
print(f"launched in gel   {math.degrees(math.asin(na / 1.45)):.4f} deg")
```

The disc comes to 49.9894 mm, which on a card held by hand is the 50.0 mm the bench
showed. The acceptance half-angle is 14.0334°. And the same fibre entered through
index-matching gel at $n_0 = 1.45$ instead of air accepts only 9.6269° — the NA did not
move, the cone did, because what was fixed was the product $n_0\sin\theta_a$.

## The mistake: subtracting the indices

$\mathrm{NA} = n_1 - n_2$ is the most common wrong formula in this subject, and on the
fibre above it is wrong by a factor of twelve.

It is tempting for three separate reasons, which is why naming it once does not
inoculate anyone. The quantity fabrication actually controls *is* a difference:
$\Delta = (n_1 - n_2)/n_1$ is what a preform is specified to and what a data sheet
prints. The difference is genuinely inside the NA, since
$n_1^2 - n_2^2 = (n_1 - n_2)(n_1 + n_2)$ — it is in there, under a root and multiplied
by roughly $2n_1$. And both expressions go to zero together when the guiding stops, so
the one check that costs nothing to run is the one check that passes.

The card settles it.

```python
import math

n1, n2 = 1.48, 1.46

for name, value in (("sqrt(n1^2 - n2^2)", math.sqrt(n1 * n1 - n2 * n2)),
                    ("n1 - n2", n1 - n2),
                    ("n1*sqrt(2*Delta)", n1 * math.sqrt(2 * (n1 - n2) / n1))):
    half = math.asin(value)
    print(f"{name:>18}:  NA = {value:.7f}   cone {math.degrees(half):6.3f} deg"
          f"   disc {200 * math.tan(half):7.3f} mm")

print(f"the two NAs differ by a factor of "
      f"{math.sqrt(n1 * n1 - n2 * n2) / (n1 - n2):.5f}")
```

An NA of 0.0200 predicts a disc 4.001 mm across. There is a disc 50 mm across on the
card. Nothing about the factor 12.12436 is subtle, and no amount of care further down
the budget survives it.

The third line is there for a different reason. The weakly-guiding form
$\mathrm{NA} \approx n_1\sqrt{2\Delta}$, which the derivation *From Snell's law to the
numerical aperture* reaches at its third step, gives 0.2433105 against the exact
0.2424871 — high by 0.34 per cent, or 0.18 mm on a 50 mm disc, which is less than the
width of the pencil line you would draw round it. That is what the approximation costs
at $\Delta = 1.35$ per cent. The approximation earns its place; the subtraction does not.

## The meter, and why an index step is a load

The 3.5 per cent has nothing to do with guiding. It happens at the flat face, at normal
incidence, before the angle argument has started.

EMAG520 spent a course on what a mismatched load does, and a dielectric boundary is one.
The wave impedance of a medium is $\eta = \eta_0/n$, so silica against air presents a
normalised load of 1.46 read from the glass side, and

$$\Gamma = \frac{n_2 - n_0}{n_2 + n_0} = \frac{0.46}{2.46} = 0.186992,
\qquad R = |\Gamma|^2 = 0.0349660$$

is the entire derivation. The sandbox *An index step is a mismatched load* opens on a
load of 73 Ω, which is $1.46 \times 50\ \Omega$, and reports $|\Gamma| = 0.187$ with
14.6 dB of return loss for precisely this reason. Drag its load resistance down to 50 Ω
and the dot collapses onto the centre of the chart: that is index-matching gel, and that
is the whole of why the gel exists.

In decibels the face costs $-10\log_{10}(1 - R) = 0.15457$ dB on the way in, and the
same again on the way out, because $R$ is symmetric in the two indices. Module 4 needs
the pair together and calls it 0.30915 dB.

The lab *The acceptance cone and the end face* asks for these as five one-line
functions, and its tests pin the critical angle to 1.406211640313002 and the NA to
0.2424871130596432 — the digits printed above, because it is the same calculation read
twice. Its fifth function, `single_mode_half_width`, is borrowed from the next module,
and the reason it has to be borrowed is the last section here.

## Where the ray picture stops

**It has no wavelength in it.** Every formula above is built from indices and angles.
None of them mentions $\lambda$. So the ray picture cannot say how many modes the fibre
carries or whether it is single-mode, because those answers depend on wavelength and
this model has no wavelength to depend on. The lab's bound
$a \le \lambda_0/(4\,\mathrm{NA})$ — 1.598 µm at 1550 nm for this fibre — has a
wavelength in its numerator and could not have come from anything on this page. Module 2
pays for it by discarding the rays and solving the wave equation instead.

**Total internal reflection is not a hard mirror.** Beyond $\theta_c$ the reflection is
total in magnitude, and the argument above stops at magnitude. It is not total in phase:
the wave returns with a lag that depends on the angle, and there is a real field in the
cladding, decaying with distance, carrying no net power away. A ray can represent
neither, and between them they are the whole content of the next module — the phase
becomes the eigenvalue equation, and the evanescent tail is why a mode has an effective
index rather than a bounce angle.

**Normal incidence is a special case.** The 3.5 per cent is for light arriving square
on. Off normal, the two polarisations part company.

```python
import math


def fresnel(ni, nt, theta_i):
    """Power reflectance at one interface, for each polarisation."""
    theta_t = math.asin(ni * math.sin(theta_i) / nt)
    ci, ct = math.cos(theta_i), math.cos(theta_t)
    rs = (ni * ci - nt * ct) / (ni * ci + nt * ct)
    rp = (nt * ci - ni * ct) / (nt * ci + ni * ct)
    return rs * rs, rp * rp


for deg in (0.0, 14.0334, 45.0, 80.0):
    rs, rp = fresnel(1.0, 1.46, math.radians(deg))
    print(f"{deg:7.4f} deg into silica:  s {100 * rs:6.3f} %   p {100 * rp:6.3f} %"
          f"   mean {100 * (rs + rp) / 2:6.3f} %")
```

At the edge of the acceptance cone the two polarisations differ by 0.59 percentage
points and their mean is 3.502 per cent, which rounds to the same 3.5 the normal
calculation gave — so the single number in the budget survives out to 14°. At 80° it
does not survive at all: the mean is 38.043 per cent and a polished face is a mirror.
That is also the mechanism an angled-polish connector uses. Tilting the face by 8°
does not reduce the reflection; it aims it outside the acceptance cone, so the reflected
power leaves the fibre instead of travelling back down it to the laser.

**A step index is an idealisation.** Graded-index fibre has no single critical angle
because it has no single boundary. Rays follow curved paths and turn round where the
local index falls to meet their own invariant, and the NA becomes a local quantity —
largest on the axis, zero at the cladding. A graded fibre quoting one NA is quoting the
on-axis value.

**A short fibre measures wider than it is.** The disc on the card was measured after a
metre. Measure it after 100 mm and the disc is larger, because light launched outside
the acceptance cone has refracted into the cladding and is still travelling there,
unguided but not yet gone. This is why a standards-body loss measurement specifies a
launch condition and a mode stripper, and why two laboratories measuring the same fibre
will disagree if one of them does not.
''',
                },
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
            "quiz": {
                "title": "Guiding is one inequality on an angle",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What is the numerical aperture of a step-index fibre?",
                        "opts": ["$\\sqrt{n_1^2 - n_2^2}$", "$n_1 - n_2$", "$n_1/n_2$", "$\\sqrt{n_1n_2}$"],
                        "a": 0,
                        "why": r"""
It comes out of applying Snell's law twice — once entering the end face, once at the
core–cladding boundary — and it is the sine of the largest angle that will still be
guided. A typical multimode fibre has $n_1 = 1.48$, $n_2 = 1.46$, so
$\text{NA} = \sqrt{0.0588} = 0.24$: an acceptance half-angle of 14°. The difference
$n_1 - n_2$ is small and appears in $\Delta$, but it is not the NA.
""",
                    },
                    {
                        "q": "The critical angle at the core–cladding boundary is:",
                        "opts": [
                            "$\\arcsin(n_2/n_1)$, measured from the normal",
                            "$\\arcsin(n_1/n_2)$",
                            "$\\arctan(n_2/n_1)$",
                            "$\\arccos(n_2/n_1)$",
                        ],
                        "a": 0,
                        "why": r"""
Snell with the refracted ray grazing along the boundary. With $n_2/n_1$ close to 1 the
critical angle is close to 90° — for the fibre above, 80.6°, so only rays within about
9° of the axis are guided. Writing $n_1/n_2$ gives an arcsine of a number greater than 1,
which is the arithmetic telling you that light cannot be totally reflected going from
low index to high.
""",
                    },
                    {
                        "q": "In terms of the relative index difference $\\Delta$, the NA is approximately:",
                        "opts": ["$n_1\\sqrt{2\\Delta}$", "$n_1\\Delta$", "$\\sqrt{\\Delta}$", "$2n_1\\Delta$"],
                        "a": 0,
                        "why": r"""
Factor $n_1^2 - n_2^2 = (n_1+n_2)(n_1-n_2) \approx 2n_1 \cdot n_1\Delta$ for small
$\Delta$. It is the form worth carrying because $\Delta$ is what data sheets quote and
what fabrication controls — and the square root is why halving $\Delta$ only reduces the
NA by 30%.
""",
                    },
                    {
                        "q": "A larger NA gives you what, and costs you what?",
                        "opts": [
                            "Easier coupling, at the price of more modal dispersion",
                            "Easier coupling with no penalty",
                            "Lower loss, at the price of a smaller core",
                            "Higher bandwidth, at the price of coupling",
                        ],
                        "a": 0,
                        "why": r"""
A wider acceptance cone catches more light from a cheap LED — and admits rays at steeper
angles, whose zig-zag path is longer, which spreads the pulse. The two are the same
inequality read in opposite directions, and the trade defines the market: high-NA
multimode for short cheap links, low-NA single-mode for long fast ones.
""",
                    },
                    {
                        "q": "Light arrives outside the acceptance cone. What happens to it?",
                        "opts": [
                            "It refracts into the cladding and is lost within a short distance",
                            "It is reflected back out of the fibre end",
                            "It propagates with higher loss",
                            "It couples into a higher-order mode",
                        ],
                        "a": 0,
                        "why": r"""
Beyond the critical angle the reflection is no longer total, so a fraction escapes at
every bounce and the ray is gone within centimetres. This is why a fibre's measured loss
depends on how far from the launch you start measuring — the cladding modes have to
strip out first, which is what a mode stripper is for and why standard loss measurements
specify a launch condition.
""",
                    },
                ],
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
            "read": [
                {
                    "title": "Two dips in a prism coupler, and an equation with no formula",
                    "minutes": 17,
                    "body": r'''
A rutile prism is clamped onto a slab waveguide on the stage of a prism coupler. The
slab is a 4.069 µm film of doped silica at $n_1 = 1.48$, buried on both sides in
cladding at $n_2 = 1.46$, so the structure is symmetric. The instrument sweeps the angle
at which a 1550 nm beam enters the prism and watches the power that comes back out.

At almost every angle, all of it comes back. At two angles — two, and no others — the
reflected power collapses into a narrow dip, because at those angles the field leaking
across the air gap under the prism travels along the surface at the same speed as
something the slab can carry, and the light goes in. Convert the two angles into axial
phase indices and the instrument reads

```text
n_e = 1.474723        and        n_e = 1.462048
```

Two dips. Both between the cladding index and the core index, neither equal to either.
Nothing in module 1 predicts that. A ray has a bounce angle, bounce angles form a
continuum, and a continuum would have smeared the dips into a band from $\theta_c$ to
grazing. The instrument shows two lines.

This module is about where the discreteness comes from, and about why the equation that
produces those two numbers has no closed-form solution at all.

## The wall is not a mirror, and that is the whole difference

EMAG510 solved a guide with conducting walls, where the tangential field had to vanish
at the metal, $k_x$ was forced to $m\pi/a$, and every cutoff was a one-line formula.
None of that survives here: the wall is a dielectric and the field does not vanish at it.

Write the mode as $e^{-j\beta z}$ with $\beta = k_0n_e$. Across the guide the field
oscillates with transverse wavenumber $\kappa = k_0\sqrt{n_1^2 - n_e^2}$, and beyond the
wall the transverse wavenumber is $k_{x2} = k_0\sqrt{n_2^2 - n_e^2}$. For a guided mode
$n_e > n_2$, so that second root is imaginary: $k_{x2} = j\gamma$ with $\gamma$ real,
and the field outside is $e^{-\gamma|x|}$ — decaying with distance, carrying no power
away, and very much not zero at the wall.

Reflection at a step in transverse wavenumber has the same form for TE as reflection at
a step in impedance, which EMAG520 worked to death:

$$\Gamma = \frac{\kappa - k_{x2}}{\kappa + k_{x2}} = \frac{\kappa - j\gamma}{\kappa + j\gamma}$$

Numerator and denominator are complex conjugates of one another, so $|\Gamma| = 1$
exactly — for every mode, at every angle past critical. Total internal reflection, in
this language, is the statement that the load has gone purely reactive. That is the rim
of the Smith chart, and it is where the sandbox *A mode is a round trip that closes*
opens: $R$ on its floor, $X$ at 120 Ω, $|\Gamma| = 0.988$, with the missing two per cent
being the 2 Ω the slider refuses to give up.

What survives a reflection of unit magnitude is the phase, and here it is
$\arg\Gamma = -2\arctan(\gamma/\kappa)$.

```python
import cmath
import math

n1, n2, lam0 = 1.48, 1.46, 1.55e-6
k0 = 2.0 * math.pi / lam0

# one guided mode of the finished slab, taken on trust for a moment
n_e = 1.474723299977725
kappa = k0 * math.sqrt(n1 * n1 - n_e * n_e)
gamma = k0 * math.sqrt(n_e * n_e - n2 * n2)

refl = (kappa - 1j * gamma) / (kappa + 1j * gamma)
print(f"kappa = {kappa:.6e} 1/m,  gamma = {gamma:.6e} 1/m")
print(f"|Gamma| at the wall  = {abs(refl):.15f}")
print(f"phase of Gamma       = {cmath.phase(refl):.10f} rad")
print(f"-2*arctan(gamma/kappa) = {-2.0 * math.atan(gamma / kappa):.10f} rad")
print(f"decay length 1/gamma = {1e6 / gamma:.4f} um")
```

The magnitude is 1 to fifteen decimals and the phase is $-2.0597330586$ rad, or $-118°$.
The cladding field falls to $1/e$ in 1.1868 µm, over half the core half-width — so a
substantial part of this mode is not in the core at all.

## A mode is a round trip that closes

Now put the phase to work. Start a wave at one wall travelling across, let it reach the
other wall, reflect, come back, and reflect again. It has covered $4a$ of transverse
path and picked up two reflections. If the field is to reproduce itself — which is what
"a mode" means — the total has to be a whole number of turns:

$$4\kappa a - 4\arctan\frac{\gamma}{\kappa} = 2m\pi$$

Write $u = \kappa a$ and $w = \gamma a$, divide by two, and rearrange the arctangent:

$$u - \arctan\frac{w}{u} = \frac{m\pi}{2}
\qquad\Longrightarrow\qquad
u\tan\!\left(u - \frac{m\pi}{2}\right) = w$$

That is the symmetric slab eigenvalue equation, and everything about it is now
explained. The integer $m$ is there because a whole number of turns is a whole number.
The $\arctan$ is there because the wall is glass rather than metal; set $\gamma \to
\infty$, which is what a perfect conductor would be, and the arctangent goes to $\pi/2$
and the equation collapses back to EMAG510's. And the reason it cannot be solved for $u$
is that $u$ appears both inside a tangent and outside it, which no rearrangement fixes.

The sandbox makes the round trip visible. Take its line-length slider from 0 to
0.5 $\lambda$ and the dot completes exactly one circuit of the chart: half a wavelength
of line is $360°$ of *round-trip* phase, because the wave crosses it twice. A mode is a
transverse angle at which that circuit closes on itself.

One equation is not enough, because $u$ and $w$ are both unknown. The second comes from
adding their definitions, which the derivation *Normalised frequency and the single-mode
condition* does in one step: $\kappa^2 + \gamma^2 = k_0^2(n_1^2 - n_2^2)$, so

$$u^2 + w^2 = V^2, \qquad V = k_0a\,\mathrm{NA} = \frac{2\pi a}{\lambda_0}\sqrt{n_1^2 - n_2^2}$$

A circle of radius $V$, and a family of tangent branches spaced $\pi/2$ apart along $u$.
The modes are the intersections, and the count follows from the spacing alone:
$\lfloor 2V/\pi\rfloor + 1$. The exercise *Only some angles survive the round trip* runs
the same argument in the full-width convention, where the circle has radius $V/2$;
mixing the two changes a mode count by exactly a factor of two.

## The two dips

Bisection is enough, because the bracketing does the hard part. On the interval
$(m\pi/2,\ \min((m{+}1)\pi/2,\ V))$ the tangent runs from zero up to its pole, so the
residual $\sqrt{V^2 - u^2} - u\tan(u - m\pi/2)$ starts positive and ends negative, and
there is exactly one root between.

```python
import math

n1, n2, lam0 = 1.48, 1.46, 1.55e-6
na = math.sqrt(n1 * n1 - n2 * n2)


def v_number(a):
    return 2.0 * math.pi * a * na / lam0


def mode_count(v):
    return int(2.0 * v / math.pi) + 1


def residual(u, v, m):
    return math.sqrt(max(v * v - u * u, 0.0)) - u * math.tan(u - m * math.pi / 2.0)


def solve_u(v, m):
    lo = m * math.pi / 2.0 + 1e-12
    hi = min((m + 1) * math.pi / 2.0, v) - 1e-12
    f_lo = residual(lo, v, m)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f_mid = residual(mid, v, m)
        if (f_lo > 0.0) == (f_mid > 0.0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


for a in (2.034666161675658e-6, 2.000e-6):
    v = v_number(a)
    print(f"half-width {a * 1e6:.6f} um -> V = {v:.15f}, {mode_count(v)} mode(s)")
    for m in range(mode_count(v)):
        u = solve_u(v, m)
        w = math.sqrt(v * v - u * u)
        b = (w / v) ** 2
        ne = math.sqrt(n2 * n2 + b * (n1 * n1 - n2 * n2))
        print(f"   m = {m}   u = {u:.12f}   w = {w:.6f}   b = {b:.6f}"
              f"   n_e = {ne:.12f}")
```

The first slab is the one under the prism. $V$ is 2.000000000000000, there are two
roots, and the effective indices are 1.474723299978 and 1.462048012826 — the two dips
the coupler found, in every digit it could resolve. Those same twelve decimals are what
the lab *Solve the slab eigenvalue equation* asserts, as 1.474723299977725 and
1.4620480128263664, against a bisection you are asked to write yourself; the code above
is that bisection, so the agreement is a check on the physics rather than a coincidence
of arithmetic.

The second slab is a wafer from the same run whose film came out at 2.000 µm. $V$ drops
to 1.965924472202252 — the value the lab pins to fifteen digits — the mode count is
unchanged, and both effective indices shift in the fourth decimal. Two slabs with the
same $V$ share their mode count, their $b$ and their field shapes once $x$ is measured
in units of $a$, which is why $b$ against $V$ is the only plot anyone draws.

The normalised guide index $b = (w/V)^2$ reads directly. It is 0 at cutoff, with $n_e$
down at the cladding index and the tail spilling out to infinity, and 1 for a deep mode
with $n_e$ at the core index and nothing outside. The fundamental here sits at 0.7348:
three-quarters of the way in, and still leaking.

## The mistake: bringing EMAG510's wall

The most expensive error here is assuming the boundary condition from the last course —
that the field goes to zero at the wall, so $\kappa a$ for the lowest mode is $\pi/2$
and no root-finding is needed.

It is tempting because it is nearly free. A whole module of EMAG510 was spent earning
$k_x = m\pi/a$, and a slab of glass in a diagram looks like a slab of anything else. The
answer even survives a plausibility check: $\pi/2 = 1.5708$ is a reasonable-looking $u$
for a guide with $V = 2$.

```python
import math

n1, n2 = 1.48, 1.46
step = n1 * n1 - n2 * n2


def n_eff(u, v):
    """Effective index from a transverse phase u, or None if u is not a guided root."""
    w2 = v * v - u * u
    if w2 <= 0.0:
        return None
    return math.sqrt(n2 * n2 + (w2 / (v * v)) * step)


hard = math.pi / 2.0            # what a conducting wall would demand of m = 0
for v, true_u in ((2.0, 1.0298665293222586), (1.0, 0.7390851332151607)):
    guess, truth = n_eff(hard, v), n_eff(true_u, v)
    shown = "no guided mode at all" if guess is None else f"n_e = {guess:.15f}"
    print(f"V = {v:.1f}:  metal wall u = {hard:.7f} -> {shown}")
    print(f"          dielectric u = {true_u:.7f} -> n_e = {truth:.15f}")
    if guess is not None:
        print(f"          the metal-wall answer is low by {truth - guess:.7f}")

u1 = 0.7390851332151607
print(f"at V = 1 the root satisfies cos(u) = u:  cos = {math.cos(u1):.16f}, "
      f"u = {u1:.16f}")
```

At $V = 2$ the metal wall predicts $n_e = 1.467695201268300$ where the prism coupler
measured 1.474723 — an error of 0.0070281. A commercial coupler resolves $n_e$ to about
$\pm 0.0005$, so the wrong model misses by fourteen times the instrument's uncertainty.
The bench refutes it on sight.

At $V = 1$ it fails harder, and in the direction that costs a design. It demands
$u = 1.5708$ when the circle has radius 1, which leaves $w^2 = V^2 - u^2$ negative and
returns no guided mode at all. The truth is that a symmetric slab *always* guides its
fundamental, however thin the film: the $m = 0$ branch of the tangent starts at the
origin, and a circle of any radius whatever crosses it. The mode at $V = 1$ is real, it
sits at $n_e = 1.469108806777969$, and it is one of the values the lab checks. A designer
carrying the metal-wall rule concludes that a thin film guides nothing and thickens it
until the guide has gone multimode.

The last line is a small gift from the algebra. At $V = 1$ the equation reads
$u\tan u = \sqrt{1 - u^2}$; substituting $\cos u = u$ makes the left side $\sin u$ and
the right side $\sqrt{1 - \cos^2 u}$, which is the same thing. So the fundamental root
at $V = 1$ is exactly the fixed point of the cosine, 0.7390851332151607, and the
bisection reproduces all sixteen digits of it. It is one closed-form value in an
equation that has none, and it makes a free test of any solver you write.

## Where this stops holding

**Symmetric only.** The fundamental never cutting off is a property of a *symmetric*
slab. Deposit the same film on a substrate with air above it and the two walls have
different $\gamma$; the round trip picks up two unequal phases, and the fundamental
acquires a genuine cutoff thickness below which the film guides nothing. Most real
planar devices are asymmetric.

**TE only.** The matching condition used above is continuity of $E_y$ and its
derivative, which is the TE case. TM matches $H_y$ and $(1/n^2)\,\partial H_y/\partial x$,
and the extra factor puts $(n_1/n_2)^2$ in front of $w$.

```python
import math

n1, n2, lam0, v = 1.48, 1.46, 1.55e-6, 2.0


def root(p):
    """Fundamental root of p*w = u*tan(u); p is 1 for TE, (n1/n2)^2 for TM."""
    lo, hi = 1e-12, min(math.pi / 2.0, v) - 1e-12
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        f = p * math.sqrt(max(v * v - mid * mid, 0.0)) - mid * math.tan(mid)
        lo, hi = (mid, hi) if f > 0.0 else (lo, mid)
    return 0.5 * (lo + hi)


ne = {}
for name, p in (("TE", 1.0), ("TM", (n1 / n2) ** 2)):
    u = root(p)
    b = (v * v - u * u) / (v * v)
    ne[name] = math.sqrt(n2 * n2 + b * (n1 * n1 - n2 * n2))
    print(f"{name}: factor {p:.10f}   u = {u:.10f}   n_e = {ne[name]:.12f}")

d = ne["TE"] - ne["TM"]
print(f"birefringence  n_e(TE) - n_e(TM) = {d:.4e}")
print(f"beat length    lambda / dn       = {1e3 * lam0 / d:.3f} mm")
```

The factor is 1.0276, the two effective indices differ by $7.8\times10^{-5}$, and the
lab solves only the TE family. That difference looks negligible and is not: the two
polarisations fall a full cycle out of step every 19.873 mm, so a centimetre-scale
device is polarisation-sensitive whether it was designed to be or not.

**A slab is not a fibre.** A circular step-index fibre replaces the sine and the
exponential with Bessel functions, and cutoff moves from $\pi/2$ to 2.405, the first zero
of $J_0$. The shape of the argument does not change — a circle, a family of branches, one
root each — which is why the capstone carries `v_number` straight over and changes only
the constant it is compared against.

**Indices held constant.** The treatment above takes $n_1$ and $n_2$ as numbers.
Material dispersion makes both functions of wavelength, so $b$ against $V$ stays exact
while $n_e$ against wavelength does not — a distinction module 3 must take seriously,
since the second derivative of that curve is what limits how far a pulse travels.
''',
                },
            ],
            "quiz": {
                "title": "Why the modes are discrete and the equation is not solvable",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A metal-walled guide gives $k_x = m\\pi/a$ in closed form. Why does the symmetric slab need a numerical root instead?",
                        "opts": [
                            "The dielectric wall passes a decaying field, so matching ties $\\kappa$ inside to $\\gamma$ outside",
                            "The core and cladding indices both vary with wavelength, which puts $\\lambda$ on both sides",
                            "Symmetry makes the conditions at the two walls degenerate, and a degenerate pair has no separate roots",
                            "The transverse field is a sine rather than a cosine, and sines have no analytic inverse",
                        ],
                        "a": 0,
                        "whys": [
                            r"The reflection at a glass wall keeps unit magnitude but carries a phase $-2\arctan(\gamma/\kappa)$, and $\gamma$ depends on the same unknown $n_e$ that $\kappa$ does. That is what puts $u$ inside a tangent and outside it at once.",
                            r"Material dispersion is real, but it is not the obstruction: freeze both indices at fixed values, as every calculation in this module does, and the equation is still transcendental.",
                            r"Symmetry is what makes the problem *easier* — it splits the modes into even and odd families and lets one equation with $m\pi/2$ cover both, and there is nothing degenerate about the pair. An asymmetric slab is harder, not more solvable.",
                            r"The core field is a sine for odd modes and a cosine for even ones, and neither choice is the difficulty. Inverting a sine is what $\arcsin$ is for.",
                        ],
                        "why": r"""
A conductor forces the tangential field to zero, which is a condition on the inside
alone and quantises $\kappa$ by itself. A dielectric wall does not: the field continues
into the cladding as $e^{-\gamma|x|}$, and continuity of the field and its slope ties
$\kappa$ to $\gamma$. Since both are functions of the one unknown $n_e$, the unknown
ends up inside a tangent and multiplying it, and $u\tan(u - m\pi/2) = w$ admits no
rearrangement that isolates $u$.
""",
                    },
                    {
                        "q": "A symmetric slab is thinned until $V = 0.9$, well below $\\pi/2$. How many guided modes does it carry?",
                        "opts": [
                            "One — the $m = 0$ branch starts at the origin, so any circle at all crosses it",
                            "None, since $V$ has fallen below the $\\pi/2$ at which the first mode turns on",
                            "One, but only for TE; the TM fundamental has a cutoff of its own at this thickness",
                            "It cannot be answered without the wavelength, which $V$ on its own does not contain",
                        ],
                        "a": 0,
                        "whys": [
                            r"The count is $\lfloor 2V/\pi\rfloor + 1$, and the $+1$ is not a fudge — it is the fundamental, which exists for every $V > 0$ however small.",
                            r"$V = \pi/2$ is where the *second* mode turns on, not the first. Reading it as the fundamental's cutoff is the metal-guide habit, and it is the error that has designers thicken a film until it goes multimode.",
                            r"TM in a symmetric slab has no cutoff either; its equation carries a factor $(n_1/n_2)^2$ on $w$, which shifts the root and leaves the $m = 0$ branch starting at the origin.",
                            r"The wavelength is already inside $V = 2\pi a\,\mathrm{NA}/\lambda_0$. That is the entire reason $V$ is worth defining: it is the one number the answer depends on.",
                        ],
                        "why": r"""
The mode count is $\lfloor 2V/\pi\rfloor + 1$, so $V = 0.9$ gives one. The tangent
branches sit $\pi/2$ apart in $u$ and the $m = 0$ branch begins at the origin, so a
circle of radius $V$ meets it for any positive $V$ whatever: a symmetric slab always
guides its fundamental, however thin the film. What a small $V$ costs is confinement,
not existence — at $V = 1$ the mode sits at $b = 0.454$ with most of its energy in the
cladding, which is a mode that bends badly and couples to anything nearby.
""",
                    },
                    {
                        "q": "The normalised guide index of a mode is $b = 0.10$. What does that say about it?",
                        "opts": [
                            "Its effective index is near the cladding, so it is close to cutoff and weakly held",
                            "Its effective index is near the core, so nearly all of its power travels inside the core",
                            "A tenth of the light in the guide travels in this mode, and the rest in others",
                            "Its transverse phase $u$ is a tenth of $V$, so it bounces at a shallow angle to the axis",
                        ],
                        "a": 0,
                        "whys": [
                            r"$b$ is defined to run from 0 at cutoff to 1 far above it, so 0.10 is a mode barely holding on, with a long evanescent tail and an $n_e$ a tenth of the way from $n_2$ to $n_1$ in the squares.",
                            r"That describes $b$ near 1. Reading the scale backwards is easy because $b$ is built from $w$, the *cladding* decay, so a small $b$ means a small $\gamma$ and a tail that reaches far.",
                            r"$b$ says nothing about how power was divided between modes at launch — it is a property of a mode's dispersion, and it is defined for a mode carrying no power at all.",
                            r"$b = (w/V)^2$, not $(u/V)$. With $b = 0.10$, $w$ is 0.32 of $V$ and $u$ is 0.95 of it, which is the steepest bounce rather than the shallowest.",
                        ],
                        "why": r"""
$b = (w/V)^2$ and $n_e^2 = n_2^2 + b(n_1^2 - n_2^2)$, so $b$ interpolates the effective
index between cladding and core: 0 at cutoff, 1 when the mode is entirely bound. At
$b = 0.10$ the mode is a tenth of the way up, its cladding decay $w$ is only $0.32V$,
and the field reaches far outside the core. The first higher mode of the slab in this
module sits at exactly 0.1018, which is why it is the one that vanishes first when the
guide is bent, heated, or trimmed.
""",
                    },
                    {
                        "q": "Why does the lab bracket mode $m$ on $(m\\pi/2,\\ \\min((m{+}1)\\pi/2,\\ V))$ rather than searching the whole range?",
                        "opts": [
                            "The tangent has a pole every $\\pi$, and one branch holds exactly one root with a sign change across it",
                            "Roots outside that window are complex, and a real bisection cannot represent them at all",
                            "It is an optimisation: the same roots are found either way, but far fewer function evaluations are needed",
                            "The window is where the residual is smooth, and Newton's method needs a smooth region to converge",
                        ],
                        "a": 0,
                        "whys": [
                            r"Bisection needs a bracket whose ends differ in sign and it needs exactly one root inside; both are guaranteed on one tangent branch and neither is guaranteed across a pole.",
                            r"There are no complex roots to avoid — the difficulty is real poles. A search crossing one sees a sign change with no root behind it and converges confidently on the pole.",
                            r"The two searches do not find the same roots. A bracket spanning a pole makes bisection converge on the pole itself, which is a wrong answer rather than a slow one.",
                            r"The method here is bisection, which needs no derivative and no smoothness — only a sign change. The bracketing is about which sign changes are genuine.",
                        ],
                        "why": r"""
Between $m\pi/2$ and the next pole, $\tan(u - m\pi/2)$ climbs from zero to infinity while
$\sqrt{V^2 - u^2}$ falls, so the residual starts positive, ends negative, and crosses
once. That is precisely what bisection needs. Widen the bracket across a pole and the
tangent jumps from $+\infty$ to $-\infty$, producing a sign change with no root behind
it — and bisection, which asks only about signs, will converge on the pole and report it
as an answer. The upper end is capped at $V$ as well, because $u > V$ makes $w$
imaginary and describes a radiating field rather than a guided one.
""",
                    },
                    {
                        "q": "A mode of this slab has $n_e = 1.4747$, between $n_2 = 1.46$ and $n_1 = 1.48$. What is that number?",
                        "opts": [
                            "The index setting the mode's axial phase velocity, $c/n_e$, with the field partly in each medium",
                            "The index of the glass at the point on the cladding wall where the ray turns round on each bounce",
                            "A fitted constant with no physical reading, produced by whatever numerical scheme found it",
                            "The average of core and cladding index weighted by the fraction of power in each",
                        ],
                        "a": 0,
                        "whys": [
                            r"$\beta = k_0n_e$ is the definition, so $n_e$ is the index the mode behaves as though it were travelling through — and it lies between the two because the mode itself lies partly in both.",
                            r"The ray does not enter the cladding and turn round in it; beyond the critical angle nothing propagates out there. The evanescent tail carries no power away and has no turning point.",
                            r"It is measurable. A prism coupler reads it off a dip angle to about $\pm0.0005$, without knowing anything about how it was computed.",
                            r"Tempting and nearly right, but the weighting is by field overlap rather than power fraction, and it is $n_e^2$ that interpolates linearly in $b$, not $n_e$.",
                        ],
                        "why": r"""
$\beta = k_0n_e$ defines it: the mode advances along the axis as though it were a plane
wave in a bulk medium of index $n_e$. It falls between the two indices because the mode
occupies both media — oscillating in the core, decaying in the cladding — and the more
of it that sits in the cladding, the closer $n_e$ falls to $n_2$. That is what $b$
measures. It is a real, measurable quantity rather than a bookkeeping device: a prism
coupler finds it directly from the angle at which the reflected power dips.
""",
                    },
                    {
                        "q": "Two symmetric slabs are built with the same $V$ but different half-widths and wavelengths. What do they share?",
                        "opts": [
                            "The same mode count and the same $b$ for every mode, with field shapes matching in units of $a$",
                            "The same effective indices, since $n_e$ is what $V$ was constructed to determine in the first place",
                            "The same cladding decay length $1/\\gamma$, which is what makes their confinement identical",
                            "Nothing in particular, unless the two also happen to share a numerical aperture",
                        ],
                        "a": 0,
                        "whys": [
                            r"$V$ is the only parameter in $u^2 + w^2 = V^2$ and $u\tan(u - m\pi/2) = w$, so the roots $u$ and $w$ — and therefore $b$ — depend on nothing else.",
                            r"$b$ is shared, and $n_e$ is not: recovering $n_e$ from $b$ needs $n_1$ and $n_2$ separately, and two slabs of equal $V$ can have quite different index pairs.",
                            r"$w = \gamma a$ is shared, so $1/\gamma$ scales with $a$ — the tail is the same fraction of the core width, and a different physical length.",
                            r"They share a great deal. $V$ already folds $a$, $\lambda_0$ and the NA into one number, which is why every textbook plot has $V$ on its axis and no wavelength anywhere.",
                        ],
                        "why": r"""
Both governing equations contain $V$ and nothing else, so the roots $u$ and $w$ are
functions of $V$ alone, and so is $b = (w/V)^2$. What is not shared is anything needing
a dimension or an index back: $n_e$ requires $n_1$ and $n_2$ separately, and $1/\gamma$
is a physical length that scales with $a$. This is the whole reason the normalised
variables exist — one curve of $b$ against $V$ describes every symmetric slab that has
ever been built, and the un-normalising is done at the end.
""",
                    },
                ],
            },
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
            "blanks": {
                "title": "Only some angles survive the round trip",
                "minutes": 9,
                "caption": "the symmetric slab, from transverse resonance to a mode count",
                "lang": "text",
                "brief": r"""
A mode is an angle that reproduces itself after one transverse round trip. Writing that
sentence as an equation gives the eigenvalue condition, and it is a root-finding problem
rather than a formula — which is what the lab solves. Fill in the chain.
""",
                "listing": """Transverse resonance: two crossings of the core, plus the phase
shift of each total internal reflection, must come back in phase:

        2*kappa*d - 2*phi = ___

with     kappa = k0 * sqrt(n1^2 - ne^2)      inside the core
         gamma = k0 * sqrt( ___ )            decaying in the cladding

Normalise with u = kappa*d/2 and w = gamma*d/2. Then

        u^2 + w^2 = ___

which is a circle -- and the eigenvalue condition u*tan(u - m*pi/2) = w
is a curve. The modes are the intersections, so the number of guided
modes is ___ .
""",
                "blanks": [
                    {
                        "prompt": "Back in phase after a round trip means what?",
                        "hole": "?",
                        "opts": ["2*m*pi", "m*pi", "pi/2", "0"],
                        "a": 0,
                        "why": "A whole number of full cycles — that is what 'reproduces itself' means, and the integer $m$ is the mode index. It is the same argument as a standing wave on a string, with the reflection phase $\\phi$ making it more interesting than an integer number of half wavelengths.",
                        "whys": [
                            "A whole number of full cycles — that is what 'reproduces itself' means, and the integer $m$ is the mode index. It is the same argument as a standing wave on a string, with the reflection phase $\\phi$ making it more interesting than an integer number of half wavelengths.",
                            "Half-cycles would mean the wave comes back inverted and cancels itself, which is the condition for a mode NOT to exist.",
                            "A fixed quarter cycle carries no mode index and cannot generate a family of solutions.",
                            "Zero is the $m = 0$ case only, and would give exactly one mode ever.",
                        ],
                    },
                    {
                        "prompt": "In the cladding the field decays. What is under the root?",
                        "hole": "?",
                        "opts": ["ne**2 - n2**2", "n2**2 - ne**2", "n1**2 - n2**2", "n1**2 - ne**2"],
                        "a": 0,
                        "why": "A guided mode has $n_2 < n_e < n_1$, so this is positive and $\\gamma$ is real — a genuinely decaying evanescent tail, not a propagating wave. That inequality *is* the definition of guidance, and the effective index is the single number that says how tightly a mode is held.",
                        "whys": [
                            "A guided mode has $n_2 < n_e < n_1$, so this is positive and $\\gamma$ is real — a genuinely decaying evanescent tail, not a propagating wave. That inequality *is* the definition of guidance, and the effective index is the single number that says how tightly a mode is held.",
                            "Negative for any guided mode, which would make $\\gamma$ imaginary and describe radiation leaking away rather than a bound mode.",
                            "That combination is the numerical aperture and does not involve the mode at all — it cannot describe how a *particular* mode decays.",
                            "This is $\\kappa$'s argument, for the oscillation inside the core, not the decay outside it.",
                        ],
                    },
                    {
                        "prompt": "What do u and w satisfy together?",
                        "hole": "?",
                        "opts": ["V**2 / 4", "V**2", "V / 2", "1"],
                        "a": 0,
                        "why": "Adding the two definitions eliminates $n_e$ and leaves the V number, with the factor of 4 from the $d/2$ in both normalisations. So the whole problem is one circle of fixed radius intersected with a family of tangent branches — and $V$ alone decides how many intersections there are.",
                        "whys": [
                            "Adding the two definitions eliminates $n_e$ and leaves the V number, with the factor of 4 from the $d/2$ in both normalisations. So the whole problem is one circle of fixed radius intersected with a family of tangent branches — and $V$ alone decides how many intersections there are.",
                            "That is the convention with $u = \\kappa d$ rather than $\\kappa d/2$; mixing the two makes the mode count wrong by a factor of two.",
                            "The circle's equation is in the squares, not the first power.",
                            "A unit circle would make the answer independent of the guide, which is exactly what $V$ exists to capture.",
                        ],
                    },
                    {
                        "prompt": "How many intersections does a circle of radius V/2 have?",
                        "hole": "?",
                        "opts": ["floor(2V/pi) + 1", "V", "always one", "unbounded"],
                        "a": 0,
                        "why": "The tangent branches sit $\\pi/2$ apart in $u$, so a circle of radius $V/2$ crosses one every $\\pi/2$. Two consequences worth keeping: there is always at least one mode in a symmetric slab, however small $V$ is; and single-mode operation needs $V < \\pi/2$, which is what sets the core diameter of single-mode fibre.",
                        "whys": [
                            "The tangent branches sit $\\pi/2$ apart in $u$, so a circle of radius $V/2$ crosses one every $\\pi/2$. Two consequences worth keeping: there is always at least one mode in a symmetric slab, however small $V$ is; and single-mode operation needs $V < \\pi/2$, which is what sets the core diameter of single-mode fibre.",
                            "$V$ is not an integer and is not a count.",
                            "A large slab supports many modes; that is what multimode fibre is.",
                            "The circle has finite radius, so the number of crossings is finite.",
                        ],
                    },
                ],
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
            "read": [
                {
                    "title": "Two reels on one bench, and the sixty-eight nanoseconds between them",
                    "minutes": 16,
                    "body": r'''
Two reels sit on the bench, each a kilometre of silica. A laser diode is driven with a
2 ns pulse; the far end goes into a fast detector and a sampling scope.

Through the first reel — step-index multimode, core 1.48, cladding 1.46 — the 2 ns pulse
comes back 68 ns wide. Not delayed by 68 ns: *widened* by it, into a low mound with a
hard leading edge and a long trailing shoulder.

Through the second reel — single-mode fibre at 1550 nm, driven by a DFB laser 0.1 nm
wide — the same pulse comes back 2 ns wide. The scope cannot separate the output from
the input.

Same glass, same length, same wavelength, same instrument. What differs is that the
first reel offers the pulse more than one way through.

## The 13.7 metres that are not there

The extreme guided ray is the one that meets the wall at exactly the critical angle;
anything steeper leaves. Module 1 put that angle at 80.570° from the wall's normal, so
the ray runs at 9.430° to the axis, and to advance one metre along the fibre it travels
$1/\sin\theta_c = n_1/n_2$ metres of glass. Over a kilometre that is 13.7 metres of
extra path, all of it crossed at the same $c/n_1$ as the axial ray, because both rays
are in the same material.

That is the whole mechanism, and the derivation *From ray paths to a bit rate* turns it
into $\tau_m = Ln_1(n_1 - n_2)/(cn_2)$ in three steps. The number is worth seeing
arrive.

```python
import math

C = 2.99792458e8
n1, n2, L = 1.48, 1.46, 1000.0        # metres of step-index multimode fibre

axial = L * n1 / C
extreme = (L * n1 / n2) * n1 / C
spread = extreme - axial

print(f"extra glass crossed by the extreme ray: {L * (n1 / n2 - 1):.4f} m")
print(f"speed inside the core:                  {C / n1:.6e} m/s")
print(f"axial ray arrives at   {axial * 1e9:.4f} ns")
print(f"extreme ray arrives at {extreme * 1e9:.4f} ns")
print(f"modal spread           {spread * 1e12:.6f} ps")
print(f"which allows           {1.0 / (2.0 * spread) / 1e6:.6f} Mb/s over this km")
```

Two arrival times, 4936.7486 ns and 5004.3753 ns, differing by 67626.693273 ps. The lab
*Pulse spreading and the bit rate it allows* asserts that spread as 67626.69327305007 ps
against the closed form, and the two agree because they are the same subtraction.

The last line applies the engineering rule the derivation ends on: allow the pulse to
spread over at most half a bit period, so $B = 1/(2\tau)$. A kilometre of this fibre
carries 7.39 Mb/s. That is the reason step-index multimode fibre is not a long-haul
medium and never was — the index step that makes it easy to couple into is the same
index step that spreads its pulses.

## Colour, not path

Kill the modal term by allowing one path only, and a second mechanism is waiting
underneath.

EMAG510 met it on brass. Two metres of WR-90 answered "how long does a signal take to
cross?" twice — 5.0369 ns read off the phase and 8.8360 ns measured on the envelope —
because $\beta$ was not proportional to $\omega$, so the chord and the tangent of the
dispersion curve had different slopes. Silica bends its curve for different reasons:
the material index depends on wavelength, and module 2's $b(V)$ curve adds a second
contribution, because $V$ contains $\lambda_0$ and so $n_e$ moves with wavelength even
in glass that does not. The consequence is the one EMAG510 established. Group delay
depends on frequency, so a source that is not monochromatic arrives spread out.

Fibre engineering rarely goes back to $d^2\beta/d\omega^2$ for this. It measures the
delay against wavelength on a real reel and quotes the slope:

$$\tau_c = D\,L\,\Delta\lambda, \qquad [D] = \frac{\text{ps}}{\text{nm}\cdot\text{km}}$$

The units are the formula. Standard single-mode fibre is about 17 ps/(nm·km) at 1550 nm.
Near 1310 nm the material and waveguide contributions have opposite signs and cancel, so
$D$ passes through zero — which is why 1310 was the first long-haul window even though
1550 has the lower loss, and why moving the waveguide term by redesigning the index
profile (dispersion-shifted fibre) moves the zero to where you want it.

The sandbox *A link is a low-pass filter* is this same fact in the frequency domain: a
wider spread is a lower corner. Two things there are worth carrying. The corner $\omega_n$
is where the phase crosses $-90°$ and not where the magnitude is 3 dB down — at the
$\zeta = 0.9$ the chart opens on, the magnitude at $\omega_n$ is already 5.1 dB down and
the 3 dB point sits back at $0.75\,\omega_n$. And the roll-off is 40 dB per decade
because there are two poles: the fibre and the receiver front end are separate band
limits, and a link that is 20 per cent too long is not 20 per cent worse.

## Two mechanisms, added the way independent things add

Path spreading and colour spreading have nothing to do with each other. One is
geometrical and would exist in a fibre with no dispersion in its glass; the other is
material and would exist in a fibre with one mode. Independent broadenings add as
variances rather than as widths, so the total is the quadrature sum
$\tau_t = \sqrt{\tau_m^2 + \tau_c^2}$.

That square root is the whole story of which term matters.

```python
import math

modal_ps = 67626.69327305007          # the 1 km multimode reel
d_ps = 17.0                           # ps/(nm km), standard fibre at 1550 nm

for w_nm in (40.0, 1.0, 0.1):
    chrom = d_ps * 1.0 * w_nm
    total = math.hypot(modal_ps, chrom)
    print(f"source {w_nm:5.1f} nm: chromatic {chrom:6.1f} ps, total {total:.8f} ps,"
          f" {1.0 / (2.0 * total * 1e-12) / 1e6:.7f} Mb/s")

print(f"in quadrature a 17 ps mechanism adds "
      f"{math.hypot(modal_ps, 17.0) - modal_ps:.10f} ps, not 17")
print(f"50 km of single-mode at 1 nm: {d_ps * 50.0 * 1.0:.1f} ps"
      f" -> {1.0 / (2.0 * 850.0 * 1e-12):.6f} bit/s")
for w_nm in (40.0, 0.1):
    reach = 1.0 / (2.0 * 1.0e10 * d_ps * w_nm * 1e-12)
    print(f"the same {w_nm:4.1f} nm source on a 10 Gb/s single-mode link"
          f" reaches {reach:.5f} km")
```

A 17 ps mechanism sitting beside a 67626.693 ps one contributes 0.0021367302 ps — its
own size divided by eight thousand. The lab pins that total at 67626.69540978027 ps and
checks that the achievable bit rate moves by under one part in $10^4$, which is the
quadrature rule stated as a test rather than a claim.

The 50 km line is the same arithmetic on a link where the modal term is absent: 850 ps
of chromatic spread allows 588235294.117647 bit/s, which the lab also asserts. Nothing
about the formula changed. What changed is which term is the biggest one in the root.

## The mistake: buying the lever that works somewhere else

Faced with a link that is too slow, the reflex is to narrow the source. It is the one
change that does not involve digging up cable, $\tau_c = DL\Delta\lambda$ is linear and
memorable, and on single-mode links the improvement is spectacular — the last two lines
above take the dispersion-limited reach of a 10 Gb/s link from 73.5 m with a 40 nm LED
to 29.41176 km with a 0.1 nm DFB, a factor of four hundred.

Apply the same swap to the kilometre of multimode on the bench and the achievable bit
rate goes from 7.3931565 Mb/s to 7.3935302 Mb/s. That is a gain of five parts in a
hundred thousand, for a source costing perhaps a hundred times as much. The quadrature
root has swallowed the entire improvement, because it was never the term that was
binding.

What makes this tempting rather than careless is that the calculation is correct in both
cases. The chromatic spread really did fall by a factor of 400 on the multimode reel too
— from 680 ps to 1.7 ps. It made no difference because 680 ps was already invisible
beside 67.6 ns. A budget exists so that you find out which term dominates *before*
spending anything, and the same discipline reappears in the next module, where the
question is whether a link is short on power or short on bandwidth.

## Where this stops holding

**The two-ray estimate is a worst case that real fibre does not reach.** Nothing keeps a
ray on one path for a kilometre. Micro-bends and index fluctuations couple power between
modes continually, so a photon that starts on the extreme ray spends part of its journey
near the axis. The spread then grows closer to $\sqrt{L}$ than to $L$ beyond a few
hundred metres, and the bandwidth–length product that the $B = 1/(2\tau_m)$ rule implies
is constant is not constant. Vendors quote multimode bandwidth at a stated length and a
stated launch condition for exactly this reason.

**A step index is the worst possible profile.** Grade the index parabolically and the
axial rays travel through the highest index, so they go slowest, while the steep rays
spend most of their path out where the glass is faster. The compensation is first-order
exact, and what is left goes as $\Delta^2$ rather than $\Delta$.

```python
import math

C = 2.99792458e8
n1, n2 = 1.48, 1.46
delta = (n1 - n2) / n1

step = 1e3 * n1 * (n1 - n2) / (C * n2) * 1e12
graded = 1e3 * n1 * delta * delta / (2.0 * C) * 1e12
print(f"step index    {step:10.3f} ps/km")
print(f"graded index  {graded:10.3f} ps/km   ({step / graded:.1f} times narrower)")

for l_km in (1.0, 100.0):
    pmd = 0.1 * math.sqrt(l_km)               # ps, at 0.1 ps/sqrt(km)
    chrom = 17.0 * l_km * 0.1
    print(f"{l_km:6.1f} km single-mode: chromatic {chrom:7.2f} ps, PMD {pmd:5.3f} ps,"
          f" total {math.hypot(chrom, pmd):8.4f} ps")
```

450.762 ps/km against 67626.693 — a factor of 150 for a change in profile and none in
material. Every multimode fibre sold for data communications is graded, and the lab's
step-index formula describes the fibre nobody buys.

**"Single-mode" is a claim about one polarisation.** Module 2 found the TE and TM
fundamentals of a symmetric slab at effective indices differing by $7.8\times10^{-5}$.
A real fibre is nominally circular, so the two polarisations are nominally degenerate,
and every departure from circularity — ovality, stress, a cable bend — splits them
again. The residue is polarisation-mode dispersion, quoted as a coefficient in
ps/$\sqrt{\text{km}}$ because the birefringence axis rotates randomly along the fibre and
the walk-off accumulates as a random walk. The last two lines put it at 1.0 ps over
100 km against 170 ps of chromatic spread: negligible at 10 Gb/s, and the limiting term
once chromatic dispersion has been compensated away, which is what happens on any modern
long-haul link.

**The half-bit-period rule is a rule.** It stands for roughly a 1 dB power penalty in a
particular receiver, not a theorem. The honest calculation is a dispersion penalty
computed at a target bit error rate for the actual pulse shape and detector, and it can
land anywhere from a third of a bit period to two-thirds. The rule is what you use to
decide whether a design is worth simulating.

**$D$ is not a constant.** It has a slope of roughly 0.09 ps/(nm²·km), so a source 40 nm
wide sees $D$ vary by about 3.6 ps/(nm·km) across its own spectrum. Worse, at the
dispersion zero the first-order formula predicts no spread at all, which is wrong: what
survives there is the slope term, going as $\Delta\lambda^2$ rather than
$\Delta\lambda$. A link designed at exactly 1310 nm is limited by a mechanism the
formula in this module cannot see.
''',
                },
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
            "quiz": {
                "title": "Different paths, different colours, different arrival times",
                "minutes": 7,
                "questions": [
                    {
                        "q": "In a step-index multimode guide, how much longer is the extreme ray's path than the axial one?",
                        "opts": [
                            "A factor of $n_1/n_2$",
                            "A factor of $n_1/n_0$",
                            "A factor of $\\sqrt{n_1/n_2}$",
                            "It depends on the launch power",
                        ],
                        "a": 0,
                        "why": r"""
The steepest guided ray travels at the critical angle, and the geometry gives a path
$n_1/n_2$ times the length. For $n_1 = 1.48$, $n_2 = 1.46$ that is 1.4% — which sounds
negligible and over a kilometre is about 68 ns of spread, enough to close the eye at
10 Mbit/s. Small fractional differences over long distances are what dispersion is.
""",
                    },
                    {
                        "q": "Why does single-mode fibre have no modal dispersion?",
                        "opts": [
                            "There is only one path, so there is nothing to spread against",
                            "Its index difference is zero",
                            "Its modes travel at the same speed",
                            "Its cladding absorbs the higher modes",
                        ],
                        "a": 0,
                        "why": r"""
One mode, one group velocity, no spread from this mechanism at all — which is why
single-mode fibre outperforms multimode by orders of magnitude in bandwidth-distance
product. It is not free: the core is around 9 µm instead of 50, so alignment tolerances
become severe and connectors get expensive. Chromatic dispersion remains, and becomes the
limit instead.
""",
                    },
                    {
                        "q": "Chromatic dispersion is quoted as a coefficient $D$. What does it multiply?",
                        "opts": [
                            "Length and source linewidth: $\\Delta\\tau = D\\,L\\,\\Delta\\lambda$",
                            "Length alone",
                            "Linewidth alone",
                            "Bit rate and length",
                        ],
                        "a": 0,
                        "why": r"""
Both, linearly. That gives two independent levers: shorten the link, or narrow the
source. A DFB laser at 0.1 nm instead of an LED at 40 nm is a factor of 400 in pulse
spread for no change to the fibre at all, which is why source linewidth is specified as
carefully as fibre grade.
""",
                    },
                    {
                        "q": "What are the units of $D$?",
                        "opts": ["ps/(nm·km)", "ps/km", "ns/nm", "dB/km"],
                        "a": 0,
                        "why": r"""
Picoseconds of spread, per nanometre of source width, per kilometre of fibre — the units
are the formula. Standard single-mode fibre is about 17 ps/(nm·km) at 1550 nm, and near
zero at 1310 nm, which is why 1310 was the first long-haul window even though 1550 has
lower loss. dB/km is attenuation, a different budget entirely.
""",
                    },
                    {
                        "q": "You halve the source linewidth. What happens to the chromatic spread?",
                        "opts": ["It halves", "It quarters", "It is unchanged", "It falls by $\\sqrt{2}$"],
                        "a": 0,
                        "why": r"""
Linear in $\Delta\lambda$, so halving halves it — and since the total spread combines
with the modal term in quadrature, the *system* improvement is smaller than that whenever
another term is comparable. Knowing which term dominates before optimising is the whole
point of writing the budget down, and it is the same discipline as the loss budget in the
next module.
""",
                    },
                ],
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
            "read": [
                {
                    "title": "Twenty-one point four decibels, and the ninety-four kilometres that were not there",
                    "minutes": 16,
                    "body": r'''
An OTDR is plugged into one end of a newly installed 80 km span and the trace comes back
on the screen: a straight line sloping down at 0.25 dB per kilometre, with eight small
steps in it where the fusion splices are, a step at each end where the patch connectors
sit, and one spike at the 42 km mark that is a mechanical splice reflecting light back
up the fibre.

Unplug the OTDR, put a calibrated source on one end and a power meter on the other, and
the end-to-end insertion loss reads 21.4 dB. The transmitter launches 0 dBm. The receiver
is specified to work down to $-28$ dBm.

That is the entire question a link budget asks, and the answer is a subtraction: the
receiver sees $-21.4$ dBm, which is 6.6 dB more than it needs. The link works, and it
will keep working for as long as those 6.6 dB last.

## Why the arithmetic is addition

Each thing between the laser and the detector *multiplies* the power by its own factor.
Eighty kilometres of fibre passes some fraction, a connector passes another, a splice a
third, and the power arriving is the product of all of them. Products are hard to hold in
the head and impossible to scan for the dominant term.

Take the logarithm and the product becomes a sum. Define a loss in decibels as
$-10\log_{10}(P_\text{out}/P_\text{in})$ and each element contributes one number, added.
Define an absolute level the same way against a fixed reference of 1 mW — that is the
"m" in dBm — and a level minus a set of losses is a level again. This is the whole
reason a budget is a column of numbers rather than a chain of fractions, and the useful
consequence is not the arithmetic but the visibility: the biggest number in the column
is the thing to fix, and you can see it without doing any work. The exercise *Every
decibel between the laser and the detector* asks for that reason in as many words, and
for the reference behind the "m", which is 1 mW and nothing else.

```python
alpha, L = 0.25, 80.0                       # dB/km, km
connectors, splices = 2 * 0.5, 8 * 0.05     # two connectors, eight fusion splices
loss = alpha * L + connectors + splices
p_tx, sens = 0.0, -28.0                     # dBm launched, dBm needed

print(f"fibre       {alpha * L:6.2f} dB")
print(f"connectors  {connectors:6.2f} dB")
print(f"splices     {splices:6.2f} dB")
print(f"total       {loss:6.2f} dB")
print(f"received    {p_tx - loss:6.2f} dBm = "
      f"{1e3 * 10 ** ((p_tx - loss) / 10.0):.4f} uW")
print(f"margin      {p_tx - sens - loss:6.2f} dB")
print(f"reach at 3 dB of margin: "
      f"{(p_tx - sens - connectors - splices - 3.0) / alpha:.1f} km")
```

The fibre is 20.00 of the 21.40 dB and everything else is rounding error beside it. The
receiver sees 7.2444 µW, which is a real power a meter reads. And the last line is the
derivation *Rearranging a budget for reach* run backwards: hold 3 dB in reserve, ask how
much fibre the rest will pay for, and the answer is 94.4 km. That is the form a designer
actually wants, and it is the number the lab *Build a link budget and invert it* asserts
as 94.4 exactly, along with a check that feeding that length back through the forward
calculation returns the 3 dB you asked for.

The sandbox *Margin as the gap above the sensitivity line* draws the same picture:
$K = 6$ puts the received level $20\log_{10}6 = 15.6$ dB above the dashed sensitivity
line, and every term in the budget eats into that gap. Take $K$ down to 1 and the curve
starts *on* the line — a budget with no margin, before the link has aged a day.

## The one term that is not bookkeeping

Seven of the eight splices are fusion splices at 0.05 dB. The spike at 42 km is a
mechanical splice, and a mechanical splice leaves a gap. Module 1 already has what is
needed: a face between silica and air reflects $((n_2-n_0)/(n_2+n_0))^2$ of the power,
and the light crosses two of them.

```python
import math

n_core = 1.46
for name, n_gap in (("air", 1.0), ("gel at 1.30", 1.30), ("index-matched", 1.46)):
    r = ((n_core - n_gap) / (n_core + n_gap)) ** 2
    print(f"{name:>14}: R = {r:.10f}   the pair of faces costs "
          f"{-10 * math.log10((1.0 - r) ** 2) + 0.0:.12f} dB")

r = ((1.46 - 1.0) / (1.46 + 1.0)) ** 2
t_min = (1.0 - r) ** 2 / (1.0 + r) ** 2
print(f"gap as two independent faces: {-10 * math.log10((1.0 - r) ** 2):.6f} dB")
print(f"gap as a cavity, worst case:  {-10 * math.log10(t_min):.6f} dB")
print(f"gap as a cavity, best case:   {-10 * math.log10(1.0) + 0.0:.6f} dB")
```

0.309147341887 dB for an air gap, which the lab checks to that many digits, and
0.029239294224 dB once the gap is filled with gel at $n = 1.30$. A factor of ten and
six fusion splices' worth of loss, bought with a substance whose only job is to have
roughly the right index. On the Smith chart it is the load moved to the centre; the
argument is EMAG520's, and the same argument produces the anti-reflection coating,
where a quarter-wave layer at $n = \sqrt{n_0n_1} = 1.208$ transforms one impedance into
the other instead of matching them directly.

## The mistake: a reach with no bit rate in it

The budget above produced 94.4 km. It is a confident, well-founded number, and there is
a way of using it that gets a link built and then found dead.

```python
p_tx, sens, alpha, fixed, margin = 1.0, -22.0, 0.25, 1.3, 3.0
d_ps, w_nm = 17.0, 0.1

loss_km = (p_tx - sens - fixed - margin) / alpha
for bitrate in (1.0e9, 1.0e10):
    disp_km = 1.0 / (2.0 * bitrate * d_ps * w_nm * 1e-12)
    binding = "loss" if loss_km <= disp_km else "dispersion"
    print(f"{bitrate / 1e9:5.1f} Gb/s: power allows {loss_km:.2f} km, "
          f"dispersion allows {disp_km:.5f} km -> limited by {binding}")
print("nothing in the power budget mentions the bit rate, so it cannot warn you")
```

Those are the capstone's own numbers. The same physical route — same fibre, same
connectors, same laser, same receiver — is loss-limited at 74.80 km when it runs at
1 Gb/s and dispersion-limited at 29.41176 km when it runs at 10 Gb/s. Build 70 km of it
for the 10 Gb/s service and every power measurement on commissioning will pass, because
the power is fine. What fails is the eye, and no meter in the loss budget looks at it.

The trap is specific and worth stating plainly: $P_t$, $S$, $\alpha$, $A_c$, $A_s$ and
$M$ contain no bit rate between them, so the reach they produce is not a function of the
bit rate, and a calculation that cannot see a variable cannot warn you about it. What
makes the error tempting is that the loss budget is the calculation everyone knows how
to do, it terminates in kilometres, and its answer is correct — it is the answer to a
different question. The capstone asks for both limits and the name of the one that
binds, and it asks for the name because the name is the thing that tells you what to
buy: a lower-loss fibre moves 74.80 and does nothing at all to 29.41176.

## Where the budget stops holding

**Two faces are not two independent events.** The 0.309147 dB above multiplies
$(1-R)$ twice, which assumes the light forgets its phase between the faces. Two parallel
partial reflectors a few wavelengths apart form a weak Fabry–Perot cavity, and the
transmission runs between 1 and $(1-R)^2/(1+R)^2$ depending on the gap to a fraction of a
wavelength: from 0.000000 dB to 0.607669 dB, with the budget's 0.309147 sitting in the
middle as the incoherent average. A connector that changes loss by half a decibel when
you warm it with your hand is not faulty; it is a cavity being tuned by thermal
expansion.

**Attenuation is a spectrum, not a number.** 0.25 dB/km is silica at 1550 nm. The same
fibre is about 0.35 dB/km at 1310 nm, and older fibre has a water absorption peak near
1383 nm that can exceed 1 dB/km. A budget written for one window does not transfer to
another, and re-using a spare fibre at a different wavelength has caught out more than
one commissioning team.

**Splice loss is a distribution.** 0.05 dB is a mean from a good machine on matched
fibre. Field splices have a tail — a fibre-type mismatch, a bad cleave, a cold day —
and a budget that multiplies a count by a mean has calculated the expected loss of a
route rather than the loss of *this* route. The honest form adds the mean and holds
enough margin for the tail, which is one of the things the margin term is doing.

**The receiver has a ceiling as well as a floor.** Sensitivity is the least power that
works; there is also an overload point above which the front end saturates and the error
rate rises again. A 500 m link built with a transmitter sized for 80 km fails, and it
fails in a way that looks exactly like a loss problem until somebody inserts a 10 dB
attenuator and it starts working.

**Power stops buying reach.** The budget is linear in $P_t$, so 10 dB more launch power
reads as 40 km more fibre. Above roughly +10 dBm into a single-mode core that stops being
true: stimulated Brillouin scattering reflects the excess back up the fibre, and
self-phase modulation broadens the source spectrum, which feeds straight back into the
$D\,L\,\Delta\lambda$ of the last module and shortens the dispersion limit. The two
budgets stop being independent at exactly the point where you try hardest to win.

**Margin is not slack.** It is a forecast of the things not on the drawing: connector
end faces collecting dust, two more splices when a digger finds the cable, a laser
dimming perhaps 1 dB across twenty-five years, temperature moving everything by a few
tenths. Those add to something close to 2 dB on an ordinary route, which is why 3 dB is
a thin margin and not a generous one, and why a budget that closes at 0.0 dB has been
shown to close on precisely one day.
''',
                },
            ],
            "quiz": {
                "title": "What is left after every decibel has been subtracted",
                "minutes": 8,
                "questions": [
                    {
                        "q": "Why is a link budget worked in decibels rather than in milliwatts?",
                        "opts": [
                            "Every element multiplies the power, and a logarithm turns that product into a column you can add",
                            "Optical detectors respond to the logarithm of the incident power, so decibels are the natural unit",
                            "Milliwatts span too many orders of magnitude along a long span to be written out conveniently",
                            "Power and voltage ratios differ by a factor of two, and only decibels can express both at once",
                        ],
                        "a": 0,
                        "whys": [
                            r"Fibre, connectors and splices each pass a fraction, so the received power is a product of fractions. Logarithms turn it into a sum, and a sum can be scanned for its biggest term at a glance.",
                            r"A photodiode's current is linear in optical power, not logarithmic. The logarithm is a choice made by the engineer writing the budget, not a property of the detector.",
                            r"True as far as it goes — 7 µW against 1 mW is a wide range — but compression is a side benefit. A budget in milliwatts would still be a product, and still be unreadable.",
                            r"That factor of two is a detail of how dB is defined for field quantities, and it is a source of confusion rather than the reason the unit is used here.",
                        ],
                        "why": r"""
Each element between laser and detector multiplies the power by its own fraction, so the
received power is a product. Taking logarithms makes it a sum, which is why a budget is
a column of numbers. The real payoff is not the ease of adding but what the column shows:
in the 80 km span here, 20.00 dB of the 21.40 dB total is fibre, and the eye finds that
without any arithmetic at all. Try the same in milliwatts and the dominant term is
invisible.
""",
                    },
                    {
                        "q": "A power budget gives a reach of 74.8 km. The link is built at 70 km, runs at 10 Gb/s, and fails — yet every power measurement passes. What was missed?",
                        "opts": [
                            "Dispersion, which limits this route to 29.4 km and appears nowhere in a power budget",
                            "The margin, which should have been larger on a route so near the 74.8 km limit",
                            "The splice count, since field splices scatter above their nominal loss and eight of them add up",
                            "Receiver overload, because at only 70 km the arriving power is above what the front end tolerates",
                        ],
                        "a": 0,
                        "whys": [
                            r"$D\,L\,\Delta\lambda$ reaches half a bit period at 29.4 km on this route at 10 Gb/s. The power budget contains no bit rate, so it could not have flagged it.",
                            r"Margin protects against loss that appears later, and the power measurements are passing — the problem is not a shortage of decibels at any point in the link's life.",
                            r"Splice scatter would show up as extra loss, and the measurements pass. It is a real risk on a real route, and it is not what fails here.",
                            r"Overload is a genuine failure mode on short links, but 70 km of fibre at 0.25 dB/km removes 17.5 dB, so the arriving power is nowhere near a front end's ceiling.",
                        ],
                        "why": r"""
The reach a power budget returns is a function of $P_t$, $S$, $\alpha$, the fixed losses
and $M$, and not one of those depends on the bit rate. Run the same route at 1 Gb/s and
it is loss-limited at 74.8 km; run it at 10 Gb/s and chromatic dispersion closes the eye
at 29.4 km, with the power still perfectly healthy. A calculation that does not contain a
variable cannot warn you about it, and the fix follows from naming which limit binds: a
lower-loss fibre moves 74.8 km and leaves 29.4 km exactly where it was.
""",
                    },
                    {
                        "q": "A mechanical splice leaves a small air gap between two fibre ends. What does the gap cost, and why?",
                        "opts": [
                            "About 0.31 dB: the light crosses two silica–air faces and each returns roughly 3.5 per cent",
                            "About 0.15 dB: one interface, since the two fibre ends are the same material as each other",
                            "About 0.07 dB, from adding the two reflectances and converting the 7 per cent total to decibels",
                            "Nothing measurable, since the gap is far shorter than a wavelength and the light crosses it",
                        ],
                        "a": 0,
                        "whys": [
                            r"Two faces, each passing $1 - R$ with $R = 0.03497$, so the pair passes $(1-R)^2 = 0.9313$ — a loss of 0.309147 dB, or six fusion splices in one component.",
                            r"Counting one face is the commonest slip here. The light leaves glass into air at the first face and re-enters glass at the second, and both are index steps.",
                            r"Adding reflectances instead of multiplying transmissions gives 0.3145 dB, which happens to be close — near enough to hide the error, and wrong in a way that grows as $R$ does.",
                            r"The gap length has almost nothing to do with it. The loss is at the two interfaces, and it would be there for a gap of any width at all.",
                        ],
                        "why": r"""
$R = ((1.46-1)/(1.46+1))^2 = 0.03497$ at each face, and the light crosses two of them, so
the pair passes $(1-R)^2 = 0.9313$ — a loss of 0.309147 dB. That is six times a 0.05 dB
fusion splice, from one component, which is the reason fusion splicing exists. Fill the
gap with gel at $n = 1.30$ and $R$ drops to 0.00336 and the loss to 0.029239 dB. The
whole of that improvement comes from choosing a material with roughly the right index —
the same move as sliding a load to the centre of a Smith chart.
""",
                    },
                    {
                        "q": "A budget closes with exactly 0.0 dB of margin. What is wrong with that?",
                        "opts": [
                            "It closes only while nothing changes: dirt, repairs and laser ageing all spend decibels later",
                            "It gives no allowance for the power meter's calibration error, which is typically a few tenths",
                            "Sensitivity is quoted at one bit rate, so a budget with no margin cannot be reused at another",
                            "It leaves nothing to spend if the link is later upgraded to a longer span or a faster line rate",
                        ],
                        "a": 0,
                        "whys": [
                            r"Connector end faces collect dust, a cut cable comes back with two more splices, and a laser dims perhaps 1 dB across its life. Around 2 dB of that is ordinary, and a 0 dB budget has none of it.",
                            r"Instrument error is real and is handled by measuring carefully, not by holding decibels back for years. Margin is about the link changing, not about the meter being unsure.",
                            r"Sensitivity does depend on bit rate, which is why it is read from the data sheet at the rate in use. That is a term in the budget, not the job of the margin.",
                            r"Headroom for a future upgrade is a reasonable thing to want and a different thing to want. Margin is spent by the link you have, on the route you have, doing nothing new.",
                        ],
                        "why": r"""
Margin is a forecast of everything not on the drawing. End faces collect dust, a digger
finds the cable and the repair adds two splices, a laser dims about 1 dB across
twenty-five years, and temperature moves everything by a few tenths. On an ordinary route
those come to something near 2 dB, which is why 3 dB is thin rather than generous. A
budget closing at 0.0 dB has been shown to close on the day of installation, and on no
other day.
""",
                    },
                    {
                        "q": "A receiver sensitivity is $-28$ dBm and a connector loss is 0.5 dB. How do the two units differ?",
                        "opts": [
                            "dBm fixes a power against 1 mW; dB is a bare ratio, so a level minus ratios is a level",
                            "dBm is used for optical power and dB for electrical power, which is why both appear here",
                            "They differ by a constant 30, which is the number of decibels between a milliwatt and a watt",
                            "dBm means the figure was measured on an instrument, where dB means it was computed",
                        ],
                        "a": 0,
                        "whys": [
                            r"$-28$ dBm is $1.6\ \mu$W, a power you could put on a meter. 0.5 dB is a fraction, 0.891, and nothing else. Subtracting the second from the first leaves a power, which is what makes the column work.",
                            r"Both units appear on both sides of a photodiode, and neither is optical or electrical by nature. The distinction is absolute against relative.",
                            r"30 dB is the gap between dBm and dBW, which is a different pairing. Confusing those two is a factor of a thousand and does happen.",
                            r"Neither notation says anything about provenance. A sensitivity in dBm is usually a data-sheet figure, and a measured loss in dB is measured.",
                        ],
                        "why": r"""
dBm is absolute: it is a power expressed against a fixed 1 mW reference, so $-28$ dBm is
1.6 µW and $0$ dBm is 1 mW. Plain dB is a ratio with no reference at all, so 0.5 dB names
the fraction 0.891 and nothing more. That is what makes the budget's arithmetic legal —
an absolute level minus a sum of ratios is an absolute level, and the final comparison is
level against level. Mixing the two, or reaching for dBW by mistake, is the classic
budget error and it costs a factor of a thousand.
""",
                    },
                    {
                        "q": "A 500 m link is built with a transmitter chosen for an 80 km span and it does not work. Inserting a 10 dB attenuator makes it work. Why?",
                        "opts": [
                            "The front end was saturating: a receiver has an overload point above its sensitivity floor",
                            "The attenuator absorbed the reflections travelling back up the fibre to the laser",
                            "At that launch power the fibre is nonlinear, and the attenuator brought it back into the linear region",
                            "The extra connectors carrying the attenuator added the loss the original budget had assumed",
                        ],
                        "a": 0,
                        "whys": [
                            r"Sensitivity is a floor; every receiver also has a ceiling, and 500 m of fibre removes only 0.125 dB. Padding the link down to the working window is the standard fix.",
                            r"Back-reflection into a laser is a real problem with real cures — angled connectors, isolators — but it does not improve when you attenuate, since the pad affects both directions.",
                            r"Nonlinearity is a long-span effect needing kilometres of interaction length. Over 500 m at an ordinary launch power there is nothing for it to build up in.",
                            r"The connectors do add loss, and that is the same fix by a different name: the link needed less power arriving, however the reduction was obtained.",
                        ],
                        "why": r"""
The budget in this module treats sensitivity as a threshold to be cleared, and the more
power that arrives the better. That holds only up to the receiver's overload point, above
which the front end saturates and the error rate rises again. Over 500 m the fibre
removes 0.125 dB, so a transmitter sized for 80 km delivers nearly all its power into a
receiver expecting a fraction of it. The symptom looks exactly like a loss fault until
somebody pads the link, which is why short links built with long-haul optics ship with an
attenuator in the box.
""",
                    },
                ],
            },
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
            "blanks": {
                "title": "Every decibel between the laser and the detector",
                "minutes": 8,
                "caption": "budget.py — a chain of multiplications, added up",
                "lang": "python",
                "brief": r"""
A link works or it does not, and the answer is a subtraction. Fill in the terms, and the
reason the whole calculation is done in decibels rather than in milliwatts.
""",
                "listing": """# Decibels are used here because they turn ___ .

# 0 dBm is defined as ___ .

P_rx_dBm = P_tx_dBm - alpha*L - splices - connectors - ___

# and the link closes if

#     P_rx_dBm >= ___
""",
                "blanks": [
                    {
                        "prompt": "Why decibels at all?",
                        "hole": "?",
                        "opts": [
                            "a chain of multiplications into a sum",
                            "a small number into a large one",
                            "power into voltage",
                            "an absolute measure into a relative one",
                        ],
                        "a": 0,
                        "why": "Each element multiplies the power by its own factor, and logarithms turn products into sums — so a budget becomes a column of numbers you can add in your head and, more importantly, one where you can see at a glance which term dominates. That visibility is the real reason, more than the arithmetic convenience.",
                        "whys": [
                            "Each element multiplies the power by its own factor, and logarithms turn products into sums — so a budget becomes a column of numbers you can add in your head and, more importantly, one where you can see at a glance which term dominates. That visibility is the real reason, more than the arithmetic convenience.",
                            "Compressing the range is a side effect, and a useful one, but not what makes the budget work.",
                            "Decibels relate powers to powers; the voltage form differs only by a factor of two in the definition.",
                            "dBm is absolute and plain dB is relative — the notation carries both, which is the opposite of a conversion.",
                        ],
                    },
                    {
                        "prompt": "The absolute reference.",
                        "hole": "?",
                        "opts": ["1 mW", "1 W", "1 uW", "0 W"],
                        "a": 0,
                        "why": "The m in dBm. So $-30$ dBm is 1 µW and $+10$ dBm is 10 mW, and a receiver sensitivity of $-28$ dBm is a genuine power you could measure with a meter. Mixing dBm and dB in the same column — one absolute, one a ratio — is the classic budget error.",
                        "whys": [
                            "The m in dBm. So $-30$ dBm is 1 µW and $+10$ dBm is 10 mW, and a receiver sensitivity of $-28$ dBm is a genuine power you could measure with a meter. Mixing dBm and dB in the same column — one absolute, one a ratio — is the classic budget error.",
                            "1 W is the reference for dBW, used in radio transmitters; it is 30 dB away from dBm and confusing the two is a factor of a thousand.",
                            "Not a standard reference; dBµ exists but means something else again.",
                            "Zero power is minus infinity on a logarithmic scale and cannot be a reference.",
                        ],
                    },
                    {
                        "prompt": "One more term before the comparison.",
                        "hole": "?",
                        "opts": [
                            "a system margin for ageing and repairs",
                            "the receiver sensitivity",
                            "the transmitter power again",
                            "the dispersion penalty in ps",
                        ],
                        "a": 0,
                        "why": "A few decibels held back deliberately, because connectors get dirty, splices get added when a cable is cut and repaired, and the laser dims over years. A budget that closes with 0 dB of margin closes only on the day it was installed.",
                        "whys": [
                            "A few decibels held back deliberately, because connectors get dirty, splices get added when a cable is cut and repaired, and the laser dims over years. A budget that closes with 0 dB of margin closes only on the day it was installed.",
                            "Sensitivity is what the result is compared *against*, on the next line — subtracting it here would count it twice.",
                            "The transmit power is already the first term.",
                            "Dispersion is measured in picoseconds and cannot be subtracted from a power. It enters as a separate penalty in dB, once converted.",
                        ],
                    },
                    {
                        "prompt": "What does the received power have to beat?",
                        "hole": "?",
                        "opts": [
                            "the receiver sensitivity",
                            "the transmitter power",
                            "zero dBm",
                            "the fibre attenuation",
                        ],
                        "a": 0,
                        "why": "The least power the receiver can turn into bits at the required error rate — which is a specification of the receiver, quoted in dBm, and depends on the bit rate. Note there is usually an upper limit too: too much power saturates the receiver, so a short link sometimes needs an attenuator, which surprises people the first time.",
                        "whys": [
                            "The least power the receiver can turn into bits at the required error rate — which is a specification of the receiver, quoted in dBm, and depends on the bit rate. Note there is usually an upper limit too: too much power saturates the receiver, so a short link sometimes needs an attenuator, which surprises people the first time.",
                            "The received power is always below the transmitted power; comparing them says only that the fibre is lossy.",
                            "0 dBm is 1 mW, far above any receiver's threshold — this test would fail every real link.",
                            "The attenuation is one of the terms already subtracted, not the threshold.",
                        ],
                    },
                ],
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
