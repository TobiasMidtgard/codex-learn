/* ============ Codewright app: state, routing, views ============ */

/* ---------- app state ---------- */
/* What each unit kind is called where a learner sees it. The type name is also a
   CSS class, so these are the words and those are the colours. */
/* disclosure glyphs, kept out of the markup so the arrows stay consistent */
const UNI = { right: '▸', down: '▾' };
const UNIT_KIND = { read: 'Read', sandbox: 'Explore', quiz: 'Quiz', blanks: 'Fill in',
  match: 'Match', numeric: 'Solve', tune: 'Design', derive: 'Derive', build: 'Build',
  code: 'Lab', project: 'Capstone' };
const XP = { read: 10, sandbox: 15, blanks: 20, match: 20, numeric: 25, quiz: 25, tune: 30, derive: 35, build: 35, code: 40, project: 120 };
const LESSON_INDEX = {};
const TRACK_LESSONS = {};
const TRACK_OF = {};
const teardownFns = [];

(function buildTrackIndex() {
  for (const t of TRACKS) {
    const flat = [];
    t.modules.forEach(function (m, mi) {
      m.lessons.forEach(function (l, li) {
        l.trackId = t.id;
        l.num = (mi + 1) + '.' + (li + 1);
        LESSON_INDEX[l.id] = { lesson: l, track: t, module: m, mi: mi };
        flat.push(l);
      });
    });
    TRACK_LESSONS[t.id] = flat;
    TRACK_OF[t.id] = t;
  }
})();

/* ---------- the foundation tracks are the first year of Computer Science ----------
   They were a parallel structure: their own rail section, their own progress block,
   their own place in the dashboard. But they are what the CS degree assumes you have
   done, which makes them its foundation year rather than a separate product. Modelled
   as courses in band 0 so the planner, the rail, search and every total treat them the
   same way as everything else — the only difference left is that opening one goes to
   the track view, because a track's lessons are not a course's modules. */
const FOUNDATION_BAND = 0;
function adoptTracksInto(programId) {
  for (const t of TRACKS) {
    t.kind = 'track';
    t.program = programId;
    t.band = FOUNDATION_BAND;
    t.title = t.name;
    t.id = t.id;
    t.level = t.level || 'Beginner';
    t.credits = t.credits || 0;
    t.hours = t.hours || Math.round(TRACK_LESSONS[t.id]
      .reduce(function (n, l) { return n + (l.min || 10); }, 0) / 60);
    t.summary = t.summary || t.blurb || '';
    t.prereqs = [];
    t.stack = t.stack || [];
    COURSE_OF[t.id] = t;
    DEGREE.courses.push(t);
  }
}

/* ---------- degree catalog ---------- */
const DEGREE = (typeof DEGREE_DATA !== 'undefined' && DEGREE_DATA) ? DEGREE_DATA : { programs: [], courses: [] };
/* The published build ships the courses as one fetched payload per programme, because
   inlined they are seven eighths of the page and nothing renders until all of it has
   parsed. The double-clickable build inlines them and lists nothing here.

   Guarded with typeof for the same reason DEGREE is: an undeclared identifier is a
   ReferenceError thrown before the first paint, and `node --check` in build.mjs is a
   syntax check that cannot see it. */
const DEGREE_CHUNK_LIST = (typeof DEGREE_CHUNKS !== 'undefined' && DEGREE_CHUNKS) ? DEGREE_CHUNKS : [];
const MISSING_PROGRAMS = [];
function programMissing(id) { return MISSING_PROGRAMS.indexOf(id) >= 0; }
/* A course is placed by (program, band). `band` is the neutral name for what the CS
   degree calls a year and the EE master's calls a track, so nothing has to pretend a
   track is a year. */
const PROGRAMS = DEGREE.programs || [];
const PROGRAM_OF = {};
PROGRAMS.forEach(function (pr) { PROGRAM_OF[pr.id] = pr; });
function programOf(c) { return PROGRAM_OF[c && c.program] || PROGRAMS[0] || null; }
function bandOf(pr, n) {
  const bands = (pr && pr.bands) || [];
  for (const b of bands) if (b.n === n) return b;
  return null;
}
function bandLabel(pr, n) { return ((pr && pr.bandNoun) || 'Year') + ' ' + n; }
function defaultProgramId() { return PROGRAMS.length ? PROGRAMS[0].id : ''; }
const COURSE_OF = {};
const COURSE_DEPENDENTS = {};
const LEVEL_ORDER = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];

function capstoneMd(c) {
  const cap = c.capstone;
  let md = cap.brief || '';
  if (cap.deliverables && cap.deliverables.length) {
    md += '\n\n## Deliverables\n\n' + cap.deliverables.map(function (d) { return '- ' + d; }).join('\n');
  }
  if (cap.constraints && cap.constraints.length) {
    md += '\n\n## Constraints\n\n' + cap.constraints.map(function (x) { return '- ' + x; }).join('\n');
  }
  if (cap.rubric && cap.rubric.length) {
    md += '\n\n## Assessment rubric\n\n| Criterion | Weight | How it is judged |\n|---|---|---|\n' +
      cap.rubric.map(function (r) {
        return '| ' + r.criterion + ' | ' + r.weight + '% | ' + String(r.evidence).replace(/\|/g, '/') + ' |';
      }).join('\n');
  }
  return md;
}

function buildDegreeIndex(courses) {
  for (const c of courses) {
    COURSE_OF[c.id] = c;
    /* a course behaves like a mini-track so lesson chrome, nav and XP all work */
    c.kind = 'course';
    c.name = c.id + ' · ' + c.title;
    c.tint = 'var(--lv-soft)';
    const flat = [];

    c.modules.forEach(function (m, mi) {
      const mnum = 'M' + (mi + 1);
      const modRef = { title: m.title };

      /* The pedagogical loop is three units per module: look at it, derive it,
         build it. Each is a lesson in its own right so progress, XP and the rail
         all work unchanged. */
      if (m.sandbox) {
        const sbl = {
          id: c.id + '-' + mnum + '-SB',
          type: 'sandbox',
          title: m.sandbox.title,
          min: m.sandbox.minutes || 8,
          mdText: m.sandbox.brief,
          sandbox: m.sandbox.visualiser,
          initial: m.sandbox.initial || {},
          notice: m.sandbox.notice || [],
          trackId: c.id, courseId: c.id, num: mnum + '\u00b7a',
        };
        LESSON_INDEX[sbl.id] = { lesson: sbl, track: c, module: modRef, mi: mi };
        flat.push(sbl);
        m.sandboxLessonId = sbl.id;
      }

      if (m.quiz) {
        const qzl = {
          id: c.id + '-' + mnum + '-QZ',
          type: 'quiz',
          title: m.quiz.title,
          min: m.quiz.minutes || 6,
          questions: m.quiz.questions || [],
          trackId: c.id, courseId: c.id, num: mnum + '\u00b7q',
        };
        LESSON_INDEX[qzl.id] = { lesson: qzl, track: c, module: modRef, mi: mi };
        flat.push(qzl);
        m.quizLessonId = qzl.id;
      }

      if (m.blanks) {
        const bkl = {
          id: c.id + '-' + mnum + '-FB',
          type: 'blanks',
          title: m.blanks.title,
          min: m.blanks.minutes || 8,
          mdText: m.blanks.brief,
          caption: m.blanks.caption,
          lang: m.blanks.lang || 'text',
          listing: m.blanks.listing,
          blanks: m.blanks.blanks || [],
          trackId: c.id, courseId: c.id, num: mnum + '\u00b7f',
        };
        LESSON_INDEX[bkl.id] = { lesson: bkl, track: c, module: modRef, mi: mi };
        flat.push(bkl);
        m.blanksLessonId = bkl.id;
      }

      if (m.numeric) {
        const nl = {
          id: c.id + '-' + mnum + '-NV',
          type: 'numeric',
          title: m.numeric.title,
          min: m.numeric.minutes || 7,
          mdText: m.numeric.brief,
          prompt: m.numeric.prompt,
          note: m.numeric.note,
          diagram: m.numeric.diagram,
          figure: m.numeric.figure,
          given: m.numeric.given || [],
          answer: m.numeric.answer,
          tol: m.numeric.tol,
          unit: m.numeric.unit,
          aside: m.numeric.aside,
          hint: m.numeric.hint,
          wrong: m.numeric.wrong,
          why: m.numeric.why,
          trackId: c.id, courseId: c.id, num: mnum + '·v',
        };
        LESSON_INDEX[nl.id] = { lesson: nl, track: c, module: modRef, mi: mi };
        flat.push(nl);
        m.numericLessonId = nl.id;
      }

      if (m.match) {
        const ml = {
          id: c.id + '-' + mnum + '-SY',
          type: 'match',
          title: m.match.title,
          min: m.match.minutes || 6,
          mdText: m.match.brief,
          prompt: m.match.prompt,
          labels: m.match.labels || [],
          items: m.match.items || [],
          trackId: c.id, courseId: c.id, num: mnum + '·s',
        };
        LESSON_INDEX[ml.id] = { lesson: ml, track: c, module: modRef, mi: mi };
        flat.push(ml);
        m.matchLessonId = ml.id;
      }

      if (m.tune) {
        const tl = {
          id: c.id + '-' + mnum + '-TN',
          type: 'tune',
          title: m.tune.title,
          min: m.tune.minutes || 9,
          mdText: m.tune.brief,
          prompt: m.tune.prompt,
          note: m.tune.note,
          model: m.tune.model,
          initial: m.tune.initial || {},
          constants: m.tune.constants || {},
          plotKey: m.tune.plotKey,
          constraints: m.tune.constraints || [],
          trackId: c.id, courseId: c.id, num: mnum + '·t',
        };
        LESSON_INDEX[tl.id] = { lesson: tl, track: c, module: modRef, mi: mi };
        flat.push(tl);
        m.tuneLessonId = tl.id;
      }

      if (m.build) {
        const bl = {
          id: c.id + '-' + mnum + '-BD',
          type: 'build',
          title: m.build.title,
          min: m.build.minutes || 20,
          mdText: m.build.brief,
          start: m.build.start || { parts: [], wires: [] },
          checks: m.build.checks || [],
          hints: m.build.hints || [],
          trackId: c.id, courseId: c.id, num: mnum + '\u00b7c',
        };
        LESSON_INDEX[bl.id] = { lesson: bl, track: c, module: modRef, mi: mi };
        flat.push(bl);
        m.buildLessonId = bl.id;
      }

      if (m.derive) {
        const dvl = {
          id: c.id + '-' + mnum + '-DV',
          type: 'derive',
          title: m.derive.title,
          min: m.derive.minutes || 12,
          mdText: m.derive.brief,
          vars: m.derive.vars || [],
          steps: m.derive.steps || [],
          closing: m.derive.closing,
          trackId: c.id, courseId: c.id, num: mnum + '\u00b7b',
        };
        LESSON_INDEX[dvl.id] = { lesson: dvl, track: c, module: modRef, mi: mi };
        flat.push(dvl);
        m.deriveLessonId = dvl.id;
      }

      if (!m.lab) return;
      const lab = m.lab;
      const lesson = {
        id: c.id + '-M' + (mi + 1),
        type: 'code',
        title: lab.title,
        min: lab.minutes || 30,
        lang: lab.runtime === 'web' ? 'web' : (lab.runtime === 'js' ? 'js' : 'python'),
        mdText: lab.brief,
        files: lab.files,
        main: lab.main,
        solution: lab.solution,
        hints: lab.hints || [],
        tests: lab.tests || [],
        trackId: c.id,
        courseId: c.id,
        num: 'M' + (mi + 1),
      };
      m.lessonId = lesson.id;
      LESSON_INDEX[lesson.id] = { lesson: lesson, track: c, module: { title: m.title }, mi: mi };
      flat.push(lesson);
    });

    if (c.capstone && c.capstone.tests && c.capstone.tests.length) {
      const cap = c.capstone;
      const lesson = {
        id: c.id + '-CAP',
        type: 'project',
        title: cap.title,
        min: cap.minutes || 240,
        lang: cap.runtime === 'web' ? 'web' : (cap.runtime === 'js' ? 'js' : 'python'),
        mdText: capstoneMd(c),
        files: cap.files,
        main: cap.main,
        solution: cap.solution,
        hints: cap.hints || [],
        tests: cap.tests,
        trackId: c.id,
        courseId: c.id,
        num: 'CAP',
      };
      c.capstoneLessonId = lesson.id;
      LESSON_INDEX[lesson.id] = { lesson: lesson, track: c, module: { title: 'Capstone' }, mi: c.modules.length };
      flat.push(lesson);
    }

    TRACK_LESSONS[c.id] = flat;
    TRACK_OF[c.id] = c;

    for (const p of (c.prereqs || [])) {
      (COURSE_DEPENDENTS[p] = COURSE_DEPENDENTS[p] || []).push(c.id);
    }
  }
}
/* the inlined build arrives with them already here; the split build adds to this */
buildDegreeIndex(DEGREE.courses);
if (PROGRAMS.length) adoptTracksInto(PROGRAMS[0].id);

/* ---------- fetching the degree payloads ----------
   One request per programme, in parallel, each with its own timeout and one retry. */
async function fetchChunk(url, ms) {
  if (typeof fetch === 'undefined') throw new Error('no fetch in this context');
  const ctl = typeof AbortController !== 'undefined' ? new AbortController() : null;
  const timer = setTimeout(function () { if (ctl) ctl.abort(); }, ms);
  try {
    const res = await fetch(url, ctl ? { signal: ctl.signal } : undefined);
    /* A 404 RESOLVES. Without this line the failure surfaces later as a JSON syntax
       error, from a different place, and routes around the retry entirely. */
    if (!res.ok) throw new Error('HTTP ' + res.status + ' for ' + url);
    const data = await res.json();
    /* Validate the whole payload HERE, where a throw is already routed to the retry
       and then to the banner. Anything that reaches buildDegreeIndex and throws
       part way through leaves half a programme indexed, and there is no clean way
       back from that — so nothing malformed is allowed to get that far. A captive
       portal returning a JSON error body, or a half-written file, both land here. */
    if (!Array.isArray(data)) throw new Error('payload is not a list of courses');
    for (const c of data) {
      if (!c || typeof c !== 'object' || typeof c.id !== 'string' || !Array.isArray(c.modules)) {
        throw new Error('payload contains a malformed course');
      }
    }
    return data;
  } finally { clearTimeout(timer); }
}

function programLoaded(id) {
  /* The foundation tracks are inlined and already sit in cs-degree, so a bare
     "does this programme have any courses" test would report it loaded and skip its
     fetch entirely. Only a fetched course counts as the payload arriving. */
  return DEGREE.courses.some(function (c) { return c.program === id && c.kind !== 'track'; });
}
function markMissing(id) { if (!programMissing(id)) MISSING_PROGRAMS.push(id); }
function markArrived(id) {
  const at = MISSING_PROGRAMS.indexOf(id);
  if (at >= 0) MISSING_PROGRAMS.splice(at, 1);
}

/* 30 s per attempt, twice. A payload is a couple of megabytes and the budget is for
   the whole body, so a short fuse does not fail fast on a slow link — it fails
   permanently, because the retry has exactly the same budget and loses the same race. */
const CHUNK_TIMEOUT_MS = 30000;

async function loadDegreeChunks() {
  /* Only ever fetch what is not already here. Re-fetching a programme that loaded
     fine means a retry for a DIFFERENT programme can un-load it: the second fetch
     fails, the id goes back on the missing list, and a working degree screen is
     replaced by an error page for courses that are sitting in the rail. */
  const todo = DEGREE_CHUNK_LIST.filter(function (ch) { return !programLoaded(ch.id); });
  if (!todo.length) return;
  const got = await Promise.all(todo.map(async function (ch) {
    /* the retry is sequential inside one promise, so a payload can never land twice */
    for (let attempt = 0; attempt < 2; attempt++) {
      try { return await fetchChunk(ch.url, CHUNK_TIMEOUT_MS); } catch (e) { if (attempt) return null; }
    }
    return null;
  }));
  /* Apply in declaration order rather than arrival order, so two machines on the same
     build index identically. MISSING_PROGRAMS is never cleared wholesale: it is the
     flag recomputeXp reads to decide whether it may write a lower XP figure, and a
     window where it is empty while the courses are still absent is a window where a
     deflated total gets persisted and synced. */
  todo.forEach(function (ch, i) {
    const courses = got[i];
    if (!courses) { markMissing(ch.id); return; }
    try {
      const fresh = courses.filter(function (c) { return !COURSE_OF[c.id]; });
      if (!fresh.length) throw new Error('payload added no courses');
      /* Index BEFORE exposing. Every renderer enumerates DEGREE.courses, and it is
         buildDegreeIndex that stamps c.kind, the synthesised lesson ids and
         TRACK_LESSONS — a course visible for even one frame before that is a page
         that breaks without throwing anything to catch. */
      buildDegreeIndex(fresh);
      for (const c of fresh) DEGREE.courses.push(c);
    } catch (e) {
      markMissing(ch.id);
      return;
    }
    markArrived(ch.id);
  });
}

function coursesInBand(programId, n) {
  return DEGREE.courses.filter(function (c) { return c.program === programId && c.band === n; });
}
function coursesInProgram(programId) {
  return DEGREE.courses.filter(function (c) { return c.program === programId; });
}
function courseUnits(c) { return TRACK_LESSONS[c.id] || []; }
/* A course keeps its labs in modules[].lab; a foundation track keeps them as units of
   type 'code'. Both mean "the parts a machine checks", so ask the units, not the shape. */
function courseLabs(c) {
  if (c && c.kind === 'track') {
    return courseUnits(c).filter(function (l) { return l.type === 'code' || l.type === 'project'; }).length;
  }
  return (c && c.modules ? c.modules : []).filter(function (m) { return m.lab; }).length;
}
function courseDone(c) {
  return courseUnits(c).reduce(function (n, l) { return n + (P.completed[l.id] ? 1 : 0); }, 0);
}
function courseComplete(c) {
  const u = courseUnits(c);
  return u.length > 0 && courseDone(c) === u.length;
}
function prereqState(c) {
  const list = (c.prereqs || []).map(function (id) {
    const pc = COURSE_OF[id];
    /* An unloaded prereq is not a met prereq. Defaulting to met would print the
       green "you have completed everything this course builds on" for a course whose
       prerequisite the app never saw. */
    return { id: id, title: pc ? pc.title : id, met: pc ? courseComplete(pc) : false, known: !!pc };
  });
  return { list: list, allMet: list.every(function (p) { return p.met; }) };
}
function degreeTotals(programId) {
  let units = 0, done = 0, credits = 0, earned = 0, labs = 0;
  const list = programId ? coursesInProgram(programId) : DEGREE.courses;
  for (const c of list) {
    const u = courseUnits(c);
    units += u.length;
    const d = courseDone(c);
    done += d;
    credits += c.credits || 0;
    if (courseComplete(c)) earned += c.credits || 0;
    labs += courseLabs(c);
  }
  return { units: units, done: done, credits: credits, earned: earned, labs: labs,
           courses: list.length,
           pct: units ? Math.round(done / units * 100) : 0 };
}

let P = { completed: {}, quiz: {}, code: {}, derive: {}, build: {}, blanks: {}, numeric: {}, match: {}, tune: {}, xp: 0, last: null, playground: null, activity: {}, name: '', railHidden: false };
/* The front page is the study plan for whichever programme you were last in. The
   dashboard that used to sit here summarised progress you could see on the screens
   themselves, and put a hop between opening the app and doing anything. */
function frontRoute() {
  const last = P.last && LESSON_INDEX[P.last] ? LESSON_INDEX[P.last] : null;
  const prog = (last && last.track && last.track.program) || defaultProgramId();
  return { view: 'degree', program: prog };
}
let route = { view: 'degree', program: '' };
const openTracks = {};
/* keyed "&lt;programId&gt;:&lt;band&gt;" — two programmes both have a band 1, and a bare
   number would open and close them together */
const openBands = {};
function bandKey(programId, n) { return programId + ':' + n; }

/* ---------- activity: real data behind the dashboard's charts ---------- */
function dayKey(d) {
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' +
    String(d.getDate()).padStart(2, '0');
}
function bumpActivity() {
  if (!P.activity) P.activity = {};
  const k = dayKey(new Date());
  P.activity[k] = (P.activity[k] || 0) + 1;
}
function activityOn(offsetDays) {
  const d = new Date();
  d.setDate(d.getDate() - offsetDays);
  return (P.activity && P.activity[dayKey(d)]) || 0;
}
/* consecutive days ending today (or yesterday, so an unfinished day keeps it) */
function streakDays() {
  if (!P.activity) return 0;
  let n = 0;
  const start = activityOn(0) > 0 ? 0 : (activityOn(1) > 0 ? 1 : -1);
  if (start < 0) return 0;
  for (let i = start; i < 400; i++) {
    if (activityOn(i) > 0) n++;
    else break;
  }
  return n;
}

function checksPassed() {
  let n = 0;
  for (const id in P.completed) {
    const info = LESSON_INDEX[id];
    if (info && info.lesson.tests) n += info.lesson.tests.length;
  }
  return n;
}

const TOTAL = { lessons: 0, tasks: 0, projects: 0 };
for (const t of TRACKS) for (const m of t.modules) for (const l of m.lessons) {
  TOTAL.lessons++;
  if (l.type === 'code') TOTAL.tasks++;
  if (l.type === 'project') TOTAL.projects++;
}

/* ---------- dom helpers ---------- */
function $(sel, root) { return (root || document).querySelector(sel); }
function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
function el(html) { const d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; }
function isMobile() {
  if (window.matchMedia) return window.matchMedia('(max-width: 980px)').matches;
  return window.innerWidth <= 980;
}

let toastTimer = null;
function toast(text, good) {
  const t = $('#toast');
  t.textContent = text;
  t.classList.toggle('good', !!good);
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(function () { t.classList.remove('show'); }, 2600);
}

/* ---------- persistence ---------- */
let saveChain = Promise.resolve();
function setSaveState(s, bad) {
  const e = $('#save-state');
  if (!e) return;
  e.textContent = s;
  e.classList.toggle('bad', !!bad);
  if (bad) e.title = 'Progress is not being stored in this browser — open Profile to export it';
  else e.removeAttribute('title');
}
let warnedNoStorage = false;
function warnNoStorage() {
  if (warnedNoStorage) return;
  warnedNoStorage = true;
  toast('Progress is not being saved — open Profile (avatar, bottom left)');
}
const saveSoon = debounce(function () { saveNow(); }, 900);
function saveNow() {
  setSaveState('Saving\u2026');
  P.updatedAt = Date.now();          /* the merge uses this to settle scalar fields */
  syncSoon();
  saveChain = saveChain.then(function () {
    return Store.save(P).then(function (ok) {
      setSaveState(ok ? 'Saved' : 'Not saved', !ok);
      if (!ok) warnNoStorage();
    });
  });
  return saveChain;
}

function level() { return Math.floor(P.xp / 150) + 1; }
function updateXp() {
  const xpEl = $('#xp-val');
  if (xpEl) xpEl.textContent = P.xp.toLocaleString('en-GB');
  const st = $('#streak-val');
  if (st) st.textContent = streakDays();
  const av = $('#avatar');
  if (av) {
    av.textContent = initials(P.name) || String(level());
    av.title = (P.name ? P.name + ' · ' : '') + 'Level ' + level() + ' · ' + P.xp + ' XP · open Profile';
  }
}
function completeLesson(id) {
  if (P.completed[id]) return false;
  P.completed[id] = true;
  const l = LESSON_INDEX[id].lesson;
  P.xp += XP[l.type] || 10;
  bumpActivity();
  updateXp();
  saveSoon();
  return true;
}
function trackDone(tid) {
  return (TRACK_LESSONS[tid] || []).reduce(function (n, l) { return n + (P.completed[l.id] ? 1 : 0); }, 0);
}
function firstIncomplete(tid) {
  for (const l of (TRACK_LESSONS[tid] || [])) if (!P.completed[l.id]) return l;
  return null;
}
function typeChip(type) {
  const label = { read: 'Read', sandbox: 'Sandbox', blanks: 'Fill in', match: 'Match', numeric: 'Solve', quiz: 'Quiz', tune: 'Tune', derive: 'Derive', build: 'Build', code: 'Code', project: 'Project' }[type] || type;
  return '<span class="chip ' + type + '">' + label + '</span>';
}

