/**
 * verify_progress.mjs — the resilience and accessibility gate for the progress store.
 *
 * Track 6's row of the curriculum names three files. src/circuit.js got a gate in cycle
 * 6 and src/desk.js in cycle 12, which recorded what it was leaving behind: *"src/app.js's
 * own persistence layer was not audited — P, saveSoon, resetProgress, the progress export
 * and import, warnNoStorage. It is where a storage defect costs a learner their whole
 * record rather than their calculator history, and it is a cycle of its own."* This is
 * that cycle, and this is the gate it was missing. What it holds:
 *
 *   * THE LAST 900 ms OF EVERY SESSION. saveSoon is debounced, and nothing flushed it.
 *     Finish a unit and close the tab inside the window and the completion, its XP and
 *     the day's activity were simply never written — and on a phone the tab is
 *     backgrounded and killed with no close event at all. desk.js has flushed the
 *     calculator on pagehide since cycle 12; the file carrying every completed unit did
 *     not. This gate hands the app a localStorage that remembers, owes it a save, fires
 *     pagehide, and reads the store back.
 *
 *   * A RESET THAT DID NOT HAPPEN. Every rule in server/merge.mjs moves progress forward
 *     and never back, which is right for two devices doing work and wrong for the one
 *     action whose purpose is removal. "Reset progress" cleared the local copy, pushed
 *     it, and the union handed all of it back about two seconds later — with the toast
 *     still on screen saying it had been cleared. This gate drives the real mergeProgress
 *     with the document resetProgress actually produces.
 *
 *   * A DOCUMENT FROM OUTSIDE, BELIEVED. The import path assigned the file straight into
 *     P: `"xp": "9999"` reached the topbar as a level-67 badge, `{"a":1}` reached it as
 *     "[object Object]", and `__proto__` reached Object.assign's [[Set]]. All three were
 *     then saved and pushed, and the server settles xp with `Math.max(Number(x) || 0)`,
 *     so a malformed file zeroed the XP the account already held.
 *
 *   * A SAVE INDICATOR NOTHING COULD HEAR, AND A CONFIRMATION NOTHING COULD HEAR. The
 *     one strip in the app that says whether progress is being kept was a bare span with
 *     no role and no live region, and `display:none` below 640px took it out of the
 *     accessibility tree on every phone. The reset confirmation was a hidden span whose
 *     text was already inside it, and the button's name did not change — so a screen
 *     reader user pressed, heard nothing, pressed again, and erased everything.
 *
 *     node tools/verify_progress.mjs
 */
import fs from 'node:fs';
import path from 'node:path';
import { loadApp } from './app_stage.mjs';
import { WIN, DOC, windowShim } from './dom_stub.mjs';
import { mergeProgress } from '../server/merge.mjs';

/* Two ways to look at the page shell, and they are not the same object.
 *
 * app_stage memoises one element per id and hands it to every `$('#thing')` the app
 * makes, so what setSaveState WRITES TO is `shellEl('save-state-say')`. renderShell also
 * assigns a string of HTML into #app, and the nodes parsed out of that string are what
 * DECLARE the roles — a different tree entirely, because nothing in the stub re-points
 * the memo at parsed children.
 *
 * The first draft of this gate read the parsed tree and asserted on behaviour, so the
 * app wrote to one node and the gate read another: three sections reported clean code
 * broken and would have reported broken code clean. Behaviour is checked through
 * shellEl, markup through the parsed shell, and each is labelled below.
 */

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')), '..');
const KEY = 'codewright-progress-v1';

let fails = 0;
const sectionFails = {};
const ok = (tag, msg) => console.log('[ok  ] ' + tag.padEnd(9) + ' ' + msg);
const bad = (tag, msg) => { fails++; sectionFails[tag] = (sectionFails[tag] || 0) + 1; console.log('[FAIL] ' + tag.padEnd(9) + ' ' + msg); };
/* A section that dies is not a section that reports — verify_circuit_ui learned this
   when one throw took a whole run's findings with it. */
async function section(tag, fn) {
  try { await fn(); } catch (e) { bad(tag, 'the section itself fell over: ' + ((e && e.stack) || e)); }
}

