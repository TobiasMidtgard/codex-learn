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
 *   3. The topbar fits a 375px phone. Its furniture is fixed-width and its knobs are
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
  const flame = px(declIn('.metric.streak .fl', 'font-size') || '13px') * EMOJI_ADVANCE;
  const digit = px(declIn('.metric.streak b', 'font-size') || '12px') * MONO_ADVANCE;
  const xpHidden = /^none$/.test(declIn('.metric.xp', 'display', phone) || '');

  /* worst case a learner can actually reach: a 365-day streak, a six-character XP */
  const streakBox = 2 * mpad + flame + mgap + 3 * digit;
  const xpBox = xpHidden ? 0 : 2 * mpad + 6 * digit;
  const items = 6 + (xpHidden ? 0 : 1);   /* menu, screen-id, spacer, streak, 2 tbtn */
  const furniture = (items - 1) * gap + menu + 2 * btn + streakBox + xpBox;
  const avail = VIEWPORT - railIcon - 2 * pad;
  const left = avail - furniture;
  const line = 'at ' + VIEWPORT + 'px: ' + avail.toFixed(0) + 'px of bar, ' + furniture.toFixed(1) +
    'px of furniture, ' + left.toFixed(1) + 'px for the screen title' + (xpHidden ? ' (XP pill stands down)' : '');
  if (left < TITLE_FLOOR) bad('topbar', line + ' — under the ' + TITLE_FLOOR + 'px floor');
  else ok('topbar', line);

  /* a control that can shrink is a control that can shrink past a finger */
  let held = true;
  for (const sel of ['.tbtn', '.menu-btn', '.metric']) {
    const f = declIn(sel, 'flex');
    if (!f || !/^none\b/.test(f)) { held = false; bad('topbar', sel + ' is not flex:none, so it shrinks below its own box under pressure'); }
  }
  if (held) ok('topbar', '.tbtn, .menu-btn and .metric hold their box (WCAG 2.5.8 target size)');
}

/* ---------- 4. the rail's id column holds the ids the catalogue actually has ---------- */
/* The track was 32px wide against a 9px right pad. Fifteen of the sixty-two ids are
   seven characters, which does not fit in 23px of any font, so text-align:right spilled
   them leftwards out of the row. A column sized against the data cannot drift back. */
{
  const MONO_ADVANCE = 0.6;
  let ids = [];
  for (const f of fs.readdirSync(path.join(ROOT, 'catalog'))) {
    if (!/^_spine.*\.json$/.test(f)) continue;
    const d = JSON.parse(fs.readFileSync(path.join(ROOT, 'catalog', f), 'utf8'));
    for (const c of (d.courses || [])) ids.push(c.id);
  }
  const longest = ids.reduce((a, b) => (b.length > a.length ? b : a), '');
  const rule = rules.find(r => r.sel === '.rail-course' && !r.media.length && /grid-template-columns/.test(r.body));
  const cidRule = rules.find(r => r.sel.indexOf('.rail-course .cid') >= 0 && /font-size/.test(r.body));
  const track = rule && parseFloat(rule.body.match(/grid-template-columns\s*:\s*([\d.]+)px/)[1]);
  const size = cidRule && parseFloat(cidRule.body.match(/font-size\s*:\s*([\d.]+)px/)[1]);
  const padR = cidRule && parseFloat((cidRule.body.match(/padding-right\s*:\s*([\d.]+)px/) || [0, 0])[1]);
  const need = longest.length * size * MONO_ADVANCE + padR;
  if (!track || !size) bad('railid', 'could not read the id column or its type size');
  else if (need > track + 1e-9) {
    bad('railid', 'the id column is ' + track + 'px and "' + longest + '" needs ' + need.toFixed(1) +
      'px (' + longest.length + ' glyphs at ' + size + 'px JetBrains Mono, plus ' + padR + 'px of pad)');
  } else {
    ok('railid', 'the ' + track + 'px id column holds "' + longest + '", the longest of ' + ids.length +
      ' course ids, at ' + need.toFixed(1) + 'px');
  }
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

console.log('');
if (fails) { console.log('FAILED: ' + fails + ' problem(s).'); process.exit(1); }
console.log('All good: theme tokens, ' + JSON.parse(fs.readFileSync(BUDGET, 'utf8')).surfaces.length +
  ' contrast surfaces in both themes, the 375px topbar and the mobile drawer.');
