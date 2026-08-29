/**
 * build.mjs — assemble the single-file Codewright app.
 *
 *   node build.mjs            -> build/codewright.html
 *   node build.mjs --check    -> validate only, write nothing
 *
 * Inputs
 *   src/index.head.html   doctype, styles, theme bootstrap, <body> openers
 *   src/lang.js           language model, inference, completion, highlighting
 *   src/studio.js         maths rendering, symbolic checking, sandboxes
 *   src/bundle.*.txt      the "@@ key" content bundle for the foundation tracks
 *   src/tracks.js         the TRACKS array
 *   src/engine.js         utilities, highlighter, markdown, editor, runners, store
 *   src/app.js            state, routing, every view
 *   catalog/_spine.json   the degree programme table
 *   catalog/<ID>.json     one emitted course per file
 */

import { readFileSync, writeFileSync, readdirSync, mkdirSync, existsSync, rmSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';

const ROOT = dirname(fileURLToPath(import.meta.url));
const SRC = join(ROOT, 'src');
const CATALOG = join(ROOT, 'catalog');
const OUT_DIR = join(ROOT, 'build');
const OUT = join(OUT_DIR, 'codewright.html');
/* GitHub Pages serves ./docs straight from the default branch, so the published
   copy is written by the same build rather than kept in step by hand. */
const DOCS_DIR = join(ROOT, 'docs');
const DOCS_OUT = join(DOCS_DIR, 'index.html');

const checkOnly = process.argv.includes('--check');
const problems = [];
const notes = [];

const read = (p) => readFileSync(p, 'utf8');

/* ---------------------------------------------------------------- bundle */
const bundleParts = readdirSync(SRC)
  .filter((f) => /^bundle\.\d+\.txt$/.test(f))
  .sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]));
if (!bundleParts.length) problems.push('no src/bundle.N.txt files found');
const bundleText = bundleParts.map((f) => read(join(SRC, f))).join('\n\n');

/* A raw </script would close the host <script type="text/plain"> tag early.
   The bundle deliberately writes them as <\/script ; parseBundle unescapes. */
if (/<\/script/i.test(bundleText)) {
  problems.push('bundle contains a raw </script — it must be written as <\\/script');
}
const bundleKeys = [...bundleText.matchAll(/^@@[ \t]+(\S+)[ \t]*$/gm)].map((m) => m[1]);
notes.push(`bundle: ${bundleParts.length} parts, ${bundleKeys.length} keys`);

/* ---------------------------------------------------------------- degree */
/* Every catalog/_spine*.json describes one programme. A course is placed by
   (program, band) — `band` is the neutral name for what CS calls a year and the EE
   M.S. calls a track, so a track never has to be labelled "Year 1". Spines written
   before this used `year`; that is still accepted and copied into `band`. */
const spineFiles = readdirSync(CATALOG)
  .filter((f) => /^_spine.*\.json$/.test(f))
  /* the base _spine.json is the founding programme and leads the list */
  .sort((a, b) => (a === '_spine.json' ? -1 : b === '_spine.json' ? 1 : a.localeCompare(b)));

const programs = [];
const allCourses = [];
const seenId = new Map();          /* id -> programme, for the collision guard */

for (const file of spineFiles) {
  const spine = JSON.parse(read(join(CATALOG, file)));
  const prog = spine.program;
  if (!prog || !prog.id) { problems.push(`${file}: no program.id`); continue; }

  /* accept the legacy `years` key, and default the noun for programmes that predate it */
  prog.bands = prog.bands || prog.years || [];
  prog.bandNoun = prog.bandNoun || 'Year';
  delete prog.years;

  const order = spine.courses.map((c) => c.id);
  const byId = new Map(spine.courses.map((c) => [c.id, c]));
  const missing = [];
  let bundled = 0;

  for (const id of order) {
    /* The lesson keyspace is flat and shared with the foundation track ids, so a
       duplicate here would silently overwrite a course rather than fail. */
    if (seenId.has(id)) {
      problems.push(`duplicate course id "${id}" in ${file} — already used by ${seenId.get(id)}`);
      continue;
    }
    seenId.set(id, prog.id);

    const cp = join(CATALOG, id + '.json');
    if (!existsSync(cp)) { missing.push(id); continue; }
    const course = JSON.parse(read(cp));

    /* the spine is the single source of truth for placement metadata */
    const s = byId.get(id);
    s.band = s.band !== undefined ? s.band : s.year;
    for (const key of ['title', 'level', 'credits', 'hours']) {
      if (String(course[key]) !== String(s[key])) {
        notes.push(`${id}: ${key} "${course[key]}" != spine "${s[key]}" — using the spine`);
        course[key] = s[key];
      }
    }
    course.band = s.band;
    course.program = prog.id;
    course.prereqs = s.prereqs;
    course.stack = course.stack && course.stack.length ? course.stack : s.stack;
    course.icon = course.icon || s.icon;
    delete course.year;

    const labs = course.modules.filter((m) => m.lab).length;
    if (!labs) problems.push(`${id}: no labs`);
    allCourses.push(course);
    bundled++;
  }

  if (missing.length) {
    notes.push(`${prog.id}: ${missing.length} course(s) not yet authored -> ${missing.join(', ')}`);
  }
  programs.push(prog);
  notes.push(`${prog.id}: ${bundled}/${order.length} courses bundled`);
}

