/**
 * verify_lazy.mjs — the catalog index and per-course hydration, driven end to end.
 *
 * The published shell no longer fetches every course before it paints. It fetches
 * one index of skeletons (tools/skeleton.mjs), builds LESSON_INDEX from that, and
 * fetches a course's own payload the first time a lesson in it opens, filling the
 * SAME lesson objects in (applyCourse in src/app.js). Three things can go wrong
 * there, and each would be invisible to every other gate:
 *
 *   1. a skeleton that indexes to different lesson ids than the course it came from —
 *      every completed unit in a learner's progress would stop matching;
 *   2. a count that disagrees with the content — the course page would print one
 *      number of checks and the lab would run another;
 *   3. a hydration that replaces lesson objects instead of filling them, or leaves a
 *      field behind — the rail's reference goes stale, or a lab opens with no files.
 *
 * So this loads the real app through tools/app_stage.mjs twice: once with the full
 * catalog inlined, once with the skeleton index and a fetch that serves the course
 * payloads, and requires the two to agree on every id, type and count; then it
 * hydrates every course through the shipped hydrateCourse and checks identity and
 * completeness lesson by lesson. Reads catalog/*.json directly, the way build.mjs does.
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadApp } from './app_stage.mjs';
import { skeletonOf } from './skeleton.mjs';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CATALOG = join(ROOT, 'catalog');

const spines = readdirSync(CATALOG).filter((f) => /^_spine.*\.json$/.test(f))
  .sort((a, b) => (a === '_spine.json' ? -1 : b === '_spine.json' ? 1 : a.localeCompare(b)));
const programs = [];
const courses = [];
for (const f of spines) {
  const spine = JSON.parse(readFileSync(join(CATALOG, f), 'utf8'));
  const prog = spine.program;
  prog.bands = prog.bands || prog.years || [];
  prog.bandNoun = prog.bandNoun || 'Year';
  programs.push(prog);
  for (const s of spine.courses) {
    let c;
    try { c = JSON.parse(readFileSync(join(CATALOG, s.id + '.json'), 'utf8')); } catch { continue; }
    c.band = s.band !== undefined ? s.band : s.year;
    c.program = prog.id;
    c.prereqs = s.prereqs;
    delete c.year;
    for (const m of c.modules) for (const b of (Array.isArray(m.build) ? m.build : (m.build ? [m.build] : []))) delete b.solution;
    courses.push(c);
  }
}
if (!courses.length) { console.log('no courses found — nothing to verify'); process.exit(1); }

const problems = [];
const say = (s) => console.log(s);

/* ---- 1. the two indexes agree ---- */
const EXPORTS = { LESSON_INDEX: 'LESSON_INDEX', COURSE_OF: 'COURSE_OF', DEGREE: 'DEGREE',
  hydrateCourse: 'hydrateCourse', nOf: 'nOf', LESSONS_OF: 'LESSONS_OF',
  loadDegreeChunks: 'loadDegreeChunks', catalogLoaded: 'catalogLoaded', MISSING_PROGRAMS: 'MISSING_PROGRAMS' };

globalThis.DEGREE_DATA = { programs, courses: JSON.parse(JSON.stringify(courses)) };
globalThis.DEGREE_CHUNKS = null;
const full = loadApp({ exports: EXPORTS }).app;

const skeletons = courses.map(skeletonOf);
const urls = { index: 'programs/catalog.test.json', courses: {} };
const served = { 'programs/catalog.test.json': { courses: skeletons } };
for (const c of courses) {
  urls.courses[c.id] = 'programs/' + c.id + '.test.json';
  served[urls.courses[c.id]] = [c];
}
let fetches = 0;
const fetchStub = (url) => {
  fetches++;
  const body = served[url];
  if (!body) return Promise.resolve({ ok: false, status: 404, json: () => Promise.reject(new Error('404')) });
  return Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(JSON.parse(JSON.stringify(body))) });
};
globalThis.DEGREE_DATA = { programs, courses: [] };
globalThis.DEGREE_CHUNKS = urls;
const lazy = loadApp({ exports: EXPORTS, fetch: fetchStub }).app;

await lazy.loadDegreeChunks();
if (!lazy.catalogLoaded()) problems.push('the index did not load through loadDegreeChunks');
if (lazy.MISSING_PROGRAMS.length) problems.push('programmes marked missing after the index loaded: ' + lazy.MISSING_PROGRAMS.join(', '));
if (fetches !== 1) problems.push(`boot made ${fetches} fetches; the index is one`);

