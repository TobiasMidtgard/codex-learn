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
    /* lambda is the obvious symbol for an eigenvalue and a syntax error in Python.
       Both sides get the same rewrite, so equivalence is unaffected. */
    PY_RESERVED.forEach(function (kw) {
      t = t.replace(new RegExp('\\b' + kw + '\\b', 'g'), kw + '_');
    });
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
        if (!name) name = (/^[A-Za-z](?:_[A-Za-z0-9]+)?/.exec(text.slice(i)) || ['x'])[0];
        const rest = text.slice(i + name.length);
        const isFn = KEEP_WHOLE.indexOf(name) !== -1 && /^\s*\(/.test(rest);
        toks.push({ t: isFn ? 'fn' : 'val', v: name });
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
    return {
      ink: v('--ink', '#EDEFF3'),
      dim: v('--ink-4', '#565C68'),
      faint: v('--ink-5', '#3A3F49'),
      line: v('--line-2', 'rgba(255,255,255,.1)'),
      accent: v('--lime', '#C7F751'),
      blue: v('--blue', '#6E9BFF'),
      purple: v('--purple', '#A78BFA'),
      amber: v('--amber', '#FFC66D'),
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

  /* ---- mount ----
     Returns a handle with dispose(); the caller must put that in `teardown`,
     because go() clears exactly one slot and nothing drains teardownFns. */
  function mount(host, spec, initial, onChange) {
    const values = Object.assign({}, initial || {});
    spec.params.forEach(function (p) {
      if (values[p.k] === undefined) values[p.k] = p.def;
    });

    host.innerHTML =
      '<div class="sbx">' +
        '<div class="sbx-canvas"><canvas></canvas></div>' +
        '<div class="sbx-side">' +
          '<div class="sbx-params">' +
            spec.params.map(function (p) {
              return '<label class="sbx-p" data-k="' + p.k + '">' +
                '<span class="sbx-l">' + (p.label || p.k) + '</span>' +
                '<span class="sbx-v" data-v="' + p.k + '"></span>' +
                '<input type="range" min="' + p.min + '" max="' + p.max + '" ' +
                  'step="' + (p.step || (p.max - p.min) / 100) + '" value="' + values[p.k] + '">' +
              '</label>';
            }).join('') +
          '</div>' +
          '<div class="sbx-read" data-read></div>' +
        '</div>' +
      '</div>';

    const cv = host.querySelector('canvas');
    const ctx = cv.getContext('2d');
    const readout = host.querySelector('[data-read]');
    let raf = 0, ro = null, disposed = false;

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
        const el = host.querySelector('[data-v="' + p.k + '"]');
        if (el) el.textContent = (p.fmt ? p.fmt(values[p.k]) : fmt(values[p.k])) + (p.unit ? ' ' + p.unit : '');
      });
      if (readout && spec.explain) {
        try { readout.innerHTML = spec.explain(values, MathML); } catch (e) { readout.textContent = ''; }
      }
      if (onChange) onChange(values);
    }

    function schedule() {
      if (raf || disposed) return;
      raf = requestAnimationFrame(function () { raf = 0; paint(); });
    }

    host.querySelectorAll('input[type=range]').forEach(function (inp) {
      const k = inp.closest('.sbx-p').dataset.k;
      inp.addEventListener('input', function () { values[k] = parseFloat(inp.value); schedule(); });
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

  return { define: define, get: get, mount: mount, frame: frame, palette: palette, fmt: fmt, all: REG };
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

    /* left: the s-plane */
    ctx.save();
    ctx.beginPath(); ctx.rect(0, 0, half, h); ctx.clip();
    const sp = kit.frame(ctx, half, h, {
      xRange: [-14, 4], yRange: [-14, 14], xTicks: 4, yTicks: 4, margin: { l: 40, r: 10, t: 14, b: 28 },
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

    ctx.save();
    ctx.beginPath(); ctx.rect(0, 0, w, topH); ctx.clip();
    const g = kit.frame(ctx, w, topH, {
      xRange: [lo, hi], yRange: [-80, 40], logX: true, xTicks: 4, yTicks: 3,
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
    if (v.r < 1.001) return 'Exactly on the circle: it oscillates forever and never settles. Marginally stable.';
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
    for (let k = 0; k < 8; k++) {
      const th = k / 8 * Math.PI * 2;
      let x = 2.7 * Math.cos(th), y = 2.7 * Math.sin(th);
      const pts = [[x, y]];
      const dt = 0.012;
      for (let n = 0; n < 1400; n++) {
        const dx = A[0][0] * x + A[0][1] * y, dy = A[1][0] * x + A[1][1] * y;
        x += dx * dt; y += dy * dt;
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
    return 'trace = ' + tr.toFixed(2) + ', det = ' + det.toFixed(2) + ' \u2014 ' + kind +
      '. Stability is decided entirely by those two numbers, never by the individual entries.';
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
    /* a fixed pseudo-random stream so the picture is stable while a slider moves */
    let seed = 12345;
    const rnd = function () {
      seed = (seed * 1103515245 + 12345) & 0x7fffffff;
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
    ctx._err = [Math.sqrt(sumErrM / N), Math.sqrt(sumErrE / N)];
  },
  explain: function (v) {
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
    let fa = Math.abs(v.fsig % v.fs);
    if (fa > v.fs / 2) fa = v.fs - fa;
    if (Math.abs(fa - v.fsig) < 0.5) {
      return 'Below the Nyquist limit of <b>' + (v.fs / 2).toFixed(0) + ' Hz</b>, so the samples ' +
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
    { k: 'fc', label: '1/f corner', min: 1, max: 100000, step: 100, def: 10000, unit: 'Hz' },
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
    f.text('corner', f.fx(v.fc) + 5, f.y0 + 13, f.P.purple);
    f.text('thermal floor', f.x0 + 6, f.fy(20 * Math.log10(v.nth)) - 6, f.P.faint);
    f.text('dB re 1 nV/\u221aHz', f.x0 + 6, f.y0 + 13, f.P.faint);
    f.text('Hz', f.x1 - 6, f.y1 + 20, f.P.faint, 'right');
  },
  explain: function (v) {
    return 'Below the corner the noise rises as 1/f and integrating for longer stops helping \u2014 ' +
      'this is the region chopping and correlated double sampling exist for. Above it the floor ' +
      'is flat at <b>' + v.nth.toFixed(1) + ' nV/\u221aHz</b>, set by resistance and temperature, ' +
      'and the only lever left is a wider device or more current.';
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
    const fr = wr / (2 * Math.PI);
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
      const cur = t < 100e-9 ? 0 : (soft ? Math.min(1, (t - 100e-9) / 60e-9) : 1);
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
      for (let sIdx = 0; sIdx < STAGES.length; sIdx++) {
        const c = start[i] + sIdx;
        const x = x0 + c * cellW;
        const stalled = i > 0 && i <= v.dep && !v.fwd && sIdx === 0;
        ctx.fillStyle = sIdx === 2 ? 'rgba(199,247,81,.22)' : 'rgba(255,255,255,.06)';
        ctx.fillRect(x, y, cellW - 2, cellH);
        ctx.fillStyle = sIdx === 2 ? P.accent : P.dim;
        ctx.textAlign = 'center';
        if (cellW > 18) ctx.fillText(STAGES[sIdx], x + (cellW - 2) / 2, y + cellH / 2);
      }
    }
    ctx.textAlign = 'left';
    ctx.fillStyle = P.faint;
    ctx.fillText('cycles \u2192', x0, 14);
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
