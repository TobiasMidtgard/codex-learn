/* mathinput.js — type mathematics the way you would say it.
 *
 * The derivation input used to demand LaTeX. Its own placeholder read
 * "your expression in LaTeX, e.g. \frac{a}{b + c}", which asks a first-year student
 * working out how many carriers sit in a slug of wire to first learn a typesetting
 * language. The mathematics was never the hard part of that step.
 *
 * So: type `(a+b)/c` and see a fraction; type `x^2` and see a superscript; type
 * `sqrt(x)` and see a radical. The expression is parsed to a tree and the tree is
 * printed as LaTeX, which is what both halves of the existing machinery already
 * speak — MathML.render draws it, MathCheck.latexToPy hands it to SymPy. Nothing
 * downstream had to change.
 *
 * Anything containing a backslash is passed through untouched. Someone who already
 * knows LaTeX, and every answer already authored in the catalog, keeps working.
 *
 * IMPLICIT MULTIPLICATION is the one genuinely ambiguous case: `nAL` could be one
 * symbol or three multiplied. A derivation declares its own symbols in `vars`, so
 * the tokeniser is told them and matches longest-first. `nAL` with vars n, A, L is a
 * product; with a var named `nAL` it is that symbol. Without a symbol table it falls
 * back to single letters, which is the convention in every algebra course.
 */
