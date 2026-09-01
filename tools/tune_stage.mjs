/**
 * tune_stage.mjs — the shipped "hit the target" view, mounted in Node.
 *
 * verify_tune.mjs asks whether a target can be reached. verify_sandbox.mjs asks whether
 * the model's plot survives its extremes. Neither has ever mounted the thing a learner
 * touches, and that is where this track's brief actually lives: extremes, resize, rapid
 * input. So this stands renderTune up on the shared DOM stub and drives it.
 *
 * The one thing worth saying about how it is built:
 *
 *   THE FRAME QUEUE IS DEFERRED ON PURPOSE. An immediate requestAnimationFrame — the
 *   obvious stub, and the one blanks_stage.mjs correctly uses because it tests no
 *   coalescing — is not merely unrealistic here, it inverts the answer. Every coalescer
 *   in this codebase is written `raf = requestAnimationFrame(function () { raf = 0; ...
 *   })`, so with a synchronous callback the assignment lands AFTER the callback has
 *   already zeroed the flag: `raf` stays truthy for ever and every later schedule()
 *   returns early. A gate wired that way reports one repaint for sixty events whether
 *   the coalescing works or not, and would pass a renderer that had none. Frames are
 *   therefore queued and drained explicitly by frame().
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { El, DOC } from './dom_stub.mjs';
import { loadApp } from './app_stage.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');

export function stage() {
  /* the deferred frame queue described above */
  const queue = new Map();
  let nextId = 1;
  const raf = (fn) => { const id = nextId++; queue.set(id, fn); return id; };
  const caf = (id) => { queue.delete(id); };
  /* every callback pending at the start of this frame, and only those: a callback that
     schedules another one belongs to the next frame, exactly as in a browser */
  const frame = () => {
    const due = [...queue.entries()];
    queue.clear();
    due.forEach(([, fn]) => fn());
    return due.length;
  };

  const observers = [];
  class RO {
    constructor(fn) { this.fn = fn; this.live = true; observers.push(this); }
    observe(el) { this.el = el; }
    disconnect() { this.live = false; }
  }
  /* what a resize does: the browser calls every live observer's callback */
  const resizeTo = (el, w, h) => {
    el.clientWidth = w; el.clientHeight = h;
    el.resize(w, h);
    observers.filter((o) => o.live).forEach((o) => o.fn([{ target: o.el }]));
  };
  const liveObservers = () => observers.filter((o) => o.live).length;

  const { app, shellEl } = loadApp({
    raf, cancelAnimationFrame: caf, ResizeObserver: RO,
    exports: {
      renderTune: 'renderTune', LESSON_INDEX: 'LESSON_INDEX',
      TRACK_LESSONS: 'TRACK_LESSONS', Tune: 'Tune', Sandbox: 'Sandbox',
      save: 'function (id, v) { P.tune = P.tune || {}; P.tune[id] = { v: v }; }',
      savedOf: 'function (id) { return P.tune && P.tune[id] ? P.tune[id].v : null; }',
      forget: 'function (id) { if (P.tune) delete P.tune[id];' +
        ' if (P.completed) delete P.completed[id]; }',
      completed: 'function (id) { return !!P.completed[id]; }',
      leave: 'function () { if (teardown) { try { teardown(); } catch (e) {} teardown = null; } }',
    },
  });

  /* app.js builds this lesson from a module's `tune` entry; the id it mints is what
     saved progress is keyed on, so the stage has to mint the same one */
  function lessonOf(lessonId, u) {
    return {
      id: lessonId, type: 'tune', title: u.title, min: u.minutes || 8,
      trackId: 'stage', courseId: 'stage', num: 'x', mdText: u.brief,
      prompt: u.prompt, note: u.note, model: u.model, initial: u.initial,
      constants: u.constants, constraints: u.constraints, plotKey: u.plotKey,
    };
  }

  function mount(lessonId, u) {
    const lesson = lessonOf(lessonId, u);
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
    app.renderTune(root, lesson);
    /* the canvas is the one element whose measured size the renderer reads; give it the
       size the stylesheet gives it (100% of a 900px column, 296px tall) */
    const cv = root.querySelector('#tn-cv');
    if (cv) { cv.clientWidth = 900; cv.clientHeight = 296; }
    return root;
  }

  const drag = (root, k, value) => {
    const sl = root.querySelector('input[data-k="' + k + '"]');
    sl.value = String(value);
    sl.dispatchEvent({ type: 'input' });
    return sl;
  };
  const click = (root, id) => root.querySelector('#' + id).dispatchEvent({ type: 'click' });
  const toastText = () => String(shellEl('toast').textContent || '');

  return {
    app, mount, frame, drag, click, toastText, resizeTo, liveObservers, DOC,
    Tune: app.Tune, Sandbox: app.Sandbox,
    save: app.save, savedOf: app.savedOf, forget: app.forget,
    completed: app.completed, leave: app.leave,
  };
}

/* every tune unit in the catalogue, with the id app.js would mint for it */
export function tuneUnits() {
  const asList = (x) => (!x ? [] : (Array.isArray(x) ? x : [x]));
  const out = [];
  for (const f of readdirSync(join(ROOT, 'catalog'))
    .filter((x) => x.endsWith('.json') && !x.startsWith('_'))) {
    const course = JSON.parse(readFileSync(join(ROOT, 'catalog', f), 'utf8'));
    (course.modules || []).forEach((m, mi) => asList(m.tune).forEach((u, ui) => {
      out.push({
        id: `${course.id}-M${mi + 1}-TN${ui ? ui + 1 : ''}`,
        where: `${course.id} M${mi + 1}`, course: course.id, unit: u,
      });
    }));
  }
  return out;
}
