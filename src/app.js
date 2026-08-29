/* ============ Codewright app: state, routing, views ============ */

/* ---------- app state ---------- */
const XP = { read: 10, quiz: 25, code: 40, project: 120 };
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

/* ---------- degree catalog ---------- */
const DEGREE = (typeof DEGREE_DATA !== 'undefined' && DEGREE_DATA) ? DEGREE_DATA : { programs: [], courses: [] };
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

(function buildDegreeIndex() {
  for (const c of DEGREE.courses) {
    COURSE_OF[c.id] = c;
    /* a course behaves like a mini-track so lesson chrome, nav and XP all work */
    c.kind = 'course';
    c.name = c.id + ' · ' + c.title;
    c.tint = 'var(--lv-soft)';
    const flat = [];

    c.modules.forEach(function (m, mi) {
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
})();

function coursesInBand(programId, n) {
  return DEGREE.courses.filter(function (c) { return c.program === programId && c.band === n; });
}
function coursesInProgram(programId) {
  return DEGREE.courses.filter(function (c) { return c.program === programId; });
}
function courseUnits(c) { return TRACK_LESSONS[c.id] || []; }
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
    return { id: id, title: pc ? pc.title : id, met: pc ? courseComplete(pc) : true, known: !!pc };
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
    labs += c.modules.filter(function (m) { return m.lab; }).length;
  }
  return { units: units, done: done, credits: credits, earned: earned, labs: labs,
           courses: list.length,
           pct: units ? Math.round(done / units * 100) : 0 };
}

let P = { completed: {}, quiz: {}, code: {}, xp: 0, last: null, playground: null, activity: {}, name: '', railHidden: false };
let route = { view: 'home' };
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
function lastWeek() {
  const names = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
  const out = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    out.push({ day: names[d.getDay()], n: activityOn(i), today: i === 0 });
  }
  return out;
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
  const label = { read: 'Read', quiz: 'Quiz', code: 'Code', project: 'Project' }[type] || type;
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
  if (t === 'dark') document.documentElement.setAttribute('data-theme', 'dark');
  else document.documentElement.removeAttribute('data-theme');
  const b = $('#theme-btn');
  if (b) {
    b.textContent = t === 'dark' ? '☀' : '☾';
    b.setAttribute('aria-label', t === 'dark' ? 'Switch to light mode' : 'Switch to dark mode');
  }
}

