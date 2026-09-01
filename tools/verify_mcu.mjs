/**
 * verify_mcu.mjs — the resilience, containment and accessibility gate for the sketch.
 *
 * Track 6's row of the curriculum names src/app.js, src/desk.js and src/circuit.js.
 * All three have gates. The microcontroller does not, and six Track 6 and Track 2
 * cycles in a row wrote down that it was being left: cycle 6 ("its own subsystem, in
 * src/mcu.js as much as here"), then 8, 12, 15, 19 and 21, each recording it and none
 * taking it. It is the only part of this application with a SECOND LANGUAGE in it —
 * nine hundred lines of lexer, parser and coroutine machine that run text a learner
 * typed — and nothing has ever driven it.
 *
 *   * A SKETCH THAT REACHED OFF THE CANVAS. Five lookup tables a learner's identifiers
 *     index — the scope chain's `vars`, `fns`, `defines`, `BUILTIN` and `CONSTANTS` —
 *     were `{}`, which inherits from Object.prototype. So `toString` was a name every
 *     one of them already had. `toString();` produced "b.f is not a function", which is
 *     the engine talking on a panel whose own file header promises a learner never has
 *     to read it; `void toString() { }` was refused as a duplicate of a function nobody
 *     wrote; and `toString = 5;` ran clean and left {v:5,f:false} on
 *     Object.prototype.toString — a sketch writing on a builtin the whole page shares,
 *     against a header that says "a tree walker can only do what this file gives it a
 *     way to do, which is arithmetic and twelve pins".
 *
 *   * BUILTINS THAT NEVER ASKED. arith() refuses a string by name on its line. The
 *     twenty builtins never did: sqrt("x") printed NaN, abs("x") printed 0, min("x",1)
 *     returned 1, pinMode(2,"OUTPUT") silently made the pin an INPUT, and
 *     analogWrite(pin,"x") silently drove zero duty.
 *
 *   * INFINITY, AGAINST THE FILE'S OWN STATED POLICY. Division by zero stops with a
 *     paragraph about infinity propagating. pow(10,400) returned Infinity, and
 *     `int y = pow(10,400);` stored 0, because Infinity|0 is 0 — a silent zero that
 *     looks like an answer.
 *
 *   * A CONSOLE CAP THAT CAPPED NOTHING. CONSOLE_MAX counts LINES, and a sketch that
 *     never prints a newline has one line. `void loop(){ print("x"); }` held a single
 *     entry that reached 59,999 characters in sixty time steps with `dropped` reading 0.
 *
 *   * A SKETCH TYPED AND THEN LOST. The textarea wrote p.code on input and called
 *     changed() only on `change` — which fires on blur. dispose() empties the panel,
 *     and removing a focused element fires no pending change, so leaving by the footer,
 *     the rail or the back button handed progress the DEFAULT sketch. Measured: onChange
 *     fired 0 times and the saved model was the one the part was placed with.
 *
 *   * A PANEL NOTHING COULD READ. The sketch box was the one control on that panel
 *     captioned by a bare <span> rather than a <label>; the syntax error was a plain
 *     <div> that changed as you typed and announced nothing; and the console scrolled
 *     with no tabindex, so a learner's own program output past 150px was reachable by
 *     wheel and by nothing else.
 *
 *     node tools/verify_mcu.mjs
 */
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { El, windowShim, WIN } from './dom_stub.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

let fails = 0;
const ok = (tag, msg) => console.log('[ok  ] ' + tag.padEnd(8) + ' ' + msg);
const bad = (tag, msg) => { fails++; console.log('[FAIL] ' + tag.padEnd(8) + ' ' + msg); };
/* A section that throws has still found something, but it loses every finding recorded
   before it — verify_circuit_ui's first run reported a TypeError instead of the four
   defects it already had. Falling over is itself a failure, and the run continues. */
function section(tag, fn) {
  try { fn(); } catch (e) { bad(tag, 'the section itself fell over: ' + ((e && e.stack) || e)); }
}

/* ---------------------------------------------------------------- loading it */
/* mcu.js is an IIFE assigned to a const, and circuit.js reads that const by bare name.
   Concatenated in one Function body so mcuAvailable() is TRUE: loaded apart, the panel
   takes its "not in this build" branch and every panel finding below would be hidden
   behind a message about the build. The `src` argument lets the mutation run at the
   bottom hand in a deliberately broken copy. */
function load(mcuSrc, cktSrc) {
  const mod = { exports: {} };
  new Function('module', 'window', 'requestAnimationFrame', 'ResizeObserver', 'devicePixelRatio',
    (mcuSrc === undefined ? readFileSync(join(ROOT, 'src', 'mcu.js'), 'utf8') : mcuSrc) + '\n' +
    (cktSrc === undefined ? readFileSync(join(ROOT, 'src', 'circuit.js'), 'utf8') : cktSrc) +
    '\nmodule.exports = { MCU, createCircuit, MCU_SKETCH };'
  )(mod, windowShim, (fn) => fn(), undefined, 1);
  return mod.exports;
}
const LIVE = load();

/* The twelve pins the panel's board model gives a sketch, standing on their own so the
   interpreter can be driven without a netlist. A0..A3 are the four with a converter. */
function board() {
  const st = {};
  for (let i = 0; i <= 17; i++) st[i] = { mode: 'in', drive: 0 };
  return {
    pinName: (p) => (p >= 0 && p <= 17 ? 'D' + p : null),
    pinList: () => 'D0 to D17',
    adcList: () => 'A0 to A3',
    mode: (n) => st[n].mode,
    setMode: (n, m) => { st[n].mode = m; },
    drive: (n, d) => { st[n].drive = d; },
    readDigital: () => 0,
    readAnalog: (n) => (n >= 14 ? 512 : null),
    _st: st,
  };
}