/* A localStorage that actually remembers, and can be told to refuse. The stage's default
   answers null and swallows every write, which is right for a gate about something else
   and useless for this one: a store that never fails cannot show that a failure is
   reported, and a store that never remembers cannot show that a write landed. */
function memStore() {
  const m = new Map();
  const s = {
    refuse: false,
    writes: 0,
    getItem: (k) => (m.has(k) ? m.get(k) : null),
    setItem: (k, v) => {
      if (s.refuse) throw Object.assign(new Error('quota'), { name: 'QuotaExceededError' });
      s.writes++; m.set(k, v);
    },
    removeItem: (k) => m.delete(k),
    doc: () => { const raw = m.get(KEY); return raw ? JSON.parse(raw) : null; },
  };
  return s;
}

const EXPORTS = {
  saveSoon: 'saveSoon', saveNow: 'saveNow', flushSave: 'flushSave',
  setSaveState: 'setSaveState', paintSaveState: 'paintSaveState',
  sanitiseProgress: 'sanitiseProgress', resetProgress: 'resetProgress',
  importProgress: 'importProgress', recomputeXp: 'recomputeXp',
  renderShell: 'renderShell', renderProfile: 'renderProfile',
  level: 'level', updateXp: 'updateXp', Store: 'Store',
  P: '() => P', setP: '(v) => { P = v; }',
  saveDirty: '() => saveDirty',
};

function mount(store) {
  const stage = loadApp({ localStorage: store, exports: EXPORTS });
  return stage;
}

let counts = { flush: 0, hostile: 0, merges: 0, said: 0, aria: 0 };

/* ================================================================ 1. the unload flush */
await section('flush', async () => {
  const store = memStore();
  const { app, doc } = mount(store);

  app.P().completed['EE101-M1'] = true;
  app.P().xp = 40;
  app.saveSoon();
  counts.flush++;
  if (store.doc()) { bad('flush', 'saveSoon wrote immediately — the debounce is gone, which is a different defect'); return; }
  if (!app.saveDirty()) { bad('flush', 'saveSoon did not record that a write is owed, so the unload path cannot know'); return; }

  WIN.dispatchEvent({ type: 'pagehide' });
  counts.flush++;
  const landed = store.doc();
  if (!landed) { bad('flush', 'pagehide did not write — the last 900 ms of the session is still being dropped'); return; }
  if (landed.completed['EE101-M1'] !== true) { bad('flush', 'pagehide wrote a document without the completion in it'); return; }
  if (landed.xp !== 40) { bad('flush', 'pagehide wrote xp ' + landed.xp + ', not the 40 that was owed'); return; }
  ok('flush', 'a completion owed to the 900 ms debounce is on disk before pagehide returns');

  /* An unload handler that writes unconditionally would write on every tab switch, and
     the document is the whole progress record. Owing nothing must cost nothing. */
  const before = store.writes;
  WIN.dispatchEvent({ type: 'pagehide' });
  counts.flush++;
  if (store.writes !== before) { bad('flush', 'pagehide wrote again with nothing owed — every tab switch serialises the whole record'); return; }
  ok('flush', 'a pagehide with nothing owed writes nothing');

  /* A phone does not close a tab, it backgrounds it and then kills it — no unload event
     of any kind, and visibilitychange is the only warning there is. Fired separately from
     pagehide, because a fix that wires only one of them leaves the commoner case open. */
  app.P().completed['EE101-M2'] = true;
  app.saveSoon();
  doc.visibilityState = 'hidden';
  doc.emit('visibilitychange');
  counts.flush++;
  const hidden = store.doc();
  if (!hidden || hidden.completed['EE101-M2'] !== true) {
    bad('flush', 'a tab going to the background did not flush — the case a phone actually ends a session with'); return;
  }
  doc.visibilityState = 'visible';
  ok('flush', 'a tab backgrounded rather than closed flushes too');

  /* The write has to be synchronous. A promise continuation queued inside an unload
     handler is under no obligation ever to run, which is why this cannot go through
     Store.save — and Store.save only *looks* synchronous when no backend is configured:
     with window.storage present it awaits the round trip before it ever reaches
     localStorage. So the backend has to be present for this to mean anything, which is
     what the first mutation run proved by letting the async version straight through. */
  windowShim.storage = { get: async () => null, set: () => new Promise(() => {}) };
  try {
    const backed = memStore();
    const b = mount(backed);
    b.app.P().completed['EE101-M4'] = true;
    b.app.saveSoon();
    b.app.flushSave();
    counts.flush++;
    const sync = backed.doc();
    if (!sync || sync.completed['EE101-M4'] !== true) {
      bad('flush', 'with a backend configured the flush no longer lands in the same tick — it is behind an await the unload will not wait for');
      return;
    }
    ok('flush', 'the flush lands synchronously even with a storage backend in front of it');
  } finally { delete windowShim.storage; }

  /* and the boot path has to ask, or the answer arrives after the loss it was for */
  const src = fs.readFileSync(path.join(ROOT, 'src', 'app.js'), 'utf8');
  const boot = src.slice(src.indexOf('async function boot()'), src.indexOf('function bootFailed'));
  if (boot.indexOf('paintSaveState()') < 0) {
    bad('flush', 'boot() no longer asks Store.status() — the indicator is blank until the first write again'); return;
  }
  if (boot.indexOf('paintSaveState()') < boot.indexOf('renderShell()')) {
    bad('flush', 'boot() paints the save state before the shell that holds it exists'); return;
  }
  ok('flush', 'boot() asks whether the store works before the learner earns anything');

  /* and it must survive the store refusing, rather than throwing out of an unload handler */
  store.refuse = true;
  app.P().completed['EE101-M3'] = true;
  app.saveSoon();
  let threw = null;
  try { WIN.dispatchEvent({ type: 'pagehide' }); } catch (e) { threw = e; }
  counts.flush++;
  if (threw) { bad('flush', 'a refusing store threw out of the pagehide handler: ' + threw.message); return; }
  ok('flush', 'a store that refuses during unload is handled rather than thrown');
});