/* ---------- theme ---------- */
function effectiveTheme() {
  if (P.theme === 'dark' || P.theme === 'light') return P.theme;
  try { if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) return 'dark'; } catch (e) {}
  return 'light';
}
function applyTheme() {
  const t = effectiveTheme();
  /* :root carries the DARK palette and [data-theme=light] overrides it, so removing
     the attribute does not select light — it selects the default, which is dark.
     Light mode was unreachable: the button toggled, the glyph changed, the colours
     did not. Name the theme in both directions. */
  document.documentElement.setAttribute('data-theme', t === 'dark' ? 'dark' : 'light');
  const b = $('#theme-btn');
  if (b) {
    b.textContent = t === 'dark' ? '☀' : '☾';
    b.setAttribute('aria-label', t === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }
}

/* Stamped by build.mjs with the hash of the shell it produced.

   GitHub Pages serves index.html with Cache-Control: max-age=600 and cannot be told
   otherwise, and this app is that one file. So for ten minutes after a deploy a
   browser can keep serving the previous build, which reads exactly like a fix that
   did not ship. The app therefore asks, once, whether it is current. */
const BUILD_ID = '__BUILD_ID__';

function checkForNewBuild() {
  /* Unstamped (running from source) or opened from disk: there is nothing to ask. */
  if (BUILD_ID.slice(0, 2) === '__') return;
  if (!/^https?:$/.test(location.protocol)) return;
  fetch('version.json?t=' + Date.now(), { cache: 'no-store' })
    .then(function (r) { return r.ok ? r.json() : null; })
    .then(function (v) {
      if (!v || !v.build || v.build === BUILD_ID) return;
      /* One attempt per build, so a stale CDN edge cannot put us in a reload loop. */
      let tried = null;
      try { tried = sessionStorage.getItem('cw-reload'); } catch (e) { return; }
      if (tried === v.build) return;
      try { sessionStorage.setItem('cw-reload', v.build); } catch (e) { return; }
      /* A plain reload re-reads the same cached entry. A different query string is a
         different cache key, which is what actually fetches the new shell. */
      location.replace(location.pathname + '?b=' + v.build);
    })
    .catch(function () { /* offline, or no version.json: keep running what we have */ });
}

/* ---------- shell ---------- */
const NAV = [
  { id: 'degree', label: 'Study plan', view: 'degree',
    d: 'M12 3 2 8l10 5 10-5-10-5ZM2 13.5l10 5 10-5M2 18l10 5 10-5' },
  { id: 'programs', label: 'All programmes', view: 'programs',
    d: 'M4 6h16M4 12h16M4 18h10' },
  { id: 'progress', label: 'Progress', view: 'progress',
    d: 'M4 19.5V14M9.5 19.5V6M15 19.5v-8M20.5 19.5V9' },
  { id: 'play', label: 'Playground', view: 'play',
    d: 'M4.5 5h15v14h-15zM8 10l2.2 2.2L8 14.4M12.8 14.6H16' },
];

function renderShell() {
  $('#app').innerHTML =
    '<div class="blob a"></div><div class="blob b"></div>' +
    '<aside class="iconrail">' +
      '<button class="logo" id="brand" title="Codex Learn"><span>&lt;/&gt;</span></button>' +
      '<nav class="iconnav" id="iconnav" aria-label="Sections">' +
        NAV.map(function (n) {
          return '<button class="inav" data-nav="' + n.id + '" title="' + n.label + '" aria-label="' + n.label + '">' +
            '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" ' +
            'stroke-linecap="round" stroke-linejoin="round"><path d="' + n.d + '"/></svg></button>';
        }).join('') +
      '</nav>' +
      '<div class="rail-foot">' +
        '<div class="div"></div>' +
        '<div class="avatar" id="avatar" title="Level">1</div>' +
      '</div>' +
    '</aside>' +
    '<div class="frame">' +
      '<header class="topbar">' +
        '<button class="menu-btn" id="menu-btn" aria-label="Open curriculum">' +
          '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M3 5h14M3 10h14M3 15h14"/></svg>' +
        '</button>' +
        '<button class="tbtn rail-btn on" id="rail-btn" aria-pressed="true" aria-label="Toggle the curriculum panel">' +
          '<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round">' +
          '<rect x="2.5" y="3.5" width="15" height="13" rx="2.5"/><path d="M8 3.5v13"/></svg>' +
        '</button>' +
        '<div class="screen-id"><b id="screen-title">Dashboard</b><span id="screen-crumb"></span></div>' +
        '<span class="spacer"></span>' +
        '<label class="search">' +
          '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" style="color:var(--ink-4)"><circle cx="11" cy="11" r="7"/><path d="m16.5 16.5 4 4"/></svg>' +
          '<input id="omni" placeholder="Search lessons" autocomplete="off" aria-label="Search lessons">' +
          '<span class="kbd">⌘K</span>' +
        '</label>' +
        '<div class="metric streak" title="Consecutive days with a completed unit">' +
          '<span class="fl">🔥</span><b id="streak-val">0</b><span>day streak</span>' +
        '</div>' +
        '<div class="metric xp" title="Experience earned"><b id="xp-val">0</b><span>XP</span></div>' +
        '<button class="tbtn" id="theme-btn" aria-label="Switch theme">☾</button>' +
        '<span class="save-state" id="save-state"></span>' +
      '</header>' +
      '<div class="degrade" id="degrade" role="status" hidden></div>' +
      /* The runner's two bars. They live in the shell rather than inside <main>
         because every renderer owns main.innerHTML outright and would wipe them. */
      '<div class="runbar" id="runbar" hidden></div>' +
      '<div class="body" id="body">' +
        '<aside class="rail" id="rail" aria-label="Curriculum"></aside>' +
        '<main class="main" id="main"></main>' +
      '</div>' +
      '<div class="runfoot" id="runfoot" hidden></div>' +
    '</div>' +
    '<div class="scrim" id="scrim"></div>';

  $('#brand').addEventListener('click', function () { go(frontRoute()); });
  $all('[data-nav]').forEach(function (b) {
    b.addEventListener('click', function () {
      const item = NAV.find(function (n) { return n.id === b.dataset.nav; });
      if (item) go({ view: item.view });
    });
  });
  $('#avatar').addEventListener('click', function () { go({ view: 'profile' }); });
  $('#menu-btn').addEventListener('click', function () { toggleRail(); });
  $('#rail-btn').addEventListener('click', toggleRailPanel);
  window.addEventListener('resize', debounce(syncRailToggle, 150));
  const omni = $('#omni');
  omni.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') { runSearch(omni.value); }
    if (e.key === 'Escape') { omni.value = ''; omni.blur(); }
  });
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && (e.key === 'k' || e.key === 'K')) {
      e.preventDefault(); omni.focus(); omni.select();
    }
  });
  $('#theme-btn').addEventListener('click', function () {
    P.theme = effectiveTheme() === 'dark' ? 'light' : 'dark';
    applyTheme();
    saveSoon();
  });
  $('#scrim').addEventListener('click', function () { toggleRail(false); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') toggleRail(false);
  });
  document.addEventListener('click', function (e) {
    const btn = e.target.closest && e.target.closest('.cb-btn');
    if (!btn) return;
    const s = CB_STORE[btn.dataset.cb];
    if (!s) return;                       /* e.g. the drawer's own Hide button */
    const box = btn.closest('.cbx');
    if (btn.classList.contains('cb-copy')) copySnippet(s.code, btn);
    else if (btn.classList.contains('cb-open')) openInPlayground(s.code, s.lang);
    else if (btn.classList.contains('cb-run')) runSnippet(s, box, btn);
  });
  updateXp();
}
/* the desktop show/hide for the curriculum rail (the mobile drawer is toggleRail) */
/* Below this the editor column gets too narrow to write in, so a split workspace
   takes the curriculum column back (see the matching rule in the stylesheet) and the
   toggle steps aside rather than becoming a control that does nothing. */
function railCrowdedOut() {
  const split = route.view === 'play' ||
    (route.view === 'lesson' && LESSON_INDEX[route.id] &&
     /code|project/.test(LESSON_INDEX[route.id].lesson.type));
  return split && window.matchMedia('(min-width:981px) and (max-width:1199px)').matches;
}
function syncRailToggle() {
  const b = $('#rail-btn');
  if (!b) return;
  /* The planner carries its own majors column, so the rail is hidden there by
     renderRoute. The toggle has to agree, or it sits lit and labelled "Hide the
     curriculum panel" over a rail that is already gone — and clicking it silently
     persists railHidden onto every other screen. */
  const off = route.view === 'play' || route.view === 'degree' || railCrowdedOut();
  b.hidden = off;
  const shown = !P.railHidden;
  b.classList.toggle('on', shown);
  b.setAttribute('aria-pressed', shown ? 'true' : 'false');
  b.title = shown ? 'Hide the curriculum panel' : 'Show the curriculum panel';
}
function toggleRailPanel() {
  P.railHidden = !P.railHidden;
  $('#body').classList.toggle('no-rail',
    P.railHidden || route.view === 'play' || route.view === 'degree');
  syncRailToggle();
  saveSoon();
}
function toggleRail(force) {
  const rail = $('#rail'), scrim = $('#scrim');
  const open = (force === undefined) ? !rail.classList.contains('open') : !!force;
  rail.classList.toggle('open', open);
  scrim.classList.toggle('open', open);
}

/* ---------- rail ---------- */
/* A payload that did not arrive is the one failure the learner has to be told about,
   because every screen would otherwise just show smaller numbers and look fine. It
   lives in the shell rather than in a toast so it survives navigation, and it stays
   until a retry succeeds. */
function renderDegradeBanner() {
  const el = $('#degrade');
  if (!el) return;
  if (!MISSING_PROGRAMS.length) { el.hidden = true; el.innerHTML = ''; return; }
  const names = MISSING_PROGRAMS.map(function (id) {
    const pr = PROGRAM_OF[id];
    return esc((pr && (pr.short || pr.name)) || id);
  }).join(' and ');
  const fromFile = typeof location !== 'undefined' && location.protocol === 'file:';
  el.hidden = false;
  el.innerHTML =
    '<span class="dg-i">!</span>' +
    '<span class="dg-t"><b>' + names + '</b> could not be loaded, so its courses, units and ' +
      'credits are missing from every total on screen. Your progress is untouched.' +
      (fromFile
        ? ' This copy was opened straight from a file, and a browser will not fetch the ' +
          'course payloads from there. Serve this folder over http instead, or build ' +
          'the single-file copy with `node build.mjs` and open build/codewright.html, ' +
          'which has the whole catalog inside it.'
        : '') +
    '</span>' +
    (fromFile ? '' : '<button class="btn dark sm" id="dg-retry">Try again</button>');
  const btn = $('#dg-retry', el);
  if (btn) btn.addEventListener('click', async function () {
    btn.disabled = true;
    btn.textContent = 'Loading\u2026';
    await loadDegreeChunks();
    renderDegradeBanner();
    renderRail();
    go(route);
  });
}

function renderRail() {
  const rail = $('#rail');
  /* The foundation tracks used to head this rail as their own unlabelled section.
     They are Computer Science's band 0 now, so they are drawn there, once. */
  let h = '';

  for (const pr of PROGRAMS) {
    if (!coursesInProgram(pr.id).filter(function (c) { return c.kind !== 'track'; }).length) {
      /* A programme whose payload failed keeps its heading and says so. Dropping the
         section entirely reads as "not written yet", which is the opposite of true. */
      if (programMissing(pr.id)) {
        h += '<div class="rail-sec">' + esc(pr.short || pr.name) + '</div>' +
          '<div class="rail-miss">could not be loaded</div>';
      }
      continue;
    }
    h += '<div class="rail-sec">' + esc(pr.short || pr.name) + '</div>';
    for (const y of pr.bands) {
      const list = coursesInBand(pr.id, y.n);
      if (!list.length) continue;
      const open = !!openBands[bandKey(pr.id, y.n)];
      const doneC = list.filter(courseComplete).length;
      h += '<div class="rail-track' + (open ? ' open' : '') + '">' +
        '<button data-band="' + y.n + '" data-program="' + esc(pr.id) + '">' +
          '<span class="t-icon" style="--tt:' + y.tint + '">' + y.icon + '</span>' +
          '<span class="t-name">' + esc(bandLabel(pr, y.n)) + '</span>' +
          '<span class="t-pct">' + doneC + '/' + list.length + '</span>' +
        '</button>';
      if (open) {
        h += '<div class="rail-module">';
        for (const c of list) {
          const units = courseUnits(c).length;
          const d = courseDone(c);
          if (c.kind === 'track') {
            /* A track keeps its lessons here rather than behind a page: they are the
               unit of work, the same way a course's modules are. */
            const topen = !!openTracks[c.id];
            h += '<div class="rail-sub' + (topen ? ' open' : '') + '" data-track="' + esc(c.id) + '">' +
              '<button class="rail-course" data-toggle="' + esc(c.id) + '">' +
                '<span class="cid">' + (topen ? UNI.down : UNI.right) + '</span>' +
                '<span class="gmark ' + (units && d === units ? 'done' : (d > 0 ? 'part' : '')) + '"></span>' +
                '<span class="ttl">' + esc(c.title) + '</span>' +
                '<span class="lk">' + d + '/' + units + '</span>' +
              '</button>';
            if (topen) {
              c.modules.forEach(function (m) {
                h += '<div class="rail-module sub"><h4>' + esc(m.title) + '</h4>';
                for (const l of m.lessons) {
                  const la = route.view === 'lesson' && route.id === l.id;
                  const lm = P.completed[l.id] ? 'done' : (la ? 'now' : '');
                  h += '<button class="rail-lesson' + (la ? ' active' : '') + '" data-lesson="' + esc(l.id) + '">' +
                    '<span class="num">' + l.num + '</span>' +
                    '<span class="gmark ' + lm + '"></span>' +
                    '<span class="ttl">' + esc(l.title) + '</span>' +
                  '</button>';
                }
                h += '</div>';
              });
            }
            h += '</div>';
            continue;
          }
          const active = route.view === 'course' && route.id === c.id;
          const mark = units && d === units ? 'done' : (d > 0 ? 'part' : (active ? 'now' : ''));
          h += '<button class="rail-course' + (active ? ' active' : '') + '" data-course="' + c.id + '">' +
            '<span class="cid">' + esc(c.id) + '</span>' +
            '<span class="gmark ' + mark + '"></span>' +
            '<span class="ttl">' + esc(c.title) + '</span>' +
            '<span class="lk">' + d + '/' + units + '</span>' +
          '</button>';
        }
        h += '</div>';
      }
      h += '</div>';
    }
  }

  rail.innerHTML = h;
  $all('[data-toggle]', rail).forEach(function (b) {
    b.addEventListener('click', function () {
      const id = b.dataset.toggle;
      openTracks[id] = !openTracks[id];
      renderRail();
    });
  });
  $all('[data-band]', rail).forEach(function (b) {
    b.addEventListener('click', function () {
      const k = bandKey(b.dataset.program, +b.dataset.band);
      openBands[k] = !openBands[k];
      renderRail();
    });
  });
  $all('[data-lesson]', rail).forEach(function (b) {
    b.addEventListener('click', function () {
      toggleRail(false);
      go({ view: 'lesson', id: b.dataset.lesson });
    });
  });
  $all('[data-course]', rail).forEach(function (b) {
    b.addEventListener('click', function () {
      toggleRail(false);
      const c = COURSE_OF[b.dataset.course];
      go(c && c.kind === 'track'
        ? { view: 'track', track: b.dataset.course }
        : { view: 'course', id: b.dataset.course });
    });
  });
}

/* ---------- routing ---------- */
let teardown = null;
/* Where the reader was on each screen. Coming back to material — from the
   Playground, from the next lesson, from anywhere — should land where they left
   off, not at the top. */
const SCROLL_MEM = {};
function routeKey(r) { return r ? r.view + ':' + (r.id || r.track || r.program || '') : ''; }
function scrollHost() { return $('#task-pane') || $('#main'); }
function rememberScroll() {
  const host = scrollHost();
  if (host && route) SCROLL_MEM[routeKey(route)] = host.scrollTop;
}

function go(r) {
  if (teardown) { try { teardown(); } catch (e) {} teardown = null; }
  rememberScroll();
  route = r;
  if (r.top) delete SCROLL_MEM[routeKey(r)];   /* re-entry that must start at the top */
  if (r.view === 'lesson') {
    const info = LESSON_INDEX[r.id];
    if (!info) { route = frontRoute(); }
    else {
      if (info.track.kind === 'course') openBands[bandKey(info.track.program, info.track.band)] = true;
      else openTracks[info.track.id] = true;
      P.last = r.id;
      saveSoon();
    }
  }
  if (r.view === 'track') openTracks[r.track] = true;
  if (r.view === 'course' && COURSE_OF[r.id]) {
    const cc = COURSE_OF[r.id];
    openBands[bandKey(cc.program, cc.band)] = true;
  }
  renderRail();

  /* icon-rail active state */
  const section = (route.view === 'course' || route.view === 'programs') ? 'degree'
    : (route.view === 'track' || route.view === 'lesson') ? navSectionFor(route)
    : route.view;
  $all('[data-nav]').forEach(function (b) {
    b.classList.toggle('active', b.dataset.nav === section);
  });

  /* header identity */
  const meta = screenMeta(route);
  $('#screen-title').textContent = meta.title;
  $('#screen-crumb').textContent = meta.crumb;

  /* A task is still part of a track: going from the 1.1 reading to the 1.2 exercise
     must not take the curriculum away, or there is no way back to the material.
     Only the Playground — which belongs to no track — owns the full width.
     Everything else is the reader's own choice, kept in P.railHidden. */
  const isSplit = route.view === 'play' ||
    (route.view === 'lesson' && /code|project/.test(LESSON_INDEX[route.id].lesson.type));
  /* The planner carries its own majors column, which is what the curriculum rail
     would otherwise be doing — two lists of the same thing side by side. */
  const hideRail = route.view === 'play' || route.view === 'degree' ||
    !!focusLesson(route) || !!P.railHidden;
  $('#body').classList.toggle('no-rail', hideRail);
  $('#body').classList.toggle('split', isSplit);
  syncRailToggle();

  const main = $('#main');
  main.classList.toggle('split', isSplit);
  main.classList.toggle('bleed', route.view === 'degree');
  main.scrollTop = 0;
  if (route.view === 'track') renderTrack(main, TRACK_OF[route.track]);
  else if (route.view === 'programs') renderPrograms(main);
  else if (route.view === 'degree') renderDegree(main, route.program);
  else if (route.view === 'course') renderCourse(main, COURSE_OF[route.id]);
  else if (route.view === 'progress') renderProgress(main);
  else if (route.view === 'profile') renderProfile(main);
  else if (route.view === 'play') renderPlayground(main);
  else if (route.view === 'lesson') {
    const l = LESSON_INDEX[route.id].lesson;
    if (l.type === 'read') renderRead(main, l);
    else if (l.type === 'quiz') renderQuiz(main, l);
    else if (l.type === 'sandbox') renderSandbox(main, l);
    else if (l.type === 'derive') renderDerive(main, l);
    else if (l.type === 'build') renderBuild(main, l);
    else if (l.type === 'blanks') renderBlanks(main, l);
    else if (l.type === 'numeric') renderNumeric(main, l);
    else if (l.type === 'match') renderMatch(main, l);
    else if (l.type === 'tune') renderTune(main, l);
    else renderCode(main, l);
  }

  paintRunner(focusLesson(route));

  const host = scrollHost();
  if (host) host.scrollTop = SCROLL_MEM[routeKey(route)] || 0;
}

/* Which unit kinds become the screen.
   `read` is an article and `code`/`project` are an IDE beside a task pane; both
   want their chrome. Everything else is a question, and a question the learner has
   to hunt for halfway down a scrolling page is the thing that kept reading as
   "there are only programming tasks here". */
const FOCUS_TYPES = { quiz: 1, blanks: 1, match: 1, numeric: 1, tune: 1, derive: 1, build: 1, sandbox: 1 };
function focusLesson(r) {
  if (!r || r.view !== 'lesson') return null;
  const info = LESSON_INDEX[r.id];
  if (!info || !FOCUS_TYPES[info.lesson.type]) return null;
  return info;
}

/* The units of the module the learner is inside, in order. That is the run: a
   handful of questions on one idea, not the whole course. */
function moduleRun(info) {
  const flat = TRACK_LESSONS[info.lesson.trackId] || [];
  return flat.filter(function (x) {
    const xi = LESSON_INDEX[x.id];
    return xi && xi.track === info.track && xi.mi === info.mi;
  });
}

function paintRunner(info) {
  const bar = $('#runbar'), foot = $('#runfoot'), main = $('#main');
  if (!info) {
    $('#app').classList.remove('focus');
    bar.hidden = true; foot.hidden = true; bar.innerHTML = ''; foot.innerHTML = '';
    return;
  }
  $('#app').classList.add('focus');

  const run = moduleRun(info);
  const at = run.indexOf(info.lesson);
  bar.hidden = false;
  bar.innerHTML =
    '<button class="rb-x" id="rb-x" aria-label="Leave this run" title="Leave this run">\u2715</button>' +
    '<div class="rb-segs">' + run.map(function (u, i) {
      return '<i class="' + (P.completed[u.id] ? 'on' : (i === at ? 'now' : '')) + '"' +
        ' title="' + esc(u.title) + '"></i>';
    }).join('') + '</div>' +
    '<span class="rb-who">' + esc(info.track.id) + ' \u00b7 ' + esc(info.module.title) + '</span>' +
    '<span class="rb-at">' + (at + 1) + '/' + run.length + '</span>';

  $('#rb-x').addEventListener('click', function () {
    go(info.track.kind === 'course'
      ? { view: 'course', id: info.track.id }
      : { view: 'track', track: info.track.id });
  });

  /* Pull the answer controls out of the article and into a bar that is always on
     screen. Moving the nodes keeps their listeners, which were wired by the
     renderer moments ago; rebuilding buttons here would silently break every
     Check in the app. */
  foot.hidden = false;
  foot.innerHTML = '';
  const artfoot = $('.article-foot', main);
  const done = artfoot ? artfoot.querySelector('.done-note') : null;
  if (done) foot.appendChild(done);
  const sp = document.createElement('span');
  sp.className = 'spacer';
  foot.appendChild(sp);
  /* Each renderer names its own action row. Numeric, match and tune share .q-acts;
     fill-in, build and derive do not. Missing one leaves its Check stranded halfway
     down the page, which is the exact problem focus mode exists to fix. */
  const acts = $('.q-acts', main) || $('.blk-acts', main) ||
    $('.build-acts', main) || $('.dv-acts', main);
  if (acts) { acts.classList.add('moved'); foot.appendChild(acts); }
  const nx = artfoot ? artfoot.querySelector('#nav-next') : null;
  if (nx) { nx.classList.add('run-next'); foot.appendChild(nx); }
  if (artfoot) artfoot.remove();
  if (!foot.children.length || (foot.children.length === 1 && foot.firstChild === sp)) foot.hidden = true;
}

function navSectionFor(r) {
  if (r.view === 'degree' || r.view === 'course' || r.view === 'track') return 'degree';
  if (r.view === 'programs') return 'programs';
  if (r.view === 'progress') return 'progress';
  if (r.view === 'play') return 'play';
  if (r.view === 'profile') return 'profile';
  if (r.view === 'lesson') return 'degree';
  return 'degree';
}

function screenMeta(r) {
  if (r.view === 'programs') {
    return { title: 'Programmes', crumb: PROGRAMS.length + ' majors · ' + DEGREE.courses.length + ' courses' };
  }
  if (r.view === 'degree') {
    const dpr = PROGRAM_OF[r.program] || PROGRAMS[0];
    const dn = dpr && programMissing(dpr.id) ? null : (dpr ? coursesInProgram(dpr.id).length : 0);
    return { title: dpr ? (dpr.short || dpr.name) : 'Programme',
             crumb: dpr ? ((dpr.bands || []).length + ' ' + (dpr.bandNoun || 'Year').toLowerCase() + 's · ' +
               (dn === null ? 'not loaded' : dn + ' courses')) : '' };
  }
  if (r.view === 'progress') return { title: 'Progress', crumb: 'Level ' + level() + ' · ' + P.xp.toLocaleString('en-GB') + ' XP' };
  if (r.view === 'play') return { title: 'Playground', crumb: 'Scratchpad · nothing is checked' };
  if (r.view === 'profile') return { title: 'Profile', crumb: (P.name || 'Unnamed learner') + ' · Level ' + level() };
  if (r.view === 'track') {
    const t = TRACK_OF[r.track];
    return { title: t ? t.name : 'Track', crumb: t ? trackDone(t.id) + ' of ' + TRACK_LESSONS[t.id].length + ' complete' : '' };
  }
  if (r.view === 'course') {
    const c = COURSE_OF[r.id];
    const cpr = c ? programOf(c) : null;
    return { title: c ? c.title : 'Course',
             crumb: c ? c.id + ' · ' + bandLabel(cpr, c.band) + ' · ' + c.level : '' };
  }
  if (r.view === 'lesson') {
    const info = LESSON_INDEX[r.id];
    if (!info) return { title: 'Lesson', crumb: '' };
    return { title: info.lesson.title, crumb: (info.track.kind === 'course' ? info.track.id : info.track.name) + ' · ' + info.module.title };
  }
  return { title: 'Codex Learn', crumb: '' };
}

