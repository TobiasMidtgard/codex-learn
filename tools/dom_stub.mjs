/**
 * dom_stub.mjs — enough of a DOM to mount the real editor, and no more.
 *
 * src/circuit.js touches no `document` at all: the whole editor is built by assigning
 * innerHTML to the root it is handed. So what a gate needs is one element that parses
 * HTML, answers the selector shapes that file uses, and delivers events up a parent
 * chain. Written here rather than pulled in because the repository has no dependencies
 * and a gate is not the place to start having them.
 *
 * It lives in its own file because two gates now drive the same editor —
 * verify_circuit_ui.mjs presses its keys, verify_circuit_model.mjs feeds its solver
 * extremes — and two stubs would drift, which would mean two different editors being
 * tested and neither of them the one that ships.
 */

/* ================================================================== a tiny DOM
 *
 * Enough of one to run createCircuit, and no more. circuit.js touches no `document`
 * at all — the whole editor is built by assigning innerHTML to the root it is handed —
 * so what is needed is an element that parses HTML, answers the selectors this file
 * uses, and delivers events. Written here rather than pulled in because the repository
 * has no dependencies and this gate is not the place to start.
 */

const VOID = new Set(['input', 'br', 'hr', 'img', 'meta', 'link', 'source']);

function decode(s) {
  return String(s).replace(/&quot;/g, '"').replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>').replace(/&amp;/g, '&');
}

let liveWindowListeners = 0;

class El {
  constructor(tag) {
    this.tagName = String(tag).toUpperCase();
    this.childNodes = [];
    this.parentElement = null;
    this._attrs = new Map();
    this._text = '';
    this._listeners = new Map();
    this.style = {};
    this.offsetWidth = 100;
    this.offsetHeight = 20;
    const self = this;
    this.classList = {
      add: (...c) => self._setClasses([...self._classes(), ...c]),
      remove: (...c) => self._setClasses(self._classes().filter((x) => !c.includes(x))),
      contains: (c) => self._classes().includes(c),
      toggle: (c, on) => (on === undefined ? (self.classList.contains(c) ? self.classList.remove(c) : self.classList.add(c))
        : (on ? self.classList.add(c) : self.classList.remove(c))),
    };
    this.dataset = new Proxy({}, {
      get: (_, k) => self.getAttribute('data-' + String(k).replace(/[A-Z]/g, (m) => '-' + m.toLowerCase())),
      set: (_, k, v) => { self.setAttribute('data-' + String(k).replace(/[A-Z]/g, (m) => '-' + m.toLowerCase()), v); return true; },
      has: (_, k) => self._attrs.has('data-' + String(k).replace(/[A-Z]/g, (m) => '-' + m.toLowerCase())),
    });
  }

  _classes() { return String(this.getAttribute('class') || '').split(/\s+/).filter(Boolean); }
  _setClasses(list) { this._attrs.set('class', [...new Set(list)].join(' ')); }

  getAttribute(n) { return this._attrs.has(n) ? this._attrs.get(n) : null; }
  setAttribute(n, v) { this._attrs.set(n, String(v)); }
  hasAttribute(n) { return this._attrs.has(n); }
  removeAttribute(n) { this._attrs.delete(n); }

  get hidden() { return this._attrs.has('hidden') && this._attrs.get('hidden') !== 'false'; }
  set hidden(v) { if (v) this._attrs.set('hidden', ''); else this._attrs.delete('hidden'); }

  get value() { return this._value === undefined ? (this.getAttribute('value') || '') : this._value; }
  set value(v) { this._value = String(v); }

  get textContent() {
    if (!this.childNodes.length) return this._text;
    return this.childNodes.map((c) => (typeof c === 'string' ? c : c.textContent)).join('');
  }
  set textContent(t) { this.childNodes = []; this._text = String(t); }

  get children() { return this.childNodes.filter((c) => typeof c !== 'string'); }

  get innerHTML() { return this._html || ''; }
  set innerHTML(html) {
    this._html = String(html);
    this.childNodes = parseHTML(String(html), this);
    this._text = '';
  }

  appendChild(el) { el.parentElement = this; this.childNodes.push(el); return el; }

  /* depth-first, self excluded — which is what querySelector means */
  _walk(out) {
    for (const c of this.childNodes) {
      if (typeof c === 'string') continue;
      out.push(c);
      c._walk(out);
    }
    return out;
  }

