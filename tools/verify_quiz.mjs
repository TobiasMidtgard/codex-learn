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
 * THE BLANKS BANK — 1103 graded holes that this gate did not look at.
 *
 *   `blanks` is a four-way graded question in everything but name, and it had no gate
 *   at all: the loop above reads m.quiz and stops, which is the "a gate that skips
 *   what it did not expect" failure this repository has already had once. What that
 *   left unwatched was not hypothetical. The options were drawn in the order they were
 *   authored and never shuffled, and the answer to 735 of the 1103 was the FIRST
 *   one — 66.6% against 26% for guessing, with 26 courses at 100%, EE231 answering all
 *   89 of its blanks to the top option. Pressing the first button was a perfect score
 *   in a quarter of the catalogue. renderBlanks now shuffles through the same helper
 *   the quiz uses, and the section at the bottom of this file proves it by driving the
 *   real renderer rather than by reading the source.
 *
 *   The same structure rules apply here, plus two of its own:
 *
 *   * an option is drawn with esc(), not through the markdown renderer, and that is
 *     deliberate — it is a literal fragment dropped into a `white-space:pre` monospace
 *     listing, `a**2 + b**2` is Python exponentiation in fourteen of them, and a
 *     MathML fraction would move every column of an ASCII table after it. So `$...$`
 *     or a code span authored into an OPTION reaches the screen as its own source.
 *     Measured and ratcheted like the length tell, because 66 of them predate the
 *     measurement.
 *   * the PROMPT is prose and does go through mdInline, so it is held to what that can
 *     draw: inline markup only, no block markup of any kind, not even a fence.
 *
 *     node tools/verify_quiz.mjs                  # every course
 *     node tools/verify_quiz.mjs catalog/CS201.json
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const BUDGET = join(ROOT, 'tools', 'quiz_budget.json');

/* The same expression emit.py rejects with, kept in step by the test below.
   "the final answer" and "the last answer" are excluded on purpose: they are the
   ordinary way to say the end of a calculation, and the rule only started reaching
   them when it was extended to `blanks`, where EE231/M1.2 says "it will be missing
   from the final answer too" — correct content that the wider pattern condemned on
   its first run, which is the same trap the case-folding note below records. */
const POSITIONAL =
  /\b(?:[Oo]ption|[Cc]hoice|[Aa]nswer)s?\s+[A-E]\b|\b[Tt]he\s+(?:first|second|third|fourth|fifth|last|final)\s+(?:option|choice)\b|\b[Tt]he\s+(?:first|second|third|fourth|fifth)\s+answer\b/;

