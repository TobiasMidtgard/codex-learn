/* ============ studio: mathematics, checking, sandboxes ============
 *
 * The three things a graduate engineering unit needs that a code lesson does not:
 * mathematics you can read, answers that can be checked as mathematics rather than
 * as strings, and a picture you can push on before any of it is formalised.
 *
 *   MathML     a LaTeX subset rendered to native MathML — no library, no fonts
 *   MathCheck  SymPy-backed equivalence, with diagnostics for the usual mistakes
 *   Sandbox    a canvas + parameter framework for the intuition visualisers
 */

/* ---------------------------------------------------------------- MathML
 *
 * KaTeX is ~1 MB of script and fonts once base64'd into a single-file app that
 * otherwise fetches nothing but Pyodide. MathML Core is native in every browser
 * this app supports, so the whole renderer is a parser and some element names.
 *
 * The subset is deliberate: fractions, scripts, radicals, accents, Greek, the
 * operators an EE curriculum uses, matrices, and \text. Anything outside it is
 * shown as its own source in monospace rather than rendered wrongly — a reader can
 * always see what was written, and it is obvious that it was not understood.
 */
const MathML = (function () {

  const GREEK = {
    alpha: 'α', beta: 'β', gamma: 'γ', delta: 'δ', epsilon: 'ϵ', varepsilon: 'ε',
    zeta: 'ζ', eta: 'η', theta: 'θ', vartheta: 'ϑ', iota: 'ι', kappa: 'κ',
    lambda: 'λ', mu: 'μ', nu: 'ν', xi: 'ξ', pi: 'π', rho: 'ρ', varrho: 'ϱ',
    sigma: 'σ', varsigma: 'ς', tau: 'τ', upsilon: 'υ', phi: 'ϕ', varphi: 'φ',
    chi: 'χ', psi: 'ψ', omega: 'ω',
    Gamma: 'Γ', Delta: 'Δ', Theta: 'Θ', Lambda: 'Λ', Xi: 'Ξ', Pi: 'Π',
    Sigma: 'Σ', Upsilon: 'Υ', Phi: 'Φ', Psi: 'Ψ', Omega: 'Ω',
  };

  const OPS = {
    cdot: '⋅', times: '×', div: '÷', pm: '±', mp: '∓', ast: '∗', star: '⋆',
    leq: '≤', le: '≤', geq: '≥', ge: '≥', neq: '≠', ne: '≠', approx: '≈',
    equiv: '≡', sim: '∼', simeq: '≃', propto: '∝', ll: '≪', gg: '≫',
    to: '→', rightarrow: '→', Rightarrow: '⇒', leftarrow: '←', Leftarrow: '⇐',
    leftrightarrow: '↔', Leftrightarrow: '⇔', mapsto: '↦',
    infty: '∞', partial: '∂', nabla: '∇', forall: '∀', exists: '∃',
    in: '∈', notin: '∉', subset: '⊂', subseteq: '⊆', cup: '∪', cap: '∩',
    angle: '∠', perp: '⊥', parallel: '∥', degree: '°', ldots: '…', dots: '…',
    cdots: '⋯', vdots: '⋮', ddots: '⋱', prime: '′', ell: 'ℓ', hbar: 'ℏ',
    Re: 'ℜ', Im: 'ℑ', circ: '∘', oplus: '⊕', otimes: '⊗', langle: '⟨', rangle: '⟩',
  };

  /* big operators take limits above and below in display mode */
  const BIG = { sum: '∑', prod: '∏', int: '∫', oint: '∮', iint: '∬', lim: 'lim',
                bigcup: '⋃', bigcap: '⋂', max: 'max', min: 'min', sup: 'sup', inf: 'inf' };

  const FUNCS = ['sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'sinh', 'cosh', 'tanh',
    'arcsin', 'arccos', 'arctan', 'log', 'ln', 'exp', 'det', 'dim', 'ker', 'deg',
    'arg', 'gcd', 'mod', 'tr', 'rank', 'diag', 'sgn'];

  const ACCENT = { hat: '^', bar: '‾', vec: '→', dot: '˙', ddot: '¨',
                   tilde: '~', widehat: '^', overline: '‾' };

  const MATRIX_FENCE = {
    bmatrix: ['[', ']'], pmatrix: ['(', ')'], vmatrix: ['|', '|'],
    Bmatrix: ['{', '}'], Vmatrix: '‖‖'.split(''), matrix: ['', ''],
  };

  function esc2(s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  /* ---- tokens ---- */
  function tokenize(src) {
    const out = [];
    let i = 0;
    while (i < src.length) {
      const c = src[i];
      if (/\s/.test(c)) { i++; continue; }
      if (c === '\\') {
        const m = /^\\([A-Za-z]+|.)/.exec(src.slice(i));
        if (!m) { i++; continue; }
        out.push({ t: 'cmd', v: m[1] });
        i += m[0].length;
        continue;
      }
      if (c === '{' || c === '}' || c === '^' || c === '_' || c === '&') {
        out.push({ t: c }); i++; continue;
      }
      const num = /^\d+(?:\.\d+)?/.exec(src.slice(i));
      if (num) { out.push({ t: 'num', v: num[0] }); i += num[0].length; continue; }
      if (/[A-Za-z]/.test(c)) { out.push({ t: 'id', v: c }); i++; continue; }
      out.push({ t: 'op', v: c }); i++;
    }
    return out;
  }

  /* ---- parse to MathML ----
     Returns null the moment it meets something outside the subset, so the caller
     can fall back to showing the source rather than a half-rendered expression. */
  function parse(toks, display) {
    let i = 0;
    let failed = false;

    function fail() { failed = true; return '<mi>?</mi>'; }

    function group() {                       /* a {...} or a single atom */
      if (i < toks.length && toks[i].t === '{') {
        i++;
        const rows = list('}');
        if (toks[i] && toks[i].t === '}') i++; else return fail();
        return '<mrow>' + rows + '</mrow>';
      }
      return atom();
    }

    function scripts(base) {
      let sub = null, sup = null;
      for (;;) {
        if (toks[i] && toks[i].t === '_' && sub === null) { i++; sub = group(); continue; }
        if (toks[i] && toks[i].t === '^' && sup === null) { i++; sup = group(); continue; }
        break;
      }
      if (sub !== null && sup !== null) return '<msubsup>' + base + sub + sup + '</msubsup>';
      if (sub !== null) return '<msub>' + base + sub + '</msub>';
      if (sup !== null) return '<msup>' + base + sup + '</msup>';
      return base;
    }

    function bigOp(name) {
      const glyph = BIG[name];
      const isWord = /^[a-z]{2,}$/.test(glyph);
      const base = isWord ? '<mo movablelimits="true">' + glyph + '</mo>'
                          : '<mo largeop="true">' + glyph + '</mo>';
      let under = null, over = null;
      for (;;) {
        if (toks[i] && toks[i].t === '_' && under === null) { i++; under = group(); continue; }
        if (toks[i] && toks[i].t === '^' && over === null) { i++; over = group(); continue; }
        break;
      }
      /* integrals keep their limits beside the sign; sums and lim stack them */
      const stack = display && name !== 'int' && name !== 'oint' && name !== 'iint';
      if (under !== null && over !== null) {
        return stack ? '<munderover>' + base + under + over + '</munderover>'
                     : '<msubsup>' + base + under + over + '</msubsup>';
      }
      if (under !== null) {
        return stack ? '<munder>' + base + under + '</munder>' : '<msub>' + base + under + '</msub>';
      }
      if (over !== null) {
        return stack ? '<mover>' + base + over + '</mover>' : '<msup>' + base + over + '</msup>';
      }
      return base;
    }

    function matrix(env) {
      const fence = MATRIX_FENCE[env];
      const rows = [];
      let cells = [];
      let cell = '';
      for (;;) {
        if (i >= toks.length) return fail();
        const t = toks[i];
        if (t.t === 'cmd' && t.v === 'end') {
          i++;
          if (toks[i] && toks[i].t === '{') {
            i++;
            let name = '';
            while (toks[i] && toks[i].t !== '}') { name += (toks[i].v || ''); i++; }
            if (toks[i]) i++;
            if (name !== env) return fail();
          }
          break;
        }
        if (t.t === '&') { i++; cells.push(cell); cell = ''; continue; }
        if (t.t === 'cmd' && t.v === '\\') { i++; cells.push(cell); rows.push(cells); cells = []; cell = ''; continue; }
        cell += atomWithScripts();
      }
      cells.push(cell);
      rows.push(cells);
      const body = '<mtable>' + rows.map(function (r) {
        return '<mtr>' + r.map(function (c) { return '<mtd>' + (c || '') + '</mtd>'; }).join('') + '</mtr>';
      }).join('') + '</mtable>';
      if (!fence[0]) return body;
      return '<mrow><mo stretchy="true">' + esc2(fence[0]) + '</mo>' + body +
             '<mo stretchy="true">' + esc2(fence[1]) + '</mo></mrow>';
    }

    function command(name) {
      if (GREEK[name]) return '<mi>' + GREEK[name] + '</mi>';
      if (OPS[name]) return '<mo>' + esc2(OPS[name]) + '</mo>';
      if (BIG[name]) return bigOp(name);
      if (FUNCS.indexOf(name) !== -1) return '<mi mathvariant="normal">' + name + '</mi>';
      if (ACCENT[name]) {
        const a = group();
        return '<mover accent="true">' + a + '<mo>' + esc2(ACCENT[name]) + '</mo></mover>';
      }
      switch (name) {
        case 'frac': case 'dfrac': case 'tfrac': {
          const a = group(), b = group();
          return '<mfrac>' + a + b + '</mfrac>';
        }
        case 'sqrt': {
          if (toks[i] && toks[i].t === 'op' && toks[i].v === '[') {
            i++;
            let idx = '';
            while (toks[i] && !(toks[i].t === 'op' && toks[i].v === ']')) idx += atomWithScripts();
            if (toks[i]) i++;
            return '<mroot>' + group() + '<mrow>' + idx + '</mrow></mroot>';
          }
          return '<msqrt>' + group() + '</msqrt>';
        }
        case 'text': case 'mathrm': case 'mathbf': case 'mathit': case 'mathsf': case 'operatorname': {
          if (!toks[i] || toks[i].t !== '{') return fail();
          i++;
          let txt = '';
          let depth = 1;
          while (i < toks.length) {
            const t = toks[i];
            if (t.t === '{') depth++;
            if (t.t === '}') { depth--; if (!depth) break; }
            txt += (t.v !== undefined ? t.v : (t.t === '^' || t.t === '_' ? t.t : ' '));
            i++;
          }
          if (toks[i]) i++;
          const variant = name === 'mathbf' ? ' mathvariant="bold"'
            : name === 'mathit' ? ' mathvariant="italic"'
            : name === 'mathsf' ? ' mathvariant="sans-serif"' : '';
          if (name === 'text') return '<mtext>' + esc2(txt) + '</mtext>';
          return '<mi mathvariant="normal"' + variant.replace(' mathvariant="normal"', '') + '>' + esc2(txt) + '</mi>';
        }
        case 'left': case 'right': {
          const t = toks[i];
          if (!t) return fail();
          i++;
          const ch = t.v === '.' ? '' : (t.v || '');
          return ch ? '<mo stretchy="true">' + esc2(ch) + '</mo>' : '';
        }
        case 'begin': {
          if (!toks[i] || toks[i].t !== '{') return fail();
          i++;
          let env = '';
          while (toks[i] && toks[i].t !== '}') { env += (toks[i].v || ''); i++; }
          if (toks[i]) i++;
          if (!MATRIX_FENCE[env]) return fail();
          return matrix(env);
        }
        case 'quad': return '<mspace width="1em"/>';
        case 'qquad': return '<mspace width="2em"/>';
        case ',': return '<mspace width="0.17em"/>';
        case ';': return '<mspace width="0.28em"/>';
        case '!': return '<mspace width="-0.17em"/>';
        case '\\': return '';
        default: return fail();
      }
    }

    function atom() {
      const t = toks[i];
      if (!t) return '';
      if (t.t === 'num') { i++; return '<mn>' + t.v + '</mn>'; }
      if (t.t === 'id') { i++; return '<mi>' + t.v + '</mi>'; }
      if (t.t === 'op') {
        i++;
        if (t.v === '(' || t.v === ')' || t.v === '[' || t.v === ']' || t.v === '|') {
          return '<mo stretchy="false">' + esc2(t.v) + '</mo>';
        }
        return '<mo>' + esc2(t.v) + '</mo>';
      }
      if (t.t === 'cmd') { i++; return command(t.v); }
      if (t.t === '{') return group();
      return fail();
    }

    function atomWithScripts() { return scripts(atom()); }

    function list(stop) {
      let out = '';
      while (i < toks.length && !failed) {
        if (stop && toks[i].t === stop) break;
        if (toks[i].t === '}' && !stop) break;
        out += atomWithScripts();
      }
      return out;
    }

    const body = list(null);
    return failed ? null : body;
  }

  function render(latex, display) {
    const src = String(latex == null ? '' : latex);
    let body = null;
    try { body = parse(tokenize(src), !!display); } catch (e) { body = null; }
    if (body === null) {
      return '<code class="math-raw" title="Outside the supported LaTeX subset">' + esc2(src) + '</code>';
    }
    return '<math xmlns="http://www.w3.org/1998/Math/MathML"' +
      (display ? ' display="block"' : '') + '>' + body + '</math>';
  }

  /* $…$ inline and $$…$$ display, leaving \$ alone */
  function inText(text) {
    return String(text).replace(/(^|[^\\])\$\$([\s\S]+?)\$\$/g, function (m, pre, body) {
      return pre + render(body, true);
    }).replace(/(^|[^\\])\$([^$\n]+?)\$/g, function (m, pre, body) {
      return pre + render(body, false);
    }).replace(/\\\$/g, '$');
  }

  return { render: render, inText: inText };
})();

/* ---------------------------------------------------------------- MathCheck
 *
 * An answer to "what is the transfer function" is not a string, and grading it as
 * one teaches the learner to match the book's algebra rather than to do their own.
 * SymPy decides equivalence, so 1/(1+sRC) and (1/RC)/(s+1/RC) both pass.
 *
 * The diagnostics matter more than the verdict. When an answer is wrong the checker
 * asks *how* it is wrong — by testing the usual transformations against it — so the
 * learner is told "you have the reciprocal" or "that is in Hz, the question asked
 * for rad/s" rather than being shown the answer and learning nothing.
 */
const MathCheck = (function () {

  /* LaTeX the learner typed -> something SymPy can parse. Deliberately small: the
     same subset MathML renders, so anything that displays can also be checked. */
  /* Python keywords that are also perfectly ordinary symbol names in engineering */
  const PY_RESERVED = ['lambda', 'is', 'in', 'not', 'or', 'and', 'if', 'else', 'for',
    'while', 'class', 'def', 'from', 'import', 'as', 'return', 'None', 'True',
    'False', 'del', 'pass', 'global', 'assert', 'raise', 'with', 'yield'];

  const GREEK_NAMES = ['alpha','beta','gamma','delta','epsilon','zeta','eta','theta',
    'iota','kappa','lambda','mu','nu','xi','rho','sigma','tau','upsilon','phi','chi',
    'psi','omega','Gamma','Delta','Theta','Lambda','Xi','Pi','Sigma','Phi','Psi','Omega'];

  /* returned instead of a mangled expression when the LaTeX is outside the subset */
  const UNSUPPORTED = '\u0000unsupported';

  function latexToPy(src, vars) {
    let t = String(src == null ? '' : src);

    /* Scripts first. \sqrt{1-\zeta^{2}} has braces inside its argument, and a
       {…} pattern that cannot nest would miss the whole root and silently drop it —
       which reads to the learner as "your correct answer is wrong". Collapsing
       scripts to brace-free forms first means the later passes only ever meet the
       nesting they can actually handle. */
    for (let g = 0; g < 8; g++) {
      const next = t.replace(/_\s*\{([^{}]*)\}/g, function (m, x) {
        return '_' + x.replace(/\\[A-Za-z]+|[^A-Za-z0-9]/g, '');
      });
      if (next === t) break;
      t = next;
    }
    for (let g = 0; g < 8; g++) {
      const next = t.replace(/\^\s*\{([^{}]*)\}/g, '**($1)');
      if (next === t) break;
      t = next;
    }

    /* The argument-taking commands, to a fixpoint — as one group, not one after
       another. Each pattern is brace-free by necessity, so \frac{a}{\sqrt{b}} cannot
       match until the radical inside it has been resolved. Running the passes
       sequentially left that fraction unresolved, and the catch-all below then
       stripped the command and its braces, turning a division into an implicit
       multiplication: \frac{\sqrt{a}}{b} came out as sqrt(a)*b. A wrong answer that
       looks like a right one is the worst possible failure here, so the loop repeats
       until nothing changes and anything still unresolved is reported instead. */
    for (let pass = 0; pass < 24; pass++) {
      const before = t;
      t = t.replace(/\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}/g, ' (($1)/($2)) ');
      t = t.replace(/\\sqrt\s*\[([^\]]*)\]\s*\{([^{}]*)\}/g, ' (($2)**(1/($1))) ');
      t = t.replace(/\\sqrt\s*\{([^{}]*)\}/g, ' sqrt($1) ');
      t = t.replace(/\\(?:mathrm|mathbf|mathit|text|operatorname)\s*\{([^{}]*)\}/g, ' $1 ');
      if (t === before) break;
    }
    /* Anything left is nesting the subset does not cover. Fail loudly. */
    if (/\\(?:[dt]?frac|sqrt|mathrm|mathbf|mathit|text|operatorname)\b/.test(t)) {
      return UNSUPPORTED;
    }

    t = t.replace(/\\left|\\right/g, ' ');
    t = t.replace(/\\cdot|\\times/g, ' * ');
    t = t.replace(/\\div/g, ' / ');
    t = t.replace(/\\infty/g, ' oo ');
    t = t.replace(/\\pi\b/g, ' pi ');
    GREEK_NAMES.forEach(function (g) {
      t = t.replace(new RegExp('\\\\' + g + '(?![A-Za-z])', 'g'), ' ' + g);
    });
    t = t.replace(/_\s*([A-Za-z0-9])/g, '_$1');
    t = t.replace(/\^/g, '**');
    t = t.replace(/\\,|\\;|\\!|\\quad|\\qquad/g, ' ');
    t = t.replace(/\\[A-Za-z]+/g, ' ');            /* anything left is unsupported */
    t = t.replace(/\{|\}/g, ' ');
    return explicitMul(t.trim(), vars);
  }

  /* Implicit multiplication binds tighter than division.
     Written mathematics reads 1/RC as 1/(RC); Python reads it as (1/R)*C. Handing
     the raw text to SymPy therefore marks a correct answer wrong — and it is the
     first thing anyone types for a first-order pole. So the products are made
     explicit here, and a run of them after a division is bracketed as one
     denominator. Symbol names the lesson declares are matched whole, so V_out stays
     one symbol while RC becomes R*C. */
  const KEEP_WHOLE = ['sqrt', 'exp', 'log', 'ln', 'sin', 'cos', 'tan', 'sinh', 'cosh',
    'tanh', 'asin', 'acos', 'atan', 'atan2', 'abs', 'Abs', 're', 'im', 'conjugate',
    'pi', 'oo', 'I', 'E']
    /* A name that arrived as \sigma is one symbol whether or not the lesson
       remembered to declare it. Splitting it into s*i*g*m*a is never what was
       meant, and the failure looks like a broken answer rather than a missing
       declaration. */
    .concat(GREEK_NAMES);

  function explicitMul(text, vars) {
    const names = (vars || []).filter(Boolean).concat(KEEP_WHOLE)
      .sort(function (a, b) { return b.length - a.length; });
    const toks = [];
    let i = 0;
    while (i < text.length) {
      const c = text[i];
      if (/\s/.test(c)) { i++; continue; }
      if (/[0-9]/.test(c)) {
        const m = /^\d+(?:\.\d+)?/.exec(text.slice(i));
        toks.push({ t: 'val', v: m[0] });
        i += m[0].length;
        continue;
      }
      if (/[A-Za-z_]/.test(c)) {
        let name = null;
        for (const n of names) {
          if (text.startsWith(n, i) && !/[A-Za-z0-9_]/.test(text[i + n.length] || '')) { name = n; break; }
        }
        if (!name) {
          const guess = /^[A-Za-z](?:_[A-Za-z0-9]+)?/.exec(text.slice(i));
          if (!guess) { i++; continue; }        /* a stray underscore, not a symbol */
          name = guess[0];
        }
        const rest = text.slice(i + name.length);
        const isFn = KEEP_WHOLE.indexOf(name) !== -1 && /^\s*\(/.test(rest);
        /* `lambda` is the obvious name for an eigenvalue and a Python keyword. Rename
           it here, once the whole name is known — doing it earlier, on the raw text,
           left `lambda_` in place of a name the matcher knew, so it fell through to
           the single-letter path and \lambda became l*a*m*b*d*a. Both sides of a
           comparison get the same rewrite, so equivalence is unaffected. */
        const safe = PY_RESERVED.indexOf(name) === -1 ? name : name + '_';
        toks.push({ t: isFn ? 'fn' : 'val', v: safe });
        i += name.length;
        continue;
      }
      if (text.startsWith('**', i)) { toks.push({ t: 'op', v: '**' }); i += 2; continue; }
      toks.push({ t: 'op', v: c });
      i++;
    }

    /* insert the multiplications the writer left out */
    const out = [];
    for (let k = 0; k < toks.length; k++) {
      const prev = out[out.length - 1];
      const cur = toks[k];
      const opens = cur.t === 'fn' || cur.t === 'val' || (cur.t === 'op' && cur.v === '(');
      const closes = prev && (prev.t === 'val' || (prev.t === 'op' && prev.v === ')'));
      if (prev && closes && opens) out.push({ t: 'op', v: '*', implicit: true });
      out.push(cur);
    }

    /* bracket an implicit product that follows a division */
    const res = [];
    for (let k = 0; k < out.length; k++) {
      res.push(out[k]);
      if (!(out[k].t === 'op' && out[k].v === '/')) continue;
      let j = k + 1, depth = 0, factors = 0, seen = [];
      while (j < out.length) {
        const t = out[j];
        if (t.t === 'op' && (t.v === '(' )) { depth++; seen.push(t); j++; continue; }
        if (t.t === 'op' && t.v === ')') {
          if (!depth) break;
          depth--; seen.push(t); j++; continue;
        }
        if (depth) { seen.push(t); j++; continue; }
        if (t.t === 'val' || t.t === 'fn') { factors++; seen.push(t); j++; continue; }
        if (t.t === 'op' && t.v === '*' && t.implicit) { seen.push(t); j++; continue; }
        if (t.t === 'op' && t.v === '**') {
          seen.push(t); j++;
          if (out[j]) { seen.push(out[j]); j++; }
          continue;
        }
        break;
      }
      if (factors > 1) {
        res.push({ t: 'op', v: '(' });
        seen.forEach(function (t) { res.push(t); });
        res.push({ t: 'op', v: ')' });
        k = j - 1;
      }
    }

    return res.map(function (t) { return t.v; }).join(' ');
  }

  function pyStr(s) { return JSON.stringify(String(s)); }

  /* One Python program: parse both sides, decide equivalence, and if it fails, work
     out which familiar mistake it is. Printed as JSON on the last line. */
  function program(studentPy, expectedPy, vars, mode, tol) {
    return [
      'import json',
      'import sympy as sp',
      'from sympy.parsing.sympy_parser import (parse_expr, standard_transformations,',
      '    implicit_multiplication_application, convert_xor, split_symbols)',
      '',
      '_names = ' + JSON.stringify((vars || []).map(function (v) {
        return PY_RESERVED.indexOf(v) === -1 ? v : v + '_';
      })),
      '_local = {n: sp.Symbol(n) for n in _names}',
      '_T = standard_transformations + (convert_xor, split_symbols, implicit_multiplication_application)',
      '',
      'def _p(text):',
      '    return parse_expr(text, local_dict=dict(_local), transformations=_T, evaluate=True)',
      '',
      '_res = {"ok": False, "kind": "wrong", "detail": ""}',
      'try:',
      '    _exp = _p(' + pyStr(expectedPy) + ')',
      'except Exception as e:',
      '    print(json.dumps({"ok": False, "kind": "internal", "detail": str(e)})); raise SystemExit',
      'try:',
      '    _got = _p(' + pyStr(studentPy) + ')',
      'except Exception as e:',
      '    print(json.dumps({"ok": False, "kind": "unparsed", "detail": str(e)})); raise SystemExit',
      '',
      'def _same(a, b):',
      '    # a relation cannot be subtracted; compare it as a relation',
      '    if isinstance(a, sp.core.relational.Relational) or isinstance(b, sp.core.relational.Relational):',
      '        if not (isinstance(a, sp.core.relational.Relational) and isinstance(b, sp.core.relational.Relational)):',
      '            return False',
      '        try:',
      '            return bool(sp.simplify(a) == sp.simplify(b))',
      '        except Exception:',
      '            return False',
      '    try:',
      '        d = sp.simplify(sp.together(a - b))',
      '        if d == 0:',
      '            return True',
      '    except Exception:',
      '        pass',
      '    try:',
      '        r = sp.simplify(sp.cancel(a / b))',
      '        if r == 1:',
      '            return True',
      '    except Exception:',
      '        pass',
      '    if not a.free_symbols and not b.free_symbols:',
      '        try:',
      '            return bool(abs(complex(a) - complex(b)) <= ' + (tol || 1e-6) + ')',
      '        except Exception:',
      '            return False',
      '    return False',
      '',
      'if _same(_got, _exp):',
      '    _res = {"ok": True, "kind": "exact", "detail": ""}',
      'elif isinstance(_got, sp.core.relational.Relational) or isinstance(_exp, sp.core.relational.Relational):',
      '    # A relation cannot be negated, inverted or scaled the way the probes below',
      '    # assume, and running them on one throws rather than diagnosing anything.',
      '    if not isinstance(_got, sp.core.relational.Relational):',
      '        _res = {"ok": False, "kind": "notrelation",',
      '                "detail": "This step wants a condition (something with <, > or =), not a plain expression."}',
      '    else:',
      '        _flip = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}',
      '        _same_sides = False',
      '        try:',
      '            _same_sides = sp.simplify(_got.lhs - _got.rhs - (_exp.lhs - _exp.rhs)) == 0',
      '        except Exception:',
      '            _same_sides = False',
      '        if _same_sides and _flip.get(_got.rel_op) == _exp.rel_op:',
      '            _res = {"ok": False, "kind": "direction",',
      '                    "detail": "Right quantity, wrong direction \u2014 the inequality points the other way."}',
      '        else:',
      '            _res = {"ok": False, "kind": "wrong",',
      '                    "detail": "That condition is not the one being asked for."}',
      'else:',
      '    _pi = sp.pi',
      '    _probes = [',
      '        ("sign",       -_got,            "Check the sign \u2014 every term is negated."),',
      '        ("reciprocal", 1/_got,           "That is the reciprocal of what was asked for."),',
      '        ("radians",    _got/(2*_pi),     "Those are radians per second; the question asked in Hz. Divide by 2\u03c0."),',
      '        ("hertz",      _got*2*_pi,       "Those are hertz; the question asked in rad/s. Multiply by 2\u03c0."),',
      '        ("half",       _got/2,           "You are a factor of two high."),',
      '        ("double",     _got*2,           "You are a factor of two low."),',
      '        ("squared",    _got**2,          "Compare the power and amplitude forms \u2014 one of them is squared."),',
      '        ("rooted",     sp.sqrt(_got),    "Compare the power and amplitude forms \u2014 one of them needs a square root."),',
      '    ]',
      '    for _name, _alt, _msg in _probes:',
      '        try:',
      '            if _same(_alt, _exp):',
      '                _res = {"ok": False, "kind": _name, "detail": _msg}',
      '                break',
      '        except Exception:',
      '            continue',
      '    else:',
      '        try:',
      '            _missing = sorted(str(x) for x in (_exp.free_symbols - _got.free_symbols))',
      '            _extra = sorted(str(x) for x in (_got.free_symbols - _exp.free_symbols))',
      '        except Exception:',
      '            _missing, _extra = [], []',
      '        if _missing:',
      '            _res = {"ok": False, "kind": "missing",',
      '                    "detail": "Nothing in your answer depends on " + ", ".join(_missing) + ", and it should."}',
      '        elif _extra:',
      '            _res = {"ok": False, "kind": "extra",',
      '                    "detail": "Your answer depends on " + ", ".join(_extra) + ", which should have cancelled."}',
      '',
      'print(json.dumps(_res))',
      '',
    ].join('\n');
  }

  let warmed = null;
  /* SymPy is a large download. Pull it while the learner is still reading, never
     when they press Check. */
  function warm() {
    if (warmed) return warmed;
    warmed = PyRunner.run({
      files: [{ name: 'main.py', content: 'import sympy\nprint("ready")\n' }],
      main: 'main.py', tests: [], onConsole: function () {},
    }).catch(function () { warmed = null; });
    return warmed;
  }

  async function check(studentLatex, expectedLatex, opts) {
    opts = opts || {};
    const student = latexToPy(studentLatex, opts.vars);
    const expected = latexToPy(expectedLatex, opts.vars);
    if (!student) return { ok: false, kind: 'empty', message: 'Nothing to check yet.' };
    if (expected === UNSUPPORTED) {
      return { ok: false, kind: 'internal',
               message: 'This step\u2019s reference answer uses LaTeX nesting the checker does not support. ' +
                        'That is a fault in the lesson, not in your answer.' };
    }
    if (student === UNSUPPORTED) {
      return { ok: false, kind: 'unparsed',
               message: 'That nesting is outside the supported LaTeX subset. Try writing it flatter \u2014 ' +
                        'for example a\u2044b as \\frac{a}{b} with simple contents on each side.' };
    }

    let out = '';
    try {
      await PyRunner.run({
        files: [{ name: 'main.py', content: program(student, expected, opts.vars, opts.mode, opts.tol) }],
        main: 'main.py', tests: [],
        onConsole: function (lvl, txt) { if (lvl === 'log') out += txt; },
      });
    } catch (e) {
      return { ok: false, kind: 'offline', message: 'The maths engine could not start: ' + String((e && e.message) || e) };
    }

    const line = String(out).trim().split('\n').filter(Boolean).pop() || '';
    let res;
    try { res = JSON.parse(line); }
    catch (e) { return { ok: false, kind: 'internal', message: 'The checker did not answer. ' + line.slice(0, 120) }; }

    if (res.ok) return { ok: true, kind: 'exact', message: 'Equivalent \u2014 that is the same expression.' };
    if (res.kind === 'unparsed') {
      return { ok: false, kind: 'unparsed',
               message: 'That did not parse as an expression. Check brackets and \\frac{}{} pairs.' };
    }
    if (res.detail) return { ok: false, kind: res.kind, message: res.detail };
    return { ok: false, kind: 'wrong', message: 'Not equivalent to the expected expression.' };
  }

  return { check: check, warm: warm, latexToPy: latexToPy };
})();