/* ==================================================== 2. a store that refuses, reported */
await section('storage', async () => {
  const store = memStore();
  store.refuse = true;
  const { app, shellEl } = mount(store);
  app.renderShell();
  if (!shellEl('app').querySelector('#save-state-say')) { bad('storage', 'the shell no longer builds #save-state-say'); return; }
  /* behaviour: the nodes the app's own $() resolves to */
  const box = shellEl('save-state');
  const say = shellEl('save-state-say');

  /* Store.status()'s own comment promises this happens before the first save. It never
     did: setSaveState ran only from inside saveNow, so a private window said nothing at
     all until the learner had already earned progress they were about to lose. */
  app.paintSaveState();
  if (!box.classList.contains('bad')) { bad('storage', 'a refusing store is not marked on the panel at boot — the warning still arrives after the loss'); return; }
  if (!/not being saved/i.test(say.textContent)) { bad('storage', 'a refusing store is not announced at boot'); return; }
  ok('storage', 'a store that refuses is on the panel and in the live region before the first save');

  /* Asked separately, and deliberately. Cycle 12 shipped an assertion that accepted the
     panel OR the announcement, so a mutation that silenced only the announcement passed —
     and the learner that strands is the one reading with a screen reader. */
  const store2 = memStore();
  const s2 = mount(store2);
  s2.app.renderShell();
  const box2 = s2.shellEl('save-state');
  const say2 = s2.shellEl('save-state-say');
  s2.app.paintSaveState();
  if (box2.classList.contains('bad')) { bad('storage', 'a working store is marked bad on the panel'); return; }
  if (say2.textContent) { bad('storage', 'a working store is announced — the live region speaks when there is no news'); return; }
  ok('storage', 'a working store is marked on neither channel');
});