/* emit.py's POSITIONAL is the authority; if the two drift, the artifact is being
   checked against a rule the source no longer applies */
{
  const py = readFileSync(join(ROOT, 'tools', 'emit.py'), 'utf8');
  const want = ['[Oo]ption|[Cc]hoice|[Aa]nswer',
    'first|second|third|fourth|fifth|last|final)\\s+(?:option|choice)',
    'first|second|third|fourth|fifth)\\s+answer'];
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

/* A blank's prompt goes through mdInline(), which draws inline markup and NO block
   markup whatever — not even the paragraphs quizProse() handles, and not a fence. */
const UNDRAWABLE_INLINE = UNDRAWABLE.concat([['a fenced block', /```/]]);

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
let blankUnits = 0, blankHoles = 0, blankWhys = 0, blankMarkup = 0;

for (const file of files) {
  const course = JSON.parse(readFileSync(file, 'utf8'));
  const id = course.id || basename(file, '.json');
  const found = [];
  const bad = [];
  const holes = [];        /* every graded hole in the course, for the tells */
  const bbad = [];
  let markup = 0;          /* options carrying markup the monospace slot draws literally */

  /* ------------------------------------------------------------ the blanks bank */
  (course.modules || []).forEach((m, mi) => {
    asList(m.blanks).forEach((u, ui) => {
      const where = `M${mi + 1}${ui ? '.' + (ui + 1) : ''}`;
      blankUnits++;
      /* the listing is authored with ___ where each blank goes and the nth ___ takes
         the nth entry; a mismatch silently drops a hole off the end or leaves one
         with nowhere to appear. emit.py refuses it at source — this is the artifact */
      const gaps = String(u.listing || '').split('___').length - 1;
      if (gaps !== (u.blanks || []).length) {
        bbad.push(`${where}: the listing has ${gaps} ___ but ${(u.blanks || []).length} ` +
          'blank(s) are defined — the nth hole takes the nth blank, so the tail of ' +
          'one of them never reaches the screen');
      }
      (u.blanks || []).forEach((h, hi) => {
        const at = `${where}/b${hi + 1}`;
        const opts = h.opts || [];
        holes.push(h);
        blankHoles++;
        if (opts.some((o) => !String(o).trim())) bbad.push(`${at}: an option is empty`);
        const seen = opts.map(norm);
        const dupe = seen.find((s, i) => seen.indexOf(s) !== i);
        if (dupe !== undefined) {
          bbad.push(`${at}: two options read the same (${JSON.stringify(dupe.slice(0, 46))}) — ` +
            'only one index is accepted, so the twin of the key is marked wrong with no reason given');
        }
        if (!String(h.why || '').trim()) bbad.push(`${at}: no explanation`);
        if (h.whys !== undefined && h.whys !== null) {
          if (!Array.isArray(h.whys) || h.whys.length !== opts.length) {
            bbad.push(`${at}: ${Array.isArray(h.whys) ? h.whys.length : 'non-list'} per-option ` +
              `explanations for ${opts.length} options — one each, the key included`);
          } else {
            blankWhys += h.whys.length;
            h.whys.forEach((w, wi) => {
              if (!String(w || '').trim()) bbad.push(`${at}: per-option explanation ${wi + 1} is empty`);
              const p = POSITIONAL.exec(w || '');
              if (p) bbad.push(`${at}: a per-option explanation says ${JSON.stringify(p[0])}, ` +
                'and the options are shuffled per learner now');
            });
          }
        }
        const p = POSITIONAL.exec(h.why || '');
        if (p) bbad.push(`${at}: the explanation says ${JSON.stringify(p[0])}, ` +
          'and the options are shuffled per learner now');

        /* the prompt and the explanations are prose drawn by mdInline, which handles
           no block markup at all */
        const prose = [['prompt', h.prompt], ['explanation', h.why]]
          .concat((Array.isArray(h.whys) ? h.whys : []).map((w, i) => [`per-option explanation ${i + 1}`, w]));
        for (const [tag, text] of prose) {
          for (const [name, rx] of UNDRAWABLE_INLINE) {
            if (rx.test(String(text || ''))) {
              bbad.push(`${at}: the ${tag} contains ${name}, and a blank's prose is drawn ` +
                'by mdInline, which draws no block markup at all — it would reach the ' +
                'screen as literal punctuation');
            }
          }
        }
        /* an option is a literal fragment of a `white-space:pre` monospace listing and
           is drawn with esc() on purpose — see the header. Markup in one is therefore
           its own source on the screen. Counted rather than refused, because 66
           predate the measurement; the budget stops there being a 67th. */
        for (const o of opts) {
          if (/\$[^$]+\$/.test(String(o)) || /`[^`]+`/.test(String(o))) markup++;
        }
      });
    });
  });

  /* ------------------------------------------------------------- the quiz bank */
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

  if (!found.length && !holes.length) continue;
  units += (course.modules || []).reduce((n, m) => n + asList(m.quiz).length, 0);
  questions += found.length;
  blankMarkup += markup;

  const b = budget[id];
  const lines = [];
  let failed = bad.length > 0 || bbad.length > 0;
  bad.forEach((l) => lines.push(`            ! ${l}`));
  bbad.forEach((l) => lines.push(`            ! blanks ${l}`));

  if (b === undefined) {
    const t0 = tells(found);
    failed = true;
    lines.push(`            ! no entry in ${basename(BUDGET)}. Add ` +
      `"${id}": { "longest": ${t0.longest}, "shortest": ${t0.shortest} } — a course with ` +
      'no recorded score is a course whose question bank can drift unwatched');
  }

  /* the same ratchet, run over the quiz bank and then over the blanks bank */
  const banks = [
    { tag: 'question', kind: 'quiz', items: found, budget: b, extra: null },
    { tag: 'hole', kind: 'blanks', items: holes, budget: b && b.blanks,
      extra: { name: 'markup', got: markup } },
  ];
  for (const bank of banks) {
    if (!bank.items.length) continue;
    const t = tells(bank.items);
    const bb = bank.budget;
    const label = bank.kind === 'quiz' ? '' : 'blanks ';
    if (bb === undefined || bb === null) {
      failed = true;
      lines.push(`            ! no "blanks" entry in ${basename(BUDGET)} for ${id}. Add ` +
        `"blanks": { "longest": ${t.longest}, "shortest": ${t.shortest}, ` +
        `"markup": ${markup} } inside it — 1103 graded holes went unwatched once already`);
      continue;
    }
    if (t.longest > bb.longest) {
      failed = true;
      lines.push(`            ! ${label}"pick the longest option" now scores ${t.longest}/${t.n} ` +
        `(${Math.round(t.longest / t.n * 100)}%), over the budget of ${bb.longest}. ` +
        'Give the distractors the same weight as the key, or the bank rewards reading nothing');
    }
    if (t.shortest > bb.shortest) {
      failed = true;
      lines.push(`            ! ${label}"pick the shortest option" now scores ${t.shortest}/${t.n}, ` +
        `over the budget of ${bb.shortest} — the length tell has been inverted, not removed`);
    }
    if (bank.extra && bank.extra.got > (bb[bank.extra.name] || 0)) {
      failed = true;
      lines.push(`            ! ${bank.extra.got} option(s) carry markup the monospace slot ` +
        `draws literally, over the budget of ${bb[bank.extra.name] || 0}. An option is a ` +
        'fragment of the listing, so write it the way the listing is written');
    }
    const better = t.longest < bb.longest || t.shortest < bb.shortest ||
      (bank.extra && bank.extra.got < (bb[bank.extra.name] || 0));
    if (better) {
      loose.push(`${id}${bank.kind === 'quiz' ? '' : ' blanks'}: longest ${bb.longest} -> ${t.longest}` +
        `, shortest ${bb.shortest} -> ${t.shortest}` +
        (bank.extra ? `, markup ${bb[bank.extra.name] || 0} -> ${bank.extra.got}` : ''));
    }
    lines.push(`            ${t.n} ${bank.tag}(s) · longest-is-key ${t.longest}` +
      ` (budget ${bb.longest}) · shortest-is-key ${t.shortest} (budget ${bb.shortest})` +
      (bank.extra ? ` · markup ${bank.extra.got} (budget ${bb[bank.extra.name] || 0})` : '') +
      ` · mean length margin ${t.margin >= 0 ? '+' : ''}${t.margin.toFixed(1)}`);
  }

  console.log(`[${failed ? 'FAIL' : 'ok  '}] ${id.padEnd(8)} ${found.length} question(s), ` +
    `${holes.length} hole(s)`);
  lines.forEach((l) => console.log(l));
  if (failed) problems++;
}

if (!questions && !blankHoles) { console.log('no quiz or blanks units found'); process.exit(0); }

/* ------------------------------------------------------------------------------
   What the renderer actually draws.

   Everything above reads the artifact. This drives the shipped renderBlanks in a
   stubbed DOM — the same trick verify_circuit_ui.mjs uses on the editor — because
   the two defects that mattered most here were both invisible in the JSON: the
   options were never shuffled, and the prompt was escaped rather than rendered. A
   rule about either one, written as a source-shape check, would have been a gate
   enforcing a comment. */
const live = await import('./blanks_stage.mjs').catch((e) => {
  console.error('FAIL  cannot stage the renderer: ' + e.message);
  process.exit(1);
});
const stage = live.stage();
let draws = 0, picks = 0, slot0 = 0, shuffledHoles = 0;
const liveBad = [];

for (const file of files) {
  const course = JSON.parse(readFileSync(file, 'utf8'));
  const id = course.id || basename(file, '.json');
  (course.modules || []).forEach((m, mi) => {
    asList(m.blanks).forEach((u, ui) => {
      const lessonId = `${id}-M${mi + 1}-FB${ui ? ui + 1 : ''}`;
      let r;
      try { r = stage.drive(lessonId, u); }
      catch (e) { liveBad.push(`${lessonId}: renderBlanks threw — ${e.message}`); return; }
      draws += r.draws;
      picks += r.picks;
      for (const line of r.problems) liveBad.push(`${lessonId}: ${line}`);
      for (const h of r.holes) {
        shuffledHoles++;
        if (h.keyAt === 0) slot0++;
      }
      /* a course whose every drawn key still lands in the top slot is a course whose
         shuffle is not running — the state this whole section exists to detect */
      if (r.holes.length >= 4 && r.holes.every((h) => h.keyAt === 0)) {
        liveBad.push(`${lessonId}: every one of its ${r.holes.length} answers is drawn in ` +
          'the top slot — the shuffle is not reaching this unit');
      }
    });
  });
}

/* Aggregate, because any single unit may legitimately shuffle back to the order it
   was authored in. A shuffle puts the key on top with probability 1/k, and this bank
   is 1043 four-way holes, 35 three-way and 25 two-way, so the expected rate is 25.8%.
   The authored order put the key first 66.6% of the time. */
if (shuffledHoles) {
  const rate = slot0 / shuffledHoles;
  if (rate > 0.40 || rate < 0.14) {
    liveBad.push(`the drawn answer lands in the top slot for ${slot0} of ${shuffledHoles} ` +
      `holes (${(rate * 100).toFixed(1)}%), which is nowhere near the ` +
      '25.8% a shuffle produces on this bank — it is either not shuffling or not uniform');
  }
}

if (liveBad.length) {
  console.log('[FAIL] renderer');
  liveBad.slice(0, 40).forEach((l) => console.log(`            ! ${l}`));
  if (liveBad.length > 40) console.log(`            ... and ${liveBad.length - 40} more`);
  problems++;
} else {
  console.log(`[ok  ] renderer  ${draws} draw(s), ${picks} option(s) picked and read back · ` +
    `the answer is drawn in the top slot ${(slot0 / shuffledHoles * 100).toFixed(1)}% ` +
    'of the time, against 66.6% before the shuffle');
}

if (loose.length) {
  console.log(`\n${loose.length} bank(s) now score BETTER than their budget. Lower the ` +
    `entries in ${basename(BUDGET)} so the improvement cannot be given back:`);
  loose.forEach((l) => console.log(`  ${l}`));
}

console.log(problems
  ? `\n${problems} course(s) with a question bank defect or over budget`
  : `\nAll good: ${questions} question(s) in ${units} quiz unit(s) and ${blankHoles} ` +
    `hole(s) in ${blankUnits} blanks unit(s) verified · ${whysGiven + blankWhys} per-option ` +
    `explanation(s) · ${draws} live draws, ${picks} options picked and read back · ` +
    'every bank within its answer-tell budget.');
process.exit(problems || loose.length ? 1 : 0);
