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
 *   src/circuit.js        schematic editor and the MNA circuit solver
 *   src/engine.js         utilities, highlighter, markdown, editor, runners, store
 *   src/app.js            state, routing, every view
 *   catalog/_spine.json   the degree programme table
 *   catalog/<ID>.json     one emitted course per file
 *
 * Outputs, two shapes from one pass over the catalog
 *   build/codewright.html            everything inlined; the file you can double-click
 *   build/index.html                 the shell, plus
 *   build/programs/<id>.<hash>.json  one fetched payload per programme
 *   docs/*                           a copy of the split shape; Pages serves this
 *
 * The split exists because the degree payload is 88% of the bytes. Inlined, none of
 * the page runs until all of it has parsed; split, the shell is an eighth of the size
 * and the payloads arrive as JSON, which parses far faster than the same bytes as a
 * JavaScript object literal.
 */

import { readFileSync, writeFileSync, readdirSync, mkdirSync, existsSync, rmSync,
         statSync, unlinkSync } from 'node:fs';
import { createHash } from 'node:crypto';

/* A unit key holds nothing, one authored object, or a list of them. */
const asList = (x) => (!x ? [] : (Array.isArray(x) ? x : [x]));

import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { execFileSync } from 'node:child_process';
import { skeletonOf } from './tools/skeleton.mjs';
import { stripJs, stripCss } from './tools/minify.mjs';

const ROOT = dirname(fileURLToPath(import.meta.url));
const SRC = join(ROOT, 'src');
const CATALOG = join(ROOT, 'catalog');
const OUT_DIR = join(ROOT, 'build');
/* GitHub Pages serves ./docs straight from the default branch, so the published
   copy is written by the same build rather than kept in step by hand. */
const DOCS_DIR = join(ROOT, 'docs');

const checkOnly = process.argv.includes('--check');
/* --preview writes build/ only and lets an un-emitted author file through with a
   note instead of a refusal: it is for looking at the app while a course is being
   written, and it never touches docs/, which is what gets published. */
const previewOnly = process.argv.includes('--preview');
const problems = [];
const notes = [];

const read = (p) => readFileSync(p, 'utf8');

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
/* A course is authored in catalog/authors/<ID>.py and EMITTED to catalog/<ID>.json,
   and it is the emitted file that ships. So a fix made at source and never re-emitted
   is a fix that does not reach anybody — the defect stays in the artifact, invisible,
   because the source reads correctly. That happened: three defects were corrected in
   EE131.py, never re-emitted, and were still being served weeks later; an auditor
   reading the built catalog reported them as live, which is how it surfaced at all.

   Mtimes are a coarse test and will occasionally cry wolf after a checkout. That is
   the right way round for this: the cost of a false alarm is one `emit.py` run, and
   the cost of a miss is shipping content that was already known to be wrong. */
const staleAuthored = [];
for (const f of readdirSync(join(CATALOG, 'authors'))) {
  if (!f.endsWith('.py') || f.startsWith('_')) continue;
  const id = f.slice(0, -3);
  const src = join(CATALOG, 'authors', f);
  const out = join(CATALOG, `${id}.json`);
  if (!existsSync(out)) { staleAuthored.push(`${id} has never been emitted`); continue; }
  if (statSync(src).mtimeMs > statSync(out).mtimeMs + 1000) {
    staleAuthored.push(`${id}.py is newer than ${id}.json`);
  }
}
if (staleAuthored.length) {
  (previewOnly ? notes : problems).push(`${staleAuthored.length} course(s) edited at source but not re-emitted, so the ` +
    `build would ship the older text: ${staleAuthored.join(', ')}. Run ` +
    `\`python -X utf8 tools/emit.py --all\`.`);
}

const allCourses = [];
/* the same courses, grouped for the split shape — filled in the one pass below, so
   the cross-spine duplicate guard below still sees every id exactly once */