/* Compile and run, the way mcuRig does: a budget of instructions per time step, and the
   clock advanced between them. Returns everything the panel can see. */
function run(MCU, code, steps = 30, ops = 1500, b, h = 1e-4) {
  const c = MCU.compile(String(code));
  if (c.error) return { compile: c.error, fault: c.error, board: b };
  b = b || board();
  const m = MCU.machine(c.program, b);
  for (let i = 0; i < steps; i++) m.advance(i * h, ops);
  const st = m.state();
  return { state: st, fault: st.fault, console: m.console(), board: b };
}
const message = (r) => (r.fault ? String(r.fault.message) : '');

/* Anything here is the engine talking rather than a sentence written for a learner —
   the same rule verify_desk.mjs holds its calculator to, and for the same reason: a
   learner debugging a sketch is already holding two things that might be wrong.
 *
 * IN TWO PARTS, AND THE SPLIT IS A DEFECT THIS GATE HAD. The first run copied desk's
 * single case-insensitive pattern, and it failed seven correct messages: the fix for
 * the infinity defect says "is infinity" and "is not a number" in English, on purpose,
 * because that is what a learner needs to read — and /\bInfinity\b/i matches it. So the
 * engine's own two spellings are matched CASE-SENSITIVELY, which is how JavaScript
 * writes them and how no sentence in this codebase does; the phrases that are engine
 * talk however they are capitalised stay insensitive. A gate that fails correct code is
 * the same defect as one that passes broken code, and it fails louder. */
