"""EE221 — Measurement and Instrumentation.

Second year. It assumes the first-year circuits sequence: DC analysis, AC steady
state, phasors and impedance, complex numbers and calculus, and enough Python to
write a function. It assumes nothing above that.

Authoring rules, as for every course module:

  * every multi-line body is r'''...''' opening on a newline, never r\"\"\"
  * file contents start at column 0 — clean_code does not dedent them
  * numpy and the standard library only
  * every expected number was produced by running the code, not assumed
  * build checks are JavaScript against the circuit API, and they measure what the
    circuit does rather than compare it to the reference drawing
  * sandbox notices were written after reading the visualiser's source in
    src/studio.js, and describe what that code actually draws at those values

The two circuit exercises were run through src/circuit.js while being written:
the module 1 reference gives 9.900990 V at the tip, 0.990099 V at the probe and
990.099 nA out of the source; the module 2 reference holds the ratio at 0.100000
at 100 Hz, 1 kHz, 10 kHz, 100 kHz, 1 MHz and 10 MHz, where the uncompensated
start falls to 0.0008842 at 1 MHz.
"""

COURSE = {
    "id": "EE221",
    "title": "Measurement and Instrumentation",
    "band": 2,
    "level": "Intermediate",
    "prereqs": ["EE102"],
    "stack": ["Python", "NumPy"],
    "credits": 10,
    "hours": 120,
    "icon": "▤",
    "summary": (
        "Every measurement changes the thing it measures, and every instrument has a "
        "floor below which it is inventing digits. This course is about the gap between "
        "the number on the display and the quantity in the circuit: what the meter's "
        "input resistance did to the node, what the probe's capacitance did to the edge, "
        "what the amplifier's noise did to the last two digits, and what any of it "
        "entitles you to claim. It ends where a laboratory notebook should end, with a "
        "value, an uncertainty, and a statement of where that uncertainty came from."
    ),
    "outcomes": [
        "Predict the loading error an instrument of stated input impedance imposes on a node of stated Thévenin impedance, at DC and at frequency, and correct for it.",
        "Explain what a ×10 probe is made of, why it needs compensating, and what an uncompensated or badly grounded probe does to a fast edge.",
        "Convert between bandwidth and rise time, and separate the instrument's contribution from the signal's in a measured edge.",
        "Design a Wheatstone bridge for a resistive sensor, choosing an excitation that trades signal against self-heating, and account for the bridge's own nonlinearity.",
        "Distinguish random from systematic error, use averaging where it helps, and report a result as a value with a combined standard uncertainty and a stated coverage factor.",
    ],
    "assessment": (
        "Three quizzes, two circuits drawn and measured in the schematic editor, two "
        "guided derivations, three Python labs checked by execution, and a capstone that "
        "takes one bench measurement from raw readings to a reported temperature with a "
        "full uncertainty budget."
    ),
    "reading": [
        "*The Art of Electronics*, Horowitz & Hill — appendix on oscilloscopes, and section 8.1 on noise.",
        "*Measurement, Instrumentation and Sensors Handbook*, Webster — chapters on bridge circuits and on strain gauges.",
        "*Evaluation of measurement data — Guide to the expression of uncertainty in measurement*, JCGM 100:2008, freely available from the BIPM. Sections 3 and 4 are the whole of module 4 in twelve pages.",
        "Tektronix, *ABCs of Probes*, primer 60W-6053. Trade literature, and the clearest account of compensation in print.",
    ],

    "modules": [
        # ---- M1 -----------------------------------------------------------
        {
            "title": "What the instrument does to the circuit",
            "summary": "A meter is a component you have added. The reading it gives is the reading of the circuit that now exists, not the one you drew.",
            "concepts": [
                "Any pair of terminals in a linear network looks, from outside, like one voltage source $V_{th}$ behind one resistance $R_{th}$. Measuring is what happens when you connect something across those two terminals.",
                "A voltmeter of input resistance $R_{in}$ reads $V_{th}R_{in}/(R_{th}+R_{in})$. The fractional error is $-R_{th}/(R_{th}+R_{in})$, and it is always negative: an attached instrument can only pull a node down.",
                "Loading error is *systematic*. Repeating the reading gives the same wrong answer, and averaging a thousand of them gives the same wrong answer to more decimal places.",
                "To hold the loading error below 1% you need $R_{in} \\ge 99R_{th}$. The familiar 10 MΩ of a digital multimeter is therefore honest up to a source resistance of about 100 kΩ, and no further.",
                "An ammeter goes *into* the loop rather than across it, and its shunt drops a burden voltage $IR_{shunt}$ which subtracts from the circuit's own supply. The current you read is the current that flows with the meter present.",
                "An oscilloscope input is 1 MΩ in parallel with 10–20 pF. A ×10 probe raises that to 10 MΩ and lowers the capacitance to about 10 pF, and charges you a factor of ten in signal for it.",
                "Input resistance is a DC figure. At 1 MHz a 15 pF input is an impedance of 10.6 kΩ, so an instrument that loads a 100 kΩ node by 0.1% at DC loads it by 90% at 1 MHz.",
                "Loading is correctable when $R_{th}$ is known: multiply the reading by $(1 + R_{th}/R_{in})$. It is a design error only when $R_{th}$ is unknown, which is most of the time.",
            ],
            "quiz": {
                "title": "Loading, burden and what averaging cannot fix",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A node whose Thévenin resistance is 100 kΩ is measured with a 10 MΩ digital multimeter. The reading is low by about:",
                        "opts": ["0.01%", "0.1%", "1%", "10%"],
                        "a": 2,
                        "why": r'''
The error is $-R_{th}/(R_{th}+R_{in}) = -100\,\text{k}/10.1\,\text{M} = -0.99\%$, which
rounds to 1%. The useful shortcut is that for $R_{in} \gg R_{th}$ the error is simply
the ratio $R_{th}/R_{in}$, here one part in a hundred. Answering 0.1% is dividing by
the wrong one of the two resistances; the error is set by how large the *source*
resistance is compared with the meter, not the other way round.
''',
                    },
                    {
                        "q": "You take that same reading nine more times and average all ten. What happens to the 1% error?",
                        "opts": [
                            "nothing at all — every reading is wrong by the same amount",
                            "it falls by $\\sqrt{10}$, to about 0.3%",
                            "it falls by 10, to 0.1%",
                            "it becomes unpredictable",
                        ],
                        "a": 0,
                        "why": r'''
Nothing. Averaging attacks the *random* part of an error, and loading is not random:
the same meter on the same node makes the same divider every time. This is the single
most important distinction in the whole course, and the one that survives into every
laboratory you will ever work in — averaging buys you resolution, never accuracy. The
$\sqrt{N}$ answer is the right formula applied to the wrong kind of error, and it is
the reason people quote six digits of a measurement that is wrong in the second.
''',
                    },
                    {
                        "q": "A 5 V supply drives a 47 Ω load. You break the loop and insert an ammeter whose shunt is 1 Ω. What does it read?",
                        "opts": [
                            "106.4 mA, the current that flowed before",
                            "104.2 mA, because the meter's own resistance reduced the current",
                            "106.4 mA, but the true current has risen to 108 mA",
                            "5 mA, because the shunt carries the current instead",
                        ],
                        "a": 1,
                        "why": r'''
The loop is now 48 Ω, so $I = 5/48 = 104.2$ mA, and the meter honestly reports the
104.2 mA that is now flowing. The 2.1% error is the current-measurement twin of
voltage loading, and it is quoted on data sheets as the *burden voltage*: 104 mV
across that shunt, taken out of the 5 V the circuit had to work with. It matters most
where it is least expected — measuring the sleep current of a battery-powered board
through a 100 Ω shunt can stop the board working.
''',
                    },
                    {
                        "q": "You need the loading error on a 47 kΩ source to stay under 0.5%. What is the smallest acceptable instrument input resistance?",
                        "opts": ["470 kΩ", "4.7 MΩ", "23.5 MΩ", "9.4 MΩ"],
                        "a": 3,
                        "why": r'''
The condition is $R_{th}/(R_{th}+R_{in}) \le 0.005$, which rearranges to
$R_{in} \ge 199R_{th} = 9.35$ MΩ. The general rule is $R_{in} \ge (1/e - 1)R_{th}$ for a
fractional error $e$, which for 1% is the familiar factor of 99. Answering 4.7 MΩ is
the factor of 100 applied as though it were the requirement rather than roughly twice
it; a factor of 100 buys you 1%, not 0.5%.
''',
                    },
                    {
                        "q": "An oscilloscope input is 1 MΩ in parallel with 15 pF. What is the magnitude of its input impedance at 1 MHz?",
                        "opts": ["1 MΩ", "106 kΩ", "10.6 kΩ", "1.06 kΩ"],
                        "a": 2,
                        "why": r'''
At 1 MHz the capacitor's reactance is $1/(2\pi fC) = 10.6$ kΩ, which is so far below
1 MΩ that the resistor might as well not be there: the parallel combination is 10.6 kΩ
to three figures. The DC input resistance is a number for the data sheet's front page;
what actually loads a high-frequency node is the capacitance. Answering 1 MΩ is
reading the input as a resistance at all frequencies, which is exactly the assumption
that makes a probe surprise you.
''',
                    },
                    {
                        "q": "Which of these is reduced by averaging many readings?",
                        "opts": [
                            "the loading error of the meter's input resistance",
                            "the offset voltage of the meter's input amplifier",
                            "the calibration error of the meter's voltage reference",
                            "the thermal noise of the source resistance",
                        ],
                        "a": 3,
                        "why": r'''
Thermal noise is genuinely random and uncorrelated between readings, so averaging $N$
of them shrinks it by $\sqrt{N}$. The other three are fixed for the duration of the
measurement: loading is a divider, an offset is a constant added to every reading, and
a reference that is 0.02% high is 0.02% high all afternoon. Sorting your error sources
into these two boxes — random, reducible by repetition; systematic, reducible only by
correction or better equipment — is the whole method of module 4.
''',
                    },
                ],
            },
            "derive": {
                "title": "The loading error, and the rule of 99",
                "minutes": 12,
                "vars": ["V_m", "V_th", "R_th", "R_in", "delta", "e"],
                "brief": r'''
The node you want to measure is a Thévenin source: an ideal $V_{th}$ behind a
resistance $R_{th}$. Your voltmeter is a resistance $R_{in}$ to ground. Connect the
two and you have built a voltage divider, whether you meant to or not.

Derive the reading, the fractional error, and the rule that tells you when a meter is
good enough.
''',
                "steps": [
                    {
                        "prompt": "Write the reading $V_m$ that appears across the meter, in terms of $V_{th}$, $R_{th}$ and $R_{in}$.",
                        "given": "The meter's resistance is the lower arm of the divider.",
                        "answer": "\\frac{V_{th} R_{in}}{R_{th} + R_{in}}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "This is the ordinary divider result. The resistance you are measuring *across* goes on top.",
                        "deconstruct": [
                            "The current round the loop is $V_{th}/(R_{th}+R_{in})$.",
                            "The voltage across $R_{in}$ is that current times $R_{in}$.",
                        ],
                    },
                    {
                        "prompt": "The fractional error is $\\delta = (V_m - V_{th})/V_{th}$. Write $\\delta$ in terms of $R_{th}$ and $R_{in}$ alone.",
                        "given": "Substitute the $V_m$ you just wrote and simplify. $V_{th}$ must cancel.",
                        "answer": "-\\frac{R_{th}}{R_{th} + R_{in}}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "Take the ratio first: $V_m/V_{th} = R_{in}/(R_{th}+R_{in})$. Then subtract one, over the common denominator.",
                        "deconstruct": [
                            "$V_m/V_{th} = R_{in}/(R_{th}+R_{in})$.",
                            "Subtracting 1 gives $(R_{in} - R_{th} - R_{in})/(R_{th}+R_{in})$.",
                            "The numerator collapses to $-R_{th}$.",
                        ],
                    },
                    {
                        "prompt": "You will accept a fractional error of magnitude $e$ at worst. Write the smallest acceptable $R_{in}$ in terms of $R_{th}$ and $e$.",
                        "given": "Set $R_{th}/(R_{th}+R_{in}) = e$ and solve for $R_{in}$.",
                        "answer": "\\frac{R_{th}(1 - e)}{e}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "Cross-multiply to $R_{th} = e R_{th} + e R_{in}$, then collect the $R_{th}$ terms.",
                        "deconstruct": [
                            "$R_{th} = e(R_{th} + R_{in})$.",
                            "So $eR_{in} = R_{th} - eR_{th} = R_{th}(1-e)$.",
                            "Divide by $e$.",
                        ],
                    },
                ],
                "closing": r'''
Put $e = 0.01$ into the last line and it reads $R_{in} \ge 99R_{th}$ — the rule of 99,
which is worth carrying around. For $e = 0.001$ it is 999, and the approximation
$R_{in} \ge R_{th}/e$ is good to within the 1% or 0.1% you were arguing about anyway.

Notice what the second step tells you: $\delta$ contains no $V_{th}$. The loading error
is a fixed fraction of whatever the node was doing, so it cannot be spotted by looking
at the number on the display, and it does not go away when you change the signal. The
only two ways out are a bigger $R_{in}$ or the correction $V_{th} = V_m(1 + R_{th}/R_{in})$,
and the second one requires you to know $R_{th}$.
''',
            },
            "build": {
                "title": "A probe that costs the circuit a tenth of what a bare input would",
                "minutes": 25,
                "brief": r'''
The canvas holds a circuit under test — a 10 V source behind a **100 kΩ** output
resistance — and, well to the right of it, an oscilloscope input drawn as a **1 MΩ**
resistor to ground with the probe on top of it. The two halves are not joined.

Join them, but not with a wire.

A bare 1 MΩ input on a 100 kΩ node is a divider: the node collapses from 10 V to
9.09 V, and the scope faithfully displays the 9.09 V that now exists. Your job is to
add **one series resistor** between the circuit and the scope input so that

- the tip of the probe presents at least 9.5 MΩ to the circuit, so the node under test
  sags by about 1% instead of 9%,
- the attenuation from the tip to the scope input is **10.0:1**, so the reading can be
  multiplied by ten and mean something,
- the scope's own 1 MΩ input is left exactly as it is.

That is a ×10 probe, and there is nothing else inside one except the compensation you
will add in module 2.

## Working it out

Call the series resistor $R_1$ and the scope input $R_2 = 1$ MΩ. The attenuation from
tip to scope is $(R_1+R_2)/R_2$, and the resistance the circuit sees at the tip is
$R_1 + R_2$. Fix the attenuation first; the input resistance then follows without any
further choice, which is exactly why the ×10 convention exists.

## Drawing it

Place a resistor in the gap, wire its left pin to the free end of the 100 kΩ and its
right pin to the top of the 1 MΩ. Click the part to set its value; `9M` is understood.
The checks measure the finished circuit, so any layout that behaves correctly passes.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 100000},
                        {"id": "p3", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 13, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 15, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 5], "b": [15, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 10},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 6, "y": 5, "rot": 0, "value": 100000},
                        {"id": "p3", "kind": "R", "x": 13, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 13, "y": 9},
                        {"id": "p5", "kind": "OUT", "x": 15, "y": 5},
                        {"id": "p6", "kind": "R", "x": 10, "y": 5, "rot": 0, "value": 9000000},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [5, 5]},
                        {"a": [13, 7], "b": [13, 9]},
                        {"a": [13, 5], "b": [15, 5]},
                        {"a": [7, 5], "b": [9, 5]},
                        {"a": [11, 5], "b": [13, 5]},
                    ],
                },
                "checks": [
                    {"name": "the circuit under test is still a 10 V source behind 100 kΩ", "code": r'''
c.assert(c.count('V') === 1,
  'One source, please: the circuit under test. Found ' + c.count('V') + '.');
c.close(c.values('V')[0], 10, 0.001, 'the source of the circuit under test');
const srcs = c.net.parts.filter(function (p) { return p.kind === 'V'; });
const plus = srcs[0].n1;
const series = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 100000) <= 2000 &&
    (p.n1 === plus || p.n2 === plus);
});
c.assert(series.length === 1,
  'The 100 kΩ output resistance of the circuit under test must stay in series with ' +
  'the source — it is the reason this exercise is hard, not an obstacle to remove.');