const degree = { programs, courses: allCourses };
if (!programs.length) notes.push('catalog: no _spine*.json — building without any programme');

/* `</script>` inside any JSON string would terminate the host <script>.
   Escaping every `<` as < keeps the JSON valid JS and inert to the parser. */
const degreeJson = JSON.stringify(degree).replace(/</g, '\\u003c');

/* ---------------------------------------------------------------- scripts */
const langJs = read(join(SRC, 'lang.js'));
const tracksJs = read(join(SRC, 'tracks.js'));
const engineJs = read(join(SRC, 'engine.js'));
const studioJs = read(join(SRC, 'studio.js'));
const appJs = read(join(SRC, 'app.js'));

const appScript = [
  langJs,
  tracksJs,
  '\n/* ============ degree catalog (generated by build.mjs) ============ */\n',
  'const DEGREE_DATA = ' + degreeJson + ';\n',
  engineJs,
  studioJs,
  appJs,
].join('\n');

/* The host page carries this script inline, so the HTML tokenizer sees it before
   the JS parser does. A literal `<!--` switches it into "script data escaped" state
   and a following literal `<script` into "double escaped", where `</script>` stops
   closing the tag — the script then swallows the rest of the document and nothing
   runs. Both parse fine as JavaScript, so `node --check` cannot see it. Spell the
   sequences out (`\x3c`, `'<\/scr' + 'ipt>'`) as the rest of the file does. */
for (const [seq, why] of [
  ['<' + '!--', 'starts an HTML comment inside the script — write it as <!\\x2d-'],
  ['<' + 'script', 'flips the tokenizer to double-escaped — write the tag name bare'],
  ['</' + 'script', 'closes the host tag early — write it as <\\/scr\' + \'ipt>'],
]) {
  if (appScript.includes(seq)) {
    const at = appScript.indexOf(seq);
    const line = appScript.slice(0, at).split('\n').length;
    problems.push(`assembled script contains a literal "${seq}" (line ~${line}) — it ${why}`);
  }
}

/* Syntax-check the assembled script before shipping it. */
if (!checkOnly || true) {
  const tmp = join(OUT_DIR, '.syntax-check.js');
  mkdirSync(OUT_DIR, { recursive: true });
  writeFileSync(tmp, appScript, 'utf8');
  try {
    execFileSync(process.execPath, ['--check', tmp], { stdio: 'pipe' });
    notes.push('syntax: assembled script parses cleanly');
  } catch (e) {
    problems.push('JavaScript syntax error in the assembled script:\n' +
      String(e.stderr || e.stdout || e.message).split('\n').slice(0, 12).join('\n'));
  } finally {
    try { rmSync(tmp, { force: true }); } catch {}
  }
}

/* ---------------------------------------------------------------- emit */
const head = read(join(SRC, 'index.head.html'));
const html = [
  head,
  '',
  '<script type="text/plain" id="bundle">',
  bundleText,
  '</' + 'script>',
  '',
  '<script>',
  appScript,
  '</' + 'script>',
  '</body>',
  '</html>',
  '',
].join('\n');

console.log('--- build report ---');
for (const n of notes) console.log('  ·', n);
if (problems.length) {
  console.log('\nPROBLEMS:');
  for (const p of problems) console.log('  !', p);
}

if (problems.length) {
  console.log('\nbuild aborted');
  process.exit(1);
}

/* The inlined artifact is the one you can open from disk; past this it stops being
   a reasonable thing to double-click, and the programme payloads should be split. */
const SIZE_BUDGET_KB = 6144;
const sizeKb = Buffer.byteLength(html, 'utf8') / 1024;
if (sizeKb > SIZE_BUDGET_KB) {
  problems.push(`built file is ${Math.round(sizeKb)} KB, over the ${SIZE_BUDGET_KB} KB budget — ` +
    'split the programme payloads instead of growing the single file');
}
if (problems.length) {
  console.log('\nPROBLEMS:');
  for (const pr of problems) console.log('  !', pr);
  console.log('\nbuild aborted');
  process.exit(1);
}

if (checkOnly) {
  console.log('\ncheck passed (nothing written)');
  process.exit(0);
}

mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(OUT, html, 'utf8');
mkdirSync(DOCS_DIR, { recursive: true });
writeFileSync(DOCS_OUT, html, 'utf8');
writeFileSync(join(DOCS_DIR, '.nojekyll'), '', 'utf8');
const kb = (Buffer.byteLength(html, 'utf8') / 1024).toFixed(0);
console.log(`\nwrote ${OUT}  (${kb} KB)`);
console.log(`wrote ${DOCS_OUT}  (this is what GitHub Pages serves)`);