/* ---------------------------------------------------------------- Sandbox
 *
 * The intuition step: move a parameter, watch the consequence, before any algebra.
 * A visualiser declares its parameters and how to draw itself; the framework owns
 * the canvas, the device-pixel scaling, the sliders and the teardown.
 *
 * Nothing here animates on a timer. Redrawing happens when a value changes, which
 * means there is no loop to leak — and the one case that does want motion
 * (a travelling wave) asks for it explicitly and is stopped by dispose().
 */
const Sandbox = (function () {
  const REG = {};

  function define(spec) { REG[spec.id] = spec; return spec; }
  function get(id) { return REG[id] || null; }

  /* ---- drawing helpers shared by every visualiser ---- */
  function palette() {
    const cs = getComputedStyle(document.documentElement);
    const v = function (n, fallback) { return (cs.getPropertyValue(n) || '').trim() || fallback; };
    /* These colours land on --editor, which is dark in both themes, so every one of them
       comes from an on-editor token rather than the page's. The accents used to be the
       exception — --lime/--blue/--purple/--amber are re-tinted dark for a light ground
       by the light theme, and were then painted on a surface that had stayed dark, which
       put purple at 2.96:1 and under the 3:1 floor. */
    return {
      ink: v('--on-editor', '#EDEFF3'),
      dim: v('--on-editor-3', '#565C68'),
      faint: v('--on-editor-4', '#3A3F49'),
      line: v('--on-editor-line', 'rgba(255,255,255,.1)'),
      accent: v('--on-editor-lime', '#C7F751'),
      blue: v('--on-editor-blue', '#6E9BFF'),
      purple: v('--on-editor-purple', '#A78BFA'),
      amber: v('--on-editor-amber', '#FFC66D'),
      surface: v('--editor', '#0A0B0E'),
    };
  }

  /* A plotting frame with margins, axes and a value->pixel mapping. */
  function frame(ctx, w, h, opts) {
    opts = opts || {};
    const P = palette();
    const m = Object.assign({ l: 46, r: 14, t: 14, b: 30 }, opts.margin || {});
    const x0 = m.l, y0 = m.t, x1 = w - m.r, y1 = h - m.b;
    const xr = opts.xRange || [0, 1];
    const yr = opts.yRange || [0, 1];
    const logX = !!opts.logX;

    function fx(v) {
      if (logX) {
        const a = Math.log10(Math.max(xr[0], 1e-12)), b = Math.log10(Math.max(xr[1], 1e-12));
        return x0 + (Math.log10(Math.max(v, 1e-12)) - a) / (b - a) * (x1 - x0);
      }
      return x0 + (v - xr[0]) / (xr[1] - xr[0]) * (x1 - x0);
    }
    function fy(v) { return y1 - (v - yr[0]) / (yr[1] - yr[0]) * (y1 - y0); }

    ctx.clearRect(0, 0, w, h);

    /* grid */
    ctx.strokeStyle = P.line;
    ctx.lineWidth = 1;
    ctx.font = '10px ui-monospace, monospace';
    ctx.fillStyle = P.faint;
    const xt = opts.xTicks || 5, yt = opts.yTicks || 4;
    for (let i = 0; i <= xt; i++) {
      const v = logX
        ? Math.pow(10, Math.log10(xr[0]) + i / xt * (Math.log10(xr[1]) - Math.log10(xr[0])))
        : xr[0] + i / xt * (xr[1] - xr[0]);
      const X = Math.round(fx(v)) + 0.5;
      ctx.beginPath(); ctx.moveTo(X, y0); ctx.lineTo(X, y1); ctx.stroke();
      const lab = opts.xLabel ? opts.xLabel(v) : fmt(v);
      ctx.textAlign = 'center'; ctx.textBaseline = 'top';
      ctx.fillText(lab, X, y1 + 6);
    }
    for (let i = 0; i <= yt; i++) {
      const v = yr[0] + i / yt * (yr[1] - yr[0]);
      const Y = Math.round(fy(v)) + 0.5;
      ctx.beginPath(); ctx.moveTo(x0, Y); ctx.lineTo(x1, Y); ctx.stroke();
      const lab = opts.yLabel ? opts.yLabel(v) : fmt(v);
      ctx.textAlign = 'right'; ctx.textBaseline = 'middle';
      ctx.fillText(lab, x0 - 7, Y);
    }
    /* axes */
    ctx.strokeStyle = P.dim;
    ctx.beginPath();
    ctx.moveTo(x0 + 0.5, y0); ctx.lineTo(x0 + 0.5, y1); ctx.lineTo(x1, y1 + 0.5);
    ctx.stroke();

    return {
      P: P, x0: x0, y0: y0, x1: x1, y1: y1, fx: fx, fy: fy,
      line: function (pts, colour, width) {
        ctx.beginPath();
        pts.forEach(function (pt, i) {
          const X = fx(pt[0]), Y = fy(pt[1]);
          if (!isFinite(X) || !isFinite(Y)) return;
          if (i === 0) ctx.moveTo(X, Y); else ctx.lineTo(X, Y);
        });
        ctx.strokeStyle = colour || P.accent;
        ctx.lineWidth = width || 2;
        ctx.lineJoin = 'round';
        ctx.stroke();
      },
      dot: function (x, y, colour, r) {
        ctx.beginPath();
        ctx.arc(fx(x), fy(y), r || 4, 0, Math.PI * 2);
        ctx.fillStyle = colour || P.accent;
        ctx.fill();
      },
      hline: function (y, colour, dash) {
        ctx.save();
        if (dash) ctx.setLineDash(dash);
        ctx.beginPath();
        ctx.moveTo(x0, Math.round(fy(y)) + 0.5);
        ctx.lineTo(x1, Math.round(fy(y)) + 0.5);
        ctx.strokeStyle = colour || P.dim;
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.restore();
      },
      /* The mirror of hline. Added for the tune plots, where half the targets are on
         the frequency axis rather than the response one: EE111 M6 asks for a resonance
         at 1 kHz and the only way to draw that was a horizontal line at y = 1000 on an
         axis running 0 to 2.4, which is off the canvas entirely. */
      vline: function (x, colour, dash) {
        ctx.save();
        if (dash) ctx.setLineDash(dash);
        ctx.beginPath();
        ctx.moveTo(Math.round(fx(x)) + 0.5, y0);
        ctx.lineTo(Math.round(fx(x)) + 0.5, y1);
        ctx.strokeStyle = colour || P.dim;
        ctx.lineWidth = 1;
        ctx.stroke();
        ctx.restore();
      },
      text: function (str, x, y, colour, align) {
        ctx.font = '11px ui-monospace, monospace';
        ctx.fillStyle = colour || P.dim;
        ctx.textAlign = align || 'left';
        ctx.textBaseline = 'alphabetic';
        ctx.fillText(str, x, y);
      },
    };
  }

  function fmt(v) {
    if (v === 0) return '0';
    const a = Math.abs(v);
    if (a >= 1000 || a < 0.01) return v.toExponential(0).replace('e+', 'e');
    if (a >= 100) return v.toFixed(0);
    if (a >= 10) return v.toFixed(1);
    return v.toFixed(2);
  }

  function clamp(v, lo, hi) { return v < lo ? lo : (v > hi ? hi : v); }
  function esc1(s) {
    return String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  /* A parameter is linear by default: the range input carries the value itself. A
     parameter marked `log` carries a tick index instead and the value is exponentiated
     back from it, because a linear slider cannot express a quantity that spans decades.
     The 1/f corner ran 1 Hz to 100 kHz in steps of 100, so every corner below 101 Hz —
     the entire region a chopper amplifier exists for — was a single notch, and two
     lessons opened on values (100 Hz, 20 kHz) the slider could not return to. */
  const LOG_TICKS = 1000;
  function toTick(p, v) {
    if (!p.log) return v;
    const a = Math.log(p.min), b = Math.log(p.max);
    return Math.round((Math.log(clamp(v, p.min, p.max)) - a) / (b - a) * LOG_TICKS);
  }
  function fromTick(p, t) {
    if (!p.log) return t;
    const a = Math.log(p.min), b = Math.log(p.max);
    const v = Math.exp(a + clamp(t, 0, LOG_TICKS) / LOG_TICKS * (b - a));
    /* three significant figures: a corner reading 9973 Hz is noise pretending to be
       precision, and it makes the readouts beside it impossible to compare */
    const mag = Math.pow(10, Math.floor(Math.log10(v)) - 2);
    return clamp(Math.round(v / mag) * mag, p.min, p.max);
  }

  /* ---- mount ----
     Returns a handle with dispose(); the caller must put that in `teardown`,
     because go() clears exactly one slot and nothing drains teardownFns. */
  function mount(host, spec, initial, onChange) {
    const values = Object.assign({}, initial || {});
    spec.params.forEach(function (p) {
      /* A catalog `initial` is author-written, and build.mjs checks only that the key
         names a real parameter. An out-of-range or non-numeric one left the input
         clamped to its own limit while the draw, the readout and the explain all still
         used the original: the thumb, the number beside the label and the picture
         disagreed with each other, and nothing anywhere said so. */
      const given = values[p.k];
      values[p.k] = (typeof given === 'number' && isFinite(given))
        ? clamp(given, p.min, p.max)
        : p.def;
    });

    host.innerHTML =
      '<div class="sbx">' +
        '<div class="sbx-canvas">' +
          '<canvas role="img" aria-label="' + esc1(spec.title || 'visualiser') +
            '. The reading below the sliders describes what it shows."></canvas>' +
        '</div>' +
        '<div class="sbx-side">' +
          '<div class="sbx-params">' +
            spec.params.map(function (p) {
              return '<label class="sbx-p" data-k="' + p.k + '">' +
                '<span class="sbx-l">' + (p.label || p.k) + '</span>' +
                /* hidden from the accessibility tree because the <label> wraps the input:
                   left visible it lands in the input's accessible *name*, so the name
                   changed on every drag and aria-valuetext below could never be heard */
                '<span class="sbx-v" data-v="' + p.k + '" aria-hidden="true"></span>' +
                '<input type="range" min="' + (p.log ? 0 : p.min) + '" ' +
                  'max="' + (p.log ? LOG_TICKS : p.max) + '" ' +
                  'step="' + (p.log ? 1 : (p.step || (p.max - p.min) / 100)) + '" ' +
                  'value="' + toTick(p, values[p.k]) + '">' +
              '</label>';
            }).join('') +
          '</div>' +
          /* the explain line is the whole point of a sandbox — the sentence that says
             what the picture now means. Without a live region it changed in silence for
             anyone not looking at it. */
          '<div class="sbx-read" data-read aria-live="polite"></div>' +
        '</div>' +
      '</div>';

    const cv = host.querySelector('canvas');
    const ctx = cv.getContext('2d');
    const readout = host.querySelector('[data-read]');
    let raf = 0, ro = null, disposed = false, lastExplain = null;

    /* Resolved once. paint() runs on every frame of a drag, and looking these up by
       selector each time put two DOM queries per parameter on the hot path. */
    const els = {};
    spec.params.forEach(function (p) {
      els[p.k] = {
        v: host.querySelector('[data-v="' + p.k + '"]'),
        input: host.querySelector('.sbx-p[data-k="' + p.k + '"] input'),
      };
    });

    function paint() {
      if (disposed) return;
      const box = cv.parentElement.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = Math.max(240, Math.round(box.width));
      const h = Math.max(160, Math.round(box.height));
      if (cv.width !== w * dpr || cv.height !== h * dpr) {
        cv.width = w * dpr; cv.height = h * dpr;
        cv.style.width = w + 'px'; cv.style.height = h + 'px';
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      try { spec.draw(ctx, w, h, values, { frame: frame, palette: palette, fmt: fmt }); }
      catch (e) {
        ctx.clearRect(0, 0, w, h);
        ctx.fillStyle = palette().dim;
        ctx.font = '12px ui-monospace, monospace';
        ctx.fillText('This visualiser failed: ' + String(e && e.message || e).slice(0, 60), 14, 24);
      }
      spec.params.forEach(function (p) {
        const shown = (p.fmt ? p.fmt(values[p.k]) : fmt(values[p.k])) + (p.unit ? ' ' + p.unit : '');
        const el = els[p.k];
        if (el.v) el.v.textContent = shown;
        /* A range input reports its own raw number, which for half of these parameters
           is not what the page shows: "1" where the label reads "direct", "0" where it
           reads "no", a tick index where it reads 20 kHz. */
        if (el.input) el.input.setAttribute('aria-valuetext', (p.label || p.k) + ' ' + shown);
      });
      if (readout && spec.explain) {
        /* Only touch the DOM when the sentence actually changed. It is a polite live
           region and a drag fires this on every frame; rewriting identical HTML sixty
           times a second gives the screen reader sixty things to consider saying. */
        let html = '';
        try { html = spec.explain(values, MathML); } catch (e) { html = ''; }
        if (html !== lastExplain) { readout.innerHTML = html; lastExplain = html; }
      }
      if (onChange) onChange(values);
    }

    function schedule() {
      if (raf || disposed) return;
      raf = requestAnimationFrame(function () { raf = 0; paint(); });
    }

    const byKey = {};
    spec.params.forEach(function (p) { byKey[p.k] = p; });
    host.querySelectorAll('input[type=range]').forEach(function (inp) {
      const k = inp.closest('.sbx-p').dataset.k;
      inp.addEventListener('input', function () {
        const raw = parseFloat(inp.value);
        values[k] = isFinite(raw) ? fromTick(byKey[k], raw) : byKey[k].def;
        schedule();
      });
    });

    if (typeof ResizeObserver !== 'undefined') {
      ro = new ResizeObserver(schedule);
      ro.observe(cv.parentElement);
    } else {
      window.addEventListener('resize', schedule);
    }

    paint();

    return {
      values: values,
      repaint: schedule,
      dispose: function () {
        disposed = true;
        if (raf) cancelAnimationFrame(raf);
        if (ro) ro.disconnect(); else window.removeEventListener('resize', schedule);
        host.innerHTML = '';
      },
    };
  }

  return { define: define, get: get, mount: mount, frame: frame, palette: palette, fmt: fmt,
           all: REG, toTick: toTick, fromTick: fromTick };
})();

/* ---------------------------------------------------------------- visualisers
 *
 * Each one is the thing the PRD calls an intuition sandbox: a parameter you can
 * move and a consequence you can watch, before any equation is introduced. They
 * compute honestly — the step response is an actual second-order solution, the
 * Bode plot an actual frequency sweep — so what the learner sees is what the
 * mathematics they are about to derive really says.
 */

/* poles ↔ step response: the single most useful picture in control */
/* ---------------------------------------------------------------- tune
 *
 * A sandbox is for looking. This is for hitting a target: the learner moves the same
 * kind of sliders, but the model reports named quantities and the exercise states
 * constraints those quantities must satisfy — all of them, at once.
 *
 * The constraints live in the catalog and the physics lives here, which is the same
 * split the circuit builds use: content says what must be true, code says what is.
 */
/* A constraint states its target either as an equality with a tolerance or as a bound
   at one or both ends. To everything downstream those are the same thing — an interval
   the quantity has to land in, with either end possibly open — so the interval is
   computed once, here, and the grading, the drawing and the gates all read it.

   They did not agree before. renderTune tested the bounds before the equality and
   verify_tune.mjs tested the equality first, so a constraint carrying both would have
   been graded one way by the app and swept the other by the gate: at {eq:6, tol:0.05,
   max:8} and x = 7 the app passed it and the gate failed it. No catalogue constraint
   carries both today, so nothing published was mis-graded — but the gate whose one job
   is to say whether a target can be hit was answering about a different rule than the
   one the learner is scored against, which is the kind of divergence that only ever
   surfaces as "the exercise is impossible" from someone who has just solved it. */
function tuneSpan(c) {
  if (!c) return null;
  if (c.eq !== undefined) {
    const tol = c.tol === undefined ? 0.01 : c.tol;
    return { lo: c.eq - tol, hi: c.eq + tol, eq: c.eq, tol: tol };
  }
  if (c.min !== undefined || c.max !== undefined) {
    return {
      lo: c.min === undefined ? -Infinity : c.min,
      hi: c.max === undefined ? Infinity : c.max,
      eq: undefined, tol: 0,
    };
  }
  return null;                       /* a constraint that states nothing holds nothing */
}
/* isFinite is part of the rule, not a guard bolted onto it: a `max`-only constraint is
   satisfied by -Infinity on a plain comparison, so a model that had overflowed used to
   report a target met. */
function tuneHolds(c, x) {
  const s = tuneSpan(c);
  return !!s && typeof x === 'number' && isFinite(x) && x >= s.lo && x <= s.hi;
}

const Tune = (function () {
  const REG = {};
  function define(spec) { REG[spec.id] = spec; return spec; }
  function get(id) { return REG[id] || null; }
  function ids() { return Object.keys(REG); }
  return { define: define, get: get, ids: ids, span: tuneSpan, holds: tuneHolds };
})();

/* Two resistors from a rail. The whole of a divider design is in the tension between
   the ratio you want and the current you are willing to spend getting it. */
Tune.define({
  id: 'divider',
  title: 'Resistive divider',
  params: [
    { k: 'r1', label: 'R1 (top)', min: 100, max: 47000, step: 100, def: 2200, unit: 'Ω' },
    { k: 'r2', label: 'R2 (bottom)', min: 100, max: 47000, step: 100, def: 2200, unit: 'Ω' },
  ],
  constants: { vin: 5 },
  /* Where a constraint on one of this model's readouts belongs on this model's own
     plot. app.js knows how to draw a line and nothing else: only the model knows which
     of its readouts the axes carry and in what units, which is the same split the rest
     of this file uses — content says what must be true, code says what is.

     Before this, app.js guessed: it drew a band wherever a constraint's key matched
     `plotKey || 'vout'`, and `vout` is a readout of this model alone. So sixteen of the
     twenty-one tune units in the catalogue drew no target at all, and the one that
     overrode the key — EE111 M6, asking for a 1 kHz resonance — got a horizontal line
     at y = 1000 on an axis running 0 to 2.4. */
  marks: function (c) {
    if (c.k !== 'vout') return null;
    const s = tuneSpan(c);
    return s && { axis: 'y', lo: s.lo, hi: s.hi, eq: s.eq };
  },
  compute: function (v, k) {
    const vin = (k && k.vin) || 5;
    const vout = vin * v.r2 / (v.r1 + v.r2);
    const i = vin / (v.r1 + v.r2);
    return {
      vout: { label: 'Vout', value: vout, unit: 'V', dp: 3 },
      i: { label: 'I total', value: i * 1000, unit: 'mA', dp: 3 },
      ratio: { label: 'Divider ratio', value: v.r2 / (v.r1 + v.r2), unit: '', dp: 3 },
    };
  },
  /* Vout against R2, with R1 held where the learner has it */
  plot: function (v, k) {
    const vin = (k && k.vin) || 5;
    const pts = [];
    for (let r2 = 100; r2 <= 47000; r2 *= 1.03) pts.push([r2, vin * r2 / (v.r1 + r2)]);
    return { x: 'R2', y: 'Vout', logX: true, yRange: [0, vin],
             xRange: [100, 47000], points: pts, at: [v.r2, vin * v.r2 / (v.r1 + v.r2)],
             caption: 'Vout vs R2 · R1 = ' + fmtOhm(v.r1) };
  },
});

/* A first-order low-pass: the corner and the attenuation you get at a stated
   frequency are one choice, not two. */
Tune.define({
  id: 'rc-lowpass',
  title: 'RC low-pass',
  params: [
    { k: 'r', label: 'R', min: 100, max: 100000, step: 100, def: 1000, unit: 'Ω' },
    { k: 'c', label: 'C', min: 1, max: 1000, step: 1, def: 100, unit: 'nF' },
  ],
  /* `fsig` is the signal you must not spoil and `fnoise` the interferer you must
     remove. Reporting the response at BOTH is what makes this a design rather than a
     reading: one constraint pushes the corner up, the other pushes it down, and the
     answer is the window where they overlap. */
  constants: { fsig: 100, fnoise: 10000 },
  /* `keep` and `reject` are the same quantity this plot's y-axis draws — |H| — read at
     one stated frequency each, so they are points ON the curve rather than levels
     across it. Drawn where they actually are, the exercise's two requirements become
     two gates the response has to thread between, which is the design tension the unit
     is about and was the one thing its picture did not show. `reject` is quoted in dB
     and the axis is linear, so it is converted here, where the model that chose the
     units is. `tau` is a time and belongs to neither axis. */
  marks: function (c, v, k) {
    const s = tuneSpan(c);
    if (!s) return null;
    if (c.k === 'fc') return { axis: 'x', lo: s.lo, hi: s.hi, eq: s.eq };
    const unDb = function (d) { return isFinite(d) ? Math.pow(10, d / 20) : (d < 0 ? 0 : Infinity); };
    if (c.k === 'keep') return { axis: 'point', x: (k && k.fsig) || 100, lo: s.lo, hi: s.hi };
    if (c.k === 'reject') {
      return { axis: 'point', x: (k && k.fnoise) || 10000, lo: unDb(s.lo), hi: unDb(s.hi) };
    }
    return null;
  },
  compute: function (v, k) {
    const c = v.c * 1e-9;
    const fc = 1 / (2 * Math.PI * v.r * c);
    const at = function (f) { return 1 / Math.sqrt(1 + Math.pow(f / fc, 2)); };
    const fsig = (k && k.fsig) || 100, fnoise = (k && k.fnoise) || 10000;
    return {
      fc: { label: 'Corner f', value: fc, unit: 'Hz', dp: 1 },
      keep: { label: 'kept at ' + fmtHz(fsig), value: at(fsig), unit: '', dp: 4 },
      reject: { label: 'rejected at ' + fmtHz(fnoise), value: 20 * Math.log10(at(fnoise)), unit: 'dB', dp: 2 },
      tau: { label: 'Time constant', value: v.r * c * 1000, unit: 'ms', dp: 3 },
    };
  },
  plot: function (v, k) {
    const c = v.c * 1e-9;
    const fc = 1 / (2 * Math.PI * v.r * c);
    /* The corner runs from 1.59 Hz (100 kΩ, 1 µF) to 1.59 MHz (100 Ω, 1 nF) and the axis
       was pinned at 10 Hz..1 MHz, so at either end of the sliders the marker for the one
       quantity this model is about was drawn outside its own frame. Open both ends far
       enough to hold whatever the sliders reach.

       And far enough to hold the two frequencies the EXERCISE names, which is a
       separate question and was not being asked: the axis floor never went below 10 Hz
       however low `fsig` was set, so EE121 M8 — a debounce filter whose whole subject is
       a 5 Hz button press — stated a requirement at a frequency its own plot did not
       reach. Found by verify_tune_ui.mjs the first time it checked that a drawn target
       lands inside the axes it is drawn on. */
    const fsig = (k && k.fsig) || 100, fnoise = (k && k.fnoise) || 10000;
    const lo = Math.min(10, Math.pow(10, Math.floor(Math.log10(fc / 4))), fsig / 2);
    const hi = Math.max(1e6, Math.pow(10, Math.ceil(Math.log10(fc * 4))), fnoise * 2);
    /* A geometric loop whose start can be zero does not draw a wrong picture, it never
       returns: `0 * 1.06` is 0, so `f <= hi` stays true and a point is pushed until the
       heap dies. It is reachable — `2 * Math.PI * v.r * c` overflows to Infinity at a
       large enough R, which makes fc exactly 0, `log10(0)` -Infinity and `10 ** -Infinity`
       zero. The value clamp keeps a slider away from it, and this keeps the loop bounded
       whoever calls it, because "the caller is careful" is not a property of a loop.
       Found by the mutation run for verify_tune_ui.mjs, which killed Node rather than
       reporting a failure. */
    if (!isFinite(lo) || lo <= 0 || !isFinite(hi) || hi <= lo) {
      throw new Error('the frequency axis is degenerate at these component values');
    }
    const pts = [];
    for (let f = lo, n = 0; f <= hi && n < 2000; f *= 1.06, n++) {
      pts.push([f, 1 / Math.sqrt(1 + Math.pow(f / fc, 2))]);
    }
    return { x: 'f', y: '|H|', logX: true, yRange: [0, 1.05], xRange: [lo, hi],
             points: pts, at: [fc, 1 / Math.SQRT2],
             caption: '|H| vs frequency · corner at ' + fmtHz(fc) };
  },
});

/* A series RLC, chosen so that damping and bandwidth pull against each other the way
   they do in every second-order design. */
Tune.define({
  id: 'rlc',
  title: 'Series RLC',
  params: [
    { k: 'r', label: 'R', min: 1, max: 400, step: 1, def: 100, unit: 'Ω' },
    { k: 'l', label: 'L', min: 1, max: 200, step: 1, def: 100, unit: 'mH' },
    { k: 'c', label: 'C', min: 0.1, max: 20, step: 0.1, def: 2.5, unit: 'µF' },
  ],
  /* This plot's x-axis is frequency and its y-axis is |H|, so `fn` is a vertical target
     and `peak` a horizontal one. `zeta` is on neither: it shapes the curve rather than
     sitting anywhere on it, and a unit constrained only on ζ correctly gets no target
     line — the picture it should be read from is the height of the resonance, which is
     what `peak` measures. A boundary outside the axis is simply not drawn, which is
     right rather than a compromise: EE102 M7's `peak ≤ 30` cannot be violated anywhere
     on a frame that ends at 2.4, and the line arrives on its own as soon as the learner
     winds the Q up far enough for the axis to grow to meet it. */
  marks: function (c) {
    const s = tuneSpan(c);
    if (!s) return null;
    if (c.k === 'fn') return { axis: 'x', lo: s.lo, hi: s.hi, eq: s.eq };
    if (c.k === 'peak') return { axis: 'y', lo: s.lo, hi: s.hi, eq: s.eq };
    return null;
  },
  compute: function (v) {
    const L = v.l * 1e-3, C = v.c * 1e-6;
    const wn = 1 / Math.sqrt(L * C);
    const zeta = (v.r / 2) * Math.sqrt(C / L);
    const peak = zeta < 0.7071 ? 1 / (2 * zeta * Math.sqrt(1 - zeta * zeta)) : 1;
    return {
      wn: { label: 'ω\u2099', value: wn, unit: 'rad/s', dp: 1 },
      fn: { label: 'f\u2099', value: wn / (2 * Math.PI), unit: 'Hz', dp: 2 },
      zeta: { label: 'damping ζ', value: zeta, unit: '', dp: 3 },
      peak: { label: 'peak gain', value: peak, unit: '', dp: 3 },
    };
  },
  plot: function (v) {
    const L = v.l * 1e-3, C = v.c * 1e-6;
    const wn = 1 / Math.sqrt(L * C);
    const zeta = (v.r / 2) * Math.sqrt(C / L);
    /* the same bound as rc-lowpass, for the same reason: L*C overflowing to Infinity
       makes wn exactly 0, and this loop then starts at 0 and never advances */
    if (!isFinite(wn) || wn <= 0) {
      throw new Error('the resonance is undefined at these component values');
    }
    const pts = [];
    for (let f = wn / (2 * Math.PI) / 60, n = 0; f <= wn / (2 * Math.PI) * 60 && n < 2000;
         f *= 1.05, n++) {
      const x = 2 * Math.PI * f / wn;
      pts.push([f, 1 / Math.sqrt(Math.pow(1 - x * x, 2) + Math.pow(2 * zeta * x, 2))]);
    }
    /* The axis was capped at 6 while the peak reaches 1414 at R = 1 Ω, L = 200 mH,
       C = 0.1 µF — the resonance and its marker were both drawn far above the frame, so
       the picture of a very high-Q circuit was indistinguishable from a flat one. The
       peak of |H| is 1/(2ζ√(1−ζ²)), not 1/(2ζ), and above ζ = 1/√2 there is no peak. */
    const peak = zeta < Math.SQRT1_2 ? 1 / (2 * zeta * Math.sqrt(1 - zeta * zeta)) : 1;
    return { x: 'f', y: '|H|', logX: true, yRange: [0, Math.max(2, peak * 1.15)],
             xRange: [wn / (2 * Math.PI) / 60, wn / (2 * Math.PI) * 60], points: pts,
             at: [wn / (2 * Math.PI), 1 / (2 * zeta)],
             caption: '|H| vs frequency · ζ = ' + zeta.toFixed(3) };
  },
});

function fmtOhm(v) {
  return v >= 1000 ? (v / 1000).toFixed(v % 1000 ? 1 : 0) + ' kΩ' : Math.round(v) + ' Ω';
}
function fmtHz(v) {
  if (v >= 1e6) return (v / 1e6).toFixed(2) + ' MHz';
  if (v >= 1e3) return (v / 1e3).toFixed(2) + ' kHz';
  return v.toFixed(1) + ' Hz';
}

Sandbox.define({
  id: 'pole-step',
  title: 'Poles and the step response',
  params: [
    { k: 'zeta', label: 'damping ζ', min: 0, max: 1.6, step: 0.01, def: 0.35 },
    { k: 'wn', label: 'natural ω\u2099', min: 0.5, max: 12, step: 0.1, def: 4, unit: 'rad/s' },
  ],
  draw: function (ctx, w, h, v, kit) {
    const zeta = v.zeta, wn = v.wn;
    const half = Math.floor(w / 2) - 8;

    /* left: the s-plane.
       The axes were fixed at -14..4 while the poles reach -34.2 at the top of both
       sliders (ζ = 1.6, ωₙ = 12): the far pole was drawn outside the plot, over the tick
       labels or past the clip entirely, so the picture showed one pole for a system that
       has two — and the overdamped case is the one whose whole point is where the second
       pole went. Scale to hold whatever the sliders produce, with the old extent as a
       floor so the frame stops breathing at small values. */
    const reach = zeta < 1
      ? Math.max(zeta * wn, wn * Math.sqrt(1 - zeta * zeta))
      : zeta * wn + wn * Math.sqrt(zeta * zeta - 1);
    const R = Math.max(14, reach * 1.2);
    ctx.save();
    ctx.beginPath(); ctx.rect(0, 0, half, h); ctx.clip();
    const sp = kit.frame(ctx, half, h, {
      xRange: [-R, R * (4 / 14)], yRange: [-R, R], xTicks: 4, yTicks: 4,
      margin: { l: 40, r: 10, t: 14, b: 28 },
    });
    sp.hline(0, sp.P.line);
    ctx.save();
    ctx.strokeStyle = sp.P.line;
    ctx.beginPath();
    ctx.moveTo(sp.fx(0), sp.y0); ctx.lineTo(sp.fx(0), sp.y1);
    ctx.stroke();
    ctx.restore();
    const sigma = -zeta * wn;
    if (zeta < 1) {
      const wd = wn * Math.sqrt(1 - zeta * zeta);
      sp.dot(sigma, wd, sp.P.accent, 5);
      sp.dot(sigma, -wd, sp.P.accent, 5);
      sp.text('ω_d = ' + kit.fmt(wd), sp.x0 + 6, sp.y0 + 14, sp.P.dim);
    } else {
      const r = wn * Math.sqrt(zeta * zeta - 1);
      sp.dot(sigma + r, 0, sp.P.amber, 5);
      sp.dot(sigma - r, 0, sp.P.amber, 5);
      sp.text('both poles real', sp.x0 + 6, sp.y0 + 14, sp.P.dim);
    }
    sp.text('s-plane', sp.x1 - 6, sp.y0 + 14, sp.P.faint, 'right');
    ctx.restore();

    /* right: the step response those poles produce */
    ctx.save();
    ctx.translate(half + 16, 0);
    const T = 12 / Math.max(wn * Math.max(zeta, 0.15), 0.6);
    const pts = [];
    let peak = 0;
    for (let i = 0; i <= 400; i++) {
      const t = i / 400 * T;
      let y;
      if (zeta < 1 - 1e-9) {
        const wd = wn * Math.sqrt(1 - zeta * zeta);
        const phi = Math.acos(Math.min(1, Math.max(-1, zeta)));
        y = 1 - Math.exp(-zeta * wn * t) / Math.sqrt(1 - zeta * zeta) * Math.sin(wd * t + phi);
      } else if (Math.abs(zeta - 1) < 1e-9) {
        y = 1 - Math.exp(-wn * t) * (1 + wn * t);
      } else {
        const r = wn * Math.sqrt(zeta * zeta - 1);
        const a = -zeta * wn + r, b = -zeta * wn - r;
        y = 1 + (b * Math.exp(a * t) - a * Math.exp(b * t)) / (a - b);
      }
      peak = Math.max(peak, y);
      pts.push([t, y]);
    }
    const st = kit.frame(ctx, w - half - 16, h, {
      xRange: [0, T], yRange: [0, Math.max(1.7, peak * 1.12)], xTicks: 4, yTicks: 4,
      margin: { l: 40, r: 12, t: 14, b: 28 },
    });
    st.hline(1, st.P.faint, [3, 4]);
    st.line(pts, st.P.accent, 2);
    st.text('step response', st.x1 - 6, st.y0 + 14, st.P.faint, 'right');
    ctx.restore();
  },
  explain: function (v) {
    const zeta = v.zeta, wn = v.wn;
    /* "Take ζ to zero" is the first thing CTRL510 module 2's brief tells the learner to
       do, and 4/(ζωₙ) is a division by zero there: the readout printed the word
       "Infinity" at the exact setting the lesson sends them to. There is no settling
       time at ζ = 0 — that is the point of the setting — so say so instead. */
    if (zeta <= 0) {
      return '<b>Undamped.</b> The poles sit on the imaginary axis at ±' + wn.toFixed(2) +
        ' rad/s, overshoot is a full 100%, and there is <em>no</em> settling time: the ' +
        'response rings at the same amplitude for ever. This is the boundary of stability, ' +
        'not a slow approach to it.';
    }
    if (zeta < 1) {
      const os = Math.exp(-Math.PI * zeta / Math.sqrt(1 - zeta * zeta)) * 100;
      return '<b>' + os.toFixed(1) + '%</b> overshoot, settling in about <b>' +
        (4 / (zeta * wn)).toFixed(2) + ' s</b>. The poles sit at an angle of ' +
        (Math.acos(zeta) * 180 / Math.PI).toFixed(0) + '° from the negative real axis \u2014 ' +
        'that angle <em>is</em> the damping.';
    }
    if (Math.abs(zeta - 1) < 0.02) return 'Critically damped: the fastest approach with no overshoot at all.';
    return 'Overdamped \u2014 two real poles, no overshoot, and the slower pole sets the pace.';
  },
});

/* Bode: gain and phase of a first- or second-order plant */
Sandbox.define({
  id: 'bode',
  title: 'Bode magnitude and phase',
  params: [
    { k: 'wn', label: 'corner ω\u2099', min: 0.5, max: 200, step: 0.5, def: 20, unit: 'rad/s' },
    { k: 'zeta', label: 'damping ζ', min: 0.05, max: 1.5, step: 0.01, def: 0.5 },
    { k: 'K', label: 'gain K', min: 0.1, max: 20, step: 0.1, def: 1 },
  ],
  draw: function (ctx, w, h, v, kit) {
    const lo = 0.1, hi = 2000;
    const mag = [], pha = [];
    for (let i = 0; i <= 300; i++) {
      const wv = Math.pow(10, Math.log10(lo) + i / 300 * (Math.log10(hi) - Math.log10(lo)));
      const x = wv / v.wn;
      const re = 1 - x * x, im = 2 * v.zeta * x;
      const m = v.K / Math.sqrt(re * re + im * im);
      mag.push([wv, 20 * Math.log10(Math.max(m, 1e-9))]);
      pha.push([wv, -Math.atan2(im, re) * 180 / Math.PI]);
    }
    const topH = Math.round(h * 0.56);

    /* K = 20 at ζ = 0.05 peaks at 46 dB against an axis that stopped at 40, so the top of
       the resonance — the only part of the plot those two sliders are about — was drawn
       outside the frame with nothing to say it had been. */
    let dbTop = 40;
    for (let i = 0; i < mag.length; i++) if (mag[i][1] + 8 > dbTop) dbTop = Math.ceil((mag[i][1] + 8) / 10) * 10;

    ctx.save();
    ctx.beginPath(); ctx.rect(0, 0, w, topH); ctx.clip();
    const g = kit.frame(ctx, w, topH, {
      xRange: [lo, hi], yRange: [-80, dbTop], logX: true, xTicks: 4, yTicks: 3,
      margin: { l: 46, r: 14, t: 12, b: 22 },
      xLabel: function (x) { return x >= 1 ? String(Math.round(x)) : x.toFixed(1); },
    });
    g.hline(0, g.P.faint, [3, 4]);
    g.line(mag, g.P.accent, 2);
    g.dot(v.wn, 20 * Math.log10(v.K / (2 * v.zeta)), g.P.amber, 4);
    g.text('dB', g.x0 + 4, g.y0 + 12, g.P.faint);
    ctx.restore();

    ctx.save();
    ctx.translate(0, topH + 4);
    const ph = kit.frame(ctx, w, h - topH - 4, {
      xRange: [lo, hi], yRange: [-190, 10], logX: true, xTicks: 4, yTicks: 3,
      margin: { l: 46, r: 14, t: 10, b: 28 },
      xLabel: function (x) { return x >= 1 ? String(Math.round(x)) : x.toFixed(1); },
    });
    ph.hline(-90, ph.P.faint, [3, 4]);
    ph.line(pha, ph.P.blue, 2);
    ph.text('degrees', ph.x0 + 4, ph.y0 + 12, ph.P.faint);
    ph.text('ω rad/s', ph.x1 - 6, ph.y1 + 20, ph.P.faint, 'right');
    ctx.restore();
  },
  explain: function (v) {
    const peak = v.zeta < 0.707
      ? 20 * Math.log10(v.K / (2 * v.zeta * Math.sqrt(1 - v.zeta * v.zeta)))
      : null;
    return 'At the corner the phase is exactly \u221290°, whatever the damping. ' +
      (peak === null
        ? 'With ζ above 0.707 there is no resonant peak at all.'
        : 'The peak here is <b>' + peak.toFixed(1) + ' dB</b>, and it grows without bound as ζ → 0.');
  },
});

/* the z-plane and its impulse response — the discrete counterpart */
Sandbox.define({
  id: 'z-plane',
  title: 'Pole radius and the impulse response',
  params: [
    { k: 'r', label: 'radius |z|', min: 0.05, max: 1.25, step: 0.01, def: 0.85 },
    { k: 'th', label: 'angle θ', min: 0, max: 3.14159, step: 0.01, def: 0.6, unit: 'rad' },
  ],
  draw: function (ctx, w, h, v, kit) {
    const P = kit.palette();
    const half = Math.floor(w / 2) - 8;

    /* unit circle */
    ctx.save();
    const cx = half / 2, cy = h / 2, R = Math.min(half, h) / 2 - 26;
    ctx.strokeStyle = P.line; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(cx - R - 12, cy); ctx.lineTo(cx + R + 12, cy);
    ctx.moveTo(cx, cy - R - 12); ctx.lineTo(cx, cy + R + 12);
    ctx.stroke();
    const inside = v.r < 1;
    ctx.fillStyle = inside ? P.accent : P.amber;
    [v.th, -v.th].forEach(function (t) {
      ctx.beginPath();
      ctx.arc(cx + v.r * R * Math.cos(t), cy - v.r * R * Math.sin(t), 5, 0, Math.PI * 2);
      ctx.fill();
    });
    ctx.font = '11px ui-monospace, monospace';
    ctx.fillStyle = P.faint;
    ctx.fillText('z-plane', 8, 18);
    ctx.restore();

    /* impulse response */
    ctx.save();
    ctx.translate(half + 16, 0);
    const N = 44, pts = [];
    let mx = 0;
    for (let n = 0; n <= N; n++) {
      const y = Math.pow(v.r, n) * Math.cos(v.th * n);
      mx = Math.max(mx, Math.abs(y));
      pts.push([n, y]);
    }
    const lim = Math.max(1.05, mx * 1.1);
    const f = kit.frame(ctx, w - half - 16, h, {
      xRange: [0, N], yRange: [-lim, lim], xTicks: 4, yTicks: 4, margin: { l: 42, r: 12, t: 14, b: 28 },
    });
    f.hline(0, f.P.line);
    pts.forEach(function (pt) {
      ctx.beginPath();
      ctx.moveTo(f.fx(pt[0]), f.fy(0));
      ctx.lineTo(f.fx(pt[0]), f.fy(pt[1]));
      ctx.strokeStyle = inside ? f.P.accent : f.P.amber;
      ctx.lineWidth = 1.5;
      ctx.stroke();
      f.dot(pt[0], pt[1], inside ? f.P.accent : f.P.amber, 2.4);
    });
    f.text('h[n]', f.x0 + 4, f.y0 + 12, f.P.faint);
    ctx.restore();
  },
  explain: function (v) {
    if (v.r < 0.999) {
      return 'Inside the unit circle, so the response decays \u2014 to 1% after about <b>' +
        Math.ceil(Math.log(0.01) / Math.log(v.r)) + ' samples</b>. Stability in discrete time is ' +
        'a radius, not a half-plane.';
    }
    /* "it oscillates forever" is only true off the real axis. At \u03b8 = 0 with r = 1 the
       response the picture draws is h[n] = 1 for every n \u2014 a flat line of identical
       samples, which is the one thing that is not an oscillation. */
    if (v.r < 1.001) {
      if (v.th < 0.005) return 'On the circle at zero angle: h[n] = 1 for every sample. It does not ' +
        'oscillate and it does not decay \u2014 a pure integrator, and marginally stable.';
      if (v.th > Math.PI - 0.005) return 'On the circle at \u03b8 = \u03c0: the samples alternate \u00b11 forever. ' +
        'Marginally stable, at the fastest rate a sampled sequence can carry.';
      return 'Exactly on the circle: it oscillates forever and never settles. Marginally stable.';
    }
    return 'Outside the circle. Every sample is larger than the last \u2014 this filter diverges.';
  },
});

/* ---- control-track visualisers ---- */

/* the phase portrait: what a 2x2 A matrix does to the state, drawn as trajectories */
Sandbox.define({
  id: 'phase-portrait',
  title: 'State-space trajectories',
  params: [
    { k: 'a11', label: 'a\u2081\u2081', min: -3, max: 3, step: 0.05, def: 0 },
    { k: 'a12', label: 'a\u2081\u2082', min: -3, max: 3, step: 0.05, def: 1 },
    { k: 'a21', label: 'a\u2082\u2081', min: -6, max: 3, step: 0.05, def: -2 },
    { k: 'a22', label: 'a\u2082\u2082', min: -4, max: 2, step: 0.05, def: -0.6 },
    /* Forward Euler steps along the tangent and lands outside the curve every time, so
       a centre \u2014 trace 0, the one case whose exact orbits are closed \u2014 was drawn as an
       outward spiral while the line underneath said "it orbits forever". At the unit
       centre the enclosed area grew 22% over the interval drawn; at the top of the
       sliders (a12 = 3, a21 = -6) it grew by a factor of 37 and the rings left the
       frame. RK4 holds the same area to 3e-5 % over the identical run. Euler stays,
       and is now labelled and switchable, because EE131 module 9 is about precisely
       this error and needs to be able to show it happening. */
    { k: 'solver', label: 'integrator', min: 0, max: 1, step: 1, def: 1,
      fmt: function (x) { return x ? 'RK4' : 'forward Euler'; } },
  ],
  draw: function (ctx, w, h, v, kit) {
    const L = 3.2;
    const f = kit.frame(ctx, w, h, {
      xRange: [-L, L], yRange: [-L, L], xTicks: 4, yTicks: 4, margin: { l: 42, r: 14, t: 14, b: 28 },
    });
    const A = [[v.a11, v.a12], [v.a21, v.a22]];

    /* direction field */
    ctx.save();
    ctx.strokeStyle = f.P.line;
    ctx.lineWidth = 1;
    for (let i = -3; i <= 3; i++) {
      for (let j = -3; j <= 3; j++) {
        const x = i * L / 3.4, y = j * L / 3.4;
        let dx = A[0][0] * x + A[0][1] * y, dy = A[1][0] * x + A[1][1] * y;
        const m = Math.hypot(dx, dy) || 1;
        dx = dx / m * 0.28; dy = dy / m * 0.28;
        ctx.beginPath();
        ctx.moveTo(f.fx(x), f.fy(y));
        ctx.lineTo(f.fx(x + dx), f.fy(y + dy));
        ctx.stroke();
      }
    }
    ctx.restore();

    /* trajectories from a ring of starts */
    const cols = [f.P.accent, f.P.blue, f.P.purple, f.P.amber];
    const rk = v.solver >= 0.5;
    const fx1 = function (x, y) { return A[0][0] * x + A[0][1] * y; };
    const fx2 = function (x, y) { return A[1][0] * x + A[1][1] * y; };
    for (let k = 0; k < 8; k++) {
      const th = k / 8 * Math.PI * 2;
      let x = 2.7 * Math.cos(th), y = 2.7 * Math.sin(th);
      const pts = [[x, y]];
      const dt = 0.012;
      for (let n = 0; n < 1400; n++) {
        if (rk) {
          const k1x = fx1(x, y), k1y = fx2(x, y);
          const k2x = fx1(x + k1x * dt / 2, y + k1y * dt / 2), k2y = fx2(x + k1x * dt / 2, y + k1y * dt / 2);
          const k3x = fx1(x + k2x * dt / 2, y + k2y * dt / 2), k3y = fx2(x + k2x * dt / 2, y + k2y * dt / 2);
          const k4x = fx1(x + k3x * dt, y + k3y * dt), k4y = fx2(x + k3x * dt, y + k3y * dt);
          x += dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x);
          y += dt / 6 * (k1y + 2 * k2y + 2 * k3y + k4y);
        } else {
          const dx = fx1(x, y), dy = fx2(x, y);
          x += dx * dt; y += dy * dt;
        }
        if (Math.abs(x) > L * 1.6 || Math.abs(y) > L * 1.6) break;
        if (n % 4 === 0) pts.push([x, y]);
      }
      f.line(pts, cols[k % cols.length], 1.4);
    }
    f.dot(0, 0, f.P.ink, 3.5);
    f.text('x\u2081', f.x1 - 6, f.y1 + 20, f.P.faint, 'right');
    f.text('x\u2082', f.x0 + 4, f.y0 + 12, f.P.faint);
  },
  explain: function (v) {
    const tr = v.a11 + v.a22;
    const det = v.a11 * v.a22 - v.a12 * v.a21;
    const disc = tr * tr - 4 * det;
    let kind;
    if (det < 0) kind = 'a <b>saddle</b> \u2014 unstable whatever you do to the gains';
    else if (disc < 0) kind = tr < 0 ? 'a <b>stable spiral</b>' : (tr > 0 ? 'an <b>unstable spiral</b>' : 'a <b>centre</b> \u2014 it orbits forever');
    else kind = tr < 0 ? 'a <b>stable node</b>' : 'an <b>unstable node</b>';
    let out = 'trace = ' + tr.toFixed(2) + ', det = ' + det.toFixed(2) + ' \u2014 ' + kind +
      '. Stability is decided entirely by those two numbers, never by the individual entries.';
    /* A centre is the one classification the drawing can contradict, so say so rather
       than leaving the learner to decide whether the creep is the physics. The Euler
       map is I + A\u00b7dt, whose determinant is 1 + tr\u00b7dt + det\u00b7dt\u00b2 \u2014 at trace zero that is
       exactly the factor the enclosed area is multiplied by, once per step. */
    if (v.solver < 0.5 && det > 0 && Math.abs(tr) < 1e-9) {
      const grow = Math.pow(1 + det * 0.012 * 0.012, 1400);
      const by = grow >= 2 ? grow.toFixed(0) + ' times' : 'a further ' + ((grow - 1) * 100).toFixed(0) + '%';
      out += ' <em>The curves drawn will not close.</em> Forward Euler grows the area they enclose ' +
        'by ' + by + ' over this run, so the orbits spiral out. Nothing in the matrix does that \u2014 ' +
        'switch the integrator to RK4 and they close.';
    }
    return out;
  },
});

/* pole placement by state feedback: move the closed-loop poles, watch the effort */
Sandbox.define({
  id: 'pole-place',
  title: 'Pole placement and control effort',
  params: [
    { k: 'p1', label: 'pole 1', min: -12, max: -0.2, step: 0.1, def: -1.5 },
    { k: 'p2', label: 'pole 2', min: -12, max: -0.2, step: 0.1, def: -3 },
  ],
  draw: function (ctx, w, h, v, kit) {
    /* plant: double integrator, x'' = u. desired char poly (s-p1)(s-p2) */
    const k1 = v.p1 * v.p2;            /* position gain */
    const k2 = -(v.p1 + v.p2);         /* velocity gain */
    const T = 8, dt = 0.004;
    let x = 1, xd = 0;
    const xs = [], us = [];
    let peakU = 0;
    for (let t = 0; t <= T; t += dt) {
      const u = -k1 * x - k2 * xd;
      peakU = Math.max(peakU, Math.abs(u));
      xd += u * dt;
      x += xd * dt;
      if (Math.round(t / dt) % 6 === 0) { xs.push([t, x]); us.push([t, u]); }
    }
    const topH = Math.round(h * 0.54);

    ctx.save();
    ctx.beginPath(); ctx.rect(0, 0, w, topH); ctx.clip();
    const a = kit.frame(ctx, w, topH, {
      xRange: [0, T], yRange: [-0.45, 1.15], xTicks: 4, yTicks: 3, margin: { l: 44, r: 14, t: 12, b: 20 },
    });
    a.hline(0, a.P.faint, [3, 4]);
    a.line(xs, a.P.accent, 2);
    a.text('position', a.x0 + 4, a.y0 + 12, a.P.faint);
    ctx.restore();

    ctx.save();
    ctx.translate(0, topH + 4);
    const lim = Math.max(2, peakU * 1.15);
    const b = kit.frame(ctx, w, h - topH - 4, {
      xRange: [0, T], yRange: [-lim, lim], xTicks: 4, yTicks: 3, margin: { l: 44, r: 14, t: 10, b: 28 },
    });
    b.hline(0, b.P.line);
    b.line(us, b.P.amber, 2);
    b.text('control effort u', b.x0 + 4, b.y0 + 12, b.P.faint);
    b.text('seconds', b.x1 - 6, b.y1 + 20, b.P.faint, 'right');
    ctx.restore();
  },
  explain: function (v) {
    const k1 = (v.p1 * v.p2).toFixed(2), k2 = (-(v.p1 + v.p2)).toFixed(2);
    const fast = Math.max(Math.abs(v.p1), Math.abs(v.p2));
    return 'K = [' + k1 + ', ' + k2 + ']. Settling goes as 1/|p|, but the peak effort grows ' +
      'roughly as |p|\u00b2 \u2014 push the poles to \u2212' + fast.toFixed(1) +
      ' and you are asking for an actuator that can deliver it. That trade is the whole of LQR.';
  },
});

/* a scalar Kalman filter: truth, noisy measurement, and the estimate between them */
Sandbox.define({
  id: 'kalman',
  title: 'Trusting the model against the measurement',
  params: [
    { k: 'q', label: 'process noise Q', min: 0.0005, max: 0.2, step: 0.0005, def: 0.01 },
    { k: 'r', label: 'measurement noise R', min: 0.005, max: 2, step: 0.005, def: 0.35 },
  ],
  draw: function (ctx, w, h, v, kit) {
    /* A fixed pseudo-random stream, so the picture is stable while a slider moves.
       This was the C-library LCG written straight into JavaScript: seed * 1103515245
       reaches 2.4e18, past the 2^53 where a double stops counting integers, so the low
       bits of every product were rounding noise. The period collapsed from 2^31 to
       10466 and bit 0 came up set 422 times in 100000 draws. It happens to be harmless
       today — the 240 values this draws are still distinct and still pass as Gaussian
       (mean 0.024, sd 0.98) — but it was luck, not design. Math.imul does the multiply
       in exact 32-bit arithmetic, which is what the constant was chosen for. */
    let seed = 12345;
    const rnd = function () {
      seed = (Math.imul(seed, 1103515245) + 12345) & 0x7fffffff;
      return seed / 0x7fffffff;
    };
    const gauss = function () {
      const u = Math.max(rnd(), 1e-9), t = rnd();
      return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * t);
    };
    const N = 120;
    const truth = [], meas = [], est = [];
    let x = 0, xh = 0, P0 = 1;
    let sumErrM = 0, sumErrE = 0;
    for (let n = 0; n < N; n++) {
      x = x + 0.03 * Math.cos(n / 9) + Math.sqrt(v.q) * gauss();
      const z = x + Math.sqrt(v.r) * gauss();
      /* predict then correct */
      P0 = P0 + v.q;
      const K = P0 / (P0 + v.r);
      xh = xh + K * (z - xh);
      P0 = (1 - K) * P0;
      truth.push([n, x]); meas.push([n, z]); est.push([n, xh]);
      sumErrM += (z - x) * (z - x);
      sumErrE += (xh - x) * (xh - x);
    }
    const all = truth.concat(meas).map(function (p) { return p[1]; });
    const lo = Math.min.apply(null, all) - 0.3, hi = Math.max.apply(null, all) + 0.3;
    const f = kit.frame(ctx, w, h, {
      xRange: [0, N], yRange: [lo, hi], xTicks: 4, yTicks: 4, margin: { l: 44, r: 14, t: 14, b: 28 },
    });
    ctx.save();
    ctx.globalAlpha = 0.55;
    meas.forEach(function (p) { f.dot(p[0], p[1], f.P.dim, 1.8); });
    ctx.restore();
    f.line(truth, f.P.blue, 2);
    f.line(est, f.P.accent, 2);
    f.text('truth', f.x0 + 6, f.y0 + 12, f.P.blue);
    f.text('estimate', f.x0 + 52, f.y0 + 12, f.P.accent);
    f.text('measurements', f.x0 + 128, f.y0 + 12, f.P.dim);
    /* The two RMS errors were computed on every frame and hung on the canvas context,
       where nothing has ever read them. They are the number the whole picture is an
       argument for — whether the estimate beat the raw sensor — so draw them. */
    const rmsM = Math.sqrt(sumErrM / N), rmsE = Math.sqrt(sumErrE / N);
    f.text('RMS error — sensor ' + rmsM.toFixed(3) + ', estimate ' + rmsE.toFixed(3) +
      ' (' + (rmsM / rmsE).toFixed(1) + '× better)', f.x0 + 6, f.y1 - 8, f.P.dim);
  },
  explain: function (v) {
    /* P = (Q + sqrt(Q^2 + 4QR))/2 solves P = PR/(P+R) + Q; K = P/(P+R) reduces to the
       line below. Checked against the loop above, which converges to it. */
    const ratio = v.q / v.r;
    const K = Math.sqrt(ratio * ratio / 4 + ratio) - ratio / 2;
    return 'The steady-state gain settles near <b>K = ' + K.toFixed(3) + '</b>. It depends only on ' +
      'the <em>ratio</em> Q/R, not on either alone: raise Q and the filter believes the sensor, ' +
      'raise R and it believes the model.';
  },
});

