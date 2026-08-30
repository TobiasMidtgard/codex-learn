/**
 * spec.mjs — render the degree catalog as a standalone specification handbook.
 *   node tools/spec.mjs   ->   build/catalog.html
 */

import { readFileSync, writeFileSync, readdirSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

/* A unit key holds nothing, one authored object, or a list of them. */
const asList = (x) => (!x ? [] : (Array.isArray(x) ? x : [x]));

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const CATALOG = join(ROOT, 'catalog');
const OUT_DIR = join(ROOT, 'build');
const OUT = join(OUT_DIR, 'catalog.html');

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
  .replace(/>/g, '&gt;').replace(/"/g, '&quot;');

/* ---------------------------------------------------------------- markdown */
function inline(s) {
  let t = esc(s);
  t = t.replace(/`([^`]+)`/g, (_, c) => `<code>${c}</code>`);
  t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/(^|[^*\w])\*([^*\n]+)\*(?![\w*])/g, '$1<em>$2</em>');
  return t;
}
function md(src) {
  const lines = String(src || '').replace(/\r/g, '').split('\n');
  let out = '', i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (/^```/.test(line)) {
      const lang = line.slice(3).trim();
      const buf = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i])) { buf.push(lines[i]); i++; }
      i++;
      out += `<pre class="code"${lang ? ` data-lang="${esc(lang)}"` : ''}><code>${esc(buf.join('\n'))}</code></pre>`;
      continue;
    }
    if (/^#{1,4}\s/.test(line)) {
      const lvl = Math.min(6, Math.max(4, line.match(/^#+/)[0].length + 2));
      out += `<h${lvl}>${inline(line.replace(/^#+\s*/, ''))}</h${lvl}>`;
      i++; continue;
    }
    if (/^\|/.test(line)) {
      const rows = [];
      while (i < lines.length && /^\|/.test(lines[i])) { rows.push(lines[i]); i++; }
      const cells = (r) => r.replace(/^\|/, '').replace(/\|\s*$/, '').split('|').map((c) => c.trim());
      let t = '<div class="scroll"><table><thead><tr>' +
        cells(rows[0]).map((c) => `<th>${inline(c)}</th>`).join('') + '</tr></thead><tbody>';
      for (let r = 1; r < rows.length; r++) {
        if (/^\|\s*:?-{2,}/.test(rows[r])) continue;
        t += '<tr>' + cells(rows[r]).map((c) => `<td>${inline(c)}</td>`).join('') + '</tr>';
      }
      out += t + '</tbody></table></div>';
      continue;
    }
    if (/^\s*[-*]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*]\s+/, '')); i++;
      }
      out += '<ul>' + items.map((x) => `<li>${inline(x)}</li>`).join('') + '</ul>';
      continue;
    }
    if (/^\s*\d+[.)]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+[.)]\s+/, '')); i++;
      }
      out += '<ol>' + items.map((x) => `<li>${inline(x)}</li>`).join('') + '</ol>';
      continue;
    }
    if (!line.trim()) { i++; continue; }
    const buf = [line]; i++;
    while (i < lines.length && lines[i].trim() &&
           !/^(#{1,4}\s|```|\s*[-*]\s+|\s*\d+[.)]\s+|\|)/.test(lines[i])) { buf.push(lines[i]); i++; }
    out += `<p>${inline(buf.join(' '))}</p>`;
  }
  return out;
}

/* ---------------------------------------------------------------- data */
const spine = JSON.parse(readFileSync(join(CATALOG, '_spine.json'), 'utf8'));
const courses = [];
for (const row of spine.courses) {
  const p = join(CATALOG, row.id + '.json');
  if (!existsSync(p)) continue;
  const c = JSON.parse(readFileSync(p, 'utf8'));
  for (const k of ['title', 'year', 'level', 'credits', 'hours']) c[k] = row[k];
  c.prereqs = row.prereqs;
  c.stack = c.stack && c.stack.length ? c.stack : row.stack;
  courses.push(c);
}
const known = new Set(courses.map((c) => c.id));
const totals = {
  courses: courses.length,
  modules: courses.reduce((s, c) => s + c.modules.length, 0),
  labs: courses.reduce((s, c) => s + c.modules.reduce((n, m) => n + asList(m.lab).length, 0), 0),
  checks: courses.reduce((s, c) => s + c.modules.reduce((n, m) => n + asList(m.lab).reduce((k, l) => k + l.tests.length, 0), 0)
    + (c.capstone.tests || []).length, 0),
  credits: courses.reduce((s, c) => s + (c.credits || 0), 0),
  hours: courses.reduce((s, c) => s + (c.hours || 0), 0),
};