/* ---------- search ---------- */
function runSearch(q) {
  q = String(q || '').trim().toLowerCase();
  if (!q) return;
  const hits = [];
  for (const id in LESSON_INDEX) {
    const info = LESSON_INDEX[id];
    const hay = (info.lesson.title + ' ' + info.track.name + ' ' + info.module.title).toLowerCase();
    if (hay.indexOf(q) !== -1) hits.push({ id: id, title: info.lesson.title });
  }
  for (const c of DEGREE.courses) {
    if ((c.id + ' ' + c.title + ' ' + c.summary).toLowerCase().indexOf(q) !== -1) {
      hits.unshift({ course: c.id, title: c.id + ' · ' + c.title });
    }
  }
  if (!hits.length) {
    /* "Nothing matches" about a course the learner worked through last week is not a
       claim the search is in any position to make while part of the catalog is absent. */
    toast(MISSING_PROGRAMS.length
      ? 'No match in what has loaded — part of the catalog is missing'
      : 'Nothing matches “' + q + '”');
    return;
  }
  const top = hits[0];
  toast(hits.length + ' match' + (hits.length > 1 ? 'es' : '') + ' — opening ' + top.title);
  if (top.course) go({ view: 'course', id: top.course });
  else go({ view: 'lesson', id: top.id });
}
function lessonNav(l) {
  const flat = TRACK_LESSONS[l.trackId];
  const i = flat.indexOf(l);
  return { prev: i > 0 ? flat[i - 1] : null, next: i < flat.length - 1 ? flat[i + 1] : null };
}
function crumbHtml(l) {
  const info = LESSON_INDEX[l.id];
  if (info.track.kind === 'course') {
    const lpr = programOf(info.track);
    return '<div class="crumb"><button data-go="home">Study plan</button><span>›</span>' +
      '<button data-go="degree">' + esc(lpr ? (lpr.short || lpr.name) : 'Programmes') + '</button><span>›</span>' +
      '<button data-go="course">' + esc(info.track.id) + '</button><span>›</span>' +
      '<span>' + esc(info.module.title) + '</span></div>';
  }
  return '<div class="crumb"><button data-go="home">Study plan</button><span>›</span>' +
    '<button data-go="track">' + esc(info.track.name) + '</button><span>›</span><span>' + esc(info.module.title) + '</span></div>';
}
function wireCrumb(root, l) {
  const info = LESSON_INDEX[l.id];
  $all('[data-go]', root).forEach(function (b) {
    b.addEventListener('click', function () {
      const k = b.dataset.go;
      if (k === 'home') go(frontRoute());
      else if (k === 'degree') go({ view: 'degree', program: info.track.program });
      else if (k === 'course') go({ view: 'course', id: info.track.id });
      else go({ view: 'track', track: info.track.id });
    });
  });
}

/* ---------- shared bits in the design's language ---------- */
function ringHtml(pct, colorVar) {
  const r = 15.5, circ = 2 * Math.PI * r;
  const on = Math.max(0, Math.min(100, pct)) / 100 * circ;
  return '<div class="ringwrap"><svg width="38" height="38" viewBox="0 0 38 38">' +
    '<circle class="trk" cx="19" cy="19" r="' + r + '" fill="none" stroke-width="3"/>' +
    '<circle class="val" cx="19" cy="19" r="' + r + '" fill="none" stroke-width="3" stroke-linecap="round"' +
    ' stroke-dasharray="' + on.toFixed(1) + ' ' + circ.toFixed(1) + '"' +
    (colorVar ? ' style="stroke:' + colorVar + '"' : '') + '/></svg>' +
    '<b>' + Math.round(pct) + '</b></div>';
}
function sparkHtml(values) {
  const max = Math.max(1, ...values);
  return '<div class="spark">' + values.map(function (v, i) {
    const h = Math.max(2, Math.round(v / max * 26));
    return '<i class="' + (i === values.length - 1 && v > 0 ? 'hi' : '') + '" style="height:' + h +
      'px;animation-delay:' + (i * 40) + 'ms"></i>';
  }).join('') + '</div>';
}
function statCard(label, value, unit, delta, spark) {
  return '<div class="stat">' +
    '<div class="top"><span class="lbl">' + esc(label) + '</span>' +
    (delta ? '<span class="delta">' + esc(delta) + '</span>' : '') + '</div>' +
    '<div class="val"><b>' + esc(String(value)) + '</b>' + (unit ? '<span>' + esc(unit) + '</span>' : '') + '</div>' +
    (spark ? sparkHtml(spark) : '') +
  '</div>';
}

function typeChipText(type) {
  return { read: 'Reading', sandbox: 'Sandbox', blanks: 'Fill in', match: 'Symbol drill', numeric: 'Find the value', quiz: 'Quiz', tune: 'Hit the target', derive: 'Derivation', build: 'Circuit', code: 'Lab', project: 'Capstone' }[type] || type;
}

/* ---------- progress ---------- */
function renderProgress(main) {
  const dt = degreeTotals();
  let allUnits = TOTAL.lessons + dt.units;
  let doneUnits = 0;
  for (const id in P.completed) if (LESSON_INDEX[id]) doneUnits++;
  const pct = allUnits ? Math.round(doneUnits / allUnits * 100) : 0;
  const toNext = 150 - (P.xp % 150);

  /* 13 weeks of real activity, most recent column last */
  let grid = '';
  for (let row = 0; row < 7; row++) {
    for (let col = 12; col >= 0; col--) {
      const offset = col * 7 + (6 - row);
      const n = activityOn(offset);
      const a = n === 0 ? 0.06 : n < 2 ? 0.22 : n < 4 ? 0.48 : n < 7 ? 0.78 : 1;
      const bg = n === 0 ? 'rgba(255,255,255,0.06)' : 'rgba(199,247,81,' + a + ')';
      grid += '<div title="' + n + ' on that day" style="aspect-ratio:1;border-radius:3px;background:' + bg + '"></div>';
    }
  }

  /* One row per band of each programme. The foundation tracks used to get their own
     five rows on top of this; they are band 0 of Computer Science now, so those rows
     were the same units counted twice. */
  const mastery = PROGRAMS.flatMap(function (pr) { return pr.bands.map(function (y) {
    const list = coursesInBand(pr.id, y.n);
    const u = list.reduce(function (s, c) { return s + courseUnits(c).length; }, 0);
    const d = list.reduce(function (s, c) { return s + courseDone(c); }, 0);
    return { name: (pr.short || pr.name) + ' · ' + bandLabel(pr, y.n) + ' — ' + y.title,
             done: d, total: u, pct: u ? d / u * 100 : 0 };
  }); }).filter(function (m) { return m.total > 0; });

  main.innerHTML = '<div class="page">' +
    '<div style="display:flex;align-items:center;gap:22px;margin-bottom:30px;flex-wrap:wrap">' +
      '<div class="ring" style="--pct:' + pct + '"><div><b>' + pct + '%</b><span>complete</span></div></div>' +
      '<div style="flex:1;min-width:240px">' +
        '<div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">' +
          '<h1 style="margin:0;font-size:28px;font-weight:600;letter-spacing:-0.03em">Your progress</h1>' +
          '<span class="chip done">Level ' + level() + '</span>' +
        '</div>' +
        '<p style="margin:8px 0 0;font-size:13.5px;color:var(--ink-3)">' +
          P.xp.toLocaleString('en-GB') + ' XP · ' + toNext + ' XP to level ' + (level() + 1) +
          ' · ' + streakDays() + '-day streak</p>' +
        '<div class="bar" style="margin-top:12px;max-width:340px"><i style="width:' +
          Math.round((P.xp % 150) / 150 * 100) + '%"></i></div>' +
      '</div>' +
      '<div style="display:flex;gap:26px;padding-left:26px;border-left:1px solid var(--line)">' +
        '<div><div style="font-size:24px;font-weight:600;letter-spacing:-0.03em">' + doneUnits + '</div>' +
          '<div class="lbl" style="font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-4);margin-top:4px">Units</div></div>' +
        '<div><div style="font-size:24px;font-weight:600;letter-spacing:-0.03em">' + checksPassed() + '</div>' +
          '<div style="font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-4);margin-top:4px">Checks</div></div>' +
        '<div><div style="font-size:24px;font-weight:600;letter-spacing:-0.03em">' + dt.earned + '</div>' +
          '<div style="font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-4);margin-top:4px">Credits</div></div>' +
      '</div>' +
    '</div>' +

    '<div style="display:grid;grid-template-columns:1fr 340px;gap:22px;align-items:start" class="home-cols">' +
      '<div style="display:flex;flex-direction:column;gap:22px">' +
        '<div>' +
          '<div class="section-h"><h2>Activity</h2><span>last 13 weeks</span></div>' +
          '<div class="panel">' +
            '<div style="display:grid;grid-template-columns:repeat(13,1fr);grid-auto-rows:1fr;gap:5px">' + grid + '</div>' +
            '<div style="display:flex;align-items:center;gap:8px;margin-top:16px;font-family:var(--mono);font-size:10.5px;color:var(--ink-4)">' +
              '<span>13 weeks</span><div style="flex:1"></div><span>less</span>' +
              '<div style="display:flex;gap:3px">' +
                ['rgba(255,255,255,0.06)', 'rgba(199,247,81,0.22)', 'rgba(199,247,81,0.48)', 'rgba(199,247,81,0.78)', '#C7F751']
                  .map(function (c) { return '<div style="width:10px;height:10px;border-radius:3px;background:' + c + '"></div>'; }).join('') +
              '</div><span>more</span>' +
            '</div>' +
          '</div>' +
        '</div>' +
        '<div>' +
          '<div class="section-h"><h2>Mastery</h2><span>every year of every programme</span></div>' +
          '<div class="panel" style="display:flex;flex-direction:column;gap:16px">' +
            mastery.map(function (m) {
              return '<div style="display:flex;flex-direction:column;gap:8px">' +
                '<div style="display:flex;justify-content:space-between;align-items:baseline">' +
                  '<span style="font-size:13.5px;font-weight:600">' + esc(m.name) + '</span>' +
                  '<span style="font-family:var(--mono);font-size:11.5px;color:var(--ink-3)">' + m.done + ' / ' + m.total + '</span>' +
                '</div><div class="bar" style="height:6px"><i style="width:' + m.pct.toFixed(1) + '%"></i></div></div>';
            }).join('') +
          '</div>' +
        '</div>' +
      '</div>' +
      '<div>' +
        '<div class="section-h"><h2>Milestones</h2><span>earned by doing</span></div>' +
        '<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px">' +
          badgeSet().map(function (b) {
            return '<div class="badge' + (b.unknown ? ' unknown' : '') + '"' +
              (b.unknown ? ' title="Cannot be checked while part of the catalog is missing"' : '') +
              ' style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 10px;border-radius:14px;' +
              'border:1px solid ' + (b.on ? 'var(--lime-30)' : 'var(--line)') + ';background:' + (b.on ? 'var(--lime-08)' : 'var(--surface-2)') +
              (b.on ? ';animation:popIn .4s var(--pop) both' : '') + '">' +
              '<span style="font-size:20px;' + (b.on ? '' : 'filter:grayscale(1);opacity:.4') + '">' + (b.unknown ? '?' : b.glyph) + '</span>' +
              '<span style="font-size:11.5px;font-weight:600;text-align:center;line-height:1.3;color:' +
              (b.on ? 'var(--lime)' : 'var(--ink-4)') + '">' + esc(b.name) + '</span></div>';
          }).join('') +
        '</div>' +
      '</div>' +
    '</div>' +
  '</div>';
}

/* ---------- sync driver ----------
   One rule: every sync is a push that returns the merged document, and the client
   adopts what comes back. That makes each save a convergence point, so two machines
   editing the same account end up agreeing without any conflict UI. */
let syncState = { at: 0, busy: false, error: '', rev: 0 };
let adopting = false;

function recomputeXp() {
  /* XP is a function of what has been completed, so it is derived rather than merged.
     A unit this build does not know about (an older or newer catalog) still counts. */
  let xp = 0;
  for (const id in P.completed) {
    if (!P.completed[id]) continue;
    const info = LESSON_INDEX[id];
    xp += info ? (XP[info.lesson.type] || 10) : 10;
  }
  /* A programme whose payload did not arrive is a different case from an unknown
     unit: those lessons exist and their real value is known, so recomputing here
     would flatten every one of them to the 10-point fallback and then persist and
     sync the deflated figure. Hold the stored number instead — it is the correct one,
     and the next load with the whole catalog recomputes it exactly. */
  if (MISSING_PROGRAMS.length && xp < (P.xp || 0)) return;
  P.xp = xp;
}

function adopt(progress) {
  if (!progress || typeof progress !== 'object') return;
  adopting = true;
  try {
    P = Object.assign({ completed: {}, quiz: {}, code: {}, derive: {}, build: {}, blanks: {}, numeric: {}, match: {}, tune: {}, xp: 0, last: null, playground: null,
                        activity: {}, name: '', railHidden: false }, progress);
    if (!P.activity || typeof P.activity !== 'object') P.activity = {};
    recomputeXp();
    applyTheme();
    updateXp();
    renderRail();
  } finally { adopting = false; }
}

async function syncNow(opts) {
  if (!Sync.signedIn() || syncState.busy) return null;
  syncState.busy = true;
  syncState.error = '';
  if (opts && opts.paint) opts.paint();
  try {
    P.updatedAt = P.updatedAt || Date.now();
    const r = await Sync.push(P);
    adopt(r.progress);
    syncState.at = Date.now();
    syncState.rev = r.rev || 0;
    Store.save(P);                 /* keep the local copy in step with the merge */
    return r;
  } catch (e) {
    syncState.error = String((e && e.message) || e);
    return null;
  } finally {
    syncState.busy = false;
    if (opts && opts.paint) opts.paint();
    if (route.view === 'profile') renderProfile($('#main'));
  }
}

const syncSoon = debounce(function () {
  if (adopting || !Sync.signedIn()) return;
  syncNow();
}, 2500);

function initials(name) {
  const parts = String(name || '').trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return '';
  return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : '')).toUpperCase();
}

/* ---------- profile ----------
   There is no server behind this app, so there is no account to sign in to. What the
   learner actually needs is what an account would have given them: to know whether
   their progress is really being kept, and to be able to move it. */
function storageNote() {
  const st = Store.status();
  if (st.mode === 'backend') {
    return { ok: true, head: 'Saved to your Claude storage',
      body: 'Progress follows this page wherever you open it.' };
  }
  if (st.mode === 'local') {
    return { ok: true, head: 'Saved in this browser',
      body: 'Progress is kept on this device, in this browser, under ' + Store.key + '. ' +
            'It will not follow you to another browser or machine \u2014 use Export below for that. ' +
            'Clearing site data erases it.' };
  }
  return { ok: false, head: 'Not being saved',
    body: st.fromFile
      ? 'This page was opened straight from a file, and browsers block storage for file:// pages. ' +
        'Serve it over http instead (node build.mjs, then node tools/serve.mjs, then open localhost:4173) ' +
        'or keep working here and press Export before you close the tab.'
      : 'This browser is refusing to store site data' + (st.error ? ' (' + st.error + ')' : '') + '. ' +
        'A private window or a blocked-cookies setting will do this. ' +
        'Everything still works, but it is gone when you close the tab \u2014 press Export first.' };
}

function progressSnapshot() {
  return { format: 'codex-learn-progress', version: 1, exported: new Date().toISOString(), progress: P };
}
function exportProgress() {
  try {
    const text = JSON.stringify(progressSnapshot(), null, 2);
    const url = URL.createObjectURL(new Blob([text], { type: 'application/json' }));
    const a = document.createElement('a');
    a.href = url;
    a.download = 'codex-learn-progress-' + dayKey(new Date()) + '.json';
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(url); a.remove(); }, 0);
    toast('Progress file downloaded', true);
  } catch (e) {
    toast('Could not export: ' + String((e && e.message) || e));
  }
}
function importProgress(file) {
  const fr = new FileReader();
  fr.onerror = function () { toast('Could not read that file'); };
  fr.onload = function () {
    let data;
    try { data = JSON.parse(String(fr.result)); }
    catch (e) { toast('That file is not valid JSON'); return; }
    const inc = (data && data.progress) ? data.progress : data;
    if (!inc || typeof inc !== 'object' || typeof inc.completed !== 'object') {
      toast('That does not look like a Codex Learn progress file');
      return;
    }
    P = Object.assign({ completed: {}, quiz: {}, code: {}, derive: {}, build: {}, blanks: {}, numeric: {}, match: {}, tune: {}, xp: 0, last: null, playground: null,
                        activity: {}, name: '', railHidden: false }, inc);
    if (!P.activity || typeof P.activity !== 'object') P.activity = {};
    applyTheme();
    updateXp();
    renderRail();
    saveNow();
    go({ view: 'profile' });
    const n = Object.keys(P.completed).length;
    toast('Restored ' + n + ' completed unit' + (n === 1 ? '' : 's'), true);
  };
  fr.readAsText(file);
}
function resetProgress() {
  P = { completed: {}, quiz: {}, code: {}, derive: {}, build: {}, blanks: {}, numeric: {}, match: {}, tune: {}, xp: 0, last: null, playground: null,
        activity: {}, name: P.name, railHidden: P.railHidden, theme: P.theme };
  updateXp();
  renderRail();
  saveNow();
  go({ view: 'profile' });
  toast('Progress cleared');
}

function relTime(ms) {
  if (!ms) return 'never';
  const d = Math.round((Date.now() - ms) / 1000);
  if (d < 45) return 'just now';
  if (d < 90) return 'a minute ago';
  if (d < 3600) return Math.round(d / 60) + ' minutes ago';
  if (d < 7200) return 'an hour ago';
  if (d < 86400) return Math.round(d / 3600) + ' hours ago';
  return Math.round(d / 86400) + ' days ago';
}

let serverUp = null;          /* null = not probed yet */

function accountCardHtml() {
  const inUse = Sync.signedIn();
  const u = Sync.user();

  if (inUse) {
    const line = syncState.busy ? 'Syncing\u2026'
      : syncState.error ? syncState.error
      : 'Last synced ' + relTime(syncState.at);
    return '<div class="pcard ' + (syncState.error ? 'warn' : 'good') + '">' +
      '<div class="pcard-h"><span class="dot"></span><b>Signed in as ' + esc(u ? u.email : 'your account') + '</b></div>' +
      '<p>Progress syncs to your account, so any machine you sign in on picks up where ' +
        'the last one left off. Finished units, quiz scores and saved code are merged rather ' +
        'than overwritten, so working on two machines never loses either side. ' +
        '<span class="sync-line">' + esc(line) + '</span></p>' +
      '<div class="pcard-acts">' +
        '<button class="btn dark" id="acc-sync"' + (syncState.busy ? ' disabled' : '') + '>Sync now</button>' +
        '<button class="btn dark" id="acc-out">Sign out</button>' +
      '</div>' +
    '</div>';
  }

  if (serverUp === false) {
    return '<div class="pcard">' +
      '<div class="pcard-h"><b>Sync across devices</b></div>' +
      '<p>No sync server is reachable from here, so this copy is local-only \u2014 which is a ' +
        'perfectly good way to use it. To sync, run <code>node server/server.mjs</code> beside ' +
        'the build and open the address it prints. If the server is somewhere else, give its ' +
        'address here.</p>' +
      '<div class="pcard-acts">' +
        '<input class="acc-in" id="acc-base" placeholder="http://localhost:4173" value="' + esc(Sync.base()) + '">' +
        '<button class="btn dark" id="acc-base-save">Use this server</button>' +
      '</div>' +
    '</div>';
  }

  return '<div class="pcard">' +
    '<div class="pcard-h"><b>Sync across devices</b></div>' +
    '<p>Create an account to carry your progress between machines. Your email is only ' +
      'an identifier \u2014 nothing is sent anywhere else, and the password is stored as a ' +
      'salted scrypt hash, never in the clear.</p>' +
    '<div class="acc-form">' +
      '<input class="acc-in" id="acc-email" type="email" autocomplete="username" placeholder="you@example.com">' +
      '<input class="acc-in" id="acc-pw" type="password" autocomplete="current-password" placeholder="Password (8+ characters)">' +
    '</div>' +
    '<div class="pcard-acts">' +
      '<button class="btn success" id="acc-in">Sign in</button>' +
      '<button class="btn dark" id="acc-new">Create account</button>' +
      '<span class="prof-warn" id="acc-msg"></span>' +
    '</div>' +
  '</div>';
}

function wireAccountCard(main) {
  const repaint = function () { if (route.view === 'profile') renderProfile($('#main')); };

  const sync = $('#acc-sync', main);
  if (sync) sync.addEventListener('click', function () { syncNow(); repaint(); });

  const out = $('#acc-out', main);
  if (out) out.addEventListener('click', async function () {
    await Sync.logout();
    toast('Signed out \u2014 progress stays on this device');
    repaint();
  });

  const baseSave = $('#acc-base-save', main);
  if (baseSave) baseSave.addEventListener('click', async function () {
    Sync.setBase($('#acc-base', main).value);
    serverUp = null;
    const h = await Sync.health();
    serverUp = h.ok;
    if (!h.ok) toast('Still cannot reach that address');
    repaint();
  });

  const email = $('#acc-email', main), pw = $('#acc-pw', main), msg = $('#acc-msg', main);
  if (!email) return;
  const busy = function (on) {
    ['#acc-in', '#acc-new'].forEach(function (sel) { const b = $(sel, main); if (b) b.disabled = on; });
  };
  const attempt = async function (fn, verb) {
    if (!email.value.trim() || !pw.value) { msg.textContent = 'Email and password, please.'; return; }
    busy(true);
    msg.textContent = verb + '\u2026';
    try {
      await fn(email.value.trim(), pw.value);
      pw.value = '';
      /* the account may already hold work from another machine — merge it in now */
      await syncNow();
      toast('Signed in \u2014 progress now syncs', true);
      repaint();
    } catch (e) {
      msg.textContent = String((e && e.message) || e);
      busy(false);
    }
  };
  $('#acc-in', main).addEventListener('click', function () { attempt(Sync.login, 'Signing in'); });
  $('#acc-new', main).addEventListener('click', function () { attempt(Sync.register, 'Creating'); });
  pw.addEventListener('keydown', function (e) { if (e.key === 'Enter') attempt(Sync.login, 'Signing in'); });
}