/* ============================================ 3. the live region does not cry every save */
await section('quiet', async () => {
  const store = memStore();
  const { app, shellEl } = mount(store);
  app.renderShell();
  const say = shellEl('save-state-say');   /* behaviour, so the node the app writes to */
  const txt = shellEl('save-state-txt');
  const said = [];
  let last = '';
  const watch = () => { if (say.textContent !== last) { last = say.textContent; if (last) said.push(last); } };

  /* A session is hundreds of saves. A live region wired to the visible word would read
     "Saving, Saved, Saving, Saved" over the top of the lesson, which is how a live region
     gets switched off — and then the one announcement that mattered is gone too. */
  for (let i = 0; i < 20; i++) { app.setSaveState('Saving…'); watch(); app.setSaveState('Saved', false); watch(); }
  counts.said += 40;
  if (said.length) { bad('quiet', '20 healthy saves produced ' + said.length + ' announcement(s): ' + JSON.stringify(said[0])); return; }
  ok('quiet', '40 state writes over 20 healthy saves are announced 0 times');

  app.setSaveState('Not saved', true); watch();
  counts.said++;
  if (said.length !== 1) { bad('quiet', 'progress stopping being saved was announced ' + said.length + ' time(s), not once'); return; }
  for (let i = 0; i < 10; i++) { app.setSaveState('Saving…'); watch(); app.setSaveState('Not saved', true); watch(); }
  counts.said += 20;
  if (said.length !== 1) { bad('quiet', 'the same failure was announced ' + said.length + ' times over'); return; }
  ok('quiet', 'the break is announced once and then not repeated for 20 further writes');

  app.setSaveState('Saved', false); watch();
  counts.said++;
  if (said.length !== 2 || !/being saved again/i.test(said[1])) { bad('quiet', 'the recovery is not announced: ' + JSON.stringify(said)); return; }
  ok('quiet', 'the recovery is announced once — 2 announcements over ' + counts.said + ' state writes');

  /* and the visible word must still move, or the fix has traded one channel for another */
  if (txt.textContent !== 'Saved') { bad('quiet', 'the visible word stopped tracking the state: ' + JSON.stringify(txt.textContent)); return; }
  ok('quiet', 'the visible word still tracks every save');
});

