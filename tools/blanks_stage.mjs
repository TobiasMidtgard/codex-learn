/**
 * blanks_stage.mjs — the shipped fill-in-the-blank view, mounted in Node.
 *
 * verify_quiz.mjs reads the artifact. This is how it reads the SCREEN. Both defects
 * that mattered most in the blanks bank were invisible in the JSON and invisible to
 * any rule written about the source: the options were drawn in the order they were
 * authored and never shuffled, so pressing the top button scored 735 of 1103; and the
 * prompt went through esc() rather than the markdown renderer, so 165 prompts carrying
 * mathematics and 80 carrying a code span arrived on the page as their own source.
 *
 * A source-shape check would have been a gate enforcing a comment. So this loads
 * lang.js, tracks.js, studio.js, engine.js and app.js exactly as build.mjs orders them,
 * hands them the tiny DOM the two circuit gates already share, and calls the real
 * renderBlanks — then clicks its buttons and reads what came back.
 *
 * It is a separate file from the gate because loading 360 KB of application source is
 * not what the rest of that gate is doing, and because a second gate wanting the same
 * view should get this one rather than write another.
 */

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { El, windowShim } from './dom_stub.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = (f) => readFileSync(join(ROOT, 'src', f), 'utf8');

/* One seed for the whole run, so the gate is deterministic. The shuffle is keyed on
   (seed, lesson id, hole number), so this is one arbitrary learner — and the aggregate
   over 1103 holes is what the caller checks, not any single unit's order. */
const SEED = 0x5EED10;