/* sliding mode: the switching surface, and the chatter that comes with it */
Sandbox.define({
  id: 'sliding-mode',
  title: 'Sliding surfaces and chatter',
  params: [
    { k: 'lam', label: 'surface slope \u03bb', min: 0.4, max: 6, step: 0.05, def: 2 },
    { k: 'eta', label: 'switching gain \u03b7', min: 0.2, max: 8, step: 0.05, def: 2.5 },
    { k: 'bl', label: 'boundary layer \u03c6', min: 0, max: 0.6, step: 0.005, def: 0 },
  ],
  draw: function (ctx, w, h, v, kit) {
    const L = 2.4;
    const f = kit.frame(ctx, w, h, {
      xRange: [-L, L], yRange: [-L * 1.6, L * 1.6], xTicks: 4, yTicks: 4, margin: { l: 44, r: 14, t: 14, b: 28 },
    });
    /* the sliding surface s = xd + lam*x = 0 */
    f.line([[-L, L * v.lam], [L, -L * v.lam]], f.P.purple, 1.6);
    if (v.bl > 0) {
      [v.bl, -v.bl].forEach(function (o) {
        ctx.save(); ctx.globalAlpha = 0.45;
        f.line([[-L, L * v.lam + o], [L, -L * v.lam + o]], f.P.purple, 1);
        ctx.restore();
      });
    }
    /* trajectories reaching the surface then sliding down it */
    [[2, 2.6], [-2, -2.6], [1.6, -2.2], [-1.6, 2.2]].forEach(function (start, i) {
      let x = start[0], xd = start[1];
      const pts = [[x, xd]];
      const dt = 0.0025;
      for (let n = 0; n < 6000; n++) {
        const sVal = xd + v.lam * x;
        const sat = v.bl > 0 ? Math.max(-1, Math.min(1, sVal / v.bl)) : (sVal > 0 ? 1 : (sVal < 0 ? -1 : 0));
        const u = -v.eta * sat;
        xd += u * dt;
        x += xd * dt;
        if (Math.abs(x) > L * 1.4 || Math.abs(xd) > L * 2.4) break;
        if (n % 6 === 0) pts.push([x, xd]);
      }
      f.line(pts, [f.P.accent, f.P.blue, f.P.amber, f.P.ink][i], 1.5);
    });
    f.dot(0, 0, f.P.ink, 3.5);
    f.text('x', f.x1 - 6, f.y1 + 20, f.P.faint, 'right');
    f.text('\u1e8b', f.x0 + 4, f.y0 + 12, f.P.faint);
  },
  explain: function (v) {
    if (v.bl === 0) {
      return 'With no boundary layer the control switches infinitely fast on the surface \u2014 ideal in ' +
        'the mathematics, <b>chatter</b> in any real actuator. Once on the surface the dynamics are ' +
        '\u1e8b = \u2212' + v.lam.toFixed(2) + 'x, first order and independent of the plant.';
    }
    return 'A boundary layer of ' + v.bl.toFixed(3) + ' trades exactness for smoothness: the switching ' +
      'becomes a saturation, the chatter goes, and the state settles into a band around the surface ' +
      'rather than onto it.';
  },
});

