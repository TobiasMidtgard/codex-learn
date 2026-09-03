/**
 * verify_minify.mjs — the comment stripper changes nothing but comments.
 *
 * tools/minify.mjs decides what is a comment with a hand-written tokenizer, and a
 * tokenizer that mistakes a `/*` inside a regular expression for a comment would
 * ship a script that parses — or does not — with different meaning. So for every
 * script that ships, and for the stylesheet:
 *
 *   1. the token stream of the stripped output, comments removed and whitespace
 *      normalised, must equal that of the source;
 *   2. the stripped script must still pass `node --check`;
 *   3. the stripped application must still stand up through tools/app_stage.mjs and
 *      index the catalog exactly as the source does — a semantic check that does not
 *      depend on the tokenizer that is under test;
 *   4. a set of deliberately awkward inputs — a regex holding `/*`, a string holding
 *      `//`, a template literal with a nested template and a comment inside `${}`,
 *      a division after a parenthesis — must come through with their tokens intact.
 */

import { readFileSync, writeFileSync, rmSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { stripJs, stripCss, significantJs, significantCss, tokenizeJs } from './minify.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'src');
const TMP = join(ROOT, 'build');
const problems = [];
const say = (s) => console.log(s);

/* ---- 4. the awkward inputs, first, because they are the cheapest to reason about ---- */
const AWKWARD = [
  ['regex holding a comment opener', 'const re = /\\/\\*not a comment\\*\\//g; x(re);'],
  ['string holding a line comment', "const s = 'http://example.com'; // real comment\nuse(s);"],
  ['division after a parenthesis', 'const a = (b + c) / 2 /* half */; const d = e / f / g;'],
  ['template with nested template and inner comment', 'const t = `a ${ `b ${ /* c */ d } e` } /* not a comment */ f`;'],
  ['regex after return', 'function f(s) { return /\\d+\\/\\d+/.test(s); }'],
  ['regex with a class holding a slash', 'const r = /[/]+/; const q = a / b;'],
  ['line comment holding a string quote', "x = 1; // it's here\ny = 2;"],
  ['block comment on its own line between tokens', 'a = 1\n/* gap */\n+ 2;'],
  ['regex after a keyword and a brace', 'if (x) { /re/.test(y); } else /s/.test(z);'],
  ['single-quoted string with an escaped quote and a slash', "const p = 'it\\'s /* fine */';"],
];
for (const [name, src] of AWKWARD) {
  const out = stripJs(src);
  if (significantJs(out) !== significantJs(src)) problems.push(`awkward: ${name} — token stream changed`);
  if (out.includes('not a comment') !== src.includes('not a comment')) problems.push(`awkward: ${name} — stripped inside a literal`);
  if (name.startsWith('block comment on its own') && !/1\n\+ 2/.test(out)) problems.push(`awkward: ${name} — the newline was lost (ASI)`);
  if (name.startsWith('line comment') && out.includes('//')) problems.push(`awkward: ${name} — comment survived`);
}
const tk = tokenizeJs("const re = /\\/\\*x\\*\\//g;");
if (!tk.some((k) => k.t === 're')) problems.push('awkward: the regex holding a comment opener was not read as a regex');
say(`awkward  ${AWKWARD.length} inputs`);

/* ---- 1 + 2. every script that ships ---- */
const scripts = ['lang.js', 'engine.js', 'studio.js', 'mathinput.js', 'mcu.js', 'circuit.js', 'desk.js', 'app.js'];
let before = 0, after = 0;
mkdirSync(TMP, { recursive: true });
for (const f of scripts) {
  const src = readFileSync(join(SRC, f), 'utf8');
  const out = stripJs(src);
  before += Buffer.byteLength(src); after += Buffer.byteLength(out);
  if (significantJs(out) !== significantJs(src)) problems.push(`${f}: token stream differs after stripping`);
  if (/\/\*[\s\S]*?\*\//.test(out.replace(/(['"`])(?:\\.|(?!\1)[^\\])*\1/g, ''))) {
    /* a block comment left outside any string: the tokenizer missed one */
    const m = out.replace(/(['"`])(?:\\.|(?!\1)[^\\])*\1/g, '').match(/\/\*[\s\S]{0,60}/);
    problems.push(`${f}: a block comment survived: ${JSON.stringify(m && m[0])}`);
  }
  const tmp = join(TMP, `.minify-check.${f}`);
  writeFileSync(tmp, out, 'utf8');
  try { execFileSync(process.execPath, ['--check', tmp], { stdio: 'pipe' }); }
  catch (e) { problems.push(`${f}: stripped output fails node --check: ${String(e.stderr).split('\n').slice(0, 3).join(' ')}`); }
  finally { try { rmSync(tmp, { force: true }); } catch {} }
}
say(`scripts  ${scripts.length} files, ${Math.round(before / 1024)} KB -> ${Math.round(after / 1024)} KB ` +
  `(${Math.round((1 - after / before) * 100)}% smaller), every token stream equal, every file parses`);

/* ---- the stylesheet ---- */
{
  const head = readFileSync(join(SRC, 'index.head.html'), 'utf8');
  const m = head.match(/<style>([\s\S]*?)<\/style>/);
  if (!m) problems.push('index.head.html: no <style> block found');
  else {
    const css = m[1], out = stripCss(css);
    if (significantCss(out) !== significantCss(css)) problems.push('stylesheet: content differs after stripping');
    if (/\/\*/.test(out)) problems.push('stylesheet: a comment survived');
    /* the declarations must survive: counted on the source with its comments taken
       out by a plain regex, which is a second, independent reading of the file */
    const decls = (s) => (s.replace(/\/\*[\s\S]*?\*\//g, '').match(/[a-z-]+\s*:\s*[^;{}]+;/g) || []).length;
    if (decls(out) !== decls(css)) problems.push(`stylesheet: ${decls(css)} declarations before, ${decls(out)} after`);
    say(`styles   ${Math.round(css.length / 1024)} KB -> ${Math.round(out.length / 1024)} KB, ${decls(css)} declarations kept`);
  }
}

/* ---- 3. the stripped application stands up ---- */
{
  const { loadApp } = await import('./app_stage.mjs');
  const { readdirSync } = await import('node:fs');
  const catalog = join(ROOT, 'catalog');
  const spine = JSON.parse(readFileSync(join(catalog, '_spine.json'), 'utf8'));
  const prog = spine.program; prog.bands = prog.bands || prog.years || []; prog.bandNoun = 'Year';
  const courses = [];
  for (const s of spine.courses.slice(0, 6)) {
    try { const c = JSON.parse(readFileSync(join(catalog, s.id + '.json'), 'utf8')); c.band = s.year; c.program = prog.id; c.prereqs = s.prereqs; courses.push(c); } catch {}
  }
  void readdirSync;
  const stage = (transform) => {
    globalThis.DEGREE_DATA = { programs: [prog], courses: JSON.parse(JSON.stringify(courses)) };
    globalThis.DEGREE_CHUNKS = null;
    return loadApp({ exports: { LESSON_INDEX: 'LESSON_INDEX', renderMd: 'renderMd' }, transform }).app;
  };
  const plain = stage(null);
  const stripped = stage(stripJs);
  const a = Object.keys(plain.LESSON_INDEX).sort().join(','), b = Object.keys(stripped.LESSON_INDEX).sort().join(',');
  if (a !== b) problems.push('the stripped app indexes a different lesson set');
  const md = '# T\n\nSome *prose* with `code` and $x^2$.\n\n```python\nprint(1) # c\n```\n';
  if (plain.renderMd(md) !== stripped.renderMd(md)) problems.push('the stripped app renders markdown differently');
  say(`app      the stripped application indexes ${Object.keys(stripped.LESSON_INDEX).length} lessons, same as the source`);
}

if (problems.length) {
  console.log(`\n${problems.length} problem(s):`);
  for (const p of problems) console.log('  -', p);
  process.exit(1);
}
console.log(`\nAll good: comments and indentation come out, nothing else does — ` +
  `${Math.round(before / 1024)} KB of script ships as ${Math.round(after / 1024)} KB.`);
