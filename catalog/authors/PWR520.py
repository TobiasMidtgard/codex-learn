"""PWR520 — Motor Drives and Field-Oriented Control.

Authored to the same rules as CTRL510, which is the reference module for this
catalog:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and sympy are allowed (both gates can run them); scipy is not
  * seed every RNG, and every expected value must be one that was computed

The machine used throughout is a four-pole-pair interior PMSM on a 300 V bus:
R = 0.45 Ω, L_d = 3.5 mH, L_q = 5.5 mH, λ_m = 85 mWb. The saliency is real
(L_q > L_d), so the reluctance term in the torque equation is not decoration.
"""

COURSE = {
    "id": "PWR520",
    "title": "Motor Drives and Field-Oriented Control",
    "band": 4,
    "level": "Expert",
    "prereqs": ["PWR510", "CTRL510"],
    "stack": ["Python", "NumPy"],
    "credits": 12,
    "hours": 150,
    "icon": "◐",
    "summary": (
        "A three-phase machine looks like three coupled time-varying inductors, which is "
        "an unpleasant thing to control. Field-oriented control makes the problem "
        "disappear by moving to a frame that turns with the rotor: in that frame the "
        "currents are constants and the machine is two first-order lags with a known "
        "cross-coupling between them. This course builds the transforms, derives the dq "
        "model, tunes the current loops, works out where the 15 per cent bus advantage of "
        "space-vector modulation comes from, and closes with field weakening."
    ),
    "outcomes": [
        "Apply the Clarke and Park transforms and say precisely what each one removes from the problem.",
        "Derive the dq voltage and torque equations of a PMSM, including the reluctance term of a salient rotor.",
        "Tune a PI current regulator by pole–zero cancellation, add the cross-coupling feedforward, and defend the choice of bandwidth.",
        "Compute space-vector dwell times, and explain the 2/√3 linear range advantage over sine-triangle modulation.",
        "Command a field-weakening d-axis current that respects both the voltage ellipse and the current circle.",
    ],
    "assessment": "Four labs, each checked by execution, and a capstone that runs a complete field-oriented current loop into and through the field-weakening region.",
    "reading": [
        "*Analysis of Electric Machinery and Drive Systems*, Krause, Wasynczuk & Sudhoff — chapters 3 and 4 for the reference-frame algebra.",
        "*Control of Electrical Drives*, Leonhard — for the cascade structure and its tuning.",
        "*Electric Motor Drives*, Mohan — for the modulator and the bus-utilisation argument.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "read": [
                {
                    "title": "Two probes on a running machine, and the two numbers they carry",
                    "minutes": 15,
                    "body": r'''
Clamp current probes on leads $a$ and $b$ of the machine this course runs on — a
four-pole-pair interior PMSM, $R = 0.45\ \Omega$, $L_d = 3.5$ mH, $L_q = 5.5$ mH,
$\lambda_m = 85$ mWb, on a 300 V bus — and load it to 4.08 N·m at 1910 rpm. Both traces
are sinusoids of 8.0 A peak at 127.3 Hz, one a third of a period behind the other.

Now open the drive's debug window on the same machine at the same instant. It shows two
numbers, $i_d = 0.00$ and $i_q = 8.00$, and they do not move. Nothing has been filtered
and nothing has been averaged: those numbers are computed from those two probes, sample
by sample, at the 10 kHz modulator rate. Two waveforms at 127.3 Hz go in, and two
constants come out.

The 127.3 Hz has to have gone somewhere. Following it is the whole of this module.

## The third lead was never carrying information

The three windings meet at a star point with no wire on it. Kirchhoff at that node is
not a modelling assumption, it is a wire count:

$$i_a + i_b + i_c = 0$$

so the third current is fixed the moment the other two are known. Two probes are not a
compromise on three; the drive that ships with three sensors uses the redundancy to
detect a failed one, and nothing else. The three currents live on a plane.

That plane needs a basis. Take the obvious one first and see what it forces. Insist that
the first axis, $\alpha$, lies along phase $a$, so that $i_\alpha$ *is* $i_a$ for any
current the machine can carry. Project the three phases — at $0°$, $120°$ and $240°$ —
onto that axis and scale by an unknown $k$:

$$i_\alpha = k\left(i_a\cos 0 + i_b\cos 120° + i_c\cos 240°\right)
           = k\left(i_a - \tfrac{1}{2}i_b - \tfrac{1}{2}i_c\right)$$

Apply the constraint. Since $i_b + i_c = -i_a$, the bracket collapses to
$i_a + \tfrac{1}{2}i_a = \tfrac{3}{2}i_a$, so $i_\alpha = \tfrac{3}{2}k\,i_a$, and the
demand that $i_\alpha = i_a$ fixes $k = \tfrac{2}{3}$. The constant nobody explains is
what you pay to keep the $\alpha$ axis pinned to a real winding. The derive unit *Why
the alpha axis is the a axis, and what a rotation preserves* walks that same collapse
one step at a time.

The second axis is $90°$ round, and the same projection with the same $k$ gives

$$i_\beta = \tfrac{2}{3}\left(i_a\sin 0 + i_b\sin 120° + i_c\sin 240°\right)
          = \tfrac{2}{3}\cdot\tfrac{\sqrt3}{2}\left(i_b - i_c\right)
          = \frac{i_b - i_c}{\sqrt3}$$

which is where the $\sqrt3$ in the lab's second formula comes from. Nothing has been
approximated and nothing has been discarded. This is a change of basis on a plane, and
it is invertible.

## Rotating with the rotor

In $\alpha\beta$ the 127.3 Hz is still there — the current vector sweeps a circle of
radius 8 A once per electrical cycle. Park removes it by measuring angles from the rotor
instead of from the stator. If the rotor's electrical angle is $\theta_e$, then

$$\begin{bmatrix} i_d \\ i_q \end{bmatrix} =
\begin{bmatrix} \cos\theta_e & \sin\theta_e \\ -\sin\theta_e & \cos\theta_e \end{bmatrix}
\begin{bmatrix} i_\alpha \\ i_\beta \end{bmatrix}$$

A vector that turns at exactly $\theta_e$ is at rest in that frame. Run the whole chain
forward and back at three unrelated instants of the same operating point:

```python
import math

W_E = 800.0                     # electrical rad/s: 127.3 Hz, 1910 rpm on four pole pairs
Z = lambda v: 0.0 if abs(v) < 1e-12 else v


def inv_park(d, q, th):
    return d * math.cos(th) - q * math.sin(th), d * math.sin(th) + q * math.cos(th)


def inv_clarke(al, be):
    """Amplitude-invariant, so i_a is i_alpha exactly."""
    return (al,
            -0.5 * al + 0.5 * math.sqrt(3.0) * be,
            -0.5 * al - 0.5 * math.sqrt(3.0) * be)


def clarke(a, b, c):
    return (2.0 / 3.0) * (a - 0.5 * b - 0.5 * c), (b - c) / math.sqrt(3.0)


def park(al, be, th):
    return (al * math.cos(th) + be * math.sin(th),
            -al * math.sin(th) + be * math.cos(th))


for t_us in (0.0, 100.0, 2500.0):
    th = W_E * t_us * 1e-6
    a, b, c = inv_clarke(*inv_park(0.0, 8.0, th))
    d, q = park(*clarke(a, b, c), th)
    print("t %6.0f us  theta %4.2f rad   i_abc %6.2f %6.2f %6.2f   sum %5.2f   i_dq %5.2f %5.2f"
          % (t_us, th, a, b, c, Z(a + b + c), Z(d), Z(q)))
```

The three phase currents are different at every row — at $\theta_e = 2.0$ rad phase $a$
carries $-7.27$ A and phase $b$ carries $+0.75$ A — and the last two columns read
`0.00 8.00` on all three. The regulator upstream sees a plant whose reference is a
constant, and a PI controller drives the error on a constant to zero. That property is
the reason field-oriented control exists; everything else in this course is machinery
built to keep it.

## What the transform preserves, in watts

Park is a rotation, so it changes no lengths: $i_d^2 + i_q^2 = i_\alpha^2 + i_\beta^2$.
That is not an aesthetic remark, it is where the copper loss lives. Each phase carries a
sinusoid of peak $\sqrt{i_d^2 + i_q^2} = 8.00$ A, so $8/\sqrt2 = 5.657$ A RMS, and three
of them through $0.45\ \Omega$ dissipate $3 \times 0.45 \times 5.657^2 = 43.2$ W. The
same number in the rotating frame is $\tfrac{3}{2}R\left(i_d^2 + i_q^2\right) =
1.5 \times 0.45 \times 64 = 43.2$ W, and it carries the same $\tfrac{3}{2}$ as the power
expression $p = \tfrac{3}{2}(v_di_d + v_qi_q)$ for the same reason: the amplitude-invariant
Clarke is not orthogonal, so the factor has to be carried by hand.

Against a shaft output of $4.08\ \text{N·m} \times 200\ \text{rad/s} = 816$ W, those
43.2 W are 5.3 per cent, and they depend on the *length* of the dq vector and on nothing
else. Module 4 spends that budget deliberately.

```python
import math

R, LAM, PP = 0.45, 0.085, 4
i_d, i_q = 0.0, 8.0
w_mech = 800.0 / PP

pk = math.hypot(i_d, i_q)
per_phase = 3.0 * R * (pk / math.sqrt(2.0)) ** 2
in_dq = 1.5 * R * (i_d ** 2 + i_q ** 2)
torque = 1.5 * PP * LAM * i_q
print("peak %.2f A, rms %.3f A -> abc loss %.1f W, dq loss %.1f W" % (pk, pk / math.sqrt(2.0), per_phase, in_dq))
print("torque %.2f Nm, shaft %.0f W, copper is %.1f%% of it"
      % (torque, torque * w_mech, 100.0 * in_dq / (torque * w_mech)))
```

## The mistake, and why it is tempting

The mistake is reading Clarke as a projection: three numbers in, two out, so something
must have been thrown away, and the transform must therefore be an approximation that
holds only while the machine is balanced. It is a reasonable instinct — almost every
other map from three dimensions to two that you meet does lose something — and it leads
people to hedge, to add correction terms for imbalance, and to distrust dq results on a
machine that is not perfectly symmetric.

Run the arithmetic on an unbalanced set and the instinct evaporates. Phase $a$ goes
open-circuit, so $i_a = 0$ and the remaining current shuttles through the $b$–$c$ pair:

```python
import math

W_E, N = 800.0, 2000
T_E = 2.0 * math.pi / W_E


def mean(xs):
    m = sum(xs) / len(xs)
    return 0.0 if abs(m) < 1e-9 else m           # a signed zero is still a zero


ds, qs = [], []
for n in range(N):
    th = 2.0 * math.pi * n / N
    i_a, i_b = 0.0, 8.0 * math.sin(th)     # phase a open; b and c are the only path
    i_c = -i_a - i_b
    al, be = (2.0 / 3.0) * (i_a - 0.5 * i_b - 0.5 * i_c), (i_b - i_c) / math.sqrt(3.0)
    ds.append(al * math.cos(th) + be * math.sin(th))
    qs.append(-al * math.sin(th) + be * math.cos(th))

print("i_d: mean %.3f A, peak-to-peak %.3f A" % (mean(ds), max(ds) - min(ds)))
print("i_q: mean %.3f A, peak-to-peak %.3f A" % (mean(qs), max(qs) - min(qs)))
print("the ripple is at 2*f_e = %.1f Hz, on an electrical period of %.2f ms"
      % (2.0 * W_E / (2.0 * math.pi), T_E * 1e3))
```

It reports a mean $i_d$ of 4.619 A, a mean $i_q$ of 0.000 A, and 9.238 A peak-to-peak on
both, pulsating at 254.6 Hz. The magnet torque follows $i_q$, so its average is zero: the
machine makes no useful torque and shakes at twice electrical frequency. That is a
correct, complete, exact description of a broken machine, produced by a transform that
supposedly only works on balanced sets. Clarke did not lose the fault. Park moved it to
$2\omega_e$, where a controller tuned for constants cannot follow it — which is a
statement about the *regulator's* bandwidth, not about the transform's validity.

## Where it stops holding

There is one component the transform genuinely does discard, and it is the one the wire
count removed. Add a neutral conductor, or a fault path to ground, and $i_a + i_b + i_c$
is no longer zero. The zero-sequence current $i_0 = \tfrac{1}{3}(i_a + i_b + i_c)$ then
exists, flows, and heats the windings, and it appears nowhere in $i_d$ or $i_q$: the
$\tfrac{2}{3}$ combination cancels it exactly, which the lab's third test checks by
adding 3.3 A to all three phases and demanding that $\alpha\beta$ not move. A two-axis
controller cannot see it and cannot regulate it. On a four-wire drive that is a third
loop somebody has to write.

The second boundary is the rotor angle itself. Every result above assumes the $\theta_e$
fed to Park is the machine's true angle. An estimator or a misaligned resolver that is
$5°$ out puts $8\sin 5° = 0.70$ A onto the $d$ axis without being asked, and leaves
$8\cos 5° = 7.97$ A on $q$. Note the asymmetry: the torque error is $1 - \cos 5°$, four
tenths of a per cent and second order in the error, while the unwanted $d$-axis current
is first order. At the 20 A rating a $10°$ error is 3.47 A of $i_d$ nobody commanded,
which changes the voltage the machine demands — the mechanism module 4 uses on purpose.
The gentle way torque degrades is why an alignment error survives commissioning; the
$d$-axis current is what eventually finds you at speed.

The third is that all of this is a static change of coordinates applied to a machine
whose inductances are held constant. Saturation makes $L_d$ and $L_q$ functions of the
currents, and a saturated machine has cross terms between the axes that no rotation
removes. Module 2 builds the model that this transform makes possible, and states its
own limits.

## What you are about to build

The sandbox *What the Park transform is rotating* puts the $\alpha\beta$ plane on screen
as a phase portrait: set both diagonal entries to zero and the trajectories close into
rings, which is a balanced set seen from the stator, and the Park transform is the change
of coordinates that stops them. The derive unit takes the $\tfrac{2}{3}$ collapse and the
length identity to their conclusions symbolically. And the lab *Clarke and Park from first
principles* asks for the four functions used throughout this reading, checked on exactly
the properties argued here: that a balanced set lands on a circle of the right radius,
that $i_\alpha$ equals $i_a$ to twelve decimal places, that a common offset on all three
phases is rejected, and that the rotation changes no lengths. Every later module calls
them.
''',
                },
            ],
            "title": "Clarke, Park and the rotating frame",
            "summary": "Three currents that sum to zero carry only two pieces of information. Rotate with the rotor and those two become constants.",
            "concepts": [
                "A wye-connected machine with no neutral obeys $i_a + i_b + i_c = 0$, so the three phase currents live on a plane, not in a volume.",
                "The Clarke transform names that plane: `αβ`, a stationary two-axis frame in which a balanced set traces a circle.",
                "Amplitude-invariant Clarke keeps peak values and makes power $\\tfrac{3}{2}(v_d i_d + v_q i_q)$; power-invariant Clarke keeps power and changes the peaks. Pick one and never mix them.",
                "The Park transform is a rotation by the electrical angle $\\theta_e$. It is orthogonal, so it changes neither the length of the current vector nor the instantaneous power.",
                "In the rotating frame a steady sinusoid becomes a constant — which is the whole reason a PI regulator with finite gain can drive its error to zero.",
            ],
            "sandbox": {
                "title": "What the Park transform is rotating",
                "visualiser": "phase-portrait",
                "minutes": 8,
                "initial": {"a11": -0.25, "a12": -1, "a21": 1, "a22": -0.25},
                "brief": r'''
Read the plane as `αβ`: $x_1$ is $i_\alpha$ and $x_2$ is $i_\beta$. The matrix
$A$ is the rule that moves the current vector, the arrows are that rule, and the
curves are eight vectors released from a ring and left to follow it.

The matrix opens at

$$A = \begin{bmatrix} -0.25 & -1 \\ 1 & -0.25 \end{bmatrix}$$

which is a rotation at one radian per second with a slow decay laid over it. The
Park transform is the change of coordinates that stops the rotation.
''',
                "notice": [
                    "Set $a_{11}$ and $a_{22}$ to zero. The readout says **centre** and the curves close into rings: constant magnitude, constant rate, which is exactly a balanced three-phase set seen in $\\alpha\\beta$. Drop the integrator slider to forward Euler and the rings open into spirals — a reminder that a fixed-step solver watching a lightly damped machine will report a magnitude drift that is entirely its own.",
                    "Swap the signs of the off-diagonal pair ($a_{12} = 1$, $a_{21} = -1$). Trace and determinant do not move, so the classification is unchanged, but the arrows now turn the other way. That is a negative-sequence set — the phase order reversed, which is what a drive sees when two motor leads are crossed.",
                    "With the diagonals still at zero, make the off-diagonals unequal: $a_{12} = -1$, $a_{21} = 2$. The rings become ellipses. In $\\alpha\\beta$ that is an unbalanced set, and after the Park rotation what should have been a dc quantity in $dq$ is instead a component pulsating at twice the electrical frequency.",
                ],
            },
            "derive": {
                "title": "Why the alpha axis is the a axis, and what a rotation preserves",
                "minutes": 14,
                "vars": ["i_a", "i_b", "i_c", "i_alpha", "i_beta", "i_d", "i_q", "I_s", "p", "v_d", "v_q"],
                "brief": r'''
The amplitude-invariant Clarke transform is

$$i_\alpha = \frac{2}{3}\left( i_a - \frac{1}{2} i_b - \frac{1}{2} i_c \right),
\qquad i_\beta = \frac{1}{\sqrt{3}}\left( i_b - i_c \right)$$

and Park is a plane rotation from $\alpha\beta$ to $dq$. The constants in Clarke
look arbitrary. They are not.
''',
                "steps": [
                    {
                        "prompt": "The machine is wye-connected with no neutral return, so $i_a + i_b + i_c = 0$. Write $i_b + i_c$ in terms of $i_a$.",
                        "answer": "-i_a",
                        "hint": "Move $i_a$ to the other side of the constraint. Nothing else is needed.",
                        "deconstruct": [
                            "The constraint is $i_a + i_b + i_c = 0$.",
                            "Subtract $i_a$ from both sides.",
                        ],
                    },
                    {
                        "prompt": "Substitute that into $i_\\alpha = \\frac{2}{3}\\left(i_a - \\frac{1}{2}i_b - \\frac{1}{2}i_c\\right)$ and simplify. Write $i_\\alpha$ in terms of $i_a$ alone.",
                        "given": "You may use $i_b + i_c = -i_a$ from the previous step.",
                        "answer": "i_a",
                        "hint": "The two halved terms are $-\\frac{1}{2}(i_b + i_c)$, which the constraint turns into $+\\frac{1}{2}i_a$.",
                        "deconstruct": [
                            "$i_a - \\frac{1}{2}(i_b + i_c) = i_a + \\frac{1}{2} i_a = \\frac{3}{2} i_a$.",
                            "Multiplying by $\\frac{2}{3}$ leaves $i_a$ exactly.",
                        ],
                    },
                    {
                        "prompt": "So the $\\alpha$ axis lies along phase $a$, and the $\\frac{2}{3}$ is what makes that true. Park is a rotation, so it preserves the length of the current vector: $i_d^2 + i_q^2 = i_\\alpha^2 + i_\\beta^2 = I_s^2$. Write $i_q$ in terms of $I_s$ and $i_d$, taking the positive root.",
                        "answer": "\\sqrt{I_s^{2} - i_d^{2}}",
                        "hint": "Rearrange the length identity for $i_q^2$ and take the square root.",
                        "deconstruct": [
                            "$i_q^2 = I_s^2 - i_d^2$.",
                            "The positive root is $\\sqrt{I_s^2 - i_d^2}$; the negative one is the same current running the other way.",
                        ],
                    },
                    {
                        "prompt": "With the amplitude-invariant convention the instantaneous power is $p = \\frac{3}{2}\\left(v_d i_d + v_q i_q\\right)$. A surface machine is run with $i_d = 0$. Write the $i_q$ that delivers a demanded power $p$ at a terminal voltage $v_q$.",
                        "answer": "\\frac{2 p}{3 v_q}",
                        "hint": "Drop the $v_d i_d$ term, then solve the remaining single equation for $i_q$.",
                        "deconstruct": [
                            "With $i_d = 0$ the power is $p = \\frac{3}{2} v_q i_q$.",
                            "Divide both sides by $\\frac{3}{2} v_q$.",
                        ],
                    },
                ],
                "closing": r'''
The $\frac{3}{2}$ in the power expression is the price of the amplitude-invariant
convention: the transform is not orthogonal, so power is not conserved across it and
the factor has to be carried by hand. The power-invariant version scales by
$\sqrt{2/3}$ instead and makes the factor disappear — at the cost of $i_\alpha$ no
longer equalling $i_a$. Every drive firmware picks one. Mixing them silently scales
every torque estimate by $\sqrt{3/2}$.
''',
            },
            "quiz": {
                "title": "Three numbers that are really two",
                "minutes": 7,
                "questions": [
                    {
                        "q": "In a wye machine with no neutral connection, $i_a + i_b + i_c = 0$. How many independent quantities do the three currents carry?",
                        "opts": ["Two", "Three", "One", "Three, but only two are measurable"],
                        "a": 0,
                        "why": r"""
The constraint removes one degree of freedom, so the three phase currents live in a
two-dimensional plane. Everything that follows is a consequence: two sensors are enough
(the third current is the negative sum of the other two), the Clarke transform is a
change of basis in that plane rather than a projection that loses something, and a
two-axis controller is not an approximation.
""",
                    },
                    {
                        "q": "What does the Clarke transform produce?",
                        "opts": [
                            "A stationary two-axis frame in which a balanced set becomes a rotating vector",
                            "A rotating frame in which balanced quantities are constant",
                            "The DC component of each phase",
                            "The magnitude of the current, with the phase discarded",
                        ],
                        "a": 0,
                        "why": r"""
Clarke names the plane: $\alpha\beta$, still stationary with respect to the stator, in
which a balanced three-phase set traces a circle at electrical speed. It is only half the
job. Park then rotates *with* that circle so it stops moving — and it is the stopping
that a PI controller needs, which is the next question.
""",
                    },
                    {
                        "q": "Why rotate into the dq frame at all?",
                        "opts": [
                            "A PI controller has zero steady-state error only on a constant, and dq makes the currents constant",
                            "It reduces the number of sensors needed",
                            "It removes the need for a model of the machine",
                            "It eliminates the switching harmonics",
                        ],
                        "a": 0,
                        "why": r"""
An integrator drives the error to zero for a step and not for a sinusoid — chase a
50 Hz current with a PI and you will always be behind it, by a phase and an amplitude
that both grow with speed. Rotating with the rotor turns the target into DC, and then the
integrator does what integrators are good at. Everything else about field-oriented
control follows from wanting that one property.
""",
                    },
                    {
                        "q": "With the amplitude-invariant Clarke transform, what is the power?",
                        "opts": [
                            "$\\tfrac{3}{2}(v_di_d + v_qi_q)$",
                            "$v_di_d + v_qi_q$",
                            "$\\tfrac{2}{3}(v_di_d + v_qi_q)$",
                            "$3(v_di_d + v_qi_q)$",
                        ],
                        "a": 0,
                        "why": r"""
The amplitude-invariant scaling keeps peak values recognisable — a 10 A peak phase
current reads as 10 in dq, which is what you want on a scope — and pays for it with a
factor of 3/2 in every power and torque expression. The power-invariant scaling with
$\sqrt{2/3}$ makes the 3/2 disappear and makes the amplitudes unfamiliar. Neither is
wrong; mixing them is, and it produces a torque constant that is off by exactly 3/2.
""",
                    },
                    {
                        "q": "Two current sensors have failed on a three-phase drive, leaving one. What can you still do?",
                        "opts": [
                            "Not enough — two independent measurements are needed to fix the vector",
                            "Everything, since the currents sum to zero",
                            "Everything, provided the machine is balanced",
                            "Nothing at all",
                        ],
                        "a": 0,
                        "why": r"""
The plane is two-dimensional and one measurement fixes only one coordinate. The
zero-sum constraint is what lets you get away with *two* sensors instead of three; it
cannot get you down to one. There are single-sensor schemes in real drives, and they work
by reconstructing the currents from the DC-link current at specific instants of the
switching period — extra information in time, not extra information from the constraint.
""",
                    },
                ],
            },
            "lab": {
                "title": "Clarke and Park from first principles",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Write the two transforms and the inverse rotation.

`clarke(i_a, i_b, i_c)` returns `(i_alpha, i_beta)` in the **amplitude-invariant**
convention:

```text
i_alpha = (2/3) * (i_a - i_b/2 - i_c/2)
i_beta  = (i_b - i_c) / sqrt(3)
```

`park(i_alpha, i_beta, theta)` rotates into the frame at angle `theta`:

```text
i_d =  i_alpha*cos(theta) + i_beta*sin(theta)
i_q = -i_alpha*sin(theta) + i_beta*cos(theta)
```

`inv_park(i_d, i_q, theta)` rotates back out again. `abc_to_dq` is already written
in terms of the other three; leave it alone.

The checks look at three things you should expect: that a balanced set lands on a
circle of the right radius, that a common offset added to all three phases vanishes,
and that the rotation changes neither length nor information.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def clarke(i_a, i_b, i_c):
    """Amplitude-invariant Clarke. Return (i_alpha, i_beta)."""
    # TODO: alpha is the two-thirds combination, beta the difference over root three.
    return 0.0, 0.0


def park(i_alpha, i_beta, theta):
    """Rotate into the frame at electrical angle theta. Return (i_d, i_q)."""
    # TODO: a plane rotation by -theta applied to the vector (i_alpha, i_beta).
    return 0.0, 0.0


def inv_park(i_d, i_q, theta):
    """Rotate back out to the stationary frame. Return (i_alpha, i_beta)."""
    # TODO: the transpose of the matrix you just used.
    return 0.0, 0.0


def abc_to_dq(i_a, i_b, i_c, theta):
    """Clarke then Park. Already written for you."""
    i_alpha, i_beta = clarke(i_a, i_b, i_c)
    return park(i_alpha, i_beta, theta)


if __name__ == "__main__":
    th = 0.9
    amp = 7.5
    i_a = amp * np.cos(th)
    i_b = amp * np.cos(th - 2.0 * np.pi / 3.0)
    i_c = amp * np.cos(th + 2.0 * np.pi / 3.0)
    print("alpha, beta:", [round(v, 6) for v in clarke(i_a, i_b, i_c)])
    print("d, q:", [round(v, 6) for v in abc_to_dq(i_a, i_b, i_c, th)])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def clarke(i_a, i_b, i_c):
    """Amplitude-invariant Clarke. Return (i_alpha, i_beta)."""
    i_alpha = (2.0 / 3.0) * (i_a - 0.5 * i_b - 0.5 * i_c)
    i_beta = (i_b - i_c) / np.sqrt(3.0)
    return float(i_alpha), float(i_beta)


def park(i_alpha, i_beta, theta):
    """Rotate into the frame at electrical angle theta. Return (i_d, i_q)."""
    c = np.cos(theta)
    s = np.sin(theta)
    return float(i_alpha * c + i_beta * s), float(-i_alpha * s + i_beta * c)


def inv_park(i_d, i_q, theta):
    """Rotate back out to the stationary frame. Return (i_alpha, i_beta)."""
    c = np.cos(theta)
    s = np.sin(theta)
    return float(i_d * c - i_q * s), float(i_d * s + i_q * c)


def abc_to_dq(i_a, i_b, i_c, theta):
    """Clarke then Park. Already written for you."""
    i_alpha, i_beta = clarke(i_a, i_b, i_c)
    return park(i_alpha, i_beta, theta)


if __name__ == "__main__":
    th = 0.9
    amp = 7.5
    i_a = amp * np.cos(th)
    i_b = amp * np.cos(th - 2.0 * np.pi / 3.0)
    i_c = amp * np.cos(th + 2.0 * np.pi / 3.0)
    print("alpha, beta:", [round(v, 6) for v in clarke(i_a, i_b, i_c)])
    print("d, q:", [round(v, 6) for v in abc_to_dq(i_a, i_b, i_c, th)])
'''}],
                "hints": [
                    "`i_beta` needs no factor of two-thirds once you divide by $\\sqrt{3}$: $\\frac{2}{3}\\cdot\\frac{\\sqrt{3}}{2} = \\frac{1}{\\sqrt{3}}$.",
                    "Park rotates the *frame* forward by `theta`, which rotates the *vector* backward — that is why the sine in the `i_q` row carries the minus sign.",
                    "`inv_park` is `park` with `-theta`, and also `park` with the two sines negated. Either is fine.",
                ],
                "tests": [
                    {"name": "a balanced set lands on a circle of the right radius", "code": r'''
import numpy as np
_th, _amp = 0.9, 7.5
_a = _amp * np.cos(_th)
_b = _amp * np.cos(_th - 2.0 * np.pi / 3.0)
_c = _amp * np.cos(_th + 2.0 * np.pi / 3.0)
_al, _be = clarke(_a, _b, _c)
assert abs(np.hypot(_al, _be) - _amp) < 1e-9, \
    f"amplitude-invariant Clarke should keep the peak {_amp}, got |i| = {np.hypot(_al, _be)}"
assert abs(_al - _amp * np.cos(_th)) < 1e-9, \
    f"i_alpha should be {_amp * np.cos(_th)}, got {_al} — check the 2/3 factor"
assert abs(_be - _amp * np.sin(_th)) < 1e-9, \
    f"i_beta should be {_amp * np.sin(_th)}, got {_be} — check the 1/sqrt(3) factor"
'''},
                    {"name": "the alpha axis lies along phase a", "code": r'''
import numpy as np
_al, _be = clarke(3.0, -1.0, -2.0)
assert abs(_al - 3.0) < 1e-12, \
    f"for a set summing to zero, i_alpha equals i_a exactly; expected 3.0, got {_al}"
assert abs(_be - 1.0 / np.sqrt(3.0)) < 1e-12, \
    f"i_beta should be (i_b - i_c)/sqrt(3) = {1.0 / np.sqrt(3.0)}, got {_be}"
'''},
                    {"name": "a common offset on all three phases is rejected", "code": r'''
import numpy as np
_al, _be = clarke(3.0, -1.0, -2.0)
_al2, _be2 = clarke(3.0 + 3.3, -1.0 + 3.3, -2.0 + 3.3)
assert abs(_al2 - _al) < 1e-12 and abs(_be2 - _be) < 1e-12, \
    "zero sequence must not reach alpha-beta; the 2/3 combination is what cancels it"
assert abs(_al) > 1e-9, "and the transform must still produce a non-zero result"
'''},
                    {"name": "Park at the electrical angle puts the whole current on d", "code": r'''
import numpy as np
_th, _amp = 0.9, 7.5
_a = _amp * np.cos(_th)
_b = _amp * np.cos(_th - 2.0 * np.pi / 3.0)
_c = _amp * np.cos(_th + 2.0 * np.pi / 3.0)
_d, _q = abc_to_dq(_a, _b, _c, _th)
assert abs(_d - _amp) < 1e-9, f"aligned with the vector, i_d should be {_amp}, got {_d}"
assert abs(_q) < 1e-9, f"and i_q should be zero, got {_q} — check the sign of the sine terms"
'''},
                    {"name": "the rotation changes no lengths", "code": r'''
import numpy as np
for _th in (0.0, 0.4, 1.7, -2.2, 5.9):
    _d, _q = park(2.5, -1.25, _th)
    assert abs(np.hypot(_d, _q) - np.hypot(2.5, -1.25)) < 1e-12, \
        f"a rotation is orthogonal: |i| must stay {np.hypot(2.5, -1.25)}, got {np.hypot(_d, _q)} at theta={_th}"
'''},
                    {"name": "inv_park undoes park", "code": r'''
import numpy as np
for _th in (0.0, 0.4, 1.7, -2.2, 5.9):
    _d, _q = park(2.5, -1.25, _th)
    _al, _be = inv_park(_d, _q, _th)
    assert abs(_al - 2.5) < 1e-12 and abs(_be + 1.25) < 1e-12, \
        f"round trip at theta={_th} should return (2.5, -1.25), got ({_al}, {_be})"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "read": [
                {
                    "title": "Thirty-five volts on an axis carrying no current",
                    "minutes": 16,
                    "body": r'''
Leave the machine of module 1 where it was — 800 electrical rad/s, $i_d = 0$, $i_q = 8$ A,
4.08 N·m — and stop looking at what the drive measures. Look at what it *outputs*. The two
voltage commands leaving the current regulator are

```text
v_d = -35.20 V
v_q = +71.60 V
```

The $q$-axis number is unsurprising: the machine is turning, it has a magnet in it, and
something has to overcome the back-EMF. The $d$-axis number is the interesting one. There
is no $d$-axis current, none is commanded, the $d$-axis resistive drop is $0.45 \times 0 =
0$ V, and the inverter is nonetheless being asked to hold 35 volts on that axis — a fifth
of the entire 173.2 V budget the modulator can synthesise. It cannot be dropped, because
dropping it puts current on $d$ that nobody wanted.

## Where the thirty-five volts comes from

The stator equation in the stationary frame has no mystery in it: $v = Ri + \dot\lambda$,
one loop equation per phase. Write the flux linkage as a plane vector, and write the
rotating-frame version $\lambda_{dq}$ of it, so that $\lambda_{s} = e^{j\theta_e}\lambda_{dq}$.
Differentiating a product does the rest:

$$\dot\lambda_{s} = e^{j\theta_e}\left(\dot\lambda_{dq} + j\omega_e\lambda_{dq}\right)$$

Rotate the whole equation back by $e^{-j\theta_e}$ and the exponential disappears, leaving

$$v_{dq} = R\,i_{dq} + \dot\lambda_{dq} + j\omega_e\lambda_{dq}$$

The last term is what a fixed vector in a turning frame looks like from outside it. It is
the same term that produces Coriolis and centrifugal accelerations in mechanics, and it
appears here for the identical reason: the coordinates move. Splitting
$j\omega_e(\lambda_d + j\lambda_q)$ into $-\omega_e\lambda_q$ on the real axis and
$+\omega_e\lambda_d$ on the imaginary one gives the two equations the blanks unit *The dq
model, and where the speed terms come from* asks you to fill in:

$$v_d = R\,i_d + \dot\lambda_d - \omega_e\lambda_q, \qquad
  v_q = R\,i_q + \dot\lambda_q + \omega_e\lambda_d$$

Now put the machine's own flux linkages in. The $d$ axis is *defined* as the direction the
magnet points, so $\lambda_d = L_d i_d + \lambda_m$ and $\lambda_q = L_q i_q$ with no magnet
term. At the operating point on the screen, $\lambda_q = 0.0055 \times 8 = 44.0$ mWb, and

$$-\omega_e\lambda_q = -800 \times 0.0440 = -35.20\ \text{V}$$

which is the number the drive is producing. It is the $q$-axis flux being carried past the
$d$ axis by the frame's own rotation, and it has nothing to do with $i_d$.

## Those terms are not losses, and here is the receipt

The most consequential thing about the two $\omega_e$ terms is what they are *not*. Take
the instantaneous power $p = \tfrac{3}{2}(v_di_d + v_qi_q)$ and feed it only the speed
terms:

$$\tfrac{3}{2}\left(i_d\left(-\omega_e L_q i_q\right) + i_q\,\omega_e\left(L_d i_d + \lambda_m\right)\right)
= \tfrac{3}{2}\,\omega_e\left(\lambda_m i_q + (L_d - L_q)i_d i_q\right) = \frac{\omega_e T_e}{P_p}$$

The $L_d i_d i_q$ and $-L_q i_d i_q$ pieces do not cancel unless the machine is
non-salient; what survives is the torque equation multiplied by mechanical speed. The
speed terms *are* the airgap power. Splitting the operating point four ways makes it
concrete:

```python
R, LD, LQ, LAM, PP = 0.45, 0.0035, 0.0055, 0.085, 4
w_e, i_d, i_q = 800.0, 0.0, 8.0

v_d = R * i_d - w_e * LQ * i_q
v_q = R * i_q + w_e * (LD * i_d + LAM)
print("v_d %+.2f V  (resistive %+.2f, speed %+.2f)" % (v_d, R * i_d, -w_e * LQ * i_q))
print("v_q %+.2f V  (resistive %+.2f, speed %+.2f)" % (v_q, R * i_q, w_e * (LD * i_d + LAM)))

p_in = 1.5 * (v_d * i_d + v_q * i_q)
p_cu = 1.5 * R * (i_d ** 2 + i_q ** 2)
p_w = 1.5 * (i_d * (-w_e * LQ * i_q) + i_q * w_e * (LD * i_d + LAM))
T_e = 1.5 * PP * (LAM * i_q + (LD - LQ) * i_d * i_q)
print("electrical in %.1f W = copper %.1f W + speed terms %.1f W" % (p_in, p_cu, p_w))
print("and the speed terms equal T_e * w_mech = %.2f Nm * %.1f rad/s = %.1f W"
      % (T_e, w_e / PP, T_e * w_e / PP))
```

Of the 71.6 V on the $q$ axis, 3.6 V is resistance and 68.0 V is back-EMF. The 3.6 V
carries the 43.2 W of copper loss counted in module 1, and the 68.0 V carries all 816 W of
shaft power. Every watt is accounted for, and the $\omega_e$ terms hold the useful ones.
This is why cancelling them with a feedforward in module 3 is not cheating and costs
nothing: you are not deleting the power, you are relieving the *regulator* of having to
discover it.

## The plant the regulator actually faces

Solve both equations for the derivatives and the machine becomes
$\dot{x} = Ax + Bv + d$ with $x = [i_d,\ i_q]^\top$, which is what the lab *Build the dq
plant and its torque* asks you to return:

$$A = \begin{bmatrix} -R/L_d & \omega_e L_q/L_d \\ -\omega_e L_d/L_q & -R/L_q \end{bmatrix},
\qquad d = \begin{bmatrix} 0 \\ -\omega_e\lambda_m/L_q \end{bmatrix}$$

At standstill $A$ is diagonal and the machine is two independent lags of $L_d/R = 7.78$ ms
and $L_q/R = 12.22$ ms. Put 800 rad/s into it and the picture changes completely:

```python
import math

R, LD, LQ = 0.45, 0.0035, 0.0055

for w_e in (0.0, 800.0):
    a11, a12, a21, a22 = -R / LD, w_e * LQ / LD, -w_e * LD / LQ, -R / LQ
    tr, det = a11 + a22, a11 * a22 - a12 * a21
    disc = tr * tr - 4.0 * det
    print("w_e %5.0f rad/s   A = [[%.1f, %.1f], [%.1f, %.1f]]" % (w_e, a11, a12, a21, a22))
    if disc >= 0.0:
        r1, r2 = 0.5 * (tr + math.sqrt(disc)), 0.5 * (tr - math.sqrt(disc))
        print("    real poles %.2f and %.2f 1/s -> %.2f ms and %.2f ms"
              % (r1, r2, -1e3 / r1, -1e3 / r2))
    else:
        sig, wd = 0.5 * tr, 0.5 * math.sqrt(-disc)
        print("    poles %.2f +/- j%.2f -> rings at %.2f Hz, decays with tau = %.2f ms,"
              " %.2f cycles to 1%%"
              % (sig, wd, wd / (2.0 * math.pi), -1e3 / sig, (wd / (2.0 * math.pi)) * math.log(100.0) / -sig))
```

The off-diagonal entries at 800 rad/s are $+1257$ and $-509$, against a diagonal of $-129$
and $-82$: the coupling beats the damping by a factor of nearly ten. Short the machine's
terminals, disturb the current, and it does not decay along two axes — it spirals, ringing
at 127.27 Hz, within a twentieth of a hertz of the electrical frequency itself, and taking
5.57 cycles to fall below one per cent. That is not a coincidence. The product of the two
cross terms is $-(\omega_e L_q/L_d)(\omega_e L_d/L_q) = -\omega_e^2$ exactly, whatever the
inductances are, so the ring frequency is the rotor speed and the inductances cancel out of
it. The sandbox *The machine with the controller switched off* is that spiral: take both
off-diagonal entries to zero and it straightens into the two lags, put the speed back and
it winds up again.

## Torque, and the term with the awkward sign

The same co-energy argument that produces the flux linkages produces

$$T_e = \tfrac{3}{2}P_p\left(\lambda_m i_q + (L_d - L_q)i_d i_q\right)$$

On this rotor $L_d - L_q = -2.0$ mH, negative, because burying the magnets puts iron in the
$q$ path and air in the $d$ path.

```python
R, LD, LQ, LAM, PP = 0.45, 0.0035, 0.0055, 0.085, 4

def torque(i_d, i_q, lam=LAM):
    return 1.5 * PP * (lam * i_q + (LD - LQ) * i_d * i_q)

base = torque(0.0, 12.0)
for i_d in (0.0, -5.0, 5.0):
    print("i_d %+5.1f A at i_q = 12 A -> %.2f Nm  (%+.1f%% on the magnet term alone)"
          % (i_d, torque(i_d, 12.0), 100.0 * (torque(i_d, 12.0) / base - 1.0)))
hot = LAM * (1.0 - 0.0011 * 75.0)
print("magnets 75 K hotter: lambda_m %.5f Wb, and 8 A of i_q makes %.3f Nm, not %.3f"
      % (hot, torque(0.0, 8.0, hot), torque(0.0, 8.0)))
```

Five amps of *negative* $d$-axis current lifts 6.12 N·m to 6.84 N·m, an 11.8 per cent gain
for current that produces no magnet torque at all; five amps positive drops it to 5.40 N·m.
Those three numbers are the lab's own assertions, and they are the whole content of maximum
torque per amp.

## The mistake, and why it is tempting

The mistake is the sign of that term, and it is made by people who understand reluctance
torque perfectly well. The reasoning goes: the rotor is pulled towards alignment with the
low-reluctance path, the low-reluctance path is the one with the larger inductance, that is
$q$ on an interior machine, therefore the saliency term should be positive and should read
$(L_q - L_d)i_di_q$. Every clause of that is true except the conclusion. The pull is real;
what the co-energy derivative gives is a coefficient of $(L_d - L_q)$, and the term is made
positive by making $i_d$ negative rather than by flipping the bracket.

It is tempting because the flipped version is *dimensionally* right, gives a positive number
for positive currents, and agrees with the verbal story. It is also self-reinforcing: an
engineer who has flipped the bracket commands positive $i_d$ for extra torque, measures less
torque, and concludes the reluctance contribution is small. The lab settles it in one line —
`_neg` must be 6.84 N·m and `_pos` 5.40 N·m — and the two are not interchangeable.

The second mistake costs less and happens more: coding one inductance for both axes. With
$L_d$ used on both, module 3's rule $K_p = \alpha L$ gives 7.0 on the $q$ axis where it
needs 11.0, and the achieved $q$-axis bandwidth is $7.0/0.0055 = 1273$ rad/s instead of
2000 — 36 per cent slow, on a loop whose whole design consists of choosing that one number.
Nothing fails; the drive is merely worse than its specification says, in a way no step
response will name.

## Where the model stops holding

Four parameters is remarkably few, and the price is visible on any real dynamometer.

**Saturation.** $L_d$ and $L_q$ are drawn here as constants. On an interior machine the $q$
path runs through iron and saturates first: an inductance of 5.5 mH at 8 A can be 4 mH near
the 20 A rating. Every consequence in this course moves with it — the feedforward
under-cancels, module 3's pole–zero cancellation misses, and the MTPA angle shifts. Serious
drives carry $L_d$ and $L_q$ as lookup tables in $i_d$ and $i_q$.

**Cross-saturation.** Worse than that, $\lambda_d$ depends on $i_q$ as well, through shared
iron. That is a mutual term $L_{dq}$ with no slot in these equations at all, and it is why a
machine identified on the $d$ axis alone gives parameters that do not predict the $q$ axis.

**Temperature.** $\lambda_m$ is not a constant either. Neodymium magnets lose roughly
0.11 per cent of remanence per kelvin, so a 75 K rise takes 85 mWb to 78.0 mWb. The last
line of the torque block above is the consequence: the same 8 A that made 4.08 N·m cold
makes 3.74 N·m hot, and a drive estimating torque from current is 9 per cent optimistic and
has no way to know.

**Loss that is not $I^2R$.** There is no iron loss anywhere in this model. Hysteresis and
eddy currents would need a resistance in parallel with the magnetising branch, and their
absence is why the model predicts a machine that costs nothing to spin at speed with no
current in it, which no machine does.

**Space and time harmonics.** The transform of module 1 assumed a sinusoidally distributed
winding. A real one has slots, so the airgap flux carries spatial harmonics that show up as
cogging and as a sixth-harmonic torque ripple in the rotating frame — invisible to a model
whose only angular dependence was removed by Park. And the inverter here is an ideal voltage
source: nothing switches, nothing has dead time, and the 10 kHz carrier does not exist.
Module 4 puts it back.

## What you are about to build

The derive unit *From the voltage equation to the state matrix and the torque* takes the
$d$-axis equation to the entry $\omega_e L_q/L_d$ of $A$ and then inverts the surface-machine
torque law, which is the calculation every torque command in a drive performs. The blanks
unit fills in the four equations above and closes on the one question that matters about the
speed terms. And the lab checks the plant entry by entry on this machine at 800 rad/s —
including that the two coupling terms have opposite signs, and that the steady state it
returns really is one.
''',
                },
            ],
            "quiz": {
                "title": "Two lags, and the terms that are not losses",
                "minutes": 8,
                "questions": [
                    {
                        "q": "At 800 electrical rad/s with $i_d$ held at zero and 8 A on $q$, the regulator outputs $v_d = -35.2$ V. What is that voltage doing?",
                        "opts": [
                            "Supplying the copper loss of the $d$-axis winding, which is what a resistive drop always is",
                            "Carrying the $q$-axis flux past the $d$ axis; it delivers no power, since $v_di_d$ is zero",
                            "Driving the $d$-axis current, which is what gives the $d$-axis regulator something to do",
                            "Opposing the magnet's flux, which is the mechanism the field-weakening command uses at speed",
                        ],
                        "a": 1,
                        "whys": [
                            r"There is no $d$-axis current, so there is no $d$-axis copper loss: $Ri_d = 0.45 \times 0 = 0$ V. A resistive drop needs a current, and this voltage is present precisely where none is flowing.",
                            r"$\lambda_q = L_qi_q = 44$ mWb, and $-\omega_e\lambda_q = -800 \times 0.044$ is the whole of it.",
                            r"It is the other way round. The regulator produces this voltage so that $i_d$ stays at zero — remove it and current appears on $d$, which is the disturbance the feedforward exists to pre-empt.",
                            r"Field weakening does oppose the magnet, but it does so with negative $i_d$ on the $\omega_eL_di_d$ term of the *q*-axis equation. This voltage is on $d$, is proportional to $i_q$, and is present at every speed above zero.",
                        ],
                        "why": r'''
The term is $-\omega_e\lambda_q = -\omega_eL_qi_q = -800 \times 0.0055 \times 8 = -35.2$ V:
the $q$-axis flux linkage being swept past the $d$ axis by the frame's own rotation. It is
proportional to the *other* axis's current, which is why it is present with $i_d$ at zero,
and why it delivers no power at this operating point — $v_di_d$ is zero however large $v_d$
is. It still costs a fifth of the modulator's 173.2 V budget, which is the practical reason
the feedforward computes it rather than leaving the regulator to find it.
''',
                    },
                    {
                        "q": "This rotor has $L_q > L_d$, so the bracket $(L_d - L_q)$ is negative. Which sign of $i_d$ raises the torque at a fixed $i_q$?",
                        "opts": [
                            "Positive, since reluctance torque pulls the rotor towards its high-inductance axis",
                            "Neither, because holding $i_q$ fixed holds the whole reluctance term fixed with it",
                            "Negative, since a negative $i_d$ against a negative bracket makes the product positive",
                            "Whichever is larger in magnitude, as the reluctance term goes with the square of $i_d$",
                        ],
                        "a": 2,
                        "whys": [
                            r"The pull towards the high-inductance axis is real, and it is what produces the term at all. What it does not do is set the sign of the coefficient: the co-energy derivative gives $(L_d - L_q)$, and positive $i_d$ against it takes 6.12 N·m down to 5.40.",
                            r"The term is the product $i_di_q$, so fixing one factor leaves the other free — which is the entire point of an MTPA command.",
                            r"$(-0.002)(-5)(12) = +0.12$, which is $0.72$ N·m on top of the magnet term's $6.12$.",
                            r"The term is linear in $i_d$, not quadratic, so its sign follows the sign of $i_d$ exactly. A quadratic term could not change sign at all, and reversing $i_d$ would then have no effect.",
                        ],
                        "why": r'''
At $i_q = 12$ A the magnet term alone gives 6.12 N·m. Adding $i_d = -5$ A makes the
reluctance product $(L_d - L_q)i_di_q = (-0.002)(-5)(12) = +0.12$, worth another 0.72 N·m
and taking the total to 6.84 N·m; $i_d = +5$ A subtracts the same amount and gives 5.40 N·m.
Both signs sound defensible in words, and only the arithmetic separates them — which is why
the lab asserts all three numbers rather than the shape of the formula.
''',
                    },
                    {
                        "q": "Multiply each speed term by its own current and sum: $\\tfrac{3}{2}\\left(i_d(-\\omega_eL_qi_q) + i_q\\omega_e(L_di_d + \\lambda_m)\\right)$. What is it?",
                        "opts": [
                            "Zero, because a rotation returns over each cycle whatever energy it stores",
                            "The airgap power $\\omega_eT_e/P_p$ — the entire mechanical output of the machine",
                            "The reactive power the inverter circulates through the dc-link capacitor",
                            "The speed-dependent part of the loss, which is the reason efficiency falls with speed",
                        ],
                        "a": 1,
                        "whys": [
                            r"The two terms cancel only when $L_d = L_q$ *and* the magnet term is set aside — and the magnet term never is. What survives is $\tfrac{3}{2}\omega_e(\lambda_mi_q + (L_d-L_q)i_di_q)$, which is 816 W at this operating point rather than zero.",
                            r"$\tfrac{3}{2}\omega_e(\lambda_mi_q + (L_d-L_q)i_di_q)$ is the torque equation multiplied by mechanical speed.",
                            r"Nothing here is reactive: the sum is real power crossing the airgap and leaving through the shaft. The dc-link capacitor handles the switching-frequency ripple, three decades above the electrical frequency.",
                            r"They dissipate nothing. The dissipation is $\tfrac{3}{2}R(i_d^2+i_q^2) = 43.2$ W and carries no $\omega_e$ at all; efficiency does fall with speed on a real machine, but through iron loss, which is absent from this model.",
                        ],
                        "why": r'''
Working the algebra through, the sum is $\tfrac{3}{2}\omega_e\left(\lambda_mi_q +
(L_d-L_q)i_di_q\right)$, which is $\omega_eT_e/P_p$ — torque times mechanical speed. At 800
rad/s and 8 A that is 816 W, and it is the whole shaft output. Reading these terms as loss
is the most consequential error available in this module, because it makes cancelling them
with a feedforward look like cheating. It is not: the power still flows, and what the
feedforward removes is the regulator's need to rediscover it from the error signal.
''',
                    },
                    {
                        "q": "Short the terminals of this machine while it turns at 800 rad/s, disturb the current, and it rings at 127.3 Hz. What sets that frequency?",
                        "opts": [
                            "The winding inductance resonating against the machine's own stray capacitance",
                            "The electrical time constants $L_d/R$ and $L_q/R$, at 7.78 ms and 12.22 ms",
                            "The two cross terms of $A$, whose product is $-\\omega_e^2$ whatever the inductances are",
                            "The 10 kHz carrier, which beats against the fundamental to leave a 127 Hz difference tone",
                        ],
                        "a": 2,
                        "whys": [
                            r"Stray capacitance in a machine resonates in the hundreds of kilohertz to megahertz, and it appears nowhere in a model built from $R$, $L$ and $\lambda_m$. The ringing here is between the two axes, not between $L$ and $C$.",
                            r"Those set the *decay*, not the frequency: the trace falls with a 9.51 ms envelope, which is the average of the two diagonal rates. Read on their own they predict two non-oscillating lags, which is exactly what the machine does at standstill.",
                            r"$-(\omega_eL_q/L_d)(\omega_eL_d/L_q) = -\omega_e^2$, so the ring frequency is the rotor speed.",
                            r"The terminals are shorted, so there is no modulator running at all. The ring is a property of the machine, and it would be there with the inverter disconnected.",
                        ],
                        "why": r'''
The cross terms are $+\omega_eL_q/L_d$ and $-\omega_eL_d/L_q$, and their product is
$-\omega_e^2$ exactly — the inductances cancel. The imaginary part of the eigenvalues is
therefore $\omega_e$ to within the small correction the diagonal makes, which is why 800
rad/s rings at 127.27 Hz against an electrical frequency of 127.32 Hz. The diagonal sets
the envelope instead: poles at $-105.2 \pm j799.7$, a 9.51 ms decay, and 5.57 cycles before
the disturbance is under one per cent. Speed decides how fast the currents turn; resistance
decides how fast they die.
''',
                    },
                    {
                        "q": "A drive is commissioned cold and reports 4.08 N·m at 8 A of $i_q$. An hour later the rotor magnets are 75 K hotter and the current is unchanged. What happens?",
                        "opts": [
                            "The report rises, because a hotter winding has more resistance and more loss",
                            "The report stays exact, since $\\lambda_m$ is a magnet property and not a thermal one",
                            "The report falls with the real torque, since it is computed from the measured current",
                            "The report still holds at 4.08 N·m while the real torque falls to about 3.74 N·m",
                        ],
                        "a": 3,
                        "whys": [
                            r"Winding resistance does rise with temperature, by about 30 per cent over 75 K, and it changes the *voltage* the regulator needs. It has no place in $T_e = \tfrac{3}{2}P_p\lambda_mi_q$, which contains no resistance at all.",
                            r"Remanence falls with temperature in every permanent-magnet material — roughly 0.11 per cent per kelvin for neodymium, and reversibly, so the machine recovers when it cools. It is one of the reasons a traction drive measures rotor temperature.",
                            r"The estimate is computed from measured current, which is exactly why it does not fall: the current is unchanged. What changed is the constant multiplying it, and the drive has no sensor for that.",
                            r"$0.085 \times (1 - 0.0011 \times 75) = 0.0780$ Wb, and $\tfrac{3}{2} \times 4 \times 0.0780 \times 8 = 3.74$ N·m.",
                        ],
                        "why": r'''
A drive estimating torque from current uses the $\lambda_m$ it was commissioned with. The
current has not moved, so neither does the estimate — but $\lambda_m$ has fallen from
85 mWb to 78.0 mWb, so the shaft is delivering 3.74 N·m against a reported 4.08, an error
of 9 per cent in the optimistic direction. Nothing in the model can detect this, which is
why machines that must hold a torque accuracy carry a rotor temperature estimate and a
$\lambda_m$ correction, and why the effect is reversible: cool the magnets and the torque
comes back.
''',
                    },
                    {
                        "q": "This model holds $R$, $L_d$, $L_q$ and $\\lambda_m$, and nothing else. Which measured behaviour can it not reproduce?",
                        "opts": [
                            "A cross-coupling between the two axes that grows in proportion to the rotor speed",
                            "A back-EMF whose amplitude grows in proportion to the speed of the rotor",
                            "A no-load loss that grows with speed while both currents are held at zero",
                            "A torque that reverses the instant the $q$-axis current is commanded negative",
                        ],
                        "a": 2,
                        "whys": [
                            r"The model produces this directly: the off-diagonal entries of $A$ are both proportional to $\omega_e$, and they are the reason the shorted machine spirals rather than decaying along two axes.",
                            r"$\omega_e\lambda_m$ is in the $q$-axis equation and is 68 V at 800 rad/s. It is the term that eventually exhausts the bus and forces field weakening in module 4.",
                            r"With both currents at zero there is no $I^2R$, and $I^2R$ is the only loss mechanism these four parameters can express.",
                            r"$T_e = \tfrac{3}{2}P_p\lambda_mi_q$ is linear and odd in $i_q$, so it reverses exactly. The lab asserts that: $+12$ A and $-12$ A must give torques summing to zero to twelve decimal places.",
                        ],
                        "why": r'''
Spin an unexcited machine and it takes real power — hysteresis and eddy currents in the
stator iron, growing faster than linearly with speed. This model has one dissipative
element, $R$, and $R$ dissipates $\tfrac{3}{2}R(i_d^2+i_q^2)$, which is zero when the
currents are. Representing iron loss needs a resistance in parallel with the magnetising
branch, which is a fifth parameter and a different circuit. The gap matters most exactly
where module 4 operates: at high speed with weak current, where the model's predicted loss
approaches zero and the machine's does not.
''',
                    },
                ],
            },
            "title": "The dq model of a PMSM",
            "summary": "Two first-order lags, a cross-coupling term that grows with speed, and a back-EMF that behaves like a disturbance.",
            "concepts": [
                "Flux linkages: $\\lambda_d = L_d i_d + \\lambda_m$ and $\\lambda_q = L_q i_q$. The magnet contributes to $d$ only, by definition of the $d$ axis.",
                "Voltage equations: $v_d = R i_d + L_d \\dot{i_d} - \\omega_e L_q i_q$ and $v_q = R i_q + L_q \\dot{i_q} + \\omega_e (L_d i_d + \\lambda_m)$.",
                "The two $\\omega_e$ terms come from differentiating a vector in a rotating frame, so neither of them dissipates anything. They do not cancel each other either: $\\tfrac{3}{2}\\left(i_d(-\\omega_e L_q i_q) + i_q \\omega_e (L_d i_d + \\lambda_m)\\right) = \\omega_e T_e / P_p$, which is the airgap power exactly. Only on a machine with $L_d = L_q$ and the magnet term set aside is the pair self-cancelling.",
                "Torque $T_e = \\frac{3}{2} P_p \\left( \\lambda_m i_q + (L_d - L_q) i_d i_q \\right)$: a magnet term plus a reluctance term that is zero on a surface machine.",
                "As a state-space plant the machine is $\\dot{x} = Ax + Bv + d$ with $A$ carrying $-R/L$ on the diagonal, the speed-dependent coupling off it, and $d$ the magnet back-EMF.",
            ],
            "sandbox": {
                "title": "The machine with the controller switched off",
                "visualiser": "phase-portrait",
                "minutes": 9,
                "initial": {"a11": -0.6, "a12": 2, "a21": -2, "a22": -0.6},
                "brief": r'''
Now $x_1$ is $i_d$ and $x_2$ is $i_q$, and the matrix is the open-loop machine:

$$A = \begin{bmatrix} -R/L_d & \omega_e L_q / L_d \\ -\omega_e L_d / L_q & -R/L_q \end{bmatrix}$$

drawn here in normalised units, with the terminals shorted and the magnet term
suppressed so that only $A$ is on show. The diagonal is the winding resistance
pulling current down; the off-diagonal pair is the speed spinning the current
vector around.
''',
                "notice": [
                    "Take $a_{12}$ and $a_{21}$ to zero — the machine at standstill. Every trajectory straightens into a radial line and the readout says **stable node**: two independent first-order lags of time constant $L/R$, with no interaction at all. That is the plant the PI regulator is tuned for.",
                    "Now put the speed back and raise it: $a_{12} = 3$, $a_{21} = -3$. The spiral makes about four full turns before it disappears into the origin, where the opening matrix managed two and a half — the cross terms rotate the current vector faster than the resistance can pull it in. The coupling a controller must reject is proportional to $\\omega_e$.",
                    "Break the symmetry: $a_{12} = 3$ with $a_{21} = -1.5$, diagonals unchanged. The spiral leans into an ellipse. That is saliency — $L_q \\neq L_d$ — and it is the same asymmetry that produces the reluctance term in the torque equation.",
                    "Hold the signs opposite as the physics requires ($a_{12} > 0$, $a_{21} < 0$) and sweep both as far as they go. The trace never moves and the determinant only grows, so the readout never leaves stable. Cross-coupling is not an instability; it is a disturbance, and disturbances are what loop gain is for.",
                ],
            },
            "derive": {
                "title": "From the voltage equation to the state matrix and the torque",
                "minutes": 15,
                "vars": ["v_d", "v_q", "R", "i_d", "i_q", "L_d", "L_q", "omega", "lambda_m", "T_e", "P_p"],
                "brief": r'''
The $d$-axis voltage equation of a PMSM, with $\omega$ written for the electrical
speed $\omega_e$, is

$$v_d = R\, i_d + L_d \dot{i_d} - \omega L_q i_q$$

and the torque of a salient rotor is

$$T_e = \frac{3}{2} P_p \left( \lambda_m i_q + (L_d - L_q)\, i_d i_q \right)$$

where $P_p$ is the number of pole pairs.
''',
                "steps": [
                    {
                        "prompt": "Solve the $d$-axis voltage equation for $\\dot{i_d}$. Write it in terms of $v_d$, $R$, $i_d$, $\\omega$, $L_q$, $i_q$ and $L_d$.",
                        "answer": "\\frac{v_d - R i_d + \\omega L_q i_q}{L_d}",
                        "hint": "Move every term except $L_d \\dot{i_d}$ to the other side, then divide by $L_d$. Watch the sign of the coupling term as it crosses over.",
                        "deconstruct": [
                            "$L_d \\dot{i_d} = v_d - R i_d + \\omega L_q i_q$.",
                            "Divide through by $L_d$.",
                        ],
                    },
                    {
                        "prompt": "Write the plant as $\\dot{x} = Ax + Bv + d$ with $x = [i_d,\\ i_q]$. What is the entry of $A$ in the first row, second column — the coefficient multiplying $i_q$ in $\\dot{i_d}$?",
                        "answer": "\\frac{\\omega L_q}{L_d}",
                        "hint": "Read it off the expression you just derived, with $v_d$ set aside into $Bv$.",
                        "deconstruct": [
                            "The derived expression is $\\dot{i_d} = (v_d - R i_d + \\omega L_q i_q)/L_d$.",
                            "Collect the $i_q$ term: its coefficient is $\\omega L_q / L_d$, and it is positive.",
                        ],
                    },
                    {
                        "prompt": "A surface-mount rotor has its magnets on the outside, so the airgap is uniform and $L_d = L_q$. Write $T_e$ for that machine.",
                        "answer": "\\frac{3}{2} P_p \\lambda_m i_q",
                        "hint": "The reluctance term carries the factor $(L_d - L_q)$. Set it to zero.",
                        "deconstruct": [
                            "With $L_d = L_q$ the factor $(L_d - L_q)$ is zero, so the whole second term vanishes.",
                            "What is left is the magnet term alone.",
                        ],
                    },
                    {
                        "prompt": "That is a pure torque constant. Invert it: for a surface machine, write the $i_q$ that produces a demanded torque $T_e$.",
                        "answer": "\\frac{2 T_e}{3 P_p \\lambda_m}",
                        "hint": "Divide the demanded torque by everything multiplying $i_q$ in the previous answer.",
                        "deconstruct": [
                            "$T_e = \\frac{3}{2} P_p \\lambda_m i_q$.",
                            "Divide both sides by $\\frac{3}{2} P_p \\lambda_m$.",
                        ],
                    },
                ],
                "closing": r'''
Two results worth separating. The first is that torque is proportional to $i_q$ and
nothing else, which is why the outer loop of every drive commands a current and not a
voltage. The second is that $\omega$ appears in $A$ but nowhere in $T_e$: speed
changes how hard the current is to control, never how much torque it makes. On a
salient rotor the reluctance term reopens the question, because it makes $i_d$ worth
having for torque as well as for flux — that is what MTPA exploits.
''',
            },
            "blanks": {
                "title": "The dq model, and where the speed terms come from",
                "minutes": 9,
                "caption": "pmsm.py — two lags and a cross-coupling that grows with speed",
                "lang": "python",
                "brief": r"""
Four equations describe a permanent-magnet machine in the rotating frame, and the two
terms that make them interesting both carry $\omega_e$. Fill them in, then read the last
line — because misreading those terms as losses is the most common way to get
field-oriented control wrong.
""",
                "listing": """# Flux linkages. The magnet contributes to the d axis only.
lambda_d = L_d * i_d + ___
lambda_q = L_q * i_q

# Voltages.
v_d = R * i_d + L_d * did_dt - ___
v_q = R * i_q + L_q * diq_dt + ___

# Both omega_e terms arise from ___ ,
# so they store and return energy rather than dissipating it.
""",
                "blanks": [
                    {
                        "prompt": "What does the magnet add?",
                        "hole": "?",
                        "opts": ["lambda_m", "0", "L_q * i_q", "R * i_d"],
                        "a": 0,
                        "why": "The magnet's own flux linkage, a constant, and it sits on the d axis by definition — the d axis is *defined* as the direction the magnet points. That single constant is where the back-EMF and the torque both come from, and it is why $i_q$ produces torque and $i_d$ does not.",
                        "whys": [
                            "The magnet's own flux linkage, a constant, and it sits on the d axis by definition — the d axis is *defined* as the direction the magnet points. That single constant is where the back-EMF and the torque both come from, and it is why $i_q$ produces torque and $i_d$ does not.",
                            "Zero would describe an induction machine or a synchronous reluctance machine — no magnet, no back-EMF, and torque from saliency alone.",
                            "The q-axis flux belongs in the q-axis equation; the two axes are orthogonal and do not share terms.",
                            "A resistance times a current is a voltage, not a flux linkage. The units do not match.",
                        ],
                    },
                    {
                        "prompt": "The d-axis equation is coupled to the q-axis current.",
                        "hole": "?",
                        "opts": [
                            "omega_e * L_q * i_q",
                            "omega_e * L_d * i_d",
                            "omega_e * lambda_m",
                            "0",
                        ],
                        "a": 0,
                        "why": "The q-axis flux, rotated into the d axis by the frame's own motion. Note it involves the *other* axis's inductance and current — that crossing is what makes the two loops interfere, and feeding it forward is what uncouples them in module 3.",
                        "whys": [
                            "The q-axis flux, rotated into the d axis by the frame's own motion. Note it involves the *other* axis's inductance and current — that crossing is what makes the two loops interfere, and feeding it forward is what uncouples them in module 3.",
                            "The d-axis flux does not couple into its own equation this way; the rotation always brings in the perpendicular component.",
                            "The magnet term appears in the q-axis equation, not the d-axis one — it is the d-axis flux rotating into q.",
                            "Zero would mean the two axes are independent at all speeds, which is exactly the illusion the feedforward creates and the machine does not have.",
                        ],
                    },
                    {
                        "prompt": "And the q-axis equation is coupled to the whole d-axis flux.",
                        "hole": "?",
                        "opts": [
                            "omega_e * (L_d * i_d + lambda_m)",
                            "omega_e * L_q * i_q",
                            "omega_e * lambda_m",
                            "0",
                        ],
                        "a": 0,
                        "why": "The entire d-axis flux linkage, magnet included. The $\\omega_e\\lambda_m$ part is the back-EMF, which grows with speed and is what eventually runs out of bus voltage and forces field weakening; the $\\omega_eL_di_d$ part is why negative $i_d$ *reduces* the required voltage, which is exactly how field weakening works.",
                        "whys": [
                            "The entire d-axis flux linkage, magnet included. The $\\omega_e\\lambda_m$ part is the back-EMF, which grows with speed and is what eventually runs out of bus voltage and forces field weakening; the $\\omega_eL_di_d$ part is why negative $i_d$ *reduces* the required voltage, which is exactly how field weakening works.",
                            "The q-axis flux rotates into the d-axis equation, not into its own.",
                            "The magnet alone is the back-EMF but omits $L_di_d$, and dropping it removes the mechanism field weakening depends on.",
                            "Zero would mean no back-EMF at any speed, and a machine that never runs out of voltage.",
                        ],
                    },
                    {
                        "prompt": "Where do the omega_e terms come from?",
                        "hole": "?",
                        "opts": [
                            "differentiating a vector in a rotating frame",
                            "iron loss in the stator",
                            "the PWM switching",
                            "the winding resistance",
                        ],
                        "a": 0,
                        "why": "They are the $\\omega \\times \\lambda$ of differentiating in a rotating coordinate system — the same term that produces Coriolis and centrifugal forces in mechanics. Which means they are not losses: they store and return energy, and cancelling them with a feedforward costs nothing and is not cheating. Reading them as loss leads to trying to minimise them, which is the wrong instinct entirely.",
                        "whys": [
                            "They are the $\\omega \\times \\lambda$ of differentiating in a rotating coordinate system — the same term that produces Coriolis and centrifugal forces in mechanics. Which means they are not losses: they store and return energy, and cancelling them with a feedforward costs nothing and is not cheating. Reading them as loss leads to trying to minimise them, which is the wrong instinct entirely.",
                            "Iron loss is real and it is nowhere in this model — it would appear as a resistance, not as a speed-dependent coupling between the axes.",
                            "The model is written in continuous time about an averaged inverter; the switching does not appear in it at all.",
                            "The resistance is already there, as $Ri_d$ and $Ri_q$, and it carries no $\\omega_e$.",
                        ],
                    },
                ],
            },
            "lab": {
                "title": "Build the dq plant and its torque",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Three functions.

`dq_model(R, L_d, L_q, lam, w_e)` returns `(A, B, d)` for $\dot{x} = Ax + Bv + d$
with $x = [i_d,\ i_q]^\top$ and $v = [v_d,\ v_q]^\top$. `A` and `B` are `(2, 2)`
arrays and `d` is `(2, 1)`. The magnet back-EMF is a constant as far as the current
loop is concerned, so it belongs in `d`, not in `A`.

`steady_state(A, B, d, v_d, v_q)` returns the `(i_d, i_q)` at which
$Ax + Bv + d = 0$. One `np.linalg.solve` does it.

`torque(pole_pairs, lam, L_d, L_q, i_d, i_q)` returns the electromagnetic torque,
including the reluctance term.

The machine used by the checks is `R = 0.45`, `L_d = 0.0035`, `L_q = 0.0055`,
`lam = 0.085`, four pole pairs.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def dq_model(R, L_d, L_q, lam, w_e):
    """Return (A, B, d) for xdot = A x + B v + d, with x = [i_d, i_q]."""
    # TODO: -R/L on the diagonal, the speed coupling off it, back-EMF in d.
    A = np.zeros((2, 2))
    B = np.zeros((2, 2))
    d = np.zeros((2, 1))
    return A, B, d


def steady_state(A, B, d, v_d, v_q):
    """Return the (i_d, i_q) at which the derivative is zero."""
    # TODO: solve A x = -(B v + d).
    return 0.0, 0.0


def torque(pole_pairs, lam, L_d, L_q, i_d, i_q):
    """Electromagnetic torque, magnet term plus reluctance term."""
    # TODO
    return 0.0


if __name__ == "__main__":
    A, B, d = dq_model(0.45, 0.0035, 0.0055, 0.085, 800.0)
    print("A =", np.round(A, 4).tolist())
    i_d, i_q = steady_state(A, B, d, 10.0, 40.0)
    print("steady state:", round(i_d, 6), round(i_q, 6))
    print("torque:", round(torque(4, 0.085, 0.0035, 0.0055, i_d, i_q), 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def dq_model(R, L_d, L_q, lam, w_e):
    """Return (A, B, d) for xdot = A x + B v + d, with x = [i_d, i_q]."""
    A = np.array([[-R / L_d, w_e * L_q / L_d],
                  [-w_e * L_d / L_q, -R / L_q]])
    B = np.array([[1.0 / L_d, 0.0],
                  [0.0, 1.0 / L_q]])
    d = np.array([[0.0], [-w_e * lam / L_q]])
    return A, B, d


def steady_state(A, B, d, v_d, v_q):
    """Return the (i_d, i_q) at which the derivative is zero."""
    A = np.asarray(A, dtype=float)
    B = np.asarray(B, dtype=float)
    d = np.asarray(d, dtype=float).reshape(2, 1)
    v = np.array([[float(v_d)], [float(v_q)]])
    x = np.linalg.solve(A, -(B @ v + d))
    return float(x[0, 0]), float(x[1, 0])


def torque(pole_pairs, lam, L_d, L_q, i_d, i_q):
    """Electromagnetic torque, magnet term plus reluctance term."""
    return 1.5 * pole_pairs * (lam * i_q + (L_d - L_q) * i_d * i_q)


if __name__ == "__main__":
    A, B, d = dq_model(0.45, 0.0035, 0.0055, 0.085, 800.0)
    print("A =", np.round(A, 4).tolist())
    i_d, i_q = steady_state(A, B, d, 10.0, 40.0)
    print("steady state:", round(i_d, 6), round(i_q, 6))
    print("torque:", round(torque(4, 0.085, 0.0035, 0.0055, i_d, i_q), 6))
'''}],
                "hints": [
                    "The two coupling entries have opposite signs and different magnitudes: $+\\omega L_q/L_d$ above the diagonal, $-\\omega L_d/L_q$ below it.",
                    "`d` carries $-\\omega \\lambda_m / L_q$ in its second row and nothing in its first — the magnet flux is on the $d$ axis, so its EMF appears on $q$.",
                    "`np.linalg.solve(A, -(B @ v + d))` is the whole of `steady_state`; remember to reshape `v` to `(2, 1)`.",
                ],
                "tests": [
                    {"name": "the diagonal of A is the electrical time constant", "code": r'''
import numpy as np
_A, _B, _d = dq_model(0.45, 0.0035, 0.0055, 0.085, 800.0)
assert np.asarray(_A).shape == (2, 2), f"A should be 2x2, got {np.asarray(_A).shape}"
assert abs(_A[0, 0] + 128.57142857142858) < 1e-9, \
    f"A[0,0] should be -R/L_d = -128.5714..., got {_A[0, 0]}"
assert abs(_A[1, 1] + 81.81818181818183) < 1e-9, \
    f"A[1,1] should be -R/L_q = -81.8181..., got {_A[1, 1]}"
'''},
                    {"name": "the coupling terms are unequal and opposite", "code": r'''
import numpy as np
_A, _B, _d = dq_model(0.45, 0.0035, 0.0055, 0.085, 800.0)
assert abs(_A[0, 1] - 1257.142857142857) < 1e-6, \
    f"A[0,1] should be +w_e*L_q/L_d = 1257.1428..., got {_A[0, 1]}"
assert abs(_A[1, 0] + 509.0909090909091) < 1e-6, \
    f"A[1,0] should be -w_e*L_d/L_q = -509.0909..., got {_A[1, 0]}"
assert _A[0, 1] > 0 > _A[1, 0], \
    "the two coupling entries must have opposite signs: the speed term rotates the current vector, it does not grow it along one axis"
'''},
                    {"name": "B inverts the inductances and d carries the back-EMF", "code": r'''
import numpy as np
_A, _B, _d = dq_model(0.45, 0.0035, 0.0055, 0.085, 800.0)
assert abs(_B[0, 0] - 1.0 / 0.0035) < 1e-6 and abs(_B[1, 1] - 1.0 / 0.0055) < 1e-6, \
    f"B should be diag(1/L_d, 1/L_q), got {np.asarray(_B).tolist()}"
assert abs(_B[0, 1]) < 1e-12 and abs(_B[1, 0]) < 1e-12, \
    "v_d cannot drive i_q directly; B is diagonal"
_dd = np.asarray(_d, dtype=float).reshape(2, 1)
assert abs(_dd[0, 0]) < 1e-12, "the magnet flux is on the d axis, so it makes no d-axis EMF"
assert abs(_dd[1, 0] + 800.0 * 0.085 / 0.0055) < 1e-6, \
    f"d[1] should be -w_e*lam/L_q = {-800.0 * 0.085 / 0.0055}, got {_dd[1, 0]}"
'''},
                    {"name": "at standstill each axis settles at v over R", "code": r'''
import numpy as np
_A, _B, _d = dq_model(0.45, 0.0035, 0.0055, 0.085, 0.0)
_id, _iq = steady_state(_A, _B, _d, 10.0, 40.0)
assert abs(_id - 10.0 / 0.45) < 1e-6, f"i_d should be v_d/R = 22.2222, got {_id}"
assert abs(_iq - 40.0 / 0.45) < 1e-6, f"i_q should be v_q/R = 88.8889, got {_iq}"
'''},
                    {"name": "the steady state really is a steady state", "code": r'''
import numpy as np
_A, _B, _d = dq_model(0.45, 0.0035, 0.0055, 0.085, 800.0)
_id, _iq = steady_state(_A, _B, _d, 10.0, 40.0)
assert abs(_id + 9.478937911758834) < 1e-6, f"expected i_d = -9.478938, got {_id}"
assert abs(_iq + 3.2421641046117) < 1e-6, f"expected i_q = -3.242164, got {_iq}"
_x = np.array([[_id], [_iq]])
_v = np.array([[10.0], [40.0]])
_res = np.asarray(_A) @ _x + np.asarray(_B) @ _v + np.asarray(_d).reshape(2, 1)
assert float(np.max(np.abs(_res))) < 1e-6, \
    f"A x + B v + d should be zero at the steady state, residual was {float(np.max(np.abs(_res)))}"
'''},
                    {"name": "a salient rotor earns torque from negative i_d", "code": r'''
_flat = torque(4, 0.085, 0.0035, 0.0035, -5.0, 12.0)
_zero = torque(4, 0.085, 0.0035, 0.0055, 0.0, 12.0)
_neg = torque(4, 0.085, 0.0035, 0.0055, -5.0, 12.0)
_pos = torque(4, 0.085, 0.0035, 0.0055, 5.0, 12.0)
assert abs(_zero - 6.12) < 1e-9, f"with i_d = 0 the torque is the magnet term, 6.12 Nm, got {_zero}"
assert abs(_flat - 6.12) < 1e-9, f"a surface machine gets nothing from i_d; expected 6.12, got {_flat}"
assert abs(_neg - 6.84) < 1e-9, f"L_q > L_d means negative i_d adds torque; expected 6.84, got {_neg}"
assert abs(_pos - 5.40) < 1e-9, f"and positive i_d removes it; expected 5.40, got {_pos}"
'''},
                    {"name": "torque is odd in i_q and zero without it", "code": r'''
assert abs(torque(4, 0.085, 0.0035, 0.0055, -5.0, 0.0)) < 1e-12, \
    "no q-axis current, no torque — the reluctance term needs both currents"
_a = torque(4, 0.085, 0.0035, 0.0055, -5.0, 12.0)
_b = torque(4, 0.085, 0.0035, 0.0055, -5.0, -12.0)
assert _a > 1.0, f"12 A of q-axis current should make several Nm, got {_a}"
assert abs(_a + _b) < 1e-12, f"reversing i_q should reverse the torque exactly, got {_a} and {_b}"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "read": [
                {
                    "title": "Thirteen hertz of plant, and the voltage that decides the rest",
                    "minutes": 16,
                    "body": r'''
Hold the rotor of the machine still, put a step of voltage on the $q$ winding, and watch
the current. It rises the way a first-order lag rises, and the time constant is
$L_q/R = 0.0055/0.45 = 12.2$ ms. Turned into a corner frequency that is
$R/(2\pi L_q) = 13.0$ Hz.

Thirteen hertz. A traction drive has to command torque out to several hundred, and torque
is current, so the plant on its own is short by a factor of about twenty-five. The build
exercise *The winding is the filter* has you place the same circuit on a canvas at bench
scale — $0.5\ \Omega$ and 2 mH, corner at 40.6 Hz — and the check calls the number
"embarrassingly low" on purpose. That corner is the entire motivation for what follows,
and the thing worth noticing is that the same inductance which makes the plant this slow
is what makes the 10 kHz switching ripple 250 times smaller than the signal. You do not
get to remove it.

## Making one number out of two gains

Once the cross-coupling of module 2 is fed forward, the plant on either axis is
$i/v = 1/(Ls + R)$, a single pole at $-R/L$. Put a PI regulator round it,
$C(s) = K_p + K_i/s$, written over a common denominator as

$$C(s) = \frac{K_p s + K_i}{s}$$

so the controller carries a zero at $s = -K_i/K_p$. There is one obvious thing to do with
a zero you own and a pole you do not want: put one on top of the other. Setting
$K_i/K_p = R/L$ makes the numerator factor $(s + R/L)$ cancel the plant's denominator
exactly, and what is left of the loop gain is

$$L(s) = \frac{K_p s + K_i}{s}\cdot\frac{1}{Ls + R} = \frac{K_p}{Ls}$$

a pure integrator. Close it and $\frac{L(s)}{1+L(s)} = \frac{K_p}{Ls + K_p}$, a first-order
lag with its pole at $-K_p/L$. Demand that pole be at $-\alpha$ and both gains fall out:
$K_p = \alpha L$, and substituting back into the cancellation condition,
$K_i = K_p R/L = \alpha R$. The derive unit *Tuning a PI current regulator by cancellation*
walks those five steps individually.

Two gains, one knob, and the knob is in rad/s of closed-loop bandwidth.

```python
R, LD, LQ = 0.45, 0.0035, 0.0055
import math

for name, L in (("d", LD), ("q", LQ)):
    print("%s axis: plant pole %.2f 1/s = %.2f Hz, tau = %.2f ms"
          % (name, R / L, R / (2.0 * math.pi * L), 1e3 * L / R))

BW = 2000.0
print("alpha = %.0f rad/s = %.1f Hz, closed-loop tau = %.0f us" % (BW, BW / (2.0 * math.pi), 1e6 / BW))
for name, L in (("d", LD), ("q", LQ)):
    print("%s axis gains: K_p = alpha*L = %.1f,  K_i = alpha*R = %.1f,  speed-up %.1fx"
          % (name, BW * L, BW * R, BW / (R / L)))
```

The two proportional gains differ because the inductances do; the two integral gains are
both 900 because $K_i = \alpha R$ contains no inductance at all — the $L$ cancelled when
the cancellation condition was substituted. That is a useful sanity check on any drive's
parameter file: unequal $K_p$, equal $K_i$.

## The number the algebra hides

Nothing in that derivation mentions voltage, and the plant model has no upper limit on it.
The inverter does. Work out what the regulator asks for at the instant a step arrives.

The integrator state is zero, the error is the whole step $\Delta i$, and the feedforward
is already claiming $\omega_e\lambda_m = 800 \times 0.085 = 68.0$ V at this operating
point. So the command is

$$v_q = K_p\,\Delta i + \omega_e\lambda_m = \alpha L_q \Delta i + 68.0$$

and it has to fit inside the modulator's 173.2 V. Rearranged, the largest step that does
not clip the regulator is

$$\Delta i_{max} = \frac{V_{max} - \omega_e\lambda_m}{\alpha L_q}$$

which is inversely proportional to the bandwidth. Doubling $\alpha$ halves the step size
you can take linearly, on the same machine at the same speed.

```python
import math

R, LQ, LAM = 0.45, 0.0055, 0.085
W_E, V_MAX = 800.0, 300.0 / math.sqrt(3.0)

ff = W_E * LAM
print("modulator limit %.1f V, feedforward already claims %.1f V, headroom %.1f V"
      % (V_MAX, ff, V_MAX - ff))
for bw in (1000.0, 2000.0, 4000.0, 6000.0):
    kp = bw * LQ
    print("alpha %5.0f rad/s: K_p %5.2f, an 8 A step asks %6.1f V of %5.1f V -> largest clean step %5.2f A"
          % (bw, kp, kp * 8.0 + ff, V_MAX, (V_MAX - ff) / kp))

t = -(LQ / R) * math.log(1.0 - 8.0 * R / (V_MAX - ff))
print("flat out, with the whole headroom on the winding, 8 A takes %.1f us" % (t * 1e6))
print("the tuned loop at 2000 rad/s takes %.0f us to reach 99%% of the same step" % (4.6e6 / 2000.0))
```

At $\alpha = 2000$ rad/s the largest clean step is 9.56 A, so the 8 A reference used all
through this course sits inside the linear region with a little to spare. At
$\alpha = 6000$ it is 3.19 A, and the same 8 A command drives the regulator hard into the
rail: it asks for 332 V from a bus that can synthesise 173.2. Nothing about the plant
changed. The gain did, and the gain multiplies an error that a step makes large.

The last two lines are the honest comparison. With the entire headroom dumped onto the
winding the machine can move 8 A in 426 µs, and that is a hard limit set by
$L_q\,\mathrm{d}i/\mathrm{d}t$. The tuned loop takes 2.3 ms to reach 99 per cent of the
same step — deliberately about five times slower than the actuator, and that ratio is what
keeps the response linear, predictable and free of overshoot. A loop tuned to the edge of
its actuator is a loop whose behaviour changes with the size of the command.

## What happens when it does clip

Which it will, because a real drive meets steps it did not design for. The sandbox *What a
decade of bandwidth costs* draws the same trade on the mechanical loop above this one:
push both poles to $-12$ and the effort trace *starts* at $-144$, with the whole peak
landing in the first sample. Here the peak lands in the first sample too, and when the
inverter cannot supply it, the error stays large while the output is stuck — and the
integrator, which knows nothing about any of this, keeps accumulating.

The lab *Tune and simulate a PI current loop* asks for exactly one line of defence, and
this is what it is worth:

```python
R, L, BW, I_REF, DT, N = 0.45, 0.0035, 2000.0, 10.0, 1e-6, 10000


def step_response(v_max=None, anti_windup=True):
    K_p, K_i = BW * L, BW * R
    i = z = 0.0
    out = []
    for _ in range(N):
        out.append(i)
        e = I_REF - i
        v = K_p * e + z
        v_s = v if v_max is None else max(-v_max, min(v_max, v))
        if v_s == v or not anti_windup:
            z += DT * K_i * e
        i += DT * (v_s - R * i) / L
    return out


for label, vmax, aw in (("no limit", None, True), ("20 V, integrator frozen", 20.0, True),
                        ("20 V, integrator free", 20.0, False)):
    ys = step_response(vmax, aw)
    peak = max(ys)
    print("%-24s peak %7.4f A (%+5.2f%% of the reference), settles at %.4f A"
          % (label, peak, 100.0 * (peak / I_REF - 1.0), ys[-1]))
```

Unlimited, the response is the first-order lag it was designed to be and never passes
10 A. Clipped at 20 V with the integrator frozen whenever the output is limited, the
current climbs more slowly and reaches 9.8383 A without ever exceeding the reference.
Clipped with the integrator left running, it goes to 10.4919 A — five per cent past a
reference that a first-order design cannot overshoot at all — and is still 0.23 A above it
at the end of the run. The difference is one `if`.

## The mistake, and why it is tempting

The mistake is treating $\alpha$ as free and raising it until the response looks fast
enough. It is tempting for reasons that are all good ones. The algebra genuinely does
reduce the design to one number. The simulation with no voltage limit genuinely does obey
it: double $\alpha$ and the rise time halves, with no penalty appearing anywhere in the
model. And $\alpha$ is the number in the specification, so making it larger feels like
progress against a requirement.

What the model does not contain is the peak voltage at the instant of the step, and that
is the quantity that runs out first. The failure it produces is not a wrong number in a
simulation; it is a drive that behaves one way on the 2 A steps used during commissioning
and another way on the 15 A step the vehicle asks for on a hill, because one of them is in
the linear region and the other is rate-limited by the bus. Raising the bandwidth moves
the boundary between those two regimes towards you.

The second mistake is quieter, and the capstone forbids it in a constraint: computing the
decoupling feedforward from the *reference* currents rather than the measured ones.
References are noise-free, available a sample earlier, and produce a visibly cleaner trace,
which is what makes it attractive. It fails exactly when the loop is limited. At 2500 rad/s
with an 8 A reference and the output clipped, the actual $i_q$ might be 2 A while the
reference says 8: a feedforward from the reference asks for
$-\omega_e L_q \times 8 = -110$ V on the $d$ axis, when the machine's real coupling is
$-\omega_e L_q \times 2 = -27.5$ V. Eighty-two volts of feedforward is being added to a
command that was already over the limit, and the vector limiter then shortens both axes to
make room for it. A feedforward built from references is an open-loop guess, and it stops
being right at the moment its help is needed.

## Where it stops holding

**The cancellation is only as good as $R$ and $L$.** Copper's resistance rises about 0.39
per cent per kelvin, so 75 K of temperature rise takes $R$ from 0.45 to 0.583 $\Omega$ and
the $q$-axis plant pole from $-81.8$ to $-106.0$ 1/s. The PI zero has not moved: it is
still at $K_i/K_p = 900/11 = 81.8$. The cancellation now misses by 24 1/s and leaves a
residual mode with a 9.4 ms time constant in a loop designed for 0.5 ms. It is invisible on
a small step, because the dominant pole at $-K_p/L$ still governs, and it shows up as a slow
tail whenever the regulator comes out of saturation — which is the one moment a current loop
is genuinely being asked to perform.

**$L$ moves too, and the other way.** $L_q$ saturates with current: 5.5 mH at 8 A can be
4.0 mH near the 20 A rating. $K_p$ was fixed at 11.0 for 5.5 mH, so the achieved bandwidth
at high current is $11.0/0.004 = 2750$ rad/s rather than 2000 — 37 per cent fast, at
precisely the operating point where the next paragraph says you can least afford it.

**The loop is not continuous.** Every line above is continuous-time algebra, and the real
regulator runs once per 100 µs modulator period with roughly one and a half periods of
computational and PWM delay, 150 µs. A pure delay contributes a phase lag of $\alpha T_d$:
at $\alpha = 2000$ rad/s that is 0.30 rad, or $17.2°$, spent before any other margin is
counted. The usual guard is $\alpha \le \omega_s/10 = 6283$ rad/s at 10 kHz, and 2000 rad/s
sits comfortably at $\omega_s/31$. Run the same design at $\alpha = 6000$ and the delay
alone costs $51.6°$, so the discrete loop overshoots where the continuous model promises it
cannot — and the 37 per cent that saturation adds to the effective bandwidth comes straight
out of what is left.

**The cascade above assumes separation.** The whole point of tuning the current loop as an
isolated first-order lag is that the speed loop above sees it as a gain. That holds while
the speed loop is roughly a decade slower, so 200 rad/s or 32 Hz, and the modulator a
decade faster than the current loop, which 10 kHz against 318 Hz satisfies with room. Close
those gaps and the two loops interact, and neither of the two designs done in isolation
describes what happens.

## What you are about to build

The build exercise puts the plant itself on a canvas and measures the 40.6 Hz corner, the
$-45°$ of phase that says it is first order and nothing more, and the 250-fold attenuation
at 10 kHz — the three facts this reading opened with, obtained from a solver rather than
asserted. The derive unit produces $K_p = \alpha L$ and $K_i = \alpha R$ symbolically. And
the lab writes `pi_gains` and `step_response`, and its last test is the one that matters
here: a 20 V clip must slow the rise, must not overshoot, and must still be converging on
the reference at the end — which is to say, it checks the `if`.
''',
                },
            ],
            "quiz": {
                "title": "One knob, and the volt-second budget it spends",
                "minutes": 8,
                "questions": [
                    {
                        "q": "The tuning collapses to $K_p = \\alpha L$, $K_i = \\alpha R$, with $\\alpha$ the only free number. What stops you setting it to 20000 rad/s?",
                        "opts": [
                            "The peak command $K_p\\Delta i$ at the instant of a step, which has to fit the bus",
                            "The pole-zero cancellation, which stops working once $\\alpha$ passes the plant pole $R/L$",
                            "Nothing in the plant model, which stays first order at every value of $\\alpha$",
                            "The integral gain, which would grow past the proportional gain and take the loop unstable",
                        ],
                        "a": 0,
                        "whys": [
                            r"$\alpha L_q\Delta i + \omega_e\lambda_m \le V_{max}$ is the whole constraint, and at 20000 rad/s an 8 A step asks for over 900 V from a 300 V bus.",
                            r"The cancellation depends on $K_i/K_p = R/L$ and on nothing else — the ratio holds at any $\alpha$, since both gains scale with it together. What breaks the cancellation is an error in $R$ or $L$, not the bandwidth.",
                            r"True of the model, and that is exactly the trap: the plant equations contain no voltage limit, so raising $\alpha$ in simulation shows a faster response and no cost anywhere. The cost lives in a variable the model does not have.",
                            r"$K_i$ is already larger than $K_p$ at every sane bandwidth — 900 against 11 at $\alpha = 2000$ — and the loop is a well-damped first-order lag. Comparing gains with different units says nothing about stability.",
                        ],
                        "why": r'''
At the instant a step arrives the integrator is at zero and the error is the whole step, so
the regulator asks for $K_p\Delta i$ on top of whatever the feedforward already claims. On
the $q$ axis at 800 rad/s the feedforward is 68.0 V of the 173.2 V available, leaving
105.2 V, so the largest step that stays linear is $105.2/(\alpha L_q)$ — 9.56 A at
$\alpha = 2000$ and 3.19 A at $\alpha = 6000$. The bandwidth is not free; it is bought with
the size of the command that still behaves the way the design says.
''',
                    },
                    {
                        "q": "The two axes end up with different proportional gains, 7.0 and 11.0, but the same integral gain of 900. Why do the integral gains match?",
                        "opts": [
                            "Because the vector voltage limiter acts on both axes together and needs matched integrators",
                            "Because $K_i = \\alpha R$ carries the shared resistance, the inductance having cancelled out",
                            "Because both axes are read by the same current sensors, which fix the integral scaling",
                            "Because the $q$ axis makes the torque, so its integrator is deliberately kept the more urgent",
                        ],
                        "a": 1,
                        "whys": [
                            r"The limiter does act on the vector, and the loop does freeze both integrators together when it clips — but that is anti-windup, not tuning. It would work identically with two different integral gains.",
                            r"$K_i = K_pR/L = (\alpha L)R/L$, and the $L$ divides out, leaving a gain that depends on the resistance the two axes share.",
                            r"Sensor scaling multiplies the measured current, so it would scale both gains on an axis together and could not make one of them match across axes while the other differs.",
                            r"Nothing here is a preference. Both axes are tuned to the same $\alpha$ by the same rule; the $q$ axis gets the larger $K_p$ because $L_q > L_d$, which makes its loop no more urgent, only differently scaled.",
                        ],
                        "why": r'''
Substituting $K_p = \alpha L$ into the cancellation condition $K_i = K_pR/L$ gives
$K_i = \alpha R$: the inductance cancels and the resistance, which both windings share,
does not. So $K_p$ is 7.0 on the $d$ axis and 11.0 on the $q$, while $K_i$ is 900 on both.
It makes a quick audit of any drive's parameter file: unequal proportional gains and equal
integral gains is what a correctly cancelled pair looks like, and two identical $K_p$
values means somebody used one inductance for a salient machine.
''',
                    },
                    {
                        "q": "The same loop is run into a 20 V clip twice, once freezing the integrator while the output is limited and once leaving it running. What is the difference?",
                        "opts": [
                            "The frozen run holds at or under the reference; the free one overshoots to 10.49 A",
                            "The frozen run reaches the reference sooner, having stopped fighting against the limiter",
                            "Nothing lasting, since the integrator unwinds once the error changes sign",
                            "The frozen run keeps a permanent offset, its integrator having lost the error it needed",
                        ],
                        "a": 0,
                        "whys": [
                            r"9.8383 A against 10.4919 A on a 10 A reference, from a design whose single real pole cannot overshoot at all.",
                            r"It reaches it later, not sooner — freezing the integrator removes command the loop would otherwise have applied, and the run is still climbing at the end. Anti-windup buys the peak, and it pays for it in rise time.",
                            r"It does unwind, and the way it unwinds is the overshoot: the accumulated state can only be discharged by an error of the opposite sign, which means being above the reference for as long as it takes.",
                            r"The integrator is frozen only while the output is clipped. The moment the command falls inside the limit it resumes, and the run settles on the reference with no offset — which is what the lab's last assertion checks.",
                        ],
                        "why": r'''
Conditional integration costs one `if` and buys the peak. Frozen, the current reaches
9.8383 A and never passes the reference; free, it reaches 10.4919 A — nearly five per cent
of overshoot from a closed loop with one real pole, which cannot overshoot on its own. The
mechanism is worth stating precisely: while the output is clipped, more integrator state
produces no more voltage, so the state charges without effect and can afterwards be
discharged only by an error of the opposite sign. That error is the drive being above its
reference, and the time it takes is the overshoot.
''',
                    },
                    {
                        "q": "At 2500 rad/s the loop is clipped and $i_q$ has reached 2 A of its 8 A reference. A feedforward built from the reference instead of the measurement does what?",
                        "opts": [
                            "Cancels the coupling more accurately, the reference carrying none of the sensor's noise",
                            "Nothing different, because the limiter removes the feedforward anyway",
                            "Asks for $-110$ V of $d$-axis feedforward where the machine's coupling is $-27.5$ V",
                            "Improves the response, since the reference is available a whole sample before the measurement",
                        ],
                        "a": 2,
                        "whys": [
                            r"It is quieter, and that is the attraction. Accuracy is a different question: a noise-free number computed for a machine state that does not exist is wrong by the whole gap between reference and measurement.",
                            r"The limiter scales the vector down, it does not remove any term from it. An oversized feedforward means the limiter takes the extra out of the *regulator's* share, which is the part actually closing the loop.",
                            r"$-\omega_eL_q \times 8$ against the true $-\omega_eL_q \times 2$, an error of 82.5 V added to a command already over the limit.",
                            r"It is available earlier, by one sample of 100 µs. What arrives early is a prediction of a current the machine has not got, and during limiting it may not get for milliseconds.",
                        ],
                        "why": r'''
The coupling term is $-\omega_eL_qi_q$, and $i_q$ means the current that is flowing. With
the reference at 8 A and the machine at 2 A, a reference-based feedforward asks for
$-2500 \times 0.0055 \times 8 = -110$ V where the machine is producing
$-2500 \times 0.0055 \times 2 = -27.5$ V, so 82.5 V of a command that is already clipped is
spent cancelling something that is not there. The limiter then shortens the whole vector to
fit, taking the reduction out of the regulator's own contribution. A feedforward from
measurements is right at every instant, including the ones where the loop is not.
''',
                    },
                    {
                        "q": "Seventy-five kelvin of temperature rise takes the winding resistance from 0.45 to 0.583 $\\Omega$, and the gains are unchanged. What follows?",
                        "opts": [
                            "The bandwidth rises in proportion, a larger resistance making the plant pole faster",
                            "Nothing: the closed-loop pole is $-K_p/L$ and has no resistance in it anywhere",
                            "A residual mode near $-106$ 1/s, seen as a slow tail on the way out of saturation",
                            "Instability, the PI zero now sitting to the right of the plant pole it was meant to cancel",
                        ],
                        "a": 2,
                        "whys": [
                            r"The plant pole does move, from $-81.8$ to $-106.0$ 1/s. The closed-loop bandwidth is set by $K_p/L$ and does not follow it — what follows is that the pole is no longer the one the zero was placed on.",
                            r"True of the dominant pole, which is why the mistuning hides on ordinary steps. It is not true of the whole response: a cancellation that misses leaves the uncancelled pole in the state trajectory, excited by anything that disturbs the state.",
                            r"The zero stays at $K_i/K_p = 81.8$ while the pole has moved to $106.0$, so the pair no longer annihilates.",
                            r"Both remain in the left half-plane and the loop remains a stable, well-damped one. An imperfect cancellation degrades the response shape; it takes rather more than a warm winding to move a pole across the axis.",
                        ],
                        "why": r'''
The PI zero is at $K_i/K_p = 900/11 = 81.8$ 1/s, placed on a plant pole that was at
$R/L_q = 81.8$ 1/s when the machine was cold. Warm, the pole is at $0.583/0.0055 = 106.0$
and the two no longer cancel, so a mode with a 9.4 ms time constant survives in a loop
designed for 0.5 ms. On a small step the dominant pole at $-K_p/L$ still dictates the shape
and nothing looks wrong. It appears as a slow tail when the regulator comes out of
saturation with a disturbed state, which is why this defect is usually found on a vehicle
rather than on a bench.
''',
                    },
                    {
                        "q": "The derivation is continuous-time, and the loop runs once per 100 µs period with about 1.5 periods of delay. What does that cost at $\\alpha = 2000$ rad/s?",
                        "opts": [
                            "A steady-state error proportional to the delay, which the integrator cannot remove",
                            "About 17° of phase, spent before any other stability margin is accounted for",
                            "Nothing, 10 kHz being three full decades above the 318 Hz closed-loop bandwidth",
                            "A gain error worth 1.5 samples, removed by scaling $K_p$ by the same factor",
                        ],
                        "a": 1,
                        "whys": [
                            r"A delay contributes phase, not a steady-state error. The integrator still drives a constant reference to zero error; what the delay threatens is the margin with which it does so.",
                            r"$\alpha T_d = 2000 \times 150\ \mu\text{s} = 0.30$ rad, and none of it is recoverable.",
                            r"It is about a decade and a half, not three: 10 kHz against 318 Hz is a ratio of 31. Three decades would be a 318 kHz modulator, which no traction inverter runs.",
                            r"A pure delay has unity magnitude at every frequency — it changes phase alone. There is no gain to correct, and scaling $K_p$ would move the crossover to where the phase lag is larger still.",
                        ],
                        "why": r'''
A pure delay $T_d$ contributes $-\alpha T_d$ radians of phase at the crossover and leaves
the magnitude untouched. With 1.5 periods of 100 µs that is 150 µs, so $2000 \times 150\
\mu\text{s} = 0.30$ rad, $17.2°$, gone before anything else is counted. It is why the usual
guard is $\alpha \le \omega_s/10$, which at 10 kHz is 6283 rad/s: the chosen 2000 rad/s
sits at $\omega_s/31$ with room to spare. Run the same design at 6000 rad/s and the delay
alone costs $51.6°$, and a loop the continuous algebra says cannot overshoot begins to.
''',
                    },
                ],
            },
            "title": "Current control in the rotating frame",
            "summary": "One PI per axis, its zero placed on the plant pole, plus a feedforward that cancels what the speed does.",
            "concepts": [
                "Once the coupling is fed forward, each axis is $i/v = 1/(Ls + R)$ — a first-order lag and nothing more.",
                "Pole–zero cancellation: put the PI zero at $-K_i/K_p = -R/L$ and the closed loop collapses to $\\alpha/(s+\\alpha)$ with $K_p = \\alpha L$, $K_i = \\alpha R$. One number to tune.",
                "The feedforward $v_d^{ff} = -\\omega_e L_q i_q$, $v_q^{ff} = \\omega_e (L_d i_d + \\lambda_m)$ removes the coupling the regulator would otherwise have to reject as a disturbance.",
                "The inverter is a saturating actuator. Without anti-windup the integrator keeps charging while the output is clipped and repays it as overshoot.",
                "Cascade separation: the current loop must be roughly a decade faster than the speed loop above it, and the modulator's switching frequency a decade above that again.",
            ],
            "sandbox": {
                "title": "What a decade of bandwidth costs",
                "visualiser": "pole-place",
                "minutes": 8,
                "initial": {"p1": -2, "p2": -4},
                "brief": r'''
The plant drawn here is a double integrator: a force accelerating a mass. In a drive
that is the mechanical half — torque accelerates the rotor, the speed integrates into
position — with the current loop underneath assumed fast enough to be a pure gain.

Position starts at 1 and is driven to zero by $u = -k_1 x - k_2 \dot{x}$, with the
gains read straight off the pole pair: matching $s^2 + k_2 s + k_1$ to
$(s - p_1)(s - p_2)$ gives $k_1 = p_1 p_2$ and $k_2 = -(p_1 + p_2)$. The upper trace
is the position; the lower one is the force it took, and in a drive that force is a
torque, which through the torque constant is a $q$-axis current the inverter has to
deliver.
''',
                "notice": [
                    "Double both poles, to $-4$ and $-8$. Settling roughly halves — about 2.3 s to 1.2 s — while the readout's first gain goes from 8 to 32. Twice the speed, four times the peak force.",
                    "Now put one pole at $-12$ and leave the other at $-2$. Settling barely improves on the original pair, because the slow pole still sets the pace, but $k_1$ has trebled from 8 to 24. Paying for a fast pole you do not use is the classic cascade mistake.",
                    "Push both poles to $-12$, the far end of both sliders. Settling drops to about half a second and the effort trace *starts* at $-144$: the peak demand is $k_1$ times the initial position, and it lands in the first sample. That number is an actuator specification, and if the current loop cannot supply it in a fraction of the settling time, none of this happens.",
                ],
            },
            "derive": {
                "title": "Tuning a PI current regulator by cancellation",
                "minutes": 14,
                "vars": ["s", "R", "L_d", "K_p", "K_i", "alpha", "i_d", "v_d"],
                "brief": r'''
Take the $d$ axis with the cross-coupling already fed forward, so what is left is

$$v_d = R\, i_d + L_d \dot{i_d}$$

and control it with $C(s) = K_p + \dfrac{K_i}{s}$. The goal is a closed loop that is
first order with a single bandwidth $\alpha$ in radians per second.
''',
                "steps": [
                    {
                        "prompt": "Laplace-transform the plant with zero initial current. Write the transfer function from $v_d$ to $i_d$.",
                        "answer": "\\frac{1}{L_d s + R}",
                        "hint": "Replace $\\dot{i_d}$ with $s\\, i_d$, collect $i_d$, and divide.",
                        "deconstruct": [
                            "$v_d = R i_d + L_d s i_d = (L_d s + R) i_d$.",
                            "So $i_d / v_d = 1/(L_d s + R)$.",
                        ],
                    },
                    {
                        "prompt": "Written over a common denominator, $C(s) = \\frac{K_p s + K_i}{s}$, so the controller has a zero at $s = -K_i/K_p$. Choose $K_i$ so that this zero sits exactly on the plant pole $-R/L_d$. Write $K_i$ in terms of $K_p$, $R$ and $L_d$.",
                        "answer": "\\frac{K_p R}{L_d}",
                        "hint": "Set $K_i/K_p = R/L_d$ and solve for $K_i$.",
                        "deconstruct": [
                            "The zero is at $-K_i/K_p$; the pole is at $-R/L_d$.",
                            "Equating the two gives $K_i = K_p R / L_d$.",
                        ],
                    },
                    {
                        "prompt": "With that choice the loop gain collapses to $L(s) = \\frac{K_p}{L_d s}$. Write the closed-loop transfer function $\\frac{L(s)}{1 + L(s)}$ as a ratio in $s$.",
                        "answer": "\\frac{K_p}{L_d s + K_p}",
                        "hint": "Multiply numerator and denominator by $L_d s$ to clear the inner fraction.",
                        "deconstruct": [
                            "$\\frac{K_p/(L_d s)}{1 + K_p/(L_d s)}$.",
                            "Multiplying top and bottom by $L_d s$ gives $K_p/(L_d s + K_p)$.",
                        ],
                    },
                    {
                        "prompt": "That is a first-order lag with a single pole at $-K_p/L_d$. For a closed-loop bandwidth $\\alpha$, write $K_p$.",
                        "answer": "\\alpha L_d",
                        "hint": "Set $K_p/L_d = \\alpha$.",
                        "deconstruct": [
                            "The pole is at $-K_p/L_d$ and you want it at $-\\alpha$.",
                            "So $K_p = \\alpha L_d$.",
                        ],
                    },
                    {
                        "prompt": "And substituting that back into the cancellation condition, write $K_i$ in terms of $\\alpha$ and $R$.",
                        "answer": "\\alpha R",
                        "hint": "Put $K_p = \\alpha L_d$ into $K_i = K_p R / L_d$ and let $L_d$ cancel.",
                        "deconstruct": [
                            "$K_i = K_p R / L_d = (\\alpha L_d) R / L_d$.",
                            "The inductance cancels, leaving $K_i = \\alpha R$.",
                        ],
                    },
                ],
                "closing": r'''
Two gains, one knob: $K_p = \alpha L$ and $K_i = \alpha R$, and the same pair of
formulae works on the $q$ axis with $L_q$ in place of $L_d$. The tuning depends on
the machine parameters and not at all on the operating point, which is the practical
payoff of doing the control in the rotating frame.

The cancellation is exact only if $R$ and $L$ are exact. A mistuned zero leaves a
slow residual mode at $-R/L$ in the state response — visible whenever the regulator
comes out of voltage saturation, which is the one place a current loop is asked to
behave.
''',
            },
            "build": {
                "title": "The winding is the filter",
                "minutes": 22,
                "brief": r"""
A field-oriented controller commands a voltage and expects a current. Between the two
sits the winding, and once the cross-coupling is fed forward each axis really is nothing
more than $i/v = 1/(Ls + R)$ — a first-order lag you can put on a canvas.

## What to build

One phase of a machine: $R = 0.5\ \Omega$ in series with $L = 2$ mH, driven from a 1 V
source. The **10 mΩ sense resistor is already there**, at the ground end, and the probe
is across it — that is how you measure a current with a voltmeter, and it is how the
drive does it too. A reading of 19.6 mV means 1.96 A.

## What the checks measure

- The DC current, which is just $V/(R + R_{sense})$ and confirms the resistance.
- The electrical pole at $(R + R_{sense})/L$, which lands at **40.6 Hz**. That is the
  bandwidth the plant gives you for free, and it is embarrassingly low — which is the
  entire motivation for the PI controller in this module. Pole-zero cancellation puts
  the PI zero right on top of this pole and replaces it with whatever bandwidth you
  chose.
- The attenuation at the **10 kHz switching frequency**, which comes out at about 250×.
  This is why PWM works at all: the inverter applies a square wave that slams between
  the rails, and the winding's own inductance turns it into a current with a few tenths
  of a per cent of ripple. Nothing was filtered on purpose. The load was already a
  filter, and that is what makes the whole technique practical.

## The thing worth noticing

The same inductance appears in both results with opposite sign of usefulness: it makes
the plant slow, which costs you control bandwidth, and it makes the ripple small, which
is what lets you switch. Every winding design is that trade.
""",
                "start": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 2, "y": 6, "rot": 1, "value": 1},
                        {"id": "g0", "kind": "GND", "x": 2, "y": 9},
                        {"id": "rsen", "kind": "R", "x": 14, "y": 7, "rot": 1, "value": 0.01},
                        {"id": "g1", "kind": "GND", "x": 14, "y": 9},
                        {"id": "out", "kind": "OUT", "x": 14, "y": 5},
                    ],
                    "wires": [
                        {"a": [2, 7], "b": [2, 9]},
                        {"a": [14, 5], "b": [14, 6]},
                        {"a": [14, 8], "b": [14, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "v", "kind": "V", "x": 2, "y": 6, "rot": 1, "value": 1},
                        {"id": "g0", "kind": "GND", "x": 2, "y": 9},
                        {"id": "rw", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 0.5},
                        {"id": "lw", "kind": "L", "x": 10, "y": 5, "rot": 0, "value": 2e-3},
                        {"id": "rsen", "kind": "R", "x": 14, "y": 7, "rot": 1, "value": 0.01},
                        {"id": "g1", "kind": "GND", "x": 14, "y": 9},
                        {"id": "out", "kind": "OUT", "x": 14, "y": 5},
                    ],
                    "wires": [
                        {"a": [2, 7], "b": [2, 9]},
                        {"a": [2, 5], "b": [5, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [11, 5], "b": [14, 5]},
                        {"a": [14, 5], "b": [14, 6]},
                        {"a": [14, 8], "b": [14, 9]},
                    ],
                },
                "checks": [
                    {
                        "name": "1.96 A at DC through 0.51 ohms",
                        "code": r"""
c.assert(c.count('L') === 1, 'One winding inductance; there are ' + c.count('L') + '.');
c.assert(c.count('R') === 2, 'Two resistors: the winding and the sense resistor.');
c.close(c.vout(), 0.019608, 0.03,
  'the sense voltage at DC. The inductor is a short at DC, so the current is ' +
  '1 V / (0.5 + 0.01) = 1.96 A, and across 10 milliohms that is 19.6 mV. A reading ' +
  'near 1 V means the probe is on the wrong side of the sense resistor');
""",
                    },
                    {
                        "name": "the electrical pole sits at 40.6 Hz",
                        "code": r"""
const fc = c.corner(0.1, 1e6);
c.close(fc, 40.58, 0.05,
  'the measured corner. It is (R + R_sense)/(2*pi*L) = 0.51/(2*pi*0.002). This is the ' +
  'plant bandwidth before any controller touches it, and it is the number the PI ' +
  'zero is placed on top of');
""",
                    },
                    {
                        "name": "10 kHz ripple is attenuated about 250 times",
                        "code": r"""
const dc = c.vout(), sw = c.gain(10e3);
c.close(dc / sw, 246.4, 0.06,
  'the ratio of DC response to the response at the 10 kHz switching frequency. The ' +
  'winding reactance there is 2*pi*10kHz*2mH = 126 ohms against 0.51 ohms of ' +
  'resistance, so the current ripple is smaller than the DC current by that ratio. ' +
  'This is why PWM produces a smooth current from a square voltage');
c.close(sw, 79.58e-6, 0.06,
  'the sense voltage at the switching frequency, in absolute terms — 80 microvolts ' +
  'against 19.6 millivolts of signal, which is the ripple a current sensor has to see ' +
  'past');
""",
                    },
                    {
                        "name": "first order, and only first order",
                        "code": r"""
c.close(c.phase(40.58), -45, 0.12,
  'the phase at the corner. A single pole gives exactly -45 degrees there; a second ' +
  'reactance anywhere in the loop would push it past that');
c.close(c.gain(1e3) / c.gain(10e3), 10.0, 0.06,
  'the fall over one decade well above the pole. A first-order lag gives a factor of ' +
  '10 per decade — 20 dB. A factor near 100 would mean a second pole');
""",
                    },
                ],
                "hints": [
                    "Both the winding resistance and the winding inductance go in series between the source and the sense resistor.",
                    "The sense resistor is deliberately tiny so that it barely disturbs the circuit it measures — but it is not zero, and the checks include it in the 0.51 Ω.",
                    "The probe stays where it is, on the node between the inductor and the sense resistor. That node's voltage is the current, scaled by 10 mΩ.",
                ],
            },
            "lab": {
                "title": "Tune and simulate a PI current loop",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
`pi_gains(R, L, bw)` returns `(K_p, K_i)` from the derivation: `bw * L` and `bw * R`.

`step_response(R, L, bw, i_ref, dt, steps, v_max=None)` simulates one axis with
forward Euler and returns the current at every step, recording it **before** each
update so the first entry is zero. Each step:

```text
e   = i_ref - i
v   = K_p*e + z                      # z is the integrator state
v_s = clip(v, -v_max, +v_max)        # or v itself when v_max is None
if v_s == v:  z += dt * K_i * e      # conditional integration: the anti-windup
i  += dt * (v_s - R*i) / L
```

That `if` is the whole of the anti-windup scheme. Leave it out and the integrator
charges up while the inverter is clipped, then has to be discharged by an error of
the opposite sign — which is overshoot you did not ask for.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def pi_gains(R, L, bw):
    """Return (K_p, K_i) for a closed-loop bandwidth of `bw` rad/s."""
    # TODO: two lines, straight from the derivation.
    return 0.0, 0.0


def step_response(R, L, bw, i_ref, dt, steps, v_max=None):
    """Forward-Euler the PI loop and return the current at every step."""
    K_p, K_i = pi_gains(R, L, bw)
    i = 0.0
    z = 0.0
    out = []
    # TODO: record i, form the error, clip the voltage, integrate conditionally,
    # then advance the current by one Euler step.
    return out


if __name__ == "__main__":
    print("gains:", pi_gains(0.45, 0.0035, 2000.0))
    ys = step_response(0.45, 0.0035, 2000.0, 10.0, 1e-6, 10000)
    print("samples:", len(ys))
    if ys:
        print("final current:", round(ys[-1], 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def pi_gains(R, L, bw):
    """Return (K_p, K_i) for a closed-loop bandwidth of `bw` rad/s."""
    return bw * L, bw * R


def step_response(R, L, bw, i_ref, dt, steps, v_max=None):
    """Forward-Euler the PI loop and return the current at every step."""
    K_p, K_i = pi_gains(R, L, bw)
    i = 0.0
    z = 0.0
    out = []
    for _ in range(steps):
        out.append(i)
        e = i_ref - i
        v = K_p * e + z
        if v_max is None:
            v_s = v
        else:
            v_s = max(-v_max, min(v_max, v))
        if v_s == v:
            z += dt * K_i * e
        i = i + dt * (v_s - R * i) / L
    return out


if __name__ == "__main__":
    print("gains:", pi_gains(0.45, 0.0035, 2000.0))
    ys = step_response(0.45, 0.0035, 2000.0, 10.0, 1e-6, 10000)
    print("samples:", len(ys))
    if ys:
        print("final current:", round(ys[-1], 6))
'''}],
                "hints": [
                    "`pi_gains` is `return bw * L, bw * R` — the inductance sets the proportional gain, the resistance the integral one.",
                    "Append the current to `out` first, then update. The check on the first sample depends on it.",
                    "`v_s == v` is a legitimate float comparison here: when the clip does nothing it returns the identical object, so the test is exact.",
                ],
                "tests": [
                    {"name": "the gains follow the cancellation rule", "code": r'''
_kp, _ki = pi_gains(0.45, 0.0035, 2000.0)
assert abs(_kp - 7.0) < 1e-12, f"K_p should be bw*L = 7.0, got {_kp}"
assert abs(_ki - 900.0) < 1e-12, f"K_i should be bw*R = 900.0, got {_ki}"
_kp2, _ki2 = pi_gains(2.0, 0.5, 10.0)
assert abs(_kp2 - 5.0) < 1e-12 and abs(_ki2 - 20.0) < 1e-12, \
    f"the rule is not specific to one machine; expected (5.0, 20.0), got ({_kp2}, {_ki2})"
'''},
                    {"name": "the PI zero lands on the plant pole", "code": r'''
_kp, _ki = pi_gains(0.45, 0.0035, 2000.0)
assert _kp > 0.0, "a zero proportional gain cancels nothing"
assert abs(_ki / _kp - 0.45 / 0.0035) < 1e-9, \
    f"K_i/K_p should equal R/L = {0.45 / 0.0035}, got {_ki / _kp}"
'''},
                    {"name": "the unlimited response is the first-order lag it was designed to be", "code": r'''
import numpy as np
_ys = step_response(0.45, 0.0035, 2000.0, 10.0, 1e-6, 10000)
assert len(_ys) == 10000, f"expected 10000 samples, got {len(_ys)}"
assert abs(_ys[0]) < 1e-12, f"the current starts at zero, got {_ys[0]}"
_k = int((1.0 / 2000.0) / 1e-6)
_want = 10.0 * (1.0 - np.exp(-1.0))
assert abs(_ys[_k] - _want) < 0.02, \
    f"one time constant in, the current should be {_want:.4f} A, got {_ys[_k]:.4f}"
assert abs(_ys[-1] - 10.0) < 1e-4, f"it should settle on the reference 10.0, got {_ys[-1]}"
'''},
                    {"name": "a first-order lag does not overshoot", "code": r'''
_ys = step_response(0.45, 0.0035, 2000.0, 10.0, 1e-6, 10000)
assert max(_ys) <= 10.0 + 1e-6, \
    f"the design has one real pole, so nothing should exceed the reference; peak was {max(_ys)}"
assert min(_ys) >= -1e-9, f"and nothing should go negative; minimum was {min(_ys)}"
'''},
                    {"name": "doubling the bandwidth halves the rise", "code": r'''
_slow = step_response(0.45, 0.0035, 1000.0, 10.0, 1e-6, 10000)
_fast = step_response(0.45, 0.0035, 2000.0, 10.0, 1e-6, 10000)
_ks = int((1.0 / 1000.0) / 1e-6)
_kf = int((1.0 / 2000.0) / 1e-6)
assert abs(_slow[_ks] - _fast[_kf]) < 0.02, \
    ("both loops should be at the same fraction of the reference after one of their own "
     f"time constants; got {_slow[_ks]:.4f} and {_fast[_kf]:.4f}")
assert _fast[_kf] > _slow[_kf] + 1.0, \
    "at the same wall-clock instant the faster loop must be further along"
'''},
                    {"name": "conditional integration keeps a clipped loop from overshooting", "code": r'''
_free = step_response(0.45, 0.0035, 2000.0, 10.0, 1e-6, 10000)
_clip = step_response(0.45, 0.0035, 2000.0, 10.0, 1e-6, 10000, v_max=20.0)
assert len(_clip) == 10000, f"expected 10000 samples, got {len(_clip)}"
_kt = int((1.0 / 2000.0) / 1e-6)
assert _clip[_kt] < _free[_kt] - 1.0, \
    ("a 20 V clip must slow the rise; unclipped reached "
     f"{_free[_kt]:.3f} A and clipped {_clip[_kt]:.3f} A at the same instant")
assert max(_clip) <= 10.0 + 1e-6, \
    f"with conditional integration there is no windup and so no overshoot; peak was {max(_clip)}"
assert _clip[-1] > 9.5, \
    f"and it must still be converging on the reference; ended at {_clip[-1]:.4f} A"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "read": [
                {
                    "title": "Fifty-four microseconds of nothing, and the fifteen per cent it hides",
                    "minutes": 17,
                    "body": r'''
Put a logic analyser on the six gate signals of the inverter driving the same machine at
the same operating point — 800 electrical rad/s, $i_d = 0$, $i_q = 8$ A — and capture one
100 µs period. The regulator is asking for 79.78 V, at an angle advancing $4.6°$ per
period; take the instant when it sits midway between two of the inverter's own vectors:

```text
000  13.5 us     all legs low: the machine shorted to the negative rail
100  11.5 us     an active vector
110  11.5 us     the next one round
111  27.0 us     all legs high: shorted to the positive rail
110  11.5 us
100  11.5 us
000  13.5 us
```

Twenty-three microseconds on each of two active states, and 53.9 µs — fifty-four per cent
of the period — with all three terminals tied to one rail and no voltage vector produced at
all. That is neither fault nor waste: it is how a device with eight possible outputs
produces an arbitrary one.

## Eight states, six of them useful

Each leg is one bit, so there are $2^3 = 8$ switch states. Take (1,0,0): phase $a$ on the
positive rail, $b$ and $c$ on the negative. The floating star point sits at the average of
the three terminal voltages, $V_{dc}/3 = 100$ V, making the line-to-neutral voltages
$+200$, $-100$, $-100$ V. Push those through module 1's Clarke transform:

$$v_\alpha = \tfrac{2}{3}\left(200 + 50 + 50\right) = 200\ \text{V},
\qquad v_\beta = \frac{-100 - (-100)}{\sqrt3} = 0$$

A vector of length $\tfrac{2}{3}V_{dc}$ along $\alpha$. The other five active states are
that construction rotated: six vectors of 200 V at $60°$ spacing, the vertices of a regular
hexagon. The remaining two, (0,0,0) and (1,1,1), tie every terminal to the same potential
and so give the zero vector twice over.

## Averaging, and where the dwell formulae come from

The machine is an inductor and cannot follow a 200 V jump in vector position, so what
reaches it over one period is the average. Demand that the average equal the reference:

$$\frac{t_1 \vec{V}_1 + t_2 \vec{V}_2 + t_0 \cdot \vec{0}}{T_s} = \vec{v}_{ref}$$

With $\vec{V}_1$ along $\alpha$, $\vec{V}_2$ at $60°$ and $\vec{v}_{ref} = m\angle\theta$
within the sector, the components read

$$m\cos\theta = \frac{2V_{dc}}{3T_s}\left(t_1 + \tfrac{1}{2}t_2\right), \qquad
  m\sin\theta = \frac{2V_{dc}}{3T_s}\cdot\frac{\sqrt3}{2}\,t_2$$

Solving the second for $t_2$ and back-substituting gives the pair the lab
*Dwell times, the linear limit, and the weakening command* asks you to implement:

$$t_1 = \frac{\sqrt3\,m\,T_s}{V_{dc}}\sin\!\left(\tfrac{\pi}{3} - \theta\right), \qquad
  t_2 = \frac{\sqrt3\,m\,T_s}{V_{dc}}\sin\theta, \qquad t_0 = T_s - t_1 - t_2$$

Now ask what constrains $m$. Nothing in the formulae stops $t_1 + t_2$ exceeding $T_s$, but
there is no more time in the period. Their sum is
$g\left(\sin(\tfrac{\pi}{3}-\theta) + \sin\theta\right)$, whose bracket differentiates to a
maximum at $\theta = \tfrac{\pi}{6}$, mid-sector, where it equals exactly 1. The binding
condition is therefore $g \le T_s$:

$$\frac{\sqrt3\,m\,T_s}{V_{dc}} \le T_s \quad\Longrightarrow\quad m \le \frac{V_{dc}}{\sqrt3} = 173.2\ \text{V}$$

The inscribed circle is not geometry bolted onto the algebra; it is where the zero time
runs out, mid-sector first. The lab's fourth test checks that: on the circle at mid-sector,
$t_1 = t_2 = T_s/2$ and $t_0 = 0$.

```python
import math

V_DC, T_S = 300.0, 1e-4
R, LD, LQ, LAM = 0.45, 0.0035, 0.0055, 0.085
W_E, i_d, i_q = 800.0, 0.0, 8.0

v_d = R * i_d - W_E * LQ * i_q
v_q = R * i_q + W_E * (LD * i_d + LAM)
m = math.hypot(v_d, v_q)
v_max = V_DC / math.sqrt(3.0)
print("reference %.2f V, %.1f%% of the %.1f V inscribed circle" % (m, 100.0 * m / v_max, v_max))

g = math.sqrt(3.0) * m * T_S / V_DC
for deg in (0.0, 30.0):
    th = math.radians(deg)
    t1 = g * math.sin(math.pi / 3.0 - th)
    t2 = g * math.sin(th)
    print("%4.0f deg into the sector: t1 %5.2f us, t2 %5.2f us, t0 %5.2f us (%4.1f%% of the period)"
          % (deg, t1 * 1e6, t2 * 1e6, (T_S - t1 - t2) * 1e6, 100.0 * (T_S - t1 - t2) / T_S))

t0 = T_S - g * math.sin(math.pi / 6.0) * 2.0
slope = (0.0 - R * i_q - W_E * (LD * i_d + LAM)) / LQ
print("during the central zero state, %.2f us long, di_q/dt = %.0f A/s" % (0.5 * t0 * 1e6, slope))
print("so i_q falls %.4f A, which is %.2f%% of the 8 A it is holding" % (abs(slope) * 0.5 * t0, 100.0 * abs(slope) * 0.5 * t0 / i_q))
```

The zero time sets the magnitude. A reference at 46 per cent of the circle spends 54 to 60
per cent of every period producing nothing, which is how a 200 V vector averages down to
79.8 V. The cost is ripple: during the long central zero state the machine sees no applied
voltage, so its back-EMF and resistance discharge the current at 13018 A/s — 0.351 A over
26.97 µs, 4.4 per cent of the 8 A it is holding. A lower modulation index lengthens $t_0$,
so ripple is worst at low speed and light load.

## The fifteen per cent, and what it really is

Sine-triangle modulation with no injection compares each phase reference against a carrier,
so it reaches a phase-voltage peak of $V_{dc}/2 = 150$ V. Space-vector modulation reaches
$V_{dc}/\sqrt3 = 173.2$ V. The ratio is

$$\frac{V_{dc}/\sqrt3}{V_{dc}/2} = \frac{2}{\sqrt3} = 1.1547$$

Fifteen per cent more voltage is fifteen per cent more speed from the same battery for a
change in software alone. Where does the extra come from, when neither machine nor bus has
changed?

From the star point. With no neutral wire only differences between terminals drive current,
so the same voltage added to all three legs is invisible to the machine. Splitting $t_0$
between (0,0,0) and (1,1,1) rather than spending it all on one is exactly such an addition,
expressed in the time domain, and its waveform is the min–max wave
$-\tfrac{1}{2}(\max + \min)$ of the three references: a triangle at three times the
fundamental, peaking at a quarter of the reference amplitude. Add it and the largest
excursion any phase makes is $\tfrac{\sqrt3}{2}A$ rather than $A$, reached where the
injection crosses zero. Setting $\tfrac{\sqrt3}{2}A = V_{dc}/2$ returns $A = V_{dc}/\sqrt3$
— the same number, from an argument with no hexagon in it.

The two are not merely equivalent at their limit. They are the same modulator:

```python
import math

V_DC, T_S = 300.0, 1e-4
STATES = [(1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 1, 1), (0, 0, 1), (1, 0, 1)]


def svm_duties(m, th):
    # build the seven-segment gate pattern, then measure each leg's on-time
    th %= 2.0 * math.pi
    k = int(th // (math.pi / 3.0))
    g = math.sqrt(3.0) * m * T_S / V_DC
    inner = th - k * (math.pi / 3.0)
    t1, t2 = g * math.sin(math.pi / 3.0 - inner), g * math.sin(inner)
    t0 = T_S - t1 - t2
    va, vb, z0, z7 = STATES[k], STATES[(k + 1) % 6], (0, 0, 0), (1, 1, 1)
    seq = [(z0, t0 / 4), (va, t1 / 2), (vb, t2 / 2), (z7, t0 / 2),
           (vb, t2 / 2), (va, t1 / 2), (z0, t0 / 4)]
    return [sum(st[leg] * dt for st, dt in seq) / T_S for leg in range(3)]


def carrier_duties(m, th):
    # three sinusoids, the min-max common mode, one comparator each
    v = [m * math.cos(th - leg * 2.0 * math.pi / 3.0) for leg in range(3)]
    cm = -0.5 * (max(v) + min(v))
    return [0.5 + (x + cm) / V_DC for x in v]


worst = max(max(abs(a - b) for a, b in zip(svm_duties(m, 2.0 * math.pi * i / 3600.0),
                                           carrier_duties(m, 2.0 * math.pi * i / 3600.0)))
            for i in range(3600) for m in (40.0, 79.785, 150.0, 173.205))
print("worst duty disagreement over 3600 angles and 4 magnitudes: %.2e" % worst)
th = math.radians(25.0)
print("space vector   : %s" % [round(x, 6) for x in svm_duties(79.785, th)])
print("min-max carrier: %s" % [round(x, 6) for x in carrier_duties(79.785, th)])
```

Across 3600 angles and four magnitudes they disagree by 6.66e-16 — arithmetic, not method.

## The mistake, and why it is tempting

The mistake is believing the 15 per cent is bought by the vector geometry — that the
hexagon, the sector arithmetic and the dwell times produce it, and that a carrier modulator
cannot reach the same limit. It is tempting because SVM is taught as geometry, the six
states are visibly a resource being allocated, and the split of $t_0$ looks like a freedom
only vectors expose. The conclusion is wrong: three comparators and one line of common-mode
arithmetic reproduce the same gate pattern to fifteen decimal places.

The cost is real: a modulator written as sector lookup, angle arithmetic and two sine
evaluations per period is several times the work of three comparisons, with sector-boundary
cases to get wrong. What the hexagon gives is not the limit but the picture of why the
limit is what it is.

## Above base speed, the voltage runs out

At 800 rad/s the reference is 79.8 V against 173.2 V available. Raise the speed at the same
8 A and $\omega_e\lambda_m$ grows linearly while the budget does not. The derive unit *The
inscribed circle, the 15 per cent, and where field weakening starts* puts the no-load
crossing at $V_{max}/\lambda_m = 2038$ rad/s; under load it comes earlier, since
$\omega_e L_q i_q$ claims part of the same budget — at 8 A the vector reaches 173.2 V by
1776 rad/s.

The way out is the $\omega_e(L_di_d + \lambda_m)$ term. Negative $i_d$ subtracts from the
magnet's flux and the $q$-axis demand falls with it. Choose $i_d$ so the demand lands on a
chosen fraction of the budget, and the ledger is this:

```python
import math

R, LD, LQ, LAM, PP = 0.45, 0.0035, 0.0055, 0.085, 4
V_MAX, I_MAX, FW = 300.0 / math.sqrt(3.0), 20.0, 0.95
w_e, i_q = 2500.0, 8.0

demand = lambda d: math.hypot(R * d - w_e * LQ * i_q, R * i_q + w_e * (LD * d + LAM))
torque = lambda d: 1.5 * PP * (LAM * i_q + (LD - LQ) * d * i_q)
copper = lambda d: 1.5 * R * (d * d + i_q * i_q)

i_d = (math.sqrt((FW * V_MAX / w_e) ** 2 - (LQ * i_q) ** 2) - LAM) / LD
for label, cur in (("i_d = 0", 0.0), ("weakened", i_d)):
    print("%-9s i_d %7.3f A  |v| %6.2f V of %.2f  T %.3f Nm  |i| %5.2f A of %.0f  copper %6.2f W"
          % (label, cur, demand(cur), V_MAX, torque(cur), math.hypot(cur, i_q), I_MAX, copper(cur)))
print("shaft %.0f W at %.0f mech rad/s; the copper is %.1f%% of it"
      % (torque(i_d) * w_e / PP, w_e / PP, 100.0 * copper(i_d) * PP / (torque(i_d) * w_e)))
```

At 2500 rad/s with $i_d = 0$ the machine demands 242.49 V from a modulator that can make
173.21 — 40 per cent over, so the loop clips, the current collapses and the torque goes
negative, which the capstone's last test asserts. Commanding $i_d = -10.300$ A brings the
demand to 170.32 V and raises the copper loss from 43.20 W to 114.81 W. Note what the
margin buys: the law sets the *flux* term to 164.54 V and the vector arrives at 170.32 V,
because it ignores the $Ri_d$ and $Ri_q$ drops. Those 5 per cent absorb them; without them
the loop sits permanently against the limiter.

The surprise is the torque column. The same 8 A of $i_q$ makes 5.069 N·m weakened against
4.080 N·m at $i_d = 0$ — 24 per cent more — because on a salient rotor the $-10.3$ A earns
reluctance torque on its way past. Field weakening here is not purely a tax. And 114.81 W
of copper is 3.6 per cent of the 3168 W now leaving the shaft, against 5.3 per cent at the
module 1 point: less efficient per amp, more efficient overall.

## Where it stops holding

**Outside the inscribed circle.** Push past 173.2 V and $t_1 + t_2$ exceeds $T_s$ at some
angles and not others, so the achievable magnitude becomes a function of direction: a
circular reference is flattened at the hexagon's corners, the current takes on fifth and
seventh harmonics in the phases and a sixth in $dq$, and the linearity the current loop was
designed around is gone. The far end of that road is six-step operation, at
$2V_{dc}/\pi = 190.99$ V of fundamental peak — 10.3 per cent past the circle, all of it
bought with distortion.

**Dead time.** The two devices in a leg must never conduct together, so each transition
carries a gap of a microsecond or two in which the current's sign, not the gate signal,
decides the output. One microsecond of 100 is a volt-second error of
$V_{dc}t_d/T_s = 3.0$ V per leg, signed by the current, so it enters as sixth-harmonic
distortion in $dq$. Three volts is 3.8 per cent of the 79.8 V commanded at 800 rad/s and
23 per cent of the 12.9 V commanded at 100 rad/s: at low speed, dead-time compensation is
the difference between a controllable drive and one that will not start smoothly. Near a
vertex $t_2$ vanishes too, and no device switches in 200 ns, so modulators drop or stretch
those pulses.

**A period is not an instant.** Everything here treats $\omega_e$ as fixed over $T_s$. At
2500 rad/s one period is 0.25 rad, $14.3°$ of rotation, so a reference computed at the start
of a period points $14.3°$ wrong by its end; implementations rotate it forward by half a
period to split the error. A stale angle is a stale feedforward, which is the residual the
sandbox *What the decoupling feedforward fails to cancel* draws — take its off-diagonal
entries to $\pm 3$ and the closed loop spirals rather than settling. Its conclusion is the
one to keep: raise the loop bandwidth rather than refine the decoupling algebra, because a
residual is a disturbance and disturbances are what loop gain is for.

**The weakening law is thin.** It ignores the resistive drops, which the 0.95 margin covers,
and holds $L_d$ constant while the machine saturates. Above 3380 rad/s at 8 A the current
circle binds first, the command clamps at $-18.33$ A, and the $q$-axis reference can no
longer be held: the drive is on the constant-power hyperbola, where torque falls with speed
whatever the controller does.

## What you are about to build

The lab checks every claim above against itself — the sector numbering, dwell times filling
exactly one period with none negative at any of 52 angles, $t_0 = 0$ mid-sector on the
inscribed circle, $t_1 = T_s$ at a vertex, and a weakening command silent below base speed,
on the ellipse above it, clamped on the current circle far above. The capstone then runs
the whole course as one loop at 800 and 2500 rad/s.
''',
                },
            ],
            "title": "Space-vector modulation and field weakening",
            "summary": "The inverter has six useful states. Using them properly buys 15 per cent of bus voltage, and beyond base speed you spend d-axis current to buy the rest.",
            "concepts": [
                "Six active switch states plus two zero states. In $\\alpha\\beta$ the active ones are vectors of length $\\tfrac{2}{3}V_{dc}$ at 60° spacing — the vertices of a hexagon.",
                "Any reference inside the hexagon is synthesised by time-averaging its two neighbouring vertices: $t_1$, $t_2$ and the remainder $t_0$ on the zero states.",
                "Linear operation needs the reference inside the *inscribed circle*, of radius $V_{dc}/\\sqrt{3}$ — against $V_{dc}/2$ for naive sine-triangle modulation. The ratio is $2/\\sqrt{3} = 1.1547$.",
                "Splitting $t_0$ evenly between the two zero states is what shifts the common mode. The shift it produces is the min–max wave, $-\\tfrac{1}{2}(\\max + \\min)$ of the three references: a triangle at three times the fundamental whose peak is one quarter of the reference amplitude. It reaches the same $2/\\sqrt{3}$ linear range as a sinusoidal third harmonic injected at one sixth, but it is not that waveform.",
                "Above base speed the back-EMF alone fills the voltage budget. Negative $i_d$ opposes the magnet flux and buys headroom back, bounded by the current circle $i_d^2 + i_q^2 \\le I_{max}^2$.",
            ],
            "sandbox": {
                "title": "What the decoupling feedforward fails to cancel",
                "visualiser": "phase-portrait",
                "minutes": 9,
                "initial": {"a11": -2, "a12": 1.5, "a21": -1.5, "a22": -2},
                "brief": r'''
Same axes as before — $x_1$ is $i_d$, $x_2$ is $i_q$ — but this is the *closed* loop,
$A - BK$, in normalised units. The diagonal is now the tuned current-loop bandwidth
rather than $R/L$, and the off-diagonal pair is whatever cross-coupling the
feedforward did not cancel: a stale flux estimate, a sample of computational delay,
an inductance that has saturated.
''',
                "notice": [
                    "Set both off-diagonals to zero — perfect decoupling. The trajectories straighten into radial lines and the readout says **stable node**: two independent first-order loops, exactly what the tuning assumed.",
                    "Take $a_{12}$ to 3 and $a_{21}$ to $-3$, a residual you can easily have at high speed. The classification flips to **stable spiral** and the currents make rather more than a full turn on the way in: a $d$-axis step now disturbs $q$, and therefore disturbs the torque.",
                    "Leave the coupling at $\\pm 3$ and raise the bandwidth instead, dragging $a_{11}$ and $a_{22}$ to the far end of their sliders, $-3$ and $-4$. The spiral tightens back towards a straight line: the turn count roughly halves, from about one and an eighth to about six tenths. A faster loop rejects the coupling it cannot cancel, which is why current-loop bandwidth, not the decoupling algebra, is the thing that has to scale with speed.",
                ],
            },
            "derive": {
                "title": "The inscribed circle, the 15 per cent, and where field weakening starts",
                "minutes": 15,
                "vars": ["V_dc", "V_max", "omega", "omega_b", "lambda_m", "L_d", "i_d", "i_q", "I_max"],
                "brief": r'''
The six active vectors of a two-level inverter have length $\frac{2}{3}V_{dc}$ and
sit 60° apart, so their tips are the vertices of a regular hexagon. A reference can
be synthesised without distortion only if it stays inside that hexagon for every
angle — that is, inside the largest circle the hexagon contains.
''',
                "steps": [
                    {
                        "prompt": "The inscribed circle touches the middle of each side. Its radius is the vertex radius times the cosine of half the 60° between vertices. Write that radius in terms of $V_{dc}$.",
                        "given": "The vertex radius is $\\frac{2}{3}V_{dc}$, and $\\cos 30^\\circ = \\frac{\\sqrt{3}}{2}$.",
                        "answer": "\\frac{V_dc}{\\sqrt{3}}",
                        "hint": "Multiply $\\frac{2}{3}V_{dc}$ by $\\frac{\\sqrt{3}}{2}$ and tidy the result.",
                        "deconstruct": [
                            "$\\frac{2}{3}V_{dc} \\cdot \\frac{\\sqrt{3}}{2} = \\frac{V_{dc}\\sqrt{3}}{3}$.",
                            "And $\\frac{\\sqrt{3}}{3} = \\frac{1}{\\sqrt{3}}$.",
                        ],
                    },
                    {
                        "prompt": "Sine-triangle modulation with no injection is limited to a phase-voltage peak of $\\frac{V_{dc}}{2}$. Write the ratio of the space-vector limit to that one.",
                        "answer": "\\frac{2}{\\sqrt{3}}",
                        "hint": "Divide the previous answer by $\\frac{V_{dc}}{2}$ and let the bus voltage cancel.",
                        "deconstruct": [
                            "$\\frac{V_{dc}/\\sqrt{3}}{V_{dc}/2} = \\frac{2}{\\sqrt{3}}$.",
                            "Numerically that is 1.1547 — the 15 per cent everyone quotes.",
                        ],
                    },
                    {
                        "prompt": "Call the inscribed radius $V_{max}$. At speed $\\omega$ with no current flowing at all, the machine already demands $\\omega\\lambda_m$ of it. Write the speed $\\omega_b$ at which that demand exactly exhausts the budget, in terms of $V_{dc}$ and $\\lambda_m$.",
                        "answer": "\\frac{V_dc}{\\sqrt{3}\\lambda_m}",
                        "hint": "Set $\\omega \\lambda_m = V_{max}$ and substitute the $V_{max}$ you found in the first step.",
                        "deconstruct": [
                            "$\\omega_b \\lambda_m = V_{max} = V_{dc}/\\sqrt{3}$.",
                            "Divide by $\\lambda_m$.",
                        ],
                    },
                    {
                        "prompt": "Above $\\omega_b$ the only way to keep operating is to reduce the flux. Ignoring the resistive drop, the $q$-axis voltage is $\\omega(L_d i_d + \\lambda_m)$. Write the $i_d$ that makes that exactly equal to $V_{max}$.",
                        "answer": "\\frac{V_max - \\omega\\lambda_m}{\\omega L_d}",
                        "hint": "Set $\\omega(L_d i_d + \\lambda_m) = V_{max}$ and solve for $i_d$ — one division and one subtraction.",
                        "deconstruct": [
                            "$L_d i_d + \\lambda_m = V_{max}/\\omega$.",
                            "So $i_d = \\left(V_{max}/\\omega - \\lambda_m\\right)/L_d$, which is the same expression over the common denominator $\\omega L_d$.",
                        ],
                    },
                ],
                "closing": r'''
Below $\omega_b$ that expression is positive, which would mean *strengthening* the
field: the command has to be clamped at zero, or at the MTPA point on a salient
machine. Above $\omega_b$ it goes negative and keeps going, so the second clamp
matters as much as the first — $i_d$ is bounded below by the current circle,
$i_d \ge -\sqrt{I_{max}^2 - i_q^2}$, and past the speed where those two bounds meet
there is no torque left to command.
''',
            },
            "quiz": {
                "title": "Six states, and what to do past base speed",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A three-phase inverter has how many *active* switch states?",
                        "opts": ["Six", "Eight", "Three", "Twelve"],
                        "a": 0,
                        "why": r"""
Eight states in total — $2^3$, one bit per leg — of which six put a non-zero voltage
vector on the machine and two short all three phases together, to the top rail or the
bottom. Those two zero states are not wasted: they are how the modulator sets the
*magnitude* of the average vector, by spending part of the period producing nothing.
""",
                    },
                    {
                        "q": "How is a reference vector between two active states produced?",
                        "opts": [
                            "By time-averaging the two neighbouring active vectors and the zero states over one period",
                            "By switching to the nearest active vector only",
                            "By adding a third harmonic to the reference",
                            "By reducing the bus voltage",
                        ],
                        "a": 0,
                        "why": r"""
The inverter can only ever produce one of eight vectors, so the reference is synthesised
*on average*: spend $t_1$ in one neighbour, $t_2$ in the other, and the remainder in a
zero state. The machine's inductance does the averaging, which connects directly back to
module 3 — the winding is the filter that makes this legitimate.
""",
                    },
                    {
                        "q": "For linear operation, where must the reference vector stay?",
                        "opts": [
                            "Inside the circle inscribed in the hexagon",
                            "Inside the hexagon",
                            "On the hexagon's boundary",
                            "Anywhere, since the modulator saturates gracefully",
                        ],
                        "a": 0,
                        "why": r"""
The hexagon is the set of averages the inverter can reach, but only the inscribed circle
of radius $V_{dc}/\sqrt{3}$ can be reached at *every angle*. Push beyond it and the
achievable magnitude depends on where the vector is pointing, so a circular reference gets
flattened at the corners and the current acquires low-order harmonics. That is
overmodulation: usable, sometimes deliberate, and no longer linear.
""",
                    },
                    {
                        "q": "How much more bus voltage does space-vector modulation use than sinusoidal PWM?",
                        "opts": ["About 15%", "About 50%", "About 5%", "None — the two are equivalent"],
                        "a": 0,
                        "why": r"""
$2/\sqrt{3} = 1.155$. Sinusoidal PWM limits each phase to $V_{dc}/2$, while SVM reaches
$V_{dc}/\sqrt{3}$, because the zero states can be distributed to shift all three phases
together — a common-mode offset the machine cannot see, since with no neutral connection
only differences matter. Fifteen per cent more voltage is fifteen per cent more speed
from the same battery, for a change in software alone.
""",
                    },
                    {
                        "q": "Past base speed the back-EMF exceeds what the bus can supply. What does field weakening do?",
                        "opts": [
                            "Injects negative $i_d$ to oppose the magnet flux",
                            "Injects positive $i_d$ to reinforce it",
                            "Reduces $i_q$ until the voltage fits",
                            "Raises the switching frequency",
                        ],
                        "a": 0,
                        "why": r"""
Negative $i_d$ makes $L_di_d$ subtract from $\lambda_m$, shrinking the total d-axis flux
and with it the back-EMF, so the machine keeps accelerating on the same bus. It is not
free: that current produces no torque and full $I^2R$ loss, and the available $i_q$
shrinks because the total current is limited. Reducing $i_q$ would also fit the voltage —
by giving up the torque, which is the thing you were trying to keep.
""",
                    },
                ],
            },
            "lab": {
                "title": "Dwell times, the linear limit, and the weakening command",
                "runtime": "python",
                "minutes": 34,
                "brief": r'''
Four functions.

`sector(v_alpha, v_beta)` returns the 60° sector, numbered 1 to 6 anticlockwise from
the positive $\alpha$ axis. Sector 1 is $[0°, 60°)$.

`dwell(v_alpha, v_beta, v_dc, t_s)` returns `(t1, t2, t0)`: the time on the vertex at
the *start* of the sector, the time on the vertex at its *end*, and the remainder on
the zero states, over one period `t_s`. So `t1` belongs to the vector the reference
has already swept past and `t2` to the one it is heading towards. With
`th` the angle *within* the sector and `m` the reference magnitude:

```text
g  = sqrt(3) * m * t_s / v_dc
t1 = g * sin(pi/3 - th)
t2 = g * sin(th)
t0 = t_s - t1 - t2
```

`linear_radius(v_dc)` returns the inscribed-circle radius.

`weakening_id(v_max, w_e, lam, L_d, i_max)` returns the $d$-axis command: zero at or
below base speed, the flux-matching value above it, and never below `-i_max`. Return
zero for `w_e <= 0`.
''',
                "files": [{"name": "main.py", "content": r'''
import numpy as np


def sector(v_alpha, v_beta):
    """Return the 60-degree sector, 1 to 6, of the reference vector."""
    # TODO: np.arctan2, wrapped into [0, 2*pi), divided by pi/3.
    return 0


def dwell(v_alpha, v_beta, v_dc, t_s):
    """Return (t1, t2, t0) for one modulation period."""
    # TODO: angle within the sector, then the two sine formulae.
    return 0.0, 0.0, 0.0


def linear_radius(v_dc):
    """Radius of the largest circle inscribed in the hexagon."""
    # TODO
    return 0.0


def weakening_id(v_max, w_e, lam, L_d, i_max):
    """The d-axis current command: zero below base speed, negative above it."""
    # TODO: clamp at zero above, at -i_max below.
    return 0.0


if __name__ == "__main__":
    print("linear radius on a 300 V bus:", round(linear_radius(300.0), 6))
    print("sector of (1, 0):", sector(1.0, 0.0))
    print("dwell:", [round(t, 9) for t in dwell(150.0, 20.0, 300.0, 1e-4)])
    print("i_d at 2500 rad/s:", round(weakening_id(linear_radius(300.0), 2500.0, 0.085, 0.0035, 20.0), 6))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import numpy as np


def sector(v_alpha, v_beta):
    """Return the 60-degree sector, 1 to 6, of the reference vector."""
    th = np.arctan2(v_beta, v_alpha) % (2.0 * np.pi)
    return int(th // (np.pi / 3.0)) + 1


def dwell(v_alpha, v_beta, v_dc, t_s):
    """Return (t1, t2, t0) for one modulation period."""
    th = np.arctan2(v_beta, v_alpha) % (2.0 * np.pi)
    k = int(th // (np.pi / 3.0))
    inner = th - k * (np.pi / 3.0)
    m = float(np.hypot(v_alpha, v_beta))
    g = np.sqrt(3.0) * m * t_s / v_dc
    t1 = float(g * np.sin(np.pi / 3.0 - inner))
    t2 = float(g * np.sin(inner))
    return t1, t2, float(t_s - t1 - t2)


def linear_radius(v_dc):
    """Radius of the largest circle inscribed in the hexagon."""
    return float(v_dc / np.sqrt(3.0))


def weakening_id(v_max, w_e, lam, L_d, i_max):
    """The d-axis current command: zero below base speed, negative above it."""
    if w_e <= 0.0:
        return 0.0
    need = (v_max / w_e - lam) / L_d
    return float(min(0.0, max(need, -i_max)))


if __name__ == "__main__":
    print("linear radius on a 300 V bus:", round(linear_radius(300.0), 6))
    print("sector of (1, 0):", sector(1.0, 0.0))
    print("dwell:", [round(t, 9) for t in dwell(150.0, 20.0, 300.0, 1e-4)])
    print("i_d at 2500 rad/s:", round(weakening_id(linear_radius(300.0), 2500.0, 0.085, 0.0035, 20.0), 6))
'''}],
                "hints": [
                    "`np.arctan2(v_beta, v_alpha) % (2*np.pi)` gives an angle in $[0, 2\\pi)$; integer-dividing by $\\pi/3$ gives 0 to 5, so add one.",
                    "The angle *within* the sector is the total angle minus `k * pi/3`, and it runs from 0 to $\\pi/3$. Both sine arguments are then in the first quadrant, so both dwell times come out non-negative.",
                    "`weakening_id` needs two clamps: `min(0.0, ...)` stops it strengthening the field below base speed, and `max(..., -i_max)` stops it exceeding the drive's rating.",
                ],
                "tests": [
                    {"name": "the six sectors are numbered anticlockwise from the alpha axis", "code": r'''
import numpy as np
assert sector(1.0, 0.0) == 1, f"the positive alpha axis is the start of sector 1, got {sector(1.0, 0.0)}"
assert sector(0.0, 1.0) == 2, f"90 degrees is in sector 2, got {sector(0.0, 1.0)}"
assert sector(-1.0, 1.0) == 3, f"135 degrees is in sector 3, got {sector(-1.0, 1.0)}"
assert sector(-1.0, 0.0) == 4, f"180 degrees is in sector 4, got {sector(-1.0, 0.0)}"
assert sector(0.0, -1.0) == 5, f"270 degrees is in sector 5, got {sector(0.0, -1.0)}"
assert sector(0.5, -0.5 * np.sqrt(3.0)) == 6, \
    f"-60 degrees wraps to 300 and is in sector 6, got {sector(0.5, -0.5 * np.sqrt(3.0))}"
'''},
                    {"name": "the linear limit beats sine-triangle by two over root three", "code": r'''
import numpy as np
_r = linear_radius(300.0)
assert abs(_r - 173.20508075688775) < 1e-9, \
    f"the inscribed radius on a 300 V bus is 173.2051 V, got {_r}"
assert abs(_r / 150.0 - 2.0 / np.sqrt(3.0)) < 1e-12, \
    f"the advantage over V_dc/2 should be {2.0 / np.sqrt(3.0)}, got {_r / 150.0}"
'''},
                    {"name": "the dwell times fill exactly one period and none is negative", "code": r'''
import numpy as np
_ts = 1e-4
_r = 0.9 * 173.20508075688775
for _deg in range(0, 360, 7):
    _th = np.deg2rad(_deg)
    _t1, _t2, _t0 = dwell(_r * np.cos(_th), _r * np.sin(_th), 300.0, _ts)
    assert abs(_t1 + _t2 + _t0 - _ts) < 1e-15, \
        f"at {_deg} degrees the three times should sum to t_s; they summed to {_t1 + _t2 + _t0}"
    assert min(_t1, _t2, _t0) > -1e-15, \
        f"at {_deg} degrees a dwell time came out negative: {(_t1, _t2, _t0)}"
    assert _t1 + _t2 > 0.5 * _ts, \
        f"at {_deg} degrees the active vectors should carry most of the period, got {(_t1 + _t2) / _ts}"
'''},
                    {"name": "the inscribed circle is exactly where the zero time runs out", "code": r'''
import numpy as np
_ts = 1e-4
_r = 173.20508075688775
_th = np.pi / 6.0
_t1, _t2, _t0 = dwell(_r * np.cos(_th), _r * np.sin(_th), 300.0, _ts)
assert abs(_t1 - 0.5 * _ts) < 1e-12 and abs(_t2 - 0.5 * _ts) < 1e-12, \
    f"mid-sector on the inscribed circle the two vertices share the period equally, got {(_t1, _t2)}"
assert abs(_t0) < 1e-12, \
    f"and there is no time left for the zero vectors, got t0 = {_t0}"
'''},
                    {"name": "a vertex direction can be pushed all the way to two thirds of the bus", "code": r'''
_ts = 1e-4
_t1, _t2, _t0 = dwell(200.0, 0.0, 300.0, _ts)
assert abs(_t1 - _ts) < 1e-12, f"pointing straight at a vertex, t1 should be the whole period, got {_t1}"
assert abs(_t2) < 1e-12, f"the vertex at the end of the sector is unused, got t2 = {_t2}"
assert abs(_t0) < 1e-12, f"and nothing is left over, got t0 = {_t0}"
'''},
                    {"name": "the weakening command switches on at base speed and not before", "code": r'''
_vmax = 173.20508075688775
for _w in (0.0, 200.0, 1000.0, 2000.0):
    _id = weakening_id(_vmax, _w, 0.085, 0.0035, 20.0)
    assert _id == 0.0, f"at {_w} rad/s the budget is not exhausted, so i_d should be 0, got {_id}"
_just_over = weakening_id(_vmax, 2100.0, 0.085, 0.0035, 20.0)
assert _just_over < -0.5, \
    ("base speed is 2037.7 rad/s, so 2100 rad/s must already call for weakening; "
     f"expected below -0.5 A, got {_just_over}")
'''},
                    {"name": "above base speed it matches the flux to the budget", "code": r'''
_vmax = 173.20508075688775
for _w in (2500.0, 3000.0, 5000.0):
    _id = weakening_id(_vmax, _w, 0.085, 0.0035, 20.0)
    assert _id < 0.0, f"at {_w} rad/s the field must be weakened, got i_d = {_id}"
    assert abs(_w * (0.0035 * _id + 0.085) - _vmax) < 1e-6, \
        (f"at {_w} rad/s the weakened flux should use exactly the budget {_vmax}, "
         f"got {_w * (0.0035 * _id + 0.085)}")
_far = weakening_id(_vmax, 40000.0, 0.085, 0.0035, 20.0)
assert abs(_far + 20.0) < 1e-12, \
    f"far above base speed the current rating binds first, so i_d should clamp at -20, got {_far}"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A field-oriented current loop, from standstill into field weakening",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
Everything in the course, assembled into one current controller and run at two
operating points: comfortably below base speed, and well above it.

The machine is the four-pole-pair interior PMSM used throughout: `R = 0.45` Ω,
`L_d = 3.5` mH, `L_q = 5.5` mH, `λ_m = 85` mWb, a 300 V bus and a 20 A peak rating.
`machine.py` holds those numbers together with the plant derivative and the torque
equation. Do not edit it; the checks depend on it.

At $V_{max} = V_{dc}/\sqrt{3} = 173.2$ V the *no-load* base speed is
$V_{max}/\lambda_m = 2038$ electrical rad/s. Under load it is lower, because
$\omega_e L_q i_q$ claims a share of the same budget: at the 8 A reference the checks
use, the budget is gone by 1776 rad/s. Well below that the loop simply hits its
reference. Well above it, it cannot — unless you weaken the field.

Build, in `main.py`:

1. `pi_gains(R, L, bw)` — the two gains from module 3, used once per axis.
2. `decouple(w_e, i_d, i_q)` — the feedforward pair $(-\omega_e L_q i_q,\
   \omega_e(L_d i_d + \lambda_m))$, computed from the *measured* currents.
3. `limit_voltage(v_d, v_q, v_max)` — scale the vector down to `v_max` if it is
   longer, preserving direction. Vectors already inside are returned untouched.
4. `id_command(w_e, iq_ref)` — the field-weakening command, with the $q$-axis
   voltage drop budgeted for and a margin left for the resistive drop:

```text
budget = FW_MARGIN * v_limit()
room   = (budget/w_e)**2 - (LQ*iq_ref)**2
flux   = sqrt(room) if room > 0 else 0
i_d    = (flux - LAM) / LD
```

   then clamped above at 0 and below at $-\sqrt{I_{max}^2 - i_{q,ref}^2}$. Return 0
   for `w_e <= 0`.
5. `run(w_e, iq_ref, dt, steps, weaken=True)` — the loop itself, returning
   `(i_d list, i_q list)` recorded before each update.

## Suggested order

The checks are ordered to light up as you build: gains, then the feedforward, then
the limiter, then the command, then the two runs. Get `decouple` exactly right before
you touch `run` — a feedforward with one sign wrong looks like a tuning problem and
is not one.

## The loop, per step

```text
record i_d, i_q
e_d, e_q      = id_ref - i_d, iq_ref - i_q
ff_d, ff_q    = decouple(w_e, i_d, i_q)
v_d, v_q      = Kp_d*e_d + z_d + ff_d,  Kp_q*e_q + z_q + ff_q
s_d, s_q      = limit_voltage(v_d, v_q, v_limit())
if unclipped:   z_d += dt*Ki_d*e_d;  z_q += dt*Ki_q*e_q
d_id, d_iq    = machine.derivative(i_d, i_q, w_e, s_d, s_q)
i_d, i_q     += dt*d_id, dt*d_iq
```

Use `BW = 2000.0` rad/s for both axes, and set `id_ref` from `id_command` when
`weaken` is true and to zero when it is false.
''',
        "deliverables": [
            "`pi_gains`, `decouple` and `limit_voltage`, each correct in isolation: the feedforward must cancel the machine's cross terms exactly, and the limiter must preserve the direction of a vector it shortens.",
            "`id_command`, implementing the voltage-ellipse law with both clamps — zero below base speed, and never past the current circle above it.",
            "`run`, a two-axis PI current loop with the feedforward, the voltage limiter and conditional integration, returning the two current histories.",
            "A run at 800 electrical rad/s that reaches an 8 A `i_q` reference with `i_d` at zero, and a run at 2500 rad/s that reaches it only with field weakening enabled.",
            "A short comment at the top of `main.py` recording the base speed you computed and the bandwidth you chose, with the reason for the margin in `id_command`.",
        ],
        "constraints": [
            "NumPy and the standard library only — no SciPy, no control or machine libraries.",
            "`machine.py` is read-only. Read its constants; do not redefine them in `main.py`.",
            "Forward Euler with the timestep given. Do not switch integrator or add sub-stepping.",
            "The feedforward must use the measured currents, not the references — a feedforward built from references is an open-loop guess and stops cancelling the moment the loop is limited.",
            "Anti-windup by conditional integration: freeze both integrators whenever the voltage vector is clipped.",
        ],
        "rubric": [
            {"criterion": "Gains and feedforward", "weight": 20,
             "evidence": "pi_gains reproduces the cancellation rule on two different plants, and decouple's output makes the machine derivative reduce exactly to the resistive decay -R i / L on both axes."},
            {"criterion": "Voltage limiter", "weight": 15,
             "evidence": "A vector inside the circle is returned unchanged, one outside comes back with magnitude exactly v_max and the ratio of its components preserved to within 1e-12."},
            {"criterion": "Field-weakening command", "weight": 25,
             "evidence": "id_command is zero while the budget still covers the operating point, negative once it does not — which at an 8 A reference is well below the no-load base speed — satisfies the voltage-ellipse budget where it is not clamped, and never violates the current circle at extreme speed."},
            {"criterion": "Closed-loop behaviour below base speed", "weight": 20,
             "evidence": "At 800 rad/s the loop reaches an 8 A q-axis reference to within 1e-3 A with the d-axis current held at zero, and never overshoots the reference."},
            {"criterion": "Closed-loop behaviour in field weakening", "weight": 20,
             "evidence": "At 2500 rad/s the run with weakening enabled holds a positive torque above 4 Nm while the run with it disabled saturates into negative q-axis current and negative torque."},
        ],
        "hints": [
            "`v_limit()` in `machine.py` returns $V_{dc}/\\sqrt{3}$. Use it rather than hard-coding 173.2.",
            "The two axes need different proportional gains, because `pi_gains` is called once with `LD` and once with `LQ`. Both integral gains come out the same, at `BW * R`.",
            "In `limit_voltage`, return the inputs unchanged when the magnitude is within the limit — the loop's anti-windup test compares the returned values with the requested ones, and scaling by a `v_max/mag` that is merely close to one still moves the last bit and freezes both integrators on a step that was never clipped.",
            "If the 2500 rad/s run with weakening still ends up with negative `i_q`, check the sign of `ff_q`: the back-EMF opposes the applied voltage, so the feedforward must *add* $\\omega_e(L_d i_d + \\lambda_m)$, not subtract it.",
        ],
        "files": [
            {"name": "machine.py", "ro": True, "content": r'''
"""The interior PMSM used all through PWR520. Do not edit."""
import numpy as np

R = 0.45          # ohm, per phase
LD = 0.0035       # H, d-axis inductance
LQ = 0.0055       # H, q-axis inductance — salient rotor, L_q > L_d
LAM = 0.085       # Wb, rotor magnet flux linkage
POLE_PAIRS = 4
V_DC = 300.0      # V, dc bus
I_MAX = 20.0      # A, peak phase current rating
FW_MARGIN = 0.95  # fraction of the voltage budget the weakening law may claim


def v_limit():
    """Largest phase-voltage peak the modulator can synthesise linearly."""
    return V_DC / np.sqrt(3.0)


def derivative(i_d, i_q, w_e, v_d, v_q):
    """Return (di_d/dt, di_q/dt) for the dq model at electrical speed w_e."""
    d_id = (v_d - R * i_d + w_e * LQ * i_q) / LD
    d_iq = (v_q - R * i_q - w_e * (LD * i_d + LAM)) / LQ
    return d_id, d_iq


def torque(i_d, i_q):
    """Electromagnetic torque, magnet term plus reluctance term."""
    return 1.5 * POLE_PAIRS * (LAM * i_q + (LD - LQ) * i_d * i_q)
'''},
            {"name": "main.py", "content": r'''
import numpy as np
import machine
from machine import R, LD, LQ, LAM, I_MAX, FW_MARGIN, v_limit

BW = 2000.0   # rad/s, closed-loop current bandwidth for both axes

# Base speed: TODO, and the reason for the margin in id_command: TODO


def pi_gains(R_, L_, bw):
    """Return (K_p, K_i) for a closed-loop bandwidth of `bw` rad/s."""
    # TODO
    return 0.0, 0.0


def decouple(w_e, i_d, i_q):
    """Return the feedforward pair (v_d_ff, v_q_ff) from the measured currents."""
    # TODO: one term per axis, and they do not have the same sign.
    return 0.0, 0.0


def limit_voltage(v_d, v_q, v_max):
    """Scale the vector down to v_max if it is longer. Otherwise return it as is."""
    # TODO
    return 0.0, 0.0


def id_command(w_e, iq_ref):
    """Field-weakening d-axis command, clamped at 0 above and the current circle below."""
    # TODO
    return 0.0


def run(w_e, iq_ref, dt, steps, weaken=True):
    """Run both current loops at a fixed electrical speed. Return (i_d list, i_q list)."""
    # TODO
    return [], []


if __name__ == "__main__":
    print("base speed:", round(v_limit() / LAM, 3), "elec rad/s")
    print("gains d:", pi_gains(R, LD, BW), " q:", pi_gains(R, LQ, BW))
    ids, iqs = run(800.0, 8.0, 2e-6, 15000)
    if ids:
        print("at 800 rad/s: i_d =", round(ids[-1], 5), " i_q =", round(iqs[-1], 5))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
import numpy as np
import machine
from machine import R, LD, LQ, LAM, I_MAX, FW_MARGIN, v_limit

BW = 2000.0   # rad/s, closed-loop current bandwidth for both axes

# Base speed is v_limit()/LAM = 173.205/0.085 = 2037.7 elec rad/s, so 800 rad/s is
# well inside the constant-torque region and 2500 rad/s is well outside it.
# id_command claims only FW_MARGIN = 95 per cent of the voltage budget because the
# ellipse law ignores the resistive drops R*i_d and R*i_q; without that margin the
# steady-state voltage demand comes out a few volts over v_limit and the loop sits
# permanently clipped.


def pi_gains(R_, L_, bw):
    """Return (K_p, K_i) for a closed-loop bandwidth of `bw` rad/s."""
    return bw * L_, bw * R_


def decouple(w_e, i_d, i_q):
    """Return the feedforward pair (v_d_ff, v_q_ff) from the measured currents."""
    return -w_e * LQ * i_q, w_e * (LD * i_d + LAM)


def limit_voltage(v_d, v_q, v_max):
    """Scale the vector down to v_max if it is longer. Otherwise return it as is."""
    mag = float(np.hypot(v_d, v_q))
    if mag <= v_max or mag == 0.0:
        return v_d, v_q
    k = v_max / mag
    return v_d * k, v_q * k


def id_command(w_e, iq_ref):
    """Field-weakening d-axis command, clamped at 0 above and the current circle below."""
    if w_e <= 0.0:
        return 0.0
    budget = FW_MARGIN * v_limit()
    room = (budget / w_e) ** 2 - (LQ * iq_ref) ** 2
    flux = float(np.sqrt(room)) if room > 0.0 else 0.0
    need = (flux - LAM) / LD
    floor = -float(np.sqrt(max(0.0, I_MAX ** 2 - iq_ref ** 2)))
    return float(min(0.0, max(need, floor)))


def run(w_e, iq_ref, dt, steps, weaken=True):
    """Run both current loops at a fixed electrical speed. Return (i_d list, i_q list)."""
    kp_d, ki_d = pi_gains(R, LD, BW)
    kp_q, ki_q = pi_gains(R, LQ, BW)
    v_max = v_limit()
    id_ref = id_command(w_e, iq_ref) if weaken else 0.0
    i_d = 0.0
    i_q = 0.0
    z_d = 0.0
    z_q = 0.0
    ids = []
    iqs = []
    for _ in range(steps):
        ids.append(i_d)
        iqs.append(i_q)
        e_d = id_ref - i_d
        e_q = iq_ref - i_q
        ff_d, ff_q = decouple(w_e, i_d, i_q)
        v_d = kp_d * e_d + z_d + ff_d
        v_q = kp_q * e_q + z_q + ff_q
        s_d, s_q = limit_voltage(v_d, v_q, v_max)
        if s_d == v_d and s_q == v_q:
            z_d += dt * ki_d * e_d
            z_q += dt * ki_q * e_q
        d_id, d_iq = machine.derivative(i_d, i_q, w_e, s_d, s_q)
        i_d = i_d + dt * d_id
        i_q = i_q + dt * d_iq
    return ids, iqs


if __name__ == "__main__":
    print("base speed:", round(v_limit() / LAM, 3), "elec rad/s")
    print("gains d:", pi_gains(R, LD, BW), " q:", pi_gains(R, LQ, BW))
    ids, iqs = run(800.0, 8.0, 2e-6, 15000)
    if ids:
        print("at 800 rad/s: i_d =", round(ids[-1], 5), " i_q =", round(iqs[-1], 5))
'''},
        ],
        "tests": [
            {"name": "the gains follow the cancellation rule on any plant", "code": r'''
from machine import R, LD, LQ
_kp, _ki = pi_gains(R, LD, 2000.0)
assert abs(_kp - 7.0) < 1e-12, f"K_p on the d axis should be 2000*0.0035 = 7.0, got {_kp}"
assert abs(_ki - 900.0) < 1e-12, f"K_i should be 2000*0.45 = 900.0, got {_ki}"
_kpq, _kiq = pi_gains(R, LQ, 2000.0)
assert abs(_kpq - 11.0) < 1e-12, f"K_p on the q axis should be 2000*0.0055 = 11.0, got {_kpq}"
assert abs(_kiq - 900.0) < 1e-12, "both axes share the same integral gain, bw*R"
_a, _b = pi_gains(2.0, 0.5, 10.0)
assert abs(_a - 5.0) < 1e-12 and abs(_b - 20.0) < 1e-12, \
    f"the rule must not be hard-coded to this machine; expected (5.0, 20.0), got ({_a}, {_b})"
'''},
            {"name": "the feedforward cancels the machine's cross terms exactly", "code": r'''
import machine
from machine import R, LD, LQ
_w, _id, _iq = 1000.0, -3.0, 8.0
_ffd, _ffq = decouple(_w, _id, _iq)
_got = machine.derivative(_id, _iq, _w, _ffd, _ffq)
_want = (-R * _id / LD, -R * _iq / LQ)
assert abs(_got[0] - _want[0]) < 1e-9, \
    f"with only the feedforward applied, di_d/dt should be -R*i_d/L_d = {_want[0]}, got {_got[0]}"
assert abs(_got[1] - _want[1]) < 1e-9, \
    f"and di_q/dt should be -R*i_q/L_q = {_want[1]}, got {_got[1]}"
assert _ffd < 0.0 < _ffq, \
    f"the two feedforward terms have opposite signs at this operating point, got {(_ffd, _ffq)}"
'''},
            {"name": "the voltage limiter shortens without turning", "code": r'''
import numpy as np
_a, _b = limit_voltage(10.0, 20.0, 173.2)
assert abs(_a - 10.0) < 1e-12 and abs(_b - 20.0) < 1e-12, \
    f"a vector inside the circle must come back untouched, got {(_a, _b)}"
_c, _d = limit_voltage(100.0, 200.0, 100.0)
assert abs(np.hypot(_c, _d) - 100.0) < 1e-9, \
    f"a vector outside must come back at exactly v_max, got |v| = {np.hypot(_c, _d)}"
assert abs(_d / _c - 2.0) < 1e-12, \
    f"and with its direction preserved: v_q/v_d should stay 2.0, got {_d / _c}"
'''},
            {"name": "the weakening command respects the voltage budget and the current circle", "code": r'''
import numpy as np
from machine import LD, LQ, LAM, I_MAX, FW_MARGIN, v_limit
for _w in (0.0, 200.0, 1000.0):
    assert id_command(_w, 8.0) == 0.0, \
        f"at {_w} rad/s there is voltage to spare, so i_d should be 0, got {id_command(_w, 8.0)}"
_id = id_command(2500.0, 8.0)
assert _id < -9.0, f"at 2500 rad/s the field must be weakened hard; expected below -9 A, got {_id}"
_budget = FW_MARGIN * v_limit()
_lhs = (2500.0 * (LD * _id + LAM)) ** 2 + (2500.0 * LQ * 8.0) ** 2
assert abs(np.sqrt(_lhs) - _budget) < 1e-6, \
    f"the weakened operating point should sit on the ellipse of radius {_budget}, got {np.sqrt(_lhs)}"
_far = id_command(40000.0, 8.0)
assert abs(_far + np.sqrt(I_MAX ** 2 - 64.0)) < 1e-9, \
    f"far above base speed the current circle binds; expected {-np.sqrt(I_MAX ** 2 - 64.0)}, got {_far}"
'''},
            {"name": "below base speed the loop simply hits its reference", "code": r'''
_ids, _iqs = run(800.0, 8.0, 2e-6, 15000)
assert len(_iqs) == 15000, f"expected 15000 samples, got {len(_iqs)}"
assert abs(_iqs[0]) < 1e-12 and abs(_ids[0]) < 1e-12, "both currents start at zero"
assert abs(_iqs[-1] - 8.0) < 1e-3, f"i_q should settle on the 8 A reference, got {_iqs[-1]}"
assert abs(_ids[-1]) < 1e-3, f"and i_d should stay at zero below base speed, got {_ids[-1]}"
assert max(_iqs) <= 8.0 + 1e-6, \
    f"the tuned loop is a first-order lag and should not overshoot; peak was {max(_iqs)}"
'''},
            {"name": "above base speed only field weakening delivers torque", "code": r'''
import machine
_wid, _wiq = run(2500.0, 8.0, 2e-6, 15000)
_nid, _niq = run(2500.0, 8.0, 2e-6, 15000, weaken=False)
assert _wid[-1] < -9.0, f"with weakening on, i_d should be driven well negative, got {_wid[-1]}"
assert _wiq[-1] > 7.5, f"and i_q should still reach most of its 8 A reference, got {_wiq[-1]}"
_t_on = machine.torque(_wid[-1], _wiq[-1])
_t_off = machine.torque(_nid[-1], _niq[-1])
assert _t_on > 4.0, f"weakened, the machine should still make over 4 Nm, got {_t_on}"
assert _t_off < 0.0, \
    ("without weakening the back-EMF exceeds the bus, the loop clips and i_q is dragged "
     f"negative, so the torque should be negative; got {_t_off} from i_q = {_niq[-1]}")
'''},
            {"name": "the run is deterministic and uses the reference it was given", "code": r'''
_a = run(800.0, 8.0, 2e-6, 4000)
_b = run(800.0, 8.0, 2e-6, 4000)
assert _a == _b, "nothing in this loop is random; two identical calls must agree exactly"
_c_ids, _c_iqs = run(800.0, 4.0, 2e-6, 15000)
assert abs(_c_iqs[-1] - 4.0) < 1e-3, \
    f"halving the reference should halve the settled current, got {_c_iqs[-1]}"
'''},
        ],
    },
}