function renderProfile(main) {
  const note = storageNote();
  const dt = degreeTotals();
  const allUnits = TOTAL.lessons + dt.units;
  let doneUnits = 0;
  for (const id in P.completed) if (LESSON_INDEX[id]) doneUnits++;

  main.innerHTML = '<div class="page">' +
    '<div class="prof-head">' +
      '<div class="prof-av">' + esc(initials(P.name) || String(level())) + '</div>' +
      '<div class="prof-id">' +
        '<label class="eyebrow" for="prof-name">Display name</label>' +
        '<input id="prof-name" class="prof-name" maxlength="40" placeholder="Add your name" value="' + esc(P.name || '') + '">' +
        '<p class="prof-sub">Level ' + level() + ' \u00b7 ' + P.xp.toLocaleString('en-GB') + ' XP \u00b7 ' +
          doneUnits + ' of ' + allUnits + ' units \u00b7 ' + checksPassed().toLocaleString('en-GB') + ' checks passed</p>' +
      '</div>' +
    '</div>' +

    '<div class="pcard ' + (note.ok ? 'good' : 'warn') + '">' +
      '<div class="pcard-h"><span class="dot"></span><b>' + esc(note.head) + '</b></div>' +
      '<p>' + esc(note.body) + '</p>' +
      '<div class="pcard-acts">' +
        '<button class="btn success" id="prof-export">Export progress</button>' +
        '<button class="btn dark" id="prof-import">Import progress</button>' +
        '<input type="file" id="prof-file" accept="application/json,.json" hidden>' +
      '</div>' +
    '</div>' +

    accountCardHtml() +

    '<div class="pcard">' +
      '<div class="pcard-h"><b>Start over</b></div>' +
      '<p>Clears every completed unit, your XP and your saved code. Your name and theme stay. ' +
        'Export first if you might want it back \u2014 this cannot be undone.</p>' +
      '<div class="pcard-acts">' +
        '<button class="btn dark" id="prof-reset">Reset progress</button>' +
        '<span class="prof-warn" id="prof-reset-note" hidden>Press again to confirm</span>' +
      '</div>' +
    '</div>' +
  '</div>';

  wireAccountCard(main);
  if (serverUp === null && !Sync.signedIn()) {
    Sync.health().then(function (h) {
      serverUp = h.ok;
      if (!h.ok && route.view === 'profile') renderProfile($('#main'));
    });
  }

  const nameEl = $('#prof-name', main);
  nameEl.addEventListener('input', function () {
    P.name = nameEl.value.trim();
    updateXp();
    $('#screen-crumb').textContent = screenMeta(route).crumb;
    $('.prof-av', main).textContent = initials(P.name) || String(level());
    saveSoon();
  });

  $('#prof-export', main).addEventListener('click', exportProgress);
  const file = $('#prof-file', main);
  $('#prof-import', main).addEventListener('click', function () { file.click(); });
  file.addEventListener('change', function () {
    if (file.files && file.files[0]) importProgress(file.files[0]);
    file.value = '';
  });

  let armed = false;
  const resetBtn = $('#prof-reset', main), resetNote = $('#prof-reset-note', main);
  resetBtn.addEventListener('click', function () {
    if (!armed) {
      armed = true;
      resetNote.hidden = false;
      setTimeout(function () { armed = false; if (resetNote) resetNote.hidden = true; }, 4000);
      return;
    }
    resetProgress();
  });
}

function badgeSet() {
  const done = Object.keys(P.completed).filter(function (id) { return LESSON_INDEX[id]; }).length;
  const caps = DEGREE.courses.filter(function (c) { return c.capstoneLessonId && P.completed[c.capstoneLessonId]; }).length;
  const full = DEGREE.courses.filter(courseComplete).length;
  /* With a programme absent these three are undercounts, so a lit badge is still
     earned but an unlit one is merely unknown. Showing it as unearned would take a
     milestone the learner has already passed and visibly remove it. */
  const partial = MISSING_PROGRAMS.length > 0;
  const mark = function (b) { return partial && !b.on ? Object.assign(b, { unknown: true }) : b; };
  return [
    { glyph: '◆', name: 'First unit', on: done >= 1 },
    { glyph: '✦', name: 'Ten units', on: done >= 10 },
    { glyph: '⬢', name: 'Fifty units', on: done >= 50 },
    { glyph: '★', name: 'First capstone', on: caps >= 1 },
    { glyph: '⚑', name: 'Course complete', on: full >= 1 },
    { glyph: '🔥', name: 'Seven-day streak', on: streakDays() >= 7 },
  ].map(function (b) {
    /* the streak is computed from P.activity alone, so the catalog cannot affect it */
    return b.name === 'Seven-day streak' ? b : mark(b);
  });
}

/* ---------- track ---------- */
function renderTrack(main, t) {
  const next = firstIncomplete(t.id);
  let modules = '';
  t.modules.forEach(function (m, mi) {
    let rows = '';
    for (const l of m.lessons) {
      const mark = P.completed[l.id] ? 'done' : (next && next.id === l.id ? 'now' : '');
      rows += '<button class="lesson-row" data-lesson="' + l.id + '">' +
        '<span class="gmark ' + mark + '"></span>' +
        '<span class="num">' + l.num + '</span>' +
        '<span class="ttl">' + esc(l.title) + '</span>' +
        typeChip(l.type) +
        '<span class="min">~' + l.min + 'm</span>' +
      '</button>';
    }
    modules += '<div class="module"><h2><span class="mnum">M' + (mi + 1) + '</span>' + esc(m.title) + '</h2>' +
      '<p class="desc">' + esc(m.desc) + '</p>' + rows + '</div>';
  });
  main.innerHTML = '<div class="page">' +
    '<div class="crumb"><button data-go="home">Study plan</button><span>›</span><span>' + esc(t.name) + '</span></div>' +
    '<div class="track-head">' +
      '<span class="t-icon" style="--tt:' + t.tint + '">' + t.icon + '</span>' +
      '<div><h1>' + esc(t.name) + '</h1><p>' + esc(t.tagline) + '</p>' +
      '<button class="btn primary" id="track-start">' + (next ? (trackDone(t.id) ? 'Continue: ' + esc(next.title) : 'Start the track') : 'Track complete — revisit') + ' →</button></div>' +
    '</div>' +
    '<div class="outcomes"><h3>You will be able to</h3><ul>' + t.outcomes.map(function (o) { return '<li>' + esc(o) + '</li>'; }).join('') + '</ul></div>' +
    modules +
  '</div>';
  $('[data-go="home"]', main).addEventListener('click', function () { go(frontRoute()); });
  $('#track-start').addEventListener('click', function () { go({ view: 'lesson', id: (next || TRACK_LESSONS[t.id][0]).id }); });
  $all('.lesson-row', main).forEach(function (b) {
    b.addEventListener('click', function () { go({ view: 'lesson', id: b.dataset.lesson }); });
  });
}

/* ---------- degree: programme overview ---------- */
const degFilters = {};
function degFilterFor(programId) {
  if (!degFilters[programId]) degFilters[programId] = { q: '', level: 'all' };
  return degFilters[programId];
}

/* The programme name with its distinctive half emphasised — each spine names the
   substring itself rather than the view hard-coding one programme's title. */
function emphasise(pr) {
  const name = esc(pr.name);
  const key = pr.emphasis ? esc(pr.emphasis) : '';
  return key && name.indexOf(key) !== -1 ? name.replace(key, '<em>' + key + '</em>') : name;
}

/* ---------- the majors ----------
   With more than one programme the catalogue needs a front door, otherwise the
   icon-rail button has to guess which one you meant. */
function renderPrograms(main) {
  const cards = PROGRAMS.map(function (pr) {
    const t = degreeTotals(pr.id);
    const authored = coursesInProgram(pr.id).length;
    const planned = (pr.bands || []).length;
    const levels = {};
    coursesInProgram(pr.id).forEach(function (c) { levels[c.level] = (levels[c.level] || 0) + 1; });
    const spread = LEVEL_ORDER.filter(function (lv) { return levels[lv]; })
      .map(function (lv) { return '<span class="chip level ' + lv + '">' + levels[lv] + ' ' + lv + '</span>'; })
      .join('');
    /* "soon" means not written yet. A programme whose payload failed to arrive is
       written, paid for and sitting on the server, so saying "soon" about it — next to
       0 Courses and 0 Units — is the most misleading thing on any screen. */
    const lost = programMissing(pr.id);
    const bandList = (pr.bands || []).map(function (b) {
      const n = coursesInBand(pr.id, b.n).length;
      return '<li><span class="pb-icon" style="--tt:' + b.tint + '">' + b.icon + '</span>' +
        '<span class="pb-t">' + esc(b.title) + '</span>' +
        '<span class="pb-n">' + (n ? n + ' course' + (n === 1 ? '' : 's') : (lost ? '—' : 'soon')) + '</span></li>';
    }).join('');
    const stat = function (v, label) {
      return '<div class="stat"><b>' + (lost ? '\u2014' : v) + '</b><span>' + label + '</span></div>';
    };
    return '<button class="prog-card' + (lost ? ' lost' : authored ? '' : ' empty') + '" data-program="' + esc(pr.id) + '">' +
      '<div class="pc-head">' +
        '<div><h2>' + emphasise(pr) + '</h2><p>' + esc(pr.subtitle) + '</p></div>' +
        ringHtml(t.pct) +
      '</div>' +
      '<div class="pc-stats">' +
        stat(authored, 'Courses') + stat(t.units, 'Units') + stat(t.labs, 'Labs') +
        '<div class="stat"><b>' + planned + '</b><span>' + esc((pr.bandNoun || 'Year') + 's') + '</span></div>' +
      '</div>' +
      (lost ? '<div class="pc-lost">Could not be loaded \u2014 use <b>Try again</b> at the top of the window</div>' : '') +
      (spread ? '<div class="pc-levels">' + spread + '</div>' : '') +
      '<ul class="pc-bands">' + bandList + '</ul>' +
    '</button>';
  }).join('');

  main.innerHTML = '<div class="page wide">' +
    '<div class="crumb"><button data-go="home">Study plan</button><span>›</span><span>Programmes</span></div>' +
    '<div class="page-head">' +
      '<h1>Two majors</h1>' +
      '<p>Pick a programme to see its ' + esc(PROGRAMS.map(function (pr) { return (pr.bandNoun || 'Year').toLowerCase(); })
        .filter(function (v, i, a) { return a.indexOf(v) === i; }).join('s and ')) + 's. ' +
      'Progress is tracked separately for each.</p>' +
    '</div>' +
    '<div class="prog-grid">' + cards + '</div>' +
  '</div>';

  $('[data-go="home"]', main).addEventListener('click', function () { go(frontRoute()); });
  $all('.prog-card', main).forEach(function (b) {
    b.addEventListener('click', function () { go({ view: 'degree', program: b.dataset.program }); });
  });
}

function courseCardHtml(c) {
  const units = courseUnits(c);
  const d = courseDone(c);
  const pre = prereqState(c);
  const complete = units.length > 0 && d === units.length;
  return '<button class="course-card lv-' + c.level + (complete ? ' done-all' : '') + (!pre.allMet && d === 0 ? ' locked' : '') + '" data-course="' + c.id + '">' +
    '<div class="cc-top">' +
      '<span class="cc-icon">' + esc(c.icon || '◆') + '</span>' +
      '<span class="cc-id">' + esc(c.id) + '</span>' +
      '<span class="spacer" style="flex:1"></span>' +
      '<span class="chip level">' + esc(c.level) + '</span>' +
    '</div>' +
    '<h3>' + esc(c.title) + '</h3>' +
    '<p>' + esc(c.summary) + '</p>' +
    '<div class="cc-chips">' +
      (c.stack || []).slice(0, 3).map(function (s) { return '<span class="chip stack">' + esc(s) + '</span>'; }).join('') +
    '</div>' +
    '<div class="cc-foot">' +
      '<span>' + d + '/' + units.length + ' units</span>' +
      '<span class="spacer"></span>' +
      (!pre.allMet && d === 0
        ? '<span class="lock-note">needs ' + pre.list.filter(function (p) { return !p.met; }).map(function (p) { return p.id; }).join(', ') + '</span>'
        : '<span>' + (c.credits || 0) + ' cr · ' + (c.hours || 0) + ' h</span>') +
    '</div>' +
  '</button>';
}

/* ---------- degree: the planner ----------
   A catalogue answers "what exists". A planner answers "what do I do next", which is
   the question anyone actually arrives with. Three columns: which degree, which year
   and subject, and what that subject needs first — with the prerequisite chain laid
   out as a path rather than left implicit in a list. */

const plannerState = {};
function plannerFor(programId) {
  if (!plannerState[programId]) plannerState[programId] = { band: null, sel: null };
  return plannerState[programId];
}

/* The chain of subjects behind one course, deepest first. Prerequisites are a graph,
   but a learner wants a route through it, so this walks the graph and returns one
   ordered path: the things to do, in the order to do them. */
function prereqChain(c, limit) {
  /* The target is marked seen before the walk starts. Without it a cycle — or a
     course that is transitively its own prerequisite through a bad spine — emits the
     target twice, and the panel shows two "Current target" cards. */
  const seen = {};
  seen[c.id] = true;
  const out = [];
  (function walk(course, depth) {
    if (!course || depth > 6) return;
    for (const id of (course.prereqs || [])) {
      const pc = COURSE_OF[id];
      if (!pc || seen[id]) continue;
      seen[id] = true;
      walk(pc, depth + 1);
      out.push(pc);
    }
  })(c, 0);
  /* an incomplete prerequisite is worth more of the four slots than a finished one */
  const undone = out.filter(function (p) { return !courseComplete(p); });
  const done = out.filter(courseComplete);
  const keep = (limit || 3);
  const shown = undone.length >= keep
    ? undone.slice(0, keep)
    : done.slice(-(keep - undone.length)).concat(undone);
  return shown.concat([c]);
}

/* a run of segments rather than one bar: at a glance you count, not estimate */
function segBar(done, total, max) {
  const n = Math.min(total, max || 14);
  const lit = total ? Math.round(done / total * n) : 0;
  let h = '<span class="segs">';
  for (let i = 0; i < n; i++) h += '<i' + (i < lit ? ' class="on"' : '') + '></i>';
  return h + '</span>';
}

function renderDegree(main, programId) {
  if (!DEGREE.courses.length) {
    /* Two different failures used to share one message. They need different answers:
       one is a build that shipped without a catalog, the other is a catalog that did
       not arrive over the network. */
    main.innerHTML = DEGREE_CHUNK_LIST.length
      ? '<div class="page"><h1>The catalog did not load</h1><p>This build fetches the ' +
        'course catalog, and none of it arrived. Check the connection and try again \u2014 ' +
        'the foundation tracks in the panel on the left do not need it.</p></div>'
      : '<div class="page"><h1>No catalog loaded</h1><p>The degree catalog was not bundled into this build.</p></div>';
    return;
  }
  if (programMissing(programId)) {
    main.innerHTML = '<div class="page"><h1>' + esc((PROGRAM_OF[programId] || {}).name || programId) +
      '</h1><p>This programme\u2019s courses could not be loaded. Everything else is ' +
      'unaffected; use <b>Try again</b> in the bar at the top.</p></div>';
    return;
  }
  const prog = PROGRAM_OF[programId] || PROGRAMS[0];
  if (!prog) { main.innerHTML = '<div class="page"><h1>No programme</h1></div>'; return; }

  const st = plannerFor(prog.id);
  const bands = prog.bands || [];
  if (st.band === null || !bands.some(function (b) { return b.n === st.band; })) {
    /* open on the year the learner is actually in: the first with unfinished work */
    const live = bands.find(function (b) {
      return coursesInBand(prog.id, b.n).some(function (c) { return !courseComplete(c); });
    });
    st.band = live ? live.n : (bands[0] ? bands[0].n : 1);
  }
  const list = coursesInBand(prog.id, st.band);
  if (!st.sel || !COURSE_OF[st.sel] || COURSE_OF[st.sel].band !== st.band ||
      COURSE_OF[st.sel].program !== prog.id) {
    const next = list.find(function (c) { return !courseComplete(c); });
    st.sel = (next || list[0] || {}).id || null;
  }
  const sel = st.sel ? COURSE_OF[st.sel] : null;
  const dt = degreeTotals(prog.id);
  /* the dashboard used to carry this; with the dashboard gone it belongs where the
     learner already is */
  const resumeTarget = (P.last && LESSON_INDEX[P.last]) ? LESSON_INDEX[P.last].lesson : null;

  /* ---- left: which degree ---- */
  const majors = PROGRAMS.map(function (pr) {
    const t = programMissing(pr.id) ? null : degreeTotals(pr.id);
    return '<button class="mj' + (pr.id === prog.id ? ' on' : '') + '" data-major="' + esc(pr.id) +
      '" aria-pressed="' + (pr.id === prog.id ? 'true' : 'false') + '">' +
      '<span class="mj-i">' + esc(pr.icon || (pr.bands && pr.bands[0] ? pr.bands[0].icon : '◆')) + '</span>' +
      '<span class="mj-n">' + esc(pr.short || pr.name) + '</span>' +
      '<span class="mj-c">' + (t ? t.credits : '\u2014') + ' cr</span>' +
    '</button>';
  }).join('');

  /* ---- middle: the year, and its subjects ---- */
  const years = bands.map(function (b) {
    return '<button class="yr' + (b.n === st.band ? ' on' : '') + '" data-band="' + b.n +
      '" aria-pressed="' + (b.n === st.band ? 'true' : 'false') +
      '" aria-label="' + esc(bandLabel(prog, b.n)) + '">' + b.n + '</button>';
  }).join('');

  const cards = list.map(function (c) {
    const units = courseUnits(c).length;
    const done = courseDone(c);
    const state = done === 0 ? 'Not started' : (done === units ? 'Complete' : 'In progress');
    const cls = done === 0 ? '' : (done === units ? 'done' : 'live');
    const pre = prereqState(c);
    return '<button class="subj' + (c.id === st.sel ? ' on' : '') + '" data-subj="' + esc(c.id) +
      '" aria-pressed="' + (c.id === st.sel ? 'true' : 'false') + '">' +
      '<div class="sj-top">' +
        '<span class="sj-icon">' + esc(c.icon || '◆') + '</span>' +
        '<div class="sj-id"><b>' + esc(c.title.split(/\s+\u2014\s+/)[0]) + '</b><span>' + esc(c.id) + '</span></div>' +
      '</div>' +
      '<div class="sj-meta">' +
        '<span title="Estimated total study time">\u25f7 \u2248 ' + (c.hours || 0) + ' h</span>' +
        '<span class="dot">\u00b7</span>' +
        '<span>' + (c.kind === 'track'
          ? units + ' unit' + (units === 1 ? '' : 's')
          : (c.credits || 0) + ' credits') + '</span>' +
      '</div>' +
      segBar(done, units, 12) +
      '<div class="sj-state ' + cls + '"><i></i>' + state +
        (!pre.allMet && done === 0 ? ' \u00b7 prerequisites open' : '') + '</div>' +
    '</button>';
  }).join('');

  /* ---- right: what this subject needs first ---- */
  let detail = '<div class="pl-empty">No subject selected.</div>';
  if (sel) {
    const units = courseUnits(sel);
    const labs = courseLabs(sel);
    /* Two prerequisites plus the target: four cards overflow the panel and it is
       the target that scrolls out of sight, which is the one card the rest of the
       panel is about. The chain already spends its slots on unfinished work. */
    const chain = prereqChain(sel, 2);
    const firstOpen = chain.find(function (p) { return p !== sel && !courseComplete(p); });
    const links = chain.map(function (p, i) {
      const isTarget = p === sel;
      const complete = courseComplete(p);
      const nextUp = p === firstOpen;
      const state = isTarget ? 'Current target' : complete ? 'Complete' : nextUp ? 'Recommended next' : 'Not started';
      const kls = isTarget ? 'target' : complete ? 'ok' : nextUp ? 'next' : '';
      const badge = isTarget ? '' : complete
        ? '<span class="pq-b ok">\u2713</span>'
        : nextUp ? '<span class="pq-b next">!</span>' : '';
      return (i ? '<span class="pq-arrow">\u2192</span>' : '') +
        '<button class="pq ' + kls + '" data-subj="' + esc(p.id) + '">' + badge +
          '<span class="pq-g">' + esc(p.icon || '◆') + '</span>' +
          '<span class="pq-n">' + esc(p.title.split(/\s+\u2014\s+/)[0]) + '</span>' +
          '<span class="pq-c">' + esc(p.id) + '</span>' +
          '<span class="pq-s">' + state + '</span>' +
        '</button>';
    }).join('');
    const goal = firstOpen || sel;
    detail =
      '<div class="pd-eyebrow">' + esc(sel.id) + ' \u00b7 ' + esc(sel.title.toUpperCase()) + '</div>' +
      '<h2 class="pd-title">' + esc(sel.title.split(/\s+\u2014\s+/)[0]) + '</h2>' +
      '<div class="pd-chips">' +
        '<span>\u25a4 ' + units.length + ' units</span>' +
        '<span>\u2697 ' + labs + ' labs</span>' +
        '<span>\u25f7 \u2248 ' + (sel.hours || 0) + ' h</span>' +
      '</div>' +
      '<p class="pd-sum">' + esc(sel.summary || '') + '</p>' +
      '<h3 class="pd-h">Recommended prerequisites</h3>' +
      '<div class="pq-row">' + links + '</div>' +
      '<p class="pd-note">\u24d8 Recommended, not required \u2014 nothing is locked, and every ' +
        'unit is checked the same way whichever order you take them in.</p>' +
      '<div class="pd-acts">' +
        '<button class="btn success" data-open="' + esc(goal.id) + '">\u25b6 ' +
          (goal === sel ? 'Open this subject' : 'Start ' + esc(goal.id)) + '</button>' +
        '<button class="btn dark" data-preview="' + esc(sel.id) + '">Preview subject</button>' +
      '</div>';
  }

  const bandMeta = bands.find(function (b) { return b.n === st.band; }) || {};

  /* Every interaction here re-renders the whole pane, so the column the learner is
     reading has to be put back where it was — otherwise choosing a subject halfway
     down a year scrolls the grid to the top and loses the card that was just clicked. */
  const keepScroll = (function () {
    const el = $('.pl-main', main);
    return el ? el.scrollTop : 0;
  })();

  main.innerHTML = '<div class="planner">' +
    '<aside class="pl-majors">' +
      '<div class="pl-lbl">Select major</div>' +
      '<div class="mj-list">' + majors + '</div>' +
      '<div class="pl-lbl mt">Where you left off</div>' +
      '<div class="fnd">' + (resumeTarget
        ? '<button class="fnd-go now" data-resume="' + esc(resumeTarget.id) + '">' +
            '<span class="fnd-t"><b>' + esc(resumeTarget.title) + '</b>' +
            '<span>' + esc(UNIT_KIND[resumeTarget.type] || resumeTarget.type) + ' \u00b7 ~' +
            (resumeTarget.min || 8) + ' min</span></span><span>\u203a</span></button>'
        : '<p class="fnd-none">Pick a subject to start.</p>') +
      '</div>' +
    '</aside>' +

    '<div class="pl-main">' +
      '<div class="pl-eyebrow">' + esc((prog.short || prog.name).toUpperCase()) + ' \u00b7 study plan</div>' +
      '<h1 class="pl-h1">Build your path, in the right order.</h1>' +
      '<p class="pl-sub">Choose a year and a subject to see what to learn first.</p>' +
      '<div class="yr-row"><span class="yr-lbl">' + esc((prog.bandNoun || 'Year').toUpperCase()) + '</span>' + years + '</div>' +
      '<h2 class="pl-h2">' + esc(bandLabel(prog, st.band)) + ' subjects' +
        (bandMeta.title ? ' <span>\u2014 ' + esc(bandMeta.title) + '</span>' : '') + '</h2>' +
      '<div class="subj-grid">' + (cards || '<p class="pl-empty">Nothing authored in this year yet.</p>') + '</div>' +
      /* A "view every subject in this year" link used to sit here. Every subject in
         the year is already on screen above it, and it navigated to the programme
         picker, which lists no subjects at all \u2014 a promise of more that led somewhere
         with less. */
      '' +
    '</div>' +

    '<aside class="pl-detail">' + detail + '</aside>' +

    '<div class="pl-foot">' +
      '<div class="pf-lbl">Degree progress</div>' +
      '<div class="pf-pct">' + dt.pct + '%</div>' +
      '<div class="pf-cr"><b>' + dt.earned + '</b> of ' + dt.credits + ' credits' +
        '<span class="pf-ok">\u2713 ' + dt.done + ' of ' + dt.units + ' units done</span></div>' +
      segBar(dt.done, dt.units, 22) +
      '<button class="pf-go" data-go="progress">View full progress <span>\u203a</span></button>' +
    '</div>' +
  '</div>';

  const pane = $('.pl-main', main);
  if (pane && keepScroll) pane.scrollTop = keepScroll;

  $all('[data-major]', main).forEach(function (b) {
    b.addEventListener('click', function () { go({ view: 'degree', program: b.dataset.major }); });
  });
  $all('[data-band]', main).forEach(function (b) {
    b.addEventListener('click', function () {
      st.band = Number(b.dataset.band); st.sel = null; renderDegree(main, prog.id);
    });
  });
  $all('[data-subj]', main).forEach(function (b) {
    b.addEventListener('click', function () {
      const c = COURSE_OF[b.dataset.subj];
      if (c && c.band === st.band && c.program === prog.id) { st.sel = c.id; renderDegree(main, prog.id); }
      else if (c) go(c.kind === 'track' ? { view: 'track', track: c.id } : { view: 'course', id: c.id });
    });
  });
  const openWhere = function (id) {
    const c = COURSE_OF[id];
    return c && c.kind === 'track' ? { view: 'track', track: id } : { view: 'course', id: id };
  };
  const openBtn = $('[data-open]', main);
  if (openBtn) openBtn.addEventListener('click', function () { go(openWhere(openBtn.dataset.open)); });
  const prevBtn = $('[data-preview]', main);
  if (prevBtn) prevBtn.addEventListener('click', function () { go(openWhere(prevBtn.dataset.preview)); });
  const res = $('[data-resume]', main);
  if (res) res.addEventListener('click', function () {
    go({ view: 'lesson', id: res.dataset.resume });
  });
  $all('[data-go]', main).forEach(function (b) {
    b.addEventListener('click', function () { go({ view: b.dataset.go }); });
  });
}