const COUNT_KEYS = ['tests', 'checks', 'questions', 'items', 'blanks', 'steps', 'constraints', 'given'];
const fullIds = Object.keys(full.LESSON_INDEX).filter((id) => full.LESSON_INDEX[id].track.kind === 'course');
const lazyIds = Object.keys(lazy.LESSON_INDEX).filter((id) => lazy.LESSON_INDEX[id].track.kind === 'course');
if (fullIds.length !== lazyIds.length) {
  problems.push(`the full catalog indexes ${fullIds.length} course lessons, the skeleton index ${lazyIds.length}`);
}
let counted = 0;
for (const id of fullIds) {
  const a = full.LESSON_INDEX[id], b = lazy.LESSON_INDEX[id];
  if (!b) { problems.push(`${id}: in the full index, missing from the skeleton index`); continue; }
  if (a.lesson.type !== b.lesson.type) problems.push(`${id}: type ${a.lesson.type} vs ${b.lesson.type}`);
  if (a.lesson.title !== b.lesson.title) problems.push(`${id}: title differs in the skeleton`);
  if (a.lesson.min !== b.lesson.min) problems.push(`${id}: minutes ${a.lesson.min} vs ${b.lesson.min}`);
  if (a.mi !== b.mi) problems.push(`${id}: module index ${a.mi} vs ${b.mi}`);
  for (const k of COUNT_KEYS) {
    if (full.nOf(a.lesson, k) !== lazy.nOf(b.lesson, k)) {
      problems.push(`${id}: ${k} counts ${full.nOf(a.lesson, k)} (content) vs ${lazy.nOf(b.lesson, k)} (skeleton)`);
    }
    counted++;
  }
}
for (const c of courses) {
  const a = full.LESSONS_OF[c.id] || [], b = lazy.LESSONS_OF[c.id] || [];
  if (a.map((l) => l.id).join(',') !== b.map((l) => l.id).join(',')) {
    problems.push(`${c.id}: the unit order differs between the two indexes`);
  }
}
say(`index    ${fullIds.length} lessons, ${counted} counts agree between content and skeleton`);

/* ---- 2. hydration fills the same objects ---- */
const before = {};
for (const id of lazyIds) before[id] = lazy.LESSON_INDEX[id].lesson;
const HEAVY = { read: ['mdText'], code: ['files', 'main', 'tests', 'mdText'], project: ['files', 'main', 'tests', 'mdText'],
  quiz: ['questions'], blanks: ['listing', 'blanks'], derive: ['steps'], numeric: ['prompt', 'why'],
  match: ['items'], tune: ['model'], build: ['start', 'checks'], sandbox: ['sandbox'] };
let hydrated = 0, fieldsChecked = 0;
for (const c of courses) {
  const lc = lazy.COURSE_OF[c.id];
  if (!lc || !lc.skeleton) { problems.push(`${c.id}: not a skeleton before hydration`); continue; }
  const before_fetches = fetches;
  await lazy.hydrateCourse(c.id);
  await lazy.hydrateCourse(c.id);            /* a second call must not fetch again */
  if (fetches !== before_fetches + 1) problems.push(`${c.id}: hydration made ${fetches - before_fetches} fetches, expected 1`);
  if (lc.skeleton) problems.push(`${c.id}: still marked skeleton after hydration`);
  if (!lc.modules.every((m) => Array.isArray(m.concepts))) problems.push(`${c.id}: concept lists did not arrive`);
  if (!lc.capstone || !Array.isArray(lc.capstone.rubric)) problems.push(`${c.id}: the capstone brief did not arrive`);
  hydrated++;
  for (const l of lazy.LESSONS_OF[c.id]) {
    if (before[l.id] !== l) problems.push(`${l.id}: hydration replaced the lesson object`);
    const want = HEAVY[l.type] || [];
    const ref = full.LESSON_INDEX[l.id].lesson;
    for (const k of want) {
      fieldsChecked++;
      if (ref[k] === undefined) continue;                 /* the content has none either */
      if (l[k] === undefined) problems.push(`${l.id}: ${k} missing after hydration`);
      else if (JSON.stringify(l[k]) !== JSON.stringify(ref[k])) problems.push(`${l.id}: ${k} differs from the content`);
    }
    for (const k of COUNT_KEYS) {
      if (lazy.nOf(l, k) !== full.nOf(ref, k)) problems.push(`${l.id}: ${k} count ${lazy.nOf(l, k)} after hydration vs ${full.nOf(ref, k)}`);
    }
  }
}
say(`hydrate  ${hydrated} courses, ${fieldsChecked} content fields present and equal, every lesson object kept`);

/* ---- 3. a payload that does not come ---- */
{
  const ghost = { id: 'GHOST999', title: 'Ghost', level: 'Beginner', band: 1, program: programs[0].id,
    modules: [{ title: 'M', summary: '', lab: { title: 'L', minutes: 5, runtime: 'python', n: { tests: 1 } } }],
    capstone: { title: 'C', n: { tests: 4 } }, skeleton: true, prereqs: [] };
  /* a fresh DEGREE_DATA: the app adopts the global object itself, so the previous
     stage's courses would otherwise already be in it */
  globalThis.DEGREE_DATA = { programs, courses: [] };
  globalThis.DEGREE_CHUNKS = { index: 'programs/none.json', courses: { GHOST999: 'programs/nowhere.json' } };
  served['programs/none.json'] = { courses: [ghost] };
  const g2 = loadApp({ exports: EXPORTS, fetch: fetchStub }).app;
  await g2.loadDegreeChunks();
  let failed = false;
  try { await g2.hydrateCourse('GHOST999'); } catch (e) { failed = true; }
  if (!failed) problems.push('hydrating a course whose payload 404s resolved');
  if (!g2.COURSE_OF.GHOST999 || !g2.COURSE_OF.GHOST999.skeleton) problems.push('a failed hydration un-marked the skeleton');
  let again = false;
  try { await g2.hydrateCourse('GHOST999'); } catch (e) { again = true; }
  if (!again) problems.push('a failed hydration was memoised, so the retry never fetched');
  say('failure  a missing payload rejects, keeps the skeleton, and retries on the next call');
}

if (problems.length) {
  console.log(`\n${problems.length} problem(s):`);
  for (const p of problems.slice(0, 40)) console.log('  -', p);
  if (problems.length > 40) console.log(`  … and ${problems.length - 40} more`);
  process.exit(1);
}
console.log(`\nAll good: ${courses.length} courses index identically from content and from skeleton, ` +
  `and hydrate in place.`);