/* ---- signal, power, field and architecture visualisers ---- */

/* sampling and aliasing: the one picture that makes Nyquist obvious */
Sandbox.define({
  id: 'spectrum',
  title: 'Sampling, aliasing and the Nyquist limit',
  params: [
    { k: 'fsig', label: 'signal f', min: 1, max: 240, step: 1, def: 30, unit: 'Hz' },
    { k: 'fs', label: 'sample rate', min: 20, max: 400, step: 5, def: 200, unit: 'Hz' },
  ],
  draw: function (ctx, w, h, v, kit) {
    const topH = Math.round(h * 0.56);
    const T = 0.1;

    /* time domain: the true wave, the samples, and the alias they imply */
    ctx.save();
    ctx.beginPath(); ctx.rect(0, 0, w, topH); ctx.clip();
    const f = kit.frame(ctx, w, topH, {
      xRange: [0, T], yRange: [-1.35, 1.35], xTicks: 4, yTicks: 2,
      margin: { l: 40, r: 12, t: 12, b: 20 },
      xLabel: function (x) { return (x * 1000).toFixed(0); },
    });
    const truth = [];
    for (let i = 0; i <= 600; i++) {
      const t = i / 600 * T;
      truth.push([t, Math.sin(2 * Math.PI * v.fsig * t)]);
    }
    f.line(truth, f.P.dim, 1.2);

    /* where the alias lands: fold the signal about multiples of fs */
    let fa = Math.abs(v.fsig % v.fs);
    if (fa > v.fs / 2) fa = v.fs - fa;
    const alias = [];
    for (let i = 0; i <= 600; i++) {
      const t = i / 600 * T;
      alias.push([t, Math.sin(2 * Math.PI * fa * t)]);
    }
    const aliased = Math.abs(fa - v.fsig) > 0.5;
    if (aliased) f.line(alias, f.P.amber, 2);

    const n = Math.floor(T * v.fs);
    for (let i = 0; i <= n; i++) {
      const t = i / v.fs;
      f.dot(t, Math.sin(2 * Math.PI * v.fsig * t), f.P.accent, 3);
    }
    f.text('ms', f.x1 - 6, f.y1 + 16, f.P.faint, 'right');
    ctx.restore();

    /* frequency domain: signal, Nyquist line, and the folded image */
    ctx.save();
    ctx.translate(0, topH + 4);
    const g = kit.frame(ctx, w, h - topH - 4, {
      xRange: [0, 260], yRange: [0, 1.25], xTicks: 4, yTicks: 2,
      margin: { l: 40, r: 12, t: 12, b: 28 },
    });
    const spike = function (x, colour, label) {
      if (x < 0 || x > 260) return;
      ctx.beginPath();
      ctx.moveTo(g.fx(x), g.fy(0));
      ctx.lineTo(g.fx(x), g.fy(1));
      ctx.strokeStyle = colour;
      ctx.lineWidth = 2;
      ctx.stroke();
      g.text(label, g.fx(x) + 4, g.fy(1) - 4, colour);
    };
    const nyq = v.fs / 2;
    ctx.save();
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(g.fx(nyq), g.y0); ctx.lineTo(g.fx(nyq), g.y1);
    ctx.strokeStyle = g.P.purple; ctx.lineWidth = 1.4; ctx.stroke();
    ctx.restore();
    g.text('f\u209b/2', g.fx(nyq) + 4, g.y0 + 12, g.P.purple);
    spike(v.fsig, g.P.dim, 'signal');
    if (aliased) spike(fa, g.P.amber, 'alias');
    g.text('Hz', g.x1 - 6, g.y1 + 20, g.P.faint, 'right');
    ctx.restore();
  },
  explain: function (v) {
    const nyq = v.fs / 2;
    let fa = Math.abs(v.fsig % v.fs);
    if (fa > nyq) fa = v.fs - fa;
    /* The strict inequality is the whole theorem, and this is the one setting where the
       caption used to contradict the dots directly above it. At f = fs/2 exactly, every
       sample is sin(pi*n) = 0: the picture draws the entire sampled sequence lying on
       the axis while the sentence read "the samples determine the wave uniquely". */
    if (Math.abs(v.fsig - nyq) < 1e-9) {
      return 'Exactly at the limit, which the sampling theorem excludes rather than ' +
        'includes. Every sample lands on a zero crossing — look at the dots, they are all ' +
        'on the axis — so the amplitude is gone and a wave of any size would have given the ' +
        'same record. Nyquist needs f <b>strictly below</b> fₛ/2.';
    }
    if (Math.abs(fa - v.fsig) < 0.5) {
      return 'Below the Nyquist limit of <b>' + nyq.toFixed(0) + ' Hz</b>, so the samples ' +
        'determine the wave uniquely. Nothing is lost.';
    }
    return 'Above Nyquist: the samples are indistinguishable from a <b>' + fa.toFixed(1) +
      ' Hz</b> wave. Nothing downstream can undo this \u2014 the information is gone at the ' +
      'converter, which is why the anti-alias filter is analogue and comes first.';
  },
});