  querySelectorAll(sel) {
    const all = this._walk([]);
    const parts = String(sel).split(',').map((s) => s.trim()).filter(Boolean);
    const hit = [];
    for (const p of parts) for (const el of all) if (matches(el, p) && !hit.includes(el)) hit.push(el);
    hit.forEach = Array.prototype.forEach;
    return hit;
  }
  querySelector(sel) { return this.querySelectorAll(sel)[0] || null; }

  closest(sel) {
    let n = this;
    while (n) { if (matchesOne(n, sel.trim())) return n; n = n.parentElement; }
    return null;
  }

  /* One box unless a gate says otherwise. `resize(w, h)` is how a gate asks what the
     editor does at 375px or at 1200: a real browser lays every element out for itself,
     so an element that has been given a size keeps it and every other one falls back to
     the default. Nothing sets this unless it is testing a resize. */
  resize(w, h) { this._rect = { left: 0, top: 0, width: w, height: h, right: w, bottom: h }; return this; }
  getBoundingClientRect() {
    return this._rect || { left: 0, top: 0, width: 900, height: 400, right: 900, bottom: 400 };
  }
  getContext() { return (this._ctx = this._ctx || stubCtx()); }
  setPointerCapture() {}
  releasePointerCapture() {}

  focus() {
    if (DOC.activeElement === this) return;
    const was = DOC.activeElement;
    DOC.activeElement = this;
    if (was && was.dispatchEvent) was.dispatchEvent({ type: 'blur' });
    this.dispatchEvent({ type: 'focus' });
  }
  blur() {
    if (DOC.activeElement !== this) return;
    DOC.activeElement = null;
    this.dispatchEvent({ type: 'blur' });
  }

  addEventListener(type, fn) {
    if (!this._listeners.has(type)) this._listeners.set(type, []);
    this._listeners.get(type).push(fn);
  }
  removeEventListener(type, fn) {
    const l = this._listeners.get(type);
    if (l) this._listeners.set(type, l.filter((f) => f !== fn));
  }
  listenerCount(type) { return (this._listeners.get(type) || []).length; }

  /* bubbles to the parent chain, the way a real one does — which is the whole point of
     testing "a key pressed outside the editor" */
  dispatchEvent(ev) {
    ev.target = ev.target || this;
    ev.defaultPrevented = !!ev.defaultPrevented;
    ev.preventDefault = () => { ev.defaultPrevented = true; };
    ev.stopPropagation = () => { ev._stopped = true; };
    let n = this;
    while (n) {
      for (const fn of (n._listeners.get(ev.type) || []).slice()) fn.call(n, ev);
      if (ev._stopped) break;
      n = n.parentElement;
    }
    return !ev.defaultPrevented;
  }
}

/* The selector grammar this file actually uses: a descendant chain of
   tag / #id / .class / [attr] / [attr="value"] terms. Anything else is a bug in the
   gate rather than in the editor, so it throws instead of quietly matching nothing.
   `#id` was added when a third gate arrived — verify_quiz.mjs drives renderBlanks,
   and app.js reaches for its buttons by id where circuit.js reaches by class. Purely
   additive: a term that used to throw now matches, and nothing that used to match
   behaves differently, which is why the two older gates report byte-identically. */