/* ================================================ 4. a progress document taken from outside */
await section('import', async () => {
  const store = memStore();
  const { app } = mount(store);

  /* Every one of these was accepted verbatim, and none of them threw — which is what
     made them survivable long enough to be saved and pushed. */
  const HOSTILE = [
    ['xp as a string', { completed: { A: true }, xp: '9999' }],
    ['xp as an object', { completed: { A: true }, xp: { a: 1 } }],
    ['xp negative', { completed: { A: true }, xp: -500 }],
    ['xp as Infinity', { completed: { A: true }, xp: 1e999 }],
    ['activity as an array', { completed: {}, activity: [1, 2, 3] }],
    ['activity holding words', { completed: {}, activity: { '2026-01-01': 'lots' } }],
    ['completed holding objects', { completed: { A: { deep: 1 } } }],
    ['completed holding false', { completed: { A: true, B: false, C: true } }],
    ['name as an object', { completed: {}, name: { x: 1 } }],
    ['name enormous', { completed: {}, name: 'x'.repeat(5000) }],
    ['railHidden as a string', { completed: {}, railHidden: 'no' }],
    ['theme junk', { completed: {}, theme: 'neon' }],
    ['seed as a word', { completed: {}, seed: 'abc' }],
    ['last as an object', { completed: {}, last: { id: 1 } }],
    ['playground as an array', { completed: {}, playground: [1] }],
    ['a slot that is a string', { completed: {}, quiz: 'nope' }],
    ['null throughout', { completed: null, quiz: null, activity: null }],
    ['nothing at all', {}],
  ];
  /* An array is an object, and dropping Array.isArray does not put an array in the slot —
     it index-keys it, so `completed: ["A","B"]` becomes {0:true,1:true} and two units
     nobody finished are counted. The first mutation run walked straight past that,
     because every assertion below asked whether the slot was an array rather than
     whether anything had survived being one. */
  const ARRAYS = ['completed', 'quiz', 'code', 'derive', 'build', 'blanks', 'numeric', 'match', 'tune', 'activity'];
  for (const [name, doc] of HOSTILE) {
    counts.hostile++;
    let out;
    try { out = app.sanitiseProgress(doc); }
    catch (e) { bad('import', name + ': sanitiseProgress threw — ' + e.message); return; }
    app.setP(out);
    /* the two readings a learner actually sees, and the two that used to go wrong */
    let lvl, topbar;
    try { lvl = app.level(); } catch (e) { lvl = NaN; }
    try { topbar = out.xp.toLocaleString('en-GB'); } catch (e) { topbar = String(e); }
    if (!Number.isFinite(lvl)) { bad('import', name + ': level() is ' + lvl); return; }
    if (!/^[\d,]+$/.test(topbar)) { bad('import', name + ': the topbar reads ' + JSON.stringify(topbar)); return; }
    if (typeof out.xp !== 'number' || !Number.isFinite(out.xp) || out.xp < 0) { bad('import', name + ': xp is ' + JSON.stringify(out.xp)); return; }
    if (typeof out.name !== 'string') { bad('import', name + ': name is ' + typeof out.name); return; }
    if (typeof out.railHidden !== 'boolean') { bad('import', name + ': railHidden is ' + typeof out.railHidden); return; }
    for (const slot of ['completed', 'quiz', 'code', 'derive', 'build', 'blanks', 'numeric', 'match', 'tune', 'activity']) {
      const v = out[slot];
      if (!v || typeof v !== 'object' || Array.isArray(v)) { bad('import', name + ': ' + slot + ' is ' + JSON.stringify(v)); return; }
    }
    for (const k in out.completed) {
      if (out.completed[k] !== true) { bad('import', name + ': completed.' + k + ' is ' + JSON.stringify(out.completed[k])); return; }
    }
    for (const k in out.activity) {
      if (!Number.isFinite(out.activity[k])) { bad('import', name + ': activity.' + k + ' is ' + JSON.stringify(out.activity[k])); return; }
    }
    /* it has to round-trip, or the export it feeds is not a backup */
    try { JSON.parse(JSON.stringify(out)); } catch (e) { bad('import', name + ': the result will not round-trip through JSON'); return; }
  }
  ok('import', counts.hostile + ' hostile documents coerced into shape, none throwing, none reaching the topbar as NaN');

  for (const slot of ARRAYS) {
    counts.hostile++;
    const o = app.sanitiseProgress({ [slot]: ['A', 'B'] });
    if (Object.keys(o[slot]).length) {
      bad('import', slot + ' handed an array kept ' + Object.keys(o[slot]).length +
        ' index-keyed entr(y/ies) — ' + JSON.stringify(o[slot])); return;
    }
  }
  ok('import', 'each of the ' + ARRAYS.length + ' slots handed an array keeps nothing from it');

  /* Object.assign writes through [[Set]], so an own "__proto__" key runs the inherited
     setter and replaces a prototype. JSON.parse produces exactly that key.
     Checked on the SLOT, not on the document: the top-level object is rebuilt from a
     fixed key list and would be clean either way, so a check there passes whether the
     guard exists or not — which is what let the first mutation run remove it unseen.
     The slots are the objects that are actually carried through. */
  const polluted = JSON.parse('{"completed":{"__proto__":{"pwned":true},"A":true},"quiz":{"__proto__":{"pwned":true}},"xp":0}');
  const clean = app.sanitiseProgress(polluted);
  counts.hostile++;
  const protos = [clean, clean.completed, clean.quiz];
  if (protos.some((o) => Object.getPrototypeOf(o) !== Object.prototype) || ({}).pwned !== undefined) {
    bad('import', 'a "__proto__" key in the file still replaces a prototype it is carried into'); return;
  }
  if (clean.completed.A !== true) { bad('import', 'the guard threw away the real key beside __proto__'); return; }
  ok('import', 'a "__proto__" key changes no prototype, in the document or in any slot it rides in');

  /* "Restored 3 completed units" over a file holding one true, one false and one absent */
  const counted = app.sanitiseProgress({ completed: { A: true, B: false, C: true } });
  if (Object.keys(counted.completed).length !== 2) {
    bad('import', 'the restored count is ' + Object.keys(counted.completed).length + ', not the 2 units actually taken'); return;
  }
  ok('import', 'the sentence a learner is shown counts the units that were actually taken');
});