/* noise: the 1/f corner, and why it decides your architecture */
Sandbox.define({
  id: 'noise-corner',
  title: 'Flicker noise, thermal noise and the corner between them',
  params: [
    /* Linear with step 100 made the whole of 1..100 Hz a single notch — the region a
       chopper amplifier exists for — and put 999 of the 1000 positions above 101 Hz.
       Two lessons opened at corners (100 Hz, 20 kHz) the slider could not return to. */
    { k: 'fc', label: '1/f corner', min: 1, max: 100000, step: 1, log: true, def: 10000, unit: 'Hz' },
    { k: 'nth', label: 'thermal floor', min: 1, max: 40, step: 0.5, def: 8, unit: 'nV/\u221aHz' },
  ],
  draw: function (ctx, w, h, v, kit) {
    const lo = 1, hi = 1e7;
    const pts = [];
    let maxv = 0;
    for (let i = 0; i <= 400; i++) {
      const fq = Math.pow(10, Math.log10(lo) + i / 400 * (Math.log10(hi) - Math.log10(lo)));
      const val = v.nth * Math.sqrt(1 + v.fc / fq);
      maxv = Math.max(maxv, val);
      pts.push([fq, 20 * Math.log10(val)]);
    }
    const f = kit.frame(ctx, w, h, {
      xRange: [lo, hi], yRange: [20 * Math.log10(v.nth) - 6, 20 * Math.log10(maxv) + 6],
      logX: true, xTicks: 7, yTicks: 4, margin: { l: 52, r: 14, t: 14, b: 30 },
      xLabel: function (x) {
        if (x >= 1e6) return (x / 1e6) + 'M';
        if (x >= 1e3) return (x / 1e3) + 'k';
        return String(Math.round(x));
      },
    });
    f.hline(20 * Math.log10(v.nth), f.P.faint, [4, 4]);
    f.line(pts, f.P.accent, 2);
    ctx.save();
    ctx.setLineDash([3, 4]);
    ctx.beginPath();
    ctx.moveTo(f.fx(v.fc), f.y0); ctx.lineTo(f.fx(v.fc), f.y1);
    ctx.strokeStyle = f.P.purple; ctx.lineWidth = 1.4; ctx.stroke();
    ctx.restore();
    /* at fc = 1 the corner label started at the left edge, on the same baseline as the
       axis caption, and the two printed on top of each other */
    const cornerX = f.fx(v.fc);
    const nearLeft = cornerX < f.x0 + 96;
    f.text('corner', cornerX + (nearLeft ? 5 : -5), f.y0 + (nearLeft ? 27 : 13),
      f.P.purple, nearLeft ? 'left' : 'right');
    f.text('thermal floor', f.x0 + 6, f.fy(20 * Math.log10(v.nth)) - 6, f.P.faint);
    f.text('dB re 1 nV/\u221aHz', f.x0 + 6, f.y0 + 13, f.P.faint);
    f.text('Hz', f.x1 - 6, f.y1 + 20, f.P.faint, 'right');
  },
  explain: function (v) {
    /* The plot is an amplitude density in nV/\u221aHz, so the slope drawn below the corner is
       10 dB per decade, not 20. Saying "rises as 1/f" beside it named the power law over
       a picture of the voltage one \u2014 and EE221 module 10's own notice, on the same
       screen, spells the distinction out and contradicted this sentence. */
    return 'Below the corner the density rises as 1/\u221af \u2014 <b>10 dB per decade</b> on this axis, ' +
      'because it is the noise <em>power</em> that goes as 1/f and the plot plots a voltage. ' +
      'Integrating for longer stops helping there, which is the region chopping and correlated ' +
      'double sampling exist for. Above it the floor is flat at <b>' + v.nth.toFixed(1) +
      ' nV/\u221aHz</b>, set by resistance and temperature, and the only lever left is a wider ' +
      'device or more current.';
  },
});

