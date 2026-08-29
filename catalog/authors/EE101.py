"""EE101 — Circuit Analysis I: Direct Current.

The first course of the EE degree. It assumes school mathematics and nothing else:
no prior circuits, no prior programming beyond arithmetic. Every term is defined
where it is first used.

Authoring rules, as for every course module:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only; this course uses neither beyond `math`
  * every expected number was produced by running the code, not assumed
  * build checks are JavaScript against the circuit API, and they measure what the
    circuit does rather than compare it to the reference drawing
"""

COURSE = {
    "id": "EE101",
    "title": "Circuit Analysis I — Direct Current",
    "band": 1,
    "level": "Beginner",
    "prereqs": [],
    "stack": ["Python"],
    "credits": 10,
    "hours": 120,
    "icon": "◉",
    "summary": (
        "Everything electrical starts here: what a current actually is, what a voltage "
        "actually measures, and the two conservation laws that between them decide every "
        "node voltage in every circuit you will ever draw. Direct current means nothing "
        "changes with time, which strips the subject down to arithmetic and lets the "
        "reasoning be the hard part. By the end you can look at a resistor network and "
        "say what every voltage, every current and every watt in it will be."
    ),
    "outcomes": [
        "State what charge, current, voltage, resistance and power are, in words and in units, without reaching for a formula sheet.",
        "Apply Ohm's law and the series and parallel combination rules to reduce a resistor network to a single number.",
        "Use Kirchhoff's current and voltage laws to find an unknown current or voltage in a network that does not reduce by inspection.",
        "Design a voltage divider that meets a required output voltage under a stated load and a stated current budget.",
        "Account for every watt a supply delivers, and check a solution by conservation of energy.",
    ],
    "assessment": (
        "Four quizzes, three circuits drawn and measured in the schematic editor, four "
        "short Python labs checked by execution, and a capstone that solves an arbitrary "
        "resistor network from first principles."
    ),
    "reading": [
        "*The Art of Electronics*, Horowitz & Hill — chapter 1, sections 1.1 to 1.4.",
        "*Fundamentals of Electric Circuits*, Alexander & Sadiku — chapters 1 to 3, for many worked examples.",
        "MIT OCW 6.002, first two lectures, freely available.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "Charge, current and voltage",
            "summary": "Three quantities and their units. Get these right and the rest of the course is arithmetic.",
            "concepts": [
                "Charge is a property of matter, measured in coulombs (C). One electron carries $-1.602176634\\times10^{-19}$ C.",
                "Current is charge per unit time: $I = Q/t$. One ampere is one coulomb passing a point every second.",
                "Conventional current is drawn in the direction positive charge would move. In a metal the electrons actually drift the other way, and no calculation in this course notices.",
                "Voltage between two points is energy per unit charge: $V = E/Q$. One volt is one joule handed to every coulomb that makes the trip.",
                "A voltage is always *between* two points. 'The voltage at node A' is shorthand for the voltage between node A and whatever was chosen as ground.",
                "Going round a circuit, charge is never used up — energy is. A bulb returns every electron it is given, at a lower energy.",
                "Direct current (DC) means nothing changes with time: every current and every voltage is one fixed number.",
            ],
            "sandbox": {
                "title": "What 'steady' means, and when it starts",
                "visualiser": "pole-step",
                "minutes": 8,
                "initial": {"zeta": 1.2, "wn": 3},
                "brief": r'''
Switch a supply on and the circuit does not arrive at its answer instantly. It moves
towards it, and after a while it stops moving. **Direct current analysis is the study
of that final, unmoving value** — everything in this course computes where the right
hand curve ends up, not how it got there.

Watch the **right-hand plot**. The horizontal dashed line is the final value the
circuit settles on; the solid curve is the journey. The left-hand plot is a map of
the two numbers that decide the shape of that journey, and it is the subject of a
later course — for now, notice only that the two dots move when you move the sliders.

The slider marked $\zeta$ (the Greek letter zeta) controls how the journey goes, and
$\omega_n$ controls how fast.
''',
                "notice": [
                    "Leave $\\zeta$ at 1.2. The curve climbs once, flattens onto the dashed line at 1, and stays there. That last value is the only thing a DC calculation ever asks for.",
                    "Drag $\\zeta$ down to 0.2. The curve now overshoots and rings, and the two dots on the left lift off the horizontal axis — but the curve still ends on the same dashed line at 1. The steady value does not depend on how the circuit gets there.",
                    "Put $\\zeta$ back at 1.2 and raise $\\omega_n$ from 3 to 12. The curve keeps exactly the same shape; only the numbers along the time axis shrink, because the plot rescales itself. Fast or slow, the DC answer is identical.",
                ],
            },
            "quiz": {
                "title": "Charge, current and voltage: the definitions",
                "minutes": 8,
                "questions": [
                    {
                        "q": "One ampere is best described as:",
                        "opts": [
                            "one coulomb of charge passing a point every second",
                            "one coulomb of charge sitting on a conductor",
                            "one joule of energy delivered every second",
                            "one electron passing a point every second",
                        ],
                        "a": 0,
                        "why": r'''
Current is a *rate*: $I = Q/t$, coulombs per second. Option B describes a quantity of
charge, not a flow of it. Option C is a watt, which is power. Option D is a flow, but
one electron per second is about $1.6\times10^{-19}$ A — a fantastically small current.
''',
                    },
                    {
                        "q": "A torch bulb draws 0.5 A for 2 minutes. How much charge passes through it?",
                        "opts": ["1 C", "60 C", "120 C", "0.25 C"],
                        "a": 1,
                        "why": r'''
$Q = It$, and $t$ must be in **seconds**: two minutes is 120 s, so
$Q = 0.5 \times 120 = 60$ C. The tempting answer 1 C comes from multiplying by 2 and
forgetting the units of time — the single most common arithmetic slip in this whole
course. When a question gives you minutes, hours or milliseconds, convert first.
''',
                    },
                    {
                        "q": "The voltage between two points in a circuit measures:",
                        "opts": [
                            "how many electrons are stored between them",
                            "the energy given to each coulomb of charge that travels between them",
                            "how fast the electrons move between them",
                            "the current that will flow between them",
                        ],
                        "a": 1,
                        "why": r'''
Voltage is energy per unit charge, $V = E/Q$, measured in joules per coulomb — and
one joule per coulomb is given the name one volt. It says nothing on its own about
how much charge moves (that is current) or how fast it drifts (which is, surprisingly,
less than a millimetre per second in a typical wire).
''',
                    },
                    {
                        "q": "A 9 V battery pushes 2 C of charge round a circuit. How much energy does it deliver?",
                        "opts": ["4.5 J", "2 J", "18 J", "11 J"],
                        "a": 2,
                        "why": r'''
Rearranging $V = E/Q$ gives $E = QV = 2 \times 9 = 18$ J. The answer 4.5 J is $V/Q$,
which is the definition upside down; it is worth writing the units out —
$\text{C} \times \text{J/C} = \text{J}$ — whenever the direction of a division is in
doubt.
''',
                    },
                    {
                        "q": "In a simple loop of battery, wire and bulb, how does the current leaving the bulb compare with the current entering it?",
                        "opts": [
                            "smaller — some current is used up making light",
                            "exactly the same",
                            "zero — the current stops at the bulb",
                            "larger — the bulb adds energy",
                        ],
                        "a": 1,
                        "why": r'''
Exactly the same. This is the single most useful correction a beginner can make:
**energy** is consumed in the bulb, **charge** is not. Every electron that goes in
comes out again, at a lower energy per electron — which is precisely what the voltage
drop across the bulb measures. Charge is conserved, and that conservation is
Kirchhoff's current law, which arrives in module 3.
''',
                    },
                    {
                        "q": "Conventional current in a copper wire is drawn from + to −, while the electrons drift from − to +. What does that mean for your calculations?",
                        "opts": [
                            "every current answer must be negated at the end",
                            "nothing, as long as you are consistent — the two descriptions give identical numbers",
                            "only the electron direction gives correct power figures",
                            "it matters for resistors but not for batteries",
                        ],
                        "a": 1,
                        "why": r'''
Nothing at all. Conventional current is a bookkeeping choice made before anyone knew
electrons existed, and every formula in this course was written to match it. Choose a
direction, mark it on the drawing, and if the arithmetic comes back negative it simply
means the real current runs the other way — which is information, not an error.
''',
                    },
                ],
            },
            "lab": {
                "title": "Counting charge and energy",
                "runtime": "python",
                "minutes": 20,
                "brief": r'''
Three one-line functions, so that the definitions become something you have actually
computed with.

- `charge(amps, seconds)` returns the charge in coulombs that passes in that time.
- `electrons(coulombs)` returns how many electrons that charge amounts to. The
  constant `ELEMENTARY_CHARGE` is already defined for you.
- `energy(coulombs, volts)` returns the energy in joules handed to that charge by
  that voltage.

Nothing here needs a loop or a condition. The point is the units: seconds, coulombs,
joules. If you find yourself wanting to divide where the definition multiplies, write
the units alongside the numbers and see which arrangement leaves you with the unit you
were asked for.
''',
                "files": [{"name": "main.py", "content": r'''
"""Charge, current and energy — the three definitions, as code."""

ELEMENTARY_CHARGE = 1.602176634e-19  # coulombs carried by one electron


def charge(amps, seconds):
    """Charge in coulombs that passes when `amps` flows for `seconds`."""
    # TODO: current is charge per second, so charge is current times seconds.
    return 0.0


def electrons(coulombs):
    """How many electrons make up this much charge."""
    # TODO: divide by the charge on one electron.
    return 0.0


def energy(coulombs, volts):
    """Energy in joules given to `coulombs` of charge by a voltage of `volts`."""
    # TODO: a volt is a joule per coulomb.
    return 0.0


if __name__ == "__main__":
    q = charge(0.5, 120)
    print("a 0.5 A torch for 2 minutes moves", q, "C")
    print("that is about", f"{electrons(q):.3e}", "electrons")
    print("from a 4.5 V battery that is", energy(q, 4.5), "J")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Charge, current and energy — the three definitions, as code."""

ELEMENTARY_CHARGE = 1.602176634e-19  # coulombs carried by one electron


def charge(amps, seconds):
    """Charge in coulombs that passes when `amps` flows for `seconds`."""
    return amps * seconds


def electrons(coulombs):
    """How many electrons make up this much charge."""
    return coulombs / ELEMENTARY_CHARGE


def energy(coulombs, volts):
    """Energy in joules given to `coulombs` of charge by a voltage of `volts`."""
    return coulombs * volts


if __name__ == "__main__":
    q = charge(0.5, 120)
    print("a 0.5 A torch for 2 minutes moves", q, "C")
    print("that is about", f"{electrons(q):.3e}", "electrons")
    print("from a 4.5 V battery that is", energy(q, 4.5), "J")
'''}],
                "hints": [
                    "`charge` is one multiplication. The only trap is being handed minutes when the formula wants seconds — the caller converts, not you.",
                    "`electrons` divides the total charge by the charge on one electron. One coulomb comes to about $6.24\\times10^{18}$ electrons; if your answer is not somewhere near $10^{18}$, the division has gone the wrong way round.",
                    "`energy` is also one multiplication: joules per coulomb, times coulombs.",
                ],
                "tests": [
                    {"name": "charge is current times time", "code": r'''
q = charge(0.5, 120)
assert abs(q - 60.0) < 1e-12, f"0.5 A for 120 s is 60 C, got {q}"
'''},
                    {"name": "a big current for a short time", "code": r'''
q = charge(2.0, 0.5)
assert abs(q - 1.0) < 1e-12, f"2 A for half a second is 1 C, got {q}"
'''},
                    {"name": "one coulomb is about 6.24e18 electrons", "code": r'''
n = electrons(1.0)
assert abs(n - 6.241509074460763e18) < 1e6, \
    f"1 C divided by 1.602176634e-19 C is about 6.2415e18, got {n}"
'''},
                    {"name": "energy is charge times voltage", "code": r'''
e = energy(2.0, 9.0)
assert abs(e - 18.0) < 1e-12, f"2 C through 9 V is 18 J, got {e}"
'''},
                    {"name": "the three combine on a real torch", "code": r'''
q = charge(0.06, 1800)
assert abs(q - 108.0) < 1e-9, f"60 mA for 30 minutes is 108 C, got {q}"
e = energy(q, 4.5)
assert abs(e - 486.0) < 1e-9, f"108 C from 4.5 V is 486 J, got {e}"
n = electrons(q)
assert n > 6e20, f"108 C should be well over 1e20 electrons, got {n}"
'''},
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Ohm's law, resistance and power",
            "summary": "One equation relating voltage and current, and one relating them to heat.",
            "concepts": [
                "Resistance relates the voltage across a component to the current through it: $V = IR$. Resistance is measured in ohms, and 1 Ω is 1 V/A.",
                "$I = V/R$ and $R = V/I$ are rearrangements of the same statement, not three separate laws.",
                "A resistor is symmetric: it has no + end, and reversing it changes nothing.",
                "Power is energy per second, measured in watts: $P = VI$, which follows directly from $V = E/Q$ and $I = Q/t$.",
                "For a resistor, substituting Ohm's law gives $P = I^2R = V^2/R$. Use whichever of the two quantities you already know.",
                "A resistor's power rating is a temperature limit, not an electrical one. Exceeding it does not change the current; it destroys the part.",
                "Real wires have a small resistance and real batteries have an internal one. In this course both are taken as zero unless a question says otherwise.",
            ],
            "quiz": {
                "title": "Ohm's law and what it costs in heat",
                "minutes": 8,
                "questions": [
                    {
                        "q": "12 V is applied across a 3 kΩ resistor. What current flows?",
                        "opts": ["36 mA", "4 mA", "250 mA", "0.25 mA"],
                        "a": 1,
                        "why": r'''
$I = V/R = 12 / 3000 = 0.004$ A, which is 4 mA. The answer 36 mA comes from
multiplying instead of dividing, and 250 mA from dividing the resistance by the
voltage. A quick sanity check: a few volts across a few thousand ohms always gives a
few milliamps, and that pairing — volts, kilohms, milliamps — is worth memorising,
because $\text{V}/\text{k}\Omega = \text{mA}$ exactly.
''',
                    },
                    {
                        "q": "For a fixed resistor, doubling the voltage across it multiplies the power it dissipates by:",
                        "opts": ["2", "4", "1 — power does not change", "√2"],
                        "a": 1,
                        "why": r'''
Four. Doubling the voltage doubles the current as well, and $P = VI$ multiplies the
two, so the power goes up by a factor of four. The formula $P = V^2/R$ says the same
thing in one step. Answering 2 means treating the current as fixed — but the current
is not free to stay put once the voltage moves, because Ohm's law ties them together.
''',
                    },
                    {
                        "q": "A resistor is rated at 0.25 W. What is the smallest resistance you may put across a 10 V supply without exceeding that rating?",
                        "opts": ["25 Ω", "40 Ω", "400 Ω", "4 kΩ"],
                        "a": 2,
                        "why": r'''
$P = V^2/R$, so $R = V^2/P = 100/0.25 = 400$ Ω. Note the direction of the inequality:
a *smaller* resistance draws a *larger* current and burns *more* power, so 400 Ω is a
lower limit — 4 kΩ is perfectly safe here, just not the smallest safe value.
''',
                    },
                    {
                        "q": "Two resistors, 100 Ω and 400 Ω, are connected in series so the same current flows through both. Which dissipates more power?",
                        "opts": [
                            "the 100 Ω, because a lower resistance always means more heat",
                            "the 400 Ω",
                            "they dissipate the same, because the current is the same",
                            "it cannot be decided without knowing the supply voltage",
                        ],
                        "a": 1,
                        "why": r'''
With a shared current the useful form is $P = I^2R$: the same $I^2$ multiplies both, so
the larger resistance dissipates more — four times more here, whatever the supply
voltage turns out to be. The trap is answering from $P = V^2/R$, which is correct only
when the two parts share a *voltage*, which is the parallel case, not this one. Pick
the form that matches the quantity the two components have in common.
''',
                    },
                    {
                        "q": "A component obeys Ohm's law. Which statement is therefore true?",
                        "opts": [
                            "a plot of voltage against current through it is a straight line through the origin",
                            "it dissipates no power",
                            "the current through it is fixed regardless of the voltage",
                            "its resistance falls as the current rises",
                        ],
                        "a": 0,
                        "why": r'''
$V = IR$ with $R$ constant is the equation of a straight line through the origin, and
its gradient *is* the resistance. That is what obeying Ohm's law means, and it is a
property real components only approximately have: a filament lamp's resistance rises
sharply as it heats, so its line bends. Every component in this course is taken as
perfectly ohmic.
''',
                    },
                ],
            },
            "build": {
                "title": "One resistor, one current",
                "minutes": 20,
                "brief": r'''
The canvas opens with a 12 V supply and a ground symbol, already joined. Your job is
to finish the loop so that **exactly 4 mA flows**.

What the finished circuit must do:

- one resistor, and only one, connected across the whole supply
- the current out of the supply is 4 mA
- a probe on the node at the top of the resistor, so the checks can read the voltage
  there

## How to draw it

Pick the resistor tool, place it, and wire its top pin to the supply's + terminal
(the **top** pin of a vertical source) and its bottom pin down to a second ground
symbol. Two ground symbols are one node — that is what ground means, and it saves a
long wire round the outside. Then place a probe (`OUT`) on the top node.

Click a component to edit its value. The value you need is not given: work it out
from $R = V/I$ before you type anything.

The checks measure the finished circuit. Any resistance that produces 4 mA passes,
however you lay the drawing out.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 3000},
                        {"id": "p3", "kind": "GND", "x": 9, "y": 9},
                        {"id": "p4", "kind": "OUT", "x": 11, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 9]},
                        {"a": [9, 5], "b": [11, 5]},
                    ],
                },
                "checks": [
                    {"name": "one 12 V supply and exactly one resistor", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
c.assert(c.count('R') === 1,
  'This exercise wants one resistor and nothing else, so the current has only one path to take. Found ' + c.count('R') + '.');
'''},
                    {"name": "the whole 12 V appears across the resistor", "code": r'''
c.close(c.vout(), 12, 0.005,
  'the probe voltage — it belongs on the node joining the supply + terminal to the top of the resistor');
'''},
                    {"name": "the supply pushes 4 mA round the loop", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
const i = Math.abs(cur[ids[0]]);
c.close(i, 0.004, 0.02, 'the current out of the supply');
'''},
                    {"name": "the resistor turns 48 mW into heat", "code": r'''
const cur = c.dc().currents;
const i = Math.abs(cur[Object.keys(cur)[0]]);
const p = c.vout() * i;
c.close(p, 0.048, 0.03, 'the power in the resistor (P = V times I)');
'''},
                ],
                "hints": [
                    "Rearrange $V = IR$ into $R = V/I$. Remember that 4 mA is 0.004 A.",
                    "12 V and 4 mA give 3 kΩ. Type `3k` into the value box — the editor understands the k, M and m suffixes.",
                    "The + terminal of a vertical source is its **top** pin. Wire that to the top of the resistor, and the bottom of the resistor to a ground symbol.",
                    "A probe reads the voltage of the node it sits on, relative to ground. Put it on the top node, not the bottom one, or it will read 0 V.",
                ],
            },
            "lab": {
                "title": "Sizing a resistor and checking it survives",
                "runtime": "python",
                "minutes": 22,
                "brief": r'''
The same three sums as the circuit you just drew, written down so they can be reused.

- `resistor_for_current(volts, amps)` returns the resistance needed to draw that
  current from that voltage.
- `power(volts, ohms)` returns the power a resistor dissipates with that voltage
  across it.
- `within_rating(volts, ohms, rating_w)` returns `True` when that resistor stays
  inside its power rating, and `False` when it would cook. A resistor exactly at its
  rating counts as acceptable.

Write `within_rating` by calling `power`, not by repeating the formula. One place for
one fact.
''',
                "files": [{"name": "main.py", "content": r'''
"""Ohm's law and power, as three reusable functions."""


def resistor_for_current(volts, amps):
    """Resistance in ohms that draws `amps` when `volts` is across it."""
    # TODO: rearrange V = I R.
    return 0.0


def power(volts, ohms):
    """Power in watts dissipated by `ohms` with `volts` across it."""
    # TODO: P = V * I, and I = V / R.
    return 0.0


def within_rating(volts, ohms, rating_w):
    """True when the resistor stays at or below its power rating."""
    # TODO: call power() and compare.
    return False


if __name__ == "__main__":
    r = resistor_for_current(12.0, 0.004)
    print("12 V at 4 mA needs", r, "ohms")
    print("which dissipates", power(12.0, r), "W")
    print("safe on a quarter-watt part?", within_rating(12.0, r, 0.25))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Ohm's law and power, as three reusable functions."""


def resistor_for_current(volts, amps):
    """Resistance in ohms that draws `amps` when `volts` is across it."""
    return volts / amps


def power(volts, ohms):
    """Power in watts dissipated by `ohms` with `volts` across it."""
    return volts * volts / ohms


def within_rating(volts, ohms, rating_w):
    """True when the resistor stays at or below its power rating."""
    return power(volts, ohms) <= rating_w


if __name__ == "__main__":
    r = resistor_for_current(12.0, 0.004)
    print("12 V at 4 mA needs", r, "ohms")
    print("which dissipates", power(12.0, r), "W")
    print("safe on a quarter-watt part?", within_rating(12.0, r, 0.25))
'''}],
                "hints": [
                    "`resistor_for_current` is `volts / amps` — nothing more.",
                    "`power` can be written as `volts * volts / ohms`, or as `volts * (volts / ohms)`, which is literally V times I.",
                    "`within_rating` should end in a comparison, and a comparison in Python is already `True` or `False` — there is no need for an `if`.",
                ],
                "tests": [
                    {"name": "12 V at 4 mA wants 3 kilohms", "code": r'''
r = resistor_for_current(12.0, 0.004)
assert abs(r - 3000.0) < 1e-9, f"12 / 0.004 is 3000 ohms, got {r}"
'''},
                    {"name": "it works for other supplies too", "code": r'''
assert abs(resistor_for_current(5.0, 0.02) - 250.0) < 1e-9, "5 V at 20 mA is 250 ohms"
assert abs(resistor_for_current(230.0, 10.0) - 23.0) < 1e-9, "230 V at 10 A is 23 ohms"
'''},
                    {"name": "the circuit you drew dissipates 48 mW", "code": r'''
p = power(12.0, 3000.0)
assert abs(p - 0.048) < 1e-12, f"12 squared over 3000 is 0.048 W, got {p}"
'''},
                    {"name": "power goes as the square of the voltage", "code": r'''
a = power(5.0, 1000.0)
b = power(10.0, 1000.0)
assert abs(a - 0.025) < 1e-12, f"5 V across 1 k is 25 mW, got {a}"
assert abs(b / a - 4.0) < 1e-9, \
    f"doubling the voltage should quadruple the power, got a ratio of {b / a}"
'''},
                    {"name": "the rating test catches an overload", "code": r'''
assert within_rating(10.0, 500.0, 0.25) is True or within_rating(10.0, 500.0, 0.25) == True, \
    "10 V across 500 ohms is 0.2 W, comfortably inside a quarter watt"
assert not within_rating(10.0, 300.0, 0.25), \
    "10 V across 300 ohms is 0.333 W, which would cook a quarter-watt part"
assert within_rating(10.0, 400.0, 0.25), \
    "exactly at the rating counts as acceptable"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "Series, parallel and Kirchhoff's two laws",
            "summary": "Charge does not pile up, and energy per charge depends on the point rather than the path. Everything else follows.",
            "concepts": [
                "Kirchhoff's current law (KCL): at any node, the currents flowing in add up to the currents flowing out. It is conservation of charge, stated locally.",
                "Kirchhoff's voltage law (KVL): round any closed loop, the voltage rises equal the voltage drops. It is conservation of energy, stated locally.",
                "Two components are in **series** when the same current must pass through both: their resistances add, $R = R_1 + R_2$.",
                "Two components are in **parallel** when the same voltage appears across both: their conductances add, $1/R = 1/R_1 + 1/R_2$.",
                "For exactly two resistors in parallel the shortcut $R = R_1R_2/(R_1+R_2)$ is the same formula rearranged. Two equal resistors in parallel give half of one.",
                "Adding a resistor in parallel always *lowers* the total resistance, because it opens another path. Adding one in series always raises it.",
                "A network that reduces by repeated series and parallel steps can be collapsed to a single resistance; one that does not needs KCL and KVL written out node by node.",
            ],
            "quiz": {
                "title": "Combining resistors, and the two laws underneath",
                "minutes": 9,
                "questions": [
                    {
                        "q": "Two 10 kΩ resistors are connected in parallel. What is the resistance of the pair?",
                        "opts": ["20 kΩ", "10 kΩ", "5 kΩ", "0.1 kΩ"],
                        "a": 2,
                        "why": r'''
5 kΩ. Two equal resistors in parallel always give half of one, because you have
doubled the number of paths the current can take while leaving the voltage across each
path unchanged: twice the current for the same voltage is half the resistance.
Answering 20 kΩ is adding them, which is the *series* rule — that is the one mistake
worth drilling until it is impossible.
''',
                    },
                    {
                        "q": "A network already has some resistance. You add one more resistor in parallel with it. The total resistance:",
                        "opts": [
                            "always goes down",
                            "always goes up",
                            "stays the same",
                            "goes up or down depending on the size of the added resistor",
                        ],
                        "a": 0,
                        "why": r'''
Always down, no matter how large the added resistor is. You have given the current an
extra route without removing any of the existing ones, so for a fixed voltage more
current flows, which is by definition a lower resistance. A very large parallel
resistor lowers the total only slightly — but it does lower it. The mirror-image fact
is that a series resistor always raises the total.
''',
                    },
                    {
                        "q": "3.0 A flows into a node. Two of the three wires leaving it carry 1.2 A and 0.5 A. What does the third carry?",
                        "opts": ["1.3 A", "1.8 A", "4.7 A", "0.7 A"],
                        "a": 0,
                        "why": r'''
KCL: what goes in comes out, so $3.0 - 1.2 - 0.5 = 1.3$ A. The answer 1.8 A subtracts
only the first branch — it is worth writing the equation out in full rather than doing
it in your head, because nodes with four or five branches are ordinary. Charge cannot
accumulate at a junction; there is nowhere in a wire for it to sit.
''',
                    },
                    {
                        "q": "A 12 V supply drives three resistors in series. Two of them are measured to have 3 V and 5 V across them. What is across the third?",
                        "opts": ["12 V", "8 V", "4 V", "it depends on the resistor values"],
                        "a": 2,
                        "why": r'''
KVL: the three drops must add up to the 12 V rise the supply provides, so the third is
$12 - 3 - 5 = 4$ V. You do not need any resistor values — that is the power of KVL,
and it works round any loop you care to trace, in any circuit, always. (The values
would tell you *why* it split that way, which is the voltage divider in module 4.)
''',
                    },
                    {
                        "q": "A 100 Ω and a 10 Ω resistor are in series across a battery. Compare the current through the 10 Ω with the current through the 100 Ω.",
                        "opts": [
                            "ten times larger through the 10 Ω",
                            "exactly the same through both",
                            "ten times smaller through the 10 Ω",
                            "it depends on which one comes first in the loop",
                        ],
                        "a": 1,
                        "why": r'''
Identical. Series means there is a single path, and every electron that leaves one
resistor must enter the next — that is KCL applied to the node between them. What
differs is the *voltage* across each: ten times more across the 100 Ω, by Ohm's law.
Series shares current, parallel shares voltage, and confusing the two is the source of
most wrong answers in this module.
''',
                    },
                    {
                        "q": "You have a drawer containing only 4 kΩ resistors. Which combination gives exactly 6 kΩ?",
                        "opts": [
                            "two in series",
                            "two in parallel",
                            "one in series with two in parallel",
                            "three in parallel",
                        ],
                        "a": 2,
                        "why": r'''
Two in parallel give 2 kΩ, and putting one more in series with that pair adds 4 kΩ, for
6 kΩ in total. This is the exact network you are about to draw in the schematic
editor. For reference, the other options give 8 kΩ, 2 kΩ and 1.33 kΩ. Building an
awkward value out of identical parts is a genuine workshop skill, not just an exercise.
''',
                    },
                ],
            },
            "build": {
                "title": "Six kilohms from a drawer of four-kilohm resistors",
                "minutes": 25,
                "brief": r'''
You are given a 12 V supply and a stock room containing **4 kΩ resistors and nothing
else**. Build a network across that supply which

- draws exactly **2 mA** from the supply, and
- puts exactly **4 V** on the probe, measured between the probe's node and ground.

Every resistor you place must be 4 kΩ. That is the constraint that makes this
interesting: 6 kΩ is not in the drawer, so you have to make it.

## Where to start

The canvas opens with the supply, a ground, and one 4 kΩ resistor hanging from the
supply rail, with the probe on its lower end. Nothing flows yet, because that lower
end has no path to ground. Work out what has to go between the probe node and ground
so that the total is 6 kΩ, then draw it.

Think about the two numbers separately. 2 mA out of 12 V fixes the *total* resistance.
4 V at the probe fixes how that total splits between the part above the probe and the
part below it.

The checks measure the current and the probe voltage. Any arrangement of 4 kΩ parts
that produces both numbers passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 4000},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 7},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [11, 7]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 12},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 4000},
                        {"id": "p3", "kind": "OUT", "x": 11, "y": 7},
                        {"id": "p4", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 4000},
                        {"id": "p5", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 4000},
                        {"id": "p6", "kind": "GND", "x": 11, "y": 10},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [11, 7]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [13, 8]},
                        {"a": [9, 10], "b": [13, 10]},
                    ],
                },
                "checks": [
                    {"name": "every resistor came out of the 4 kΩ drawer", "code": r'''
const rs = c.values('R');
c.assert(rs.length >= 2,
  'One resistor cannot be both the series part and the parallel part. Found ' + rs.length + '.');
rs.forEach(function (r) {
  c.assert(Math.abs(r - 4000) <= 40,
    'Every resistor must be 4 kΩ — found one of ' + c.fmt(r, 'Ω') + '.');
});
'''},
                    {"name": "one 12 V supply drives the network", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source; found ' + c.count('V') + '.');
c.close(c.values('V')[0], 12, 0.001, 'the supply voltage');
'''},
                    {"name": "the probe reads 4 V", "code": r'''
c.close(c.vout(), 4.0, 0.02,
  'the probe voltage — 8 V is dropped above it and 4 V below it');
'''},
                    {"name": "the supply delivers 2 mA, so the total is 6 kΩ", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
const i = Math.abs(cur[ids[0]]);
c.close(i, 0.002, 0.02, 'the current out of the supply');
'''},
                ],
                "hints": [
                    "12 V at 2 mA means the whole network is $12/0.002 = 6$ kΩ. You already have 4 kΩ of it in place.",
                    "So 2 kΩ has to sit between the probe node and ground — and 2 kΩ is what two 4 kΩ resistors give when they are in parallel.",
                    "In parallel means both ends joined: wire the tops of the two lower resistors together and to the probe node, and wire both bottoms together and to a ground symbol.",
                    "Check your work with the voltages before you run: 2 mA through the top 4 kΩ drops 8 V, leaving 4 V at the probe, and 2 mA through the 2 kΩ pair drops exactly that 4 V.",
                ],
            },
            "lab": {
                "title": "Combination rules and a missing current",
                "runtime": "python",
                "minutes": 24,
                "brief": r'''
Three small functions covering the whole of this module.

- `series(values)` returns the resistance of a list of resistors in series.
- `parallel(values)` returns the resistance of a list of resistors in parallel. Use
  the conductance form, $1/R = \sum 1/R_i$, so that it works for any number of them,
  not just two.
- `missing_current(into, out_of)` applies KCL at a node: given a list of the currents
  flowing **in** and a list of the currents known to flow **out**, return the current
  in the one remaining branch, taken as positive when it flows out of the node.

`sum()` will do most of the work. For `parallel`, a generator expression inside
`sum()` adds the reciprocals in one line.
''',
                "files": [{"name": "main.py", "content": r'''
"""Series, parallel, and Kirchhoff's current law."""


def series(values):
    """Total resistance of resistors carrying the same current."""
    # TODO: in series, resistances add.
    return 0.0


def parallel(values):
    """Total resistance of resistors sharing the same voltage."""
    # TODO: add the reciprocals, then take the reciprocal of the sum.
    return 0.0


def missing_current(into, out_of):
    """KCL: the current in the one branch not yet accounted for."""
    # TODO: everything that goes in must come out.
    return 0.0


if __name__ == "__main__":
    pair = parallel([4000.0, 4000.0])
    print("two 4k in parallel:", pair, "ohms")
    print("with another 4k in series:", series([4000.0, pair]), "ohms")
    print("third branch of the node:", missing_current([3.0], [1.2, 0.5]), "A")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Series, parallel, and Kirchhoff's current law."""


def series(values):
    """Total resistance of resistors carrying the same current."""
    return sum(values)


def parallel(values):
    """Total resistance of resistors sharing the same voltage."""
    return 1.0 / sum(1.0 / v for v in values)


def missing_current(into, out_of):
    """KCL: the current in the one branch not yet accounted for."""
    return sum(into) - sum(out_of)


if __name__ == "__main__":
    pair = parallel([4000.0, 4000.0])
    print("two 4k in parallel:", pair, "ohms")
    print("with another 4k in series:", series([4000.0, pair]), "ohms")
    print("third branch of the node:", missing_current([3.0], [1.2, 0.5]), "A")
'''}],
                "hints": [
                    "`series` is `sum(values)`.",
                    "`parallel` is `1.0 / sum(1.0 / v for v in values)`. Adding the reciprocals is adding the conductances.",
                    "`missing_current` is the total in minus the total out — a single subtraction of two sums.",
                    "A useful self-check: `parallel` must always return something smaller than the smallest resistor you gave it.",
                ],
                "tests": [
                    {"name": "series adds", "code": r'''
assert abs(series([4000.0, 4000.0]) - 8000.0) < 1e-9, "two 4k in series is 8k"
assert abs(series([1000.0, 2200.0, 470.0]) - 3670.0) < 1e-9, "1k + 2k2 + 470 is 3670"
'''},
                    {"name": "two equal resistors in parallel halve", "code": r'''
p = parallel([4000.0, 4000.0])
assert abs(p - 2000.0) < 1e-9, f"two 4k in parallel is 2k, got {p}"
'''},
                    {"name": "parallel works for three, and always shrinks", "code": r'''
p = parallel([1000.0, 2200.0, 470.0])
assert p < 470.0, f"a parallel total must be below the smallest part, got {p}"
assert abs(p - 279.1576673866091) < 1e-6, \
    f"1k, 2k2 and 470 in parallel is about 279.158 ohms, got {p}"
'''},
                    {"name": "the module 3 circuit comes out at 6 kilohms", "code": r'''
total = series([4000.0, parallel([4000.0, 4000.0])])
assert abs(total - 6000.0) < 1e-9, f"4k in series with 4k||4k is 6k, got {total}"
assert abs(12.0 / total - 0.002) < 1e-12, "12 V across 6k is 2 mA"
'''},
                    {"name": "KCL finds the missing branch", "code": r'''
i = missing_current([3.0], [1.2, 0.5])
assert abs(i - 1.3) < 1e-12, f"3.0 in, 1.7 accounted for, so 1.3 A left, got {i}"
j = missing_current([0.4, 0.25], [0.5])
assert abs(j - 0.15) < 1e-12, f"0.65 in, 0.5 out, so 0.15 A left, got {j}"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "The voltage divider, loading and the power budget",
            "summary": "Two resistors in series split a supply in proportion — until something is connected across the output.",
            "concepts": [
                "Two resistors in series across a supply divide it in proportion to their resistances: $V_{out} = V_{in}\\,R_2/(R_1+R_2)$, with $R_2$ the one the output is taken across.",
                "The ratio depends only on the *ratio* of the two resistors. Scaling both by ten leaves the output alone and divides the current by ten.",
                "The divider formula assumes nothing is drawn from the output. Anything connected there sits in parallel with $R_2$ and pulls the output down.",
                "A *stiff* divider is one whose own current is much larger than the load current; the usual rule of thumb is at least ten times, and never less than twice.",
                "Stiffness costs heat. Every milliamp of divider current is a milliamp the supply pays for, whether a load uses it or not.",
                "Conservation of energy gives a free check on any solution: the power the supply delivers must equal the sum of the powers dissipated in every resistor.",
            ],
            "sandbox": {
                "title": "A ratio, read as a gain",
                "visualiser": "bode",
                "minutes": 7,
                "initial": {"wn": 60, "zeta": 0.9, "K": 0.5},
                "brief": r'''
A divider does one thing: it multiplies its input by a fixed number smaller than one.
Engineers usually quote that number as a **gain**, and often in **decibels**, where a
gain $G$ is written as $20\log_{10}G$ dB.

The top plot here is gain in decibels; the bottom is a phase shift, which for a
resistive divider is always zero. The horizontal axis is frequency, which does not
appear anywhere in this course — a network of resistors alone behaves identically at
every frequency, so a resistive divider is the perfectly **flat** left-hand part of
this picture and nothing else. The curved right-hand part arrives in EE102, when
capacitors join in.

The slider $K$ is the gain. Leave the other two alone at first.
''',
                "notice": [
                    "$K$ opens at 0.5 — a divider that halves its input — and the flat left-hand part of the top plot sits at −6 dB. Those are two ways of saying the same thing.",
                    "Take $K$ down to 0.1 and the flat part drops to −20 dB. Every further factor of ten in the ratio costs another 20 dB, which is the whole reason decibels are used.",
                    "The bottom plot starts at 0° on the far left and stays within a few degrees of it out to about $\\omega = 3$: there the output rises and falls in step with the input, simply smaller, which is all a resistive divider ever does. Read further right and the phase bends away long before the gain visibly does — at $\\omega = 20$ the top plot still looks flat while the phase has already reached −34°.",
                    "Drag the corner $\\omega_n$ to its maximum, 200, and the flat region covers most of the plot. A purely resistive divider is the limit where the corner has gone off to infinity and only the flat part is left.",
                ],
            },
            "quiz": {
                "title": "Dividers under load",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A 9 V supply feeds 20 kΩ in series with 10 kΩ, with the output taken across the 10 kΩ. With nothing connected to the output, what is it?",
                        "opts": ["6 V", "3 V", "4.5 V", "0.3 V"],
                        "a": 1,
                        "why": r'''
$V_{out} = 9 \times 10/(20+10) = 3$ V. The 10 kΩ is one third of the total 30 kΩ, so it
gets one third of the supply. Answering 6 V means using the *upper* resistor on top of
the fraction — always put the resistance you are measuring across on top, and sanity
check the result: the output must land between 0 V and the supply, and closer to
whichever resistor is larger.
''',
                    },
                    {
                        "q": "You replace that divider's 20 kΩ and 10 kΩ with 200 kΩ and 100 kΩ. With nothing connected to the output, what changes?",
                        "opts": [
                            "the output is still 3 V, and the current falls to a tenth",
                            "the output falls to 0.3 V",
                            "the output rises to 30 V",
                            "nothing at all changes",
                        ],
                        "a": 0,
                        "why": r'''
The output depends only on the ratio, which is unchanged, so it is still 3 V. What
changes is the current: 0.3 mA becomes 0.03 mA, and the power wasted in the divider
falls by the same factor of ten. That is not a free lunch, though — the higher the
resistances, the more the output sags when a load is connected, which is the next
question.
''',
                    },
                    {
                        "q": "A divider is set up to give 3 V. You then connect a load resistor across the output, equal in value to the lower resistor. What happens to the output?",
                        "opts": [
                            "it stays at 3 V, because the divider sets the voltage",
                            "it falls, because the load is in parallel with the lower resistor",
                            "it rises, because there is now more current",
                            "it falls to zero",
                        ],
                        "a": 1,
                        "why": r'''
It falls. The load sits in parallel with the lower resistor, and a parallel pair is
always smaller than either part — here half of the lower resistor. The divider now
splits its supply between the upper resistor and a *smaller* lower one, so the output
drops. This is the single most common surprise in practical work: a divider that
measures perfectly with a meter on it collapses the moment something real is attached.
''',
                    },
                    {
                        "q": "In an unloaded divider of 20 kΩ on top and 10 kΩ below, which resistor dissipates more power?",
                        "opts": [
                            "the 10 kΩ, because more current flows through it",
                            "the 20 kΩ",
                            "the same, because they are in series",
                            "it depends on the supply voltage",
                        ],
                        "a": 1,
                        "why": r'''
They carry the same current, being in series, so $P = I^2R$ makes the larger resistance
the hotter one — twice as hot here. Option A misreads series for parallel: the current
through both is identical, which is exactly why $I^2R$ is the right form to reach for.
''',
                    },
                    {
                        "q": "A 9 V supply drives a divider drawing 0.3 mA, and the two resistors dissipate 1.8 mW and 0.9 mW. What must the supply be delivering?",
                        "opts": ["0.9 mW", "1.8 mW", "2.7 mW", "it cannot be worked out from this"],
                        "a": 2,
                        "why": r'''
2.7 mW, and there are two ways to see it. Directly: $P = VI = 9 \times 0.0003$. By
conservation: energy cannot go anywhere except into those two resistors, so the two
dissipations must add up to what the supply provides. Whenever those two numbers
disagree in your own work, there is an arithmetic error somewhere — it is the cheapest
check in circuit analysis, and it is the one the capstone is built around.
''',
                    },
                ],
            },
            "build": {
                "title": "A 3 V rail that survives its load",
                "minutes": 28,
                "brief": r'''
A 9 V battery has to supply a sensor that needs **3.00 V** and behaves, electrically,
exactly like a 100 kΩ resistor to ground. The battery is small, so the whole circuit
may draw no more than **500 µA**.

The canvas opens with the battery, the 100 kΩ load already in place, the grounds, and
a probe on the load. Add the two divider resistors so that

- the probe reads 3.00 V **with the load connected**,
- the supply delivers between 90 µA and 500 µA.

The lower bound is a design rule rather than a law. At 3.00 V the load itself takes
$3/100\text{k} = 30$ µA, and a divider carrying less than about twice its load current
sags badly when the load changes — so the divider wants 60 µA of its own, and the
supply, which carries the divider current *and* the load current, wants 90 µA. The
upper bound is the battery.

## The trap

Designing this as though the load were not there gives 20 kΩ over 10 kΩ — and measures
2.81 V, which fails. The load is in parallel with your lower resistor, and the two of
them together are what forms the bottom half of the divider. Work out what the *pair*
must come to, then work out what the lower resistor has to be so that the pair comes
to that.

Values need not be round numbers. Type them as you like — `11.1k` is understood, and
so is `11111`.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p5", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 100000},
                        {"id": "p6", "kind": "GND", "x": 13, "y": 11},
                        {"id": "p7", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 8], "b": [13, 8]},
                        {"a": [13, 10], "b": [13, 11]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 9},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 9, "y": 6, "rot": 1, "value": 20000},
                        {"id": "p3", "kind": "R", "x": 9, "y": 9, "rot": 1, "value": 11111.111111111111},
                        {"id": "p4", "kind": "GND", "x": 9, "y": 11},
                        {"id": "p5", "kind": "R", "x": 13, "y": 9, "rot": 1, "value": 100000},
                        {"id": "p6", "kind": "GND", "x": 13, "y": 11},
                        {"id": "p7", "kind": "OUT", "x": 11, "y": 8},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [9, 5]},
                        {"a": [9, 7], "b": [9, 8]},
                        {"a": [9, 8], "b": [13, 8]},
                        {"a": [9, 10], "b": [9, 11]},
                        {"a": [13, 10], "b": [13, 11]},
                    ],
                },
                "checks": [
                    {"name": "the 100 kΩ load is still across the output", "code": r'''
const rs = c.values('R');
c.assert(rs.some(function (r) { return Math.abs(r - 100000) <= 1000; }),
  'The 100 kΩ load is the problem, not an obstacle — leave it in the circuit.');
c.assert(rs.length >= 3,
  'A divider is two resistors, and with the load that makes at least three. Found ' + rs.length + '.');
const out = c.outNode();
c.assert(c.net.parts.some(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 100000) <= 1000 &&
    ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
}), 'The 100 kΩ load must run from the probed node to ground — a load left dangling ' +
   'is no load at all, and the whole point of this exercise is what happens when it is there.');
'''},
                    {"name": "one 9 V battery drives it", "code": r'''
c.assert(c.count('V') === 1, 'Use exactly one voltage source; found ' + c.count('V') + '.');
c.close(c.values('V')[0], 9, 0.001, 'the supply voltage');
'''},
                    {"name": "the load sees 3.00 V", "code": r'''
c.close(c.vout(), 3.0, 0.02,
  'the voltage at the load — remember the load is in parallel with your lower resistor');
'''},
                    {"name": "the battery gives between 90 µA and 500 µA", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the supply current" means one thing.');
const i = Math.abs(cur[ids[0]]);
/* both bounds carry a rounding allowance, so a design sitting exactly on one of
   them is not failed by the last decimal place of a resistor value */
c.assert(i <= 500e-6 * 1.005,
  'The battery may not be asked for more than 500 µA; this circuit draws ' + c.fmt(i, 'A') + '.');
c.assert(i >= 90e-6 * 0.99,
  'The load takes 30 µA and the divider should carry at least twice that on its own, ' +
  'so the supply must deliver at least 90 µA; this circuit draws ' + c.fmt(i, 'A') + '.');
'''},
                ],
                "hints": [
                    "Call the parallel combination of your lower resistor and the 100 kΩ load $X$. The circuit is then an ordinary two-resistor divider of $R_{top}$ and $X$.",
                    "For 3 V out of 9 V, $X$ must be one third of the total, which means $R_{top} = 2X$.",
                    "Pick $X$ first from the current budget: the supply current is $9/(R_{top}+X) = 9/(3X)$, so $X = 10$ kΩ gives 300 µA, comfortably inside both limits.",
                    "Then solve $1/X = 1/R_{low} + 1/100\\text{k}$ for $R_{low}$. With $X = 10$ kΩ it comes to about 11.1 kΩ, and $R_{top}$ is 20 kΩ.",
                ],
            },
            "lab": {
                "title": "Designing the divider you just drew",
                "runtime": "python",
                "minutes": 26,
                "brief": r'''
The algebra behind the circuit, so that the next one takes a second rather than a
sheet of paper.

- `divider_out(vin, r_top, r_bottom)` — the output with nothing connected to it.
- `loaded_out(vin, r_top, r_bottom, r_load)` — the output when `r_load` is connected
  across the bottom resistor. Combine the two lower resistors in parallel first, then
  reuse `divider_out`.
- `bottom_for(vin, vout, r_top, r_load)` — the value the bottom resistor must have so
  that the loaded output is exactly `vout`.

For the last one, work backwards. If the parallel combination of the bottom resistor
and the load is $X$, then $v_{out} = v_{in}X/(R_{top}+X)$, and solving for $X$ gives

```text
X = r_top * ratio / (1 - ratio)      where ratio = vout / vin
```

Then recover the bottom resistor from $1/X = 1/R_{bottom} + 1/R_{load}$.
''',
                "files": [{"name": "main.py", "content": r'''
"""Voltage dividers, with and without a load."""


def divider_out(vin, r_top, r_bottom):
    """Output voltage of an unloaded divider, measured across r_bottom."""
    # TODO: vin times the fraction of the total resistance that r_bottom holds.
    return 0.0


def loaded_out(vin, r_top, r_bottom, r_load):
    """Output voltage when r_load is connected across r_bottom."""
    # TODO: combine r_bottom and r_load in parallel, then call divider_out.
    return 0.0


def bottom_for(vin, vout, r_top, r_load):
    """Bottom resistor that gives exactly `vout` with `r_load` connected."""
    # TODO: find the parallel value X that the divider needs, then undo the parallel.
    return 0.0


if __name__ == "__main__":
    print("unloaded 20k/10k from 9 V:", divider_out(9.0, 20000.0, 10000.0), "V")
    print("with a 100k load:", loaded_out(9.0, 20000.0, 10000.0, 100000.0), "V")
    rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
    print("bottom resistor for a true 3 V:", rb, "ohms")
    print("check:", loaded_out(9.0, 20000.0, rb, 100000.0), "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Voltage dividers, with and without a load."""


def divider_out(vin, r_top, r_bottom):
    """Output voltage of an unloaded divider, measured across r_bottom."""
    return vin * r_bottom / (r_top + r_bottom)


def loaded_out(vin, r_top, r_bottom, r_load):
    """Output voltage when r_load is connected across r_bottom."""
    pair = 1.0 / (1.0 / r_bottom + 1.0 / r_load)
    return divider_out(vin, r_top, pair)


def bottom_for(vin, vout, r_top, r_load):
    """Bottom resistor that gives exactly `vout` with `r_load` connected."""
    ratio = vout / vin
    x = r_top * ratio / (1.0 - ratio)
    return 1.0 / (1.0 / x - 1.0 / r_load)


if __name__ == "__main__":
    print("unloaded 20k/10k from 9 V:", divider_out(9.0, 20000.0, 10000.0), "V")
    print("with a 100k load:", loaded_out(9.0, 20000.0, 10000.0, 100000.0), "V")
    rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
    print("bottom resistor for a true 3 V:", rb, "ohms")
    print("check:", loaded_out(9.0, 20000.0, rb, 100000.0), "V")
'''}],
                "hints": [
                    "`divider_out` is `vin * r_bottom / (r_top + r_bottom)`. The resistance you measure across goes on top of the fraction.",
                    "`loaded_out` should not repeat the divider formula: work out the parallel pair, then hand it to `divider_out` as the new bottom resistor.",
                    "In `bottom_for`, `ratio` is `vout / vin`, and `x` is the parallel value the divider needs. Then undo the parallel with `1 / (1/x - 1/r_load)`.",
                    "If `bottom_for` returns a negative number, the output you asked for is impossible with that top resistor and that load — the load alone already pulls the output below the target.",
                ],
                "tests": [
                    {"name": "the unloaded divider splits by ratio", "code": r'''
v = divider_out(9.0, 20000.0, 10000.0)
assert abs(v - 3.0) < 1e-12, f"10k of 30k from 9 V is 3 V, got {v}"
assert abs(divider_out(9.0, 200000.0, 100000.0) - 3.0) < 1e-12, \
    "scaling both resistors by ten must not change the output"
'''},
                    {"name": "a load pulls the output down", "code": r'''
v = loaded_out(9.0, 20000.0, 10000.0, 100000.0)
assert abs(v - 2.8125) < 1e-9, \
    f"10k in parallel with 100k is 9090.9 ohms, giving 2.8125 V, got {v}"
assert v < divider_out(9.0, 20000.0, 10000.0), "the loaded output must be the lower one"
'''},
                    {"name": "a very light load barely matters", "code": r'''
v = loaded_out(9.0, 20000.0, 10000.0, 1e9)
assert abs(v - 3.0) < 1e-4, f"a 1 G-ohm load should leave the divider alone, got {v}"
'''},
                    {"name": "the design function hits the target", "code": r'''
rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
assert abs(rb - 11111.111111111111) < 1e-6, \
    f"the bottom resistor should be about 11.111 k, got {rb}"
back = loaded_out(9.0, 20000.0, rb, 100000.0)
assert abs(back - 3.0) < 1e-9, f"feeding it back should give exactly 3 V, got {back}"
'''},
                    {"name": "it also works for a different rail", "code": r'''
rb = bottom_for(5.0, 3.3, 33000.0, 100000.0)
back = loaded_out(5.0, 33000.0, rb, 100000.0)
assert abs(back - 3.3) < 1e-9, f"expected 3.3 V back, got {back}"
assert rb > 0, f"a positive resistor should be possible here, got {rb}"
'''},
                ],
            },
        },
    ],

    # ---- capstone ---------------------------------------------------------
    "capstone": {
        "title": "A solver for any resistor network",
        "runtime": "python",
        "minutes": 120,
        "brief": r'''
Everything in this course has been a network simple enough to reduce by inspection.
Most networks are not, so engineers solve them a different way: write Kirchhoff's
current law at every node at once, and let linear algebra do the rest. That method is
called **nodal analysis**, and it is what every circuit simulator in the world does
underneath. You are going to write one.

## The idea, in one paragraph

Number the nodes. Ground is node 0 and its voltage is defined as 0 V. For every other
node, KCL says the currents leaving it through the resistors attached to it add up to
zero. The current leaving node $a$ towards node $b$ through a resistance $R$ is
$(v_a - v_b)/R$ by Ohm's law. Writing that out for every node gives one linear
equation per unknown voltage, and a linear system is something a computer solves
without thinking. Where a supply holds a node at a fixed voltage, that node's equation
is simply $v = V$, and it replaces the KCL equation there.

`dcsolve.py` gives you `linsolve(A, b)`, which solves $Ax = b$ by Gaussian
elimination. You do not need to read it, and you may not edit it. Your work is
building `A` and `b` from the circuit — the physics — and then reading useful
quantities back out.

## What you are building

Represent a circuit as

```text
n_nodes    how many non-ground nodes there are, numbered 1..n_nodes
resistors  a list of (a, b, ohms) triples; node 0 means ground
fixed      a dict {node: volts} of nodes held at a known voltage by a supply
```

Then implement, in `main.py`:

1. `solve_network(n_nodes, resistors, fixed)` — returns a list of voltages of length
   `n_nodes + 1`, with `voltages[0] == 0.0` for ground.
2. `branch_current(voltages, a, b, ohms)` — the current flowing from node `a` to node
   `b` through that resistor.
3. `supply_current(voltages, resistors, node)` — the current a supply must push into
   `node`, which is the sum of the currents leaving that node through every resistor
   attached to it.
4. `power_report(voltages, resistors, fixed)` — returns the tuple
   `(supplied, dissipated)`: the total power out of all supplies, and the total power
   turned into heat by all resistors. If your solver is right these two agree to many
   decimal places, and that is the check you should run on every circuit you ever
   solve.
5. `bottom_for(vin, vout, r_top, r_load)` — the loaded-divider design function from
   module 4, brought along so the capstone can design a circuit and then verify it
   with the solver.

## Building the matrix

For each resistor `(a, b, R)` with conductance $g = 1/R$, add $g$ to the diagonal of
both `a` and `b`, and subtract $g$ from the two off-diagonal entries joining them —
skipping anything involving node 0, which has no row and no column because its
voltage is already known. That pattern is exactly KCL written out; work through a
two-node example by hand once and you will never need to look it up again.

Then, for each fixed node, throw away the row you just built for it and put a single
1 on its diagonal with the known voltage on the right-hand side.

## Suggested order

Get `solve_network` right on a single resistor first — one node, one equation, and you
can check the answer in your head. Then a divider, then the ladder in the tests. The
power report is the last thing to write and the first thing to trust.

The Python is a step up from the one-line labs, but only a step: a list of lists, a
couple of `for` loops, and a dictionary you walk with `.items()`. Nothing else, and
the hints spell out each piece. If those constructs are new, EE131 (Programming for
Engineers) covers them in its first weeks and runs alongside this course.
''',
        "deliverables": [
            "`solve_network`, building the conductance matrix from the resistor list and solving it, with ground fixed at 0 V and every supply node fixed at its stated voltage.",
            "`branch_current`, returning the current through one named resistor from the solved node voltages.",
            "`supply_current`, returning the current a supply pushes into a fixed node, by summing what leaves that node through the resistors.",
            "`power_report`, returning total supplied and total dissipated power, which must agree for any correct solution.",
            "`bottom_for`, the loaded-divider design function, plus a comment in `main.py` naming one circuit you designed with it and verified with `solve_network`.",
        ],
        "constraints": [
            "The standard library only. No NumPy, and certainly no circuit-simulation package — `linsolve` in `dcsolve.py` is the only linear algebra you need.",
            "Do not edit `dcsolve.py`.",
            "Node 0 is ground and always has voltage 0.0. It never gets a row or a column in the matrix.",
            "`solve_network` must work for any number of nodes, not just the sizes that appear in the checks.",
            "Do not special-case the test circuits. A solver that recognises a divider and returns the divider formula is not a solver.",
        ],
        "rubric": [
            {"criterion": "Matrix assembly", "weight": 30,
             "evidence": "Conductances are stamped on the diagonal and off-diagonal correctly, ground is excluded, and fixed nodes replace their own row — demonstrated on networks of one, two and three unknown nodes."},
            {"criterion": "Currents from voltages", "weight": 20,
             "evidence": "branch_current and supply_current return the right magnitude and the right sign on a divider and on a ladder, matching hand calculations."},
            {"criterion": "Power conservation", "weight": 25,
             "evidence": "power_report's two totals agree to within 1e-9 on every test network, which is only possible if the node voltages are genuinely correct."},
            {"criterion": "Design and verification", "weight": 25,
             "evidence": "bottom_for produces a resistor that, when fed back through solve_network as a real three-resistor circuit, gives the requested output voltage."},
        ],
        "hints": [
            "Build the matrix as a list of lists of floats, size `n_nodes` by `n_nodes`, and index node `k` at row and column `k - 1`.",
            "Guard every stamp with `if a:` and `if b:` — node 0 is ground and has no row.",
            "For a fixed node, overwrite its whole row with zeros and a single 1.0 on the diagonal, and set that entry of the right-hand side to the supply voltage. Do this after all the resistors are stamped, not before.",
            "`supply_current` should loop over the resistor list and pick out the ones with the node at either end, remembering that `(a, b, R)` might have the node in either position.",
            "If the two power totals disagree, the sign convention in `supply_current` is the usual culprit: the power a supply delivers is its voltage times the current flowing *out* of it into the network.",
        ],
        "files": [
            {"name": "dcsolve.py", "ro": True, "content": r'''
"""Gaussian elimination with partial pivoting. Do not edit.

This is the one piece of machinery the capstone hands you: given a square matrix A
and a right-hand side b, it returns the x that satisfies A x = b. Nothing in it knows
anything about circuits, which is the point — the physics is entirely in how you fill
A and b in.
"""


def linsolve(A, b):
    """Solve A x = b for x. A is a list of rows; b is a list. Returns a list."""
    n = len(b)
    M = [list(map(float, A[i])) + [float(b[i])] for i in range(n)]

    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[pivot][col]) < 1e-15:
            raise ValueError(
                "singular matrix: node %d has no path to a known voltage" % (col + 1)
            )
        M[col], M[pivot] = M[pivot], M[col]
        for r in range(col + 1, n):
            f = M[r][col] / M[col][col]
            if f == 0.0:
                continue
            for k in range(col, n + 1):
                M[r][k] -= f * M[col][k]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = M[i][n] - sum(M[i][k] * x[k] for k in range(i + 1, n))
        x[i] = s / M[i][i]
    return x
'''},
            {"name": "main.py", "content": r'''
"""Nodal analysis: Kirchhoff's current law, written once and solved for any network.

Designed and verified with this file:
    TODO: name a circuit you designed with bottom_for and checked with solve_network.
"""

from dcsolve import linsolve


def solve_network(n_nodes, resistors, fixed):
    """Node voltages of a resistor network.

    n_nodes    number of non-ground nodes, numbered 1..n_nodes
    resistors  list of (a, b, ohms); node 0 is ground
    fixed      dict {node: volts} for nodes held by a supply

    Returns a list of length n_nodes + 1 whose first entry is 0.0 (ground).
    """
    A = [[0.0] * n_nodes for _ in range(n_nodes)]
    b = [0.0] * n_nodes
    # TODO: stamp every resistor's conductance into A, skipping node 0.
    # TODO: replace the row of each fixed node with 1.0 on the diagonal.
    return [0.0] * (n_nodes + 1)


def branch_current(voltages, a, b, ohms):
    """Current flowing from node a to node b through a resistor of `ohms`."""
    # TODO: Ohm's law across the two node voltages.
    return 0.0


def supply_current(voltages, resistors, node):
    """Current a supply must push into `node` to hold it where it is."""
    # TODO: sum what leaves `node` through every resistor attached to it.
    return 0.0


def power_report(voltages, resistors, fixed):
    """Return (supplied, dissipated) in watts. They should be equal."""
    # TODO: supplies deliver V * I; resistors dissipate (dV)^2 / R.
    return (0.0, 0.0)


def bottom_for(vin, vout, r_top, r_load):
    """Bottom resistor of a divider giving `vout` with `r_load` connected."""
    # TODO: the module 4 design formula.
    return 0.0


if __name__ == "__main__":
    # a 9 V supply, 20 k on top, 11.1 k below, feeding a 100 k load
    rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
    net = [(1, 2, 20000.0), (2, 0, rb), (2, 0, 100000.0)]
    v = solve_network(2, net, {1: 9.0})
    print("node voltages:", [round(x, 6) for x in v])
    print("supply current:", supply_current(v, net, 1), "A")
    print("power (supplied, dissipated):", power_report(v, net, {1: 9.0}))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""Nodal analysis: Kirchhoff's current law, written once and solved for any network.

Designed and verified with this file:
    a 3.00 V rail for a 100 k load, taken from a 9 V battery with a 20 k top
    resistor. bottom_for gives 11111.11 ohms; solve_network on the resulting
    three-resistor circuit returns 3.000000 V at the load and 300 uA out of the
    battery, and the two halves of power_report agree to 1e-18.
"""

from dcsolve import linsolve


def solve_network(n_nodes, resistors, fixed):
    """Node voltages of a resistor network.

    n_nodes    number of non-ground nodes, numbered 1..n_nodes
    resistors  list of (a, b, ohms); node 0 is ground
    fixed      dict {node: volts} for nodes held by a supply

    Returns a list of length n_nodes + 1 whose first entry is 0.0 (ground).
    """
    A = [[0.0] * n_nodes for _ in range(n_nodes)]
    b = [0.0] * n_nodes

    for (a, bb, ohms) in resistors:
        g = 1.0 / ohms
        if a:
            A[a - 1][a - 1] += g
        if bb:
            A[bb - 1][bb - 1] += g
        if a and bb:
            A[a - 1][bb - 1] -= g
            A[bb - 1][a - 1] -= g

    for node, volts in fixed.items():
        A[node - 1] = [0.0] * n_nodes
        A[node - 1][node - 1] = 1.0
        b[node - 1] = float(volts)

    return [0.0] + list(linsolve(A, b))


def branch_current(voltages, a, b, ohms):
    """Current flowing from node a to node b through a resistor of `ohms`."""
    return (voltages[a] - voltages[b]) / ohms


def supply_current(voltages, resistors, node):
    """Current a supply must push into `node` to hold it where it is."""
    total = 0.0
    for (a, b, ohms) in resistors:
        if a == node:
            total += branch_current(voltages, a, b, ohms)
        elif b == node:
            total += branch_current(voltages, b, a, ohms)
    return total


def power_report(voltages, resistors, fixed):
    """Return (supplied, dissipated) in watts. They should be equal."""
    supplied = 0.0
    for node, volts in fixed.items():
        supplied += float(volts) * supply_current(voltages, resistors, node)
    dissipated = 0.0
    for (a, b, ohms) in resistors:
        dv = voltages[a] - voltages[b]
        dissipated += dv * dv / ohms
    return (supplied, dissipated)


def bottom_for(vin, vout, r_top, r_load):
    """Bottom resistor of a divider giving `vout` with `r_load` connected."""
    ratio = vout / vin
    x = r_top * ratio / (1.0 - ratio)
    return 1.0 / (1.0 / x - 1.0 / r_load)


if __name__ == "__main__":
    # a 9 V supply, 20 k on top, 11.1 k below, feeding a 100 k load
    rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
    net = [(1, 2, 20000.0), (2, 0, rb), (2, 0, 100000.0)]
    v = solve_network(2, net, {1: 9.0})
    print("node voltages:", [round(x, 6) for x in v])
    print("supply current:", supply_current(v, net, 1), "A")
    print("power (supplied, dissipated):", power_report(v, net, {1: 9.0}))
'''},
        ],
        "tests": [
            {"name": "one resistor across a supply", "code": r'''
net = [(1, 0, 3000.0)]
v = solve_network(1, net, {1: 12.0})
assert len(v) == 2, f"one non-ground node means two voltages including ground, got {len(v)}"
assert abs(v[0]) < 1e-12, "node 0 is ground and must be exactly 0 V"
assert abs(v[1] - 12.0) < 1e-9, f"the supply holds node 1 at 12 V, got {v[1]}"
i = branch_current(v, 1, 0, 3000.0)
assert abs(i - 0.004) < 1e-12, f"12 V across 3 k is 4 mA, got {i}"
'''},
            {"name": "a loaded divider matches the hand calculation", "code": r'''
net = [(1, 2, 20000.0), (2, 0, 10000.0), (2, 0, 100000.0)]
v = solve_network(2, net, {1: 9.0})
assert abs(v[1] - 9.0) < 1e-9, f"node 1 is held at 9 V, got {v[1]}"
assert abs(v[2] - 2.8125) < 1e-9, \
    f"10k parallel 100k is 9090.9 ohms, so the output is 2.8125 V, got {v[2]}"
'''},
            {"name": "a three-node ladder", "code": r'''
net = [(1, 2, 1000.0), (2, 0, 1000.0), (2, 3, 1000.0), (3, 0, 1000.0)]
v = solve_network(3, net, {1: 10.0})
assert abs(v[2] - 4.0) < 1e-9, f"node 2 should sit at 4 V, got {v[2]}"
assert abs(v[3] - 2.0) < 1e-9, f"node 3 should sit at 2 V, got {v[3]}"
i = supply_current(v, net, 1)
assert abs(i - 0.006) < 1e-12, f"6 V across the first 1 k is 6 mA out of the supply, got {i}"
'''},
            {"name": "energy is conserved on the ladder", "code": r'''
net = [(1, 2, 1000.0), (2, 0, 1000.0), (2, 3, 1000.0), (3, 0, 1000.0)]
v = solve_network(3, net, {1: 10.0})
supplied, dissipated = power_report(v, net, {1: 10.0})
assert abs(supplied - 0.06) < 1e-12, f"10 V at 6 mA is 60 mW supplied, got {supplied}"
assert abs(supplied - dissipated) < 1e-9, \
    f"supplied {supplied} and dissipated {dissipated} must agree"
'''},
            {"name": "energy is conserved on the divider too", "code": r'''
net = [(1, 2, 20000.0), (2, 0, 11111.111111111111), (2, 0, 100000.0)]
v = solve_network(2, net, {1: 9.0})
supplied, dissipated = power_report(v, net, {1: 9.0})
assert abs(supplied - 0.0027) < 1e-12, f"9 V at 300 uA is 2.7 mW, got {supplied}"
assert abs(supplied - dissipated) < 1e-12, \
    f"supplied {supplied} and dissipated {dissipated} must agree"
'''},
            {"name": "a design, verified by the solver", "code": r'''
rb = bottom_for(9.0, 3.0, 20000.0, 100000.0)
assert abs(rb - 11111.111111111111) < 1e-6, f"expected about 11.111 k, got {rb}"
net = [(1, 2, 20000.0), (2, 0, rb), (2, 0, 100000.0)]
v = solve_network(2, net, {1: 9.0})
assert abs(v[2] - 3.0) < 1e-9, f"the designed divider should give 3.000 V, got {v[2]}"
i = supply_current(v, net, 1)
assert abs(i - 0.0003) < 1e-12, f"the battery should give 300 uA, got {i}"
'''},
            {"name": "a second design, on a different rail", "code": r'''
rb = bottom_for(5.0, 3.3, 33000.0, 100000.0)
net = [(1, 2, 33000.0), (2, 0, rb), (2, 0, 100000.0)]
v = solve_network(2, net, {1: 5.0})
assert abs(v[2] - 3.3) < 1e-9, f"expected 3.3 V, got {v[2]}"
supplied, dissipated = power_report(v, net, {1: 5.0})
assert abs(supplied - dissipated) < 1e-12, "the power check must hold here as well"
'''},
            {"name": "the solver is general, not a divider in disguise", "code": r'''
net = [(1, 2, 500.0), (2, 3, 1500.0), (3, 0, 2000.0), (2, 0, 4000.0), (1, 3, 8000.0)]
v = solve_network(3, net, {1: 24.0})
assert abs(v[1] - 24.0) < 1e-9, "node 1 is fixed by the supply"
for k in (2, 3):
    leaving = 0.0
    for (a, b, r) in net:
        if a == k:
            leaving += branch_current(v, a, b, r)
        elif b == k:
            leaving += branch_current(v, b, a, r)
    assert abs(leaving) < 1e-9, \
        f"KCL must hold at node {k}: currents leaving sum to {leaving}, not 0"
supplied, dissipated = power_report(v, net, {1: 24.0})
assert supplied > 0, "the supply should be delivering power, not absorbing it"
assert abs(supplied - dissipated) < 1e-9, \
    f"supplied {supplied} and dissipated {dissipated} must agree"
'''},
        ],
    },
}