/* ---------- degree: one course ---------- */
function depMapSvg(c) {
  const pre = (c.prereqs || []).filter(function (id) { return COURSE_OF[id]; });
  const post = (COURSE_DEPENDENTS[c.id] || []).filter(function (id) { return COURSE_OF[id]; });
  if (!pre.length && !post.length) return '';
  const W = 660, colW = 210, boxW = 168, boxH = 34, vGap = 12;
  const rows = Math.max(pre.length, post.length, 1);
  const H = Math.max(rows * (boxH + vGap) + 20, 90);
  function col(list, x, cls) {
    const total = list.length * (boxH + vGap) - vGap;
    const top = (H - total) / 2;
    return list.map(function (id, i) {
      const y = top + i * (boxH + vGap);
      const cc = COURSE_OF[id];
      return { id: id, x: x, y: y, done: courseComplete(cc), cls: cls };
    });
  }
  const L = col(pre, 8, 'pre');
  const R = col(post, 8 + colW * 2, 'post');
  const midY = (H - boxH) / 2;
  const M = [{ id: c.id, x: 8 + colW, y: midY, done: courseComplete(c), cls: 'here' }];
  let edges = '';
  for (const n of L) {
    edges += '<path class="de hot" d="M' + (n.x + boxW) + ',' + (n.y + boxH / 2) +
      ' C' + (n.x + boxW + 20) + ',' + (n.y + boxH / 2) + ' ' + (M[0].x - 20) + ',' + (midY + boxH / 2) +
      ' ' + M[0].x + ',' + (midY + boxH / 2) + '"/>';
  }
  for (const n of R) {
    edges += '<path class="de" d="M' + (M[0].x + boxW) + ',' + (midY + boxH / 2) +
      ' C' + (M[0].x + boxW + 20) + ',' + (midY + boxH / 2) + ' ' + (n.x - 20) + ',' + (n.y + boxH / 2) +
      ' ' + n.x + ',' + (n.y + boxH / 2) + '"/>';
  }
  function node(n) {
    const cc = COURSE_OF[n.id];
    const label = n.id + ' · ' + (cc ? cc.title : '');
    const short = label.length > 26 ? label.slice(0, 25) + '…' : label;
    return '<g class="dn ' + (n.cls === 'here' ? 'here' : (n.done ? 'done' : '')) + '" data-goto="' + n.id + '">' +
      '<rect x="' + n.x + '" y="' + n.y + '" width="' + boxW + '" height="' + boxH + '" rx="8"/>' +
      '<text x="' + (n.x + 10) + '" y="' + (n.y + 21) + '">' + esc(short) + '</text></g>';
  }
  return '<div class="depmap"><h3>Where this sits</h3><svg viewBox="0 0 ' + W + ' ' + H + '" width="100%" height="' + H + '">' +
    edges + L.concat(M, R).map(node).join('') + '</svg></div>';
}

function renderCourse(main, c) {
  if (!c) { go({ view: 'programs' }); return; }
  const cpr = programOf(c);
  const units = courseUnits(c);
  const d = courseDone(c);
  const pre = prereqState(c);
  const next = firstIncomplete(c.id);
  const cap = c.capstone;

  /* Every unit in the module, in order.

     This page used to render `m.lab` and nothing else — so a course whose modules
     open with a sandbox, ask a quiz, drill the symbols, work a number and build a
     circuit before they ever reach Python showed exactly one button, labelled Lab.
     The other units existed, were indexed and were graded; they were reachable only
     from the curriculum rail. Anyone arriving through the planner saw a programming
     course, which is the complaint that kept coming back. */
  const byModule = {};
  courseUnits(c).forEach(function (l) {
    const info = LESSON_INDEX[l.id];
    if (!info) return;
    (byModule[info.mi] = byModule[info.mi] || []).push(l);
  });

  function unitMeta(l) {
    const bits = [];
    if (l.tests && l.tests.length) bits.push(l.tests.length + ' automated checks');
    if (l.checks && l.checks.length) bits.push(l.checks.length + ' measured checks');
    if (l.questions && l.questions.length) bits.push(l.questions.length + ' questions');
    if (l.items && l.items.length) bits.push(l.items.length + ' symbols');
    if (l.blanks && l.blanks.length) bits.push(l.blanks.length + ' blanks');
    if (l.steps && l.steps.length) bits.push(l.steps.length + ' steps');
    if (l.constraints && l.constraints.length) bits.push(l.constraints.length + ' constraints');
    if (l.given && l.given.length) bits.push('one number to find');
    return bits.length ? ' \u00b7 ' + bits.join(' \u00b7 ') : '';
  }

  let mods = '';
  c.modules.forEach(function (m, mi) {
    const us = byModule[mi] || [];
    const doneN = us.filter(function (l) { return P.completed[l.id]; }).length;
    const allDone = us.length > 0 && doneN === us.length;
    mods += '<div class="mod" data-mod="' + mi + '">' +
      '<button class="mod-head">' +
        '<span class="gmark ' + (allDone ? 'done' : '') + '"></span>' +
        '<span class="mnum">M' + (mi + 1) + '</span>' +
        '<span class="mtitle">' + esc(m.title) +
          (m.summary ? '<span class="msum">' + esc(m.summary) + '</span>' : '') +
        '</span>' +
        '<span class="mcount">' + doneN + '/' + us.length + '</span>' +
        '<span class="caret">\u25b6</span>' +
      '</button>' +
      '<div class="mod-body" hidden>' +
        '<h4>Key concepts</h4>' +
        '<ul>' + m.concepts.map(function (x) { return '<li>' + mdInline(x) + '</li>'; }).join('') + '</ul>' +
        '<h4>Units</h4>' +
        '<div class="unit-list">' + us.map(function (l) {
          const ud = !!P.completed[l.id];
          return '<button class="lab-row" data-lesson="' + esc(l.id) + '">' +
            '<span class="gmark ' + (ud ? 'done' : '') + '"></span>' +
            '<span class="chip ' + esc(l.type) + '">' + esc(UNIT_KIND[l.type] || l.type) + '</span>' +
            '<span class="lab-t"><b>' + esc(l.title) + '</b>' +
              '<span>~' + (l.min || 8) + ' min' + unitMeta(l) + '</span></span>' +
            '<span class="go">' + (ud ? 'revisit \u25b8' : 'open \u25b8') + '</span>' +
          '</button>';
        }).join('') + '</div>' +
      '</div>' +
    '</div>';
  });

  const capDone = c.capstoneLessonId && P.completed[c.capstoneLessonId];
  main.innerHTML = '<div class="page wide lv-' + c.level + '">' +
    '<div class="crumb"><button data-go="home">Study plan</button><span>›</span>' +
      '<button data-go="degree">' + esc(cpr ? (cpr.short || cpr.name) : 'Programmes') + '</button><span>›</span>' +
      '<span>' + esc(bandLabel(cpr, c.band)) + '</span><span>›</span><span>' + esc(c.id) + '</span></div>' +

    '<div class="course-head">' +
      '<div>' +
        '<div class="ch-id">' +
          '<span class="ch-icon">' + esc(c.icon || '◆') + '</span>' +
          '<span class="chip mono">' + esc(c.id) + '</span>' +
          '<span class="chip level">' + esc(c.level) + '</span>' +
          '<span class="chip mono">' + esc(bandLabel(cpr, c.band)) + '</span>' +
        '</div>' +
        '<h1>' + esc(c.title) + '</h1>' +
        '<p class="lede">' + esc(c.summary) + '</p>' +
        '<button class="btn primary" id="course-start">' +
          (next ? (d ? 'Continue: ' + esc(next.title) : 'Start the course') : 'Course complete — revisit') + ' →</button>' +
      '</div>' +
      '<div class="meta-card"><dl>' +
        '<dt>Level</dt><dd><span class="chip level">' + esc(c.level) + '</span></dd>' +
        '<dt>Prereqs</dt><dd>' + (pre.list.length
          ? pre.list.map(function (p) {
              return '<button class="chip prereq ' + (p.met ? 'met' : 'unmet') + '" data-goto="' + p.id + '">' + esc(p.id) + '</button>';
            }).join('')
          : '<span class="chip">None</span>') + '</dd>' +
        '<dt>Stack</dt><dd>' + (c.stack || []).map(function (s) { return '<span class="chip stack">' + esc(s) + '</span>'; }).join('') + '</dd>' +
        '<dt>Credits</dt><dd class="plain">' + (c.credits || 0) + ' · ' + (c.hours || 0) + ' h</dd>' +
        '<dt>Progress</dt><dd class="plain">' + d + ' / ' + units.length + ' units</dd>' +
        (c.assessment ? '<dt>Assessed</dt><dd class="plain" style="font-family:var(--font-body);font-size:13px">' + esc(c.assessment) + '</dd>' : '') +
      '</dl></div>' +
    '</div>' +

    (pre.list.length ? (
      '<div class="gate' + (pre.allMet ? ' ok' : '') + '">' +
        '<span class="g-icon">' + (pre.allMet ? '✓' : '!') + '</span>' +
        '<div>' + (pre.allMet
          ? '<b>Prerequisites met</b>You have completed everything this course builds on.'
          : '<b>Prerequisites not yet complete</b>This course assumes ' +
            pre.list.filter(function (p) { return !p.met; }).map(function (p) { return esc(p.id) + ' (' + esc(p.title) + ')'; }).join(' and ') +
            '. Nothing is locked — but expect gaps if you skip ahead.') +
        '</div></div>'
    ) : '') +

    (c.outcomes && c.outcomes.length ? (
      '<div class="outcomes"><h3>On completion you will be able to</h3><ul>' +
      c.outcomes.map(function (o) { return '<li>' + mdInline(o) + '</li>'; }).join('') + '</ul></div>'
    ) : '') +

    '<div class="section-h"><h2>Modules</h2><span>' + c.modules.length + ' modules · ' + units.length + ' units, every one checked</span></div>' +
    '<div class="mod-list">' + mods + '</div>' +

    (cap ? (
      '<div class="capstone-card">' +
        '<div class="cap-eyebrow">Capstone project</div>' +
        '<h2>' + esc(cap.title) + '</h2>' +
        '<div class="cap-cols">' +
          (cap.deliverables && cap.deliverables.length ? '<div><h4>Deliverables</h4><ul>' +
            cap.deliverables.map(function (x) { return '<li>' + mdInline(x) + '</li>'; }).join('') + '</ul></div>' : '') +
          (cap.constraints && cap.constraints.length ? '<div><h4>Constraints</h4><ul>' +
            cap.constraints.map(function (x) { return '<li>' + mdInline(x) + '</li>'; }).join('') + '</ul></div>' : '') +
        '</div>' +
        (cap.rubric && cap.rubric.length ? (
          '<table class="rubric"><thead><tr><th>Criterion</th><th>Weight</th><th>How it is judged</th></tr></thead><tbody>' +
          cap.rubric.map(function (r) {
            return '<tr><td>' + esc(r.criterion) + '</td>' +
              '<td class="w">' + r.weight + '%<span class="wbar"><i style="width:' + r.weight + '%"></i></span></td>' +
              '<td>' + mdInline(r.evidence) + '</td></tr>';
          }).join('') + '</tbody></table>'
        ) : '') +
        (c.capstoneLessonId ? '<div style="margin-top:16px"><button class="btn ' + (capDone ? '' : 'primary') + '" id="cap-open">' +
          (capDone ? '✓ Capstone passed — reopen' : 'Open the capstone workspace') + ' →</button></div>' : '') +
      '</div>'
    ) : '') +

    depMapSvg(c) +

    (c.reading && c.reading.length ? (
      '<div class="outcomes"><h3>Reading</h3><ul>' +
      c.reading.map(function (r) { return '<li>' + mdInline(r) + '</li>'; }).join('') + '</ul></div>'
    ) : '') +
  '</div>';

  $('[data-go="home"]', main).addEventListener('click', function () { go(frontRoute()); });
  $('[data-go="degree"]', main).addEventListener('click', function () { go({ view: 'degree', program: c.program }); });
  $('#course-start', main).addEventListener('click', function () {
    go({ view: 'lesson', id: (next || units[0]).id });
  });
  const capBtn = $('#cap-open', main);
  if (capBtn) capBtn.addEventListener('click', function () { go({ view: 'lesson', id: c.capstoneLessonId }); });
  $all('[data-goto]', main).forEach(function (b) {
    b.addEventListener('click', function (e) { e.stopPropagation(); go({ view: 'course', id: b.dataset.goto }); });
  });
  $all('.mod', main).forEach(function (mod) {
    const head = $('.mod-head', mod), body = $('.mod-body', mod);
    head.addEventListener('click', function () {
      const open = mod.classList.toggle('open');
      body.hidden = !open;
    });
  });
  $all('.lab-row', main).forEach(function (b) {
    b.addEventListener('click', function (e) { e.stopPropagation(); go({ view: 'lesson', id: b.dataset.lesson }); });
  });
  /* open the module holding the next unit, so the page lands where you left off */
  if (next) {
    const idx = c.modules.findIndex(function (m) { return m.lessonId === next.id; });
    if (idx >= 0) {
      const mod = $all('.mod', main)[idx];
      if (mod) { mod.classList.add('open'); $('.mod-body', mod).hidden = false; }
    }
  }
}

/* ---------- lesson chrome ---------- */
function lessonHeader(l) {
  return crumbHtml(l) +
    '<div class="lesson-title"><span class="lnum">' + l.num + '</span><h1>' + esc(l.title) + '</h1></div>' +
    '<div class="lesson-meta">' + typeChip(l.type) + '<span>~' + l.min + ' min</span>' +
    (P.completed[l.id] ? '<span class="chip done">✓ Completed</span>' : '') + '</div>';
}
function footNav(l, markHtml) {
  const nav = lessonNav(l);
  return '<div class="article-foot">' + (markHtml || '') + '<span class="spacer"></span>' +
    (nav.prev ? '<button class="btn" id="nav-prev">← ' + esc(nav.prev.title) + '</button>' : '') +
    (nav.next ? '<button class="btn ' + (P.completed[l.id] ? 'primary' : '') + '" id="nav-next">' + esc(nav.next.title) + ' →</button>' : '') +
  '</div>';
}
function wireFootNav(root, l) {
  const nav = lessonNav(l);
  const p = $('#nav-prev', root), n = $('#nav-next', root);
  if (p) p.addEventListener('click', function () { go({ view: 'lesson', id: nav.prev.id }); });
  if (n) n.addEventListener('click', function () { go({ view: 'lesson', id: nav.next.id }); });
}

/* ---------- read ---------- */
function renderRead(main, l) {
  const done = P.completed[l.id];
  main.innerHTML = '<div class="lesson-read">' + lessonHeader(l) +
    '<div class="article">' + renderMd(BUNDLE[l.md] || '*missing content*') + '</div>' +
    footNav(l, done ? '<span class="done-note">✓ Read</span>' : '<button class="btn success" id="mark-read">✓ Mark as read</button>') +
  '</div>';
  wireCrumb(main, l);
  wireFootNav(main, l);
  const mb = $('#mark-read', main);
  if (mb) mb.addEventListener('click', function () {
    completeLesson(l.id);
    toast('Read · +' + XP.read + ' XP', true);
    renderRail();
    go({ view: 'lesson', id: l.id });
  });
}

/* ---------- quiz ---------- */
/* Options were rendered in the order they were authored, and one course shipped with
   all twenty-four answers at index 0 — a perfect score by pressing A every time. The
   order is now derived from the lesson id and the question number, so it is stable for
   a given learner (their best score keeps its meaning) but not the authoring order. */
function shuffledOptions(lessonId, qi, q) {
  let h = 2166136261;
  const key = lessonId + ':' + qi;
  for (let i = 0; i < key.length; i++) {
    h ^= key.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  const idx = q.opts.map(function (_, i) { return i; });
  for (let i = idx.length - 1; i > 0; i--) {
    h = Math.imul(h ^ (h >>> 15), 2246822507);
    const j = (h >>> 0) % (i + 1);
    const t = idx[i]; idx[i] = idx[j]; idx[j] = t;
  }
  return { order: idx, opts: idx.map(function (i) { return q.opts[i]; }), a: idx.indexOf(q.a) };
}

function renderQuiz(main, l) {
  const shuffled = l.questions.map(function (q, qi) { return shuffledOptions(l.id, qi, q); });
  const answers = new Array(l.questions.length).fill(null);
  main.innerHTML = '<div class="lesson-read">' + lessonHeader(l) +
    '<p style="color:var(--ink-2);margin:0 0 18px">Answer every question — explanations appear as you go. ' +
    '<b>' + Math.ceil(l.questions.length * 0.7) + ' of ' + l.questions.length + '</b> needed to pass.' +
    (P.quiz[l.id] ? ' Best so far: <b>' + P.quiz[l.id] + '%</b>.' : '') + '</p>' +
    '<div id="quiz"></div><div id="quiz-out"></div>' + footNav(l, '') +
  '</div>';
  wireCrumb(main, l);
  wireFootNav(main, l);
  const box = $('#quiz', main);
  l.questions.forEach(function (q, qi) {
    const card = el('<div class="quiz-q"><div class="qn">QUESTION ' + (qi + 1) + ' / ' + l.questions.length + '</div>' +
      '<div class="qt">' + mdInline(q.q) + '</div>' +
      '<div class="opts">' + shuffled[qi].opts.map(function (o, oi) {
        return '<button class="opt" data-oi="' + oi + '"><span class="k">' + 'ABCD'[oi] + '</span><span>' + mdInline(o) + '</span></button>';
      }).join('') + '</div><div class="ex-slot"></div></div>');
    box.appendChild(card);
    $all('.opt', card).forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (answers[qi] !== null) return;
        const oi = +btn.dataset.oi;
        answers[qi] = oi;
        $all('.opt', card).forEach(function (b2) {
          b2.disabled = true;
          const i2 = +b2.dataset.oi;
          if (i2 === shuffled[qi].a) b2.classList.add('correct');
          else if (i2 === oi) b2.classList.add('wrong');
        });
        const good = oi === shuffled[qi].a;
        $('.ex-slot', card).innerHTML = '<div class="explain ' + (good ? 'good' : 'bad') + '">' +
          (good ? '✓ Right. ' : '✗ Not quite — the answer is <b>' + 'ABCD'[shuffled[qi].a] + '</b>. ') + mdInline(q.why) + '</div>';
        if (answers.every(function (a) { return a !== null; })) finish();
      });
    });
  });
  function finish() {
    const correct = answers.filter(function (a, i) { return a === shuffled[i].a; }).length;
    const pct = Math.round(correct / l.questions.length * 100);
    const pass = pct >= 70;
    P.quiz[l.id] = Math.max(P.quiz[l.id] || 0, pct);
    let xpNote = '';
    if (pass) {
      if (completeLesson(l.id)) xpNote = ' · +' + XP.quiz + ' XP';
      renderRail();
    } else { saveSoon(); }
    const nav = lessonNav(l);
    $('#quiz-out', main).innerHTML = '<div class="quiz-result">' +
      '<div class="score">' + correct + ' / ' + l.questions.length + '</div>' +
      '<p>' + (pass ? 'Passed — quiz complete' + xpNote + '.' : 'Below 70% — skim the reading again and retry. Nothing lost.') + '</p>' +
      '<div style="display:flex;gap:8px;flex-wrap:wrap">' +
        '<button class="btn dark" id="quiz-retry">Retry</button>' +
        (pass && nav.next ? '<button class="btn primary" id="quiz-next">' + esc(nav.next.title) + ' →</button>' : '') +
      '</div></div>';
    $('#quiz-out', main).scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    $('#quiz-retry', main).addEventListener('click', function () { go({ view: 'lesson', id: l.id, top: true }); });
    const qn = $('#quiz-next', main);
    if (qn) qn.addEventListener('click', function () { go({ view: 'lesson', id: nav.next.id }); });
  }
}

/* ---------- code / project ---------- */
/* files may carry inline `content` (degree labs) or a bundle `key` (track lessons) */
function fileText(f) { return (typeof f.content === 'string') ? f.content : bundleFile(f.key); }
function lessonMd(l) { return (typeof l.mdText === 'string') ? l.mdText : (BUNDLE[l.md] || ''); }
function starterFiles(l) {
  return l.files.map(function (f) {
    return { name: f.name, content: fileText(f), ro: !!f.ro };
  });
}
function currentFiles(l) {
  const base = starterFiles(l);
  const saved = P.code[l.id] && P.code[l.id].files;
  if (saved) for (const f of base) if (!f.ro && typeof saved[f.name] === 'string') f.content = saved[f.name];
  return base;
}

/* ---------- lesson: find the value ----------
   The plainest question in engineering and the one most worth asking: here is a
   circuit, here are the numbers on it, what does the meter read. The diagram is drawn
   by the same painter the schematic editor uses, so it cannot drift from what the
   solver would show for the same model, and the givens are a table rather than prose
   because that is how a datasheet hands them to you. */
function renderNumeric(main, l) {
  const saved = (P.numeric && P.numeric[l.id]) || {};
  let value = saved.v === undefined ? '' : String(saved.v);
  let verdict = null;

  function close(x) {
    const tol = l.tol === undefined ? Math.abs(l.answer) * 0.01 : l.tol;
    return Math.abs(x - l.answer) <= Math.abs(tol) + 1e-12;
  }

  function paint() {
    const done = !!P.completed[l.id];
    main.innerHTML = '<div class="page reading">' +
      lessonHeader(l) +
      '<div class="article">' + renderMd(lessonMd(l)) + '</div>' +
      '<h3 class="q-prompt">' + mdInline(l.prompt || '') + '</h3>' +
      (l.note ? '<p class="q-note">' + mdInline(l.note) + '</p>' : '') +
      '<div class="numq">' +
        '<div class="numq-fig">' + (l.diagram ? '<div id="numq-dia"></div>'
          : '<div class="numq-nofig">' + mdInline(l.figure || '') + '</div>') + '</div>' +
        '<div class="numq-side">' +
          '<div class="nq-lbl">Your answer</div>' +
          '<div class="nq-in"><input type="text" inputmode="decimal" id="nq-v" value="' + esc(value) +
            '" placeholder="0.00" autocomplete="off" spellcheck="false">' +
            '<span class="nq-u">' + esc(l.unit || '') + '</span></div>' +
          (l.given && l.given.length
            ? '<div class="nq-lbl mt">Given</div><table class="nq-given">' +
              l.given.map(function (g) {
                return '<tr><td>' + mdInline(g.label) + '</td><td>' + mdInline(g.value) + '</td></tr>';
              }).join('') + '</table>'
            : '') +
          (l.aside ? '<p class="nq-aside">' + mdInline(l.aside) + '</p>' : '') +
        '</div>' +
      '</div>' +
      (verdict
        ? '<div class="q-verdict ' + (verdict.ok ? 'ok' : 'no') + '">' +
            '<span class="gmark ' + (verdict.ok ? 'done' : 'fail') + '"></span>' +
            '<div><b>' + (verdict.ok ? 'That is it.' : verdict.head) + '</b>' +
            '<p>' + mdInline(verdict.ok ? (l.why || '') : verdict.body) + '</p></div>' +
          '</div>'
        : '') +
      '<div class="q-acts">' +
        '<button class="btn success" id="nq-check">Check</button>' +
        (l.hint ? '<button class="btn dark" id="nq-hint">Hint</button>' : '') +
      '</div>' +
      (saved.hint ? '<div class="q-hint">' + mdInline(l.hint) + '</div>' : '') +
      footNav(l, done ? '<span class="done-note">\u2713 Solved</span>' : '') +
    '</div>';

    wireCrumb(main, l);
    wireFootNav(main, l);

    if (l.diagram) {
      const host = $('#numq-dia', main);
      if (host && typeof createCircuit === 'function') {
        const h = createCircuit(host, { model: l.diagram, readOnly: true });
        teardown = function () { h.dispose(); };
      }
    }

    const inp = $('#nq-v', main);
    inp.addEventListener('input', function () { value = inp.value; });
    inp.addEventListener('keydown', function (e) { if (e.key === 'Enter') check(); });

    $('#nq-check', main).addEventListener('click', check);
    const hb = $('#nq-hint', main);
    if (hb) hb.addEventListener('click', function () {
      P.numeric = P.numeric || {};
      P.numeric[l.id] = Object.assign({}, P.numeric[l.id], { hint: true });
      saved.hint = true;
      saveSoon();
      paint();
    });
  }

  function check() {
    /* "3,44" is a decimal in most of the world and a thousands separator in the
       rest, and guessing wrong is worse than asking: stripping it silently turned a
       correct 3,44 into 344 and then explained, confidently, that it was out by a
       factor of a hundred. */
    const raw = String(value).trim();
    if (/,/.test(raw)) {
      verdict = { ok: false, head: 'Use a full stop for the decimal point.',
                  body: 'A comma means different things in different places, so this box ' +
                        'will not guess. Write ' + String(l.answer) + '-style: digits, a full stop, digits.' };
      paint();
      return;
    }
    const x = Number(raw);
    if (!raw || !isFinite(x)) {
      verdict = { ok: false, head: 'That is not a number.',
                  body: 'Type a plain decimal \u2014 no units, no thousands separators.' };
      paint();
      return;
    }
    if (close(x)) {
      verdict = { ok: true };
      P.numeric = P.numeric || {};
      P.numeric[l.id] = Object.assign({}, P.numeric[l.id], { v: raw, ok: true });
      saveSoon();
      if (completeLesson(l.id)) toast('Correct \u00b7 +' + XP.numeric + ' XP', true);
      renderRail();
      paint();
      return;
    }
    /* A wrong number is more informative than a wrong word: the RATIO to the right
       answer usually names the mistake outright. */
    const r = l.answer === 0 ? Infinity : x / l.answer;
    let head = 'Not quite.';
    let body = l.wrong || 'Check the arithmetic and try again.';
    const near = function (v, t) { return Math.abs(r - v) <= (t || 0.04) * v; };
    if (near(1000) || near(0.001)) { head = 'Right number, wrong scale.'; body = 'That is out by a factor of a thousand \u2014 a prefix went astray. Milli, micro and kilo are the usual suspects.'; }
    else if (near(2 * Math.PI) || near(1 / (2 * Math.PI))) { head = 'A factor of 2π is missing.'; body = 'Angular frequency ω is 2πf. Whichever of the two the formula wants, it wants only that one.'; }
    else if (near(1000000) || near(0.000001)) { head = 'Out by a million.'; body = 'Two prefixes have gone the same way. Write every quantity in base units once, then convert at the end.'; }
    else if (Math.abs(r + 1) < 0.04) { head = 'The sign is inverted.'; body = 'The magnitude is right. Check which node you measured against, or which way the current was defined.'; }
    else if (near(2) || near(0.5)) { head = 'Out by a factor of two.'; body = 'A halving or a doubling has gone the wrong way \u2014 a peak against an amplitude, or one arm of a pair counted once instead of twice.'; }
    verdict = { ok: false, head: head, body: body };
    P.numeric = P.numeric || {};
    /* Keep `ok` if it was ever earned. Overwriting it with a later wrong attempt made
       the unit reopen pre-filled with a wrong answer under a "Solved" badge. */
    P.numeric[l.id] = Object.assign({}, P.numeric[l.id], { v: raw });
    saveSoon();
    paint();
  }

  paint();
}

