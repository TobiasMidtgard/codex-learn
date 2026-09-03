const MCU = (function () {
const OPS_PER_SECOND = 1e6;
const OPS_MAX_STEP = 20000;
const MAX_DEPTH = 64;
const STALL_STEPS = 50;
const CONSOLE_MAX = 400;
const CONSOLE_MAX_CHARS = 20000;
function num(v, f) { return { v: v, f: !!f }; }
function str(s) { return { s: s }; }
const ZERO = num(0, false);
function toInt(v) { return v | 0; }
function isNum(x) { return x && x.s === undefined; }
function finite(v, line, what) {
if (typeof v === 'number' && v - v === 0) return v;
fail(line, what + ' is ' + (v !== v ? 'not a number' : v > 0 ? 'infinity' : 'minus infinity') +
'. Every number worked out from it afterwards would be as well — and stored into ' +
'an int it becomes 0, which looks like an answer. The sketch stops here instead.');
}
function Fault(line, message) {
return { mcuFault: true, line: line, message: message };
}
function fail(line, message) { throw Fault(line, message); }
function bare(o) { return Object.assign(Object.create(null), o || {}); }
const PUNCT = [
'<<=', '>>=', '&&', '||', '==', '!=', '<=', '>=', '<<', '>>', '++', '--',
'+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=',
'{', '}', '(', ')', '[', ']', ';', ',', '.', '+', '-', '*', '/', '%',
'<', '>', '=', '!', '&', '|', '^', '~', '?', ':',
];
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
if (c === "'") {
const esc = src[i + 1] === '\\';
const ch = esc ? bare({ n: '\n', t: '\t', '0': '\0', '\\': '\\', "'": "'" })[src[i + 2]] : src[i + 1];
if (esc && ch === undefined) {
fail(line, 'there is no escape "\\' + (src[i + 2] === undefined ? '' : src[i + 2]) +
'" in a character literal here. The ones there are are \\n, \\t, \\0, \\\\ and \\\'.');
}
const end = esc ? i + 3 : i + 2;
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
if (j === i + 2) fail(line, '"' + src.slice(i, j) + '" has no digits after it. ' +
'A hexadecimal number needs at least one, as in 0x1F.');
out.push({ t: 'num', v: num(parseInt(src.slice(i, j), 16) | 0, false), line: line });
i = j;
continue;
}
if (c === '0' && (src[i + 1] === 'b' || src[i + 1] === 'B')) {
j = i + 2;
while (j < n && /[01]/.test(src[j])) j++;
if (j === i + 2) fail(line, '"' + src.slice(i, j) + '" has no digits after it. ' +
'A binary number needs at least one 0 or 1, as in 0b1011.');
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
if (/[fF]/.test(src[j] || '')) { isF = true; j++; }
else if (/[uUlL]/.test(src[j] || '')) { while (/[uUlL]/.test(src[j] || '')) j++; }
out.push({ t: 'num', v: num(isF ? finite(parseFloat(text), line, 'the number ' + text)
: (parseInt(text, 10) | 0), isF), line: line });
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
function typeHere() {
let j = k;
if (tokens[j].t === 'id' && tokens[j].s === 'const') j++;
if (tokens[j].t === 'id' && tokens[j].s === 'unsigned') j++;
const t = tokens[j];
if (t.t !== 'id' || !TYPES[t.s]) return null;
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
const fns = bare(null);
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
if (eat(';')) continue;
if (fns[name]) fail(nameTok.line, 'there is already a function called ' + name + '.');
fns[name] = { name: name, ret: retType, params: params, body: block(), line: nameTok.line };
continue;
}
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
const CONSTANTS = bare({
HIGH: num(1, false), LOW: num(0, false),
INPUT: num(0, false), OUTPUT: num(1, false), INPUT_PULLUP: num(2, false),
true: num(1, false), false: num(0, false),
PI: num(Math.PI, true), TWO_PI: num(2 * Math.PI, true), HALF_PI: num(Math.PI / 2, true),
A0: num(14, false), A1: num(15, false), A2: num(16, false), A3: num(17, false),
});
function truthy(x) { return isNum(x) && x.v !== 0; }
function show(x) {
if (!isNum(x)) return x.s;
return x.f ? x.v.toFixed(2) : String(x.v | 0);
}
function make(program, board, opts) {
opts = opts || {};
const fns = program.fns;
const M = {
t: 0,
line: 0,
fault: null,
console: [],
dropped: 0,
chars: 0,
cut: 0,
wake: 0,
left: 0,
ops: 0,
depth: 0,
loops: 0,
inSetup: true,
io: false,
stall: 0,
suspended: false,
};
function scope(parent) { return { vars: bare(null), up: parent }; }
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
function emit(text) {
M.io = true;
if (M.chars >= CONSOLE_MAX_CHARS) { M.cut += text.length; return; }
if (M.console.length >= CONSOLE_MAX) { M.dropped++; return; }
M.chars += text.length;
const last = M.console.length - 1;
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
function pin(x, line) {
if (!isNum(x)) fail(line, 'a pin number has to be a number.');
const p = toInt(Math.trunc(x.v));
if (board.pinName(p) === null) {
fail(line, 'there is no pin ' + p + ' on this part. It has ' + board.pinList() + '.');
}
return p;
}
const BUILTIN = bare({
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
});
BUILTIN['Serial.print'] = BUILTIN.print;
BUILTIN['Serial.println'] = BUILTIN.println;
BUILTIN['Serial.begin'] = { n: -1, f: function () { return ZERO; } };
const TAKES_TEXT = bare({
print: 1, println: 1, 'Serial.print': 1, 'Serial.println': 1, 'Serial.begin': 1,
});
function* sleep(secs) {
M.io = true;
M.wake = M.t + secs;
while (M.t < M.wake) yield;
}
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
case '+': return f ? num(finite(a.v + b.v, line, 'this sum'), true) : num(toInt(a.v + b.v), false);
case '-': return f ? num(finite(a.v - b.v, line, 'this difference'), true) : num(toInt(a.v - b.v), false);
case '*': return f ? num(finite(a.v * b.v, line, 'this product'), true) : num(toInt(Math.trunc(a.v * b.v)), false);
case '/':
if (b.v === 0) {
fail(line, 'division by zero. ' + (f ? 'A float divided by zero is infinity, ' +
'and every number computed from it afterwards would be infinity too — so ' +
'the sketch stops here instead.'
: 'Whatever this divisor was counted from came out zero.'));
}
return f ? num(finite(a.v / b.v, line, 'this quotient'), true) : num(toInt(Math.trunc(a.v / b.v)), false);
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
if (!TAKES_TEXT[node.name]) {
for (let i = 0; i < args.length; i++) {
if (!isNum(args[i])) {
fail(node.line, node.name + ' works on numbers, and argument ' +
(i + 1) + ' is a piece of text. Strings here are only for printing — ' +
'print, println and their Serial spellings are the only things that take one.');
}
}
}
if (b.block) return yield* b.block(args, node.line);
const r = b.f(args, node.line);
if (isNum(r)) finite(r.v, node.line, 'what ' + node.name + ' worked out');
return r;
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
function* run(node, sc) {
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
function* main() {
for (let i = 0; i < program.globals.length; i++) {
yield* run(program.globals[i], globalScope);
}
if (fns.setup) yield* invoke(fns.setup, [], fns.setup.line);
M.inSetup = false;
if (!fns.loop) {
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
state: function () {
return { fault: M.fault, line: M.line, ops: M.ops, loops: M.loops,
inSetup: M.inSetup, done: !!M.done, sleeping: M.t < M.wake,
dropped: M.dropped, cut: M.cut };
},
console: function () { return M.console.map(function (l) { return l.text; }); },
hasLoop: !!fns.loop,
hasSetup: !!fns.setup,
};
}
function compile(source) {
const defines = bare(null);
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
OPS_PER_SECOND: OPS_PER_SECOND,
opsFor: function (h) {
return Math.max(1, Math.min(Math.round(h * OPS_PER_SECOND), OPS_MAX_STEP));
},
};
})();

const Lin = (function () {
function cadd(a, b) { return [a[0] + b[0], a[1] + b[1]]; }
function csub(a, b) { return [a[0] - b[0], a[1] - b[1]]; }
function cmul(a, b) { return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]]; }
function cdiv(a, b) {
const d = b[0] * b[0] + b[1] * b[1];
if (d === 0) return [0, 0];
return [(a[0] * b[0] + a[1] * b[1]) / d, (a[1] * b[0] - a[0] * b[1]) / d];
}
function cabs(a) { return Math.hypot(a[0], a[1]); }
function solve(A, b) {
const n = b.length;
const M = A.map(function (row, i) { return row.slice().concat([b[i]]); });
for (let col = 0; col < n; col++) {
let piv = col, best = cabs(M[col][col]);
for (let r = col + 1; r < n; r++) {
const m = cabs(M[r][col]);
if (m > best) { best = m; piv = r; }
}
if (best < 1e-14) return null;
if (piv !== col) { const t = M[col]; M[col] = M[piv]; M[piv] = t; }
const d = M[col][col];
for (let c = col; c <= n; c++) M[col][c] = cdiv(M[col][c], d);
for (let r = 0; r < n; r++) {
if (r === col) continue;
const f = M[r][col];
if (cabs(f) === 0) continue;
for (let c = col; c <= n; c++) M[r][c] = csub(M[r][c], cmul(f, M[col][c]));
}
}
return M.map(function (row) { return row[n]; });
}
function zeros(n) {
const A = [];
for (let i = 0; i < n; i++) {
const row = [];
for (let j = 0; j < n; j++) row.push([0, 0]);
A.push(row);
}
return A;
}
return { solve: solve, zeros: zeros, cadd: cadd, csub: csub, cmul: cmul, cdiv: cdiv, cabs: cabs };
})();
const MCU_SKETCH = [
'// pinMode says which way a pin faces. digitalWrite then drives it',
'// to Vcc or to 0 V through the pin resistance — see the panel.',
'void setup() {',
'  pinMode(3, OUTPUT);',
'}',
'',
'void loop() {',
'  digitalWrite(3, HIGH);',
'  delay(200);',
'  digitalWrite(3, LOW);',
'  delay(200);',
'}',
'',
].join('\n');
let MCU_PANEL_SEQ = 0;
function bareTable(o) { return Object.assign(Object.create(null), o); }
const PART_KINDS = bareTable({
R: { name: 'Resistor', unit: 'Ω', def: 1000, pins: 2, sym: 'R' },
C: { name: 'Capacitor', unit: 'F', def: 1e-6, pins: 2, sym: 'C' },
L: { name: 'Inductor', unit: 'H', def: 1e-3, pins: 2, sym: 'L' },
V: { name: 'Voltage source', unit: 'V', def: 5, pins: 2, sym: 'V' },
I: { name: 'Current source', unit: 'A', def: 0.001, pins: 2, sym: 'I' },
GND: { name: 'Ground', unit: '', def: 0, pins: 1, sym: '⏚' },
OUT: { name: 'Probe', unit: '', def: 0, pins: 1, sym: '◦' },
SW: { name: 'Switch', unit: 'Ω', def: 0, pins: 2, sym: 'SW', state: { closed: false } },
LDR: { name: 'Light sensor', unit: 'Ω', def: 10000, pins: 2, sym: 'LDR', state: { gamma: 0.7 },
senses: 'lux' },
NTC: { name: 'Thermistor', unit: 'Ω', def: 10000, pins: 2, sym: 'NTC', state: { beta: 3950 },
senses: 'tempC' },
POT: { name: 'Potentiometer', unit: 'Ω', def: 10000, pins: 3, sym: 'POT', state: { wiper: 0.5 } },
D: { name: 'Diode', unit: 'A', def: 1e-14, pins: 2, sym: 'D', state: { n: 1 } },
LED: { name: 'LED', unit: 'A', def: 1e-18, pins: 2, sym: 'LED', state: { n: 2, inom: 0.02 } },
NPN: { name: 'NPN transistor', unit: 'A', def: 1e-14, pins: 3, sym: 'NPN',
state: { bf: 100, br: 1 } },
PNP: { name: 'PNP transistor', unit: 'A', def: 1e-14, pins: 3, sym: 'PNP',
state: { bf: 100, br: 1 } },
NMOS: { name: 'N-channel MOSFET', unit: 'A/V²', def: 2e-3, pins: 3, sym: 'NMOS',
state: { vth: 1, lambda: 0.02 } },
PMOS: { name: 'P-channel MOSFET', unit: 'A/V²', def: 1e-3, pins: 3, sym: 'PMOS',
state: { vth: 1, lambda: 0.02 } },
OPAMP: { name: 'Op-amp', unit: '', def: 1e5, pins: 3, sym: 'OPAMP',
state: { vpos: 15, vneg: -15 } },
LAMP: { name: 'Lamp', unit: 'Ω', def: 220, pins: 2, sym: 'LAMP', state: { pnom: 0.25 } },
METER: { name: 'Ammeter', unit: 'Ω', def: 0.1, pins: 2, sym: 'METER' },
BAR: { name: 'Bar display', unit: 'V', def: 5, pins: 1, sym: 'BAR' },
IC: { name: 'Block', unit: '', def: 0, pins: 0, sym: 'IC' },
BB: { name: 'Breadboard', unit: '', def: 30, pins: 0, sym: 'BB' },
MCU: { name: 'Microcontroller', unit: '', def: 0, pins: 0, sym: 'MCU',
state: { code: MCU_SKETCH } },
});
const ENV_DEFAULT = { lux: 200, tempC: 25 };
const SW_ON = 0.05, SW_OFF = 1e8;
const Sensors = {
ldr: function (r10, gamma, lux) {
const E = Math.min(Math.max(lux, 0.01), 1e5);
const g = Math.min(Math.max(gamma, 0.05), 3);
return Math.min(Math.max(Math.max(r10, 1) * Math.pow(10 / E, g), 1), 1e9);
},
ntc: function (r25, beta, tempC) {
const T = Math.max(tempC + 273.15, 1);
const B = Math.min(Math.max(beta, 1), 20000);
return Math.min(Math.max(Math.max(r25, 1) * Math.exp(B * (1 / T - 1 / 298.15)), 0.01), 1e12);
},
};
const MCU_VCC = 5;
const MCU_ROUT = 25;
const MCU_RPULL = 40e3;
const MCU_RSUP = 0.5;
const MCU_RIN = 1e8;
const MCU_VIH = 0.6 * MCU_VCC, MCU_VIL = 0.4 * MCU_VCC;
const MCU_ADC_BITS = 10, MCU_ADC_MAX = 1023;
const MCU_W = 4, MCU_H = 7;
const MCU_PINS = [
{ n: 0, name: '0', side: 0, row: 1, adc: false },
{ n: 1, name: '1', side: 0, row: 2, adc: false },
{ n: 2, name: '2', side: 0, row: 3, adc: false },
{ n: 3, name: '3', side: 0, row: 4, adc: false },
{ n: 4, name: '4', side: 0, row: 5, adc: false },
{ n: 5, name: '5', side: 0, row: 6, adc: false },
{ n: 14, name: 'A0', side: 1, row: 1, adc: true },
{ n: 15, name: 'A1', side: 1, row: 2, adc: true },
{ n: 16, name: 'A2', side: 1, row: 3, adc: true },
{ n: 17, name: 'A3', side: 1, row: 4, adc: true },
{ n: null, name: 'Vcc', side: 1, row: 5, power: 'vcc' },
{ n: null, name: 'GND', side: 1, row: 6, power: 'gnd' },
];
function mcuReset(id) {
return { id: id, vcc: MCU_VCC,
pins: MCU_PINS.map(function (d) {
return { n: d.n, name: d.name, power: d.power || null, adc: !!d.adc,
node: 0, mode: 'in', drive: 0, last: 0 };
}) };
}
function mcuNorton(pin) {
if (pin.power === 'gnd') return null;
if (pin.power === 'vcc') return { g: 1 / MCU_RSUP, i: MCU_VCC / MCU_RSUP };
if (pin.mode === 'out') return { g: 1 / MCU_ROUT, i: pin.drive * MCU_VCC / MCU_ROUT };
if (pin.mode === 'pullup') {
return { g: 1 / MCU_RIN + 1 / MCU_RPULL, i: MCU_VCC / MCU_RPULL };
}
return { g: 1 / MCU_RIN, i: 0 };
}
function mcuLevel(pin, volts) {
if (volts >= MCU_VIH) pin.last = 1;
else if (volts <= MCU_VIL) pin.last = 0;
return pin.last;
}
function ohmsOf(p, env) {
const e = env || ENV_DEFAULT;
if (p.kind === 'SW') return p.closed ? SW_ON : SW_OFF;
if (p.kind === 'LDR') return Sensors.ldr(p.value, p.gamma === undefined ? 0.7 : p.gamma, e.lux);
if (p.kind === 'NTC') return Sensors.ntc(p.value, p.beta === undefined ? 3950 : p.beta, e.tempC);
if (p.kind === 'LAMP') return Math.max(p.value, 1e-3);
if (p.kind === 'METER') return Math.max(p.value, 1e-6);
return null;
}
function potSplit(p) {
const total = Math.max(p.value, 1e-3);
const w = Math.min(Math.max(p.wiper === undefined ? 0.5 : p.wiper, 0), 1);
return [Math.max(total * w, 1e-3), Math.max(total * (1 - w), 1e-3)];
}
function param(p, key, lo, hi) {
const k = PART_KINDS[p.kind];
const d = k && k.state ? k.state[key] : 0;
const v = Number(p[key] === undefined ? d : p[key]);
return Math.min(Math.max(isFinite(v) ? v : d, lo), hi);
}
const T_NOM = 300;
const VT = 1.380649e-23 * T_NOM / 1.602176634e-19;
const EXP_CAP = 40;
function pnExp(vj, nvt, is) {
const top = EXP_CAP * nvt;
if (vj <= top) {
const ex = Math.exp(vj / nvt);
return [is * (ex - 1), is * ex / nvt];
}
const ex = Math.exp(EXP_CAP);
const g = is * ex / nvt;
return [is * (ex - 1) + g * (vj - top), g];
}
function vcritOf(is, nvt) {
return nvt * Math.log(nvt / (Math.SQRT2 * Math.max(is, 1e-30)));
}
function pnjlim(vnew, vold, nvt, vcrit) {
if (vnew > vcrit && Math.abs(vnew - vold) > 2 * nvt) {
if (vold > 0) {
const arg = 1 + (vnew - vold) / nvt;
return arg > 0 ? vold + nvt * Math.log(arg) : vcrit;
}
return nvt * Math.log(vnew / nvt);
}
return vnew;
}
function junctionV(st, key, asked, nvt, vcrit) {
const had = st[key];
const v = had === undefined ? vcrit : pnjlim(asked, had, nvt, vcrit);
if (v !== asked) st.lim = true;
st[key] = v;
return v;
}
const FET_STEP = 2;
function fetlim(vnew, vold) {
if (vnew > vold + FET_STEP) return vold + FET_STEP;
if (vnew < vold - FET_STEP) return vold - FET_STEP;
return vnew;
}
const OP_ROUT = 75;
const Devices = (function () {
function diode(d, v, st) {
const nvt = d.n * VT;
const asked = v[0] - v[1];
const vd = st.raw ? asked
: junctionV(st, 'vd', asked, nvt, vcritOf(d.is, nvt));
const r = pnExp(vd, nvt, d.is);
return { i: [r[0], -r[0]], j: [[r[1], -r[1]], [-r[1], r[1]]],
v: [v[1] + vd, v[1]] };
}
function bjt(d, v, st) {
const s = d.sign, nvt = VT, vcrit = vcritOf(d.is, nvt);
const abe = s * (v[2] - v[1]), abc = s * (v[2] - v[0]);
const vbe = st.raw ? abe : junctionV(st, 'vbe', abe, nvt, vcrit);
const vbc = st.raw ? abc : junctionV(st, 'vbc', abc, nvt, vcrit);
const F = pnExp(vbe, nvt, d.is), R = pnExp(vbc, nvt, d.is);
const rf = 1 / d.bf, rr = 1 / d.br;
const ic = F[0] - R[0] * (1 + rr);
const ib = F[0] * rf + R[0] * rr;
const gr = R[1] * (1 + rr);
const jc = [gr, -F[1], F[1] - gr];
const jb = [-R[1] * rr, -F[1] * rf, F[1] * rf + R[1] * rr];
const je = [-jc[0] - jb[0], -jc[1] - jb[1], -jc[2] - jb[2]];
return { i: [s * ic, -s * (ic + ib), s * ib], j: [jc, je, jb],
v: [v[1] + s * (vbe - vbc), v[1], v[1] + s * vbe] };
}
function square(vgs, vds, d) {
const vov = vgs - d.vth;
if (vov <= 0) return [0, 0, 0];
const e = 1 + d.lambda * vds;
if (vds < vov) {
const q = vov * vds - 0.5 * vds * vds;
return [d.k * q * e, d.k * vds * e,
d.k * (vov - vds) * e + d.k * q * d.lambda];
}
return [0.5 * d.k * vov * vov * e,
d.k * vov * e,
0.5 * d.k * vov * vov * d.lambda];
}
function mos(d, v, st) {
const s = d.sign;
let vgs = s * (v[2] - v[1]);
let vds = s * (v[0] - v[1]);
if (!st.raw) {
const ags = vgs, ads = vds;
vgs = fetlim(vgs, st.vgs === undefined ? 0 : st.vgs);
vds = fetlim(vds, st.vds === undefined ? 0 : st.vds);
if (vgs !== ags || vds !== ads) st.lim = true;
st.vgs = vgs; st.vds = vds;
}
let id, gm, gds;
if (vds >= 0) {
const m = square(vgs, vds, d);
id = m[0]; gm = m[1]; gds = m[2];
} else {
const m = square(vgs - vds, -vds, d);
id = -m[0]; gm = -m[1]; gds = m[1] + m[2];
}
const row = [gds, -(gm + gds), gm];
return { i: [s * id, -s * id, 0],
j: [row, [-row[0], -row[1], -row[2]], [0, 0, 0]],
v: [v[1] + s * vds, v[1], v[1] + s * vgs] };
}
function opamp(d, v, st) {
const mid = (d.vpos + d.vneg) / 2;
const sw = Math.max((d.vpos - d.vneg) / 2, 1e-3);
const lin = sw / d.gain;
const th = Math.tanh((v[0] - v[2]) / lin);
const gout = 1 / OP_ROUT;
const a = d.gain * (1 - th * th) * gout;
return { i: [0, gout * (v[1] - (mid + sw * th)), 0],
j: [[0, 0, 0], [-a, gout, a], [0, 0, 0]], v: v };
}
function junction(p) {
return { is: Math.max(p.value, 1e-30), n: param(p, 'n', 0.5, 4) };
}
function bipolar(p, s) {
return { is: Math.max(p.value, 1e-30), sign: s,
bf: param(p, 'bf', 1, 5000), br: param(p, 'br', 0.01, 100) };
}
function fet(p, s) {
return { k: Math.max(p.value, 1e-12), sign: s,
vth: param(p, 'vth', 0.05, 20), lambda: param(p, 'lambda', 0, 1) };
}
const KIND = {
D: { iv: diode, of: junction },
LED: { iv: diode, of: junction },
NPN: { iv: bjt, of: function (p) { return bipolar(p, 1); } },
PNP: { iv: bjt, of: function (p) { return bipolar(p, -1); } },
NMOS: { iv: mos, of: function (p) { return fet(p, 1); } },
PMOS: { iv: mos, of: function (p) { return fet(p, -1); } },
OPAMP: { iv: opamp, of: function (p) {
const hi = param(p, 'vpos', -100, 100), lo = param(p, 'vneg', -100, 100);
return { gain: Math.min(Math.max(p.value, 10), 1e9),
vpos: Math.max(hi, lo + 1e-3), vneg: Math.min(lo, hi - 1e-3) };
} },
};
function build(p) {
const k = KIND[p.kind];
if (!k) return null;
const d = k.of(p);
d.iv = k.iv;
d.kind = p.kind;
d.id = p.id;
return d;
}
return {
is: function (kind) { return !!KIND[kind]; },
build: build,
dropAt: function (is, n, amps) { return n * VT * Math.log(amps / is + 1); },
VT: VT, T_NOM: T_NOM, OP_ROUT: OP_ROUT,
};
})();
function fmtEng(v, unit) {
if (v === 0) return '0 ' + unit;
const a = Math.abs(v);
const P = [[1e9, 'G'], [1e6, 'M'], [1e3, 'k'], [1, ''], [1e-3, 'm'],
[1e-6, 'µ'], [1e-9, 'n'], [1e-12, 'p']];
for (const [mul, pre] of P) {
if (a >= mul * 0.999) {
const s = (v / mul);
let txt = Math.abs(s) >= 100 ? s.toFixed(0)
: Math.abs(s) >= 10 ? s.toFixed(1) : s.toFixed(2);
if (txt.indexOf('.') >= 0) txt = txt.replace(/0+$/, '').replace(/\.$/, '');
return txt + ' ' + pre + unit;
}
}
return v.toExponential(2) + ' ' + unit;
}
function parseEng(text, fallback) {
const m = /^\s*(-?[\d.]+(?:[eE][-+]?\d+)?)\s*([GMkmunpµ]?)/.exec(String(text));
if (!m) return fallback;
const mul = { G: 1e9, M: 1e6, k: 1e3, '': 1, m: 1e-3, u: 1e-6, 'µ': 1e-6, n: 1e-9, p: 1e-12 };
const v = parseFloat(m[1]) * (mul[m[2]] !== undefined ? mul[m[2]] : 1);
return isFinite(v) ? v : fallback;
}
const VALUE_FLOOR = bareTable({
R: 1e-6, LDR: 1, NTC: 1, POT: 1e-2, LAMP: 1e-3, METER: 1e-6,
C: 1e-15, L: 1e-12,
D: 1e-30, LED: 1e-30, NPN: 1e-30, PNP: 1e-30,
NMOS: 1e-12, PMOS: 1e-12, OPAMP: 1,
});
const VALUE_CEIL = bareTable({
R: 1e12, LDR: 1e9, NTC: 1e12, POT: 1e12, LAMP: 1e12, METER: 1e12,
C: 1e6, L: 1e6,
D: 1e3, LED: 1e3, NPN: 1e3, PNP: 1e3,
NMOS: 1e6, PMOS: 1e6, OPAMP: 1e12,
V: 1e9, I: 1e9,
});
function clampValue(kind, v, fallback) {
if (!isFinite(v)) return fallback;
const floor = VALUE_FLOOR[kind];
if (floor !== undefined && v < floor) return floor;
const ceil = VALUE_CEIL[kind];
if (ceil !== undefined && Math.abs(v) > ceil) return v < 0 ? -ceil : ceil;
return v;
}
function turnsOf(p) { return ((((p.rot || 0) | 0) % 4) + 4) % 4; }
const CELL_LIMIT = 1e6;
const DRAW_DEPTH = 8;
function cellOf(v) {
if (typeof v !== 'number' && typeof v !== 'string') return null;
if (typeof v === 'string' && !v.trim()) return null;
const n = Math.round(Number(v));
return isFinite(n) && Math.abs(n) <= CELL_LIMIT ? n : null;
}
function pointOf(pt) {
if (!Array.isArray(pt)) return null;
const x = cellOf(pt[0]), y = cellOf(pt[1]);
return x === null || y === null ? null : [x, y];
}
const REF_PREFIX = { R: 'R', C: 'C', L: 'L', V: 'V', I: 'I', D: 'D', LED: 'LED',
SW: 'SW', LDR: 'LDR', NTC: 'NTC', POT: 'POT', LAMP: 'LA', METER: 'ME', BAR: 'BA',
NPN: 'Q', PNP: 'Q', NMOS: 'M', PMOS: 'M', OPAMP: 'U', IC: 'U', MCU: 'MCU',
GND: 'GND', OUT: 'TP', BB: 'BB' };
function refPrefix(kind) { return REF_PREFIX[kind] || kind; }
function stampRefs(parts) {
const used = {};
parts.forEach(function (p) {
if (typeof p.ref !== 'number') return;
const pre = refPrefix(p.kind);
(used[pre] = used[pre] || {})[p.ref] = 1;
});
parts.forEach(function (p) {
if (typeof p.ref === 'number') return;
const pre = refPrefix(p.kind);
const seen = used[pre] = used[pre] || {};
let n = 1;
while (seen[n]) n++;
seen[n] = 1;
p.ref = n;
});
}
function sanitiseDrawing(m, depth) {
const out = { parts: [], wires: [] };
if (!m || typeof m !== 'object' || Array.isArray(m)) return out;
Object.keys(m).forEach(function (k) {
if (k !== 'parts' && k !== 'wires' && k !== '__proto__') out[k] = m[k];
});
const d = (depth || 0) + 1;
(Array.isArray(m.parts) ? m.parts : []).forEach(function (p) {
if (!p || typeof p !== 'object' || Array.isArray(p)) return;
const x = cellOf(p.x), y = cellOf(p.y);
if (x === null || y === null) return;
if (!PART_KINDS[p.kind]) return;
const q = {};
Object.keys(p).forEach(function (k) { if (k !== '__proto__') q[k] = p[k]; });
q.x = x; q.y = y;
if (p.rot !== undefined) q.rot = turnsOf(p);
if (q.value !== undefined) {
const k = PART_KINDS[q.kind];
q.value = clampValue(q.kind, Number(q.value), k ? k.def : 0);
}
if (Array.isArray(p.ports)) {
q.ports = p.ports.map(function (port) {
if (!port || !Array.isArray(port.cells)) return port;
return Object.assign({}, port, { cells: port.cells.map(pointOf).filter(Boolean) });
});
}
if (p.inner) {
q.inner = d < DRAW_DEPTH ? sanitiseDrawing(p.inner, d) : { parts: [], wires: [] };
}
out.parts.push(q);
});
(Array.isArray(m.wires) ? m.wires : []).forEach(function (wr) {
if (!wr || typeof wr !== 'object') return;
const a = pointOf(wr.a), b = pointOf(wr.b);
if (a === null || b === null) return;
out.wires.push({ a: a, b: b });
});
stampRefs(out.parts);
return out;
}
function pinWords(p) {
return [['left', 'right', 'above'], ['top', 'bottom', 'to the right'],
['right', 'left', 'below'], ['bottom', 'top', 'to the left']][turnsOf(p)];
}
const BB_RAIL = 2;
const BB_STRIP = 5;
const BB_CHAN = BB_RAIL + BB_STRIP;
const BB_H = BB_RAIL * 2 + BB_STRIP * 2 + 1;
const BB_COLS = 30;
function bbCols(p) {
const n = Math.round(Number(p.value));
return Math.min(Math.max(isFinite(n) && n > 0 ? n : BB_COLS, 4), 200);
}
function bbStripAt(p, cx, cy) {
const c = cx - p.x, r = cy - p.y;
if (c < 0 || c >= bbCols(p) || r < 0 || r >= BB_H) return null;
if (r === BB_CHAN) return null;
if (r < BB_RAIL || r >= BB_H - BB_RAIL) return 'rail' + r;
return (r < BB_CHAN ? 'u' : 'l') + c;
}
function bodyOf(p) {
if (p.kind === 'IC') return [Math.max(1, p.w || 0), Math.max(1, p.h || 0)];
if (p.kind === 'BB') return [bbCols(p) - 1, BB_H - 1];
if (p.kind === 'MCU') return [MCU_W, MCU_H];
return null;
}
const Netlist = (function () {
function pinsOf(p) {
const k = PART_KINDS[p.kind];
if (p.kind === 'IC') {
const out = [];
(p.ports || []).forEach(function (port) {
(port.cells || []).forEach(function (c) { out.push([p.x + c[0], p.y + c[1]]); });
});
return out;
}
if (p.kind === 'BB') return [];
if (p.kind === 'MCU') {
return MCU_PINS.map(function (d) {
return [p.x + (d.side ? MCU_W : 0), p.y + d.row];
});
}
const n = k ? k.pins : 2;
if (n === 1) return [[p.x, p.y]];
const r = turnsOf(p);
const dx = [1, 0, -1, 0][r], dy = [0, 1, 0, -1][r];
const span = [[p.x - dx, p.y - dy], [p.x + dx, p.y + dy]];
if (n < 3) return span;
span.push([p.x + dy, p.y - dx]);
return span;
}
function plusFirst(p) {
const pins = pinsOf(p);
if (p.kind !== 'V' && p.kind !== 'I') return pins;
return (turnsOf(p) % 2) ? pins : [pins[1], pins[0]];
}
function key(pt, at) { return (at || '') + pt[0] + ',' + pt[1]; }
function joiner() {
const parent = {};
function find(a) {
if (parent[a] === undefined) { parent[a] = a; return a; }
while (parent[a] !== a) { parent[a] = parent[parent[a]]; a = parent[a]; }
return a;
}
function union(a, b) {
const ra = find(a), rb = find(b);
if (ra !== rb) parent[ra] = rb;
}
function run(w, at) {
const dx = Math.sign(w.b[0] - w.a[0]), dy = Math.sign(w.b[1] - w.a[1]);
const n = Math.max(Math.abs(w.b[0] - w.a[0]), Math.abs(w.b[1] - w.a[1]));
let cur = [w.a[0], w.a[1]];
find(key(cur, at));
for (let i = 0; i < n; i++) {
const nxt = [cur[0] + dx, cur[1] + dy];
union(key(cur, at), key(nxt, at));
cur = nxt;
}
}
return { parent: parent, find: find, union: union, run: run };
}
function bindBoard(p, uf, at) {
const cols = bbCols(p);
const first = {};
for (let c = 0; c < cols; c++) {
for (let r = 0; r < BB_H; r++) {
const s = bbStripAt(p, p.x + c, p.y + r);
if (s === null) continue;
const k = key([p.x + c, p.y + r], at);
if (uf.parent[k] === undefined) continue;
if (first[s] === undefined) first[s] = k; else uf.union(first[s], k);
}
}
}
const MAX_DEPTH = 8;
function flatten(m, out, at, depth) {
(m.parts || []).forEach(function (p) {
out.parts.push({ p: p, at: at });
if (p.kind !== 'IC') return;
const inside = at + p.id + '|';
(p.ports || []).forEach(function (port) {
(port.cells || []).forEach(function (c) {
out.joins.push([key([p.x + c[0], p.y + c[1]], at), key(c, inside)]);
});
});
if (depth + 1 > MAX_DEPTH) { out.tooDeep = MAX_DEPTH; return; }
flatten(p.inner || { parts: [], wires: [] }, out, inside, depth + 1);
});
(m.wires || []).forEach(function (w) { out.wires.push({ w: w, at: at }); });
}
function build(model, env) {
const world = Object.assign({}, ENV_DEFAULT, env || {});
const flat = { parts: [], wires: [], joins: [], tooDeep: 0 };
flatten(model || { parts: [], wires: [] }, flat, '', 0);
const uf = joiner();
const parent = uf.parent, find = uf.find, union = uf.union;
flat.parts.forEach(function (e) {
if (e.p.kind === 'BAR') return;
pinsOf(e.p).forEach(function (pt) { find(key(pt, e.at)); });
});
flat.wires.forEach(function (e) { uf.run(e.w, e.at); });
flat.joins.forEach(function (j) { find(j[0]); find(j[1]); union(j[0], j[1]); });
flat.parts.forEach(function (e) {
if (e.p.kind === 'BB') bindBoard(e.p, uf, e.at);
});
let gndRoot = null;
flat.parts.forEach(function (e) {
if (e.p.kind !== 'GND') return;
const r = find(key(pinsOf(e.p)[0], e.at));
if (gndRoot === null) gndRoot = r; else union(r, gndRoot);
});
if (gndRoot !== null) gndRoot = find(gndRoot);
const nodeOf = {};
let next = 1;
Object.keys(parent).forEach(function (k) {
const r = find(k);
if (nodeOf[r] === undefined) nodeOf[r] = (r === gndRoot) ? 0 : next++;
});
const probes = flat.parts
.filter(function (e) { return e.p.kind === 'OUT'; })
.map(function (e) { return nodeOf[find(key(pinsOf(e.p)[0], e.at))]; });
const placed = [];
const parts = [];
const readouts = [];
const mcus = {};
flat.parts.forEach(function (e) {
const p = e.p;
const pid = e.at + p.id;
if (p.kind === 'GND' || p.kind === 'OUT') return;
if (p.kind === 'IC') {
placed.push({ id: pid, kind: 'IC', value: 0 });
return;
}
if (p.kind === 'BB') {
placed.push({ id: pid, kind: 'BB', value: bbCols(p) });
return;
}
if (p.kind === 'MCU') {
const rec = mcuReset(pid);
const pins = pinsOf(p).map(function (pt) { return nodeOf[find(key(pt, e.at))]; });
rec.pins.forEach(function (pin, i) { pin.node = pins[i]; });
rec.gnd = pins[MCU_PINS.length - 1];
rec.code = typeof p.code === 'string' ? p.code : MCU_SKETCH;
mcus[pid] = rec;
placed.push({ id: pid, kind: 'MCU', value: 0 });
readouts.push({ id: pid, kind: 'MCU', mcu: rec });
parts.push({ id: pid, kind: 'MCU', mcu: rec });
return;
}
if (p.kind === 'BAR') {
const kk = key(pinsOf(p)[0], e.at);
placed.push({ id: pid, kind: p.kind, value: p.value });
readouts.push({ id: pid, kind: 'BAR', full: p.value,
node: parent[kk] === undefined ? null : nodeOf[find(kk)] });
return;
}
const pins = plusFirst(p).map(function (pt) { return nodeOf[find(key(pt, e.at))]; });
placed.push({ id: pid, kind: p.kind, value: p.value });
if (p.kind === 'POT') {
const rr = potSplit(p);
parts.push({ id: pid + '#a', kind: 'R', value: rr[0], n1: pins[0], n2: pins[2], of: pid });
parts.push({ id: pid + '#b', kind: 'R', value: rr[1], n1: pins[2], n2: pins[1], of: pid });
readouts.push({ id: pid, kind: 'POT', nodes: pins, ohms: rr[0] + rr[1], split: rr });
return;
}
if (Devices.is(p.kind)) {
const dev = Devices.build(p);
dev.id = pid;
dev.nodes = pins.slice(0, PART_KINDS[p.kind].pins);
parts.push(dev);
readouts.push({ id: pid, kind: p.kind, nodes: dev.nodes });
return;
}
const ohms = ohmsOf(p, world);
if (ohms !== null) {
parts.push({ id: pid, kind: 'R', value: ohms, n1: pins[0], n2: pins[1], of: pid, was: p.kind });
readouts.push({ id: pid, kind: p.kind, nodes: pins, ohms: ohms });
return;
}
parts.push({ id: pid, kind: p.kind, value: p.value, n1: pins[0], n2: pins[1], ac: p.ac });
});
const grounded = {};
parts.forEach(function (q) {
if (q.kind === 'MCU') return;
[q.n1, q.n2].concat(q.nodes || []).forEach(function (nd) {
if (nd !== undefined) grounded[nd] = 1;
});
});
const floatingMcus = Object.keys(mcus).filter(function (id) {
return mcus[id].gnd !== 0 && !grounded[mcus[id].gnd];
});
return { parts: parts, probes: probes, nodeCount: next, hasGround: gndRoot !== null,
placed: placed, readouts: readouts, env: world, tooDeep: flat.tooDeep,
mcus: mcus, floatingMcus: floatingMcus,
nodeAt: function (pt, at) {
const k = key(pt, at);
return parent[k] === undefined ? null : nodeOf[find(k)];
} };
}
return { build: build, pinsOf: pinsOf, plusFirst: plusFirst,
joiner: joiner, bindBoard: bindBoard, key: key, MAX_DEPTH: MAX_DEPTH };
})();
const MNA = (function () {
function currentCarriers(parts, mode) {
return parts.filter(function (p) {
return p.kind === 'V' || (p.kind === 'L' && mode !== 'ac');
});
}
function frame(net, mode) {
const carriers = currentCarriers(net.parts, mode);
const n = net.nodeCount - 1 + carriers.length;
return { carriers: carriers, n: n, idxOf: function (p) { return net.nodeCount - 1 + carriers.indexOf(p); } };
}
function stampG(A, i, j, g) {
if (i > 0) A[i - 1][i - 1] = Lin.cadd(A[i - 1][i - 1], g);
if (j > 0) A[j - 1][j - 1] = Lin.cadd(A[j - 1][j - 1], g);
if (i > 0 && j > 0) {
A[i - 1][j - 1] = Lin.csub(A[i - 1][j - 1], g);
A[j - 1][i - 1] = Lin.csub(A[j - 1][i - 1], g);
}
}
function stampCurrent(b, i, j, cur) {
if (i > 0) b[i - 1] = Lin.csub(b[i - 1], cur);
if (j > 0) b[j - 1] = Lin.cadd(b[j - 1], cur);
}
function stampMcu(A, b, rec) {
rec.pins.forEach(function (pin) {
const nrt = mcuNorton(pin);
if (!nrt) return;
stampG(A, pin.node, rec.gnd, [nrt.g, 0]);
if (nrt.i) stampCurrent(b, rec.gnd, pin.node, [nrt.i, 0]);
});
}
function problems(net) {
if (net.tooDeep) {
return 'Blocks are nested more than ' + net.tooDeep + ' deep, and everything below ' +
'that is not in the netlist — so there is no answer to give you that would be ' +
'about the circuit you drew. Ungroup a level and solve again.';
}
if (!net.hasGround) return 'No ground. Every circuit needs one, or the node voltages have nothing to be measured against.';
if (net.floatingMcus && net.floatingMcus.length) {
const who = net.floatingMcus.map(function (id) { return id.replace('p', 'part '); });
return 'The GND pin of ' + who.join(' and ') + ' is not connected to anything. ' +
'Every pin of a microcontroller is driven and read against its own GND pin, so ' +
'without that connection the whole part floats: its pin voltages have differences ' +
'but no values, which is a circuit with no unique answer. Wire GND to the same ' +
'ground the rest of the circuit uses.';
}
if (!net.parts.length) return 'Nothing to solve yet — place some components and wire them up.';
return null;
}
const UNDER_DC = 'The circuit is under-determined — usually a node connected to nothing, or two voltage sources in a loop.';
const UNDER_TRAN = 'The circuit is under-determined.';
const GMIN = 1e-12;
const NR_MAX = 100;
const RELTOL = 1e-6, VNTOL = 1e-9, ABSTOL = 1e-12;
function devicesOf(net) {
return net.parts.filter(function (p) { return !!p.iv; });
}
function freshState(devs) {
const s = {};
devs.forEach(function (d) { s[d.id] = {}; });
return s;
}
function rhs(n) {
const b = [];
for (let i = 0; i < n; i++) b.push([0, 0]);
return b;
}
function nodeVolts(nodes, x) {
return nodes.map(function (n) { return n > 0 && x ? x[n - 1][0] : 0; });
}
function stampTangent(A, nodes, J) {
for (let k = 0; k < nodes.length; k++) {
if (nodes[k] <= 0) continue;
for (let l = 0; l < nodes.length; l++) {
if (nodes[l] <= 0 || !J[k][l]) continue;
A[nodes[k] - 1][nodes[l] - 1] = Lin.cadd(A[nodes[k] - 1][nodes[l] - 1], [J[k][l], 0]);
}
}
}
function stampDevice(A, b, nodes, v, i, J) {
stampTangent(A, nodes, J);
for (let k = 0; k < nodes.length; k++) {
const nk = nodes[k];
if (nk <= 0) continue;
let ieq = i[k];
for (let l = 0; l < nodes.length; l++) ieq -= J[k][l] * v[l];
b[nk - 1] = Lin.csub(b[nk - 1], [ieq, 0]);
}
}
function settled(x, prev, nodeRows) {
for (let i = 0; i < x.length; i++) {
const a = x[i][0], p = prev[i][0];
const floor = i < nodeRows ? VNTOL : ABSTOL;
if (Math.abs(a - p) > RELTOL * Math.max(Math.abs(a), Math.abs(p)) + floor) return false;
}
return true;
}
function allFinite(x) {
for (let i = 0; i < x.length; i++) if (!isFinite(x[i][0]) || !isFinite(x[i][1])) return false;
return true;
}
function tangentsAt(devs, x) {
return devs.map(function (d) {
const vs = nodeVolts(d.nodes, x);
return { nodes: d.nodes, j: d.iv(d, vs, { raw: true }).j };
});
}
function stalled(msg, x, before, nodeRows) {
let worst = 0, at = 0;
if (x && before) {
for (let i = 0; i < nodeRows; i++) {
const d = Math.abs(x[i][0] - before[i][0]);
if (d > worst) { worst = d; at = i + 1; }
}
}
return 'The iteration did not settle: ' + NR_MAX + ' passes at ' + msg.where +
' and the node voltages were still moving' +
(at ? ' (node ' + at + ' by ' + fmtEng(worst, 'V') + ' on the last one)' : '') +
'. A non-linear circuit can fail to converge because it genuinely has more than one ' +
'operating point — a latch, or positive feedback round an op-amp — or because a ' +
'device is being driven far outside what its model was written for. Rather than ' +
'hand you the last guess as though it were an answer, this is the answer: it did ' +
'not converge.';
}
function blewUp(msg) {
return 'The iteration went to infinity at ' + msg.where + ' and came back as not a ' +
'number. Something is driving a device past anything the step limiting can hold — ' +
'a diode straight across a voltage source, with no resistance anywhere in the loop, ' +
'is the usual one.';
}
function overflowed(msg) {
return 'The arithmetic overflowed at ' + msg.where + ' and the answer came back as ' +
'not a number. Some value in this circuit is large enough that the numbers built ' +
'from it are past what double precision can hold — a capacitance or an inductance ' +
'is the usual one, because the companion model divides it by the time step and so ' +
'runs out of range long before the value itself does. Rather than hand you a plot ' +
'of nothing, this is the answer: there is none at that value.';
}
function iterate(net, f, devs, state, stamp, guess, msg) {
const nodeRows = net.nodeCount - 1;
if (!devs.length) {
const A = Lin.zeros(f.n), b = rhs(f.n);
stamp(A, b);
const x = Lin.solve(A, b);
if (!x) return { error: msg.under };
if (!allFinite(x)) return { error: overflowed(msg) };
return { x: x };
}
let prev = guess || null, before = null;
for (let pass = 1; pass <= NR_MAX; pass++) {
const A = Lin.zeros(f.n), b = rhs(f.n);
stamp(A, b);
for (let i = 0; i < nodeRows; i++) A[i][i] = Lin.cadd(A[i][i], [GMIN, 0]);
let held = false;
devs.forEach(function (d) {
const st = state[d.id];
st.lim = false;
const vs = nodeVolts(d.nodes, prev);
const r = d.iv(d, vs, st);
if (st.lim) held = true;
stampDevice(A, b, d.nodes, r.v, r.i, r.j);
});
const x = Lin.solve(A, b);
if (!x) return { error: msg.under };
if (!allFinite(x)) return { error: blewUp(msg) };
if (prev && !held && settled(x, prev, nodeRows)) {
return { x: x, passes: pass, tangents: tangentsAt(devs, x) };
}
before = prev;
prev = x;
}
return { error: stalled(msg, prev, before, nodeRows) };
}
function stampDC(net, f, A, b) {
net.parts.forEach(function (p) {
if (p.kind === 'R') stampG(A, p.n1, p.n2, [1 / Math.max(p.value, 1e-12), 0]);
else if (p.kind === 'I') stampCurrent(b, p.n1, p.n2, [p.value, 0]);
else if (p.kind === 'MCU') stampMcu(A, b, p.mcu);
else if (p.kind === 'C') {  }
else if (p.kind === 'V' || p.kind === 'L') {
const k = f.idxOf(p);
const volts = p.kind === 'V' ? p.value : 0;
if (p.n1 > 0) { A[p.n1 - 1][k] = Lin.cadd(A[p.n1 - 1][k], [1, 0]); A[k][p.n1 - 1] = Lin.cadd(A[k][p.n1 - 1], [1, 0]); }
if (p.n2 > 0) { A[p.n2 - 1][k] = Lin.csub(A[p.n2 - 1][k], [1, 0]); A[k][p.n2 - 1] = Lin.csub(A[k][p.n2 - 1], [1, 0]); }
b[k] = [volts, 0];
}
});
}
function dc(net) {
const bad = problems(net);
if (bad) return { error: bad };
const f = frame(net, 'dc');
if (f.n === 0) return { error: 'Everything is tied to ground; there is nothing to solve for.' };
const devs = devicesOf(net);
const r = iterate(net, f, devs, freshState(devs),
function (A, b) { stampDC(net, f, A, b); }, null,
{ where: 'the operating point', under: UNDER_DC });
if (r.error) return { error: r.error };
const v = [0];
for (let i = 0; i < net.nodeCount - 1; i++) v.push(r.x[i][0]);
const currents = {};
f.carriers.forEach(function (p) { currents[p.id] = r.x[f.idxOf(p)][0]; });
return { v: v, currents: currents, passes: r.passes || 1, tangents: r.tangents || [] };
}
function bias(net) {
if (!net.__bias) net.__bias = dc(net);
return net.__bias;
}
function acSolve(net, w) {
const devs = devicesOf(net);
let tangents = null;
if (devs.length) {
const op = bias(net);
if (op.error) return { error: 'nobias' };
tangents = op.tangents;
}
const f = frame(net, 'ac');
const A = Lin.zeros(f.n);
const b = [];
for (let i = 0; i < f.n; i++) b.push([0, 0]);
if (tangents) {
for (let i = 0; i < net.nodeCount - 1; i++) A[i][i] = Lin.cadd(A[i][i], [GMIN, 0]);
tangents.forEach(function (t) { stampTangent(A, t.nodes, t.j); });
}
net.parts.forEach(function (p) {
if (p.kind === 'R') stampG(A, p.n1, p.n2, [1 / Math.max(p.value, 1e-12), 0]);
else if (p.kind === 'C') stampG(A, p.n1, p.n2, [0, w * p.value]);
else if (p.kind === 'L') stampG(A, p.n1, p.n2, Lin.cdiv([1, 0], [0, w * Math.max(p.value, 1e-15)]));
else if (p.kind === 'I') stampCurrent(b, p.n1, p.n2, [p.value, 0]);
else if (p.kind === 'MCU') stampMcu(A, b, p.mcu);
else if (p.kind === 'V') {
const k = f.idxOf(p);
if (p.n1 > 0) { A[p.n1 - 1][k] = Lin.cadd(A[p.n1 - 1][k], [1, 0]); A[k][p.n1 - 1] = Lin.cadd(A[k][p.n1 - 1], [1, 0]); }
if (p.n2 > 0) { A[p.n2 - 1][k] = Lin.csub(A[p.n2 - 1][k], [1, 0]); A[k][p.n2 - 1] = Lin.csub(A[k][p.n2 - 1], [1, 0]); }
b[k] = [p.value, 0];
}
});
const x = Lin.solve(A, b);
if (!x) return { error: 'singular' };
if (!allFinite(x)) return { error: 'overflow' };
const v = [[0, 0]];
for (let i = 0; i < net.nodeCount - 1; i++) v.push(x[i]);
return { v: v };
}
function acAt(net, w) {
const r = acSolve(net, w);
return r.error ? null : r.v;
}
function ac(net, f1, f2, points) {
const bad = problems(net);
if (bad) return { error: bad };
const shown = function (v) { return isFinite(v) ? fmtEng(v, 'Hz') : 'not a number'; };
if (!(isFinite(f1) && isFinite(f2) && f1 > 0 && f2 > f1)) {
return { error: 'That is not a frequency range. A sweep runs from a lower frequency ' +
'to a higher one and both ends have to be above zero, because the axis is ' +
'logarithmic and there is no room on it between a frequency and itself. From ' +
'reads ' + shown(f1) + ' and To reads ' + shown(f2) + '.' };
}
if (!(points >= 2)) return { error: 'A sweep needs at least two points.' };
if (!net.parts.some(function (p) {
return p.kind === 'V' || p.kind === 'I' || p.kind === 'MCU';
})) {
return { error: 'No source to sweep. Add a voltage or current source.' };
}
if (devicesOf(net).length) {
const op = bias(net);
if (op.error) {
return { error: 'A sweep is taken about the DC operating point, and this circuit ' +
'has not got one. ' + op.error };
}
}
const out = [];
for (let i = 0; i < points; i++) {
const fq = Math.pow(10, Math.log10(f1) + i / (points - 1) * (Math.log10(f2) - Math.log10(f1)));
const r = acSolve(net, 2 * Math.PI * fq);
if (r.error === 'overflow') {
return { error: 'The arithmetic overflowed at ' + fmtEng(fq, 'Hz') + ' and the ' +
'answer came back as not a number. An admittance is wC or 1/(wL), so it is the ' +
'frequency and the reactance TOGETHER that run out of double precision — which ' +
'is why a sweep can overflow at its top end and be perfectly well behaved at ' +
'its bottom one. Rather than draw a plot with a hole in it, this is the answer.' };
}
if (r.error) return { error: 'The circuit is under-determined at ' + fmtEng(fq, 'Hz') + '.' };
out.push({ f: fq, v: r.v });
}
return { sweep: out };
}
function tran(net, tStop, h, hooks) {
const bad = problems(net);
if (bad) return { error: bad };
const f = frame(net, 'tran');
const MAX_STEPS = 4000;
let steps = Math.max(2, Math.round(tStop / h));
if (steps > MAX_STEPS) { h = tStop / MAX_STEPS; steps = MAX_STEPS; }
const prevV = {};
const prevI = {};
net.parts.forEach(function (p) { prevV[p.id] = 0; prevI[p.id] = 0; });
const devs = devicesOf(net);
const state = freshState(devs);
const msg = { where: 'a time step', under: UNDER_TRAN };
function stampStep(hh) {
return function (A, b) {
net.parts.forEach(function (p) {
if (p.kind === 'R') stampG(A, p.n1, p.n2, [1 / Math.max(p.value, 1e-12), 0]);
else if (p.kind === 'C') {
const g = Math.max(p.value, 1e-18) / hh;
stampG(A, p.n1, p.n2, [g, 0]);
stampCurrent(b, p.n1, p.n2, [-g * prevV[p.id], 0]);
} else if (p.kind === 'I') stampCurrent(b, p.n1, p.n2, [p.value, 0]);
else if (p.kind === 'MCU') stampMcu(A, b, p.mcu);
else if (p.kind === 'V' || p.kind === 'L') {
const k = f.idxOf(p);
if (p.n1 > 0) { A[p.n1 - 1][k] = Lin.cadd(A[p.n1 - 1][k], [1, 0]); A[k][p.n1 - 1] = Lin.cadd(A[k][p.n1 - 1], [1, 0]); }
if (p.n2 > 0) { A[p.n2 - 1][k] = Lin.csub(A[p.n2 - 1][k], [1, 0]); A[k][p.n2 - 1] = Lin.csub(A[k][p.n2 - 1], [1, 0]); }
if (p.kind === 'V') {
b[k] = [p.value, 0];
} else {
const Lh = Math.max(p.value, 1e-15) / hh;
A[k][k] = Lin.csub(A[k][k], [Lh, 0]);
b[k] = [-Lh * prevI[p.id], 0];
}
}
});
};
}
const times = [], volts = [];
const v0 = [];
for (let i = 0; i < net.nodeCount; i++) v0.push(0);
let guess = null;
const solveFirst = devs.length ||
net.parts.some(function (p) { return p.kind === 'MCU'; });
if (solveFirst) {
const first = iterate(net, f, devs, state, stampStep(h * 1e-6), null,
{ where: 'the first instant', under: UNDER_TRAN });
if (first.error) return { error: first.error };
for (let i = 0; i < net.nodeCount - 1; i++) v0[i + 1] = first.x[i][0];
guess = first.x;
} else {
net.parts.forEach(function (p) {
if (p.kind === 'V') { if (p.n1 > 0) v0[p.n1] = p.value; }
});
}
times.push(0);
volts.push(v0);
if (hooks && hooks.begin) hooks.begin(h);
if (hooks && hooks.after) hooks.after(0, v0);
const step = stampStep(h);
for (let s = 1; s <= steps; s++) {
const r = iterate(net, f, devs, state, step, guess, msg);
if (r.error) return { error: r.error };
const x = r.x;
guess = x;
const v = [0];
for (let i = 0; i < net.nodeCount - 1; i++) v.push(x[i][0]);
times.push(s * h);
volts.push(v);
net.parts.forEach(function (p) {
if (p.kind === 'C') prevV[p.id] = v[p.n1] - v[p.n2];
if (p.kind === 'L') prevI[p.id] = x[f.idxOf(p)][0];
});
if (hooks && hooks.after) hooks.after(s * h, v);
if (hooks && hooks.stop && hooks.stop()) break;
}
return { t: times, v: volts, h: h };
}
return { dc: dc, ac: ac, tran: tran, acAt: acAt, stampMcu: stampMcu };
})();
function mcuAvailable() { return typeof MCU !== 'undefined' && !!MCU; }
function mcuBoard(rec, ref) {
const byN = {};
rec.pins.forEach(function (p) { if (p.n !== null) byN[p.n] = p; });
const adcs = rec.pins.filter(function (p) { return p.adc; })
.map(function (p) { return p.name; }).join(', ');
const all = rec.pins.filter(function (p) { return p.n !== null; })
.map(function (p) { return p.name; }).join(', ');
function volts(p) {
const v = ref.v;
if (!v) return 0;
return (v[p.node] || 0) - (v[rec.gnd] || 0);
}
return {
pinName: function (n) { return byN[n] ? byN[n].name : null; },
pinList: function () { return all; },
adcList: function () { return adcs; },
mode: function (n) { return byN[n].mode; },
setMode: function (n, m) {
byN[n].mode = m;
if (m !== 'out') byN[n].drive = 0;
},
drive: function (n, d) { byN[n].drive = Math.min(Math.max(d, 0), 1); },
readDigital: function (n) { return mcuLevel(byN[n], volts(byN[n])); },
readAnalog: function (n) {
const p = byN[n];
if (!p.adc) return null;
const frac = volts(p) / MCU_VCC;
return Math.min(Math.max(Math.round(frac * MCU_ADC_MAX), 0), MCU_ADC_MAX);
},
};
}
function mcuRig(net) {
const ids = Object.keys((net && net.mcus) || {});
if (!ids.length) return null;
if (!mcuAvailable()) return { ids: ids, missing: true, rigs: [] };
const ref = { v: null };
let ops = 1;
const rigs = ids.map(function (id) {
const rec = net.mcus[id];
const c = MCU.compile(rec.code);
if (c.error) return { id: id, rec: rec, error: c.error };
return { id: id, rec: rec, machine: MCU.machine(c.program, mcuBoard(rec, ref)) };
});
const live = rigs.filter(function (r) { return r.machine; });
return {
ids: ids, rigs: rigs, missing: false,
faulted: function () {
return live.some(function (r) { return !!r.machine.state().fault; });
},
hooks: {
begin: function (h) { ops = MCU.opsFor(h); },
after: function (t, v) {
ref.v = v;
live.forEach(function (r) { r.machine.advance(t, ops); });
},
stop: function () {
return live.some(function (r) { return !!r.machine.state().fault; });
},
},
ops: function () { return ops; },
};
}
let SYM_STYLE = 'iec';
function symbolStyle(s) {
if (s !== undefined) SYM_STYLE = (s === 'ansi') ? 'ansi' : 'iec';
return SYM_STYLE;
}
function resistorBody(c, x0, x1, h) {
if (SYM_STYLE === 'iec') {
c.moveTo(x0, -h); c.lineTo(x1, -h); c.lineTo(x1, h); c.lineTo(x0, h); c.closePath();
return;
}
const n = 6, w = (x1 - x0) / n, a = h * 1.5;
c.moveTo(x0, 0);
for (let i = 0; i < n; i++) c.lineTo(x0 + (i + 0.5) * w, i % 2 ? a : -a);
c.lineTo(x1, 0);
}
const Symbols = (function () {
const DEF = {};
function define(id, name, draw) { DEF[id] = { id: id, name: name, draw: draw }; }
function get(id) { return DEF[id] || null; }
function ids() { return Object.keys(DEF); }
define('R', 'Resistor', function (c) {
c.moveTo(-60, 0); c.lineTo(-30, 0);
resistorBody(c, -30, 30, 11);
c.moveTo(30, 0); c.lineTo(60, 0);
});
define('LDR', 'Photoresistor', function (c) {
c.moveTo(-60, 0); c.lineTo(-30, 0);
resistorBody(c, -30, 30, 11);
c.moveTo(30, 0); c.lineTo(60, 0);
for (const ax of [-18, 4]) {
c.moveTo(ax - 20, -46); c.lineTo(ax, -26);
c.moveTo(ax, -26); c.lineTo(ax - 11, -29);
c.moveTo(ax, -26); c.lineTo(ax - 3, -37);
}
});
define('NTC', 'Thermistor', function (c) {
c.moveTo(-60, 0); c.lineTo(-30, 0);
resistorBody(c, -30, 30, 11);
c.moveTo(30, 0); c.lineTo(60, 0);
c.moveTo(-36, 26); c.lineTo(-25, 26); c.lineTo(30, -26);
});
define('POT', 'Potentiometer', function (c) {
c.moveTo(-60, 0); c.lineTo(-30, 0);
resistorBody(c, -30, 30, 11);
c.moveTo(30, 0); c.lineTo(60, 0);
c.moveTo(0, -40); c.lineTo(0, -22);
c.moveTo(-8, -30); c.lineTo(0, -21); c.lineTo(8, -30);
});
define('LAMP', 'Lamp', function (c) {
c.moveTo(-60, 0); c.lineTo(-24, 0);
c.moveTo(24, 0); c.lineTo(60, 0);
c.moveTo(24, 0); c.arc(0, 0, 24, 0, Math.PI * 2);
c.moveTo(-17, -17); c.lineTo(17, 17);
c.moveTo(-17, 17); c.lineTo(17, -17);
});
define('METER', 'Ammeter', function (c) {
c.moveTo(-60, 0); c.lineTo(-24, 0);
c.moveTo(24, 0); c.lineTo(60, 0);
c.moveTo(24, 0); c.arc(0, 0, 24, 0, Math.PI * 2);
c.moveTo(-10, 11); c.lineTo(0, -12); c.lineTo(10, 11);
c.moveTo(-5.5, 0); c.lineTo(5.5, 0);
});
define('BAR', 'Bar display', function (c) {
c.moveTo(0, -40); c.lineTo(0, -26);
c.moveTo(-30, -26); c.lineTo(30, -26); c.lineTo(30, 26);
c.lineTo(-30, 26); c.closePath();
for (let i = 0; i < 4; i++) {
c.moveTo(-22 + i * 13, -16); c.lineTo(-22 + i * 13, 16);
}
});
define('OUT', 'Test point', function (c) {
c.moveTo(0, 40); c.lineTo(0, 8);
c.moveTo(0, 8); c.arc(0, 0, 8, Math.PI / 2, Math.PI * 2.5);
c.moveTo(-22, -22); c.lineTo(22, -22);
});
define('BB', 'Breadboard', function (c) {
c.moveTo(-56, -34); c.lineTo(56, -34); c.lineTo(56, 34);
c.lineTo(-56, 34); c.closePath();
c.moveTo(-56, 0); c.lineTo(56, 0);
for (let i = 0; i < 7; i++) {
const x = -42 + i * 14;
c.moveTo(x, -22); c.lineTo(x, -12);
c.moveTo(x, 12); c.lineTo(x, 22);
}
});
define('MCU', 'Microcontroller', function (c) {
c.moveTo(-34, -34); c.lineTo(34, -34); c.lineTo(34, 34);
c.lineTo(-34, 34); c.closePath();
for (let i = 0; i < 4; i++) {
const y = -21 + i * 14;
c.moveTo(-34, y); c.lineTo(-56, y);
c.moveTo(34, y); c.lineTo(56, y);
}
c.moveTo(-34, -20); c.arc(-34, -34, 14, Math.PI / 2, 0, true);
});
define('C', 'Capacitor', function (c) {
c.moveTo(-60, 0); c.lineTo(-9, 0);
c.moveTo(9, 0); c.lineTo(60, 0);
c.moveTo(-9, -26); c.lineTo(-9, 26);
c.moveTo(9, -26); c.lineTo(9, 26);
});
define('L', 'Inductor', function (c) {
c.moveTo(-60, 0); c.lineTo(-32, 0);
for (let i = 0; i < 4; i++) c.arc(-32 + 8 + i * 16, 0, 8, Math.PI, 0, false);
c.lineTo(60, 0);
});
define('D', 'Diode', function (c) {
c.moveTo(-60, 0); c.lineTo(-16, 0);
c.moveTo(-16, -20); c.lineTo(-16, 20); c.lineTo(18, 0); c.closePath();
c.moveTo(18, -20); c.lineTo(18, 20);
c.moveTo(18, 0); c.lineTo(60, 0);
});
define('LED', 'LED', function (c) {
c.moveTo(-60, 0); c.lineTo(-16, 0);
c.moveTo(-16, -20); c.lineTo(-16, 20); c.lineTo(18, 0); c.closePath();
c.moveTo(18, -20); c.lineTo(18, 20);
c.moveTo(18, 0); c.lineTo(60, 0);
for (const dx of [0, 15]) {
c.moveTo(2 + dx, -26); c.lineTo(16 + dx, -40);
c.moveTo(16 + dx, -40); c.lineTo(9 + dx, -38);
c.moveTo(16 + dx, -40); c.lineTo(14 + dx, -33);
}
});
define('GND', 'Ground', function (c) {
c.moveTo(0, -30); c.lineTo(0, 0);
c.moveTo(-34, 0); c.lineTo(34, 0);
c.moveTo(-21, 13); c.lineTo(21, 13);
c.moveTo(-9, 26); c.lineTo(9, 26);
});
define('V', 'Voltage source', function (c) {
c.arc(0, 0, 30, 0, Math.PI * 2);
c.moveTo(-60, 0); c.lineTo(-30, 0);
c.moveTo(30, 0); c.lineTo(60, 0);
c.moveTo(38, -17); c.lineTo(52, -17);
c.moveTo(45, -24); c.lineTo(45, -10);
c.moveTo(-52, -17); c.lineTo(-38, -17);
});
define('BATT', 'Battery', function (c) {
c.moveTo(-60, 0); c.lineTo(-18, 0);
c.moveTo(-18, -26); c.lineTo(-18, 26);
c.moveTo(-6, -13); c.lineTo(-6, 13);
c.moveTo(6, -26); c.lineTo(6, 26);
c.moveTo(18, -13); c.lineTo(18, 13);
c.moveTo(18, 0); c.lineTo(60, 0);
});
define('I', 'Current source', function (c) {
c.arc(0, 0, 30, 0, Math.PI * 2);
c.moveTo(-60, 0); c.lineTo(-30, 0);
c.moveTo(30, 0); c.lineTo(60, 0);
c.moveTo(-21, 0); c.lineTo(21, 0);
c.moveTo(10, -9); c.lineTo(21, 0); c.lineTo(10, 9);
});
define('NPN', 'NPN transistor', function (c) {
c.moveTo(-60, 0); c.lineTo(-14, 0);
c.moveTo(-14, -28); c.lineTo(-14, 28);
c.moveTo(-14, -14); c.lineTo(22, -34);
c.lineTo(22, -60);
c.moveTo(-14, 14); c.lineTo(22, 34);
c.lineTo(22, 60);
c.moveTo(9, 20); c.lineTo(22, 34); c.lineTo(7, 31);
});
define('PNP', 'PNP transistor', function (c) {
c.moveTo(-60, 0); c.lineTo(-14, 0);
c.moveTo(-14, -28); c.lineTo(-14, 28);
c.moveTo(-14, -14); c.lineTo(22, -34);
c.lineTo(22, -60);
c.moveTo(-14, 14); c.lineTo(22, 34);
c.lineTo(22, 60);
c.moveTo(-1, 8); c.lineTo(-14, 14); c.lineTo(-3, 22);
});
function fet(c, into) {
c.moveTo(-60, 0); c.lineTo(-24, 0);
c.moveTo(-24, -30); c.lineTo(-24, 30);
c.moveTo(-12, -30); c.lineTo(-12, -14);
c.moveTo(-12, -7); c.lineTo(-12, 7);
c.moveTo(-12, 14); c.lineTo(-12, 30);
c.moveTo(-12, -22); c.lineTo(22, -22); c.lineTo(22, -60);
c.moveTo(-12, 22); c.lineTo(22, 22); c.lineTo(22, 60);
c.moveTo(-12, 0); c.lineTo(22, 0); c.lineTo(22, 22);
if (into) { c.moveTo(-1, -6); c.lineTo(-12, 0); c.lineTo(-1, 6); }
else { c.moveTo(-11, -6); c.lineTo(0, 0); c.lineTo(-11, 6); }
}
define('NMOS', 'N-channel MOSFET', function (c) { fet(c, true); });
define('PMOS', 'P-channel MOSFET', function (c) { fet(c, false); });
define('SW', 'Switch', function (c) {
c.moveTo(-60, 0); c.lineTo(-24, 0);
c.moveTo(-24, 0); c.lineTo(20, -24);
c.moveTo(24, 0); c.lineTo(60, 0);
c.arc(-24, 0, 4, 0, Math.PI * 2);
c.moveTo(28, 0); c.arc(24, 0, 4, 0, Math.PI * 2);
});
define('OPAMP', 'Op-amp', function (c) {
c.moveTo(-26, -38); c.lineTo(-26, 38); c.lineTo(34, 0); c.closePath();
c.moveTo(-60, -19); c.lineTo(-26, -19);
c.moveTo(-60, 19); c.lineTo(-26, 19);
c.moveTo(34, 0); c.lineTo(60, 0);
c.moveTo(-21, -24); c.lineTo(-9, -24);
c.moveTo(-15, -30); c.lineTo(-15, -18);
c.moveTo(-21, 24); c.lineTo(-9, 24);
});
function paint(canvas, id, colour) {
const spec = DEF[id];
if (!canvas || !spec) return;
const dpr = window.devicePixelRatio || 1;
const w = canvas.clientWidth || 200, h = canvas.clientHeight || 130;
canvas.width = Math.round(w * dpr);
canvas.height = Math.round(h * dpr);
const ctx = canvas.getContext('2d');
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
ctx.clearRect(0, 0, w, h);
const scale = Math.min(w / 150, h / 110);
ctx.save();
ctx.translate(w / 2, h / 2);
ctx.scale(scale, scale);
ctx.strokeStyle = colour || '#EDEFF3';
ctx.lineWidth = 3.4 / scale * Math.max(scale, 0.6);
ctx.lineCap = 'round';
ctx.lineJoin = 'round';
ctx.beginPath();
spec.draw(ctx);
ctx.stroke();
ctx.restore();
}
return { define: define, get: get, ids: ids, paint: paint, all: DEF };
})();
function cktEsc(t) {
return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
}
const BAR_TOOLS = [
['select', 'Select', 'S', 'Select, move and rotate what is already on the canvas'],
['wire', 'Wire', 'W', 'Draw a wire — or just drag from any terminal, which needs no tool at all'],
];
const PART_CATS = [
{ name: 'Passive', hint: 'Resistors, capacitors, inductors', parts: [
['R', 'Resistor', 'R', 'Resistor'],
['C', 'Capacitor', 'C', 'Capacitor'],
['L', 'Inductor', 'L', 'Inductor'],
['POT', 'Potentiometer', '', 'Potentiometer — three pins, a wiper along the track'],
] },
{ name: 'Sources', hint: 'Supplies, ground and probes', parts: [
['V', 'Voltage source', 'V', 'Voltage source'],
['I', 'Current source', 'I', 'Current source'],
['GND', 'Ground', 'G', 'Ground — the node every voltage is measured against'],
['OUT', 'Test point', 'P', 'Mark the output node'],
] },
{ name: 'Switching', hint: 'Switches and sensors', parts: [
['SW', 'Switch', 'K', 'Switch — click it on the canvas to open and close it'],
['LDR', 'Photoresistor', '', 'Light sensor — resistance falls as light rises'],
['NTC', 'Thermistor', '', 'Thermistor — resistance falls as temperature rises'],
] },
{ name: 'Semiconductors', hint: 'Diodes, transistors, op-amps', parts: [
['D', 'Diode', 'D', 'Diode — Shockley, solved by iteration rather than by a 0.7 V rule'],
['LED', 'LED', 'E', 'LED — the same junction, and it lights when it conducts'],
['NPN', 'NPN transistor', 'Q', 'NPN bipolar — Ebers-Moll'],
['PNP', 'PNP transistor', '⇧Q', 'PNP bipolar — Ebers-Moll'],
['NMOS', 'N-channel MOSFET', 'M', 'N-channel MOSFET — level 1 square law'],
['PMOS', 'P-channel MOSFET', '⇧M', 'P-channel MOSFET — level 1 square law'],
['OPAMP', 'Op-amp', 'O', 'Op-amp — finite gain, output limited to its rails'],
] },
{ name: 'Readouts', hint: 'Parts that show you a number', parts: [
['LAMP', 'Lamp', '', 'Indicator lamp — a resistance that lights with the power in it'],
['METER', 'Ammeter', '', 'Ammeter — reads the current through it'],
['BAR', 'Bar display', '', 'Bar display — reads the node it sits on'],
] },
{ name: 'Boards', hint: 'Breadboard and microcontroller', parts: [
['BB', 'Breadboard', 'B', 'Breadboard — a strip of five holes is already one node, with no wire drawn'],
['MCU', 'Microcontroller', 'U', 'Microcontroller — twelve pins and a sketch you write; run it with a transient'],
] },
];
const PART_KEYS = (function () {
const byKey = {};
BAR_TOOLS.concat.apply(BAR_TOOLS, PART_CATS.map(function (c) { return c.parts; }))
.forEach(function (t) {
if (!t[2]) return;
byKey[t[2].replace('⇧', 'shift+').toLowerCase()] = t[0];
});
return byKey;
})();
function toolBtn(t) {
return '<button class="ckt-t ckt-bare" data-tool="' + t[0] + '" title="' + cktEsc(t[3]) +
' (' + t[2] + ')" aria-label="' + cktEsc(t[1]) + '" aria-keyshortcuts="' + t[2] +
'" aria-pressed="false">' + cktEsc(t[1]) + '</button>';
}
function partBtn(t) {
return '<button class="ckt-p" data-tool="' + t[0] + '" title="' + cktEsc(t[3]) +
(t[2] ? ' (' + t[2] + ')' : '') + '" aria-label="' + cktEsc(t[1]) +
'" aria-pressed="false">' +
'<canvas class="ckt-ico" data-sym="' + t[0] + '" aria-hidden="true"></canvas>' +
'<span class="ckt-pl"><span class="ckt-pn">' + cktEsc(t[1]) + '</span>' +
(t[2] ? '<kbd class="ckt-kb">' + cktEsc(t[2]) + '</kbd>' : '') + '</span>' +
'</button>';
}
let cktUid = 0;
function createCircuit(root, opts) {
opts = opts || {};
const GRID = 26;
const model = JSON.parse(JSON.stringify(sanitiseDrawing(opts.model, 0)));
let seq = 0;
(function scan(m) {
(m.parts || []).forEach(function (p) {
const mm = /^p(\d+)$/.exec(p.id);
if (mm) seq = Math.max(seq, +mm[1] + 1);
if (p.inner) scan(p.inner);
});
})(model);
let path = [];
let cur = model;
let tool = 'select';
let view = { s: 1, px: 0, py: 0 };
let selIds = new Set();
let drag = null;
let marquee = null;
let panFrom = null;
let codeFull = false;
let wireFrom = null;
let wireDown = null;
let hoverConn = null;
const selWires = new Set();
let hover = null;
let hoverSp = null;
let caret = null;
let cvFocused = false;
let caretByKey = false;
let analysis = { mode: 'dc', node: 1, f1: 10, f2: 1e6, tstop: 5e-3 };
let result = null;
let mcuRun = null;
let disposed = false;
const uid = 'ckt' + (cktUid++);
if (opts.readOnly) {
root.innerHTML = '<div class="ckt ckt-ro"><div class="ckt-main">' +
'<div class="ckt-canvas"><canvas role="img" aria-label="' +
esc2(opts.label || 'Schematic diagram for this question') + '"></canvas></div></div></div>';
} else {
root.innerHTML =
'<div class="ckt">' +
'<div class="ckt-bar">' +
'<div class="ckt-tools" role="group" aria-label="Tools and parts">' +
BAR_TOOLS.map(toolBtn).join('') +
PART_CATS.map(function (cat) {
return '<details class="ckt-cat"><summary class="ckt-t" title="' +
esc2(cat.hint) + '">' + esc2(cat.name) +
'<span class="ckt-caret" aria-hidden="true">\u25be</span></summary>' +
'<div class="ckt-menu" role="group" aria-label="' + esc2(cat.name) + '">' +
cat.parts.map(partBtn).join('') + '</div></details>';
}).join('') +
'</div>' +
'<span class="spacer"></span>' +
'<button class="ckt-t" data-act="zoomout" title="Zoom out (-)" aria-label="Zoom out">−</button>' +
'<button class="ckt-t" data-act="zoomin" title="Zoom in (+)" aria-label="Zoom in">+</button>' +
'<button class="ckt-t" data-act="fit" title="Fit the drawing to the window (0)">Fit</button>' +
'<button class="ckt-t" data-act="group" title="Fold the selection into one block (Shift+G)">Group</button>' +
'<button class="ckt-t" data-act="ungroup" title="Open a block back out onto the canvas (Shift+U)">Ungroup</button>' +
'<button class="ckt-t" data-act="rotate" title="Rotate the selection (Shift+R)">Rotate</button>' +
'<button class="ckt-t" data-act="delete" title="Delete the selection (Del)">Delete</button>' +
'<button class="ckt-t" data-act="clear">Clear</button>' +
'<button class="ckt-t" data-act="full" title="Fill the screen (F)" ' +
'aria-keyshortcuts="F" aria-pressed="false">Expand</button>' +
'</div>' +
'<div class="ckt-bar" data-crumbs style="display:none"></div>' +
'<div class="ckt-main">' +
'<div class="ckt-canvas">' +
'<canvas tabindex="0" role="application" aria-describedby="' + uid + '-keys"' +
' aria-label="Schematic canvas. Press Enter for the key map."></canvas>' +
'<p class="ckt-vh" id="' + uid + '-keys">Arrow keys move the caret one cell; ' +
'hold Shift to move the selection instead. Enter places the part the toolbar ' +
'has chosen, draws a wire between two presses, or picks up what is under the ' +
'caret; Enter again on a block that is already selected opens it, and on a ' +
'switch throws it. A letter picks a part up: S select, W wire, R resistor, ' +
'C capacitor, L inductor, V voltage source, I current source, G ground, ' +
'P test point, K switch, D diode, E light emitting diode, Q and Shift+Q the ' +
'two bipolars, M and Shift+M the two MOSFETs, O op-amp, B breadboard, ' +
'U microcontroller. Shift+R rotates, Shift+G groups, Shift+U ungroups, ' +
'Delete removes the selected parts and wires, and Escape lets go and then ' +
'closes a block. With a pointer, dragging on empty canvas selects everything ' +
'inside the band, wires included; hold Shift to leave the wires out and add ' +
'to what is already selected. Plus and minus zoom, 0 fits the drawing. Tab ' +
'leaves the canvas.</p>' +
'<p class="ckt-vh" data-say role="status" aria-live="polite"></p>' +
'</div>' +
'<div class="ckt-side">' +
'<div class="ckt-panel" data-panel="part"></div>' +
'<div class="ckt-panel" data-panel="env" hidden></div>' +
'<div class="ckt-panel">' +
'<h4>Analysis</h4>' +
'<div class="seg ckt-modes" role="group" aria-label="Analysis">' +
'<button data-an="dc" class="active" aria-pressed="true">Operating point</button>' +
'<button data-an="ac" aria-pressed="false">Frequency</button>' +
'<button data-an="tran" aria-pressed="false">Transient</button>' +
'</div>' +
'<div class="ckt-opts" data-opts></div>' +
'<button class="btn success ckt-run">Solve</button>' +
'</div>' +
'<div class="ckt-out" data-out role="region" aria-label="Analysis result"></div>' +
'</div>' +
'</div>' +
'<div class="ckt-plot" data-plot hidden><canvas role="img" ' +
'aria-label="The analysis plot. Press Solve to draw one."></canvas></div>' +
'</div>';
}
const cv = root.querySelector('.ckt-canvas canvas');
const ctx = cv.getContext('2d');
const plotWrap = root.querySelector('[data-plot]');
const ro_ = !!opts.readOnly;
const plotCv = plotWrap ? plotWrap.querySelector('canvas') : null;
const outEl = root.querySelector('[data-out]');
const partPanel = root.querySelector('[data-panel="part"]');
const envPanel = root.querySelector('[data-panel="env"]');
const optsEl = root.querySelector('[data-opts]');
const crumbEl = root.querySelector('[data-crumbs]');
const sayEl = root.querySelector('[data-say]');
let saidTwice = false;
function announce(msg) {
if (!sayEl || !msg) return;
saidTwice = !saidTwice;
sayEl.textContent = msg + (saidTwice ? ' ' : '');
}
const env = Object.assign({}, ENV_DEFAULT, (opts.model && opts.model.env) || null);
function snapshot() {
const copy = JSON.parse(JSON.stringify(model));
Object.defineProperty(copy, 'env', {
value: Object.assign({}, env), enumerable: false, writable: true, configurable: true,
});
return copy;
}
function P() { return typeof Sandbox !== 'undefined' ? Sandbox.palette() : { ink: '#EDEFF3', dim: '#868E9C', faint: '#78808E', rule: '#6A7280', line: 'rgba(255,255,255,.10)', accent: '#C7F751', blue: '#6E9BFF', amber: '#FFC66D', purple: '#A78BFA', surface: '#0A0B0E' }; }
function prefix() {
return path.map(function (id) { return id + '|'; }).join('');
}
function reseat() {
const kept = [];
let m = model;
for (let i = 0; i < path.length; i++) {
const b = (m.parts || []).filter(function (q) { return q.id === path[i]; })[0];
if (!b || b.kind !== 'IC') break;
kept.push(b.id);
m = b.inner || (b.inner = { parts: [], wires: [] });
}
path = kept;
cur = m;
}
const originX = 2, originY = 2;
function gx(x) { return (x - originX) * GRID + GRID; }
function gy(y) { return (y - originY) * GRID + GRID; }
function toWorld(sx, sy) { return [sx / view.s + view.px, sy / view.s + view.py]; }
function toGrid(sx, sy) {
const w = toWorld(sx, sy);
return [Math.round((w[0] - GRID) / GRID) + originX, Math.round((w[1] - GRID) / GRID) + originY];
}
function evPt(e) {
const r = cv.getBoundingClientRect();
return [e.clientX - r.left, e.clientY - r.top];
}
function contentBounds() {
let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
const see = function (px, py) {
if (px < x0) x0 = px; if (px > x1) x1 = px;
if (py < y0) y0 = py; if (py > y1) y1 = py;
};
cur.parts.forEach(function (p) {
Netlist.pinsOf(p).forEach(function (pt) { see(pt[0], pt[1]); });
see(p.x, p.y);
if (bodyOf(p)) see(p.x + bodyW(p), p.y + bodyH(p));
});
cur.wires.forEach(function (wr) { see(wr.a[0], wr.a[1]); see(wr.b[0], wr.b[1]); });
if (!isFinite(x0)) return null;
return { x0: x0, y0: y0, x1: x1, y1: y1 };
}
function zoomTo(scale, anchorSx, anchorSy) {
const ns = Math.max(0.3, Math.min(4, isFinite(scale) ? scale : 1));
if (anchorSx === undefined) { view.s = ns; paintSoon(); return; }
const before = toWorld(anchorSx, anchorSy);
view.s = ns;
const after = toWorld(anchorSx, anchorSy);
view.px += before[0] - after[0];
view.py += before[1] - after[1];
paintSoon();
}
let fitShort = false;
function zoomFit() {
const b = contentBounds();
const box = cv.parentElement.getBoundingClientRect();
const w = Math.max(320, box.width), h = Math.max(260, box.height);
if (!b) { view = { s: 1, px: 0, py: 0 }; fitShort = false; paint(); return; }
const pad = 1.5;
const needW = (b.x1 - b.x0 + pad * 2) * GRID, needH = (b.y1 - b.y0 + pad * 2) * GRID;
const want = Math.min(w / needW, h / needH);
view.s = Math.max(0.3, Math.min(4, want));
view.px = gx(b.x0 - pad) - (w / view.s - needW) / 2;
view.py = gy(b.y0 - pad) - (h / view.s - needH) / 2;
fitShort = want < 0.3;
paint();
}
function selOne() {
if (selIds.size !== 1) return null;
const id = selIds.values().next().value;
return cur.parts.find(function (p) { return p.id === id; }) || null;
}
function selParts() { return cur.parts.filter(function (p) { return selIds.has(p.id); }); }
function moveBy(dx, dy) {
const parts = new Set(selParts());
const wires = new Set();
selParts().filter(function (q) { return q.kind === 'BB'; }).forEach(function (b) {
const w = bodyW(b), h = bodyH(b);
const on = function (pt) {
return pt[0] >= b.x && pt[0] <= b.x + w && pt[1] >= b.y && pt[1] <= b.y + h;
};
cur.parts.forEach(function (q) {
if (parts.has(q)) return;
const pins = Netlist.pinsOf(q);
if (pins.length && pins.every(on)) parts.add(q);
});
cur.wires.forEach(function (wr) { if (on(wr.a) && on(wr.b)) wires.add(wr); });
});
const carried = [];
cur.wires.forEach(function (wr) {
const k = wireKey(wr);
if (selWires.has(k)) { selWires.delete(k); carried.push(wr); wires.add(wr); }
});
parts.forEach(function (q) { q.x += dx; q.y += dy; });
wires.forEach(function (wr) {
wr.a = [wr.a[0] + dx, wr.a[1] + dy];
wr.b = [wr.b[0] + dx, wr.b[1] + dy];
});
carried.forEach(function (wr) { selWires.add(wireKey(wr)); });
}
function bodyW(p) { const b = bodyOf(p); return b ? b[0] : 0; }
function bodyH(p) { const b = bodyOf(p); return b ? b[1] : 0; }
function cellPartAt(pt) {
return cur.parts.find(function (p) {
return !bodyOf(p) && p.x === pt[0] && p.y === pt[1];
});
}
function bodyAt(pt) {
return cur.parts.find(function (p) {
const b = bodyOf(p);
return !!b && pt[0] >= p.x && pt[0] <= p.x + b[0] &&
pt[1] >= p.y && pt[1] <= p.y + b[1];
});
}
function partAt(pt) {
return cellPartAt(pt) || bodyAt(pt);
}
function dcAt(pt) {
if (!result || result.kind !== 'dc' || !result.net) return null;
const n = result.net.nodeAt(pt, prefix());
if (n === null || n === undefined || result.v[n] === undefined) return null;
return result.v[n];
}
function acrossOf(p) {
const pins = Netlist.pinsOf(p);
const a = dcAt(pins[0]), b = dcAt(pins[1]);
return (a === null || b === null) ? null : a - b;
}
function lampPower(p) {
const u = acrossOf(p);
return u === null ? null : u * u / Math.max(p.value, 1e-3);
}
function deviceOp(p) {
if (!Devices.is(p.kind)) return null;
const pins = Netlist.pinsOf(p);
const vs = [];
for (let i = 0; i < PART_KINDS[p.kind].pins; i++) {
const u = dcAt(pins[i]);
if (u === null) return null;
vs.push(u);
}
const d = Devices.build(p);
return { v: vs, i: d.iv(d, vs, { raw: true }).i };
}
function mcuRecOf(p) {
if (!result || !result.net || !result.net.mcus) return null;
return result.net.mcus[prefix() + p.id] || null;
}
function drawGlow(pal, br, r) {
const g = Math.sqrt(br);
ctx.save();
ctx.globalAlpha = 0.18 + 0.55 * g;
ctx.fillStyle = pal.amber;
ctx.beginPath(); ctx.arc(0, 0, r, 0, Math.PI * 2); ctx.fill();
ctx.globalAlpha = 0.35 + 0.5 * g;
ctx.strokeStyle = pal.amber;
ctx.beginPath();
for (let i = 0; i < 8; i++) {
const a = i * Math.PI / 4 + Math.PI / 8;
ctx.moveTo(Math.cos(a) * (r + 2), Math.sin(a) * (r + 2));
ctx.lineTo(Math.cos(a) * (r + 3 + 5 * g), Math.sin(a) * (r + 3 + 5 * g));
}
ctx.stroke();
ctx.restore();
ctx.beginPath();
}
function nextRef(kind, within) {
const pre = refPrefix(kind);
const used = {};
(within || model.parts).forEach(function (p) {
if (refPrefix(p.kind) !== pre) return;
const n = typeof p.ref === 'number' ? p.ref : null;
if (n) used[n] = 1;
});
let n = 1;
while (used[n]) n++;
return n;
}
function refOf(p) {
return refPrefix(p.kind) + (typeof p.ref === 'number' ? p.ref : p.id.replace('p', ''));
}
function labelOf(p, k) {
const n = (typeof p.ref === 'number' ? p.ref : p.id.replace('p', ''));
if (p.kind === 'SW') return 'SW' + n + '  ' + (p.closed ? 'closed' : 'open');
if (p.kind === 'LDR' || p.kind === 'NTC') return p.kind + n + '  ' + fmtEng(ohmsOf(p, env), 'Ω');
if (p.kind === 'POT') {
const w = p.wiper === undefined ? 0.5 : p.wiper;
return 'POT' + n + '  ' + fmtEng(p.value, 'Ω') + ' w=' + w.toFixed(2);
}
if (p.kind === 'LAMP') {
const pw = lampPower(p);
return 'LAMP' + n + '  ' + fmtEng(p.value, 'Ω') + (pw === null ? '' : '  ' + fmtEng(pw, 'W'));
}
if (p.kind === 'METER') {
const u = acrossOf(p);
return 'A' + n + (u === null ? '  in series' : '  ' + fmtEng(u / Math.max(p.value, 1e-6), 'A'));
}
if (Devices.is(p.kind)) {
const op = deviceOp(p);
if (p.kind === 'OPAMP') return 'U' + n + '  A=' + fmtEng(p.value, '');
if (op === null) return p.kind + n;
if (p.kind === 'D' || p.kind === 'LED') {
return p.kind + n + '  ' + fmtEng(op.v[0] - op.v[1], 'V') + ' ' + fmtEng(op.i[0], 'A');
}
return p.kind + n + '  ' + (p.kind === 'NPN' || p.kind === 'PNP' ? 'Ic ' : 'Id ') +
fmtEng(Math.abs(op.i[0]), 'A');
}
return p.kind + n + '  ' + fmtEng(p.value, k.unit);
}
function drawBoard(p, colour, pal) {
const C = bbCols(p);
const edge = colour || pal.line;
const M = 0.8;
const x0 = gx(p.x - M), x1 = gx(p.x + C - 1 + M);
const y0 = gy(p.y - M), y1 = gy(p.y + BB_H - 1 + M);
const r = 5;
ctx.save();
ctx.lineWidth = 1.5;
ctx.lineCap = 'butt';
ctx.beginPath();
ctx.moveTo(x0 + r, y0);
ctx.lineTo(x1 - r, y0); ctx.quadraticCurveTo(x1, y0, x1, y0 + r);
ctx.lineTo(x1, y1 - r); ctx.quadraticCurveTo(x1, y1, x1 - r, y1);
ctx.lineTo(x0 + r, y1); ctx.quadraticCurveTo(x0, y1, x0, y1 - r);
ctx.lineTo(x0, y0 + r); ctx.quadraticCurveTo(x0, y0, x0 + r, y0);
ctx.closePath();
ctx.fillStyle = pal.surface || '#0A0B0E';
ctx.fill();
ctx.strokeStyle = edge;
ctx.stroke();
const cy0 = gy(p.y + BB_CHAN - 0.5), cy1 = gy(p.y + BB_CHAN + 0.5);
ctx.fillStyle = pal.faint;
ctx.globalAlpha = 0.12;
ctx.fillRect(x0 + 1.5, cy0, x1 - x0 - 3, cy1 - cy0);
ctx.globalAlpha = 1;
ctx.strokeStyle = pal.rule;
ctx.lineWidth = 1;
ctx.beginPath();
ctx.moveTo(x0 + 1.5, cy0); ctx.lineTo(x1 - 1.5, cy0);
ctx.moveTo(x0 + 1.5, cy1); ctx.lineTo(x1 - 1.5, cy1);
ctx.stroke();
ctx.lineWidth = 1.5;
ctx.font = '10px ui-monospace, monospace';
ctx.textBaseline = 'middle';
[[0, -1, '+', pal.amber], [BB_RAIL - 1, 1, '−', pal.blue],
[BB_H - BB_RAIL, -1, '−', pal.blue], [BB_H - 1, 1, '+', pal.amber]]
.forEach(function (rail) {
const ry = gy(p.y + rail[0]) + rail[1] * GRID * 0.42;
ctx.strokeStyle = rail[3];
ctx.beginPath();
ctx.moveTo(gx(p.x), ry); ctx.lineTo(gx(p.x + C - 1), ry);
ctx.stroke();
ctx.fillStyle = rail[3];
ctx.textAlign = 'right';
ctx.fillText(rail[2], x0 - 4, ry);
ctx.textAlign = 'left';
ctx.fillText(rail[2], x1 + 4, ry);
});
ctx.fillStyle = pal.dim;
ctx.globalAlpha = 0.7;
for (let c = 0; c < C; c++) {
for (let rw = 0; rw < BB_H; rw++) {
if (bbStripAt(p, p.x + c, p.y + rw) === null) continue;
ctx.fillRect(gx(p.x + c) - 1.6, gy(p.y + rw) - 1.6, 3.2, 3.2);
}
}
ctx.font = '8.5px ui-monospace, monospace';
ctx.textAlign = 'center';
for (let c = 4; c < C; c += 5) ctx.fillText(String(c + 1), gx(p.x + c), gy(p.y + BB_CHAN));
ctx.globalAlpha = 1;
ctx.restore();
}
function drawPart(p, colour, pal) {
const x = gx(p.x), y = gy(p.y);
const k = PART_KINDS[p.kind];
pal = pal || P();
ctx.strokeStyle = colour;
ctx.fillStyle = colour;
ctx.lineWidth = 1.8;
ctx.lineCap = 'round';
if (p.kind === 'OUT') {
ctx.beginPath();
ctx.arc(x, y, 5, 0, Math.PI * 2);
ctx.stroke();
ctx.beginPath();
ctx.moveTo(x, y - 5); ctx.lineTo(x, y - 13);
ctx.stroke();
ctx.font = '10px ui-monospace, monospace';
ctx.textAlign = 'center';
ctx.fillText('out', x, y - 18);
return;
}
if (p.kind === 'GND') {
ctx.beginPath();
ctx.moveTo(x, y); ctx.lineTo(x, y + 8);
ctx.moveTo(x - 9, y + 8); ctx.lineTo(x + 9, y + 8);
ctx.moveTo(x - 5, y + 12); ctx.lineTo(x + 5, y + 12);
ctx.moveTo(x - 2, y + 16); ctx.lineTo(x + 2, y + 16);
ctx.stroke();
return;
}
if (p.kind === 'BAR') {
const full = Math.abs(p.value) > 1e-12 ? Math.abs(p.value) : 5;
const v = dcAt([p.x, p.y]);
const bw = 48, bh = 11, bx = x - bw / 2, by = y - 8 - bh;
ctx.beginPath();
ctx.moveTo(x, y); ctx.lineTo(x, by + bh);
ctx.stroke();
ctx.strokeRect(bx, by, bw, bh);
if (v !== null) {
const frac = Math.min(Math.max(v / full, 0), 1);
ctx.fillStyle = v < 0 ? pal.amber : colour;
if (frac > 0) ctx.fillRect(bx + 1.5, by + 1.5, (bw - 3) * frac, bh - 3);
if (v > full) {
ctx.beginPath();
ctx.moveTo(bx + bw + 3, by + 1); ctx.lineTo(bx + bw + 8, by + bh / 2);
ctx.lineTo(bx + bw + 3, by + bh - 1);
ctx.fillStyle = pal.amber;
ctx.fill();
}
}
ctx.font = '10.5px ui-monospace, monospace';
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';
ctx.fillStyle = v === null ? pal.dim : (v < 0 || v > full ? pal.amber : colour);
ctx.fillText(v === null ? 'BAR' + p.id.replace('p', '') : fmtEng(v, 'V'), x, by - 8);
ctx.fillStyle = pal.dim;
ctx.fillText('0–' + fmtEng(full, 'V'), x, y + 11);
return;
}
if (p.kind === 'MCU') {
const rec = mcuRecOf(p);
const bx = gx(p.x + MCU_W), by = gy(p.y + MCU_H), r = 4;
ctx.beginPath();
ctx.moveTo(x + r, y);
ctx.lineTo(bx - r, y); ctx.quadraticCurveTo(bx, y, bx, y + r);
ctx.lineTo(bx, by - r); ctx.quadraticCurveTo(bx, by, bx - r, by);
ctx.lineTo(x + r, by); ctx.quadraticCurveTo(x, by, x, by - r);
ctx.lineTo(x, y + r); ctx.quadraticCurveTo(x, y, x + r, y);
ctx.closePath();
ctx.fillStyle = pal.surface || '#0A0B0E';
ctx.fill();
ctx.strokeStyle = colour;
ctx.stroke();
ctx.font = '9px ui-monospace, monospace';
ctx.textBaseline = 'middle';
MCU_PINS.forEach(function (d, i) {
const pin = rec ? rec.pins[i] : null;
const px = gx(p.x + (d.side ? MCU_W : 0)), py = gy(p.y + d.row);
const driving = pin && (pin.power || pin.mode === 'out' || pin.mode === 'pullup');
ctx.fillStyle = pin && pin.mode === 'out' && pin.drive > 0.5 ? pal.accent : colour;
if (driving) ctx.fillRect(px - 3, py - 3, 6, 6);
else { ctx.strokeStyle = colour; ctx.strokeRect(px - 2.5, py - 2.5, 5, 5); }
ctx.fillStyle = d.power ? pal.dim : colour;
ctx.textAlign = d.side ? 'right' : 'left';
ctx.fillText(d.name, px + (d.side ? -7 : 7), py);
if (!pin || d.power) return;
const tag = pin.mode === 'out'
? (pin.drive === 0 || pin.drive === 1 ? (pin.drive ? 'H' : 'L')
: Math.round(pin.drive * 100) + '%')
: pin.mode === 'pullup' ? 'pu' : '';
if (!tag) return;
ctx.fillStyle = pal.dim;
ctx.fillText(tag, px + (d.side ? -30 : 30), py);
});
ctx.fillStyle = colour;
ctx.textAlign = 'center';
ctx.font = '10px ui-monospace, monospace';
ctx.fillText('MCU' + p.id.replace('p', ''), (x + bx) / 2, gy(p.y) + GRID / 2);
ctx.font = '8.5px ui-monospace, monospace';
ctx.fillStyle = pal.dim;
ctx.fillText(fmtEng(MCU_VCC, 'V'), (x + bx) / 2, gy(p.y + MCU_H) - GRID / 2);
return;
}
if (p.kind === 'IC') {
const bx = gx(p.x + bodyW(p)), by = gy(p.y + bodyH(p)), r = 4;
ctx.beginPath();
ctx.moveTo(x + r, y);
ctx.lineTo(bx - r, y); ctx.quadraticCurveTo(bx, y, bx, y + r);
ctx.lineTo(bx, by - r); ctx.quadraticCurveTo(bx, by, bx - r, by);
ctx.lineTo(x + r, by); ctx.quadraticCurveTo(x, by, x, by - r);
ctx.lineTo(x, y + r); ctx.quadraticCurveTo(x, y, x + r, y);
ctx.closePath();
ctx.fillStyle = pal.surface || '#0A0B0E';
ctx.fill();
ctx.strokeStyle = colour;
ctx.stroke();
ctx.fillStyle = colour;
ctx.font = '9.5px ui-monospace, monospace';
ctx.textBaseline = 'middle';
(p.ports || []).forEach(function (port) {
(port.cells || []).forEach(function (c) {
const px = gx(p.x + c[0]), py = gy(p.y + c[1]);
ctx.fillRect(px - 2.5, py - 2.5, 5, 5);
if (c[0] === 0) { ctx.textAlign = 'left'; ctx.fillText(port.name, px + 7, py); }
else if (c[0] === bodyW(p)) { ctx.textAlign = 'right'; ctx.fillText(port.name, px - 7, py); }
else { ctx.textAlign = 'center'; ctx.fillText(port.name, px, py + (c[1] === 0 ? 9 : -9)); }
});
});
ctx.save();
ctx.beginPath();
ctx.rect(x + 2, y + 2, bx - x - 4, by - y - 4);
ctx.clip();
const held = ((p.inner && p.inner.parts) || []).length;
const mx = (x + bx) / 2, my = (y + by) / 2;
ctx.textAlign = 'center';
ctx.font = 'bold 11px ui-monospace, monospace';
ctx.fillText(p.title || 'Block', mx, held ? my - 6 : my);
if (held) {
ctx.font = '9.5px ui-monospace, monospace';
ctx.fillStyle = pal.dim;
ctx.fillText(held + (held === 1 ? ' part' : ' parts'), mx, my + 7);
}
ctx.restore();
return;
}
ctx.save();
ctx.translate(x, y);
if (p.rot) ctx.rotate(turnsOf(p) * Math.PI / 2);
const L = GRID;
ctx.beginPath();
if (p.kind === 'R') {
ctx.moveTo(-L, 0); ctx.lineTo(-13, 0);
resistorBody(ctx, -13, 13, 4);
ctx.moveTo(13, 0); ctx.lineTo(L, 0);
ctx.stroke();
} else if (p.kind === 'C') {
ctx.moveTo(-L, 0); ctx.lineTo(-4, 0);
ctx.moveTo(4, 0); ctx.lineTo(L, 0);
ctx.moveTo(-4, -9); ctx.lineTo(-4, 9);
ctx.moveTo(4, -9); ctx.lineTo(4, 9);
ctx.stroke();
} else if (p.kind === 'L') {
ctx.moveTo(-L, 0); ctx.lineTo(-14, 0);
for (let i = 0; i < 4; i++) ctx.arc(-14 + 7 + i * 7, 0, 3.5, Math.PI, 0, false);
ctx.lineTo(L, 0);
ctx.stroke();
} else if (p.kind === 'SW') {
ctx.moveTo(-L, 0); ctx.lineTo(-12, 0);
ctx.moveTo(12, 0); ctx.lineTo(L, 0);
if (p.closed) { ctx.moveTo(-12, 0); ctx.lineTo(12, 0); }
else { ctx.moveTo(-12, 0); ctx.lineTo(10, -12); }
ctx.stroke();
ctx.beginPath(); ctx.arc(-12, 0, 2.2, 0, Math.PI * 2); ctx.fill();
ctx.beginPath(); ctx.arc(12, 0, 2.2, 0, Math.PI * 2); ctx.fill();
} else if (p.kind === 'LDR' || p.kind === 'NTC' || p.kind === 'POT') {
ctx.moveTo(-L, 0); ctx.lineTo(-13, 0);
resistorBody(ctx, -13, 13, 4);
ctx.moveTo(13, 0); ctx.lineTo(L, 0);
if (p.kind === 'LDR') {
for (const ax of [-8, 2]) {
ctx.moveTo(ax - 9, -21); ctx.lineTo(ax, -12);
ctx.moveTo(ax, -12); ctx.lineTo(ax - 5, -13.5);
ctx.moveTo(ax, -12); ctx.lineTo(ax - 1.5, -17);
}
} else if (p.kind === 'NTC') {
ctx.moveTo(-16, 12); ctx.lineTo(-11, 12); ctx.lineTo(13, -12);
} else {
ctx.moveTo(0, -L); ctx.lineTo(0, -10);
ctx.moveTo(-3.5, -14); ctx.lineTo(0, -9.5); ctx.lineTo(3.5, -14);
}
ctx.stroke();
} else if (p.kind === 'D' || p.kind === 'LED') {
if (p.kind === 'LED') {
const op = deviceOp(p);
const br = op === null ? 0
: Math.min(Math.max(op.i[0] / Math.max(p.inom === undefined ? 0.02 : p.inom, 1e-9), 0), 1);
if (br > 0.002) drawGlow(pal, br, 12);
}
ctx.save();
const sd = L / 60;
ctx.scale(sd, sd);
ctx.lineWidth = 1.8 / sd;
ctx.beginPath();
Symbols.get(p.kind).draw(ctx);
ctx.stroke();
ctx.restore();
} else if (p.kind === 'NPN' || p.kind === 'PNP' || p.kind === 'NMOS' || p.kind === 'PMOS') {
ctx.save();
const sx = 2 * L / 120, sy = L / 82;
ctx.transform(0, sy, sx, 0, 0, -sy * 22);
ctx.lineWidth = 1.8 / Math.sqrt(sx * sy);
ctx.beginPath();
Symbols.get(p.kind).draw(ctx);
ctx.stroke();
ctx.restore();
} else if (p.kind === 'OPAMP') {
ctx.moveTo(-13, -15); ctx.lineTo(13, 0); ctx.lineTo(-13, 15); ctx.closePath();
ctx.moveTo(-L, 0); ctx.lineTo(-13, 0);
ctx.moveTo(13, 0); ctx.lineTo(L, 0);
ctx.moveTo(0, -L); ctx.lineTo(0, -7.5);
ctx.moveTo(-11, 6); ctx.lineTo(-5, 6);
ctx.moveTo(-8, 3); ctx.lineTo(-8, 9);
ctx.moveTo(-8, -7); ctx.lineTo(-2, -7);
ctx.stroke();
} else if (p.kind === 'LAMP') {
const pw = lampPower(p);
const br = pw === null ? 0 : Math.min(Math.max(pw / Math.max(p.pnom === undefined ? 0.25 : p.pnom, 1e-9), 0), 1);
if (br > 0.002) drawGlow(pal, br, 11);
ctx.moveTo(-L, 0); ctx.lineTo(-11, 0);
ctx.moveTo(11, 0); ctx.lineTo(L, 0);
ctx.stroke();
ctx.beginPath();
ctx.arc(0, 0, 11, 0, Math.PI * 2);
ctx.stroke();
ctx.beginPath();
const d = 11 * Math.SQRT1_2;
ctx.moveTo(-d, -d); ctx.lineTo(d, d);
ctx.moveTo(-d, d); ctx.lineTo(d, -d);
ctx.stroke();
} else if (p.kind === 'METER') {
ctx.moveTo(-L, 0); ctx.lineTo(-11, 0);
ctx.moveTo(11, 0); ctx.lineTo(L, 0);
ctx.stroke();
ctx.beginPath();
ctx.arc(0, 0, 11, 0, Math.PI * 2);
ctx.stroke();
ctx.beginPath();
ctx.moveTo(-7, -16); ctx.lineTo(7, -16);
ctx.moveTo(3, -19); ctx.lineTo(7, -16); ctx.lineTo(3, -13);
ctx.stroke();
} else {
ctx.moveTo(-L, 0); ctx.lineTo(-11, 0);
ctx.moveTo(11, 0); ctx.lineTo(L, 0);
ctx.stroke();
ctx.beginPath();
ctx.arc(0, 0, 11, 0, Math.PI * 2);
ctx.stroke();
if (p.kind === 'I') {
ctx.beginPath();
const sgn = (turnsOf(p) % 2) ? -1 : 1;
ctx.moveTo(-8 * sgn, 0); ctx.lineTo(8 * sgn, 0);
ctx.moveTo(3.5 * sgn, -4); ctx.lineTo(8 * sgn, 0); ctx.lineTo(3.5 * sgn, 4);
ctx.stroke();
}
}
ctx.restore();
if (p.kind === 'V') {
const r = turnsOf(p);
const d = [[1, 0], [0, -1], [-1, 0], [0, 1]][r];
const q = (r % 2) ? [-1, 0] : [0, -1];
const px = x + d[0] * 17 + q[0] * 8, py = y + d[1] * 17 + q[1] * 8;
const nx = x - d[0] * 17 + q[0] * 8, ny = y - d[1] * 17 + q[1] * 8;
ctx.beginPath();
ctx.moveTo(px - 3.5, py); ctx.lineTo(px + 3.5, py);
ctx.moveTo(px, py - 3.5); ctx.lineTo(px, py + 3.5);
ctx.moveTo(nx - 3.5, ny); ctx.lineTo(nx + 3.5, ny);
ctx.stroke();
}
if (p.kind === 'METER') {
ctx.font = 'bold 10px ui-monospace, monospace';
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';
ctx.fillStyle = colour;
ctx.fillText('A', x, y + 0.5);
}
ctx.font = '10.5px ui-monospace, monospace';
ctx.textAlign = 'center';
ctx.textBaseline = 'middle';
ctx.fillStyle = colour;
const lab = labelOf(p, k);
const wide = { LDR: 24, METER: 22, LAMP: 22, SW: 20, NTC: 20 }[p.kind];
if ((PART_KINDS[p.kind] || {}).pins === 3) {
const r = turnsOf(p);
if (r === 1) { ctx.textAlign = 'right'; ctx.fillText(lab, x - 22, y); }
else if (r === 3) { ctx.textAlign = 'left'; ctx.fillText(lab, x + 22, y); }
else ctx.fillText(lab, x, y + (r === 2 ? -22 : 22));
} else if (wide) {
if (turnsOf(p) % 2) { ctx.textAlign = 'left'; ctx.fillText(lab, x + wide, y); }
else ctx.fillText(lab, x, y - 26);
} else if (turnsOf(p) % 2) {
ctx.textAlign = 'left';
ctx.fillText(lab, x + 17, y);
} else ctx.fillText(lab, x, y - 17);
}
function paint() {
if (disposed) return;
const box = cv.parentElement.getBoundingClientRect();
const dpr = Math.min(window.devicePixelRatio || 1, 2);
const w = Math.max(320, Math.round(box.width));
const h = Math.max(260, Math.round(box.height));
if (cv.width !== w * dpr || cv.height !== h * dpr) {
cv.width = w * dpr; cv.height = h * dpr;
cv.style.width = w + 'px'; cv.style.height = h + 'px';
}
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
const pal = P();
ctx.clearRect(0, 0, w, h);
let roScale = 1, roX0 = 0, roY0 = 0;
const rob = ro_ && cur.parts.length ? contentBounds() : null;
if (rob) {
const pad = 1.2;
const needW = (rob.x1 - rob.x0 + pad * 2) * GRID, needH = (rob.y1 - rob.y0 + pad * 2) * GRID;
roScale = Math.max(0.08, Math.min(w / needW, h / needH, 1.6));
roX0 = (rob.x0 - pad - originX) * GRID + GRID - (w / roScale - needW) / 2;
roY0 = (rob.y0 - pad - originY) * GRID + GRID - (h / roScale - needH) / 2;
ctx.setTransform(dpr * roScale, 0, 0, dpr * roScale,
-roX0 * roScale * dpr, -roY0 * roScale * dpr);
}
if (!ro_) {
ctx.setTransform(dpr * view.s, 0, 0, dpr * view.s,
-view.px * view.s * dpr, -view.py * view.s * dpr);
}
const dscale = ro_ ? roScale : view.s;
const vx0 = ro_ ? roX0 : view.px, vy0 = ro_ ? roY0 : view.py;
const vx1 = vx0 + w / dscale, vy1 = vy0 + h / dscale;
const GRID_MIN_PX = 5;
const GRID_MAX = 20000;
if (GRID * dscale >= GRID_MIN_PX) {
const c0 = Math.max(1, Math.floor(vx0 / GRID)), c1 = Math.floor(vx1 / GRID) + 1;
const r0 = Math.max(1, Math.floor(vy0 / GRID)), r1 = Math.floor(vy1 / GRID) + 1;
const cols = Math.min(Math.max(0, c1 - c0 + 1), GRID_MAX);
const rows = Math.min(Math.max(0, r1 - r0 + 1), GRID_MAX);
ctx.fillStyle = pal.faint;
ctx.globalAlpha = 0.20;
for (let i = 0; i < cols; i++) {
const X = (c0 + i) * GRID;
for (let j = 0; j < rows; j++) {
ctx.fillRect(X - 0.5, (r0 + j) * GRID - 0.5, 1, 1);
}
}
ctx.globalAlpha = 1;
}
cur.parts.forEach(function (p) {
if (p.kind === 'BB') drawBoard(p, selIds.has(p.id) ? pal.accent : null, pal);
});
ctx.lineWidth = 2;
cur.wires.forEach(function (wr) {
const on = selWires.has(wireKey(wr));
ctx.strokeStyle = on ? pal.accent : pal.dim;
ctx.lineWidth = on ? 4 : 2;
ctx.beginPath();
ctx.moveTo(gx(wr.a[0]), gy(wr.a[1]));
ctx.lineTo(gx(wr.b[0]), gy(wr.b[1]));
ctx.stroke();
});
ctx.lineWidth = 2;
const count = {};
function bump(pt) { const k = pt[0] + ',' + pt[1]; count[k] = (count[k] || 0) + 1; }
cur.wires.forEach(function (wr) { bump(wr.a); bump(wr.b); });
cur.parts.forEach(function (p) { Netlist.pinsOf(p).forEach(bump); });
ctx.fillStyle = pal.dim;
Object.keys(count).forEach(function (k) {
if (count[k] < 3) return;
const xy = k.split(',').map(Number);
ctx.beginPath();
ctx.arc(gx(xy[0]), gy(xy[1]), 3, 0, Math.PI * 2);
ctx.fill();
});
cur.parts.forEach(function (p) {
if (p.kind === 'BB') return;
drawPart(p, selIds.has(p.id) ? pal.accent : pal.ink, pal);
});
paintMarquee();
const lead = hover || (cvFocused && caretByKey ? caret : null);
if (wireFrom && lead) {
ctx.save();
ctx.setLineDash([4, 4]);
ctx.strokeStyle = pal.accent;
ctx.lineWidth = 2;
ctx.beginPath();
ctx.moveTo(gx(wireFrom[0]), gy(wireFrom[1]));
elbow(wireFrom, lead).forEach(function (seg) {
ctx.lineTo(gx(seg[1][0]), gy(seg[1][1]));
});
ctx.stroke();
ctx.restore();
const tgt = connAt(lead);
if (tgt) {
ctx.save();
ctx.strokeStyle = pal.accent;
ctx.lineWidth = 2 / view.s;
ctx.beginPath();
ctx.arc(gx(lead[0]), gy(lead[1]), GRID * 0.3, 0, Math.PI * 2);
ctx.stroke();
ctx.restore();
}
}
if (hoverConn && !wireFrom) {
ctx.save();
ctx.strokeStyle = pal.accent;
ctx.fillStyle = pal.accent;
ctx.lineWidth = 2 / view.s;
ctx.beginPath();
ctx.arc(gx(hoverConn.pt[0]), gy(hoverConn.pt[1]), GRID * 0.3, 0, Math.PI * 2);
if (hoverConn.kind === 'wire') { ctx.globalAlpha = 0.25; ctx.fill(); ctx.globalAlpha = 1; }
ctx.stroke();
ctx.restore();
}
if (cvFocused && caret && caretByKey) {
ctx.save();
ctx.strokeStyle = pal.accent;
ctx.lineWidth = 2 / view.s;
ctx.beginPath();
ctx.arc(gx(caret[0]), gy(caret[1]), GRID * 0.44, 0, Math.PI * 2);
ctx.stroke();
ctx.setLineDash([3 / view.s, 3 / view.s]);
ctx.lineWidth = 1 / view.s;
ctx.beginPath();
ctx.moveTo(gx(caret[0]) - GRID * 0.8, gy(caret[1]));
ctx.lineTo(gx(caret[0]) + GRID * 0.8, gy(caret[1]));
ctx.moveTo(gx(caret[0]), gy(caret[1]) - GRID * 0.8);
ctx.lineTo(gx(caret[0]), gy(caret[1]) + GRID * 0.8);
ctx.stroke();
ctx.restore();
}
if (result && result.kind === 'dc' && result.net) {
ctx.font = '10.5px ui-monospace, monospace';
ctx.textAlign = 'left';
const at = prefix();
const seen = {};
cur.parts.forEach(function (p) {
Netlist.pinsOf(p).forEach(function (pt) {
const n = result.net.nodeAt(pt, at);
if (n === null || n === 0 || seen[n]) return;
seen[n] = 1;
ctx.fillStyle = pal.accent;
ctx.fillText(fmtEng(result.v[n], 'V'), gx(pt[0]) + 6, gy(pt[1]) - 8);
});
});
}
paintTip(pal, w, h);
describeCanvas();
}
const paintSoon = perFrame(function () { paint(); });
let lastName = null;
function describeCanvas() {
if (ro_) return;
const np = cur.parts.length, nw = cur.wires.length;
let s = 'Schematic canvas. ';
s += np ? np + (np === 1 ? ' part' : ' parts') : 'No parts';
s += nw ? ' and ' + nw + (nw === 1 ? ' wire. ' : ' wires. ') : '. ';
if (path.length) s += 'Inside a block, ' + path.length + ' deep. ';
if (selIds.size) s += selIds.size + ' selected. ';
s += 'Zoom ' + Math.round(view.s * 100) + ' per cent. Press Enter for the key map.';
if (s !== lastName) { cv.setAttribute('aria-label', s); lastName = s; }
}
function paintTip(pal, w, h) {
const b = hoverSp && tipBlock();
if (!b) return;
const title = String(b.title || 'Block');
const desc = String(b.desc || '').trim();
ctx.save();
const dpr = Math.min(window.devicePixelRatio || 1, 2);
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
const PAD = 8, MAXW = 230;
ctx.font = 'bold 11.5px ui-monospace, monospace';
let width = Math.min(Math.max(ctx.measureText(title).width, 90), MAXW);
ctx.font = '11px ui-monospace, monospace';
const lines = desc
? wrapText(desc, MAXW)
: ['Double-click to open it. Describe it in the panel.'];
lines.forEach(function (l) { width = Math.max(width, Math.min(ctx.measureText(l).width, MAXW)); });
const bh = PAD * 2 + 15 + lines.length * 14;
const bw = width + PAD * 2;
const tx = Math.min(hoverSp[0] + 14, Math.max(4, w - bw - 4));
const ty = Math.min(hoverSp[1] + 16, Math.max(4, h - bh - 4));
ctx.globalAlpha = 0.97;
ctx.fillStyle = pal.surface || '#0A0B0E';
ctx.fillRect(tx, ty, bw, bh);
ctx.globalAlpha = 1;
ctx.strokeStyle = pal.accent;
ctx.lineWidth = 1;
ctx.strokeRect(tx + 0.5, ty + 0.5, bw - 1, bh - 1);
ctx.textAlign = 'left';
ctx.textBaseline = 'alphabetic';
ctx.fillStyle = pal.accent;
ctx.font = 'bold 11.5px ui-monospace, monospace';
ctx.fillText(title, tx + PAD, ty + PAD + 11);
ctx.fillStyle = desc ? pal.ink : pal.dim;
ctx.font = '11px ui-monospace, monospace';
lines.forEach(function (l, i) { ctx.fillText(l, tx + PAD, ty + PAD + 26 + i * 14); });
ctx.restore();
}
function wrapText(text, maxw) {
const words = text.split(/\s+/);
const out = [];
let line = '';
for (let i = 0; i < words.length && out.length < 8; i++) {
const test = line ? line + ' ' + words[i] : words[i];
if (ctx.measureText(test).width > maxw && line) { out.push(line); line = words[i]; }
else line = test;
}
if (line && out.length < 8) out.push(line);
else if (line) out[out.length - 1] += ' …';
return out;
}
function tipBlock() {
if (drag || marquee || panFrom || wireFrom || !hover) return null;
const hit = partAt(hover);
return hit && hit.kind === 'IC' ? hit : null;
}
function paintMarquee() {
if (!marquee) return;
const a = marquee.a, b = marquee.b;
const x = Math.min(a[0], b[0]), y = Math.min(a[1], b[1]);
ctx.save();
ctx.strokeStyle = P().accent;
ctx.setLineDash([4, 3]);
ctx.lineWidth = 1 / view.s;
ctx.strokeRect(x, y, Math.abs(b[0] - a[0]), Math.abs(b[1] - a[1]));
ctx.restore();
}
function paintPart() {
const p = selOne();
if (codeFull && !(p && p.kind === 'MCU')) {
codeFull = false;
const openBox = partPanel.querySelector('.ckt-code');
if (openBox) openBox.classList.remove('full');
syncExpanded();
}
if (selIds.size > 1) {
partPanel.innerHTML = '<h4>' + selIds.size + ' parts' +
(selWires.size ? ' and ' + selWires.size + (selWires.size === 1 ? ' wire' : ' wires') : '') + ' selected</h4>' +
'<p class="ckt-hint">Drag to move them together' +
(selWires.size ? ', wires included' : '') + '. R rotates, Delete removes. ' +
'G folds them into one block, whose pins are worked out from which nets cross ' +
'the edge of the selection; U opens any block among them back out. ' +
'Click an empty cell to deselect.</p>';
return;
}
if (p && p.kind === 'IC') { paintBlock(p); return; }
if (p && p.kind === 'MCU') { paintMcu(p); return; }
if (!p || p.kind === 'GND' || p.kind === 'OUT') {
partPanel.innerHTML = '<h4>Component</h4><p class="ckt-hint">' +
(tool === 'wire' ? 'Click a pin, then click where the wire should end.'
: tool === 'select' ? 'Click a component to select it, or drag on empty canvas to select everything the band surrounds, wires included; Shift leaves the wires out.'
: 'Click the grid to place a ' + PART_KINDS[tool].name.toLowerCase() + '.') +
' Or tab to the canvas and use the arrow keys: Enter does what a click does, ' +
'Shift with an arrow moves what is selected, and Escape lets go.</p>';
return;
}
const k = PART_KINDS[p.kind];
partPanel.innerHTML = '<h4>' + k.name + ' ' + esc2(refOf(p)) + '</h4>' +
(p.kind === 'SW'
? '<button class="ckt-t" data-sw style="width:100%;margin-bottom:8px">' +
(p.closed ? 'Closed — click to open' : 'Open — click to close') + '</button>'
: '<label class="ckt-f"><span>' + esc2(VALUE_LABEL[p.kind] || ('Value (' + k.unit + ')')) + '</span>' +
'<input data-val value="' + esc2(fmtEng(p.value, '').trim()) + '"></label>') +
(PART_FIELDS[p.kind] || []).map(function (f) {
const cur = p[f[0]] === undefined ? PART_KINDS[p.kind].state[f[0]] : p[f[0]];
return '<label class="ckt-f"><span>' + esc2(f[1]) + '</span>' +
'<input data-x="' + f[0] + '" value="' + esc2(String(cur)) + '"></label>';
}).join('') +
(p.kind === 'POT'
? '<div class="ckt-f" style="grid-template-columns:auto 1fr auto">' +
'<span>Wiper</span><input type="range" data-wiper min="0" max="1000" step="1" ' +
'aria-label="Wiper position, 0 to 1" aria-valuetext="' +
(p.wiper === undefined ? 0.5 : p.wiper).toFixed(2) + '" value="' +
Math.round((p.wiper === undefined ? 0.5 : p.wiper) * 1000) +
'" style="height:18px;padding:0;border:0;background:none;accent-color:var(--lime);width:100%">' +
'<span data-wiperval style="color:var(--accent-ink)">' +
(p.wiper === undefined ? 0.5 : p.wiper).toFixed(2) + '</span></div>'
: '') +
'<p class="ckt-hint" data-note>' + modelNote(p) + '</p>' + boardShortNote(p);
const inp = partPanel.querySelector('[data-val]');
function commitValue() {
const want = parseEng(inp.value, p.value);
p.value = clampValue(p.kind, want, p.value);
changed();
const mine = selOne() === p;
if (mine) paintPart();
if (p.value !== want && mine) {
const who = 'A ' + (PART_KINDS[p.kind].name || p.kind).toLowerCase() + ' ';
const ceil = VALUE_CEIL[p.kind];
announce(ceil !== undefined && Math.abs(want) > ceil
? who + 'that large is past what the arithmetic can hold once the solver ' +
'divides it by a time step, so this is now ' + fmtEng(p.value, k.unit) + '.'
: who + 'has to be more than zero, so this is now ' + fmtEng(p.value, k.unit) + '.');
}
}
if (inp) {
inp.addEventListener('input', function () { editSoon(commitValue); });
inp.addEventListener('change', function () { pendingEdit = commitValue; flushEdit(); });
}
partPanel.querySelectorAll('[data-x]').forEach(function (el) {
function commitField() {
const f = (PART_FIELDS[p.kind] || []).filter(function (q) { return q[0] === el.dataset.x; })[0];
if (!f) return;
const v = parseEng(el.value, p[el.dataset.x]);
p[el.dataset.x] = Math.min(Math.max(isFinite(v) ? v : f[2], f[2]), f[3]);
changed();
if (selOne() === p) paintPart();
}
el.addEventListener('input', function () { editSoon(commitField); });
el.addEventListener('change', function () { pendingEdit = commitField; flushEdit(); });
});
const sw = partPanel.querySelector('[data-sw]');
if (sw) sw.addEventListener('click', function () { toggleSwitch(p); });
const wip = partPanel.querySelector('[data-wiper]');
if (wip) wip.addEventListener('input', function () {
p.wiper = Math.min(Math.max(+wip.value / 1000, 0), 1);
partPanel.querySelector('[data-wiperval]').textContent = p.wiper.toFixed(2);
wip.setAttribute('aria-valuetext', p.wiper.toFixed(2));
refreshNote();
retouchSoon();
});
}
function boardShortNote(p) {
const pins = Netlist.pinsOf(p);
if (pins.length < 2) return '';
let where = null;
cur.parts.forEach(function (b) {
if (b.kind !== 'BB' || where) return;
const seen = {};
pins.forEach(function (pt) {
const s = bbStripAt(b, pt[0], pt[1]);
if (s === null) return;
if (seen[s]) where = s; else seen[s] = 1;
});
});
if (!where) return '';
return '<p class="ckt-hint" style="color:var(--amber,#FFC66D)">Both ends of this are ' +
'in one strip of the board, which has therefore shorted it out — a strip is five ' +
'holes and all five are the same node. ' +
(where.indexOf('rail') === 0
? 'That strip is a power rail, and a rail runs the whole length of the board, so ' +
'moving along it will not help: bring one end off the rail.'
: 'Move one end to the next column along, or over the channel into the other half.') +
'</p>';
}
function paintBlock(p) {
const pins = (p.ports || []).length;
const held = ((p.inner && p.inner.parts) || []).length;
partPanel.innerHTML = '<h4>' + esc2(refOf(p)) + '</h4>' +
'<label class="ckt-f"><span>Title</span>' +
'<input data-title value="' + esc2(p.title || '') + '"></label>' +
'<div class="ckt-f" style="grid-template-columns:1fr;align-items:stretch">' +
'<span>Description</span>' +
'<textarea data-desc rows="4" style="width:100%;padding:6px 8px;border-radius:var(--r);' +
'border:1px solid var(--line-2);background:var(--surface-2,transparent);color:inherit;' +
'font:inherit;font-size:12px;line-height:1.5;resize:vertical">' +
esc2(p.desc || '') + '</textarea></div>' +
'<div style="display:flex;gap:6px;margin-bottom:8px">' +
'<button class="ckt-t" data-open style="flex:1">Open</button>' +
'<button class="ckt-t" data-ungroup style="flex:1">Ungroup</button></div>' +
'<p class="ckt-hint">' + held + (held === 1 ? ' part' : ' parts') + ' inside, behind ' +
pins + (pins === 1 ? ' pin' : ' pins') + '. The pins are not a list anyone typed: ' +
'they are the nets that had a connection inside the selection and a connection ' +
'outside it when it was folded up, and they sit on the very cells those crossings ' +
'were on — so grouping and ungrouping leave the circuit solving exactly as it did. ' +
'Nothing about a block reaches the solver; it is flattened back out before a single ' +
'node is numbered.</p>' +
(pins
? '<p class="ckt-hint" style="margin-top:8px">Pins, in the order they are drawn:</p>' +
(p.ports || []).map(function (port, i) {
return '<label class="ckt-f"><span>Pin ' + (i + 1) + '</span>' +
'<input data-port="' + i + '" value="' + esc2(port.name) + '"></label>';
}).join('')
: '<p class="ckt-hint" style="margin-top:8px">No pins at all — nothing outside this ' +
'block is wired to anything inside it, so it is a circuit of its own sitting on ' +
'the same canvas. That is legal, and it is usually a wire you meant to draw.</p>');
const t = partPanel.querySelector('[data-title]');
t.addEventListener('input', function () {
p.title = t.value;
paintCrumbs();
paint();
});
t.addEventListener('change', function () { retouch(); });
const d = partPanel.querySelector('[data-desc]');
d.addEventListener('change', function () { p.desc = d.value; retouch(); });
d.addEventListener('input', function () { p.desc = d.value; });
partPanel.querySelectorAll('[data-port]').forEach(function (el) {
el.addEventListener('input', function () {
p.ports[+el.dataset.port].name = el.value;
paint();
});
el.addEventListener('change', function () { retouch(); });
});
partPanel.querySelector('[data-open]').addEventListener('click', function () { openBlock(p); });
partPanel.querySelector('[data-ungroup]').addEventListener('click', doUngroup);
}
function mcuRigFor(p) {
if (!mcuRun) return null;
const id = prefix() + p.id;
return mcuRun.rigs.filter(function (r) { return r.id === id; })[0] || null;
}
function faultLine(f) {
return '<div class="ckt-err">' + (f.line ? 'Line ' + f.line + ': ' : '') +
esc2(f.message) + '</div>';
}
function paintMcu(p) {
const code = typeof p.code === 'string' ? p.code : MCU_SKETCH;
const gone = !mcuAvailable();
const built = gone ? null : MCU.compile(code);
const rig = mcuRigFor(p);
const st = rig && rig.machine ? rig.machine.state() : null;
const uid = 'mcu' + (++MCU_PANEL_SEQ);
partPanel.innerHTML = '<h4>Microcontroller ' + esc2(refOf(p)) + '</h4>' +
(gone
? '<div class="ckt-err">The interpreter (src/mcu.js) is not in this build, so ' +
'this part can be drawn and wired but not run. Its pins stamp at reset — every ' +
'one an input — which is what a board with power and no program does.</div>'
: '') +
'<div class="ckt-code' + (codeFull ? ' full' : '') + '">' +
'<div class="ckt-code-h"><span id="' + uid + '-lab">Sketch</span>' +
'<button class="ckt-t" data-codefull aria-pressed="' + (codeFull ? 'true' : 'false') +
'" title="' + (codeFull ? 'Back into the panel (Escape)' : 'Write it full size') + '">' +
(codeFull ? 'Shrink' : 'Expand') + '</button></div>' +
'<div class="ckt-ed"><div data-ed></div></div>' +
'<div data-built id="' + uid + '-err" role="status" aria-live="polite">' +
(built && built.error ? faultLine(built.error) : '') + '</div>' +
(st && st.fault ? faultLine(st.fault) : '') +
(st && !st.fault
? '<p class="ckt-hint">' +
(st.done ? 'Finished: there is no loop(), so the sketch ran once and stopped. '
: st.inSetup ? 'Still inside setup() when the run ended. '
: st.loops + (st.loops === 1 ? ' iteration' : ' iterations') + ' of loop(). ') +
st.ops.toLocaleString() + ' instructions, ' + mcuRun.ops() +
' per time step.' + (st.dropped ? ' ' + st.dropped + ' console lines dropped.' : '') +
(st.cut ? ' ' + st.cut.toLocaleString() + ' further characters not kept.' : '') +
'</p>'
: '') +
(rig && rig.error ? faultLine(rig.error) : '') +
mcuConsole(rig, uid) +
'</div>' +
'<p class="ckt-hint" data-note>' + modelNote(p) + '</p>';
const ed = createEditor(partPanel.querySelector('[data-ed]'), {
lang: 'mcu',
onRun: function () { solve(); },
});
ed.setValue(code);
const ta = partPanel.querySelector('.ed-ta');
ta.setAttribute('data-code', '');
ta.removeAttribute('aria-label');
ta.setAttribute('aria-labelledby', uid + '-lab');
ta.setAttribute('id', uid);
ta.setAttribute('aria-describedby', uid + '-err');
ta.setAttribute('aria-invalid', built && built.error ? 'true' : 'false');
const codeBox = partPanel.querySelector('.ckt-code');
partPanel.querySelector('[data-codefull]').addEventListener('click', function () {
codeFull = !codeFull;
paintMcu(p);
syncExpanded();
const nta = partPanel.querySelector('[data-code]');
if (nta) { nta.focus(); nta.setSelectionRange(nta.value.length, nta.value.length); }
announce(codeFull ? 'The sketch fills the screen. Escape puts it back.'
: 'The sketch is back in the panel.');
});
codeBox.addEventListener('keydown', function (e) {
if (e.key !== 'Escape' || !codeFull) return;
e.preventDefault();
e.stopPropagation();
codeFull = false;
paintMcu(p);
syncExpanded();
announce('The sketch is back in the panel.');
});
let checkTimer = null;
function diagnose() {
checkTimer = null;
if (partPanel.querySelector('[data-code]') !== ta) return;
const now = mcuAvailable() ? MCU.compile(ta.value) : null;
const box = partPanel.querySelector('[data-built]');
if (box) box.innerHTML = now && now.error ? faultLine(now.error) : '';
ta.setAttribute('aria-invalid', now && now.error ? 'true' : 'false');
}
ta.addEventListener('input', function () {
p.code = ta.value;
editSoon(function () { changed(); });
if (checkTimer) clearTimeout(checkTimer);
checkTimer = setTimeout(diagnose, 500);
});
ta.addEventListener('change', function () {
p.code = ta.value;
if (checkTimer) { clearTimeout(checkTimer); diagnose(); }
pendingEdit = function () { changed(); };
flushEdit();
});
}
function mcuConsole(rig, uid) {
if (!rig || !rig.machine) return '';
const lines = rig.machine.console();
if (!lines.length) {
return '<p class="ckt-hint">The sketch printed nothing. print("..."), println(x) ' +
'and Serial.println(x) all write here.</p>';
}
return '<h4 style="margin-top:10px" id="' + uid + '-con">Console</h4>' +
'<pre data-console tabindex="0" role="group" aria-labelledby="' + uid + '-con" ' +
'style="max-height:150px;overflow:auto;' +
'margin:0 0 8px;padding:6px 8px;border-radius:var(--r);border:1px solid var(--line-2);' +
'font-family:var(--mono,ui-monospace,monospace);font-size:11px;line-height:1.5;' +
'white-space:pre-wrap">' + esc2(lines.join('\n')) + '</pre>';
}
const VALUE_LABEL = bareTable({
LDR: 'R at 10 lx (Ω)', NTC: 'R at 25 °C (Ω)', POT: 'Total (Ω)',
BB: 'Columns',
LAMP: 'Resistance (Ω)', METER: 'Burden (Ω)', BAR: 'Full scale (V)',
D: 'Is (A)', LED: 'Is (A)', NPN: 'Is (A)', PNP: 'Is (A)',
NMOS: 'k (A/V²)', PMOS: 'k (A/V²)', OPAMP: 'Open-loop gain',
});
const PART_FIELDS = bareTable({
LDR: [['gamma', 'γ slope', 0.05, 3]],
NTC: [['beta', 'B (K)', 1, 20000]],
LAMP: [['pnom', 'Full at (W)', 1e-9, 1e6]],
D: [['n', 'Ideality n', 0.5, 4]],
LED: [['n', 'Ideality n', 0.5, 4], ['inom', 'Full at (A)', 1e-6, 1]],
NPN: [['bf', 'βF forward', 1, 5000], ['br', 'βR reverse', 0.01, 100]],
PNP: [['bf', 'βF forward', 1, 5000], ['br', 'βR reverse', 0.01, 100]],
NMOS: [['vth', 'Vth (V)', 0.05, 20], ['lambda', 'λ (1/V)', 0, 1]],
PMOS: [['vth', 'Vth (V)', 0.05, 20], ['lambda', 'λ (1/V)', 0, 1]],
OPAMP: [['vpos', 'V+ rail (V)', -100, 100], ['vneg', 'V− rail (V)', -100, 100]],
});
function modelNote(p) {
const n = p.id.replace('p', '');
if (p.kind === 'MCU') {
return 'Vcc is ' + fmtEng(MCU_VCC, 'V') + ' and every pin is referenced to this ' +
'part\'s own GND pin, never to the circuit\'s ground — so an output at LOW is ' +
fmtEng(MCU_ROUT, 'Ω') + ' to that pin and not a wire to ground. Wire GND, or the ' +
'whole part floats and the solver says so.<br><br>' +
'An OUTPUT is a source at ' + fmtEng(MCU_VCC, 'V') + ' or 0 V behind ' +
fmtEng(MCU_ROUT, 'Ω') + ', which is what limits the current it can pass: an LED ' +
'straight to ground draws about ' + fmtEng(MCU_VCC / MCU_ROUT, 'A') + ' at most, ' +
'and that is the reason for the resistor, not a rule of thumb.<br><br>' +
'An INPUT is ' + fmtEng(MCU_RIN, 'Ω') + ' to GND and reads through a Schmitt ' +
'trigger: above ' + fmtEng(MCU_VIH, 'V') + ' it reads 1, below ' +
fmtEng(MCU_VIL, 'V') + ' it reads 0, and between the two it reads whatever it read ' +
'last. INPUT_PULLUP adds ' + fmtEng(MCU_RPULL, 'Ω') + ' up to Vcc, which is what ' +
'makes a button to ground work with no other components.<br><br>' +
'analogRead gives ' + MCU_ADC_BITS + ' bits, 0 to ' + MCU_ADC_MAX + ', against Vcc ' +
'as the reference — so one count is ' + fmtEng(MCU_VCC / (MCU_ADC_MAX + 1), 'V') +
' and the reading is a FRACTION of the supply rather than a voltage. There is no ' +
'sampling time, no input capacitance and no conversion delay: the count is taken ' +
'from the solved node voltage at that instant.<br><br>' +
'analogWrite stamps the MEAN of the pulse train, duty/255 of Vcc, and not a ' +
'switching waveform. A filter or an LED responds to that mean and the answer here ' +
'is right; anything that responds within one PWM period — a scope on the pin, a ' +
'motor commutating, a second logic input reading it — is not modelled at all, and ' +
'this would show it a steady voltage that never exists.<br><br>' +
'The Vcc pin supplies ' + fmtEng(MCU_VCC, 'V') + ' through ' +
fmtEng(MCU_RSUP, 'Ω') + '. There is no current limit and no brown-out: load it ' +
'hard enough and it will sag, which is honest, but nothing will reset.<br><br>' +
'On the drawing, a filled pin is one pushing current — an output, a pull-up, or ' +
'a power pin — and a hollow one is only listening. H, L and a percentage are ' +
'where the sketch LEFT that pin when the run ended, not where it sat throughout: ' +
'a blinking pin shows whichever half of the blink the last time step landed in. ' +
'The plot is where the history is.<br><br>' +
'The sketch runs only during a TRANSIENT. In the operating point and the ' +
'frequency sweep every pin is stamped at reset — an input, high impedance — ' +
'because a program is a thing that happens over time and neither of those ' +
'analyses has any.' +
(mcuAvailable()
? '<br><br>It runs at ' + MCU.OPS_PER_SECOND.toLocaleString() + ' operations per ' +
'second of simulated time, suspended between steps so an endless loop() costs ' +
'nothing. An operation is one statement or one operator, which no real ' +
'processor charges alike; the rate is stated rather than realistic. delay() ' +
'and millis() run on the simulation clock, so their resolution is the time ' +
'step. A pin written during one step reaches the matrix at the next.'
: '');
}
if (p.kind === 'SW') {
return 'A state, not a value. Closed stamps ' + fmtEng(SW_ON, 'Ω') + '; open stamps ' +
fmtEng(SW_OFF, 'Ω') + ' rather than deleting the branch, so whatever hangs off the far ' +
'side still has a defined voltage instead of the solver calling the circuit ' +
'under-determined. Click the switch on the canvas to toggle it.';
}
if (p.kind === 'LDR') {
return 'R = R₁₀ · (10 lx / E)^γ — the photoresistor power law, R₁₀ being the resistance ' +
'at the 10 lx a datasheet quotes. More light, less resistance. At E = ' +
fmtEng(env.lux, 'lx') + ' this one is ' + fmtEng(ohmsOf(p, env), 'Ω') +
'. Drag the light slider and watch it move.';
}
if (p.kind === 'NTC') {
return 'R = R₂₅ · exp(B · (1/T − 1/298.15)), T in kelvin — the beta model. B > 0 makes ' +
'the exponent negative as T rises, so resistance FALLS with heat, which is what the N ' +
'in NTC means. It is a two-point fit, worth a few percent over a 50 K span and no more; ' +
'Steinhart–Hart is what you reach for beyond that. At ' + env.tempC.toFixed(1) +
' °C this one is ' + fmtEng(ohmsOf(p, env), 'Ω') + '.';
}
if (p.kind === 'POT') {
const rr = potSplit(p);
return 'Three pins, stamped as two resistances sharing the wiper node: ' +
fmtEng(rr[0], 'Ω') + ' from the first pin to the wiper and ' + fmtEng(rr[1], 'Ω') +
' from the wiper to the second. The wiper is the third pin, leaving the body at ' +
'right angles to the track — ' + pinWords(p)[2] + ' it as drawn.';
}
if (p.kind === 'LAMP') {
const pw = lampPower(p);
return 'An ordinary resistance to the solver. The brightness is drawn from the power in ' +
'it, P = V²/R, against ' + fmtEng(p.pnom === undefined ? 0.25 : p.pnom, 'W') +
' for full brightness' + (pw === null ? '' : '; right now P = ' + fmtEng(pw, 'W')) +
'. Nothing here is non-linear: a real filament\'s resistance climbs as it heats, and ' +
'that is not modelled.';
}
if (p.kind === 'METER') {
const u = acrossOf(p);
return 'An ammeter goes IN SERIES: break the branch and put it in the gap. It reads the ' +
'current through itself as V / ' + fmtEng(p.value, 'Ω') + ', positive from the ' +
pinWords(p)[0] + ' pin to the ' + pinWords(p)[1] +
' — the arrow says which way' + (u === null ? '' : '; now ' + fmtEng(u / Math.max(p.value, 1e-6), 'A')) +
'. The burden resistance is honest rather than ideal: it is what the measurement costs ' +
'the circuit, and it keeps the meter a resistor the linear solver already understands.';
}
if (p.kind === 'BAR') {
const v = dcAt([p.x, p.y]);
return 'Reads the node it sits on, against ground, and takes no part in the solution — ' +
'placing it changes no answer. The bar fills from 0 to the full scale; past that it ' +
'gets a caret rather than a full bar that quietly lies, and a negative voltage reads ' +
'in amber with the bar empty' + (v === null ? '. Solve to give it something to show.' :
', and it is showing ' + fmtEng(v, 'V') + ' now.');
}
if (p.kind === 'BB') {
return 'Not a component: it is connection without wire, and the one part on this ' +
'canvas that carries no current at all. A terminal strip is five holes in a ' +
'column and all five are one node before anything is put in them. The channel ' +
'down the middle is what makes the upper half of a column and the lower half two ' +
'nodes instead of one — which is the gap a DIP is built to straddle, and why ' +
'a part bridging it lands one end in each. The four stripes are rails, and each ' +
'one runs the whole length. A pin joins a strip by sitting on its hole, which is ' +
'the same test that decides whether a pin meets a wire, so there is no second ' +
'rule here to learn. Nothing is stamped: a strip nothing reaches is not a node, ' +
'so a board may lie under a half-built circuit without the solver ever calling ' +
'it under-determined. This one is ' + bbCols(p) + ' columns wide.';
}
if (Devices.is(p.kind)) {
const w = pinWords(p), a = w[0], b = w[1], c = w[2];
const vt = 'Vt = ' + (Devices.VT * 1000).toFixed(2) + ' mV, which is kT/q at ' +
Devices.T_NOM + ' K';
const op = deviceOp(p);
if (p.kind === 'D' || p.kind === 'LED') {
const nn = param(p, 'n', 0.5, 4);
const at = p.kind === 'LED' ? param(p, 'inom', 1e-6, 1) : 1e-3;
return 'Shockley: I = Is·(exp(V / (n·Vt)) − 1), with Is = ' + fmtEng(p.value, 'A') +
', n = ' + nn + ' and ' + vt + '. That puts ' +
fmtEng(Devices.dropAt(Math.max(p.value, 1e-30), nn, at), 'V') + ' across it at ' +
fmtEng(at, 'A') + '. The anode is the ' + a + ' pin — the end the triangle points ' +
'away from. Nothing here is a 0.7 V rule of thumb: the drop you read is the one ' +
'the current makes, found by iterating until the two agree' +
(op === null ? '' : ', and right now that is ' + fmtEng(op.v[0] - op.v[1], 'V') +
' at ' + fmtEng(op.i[0], 'A')) + '. ' +
(p.kind === 'LED'
? 'It lights on the canvas in proportion to the current through it, against ' +
fmtEng(at, 'A') + ' for full brightness. Not modelled: the colour, the light ' +
'itself (that glow is drawn from current, not from photons), junction ' +
'capacitance, and reverse breakdown — which for a real LED is only a few volts, ' +
'so this one will happily survive something the part on your desk would not.'
: 'Not modelled: junction capacitance, so this diode has no switching speed and ' +
'no reverse recovery; the bulk series resistance, so the curve never straightens ' +
'out at high current; reverse breakdown, so it is not a Zener however hard you ' +
'push it backwards; and any temperature but ' + Devices.T_NOM + ' K.');
}
if (p.kind === 'NPN' || p.kind === 'PNP') {
const bf = param(p, 'bf', 1, 5000);
return 'Ebers-Moll, transport form: Ic = Is·(exp(Vbe/Vt) − exp(Vbc/Vt)) − ' +
'(Is/βR)·(exp(Vbc/Vt) − 1), and a base current that is each junction\'s own ' +
'current over its beta. Is = ' + fmtEng(p.value, 'A') + ', βF = ' + bf + ', βR = ' +
param(p, 'br', 0.01, 100) + ', ' + vt + '. Vbe comes out at ' +
fmtEng(Devices.dropAt(Math.max(p.value, 1e-30), 1, 1e-3), 'V') + ' for a milliamp ' +
'of collector current' + (op === null ? '' : '; right now Ic = ' +
fmtEng(Math.abs(op.i[0]), 'A') + ' and Vbe = ' + fmtEng(Math.abs(op.v[2] - op.v[1]), 'V')) +
'. Collector is the ' + a + ' pin, emitter the ' + b + ', base on the pin ' + c +
' — the third pin, where a potentiometer keeps its wiper. ' +
'Ebers-Moll has no Early effect, so collector current does not climb with Vce and ' +
'the output resistance is infinite: a common-emitter stage here has a gain set only ' +
'by its load. Beta is a constant, so it does not fall off at high current or low, and ' +
'there is no base resistance, no junction capacitance and therefore no fT and no ' +
'frequency limit of its own. Gummel-Poon is the model that adds those; this is not it, ' +
'and says so rather than letting you find out.';
}
if (p.kind === 'NMOS' || p.kind === 'PMOS') {
const sign = p.kind === 'NMOS' ? '' : ' — for the P-channel every voltage in it is ' +
'measured the other way round, so Vth is typed as a magnitude and the source sits at ' +
'the positive end';
return 'Level 1, the square law' + sign + ': cut off below Vov = Vgs − Vth, then triode ' +
'while Vds < Vov with Id = k·(Vov·Vds − Vds²/2)·(1 + λ·Vds), then saturation with ' +
'Id = ½·k·Vov²·(1 + λ·Vds). k = ' + fmtEng(p.value, 'A/V²') + ', Vth = ' +
fmtEng(param(p, 'vth', 0.05, 20), 'V') + ', λ = ' + param(p, 'lambda', 0, 1) + ' /V' +
(op === null ? '' : '; right now Id = ' + fmtEng(Math.abs(op.i[0]), 'A')) + '. ' +
'Drain is the ' + a + ' pin, source the ' + b + ', gate on the pin ' + c + '. The gate draws ' +
'no current whatever, which is true of a real one to within picoamps. Drain and source ' +
'are interchangeable and the model swaps them when Vds goes the other way, which is ' +
'what lets this work as a pass gate. ' +
'The body is tied to the source, so there is no body effect and Vth never moves. λ is a ' +
'straight line bolted onto the saturation current, not channel-length modulation: it ' +
'gives roughly the right output resistance and knows nothing about the actual channel. ' +
'Below Vth the current is exactly zero, where a real device is passing nanoamps and a ' +
'low-power design lives or dies by them. And there is no gate capacitance, so no ' +
'switching time, no charge to drive and no dynamic power.';
}
const hi = param(p, 'vpos', -100, 100), lo = param(p, 'vneg', -100, 100);
return 'A controlled source, not an ideal one: Vout = A·(V+ − V−), limited to the rails, ' +
'driven out through ' + fmtEng(Devices.OP_ROUT, 'Ω') + ' of output resistance, with an ' +
'input stage that draws nothing at all. A = ' + fmtEng(p.value, '') + ', rails ' +
fmtEng(lo, 'V') + ' to ' + fmtEng(hi, 'V') + ', so the linear region is the ' +
fmtEng(Math.max(hi - lo, 1e-3) / Math.max(p.value, 10), 'V') + ' either side of zero ' +
'where the gain has not yet run into them. The non-inverting input is the ' + a +
' pin, the output the ' + b + ', the inverting input on the pin ' + c + '. ' +
'The gain is large and finite because an infinite one is a row of zeros in the matrix, ' +
'which is not an answer but a singular matrix; and the limit is a smooth one rather than ' +
'a hard clip because a hard clip has a slope of zero past the corner, and an iteration ' +
'cannot steer on a slope of zero. ' +
'The rails are parameters, not pins: there is nothing here to wire a supply to, and this ' +
'op-amp draws no supply current — which makes it the one part on the canvas whose ' +
'terminal currents do not add up to zero, because the current it delivers comes from a ' +
'supply that is not drawn. Also missing: input offset voltage, bias current, slew rate, ' +
'and any roll-off with frequency at all. The open-loop gain here is ' + fmtEng(p.value, '') +
' at one hertz and ' + fmtEng(p.value, '') + ' at one megahertz, which is the one thing a ' +
'real op-amp is certainly not — so a bandwidth measured on this circuit is the ' +
'bandwidth of the network you built around it, and nothing to do with the part.';
}
if (p.kind === 'V' || p.kind === 'I') {
return 'The + terminal is the ' + pinWords(p)[turnsOf(p) % 2 ? 0 : 1] + ' pin. ' +
'A frequency sweep drives it at this same amplitude, so set it to 1 for a plain transfer function.';
}
return 'Part ' + n + '. Type a value with the usual prefixes — 4k7 is not understood, 4.7k is.';
}
function refreshNote() {
const sel = selOne();
const note = partPanel && partPanel.querySelector('[data-note]');
if (sel && note) note.innerHTML = modelNote(sel);
}
function hostBlock() {
let m = model, b = null;
for (let i = 0; i < path.length; i++) {
b = (m.parts || []).filter(function (q) { return q.id === path[i]; })[0];
if (!b) return null;
m = b.inner || {};
}
return b;
}
function doGroup() {
const sel = selParts();
if (!sel.length) return;
const uf = Netlist.joiner();
cur.parts.forEach(function (p) {
Netlist.pinsOf(p).forEach(function (pt) { uf.find(Netlist.key(pt, '')); });
});
cur.wires.forEach(function (w) { uf.run(w, ''); });
cur.parts.forEach(function (p) {
if (p.kind === 'BB') Netlist.bindBoard(p, uf, '');
});
const tally = {};
function at(pt) {
const r = uf.find(Netlist.key(pt, ''));
return tally[r] || (tally[r] = { in: 0, out: 0, cells: [], seen: {}, gnd: false });
}
cur.parts.forEach(function (p) {
const mine = selIds.has(p.id);
Netlist.pinsOf(p).forEach(function (pt) {
const t = at(pt);
if (p.kind === 'GND') t.gnd = true;
if (!mine) { t.out++; return; }
t.in++;
const kk = pt[0] + ',' + pt[1];
if (!t.seen[kk]) { t.seen[kk] = 1; t.cells.push(pt); }
});
});
const host = hostBlock();
if (host) {
(host.ports || []).forEach(function (port) {
(port.cells || []).forEach(function (c) { at(c).out++; });
});
}
function netOf(pt) { return tally[uf.find(Netlist.key(pt, ''))]; }
function crosses(t) { return !!t && t.in > 0 && t.out > 0; }
function swallowed(t) { return !!t && t.in > 0 && t.out === 0; }
let ox = Infinity, oy = Infinity, x1 = -Infinity, y1 = -Infinity;
sel.forEach(function (p) {
const see = function (a, b) {
if (a < ox) ox = a; if (a > x1) x1 = a;
if (b < oy) oy = b; if (b > y1) y1 = b;
};
Netlist.pinsOf(p).forEach(function (pt) { see(pt[0], pt[1]); });
see(p.x, p.y);
if (bodyOf(p)) see(p.x + bodyW(p), p.y + bodyH(p));
});
if (!isFinite(ox)) return;
const ports = [];
Object.keys(tally).forEach(function (r) {
const t = tally[r];
if (!crosses(t)) return;
t.cells.sort(function (a, b) { return (a[1] - b[1]) || (a[0] - b[0]); });
ports.push(t);
});
ports.sort(function (a, b) {
return (a.cells[0][1] - b.cells[0][1]) || (a.cells[0][0] - b.cells[0][0]);
});
const blk = {
id: 'p' + (seq++), kind: 'IC', x: ox, y: oy, rot: 0, value: 0,
ref: nextRef('IC', cur.parts),
title: 'Block ' + (countBlocks(model) + 1), desc: '',
w: Math.max(1, x1 - ox), h: Math.max(1, y1 - oy),
ports: ports.map(function (t, i) {
return { name: t.gnd ? 'GND' : String(i + 1),
cells: t.cells.map(function (c) { return [c[0] - ox, c[1] - oy]; }) };
}),
inner: {
parts: sel.map(function (p) {
const q = JSON.parse(JSON.stringify(p));
q.x -= ox; q.y -= oy;
return q;
}),
wires: cur.wires.filter(function (w) { return swallowed(netOf(w.a)); })
.map(function (w) {
return { a: [w.a[0] - ox, w.a[1] - oy], b: [w.b[0] - ox, w.b[1] - oy] };
}),
},
};
cur.wires = cur.wires.filter(function (w) { return !swallowed(netOf(w.a)); });
cur.parts = cur.parts.filter(function (p) { return !selIds.has(p.id); });
cur.parts.push(blk);
selIds.clear(); selWires.clear();
selIds.add(blk.id);
changed();
paintPart();
}
function doUngroup() {
const blocks = selParts().filter(function (p) { return p.kind === 'IC'; });
if (!blocks.length) return;
const gone = {};
blocks.forEach(function (b) { gone[b.id] = 1; });
const taken = {};
cur.parts.forEach(function (p) { if (!gone[p.id]) taken[p.id] = 1; });
const back = [];
blocks.forEach(function (b) {
(((b.inner || {}).parts) || []).forEach(function (p) {
const q = JSON.parse(JSON.stringify(p));
q.x += b.x; q.y += b.y;
if (taken[q.id]) q.id = 'p' + (seq++);
taken[q.id] = 1;
back.push(q);
});
cur.wires = cur.wires.concat((((b.inner || {}).wires) || []).map(function (w) {
return { a: [w.a[0] + b.x, w.a[1] + b.y], b: [w.b[0] + b.x, w.b[1] + b.y] };
}));
});
cur.parts = cur.parts.filter(function (p) { return !gone[p.id]; }).concat(back);
selIds.clear(); selWires.clear();
back.forEach(function (p) { selIds.add(p.id); });
changed();
paintPart();
}
function countBlocks(m) {
let n = 0;
(m.parts || []).forEach(function (p) {
if (p.kind !== 'IC') return;
n += 1 + countBlocks(p.inner || {});
});
return n;
}
function openBlock(b) {
if (!b || b.kind !== 'IC') return;
path.push(b.id);
reseat();
afterMove();
}
function closeTo(depth) {
path = path.slice(0, Math.max(0, depth));
reseat();
afterMove();
}
function afterMove() {
selIds.clear(); selWires.clear();
wireFrom = null; wireDown = null; hoverConn = null; marquee = null; drag = null;
paintCrumbs();
paintPart();
zoomFit();
}
function paintCrumbs() {
if (!crumbEl) return;
if (!path.length) { crumbEl.style.display = 'none'; crumbEl.innerHTML = ''; return; }
crumbEl.style.display = '';
const names = ['Circuit'];
let m = model;
path.forEach(function (id) {
const b = (m.parts || []).filter(function (q) { return q.id === id; })[0] || {};
names.push(b.title || 'Block');
m = b.inner || {};
});
crumbEl.innerHTML = '<button class="ckt-t" data-up="' + (path.length - 1) +
'" title="Back out one level (Escape)">↑ Out</button>' +
'<span class="spacer" style="flex:none;width:4px"></span>' +
names.map(function (n, i) {
return (i ? '<span style="color:var(--ink-5);font-size:11px">›</span>' : '') +
(i === names.length - 1
? '<span style="font-family:var(--mono);font-size:11px;color:var(--lime)">' + esc2(n) + '</span>'
: '<button class="ckt-t" data-crumb="' + i + '">' + esc2(n) + '</button>');
}).join('');
crumbEl.querySelectorAll('[data-crumb]').forEach(function (b) {
b.addEventListener('click', function () { closeTo(+b.dataset.crumb); });
});
crumbEl.querySelectorAll('[data-up]').forEach(function (b) {
b.addEventListener('click', function () { closeTo(+b.dataset.up); });
});
}
function retouch() {
if (opts.onChange) opts.onChange(snapshot());
if (result) solve(); else paint();
paintEnv();
}
function perFrame(fn) {
let pending = false;
return function () {
if (pending) return;
pending = true;
const later = function () {
pending = false;
if (disposed) return;
fn();
};
if (typeof requestAnimationFrame === 'function') requestAnimationFrame(later);
else setTimeout(later, 16);
};
}
const retouchSoon = perFrame(function () { retouch(); });
function toggleSwitch(p) {
p.closed = !p.closed;
retouch();
paintPart();
}
function esc2(t) { return String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;'); }
const ENV_Q = [
{ key: 'lux', label: 'Light', unit: 'lx', log: true, min: 0.1, max: 1e5,
note: 'Moonlight is about 0.1 lx, a lit room 200 lx, an overcast day 1 klx, ' +
'direct sun 100 klx.' },
{ key: 'tempC', label: 'Temperature', unit: '°C', log: false, min: -20, max: 120,
note: 'Kelvin is what the beta model wants; this slider is in °C because that is ' +
'what a datasheet and a room both speak.' },
];
function envQ(key) { return ENV_Q.filter(function (q) { return q.key === key; })[0]; }
function envToSlider(q, v) {
const t = q.log ? Math.log(Math.max(v, q.min) / q.min) / Math.log(q.max / q.min)
: (v - q.min) / (q.max - q.min);
return Math.round(Math.min(Math.max(t, 0), 1) * 1000);
}
function envFromSlider(q, t) {
const f = Math.min(Math.max(t / 1000, 0), 1);
return q.log ? q.min * Math.pow(q.max / q.min, f) : q.min + f * (q.max - q.min);
}
function envShow(q) {
return q.log ? fmtEng(env[q.key], q.unit) : env[q.key].toFixed(1) + ' ' + q.unit;
}
function senses(m, q) {
return (m.parts || []).some(function (p) {
const k = PART_KINDS[p.kind];
if (k && k.senses === q.key) return true;
return p.kind === 'IC' && senses(p.inner || {}, q);
});
}
function envInUse() {
return ENV_Q.filter(function (q) { return senses(model, q); });
}
let envSig = null;
function paintEnv() {
if (!envPanel) return;
const qs = envInUse();
const sig = qs.map(function (q) { return q.key; }).join(',');
if (sig === envSig) {
qs.forEach(function (q) {
const el = envPanel.querySelector('[data-envval="' + q.key + '"]');
if (el) el.textContent = envShow(q);
});
return;
}
envSig = sig;
if (!qs.length) { envPanel.hidden = true; envPanel.innerHTML = ''; return; }
envPanel.hidden = false;
envPanel.innerHTML = '<h4>Environment</h4>' + qs.map(function (q) {
return '<div style="margin-bottom:10px">' +
'<div style="display:flex;justify-content:space-between;gap:8px;font-family:var(--mono);' +
'font-size:10.5px;color:var(--ink-4);margin-bottom:4px">' +
'<span>' + esc2(q.label) + '</span>' +
'<span data-envval="' + q.key + '" style="color:var(--lime)">' + esc2(envShow(q)) + '</span></div>' +
'<input type="range" data-env="' + q.key + '" min="0" max="1000" step="1" value="' +
envToSlider(q, env[q.key]) + '" aria-label="' + esc2(q.label) +
'" style="width:100%;height:18px;padding:0;border:0;background:none;accent-color:var(--lime)">' +
'<p class="ckt-hint" style="margin-top:4px">' + esc2(q.note) + '</p>' +
'</div>';
}).join('') +
'<p class="ckt-hint">Simulated, not measured — and not part of the schematic, so a ' +
'saved circuit does not remember where you left these. The solution updates as you drag.</p>';
envPanel.querySelectorAll('[data-env]').forEach(function (el) {
el.addEventListener('input', function () {
const q = envQ(el.dataset.env);
env[q.key] = envFromSlider(q, +el.value);
const out = envPanel.querySelector('[data-envval="' + q.key + '"]');
if (out) out.textContent = envShow(q);
envTouched();
});
});
}
const envTouched = perFrame(function () {
retouch();
paintPart();
});
const AN_RANGE = { f1: [0.01, 1e12, 'Hz'], f2: [1, 1e12, 'Hz'], tstop: [1e-9, 1e6, 's'] };
function anField(el, key, what) {
el.addEventListener('change', function (e) {
const lim = AN_RANGE[key];
const want = parseEng(e.target.value, analysis[key]);
analysis[key] = Math.min(Math.max(isFinite(want) ? want : analysis[key], lim[0]), lim[1]);
e.target.value = fmtEng(analysis[key], lim[2]);
if (analysis[key] !== want) {
announce(what + ' has to be between ' + fmtEng(lim[0], lim[2]) + ' and ' +
fmtEng(lim[1], lim[2]) + ', so it is now ' + fmtEng(analysis[key], lim[2]) + '.');
}
});
}
function paintOpts() {
if (analysis.mode === 'ac') {
optsEl.innerHTML =
'<label class="ckt-f"><span>From</span><input data-f1 value="' + fmtEng(analysis.f1, 'Hz') + '"></label>' +
'<label class="ckt-f"><span>To</span><input data-f2 value="' + fmtEng(analysis.f2, 'Hz') + '"></label>';
anField(optsEl.querySelector('[data-f1]'), 'f1', 'The bottom of the sweep');
anField(optsEl.querySelector('[data-f2]'), 'f2', 'The top of the sweep');
} else if (analysis.mode === 'tran') {
optsEl.innerHTML = '<label class="ckt-f"><span>Stop after</span><input data-ts value="' + fmtEng(analysis.tstop, 's') + '"></label>';
anField(optsEl.querySelector('[data-ts]'), 'tstop', 'The length of the run');
} else {
optsEl.innerHTML = '<p class="ckt-hint">Solves the DC operating point and writes each node voltage onto the schematic.</p>';
}
}
function solve() {
const net = Netlist.build(model, env);
let r;
mcuRun = null;
if (analysis.mode === 'dc') r = MNA.dc(net);
else if (analysis.mode === 'ac') r = MNA.ac(net, analysis.f1, analysis.f2, 220);
else {
mcuRun = mcuRig(net);
r = MNA.tran(net, analysis.tstop, analysis.tstop / 900,
mcuRun && !mcuRun.missing ? mcuRun.hooks : null);
}
if (r.error) {
result = null;
mcuRun = null;
plotWrap.hidden = true;
outEl.innerHTML = '<div class="ckt-err">' + esc2(r.error) + '</div>';
announce('Did not solve. ' + r.error);
paint();
refreshNote();
paintPart();
return;
}
result = Object.assign({ kind: analysis.mode, net: net }, r);
if (analysis.mode === 'dc') {
plotWrap.hidden = true;
const rows = [];
for (let n = 1; n < net.nodeCount; n++) rows.push('<tr><td>node ' + n + '</td><td>' + fmtEng(r.v[n], 'V') + '</td></tr>');
Object.keys(r.currents).forEach(function (id) {
rows.push('<tr><td>' + id.replace('p', 'part ') + '</td><td>' + fmtEng(Math.abs(r.currents[id]), 'A') + '</td></tr>');
});
outEl.innerHTML = '<table class="ckt-tab">' + rows.join('') + '</table>';
announce(net.nodeCount - 1 === 0
? 'Solved. Nothing but ground: no node to report.'
: 'Solved. ' + (net.nodeCount - 1) + (net.nodeCount - 1 === 1 ? ' node, ' : ' nodes, ') +
'node 1 at ' + fmtEng(r.v[1], 'V') + '. The full table is in the analysis result panel.');
} else {
plotWrap.hidden = false;
analysis.node = Math.min(Math.max(analysis.node, 1), Math.max(1, net.nodeCount - 1));
const picks = [];
for (let n = 1; n < net.nodeCount; n++) {
picks.push('<button data-node="' + n + '"' + (n === analysis.node ? ' class="active"' : '') +
' aria-pressed="' + (n === analysis.node ? 'true' : 'false') + '">node ' + n + '</button>');
}
outEl.innerHTML = '<div class="seg ckt-nodes" role="group" aria-label="Which node to plot">' +
picks.join('') + '</div>' + mcuStatus();
outEl.querySelectorAll('[data-node]').forEach(function (b) {
b.addEventListener('click', function () {
analysis.node = +b.dataset.node;
outEl.querySelectorAll('[data-node]').forEach(function (o) {
o.setAttribute('aria-pressed', o === b ? 'true' : 'false');
});
solveRepaint();
announce('Plotting node ' + analysis.node + '.');
});
});
paintPlot();
announce((analysis.mode === 'ac' ? 'Frequency sweep' : 'Transient run') + ' finished over ' +
(net.nodeCount - 1) + (net.nodeCount - 1 === 1 ? ' node' : ' nodes') +
'. The plot is under the canvas; the node buttons choose what it shows.' +
mcuSpoken());
}
paint();
refreshNote();
if (mcuRun) paintPart();
}
function mcuStatus() {
if (!mcuRun) return '';
if (mcuRun.missing) {
return '<p class="ckt-hint">The interpreter (src/mcu.js) is not in this build, so ' +
'the pins stayed at reset for the whole run.</p>';
}
return mcuRun.rigs.map(function (r) {
const who = 'MCU ' + r.id.split('|').pop().replace('p', '');
if (r.error) {
return '<div class="ckt-err">' + esc2(who) + ' did not compile — line ' +
r.error.line + ': ' + esc2(r.error.message) + '</div>';
}
const st = r.machine.state();
if (st.fault) {
return '<div class="ckt-err">' + esc2(who) + ' stopped at line ' + st.fault.line +
': ' + esc2(st.fault.message) + ' The trace ends where it stopped.</div>';
}
return '<p class="ckt-hint">' + esc2(who) + ': ' +
(st.inSetup ? 'still in setup() when the run ended'
: st.done ? 'ran to the end; there is no loop()'
: st.loops + (st.loops === 1 ? ' iteration' : ' iterations') + ' of loop()') +
', ' + st.ops.toLocaleString() + ' instructions.</p>';
}).join('');
}
function mcuSpoken() {
if (!mcuRun) return '';
if (mcuRun.missing) return ' The interpreter is not in this build, so the pins stayed at reset.';
return mcuRun.rigs.map(function (r) {
const who = 'MCU ' + r.id.split('|').pop().replace('p', '');
if (r.error) return ' ' + who + ' did not compile — line ' + r.error.line + ': ' + r.error.message;
const st = r.machine.state();
if (st.fault) {
return ' ' + who + ' stopped at line ' + st.fault.line + ': ' + st.fault.message +
' The trace ends where it stopped.';
}
return '';
}).join('');
}
function solveRepaint() { paintPlot(); outEl.querySelectorAll('[data-node]').forEach(function (b) { b.classList.toggle('active', +b.dataset.node === analysis.node); }); }
function paintPlot() {
if (!result || typeof Sandbox === 'undefined') return;
const box = plotCv.getBoundingClientRect();
const dpr = Math.min(window.devicePixelRatio || 1, 2);
const w = Math.max(320, Math.round(box.width)), h = 190;
plotCv.width = w * dpr; plotCv.height = h * dpr;
plotCv.style.height = h + 'px';
const c = plotCv.getContext('2d');
c.setTransform(dpr, 0, 0, dpr, 0, 0);
const n = Math.min(analysis.node, result.net.nodeCount - 1);
if (result.kind === 'ac') {
const pts = result.sweep.map(function (s) {
return [s.f, 20 * Math.log10(Math.max(Lin.cabs(s.v[n]), 1e-12))];
});
const ys = pts.map(function (p) { return p[1]; });
const f = Sandbox.frame(c, w, h, {
xRange: [analysis.f1, analysis.f2], yRange: [Math.min.apply(null, ys) - 4, Math.max.apply(null, ys) + 4],
logX: true, xTicks: 5, yTicks: 4, margin: { l: 50, r: 14, t: 12, b: 26 },
xLabel: function (x) { return x >= 1e6 ? (x / 1e6) + 'M' : x >= 1e3 ? (x / 1e3) + 'k' : String(Math.round(x)); },
});
f.line(pts, f.P.accent, 2);
f.text('dB at node ' + n, f.x0 + 6, f.y0 + 13, f.P.faint);
f.text('Hz', f.x1 - 6, f.y1 + 18, f.P.faint, 'right');
const top = ys.indexOf(Math.max.apply(null, ys));
describe('Frequency response at node ' + n + ', ' + pts.length + ' points from ' +
fmtEng(pts[0][0], 'Hz') + ' to ' + fmtEng(pts[pts.length - 1][0], 'Hz') + '. ' +
ys[0].toFixed(1) + ' dB at the bottom, ' + ys[ys.length - 1].toFixed(1) +
' dB at the top, highest ' + ys[top].toFixed(1) + ' dB at ' + fmtEng(pts[top][0], 'Hz') + '.');
} else {
const pts = result.t.map(function (t, i) { return [t, result.v[i][n]]; });
const ys = pts.map(function (p) { return p[1]; });
const lo = Math.min.apply(null, ys), hi = Math.max.apply(null, ys);
const pad = Math.max((hi - lo) * 0.12, 1e-6);
const f = Sandbox.frame(c, w, h, {
xRange: [0, result.t[result.t.length - 1]], yRange: [lo - pad, hi + pad],
xTicks: 5, yTicks: 4, margin: { l: 50, r: 14, t: 12, b: 26 },
xLabel: function (x) { return fmtEng(x, ''); },
});
f.line(pts, f.P.accent, 2);
f.text('V at node ' + n, f.x0 + 6, f.y0 + 13, f.P.faint);
f.text('seconds', f.x1 - 6, f.y1 + 18, f.P.faint, 'right');
describe('Transient at node ' + n + ', ' + pts.length + ' samples over ' +
fmtEng(pts[pts.length - 1][0], 's') + '. Starts at ' + fmtEng(ys[0], 'V') +
', ends at ' + fmtEng(ys[ys.length - 1], 'V') + ', between ' + fmtEng(lo, 'V') +
' and ' + fmtEng(hi, 'V') + '.');
}
}
function describe(text) { if (plotCv) plotCv.setAttribute('aria-label', text); }
let pendingEdit = null, editTimer = null;
function editSoon(fn) {
pendingEdit = fn;
if (editTimer) clearTimeout(editTimer);
editTimer = setTimeout(flushEdit, 600);
}
function flushEdit() {
if (editTimer) { clearTimeout(editTimer); editTimer = null; }
const fn = pendingEdit;
pendingEdit = null;
if (fn) fn();
}
function changed() {
if (disposed) return;
result = null;
mcuRun = null;
plotWrap.hidden = true;
reseat();
paintCrumbs();
if (opts.onChange) opts.onChange(snapshot());
paintEnv();
paint();
}
if (ro_) {
let dro = null;
if (typeof ResizeObserver !== 'undefined') {
dro = new ResizeObserver(function () { paintSoon(); });
dro.observe(cv.parentElement);
}
paint();
return {
getModel: function () { return snapshot(); },
solve: function () { return null; },
dispose: function () {
if (disposed) return;
disposed = true;
if (dro) dro.disconnect();
root.innerHTML = '';
},
};
}
const DRAG_SLOP = 4;
let down = null;
cv.addEventListener('pointermove', function (e) {
const sp = evPt(e);
const wasTip = tipBlock();
hover = toGrid(sp[0], sp[1]);
hoverSp = sp;
if (panFrom) {
view.px = panFrom.px + (panFrom.sx - sp[0]) / view.s;
view.py = panFrom.py + (panFrom.sy - sp[1]) / view.s;
paintSoon();
return;
}
if (wireDown && !wireDown.started &&
Math.hypot(sp[0] - wireDown.sx, sp[1] - wireDown.sy) > DRAG_SLOP) {
wireDown.started = true;
announce(startWire(wireDown.pt));
}
if (wireDown) { paintSoon(); return; }
if (down && !drag && !marquee && down.mode === 'maybe-move' &&
Math.hypot(sp[0] - down.sx, sp[1] - down.sy) > DRAG_SLOP) {
drag = { from: down.grid, moved: false };
}
if (down && !drag && !marquee && down.mode === 'maybe-marquee' &&
Math.hypot(sp[0] - down.sx, sp[1] - down.sy) > DRAG_SLOP) {
marquee = { a: toWorld(down.sx, down.sy), b: toWorld(sp[0], sp[1]) };
}
if (drag) {
const dx = hover[0] - drag.from[0], dy = hover[1] - drag.from[1];
if (dx || dy) {
moveBy(dx, dy);
drag.from = hover;
drag.moved = true;
paintSoon();
}
return;
}
if (marquee) { marquee.b = toWorld(sp[0], sp[1]); paintSoon(); return; }
const wasConn = hoverConn;
const con = (down || wireFrom || wireDown) ? null : connAt(hover);
hoverConn = (con && con.part && Netlist.pinsOf(con.part).length <= 1) ? null : con;
const conKey = hoverConn ? hoverConn.kind + wireKey({ a: hoverConn.pt, b: hoverConn.pt }) : '';
const wasKey = wasConn ? wasConn.kind + wireKey({ a: wasConn.pt, b: wasConn.pt }) : '';
if (conKey !== wasKey) { cv.style.cursor = hoverConn ? 'crosshair' : ''; paintSoon(); return; }
const isTip = tipBlock();
if (isTip || wasTip) { paintSoon(); return; }
if (wireFrom) paintSoon();
});
cv.addEventListener('pointerleave', function () {
const had = tipBlock() || hoverConn;
hover = null; hoverSp = null; hoverConn = null;
cv.style.cursor = '';
if (wireFrom || had) paint();
});
cv.addEventListener('contextmenu', function (e) {
if (!wireFrom) return;
e.preventDefault();
announce(cancelWire());
});
cv.addEventListener('wheel', function (e) {
if (e.ctrlKey) return;
e.preventDefault();
const sp = evPt(e);
zoomTo(view.s * (e.deltaY < 0 ? 1.12 : 1 / 1.12), sp[0], sp[1]);
}, { passive: false });
function wireAt(pt) {
if (!wireFrom) { wireFrom = pt; paint(); return 'Wire started at ' + cellName(pt) + '.'; }
const end = Math.abs(pt[0] - wireFrom[0]) > Math.abs(pt[1] - wireFrom[1])
? [pt[0], wireFrom[1]] : [wireFrom[0], pt[1]];
let msg = 'Wire cancelled.';
if (end[0] !== wireFrom[0] || end[1] !== wireFrom[1]) {
cur.wires.push({ a: wireFrom, b: end });
msg = 'Wire drawn from ' + cellName(wireFrom) + ' to ' + cellName(end) + '.';
changed();
}
wireFrom = null;
paint();
return msg;
}
function wireKey(w) { return w.a[0] + ',' + w.a[1] + ':' + w.b[0] + ',' + w.b[1]; }
function onWire(w, g) {
const dx = w.b[0] - w.a[0], dy = w.b[1] - w.a[1];
if (dx && dy) return false;
if (dx) {
return g[1] === w.a[1] &&
g[0] >= Math.min(w.a[0], w.b[0]) && g[0] <= Math.max(w.a[0], w.b[0]);
}
if (dy) {
return g[0] === w.a[0] &&
g[1] >= Math.min(w.a[1], w.b[1]) && g[1] <= Math.max(w.a[1], w.b[1]);
}
return g[0] === w.a[0] && g[1] === w.a[1];
}
function wireAtPt(g) {
for (let i = cur.wires.length - 1; i >= 0; i--) {
if (onWire(cur.wires[i], g)) return cur.wires[i];
}
return null;
}
function connAt(g) {
if (!g) return null;
for (let i = cur.parts.length - 1; i >= 0; i--) {
const p = cur.parts[i];
const ps = Netlist.pinsOf(p);
for (let j = 0; j < ps.length; j++) {
if (ps[j][0] === g[0] && ps[j][1] === g[1]) {
return { pt: [ps[j][0], ps[j][1]], part: p, pin: j, kind: 'pin' };
}
}
}
const w = wireAtPt(g);
if (w) return { pt: [g[0], g[1]], wire: w, kind: 'wire' };
return null;
}
function elbow(a, b) {
if (a[0] === b[0] && a[1] === b[1]) return [];
if (a[0] === b[0] || a[1] === b[1]) return [[a, b]];
const c = Math.abs(b[0] - a[0]) >= Math.abs(b[1] - a[1])
? [b[0], a[1]] : [a[0], b[1]];
return [[a, c], [c, b]];
}
function splitWiresAt(pt) {
for (let i = cur.wires.length - 1; i >= 0; i--) {
const w = cur.wires[i];
if (!onWire(w, pt)) continue;
if ((pt[0] === w.a[0] && pt[1] === w.a[1]) ||
(pt[0] === w.b[0] && pt[1] === w.b[1])) continue;
selWires.delete(wireKey(w));
cur.wires.splice(i, 1,
{ a: w.a, b: [pt[0], pt[1]] },
{ a: [pt[0], pt[1]], b: w.b });
}
}
function startWire(pt) {
wireFrom = [pt[0], pt[1]];
paint();
return 'Wire started at ' + cellName(wireFrom) + '. Click to finish, Escape to cancel.';
}
function cancelWire() {
if (!wireFrom) return null;
wireFrom = null; wireDown = null;
paint();
return 'Wire cancelled.';
}
function commitWire(pt) {
const from = wireFrom;
wireFrom = null; wireDown = null;
if (!from) return null;
const segs = elbow(from, pt);
if (!segs.length) { paint(); return 'Wire cancelled — it would end where it began.'; }
segs.forEach(function (seg) {
splitWiresAt(seg[0]);
splitWiresAt(seg[1]);
cur.wires.push({ a: seg[0], b: seg[1] });
});
changed();
paint();
const end = connAt(pt);
return 'Wire from ' + cellName(from) + ' to ' +
(end && end.part ? partName(end.part) : cellName(pt)) + '.';
}
function selectAt(pt, shift) {
const hit = partAt(pt);
if (hit) {
if (shift) {
if (selIds.has(hit.id)) selIds.delete(hit.id); else selIds.add(hit.id);
} else if (!selIds.has(hit.id)) {
selIds.clear();
selWires.clear();
selIds.add(hit.id);
}
if (!shift) selWires.clear();
return hit;
}
const w = wireAtPt(pt);
if (w) {
const k = wireKey(w);
if (shift) {
if (selWires.has(k)) selWires.delete(k); else selWires.add(k);
} else if (!selWires.has(k)) {
selIds.clear(); selWires.clear(); selWires.add(k);
}
return null;
}
if (!shift) { selIds.clear(); selWires.clear(); }
return hit;
}
function placeAt(pt) {
const existing = cellPartAt(pt) || (bodyOf({ kind: tool }) ? bodyAt(pt) : undefined);
if (existing) {
selIds.clear(); selWires.clear(); selIds.add(existing.id); paintPart(); paint();
return partName(existing) + ' is already at ' + cellName(pt) + '; selected it instead.';
}
const kind = tool;
const p = { id: 'p' + (seq++), kind: kind, x: pt[0], y: pt[1], rot: 0,
ref: nextRef(kind, cur.parts),
value: PART_KINDS[kind].def };
const st = PART_KINDS[kind].state;
if (st) Object.keys(st).forEach(function (key2) { p[key2] = st[key2]; });
cur.parts.push(p);
selIds.clear(); selWires.clear();
selIds.add(p.id);
changed();
paintPart();
return 'Placed ' + partName(p) + ' at ' + cellName(pt) + '.';
}
function cellName(pt) { return 'column ' + (pt[0] - originX + 1) + ', row ' + (pt[1] - originY + 1); }
function partName(p) {
const k = PART_KINDS[p.kind];
return (k ? k.name : p.kind) + ' ' + refOf(p);
}
cv.addEventListener('pointerdown', function (e) {
const sp = evPt(e);
const pt = toGrid(sp[0], sp[1]);
focusCanvas();
caret = pt;
caretByKey = false;
if (e.button === 1 || spaceDown) {
panFrom = { sx: sp[0], sy: sp[1], px: view.px, py: view.py };
cv.setPointerCapture(e.pointerId);
e.preventDefault();
return;
}
if (e.button !== 0) return;
if (wireFrom) { announce(commitWire(pt)); return; }
if (hoverConn && (tool === 'select' || tool === 'wire')) {
cv.setPointerCapture(e.pointerId);
wireDown = { sx: sp[0], sy: sp[1], pt: hoverConn.pt, kind: hoverConn.kind,
part: hoverConn.part || null, started: false, shift: e.shiftKey };
hoverConn = null;
paint();
return;
}
if (tool === 'wire') { announce(wireAt(pt)); return; }
if (tool === 'select') {
cv.setPointerCapture(e.pointerId);
const hit = selectAt(pt, e.shiftKey);
down = hit
? { sx: sp[0], sy: sp[1], grid: pt, mode: 'maybe-move', hit: hit.id, shift: e.shiftKey }
: { sx: sp[0], sy: sp[1], grid: pt, mode: 'maybe-marquee', shift: e.shiftKey };
paintPart();
paint();
return;
}
announce(placeAt(pt));
});
function endPointer(e) {
if (panFrom) { panFrom = null; return; }
if (wireDown) {
const w = wireDown;
wireDown = null;
if (e && e.type === 'pointercancel') { announce(cancelWire()); return; }
if (w.started) {
const sp2 = e && e.clientX !== undefined ? evPt(e) : null;
announce(commitWire(sp2 ? toGrid(sp2[0], sp2[1]) : w.pt));
return;
}
if (partAt(w.pt)) {
const hit = selectAt(w.pt, w.shift);
if (hit && hit.kind === 'SW' && !w.shift) toggleSwitch(hit);
paintPart(); paint();
announce(hit ? 'Selected ' + partName(hit) + '.' : selectedSaid());
return;
}
if (w.kind === 'wire') {
selectAt(w.pt, w.shift);
paintPart(); paint();
announce(selectedSaid());
return;
}
announce(startWire(w.pt));
return;
}
if (marquee) {
const x0 = Math.min(marquee.a[0], marquee.b[0]), x1 = Math.max(marquee.a[0], marquee.b[0]);
const y0 = Math.min(marquee.a[1], marquee.b[1]), y1 = Math.max(marquee.a[1], marquee.b[1]);
cur.parts.forEach(function (p) {
const wx = gx(p.x), wy = gy(p.y);
const wx2 = bodyOf(p) ? gx(p.x + bodyW(p)) : wx;
const wy2 = bodyOf(p) ? gy(p.y + bodyH(p)) : wy;
if (wx >= x0 && wx2 <= x1 && wy >= y0 && wy2 <= y1) selIds.add(p.id);
});
if (!(down && down.shift)) {
cur.wires.forEach(function (w) {
const ax = gx(w.a[0]), ay = gy(w.a[1]), bx = gx(w.b[0]), by = gy(w.b[1]);
if (Math.min(ax, bx) >= x0 && Math.max(ax, bx) <= x1 &&
Math.min(ay, by) >= y0 && Math.max(ay, by) <= y1) selWires.add(wireKey(w));
});
}
marquee = null;
paintPart();
paint();
}
if (!drag && down && down.mode === 'maybe-move' && down.hit &&
!down.shift && !(e && e.type === 'pointercancel')) {
const hp = cur.parts.filter(function (p) { return p.id === down.hit; })[0];
if (hp && hp.kind === 'SW') toggleSwitch(hp);
}
if (drag) {
if (drag.moved) changed();
drag = null;
}
down = null;
}
cv.addEventListener('pointerup', endPointer);
cv.addEventListener('pointercancel', endPointer);
cv.addEventListener('dblclick', function (e) {
const sp = evPt(e);
const hit = partAt(toGrid(sp[0], sp[1]));
if (hit && hit.kind === 'IC') { e.preventDefault(); openBlock(hit); }
});
let spaceDown = false;
function focusCanvas() {
try { cv.focus({ preventScroll: true }); } catch (e2) { try { cv.focus(); } catch (e3) {} }
}
function caretHome() {
const one = selParts()[0];
if (one) return [one.x, one.y];
const box = cv.parentElement.getBoundingClientRect();
return toGrid(Math.max(320, box.width) / 2, Math.max(260, box.height) / 2);
}
function revealCaret() {
if (!caret) return;
const box = cv.parentElement.getBoundingClientRect();
const w = Math.max(320, box.width), h = Math.max(260, box.height);
const sx = (gx(caret[0]) - view.px) * view.s, sy = (gy(caret[1]) - view.py) * view.s;
const m = GRID * view.s;
if (sx < m) view.px -= (m - sx) / view.s;
if (sx > w - m) view.px += (sx - (w - m)) / view.s;
if (sy < m) view.py -= (m - sy) / view.s;
if (sy > h - m) view.py += (sy - (h - m)) / view.s;
}
const ARROWS = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
function onKey(e) {
if (e.target && /input|textarea|select/i.test(e.target.tagName)) return;
if (e.target && e.target.isContentEditable) return;
const step = ARROWS[e.key];
if (step) {
e.preventDefault();
caretByKey = true;
if (!caret) { caret = caretHome(); revealCaret(); paint(); announce('Caret at ' + cellName(caret) + '.'); return; }
if (e.shiftKey) {
if (!selIds.size) { announce('Nothing is selected, so there is nothing to move.'); return; }
moveBy(step[0], step[1]);
caret = [caret[0] + step[0], caret[1] + step[1]];
changed();
revealCaret();
paint();
announce('Moved the selection to ' + cellName(caret) + '.');
return;
}
caret = [caret[0] + step[0], caret[1] + step[1]];
revealCaret();
paint();
const under = partAt(caret);
announce(cellName(caret) + (under ? ', ' + partName(under) + '.' : '.'));
return;
}
if (e.key === 'Enter' || e.key === ' ' || e.key === 'Spacebar' || e.code === 'Space') {
e.preventDefault();
if (e.key !== 'Enter' && hoverSp) {
if (!spaceDown) { spaceDown = true; cv.style.cursor = 'grab'; }
return;
}
caretByKey = true;
if (!caret) { caret = caretHome(); revealCaret(); paint(); announce('Caret at ' + cellName(caret) + '.'); return; }
if (tool === 'wire') { announce(wireAt(caret)); return; }
if (tool === 'select') {
const already = selIds.size === 1 && partAt(caret) && selIds.has(partAt(caret).id);
const hit = selectAt(caret, e.shiftKey);
paintPart(); paint();
if (hit && hit.kind === 'SW' && !e.shiftKey) {
toggleSwitch(hit); paintPart();
announce(partName(hit) + ' is now ' + (hit.closed ? 'closed' : 'open') + '.');
} else if (hit && hit.kind === 'IC' && !e.shiftKey && already) {
openBlock(hit);
announce('Opened ' + partName(hit) + '. Escape closes it again.');
} else {
announce(hit ? 'Selected ' + partName(hit) + '.' : 'Selection cleared.');
}
return;
}
announce(placeAt(caret));
return;
}
if (e.key === 'Delete' || e.key === 'Backspace') {
const nP = selIds.size, nW = selWires.size;
doDelete();
e.preventDefault();
announce(deleteSaid(nP, nW));
}
else if (e.key === 'f' || e.key === 'F') { announce(toggleFull()); e.preventDefault(); }
else if (e.shiftKey && e.key === 'R') { doRotate(); announce(rotationSaid()); }
else if (e.shiftKey && e.key === 'G') { doGroup(); announce(blockSaid('Grouped')); }
else if (e.shiftKey && e.key === 'U') { doUngroup(); announce(blockSaid('Ungrouped')); }
else if (!e.ctrlKey && !e.metaKey && !e.altKey && e.key.length === 1 &&
PART_KEYS[(e.shiftKey ? 'shift+' : '') + e.key.toLowerCase()]) {
const picked = PART_KEYS[(e.shiftKey ? 'shift+' : '') + e.key.toLowerCase()];
wireFrom = null; wireDown = null;
setTool(picked);
e.preventDefault();
announce(toolSaid(picked));
}
else if (e.key === 'Escape') {
if (wireFrom || marquee || selIds.size || selWires.size) {
wireFrom = null; wireDown = null; marquee = null;
selIds.clear(); selWires.clear();
paintPart(); paint();
announce('Let go.');
} else if (path.length) { closeTo(path.length - 1); announce('Closed the block.'); }
else if (isFull()) { setFull(false); announce('Back in the page.'); }
}
else if ((e.ctrlKey || e.metaKey) && (e.key === 'a' || e.key === 'A')) {
selIds.clear(); selWires.clear();
cur.parts.forEach(function (p) { selIds.add(p.id); });
cur.wires.forEach(function (w) { selWires.add(wireKey(w)); });
paintPart(); paint(); e.preventDefault();
announce(selectedSaid());
}
else if (e.key === '+' || e.key === '=') { zoomTo(view.s * 1.2); announce(zoomSaid()); }
else if (e.key === '-' || e.key === '_') { zoomTo(view.s / 1.2); announce(zoomSaid()); }
else if (e.key === '0') { zoomFit(); announce(fitSaid()); }
}
function zoomSaid() { return 'Zoom ' + Math.round(view.s * 100) + ' per cent.'; }
function fitSaid() {
if (!cur.parts.length && !cur.wires.length) return 'Nothing to fit. Zoom back to 100 per cent.';
if (fitShort) {
return 'Fitted as far as the zoom goes, ' + Math.round(view.s * 100) +
' per cent. The drawing is wider than the window can show at that zoom, so this ' +
'is the middle of it.';
}
return 'Fitted the drawing to the window. Zoom ' + Math.round(view.s * 100) + ' per cent.';
}
function rotationSaid() {
const ps = selParts().filter(function (p) { const k = PART_KINDS[p.kind]; return !k || k.pins > 1; });
if (!ps.length) return 'Nothing here can be turned.';
return 'Rotated ' + ps.length + (ps.length === 1 ? ' part to ' : ' parts to ') +
(turnsOf(ps[0]) * 90) + ' degrees.';
}
function blockSaid(verb) { return verb + '. ' + cur.parts.length + ' parts on this drawing.'; }
function releaseSpace() {
if (!spaceDown) return;
spaceDown = false;
cv.style.cursor = '';
}
function onSpaceUp(e) { if (e.code === 'Space' || e.key === ' ') releaseSpace(); }
function onWinBlur() { releaseSpace(); flushEdit(); }
function onCanvasFocus() { cvFocused = true; paint(); }
function onCanvasBlur() { cvFocused = false; releaseSpace(); paint(); }
cv.addEventListener('keydown', onKey);
cv.addEventListener('keyup', onSpaceUp);
cv.addEventListener('focus', onCanvasFocus);
cv.addEventListener('blur', onCanvasBlur);
window.addEventListener('blur', onWinBlur);
window.addEventListener('pagehide', flushEdit);
function doRotate() {
const ps = selParts().filter(function (p) {
const k = PART_KINDS[p.kind];
return !k || k.pins > 1;
});
if (!ps.length) return;
ps.forEach(function (p) { p.rot = (turnsOf(p) + 1) % 4; });
changed();
paintPart();
}
function doDelete() {
if (!selIds.size && !selWires.size) return;
cur.parts = cur.parts.filter(function (p) { return !selIds.has(p.id); });
cur.wires = cur.wires.filter(function (w) { return !selWires.has(wireKey(w)); });
selIds.clear();
selWires.clear();
changed();
paintPart();
}
function selectedSaid() {
const bits = [];
if (selIds.size) bits.push(selIds.size + (selIds.size === 1 ? ' part' : ' parts'));
if (selWires.size) bits.push(selWires.size + (selWires.size === 1 ? ' wire' : ' wires'));
return bits.length ? 'Selected ' + bits.join(' and ') + '.' : 'Nothing to select.';
}
function deleteSaid(nP, nW) {
if (!nP && !nW) return 'Nothing is selected.';
const bits = [];
if (nP) bits.push(nP + (nP === 1 ? ' part' : ' parts'));
if (nW) bits.push(nW + (nW === 1 ? ' wire' : ' wires'));
return 'Deleted ' + bits.join(' and ') + '.';
}
const cats = Array.prototype.slice.call(root.querySelectorAll('.ckt-cat'));
function closeCats() { cats.forEach(function (d) { d.open = false; }); }
cats.forEach(function (d) {
d.addEventListener('toggle', function () {
if (!d.open) return;
cats.forEach(function (o) { if (o !== d) o.open = false; });
requestAnimationFrame(paintIcons);
});
});
root.addEventListener('pointerdown', function (e) {
if (!cats.some(function (d) { return d.open; })) return;
if (e.target && e.target.closest && e.target.closest('.ckt-cat')) return;
closeCats();
}, true);
const icons = Array.prototype.slice.call(root.querySelectorAll('.ckt-ico'));
function paintIcons() {
const ink = getComputedStyle(document.documentElement)
.getPropertyValue('--ink').trim() || P().ink;
icons.forEach(function (c) { Symbols.paint(c, c.dataset.sym, ink); });
}
paintIcons();
requestAnimationFrame(paintIcons);
root.__cktIcons = paintIcons;
function paintTools() {
root.querySelectorAll('[data-tool]').forEach(function (o) {
const on = o.dataset.tool === tool;
o.classList.toggle('on', on);
o.setAttribute('aria-pressed', on ? 'true' : 'false');
});
cats.forEach(function (d) {
d.classList.toggle('holds', !!d.querySelector('[data-tool].on'));
});
}
function toolSaid(kind) {
const b = root.querySelector('[data-tool="' + kind + '"]');
const name = b ? b.getAttribute('aria-label') : kind;
if (kind === 'select') return 'Select. Click a part or a wire; drag from a terminal to wire.';
if (kind === 'wire') return 'Wire. Click a cell, then another.';
return name + ' chosen. Click the canvas, or press Enter, to place one.';
}
function setTool(kind) {
tool = kind;
closeCats();
paintTools();
paintPart();
paint();
}
root.querySelectorAll('[data-tool]').forEach(function (b) {
b.addEventListener('click', function () {
wireFrom = null; wireDown = null;
setTool(b.dataset.tool);
announce(toolSaid(b.dataset.tool));
});
});
const shell = root.querySelector('.ckt');
const fullBtn = root.querySelector('[data-act="full"]');
function isFull() { return shell.classList.contains('full'); }
function syncExpanded() {
document.body.classList.toggle('ckt-expanded',
!!document.querySelector('.ckt.full, .ckt-code.full'));
}
function setFull(on) {
shell.classList.toggle('full', !!on);
syncExpanded();
fullBtn.setAttribute('aria-pressed', on ? 'true' : 'false');
fullBtn.textContent = on ? 'Shrink' : 'Expand';
fullBtn.title = on ? 'Back into the page (F, or Escape)' : 'Fill the screen (F)';
if (on && shell.requestFullscreen) {
shell.requestFullscreen().catch(function () {});
} else if (!on && document.fullscreenElement === shell && document.exitFullscreen) {
document.exitFullscreen().catch(function () {});
}
if (on && (cur.parts.length || cur.wires.length)) zoomFit();
paintSoon();
}
function toggleFull() {
setFull(!isFull());
return isFull() ? 'Filling the screen. F or Escape puts it back.'
: 'Back in the page.';
}
fullBtn.addEventListener('click', function () { announce(toggleFull()); });
function onFsChange() {
if (document.fullscreenElement !== shell && isFull()) setFull(false);
}
document.addEventListener('fullscreenchange', onFsChange);
root.querySelector('[data-act="zoomin"]').addEventListener('click', function () { zoomTo(view.s * 1.2); });
root.querySelector('[data-act="zoomout"]').addEventListener('click', function () { zoomTo(view.s / 1.2); });
root.querySelector('[data-act="fit"]').addEventListener('click', function () {
zoomFit(); announce(fitSaid());
});
root.querySelector('[data-act="group"]').addEventListener('click', doGroup);
root.querySelector('[data-act="ungroup"]').addEventListener('click', doUngroup);
root.querySelector('[data-act="rotate"]').addEventListener('click', doRotate);
root.querySelector('[data-act="delete"]').addEventListener('click', doDelete);
root.querySelector('[data-act="clear"]').addEventListener('click', function () {
cur.parts = []; cur.wires = []; selIds.clear(); selWires.clear();
wireFrom = null; wireDown = null; hoverConn = null;
view = { s: 1, px: 0, py: 0 };
changed(); paintPart();
announce('Cleared the drawing.');
});
root.querySelectorAll('[data-an]').forEach(function (b) {
b.addEventListener('click', function () {
analysis.mode = b.dataset.an;
root.querySelectorAll('[data-an]').forEach(function (o) {
o.classList.toggle('active', o === b);
o.setAttribute('aria-pressed', o === b ? 'true' : 'false');
});
paintOpts();
});
});
root.querySelector('.ckt-run').addEventListener('click', solve);
root.querySelector('[data-act="fit"]').setAttribute('aria-keyshortcuts', '0');
root.querySelector('[data-act="rotate"]').setAttribute('aria-keyshortcuts', 'Shift+R');
root.querySelector('[data-act="delete"]').setAttribute('aria-keyshortcuts', 'Delete');
root.querySelector('[data-act="group"]').setAttribute('aria-keyshortcuts', 'Shift+G');
root.querySelector('[data-act="ungroup"]').setAttribute('aria-keyshortcuts', 'Shift+U');
let ro = null;
if (typeof ResizeObserver !== 'undefined') {
ro = new ResizeObserver(function () { paintSoon(); if (result && !plotWrap.hidden) paintPlot(); });
ro.observe(cv.parentElement);
}
paintTools();
paintCrumbs();
paintPart();
paintEnv();
paintOpts();
paint();
return {
getModel: function () { return snapshot(); },
solve: solve,
dispose: function () {
if (disposed) return;
flushEdit();
disposed = true;
window.removeEventListener('blur', onWinBlur);
window.removeEventListener('pagehide', flushEdit);
document.removeEventListener('fullscreenchange', onFsChange);
if (document.fullscreenElement === shell && document.exitFullscreen) {
document.exitFullscreen().catch(function () {});
}
if (ro) ro.disconnect();
codeFull = false;
root.innerHTML = '';
syncExpanded();
},
};
}
const CIRCUIT_EXAMPLE = {
parts: [
{ id: 'p0', kind: 'V', x: 3, y: 6, rot: 1, value: 5, ac: 1 },
{ id: 'p1', kind: 'R', x: 6, y: 4, rot: 0, value: 1000 },
{ id: 'p2', kind: 'C', x: 9, y: 6, rot: 1, value: 1e-7 },
{ id: 'p3', kind: 'GND', x: 3, y: 9 },
{ id: 'p4', kind: 'GND', x: 9, y: 9 },
],
wires: [
{ a: [3, 5], b: [3, 4] },
{ a: [3, 4], b: [5, 4] },
{ a: [7, 4], b: [9, 4] },
{ a: [9, 4], b: [9, 5] },
{ a: [3, 7], b: [3, 9] },
{ a: [9, 7], b: [9, 9] },
],
};
function circuitContext(model, env) {
const net = Netlist.build(model, env || (model && model.env) || null);
const cache = {};
function need(what) {
if (net.tooDeep) {
throw new Error('Blocks are nested more than ' + net.tooDeep + ' deep, so part of ' +
'the circuit is not in the netlist and ' + what + ' would be about a different one.');
}
if (!net.hasGround) throw new Error('Add a ground before ' + what + ' can mean anything.');
}
function allParts(m, at, out) {
(((m && m.parts) || [])).forEach(function (p) {
out.push({ p: p, id: at + p.id });
if (p.kind === 'IC') allParts(p.inner, at + p.id + '|', out);
});
return out;
}
function out() {
if (!net.probes.length) throw new Error('Place a probe on the node you are treating as the output.');
if (net.probes.length > 1) throw new Error('There is more than one probe; the checks read a single output.');
return net.probes[0];
}
return {
net: net,
count: function (kind) { return net.placed.filter(function (p) { return p.kind === kind; }).length; },
values: function (kind) { return net.placed.filter(function (p) { return p.kind === kind; }).map(function (p) { return p.value; }); },
ohms: function (id) {
const r = net.readouts.filter(function (x) { return x.id === id; })[0] ||
net.readouts.filter(function (x) { return x.id.split('|').pop() === id; })[0];
return r ? r.ohms : null;
},
env: net.env,
outNode: out,
nodeCount: function () { return net.nodeCount; },
device: function (id) {
const hit = allParts(model, '', []).filter(function (q) {
return q.id === id || q.p.id === id;
})[0];
const p = hit && hit.p;
if (!p || !Devices.is(p.kind)) {
throw new Error('There is no non-linear device called ' + id + ' in this circuit.');
}
const r = this.dc();
const seen = net.readouts.filter(function (x) { return x.id === hit.id; })[0];
const vs = seen.nodes.map(function (n) { return r.v[n]; });
const d = Devices.build(p);
return { kind: p.kind, v: vs, i: d.iv(d, vs, { raw: true }).i };
},
dc: function () {
need('a DC answer');
if (!cache.dc) {
const r = MNA.dc(net);
if (r.error) throw new Error(r.error);
cache.dc = r;
}
return cache.dc;
},
vout: function () { return this.dc().v[out()]; },
gain: function (f) {
need('a frequency response');
const v = MNA.acAt(net, 2 * Math.PI * f);
if (!v) throw new Error('The circuit is under-determined at ' + fmtEng(f, 'Hz') + '.');
return Lin.cabs(v[out()]);
},
phase: function (f) {
need('a frequency response');
const v = MNA.acAt(net, 2 * Math.PI * f);
if (!v) throw new Error('The circuit is under-determined at ' + fmtEng(f, 'Hz') + '.');
return Math.atan2(v[out()][1], v[out()][0]) * 180 / Math.PI;
},
corner: function (lo, hi) {
need('a corner frequency');
const self = this;
const ref = self.gain(lo);
const target = ref / Math.SQRT2;
let a = lo, b = hi;
for (let i = 0; i < 60; i++) {
const mid = Math.sqrt(a * b);
if (self.gain(mid) > target) a = mid; else b = mid;
}
return Math.sqrt(a * b);
},
step: function (tstop) {
need('a transient');
const r = MNA.tran(net, tstop, tstop / 600);
if (r.error) throw new Error(r.error);
const n = out();
return { t: r.t, v: r.v.map(function (row) { return row[n]; }) };
},
sketch: function (tstop) {
need('a sketch run');
const rig = mcuRig(net);
if (!rig) throw new Error('There is no microcontroller in this circuit.');
if (rig.missing) {
throw new Error('The interpreter is not loaded in this environment, so a sketch ' +
'cannot be run. src/mcu.js has to be loaded alongside src/circuit.js.');
}
const bad = rig.rigs.filter(function (r) { return r.error; })[0];
if (bad) {
throw new Error('The sketch on ' + bad.id + ' does not compile — line ' +
bad.error.line + ': ' + bad.error.message);
}
const r = MNA.tran(net, tstop, tstop / 600, rig.hooks);
if (r.error) throw new Error(r.error);
const first = rig.rigs[0];
const st = first.machine.state();
return {
t: r.t,
node: function (n) { return r.v.map(function (row) { return row[n]; }); },
out: net.probes.length === 1
? r.v.map(function (row) { return row[net.probes[0]]; }) : null,
console: first.machine.console(),
fault: st.fault,
loops: st.loops,
pin: function (name) {
return first.rec.pins.filter(function (q) { return q.name === String(name); })[0] || null;
},
};
},
assert: function (cond, msg) { if (!cond) throw new Error(msg || 'Assertion failed'); },
close: function (got, want, tolFrac, msg) {
const tol = Math.abs(want * (tolFrac === undefined ? 0.05 : tolFrac));
if (!(Math.abs(got - want) <= tol)) {
throw new Error((msg ? msg + ' — ' : '') + 'measured ' + Number(got).toPrecision(4) +
', expected ' + Number(want).toPrecision(4));
}
},
fmt: fmtEng,
};
}
function runCircuitChecks(model, checks, env) {
return (checks || []).map(function (c) {
let ctx;
try { ctx = circuitContext(model, env); }
catch (e) { return { name: c.name, pass: false, message: String(e && e.message || e) }; }
try {
const fn = new Function('c', '"use strict";\n' + c.code);
fn(ctx);
return { name: c.name, pass: true };
} catch (e) {
return { name: c.name, pass: false, message: String((e && e.message) || e) };
}
});
}
