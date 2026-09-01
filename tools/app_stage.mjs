/**
 * app_stage.mjs — src/app.js loaded and running in Node, once.
 *
 * Two gates now mount real views out of app.js — verify_quiz.mjs drives renderBlanks
 * through blanks_stage.mjs, verify_tune_ui.mjs drives renderTune through
 * tune_stage.mjs — and the 360 KB of application source they each have to stand up is
 * identical. Kept as two copies it would drift, which would mean two different
 * applications under test and neither of them the one that ships. That is the argument
 * cycle 8 made when it pulled dom_stub.mjs out from under the two circuit gates, and it
 * is the same argument here.
 *
 * What belongs in this file is only what every view needs: the load order build.mjs
 * uses, the page-shell document every renderer reaches into, and the browser globals
 * app.js closes over. Anything a single view needs — a seed, a saved-progress preset,
 * a lesson shape — belongs in that view's stage.
 */

import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { El, windowShim } from './dom_stub.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = (f) => readFileSync(join(ROOT, 'src', f), 'utf8');

/* the order build.mjs concatenates them in: app.js reads TRACKS at the top and reaches
   MathML out of studio.js the moment any prose is rendered */
export const LOAD_ORDER = ['lang.js', 'tracks.js', 'studio.js', 'engine.js', 'app.js'];

/**
 * @param {object} opts
 *   exports  — a `{ name: expression }` map appended as module.exports, so a stage asks
 *              for the renderer and the state it needs by name rather than by reaching
 *              into a closure it cannot see.
 *   raf      — the requestAnimationFrame this run should use. The default runs the
 *              callback immediately, which is what a gate wants when it is not testing
 *              coalescing. A gate that IS testing coalescing must pass a deferred one:
 *              `raf = requestAnimationFrame(cb)` assigns AFTER a synchronous cb has
 *              already zeroed the flag, so an immediate rAF wedges every coalescer in
 *              the app permanently shut and reports perfect batching that is really no
 *              batching at all. That artefact is why this parameter exists.
 */
export function loadApp(opts) {
  opts = opts || {};
  globalThis.__CW_NO_BOOT = 1;

  const src = LOAD_ORDER.map(SRC).join('\n') + '\nmodule.exports = {' +
    Object.entries(opts.exports || {}).map(([k, v]) => ` ${k}: ${v}`).join(',') + ' };';

  /* One memoised element per id. Completing a lesson raises a toast and repaints the
     rail, both of which reach for parts of the page shell no stage builds; giving them
     something to write into is cheaper than pretending the completion path does not
     exist, because it is the path a learner who gets everything right is on. */
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
       against the whole document belongs to a view no stage mounts */
    querySelector: (s) => (/^#[\w-]+$/.test(s) ? shellEl(s.slice(1)) : null),
    querySelectorAll: () => [],
  };

  const mod = { exports: {} };
  new Function('module', 'window', 'document', 'localStorage', 'requestAnimationFrame',
    'ResizeObserver', 'devicePixelRatio', 'fetch', 'location', 'navigator', 'matchMedia',
    'getComputedStyle', 'cancelAnimationFrame', 'setTimeout', 'clearTimeout', src)(
    mod, windowShim, doc,
    { getItem: () => null, setItem: () => {}, removeItem: () => {} },
    opts.raf || ((fn) => { fn(); return 1; }),
    opts.ResizeObserver || class { observe() {} disconnect() {} },
    1,
    () => Promise.reject(new Error('the gate does not serve the network')),
    { hash: '', href: '', pathname: '/' },
    { userAgent: 'node', language: 'en' },
    () => ({ matches: false, addEventListener: () => {} }),
    /* palette() reads custom properties off the document; returning nothing lets every
       colour fall through to the declared fallback, which is what verify_sandbox does */
    () => ({ getPropertyValue: () => '' }),
    opts.cancelAnimationFrame || (() => {}),
    (fn) => 0, () => {});

  return { app: mod.exports, doc, shellEl, El };
}
