/**
 * verify_desk.mjs — the resilience and persistence gate for the desk.
 *
 * src/desk.js is a notepad and a calculator in a modal, and it is named in Track 6's
 * row of the curriculum beside app.js and circuit.js. Those two have gates. This had
 * none, and it is the one file in the codebase that carries its own CSS — which is how
 * it stayed outside tools/verify_theme.mjs as well, for as long as both have existed.
 *
 *   * AN ENGINE ERROR PRESENTED AS ARITHMETIC. The parser is recursive descent with
 *     about eight frames per bracket and had no depth limit, and evaluate() repeated
 *     whatever it caught. So a deep enough expression put "Maximum call stack size
 *     exceeded" in the history as the account of the learner's own sum, and announced
 *     it to a screen reader. This gate drives an extremes grid — zero, negative,
 *     enormous, identical, deep, long, malformed — and rejects any message that is the
 *     engine talking rather than a sentence written for a learner.
 *
 *   * A STORE THAT REFUSED IN SILENCE. writeJSON returns false when localStorage
 *     refuses. flushSave has always checked it; saveState never did — and saveState is
 *     the one that carries the history, the variables, `ans`, the angle mode and the
 *     geometry. Every calculation of the session, dropped on reload, with nothing said.
 *     This gate mounts the real desk against a localStorage that refuses and requires
 *     the learner to be told; and against one that works, and requires silence.
 *
 *   * A STYLESHEET NO GATE COULD SEE. Desk.css() is what lets verify_theme.mjs measure
 *     this file. Checked here so the wiring cannot be quietly removed.
 *
 *     node tools/verify_desk.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { El } from './dom_stub.mjs';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')), '..');
const SRC = process.argv[2] ? path.resolve(process.argv[2]) : path.join(ROOT, 'src', 'desk.js');
const source = fs.readFileSync(SRC, 'utf8');

let fails = 0;
const sectionFails = {};
const ok = (tag, msg) => console.log('[ok  ] ' + tag.padEnd(9) + ' ' + msg);
const bad = (tag, msg) => { fails++; sectionFails[tag] = (sectionFails[tag] || 0) + 1; console.log('[FAIL] ' + tag.padEnd(9) + ' ' + msg); };
const clean = (tag) => !sectionFails[tag];
/* A section that dies is not a section that reports — the same lesson verify_circuit_ui
   learned when one throw took a whole run's findings with it. */
