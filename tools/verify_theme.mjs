/* verify_theme.mjs — the gate Track 5 did not have.
 *
 * There is nothing in a stylesheet for a solver to disagree with, which is why this
 * track had no gate while the other five acquired one. So this does not try to judge
 * the design. It checks the three things about it that are arithmetic:
 *
 *   1. Every colour comes from a token, or is exempted here in writing. The curriculum
 *      states the invariant — "a hard-coded hex is a light-theme bug waiting" — and it
 *      has now been broken twice: seven unit chips in one cycle, the primary nav's
 *      hover wash in this one.
 *   2. Contrast, in BOTH themes, recomputed from the live token tables. Budgeted per
 *      entry in tools/theme_budget.json, so a token edit that quietly drops a surface
 *      under the floor fails here rather than shipping.
 *   3. The canvas palette. Sandbox.palette() is JavaScript rather than CSS, so none
 *      of the above reached it, and its two quiet tiers were the oldest unfixed
 *      defect this track had: five cycles measured them by hand and handed them on.
 *   4. The topbar fits a 375px phone. Its furniture is fixed-width and its knobs are
 *      tokens, so the sum is computable — and it did not fit, which is why the screen
 *      title was being shrunk to nothing.
 *
 * Reads src/index.head.html as shipped. No browser, so nothing here measures a glyph:
 * where an advance width is needed it comes from the font's own metric and is named.
 */
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, '$1')), '..');
/* an explicit path so the gate can be pointed at a deliberately broken copy; a gate
   that has never been seen to fail is a gate nobody has checked */
const HEAD = process.argv[2] ? path.resolve(process.argv[2]) : path.join(ROOT, 'src', 'index.head.html');
const BUDGET = path.join(ROOT, 'tools', 'theme_budget.json');

const src = fs.readFileSync(HEAD, 'utf8');
const css = src.slice(src.indexOf('<style>') + 7, src.indexOf('</style>'));

/* src/desk.js is the only file in the codebase that carries its own CSS — a modal that
   is inert until summoned pays for none of it until it is opened, and injecting on first
   open keeps the whole feature in one file. The consequence was that this gate, which
   reads the stylesheet, had never measured a single desk surface: 107 surfaces budgeted
   and not one of them from the file that paints the notepad and the calculator. It is
   read here through the same public entry point the app uses, so what is measured is
   what ships. See GAUNTLET_LOG cycle 12. */
function deskCss() {
  const mod = { exports: {} };
  new Function('module', fs.readFileSync(path.join(ROOT, 'src', 'desk.js'), 'utf8') +
    '\nmodule.exports = { Desk };')(mod);
  if (typeof mod.exports.Desk?.css !== 'function') {
    bad('tokens', 'src/desk.js no longer exposes its stylesheet — this gate cannot see it');
    return '';
  }
  return mod.exports.Desk.css();
}

let fails = 0;
const sectionFails = {};
function ok(tag, msg) { console.log('[ok  ] ' + tag.padEnd(8) + ' ' + msg); }
function bad(tag, msg) { fails++; sectionFails[tag] = (sectionFails[tag] || 0) + 1; console.log('[FAIL] ' + tag.padEnd(8) + ' ' + msg); }
const clean = tag => !sectionFails[tag];

/* ---------- a rule walker that understands @media, which a regex does not ---------- */
/* `([^{}]+){([^{}]*)}` reads "@media (max-width:980px){ :root" as one selector and then
   enforces nothing about the rest of the block. Every rule below carries the media
   preludes it sits inside, because a rule's meaning depends on them. */
