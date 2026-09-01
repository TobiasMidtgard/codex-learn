/**
 * skeleton.mjs — a course with its content taken out and its shape left in.
 *
 * The published shell used to fetch every course payload before the first screen
 * painted: 62 files and 13 MB, of which the study plan needs the titles and the
 * counts and nothing else. A skeleton is what the study plan, the rail, the course
 * page, search and the XP arithmetic actually read — every unit's title, minutes
 * and the numbers the course page prints beside it — so the app can index the whole
 * catalog from one small file and fetch a course's content the first time a lesson
 * in it opens.
 *
 * The rule for what stays is "what a renderer reads before a lesson opens". Lesson
 * IDS are derived from position and kind (see buildDegreeIndex in src/app.js), so a
 * skeleton keeps every unit in place, including empty ones, and never re-orders.
 *
 * Shared by build.mjs, which writes the index, and tools/verify_lazy.mjs, which
 * proves a skeleton indexes to the same lesson ids as the course it came from.
 */

/* A unit key holds nothing, one authored object, or a list of them. */
const asList = (x) => (!x ? [] : (Array.isArray(x) ? x : [x]));
const sameShape = (orig, list) => (Array.isArray(orig) ? list : list[0]);
const len = (v) => (Array.isArray(v) ? v.length : 0);

/* Per kind: which arrays the course page counts (see unitMeta in src/app.js), and
   any flag a screen needs before the content arrives. */
const COUNTS = {
  read: [],
  sandbox: ['notice'],
  derive: ['steps'],
  blanks: ['blanks'],
  numeric: ['given'],
  match: ['items'],
  tune: ['constraints'],
  build: ['checks'],
  quiz: ['questions'],
  lab: ['tests'],
};

export const UNIT_KEYS = Object.keys(COUNTS);

function skeletonUnit(kind, u) {
  if (!u || typeof u !== 'object') return u;
  const n = {};
  for (const k of COUNTS[kind]) n[k] = len(u[k]);
  const out = { title: u.title, n };
  if (u.minutes !== undefined) out.minutes = u.minutes;
  if (kind === 'lab') out.runtime = u.runtime;
  /* a numeric unit with a schematic needs the circuit painter, which the split
     shell loads on demand — the loader has to know before the content arrives */
  if (kind === 'numeric' && u.diagram) n.diagram = 1;
  return out;
}

export function skeletonOf(course) {
  const c = {};
  for (const k of Object.keys(course)) {
    if (k === 'modules' || k === 'capstone') continue;
    c[k] = course[k];
  }
  /* A module's concept list and the capstone's brief, deliverables and rubric are
     read by the course page and nowhere earlier, and between them they were 530 KB
     of the 915 KB a skeleton index came to. The course page prefetches the course
     and repaints when it arrives, so they travel with the content instead. */
  c.modules = (course.modules || []).map((m) => {
    const sm = { title: m.title, summary: m.summary };
    for (const kind of UNIT_KEYS) {
      if (m[kind] === undefined) continue;
      if (!m[kind]) { sm[kind] = m[kind]; continue; }
      sm[kind] = sameShape(m[kind], asList(m[kind]).map((u) => skeletonUnit(kind, u)));
    }
    return sm;
  });
  const cap = course.capstone;
  if (cap) {
    c.capstone = {
      title: cap.title,
      minutes: cap.minutes,
      runtime: cap.runtime,
      n: { tests: len(cap.tests), deliverables: len(cap.deliverables), rubric: len(cap.rubric) },
    };
  }
  c.skeleton = true;
  return c;
}
