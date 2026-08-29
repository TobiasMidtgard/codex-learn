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
  const GREEK_NAMES = ['alpha','beta','gamma','delta','epsilon','zeta','eta','theta',
    'iota','kappa','lambda','mu','nu','xi','rho','sigma','tau','upsilon','phi','chi',
    'psi','omega','Gamma','Delta','Theta','Lambda','Xi','Pi','Sigma','Phi','Psi','Omega'];

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

    /* now the argument-taking commands, innermost first so nesting resolves */
    for (let g = 0; g < 12; g++) {
      const next = t.replace(/\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}/g, ' (($1)/($2)) ');
      if (next === t) break;
      t = next;
    }
    for (let g = 0; g < 12; g++) {
      const next = t
        .replace(/\\sqrt\s*\[([^\]]*)\]\s*\{([^{}]*)\}/g, ' (($2)**(1/($1))) ')
        .replace(/\\sqrt\s*\{([^{}]*)\}/g, ' sqrt($1) ');
      if (next === t) break;
      t = next;
    }
    for (let g = 0; g < 8; g++) {
      const next = t.replace(/\\(?:mathrm|mathbf|mathit|text|operatorname)\s*\{([^{}]*)\}/g, ' $1 ');
      if (next === t) break;
      t = next;
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
    'pi', 'oo', 'I', 'E'];

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
      '_names = ' + JSON.stringify(vars || []),
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
