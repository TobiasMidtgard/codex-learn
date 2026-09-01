/**
 * verify_quiz.mjs — the correctness gate for the question bank.
 *
 * Every other unit kind has a gate. A quiz did not, because there is nothing in a
 * quiz for a solver to disagree with: the key is whatever the author typed, and no
 * amount of arithmetic can tell you it is the wrong option. So this gate does not
 * try to mark the questions. It measures whether they can be answered WITHOUT
 * READING THEM — which is the failure mode a question bank actually has, and one
 * that is invisible to every reviewer who reads the questions.
 *
 * Two things it checks, and they are different in kind.
 *
 * STRUCTURE — hard failures, no budget, no exceptions:
 *
 *   * two options that read the same. Only one index is accepted, so a learner can
 *     pick the identical twin of the key and be marked wrong with nothing on the
 *     screen to explain it.
 *   * an option that is empty, or a `why` that is.
 *   * `whys` present but not one entry per option — a silently missing explanation
 *     is worse than none, because the ones around it make it look complete.
 *   * "option B", "the third choice" and friends anywhere in the feedback. The
 *     options are shuffled per learner, so a positional reference names nothing.
 *     emit.py rejects these at the source; this re-checks the artifact the app
 *     actually serves, because that is what a learner reads.
 *   * block markup the quiz renderer cannot draw. quizProse() handles paragraphs and
 *     fenced code and nothing else, so a table, heading, bullet or blockquote in a
 *     question reaches the screen as literal punctuation. This is not hypothetical:
 *     five EE131 stems were fenced Python blocks rendered by mdInline(), which had no
 *     fence support at all, so `if v > 0: print("positive") elif v > 5: ...` arrived
 *     on one unindented line — in a language whose meaning IS the indentation. The
 *     renderer was taught fences; everything else it still cannot draw is refused
 *     here, so the next author finds out at the gate rather than the learner does.
 *
 * EXPLOITABILITY — measured, and ratcheted against tools/quiz_budget.json:
 *
 *   The option order is shuffled per learner, so the answer's POSITION cannot be
 *   exploited. Its LENGTH can. When an author writes the key as a full, hedged,
 *   correct sentence and the distractors as short dismissals, "always pick the
 *   longest" becomes a strategy — and it survives every shuffle, every reviewer and
 *   every reading of the question, because each question looks fine on its own. It
 *   is only visible in aggregate, which is exactly what a gate is for.
 *
 *   At the time this was written the catalogue scored 48% on that strategy across
 *   1356 questions, against 25% for guessing. One course sat at 92%.
 *
 *   That debt cannot be paid off in one cycle without touching every course, which
 *   is its own kind of defect. So the budget file records what each course scores
 *   today and this gate fails when a course gets WORSE. New content therefore cannot
 *   add to the debt, and a cycle that improves a course is told to lower its entry.
 *
 *     node tools/verify_quiz.mjs                  # every course
 *     node tools/verify_quiz.mjs catalog/CS201.json
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const BUDGET = join(ROOT, 'tools', 'quiz_budget.json');

/* the same expression emit.py rejects with, kept in step by the test below */
const POSITIONAL =
  /\b(?:[Oo]ption|[Cc]hoice|[Aa]nswer)s?\s+[A-E]\b|\b[Tt]he\s+(?:first|second|third|fourth|fifth|last|final)\s+(?:option|choice|answer)\b/;

/* emit.py's POSITIONAL is the authority; if the two drift, the artifact is being
   checked against a rule the source no longer applies */
{
  const py = readFileSync(join(ROOT, 'tools', 'emit.py'), 'utf8');
  const want = ['[Oo]ption|[Cc]hoice|[Aa]nswer', 'first|second|third|fourth|fifth|last|final'];
  if (!want.every((w) => py.includes(w))) {
    console.error('FAIL  emit.py\'s positional-reference rule has changed shape — ' +
      'update POSITIONAL in verify_quiz.mjs to match it');
    process.exit(1);
  }
}

/* what quizProse() in src/app.js can actually draw: paragraphs, and fenced code.
   Everything else block-level arrives as literal punctuation. */