const byProgram = {};
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
    /* The lesson keyspace is flat and shared across every programme, so a duplicate
       here would silently overwrite a course rather than fail. */
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

    /* A build exercise's reference schematic is the answer key. It exists so
       verify_circuits.mjs can prove the checks are satisfiable, and that gate reads
       catalog/*.json directly — so shipping it to the browser buys nothing and costs
       twice: it is readable from the console, and 36 schematics are real bytes in a
       file already close to its size budget. */
    for (const m of course.modules) {
      for (const b of asList(m.build)) delete b.solution;
    }

    const labs = course.modules.reduce((n, m) => n + asList(m.lab).length, 0);
    if (!labs) problems.push(`${id}: no labs`);
    allCourses.push(course);
    (byProgram[prog.id] = byProgram[prog.id] || []).push(course);
    bundled++;
  }

  if (missing.length) {
    notes.push(`${prog.id}: ${missing.length} course(s) not yet authored -> ${missing.join(', ')}`);
  }
  programs.push(prog);
  notes.push(`${prog.id}: ${bundled}/${order.length} courses bundled`);
}

/* A sandbox unit names a visualiser and the parameters it opens with. Neither is
   checked by emit.py or verify_labs — a wrong id renders a "visualiser missing" card,
   and a wrong parameter key is silently ignored, so the learner sees a sandbox that
   opens somewhere other than the brief describes. Both are only visible here, where
   the catalog and the visualiser registry are in the same place. */