async function section(tag, fn) {
  try { await fn(); } catch (e) { bad(tag, 'the section itself fell over: ' + (e && e.stack || e)); }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/* ---------------------------------------------------------------- loading it */
/* desk.js touches document, window, localStorage and navigator by bare name, so they
   go in as parameters: one call site, and a store that refuses is a store this gate
   built rather than one it hopes the platform provides. */
function load(store) {
  const body = new El('body'), head = new El('head');
  const docListeners = [];
  const document = {
    body, head,
    activeElement: null,
    visibilityState: 'visible',
    createElement: (t) => new El(t),
    querySelector: (s) => body.querySelector(s),
    getElementById: () => null,       /* the toolbar trigger lives in the shell */
    addEventListener: (t, f) => docListeners.push([t, f]),
    removeEventListener: (t, f) => {
      const i = docListeners.findIndex((x) => x[0] === t && x[1] === f);
      if (i >= 0) docListeners.splice(i, 1);
    },
  };
  const winListeners = [];
  const window = {
    innerWidth: 1200, innerHeight: 900,
    confirm: () => true,
    addEventListener: (t, f) => winListeners.push([t, f]),
    removeEventListener: (t, f) => {
      const i = winListeners.findIndex((x) => x[0] === t && x[1] === f);
      if (i >= 0) winListeners.splice(i, 1);
    },
  };
  const navigator = { clipboard: { writeText: () => Promise.resolve() } };
  const mod = { exports: {} };
  new Function('module', 'document', 'window', 'localStorage', 'navigator',
    source + '\nmodule.exports = { Desk };')(mod, document, window, store, navigator);
  return { Desk: mod.exports.Desk, document, window, body, docListeners, winListeners };
}

/* a localStorage that works, and one that refuses the way a full quota does */
function goodStore() {
  const m = new Map();
  return {
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => { m.set(k, String(v)); },
    removeItem: (k) => { m.delete(k); },
    _map: m,
  };
}
function fullStore() {
  return {
    getItem: () => null,
    setItem: () => { const e = new Error('QuotaExceededError'); e.name = 'QuotaExceededError'; throw e; },
    removeItem: () => {},
  };
}

/* ================================================================== 1. the language */
/* Anything a learner could type, and a few things only a paste could produce. Nothing
   here may throw out of evaluate(), and no message may be the engine talking. */
const ENGINE = /call stack|\bNaN\b|\bundefined\b|\bInfinity\b|\[object|RangeError|TypeError|is not a function|cannot read/i;
/* "undefined" is a word mathematics owns too — "log of zero is undefined" is the right
   sentence. Allowed only in that shape, where it is the predicate of a claim about the
   value and not the name of a JavaScript one. */
const MATHS_UNDEFINED = /\bis undefined\b/g;

const GRID = [
  /* zero */
  '1/0', '0/0', '5%0', '0||0', '100||0', 'log(0)', 'ln(0)', 'sqrt(0)', '0^0', '0^-1',
  /* negative */
  'sqrt(-4)', 'ln(-1)', '(-8)^(1/3)', '-2^2', 'asin(2)', '100||-100', 'min(-1,-2)',
  /* enormous */
  '1e308*10', '9^9^9', '2^1024', 'exp(1000)', '1e400', '1e308+1e308', '1e-320/1e10',
  /* identical */
  '5||5', '0-0', '1/1', 'x=x', 'max(3,3)',
  /* malformed */
  '', '   ', '((', '))', 'foo(', '1 2 3', '=', 'ans', 'pi()', '1,,2', '@#$', ',', '()',
  'sin', 'sin()', 'par()', 'atan2(1)', '1..2', 'e=1', 'pi=1', 'sqrt=1',
  /* the shapes that used to reach the engine */
  '('.repeat(80) + '1' + ')'.repeat(80),
  'sqrt('.repeat(80) + '1' + ')'.repeat(80),
  '('.repeat(4000) + '1' + ')'.repeat(4000),
  '1' + '+1'.repeat(20000),
  '-'.repeat(5000) + '1',
];

await section('language', async () => {
  const { Desk } = load(goodStore());
  let threw = 0, engine = 0;
  for (const src of GRID) {
    let r;
    try { r = Desk.evaluate(src); } catch (e) { threw++; bad('language', JSON.stringify(src.slice(0, 30)) + ' threw ' + e.constructor.name + ': ' + e.message); continue; }
    if (!r || typeof r !== 'object') { bad('language', JSON.stringify(src.slice(0, 30)) + ' returned no verdict'); continue; }
    const said = r.ok ? String(r.display) + ' ' + String(r.raw) : String(r.error);
    /* "log of zero is undefined" is mathematics, not JavaScript. Struck out first, then
       whatever is left is tested — the first version of this condition tried to do both
       at once and let four mutations through, which is why the mutation run exists. */
    const stripped = said.replace(MATHS_UNDEFINED, ' ');
    if (ENGINE.test(stripped)) {
      engine++;
      bad('language', JSON.stringify(src.slice(0, 30)) + ' -> ' + said);
    }
  }
  if (!threw && !engine) ok('language', GRID.length + ' expressions at the extremes — zero, negative, enormous, identical, deep, malformed — every one answered with a sentence, none with an engine error');
});

/* ================================================================== 2. the stack */
/* The length cap and the depth cap only matter if together they make the engine's own
   limit unreachable. The worst shapes the grammar allows, at exactly the longest input
   the box accepts. */
await section('stack', async () => {
  const { Desk } = load(goodStore());
  const LIMIT = 1000;
  const worst = [
    ['nested brackets', '('.repeat(LIMIT / 2) + '1' + ')'.repeat(LIMIT / 2)],
    ['nested calls', 'sqrt('.repeat(Math.floor(LIMIT / 6)) + '1' + ')'.repeat(Math.floor(LIMIT / 6))],
    ['a long sum', '1' + '+1'.repeat(Math.floor((LIMIT - 1) / 2))],
    ['unary depth', '-'.repeat(LIMIT - 1) + '1'],
    ['a long product', '1' + '*1'.repeat(Math.floor((LIMIT - 1) / 2))],
    ['argument list', 'max(' + '1,'.repeat(Math.floor(LIMIT / 2) - 2) + '1)'],
  ];
  let n = 0;
  for (const [name, src] of worst) {
    const at = src.length <= LIMIT ? src : src.slice(0, LIMIT);
    let r;
    try { r = Desk.evaluate(at); } catch (e) { bad('stack', name + ' at ' + at.length + ' chars threw ' + e.constructor.name); continue; }
    const said = r.ok ? '' : String(r.error);
    if (/call stack/i.test(said)) { bad('stack', name + ' at ' + at.length + ' chars still reaches the engine stack'); continue; }
    n++;
  }
  /* The catch in evaluate() turns anything non-calc into "that was too much to work out
     in one go", so no engine text reaches a learner even with both caps gone — which
     means the caps are not load-bearing to the section above, and a mutation removing
     them passed. They earn their place by saying something the learner can act on, so
     that is what is checked: the refusal has to name the limit it hit. */
  const named = [
    ['too long', '1' + '+1'.repeat(20000), /\b1000\b/, 'the character limit'],
    ['too deep', '('.repeat(300) + '1' + ')'.repeat(300), /\bnested\b/i, 'the nesting limit'],
  ];
  for (const [what, src, re, why] of named) {
    const r = Desk.evaluate(src);
    if (r.ok) { bad('stack', what + ': accepted an expression it should refuse'); continue; }
    if (!re.test(String(r.error))) {
      bad('stack', what + ': refused without naming ' + why + ' — "' + r.error + '"');
    }
  }
  if (clean('stack')) ok('stack', n + ' worst-case shapes at the ' + LIMIT + '-character limit, none reaching the engine stack, and both limits refuse by name rather than by giving up');
});

/* ================================================================== 3. what it shows */
/* The history keeps the double and prints two readings of it. A learner who carries a
   value forward with `ans` and one who clicks the number must get the same answer. */
await section('shown', async () => {
  const { Desk } = load(goodStore());
  const vals = ['4k7', '4k7||10k', '1/(2*pi*sqrt(47m*220n))', '1p', '10M', '-3.3', '0',
    '1/3', '2^40', '1e-11'];
  let n = 0;
  for (const src of vals) {
    const r = Desk.evaluate(src);
    if (!r.ok) { bad('shown', src + ' would not work out: ' + r.error); continue; }
    if (!isFinite(r.value)) { bad('shown', src + ' returned a non-finite value'); continue; }
    if (ENGINE.test(String(r.display)) || ENGINE.test(String(r.raw))) { bad('shown', src + ' prints ' + r.display + ' / ' + r.raw); continue; }
    /* the raw reading has to be the same number, not a different one */
    const back = Number(r.raw);
    if (!isFinite(back) || (r.value !== 0 && Math.abs(back - r.value) / Math.abs(r.value) > 1e-9)) {
      bad('shown', src + ': the unrounded reading ' + r.raw + ' is not the value ' + r.value);
      continue;
    }
    n++;
  }
  if (clean('shown')) ok('shown', n + ' results whose unrounded reading is the value the history actually holds');
});

/* ================================================================== 4. persistence */
/* The defect this gate was written for. A store that refuses must be reported; a store
   that works must not be. Driven against the real modal, not read as source. */
await section('storage', async () => {
  /* --- a store that refuses --- */
  const refused = load(fullStore());
  refused.Desk.open('calc');
  if (!refused.Desk.isOpen()) { bad('storage', 'the desk would not open'); return; }
  const panel = refused.body.querySelector('.dsk');
  if (!panel) { bad('storage', 'the desk did not build its panel'); return; }
  const input = panel.querySelector('[data-input]');
  const say = panel.querySelector('[data-say]');
  const saved = panel.querySelector('[data-saved]');
  const prev = panel.querySelector('[data-prev]');
  if (!input || !say || !saved || !prev) { bad('storage', 'the desk is missing its input, live region or status'); return; }

  input.value = '2+2';
  input.dispatchEvent({ type: 'keydown', key: 'Enter', preventDefault() {}, stopPropagation() {} });
  await sleep(120);

  /* The two channels are asked separately and on purpose. Checking "either one carried
     it" let a mutation that silenced the live region and kept the visible line pass —
     and the learner that mutation strands is the one reading with a screen reader. */
  const heard = String(say.textContent || '');
  const shown = String(saved.textContent || '') + ' ' + String(prev.textContent || '');
  const REFUSED = /could not save|will not remember|storage is full/i;
  if (!REFUSED.test(heard)) {
    bad('storage', 'a store that refuses every write was never announced: live region said "' + heard + '"');
  }
  if (!REFUSED.test(shown)) {
    bad('storage', 'a store that refuses every write showed nothing: panel said "' + shown.trim() + '"');
  }
  if (!saved.classList.contains('warn')) {
    bad('storage', 'the saved-state line is not marked as a warning when the store refuses');
  }

  /* --- a store that works --- */
  const fine = load(goodStore());
  fine.Desk.open('calc');
  const p2 = fine.body.querySelector('.dsk');
  const in2 = p2.querySelector('[data-input]');
  const say2 = p2.querySelector('[data-say]');
  const saved2 = p2.querySelector('[data-saved]');
  in2.value = '2+2';
  in2.dispatchEvent({ type: 'keydown', key: 'Enter', preventDefault() {}, stopPropagation() {} });
  await sleep(120);
  const heard2 = String(say2.textContent || '') + ' ' + String(saved2.textContent || '');
  if (/could not save|storage is full/i.test(heard2)) {
    bad('storage', 'a store that works was reported as full: "' + heard2.trim() + '"');
  }
  if (!/4/.test(String(say2.textContent || ''))) {
    bad('storage', 'the result was not announced: "' + String(say2.textContent) + '"');
  }
  if (clean('storage')) {
    ok('storage', 'a refusing store is reported in the live region and on the panel, a working one is not, and the result is announced either way');
  }
});

/* ================================================================== 5. the stylesheet */
await section('style', async () => {
  const { Desk } = load(goodStore());
  if (typeof Desk.css !== 'function') {
    bad('style', 'Desk.css() is gone — tools/verify_theme.mjs cannot measure this file without it');
    return;
  }
  const css = String(Desk.css());
  const need = ['.dsk-val', '.dsk-title', '.dsk-ta', '.dsk-in input', '--dsk-veil'];
  const missing = need.filter((s) => css.indexOf(s) < 0);
  if (missing.length) { bad('style', 'the stylesheet no longer declares: ' + missing.join(', ')); return; }
  if (css.indexOf('[data-theme=light]') < 0) { bad('style', 'the stylesheet declares no light theme at all'); return; }
  /* the accent as ink is the trap five cycles have now hit; the tokens exist for it */
  ok('style', 'Desk.css() hands the theme gate ' + css.split('\n').length + ' lines, light theme included');
});

/* ================================================================== */
console.log('');
if (fails) {
  console.log('FAILED: ' + fails + ' problem(s).');
  process.exit(1);
}
console.log('All good: the desk answers ' + (GRID.length + 6) + ' expressions at the extremes without an engine error, ' +
  'keeps its two limits between a paste and the stack, reports a store that refuses, and hands its own stylesheet to the theme gate.');