export function stage() {
  /* the load order build.mjs uses; app.js reads TRACKS at the top and MathML from
     studio.js the moment any prose is rendered */
  globalThis.__CW_NO_BOOT = 1;
  const src = ['lang.js', 'tracks.js', 'studio.js', 'engine.js', 'app.js'].map(SRC).join('\n') +
    '\nmodule.exports = { renderBlanks: renderBlanks, LESSON_INDEX: LESSON_INDEX,' +
    ' TRACK_LESSONS: TRACK_LESSONS, mdInline: mdInline,' +
    ' seed: function (s) { P.seed = s; },' +
    ' preset: function (id, picked) { P.blanks = P.blanks || {}; P.blanks[id] = picked; },' +
    ' forget: function (id) { if (P.blanks) delete P.blanks[id];' +
    ' if (P.completed) delete P.completed[id]; } };';

  const mod = { exports: {} };
  /* Filling every blank correctly completes the lesson, which raises a toast and
     repaints the rail — both of which reach for elements of the page shell this stage
     does not build. One memoised element per id is enough for them to write into and
     is cheaper than pretending the completion path does not exist: it is the path a
     learner who gets everything right is on. */
  const byId = new Map();
  const shellEl = (id) => {
    if (!byId.has(id)) { const e = new El('div'); e.setAttribute('id', id); byId.set(id, e); }
    return byId.get(id);
  };
  const doc = {
    readyState: 'complete',
    getElementById: shellEl,
    createElement: (t) => new El(t),
    addEventListener: () => {},
    documentElement: new El('html'),
    body: new El('body'),
    activeElement: null,
    /* the app reaches the shell by id and everything else by class; a class selector
       against the whole document belongs to a view this stage does not mount */
    querySelector: (s) => (/^#[\w-]+$/.test(s) ? shellEl(s.slice(1)) : null),
    querySelectorAll: () => [],
  };
  new Function('module', 'window', 'document', 'localStorage', 'requestAnimationFrame',
    'ResizeObserver', 'devicePixelRatio', 'fetch', 'location', 'navigator', 'matchMedia', src)(
    mod, windowShim, doc,
    { getItem: () => null, setItem: () => {}, removeItem: () => {} },
    (fn) => fn(), undefined, 1,
    () => Promise.reject(new Error('the gate does not serve the network')),
    { hash: '', href: '', pathname: '/' },
    { userAgent: 'node', language: 'en' },
    () => ({ matches: false, addEventListener: () => {} }));

  const app = mod.exports;
  app.seed(SEED);

  /* app.js builds this lesson from a module's `blanks` entry; the id it mints is what
     the shuffle is keyed on, so the gate has to mint the same one */
  function lessonOf(lessonId, u) {
    return {
      id: lessonId, type: 'blanks', title: u.title, min: u.minutes || 8,
      trackId: 'stage', courseId: 'stage', num: 'x', mdText: u.brief,
      caption: u.caption, lang: u.lang || 'text', listing: u.listing,
      blanks: u.blanks || [],
    };
  }

  function mount(lesson) {
    /* lessonHeader and footNav walk the index and the flat lesson list; one course of
       one lesson is all either of them needs */
    app.LESSON_INDEX[lesson.id] = {
      lesson,
      track: { id: 'stage', kind: 'course', title: 'staged', name: 'staged',
        program: 'stage', band: 1, modules: [{ title: 'staged', lessons: [lesson] }] },
      module: { title: 'staged' }, mi: 0,
    };
    app.TRACK_LESSONS.stage = [lesson];
    const root = new El('div');
    app.renderBlanks(root, lesson);
    return root;
  }

  const click = (el) => el.dispatchEvent({ type: 'click' });
  /* The tiny DOM keeps a text node as the source that was assigned, so an option
     containing `&`, `<` or `"` reads back as the entity esc() wrote. A browser hands
     back the character. Decoding here compares what a learner sees rather than what
     the stub stored — without it the gate condemns `s & nfa.accepting` and a dozen
     others like it, which is a gate condemning working content. */
  const textOf = (el) => String(el.textContent)
    .replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');

  function drive(lessonId, u) {
    const problems = [];
    const blanks = u.blanks || [];
    const lesson = lessonOf(lessonId, u);
    app.forget(lessonId);
    let draws = 0, picks = 0;
    const holes = [];
    if (!blanks.length) return { draws, picks, holes, problems };

    let root = mount(lesson); draws++;
    const slots = root.querySelectorAll('[data-blk]');
    if (slots.length !== blanks.length) {
      problems.push(`${slots.length} blank button(s) drawn for ${blanks.length} blank(s)`);
      return { draws, picks, holes, problems };
    }
    /* the accessible name, because a row of buttons all reading "?" is what a screen
       reader met before */
    if (!/^Blank 1 of \d+/.test(String(slots[0].getAttribute('aria-label') || ''))) {
      problems.push('a blank button has no accessible name — a screen reader meets ' +
        (blanks.length) + ' buttons all called "?"');
    }
    if (!/blk-listing[^>]*tabindex="0"/.test(root.innerHTML)) {
      problems.push('the listing scrolls sideways and cannot be reached by keyboard');
    }

    /* ---- the order that is drawn, and the prose that is drawn with it ---- */
    const orderOf = [];        /* for each hole: authored index, in drawn order */
    for (let i = 0; i < blanks.length; i++) {
      const b = blanks[i];
      click(root.querySelectorAll('[data-blk]')[i]); draws++;
      const pick = root.querySelector('.blk-pick');
      if (!pick) { problems.push(`b${i + 1}: opening the blank drew no option list`); return { draws, picks, holes, problems }; }
      if (!pick.getAttribute('aria-labelledby')) {
        problems.push(`b${i + 1}: the option list is not labelled by its prompt`);
      }
      const head = root.querySelector('.blk-pick-h');
      const drawnPrompt = head ? textOf(head) : '';
      const srcPrompt = String(b.prompt || '');
      if (/\$[^$]+\$/.test(srcPrompt) && drawnPrompt.includes('$')) {
        problems.push(`b${i + 1}: the prompt's mathematics reaches the screen as its own ` +
          `source — "${drawnPrompt.slice(0, 60)}"`);
      }
      if (/`[^`]+`/.test(srcPrompt) && drawnPrompt.includes('`')) {
        problems.push(`b${i + 1}: the prompt's code span reaches the screen as backticks — ` +
          `"${drawnPrompt.slice(0, 60)}"`);
      }
      const shown = root.querySelectorAll('.blk-opt');
      const drawn = shown.map(textOf);
      const authored = (b.opts || []).map(String);
      if (drawn.length !== authored.length ||
          [...drawn].sort().join(' ') !== [...authored].sort().join(' ')) {
        problems.push(`b${i + 1}: the drawn options are not a permutation of the authored ones`);
      }
      const idx = shown.map((o) => +o.getAttribute('data-opt'));
      if (idx.some((n, k) => !Number.isInteger(n) || n < 0 || n >= authored.length ||
                             idx.indexOf(n) !== k)) {
        problems.push(`b${i + 1}: the drawn options do not carry one authored index each`);
      }
      orderOf.push(idx);
      holes.push({ keyAt: idx.indexOf(b.a) });
      click(root.querySelectorAll('[data-blk]')[i]);  /* close it again */ draws++;
    }

    /* ---- round 0: fill every hole through the buttons, and read the answers back ---- */
    const widest = Math.max(...blanks.map((b) => (b.opts || []).length));
    for (let r = 0; r < widest; r++) {
      /* which authored option a learner picking the r-th DRAWN option would land on */
      const want = orderOf.map((idx, i) => idx[Math.min(r, idx.length - 1)]);
      if (r === 0) {
        for (let i = 0; i < blanks.length; i++) {
          click(root.querySelectorAll('[data-blk]')[i]); draws++;
          const shown = root.querySelectorAll('.blk-opt');
          click(shown[0]); draws++; picks++;
          const slot = root.querySelectorAll('[data-blk]')[i];
          if (textOf(slot) !== String(blanks[i].opts[want[i]])) {
            problems.push(`b${i + 1}: picking an option put "${textOf(slot)}" in the ` +
              `blank, not "${blanks[i].opts[want[i]]}" — the shuffle's index map is wrong`);
          }
        }
      } else {
        /* later rounds are seeded through saved progress, which is the same path a
           returning learner takes and is two paints instead of two per hole */
        const picked = {};
        want.forEach((a, i) => { picked[i] = a; });
        app.preset(lessonId, picked);
        root = mount(lesson); draws++;
        picks += blanks.length;
      }
      const chk = root.querySelector('#blk-check');
      if (!chk) { problems.push(`round ${r}: Check is missing with every blank filled`); break; }
      if (chk.hasAttribute('disabled')) {
        problems.push(`round ${r}: Check is still disabled with every blank filled`);
        break;
      }
      click(chk); draws++;
      const rows = root.querySelectorAll('.blk-row p');
      if (rows.length !== blanks.length) {
        problems.push(`round ${r}: ${rows.length} explanation(s) for ${blanks.length} blank(s)`);
        break;
      }
      for (let i = 0; i < blanks.length; i++) {
        const b = blanks[i];
        const owed = (b.whys && b.whys[want[i]]) || b.why;
        /* the drawn paragraph is the explanation for the option ACTUALLY PICKED. This
           is the check that proves the shuffle's remap: whys are authored against the
           order in the file, and what the learner pressed is a slot in another order. */
        const got = textOf(rows[i]);
        const owedText = new El('div');
        owedText.innerHTML = app.mdInline(owed);
        if (got !== textOf(owedText)) {
          problems.push(`b${i + 1}: picking "${b.opts[want[i]]}" is answered with the ` +
            'explanation for a different option');
        }
      }
      /* the score line Check moves the keyboard onto */
      if (!/blk-fb[^>]*tabindex="-1"/.test(root.innerHTML) ||
          !/blk-fb-h">\d+ of \d+ right/.test(root.innerHTML)) {
        problems.push(`round ${r}: Check drew no score for the keyboard to land on`);
      }
    }

    /* ---- a learner's saved answers still mean what they meant ---- */
    const keys = {};
    blanks.forEach((b, i) => { keys[i] = b.a; });
    app.preset(lessonId, keys);
    root = mount(lesson); draws++;
    click(root.querySelector('#blk-check')); draws++;
    const m = /blk-fb-h">(\d+) of (\d+) right/.exec(root.innerHTML);
    if (!m || m[1] !== m[2]) {
      problems.push('answers saved as the authored key indices no longer grade as right — ' +
        'the shuffle has changed what a stored answer means, and every learner\'s ' +
        'completed work with it');
    }
    app.forget(lessonId);
    return { draws, picks, holes, problems };
  }

  return { drive };
}
