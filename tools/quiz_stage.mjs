/**
 * quiz_stage.mjs — the shipped quiz view, mounted in Node.
 *
 * The other half of blanks_stage.mjs, and it should have existed first. verify_quiz.mjs
 * has read the artifact since cycle 3 and driven the real renderBlanks since cycle 9,
 * and in between those two the surface that delivers 1366 questions across 252 units —
 * every graded question in the catalogue that is not a blank — was mounted by nothing.
 * That is the same "a gate that skips what it did not expect" shape the blanks half was
 * written to close, in the half next door.
 *
 * What was unwatched is not hypothetical. Three things in renderQuiz are invisible in
 * the JSON and invisible to any rule written about the source:
 *
 *   * THE SHUFFLE. The authored key is index 0 for 548 of the 1366 questions, and 22
 *     courses author EVERY key at index 0. shuffledOptions() is the only thing between
 *     that and a bank answerable by pressing the top button — which is precisely the
 *     state cycle 9 found the blanks bank in, where no shuffle existed. One mechanism,
 *     never tested.
 *   * THE REMAP. `whys` are authored against the order in the file and the learner
 *     presses a slot in another order, so renderQuiz reaches for
 *     `q.whys[shuffled[qi].order[oi]]`. Get that indirection wrong and every learner is
 *     answered with the explanation for an option they did not pick — content that is
 *     perfectly correct in the file and wrong on the screen, which no reader of either
 *     one would catch.
 *   * THE LETTER. A wrong answer is told "the answer is B", and that B is the key's
 *     DRAWN slot, not its authored index. The two differ for three quarters of all
 *     questions.
 *
 * So this loads the application through app_stage.mjs, mounts the real renderQuiz, and
 * presses every option of every question in the catalogue — reading back what the
 * learner who pressed it is actually shown.
 *
 * The authored index of a drawn option is recovered from its text, because `data-oi`
 * carries the drawn index and the authored one lives in a closure. That is sound only
 * because two options reading the same is already a hard structural failure in the gate
 * above; if that check is ever removed, this mapping loses its footing.
 */

import { El } from './dom_stub.mjs';
import { loadApp } from './app_stage.mjs';

/* One seed for the whole run, so the gate is deterministic. The shuffle is keyed on
   (seed, lesson id, question number), so this is one arbitrary learner, and what the
   caller checks is the aggregate over 1366 questions rather than any single order. */
const SEED = 0x9C1200;