const ENGINE_SAYS = /call stack|\[object|RangeError|TypeError|is not a function|cannot read|b\.f\b/i;
const ENGINE_SPELLS = /\bNaN\b|\bundefined\b|\bInfinity\b/;
const ENGINE = { test: (s) => ENGINE_SAYS.test(String(s)) || ENGINE_SPELLS.test(String(s)) };

let drives = 0;

/* ================================================================ 1. sealed tables */
/* Every name that rides in on Object.prototype, driven through each of the five ways a
   sketch can name something. None may reach the engine, and none may leave a mark on
   anything outside the machine. */
section('sealed', () => {
  const NAMES = Object.getOwnPropertyNames(Object.prototype)
    .concat(['__proto__', 'prototype', 'name', 'length', 'call', 'apply', 'bind']);
  const SHAPES = [
    ['called', (n) => 'void loop(){ ' + n + '(); }'],
    ['read', (n) => 'void loop(){ int q = ' + n + '; }'],
    ['assigned', (n) => 'void loop(){ ' + n + ' = 5; }'],
    ['printed', (n) => 'void loop(){ println(' + n + '); }'],
    ['declared', (n) => 'void loop(){ int ' + n + ' = 5; println(' + n + '); }'],
    ['defined', (n) => 'void ' + n + '(){ } void loop(){ ' + n + '(); }'],
  ];
  let checked = 0, leaked = 0;
  for (const n of NAMES) {
    for (const [shape, mk] of SHAPES) {
      const r = run(LIVE.MCU, mk(n), 4, 400);
      checked++; drives++;
      const msg = message(r);
      if (msg && ENGINE.test(msg)) {
        bad('sealed', '`' + n + '` ' + shape + ' answers with the engine: ' + msg.slice(0, 70));
        leaked++;
      }
    }
  }
  /* The containment half. A name that merely errors politely is not enough: the
     question is whether running a sketch can change anything the page shares. */
  const WITNESS = ['toString', 'valueOf', 'constructor', 'hasOwnProperty', 'isPrototypeOf'];
  for (const n of WITNESS) {
    run(LIVE.MCU, 'void loop(){ ' + n + ' = 5; }', 4, 400);
    run(LIVE.MCU, 'void loop(){ int ' + n + ' = 5; }', 4, 400);
    drives += 2;
    const target = Object.prototype[n];
    if (target && Object.prototype.hasOwnProperty.call(target, 'val')) {
      bad('sealed', 'a sketch assigning to `' + n + '` wrote onto Object.prototype.' + n +
        ' — it reached off this canvas and onto a builtin the whole page shares');
      delete target.val;
    }
  }
  if (({}).val !== undefined || Object.prototype.type !== undefined) {
    bad('sealed', 'Object.prototype carries a field a sketch put there');
  }
  /* And the two the sealing is supposed to have MADE work, so the fix is not just a
     wall: an ordinary name that happens to collide is an ordinary variable. */
  const own = run(LIVE.MCU, 'void loop(){ int toString = 7; println(toString); }', 4, 400);
  if (own.console.join('') !== '7'.repeat(own.console.length) || !own.console.length) {
    bad('sealed', 'a variable called toString does not behave like a variable: ' +
      JSON.stringify(own.console.slice(0, 2)) + ' ' + message(own).slice(0, 60));
  }
  const proto = run(LIVE.MCU, 'void loop(){ int __proto__ = 3; println(__proto__); }', 4, 400);
  if (proto.console[0] !== '3') {
    bad('sealed', '`int __proto__` is not an ordinary variable: ' +
      JSON.stringify(proto.console[0]) + ' ' + message(proto).slice(0, 60));
  }
  const fn = run(LIVE.MCU, 'int toString(){ return 4; } void loop(){ println(toString()); }', 4, 400);
  if (fn.console[0] !== '4') {
    bad('sealed', 'a function called toString is refused as a duplicate of one nobody wrote: ' +
      message(fn).slice(0, 70));
  }
  if (!leaked) {
    ok('sealed', NAMES.length + ' inherited names x ' + SHAPES.length + ' shapes = ' + checked +
      ' sketches: none reaches the engine, none marks Object.prototype, and the four ' +
      'that collide with real variables still work');
  }
});

/* ================================================================ 2. no engine talk */
section('engine', () => {
  const HOSTILE = [
    '', '   ', '\n\n\n', '//nothing', '/* never closed',
    'void loop(){', 'void loop(){ }}', 'void loop(){ ; ; ; }',
    'void loop(){ int a; a = a + 1; }',
    'void loop(){ int a = 1/0; }', 'void loop(){ float a = 1.0/0.0; }',
    'void loop(){ int a = 5 % 0; }',
    'void loop(){ int a[3]; }', 'void loop(){ Wire.begin(); }',
    'void loop(){ nosuch(); }', 'void loop(){ println(nosuch); }',
    'void loop(){ int a = 1; int a = 2; }',
    'void loop(){ return 1; }', 'int f(){ } void loop(){ f(); }',
    'void f(){ return 1; } void loop(){ f(); }',
    'int f(int x){ return f(x+1); } void loop(){ f(0); }',
    'void loop(){ while(1){ } }', 'void loop(){ for(;;){ } }',
    'void loop(){ }', 'void setup(){ }',
    'void loop(){ digitalWrite(99, HIGH); }', 'void loop(){ analogRead(2); }',
    'void loop(){ pinMode(3, 7); }', 'void loop(){ delay(-5); }',
    'void loop(){ delay(1e9); }', 'void loop(){ println("unclosed }',
    "void loop(){ println('ab'); }", 'void loop(){ println(0x); }',
    '#define X\nvoid loop(){ }', '#pragma once\nvoid loop(){ }',
    '#define X 2\nvoid loop(){ println(X); }',
    'void loop(){ Serial.read(); }', 'void loop(){ Other.print(1); }',
    'void loop(){ println(1 ? 2 : 3); }', 'void loop(){ int x = 3; x <<= 40; println(x); }',
    'void loop(){ println(1e400); }', 'void loop(){ println(sqrt(-1)); }',
    'void loop(){ println("a" + 1); }', 'void loop(){ int x = "a"; }',
    'void setup(int a){ } void loop(){ }',
    'void loop(){ ++5; }', 'void loop(){ 5 = 6; }',
  ];
  let clean = 0;
  for (const src of HOSTILE) {
    let r;
    try { r = run(LIVE.MCU, src, 8, 600); }
    catch (e) { bad('engine', JSON.stringify(src.slice(0, 34)) + ' threw out of the machine: ' + e.message); continue; }
    drives++;
    const msg = message(r);
    if (msg && ENGINE.test(msg)) {
      bad('engine', JSON.stringify(src.slice(0, 34)) + ' answers with the engine: ' + msg.slice(0, 70));
      continue;
    }
    if (msg && !/[.!]$/.test(msg.trim())) {
      bad('engine', JSON.stringify(src.slice(0, 34)) + ' answers with a fragment: ' + msg.slice(0, 70));
      continue;
    }
    for (const line of r.console || []) {
      if (ENGINE.test(line)) {
        bad('engine', JSON.stringify(src.slice(0, 34)) + ' PRINTS the engine: ' + line.slice(0, 50));
      }
    }
    clean++;
  }
  /* The one sketch every learner meets, which no gate has ever compiled. It blinks on
     delay(200), so the clock has to cover more than a millisecond or it never leaves
     the first delay — which is what this check said the first time it ran. */
  const d = run(LIVE.MCU, LIVE.MCU_SKETCH, 60, 2000, undefined, 0.02);
  if (d.fault) bad('engine', 'the default sketch a new MCU is placed with does not run: ' + message(d));
  else if (!d.state.loops) bad('engine', 'the default sketch never completed an iteration of loop() ' +
    'over ' + (60 * 0.02) + ' s of simulated time');
  if (clean === HOSTILE.length) {
    ok('engine', HOSTILE.length + ' hostile sketches — empty, unclosed, undeclared, ' +
      'endless, out of range — every one answered with a sentence, none with the engine · ' +
      'the default sketch runs ' + d.state.loops + ' iterations');
  }
});

/* ================================================================ 3. text and types */
section('types', () => {
  /* Every builtin the panel offers, and which of them may see a string. */
  const TEXT_OK = new Set(['print', 'println', 'Serial.print', 'Serial.println', 'Serial.begin']);
  const CALLS = {
    pinMode: 'pinMode("x", OUTPUT)', digitalWrite: 'digitalWrite("x", HIGH)',
    analogWrite: 'analogWrite("x", 10)', digitalRead: 'digitalRead("x")',
    analogRead: 'analogRead("x")', delay: 'delay("x")', delayMicroseconds: 'delayMicroseconds("x")',
    map: 'map("x",0,1,0,2)', constrain: 'constrain("x",0,1)', min: 'min("x",1)', max: 'max("x",1)',
    abs: 'abs("x")', sqrt: 'sqrt("x")', pow: 'pow("x",2)', sin: 'sin("x")', cos: 'cos("x")',
    tan: 'tan("x")', floor: 'floor("x")', ceil: 'ceil("x")', round: 'round("x")',
  };
  let refused = 0;
  for (const [name, call] of Object.entries(CALLS)) {
    const r = run(LIVE.MCU, 'void setup(){ } void loop(){ ' + call + '; }', 4, 400);
    drives++;
    if (!r.fault) {
      bad('types', call + ' took a string and ran anyway — arith() refuses one by name and ' +
        'this did not');
      continue;
    }
    if (!new RegExp(name.replace('.', '\\.')).test(message(r))) {
      bad('types', call + ' refused without naming ' + name + ': ' + message(r).slice(0, 70));
      continue;
    }
    refused++;
  }
  /* The other half: the ones that MUST take a string, or the console has no purpose. */
  for (const p of ['print("hi")', 'println("hi")', 'Serial.print("hi")', 'Serial.println("hi")', 'Serial.begin(9600)']) {
    const r = run(LIVE.MCU, 'void loop(){ ' + p + '; }', 3, 300);
    drives++;
    if (r.fault) bad('types', p + ' was refused a string, and printing is what strings are for: ' + message(r).slice(0, 60));
  }
  /* And the second pin argument, which reaches the board rather than arithmetic:
     digitalWrite(p,"HIGH") used to write LOW and analogWrite(p,"x") zero duty. */
  const b = board();
  const w = run(LIVE.MCU, 'void setup(){ pinMode(3, OUTPUT); } void loop(){ digitalWrite(3, "HIGH"); }', 4, 400, b);
  drives++;
  if (!w.fault) bad('types', 'digitalWrite(3, "HIGH") drove the pin to ' + b._st[3].drive + ' instead of saying so');
  if (refused === Object.keys(CALLS).length && TEXT_OK.size === 5) {
    ok('types', refused + ' builtins refuse a string by their own name, the ' + TEXT_OK.size +
      ' that print still take one, and a pin written with text is refused rather than driven low');
  }
});

/* ================================================================ 4. finite numbers */
section('finite', () => {
  const CASES = [
    ['float y = pow(10,400);', 'pow'],
    ['int y = pow(10,400);', 'pow'],
    ['float y = pow(-1, 0.5);', 'pow'],
    ['float y = 1e308 * 10.0;', 'product'],
    ['float y = 1e308 + 1e308;', 'sum'],
    ['float y = -1e308 - 1e308;', 'difference'],
    ['float y = 1e400;', 'number'],
    ['float y = 1.0 / 0.0;', 'zero'],
  ];
  let stopped = 0;
  for (const [stmt, word] of CASES) {
    const r = run(LIVE.MCU, 'void loop(){ ' + stmt + ' println(y); }', 4, 400);
    drives++;
    if (!r.fault) {
      bad('finite', stmt + ' ran and printed ' + JSON.stringify(r.console[0]) +
        ' — the file stops a division by zero for exactly this reason');
      continue;
    }
    if (ENGINE.test(message(r))) { bad('finite', stmt + ' answers with the engine'); continue; }
    if (!message(r).toLowerCase().includes(word)) {
      bad('finite', stmt + ' refused without saying where it came from: ' + message(r).slice(0, 70));
      continue;
    }
    stopped++;
  }
  /* The one that made this worth doing: stored into an int, Infinity is 0. */
  const silent = run(LIVE.MCU, 'void loop(){ int y = pow(10,400); println(y); }', 4, 400);
  if (!silent.fault && silent.console[0] === '0') {
    bad('finite', 'int y = pow(10,400) stored 0 and printed it as an answer');
  }
  /* And ordinary arithmetic is untouched — a floor that refuses real sums is worse. */
  const fine = run(LIVE.MCU, 'void loop(){ float y = 1e300 / 1e10; println(y); }', 3, 300);
  drives++;
  if (fine.fault) bad('finite', 'an ordinary large quotient was refused: ' + message(fine).slice(0, 60));
  if (stopped === CASES.length) {
    ok('finite', stopped + ' ways to make an infinity or a NaN, every one stopped on the line ' +
      'that made it and named for what made it · 1e300/1e10 still answers');
  }
});

/* ================================================================ 5. bounded */
section('bounded', () => {
  /* The console, in the two ways it can be too much: too many lines, and one line too
     long. The second is the one CONSOLE_MAX never saw. */
  const many = run(LIVE.MCU, 'void loop(){ println("x"); }', 60, 4000);
  drives++;
  if (many.console.length > 400) bad('bounded', 'the line cap let ' + many.console.length + ' lines through');
  if (!many.state.dropped) bad('bounded', 'lines were dropped and the panel is told 0');

  const long = run(LIVE.MCU, 'void loop(){ print("x"); }', 80, 4000);
  drives++;
  const held = long.console.join('').length;
  if (held > 20000) {
    bad('bounded', 'a sketch that never prints a newline held ' + held +
      ' characters in ' + long.console.length + ' line(s) — the line cap counts lines, and there is one');
  }
  if (!long.state.cut) {
    bad('bounded', 'output was thrown away and nothing on the panel says so');
  }
  /* A single print of a string full of newlines, which overshoots the line cap inside
     one call rather than across calls. */
  const burst = run(LIVE.MCU, 'void loop(){ println("a\\nb\\nc\\nd\\ne"); }', 60, 4000);
  drives++;
  if (burst.console.length > 410) bad('bounded', 'one print of five lines overshot the cap to ' + burst.console.length);

  /* Recursion, the stall watchdog, and an endless loop that must cost nothing. */
  const deep = run(LIVE.MCU, 'int f(int x){ return f(x+1); } void loop(){ f(0); }', 6, 900);
  drives++;
  if (!deep.fault || !/deep/.test(message(deep))) {
    bad('bounded', 'runaway recursion was not caught by name: ' + message(deep).slice(0, 60));
  }
  const stall = run(LIVE.MCU, 'void loop(){ int i = 0; while(1){ i = i + 1; } }', 120, 800);
  drives++;
  if (!stall.fault || !/stuck/.test(message(stall))) {
    bad('bounded', 'a loop that can neither change the circuit nor notice it was not caught: ' + message(stall).slice(0, 60));
  }
  const idle = run(LIVE.MCU, 'void loop(){ }', 200, 800);
  drives++;
  if (idle.fault) bad('bounded', 'an empty loop() faulted: ' + message(idle).slice(0, 60));
  if (idle.state.loops < 100) bad('bounded', 'an empty loop() only got round ' + idle.state.loops + ' times in 200 steps');

  /* delay() has to sleep on the simulation clock, not for a number of resumes. */
  const naps = run(LIVE.MCU, 'void loop(){ println(1); delay(1000); }', 40, 4000);
  drives++;
  if (naps.console.length !== 1) {
    bad('bounded', 'delay(1000) over 4 ms of simulated time printed ' + naps.console.length +
      ' times, so it slept for resumes rather than for time');
  }
  if (!fails) {
    ok('bounded', 'the console holds at most 400 lines and 20000 characters and reports both cuts · ' +
      'recursion, a stalled loop and an endless one each answered · an empty loop() ran ' +
      idle.state.loops + ' iterations for nothing · delay() sleeps on the clock');
  }
});

/* ================================================================ 6. lexer edges */
section('lexer', () => {
  const CASES = [
    ["void loop(){ println('\\q'); }", 'escape', 'an unknown escape used to lex as 117 — the "u" of "undefined"'],
    ['void loop(){ println(0x); }', 'digits', '0x with nothing after it used to be 0'],
    ['void loop(){ println(0b); }', 'digits', '0b with nothing after it used to be 0'],
    ['void loop(){ println("a); }', 'closed', 'an unclosed string'],
    ['/* never closed\nvoid loop(){ }', 'closed', 'an unclosed block comment'],
    ["void loop(){ println('ab'); }", 'exactly one', 'a two-character literal'],
    ['void loop(){ println(@); }', 'no "@"', 'a character not in the language'],
  ];
  let named = 0;
  for (const [src, want, why] of CASES) {
    const r = run(LIVE.MCU, src, 3, 300);
    drives++;
    if (!r.fault) { bad('lexer', why + ' was accepted: ' + JSON.stringify(r.console[0])); continue; }
    if (!message(r).includes(want)) {
      bad('lexer', why + ' was refused without saying "' + want + '": ' + message(r).slice(0, 70));
      continue;
    }
    named++;
  }
  /* The escapes that DO exist still work, or the refusal above is a regression. */
  const good = run(LIVE.MCU, "void loop(){ println('\\n'); println('\\t'); println('A'); }", 3, 400);
  drives++;
  if (good.fault) bad('lexer', 'a character literal that is fine was refused: ' + message(good).slice(0, 60));
  else if (good.console.slice(0, 3).join(',') !== '10,9,65') {
    bad('lexer', "'\\n', '\\t' and 'A' lex as " + good.console.slice(0, 3).join(',') + ' rather than 10,9,65');
  }
  if (named === CASES.length) {
    ok('lexer', named + ' malformed literals refused by name rather than lexed into a ' +
      'plausible number · the four escapes that exist still give 10, 9 and 65');
  }
});

/* ================================================================ 7. the panel */
/* Places an MCU with the keyboard — the route verify_circuit_ui drives — which leaves
   the new part selected, so the panel under test is the sketch panel. */
function mountMcu(exports, grounded) {
  const root = new El('div');
  let saves = 0, last = null;
  const handle = exports.createCircuit(root, {
    model: { parts: [], wires: [] },
    onChange: (m) => { saves++; last = m; },
  });
  const cv = root.querySelector('.ckt-canvas canvas');
  const tool = (t) => { const b = root.querySelector('[data-tool="' + t + '"]'); b.dispatchEvent({ type: 'click', target: b }); };
  const k = (key, n = 1) => { for (let i = 0; i < n; i++) cv.dispatchEvent({ type: 'keydown', key, code: key,
    target: cv, shiftKey: false, ctrlKey: false, metaKey: false, altKey: false }); };
  tool('MCU'); cv.focus(); k('ArrowRight'); k('ArrowDown'); k('Enter');
  if (grounded) {
    /* A transient needs a reference or the matrix is singular and no sketch ever runs —
       so the console, which only exists after one has, could not be reached at all.
       pinsOf puts an MCU's GND at [x + MCU_W, y + row], side 1 row 6, and a pin joins by
       SITTING on a cell: the same test that decides whether a pin meets a wire. Then
       back to the origin and select, because paintPart paints the selected part and the
       console is on the panel. */
    tool('GND'); k('ArrowRight', 4); k('ArrowDown', 6); k('Enter');
    tool('select'); k('ArrowLeft', 4); k('ArrowUp', 6); k('Enter');
  }
  return { root, handle, cv, k, tool,
    ta: () => root.querySelector('[data-code]'),
    tran: () => { const b = root.querySelector('[data-an="tran"]'); b.dispatchEvent({ type: 'click', target: b }); },
    said: () => String((root.querySelector('[data-say]') || {}).textContent || '').trim(),
    saves: () => saves, last: () => last };
}

section('panel', () => {
  const h = mountMcu(LIVE);
  const ta = h.ta();
  if (!ta) { bad('panel', 'placing an MCU with the keyboard produced no sketch box'); return; }
  let held = 0;

  const id = ta.getAttribute('id');
  if (!id) bad('panel', 'the sketch box has no id, so nothing can be wired to it'); else held++;
  /* A <label>, as every other field on this panel is. A <span> beside a control is a
     caption for the eye and nothing in the accessibility tree. */
  const label = ta.closest('label');
  if (!label) bad('panel', 'the sketch box is not inside a <label> — it reads as an unlabelled textarea');
  else if (label.getAttribute('for') !== id) bad('panel', 'the label does not point at the sketch box');
  else held++;

  const errId = ta.getAttribute('aria-describedby');
  const box = h.root.querySelector('[data-built]');
  if (!box) bad('panel', 'there is no box for a syntax error');
  else if (box.getAttribute('id') !== errId) bad('panel', 'aria-describedby does not point at the error box');
  else held++;
  if (box && box.getAttribute('aria-live') !== 'polite') {
    bad('panel', 'the syntax error changes as the learner types and is not a live region');
  } else held++;
  if (ta.getAttribute('aria-invalid') !== 'false') {
    bad('panel', 'a sketch that compiles is marked invalid');
  } else held++;

  /* Typing something broken has to reach both channels — and only after the debounce,
     because a live region rewritten on every keystroke reads a fresh sentence into a
     screen reader for every letter of a half-typed name. */
  ta.value = 'void loop({';
  ta.dispatchEvent({ type: 'input', target: ta });
  drives++;
  if (box.innerHTML.trim() !== '') bad('panel', 'the diagnosis was written on the keystroke rather than after the pause');
  else held++;
  h.handle.dispose();
  if (held === 6) ok('panel', held + ' contracts hold on a freshly painted sketch box: an id, a ' +
    '<label> that points at it, an error box aria-describedby points at, that box a polite ' +
    'live region, aria-invalid false on a sketch that compiles, and nothing written on the keystroke');
});

/* The debounced halves of the panel, and the three exits, need a clock — so they run
   after the synchronous sections rather than inside them. */
async function panelAsync() {
  let held = 0;
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));

  /* --- the diagnosis arrives, on both channels --- */
  const h = mountMcu(LIVE);
  const ta = h.ta();
  ta.value = 'void loop({';
  ta.dispatchEvent({ type: 'input', target: ta });
  await wait(700);
  const box = h.root.querySelector('[data-built]');
  drives++;
  if (!/ckt-err/.test(box.innerHTML)) bad('panel', 'a broken sketch produced no diagnosis after the pause');
  else if (ENGINE.test(box.innerHTML)) bad('panel', 'the diagnosis on the panel is the engine talking');
  else held++;
  if (ta.getAttribute('aria-invalid') !== 'true') bad('panel', 'a sketch that does not compile is not marked invalid');
  else held++;
  ta.value = 'void loop(){ }';
  ta.dispatchEvent({ type: 'input', target: ta });
  await wait(700);
  if (box.innerHTML.trim() !== '') bad('panel', 'the diagnosis stayed after the sketch was fixed');
  else held++;
  if (ta.getAttribute('aria-invalid') !== 'false') bad('panel', 'a fixed sketch is still marked invalid');
  else held++;
  h.handle.dispose();

  /* --- the console is reachable from a keyboard --- */
  const h2 = mountMcu(LIVE, true);
  h2.ta().value = 'void setup(){ println("hello"); }\nvoid loop(){ println(millis()); delay(1); }';
  h2.ta().dispatchEvent({ type: 'change', target: h2.ta() });
  h2.tran();
  h2.handle.solve();
  drives++;
  const pre = h2.root.querySelectorAll('pre')[0];
  if (!pre) {
    bad('panel', 'a sketch that printed produced no console');
  } else {
    if (pre.getAttribute('tabindex') !== '0') {
      bad('panel', 'the console scrolls and takes no focus — its overflow is reachable by wheel and by nothing else');
    } else held++;
    if (!pre.getAttribute('aria-labelledby') && !pre.getAttribute('aria-label')) {
      bad('panel', 'the console takes focus and has no name');
    } else held++;
    if (pre.getAttribute('aria-live')) {
      bad('panel', 'the console is a live region — a sketch printing every time step would read hundreds of lines aloud');
    } else held++;
  }
  if (!/finished/.test(h2.said())) bad('panel', 'a transient that ran was not announced');
  else if (/stopped at line/.test(h2.said())) bad('panel', 'a sketch that ran clean was reported as stopped');
  else held++;
  h2.handle.dispose();

  /* --- a sketch that STOPS ends the run, so the run's own sentence has to say so.
         It was said under the plot and on the part panel, both of which a screen reader
         has to go and find; the trace being flat is the thing it explains. --- */
  const h3 = mountMcu(LIVE, true);
  h3.ta().value = 'void setup(){ } void loop(){ int y = 1/0; }';
  h3.ta().dispatchEvent({ type: 'change', target: h3.ta() });
  h3.tran();
  h3.handle.solve();
  drives++;
  if (!/stopped at line/.test(h3.said())) {
    bad('panel', 'a sketch that faulted and ended the run was not in the sentence that ' +
      'reports the run: ' + JSON.stringify(h3.said().slice(0, 90)));
  } else if (ENGINE.test(h3.said())) {
    bad('panel', 'what was announced is the engine talking');
  } else held++;
  h3.handle.dispose();

  /* --- ids are unique across editors on one page --- */
  const a = mountMcu(LIVE), b = mountMcu(LIVE);
  drives += 2;
  if (a.ta().getAttribute('id') === b.ta().getAttribute('id')) {
    bad('panel', 'two editors on one page give their sketch boxes the same id, so ' +
      'aria-describedby points at whichever the document holds first');
  } else held++;
  a.handle.dispose(); b.handle.dispose();

  if (held >= 10) ok('panel', held + ' accessibility contracts hold on the sketch panel: labelled, ' +
    'described, marked valid or not, diagnosed after a pause rather than per keystroke, ' +
    'a console that takes focus and has a name and does not announce itself, and ids ' +
    'that are unique across editors');
}

