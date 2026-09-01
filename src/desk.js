/* ============ the desk ============
 *
 * A notepad and a calculator that open as a modal over whatever the learner is
 * doing. Working a problem should not mean leaving the page, opening a tab, or
 * reaching for a pocket calculator that has never heard of a kilohm.
 *
 *   Calc    a real expression language — engineering suffixes both ways, a
 *           parallel operator, variables, `ans`, and a clickable history
 *   Notes   plain text, autosaved, one pad per lesson plus a scratch pad that
 *           is always there; a result crosses from the calculator in one click
 *
 * The parser is a hand-written tokeniser and recursive-descent parser. Not eval,
 * and not `new Function`: this is a text box on a learning platform, and an
 * expression language we own is also the only way to get `||` and `4k7` at all —
 * neither is JavaScript, and `4k7` is not even a JavaScript token.
 *
 * This is the one file in the codebase that carries its own CSS. Everything else
 * keeps style in src/index.head.html, but a modal that is inert until summoned
 * pays for none of it until it is opened, and injecting on first open keeps the
 * whole feature in one file.
 *
 * Public surface — one global:
 *
 *   Desk.open(tab)      'calc' | 'notes'   (default: the tab last used)
 *   Desk.close()
 *   Desk.toggle()
 *   Desk.isOpen()
 *   Desk.context(info)  { lessonId, title } — what the learner is on now
 *   Desk.evaluate(src)  the parser, headless: { ok, value, display, error }
 *   Desk.format(v,unit) engineering notation, the same as the schematics use
 */