function parseRules(text) {
  const clean = text.replace(/\/\*[\s\S]*?\*\//g, '');
  const out = [];
  const stack = [];
  let i = 0, buf = '';
  while (i < clean.length) {
    const c = clean[i];
    if (c === '{') {
      const prelude = buf.trim().replace(/\s+/g, ' ');
      buf = '';
      if (prelude.startsWith('@')) { stack.push(prelude); i++; continue; }
      /* a rule: read to its matching close */
      let d = 1, j = i + 1;
      for (; j < clean.length && d; j++) { if (clean[j] === '{') d++; else if (clean[j] === '}') d--; }
      out.push({ sel: prelude, body: clean.slice(i + 1, j - 1).trim(), media: stack.slice() });
      i = j;
      continue;
    }
    if (c === '}') { stack.pop(); buf = ''; i++; continue; }
    buf += c; i++;
  }
  return out;
}
/* Both stylesheets, walked as one. The desk's :root block declares two tokens of its
   own (--dsk-veil, --dsk-shadow), so it has to reach tokensFrom() as well as the
   contrast pass — concatenating here is what puts it in front of every check below
   rather than only the one that named it. */
const rules = parseRules(css).concat(parseRules(deskCss()));

/* ---------- token tables ---------- */
function tokensFrom(sel) {
  const t = {};
  for (const r of rules) if (r.sel === sel) for (const m of r.body.matchAll(/(--[\w-]+)\s*:\s*([^;]+)/g)) t[m[1]] = m[2].trim();
  return t;
}
const dark = tokensFrom(':root');
const light = Object.assign({}, dark, tokensFrom('[data-theme=light]'));
if (!dark['--ground'] || !light['--ground']) { bad('tokens', 'could not read both token tables'); process.exit(1); }

/* ---------- type ---------- */
/* A size now comes from --t-* the way a colour comes from --ink-*, so anything that
   reasons about a length in glyphs has to resolve the token first. Both consumers below
   used to parseFloat the declaration, which was a literal; the moment it stopped being
   one the id column threw and the topbar printed "NaNpx of furniture" and still reported
   [ok], because NaN < 60 is false. Neither of those is a colour bug and neither would
   have been found by the contrast pass — a gate that cannot compute its own number has
   to say so rather than pass. */
function typePx(v, depth) {
  if (v == null) return NaN;
  v = String(v).trim(); depth = depth || 0;
  if (depth > 8) return NaN;
  const m = v.match(/^var\(\s*(--[\w-]+)\s*(?:,\s*([\s\S]*))?\)$/);
  if (m) return dark[m[1]] !== undefined ? typePx(dark[m[1]], depth + 1) : typePx(m[2], depth + 1);
  const p = v.match(/^([\d.]+)px$/);
  return p ? parseFloat(p[1]) : NaN;
}

/* ---------- colour ---------- */
function parseColor(c, tbl, depth) {
  c = String(c).trim(); depth = depth || 0;
  if (depth > 8) return null;
  let m = c.match(/^var\(\s*(--[\w-]+)\s*(?:,\s*([\s\S]*))?\)$/);
  if (m) { const r = tbl[m[1]]; return r ? parseColor(r, tbl, depth + 1) : (m[2] ? parseColor(m[2], tbl, depth + 1) : null); }
  m = c.match(/^color-mix\(in srgb,\s*([\s\S]+?)\s+([\d.]+)%\s*,\s*transparent\s*\)$/);
  if (m) { const b = parseColor(m[1], tbl, depth + 1); if (!b) return null; return [b[0], b[1], b[2], b[3] * (+m[2] / 100)]; }
  m = c.match(/^#([0-9a-f]{6})$/i);
  if (m) return [parseInt(m[1].slice(0, 2), 16), parseInt(m[1].slice(2, 4), 16), parseInt(m[1].slice(4, 6), 16), 1];
  m = c.match(/^#([0-9a-f]{3})$/i);
  if (m) return m[1].split('').map(x => parseInt(x + x, 16)).concat([1]);
  m = c.match(/^rgba?\(([^)]+)\)$/i);
  if (m) { const p = m[1].split(',').map(x => parseFloat(x)); return [p[0], p[1], p[2], p.length > 3 ? p[3] : 1]; }
  if (c === 'white') return [255, 255, 255, 1];
  if (c === 'transparent') return [0, 0, 0, 0];
  return null;
}
const overlay = (fg, bg) => [0, 1, 2].map(i => fg[i] * fg[3] + bg[i] * (1 - fg[3])).concat([1]);
function luminance(c) {
  const f = c.slice(0, 3).map(v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); });
  return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2];
}
function contrast(a, b) {
  const l1 = luminance(a), l2 = luminance(b);
  return (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
}
/* a background stack is written outermost-last; anything translucent composites down
   onto --ground, which is the only surface in the app that is always opaque */
function flatten(stack, tbl) {
  let bg = null;
  for (let i = stack.length - 1; i >= 0; i--) {
    const c = parseColor(stack[i], tbl);
    if (!c) return null;
    bg = bg === null ? (c[3] === 1 ? c : overlay(c, parseColor('var(--ground)', tbl))) : overlay(c, bg);
  }
  return bg;
}

/* ---------- 1. every colour from a token ---------- */
/* A literal is allowed only where a theme cannot help: a surface that is dark in both
   themes on purpose, a scrim, ink on user-supplied content, or a value that is already
   inside a [data-theme=light] rule. Each exemption states why, because an exemption
   list with no reasons is a way of turning a gate off one line at a time. */
const LITERAL_EXEMPT = [
  { re: /^\.blob/, why: 'decorative background wash; the light theme dims the pair with opacity:.55' },
  { re: /^::selection$/, why: 'selection tint; the browser composites it over the ink itself' },
  { re: /^\.ed-ta::selection$/, why: 'same, in the editor' },
  { re: /^\.scrim$/, why: 'a modal scrim darkens the page in both themes by definition' },
  { re: /^\.toast$/, why: 'the toast is a dark chip in both themes, like the editor' },
  { re: /^\.gmark\.fail::(after|before)$/, why: 'white cross on --bad, which is dark in both themes' },
  { re: /^\.pb-icon$/, why: 'the fallback when a band has no --tt tint' },
  { re: /^\.cb-preview$/, why: 'the iframe that renders the learner own HTML, which assumes a white canvas' },
  { re: /^\.preview-(wrap|frame)$/, why: 'same iframe' },
  { re: /^\.(wb-bar|wb-panel|wb-foot|mobile-tabs|mobile-tabs button|ftab:hover|ftab\.active|ptab\.active|ptab \.badge|ptab \.badge\.bad|wbar|rt-status\.ready i|ftab\.active::before)$/, why: 'the workbench chrome sits on --editor, which is dark in both themes' },
  { re: /^\.(pq-b\.ok|pq-b\.next|dg-i)$/, why: 'ink on a saturated amber or green chip that does not flip' },
  { re: /^\.(track-card|course-card):hover$/, why: 'a lift shadow; black at low alpha is the shadow in both themes' },
  { re: /^\.btn\.run:disabled$/, why: 'the workbench run button, which sits on --editor; same list' },
  { re: /^\.(resume \.rr::before|spark i\.hi|weekchart \.d\.today i|rowlink \.ic|strip i\.now|lv-Intermediate|lv-Advanced|pcard\.warn \.dot|btn\.primary:hover|btn\.run:hover|prof-av)$/, why: 'accent tint or glow outside this cycle subsystem — see GAUNTLET_LOG cycle 5' },
];
{
  const lightSels = new Set();
  for (const r of rules) if (/\[data-theme=light\]/.test(r.sel)) {
    for (const p of r.sel.split(',')) lightSels.add(p.trim().replace(/\[data-theme=light\]\s*/, '').trim());
  }
  const offenders = [];
  for (const r of rules) {
    if (/\[data-theme=light\]/.test(r.sel)) continue;
    if (/^:root$|^\[data-theme/.test(r.sel)) continue;
    if (r.media.some(m => /@keyframes/.test(m))) continue;
    const lits = [...r.body.matchAll(/(?:^|[:\s,(])(#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\))/g)].map(x => x[1]);
    if (!lits.length) continue;
    const parts = r.sel.split(',').map(s => s.trim());
    if (parts.every(p => lightSels.has(p))) continue;
    if (LITERAL_EXEMPT.some(e => parts.every(p => e.re.test(p)))) continue;
    offenders.push(r.sel + '  ->  ' + [...new Set(lits)].join(' '));
  }
  if (offenders.length) {
    for (const o of offenders) bad('tokens', 'literal colour with no light theme: ' + o);
  } else {
    ok('tokens', 'every colour comes from a token or a written exemption (' + LITERAL_EXEMPT.length + ' exemptions)');
  }
}

/* ---------- 2. contrast, both themes, against a budget ---------- */
const FLOOR = { text: 4.5, large: 3.0, graphic: 3.0, state: 1.1 };
{
  const budget = JSON.parse(fs.readFileSync(BUDGET, 'utf8'));
  /* A `state` entry names the RULE whose background it is asking about, and the value
     is read out of the stylesheet — for the dark theme from `sel`, for the light one
     from `[data-theme=light] sel`, falling back to the dark value when that rule does
     not exist. That fallback is the defect this cycle opened on: .inav:hover had no
     light rule, so it painted white over white and measured 1.00:1. Reading it here
     rather than restating it in the budget is what makes the check load-bearing. */
  /* The value a rule actually declares, read out of the stylesheet. Same lookup for both
     themes: `sel` for dark, `[data-theme=light] sel` for light, falling back to the dark
     rule when the light one does not exist — that fallback IS the .inav:hover defect.

     This started as hoverBg, for `state` entries only, and that was the whole weakness of
     this gate: every other entry took its colour from the BUDGET, so the budget described
     the stylesheet instead of enforcing it. Reverting a fixed rule to the token it had
     before left the gate green, because nothing ever asked the stylesheet what colour it
     was using. Demonstrated: 14 mutations of the answering surface, of which this gate
     rejected 2. An entry that names `sel` is now read from the source and the budget's own
     `fg` is ignored, so a revert moves the measured number. See GAUNTLET_LOG cycle 11. */
  function declared(sel, prop, theme) {
    const want = theme === 'light' ? '[data-theme=light] ' + sel : sel;
    const re = new RegExp('(?:^|;)\\s*' + prop + '\\s*:\\s*([^;]+)');
    for (let i = rules.length - 1; i >= 0; i--) {
      const r = rules[i];
      if (r.media.length) continue;
      if (r.sel.split(',').map(s => s.trim()).indexOf(want) < 0) continue;
      const m = r.body.match(re);
      if (m) return m[1].trim();
    }
    return theme === 'light' ? declared(sel, prop, 'dark') : null;
  }
  const hoverBg = (sel, theme) => declared(sel, 'background(?:-color)?', theme);
  let worstText = Infinity, worstName = '';
  let worstState = Infinity, worstStateName = '';
  /* An entry that carries its own `floor` is one the design deliberately holds below the
     standard — a placeholder that must stay quieter than the value it stands in for. It
     still has to clear the floor it declares, but it must not set the headline: letting
     it do so makes the summary read like a regression every time such a surface is added,
     and the headline is the number the log compares between cycles. Counted instead. */
  let relaxed = 0;
  /* how many surfaces take their ink from the stylesheet rather than from this file */
  let sourceRead = 0;
  for (const e of budget.surfaces) {
    const floor = e.floor !== undefined ? e.floor : FLOOR[e.kind];
    if (floor === undefined) { bad('contrast', e.name + ': unknown kind "' + e.kind + '"'); continue; }
    for (const [theme, tbl] of [['dark', dark], ['light', light]]) {
      let r;
      if (e.kind === 'state') {
        const under = (theme === 'light' && e.vsLight) ? e.vsLight : e.vs;
        let stack;
        if (e.from) {
          const paint = hoverBg(e.from, theme);
          if (!paint) { bad('contrast', e.name + ' [' + theme + ']: no background on ' + e.from); continue; }
          stack = [paint].concat(under);
        } else {
          stack = (theme === 'light' && e.bgLight) ? e.bgLight : e.bg;
        }
        const on = flatten(stack, tbl), off = flatten(under, tbl);
        if (!on || !off) { bad('contrast', e.name + ' [' + theme + ']: a colour did not resolve'); continue; }
        r = contrast(on, off);
        if (r < worstState) { worstState = r; worstStateName = e.name + ' [' + theme + ']'; }
      } else {
        const bg = flatten((theme === 'light' && e.bgLight) ? e.bgLight : e.bg, tbl);
        /* `sel` names the rule the ink comes from, and the stylesheet is then the
           authority; `fg` alone is a description and cannot fail when the source moves. */
        let fgSrc = e.fg;
        if (e.sel) {
          fgSrc = declared(e.sel, e.prop || 'color', theme);
          if (!fgSrc) { bad('contrast', e.name + ' [' + theme + ']: `' + e.sel + '` declares no ' + (e.prop || 'color')); continue; }
          if (theme === 'dark') sourceRead++;
        }
        const fg = parseColor(fgSrc, tbl);
        if (!bg || !fg) { bad('contrast', e.name + ' [' + theme + ']: a colour did not resolve'); continue; }
        r = contrast(overlay(fg, bg), bg);
        if (e.kind === 'text' && e.floor === undefined && r < worstText) { worstText = r; worstName = e.name + ' [' + theme + ']'; }
      }
      if (e.floor !== undefined && theme === 'dark') relaxed++;
      if (r + 1e-9 < floor) {
        bad('contrast', e.name + ' [' + theme + '] ' + r.toFixed(2) + ':1 is under the ' + floor + ':1 floor for ' + e.kind);
      }
      /* A surface held below the standard floor on purpose is one whose defect is being
         too LOUD, and a floor cannot say that. The three placeholders are the case: a
         placeholder that reaches 4.5:1 stops being distinguishable from a filled field,
         which is the decision cycle 5 recorded and cycle 11 wrote the 2.5 for. Until this
         cycle they shared --on-editor-3 with the canvas, so raising the canvas would have
         raised them too and nothing would have objected. */
      if (e.ceiling !== undefined && r > e.ceiling + 1e-9) {
        bad('contrast', e.name + ' [' + theme + '] ' + r.toFixed(2) + ':1 is over the ' + e.ceiling +
          ':1 ceiling it is deliberately held under');
      }
    }
  }
  if (clean('contrast')) ok('contrast', budget.surfaces.length + ' surfaces x 2 themes clear their floor · tightest text ' +
    worstText.toFixed(2) + ':1 (' + worstName + ') · faintest state ' + worstState.toFixed(2) + ':1 (' + worstStateName + ')' +
    (relaxed ? ' · ' + relaxed + ' held below the standard floor on purpose, each with its own' : '') +
    ' · ' + sourceRead + ' read their ink out of the stylesheet');
}

/* ---------- 3. the topbar fits a phone ---------- */
/* Every number here is read out of the stylesheet, so turning a knob back moves the
   result. The two glyph advances are the fonts' own metrics and are named, because
   nothing in this repository can measure text. */
{
  const MONO_ADVANCE = 0.6;      /* JetBrains Mono: 600/1000 em, all glyphs */
  const EMOJI_ADVANCE = 1.15;    /* a colour emoji is squarer than a Latin glyph */
  const VIEWPORT = 375;          /* the width the curriculum names */
  const TITLE_FLOOR = 60;        /* the screen title has to survive with an ellipsis */
  const px = v => parseFloat(v);
  function declIn(sel, prop, mediaRe) {
    for (let i = rules.length - 1; i >= 0; i--) {
      const r = rules[i];
      if (r.sel.split(',').map(s => s.trim()).indexOf(sel) < 0) continue;
      if (mediaRe && !r.media.some(m => mediaRe.test(m))) continue;
      if (!mediaRe && r.media.length) continue;
      const m = r.body.match(new RegExp('(?:^|;)\\s*' + prop.replace(/[-]/g, '\\-') + '\\s*:\\s*([^;]+)'));
      if (m) return m[1].trim();
    }
    return null;
  }
  const phone = /max-width:\s*640px/;
  const tablet = /max-width:\s*980px/;
  const railIcon = px(declIn(':root', '--rail-icon', tablet) || declIn(':root', '--rail-icon'));
  const gap = px(declIn('.topbar', '--topbar-gap', phone) || declIn(':root', '--topbar-gap'));
  const pad = px(declIn('.topbar', '--topbar-pad', phone) || declIn(':root', '--topbar-pad'));
  const mpad = px(declIn('.metric', '--metric-pad', phone) || '12px');
  const mgap = px(declIn('.metric', 'gap') || '6px');
  const btn = px(declIn('.tbtn', 'width') || '32px');
  const menu = px(declIn('.menu-btn', 'width') || '32px');
  const flameSize = typePx(declIn('.metric.streak .fl', 'font-size') || '13px');
  const digitSize = typePx(declIn('.metric.streak b', 'font-size') || '12px');
  const flame = flameSize * EMOJI_ADVANCE;
  const digit = digitSize * MONO_ADVANCE;
  const xpHidden = /^none$/.test(declIn('.metric.xp', 'display', phone) || '');

  /* Every input named, so an unresolved one is reported as itself rather than as a NaN
     that propagates into the total and then passes the floor test by being unordered. */
  for (const [what, v] of [['--rail-icon', railIcon], ['--topbar-gap', gap], ['--topbar-pad', pad],
                           ['--metric-pad', mpad], ['.metric gap', mgap], ['.tbtn width', btn],
                           ['.menu-btn width', menu], ['.metric.streak .fl font-size', flameSize],
                           ['.metric.streak b font-size', digitSize]]) {
    if (!Number.isFinite(v)) bad('topbar', 'could not resolve ' + what + ' — this check cannot be computed, so it is not passing');
  }

  /* worst case a learner can actually reach: a 365-day streak, a six-character XP */
  const streakBox = 2 * mpad + flame + mgap + 3 * digit;
  const xpBox = xpHidden ? 0 : 2 * mpad + 6 * digit;
  const items = 6 + (xpHidden ? 0 : 1);   /* menu, screen-id, spacer, streak, 2 tbtn */
  const furniture = (items - 1) * gap + menu + 2 * btn + streakBox + xpBox;
  const avail = VIEWPORT - railIcon - 2 * pad;
  const left = avail - furniture;
  const line = 'at ' + VIEWPORT + 'px: ' + avail.toFixed(0) + 'px of bar, ' + furniture.toFixed(1) +
    'px of furniture, ' + left.toFixed(1) + 'px for the screen title' + (xpHidden ? ' (XP pill stands down)' : '');
  if (!Number.isFinite(left)) bad('topbar', line + ' — the bar\'s own arithmetic did not resolve');
  else if (left < TITLE_FLOOR) bad('topbar', line + ' — under the ' + TITLE_FLOOR + 'px floor');
  else ok('topbar', line);

  /* a control that can shrink is a control that can shrink past a finger */
  let held = true;
  for (const sel of ['.tbtn', '.menu-btn', '.metric']) {
    const f = declIn(sel, 'flex');
    if (!f || !/^none\b/.test(f)) { held = false; bad('topbar', sel + ' is not flex:none, so it shrinks below its own box under pressure'); }
  }
  if (held) ok('topbar', '.tbtn, .menu-btn and .metric hold their box (WCAG 2.5.8 target size)');
}

/* ---------- 4. the fixed tracks that are sized against the type they hold ---------- */
/* This check used to be about one column. The id track was 32px against a 9px right pad
   and fifteen of the sixty-two ids are seven characters, so text-align:right spilled them
   leftwards out of the row; a track sized against the data cannot drift back.
 *
 * It was written for `.rail-course .cid` and stopped there — and `.rail-lesson .num`, the
 * rule immediately ABOVE it in the stylesheet, sharing its font-size declaration and its
 * padding, had exactly the same defect and was never measured. 596 of the 1990 lesson
 * numbers the rail can draw are four or five glyphs, and 22px of track holds 3.6, so
 * 30% of the rail was drawing a number with its leading glyph cut off — "10·r2" as
 * "0·r2", which is not a truncation a learner can see is a truncation. It is the
 * curriculum's own invariant: a gate that skips what it did not expect is worse than no
 * gate. Both tracks are entries now, and adding a third is a row rather than a rewrite.
 *
 * The worst case is derived from the catalogue and from app.js's own two num formats,
 * not written down here, because a literal would stop tracking the data the moment a
 * course gained an eleventh module. */
{
  const MONO_ADVANCE = 0.6;

  /* every course id, for the id column */
  const ids = [];
  for (const f of fs.readdirSync(path.join(ROOT, 'catalog'))) {
    if (!/^_spine.*\.json$/.test(f)) continue;
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, 'catalog', f), 'utf8'));
    for (const c of (d.courses || [])) ids.push(c.id);
  }

  /* every lesson number, built the way src/app.js builds it. UNIT_SPEC's order and tags
     are read out of app.js rather than copied, so a new unit kind cannot silently widen
     the column without this gate noticing. */
  const appSrc = fs.readFileSync(path.join(ROOT, 'src', 'app.js'), 'utf8');
  const spec = [...appSrc.matchAll(/\{\s*key:\s*'(\w+)',\s*sfx:\s*'\w+',\s*type:\s*'\w+',\s*tag:\s*'(\w+)'/g)]
    .map(m => [m[1], m[2]]);
  if (!spec.length) bad('tracks', 'could not read UNIT_SPEC out of src/app.js, so the lesson numbers cannot be derived');
  const nums = [];
  const asList = v => (v == null ? [] : (Array.isArray(v) ? v : [v]));
  for (const f of fs.readdirSync(path.join(ROOT, 'catalog'))) {
    if (!/\.json$/.test(f) || f.startsWith('_')) continue;
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, 'catalog', f), 'utf8'));
    (d.modules || []).forEach((m, mi) => {
      for (const [key, tag] of spec) {
        asList(m[key]).forEach((u, ui) => { if (u) nums.push((mi + 1) + '·' + tag + (ui ? (ui + 1) : '')); });
      }
      asList(m.lab).forEach((lab, li) => { if (lab) nums.push('' + (mi + 1) + (li ? '·L' + (li + 1) : '')); });
    });
  }
  /* the foundation tracks in src/tracks.js use the other format — app.js:23 */
  {
    const tj = fs.readFileSync(path.join(ROOT, 'src', 'tracks.js'), 'utf8');
    const arrayAt = (text, from) => {
      let d = 0, j = from;
      for (; j < text.length; j++) { if (text[j] === '[') d++; else if (text[j] === ']' && --d === 0) break; }
      return text.slice(from, j);
    };
    for (const mm of tj.matchAll(/modules:\s*\[/g)) {
      const block = arrayAt(tj, mm.index + mm[0].length - 1);
      let mi = 0;
      for (const lm of block.matchAll(/lessons:\s*\[/g)) {
        const lessons = arrayAt(block, lm.index + lm[0].length - 1);
        const n = (lessons.match(/\{\s*id:/g) || []).length;
        for (let li = 0; li < n; li++) nums.push((mi + 1) + '.' + (li + 1));
        mi++;
      }
    }
  }

  const longestOf = a => a.reduce((x, y) => (y.length > x.length ? y : x), '');
  const COLUMNS = [
    { name: 'the course id column', row: '.rail-course', cell: '.rail-course .cid',
      col: 0, strings: ids, what: 'course ids' },
    { name: 'the lesson number column', row: '.rail-lesson', cell: '.rail-lesson .num',
      col: 0, strings: nums, what: 'lesson numbers the rail can draw' },
  ];
  const said = [];
  for (const c of COLUMNS) {
    const rowRule = rules.find(r => r.sel === c.row && !r.media.length && /grid-template-columns/.test(r.body));
    const cellRule = rules.find(r => r.sel.split(',').map(s => s.trim()).indexOf(c.cell) >= 0 && /font-size/.test(r.body));
    if (!rowRule || !cellRule) { bad('tracks', c.name + ': could not find ' + c.row + '\'s grid or ' + c.cell + '\'s type'); continue; }
    const tracks = rowRule.body.match(/grid-template-columns\s*:\s*([^;}]+)/)[1].trim().split(/\s+/);
    const track = parseFloat(tracks[c.col]);
    const size = typePx((cellRule.body.match(/font-size\s*:\s*([^;}]+)/) || [])[1]);
    const padR = parseFloat((cellRule.body.match(/padding-right\s*:\s*([\d.]+)px/) || [0, 0])[1]) || 0;
    if (!Number.isFinite(track) || !Number.isFinite(size)) {
      bad('tracks', c.name + ': could not resolve the track (' + tracks[c.col] + ') or the type size (' +
        (cellRule.body.match(/font-size\s*:\s*([^;}]+)/) || [])[1] + ')');
      continue;
    }
    const longest = longestOf(c.strings);
    const need = longest.length * size * MONO_ADVANCE + padR;
    /* how many would be cut, not merely whether the worst one is — a column that clips
       0.4% of its rows and one that clips 30% are not the same defect */
    const room = (track - padR) / (size * MONO_ADVANCE);
    const over = c.strings.filter(s => s.length > room + 1e-9).length;
    if (need > track + 1e-9) {
      bad('tracks', c.name + ' is ' + track + 'px and "' + longest + '" needs ' + need.toFixed(1) +
        'px (' + longest.length + ' glyphs at ' + size + 'px JetBrains Mono, plus ' + padR + 'px of pad) — ' +
        over + ' of ' + c.strings.length + ' ' + c.what + ' lose their leading glyph, and text-align:right ' +
        'inside overflow:hidden cuts the FRONT, so what is drawn is another row\'s number');
    } else {
      said.push(track + 'px holds "' + longest + '", the longest of ' + c.strings.length + ' ' + c.what + ', at ' + need.toFixed(1) + 'px');
    }
  }
  if (clean('tracks')) ok('tracks', said.join(' · '));
}

/* ---------- 5. the mobile drawer leaves the tab order when it closes ---------- */
{
  const closed = rules.find(r => r.sel === '.rail' && r.media.some(m => /max-width:\s*980px/.test(m)));
  const open = rules.find(r => r.sel === '.rail.open' && r.media.some(m => /max-width:\s*980px/.test(m)));
  const hides = closed && /visibility\s*:\s*hidden/.test(closed.body);
  const shows = open && /visibility\s*:\s*visible/.test(open.body);
  if (hides && shows) ok('drawer', 'the closed drawer is out of the tab order and the open one is in it');
  else bad('drawer', 'the closed drawer is only translated off-screen, which leaves every control in it tabbable');
}

/* ---------- 6. the canvas palette, which is JavaScript and so had no gate ----------
 *
 * Sandbox.palette() is the ink of every pixel this application draws that is not a DOM
 * node: 13 visualisers, 3 tune models, the analysis plot, the schematic canvas and the
 * breadboard. It reads --on-editor-* out of the live token table, so the values ARE in
 * the stylesheet this gate already parses — but nothing connected them, and the two
 * quiet tiers sat at 2.93:1 and 1.86:1 while five cycles measured them by hand and
 * handed them on. What follows is the connection.
 *
 *   a. Every tier's fallback literal — in studio.js's own v(name, fallback) and in the
 *      standalone copy circuit.js keeps for when Sandbox is absent — equals the token.
 *      They did not: circuit.js's read dim '#888' and faint '#555' against tokens of
 *      #565C68 and #3A3F49, so the fallback path drew a DIFFERENT and, as it happens,
 *      more legible picture than the real one.
 *   b. Every tier clears the floor its use demands, in both themes, against --editor.
 *   c. The paint sites are recounted from source. A tier's floor is a claim about how
 *      it is used; if the count moves, the claim has not been re-checked. This is what
 *      stops the next `f.text(..., P.rule)` from quietly putting text on a 3:1 tier.
 */
{
  const studio = fs.readFileSync(path.join(ROOT, 'src', 'studio.js'), 'utf8');
  const circuitSrc = fs.readFileSync(path.join(ROOT, 'src', 'circuit.js'), 'utf8');
  const budget = JSON.parse(fs.readFileSync(BUDGET, 'utf8'));
  const cv = budget.canvas;
  if (!cv) bad('canvas', 'tools/theme_budget.json has no `canvas` block');
  else {
    /* --- a. the palette, and the two fallback tables that shadow it --- */
    const palBody = (studio.match(/function palette\(\)\s*\{([\s\S]*?)\n  \}/) || [])[1] || '';
    const tiers = {};
    for (const m of palBody.matchAll(/(\w+)\s*:\s*v\('(--[\w-]+)'\s*,\s*'([^']+)'\)/g)) {
      tiers[m[1]] = { token: m[2], fallback: m[3] };
    }
    if (!Object.keys(tiers).length) bad('canvas', 'could not read Sandbox.palette() out of src/studio.js');

    const shadowBody = (circuitSrc.match(/Sandbox\.palette\(\)\s*:\s*\{([^}]*)\}/) || [])[1] || '';
    const shadow = {};
    for (const m of shadowBody.matchAll(/(\w+)\s*:\s*'([^']+)'/g)) shadow[m[1]] = m[2];
    if (!Object.keys(shadow).length) bad('canvas', 'could not read circuit.js’s standalone fallback palette');

    const same = (a, b) => {
      const x = parseColor(a, dark), y = parseColor(b, dark);
      return x && y && x.every((v, i) => Math.abs(v - y[i]) < 0.5);
    };
    let drift = 0;
    for (const [name, t] of Object.entries(tiers)) {
      const declared = dark[t.token];
      if (declared === undefined) { bad('canvas', 'palette tier `' + name + '` reads ' + t.token + ', which :root does not define'); continue; }
      if (!same(t.fallback, declared)) {
        bad('canvas', 'palette tier `' + name + '`: the fallback ' + t.fallback + ' is not ' + t.token + ' = ' + declared +
          ' — the no-stylesheet path would draw a different picture'); drift++;
      }
      if (shadow[name] === undefined) {
        bad('canvas', 'circuit.js’s fallback palette has no `' + name + '`, so a canvas drawn without Sandbox paints it undefined'); drift++;
      } else if (!same(shadow[name], declared)) {
        bad('canvas', 'circuit.js’s fallback `' + name + '` is ' + shadow[name] + ', not ' + t.token + ' = ' + declared); drift++;
      }
    }
    for (const name of Object.keys(shadow)) {
      if (tiers[name] === undefined && name !== 'surface') {
        bad('canvas', 'circuit.js’s fallback palette carries `' + name + '`, which Sandbox.palette() does not return');
      }
    }
    if (!drift && clean('canvas')) {
      ok('canvas', Object.keys(tiers).length + ' palette tiers, and both fallback tables agree with the tokens they stand in for');
    }

    /* --- b + c. the floor each tier's own use demands, and the count that claim rests on --- */
    const HAY = studio + '\n' + circuitSrc;
    const lines = HAY.split('\n');
    let worst = Infinity, worstName = '';
    for (const e of cv.tiers) {
      const t = tiers[e.tier];
      if (!t) { bad('canvas', 'the budget names a tier `' + e.tier + '` that Sandbox.palette() does not return'); continue; }
      const floor = e.floor !== undefined ? e.floor : FLOOR[e.kind];
      if (floor === undefined) { bad('canvas', e.tier + ': unknown kind "' + e.kind + '"'); continue; }
      const shown = [];
      for (const [theme, tbl] of [['dark', dark], ['light', light]]) {
        const bg = flatten(e.bg || ['var(--editor)'], tbl);
        const fg = parseColor('var(' + t.token + ')', tbl);
        if (!bg || !fg) { bad('canvas', e.tier + ' [' + theme + ']: a colour did not resolve'); continue; }
        let r = contrast(overlay(fg, bg), bg);
        if (e.alpha !== undefined) r = contrast(overlay(fg.slice(0, 3).concat([e.alpha]), bg), bg);
        shown.push(r);
        if (e.kind !== 'decoration' && r < worst) { worst = r; worstName = e.tier + ' [' + theme + ']'; }
        if (r + 1e-9 < floor) {
          bad('canvas', 'P.' + e.tier + ' [' + theme + '] ' + r.toFixed(2) + ':1 is under the ' + floor +
            ':1 floor for ' + e.kind + ' — ' + e.why);
        }
        if (e.ceiling !== undefined && r > e.ceiling + 1e-9) {
          bad('canvas', 'P.' + e.tier + ' [' + theme + '] ' + r.toFixed(2) + ':1 is over the ' + e.ceiling +
            ':1 ceiling this surface is held to — ' + e.why);
        }
      }
      /* the count the floor's claim rests on */
      const re = new RegExp('\\b(?:P|pal)\\.' + e.tier + '\\b');
      const n = lines.filter(l => re.test(l)).length;
      if (n !== e.sites) {
        bad('canvas', 'P.' + e.tier + ' is painted at ' + n + ' sites, and the budget records ' + e.sites +
          '. A tier’s floor is a claim about how it is used; re-audit the new site, then move the number.');
      }
      if (shown.length === 2) cv._measured = (cv._measured || []).concat([[e.tier, shown[0], shown[1], n]]);
    }

    /* --- d. the decorations, whose alpha is read out of the source --- */
    /* A tier can be raised and a decoration painted through it raised with it, silently:
       the grid on the schematic canvas was `faint` at globalAlpha 0.5, and `faint` going
       from 1.73:1 to 4.60 would have taken the snapping grid from 1.27 to 2.07 — quietly
       making the background the loudest thing behind a circuit. So the alpha comes from
       the source, not from the budget: writing it here would describe the code instead of
       holding it, which is the failure cycle 11 found in this gate's first version. */
    const SRC = { 'studio.js': studio, 'circuit.js': circuitSrc };
    const claimed = new Set();
    for (const d of (cv.decorations || [])) {
      const text = SRC[d.file];
      if (!text) { bad('canvas', d.name + ': no such file "' + d.file + '"'); continue; }
      /* Each entry names the line it is about. The first version of this loop matched from
         the top of the file, so both decorations resolved to whichever paints first: one
         was measured twice and the other never, and putting the grid's alpha back to 0.5
         was ACCEPTED. `anchor` has to occur exactly once, because an anchor that matches
         two places is the same bug wearing a different hat. */
      const at = text.indexOf(d.anchor);
      if (at < 0) { bad('canvas', d.name + ': the anchor ' + JSON.stringify(d.anchor) + ' is not in ' + d.file + ' — the decoration this entry holds down has been moved or rewritten'); continue; }
      if (text.indexOf(d.anchor, at + 1) >= 0) { bad('canvas', d.name + ': the anchor ' + JSON.stringify(d.anchor) + ' occurs more than once in ' + d.file + ', so it does not identify a site'); continue; }
      const re = new RegExp('(?:P|pal)\\.' + d.tier + '\\s*;[\\s\\S]{0,200}?globalAlpha\\s*=\\s*([\\d.]+)');
      const m = text.slice(at).match(re);
      if (!m) { bad('canvas', d.name + ': no `' + d.tier + '` painted through a globalAlpha after its anchor in ' + d.file); continue; }
      /* Two entries resolving to one site is the same defect as one anchor matching two
         places, and the check above cannot see it: each anchor is unique in the file and
         they both still land on whichever paints first. Ask where each one LANDED. */
      const site = d.file + ':' + (at + m.index);
      if (claimed.has(site)) {
        bad('canvas', d.name + ': resolves to the same paint site as an earlier entry (' + site +
          '), so one decoration is measured twice and another is measured never');
        continue;
      }
      claimed.add(site);
      const alpha = parseFloat(m[1]);
      const t = tiers[d.tier];
      if (!t) { bad('canvas', d.name + ': unknown tier `' + d.tier + '`'); continue; }
      for (const [theme, tbl] of [['dark', dark], ['light', light]]) {
        const bg = flatten(['var(--editor)'], tbl);
        const fg = parseColor('var(' + t.token + ')', tbl);
        if (!bg || !fg) { bad('canvas', d.name + ' [' + theme + ']: a colour did not resolve'); continue; }
        const r = contrast(overlay(fg.slice(0, 3).concat([alpha]), bg), bg);
        if (r > d.ceiling + 1e-9) {
          bad('canvas', d.name + ' [' + theme + '] is ' + r.toFixed(2) + ':1 at globalAlpha ' + alpha +
            ', over the ' + d.ceiling + ':1 this surface is held under — ' + d.why);
        }
      }
      cv._decor = (cv._decor || []).concat([[d.tier, alpha]]);
    }

    if (clean('canvas')) {
      const total = (cv._measured || []).reduce((a, r) => a + r[3], 0);
      ok('canvas', total + ' paint sites across ' + (cv._measured || []).length + ' tiers clear their floor in both themes · quietest ' +
        (worst === Infinity ? 'n/a' : worst.toFixed(2) + ':1 (' + worstName + ')') + ' · ' +
        (cv._decor || []).length + ' decorations held under their ceiling at the alpha the source declares');
    }
  }
}