/* ========================================= 5. a reset and an import that cross the wire */
await section('merge', async () => {
  const store = memStore();
  const { app } = mount(store);

  const account = {
    completed: { 'EE101-M1': true, 'EE101-QZ': true, 'EE111-M3': true },
    quiz: { 'EE101-QZ': 100 }, activity: { '2026-08-30': 5 },
    code: { 'EE101-M2': { files: { 'a.py': 'x' }, t: 900 } },
    xp: 260, name: 'Ada', updatedAt: 1000,
  };

  /* the document resetProgress actually produces, taken from the function rather than
     written out here — a gate that hand-rolls its subject checks its own arithmetic */
  app.setP(app.sanitiseProgress(account));
  app.P().name = 'Ada';
  app.resetProgress();
  const cleared = JSON.parse(JSON.stringify(app.P()));
  counts.merges++;
  if (!cleared.clearedAt) { bad('merge', 'resetProgress does not stamp clearedAt, so the reset cannot cross the wire'); return; }
  if ((cleared.updatedAt || 0) < cleared.clearedAt) { bad('merge', 'the cleared document is older than its own clear stamp, so the server will discard it'); return; }

  const after = mergeProgress(account, cleared);
  counts.merges++;
  if (Object.keys(after.completed).length) { bad('merge', 'the server handed ' + Object.keys(after.completed).length + ' completed unit(s) back after a reset'); return; }
  if (after.xp !== 0) { bad('merge', 'the server handed ' + after.xp + ' XP back after a reset'); return; }
  if (Object.keys(after.quiz).length || Object.keys(after.activity).length || Object.keys(after.code).length) {
    bad('merge', 'quiz scores, activity or saved code survived a reset'); return;
  }
  if (after.name !== 'Ada') { bad('merge', 'the reset erased the name, which the card promises it keeps'); return; }
  ok('merge', 'a reset clears the account and keeps the name the card says it keeps');

  /* the whole merge is built on being order-independent; a tombstone must not break that */
  const ab = JSON.stringify(mergeProgress(account, cleared));
  const ba = JSON.stringify(mergeProgress(cleared, account));
  counts.merges += 2;
  if (ab !== ba) { bad('merge', 'merge(a,b) and merge(b,a) no longer agree'); return; }
  ok('merge', 'the tombstone is order-independent');

  /* the case a single replace endpoint would not have covered: a second machine that has
     been asleep since before the reset and now pushes the copy it still holds */
  const stale = { completed: { 'EE101-M1': true }, xp: 100, updatedAt: cleared.clearedAt - 500 };
  const m2 = mergeProgress(after, stale);
  counts.merges++;
  if (Object.keys(m2.completed).length) { bad('merge', 'a second device resurrected ' + Object.keys(m2.completed).length + ' unit(s) after the reset'); return; }
  ok('merge', 'a second device holding a copy older than the clear does not resurrect it');

  /* and the other direction, which is the reason this is a timestamp and not a flag:
     work genuinely done on another machine after the reset is not the reset's to delete */
  const fresh = { completed: { 'EE999-M1': true }, xp: 20, updatedAt: cleared.clearedAt + 5000 };
  const m3 = mergeProgress(after, fresh);
  counts.merges++;
  if (m3.completed['EE999-M1'] !== true) { bad('merge', 'work done after the reset was deleted by it'); return; }
  ok('merge', 'work done on another machine after the reset survives it');

  /* every account that exists today has no clearedAt at all, and must merge exactly as
     it did before this field existed */
  const a = { completed: { A: true }, quiz: { Q: 10 }, xp: 10, name: 'One', updatedAt: 1000 };
  const b = { completed: { B: true }, quiz: { Q: 40 }, xp: 20, name: 'Two', updatedAt: 2000 };
  const legacy = mergeProgress(a, b);
  counts.merges++;
  if (!legacy.completed.A || !legacy.completed.B || legacy.xp !== 20 || legacy.quiz.Q !== 40 || legacy.name !== 'Two') {
    bad('merge', 'a pair of documents with no clearedAt no longer merges the way it did'); return;
  }
  ok('merge', 'documents predating the tombstone union exactly as before');
});