const studioJs = read(join(SRC, 'studio.js'));
const circuitJs = read(join(SRC, 'circuit.js'));
const VIS = new Map();
for (const block of studioJs.split('Sandbox.define({').slice(1)) {
  const id = (block.match(/id:\s*'([^']+)'/) || [])[1];
  if (!id) continue;
  const params = block.slice(0, block.indexOf('draw:'));
  VIS.set(id, new Set([...params.matchAll(/\{\s*k:\s*'([^']+)'/g)].map((m) => m[1])));
}
for (const c of allCourses) {
  for (const [mi, m] of c.modules.entries()) {
    for (const sb of asList(m.sandbox)) {
    const id = sb.visualiser;
    if (!VIS.has(id)) {
      problems.push(`${c.id}/M${mi + 1}: sandbox names "${id}", which is not a registered ` +
        `visualiser (have: ${[...VIS.keys()].join(', ')})`);
      continue;
    }
    for (const k of Object.keys(sb.initial || {})) {
      if (!VIS.get(id).has(k)) {
        problems.push(`${c.id}/M${mi + 1}: sandbox sets "${k}", which is not a parameter of ` +
          `"${id}" (it takes: ${[...VIS.get(id)].join(', ')})`);
      }
    }
    }
  }
}
notes.push(`visualisers: ${VIS.size} registered, every sandbox reference checked`);

/* The same argument as the sandbox check above, for the two other places a unit names
   something the code has to supply.

   emit.py keeps its own copies of these lists so an author gets the error while
   authoring rather than at build time. Copies go stale, so the copies themselves are
   checked here against the source they were copied from — which is the part emit.py
   cannot do, because it is the thing being checked. */
const TUNE_IDS = new Set([...studioJs.matchAll(/Tune\.define\(\{\s*\n?\s*id:\s*'([^']+)'/g)].map((m) => m[1]));
const SYM_IDS = new Set([...circuitJs.matchAll(/define\('([^']+)',\s*'/g)].map((m) => m[1]));
for (const c of allCourses) {
  for (const [mi, m] of c.modules.entries()) {
    for (const t of asList(m.tune)) {
      if (!TUNE_IDS.has(t.model)) {
        problems.push(`${c.id}/M${mi + 1}: tune names the "${t.model}" model, which is not ` +
          `defined in studio.js (have: ${[...TUNE_IDS].join(', ')})`);
      }
    }
    for (const it of asList(m.match).flatMap((q) => q.items || [])) {
      if (!SYM_IDS.has(it.sym)) {
        problems.push(`${c.id}/M${mi + 1}: the symbol drill asks for "${it.sym}", which circuit.js ` +
          `cannot draw (have: ${[...SYM_IDS].join(', ')})`);
      }
    }
  }
}
/* ---- the sketch language: what the machine has, and what the editor offers ----
 *
 * src/mcu.js is the only definition of this language. lang.js describes it to the
 * editor — highlighting and completion both read the same tables — and the two are
 * held together here rather than by anybody remembering. */
{
  const mcuJsSrc = read(join(ROOT, 'src', 'mcu.js'));
  const langJsSrc = read(join(ROOT, 'src', 'lang.js'));

  /* the interpreter's own tables */
  const builtinBlock = mcuJsSrc.slice(mcuJsSrc.indexOf('const BUILTIN = bare({'));
  const machineHas = new Set(
    [...builtinBlock.slice(0, builtinBlock.indexOf('\n    });'))
      .matchAll(/^      ([A-Za-z_]\w*)\s*:\s*\{\s*n:/gm)].map((m) => m[1]));
  const constBlock = mcuJsSrc.slice(mcuJsSrc.indexOf('const CONSTANTS = bare({'));
  for (const m of constBlock.slice(0, constBlock.indexOf('});'))
    .matchAll(/([A-Za-z_]\w*)\s*:\s*num\(/g)) machineHas.add(m[1]);

  /* what the editor offers: the fn()/konst() entries of MCU_GLOBALS */
  const globalsBlock = langJsSrc.slice(langJsSrc.indexOf('const MCU_GLOBALS = ['));
  const editorOffers = new Set(
    [...globalsBlock.slice(0, globalsBlock.indexOf('\n];'))
      .matchAll(/^  (?:fn|konst)\('([A-Za-z_]\w*)'/gm)].map((m) => m[1]));

  if (!machineHas.size || !editorOffers.size) {
    problems.push('the sketch-language guard found no names on one side — its ' +
      'assumptions about mcu.js or lang.js have gone stale, so it is now checking nothing');
  }
  for (const n of [...machineHas].filter((x) => !editorOffers.has(x))) {
    problems.push(`the sketch builtin "${n}" exists in src/mcu.js but the editor does not ` +
      `offer it — a name the machine has that nothing tells the learner about`);
  }
  for (const n of [...editorOffers].filter((x) => !machineHas.has(x))) {
    problems.push(`the editor offers "${n}" in the sketch language, but src/mcu.js has no ` +
      `such name — the sketch would be refused on the line that used it`);
  }
}

/* Read emit.py's copies back and compare. Without this the guard above only caught
   a unit naming something nothing defines — it never noticed emit.py and the source
   disagreeing, which is the failure that actually happens: a model gains a readout,
   or a symbol is added, and the authoring-time list silently rots. */
{
  const emitPy = read(join(ROOT, 'tools', 'emit.py'));
  const setFrom = (re) => {
    const m = emitPy.match(re);
    return new Set(m ? [...m[1].matchAll(/"([^"]+)"/g)].map((x) => x[1]) : []);
  };
  const diff = (a, b) => [...a].filter((x) => !b.has(x));

  const emitSyms = setFrom(/MATCH_SYMBOLS = \{([^}]*)\}/);
  const emitModels = new Set([...emitPy.matchAll(/^\s{4}"([a-z0-9-]+)":\s*\{/gm)].map((m) => m[1]));

  for (const [what, mine, theirs] of [
    ['symbol', SYM_IDS, emitSyms],
    ['tune model', TUNE_IDS, emitModels],
  ]) {
    for (const x of diff(mine, theirs)) {
      problems.push(`${what} "${x}" is defined in src/ but missing from emit.py's list — ` +
        'an author cannot use it and will be told it does not exist');
    }
    for (const x of diff(theirs, mine)) {
      problems.push(`${what} "${x}" is listed in emit.py but no longer defined in src/ — ` +
        'emit.py would accept a unit the build then cannot render');
    }
  }

  /* And the per-model readout keys, which is how a constraint becomes untargetable */
  for (const id of TUNE_IDS) {
    const body = studioJs.slice(studioJs.indexOf(`id: '${id}'`));
    const compute = body.slice(body.indexOf('compute:'), body.indexOf('plot:'));
    const real = new Set([...compute.matchAll(/^\s{6}([a-z0-9_]+):\s*\{\s*label:/gm)].map((m) => m[1]));
    const listed = setFrom(new RegExp('"' + id + '":\\s*\\{([^}]*)\\}'));
    if (!real.size || !listed.size) continue;
    for (const k of diff(real, listed)) {
      problems.push(`the ${id} model reports "${k}", which emit.py does not list — ` +
        'no unit can constrain it');
    }
    for (const k of diff(listed, real)) {
      problems.push(`emit.py lists "${k}" for the ${id} model, which it no longer reports — ` +
        'a constraint on it would be accepted and then never satisfiable');
    }
  }
}

notes.push(`tune models: ${TUNE_IDS.size} registered · symbols: ${SYM_IDS.size} drawable · ` +
  "emit.py's copies agree");


const degree = { programs, courses: allCourses };
if (!programs.length) notes.push('catalog: no _spine*.json — building without any programme');

/* ---------------------------------------------------------------- scripts */
const langJs = read(join(SRC, 'lang.js'));
const engineJs = read(join(SRC, 'engine.js'));
const appJs = read(join(SRC, 'app.js'));
/* The desk (notepad + calculator) is optional: the app guards every call to it with a
   typeof check, so a build without the file is a build without the modal rather than a
   broken page. Read defensively so that stays true. */
const deskJs = existsSync(join(SRC, 'desk.js')) ? read(join(SRC, 'desk.js')) : '';
/* The microcontroller's interpreter. circuit.js guards every use of it with a typeof
   check and says plainly in the panel when it is absent, so a build without the file
   is a build whose MCU part draws and solves but does not run a sketch. Read the same
   defensive way as the desk. */
const mcuJs = existsSync(join(SRC, 'mcu.js')) ? read(join(SRC, 'mcu.js')) : '';
/* Natural notation -> LaTeX for the derivation input. Read defensively like the
   others: app.js guards its use, so a build without the file is a build that
   still expects LaTeX rather than a broken page. */
const mathInputJs = existsSync(join(SRC, 'mathinput.js')) ? read(join(SRC, 'mathinput.js')) : '';
const headSrc = read(join(SRC, 'index.head.html'));

/* What ships is the source with its comments and indentation taken out
   (tools/minify.mjs) — a third of the script bytes and a quarter of the stylesheet,
   none of it read by a browser. The source files stay as they are; every check above
   this line read them raw, and tools/verify_minify.mjs proves the stripped text has
   the same tokens. */
const shipped = {};
let rawKb = 0, shippedKb = 0;
for (const [name, text] of Object.entries({ langJs, engineJs, studioJs, mathInputJs, mcuJs, circuitJs, deskJs, appJs })) {
  shipped[name] = text ? stripJs(text) : '';
  rawKb += Buffer.byteLength(text, 'utf8') / 1024;
  shippedKb += Buffer.byteLength(shipped[name], 'utf8') / 1024;
}
const head = headSrc.replace(/<style>([\s\S]*?)<\/style>/, (m, css) => '<style>\n' + stripCss(css) + '\n</style>');
notes.push(`shipped scripts: ${Math.round(rawKb)} KB of source -> ${Math.round(shippedKb)} KB without comments ` +
  `or indentation; stylesheet ${Math.round(headSrc.length / 1024)} KB -> ${Math.round(head.length / 1024)} KB`);

/* A literal `</script>` inside any JSON string would terminate the host <script>, and
   the catalog really contains them — WEB301 and ELEC420 teach HTML. Escaping every
   `<` as \u003c keeps the JSON valid JavaScript and inert to the HTML tokenizer.
   This is needed only for the literal that is INLINED into the page. A chunk is
   fetched and handed to JSON.parse, which is not an HTML context, so it ships raw:
   the escape would cost 26 KB across the catalog and nothing at all after gzip.
   Building one escaped string and using it for both shapes is the trap — it either
   bloats every chunk or, done the other way round, truncates the two web courses. */
const inlineLiteral = (v) => JSON.stringify(v).replace(/</g, '\u005cu003c');

/* Assemble one shape. Called twice, sequentially: the two scripts are not in a subset
   relation (the shell carries a chunk list the inlined build does not), so the
   tokenizer guard and the syntax check have to run against each of them. */
/* The circuit editor and the sketch interpreter are needed on the build, schematic,
   symbol and playground screens and nowhere else, and together they are a third of
   the shipped script. The split shell leaves them out and fetches lib/circuit.<hash>.js
   the first time one of those screens opens (ensureCircuit in app.js); the inlined
   file keeps them, because it must fetch nothing. */
const circuitLib = [shipped.mcuJs, shipped.circuitJs].join('\n');
const circuitLibName = `circuit.${createHash('sha256').update(circuitLib).digest('hex').slice(0, 8)}.js`;

function assemble(label, degreeLiteral, chunkLiteral, withCircuit) {
  const appScript = [
    shipped.langJs,
    'const DEGREE_DATA = ' + degreeLiteral + ';\n',
    /* Always emitted, even empty: app.js guards it with typeof, but an undeclared
       identifier is a ReferenceError that `node --check` cannot see, and it would
       blank the page before anything painted. */
    'const DEGREE_CHUNKS = ' + chunkLiteral + ';\n',
    shipped.engineJs,
    shipped.studioJs,
    shipped.mathInputJs,
    withCircuit ? circuitLib : '',
    shipped.deskJs,
    shipped.appJs,
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
      problems.push(`the ${label} script contains a literal "${seq}" (line ~${line}) — it ${why}`);
    }
  }

  /* Syntax-check before shipping. The temp is named per shape so two assemblies
     cannot clobber each other's file. */
  const tmp = join(OUT_DIR, '.syntax-check.' + label.replace(/\W+/g, '-') + '.js');
  mkdirSync(OUT_DIR, { recursive: true });
  writeFileSync(tmp, appScript, 'utf8');
  try {
    execFileSync(process.execPath, ['--check', tmp], { stdio: 'pipe' });
    notes.push(`syntax: the ${label} script parses cleanly`);
  } catch (e) {
    problems.push(`JavaScript syntax error in the ${label} script:\n` +
      String(e.stderr || e.stdout || e.message).split('\n').slice(0, 12).join('\n'));
  } finally {
    try { rmSync(tmp, { force: true }); } catch {}
  }

  return [
    head,
    '',
    '<script>',
    appScript,
    '</' + 'script>',
    '</body>',
    '</html>',
    '',
  ].join('\n');
}

/* ---------------------------------------------------------------- emit */
/* Shape one: everything inlined, and therefore no chunk list at all — a build that
   lists nothing is a build that fetches nothing, which is what keeps file:// working
   rather than a promise made in a comment. */
const inlineHtml = assemble('inlined', inlineLiteral(degree), 'null', true);

/* The on-demand library is a script file of its own, so it needs only the syntax
   check and none of the HTML-tokenizer guards. */
{
  const tmp = join(OUT_DIR, '.syntax-check.circuit-lib.js');
  mkdirSync(OUT_DIR, { recursive: true });
  writeFileSync(tmp, circuitLib, 'utf8');
  try {
    execFileSync(process.execPath, ['--check', tmp], { stdio: 'pipe' });
    notes.push(`syntax: the circuit library parses cleanly (${Math.round(Buffer.byteLength(circuitLib) / 1024)} KB, fetched on demand)`);
  } catch (e) {
    problems.push('JavaScript syntax error in the circuit library:\n' +
      String(e.stderr || e.stdout || e.message).split('\n').slice(0, 12).join('\n'));
  } finally {
    try { rmSync(tmp, { force: true }); } catch {}
  }
}

/* Shape two: the shell, plus one payload per programme.

   The filename carries a hash of the payload, for a reason worth stating: the shell
   holds the code that interprets the chunk, so a stale chunk against a fresh shell is
   not merely old data — ids stop matching LESSON_INDEX and there is nothing to retry,
   because the fetch succeeded. Naming the file after its contents makes a stale chunk
   unaddressable instead. GitHub Pages sets its own cache headers and cannot be told
   otherwise, and both dev servers send no-store, so this failure is not reproducible
   locally — which is exactly why it is designed out rather than tested for. */
/* One payload per programme, which is how this started, put a whole degree behind a
   single fetch. That was tolerable at four modules a course and stops being so the
   moment a course carries a real syllabus: the per-payload budget is 3 MB and
   ee-msc was at 2.5 MB before any of the depth work landed.

   So a payload is a BAND of a programme — one year. That is also the unit the planner
   navigates in, which is what makes it the right seam rather than merely a smaller
   one. */
/* A payload is ONE COURSE.

   It was one per programme, then one per band. Both stopped fitting as the courses
   gained real syllabi: ee-msc year 1 reached 3.2 MB with its six courses only half
   written, against a 3 MB per-payload budget, and it would have kept growing.

   A course is the right unit and not merely a smaller one: it is what a learner
   opens, it is the granularity the rail and the planner already navigate, and its
   size is bounded by how much one subject can hold rather than by how many subjects
   happen to share a year. */
const chunks = [];
for (const prog of programs) {
  for (const c of (byProgram[prog.id] || [])) {
    const json = JSON.stringify([c]);
    const hash = createHash('sha256').update(json).digest('hex').slice(0, 8);
    const name = `${prog.id}.${c.id}.${hash}.json`;
    chunks.push({ id: prog.id, band: c.band === undefined ? 0 : c.band, course: c.id,
                  name: name, json: json, url: `programs/${name}`, courses: 1 });
  }
}
/* And the payload the shell fetches FIRST: every course as a skeleton — titles,
   minutes and counts, no content (tools/skeleton.mjs). The shell indexes the whole
   catalog from this one file and fetches a course's own payload the first time a
   lesson in it opens. Before this the shell fetched all 62 payloads, 13 MB, before
   the study plan could paint. */
const courseChunks = chunks.slice();
const indexJson = JSON.stringify({ courses: allCourses.map(skeletonOf) });
const indexName = `catalog.${createHash('sha256').update(indexJson).digest('hex').slice(0, 8)}.json`;
const indexChunk = { id: 'catalog', band: -1, course: '_index', name: indexName, json: indexJson,
                     url: `programs/${indexName}`, courses: allCourses.length };
chunks.push(indexChunk);

/* Pages publishes this repo as a PROJECT page, at /codex-learn/ — there is no CNAME.
   A leading slash would resolve to the user root and 404 in production while passing
   every local check, because locally the server root IS the site root. */
for (const ch of chunks) {
  if (/^\//.test(ch.url) || /^[a-z][a-z0-9+.-]*:/i.test(ch.url)) {
    problems.push(`chunk url "${ch.url}" is not document-relative — Pages serves this ` +
      'site from a subpath, where a leading slash points off the site root');
  }
}

const shellHtml = assemble('split shell',
  inlineLiteral({ programs, courses: [] }),
  JSON.stringify({
    index: indexChunk.url,
    courses: Object.fromEntries(courseChunks.map((c) => [c.course, c.url])),
    circuit: `lib/${circuitLibName}`,
  }), false);

/* The inlined shape must list nothing. Asserted rather than assumed: both shapes come
   out of one run, and it is the null that keeps the double-clickable file from
   attempting a fetch it cannot make. */
if (!/const DEGREE_CHUNKS = null;/.test(inlineHtml)) {
  problems.push('the inlined build lists chunks — it must fetch nothing');
}

const kbOf = (t) => Buffer.byteLength(t, 'utf8') / 1024;
/* The stamp is the hash of the shell as assembled, so it changes exactly when the
   shipped bytes change. Computed before substitution, or it would chase itself. */
const BUILD_ID = createHash('sha256').update(shellHtml).digest('hex').slice(0, 12);
const stamp = (h) => h.replace('__BUILD_ID__', BUILD_ID);

const inlineKb = kbOf(inlineHtml);
const shellKb = kbOf(shellHtml);
const chunkKb = chunks.map((c) => kbOf(c.json));
const chunksTotalKb = chunkKb.reduce((a, b) => a + b, 0);
const indexKb = kbOf(indexJson);

notes.push(`inlined artifact: ${Math.round(inlineKb)} KB`);
notes.push(`split shell: ${Math.round(shellKb)} KB, plus a ${Math.round(indexKb)} KB catalog index ` +
  `fetched at boot, plus ${courseChunks.length} course payload(s) totalling ` +
  `${Math.round(chunksTotalKb - indexKb)} KB fetched one course at a time`);
const bigThree = courseChunks.map((c, i) => [c.name, chunkKb[i]]).sort((a, b) => b[1] - a[1]).slice(0, 3);
notes.push(`${courseChunks.length} course payloads, largest: ` +
  bigThree.map(([n, k]) => `${n.replace(/\.[0-9a-f]{8}\.json$/, '')} ${Math.round(k)} KB`).join(', '));

console.log('--- build report ---');
for (const n of notes) console.log('  ·', n);
if (problems.length) {
  console.log('\nPROBLEMS:');
  for (const p of problems) console.log('  !', p);
  console.log('\nbuild aborted');
  process.exit(1);
}

/* Four budgets, because the two shapes fail in different ways.

   The inlined artifact is bounded by what is reasonable to double-click; nothing
   waits on it over a network any more, so it has room. The shell is what gates the
   first paint and is the one to keep small. A single chunk matters more than the sum,
   because it is one fetch behind one timeout: split a programme before letting one
   payload grow past this. */
/* The inlined artifact holds the whole catalog in one file, so it grows with the
   syllabus by design: 8 MB was already 95% spent before a single course reached full
   density. Like the module ceiling, this number is here to catch a build that has gone
   wrong, not to ration content. If it is ever genuinely too large to open from disk,
   the answer is to stop shipping the inlined shape, not to write less. */
const INLINE_BUDGET_KB = 32768;
/* The shell is what a browser parses before anything paints, so this number is a real
   user cost and not bookkeeping. It has been raised once, deliberately: the app gained
   a Newton-Raphson circuit solver, a subcircuit flattener, a breadboard, a 48 KB
   microcontroller interpreter and a 56 KB notepad, none of which existed when 1024 was
   chosen. That is the catalog's neighbours growing, which is precisely what this check
   is for — so the number moves only with a reason written down.

   The honest lever, when this is next hit, is not a bigger number. src/mcu.js and
   src/circuit.js are needed on the circuit and playground screens and nowhere else;
   loading them on demand would take roughly 250 KB out of first paint. Raise this
   again only if that has been considered and rejected. */
const SHELL_BUDGET_KB = 1536;
const CHUNK_BUDGET_KB = 3072;
/* The total is now the catalog's footprint on disk across every band, not the size
   of any one fetch — that is what CHUNK_BUDGET_KB bounds, and chunking by band is
   what keeps it honest. Raised because a catalog with real syllabi is simply larger;
   the number that governs what a browser waits for is the per-payload one. */
const CHUNKS_TOTAL_KB = 24576;

if (inlineKb > INLINE_BUDGET_KB) {
  problems.push(`the inlined artifact is ${Math.round(inlineKb)} KB, over the ` +
    `${INLINE_BUDGET_KB} KB budget — it exists only to be opened from disk, so drop a ` +
    'programme from IT rather than from the published build');
}
if (shellKb > SHELL_BUDGET_KB) {
  problems.push(`the split shell is ${Math.round(shellKb)} KB, over the ${SHELL_BUDGET_KB} KB ` +
    'budget — something other than the catalog has grown into the first paint');
}
chunks.forEach((c, i) => {
  if (chunkKb[i] > CHUNK_BUDGET_KB) {
    problems.push(`${c.name} is ${Math.round(chunkKb[i])} KB, over the ${CHUNK_BUDGET_KB} KB ` +
      'per-payload budget — chunk that programme by band');
  }
});
if (chunksTotalKb > CHUNKS_TOTAL_KB) {
  problems.push(`the payloads total ${Math.round(chunksTotalKb)} KB, over the ` +
    `${CHUNKS_TOTAL_KB} KB budget`);
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

/* Delete payloads from older builds, but keep the immediately previous generation:
   a reader still holding the last deploy's shell is asking for its hashed filenames,
   and removing them the moment a new build lands would 404 a page that was working a
   minute ago. docs/ is tracked, so an orphan would otherwise be committed and served
   for ever. */
/* Which payloads may be deleted is a question about BUILD HISTORY, and the file
   system does not know the answer: a fresh clone stamps every file with the checkout
   time, so ordering by mtime picks an arbitrary survivor and can delete the very file
   the deployed shell is asking for. So the history is recorded explicitly, in a small
   file that is committed alongside the payloads.

   Three generations are kept rather than one. The generations here are BUILDS, and
   several builds happen between deploys while iterating; keeping only one would let
   two local rebuilds delete what the live site is still serving. */
const PREV_FILE = '_generations.json';
const KEEP_GENERATIONS = 3;

function pruneChunks(dir, currentNames, ext) {
  ext = ext || '.json';
  const prevPath = join(dir, PREV_FILE);
  let history = [];
  if (existsSync(prevPath)) {
    try {
      const parsed = JSON.parse(readFileSync(prevPath, 'utf8'));
      if (Array.isArray(parsed)) history = parsed.filter((g) => Array.isArray(g));
    } catch { /* unreadable history: keep everything this round and rewrite it */ }
  }
  /* newest first, and never record the same generation twice in a row */
  const current = [...currentNames].sort();
  const same = history[0] && history[0].length === current.length &&
    history[0].every((n, i) => n === current[i]);
  if (!same) history.unshift(current);
  history = history.slice(0, KEEP_GENERATIONS);

  const keep = new Set(history.flat());
  const removed = [];
  if (existsSync(dir)) {
    for (const f of readdirSync(dir)) {
      if (f === PREV_FILE || !f.endsWith(ext) || keep.has(f)) continue;
      unlinkSync(join(dir, f));
      removed.push(f);
    }
  }
  writeFileSync(prevPath, JSON.stringify(history, null, 1), 'utf8');
  return removed;
}

function writeShape(dir, { inline }) {
  mkdirSync(dir, { recursive: true });
  const chunkDir = join(dir, 'programs');
  mkdirSync(chunkDir, { recursive: true });
  writeFileSync(join(dir, 'index.html'), stamp(shellHtml), 'utf8');
  /* What a running tab fetches to find out whether it is the current build. */
  writeFileSync(join(dir, 'version.json'), JSON.stringify({ build: BUILD_ID }) + '\n', 'utf8');
  for (const c of chunks) writeFileSync(join(chunkDir, c.name), c.json, 'utf8');
  if (inline) writeFileSync(join(dir, 'codewright.html'), stamp(inlineHtml), 'utf8');
  /* the on-demand circuit library, hashed and kept by generation like a payload */
  const libDir = join(dir, 'lib');
  mkdirSync(libDir, { recursive: true });
  writeFileSync(join(libDir, circuitLibName), circuitLib, 'utf8');
  return pruneChunks(chunkDir, chunks.map((c) => c.name))
    .concat(pruneChunks(libDir, [circuitLibName], '.js'));
}

const droppedBuild = writeShape(OUT_DIR, { inline: true });
const droppedDocs = previewOnly ? [] : writeShape(DOCS_DIR, { inline: false });
if (!previewOnly) writeFileSync(join(DOCS_DIR, '.nojekyll'), '', 'utf8');

console.log(`\nwrote ${join(OUT_DIR, 'codewright.html')}  (${Math.round(inlineKb)} KB, inlined — open this one from disk)`);
console.log(`wrote ${join(OUT_DIR, 'index.html')}  (${Math.round(shellKb)} KB shell + ${chunks.length} payloads — what a browser gets)`);
for (const d of [...new Set([...droppedBuild, ...droppedDocs])]) console.log(`  removed stale ${d}`);

/* docs/ is tracked and the payload filenames change whenever a course does, so a
   habitual `git add docs/index.html` would publish a shell whose payloads 404. Print
   the command that stages all of it. */
if (previewOnly) {
  console.log('\npreview build: docs/ was not written');
} else {
  console.log('\ndocs/ is what GitHub Pages serves. To publish:');
  console.log('  git add docs/index.html docs/version.json docs/programs docs/.nojekyll');
}