'''},
                    {"name": "the scope's 1 MΩ input is untouched", "code": r'''
const cur = c.dc().currents;
const ids = Object.keys(cur);
c.assert(ids.length === 1, 'Exactly one source, so that "the current" means one thing.');
const i = Math.abs(cur[ids[0]]);
c.assert(i > 1e-12,
  'No current is flowing at all, so nothing is connected to the scope input yet.');
const rbot = c.vout() / i;
c.close(rbot, 1e6, 0.05,
  'the resistance measured from the probed node to ground — that is the scope input, ' +
  'and it is a given, not a design variable');
'''},
                    {"name": "the attenuation from tip to scope input is 10.0:1", "code": r'''
const srcs = c.net.parts.filter(function (p) { return p.kind === 'V'; });
c.assert(srcs.length === 1, 'Use exactly one source.');
const plus = srcs[0].n1;
const series = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 100000) <= 2000 &&
    (p.n1 === plus || p.n2 === plus);
});
c.assert(series.length === 1, 'The 100 kΩ source resistance must stay in series with the source.');
const tip = series[0].n1 === plus ? series[0].n2 : series[0].n1;
const cur = c.dc().currents;
const i = Math.abs(cur[Object.keys(cur)[0]]);
c.assert(i > 1e-12, 'No current is flowing, so there is no attenuation to measure yet.');
const ratio = c.dc().v[tip] / c.vout();
c.assert(isFinite(ratio), 'The probed node is at 0 V, so the ratio is meaningless.');
c.close(ratio, 10, 0.02,
  'the attenuation from the probe tip to the scope input');
'''},
                    {"name": "the node under test barely notices the probe", "code": r'''
const srcs = c.net.parts.filter(function (p) { return p.kind === 'V'; });
const plus = srcs[0].n1;
const series = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 100000) <= 2000 &&
    (p.n1 === plus || p.n2 === plus);
});
c.assert(series.length === 1, 'The 100 kΩ source resistance must stay in series with the source.');
const tip = series[0].n1 === plus ? series[0].n2 : series[0].n1;
const cur = c.dc().currents;
const i = Math.abs(cur[Object.keys(cur)[0]]);
c.assert(i > 1e-9,
  'Nothing is drawing current from the node under test, so it is not being measured at all.');
const vt = c.dc().v[tip];
c.assert(vt >= 9.85,
  'With the probe attached the node under test sits at ' + c.fmt(vt, 'V') +
  '. It was 10 V unloaded, and the specification allows it to sag by 1.5% at most.');
'''},
                    {"name": "the probe presents 10 MΩ, give or take a tenth", "code": r'''
const srcs = c.net.parts.filter(function (p) { return p.kind === 'V'; });
const plus = srcs[0].n1;
const series = c.net.parts.filter(function (p) {
  return p.kind === 'R' && Math.abs(p.value - 100000) <= 2000 &&
    (p.n1 === plus || p.n2 === plus);
});
c.assert(series.length === 1, 'The 100 kΩ source resistance must stay in series with the source.');
const tip = series[0].n1 === plus ? series[0].n2 : series[0].n1;
const cur = c.dc().currents;
const i = Math.abs(cur[Object.keys(cur)[0]]);
c.assert(i > 1e-12, 'No current flows into the probe, so it has no input resistance to measure.');
const rp = c.dc().v[tip] / i;
c.assert(rp >= 9e6 && rp <= 11e6,
  'The probe presents ' + c.fmt(rp, 'Ω') + ' at its tip. A ×10 probe on a 1 MΩ input ' +
  'is 10 MΩ by construction; anything else means the ratio or the scope input has been changed.');
'''},
                ],
                "hints": [
                    "The attenuation you want is 10, and the lower arm of the divider is the scope's 1 MΩ. Ten parts in total, one of them below the probe point: nine above it.",
                    "So the series resistor is 9 MΩ. Type `9M` into the value box — the editor understands the M, k, m, µ, n and p suffixes.",
                    "Wire the free end of the 100 kΩ to one pin of your resistor and the other pin to the top of the 1 MΩ. The probe already sits on the scope input node; leave it there.",
                    "Check yourself before running: 10 V across 100 kΩ + 9 MΩ + 1 MΩ is 990 nA, which puts 9.901 V at the tip and 0.9901 V at the scope. Multiply the reading by ten and you recover 9.901 V — exactly what the node is doing with the probe on it, and within 1% of the 10 V it had before you touched it.",
                ],
            },
        },

        # ---- M2 -----------------------------------------------------------
        {
            "title": "Probes, compensation and rise time",
            "summary": "The resistors set the ratio at DC; the capacitors set it everywhere else. Getting them to agree is the whole of probe compensation.",
            "concepts": [
                "Every resistor in a probe has capacitance across it, wanted or not: the 9 MΩ has a few picofarads of its own, and the scope's 1 MΩ has 10–20 pF of input and cable.",
                "Each arm of the divider is therefore $R$ in parallel with $C$, of impedance $R/(1+j\\omega RC)$. The ratio is frequency independent only if the two arms have the same time constant.",
                "The compensation condition is $R_1C_1 = R_2C_2$. Satisfy it and the divider gives $R_2/(R_1+R_2)$ at every frequency, which is also $C_1/(C_1+C_2)$ — the resistive and capacitive dividers agree.",
                "Leave it unsatisfied and the probe is a filter. With $C_1 = 0$, a 9 MΩ/1 MΩ probe into 20 pF rolls off at $1/(2\\pi(R_1\\|R_2)C_2) = 8.8$ kHz: useless above the audio band.",
                "On a square wave, under-compensation ($R_1C_1 < R_2C_2$) rounds the top of each edge and the trace droops up to the flat level; over-compensation spikes and settles back down. The trimmer in the probe body adjusts $C_1$ until the corners are square.",
                "A first-order system's 10–90% rise time and its −3 dB bandwidth are locked together: $t_r = \\ln(9)\\tau$ and $f_{3dB} = 1/(2\\pi\\tau)$, so $t_r f_{3dB} = \\ln(9)/2\\pi = 0.35$.",
                "Cascaded stages add rise times in quadrature: $t_{measured}^2 \\approx t_{signal}^2 + t_{scope}^2$. A 1 ns edge on a 350 MHz scope (1 ns of its own) displays as 1.41 ns, and reading 1.41 ns off the screen as though it were the signal is a 41% error.",
                "The probe's ground lead is an inductor — roughly 1 nH per millimetre — and with the tip capacitance it forms a resonant tank. Every fast edge rings it, and the ringing is on the screen, not in the circuit.",
            ],
            "sandbox": {
                "title": "The ring that lives in your ground lead",
                "visualiser": "switching",
                "minutes": 10,
                "initial": {"ls": 80, "coss": 150, "dead": 0},
                "brief": r'''
This visualiser was written for a power switch, and its labels say so: a drain voltage
in green or amber, a device current in blue, and a dead time in nanoseconds. Read it
here as a probe instead. The tank it draws — an
inductance, a capacitance and a fast edge — is exactly the tank your probe makes, with
**loop inductance** standing for the ground lead and **device $C_{oss}$** standing for
the capacitance at the tip.

The trace is flat until 100 ns; that is the edge arriving. What happens after it is
what your screen shows you, and none of it is in the circuit you are measuring.

The two sliders that matter here are the inductance and the capacitance. The dead time
is the one control with no probe counterpart; leave it at 0 until the last notice.
''',
                "notice": [
                    "At the opening values — 80 nH of lead and 150 pF of tip, which is a 1× probe on the ordinary 8 cm flying ground lead — the trace falls at 100 ns and rings. The period is about 22 ns, so the ring is at $1/(2\\pi\\sqrt{LC}) = 46$ MHz, and it takes about 120 ns to fall to a twentieth of the step height. That is a 46 MHz oscillation printed on top of a step that never oscillated.",
                    "Look at the first swing below zero: it runs a little past the bottom gridline of the frame, which is drawn for a switching waveform rather than for this ring. The ring genuinely overshoots by most of the step height — that is the point, not a drawing error.",
                    "Take the capacitance down to 20 pF — the bottom of the slider, and the right order for a ×10 probe tip rather than the 150 pF of a bare 1× one. The ring speeds up to about 126 MHz (a period near 8 ns) and reaches that same twentieth in about 50 ns instead of 120. The *number* of visible cycles barely moves — about five and a half becomes about six and a half — because most of the damping in this model is a fixed fraction of the ring period; what you have bought is a disturbance that is finished sooner.",
                    "Put the capacitance back to 150 pF and cut the inductance from 80 nH to 20 nH — at the 1 nH per millimetre of the concepts above, an 8 cm ground lead replaced by a 2 cm one. The frequency doubles to 92 MHz and the ring is down to that twentieth in about 70 ns. Nothing about the scope changed. This is why the little spring-clip ground tip exists.",
                    "Finally, raise the dead time. With 80 nH and 150 pF the visualiser computes a quarter-period of 5.4 ns, and somewhere between the 5 ns and 10 ns settings the whole picture changes: the trace switches colour, falls once as a smooth quarter-cosine to zero and stays there, and the blue current becomes a 60 ns ramp. That is the visualiser's soft-switching branch, and it is a power-electronics result with no probe counterpart — a probe has nothing that can hold the edge off until the tank has finished swinging. It is worth one look as a picture of what a ring-free edge would be, then put the slider back to 0.",
                ],
            },
            "build": {
                "title": "Compensating the probe you just built",
                "minutes": 25,
                "brief": r'''