const MathInput = (function () {

  const GREEK = ['alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
    'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'rho', 'sigma', 'tau', 'upsilon',
    'phi', 'chi', 'psi', 'omega', 'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi',
    'Sigma', 'Phi', 'Psi', 'Omega'];

  /* Printed with a backslash and their own spacing, so `sin x` does not come out as
     the product of three symbols. */
  const FUNCS = ['sin', 'cos', 'tan', 'asin', 'acos', 'atan', 'sinh', 'cosh', 'tanh',
    'ln', 'log', 'exp', 'sqrt', 'abs', 'min', 'max', 'det'];

  const CONSTS = { pi: '\\pi', inf: '\\infty', infinity: '\\infty', infty: '\\infty' };

  function isAlpha(c) { return /[A-Za-z]/.test(c); }
  function isDigit(c) { return /[0-9]/.test(c); }

  /* ---------------------------------------------------------------- tokeniser */
  function lex(src, vars) {
    const names = (vars || []).slice().sort(function (a, b) { return b.length - a.length; });
    const out = [];
    let i = 0;
    while (i < src.length) {
      const c = src[i];
      if (c === ' ' || c === '\t') { i++; continue; }

      if (isDigit(c) || (c === '.' && isDigit(src[i + 1]))) {
        let j = i;
        while (j < src.length && (isDigit(src[j]) || src[j] === '.')) j++;
        out.push({ t: 'num', v: src.slice(i, j) });
        i = j;
        continue;
      }

      if (isAlpha(c)) {
        /* a declared symbol, longest first, so `nAL` splits only where it must */
        let hit = null;
        for (const nm of names) {
          if (src.startsWith(nm, i) && !isAlpha(src[i + nm.length] || '')) { hit = nm; break; }
        }
        if (!hit) {
          let j = i;
          while (j < src.length && isAlpha(src[j])) j++;
          const word = src.slice(i, j);
          const lower = word.toLowerCase();
          if (FUNCS.indexOf(lower) >= 0 || CONSTS[lower] || GREEK.indexOf(word) >= 0) hit = word;
          else if (names.length) hit = src[i];          /* symbols were declared: one letter */
          else hit = word.length <= 2 ? word : src[i];  /* none declared: single letters */
        }
        i += hit.length;
        /* a trailing _1 or _{n+1} belongs to the name */
        let sub = '';
        if (src[i] === '_') {
          i++;
          if (src[i] === '{') {
            let d = 1, j = i + 1;
            while (j < src.length && d) { if (src[j] === '{') d++; if (src[j] === '}') d--; j++; }
            sub = src.slice(i + 1, j - 1);
            i = j;
          } else {
            let j = i;
            while (j < src.length && /[A-Za-z0-9]/.test(src[j])) j++;
            sub = src.slice(i, j);
            i = j;
          }
        }
        out.push({ t: 'name', v: hit, sub: sub });
        continue;
      }

      const two = src.substr(i, 2);
      if (two === '<=' || two === '>=' || two === '!=' || two === '**') {
        out.push({ t: 'op', v: two === '**' ? '^' : two });
        i += 2;
        continue;
      }
      if ('+-*/^()=<>,|'.indexOf(c) >= 0) { out.push({ t: 'op', v: c }); i++; continue; }
      /* Anything else is passed through as itself rather than rejected: a stray
         character should not blank the preview while someone is mid-word. */
      out.push({ t: 'raw', v: c });
      i++;
    }
    return out;
  }

  /* ---------------------------------------------------------------- parser */
  function parse(toks) {
    let p = 0;
    const peek = function () { return toks[p]; };
    const eat = function (v) {
      const t = toks[p];
      if (t && t.t === 'op' && t.v === v) { p++; return true; }
      return false;
    };

    function relation() {
      let l = add();
      const t = peek();
      if (t && t.t === 'op' && ['=', '<', '>', '<=', '>=', '!='].indexOf(t.v) >= 0) {
        p++;
        return { k: 'rel', op: t.v, a: l, b: relation() };
      }
      return l;
    }

    function add() {
      let l = mul();
      for (;;) {
        if (eat('+')) l = { k: 'bin', op: '+', a: l, b: mul() };
        else if (eat('-')) l = { k: 'bin', op: '-', a: l, b: mul() };
        else return l;
      }
    }

    function mul() {
      let l = unary();
      for (;;) {
        if (eat('*')) { l = { k: 'bin', op: '*', a: l, b: unary() }; continue; }
        if (eat('/')) { l = { k: 'frac', a: l, b: unary() }; continue; }
        /* juxtaposition: `2x`, `n A L`, `(a+b)(c+d)` */
        const t = peek();
        if (t && (t.t === 'num' || t.t === 'name' || (t.t === 'op' && t.v === '('))) {
          l = { k: 'bin', op: ' ', a: l, b: unary() };
          continue;
        }
        return l;
      }
    }

    function unary() {
      if (eat('-')) return { k: 'neg', a: unary() };
      if (eat('+')) return unary();
      return power();
    }

    function power() {
      const b = atom();
      if (eat('^')) return { k: 'pow', a: b, b: unary() };
      return b;
    }

    function atom() {
      const t = peek();
      if (!t) return { k: 'empty' };
      if (t.t === 'num') { p++; return { k: 'num', v: t.v }; }
      if (t.t === 'raw') { p++; return { k: 'raw', v: t.v }; }
      if (t.t === 'name') {
        p++;
        const lower = String(t.v).toLowerCase();
        if (FUNCS.indexOf(lower) >= 0 && peek() && peek().t === 'op' && peek().v === '(') {
          p++;
          const arg = relation();
          eat(')');
          return { k: 'call', fn: lower, a: arg };
        }
        return { k: 'name', v: t.v, sub: t.sub };
      }
      if (t.t === 'op' && t.v === '(') {
        p++;
        const inner = relation();
        eat(')');
        return { k: 'group', a: inner };
      }
      if (t.t === 'op' && t.v === '|') {
        p++;
        const inner = relation();
        eat('|');
        return { k: 'call', fn: 'abs', a: inner };
      }
      p++;                       /* an unmatched operator: show it, do not stall */
      return { k: 'raw', v: t.v };
    }

    const tree = relation();
    return tree;
  }

  /* ---------------------------------------------------------------- to LaTeX */
  function nameTex(v, sub) {
    let base;
    const lower = String(v).toLowerCase();
    if (GREEK.indexOf(v) >= 0) base = '\\' + v;
    else if (CONSTS[lower]) base = CONSTS[lower];
    else if (FUNCS.indexOf(lower) >= 0) base = '\\operatorname{' + lower + '}';
    else base = v;
    /* A subscript is a LABEL, not an expression. Parsing it split `v_drift` into
       a product of five letters. */
    return sub ? base + '_{\\mathrm{' + sub + '}}' : base;
  }

  const REL = { '<=': '\\le ', '>=': '\\ge ', '!=': '\\ne ', '=': '=', '<': '<', '>': '>' };

  function tex(n) {
    if (!n) return '';
    switch (n.k) {
      case 'empty': return '';
      case 'num': return n.v;
      case 'raw': return n.v === '&' ? '\\&' : n.v;
      case 'name': return nameTex(n.v, n.sub);
      case 'group': return '\\left(' + tex(n.a) + '\\right)';
      case 'neg': return '-' + tex(n.a);
      case 'rel': return tex(n.a) + ' ' + (REL[n.op] || n.op) + ' ' + tex(n.b);
      case 'frac': return '\\frac{' + bare(n.a) + '}{' + bare(n.b) + '}';
      case 'pow': return texAtom(n.a) + '^{' + bare(n.b) + '}';
      case 'call':
        if (n.fn === 'sqrt') return '\\sqrt{' + bare(n.a) + '}';
        if (n.fn === 'abs') return '\\left|' + tex(n.a) + '\\right|';
        if (n.fn === 'exp') return 'e^{' + tex(n.a) + '}';
        return '\\' + n.fn + '\\left(' + tex(n.a) + '\\right)';
      case 'bin':
        if (n.op === '*') return tex(n.a) + ' \\cdot ' + tex(n.b);
        if (n.op === ' ') return tex(n.a) + '\\,' + tex(n.b);
        return tex(n.a) + ' ' + n.op + ' ' + tex(n.b);
      default: return '';
    }
  }

  /* Inside a fraction, a radical or a superscript the delimiter already groups, so
     a bracket the writer typed there is noise: 1/(2*pi*r) should print as a
     fraction over 2*pi*r, not over (2*pi*r). */
  function bare(n) { return n && n.k === 'group' ? tex(n.a) : tex(n); }

  /* A power's base needs bracketing when it is not already a single thing, or
     `a+b^2` and `(a+b)^2` would print identically. */
  function texAtom(n) {
    if (n && (n.k === 'num' || n.k === 'name' || n.k === 'group' || n.k === 'call')) return tex(n);
    return '\\left(' + tex(n) + '\\right)';
  }

  /* ---------------------------------------------------------------- outside */
  function toLatex(src, vars) {
    const s = String(src == null ? '' : src);
    if (!s.trim()) return '';
    /* Already LaTeX: leave it entirely alone. Every answer in the catalog is
       authored this way, and someone who knows the language should not have it
       rewritten under them. */
    if (s.indexOf('\\') >= 0) return s;
    try { return tex(parse(lex(s, vars))); } catch (e) { return s; }
  }

  return { toLatex: toLatex, FUNCS: FUNCS, GREEK: GREEK };
})();