const UNDRAWABLE = [
  ['a table', /^[ \t]*\|/m],
  ['a heading', /^[ \t]*#{1,6}\s/m],
  ['a list bullet', /^[ \t]*[-*+][ \t]+\S/m],
  ['a blockquote', /^[ \t]*>[ \t]/m],
];

/* if the renderer stops handling fences, this gate is checking a rule that no longer
   holds — the EE131 stems would silently break again */
{
  const js = readFileSync(join(ROOT, 'src', 'app.js'), 'utf8');
  if (!/function quizProse/.test(js) || !js.includes('qcode')) {
    console.error('FAIL  src/app.js no longer has quizProse() drawing fenced blocks — ' +
      'the block-markup rule here was written against it');
    process.exit(1);
  }
}

const asList = (v) => (!v ? [] : Array.isArray(v) ? v : [v]);
/* whitespace only, and deliberately NOT case-folded. MA201/M4 asks which statement
   relates a density to its cdf and offers "f(x) = F'(x) and F = int f" against
   "F(x) = f'(x) and f = int F" — two opposite claims that differ in nothing but the
   case of two letters. Case-folding reported that correct question as a duplicate the
   first time this gate ran. A gate that condemns working content is worse than the
   defect it was written to find. */
const norm = (s) => String(s).replace(/\s+/g, ' ').trim();

/* What a learner who reads nothing scores. `longest` is the strategy that works;
   `shortest` is its mirror, and a course that fails it hard is exploitable in the
   other direction. Both are reported so a fix cannot just invert the problem. */
function tells(questions) {
  let longest = 0, shortest = 0, margin = 0;
  for (const q of questions) {
    const len = q.opts.map((o) => o.length);
    const key = len[q.a];
    const rest = len.filter((_, i) => i !== q.a);
    if (key > Math.max(...rest)) longest++;
    if (key < Math.min(...rest)) shortest++;
    margin += key - Math.max(...rest);
  }
  return { longest, shortest, n: questions.length,
           margin: questions.length ? margin / questions.length : 0 };
}

let budget = {};
try { budget = JSON.parse(readFileSync(BUDGET, 'utf8')); }
catch { console.error(`FAIL  cannot read ${basename(BUDGET)} — the ratchet is the gate`); process.exit(1); }

const only = process.argv[2];
const files = only ? [only]
  : readdirSync(join(ROOT, 'catalog'))
      .filter((f) => f.endsWith('.json') && !f.startsWith('_'))
      .map((f) => join(ROOT, 'catalog', f));

let problems = 0, units = 0, questions = 0, whysGiven = 0, loose = [];

for (const file of files) {
  const course = JSON.parse(readFileSync(file, 'utf8'));
  const id = course.id || basename(file, '.json');
  const found = [];
  const bad = [];

  (course.modules || []).forEach((m, mi) => {
    asList(m.quiz).forEach((u, ui) => {
      const where = `M${mi + 1}${ui ? '.' + (ui + 1) : ''}`;
      found.push(...(u.questions || []));
      (u.questions || []).forEach((q, qi) => {
        const at = `${where}/q${qi + 1}`;
        const opts = q.opts || [];
        if (opts.some((o) => !String(o).trim())) bad.push(`${at}: an option is empty`);
        const seen = opts.map(norm);
        const dupe = seen.find((s, i) => seen.indexOf(s) !== i);
        if (dupe !== undefined) {
          bad.push(`${at}: two options read the same (${JSON.stringify(dupe.slice(0, 46))}) — ` +
            'only one index is accepted, so the twin of the key is marked wrong with no reason given');
        }
        if (!String(q.why || '').trim()) bad.push(`${at}: no explanation`);
        if (q.whys !== undefined) {
          if (!Array.isArray(q.whys) || q.whys.length !== opts.length) {
            bad.push(`${at}: ${Array.isArray(q.whys) ? q.whys.length : 'non-list'} per-option ` +
              `explanations for ${opts.length} options — one each, the key included`);
          } else {
            whysGiven += q.whys.length;
            q.whys.forEach((w, wi) => {
              if (!String(w || '').trim()) bad.push(`${at}: per-option explanation ${wi + 1} is empty`);
              const hit = POSITIONAL.exec(w || '');
              if (hit) bad.push(`${at}: a per-option explanation says ${JSON.stringify(hit[0])}, ` +
                'and the options are shuffled per learner');
            });
          }
        }
        const hit = POSITIONAL.exec(q.why || '');
        if (hit) bad.push(`${at}: the explanation says ${JSON.stringify(hit[0])}, ` +
          'and the options are shuffled per learner');

        const texts = [['question', q.q], ['explanation', q.why]]
          .concat(opts.map((o, i) => [`option ${i + 1}`, o]))
          .concat((Array.isArray(q.whys) ? q.whys : []).map((w, i) => [`per-option explanation ${i + 1}`, w]));
        for (const [tag, text] of texts) {
          for (const [name, rx] of UNDRAWABLE) {
            if (rx.test(String(text || ''))) {
              bad.push(`${at}: the ${tag} contains ${name}, and the quiz renderer draws ` +
                'only paragraphs and fenced code — it would reach the screen as literal text');
            }
          }
          /* an option is rendered inside a <button>; a <pre> cannot go there */
          if (tag.startsWith('option') && /```/.test(String(text || ''))) {
            bad.push(`${at}: the ${tag} contains a fenced block, which options cannot carry ` +
              '— they are buttons. Put the listing in the question instead');
          }
        }
      });
    });
  });

  if (!found.length) continue;
  units += (course.modules || []).reduce((n, m) => n + asList(m.quiz).length, 0);
  questions += found.length;

  const t = tells(found);
  const b = budget[id];
  const lines = [];
  let failed = bad.length > 0;
  bad.forEach((l) => lines.push(`            ! ${l}`));

  if (b === undefined) {
    failed = true;
    lines.push(`            ! no entry in ${basename(BUDGET)}. Add ` +
      `"${id}": { "longest": ${t.longest}, "shortest": ${t.shortest} } — a course with ` +
      'no recorded score is a course whose question bank can drift unwatched');
  } else {
    if (t.longest > b.longest) {
      failed = true;
      lines.push(`            ! "pick the longest option" now scores ${t.longest}/${t.n} ` +
        `(${Math.round(t.longest / t.n * 100)}%), over the budget of ${b.longest}. ` +
        'Give the distractors the same weight as the key, or the bank rewards reading nothing');
    }
    if (t.shortest > b.shortest) {
      failed = true;
      lines.push(`            ! "pick the shortest option" now scores ${t.shortest}/${t.n}, ` +
        `over the budget of ${b.shortest} — the length tell has been inverted, not removed`);
    }
    if (t.longest < b.longest || t.shortest < b.shortest) {
      loose.push(`${id}: longest ${b.longest} -> ${t.longest}, shortest ${b.shortest} -> ${t.shortest}`);
    }
  }

  lines.push(`            ${t.n} question(s) · longest-is-key ${t.longest}` +
    ` (budget ${b ? b.longest : '?'}) · shortest-is-key ${t.shortest}` +
    ` (budget ${b ? b.shortest : '?'}) · mean length margin ${t.margin >= 0 ? '+' : ''}${t.margin.toFixed(1)}`);

  console.log(`[${failed ? 'FAIL' : 'ok  '}] ${id.padEnd(8)} ${found.length} question(s)`);
  lines.forEach((l) => console.log(l));
  if (failed) problems++;
}

if (!questions) { console.log('no quiz units found'); process.exit(0); }

if (loose.length) {
  console.log(`\n${loose.length} course(s) now score BETTER than their budget. Lower the ` +
    `entries in ${basename(BUDGET)} so the improvement cannot be given back:`);
  loose.forEach((l) => console.log(`  ${l}`));
}

console.log(problems
  ? `\n${problems} course(s) with a question bank defect or over budget`
  : `\nAll good: ${questions} question(s) in ${units} quiz unit(s) verified · ` +
    `${whysGiven} per-option explanation(s) · every course within its answer-tell budget.`);
process.exit(problems || loose.length ? 1 : 0);