/* hard versus soft switching, and the ringing that decides your losses */
Sandbox.define({
  id: 'switching',
  title: 'Hard switching, ringing and ZVS',
  params: [
    { k: 'ls', label: 'loop inductance', min: 1, max: 80, step: 1, def: 30, unit: 'nH' },
    { k: 'coss', label: 'device C\u2092\u209b\u209b', min: 20, max: 600, step: 10, def: 150, unit: 'pF' },
    { k: 'dead', label: 'dead time', min: 0, max: 300, step: 5, def: 0, unit: 'ns' },
  ],
  draw: function (ctx, w, h, v, kit) {
    const L = v.ls * 1e-9, C = v.coss * 1e-12;
    const wr = 1 / Math.sqrt(L * C);
    const Tspan = 600e-9;
    const zeta = 0.06;
    /* resonant time to swing Vds fully: a quarter period */
    const tSwing = (Math.PI / 2) / wr;
    const dead = v.dead * 1e-9;
    const soft = dead >= tSwing * 0.95;

    const vds = [], isw = [];
    for (let i = 0; i <= 700; i++) {
      const t = i / 700 * Tspan;
      let y;
      if (t < 100e-9) y = 1;
      else {
        const td = t - 100e-9;
        if (soft) {
          /* the tank swings Vds down to zero before the device turns on */
          y = td < tSwing ? Math.cos(wr * td) : 0;
          if (y < 0) y = 0;
        } else {
          const env = Math.exp(-zeta * wr * td);
          y = env * Math.cos(wr * td) * 0.9;
          if (td > dead) y = y * Math.exp(-(td - dead) * 6e6);
        }
      }
      vds.push([t * 1e9, y]);
      /* The soft-switched current used to start rising the instant the drain began to
         fall, so the picture drew current and voltage overlapping — which is the
         definition of hard switching — under a caption reading "turns on at zero volts".
         The device conducts after the tank has finished the swing; that is what the dead
         time is for, and now it is what the trace shows. */
      let cur;
      if (t < 100e-9) cur = 0;
      else if (!soft) cur = 1;
      else {
        const since = t - 100e-9 - tSwing;
        cur = since <= 0 ? 0 : Math.min(1, since / 60e-9);
      }
      isw.push([t * 1e9, cur]);
    }

    const f = kit.frame(ctx, w, h, {
      xRange: [0, Tspan * 1e9], yRange: [-0.6, 1.5], xTicks: 4, yTicks: 4,
      margin: { l: 44, r: 14, t: 14, b: 30 },
    });
    f.hline(0, f.P.line);
    f.line(isw, f.P.blue, 1.6);
    f.line(vds, soft ? f.P.accent : f.P.amber, 2);
    f.text('V\u2091\u209b', f.x0 + 6, f.y0 + 13, soft ? f.P.accent : f.P.amber);
    f.text('I\u209b\u1d65\u1d65', f.x0 + 44, f.y0 + 13, f.P.blue);
    f.text('ns', f.x1 - 6, f.y1 + 20, f.P.faint, 'right');
  },
  explain: function (v) {
    const L = v.ls * 1e-9, C = v.coss * 1e-12;
    const fr = 1 / (2 * Math.PI * Math.sqrt(L * C));
    const tSwing = (Math.PI / 2) / (1 / Math.sqrt(L * C));
    const soft = v.dead * 1e-9 >= tSwing * 0.95;
    return 'The parasitic tank rings at <b>' + (fr / 1e6).toFixed(1) + ' MHz</b> and needs <b>' +
      (tSwing * 1e9).toFixed(0) + ' ns</b> to swing the drain to zero. ' +
      (soft
        ? 'Your dead time covers it, so the device turns on at zero volts \u2014 no CV\u00b2f loss and no ringing.'
        : 'Your dead time is shorter than that, so the device turns on into a charged capacitance: the energy \u00bdCV\u00b2 is dissipated every cycle and the loop rings.');
  },
});