export function stage() {
  const { app } = loadApp({
    exports: {
      renderQuiz: 'renderQuiz', LESSON_INDEX: 'LESSON_INDEX',
      LESSONS_OF: 'LESSONS_OF', mdInline: 'mdInline', quizProse: 'quizProse',
      seed: 'function (s) { P.seed = s; }',
      best: 'function (id) { return P.quiz[id]; }',
      forget: 'function (id) { delete P.quiz[id];' +
        ' if (P.completed) delete P.completed[id]; }',
    },
  });
  app.seed(SEED);

  /* app.js mints this lesson out of a module's `quiz` entry, and the id it mints is what
     the shuffle is keyed on — so the gate has to mint the same one */
  function lessonOf(lessonId, u) {
    return {
      id: lessonId, type: 'quiz', title: u.title, min: u.minutes || 6,
      trackId: 'stage', courseId: 'stage', num: 'x', questions: u.questions || [],
    };
  }

  function mount(lesson) {
    app.LESSON_INDEX[lesson.id] = {
      lesson,
      track: { id: 'stage', kind: 'course', title: 'staged', name: 'staged',
        program: 'stage', band: 1, modules: [{ title: 'staged', lessons: [lesson] }] },
      module: { title: 'staged' }, mi: 0,
    };
    app.LESSONS_OF.stage = [lesson];
    const root = new El('div');
    app.renderQuiz(root, lesson);
    return root;
  }

  const click = (el) => el.dispatchEvent({ type: 'click' });

  /* The tiny DOM keeps a text node as the source that was assigned, so text carrying
     `&`, `<` or `"` reads back as the entity esc() wrote. A browser hands back the
     character. Cycle 9 met this as a gate condemning fourteen correct options. */
  const textOf = (el) => String(el.textContent)
    .replace(/&quot;/g, '"').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');

  /* Read the SCREEN. The stub only keeps `innerHTML` on an element that was assigned
     one, and everything inside a parsed card was not — so reading a card's markup back
     gives the empty string and every comparison against it silently passes. Text is what
     a learner gets anyway, which is what this gate is about. */
  const readText = (el) => textOf(el).replace(/\s+/g, ' ').trim();

  /* what a string authored in the file looks like once the renderer has had it */
  function drawn(html) {
    const box = new El('div');
    box.innerHTML = html;
    return readText(box);
  }
  const asInline = (s) => drawn(app.mdInline(String(s == null ? '' : s)));
  const asProse = (s) => drawn(app.quizProse(String(s == null ? '' : s)));

  /* the option's own text, without the A/B/C/D key the button draws in front of it */
  function optText(btn) {
    const body = btn.querySelectorAll('span')
      .filter((s) => String(s.getAttribute('class') || '') !== 'k');
    return body.length ? readText(body[body.length - 1]) : readText(btn);
  }

  function drive(lessonId, u) {
    const problems = [];
    const questions = (u.questions || []).filter(Boolean);
    const lesson = lessonOf(lessonId, u);
    app.forget(lessonId);
    let draws = 0, picks = 0;
    const slots = [];
    if (!questions.length) return { draws, picks, slots, problems };

    /* ---- what a learner meets before pressing anything ---- */
    let root = mount(lesson); draws++;
    const cards = root.querySelectorAll('.quiz-q');
    if (cards.length !== questions.length) {
      problems.push(`${cards.length} question card(s) drawn for ${questions.length} question(s)`);
      return { draws, picks, slots, problems };
    }
    const out = root.querySelector('#quiz-out');
    if (!out || out.getAttribute('role') !== 'status') {
      problems.push('the result region is missing or is not a live region');
    } else if (readText(out)) {
      /* a live region has to exist before its content changes or it announces nothing */
      problems.push('the result region is drawn with content already in it, so the score ' +
        'it later carries will not be announced');
    }

    /* the authored index behind each drawn slot, per question */
    const orderOf = [];
    for (let qi = 0; qi < questions.length; qi++) {
      const q = questions[qi];
      const card = cards[qi];
      const opts = card.querySelectorAll('.opt');
      const authored = (q.opts || []).map(asInline);
      if (opts.length !== authored.length) {
        problems.push(`q${qi + 1}: ${opts.length} option button(s) for ${authored.length} option(s)`);
        return { draws, picks, slots, problems };
      }
      /* the options are a group labelled by the question, or a screen reader meets four
         unrelated buttons with nothing saying which question they answer */
      const group = card.querySelector('.opts');
      const labelledBy = group && group.getAttribute('aria-labelledby');
      if (!group || group.getAttribute('role') !== 'group' || !labelledBy) {
        problems.push(`q${qi + 1}: the option buttons are not a labelled group`);
      } else if (!card.querySelector(`#${labelledBy}`)) {
        problems.push(`q${qi + 1}: the option group is labelled by an id that is not on the page`);
      }

      /* the stem reaches the screen drawn, not as its own source */
      const stem = card.querySelector('.qt');
      const src = String(q.q || '');
      if (/```/.test(src) && !stem.querySelector('.qcode')) {
        problems.push(`q${qi + 1}: the stem's fenced block is not drawn as a code block`);
      }
      const stemText = readText(stem);
      if (/\$[^$]+\$/.test(src) && stemText.includes('$')) {
        problems.push(`q${qi + 1}: the stem's mathematics reaches the screen as its own source`);
      }
      if (/`[^`]+`/.test(src) && stemText.includes('`')) {
        problems.push(`q${qi + 1}: the stem's code span reaches the screen as backticks`);
      }

      const shown = opts.map(optText);
      if ([...shown].sort().join(' ') !== [...authored].sort().join(' ')) {
        problems.push(`q${qi + 1}: the drawn options are not a permutation of the authored ones`);
        return { draws, picks, slots, problems };
      }
      /* The authored index each drawn slot carries, which is what the whys lookup uses.
         It cannot be recovered from the text: MathML lives in structure rather than in
         characters, so `I_m/\sqrt{2}` and `I_m/2` flatten to the same string, and six
         questions in the catalogue hold a pair like that. Both are drawn and announced
         correctly in a browser, because <msqrt> is a real element — the flattening is
         this gate's limit, not those questions' defect. */
      const idx = opts.map((o) => +o.getAttribute('data-ai'));
      if (idx.some((n, k) => !Number.isInteger(n) || n < 0 || n >= authored.length ||
                             idx.indexOf(n) !== k)) {
        problems.push(`q${qi + 1}: the drawn options do not carry one authored index each`);
        return { draws, picks, slots, problems };
      }
      /* and the index has to agree with the option it is attached to, or it is a
         permutation that labels nothing. Checked only where the text is unambiguous,
         which is every question but the six above. */
      const mislabelled = idx.findIndex((n, k) =>
        shown[k] !== authored[n] && shown.filter((t) => t === shown[k]).length === 1);
      if (mislabelled >= 0) {
        problems.push(`q${qi + 1}: a drawn option carries the authored index of a different option`);
        return { draws, picks, slots, problems };
      }
      orderOf.push(idx);
      slots.push({ keyAt: idx.indexOf(q.a), of: idx.length });
    }
    /* a unit whose every drawn key is still in the top slot is a unit the shuffle is not
       reaching — the state this whole file exists to detect */
    if (slots.length >= 4 && slots.every((s) => s.keyAt === 0)) {
      problems.push(`every one of its ${slots.length} answers is drawn in the top slot — ` +
        'the shuffle is not reaching this unit');
    }

    /* ---- press each drawn slot in turn, on a fresh mount, and read the answer back ---- */
    const widest = Math.max(...questions.map((q) => (q.opts || []).length));
    for (let r = 0; r < widest; r++) {
      root = mount(lesson); draws++;
      const cs = root.querySelectorAll('.quiz-q');
      let right = 0;
      for (let qi = 0; qi < questions.length; qi++) {
        const q = questions[qi];
        const idx = orderOf[qi];
        const at = Math.min(r, idx.length - 1);
        const authoredAt = idx[at];
        const opts = cs[qi].querySelectorAll('.opt');
        click(opts[at]); picks++;
        if (authoredAt === q.a) right++;

        const ex = cs[qi].querySelector('.explain');
        if (!ex) { problems.push(`q${qi + 1}: pressing an option drew no explanation`); continue; }
        /* cycle 3's fix: the clicked button is disabled and a disabled element cannot
           hold focus, so the explanation has to be able to take it */
        if (ex.getAttribute('tabindex') !== '-1') {
          problems.push(`q${qi + 1}: the explanation cannot take focus, so answering with ` +
            'the keyboard drops it on the document');
        }

        /* the letter a wrong answer is pointed at is the key's DRAWN slot */
        const head = readText(cs[qi].querySelector('.ex-head'));
        const keyAt = idx.indexOf(q.a);
        if (at === keyAt) {
          if (!/^✓/.test(head)) {
            problems.push(`q${qi + 1}: pressing the correct option is not marked right`);
          }
        } else if (!head.includes('ABCDE'[keyAt])) {
          problems.push(`q${qi + 1}: a wrong answer is pointed at "${head.slice(-3)}", but the ` +
            `key is drawn in slot ${'ABCDE'[keyAt]} — the letter is the authored index, not the drawn one`);
        }

        /* THE REMAP. whys are authored against the order in the file; what was pressed
           is a slot in another order. This is the check that proves the indirection. */
        const picked = cs[qi].querySelector('.ex-picked');
        if (q.whys && q.whys.length) {
          if (!picked) {
            problems.push(`q${qi + 1}: the question carries per-option explanations and ` +
              'pressing an option drew none of them');
          } else {
            const got = readText(picked);
            const owed = asProse(q.whys[authoredAt]);
            if (got !== owed) {
              const which = q.whys.findIndex((w) => asProse(w) === got);
              problems.push(`q${qi + 1}: pressing "${String(q.opts[authoredAt]).slice(0, 40)}" ` +
                `is answered with the explanation authored for ` +
                (which < 0 ? 'no option at all' : `a different option`));
            }
          }
        } else if (picked) {
          problems.push(`q${qi + 1}: an explanation slot was drawn for a question with no whys`);
        }

        /* clicking faster than it re-solves: a second press must change nothing */
        const before = String(cs[qi].querySelector('.ex-slot').innerHTML);
        click(opts[(at + 1) % opts.length]);
        if (String(cs[qi].querySelector('.ex-slot').innerHTML) !== before) {
          problems.push(`q${qi + 1}: a second press re-answers a question already answered`);
        }
      }

      /* every question answered, so the score is drawn — and it is the score for the
         options actually pressed */
      const score = root.querySelector('.score');
      if (!score) {
        problems.push(`round ${r}: every question answered and no score was drawn`);
      } else if (readText(score) !== `${right} / ${questions.length}`) {
        problems.push(`round ${r}: the score reads "${readText(score)}" where ` +
          `${right} of ${questions.length} were answered correctly`);
      }
    }

    app.forget(lessonId);
    return { draws, picks, slots, problems };
  }

  /* the high-water mark, checked once rather than per unit: answer everything right,
     then everything wrong, and the recorded best must not fall */
  function bestIsHighWater(lessonId, u) {
    const lesson = lessonOf(lessonId, u);
    app.forget(lessonId);
    let root = mount(lesson);
    let cards = root.querySelectorAll('.quiz-q');
    (u.questions || []).forEach((q, qi) => {
      const opts = cards[qi].querySelectorAll('.opt');
      const idx = opts.map((o) => +o.getAttribute('data-ai'));
      click(opts[idx.indexOf(q.a)]);
    });
    const high = app.best(lessonId);
    root = mount(lesson);
    cards = root.querySelectorAll('.quiz-q');
    (u.questions || []).forEach((q, qi) => {
      const opts = cards[qi].querySelectorAll('.opt');
      const idx = opts.map((o) => +o.getAttribute('data-ai'));
      click(opts[(idx.indexOf(q.a) + 1) % opts.length]);
    });
    const after = app.best(lessonId);
    app.forget(lessonId);
    return { high, after };
  }

  return { drive, bestIsHighWater };
}
