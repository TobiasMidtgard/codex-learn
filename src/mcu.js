/* ============ mcu ============
 *
 * A small language with the shape of an Arduino sketch, and a machine that runs it a
 * few instructions at a time.
 *
 *   Lex      source to tokens, carrying the line each one came off
 *   Parse    tokens to a tree, refusing what this subset does not have and saying so
 *   Machine  the tree, executed as a coroutine that can be stopped mid-statement
 *
 * Nothing here evaluates learner text as JavaScript. eval and new Function would be a
 * dozen lines instead of nine hundred, and they would hand a sketch the whole browser:
 * the page's own variables, the network, the storage the rest of the app keeps a
 * learner's work in. A tree walker can only do what this file gives it a way to do,
 * which is arithmetic and twelve pins.
 *
 * THE PART THAT IS NOT OBVIOUS is that the machine cannot simply be run. An analogue
 * solver advances in time steps, and a microcontroller has to advance beside it; and
 * the correct shape of every sketch anyone will write here is
 *
 *     void loop() { ... }        called again, forever
 *
 * which does not terminate and is not supposed to. Running loop() to completion works
 * exactly until the first learner writes `while (digitalRead(2) == LOW) ;` — a
 * perfectly good way to wait for a button, and a browser tab that never paints again.
 * So execution is a generator: it is handed a budget of instructions, it runs until
 * the budget is gone or it has asked to sleep, and it SUSPENDS with its call stack,
 * its loop counters and its half-finished expression intact. The solver takes its time
 * step, and the machine is handed the next budget. An infinite loop() is then the
 * ordinary case rather than the fatal one.
 *
 * Time is the simulation's time, not a count of instructions: delay() sleeps until the
 * simulated clock passes a wake time, and millis() reads that same clock. The
 * instruction budget decides how much a sketch gets DONE between two time steps; it
 * does not decide what time it is. Those being separate is why a sketch that computes
 * a lot and a sketch that computes nothing both see the same circuit at the same
 * moment.
 */