/* the Smith chart: impedance matching as motion on a circle */
Sandbox.define({
  id: 'smith',
  title: 'Matching on the Smith chart',
  params: [
    { k: 'rl', label: 'load R', min: 2, max: 300, step: 1, def: 100, unit: '\u03a9' },
    { k: 'xl', label: 'load X', min: -200, max: 200, step: 1, def: 60, unit: '\u03a9' },
    { k: 'len', label: 'line length', min: 0, max: 0.5, step: 0.005, def: 0, unit: '\u03bb' },
  ],
  draw: function (ctx, w, h, v, kit) {
    const P = kit.palette();
    const Z0 = 50;
    const R = Math.min(w, h) / 2 - 22;
    const cx = w / 2, cy = h / 2;

    function plot(re, im) { return [cx + re * R, cy - im * R]; }

    /* constant-resistance and constant-reactance circles */
    ctx.strokeStyle = P.line; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, Math.PI * 2); ctx.stroke();
    [0.2, 0.5, 1, 2, 5].forEach(function (r) {
      const c = r / (1 + r), rad = 1 / (1 + r);
      ctx.beginPath();
      ctx.arc(cx + c * R, cy, rad * R, 0, Math.PI * 2);
      ctx.stroke();
    });
    [0.2, 0.5, 1, 2, 5].forEach(function (x) {
      [1, -1].forEach(function (sgn) {
        const rad = R / x;
        ctx.save();
        ctx.beginPath();
        ctx.arc(cx + R, cy - sgn * rad, rad, 0, Math.PI * 2);
        ctx.clip();
        ctx.beginPath();
        ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
        ctx.save();
        ctx.beginPath();
        ctx.arc(cx, cy, R, 0, Math.PI * 2);
        ctx.clip();
        ctx.beginPath();
        ctx.arc(cx + R, cy - sgn * rad, rad, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      });
    });
    ctx.strokeStyle = P.dim;
    ctx.beginPath(); ctx.moveTo(cx - R, cy); ctx.lineTo(cx + R, cy); ctx.stroke();

    /* the load, and where a length of line moves it */
    const zr = v.rl / Z0, zi = v.xl / Z0;
    const den = (zr + 1) * (zr + 1) + zi * zi;
    let gr = ((zr - 1) * (zr + 1) + zi * zi) / den;
    let gi = (2 * zi) / den;
    const mag = Math.hypot(gr, gi);
    const ang0 = Math.atan2(gi, gr);
    const ang = ang0 - 4 * Math.PI * v.len;
    const mr = mag * Math.cos(ang), mi = mag * Math.sin(ang);

    /* the constant-VSWR circle the line travels along */
    ctx.save();
    ctx.setLineDash([3, 4]);
    ctx.strokeStyle = P.purple;
    ctx.beginPath(); ctx.arc(cx, cy, mag * R, 0, Math.PI * 2); ctx.stroke();
    ctx.restore();

    const a = plot(gr, gi), b = plot(mr, mi);
    ctx.fillStyle = P.dim;
    ctx.beginPath(); ctx.arc(a[0], a[1], 4, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = P.accent;
    ctx.beginPath(); ctx.arc(b[0], b[1], 5.5, 0, Math.PI * 2); ctx.fill();
    ctx.font = '11px ui-monospace, monospace';
    ctx.fillStyle = P.faint;
    ctx.fillText('centre = 50 \u03a9', 8, h - 8);
  },
  explain: function (v) {
    const Z0 = 50;
    const zr = v.rl / Z0, zi = v.xl / Z0;
    const den = (zr + 1) * (zr + 1) + zi * zi;
    const gr = ((zr - 1) * (zr + 1) + zi * zi) / den;
    const gi = (2 * zi) / den;
    const mag = Math.hypot(gr, gi);
    const vswr = (1 + mag) / (1 - mag);
    return '|\u0393| = <b>' + mag.toFixed(3) + '</b>, VSWR <b>' + vswr.toFixed(2) + ':1</b>, ' +
      'return loss ' + (-20 * Math.log10(Math.max(mag, 1e-6))).toFixed(1) + ' dB. ' +
      'A length of lossless line rotates you clockwise on the dashed circle without ever ' +
      'changing its radius \u2014 line alone can never match a load, only move where the mismatch sits.';
  },
});

/* a pipeline you can watch stall */
Sandbox.define({
  id: 'pipeline',
  title: 'Pipeline hazards and what they cost',
  params: [
    { k: 'dep', label: 'dependent pairs', min: 0, max: 6, step: 1, def: 3 },
    { k: 'fwd', label: 'forwarding on', min: 0, max: 1, step: 1, def: 0, fmt: function (x) { return x ? 'yes' : 'no'; } },
    { k: 'miss', label: 'branch mispredicts', min: 0, max: 4, step: 1, def: 1 },
  ],
  draw: function (ctx, w, h, v, kit) {
    const P = kit.palette();
    const STAGES = ['IF', 'ID', 'EX', 'ME', 'WB'];
    const N = 9;
    /* build a schedule: each instruction starts one cycle after the last, plus stalls */
    const start = [];
    let t = 0, stalls = 0, flushes = 0;
    for (let i = 0; i < N; i++) {
      let extra = 0;
      if (i > 0 && i <= v.dep) extra = v.fwd ? 0 : 2;
      if (v.miss && i > 0 && i % 3 === 0 && flushes < v.miss) { extra += 2; flushes++; }
      stalls += extra;
      t += 1 + extra;
      start.push(t);
    }
    const total = start[N - 1] + STAGES.length;
    const cellW = Math.max(14, Math.min(30, (w - 92) / total));
    const cellH = Math.max(13, Math.min(22, (h - 46) / N));
    const x0 = 78, y0 = 28;

    ctx.font = '10px ui-monospace, monospace';
    ctx.textBaseline = 'middle';
    for (let i = 0; i < N; i++) {
      const y = y0 + i * (cellH + 3);
      ctx.fillStyle = P.faint;
      ctx.textAlign = 'right';
      ctx.fillText('i' + i, x0 - 8, y + cellH / 2);

      /* The bubbles themselves. The schedule shifted each stalled instruction to the
         right and drew nothing in the gap, so the cost the caption talks about was
         only ever visible as a wider staircase \u2014 the one thing a pipeline diagram
         exists to show was the one thing missing from it. */
      const held = start[i] - (i > 0 ? start[i - 1] + 1 : 1);
      for (let b = 0; b < held; b++) {
        const x = x0 + (start[i] - held + b) * cellW;
        ctx.save();
        ctx.globalAlpha = 0.5;
        ctx.strokeStyle = P.amber;
        ctx.setLineDash([2, 2]);
        ctx.strokeRect(x + 0.5, y + 0.5, cellW - 3, cellH - 1);
        ctx.restore();
        if (cellW > 18) {
          ctx.fillStyle = P.amber;
          ctx.textAlign = 'center';
          ctx.fillText('\u2013', x + (cellW - 2) / 2, y + cellH / 2);
        }
      }

      for (let sIdx = 0; sIdx < STAGES.length; sIdx++) {
        const x = x0 + (start[i] + sIdx) * cellW;
        /* the tint was a baked copy of --lime, which is a light-theme bug waiting for
           the day the token moves and this does not */
        ctx.save();
        ctx.globalAlpha = sIdx === 2 ? 0.22 : 0.06;
        ctx.fillStyle = sIdx === 2 ? P.accent : P.ink;
        ctx.fillRect(x, y, cellW - 2, cellH);
        ctx.restore();
        ctx.fillStyle = sIdx === 2 ? P.accent : P.dim;
        ctx.textAlign = 'center';
        if (cellW > 18) ctx.fillText(STAGES[sIdx], x + (cellW - 2) / 2, y + cellH / 2);
      }
    }
    ctx.textAlign = 'left';
    ctx.fillStyle = P.faint;
    ctx.fillText('cycles \u2192', x0, 14);
    if (stalls) {
      ctx.fillStyle = P.amber;
      ctx.fillText(stalls + ' bubble' + (stalls === 1 ? '' : 's'), x0 + 62, 14);
    }
  },
  explain: function (v) {
    const N = 9;
    const dep = v.fwd ? 0 : v.dep * 2;
    const br = Math.min(v.miss, 2) * 2;
    const cycles = N + 4 + dep + br;
    const cpi = cycles / N;
    return '<b>' + cycles + ' cycles</b> for ' + N + ' instructions \u2014 CPI ' + cpi.toFixed(2) + '. ' +
      (v.fwd
        ? 'Forwarding removes the data hazard entirely: the value goes EX\u2192EX without ever visiting the register file.'
        : 'Each dependent pair costs two bubbles, because the register write happens in WB and the read in ID.') +
      ' A mispredict costs the whole front end.';
  },
});

const CACHE_MEMO = {};
/* A fixed working set, so growing the cache genuinely starts to hold it and the
   miss rate falls. Scaling the set with the cache kept the ratio constant, the curve
   dead flat, and every caption about capacity misses "starting to fit" false. */
const WORKING_SET = 32 * 1024;
const CACHE_LINE = 64;

/* The model lives out here, above both draw() and explain(), because it used to live
   inside draw() and explain() then re-derived its claims from the slider positions
   instead. The two disagreed: at 4 KB with a 512-byte stride the marker read 100% while
   the sentence under it said "only the compulsory miss on first touch — the floor no
   cache can go below". Everything the caption now asserts is measured on the same walk
   the curve is drawn from. */

/* Consecutive addresses inside one 64-byte line are guaranteed hits after the first:
   the line was just installed, so it is present and most-recently-used in its set.
   Simulating one access per run of them and counting the rest gives an identical answer
   for a sixty-fourth of the work — checked exhaustively against the address-by-address
   version over every (size, associativity, stride) the sliders reach. It matters because
   a stride-1 repaint took 627 ms, and the stride slider steps by 1 across 1..512: the
   whole left-hand end of it redrew about once a second. */
function cacheRun(setCount, assoc, stride) {
  const tags = [];
  for (let i = 0; i < setCount; i++) tags.push([]);
  let hits = 0, total = 0;
  for (let pass = 0; pass < 3; pass++) {
    let addr = 0;
    while (addr < WORKING_SET) {
      const line = Math.floor(addr / CACHE_LINE);
      const lineEnd = Math.min(WORKING_SET, (line + 1) * CACHE_LINE);
      const runLen = Math.ceil((lineEnd - addr) / stride);
      const arr = tags[line % setCount];
      const tag = Math.floor(line / setCount);
      const at = arr.indexOf(tag);
      total += runLen;
      if (at !== -1) { hits += runLen; arr.splice(at, 1); arr.push(tag); }
      else { hits += runLen - 1; arr.push(tag); if (arr.length > assoc) arr.shift(); }
      addr += runLen * stride;
    }
  }
  return total ? hits / total : 0;
}

/* the miss rate the marker sits at, from the slider positions the picture uses */
function cacheMiss(kb, ways, stride) {
  const assoc = Math.max(1, Math.round(ways));
  const lines = Math.max(assoc, Math.floor(kb * 1024 / CACHE_LINE));
  return (1 - cacheRun(Math.max(1, Math.floor(lines / assoc)), assoc, stride)) * 100;
}

/* the same capacity with no placement restriction at all — the textbook definition of
   the line between a conflict miss and the rest */
function cacheIdeal(kb, stride) {
  const lines = Math.max(1, Math.floor(kb * 1024 / CACHE_LINE));
  return (1 - cacheRun(1, lines, stride)) * 100;
}

/* one miss per distinct line on first touch, over the accesses actually made: what a
   cache of unbounded size would still pay */
function cacheFloor(stride) {
  let lines = 0, accesses = 0, addr = 0, last = -1;
  while (addr < WORKING_SET) {
    const line = Math.floor(addr / CACHE_LINE);
    if (line !== last) { lines++; last = line; }
    accesses++;
    addr += stride;
  }
  return accesses ? lines / (accesses * 3) * 100 : 0;
}
/* a cache you can starve: capacity against associativity, on a real trace */
Sandbox.define({
  id: 'cache',
  title: 'Capacity, associativity and the miss rate',
  params: [
    { k: 'kb', label: 'cache size', min: 1, max: 64, step: 1, def: 8, unit: 'KB' },
    { k: 'ways', label: 'associativity', min: 1, max: 16, step: 1, def: 1,
      fmt: function (x) { return x === 1 ? 'direct' : x + '-way'; } },
    { k: 'stride', label: 'access stride', min: 1, max: 512, step: 1, def: 64, unit: 'B' },
  ],
  draw: function (ctx, w, h, v, kit) {
    const ways = Math.max(1, Math.round(v.ways));

    /* A curve depends only on (associativity, stride) — dragging the size slider
       moves the marker along one that is already computed. Without the memo every
       frame re-simulated four full sweeps and the slider felt broken. */
    function sweep(assoc) {
      const key = assoc + ':' + v.stride;
      if (CACHE_MEMO[key]) return CACHE_MEMO[key];
      const out = [];
      for (let k = 1; k <= 64; k++) out.push([k, cacheMiss(k, assoc, v.stride)]);
      if (Object.keys(CACHE_MEMO).length > 60) for (const k in CACHE_MEMO) delete CACHE_MEMO[k];
      CACHE_MEMO[key] = out;
      return out;
    }
    const pts = sweep(ways);
    const here = cacheMiss(v.kb, ways, v.stride);

    const f = kit.frame(ctx, w, h, {
      xRange: [1, 64], yRange: [0, 105], xTicks: 4, yTicks: 4,
      margin: { l: 46, r: 14, t: 14, b: 30 },
    });
    /* the other associativities, faintly, for comparison */
    ctx.save();
    ctx.globalAlpha = 0.32;
    [1, 4, 16].forEach(function (a, i) {
      if (a === ways) return;
      f.line(sweep(a), [f.P.blue, f.P.purple, f.P.amber][i], 1.2);
    });
    ctx.restore();
    f.line(pts, f.P.accent, 2);
    f.dot(v.kb, here, f.P.accent, 5);
    f.text('miss rate %', f.x0 + 6, f.y0 + 13, f.P.faint);
    f.text('cache size KB', f.x1 - 6, f.y1 + 20, f.P.faint, 'right');
  },
  /* The three C's, decomposed by running the same trace three ways rather than deduced
     from where the sliders happen to be. The version that deduced them managed to tell
     a learner they were sitting on "the floor no cache can go below" while the marker
     six inches above read 100%. */
  explain: function (v) {
    const ways = Math.max(1, Math.round(v.ways));
    const here = cacheMiss(v.kb, ways, v.stride);
    const ideal = cacheIdeal(v.kb, v.stride);
    const floor = cacheFloor(v.stride);
    const capacity = Math.max(0, ideal - floor);
    const conflict = Math.max(0, here - ideal);
    const pc = function (x) { return x.toFixed(x < 9.995 ? 2 : 1) + '%'; };
    const head = 'Miss rate <b>' + pc(here) + '</b> \u2014 ' + pc(floor) + ' compulsory, ' +
      pc(capacity) + ' capacity, ' + pc(conflict) + ' conflict, split by running this same walk ' +
      'against an unbounded cache and against a fully associative one of this size. ';

    if (conflict > 0.05 && conflict >= capacity) {
      return head + 'Most of it is <b>conflict</b>: the same capacity with no placement ' +
        'restriction reads ' + pc(ideal) + '. Associativity is the lever here, not size.';
    }
    if (capacity > 0.05) {
      return head + 'Most of it is <b>capacity</b> \u2014 the walk touches more lines than fit, ' +
        'so each one is evicted before it comes round again. Only a bigger cache moves this.';
    }
    return head + 'There is nothing left to remove: every miss is a line being read for the ' +
      'first time. The stride uses ' + Math.min(v.stride, CACHE_LINE) + ' of every ' + CACHE_LINE +
      ' bytes fetched, and no cache buys back bytes the walk never asks for.';
  },
});