/* ================================================================ 8. nothing is lost */
async function keeps() {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const TYPED = 'void setup(){ pinMode(13, OUTPUT); }\nvoid loop(){ digitalWrite(13, HIGH); }';
  const isTyped = (m) => !!m && /pinMode\(13, OUTPUT\)/.test(m.parts[0].code || '');
  let kept = 0;

  /* The exit that lost it: typed, never blurred, and the page moved on. dispose()
     empties the panel, and removing a focused element fires no pending change. */
  const bye = mountMcu(LIVE);
  bye.ta().value = TYPED;
  bye.ta().dispatchEvent({ type: 'input', target: bye.ta() });
  bye.handle.dispose();
  drives++;
  if (!isTyped(bye.last())) {
    bad('keeps', 'a sketch typed and then left by the footer, the rail or the back button ' +
      'never reached progress — what was saved was ' +
      JSON.stringify(String((bye.last() && bye.last().parts[0].code) || '').slice(0, 30)));
  } else kept++;

  /* Alt-tab, which dispose never sees. */
  const away = mountMcu(LIVE);
  away.ta().value = TYPED;
  away.ta().dispatchEvent({ type: 'input', target: away.ta() });
  /* windowShim only forwards addEventListener to WIN, so WIN is where the handlers
     actually live and WIN is what has to be fired. */
  WIN.dispatchEvent({ type: 'blur' });
  drives++;
  if (!isTyped(away.last())) bad('keeps', 'a sketch typed and then alt-tabbed away from was not banked');
  else kept++;
  away.handle.dispose();

  /* The ordinary blur, which always worked, and must go on working. */
  const blur = mountMcu(LIVE);
  blur.ta().value = TYPED;
  blur.ta().dispatchEvent({ type: 'input', target: blur.ta() });
  blur.ta().dispatchEvent({ type: 'change', target: blur.ta() });
  drives++;
  if (!isTyped(blur.last())) bad('keeps', 'a sketch committed on blur did not reach progress');
  else kept++;
  blur.handle.dispose();

  /* And the debounce on its own, with nobody leaving at all. */
  const idle = mountMcu(LIVE);
  idle.ta().value = TYPED;
  idle.ta().dispatchEvent({ type: 'input', target: idle.ta() });
  const during = idle.saves();
  await wait(900);
  drives++;
  if (!isTyped(idle.last())) bad('keeps', 'a sketch typed and left alone never reached progress');
  else kept++;
  if (idle.saves() - during > 1) {
    bad('keeps', 'one burst of typing produced ' + (idle.saves() - during) +
      ' saves — the debounce is meant to keep it to one');
  } else kept++;
  idle.handle.dispose();

  /* A disposed editor must still never write. Cycle 6's rule, re-checked because this
     cycle added a new call into changed() and it runs from dispose(). */
  const gone = mountMcu(LIVE);
  const orphan = gone.ta();          /* held BEFORE dispose — the panel is emptied by it */
  orphan.value = TYPED;
  orphan.dispatchEvent({ type: 'input', target: orphan });
  gone.handle.dispose();
  const after = gone.saves();
  orphan.value = TYPED + '\n// and more';
  orphan.dispatchEvent({ type: 'input', target: orphan });
  orphan.dispatchEvent({ type: 'change', target: orphan });
  gone.handle.dispose();
  await wait(900);
  drives++;
  if (gone.saves() !== after) {
    bad('keeps', 'a disposed editor wrote ' + (gone.saves() - after) + ' more time(s) into saved progress');
  } else kept++;

  if (kept >= 6) ok('keeps', kept + ' commit paths hold: a sketch survives the footer, an alt-tab, ' +
    'a blur and being left alone, one burst of typing is one save, and a disposed ' +
    'editor still writes nothing');
}