Here is the same ×10 probe, now with the parts nobody draws: the scope's input
capacitance, **20 pF**, sits across its 1 MΩ input, and the source is an ideal 1 V
signal generator with no output resistance so that the probe's own behaviour is all
that is on show.

Run the frequency response as it stands and you will find a divider that gives 0.1 at
DC, 0.0662 at 10 kHz and 0.00088 at 1 MHz. The resistors set the ratio at DC; above a
few kilohertz the 20 pF has taken over and there is nothing above the probe point to
balance it.

Add **one capacitor** so that the ratio is 0.1 at every frequency from 100 Hz to
10 MHz.

## What you are solving

Each arm is a resistor in parallel with a capacitor, of impedance $R/(1+j\omega RC)$.
Write the divider ratio with both arms in that form and you will find the $\omega$
cancels out of the whole expression exactly when $R_1C_1 = R_2C_2$. That is the only
condition; everything else about compensation follows from it.

The scope's 20 pF is fixed — it is inside the instrument. So is the 9 MΩ and the
1 MΩ. There is exactly one unknown.

## Drawing it

A capacitor placed above the 9 MΩ with a wire down to each of its pins puts the two in
parallel. `2.22p` is understood by the value box, and so is `2.222e-12`.
''',
                "start": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "rot": 0, "value": 9000000},
                        {"id": "p3", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 12, "y": 9},
                        {"id": "p5", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 2e-11},
                        {"id": "p6", "kind": "GND", "x": 15, "y": 9},
                        {"id": "p7", "kind": "OUT", "x": 17, "y": 5},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [12, 5]},
                        {"a": [12, 5], "b": [15, 5]},
                        {"a": [12, 7], "b": [12, 9]},
                        {"a": [15, 7], "b": [15, 9]},
                        {"a": [15, 5], "b": [17, 5]},
                    ],
                },
                "solution": {
                    "parts": [
                        {"id": "p0", "kind": "V", "x": 3, "y": 6, "rot": 1, "value": 1},
                        {"id": "p1", "kind": "GND", "x": 3, "y": 9},
                        {"id": "p2", "kind": "R", "x": 8, "y": 5, "rot": 0, "value": 9000000},
                        {"id": "p3", "kind": "R", "x": 12, "y": 6, "rot": 1, "value": 1000000},
                        {"id": "p4", "kind": "GND", "x": 12, "y": 9},
                        {"id": "p5", "kind": "C", "x": 15, "y": 6, "rot": 1, "value": 2e-11},
                        {"id": "p6", "kind": "GND", "x": 15, "y": 9},
                        {"id": "p7", "kind": "OUT", "x": 17, "y": 5},
                        {"id": "p8", "kind": "C", "x": 8, "y": 2, "rot": 0, "value": 2.2222222222222223e-12},
                    ],
                    "wires": [
                        {"a": [3, 7], "b": [3, 9]},
                        {"a": [3, 5], "b": [7, 5]},
                        {"a": [9, 5], "b": [12, 5]},
                        {"a": [12, 5], "b": [15, 5]},
                        {"a": [12, 7], "b": [12, 9]},
                        {"a": [15, 7], "b": [15, 9]},
                        {"a": [15, 5], "b": [17, 5]},
                        {"a": [7, 2], "b": [7, 5]},
                        {"a": [9, 2], "b": [9, 5]},
                    ],
                },
                "checks": [
                    {"name": "the scope input is still 1 MΩ in parallel with 20 pF", "code": r'''
const out = c.outNode();
function across(kind, value, tol) {
  return c.net.parts.some(function (p) {
    return p.kind === kind && Math.abs(p.value - value) <= tol &&
      ((p.n1 === out && p.n2 === 0) || (p.n2 === out && p.n1 === 0));
  });
}
c.assert(across('R', 1e6, 1e4),
  'The 1 MΩ scope input must still run from the probed node to ground.');
c.assert(across('C', 20e-12, 1e-12),
  'The 20 pF input capacitance must still run from the probed node to ground. It is ' +
  'inside the instrument; compensating a probe means balancing it, not deleting it.');
'''},
                    {"name": "the ratio is still a tenth at DC", "code": r'''
c.close(c.vout() / c.values('V')[0], 0.1, 0.02,
  'the DC ratio — the resistors alone decide this one, and it was already right');
'''},
                    {"name": "the ratio is a tenth at 1 MHz as well", "code": r'''
c.close(c.gain(1e6), 0.1, 0.03,
  'the ratio at 1 MHz, where the capacitors alone decide it');
'''},
                    {"name": "and everywhere between: flat from 100 Hz to 10 MHz", "code": r'''
const fs = [100, 1e3, 1e4, 1e5, 1e6, 1e7];
const gs = fs.map(function (f) { return c.gain(f); });
const hi = Math.max.apply(null, gs);
const lo = Math.min.apply(null, gs);
c.assert(lo > 0, 'The response has collapsed to zero somewhere in the band.');
c.assert(hi / lo <= 1.03,
  'The ratio varies by ' + ((hi / lo - 1) * 100).toFixed(1) + '% across the band ' +
  '(from ' + lo.toPrecision(3) + ' to ' + hi.toPrecision(3) + '). Compensation means ' +
  'the two arms share one time constant, so nothing is left for frequency to change.');
'''},
                    {"name": "the phase shift is gone too", "code": r'''
const ph = c.phase(1e5);
c.assert(Math.abs(ph) <= 3,
  'At 100 kHz the probe shifts the phase by ' + ph.toFixed(1) + '°. A compensated ' +
  'divider is a pure real ratio: no amplitude change with frequency and no phase shift.');
