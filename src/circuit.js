/* ============ circuits ============
 *
 * A schematic you draw, and a solver that actually solves it.
 *
 *   Netlist   parts on a grid, wires between grid points, nodes by union-find
 *   MNA       modified nodal analysis — DC operating point, AC sweep, transient
 *   Editor    place, wire, move, edit values, delete; canvas only, no libraries
 *
 * The solver is the real method, not a lookup table of textbook answers: the same
 * stamps a SPICE engine uses, assembled into a matrix and solved by Gaussian
 * elimination with partial pivoting. Capacitors and inductors get companion models
 * for transient, and complex admittances for AC. Diodes, bipolars, MOSFETs and
 * op-amps are replaced each pass by the straight line tangent to their curve at the
 * present guess, and the whole circuit solved again until the node voltages stop
 * moving — Newton-Raphson, and the reason those parts can be on the canvas at all.
 *
 * Where a model stops is stated rather than hidden, in the panel beside the part that
 * uses it, because a learner who trusts a wrong answer is worse off than one who knows
 * where the tool ends. An iteration that does not settle says so and returns no
 * numbers at all, for exactly the same reason.
 */

/* ---------------------------------------------------------------- linear algebra */
const Lin = (function () {

  /* complex numbers as [re, im] — enough for AC, and cheaper than objects */
  function cadd(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
  function csub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
  function cmul(a, b) { return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]]; }
  function cdiv(a, b) {
    const d = b[0] * b[0] + b[1] * b[1];
    if (d === 0) return [0, 0];
    return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d];
  }
  function cabs(a) { return Math.hypot(a[0], a[1]); }

  /* Gaussian elimination with partial pivoting, over complex numbers.
     A singular matrix means the circuit is under-determined — a floating node, or a
     loop of voltage sources — and the caller turns that into a readable message. */
  function solve(A, b) {
    const n = b.length;
    const M = A.map(function (row, i) { return row.slice().concat([b[i]]); });
    for (let col = 0; col < n; col++) {
      let piv = col, best = cabs(M[col][col]);
      for (let r = col + 1; r < n; r++) {
        const m = cabs(M[r][col]);
        if (m > best) { best = m; piv = r; }
      }
      if (best < 1e-14) return null;
      if (piv !== col) { const t = M[col]; M[col] = M[piv]; M[piv] = t; }
      const d = M[col][col];
      for (let c = col; c <= n; c++) M[col][c] = cdiv(M[col][c], d);
      for (let r = 0; r < n; r++) {
        if (r === col) continue;
        const f = M[r][col];
        if (cabs(f) === 0) continue;
        for (let c = col; c <= n; c++) M[r][c] = csub(M[r][c], cmul(f, M[col][c]));
      }
    }
    return M.map(function (row) { return row[n]; });
  }

  function zeros(n) {
    const A = [];
    for (let i = 0; i < n; i++) {
      const row = [];
      for (let j = 0; j < n; j++) row.push([0, 0]);
      A.push(row);
    }
    return A;
  }

  return { solve: solve, zeros: zeros, cadd: cadd, csub: csub, cmul: cmul, cdiv: cdiv, cabs: cabs };
})();

/* What a microcontroller is holding when one is placed. Something that does
   something, rather than an empty editor: the first thing anyone wants to see is a
   pin they can watch move, and a blink is the shortest sketch that has one. */
const MCU_SKETCH = [
  '// pinMode says which way a pin faces. digitalWrite then drives it',
  '// to Vcc or to 0 V through the pin resistance — see the panel.',
  'void setup() {',
  '  pinMode(3, OUTPUT);',
  '}',
  '',
  'void loop() {',
  '  digitalWrite(3, HIGH);',
  '  delay(200);',
  '  digitalWrite(3, LOW);',
  '  delay(200);',
  '}',
  '',
].join('\n');

/* Sketch panels ever painted, for the ids the panel's label and its live region are
   wired together with. Module scope rather than per editor because an id has to be
   unique in the document and a page can hold more than one editor. */
let MCU_PANEL_SEQ = 0;

/* Every table below is indexed by `p.kind`, and a kind comes out of a MODEL — which
   reaches this file from a course's JSON, and also from `circuit.json` inside a progress
   document a learner imported from a file they were given. `{}` inherits from
   Object.prototype, so `PART_KINDS.toString` was a function before any part existed, and
   a part whose kind was "toString" got past every `if (!PART_KINDS[p.kind]) return` guard
   in the file and died four frames later on `k.of is not a function` — the whole
   schematic canvas, gone, on a drawing the learner did not write.
     Found by sweeping for the shape rather than by being pointed at it: it is the same
   defect as the five lookup tables in src/mcu.js, which is what this cycle came for. A
   null prototype is the same one-word fix, and nothing calls a method on any of these —
   they are read with [] and nothing else, which is what makes it safe. */
function bareTable(o) { return Object.assign(Object.create(null), o); }

/* ---------------------------------------------------------------- parts */
const PART_KINDS = bareTable({
  R: { name: 'Resistor', unit: 'Ω', def: 1000, pins: 2, sym: 'R' },
  C: { name: 'Capacitor', unit: 'F', def: 1e-6, pins: 2, sym: 'C' },
  L: { name: 'Inductor', unit: 'H', def: 1e-3, pins: 2, sym: 'L' },
  V: { name: 'Voltage source', unit: 'V', def: 5, pins: 2, sym: 'V' },
  I: { name: 'Current source', unit: 'A', def: 0.001, pins: 2, sym: 'I' },
  GND: { name: 'Ground', unit: '', def: 0, pins: 1, sym: '⏚' },
  /* Node numbering falls out of however the schematic was drawn, so a check has no
     way to name "the output" on its own. The learner marks it. Placing a probe is
     also the habit you want: measure where you meant to, not where it was easy. */
  OUT: { name: 'Probe', unit: '', def: 0, pins: 1, sym: '◦' },

  /* ---- parts that are a resistance the learner does not type ----
   *
   * A switch, a light-dependent resistor and a thermistor are all the same thing to
   * this solver: a resistance whose number comes from somewhere other than the value
   * box. Netlist.build works that number out before stamping, so the matrix never
   * learns that anything moved — one stamp, one solve, no iteration. The devices
   * further down the file do iterate, and deliberately not these: a thrown switch is
   * not a non-linearity, it is a number you chose. What makes them worth having is
   * that the "somewhere else" is a state you can click or a slider you can drag, and
   * the circuit answers.
   *
   * `state` is the extra data a kind carries beyond `value`, copied onto the part
   * when it is placed. */
  SW: { name: 'Switch', unit: 'Ω', def: 0, pins: 2, sym: 'SW', state: { closed: false } },
  LDR: { name: 'Light sensor', unit: 'Ω', def: 10000, pins: 2, sym: 'LDR', state: { gamma: 0.7 },
         senses: 'lux' },
  NTC: { name: 'Thermistor', unit: 'Ω', def: 10000, pins: 2, sym: 'NTC', state: { beta: 3950 },
         senses: 'tempC' },
  POT: { name: 'Potentiometer', unit: 'Ω', def: 10000, pins: 3, sym: 'POT', state: { wiper: 0.5 } },

  /* ---- parts whose current is a curve, not a ratio ----
   *
   * These are the ones the matrix cannot answer in a single solve, because what they
   * pass depends on the very voltages being solved for. Each declares its parameters
   * in `state` the way a sensor does, and each states its model — and what its model
   * leaves out — in the component panel. The defaults are chosen so the first number a
   * learner sees is the textbook one: 0.65 V across a silicon diode at a milliamp,
   * 1.9 V across a red LED at ten, 0.65 V of Vbe for a milliamp of collector current.
   *
   * `value` is whichever parameter the panel calls the value: the saturation current
   * for a junction, the transconductance parameter for a MOSFET, the open-loop gain
   * for an op-amp. */
  D: { name: 'Diode', unit: 'A', def: 1e-14, pins: 2, sym: 'D', state: { n: 1 } },
  LED: { name: 'LED', unit: 'A', def: 1e-18, pins: 2, sym: 'LED', state: { n: 2, inom: 0.02 } },
  NPN: { name: 'NPN transistor', unit: 'A', def: 1e-14, pins: 3, sym: 'NPN',
         state: { bf: 100, br: 1 } },
  PNP: { name: 'PNP transistor', unit: 'A', def: 1e-14, pins: 3, sym: 'PNP',
         state: { bf: 100, br: 1 } },
  NMOS: { name: 'N-channel MOSFET', unit: 'A/V²', def: 2e-3, pins: 3, sym: 'NMOS',
          state: { vth: 1, lambda: 0.02 } },
  PMOS: { name: 'P-channel MOSFET', unit: 'A/V²', def: 1e-3, pins: 3, sym: 'PMOS',
          state: { vth: 1, lambda: 0.02 } },
  OPAMP: { name: 'Op-amp', unit: '', def: 1e5, pins: 3, sym: 'OPAMP',
           state: { vpos: 15, vneg: -15 } },

  /* ---- readouts ----
   * LAMP and METER are resistances too, and say so. BAR touches nothing: it reads a
   * node the way the probe does and draws the answer. */
  LAMP: { name: 'Lamp', unit: 'Ω', def: 220, pins: 2, sym: 'LAMP', state: { pnom: 0.25 } },
  METER: { name: 'Ammeter', unit: 'Ω', def: 0.1, pins: 2, sym: 'METER' },
  BAR: { name: 'Bar display', unit: 'V', def: 5, pins: 1, sym: 'BAR' },

  /* ---- a piece of circuit, folded up ----
   * The one kind that is not a component. A block holds a schematic of its own and
   * shows a rectangle instead, and how many pins it has is a property of what was
   * folded into it rather than of the kind — so `pins` is 0 here and pinsOf asks the
   * block itself. It is not on the toolbar because there is nothing to place: a block
   * comes into existence by grouping a selection, and dies by ungrouping. */
  IC: { name: 'Block', unit: '', def: 0, pins: 0, sym: 'IC' },

  /* ---- a piece of connection, with nothing on it ----
   * The other kind that is not a component, and the only one that carries no current
   * at all. A board has no pins and stamps nothing; what it has is HOLES, and holes
   * that are already joined to one another before anything is put in them. `value` is
   * the number of columns, because a board's one dimension is how long it is. */
  BB: { name: 'Breadboard', unit: '', def: 30, pins: 0, sym: 'BB' },

  /* ---- a part that is a program ----
   * The third kind that is not a component, and the only one whose behaviour is not
   * in this file at all: what its pins do is decided by a sketch the learner writes,
   * run by the interpreter in src/mcu.js. `pins` is 0 for the same reason a block's
   * is — the count comes from MCU_PINS below rather than from the registry — and
   * `value` is 0 because there is no one number to type. What it carries instead is
   * `code`, and that is why `state` here holds a string where every other kind holds
   * a number. */
  MCU: { name: 'Microcontroller', unit: '', def: 0, pins: 0, sym: 'MCU',
         state: { code: MCU_SKETCH } },
});

/* The simulated world the sensors sense. Not part of the schematic — a circuit is
   the same circuit in the dark and in the light — so it is passed in beside the
   model and defaulted here for every caller that has no opinion. */
const ENV_DEFAULT = { lux: 200, tempC: 25 };

/* Switch resistances. Open is a very large resistance rather than a deleted branch:
   removing the branch would leave whatever hangs off the far side connected to
   nothing, and the solver reports that as an under-determined circuit — a baffling
   thing to show someone whose only crime was opening a switch. At 100 MΩ the far
   side still has a defined voltage, and the leakage through it (50 nA from a 5 V
   supply) is smaller than any real switch's. */
const SW_ON = 0.05, SW_OFF = 1e8;

/* How a sensor turns a simulated quantity into ohms. Both are the textbook models,
   named and parameterised in the component panel so the learner reads the curve
   rather than trusting it. Getting the SIGN of either one backwards would teach
   something false, so each is written to make the direction obvious:
   more light -> less resistance, more heat -> less resistance. */
const Sensors = {
  /* photoresistor power law: R = R10 * (10 lx / E)^gamma.
     gamma ~ 0.7 is a typical CdS cell. 10 lx is the stated reference point because
     a datasheet quotes one, and quoting it makes R10 a number you can look up. */
  ldr: function (r10, gamma, lux) {
    const E = Math.min(Math.max(lux, 0.01), 1e5);
    const g = Math.min(Math.max(gamma, 0.05), 3);
    return Math.min(Math.max(Math.max(r10, 1) * Math.pow(10 / E, g), 1), 1e9);
  },
  /* beta (B-parameter) model: R = R25 * exp(B * (1/T - 1/298.15)), T in kelvin.
     B > 0 makes the exponent negative as T rises, so the resistance falls — which is
     what the N in NTC means. It is a two-point fit, good to a few percent over a
     50 K span and no better; the Steinhart-Hart form is what you use when you need
     more, and this panel says so. */
  ntc: function (r25, beta, tempC) {
    const T = Math.max(tempC + 273.15, 1);
    const B = Math.min(Math.max(beta, 1), 20000);
    return Math.min(Math.max(Math.max(r25, 1) * Math.exp(B * (1 / T - 1 / 298.15)), 0.01), 1e12);
  },
};

/* ---------------------------------------------------------------- the pin model
 *
 * What a microcontroller IS, to a solver that only knows about conductances and
 * currents. Everything the sketch does reaches the matrix through these numbers and
 * nothing else, so they are the whole of the electrical claim this part makes, and
 * every one of them is quoted in the panel.
 *
 * The shape is always the same: a Thevenin source — a voltage behind a resistance —
 * stamped as its Norton equivalent between the pin and the part's OWN ground pin, and
 * never between the pin and node 0. That distinction costs one extra argument and is
 * the difference between a model that is right and a model that happens to be right
 * whenever the learner remembers to wire the ground pin to the same ground everything
 * else uses. An output at LOW is not a wire to ground; it is 25 Ω to the ground pin,
 * and if that pin is somewhere else then so is the output.
 *
 * A pin does not switch. digitalWrite lands a number in `drive`, and the next matrix
 * built reads it: there is no event, no edge and no instant in between two time steps.
 * What that costs is written where it is felt — see MCU_PWM below.
 */
const MCU_VCC = 5;                 /* the regulated supply the pins swing between */
const MCU_ROUT = 25;               /* a driver's on-resistance, which is what an AVR's is */
const MCU_RPULL = 40e3;            /* the internal pull-up; the datasheet says 20-50 kΩ */
const MCU_RSUP = 0.5;              /* what the Vcc pin can be loaded through */
/* An input draws nothing, and "nothing" has to be a resistance rather than an absence
   for exactly the reason an open switch does — see SW_OFF, which is the same number
   for the same reason: a pin wired to nothing else must still have a defined voltage,
   or the solver calls a perfectly ordinary circuit under-determined. */
const MCU_RIN = 1e8;
/* Thresholds. Not one threshold at half the supply: a real input is a Schmitt trigger,
   and the gap between the two is what stops a slowly-charging RC node from being read
   as a hundred alternating ones and zeros as it drifts across the middle. Between them
   a pin reads whatever it read last, which is what hysteresis means. 0.6 and 0.4 of
   Vcc are the AVR's own figures. */
const MCU_VIH = 0.6 * MCU_VCC, MCU_VIL = 0.4 * MCU_VCC;
const MCU_ADC_BITS = 10, MCU_ADC_MAX = 1023;

/* The pins, in the order they are drawn and the order pinsOf hands them over: down the
   left edge, then down the right. `n` is the number a sketch calls them by — 0 to 5,
   and 14 to 17 for the analogue four, which is where A0 lives on the board this is
   shaped after. Power is not numbered because no sketch can address it. */
/* The body is two rows taller than the pins need. Rows 0 and MCU_H carry no pin, and
   that empty band at each end is not padding for the look of it: a pin's name is
   written INWARD from its cell, and a pin on the very top row writes its name across
   the outline. It also leaves the two bands the title and the supply are written in,
   clear of every label rather than squeezed between two of them. */
const MCU_W = 4, MCU_H = 7;        /* the body, in cells beyond the origin */
const MCU_PINS = [
  { n: 0, name: '0', side: 0, row: 1, adc: false },
  { n: 1, name: '1', side: 0, row: 2, adc: false },
  { n: 2, name: '2', side: 0, row: 3, adc: false },
  { n: 3, name: '3', side: 0, row: 4, adc: false },
  { n: 4, name: '4', side: 0, row: 5, adc: false },
  { n: 5, name: '5', side: 0, row: 6, adc: false },
  { n: 14, name: 'A0', side: 1, row: 1, adc: true },
  { n: 15, name: 'A1', side: 1, row: 2, adc: true },
  { n: 16, name: 'A2', side: 1, row: 3, adc: true },
  { n: 17, name: 'A3', side: 1, row: 4, adc: true },
  { n: null, name: 'Vcc', side: 1, row: 5, power: 'vcc' },
  { n: null, name: 'GND', side: 1, row: 6, power: 'gnd' },
];

/* The state one part's pins are in. Reset is every pin an input: that is what a
   real one does on power-up, and it is also the only honest thing to stamp in an
   analysis that has no time in it — see the operating-point note in the panel. */
function mcuReset(id) {
  return { id: id, vcc: MCU_VCC,
           pins: MCU_PINS.map(function (d) {
             return { n: d.n, name: d.name, power: d.power || null, adc: !!d.adc,
                      node: 0, mode: 'in', drive: 0, last: 0 };
           }) };
}

/* The Norton a pin presents: a conductance to the ground pin, and a current into the
   pin node. One function, asked by the DC stamp, the AC stamp and every time step, so
   the three cannot come to disagree about what an output is. */
function mcuNorton(pin) {
  if (pin.power === 'gnd') return null;                    /* the reference itself */
  if (pin.power === 'vcc') return { g: 1 / MCU_RSUP, i: MCU_VCC / MCU_RSUP };
  if (pin.mode === 'out') return { g: 1 / MCU_ROUT, i: pin.drive * MCU_VCC / MCU_ROUT };
  if (pin.mode === 'pullup') {
    return { g: 1 / MCU_RIN + 1 / MCU_RPULL, i: MCU_VCC / MCU_RPULL };
  }
  return { g: 1 / MCU_RIN, i: 0 };
}

/* Volts on a pin to the bit a sketch reads, with the hysteresis above: `last` is
   carried on the pin so a voltage in the gap gives back what the pin gave last time
   rather than a coin toss. */
function mcuLevel(pin, volts) {
  if (volts >= MCU_VIH) pin.last = 1;
  else if (volts <= MCU_VIL) pin.last = 0;
  return pin.last;
}

/* The one resistance a dynamic part is worth, right now. Returns null for anything
   the solver already understands on its own. */
function ohmsOf(p, env) {
  const e = env || ENV_DEFAULT;
  if (p.kind === 'SW') return p.closed ? SW_ON : SW_OFF;
  if (p.kind === 'LDR') return Sensors.ldr(p.value, p.gamma === undefined ? 0.7 : p.gamma, e.lux);
  if (p.kind === 'NTC') return Sensors.ntc(p.value, p.beta === undefined ? 3950 : p.beta, e.tempC);
  if (p.kind === 'LAMP') return Math.max(p.value, 1e-3);
  if (p.kind === 'METER') return Math.max(p.value, 1e-6);
  return null;
}

/* Wiper 0..1 -> the two track resistances either side of it. Clamped away from a
   dead short at each end so a wiper wound fully over does not put a zero-ohm branch
   in the matrix. */
function potSplit(p) {
  const total = Math.max(p.value, 1e-3);
  const w = Math.min(Math.max(p.wiper === undefined ? 0.5 : p.wiper, 0), 1);
  return [Math.max(total * w, 1e-3), Math.max(total * (1 - w), 1e-3)];
}

/* A parameter a part may or may not carry. A schematic authored in a catalog file
   states only the fields its exercise cares about, so anything missing falls back to
   the default its kind declares rather than to undefined — which would otherwise reach
   an exponential as NaN and take every node in the circuit with it. The clamp is the
   same idea as the sensors': a diode with an ideality of zero is not a diode. */
function param(p, key, lo, hi) {
  const k = PART_KINDS[p.kind];
  const d = k && k.state ? k.state[key] : 0;
  const v = Number(p[key] === undefined ? d : p[key]);
  return Math.min(Math.max(isFinite(v) ? v : d, lo), hi);
}

/* ---------------------------------------------------------------- non-linear devices
 *
 * Everything above this line resolves to a number before the matrix is built. A diode
 * cannot: the current through it depends on the voltage across it, and that voltage is
 * what the matrix is being solved for. The way out is to guess an operating point,
 * replace each device by the straight line tangent to its curve there, solve that
 * linear circuit, and take the answer as the next guess. The loop lives in MNA; this
 * section is the physics it iterates on.
 *
 * Every device answers one question: given the voltages on my terminals, what current
 * flows into each of them, and how does each of those currents move when each terminal
 * voltage moves? That pair — a vector i[] and a Jacobian j[][] — plus v[], the point it
 * actually worked them out at, is all MNA needs, and it turns them into a conductance
 * and a current source without knowing which device they came from.
 *
 * v[] is returned rather than assumed because a device may not have used the voltages it
 * was handed: the limiting below routinely hands back a junction a long way from where
 * Newton asked for it. A tangent is a line through a POINT, and stamping the slope from
 * one point with the intercept from another describes no curve at all — the iteration
 * still lands on a real answer in the end, because at the end nothing is limited and the
 * two agree, but on the way it wanders, and a circuit that wanders far enough runs out
 * of passes and reports a failure it does not have. A diode, a bipolar and a MOSFET are therefore the same shape of thing
 * to the solver, and a fourth kind is one more function rather than one more stamp.
 *
 * The sign convention is the one the linear stamps already use: i[k] is positive when
 * current flows out of node k and into the device. A plain resistor written this way is
 * i = [g(v0−v1), −g(v0−v1)] with j = [[g,−g],[−g,g]] and v unchanged, which is exactly
 * what stampG assembles — so the two halves of the solver agree about which way current goes
 * without either of them having to be told.
 */

/* Thermal voltage, kT/q. Every exponential below is in units of it, and every panel
   quotes it, because "0.7 volts" is something you remember and kT/q is something you
   can derive. 300 K rather than 300.15 or 293: it is the temperature a datasheet draws
   its curves at, and picking anything else would make the numbers here disagree with
   the ones a learner looks up. Nothing in this file models any other temperature. */
const T_NOM = 300;
const VT = 1.380649e-23 * T_NOM / 1.602176634e-19;      /* 25.85 mV */

/* Past this many thermal voltages the exponential is continued as the straight line it
   had reached. Nothing should ever get here — pnjlim below is what keeps junction
   voltages in range — but a guard that returns a large finite number leaves a bad guess
   recoverable, where exp(2000) returns Infinity, Infinity minus Infinity returns NaN,
   and one solve later every node in the circuit is NaN. */
const EXP_CAP = 40;

/* The Shockley current and its slope together, because the solver always wants both. */
function pnExp(vj, nvt, is) {
  const top = EXP_CAP * nvt;
  if (vj <= top) {
    const ex = Math.exp(vj / nvt);
    return [is * (ex - 1), is * ex / nvt];
  }
  const ex = Math.exp(EXP_CAP);
  const g = is * ex / nvt;
  return [is * (ex - 1) + g * (vj - top), g];
}

/* The voltage past which a junction's conductance is climbing faster than the rest of
   the circuit can hold it down, and therefore where a step has to start being held. */
function vcritOf(is, nvt) {
  return nvt * Math.log(nvt / (Math.SQRT2 * Math.max(is, 1e-30)));
}

/* Junction limiting, and the reason a diode circuit solves at all from a cold start.
   The first Newton step is taken on a curve that is essentially flat at 0 V, so it asks
   for something like the whole supply across the junction; the next pass evaluates
   exp(5/0.026), which is e^193, gets a conductance of 1e70, and the pass after that is
   Infinity and then NaN across the whole circuit. The fix is not to refuse the step but
   to compress it: past vcrit a forward step is replaced by the Vt·ln of itself, which
   is still a large move in the direction Newton asked for and a small move in current.
   Steps the other way are left alone — an exponential running backwards underflows to
   zero, which is harmless and is also the right answer. */
function pnjlim(vnew, vold, nvt, vcrit) {
  if (vnew > vcrit && Math.abs(vnew - vold) > 2 * nvt) {
    if (vold > 0) {
      const arg = 1 + (vnew - vold) / nvt;
      return arg > 0 ? vold + nvt * Math.log(arg) : vcrit;
    }
    return nvt * Math.log(vnew / nvt);
  }
  return vnew;
}

/* What voltage to evaluate a junction at on this pass: the one the last solve implies,
   held back by pnjlim so the exponential cannot run away — except on the very first
   pass, which has no last solve to imply anything. The all-zero guess a cold start
   begins from puts every junction at 0 V, where the curve is flat, and the limiter then
   has to climb to the knee one Vt·ln at a time: thirty-odd passes to arrive somewhere
   the first pass could simply have been put. So a junction with no history is started AT
   the knee. The second pass then lands within a hundred millivolts of the answer, with
   Newton correcting downwards from there — the direction nothing limits, so it costs
   nothing. Being placed rather than solved, that first value counts as a limited step
   and does not let the iteration call itself converged. */
function junctionV(st, key, asked, nvt, vcrit) {
  const had = st[key];
  const v = had === undefined ? vcrit : pnjlim(asked, had, nvt, vcrit);
  if (v !== asked) st.lim = true;
  st[key] = v;
  return v;
}

/* A level-1 MOSFET is a polynomial, so unlike a junction it has nothing to overflow.
   What it has is three regions with a corner between them, and a step that jumps clean
   across a corner can sit there swapping cutoff for saturation and back for as long as
   you let it. Capping how far a controlling voltage may move in one pass costs a few
   passes and stops the swap. Two volts because that is comfortably wider than the gap
   between the corners of any sane device and narrow enough to land inside a region. */
const FET_STEP = 2;
function fetlim(vnew, vold) {
  if (vnew > vold + FET_STEP) return vold + FET_STEP;
  if (vnew < vold - FET_STEP) return vold - FET_STEP;
  return vnew;
}

/* An op-amp is not ideal here, and the two departures are what make it solvable. Its
   open-loop gain is finite: an infinite one would put a row of all zeros in the matrix,
   which is a singular matrix and not an answer. And its output is driven through a real
   resistance, so the output pin is a Norton source — a conductance and a current — and
   needs no extra unknown of its own. 75 Ω is what a small op-amp's open-loop output
   resistance actually is, so the honest model and the convenient one are the same. */
const OP_ROUT = 75;

const Devices = (function () {

  /* ---- diode, and the LED that is the same equation with different numbers ----
     Terminals [anode, cathode], which is pin order: the end the triangle points away
     from, then the bar. */
  function diode(d, v, st) {
    const nvt = d.n * VT;
    const asked = v[0] - v[1];
    const vd = st.raw ? asked
      : junctionV(st, 'vd', asked, nvt, vcritOf(d.is, nvt));
    const r = pnExp(vd, nvt, d.is);
    return { i: [r[0], -r[0]], j: [[r[1], -r[1]], [-r[1], r[1]]],
             v: [v[1] + vd, v[1]] };
  }

  /* ---- bipolar, Ebers-Moll in transport form ----
     Terminals in pin order, which for every three-pin part is the two along the body
     and then the control pin: [collector, emitter, base]. Not the C-B-E a datasheet
     lists, and deliberately not — every device here is indexed the way its pins come
     off the grid, so nothing between the netlist and the panel has to remember a
     per-device permutation, which is exactly the sort of thing that is wrong once and
     then wrong everywhere.
     Two junctions, two betas, and nothing else: the collector current is the difference
     between what the two junctions inject, and the base current is each junction's own
     current divided by its beta.

     `s` is +1 for an NPN and −1 for a PNP, and that is the whole difference between
     them. Negating the junction voltages AND the terminal currents leaves the Jacobian
     alone, because the two sign flips cancel in the derivative — so there is one set of
     partials written out here and not two nearly-identical sets to keep in step. */
  function bjt(d, v, st) {
    const s = d.sign, nvt = VT, vcrit = vcritOf(d.is, nvt);
    const abe = s * (v[2] - v[1]), abc = s * (v[2] - v[0]);
    const vbe = st.raw ? abe : junctionV(st, 'vbe', abe, nvt, vcrit);
    const vbc = st.raw ? abc : junctionV(st, 'vbc', abc, nvt, vcrit);
    const F = pnExp(vbe, nvt, d.is), R = pnExp(vbc, nvt, d.is);
    const rf = 1 / d.bf, rr = 1 / d.br;
    const ic = F[0] - R[0] * (1 + rr);
    const ib = F[0] * rf + R[0] * rr;
    /* rows and columns both in pin order [collector, emitter, base]; the emitter takes
       back whatever the other two passed, which is why its row is the negated sum */
    const gr = R[1] * (1 + rr);
    const jc = [gr, -F[1], F[1] - gr];
    const jb = [-R[1] * rr, -F[1] * rf, F[1] * rf + R[1] * rr];
    const je = [-jc[0] - jb[0], -jc[1] - jb[1], -jc[2] - jb[2]];
    /* the terminal voltages these were worked out at, which after limiting are not the
       ones handed in: the emitter is left where it was and the other two put wherever
       the two junction voltages actually used imply */
    return { i: [s * ic, -s * (ic + ib), s * ib], j: [jc, je, jb],
             v: [v[1] + s * (vbe - vbc), v[1], v[1] + s * vbe] };
  }

  /* the square law itself: drain current, transconductance and output conductance */
  function square(vgs, vds, d) {
    const vov = vgs - d.vth;
    if (vov <= 0) return [0, 0, 0];                                   /* cutoff */
    const e = 1 + d.lambda * vds;
    if (vds < vov) {                                                  /* triode */
      const q = vov * vds - 0.5 * vds * vds;
      return [d.k * q * e, d.k * vds * e,
              d.k * (vov - vds) * e + d.k * q * d.lambda];
    }
    return [0.5 * d.k * vov * vov * e,                                /* saturation */
            d.k * vov * e,
            0.5 * d.k * vov * vov * d.lambda];
  }

  /* ---- MOSFET, SPICE level 1 ----
     Terminals in pin order again: [drain, source, gate]. The gate draws nothing at all,
     which is exactly why gmin exists — a gate wired only to another gate is a node with
     no conductance on it anywhere, and a matrix row of zeros is not an answer. */
  function mos(d, v, st) {
    const s = d.sign;
    let vgs = s * (v[2] - v[1]);
    let vds = s * (v[0] - v[1]);
    if (!st.raw) {
      const ags = vgs, ads = vds;
      vgs = fetlim(vgs, st.vgs === undefined ? 0 : st.vgs);
      vds = fetlim(vds, st.vds === undefined ? 0 : st.vds);
      if (vgs !== ags || vds !== ads) st.lim = true;
      st.vgs = vgs; st.vds = vds;
    }
    let id, gm, gds;
    if (vds >= 0) {
      const m = square(vgs, vds, d);
      id = m[0]; gm = m[1]; gds = m[2];
    } else {
      /* Below its own source the channel simply runs the other way, so the same square
         law applies with drain and source exchanged. Solving in the swapped frame and
         mapping the partials back is what lets a MOSFET be a pass gate, where which end
         is the source is decided by the signal and not by the drawing. */
      const m = square(vgs - vds, -vds, d);
      id = -m[0]; gm = -m[1]; gds = m[1] + m[2];
    }
    /* the drain row against [Vd, Vs, Vg]; the source row is its negative, and the gate
       row is empty because the gate passes nothing whatever the rest of it does */
    const row = [gds, -(gm + gds), gm];
    return { i: [s * id, -s * id, 0],
             j: [row, [-row[0], -row[1], -row[2]], [0, 0, 0]],
             v: [v[1] + s * vds, v[1], v[1] + s * vgs] };
  }

  /* ---- op-amp ----
     Terminals [in+, out, in−]: the two along the body and the control pin at right
     angles to it, which is the geometry a potentiometer already established.

     The output follows the gain until it reaches a rail and then stops, and the stop is
     a tanh rather than a hard clip on purpose. A hard clip has a slope of exactly zero
     beyond the corner, and Newton cannot steer on a slope of zero: it would put the
     output on a rail and have nothing to tell it how to come back. tanh saturates just
     as firmly, keeps a slope the whole way, and needs no limiting of its own — it is
     bounded everywhere, so unlike an exponential it cannot be made to overflow. */
  function opamp(d, v, st) {
    const mid = (d.vpos + d.vneg) / 2;
    const sw = Math.max((d.vpos - d.vneg) / 2, 1e-3);
    const lin = sw / d.gain;                    /* half-width of the linear region */
    const th = Math.tanh((v[0] - v[2]) / lin);
    const gout = 1 / OP_ROUT;
    const a = d.gain * (1 - th * th) * gout;    /* the slope actually in force */
    /* nothing here is limited, so the point used is the point handed in — and it has to
       be reported all the same, because unlike every other device the op-amp's rows do
       not sum to zero (its output current comes from a supply that is not drawn), so its
       equivalent current genuinely depends on where the terminals are and not only on
       the differences between them */
    return { i: [0, gout * (v[1] - (mid + sw * th)), 0],
             j: [[0, 0, 0], [-a, gout, a], [0, 0, 0]], v: v };
  }

  function junction(p) {
    return { is: Math.max(p.value, 1e-30), n: param(p, 'n', 0.5, 4) };
  }
  function bipolar(p, s) {
    return { is: Math.max(p.value, 1e-30), sign: s,
             bf: param(p, 'bf', 1, 5000), br: param(p, 'br', 0.01, 100) };
  }
  function fet(p, s) {
    return { k: Math.max(p.value, 1e-12), sign: s,
             vth: param(p, 'vth', 0.05, 20), lambda: param(p, 'lambda', 0, 1) };
  }

  const KIND = {
    D: { iv: diode, of: junction },
    LED: { iv: diode, of: junction },
    NPN: { iv: bjt, of: function (p) { return bipolar(p, 1); } },
    PNP: { iv: bjt, of: function (p) { return bipolar(p, -1); } },
    NMOS: { iv: mos, of: function (p) { return fet(p, 1); } },
    PMOS: { iv: mos, of: function (p) { return fet(p, -1); } },
    OPAMP: { iv: opamp, of: function (p) {
      const hi = param(p, 'vpos', -100, 100), lo = param(p, 'vneg', -100, 100);
      return { gain: Math.min(Math.max(p.value, 10), 1e9),
               vpos: Math.max(hi, lo + 1e-3), vneg: Math.min(lo, hi - 1e-3) };
    } },
  };

  /* One device, ready to be asked for currents. The parameters are read out of the part
     ONCE here rather than on every pass, so a Newton loop of a hundred passes across
     four thousand time steps is not four hundred thousand trips through the clamps. */
  function build(p) {
    const k = KIND[p.kind];
    if (!k) return null;
    const d = k.of(p);
    d.iv = k.iv;
    d.kind = p.kind;
    d.id = p.id;
    return d;
  }

  return {
    is: function (kind) { return !!KIND[kind]; },
    build: build,
    /* the drop a junction settles at for a given current, which is what the panel
       quotes: the model read backwards, so the number cannot drift from the model */
    dropAt: function (is, n, amps) { return n * VT * Math.log(amps / is + 1); },
    VT: VT, T_NOM: T_NOM, OP_ROUT: OP_ROUT,
  };
})();

/* engineering notation both ways, because 1e-6 is not how anyone says a microfarad */
function fmtEng(v, unit) {
  if (v === 0) return '0 ' + unit;
  const a = Math.abs(v);
  const P = [[1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'],
             [1e-6, 'µ'], [1e-9, 'n'], [1e-12, 'p']];
  for (const [mul, pre] of P) {
    if (a >= mul * 0.999) {
      const s = (v / mul);
      let txt = Math.abs(s) >= 100 ? s.toFixed(0)
        : Math.abs(s) >= 10 ? s.toFixed(1) : s.toFixed(2);
      /* Trim only the zeros that follow a decimal point. Trimming unconditionally
         ate the zeros of an integer, so a 100 pF capacitor was labelled 1 pF and a
         200 ohm resistor 2 ohm — on the schematic the learner reads while working
         out why the answer is a hundred times off. */
      if (txt.indexOf('.') >= 0) txt = txt.replace(/0+$/, '').replace(/\.$/, '');
      return txt + ' ' + pre + unit;
    }
  }
  return v.toExponential(2) + ' ' + unit;
}

function parseEng(text, fallback) {
  const m = /^\s*(-?[\d.]+(?:[eE][-+]?\d+)?)\s*([GMkmunpµ]?)/.exec(String(text));
  if (!m) return fallback;
  const mul = { G: 1e9, M: 1e6, k: 1e3, '': 1, m: 1e-3, u: 1e-6, 'µ': 1e-6, n: 1e-9, p: 1e-12 };
  const v = parseFloat(m[1]) * (mul[m[2]] !== undefined ? mul[m[2]] : 1);
  return isFinite(v) ? v : fallback;
}

/* The kinds whose value is a quantity that cannot be zero or negative, and the floor
   each one is held above. A source may sit at zero and may be negative — that is a
   direction, and the whole of superposition depends on being able to write it. A
   resistance, a capacitance, an inductance, a saturation current, a transconductance
   and an open-loop gain may not: none of them has a meaning at zero, and every stamp
   that consumes one already defends itself against the number, which is exactly why
   nothing ever reported the value that got in.
   Floors are set far below anything a lesson uses — a femtofarad, a picohenry, a
   micro-ohm — because the job here is to reject the impossible, not to police the
   unusual. `SW` is absent: its resistance comes from its state, not from the box, and
   it has no value field on the panel at all.
   FIVE of them are not at that micro-ohm, and the reason is the whole point of the
   table. A floor is only honest if a value AT it reaches the solver unchanged; below
   that the box accepts a number the stamp then silently replaces, which is the exact
   defect — the panel reading one thing and the solver using another — that this table
   was minted to close. The five kinds whose resistance is resolved rather than typed
   each carry a guard of their own: ohmsOf holds a lamp at 1 mΩ and a meter at 1 µΩ,
   potSplit holds a track at 1 mΩ per half, and Sensors holds both R10 and R25 at 1 Ω.
   At 1e-6 the table was a million times under Sensors' guard, so an LDR set to a
   micro-ohm was accepted, drawn, saved and reloaded at a micro-ohm and stamped at one
   ohm. Each of the five now sits at the number its own resolver will actually honour,
   and verify_circuit_model.mjs resolves every one of them at the floor and requires the
   value back unchanged. */
const VALUE_FLOOR = bareTable({
  R: 1e-6, LDR: 1, NTC: 1, POT: 1e-2, LAMP: 1e-3, METER: 1e-6,
  C: 1e-15, L: 1e-12,
  D: 1e-30, LED: 1e-30, NPN: 1e-30, PNP: 1e-30,
  NMOS: 1e-12, PMOS: 1e-12, OPAMP: 1,
});
/* And the other end of the same field, which the floor above never had.
   The floor exists because a resistance of zero was stamped as a 1 pΩ short while the
   panel read 0 Ω. The ceiling exists for the mirror-image reason: what reaches a stamp
   is not the value but something BUILT from it, and a capacitor's companion conductance
   is C divided by the time step — so it leaves double precision at a capacitance the
   value box was perfectly happy with, and the answer comes back as 900 samples of NaN.
   Set, like the floors, far above anything a lesson uses: the largest of each kind in
   the whole catalogue is 9 MΩ, 20 F, 15 H, 230 V and 25 A, so every one of these has
   five orders of headroom or more. The job is to reject the impossible, not to police
   the unusual, and verify_circuit_model.mjs checks both directions against the
   catalogue so a ceiling that condemned working content would fail rather than ship.
   V and I are here and NOT in the floor table, which is not an inconsistency: a source
   carries a sign that means direction and half the superposition material depends on
   being able to write it, while none of it depends on being able to write 1e308 V. */
const VALUE_CEIL = bareTable({
  /* LDR at a gigohm and not a terohm, because Sensors.ldr caps its own result there and
     a ceiling above a resolver's own cap is the floor defect wearing the other hat — the
     box would accept a terohm and the stamp would use a gigohm. Found by the gate at the
     first run of the check written for the floor, which is the argument for writing the
     check as a rule rather than as a list of the five kinds already known to be wrong. */
  R: 1e12, LDR: 1e9, NTC: 1e12, POT: 1e12, LAMP: 1e12, METER: 1e12,
  C: 1e6, L: 1e6,
  D: 1e3, LED: 1e3, NPN: 1e3, PNP: 1e3,
  NMOS: 1e6, PMOS: 1e6, OPAMP: 1e12,
  V: 1e9, I: 1e9,
});
function clampValue(kind, v, fallback) {
  if (!isFinite(v)) return fallback;
  const floor = VALUE_FLOOR[kind];
  if (floor !== undefined && v < floor) return floor;
  const ceil = VALUE_CEIL[kind];
  /* on the SIZE, so a −230 V supply is still a −230 V supply */
  if (ceil !== undefined && Math.abs(v) > ceil) return v < 0 ? -ceil : ceil;
  return v;
}

/* Quarter turns clockwise, normalised. Module level rather than tucked inside the
   netlist because the pins, the polarity, the drawing and the panel all have to agree
   about which way round a part is, and one function is how they are made to. */
function turnsOf(p) { return ((((p.rot || 0) | 0) % 4) + 4) % 4; }

/* ---- a drawing the editor was handed is not a drawing it can trust ----
 *
 * A model reaches createCircuit from four doors and only one of them is authored: a
 * lesson's `start`, a question's figure, the Playground's saved circuit, and
 * `P.build[id]` — the learner's own saved work. That last one comes back through
 * `sanitiseProgress`, which shape-checks the map and passes every drawing inside it
 * through **verbatim**, and `importProgress` fills that map from a file on disk. So
 * arbitrary JSON reaches this editor through a supported gesture, and until now the
 * editor deep-copied it and drew it. Both of the following were measured through the
 * shipped editor before this was written.
 *
 *   * A COORDINATE LARGE ENOUGH TO STOP ARITHMETIC. paint()'s grid ran
 *     `for (X = ...; X < ...; X += GRID)`, and above 2^58 — 2.882e17 — adding 26 to a
 *     double does not change it. zoomFit puts the viewport at about 13 times the
 *     largest coordinate, so a wire ending at x = 1e17 froze the tab on the first press
 *     of Fit. Not slowly: the loop never takes a second step, and there is no way out
 *     of it but closing the page. x = 1e16 returned in 1 ms; 1e17 had not returned when
 *     the run was killed at 25 seconds.
 *
 *   * A COORDINATE THAT IS A STRING. `x - 1` coerces and `x + 1` concatenates, so a
 *     part saved with x: "6" reports its pins at cells 5 and **"61"**. The resistor is
 *     drawn where it was put and the netlist joins a node 55 cells away — the solver
 *     answering about a circuit that is not the one on the screen, which is the worst
 *     shape a defect can take here. It cannot be picked up and moved either: measured,
 *     an identical part with a numeric x drags from 5 to 8 and the string one does not
 *     move at all.
 *
 * The bound is on the SIZE and it is enormous on purpose. The widest drawing in the
 * whole catalogue is 27 cells across and the tallest 19 — counted, not estimated — so a
 * million is four orders above anything real and ten orders below where the arithmetic
 * goes. The job is to reject the impossible, not to police the unusual: the rule
 * VALUE_CEIL is set by, applied to geometry.
 */
const CELL_LIMIT = 1e6;
const DRAW_DEPTH = 8;        /* blocks nest, and Netlist.flatten stops at the same number */

function cellOf(v) {
  /* Only a number, or a string that is one. Number() alone would be worse than no check
     at all here: Number(null), Number(false) and Number('') are all 0, so a coordinate
     that is missing would become the coordinate ZERO — a part silently moved to the
     origin, on top of whatever is already there, and joined to it by the netlist. A
     dropped part is visible; a moved one is a different circuit that looks fine. */
  if (typeof v !== 'number' && typeof v !== 'string') return null;
  if (typeof v === 'string' && !v.trim()) return null;
  const n = Math.round(Number(v));
  return isFinite(n) && Math.abs(n) <= CELL_LIMIT ? n : null;
}
function pointOf(pt) {
  if (!Array.isArray(pt)) return null;
  const x = cellOf(pt[0]), y = cellOf(pt[1]);
  return x === null || y === null ? null : [x, y];
}
/* R1, R2, C1 — a part's number among its own KIND, on its own CANVAS.

   The label used to be the part's creation index across every kind, so a canvas that
   already held a ground and a source gave you "R8" for your first resistor, and every
   schematic in the catalog — all of which predate this — read V0 and R3. The number a
   learner sees has to be the one they would write on paper.

   The table lives out here rather than inside the editor because the sanitiser needs
   it: designators are stamped on the way IN, which is the one place that covers the
   catalog's drawings, a learner's saved circuit and a read-only diagram alike. */
const REF_PREFIX = { R: 'R', C: 'C', L: 'L', V: 'V', I: 'I', D: 'D', LED: 'LED',
  SW: 'SW', LDR: 'LDR', NTC: 'NTC', POT: 'POT', LAMP: 'LA', METER: 'ME', BAR: 'BA',
  NPN: 'Q', PNP: 'Q', NMOS: 'M', PMOS: 'M', OPAMP: 'U', IC: 'U', MCU: 'MCU',
  GND: 'GND', OUT: 'TP', BB: 'BB' };

function refPrefix(kind) { return REF_PREFIX[kind] || kind; }

/* A part that already carries a number keeps it — that is what stops a canvas somebody
   is halfway through annotating from renumbering itself when it is reopened — and the
   gaps are filled in drawing order, skipping numbers already claimed. */
function stampRefs(parts) {
  const used = {};
  parts.forEach(function (p) {
    if (typeof p.ref !== 'number') return;
    const pre = refPrefix(p.kind);
    (used[pre] = used[pre] || {})[p.ref] = 1;
  });
  parts.forEach(function (p) {
    if (typeof p.ref === 'number') return;
    const pre = refPrefix(p.kind);
    const seen = used[pre] = used[pre] || {};
    let n = 1;
    while (seen[n]) n++;
    seen[n] = 1;
    p.ref = n;
  });
}

function sanitiseDrawing(m, depth) {
  const out = { parts: [], wires: [] };
  if (!m || typeof m !== 'object' || Array.isArray(m)) return out;
  /* everything that is not geometry is carried across untouched — `env`, a block's
     title and description, whatever a later kind adds — because this function's job is
     the coordinates and a sanitiser that silently drops fields is its own defect */
  Object.keys(m).forEach(function (k) {
    if (k !== 'parts' && k !== 'wires' && k !== '__proto__') out[k] = m[k];
  });
  const d = (depth || 0) + 1;
  (Array.isArray(m.parts) ? m.parts : []).forEach(function (p) {
    if (!p || typeof p !== 'object' || Array.isArray(p)) return;
    const x = cellOf(p.x), y = cellOf(p.y);
    /* A part whose cell cannot be recovered is dropped, not moved to the origin. Moved,
       it would land on top of whatever is already there and the netlist would join it —
       a wrong circuit that looks like a right one, which is exactly what the string case
       above already produced. Dropped, the drawing is short one part and the learner can
       see that it is. */
    if (x === null || y === null) return;
    /* And a part of a kind this build does not have, for the same reason and by the
       same rule. Everything downstream reads PART_KINDS[p.kind] and uses the answer
       without asking — `k.pins`, `k.sym`, `k.def` — so an unknown kind was not a part
       drawn wrongly, it was a TypeError four frames into paint() and the whole canvas
       gone. That is reachable: a model reaches this file from a course's JSON, which is
       validated, and from `circuit.json` inside a progress document, which is a file the
       learner was handed. It was two defects wearing one coat — the table inheriting
       from Object.prototype made "toString" a kind, and a kind nobody has ever heard of
       crashed just the same. Sealing the tables fixed the first; this is the second, and
       it is the one that was always there. */
    if (!PART_KINDS[p.kind]) return;
    const q = {};
    Object.keys(p).forEach(function (k) { if (k !== '__proto__') q[k] = p[k]; });
    q.x = x; q.y = y;
    /* Normalised only where it is written. `rot` absent already means zero everywhere —
       turnsOf((p.rot || 0)) — so adding it would change 1081 parts across the 386
       published drawings for no behaviour at all, and would write the difference back
       into the learner's save on the next edit. A guard is measured by what it does to
       what is already right, and the right answer there is nothing. */
    if (p.rot !== undefined) q.rot = turnsOf(p);
    if (q.value !== undefined) {
      const k = PART_KINDS[q.kind];
      q.value = clampValue(q.kind, Number(q.value), k ? k.def : 0);
    }
    /* A block's ports are cells as well, measured from the block's own origin, and a
       port off at 1e17 reaches paint() through pinsOf exactly as a part does. */
    if (Array.isArray(p.ports)) {
      q.ports = p.ports.map(function (port) {
        if (!port || !Array.isArray(port.cells)) return port;
        return Object.assign({}, port, { cells: port.cells.map(pointOf).filter(Boolean) });
      });
    }
    if (p.inner) {
      /* Deeper than the netlist will flatten is a drawing nothing can solve, so it is
         emptied rather than carried — and the recursion is bounded by the same number
         the solver bounds itself by rather than by a second opinion about nesting. */
      q.inner = d < DRAW_DEPTH ? sanitiseDrawing(p.inner, d) : { parts: [], wires: [] };
    }
    out.parts.push(q);
  });
  (Array.isArray(m.wires) ? m.wires : []).forEach(function (wr) {
    if (!wr || typeof wr !== 'object') return;
    const a = pointOf(wr.a), b = pointOf(wr.b);
    if (a === null || b === null) return;
    out.wires.push({ a: a, b: b });
  });
  /* Each block's insides were stamped by their own recursive call above, because a
     block is its own schematic and its own namespace. */
  stampRefs(out.parts);
  return out;
}

/* The two ends of a body and its control pin, in the words the drawing puts them in. */
function pinWords(p) {
  return [['left', 'right', 'above'], ['top', 'bottom', 'to the right'],
          ['right', 'left', 'below'], ['bottom', 'top', 'to the left']][turnsOf(p)];
}

/* ---------------------------------------------------------------- breadboard
 *
 * Everywhere else on this canvas, two things are connected because a wire was drawn
 * between them. A breadboard is the one place where they are connected because of
 * where they were PUT. That is the whole part and the whole difficulty: the drawing
 * shows holes and no wires, and the netlist has to agree with the reader that a strip
 * of five holes is already one node.
 *
 * The rows, top to bottom, in the layout of the board a learner has actually held:
 *
 *     row 0            + rail, running the whole length
 *     row 1            − rail, running the whole length
 *     rows 2..6        terminal strips, five holes, ONE PER COLUMN
 *     row 7            the channel — no holes at all
 *     rows 8..12       terminal strips again, and separately
 *     row 13           − rail
 *     row 14           + rail
 *
 * So the rails run ALONG the board and the terminal strips run ACROSS it, which is
 * the crossing that makes the thing useful: a supply reaches every column, and each
 * column is still its own node. The channel is what separates the two halves of a
 * column, and it is one cell wide for a reason that is not cosmetic. A two-pin part
 * in this editor spans exactly two cells (see pinsOf), so a channel one cell wide is
 * the only width at which an ordinary resistor can bridge it and land one pin in each
 * half — which is how a DIP sits, and the gesture the board exists to teach. A real
 * channel is 0.3 in and would be two cells here; a board nothing in the toolbox could
 * straddle would be a picture of a breadboard rather than one.
 */
const BB_RAIL = 2;                                   /* rail lines along each edge */
const BB_STRIP = 5;                                  /* holes in one terminal strip */
const BB_CHAN = BB_RAIL + BB_STRIP;                  /* the row the channel is on */
const BB_H = BB_RAIL * 2 + BB_STRIP * 2 + 1;         /* rows of holes plus the channel */
const BB_COLS = 30;                                  /* the half-size board, 30 columns */

/* Clamped, and defaulted the way `param` defaults a device parameter: a board authored
   in a catalog file may state only that it is a board. Four columns is the shortest
   thing still worth calling one. */
function bbCols(p) {
  const n = Math.round(Number(p.value));
  return Math.min(Math.max(isFinite(n) && n > 0 ? n : BB_COLS, 4), 200);
}

/* Which strip a grid cell is a hole of, or null if the cell is not a hole of this
   board — off it, or in the channel. The id is a STRING and it only has to be unique
   within one board, since that is the only place it is ever compared. Rails are named
   by their row, so every column of a rail row answers the same id and the rail is one
   node down the length of the board; terminal holes are named by their column and by
   which side of the channel they are on, so the two halves of a column are two nodes
   that happen to be drawn in line with each other. */
function bbStripAt(p, cx, cy) {
  const c = cx - p.x, r = cy - p.y;
  if (c < 0 || c >= bbCols(p) || r < 0 || r >= BB_H) return null;
  if (r === BB_CHAN) return null;
  if (r < BB_RAIL || r >= BB_H - BB_RAIL) return 'rail' + r;
  return (r < BB_CHAN ? 'u' : 'l') + c;
}

/* The cells a part covers beyond the one it stands on, or null if it stands on one
   cell like every symbol does. A block and a board are bodies with an area, and the
   netlist's flattener, the editor's hit test, the marquee, zoom-to-fit and the
   read-only painter all have to agree about how big they are — so they ask here
   rather than each carrying its own idea of which kinds are big. */
function bodyOf(p) {
  if (p.kind === 'IC') return [Math.max(1, p.w || 0), Math.max(1, p.h || 0)];
  if (p.kind === 'BB') return [bbCols(p) - 1, BB_H - 1];
  if (p.kind === 'MCU') return [MCU_W, MCU_H];
  return null;
}

/* ---------------------------------------------------------------- netlist */
const Netlist = (function () {

  /* Pins in grid coordinates. A part sits at (x, y) and is either horizontal or
     vertical; two-pin parts span two cells so a wire can meet them squarely. */
  /* `rot` counts quarter turns clockwise: 0 lying flat, 1 standing up, and 2 and 3 the
     same two the other way round. Two of them were enough while every part the solver
     understood was symmetric end to end — a resistor turned round is the same resistor.
     A diode is not, and neither is a transistor, so a part that cannot be turned to
     face the other way is a part half the circuits that need it cannot use.
     Pin count comes from the registry rather than from a list of kind names here, so a
     new kind gets its geometry by declaring how many pins it has. One pin sits on its
     cell; two span it along whichever axis rot puts them, FIRST pin trailing; the third
     — a potentiometer's wiper, a base, a gate — leaves the body at right angles, one
     cell out, which is where the arrow in the symbol points. rot 0 and 1 land exactly
     where they always did, so nothing already drawn has moved. */
  function pinsOf(p) {
    const k = PART_KINDS[p.kind];
    /* A block's pins are wherever its boundary was, and it was grouped ON that
       boundary — so a port's offset is the offset the crossing cell already had from
       the block's origin, and the pin lands back on the exact cell the wire outside
       still ends at. Grouping therefore changes no connection, and neither does
       dragging a block: the pins travel with it the way any part's do. A port can hold
       more than one cell, because a net that crossed in two places is one net. */
    if (p.kind === 'IC') {
      const out = [];
      (p.ports || []).forEach(function (port) {
        (port.cells || []).forEach(function (c) { out.push([p.x + c[0], p.y + c[1]]); });
      });
      return out;
    }
    /* A board has no pins. It has holes, and whatever is in a hole is somebody else's
       pin — which is why nothing here, and nothing in the pass that walks pins into
       the union-find, can create a node for a board. Sixty empty strips that each
       became a node would be sixty floating nodes, and the solver would rightly call
       a circuit with a board sitting beside it under-determined. The strips are joined
       further down instead, out of cells that already exist. */
    if (p.kind === 'BB') return [];
    /* A microcontroller's pins are a fixed header rather than a count in the registry,
       and they are NOT turned by rot: a body wide enough to write twelve names inside
       has no reading of "rotated" that is not just a different drawing, and a block and
       a board already answer the same way. What that costs is that the pin order on the
       canvas is the pin order in MCU_PINS, always — which is also what makes a schematic
       drawn last week still name the same pins today. */
    if (p.kind === 'MCU') {
      return MCU_PINS.map(function (d) {
        return [p.x + (d.side ? MCU_W : 0), p.y + d.row];
      });
    }
    const n = k ? k.pins : 2;
    if (n === 1) return [[p.x, p.y]];
    const r = turnsOf(p);
    const dx = [1, 0, -1, 0][r], dy = [0, 1, 0, -1][r];
    const span = [[p.x - dx, p.y - dy], [p.x + dx, p.y + dy]];
    if (n < 3) return span;
    span.push([p.x + dy, p.y - dx]);
    return span;
  }

  /* Sources need a polarity, and it has to be the one people draw. A schematic is
     read left to right and bottom to top, so the + terminal is the RIGHT pin of a
     horizontal source and the TOP pin of a vertical one. Ordering the pins that way
     here means a divider laid out with ground on the left gives a positive output,
     which is what anyone building one expects. R, C and L are symmetric and do not
     care. The editor draws the + so it is never a guess.
     Turned through half a circle the + goes with the part, as it would if you lifted a
     battery out and put it back the other way round — which is why the test is on
     whether the body is upright and not on whether rot is set. */
  function plusFirst(p) {
    const pins = pinsOf(p);
    if (p.kind !== 'V' && p.kind !== 'I') return pins;
    return (turnsOf(p) % 2) ? pins : [pins[1], pins[0]];
  }

  /* A grid point, named. The name carries WHICH drawing the point is in as well as
     where it is — see the flattener below — and an empty prefix is the top level, so
     a schematic with no blocks in it is keyed exactly as it always was. */
  function key(pt, at) { return (at || '') + pt[0] + ',' + pt[1]; }

  /* Union-find over every point touched by a wire or a pin: two points in the same
     set are electrically the same node. Handed out rather than kept private because
     the editor's grouping code has to ask the same question of the same drawing —
     which net is this pin on — and a second implementation of "connected" would sooner
     or later answer differently from this one. When it did, a block would grow a pin
     where no current flows and lose one where it does. */
  function joiner() {
    const parent = {};
    function find(a) {
      if (parent[a] === undefined) { parent[a] = a; return a; }
      while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a]; }
      return a;
    }
    function union(a, b) {
      const ra = find(a), rb = find(b);
      if (ra !== rb) parent[ra] = rb;
    }
    /* a wire is a straight run; every grid point along it joins the same node */
    function run(w, at) {
      const dx = Math.sign(w.b[0] - w.a[0]), dy = Math.sign(w.b[1] - w.a[1]);
      const n = Math.max(Math.abs(w.b[0] - w.a[0]), Math.abs(w.b[1] - w.a[1]));
      let cur = [w.a[0], w.a[1]];
      find(key(cur, at));
      for (let i = 0; i < n; i++) {
        const nxt = [cur[0] + dx, cur[1] + dy];
        union(key(cur, at), key(nxt, at));
        cur = nxt;
      }
    }
    return { parent: parent, find: find, union: union, run: run };
  }

  /* ---- what a board joins ----
   *
   * One board, one drawing, applied to a joiner that has already had every pin and
   * every wire put through it. It walks the holes and unions the ones on a strip that
   * are ALREADY on the map — a cell nothing reaches is skipped rather than created,
   * so an empty board is electrically nothing, exactly as an empty board on a desk is.
   * That single `undefined` test is the difference between a board you can leave lying
   * under a half-built circuit and a board that makes the solver refuse to answer.
   *
   * It is handed the joiner rather than owning one because the grouping code has to
   * ask the same question of the same drawing — which net is this cell on — and the
   * comment on joiner() explains what a second answer to that would cost.
   *
   * Note what is NOT special-cased: a wire lying across the board. Its run puts every
   * cell it passes through on the map, so it joins the strips it crosses, exactly as a
   * wire drawn across another wire already joins it. That is the editor's one rule for
   * what touching means, and a board is not a reason to have two of them.
   */
  function bindBoard(p, uf, at) {
    const cols = bbCols(p);
    const first = {};
    for (let c = 0; c < cols; c++) {
      for (let r = 0; r < BB_H; r++) {
        const s = bbStripAt(p, p.x + c, p.y + r);
        if (s === null) continue;
        const k = key([p.x + c, p.y + r], at);
        if (uf.parent[k] === undefined) continue;
        if (first[s] === undefined) first[s] = k; else uf.union(first[s], k);
      }
    }
  }

  /* ---- subcircuits ----
   *
   * A block is one part on the canvas and a whole schematic underneath it. The solver
   * is never told: the folding is undone HERE, before a single node is numbered, so
   * the editor, the graders and the read-only painter are all handed an ordinary flat
   * netlist and none of them has to know that blocks exist. A subcircuit only the
   * editor understood would be a circuit that grades differently from how it draws.
   *
   * Nodes cannot collide, because a grid point is addressed by a STRING and a block's
   * insides are addressed under a prefix made of the block ids standing above them.
   * "3,4" is the top level, "p7|3,4" is that cell inside block p7, and "p7|p2|3,4" is
   * inside a block inside it. A cell is named by where it is AND by which drawing it
   * is in, which is what makes two blocks holding the same schematic two circuits
   * rather than one. Nothing is renamed to avoid a clash; the names never meet.
   *
   * The interface is joined the same way, and a port's offset is what does it: read
   * against the block's position it names a cell in the PARENT drawing, and read
   * against the block's origin it names a cell INSIDE. Union those two keys and the
   * pin is wired to whatever the parent has on it — no lookup, no matching by name,
   * and nothing that can go stale when either side is edited.
   */
  const MAX_DEPTH = 8;

  function flatten(m, out, at, depth) {
    (m.parts || []).forEach(function (p) {
      out.parts.push({ p: p, at: at });
      if (p.kind !== 'IC') return;
      const inside = at + p.id + '|';
      (p.ports || []).forEach(function (port) {
        (port.cells || []).forEach(function (c) {
          out.joins.push([key([p.x + c[0], p.y + c[1]], at), key(c, inside)]);
        });
      });
      /* A depth limit, because a hand-written model can nest as deep as it likes and a
         blown stack is not a diagnosis. It is recorded rather than swallowed: a block
         whose contents were quietly dropped is a circuit missing parts that nothing on
         the screen says are missing. */
      if (depth + 1 > MAX_DEPTH) { out.tooDeep = MAX_DEPTH; return; }
      flatten(p.inner || { parts: [], wires: [] }, out, inside, depth + 1);
    });
    (m.wires || []).forEach(function (w) { out.wires.push({ w: w, at: at }); });
  }

  function build(model, env) {
    const world = Object.assign({}, ENV_DEFAULT, env || {});
    const flat = { parts: [], wires: [], joins: [], tooDeep: 0 };
    flatten(model || { parts: [], wires: [] }, flat, '', 0);
    const uf = joiner();
    const parent = uf.parent, find = uf.find, union = uf.union;

    /* A bar display is deliberately left out of this pass. Every other pin creates a
       node whether or not anything else reaches it, which is right for a part that
       carries current — but a display dropped on an empty cell would then be a node
       with nothing stamped on it, and the solver would call the whole circuit
       under-determined. A readout must never be able to break the answer it exists to
       show, so a bar takes the node it lands on and creates none. */
    flat.parts.forEach(function (e) {
      if (e.p.kind === 'BAR') return;
      pinsOf(e.p).forEach(function (pt) { find(key(pt, e.at)); });
    });
    flat.wires.forEach(function (e) { uf.run(e.w, e.at); });
    /* and last, every block's pins tied to the cells the parent drawing has them on */
    flat.joins.forEach(function (j) { find(j[0]); find(j[1]); union(j[0], j[1]); });
    /* Boards last, because a board joins cells rather than making them: everything
       that can put a cell on the map — a pin, a wire, a block's interface — has to
       have run first, or a hole would be judged empty because its occupant had not
       been looked at yet. */
    flat.parts.forEach(function (e) {
      if (e.p.kind === 'BB') bindBoard(e.p, uf, e.at);
    });

    /* ground first, so it becomes node 0 and drops out of the unknowns. A ground
       anywhere grounds everything, insides included: it is one circuit. */
    let gndRoot = null;
    flat.parts.forEach(function (e) {
      if (e.p.kind !== 'GND') return;
      const r = find(key(pinsOf(e.p)[0], e.at));
      if (gndRoot === null) gndRoot = r; else union(r, gndRoot);
    });
    if (gndRoot !== null) gndRoot = find(gndRoot);

    const nodeOf = {};
    let next = 1;
    Object.keys(parent).forEach(function (k) {
      const r = find(k);
      if (nodeOf[r] === undefined) nodeOf[r] = (r === gndRoot) ? 0 : next++;
    });

    const probes = flat.parts
      .filter(function (e) { return e.p.kind === 'OUT'; })
      .map(function (e) { return nodeOf[find(key(pinsOf(e.p)[0], e.at))]; });

    /* Everything the learner placed, in the order they placed it, with GND and OUT
       left out exactly as before — this is what `count` and `values` answer from, so
       a potentiometer that stamps as two resistors is still one potentiometer and
       not two resistors. */
    const placed = [];
    /* What the solver is given. Every entry here is an R, C, L, V or I with a plain
       number in `value`: a switch state and a sensor reading against the simulated
       environment are resolved HERE, before any stamping, and the matrix downstream
       stays linear and has no idea anything varies. */
    const parts = [];
    /* Parts that read the solution instead of taking part in it, plus the resolved
       ohms of the ones that do both, so the editor can label them without re-deriving
       any of this. */
    const readouts = [];
    /* The pin states of every microcontroller in the circuit, by id. Held on the net
       rather than on the part because it is not something the schematic saves: a
       drawing does not remember which pins were high the last time it was run, any
       more than it remembers where the light slider was. The interpreter mutates these
       records between time steps and the stamps read them; a circuit solved with no
       interpreter attached simply solves them at reset, which is the honest picture of
       a board with power and no program. */
    const mcus = {};

    flat.parts.forEach(function (e) {
      const p = e.p;
      /* Ids are prefixed exactly as cells are, so two blocks holding the same
         schematic do not share a Newton state or overwrite one another in the table of
         branch currents. At the top level the prefix is empty and an id is what it has
         always been. */
      const pid = e.at + p.id;
      if (p.kind === 'GND' || p.kind === 'OUT') return;
      if (p.kind === 'IC') {
        /* The block stamps nothing: what it holds is already in this same list, spliced
           in above. It is still counted as placed, so a check can ask how many blocks
           were built — and so counting resistors goes on counting the ones inside one,
           which is the honest answer to "how many resistors are in this circuit". */
        placed.push({ id: pid, kind: 'IC', value: 0 });
        return;
      }
      if (p.kind === 'BB') {
        /* The board is not in the circuit; the circuit is in the board. It stamps
           nothing, it owns no node, and every connection it makes is between cells
           that were already there — so it leaves this loop before anything asks it
           for pins it does not have. Counted as placed all the same, so a check can
           ask whether the learner built on one. */
        placed.push({ id: pid, kind: 'BB', value: bbCols(p) });
        return;
      }
      if (p.kind === 'MCU') {
        const rec = mcuReset(pid);
        const pins = pinsOf(p).map(function (pt) { return nodeOf[find(key(pt, e.at))]; });
        rec.pins.forEach(function (pin, i) { pin.node = pins[i]; });
        rec.gnd = pins[MCU_PINS.length - 1];
        rec.code = typeof p.code === 'string' ? p.code : MCU_SKETCH;
        mcus[pid] = rec;
        placed.push({ id: pid, kind: 'MCU', value: 0 });
        readouts.push({ id: pid, kind: 'MCU', mcu: rec });
        /* One entry, not twelve: the stamp walks the record's own pins, so the pin
           order in the matrix and the pin order on the drawing are the same list read
           twice rather than two lists kept in step. */
        parts.push({ id: pid, kind: 'MCU', mcu: rec });
        return;
      }
      if (p.kind === 'BAR') {
        /* look the node up without creating one — see the pass above */
        const kk = key(pinsOf(p)[0], e.at);
        placed.push({ id: pid, kind: p.kind, value: p.value });
        readouts.push({ id: pid, kind: 'BAR', full: p.value,
                        node: parent[kk] === undefined ? null : nodeOf[find(kk)] });
        return;
      }
      const pins = plusFirst(p).map(function (pt) { return nodeOf[find(key(pt, e.at))]; });
      placed.push({ id: pid, kind: p.kind, value: p.value });

      if (p.kind === 'POT') {
        const rr = potSplit(p);
        /* two resistances sharing the wiper node: pin A to wiper, wiper to pin B */
        parts.push({ id: pid + '#a', kind: 'R', value: rr[0], n1: pins[0], n2: pins[2], of: pid });
        parts.push({ id: pid + '#b', kind: 'R', value: rr[1], n1: pins[2], n2: pins[1], of: pid });
        readouts.push({ id: pid, kind: 'POT', nodes: pins, ohms: rr[0] + rr[1], split: rr });
        return;
      }
      /* A device the solver has to iterate on goes through unresolved: there is no one
         number to work out in advance, which is the whole difference between it and a
         thermistor. It carries its own pins rather than n1/n2, because three-terminal
         parts have three, and it takes them in the order pinsOf gives them — the two
         along the body then the control pin at right angles, the convention POT set.
         Which terminal is which is drawn on the symbol and named in the panel. */
      if (Devices.is(p.kind)) {
        const dev = Devices.build(p);
        dev.id = pid;
        dev.nodes = pins.slice(0, PART_KINDS[p.kind].pins);
        parts.push(dev);
        readouts.push({ id: pid, kind: p.kind, nodes: dev.nodes });
        return;
      }
      const ohms = ohmsOf(p, world);
      if (ohms !== null) {
        parts.push({ id: pid, kind: 'R', value: ohms, n1: pins[0], n2: pins[1], of: pid, was: p.kind });
        readouts.push({ id: pid, kind: p.kind, nodes: pins, ohms: ohms });
        return;
      }
      parts.push({ id: pid, kind: p.kind, value: p.value, n1: pins[0], n2: pins[1], ac: p.ac });
    });

    /* ---- a microcontroller nobody gave a ground to ----
     * Every one of its pins is stamped against its OWN ground pin, so an ungrounded
     * part is an island: a group of nodes with a defined set of voltage DIFFERENCES
     * and no defined voltage. That is a singular matrix and a true one — the circuit
     * really has no unique answer — but "the circuit is under-determined" sends a
     * learner looking for a floating node when what they have is a chip they forgot to
     * ground, which is a different search. The condition is exact rather than a guess:
     * the ground pin is not the circuit's ground, and nothing else in the netlist is on
     * that node either. */
    const grounded = {};
    parts.forEach(function (q) {
      if (q.kind === 'MCU') return;
      [q.n1, q.n2].concat(q.nodes || []).forEach(function (nd) {
        if (nd !== undefined) grounded[nd] = 1;
      });
    });
    const floatingMcus = Object.keys(mcus).filter(function (id) {
      return mcus[id].gnd !== 0 && !grounded[mcus[id].gnd];
    });

    return { parts: parts, probes: probes, nodeCount: next, hasGround: gndRoot !== null,
             placed: placed, readouts: readouts, env: world, tooDeep: flat.tooDeep,
             mcus: mcus, floatingMcus: floatingMcus,
             /* `at` names the drawing the point is in, so the editor can ask what node a
                cell is on while looking INSIDE a block. Left off, it means the top
                level, which is every caller that has never heard of one. */
             nodeAt: function (pt, at) {
               const k = key(pt, at);
               return parent[k] === undefined ? null : nodeOf[find(k)];
             } };
  }

  return { build: build, pinsOf: pinsOf, plusFirst: plusFirst,
           joiner: joiner, bindBoard: bindBoard, key: key, MAX_DEPTH: MAX_DEPTH };
})();

/* ---------------------------------------------------------------- MNA */
const MNA = (function () {

  /* Which parts need a current unknown of their own: voltage sources always, and
     inductors in DC (a short is a zero-volt source) and in transient. */
  function currentCarriers(parts, mode) {
    return parts.filter(function (p) {
      return p.kind === 'V' || (p.kind === 'L' && mode !== 'ac');
    });
  }

  function frame(net, mode) {
    const carriers = currentCarriers(net.parts, mode);
    const n = net.nodeCount - 1 + carriers.length;
    return { carriers: carriers, n: n, idxOf: function (p) { return net.nodeCount - 1 + carriers.indexOf(p); } };
  }

  function stampG(A, i, j, g) {
    /* i and j are node numbers; node 0 is ground and has no row */
    if (i > 0) A[i - 1][i - 1] = Lin.cadd(A[i - 1][i - 1], g);
    if (j > 0) A[j - 1][j - 1] = Lin.cadd(A[j - 1][j - 1], g);
    if (i > 0 && j > 0) {
      A[i - 1][j - 1] = Lin.csub(A[i - 1][j - 1], g);
      A[j - 1][i - 1] = Lin.csub(A[j - 1][i - 1], g);
    }
  }

  function stampCurrent(b, i, j, cur) {
    if (i > 0) b[i - 1] = Lin.csub(b[i - 1], cur);
    if (j > 0) b[j - 1] = Lin.cadd(b[j - 1], cur);
  }

  /* Every pin of one microcontroller, at whatever the sketch has left them at. Each is
     a Thevenin source between the pin and the part's ground pin, stamped as its Norton
     — see mcuNorton, which is where the numbers are and where the reasoning for them
     is. Linear in the matrix and re-read on every stamp, which is what lets an output
     change between two time steps without the solver knowing anything has happened.
     Nothing here iterates: a pin driven high is a number the sketch chose, exactly as
     a thrown switch is, and neither is a non-linearity. */
  function stampMcu(A, b, rec) {
    rec.pins.forEach(function (pin) {
      const nrt = mcuNorton(pin);
      if (!nrt) return;
      stampG(A, pin.node, rec.gnd, [nrt.g, 0]);
      if (nrt.i) stampCurrent(b, rec.gnd, pin.node, [nrt.i, 0]);
    });
  }

  function problems(net) {
    /* Asked before anything else: past the nesting limit the netlist is missing parts,
       and every answer below it would be an answer to a different circuit. Refusing is
       the only honest thing left. */
    if (net.tooDeep) {
      return 'Blocks are nested more than ' + net.tooDeep + ' deep, and everything below ' +
        'that is not in the netlist — so there is no answer to give you that would be ' +
        'about the circuit you drew. Ungroup a level and solve again.';
    }
    if (!net.hasGround) return 'No ground. Every circuit needs one, or the node voltages have nothing to be measured against.';
    if (net.floatingMcus && net.floatingMcus.length) {
      const who = net.floatingMcus.map(function (id) { return id.replace('p', 'part '); });
      return 'The GND pin of ' + who.join(' and ') + ' is not connected to anything. ' +
        'Every pin of a microcontroller is driven and read against its own GND pin, so ' +
        'without that connection the whole part floats: its pin voltages have differences ' +
        'but no values, which is a circuit with no unique answer. Wire GND to the same ' +
        'ground the rest of the circuit uses.';
    }
    if (!net.parts.length) return 'Nothing to solve yet — place some components and wire them up.';
    return null;
  }

  const UNDER_DC = 'The circuit is under-determined — usually a node connected to nothing, or two voltage sources in a loop.';
  const UNDER_TRAN = 'The circuit is under-determined.';

  /* ---- Newton-Raphson ----
   *
   * A linear circuit has one answer and one solve finds it. A circuit with a diode in
   * it has an answer that depends on itself, so it is found by successive approximation:
   * linearise every device where the last answer said it was sitting, solve, and repeat
   * until the answer stops moving. Everything below is the bookkeeping that makes that
   * loop trustworthy rather than merely convergent-looking.
   */

  /* A conductance from every node to ground. Iteration passes through states no real
     circuit is ever in — a MOSFET in cutoff has an infinite resistance from drain to
     source, and on the pass that finds it, the drain may be attached to nothing else at
     all — and a matrix row of zeros stops the whole solve on a circuit that has a
     perfectly good answer two passes later. gmin gives every node a diagonal entry so
     the pass can complete and the iteration can carry on to the answer.
     1e-12 S is a terrohm: 5 pA leaks out of a 5 V node through it, which is six orders
     below the microamps the smallest of these circuits carries and cannot move a
     printed answer, while being a hundred times the pivot threshold in Lin.solve.
     It is added ONLY when there is something non-linear to iterate on. A linear circuit
     that is singular is genuinely under-determined, and propping one up with gmin would
     turn "this circuit has no unique answer" into a number — which is the one thing this
     solver has never done. */
  const GMIN = 1e-12;

  /* When to stop, and when to give up.
     Two tolerances, because a 5 V rail and a 0.6 V junction cannot share one: a relative
     part that keeps a check on a supply node meaningful, and an absolute floor, because
     nothing is ever within a part in a million of nothing and a node sitting at zero
     would otherwise never be declared settled. Branch currents get their own floor —
     an amp and a volt are not the same size of number.
     These are tighter than SPICE's own defaults (1e-3 and 1 µV), which these circuits
     are small enough to afford, and which means a check comparing an answer to four
     figures is reading the circuit rather than the tolerance. */
  const NR_MAX = 100;
  const RELTOL = 1e-6, VNTOL = 1e-9, ABSTOL = 1e-12;

  function devicesOf(net) {
    return net.parts.filter(function (p) { return !!p.iv; });
  }
  function freshState(devs) {
    const s = {};
    devs.forEach(function (d) { s[d.id] = {}; });
    return s;
  }
  function rhs(n) {
    const b = [];
    for (let i = 0; i < n; i++) b.push([0, 0]);
    return b;
  }
  function nodeVolts(nodes, x) {
    return nodes.map(function (n) { return n > 0 && x ? x[n - 1][0] : 0; });
  }

  /* The conductance half of a device's linearisation: every terminal against every
     other. This alone is what an AC sweep wants, since a small signal rides on top of
     the operating point and asks only about the slope there. */
  function stampTangent(A, nodes, J) {
    for (let k = 0; k < nodes.length; k++) {
      if (nodes[k] <= 0) continue;
      for (let l = 0; l < nodes.length; l++) {
        if (nodes[l] <= 0 || !J[k][l]) continue;
        A[nodes[k] - 1][nodes[l] - 1] = Lin.cadd(A[nodes[k] - 1][nodes[l] - 1], [J[k][l], 0]);
      }
    }
  }

  /* The whole companion model, in six lines: the tangent as a conductance, plus a
     current source carrying everything the real curve does that the tangent does not.
     Every device in the file reduces to this, which is why none of them needs a stamp
     of its own. */
  function stampDevice(A, b, nodes, v, i, J) {
    stampTangent(A, nodes, J);
    for (let k = 0; k < nodes.length; k++) {
      const nk = nodes[k];
      if (nk <= 0) continue;
      let ieq = i[k];
      for (let l = 0; l < nodes.length; l++) ieq -= J[k][l] * v[l];
      b[nk - 1] = Lin.csub(b[nk - 1], [ieq, 0]);
    }
  }

  function settled(x, prev, nodeRows) {
    for (let i = 0; i < x.length; i++) {
      const a = x[i][0], p = prev[i][0];
      const floor = i < nodeRows ? VNTOL : ABSTOL;
      if (Math.abs(a - p) > RELTOL * Math.max(Math.abs(a), Math.abs(p)) + floor) return false;
    }
    return true;
  }
  function allFinite(x) {
    for (let i = 0; i < x.length; i++) if (!isFinite(x[i][0]) || !isFinite(x[i][1])) return false;
    return true;
  }

  /* The linearisation left standing at the settled point, kept so an AC sweep can be
     taken about it. Re-evaluated with the limiters switched off: they exist to hold a
     guess back, and this is not a guess. */
  function tangentsAt(devs, x) {
    return devs.map(function (d) {
      const vs = nodeVolts(d.nodes, x);
      return { nodes: d.nodes, j: d.iv(d, vs, { raw: true }).j };
    });
  }

  /* Say which node would not settle and by how much. "It did not converge" is true and
     useless; the node still moving is nearly always the one with the device on it. */
  function stalled(msg, x, before, nodeRows) {
    let worst = 0, at = 0;
    if (x && before) {
      for (let i = 0; i < nodeRows; i++) {
        const d = Math.abs(x[i][0] - before[i][0]);
        if (d > worst) { worst = d; at = i + 1; }
      }
    }
    return 'The iteration did not settle: ' + NR_MAX + ' passes at ' + msg.where +
      ' and the node voltages were still moving' +
      (at ? ' (node ' + at + ' by ' + fmtEng(worst, 'V') + ' on the last one)' : '') +
      '. A non-linear circuit can fail to converge because it genuinely has more than one ' +
      'operating point — a latch, or positive feedback round an op-amp — or because a ' +
      'device is being driven far outside what its model was written for. Rather than ' +
      'hand you the last guess as though it were an answer, this is the answer: it did ' +
      'not converge.';
  }
  function blewUp(msg) {
    return 'The iteration went to infinity at ' + msg.where + ' and came back as not a ' +
      'number. Something is driving a device past anything the step limiting can hold — ' +
      'a diode straight across a voltage source, with no resistance anywhere in the loop, ' +
      'is the usual one.';
  }
  /* The same failure with no device in the circuit to blame it on. A linear stamp can
     overflow all by itself: a capacitor's companion conductance is C/h, and h is the
     time step, so it runs out of double precision at a capacitance the value box was
     perfectly happy to accept. Infinity in the matrix, Infinity minus Infinity out of
     the elimination, and every node NaN. */
  function overflowed(msg) {
    return 'The arithmetic overflowed at ' + msg.where + ' and the answer came back as ' +
      'not a number. Some value in this circuit is large enough that the numbers built ' +
      'from it are past what double precision can hold — a capacitance or an inductance ' +
      'is the usual one, because the companion model divides it by the time step and so ' +
      'runs out of range long before the value itself does. Rather than hand you a plot ' +
      'of nothing, this is the answer: there is none at that value.';
  }

  /* One solve if there is nothing to iterate on, Newton if there is. `stamp` lays down
     whatever is linear about this particular analysis — DC, or one backward-Euler step —
     and knows nothing about devices; `state` carries each device's junction voltages
     between passes, and between time steps, so the limiting has a previous value to hold
     against; `guess` is where to start, which for a time step is the step before it. */
  function iterate(net, f, devs, state, stamp, guess, msg) {
    const nodeRows = net.nodeCount - 1;

    if (!devs.length) {
      const A = Lin.zeros(f.n), b = rhs(f.n);
      stamp(A, b);
      const x = Lin.solve(A, b);
      if (!x) return { error: msg.under };
      /* The same check the Newton branch below has always had, on the branch that never
         did. Lin.solve rejects a pivot too small to divide by; it has nothing to say
         about one so large that dividing by it produces NaN — `best < 1e-14` is false
         when best is NaN — so a singular circuit was caught and an overflowing one went
         straight through the test. Every one of the 376 published schematics is linear
         and takes this branch; not one of them contains a device to iterate on. So the
         guarded path was the one nobody is on and the unguarded path was all of them: a
         capacitance of 1e308 F came back as 900 non-finite samples with no error at all,
         the panel announced a finished run over 2 nodes, and the node the supply holds
         up still drew a convincing flat line beside a trace that was not there. */
      if (!allFinite(x)) return { error: overflowed(msg) };
      return { x: x };
    }

    let prev = guess || null, before = null;
    for (let pass = 1; pass <= NR_MAX; pass++) {
      const A = Lin.zeros(f.n), b = rhs(f.n);
      stamp(A, b);
      for (let i = 0; i < nodeRows; i++) A[i][i] = Lin.cadd(A[i][i], [GMIN, 0]);
      let held = false;
      devs.forEach(function (d) {
        const st = state[d.id];
        st.lim = false;
        const vs = nodeVolts(d.nodes, prev);
        const r = d.iv(d, vs, st);
        if (st.lim) held = true;
        stampDevice(A, b, d.nodes, r.v, r.i, r.j);
      });
      const x = Lin.solve(A, b);
      if (!x) return { error: msg.under };
      if (!allFinite(x)) return { error: blewUp(msg) };
      /* A pass whose device voltages were held back by a limiter has not converged
         however small its step looks: the step it took is the one the limiter allowed,
         not the one Newton asked for, and mistaking the two is how a solver reports a
         confident wrong answer. */
      if (prev && !held && settled(x, prev, nodeRows)) {
        return { x: x, passes: pass, tangents: tangentsAt(devs, x) };
      }
      before = prev;
      prev = x;
    }
    return { error: stalled(msg, prev, before, nodeRows) };
  }

  /* ---- DC operating point ---- */
  function stampDC(net, f, A, b) {
    net.parts.forEach(function (p) {
      if (p.kind === 'R') stampG(A, p.n1, p.n2, [1 / Math.max(p.value, 1e-12), 0]);
      else if (p.kind === 'I') stampCurrent(b, p.n1, p.n2, [p.value, 0]);
      else if (p.kind === 'MCU') stampMcu(A, b, p.mcu);
      else if (p.kind === 'C') { /* open circuit at DC */ }
      else if (p.kind === 'V' || p.kind === 'L') {
        const k = f.idxOf(p);
        /* an inductor is a zero-volt source at DC */
        const volts = p.kind === 'V' ? p.value : 0;
        if (p.n1 > 0) { A[p.n1 - 1][k] = Lin.cadd(A[p.n1 - 1][k], [1, 0]); A[k][p.n1 - 1] = Lin.cadd(A[k][p.n1 - 1], [1, 0]); }
        if (p.n2 > 0) { A[p.n2 - 1][k] = Lin.csub(A[p.n2 - 1][k], [1, 0]); A[k][p.n2 - 1] = Lin.csub(A[k][p.n2 - 1], [1, 0]); }
        b[k] = [volts, 0];
      }
    });
  }

  function dc(net) {
    const bad = problems(net);
    if (bad) return { error: bad };
    const f = frame(net, 'dc');
    if (f.n === 0) return { error: 'Everything is tied to ground; there is nothing to solve for.' };
    const devs = devicesOf(net);
    const r = iterate(net, f, devs, freshState(devs),
      function (A, b) { stampDC(net, f, A, b); }, null,
      { where: 'the operating point', under: UNDER_DC });
    if (r.error) return { error: r.error };
    const v = [0];
    for (let i = 0; i < net.nodeCount - 1; i++) v.push(r.x[i][0]);
    const currents = {};
    f.carriers.forEach(function (p) { currents[p.id] = r.x[f.idxOf(p)][0]; });
    return { v: v, currents: currents, passes: r.passes || 1, tangents: r.tangents || [] };
  }

  /* The operating point an AC sweep is taken about. A sweep asks what a SMALL change
     does, so for a non-linear part the answer is the slope of its curve at the point the
     circuit is actually sitting at — which means a transistor stage's gain here is the
     gain its bias gives it, and moving the bias moves the plot, exactly as it does on the
     bench. Cached on the net because finding a corner frequency asks for sixty
     frequencies and the bias does not move between any of them. */
  function bias(net) {
    if (!net.__bias) net.__bias = dc(net);
    return net.__bias;
  }

  /* ---- AC, one frequency ----
   *
   * Two entry points to one solve. acSolve says WHY it could not answer, because a
   * sweep of sixty frequencies has to put the reason on the screen; acAt keeps the
   * shape this file has always exposed — a vector, or null — because catalogue checks
   * call it directly and a check is not a place to report a cause. */
  function acSolve(net, w) {
    const devs = devicesOf(net);
    let tangents = null;
    if (devs.length) {
      const op = bias(net);
      if (op.error) return { error: 'nobias' };
      tangents = op.tangents;
    }
    const f = frame(net, 'ac');
    const A = Lin.zeros(f.n);
    const b = [];
    for (let i = 0; i < f.n; i++) b.push([0, 0]);

    if (tangents) {
      for (let i = 0; i < net.nodeCount - 1; i++) A[i][i] = Lin.cadd(A[i][i], [GMIN, 0]);
      tangents.forEach(function (t) { stampTangent(A, t.nodes, t.j); });
    }

    net.parts.forEach(function (p) {
      if (p.kind === 'R') stampG(A, p.n1, p.n2, [1 / Math.max(p.value, 1e-12), 0]);
      else if (p.kind === 'C') stampG(A, p.n1, p.n2, [0, w * p.value]);
      else if (p.kind === 'L') stampG(A, p.n1, p.n2, Lin.cdiv([1, 0], [0, w * Math.max(p.value, 1e-15)]));
      else if (p.kind === 'I') stampCurrent(b, p.n1, p.n2, [p.value, 0]);
      /* A sweep asks what a small change does, and a pin does not respond to one: it
         is a source and a resistance, both fixed for as long as the sketch leaves them
         alone. So the pins contribute their conductances and their sources here exactly
         as at DC, and the answer is the response of the circuit AROUND a part that is
         holding still — which is the only frequency response a program has. */
      else if (p.kind === 'MCU') stampMcu(A, b, p.mcu);
      else if (p.kind === 'V') {
        const k = f.idxOf(p);
        if (p.n1 > 0) { A[p.n1 - 1][k] = Lin.cadd(A[p.n1 - 1][k], [1, 0]); A[k][p.n1 - 1] = Lin.cadd(A[k][p.n1 - 1], [1, 0]); }
        if (p.n2 > 0) { A[p.n2 - 1][k] = Lin.csub(A[p.n2 - 1][k], [1, 0]); A[k][p.n2 - 1] = Lin.csub(A[k][p.n2 - 1], [1, 0]); }
        b[k] = [p.value, 0];
      }
    });

    const x = Lin.solve(A, b);
    /* Two words rather than two sentences: the caller knows the frequency and this does
       not, and a message with the frequency missing out of it is the one thing worse
       than no message. */
    if (!x) return { error: 'singular' };
    /* An admittance is wC or 1/(wL), so an enormous reactance overflows the stamp
       rather than the value — and at DC the linear path's own check does not run here,
       because an AC point is one solve and not an iteration. Same rule, said again in
       the one place that does not go through iterate(). */
    if (!allFinite(x)) return { error: 'overflow' };
    const v = [[0, 0]];
    for (let i = 0; i < net.nodeCount - 1; i++) v.push(x[i]);
    return { v: v };
  }
  function acAt(net, w) {
    const r = acSolve(net, w);
    return r.error ? null : r.v;
  }

  function ac(net, f1, f2, points) {
    const bad = problems(net);
    if (bad) return { error: bad };
    /* Two boxes clamped one at a time are not a range. From and To are held apart from
       zero and from each other on the panel, and never against ONE ANOTHER, so a sweep
       from 1 kHz to 1 kHz ran 220 points at one frequency and handed the plot a
       zero-width logarithmic axis — on which every gridline, every tick label and the
       whole curve map to NaN and are silently not drawn, under a status line saying the
       sweep had finished. A decade is not demanded; an interval is. */
    const shown = function (v) { return isFinite(v) ? fmtEng(v, 'Hz') : 'not a number'; };
    if (!(isFinite(f1) && isFinite(f2) && f1 > 0 && f2 > f1)) {
      return { error: 'That is not a frequency range. A sweep runs from a lower frequency ' +
        'to a higher one and both ends have to be above zero, because the axis is ' +
        'logarithmic and there is no room on it between a frequency and itself. From ' +
        'reads ' + shown(f1) + ' and To reads ' + shown(f2) + '.' };
    }
    if (!(points >= 2)) return { error: 'A sweep needs at least two points.' };
    /* A microcontroller counts as a source, because its Vcc pin and any driven output
       are exactly that. Leaving it out would refuse a sweep of the RC hanging off a
       PWM pin, which is the one frequency response anybody asks a board for. */
    if (!net.parts.some(function (p) {
      return p.kind === 'V' || p.kind === 'I' || p.kind === 'MCU';
    })) {
      return { error: 'No source to sweep. Add a voltage or current source.' };
    }
    /* A non-linear circuit has no frequency response until it has a bias to have one
       about, so a failure to find that bias is reported as itself rather than as a
       sweep that mysteriously would not run. */
    if (devicesOf(net).length) {
      const op = bias(net);
      if (op.error) {
        return { error: 'A sweep is taken about the DC operating point, and this circuit ' +
          'has not got one. ' + op.error };
      }
    }
    const out = [];
    for (let i = 0; i < points; i++) {
      const fq = Math.pow(10, Math.log10(f1) + i / (points - 1) * (Math.log10(f2) - Math.log10(f1)));
      const r = acSolve(net, 2 * Math.PI * fq);
      if (r.error === 'overflow') {
        return { error: 'The arithmetic overflowed at ' + fmtEng(fq, 'Hz') + ' and the ' +
          'answer came back as not a number. An admittance is wC or 1/(wL), so it is the ' +
          'frequency and the reactance TOGETHER that run out of double precision — which ' +
          'is why a sweep can overflow at its top end and be perfectly well behaved at ' +
          'its bottom one. Rather than draw a plot with a hole in it, this is the answer.' };
      }
      if (r.error) return { error: 'The circuit is under-determined at ' + fmtEng(fq, 'Hz') + '.' };
      out.push({ f: fq, v: r.v });
    }
    return { sweep: out };
  }

  /* ---- transient, backward Euler, and the one analysis a program can take part in ----
   *
   * Backward Euler rather than trapezoidal: it is unconditionally stable and never
   * rings on a step, so a learner watching an RC charge sees the physics rather than
   * an artefact of the integrator.
   *
   * `hooks` is how something outside the solver rides along with the time steps. It is
   * optional and every existing caller omits it, so a transient with no hooks is the
   * transient this file has always run.
   *
   *   hooks.begin(h)          the step length that was actually settled on
   *   hooks.after(t, volts)   every solved point, in order, including the first
   *
   * `after` is where a microcontroller reads its input pins and runs the next slice of
   * its sketch, and where whatever it writes to its output pins lands in the records
   * the next step's stamp reads. So a pin written at time t appears in the circuit at
   * t + h and not before. That is a real latency and not a rounding: it is the price of
   * co-simulating two things that each need the other's answer, and the alternative —
   * iterating the program and the matrix together to a joint fixed point — has no
   * meaning for a program, which is not a curve and has no tangent. One step of
   * latency, stated, beats a fixed point that does not exist.
   */
  function tran(net, tStop, h, hooks) {
    const bad = problems(net);
    if (bad) return { error: bad };
    const f = frame(net, 'tran');
    /* A step cap has to cost resolution, never span: clamping the count while
       keeping h shortened the simulation instead of coarsening it, so a run asked to
       cover five time constants quietly stopped at two and the curve looked as if it
       had settled somewhere it had not. */
    const MAX_STEPS = 4000;
    let steps = Math.max(2, Math.round(tStop / h));
    if (steps > MAX_STEPS) { h = tStop / MAX_STEPS; steps = MAX_STEPS; }
    const prevV = {};
    const prevI = {};
    net.parts.forEach(function (p) { prevV[p.id] = 0; prevI[p.id] = 0; });

    const devs = devicesOf(net);
    const state = freshState(devs);
    const msg = { where: 'a time step', under: UNDER_TRAN };

    /* one backward-Euler step, of whatever length is asked for */
    function stampStep(hh) {
      return function (A, b) {
        net.parts.forEach(function (p) {
          if (p.kind === 'R') stampG(A, p.n1, p.n2, [1 / Math.max(p.value, 1e-12), 0]);
          else if (p.kind === 'C') {
            /* companion: conductance C/h with a current source carrying the history */
            const g = Math.max(p.value, 1e-18) / hh;
            stampG(A, p.n1, p.n2, [g, 0]);
            stampCurrent(b, p.n1, p.n2, [-g * prevV[p.id], 0]);
          } else if (p.kind === 'I') stampCurrent(b, p.n1, p.n2, [p.value, 0]);
          /* Read fresh on every stamp, and therefore fresh on every Newton pass and
             every step: whatever the sketch left in `drive` between the last step and
             this one is what the matrix is built from. This one line is the entire
             mechanism by which a program reaches the circuit. */
          else if (p.kind === 'MCU') stampMcu(A, b, p.mcu);
          else if (p.kind === 'V' || p.kind === 'L') {
            const k = f.idxOf(p);
            if (p.n1 > 0) { A[p.n1 - 1][k] = Lin.cadd(A[p.n1 - 1][k], [1, 0]); A[k][p.n1 - 1] = Lin.cadd(A[k][p.n1 - 1], [1, 0]); }
            if (p.n2 > 0) { A[p.n2 - 1][k] = Lin.csub(A[p.n2 - 1][k], [1, 0]); A[k][p.n2 - 1] = Lin.csub(A[k][p.n2 - 1], [1, 0]); }
            if (p.kind === 'V') {
              b[k] = [p.value, 0];
            } else {
              /* inductor companion: v = (L/h)(i - i_prev) */
              const Lh = Math.max(p.value, 1e-15) / hh;
              A[k][k] = Lin.csub(A[k][k], [Lh, 0]);
              b[k] = [-Lh * prevI[p.id], 0];
            }
          }
        });
      };
    }

    const times = [], volts = [];
    /* The initial condition, before any step. Backward Euler solves for the state at
       the *end* of a step, so without this the first sample already shows one step of
       charging and an RC curve appears not to start at zero. */
    const v0 = [];
    for (let i = 0; i < net.nodeCount; i++) v0.push(0);
    let guess = null;
    /* A microcontroller makes the first instant unwritable for the same reason a diode
       does: the node its Vcc pin holds up is not a source's own node, and the node an
       output drives is behind 25 Ω. So a circuit with one is solved for its first
       sample rather than assumed, by the same short-step trick below. Every transient
       without one takes the path it always took. */
    const solveFirst = devs.length ||
      net.parts.some(function (p) { return p.kind === 'MCU'; });
    if (solveFirst) {
      /* A non-linear circuit's first sample cannot be written down the way a linear
         one's can, because the node a source drives is not the node the source is at
         once there is a diode in between. So it is solved — by the same backward-Euler
         stamp taken over a step short enough that no capacitor charges and no inductor
         builds current, which leaves every reactance at its initial condition and asks
         only what the resistive part of the circuit does at the instant the supply
         arrives. The linear path keeps the sample it has always written: a hundred and
         fifty published transients start at it. */
      const first = iterate(net, f, devs, state, stampStep(h * 1e-6), null,
        { where: 'the first instant', under: UNDER_TRAN });
      if (first.error) return { error: first.error };
      for (let i = 0; i < net.nodeCount - 1; i++) v0[i + 1] = first.x[i][0];
      guess = first.x;
    } else {
      net.parts.forEach(function (p) {
        if (p.kind === 'V') { if (p.n1 > 0) v0[p.n1] = p.value; }
      });
    }
    times.push(0);
    volts.push(v0);
    if (hooks && hooks.begin) hooks.begin(h);
    /* The sketch sees the instant the power arrives before it sees anything else,
       which is where setup() belongs. */
    if (hooks && hooks.after) hooks.after(0, v0);

    const step = stampStep(h);
    for (let s = 1; s <= steps; s++) {
      /* the step before is where this one starts looking, which is why a transient
         costs two or three passes a point rather than the dozen a cold start costs */
      const r = iterate(net, f, devs, state, step, guess, msg);
      if (r.error) return { error: r.error };
      const x = r.x;
      guess = x;
      const v = [0];
      for (let i = 0; i < net.nodeCount - 1; i++) v.push(x[i][0]);
      times.push(s * h);
      volts.push(v);

      net.parts.forEach(function (p) {
        if (p.kind === 'C') prevV[p.id] = v[p.n1] - v[p.n2];
        if (p.kind === 'L') prevI[p.id] = x[f.idxOf(p)][0];
      });
      /* After the history, so anything a hook does to a pin belongs to the NEXT step
         and cannot retroactively change the step just solved. */
      if (hooks && hooks.after) hooks.after(s * h, v);
      /* A sketch that has faulted has nothing further to say, and the circuit after it
         is a circuit frozen at whatever its pins were left at — true, and not what the
         learner is looking at the plot to find out. Stopping here and returning the run
         so far lets the panel show the fault beside the part of the trace that led to
         it. */
      if (hooks && hooks.stop && hooks.stop()) break;
    }
    /* h may have been coarsened above, so report the one actually used */
    return { t: times, v: volts, h: h };
  }

  return { dc: dc, ac: ac, tran: tran, acAt: acAt, stampMcu: stampMcu };
})();

/* ---------------------------------------------------------------- program and circuit
 *
 * The join. Above this line nothing knows what a sketch is: the solver has a record of
 * pin states and stamps it. Below this line nothing knows what a matrix is: the
 * interpreter has twelve pins and asks them questions. This is the twenty lines in
 * between, and keeping it this thin is what stops either half from growing an opinion
 * about the other.
 *
 * The interpreter is in src/mcu.js and is NOT part of this file. It is reached through
 * a typeof guard, the way the app reaches its notepad — a build without that file is a
 * build where a microcontroller is a part you can draw and cannot run, and the panel
 * says exactly that rather than throwing. Every other analysis in this file goes on
 * working either way, which is the property that guard is protecting.
 */
function mcuAvailable() { return typeof MCU !== 'undefined' && !!MCU; }

/* One part's pins, dressed as the board an interpreter expects. The voltages come from
   `ref`, which the transient refills at every solved point — read through the object
   rather than captured, because the array is a new one each step. */
function mcuBoard(rec, ref) {
  const byN = {};
  rec.pins.forEach(function (p) { if (p.n !== null) byN[p.n] = p; });
  const adcs = rec.pins.filter(function (p) { return p.adc; })
    .map(function (p) { return p.name; }).join(', ');
  const all = rec.pins.filter(function (p) { return p.n !== null; })
    .map(function (p) { return p.name; }).join(', ');
  /* Always against the part's OWN ground pin, never against node 0 — the same rule the
     stamps follow, and it has to be the same rule or the sketch would read a pin
     against one reference while the solver drove it against another. */
  function volts(p) {
    const v = ref.v;
    if (!v) return 0;
    return (v[p.node] || 0) - (v[rec.gnd] || 0);
  }
  return {
    pinName: function (n) { return byN[n] ? byN[n].name : null; },
    pinList: function () { return all; },
    adcList: function () { return adcs; },
    mode: function (n) { return byN[n].mode; },
    setMode: function (n, m) {
      byN[n].mode = m;
      /* Leaving OUTPUT drops whatever was being driven. A pin that kept its old drive
         while claiming to be an input would go on holding a node up through 25 Ω with
         nothing on screen saying so. */
      if (m !== 'out') byN[n].drive = 0;
    },
    drive: function (n, d) { byN[n].drive = Math.min(Math.max(d, 0), 1); },
    readDigital: function (n) { return mcuLevel(byN[n], volts(byN[n])); },
    readAnalog: function (n) {
      const p = byN[n];
      if (!p.adc) return null;
      /* Vcc is the reference, which is why the count is a fraction of the supply and
         not a voltage: 512 means half of whatever Vcc is, and a sketch that wants volts
         has to multiply by it. That is the ratiometric reading a real ADC gives, and
         the source of the classic surprise when the supply sags. */
      const frac = volts(p) / MCU_VCC;
      return Math.min(Math.max(Math.round(frac * MCU_ADC_MAX), 0), MCU_ADC_MAX);
    },
  };
}

/* Everything needed to co-simulate one netlist's microcontrollers: a compiled machine
   per part, and the hooks MNA.tran calls. Returns null when there is nothing to run, so
   every circuit without one takes the path it always took. */
function mcuRig(net) {
  const ids = Object.keys((net && net.mcus) || {});
  if (!ids.length) return null;
  if (!mcuAvailable()) return { ids: ids, missing: true, rigs: [] };

  const ref = { v: null };
  let ops = 1;
  const rigs = ids.map(function (id) {
    const rec = net.mcus[id];
    const c = MCU.compile(rec.code);
    if (c.error) return { id: id, rec: rec, error: c.error };
    return { id: id, rec: rec, machine: MCU.machine(c.program, mcuBoard(rec, ref)) };
  });
  const live = rigs.filter(function (r) { return r.machine; });

  return {
    ids: ids, rigs: rigs, missing: false,
    /* True the moment any sketch faults, which is what stops the transient: see the
       note at the `hooks.stop` call. A sketch that failed to compile does not stop
       anything — there was never a run to stop, and the other parts are still running. */
    faulted: function () {
      return live.some(function (r) { return !!r.machine.state().fault; });
    },
    hooks: {
      begin: function (h) { ops = MCU.opsFor(h); },
      after: function (t, v) {
        ref.v = v;
        live.forEach(function (r) { r.machine.advance(t, ops); });
      },
      stop: function () {
        return live.some(function (r) { return !!r.machine.state().fault; });
      },
    },
    /* How many instructions a step is worth, for the panel to quote. Zero until begin
       has been called, because before a run there is no step length to answer about. */
    ops: function () { return ops; },
  };
}

/* ---------------------------------------------------------------- symbols
 *
 * The schematic editor draws parts small, rotated, and only for the kinds the solver
 * understands. A drill needs the opposite: one symbol, large, centred, and a
 * vocabulary wider than the solver's — a learner has to recognise a transistor long
 * before anything here can simulate one.
 *
 * So this is a separate table on purpose. Adding a symbol here teaches it; it does
 * not claim the solver can do anything with it.
 */
/* ---- ANSI or IEC ----
 *
 * The zigzag resistor is a North American convention. IEC 60617 — the standard behind
 * every schematic printed in Europe, and what anyone taught outside the US will have
 * in their hand — draws a plain rectangle. The same split runs through the whole
 * resistor family: a photoresistor, a thermistor and a potentiometer are all a
 * resistor body with something done to it, so all four move together or none of them
 * should.
 *
 * One module-level setting rather than a parameter threaded through forty drawing
 * calls, because there is exactly one answer per reader and it does not vary by
 * canvas. The profile writes it; every drawing in the app reads it.
 *
 * IEC is the default because it is what this app is being built for, and a default
 * nobody has to go and find beats a setting that is technically available.
 */
let SYM_STYLE = 'iec';
function symbolStyle(s) {
  if (s !== undefined) SYM_STYLE = (s === 'ansi') ? 'ansi' : 'iec';
  return SYM_STYLE;
}

/* The body of the resistor family, between x0 and x1, h being the half-height of the
   IEC rectangle. The zigzag reaches half again as far, which is what keeps the two
   conventions the same visual weight at the same size. The path arrives at (x0, 0) and
   leaves the caller to continue from (x1, 0) — true of both, so a caller does not have
   to know which one it drew. */
function resistorBody(c, x0, x1, h) {
  if (SYM_STYLE === 'iec') {
    c.moveTo(x0, -h); c.lineTo(x1, -h); c.lineTo(x1, h); c.lineTo(x0, h); c.closePath();
    return;
  }
  const n = 6, w = (x1 - x0) / n, a = h * 1.5;
  c.moveTo(x0, 0);
  for (let i = 0; i < n; i++) c.lineTo(x0 + (i + 0.5) * w, i % 2 ? a : -a);
  c.lineTo(x1, 0);
}

const Symbols = (function () {
  const DEF = {};
  function define(id, name, draw) { DEF[id] = { id: id, name: name, draw: draw }; }
  function get(id) { return DEF[id] || null; }
  function ids() { return Object.keys(DEF); }

  /* Every draw() works in a box from (-60,-40) to (60,40); the caller scales. */
  define('R', 'Resistor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-30, 0);
    resistorBody(c, -30, 30, 11);
    c.moveTo(30, 0); c.lineTo(60, 0);
  });

  /* The rest of the resistor family, and the parts that had no symbol at all. Each is
     the drawing the editor was already making on its own canvas, at the registry's
     scale — one drawing per part, so a palette icon and the thing it places cannot
     come to disagree. */
  define('LDR', 'Photoresistor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-30, 0);
    resistorBody(c, -30, 30, 11);
    c.moveTo(30, 0); c.lineTo(60, 0);
    /* light arriving: the arrows point IN, where an LED's point away */
    for (const ax of [-18, 4]) {
      c.moveTo(ax - 20, -46); c.lineTo(ax, -26);
      c.moveTo(ax, -26); c.lineTo(ax - 11, -29);
      c.moveTo(ax, -26); c.lineTo(ax - 3, -37);
    }
  });

  define('NTC', 'Thermistor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-30, 0);
    resistorBody(c, -30, 30, 11);
    c.moveTo(30, 0); c.lineTo(60, 0);
    c.moveTo(-36, 26); c.lineTo(-25, 26); c.lineTo(30, -26);
  });

  define('POT', 'Potentiometer', function (c) {
    c.moveTo(-60, 0); c.lineTo(-30, 0);
    resistorBody(c, -30, 30, 11);
    c.moveTo(30, 0); c.lineTo(60, 0);
    c.moveTo(0, -40); c.lineTo(0, -22);
    c.moveTo(-8, -30); c.lineTo(0, -21); c.lineTo(8, -30);
  });

  define('LAMP', 'Lamp', function (c) {
    c.moveTo(-60, 0); c.lineTo(-24, 0);
    c.moveTo(24, 0); c.lineTo(60, 0);
    c.moveTo(24, 0); c.arc(0, 0, 24, 0, Math.PI * 2);
    c.moveTo(-17, -17); c.lineTo(17, 17);
    c.moveTo(-17, 17); c.lineTo(17, -17);
  });

  define('METER', 'Ammeter', function (c) {
    c.moveTo(-60, 0); c.lineTo(-24, 0);
    c.moveTo(24, 0); c.lineTo(60, 0);
    c.moveTo(24, 0); c.arc(0, 0, 24, 0, Math.PI * 2);
    /* the A, drawn rather than typed, so it turns with the symbol */
    c.moveTo(-10, 11); c.lineTo(0, -12); c.lineTo(10, 11);
    c.moveTo(-5.5, 0); c.lineTo(5.5, 0);
  });

  define('BAR', 'Bar display', function (c) {
    c.moveTo(0, -40); c.lineTo(0, -26);
    c.moveTo(-30, -26); c.lineTo(30, -26); c.lineTo(30, 26);
    c.lineTo(-30, 26); c.closePath();
    for (let i = 0; i < 4; i++) {
      c.moveTo(-22 + i * 13, -16); c.lineTo(-22 + i * 13, 16);
    }
  });

  define('OUT', 'Test point', function (c) {
    c.moveTo(0, 40); c.lineTo(0, 8);
    c.moveTo(0, 8); c.arc(0, 0, 8, Math.PI / 2, Math.PI * 2.5);
    c.moveTo(-22, -22); c.lineTo(22, -22);
  });

  define('BB', 'Breadboard', function (c) {
    c.moveTo(-56, -34); c.lineTo(56, -34); c.lineTo(56, 34);
    c.lineTo(-56, 34); c.closePath();
    c.moveTo(-56, 0); c.lineTo(56, 0);
    for (let i = 0; i < 7; i++) {
      const x = -42 + i * 14;
      c.moveTo(x, -22); c.lineTo(x, -12);
      c.moveTo(x, 12); c.lineTo(x, 22);
    }
  });

  define('MCU', 'Microcontroller', function (c) {
    c.moveTo(-34, -34); c.lineTo(34, -34); c.lineTo(34, 34);
    c.lineTo(-34, 34); c.closePath();
    for (let i = 0; i < 4; i++) {
      const y = -21 + i * 14;
      c.moveTo(-34, y); c.lineTo(-56, y);
      c.moveTo(34, y); c.lineTo(56, y);
    }
    c.moveTo(-34, -20); c.arc(-34, -34, 14, Math.PI / 2, 0, true);
  });

  define('C', 'Capacitor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-9, 0);
    c.moveTo(9, 0); c.lineTo(60, 0);
    c.moveTo(-9, -26); c.lineTo(-9, 26);
    c.moveTo(9, -26); c.lineTo(9, 26);
  });

  define('L', 'Inductor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-32, 0);
    for (let i = 0; i < 4; i++) c.arc(-32 + 8 + i * 16, 0, 8, Math.PI, 0, false);
    c.lineTo(60, 0);
  });

  define('D', 'Diode', function (c) {
    c.moveTo(-60, 0); c.lineTo(-16, 0);
    c.moveTo(-16, -20); c.lineTo(-16, 20); c.lineTo(18, 0); c.closePath();
    c.moveTo(18, -20); c.lineTo(18, 20);
    c.moveTo(18, 0); c.lineTo(60, 0);
  });

  define('LED', 'LED', function (c) {
    c.moveTo(-60, 0); c.lineTo(-16, 0);
    c.moveTo(-16, -20); c.lineTo(-16, 20); c.lineTo(18, 0); c.closePath();
    c.moveTo(18, -20); c.lineTo(18, 20);
    c.moveTo(18, 0); c.lineTo(60, 0);
    /* the two arrows that separate an LED from an ordinary diode */
    for (const dx of [0, 15]) {
      c.moveTo(2 + dx, -26); c.lineTo(16 + dx, -40);
      c.moveTo(16 + dx, -40); c.lineTo(9 + dx, -38);
      c.moveTo(16 + dx, -40); c.lineTo(14 + dx, -33);
    }
  });

  define('GND', 'Ground', function (c) {
    c.moveTo(0, -30); c.lineTo(0, 0);
    c.moveTo(-34, 0); c.lineTo(34, 0);
    c.moveTo(-21, 13); c.lineTo(21, 13);
    c.moveTo(-9, 26); c.lineTo(9, 26);
  });

  define('V', 'Voltage source', function (c) {
    c.arc(0, 0, 30, 0, Math.PI * 2);
    c.moveTo(-60, 0); c.lineTo(-30, 0);
    c.moveTo(30, 0); c.lineTo(60, 0);
    c.moveTo(-15, -9); c.lineTo(-3, -9);
    c.moveTo(-9, -15); c.lineTo(-9, -3);
    c.moveTo(3, -9); c.lineTo(15, -9);
  });

  define('BATT', 'Battery', function (c) {
    c.moveTo(-60, 0); c.lineTo(-18, 0);
    c.moveTo(-18, -26); c.lineTo(-18, 26);
    c.moveTo(-6, -13); c.lineTo(-6, 13);
    c.moveTo(6, -26); c.lineTo(6, 26);
    c.moveTo(18, -13); c.lineTo(18, 13);
    c.moveTo(18, 0); c.lineTo(60, 0);
  });

  define('I', 'Current source', function (c) {
    c.arc(0, 0, 30, 0, Math.PI * 2);
    c.moveTo(-60, 0); c.lineTo(-30, 0);
    c.moveTo(30, 0); c.lineTo(60, 0);
    c.moveTo(0, 16); c.lineTo(0, -16);
    c.moveTo(-7, -8); c.lineTo(0, -17); c.lineTo(7, -8);
  });

  define('NPN', 'NPN transistor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-14, 0);          /* base lead */
    c.moveTo(-14, -28); c.lineTo(-14, 28);       /* base bar */
    c.moveTo(-14, -14); c.lineTo(22, -34);       /* collector */
    c.lineTo(22, -60);
    c.moveTo(-14, 14); c.lineTo(22, 34);         /* emitter */
    c.lineTo(22, 60);
    /* the emitter arrow, pointing out — this is what makes it NPN */
    c.moveTo(9, 20); c.lineTo(22, 34); c.lineTo(7, 31);
  });

  define('PNP', 'PNP transistor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-14, 0);
    c.moveTo(-14, -28); c.lineTo(-14, 28);
    c.moveTo(-14, -14); c.lineTo(22, -34);
    c.lineTo(22, -60);
    c.moveTo(-14, 14); c.lineTo(22, 34);
    c.lineTo(22, 60);
    /* the arrow points IN at the base, which is the whole difference */
    c.moveTo(-1, 8); c.lineTo(-14, 14); c.lineTo(-3, 22);
  });

  /* The two MOSFETs share every line but the body arrow, and they share the lead
     geometry of the bipolars above — control lead out to (-60, 0), the other two to
     (22, ∓60) — because the editor lands all four on their pins with one transform.
     A symbol drawn to a different geometry would still draw; it would just stop
     meeting its own wires. */
  function fet(c, into) {
    c.moveTo(-60, 0); c.lineTo(-24, 0);          /* gate lead */
    c.moveTo(-24, -30); c.lineTo(-24, 30);       /* gate plate, off the channel */
    /* the channel in three pieces: an enhancement device has no channel until the gate
       makes one, and the two gaps are how the symbol says so */
    c.moveTo(-12, -30); c.lineTo(-12, -14);
    c.moveTo(-12, -7); c.lineTo(-12, 7);
    c.moveTo(-12, 14); c.lineTo(-12, 30);
    c.moveTo(-12, -22); c.lineTo(22, -22); c.lineTo(22, -60);   /* drain */
    c.moveTo(-12, 22); c.lineTo(22, 22); c.lineTo(22, 60);      /* source */
    c.moveTo(-12, 0); c.lineTo(22, 0); c.lineTo(22, 22);        /* body, tied to source */
    /* the body arrow: in at the channel for N, out of it for P */
    if (into) { c.moveTo(-1, -6); c.lineTo(-12, 0); c.lineTo(-1, 6); }
    else { c.moveTo(-11, -6); c.lineTo(0, 0); c.lineTo(-11, 6); }
  }
  define('NMOS', 'N-channel MOSFET', function (c) { fet(c, true); });
  define('PMOS', 'P-channel MOSFET', function (c) { fet(c, false); });

  define('SW', 'Switch', function (c) {
    c.moveTo(-60, 0); c.lineTo(-24, 0);
    c.moveTo(-24, 0); c.lineTo(20, -24);
    c.moveTo(24, 0); c.lineTo(60, 0);
    c.arc(-24, 0, 4, 0, Math.PI * 2);
    c.moveTo(28, 0); c.arc(24, 0, 4, 0, Math.PI * 2);
  });

  define('OPAMP', 'Op-amp', function (c) {
    c.moveTo(-26, -38); c.lineTo(-26, 38); c.lineTo(34, 0); c.closePath();
    c.moveTo(-60, -19); c.lineTo(-26, -19);
    c.moveTo(-60, 19); c.lineTo(-26, 19);
    c.moveTo(34, 0); c.lineTo(60, 0);
    c.moveTo(-21, -24); c.lineTo(-9, -24);      /* + */
    c.moveTo(-15, -30); c.lineTo(-15, -18);
    c.moveTo(-21, 24); c.lineTo(-9, 24);        /* - */
  });

  /* Paint one symbol into a canvas, sized to it and centred. */
  function paint(canvas, id, colour) {
    const spec = DEF[id];
    if (!canvas || !spec) return;
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth || 200, h = canvas.clientHeight || 130;
    canvas.width = Math.round(w * dpr);
    canvas.height = Math.round(h * dpr);
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    const scale = Math.min(w / 150, h / 110);
    ctx.save();
    ctx.translate(w / 2, h / 2);
    ctx.scale(scale, scale);
    ctx.strokeStyle = colour || '#EDEFF3';
    ctx.lineWidth = 3.4 / scale * Math.max(scale, 0.6);
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.beginPath();
    spec.draw(ctx);
    ctx.stroke();
    ctx.restore();
  }

  return { define: define, get: get, ids: ids, paint: paint, all: DEF };
})();

/* ---------------------------------------------------------------- editor
 *
 * A schematic canvas: pick a part, click to place it, drag to wire. Everything is
 * on a grid so a pin either meets a wire or it does not — no near-misses, and no
 * hunting for the one connection that was two pixels out.
 *
 * And on a grid, so a caret can be moved along it: every gesture below has a key
 * that does the same thing, because 80 circuit exercises are graded work and a
 * graded unit no keyboard can reach is a unit some learners cannot sit.
 */

/* Attribute-safe text, for the markup the palette builds before any editor exists.
   createCircuit has its own copy under the same job; this one is out here because the
   tables above are module-level and cannot reach into a function scope. */
function cktEsc(t) {
  return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
}

/* ---- the palette ----
 *
 * Each entry is [kind, name, shortcut, description]. The name is what a screen reader
 * gets and what sits under the icon; the description is the hover text and carries the
 * one thing about the part that is worth knowing before you place it.
 *
 * Shortcuts are plain letters, which is what the hand expects and what every drawing
 * program uses. That cost rotate, group and ungroup their bare `R`, `G` and `U` — they
 * moved to Shift — because a resistor is placed a hundred times in a session and a
 * block is grouped twice, and the commoner action should have the cheaper key. A
 * modifier was not an option in the other direction: Ctrl+R reloads the page.
 */
const BAR_TOOLS = [
  ['select', 'Select', 'S', 'Select, move and rotate what is already on the canvas'],
  ['wire', 'Wire', 'W', 'Draw a wire — or just drag from any terminal, which needs no tool at all'],
];

const PART_CATS = [
  { name: 'Passive', hint: 'Resistors, capacitors, inductors', parts: [
    ['R', 'Resistor', 'R', 'Resistor'],
    ['C', 'Capacitor', 'C', 'Capacitor'],
    ['L', 'Inductor', 'L', 'Inductor'],
    ['POT', 'Potentiometer', '', 'Potentiometer — three pins, a wiper along the track'],
  ] },
  { name: 'Sources', hint: 'Supplies, ground and probes', parts: [
    ['V', 'Voltage source', 'V', 'Voltage source'],
    ['I', 'Current source', 'I', 'Current source'],
    ['GND', 'Ground', 'G', 'Ground — the node every voltage is measured against'],
    ['OUT', 'Test point', 'P', 'Mark the output node'],
  ] },
  { name: 'Switching', hint: 'Switches and sensors', parts: [
    ['SW', 'Switch', 'K', 'Switch — click it on the canvas to open and close it'],
    ['LDR', 'Photoresistor', '', 'Light sensor — resistance falls as light rises'],
    ['NTC', 'Thermistor', '', 'Thermistor — resistance falls as temperature rises'],
  ] },
  { name: 'Semiconductors', hint: 'Diodes, transistors, op-amps', parts: [
    ['D', 'Diode', 'D', 'Diode — Shockley, solved by iteration rather than by a 0.7 V rule'],
    ['LED', 'LED', 'E', 'LED — the same junction, and it lights when it conducts'],
    ['NPN', 'NPN transistor', 'Q', 'NPN bipolar — Ebers-Moll'],
    ['PNP', 'PNP transistor', '⇧Q', 'PNP bipolar — Ebers-Moll'],
    ['NMOS', 'N-channel MOSFET', 'M', 'N-channel MOSFET — level 1 square law'],
    ['PMOS', 'P-channel MOSFET', '⇧M', 'P-channel MOSFET — level 1 square law'],
    ['OPAMP', 'Op-amp', 'O', 'Op-amp — finite gain, output limited to its rails'],
  ] },
  { name: 'Readouts', hint: 'Parts that show you a number', parts: [
    ['LAMP', 'Lamp', '', 'Indicator lamp — a resistance that lights with the power in it'],
    ['METER', 'Ammeter', '', 'Ammeter — reads the current through it'],
    ['BAR', 'Bar display', '', 'Bar display — reads the node it sits on'],
  ] },
  { name: 'Boards', hint: 'Breadboard and microcontroller', parts: [
    ['BB', 'Breadboard', 'B', 'Breadboard — a strip of five holes is already one node, with no wire drawn'],
    ['MCU', 'Microcontroller', 'U', 'Microcontroller — twelve pins and a sketch you write; run it with a transient'],
  ] },
];

/* kind -> shortcut, and the reverse, built from the one table above so a key and the
   caption that advertises it cannot disagree. */
const PART_KEYS = (function () {
  const byKey = {};
  BAR_TOOLS.concat.apply(BAR_TOOLS, PART_CATS.map(function (c) { return c.parts; }))
    .forEach(function (t) {
      if (!t[2]) return;
      /* the cap reads ⇧Q because "Shift+Q" does not fit in a tile corner; the
         handler asks for "shift+q", so the two are reconciled here rather than by
         keeping a second table that can drift */
      byKey[t[2].replace('⇧', 'shift+').toLowerCase()] = t[0];
    });
  return byKey;
})();

function toolBtn(t) {
  return '<button class="ckt-t ckt-bare" data-tool="' + t[0] + '" title="' + cktEsc(t[3]) +
    ' (' + t[2] + ')" aria-label="' + cktEsc(t[1]) + '" aria-keyshortcuts="' + t[2] +
    '" aria-pressed="false">' + cktEsc(t[1]) + '</button>';
}

function partBtn(t) {
  /* The icon is painted from the symbol registry after mount, so it is the same
     drawing the canvas will make — including which convention the reader has chosen.
     A picture of an ANSI resistor on the button that places an IEC one would be worse
     than no picture. */
  return '<button class="ckt-p" data-tool="' + t[0] + '" title="' + cktEsc(t[3]) +
    (t[2] ? ' (' + t[2] + ')' : '') + '" aria-label="' + cktEsc(t[1]) +
    '" aria-pressed="false">' +
    '<canvas class="ckt-ico" data-sym="' + t[0] + '" aria-hidden="true"></canvas>' +
    '<span class="ckt-pl"><span class="ckt-pn">' + cktEsc(t[1]) + '</span>' +
    (t[2] ? '<kbd class="ckt-kb">' + cktEsc(t[2]) + '</kbd>' : '') + '</span>' +
    '</button>';
}

/* One counter for every editor ever mounted, so `aria-describedby` and the ids it
   points at cannot collide when a lesson shows a diagram beside an editor. */
let cktUid = 0;

function createCircuit(root, opts) {
  opts = opts || {};
  const GRID = 26;
  /* Two separate jobs, in this order. The sanitiser makes the drawing one this file can
     survive; the deep copy makes editing it stop short of a lesson's own `start`. The
     sanitiser has to run FIRST and on the raw object: JSON.stringify turns NaN into
     null, and null is a value Number() reads as ZERO, so copying first would convert
     "this part has no position" into "this part is at the origin" before anything got
     the chance to reject it. */
  const model = JSON.parse(JSON.stringify(sanitiseDrawing(opts.model, 0)));
  /* One counter for the whole tree, not one per drawing. Ids inside a block are
     prefixed before they reach the solver and need only be unique among their own
     siblings, but ungrouping tips a block's contents out among the parent's — and two
     parts called p3 in one drawing is a selection that cannot be told apart. Handing
     out a number nothing anywhere is using costs nothing and removes the question. */
  let seq = 0;
  (function scan(m) {
    (m.parts || []).forEach(function (p) {
      const mm = /^p(\d+)$/.exec(p.id);
      if (mm) seq = Math.max(seq, +mm[1] + 1);
      if (p.inner) scan(p.inner);
    });
  })(model);

  /* Which drawing the canvas is showing. `model` stays the whole circuit — it is what
     is saved, what is graded and what is solved, whatever is on screen — and `cur` is
     the one whose parts the pointer edits, which is `model` until a block is opened.
     `path` is the blocks between the two: the breadcrumb draws it, and the netlist is
     addressed through it. Inner drawings are nested inside the root by reference, so
     editing `cur` edits the circuit and there is nothing to write back. */
  let path = [];
  let cur = model;

  /* Select, not resistor. Opening a drawing tool in a placing mode means the first
     click anywhere drops a part nobody asked for. */
  let tool = 'select';
  /* The viewport. `s` is the zoom, `px`/`py` are the world-pixel coordinates of the
     top-left corner of what you can see. Every screen<->grid conversion goes through
     it, so there is one place that knows where things are. */
  let view = { s: 1, px: 0, py: 0 };
  let selIds = new Set();      /* selected part ids */
  let drag = null;             /* a move in progress */
  let marquee = null;          /* a rubber-band selection in progress */
  let panFrom = null;          /* a pan in progress */
  let wireFrom = null;         /* grid point a wire is being drawn from */
  let wireDown = null;         /* the press that started it, for drag-vs-click */
  let hoverConn = null;        /* the terminal under the pointer, if any */
  const selWires = new Set();  /* selected wires, by endpoint key */
  let hover = null;
  let hoverSp = null;          /* the pointer in screen pixels, for the hover card */
  /* Where the keyboard is on the grid, and whether the canvas holds focus. Declared up
     here with the rest of the editor's state rather than beside the key handlers,
     because paint() reads both and a read-only diagram paints and returns long before
     the handlers are reached — a `let` further down would be in its temporal dead zone
     and every schematic in the catalogue would throw on first draw. */
  let caret = null;
  let cvFocused = false;
  /* Drawn only once a key has been pressed. A click leaves the caret where it landed so
     the keyboard picks up from there, but it does not put a ring on the drawing: a mouse
     user who has never touched an arrow key should see the canvas they saw before. */
  let caretByKey = false;
  let analysis = { mode: 'dc', node: 1, f1: 10, f2: 1e6, tstop: 5e-3 };
  let result = null;
  /* The machines the last transient ran, kept only so the panel can show what they
     printed and where they stopped. Cleared by changed() with everything else: a
     console belonging to a circuit that has since been edited is a console about a
     circuit that no longer exists. */
  let mcuRun = null;
  let disposed = false;

  /* A question that shows a circuit wants the drawing and nothing else — no tools,
     no analysis panel, nothing to click. Same painter, so a diagram can never drift
     from what the editor would show for the same model. */
  const uid = 'ckt' + (cktUid++);
  if (opts.readOnly) {
    /* A diagram is a picture and is labelled as one. role=img with a name is what
       stops a screen reader announcing a bare, empty "canvas" in the middle of a
       question — the same treatment the sandboxes got. */
    root.innerHTML = '<div class="ckt ckt-ro"><div class="ckt-main">' +
      '<div class="ckt-canvas"><canvas role="img" aria-label="' +
      esc2(opts.label || 'Schematic diagram for this question') + '"></canvas></div></div></div>';
  } else {
  root.innerHTML =
    '<div class="ckt">' +
      '<div class="ckt-bar">' +
        '<div class="ckt-tools" role="group" aria-label="Tools and parts">' +
          /* Two buttons stay on the bar itself, because they are the two you reach for
             between every other action and a menu you have to open first would be a
             menu you never close. Everything else is a part, and parts live in the
             drawers below. */
          BAR_TOOLS.map(toolBtn).join('') +
          PART_CATS.map(function (cat) {
            /* <details> rather than a hand-rolled popover: it opens on click and on
               Enter, closes on Escape, and is in the tab order — all of which a div
               with a click handler has to be taught, usually badly. */
            return '<details class="ckt-cat"><summary class="ckt-t" title="' +
              esc2(cat.hint) + '">' + esc2(cat.name) +
              '<span class="ckt-caret" aria-hidden="true">\u25be</span></summary>' +
              '<div class="ckt-menu" role="group" aria-label="' + esc2(cat.name) + '">' +
              cat.parts.map(partBtn).join('') + '</div></details>';
          }).join('') +
        '</div>' +
        '<span class="spacer"></span>' +
        '<button class="ckt-t" data-act="zoomout" title="Zoom out (-)" aria-label="Zoom out">−</button>' +
        '<button class="ckt-t" data-act="zoomin" title="Zoom in (+)" aria-label="Zoom in">+</button>' +
        '<button class="ckt-t" data-act="fit" title="Fit the drawing to the window (0)">Fit</button>' +
        '<button class="ckt-t" data-act="group" title="Fold the selection into one block (Shift+G)">Group</button>' +
        '<button class="ckt-t" data-act="ungroup" title="Open a block back out onto the canvas (Shift+U)">Ungroup</button>' +
        '<button class="ckt-t" data-act="rotate" title="Rotate the selection (Shift+R)">Rotate</button>' +
        '<button class="ckt-t" data-act="delete" title="Delete the selection (Del)">Delete</button>' +
        '<button class="ckt-t" data-act="clear">Clear</button>' +
        '<button class="ckt-t" data-act="full" title="Fill the screen (F)" ' +
          'aria-keyshortcuts="F" aria-pressed="false">Expand</button>' +
      '</div>' +
      /* Where you are, and the way back. A block that opens onto a canvas identical to
         the one you came from is a place you can get lost in, so the trail is always on
         screen while there is one — and is not a strip of empty chrome when there is
         not. */
      '<div class="ckt-bar" data-crumbs style="display:none"></div>' +
      '<div class="ckt-main">' +
        /* The canvas is a focus stop and says what it is. role=application because the
           key map below is the whole interface — arrows, Enter and Escape have meanings
           here that are not the browser's, and a screen reader in browse mode would eat
           every one of them before this file saw it. The description is where the map
           lives for someone who cannot see the panel that repeats it. */
        '<div class="ckt-canvas">' +
          '<canvas tabindex="0" role="application" aria-describedby="' + uid + '-keys"' +
            ' aria-label="Schematic canvas. Press Enter for the key map."></canvas>' +
          '<p class="ckt-vh" id="' + uid + '-keys">Arrow keys move the caret one cell; ' +
            'hold Shift to move the selection instead. Enter places the part the toolbar ' +
            'has chosen, draws a wire between two presses, or picks up what is under the ' +
            'caret; Enter again on a block that is already selected opens it, and on a ' +
            'switch throws it. A letter picks a part up: S select, W wire, R resistor, ' +
            'C capacitor, L inductor, V voltage source, I current source, G ground, ' +
            'P test point, K switch, D diode, E light emitting diode, Q and Shift+Q the ' +
            'two bipolars, M and Shift+M the two MOSFETs, O op-amp, B breadboard, ' +
            'U microcontroller. Shift+R rotates, Shift+G groups, Shift+U ungroups, ' +
            'Delete removes the selected parts and wires, and Escape lets go and then ' +
            'closes a block. Plus and minus zoom, 0 fits the drawing. Tab leaves the ' +
            'canvas.</p>' +
          /* Every action on this canvas changes a picture and nothing else. This is
             where it is said in words. */
          '<p class="ckt-vh" data-say role="status" aria-live="polite"></p>' +
        '</div>' +
        '<div class="ckt-side">' +
          '<div class="ckt-panel" data-panel="part"></div>' +
          '<div class="ckt-panel" data-panel="env" hidden></div>' +
          '<div class="ckt-panel">' +
            '<h4>Analysis</h4>' +
            '<div class="seg ckt-modes" role="group" aria-label="Analysis">' +
              '<button data-an="dc" class="active" aria-pressed="true">Operating point</button>' +
              '<button data-an="ac" aria-pressed="false">Frequency</button>' +
              '<button data-an="tran" aria-pressed="false">Transient</button>' +
            '</div>' +
            '<div class="ckt-opts" data-opts></div>' +
            '<button class="btn success ckt-run">Solve</button>' +
          '</div>' +
          '<div class="ckt-out" data-out role="region" aria-label="Analysis result"></div>' +
        '</div>' +
      '</div>' +
      /* Cycle 2 named every sandbox canvas and cycle 6 named the schematic and the
         read-only diagram. This one — the whole output of a sweep or a transient — was
         still a bare canvas, which a screen reader announces as nothing at all. The name
         is rewritten by paintPlot out of the same arrays the curve is drawn from, so it
         cannot describe a plot other than the one on the screen. */
      '<div class="ckt-plot" data-plot hidden><canvas role="img" ' +
        'aria-label="The analysis plot. Press Solve to draw one."></canvas></div>' +
    '</div>';
  }

  const cv = root.querySelector('.ckt-canvas canvas');
  const ctx = cv.getContext('2d');
  const plotWrap = root.querySelector('[data-plot]');
  const ro_ = !!opts.readOnly;
  const plotCv = plotWrap ? plotWrap.querySelector('canvas') : null;
  const outEl = root.querySelector('[data-out]');
  const partPanel = root.querySelector('[data-panel="part"]');
  const envPanel = root.querySelector('[data-panel="env"]');
  const optsEl = root.querySelector('[data-opts]');
  const crumbEl = root.querySelector('[data-crumbs]');
  const sayEl = root.querySelector('[data-say]');

  /* Everything this editor does, it does by redrawing. Said here in words, once, so a
     learner who is not watching the canvas is told what just happened to it — and
     re-stamped with a hair space when the same sentence repeats, because a live region
     whose text has not changed announces nothing, and "placed a resistor" four times
     running is four real events. U+200A rather than a plain space: a trailing ordinary
     space is collapsed out of the computed name, so it would change the DOM and not the
     string, which is the half of the fix that does not work. */
  let saidTwice = false;
  function announce(msg) {
    if (!sayEl || !msg) return;
    saidTwice = !saidTwice;
    sayEl.textContent = msg + (saidTwice ? ' ' : '');
  }

  /* The simulated world, held beside the model rather than in it: a schematic is the
     same schematic in the dark and in the light, and a saved circuit should not
     remember what the light slider happened to be at. Seeded from the model when one
     arrives carrying an environment, so the editor shows the world its own grading
     resolves sensors against rather than a different one. */
  const env = Object.assign({}, ENV_DEFAULT, (opts.model && opts.model.env) || null);

  /* The model as the outside world gets it. The environment rides along, because a
     grader that is handed only the model has no other way to learn what the learner
     set the sliders to — and grading an LDR at a light level the learner is not
     looking at makes the grade disagree with the schematic in front of them, silently.
     It rides along NON-ENUMERABLY: JSON.stringify sees only the schematic, so a saved
     circuit still does not remember the sliders, exactly as the panel promises. */
  function snapshot() {
    const copy = JSON.parse(JSON.stringify(model));
    Object.defineProperty(copy, 'env', {
      value: Object.assign({}, env), enumerable: false, writable: true, configurable: true,
    });
    return copy;
  }

  function P() { return typeof Sandbox !== 'undefined' ? Sandbox.palette() : { ink: '#EDEFF3', dim: '#868E9C', faint: '#78808E', rule: '#6A7280', line: 'rgba(255,255,255,.10)', accent: '#C7F751', blue: '#6E9BFF', amber: '#FFC66D', purple: '#A78BFA', surface: '#0A0B0E' }; }

  /* The key prefix for the drawing on screen — see the flattener. Empty at the top
     level, so every question the canvas asks of a netlist it did not open a block in
     is the question it always asked. */
  function prefix() {
    return path.map(function (id) { return id + '|'; }).join('');
  }

  /* The blocks named by `path`, top down, and the drawing at the end of them. Walked
     from the root each time rather than remembered, so an ungroup or a delete that
     removes a block the trail runs through leaves the canvas somewhere that exists. */
  function reseat() {
    const kept = [];
    let m = model;
    for (let i = 0; i < path.length; i++) {
      const b = (m.parts || []).filter(function (q) { return q.id === path[i]; })[0];
      if (!b || b.kind !== 'IC') break;
      kept.push(b.id);
      m = b.inner || (b.inner = { parts: [], wires: [] });
    }
    path = kept;
    cur = m;
  }

  /* ---- geometry ----
     gx/gy map a grid cell to WORLD pixels and know nothing about zoom or scroll; the
     canvas transform applies the viewport. Keeping the two apart is what lets every
     drawing routine below stay exactly as it was when zoom arrived. */
  const originX = 2, originY = 2;
  function gx(x) { return (x - originX) * GRID + GRID; }
  function gy(y) { return (y - originY) * GRID + GRID; }
  /* screen pixels -> world pixels -> the nearest grid cell */
  function toWorld(sx, sy) { return [sx / view.s + view.px, sy / view.s + view.py]; }
  function toGrid(sx, sy) {
    const w = toWorld(sx, sy);
    return [Math.round((w[0] - GRID) / GRID) + originX, Math.round((w[1] - GRID) / GRID) + originY];
  }
  function evPt(e) {
    const r = cv.getBoundingClientRect();
    return [e.clientX - r.left, e.clientY - r.top];
  }

  /* Everything the drawing occupies, in grid cells. Used by zoom-to-fit and by the
     read-only painter, which have always needed the same answer. */
  function contentBounds() {
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    const see = function (px, py) {
      if (px < x0) x0 = px; if (px > x1) x1 = px;
      if (py < y0) y0 = py; if (py > y1) y1 = py;
    };
    cur.parts.forEach(function (p) {
      Netlist.pinsOf(p).forEach(function (pt) { see(pt[0], pt[1]); });
      see(p.x, p.y);
      /* a body is an area as well as a set of pins — a block whose pins all sit up one
         end, or a board, which has no pins at all — and either would otherwise be
         fitted with half of itself off the screen */
      if (bodyOf(p)) see(p.x + bodyW(p), p.y + bodyH(p));
    });
    cur.wires.forEach(function (wr) { see(wr.a[0], wr.a[1]); see(wr.b[0], wr.b[1]); });
    if (!isFinite(x0)) return null;
    return { x0: x0, y0: y0, x1: x1, y1: y1 };
  }

  function zoomTo(scale, anchorSx, anchorSy) {
    const ns = Math.max(0.3, Math.min(4, isFinite(scale) ? scale : 1));
    if (anchorSx === undefined) { view.s = ns; paintSoon(); return; }
    /* keep the point under the cursor still: it is the difference between zooming
       and being thrown across the drawing */
    const before = toWorld(anchorSx, anchorSy);
    view.s = ns;
    const after = toWorld(anchorSx, anchorSy);
    view.px += before[0] - after[0];
    view.py += before[1] - after[1];
    /* A wheel is a continuous gesture — a trackpad sends notches faster than a frame,
       and 40 inside one frame were 40 full repaints. */
    paintSoon();
  }

  /* Whether the last fit had to stop at the zoom floor with the drawing still overflowing
     the window. Read by the announcement, so what the learner is told matches what the
     canvas did. */
  let fitShort = false;
  function zoomFit() {
    const b = contentBounds();
    const box = cv.parentElement.getBoundingClientRect();
    const w = Math.max(320, box.width), h = Math.max(260, box.height);
    if (!b) { view = { s: 1, px: 0, py: 0 }; fitShort = false; paint(); return; }
    const pad = 1.5;
    const needW = (b.x1 - b.x0 + pad * 2) * GRID, needH = (b.y1 - b.y0 + pad * 2) * GRID;
    const want = Math.min(w / needW, h / needH);
    view.s = Math.max(0.3, Math.min(4, want));
    view.px = gx(b.x0 - pad) - (w / view.s - needW) / 2;
    view.py = gy(b.y0 - pad) - (h / view.s - needH) / 2;
    /* The centring is correct even when the zoom floor bites — the drawing's centre is
       put on the viewport's centre either way, which was checked algebraically rather
       than assumed after a first reading called it a bug. What is NOT correct is calling
       that "fitted": below 0.3 the drawing is wider than the window can hold, so the
       middle is shown and both ends are off, and for a sparse drawing the middle is
       empty. The caller says so rather than reporting a success it did not have.
       No published drawing reaches this: the widest of the 386 in the catalogue is 27
       cells, and the floor does not bite until about 112. */
    fitShort = want < 0.3;
    paint();
  }

  function selOne() {
    if (selIds.size !== 1) return null;
    const id = selIds.values().next().value;
    return cur.parts.find(function (p) { return p.id === id; }) || null;
  }
  function selParts() { return cur.parts.filter(function (p) { return selIds.has(p.id); }); }

  /* What a drag actually moves: the selection, and — if a board is in it — everything
     standing entirely on that board.
     A board that slid out from under its own circuit would leave every pin hanging in
     air. A board that took its parts but left its wires would be worse: the parts would
     arrive where the wires no longer reach, and the circuit would have changed without
     one thing on the screen looking wrong. So the test is the WHOLE object and not part
     of it — a part travels when every pin of it is on the board, a wire when both its
     ends are. Anything with one end off the board is a lead going somewhere else, and it
     stretches instead, which is what a lead does when you pick a board up. */
  function moveBy(dx, dy) {
    const parts = new Set(selParts());
    const wires = new Set();
    /* the boards read off a snapshot, since the loop below adds to `parts` */
    selParts().filter(function (q) { return q.kind === 'BB'; }).forEach(function (b) {
      const w = bodyW(b), h = bodyH(b);
      const on = function (pt) {
        return pt[0] >= b.x && pt[0] <= b.x + w && pt[1] >= b.y && pt[1] <= b.y + h;
      };
      cur.parts.forEach(function (q) {
        if (parts.has(q)) return;
        const pins = Netlist.pinsOf(q);
        if (pins.length && pins.every(on)) parts.add(q);
      });
      cur.wires.forEach(function (wr) { if (on(wr.a) && on(wr.b)) wires.add(wr); });
    });
    parts.forEach(function (q) { q.x += dx; q.y += dy; });
    wires.forEach(function (wr) {
      wr.a = [wr.a[0] + dx, wr.a[1] + dy];
      wr.b = [wr.b[0] + dx, wr.b[1] + dy];
    });
  }

  /* A body's footprint, in cells. A block's is the ground it was standing on when it
     was folded up, kept rather than recomputed so that editing its insides does not
     make the body on the parent canvas breathe in and out; a board's falls out of how
     many columns it has. See bodyOf: a side of zero is opened out to one, since a
     rectangle with no height is a line. */
  function bodyW(p) { const b = bodyOf(p); return b ? b[0] : 0; }
  function bodyH(p) { const b = bodyOf(p); return b ? b[1] : 0; }

  /* A symbol sits on its own cell and is picked up there. */
  function cellPartAt(pt) {
    return cur.parts.find(function (p) {
      return !bodyOf(p) && p.x === pt[0] && p.y === pt[1];
    });
  }
  /* A body is picked up anywhere on it, the way a thing that size has to be. */
  function bodyAt(pt) {
    return cur.parts.find(function (p) {
      const b = bodyOf(p);
      return !!b && pt[0] >= p.x && pt[0] <= p.x + b[0] &&
                    pt[1] >= p.y && pt[1] <= p.y + b[1];
    });
  }
  /* Symbols first, bodies second, and the order is the point: a resistor plugged into
     a board is standing ON the board, and a click that reached the board instead would
     make everything built on one unselectable. A block never overlapped anything
     before, so nothing already drawn is picked up differently. */
  function partAt(pt) {
    return cellPartAt(pt) || bodyAt(pt);
  }

  /* ---- reading the answer back off the schematic ----
   *
   * A readout shows the operating point and nothing else. A lamp brightening through
   * a transient would need an animation nobody asked for, and a lamp showing the
   * first point of a frequency sweep would be showing a number that means nothing —
   * so until there is a DC answer on the canvas, the displays sit blank rather than
   * inventing a reading. */
  /* The solve is always of the WHOLE circuit — a subcircuit's answer depends on what
     is outside it, so solving one on its own would be solving a circuit that does not
     exist — and the prefix is what turns a cell on the canvas in front of you into the
     node it became once everything was flattened. */
  function dcAt(pt) {
    if (!result || result.kind !== 'dc' || !result.net) return null;
    const n = result.net.nodeAt(pt, prefix());
    if (n === null || n === undefined || result.v[n] === undefined) return null;
    return result.v[n];
  }
  /* volts across a two-pin part, in the pin order the netlist uses */
  function acrossOf(p) {
    const pins = Netlist.pinsOf(p);
    const a = dcAt(pins[0]), b = dcAt(pins[1]);
    return (a === null || b === null) ? null : a - b;
  }
  function lampPower(p) {
    const u = acrossOf(p);
    return u === null ? null : u * u / Math.max(p.value, 1e-3);
  }

  /* What a non-linear part is actually doing, taken from the node voltages written on
     the canvas and put back through the same model the solver iterated on. Read back
     rather than carried out of the solve, because then the current a learner sees on the
     part and the voltages they see on its pins are provably the same answer: if the two
     ever disagreed, the model would be the thing at fault and it would show. The
     limiters are off, since these are settled voltages and not a guess to be held. */
  function deviceOp(p) {
    if (!Devices.is(p.kind)) return null;
    const pins = Netlist.pinsOf(p);
    const vs = [];
    for (let i = 0; i < PART_KINDS[p.kind].pins; i++) {
      const u = dcAt(pins[i]);
      if (u === null) return null;
      vs.push(u);
    }
    const d = Devices.build(p);
    return { v: vs, i: d.iv(d, vs, { raw: true }).i };
  }

  /* The pin states a microcontroller was left in by the last solve, or null before
     there has been one. Taken off the netlist that solve built rather than kept beside
     it, so what the drawing shows and what the matrix was stamped from are the same
     object and cannot describe two different runs. */
  function mcuRecOf(p) {
    if (!result || !result.net || !result.net.mcus) return null;
    return result.net.mcus[prefix() + p.id] || null;
  }

  /* The halo a part that emits gets: a filled disc and eight rays, both scaled by the
     square root of the brightness because the eye is not linear in power. Shared, so the
     lamp and the LED cannot come to disagree about what bright looks like. */
  function drawGlow(pal, br, r) {
    const g = Math.sqrt(br);
    ctx.save();
    ctx.globalAlpha = 0.18 + 0.55 * g;
    ctx.fillStyle = pal.amber;
    ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();
    ctx.globalAlpha = 0.35 + 0.5 * g;
    ctx.strokeStyle = pal.amber;
    ctx.beginPath();
    for (let i = 0; i < 8; i++) {
      const a = i * Math.PI / 4 + Math.PI / 8;
      ctx.moveTo(Math.cos(a) * (r + 2), Math.sin(a) * (r + 2));
      ctx.lineTo(Math.cos(a) * (r + 3 + 5 * g), Math.sin(a) * (r + 3 + 5 * g));
    }
    ctx.stroke();
    ctx.restore();
    ctx.beginPath();
  }

  /* What a part writes next to itself. A sensor shows the resistance it has resolved
     to in the current environment, not the parameter in its value box: the whole
     point of a sensor is that the number moves, and watching it move as the slider
     moves is the fastest way to see which way round the model goes. */
  /* R1, R2, C1 — numbered per KIND and per CANVAS, the way a schematic is.

     The label used to be the part's creation index across every kind, so a canvas
     where you had already placed a ground, a source and a couple of others gave you
     "R8" for your first resistor. The number a learner reads has to be the one they
     would write on paper.

     Assigned once, when the part is placed, and kept: deleting R1 does not renumber
     R2 to R1 underneath a drawing someone is halfway through annotating. */
  function nextRef(kind, within) {
    const pre = refPrefix(kind);
    const used = {};
    (within || model.parts).forEach(function (p) {
      if (refPrefix(p.kind) !== pre) return;
      const n = typeof p.ref === 'number' ? p.ref : null;
      if (n) used[n] = 1;
    });
    let n = 1;
    while (used[n]) n++;
    return n;
  }

  /* The fallback is for a part that somehow reached the canvas without passing the
     sanitiser; everything that came in through a model has been stamped already. */
  function refOf(p) {
    return refPrefix(p.kind) + (typeof p.ref === 'number' ? p.ref : p.id.replace('p', ''));
  }

  function labelOf(p, k) {
    const n = (typeof p.ref === 'number' ? p.ref : p.id.replace('p', ''));
    if (p.kind === 'SW') return 'SW' + n + '  ' + (p.closed ? 'closed' : 'open');
    if (p.kind === 'LDR' || p.kind === 'NTC') return p.kind + n + '  ' + fmtEng(ohmsOf(p, env), 'Ω');
    if (p.kind === 'POT') {
      const w = p.wiper === undefined ? 0.5 : p.wiper;
      return 'POT' + n + '  ' + fmtEng(p.value, 'Ω') + ' w=' + w.toFixed(2);
    }
    if (p.kind === 'LAMP') {
      const pw = lampPower(p);
      return 'LAMP' + n + '  ' + fmtEng(p.value, 'Ω') + (pw === null ? '' : '  ' + fmtEng(pw, 'W'));
    }
    if (p.kind === 'METER') {
      const u = acrossOf(p);
      return 'A' + n + (u === null ? '  in series' : '  ' + fmtEng(u / Math.max(p.value, 1e-6), 'A'));
    }
    /* A non-linear part's value is a saturation current or a square-law constant, and
       writing 10 fA beside a diode tells a learner nothing they can use. What they want
       from the drawing is where the device has landed, so the label is the operating
       point when there is one and the part's name when there is not. */
    if (Devices.is(p.kind)) {
      const op = deviceOp(p);
      if (p.kind === 'OPAMP') return 'U' + n + '  A=' + fmtEng(p.value, '');
      if (op === null) return p.kind + n;
      if (p.kind === 'D' || p.kind === 'LED') {
        return p.kind + n + '  ' + fmtEng(op.v[0] - op.v[1], 'V') + ' ' + fmtEng(op.i[0], 'A');
      }
      return p.kind + n + '  ' + (p.kind === 'NPN' || p.kind === 'PNP' ? 'Ic ' : 'Id ') +
        fmtEng(Math.abs(op.i[0]), 'A');
    }
    return p.kind + n + '  ' + fmtEng(p.value, k.unit);
  }

  /* ---- drawing ---- */

  /* A breadboard, drawn as what it is: holes. There is not one line on it standing for
     a connection, because on the real thing there is not one either — the connections
     are underneath, and reading them off the layout is the entire skill the board
     teaches. Drawing them would hand the learner the answer and, worse, would put a
     mark on the canvas that means something different from every other mark on it. So
     the drawing's job is only to make the layout unmistakable: five holes to a strip,
     a channel splitting every column in two, and the rails running the length with a
     sign at each end.
     Every hole comes from bbStripAt, the same function the netlist joins strips with,
     so the board cannot come to show a hole that is not there or hide one that is. */
  function drawBoard(p, colour, pal) {
    const C = bbCols(p);
    const edge = colour || pal.line;
    /* The lip of board outside the outer holes. Wide enough that the rail stripe below
       reads as printed ON the board rather than as the edge of it — at a narrower lip
       the two lines sit a few pixels apart and the eye takes the pair for one border. */
    const M = 0.8;
    const x0 = gx(p.x - M), x1 = gx(p.x + C - 1 + M);
    const y0 = gy(p.y - M), y1 = gy(p.y + BB_H - 1 + M);
    const r = 5;

    ctx.save();
    ctx.lineWidth = 1.5;
    ctx.lineCap = 'butt';
    ctx.beginPath();
    /* corners rounded by hand; roundRect is not old enough to rely on */
    ctx.moveTo(x0 + r, y0);
    ctx.lineTo(x1 - r, y0); ctx.quadraticCurveTo(x1, y0, x1, y0 + r);
    ctx.lineTo(x1, y1 - r); ctx.quadraticCurveTo(x1, y1, x1 - r, y1);
    ctx.lineTo(x0 + r, y1); ctx.quadraticCurveTo(x0, y1, x0, y1 - r);
    ctx.lineTo(x0, y0 + r); ctx.quadraticCurveTo(x0, y0, x0 + r, y0);
    ctx.closePath();
    ctx.fillStyle = pal.surface || '#0A0B0E';
    ctx.fill();
    ctx.strokeStyle = edge;
    ctx.stroke();

    /* The channel, sunk rather than merely left blank. It is the one feature of the
       board that is a fact about the netlist — it is why the two halves of a column
       are two nodes — and an empty row would read as holes somebody forgot to draw. */
    const cy0 = gy(p.y + BB_CHAN - 0.5), cy1 = gy(p.y + BB_CHAN + 0.5);
    /* The wash is decoration and stays where it was: `faint` went from 1.73:1 to 4.60,
       so holding this at 1.14 means dropping the alpha from 0.30 to 0.12. The two edges
       are not decoration — they are the boundary the comment above is about — so they
       take `rule`, which is the tier for a mark that means something without being read. */
    ctx.fillStyle = pal.faint;
    ctx.globalAlpha = 0.12;
    ctx.fillRect(x0 + 1.5, cy0, x1 - x0 - 3, cy1 - cy0);
    ctx.globalAlpha = 1;
    ctx.strokeStyle = pal.rule;
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(x0 + 1.5, cy0); ctx.lineTo(x1 - 1.5, cy0);
    ctx.moveTo(x0 + 1.5, cy1); ctx.lineTo(x1 - 1.5, cy1);
    ctx.stroke();

    /* The rail stripes, with the sign written at both ends of each. A rail is the one
       strip whose extent you cannot see from the holes — five in a row look the same
       whether they stop at the fifth or run to the end of the board — so the stripe is
       doing real work and not decoration. */
    ctx.lineWidth = 1.5;
    ctx.font = '10px ui-monospace, monospace';
    ctx.textBaseline = 'middle';
    [[0, -1, '+', pal.amber], [BB_RAIL - 1, 1, '−', pal.blue],
     [BB_H - BB_RAIL, -1, '−', pal.blue], [BB_H - 1, 1, '+', pal.amber]]
      .forEach(function (rail) {
        const ry = gy(p.y + rail[0]) + rail[1] * GRID * 0.42;
        ctx.strokeStyle = rail[3];
        ctx.beginPath();
        ctx.moveTo(gx(p.x), ry); ctx.lineTo(gx(p.x + C - 1), ry);
        ctx.stroke();
        ctx.fillStyle = rail[3];
        ctx.textAlign = 'right';
        ctx.fillText(rail[2], x0 - 4, ry);
        ctx.textAlign = 'left';
        ctx.fillText(rail[2], x1 + 4, ry);
      });

    /* The holes. Small and square, and deliberately not the round junction dot this
       canvas draws where three things meet: a hole is somewhere a lead may go, and
       nothing is joined there until one does. */
    ctx.fillStyle = pal.dim;
    ctx.globalAlpha = 0.7;
    for (let c = 0; c < C; c++) {
      for (let rw = 0; rw < BB_H; rw++) {
        if (bbStripAt(p, p.x + c, p.y + rw) === null) continue;
        ctx.fillRect(gx(p.x + c) - 1.6, gy(p.y + rw) - 1.6, 3.2, 3.2);
      }
    }

    /* Column numbers every five, printed in the channel: the way a board does it, and
       the one row with no holes for them to sit on top of. */
    ctx.font = '8.5px ui-monospace, monospace';
    ctx.textAlign = 'center';
    for (let c = 4; c < C; c += 5) ctx.fillText(String(c + 1), gx(p.x + c), gy(p.y + BB_CHAN));
    ctx.globalAlpha = 1;
    ctx.restore();
  }

  function drawPart(p, colour, pal) {
    const x = gx(p.x), y = gy(p.y);
    const k = PART_KINDS[p.kind];
    pal = pal || P();
    ctx.strokeStyle = colour;
    ctx.fillStyle = colour;
    ctx.lineWidth = 1.8;
    ctx.lineCap = 'round';

    if (p.kind === 'OUT') {
      ctx.beginPath();
      ctx.arc(x, y, 5, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(x, y - 5); ctx.lineTo(x, y - 13);
      ctx.stroke();
      ctx.font = '10px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.fillText('out', x, y - 18);
      return;
    }

    if (p.kind === 'GND') {
      ctx.beginPath();
      ctx.moveTo(x, y); ctx.lineTo(x, y + 8);
      ctx.moveTo(x - 9, y + 8); ctx.lineTo(x + 9, y + 8);
      ctx.moveTo(x - 5, y + 12); ctx.lineTo(x + 5, y + 12);
      ctx.moveTo(x - 2, y + 16); ctx.lineTo(x + 2, y + 16);
      ctx.stroke();
      return;
    }

    /* A bar display hangs off one node and takes no part in the solution, so it is
       drawn like the probe: a stub up to a gauge, the number above it, and the scale
       it is being read against written underneath. A bar with no stated full scale
       is a bar you cannot read. */
    if (p.kind === 'BAR') {
      const full = Math.abs(p.value) > 1e-12 ? Math.abs(p.value) : 5;
      const v = dcAt([p.x, p.y]);
      const bw = 48, bh = 11, bx = x - bw / 2, by = y - 8 - bh;
      ctx.beginPath();
      ctx.moveTo(x, y); ctx.lineTo(x, by + bh);
      ctx.stroke();
      ctx.strokeRect(bx, by, bw, bh);
      if (v !== null) {
        const frac = Math.min(Math.max(v / full, 0), 1);
        ctx.fillStyle = v < 0 ? pal.amber : colour;
        if (frac > 0) ctx.fillRect(bx + 1.5, by + 1.5, (bw - 3) * frac, bh - 3);
        /* over-range gets a caret rather than a full bar that quietly lies */
        if (v > full) {
          ctx.beginPath();
          ctx.moveTo(bx + bw + 3, by + 1); ctx.lineTo(bx + bw + 8, by + bh / 2);
          ctx.lineTo(bx + bw + 3, by + bh - 1);
          ctx.fillStyle = pal.amber;
          ctx.fill();
        }
      }
      ctx.font = '10.5px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = v === null ? pal.dim : (v < 0 || v > full ? pal.amber : colour);
      ctx.fillText(v === null ? 'BAR' + p.id.replace('p', '') : fmtEng(v, 'V'), x, by - 8);
      ctx.fillStyle = pal.dim;
      ctx.fillText('0–' + fmtEng(full, 'V'), x, y + 11);
      return;
    }

    /* ---- a microcontroller ----
       A body like a block's, and for the same reason: twelve pins with names on them
       do not fit on a symbol. What it has that a block does not is a STATE worth
       drawing — after a run, each pin is showing which way it is facing and what it
       last drove or read, because "the sketch says HIGH" and "the pin is at 5 V" are
       two different claims and this is where a learner finds out they have come apart. */
    if (p.kind === 'MCU') {
      const rec = mcuRecOf(p);
      const bx = gx(p.x + MCU_W), by = gy(p.y + MCU_H), r = 4;
      ctx.beginPath();
      ctx.moveTo(x + r, y);
      ctx.lineTo(bx - r, y); ctx.quadraticCurveTo(bx, y, bx, y + r);
      ctx.lineTo(bx, by - r); ctx.quadraticCurveTo(bx, by, bx - r, by);
      ctx.lineTo(x + r, by); ctx.quadraticCurveTo(x, by, x, by - r);
      ctx.lineTo(x, y + r); ctx.quadraticCurveTo(x, y, x + r, y);
      ctx.closePath();
      ctx.fillStyle = pal.surface || '#0A0B0E';
      ctx.fill();
      ctx.strokeStyle = colour;
      ctx.stroke();

      ctx.font = '9px ui-monospace, monospace';
      ctx.textBaseline = 'middle';
      MCU_PINS.forEach(function (d, i) {
        const pin = rec ? rec.pins[i] : null;
        const px = gx(p.x + (d.side ? MCU_W : 0)), py = gy(p.y + d.row);
        /* A driven pin is filled, everything else is hollow: the difference between a
           pin pushing current and a pin merely listening is the single most useful
           thing this drawing can carry, and it reads at any zoom. */
        const driving = pin && (pin.power || pin.mode === 'out' || pin.mode === 'pullup');
        ctx.fillStyle = pin && pin.mode === 'out' && pin.drive > 0.5 ? pal.accent : colour;
        if (driving) ctx.fillRect(px - 3, py - 3, 6, 6);
        else { ctx.strokeStyle = colour; ctx.strokeRect(px - 2.5, py - 2.5, 5, 5); }

        ctx.fillStyle = d.power ? pal.dim : colour;
        ctx.textAlign = d.side ? 'right' : 'left';
        ctx.fillText(d.name, px + (d.side ? -7 : 7), py);
        /* and, when there is an answer on the canvas, what the pin is actually doing */
        if (!pin || d.power) return;
        const tag = pin.mode === 'out'
          ? (pin.drive === 0 || pin.drive === 1 ? (pin.drive ? 'H' : 'L')
             : Math.round(pin.drive * 100) + '%')
          : pin.mode === 'pullup' ? 'pu' : '';
        if (!tag) return;
        ctx.fillStyle = pal.dim;
        ctx.fillText(tag, px + (d.side ? -30 : 30), py);
      });

      /* In the two empty bands rather than across the middle: the middle of this body is
         a pin row whichever way you count, and a name written along one is a name
         written through a label. */
      ctx.fillStyle = colour;
      ctx.textAlign = 'center';
      ctx.font = '10px ui-monospace, monospace';
      ctx.fillText('MCU' + p.id.replace('p', ''), (x + bx) / 2, gy(p.y) + GRID / 2);
      ctx.font = '8.5px ui-monospace, monospace';
      ctx.fillStyle = pal.dim;
      ctx.fillText(fmtEng(MCU_VCC, 'V'), (x + bx) / 2, gy(p.y + MCU_H) - GRID / 2);
      return;
    }

    /* ---- a block ----
       A body, not a symbol: a rectangle standing on the ground the parts it swallowed
       were standing on, with a filled pin on every cell its boundary was crossed at.
       Those cells are not chosen for the look of the thing — they are exactly where the
       wires outside already ended (see pinsOf), and that is the whole reason folding a
       selection up leaves every answer where it was. The body is filled rather than
       outlined so a wire passing behind one reads as passing behind it. */
    if (p.kind === 'IC') {
      const bx = gx(p.x + bodyW(p)), by = gy(p.y + bodyH(p)), r = 4;
      ctx.beginPath();
      /* corners rounded by hand; roundRect is not old enough to rely on */
      ctx.moveTo(x + r, y);
      ctx.lineTo(bx - r, y); ctx.quadraticCurveTo(bx, y, bx, y + r);
      ctx.lineTo(bx, by - r); ctx.quadraticCurveTo(bx, by, bx - r, by);
      ctx.lineTo(x + r, by); ctx.quadraticCurveTo(x, by, x, by - r);
      ctx.lineTo(x, y + r); ctx.quadraticCurveTo(x, y, x + r, y);
      ctx.closePath();
      ctx.fillStyle = pal.surface || '#0A0B0E';
      ctx.fill();
      ctx.strokeStyle = colour;
      ctx.stroke();

      ctx.fillStyle = colour;
      ctx.font = '9.5px ui-monospace, monospace';
      ctx.textBaseline = 'middle';
      (p.ports || []).forEach(function (port) {
        (port.cells || []).forEach(function (c) {
          const px = gx(p.x + c[0]), py = gy(p.y + c[1]);
          ctx.fillRect(px - 2.5, py - 2.5, 5, 5);
          /* the name is written on the inward side, where no wire can arrive */
          if (c[0] === 0) { ctx.textAlign = 'left'; ctx.fillText(port.name, px + 7, py); }
          else if (c[0] === bodyW(p)) { ctx.textAlign = 'right'; ctx.fillText(port.name, px - 7, py); }
          else { ctx.textAlign = 'center'; ctx.fillText(port.name, px, py + (c[1] === 0 ? 9 : -9)); }
        });
      });

      /* The title, clipped to the body. A name that runs on over the wires beside the
         block is worse than one that is cut off, because a cut-off name is visibly
         cut off and a name lying across a wire is just unreadable. */
      ctx.save();
      ctx.beginPath();
      ctx.rect(x + 2, y + 2, bx - x - 4, by - y - 4);
      ctx.clip();
      const held = ((p.inner && p.inner.parts) || []).length;
      const mx = (x + bx) / 2, my = (y + by) / 2;
      ctx.textAlign = 'center';
      ctx.font = 'bold 11px ui-monospace, monospace';
      ctx.fillText(p.title || 'Block', mx, held ? my - 6 : my);
      if (held) {
        ctx.font = '9.5px ui-monospace, monospace';
        ctx.fillStyle = pal.dim;
        ctx.fillText(held + (held === 1 ? ' part' : ' parts'), mx, my + 7);
      }
      ctx.restore();
      return;
    }

    ctx.save();
    ctx.translate(x, y);
    if (p.rot) ctx.rotate(turnsOf(p) * Math.PI / 2);
    const L = GRID;                       /* pin-to-pin half span */
    ctx.beginPath();
    if (p.kind === 'R') {
      ctx.moveTo(-L, 0); ctx.lineTo(-13, 0);
      resistorBody(ctx, -13, 13, 4);
      ctx.moveTo(13, 0); ctx.lineTo(L, 0);
      ctx.stroke();
    } else if (p.kind === 'C') {
      ctx.moveTo(-L, 0); ctx.lineTo(-4, 0);
      ctx.moveTo(4, 0); ctx.lineTo(L, 0);
      ctx.moveTo(-4, -9); ctx.lineTo(-4, 9);
      ctx.moveTo(4, -9); ctx.lineTo(4, 9);
      ctx.stroke();
    } else if (p.kind === 'L') {
      ctx.moveTo(-L, 0); ctx.lineTo(-14, 0);
      for (let i = 0; i < 4; i++) ctx.arc(-14 + 7 + i * 7, 0, 3.5, Math.PI, 0, false);
      ctx.lineTo(L, 0);
      ctx.stroke();
    } else if (p.kind === 'SW') {
      /* The blade is the state: drawn lying down when closed and lifted when open, so
         the schematic answers "is it on?" without anyone opening a panel. */
      ctx.moveTo(-L, 0); ctx.lineTo(-12, 0);
      ctx.moveTo(12, 0); ctx.lineTo(L, 0);
      if (p.closed) { ctx.moveTo(-12, 0); ctx.lineTo(12, 0); }
      else { ctx.moveTo(-12, 0); ctx.lineTo(10, -12); }
      ctx.stroke();
      ctx.beginPath(); ctx.arc(-12, 0, 2.2, 0, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.arc(12, 0, 2.2, 0, Math.PI * 2); ctx.fill();
    } else if (p.kind === 'LDR' || p.kind === 'NTC' || p.kind === 'POT') {
      /* all three are a resistor body with something done to it */
      ctx.moveTo(-L, 0); ctx.lineTo(-13, 0);
      resistorBody(ctx, -13, 13, 4);
      ctx.moveTo(13, 0); ctx.lineTo(L, 0);
      if (p.kind === 'LDR') {
        /* two arrows pointing IN at the body: light arriving, the sense the symbol
           has always had — an LED's arrows point away because it emits */
        for (const ax of [-8, 2]) {
          ctx.moveTo(ax - 9, -21); ctx.lineTo(ax, -12);
          ctx.moveTo(ax, -12); ctx.lineTo(ax - 5, -13.5);
          ctx.moveTo(ax, -12); ctx.lineTo(ax - 1.5, -17);
        }
      } else if (p.kind === 'NTC') {
        /* the thermistor's diagonal, with its foot along the bottom */
        ctx.moveTo(-16, 12); ctx.lineTo(-11, 12); ctx.lineTo(13, -12);
      } else {
        /* the wiper: an arrow down the third pin onto the track */
        ctx.moveTo(0, -L); ctx.lineTo(0, -10);
        ctx.moveTo(-3.5, -14); ctx.lineTo(0, -9.5); ctx.lineTo(3.5, -14);
      }
      ctx.stroke();
    } else if (p.kind === 'D' || p.kind === 'LED') {
      /* The registry's own path, at the one scale that puts its two leads on the two
         pins: 60 units of symbol to a grid cell. The drill's symbol and the editor's are
         therefore one drawing and cannot come to disagree about which way the triangle
         points — which matters here more than anywhere else in the file, because for a
         diode the triangle IS the polarity. The anode is the pin the current enters, at
         local −L: left flat, top rotated, the same reading as plusFirst's. */
      if (p.kind === 'LED') {
        const op = deviceOp(p);
        const br = op === null ? 0
          : Math.min(Math.max(op.i[0] / Math.max(p.inom === undefined ? 0.02 : p.inom, 1e-9), 0), 1);
        if (br > 0.002) drawGlow(pal, br, 12);
      }
      ctx.save();
      const sd = L / 60;
      ctx.scale(sd, sd);
      ctx.lineWidth = 1.8 / sd;
      ctx.beginPath();
      Symbols.get(p.kind).draw(ctx);
      ctx.stroke();
      ctx.restore();
    } else if (p.kind === 'NPN' || p.kind === 'PNP' || p.kind === 'NMOS' || p.kind === 'PMOS') {
      /* All four transistor symbols in the registry share one lead geometry — the
         control lead ending at (-60, 0) and the two channel leads at (22, ∓60) — and
         landing those three points on the three cells a three-pin part has is a single
         affine map. So these are the registry's paths too, quarter-turned and squeezed:
         the 120 units between the channel leads become the 2·GRID between the outer
         pins, and the 82 units from the control lead across to them become the GRID out
         to the third. A symbol and its own pins can then never drift apart, and the
         emitter arrow on the canvas is the same arrow as the one in the drill.
         The map reflects as well as turns, which costs nothing: an arrow along a lead
         still points along that lead afterwards, and that is the whole of what it says. */
      ctx.save();
      const sx = 2 * L / 120, sy = L / 82;
      ctx.transform(0, sy, sx, 0, 0, -sy * 22);
      ctx.lineWidth = 1.8 / Math.sqrt(sx * sy);
      ctx.beginPath();
      Symbols.get(p.kind).draw(ctx);
      ctx.stroke();
      ctx.restore();
    } else if (p.kind === 'OPAMP') {
      /* The one symbol that is drawn here rather than traced from the registry. Its
         three leads leave the body as two-from-the-left and one-from-the-right, and no
         affine map takes that to the two-in-line-plus-one-at-right-angles a three-pin
         part has without shearing the triangle into a wedge. A leaning op-amp is worse
         than a second drawing, so: a second drawing, and the registry keeps the upright
         one the drill needs.
         The + and − ride inside the body, so they turn with it and stay attached to the
         inputs they name — unlike the source's + in the branch below, which sits on a
         circle that looks the same either way up. */
      ctx.moveTo(-13, -15); ctx.lineTo(13, 0); ctx.lineTo(-13, 15); ctx.closePath();
      ctx.moveTo(-L, 0); ctx.lineTo(-13, 0);        /* in+, in line with the body */
      ctx.moveTo(13, 0); ctx.lineTo(L, 0);          /* out */
      ctx.moveTo(0, -L); ctx.lineTo(0, -7.5);       /* in−, down the third pin */
      ctx.moveTo(-11, 6); ctx.lineTo(-5, 6);        /* + beside the in-line input */
      ctx.moveTo(-8, 3); ctx.lineTo(-8, 9);
      ctx.moveTo(-8, -7); ctx.lineTo(-2, -7);       /* − beside the third pin */
      ctx.stroke();
    } else if (p.kind === 'LAMP') {
      const pw = lampPower(p);
      const br = pw === null ? 0 : Math.min(Math.max(pw / Math.max(p.pnom === undefined ? 0.25 : p.pnom, 1e-9), 0), 1);
      /* brightness is shown, not stated — see drawGlow */
      if (br > 0.002) drawGlow(pal, br, 11);
      ctx.moveTo(-L, 0); ctx.lineTo(-11, 0);
      ctx.moveTo(11, 0); ctx.lineTo(L, 0);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, 11, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      const d = 11 * Math.SQRT1_2;
      ctx.moveTo(-d, -d); ctx.lineTo(d, d);
      ctx.moveTo(-d, d); ctx.lineTo(d, -d);
      ctx.stroke();
    } else if (p.kind === 'METER') {
      ctx.moveTo(-L, 0); ctx.lineTo(-11, 0);
      ctx.moveTo(11, 0); ctx.lineTo(L, 0);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, 11, 0, Math.PI * 2);
      ctx.stroke();
      /* the reference direction the reading is signed against — an ammeter that does
         not say which way is positive turns every answer into a coin toss */
      ctx.beginPath();
      ctx.moveTo(-7, -16); ctx.lineTo(7, -16);
      ctx.moveTo(3, -19); ctx.lineTo(7, -16); ctx.lineTo(3, -13);
      ctx.stroke();
    } else {
      /* V and I share a circle; the marking inside says which */
      ctx.moveTo(-L, 0); ctx.lineTo(-11, 0);
      ctx.moveTo(11, 0); ctx.lineTo(L, 0);
      ctx.stroke();
      ctx.beginPath();
      ctx.arc(0, 0, 11, 0, Math.PI * 2);
      ctx.stroke();
      ctx.beginPath();
      if (p.kind === 'V') {
        /* + on the terminal the solver treats as positive — which is the RIGHT pin
           flat and the TOP pin rotated (see plusFirst). Rotating the canvas by +90°
           sends local +x to the BOTTOM of the screen, so drawing the + at a fixed
           local +x put it on the bottom pin of a vertical source: the drawn polarity
           was the opposite of the solved one, and a learner reading the sign off the
           symbol got it backwards. The glyphs swap ends with the symbol instead. The
           solver's convention is untouched; only the label moves. What decides it is
           whether the body is standing up, not whether it has been turned at all: turned
           through half a circle the source is the same way up and the + is simply at the
           other end, which the canvas rotation has already seen to. */
        const s = (turnsOf(p) % 2) ? -1 : 1;
        ctx.moveTo(3 * s, -4); ctx.lineTo(9 * s, -4);
        ctx.moveTo(6 * s, -7); ctx.lineTo(6 * s, -1);
        ctx.moveTo(-9 * s, -4); ctx.lineTo(-3 * s, -4);
      } else {
        ctx.moveTo(0, 7); ctx.lineTo(0, -7);
        ctx.moveTo(-3.5, -3.5); ctx.lineTo(0, -7); ctx.lineTo(3.5, -3.5);
      }
      ctx.stroke();
    }
    ctx.restore();

    /* Letters go on outside the rotation, or a vertical meter reads sideways. */
    if (p.kind === 'METER') {
      ctx.font = 'bold 10px ui-monospace, monospace';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = colour;
      ctx.fillText('A', x, y + 0.5);
    }

    /* Value label, clear of the body — and clear of whatever the body grew. R, C, L,
       V and I keep the placement they have always had, because a hundred and fifty
       published figures are drawn with it. The kinds that carry a mark outside the
       body (an LDR's arrows, a meter's direction arrow, a lamp's glow) need more room
       than that, and a potentiometer needs its label on the side its wiper is not:
       the wiper is a pin, a wire arrives on it, and a label centred there would be
       written across the wire. */
    ctx.font = '10.5px ui-monospace, monospace';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = colour;
    const lab = labelOf(p, k);
    const wide = { LDR: 24, METER: 22, LAMP: 22, SW: 20, NTC: 20 }[p.kind];
    /* Any part with a pin at right angles to its body wants its label on the other side,
       for the reason the potentiometer wanted it there: a wire arrives on that third
       pin, and a label written across a wire is a label nobody can read. Asking the
       registry how many pins a kind has rather than listing the kinds means a transistor
       inherits the placement instead of having to be remembered. */
    if ((PART_KINDS[p.kind] || {}).pins === 3) {
      /* opposite the control pin, whichever of the four ways round the part is turned */
      const r = turnsOf(p);
      if (r === 1) { ctx.textAlign = 'right'; ctx.fillText(lab, x - 22, y); }
      else if (r === 3) { ctx.textAlign = 'left'; ctx.fillText(lab, x + 22, y); }
      else ctx.fillText(lab, x, y + (r === 2 ? -22 : 22));
    } else if (wide) {
      if (turnsOf(p) % 2) { ctx.textAlign = 'left'; ctx.fillText(lab, x + wide, y); }
      else ctx.fillText(lab, x, y - 26);
    } else if (turnsOf(p) % 2) {
      /* Left-aligned, not centred. A centred label grows in BOTH directions, so
         "V1  12 V" reached back across the source it names while "R1" sat clear —
         the longer the value, the worse the overlap, which is the wrong way round. */
      ctx.textAlign = 'left';
      ctx.fillText(lab, x + 17, y);
    } else ctx.fillText(lab, x, y - 17);
  }

  function paint() {
    if (disposed) return;
    const box = cv.parentElement.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(320, Math.round(box.width));
    const h = Math.max(260, Math.round(box.height));
    if (cv.width !== w * dpr || cv.height !== h * dpr) {
      cv.width = w * dpr; cv.height = h * dpr;
      cv.style.width = w + 'px'; cv.style.height = h + 'px';
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const pal = P();
    ctx.clearRect(0, 0, w, h);

    /* A diagram is a question's illustration, so cropping it is not a cosmetic
       failure — the probe the question asks about was falling off the right-hand edge
       at ordinary laptop widths. The editor can scroll and pan; a diagram cannot, so
       it scales itself to fit and centres what is left.
       The bounds come from contentBounds() rather than from a second copy of it. There
       were two, differing only in their padding, and a fix applied to one of them was a
       fix that reached half the canvases in the app. */
    let roScale = 1, roX0 = 0, roY0 = 0;
    const rob = ro_ && cur.parts.length ? contentBounds() : null;
    if (rob) {
      const pad = 1.2;
      const needW = (rob.x1 - rob.x0 + pad * 2) * GRID, needH = (rob.y1 - rob.y0 + pad * 2) * GRID;
      /* A floor as well as a ceiling. The ceiling was here because a two-part diagram
         blown up to fill a laptop is a cartoon; the floor is here because the other end
         had nothing at all, and a diagram whose span is large enough draws at a scale
         near zero — every part of it inside one pixel, an empty box with no error. No
         published diagram reaches it (the widest of the 386 is 27 cells and the deepest
         it goes is 1.18), so this bounds a case content cannot currently produce, which
         is the only time to add a bound cheaply. */
      roScale = Math.max(0.08, Math.min(w / needW, h / needH, 1.6));
      roX0 = (rob.x0 - pad - originX) * GRID + GRID - (w / roScale - needW) / 2;
      roY0 = (rob.y0 - pad - originY) * GRID + GRID - (h / roScale - needH) / 2;
      ctx.setTransform(dpr * roScale, 0, 0, dpr * roScale,
        -roX0 * roScale * dpr, -roY0 * roScale * dpr);
    }

    /* The editor's viewport. The read-only branch above has already set its own
       fit-to-box transform and must not be overwritten. */
    if (!ro_) {
      ctx.setTransform(dpr * view.s, 0, 0, dpr * view.s,
        -view.px * view.s * dpr, -view.py * view.s * dpr);
    }

    /* Grid dots, drawn across whatever part of the world is currently visible rather
       than across the canvas: at any zoom other than 1 those are different regions,
       and drawing the canvas one leaves the dots pinned to the screen while the
       circuit slides underneath.
       The scale is the drawn one — the read-only branch fits to the box and has its
       own — so the region asked for is the region the transform will actually map,
       rather than the editor's viewport borrowed for a picture that is not using it. */
    const dscale = ro_ ? roScale : view.s;
    const vx0 = ro_ ? roX0 : view.px, vy0 = ro_ ? roY0 : view.py;
    const vx1 = vx0 + w / dscale, vy1 = vy0 + h / dscale;
    /* Counted, not walked. `for (X = start; X < end; X += GRID)` is a loop whose step
       is only a step while the numbers are small: above 2^58 a double does not change
       when 26 is added to it, so X stops advancing, the condition stays true and the
       tab is gone — no error, no slow frame, nothing to interrupt. That is not a
       hypothetical. zoomFit puts view.px at about 13 times the largest coordinate in
       the drawing, so one wire ending at x = 1e17 in a saved circuit froze the page on
       the first press of Fit, measured. The coordinates are bounded now (see
       sanitiseDrawing), and this loop is bounded too, because "the caller is careful"
       is not a property a loop can rely on and this caller was not.
       The density cut-off below is NOT a saving at the zoom the editor reaches: at the
       0.3 floor the dots are 7.8px apart, and the grid there costs 13478 fillRect calls
       a repaint against 1236 at zoom 1 — measured before and after, unchanged, because
       0.3 is above the cut-off. What made that number stop mattering is the coalescer,
       which holds it to one repaint a frame instead of one an event. The cut-off is here
       for the read-only branch, whose scale now has a floor of 0.08 and whose dots would
       be a fifth of a pixel apart — a tint, not a snapping guide — and as the backstop
       that keeps this loop bounded whatever a later caller does to the viewport. */
    const GRID_MIN_PX = 5;      /* dots closer than this are mush, not a snapping guide */
    const GRID_MAX = 20000;     /* a backstop, an order above the densest honest grid */
    if (GRID * dscale >= GRID_MIN_PX) {
      const c0 = Math.max(1, Math.floor(vx0 / GRID)), c1 = Math.floor(vx1 / GRID) + 1;
      const r0 = Math.max(1, Math.floor(vy0 / GRID)), r1 = Math.floor(vy1 / GRID) + 1;
      const cols = Math.min(Math.max(0, c1 - c0 + 1), GRID_MAX);
      const rows = Math.min(Math.max(0, r1 - r0 + 1), GRID_MAX);
      /* Held at 1.28:1, where it was: the snapping grid is the one thing on this canvas
         that is genuinely decoration, and `faint` rising to 4.60 would have made it the
         loudest background in the app. 0.50 -> 0.20 keeps it exactly as quiet. */
      ctx.fillStyle = pal.faint;
      ctx.globalAlpha = 0.20;
      for (let i = 0; i < cols; i++) {
        const X = (c0 + i) * GRID;
        for (let j = 0; j < rows; j++) {
          ctx.fillRect(X - 0.5, (r0 + j) * GRID - 0.5, 1, 1);
        }
      }
      ctx.globalAlpha = 1;
    }

    /* Boards go down before the wires and before the parts, because that is the order
       they go down on a desk: the board is the ground everything else is built on. A
       jumper drawn across one has to be visible ON it, and a resistor plugged into it
       has to be visible IN it — both of which a body painted in part order would
       cover, since the parts pass runs after the wires and in whatever order the
       learner happened to place things. */
    cur.parts.forEach(function (p) {
      if (p.kind === 'BB') drawBoard(p, selIds.has(p.id) ? pal.accent : null, pal);
    });

    /* wires — a selected one in the same accent a selected part takes, and thicker,
       since a two-pixel line changing colour is not enough to see on a busy drawing */
    ctx.lineWidth = 2;
    cur.wires.forEach(function (wr) {
      const on = selWires.has(wireKey(wr));
      ctx.strokeStyle = on ? pal.accent : pal.dim;
      ctx.lineWidth = on ? 4 : 2;
      ctx.beginPath();
      ctx.moveTo(gx(wr.a[0]), gy(wr.a[1]));
      ctx.lineTo(gx(wr.b[0]), gy(wr.b[1]));
      ctx.stroke();
    });
    ctx.lineWidth = 2;

    /* junction dots where three or more things meet */
    const count = {};
    function bump(pt) { const k = pt[0] + ',' + pt[1]; count[k] = (count[k] || 0) + 1; }
    cur.wires.forEach(function (wr) { bump(wr.a); bump(wr.b); });
    cur.parts.forEach(function (p) { Netlist.pinsOf(p).forEach(bump); });
    ctx.fillStyle = pal.dim;
    Object.keys(count).forEach(function (k) {
      if (count[k] < 3) return;
      const xy = k.split(',').map(Number);
      ctx.beginPath();
      ctx.arc(gx(xy[0]), gy(xy[1]), 3, 0, Math.PI * 2);
      ctx.fill();
    });

    /* parts */
    cur.parts.forEach(function (p) {
      if (p.kind === 'BB') return;              /* already down, under the wires */
      drawPart(p, selIds.has(p.id) ? pal.accent : pal.ink, pal);
    });

    paintMarquee();

    /* The wire being drawn, from whichever of the two pointers is live. The caret is
       second so a mouse still wins while it is on the canvas. */
    const lead = hover || (cvFocused && caretByKey ? caret : null);
    if (wireFrom && lead) {
      ctx.save();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = pal.accent;
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(gx(wireFrom[0]), gy(wireFrom[1]));
      /* The preview is the wire that would be made, corner and all, rather than the
         single straight segment it used to show — which meant a diagonal drag drew
         one line and committed another. */
      elbow(wireFrom, lead).forEach(function (seg) {
        ctx.lineTo(gx(seg[1][0]), gy(seg[1][1]));
      });
      ctx.stroke();
      ctx.restore();
      /* where it would land */
      const tgt = connAt(lead);
      if (tgt) {
        ctx.save();
        ctx.strokeStyle = pal.accent;
        ctx.lineWidth = 2 / view.s;
        ctx.beginPath();
        ctx.arc(gx(lead[0]), gy(lead[1]), GRID * 0.3, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }
    }

    /* The ring that says a wire can start here. It is the whole of the discoverability
       for wiring: without it the only way to learn that terminals are special is to be
       told, and nothing on the canvas was doing the telling. Drawn at a constant size
       on screen rather than in world units, so it stays a target you can hit at any
       zoom. A hollow ring on a pin, a filled dot on a wire — the second is a branch
       off something already drawn, and it makes a junction. */
    if (hoverConn && !wireFrom) {
      ctx.save();
      ctx.strokeStyle = pal.accent;
      ctx.fillStyle = pal.accent;
      ctx.lineWidth = 2 / view.s;
      ctx.beginPath();
      ctx.arc(gx(hoverConn.pt[0]), gy(hoverConn.pt[1]), GRID * 0.3, 0, Math.PI * 2);
      if (hoverConn.kind === 'wire') { ctx.globalAlpha = 0.25; ctx.fill(); ctx.globalAlpha = 1; }
      ctx.stroke();
      ctx.restore();
    }

    /* The caret. A ring rather than a filled cell, because what matters is the cell it
       is around and not the mark itself, and drawn from `accent` so it carries the same
       contrast on this ground as everything else the learner is meant to see. */
    if (cvFocused && caret && caretByKey) {
      ctx.save();
      ctx.strokeStyle = pal.accent;
      ctx.lineWidth = 2 / view.s;
      ctx.beginPath();
      ctx.arc(gx(caret[0]), gy(caret[1]), GRID * 0.44, 0, Math.PI * 2);
      ctx.stroke();
      ctx.setLineDash([3 / view.s, 3 / view.s]);
      ctx.lineWidth = 1 / view.s;
      ctx.beginPath();
      ctx.moveTo(gx(caret[0]) - GRID * 0.8, gy(caret[1]));
      ctx.lineTo(gx(caret[0]) + GRID * 0.8, gy(caret[1]));
      ctx.moveTo(gx(caret[0]), gy(caret[1]) - GRID * 0.8);
      ctx.lineTo(gx(caret[0]), gy(caret[1]) + GRID * 0.8);
      ctx.stroke();
      ctx.restore();
    }

    /* DC answers, written on the schematic where they belong */
    if (result && result.kind === 'dc' && result.net) {
      ctx.font = '10.5px ui-monospace, monospace';
      ctx.textAlign = 'left';
      const at = prefix();
      const seen = {};
      cur.parts.forEach(function (p) {
        Netlist.pinsOf(p).forEach(function (pt) {
          const n = result.net.nodeAt(pt, at);
          if (n === null || n === 0 || seen[n]) return;
          seen[n] = 1;
          ctx.fillStyle = pal.accent;
          ctx.fillText(fmtEng(result.v[n], 'V'), gx(pt[0]) + 6, gy(pt[1]) - 8);
        });
      });
    }

    /* The hover card goes on last and outside the viewport transform, so it is the
       same size at every zoom and nothing is drawn over it. */
    paintTip(pal, w, h);
    describeCanvas();
  }

  /* One repaint a frame, however fast the input arrives.
   *
   * Every continuous gesture on this canvas — a pan, a wheel, a drag, a rubber band,
   * a resize — repainted synchronously per event, and a pointer can outrun a frame.
   * Measured through the shipped editor: 60 pan moves inside one frame cost 61 full
   * repaints and 40 wheel notches cost 40, while one repaint at the 0.3 zoom floor on a
   * 1200x800 canvas was 13478 fillRect calls. The solver has been coalesced through
   * perFrame since it was written, for exactly this reason; the drawing never was.
   *
   * Discrete actions keep calling paint() directly. Placing a part, pressing Escape or
   * tabbing away happen once, and there is nothing to collapse — deferring them only
   * makes them later. */
  const paintSoon = perFrame(function () { paint(); });

  /* What the canvas calls itself, rebuilt from what was just drawn.
   *
   * role="application" with a fixed name is what this was: "Schematic canvas. Press
   * Enter for the key map." on an empty canvas and on a finished twelve-part filter
   * alike — measured, unchanged across placing parts. The status line announces each
   * action as it happens, which serves somebody who is doing the actions and nobody who
   * arrives at the canvas afterwards: a learner returning to saved work, or tabbing back
   * from the value box, had no way to ask what is on the drawing. Cycle 8 gave the
   * analysis plot a name built out of the arrays its curve was drawn from; this is the
   * same rule on the other canvas.
   *
   * Not a live region, deliberately, and for the reason the plot's is not: a name that
   * re-announced itself on every frame of a drag would make the editor unusable. It is
   * there to be asked. */
  let lastName = null;
  function describeCanvas() {
    if (ro_) return;                    /* a diagram carries the label its author wrote */
    const np = cur.parts.length, nw = cur.wires.length;
    let s = 'Schematic canvas. ';
    s += np ? np + (np === 1 ? ' part' : ' parts') : 'No parts';
    s += nw ? ' and ' + nw + (nw === 1 ? ' wire. ' : ' wires. ') : '. ';
    if (path.length) s += 'Inside a block, ' + path.length + ' deep. ';
    if (selIds.size) s += selIds.size + ' selected. ';
    s += 'Zoom ' + Math.round(view.s * 100) + ' per cent. Press Enter for the key map.';
    /* Written only when it moves. Setting an attribute to the value it already holds is
       a mutation a screen reader can react to, and this runs on every frame of a drag. */
    if (s !== lastName) { cv.setAttribute('aria-label', s); lastName = s; }
  }

  /* What a block says about itself when you point at it. Drawn here rather than left
     to the browser's own tooltip because the title attribute waits the best part of a
     second, shows one run of text in a font nobody chose, and would be the only place
     in this editor where something the learner wrote is displayed by the platform
     rather than by the drawing. */
  function paintTip(pal, w, h) {
    const b = hoverSp && tipBlock();
    if (!b) return;
    const title = String(b.title || 'Block');
    const desc = String(b.desc || '').trim();
    /* Saved and restored around the lot, transform included, because everything below
       is set for a card and nothing below is set for a schematic — and the parts of
       the NEXT frame are drawn before anything here is set again. A font left behind
       here comes back as a part label in the wrong place. */
    ctx.save();
    /* back to screen pixels, whatever the viewport was doing */
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const PAD = 8, MAXW = 230;
    ctx.font = 'bold 11.5px ui-monospace, monospace';
    let width = Math.min(Math.max(ctx.measureText(title).width, 90), MAXW);
    ctx.font = '11px ui-monospace, monospace';
    const lines = desc
      ? wrapText(desc, MAXW)
      : ['Double-click to open it. Describe it in the panel.'];
    lines.forEach(function (l) { width = Math.max(width, Math.min(ctx.measureText(l).width, MAXW)); });
    const bh = PAD * 2 + 15 + lines.length * 14;
    const bw = width + PAD * 2;
    /* kept on the canvas: a card that runs off the edge is a card half of which was
       written for nobody */
    const tx = Math.min(hoverSp[0] + 14, Math.max(4, w - bw - 4));
    const ty = Math.min(hoverSp[1] + 16, Math.max(4, h - bh - 4));

    ctx.globalAlpha = 0.97;
    ctx.fillStyle = pal.surface || '#0A0B0E';
    ctx.fillRect(tx, ty, bw, bh);
    ctx.globalAlpha = 1;
    ctx.strokeStyle = pal.accent;
    ctx.lineWidth = 1;
    ctx.strokeRect(tx + 0.5, ty + 0.5, bw - 1, bh - 1);

    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = pal.accent;
    ctx.font = 'bold 11.5px ui-monospace, monospace';
    ctx.fillText(title, tx + PAD, ty + PAD + 11);
    ctx.fillStyle = desc ? pal.ink : pal.dim;
    ctx.font = '11px ui-monospace, monospace';
    lines.forEach(function (l, i) { ctx.fillText(l, tx + PAD, ty + PAD + 26 + i * 14); });
    ctx.restore();
  }

  /* Greedy wrap against the font already selected on the context. Long enough for a
     paragraph and no longer: a description that fills the canvas is a panel, and the
     panel is where the whole of it lives. */
  function wrapText(text, maxw) {
    const words = text.split(/\s+/);
    const out = [];
    let line = '';
    for (let i = 0; i < words.length && out.length < 8; i++) {
      const test = line ? line + ' ' + words[i] : words[i];
      if (ctx.measureText(test).width > maxw && line) { out.push(line); line = words[i]; }
      else line = test;
    }
    if (line && out.length < 8) out.push(line);
    else if (line) out[out.length - 1] += ' …';
    return out;
  }

  /* The block under the pointer, if the pointer is over one and doing nothing else. A
     card that follows you through a drag is a card in the way. */
  function tipBlock() {
    if (drag || marquee || panFrom || wireFrom || !hover) return null;
    const hit = partAt(hover);
    return hit && hit.kind === 'IC' ? hit : null;
  }

  /* ---- panels ---- */
  function paintMarquee() {
    if (!marquee) return;
    const a = marquee.a, b = marquee.b;
    const x = Math.min(a[0], b[0]), y = Math.min(a[1], b[1]);
    ctx.save();
    ctx.strokeStyle = P().accent;
    ctx.setLineDash([4, 3]);
    ctx.lineWidth = 1 / view.s;
    ctx.strokeRect(x, y, Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1]));
    ctx.restore();
  }

  function paintPart() {
    const p = selOne();
    if (selIds.size > 1) {
      partPanel.innerHTML = '<h4>' + selIds.size + ' parts selected</h4>' +
        '<p class="ckt-hint">Drag to move them together. R rotates, Delete removes. ' +
        'G folds them into one block, whose pins are worked out from which nets cross ' +
        'the edge of the selection; U opens any block among them back out. ' +
        'Click an empty cell to deselect.</p>';
      return;
    }
    if (p && p.kind === 'IC') { paintBlock(p); return; }
    if (p && p.kind === 'MCU') { paintMcu(p); return; }
    if (!p || p.kind === 'GND' || p.kind === 'OUT') {
      /* The keyboard route is written where a sighted keyboard learner will actually
         meet it. The same map is on the canvas's own description for a screen reader,
         and the two are kept short enough to stay in step. */
      partPanel.innerHTML = '<h4>Component</h4><p class="ckt-hint">' +
        (tool === 'wire' ? 'Click a pin, then click where the wire should end.'
          : tool === 'select' ? 'Click a component to select it.'
          : 'Click the grid to place a ' + PART_KINDS[tool].name.toLowerCase() + '.') +
        ' Or tab to the canvas and use the arrow keys: Enter does what a click does, ' +
        'Shift with an arrow moves what is selected, and Escape lets go.</p>';
      return;
    }
    const k = PART_KINDS[p.kind];
    partPanel.innerHTML = '<h4>' + k.name + ' ' + esc2(refOf(p)) + '</h4>' +
      (p.kind === 'SW'
        ? '<button class="ckt-t" data-sw style="width:100%;margin-bottom:8px">' +
          (p.closed ? 'Closed — click to open' : 'Open — click to close') + '</button>'
        : '<label class="ckt-f"><span>' + esc2(VALUE_LABEL[p.kind] || ('Value (' + k.unit + ')')) + '</span>' +
          '<input data-val value="' + esc2(fmtEng(p.value, '').trim()) + '"></label>') +
      (PART_FIELDS[p.kind] || []).map(function (f) {
        const cur = p[f[0]] === undefined ? PART_KINDS[p.kind].state[f[0]] : p[f[0]];
        return '<label class="ckt-f"><span>' + esc2(f[1]) + '</span>' +
          '<input data-x="' + f[0] + '" value="' + esc2(String(cur)) + '"></label>';
      }).join('') +
      (p.kind === 'POT'
        ? '<div class="ckt-f" style="grid-template-columns:auto 1fr auto">' +
          /* The slider carries thousandths so the drag is smooth; the label beside it,
             the model and the note all speak in the 0..1 the wiper actually is. A range
             input announces its own raw value, so without aria-valuetext this control
             reads "500" to a screen reader and "0.50" to everyone else. */
          '<span>Wiper</span><input type="range" data-wiper min="0" max="1000" step="1" ' +
          'aria-label="Wiper position, 0 to 1" aria-valuetext="' +
          (p.wiper === undefined ? 0.5 : p.wiper).toFixed(2) + '" value="' +
          Math.round((p.wiper === undefined ? 0.5 : p.wiper) * 1000) +
          '" style="height:18px;padding:0;border:0;background:none;accent-color:var(--lime);width:100%">' +
          '<span data-wiperval style="color:var(--accent-ink)">' +
          (p.wiper === undefined ? 0.5 : p.wiper).toFixed(2) + '</span></div>'
        : '') +
      '<p class="ckt-hint" data-note>' + modelNote(p) + '</p>' + boardShortNote(p);

    const inp = partPanel.querySelector('[data-val]');
    /* Named, because it now runs from two places: the blur that always ran it, and the
       flush that catches a value typed and never blurred. It reads inp.value when it
       runs rather than when it was scheduled, so what is committed is what is in the
       box — including after the panel has been rebuilt around a different part, in
       which case the repaint and the announcement stand down and only the write to
       THIS part's model happens. */
    function commitValue() {
      /* Every OTHER field on this panel is clamped to the range its kind declares, two
         lines below. The value box — the one field every part has — was not, so a
         resistance of 0 or of −5 was accepted, written into the model, and saved. The
         stamps guard themselves (`1 / Math.max(p.value, 1e-12)`), so what shipped was
         worse than a crash: the solver quietly treated it as a 1 pΩ short while the
         panel beside it went on reading −5 Ω, and the learner's own saved circuit was
         the one lying to them. */
      const want = parseEng(inp.value, p.value);
      p.value = clampValue(p.kind, want, p.value);
      changed();
      /* The repaint is what puts the real value back in the box after "nonsense" was
         typed into it, so it happens whether or not the number moved — but only while
         this is still the part on the panel. */
      const mine = selOne() === p;
      if (mine) paintPart();
      if (p.value !== want && mine) {
        const who = 'A ' + (PART_KINDS[p.kind].name || p.kind).toLowerCase() + ' ';
        /* Which end it hit, and why that end is there. "Out of range" would be a
           correction the learner cannot learn anything from — the point of saying it
           out loud at all is that the reason is different at each end: nothing is a
           resistance at zero, and nothing survives being divided by a time step at
           1e308. Asked of the CEILING and not of the two magnitudes, because −5 Ω is
           larger than the floor it lands on and would have been told it was too big. */
        const ceil = VALUE_CEIL[p.kind];
        announce(ceil !== undefined && Math.abs(want) > ceil
          ? who + 'that large is past what the arithmetic can hold once the solver ' +
            'divides it by a time step, so this is now ' + fmtEng(p.value, k.unit) + '.'
          : who + 'has to be more than zero, so this is now ' + fmtEng(p.value, k.unit) + '.');
      }
    }
    if (inp) {
      /* Typing only STAGES. Committing per keystroke would clamp "4" on the way to
         "4.7k" and rewrite the box under the typist — which is why this was on `change`
         in the first place, and why the fix is a flush rather than a move to `input`. */
      inp.addEventListener('input', function () { editSoon(commitValue); });
      inp.addEventListener('change', function () { pendingEdit = commitValue; flushEdit(); });
    }
    partPanel.querySelectorAll('[data-x]').forEach(function (el) {
      function commitField() {
        const f = (PART_FIELDS[p.kind] || []).filter(function (q) { return q[0] === el.dataset.x; })[0];
        if (!f) return;
        const v = parseEng(el.value, p[el.dataset.x]);
        p[el.dataset.x] = Math.min(Math.max(isFinite(v) ? v : f[2], f[2]), f[3]);
        changed();
        if (selOne() === p) paintPart();
      }
      /* The same staging, for the same reason: a γ or a βF typed and never blurred was
         lost exactly as a resistance was. */
      el.addEventListener('input', function () { editSoon(commitField); });
      el.addEventListener('change', function () { pendingEdit = commitField; flushEdit(); });
    });
    const sw = partPanel.querySelector('[data-sw]');
    if (sw) sw.addEventListener('click', function () { toggleSwitch(p); });
    const wip = partPanel.querySelector('[data-wiper]');
    if (wip) wip.addEventListener('input', function () {
      p.wiper = Math.min(Math.max(+wip.value / 1000, 0), 1);
      partPanel.querySelector('[data-wiperval]').textContent = p.wiper.toFixed(2);
      wip.setAttribute('aria-valuetext', p.wiper.toFixed(2));
      /* The note quotes the two stamped resistances, so it goes stale the instant the
         wiper moves — and it is the one label that exists so the learner can read the
         model rather than trust it. Rewritten in place rather than through
         paintPart(), which would rebuild the slider out from under the pointer. */
      refreshNote();
      retouchSoon();
    });
  }

  /* Both ends of a part in the SAME strip is the mistake every first breadboard
     produces, and it is the one mistake this canvas cannot draw: the short is under the
     board, and there is no wire on the screen for the eye to catch. So the panel says
     it in words, which is the only place left to say it. */
  function boardShortNote(p) {
    const pins = Netlist.pinsOf(p);
    if (pins.length < 2) return '';
    let where = null;
    cur.parts.forEach(function (b) {
      if (b.kind !== 'BB' || where) return;
      const seen = {};
      pins.forEach(function (pt) {
        const s = bbStripAt(b, pt[0], pt[1]);
        if (s === null) return;
        if (seen[s]) where = s; else seen[s] = 1;
      });
    });
    if (!where) return '';
    return '<p class="ckt-hint" style="color:var(--amber,#FFC66D)">Both ends of this are ' +
      'in one strip of the board, which has therefore shorted it out — a strip is five ' +
      'holes and all five are the same node. ' +
      (where.indexOf('rail') === 0
        ? 'That strip is a power rail, and a rail runs the whole length of the board, so ' +
          'moving along it will not help: bring one end off the rail.'
        : 'Move one end to the next column along, or over the channel into the other half.') +
      '</p>';
  }

  /* A block has no value to type, so its panel is the one place the two things only a
     person can supply are written: what this piece of circuit is called and what it is
     for. The title is defaulted rather than left empty — "Block 3" is at least true,
     and an unnamed rectangle on a schematic is worse than a dully named one. The
     description is where the reason lives, and it is the reason a block is worth
     having at all: the rectangle hides the parts, and only the words say why hiding
     them was the right idea. */
  function paintBlock(p) {
    const pins = (p.ports || []).length;
    const held = ((p.inner && p.inner.parts) || []).length;
    partPanel.innerHTML = '<h4>' + esc2(refOf(p)) + '</h4>' +
      '<label class="ckt-f"><span>Title</span>' +
      '<input data-title value="' + esc2(p.title || '') + '"></label>' +
      '<div class="ckt-f" style="grid-template-columns:1fr;align-items:stretch">' +
      '<span>Description</span>' +
      '<textarea data-desc rows="4" style="width:100%;padding:6px 8px;border-radius:var(--r);' +
      'border:1px solid var(--line-2);background:var(--surface-2,transparent);color:inherit;' +
      'font:inherit;font-size:12px;line-height:1.5;resize:vertical">' +
      esc2(p.desc || '') + '</textarea></div>' +
      '<div style="display:flex;gap:6px;margin-bottom:8px">' +
      '<button class="ckt-t" data-open style="flex:1">Open</button>' +
      '<button class="ckt-t" data-ungroup style="flex:1">Ungroup</button></div>' +
      '<p class="ckt-hint">' + held + (held === 1 ? ' part' : ' parts') + ' inside, behind ' +
      pins + (pins === 1 ? ' pin' : ' pins') + '. The pins are not a list anyone typed: ' +
      'they are the nets that had a connection inside the selection and a connection ' +
      'outside it when it was folded up, and they sit on the very cells those crossings ' +
      'were on — so grouping and ungrouping leave the circuit solving exactly as it did. ' +
      'Nothing about a block reaches the solver; it is flattened back out before a single ' +
      'node is numbered.</p>' +
      (pins
        ? '<p class="ckt-hint" style="margin-top:8px">Pins, in the order they are drawn:</p>' +
          (p.ports || []).map(function (port, i) {
            return '<label class="ckt-f"><span>Pin ' + (i + 1) + '</span>' +
              '<input data-port="' + i + '" value="' + esc2(port.name) + '"></label>';
          }).join('')
        : '<p class="ckt-hint" style="margin-top:8px">No pins at all — nothing outside this ' +
          'block is wired to anything inside it, so it is a circuit of its own sitting on ' +
          'the same canvas. That is legal, and it is usually a wire you meant to draw.</p>');

    const t = partPanel.querySelector('[data-title]');
    t.addEventListener('input', function () {
      p.title = t.value;
      paintCrumbs();
      paint();
    });
    /* A rename changes no connection and no value, so the answer on the canvas is
       still the answer: retouch saves it and re-solves in place rather than throwing
       the solution away the way an edit to the drawing does. */
    t.addEventListener('change', function () { retouch(); });
    const d = partPanel.querySelector('[data-desc]');
    d.addEventListener('change', function () { p.desc = d.value; retouch(); });
    d.addEventListener('input', function () { p.desc = d.value; });
    partPanel.querySelectorAll('[data-port]').forEach(function (el) {
      el.addEventListener('input', function () {
        p.ports[+el.dataset.port].name = el.value;
        paint();
      });
      el.addEventListener('change', function () { retouch(); });
    });
    partPanel.querySelector('[data-open]').addEventListener('click', function () { openBlock(p); });
    partPanel.querySelector('[data-ungroup]').addEventListener('click', doUngroup);
  }

  /* ---- the sketch, its console, and its faults ----
   *
   * The one panel in this file whose subject is not a number. A learner debugging here
   * is holding two things that could be wrong — the sketch and the circuit — and every
   * decision below is about telling those two apart. The sketch is checked as it is
   * typed, so a syntax error is reported before any run and can never be mistaken for a
   * circuit that would not solve. A fault at run time names its line. And the console is
   * kept separate from the solver's own output pane, because "my program printed this"
   * and "the solver could not converge" are not the same kind of sentence.
   */
  function mcuRigFor(p) {
    if (!mcuRun) return null;
    const id = prefix() + p.id;
    return mcuRun.rigs.filter(function (r) { return r.id === id; })[0] || null;
  }

  function faultLine(f) {
    return '<div class="ckt-err">' + (f.line ? 'Line ' + f.line + ': ' : '') +
      esc2(f.message) + '</div>';
  }

  function paintMcu(p) {
    const code = typeof p.code === 'string' ? p.code : MCU_SKETCH;
    const gone = !mcuAvailable();
    const built = gone ? null : MCU.compile(code);
    const rig = mcuRigFor(p);
    const st = rig && rig.machine ? rig.machine.state() : null;
    /* Ids have to be unique in the DOCUMENT, not in this editor: a lesson can hold a
       diagram and a playground at once, and two boxes both called "mcu-code" make
       aria-describedby point at whichever the document happens to hold first. */
    const uid = 'mcu' + (++MCU_PANEL_SEQ);

    partPanel.innerHTML = '<h4>Microcontroller ' + esc2(refOf(p)) + '</h4>' +
      (gone
        ? '<div class="ckt-err">The interpreter (src/mcu.js) is not in this build, so ' +
          'this part can be drawn and wired but not run. Its pins stamp at reset — every ' +
          'one an input — which is what a board with power and no program does.</div>'
        : '') +
      /* A <label>, as every other field on this panel already is. The sketch box was
         the one control here captioned by a bare <span> — a legend for the eye and
         nothing at all for the accessibility tree, so the largest and most important
         input in the editor read as an unlabelled textarea. */
      '<label class="ckt-f" for="' + uid + '" style="grid-template-columns:1fr;align-items:stretch">' +
      '<span>Sketch</span>' +
      '<textarea id="' + uid + '" data-code rows="14" spellcheck="false" ' +
      'aria-describedby="' + uid + '-err" aria-invalid="' + (built && built.error ? 'true' : 'false') + '" ' +
      'style="width:100%;padding:6px 8px;' +
      'border-radius:var(--r);border:1px solid var(--line-2);background:var(--surface-2,transparent);' +
      'color:inherit;font-family:var(--mono,ui-monospace,monospace);font-size:11px;line-height:1.5;' +
      'resize:vertical;white-space:pre;overflow-wrap:normal;overflow-x:auto">' +
      esc2(code) + '</textarea></label>' +
      /* The syntax error is the one thing on this panel that changes while the learner
         is typing, and it was written into a plain <div>: on screen the moment a
         bracket was missed, and silent to a screen reader for ever. A live region, and
         a polite one — see the debounce on the handler below for why it is not written
         on every keystroke. */
      '<div data-built id="' + uid + '-err" role="status" aria-live="polite">' +
      (built && built.error ? faultLine(built.error) : '') + '</div>' +
      (st && st.fault ? faultLine(st.fault) : '') +
      (st && !st.fault
        ? '<p class="ckt-hint">' +
          (st.done ? 'Finished: there is no loop(), so the sketch ran once and stopped. '
            : st.inSetup ? 'Still inside setup() when the run ended. '
            : st.loops + (st.loops === 1 ? ' iteration' : ' iterations') + ' of loop(). ') +
          st.ops.toLocaleString() + ' instructions, ' + mcuRun.ops() +
          ' per time step.' + (st.dropped ? ' ' + st.dropped + ' console lines dropped.' : '') +
          /* Two caps, so two sentences: a sketch that never prints a newline is cut by
             characters and drops no lines at all, and saying "0 lines dropped" while
             silently throwing away half its output is the defect, not the report. */
          (st.cut ? ' ' + st.cut.toLocaleString() + ' further characters not kept.' : '') +
          '</p>'
        : '') +
      (rig && rig.error ? faultLine(rig.error) : '') +
      mcuConsole(rig, uid) +
      '<p class="ckt-hint" data-note>' + modelNote(p) + '</p>';

    const ta = partPanel.querySelector('[data-code]');
    /* Checked as it is typed and committed on an idle debounce. Three events rather
       than two: `input` keeps the model and schedules the save, the debounce writes
       the diagnosis and the save, and `change` commits at once because a blur is the
       learner already having moved on. */
    let checkTimer = null;
    function diagnose() {
      checkTimer = null;
      /* A repaint between the keystroke and the timer leaves this closure holding a
         textarea the panel no longer contains, and [data-built] would then find the NEW
         box and write the OLD sketch's diagnosis into it. Nothing to clear on dispose
         either: an emptied panel fails this test the same way. */
      if (partPanel.querySelector('[data-code]') !== ta) return;
      const now = mcuAvailable() ? MCU.compile(ta.value) : null;
      const box = partPanel.querySelector('[data-built]');
      if (box) box.innerHTML = now && now.error ? faultLine(now.error) : '';
      ta.setAttribute('aria-invalid', now && now.error ? 'true' : 'false');
    }
    ta.addEventListener('input', function () {
      p.code = ta.value;
      editSoon(function () { changed(); });
      /* Debounced, and the reason is the live region rather than the cost of a compile,
         which is nothing. Most of these messages quote the token they stopped at —
         `found "ab"` one keystroke after `found "a"` — so an immediate live region
         would read a fresh sentence into a screen reader on every letter of a
         half-typed identifier. 500 ms of quiet is what makes it an answer instead of a
         stream, and it is why the box is not repainted on the keystroke either. */
      if (checkTimer) clearTimeout(checkTimer);
      checkTimer = setTimeout(diagnose, 500);
    });
    ta.addEventListener('change', function () {
      p.code = ta.value;
      if (checkTimer) { clearTimeout(checkTimer); diagnose(); }
      /* A blur is the learner having moved on, so this commits at once rather than
         waiting out a debounce they are no longer typing against. */
      pendingEdit = function () { changed(); };
      flushEdit();
    });
  }

  function mcuConsole(rig, uid) {
    if (!rig || !rig.machine) return '';
    const lines = rig.machine.console();
    if (!lines.length) {
      return '<p class="ckt-hint">The sketch printed nothing. print("..."), println(x) ' +
        'and Serial.println(x) all write here.</p>';
    }
    /* tabindex, because this box scrolls. A region that overflows and takes no focus
       can be reached by a mouse wheel and by nothing else — the output of the learner's
       own program, past the first 150px of it, unreachable from a keyboard (WCAG 2.1.1).
       role and a name so that arriving in it by Tab says what it is; NOT a live region,
       because a sketch printing every time step would read hundreds of lines aloud. */
    return '<h4 style="margin-top:10px" id="' + uid + '-con">Console</h4>' +
      '<pre tabindex="0" role="group" aria-labelledby="' + uid + '-con" ' +
      'style="max-height:150px;overflow:auto;' +
      'margin:0 0 8px;padding:6px 8px;border-radius:var(--r);border:1px solid var(--line-2);' +
      'font-family:var(--mono,ui-monospace,monospace);font-size:11px;line-height:1.5;' +
      'white-space:pre-wrap">' + esc2(lines.join('\n')) + '</pre>';
  }

  /* What the value box means for a kind whose value is not simply "the value". */
  const VALUE_LABEL = bareTable({
    LDR: 'R at 10 lx (Ω)', NTC: 'R at 25 °C (Ω)', POT: 'Total (Ω)',
    BB: 'Columns',
    LAMP: 'Resistance (Ω)', METER: 'Burden (Ω)', BAR: 'Full scale (V)',
    D: 'Is (A)', LED: 'Is (A)', NPN: 'Is (A)', PNP: 'Is (A)',
    NMOS: 'k (A/V²)', PMOS: 'k (A/V²)', OPAMP: 'Open-loop gain',
  });
  /* The extra numbers a kind carries beyond `value`: key, label, and the range it is
     clamped to, because a γ of zero or a negative B is a model that means nothing. */
  const PART_FIELDS = bareTable({
    LDR: [['gamma', 'γ slope', 0.05, 3]],
    NTC: [['beta', 'B (K)', 1, 20000]],
    LAMP: [['pnom', 'Full at (W)', 1e-9, 1e6]],
    D: [['n', 'Ideality n', 0.5, 4]],
    LED: [['n', 'Ideality n', 0.5, 4], ['inom', 'Full at (A)', 1e-6, 1]],
    NPN: [['bf', 'βF forward', 1, 5000], ['br', 'βR reverse', 0.01, 100]],
    PNP: [['bf', 'βF forward', 1, 5000], ['br', 'βR reverse', 0.01, 100]],
    NMOS: [['vth', 'Vth (V)', 0.05, 20], ['lambda', 'λ (1/V)', 0, 1]],
    PMOS: [['vth', 'Vth (V)', 0.05, 20], ['lambda', 'λ (1/V)', 0, 1]],
    OPAMP: [['vpos', 'V+ rail (V)', -100, 100], ['vneg', 'V− rail (V)', -100, 100]],
  });

  /* The model, written where the learner can read it. A sensor whose curve you have
     to take on trust is a magic box, and a magic box teaches nothing — so each of
     these states the equation, its parameters, and what it does NOT model. */
  function modelNote(p) {
    const n = p.id.replace('p', '');
    if (p.kind === 'MCU') {
      /* Longer than any other note here, and deliberately: a microcontroller makes more
         claims than any other part on this canvas, and every one of them is a place a
         learner could be misled. Each paragraph states a number and then states what the
         number does NOT cover. */
      return 'Vcc is ' + fmtEng(MCU_VCC, 'V') + ' and every pin is referenced to this ' +
        'part\'s own GND pin, never to the circuit\'s ground — so an output at LOW is ' +
        fmtEng(MCU_ROUT, 'Ω') + ' to that pin and not a wire to ground. Wire GND, or the ' +
        'whole part floats and the solver says so.<br><br>' +

        'An OUTPUT is a source at ' + fmtEng(MCU_VCC, 'V') + ' or 0 V behind ' +
        fmtEng(MCU_ROUT, 'Ω') + ', which is what limits the current it can pass: an LED ' +
        'straight to ground draws about ' + fmtEng(MCU_VCC / MCU_ROUT, 'A') + ' at most, ' +
        'and that is the reason for the resistor, not a rule of thumb.<br><br>' +

        'An INPUT is ' + fmtEng(MCU_RIN, 'Ω') + ' to GND and reads through a Schmitt ' +
        'trigger: above ' + fmtEng(MCU_VIH, 'V') + ' it reads 1, below ' +
        fmtEng(MCU_VIL, 'V') + ' it reads 0, and between the two it reads whatever it read ' +
        'last. INPUT_PULLUP adds ' + fmtEng(MCU_RPULL, 'Ω') + ' up to Vcc, which is what ' +
        'makes a button to ground work with no other components.<br><br>' +

        'analogRead gives ' + MCU_ADC_BITS + ' bits, 0 to ' + MCU_ADC_MAX + ', against Vcc ' +
        'as the reference — so one count is ' + fmtEng(MCU_VCC / (MCU_ADC_MAX + 1), 'V') +
        ' and the reading is a FRACTION of the supply rather than a voltage. There is no ' +
        'sampling time, no input capacitance and no conversion delay: the count is taken ' +
        'from the solved node voltage at that instant.<br><br>' +

        'analogWrite stamps the MEAN of the pulse train, duty/255 of Vcc, and not a ' +
        'switching waveform. A filter or an LED responds to that mean and the answer here ' +
        'is right; anything that responds within one PWM period — a scope on the pin, a ' +
        'motor commutating, a second logic input reading it — is not modelled at all, and ' +
        'this would show it a steady voltage that never exists.<br><br>' +

        'The Vcc pin supplies ' + fmtEng(MCU_VCC, 'V') + ' through ' +
        fmtEng(MCU_RSUP, 'Ω') + '. There is no current limit and no brown-out: load it ' +
        'hard enough and it will sag, which is honest, but nothing will reset.<br><br>' +

        'On the drawing, a filled pin is one pushing current — an output, a pull-up, or ' +
        'a power pin — and a hollow one is only listening. H, L and a percentage are ' +
        'where the sketch LEFT that pin when the run ended, not where it sat throughout: ' +
        'a blinking pin shows whichever half of the blink the last time step landed in. ' +
        'The plot is where the history is.<br><br>' +

        'The sketch runs only during a TRANSIENT. In the operating point and the ' +
        'frequency sweep every pin is stamped at reset — an input, high impedance — ' +
        'because a program is a thing that happens over time and neither of those ' +
        'analyses has any.' +
        (mcuAvailable()
          ? '<br><br>It runs at ' + MCU.OPS_PER_SECOND.toLocaleString() + ' operations per ' +
            'second of simulated time, suspended between steps so an endless loop() costs ' +
            'nothing. An operation is one statement or one operator, which no real ' +
            'processor charges alike; the rate is stated rather than realistic. delay() ' +
            'and millis() run on the simulation clock, so their resolution is the time ' +
            'step. A pin written during one step reaches the matrix at the next.'
          : '');
    }
    if (p.kind === 'SW') {
      return 'A state, not a value. Closed stamps ' + fmtEng(SW_ON, 'Ω') + '; open stamps ' +
        fmtEng(SW_OFF, 'Ω') + ' rather than deleting the branch, so whatever hangs off the far ' +
        'side still has a defined voltage instead of the solver calling the circuit ' +
        'under-determined. Click the switch on the canvas to toggle it.';
    }
    if (p.kind === 'LDR') {
      return 'R = R₁₀ · (10 lx / E)^γ — the photoresistor power law, R₁₀ being the resistance ' +
        'at the 10 lx a datasheet quotes. More light, less resistance. At E = ' +
        fmtEng(env.lux, 'lx') + ' this one is ' + fmtEng(ohmsOf(p, env), 'Ω') +
        '. Drag the light slider and watch it move.';
    }
    if (p.kind === 'NTC') {
      return 'R = R₂₅ · exp(B · (1/T − 1/298.15)), T in kelvin — the beta model. B > 0 makes ' +
        'the exponent negative as T rises, so resistance FALLS with heat, which is what the N ' +
        'in NTC means. It is a two-point fit, worth a few percent over a 50 K span and no more; ' +
        'Steinhart–Hart is what you reach for beyond that. At ' + env.tempC.toFixed(1) +
        ' °C this one is ' + fmtEng(ohmsOf(p, env), 'Ω') + '.';
    }
    if (p.kind === 'POT') {
      const rr = potSplit(p);
      return 'Three pins, stamped as two resistances sharing the wiper node: ' +
        fmtEng(rr[0], 'Ω') + ' from the first pin to the wiper and ' + fmtEng(rr[1], 'Ω') +
        ' from the wiper to the second. The wiper is the third pin, leaving the body at ' +
        'right angles to the track — ' + pinWords(p)[2] + ' it as drawn.';
    }
    if (p.kind === 'LAMP') {
      const pw = lampPower(p);
      return 'An ordinary resistance to the solver. The brightness is drawn from the power in ' +
        'it, P = V²/R, against ' + fmtEng(p.pnom === undefined ? 0.25 : p.pnom, 'W') +
        ' for full brightness' + (pw === null ? '' : '; right now P = ' + fmtEng(pw, 'W')) +
        '. Nothing here is non-linear: a real filament\'s resistance climbs as it heats, and ' +
        'that is not modelled.';
    }
    if (p.kind === 'METER') {
      const u = acrossOf(p);
      return 'An ammeter goes IN SERIES: break the branch and put it in the gap. It reads the ' +
        'current through itself as V / ' + fmtEng(p.value, 'Ω') + ', positive from the ' +
        pinWords(p)[0] + ' pin to the ' + pinWords(p)[1] +
        ' — the arrow says which way' + (u === null ? '' : '; now ' + fmtEng(u / Math.max(p.value, 1e-6), 'A')) +
        '. The burden resistance is honest rather than ideal: it is what the measurement costs ' +
        'the circuit, and it keeps the meter a resistor the linear solver already understands.';
    }
    if (p.kind === 'BAR') {
      const v = dcAt([p.x, p.y]);
      return 'Reads the node it sits on, against ground, and takes no part in the solution — ' +
        'placing it changes no answer. The bar fills from 0 to the full scale; past that it ' +
        'gets a caret rather than a full bar that quietly lies, and a negative voltage reads ' +
        'in amber with the bar empty' + (v === null ? '. Solve to give it something to show.' :
        ', and it is showing ' + fmtEng(v, 'V') + ' now.');
    }
    if (p.kind === 'BB') {
      return 'Not a component: it is connection without wire, and the one part on this ' +
        'canvas that carries no current at all. A terminal strip is five holes in a ' +
        'column and all five are one node before anything is put in them. The channel ' +
        'down the middle is what makes the upper half of a column and the lower half two ' +
        'nodes instead of one — which is the gap a DIP is built to straddle, and why ' +
        'a part bridging it lands one end in each. The four stripes are rails, and each ' +
        'one runs the whole length. A pin joins a strip by sitting on its hole, which is ' +
        'the same test that decides whether a pin meets a wire, so there is no second ' +
        'rule here to learn. Nothing is stamped: a strip nothing reaches is not a node, ' +
        'so a board may lie under a half-built circuit without the solver ever calling ' +
        'it under-determined. This one is ' + bbCols(p) + ' columns wide.';
    }
    /* ---- the non-linear parts ----
       Every one of these states its equation, its parameters, and what it leaves out.
       The last of those is the part that matters: a learner told that Ebers-Moll has no
       Early effect has learnt something about bipolars, and one who is not told has
       quietly learnt that collector current does not depend on Vce, which is false. */
    if (Devices.is(p.kind)) {
      /* the three pin positions, in the words the drawing puts them in */
      const w = pinWords(p), a = w[0], b = w[1], c = w[2];
      const vt = 'Vt = ' + (Devices.VT * 1000).toFixed(2) + ' mV, which is kT/q at ' +
        Devices.T_NOM + ' K';
      const op = deviceOp(p);

      if (p.kind === 'D' || p.kind === 'LED') {
        const nn = param(p, 'n', 0.5, 4);
        const at = p.kind === 'LED' ? param(p, 'inom', 1e-6, 1) : 1e-3;
        return 'Shockley: I = Is·(exp(V / (n·Vt)) − 1), with Is = ' + fmtEng(p.value, 'A') +
          ', n = ' + nn + ' and ' + vt + '. That puts ' +
          fmtEng(Devices.dropAt(Math.max(p.value, 1e-30), nn, at), 'V') + ' across it at ' +
          fmtEng(at, 'A') + '. The anode is the ' + a + ' pin — the end the triangle points ' +
          'away from. Nothing here is a 0.7 V rule of thumb: the drop you read is the one ' +
          'the current makes, found by iterating until the two agree' +
          (op === null ? '' : ', and right now that is ' + fmtEng(op.v[0] - op.v[1], 'V') +
            ' at ' + fmtEng(op.i[0], 'A')) + '. ' +
          (p.kind === 'LED'
            ? 'It lights on the canvas in proportion to the current through it, against ' +
              fmtEng(at, 'A') + ' for full brightness. Not modelled: the colour, the light ' +
              'itself (that glow is drawn from current, not from photons), junction ' +
              'capacitance, and reverse breakdown — which for a real LED is only a few volts, ' +
              'so this one will happily survive something the part on your desk would not.'
            : 'Not modelled: junction capacitance, so this diode has no switching speed and ' +
              'no reverse recovery; the bulk series resistance, so the curve never straightens ' +
              'out at high current; reverse breakdown, so it is not a Zener however hard you ' +
              'push it backwards; and any temperature but ' + Devices.T_NOM + ' K.');
      }

      if (p.kind === 'NPN' || p.kind === 'PNP') {
        const bf = param(p, 'bf', 1, 5000);
        return 'Ebers-Moll, transport form: Ic = Is·(exp(Vbe/Vt) − exp(Vbc/Vt)) − ' +
          '(Is/βR)·(exp(Vbc/Vt) − 1), and a base current that is each junction\'s own ' +
          'current over its beta. Is = ' + fmtEng(p.value, 'A') + ', βF = ' + bf + ', βR = ' +
          param(p, 'br', 0.01, 100) + ', ' + vt + '. Vbe comes out at ' +
          fmtEng(Devices.dropAt(Math.max(p.value, 1e-30), 1, 1e-3), 'V') + ' for a milliamp ' +
          'of collector current' + (op === null ? '' : '; right now Ic = ' +
            fmtEng(Math.abs(op.i[0]), 'A') + ' and Vbe = ' + fmtEng(Math.abs(op.v[2] - op.v[1]), 'V')) +
          '. Collector is the ' + a + ' pin, emitter the ' + b + ', base on the pin ' + c +
          ' — the third pin, where a potentiometer keeps its wiper. ' +
          'Ebers-Moll has no Early effect, so collector current does not climb with Vce and ' +
          'the output resistance is infinite: a common-emitter stage here has a gain set only ' +
          'by its load. Beta is a constant, so it does not fall off at high current or low, and ' +
          'there is no base resistance, no junction capacitance and therefore no fT and no ' +
          'frequency limit of its own. Gummel-Poon is the model that adds those; this is not it, ' +
          'and says so rather than letting you find out.';
      }

      if (p.kind === 'NMOS' || p.kind === 'PMOS') {
        const sign = p.kind === 'NMOS' ? '' : ' — for the P-channel every voltage in it is ' +
          'measured the other way round, so Vth is typed as a magnitude and the source sits at ' +
          'the positive end';
        return 'Level 1, the square law' + sign + ': cut off below Vov = Vgs − Vth, then triode ' +
          'while Vds < Vov with Id = k·(Vov·Vds − Vds²/2)·(1 + λ·Vds), then saturation with ' +
          'Id = ½·k·Vov²·(1 + λ·Vds). k = ' + fmtEng(p.value, 'A/V²') + ', Vth = ' +
          fmtEng(param(p, 'vth', 0.05, 20), 'V') + ', λ = ' + param(p, 'lambda', 0, 1) + ' /V' +
          (op === null ? '' : '; right now Id = ' + fmtEng(Math.abs(op.i[0]), 'A')) + '. ' +
          'Drain is the ' + a + ' pin, source the ' + b + ', gate on the pin ' + c + '. The gate draws ' +
          'no current whatever, which is true of a real one to within picoamps. Drain and source ' +
          'are interchangeable and the model swaps them when Vds goes the other way, which is ' +
          'what lets this work as a pass gate. ' +
          'The body is tied to the source, so there is no body effect and Vth never moves. λ is a ' +
          'straight line bolted onto the saturation current, not channel-length modulation: it ' +
          'gives roughly the right output resistance and knows nothing about the actual channel. ' +
          'Below Vth the current is exactly zero, where a real device is passing nanoamps and a ' +
          'low-power design lives or dies by them. And there is no gate capacitance, so no ' +
          'switching time, no charge to drive and no dynamic power.';
      }

      /* op-amp */
      const hi = param(p, 'vpos', -100, 100), lo = param(p, 'vneg', -100, 100);
      return 'A controlled source, not an ideal one: Vout = A·(V+ − V−), limited to the rails, ' +
        'driven out through ' + fmtEng(Devices.OP_ROUT, 'Ω') + ' of output resistance, with an ' +
        'input stage that draws nothing at all. A = ' + fmtEng(p.value, '') + ', rails ' +
        fmtEng(lo, 'V') + ' to ' + fmtEng(hi, 'V') + ', so the linear region is the ' +
        fmtEng(Math.max(hi - lo, 1e-3) / Math.max(p.value, 10), 'V') + ' either side of zero ' +
        'where the gain has not yet run into them. The non-inverting input is the ' + a +
        ' pin, the output the ' + b + ', the inverting input on the pin ' + c + '. ' +
        'The gain is large and finite because an infinite one is a row of zeros in the matrix, ' +
        'which is not an answer but a singular matrix; and the limit is a smooth one rather than ' +
        'a hard clip because a hard clip has a slope of zero past the corner, and an iteration ' +
        'cannot steer on a slope of zero. ' +
        'The rails are parameters, not pins: there is nothing here to wire a supply to, and this ' +
        'op-amp draws no supply current — which makes it the one part on the canvas whose ' +
        'terminal currents do not add up to zero, because the current it delivers comes from a ' +
        'supply that is not drawn. Also missing: input offset voltage, bias current, slew rate, ' +
        'and any roll-off with frequency at all. The open-loop gain here is ' + fmtEng(p.value, '') +
        ' at one hertz and ' + fmtEng(p.value, '') + ' at one megahertz, which is the one thing a ' +
        'real op-amp is certainly not — so a bandwidth measured on this circuit is the ' +
        'bandwidth of the network you built around it, and nothing to do with the part.';
    }
    if (p.kind === 'V' || p.kind === 'I') {
      return 'The + terminal is the ' + pinWords(p)[turnsOf(p) % 2 ? 0 : 1] + ' pin. ' +
        'A frequency sweep drives it at this same amplitude, so set it to 1 for a plain transfer function.';
    }
    return 'Part ' + n + '. Type a value with the usual prefixes — 4k7 is not understood, 4.7k is.';
  }

  /* The model note quotes numbers that move — the two halves of a potentiometer, the
     power in a lamp, the current through a meter, the voltage a bar is showing — so
     any in-place change makes it stale, and it is the one label that exists for the
     learner to read the model rather than trust it. Rewritten in place rather than
     through paintPart(), which rebuilds the panel and would take a slider out from
     under the pointer mid-drag. */
  function refreshNote() {
    const sel = selOne();
    const note = partPanel && partPanel.querySelector('[data-note]');
    /* Markup, because paintPart has always written a note through innerHTML and these
       two have to render the same string the same way. They did not: a note long enough
       to need a paragraph break showed the break as literal text every time a solve
       refreshed it, and looked right again the next time the panel was rebuilt. */
    if (sel && note) note.innerHTML = modelNote(sel);
  }

  /* ---- folding a selection into a block ----
   *
   * The interface of a block is not something the learner declares; it is something
   * the drawing has already decided. A net with a connection inside the selection and
   * a connection outside it HAS to become a pin, or grouping would quietly cut it —
   * and a net wholly inside is nobody else's business and must not become one. So the
   * two counts below are the whole rule, and they are counted with the netlist's own
   * union-find rather than a second one written to look at the same thing.
   *
   * Where the block is then put matters as much as which pins it has. It is laid down
   * on the footprint the selection had, and each pin keeps the exact cell its crossing
   * was on, so every wire left outside still ends where it ended. Group and the
   * netlist is the netlist you had; ungroup and it is that same netlist again. A block
   * that had to be re-wired to work would be a block nobody could trust with a circuit
   * that was already right.
   *
   * Wires are sorted by the net they are on, not by where they lie: a wire on a wholly
   * internal net goes inside, and everything else stays. A wire that runs between two
   * selected parts and ALSO reaches something outside is on a crossing net and stays
   * put, which is why a port holds a list of cells and not one — both of the inside
   * ends it left behind have to arrive back at the same pin.
   */
  /* The block the canvas is standing inside, if it is standing inside one. */
  function hostBlock() {
    let m = model, b = null;
    for (let i = 0; i < path.length; i++) {
      b = (m.parts || []).filter(function (q) { return q.id === path[i]; })[0];
      if (!b) return null;
      m = b.inner || {};
    }
    return b;
  }

  function doGroup() {
    const sel = selParts();
    if (!sel.length) return;

    const uf = Netlist.joiner();
    cur.parts.forEach(function (p) {
      Netlist.pinsOf(p).forEach(function (pt) { uf.find(Netlist.key(pt, '')); });
    });
    cur.wires.forEach(function (w) { uf.run(w, ''); });
    /* and the boards, by the netlist's own function rather than a second reading of
       what a strip joins — without this, folding up a selection built on a board
       would count the two ends of a strip as two nets and grow the block a pin for
       each, which is a block that solves differently from the drawing it came from */
    cur.parts.forEach(function (p) {
      if (p.kind === 'BB') Netlist.bindBoard(p, uf, '');
    });

    /* one tally per net: how many pins reach it from each side of the line */
    const tally = {};
    function at(pt) {
      const r = uf.find(Netlist.key(pt, ''));
      return tally[r] || (tally[r] = { in: 0, out: 0, cells: [], seen: {}, gnd: false });
    }
    cur.parts.forEach(function (p) {
      const mine = selIds.has(p.id);
      Netlist.pinsOf(p).forEach(function (pt) {
        const t = at(pt);
        if (p.kind === 'GND') t.gnd = true;
        if (!mine) { t.out++; return; }
        t.in++;
        const kk = pt[0] + ',' + pt[1];
        if (!t.seen[kk]) { t.seen[kk] = 1; t.cells.push(pt); }
      });
    });
    /* The drawing on screen may itself be the inside of a block, and that block's own
       pins are connections to the world as surely as any part is — they are simply not
       drawn as parts, because what they reach is one level up. Counting them as
       outside is what stops a selection that swallows a pin cell from quietly cutting
       the block off from its own parent: without this, folding up the only resistor in
       a block would produce something with no pins at all, still drawn, still saved,
       and connected to nothing. */
    const host = hostBlock();
    if (host) {
      (host.ports || []).forEach(function (port) {
        (port.cells || []).forEach(function (c) { at(c).out++; });
      });
    }
    function netOf(pt) { return tally[uf.find(Netlist.key(pt, ''))]; }
    function crosses(t) { return !!t && t.in > 0 && t.out > 0; }
    function swallowed(t) { return !!t && t.in > 0 && t.out === 0; }

    /* The origin is the top-left of the ground the selection stood on, and everything
       that goes inside is measured from it — so the block's own position is the only
       thing that has to move when it is dragged, and a port's offset reads correctly
       against both drawings at once. */
    let ox = Infinity, oy = Infinity, x1 = -Infinity, y1 = -Infinity;
    sel.forEach(function (p) {
      const see = function (a, b) {
        if (a < ox) ox = a; if (a > x1) x1 = a;
        if (b < oy) oy = b; if (b > y1) y1 = b;
      };
      Netlist.pinsOf(p).forEach(function (pt) { see(pt[0], pt[1]); });
      see(p.x, p.y);
      if (bodyOf(p)) see(p.x + bodyW(p), p.y + bodyH(p));
    });
    if (!isFinite(ox)) return;

    /* Ports in reading order — down the drawing and across it — so the numbering on
       the block is the order a person would have counted them in. */
    const ports = [];
    Object.keys(tally).forEach(function (r) {
      const t = tally[r];
      if (!crosses(t)) return;
      t.cells.sort(function (a, b) { return (a[1] - b[1]) || (a[0] - b[0]); });
      ports.push(t);
    });
    ports.sort(function (a, b) {
      return (a.cells[0][1] - b.cells[0][1]) || (a.cells[0][0] - b.cells[0][0]);
    });

    const blk = {
      id: 'p' + (seq++), kind: 'IC', x: ox, y: oy, rot: 0, value: 0,
      ref: nextRef('IC', cur.parts),
      title: 'Block ' + (countBlocks(model) + 1), desc: '',
      w: Math.max(1, x1 - ox), h: Math.max(1, y1 - oy),
      /* A pin carried out to ground is named for what it is rather than numbered: it
         is the one net whose job a reader already knows. */
      ports: ports.map(function (t, i) {
        return { name: t.gnd ? 'GND' : String(i + 1),
                 cells: t.cells.map(function (c) { return [c[0] - ox, c[1] - oy]; }) };
      }),
      inner: {
        parts: sel.map(function (p) {
          const q = JSON.parse(JSON.stringify(p));
          q.x -= ox; q.y -= oy;
          return q;
        }),
        wires: cur.wires.filter(function (w) { return swallowed(netOf(w.a)); })
          .map(function (w) {
            return { a: [w.a[0] - ox, w.a[1] - oy], b: [w.b[0] - ox, w.b[1] - oy] };
          }),
      },
    };

    cur.wires = cur.wires.filter(function (w) { return !swallowed(netOf(w.a)); });
    cur.parts = cur.parts.filter(function (p) { return !selIds.has(p.id); });
    cur.parts.push(blk);
    selIds.clear(); selWires.clear();
    selIds.add(blk.id);
    changed();
    paintPart();
  }

  /* Ungroup, because a learner who folds up the wrong seven parts has to be able to
     say so, and because a block you cannot take apart is a black box in the sense
     nobody wants one. It is the exact inverse: the contents go back to the cells they
     came from, and the pins were on those cells all along, so the drawing that comes
     out is the drawing that went in. */
  function doUngroup() {
    /* Every block in the selection, not only a lone one. What comes out of an ungroup
       is a selection of several parts, so insisting on a selection of exactly one
       would mean a block nested inside what you just unfolded could not be unfolded in
       turn without clicking away first — and "select everything, ungroup" is the
       obvious way to flatten a level. Blocks the selection does not name are untouched
       whatever else is in it. */
    const blocks = selParts().filter(function (p) { return p.kind === 'IC'; });
    if (!blocks.length) return;
    const gone = {};
    blocks.forEach(function (b) { gone[b.id] = 1; });
    const taken = {};
    cur.parts.forEach(function (p) { if (!gone[p.id]) taken[p.id] = 1; });

    const back = [];
    blocks.forEach(function (b) {
      (((b.inner || {}).parts) || []).forEach(function (p) {
        const q = JSON.parse(JSON.stringify(p));
        q.x += b.x; q.y += b.y;
        /* An id that already means something else out here is renumbered rather than
           allowed to collide: two parts with one name is a selection that cannot be
           told apart and a delete that takes both. */
        if (taken[q.id]) q.id = 'p' + (seq++);
        taken[q.id] = 1;
        back.push(q);
      });
      cur.wires = cur.wires.concat((((b.inner || {}).wires) || []).map(function (w) {
        return { a: [w.a[0] + b.x, w.a[1] + b.y], b: [w.b[0] + b.x, w.b[1] + b.y] };
      }));
    });
    cur.parts = cur.parts.filter(function (p) { return !gone[p.id]; }).concat(back);
    selIds.clear(); selWires.clear();
    back.forEach(function (p) { selIds.add(p.id); });
    changed();
    paintPart();
  }

  function countBlocks(m) {
    let n = 0;
    (m.parts || []).forEach(function (p) {
      if (p.kind !== 'IC') return;
      n += 1 + countBlocks(p.inner || {});
    });
    return n;
  }

  /* ---- going in and coming back out ----
   * Opening a block does not open a second editor; it points this one at the drawing
   * inside. Every tool, the solver and the analysis panel go on working, and the solve
   * is still of the whole circuit — because what a subcircuit does depends entirely on
   * what is wired to it, and a block solved on its own would be answering about a
   * circuit that does not exist. */
  function openBlock(b) {
    if (!b || b.kind !== 'IC') return;
    path.push(b.id);
    reseat();
    afterMove();
  }
  function closeTo(depth) {
    path = path.slice(0, Math.max(0, depth));
    reseat();
    afterMove();
  }
  function afterMove() {
    selIds.clear(); selWires.clear();
    wireFrom = null; wireDown = null; hoverConn = null; marquee = null; drag = null;
    paintCrumbs();
    paintPart();
    /* Fit rather than keep the viewport: the inside of a block is drawn around its own
       origin and can be nowhere near where the parent canvas was looking, and arriving
       at an empty stretch of grid reads as a block that lost its contents. */
    zoomFit();
  }

  /* The trail, and the way back along it. Present only when there is somewhere to go
     back to — a breadcrumb reading "Circuit" and nothing else is a strip of chrome
     saying you are where you already knew you were. */
  function paintCrumbs() {
    if (!crumbEl) return;
    if (!path.length) { crumbEl.style.display = 'none'; crumbEl.innerHTML = ''; return; }
    crumbEl.style.display = '';
    const names = ['Circuit'];
    let m = model;
    path.forEach(function (id) {
      const b = (m.parts || []).filter(function (q) { return q.id === id; })[0] || {};
      names.push(b.title || 'Block');
      m = b.inner || {};
    });
    crumbEl.innerHTML = '<button class="ckt-t" data-up="' + (path.length - 1) +
      '" title="Back out one level (Escape)">↑ Out</button>' +
      '<span class="spacer" style="flex:none;width:4px"></span>' +
      names.map(function (n, i) {
        return (i ? '<span style="color:var(--ink-5);font-size:11px">›</span>' : '') +
          (i === names.length - 1
            ? '<span style="font-family:var(--mono);font-size:11px;color:var(--lime)">' + esc2(n) + '</span>'
            : '<button class="ckt-t" data-crumb="' + i + '">' + esc2(n) + '</button>');
      }).join('');
    crumbEl.querySelectorAll('[data-crumb]').forEach(function (b) {
      b.addEventListener('click', function () { closeTo(+b.dataset.crumb); });
    });
    crumbEl.querySelectorAll('[data-up]').forEach(function (b) {
      b.addEventListener('click', function () { closeTo(+b.dataset.up); });
    });
  }

  /* A change that alters numbers but not topology: a switch thrown, a wiper moved, a
     slider dragged. The model is saved and the answer re-solved in place, rather than
     thrown away the way an edit to the drawing throws it away — the whole point of
     flipping a switch is to see what it did to the answer you were already looking
     at. */
  function retouch() {
    if (opts.onChange) opts.onChange(snapshot());
    if (result) solve(); else paint();
    paintEnv();
  }

  /* One run per frame however fast the input arrives. A DC point is cheap, but a
     220-point sweep is not, and queueing one per pointer event would make a slider
     feel like it was stuck in treacle. Every continuous control goes through this —
     the wiper as well as the environment sliders, since they cost the same solve. */
  function perFrame(fn) {
    let pending = false;
    return function () {
      if (pending) return;
      pending = true;
      const later = function () {
        pending = false;
        if (disposed) return;
        fn();
      };
      if (typeof requestAnimationFrame === 'function') requestAnimationFrame(later);
      else setTimeout(later, 16);
    };
  }
  const retouchSoon = perFrame(function () { retouch(); });

  function toggleSwitch(p) {
    p.closed = !p.closed;
    retouch();
    paintPart();
  }
  function esc2(t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); }

  /* ---- the simulated world ----
   *
   * A sensor whose reading cannot be varied is a resistor with a fancy name. This is
   * the panel that makes it a sensor: one slider per quantity something on the canvas
   * actually senses, and the circuit re-solves as it moves.
   *
   * The sliders appear only when a part needs them. A light slider above a schematic
   * with no light sensor in it is a control that does nothing, and a control that
   * does nothing is a lie about what the model contains. */
  const ENV_Q = [
    { key: 'lux', label: 'Light', unit: 'lx', log: true, min: 0.1, max: 1e5,
      note: 'Moonlight is about 0.1 lx, a lit room 200 lx, an overcast day 1 klx, ' +
            'direct sun 100 klx.' },
    { key: 'tempC', label: 'Temperature', unit: '°C', log: false, min: -20, max: 120,
      note: 'Kelvin is what the beta model wants; this slider is in °C because that is ' +
            'what a datasheet and a room both speak.' },
  ];
  function envQ(key) { return ENV_Q.filter(function (q) { return q.key === key; })[0]; }
  function envToSlider(q, v) {
    const t = q.log ? Math.log(Math.max(v, q.min) / q.min) / Math.log(q.max / q.min)
                    : (v - q.min) / (q.max - q.min);
    return Math.round(Math.min(Math.max(t, 0), 1) * 1000);
  }
  function envFromSlider(q, t) {
    const f = Math.min(Math.max(t / 1000, 0), 1);
    return q.log ? q.min * Math.pow(q.max / q.min, f) : q.min + f * (q.max - q.min);
  }
  function envShow(q) {
    return q.log ? fmtEng(env[q.key], q.unit) : env[q.key].toFixed(1) + ' ' + q.unit;
  }
  /* Which quantities anything in the circuit actually senses, in a fixed order.
     Asked of the whole circuit rather than of the drawing on screen, because a
     thermistor folded into a block is still a thermistor in the circuit being solved,
     and a slider that vanished when you grouped it would be a control disappearing
     from a model that still depends on it. */
  function senses(m, q) {
    return (m.parts || []).some(function (p) {
      const k = PART_KINDS[p.kind];
      if (k && k.senses === q.key) return true;
      return p.kind === 'IC' && senses(p.inner || {}, q);
    });
  }
  function envInUse() {
    return ENV_Q.filter(function (q) { return senses(model, q); });
  }

  let envSig = null;
  function paintEnv() {
    if (!envPanel) return;
    const qs = envInUse();
    const sig = qs.map(function (q) { return q.key; }).join(',');
    if (sig === envSig) {
      /* same sliders, new numbers: leave the inputs alone so a drag is not interrupted */
      qs.forEach(function (q) {
        const el = envPanel.querySelector('[data-envval="' + q.key + '"]');
        if (el) el.textContent = envShow(q);
      });
      return;
    }
    envSig = sig;
    if (!qs.length) { envPanel.hidden = true; envPanel.innerHTML = ''; return; }
    envPanel.hidden = false;
    envPanel.innerHTML = '<h4>Environment</h4>' + qs.map(function (q) {
      return '<div style="margin-bottom:10px">' +
        '<div style="display:flex;justify-content:space-between;gap:8px;font-family:var(--mono);' +
        'font-size:10.5px;color:var(--ink-4);margin-bottom:4px">' +
        '<span>' + esc2(q.label) + '</span>' +
        '<span data-envval="' + q.key + '" style="color:var(--lime)">' + esc2(envShow(q)) + '</span></div>' +
        '<input type="range" data-env="' + q.key + '" min="0" max="1000" step="1" value="' +
        envToSlider(q, env[q.key]) + '" aria-label="' + esc2(q.label) +
        '" style="width:100%;height:18px;padding:0;border:0;background:none;accent-color:var(--lime)">' +
        '<p class="ckt-hint" style="margin-top:4px">' + esc2(q.note) + '</p>' +
        '</div>';
    }).join('') +
      '<p class="ckt-hint">Simulated, not measured — and not part of the schematic, so a ' +
      'saved circuit does not remember where you left these. The solution updates as you drag.</p>';

    envPanel.querySelectorAll('[data-env]').forEach(function (el) {
      el.addEventListener('input', function () {
        const q = envQ(el.dataset.env);
        env[q.key] = envFromSlider(q, +el.value);
        const out = envPanel.querySelector('[data-envval="' + q.key + '"]');
        if (out) out.textContent = envShow(q);
        envTouched();
      });
    });
  }

  /* One re-solve per frame however fast the slider moves — see perFrame. retouch()
     rather than a bare solve, because where the sliders stand is now part of what
     grading sees, and the outside world has to hear about it the same way it hears
     about a thrown switch. */
  const envTouched = perFrame(function () {
    retouch();
    paintPart();
  });

  /* The three boxes on the analysis panel were each held above a floor and none of them
     had a ceiling, which is the value box's defect in the field next door: a sweep to
     1e308 Hz overflows the admittance stamp, and a run of 1e308 seconds is a step of
     1e305 seconds. Held at both ends now, and — like the value box, and for cycle 6's
     reason — a number that was corrected says so instead of quietly becoming a
     different number in a box the learner is no longer looking at.
     The three floors are the ones this panel already had — 0.01 Hz, 1 Hz and 1 ns —
     kept to the number, because a floor that moved would be a behaviour change this
     cycle was not asked for and the defect was never at that end. */
  const AN_RANGE = { f1: [0.01, 1e12, 'Hz'], f2: [1, 1e12, 'Hz'], tstop: [1e-9, 1e6, 's'] };
  function anField(el, key, what) {
    el.addEventListener('change', function (e) {
      const lim = AN_RANGE[key];
      const want = parseEng(e.target.value, analysis[key]);
      analysis[key] = Math.min(Math.max(isFinite(want) ? want : analysis[key], lim[0]), lim[1]);
      e.target.value = fmtEng(analysis[key], lim[2]);
      if (analysis[key] !== want) {
        announce(what + ' has to be between ' + fmtEng(lim[0], lim[2]) + ' and ' +
          fmtEng(lim[1], lim[2]) + ', so it is now ' + fmtEng(analysis[key], lim[2]) + '.');
      }
    });
  }
  function paintOpts() {
    if (analysis.mode === 'ac') {
      optsEl.innerHTML =
        '<label class="ckt-f"><span>From</span><input data-f1 value="' + fmtEng(analysis.f1, 'Hz') + '"></label>' +
        '<label class="ckt-f"><span>To</span><input data-f2 value="' + fmtEng(analysis.f2, 'Hz') + '"></label>';
      anField(optsEl.querySelector('[data-f1]'), 'f1', 'The bottom of the sweep');
      anField(optsEl.querySelector('[data-f2]'), 'f2', 'The top of the sweep');
    } else if (analysis.mode === 'tran') {
      optsEl.innerHTML = '<label class="ckt-f"><span>Stop after</span><input data-ts value="' + fmtEng(analysis.tstop, 's') + '"></label>';
      anField(optsEl.querySelector('[data-ts]'), 'tstop', 'The length of the run');
    } else {
      optsEl.innerHTML = '<p class="ckt-hint">Solves the DC operating point and writes each node voltage onto the schematic.</p>';
    }
  }

  /* ---- solving ---- */
  function solve() {
    /* the environment is resolved into resistances here, once, before any stamping */
    const net = Netlist.build(model, env);
    let r;
    mcuRun = null;
    if (analysis.mode === 'dc') r = MNA.dc(net);
    else if (analysis.mode === 'ac') r = MNA.ac(net, analysis.f1, analysis.f2, 220);
    else {
      /* The one analysis a sketch takes part in. The rig is built before the run and
         kept after it, so what the panel reports and what drove the pins are the same
         machines rather than a second run of the same source. */
      mcuRun = mcuRig(net);
      r = MNA.tran(net, analysis.tstop, analysis.tstop / 900,
        mcuRun && !mcuRun.missing ? mcuRun.hooks : null);
    }

    if (r.error) {
      result = null;
      /* A run that never happened has no console and no line count, and reporting one
         at zero would read as a sketch that did nothing rather than a circuit that
         would not solve. */
      mcuRun = null;
      plotWrap.hidden = true;
      outEl.innerHTML = '<div class="ckt-err">' + esc2(r.error) + '</div>';
      /* The one message on this screen a learner most needs and is least likely to be
         looking at: they pressed Solve and are watching the drawing, not the panel. */
      announce('Did not solve. ' + r.error);
      paint();
      refreshNote();
      paintPart();
      return;
    }
    result = Object.assign({ kind: analysis.mode, net: net }, r);
    if (analysis.mode === 'dc') {
      plotWrap.hidden = true;
      const rows = [];
      for (let n = 1; n < net.nodeCount; n++) rows.push('<tr><td>node ' + n + '</td><td>' + fmtEng(r.v[n], 'V') + '</td></tr>');
      Object.keys(r.currents).forEach(function (id) {
        rows.push('<tr><td>' + id.replace('p', 'part ') + '</td><td>' + fmtEng(Math.abs(r.currents[id]), 'A') + '</td></tr>');
      });
      outEl.innerHTML = '<table class="ckt-tab">' + rows.join('') + '</table>';
      /* The table is a region with a name rather than a live one: making it live would
         read every node and every current on every solve, which is the whole answer
         shouted at someone who asked for one number. The headline goes to the status
         line and the table is there to be read at leisure. */
      announce(net.nodeCount - 1 === 0
        ? 'Solved. Nothing but ground: no node to report.'
        : 'Solved. ' + (net.nodeCount - 1) + (net.nodeCount - 1 === 1 ? ' node, ' : ' nodes, ') +
          'node 1 at ' + fmtEng(r.v[1], 'V') + '. The full table is in the analysis result panel.');
    } else {
      plotWrap.hidden = false;
      /* The node the learner picked may not exist any more — they chose node 5, edited
         the circuit down to three nodes and solved again. paintPlot has always clamped
         for its own use, so the plot quietly fell back to the highest node there is
         while the picker showed NO button pressed at all, because none of them equalled
         the number still sitting in analysis.node. Clamped where it is stored, so the
         two agree by construction rather than by both happening to do the same sum. */
      analysis.node = Math.min(Math.max(analysis.node, 1), Math.max(1, net.nodeCount - 1));
      const picks = [];
      for (let n = 1; n < net.nodeCount; n++) {
        picks.push('<button data-node="' + n + '"' + (n === analysis.node ? ' class="active"' : '') +
          ' aria-pressed="' + (n === analysis.node ? 'true' : 'false') + '">node ' + n + '</button>');
      }
      outEl.innerHTML = '<div class="seg ckt-nodes" role="group" aria-label="Which node to plot">' +
        picks.join('') + '</div>' + mcuStatus();
      outEl.querySelectorAll('[data-node]').forEach(function (b) {
        b.addEventListener('click', function () {
          analysis.node = +b.dataset.node;
          outEl.querySelectorAll('[data-node]').forEach(function (o) {
            o.setAttribute('aria-pressed', o === b ? 'true' : 'false');
          });
          solveRepaint();
          announce('Plotting node ' + analysis.node + '.');
        });
      });
      paintPlot();
      announce((analysis.mode === 'ac' ? 'Frequency sweep' : 'Transient run') + ' finished over ' +
        (net.nodeCount - 1) + (net.nodeCount - 1 === 1 ? ' node' : ' nodes') +
        '. The plot is under the canvas; the node buttons choose what it shows.' +
        /* A sketch that stopped is why the trace is flat, and it was said in two places
           a screen reader has to go and find — the line under the plot and the part
           panel. It ends the run, so it belongs in the sentence that reports the run. */
        mcuSpoken());
    }
    paint();
    /* the numbers the note quotes are the ones that just changed */
    refreshNote();
    /* The console and the run report live in the component panel, and nothing else
       rewrites it after a solve. Only when a sketch actually ran, so selecting a
       resistor and pressing Solve does not rebuild a panel that has not changed. */
    if (mcuRun) paintPart();
  }

  /* A line under the plot saying whether the program got anywhere, because a trace
     that is flat when it should be blinking has two possible causes and the learner
     should not have to click the part to find out which. */
  function mcuStatus() {
    if (!mcuRun) return '';
    if (mcuRun.missing) {
      return '<p class="ckt-hint">The interpreter (src/mcu.js) is not in this build, so ' +
        'the pins stayed at reset for the whole run.</p>';
    }
    return mcuRun.rigs.map(function (r) {
      /* the id as the canvas writes it, which for a part inside a block is the part's
         own number and not the trail of blocks above it */
      const who = 'MCU ' + r.id.split('|').pop().replace('p', '');
      if (r.error) {
        return '<div class="ckt-err">' + esc2(who) + ' did not compile — line ' +
          r.error.line + ': ' + esc2(r.error.message) + '</div>';
      }
      const st = r.machine.state();
      if (st.fault) {
        return '<div class="ckt-err">' + esc2(who) + ' stopped at line ' + st.fault.line +
          ': ' + esc2(st.fault.message) + ' The trace ends where it stopped.</div>';
      }
      return '<p class="ckt-hint">' + esc2(who) + ': ' +
        (st.inSetup ? 'still in setup() when the run ended'
          : st.done ? 'ran to the end; there is no loop()'
          : st.loops + (st.loops === 1 ? ' iteration' : ' iterations') + ' of loop()') +
        ', ' + st.ops.toLocaleString() + ' instructions.</p>';
    }).join('');
  }
  /* The same three outcomes mcuStatus() paints, as one clause for the live region.
     Silent when every sketch ran, because "MCU 1 ran" on every solve is noise. */
  function mcuSpoken() {
    if (!mcuRun) return '';
    if (mcuRun.missing) return ' The interpreter is not in this build, so the pins stayed at reset.';
    return mcuRun.rigs.map(function (r) {
      const who = 'MCU ' + r.id.split('|').pop().replace('p', '');
      if (r.error) return ' ' + who + ' did not compile — line ' + r.error.line + ': ' + r.error.message;
      const st = r.machine.state();
      if (st.fault) {
        return ' ' + who + ' stopped at line ' + st.fault.line + ': ' + st.fault.message +
          ' The trace ends where it stopped.';
      }
      return '';
    }).join('');
  }

  function solveRepaint() { paintPlot(); outEl.querySelectorAll('[data-node]').forEach(function (b) { b.classList.toggle('active', +b.dataset.node === analysis.node); }); }

  function paintPlot() {
    if (!result || typeof Sandbox === 'undefined') return;
    /* The canvas's OWN box, not its parent's. .ckt-plot carries 8px of padding, and
       under box-sizing:border-box a parent's rect includes it — so measuring the parent
       made the canvas 16px wider than the space it had, at every viewport size, and
       .ckt's overflow:hidden clipped the difference off the right-hand end of every
       trace and half the axis label with it. The stylesheet stretches this canvas to
       its box (width:100%, min-width:320px), so its own rect IS the content box.
       And nothing sets style.width here for the same reason: CSS owns the layout, this
       owns the backing store, or the next resize would measure the last one's answer
       and the canvas could never shrink again. */
    const box = plotCv.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(320, Math.round(box.width)), h = 190;
    plotCv.width = w * dpr; plotCv.height = h * dpr;
    plotCv.style.height = h + 'px';
    const c = plotCv.getContext('2d');
    c.setTransform(dpr, 0, 0, dpr, 0, 0);
    const n = Math.min(analysis.node, result.net.nodeCount - 1);

    if (result.kind === 'ac') {
      const pts = result.sweep.map(function (s) {
        return [s.f, 20 * Math.log10(Math.max(Lin.cabs(s.v[n]), 1e-12))];
      });
      const ys = pts.map(function (p) { return p[1]; });
      const f = Sandbox.frame(c, w, h, {
        xRange: [analysis.f1, analysis.f2], yRange: [Math.min.apply(null, ys) - 4, Math.max.apply(null, ys) + 4],
        logX: true, xTicks: 5, yTicks: 4, margin: { l: 50, r: 14, t: 12, b: 26 },
        xLabel: function (x) { return x >= 1e6 ? (x / 1e6) + 'M' : x >= 1e3 ? (x / 1e3) + 'k' : String(Math.round(x)); },
      });
      f.line(pts, f.P.accent, 2);
      f.text('dB at node ' + n, f.x0 + 6, f.y0 + 13, f.P.faint);
      f.text('Hz', f.x1 - 6, f.y1 + 18, f.P.faint, 'right');
      /* What the curve does, in the order it does it: where it starts, where it ends,
         and its largest value — which for a filter is the pass band and for a resonance
         is the peak, and is the one number a reader cannot get from the ends alone. */
      const top = ys.indexOf(Math.max.apply(null, ys));
      describe('Frequency response at node ' + n + ', ' + pts.length + ' points from ' +
        fmtEng(pts[0][0], 'Hz') + ' to ' + fmtEng(pts[pts.length - 1][0], 'Hz') + '. ' +
        ys[0].toFixed(1) + ' dB at the bottom, ' + ys[ys.length - 1].toFixed(1) +
        ' dB at the top, highest ' + ys[top].toFixed(1) + ' dB at ' + fmtEng(pts[top][0], 'Hz') + '.');
    } else {
      const pts = result.t.map(function (t, i) { return [t, result.v[i][n]]; });
      const ys = pts.map(function (p) { return p[1]; });
      const lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys);
      const pad = Math.max((hi - lo) * 0.12, 1e-6);
      const f = Sandbox.frame(c, w, h, {
        xRange: [0, result.t[result.t.length - 1]], yRange: [lo - pad, hi + pad],
        xTicks: 5, yTicks: 4, margin: { l: 50, r: 14, t: 12, b: 26 },
        xLabel: function (x) { return fmtEng(x, ''); },
      });
      f.line(pts, f.P.accent, 2);
      f.text('V at node ' + n, f.x0 + 6, f.y0 + 13, f.P.faint);
      f.text('seconds', f.x1 - 6, f.y1 + 18, f.P.faint, 'right');
      describe('Transient at node ' + n + ', ' + pts.length + ' samples over ' +
        fmtEng(pts[pts.length - 1][0], 's') + '. Starts at ' + fmtEng(ys[0], 'V') +
        ', ends at ' + fmtEng(ys[ys.length - 1], 'V') + ', between ' + fmtEng(lo, 'V') +
        ' and ' + fmtEng(hi, 'V') + '.');
    }
  }
  /* The plot's accessible name, rewritten on every repaint. Not a live region: it is a
     picture, and a picture that announced itself on every frame of a dragged slider
     would be unusable. Someone reading the plot goes to it and it says what it shows. */
  function describe(text) { if (plotCv) plotCv.setAttribute('aria-label', text); }

  /* ---- the component panel's uncommitted edit ----
   *
   * EVERY FIELD ON THAT PANEL COMMITTED ON `change`, WHICH FIRES ON BLUR. dispose()
   * empties root.innerHTML, and removing a focused element from the document does NOT
   * fire its pending change — so a learner who typed and then left by the footer, the
   * icon rail or the back button lost what they had typed, with nothing said. Driven
   * rather than argued, on both fields:
   *
   *     a sketch typed, never blurred, then disposed   onChange fired 0 times and what
   *                                                    reached progress was the DEFAULT
   *                                                    sketch the part was placed with
   *     "4.7k" typed into a resistor, never blurred    the saved value was still 1000
   *
   * One slot rather than a timer per field, because a fourth field added later should
   * join this rather than grow a fourth. Not a commit per keystroke — the note on the
   * sketch handler is right that that would put a save between every two letters, and
   * the value box additionally CLAMPS, so committing "4" on the way to "4.7k" would
   * rewrite the box under the typist. A short idle debounce instead, flushed by each of
   * the three exits that can come first: the window going away, the page being hidden,
   * and dispose. The 600 ms sits under app.js's own 900 ms progress debounce on purpose,
   * so the two nest rather than race.
   */
  let pendingEdit = null, editTimer = null;
  function editSoon(fn) {
    pendingEdit = fn;
    if (editTimer) clearTimeout(editTimer);
    editTimer = setTimeout(flushEdit, 600);
  }
  function flushEdit() {
    if (editTimer) { clearTimeout(editTimer); editTimer = null; }
    const fn = pendingEdit;
    pendingEdit = null;
    if (fn) fn();
  }

  function changed() {
    /* An editor that has been disposed must never reach onChange. Its `cur` is a model
       nothing on screen is showing, and onChange is what writes the learner's circuit
       into their saved progress — so a stale editor that still hears a key would save a
       drawing over the one they can see. Nothing can deliver that key now, but this is
       the line that makes it a rule rather than a consequence. */
    if (disposed) return;
    result = null;
    mcuRun = null;
    plotWrap.hidden = true;
    /* An edit can remove the block the canvas is standing inside — nothing in the UI
       offers that today, but a model handed in from outside can, and a canvas pointed
       at a drawing that is no longer in the circuit would edit parts nobody can save.
       Walking the trail from the root again is cheap and cannot be wrong. */
    reseat();
    paintCrumbs();
    if (opts.onChange) opts.onChange(snapshot());
    /* a sensor may have arrived or left, and with it the slider that drives it */
    paintEnv();
    paint();
  }

  /* A diagram is a picture. Everything from here down is editing, analysis and
     chrome — pointer handlers that place parts, a document-level keydown listener,
     and lookups for a toolbar this DOM does not have. Returning above all of it is
     what actually makes read-only read-only: the previous version returned below the
     handlers, so clicking a question's schematic inserted a resistor into it. */
  if (ro_) {
    let dro = null;
    if (typeof ResizeObserver !== 'undefined') {
      dro = new ResizeObserver(function () { paintSoon(); });
      dro.observe(cv.parentElement);
    }
    paint();
    return {
      getModel: function () { return snapshot(); },
      solve: function () { return null; },
      dispose: function () {
        if (disposed) return;
        disposed = true;
        if (dro) dro.disconnect();
        root.innerHTML = '';
      },
    };
  }

  /* ---- interaction ---- */
  /* How far the pointer has moved, in screen pixels, since it went down. A click and
     a drag start identically, so nothing commits to being a drag until it has moved
     far enough that the learner clearly meant it. */
  const DRAG_SLOP = 4;
  let down = null;

  cv.addEventListener('pointermove', function (e) {
    const sp = evPt(e);
    const wasTip = tipBlock();
    hover = toGrid(sp[0], sp[1]);
    hoverSp = sp;

    if (panFrom) {
      view.px = panFrom.px + (panFrom.sx - sp[0]) / view.s;
      view.py = panFrom.py + (panFrom.sy - sp[1]) / view.s;
      paintSoon();
      return;
    }

    /* Past the slop, the gesture is a drag, and a drag off a terminal is a wire.
       Below the slop it is still undecided, because a press that has not moved is on
       its way to being a click — and a click has three other meanings. */
    if (wireDown && !wireDown.started &&
        Math.hypot(sp[0] - wireDown.sx, sp[1] - wireDown.sy) > DRAG_SLOP) {
      wireDown.started = true;
      announce(startWire(wireDown.pt));
    }
    if (wireDown) { paintSoon(); return; }

    if (down && !drag && !marquee && down.mode === 'maybe-move' &&
        Math.hypot(sp[0] - down.sx, sp[1] - down.sy) > DRAG_SLOP) {
      drag = { from: down.grid, moved: false };
    }
    if (down && !drag && !marquee && down.mode === 'maybe-marquee' &&
        Math.hypot(sp[0] - down.sx, sp[1] - down.sy) > DRAG_SLOP) {
      marquee = { a: toWorld(down.sx, down.sy), b: toWorld(sp[0], sp[1]) };
    }

    if (drag) {
      const dx = hover[0] - drag.from[0], dy = hover[1] - drag.from[1];
      if (dx || dy) {
        moveBy(dx, dy);
        drag.from = hover;
        drag.moved = true;
        paintSoon();
      }
      return;
    }

    if (marquee) { marquee.b = toWorld(sp[0], sp[1]); paintSoon(); return; }

    /* The terminal under the pointer, which is what the ring is drawn around. Only
       while nothing else is in hand: a ring offering to start a wire in the middle of
       a drag would be offering something the release is not going to do. */
    const wasConn = hoverConn;
    const con = (down || wireFrom || wireDown) ? null : connAt(hover);
    hoverConn = (con && con.part && Netlist.pinsOf(con.part).length <= 1) ? null : con;
    const conKey = hoverConn ? hoverConn.kind + wireKey({ a: hoverConn.pt, b: hoverConn.pt }) : '';
    const wasKey = wasConn ? wasConn.kind + wireKey({ a: wasConn.pt, b: wasConn.pt }) : '';
    if (conKey !== wasKey) { cv.style.cursor = hoverConn ? 'crosshair' : ''; paintSoon(); return; }
    /* The hover card is drawn by paint(), so it only appears if something asks for a
       repaint — and pointer movement over a block otherwise asks for nothing. Repaint
       when the card would change and not on every pixel of travel: the card follows
       the pointer, so a moving pointer over one block is a repaint per event, which is
       what the whole canvas costs. */
    const isTip = tipBlock();
    if (isTip || wasTip) { paintSoon(); return; }
    if (wireFrom) paintSoon();
  });

  cv.addEventListener('pointerleave', function () {
    const had = tipBlock() || hoverConn;
    hover = null; hoverSp = null; hoverConn = null;
    cv.style.cursor = '';
    if (wireFrom || had) paint();
  });

  /* The other half of Escape. A right click is what a drawing tool has meant by
     "stop doing that" for thirty years, and it is already in the hand that is
     drawing. The menu is only suppressed when there is something to cancel. */
  cv.addEventListener('contextmenu', function (e) {
    if (!wireFrom) return;
    e.preventDefault();
    announce(cancelWire());
  });

  /* Wheel zooms about the cursor. Ctrl+wheel is the browser's own page zoom on some
     setups, so it is left alone. */
  cv.addEventListener('wheel', function (e) {
    if (e.ctrlKey) return;
    e.preventDefault();
    const sp = evPt(e);
    zoomTo(view.s * (e.deltaY < 0 ? 1.12 : 1 / 1.12), sp[0], sp[1]);
  }, { passive: false });

  /* ---- what a gesture at a cell means ----
   *
   * Lifted out of the pointer handler so the keyboard can do the same thing rather
   * than a near-miss of it. The wire Enter draws and the wire a click draws are now
   * the same three lines, and the refusal to stack two parts on one cell is enforced
   * once. Each returns the sentence for the live region, or '' when nothing happened.
   */
  function wireAt(pt) {
    if (!wireFrom) { wireFrom = pt; paint(); return 'Wire started at ' + cellName(pt) + '.'; }
    /* wires stay orthogonal: take the dominant direction */
    const end = Math.abs(pt[0] - wireFrom[0]) > Math.abs(pt[1] - wireFrom[1])
      ? [pt[0], wireFrom[1]] : [wireFrom[0], pt[1]];
    let msg = 'Wire cancelled.';
    if (end[0] !== wireFrom[0] || end[1] !== wireFrom[1]) {
      cur.wires.push({ a: wireFrom, b: end });
      msg = 'Wire drawn from ' + cellName(wireFrom) + ' to ' + cellName(end) + '.';
      changed();
    }
    wireFrom = null;
    paint();
    return msg;
  }

  /* The selection change a click at a cell makes, with no drag in it. */
  /* ---- where a wire may start or end ----
   *
   * A terminal is a part's pin or any point along an existing wire. Both are offered
   * because both are things a wire can legally join, and refusing the second would
   * mean a learner who wants to branch off a supply rail has to guess which cell the
   * rail happens to end at.
   *
   * Identity for a wire is its two endpoints rather than an id, because wires are
   * created by three different paths (here, the catalog loader, and ungrouping) and
   * only one of them could have been taught to stamp an id. Two wires with the same
   * endpoints are the same connection drawn twice, so treating them as one thing is
   * right rather than merely convenient.
   */
  function wireKey(w) { return w.a[0] + ',' + w.a[1] + ':' + w.b[0] + ',' + w.b[1]; }

  function onWire(w, g) {
    const dx = w.b[0] - w.a[0], dy = w.b[1] - w.a[1];
    /* A diagonal run is not something this editor can draw, and guessing which cells
       one passes through would be inventing connections. */
    if (dx && dy) return false;
    if (dx) {
      return g[1] === w.a[1] &&
        g[0] >= Math.min(w.a[0], w.b[0]) && g[0] <= Math.max(w.a[0], w.b[0]);
    }
    if (dy) {
      return g[0] === w.a[0] &&
        g[1] >= Math.min(w.a[1], w.b[1]) && g[1] <= Math.max(w.a[1], w.b[1]);
    }
    return g[0] === w.a[0] && g[1] === w.a[1];
  }

  function wireAtPt(g) {
    for (let i = cur.wires.length - 1; i >= 0; i--) {
      if (onWire(cur.wires[i], g)) return cur.wires[i];
    }
    return null;
  }

  /* Pins beat wires: where a wire already ends on a pin, the thing the learner is
     pointing at is the component. Later parts beat earlier ones, matching the paint
     order — what is drawn on top is what gets picked. */
  function connAt(g) {
    if (!g) return null;
    for (let i = cur.parts.length - 1; i >= 0; i--) {
      const p = cur.parts[i];
      const ps = Netlist.pinsOf(p);
      for (let j = 0; j < ps.length; j++) {
        if (ps[j][0] === g[0] && ps[j][1] === g[1]) {
          return { pt: [ps[j][0], ps[j][1]], part: p, pin: j, kind: 'pin' };
        }
      }
    }
    const w = wireAtPt(g);
    if (w) return { pt: [g[0], g[1]], wire: w, kind: 'wire' };
    return null;
  }

  /* Two cells that do not share a row or a column need a corner. It goes along
     whichever axis the drag covered more of first, so the wire follows the hand
     rather than turning somewhere the learner did not aim. */
  function elbow(a, b) {
    if (a[0] === b[0] && a[1] === b[1]) return [];
    if (a[0] === b[0] || a[1] === b[1]) return [[a, b]];
    const c = Math.abs(b[0] - a[0]) >= Math.abs(b[1] - a[1])
      ? [b[0], a[1]] : [a[0], b[1]];
    return [[a, c], [c, b]];
  }

  /* A wire ending part-way along another wire splits it, so that what is stored is
     what the drawing shows: runs between junctions. The solver did not need this —
     every cell along a run is already the same node — but selecting and deleting do.
     Without it, clicking the branch of a T and pressing Delete takes away the whole
     rail it branched off. */
  function splitWiresAt(pt) {
    for (let i = cur.wires.length - 1; i >= 0; i--) {
      const w = cur.wires[i];
      if (!onWire(w, pt)) continue;
      if ((pt[0] === w.a[0] && pt[1] === w.a[1]) ||
          (pt[0] === w.b[0] && pt[1] === w.b[1])) continue;
      selWires.delete(wireKey(w));
      cur.wires.splice(i, 1,
        { a: w.a, b: [pt[0], pt[1]] },
        { a: [pt[0], pt[1]], b: w.b });
    }
  }

  function startWire(pt) {
    wireFrom = [pt[0], pt[1]];
    paint();
    return 'Wire started at ' + cellName(wireFrom) + '. Click to finish, Escape to cancel.';
  }

  function cancelWire() {
    if (!wireFrom) return null;
    wireFrom = null; wireDown = null;
    paint();
    return 'Wire cancelled.';
  }

  function commitWire(pt) {
    const from = wireFrom;
    wireFrom = null; wireDown = null;
    if (!from) return null;
    const segs = elbow(from, pt);
    if (!segs.length) { paint(); return 'Wire cancelled — it would end where it began.'; }
    segs.forEach(function (seg) {
      splitWiresAt(seg[0]);
      splitWiresAt(seg[1]);
      cur.wires.push({ a: seg[0], b: seg[1] });
    });
    changed();
    paint();
    const end = connAt(pt);
    return 'Wire from ' + cellName(from) + ' to ' +
      (end && end.part ? partName(end.part) : cellName(pt)) + '.';
  }

  function selectAt(pt, shift) {
    const hit = partAt(pt);
    if (hit) {
      if (shift) {
        if (selIds.has(hit.id)) selIds.delete(hit.id); else selIds.add(hit.id);
      } else if (!selIds.has(hit.id)) {
        selIds.clear();
        selWires.clear();
        selIds.add(hit.id);
      }
      if (!shift) selWires.clear();
      return hit;
    }
    /* No part here: a wire under the pointer is what was meant. Wires and parts share
       one selection so that Delete, and the panel that reports what is selected, have
       one answer rather than two. */
    const w = wireAtPt(pt);
    if (w) {
      const k = wireKey(w);
      if (shift) {
        if (selWires.has(k)) selWires.delete(k); else selWires.add(k);
      } else if (!selWires.has(k)) {
        selIds.clear(); selWires.clear(); selWires.add(k);
      }
      return null;
    }
    if (!shift) { selIds.clear(); selWires.clear(); }
    return hit;
  }

  function placeAt(pt) {
    /* Placing: refuse to stack two parts on one cell. A body is not a part on that
       cell, it is the ground under it — the whole point of a board is that you put
       things on it — so only a symbol blocks. Two bodies on one cell is still
       refused, since a board laid across a block, or across another board, is a
       drawing nobody can read and a hole nobody can say the owner of. */
    const existing = cellPartAt(pt) || (bodyOf({ kind: tool }) ? bodyAt(pt) : undefined);
    if (existing) {
      selIds.clear(); selWires.clear(); selIds.add(existing.id); paintPart(); paint();
      return partName(existing) + ' is already at ' + cellName(pt) + '; selected it instead.';
    }
    const kind = tool;
    const p = { id: 'p' + (seq++), kind: kind, x: pt[0], y: pt[1], rot: 0,
                /* numbered among its own kind on THIS canvas, not across every part
                   ever placed — a block's insides are their own namespace */
                ref: nextRef(kind, cur.parts),
                value: PART_KINDS[kind].def };
    /* kinds that carry state beyond a value start with the registry's defaults, so a
       part is never placed half-defined and then behaves oddly */
    const st = PART_KINDS[kind].state;
    if (st) Object.keys(st).forEach(function (key2) { p[key2] = st[key2]; });
    cur.parts.push(p);
    selIds.clear(); selWires.clear();
    selIds.add(p.id);
    changed();
    paintPart();
    return 'Placed ' + partName(p) + ' at ' + cellName(pt) + '.';
  }

  /* A cell and a part, in the words the live region uses. Column and row rather than
     raw grid numbers, because the origin moves when a block is opened and "column 3,
     row 6" is a place on the drawing in front of you rather than a coordinate in a
     space nothing on screen shows. */
  function cellName(pt) { return 'column ' + (pt[0] - originX + 1) + ', row ' + (pt[1] - originY + 1); }
  function partName(p) {
    const k = PART_KINDS[p.kind];
    return (k ? k.name : p.kind) + ' ' + refOf(p);
  }

  cv.addEventListener('pointerdown', function (e) {
    const sp = evPt(e);
    const pt = toGrid(sp[0], sp[1]);
    /* A click is also how this canvas is reached from a keyboard: without it the tab
       order runs straight past the one control on the page that has any work in it. */
    focusCanvas();
    caret = pt;
    caretByKey = false;

    /* Middle button, or space held: pan. Both are what a drawing tool does, and the
       second is the one people already have in their fingers. */
    if (e.button === 1 || spaceDown) {
      panFrom = { sx: sp[0], sy: sp[1], px: view.px, py: view.py };
      cv.setPointerCapture(e.pointerId);
      e.preventDefault();
      return;
    }
    if (e.button !== 0) return;

    /* A wire in flight: this click finishes it. Checked before everything else,
       because while a wire is being drawn no other gesture is on offer. */
    if (wireFrom) { announce(commitWire(pt)); return; }

    /* Pressing on a terminal starts a wire, whatever tool is selected. This is the
       gesture the ring was advertising, and it replaces having to find a wire mode
       first: the connection points are where wires can go, so pointing at one and
       pressing is unambiguous. Release without moving leaves the wire in flight for
       a second click; release after moving finishes it there. */
    if (hoverConn && (tool === 'select' || tool === 'wire')) {
      cv.setPointerCapture(e.pointerId);
      wireDown = { sx: sp[0], sy: sp[1], pt: hoverConn.pt, kind: hoverConn.kind,
                   part: hoverConn.part || null, started: false, shift: e.shiftKey };
      hoverConn = null;
      paint();
      return;
    }

    if (tool === 'wire') { announce(wireAt(pt)); return; }

    if (tool === 'select') {
      cv.setPointerCapture(e.pointerId);
      const hit = selectAt(pt, e.shiftKey);
      /* Dragging a part that is already part of a multiple selection moves the whole
         selection; that is why selectAt's clear is conditional. `shift` is carried so
         the click-to-use gesture below can tell a plain click from one that was only
         ever adjusting the selection. */
      down = hit
        ? { sx: sp[0], sy: sp[1], grid: pt, mode: 'maybe-move', hit: hit.id, shift: e.shiftKey }
        : { sx: sp[0], sy: sp[1], grid: pt, mode: 'maybe-marquee' };
      paintPart();
      paint();
      return;
    }

    announce(placeAt(pt));
  });

  function endPointer(e) {
    if (panFrom) { panFrom = null; return; }
    /* Drag-and-release finishes the wire where the pointer let go; press-and-release
       on the spot leaves it in flight, so both habits work and neither has to be
       taught. A cancelled pointer is the browser taking over, not the learner
       finishing, so it drops the wire rather than committing one nobody drew. */
    if (wireDown) {
      const w = wireDown;
      wireDown = null;
      if (e && e.type === 'pointercancel') { announce(cancelWire()); return; }
      if (w.started) {
        const sp2 = e && e.clientX !== undefined ? evPt(e) : null;
        announce(commitWire(sp2 ? toGrid(sp2[0], sp2[1]) : w.pt));
        return;
      }
      /* A click, then, and a click on this canvas already meant something. A part
         under the pointer is selected, as it always was — which is the only thing
         keeping a ground, whose single pin IS the part, pickup-able at all. A wire
         under the pointer is selected, which is how it reaches Delete. Only a bare
         terminal with nothing else to mean is left over, and that starts a wire for
         people who would rather click twice than drag. */
      if (partAt(w.pt)) {
        const hit = selectAt(w.pt, w.shift);
        if (hit && hit.kind === 'SW' && !w.shift) toggleSwitch(hit);
        paintPart(); paint();
        announce(hit ? 'Selected ' + partName(hit) + '.' : selectedSaid());
        return;
      }
      if (w.kind === 'wire') {
        selectAt(w.pt, w.shift);
        paintPart(); paint();
        announce(selectedSaid());
        return;
      }
      announce(startWire(w.pt));
      return;
    }
    if (marquee) {
      const x0 = Math.min(marquee.a[0], marquee.b[0]), x1 = Math.max(marquee.a[0], marquee.b[0]);
      const y0 = Math.min(marquee.a[1], marquee.b[1]), y1 = Math.max(marquee.a[1], marquee.b[1]);
      cur.parts.forEach(function (p) {
        /* a body is caught by its area rather than by its origin corner, so a rubber
           band drawn round what you can see picks up what you can see */
        const wx = gx(p.x), wy = gy(p.y);
        const wx2 = bodyOf(p) ? gx(p.x + bodyW(p)) : wx;
        const wy2 = bodyOf(p) ? gy(p.y + bodyH(p)) : wy;
        if (wx >= x0 && wx2 <= x1 && wy >= y0 && wy2 <= y1) selIds.add(p.id);
      });
      marquee = null;
      paintPart();
      paint();
    }
    /* A switch is the one part whose state you set by using it rather than by typing
       a number, so a plain click on one throws it. It has to be a CLICK and not a
       press, and not a drag either: toggling on pointerdown would flip the switch
       every time you picked one up to move it. Nor a shift-click: that gesture is
       aimed at the selection, and adding a switch to a selection should no more throw
       it than adding a resistor should change its value. Nor a cancelled gesture: the
       browser taking the pointer away is not the learner using the switch. */
    if (!drag && down && down.mode === 'maybe-move' && down.hit &&
        !down.shift && !(e && e.type === 'pointercancel')) {
      const hp = cur.parts.filter(function (p) { return p.id === down.hit; })[0];
      if (hp && hp.kind === 'SW') toggleSwitch(hp);
    }
    if (drag) {
      /* one undo entry per gesture, not one per grid cell crossed */
      if (drag.moved) changed();
      drag = null;
    }
    down = null;
  }
  cv.addEventListener('pointerup', endPointer);
  cv.addEventListener('pointercancel', endPointer);

  /* Double-click opens a block. It is the gesture people already use on a folder, and
     it costs nothing anywhere else: every other part on this canvas ignores a second
     click, and a switch has already been thrown by the first one and is thrown back by
     the second, which is what a switch clicked twice should do. */
  cv.addEventListener('dblclick', function (e) {
    const sp = evPt(e);
    const hit = partAt(toGrid(sp[0], sp[1]));
    if (hit && hit.kind === 'IC') { e.preventDefault(); openBlock(hit); }
  });

  /* ---- the keyboard ----
   *
   * All of this was on `document`, guarded only against a keydown whose target was an
   * input or a textarea. Three things followed, none of them local to this canvas:
   *
   *   * `Space` was preventDefault()ed for the whole page. A <button> is activated on
   *     keyup only if the keydown left it active, and the browser sets that in the
   *     keydown default action — so cancelling the keydown cancels the press. With a
   *     build exercise on screen, Space no longer worked on "Check the circuit", on the
   *     footer navigation, on the rail, or on anything in the desk modal, and no longer
   *     scrolled the reading above the canvas either.
   *   * `Ctrl+A` was taken, with preventDefault, from the whole document — so a lesson
   *     carrying an editor was a lesson whose text could not be selected.
   *   * `R`, `G`, `U`, `Delete` and `Backspace` fired from anywhere outside an input.
   *     Pressing R while the focus was on a footer button rotated a part somewhere down
   *     the page, and Backspace deleted the selection.
   *
   * Everything is now on the canvas, which is a focus stop. A key with a meaning here
   * has that meaning while the caret is here and no other time.
   */
  /* The caret itself is declared with the editor's other state, above. Null until the
     canvas is used, and drawn only while the canvas holds focus: a caret on a canvas
     nobody is steering is one more mark on a busy drawing. */
  let spaceDown = false;

  function focusCanvas() {
    try { cv.focus({ preventScroll: true }); } catch (e2) { try { cv.focus(); } catch (e3) {} }
  }

  /* The cell the caret starts on: whatever is selected, else the middle of what can be
     seen — never (0,0), which on a panned canvas is off screen and reads as a caret
     that did not appear. */
  function caretHome() {
    const one = selParts()[0];
    if (one) return [one.x, one.y];
    const box = cv.parentElement.getBoundingClientRect();
    return toGrid(Math.max(320, box.width) / 2, Math.max(260, box.height) / 2);
  }

  /* Keep the caret on screen: a caret arrowed past the edge of the viewport is a caret
     the learner has lost, and every key after that lands somewhere invisible. */
  function revealCaret() {
    if (!caret) return;
    const box = cv.parentElement.getBoundingClientRect();
    const w = Math.max(320, box.width), h = Math.max(260, box.height);
    const sx = (gx(caret[0]) - view.px) * view.s, sy = (gy(caret[1]) - view.py) * view.s;
    const m = GRID * view.s;
    if (sx < m) view.px -= (m - sx) / view.s;
    if (sx > w - m) view.px += (sx - (w - m)) / view.s;
    if (sy < m) view.py -= (m - sy) / view.s;
    if (sy > h - m) view.py += (sy - (h - m)) / view.s;
  }

  const ARROWS = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };

  function onKey(e) {
    /* This cannot fire while the listener is on the canvas — a canvas has no focusable
       children, so `e.target` is always the canvas itself. It is here because the value
       boxes and the sketch DO live inside this editor, and the old handler, one level up
       on the document, needed exactly this test to stay out of the way of typing. If
       anyone moves the listener back up, the guard should already be where they need it
       rather than something they have to remember to restore. */
    if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
    if (e.target && e.target.isContentEditable) return;

    const step = ARROWS[e.key];
    if (step) {
      e.preventDefault();
      caretByKey = true;
      if (!caret) { caret = caretHome(); revealCaret(); paint(); announce('Caret at ' + cellName(caret) + '.'); return; }
      if (e.shiftKey) {
        /* Shift+arrow moves the selection, which is the drag gesture without a pointer.
           One changed() per press rather than per cell is wrong for a drag and right
           here: each press is a deliberate step the learner can see the result of. */
        if (!selIds.size) { announce('Nothing is selected, so there is nothing to move.'); return; }
        moveBy(step[0], step[1]);
        caret = [caret[0] + step[0], caret[1] + step[1]];
        changed();
        revealCaret();
        paint();
        announce('Moved the selection to ' + cellName(caret) + '.');
        return;
      }
      caret = [caret[0] + step[0], caret[1] + step[1]];
      revealCaret();
      paint();
      const under = partAt(caret);
      announce(cellName(caret) + (under ? ', ' + partName(under) + '.' : '.'));
      return;
    }

    if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar' || e.code === 'Space') {
      e.preventDefault();
      /* Space held with the pointer over the drawing is the pan modifier, the way it is
         in every drawing tool. That is the only situation in which it is a modifier for
         a drag rather than the key the learner just pressed, so it is the only one that
         takes it — and it is reached only through the canvas, so the page keeps its own
         Space everywhere else. */
      if (e.key !== 'Enter' && hoverSp) {
        if (!spaceDown) { spaceDown = true; cv.style.cursor = 'grab'; }
        return;
      }
      caretByKey = true;
      if (!caret) { caret = caretHome(); revealCaret(); paint(); announce('Caret at ' + cellName(caret) + '.'); return; }
      if (tool === 'wire') { announce(wireAt(caret)); return; }
      if (tool === 'select') {
        /* A block is opened by double-clicking it, so the key is pressing Enter on one
           that is already selected — the second press, which is what a double click is.
           Read before the selection changes, because selecting it is what the first
           press did. */
        const already = selIds.size === 1 && partAt(caret) && selIds.has(partAt(caret).id);
        const hit = selectAt(caret, e.shiftKey);
        paintPart(); paint();
        /* A switch is used by clicking it, and Enter is the click. Not on shift, which
           is aimed at the selection — the same rule endPointer applies to the mouse. */
        if (hit && hit.kind === 'SW' && !e.shiftKey) {
          toggleSwitch(hit); paintPart();
          announce(partName(hit) + ' is now ' + (hit.closed ? 'closed' : 'open') + '.');
        } else if (hit && hit.kind === 'IC' && !e.shiftKey && already) {
          openBlock(hit);
          announce('Opened ' + partName(hit) + '. Escape closes it again.');
        } else {
          announce(hit ? 'Selected ' + partName(hit) + '.' : 'Selection cleared.');
        }
        return;
      }
      announce(placeAt(caret));
      return;
    }

    if (e.key === 'Delete' || e.key === 'Backspace') {
      const nP = selIds.size, nW = selWires.size;
      doDelete();
      e.preventDefault();
      announce(deleteSaid(nP, nW));
    }
    /* Shift for the three verbs, plain letters for the parts. A resistor is placed a
       hundred times in a session and a block is grouped twice, so the commoner action
       gets the cheaper key. It could not go the other way: Ctrl+R reloads the page. */
    else if (e.key === 'f' || e.key === 'F') { announce(toggleFull()); e.preventDefault(); }
    else if (e.shiftKey && e.key === 'R') { doRotate(); announce(rotationSaid()); }
    else if (e.shiftKey && e.key === 'G') { doGroup(); announce(blockSaid('Grouped')); }
    else if (e.shiftKey && e.key === 'U') { doUngroup(); announce(blockSaid('Ungrouped')); }
    else if (!e.ctrlKey && !e.metaKey && !e.altKey && e.key.length === 1 &&
             PART_KEYS[(e.shiftKey ? 'shift+' : '') + e.key.toLowerCase()]) {
      /* Picking up a part cancels a half-drawn wire, the way reaching for a different
         tool always has. */
      const picked = PART_KEYS[(e.shiftKey ? 'shift+' : '') + e.key.toLowerCase()];
      wireFrom = null; wireDown = null;
      setTool(picked);
      e.preventDefault();
      announce(toolSaid(picked));
    }
    else if (e.key === 'Escape') {
      /* Escape drops whatever is in hand first, and only then backs out of a block:
         inside one, the gesture that cancels a half-drawn wire must not also throw
         away where you are. */
      if (wireFrom || marquee || selIds.size || selWires.size) {
        wireFrom = null; wireDown = null; marquee = null;
        selIds.clear(); selWires.clear();
        paintPart(); paint();
        announce('Let go.');
      } else if (path.length) { closeTo(path.length - 1); announce('Closed the block.'); }
      /* Last in the chain on purpose: Escape drops what is in hand, then backs out of
         a block, and only when there is neither does it give the screen back. Leaving
         a canvas you are lost on should not also close the block you were lost in. */
      else if (isFull()) { setFull(false); announce('Back in the page.'); }
    }
    else if ((e.ctrlKey || e.metaKey) && (e.key === 'a' || e.key === 'A')) {
      selIds.clear(); selWires.clear();
      cur.parts.forEach(function (p) { selIds.add(p.id); });
      cur.wires.forEach(function (w) { selWires.add(wireKey(w)); });
      paintPart(); paint(); e.preventDefault();
      announce(selectedSaid());
    }
    else if (e.key === '+' || e.key === '=') { zoomTo(view.s * 1.2); announce(zoomSaid()); }
    else if (e.key === '-' || e.key === '_') { zoomTo(view.s / 1.2); announce(zoomSaid()); }
    else if (e.key === '0') { zoomFit(); announce(fitSaid()); }
  }

  function zoomSaid() { return 'Zoom ' + Math.round(view.s * 100) + ' per cent.'; }
  /* The button said nothing at all and the key said 'Fitted the drawing to the window.'
     whether it had or not. One sentence for both, and it reports the zoom it reached —
     which is the thing the learner cannot see and the only part worth saying. */
  function fitSaid() {
    if (!cur.parts.length && !cur.wires.length) return 'Nothing to fit. Zoom back to 100 per cent.';
    if (fitShort) {
      return 'Fitted as far as the zoom goes, ' + Math.round(view.s * 100) +
        ' per cent. The drawing is wider than the window can show at that zoom, so this ' +
        'is the middle of it.';
    }
    return 'Fitted the drawing to the window. Zoom ' + Math.round(view.s * 100) + ' per cent.';
  }
  function rotationSaid() {
    const ps = selParts().filter(function (p) { const k = PART_KINDS[p.kind]; return !k || k.pins > 1; });
    if (!ps.length) return 'Nothing here can be turned.';
    return 'Rotated ' + ps.length + (ps.length === 1 ? ' part to ' : ' parts to ') +
      (turnsOf(ps[0]) * 90) + ' degrees.';
  }
  function blockSaid(verb) { return verb + '. ' + cur.parts.length + ' parts on this drawing.'; }

  function releaseSpace() {
    if (!spaceDown) return;
    spaceDown = false;
    cv.style.cursor = '';
  }
  function onSpaceUp(e) { if (e.code === 'Space' || e.key === ' ') releaseSpace(); }

  /* Alt-tabbing away with space held used to leave the flag set for the rest of the
     session: the keyup went to another window, and the next plain click on the canvas
     panned instead of placing a part, with the cursor still reading "grab". Two ways
     out of the window, and both of them end the hold. */
  /* Also where a half-typed sketch is banked. Alt-tabbing away and closing the tab are
     the two exits dispose() never sees, and the debounce is 600 ms — long enough to
     still be pending. pagehide rather than unload: unload is not fired at all on a
     mobile browser that backgrounds the tab and then reclaims it. */
  function onWinBlur() { releaseSpace(); flushEdit(); }
  function onCanvasFocus() { cvFocused = true; paint(); }
  /* The caret is kept, not cleared: tabbing to a value box to type a resistance and
     tabbing back is one gesture, and coming back to the middle of the canvas instead of
     to where you were is the sort of thing that makes a keyboard route unusable. Only
     the drawing of it goes. */
  function onCanvasBlur() { cvFocused = false; releaseSpace(); paint(); }

  cv.addEventListener('keydown', onKey);
  cv.addEventListener('keyup', onSpaceUp);
  cv.addEventListener('focus', onCanvasFocus);
  cv.addEventListener('blur', onCanvasBlur);
  window.addEventListener('blur', onWinBlur);
  window.addEventListener('pagehide', flushEdit);

  function doRotate() {
    /* one-pin parts sit on their cell and have no direction to turn — which is now a
       question of how many pins a kind declares rather than a list of two names */
    const ps = selParts().filter(function (p) {
      const k = PART_KINDS[p.kind];
      return !k || k.pins > 1;
    });
    if (!ps.length) return;
    /* four quarter turns, not two: a diode or a transistor has to be able to face
       the other way, and a resistor turned twice looks exactly as it did */
    ps.forEach(function (p) { p.rot = (turnsOf(p) + 1) % 4; });
    changed();
    paintPart();
  }
  function doDelete() {
    if (!selIds.size && !selWires.size) return;
    /* A wire with nothing left at either end is a wire the learner cannot see the
       purpose of, but it may still be carrying a connection between two other
       things, so deleting parts leaves wires alone. Deleting a WIRE is different:
       it was asked for by name. */
    cur.parts = cur.parts.filter(function (p) { return !selIds.has(p.id); });
    cur.wires = cur.wires.filter(function (w) { return !selWires.has(wireKey(w)); });
    selIds.clear();
    selWires.clear();
    changed();
    paintPart();
  }

  function selectedSaid() {
    const bits = [];
    if (selIds.size) bits.push(selIds.size + (selIds.size === 1 ? ' part' : ' parts'));
    if (selWires.size) bits.push(selWires.size + (selWires.size === 1 ? ' wire' : ' wires'));
    return bits.length ? 'Selected ' + bits.join(' and ') + '.' : 'Nothing to select.';
  }

  function deleteSaid(nP, nW) {
    if (!nP && !nW) return 'Nothing is selected.';
    const bits = [];
    if (nP) bits.push(nP + (nP === 1 ? ' part' : ' parts'));
    if (nW) bits.push(nW + (nW === 1 ? ' wire' : ' wires'));
    return 'Deleted ' + bits.join(' and ') + '.';
  }

  /* A diagram has no tools, no analysis panel and nothing to click, so there is
     nothing below this line to wire up. Returning early is what makes the read-only
     DOM safe to shrink: every lookup after this point assumes the full chrome. */
  /* Only one drawer open at a time, and choosing a part closes the one it came from:
     a menu that stays open over the canvas you are about to click is a menu in the
     way. <details> gives the open/close, the Enter key and the tab stop for free —
     everything below is the part that is specific to a palette. */
  const cats = Array.prototype.slice.call(root.querySelectorAll('.ckt-cat'));
  function closeCats() { cats.forEach(function (d) { d.open = false; }); }
  cats.forEach(function (d) {
    d.addEventListener('toggle', function () {
      if (!d.open) return;
      cats.forEach(function (o) { if (o !== d) o.open = false; });
      /* A closed drawer's canvases have no layout, so their first paint would land in
         a zero-width backing store. Paint them when the drawer opens instead. */
      requestAnimationFrame(paintIcons);
    });
  });
  /* A press anywhere outside a drawer closes it. Captured on this editor rather than
     on the document, because a lesson can hold two of these and one palette has no
     business reacting to the other's clicks. */
  root.addEventListener('pointerdown', function (e) {
    if (!cats.some(function (d) { return d.open; })) return;
    if (e.target && e.target.closest && e.target.closest('.ckt-cat')) return;
    closeCats();
  }, true);

  /* The icons are the registry's own paths, so a button shows the drawing the canvas
     will make — including which convention the reader has chosen. A picture of an ANSI
     resistor on the button that places an IEC one would be worse than no picture. */
  const icons = Array.prototype.slice.call(root.querySelectorAll('.ckt-ico'));
  function paintIcons() {
    /* The PAGE's ink, not the canvas's. P().ink is for the schematic surface, which is
       deliberately dark in both themes and so hands back a near-white in both — which
       on the light theme's white drawer paints every icon in nothing at all. */
    const ink = getComputedStyle(document.documentElement)
      .getPropertyValue('--ink').trim() || P().ink;
    icons.forEach(function (c) { Symbols.paint(c, c.dataset.sym, ink); });
  }
  paintIcons();
  requestAnimationFrame(paintIcons);
  root.__cktIcons = paintIcons;

  /* One place that records which tool is on, so the bar, the drawers and the key map
     cannot end up disagreeing about it. The class was the only record before, and a
     class is not a state any assistive technology can read. */
  function paintTools() {
    root.querySelectorAll('[data-tool]').forEach(function (o) {
      const on = o.dataset.tool === tool;
      o.classList.toggle('on', on);
      o.setAttribute('aria-pressed', on ? 'true' : 'false');
    });
    /* A drawer whose part is the one in hand says so on its own face, since the
       chosen button inside it is not visible while it is shut. */
    cats.forEach(function (d) {
      d.classList.toggle('holds', !!d.querySelector('[data-tool].on'));
    });
  }

  function toolSaid(kind) {
    const b = root.querySelector('[data-tool="' + kind + '"]');
    const name = b ? b.getAttribute('aria-label') : kind;
    if (kind === 'select') return 'Select. Click a part or a wire; drag from a terminal to wire.';
    if (kind === 'wire') return 'Wire. Click a cell, then another.';
    return name + ' chosen. Click the canvas, or press Enter, to place one.';
  }

  function setTool(kind) {
    tool = kind;
    closeCats();
    paintTools();
    paintPart();
    paint();
  }

  root.querySelectorAll('[data-tool]').forEach(function (b) {
    b.addEventListener('click', function () {
      wireFrom = null; wireDown = null;
      setTool(b.dataset.tool);
      announce(toolSaid(b.dataset.tool));
    });
  });
  /* ---- filling the screen ----
   *
   * Two mechanisms for one gesture. The class is what actually lays the editor out
   * over the page, and it works everywhere — inside an iframe, on a browser that
   * refuses the request, on a phone. The native request is asked for on top of it so
   * the browser's own chrome goes too, and if it is refused the class alone still does
   * the job. Which is why the class is applied FIRST and never waits on the promise.
   *
   * The canvas is sized by a ResizeObserver already, so nothing here has to repaint:
   * changing the box is the whole of it.
   */
  const shell = root.querySelector('.ckt');
  const fullBtn = root.querySelector('[data-act="full"]');
  function isFull() { return shell.classList.contains('full'); }
  function setFull(on) {
    shell.classList.toggle('full', !!on);
    /* .page carries an entry animation, and an element with an animation that can
       touch transform is a containing block for position:fixed — so `inset:0` was
       measured against the article rather than the window, and the editor came out
       887px tall inside a 1320px window. The class below turns that animation off
       while the editor is expanded, and stops the page behind from scrolling. */
    document.body.classList.toggle('ckt-expanded', !!on);
    fullBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
    fullBtn.textContent = on ? 'Shrink' : 'Expand';
    fullBtn.title = on ? 'Back into the page (F, or Escape)' : 'Fill the screen (F)';
    if (on && shell.requestFullscreen) {
      /* A rejected request is the ordinary case on a page that has not been clicked
         yet, and the class has already done the useful half. */
      shell.requestFullscreen().catch(function () {});
    } else if (!on && document.fullscreenElement === shell && document.exitFullscreen) {
      document.exitFullscreen().catch(function () {});
    }
    /* Expanding is asking for room, so the drawing is refitted into the room it just
       got. Without this the circuit stays the size it was in a 340px box, marooned in
       the top-left corner of a screen-sized canvas, and the first thing anyone does is
       press Fit. Only on the way out, and only when there is something to fit. */
    if (on && (cur.parts.length || cur.wires.length)) zoomFit();
    paintSoon();
  }
  function toggleFull() {
    setFull(!isFull());
    return isFull() ? 'Filling the screen. F or Escape puts it back.'
      : 'Back in the page.';
  }
  fullBtn.addEventListener('click', function () { announce(toggleFull()); });
  /* Leaving fullscreen by the browser's own route — Escape, or F11 — has to take the
     class with it, or the editor stays pinned over the page with nothing to say so. */
  function onFsChange() {
    if (document.fullscreenElement !== shell && isFull()) setFull(false);
  }
  document.addEventListener('fullscreenchange', onFsChange);

  root.querySelector('[data-act="zoomin"]').addEventListener('click', function () { zoomTo(view.s * 1.2); });
  root.querySelector('[data-act="zoomout"]').addEventListener('click', function () { zoomTo(view.s / 1.2); });
  root.querySelector('[data-act="fit"]').addEventListener('click', function () {
    zoomFit(); announce(fitSaid());
  });
  root.querySelector('[data-act="group"]').addEventListener('click', doGroup);
  root.querySelector('[data-act="ungroup"]').addEventListener('click', doUngroup);
  root.querySelector('[data-act="rotate"]').addEventListener('click', doRotate);
  root.querySelector('[data-act="delete"]').addEventListener('click', doDelete);
  root.querySelector('[data-act="clear"]').addEventListener('click', function () {
    cur.parts = []; cur.wires = []; selIds.clear(); selWires.clear();
    wireFrom = null; wireDown = null; hoverConn = null;
    view = { s: 1, px: 0, py: 0 };
    changed(); paintPart();
    announce('Cleared the drawing.');
  });
  root.querySelectorAll('[data-an]').forEach(function (b) {
    b.addEventListener('click', function () {
      analysis.mode = b.dataset.an;
      root.querySelectorAll('[data-an]').forEach(function (o) {
        o.classList.toggle('active', o === b);
        o.setAttribute('aria-pressed', o === b ? 'true' : 'false');
      });
      paintOpts();
    });
  });
  root.querySelector('.ckt-run').addEventListener('click', solve);

  root.querySelector('[data-act="fit"]').setAttribute('aria-keyshortcuts', '0');
  root.querySelector('[data-act="rotate"]').setAttribute('aria-keyshortcuts', 'Shift+R');
  root.querySelector('[data-act="delete"]').setAttribute('aria-keyshortcuts', 'Delete');
  root.querySelector('[data-act="group"]').setAttribute('aria-keyshortcuts', 'Shift+G');
  root.querySelector('[data-act="ungroup"]').setAttribute('aria-keyshortcuts', 'Shift+U');


  let ro = null;
  if (typeof ResizeObserver !== 'undefined') {
    ro = new ResizeObserver(function () { paintSoon(); if (result && !plotWrap.hidden) paintPlot(); });
    ro.observe(cv.parentElement);
  }

  paintTools();
  paintCrumbs();
  paintPart();
  paintEnv();
  paintOpts();
  paint();

  return {
    getModel: function () { return snapshot(); },
    solve: solve,
    dispose: function () {
      /* Idempotent, and the first line rather than the last: a second dispose used to
         be harmless only by luck, and everything below is written to be safe to skip. */
      if (disposed) return;
      /* BEFORE `disposed`, and that ordering is the whole fix: changed() returns early
         on a disposed editor, so a flush one line lower would be a flush that does
         nothing. This is the line that keeps a sketch typed and never blurred — the
         footer, the icon rail, the back button all arrive here. */
      flushEdit();
      disposed = true;
      /* The keyboard now lives on the canvas, which goes with the DOM below — but the
         window listeners do not, so they are released here or every editor ever opened
         keeps two for the rest of the session. */
      window.removeEventListener('blur', onWinBlur);
      window.removeEventListener('pagehide', flushEdit);
      /* Same reasoning for the document listener the expand button needs, and one step
         further: a lesson navigated away from while the editor filled the screen would
         otherwise leave the browser in fullscreen with nothing in it. */
      document.removeEventListener('fullscreenchange', onFsChange);
      if (isFull()) document.body.classList.remove('ckt-expanded');
      if (document.fullscreenElement === shell && document.exitFullscreen) {
        document.exitFullscreen().catch(function () {});
      }
      if (ro) ro.disconnect();
      root.innerHTML = '';
    },
  };
}

/* a worked example, so the canvas is never empty on first open */
const CIRCUIT_EXAMPLE = {
  parts: [
    { id: 'p0', kind: 'V', x: 3, y: 6, rot: 1, value: 5, ac: 1 },
    { id: 'p1', kind: 'R', x: 6, y: 4, rot: 0, value: 1000 },
    { id: 'p2', kind: 'C', x: 9, y: 6, rot: 1, value: 1e-7 },
    { id: 'p3', kind: 'GND', x: 3, y: 9 },
    { id: 'p4', kind: 'GND', x: 9, y: 9 },
  ],
  wires: [
    { a: [3, 5], b: [3, 4] },
    { a: [3, 4], b: [5, 4] },
    { a: [7, 4], b: [9, 4] },
    { a: [9, 4], b: [9, 5] },
    { a: [3, 7], b: [3, 9] },
    { a: [9, 7], b: [9, 9] },
  ],
};

/* ---------------------------------------------------------------- grading
 *
 * A circuit exercise is checked the way a code lab is: the learner's work is run,
 * and each check either raises or does not. The check writes ordinary JavaScript
 * against a small API, so "the corner is at 1 kHz" is expressed as the measurement
 * it actually is rather than as a shape the schematic has to match. Two learners
 * who build different but equally correct filters both pass.
 */
function circuitContext(model, env) {
  /* The environment can arrive two ways: named by the caller, or riding on the model
     the editor handed out. Grading gets only a model, so without the second door a
     light or temperature sensor would always be resolved at ENV_DEFAULT and the grade
     would disagree with the numbers on the learner's screen. A model with neither
     still lands on ENV_DEFAULT, which is every exercise that has no sensor in it. */
  const net = Netlist.build(model, env || (model && model.env) || null);
  const cache = {};

  function need(what) {
    if (net.tooDeep) {
      throw new Error('Blocks are nested more than ' + net.tooDeep + ' deep, so part of ' +
        'the circuit is not in the netlist and ' + what + ' would be about a different one.');
    }
    if (!net.hasGround) throw new Error('Add a ground before ' + what + ' can mean anything.');
  }

  /* Every part in the circuit, blocks opened out, each with the prefixed id the netlist
     knows it by. A check that names a part by id goes on naming the same part after the
     learner folds it into a block — and finds one that has only ever lived inside one. */
  function allParts(m, at, out) {
    (((m && m.parts) || [])).forEach(function (p) {
      out.push({ p: p, id: at + p.id });
      if (p.kind === 'IC') allParts(p.inner, at + p.id + '|', out);
    });
    return out;
  }
  function out() {
    if (!net.probes.length) throw new Error('Place a probe on the node you are treating as the output.');
    if (net.probes.length > 1) throw new Error('There is more than one probe; the checks read a single output.');
    return net.probes[0];
  }

  return {
    net: net,
    /* How many of a kind the learner used. Asked of what was PLACED, not of what was
       stamped: a potentiometer reaches the solver as two resistors and a lamp as one,
       and neither should make count('R') go up. For R, C, L, V and I the two lists
       are the same list. */
    count: function (kind) { return net.placed.filter(function (p) { return p.kind === kind; }).length; },
    values: function (kind) { return net.placed.filter(function (p) { return p.kind === kind; }).map(function (p) { return p.value; }); },
    /* What a dynamic part actually resolved to in this environment. A bare id still
       finds a part that has since been folded into a block, since the netlist knows it
       by a longer name now and the check that asks for it does not. */
    ohms: function (id) {
      const r = net.readouts.filter(function (x) { return x.id === id; })[0] ||
        net.readouts.filter(function (x) { return x.id.split('|').pop() === id; })[0];
      return r ? r.ohms : null;
    },
    env: net.env,
    outNode: out,
    nodeCount: function () { return net.nodeCount; },

    /* A non-linear part at the operating point: the voltage on each terminal and the
       current into each, in the order the panel names them, which is pin order —
       [anode, cathode] for a junction, [collector, emitter, base] for a bipolar,
       [drain, source, gate] for a MOSFET, [in+, out, in−] for an op-amp. A
       check can then ask what a transistor is biased at rather than inferring it from
       two node voltages and a subtraction, which is the sort of arithmetic a check
       should be verifying rather than doing. */
    device: function (id) {
      const hit = allParts(model, '', []).filter(function (q) {
        return q.id === id || q.p.id === id;
      })[0];
      const p = hit && hit.p;
      if (!p || !Devices.is(p.kind)) {
        throw new Error('There is no non-linear device called ' + id + ' in this circuit.');
      }
      const r = this.dc();
      const seen = net.readouts.filter(function (x) { return x.id === hit.id; })[0];
      const vs = seen.nodes.map(function (n) { return r.v[n]; });
      const d = Devices.build(p);
      return { kind: p.kind, v: vs, i: d.iv(d, vs, { raw: true }).i };
    },

    /* DC operating point; throws with the solver's own message on a bad circuit */
    dc: function () {
      need('a DC answer');
      if (!cache.dc) {
        const r = MNA.dc(net);
        if (r.error) throw new Error(r.error);
        cache.dc = r;
      }
      return cache.dc;
    },
    vout: function () { return this.dc().v[out()]; },

    /* magnitude and phase of the probed node at one frequency */
    gain: function (f) {
      need('a frequency response');
      const v = MNA.acAt(net, 2 * Math.PI * f);
      if (!v) throw new Error('The circuit is under-determined at ' + fmtEng(f, 'Hz') + '.');
      return Lin.cabs(v[out()]);
    },
    phase: function (f) {
      need('a frequency response');
      const v = MNA.acAt(net, 2 * Math.PI * f);
      if (!v) throw new Error('The circuit is under-determined at ' + fmtEng(f, 'Hz') + '.');
      return Math.atan2(v[out()][1], v[out()][0]) * 180 / Math.PI;
    },
    /* the -3 dB point, found by bisection on the measured response */
    corner: function (lo, hi) {
      need('a corner frequency');
      const self = this;
      const ref = self.gain(lo);
      const target = ref / Math.SQRT2;
      let a = lo, b = hi;
      for (let i = 0; i < 60; i++) {
        const mid = Math.sqrt(a * b);
        if (self.gain(mid) > target) a = mid; else b = mid;
      }
      return Math.sqrt(a * b);
    },
    /* the probed node over time */
    step: function (tstop) {
      need('a transient');
      const r = MNA.tran(net, tstop, tstop / 600);
      if (r.error) throw new Error(r.error);
      const n = out();
      return { t: r.t, v: r.v.map(function (row) { return row[n]; }) };
    },

    /* ---- a sketch, run against the circuit it is wired into ----
     *
     * The transient and the program, co-simulated exactly as the editor's Solve button
     * does it, so a check that says "the LED is lit two hundred milliseconds after
     * power-up" is reading the same run the learner is watching.
     *
     * `node` is a series per node and `out` the probed one; `console` is what the sketch
     * printed, so a check can require an answer the sketch worked out as well as a
     * voltage it produced. A sketch that faults does NOT throw: the fault is handed back
     * as data, because "your program divides by zero on line 9" is a thing a check may
     * want to assert about and is certainly a thing it should report as itself rather
     * than as a failed measurement. */
    sketch: function (tstop) {
      need('a sketch run');
      const rig = mcuRig(net);
      if (!rig) throw new Error('There is no microcontroller in this circuit.');
      if (rig.missing) {
        throw new Error('The interpreter is not loaded in this environment, so a sketch ' +
          'cannot be run. src/mcu.js has to be loaded alongside src/circuit.js.');
      }
      const bad = rig.rigs.filter(function (r) { return r.error; })[0];
      if (bad) {
        throw new Error('The sketch on ' + bad.id + ' does not compile — line ' +
          bad.error.line + ': ' + bad.error.message);
      }
      const r = MNA.tran(net, tstop, tstop / 600, rig.hooks);
      if (r.error) throw new Error(r.error);
      const first = rig.rigs[0];
      const st = first.machine.state();
      return {
        t: r.t,
        node: function (n) { return r.v.map(function (row) { return row[n]; }); },
        out: net.probes.length === 1
          ? r.v.map(function (row) { return row[net.probes[0]]; }) : null,
        console: first.machine.console(),
        fault: st.fault,
        loops: st.loops,
        /* the pins as the run left them, which is how a check asks what the sketch
           decided rather than what the circuit did about it */
        pin: function (name) {
          return first.rec.pins.filter(function (q) { return q.name === String(name); })[0] || null;
        },
      };
    },

    assert: function (cond, msg) { if (!cond) throw new Error(msg || 'Assertion failed'); },
    close: function (got, want, tolFrac, msg) {
      const tol = Math.abs(want * (tolFrac === undefined ? 0.05 : tolFrac));
      if (!(Math.abs(got - want) <= tol)) {
        throw new Error((msg ? msg + ' — ' : '') + 'measured ' + Number(got).toPrecision(4) +
          ', expected ' + Number(want).toPrecision(4));
      }
    },
    fmt: fmtEng,
  };
}

/* Run every check of a circuit exercise against one schematic, in one simulated
   environment: the one named here, else the one the model carries, else the default.
   A sensor is graded against the world the learner set, not a world nobody chose. */
function runCircuitChecks(model, checks, env) {
  return (checks || []).map(function (c) {
    let ctx;
    try { ctx = circuitContext(model, env); }
    catch (e) { return { name: c.name, pass: false, message: String(e && e.message || e) }; }
    try {
      const fn = new Function('c', '"use strict";\n' + c.code);
      fn(ctx);
      return { name: c.name, pass: true };
    } catch (e) {
      return { name: c.name, pass: false, message: String((e && e.message) || e) };
    }
  });
}