/* ---------------------------------------------------------------- render */
const prereqChip = (id) => known.has(id)
  ? `<a class="pc" href="#${id}">${esc(id)}</a>`
  : `<span class="pc off">${esc(id)}</span>`;

function courseSection(c) {
  const modules = c.modules.map((m, i) => `
    <section class="module">
      <div class="mhead">
        <span class="mnum">${String(i + 1).padStart(2, '0')}</span>
        <div>
          <h4>${esc(m.title)}</h4>
          ${m.summary ? `<p class="msum">${inline(m.summary)}</p>` : ''}
        </div>
      </div>
      <div class="mbody">
        <div class="concepts">
          <h5>Key theoretical concepts</h5>
          <ul>${m.concepts.map((x) => `<li>${inline(x)}</li>`).join('')}</ul>
        </div>
        ${asList(m.lab).map((lab) => `
        <div class="lab">
          <h5>Interactive coding lab<span class="labmeta">${lab.minutes} min · ${lab.tests.length} automated checks · ${esc(lab.runtime)}</span></h5>
          <p class="labtitle">${esc(lab.title)}</p>
          <div class="brief">${md(lab.brief)}</div>
          <details class="checks">
            <summary>Automated test requirements <span class="cnt">${lab.tests.length}</span></summary>
            <ol>${lab.tests.map((t) => `<li>${esc(t.name)}</li>`).join('')}</ol>
          </details>
        </div>`).join('')}
      </div>
    </section>`).join('');

  const cap = c.capstone;
  const rubric = (cap.rubric || []).map((r) => `
    <tr>
      <td class="crit">${esc(r.criterion)}</td>
      <td class="wt"><span class="wnum">${r.weight}%</span><span class="wbar"><i style="width:${r.weight}%"></i></span></td>
      <td>${inline(r.evidence)}</td>
    </tr>`).join('');

  return `
  <article class="course lv-${c.level}" id="${c.id}" data-search="${esc((c.id + ' ' + c.title + ' ' + c.summary + ' ' + c.stack.join(' ') + ' ' + c.level).toLowerCase())}">
    <header class="chead">
      <div class="cid">
        <span class="code">${esc(c.id)}</span>
        <span class="lvl">${esc(c.level)}</span>
        <span class="yr">Year ${c.year}</span>
      </div>
      <h3>${esc(c.title)}</h3>
      <p class="lede">${inline(c.summary)}</p>
    </header>

    <dl class="meta">
      <div><dt>Prerequisites</dt><dd>${c.prereqs.length ? c.prereqs.map(prereqChip).join('') : '<span class="pc none">None</span>'}</dd></div>
      <div><dt>Primary stack</dt><dd>${c.stack.map((s) => `<span class="tech">${esc(s)}</span>`).join('')}</dd></div>
      <div><dt>Credits</dt><dd class="num">${c.credits}</dd></div>
      <div><dt>Notional hours</dt><dd class="num">${c.hours}</dd></div>
      <div><dt>Assessment</dt><dd class="plain">${esc(c.assessment || '—')}</dd></div>
    </dl>

    ${c.outcomes && c.outcomes.length ? `
    <div class="outcomes">
      <h5>On completion, the student can</h5>
      <ul>${c.outcomes.map((o) => `<li>${inline(o)}</li>`).join('')}</ul>
    </div>` : ''}

    <div class="modules">${modules}</div>

    <section class="capstone">
      <div class="caphead">
        <span class="capeyebrow">Capstone practical project</span>
        <h4>${esc(cap.title)}</h4>
      </div>
      <div class="brief">${md(cap.brief)}</div>
      <div class="capgrid">
        ${cap.deliverables && cap.deliverables.length ? `<div><h5>Deliverables</h5><ul>${cap.deliverables.map((x) => `<li>${inline(x)}</li>`).join('')}</ul></div>` : ''}
        ${cap.constraints && cap.constraints.length ? `<div><h5>System constraints</h5><ul>${cap.constraints.map((x) => `<li>${inline(x)}</li>`).join('')}</ul></div>` : ''}
      </div>
      ${rubric ? `<h5 class="rubh">Evaluation rubric</h5>
      <div class="scroll"><table class="rubric"><thead><tr><th>Criterion</th><th>Weight</th><th>Evidence assessed</th></tr></thead><tbody>${rubric}</tbody></table></div>` : ''}
      ${(cap.tests || []).length ? `<p class="capnote">Graded by <strong>${cap.tests.length}</strong> automated checks executed against the submission.</p>` : ''}
    </section>
  </article>`;
}