/* ================================================= 6. the confirmation can be heard */
await section('confirm', async () => {
  const store = memStore();
  const { app, shellEl } = mount(store);
  app.renderShell();
  const main = shellEl('main');
  app.renderProfile(main);

  const note = main.querySelector('#prof-reset-note');
  const btn = main.querySelector('#prof-reset');
  if (!note || !btn) { bad('confirm', 'the profile no longer builds the reset control and its note'); return; }
  counts.aria++;

  /* A live region has to be present and empty for text arriving in it to be announced.
     The note used to ship with its sentence already inside it and merely `hidden`, so
     un-hiding announced nothing at all in most screen readers. */
  if (note.getAttribute('role') !== 'status' && !note.getAttribute('aria-live')) {
    bad('confirm', 'the confirmation note is not a live region'); return;
  }
  if (note.textContent) { bad('confirm', 'the note ships with its text already in it, so arriving text is not new'); return; }
  if (note.hasAttribute('hidden')) { bad('confirm', 'the note is hidden, so its live region is not in the tree'); return; }
  ok('confirm', 'the confirmation note is an empty live region at rest');

  const rest = btn.textContent;
  btn.dispatchEvent({ type: 'click' });
  counts.aria++;
  if (!note.textContent) { bad('confirm', 'arming the reset announces nothing — the confirmation is silent again'); return; }
  if (!/cannot be undone|erase/i.test(note.textContent)) { bad('confirm', 'the armed announcement does not say what the next press does'); return; }
  if (btn.textContent === rest) { bad('confirm', 'the button says the same thing armed and unarmed, so nothing tells you which press this is'); return; }
  /* WCAG 2.5.3: the accessible name has to contain the visible label, so the state has
     to move the visible text rather than only an aria-label beside it */
  if (btn.getAttribute('aria-label') && btn.getAttribute('aria-label').indexOf(btn.textContent) < 0) {
    bad('confirm', 'the accessible name no longer contains the visible label'); return;
  }
  ok('confirm', 'arming says what the next press does, and the button says which press this is');

  /* one press must never be enough */
  const startedWith = Object.keys(app.P().completed).length;
  app.P().completed['EE101-M1'] = true;
  const s2 = mount(memStore());
  s2.app.renderShell();
  const m2 = s2.shellEl('main');
  s2.app.renderProfile(m2);
  s2.app.P().completed['EE101-M1'] = true;
  m2.querySelector('#prof-reset').dispatchEvent({ type: 'click' });
  counts.aria++;
  if (Object.keys(s2.app.P().completed).length === 0) { bad('confirm', 'a single press erased everything'); return; }
  m2.querySelector('#prof-reset').dispatchEvent({ type: 'click' });
  counts.aria++;
  if (Object.keys(s2.app.P().completed).length !== 0) { bad('confirm', 'two presses did not erase'); return; }
  ok('confirm', 'one press arms and does not erase; two presses erase');

  /* go() replaces main.innerHTML, so the control that was pressed is destroyed and focus
     falls to <body>. A keyboard user is dropped at the top of the document, silently. */
  /* El.focus() records on dom_stub's own DOC, which is the stub for document.activeElement */
  const focused = DOC.activeElement;
  if (!focused || !focused.getAttribute || focused.getAttribute('id') !== 'prof-reset') {
    bad('confirm', 'focus was not returned to a control after the screen repainted (it is on ' +
      (focused && focused.getAttribute ? (focused.getAttribute('id') || focused.tagName) : String(focused)) + ')');
    return;
  }
  ok('confirm', 'focus is returned to the control that did the thing, not dropped to the document');
});