function matchesOne(el, term) {
  const re = /^([a-zA-Z][\w-]*)?((?:#[\w-]+|\.[\w-]+|\[[^\]]+\])*)$/.exec(term);
  if (!re) throw new Error('the gate cannot parse the selector "' + term + '"');
  if (re[1] && el.tagName !== re[1].toUpperCase()) return false;
  for (const bit of re[2].match(/#[\w-]+|\.[\w-]+|\[[^\]]+\]/g) || []) {
    if (bit[0] === '#') { if (el.getAttribute('id') !== bit.slice(1)) return false; continue; }
    if (bit[0] === '.') { if (!el.classList.contains(bit.slice(1))) return false; continue; }
    const m = /^\[([\w-]+)(?:=["']?([^"'\]]*)["']?)?\]$/.exec(bit);
    if (!m) throw new Error('the gate cannot parse the selector "' + term + '"');
    if (!el.hasAttribute(m[1])) return false;
    if (m[2] !== undefined && el.getAttribute(m[1]) !== m[2]) return false;
  }
  return true;
}
function matches(el, sel) {
  const terms = sel.trim().split(/\s+/);
  if (!matchesOne(el, terms[terms.length - 1])) return false;
  let n = el.parentElement;
  for (let i = terms.length - 2; i >= 0; i--) {
    while (n && !matchesOne(n, terms[i])) n = n.parentElement;
    if (!n) return false;
    n = n.parentElement;
  }
  return true;
}

function parseHTML(html, parent) {
  const out = [];
  const stack = [{ el: null, kids: out }];
  const tok = /<\/?([a-zA-Z][\w-]*)((?:\s+[\w:-]+(?:=(?:"[^"]*"|'[^']*'|[^\s>]+))?)*)\s*\/?>/g;
  let last = 0, m;
  const text = (s) => { if (s) stack[stack.length - 1].kids.push(s); };
  while ((m = tok.exec(html))) {
    text(html.slice(last, m.index));
    last = tok.lastIndex;
    const name = m[1].toLowerCase();
    if (m[0][1] === '/') {
      for (let i = stack.length - 1; i > 0; i--) {
        if (stack[i].el.tagName === name.toUpperCase()) { stack.length = i; break; }
      }
      continue;
    }
    const el = new El(name);
    const at = /([\w:-]+)(?:=(?:"([^"]*)"|'([^']*)'|([^\s>]+)))?/g;
    let a;
    while ((a = at.exec(m[2]))) {
      el.setAttribute(a[1], decode(a[2] !== undefined ? a[2] : a[3] !== undefined ? a[3] : a[4] !== undefined ? a[4] : ''));
    }
    const top = stack[stack.length - 1];
    el.parentElement = top.el || parent;
    top.kids.push(el);
    if (!VOID.has(name)) stack.push({ el: el, kids: el.childNodes });
  }
  text(html.slice(last));
  return out;
}

/* the recording canvas from verify_sandbox, which objects to a coordinate nobody can draw */
function stubCtx() {
  const bad = [];
  const check = (op, args) => {
    for (const a of args) if (typeof a === 'number' && !isFinite(a)) { bad.push(op + '(' + args.join(', ') + ')'); return; }
  };
  /* Ops per frame, segmented on clearRect, which paint() calls exactly once at the top.
     That is how a mark that should be on the canvas is told apart from one that is
     computed and then not drawn — the failure mode cycle 2 found in kalman's RMS
     error, and the one a caret nobody paints would be. */
  const frames = [];
  let n = 0;
  const ctx = { bad, frames, canvas: { width: 900, height: 400 } };
  const tick = (op, args) => { n++; check(op, args); };
  for (const op of ['moveTo', 'lineTo', 'arc', 'rect', 'fillRect', 'strokeRect',
    'translate', 'scale', 'setTransform', 'transform', 'quadraticCurveTo', 'bezierCurveTo',
    'arcTo', 'ellipse', 'rotate', 'roundRect']) ctx[op] = (...a) => tick(op, a);
  ctx.clearRect = (...a) => { frames.push(n); n = 0; check('clearRect', a); };
  for (const op of ['beginPath', 'closePath', 'stroke', 'fill', 'clip', 'save', 'restore',
    'setLineDash', 'getLineDash', 'createLinearGradient', 'createRadialGradient']) ctx[op] = () => { n++; };
  ctx.fillText = (s, x, y) => tick('fillText', [x, y]);
  ctx.strokeText = (s, x, y) => tick('strokeText', [x, y]);
  ctx.measureText = () => ({ width: 10 });
  return ctx;
}

const DOC = { activeElement: null };
const WIN = new El('window');
const windowShim = {
  devicePixelRatio: 1,
  addEventListener: (t, f) => { liveWindowListeners++; WIN.addEventListener(t, f); },
  removeEventListener: (t, f) => { liveWindowListeners--; WIN.removeEventListener(t, f); },
};

/* How many window listeners are live, which is how a gate catches a dispose that
   forgot one. A function rather than the binding itself: an imported `let` is a live
   view in ESM, but exporting the accessor says out loud that the number moves. */
export function windowListenerCount() { return liveWindowListeners; }

export { El, matches, matchesOne, parseHTML, stubCtx, DOC, WIN, windowShim, VOID, decode };