'''},
                ],
                "hints": [
                    "Write the two arm impedances as $R_1/(1+j\\omega R_1C_1)$ and $R_2/(1+j\\omega R_2C_2)$ and form the divider ratio $Z_2/(Z_1+Z_2)$.",
                    "The ratio loses its frequency dependence exactly when $R_1C_1 = R_2C_2$. Everything else is arithmetic.",
                    "$R_2C_2 = 10^6 \\times 20\\,\\text{pF} = 20$ µs. Your capacitor has to make $9\\,\\text{M}\\Omega \\times C_1$ come to the same 20 µs.",
                    "That is $C_1 = 20\\,\\text{pF}/9 = 2.22$ pF. Notice it is the capacitive divider $C_1/(C_1+C_2) = 2.22/22.2 = 0.1$ — the same tenth the resistors give.",
                ],
            },
            "lab": {
                "title": "Bandwidth, rise time, and what the scope added",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
Five functions, all one-liners once you have the two relations straight, and together
they answer the question every fast measurement asks: is that edge real?

- `rise_time(bandwidth_hz)` — the 10–90% rise time of a first-order system of that
  bandwidth. Use $t_r f_{3dB} = 0.35$.
- `bandwidth(rise_s)` — the same relation the other way round.
- `observed_rise(times)` — several stages in cascade, each with its own rise time,
  combine in quadrature: the result is the square root of the sum of the squares.
- `signal_rise(measured, instrument)` — undo that combination to recover the signal's
  own rise time from what the screen showed. If the measured edge is not slower than
  the instrument's own, the measurement is impossible rather than merely difficult, so
  raise a `ValueError` in that case.
- `bandwidth_needed(edge_s, max_error)` — the instrument bandwidth required so that a
  signal edge of `edge_s` is displayed no more than a fraction `max_error` too slow.
  Set $t_{obs} = t_{sig}\sqrt{1+(t_{inst}/t_{sig})^2} \le t_{sig}(1+e)$, solve for the
  largest acceptable $t_{inst}$, and convert that to a bandwidth.

Import `math` and use `math.sqrt`. Nothing here needs NumPy.
''',
                "files": [{"name": "main.py", "content": r'''
"""Bandwidth and rise time: what the instrument added to the edge."""

import math

BW_RISE_PRODUCT = 0.35  # ln(9) / (2 pi), for a first-order response


def rise_time(bandwidth_hz):
    """10-90% rise time of a first-order system of this bandwidth, in seconds."""
    # TODO: the product of bandwidth and rise time is BW_RISE_PRODUCT.
    return 0.0


def bandwidth(rise_s):
    """The -3 dB bandwidth implied by this 10-90% rise time, in hertz."""
    # TODO: the same relation, rearranged.
    return 0.0


def observed_rise(times):
    """Rise time seen when stages with these rise times are cascaded."""
    # TODO: square each one, add them, take the square root.
    return 0.0


def signal_rise(measured, instrument):
    """The signal's own rise time, given what was measured and what the
    instrument contributes. Raise ValueError if the measurement is impossible."""
    # TODO: invert observed_rise for two stages, after checking it can be inverted.
    return 0.0


def bandwidth_needed(edge_s, max_error):
    """Instrument bandwidth that displays an edge of edge_s no more than a
    fraction max_error too slow."""
    # TODO: the allowed instrument rise time is edge_s * sqrt((1 + e)**2 - 1).
    return 0.0


if __name__ == "__main__":
    print("a 100 MHz scope rises in", rise_time(100e6), "s")
    print("a 1 ns edge needs about", bandwidth(1e-9) / 1e6, "MHz")
    print("1 ns signal on a 1 ns scope shows as", observed_rise([1e-9, 1e-9]), "s")
    print("6.1 ns measured on a 3.5 ns scope was really",
          signal_rise(6.1e-9, 3.5e-9), "s")
    print("a 10 ns edge to within 2% needs", bandwidth_needed(10e-9, 0.02) / 1e6, "MHz")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Bandwidth and rise time: what the instrument added to the edge."""

import math

BW_RISE_PRODUCT = 0.35  # ln(9) / (2 pi), for a first-order response


def rise_time(bandwidth_hz):
    """10-90% rise time of a first-order system of this bandwidth, in seconds."""
    return BW_RISE_PRODUCT / bandwidth_hz


def bandwidth(rise_s):
    """The -3 dB bandwidth implied by this 10-90% rise time, in hertz."""
    return BW_RISE_PRODUCT / rise_s


def observed_rise(times):
    """Rise time seen when stages with these rise times are cascaded."""
    return math.sqrt(sum(t * t for t in times))


def signal_rise(measured, instrument):
    """The signal's own rise time, given what was measured and what the
    instrument contributes. Raise ValueError if the measurement is impossible."""
    if measured <= instrument:
        raise ValueError(
            "a measured edge of %g s is not slower than the instrument's own %g s, "
            "so the signal's rise time cannot be recovered" % (measured, instrument)
        )
    return math.sqrt(measured * measured - instrument * instrument)


def bandwidth_needed(edge_s, max_error):
    """Instrument bandwidth that displays an edge of edge_s no more than a
    fraction max_error too slow."""
    allowed = edge_s * math.sqrt((1.0 + max_error) ** 2 - 1.0)
    return BW_RISE_PRODUCT / allowed


if __name__ == "__main__":
    print("a 100 MHz scope rises in", rise_time(100e6), "s")
    print("a 1 ns edge needs about", bandwidth(1e-9) / 1e6, "MHz")
    print("1 ns signal on a 1 ns scope shows as", observed_rise([1e-9, 1e-9]), "s")
    print("6.1 ns measured on a 3.5 ns scope was really",
          signal_rise(6.1e-9, 3.5e-9), "s")
    print("a 10 ns edge to within 2% needs", bandwidth_needed(10e-9, 0.02) / 1e6, "MHz")
'''}],
                "hints": [
                    "`rise_time` is `BW_RISE_PRODUCT / bandwidth_hz`, and `bandwidth` is the same division with the argument in the denominator instead.",
                    "`observed_rise` is `math.sqrt(sum(t * t for t in times))`. It must work for a list of any length, not just two.",
                    "`signal_rise` needs its guard *before* the subtraction, or you will be taking the square root of a negative number and getting a `ValueError` with an unhelpful message instead of an informative one.",
                    "For `bandwidth_needed`: the observed edge is $t\\sqrt{1+(t_i/t)^2}$, and you want that at or below $t(1+e)$. Squaring both sides gives $1 + (t_i/t)^2 \\le (1+e)^2$, so $t_i \\le t\\sqrt{(1+e)^2-1}$. A 2% error allowance on a 10 ns edge leaves 2.01 ns, which is 174 MHz.",
                ],
                "tests": [
                    {"name": "the 0.35 product both ways", "code": r'''
tr = rise_time(100e6)
assert abs(tr - 3.5e-9) < 1e-15, f"a 100 MHz bandwidth rises in 3.5 ns, got {tr}"
bw = bandwidth(3.5e-9)
assert abs(bw - 100e6) < 1.0, f"3.5 ns implies 100 MHz, got {bw}"
assert abs(bandwidth(rise_time(2.5e8)) - 2.5e8) < 1.0, \
    "the two functions must be exact inverses of each other"
'''},
                    {"name": "a 350 MHz scope has a 1 ns rise time", "code": r'''
tr = rise_time(350e6)
assert abs(tr - 1.0e-9) < 1e-12, f"0.35 / 350 MHz is 1.0 ns, got {tr}"
'''},
                    {"name": "cascaded stages add in quadrature", "code": r'''
two = observed_rise([1e-9, 1e-9])
assert abs(two - 1.4142135623730951e-9) < 1e-18, \
    f"two 1 ns stages show as 1.414 ns, not 2 ns, got {two}"
three = observed_rise([5e-9, 3.5e-9, 1e-9])
assert abs(three - 6.184658438426491e-9) < 1e-18, \
    f"5, 3.5 and 1 ns in quadrature is 6.1847 ns, got {three}"
one = observed_rise([4.2e-9])
assert abs(one - 4.2e-9) < 1e-18, f"a single stage adds nothing, got {one}"
'''},
                    {"name": "the instrument's contribution comes back out", "code": r'''
sig = signal_rise(6.1e-9, 3.5e-9)
assert abs(sig - 4.995998398718719e-9) < 1e-18, \
    f"6.1 ns measured through a 3.5 ns scope was a 5.00 ns edge, got {sig}"
back = observed_rise([sig, 3.5e-9])
assert abs(back - 6.1e-9) < 1e-18, \
    f"putting it back through observed_rise must return 6.1 ns, got {back}"
'''},
                    {"name": "an impossible measurement is refused, not fudged", "code": r'''
raised = False
try:
    signal_rise(2.0e-9, 3.5e-9)
except ValueError:
    raised = True
assert raised, \
    "an edge measured faster than the instrument itself is impossible; raise ValueError"
raised = False
try:
    signal_rise(3.5e-9, 3.5e-9)
except ValueError:
    raised = True
assert raised, "equal rise times imply a signal edge of zero; that is impossible too"
'''},
                    {"name": "choosing a scope for an edge", "code": r'''
bw = bandwidth_needed(10e-9, 0.02)
assert abs(bw - 174131508.28674808) < 1.0, \
    f"a 10 ns edge to within 2% needs 174 MHz, got {bw}"
fast = bandwidth_needed(2e-9, 0.03)
assert abs(fast - 709135786.1639695) < 10.0, \
    f"a 2 ns edge to within 3% needs 709 MHz, got {fast}"
tight = bandwidth_needed(10e-9, 0.005)
assert tight > bw, "a tighter error allowance must demand more bandwidth, not less"
'''},
                ],
            },
        },

        # ---- M3 -----------------------------------------------------------
        {
            "title": "The Wheatstone bridge",
            "summary": "Two dividers, one excitation, and a difference. It is how a resistance change of one part in a thousand becomes a voltage you can amplify.",
            "concepts": [
                "A bridge is two voltage dividers across one excitation, read as the difference between their midpoints: $V_o = V_{ex}\\left(\\frac{R_2}{R_1+R_2} - \\frac{R_4}{R_3+R_4}\\right)$, with $R_2$ and $R_4$ the lower arms.",
                "The bridge balances — $V_o = 0$ — when $R_1/R_2 = R_3/R_4$. Balance is a condition on *ratios*, so it does not depend on the excitation voltage at all.",
                "That is why a null measurement is the most accurate kind: at balance the excitation may drift, and the reading stays zero. Only its *stability during the reading* matters, never its calibration.",
                "In a quarter bridge one arm is a sensor of resistance $R(1+x)$ and the other three are fixed at $R$. Then $V_o = V_{ex}\\,x/(4+2x)$, which is $V_{ex}x/4$ for small $x$ and never exactly that.",
                "Reading a quarter bridge with the linear formula therefore under-reads by a fraction $x/(2+x)$, about $x/2$: at $x = 1\\%$ the strain you infer is 0.5% low. Half and full bridges cancel this term exactly.",
                "A strain gauge converts strain to resistance through its gauge factor: $x = G\\varepsilon$, with $G \\approx 2$ for foil gauges. A 1000 µε strain on a 350 Ω gauge is 0.7 Ω, and at 5 V excitation that is 2.5 mV — which is what the instrumentation amplifier is for.",
                "Each arm dissipates $V_{ex}^2/4R$ when the bridge is balanced with equal arms, so doubling the excitation doubles the signal and quadruples the self-heating. For a platinum resistance thermometer, self-heating is a temperature error that looks exactly like the temperature you are trying to measure.",
                "Lead resistance in series with a remote sensor adds directly to its arm and is indistinguishable from signal. The three-wire connection puts an equal length of lead in the adjacent arm so that the two cancel to first order.",
                "If the excitation also serves as the reference of the analogue-to-digital converter, the conversion is *ratiometric*: excitation drift divides out of the final number and stops being an error source at all.",
            ],
            "quiz": {
                "title": "Balance, sensitivity and the price of excitation",
                "minutes": 10,
                "questions": [
                    {
                        "q": "The left branch of a bridge is 1 kΩ on top and 2 kΩ below. The right branch has 4.7 kΩ on top. What lower arm balances the bridge?",
                        "opts": ["2.35 kΩ", "9.4 kΩ", "4.7 kΩ", "2 kΩ"],
                        "a": 1,
                        "why": r'''
Balance needs $R_1/R_2 = R_3/R_4$, so $R_4 = R_3R_2/R_1 = 4.7\text{k} \times 2 = 9.4$ kΩ.
The two branches must have the same *ratio*, not the same resistances: 1:2 on the left
has to be matched by 4.7:9.4 on the right. Answering 2.35 kΩ inverts the ratio, which
is the commonest slip; check by asking which side of each branch is the larger one —
both lower arms must be the bigger of their pair.
''',
                    },
                    {
                        "q": "You balance a bridge by adjusting one arm until the detector reads zero. Your excitation supply then drifts by 2%. What happens to the balance point?",
                        "opts": [
                            "the reading moves by 2%",
                            "the reading moves by 1%",
                            "nothing — zero times anything is still zero",
                            "the balance point shifts to a different arm value",
                        ],
                        "a": 2,
                        "why": r'''
Nothing. The output is $V_{ex}$ multiplied by a difference of two ratios, and at
balance that difference is exactly zero: scaling zero changes nothing. This is what
makes a null method so much better than a deflection method — the accuracy of the
excitation drops out of the result entirely, and all that is left is how well you can
detect zero. It is the same reason a beam balance beats a spring scale.
''',
                    },
                    {
                        "q": "A Pt1000 sits in one arm of a bridge whose other three arms are 1000 Ω, excited at 2.000 V. The sensor rises to 1003.85 Ω. What is the output?",
                        "opts": ["1.92 mV", "3.85 mV", "7.70 mV", "0.96 mV"],
                        "a": 0,
                        "why": r'''
$V_o = V_{ex}x/(4+2x)$ with $x = 3.85/1000$, which gives 1.9213 mV — near enough
$V_{ex}x/4 = 1.925$ mV. The factor of four is the thing to remember, and it comes from
the divider alone: differentiate the sensor branch's $(1+x)/(2+x)$ at $x = 0$ and you
get exactly $1/4$, so an equal-arm divider moves by a quarter of the fractional change
in one of its arms. The reference branch adds nothing, because none of its arms moved.
Answering 3.85 mV forgets both the excitation and the four.
''',
                    },
                    {
                        "q": "A quarter bridge is read with the linear formula $x = 4V_o/V_{ex}$ when the true $x$ is 0.01. The inferred value is:",
                        "opts": ["exact", "0.5% low", "0.5% high", "2% low"],
                        "a": 1,
                        "why": r'''
The exact output is $V_{ex}x/(4+2x)$, so the linear inversion returns
$x/(1+x/2)$ — low by $x/(2+x) = 0.4975\%$. The rule of thumb is that a quarter bridge
is nonlinear by about half the fractional resistance change. For a strain gauge at
1000 µε that is a 0.1% error and usually ignorable; for a thermistor changing by tens
of per cent it dominates everything else, and you either use the exact inversion or a
bridge configuration that cancels it.
''',
                    },
                    {
                        "q": "You double the excitation of a balanced equal-arm bridge to get more signal. What happens to the power dissipated in the sensor?",
                        "opts": ["unchanged", "doubles", "quadruples", "halves"],
                        "a": 2,
                        "why": r'''
Each arm carries $V_{ex}/2R$ and dissipates $V_{ex}^2/4R$, so doubling the excitation
doubles the signal and multiplies the heating by four. That trade is the whole of
excitation design: signal goes up linearly, self-heating goes up quadratically, and for
a temperature sensor the self-heating is not merely a nuisance but an error in the
measured quantity itself. Answering 'doubles' is reading $P = VI$ while holding the
current fixed, but the current doubles too.
''',
                    },
                    {
                        "q": "A remote 100 Ω platinum sensor is wired to a bridge with two long leads of 1.5 Ω each. What does the three-wire connection achieve?",
                        "opts": [
                            "it removes the lead resistance from the circuit entirely",
                            "it doubles the sensitivity by using both leads as signal",
                            "it lowers the total lead resistance to 0.75 Ω by paralleling the leads",
                            "it puts an equal lead in the adjacent arm, which cancels it",
                        ],
                        "a": 3,
                        "why": r'''
The third wire lets one lead sit in the sensor's arm and an identical lead in the
neighbouring arm, so their equal resistances — and, more importantly, their equal
temperature coefficients — cancel to first order in the ratio that sets balance. The
resistance is still physically there; what has gone is its *effect*. Nothing removes
lead resistance from the circuit, and 3 Ω added to a 100 Ω sensor would otherwise read
as about 7.7 °C of temperature that is not there.
''',
                    },
                ],
            },
            "derive": {
                "title": "The quarter bridge, exactly and then approximately",
                "minutes": 14,
                "vars": ["V_o", "V_ex", "R", "x", "G", "epsilon"],
                "brief": r'''
Four arms across an excitation $V_{ex}$. Three of them are $R$; the lower left one is
a sensor whose resistance has moved to $R(1+x)$, where $x$ is the fractional change —
a few parts per thousand for a strain gauge, a few per cent for a resistance
thermometer over its range.

The output is the left midpoint minus the right midpoint. Derive it exactly, then find
out what the usual linear formula costs you.
''',
                "steps": [
                    {
                        "prompt": "Write the left midpoint as a fraction of $V_{ex}$. The upper arm is $R$, the lower is $R(1+x)$.",
                        "given": "An ordinary divider, with the output taken across the lower arm.",
                        "answer": "\\frac{1+x}{2+x}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "The fraction is lower arm over total. Every $R$ cancels, which is the first sign that a bridge only cares about ratios.",
                        "deconstruct": [
                            "The fraction is $R(1+x) / (R + R(1+x))$.",
                            "Take $R$ out of the top and bottom and it cancels.",
                        ],
                    },
                    {
                        "prompt": "The right-hand branch is two equal arms, so its midpoint sits at exactly half the excitation. Write $V_o/V_{ex}$, the left fraction minus the right.",
                        "given": "Put the difference over a single denominator and simplify.",
                        "answer": "\\frac{x}{4+2x}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "Subtract $1/2$ from the fraction you just found, over the common denominator $2(2+x)$.",
                        "deconstruct": [
                            "$\\frac{1+x}{2+x} - \\frac{1}{2} = \\frac{2(1+x) - (2+x)}{2(2+x)}$.",
                            "The numerator is $2 + 2x - 2 - x = x$.",
                            "So the result is $x/(2(2+x))$, which is $x/(4+2x)$.",
                        ],
                    },
                    {
                        "prompt": "For $x \\ll 1$ the denominator is nearly 4. Write the small-signal approximation for $V_o$ itself, in terms of $V_{ex}$ and $x$.",
                        "answer": "\\frac{V_{ex} x}{4}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "Drop the $2x$ next to the 4 and multiply back through by $V_{ex}$.",
                        "deconstruct": [
                            "$V_o = V_{ex}\\,x/(4+2x)$.",
                            "With $2x$ negligible beside 4, the denominator is just 4.",
                        ],
                    },
                    {
                        "prompt": "Someone reads the bridge and infers $\\hat{x} = 4V_o/V_{ex}$. Write the fractional error $(\\hat{x}-x)/x$ of that inference, in terms of $x$.",
                        "given": "Substitute the exact $V_o$ from step 2 into $\\hat{x} = 4V_o/V_{ex}$ first.",
                        "answer": "-\\frac{x}{2+x}",
                        "placeholder": "e.g. \\frac{a + b}{c d}",
                        "hint": "You will find $\\hat{x} = 4x/(4+2x)$. Divide that by $x$, subtract 1, and tidy up.",
                        "deconstruct": [
                            "$\\hat{x} = 4x/(4+2x) = 2x/(2+x)$.",
                            "$\\hat{x}/x = 2/(2+x)$.",
                            "Subtracting 1 gives $(2 - 2 - x)/(2+x) = -x/(2+x)$.",
                        ],
                    },
                ],
                "closing": r'''
The last line is the bridge's nonlinearity, and it is negative: the linear formula
always under-reads a positive $x$. Its size is about $x/2$, so a 1% resistance change
is inferred 0.5% low, and a 0.1% change 0.05% low — which is why strain gauge work
mostly ignores it and thermistor work never can.

Two things are worth noticing about the algebra. First, $R$ vanished in step 1 and
never came back: the output depends on the *fractional* change, not on whether the
sensor is 120 Ω or 1 kΩ. Second, every term still carries a factor of $V_{ex}$, so
doubling the excitation doubles the output — and that is the temptation the
self-heating limit exists to resist.
''',
            },
            "lab": {
                "title": "A bridge, its sensitivity and its limits",
                "runtime": "python",
                "minutes": 30,
                "brief": r'''
Five functions that between them size a bridge and read it back.

- `bridge_output(vex, r1, r2, r3, r4)` — the general four-arm result, with `r2` and
  `r4` the lower arms and the output taken as left midpoint minus right midpoint.
- `quarter_output(vex, r, dr)` — three arms at `r`, the lower left at `r + dr`. Write
  it as one call to `bridge_output`, not as a second copy of the algebra.
- `nonlinearity(x)` — the fractional error of inferring $x$ from the linear formula,
  which you derived as $-x/(2+x)$.
- `strain_from_output(vout, vex, gf)` — invert the *exact* quarter-bridge relation to
  recover $x$, then divide by the gauge factor to get strain. Inverting
  $V_o = V_{ex}x/(4+2x)$ gives $x = 4V_o/(V_{ex} - 2V_o)$.
- `max_excitation(r, p_max)` — the largest excitation an equal-arm bridge may use if
  no arm is to dissipate more than `p_max`. Each arm carries $V_{ex}/2R$.

Import `math` for the square root. The point of `nonlinearity` being separate is that
you can then ask, of any bridge, whether the linear formula is good enough before
deciding to use it.
''',
                "files": [{"name": "main.py", "content": r'''
"""The Wheatstone bridge: output, inversion, nonlinearity and excitation limits."""

import math


def bridge_output(vex, r1, r2, r3, r4):
    """Left midpoint minus right midpoint, in volts. r2 and r4 are the lower arms."""
    # TODO: two dividers, subtracted.
    return 0.0


def quarter_output(vex, r, dr):
    """Output when the lower left arm is r + dr and the other three are r."""
    # TODO: one call to bridge_output.
    return 0.0


def nonlinearity(x):
    """Fractional error of inferring x with the linear formula 4 Vo / Vex."""
    # TODO: the result you derived in this module.
    return 0.0


def strain_from_output(vout, vex, gf):
    """Strain, from an exact inversion of the quarter-bridge relation."""
    # TODO: recover x first, then divide by the gauge factor.
    return 0.0


def max_excitation(r, p_max):
    """Largest excitation for which no arm of an equal-arm bridge exceeds p_max."""
    # TODO: arm current is vex / 2r, and the arm dissipates i squared times r.
    return 0.0


if __name__ == "__main__":
    print("balanced:", bridge_output(2.0, 1000, 1000, 1000, 1000), "V")
    print("Pt1000 at +3.85 ohm:", quarter_output(2.0, 1000.0, 3.85), "V")
    print("nonlinearity at x = 1%:", nonlinearity(0.01))
    out = quarter_output(5.0, 350.0, 0.7)
    print("350 ohm gauge, 0.7 ohm change:", out, "V")
    print("recovered strain:", strain_from_output(out, 5.0, 2.0))
    print("max excitation for 1 mW in a 1k arm:", max_excitation(1000.0, 1e-3), "V")
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""The Wheatstone bridge: output, inversion, nonlinearity and excitation limits."""

import math


def bridge_output(vex, r1, r2, r3, r4):
    """Left midpoint minus right midpoint, in volts. r2 and r4 are the lower arms."""
    return vex * (r2 / (r1 + r2) - r4 / (r3 + r4))


def quarter_output(vex, r, dr):
    """Output when the lower left arm is r + dr and the other three are r."""
    return bridge_output(vex, r, r + dr, r, r)


def nonlinearity(x):
    """Fractional error of inferring x with the linear formula 4 Vo / Vex."""
    return -x / (2.0 + x)


def strain_from_output(vout, vex, gf):
    """Strain, from an exact inversion of the quarter-bridge relation."""
    x = 4.0 * vout / (vex - 2.0 * vout)
    return x / gf


def max_excitation(r, p_max):
    """Largest excitation for which no arm of an equal-arm bridge exceeds p_max."""
    return 2.0 * math.sqrt(p_max * r)


if __name__ == "__main__":
    print("balanced:", bridge_output(2.0, 1000, 1000, 1000, 1000), "V")
    print("Pt1000 at +3.85 ohm:", quarter_output(2.0, 1000.0, 3.85), "V")
    print("nonlinearity at x = 1%:", nonlinearity(0.01))
    out = quarter_output(5.0, 350.0, 0.7)
    print("350 ohm gauge, 0.7 ohm change:", out, "V")
    print("recovered strain:", strain_from_output(out, 5.0, 2.0))
    print("max excitation for 1 mW in a 1k arm:", max_excitation(1000.0, 1e-3), "V")
'''}],
                "hints": [
                    "`bridge_output` is `vex * (r2 / (r1 + r2) - r4 / (r3 + r4))`. Keep the two dividers side by side and the sign convention looks after itself.",
                    "`quarter_output` should call `bridge_output(vex, r, r + dr, r, r)`. If you find yourself typing a division, you are writing the algebra out a second time.",
                    "`strain_from_output` needs the exact inversion $x = 4V_o/(V_{ex} - 2V_o)$, not $4V_o/V_{ex}$ — the tests check that a value put in through `quarter_output` comes back out to twelve figures.",
                    "For `max_excitation`: the arm current is $V_{ex}/2R$, so the arm power is $V_{ex}^2/4R$. Setting that equal to `p_max` gives $V_{ex} = 2\\sqrt{P_{max}R}$, which is 2.0 V for 1 mW in a 1 kΩ arm.",
                ],
                "tests": [
                    {"name": "a balanced bridge reads zero and an unbalanced one does not", "code": r'''
z = bridge_output(2.0, 1000, 1000, 1000, 1000)
assert abs(z) < 1e-15, f"equal arms must give exactly zero, got {z}"
r = bridge_output(2.0, 1000, 2000, 4700, 9400)
assert abs(r) < 1e-15, f"1:2 against 4.7k:9.4k is also balanced, got {r}"
u = bridge_output(2.0, 1000, 1003.85, 1000, 1000)
assert abs(u - 0.0019213014946228846) < 1e-15, \
    f"one arm 3.85 ohms high should give 1.9213 mV, got {u}"
'''},
                    {"name": "the quarter bridge agrees with the general form", "code": r'''
q = quarter_output(2.0, 1000.0, 3.85)
assert abs(q - 0.0019213014946228846) < 1e-15, \
    f"a Pt1000 3.85 ohms up at 2 V excitation gives 1.9213 mV, got {q}"
g = quarter_output(5.0, 350.0, 0.7)
assert abs(g - 0.0024975024975021354) < 1e-15, \
    f"a 350 ohm gauge 0.7 ohms up at 5 V gives 2.4975 mV, got {g}"
assert abs(quarter_output(2.0, 1000.0, 0.0)) < 1e-15, "no change means no output"
neg = quarter_output(2.0, 1000.0, -3.85)
assert neg < 0, f"a falling sensor resistance must give a negative output, got {neg}"
'''},
                    {"name": "the bridge is not quite linear", "code": r'''
n = nonlinearity(0.01)
assert abs(n - (-0.0049751243781094535)) < 1e-15, \
    f"at x = 1% the linear formula is 0.4975% low, got {n}"
assert nonlinearity(0.002) < 0, "the error is always negative for a positive x"
assert abs(nonlinearity(0.002) - (-0.0009990009990009992)) < 1e-15, \
    "at x = 0.2% the error should be about -0.0999%"
small, large = abs(nonlinearity(0.001)), abs(nonlinearity(0.1))
assert large > 10 * small, \
    "the error grows with x, so a thermistor cannot be read the way a strain gauge is"
'''},
                    {"name": "an exact inversion round-trips", "code": r'''
out = quarter_output(5.0, 350.0, 0.7)
eps = strain_from_output(out, 5.0, 2.0)
assert abs(eps - 1e-3) < 1e-12, \
    f"0.7 ohms on a 350 ohm gauge of factor 2 is 1000 microstrain, got {eps}"
big = quarter_output(2.0, 1000.0, 100.0)
x = strain_from_output(big, 2.0, 1.0)
assert abs(x - 0.1) < 1e-12, \
    f"the inversion must stay exact for a 10% change, got {x} instead of 0.1"
'''},
                    {"name": "excitation is limited by what the arm can dissipate", "code": r'''
v = max_excitation(1000.0, 1e-3)
assert abs(v - 2.0) < 1e-12, f"1 mW in a 1 k arm allows 2.000 V, got {v}"
v2 = max_excitation(350.0, 5e-3)
assert abs(v2 - 2.6457513110645907) < 1e-12, \
    f"5 mW in a 350 ohm arm allows 2.6458 V, got {v2}"
arm_power = (v / (2 * 1000.0)) ** 2 * 1000.0
assert abs(arm_power - 1e-3) < 1e-15, \
    f"check yourself: the arm at that excitation dissipates {arm_power} W"
'''},
                ],
            },
        },

        # ---- M4 -----------------------------------------------------------
        {
            "title": "Noise, averaging and the number you report",
            "summary": "Below some level every instrument is reporting its own noise. Knowing where that level is, and saying so, is the last skill in the course.",
            "concepts": [
                "Any resistance generates thermal noise of spectral density $\\sqrt{4kTR}$ volts per root hertz: 4.07 nV/√Hz for 1 kΩ at 300 K, and 128.7 nV/√Hz for 1 MΩ. It is set by physics, not by workmanship.",
                "Density is per root hertz because noise powers add: over a bandwidth $B$ the total is density $\\times\\sqrt{B}$. Halving the bandwidth improves the r.m.s. noise by $\\sqrt{2}$, and costs you speed.",
                "Below the flicker corner the density rises as $1/\\sqrt{f}$ — the *power* goes as $1/f$ — so integrating for longer stops helping. Chopper stabilisation and correlated double sampling exist to move signals above that corner.",
                "Averaging $N$ independent readings reduces the random part by $\\sqrt{N}$ and the systematic part by nothing. Ten times better costs a hundred times longer, which is why averaging is a last resort rather than a first one.",
                "A Type A uncertainty is evaluated statistically from repeated readings: the standard uncertainty of the mean is $s/\\sqrt{n}$, with $s$ the sample standard deviation.",
                "A Type B uncertainty comes from anywhere else — a data sheet, a calibration certificate, a tolerance band. A stated limit $\\pm a$ with no other information is treated as a rectangular distribution of standard uncertainty $a/\\sqrt{3}$.",
                "Independent contributions combine in quadrature into the combined standard uncertainty $u_c$, and each is weighted by its sensitivity coefficient $\\partial y/\\partial x_i$ — how much the result moves when that input moves.",
                "Reporting: multiply by a coverage factor, conventionally $k = 2$ for about 95% confidence, and quote the expanded uncertainty to two significant figures with the value rounded to the same decimal place. State $k$; a bare $\\pm$ means nothing.",
                "Resolution is not accuracy. A 6½-digit display of a quantity known to 0.1% is showing four digits of measurement and two of decoration.",
            ],
            "sandbox": {
                "title": "Where the floor stops falling",
                "visualiser": "noise-corner",
                "minutes": 9,
                "initial": {"fc": 1001, "nth": 10},
                "brief": r'''
This is the noise density of an amplifier input, in decibels relative to 1 nV/√Hz,
against frequency from 1 Hz to 10 MHz on a logarithmic axis. The curve is
$e_n = e_{th}\sqrt{1 + f_c/f}$: a flat thermal floor with a $1/f$ tail rising out of it
at low frequency.

Two markers are drawn for you. The faint dashed horizontal line is the thermal floor
itself, and the purple dashed vertical line is the corner frequency $f_c$ where the
two mechanisms contribute equally.

The vertical axis rescales itself as you move the sliders, so read the *numbers* on it
rather than the height of the trace.
''',
                "notice": [
                    "At the opening values — a floor of 10 nV/√Hz and a corner just above 1 kHz — the dashed floor sits at 20 dB, because 20 dB re 1 nV/√Hz is 10 nV/√Hz. Where the purple line crosses the trace, the trace is 23 dB: exactly 3 dB above the floor, since at $f = f_c$ the formula gives $e_{th}\\sqrt{2}$.",
                    "Below the corner the trace falls at **10 dB per decade**, not 20: read 50 dB at 1 Hz, 40 dB at 10 Hz, 30.4 dB at 100 Hz. The noise *power* goes as $1/f$, so the density, which is a voltage, goes as $1/\\sqrt{f}$.",
                    "Push the thermal floor slider up to 40 nV/√Hz and the drawn curve does not change shape at all — only the axis labels move, by $20\\log_{10}4 = 12$ dB. The floor and the corner are independent: one is set by resistance and temperature, the other by the device's flicker mechanism.",
                    "Drag the corner slider all the way left, to 1 Hz. The purple line lands on the left-hand axis and the trace is within half a decibel of flat from 10 Hz upwards; that is what a chopper-stabilised amplifier looks like, and it is why one is worth having for a bridge measurement that takes seconds.",
                    "Now drag the corner all the way right, to 100 kHz. The $1/f$ region now covers five of the seven decades on the axis, and only the top two are flat. Averaging a slow measurement helps in the flat region and stops helping in the sloped one, so this is the picture that decides whether averaging is worth the time.",
                ],
            },
            "quiz": {
                "title": "Floors, averages and honest numbers",
                "minutes": 10,
                "questions": [
                    {
                        "q": "An amplifier with a 10 nV/√Hz input noise density is used over a 1 MHz bandwidth. What is the r.m.s. noise at its input?",
                        "opts": ["10 µV", "10 mV", "1 µV", "3.2 nV"],
                        "a": 0,
                        "why": r'''
$10\,\text{nV}/\sqrt{\text{Hz}} \times \sqrt{10^6\,\text{Hz}} = 10\,\text{nV} \times 1000
= 10$ µV. The root hertz in the unit is the whole instruction: multiply by the square
root of the bandwidth, never by the bandwidth. Answering 10 mV is multiplying by
$10^6$ instead of $10^3$, and it is worth doing the unit arithmetic explicitly once —
$\text{V}/\sqrt{\text{Hz}} \times \sqrt{\text{Hz}} = \text{V}$ — to see why.
''',
                    },
                    {
                        "q": "Your reading has a random uncertainty of 1 mV and you need 0.1 mV. How many readings must you average, assuming they are independent?",
                        "opts": ["10", "32", "100", "1000"],
                        "a": 2,
                        "why": r'''
Averaging improves the random part by $\sqrt{N}$, so a factor of ten needs $N = 100$.
The cost is brutal and worth internalising: the next factor of ten costs 10 000
readings. Answering 10 is applying the improvement linearly, which is the mistake that
makes people think a slow measurement can be made arbitrarily good by waiting. If the
noise is flicker rather than white, even the $\sqrt{N}$ is optimistic.
''',
                    },
                    {
                        "q": "A data sheet says the reference is accurate to ±2 mV, with no other information. What standard uncertainty do you enter in the budget?",
                        "opts": ["2 mV", "1 mV", "1.15 mV", "0.67 mV"],
                        "a": 2,
                        "why": r'''
A stated limit with no distribution named is treated as rectangular: every value in the
band is equally likely, and the standard deviation of a rectangular distribution of
half-width $a$ is $a/\sqrt{3} = 2/1.732 = 1.15$ mV. Entering the 2 mV itself
double-counts, because a limit is not a standard deviation; entering 1 mV is the
half-width halved, which corresponds to no distribution at all. This is the single
most-used conversion in an uncertainty budget.
''',
                    },
                    {
                        "q": "Two independent contributions to a result are 0.3 °C and 0.4 °C. What is the combined standard uncertainty?",
                        "opts": ["0.7 °C", "0.5 °C", "0.35 °C", "0.1 °C"],
                        "a": 1,
                        "why": r'''
Independent uncertainties add in quadrature: $\sqrt{0.3^2 + 0.4^2} = 0.5$ °C. Adding
them arithmetically to 0.7 °C assumes the two always err in the same direction, which
is a worst case rather than an uncertainty. Notice how little the smaller one matters:
had it been 0.1 °C the total would have been 0.41 °C. Chasing the second-largest term
in a budget is nearly always wasted effort.
''',
                    },
                    {
                        "q": "A result is 24.318 °C with a combined standard uncertainty of 0.176 °C. How should it be reported at $k = 2$?",
                        "opts": [
                            "24.318 °C ± 0.176 °C",
                            "24.3 °C ± 0.2 °C",
                            "24.32 °C ± 0.35 °C (k = 2)",
                            "24.318 °C ± 0.352 °C (k = 2)",
                        ],
                        "a": 2,
                        "why": r'''
Expand first: $U = 2 \times 0.176 = 0.352$ °C, quoted to two significant figures as
0.35 °C, with the value rounded to the same decimal place — 24.32 °C — and $k$ stated.
Quoting 24.318 ± 0.352 keeps three digits the uncertainty says are meaningless; quoting
24.318 ± 0.176 reports a *standard* uncertainty as though it were an interval and omits
$k$ entirely, so the reader cannot tell whether it covers 68% or 95%; and 24.3 ± 0.2 has
thrown away a figure the measurement had earned.
''',
                    },
                    {
                        "q": "You replace a 6½-digit meter with an 8½-digit one to measure a bridge output whose dominant error is the 0.1% tolerance of the completion resistors. What improves?",
                        "opts": [
                            "the accuracy, by two orders of magnitude",
                            "only the speed of the measurement",
                            "the random part, by a factor of 100, and the total by the same",
                            "nothing that matters — the resistors still dominate the budget",
                        ],
                        "a": 3,
                        "why": r'''
Nothing that matters. A budget is a sum in quadrature, and a term that is already
negligible cannot become more negligible: if the resistors contribute 0.1% and the
meter 0.0001%, removing the meter term entirely changes the total in the fifth decimal
place. The money belongs on the resistors — or on a configuration that cancels them.
Reading a budget before buying equipment is the practical use of module 4, and the
capstone is built around exactly this comparison.
''',
                    },
                ],
            },
            "lab": {
                "title": "Noise floors, averaging and an uncertainty budget",
                "runtime": "python",
                "minutes": 32,
                "brief": r'''
Seven small functions covering the arithmetic of module 4.

- `johnson_density(r, t)` — thermal noise density $\sqrt{4kTR}$ in volts per root
  hertz. `BOLTZMANN` is defined for you.
- `rms_noise(density, bw)` — total r.m.s. noise of a white density over a bandwidth.
- `averages_needed(single, target)` — how many independent readings must be averaged
  to bring a random uncertainty of `single` down to `target`. Return a whole number,
  rounded **up**: 99.2 readings is not a thing.
- `type_a(values)` — the standard uncertainty of the mean of repeated readings, which
  is the sample standard deviation (the $n-1$ one) divided by $\sqrt{n}$.
- `type_b_rect(halfwidth)` — the standard uncertainty of a stated limit, $a/\sqrt{3}$.
- `combined(us)` — independent contributions in quadrature.
- `round_report(value, u)` — return `(value, u)` rounded for publication: `u` to two
  significant figures, and `value` to that same decimal place. Find the decimal place
  with `math.floor(math.log10(abs(u)))`; if that exponent is $e$, you are keeping
  $1-e$ decimals.

Use `math.ceil` for the rounding up, and Python's built-in `round` for the last one.
''',
                "files": [{"name": "main.py", "content": r'''
"""Noise floors, averaging, and the arithmetic of an uncertainty budget."""

import math

BOLTZMANN = 1.380649e-23  # J/K, exact by definition since 2019


def johnson_density(r, t):
    """Thermal noise density of a resistance r at temperature t, in V/sqrt(Hz)."""
    # TODO: the square root of 4 k T R.
    return 0.0


def rms_noise(density, bw):
    """Total r.m.s. noise of a white density over a bandwidth, in volts."""
    # TODO: density times the square root of the bandwidth.
    return 0.0


def averages_needed(single, target):
    """Readings to average to bring a random uncertainty down to target."""
    # TODO: averaging improves as the square root of the count. Round up.
    return 0


def type_a(values):
    """Standard uncertainty of the mean of these repeated readings."""
    # TODO: sample standard deviation over the square root of the count.
    return 0.0


def type_b_rect(halfwidth):
    """Standard uncertainty of a stated limit of plus or minus halfwidth."""
    # TODO: a rectangular distribution has standard deviation a / sqrt(3).
    return 0.0


def combined(us):
    """Combined standard uncertainty of independent contributions."""
    # TODO: in quadrature.
    return 0.0


def round_report(value, u):
    """(value, u) rounded for publication: u to two significant figures."""
    # TODO: find the decimal place from the exponent of u, then round both.
    return (0.0, 0.0)


if __name__ == "__main__":
    print("1 k at 300 K:", johnson_density(1000.0, 300.0), "V/sqrt(Hz)")
    print("over 1 MHz that is:", rms_noise(johnson_density(1000.0, 300.0), 1e6), "V")
    print("1 mV down to 0.1 mV needs", averages_needed(1e-3, 1e-4), "readings")
    xs = [9.9012, 9.9008, 9.9015, 9.9006, 9.9011, 9.9009]
    ua = type_a(xs)
    ub = type_b_rect(0.0030)
    uc = combined([ua, ub])
    print("type A:", ua, " type B:", ub, " combined:", uc)
    print("reported:", round_report(sum(xs) / len(xs), 2 * uc))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
"""Noise floors, averaging, and the arithmetic of an uncertainty budget."""

import math

BOLTZMANN = 1.380649e-23  # J/K, exact by definition since 2019


def johnson_density(r, t):
    """Thermal noise density of a resistance r at temperature t, in V/sqrt(Hz)."""
    return math.sqrt(4.0 * BOLTZMANN * t * r)


def rms_noise(density, bw):
    """Total r.m.s. noise of a white density over a bandwidth, in volts."""
    return density * math.sqrt(bw)


def averages_needed(single, target):
    """Readings to average to bring a random uncertainty down to target."""
    return math.ceil((single / target) ** 2)


def type_a(values):
    """Standard uncertainty of the mean of these repeated readings."""
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(var) / math.sqrt(n)


def type_b_rect(halfwidth):
    """Standard uncertainty of a stated limit of plus or minus halfwidth."""
    return halfwidth / math.sqrt(3.0)


def combined(us):
    """Combined standard uncertainty of independent contributions."""
    return math.sqrt(sum(u * u for u in us))


def round_report(value, u):
    """(value, u) rounded for publication: u to two significant figures."""
    places = 1 - math.floor(math.log10(abs(u)))
    return (round(value, places), round(u, places))


if __name__ == "__main__":
    print("1 k at 300 K:", johnson_density(1000.0, 300.0), "V/sqrt(Hz)")
    print("over 1 MHz that is:", rms_noise(johnson_density(1000.0, 300.0), 1e6), "V")
    print("1 mV down to 0.1 mV needs", averages_needed(1e-3, 1e-4), "readings")
    xs = [9.9012, 9.9008, 9.9015, 9.9006, 9.9011, 9.9009]
    ua = type_a(xs)
    ub = type_b_rect(0.0030)
    uc = combined([ua, ub])
    print("type A:", ua, " type B:", ub, " combined:", uc)
    print("reported:", round_report(sum(xs) / len(xs), 2 * uc))
'''}],
                "hints": [
                    "`johnson_density` is `math.sqrt(4.0 * BOLTZMANN * t * r)`. A 1 kΩ resistor at 300 K comes to 4.07 nV/√Hz; if you get a number near $10^{-17}$ you have forgotten the square root.",
                    "`averages_needed` is `math.ceil((single / target) ** 2)` — square the ratio, because the improvement goes as the square root of the count.",
                    "`type_a` needs the $n-1$ divisor for the variance and then a further division by $\\sqrt{n}$ for the standard error of the mean. Two square roots, or one on the whole quotient.",
                    "For `round_report`, `math.floor(math.log10(0.0035))` is −3, so you keep $1-(-3) = 4$ decimals: `round(u, 4)` gives 0.0035 and the value is rounded to four decimals as well.",
                ],
                "tests": [
                    {"name": "thermal noise of a resistor", "code": r'''
d = johnson_density(1000.0, 300.0)
assert abs(d - 4.070354775692163e-09) < 1e-20, \
    f"1 k at 300 K is 4.0704 nV/rtHz, got {d}"
big = johnson_density(1e6, 300.0)
assert abs(big - 1.2871591976131003e-07) < 1e-18, \
    f"1 M at 300 K is 128.7 nV/rtHz, got {big}"
assert abs(big / d - math.sqrt(1000.0)) < 1e-9, \
    "a thousand times the resistance is only sqrt(1000) times the noise"
'''},
                    {"name": "density becomes volts through a bandwidth", "code": r'''
v = rms_noise(10e-9, 1e6)
assert abs(v - 1e-5) < 1e-18, f"10 nV/rtHz over 1 MHz is 10 uV, got {v}"
wide = rms_noise(10e-9, 20e6)
assert abs(wide - 4.4721359549995795e-05) < 1e-16, \
    f"the same density over 20 MHz is 44.7 uV, got {wide}"
assert abs(wide / v - math.sqrt(20.0)) < 1e-9, \
    "twenty times the bandwidth is sqrt(20) times the noise, not twenty times"
'''},
                    {"name": "averaging is expensive", "code": r'''
n = averages_needed(1e-3, 1e-4)
assert n == 100, f"a factor of ten costs a hundred readings, got {n}"
assert averages_needed(2.5e-3, 5e-4) == 25, "a factor of five costs twenty-five"
assert averages_needed(1e-3, 9.9e-5) == 103, \
    "a non-integer answer must round up, not down or to nearest"
assert isinstance(averages_needed(1e-3, 1e-4), int), "return a whole number of readings"
'''},
                    {"name": "Type A from repeats, Type B from a limit", "code": r'''
xs = [9.9012, 9.9008, 9.9015, 9.9006, 9.9011, 9.9009]
ua = type_a(xs)
assert abs(ua - 0.00013017082793169405) < 1e-15, \
    f"the standard uncertainty of that mean is 0.13 mV, got {ua}"
ub = type_b_rect(0.0030)
assert abs(ub - 0.0017320508075688774) < 1e-15, \
    f"a +/- 3 mV limit is a 1.73 mV standard uncertainty, got {ub}"
assert ub > ua, "the data sheet limit dominates these repeats, which is the usual case"
'''},
                    {"name": "contributions combine in quadrature", "code": r'''
c = combined([0.3, 0.4])
assert abs(c - 0.5) < 1e-12, f"0.3 and 0.4 combine to 0.5, not 0.7, got {c}"
one = combined([0.42])
assert abs(one - 0.42) < 1e-15, "a single contribution combines to itself"
lopsided = combined([0.4, 0.04])
assert abs(lopsided - 0.4019950248448356) < 1e-12, \
    "a contribution ten times smaller adds half a per cent, which is why budgets are read top-down"
'''},
                    {"name": "the reported number keeps only the digits it has", "code": r'''
v, u = round_report(9.901016666666667, 0.0034738707197847322)
assert abs(u - 0.0035) < 1e-12, f"the uncertainty rounds to two figures, 0.0035, got {u}"
assert abs(v - 9.901) < 1e-12, f"the value follows to the same decimal place, got {v}"
v2, u2 = round_report(1234.5678, 2.13)
assert abs(u2 - 2.1) < 1e-12 and abs(v2 - 1234.6) < 1e-12, \
    f"1234.5678 +/- 2.13 reports as 1234.6 +/- 2.1, got {(v2, u2)}"
v3, u3 = round_report(0.0512345, 0.00123)
assert abs(u3 - 0.0012) < 1e-15 and abs(v3 - 0.0512) < 1e-15, \
    f"0.0512345 +/- 0.00123 reports as 0.0512 +/- 0.0012, got {(v3, u3)}"
'''},
                ],
            },
        },
    ],

    "capstone": {
        "title": "One temperature, reported honestly",
        "runtime": "python",
        "minutes": 240,
        "brief": r'''
A platinum resistance thermometer sits in one arm of a bridge on the bench next door.
The run has already been done, and `bench.py` holds everything that was written down:

- twelve readings of the bridge output, taken with a digital multimeter,
- the excitation, 2.000 V, from a supply specified to ±2 mV,
- the three completion resistors, nominally 1000 Ω, from a 0.1% batch,
- the sensor's nominal resistance at 0 °C, 1000 Ω, from a class A Pt1000 specified
  to ±0.6 Ω at that point,
- the bridge's Thévenin output resistance, 1000 Ω, and the multimeter's input
  resistance, 10 MΩ.

Your job is to turn that into one line of a report: a temperature, an expanded
uncertainty, and a coverage factor. Along the way you have to decide which of the four
input quantities actually matters, which is the question the whole course has been
building towards.

## The measurement chain

Four steps, each a function you write.

1. **Undo the loading.** The multimeter's 10 MΩ sits across a bridge whose Thévenin
   resistance is 1 kΩ, so every reading is low by $R_{th}/(R_{th}+R_{in})$. The
   correction is $V = V_{meas}(1 + R_{th}/R_{in})$.
2. **Invert the bridge.** From $V_o = V_{ex}x/(4+2x)$, recover
   $x = 4V_o/(V_{ex}-2V_o)$ and hence the sensor's resistance $R_s = R_c(1+x)$, where
   $R_c$ is the completion resistance the sensor is compared against.
3. **Convert to temperature.** Take the sensor as linear over this range:
   $R_s = R_0(1 + \alpha T)$ with $\alpha = 3.85\times10^{-3}$ per kelvin, so
   $T = (R_s/R_0 - 1)/\alpha$.
4. **Propagate the uncertainties.** Each input $x_i$ has a standard uncertainty
   $u(x_i)$, and it contributes $|\partial T/\partial x_i|\,u(x_i)$ to the result.

## Sensitivity coefficients without calculus

You are not asked to differentiate the chain by hand. Evaluate each coefficient
numerically, by nudging one input and seeing how far the answer moves:

```text
c_i = (T(x_i + h) - T(x_i - h)) / (2h),  with h a millionth of x_i
```

That central difference is accurate to well under a part in a million on a function
this smooth, and it keeps working when you change the model — which is the real reason
professional budgets are computed this way rather than symbolically.

## What the answer is for

When your budget prints, one term will be a hundred times larger than another. Write
one sentence in the module docstring of `main.py` naming the dominant term and saying
what you would change to improve the result — and, just as usefully, what you would
*not* bother changing. The last deliverable is that sentence; it is the difference
between operating an instrument and understanding one.
''',
        "deliverables": [
            "`corrected_output`, undoing the multimeter's loading of the bridge output, in the correct direction: the corrected value must be larger than the reading.",
            "`sensor_resistance`, inverting the exact quarter-bridge relation — not the linear approximation — to recover the sensor's resistance from the corrected output.",
            "`temperature`, converting a sensor resistance to a temperature through the linear platinum model.",
            "`budget`, returning one contribution in kelvin for each named input, each evaluated as a numerical sensitivity coefficient times that input's standard uncertainty.",
            "`combine` and `report`, giving the combined standard uncertainty and the final published string, with the uncertainty at two significant figures, the value at the same decimal place, and the coverage factor stated.",
            "One sentence in the module docstring of `main.py` naming the dominant contribution and saying what would and would not be worth improving.",
        ],
        "constraints": [
            "The standard library only. `math` is all this needs; NumPy is permitted by the course but buys nothing here.",
            "Do not edit `bench.py`. It is the record of what was measured, and editing your data to fit your analysis is the one unforgivable sin in this subject.",
            "`budget` must work for any subset of the four inputs, and must key its result by the same names it was given, so that a budget can be re-run with one term switched off.",
            "Sensitivity coefficients are to be evaluated numerically from your own chain, not hard-coded. A budget that stops agreeing with the model when the model changes is worse than no budget.",
            "`report` states the coverage factor. A value with a ± and no $k$ is not a result.",
        ],
        "rubric": [
            {"criterion": "Measurement chain", "weight": 30,
             "evidence": "corrected_output, sensor_resistance and temperature compose into a temperature that reproduces the reference value from the bench data to nine figures, with the loading correction applied in the direction that makes the reading larger rather than smaller."},
            {"criterion": "Uncertainty budget", "weight": 30,
             "evidence": "budget returns one contribution per named input, each equal to a numerically evaluated sensitivity coefficient times that input's standard uncertainty, and agrees with independently computed values on the bench case and on a second case with different numbers."},
            {"criterion": "Combination and reporting", "weight": 20,
             "evidence": "combine gives the quadrature sum, and report rounds the expanded uncertainty to two significant figures with the value at the same decimal place and the coverage factor stated, including the awkward case where the uncertainty is larger than one."},
            {"criterion": "Interpretation", "weight": 20,
             "evidence": "The docstring sentence names the completion and sensor resistors as the dominant terms, and identifies the multimeter and the averaging as the places where further effort would be wasted."},
        ],
        "hints": [
            "Write `temperature_from(v_out, vex, rc, r0)` as a single function composing steps 2 and 3. `budget` then needs to perturb only that one function, which is what makes the numerical derivative easy.",
            "For the perturbation size, `h = abs(x) * 1e-6` works for every input here. Guard against a zero input with a small floor, or a budget entry for a quantity that happens to be zero will divide by nothing.",
            "Build the perturbed argument lists with `dict(args)` copies and keyword expansion — `temperature_from(**hi)` — rather than four `if` branches. The result is shorter and does not have to be rewritten when the model gains a fifth input.",
            "The completion resistance enters twice over: it scales the sensor resistance directly, and it is the thing the sensor is being compared against. Its sensitivity coefficient comes out near 0.26 K per ohm, so 0.577 Ω of standard uncertainty is 0.15 K.",
            "For `report`, the number of decimals is `max(0, 1 - math.floor(math.log10(abs(u))))`, and `\"%.*f\" % (places, value)` takes the count as an argument. The clamp at zero matters: an uncertainty of 21 would otherwise ask for minus one decimal place and raise.",
        ],
        "files": [
            {"name": "bench.py", "ro": True, "content": r'''
"""The record of one bench run. Do not edit.

Twelve readings of a Pt1000 quarter bridge, taken with a 6.5-digit multimeter on its
100 mV range, plus every specification that was copied off the instruments and the
component reels at the time. Nothing here is a measurement you can repeat; it is what
the notebook says, which is all any analysis ever has.
"""

# bridge output readings, volts
RAW = [
    0.00192055, 0.00192172, 0.00192096, 0.00192140,
    0.00192118, 0.00192083, 0.00192155, 0.00192101,
    0.00192129, 0.00192074, 0.00192147, 0.00192110,
]

EXCITATION = 2.000        # V, bridge excitation
COMPLETION = 1000.0       # ohm, the three fixed arms
NOMINAL = 1000.0          # ohm, sensor resistance at 0 C
BRIDGE_RTH = 1000.0       # ohm, Thevenin resistance at the bridge output
DMM_RIN = 10.0e6          # ohm, multimeter input resistance

# stated limits, half-widths, all rectangular
U_EXCITATION_HALFWIDTH = 2.0e-3   # V, supply specification
U_COMPLETION_HALFWIDTH = 1.0      # ohm, 0.1% of 1000
U_NOMINAL_HALFWIDTH = 0.6         # ohm, class A Pt1000 at 0 C
'''},
            {"name": "main.py", "content": r'''
"""A Pt1000 bridge measurement, from twelve readings to one reported temperature.

TODO: one sentence naming the dominant contribution to the uncertainty, and saying
what you would change to improve the result and what you would not bother changing.
"""

import math

from bench import (RAW, EXCITATION, COMPLETION, NOMINAL, BRIDGE_RTH, DMM_RIN,
                   U_EXCITATION_HALFWIDTH, U_COMPLETION_HALFWIDTH,
                   U_NOMINAL_HALFWIDTH)

ALPHA = 3.85e-3  # per kelvin, platinum


def corrected_output(v_meas, r_th, r_in):
    """The bridge output before the multimeter loaded it, in volts."""
    # TODO: multiply by (1 + r_th / r_in).
    return 0.0


def sensor_resistance(v_out, vex, rc):
    """Sensor resistance, from an exact inversion of the quarter bridge."""
    # TODO: recover x = 4 Vo / (Vex - 2 Vo), then return rc * (1 + x).
    return 0.0


def temperature(rs, r0):
    """Temperature in degrees Celsius from a platinum sensor resistance."""
    # TODO: invert rs = r0 (1 + ALPHA T).
    return 0.0


def temperature_from(v_out, vex, rc, r0):
    """The whole chain, as one function of four inputs."""
    # TODO: compose sensor_resistance and temperature.
    return 0.0


def type_a(values):
    """Standard uncertainty of the mean of repeated readings."""
    # TODO: sample standard deviation over the square root of the count.
    return 0.0


def type_b_rect(halfwidth):
    """Standard uncertainty of a stated limit."""
    # TODO: a rectangular distribution has standard deviation a / sqrt(3).
    return 0.0


def budget(v_out, vex, rc, r0, u):
    """Contribution of each named input to the temperature, in kelvin.

    `u` maps input names -- any of "v_out", "vex", "rc", "r0" -- to their standard
    uncertainties. The result has the same keys.
    """
    # TODO: for each named input, a central difference for the sensitivity
    # coefficient, times that input's standard uncertainty, in magnitude.
    return {}


def combine(us):
    """Combined standard uncertainty of independent contributions."""
    # TODO: in quadrature.
    return 0.0


def report(value, u, k, unit):
    """The published string: value, expanded uncertainty, coverage factor."""
    # TODO: two significant figures on u, the value to the same decimal place.
    return ""


if __name__ == "__main__":
    v_mean = sum(RAW) / len(RAW)
    v_true = corrected_output(v_mean, BRIDGE_RTH, DMM_RIN)
    rs = sensor_resistance(v_true, EXCITATION, COMPLETION)
    t = temperature(rs, NOMINAL)
    print("mean reading      ", v_mean, "V")
    print("loading corrected ", v_true, "V")
    print("sensor resistance ", rs, "ohm")
    print("temperature       ", t, "C")

    u = {
        "v_out": type_a(RAW),
        "vex": type_b_rect(U_EXCITATION_HALFWIDTH),
        "rc": type_b_rect(U_COMPLETION_HALFWIDTH),
        "r0": type_b_rect(U_NOMINAL_HALFWIDTH),
    }
    b = budget(v_true, EXCITATION, COMPLETION, NOMINAL, u)
    print("budget, kelvin:")
    for name in sorted(b):
        print("   %-6s %s" % (name, b[name]))
    uc = combine(list(b.values()))
    print("combined standard uncertainty", uc, "K")
    print("reported:", report(t, 2.0 * uc, 2, "K"))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "main.py", "content": r'''
"""A Pt1000 bridge measurement, from twelve readings to one reported temperature.

The completion resistors dominate: their 0.1% tolerance contributes 0.151 K of the
0.176 K combined standard uncertainty, with the sensor's own 0.6 ohm tolerance next at
0.090 K. Measuring the four completion resistors once against a calibrated standard,
and using the measured values, would remove most of the budget; buying a better
multimeter would not, because the twelve readings contribute 0.00005 K and averaging
more of them would be effort spent on the smallest term in the sum.
"""

import math

from bench import (RAW, EXCITATION, COMPLETION, NOMINAL, BRIDGE_RTH, DMM_RIN,
                   U_EXCITATION_HALFWIDTH, U_COMPLETION_HALFWIDTH,
                   U_NOMINAL_HALFWIDTH)

ALPHA = 3.85e-3  # per kelvin, platinum


def corrected_output(v_meas, r_th, r_in):
    """The bridge output before the multimeter loaded it, in volts."""
    return v_meas * (1.0 + r_th / r_in)


def sensor_resistance(v_out, vex, rc):
    """Sensor resistance, from an exact inversion of the quarter bridge."""
    x = 4.0 * v_out / (vex - 2.0 * v_out)
    return rc * (1.0 + x)


def temperature(rs, r0):
    """Temperature in degrees Celsius from a platinum sensor resistance."""
    return (rs / r0 - 1.0) / ALPHA


def temperature_from(v_out, vex, rc, r0):
    """The whole chain, as one function of four inputs."""
    return temperature(sensor_resistance(v_out, vex, rc), r0)


def type_a(values):
    """Standard uncertainty of the mean of repeated readings."""
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(var) / math.sqrt(n)


def type_b_rect(halfwidth):
    """Standard uncertainty of a stated limit."""
    return halfwidth / math.sqrt(3.0)


def budget(v_out, vex, rc, r0, u):
    """Contribution of each named input to the temperature, in kelvin.

    `u` maps input names -- any of "v_out", "vex", "rc", "r0" -- to their standard
    uncertainties. The result has the same keys.
    """
    args = {"v_out": v_out, "vex": vex, "rc": rc, "r0": r0}
    out = {}
    for name, ux in u.items():
        h = abs(args[name]) * 1e-6
        if h == 0.0:
            h = 1e-12
        hi = dict(args)
        lo = dict(args)
        hi[name] = args[name] + h
        lo[name] = args[name] - h
        coeff = (temperature_from(**hi) - temperature_from(**lo)) / (2.0 * h)
        out[name] = abs(coeff * ux)
    return out


def combine(us):
    """Combined standard uncertainty of independent contributions."""
    return math.sqrt(sum(u * u for u in us))


def report(value, u, k, unit):
    """The published string: value, expanded uncertainty, coverage factor."""
    places = max(0, 1 - math.floor(math.log10(abs(u))))
    return "%.*f %s ± %.*f %s (k = %d)" % (places, value, unit,
                                                places, u, unit, k)


if __name__ == "__main__":
    v_mean = sum(RAW) / len(RAW)
    v_true = corrected_output(v_mean, BRIDGE_RTH, DMM_RIN)
    rs = sensor_resistance(v_true, EXCITATION, COMPLETION)
    t = temperature(rs, NOMINAL)
    print("mean reading      ", v_mean, "V")
    print("loading corrected ", v_true, "V")
    print("sensor resistance ", rs, "ohm")
    print("temperature       ", t, "C")

    u = {
        "v_out": type_a(RAW),
        "vex": type_b_rect(U_EXCITATION_HALFWIDTH),
        "rc": type_b_rect(U_COMPLETION_HALFWIDTH),
        "r0": type_b_rect(U_NOMINAL_HALFWIDTH),
    }
    b = budget(v_true, EXCITATION, COMPLETION, NOMINAL, u)
    print("budget, kelvin:")
    for name in sorted(b):
        print("   %-6s %s" % (name, b[name]))
    uc = combine(list(b.values()))
    print("combined standard uncertainty", uc, "K")
    print("reported:", report(t, 2.0 * uc, 2, "K"))
'''},
        ],
        "tests": [
            {"name": "the loading correction goes the right way", "code": r'''
v = corrected_output(0.00192115, 1000.0, 10.0e6)
assert v > 0.00192115, "the true output is larger than the loaded reading, not smaller"
assert abs(v - 0.001921342115) < 1e-15, \
    f"0.00192115 V through a 1 k / 10 M divider was really 0.001921342115 V, got {v}"
hard = corrected_output(1.0, 1e6, 1e4)
assert abs(hard - 101.0) < 1e-12, \
    f"a 1 M source read on a 10 k input is out by a factor of 101, got {hard}"
'''},
            {"name": "the bridge inversion is exact, not linearised", "code": r'''
rs = sensor_resistance(0.001921342115, 2.000, 1000.0)
assert abs(rs - 1003.8500815538356) < 1e-9, \
    f"that output means a sensor of 1003.85008 ohm, got {rs}"
forward = 2.000 * (1003.8500815538356 / 1000.0 - 1.0) / (4.0 + 2.0 * 0.0038500815538356)
assert abs(forward - 0.001921342115) < 1e-15, \
    "the forward relation must reproduce the output your inversion consumed"
big = sensor_resistance(2.000 * 0.1 / (4.0 + 0.2), 2.000, 1000.0)
assert abs(big - 1100.0) < 1e-9, \
    f"a 10% change must invert exactly to 1100 ohm, got {big} (the linear formula gives 1105)"
'''},
            {"name": "resistance becomes temperature", "code": r'''
assert abs(temperature(1000.0, 1000.0)) < 1e-12, "1000 ohm is 0 C by definition"
t = temperature(1003.85, 1000.0)
assert abs(t - 1.0) < 1e-12, f"1003.85 ohm is 1.000 C for alpha = 3.85e-3, got {t}"
cold = temperature(961.5, 1000.0)
assert abs(cold - (-10.0)) < 1e-9, f"961.5 ohm is -10.00 C, got {cold}"
'''},
            {"name": "the whole chain on the bench data", "code": r'''
v_mean = sum(RAW) / len(RAW)
assert abs(v_mean - 0.00192115) < 1e-15, f"the mean of the twelve readings is 1.92115 mV, got {v_mean}"
t = temperature_from(corrected_output(v_mean, BRIDGE_RTH, DMM_RIN),
                     EXCITATION, COMPLETION, NOMINAL)
assert abs(t - 1.0000211828144399) < 1e-9, \
    f"the bench run comes to 1.0000212 C, got {t}"
raw_t = temperature_from(v_mean, EXCITATION, COMPLETION, NOMINAL)
assert raw_t < t, "skipping the loading correction reads low; that is what loading does"
assert abs(t - raw_t - 1.00184587e-4) < 1e-9, \
    f"the loading correction is worth 0.0001 K here, got {t - raw_t}"
'''},
            {"name": "every input gets its own line in the budget", "code": r'''
u = {"v_out": type_a(RAW),
     "vex": type_b_rect(U_EXCITATION_HALFWIDTH),
     "rc": type_b_rect(U_COMPLETION_HALFWIDTH),
     "r0": type_b_rect(U_NOMINAL_HALFWIDTH)}
assert abs(u["v_out"] - 1.0146651933250557e-07) < 1e-15, \
    f"the Type A uncertainty of those twelve readings is 0.101 uV, got {u['v_out']}"
assert abs(u["rc"] - 0.5773502691896258) < 1e-12, "a 1 ohm limit is a 0.577 ohm standard uncertainty"
v_true = corrected_output(sum(RAW) / len(RAW), BRIDGE_RTH, DMM_RIN)
b = budget(v_true, EXCITATION, COMPLETION, NOMINAL, u)
assert set(b) == set(u), f"the budget must be keyed by the inputs it was given, got {sorted(b)}"
assert abs(b["rc"] - 0.15053847137212684) < 1e-6, \
    f"the completion resistors contribute 0.1505 K, got {b['rc']}"
assert abs(b["r0"] - 0.09032308282327609) < 1e-6, \
    f"the sensor tolerance contributes 0.0903 K, got {b['r0']}"
assert abs(b["vex"] - 0.0005784739432217952) < 1e-8, \
    f"the excitation contributes 0.00058 K, got {b['vex']}"
assert abs(b["v_out"] - 5.291301263200489e-05) < 1e-9, \
    f"the twelve readings contribute 0.000053 K, got {b['v_out']}"
assert b["rc"] > 1000 * b["v_out"], "the resistors dominate the readings by three orders of magnitude"
'''},
            {"name": "a budget can be re-run with terms switched off", "code": r'''
v_true = corrected_output(sum(RAW) / len(RAW), BRIDGE_RTH, DMM_RIN)
only = budget(v_true, EXCITATION, COMPLETION, NOMINAL, {"rc": 0.5773502691896258})
assert set(only) == {"rc"}, f"only the named inputs get a line, got {sorted(only)}"
assert abs(only["rc"] - 0.15053847137212684) < 1e-6, \
    "a contribution must not depend on which other terms were asked for"
none = budget(v_true, EXCITATION, COMPLETION, NOMINAL, {})
assert none == {}, "an empty budget is empty, not an error"
'''},
            {"name": "combination and the published line", "code": r'''
c = combine([0.15053847137212684, 0.09032308282327609,
             0.0005784739432217952, 5.291301263200489e-05])
assert abs(c - 0.1755574780111828) < 1e-9, \
    f"those four combine to 0.17556 K, got {c}"
line = report(1.0000211828144399, 2.0 * 0.1755574780111828, 2, "K")
assert line == "1.00 K ± 0.35 K (k = 2)", f"got {line!r}"
volts = report(9.901016666666667, 0.0034738707197847322, 2, "V")
assert volts == "9.9010 V ± 0.0035 V (k = 2)", f"got {volts!r}"
coarse = report(1234.5678, 21.3, 2, "V")
assert coarse == "1235 V ± 21 V (k = 2)", \
    f"an uncertainty above ten leaves no decimals at all, got {coarse!r}"
'''},
        ],
    },
}