/* ================================================================ 9. the mutation run */
/* Cycles 19 and 24 both found that a fresh gate scores some of its own checks on the
   wrong thing, and both found it this way: break the source on purpose, one edit at a
   time, and require the gate to notice. A check that passes against a broken file
   enforces nothing however well it reads. */
async function mutations() {
  const mcu = readFileSync(join(ROOT, 'src', 'mcu.js'), 'utf8');
  const ckt = readFileSync(join(ROOT, 'src', 'circuit.js'), 'utf8');
  const MUT = [
    ['the scope chain is a plain object again', () =>
      [mcu.replace('function scope(parent) { return { vars: bare(null), up: parent }; }',
        'function scope(parent) { return { vars: {}, up: parent }; }'), ckt]],
    ['BUILTIN is a plain object again', () =>
      [mcu.replace('const BUILTIN = bare({', 'const BUILTIN = ({'), ckt]],
    ['fns is a plain object again', () => [mcu.replace('const fns = bare(null);', 'const fns = {};'), ckt]],
    ['the builtins stop asking for numbers', () =>
      [mcu.replace('if (!TAKES_TEXT[node.name]) {', 'if (false) {'), ckt]],
    ['infinity is allowed through again', () =>
      [mcu.replace('if (typeof v === \'number\' && v - v === 0) return v;', 'return v;'), ckt]],
    ['the console character cap is removed', () =>
      [mcu.replace('if (M.chars >= CONSOLE_MAX_CHARS) { M.cut += text.length; return; }', ''), ckt]],
    ['the unknown-escape refusal is removed', () =>
      [mcu.replace('if (esc && ch === undefined) {', 'if (false) {'), ckt]],
    ['dispose stops flushing the panel', () =>
      [mcu, ckt.replace('      flushEdit();\n      disposed = true;', '      disposed = true;')]],
    ['the debounce never fires', () => [mcu, ckt.replace('editTimer = setTimeout(flushEdit, 600);', '')]],
    ['window blur stops flushing', () =>
      [mcu, ckt.replace('function onWinBlur() { releaseSpace(); flushEdit(); }',
        'function onWinBlur() { releaseSpace(); }')]],
    ['the sketch box loses its label', () =>
      [mcu, ckt.replace("'<label class=\"ckt-f\" for=\"' + uid + '\" style=\"grid-template-columns:1fr;align-items:stretch\">'",
        "'<div class=\"ckt-f\" style=\"grid-template-columns:1fr;align-items:stretch\">'")]],
    ['the error box stops being a live region', () =>
      [mcu, ckt.replace('role="status" aria-live="polite">', '>')]],
    ['the console stops taking focus', () => [mcu, ckt.replace("'<pre tabindex=\"0\" role=\"group\"", "'<pre role=\"group\"")]],
  ];
  let caught = 0, missed = [], unloadable = [];
  for (const [what, mk] of MUT) {
    const [m, c] = mk();
    /* A replace() that matched nothing hands back the file unchanged, and an unchanged
       file passing is not a mutation surviving — it is a mutation that never happened.
       Distinguished, because the first is a finding and the second is a typo in this
       list, and counting them together is how a mutation run flatters itself. */
    if (m === mcu && c === ckt) { missed.push(what + ' — the mutation never applied'); continue; }
    let ex;
    try { ex = load(m, c); }
    catch (e) { unloadable.push(what); continue; }
    if (await scoreAgainst(ex)) caught++; else missed.push(what);
  }
  for (const m of missed) bad('mutants', 'a broken build passed every check: ' + m);
  /* Equally a finding. A build that will not parse is caught by the LOADER, and a
     loader is not a check — it would report an untested contract as held. */
  for (const m of unloadable) bad('mutants', 'the mutated build did not load, so nothing ' +
    'in this file was actually scored against it: ' + m);
  if (!missed.length && !unloadable.length) {
    ok('mutants', caught + ' deliberate breakages, ' + caught + ' caught by a check rather ' +
      'than by the loader — every contract in this file fails when the thing it claims to hold is removed');
  }
}