/* ---------- shell ---------- */
const NAV = [
  { id: 'home', label: 'Dashboard', view: 'home',
    d: 'M3 10.5 12 3l9 7.5M5.5 9.2V20h13V9.2' },
  { id: 'degree', label: 'Programmes', view: 'programs',
    d: 'M12 3 2 8l10 5 10-5-10-5ZM2 13.5l10 5 10-5M2 18l10 5 10-5' },
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
      '<div class="body" id="body">' +
        '<aside class="rail" id="rail" aria-label="Curriculum"></aside>' +
        '<main class="main" id="main"></main>' +
      '</div>' +
    '</div>' +
    '<div class="scrim" id="scrim"></div>';

  $('#brand').addEventListener('click', function () { go({ view: 'home' }); });
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
  const off = route.view === 'play' || railCrowdedOut();
  b.hidden = off;
  const shown = !P.railHidden;
  b.classList.toggle('on', shown);
  b.setAttribute('aria-pressed', shown ? 'true' : 'false');
  b.title = shown ? 'Hide the curriculum panel' : 'Show the curriculum panel';
}
function toggleRailPanel() {
  P.railHidden = !P.railHidden;
  $('#body').classList.toggle('no-rail', P.railHidden || route.view === 'play');
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
function renderRail() {
  const rail = $('#rail');
  let h = '<div class="rail-sec">Foundation tracks</div>';
  for (const t of TRACKS) {
    const done = trackDone(t.id), total = TRACK_LESSONS[t.id].length;
    const open = !!openTracks[t.id];
    h += '<div class="rail-track' + (open ? ' open' : '') + '" data-track="' + t.id + '">' +
      '<button data-toggle="' + t.id + '">' +
        '<span class="t-icon" style="--tt:' + t.tint + '">' + t.icon + '</span>' +
        '<span class="t-name">' + esc(t.name) + '</span>' +
        '<span class="t-pct">' + done + '/' + total + '</span>' +
      '</button>';
    if (open) {
      t.modules.forEach(function (m) {
        h += '<div class="rail-module"><h4>' + esc(m.title) + '</h4>';
        for (const l of m.lessons) {
          const active = route.view === 'lesson' && route.id === l.id;
          const mark = P.completed[l.id] ? 'done' : (active ? 'now' : '');
          h += '<button class="rail-lesson' + (active ? ' active' : '') + '" data-lesson="' + l.id + '">' +
            '<span class="num">' + l.num + '</span>' +
            '<span class="gmark ' + mark + '"></span>' +
            '<span class="ttl">' + esc(l.title) + '</span>' +
          '</button>';
        }
        h += '</div>';
      });
    }
    h += '</div>';
  }

  for (const pr of PROGRAMS) {
    if (!coursesInProgram(pr.id).length) continue;
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
          const active = route.view === 'course' && route.id === c.id;
          const units = courseUnits(c).length;
          const d = courseDone(c);
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
      go({ view: 'course', id: b.dataset.course });
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
    if (!info) { route = { view: 'home' }; }
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
  const hideRail = route.view === 'play' || !!P.railHidden;
  $('#body').classList.toggle('no-rail', hideRail);
  $('#body').classList.toggle('split', isSplit);
  syncRailToggle();

  const main = $('#main');
  main.classList.toggle('split', isSplit);
  main.scrollTop = 0;
  if (route.view === 'home') renderHome(main);
  else if (route.view === 'track') renderTrack(main, TRACK_OF[route.track]);
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
    else renderCode(main, l);
  }

  const host = scrollHost();
  if (host) host.scrollTop = SCROLL_MEM[routeKey(route)] || 0;
}

function navSectionFor(r) {
  if (r.view === 'track') return 'home';
  const info = LESSON_INDEX[r.id];
  return info && info.track.kind === 'course' ? 'degree' : 'home';
}

function screenMeta(r) {
  if (r.view === 'home') return { title: 'Dashboard', crumb: TOTAL.lessons + ' lessons · ' + DEGREE.courses.length + ' degree courses' };
  if (r.view === 'programs') {
    return { title: 'Programmes', crumb: PROGRAMS.length + ' majors · ' + DEGREE.courses.length + ' courses' };
  }
  if (r.view === 'degree') {
    const dpr = PROGRAM_OF[r.program] || PROGRAMS[0];
    const dn = dpr ? coursesInProgram(dpr.id).length : 0;
    return { title: dpr ? (dpr.short || dpr.name) : 'Programme',
             crumb: dpr ? ((dpr.bands || []).length + ' ' + (dpr.bandNoun || 'Year').toLowerCase() + 's · ' + dn + ' courses') : '' };
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
  if (!hits.length) { toast('Nothing matches “' + q + '”'); return; }
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
    return '<div class="crumb"><button data-go="home">Home</button><span>›</span>' +
      '<button data-go="degree">' + esc(lpr ? (lpr.short || lpr.name) : 'Programmes') + '</button><span>›</span>' +
      '<button data-go="course">' + esc(info.track.id) + '</button><span>›</span>' +
      '<span>' + esc(info.module.title) + '</span></div>';
  }
  return '<div class="crumb"><button data-go="home">Home</button><span>›</span>' +
    '<button data-go="track">' + esc(info.track.name) + '</button><span>›</span><span>' + esc(info.module.title) + '</span></div>';
}
function wireCrumb(root, l) {
  const info = LESSON_INDEX[l.id];
  $all('[data-go]', root).forEach(function (b) {
    b.addEventListener('click', function () {
      const k = b.dataset.go;
      if (k === 'home') go({ view: 'home' });
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

/* ---------- home / dashboard ---------- */
function renderHome(main) {
  const last = P.last && LESSON_INDEX[P.last] ? LESSON_INDEX[P.last] : null;
  const target = last ? last.lesson : TRACK_LESSONS.python[0];
  const tinfo = LESSON_INDEX[target.id];
  const dt = degreeTotals();
  const started = P.xp > 0;

  /* ---- totals across both curricula, all real ---- */
  let allUnits = TOTAL.lessons + dt.units;
  let doneUnits = 0;
  for (const id in P.completed) if (LESSON_INDEX[id]) doneUnits++;
  const week = lastWeek();
  const weekTotal = week.reduce(function (s, d) { return s + d.n; }, 0);
  const weekMax = Math.max(1, ...week.map(function (d) { return d.n; }));

  /* ---- the resume card's right pane: a real excerpt of what is next ---- */
  let snippet = '';
  if (target.files) {
    const files = currentFiles(target);
    const f = files.find(function (x) { return x.name === target.main; }) || files[0];
    const lines = f.content.split('\n').filter(function (l) { return l.trim().length; }).slice(0, 5);
    snippet = Highlight.render(lines.join('\n'), langOfFile(f.name));
  } else {
    const md = lessonMd(target) || BUNDLE[target.md] || '';
    const plain = md.replace(/[#*`>|]/g, '').split('\n').filter(function (l) { return l.trim().length > 30; }).slice(0, 4);
    snippet = plain.map(function (l) { return esc(l.trim().slice(0, 54)); }).join('\n');
  }

  /* ---- foundation track cards ---- */
  let cards = '';
  for (const t of TRACKS) {
    const flat = TRACK_LESSONS[t.id];
    const done = trackDone(t.id);
    const pct = flat.length ? done / flat.length * 100 : 0;
    const now = firstIncomplete(t.id);
    let strip = '';
    for (const l of flat) {
      const cls = (P.completed[l.id] ? 'done' : (now && now.id === l.id ? 'now' : '')) + (l.type === 'project' ? ' proj' : '');
      strip += '<i class="' + cls.trim() + '"></i>';
    }
    cards += '<button class="track-card" data-track="' + t.id + '">' +
      '<div class="head"><span class="t-icon">' + t.icon + '</span>' + ringHtml(pct) + '</div>' +
      '<h3>' + esc(t.name) + '</h3>' +
      '<p class="tag">' + done + ' / ' + flat.length + ' complete</p>' +
      '<div class="strip">' + strip + '</div>' +
    '</button>';
  }

  main.innerHTML = '<div class="page">' +
    '<div class="hero">' +
      '<div>' +
        '<div class="eyebrow">Level ' + level() + ' · ' + doneUnits + ' of ' + allUnits + ' units</div>' +
        '<h1>' + (started ? 'Welcome back.' : 'Learn by <em>building things</em> that run.') + '</h1>' +
        '<p class="lede">' + (started
          ? 'Every lab here is checked by tests that actually execute your code. Pick up where you left off, or open the degree catalog.'
          : esc(TRACKS.length + ' foundation tracks and ' + PROGRAMS.length + ' full degree ' +
          (PROGRAMS.length === 1 ? 'programme' : 'programmes') + ' \u2014 ') + (TOTAL.tasks + dt.labs) +
            ' coding labs, all auto-checked, no setup. Your progress saves itself.') + '</p>' +
      '</div>' +
      '<div class="acts">' +
        '<button class="btn" id="open-degree">Degree catalog</button>' +
        '<button class="btn primary" id="resume-btn">' + (started ? 'Resume' : 'Start learning') +
          '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M5 12h13m-5-6 6 6-6 6"/></svg></button>' +
      '</div>' +
    '</div>' +

    '<div class="resume" id="resume-card">' +
      '<div class="rl">' +
        '<div class="tagrow">' +
          '<span class="flag">' + (P.completed[target.id] ? 'Revisit' : (started ? 'In progress' : 'Start here')) + '</span>' +
          '<span class="where">' + esc(tinfo.track.kind === 'course' ? tinfo.track.id : tinfo.track.name) +
            ' · ' + esc(tinfo.module.title) + '</span>' +
        '</div>' +
        '<div><h3>' + esc(target.title) + '</h3>' +
        '<p>' + esc(tinfo.track.kind === 'course'
            ? 'A checked lab in the degree programme. ' + (target.tests ? target.tests.length + ' automated checks decide when it is done.' : '')
            : (TRACK_OF[tinfo.track.id] || {}).tagline || '') + '</p></div>' +
        '<div class="foot">' +
          '<div class="r"><span>' + typeChipText(target.type) + ' · ~' + target.min + ' min</span>' +
            '<em>' + (target.tests ? target.tests.length + ' checks' : 'reading') + '</em></div>' +
          '<div class="bar"><i style="width:' + Math.round(doneUnits / Math.max(1, allUnits) * 100) + '%"></i></div>' +
        '</div>' +
      '</div>' +
      '<div class="rr"><pre style="margin:0;font:inherit;white-space:pre-wrap">' + snippet + '</pre><span class="caret"></span></div>' +
    '</div>' +

    '<div class="stats">' +
      statCard('Experience', P.xp.toLocaleString('en-GB'), 'xp', started ? 'LVL ' + level() : '', week.map(function (d) { return d.n; })) +
      statCard('Streak', streakDays(), streakDays() === 1 ? 'day' : 'days', '', week.map(function (d) { return d.n > 0 ? 1 : 0; })) +
      statCard('Units done', doneUnits, 'of ' + allUnits, Math.round(doneUnits / Math.max(1, allUnits) * 100) + '%', null) +
      statCard('Checks passed', checksPassed().toLocaleString('en-GB'), '', '', null) +
    '</div>' +

    '<div style="display:grid;grid-template-columns:1.6fr 1fr;gap:22px;align-items:start" class="home-cols">' +
      '<div>' +
        '<div class="section-h"><h2>Foundation tracks</h2><span>' + TRACKS.length + ' tracks · start anywhere</span></div>' +
        '<div class="tracks-grid">' + cards + '</div>' +
      '</div>' +
      '<div>' +
        '<div class="section-h"><h2>This week</h2><span style="font-family:var(--mono);color:var(--lime)">' +
          weekTotal + ' unit' + (weekTotal === 1 ? '' : 's') + '</span></div>' +
        '<div class="panel">' +
          '<div class="weekchart">' +
            week.map(function (d) {
              const h = Math.max(3, Math.round(d.n / weekMax * 92));
              return '<div class="d' + (d.today ? ' today' : '') + '">' +
                '<i style="height:' + h + 'px"></i><span>' + d.day + '</span></div>';
            }).join('') +
          '</div>' +
          '<div class="hr"></div>' +
          '<button class="rowlink" id="go-degree-row">' +
            '<span class="ic"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"><path d="M13 2 4 14h6l-1 8 9-12h-6z"/></svg></span>' +
            '<span class="tx"><b>' + (PROGRAMS.length > 1 ? PROGRAMS.length + ' degree programmes' : (PROGRAMS[0] ? PROGRAMS[0].name : 'Degree catalog')) + '</b>' +
            '<span>' + dt.done + ' of ' + dt.units + ' units · ' + dt.pct + '% complete</span></span>' +
            '<svg class="go" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m9 5 7 7-7 7"/></svg>' +
          '</button>' +
        '</div>' +
      '</div>' +
    '</div>' +
  '</div>';

  $('#resume-btn').addEventListener('click', function () { go({ view: 'lesson', id: target.id }); });
  $('#resume-card').addEventListener('click', function () { go({ view: 'lesson', id: target.id }); });
  $('#open-degree').addEventListener('click', function () { go({ view: 'programs' }); });
  $('#go-degree-row').addEventListener('click', function () { go({ view: 'programs' }); });
  $all('.track-card', main).forEach(function (c) {
    c.addEventListener('click', function () { go({ view: 'track', track: c.dataset.track }); });
  });
}

function typeChipText(type) {
  return { read: 'Reading', quiz: 'Quiz', code: 'Lab', project: 'Capstone' }[type] || type;
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

  const mastery = TRACKS.map(function (t) {
    const flat = TRACK_LESSONS[t.id];
    const done = trackDone(t.id);
    return { name: t.name, done: done, total: flat.length, pct: flat.length ? done / flat.length * 100 : 0 };
  }).concat(PROGRAMS.flatMap(function (pr) { return pr.bands.map(function (y) {
    const list = coursesInBand(pr.id, y.n);
    const u = list.reduce(function (s, c) { return s + courseUnits(c).length; }, 0);
    const d = list.reduce(function (s, c) { return s + courseDone(c); }, 0);
    return { name: (pr.short || pr.name) + ' · ' + bandLabel(pr, y.n) + ' — ' + y.title,
             done: d, total: u, pct: u ? d / u * 100 : 0 };
  }); }).filter(function (m) { return m.total > 0; }));

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
          '<div class="section-h"><h2>Mastery</h2><span>tracks and degree years</span></div>' +
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
            return '<div style="display:flex;flex-direction:column;align-items:center;gap:8px;padding:16px 10px;border-radius:14px;' +
              'border:1px solid ' + (b.on ? 'var(--lime-30)' : 'var(--line)') + ';background:' + (b.on ? 'var(--lime-08)' : 'var(--surface-2)') +
              (b.on ? ';animation:popIn .4s var(--pop) both' : '') + '">' +
              '<span style="font-size:20px;' + (b.on ? '' : 'filter:grayscale(1);opacity:.4') + '">' + b.glyph + '</span>' +
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
  P.xp = xp;
}

function adopt(progress) {
  if (!progress || typeof progress !== 'object') return;
  adopting = true;
  try {
    P = Object.assign({ completed: {}, quiz: {}, code: {}, xp: 0, last: null, playground: null,
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
    P = Object.assign({ completed: {}, quiz: {}, code: {}, xp: 0, last: null, playground: null,
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
  P = { completed: {}, quiz: {}, code: {}, xp: 0, last: null, playground: null,
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
  return [
    { glyph: '◆', name: 'First unit', on: done >= 1 },
    { glyph: '✦', name: 'Ten units', on: done >= 10 },
    { glyph: '⬢', name: 'Fifty units', on: done >= 50 },
    { glyph: '★', name: 'First capstone', on: caps >= 1 },
    { glyph: '⚑', name: 'Course complete', on: full >= 1 },
    { glyph: '🔥', name: 'Seven-day streak', on: streakDays() >= 7 },
  ];
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
    '<div class="crumb"><button data-go="home">Home</button><span>›</span><span>' + esc(t.name) + '</span></div>' +
    '<div class="track-head">' +
      '<span class="t-icon" style="--tt:' + t.tint + '">' + t.icon + '</span>' +
      '<div><h1>' + esc(t.name) + '</h1><p>' + esc(t.tagline) + '</p>' +
      '<button class="btn primary" id="track-start">' + (next ? (trackDone(t.id) ? 'Continue: ' + esc(next.title) : 'Start the track') : 'Track complete — revisit') + ' →</button></div>' +
    '</div>' +
    '<div class="outcomes"><h3>You will be able to</h3><ul>' + t.outcomes.map(function (o) { return '<li>' + esc(o) + '</li>'; }).join('') + '</ul></div>' +
    modules +
  '</div>';
  $('[data-go="home"]', main).addEventListener('click', function () { go({ view: 'home' }); });
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
    const bandList = (pr.bands || []).map(function (b) {
      const n = coursesInBand(pr.id, b.n).length;
      return '<li><span class="pb-icon" style="--tt:' + b.tint + '">' + b.icon + '</span>' +
        '<span class="pb-t">' + esc(b.title) + '</span>' +
        '<span class="pb-n">' + (n ? n + ' course' + (n === 1 ? '' : 's') : 'soon') + '</span></li>';
    }).join('');
    return '<button class="prog-card' + (authored ? '' : ' empty') + '" data-program="' + esc(pr.id) + '">' +
      '<div class="pc-head">' +
        '<div><h2>' + emphasise(pr) + '</h2><p>' + esc(pr.subtitle) + '</p></div>' +
        ringHtml(t.pct) +
      '</div>' +
      '<div class="pc-stats">' +
        '<div class="stat"><b>' + authored + '</b><span>Courses</span></div>' +
        '<div class="stat"><b>' + t.units + '</b><span>Units</span></div>' +
        '<div class="stat"><b>' + t.labs + '</b><span>Labs</span></div>' +
        '<div class="stat"><b>' + planned + '</b><span>' + esc((pr.bandNoun || 'Year') + 's') + '</span></div>' +
      '</div>' +
      (spread ? '<div class="pc-levels">' + spread + '</div>' : '') +
      '<ul class="pc-bands">' + bandList + '</ul>' +
    '</button>';
  }).join('');

  main.innerHTML = '<div class="page wide">' +
    '<div class="crumb"><button data-go="home">Home</button><span>›</span><span>Programmes</span></div>' +
    '<div class="page-head">' +
      '<h1>Two majors</h1>' +
      '<p>Pick a programme to see its ' + esc(PROGRAMS.map(function (pr) { return (pr.bandNoun || 'Year').toLowerCase(); })
        .filter(function (v, i, a) { return a.indexOf(v) === i; }).join('s and ')) + 's. ' +
      'Progress is tracked separately for each.</p>' +
    '</div>' +
    '<div class="prog-grid">' + cards + '</div>' +
  '</div>';

  $('[data-go="home"]', main).addEventListener('click', function () { go({ view: 'home' }); });
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

function renderDegree(main, programId) {
  if (!DEGREE.courses.length) {
    main.innerHTML = '<div class="page"><h1>No catalog loaded</h1><p>The degree catalog was not bundled into this build.</p></div>';
    return;
  }
  const prog = PROGRAM_OF[programId] || PROGRAMS[0];
  if (!prog) { main.innerHTML = '<div class="page"><h1>No programme</h1></div>'; return; }
  const dt = degreeTotals(prog.id);
  const filt = degFilterFor(prog.id);

  function bands() {
    let out = '';
    const q = filt.q.trim().toLowerCase();
    let shown = 0;
    for (const y of prog.bands) {
      let list = coursesInBand(prog.id, y.n);
      if (q) {
        list = list.filter(function (c) {
          return (c.id + ' ' + c.title + ' ' + c.summary + ' ' + (c.stack || []).join(' ')).toLowerCase().indexOf(q) !== -1;
        });
      }
      if (filt.level !== 'all') list = list.filter(function (c) { return c.level === filt.level; });
      if (!list.length) continue;
      shown += list.length;
      const all = coursesInBand(prog.id, y.n);
      const doneC = all.filter(courseComplete).length;
      const pct = all.length ? Math.round(doneC / all.length * 100) : 0;
      out += '<section class="year-band">' +
        '<div class="year-head">' +
          '<span class="year-badge" style="--tt:' + y.tint + '">' + y.n + '</span>' +
          '<div><h2>' + esc(bandLabel(prog, y.n)) + ' — ' + esc(y.title) + '</h2><p>' + esc(y.theme) + '</p></div>' +
          '<div class="yr-prog"><b>' + doneC + '/' + all.length + '</b>courses<div class="bar"><i style="width:' + pct + '%"></i></div></div>' +
        '</div>' +
        '<div class="course-grid">' + list.map(courseCardHtml).join('') + '</div>' +
      '</section>';
    }
    return { html: out || '<p style="color:var(--ink-3)">No course matches that filter.</p>', shown: shown };
  }

  const b = bands();
  main.innerHTML = '<div class="page wide">' +
    '<div class="crumb"><button data-go="home">Home</button><span>›</span>' +
      '<button data-go="programs">Programmes</button><span>›</span><span>' + esc(prog.short || prog.name) + '</span></div>' +
    '<div class="deg-hero">' +
      '<div>' +
        '<h1>' + emphasise(prog) + '</h1>' +
        '<p>' + esc(prog.subtitle) + '</p>' +
        '<div class="deg-stats">' +
          '<div class="stat"><b>' + dt.courses + '</b><span>Courses</span></div>' +
          '<div class="stat"><b>' + dt.labs + '</b><span>Labs</span></div>' +
          '<div class="stat"><b>' + dt.units + '</b><span>Units</span></div>' +
          '<div class="stat"><b>' + dt.credits + '</b><span>Credits</span></div>' +
        '</div>' +
      '</div>' +
      '<div class="deg-progress">' +
        '<div class="ring" style="--pct:' + dt.pct + '"><div><b>' + dt.pct + '%</b><span>complete</span></div></div>' +
        '<div class="pl"><h3>' + dt.done + ' of ' + dt.units + ' units</h3>' +
        '<p>' + dt.earned + ' of ' + dt.credits + ' credits earned. A course counts as complete when every lab and its capstone pass.</p></div>' +
      '</div>' +
    '</div>' +
    '<div class="filters">' +
      '<input type="search" id="deg-q" placeholder="Search courses, topics, languages…" value="' + esc(filt.q) + '">' +
      '<div class="seg" id="deg-lv">' +
        ['all'].concat(LEVEL_ORDER).map(function (lv) {
          return '<button data-lv="' + lv + '"' + (filt.level === lv ? ' class="active"' : '') + '>' +
            (lv === 'all' ? 'All levels' : lv) + '</button>';
        }).join('') +
      '</div>' +
      '<span class="count">' + b.shown + ' shown</span>' +
    '</div>' +
    b.html +
  '</div>';

  $('[data-go="home"]', main).addEventListener('click', function () { go({ view: 'home' }); });
  $('[data-go="programs"]', main).addEventListener('click', function () { go({ view: 'programs' }); });
  $all('.course-card', main).forEach(function (c) {
    c.addEventListener('click', function () { go({ view: 'course', id: c.dataset.course }); });
  });
  const q = $('#deg-q', main);
  q.addEventListener('input', debounce(function () {
    filt.q = q.value;
    const pos = q.selectionStart;
    renderDegree(main, prog.id);
    const nq = $('#deg-q', main);
    if (nq) { nq.focus(); try { nq.setSelectionRange(pos, pos); } catch (e) {} }
  }, 180));
  $all('#deg-lv button', main).forEach(function (bn) {
    bn.addEventListener('click', function () { filt.level = bn.dataset.lv; renderDegree(main, prog.id); });
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

  let mods = '';
  c.modules.forEach(function (m, mi) {
    const lid = m.lessonId;
    const done = lid && P.completed[lid];
    mods += '<div class="mod" data-mod="' + mi + '">' +
      '<button class="mod-head">' +
        '<span class="gmark ' + (done ? 'done' : '') + '"></span>' +
        '<span class="mnum">M' + (mi + 1) + '</span>' +
        '<span class="mtitle">' + esc(m.title) +
          (m.summary ? '<span class="msum">' + esc(m.summary) + '</span>' : '') +
        '</span>' +
        '<span class="caret">▶</span>' +
      '</button>' +
      '<div class="mod-body" hidden>' +
        '<h4>Key concepts</h4>' +
        '<ul>' + m.concepts.map(function (x) { return '<li>' + mdInline(x) + '</li>'; }).join('') + '</ul>' +
        (m.lab ? (
          '<button class="lab-row" data-lesson="' + lid + '">' +
            '<span class="chip lab">Lab</span>' +
            '<span class="lab-t"><b>' + esc(m.lab.title) + '</b>' +
              '<span>~' + (m.lab.minutes || 30) + ' min · ' + (m.lab.tests || []).length + ' automated checks</span></span>' +
            '<span class="go">' + (done ? 'revisit ▸' : 'open ▸') + '</span>' +
          '</button>'
        ) : '') +
      '</div>' +
    '</div>';
  });

  const capDone = c.capstoneLessonId && P.completed[c.capstoneLessonId];
  main.innerHTML = '<div class="page wide lv-' + c.level + '">' +
    '<div class="crumb"><button data-go="home">Home</button><span>›</span>' +
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

    '<div class="section-h"><h2>Modules</h2><span>' + c.modules.length + ' modules · each ends in a checked lab</span></div>' +
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

  $('[data-go="home"]', main).addEventListener('click', function () { go({ view: 'home' }); });
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
function renderQuiz(main, l) {
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
      '<div class="opts">' + q.opts.map(function (o, oi) {
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
          if (i2 === q.a) b2.classList.add('correct');
          else if (i2 === oi) b2.classList.add('wrong');
        });
        const good = oi === q.a;
        $('.ex-slot', card).innerHTML = '<div class="explain ' + (good ? 'good' : 'bad') + '">' +
          (good ? '✓ Right. ' : '✗ Not quite — the answer is <b>' + 'ABCD'[q.a] + '</b>. ') + mdInline(q.why) + '</div>';
        if (answers.every(function (a) { return a !== null; })) finish();
      });
    });
  });
  function finish() {
    const correct = answers.filter(function (a, i) { return a === l.questions[i].a; }).length;
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
const PLAY_DEFAULTS = {
  python: { main: 'main.py', files: { 'main.py': '# Scratchpad — anything goes.\nfor i in range(1, 6):\n    print("*" * i)\n' } },
  js: { main: 'script.js', files: { 'script.js': '// Scratchpad — console.log away.\nconst names = ["Ada", "Linus", "Grace"];\nfor (const n of names) console.log("Hei, " + n + "!");\n' } },
  web: { main: 'index.html', files: {
    'index.html': '<!doctype html>\n<html>\n<head>\n  <meta charset="utf-8">\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n  <h1>Playground</h1>\n  <p>Edit index.html, style.css and app.js — then Run.</p>\n  <button id="go">Click me</button>\n  <scr' + 'ipt src="app.js"><\\/scr' + 'ipt>\n</body>\n</html>\n',
    'style.css': 'body { font-family: system-ui, sans-serif; padding: 24px; background: #f5f6f8; }\nh1 { color: #f26a1b; }\nbutton { padding: 8px 14px; border-radius: 8px; border: 1px solid #ccc; background: #fff; cursor: pointer; }\n',
    'app.js': 'let clicks = 0;\ndocument.querySelector("#go").addEventListener("click", () => {\n  clicks += 1;\n  document.querySelector("#go").textContent = "Clicked " + clicks + "x";\n});\n',
  } },
};
function playState() {
  if (!P.playground) P.playground = { mode: 'python', files: {} };
  const st = P.playground;
  for (const mode of ['python', 'js', 'web']) {
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

function renderPlayground(main) {
  const st = playState();
  let mode = st.mode || 'python';
  let names = Object.keys(st.files[mode]);
  let active = 0;
  let running = false;

  main.innerHTML =
  '<div class="play">' +
    '<div class="play-head"><h1>Playground</h1>' +
      '<div class="seg" id="seg">' +
        '<button data-m="python">Python</button><button data-m="js">JavaScript</button><button data-m="web">Web page</button>' +
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
    P = Object.assign({ completed: {}, quiz: {}, code: {}, xp: 0, last: null, playground: null,
                       activity: {}, name: '', railHidden: false }, saved);
    if (!P.activity || typeof P.activity !== 'object') P.activity = {};
  }
  renderShell();
  applyTheme();
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
  go({ view: 'home' });
}
if (typeof window !== 'undefined' && typeof document !== 'undefined' && !(typeof globalThis !== 'undefined' && globalThis.__CW_NO_BOOT)) {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
}
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { parseBundle: parseBundle, renderMd: renderMd, Highlight: Highlight, dedent: dedent, mdInline: mdInline, TRACKS: TRACKS, LESSON_INDEX: LESSON_INDEX, DEGREE: DEGREE };
}
