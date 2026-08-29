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
                    "Set $a_{11}$ and $a_{22}$ to zero. The readout says **centre** and the curves close into rings: constant magnitude, constant rate, which is exactly a balanced three-phase set seen in $\\alpha\\beta$. They creep outward by about a tenth of their radius over the drawn interval — that is the forward-Euler integrator in the sketching code, not the physics.",
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