/* ---------- 7. the type ramp, which had no gate and so had no scale ----------
 *
 * Every colour in this application has been held to a token since cycle 5 and to a
 * measured contrast since cycle 11. Nothing has ever measured a SIZE. The result was
 * what an unheld dimension always becomes: 36 distinct type sizes, 285 of the 323
 * declarations below 18px spread across fifteen values in half-pixel steps, and 61
 * rules under 11px. Adjacent ratios of 1.034 mean the hierarchy those values were
 * chosen to express does not survive being drawn.
 *
 *   a. The ramp is a scale — whole pixels, strictly increasing, no step so small that
 *      it cannot be seen, and a floor under the smallest.
 *   b. Nothing below the display band declares a literal. This is the check that stops
 *      a sixteenth value being added the way the first fifteen were.
 *   c. The display band is enumerated. It is deliberately NOT collapsed — those sizes
 *      are per-component headings and three of them are emoji boxes rather than text —
 *      so it is held by being listed, and a new one has to be written down.
 *   d. Relative sizes are resolved against the parent they inherit from. `.88em` is
 *      fine on a 14px parent and 10.56px on a 12px one, and no check on the DECLARED
 *      size can see the difference.
 *   e. The canvas draws text the DOM never sees, at sizes the DOM does not use, on a
 *      surface where a browser's text zoom does nothing at all.
 */
{
  const budget = JSON.parse(fs.readFileSync(BUDGET, 'utf8'));
  const T = budget.type;
  if (!T) bad('type', 'tools/theme_budget.json has no `type` block');
  else {
    /* --- a. the ramp is a scale --- */
    const ramp = T.ramp.map(name => ({ name, px: typePx(dark[name]) }));
    const missing = ramp.filter(s => !Number.isFinite(s.px));
    if (missing.length) bad('type', 'the budget names ' + missing.map(s => s.name).join(', ') + ', which :root does not define as a length');
    else {
      for (const s of ramp) {
        if (s.px !== Math.round(s.px)) bad('type', s.name + ' is ' + s.px + 'px — a half pixel is not a step, it is the defect this ramp replaced');
        if (s.px < T.floor) bad('type', s.name + ' is ' + s.px + 'px, under the ' + T.floor + 'px floor');
      }
      for (let i = 1; i < ramp.length; i++) {
        const r = ramp[i].px / ramp[i - 1].px;
        if (ramp[i].px <= ramp[i - 1].px) {
          bad('type', ramp[i].name + ' (' + ramp[i].px + 'px) is not above ' + ramp[i - 1].name + ' (' + ramp[i - 1].px + 'px) — the ramp has to ascend to be one');
        } else if (r < T.minRatio - 1e-9) {
          bad('type', ramp[i - 1].name + ' -> ' + ramp[i].name + ' is a ratio of ' + r.toFixed(3) +
            ', under the ' + T.minRatio + ' this ramp holds. Two steps a reader cannot tell apart are one step wearing two names.');
        }
      }
    }

    /* --- b. nothing under the display band is a literal --- */
    const literals = [];
    for (const r of rules) {
      for (const m of r.body.matchAll(/font-size\s*:\s*([\d.]+)px/g)) {
        const v = parseFloat(m[1]);
        if (v < T.displayFloor) literals.push({ sel: r.sel, px: v });
      }
    }
    for (const l of literals) {
      bad('type', l.sel + ' declares font-size:' + l.px + 'px directly. Sizes under ' + T.displayFloor +
        'px come from the --t-* ramp; a literal here is how the ramp stops being one.');
    }

    /* --- c. the display band, enumerated rather than collapsed --- */
    const seen = new Map();
    for (const r of rules) {
      for (const m of r.body.matchAll(/font-size\s*:\s*([\d.]+)px/g)) {
        const v = parseFloat(m[1]);
        if (v >= T.displayFloor) seen.set(v, (seen.get(v) || []).concat([r.sel]));
      }
    }
    const listed = new Set(T.display.map(d => d.px));
    for (const [v, sels] of [...seen].sort((a, b) => a[0] - b[0])) {
      if (!listed.has(v)) {
        bad('type', 'font-size:' + v + 'px is used by ' + sels.join(', ') + ' and is not in the budget\'s display band. ' +
          'Either it belongs on the ramp, or it is a display size and needs a line saying which component it is for.');
      }
    }
    for (const d of T.display) {
      if (!seen.has(d.px)) bad('type', 'the budget lists ' + d.px + 'px in the display band and nothing uses it — a list that outlives its entries stops being a record of anything');
    }

    /* --- d. relative sizes, resolved against the parent they inherit from --- */
    /* Declared-size checks are blind here by construction: `.88em` is a legal, sensible
       declaration whose rendered size is a fact about some OTHER rule. Each entry names
       the parent it inherits from, and the parent's size is read from the stylesheet, so
       dropping a parent onto a smaller step is what trips this rather than editing the
       child. */
    let smallestRel = Infinity, smallestRelName = '';
    for (const e of (T.relative || [])) {
      const parentRule = rules.filter(r => r.sel.split(',').map(s => s.trim()).indexOf(e.parent) >= 0 && /font-size/.test(r.body)).pop();
      if (!parentRule) { bad('type', e.sel + ': its parent ' + e.parent + ' declares no font-size, so this size cannot be resolved'); continue; }
      const parentPx = typePx((parentRule.body.match(/font-size\s*:\s*([^;}]+)/) || [])[1]);
      if (!Number.isFinite(parentPx)) { bad('type', e.sel + ': ' + e.parent + '\'s font-size did not resolve'); continue; }
      const computed = parentPx * e.em;
      if (computed < smallestRel) { smallestRel = computed; smallestRelName = e.sel; }
      if (computed + 1e-9 < T.floor) {
        bad('type', e.sel + ' is ' + e.em + 'em of ' + e.parent + ' (' + parentPx + 'px) = ' + computed.toFixed(2) +
          'px, under the ' + T.floor + 'px floor — ' + e.why);
      }
    }

    /* --- e. the canvas, which is type no stylesheet holds and no text zoom reaches --- */
    const canvasSizes = [];
    for (const file of ['studio.js', 'circuit.js']) {
      const text = fs.readFileSync(path.join(ROOT, 'src', file), 'utf8');
      for (const m of text.matchAll(/font\s*=\s*['"`](?:bold\s+)?([\d.]+)px/g)) canvasSizes.push({ file, px: parseFloat(m[1]) });
    }
    const cfloor = T.canvas.floor;
    for (const c of canvasSizes) {
      if (c.px + 1e-9 < cfloor) {
        bad('type', 'src/' + c.file + ' draws canvas text at ' + c.px + 'px, under the ' + cfloor +
          'px this surface is held to. Canvas text is not text: a browser\'s text zoom does not reach it.');
      }
    }
    const under = canvasSizes.filter(c => c.px < T.floor).length;
    if (under > T.canvas.underFloor) {
      bad('type', under + ' canvas draw sites are under the DOM\'s ' + T.floor + 'px floor and the budget records ' +
        T.canvas.underFloor + '. This number is a debt, so it may shrink and be written down — it may not grow.');
    }

    /* --- f. tracking, which is the same dimension one layer in --- */
    /* All 36 positive letter-spacing declarations sit on --t-label doing one job, and
       they carried twelve values — .1em and .10em among them, the same number written
       twice. A size ramp that does not hold its tracking is half a scale: the tier is
       one decision and it had twelve answers. The negative ramp is NOT held, on the same
       argument as the display band — it descends correctly with size and each value
       belongs to a heading this cycle deliberately did not collapse — but its two
       duplicate spellings were normalised so the set is countable. */
    const trackLits = [];
    let tracked = 0;
    for (const r of rules) {
      for (const m of r.body.matchAll(/letter-spacing\s*:\s*([^;}]+)/g)) {
        const v = m[1].trim();
        if (/^var\(--tr-/.test(v)) { tracked++; continue; }
        if (/^-/.test(v) || v === '0') continue;          /* the display ramp, and no tracking at all */
        trackLits.push({ sel: r.sel, v });
      }
    }
    for (const l of trackLits) {
      bad('type', l.sel + ' tracks by ' + l.v + ' directly. Positive tracking on the label tier comes ' +
        'from --tr-caps or --tr-mono; twelve hand-picked values is what this replaced.');
    }
    for (const name of (T.tracking || [])) {
      if (dark[name] === undefined) bad('type', 'the budget names ' + name + ', which :root does not define');
    }
    const negSpellings = new Set();
    for (const r of rules) {
      for (const m of r.body.matchAll(/letter-spacing\s*:\s*(-[\d.]+em)/g)) negSpellings.add(m[1]);
    }
    const dupes = [...negSpellings].filter(s => negSpellings.has(s.replace(/^-\./, '-0.')) && /^-\./.test(s));
    for (const d of dupes) bad('type', 'the display ramp writes ' + d + ' and ' + d.replace(/^-\./, '-0.') + ' for one value');

    if (clean('type')) {
      const smallestCanvas = canvasSizes.reduce((a, c) => Math.min(a, c.px), Infinity);
      ok('type', ramp.length + ' steps from ' + ramp[0].px + 'px to ' + ramp[ramp.length - 1].px +
        'px hold every one of ' + (rules.reduce((n, r) => n + (r.body.match(/font-size\s*:\s*var\(--t-/g) || []).length, 0)) +
        ' sized declarations · tightest step ' +
        Math.min(...ramp.slice(1).map((s, i) => s.px / ramp[i].px)).toFixed(3) +
        ' · ' + seen.size + ' display sizes enumerated · smallest relative ' + smallestRel.toFixed(2) +
        'px (' + smallestRelName + ')');
      ok('type', canvasSizes.length + ' canvas draw sites across 2 files, smallest ' + smallestCanvas +
        'px, ' + under + ' under the DOM floor — recorded as a debt and held from growing');
      ok('type', tracked + ' positive tracking declarations come from ' + (T.tracking || []).length +
        ' tokens, and the display ramp\'s ' + negSpellings.size + ' negative values are each written one way');
    }
  }
}

console.log('');
if (fails) { console.log('FAILED: ' + fails + ' problem(s).'); process.exit(1); }
console.log('All good: theme tokens, ' + JSON.parse(fs.readFileSync(BUDGET, 'utf8')).surfaces.length +
  ' contrast surfaces in both themes, the type ramp every size comes from, ' +
  'the canvas palette every drawing shares, the 375px topbar and the mobile drawer.');