/* The gate's own checks, re-run against an arbitrary build and answering yes/no rather
   than printing. Kept deliberately narrow: one representative assertion per fix, so a
   mutation is scored by the check that is supposed to hold it and not by a side effect. */
async function scoreAgainst(ex) {
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  try {
    for (const src of ['void loop(){ toString(); }', 'void loop(){ println(constructor); }',
                       'void loop(){ valueOf(); }']) {
      const r = run(ex.MCU, src, 4, 400);
      if (r.fault && ENGINE.test(String(r.fault.message))) return true;
    }
    if (!run(ex.MCU, 'void loop(){ println(sqrt("x")); }', 4, 400).fault) return true;
    if (!run(ex.MCU, 'void loop(){ int y = pow(10,400); println(y); }', 4, 400).fault) return true;
    if (run(ex.MCU, 'void loop(){ print("x"); }', 80, 4000).console.join('').length > 20000) return true;
    if (!run(ex.MCU, "void loop(){ println('\\q'); }", 3, 300).fault) return true;
    const fnDup = run(ex.MCU, 'int toString(){ return 4; } void loop(){ println(toString()); }', 4, 400);
    if (fnDup.console[0] !== '4') return true;

    const h = mountMcu(ex);
    const ta = h.ta();
    if (!ta) return true;
    if (!ta.closest('label')) { h.handle.dispose(); return true; }
    const box = h.root.querySelector('[data-built]');
    if (!box || box.getAttribute('aria-live') !== 'polite') { h.handle.dispose(); return true; }
    ta.value = 'void setup(){ println("hi"); } void loop(){ }';
    ta.dispatchEvent({ type: 'change', target: ta });
    h.handle.solve();
    const pre = h.root.querySelectorAll('pre')[0];
    if (!pre || pre.getAttribute('tabindex') !== '0') { h.handle.dispose(); return true; }
    h.handle.dispose();

    /* the two commit paths, each on its own */
    const bye = mountMcu(ex);
    bye.ta().value = 'void setup(){ pinMode(13, OUTPUT); }';
    bye.ta().dispatchEvent({ type: 'input', target: bye.ta() });
    bye.handle.dispose();
    if (!/pinMode\(13, OUTPUT\)/.test((bye.last() && bye.last().parts[0].code) || '')) return true;

    const idle = mountMcu(ex);
    idle.ta().value = 'void setup(){ pinMode(13, OUTPUT); }';
    idle.ta().dispatchEvent({ type: 'input', target: idle.ta() });
    await wait(900);
    const kept = /pinMode\(13, OUTPUT\)/.test((idle.last() && idle.last().parts[0].code) || '');
    idle.handle.dispose();
    if (!kept) return true;

    /* the alt-tab path, which dispose never sees and the debounce may not reach */
    const away = mountMcu(ex);
    away.ta().value = 'void setup(){ pinMode(13, OUTPUT); }';
    away.ta().dispatchEvent({ type: 'input', target: away.ta() });
    WIN.dispatchEvent({ type: 'blur' });
    const banked = /pinMode\(13, OUTPUT\)/.test((away.last() && away.last().parts[0].code) || '');
    away.handle.dispose();
    if (!banked) return true;
  } catch (e) {
    /* A mutated build that throws mid-drive HAS been caught by a check — the check
       drove it and it fell over. That is different from one that never loaded, which
       is handled by the caller. */
    return true;
  }
  return false;
}

/* ---------------------------------------------------------------- run */
await panelAsync();
await keeps();
await mutations();

console.log('');
if (fails) {
  console.log(fails + ' failure(s) — the sketch subsystem is not clean.');
  process.exit(1);
}
console.log('All good: the interpreter answers ' + drives + ' driven sketches and gestures without ' +
  'once talking like an engine, keeps a learner\'s program out of the page it runs in, ' +
  'bounds its own console, holds 13 accessibility contracts on the panel, and loses no ' +
  'sketch on any of the four ways out of a lesson.');
