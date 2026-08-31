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

/* ---------------------------------------------------------------- parts */
const PART_KINDS = {
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
};

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

/* Quarter turns clockwise, normalised. Module level rather than tucked inside the
   netlist because the pins, the polarity, the drawing and the panel all have to agree
   about which way round a part is, and one function is how they are made to. */
function turnsOf(p) { return ((((p.rot || 0) | 0) % 4) + 4) % 4; }

/* The two ends of a body and its control pin, in the words the drawing puts them in. */
function pinWords(p) {
  return [['left', 'right', 'above'], ['top', 'bottom', 'to the right'],
          ['right', 'left', 'below'], ['bottom', 'top', 'to the left']][turnsOf(p)];
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

  function key(pt) { return pt[0] + ',' + pt[1]; }

  /* Union-find over every point touched by a wire or a pin: two points in the same
     set are electrically the same node. */
  function build(model, env) {
    const world = Object.assign({}, ENV_DEFAULT, env || {});
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

    /* A bar display is deliberately left out of this pass. Every other pin creates a
       node whether or not anything else reaches it, which is right for a part that
       carries current — but a display dropped on an empty cell would then be a node
       with nothing stamped on it, and the solver would call the whole circuit
       under-determined. A readout must never be able to break the answer it exists to
       show, so a bar takes the node it lands on and creates none. */
    model.parts.forEach(function (p) {
      if (p.kind === 'BAR') return;
      pinsOf(p).forEach(function (pt) { find(key(pt)); });
    });
    model.wires.forEach(function (w) {
      /* a wire is a straight run; every grid point along it joins the same node */
      const dx = Math.sign(w.b[0] - w.a[0]), dy = Math.sign(w.b[1] - w.a[1]);
      const n = Math.max(Math.abs(w.b[0] - w.a[0]), Math.abs(w.b[1] - w.a[1]));
      let cur = [w.a[0], w.a[1]];
      find(key(cur));
      for (let i = 0; i < n; i++) {
        const nxt = [cur[0] + dx, cur[1] + dy];
        union(key(cur), key(nxt));
        cur = nxt;
      }
    });

    /* ground first, so it becomes node 0 and drops out of the unknowns */
    const gnd = model.parts.filter(function (p) { return p.kind === 'GND'; });
    let gndRoot = null;
    gnd.forEach(function (p) {
      const r = find(key(pinsOf(p)[0]));
      if (gndRoot === null) gndRoot = r; else union(r, gndRoot);
    });
    if (gndRoot !== null) gndRoot = find(gndRoot);

    const nodeOf = {};
    let next = 1;
    Object.keys(parent).forEach(function (k) {
      const r = find(k);
      if (nodeOf[r] === undefined) nodeOf[r] = (r === gndRoot) ? 0 : next++;
    });

    const probes = model.parts
      .filter(function (p) { return p.kind === 'OUT'; })
      .map(function (p) { return nodeOf[find(key(pinsOf(p)[0]))]; });

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

    model.parts.forEach(function (p) {
      if (p.kind === 'GND' || p.kind === 'OUT') return;
      if (p.kind === 'BAR') {
        /* look the node up without creating one — see the pass above */
        const kk = key(pinsOf(p)[0]);
        placed.push({ id: p.id, kind: p.kind, value: p.value });
        readouts.push({ id: p.id, kind: 'BAR', full: p.value,
                        node: parent[kk] === undefined ? null : nodeOf[find(kk)] });
        return;
      }
      const pins = plusFirst(p).map(function (pt) { return nodeOf[find(key(pt))]; });
      placed.push({ id: p.id, kind: p.kind, value: p.value });

      if (p.kind === 'POT') {
        const rr = potSplit(p);
        /* two resistances sharing the wiper node: pin A to wiper, wiper to pin B */
        parts.push({ id: p.id + '#a', kind: 'R', value: rr[0], n1: pins[0], n2: pins[2], of: p.id });
        parts.push({ id: p.id + '#b', kind: 'R', value: rr[1], n1: pins[2], n2: pins[1], of: p.id });
        readouts.push({ id: p.id, kind: 'POT', nodes: pins, ohms: rr[0] + rr[1], split: rr });
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
        dev.nodes = pins.slice(0, PART_KINDS[p.kind].pins);
        parts.push(dev);
        readouts.push({ id: p.id, kind: p.kind, nodes: dev.nodes });
        return;
      }
      const ohms = ohmsOf(p, world);
      if (ohms !== null) {
        parts.push({ id: p.id, kind: 'R', value: ohms, n1: pins[0], n2: pins[1], of: p.id, was: p.kind });
        readouts.push({ id: p.id, kind: p.kind, nodes: pins, ohms: ohms });
        return;
      }
      parts.push({ id: p.id, kind: p.kind, value: p.value, n1: pins[0], n2: pins[1], ac: p.ac });
    });

    return { parts: parts, probes: probes, nodeCount: next, hasGround: gndRoot !== null,
             placed: placed, readouts: readouts, env: world,
             nodeAt: function (pt) { const k = key(pt); return parent[k] === undefined ? null : nodeOf[find(k)]; } };
  }

  return { build: build, pinsOf: pinsOf, plusFirst: plusFirst };
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

  function problems(net) {
    if (!net.hasGround) return 'No ground. Every circuit needs one, or the node voltages have nothing to be measured against.';
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
      return x ? { x: x } : { error: msg.under };
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

  /* ---- AC, one frequency ---- */
  function acAt(net, w) {
    const devs = devicesOf(net);
    let tangents = null;
    if (devs.length) {
      const op = bias(net);
      if (op.error) return null;
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
      else if (p.kind === 'V') {
        const k = f.idxOf(p);
        if (p.n1 > 0) { A[p.n1 - 1][k] = Lin.cadd(A[p.n1 - 1][k], [1, 0]); A[k][p.n1 - 1] = Lin.cadd(A[k][p.n1 - 1], [1, 0]); }
        if (p.n2 > 0) { A[p.n2 - 1][k] = Lin.csub(A[p.n2 - 1][k], [1, 0]); A[k][p.n2 - 1] = Lin.csub(A[k][p.n2 - 1], [1, 0]); }
        b[k] = [p.value, 0];
      }
    });

    const x = Lin.solve(A, b);
    if (!x) return null;
    const v = [[0, 0]];
    for (let i = 0; i < net.nodeCount - 1; i++) v.push(x[i]);
    return v;
  }

  function ac(net, f1, f2, points) {
    const bad = problems(net);
    if (bad) return { error: bad };
    if (!net.parts.some(function (p) { return p.kind === 'V' || p.kind === 'I'; })) {
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
      const v = acAt(net, 2 * Math.PI * fq);
      if (!v) return { error: 'The circuit is under-determined at ' + fmtEng(fq, 'Hz') + '.' };
      out.push({ f: fq, v: v });
    }
    return { sweep: out };
  }

  /* ---- transient, backward Euler ----
     Backward Euler rather than trapezoidal: it is unconditionally stable and never
     rings on a step, so a learner watching an RC charge sees the physics rather than
     an artefact of the integrator. */
  function tran(net, tStop, h) {
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
    if (devs.length) {
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
    }
    /* h may have been coarsened above, so report the one actually used */
    return { t: times, v: volts, h: h };
  }

  return { dc: dc, ac: ac, tran: tran, acAt: acAt };
})();

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
const Symbols = (function () {
  const DEF = {};
  function define(id, name, draw) { DEF[id] = { id: id, name: name, draw: draw }; }
  function get(id) { return DEF[id] || null; }
  function ids() { return Object.keys(DEF); }

  /* Every draw() works in a box from (-60,-40) to (60,40); the caller scales. */
  define('R', 'Resistor', function (c) {
    c.moveTo(-60, 0); c.lineTo(-30, 0);
    const n = 6, w = 60 / n;
    for (let i = 0; i < n; i++) c.lineTo(-30 + (i + 0.5) * w, i % 2 ? 17 : -17);
    c.lineTo(30, 0); c.lineTo(60, 0);
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
 */
function createCircuit(root, opts) {
  opts = opts || {};
  const GRID = 26;
  const model = opts.model && opts.model.parts
    ? JSON.parse(JSON.stringify(opts.model))
    : { parts: [], wires: [] };
  let seq = model.parts.reduce(function (n, p) {
    const m = /^p(\d+)$/.exec(p.id);
    return m ? Math.max(n, +m[1] + 1) : n;
  }, 0);

  let tool = 'R';
  /* The viewport. `s` is the zoom, `px`/`py` are the world-pixel coordinates of the
     top-left corner of what you can see. Every screen<->grid conversion goes through
     it, so there is one place that knows where things are. */
  let view = { s: 1, px: 0, py: 0 };
  let selIds = new Set();      /* selected part ids */
  let drag = null;             /* a move in progress */
  let marquee = null;          /* a rubber-band selection in progress */
  let panFrom = null;          /* a pan in progress */
  let wireFrom = null;         /* grid point a wire is being drawn from */
  let hover = null;
  let analysis = { mode: 'dc', node: 1, f1: 10, f2: 1e6, tstop: 5e-3 };
  let result = null;
  let disposed = false;

  /* A question that shows a circuit wants the drawing and nothing else — no tools,
     no analysis panel, nothing to click. Same painter, so a diagram can never drift
     from what the editor would show for the same model. */
  if (opts.readOnly) {
    root.innerHTML = '<div class="ckt ckt-ro"><div class="ckt-main">' +
      '<div class="ckt-canvas"><canvas></canvas></div></div></div>';
  } else {
  root.innerHTML =
    '<div class="ckt">' +
      '<div class="ckt-bar">' +
        '<div class="ckt-tools">' +
          [['select', 'Select', 'Select and move parts'], ['wire', 'Wire', 'Draw a wire'],
           ['R', 'R', 'Resistor'], ['C', 'C', 'Capacitor'], ['L', 'L', 'Inductor'],
           ['V', 'V', 'Voltage source'], ['I', 'I', 'Current source'],
           ['GND', 'GND', 'Ground'], ['OUT', 'Probe', 'Mark the output node'],
           ['SW', 'SW', 'Switch — click it on the canvas to open and close it'],
           ['LDR', 'LDR', 'Light sensor — resistance falls as light rises'],
           ['NTC', 'NTC', 'Thermistor — resistance falls as temperature rises'],
           ['POT', 'POT', 'Potentiometer — three pins, a wiper along the track'],
           ['LAMP', 'Lamp', 'Indicator lamp — a resistance that lights with the power in it'],
           ['METER', 'Meter', 'Ammeter — reads the current through it'],
           ['BAR', 'Bar', 'Bar display — reads the node it sits on'],
           ['D', 'D', 'Diode — Shockley, solved by iteration rather than by a 0.7 V rule'],
           ['LED', 'LED', 'LED — the same junction, and it lights when it conducts'],
           ['NPN', 'NPN', 'NPN bipolar — Ebers-Moll'],
           ['PNP', 'PNP', 'PNP bipolar — Ebers-Moll'],
           ['NMOS', 'NMOS', 'N-channel MOSFET — level 1 square law'],
           ['PMOS', 'PMOS', 'P-channel MOSFET — level 1 square law'],
           ['OPAMP', 'Op-amp', 'Op-amp — finite gain, output limited to its rails']].map(function (t) {
            return '<button class="ckt-t" data-tool="' + t[0] + '" title="' + t[2] + '">' + t[1] + '</button>';
          }).join('') +
        '</div>' +
        '<span class="spacer"></span>' +
        '<button class="ckt-t" data-act="zoomout" title="Zoom out (-)">−</button>' +
        '<button class="ckt-t" data-act="zoomin" title="Zoom in (+)">+</button>' +
        '<button class="ckt-t" data-act="fit" title="Fit the drawing to the window (0)">Fit</button>' +
        '<button class="ckt-t" data-act="rotate" title="Rotate the selection (R)">Rotate</button>' +
        '<button class="ckt-t" data-act="delete" title="Delete the selection (Del)">Delete</button>' +
        '<button class="ckt-t" data-act="clear">Clear</button>' +
      '</div>' +
      '<div class="ckt-main">' +
        '<div class="ckt-canvas"><canvas></canvas></div>' +
        '<div class="ckt-side">' +
          '<div class="ckt-panel" data-panel="part"></div>' +
          '<div class="ckt-panel" data-panel="env" hidden></div>' +
          '<div class="ckt-panel">' +
            '<h4>Analysis</h4>' +
            '<div class="seg ckt-modes">' +
              '<button data-an="dc" class="active">Operating point</button>' +
              '<button data-an="ac">Frequency</button>' +
              '<button data-an="tran">Transient</button>' +
            '</div>' +
            '<div class="ckt-opts" data-opts></div>' +
            '<button class="btn success ckt-run">Solve</button>' +
          '</div>' +
          '<div class="ckt-out" data-out></div>' +
        '</div>' +
      '</div>' +
      '<div class="ckt-plot" data-plot hidden><canvas></canvas></div>' +
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

  function P() { return typeof Sandbox !== 'undefined' ? Sandbox.palette() : { ink: '#eee', dim: '#888', faint: '#555', line: '#333', accent: '#C7F751', blue: '#6E9BFF', amber: '#FFC66D', purple: '#A78BFA' }; }

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
    model.parts.forEach(function (p) { Netlist.pinsOf(p).forEach(function (pt) { see(pt[0], pt[1]); }); see(p.x, p.y); });
    model.wires.forEach(function (wr) { see(wr.a[0], wr.a[1]); see(wr.b[0], wr.b[1]); });
    if (!isFinite(x0)) return null;
    return { x0: x0, y0: y0, x1: x1, y1: y1 };
  }

  function zoomTo(scale, anchorSx, anchorSy) {
    const ns = Math.max(0.3, Math.min(4, scale));
    if (anchorSx === undefined) { view.s = ns; paint(); return; }
    /* keep the point under the cursor still: it is the difference between zooming
       and being thrown across the drawing */
    const before = toWorld(anchorSx, anchorSy);
    view.s = ns;
    const after = toWorld(anchorSx, anchorSy);
    view.px += before[0] - after[0];
    view.py += before[1] - after[1];
    paint();
  }

  function zoomFit() {
    const b = contentBounds();
    const box = cv.parentElement.getBoundingClientRect();
    const w = Math.max(320, box.width), h = Math.max(260, box.height);
    if (!b) { view = { s: 1, px: 0, py: 0 }; paint(); return; }
    const pad = 1.5;
    const needW = (b.x1 - b.x0 + pad * 2) * GRID, needH = (b.y1 - b.y0 + pad * 2) * GRID;
    view.s = Math.max(0.3, Math.min(4, Math.min(w / needW, h / needH)));
    view.px = gx(b.x0 - pad) - (w / view.s - needW) / 2;
    view.py = gy(b.y0 - pad) - (h / view.s - needH) / 2;
    paint();
  }

  function selOne() {
    if (selIds.size !== 1) return null;
    const id = selIds.values().next().value;
    return model.parts.find(function (p) { return p.id === id; }) || null;
  }
  function selParts() { return model.parts.filter(function (p) { return selIds.has(p.id); }); }

  function partAt(pt) {
    return model.parts.find(function (p) {
      if (p.kind === 'GND') return p.x === pt[0] && p.y === pt[1];
      return p.x === pt[0] && p.y === pt[1];
    });
  }

  /* ---- reading the answer back off the schematic ----
   *
   * A readout shows the operating point and nothing else. A lamp brightening through
   * a transient would need an animation nobody asked for, and a lamp showing the
   * first point of a frequency sweep would be showing a number that means nothing —
   * so until there is a DC answer on the canvas, the displays sit blank rather than
   * inventing a reading. */
  function dcAt(pt) {
    if (!result || result.kind !== 'dc' || !result.net) return null;
    const n = result.net.nodeAt(pt);
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
  function labelOf(p, k) {
    const n = p.id.replace('p', '');
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

    ctx.save();
    ctx.translate(x, y);
    if (p.rot) ctx.rotate(turnsOf(p) * Math.PI / 2);
    const L = GRID;                       /* pin-to-pin half span */
    ctx.beginPath();
    if (p.kind === 'R') {
      ctx.moveTo(-L, 0); ctx.lineTo(-13, 0);
      for (let i = 0; i < 6; i++) ctx.lineTo(-13 + (i + 0.5) * 26 / 6, (i % 2 ? 6 : -6));
      ctx.lineTo(13, 0); ctx.lineTo(L, 0);
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
      for (let i = 0; i < 6; i++) ctx.lineTo(-13 + (i + 0.5) * 26 / 6, (i % 2 ? 6 : -6));
      ctx.lineTo(13, 0); ctx.lineTo(L, 0);
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
    } else if (turnsOf(p) % 2) ctx.fillText(lab, x + 34, y);
    else ctx.fillText(lab, x, y - 17);
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
       it scales itself to fit and centres what is left. */
    if (ro_ && model.parts.length) {
      let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
      const see = function (px, py) {
        if (px < x0) x0 = px; if (px > x1) x1 = px;
        if (py < y0) y0 = py; if (py > y1) y1 = py;
      };
      model.parts.forEach(function (p2) { Netlist.pinsOf(p2).forEach(function (pt) { see(pt[0], pt[1]); }); see(p2.x, p2.y); });
      model.wires.forEach(function (wr) { see(wr.a[0], wr.a[1]); see(wr.b[0], wr.b[1]); });
      const pad = 1.2;
      const needW = (x1 - x0 + pad * 2) * GRID, needH = (y1 - y0 + pad * 2) * GRID;
      const s2 = Math.min(w / needW, h / needH, 1.6);
      ctx.setTransform(dpr * s2, 0, 0, dpr * s2,
        dpr * ((w - needW * s2) / 2 - (x0 - pad - originX) * GRID * s2 - GRID * s2),
        dpr * ((h - needH * s2) / 2 - (y0 - pad - originY) * GRID * s2 - GRID * s2));
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
       circuit slides underneath. */
    const vx0 = ro_ ? 0 : view.px, vy0 = ro_ ? 0 : view.py;
    const vx1 = vx0 + (ro_ ? w : w / view.s), vy1 = vy0 + (ro_ ? h : h / view.s);
    ctx.fillStyle = pal.faint;
    ctx.globalAlpha = 0.5;
    for (let X = Math.floor(vx0 / GRID) * GRID; X < vx1 + GRID; X += GRID) {
      if (X < GRID) continue;
      for (let Y = Math.floor(vy0 / GRID) * GRID; Y < vy1 + GRID; Y += GRID) {
        if (Y < GRID) continue;
        ctx.fillRect(X - 0.5, Y - 0.5, 1, 1);
      }
    }
    ctx.globalAlpha = 1;

    /* wires */
    ctx.strokeStyle = pal.dim;
    ctx.lineWidth = 2;
    model.wires.forEach(function (wr) {
      ctx.beginPath();
      ctx.moveTo(gx(wr.a[0]), gy(wr.a[1]));
      ctx.lineTo(gx(wr.b[0]), gy(wr.b[1]));
      ctx.stroke();
    });

    /* junction dots where three or more things meet */
    const count = {};
    function bump(pt) { const k = pt[0] + ',' + pt[1]; count[k] = (count[k] || 0) + 1; }
    model.wires.forEach(function (wr) { bump(wr.a); bump(wr.b); });
    model.parts.forEach(function (p) { Netlist.pinsOf(p).forEach(bump); });
    ctx.fillStyle = pal.dim;
    Object.keys(count).forEach(function (k) {
      if (count[k] < 3) return;
      const xy = k.split(',').map(Number);
      ctx.beginPath();
      ctx.arc(gx(xy[0]), gy(xy[1]), 3, 0, Math.PI * 2);
      ctx.fill();
    });

    /* parts */
    model.parts.forEach(function (p) {
      drawPart(p, selIds.has(p.id) ? pal.accent : pal.ink, pal);
    });

    paintMarquee();

    /* the wire being drawn */
    if (wireFrom && hover) {
      ctx.save();
      ctx.setLineDash([4, 4]);
      ctx.strokeStyle = pal.accent;
      ctx.beginPath();
      ctx.moveTo(gx(wireFrom[0]), gy(wireFrom[1]));
      const straight = Math.abs(hover[0] - wireFrom[0]) > Math.abs(hover[1] - wireFrom[1])
        ? [hover[0], wireFrom[1]] : [wireFrom[0], hover[1]];
      ctx.lineTo(gx(straight[0]), gy(straight[1]));
      ctx.stroke();
      ctx.restore();
    }

    /* DC answers, written on the schematic where they belong */
    if (result && result.kind === 'dc' && result.net) {
      ctx.font = '10.5px ui-monospace, monospace';
      ctx.textAlign = 'left';
      const seen = {};
      model.parts.forEach(function (p) {
        Netlist.pinsOf(p).forEach(function (pt) {
          const n = result.net.nodeAt(pt);
          if (n === null || n === 0 || seen[n]) return;
          seen[n] = 1;
          ctx.fillStyle = pal.accent;
          ctx.fillText(fmtEng(result.v[n], 'V'), gx(pt[0]) + 6, gy(pt[1]) - 8);
        });
      });
    }
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
        'Click an empty cell to deselect.</p>';
      return;
    }
    if (!p || p.kind === 'GND' || p.kind === 'OUT') {
      partPanel.innerHTML = '<h4>Component</h4><p class="ckt-hint">' +
        (tool === 'wire' ? 'Click a pin, then click where the wire should end.'
          : tool === 'select' ? 'Click a component to select it.'
          : 'Click the grid to place a ' + PART_KINDS[tool].name.toLowerCase() + '.') + '</p>';
      return;
    }
    const k = PART_KINDS[p.kind];
    partPanel.innerHTML = '<h4>' + k.name + ' ' + esc2(p.id.replace('p', '')) + '</h4>' +
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
          '<span>Wiper</span><input type="range" data-wiper min="0" max="1000" step="1" value="' +
          Math.round((p.wiper === undefined ? 0.5 : p.wiper) * 1000) +
          '" style="height:18px;padding:0;border:0;background:none;accent-color:var(--lime);width:100%">' +
          '<span data-wiperval style="color:var(--lime)">' +
          (p.wiper === undefined ? 0.5 : p.wiper).toFixed(2) + '</span></div>'
        : '') +
      '<p class="ckt-hint" data-note>' + modelNote(p) + '</p>';

    const inp = partPanel.querySelector('[data-val]');
    if (inp) inp.addEventListener('change', function () {
      p.value = parseEng(inp.value, p.value);
      changed();
      paintPart();
    });
    partPanel.querySelectorAll('[data-x]').forEach(function (el) {
      el.addEventListener('change', function () {
        const f = (PART_FIELDS[p.kind] || []).filter(function (q) { return q[0] === el.dataset.x; })[0];
        const v = parseEng(el.value, p[el.dataset.x]);
        p[el.dataset.x] = Math.min(Math.max(isFinite(v) ? v : f[2], f[2]), f[3]);
        changed();
        paintPart();
      });
    });
    const sw = partPanel.querySelector('[data-sw]');
    if (sw) sw.addEventListener('click', function () { toggleSwitch(p); });
    const wip = partPanel.querySelector('[data-wiper]');
    if (wip) wip.addEventListener('input', function () {
      p.wiper = Math.min(Math.max(+wip.value / 1000, 0), 1);
      partPanel.querySelector('[data-wiperval]').textContent = p.wiper.toFixed(2);
      /* The note quotes the two stamped resistances, so it goes stale the instant the
         wiper moves — and it is the one label that exists so the learner can read the
         model rather than trust it. Rewritten in place rather than through
         paintPart(), which would rebuild the slider out from under the pointer. */
      refreshNote();
      retouchSoon();
    });
  }

  /* What the value box means for a kind whose value is not simply "the value". */
  const VALUE_LABEL = {
    LDR: 'R at 10 lx (Ω)', NTC: 'R at 25 °C (Ω)', POT: 'Total (Ω)',
    LAMP: 'Resistance (Ω)', METER: 'Burden (Ω)', BAR: 'Full scale (V)',
    D: 'Is (A)', LED: 'Is (A)', NPN: 'Is (A)', PNP: 'Is (A)',
    NMOS: 'k (A/V²)', PMOS: 'k (A/V²)', OPAMP: 'Open-loop gain',
  };
  /* The extra numbers a kind carries beyond `value`: key, label, and the range it is
     clamped to, because a γ of zero or a negative B is a model that means nothing. */
  const PART_FIELDS = {
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
  };

  /* The model, written where the learner can read it. A sensor whose curve you have
     to take on trust is a magic box, and a magic box teaches nothing — so each of
     these states the equation, its parameters, and what it does NOT model. */
  function modelNote(p) {
    const n = p.id.replace('p', '');
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
    if (sel && note) note.textContent = modelNote(sel);
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
  /* which quantities anything on the canvas actually senses, in a fixed order */
  function envInUse() {
    return ENV_Q.filter(function (q) {
      return model.parts.some(function (p) {
        const k = PART_KINDS[p.kind];
        return k && k.senses === q.key;
      });
    });
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

  function paintOpts() {
    if (analysis.mode === 'ac') {
      optsEl.innerHTML =
        '<label class="ckt-f"><span>From</span><input data-f1 value="' + fmtEng(analysis.f1, 'Hz') + '"></label>' +
        '<label class="ckt-f"><span>To</span><input data-f2 value="' + fmtEng(analysis.f2, 'Hz') + '"></label>';
      optsEl.querySelector('[data-f1]').addEventListener('change', function (e) { analysis.f1 = Math.max(0.01, parseEng(e.target.value, analysis.f1)); });
      optsEl.querySelector('[data-f2]').addEventListener('change', function (e) { analysis.f2 = Math.max(1, parseEng(e.target.value, analysis.f2)); });
    } else if (analysis.mode === 'tran') {
      optsEl.innerHTML = '<label class="ckt-f"><span>Stop after</span><input data-ts value="' + fmtEng(analysis.tstop, 's') + '"></label>';
      optsEl.querySelector('[data-ts]').addEventListener('change', function (e) { analysis.tstop = Math.max(1e-9, parseEng(e.target.value, analysis.tstop)); });
    } else {
      optsEl.innerHTML = '<p class="ckt-hint">Solves the DC operating point and writes each node voltage onto the schematic.</p>';
    }
  }

  /* ---- solving ---- */
  function solve() {
    /* the environment is resolved into resistances here, once, before any stamping */
    const net = Netlist.build(model, env);
    let r;
    if (analysis.mode === 'dc') r = MNA.dc(net);
    else if (analysis.mode === 'ac') r = MNA.ac(net, analysis.f1, analysis.f2, 220);
    else r = MNA.tran(net, analysis.tstop, analysis.tstop / 900);

    if (r.error) {
      result = null;
      plotWrap.hidden = true;
      outEl.innerHTML = '<div class="ckt-err">' + esc2(r.error) + '</div>';
      paint();
      refreshNote();
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
    } else {
      plotWrap.hidden = false;
      const picks = [];
      for (let n = 1; n < net.nodeCount; n++) {
        picks.push('<button data-node="' + n + '"' + (n === analysis.node ? ' class="active"' : '') + '>node ' + n + '</button>');
      }
      outEl.innerHTML = '<div class="seg ckt-nodes">' + picks.join('') + '</div>';
      outEl.querySelectorAll('[data-node]').forEach(function (b) {
        b.addEventListener('click', function () { analysis.node = +b.dataset.node; solveRepaint(); });
      });
      paintPlot();
    }
    paint();
    /* the numbers the note quotes are the ones that just changed */
    refreshNote();
  }
  function solveRepaint() { paintPlot(); outEl.querySelectorAll('[data-node]').forEach(function (b) { b.classList.toggle('active', +b.dataset.node === analysis.node); }); }

  function paintPlot() {
    if (!result || typeof Sandbox === 'undefined') return;
    const box = plotCv.parentElement.getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(320, Math.round(box.width)), h = 190;
    plotCv.width = w * dpr; plotCv.height = h * dpr;
    plotCv.style.width = w + 'px'; plotCv.style.height = h + 'px';
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
    }
  }

  function changed() {
    result = null;
    plotWrap.hidden = true;
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
      dro = new ResizeObserver(function () { paint(); });
      dro.observe(cv.parentElement);
    }
    paint();
    return {
      getModel: function () { return snapshot(); },
      solve: function () { return null; },
      dispose: function () {
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
    hover = toGrid(sp[0], sp[1]);

    if (panFrom) {
      view.px = panFrom.px + (panFrom.sx - sp[0]) / view.s;
      view.py = panFrom.py + (panFrom.sy - sp[1]) / view.s;
      paint();
      return;
    }

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
        selParts().forEach(function (p) { p.x += dx; p.y += dy; });
        drag.from = hover;
        drag.moved = true;
        paint();
      }
      return;
    }

    if (marquee) { marquee.b = toWorld(sp[0], sp[1]); paint(); return; }
    if (wireFrom) paint();
  });

  cv.addEventListener('pointerleave', function () { hover = null; if (wireFrom) paint(); });

  /* Wheel zooms about the cursor. Ctrl+wheel is the browser's own page zoom on some
     setups, so it is left alone. */
  cv.addEventListener('wheel', function (e) {
    if (e.ctrlKey) return;
    e.preventDefault();
    const sp = evPt(e);
    zoomTo(view.s * (e.deltaY < 0 ? 1.12 : 1 / 1.12), sp[0], sp[1]);
  }, { passive: false });

  cv.addEventListener('pointerdown', function (e) {
    const sp = evPt(e);
    const pt = toGrid(sp[0], sp[1]);

    /* Middle button, or space held: pan. Both are what a drawing tool does, and the
       second is the one people already have in their fingers. */
    if (e.button === 1 || spaceDown) {
      panFrom = { sx: sp[0], sy: sp[1], px: view.px, py: view.py };
      cv.setPointerCapture(e.pointerId);
      e.preventDefault();
      return;
    }
    if (e.button !== 0) return;

    if (tool === 'wire') {
      if (!wireFrom) { wireFrom = pt; paint(); return; }
      /* wires stay orthogonal: take the dominant direction */
      const end = Math.abs(pt[0] - wireFrom[0]) > Math.abs(pt[1] - wireFrom[1])
        ? [pt[0], wireFrom[1]] : [wireFrom[0], pt[1]];
      if (end[0] !== wireFrom[0] || end[1] !== wireFrom[1]) {
        model.wires.push({ a: wireFrom, b: end });
        changed();
      }
      wireFrom = null;
      paint();
      return;
    }

    if (tool === 'select') {
      const hit = partAt(pt);
      cv.setPointerCapture(e.pointerId);
      if (hit) {
        if (e.shiftKey) {
          if (selIds.has(hit.id)) selIds.delete(hit.id); else selIds.add(hit.id);
        } else if (!selIds.has(hit.id)) {
          selIds.clear();
          selIds.add(hit.id);
        }
        /* Dragging a part that is already part of a multiple selection moves the
           whole selection; that is why the clear above is conditional. `shift` is
           carried so the click-to-use gesture below can tell a plain click from one
           that was only ever adjusting the selection. */
        down = { sx: sp[0], sy: sp[1], grid: pt, mode: 'maybe-move', hit: hit.id, shift: e.shiftKey };
      } else {
        if (!e.shiftKey) selIds.clear();
        down = { sx: sp[0], sy: sp[1], grid: pt, mode: 'maybe-marquee' };
      }
      paintPart();
      paint();
      return;
    }

    /* placing: refuse to stack two parts on one cell */
    const existing = partAt(pt);
    if (existing) { selIds.clear(); selIds.add(existing.id); paintPart(); paint(); return; }
    const kind = tool;
    const p = { id: 'p' + (seq++), kind: kind, x: pt[0], y: pt[1], rot: 0,
                value: PART_KINDS[kind].def };
    /* kinds that carry state beyond a value start with the registry's defaults, so a
       part is never placed half-defined and then behaves oddly */
    const st = PART_KINDS[kind].state;
    if (st) Object.keys(st).forEach(function (key2) { p[key2] = st[key2]; });
    model.parts.push(p);
    selIds.clear();
    selIds.add(p.id);
    changed();
    paintPart();
  });

  function endPointer(e) {
    if (panFrom) { panFrom = null; return; }
    if (marquee) {
      const x0 = Math.min(marquee.a[0], marquee.b[0]), x1 = Math.max(marquee.a[0], marquee.b[0]);
      const y0 = Math.min(marquee.a[1], marquee.b[1]), y1 = Math.max(marquee.a[1], marquee.b[1]);
      model.parts.forEach(function (p) {
        const wx = gx(p.x), wy = gy(p.y);
        if (wx >= x0 && wx <= x1 && wy >= y0 && wy <= y1) selIds.add(p.id);
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
      const hp = model.parts.filter(function (p) { return p.id === down.hit; })[0];
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

  /* Space is held to pan, the way it is in every drawing tool. Tracked on the
     document because the canvas does not take keyboard focus. */
  let spaceDown = false;
  function onSpaceDown(e) {
    if (e.code !== 'Space' || spaceDown) return;
    if (e.target && /input|textarea/i.test(e.target.tagName)) return;
    spaceDown = true;
    cv.style.cursor = 'grab';
    e.preventDefault();
  }
  function onSpaceUp(e) {
    if (e.code !== 'Space') return;
    spaceDown = false;
    cv.style.cursor = '';
  }
  document.addEventListener('keydown', onSpaceDown);
  document.addEventListener('keyup', onSpaceUp);

  function onKey(e) {
    if (e.target && /input|textarea/i.test(e.target.tagName)) return;
    if (e.key === 'Delete' || e.key === 'Backspace') { doDelete(); e.preventDefault(); }
    else if (e.key === 'r' || e.key === 'R') { doRotate(); }
    else if (e.key === 'Escape') { wireFrom = null; marquee = null; selIds.clear(); paintPart(); paint(); }
    else if ((e.ctrlKey || e.metaKey) && (e.key === 'a' || e.key === 'A')) {
      selIds.clear();
      model.parts.forEach(function (p) { selIds.add(p.id); });
      paintPart(); paint(); e.preventDefault();
    }
    else if (e.key === '+' || e.key === '=') { zoomTo(view.s * 1.2); }
    else if (e.key === '-' || e.key === '_') { zoomTo(view.s / 1.2); }
    else if (e.key === '0') { zoomFit(); }
  }
  document.addEventListener('keydown', onKey);

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
    if (!selIds.size) return;
    /* A wire with nothing left at either end is a wire the learner cannot see the
       purpose of, but it may still be carrying a connection between two other
       things, so deleting parts leaves wires alone. */
    model.parts = model.parts.filter(function (p) { return !selIds.has(p.id); });
    selIds.clear();
    changed();
    paintPart();
  }

  /* A diagram has no tools, no analysis panel and nothing to click, so there is
     nothing below this line to wire up. Returning early is what makes the read-only
     DOM safe to shrink: every lookup after this point assumes the full chrome. */
  root.querySelectorAll('[data-tool]').forEach(function (b) {
    b.addEventListener('click', function () {
      tool = b.dataset.tool;
      wireFrom = null;
      root.querySelectorAll('[data-tool]').forEach(function (o) { o.classList.toggle('on', o === b); });
      paintPart();
      paint();
    });
  });
  root.querySelector('[data-act="zoomin"]').addEventListener('click', function () { zoomTo(view.s * 1.2); });
  root.querySelector('[data-act="zoomout"]').addEventListener('click', function () { zoomTo(view.s / 1.2); });
  root.querySelector('[data-act="fit"]').addEventListener('click', zoomFit);
  root.querySelector('[data-act="rotate"]').addEventListener('click', doRotate);
  root.querySelector('[data-act="delete"]').addEventListener('click', doDelete);
  root.querySelector('[data-act="clear"]').addEventListener('click', function () {
    model.parts = []; model.wires = []; selIds.clear();
    view = { s: 1, px: 0, py: 0 };
    changed(); paintPart();
  });
  root.querySelectorAll('[data-an]').forEach(function (b) {
    b.addEventListener('click', function () {
      analysis.mode = b.dataset.an;
      root.querySelectorAll('[data-an]').forEach(function (o) { o.classList.toggle('active', o === b); });
      paintOpts();
    });
  });
  root.querySelector('.ckt-run').addEventListener('click', solve);

  let ro = null;
  if (typeof ResizeObserver !== 'undefined') {
    ro = new ResizeObserver(function () { paint(); if (result && !plotWrap.hidden) paintPlot(); });
    ro.observe(cv.parentElement);
  }

  root.querySelector('[data-tool="R"]').classList.add('on');
  paintPart();
  paintEnv();
  paintOpts();
  paint();

  return {
    getModel: function () { return snapshot(); },
    solve: solve,
    dispose: function () {
      disposed = true;
      document.removeEventListener('keydown', onKey);
      /* space-to-pan is tracked on the document because the canvas takes no keyboard
         focus, so it has to be released here or every editor ever opened keeps
         listening for the rest of the session */
      document.removeEventListener('keydown', onSpaceDown);
      document.removeEventListener('keyup', onSpaceUp);
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
    if (!net.hasGround) throw new Error('Add a ground before ' + what + ' can mean anything.');
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
    /* what a dynamic part actually resolved to in this environment */
    ohms: function (id) {
      const r = net.readouts.filter(function (x) { return x.id === id; })[0];
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
      const p = ((model && model.parts) || []).filter(function (q) { return q.id === id; })[0];
      if (!p || !Devices.is(p.kind)) {
        throw new Error('There is no non-linear device called ' + id + ' in this circuit.');
      }
      const r = this.dc();
      const seen = net.readouts.filter(function (x) { return x.id === id; })[0];
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