/* ---------- lesson: symbol drill ----------
   Recognition is a separate skill from calculation and it is usually left to
   osmosis. Pick a label, tap the symbol it belongs to; tap a placed label to take it
   back. Everything is drawn from the same symbol table, so a drill can never show a
   symbol the rest of the app draws differently. */
function renderMatch(main, l) {
  const saved = (P.match && P.match[l.id]) || {};
  const placed = {};
  (l.items || []).forEach(function (_, i) {
    /* A saved index can outlive the labels it referred to if the unit is re-authored;
       an out-of-range one used to render the string "undefined" and still count as
       placed. Treat anything that does not name a current label as empty. */
    const v = saved[i];
    placed[i] = (typeof v === 'number' && v >= 0 && v < (l.labels || []).length) ? v : null;
  });
  let armed = null;
  let checked = false;

  function used(li) {
    return Object.keys(placed).some(function (k) { return placed[k] === li; });
  }
  function filled_() {
    const o = {};
    Object.keys(placed).forEach(function (k) { if (placed[k] !== null) o[k] = placed[k]; });
    return o;
  }

  function paint() {
    const done = !!P.completed[l.id];
    const items = l.items || [];
    const filled = items.filter(function (_, i) { return placed[i] !== null; }).length;
    const right = items.filter(function (it, i) { return placed[i] === it.a; }).length;

    main.innerHTML = '<div class="page reading">' +
      lessonHeader(l) +
      '<div class="article">' + renderMd(lessonMd(l)) + '</div>' +
      '<h3 class="q-prompt">' + mdInline(l.prompt || '') + '</h3>' +
      '<p class="q-note">Tap a placed label to take it back. Every label is used exactly once.</p>' +
      '<div class="mt-labels">' +
        (l.labels || []).map(function (lb, li) {
          return '<button type="button" class="mt-lb' + (armed === li ? ' armed' : '') +
            (used(li) ? ' spent' : '') + '" data-lb="' + li + '"' +
            ' aria-pressed="' + (armed === li ? 'true' : 'false') + '"' +
            (used(li) ? ' disabled' : '') + '>' + esc(lb) + '</button>';
        }).join('') +
      '</div>' +
      '<div class="mt-grid">' +
        items.map(function (it, i) {
          const v = placed[i];
          const state = !checked ? (v === null ? '' : ' filled')
            : (v === it.a ? ' right' : ' wrong');
          return '<button type="button" class="mt-card' + state + '" data-item="' + i + '"' +
            ' aria-label="Symbol ' + (i + 1) + ' of ' + items.length +
            (v === null ? ', empty' : ', labelled ' + esc(l.labels[v])) + '">' +
            '<canvas class="mt-cv" data-sym="' + esc(it.sym) + '"></canvas>' +
            '<div class="mt-slot">' + (v === null ? '\u2014' : esc(l.labels[v])) + '</div>' +
          '</button>';
        }).join('') +
      '</div>' +
      '<div class="q-acts">' +
        '<button class="btn success" id="mt-check"' + (filled === items.length ? '' : ' disabled') + '>' +
          (checked ? 'Check again' : 'Check') + '</button>' +
        (checked ? '<button class="btn dark" id="mt-reset">Clear</button>' : '') +
        '<span class="q-count">' + (checked ? right + ' / ' + items.length + ' right'
          : filled + ' / ' + items.length + ' placed') + '</span>' +
      '</div>' +
      (checked
        ? '<div class="mt-fb">' + items.map(function (it, i) {
            const ok = placed[i] === it.a;
            return '<div class="blk-row ' + (ok ? 'right' : 'wrong') + '">' +
              '<span class="gmark ' + (ok ? 'done' : 'fail') + '"></span>' +
              '<div><b>' + esc(l.labels[it.a]) + '</b>' +
              (ok ? '' : ' <span class="blk-yours">you put ' +
                (placed[i] === null ? 'nothing' : esc(l.labels[placed[i]])) + '</span>') +
              '<p>' + mdInline(it.why || '') + '</p></div>' +
            '</div>';
          }).join('') + '</div>'
        : '') +
      footNav(l, done ? '<span class="done-note">\u2713 Named</span>' : '') +
    '</div>';

    wireCrumb(main, l);
    wireFootNav(main, l);

    const cvs = $all('.mt-cv', main);
    const paintAll = function () {
      const ink = getComputedStyle(document.documentElement).getPropertyValue('--ink').trim() || '#EDEFF3';
      cvs.forEach(function (cv) { Symbols.paint(cv, cv.dataset.sym, ink); });
    };
    paintAll();
    requestAnimationFrame(paintAll);        /* once more after layout settles */
    /* The grid is auto-fit, so the cards change width with the window and the canvas
       backing store has to be resized with them — otherwise the symbols stay at the
       first width and blur or clip. */
    const mro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(paintAll) : null;
    if (mro && cvs[0]) mro.observe(cvs[0]);
    teardown = function () { if (mro) mro.disconnect(); };

    $all('[data-lb]', main).forEach(function (b) {
      b.addEventListener('click', function () {
        const li = +b.dataset.lb;
        armed = armed === li ? null : li;
        paint();
      });
    });
    $all('[data-item]', main).forEach(function (card) {
      card.addEventListener('click', function () {
        const i = +card.dataset.item;
        if (placed[i] !== null) { placed[i] = null; }
        else if (armed !== null) { placed[i] = armed; armed = null; }
        else return;
        P.match = P.match || {};
        /* Only the slots that actually hold a label are stored. Writing an explicit
           null for every empty slot makes the two-device merge — which takes the
           union of the two objects — overwrite a real placement with a null. */
        P.match[l.id] = filled_();
        checked = false;
        saveSoon();
        paint();
      });
    });
    const ck = $('#mt-check', main);
    if (ck) ck.addEventListener('click', function () {
      checked = true;
      const got = items.filter(function (it, i) { return placed[i] === it.a; }).length;
      paint();
      if (got === items.length) {
        if (completeLesson(l.id)) toast('Every symbol named \u00b7 +' + XP.match + ' XP', true);
        renderRail();
      }
    });
    const rs = $('#mt-reset', main);
    if (rs) rs.addEventListener('click', function () {
      items.forEach(function (_, i) { placed[i] = null; });
      P.match = P.match || {};
      P.match[l.id] = {};
      checked = false; armed = null;
      saveSoon();
      paint();
    });
  }

  paint();
}

/* ---------- lesson: hit the target ----------
   A sandbox with a goal. The sliders are the same, the plot is the same, and the
   difference is that the exercise states constraints which all have to hold at once —
   which is what turns "see what this does" into a design problem, because in every
   real one the constraints pull against each other. */
function renderTune(main, l) {
  const spec = Tune.get(l.model);
  const saved = (P.tune && P.tune[l.id]) || {};
  const v = {};
  (spec ? spec.params : []).forEach(function (p) {
    const start = (l.initial && l.initial[p.k] !== undefined) ? l.initial[p.k] : p.def;
    v[p.k] = saved.v && saved.v[p.k] !== undefined ? saved.v[p.k] : start;
  });
  const consts = Object.assign({}, spec && spec.constants, l.constants || {});
  let plotCv = null;

  function readouts() { return spec.compute(v, consts); }

  function holdsC(c, x) {
    if (c.max !== undefined && c.min !== undefined) return x >= c.min && x <= c.max;
    if (c.max !== undefined) return x <= c.max;
    if (c.min !== undefined) return x >= c.min;
    if (c.eq !== undefined) return Math.abs(x - c.eq) <= (c.tol === undefined ? 0.01 : c.tol);
    return false;
  }

  function tests() {
    const out = readouts();
    return (l.constraints || []).map(function (c) {
      const r = out[c.k];
      const x = r ? r.value : NaN;
      return { c: c, ok: r ? holdsC(c, x) : false, got: x, r: r };
    });
  }

  function drawPlot() {
    if (!plotCv || !spec.plot) return;
    const pl = spec.plot(v, consts);
    const dpr = window.devicePixelRatio || 1;
    const w = plotCv.clientWidth || 600, h = plotCv.clientHeight || 300;
    plotCv.width = Math.round(w * dpr); plotCv.height = Math.round(h * dpr);
    const ctx = plotCv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const f = Sandbox.frame(ctx, w, h, {
      xRange: pl.xRange, yRange: pl.yRange, logX: !!pl.logX,
      xTicks: 6, yTicks: 5, margin: { l: 52, r: 16, t: 16, b: 30 },
    });
    /* the target band, drawn first so the curve sits on top of it */
    (l.constraints || []).forEach(function (c) {
      if (c.k !== (l.plotKey || 'vout') || c.eq === undefined) return;
      ctx.save();
      ctx.strokeStyle = f.P.amber;
      ctx.setLineDash([7, 6]);
      ctx.lineWidth = 1.6;
      ctx.beginPath();
      ctx.moveTo(f.x0, f.fy(c.eq)); ctx.lineTo(f.x1, f.fy(c.eq));
      ctx.stroke();
      ctx.restore();
    });
    f.line(pl.points, f.P.accent, 2.2);
    if (pl.at) f.dot(pl.at[0], pl.at[1], f.P.accent, 5);
    const cap = $('#tn-cap', main);
    if (cap) cap.textContent = pl.caption || '';
  }

  function refresh() {
    const out = readouts();
    const ts = tests();
    const box = $('#tn-read', main);
    if (box) {
      box.innerHTML = Object.keys(out).map(function (k) {
        const r = out[k];
        const t = ts.find(function (x) { return x.c.k === k; });
        /* A readout is graded on its exact value and displayed rounded, so the two
           can disagree: 1.0004 mA shows as 1.000 and fails a 1.00 cap, which reads as
           the app being broken. Add digits only when that actually happens — when the
           number as displayed would satisfy the constraint the raw value fails. */
        let dp = r.dp;
        if (t && !t.ok) {
          const shown = Number((+r.value).toFixed(r.dp));
          if (holdsC(t.c, shown)) dp = r.dp + 3;
        }
        return '<div class="tn-r' + (t ? (t.ok ? ' ok' : ' no') : '') + '">' +
          '<span>' + esc(r.label) + '</span><b>' + (+r.value).toFixed(dp) +
          (r.unit ? ' ' + r.unit : '') + '</b></div>';
      }).join('');
    }
    const st = $('#tn-state', main);
    if (st) {
      const pass = ts.length && ts.every(function (t) { return t.ok; });
      st.className = 'tn-goal' + (pass ? ' met' : '');
      st.innerHTML = (l.constraints || []).map(function (c, i) {
        const t = ts[i];
        return '<span class="tn-c' + (t && t.ok ? ' ok' : '') + '">' +
          (t && t.ok ? '\u2713 ' : '\u00b7 ') + esc(c.label) + '</span>';
      }).join('');
    }
    drawPlot();
    const ck = $('#tn-check', main);
    if (ck) ck.disabled = false;
  }

  function paint() {
    const done = !!P.completed[l.id];
    if (!spec) {
      main.innerHTML = '<div class="page reading">' + lessonHeader(l) +
        '<div class="pcard warn"><div class="pcard-h"><span class="dot"></span><b>Model missing</b></div>' +
        '<p>This unit asks for the <code>' + esc(l.model || '?') + '</code> model, which is not in this build.</p></div>' +
        footNav(l, '') + '</div>';
      wireCrumb(main, l); wireFootNav(main, l);
      return;
    }
    main.innerHTML = '<div class="page reading">' +
      lessonHeader(l) +
      '<div class="article">' + renderMd(lessonMd(l)) + '</div>' +
      '<h3 class="q-prompt">' + mdInline(l.prompt || '') + '</h3>' +
      (l.note ? '<p class="q-note">' + mdInline(l.note) + '</p>' : '') +
      '<div class="tune">' +
        '<div class="tn-plot"><div class="tn-cap" id="tn-cap"></div><canvas id="tn-cv"></canvas></div>' +
        '<div class="tn-side">' +
          spec.params.map(function (p) {
            return '<div class="tn-p">' +
              '<div class="tn-ph"><span>' + esc(p.label) + '</span><b data-out="' + p.k + '">' +
                v[p.k] + (p.unit ? ' ' + p.unit : '') + '</b></div>' +
              '<input type="range" data-k="' + p.k + '" min="' + p.min + '" max="' + p.max +
                '" step="' + p.step + '" value="' + v[p.k] + '">' +
            '</div>';
          }).join('') +
          '<div class="tn-reads" id="tn-read"></div>' +
          '<div class="tn-goal" id="tn-state"></div>' +
        '</div>' +
      '</div>' +
      '<div class="q-acts">' +
        '<button class="btn success" id="tn-check">Check</button>' +
        '<button class="btn dark" id="tn-reset">Reset</button>' +
      '</div>' +
      footNav(l, done ? '<span class="done-note">\u2713 Met</span>' : '') +
    '</div>';

    wireCrumb(main, l);
    wireFootNav(main, l);
    plotCv = $('#tn-cv', main);

    $all('input[type=range]', main).forEach(function (sl) {
      sl.addEventListener('input', function () {
        v[sl.dataset.k] = Number(sl.value);
        const p = spec.params.find(function (x) { return x.k === sl.dataset.k; });
        const lab = $('[data-out="' + sl.dataset.k + '"]', main);
        if (lab) lab.textContent = sl.value + (p && p.unit ? ' ' + p.unit : '');
        P.tune = P.tune || {};
        P.tune[l.id] = { v: Object.assign({}, v) };
        saveSoon();
        refresh();
      });
    });
    $('#tn-check', main).addEventListener('click', function () {
      const ts = tests();
      const pass = ts.length && ts.every(function (t) { return t.ok; });
      if (pass) {
        const first = completeLesson(l.id);
        renderRail();
        /* One toast, not two: the second used to replace the first immediately, so
           the XP award was never actually seen. And repaint, or the footer keeps
           saying the unit is unfinished after it has just been finished. */
        toast(first ? 'All constraints hold \u00b7 +' + XP.tune + ' XP'
                    : 'All constraints hold at once.', true);
        paint();
        return;
      } else {
        const bad = ts.filter(function (t) { return !t.ok; });
        toast(bad.length + ' constraint' + (bad.length > 1 ? 's' : '') + ' still unmet: ' +
          bad.map(function (t) { return t.c.label; }).join('; '));
      }
      refresh();
    });
    $('#tn-reset', main).addEventListener('click', function () {
      spec.params.forEach(function (p) {
        v[p.k] = (l.initial && l.initial[p.k] !== undefined) ? l.initial[p.k] : p.def;
      });
      P.tune = P.tune || {};
      P.tune[l.id] = { v: Object.assign({}, v) };
      saveSoon();
      paint();
    });

    refresh();
    /* paint() is re-entrant — Reset and Check both call it — so the previous
       observer has to go before a new one is made, or every press leaves one behind
       redrawing a canvas that is no longer on the page. */
    if (teardown) { try { teardown(); } catch (e) {} }
    const ro = typeof ResizeObserver !== 'undefined' ? new ResizeObserver(drawPlot) : null;
    if (ro && plotCv) ro.observe(plotCv);
    teardown = function () { if (ro) ro.disconnect(); };
  }

  paint();
}

/* ---------- lesson: fill the blanks ----------
   Taken from the Voltaic design: a listing with holes in it that you click to fill.
   It reads as one artefact rather than a list of questions, and because a blank is
   just a slot with options it works on an equation as readily as on code — which is
   the point, since a physics module should not have to ask its questions in Python.

   Answering is one click, so it is cheap to attempt and cheap to be wrong; the
   explanation for the option you chose is what carries the teaching. */
function renderBlanks(main, l) {
  const state = (P.blanks && P.blanks[l.id]) || {};
  const picked = {};
  (l.blanks || []).forEach(function (b, i) { picked[i] = state[i] === undefined ? null : state[i]; });
  let open = null;          /* which blank's option list is showing */
  let checked = false;

  function slotHtml(b, i) {
    const val = picked[i];
    const isRight = val !== null && val === b.a;
    const cls = !checked ? (val === null ? '' : ' filled')
      : (isRight ? ' right' : ' wrong');
    const label = val === null ? (b.hole || '?') : b.opts[val];
    return '<button class="blk' + cls + (open === i ? ' open' : '') + '" data-blk="' + i + '">' +
      esc(label) + '</button>';
  }

  /* the listing is authored with ___ where each blank goes, in order */
  function listing() {
    const parts = String(l.listing || '').split('___');
    let out = '';
    for (let i = 0; i < parts.length; i++) {
      out += Highlight.render(parts[i], l.lang || 'text');
      if (i < parts.length - 1 && l.blanks[i]) out += slotHtml(l.blanks[i], i);
    }
    return out;
  }

  function chooser() {
    if (open === null) return '';
    const b = l.blanks[open];
    return '<div class="blk-pick">' +
      '<div class="blk-pick-h">' + esc(b.prompt || 'Which one belongs here?') + '</div>' +
      b.opts.map(function (o, oi) {
        return '<button class="blk-opt' + (picked[open] === oi ? ' on' : '') +
          '" data-opt="' + oi + '">' + esc(o) + '</button>';
      }).join('') +
    '</div>';
  }

  function feedback() {
    if (!checked) return '';
    return '<div class="blk-fb">' + l.blanks.map(function (b, i) {
      const ok = picked[i] === b.a;
      return '<div class="blk-row ' + (ok ? 'right' : 'wrong') + '">' +
        '<span class="gmark ' + (ok ? 'done' : 'fail') + '"></span>' +
        '<div><b>' + esc(b.opts[b.a]) + '</b>' +
        (ok ? '' : ' <span class="blk-yours">you chose ' +
          (picked[i] === null ? 'nothing' : esc(b.opts[picked[i]])) + '</span>') +
        '<p>' + mdInline((picked[i] !== null && b.whys && b.whys[picked[i]]) || b.why) + '</p></div>' +
      '</div>';
    }).join('') + '</div>';
  }

  function paint() {
    const filled = l.blanks.filter(function (_, i) { return picked[i] !== null; }).length;
    const right = l.blanks.filter(function (b, i) { return picked[i] === b.a; }).length;
    main.innerHTML = '<div class="page reading">' +
      lessonHeader(l) +
      '<div class="article">' + renderMd(lessonMd(l)) + '</div>' +
      '<div class="blk-wrap">' +
        '<div class="blk-bar"><span class="blk-file">' + esc(l.caption || 'fill in the blanks') + '</span>' +
          '<span class="blk-count">' + (checked ? right + ' / ' + l.blanks.length + ' right'
            : filled + ' / ' + l.blanks.length + ' filled') + '</span></div>' +
        '<pre class="blk-listing"><code>' + listing() + '</code></pre>' +
      '</div>' +
      chooser() +
      '<div class="blk-acts">' +
        '<button class="btn success" id="blk-check"' + (filled === l.blanks.length ? '' : ' disabled') + '>' +
          (checked ? 'Check again' : 'Check') + '</button>' +
        (checked ? '<button class="btn dark" id="blk-retry">Clear and retry</button>' : '') +
      '</div>' +
      feedback() +
      footNav(l, P.completed[l.id] ? '<span class="done-note">\u2713 Filled</span>' : '') +
    '</div>';

    wireCrumb(main, l);
    wireFootNav(main, l);

    $all('[data-blk]', main).forEach(function (b) {
      b.addEventListener('click', function () {
        const i = +b.dataset.blk;
        open = (open === i) ? null : i;
        paint();
      });
    });
    $all('[data-opt]', main).forEach(function (b) {
      b.addEventListener('click', function () {
        picked[open] = +b.dataset.opt;
        P.blanks = P.blanks || {};
        P.blanks[l.id] = Object.assign({}, picked);
        saveSoon();
        open = null;
        checked = false;
        paint();
      });
    });
    const chk = $('#blk-check', main);
    if (chk) chk.addEventListener('click', function () {
      checked = true;
      const got = l.blanks.filter(function (b, i) { return picked[i] === b.a; }).length;
      paint();
      if (got === l.blanks.length) {
        if (completeLesson(l.id)) toast('All blanks filled \u00b7 +' + XP.blanks + ' XP', true);
        renderRail();
      }
    });
    const rt = $('#blk-retry', main);
    if (rt) rt.addEventListener('click', function () {
      l.blanks.forEach(function (_, i) { picked[i] = null; });
      P.blanks = P.blanks || {};
      P.blanks[l.id] = {};
      checked = false;
      saveSoon();
      paint();
    });
  }

  paint();
}

/* ---------- lesson: build a circuit ----------
   The schematic is the answer. Checks measure what the learner built rather than
   comparing it to a reference drawing, so two different but equally correct filters
   both pass — which is the whole reason to grade behaviour instead of shape. */