/* ========================================== 7. the markup and the stylesheet contract */
await section('aria', async () => {
  const store = memStore();
  const { app, shellEl } = mount(store);
  app.renderShell();
  const root = shellEl('app');

  const say = root.querySelector('#save-state-say');
  const txt = root.querySelector('#save-state-txt');
  if (!say) { bad('aria', '#save-state has no live region — it goes to "Not saved" and says nothing'); return; }
  if (say.getAttribute('role') !== 'status' && !say.getAttribute('aria-live')) { bad('aria', '#save-state-say is not a live region'); return; }
  if (!txt || txt.getAttribute('aria-hidden') !== 'true') {
    bad('aria', 'the visible word is not aria-hidden, so every save is read out as well as shown'); return;
  }
  counts.aria += 2;
  ok('aria', 'the save indicator announces through a live region and reads its word to nobody');

  const main = shellEl('main');
  app.renderProfile(main);
  const accCard = main.innerHTML;
  /* the sign-in card only builds #acc-msg when it is showing the form */
  if (accCard.indexOf('id="acc-msg"') >= 0) {
    const msg = main.querySelector('#acc-msg');
    if (msg.getAttribute('role') !== 'status' && !msg.getAttribute('aria-live')) {
      bad('aria', '#acc-msg is not a live region — "wrong email or password" is shown to nobody'); return;
    }
    counts.aria++;
    ok('aria', 'the sign-in failure message is a live region');
  }

  /* The 640px rule used display:none, which takes the node out of the accessibility tree
     along with the layout — so on every phone the one channel that says progress is not
     being stored was gone. The word may stand down; the element may not. */
  const css = fs.readFileSync(path.join(ROOT, 'src', 'index.head.html'), 'utf8');
  /* The phone block, taken by matching ITS OWN braces rather than by cutting at the
     next at-rule that happened to follow it. The cut version read as far as the first
     @media (prefers-reduced-motion) after the first 640px block, so adding one
     anywhere between the two moved the window off the rule this is about and reported
     a missing rule that was still there. Two rounds of the stylesheet growing is
     enough to say the window has to come from the source, not from a landmark. */
  const block = (() => {
    let out = '';
    for (let i = css.indexOf('@media (max-width:640px)'); i >= 0;
         i = css.indexOf('@media (max-width:640px)', i + 1)) {
      let depth = 0, j = css.indexOf('{', i);
      if (j < 0) continue;
      let k = j;
      for (; k < css.length; k++) {
        if (css[k] === '{') depth++;
        else if (css[k] === '}' && --depth === 0) break;
      }
      out += css.slice(i, k + 1) + '\n';
    }
    return out;
  })();
  if (/(^|[},;\s])\.save-state\s*\{[^}]*display\s*:\s*none/.test(block)) {
    bad('aria', 'the 640px rule still takes the whole save indicator out of the accessibility tree'); return;
  }
  if (!/\.save-state\s+\.ss-txt\s*\{[^}]*display\s*:\s*none/.test(block)) {
    bad('aria', 'the 640px rule no longer stands the save word down, so the topbar arithmetic has a column it does not count'); return;
  }
  if (!/\.vh\s*\{[^}]*clip-path/.test(css)) { bad('aria', '.vh is not clipped out of the layout, so the live region takes space'); return; }
  if (/\.vh\s*\{[^}]*display\s*:\s*none/.test(css)) { bad('aria', '.vh uses display:none, which takes it out of the accessibility tree too'); return; }
  counts.aria += 3;
  ok('aria', 'the save indicator survives 640px in the accessibility tree with only its word stood down');

  /* A button that disables itself takes focus with it. */
  const src = fs.readFileSync(path.join(ROOT, 'src', 'app.js'), 'utf8');
  const wire = src.slice(src.indexOf('function wireAccountCard'), src.indexOf('function renderProfile'));
  if (/\bb\.disabled\s*=/.test(wire)) {
    bad('aria', 'the sign-in buttons disable themselves, which blurs the one that was just pressed'); return;
  }
  if (wire.indexOf('aria-disabled') < 0) { bad('aria', 'the sign-in buttons say nothing about being busy'); return; }
  counts.aria++;
  ok('aria', 'the sign-in buttons report busy without taking focus with them');

  /* The call sites, read as source: every door into P goes through the one rule. */
  const doors = src.match(/P = (?:Object\.assign|sanitiseProgress|\{)/g) || [];
  const assigns = (src.match(/P = Object\.assign\(\{ completed:/g) || []).length;
  if (assigns) { bad('aria', assigns + ' door(s) into P still Object.assign a document straight in'); return; }
  counts.aria++;
  ok('aria', 'all ' + doors.length + ' assignments to P go through sanitiseProgress or the literal reset');
});

/* ================================================================== */
console.log('');
if (fails) {
  console.log('FAILED: ' + fails + ' problem(s).');
  process.exit(1);
}
console.log('All good: the progress store lands ' + counts.flush + ' unload writes without outrunning the document, ' +
  'coerces ' + counts.hostile + ' hostile documents into shape, keeps a reset cleared across ' + counts.merges + ' merges, ' +
  'announces 2 things in ' + counts.said + ' state writes, and holds ' + counts.aria + ' accessibility contracts.');