const Desk = (function () {

  const K_NOTES = 'codex-desk-notes-v1';   /* { scratch, lessons: { id: {...} } } */
  const K_STATE = 'codex-desk-state-v1';   /* tab, angle mode, vars, history, geometry */

  const HIST_MAX = 80;
  const SAVE_MS = 700;

  /* Two limits the language did not have, and both of them are storage limits as much
     as parser ones. A history row keeps the source it was worked out from, and eighty
     of them are serialised into localStorage on every result — so an expression with
     no ceiling is a store with no ceiling. And the parser is recursive descent with
     about eight frames per bracket, so deep enough input reached the engine's own
     limit and the learner was shown "Maximum call stack size exceeded" as the
     explanation of their sum. Refusing is the fix; truncating is not, because a
     silently shortened expression returns a confident wrong answer. */
  const SRC_MAX = 1000;
  const DEPTH_MAX = 64;

  /* ================================================================ numbers */

  /* The suffix table circuit.js parses, plus `K`, because people type it. Both
     micro signs are here: U+00B5 (MICRO SIGN, what a keyboard gives you) and
     U+03BC (GREEK SMALL LETTER MU, what a copy-paste from a datasheet gives you). */
  const SUFFIX = {
    G: 1e9, M: 1e6, k: 1e3, K: 1e3, m: 1e-3,
    u: 1e-6, 'µ': 1e-6, 'μ': 1e-6, n: 1e-9, p: 1e-12,
  };

  /* Engineering notation, mirroring fmtEng in src/circuit.js — including the
     trailing-zero rule, which trims only the zeros AFTER a decimal point. Trimming
     unconditionally once printed a 100 pF capacitor as 1 pF, and a calculator that
     disagrees with the schematic beside it is worse than no calculator.
     When circuit.js is in the bundle we call its copy outright, so the two can
     never drift; the local copy is what keeps this file testable on its own. */
  function deskFmtEng(v, unit) {
    if (v === 0) return '0 ' + unit;
    const a = Math.abs(v);
    const P = [[1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'],
      [1e-6, 'µ'], [1e-9, 'n'], [1e-12, 'p']];
    for (let i = 0; i < P.length; i++) {
      const mul = P[i][0], pre = P[i][1];
      if (a >= mul * 0.999) {
        const s = v / mul;
        let txt = Math.abs(s) >= 100 ? s.toFixed(0)
          : Math.abs(s) >= 10 ? s.toFixed(1) : s.toFixed(2);
        if (txt.indexOf('.') >= 0) txt = txt.replace(/0+$/, '').replace(/\.$/, '');
        return txt + ' ' + pre + unit;
      }
    }
    return v.toExponential(2) + ' ' + unit;
  }

  function format(v, unit) {
    const u = unit === undefined || unit === null ? '' : unit;
    /* typeof on a const still in its temporal dead zone throws, so this is guarded
       rather than tested — it only ever runs after the whole bundle has evaluated,
       but the try costs nothing and makes the order of the two files irrelevant. */
    try {
      if (typeof fmtEng === 'function') return String(fmtEng(v, u)).trim();
    } catch (e) { /* circuit.js is not in this build */ }
    return deskFmtEng(v, u).trim();
  }

  /* The unrounded value, for the dim line under the engineering one. A learner
     checking whether 3.20 k really was 3197.28 should not have to take it on faith. */
  function rawNum(v) {
    if (!isFinite(v)) return String(v);
    if (v === 0) return '0';
    const a = Math.abs(v);
    if (a >= 1e-4 && a < 1e12) {
      let s = v.toPrecision(10);
      if (s.indexOf('e') < 0 && s.indexOf('.') >= 0) s = s.replace(/0+$/, '').replace(/\.$/, '');
      return s;
    }
    /* Ten significant figures here too. This branch carried seven, so the line that
       exists to show the reading behind the rounding was itself rounded three figures
       harder the moment the value left 1e-4..1e12 — and outside that range is where a
       picofarad and a gigahertz live. `2^40` read 1.099512e+12 for 1099511627776. */
    return v.toExponential(9).replace(/0+e/, 'e').replace(/\.e/, 'e');
  }

  /* ================================================================ tokeniser */

  function calcErr(msg, pos) {
    const e = new Error(msg);
    e.calc = true;
    e.pos = pos === undefined ? -1 : pos;
    return e;
  }

  const isDigit = function (c) { return c >= '0' && c <= '9'; };
  const isIdent = function (c) { return c !== undefined && /[A-Za-z_0-9]/.test(c); };
  const isIdentStart = function (c) { return c !== undefined && /[A-Za-z_]/.test(c); };
  const isSpace = function (c) { return c === ' ' || c === '\t' || c === '\n' || c === '\r'; };

  function tokenize(src) {
    const s = String(src);
    const out = [];
    let i = 0;

    while (i < s.length) {
      const c = s[i];

      if (isSpace(c)) { i++; continue; }

      /* a number, possibly with an engineering suffix in either position */
      if (isDigit(c) || (c === '.' && isDigit(s[i + 1]))) {
        const start = i;
        while (isDigit(s[i])) i++;
        let hasDot = false;
        if (s[i] === '.') { hasDot = true; i++; while (isDigit(s[i])) i++; }
        let value = parseFloat(s.slice(start, i));

        const expSign = s[i + 1] === '+' || s[i + 1] === '-';
        if ((s[i] === 'e' || s[i] === 'E') &&
            (isDigit(s[i + 1]) || (expSign && isDigit(s[i + 2])))) {
          i++;
          if (s[i] === '+' || s[i] === '-') i++;
          while (isDigit(s[i])) i++;
          value = parseFloat(s.slice(start, i));
        } else {
          /* An engineering suffix. It may sit against the digits or be separated
             from them by space: `4.7k` and `4.7 k` are the same value, and the
             spaced form is how every schematic and datasheet in this catalog
             writes it. Either way it is a suffix only when what follows it cannot
             continue a name — `2p` and `2 p` are two picofarads, `2pi` and `2 pi`
             are a mistake worth naming rather than silently reading as 2p times
             something. */
          let j = i;
          while (isSpace(s[j])) j++;
          const suf = s[j];
          const after = s[j + 1];
          /* `4k7` puts the rest of the mantissa after the suffix, but only when the
             two are written as one word. Across a space `2 m1` reads as two things,
             and the learner who wants 2.1 m has `2m1` and `2.1 m` to say it with. */
          const rNotation = j === i && isDigit(after);
          if (Object.prototype.hasOwnProperty.call(SUFFIX, suf) &&
              (rNotation || !isIdent(after))) {
            i = j + 1;
            let frac = '';
            while (isDigit(s[i])) { frac += s[i]; i++; }
            if (frac && hasDot) {
              throw calcErr('"' + s.slice(start, i) + '" writes the decimal twice — ' +
                'it is either 4.7k or 4k7, not both', start);
            }
            if (frac) value += parseInt(frac, 10) / Math.pow(10, frac.length);
            value *= SUFFIX[suf];
          }
        }
        out.push({ t: 'num', v: value, text: s.slice(start, i), pos: start });
        continue;
      }

      /* pi may be typed as the letter */
      if (c === 'π') { out.push({ t: 'name', v: 'pi', pos: i }); i++; continue; }

      if (isIdentStart(c)) {
        const start = i;
        while (isIdent(s[i])) i++;
        out.push({ t: 'name', v: s.slice(start, i), pos: start });
        continue;
      }

      if (c === '|') {
        if (s[i + 1] === '|') { out.push({ t: 'op', v: '||', pos: i }); i += 2; continue; }
        throw calcErr('a single | means nothing here — parallel is written ||', i);
      }
      if (c === '*' && s[i + 1] === '*') { out.push({ t: 'op', v: '^', pos: i }); i += 2; continue; }
      if ('+-*/%^(),='.indexOf(c) >= 0) { out.push({ t: 'op', v: c, pos: i }); i++; continue; }

      throw calcErr('I do not know what to do with "' + c + '"', i);
    }

    out.push({ t: 'end', v: '', pos: s.length });

    /* Juxtaposition is multiplication — `4x`, `2 pi`, `2(3+4)` — because that is how
       the notation is written everywhere else, including in the derivation input two
       panels away, which would otherwise accept `n A L` while this refused `4x`.

       The ambiguity this guard once refused wholesale is settled a stage earlier: the
       lexer takes an engineering suffix greedily, so by the time these tokens exist
       `4k7` is ONE number and `4x` is two things. What is left is genuinely a product.

       Two numbers touching stays an error. `4 5` is a typo, never a product, and
       saying so beats silently returning 20. */
    for (let j = 0; j < out.length - 1; j++) {
      if (out[j].t !== 'num' || out[j + 1].t !== 'num') continue;
      throw calcErr('two numbers with nothing between them — did you mean ' +
        out[j].text + ' * ' + out[j + 1].text + '?', out[j + 1].pos);
    }
    return out;
  }

  /* ================================================================ parser
   *
   *   expr    := assign
   *   assign  := NAME '=' assign | add
   *   add     := par ( ('+' | '-') par )*
   *   par     := mul ( '||' mul )*
   *   mul     := unary ( ('*' | '/' | '%') unary )*
   *   unary   := ('-' | '+') unary | power
   *   power   := primary ( '^' unary )?          -- right associative
   *   primary := NUMBER | NAME | NAME '(' args ')' | '(' expr ')'
   *
   * `||` sits between + and *, so `1k + 2k || 3k` is 1k + (2k||3k) — a resistor in
   * series with a parallel pair, which is how a series-parallel network is written
   * on paper and the reading that needs the fewest brackets in practice.
   */

  function parse(tokens) {
    let p = 0;
    /* Nesting depth, counted where the grammar actually recurses: a bracket and a
       function's argument list are the only two places parsePrimary re-enters
       parseExpr. Sixty-four is far past any expression anyone writes and far short of
       the engine's stack. */
    let depth = 0;
    function deeper() {
      if (++depth > DEPTH_MAX) {
        throw calcErr('that is nested more than ' + DEPTH_MAX + ' brackets deep — ' +
          'work it out in a few steps, or name the parts');
      }
    }

    function tok() { return tokens[p]; }
    function isOp(v) { const t = tokens[p]; return t.t === 'op' && t.v === v; }
    function describe(t) {
      if (t.t === 'end') return 'the end of the expression';
      if (t.t === 'num') return 'the number ' + t.text;
      if (t.t === 'name') return 'the name ' + t.v;
      return '"' + t.v + '"';
    }

    function parseExpr() { return parseAssign(); }

    function parseAssign() {
      const t = tokens[p], n = tokens[p + 1];
      if (t.t === 'name' && n && n.t === 'op' && n.v === '=') {
        p += 2;
        return { k: 'assign', name: t.v, a: parseAssign(), pos: t.pos };
      }
      return parseAdd();
    }

    function parseAdd() {
      let a = parsePar();
      while (isOp('+') || isOp('-')) {
        const o = tok(); p++;
        a = { k: 'bin', op: o.v, a: a, b: parsePar(), pos: o.pos };
      }
      return a;
    }

    function parsePar() {
      let a = parseMul();
      while (isOp('||')) {
        const o = tok(); p++;
        a = { k: 'bin', op: '||', a: a, b: parseMul(), pos: o.pos };
      }
      return a;
    }

    function parseMul() {
      let a = parseUnary();
      for (;;) {
        if (isOp('*') || isOp('/') || isOp('%')) {
          const o = tok(); p++;
          a = { k: 'bin', op: o.v, a: a, b: parseUnary(), pos: o.pos };
          continue;
        }
        /* Juxtaposition binds exactly as `*` does and evaluates left to right, so
           `2x/3y` is `2*x/3*y` — with x=6, y=2 that is 8, not 2. Textbooks often read
           `2x/3y` as (2x)/(3y) by giving juxtaposition the tighter grip; a calculator
           that quietly did that would disagree with the `*` its own history shows.
           Bracket the denominator when you mean it.

           A name or an opening bracket can start a factor; an operator or the end of
           input cannot. */
        const t = tok();
        if (t && (t.t === 'name' || (t.t === 'op' && t.v === '('))) {
          a = { k: 'bin', op: '*', a: a, b: parseUnary(), pos: t.pos };
          continue;
        }
        return a;
      }
    }

    function parseUnary() {
      if (isOp('-') || isOp('+')) {
        const o = tok(); p++;
        return { k: 'un', op: o.v, a: parseUnary(), pos: o.pos };
      }
      return parsePower();
    }

    function parsePower() {
      const base = parsePrimary();
      if (isOp('^')) {
        const o = tok(); p++;
        /* right operand goes through unary so `2^-1` reads */
        return { k: 'bin', op: '^', a: base, b: parseUnary(), pos: o.pos };
      }
      return base;
    }

    function parsePrimary() {
      const t = tok();

      if (t.t === 'num') { p++; return { k: 'num', v: t.v, pos: t.pos }; }

      if (t.t === 'name') {
        p++;
        if (isOp('(')) {
          const open = tok().pos;
          p++;
          deeper();
          const args = [];
          if (!isOp(')')) {
            for (;;) {
              args.push(parseExpr());
              if (isOp(',')) { p++; continue; }
              break;
            }
          }
          if (!isOp(')')) {
            throw calcErr('unbalanced bracket: the ( after ' + t.v + ' is never closed', open);
          }
          p++;
          depth--;
          return { k: 'call', name: t.v, args: args, pos: t.pos };
        }
        return { k: 'name', v: t.v, pos: t.pos };
      }

      if (t.t === 'op' && t.v === '(') {
        const open = t.pos;
        p++;
        deeper();
        const inner = parseExpr();
        if (!isOp(')')) throw calcErr('unbalanced bracket: the ( is never closed', open);
        p++;
        depth--;
        return inner;
      }

      if (t.t === 'op' && t.v === ')') {
        throw calcErr('unbalanced bracket: a ) with no ( to close', t.pos);
      }
      if (t.t === 'end') throw calcErr('the expression stops early — something is missing', t.pos);
      throw calcErr('I did not expect ' + describe(t) + ' here', t.pos);
    }

    const node = parseExpr();
    const rest = tok();
    if (rest.t !== 'end') {
      if (rest.t === 'op' && rest.v === ')') {
        throw calcErr('unbalanced bracket: a ) with no ( to close', rest.pos);
      }
      if (rest.t === 'op' && rest.v === ',') {
        throw calcErr('a comma only separates the arguments of a function', rest.pos);
      }
      throw calcErr('I did not expect ' + describe(rest) + ' after that', rest.pos);
    }
    return node;
  }

  /* ================================================================ evaluate */

  const CONSTS = { pi: Math.PI, e: Math.E };

  function par2(a, b) {
    /* A short across anything is a short. Everything else is the product over the
       sum, which is only undefined when the two exactly cancel. */
    if (a === 0 || b === 0) return 0;
    if (a + b === 0) throw calcErr('x || -x has no value — the two cancel exactly');
    return (a * b) / (a + b);
  }

  function need(name, args, n) {
    if (args.length !== n) {
      throw calcErr(name + ' takes ' + n + ' ' + (n === 1 ? 'argument' : 'arguments') +
        ', not ' + args.length);
    }
  }
  function needSome(name, args) {
    if (!args.length) throw calcErr(name + ' needs at least one value');
  }

  const FUNCS = {
    sqrt: function (a, env, n) {
      need(n, a, 1);
      if (a[0] < 0) throw calcErr('sqrt of a negative number is not a real value');
      return Math.sqrt(a[0]);
    },
    cbrt: function (a, env, n) { need(n, a, 1); return Math.cbrt(a[0]); },
    abs: function (a, env, n) { need(n, a, 1); return Math.abs(a[0]); },
    exp: function (a, env, n) { need(n, a, 1); return Math.exp(a[0]); },
    ln: function (a, env, n) { need(n, a, 1); return logOf(a[0], Math.E, 'ln'); },
    log: function (a, env, n) {
      /* base 10 by default: this is an electronics course, and log means log10 in
         every decibel formula the learner will meet. log(x, b) if they want another. */
      if (a.length === 2) return logOf(a[0], a[1], 'log');
      need(n, a, 1);
      return logOf(a[0], 10, 'log');
    },
    log10: function (a, env, n) { need(n, a, 1); return logOf(a[0], 10, 'log10'); },
    log2: function (a, env, n) { need(n, a, 1); return logOf(a[0], 2, 'log2'); },
    sin: function (a, env, n) { need(n, a, 1); return Math.sin(toRad(a[0], env)); },
    cos: function (a, env, n) { need(n, a, 1); return Math.cos(toRad(a[0], env)); },
    tan: function (a, env, n) {
      need(n, a, 1);
      /* Math.tan does not report the asymptote, because the double nearest π/2
         is not π/2: tan(90) came back 1.633e16, survived the isFinite check,
         and printed as "16331239 G" — an engineering reading of infinity, in
         the same font as every honest answer. Name the degree case exactly;
         catch the radian one by magnitude, where no equality test can. */
      if (env.deg && ((a[0] % 180) + 180) % 180 === 90) {
        throw calcErr('the tangent of ' + a[0] + '° is undefined — ' +
          'the ratio runs off to infinity there');
      }
      const v = Math.tan(toRad(a[0], env));
      if (Math.abs(v) > 1e15) {
        throw calcErr('that is close enough to a right angle that the tangent ' +
          'has no value this can hold');
      }
      return v;
    },
    asin: function (a, env, n) {
      need(n, a, 1);
      if (a[0] < -1 || a[0] > 1) throw calcErr('asin only takes a value between -1 and 1');
      return fromRad(Math.asin(a[0]), env);
    },
    acos: function (a, env, n) {
      need(n, a, 1);
      if (a[0] < -1 || a[0] > 1) throw calcErr('acos only takes a value between -1 and 1');
      return fromRad(Math.acos(a[0]), env);
    },
    atan: function (a, env, n) { need(n, a, 1); return fromRad(Math.atan(a[0]), env); },
    atan2: function (a, env, n) { need(n, a, 2); return fromRad(Math.atan2(a[0], a[1]), env); },
    round: function (a, env, n) { need(n, a, 1); return Math.round(a[0]); },
    floor: function (a, env, n) { need(n, a, 1); return Math.floor(a[0]); },
    ceil: function (a, env, n) { need(n, a, 1); return Math.ceil(a[0]); },
    sign: function (a, env, n) { need(n, a, 1); return Math.sign(a[0]); },
    hypot: function (a, env, n) { needSome(n, a); return Math.hypot.apply(Math, a); },
    min: function (a, env, n) { needSome(n, a); return Math.min.apply(Math, a); },
    max: function (a, env, n) { needSome(n, a); return Math.max.apply(Math, a); },
    /* the operator, as a function, for more than two at once */
    par: function (a, env, n) { needSome(n, a); return a.reduce(par2); },
  };

  function logOf(x, base, name) {
    if (x === 0) throw calcErr(name + ' of zero is undefined');
    if (x < 0) throw calcErr(name + ' of a negative number is not a real value');
    /* The base is as capable of being undefined as the value is, and unguarded it
       escaped as an answer rather than an error: log(8,0) came out as -0 and printed
       "0", and log(8,1) as Infinity, which read as "larger than this can hold". */
    if (!(base > 0)) throw calcErr(name + ' needs a base above zero, not ' + base);
    if (base === 1) throw calcErr('there is no ' + name + ' in base 1 — ' +
      'every power of 1 is 1');
    if (base === Math.E) return Math.log(x);
    return Math.log(x) / Math.log(base);
  }
  function toRad(x, env) { return env.deg ? x * Math.PI / 180 : x; }
  function fromRad(x, env) { return env.deg ? x * 180 / Math.PI : x; }

  function lookupName(n, env) {
    if (n === 'ans') {
      if (env.ans === null || env.ans === undefined) {
        throw calcErr('there is no previous answer yet — ans needs something above it');
      }
      return env.ans;
    }
    if (Object.prototype.hasOwnProperty.call(CONSTS, n)) return CONSTS[n];
    if (Object.prototype.hasOwnProperty.call(env.vars, n)) return env.vars[n];

    /* A near miss is almost always a capital letter, and "unknown name: R1" with no
       further help is the sort of answer that sends people to a physical calculator. */
    const lower = n.toLowerCase();
    const near = Object.keys(env.vars).filter(function (k) { return k.toLowerCase() === lower; });
    if (near.length) throw calcErr('unknown name: ' + n + ' — did you mean ' + near[0] + '?');
    if (Object.prototype.hasOwnProperty.call(FUNCS, n)) {
      throw calcErr(n + ' is a function — it needs brackets, as in ' + n + '(2)');
    }
    throw calcErr('unknown name: ' + n);
  }

  function evalNode(node, env) {
    switch (node.k) {
      case 'num': return node.v;
      case 'name': return lookupName(node.v, env);

      case 'un': {
        const v = evalNode(node.a, env);
        return node.op === '-' ? -v : v;
      }

      case 'bin': {
        const a = evalNode(node.a, env);
        const b = evalNode(node.b, env);
        switch (node.op) {
          case '+': return a + b;
          case '-': return a - b;
          case '*': return a * b;
          case '/':
            if (b === 0) throw calcErr('division by zero');
            return a / b;
          case '%':
            if (b === 0) throw calcErr('division by zero');
            return a % b;
          case '^': {
            const r = Math.pow(a, b);
            if (isNaN(r) && !isNaN(a) && !isNaN(b)) {
              throw calcErr('a negative number to a fractional power is not a real value');
            }
            return r;
          }
          case '||': return par2(a, b);
        }
        throw calcErr('unknown operator ' + node.op);
      }

      case 'call': {
        const fn = FUNCS[Object.prototype.hasOwnProperty.call(FUNCS, node.name) ? node.name : ''];
        if (!fn) {
          if (node.name === 'ans' || Object.prototype.hasOwnProperty.call(CONSTS, node.name)) {
            throw calcErr(node.name + ' is a value, not a function');
          }
          throw calcErr('unknown function: ' + node.name);
        }
        const args = node.args.map(function (x) { return evalNode(x, env); });
        return fn(args, env, node.name);
      }

      case 'assign': {
        const n = node.name;
        if (n === 'ans') throw calcErr('ans is the previous answer — it cannot be assigned');
        if (Object.prototype.hasOwnProperty.call(CONSTS, n)) {
          throw calcErr(n + ' is a constant — pick another name');
        }
        if (Object.prototype.hasOwnProperty.call(FUNCS, n)) {
          throw calcErr(n + ' is a function — pick another name');
        }
        const v = evalNode(node.a, env);
        env.vars[n] = v;
        env.assigned = n;
        return v;
      }
    }
    throw calcErr('I could not work that out');
  }

  /* One entry point for the whole language. `env` is not mutated unless the caller
     hands one over — the live preview under the input evaluates against a copy so
     that typing `r1 = 4k7` does not define r1 before Enter is pressed. */
  function evaluate(src, env) {
    const e = env || { vars: {}, ans: null, deg: true };
    if (!String(src).trim()) return { ok: false, error: 'nothing to work out' };
    if (String(src).length > SRC_MAX) {
      return { ok: false, error: 'that is ' + String(src).length + ' characters long — ' +
        'this box works out expressions up to ' + SRC_MAX + '. Name the parts and ' +
        'combine them.' };
    }
    try {
      const node = parse(tokenize(src));
      const v = evalNode(node, e);
      if (typeof v !== 'number' || isNaN(v)) {
        return { ok: false, error: 'that does not come out to a number' };
      }
      if (!isFinite(v)) return { ok: false, error: 'the result is larger than this can hold' };
      return {
        ok: true, value: v, display: format(v, ''), raw: rawNum(v),
        assigned: e.assigned || null,
      };
    } catch (err) {
      /* A calc error is a sentence written for a learner. Anything else is the engine
         talking — a RangeError from a stack the two limits above should already have
         kept us off — and repeating it verbatim puts "Maximum call stack size
         exceeded" in the history as though it were an account of their arithmetic. */
      if (err && err.calc) return { ok: false, error: String(err.message), pos: err.pos };
      return { ok: false, error: 'that was too much to work out in one go — ' +
        'try it in a few steps' };
    } finally {
      delete e.assigned;
    }
  }

  /* ================================================================ storage */

  function readJSON(key, fallback) {
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return fallback;
      const v = JSON.parse(raw);
      return (v && typeof v === 'object') ? v : fallback;
    } catch (e) { return fallback; }
  }
  function writeJSON(key, value) {
    try { localStorage.setItem(key, JSON.stringify(value)); return true; }
    catch (e) { return false; }
  }

  let notes = null;   /* { scratch: {text, at}, lessons: {id: {title, text, at}} } */
  let state = null;   /* { tab, deg, vars, ans, history, geom, pick } */

  function loadAll() {
    if (!notes) {
      notes = readJSON(K_NOTES, null) || { scratch: { text: '', at: 0 }, lessons: {} };
      if (!notes.scratch || typeof notes.scratch !== 'object') notes.scratch = { text: '', at: 0 };
      if (!notes.lessons || typeof notes.lessons !== 'object') notes.lessons = {};
    }
    if (!state) {
      const s = readJSON(K_STATE, null) || {};
      state = {
        tab: s.tab === 'notes' ? 'notes' : 'calc',
        deg: s.deg !== false,
        vars: (s.vars && typeof s.vars === 'object') ? s.vars : {},
        ans: typeof s.ans === 'number' ? s.ans : null,
        history: Array.isArray(s.history) ? s.history.slice(-HIST_MAX) : [],
        geom: (s.geom && typeof s.geom === 'object') ? s.geom : null,
        pick: s.pick === 'scratch' ? 'scratch' : 'lesson',
      };
      /* a stored variable that is not a number is a corrupted store, not a value */
      Object.keys(state.vars).forEach(function (k) {
        if (typeof state.vars[k] !== 'number' || !isFinite(state.vars[k])) delete state.vars[k];
      });
    }
  }

  /* Whether the last write landed. Not announced from in here, and that is the point:
     the first version of this fix said its piece the moment the desk opened, and run()
     then announced the result 60ms later over the top of it — say() cancels whatever is
     pending, so a warning issued on its own is a warning nobody hears. The state is
     recorded here and the places that speak fold it into the sentence they were already
     going to say. Caught by the gate's own control case failing. */
  let storageFailed = false;

  /* writeJSON returns false when localStorage refuses — a full quota, a private
     window, storage switched off. flushSave has always checked that and told the
     learner. This one did not, and this one carries the history, the variables, `ans`,
     the angle mode and the panel's geometry: every calculation made in the session and
     every value named. A learner whose store was full lost all of it on reload and was
     never told, because the one function that reports lives on the other tab. */
  function saveState() {
    loadAll();
    const ok = writeJSON(K_STATE, {
      tab: state.tab, deg: state.deg, vars: state.vars, ans: state.ans,
      history: state.history.slice(-HIST_MAX), geom: state.geom, pick: state.pick,
    });
    storageFailed = !ok;
    if (!ok && open_ && elems) {
      elems.saved.classList.add('warn');
      elems.saved.textContent = 'could not save — storage is full';
      /* the notes tab has a place for this and the calculator does not, so put it
         where the eye already is: directly above the box being typed into */
      elems.prev.innerHTML = '<b>could not save — storage is full</b>';
    }
    return ok;
  }

  /* ================================================================ context */

  let ctx = { lessonId: null, title: '' };

  function currentNoteKey() {
    if (state.pick === 'lesson' && ctx.lessonId) return ctx.lessonId;
    return null;                                   /* null means the scratch pad */
  }
  function currentNote() {
    const k = currentNoteKey();
    if (!k) return notes.scratch;
    if (!notes.lessons[k]) notes.lessons[k] = { title: ctx.title || k, text: '', at: 0 };
    if (ctx.title) notes.lessons[k].title = ctx.title;
    return notes.lessons[k];
  }
  function currentNoteName() {
    const k = currentNoteKey();
    if (!k) return 'Scratch pad';
    return (notes.lessons[k] && notes.lessons[k].title) || ctx.title || k;
  }

  /* ================================================================ style */

  let styled = false;

  /* The stylesheet, lifted out of ensureStyle into a function of its own so that a
     gate can read it without a DOM. This is the only file in the codebase that carries
     its own CSS, and the consequence went unnoticed for as long as both have existed:
     tools/verify_theme.mjs reads src/index.head.html, so every surface in the app was
     measured in both themes except these — and the "every colour comes from a token"
     invariant was never applied here either. Built on demand, so a desk that is never
     opened still pays for none of it. */
  function deskCss() {
    return [
      /* Two colours the tokens do not carry — a veil and a shadow — declared here as
         tokens of their own so nothing below hard-codes a colour, and so the light
         theme gets its own pair rather than a dark one at reduced opacity. */
      /* The veil is built from --ground in the dark theme and from --ink in the
         light one, because in both cases that is the near-black token: a veil mixed
         from a light --ground is a wash of off-white over off-white, and the page
         behind reads as still live. */
      ':root{--dsk-veil:color-mix(in srgb,var(--ground) 76%,transparent);',
      '  --dsk-shadow:0 30px 80px rgba(0,0,0,.55)}',
      '[data-theme=light]{--dsk-veil:color-mix(in srgb,var(--ink) 32%,transparent);',
      '  --dsk-shadow:0 24px 60px rgba(15,25,5,.20)}',

      '@keyframes dsk-in{from{opacity:0}to{opacity:1}}',
      '@keyframes dsk-rise{from{opacity:0;transform:translateY(10px) scale(.985)}to{opacity:1;transform:none}}',

      /* display:grid would beat a bare [hidden], and the rule that hides it lives in
         another file. This one belongs to the modal, so it travels with it. */
      '.dsk-back[hidden]{display:none}',
      '.dsk-back{position:fixed;inset:0;z-index:55;display:grid;place-items:center;padding:20px;',
      '  background:var(--dsk-veil);backdrop-filter:blur(3px);-webkit-backdrop-filter:blur(3px);',
      '  animation:dsk-in .15s var(--ease) both}',

      '.dsk{position:relative;width:min(780px,94vw);height:min(580px,86vh);',
      '  min-width:340px;min-height:280px;max-width:96vw;max-height:92vh;',
      '  display:flex;flex-direction:column;overflow:hidden;resize:both;',
      '  border:1px solid var(--line-3);border-radius:var(--r-lg);background:var(--surface-solid);',
      '  box-shadow:var(--dsk-shadow);animation:dsk-rise .18s var(--ease) both}',

      /* head */
      '.dsk-head{display:flex;align-items:center;gap:10px;flex:none;padding:9px 10px 9px 14px;',
      '  border-bottom:1px solid var(--line);background:var(--sunk);cursor:grab;',
      '  touch-action:none;user-select:none;-webkit-user-select:none}',
      '.dsk-head.drag{cursor:grabbing}',
      '.dsk-grip{display:flex;gap:3px;flex:none;opacity:.7}',
      '.dsk-grip i{width:3px;height:3px;border-radius:50%;background:var(--ink-5)}',
      /* --accent-ink, not --lime, everywhere the accent is used as INK on a surface the
         light theme flips. --lime is #5F8A0B there — a fill colour, tuned to carry
         --on-lime on top of it — and as ink it lands at 3.7-4.1:1. Cycle 5 minted
         --accent-ink for this and cycle 6 made the same repair on the schematic
         editor's result table; this file was never measured because it is the one file
         that carries its own CSS. Code spans take --code-ink, the darker of the two,
         which is what they take everywhere else in the app. */
      '.dsk-title{font-family:var(--mono);font-size:10px;letter-spacing:.16em;',
      '  text-transform:uppercase;color:var(--accent-ink);flex:none}',
      '.dsk-tabs{display:inline-flex;gap:3px;padding:3px;border-radius:10px;margin-left:6px;',
      '  background:var(--surface-2);border:1px solid var(--line)}',
      '.dsk-tab{padding:4px 12px;border-radius:7px;font-size:12px;font-weight:600;color:var(--ink-3)}',
      '.dsk-tab:hover{color:var(--ink)}',
      '.dsk-tab[aria-selected=true]{background:var(--lime);color:var(--on-lime)}',
      '.dsk-where{flex:1;min-width:0;text-align:right;font-family:var(--mono);font-size:10.5px;',
      '  color:var(--ink-3);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
      '.dsk-x{flex:none;width:28px;height:28px;border-radius:8px;display:grid;place-items:center;',
      '  color:var(--ink-3);font-size:15px;line-height:1}',
      '.dsk-x:hover{background:var(--surface-2);color:var(--ink)}',

      '.dsk-pane{flex:1;min-height:0;display:none;flex-direction:column}',
      '.dsk-pane.on{display:flex}',

      /* calculator */
      '.dsk-hist{flex:1;min-height:0;overflow:auto;padding:12px 14px;display:flex;',
      '  flex-direction:column;justify-content:flex-end;gap:9px}',
      '.dsk-empty{color:var(--ink-3);font-size:12.5px;line-height:1.75;margin:auto 0}',
      '.dsk-empty code{font-family:var(--mono);font-size:12px;color:var(--code-ink);',
      '  background:var(--lime-08);padding:1px 5px;border-radius:4px}',
      '.dsk-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 8px;',
      '  padding:7px 9px;border-radius:var(--r);border:1px solid transparent}',
      '.dsk-row:hover{border-color:var(--line);background:var(--surface-2)}',
      '.dsk-ex{grid-column:1;text-align:left;font-family:var(--mono);font-size:12px;',
      '  color:var(--ink-3);white-space:pre-wrap;word-break:break-word;line-height:1.5}',
      '.dsk-row:hover .dsk-ex{color:var(--ink-2)}',
      '.dsk-val{grid-column:1;text-align:left;font-family:var(--mono);font-size:15px;',
      '  color:var(--accent-ink);word-break:break-word;line-height:1.4}',
      '.dsk-val small{display:block;font-size:10.5px;color:var(--ink-3);margin-top:2px}',
      '.dsk-row.err .dsk-val{color:var(--bad);font-size:12.5px}',
      '.dsk-send{grid-row:1/span 2;grid-column:2;align-self:center;width:26px;height:26px;',
      '  border-radius:7px;color:var(--ink-3);font-size:12px;opacity:0;transition:opacity .14s}',
      '.dsk-row:hover .dsk-send,.dsk-send:focus-visible{opacity:1}',
      '.dsk-send:hover{background:var(--lime-12);color:var(--accent-ink)}',

      '.dsk-foot{flex:none;border-top:1px solid var(--line);background:var(--sunk);padding:9px 12px}',
      '.dsk-prev{min-height:16px;font-family:var(--mono);font-size:11px;color:var(--ink-3);',
      '  padding:0 2px 5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}',
      '.dsk-prev b{color:var(--ink-3);font-weight:500}',
      '.dsk-in{display:flex;align-items:center;gap:8px;padding:0 10px;border-radius:var(--r);',
      '  border:1px solid var(--line-3);background:var(--editor)}',
      '.dsk-in:focus-within{border-color:var(--lime)}',
      '.dsk-in .car{font-family:var(--mono);font-size:14px;color:var(--on-editor-lime);flex:none}',
      '.dsk-in input{flex:1;min-width:0;height:42px;border:0;background:none;outline:none;',
      '  color:var(--on-editor);font-family:var(--mono);font-size:15px}',
      '.dsk-in input::placeholder{color:var(--on-editor-hint)}',
      '.dsk-mini{flex:none;height:26px;padding:0 9px;border-radius:7px;font-family:var(--mono);',
      '  font-size:10.5px;letter-spacing:.06em;color:var(--on-editor-2);border:1px solid var(--on-editor-line)}',
      '.dsk-mini:hover{color:var(--on-editor);border-color:var(--ink-4)}',
      '.dsk-mini.on{color:var(--on-editor-lime);border-color:var(--lime-30);background:var(--lime-12)}',
      '.dsk-tips{display:none;padding:10px 2px 0;font-size:12px;line-height:1.7;color:var(--ink-3)}',
      '.dsk-tips.on{display:block}',
      '.dsk-tips b{color:var(--ink-2);font-weight:600}',
      '.dsk-tips code{font-family:var(--mono);font-size:11.5px;color:var(--code-ink)}',

      /* notes */
      '.dsk-notebar{flex:none;display:flex;align-items:center;gap:6px;padding:9px 12px;',
      '  border-bottom:1px solid var(--line)}',
      '.dsk-pick{height:26px;padding:0 11px;border-radius:7px;font-size:11.5px;font-weight:600;',
      '  color:var(--ink-4);border:1px solid var(--line-2);max-width:230px;overflow:hidden;',
      '  white-space:nowrap;text-overflow:ellipsis}',
      '.dsk-pick:hover{color:var(--ink)}',
      '.dsk-pick[aria-pressed=true]{color:var(--accent-ink);border-color:var(--lime-30);background:var(--lime-08)}',
      '.dsk-saved{margin-left:auto;font-family:var(--mono);font-size:10.5px;color:var(--ink-3);',
      '  white-space:nowrap}',
      '.dsk-saved.warn{color:var(--amber)}',
      '.dsk-ta{flex:1;min-height:0;width:100%;resize:none;border:0;outline:none;padding:14px 16px;',
      '  background:var(--editor);color:var(--on-editor);font-family:var(--mono);font-size:13px;',
      '  line-height:1.75;tab-size:2}',
      '.dsk-ta::placeholder{color:var(--on-editor-hint)}',
      '.dsk-notefoot{flex:none;display:flex;align-items:center;gap:8px;padding:8px 12px;',
      '  border-top:1px solid var(--line);background:var(--sunk);',
      '  font-family:var(--mono);font-size:10.5px;color:var(--ink-3)}',
      '.dsk-notefoot .sp{flex:1}',

      /* The one live region in the modal. The stylesheet carries no visually-hidden
         utility, so it is declared here and travels with the component. */
      '.dsk-say{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;',
      '  clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap;border:0}',

      '@media (max-width:560px){',
      '  .dsk-back{padding:0}',
      '  .dsk{width:100vw;height:100dvh;max-width:100vw;max-height:100dvh;border-radius:0;resize:none}',
      '  .dsk-where{display:none}',
      '}',
      '@media (prefers-reduced-motion:reduce){',
      '  .dsk-back,.dsk{animation:none}',
      '  .dsk-send{transition:none}',
      '}',
    ].join('\n');
  }

  function ensureStyle() {
    if (styled || typeof document === 'undefined') return;
    styled = true;
    const tag = document.createElement('style');
    tag.id = 'desk-style';
    tag.textContent = deskCss();
    document.head.appendChild(tag);
  }

  /* ================================================================ dom */

  let back = null, panel = null, elems = null;
  let open_ = false, lastFocus = null, hidden = null;
  let saveTimer = 0, recall = -1, draft = '';

  const esc = function (s) {
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;')
      .replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  };

  function build() {
    back = document.createElement('div');
    back.className = 'dsk-back';
    back.innerHTML = [
      '<div class="dsk" role="dialog" aria-modal="true" aria-label="Desk: notepad and calculator">',
      '  <div class="dsk-head" data-head>',
      '    <span class="dsk-grip" aria-hidden="true"><i></i><i></i><i></i></span>',
      '    <span class="dsk-title">Desk</span>',
      '    <div class="dsk-tabs" role="tablist" aria-label="Desk sections">',
      '      <button class="dsk-tab" role="tab" id="dsk-tab-calc" aria-controls="dsk-pane-calc"',
      '        data-tab="calc" tabindex="-1">Calculator</button>',
      '      <button class="dsk-tab" role="tab" id="dsk-tab-notes" aria-controls="dsk-pane-notes"',
      '        data-tab="notes" tabindex="-1">Notes</button>',
      '    </div>',
      '    <span class="dsk-where" data-where></span>',
      '    <button class="dsk-x" data-close aria-label="Close the desk (Esc)">✕</button>',
      '  </div>',

      '  <div class="dsk-pane" role="tabpanel" id="dsk-pane-calc"',
      '    aria-labelledby="dsk-tab-calc" data-pane="calc">',
      '    <div class="dsk-hist" data-hist></div>',
      '    <div class="dsk-foot">',
      '      <div class="dsk-prev" data-prev></div>',
      '      <div class="dsk-in">',
      '        <span class="car" aria-hidden="true">›</span>',
      '        <input data-input type="text" spellcheck="false" autocomplete="off"',
      '          autocapitalize="off" autocorrect="off" aria-label="Expression"',
      '          placeholder="4k7 || 10k">',
      '        <button class="dsk-mini" data-angle title="Degrees or radians"></button>',
      '        <button class="dsk-mini" data-tonote aria-label="Send the last result to the note"',
      '          title="Send the last result to the note">→ note</button>',
      '        <button class="dsk-mini" data-help id="dsk-help" aria-controls="dsk-tips"',
      '          aria-expanded="false" aria-label="What this calculator understands"',
      '          title="What this calculator understands">?</button>',
      '      </div>',
      '      <div class="dsk-tips" id="dsk-tips" data-tips></div>',
      '    </div>',
      '  </div>',

      '  <div class="dsk-pane" role="tabpanel" id="dsk-pane-notes"',
      '    aria-labelledby="dsk-tab-notes" data-pane="notes">',
      '    <div class="dsk-notebar">',
      '      <button class="dsk-pick" data-pick="lesson" aria-pressed="false"></button>',
      '      <button class="dsk-pick" data-pick="scratch" aria-pressed="false">Scratch pad</button>',
      '      <span class="dsk-saved" data-saved></span>',
      '    </div>',
      '    <textarea class="dsk-ta" data-ta spellcheck="true"',
      '      placeholder="Working, values, the thing you will forget by tomorrow."></textarea>',
      '    <div class="dsk-notefoot">',
      '      <span data-count></span><span class="sp"></span>',
      '      <button class="dsk-mini" data-copy>copy</button>',
      '      <button class="dsk-mini" data-clear>clear</button>',
      '    </div>',
      '  </div>',
      '  <p class="dsk-say" data-say role="status" aria-live="polite"></p>',
      '</div>',
    ].join('\n');

    panel = back.querySelector('.dsk');
    elems = {
      head: back.querySelector('[data-head]'),
      where: back.querySelector('[data-where]'),
      tabs: Array.prototype.slice.call(back.querySelectorAll('.dsk-tab')),
      panes: {
        calc: back.querySelector('[data-pane=calc]'),
        notes: back.querySelector('[data-pane=notes]'),
      },
      hist: back.querySelector('[data-hist]'),
      prev: back.querySelector('[data-prev]'),
      input: back.querySelector('[data-input]'),
      angle: back.querySelector('[data-angle]'),
      tonote: back.querySelector('[data-tonote]'),
      help: back.querySelector('[data-help]'),
      tips: back.querySelector('[data-tips]'),
      picks: Array.prototype.slice.call(back.querySelectorAll('.dsk-pick')),
      saved: back.querySelector('[data-saved]'),
      ta: back.querySelector('[data-ta]'),
      count: back.querySelector('[data-count]'),
      copy: back.querySelector('[data-copy]'),
      clear: back.querySelector('[data-clear]'),
      say: back.querySelector('[data-say]'),
    };

    elems.tips.innerHTML = [
      '<b>Suffixes</b> both ways: <code>4k7</code>, <code>4.7k</code>, <code>220n</code>,',
      ' <code>10M</code>, <code>1u</code>, <code>2p</code> — and answers come back the same way.<br>',
      '<b>Parallel</b>: <code>4k7 || 10k</code>, or <code>par(1k,2k,3k)</code>.',
      ' It binds tighter than + and looser than *.<br>',
      '<b>Names</b>: <code>r1 = 4k7</code>, then <code>12 / r1</code>.',
      ' <code>ans</code> is the answer above.<br>',
      '<b>Functions</b>: sqrt cbrt abs exp ln log log10 log2 sin cos tan asin acos atan',
      ' atan2 hypot round floor ceil sign min max par, and <code>pi</code>.',
      ' <code>log</code> is base 10.',
    ].join('');

    /* --- wiring --- */
    back.addEventListener('mousedown', function (e) { if (e.target === back) close(); });

    elems.tabs.forEach(function (b) {
      b.addEventListener('click', function () { show(b.dataset.tab); });
      b.addEventListener('keydown', onTabKey);
    });
    back.querySelector('[data-close]').addEventListener('click', function () { close(); });

    elems.input.addEventListener('keydown', onInputKey);
    elems.input.addEventListener('input', function () { recall = -1; preview(); });

    elems.angle.addEventListener('click', function () {
      state.deg = !state.deg;
      paintAngle();
      preview();
      saveState();
      elems.input.focus();
    });
    elems.tonote.addEventListener('click', function () { sendLast(); });
    elems.help.addEventListener('click', function () {
      const on = elems.tips.classList.toggle('on');
      elems.help.classList.toggle('on', on);
      elems.help.setAttribute('aria-expanded', on ? 'true' : 'false');
    });

    elems.picks.forEach(function (b) {
      b.addEventListener('click', function () {
        flushSave();
        state.pick = b.dataset.pick;
        saveState();
        paintNotes();
        elems.ta.focus();
      });
    });
    elems.ta.addEventListener('input', function () {
      paintCount();
      elems.saved.classList.remove('warn');
      elems.saved.textContent = 'unsaved…';
      saveSoon();
    });
    elems.ta.addEventListener('blur', flushSave);
    elems.copy.addEventListener('click', function () {
      const t = elems.ta.value;
      if (!t) return;
      try {
        navigator.clipboard.writeText(t).then(function () { flash('copied'); }, function () { flash('could not copy'); });
      } catch (e) { flash('could not copy'); }
    });
    elems.clear.addEventListener('click', function () {
      if (!elems.ta.value) return;
      /* One press empties it, a second press within the modal's lifetime does not
         bring it back — so ask, because a lost page of working is not recoverable. */
      if (!window.confirm('Clear "' + currentNoteName() + '"? This cannot be undone.')) return;
      elems.ta.value = '';
      paintCount();
      flushSave();
    });

    elems.head.addEventListener('pointerdown', onDragStart);

    /* `resize:both` puts a gripper in the panel's bottom-right corner, and dragging
       it is the only way a learner can choose a size. Arm on a press there, so the
       observer records a chosen size and not one the stylesheet merely computed —
       every reflow is a border-box change too, the first layout on open included,
       and `width:min(780px,94vw)` makes one out of every window resize. Persisting
       those pinned an inline width that then outranked the responsive rule. */
    let sizing = false;
    panel.addEventListener('pointerdown', function (e) {
      const r = panel.getBoundingClientRect();
      /* a control that happens to sit in the corner is a control, not the gripper —
         and `clear` puts up a confirm(), through which no pointerup arrives */
      sizing = e.button === 0 &&
        e.clientX >= r.right - 24 && e.clientY >= r.bottom - 24 &&
        !e.target.closest('button,input,textarea,select,a');
    });
    /* on the window, not the panel: a resize drag can end with the pointer well
       outside the panel, and a gesture left armed would record the next reflow */
    const notSizing = function () { sizing = false; };
    window.addEventListener('pointerup', notSizing);
    window.addEventListener('pointercancel', notSizing);

    if (typeof ResizeObserver === 'function') {
      let rt = 0;
      const ro = new ResizeObserver(function () {
        /* checked here, not in the debounced body: this runs in the frame the size
           changed in, while the gripper is still under the pointer */
        if (!sizing) return;
        clearTimeout(rt);
        rt = setTimeout(function () {
          /* the phone layout's size is the viewport's, not the learner's choice */
          if (!open_ || !panel || phone()) return;
          const r = panel.getBoundingClientRect();
          state.geom = state.geom || {};
          state.geom.w = Math.round(r.width);
          state.geom.h = Math.round(r.height);
          saveState();
        }, 250);
      });
      ro.observe(panel);
    }

    document.body.appendChild(back);
  }

  /* ================================================================ painting */

  function paintAngle() {
    elems.angle.textContent = state.deg ? 'DEG' : 'RAD';
    elems.angle.classList.toggle('on', !state.deg);
    elems.angle.setAttribute('aria-label', state.deg
      ? 'Angles in degrees — switch to radians'
      : 'Angles in radians — switch to degrees');
  }

  function paintHistory() {
    const h = state.history;
    if (!h.length) {
      elems.hist.innerHTML = '<div class="dsk-empty">Nothing worked out yet.<br>' +
        'Try <code>4k7 || 10k</code>, or <code>1/(2*pi*sqrt(47m*220n))</code>,<br>' +
        'or name something: <code>r1 = 4k7</code>.</div>';
      return;
    }
    elems.hist.innerHTML = h.map(function (r, i) {
      const val = r.ok
        ? '<span class="dsk-val" data-val="' + i + '" role="button" tabindex="0" ' +
          'title="Put this value in the box">' + esc(r.display) +
          '<small>' + esc(r.raw) + '</small></span>'
        : '<span class="dsk-val">' + esc(r.error) + '</span>';
      return '<div class="dsk-row' + (r.ok ? '' : ' err') + '">' +
        '<button class="dsk-ex" data-ex="' + i + '" title="Put this expression back in the box">' +
        esc(r.src) + '</button>' + val +
        (r.ok ? '<button class="dsk-send" data-send="' + i + '" ' +
          'aria-label="Send this result to the note" title="Send to the note">↴</button>' : '') +
        '</div>';
    }).join('');
    elems.hist.scrollTop = elems.hist.scrollHeight;
  }

  function paintNotes() {
    const lessonBtn = elems.picks[0];
    lessonBtn.textContent = ctx.title || 'This lesson';
    lessonBtn.disabled = !ctx.lessonId;
    lessonBtn.title = ctx.lessonId ? 'Notes for ' + (ctx.title || ctx.lessonId)
      : 'Open a lesson and its own note appears here';
    const onLesson = !!currentNoteKey();
    lessonBtn.setAttribute('aria-pressed', onLesson ? 'true' : 'false');
    elems.picks[1].setAttribute('aria-pressed', onLesson ? 'false' : 'true');

    const note = currentNote();
    if (elems.ta.value !== note.text) elems.ta.value = note.text || '';
    paintCount();
    elems.saved.classList.remove('warn');
    elems.saved.textContent = note.at ? 'saved ' + clock(note.at) : '';
  }

  function paintCount() {
    const t = elems.ta.value;
    const lines = t ? t.split('\n').length : 0;
    elems.count.textContent = t.length + (t.length === 1 ? ' char' : ' chars') +
      ' · ' + lines + (lines === 1 ? ' line' : ' lines');
  }

  function paintWhere() {
    elems.where.textContent = ctx.title || '';
    elems.where.title = ctx.title || '';
  }

  function clock(ms) {
    const d = new Date(ms);
    const p = function (n) { return (n < 10 ? '0' : '') + n; };
    return p(d.getHours()) + ':' + p(d.getMinutes());
  }

  /* The modal's only live region. Cleared and re-set rather than assigned, so
     that working the same expression twice is announced twice: an assignment of
     identical text is not a mutation, and assistive tech would stay silent. */
  let sayTimer = 0;
  function say(msg) {
    if (!elems || !elems.say) return;
    clearTimeout(sayTimer);
    elems.say.textContent = '';
    sayTimer = setTimeout(function () {
      if (elems && elems.say) elems.say.textContent = msg;
    }, 60);
  }

  function flash(msg) {
    say(msg);
    elems.saved.classList.remove('warn');
    elems.saved.textContent = msg;
    setTimeout(function () {
      if (!open_) return;
      const note = currentNote();
      if (elems.saved.textContent === msg) {
        elems.saved.textContent = note.at ? 'saved ' + clock(note.at) : '';
      }
    }, 1800);
  }

  /* ================================================================ calculator */

  function envNow() {
    return { vars: state.vars, ans: state.ans, deg: state.deg };
  }

  function preview() {
    const src = elems.input.value.trim();
    if (!src) { elems.prev.textContent = ''; return; }
    /* A copy of the variables, so a preview of `r1 = 4k7` defines nothing.
       Errors stay silent here: half an expression is not a mistake, it is a
       half-typed expression, and shouting about it while someone types is noise. */
    const r = evaluate(src, { vars: Object.assign({}, state.vars), ans: state.ans, deg: state.deg });
    elems.prev.innerHTML = r.ok ? '= <b>' + esc(r.display) + '</b>' : '';
  }

  function onInputKey(e) {
    if (e.key === 'Enter') { e.preventDefault(); run(); return; }
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
      const h = state.history;
      if (!h.length) return;
      e.preventDefault();
      if (recall === -1) { draft = elems.input.value; recall = h.length; }
      recall += (e.key === 'ArrowUp' ? -1 : 1);
      if (recall < 0) recall = 0;
      if (recall >= h.length) { recall = -1; elems.input.value = draft; preview(); return; }
      elems.input.value = h[recall].src;
      elems.input.setSelectionRange(elems.input.value.length, elems.input.value.length);
      preview();
    }
  }

  function run() {
    const src = elems.input.value.trim();
    if (!src) return;
    const r = evaluate(src, envNow());
    const row = r.ok
      ? { src: src, ok: true, value: r.value, display: r.display, raw: r.raw }
      : { src: src, ok: false, error: r.error };
    if (r.ok) state.ans = r.value;
    state.history.push(row);
    if (state.history.length > HIST_MAX) state.history.splice(0, state.history.length - HIST_MAX);
    elems.input.value = '';
    recall = -1; draft = '';
    elems.prev.textContent = '';
    paintHistory();
    /* Saved before anything is said, so that what is said can be true about both. A
       result announced and then contradicted 60ms later by a warning that cancels it
       is worse than either sentence on its own. */
    const stored = saveState();
    /* The result was the one thing in this modal a screen reader never heard:
       the input clears, the preview clears, and the history is not a live
       region. The preview used to be one, and read a running total over the
       user's own typing echo instead. */
    say((r.ok ? src + ' equals ' + r.display : r.error) +
      (stored ? '' : ' — but it could not be saved; storage is full, so this will not be here next time.'));
  }

  function lastOk() {
    for (let i = state.history.length - 1; i >= 0; i--) {
      if (state.history[i].ok) return state.history[i];
    }
    return null;
  }

  function sendLast() { sendRow(lastOk()); }

  /* The whole reason the two live in one modal: a result crosses into the note the
     learner is keeping, in the note's own words — expression and answer, not a bare
     number they will not recognise in an hour. */
  function sendRow(row) {
    if (!row) { flash('nothing to send yet'); return; }
    const line = row.src + ' = ' + row.display;
    const cur = elems.ta.value;
    elems.ta.value = cur + (cur && !/\n$/.test(cur) ? '\n' : '') + line + '\n';
    paintCount();
    flushSave();
    flash('sent to ' + (currentNoteKey() ? 'the lesson note' : 'the scratch pad'));
    /* the note badge is on the other tab; say so where the eye already is */
    elems.prev.innerHTML = '<b>' + esc(line) + '</b> → ' + esc(currentNoteName());
  }

  /* ================================================================ notes save */

  function saveSoon() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(flushSave, SAVE_MS);
  }

  /* currentNote() creates the row for whichever lesson is open, so opening the
     desk on a lesson and reading on leaves an empty row behind for every lesson
     walked past — and the next real save serialises the lot. The delete above
     only ever reached the note being written; by the time it runs, the walked-past
     rows belong to lessons that are no longer current, so it never reached them.
     Prune the whole map on the way out instead. */
  function saveNotes() {
    Object.keys(notes.lessons).forEach(function (id) {
      const n = notes.lessons[id];
      if (!n || !String(n.text || '').trim()) delete notes.lessons[id];
    });
    return writeJSON(K_NOTES, notes);
  }

  function flushSave() {
    clearTimeout(saveTimer);
    if (!open_ || !elems) return;
    const note = currentNote();
    const text = elems.ta.value;
    if (text === note.text) {
      if (elems.saved.textContent === 'unsaved…') {
        elems.saved.textContent = note.at ? 'saved ' + clock(note.at) : '';
      }
      return;
    }
    note.text = text;
    note.at = Date.now();
    /* An empty lesson note is a note that was never written — do not keep a row
       for every lesson the learner merely walked past. */
    const k = currentNoteKey();
    if (k && !text.trim()) delete notes.lessons[k];
    const ok = saveNotes();
    elems.saved.classList.toggle('warn', !ok);
    elems.saved.textContent = ok ? 'saved ' + clock(note.at) : 'could not save — storage is full';
    if (!ok) say('Could not save — storage is full');
  }

  /* ================================================================ dragging */

  let drag = null;

  function onDragStart(e) {
    if (e.button !== 0) return;
    if (e.target.closest('button,input,textarea,select,a')) return;
    const r = panel.getBoundingClientRect();
    /* Position only. Freezing the measured size here as an inline width was the
       third way a size the learner never chose got pinned: `width:min(780px,94vw)`
       resolves against the viewport whether the panel is in the backdrop's grid or
       taken out of it, so the size needs no help to survive the drag, and an inline
       one outranks the responsive rule for the rest of the session. */
    place(r.left, r.top);
    drag = { dx: e.clientX - r.left, dy: e.clientY - r.top };
    elems.head.classList.add('drag');
    /* A pointerdown without a real pointer — a synthetic event, or a device that
       reports none — must not leave the header stuck in a drag it can never end. */
    try { elems.head.setPointerCapture(e.pointerId); }
    catch (err) { drag = null; elems.head.classList.remove('drag'); return; }
    elems.head.addEventListener('pointermove', onDragMove);
    elems.head.addEventListener('pointerup', onDragEnd);
    elems.head.addEventListener('pointercancel', onDragEnd);
    e.preventDefault();
  }
  function onDragMove(e) {
    if (!drag) return;
    place(e.clientX - drag.dx, e.clientY - drag.dy);
  }
  function onDragEnd(e) {
    if (!drag) return;
    drag = null;
    elems.head.classList.remove('drag');
    try { elems.head.releasePointerCapture(e.pointerId); } catch (err) { /* already gone */ }
    elems.head.removeEventListener('pointermove', onDragMove);
    elems.head.removeEventListener('pointerup', onDragEnd);
    elems.head.removeEventListener('pointercancel', onDragEnd);
    /* A drag is a choice of position and nothing else. Measuring the size here and
       storing it too pinned a width the learner never picked — the same way the
       resize observer used to — and an inline width defeats the responsive rule. */
    const r = panel.getBoundingClientRect();
    const g = state.geom || {};
    state.geom = { x: Math.round(r.left), y: Math.round(r.top), w: g.w, h: g.h };
    saveState();
  }

  /* Taking the panel out of the backdrop's centring grid. It is clamped to stay
     wholly on screen: a modal dragged off an edge by its only handle is a modal you
     can no longer move, and one restored off-screen after the window was resized is
     a feature that has simply vanished. */
  function place(x, y) {
    const rect = panel.getBoundingClientRect();
    const maxX = Math.max(0, window.innerWidth - rect.width);
    const maxY = Math.max(0, window.innerHeight - rect.height);
    panel.style.position = 'fixed';
    panel.style.margin = '0';
    panel.style.left = Math.round(Math.min(Math.max(x, 0), maxX)) + 'px';
    panel.style.top = Math.round(Math.min(Math.max(y, 0), maxY)) + 'px';
  }

  const phone = function () { return window.innerWidth <= 560; };

  /* Back to the stylesheet's own sizing. Leaving a desktop session's inline width on
     the element defeated the phone layout entirely: the media query says full bleed,
     and a stale `width:780px` quietly outranks it. */
  function clearGeom() {
    ['position', 'margin', 'left', 'top', 'width', 'height'].forEach(function (k) {
      panel.style[k] = '';
    });
  }

  function applyGeom() {
    const g = state.geom;
    if (!g || phone()) { clearGeom(); return; }
    if (g.w && g.h) { panel.style.width = g.w + 'px'; panel.style.height = g.h + 'px'; }
    if (typeof g.x === 'number' && typeof g.y === 'number') place(g.x, g.y);
  }

  function onWinResize() {
    if (!open_) return;
    if (phone()) { clearGeom(); return; }
    if (panel.style.position !== 'fixed') return;
    const r = panel.getBoundingClientRect();
    place(r.left, r.top);
  }

  /* ================================================================ focus */

  /* Deliberately broad, with the exclusions moved into the filter: the old
     selector could not say "a button that is not a tab stop", so the roving
     tabindex on the tablist would have let Tab wrap onto the unselected tab. */
  const FOCUSABLE = 'a[href],button,input,textarea,select,[tabindex]';

  function focusables() {
    return Array.prototype.filter.call(panel.querySelectorAll(FOCUSABLE), function (el) {
      if (el.disabled) return false;
      if (el.getAttribute('tabindex') === '-1') return false;
      return el.offsetWidth > 0 || el.offsetHeight > 0 || el === document.activeElement;
    });
  }

  function onKey(e) {
    if (!open_) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      e.stopPropagation();      /* the shell also closes its rail on Escape */
      close();
      return;
    }
    if (e.altKey && (e.key === 'k' || e.key === 'K')) {
      /* the shell's own Alt+K ignores keydowns inside an input, which is exactly
         where the caret is while the desk is open, so close it from here */
      e.preventDefault();
      e.stopPropagation();
      close();
      return;
    }
    if (e.key !== 'Tab') return;
    const list = focusables();
    if (!list.length) return;
    const first = list[0], last = list[list.length - 1];
    const here = document.activeElement;
    if (!panel.contains(here)) { e.preventDefault(); first.focus(); return; }
    if (e.shiftKey && here === first) { e.preventDefault(); last.focus(); }
    else if (!e.shiftKey && here === last) { e.preventDefault(); first.focus(); }
  }

  function onHistClick(e) {
    const ex = e.target.closest('[data-ex]');
    if (ex) {
      const row = state.history[+ex.dataset.ex];
      if (row) { elems.input.value = row.src; elems.input.focus(); recall = -1; preview(); }
      return;
    }
    const send = e.target.closest('[data-send]');
    if (send) { sendRow(state.history[+send.dataset.send]); return; }
    const val = e.target.closest('[data-val]');
    if (val) {
      const row = state.history[+val.dataset.val];
      if (!row || !row.ok) return;
      /* The row holds the exact double; `raw` under it is a 10-figure reading of it.
         Inserting the reading would make clicking a value and carrying it with `ans`
         give different answers three steps later, so insert the value itself. */
      insert(String(row.value));
    }
  }

  function insert(text) {
    const el = elems.input;
    el.focus();
    const a = el.selectionStart, b = el.selectionEnd;
    if (typeof el.setRangeText === 'function') el.setRangeText(text, a, b, 'end');
    else el.value = el.value.slice(0, a) + text + el.value.slice(b);
    recall = -1;
    preview();
  }

  /* ================================================================ open/close */

  function show(tab) {
    const t = tab === 'notes' ? 'notes' : 'calc';
    state.tab = t;
    elems.tabs.forEach(function (b) {
      const on = b.dataset.tab === t;
      b.setAttribute('aria-selected', on ? 'true' : 'false');
      /* A tablist is one Tab stop, not one per tab. That is what role=tab
         promises, and it is what makes the arrow keys below load-bearing
         rather than decorative. */
      b.tabIndex = on ? 0 : -1;
    });
    elems.panes.calc.classList.toggle('on', t === 'calc');
    elems.panes.notes.classList.toggle('on', t === 'notes');
    if (t === 'notes') { paintNotes(); elems.ta.focus(); }
    else { paintHistory(); elems.input.focus(); }
    saveState();
  }

  /* Left/Right/Home/End across the tablist. With the roving tabindex above, this
     is the only keyboard route to the unselected tab. */
  function onTabKey(e) {
    const i = elems.tabs.indexOf(e.target);
    if (i < 0) return;
    const n = elems.tabs.length;
    let j = -1;
    if (e.key === 'ArrowRight') j = (i + 1) % n;
    else if (e.key === 'ArrowLeft') j = (i - 1 + n) % n;
    else if (e.key === 'Home') j = 0;
    else if (e.key === 'End') j = n - 1;
    if (j < 0) return;
    e.preventDefault();
    /* show() ends by focusing the pane's own field, which is right for a click
       and wrong for an arrow key: focus belongs on the tab being arrowed to. */
    show(elems.tabs[j].dataset.tab);
    elems.tabs[j].focus();
  }

  function open(tab) {
    if (typeof document === 'undefined') return;
    loadAll();
    ensureStyle();
    if (!back) build();
    if (open_) { show(tab || state.tab); return; }

    lastFocus = document.activeElement;
    open_ = true;
    back.hidden = false;
    if (!back.isConnected) document.body.appendChild(back);

    /* the rest of the page is not reachable while this is up; say so for anything
       reading the tree, and put it back exactly as it was found */
    const app = document.querySelector('.app');
    if (app && !app.hasAttribute('aria-hidden')) { app.setAttribute('aria-hidden', 'true'); hidden = app; }

    paintAngle();
    paintWhere();
    paintHistory();
    paintNotes();
    applyGeom();
    show(tab || state.tab);

    /* every listener that could touch a keystroke goes on at open and comes off at
       close, so a closed desk is genuinely not listening */
    document.addEventListener('keydown', onKey, true);
    window.addEventListener('resize', onWinResize);
    window.addEventListener('pagehide', flushSave);
    document.addEventListener('visibilitychange', onHide);
    elems.hist.addEventListener('click', onHistClick);
    elems.hist.addEventListener('keydown', onHistKey);
    markTrigger(true);
  }

  function onHistKey(e) {
    if (e.key !== 'Enter' && e.key !== ' ') return;
    if (!e.target.closest('[data-val]')) return;
    e.preventDefault();
    onHistClick(e);
  }

  function onHide() { if (document.visibilityState === 'hidden') flushSave(); }

  /* The toolbar button opens this dialog, so its expanded state is part of the
     dialog's contract. Queried each time rather than cached: the shell owns its
     header markup and re-renders it, and a cached node would be kept honest
     forever while the live one never was. */
  function markTrigger(on) {
    const b = document.getElementById('desk-btn');
    if (b) b.setAttribute('aria-expanded', on ? 'true' : 'false');
  }

  function close() {
    if (!open_) return;
    flushSave();
    saveState();
    open_ = false;

    document.removeEventListener('keydown', onKey, true);
    window.removeEventListener('resize', onWinResize);
    window.removeEventListener('pagehide', flushSave);
    document.removeEventListener('visibilitychange', onHide);
    elems.hist.removeEventListener('click', onHistClick);
    elems.hist.removeEventListener('keydown', onHistKey);

    if (hidden) { hidden.removeAttribute('aria-hidden'); hidden = null; }
    back.hidden = true;
    markTrigger(false);

    /* Focus goes back to whatever had it. Losing it to <body> means the next Tab
       starts from the top of the page, which is a long way from the lesson. */
    const to = lastFocus;
    lastFocus = null;
    if (to && to.isConnected && typeof to.focus === 'function') {
      try { to.focus({ preventScroll: true }); } catch (e) { to.focus(); }
    }
  }

  function context(info) {
    const next = info || {};
    const id = next.lessonId ? String(next.lessonId) : null;
    const title = next.title ? String(next.title) : '';
    if (id === ctx.lessonId && title === ctx.title) return;

    if (open_) flushSave();                 /* the old note, before the pointer moves */
    loadAll();
    ctx = { lessonId: id, title: title };
    if (id && notes && notes.lessons[id] && title) notes.lessons[id].title = title;
    /* `pick` is left alone: a learner who has deliberately parked on the scratch pad
       should still be on it after moving to the next lesson. With pick on 'lesson'
       and no lesson to show, currentNote falls back to the scratch pad anyway. */
    if (open_) { paintWhere(); paintNotes(); }
  }

  return {
    open: open,
    close: close,
    toggle: function (tab) { if (open_) close(); else open(tab); },
    isOpen: function () { return open_; },
    context: context,

    /* the parser, headless — useful anywhere a typed value needs reading, and the
       only way to test the language without a DOM */
    evaluate: function (src, opts) {
      const o = opts || {};
      return evaluate(src, {
        vars: o.vars || {},
        ans: o.ans === undefined ? null : o.ans,
        deg: o.deg === undefined ? true : !!o.deg,
      });
    },
    format: format,

    /* The stylesheet, so tools/verify_theme.mjs can measure this file's surfaces in
       both themes the way it measures every other file's. Exposed rather than parsed
       out of the source, so the gate reads what actually ships. */
    css: deskCss,
  };
})();