const MCU = (function () {

  /* ---- the numbers that define the machine ----
   *
   * OPS_PER_SECOND is not a clock speed and this is not an instruction set: one "op"
   * here is one statement or one operator, which no real processor charges the same
   * for. It is quoted anyway, and quoted in the panel, because a sketch has to get a
   * defined amount done per time step or the answer depends on how fast the reader's
   * laptop is — and an arbitrary number that is stated beats an arbitrary number that
   * is hidden. A megaop per second is the right order for a small 8-bit part running
   * interpreted-looking C, and it makes the arithmetic easy to check by hand: a
   * hundred ops is a hundred microseconds. */
  const OPS_PER_SECOND = 1e6;

  /* Ops a single time step may ever be given, however long the step is. A transient
     asked to cover an hour would otherwise hand the machine three billion ops in one
     go and hang the tab in the one place all this machinery exists to stop it. */
  const OPS_MAX_STEP = 20000;

  /* Recursion. Deep enough for anything worth writing at this level, shallow enough
     that the generator delegation underneath it cannot blow the JavaScript stack —
     which would surface as a browser error naming a line of THIS file, and a learner
     debugging their own sketch does not need to read mine. */
  const MAX_DEPTH = 64;

  /* The watchdog. Running out of instructions is NORMAL and is not a fault: it is
     what suspension is for. What is a fault is a sketch that runs out of instructions
     over and over while never touching a pin, never printing, never sleeping and never
     finishing an iteration of loop() — because that sketch cannot affect the circuit
     or observe it, and no number of further time steps will change that. Fifty steps
     is long enough that a slow calculation between two digitalWrites is not caught. */
  const STALL_STEPS = 50;

  /* Console lines kept. A sketch printing every step of a long transient will produce
     thousands, and a panel that has to lay out thousands is a panel that stops
     scrolling smoothly. The cut is reported rather than silent. */
  const CONSOLE_MAX = 400;

  /* ---------------------------------------------------------------- values
   *
   * Two kinds, and the split is the reason `3 / 2` is 1 here as it is on the hardware.
   * A number carries whether it is a float; two ints divided give an int, and an int
   * assigned into a float variable becomes one. Getting this wrong is not a detail —
   * `int pct = 100 * x / total;` behaving like real arithmetic would teach a learner
   * that C does something it does not do, and the day they run the same sketch on a
   * board it would give a different answer with nothing on screen to explain why.
   *
   * A string exists only so print() has something to print. Arithmetic on one is a
   * fault rather than a concatenation, because this subset has no strings to build. */
  function num(v, f) { return { v: v, f: !!f }; }
  function str(s) { return { s: s }; }
  const ZERO = num(0, false);

  /* An int is 32 bits and wraps, which is what the bitwise operators need to mean
     anything. Not 16, which is what `int` is on an AVR: the machine drawn on this
     canvas is a made-up one, and a width that matches JavaScript's own bitwise
     operators cannot disagree with them. Stated in the panel. */
  function toInt(v) { return v | 0; }

  function isNum(x) { return x && x.s === undefined; }

  /* ---------------------------------------------------------------- faults
   *
   * Every fault carries the line it happened on. A learner debugging a sketch inside a
   * circuit simulator is holding two things that could be wrong, and the first job of
   * any message here is to say which one this is and where. */
  function Fault(line, message) {
    return { mcuFault: true, line: line, message: message };
  }
  function fail(line, message) { throw Fault(line, message); }

  /* ---------------------------------------------------------------- lexer */

  const PUNCT = [
    '<<=', '>>=', '&&', '||', '==', '!=', '<=', '>=', '<<', '>>', '++', '--',
    '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=',
    '{', '}', '(', ')', '[', ']', ';', ',', '.', '+', '-', '*', '/', '%',
    '<', '>', '=', '!', '&', '|', '^', '~', '?', ':',
  ];

  /* The words that introduce a type. `long` and `double` are accepted and are the same
     two types as `int` and `float` — a machine with one integer width and one float
     width has nothing to widen to, and silently accepting a keyword that promises more
     precision than exists would be the lie. The panel says which are aliases. */
  const TYPES = {
    int: 'int', long: 'int', byte: 'int', bool: 'int', boolean: 'int', char: 'int',
    float: 'float', double: 'float', void: 'void',
  };

  function lex(src, defines) {
    const out = [];
    let i = 0, line = 1;
    const n = src.length;

    function push(t, text) { out.push({ t: t, s: text, line: line }); }

    while (i < n) {
      const c = src[i];
      if (c === '\n') { line++; i++; continue; }
      if (c === ' ' || c === '\t' || c === '\r') { i++; continue; }

      /* comments, both spellings */
      if (c === '/' && src[i + 1] === '/') {
        while (i < n && src[i] !== '\n') i++;
        continue;
      }
      if (c === '/' && src[i + 1] === '*') {
        const at = line;
        i += 2;
        while (i < n && !(src[i] === '*' && src[i + 1] === '/')) { if (src[i] === '\n') line++; i++; }
        if (i >= n) fail(at, 'this block comment is never closed.');
        i += 2;
        continue;
      }

      /* Preprocessor. A sketch copied off a page begins with #include, and a great
         many begin with #define — so both are understood rather than rejected, and
         anything else on a # line is refused by name instead of being skipped into a
         silence the learner has to guess at. */
      if (c === '#') {
        let j = i;
        while (j < n && src[j] !== '\n') j++;
        const text = src.slice(i, j).trim();
        const inc = /^#\s*include\b/.test(text);
        const def = /^#\s*define\s+([A-Za-z_]\w*)\s+(.+)$/.exec(text);
        if (def) {
          const val = Number(def[2].trim());
          if (!isFinite(val)) {
            fail(line, '#define here has to give a plain number; "' + def[2].trim() +
              '" is not one, and this subset has no textual macros.');
          }
          defines[def[1]] = num(val, /[.eE]/.test(def[2]));
        } else if (!inc) {
          fail(line, 'the only preprocessor lines this subset understands are #include, ' +
            'which it ignores because every library it could name is already here or is ' +
            'not, and #define NAME <number>.');
        }
        i = j;
        continue;
      }

      /* a string, for print() and nothing else */
      if (c === '"') {
        let s = '';
        i++;
        while (i < n && src[i] !== '"') {
          if (src[i] === '\n') fail(line, 'this string runs off the end of the line.');
          if (src[i] === '\\') {
            const e = src[i + 1];
            s += e === 'n' ? '\n' : e === 't' ? '\t' : e === '\\' ? '\\' : e === '"' ? '"' : e;
            i += 2;
            continue;
          }
          s += src[i++];
        }
        if (i >= n) fail(line, 'this string is never closed.');
        i++;
        push('str', s);
        continue;
      }

      /* a character literal is a number, which is what it is in C */
      if (c === "'") {
        const ch = src[i + 1] === '\\' ? { n: '\n', t: '\t', '0': '\0' }[src[i + 2]] : src[i + 1];
        const end = src[i + 1] === '\\' ? i + 3 : i + 2;
        if (src[end] !== "'") fail(line, "a character literal holds exactly one character.");
        out.push({ t: 'num', v: num(String(ch).charCodeAt(0), false), line: line });
        i = end + 1;
        continue;
      }

      if (c >= '0' && c <= '9') {
        let j = i, isF = false;
        if (c === '0' && (src[i + 1] === 'x' || src[i + 1] === 'X')) {
          j = i + 2;
          while (j < n && /[0-9a-fA-F]/.test(src[j])) j++;
          out.push({ t: 'num', v: num(parseInt(src.slice(i, j), 16) | 0, false), line: line });
          i = j;
          continue;
        }
        if (c === '0' && (src[i + 1] === 'b' || src[i + 1] === 'B')) {
          j = i + 2;
          while (j < n && /[01]/.test(src[j])) j++;
          out.push({ t: 'num', v: num(parseInt(src.slice(i + 2, j), 2) | 0, false), line: line });
          i = j;
          continue;
        }
        while (j < n && /[0-9]/.test(src[j])) j++;
        if (src[j] === '.') { isF = true; j++; while (j < n && /[0-9]/.test(src[j])) j++; }
        if (src[j] === 'e' || src[j] === 'E') {
          isF = true;
          j++;
          if (src[j] === '+' || src[j] === '-') j++;
          while (j < n && /[0-9]/.test(src[j])) j++;
        }
        let text = src.slice(i, j);
        /* the float and long suffixes a datasheet's example code is full of */
        if (/[fF]/.test(src[j] || '')) { isF = true; j++; }
        else if (/[uUlL]/.test(src[j] || '')) { while (/[uUlL]/.test(src[j] || '')) j++; }
        out.push({ t: 'num', v: num(isF ? parseFloat(text) : (parseInt(text, 10) | 0), isF), line: line });
        i = j;
        continue;
      }

      if (/[A-Za-z_]/.test(c)) {
        let j = i;
        while (j < n && /[A-Za-z0-9_]/.test(src[j])) j++;
        push('id', src.slice(i, j));
        i = j;
        continue;
      }

      const hit = PUNCT.filter(function (p) { return src.startsWith(p, i); })[0];
      if (!hit) fail(line, 'there is no "' + c + '" in this language.');
      push('op', hit);
      i += hit.length;
    }
    out.push({ t: 'end', s: '', line: line });
    return out;
  }

  /* ---------------------------------------------------------------- parser
   *
   * Recursive descent, ordinary precedence climbing, and one rule that is worth
   * stating: everything this subset does NOT have is refused HERE, by name, with a
   * line — not at run time and not by quietly doing something else. A learner who
   * writes an array gets told there are no arrays, on the line the bracket is on,
   * before anything runs. Half of what makes a small language usable is that its
   * edges are where it says they are. */
  function parse(tokens) {
    let k = 0;
    function peek() { return tokens[k]; }
    function at(s) { const t = tokens[k]; return (t.t === 'op' || t.t === 'id') && t.s === s; }
    function eat(s) { if (at(s)) { k++; return true; } return false; }
    function want(s, what) {
      if (!eat(s)) {
        fail(peek().line, 'expected "' + s + '"' + (what ? ' ' + what : '') +
          ', found "' + (peek().s || peek().t) + '".');
      }
    }
    function ident(what) {
      const t = peek();
      if (t.t !== 'id') fail(t.line, 'expected ' + what + ', found "' + (t.s || t.t) + '".');
      k++;
      return t.s;
    }

    /* ---- expressions ---- */
    function primary() {
      const t = peek();
      if (t.t === 'num') { k++; return { k: 'num', v: t.v, line: t.line }; }
      if (t.t === 'str') { k++; return { k: 'str', v: t.s, line: t.line }; }
      if (at('(')) { k++; const e = expr(); want(')', 'to close this group'); return e; }
      if (at('-') || at('+') || at('!') || at('~')) {
        k++;
        return { k: 'un', op: t.s, a: unary(), line: t.line };
      }
      if (at('++') || at('--')) {
        k++;
        const target = unary();
        if (target.k !== 'var') fail(t.line, t.s + ' has to be applied to a variable.');
        return { k: 'pre', op: t.s, name: target.name, line: t.line };
      }
      if (t.t === 'id') {
        k++;
        let name = t.s;
        /* Serial.println and its siblings. The dot is allowed only here, because this
           subset has no objects — Serial is a name with a full stop in it, and saying
           so is better than pretending to a member lookup that does not exist. */
        if (at('.')) {
          k++;
          const member = ident('a name after the dot');
          if (name !== 'Serial') {
            fail(t.line, 'there are no objects in this subset; "' + name + '." is not ' +
              'something you can write. Serial.print and Serial.println exist as names ' +
              'with a dot in them, and nothing else does.');
          }
          name = 'Serial.' + member;
        }
        if (at('(')) {
          k++;
          const args = [];
          if (!at(')')) {
            do { args.push(expr()); } while (eat(','));
          }
          want(')', 'to close the argument list');
          return { k: 'call', name: name, args: args, line: t.line };
        }
        if (at('[')) {
          fail(t.line, 'there are no arrays in this subset — only int and float ' +
            'variables. Whatever this was going to hold, hold it in named variables ' +
            'or work it out as you go.');
        }
        return { k: 'var', name: name, line: t.line };
      }
      fail(t.line, 'expected a value, found "' + (t.s || t.t) + '".');
    }

    function unary() {
      let e = primary();
      while (at('++') || at('--')) {
        const t = peek();
        k++;
        if (e.k !== 'var') fail(t.line, t.s + ' has to be applied to a variable.');
        e = { k: 'post', op: t.s, name: e.name, line: t.line };
      }
      return e;
    }

    /* precedence, loosest last; && and || are separate because they short-circuit */
    const LEVELS = [
      ['*', '/', '%'], ['+', '-'], ['<<', '>>'],
      ['<', '<=', '>', '>='], ['==', '!='], ['&'], ['^'], ['|'],
    ];
    function binary(level) {
      if (level < 0) return unary();
      let left = binary(level - 1);
      for (;;) {
        const t = peek();
        if (t.t !== 'op' || LEVELS[level].indexOf(t.s) < 0) return left;
        k++;
        left = { k: 'bin', op: t.s, a: left, b: binary(level - 1), line: t.line };
      }
    }
    function logAnd() {
      let left = binary(LEVELS.length - 1);
      while (at('&&')) { const l = peek().line; k++; left = { k: 'and', a: left, b: binary(LEVELS.length - 1), line: l }; }
      return left;
    }
    function logOr() {
      let left = logAnd();
      while (at('||')) { const l = peek().line; k++; left = { k: 'or', a: left, b: logAnd(), line: l }; }
      return left;
    }
    function ternary() {
      const c = logOr();
      if (!at('?')) return c;
      const l = peek().line;
      k++;
      const a = expr();
      want(':', 'in this conditional');
      return { k: 'if3', c: c, a: a, b: ternary(), line: l };
    }
    const ASSIGN = ['=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>='];
    function expr() {
      const left = ternary();
      const t = peek();
      if (t.t === 'op' && ASSIGN.indexOf(t.s) >= 0) {
        if (left.k !== 'var') {
          fail(t.line, 'the left of "' + t.s + '" has to be a variable.');
        }
        k++;
        return { k: 'set', op: t.s, name: left.name, a: expr(), line: t.line };
      }
      return left;
    }

    /* ---- statements ---- */
    function typeHere() {
      /* `const int x = 3;` is how a pin number gets a name, so const is accepted and
         then ignored: nothing in this subset can write through an alias anyway, so
         enforcing it would refuse programs for a danger the machine does not have. */
      let j = k;
      if (tokens[j].t === 'id' && tokens[j].s === 'const') j++;
      if (tokens[j].t === 'id' && tokens[j].s === 'unsigned') j++;
      const t = tokens[j];
      if (t.t !== 'id' || !TYPES[t.s]) return null;
      /* a type only starts a declaration when a name follows it */
      if (tokens[j + 1].t !== 'id') return null;
      return { type: TYPES[t.s], at: j };
    }

    function block() {
      const line = peek().line;
      want('{', 'to open this block');
      const body = [];
      while (!at('}')) {
        if (peek().t === 'end') fail(line, 'this block is never closed.');
        body.push(statement());
      }
      k++;
      return { k: 'block', body: body, line: line };
    }

    function decl() {
      const info = typeHere();
      k = info.at + 1;
      const line = peek().line;
      const names = [];
      do {
        const name = ident('a variable name');
        if (at('[')) {
          fail(peek().line, 'there are no arrays in this subset — only single int and ' +
            'float variables.');
        }
        names.push({ name: name, init: eat('=') ? expr() : null });
      } while (eat(','));
      return { k: 'decl', type: info.type, names: names, line: line };
    }

    function statement() {
      const t = peek();
      if (at('{')) return block();
      if (at(';')) { k++; return { k: 'block', body: [], line: t.line }; }
      if (at('if')) {
        k++;
        want('(', 'after if');
        const c = expr();
        want(')', 'to close the condition');
        const a = statement();
        const b = eat('else') ? statement() : null;
        return { k: 'if', c: c, a: a, b: b, line: t.line };
      }
      if (at('while')) {
        k++;
        want('(', 'after while');
        const c = expr();
        want(')', 'to close the condition');
        return { k: 'while', c: c, body: statement(), line: t.line };
      }
      if (at('for')) {
        k++;
        want('(', 'after for');
        const init = at(';') ? null : (typeHere() ? decl() : { k: 'expr', a: expr(), line: t.line });
        want(';', 'after the initialiser');
        const c = at(';') ? null : expr();
        want(';', 'after the condition');
        const post = at(')') ? null : expr();
        want(')', 'to close the for header');
        return { k: 'for', init: init, c: c, post: post, body: statement(), line: t.line };
      }
      if (at('return')) {
        k++;
        const a = at(';') ? null : expr();
        want(';', 'after return');
        return { k: 'ret', a: a, line: t.line };
      }
      if (at('break')) { k++; want(';', 'after break'); return { k: 'break', line: t.line }; }
      if (at('continue')) { k++; want(';', 'after continue'); return { k: 'cont', line: t.line }; }
      if (typeHere()) {
        const d = decl();
        want(';', 'after this declaration');
        return d;
      }
      const e = expr();
      want(';', 'after this statement');
      return { k: 'expr', a: e, line: t.line };
    }

    /* ---- the file ---- */
    const fns = {};
    const globals = [];
    while (peek().t !== 'end') {
      const info = typeHere();
      if (!info) {
        fail(peek().line, 'expected a function or a variable declaration at the top ' +
          'level, found "' + (peek().s || peek().t) + '". Every statement has to be ' +
          'inside setup(), loop(), or a function you write.');
      }
      const retType = info.type;
      k = info.at + 1;
      const nameTok = peek();
      const name = ident('a name');
      if (at('(')) {
        k++;
        const params = [];
        if (!at(')')) {
          do {
            const pt = typeHere();
            if (!pt) fail(peek().line, 'every parameter needs a type.');
            k = pt.at + 1;
            params.push({ type: pt.type, name: ident('a parameter name') });
          } while (eat(','));
        }
        want(')', 'to close the parameter list');
        if (eat(';')) continue;                    /* a forward declaration; harmless */
        if (fns[name]) fail(nameTok.line, 'there is already a function called ' + name + '.');
        fns[name] = { name: name, ret: retType, params: params, body: block(), line: nameTok.line };
        continue;
      }
      /* a global, declared the same way a local is */
      k = info.at + 1;
      const names = [];
      do {
        const nm = ident('a variable name');
        names.push({ name: nm, init: eat('=') ? expr() : null });
      } while (eat(','));
      want(';', 'after this declaration');
      globals.push({ k: 'decl', type: retType, names: names, line: nameTok.line });
    }
    return { fns: fns, globals: globals };
  }

  /* ---------------------------------------------------------------- constants
   *
   * The names a sketch expects to already exist. Deliberately short: every one of
   * these is a promise that the thing it names behaves the way the board it came from
   * behaves, and a name defined here that the pin model does not honour is worse than
   * a name that is missing, because a missing name is reported on its line. */
  const CONSTANTS = {
    HIGH: num(1, false), LOW: num(0, false),
    INPUT: num(0, false), OUTPUT: num(1, false), INPUT_PULLUP: num(2, false),
    true: num(1, false), false: num(0, false),
    PI: num(Math.PI, true), TWO_PI: num(2 * Math.PI, true), HALF_PI: num(Math.PI / 2, true),
    A0: num(14, false), A1: num(15, false), A2: num(16, false), A3: num(17, false),
  };

  /* ---------------------------------------------------------------- machine */

  function truthy(x) { return isNum(x) && x.v !== 0; }

  function show(x) {
    if (!isNum(x)) return x.s;
    /* the two decimals Serial.print gives a float, and no decimals for an int — the
       distinction the learner is being taught, visible in the output that teaches it */
    return x.f ? x.v.toFixed(2) : String(x.v | 0);
  }

  function make(program, board, opts) {
    opts = opts || {};
    const fns = program.fns;

    const M = {
      t: 0,                 /* the simulation clock, in seconds */
      line: 0,              /* the line last reached, for a fault or a stall */
      fault: null,
      console: [],
      dropped: 0,
      wake: 0,              /* delay() sleeps until the clock passes this */
      left: 0,              /* instructions remaining in this time step */
      ops: 0,               /* instructions since the machine started */
      depth: 0,
      loops: 0,             /* completed iterations of loop() */
      inSetup: true,
      io: false,            /* did anything observable happen this step */
      stall: 0,
      suspended: false,
    };

    /* ---- scopes ----
       A chain of plain objects. Each holds the declared TYPE beside the value, because
       assignment converts to the declared type and not to the type of what is being
       assigned — which is the whole of why `int` division truncates and a float
       variable holding an int result still prints two decimals. */
    function scope(parent) { return { vars: {}, up: parent }; }
    const globalScope = scope(null);

    function lookup(sc, name) {
      for (let s = sc; s; s = s.up) if (s.vars[name] !== undefined) return s.vars[name];
      return null;
    }
    function declare(sc, name, type, val, line) {
      if (Object.prototype.hasOwnProperty.call(sc.vars, name)) {
        fail(line, name + ' is already declared in this block.');
      }
      sc.vars[name] = { type: type, val: cast(type, val, line) };
    }
    function cast(type, x, line) {
      if (!isNum(x)) fail(line, 'a string cannot be stored in a ' + type + ' variable.');
      if (type === 'float') return num(x.v, true);
      return num(toInt(Math.trunc(x.v)), false);
    }

    /* ---- console ---- */
    function emit(text) {
      M.io = true;
      if (M.console.length >= CONSOLE_MAX) { M.dropped++; return; }
      const last = M.console.length - 1;
      /* print() continues the line print() started; println() ends one. Held as a
         partial last entry so the panel can show a half-written line as it is. */
      if (last >= 0 && M.console[last].open) {
        M.console[last].text += text;
      } else {
        M.console.push({ text: text, open: true });
      }
      const cur = M.console[M.console.length - 1];
      const nl = cur.text.indexOf('\n');
      if (nl >= 0) {
        const parts = cur.text.split('\n');
        M.console.pop();
        for (let q = 0; q < parts.length - 1; q++) M.console.push({ text: parts[q], open: false });
        if (parts[parts.length - 1] !== '') M.console.push({ text: parts[parts.length - 1], open: true });
      }
    }

    /* ---- built-in functions ----
     *
     * `n` is how many arguments, `f` computes, and `block` marks the two that suspend:
     * a builtin that sleeps has to be a generator, because sleeping means yielding out
     * through every frame between here and the driver. */
    function pin(x, line) {
      if (!isNum(x)) fail(line, 'a pin number has to be a number.');
      const p = toInt(Math.trunc(x.v));
      if (board.pinName(p) === null) {
        fail(line, 'there is no pin ' + p + ' on this part. It has ' + board.pinList() + '.');
      }
      return p;
    }

    const BUILTIN = {
      pinMode: { n: 2, f: function (a, line) {
        const p = pin(a[0], line);
        const m = toInt(a[1].v);
        if (m !== 0 && m !== 1 && m !== 2) {
          fail(line, 'pinMode takes INPUT, OUTPUT or INPUT_PULLUP; it was given ' + m + '.');
        }
        board.setMode(p, m === 1 ? 'out' : m === 2 ? 'pullup' : 'in');
        M.io = true;
        return ZERO;
      } },
      digitalWrite: { n: 2, f: function (a, line) {
        const p = pin(a[0], line);
        if (board.mode(p) !== 'out') {
          fail(line, 'pin ' + board.pinName(p) + ' has not been set to OUTPUT, so writing ' +
            'to it does nothing to the circuit. On real hardware this quietly switches the ' +
            'pull-up instead, which is a bug you would spend an evening on; here it is ' +
            'this message. Call pinMode(' + board.pinName(p) + ', OUTPUT) in setup().');
        }
        board.drive(p, truthy(a[1]) ? 1 : 0);
        M.io = true;
        return ZERO;
      } },
      analogWrite: { n: 2, f: function (a, line) {
        const p = pin(a[0], line);
        if (board.mode(p) !== 'out') {
          fail(line, 'pin ' + board.pinName(p) + ' has not been set to OUTPUT. ' +
            'Call pinMode(' + board.pinName(p) + ', OUTPUT) in setup().');
        }
        const d = Math.min(Math.max(toInt(Math.trunc(a[1].v)), 0), 255);
        board.drive(p, d / 255);
        M.io = true;
        return ZERO;
      } },
      digitalRead: { n: 1, f: function (a, line) {
        M.io = true;
        return num(board.readDigital(pin(a[0], line)), false);
      } },
      analogRead: { n: 1, f: function (a, line) {
        const p = pin(a[0], line);
        const c = board.readAnalog(p);
        /* Not every pin has a converter behind it, and reading one that has not is the
           mistake that produces a plausible-looking zero. The board answers null rather
           than a number so the refusal happens here, on the line, with the pins that
           would have worked named. */
        if (c === null) {
          fail(line, 'pin ' + board.pinName(p) + ' has no analogue-to-digital converter ' +
            'behind it. The pins that do are ' + board.adcList() + '; every other pin can ' +
            'only tell you which side of the logic threshold it is on, with digitalRead.');
        }
        M.io = true;
        return num(c, false);
      } },
      millis: { n: 0, f: function () { return num(Math.floor(M.t * 1000) | 0, false); } },
      micros: { n: 0, f: function () { return num(Math.floor(M.t * 1e6) | 0, false); } },
      delay: { n: 1, block: function* (a, line) {
        if (!isNum(a[0])) fail(line, 'delay takes a number of milliseconds.');
        yield* sleep(Math.max(a[0].v, 0) / 1000);
        return ZERO;
      } },
      delayMicroseconds: { n: 1, block: function* (a, line) {
        if (!isNum(a[0])) fail(line, 'delayMicroseconds takes a number.');
        yield* sleep(Math.max(a[0].v, 0) / 1e6);
        return ZERO;
      } },
      print: { n: -1, f: function (a) { a.forEach(function (x) { emit(show(x)); }); return ZERO; } },
      println: { n: -1, f: function (a) { a.forEach(function (x) { emit(show(x)); }); emit('\n'); return ZERO; } },
      map: { n: 5, f: function (a, line) {
        const lo = a[1].v, hi = a[2].v;
        if (hi === lo) fail(line, 'map cannot work with an input range of zero width.');
        const r = (a[0].v - lo) * (a[4].v - a[3].v) / (hi - lo) + a[3].v;
        /* integer in, integer out, truncated — which is what the Arduino one does, and
           the reason map(v, 0, 1023, 0, 5) gives you 0 or 1 and never 2.5 */
        const anyF = a.some(function (x) { return x.f; });
        return anyF ? num(r, true) : num(toInt(Math.trunc(r)), false);
      } },
      constrain: { n: 3, f: function (a) {
        const v = Math.min(Math.max(a[0].v, a[1].v), a[2].v);
        return num(a[0].f ? v : toInt(Math.trunc(v)), a[0].f);
      } },
      min: { n: 2, f: function (a) { return a[0].v <= a[1].v ? a[0] : a[1]; } },
      max: { n: 2, f: function (a) { return a[0].v >= a[1].v ? a[0] : a[1]; } },
      abs: { n: 1, f: function (a) { return num(Math.abs(a[0].v), a[0].f); } },
      sqrt: { n: 1, f: function (a, line) {
        if (a[0].v < 0) fail(line, 'sqrt of a negative number has no answer here.');
        return num(Math.sqrt(a[0].v), true);
      } },
      pow: { n: 2, f: function (a) { return num(Math.pow(a[0].v, a[1].v), true); } },
      sin: { n: 1, f: function (a) { return num(Math.sin(a[0].v), true); } },
      cos: { n: 1, f: function (a) { return num(Math.cos(a[0].v), true); } },
      tan: { n: 1, f: function (a) { return num(Math.tan(a[0].v), true); } },
      floor: { n: 1, f: function (a) { return num(Math.floor(a[0].v), a[0].f); } },
      ceil: { n: 1, f: function (a) { return num(Math.ceil(a[0].v), a[0].f); } },
      round: { n: 1, f: function (a) { return num(Math.round(a[0].v) | 0, false); } },
    };
    /* Serial is the same three functions under the names a sketch off a web page uses.
       begin() is accepted and does nothing, because there is no serial port here and
       there is no baud rate to get wrong — the console is the port. */
    BUILTIN['Serial.print'] = BUILTIN.print;
    BUILTIN['Serial.println'] = BUILTIN.println;
    BUILTIN['Serial.begin'] = { n: -1, f: function () { return ZERO; } };

    function* sleep(secs) {
      M.io = true;
      M.wake = M.t + secs;
      /* Yielding until the clock has passed the wake time, rather than once: the
         driver resumes this generator whenever it has budget, and a delay that woke on
         the first resume would be a delay of one time step however long it asked for. */
      while (M.t < M.wake) yield;
    }

    /* ---- the walker ----
     *
     * One op is charged per statement, per operator and per function call, and the
     * budget is checked at the same places. A `yield` here is what suspension IS: the
     * whole JavaScript call stack between the driver and this point stays alive,
     * holding the sketch's own stack inside it, and resuming is one call to next().
     *
     * THE INVARIANT THE DRIVER DEPENDS ON is that no cycle in a running sketch is free.
     * Every way of getting back to where you were passes through either a loop, whose
     * back edge ticks, or a function call, which ticks on the way in — and the machine's
     * own `for (;;) loop()` at the bottom of this file is a call, so it ticks too. Break
     * that and `void loop() { }` becomes a driver spinning on a generator that yields
     * without ever spending anything, which is the hang all of this exists to prevent
     * and is exactly how it was first written. */
    function* tick(line) {
      M.ops++;
      M.line = line;
      if (--M.left <= 0) yield;
    }

    const BREAK = { sig: 'break' }, CONT = { sig: 'continue' };

    function* evalNode(node, sc) {
      switch (node.k) {
        case 'num': return node.v;
        case 'str': return str(node.v);
        case 'var': {
          const slot = lookup(sc, node.name);
          if (slot) return slot.val;
          if (CONSTANTS[node.name]) return CONSTANTS[node.name];
          if (program.defines[node.name]) return program.defines[node.name];
          if (fns[node.name] || BUILTIN[node.name]) {
            fail(node.line, node.name + ' is a function; it needs brackets after it.');
          }
          fail(node.line, 'there is nothing called ' + node.name + ' here. Declare it ' +
            'with a type — int ' + node.name + ' = 0; — before you use it.');
          break;
        }
        case 'un': {
          yield* tick(node.line);
          const a = yield* evalNode(node.a, sc);
          if (!isNum(a)) fail(node.line, 'a string has no arithmetic.');
          if (node.op === '-') return num(-a.v, a.f);
          if (node.op === '+') return a;
          if (node.op === '!') return num(a.v === 0 ? 1 : 0, false);
          return num(~toInt(a.v), false);
        }
        case 'pre': case 'post': {
          yield* tick(node.line);
          const slot = lookup(sc, node.name);
          if (!slot) fail(node.line, 'there is nothing called ' + node.name + ' here.');
          const was = slot.val;
          const next = num(was.v + (node.op === '++' ? 1 : -1), was.f);
          slot.val = cast(slot.type, next, node.line);
          return node.k === 'pre' ? slot.val : was;
        }
        case 'bin': {
          yield* tick(node.line);
          const a = yield* evalNode(node.a, sc);
          const b = yield* evalNode(node.b, sc);
          return arith(node.op, a, b, node.line);
        }
        case 'and': {
          yield* tick(node.line);
          const a = yield* evalNode(node.a, sc);
          if (!truthy(a)) return num(0, false);
          return num(truthy(yield* evalNode(node.b, sc)) ? 1 : 0, false);
        }
        case 'or': {
          yield* tick(node.line);
          const a = yield* evalNode(node.a, sc);
          if (truthy(a)) return num(1, false);
          return num(truthy(yield* evalNode(node.b, sc)) ? 1 : 0, false);
        }
        case 'if3': {
          yield* tick(node.line);
          return truthy(yield* evalNode(node.c, sc))
            ? yield* evalNode(node.a, sc) : yield* evalNode(node.b, sc);
        }
        case 'set': {
          yield* tick(node.line);
          const slot = lookup(sc, node.name);
          if (!slot) {
            fail(node.line, 'there is nothing called ' + node.name + ' here. A variable ' +
              'has to be declared with a type before it can be assigned to.');
          }
          const rhs = yield* evalNode(node.a, sc);
          const val = node.op === '='
            ? rhs
            : arith(node.op.slice(0, node.op.length - 1), slot.val, rhs, node.line);
          slot.val = cast(slot.type, val, node.line);
          return slot.val;
        }
        case 'call': return yield* call(node, sc);
      }
      fail(node.line, 'this expression is not something the machine understands.');
    }

    function arith(op, a, b, line) {
      if (!isNum(a) || !isNum(b)) {
        fail(line, 'a string has no arithmetic; strings here are only for printing.');
      }
      const f = a.f || b.f;
      switch (op) {
        case '+': return f ? num(a.v + b.v, true) : num(toInt(a.v + b.v), false);
        case '-': return f ? num(a.v - b.v, true) : num(toInt(a.v - b.v), false);
        case '*': return f ? num(a.v * b.v, true) : num(toInt(Math.trunc(a.v * b.v)), false);
        case '/':
          if (b.v === 0) {
            fail(line, 'division by zero. ' + (f ? 'A float divided by zero is infinity, ' +
              'and every number computed from it afterwards would be infinity too — so ' +
              'the sketch stops here instead.'
              : 'Whatever this divisor was counted from came out zero.'));
          }
          return f ? num(a.v / b.v, true) : num(toInt(Math.trunc(a.v / b.v)), false);
        case '%':
          if (toInt(b.v) === 0) fail(line, 'the remainder after dividing by zero has no value.');
          return num(toInt(a.v) % toInt(b.v), false);
        case '<': return num(a.v < b.v ? 1 : 0, false);
        case '<=': return num(a.v <= b.v ? 1 : 0, false);
        case '>': return num(a.v > b.v ? 1 : 0, false);
        case '>=': return num(a.v >= b.v ? 1 : 0, false);
        case '==': return num(a.v === b.v ? 1 : 0, false);
        case '!=': return num(a.v !== b.v ? 1 : 0, false);
        case '&': return num(toInt(a.v) & toInt(b.v), false);
        case '|': return num(toInt(a.v) | toInt(b.v), false);
        case '^': return num(toInt(a.v) ^ toInt(b.v), false);
        case '<<': return num(toInt(a.v) << toInt(b.v), false);
        case '>>': return num(toInt(a.v) >> toInt(b.v), false);
      }
      fail(line, 'there is no "' + op + '" operator here.');
    }

    function* call(node, sc) {
      yield* tick(node.line);
      const args = [];
      for (let i = 0; i < node.args.length; i++) args.push(yield* evalNode(node.args[i], sc));

      const b = BUILTIN[node.name];
      if (b) {
        if (b.n >= 0 && args.length !== b.n) {
          fail(node.line, node.name + ' takes ' + b.n + ' argument' + (b.n === 1 ? '' : 's') +
            ', not ' + args.length + '.');
        }
        if (b.block) return yield* b.block(args, node.line);
        return b.f(args, node.line);
      }

      const fn = fns[node.name];
      if (!fn) {
        fail(node.line, 'there is no function called ' + node.name + '. This subset has ' +
          Object.keys(BUILTIN).length + ' built-in functions, and whatever else you have ' +
          'written above.');
      }
      if (args.length !== fn.params.length) {
        fail(node.line, fn.name + ' takes ' + fn.params.length + ' argument' +
          (fn.params.length === 1 ? '' : 's') + ', not ' + args.length + '.');
      }
      return yield* invoke(fn, args, node.line);
    }

    function* invoke(fn, args, line) {
      yield* tick(fn.line);
      if (++M.depth > MAX_DEPTH) {
        M.depth--;
        fail(line, fn.name + ' has called itself ' + MAX_DEPTH + ' deep. A recursion that ' +
          'goes this far here is nearly always one with no base case, or one whose base ' +
          'case is never reached.');
      }
      const sc = scope(globalScope);
      fn.params.forEach(function (p, i) { declare(sc, p.name, p.type, args[i], line); });
      const r = yield* run(fn.body, sc);
      M.depth--;
      if (r && r.sig === 'return') {
        if (fn.ret === 'void' && r.val !== undefined) {
          fail(line, fn.name + ' is declared void, so it cannot return a value.');
        }
        return r.val === undefined ? ZERO : cast(fn.ret === 'void' ? 'int' : fn.ret, r.val, line);
      }
      if (fn.ret !== 'void') {
        fail(line, fn.name + ' is declared ' + fn.ret + ' but reached its closing brace ' +
          'without returning anything.');
      }
      return ZERO;
    }

    /* A statement runs and gives back nothing, or a signal that has to travel outward:
       break, continue, or a return with its value. Signals rather than exceptions
       because an exception unwinds the generator stack, and unwinding is exactly what
       suspension must never do. */
    function* run(node, sc) {
      /* charged here, once, for every statement there is — see the invariant above; a
         kind that ticked only inside its own case is a kind that can be made free by
         being written empty */
      yield* tick(node.line);
      switch (node.k) {
        case 'block': {
          const inner = scope(sc);
          for (let i = 0; i < node.body.length; i++) {
            const sig = yield* run(node.body[i], inner);
            if (sig) return sig;
          }
          return null;
        }
        case 'decl': {
          for (let i = 0; i < node.names.length; i++) {
            const d = node.names[i];
            const val = d.init ? yield* evalNode(d.init, sc) : ZERO;
            declare(sc, d.name, node.type, val, node.line);
          }
          return null;
        }
        case 'expr':
          yield* evalNode(node.a, sc);
          return null;
        case 'if':
          if (truthy(yield* evalNode(node.c, sc))) return yield* run(node.a, sc);
          return node.b ? yield* run(node.b, sc) : null;
        case 'while':
          for (;;) {
            yield* tick(node.line);
            if (!truthy(yield* evalNode(node.c, sc))) return null;
            const sig = yield* run(node.body, sc);
            if (sig === BREAK) return null;
            if (sig && sig !== CONT) return sig;
          }
        case 'for': {
          const outer = scope(sc);
          if (node.init) yield* run(node.init, outer);
          for (;;) {
            yield* tick(node.line);
            if (node.c && !truthy(yield* evalNode(node.c, outer))) return null;
            const sig = yield* run(node.body, outer);
            if (sig === BREAK) return null;
            if (sig && sig !== CONT) return sig;
            if (node.post) yield* evalNode(node.post, outer);
          }
        }
        case 'ret': {
          const val = node.a ? yield* evalNode(node.a, sc) : undefined;
          return { sig: 'return', val: val };
        }
        case 'break': return BREAK;
        case 'cont': return CONT;
      }
      fail(node.line, 'this statement is not something the machine understands.');
    }

    /* ---- the one generator the whole sketch lives inside ----
       setup() once, then loop() forever. Nothing about "forever" is special: it is a
       while loop that yields, which is why it costs nothing to leave running. */
    function* main() {
      for (let i = 0; i < program.globals.length; i++) {
        yield* run(program.globals[i], globalScope);
      }
      if (fns.setup) yield* invoke(fns.setup, [], fns.setup.line);
      M.inSetup = false;
      if (!fns.loop) {
        /* A sketch with no loop() is legal C and a finished program; it is worth
           saying so rather than leaving the panel looking as though something hung. */
        M.done = true;
        return;
      }
      for (;;) {
        yield* invoke(fns.loop, [], fns.loop.line);
        M.loops++;
        M.io = true;
        yield;
      }
    }

    const gen = main();

    /* ---- the driver ----
     *
     * Called once per solver time step, with the clock and how many instructions this
     * step is worth. Everything above suspends into here and is resumed from here. */
    function advance(t, ops) {
      M.t = t;
      M.io = false;
      M.left = ops;
      M.suspended = false;
      if (M.fault || M.done) return;
      while (M.left > 0 && M.t >= M.wake) {
        let r;
        try {
          r = gen.next();
        } catch (e) {
          M.fault = e && e.mcuFault ? e : Fault(M.line, String((e && e.message) || e));
          return;
        }
        if (r.done) { M.done = true; return; }
      }
      M.suspended = true;
      /* The watchdog. See STALL_STEPS: out of instructions is normal, out of
         instructions while doing nothing the circuit could ever notice is not. */
      if (M.t < M.wake || M.io) {
        M.stall = 0;
      } else if (++M.stall >= STALL_STEPS) {
        M.fault = Fault(M.line, 'stuck here: ' + STALL_STEPS + ' time steps and ' +
          'roughly ' + (STALL_STEPS * ops) + ' instructions have gone by without this ' +
          'sketch reading a pin, writing a pin, printing, calling delay, or finishing ' +
          'an iteration of loop(). A loop that touches none of those cannot change the ' +
          'circuit or notice it changing, so no amount of further time will get it out.');
      }
    }

    return {
      advance: advance,
      /* Everything the panel reports, read rather than pushed, so the machine has no
         opinion about how it is displayed. */
      state: function () {
        return { fault: M.fault, line: M.line, ops: M.ops, loops: M.loops,
                 inSetup: M.inSetup, done: !!M.done, sleeping: M.t < M.wake,
                 dropped: M.dropped };
      },
      console: function () { return M.console.map(function (l) { return l.text; }); },
      hasLoop: !!fns.loop,
      hasSetup: !!fns.setup,
    };
  }

  /* ---------------------------------------------------------------- outside */

  /* Source to a program, or to the one fault that stopped it becoming one. Compiling
     is separate from running because a sketch with a typo in it should be reported the
     moment it is typed, and not on time step four hundred. */
  function compile(source) {
    const defines = {};
    try {
      const program = parse(lex(String(source || ''), defines));
      program.defines = defines;
      if (!program.fns.loop && !program.fns.setup) {
        return { error: Fault(1, 'a sketch needs a setup(), a loop(), or both. ' +
          'void setup() runs once when the circuit powers up; void loop() runs over and ' +
          'over for as long as it has power.') };
      }
      ['setup', 'loop'].forEach(function (nm) {
        const fn = program.fns[nm];
        if (fn && fn.params.length) {
          fail(fn.line, nm + '() takes no arguments — the machine is what calls it.');
        }
      });
      return { program: program };
    } catch (e) {
      return { error: e && e.mcuFault ? e : Fault(0, String((e && e.message) || e)) };
    }
  }

  return {
    compile: compile,
    machine: make,
    /* Quoted by the panel. The other numbers at the top of this file are quoted inside
       their own messages instead, so nothing outside has to be told about them. */
    OPS_PER_SECOND: OPS_PER_SECOND,
    /* How many instructions a step of this length is worth. Here rather than in the
       caller so the panel's quoted rate and the machine's actual rate are one number. */
    opsFor: function (h) {
      return Math.max(1, Math.min(Math.round(h * OPS_PER_SECOND), OPS_MAX_STEP));
    },
  };
})();