function renderBuild(main, l) {
  const saved = (P.build && P.build[l.id]) || null;
  const start = saved || l.start || { parts: [], wires: [] };
  let results = null;

  function checksHtml() {
    if (!results) {
      return '<div class="checks"><div class="ck-head">' + l.checks.length +
        ' to pass</div>' + l.checks.map(function (c) {
          return '<div class="check"><span class="gmark"></span><span class="name">' +
            esc(c.name) + '</span></div>';
        }).join('') + '</div>';
    }
    const passed = results.filter(function (r) { return r.pass; }).length;
    return '<div class="checks"><div class="ck-head">' + passed + ' / ' + results.length +
      ' passing</div>' + results.map(function (r) {
        return '<div class="check ' + (r.pass ? 'pass' : 'fail') + '">' +
          '<span class="gmark ' + (r.pass ? 'done' : 'fail') + '"></span>' +
          '<span class="name">' + esc(r.name) + '</span>' +
          (r.pass ? '' : '<span class="msg">' + esc(r.message || '') + '</span>') +
        '</div>';
      }).join('') + '</div>';
  }

  function paint() {
    main.innerHTML = '<div class="page reading">' +
      lessonHeader(l) +
      '<div class="article">' + renderMd(lessonMd(l)) + '</div>' +
      '<div id="build-mount"></div>' +
      '<div class="build-acts">' +
        '<button class="btn success" id="build-run">Check the circuit</button>' +
        '<button class="btn dark" id="build-reset">Start over</button>' +
      '</div>' +
      '<div id="build-checks">' + checksHtml() + '</div>' +
      (l.hints && l.hints.length
        ? '<div class="helpers"><button class="btn dark" id="hint-btn">Show a hint</button>' +
          '<div id="hint-body" hidden>' + renderMd(l.hints.map(function (h, i) {
            return (i + 1) + '. ' + h;
          }).join('\n')) + '</div></div>'
        : '') +
      footNav(l, P.completed[l.id] ? '<span class="done-note">\u2713 Built</span>' : '') +
    '</div>';

    wireCrumb(main, l);
    wireFootNav(main, l);

    const handle = createCircuit($('#build-mount', main), {
      model: model,
      onChange: function (m2) {
        model = m2;
        P.build = P.build || {};
        P.build[l.id] = m2;
        saveSoon();
      },
    });
    teardown = function () { handle.dispose(); };

    const hb = $('#hint-btn', main);
    if (hb) hb.addEventListener('click', function () {
      const body = $('#hint-body', main);
      body.hidden = !body.hidden;
      hb.textContent = body.hidden ? 'Show a hint' : 'Hide the hint';
    });

    $('#build-reset', main).addEventListener('click', function () {
      model = JSON.parse(JSON.stringify(l.start || { parts: [], wires: [] }));
      P.build = P.build || {};
      P.build[l.id] = model;
      results = null;
      saveSoon();
      paint();
    });

    $('#build-run', main).addEventListener('click', function () {
      results = runCircuitChecks(model, l.checks || []);
      $('#build-checks', main).innerHTML = checksHtml();
      const passed = results.filter(function (r) { return r.pass; }).length;
      if (passed === results.length && results.length) {
        if (completeLesson(l.id)) toast('Circuit built \u00b7 +' + XP.build + ' XP', true);
        renderRail();
      }
    });
  }

  let model = JSON.parse(JSON.stringify(start));
  paint();
}

/* ---------- lesson: sandbox ----------
   The intuition step. Nothing is graded: the learner moves a parameter and watches
   what happens, and the unit is complete once they say they have seen it. Making it
   scored would turn playing into guessing, which is the opposite of the point. */
function renderSandbox(main, l) {
  const spec = Sandbox.get(l.sandbox);
  const done = !!P.completed[l.id];

  main.innerHTML = '<div class="page reading">' +
    lessonHeader(l) +
    '<div class="article">' + renderMd(lessonMd(l)) + '</div>' +
    (spec
      ? '<div class="sbx-host" id="sbx-host"></div>' +
        (l.notice && l.notice.length
          ? '<div class="sbx-notice"><h4>Push on it</h4><ul>' +
            l.notice.map(function (n) { return '<li>' + mdInline(n) + '</li>'; }).join('') +
            '</ul></div>'
          : '')
      : '<div class="pcard warn"><div class="pcard-h"><span class="dot"></span><b>Visualiser missing</b></div>' +
        '<p>This unit asks for the <code>' + esc(l.sandbox || '?') + '</code> visualiser, which is not in this build.</p></div>') +
    footNav(l, done
      ? '<span class="done-note">\u2713 Explored</span>'
      : '<button class="btn success" id="mark-explored">I have seen it</button>') +
  '</div>';

  wireCrumb(main, l);
  wireFootNav(main, l);

  const host = $('#sbx-host', main);
  if (spec && host) {
    const handle = Sandbox.mount(host, spec, l.initial || {});
    /* go() clears exactly one teardown slot; teardownFns is never drained, so the
       canvas and its ResizeObserver have to be released here or they outlive the view */
    teardown = function () { handle.dispose(); };
  }

  const mk = $('#mark-explored', main);
  if (mk) {
    mk.addEventListener('click', function () {
      if (completeLesson(l.id)) toast('Explored \u00b7 +' + XP.sandbox + ' XP', true);
      renderRail();
      go({ view: 'lesson', id: l.id });
    });
  }
}

/* ---------- lesson: guided derivation ----------
   The scaffolded middle step. Each stage asks for the next expression rather than
   showing it; SymPy decides equivalence, so any correct algebra is accepted. A step
   that will not come can be broken into smaller ones rather than surrendered. */
/* A placeholder is meant to show the *shape* of an answer, not the answer. Almost the
   whole catalogue — 337 of 376 steps, including the first course, which every later
   one copied — set it equal to the answer, so the thing being asked for was printed
   in the box before the learner typed a character. Rejecting it here fixes every one
   of them at once, and tools/verify_derivations.py fails the build if it comes back. */
function placeholderFor(st) {
  const ph = String(st.placeholder || '').replace(/\s+/g, '');
  const an = String(st.answer || '').replace(/\s+/g, '');
  if (ph && ph !== an) return st.placeholder;
  return 'your expression in LaTeX, e.g. \\frac{a}{b + c}';
}

function renderDerive(main, l) {
  const steps = l.steps || [];
  const state = (P.derive && P.derive[l.id]) || { done: 0 };
  let reached = Math.min(state.done || 0, steps.length);

  function stepHtml(st, i) {
    const solved = i < reached;
    const active = i === reached;
    const locked = i > reached;
    return '<section class="dv-step' + (solved ? ' solved' : active ? ' active' : ' locked') + '" data-i="' + i + '">' +
      '<div class="dv-head">' +
        '<span class="dv-n">' + (solved ? '\u2713' : (i + 1)) + '</span>' +
        '<div class="dv-ask">' + (locked ? '<span class="dv-hidden">Unlocks when the step above is done</span>' : renderMd(st.prompt)) + '</div>' +
      '</div>' +
      (locked ? '' :
        (st.given ? '<div class="dv-given">' + renderMd(st.given) + '</div>' : '') +
        (solved
          ? '<div class="dv-answer">' + MathML.render(st.answer, true) + '</div>'
          : '<div class="dv-work">' +
              '<label class="dv-in"><span>Your expression, in LaTeX</span>' +
                '<input type="text" data-ans="' + i + '" placeholder="' + esc(placeholderFor(st)) + '" autocomplete="off" spellcheck="false"></label>' +
              '<div class="dv-preview" data-prev="' + i + '"></div>' +
              '<div class="dv-acts">' +
                '<button class="btn success" data-check="' + i + '">Check</button>' +
                (st.deconstruct && st.deconstruct.length
                  ? '<button class="btn dark" data-decon="' + i + '">Deconstruct this step</button>' : '') +
                (st.hint ? '<button class="btn dark" data-hint="' + i + '">Hint</button>' : '') +
              '</div>' +
              '<div class="dv-msg" data-msg="' + i + '"></div>' +
              '<div class="dv-sub" data-sub="' + i + '" hidden>' +
                (st.deconstruct || []).map(function (d, k) {
                  return '<div class="dv-substep"><b>' + (k + 1) + '</b><div>' + renderMd(d) + '</div></div>';
                }).join('') +
              '</div>' +
            '</div>')) +
    '</section>';
  }

  function paint() {
    const allDone = reached >= steps.length;
    main.innerHTML = '<div class="page reading">' +
      lessonHeader(l) +
      '<div class="article">' + renderMd(lessonMd(l)) + '</div>' +
      '<div class="dv-prog"><div class="bar"><i style="width:' +
        (steps.length ? Math.round(reached / steps.length * 100) : 0) + '%"></i></div>' +
        '<span>' + reached + ' of ' + steps.length + ' steps</span></div>' +
      '<div class="dv-steps">' + steps.map(stepHtml).join('') + '</div>' +
      (allDone && l.closing ? '<div class="dv-closing">' + renderMd(l.closing) + '</div>' : '') +
      footNav(l, allDone
        ? '<span class="done-note">\u2713 Derived</span>'
        : '<span class="dv-left">' + (steps.length - reached) + ' step' + (steps.length - reached === 1 ? '' : 's') + ' to go</span>') +
    '</div>';

    wireCrumb(main, l);
    wireFootNav(main, l);
    wire();
  }

  function wire() {
    const i = reached;
    const input = $('[data-ans="' + i + '"]', main);
    if (!input) return;
    const prev = $('[data-prev="' + i + '"]', main);
    const msg = $('[data-msg="' + i + '"]', main);
    const st = steps[i];

    const preview = debounce(function () {
      prev.innerHTML = input.value.trim() ? MathML.render(input.value, false) : '';
    }, 140);
    input.addEventListener('input', preview);
    input.focus();

    const decon = $('[data-decon="' + i + '"]', main);
    if (decon) decon.addEventListener('click', function () {
      const sub = $('[data-sub="' + i + '"]', main);
      sub.hidden = !sub.hidden;
      decon.textContent = sub.hidden ? 'Deconstruct this step' : 'Hide the breakdown';
    });

    const hint = $('[data-hint="' + i + '"]', main);
    if (hint) hint.addEventListener('click', function () {
      msg.className = 'dv-msg hint';
      msg.innerHTML = mdInline(st.hint);
    });

    const btn = $('[data-check="' + i + '"]', main);
    let busy = false;
    async function check() {
      if (busy) return;
      const typed = input.value.trim();
      if (!typed) { msg.className = 'dv-msg bad'; msg.textContent = 'Type an expression first.'; return; }
      busy = true;
      btn.disabled = true;
      msg.className = 'dv-msg';
      msg.textContent = 'Checking\u2026';
      const r = await MathCheck.check(typed, st.answer, { vars: l.vars || [], tol: st.tol });
      busy = false;
      btn.disabled = false;
      if (r.ok) {
        reached = i + 1;
        P.derive = P.derive || {};
        P.derive[l.id] = { done: reached, t: Date.now() };
        saveSoon();
        if (reached >= steps.length) {
          if (completeLesson(l.id)) toast('Derivation complete \u00b7 +' + XP.derive + ' XP', true);
          renderRail();
        }
        paint();
        return;
      }
      msg.className = 'dv-msg bad';
      msg.innerHTML = esc(r.message);
    }
    btn.addEventListener('click', check);
    input.addEventListener('keydown', function (e) { if (e.key === 'Enter') check(); });
  }

  paint();
  /* SymPy is a large download; start it while the learner reads the first step */
  MathCheck.warm();
}

function renderCode(main, l) {
  const files = currentFiles(l);
  let active = 0;
  let running = false;
  let hintsShown = (P.code[l.id] && P.code[l.id].hints) || 0;
  const kind = l.lang === 'python' ? 'python' : (l.lang === 'web' ? 'web' : 'js');
  const hasPreview = kind === 'web';

  main.innerHTML =
  '<div class="lesson-code">' +
    '<div class="mobile-tabs">' +
      '<button data-mt="task" class="active">Task</button>' +
      '<button data-mt="code">Code</button>' +
      '<button data-mt="output">Output<span class="badge" id="mt-badge"></span></button>' +
    '</div>' +
    '<div class="task-pane" id="task-pane">' +
      lessonHeader(l) +
      '<div class="article">' + renderMd(lessonMd(l)) + '</div>' +
      '<div class="checks" id="checks-main"></div>' +
      '<div class="helpers">' +
        (l.hints && l.hints.length ? '<div class="helper"><button id="hint-btn"><span>💡 Hint</span><span class="k" id="hint-k"></span></button><div class="hint-body" id="hint-body" hidden></div></div>' : '') +
        (l.solution && l.solution.length ? '<div class="helper"><button id="sol-btn"><span>🔒 Solution</span><span class="k">reveal when stuck</span></button><div class="sol-body" id="sol-body" hidden></div></div>' : '') +
      '</div>' +
      footNav(l, P.completed[l.id] ? '<span class="done-note">✓ Solved</span>' : '') +
    '</div>' +
    '<div class="workbench" id="workbench">' +
      '<div class="wb-bar">' +
        '<div class="ftabs" id="ftabs"></div>' +
        '<div class="wb-actions">' +
          (kind === 'python' ? '<span class="rt-status" id="rt-status"><i></i><span id="rt-label">python</span></span>' : '') +
          '<button class="btn dark sm" id="reset-btn">Reset</button>' +
          '<button class="btn run" id="run-btn">▶ Run</button>' +
        '</div>' +
      '</div>' +
      '<div class="wb-editor"><div id="ed-mount"></div></div>' +
      '<div class="wb-resize" id="wb-resize"></div>' +
      '<div class="wb-panel" id="wb-panel">' +
        '<div class="ptabs">' +
          '<button class="ptab active" data-pt="console">Console</button>' +
          '<button class="ptab" data-pt="checks">Checks<span class="badge" id="pt-badge" hidden></span></button>' +
          (hasPreview ? '<button class="ptab" data-pt="preview">Preview</button>' : '') +
          '<span class="spacer"></span><span class="note" id="panel-note"></span>' +
        '</div>' +
        '<div class="pbody">' +
          '<div class="console" id="console"><span class="empty">Press Run — output appears here.</span></div>' +
          '<div class="checks-mini" id="checks-mini" hidden></div>' +
          '<div class="preview-wrap" id="preview-wrap" ' + (hasPreview ? 'hidden' : 'hidden style="visibility:hidden"') + '></div>' +
        '</div>' +
      '</div>' +
      '<div class="wb-foot">' +
        '<span class="foot-hint"><kbd>Ctrl</kbd>+<kbd>Enter</kbd> run · <kbd>Ctrl</kbd>+<kbd>Space</kbd> suggest</span>' +
        '<span class="spacer"></span>' +
        '<button class="btn dark sm" id="indent-btn">⇥ Indent</button>' +
      '</div>' +
    '</div>' +
  '</div>';

  wireCrumb(main, l);
  wireFootNav(main, l);

  /* editor */
  const ed = createEditor($('#ed-mount'), {
    lang: langOfFile(files[active].name),
    onRun: doRun,
    onSave: function () { persist(); saveNow(); toast('Saved'); },
    onChange: function (v) {
      if (!files[active].ro) { files[active].content = v; persistSoon(); }
    },
    acExtra: function () {
      return files.map(function (f, i) { return i === active ? '' : f.content; }).join('\n');
    },
  });
  const persistSoon = debounce(persist, 700);
  function persist() {
    const saved = {};
    for (const f of files) if (!f.ro) saved[f.name] = f.content;
    P.code[l.id] = { files: saved, hints: hintsShown, t: Date.now() };   /* t: which device edited last */
    saveSoon();
  }

  function renderFtabs() {
    $('#ftabs').innerHTML = files.map(function (f, i) {
      return '<button class="ftab' + (i === active ? ' active' : '') + (f.ro ? ' ro' : '') + '" data-fi="' + i + '">' +
        esc(f.name) + (f.ro ? '<span class="ro-tag">read-only</span>' : '') + '</button>';
    }).join('');
    $all('.ftab', main).forEach(function (b) {
      b.addEventListener('click', function () { setActive(+b.dataset.fi); });
    });
  }
  function setActive(i) {
    active = i;
    ed.setLang(langOfFile(files[i].name));
    ed.setReadOnly(files[i].ro);
    ed.setValue(files[i].content);
    renderFtabs();
  }
  renderFtabs();
  ed.setReadOnly(files[active].ro);
  ed.setValue(files[active].content);

  /* console */
  let lineCount = 0;
  function clearConsole() { $('#console').innerHTML = ''; lineCount = 0; }
  function logLine(level, text) {
    if (lineCount > 600) return;
    lineCount++;
    const c = $('#console');
    if (!c) return;
    const ln = document.createElement('span');
    ln.className = 'ln ' + level;
    ln.textContent = lineCount > 600 ? '… output truncated …' : text;
    c.appendChild(ln);
    c.scrollTop = c.scrollHeight;
  }

  /* checks */
  function checksBlock(state) {
    const tests = l.tests;
    const passed = state.results ? state.results.filter(function (r) { return r && r.pass; }).length : 0;
    let head = '<h3><span>Checks</span><b' + (state.results && passed === tests.length ? ' class="allgood"' : '') + '>' +
      (state.results ? passed + ' / ' + tests.length : (state.phase === 'running' ? 'running…' : tests.length + ' to pass')) + '</b></h3>';
    let rows = tests.map(function (t, i) {
      const r = state.results && state.results[i];
      const mark = state.phase === 'running' ? 'run' : (r ? (r.pass ? 'done' : 'fail') : '');
      const cls = r ? (r.pass ? 'pass' : 'fail') : '';
      return '<div class="check ' + cls + '"><span class="gmark ' + mark + '"></span><div>' +
        '<div class="name">' + esc(t.name) + '</div>' +
        (r && !r.pass && r.message ? '<div class="msg">' + esc(r.message) + '</div>' : '') +
      '</div></div>';
    }).join('');
    return head + rows;
  }
  function renderChecks(state) {
    const html = checksBlock(state);
    $('#checks-main').innerHTML = html;
    $('#checks-mini').innerHTML = html;
    const b = $('#pt-badge'), mb = $('#mt-badge');
    if (state.results) {
      const passed = state.results.filter(function (r) { return r && r.pass; }).length;
      const good = passed === l.tests.length;
      b.hidden = false;
      b.textContent = passed + '/' + l.tests.length;
      b.className = 'badge ' + (good ? 'good' : 'bad');
      mb.textContent = ' ' + passed + '/' + l.tests.length;
    } else { b.hidden = true; mb.textContent = ''; }
  }
  renderChecks({ phase: 'idle' });

  /* panel tabs */
  function setPtab(which) {
    $all('.ptab', main).forEach(function (b) { b.classList.toggle('active', b.dataset.pt === which); });
    $('#console').hidden = which !== 'console';
    $('#checks-mini').hidden = which !== 'checks';
    const pw = $('#preview-wrap');
    if (hasPreview) pw.hidden = which !== 'preview';
  }
  $all('.ptab', main).forEach(function (b) {
    b.addEventListener('click', function () { setPtab(b.dataset.pt); });
  });

  /* mobile tabs */
  function setMtab(which) {
    $all('.mobile-tabs button', main).forEach(function (b) { b.classList.toggle('active', b.dataset.mt === which); });
    $('#task-pane').classList.toggle('mob-hide', which !== 'task');
    const wb = $('#workbench');
    wb.classList.toggle('mob-hide', which === 'task');
    wb.classList.toggle('mode-code', which === 'code');
    wb.classList.toggle('mode-output', which === 'output');
  }
  $all('.mobile-tabs button', main).forEach(function (b) {
    b.addEventListener('click', function () { setMtab(b.dataset.mt); });
  });
  setMtab(isMobile() ? 'task' : 'code');

  $('#indent-btn').addEventListener('click', function () { ed.insertIndent(); ed.focus(); });

  /* resize */
  (function () {
    const rz = $('#wb-resize'), panel = $('#wb-panel');
    let startY = 0, startH = 0;
    rz.addEventListener('pointerdown', function (e) {
      startY = e.clientY; startH = panel.getBoundingClientRect().height;
      rz.setPointerCapture(e.pointerId);
      function move(ev) {
        const h = clamp(startH + (startY - ev.clientY), 90, window.innerHeight * 0.75);
        panel.style.flex = '0 0 ' + h + 'px';
      }
      function up() { rz.removeEventListener('pointermove', move); rz.removeEventListener('pointerup', up); }
      rz.addEventListener('pointermove', move);
      rz.addEventListener('pointerup', up);
    });
  })();

  /* python status chip */
  if (kind === 'python') {
    const chip = $('#rt-status'), label = $('#rt-label');
    teardownFns.push(PyRunner.onStatus(function (s) {
      if (!document.contains(chip)) return;
      chip.className = 'rt-status ' + (s === 'ready' || s === 'running' ? 'ready' : s === 'loading' ? 'loading' : s === 'error' ? 'error' : '');
      label.textContent = s === 'loading' ? 'loading python…' : s === 'error' ? 'python failed' : s === 'running' ? 'running' : 'python';
    }));
  }

  /* hints */
  const hb = $('#hint-btn');
  if (hb) {
    const body = $('#hint-body'), k = $('#hint-k');
    const paintHints = function () {
      k.textContent = hintsShown + ' / ' + l.hints.length + ' shown';
      body.hidden = hintsShown === 0;
      body.innerHTML = l.hints.slice(0, hintsShown).map(function (h) { return '<div class="hint-item">' + mdInline(h) + '</div>'; }).join('') +
        (hintsShown < l.hints.length ? '<div style="margin-top:8px"><button class="btn sm" id="hint-more">Show next hint</button></div>' : '');
      const more = $('#hint-more');
      if (more) more.addEventListener('click', function () { hintsShown++; persist(); paintHints(); });
    };
    hb.addEventListener('click', function () {
      if (hintsShown === 0) hintsShown = 1;
      persist();
      body.hidden = false;
      paintHints();
    });
    if (hintsShown > 0) paintHints();
  }

  /* solution */
  const sb = $('#sol-btn'), sbody = $('#sol-body');
  let solOpen = false, solConfirm = false;
  if (sb) sb.addEventListener('click', function () {
    if (!solOpen && !solConfirm) {
      solConfirm = true;
      sb.querySelector('.k').textContent = 'sure? tap again';
      setTimeout(function () { if (!solOpen) { solConfirm = false; sb.querySelector('.k').textContent = 'reveal when stuck'; } }, 2600);
      return;
    }
    solOpen = !solOpen;
    sbody.hidden = !solOpen;
    sb.querySelector('.k').textContent = solOpen ? 'hide' : 'reveal when stuck';
    if (solOpen && !sbody.dataset.built) {
      sbody.dataset.built = '1';
      sbody.innerHTML = l.solution.map(function (f, i) {
        return '<div class="fname">' + esc(f.name) + '</div>' +
          '<pre class="md-code"><code>' + Highlight.render(fileText(f), langOfFile(f.name)) + '</code></pre>' +
          '<div class="sol-actions"><button class="btn sm" data-load="' + i + '">Load into editor</button></div>';
      }).join('');
      $all('[data-load]', sbody).forEach(function (b) {
        let armed = false;
        b.addEventListener('click', function () {
          const f = l.solution[+b.dataset.load];
          if (!armed) { armed = true; b.textContent = 'Overwrite ' + f.name + '?'; setTimeout(function () { armed = false; b.textContent = 'Load into editor'; }, 2600); return; }
          const target = files.find(function (x) { return x.name === f.name; });
          if (target && !target.ro) {
            target.content = fileText(f);
            if (files[active].name === f.name) ed.setValue(target.content);
            persist();
            toast('Solution loaded into ' + f.name);
          }
          armed = false; b.textContent = 'Load into editor';
        });
      });
    }
  });

  /* reset */
  const rb = $('#reset-btn');
  let resetArmed = false;
  rb.addEventListener('click', function () {
    if (!resetArmed) {
      resetArmed = true; rb.textContent = 'Reset — sure?';
      setTimeout(function () { resetArmed = false; rb.textContent = 'Reset'; }, 2600);
      return;
    }
    resetArmed = false; rb.textContent = 'Reset';
    const fresh = starterFiles(l);
    for (let i = 0; i < files.length; i++) files[i].content = fresh[i].content;
    delete P.code[l.id];
    hintsShown = 0;
    saveSoon();
    setActive(active);
    clearConsole();
    logLine('sys', 'Reset to the starter code.');
    renderChecks({ phase: 'idle' });
  });

  /* run */
  const runBtn = $('#run-btn');
  async function doRun() {
    if (running) return;
    running = true;
    runBtn.disabled = true;
    runBtn.textContent = '… Running';
    persist();
    clearConsole();
    renderChecks({ phase: 'running', results: null });
    if (isMobile()) setMtab('output');
    setPtab(hasPreview ? 'preview' : 'console');
    if (!hasPreview) setPtab('console');
    const runFiles = files.map(function (f) { return { name: f.name, content: f.content }; });
    function finish(results) {
      running = false;
      runBtn.disabled = false;
      runBtn.textContent = '▶ Run';
      if (!results) { renderChecks({ phase: 'idle' }); return; }
      renderChecks({ phase: 'done', results: results });
      const passed = results.filter(function (r) { return r.pass; }).length;
      if (passed === l.tests.length && l.tests.length) {
        const isNew = completeLesson(l.id);
        renderRail();
        const nx = $('#nav-next', main);
        if (nx) nx.classList.add('primary');
        toast(isNew ? '✓ All checks pass — +' + (XP[l.type]) + ' XP' : '✓ All checks pass', true);
        if (!isMobile()) setPtab('checks');
      } else if (l.tests.length) {
        toast(passed + ' / ' + l.tests.length + ' checks pass');
        setPtab('checks');
      }
    }
    try {
      if (kind === 'python') {
        if (PyRunner.getStatus() !== 'ready') logLine('sys', 'Fetching the Python runtime (~10 MB) — only the first run waits for this…');
        const r = await PyRunner.run({ files: runFiles, main: l.main, tests: l.tests, onConsole: logLine });
        finish(r.results);
      } else {
        WebRunner.run({
          kind: kind, files: runFiles, main: l.main, tests: l.tests,
          mount: $('#preview-wrap'),
          onConsole: logLine,
          onTests: function (results) { finish(results); },
          onDone: function (ok) { if (ok === null) finish(null); },
        });
      }
    } catch (e) {
      logLine('error', String((e && e.message) || e));
      finish(null);
    }
  }
  runBtn.addEventListener('click', doRun);

  teardown = function () { persistSoon(); persist(); };
}