const years = spine.program.years.map((y) => {
  const list = courses.filter((c) => c.year === y.n);
  if (!list.length) return '';
  return `
  <section class="year" id="year-${y.n}">
    <header class="yhead">
      <span class="ynum">Year ${y.n}</span>
      <h2>${esc(y.title)}</h2>
      <p>${esc(y.theme)}</p>
      <div class="ystats">
        <span>${list.length} courses</span>
        <span>${list.reduce((s, c) => s + c.credits, 0)} credits</span>
        <span>${list.reduce((s, c) => s + c.modules.reduce((n, m) => n + asList(m.lab).length, 0), 0)} labs</span>
      </div>
    </header>
    ${list.map(courseSection).join('')}
  </section>`;
}).join('');

const nav = spine.program.years.map((y) => {
  const list = courses.filter((c) => c.year === y.n);
  if (!list.length) return '';
  return `<div class="navyear">
    <a class="ny" href="#year-${y.n}">Year ${y.n} · ${esc(y.title)}</a>
    <ul>${list.map((c) => `<li><a href="#${c.id}" data-nav="${c.id}"><span class="nc">${esc(c.id)}</span>${esc(c.title)}</a></li>`).join('')}</ul>
  </div>`;
}).join('');

const html = `<title>CS Degree Handbook</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Spectral:ital,wght@0,400;0,600;0,700;1,400&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{
  --paper:#F2F4F7; --card:#FFFFFF; --sunk:#E8ECF2;
  --ink:#16202E; --ink-2:#465468; --ink-3:#778395;
  --rule:#DCE2EA; --rule-2:#C3CCD8;
  --accent:#1D5FD6; --accent-soft:#E4EDFC;
  --ochre:#A2621B; --ochre-soft:#F7EEDF;
  --lv1:#5B8DEF; --lv2:#2E6FD9; --lv3:#1D4EAE; --lv4:#16307A;
  --serif:"Spectral",Georgia,"Times New Roman",serif;
  --sans:"IBM Plex Sans","Segoe UI",system-ui,-apple-system,sans-serif;
  --mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
  --maxw:1360px;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --paper:#0E141C; --card:#151D28; --sunk:#1B2531;
    --ink:#E6ECF4; --ink-2:#AFBCCD; --ink-3:#7C8BA0;
    --rule:#26313F; --rule-2:#374453;
    --accent:#7BA6F5; --accent-soft:#17253E;
    --ochre:#D9A55E; --ochre-soft:#2C2214;
    --lv1:#8FB4F7; --lv2:#6E9BF2; --lv3:#4F7FE0; --lv4:#3D65C4;
  }
}
:root[data-theme="dark"]{
  --paper:#0E141C; --card:#151D28; --sunk:#1B2531;
  --ink:#E6ECF4; --ink-2:#AFBCCD; --ink-3:#7C8BA0;
  --rule:#26313F; --rule-2:#374453;
  --accent:#7BA6F5; --accent-soft:#17253E;
  --ochre:#D9A55E; --ochre-soft:#2C2214;
  --lv1:#8FB4F7; --lv2:#6E9BF2; --lv3:#4F7FE0; --lv4:#3D65C4;
}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:15.5px;line-height:1.6;-webkit-font-smoothing:antialiased}
a{color:var(--accent)}
h1,h2,h3,h4{font-family:var(--serif);text-wrap:balance;margin:0}
.scroll{overflow-x:auto}
code{font-family:var(--mono);font-size:.88em;background:var(--sunk);padding:1px 5px;border-radius:4px}
pre.code{position:relative;overflow-x:auto;background:var(--sunk);border:1px solid var(--rule);border-radius:8px;padding:13px 15px;margin:0 0 14px;font-family:var(--mono);font-size:12.7px;line-height:1.62}
pre.code code{background:none;padding:0;font-size:inherit}
pre.code[data-lang]::after{content:attr(data-lang);position:absolute;top:7px;right:10px;font-family:var(--mono);font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3)}
table{border-collapse:collapse;width:100%;font-size:14.2px;margin:0 0 14px}
th{text-align:left;font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);font-weight:600;padding:6px 10px;border-bottom:1px solid var(--rule-2)}
td{padding:8px 10px;border-bottom:1px solid var(--rule);vertical-align:top;color:var(--ink-2)}
tr:last-child td{border-bottom:0}

/* masthead */
.masthead{border-bottom:1px solid var(--rule);background:var(--card)}
.mwrap{max-width:var(--maxw);margin:0 auto;padding:42px 30px 34px}
.eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--accent);margin:0 0 12px}
.masthead h1{font-size:clamp(30px,4.6vw,50px);font-weight:700;letter-spacing:-.015em;line-height:1.04;margin:0 0 12px}
.masthead p{max-width:64ch;color:var(--ink-2);font-size:16.5px;margin:0 0 22px}
.figures{display:flex;flex-wrap:wrap;gap:0;border:1px solid var(--rule);border-radius:9px;overflow:hidden}
.fig{flex:1 1 120px;padding:13px 16px;border-right:1px solid var(--rule);background:var(--card)}
.fig:last-child{border-right:0}
.fig b{display:block;font-family:var(--mono);font-size:23px;font-weight:600;letter-spacing:-.02em;font-variant-numeric:tabular-nums}
.fig span{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3)}

/* shell */
.shell{max-width:var(--maxw);margin:0 auto;padding:0 30px 90px;display:grid;grid-template-columns:250px minmax(0,1fr);gap:44px;align-items:start}
.index{position:sticky;top:0;max-height:100vh;overflow-y:auto;padding:26px 0 40px}
.finder{width:100%;padding:8px 11px;font:14px var(--sans);color:var(--ink);background:var(--card);border:1px solid var(--rule-2);border-radius:7px;margin-bottom:16px}
.finder::placeholder{color:var(--ink-3)}
.navyear{margin-bottom:18px}
.ny{display:block;font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-3);text-decoration:none;padding-bottom:6px;border-bottom:1px solid var(--rule);margin-bottom:7px}
.ny:hover{color:var(--accent)}
.index ul{list-style:none;margin:0;padding:0}
.index li a{display:flex;gap:8px;align-items:baseline;padding:3px 0;font-size:13.2px;color:var(--ink-2);text-decoration:none;line-height:1.35}
.index li a:hover{color:var(--accent)}
.index li a.on{color:var(--accent);font-weight:600}
.nc{font-family:var(--mono);font-size:10.5px;color:var(--ink-3);min-width:52px;flex:none}

/* years */
.year{padding-top:40px}
.yhead{padding:0 0 8px;margin-bottom:26px;border-bottom:2px solid var(--ink)}
.ynum{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.yhead h2{font-size:clamp(24px,3vw,33px);letter-spacing:-.015em;margin:5px 0 4px}
.yhead p{margin:0 0 12px;color:var(--ink-2);max-width:62ch}
.ystats{display:flex;gap:16px;font-family:var(--mono);font-size:11.5px;color:var(--ink-3);padding-bottom:10px;font-variant-numeric:tabular-nums}

/* course */
.course{background:var(--card);border:1px solid var(--rule);border-radius:11px;padding:26px 28px;margin-bottom:20px;scroll-margin-top:16px}
.course.hide{display:none}
.lv-Beginner{--lv:var(--lv1)} .lv-Intermediate{--lv:var(--lv2)}
.lv-Advanced{--lv:var(--lv3)} .lv-Expert{--lv:var(--lv4)}
.cid{display:flex;align-items:center;gap:9px;flex-wrap:wrap;margin-bottom:9px}
.code{font-family:var(--mono);font-weight:600;font-size:12.5px;letter-spacing:.05em;color:#fff;background:var(--lv);padding:3px 8px;border-radius:5px}
.lvl{font-size:11px;letter-spacing:.08em;text-transform:uppercase;font-weight:600;color:var(--lv)}
.yr{font-family:var(--mono);font-size:11px;color:var(--ink-3)}
.chead h3{font-size:26px;font-weight:700;letter-spacing:-.015em;line-height:1.15;margin:0 0 8px}
.lede{margin:0 0 18px;color:var(--ink-2);max-width:66ch}

.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:0;margin:0 0 20px;border:1px solid var(--rule);border-radius:8px;overflow:hidden}
.meta>div{padding:11px 14px;border-right:1px solid var(--rule)}
.meta>div:last-child{border-right:0}
dt{font-size:10px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin-bottom:5px}
dd{margin:0;display:flex;flex-wrap:wrap;gap:5px}
dd.num{font-family:var(--mono);font-size:16px;font-weight:600;font-variant-numeric:tabular-nums}
dd.plain{display:block;font-size:13px;color:var(--ink-2);line-height:1.45}
.pc{font-family:var(--mono);font-size:11.5px;font-weight:600;padding:2px 7px;border-radius:5px;background:var(--accent-soft);color:var(--accent);text-decoration:none}
.pc:hover{background:var(--accent);color:#fff}
.pc.none,.pc.off{background:var(--sunk);color:var(--ink-3)}
.tech{font-family:var(--mono);font-size:11px;padding:2px 7px;border-radius:5px;background:var(--sunk);color:var(--ink-2)}

.outcomes{background:var(--sunk);border-radius:8px;padding:14px 18px;margin:0 0 22px}
h5{font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--ink-3);margin:0 0 8px;font-weight:600}
.outcomes ul{margin:0;padding-left:18px;columns:2;column-gap:30px}
.outcomes li{margin:3px 0;break-inside:avoid;font-size:14px;color:var(--ink-2)}

.module{border-top:1px solid var(--rule);padding:18px 0 4px}
.mhead{display:flex;gap:13px;align-items:baseline;margin-bottom:12px}
.mnum{font-family:var(--mono);font-size:12px;font-weight:600;color:var(--ink-3);flex:none;padding-top:2px}
.mhead h4{font-size:18.5px;font-weight:600;letter-spacing:-.01em}
.msum{margin:3px 0 0;color:var(--ink-3);font-size:13.6px}
.mbody{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.25fr);gap:26px;padding-left:33px}
.concepts ul{margin:0;padding-left:17px}
.concepts li{margin:4px 0;font-size:14px;color:var(--ink-2)}
.lab{border-left:2px solid var(--accent);padding-left:16px}
.labmeta{display:block;font-family:var(--mono);font-size:10px;letter-spacing:.04em;text-transform:none;color:var(--ink-3);margin-top:3px;font-weight:400}
.labtitle{margin:0 0 9px;font-weight:600;font-size:15px}
.brief{font-size:14.2px;color:var(--ink-2)}
.brief p{margin:0 0 11px}
.brief ul,.brief ol{margin:0 0 11px;padding-left:19px}
.brief li{margin:3px 0}
.brief h4,.brief h5,.brief h6{font-family:var(--sans);font-size:12px;letter-spacing:.05em;text-transform:uppercase;color:var(--ink-3);margin:14px 0 6px;font-weight:600}
details.checks{margin-top:10px;border-top:1px dashed var(--rule-2);padding-top:9px}
details.checks summary{cursor:pointer;font-size:11px;letter-spacing:.07em;text-transform:uppercase;color:var(--ink-3);font-weight:600}
details.checks summary:hover{color:var(--accent)}
.cnt{font-family:var(--mono);background:var(--accent-soft);color:var(--accent);padding:1px 6px;border-radius:20px;margin-left:5px;letter-spacing:0}
details.checks ol{margin:9px 0 0;padding-left:20px}
details.checks li{font-size:13.2px;color:var(--ink-2);margin:3px 0}

.capstone{margin-top:22px;border:1px solid var(--rule);border-top:3px solid var(--ochre);border-radius:9px;padding:20px 22px;background:var(--card)}
.capeyebrow{font-family:var(--mono);font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--ochre)}
.caphead h4{font-size:20px;font-weight:700;letter-spacing:-.01em;margin:5px 0 12px}
.capgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px;margin:16px 0 4px}
.capgrid ul{margin:0;padding-left:18px}
.capgrid li{margin:4px 0;font-size:14px;color:var(--ink-2)}
.rubh{margin-top:20px}
.rubric .crit{font-weight:600;color:var(--ink);white-space:nowrap}
.rubric .wt{white-space:nowrap;width:110px}
.wnum{font-family:var(--mono);font-size:13px;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}
.wbar{display:block;width:78px;height:4px;border-radius:20px;background:var(--sunk);margin-top:4px;overflow:hidden}
.wbar i{display:block;height:100%;background:var(--ochre);border-radius:20px}
.capnote{margin:14px 0 0;font-size:13.4px;color:var(--ink-3);border-top:1px solid var(--rule);padding-top:11px}

.empty{padding:40px 0;color:var(--ink-3);font-size:15px}
.foot{max-width:var(--maxw);margin:0 auto;padding:26px 30px 60px;color:var(--ink-3);font-size:13px;border-top:1px solid var(--rule)}

@media (max-width:1080px){
  .shell{grid-template-columns:1fr;gap:0}
  .index{position:static;max-height:none;padding:22px 0 8px}
  .index .navyear{display:inline-block;vertical-align:top;width:min(100%,300px);margin-right:24px}
  .mbody{grid-template-columns:1fr;padding-left:0;gap:18px}
  .outcomes ul{columns:1}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
</style>

<header class="masthead">
  <div class="mwrap">
    <p class="eyebrow">Programme specification</p>
    <h1>${esc(spine.program.name)}</h1>
    <p>${esc(spine.program.subtitle)} Every module ends in a sandboxed coding lab whose reference solution is executed and verified against its own checks before it ships.</p>
    <div class="figures">
      <div class="fig"><b>${totals.courses}</b><span>Courses</span></div>
      <div class="fig"><b>${totals.modules}</b><span>Modules</span></div>
      <div class="fig"><b>${totals.labs}</b><span>Coding labs</span></div>
      <div class="fig"><b>${totals.checks}</b><span>Automated checks</span></div>
      <div class="fig"><b>${totals.credits}</b><span>Credits</span></div>
      <div class="fig"><b>${totals.hours.toLocaleString('en-GB')}</b><span>Notional hours</span></div>
    </div>
  </div>
</header>

<div class="shell">
  <nav class="index">
    <input class="finder" id="finder" type="search" placeholder="Filter courses…" aria-label="Filter courses">
    ${nav}
  </nav>
  <main>
    ${years}
    <p class="empty" id="noresults" hidden>No course matches that filter.</p>
  </main>
</div>
<footer class="foot">Generated from the Codewright course catalog. Difficulty is encoded in each course code's tint, from Beginner through Expert.</footer>

<script>
(function () {
  var finder = document.getElementById('finder');
  var courses = Array.prototype.slice.call(document.querySelectorAll('.course'));
  var years = Array.prototype.slice.call(document.querySelectorAll('.year'));
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('[data-nav]'));
  var none = document.getElementById('noresults');

  finder.addEventListener('input', function () {
    var q = finder.value.trim().toLowerCase();
    var shown = 0;
    courses.forEach(function (c) {
      var hit = !q || c.dataset.search.indexOf(q) !== -1;
      c.classList.toggle('hide', !hit);
      if (hit) shown++;
      var link = document.querySelector('[data-nav="' + c.id + '"]');
      if (link) link.parentElement.style.display = hit ? '' : 'none';
    });
    years.forEach(function (y) {
      y.style.display = y.querySelector('.course:not(.hide)') ? '' : 'none';
    });
    none.hidden = shown > 0;
  });

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var link = document.querySelector('[data-nav="' + e.target.id + '"]');
        if (link && e.isIntersecting) {
          navLinks.forEach(function (l) { l.classList.remove('on'); });
          link.classList.add('on');
        }
      });
    }, { rootMargin: '-10% 0px -80% 0px' });
    courses.forEach(function (c) { io.observe(c); });
  }
})();
</script>`;

mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(OUT, html, 'utf8');
console.log(`wrote ${OUT} (${(Buffer.byteLength(html, 'utf8') / 1024).toFixed(0)} KB) — ` +
  `${totals.courses} courses, ${totals.modules} modules, ${totals.labs} labs, ${totals.checks} checks`);