/* ---------- playground ---------- */
/* the modes whose body is a code editor; anything else renders its own view */
const PLAY_CODE_MODES = { python: 1, js: 1, web: 1 };
const PLAY_DEFAULTS = {
  python: { main: 'main.py', files: { 'main.py': '# Scratchpad — anything goes.\nfor i in range(1, 6):\n    print("*" * i)\n' } },
  js: { main: 'script.js', files: { 'script.js': '// Scratchpad — console.log away.\nconst names = ["Ada", "Linus", "Grace"];\nfor (const n of names) console.log("Hei, " + n + "!");\n' } },
  web: { main: 'index.html', files: {
    'index.html': '<!doctype html>\n<html>\n<head>\n  <meta charset="utf-8">\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n  <h1>Playground</h1>\n  <p>Edit index.html, style.css and app.js — then Run.</p>\n  <button id="go">Click me</button>\n  <scr' + 'ipt src="app.js"><\\/scr' + 'ipt>\n</body>\n</html>\n',
    'style.css': 'body { font-family: system-ui, sans-serif; padding: 24px; background: #f5f6f8; }\nh1 { color: #f26a1b; }\nbutton { padding: 8px 14px; border-radius: 8px; border: 1px solid #ccc; background: #fff; cursor: pointer; }\n',
    'app.js': 'let clicks = 0;\ndocument.querySelector("#go").addEventListener("click", () => {\n  clicks += 1;\n  document.querySelector("#go").textContent = "Clicked " + clicks + "x";\n});\n',
  } },
  /* the schematic lives as JSON in the same per-mode file slot the code modes use,
     so it is saved, synced and reset by exactly the same machinery */
  circuit: { main: 'circuit.json', files: { 'circuit.json': '' } },
};
function playState() {
  if (!P.playground) P.playground = { mode: 'python', files: {} };
  const st = P.playground;
  /* every mode PLAY_DEFAULTS declares, not a list that has to be remembered twice:
     a mode missing from here gets no file slot, and its edits fail silently */
  for (const mode of Object.keys(PLAY_DEFAULTS)) {
    if (!st.files[mode]) st.files[mode] = Object.assign({}, PLAY_DEFAULTS[mode].files);
  }
  return st;
}
/* ---------- inline example runner ----------
   Examples in the reading material run where they sit. Nothing about running one
   navigates, re-renders the view, or disturbs the tree rail, so the reader never
   loses their place in the material. */
const CB_RUNS = {};
/* WebRunner's watchdog line is worded for lab runs; an example has no tests. */
const CB_WATCHDOG = 'Tests did not finish within 10s';
const CB_TIMEOUT_MSG = 'This example did not finish within 10s — an infinite loop, or a very long timer?';

function copySnippet(code, btn) {
  /* the pristine label, cached: a second click during the flash would otherwise
     capture "Copied" and restore that forever */
  if (!btn.dataset.label) btn.dataset.label = btn.textContent;
  const was = btn.dataset.label;
  const flash = function (msg) {
    btn.textContent = msg;
    clearTimeout(+btn.dataset.flashT || 0);
    btn.dataset.flashT = setTimeout(function () { btn.textContent = was; }, 1200);
  };
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(code).then(function () { flash('Copied'); }, function () { flash('Press Ctrl+C'); });
    return;
  }
  try {
    const ta = document.createElement('textarea');
    ta.value = code;
    ta.setAttribute('readonly', '');
    ta.style.cssText = 'position:fixed;top:-1000px;opacity:0';
    document.body.appendChild(ta);
    ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    flash(ok ? 'Copied' : 'Press Ctrl+C');
  } catch (e) { flash('Press Ctrl+C'); }
}

function cbDrawer(box) {
  let out = box.querySelector('.cb-out');
  if (out) return out;
  out = el(
    '<div class="cb-out">' +
      '<div class="cb-out-head"><b>Output</b><span class="st"></span><span class="sp"></span>' +
        '<button class="cb-btn cb-hide" type="button">Hide</button></div>' +
      '<div class="cb-console"></div>' +
      '<div class="cb-preview" hidden></div>' +
      '<div class="cb-frame" style="width:0;height:0;overflow:hidden"></div>' +
    '</div>');
  out.querySelector('.cb-hide').addEventListener('click', function () { out.remove(); });
  box.appendChild(out);
  return out;
}
function cbStatus(out, text, cls) {
  const st = out.querySelector('.st');
  st.textContent = text;
  st.className = 'st' + (cls ? ' ' + cls : '');
}
function cbLine(out, level, text) {
  const c = out.querySelector('.cb-console');
  if (!c || c.children.length > 300) return;
  const ln = document.createElement('span');
  ln.className = 'ln ' + level;
  ln.textContent = text;
  c.appendChild(ln);
  c.scrollTop = c.scrollHeight;
}

function runSnippet(s, box, btn) {
  const id = box.dataset.cbx;
  if (CB_RUNS[id]) return;
  CB_RUNS[id] = true;
  btn.disabled = true;

  const out = cbDrawer(box);
  const con = out.querySelector('.cb-console');
  const prev = out.querySelector('.cb-preview');
  con.innerHTML = '';
  const finish = function (label, cls) {
    CB_RUNS[id] = false;
    btn.disabled = false;
    cbStatus(out, label, cls);
  };

  if (s.lang === 'html') {
    con.hidden = true;
    prev.hidden = false;
    cbStatus(out, 'rendering…', '');
    let doc = s.code;
    if (!/<html|<!doctype/i.test(doc)) {
      doc = '<!doctype html>\n<html>\n<head><meta charset="utf-8"></head>\n<body>\n' + doc + '\n</body>\n</html>';
    }
    WebRunner.run({
      mount: prev, kind: 'web', main: 'index.html', tests: [],
      files: [{ name: 'index.html', content: doc }],
      onConsole: function (level, text) {
        /* the frame's own console has no panel here — only errors are worth surfacing */
        if (level !== 'error' || String(text).indexOf(CB_WATCHDOG) === 0) return;
        con.hidden = false;
        cbLine(out, level, text);
      },
      onTests: function () {},
      onDone: function (ok) {
        if (!ok) { con.hidden = false; cbLine(out, 'error', CB_TIMEOUT_MSG); }
        finish(ok ? 'rendered' : 'timed out', ok ? 'ok' : 'bad');
      },
    });
    return;
  }

  con.hidden = false;
  prev.hidden = true;

  if (s.lang === 'js') {
    cbStatus(out, 'running…', '');
    let bad = false;
    WebRunner.run({
      mount: out.querySelector('.cb-frame'), kind: 'js', main: 'script.js', tests: [],
      files: [{ name: 'script.js', content: s.code }],
      onConsole: function (level, text) {
        if (String(text).indexOf(CB_WATCHDOG) === 0) return;
        if (level === 'error') bad = true;
        cbLine(out, level, text);
      },
      onTests: function () {},
      onDone: function (ok) {
        if (!ok) {
          cbLine(out, 'error', CB_TIMEOUT_MSG);
          finish('timed out', 'bad');
          return;
        }
        if (!con.children.length) cbLine(out, 'sys', 'ran — this example prints nothing');
        finish(bad ? 'error' : 'done', bad ? 'bad' : 'ok');
      },
    });
    return;
  }

  /* python */
  const st = PyRunner.getStatus();
  cbStatus(out, st === 'ready' ? 'running…' : (st === 'running' ? 'queued…' : 'starting Python…'), '');
  if (st !== 'ready' && st !== 'running') {
    cbLine(out, 'sys', 'Starting the Python runtime — the first run downloads it (~10 MB).');
  }
  PyRunner.run({
    files: [{ name: 'main.py', content: s.code }], main: 'main.py', tests: [],
    onConsole: function (level, text) { cbLine(out, level, text); },
  }).then(function (r) {
    if (!con.querySelector('.ln:not(.sys)')) cbLine(out, 'sys', 'ran — this example prints nothing');
    finish(r.ok ? 'done' : 'error', r.ok ? 'ok' : 'bad');
  }, function (err) {
    cbLine(out, 'error', String((err && err.message) || err));
    finish('error', 'bad');
  });
}

function openInPlayground(code, lang) {
  const st = playState();
  const mode = lang === 'python' ? 'python' : (lang === 'html' ? 'web' : 'js');
  st.mode = mode;
  if (mode === 'python') st.files.python['main.py'] = code + '\n';
  else if (mode === 'js') st.files.js['script.js'] = code + '\n';
  else {
    let doc = code;
    if (!/<html|<!doctype/i.test(doc)) {
      doc = '<!doctype html>\n<html>\n<head><meta charset="utf-8"></head>\n<body>\n' + doc + '\n</body>\n</html>';
    }
    st.files.web = { 'index.html': doc + '\n' };
  }
  saveSoon();
  /* carry the origin so the Playground can offer a one-click way back */
  go({ view: 'play', from: (route && route.view !== 'play') ? route : null });
  toast('Opened in the Playground — press Run');
}

/* ---------- playground: circuits ----------
   A schematic instead of a text editor. It shares the playground's per-mode file
   slot, so saving, syncing and Reset all work without knowing what is inside. */
function renderCircuitPlayground(main, st) {
  let saved = null;
  const slot = st.files.circuit || (st.files.circuit = {});
  try { saved = JSON.parse(slot['circuit.json'] || 'null'); } catch (e) { saved = null; }
  const model = (saved && saved.parts && saved.parts.length) ? saved : CIRCUIT_EXAMPLE;

  main.innerHTML =
    '<div class="play">' +
      '<div class="play-head"><h1>Playground</h1>' +
        '<div class="seg" id="seg">' +
          '<button data-m="python">Python</button><button data-m="js">JavaScript</button>' +
          '<button data-m="web">Web page</button><button data-m="circuit" class="active">Circuit</button>' +
        '</div>' +
        '<span class="hint">Draw a circuit and solve it \u2014 saved automatically.</span>' +
        (route.from ? '<span class="sp"></span><button class="btn dark sm" id="play-back">\u2190 Back to ' +
          esc(screenMeta(route.from).title) + '</button>' : '') +
      '</div>' +
      '<div id="ckt-mount"></div>' +
      '<p class="ckt-note">Linear components only: resistors, capacitors, inductors and ideal sources. ' +
      'There is no Newton loop, so no diodes or transistors \u2014 the solver would have to lie about them.</p>' +
    '</div>';

  $all('#seg button', main).forEach(function (b) {
    b.addEventListener('click', function () {
      if (b.dataset.m === 'circuit') return;
      st.mode = b.dataset.m;
      saveSoon();
      go({ view: 'play' });
    });
  });
  const back = $('#play-back', main);
  if (back) back.addEventListener('click', function () { go(route.from); });

  const handle = createCircuit($('#ckt-mount', main), {
    model: model,
    onChange: function (m) {
      slot['circuit.json'] = JSON.stringify(m);
      saveSoon();
    },
  });
  teardown = function () { handle.dispose(); };
}

function renderPlayground(main) {
  const st = playState();
  let mode = st.mode || 'python';
  if (mode === 'circuit') { renderCircuitPlayground(main, st); return; }
  let names = Object.keys(st.files[mode]);
  let active = 0;
  let running = false;

  main.innerHTML =
  '<div class="play">' +
    '<div class="play-head"><h1>Playground</h1>' +
      '<div class="seg" id="seg">' +
        '<button data-m="python">Python</button><button data-m="js">JavaScript</button>' +
        '<button data-m="web">Web page</button><button data-m="circuit">Circuit</button>' +
      '</div>' +
      '<span class="hint">A scratchpad — saved automatically, no checks.</span>' +
      (route.from ? '<span class="sp"></span><button class="btn dark sm" id="play-back">← Back to ' +
        esc(screenMeta(route.from).title) + '</button>' : '') +
    '</div>' +
    '<div class="workbench">' +
      '<div class="wb-bar">' +
        '<div class="ftabs" id="p-ftabs"></div>' +
        '<div class="wb-actions">' +
          '<span class="newfile" id="newfile" hidden><input id="nf-input" placeholder="new-file.py" aria-label="New file name"><button class="btn dark sm" id="nf-add">Add</button></span>' +
          '<button class="btn dark sm" id="p-newfile-btn">+ File</button>' +
          '<span class="rt-status" id="p-rt" hidden><i></i><span id="p-rt-label">python</span></span>' +
          '<button class="btn dark sm" id="p-reset">Reset</button>' +
          '<button class="btn run" id="p-run">▶ Run</button>' +
        '</div>' +
      '</div>' +
      '<div class="wb-editor"><div id="p-ed"></div></div>' +
      '<div class="wb-resize" id="p-resize"></div>' +
      '<div class="wb-panel" id="p-panel">' +
        '<div class="ptabs">' +
          '<button class="ptab active" data-pt="console">Console</button>' +
          '<button class="ptab" data-pt="preview" id="p-prev-tab" hidden>Preview</button>' +
          '<span class="spacer"></span><span class="note">Ctrl+Enter runs</span>' +
        '</div>' +
        '<div class="pbody">' +
          '<div class="console" id="p-console"><span class="empty">Press Run — output appears here.</span></div>' +
          '<div class="preview-wrap" id="p-preview" hidden></div>' +
        '</div>' +
      '</div>' +
    '</div>' +
  '</div>';

  const backBtn = $('#play-back', main);
  if (backBtn) backBtn.addEventListener('click', function () { go(route.from); });

  const ed = createEditor($('#p-ed'), {
    lang: 'python',
    onRun: doRun,
    onSave: function () { saveNow(); toast('Saved'); },
    onChange: function (v) { st.files[mode][names[active]] = v; saveSoon(); },
    acExtra: function () {
      return names.map(function (n, i) { return i === active ? '' : st.files[mode][n]; }).join('\n');
    },
  });

  let lineCount = 0;
  function clearConsole() { $('#p-console').innerHTML = ''; lineCount = 0; }
  function logLine(level, text) {
    if (lineCount > 600) return;
    lineCount++;
    const c = $('#p-console');
    if (!c) return;
    const ln = document.createElement('span');
    ln.className = 'ln ' + level;
    ln.textContent = text;
    c.appendChild(ln);
    c.scrollTop = c.scrollHeight;
  }
  function setPtab(which) {
    $all('.ptab', main).forEach(function (b) { b.classList.toggle('active', b.dataset.pt === which); });
    $('#p-console').hidden = which !== 'console';
    $('#p-preview').hidden = which !== 'preview';
  }
  $all('.ptab', main).forEach(function (b) { b.addEventListener('click', function () { setPtab(b.dataset.pt); }); });

  function renderFtabs() {
    $('#p-ftabs').innerHTML = names.map(function (n, i) {
      return '<button class="ftab' + (i === active ? ' active' : '') + '" data-fi="' + i + '">' + esc(n) + '</button>';
    }).join('');
    $all('#p-ftabs .ftab', main).forEach(function (b) {
      b.addEventListener('click', function () { setActive(+b.dataset.fi); });
    });
  }
  function setActive(i) {
    active = i;
    ed.setLang(langOfFile(names[i]));
    ed.setValue(st.files[mode][names[i]]);
    renderFtabs();
  }
  function setMode(m) {
    /* Not every mode is a text editor. Switching in place worked while all three
       were, but the circuit mode needs a different view entirely — without this it
       loaded circuit.json into the code editor and the schematic "disappeared". */
    if (!PLAY_CODE_MODES[m]) { st.mode = m; saveSoon(); go({ view: 'play' }); return; }
    mode = m;
    st.mode = m;
    names = Object.keys(st.files[m]);
    active = 0;
    $all('#seg button', main).forEach(function (b) { b.classList.toggle('active', b.dataset.m === m); });
    $('#p-prev-tab').hidden = m !== 'web';
    $('#p-rt').hidden = m !== 'python';
    $('#p-newfile-btn').hidden = m === 'js';
    setPtab('console');
    setActive(0);
    saveSoon();
  }
  $all('#seg button', main).forEach(function (b) { b.addEventListener('click', function () { setMode(b.dataset.m); }); });

  $('#p-newfile-btn').addEventListener('click', function () {
    const nf = $('#newfile');
    nf.hidden = !nf.hidden;
    if (!nf.hidden) $('#nf-input').focus();
  });
  function addFile() {
    const name = $('#nf-input').value.trim();
    const okExt = mode === 'python' ? /^[\w.-]+\.py$/ : /^[\w.-]+\.(css|js|html)$/;
    if (!okExt.test(name)) { toast(mode === 'python' ? 'Name it like helpers.py' : 'Use .css, .js or .html'); return; }
    if (st.files[mode][name] !== undefined) { toast('That file already exists'); return; }
    st.files[mode][name] = mode === 'python' ? '# ' + name + '\n' : '';
    names = Object.keys(st.files[mode]);
    $('#nf-input').value = '';
    $('#newfile').hidden = true;
    setActive(names.indexOf(name));
    saveSoon();
  }
  $('#nf-add').addEventListener('click', addFile);
  $('#nf-input').addEventListener('keydown', function (e) { if (e.key === 'Enter') addFile(); });

  $('#p-reset').addEventListener('click', function () {
    st.files[mode] = Object.assign({}, PLAY_DEFAULTS[mode].files);
    names = Object.keys(st.files[mode]);
    setActive(0);
    clearConsole();
    saveSoon();
  });

  (function () {
    const rz = $('#p-resize'), panel = $('#p-panel');
    rz.addEventListener('pointerdown', function (e) {
      const startY = e.clientY, startH = panel.getBoundingClientRect().height;
      rz.setPointerCapture(e.pointerId);
      function move(ev) { panel.style.flex = '0 0 ' + clamp(startH + (startY - ev.clientY), 90, window.innerHeight * 0.75) + 'px'; }
      function up() { rz.removeEventListener('pointermove', move); rz.removeEventListener('pointerup', up); }
      rz.addEventListener('pointermove', move);
      rz.addEventListener('pointerup', up);
    });
  })();

  PyRunner.onStatus(function (s) {
    const chip = $('#p-rt'), label = $('#p-rt-label');
    if (!chip || !document.contains(chip)) return;
    chip.className = 'rt-status ' + (s === 'ready' || s === 'running' ? 'ready' : s === 'loading' ? 'loading' : s === 'error' ? 'error' : '');
    label.textContent = s === 'loading' ? 'loading python…' : s === 'error' ? 'python failed' : 'python';
  });

  const runBtn = $('#p-run');
  async function doRun() {
    if (running) return;
    running = true;
    runBtn.disabled = true;
    runBtn.textContent = '… Running';
    clearConsole();
    const runFiles = names.map(function (n) { return { name: n, content: st.files[mode][n] }; });
    function done() { running = false; runBtn.disabled = false; runBtn.textContent = '▶ Run'; }
    try {
      if (mode === 'python') {
        setPtab('console');
        if (PyRunner.getStatus() !== 'ready') logLine('sys', 'Fetching the Python runtime (~10 MB) — only the first run waits for this…');
        await PyRunner.run({ files: runFiles, main: 'main.py', tests: [], onConsole: logLine });
        done();
      } else {
        if (mode === 'web') setPtab('preview'); else setPtab('console');
        WebRunner.run({
          kind: mode === 'web' ? 'web' : 'js',
          files: runFiles,
          main: PLAY_DEFAULTS[mode].main,
          tests: [],
          mount: $('#p-preview'),
          onConsole: logLine,
          onTests: function () {},
          onDone: function () { done(); },
        });
        setTimeout(done, 800);
      }
    } catch (e) {
      logLine('error', String((e && e.message) || e));
      done();
    }
  }
  runBtn.addEventListener('click', doRun);

  setMode(mode);
}

/* ---------- boot ---------- */
async function boot() {
  const bundleEl = document.getElementById('bundle');
  BUNDLE = parseBundle(bundleEl ? bundleEl.textContent : '');
  const saved = await Store.load();
  if (saved && typeof saved === 'object') {
    P = Object.assign({ completed: {}, quiz: {}, code: {}, derive: {}, build: {}, blanks: {}, numeric: {}, match: {}, tune: {}, xp: 0, last: null, playground: null,
                       activity: {}, name: '', railHidden: false }, saved);
    if (!P.activity || typeof P.activity !== 'object') P.activity = {};
  }
  renderShell();
  applyTheme();

  /* The catalog has to be indexed before anything below this line runs, and the
     ordering is load-bearing rather than tidy:

       - Sync.push -> adopt -> recomputeXp values every completed unit by its type,
         which it can only do once LESSON_INDEX knows the types;
       - the P.last restore reads info.track.program to open the right band;
       - the study plan picks the Resume target and lists the year's subjects.

     None of those throw when the catalog is absent. They just quietly say something
     untrue, which is the worst of the available failures. */
  renderDegradeBanner();
  if (DEGREE_CHUNK_LIST.length && !DEGREE.courses.length) {
    /* Something on screen while the payloads are in flight. renderShell has already
       painted the chrome and the foundation rail; this fills the one panel that has
       nothing to show yet. */
    const m = $('#main');
    if (m) {
      m.innerHTML = '<div class="boot-wait"><div>Loading the course catalog\u2026</div>' +
        '<div class="bw-bar"><i></i></div></div>';
    }
    const omni = $('#omni');
    if (omni) { omni.disabled = true; omni.placeholder = 'Loading\u2026'; }
  }
  await loadDegreeChunks();
  const omni = $('#omni');
  if (omni) { omni.disabled = false; omni.placeholder = 'Search lessons'; }
  renderDegradeBanner();
  renderRail();

  /* pull whatever the account already has before the first screen paints, so a
     second machine opens where the first one left off rather than at zero */
  if (Sync.signedIn()) {
    try {
      /* short fuse on the boot pull: a slow or absent server delays the first paint */
      const r = await Sync.push(P, 5000);
      adopt(r.progress);
      syncState.at = Date.now();
      syncState.rev = r.rev || 0;
      Store.save(P);
    } catch (e) {
      syncState.error = String((e && e.message) || e);
    }
  }
  openTracks.python = true;
  if (P.last && LESSON_INDEX[P.last]) {
    const info = LESSON_INDEX[P.last];
    if (info.track.kind === 'course') openBands[bandKey(info.track.program, info.track.band)] = true;
    else openTracks[info.track.id] = true;
  }
  go(frontRoute());
  setTimeout(checkForNewBuild, 2000);
}
/* boot() used to be unrejectable by construction — its only awaits were Store.load,
   which swallows everything, and a Sync call already inside a try. Fetching the
   catalog breaks that, and an unhandled rejection here is a permanently blank page
   with nothing on screen to explain it. */
function bootFailed(e) {
  try { console.error('[codewright] boot failed', e); } catch (_) {}
  const app = document.getElementById('app');
  if (!app) return;
  app.innerHTML = '<div style="max-width:34rem;margin:18vh auto;padding:0 24px;' +
    'font:15px/1.6 system-ui,sans-serif;color:#c9d1d9">' +
    '<h1 style="font-size:20px;margin:0 0 10px">Codex Learn could not start</h1>' +
    '<p style="margin:0 0 14px;color:#8b949e">' +
    String((e && e.message) || e).replace(/[<>&]/g, '') + '</p>' +
    '<button onclick="location.reload()" style="padding:8px 16px;border-radius:8px;' +
    'border:1px solid #30363d;background:#161b22;color:inherit;cursor:pointer">Reload</button>' +
    '</div>';
}
if (typeof window !== 'undefined' && typeof document !== 'undefined' && !(typeof globalThis !== 'undefined' && globalThis.__CW_NO_BOOT)) {
  const start = function () { Promise.resolve().then(boot).catch(bootFailed); };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { parseBundle: parseBundle, renderMd: renderMd, Highlight: Highlight, dedent: dedent, mdInline: mdInline, TRACKS: TRACKS, LESSON_INDEX: LESSON_INDEX, DEGREE: DEGREE };
}
