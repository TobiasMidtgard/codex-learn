/* ============ language intelligence ============
 *
 * What the editor knows about the code being written: the types that exist, what you
 * can do with each of them, and what is actually reachable at the caret.
 *
 * Three layers:
 *   TYPES / GLOBALS / MODULES   the static model — members, signatures, one-line docs
 *   analyze()                   reads the buffer and infers what each name holds
 *   Complete.suggest()          decides what is valid at the caret and ranks it
 *
 * The model is deliberately small and hand-written rather than scraped: a learner is
 * better served by thirty members with real explanations than three hundred bare
 * names. Every entry carries a `ret` so chained calls keep their type.
 */

/* ---------- language word lists (shared: highlighter + autocomplete) ---------- */
const PY_KW_WORDS = ['False','None','True','and','as','assert','async','await','break','class','continue','def','del','elif','else','except','finally','for','from','global','if','import','in','is','lambda','nonlocal','not','or','pass','raise','return','try','while','with','yield'];
const PY_BI_WORDS = ['print','len','range','str','int','float','bool','list','dict','set','tuple','open','input','sum','min','max','sorted','reversed','round','abs','any','all','enumerate','zip','map','filter','isinstance','type','super','self','cls','object','Exception','ValueError','TypeError','KeyError','IndexError','AttributeError','ZeroDivisionError','FileNotFoundError','RuntimeError','NotImplementedError','StopIteration','__init__','__str__','__repr__','__name__','__main__'];
const JS_KW_WORDS = ['break','case','catch','class','const','continue','debugger','default','delete','do','else','export','extends','finally','for','function','if','import','in','instanceof','let','new','of','return','static','super','switch','this','throw','try','typeof','var','void','while','with','yield','async','await','get','set','null','undefined','true','false','NaN','Infinity'];
const JS_BI_WORDS = ['console','document','window','Math','JSON','Array','Object','String','Number','Boolean','Promise','Map','Set','Date','Error','RegExp','Symbol','fetch','setTimeout','setInterval','clearTimeout','clearInterval','parseInt','parseFloat','isNaN','alert','prompt','require','module','process','globalThis','parent'];

/* completion kinds — the vocabulary the menu renders */
const K = {
  VAR: 'variable', FN: 'function', METHOD: 'method', PROP: 'property',
  TYPE: 'type', IFACE: 'interface', KW: 'keyword', CONST: 'constant',
  SNIP: 'snippet', MOD: 'module', PARAM: 'parameter', FIELD: 'field',
};

const KIND_LABEL = {
  variable: 'Variable', function: 'Function', method: 'Method', property: 'Property',
  type: 'Type', interface: 'Interface', keyword: 'Keyword', constant: 'Constant',
  snippet: 'Snippet', module: 'Module', parameter: 'Parameter', field: 'Field',
};

/* single-glyph marks, in the spirit of an editor's completion icons */
const KIND_MARK = {
  variable: '\u25cb', function: '\u0192', method: '\u25c7', property: '\u25a1',
  type: '\u25b3', interface: '\u25b7', keyword: '\u25c6', constant: '\u25cf',
  snippet: '\u2726', module: '\u25a3', parameter: '\u25cb', field: '\u25a1',
};

/* ---------------------------------------------------------------- helpers */
function mem(n, kind, detail, doc, ret) {
  return { n: n, k: kind, detail: detail || '', doc: doc || '', ret: ret || '' };
}
function meth(n, detail, doc, ret) { return mem(n, K.METHOD, detail, doc, ret); }
function prop(n, detail, doc, ret) { return mem(n, K.PROP, detail, doc, ret); }
function fn(n, detail, doc, ret) { return mem(n, K.FN, detail, doc, ret); }
function konst(n, detail, doc, ret) { return mem(n, K.CONST, detail, doc, ret); }

/* ---------------------------------------------------------------- python */
const PY_TYPES = {
  str: { label: 'str', members: [
    meth('upper', '() -> str', 'A copy with every character upper-cased.', 'str'),
    meth('lower', '() -> str', 'A copy with every character lower-cased.', 'str'),
    meth('strip', '(chars=None) -> str', 'Removes whitespace (or the given characters) from both ends.', 'str'),
    meth('lstrip', '(chars=None) -> str', 'Removes leading whitespace.', 'str'),
    meth('rstrip', '(chars=None) -> str', 'Removes trailing whitespace.', 'str'),
    meth('split', '(sep=None, maxsplit=-1) -> list[str]', 'Splits into a list. With no argument, splits on any run of whitespace.', 'list'),
    meth('rsplit', '(sep=None, maxsplit=-1) -> list[str]', 'Splits from the right.', 'list'),
    meth('splitlines', '(keepends=False) -> list[str]', 'Splits on line breaks.', 'list'),
    meth('join', '(iterable) -> str', 'Joins the items of an iterable, using this string as the separator: ", ".join(names)', 'str'),
    meth('replace', '(old, new, count=-1) -> str', 'A copy with every occurrence of old replaced.', 'str'),
    meth('startswith', '(prefix) -> bool', 'True if the string begins with prefix.', 'bool'),
    meth('endswith', '(suffix) -> bool', 'True if the string ends with suffix.', 'bool'),
    meth('find', '(sub) -> int', 'Index of the first occurrence, or -1. Use index() to raise instead.', 'int'),
    meth('index', '(sub) -> int', 'Index of the first occurrence. Raises ValueError if absent.', 'int'),
    meth('count', '(sub) -> int', 'How many non-overlapping times sub appears.', 'int'),
    meth('format', '(*args, **kwargs) -> str', 'Fills {} placeholders. An f-string is usually clearer.', 'str'),
    meth('title', '() -> str', 'Upper-cases the first letter of each word.', 'str'),
    meth('capitalize', '() -> str', 'Upper-cases the first character only.', 'str'),
    meth('isdigit', '() -> bool', 'True if every character is a digit and the string is not empty.', 'bool'),
    meth('isalpha', '() -> bool', 'True if every character is a letter.', 'bool'),
    meth('isalnum', '() -> bool', 'True if every character is a letter or digit.', 'bool'),
    meth('isspace', '() -> bool', 'True if every character is whitespace.', 'bool'),
    meth('zfill', '(width) -> str', 'Pads on the left with zeros to the given width.', 'str'),
    meth('ljust', '(width, fill=" ") -> str', 'Pads on the right to the given width.', 'str'),
    meth('rjust', '(width, fill=" ") -> str', 'Pads on the left to the given width.', 'str'),
    meth('center', '(width, fill=" ") -> str', 'Centres the text in a field of the given width.', 'str'),
    meth('removeprefix', '(prefix) -> str', 'Drops prefix if present.', 'str'),
    meth('removesuffix', '(suffix) -> str', 'Drops suffix if present.', 'str'),
    meth('encode', '(encoding="utf-8") -> bytes', 'Converts text to bytes.', 'bytes'),
  ] },
  list: { label: 'list', members: [
    meth('append', '(item) -> None', 'Adds one item to the end.', 'None'),
    meth('extend', '(iterable) -> None', 'Adds every item of an iterable to the end.', 'None'),
    meth('insert', '(index, item) -> None', 'Inserts before the given index.', 'None'),
    meth('remove', '(value) -> None', 'Removes the first item equal to value.', 'None'),
    meth('pop', '(index=-1)', 'Removes and returns an item — the last one by default.', ''),
    meth('sort', '(key=None, reverse=False) -> None', 'Sorts in place. sorted() returns a new list instead.', 'None'),
    meth('reverse', '() -> None', 'Reverses in place.', 'None'),
    meth('clear', '() -> None', 'Removes every item.', 'None'),
    meth('copy', '() -> list', 'A shallow copy.', 'list'),
    meth('index', '(value) -> int', 'Index of the first item equal to value.', 'int'),
    meth('count', '(value) -> int', 'How many items equal value.', 'int'),
  ] },
  dict: { label: 'dict', members: [
    meth('get', '(key, default=None)', 'The value for key, or default when missing — never raises.', ''),
    meth('keys', '() -> dict_keys', 'A view of the keys.', 'list'),
    meth('values', '() -> dict_values', 'A view of the values.', 'list'),
    meth('items', '() -> dict_items', 'A view of (key, value) pairs — what you loop over.', 'list'),
    meth('update', '(other) -> None', 'Adds or replaces entries from another mapping.', 'None'),
    meth('pop', '(key, default)', 'Removes key and returns its value.', ''),
    meth('setdefault', '(key, default=None)', 'Returns the value, inserting default first if the key is missing.', ''),
    meth('clear', '() -> None', 'Removes every entry.', 'None'),
    meth('copy', '() -> dict', 'A shallow copy.', 'dict'),
  ] },
  set: { label: 'set', members: [
    meth('add', '(item) -> None', 'Adds an item; already-present items are ignored.', 'None'),
    meth('discard', '(item) -> None', 'Removes an item if present — no error if it is not.', 'None'),
    meth('remove', '(item) -> None', 'Removes an item. Raises KeyError if absent.', 'None'),
    meth('union', '(other) -> set', 'Every item in either set.', 'set'),
    meth('intersection', '(other) -> set', 'Only the items in both.', 'set'),
    meth('difference', '(other) -> set', 'Items in this set but not the other.', 'set'),
    meth('issubset', '(other) -> bool', 'True if every item is also in other.', 'bool'),
    meth('update', '(other) -> None', 'Adds every item of another iterable.', 'None'),
  ] },
  int: { label: 'int', members: [
    meth('bit_length', '() -> int', 'Bits needed to represent the number.', 'int'),
    meth('to_bytes', '(length, byteorder) -> bytes', 'The number as bytes.', 'bytes'),
  ] },
  float: { label: 'float', members: [
    meth('is_integer', '() -> bool', 'True when the value has no fractional part.', 'bool'),
  ] },
  tuple: { label: 'tuple', members: [
    meth('count', '(value) -> int', 'How many items equal value.', 'int'),
    meth('index', '(value) -> int', 'Index of the first item equal to value.', 'int'),
  ] },
  bytes: { label: 'bytes', members: [
    meth('decode', '(encoding="utf-8") -> str', 'Converts bytes back to text.', 'str'),
    meth('hex', '() -> str', 'Hexadecimal representation.', 'str'),
  ] },
  file: { label: 'file', members: [
    meth('read', '(size=-1) -> str', 'Reads the whole file, or size characters.', 'str'),
    meth('readline', '() -> str', 'Reads one line, including its newline.', 'str'),
    meth('readlines', '() -> list[str]', 'Every line as a list.', 'list'),
    meth('write', '(text) -> int', 'Writes text; returns how many characters were written.', 'int'),
    meth('writelines', '(lines) -> None', 'Writes every string in an iterable.', 'None'),
    meth('close', '() -> None', 'Closes the file. A with-block does this for you.', 'None'),
    meth('seek', '(offset) -> int', 'Moves the read position.', 'int'),
  ] },
};

/* builtins, with the return type that makes chaining work */
const PY_GLOBALS = [
  fn('print', '(*values, sep=" ", end="\\n") -> None', 'Writes values to the console.', 'None'),
  fn('len', '(obj) -> int', 'How many items a sequence or collection holds.', 'int'),
  fn('range', '(start, stop, step=1) -> range', 'A sequence of numbers, most often used in a for-loop.', 'list'),
  fn('str', '(obj) -> str', 'Converts a value to text.', 'str'),
  fn('int', '(x, base=10) -> int', 'Converts to a whole number, truncating floats.', 'int'),
  fn('float', '(x) -> float', 'Converts to a decimal number.', 'float'),
  fn('bool', '(x) -> bool', 'Truthiness of a value.', 'bool'),
  fn('list', '(iterable=()) -> list', 'Builds a list from any iterable.', 'list'),
  fn('dict', '(**kwargs) -> dict', 'Builds a dictionary.', 'dict'),
  fn('set', '(iterable=()) -> set', 'Builds a set — unordered, no duplicates.', 'set'),
  fn('tuple', '(iterable=()) -> tuple', 'Builds an immutable sequence.', 'tuple'),
  fn('open', '(file, mode="r") -> file', 'Opens a file. Prefer a with-block so it closes itself.', 'file'),
  fn('input', '(prompt="") -> str', 'Reads a line of text from the user — always a string.', 'str'),
  fn('sum', '(iterable, start=0)', 'Adds up every item.', 'int'),
  fn('min', '(iterable, key=None)', 'The smallest item.', ''),
  fn('max', '(iterable, key=None)', 'The largest item.', ''),
  fn('sorted', '(iterable, key=None, reverse=False) -> list', 'A new sorted list; the original is untouched.', 'list'),
  fn('reversed', '(seq)', 'The sequence back to front.', ''),
  fn('round', '(number, ndigits=None)', 'Rounds to the given number of decimals.', 'float'),
  fn('abs', '(x)', 'Distance from zero.', ''),
  fn('any', '(iterable) -> bool', 'True if at least one item is truthy.', 'bool'),
  fn('all', '(iterable) -> bool', 'True if every item is truthy.', 'bool'),
  fn('enumerate', '(iterable, start=0)', 'Pairs each item with its index: for i, item in enumerate(xs)', ''),
  fn('zip', '(*iterables)', 'Walks several sequences in step.', ''),
  fn('map', '(func, iterable)', 'Applies func to every item. A comprehension is often clearer.', ''),
  fn('filter', '(func, iterable)', 'Keeps the items for which func is true.', ''),
  fn('isinstance', '(obj, classinfo) -> bool', 'True if obj is of that type.', 'bool'),
  fn('type', '(obj)', 'The type of a value.', ''),
  fn('repr', '(obj) -> str', 'A debugging representation, quotes and all.', 'str'),
  fn('super', '() -> object', 'The parent class, for calling its methods.', ''),
  fn('divmod', '(a, b) -> tuple', 'Quotient and remainder together.', 'tuple'),
  fn('chr', '(i) -> str', 'The character for a code point.', 'str'),
  fn('ord', '(c) -> int', 'The code point of a character.', 'int'),
  fn('hex', '(n) -> str', 'Hexadecimal text for an integer.', 'str'),
  fn('format', '(value, spec) -> str', 'Formats one value: format(x, ".2f")', 'str'),
  konst('True', 'bool', 'Boolean true.', 'bool'),
  konst('False', 'bool', 'Boolean false.', 'bool'),
  konst('None', 'None', 'The absence of a value.', 'None'),
  mem('self', K.VAR, 'the instance', 'The object a method was called on. Always the first parameter of a method.', ''),
  mem('__name__', K.CONST, 'str', 'The module name — "__main__" when the file is the one being run.', 'str'),
];

const PY_EXCEPTIONS = ['Exception', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
  'AttributeError', 'ZeroDivisionError', 'FileNotFoundError', 'RuntimeError',
  'NotImplementedError', 'StopIteration', 'OverflowError', 'ArithmeticError', 'AssertionError']
  .map(function (n) { return mem(n, K.TYPE, 'exception', 'Raise or catch it: raise ' + n + '("...")', ''); });

const PY_MODULES = {
  math: [
    fn('sqrt', '(x) -> float', 'Square root.', 'float'), fn('floor', '(x) -> int', 'Rounds down.', 'int'),
    fn('ceil', '(x) -> int', 'Rounds up.', 'int'), fn('pow', '(x, y) -> float', 'x to the power y.', 'float'),
    fn('fabs', '(x) -> float', 'Absolute value as a float.', 'float'),
    fn('gcd', '(a, b) -> int', 'Greatest common divisor.', 'int'),
    fn('log', '(x, base=e) -> float', 'Logarithm.', 'float'), fn('log2', '(x) -> float', 'Base-2 logarithm.', 'float'),
    fn('sin', '(x) -> float', 'Sine, in radians.', 'float'), fn('cos', '(x) -> float', 'Cosine, in radians.', 'float'),
    fn('tan', '(x) -> float', 'Tangent, in radians.', 'float'),
    fn('isclose', '(a, b) -> bool', 'Compares floats with a tolerance — the safe way to test equality.', 'bool'),
    konst('pi', 'float', '3.14159…', 'float'), konst('e', 'float', "Euler's number.", 'float'),
    konst('inf', 'float', 'Positive infinity.', 'float'),
  ],
  random: [
    fn('randint', '(a, b) -> int', 'A whole number from a to b, both included.', 'int'),
    fn('random', '() -> float', 'A float in [0.0, 1.0).', 'float'),
    fn('choice', '(seq)', 'One item picked at random.', ''),
    fn('choices', '(population, k=1) -> list', 'k items, with replacement.', 'list'),
    fn('sample', '(population, k) -> list', 'k distinct items.', 'list'),
    fn('shuffle', '(seq) -> None', 'Shuffles a list in place.', 'None'),
    fn('uniform', '(a, b) -> float', 'A float between a and b.', 'float'),
    fn('seed', '(a=None) -> None', 'Fixes the sequence so a run is repeatable — do this in tests.', 'None'),
  ],
  json: [
    fn('dumps', '(obj, indent=None) -> str', 'Serialises a value to JSON text.', 'str'),
    fn('loads', '(s)', 'Parses JSON text back into Python values.', ''),
    fn('dump', '(obj, fp) -> None', 'Writes JSON to an open file.', 'None'),
    fn('load', '(fp)', 'Reads JSON from an open file.', ''),
  ],
  re: [
    fn('search', '(pattern, string)', 'Finds the first match anywhere, or None.', ''),
    fn('match', '(pattern, string)', 'Matches only at the start.', ''),
    fn('fullmatch', '(pattern, string)', 'Requires the whole string to match.', ''),
    fn('findall', '(pattern, string) -> list', 'Every non-overlapping match.', 'list'),
    fn('finditer', '(pattern, string)', 'Every match, as objects.', ''),
    fn('sub', '(pattern, repl, string) -> str', 'Replaces every match.', 'str'),
    fn('split', '(pattern, string) -> list', 'Splits on a pattern.', 'list'),
    fn('compile', '(pattern)', 'Pre-compiles a pattern you will reuse.', ''),
    fn('escape', '(s) -> str', 'Escapes regex metacharacters in literal text.', 'str'),
  ],
  time: [
    fn('time', '() -> float', 'Seconds since the epoch.', 'float'),
    fn('sleep', '(seconds) -> None', 'Pauses.', 'None'),
    fn('perf_counter', '() -> float', 'A high-resolution clock — use it for timing, not time().', 'float'),
    fn('monotonic', '() -> float', 'A clock that never goes backwards.', 'float'),
  ],
  os: [
    fn('getcwd', '() -> str', 'The current working directory.', 'str'),
    fn('listdir', '(path=".") -> list', 'Names inside a directory.', 'list'),
    fn('remove', '(path) -> None', 'Deletes a file.', 'None'),
    fn('rename', '(src, dst) -> None', 'Moves or renames.', 'None'),
    fn('makedirs', '(path, exist_ok=False) -> None', 'Creates a directory and its parents.', 'None'),
    prop('path', 'module', 'Path helpers: os.path.join, basename, exists.', ''),
    prop('environ', 'dict', 'Environment variables.', 'dict'),
  ],
  sys: [
    fn('exit', '(code=0) -> None', 'Stops the program.', 'None'),
    prop('argv', 'list[str]', 'Command-line arguments.', 'list'),
    prop('path', 'list[str]', 'Where imports are searched for.', 'list'),
    prop('maxsize', 'int', 'The largest practical integer.', 'int'),
  ],
  collections: [
    fn('Counter', '(iterable) -> Counter', 'Counts how often each item appears.', 'dict'),
    fn('defaultdict', '(factory) -> defaultdict', 'A dict that creates missing values for you.', 'dict'),
    fn('deque', '(iterable=()) -> deque', 'A list with fast appends and pops at both ends.', 'list'),
    fn('namedtuple', '(name, fields)', 'A tuple whose positions have names.', ''),
    fn('OrderedDict', '() -> OrderedDict', 'A dict that remembers insertion order explicitly.', 'dict'),
  ],
  itertools: [
    fn('product', '(*iterables)', 'Cartesian product — nested loops, flattened.', ''),
    fn('permutations', '(iterable, r=None)', 'Every ordering.', ''),
    fn('combinations', '(iterable, r)', 'Every unordered selection of r items.', ''),
    fn('chain', '(*iterables)', 'Treats several iterables as one.', ''),
    fn('islice', '(iterable, stop)', 'Slices any iterable.', ''),
    fn('groupby', '(iterable, key=None)', 'Groups consecutive items — sort first.', ''),
    fn('accumulate', '(iterable)', 'Running totals.', ''),
    fn('count', '(start=0, step=1)', 'Counts upward forever.', ''),
    fn('cycle', '(iterable)', 'Repeats an iterable forever.', ''),
  ],
  statistics: [
    fn('mean', '(data) -> float', 'Arithmetic average.', 'float'),
    fn('median', '(data) -> float', 'Middle value.', 'float'),
    fn('mode', '(data)', 'Most common value.', ''),
    fn('stdev', '(data) -> float', 'Sample standard deviation.', 'float'),
    fn('pstdev', '(data) -> float', 'Population standard deviation.', 'float'),
  ],
  string: [
    konst('ascii_lowercase', 'str', "'abcdefghijklmnopqrstuvwxyz'", 'str'),
    konst('ascii_uppercase', 'str', "'ABCDEFGHIJKLMNOPQRSTUVWXYZ'", 'str'),
    konst('ascii_letters', 'str', 'Lower-case then upper-case.', 'str'),
    konst('digits', 'str', "'0123456789'", 'str'),
    konst('punctuation', 'str', 'ASCII punctuation characters.', 'str'),
  ],
  hashlib: [
    fn('sha256', '(data=b"")', 'SHA-256 hasher. Call .hexdigest() for the result.', ''),
    fn('sha1', '(data=b"")', 'SHA-1 hasher — obsolete for security.', ''),
    fn('md5', '(data=b"")', 'MD5 hasher — broken for security, fine for checksums.', ''),
  ],
  secrets: [
    fn('token_hex', '(nbytes=32) -> str', 'A cryptographically strong random hex string.', 'str'),
    fn('token_urlsafe', '(nbytes=32) -> str', 'A strong random URL-safe string.', 'str'),
    fn('randbelow', '(n) -> int', 'A strong random integer below n.', 'int'),
    fn('choice', '(seq)', 'A strong random choice.', ''),
  ],
  functools: [
    fn('lru_cache', '(maxsize=128)', 'Decorator that remembers results of pure functions.', ''),
    fn('reduce', '(func, iterable, initial)', 'Folds a sequence into one value.', ''),
    fn('wraps', '(func)', 'Decorator that keeps the wrapped name and docstring.', ''),
    fn('partial', '(func, *args)', 'Pre-fills some arguments.', ''),
  ],
  heapq: [
    fn('heappush', '(heap, item) -> None', 'Pushes onto a min-heap.', 'None'),
    fn('heappop', '(heap)', 'Pops the smallest item.', ''),
    fn('heapify', '(list) -> None', 'Turns a list into a heap in place.', 'None'),
    fn('nsmallest', '(n, iterable) -> list', 'The n smallest items.', 'list'),
    fn('nlargest', '(n, iterable) -> list', 'The n largest items.', 'list'),
  ],
  bisect: [
    fn('bisect_left', '(a, x) -> int', 'Insertion point in a sorted list, before equals.', 'int'),
    fn('bisect_right', '(a, x) -> int', 'Insertion point after equals.', 'int'),
    fn('insort', '(a, x) -> None', 'Inserts keeping the list sorted.', 'None'),
  ],
  textwrap: [
    fn('dedent', '(text) -> str', 'Removes common leading whitespace.', 'str'),
    fn('fill', '(text, width=70) -> str', 'Wraps text to a width.', 'str'),
    fn('shorten', '(text, width) -> str', 'Truncates with an ellipsis.', 'str'),
  ],
  datetime: [
    fn('datetime', '(year, month, day)', 'A date and time. datetime.now() for the current moment.', ''),
    fn('date', '(year, month, day)', 'A calendar date.', ''),
    fn('timedelta', '(days=0, seconds=0)', 'A duration you can add to a date.', ''),
  ],
  dataclasses: [
    fn('dataclass', '(cls=None, *, frozen=False)', 'Decorator that writes __init__, __repr__ and __eq__ for you.', ''),
    fn('field', '(default_factory=None)', 'Per-field configuration, e.g. a fresh list per instance.', ''),
    fn('asdict', '(instance) -> dict', 'The instance as a dictionary.', 'dict'),
  ],
  hmac: [
    fn('new', '(key, msg, digestmod)', 'A keyed hash.', ''),
    fn('compare_digest', '(a, b) -> bool', 'Constant-time comparison — use it for secrets.', 'bool'),
  ],
  copy: [
    fn('copy', '(x)', 'A shallow copy.', ''),
    fn('deepcopy', '(x)', 'A fully independent copy.', ''),
  ],
};

const PY_SNIPPETS = [
  { n: 'main', detail: 'if __name__ == "__main__"', doc: 'The guard that runs code only when the file is executed directly.',
    body: 'if __name__ == "__main__":\n    ${1:main()}' },
  { n: 'def', detail: 'function definition', doc: 'Defines a function with a docstring.',
    body: 'def ${1:name}(${2:args}):\n    """${3:What it does.}"""\n    ${0:pass}' },
  { n: 'class', detail: 'class definition', doc: 'A class with an initialiser.',
    body: 'class ${1:Name}:\n    def __init__(self, ${2:value}):\n        self.value = value\n        ${0}' },
  { n: 'for', detail: 'for item in iterable', doc: 'Loops over every item.',
    body: 'for ${1:item} in ${2:items}:\n    ${0:pass}' },
  { n: 'fore', detail: 'for i, item in enumerate(...)', doc: 'Loops with the index alongside the item.',
    body: 'for ${1:i}, ${2:item} in enumerate(${3:items}):\n    ${0:pass}' },
  { n: 'forr', detail: 'for i in range(n)', doc: 'Counts from 0 up to n-1.',
    body: 'for ${1:i} in range(${2:n}):\n    ${0:pass}' },
  { n: 'while', detail: 'while condition', doc: 'Repeats while a condition holds.',
    body: 'while ${1:condition}:\n    ${0:pass}' },
  { n: 'if', detail: 'if condition', doc: 'Runs a block conditionally.',
    body: 'if ${1:condition}:\n    ${0:pass}' },
  { n: 'ifelse', detail: 'if / else', doc: 'One branch or the other.',
    body: 'if ${1:condition}:\n    ${2:pass}\nelse:\n    ${0:pass}' },
  { n: 'try', detail: 'try / except', doc: 'Handles an error instead of crashing.',
    body: 'try:\n    ${1:pass}\nexcept ${2:ValueError} as e:\n    ${0:print(e)}' },
  { n: 'with', detail: 'with open(...) as f', doc: 'Opens a file that closes itself.',
    body: 'with open(${1:"file.txt"}) as f:\n    ${0:text = f.read()}' },
  { n: 'comp', detail: 'list comprehension', doc: 'Builds a list from an iterable in one expression.',
    body: '[${1:value} for value in ${2:items}]' },
  { n: 'dcomp', detail: 'dict comprehension', doc: 'Builds a dictionary in one expression.',
    body: '{key: ${1:value} for key, value in ${2:mapping}.items()}' },
  { n: 'printf', detail: 'print(f"...")', doc: 'Prints an f-string.',
    body: 'print(f"${1:label}: {${2:value}}")' },
];

/* ---------------------------------------------------------------- javascript */
const JS_TYPES = {
  string: { label: 'string', members: [
    prop('length', 'number', 'How many characters.', 'number'),
    meth('toUpperCase', '() -> string', 'Upper-cased copy.', 'string'),
    meth('toLowerCase', '() -> string', 'Lower-cased copy.', 'string'),
    meth('trim', '() -> string', 'Removes whitespace from both ends.', 'string'),
    meth('split', '(sep) -> string[]', 'Splits into an array.', 'array'),
    meth('replace', '(pattern, replacement) -> string', 'Replaces the first match (or all, with a /g regex).', 'string'),
    meth('replaceAll', '(search, replacement) -> string', 'Replaces every occurrence.', 'string'),
    meth('startsWith', '(prefix) -> boolean', 'True if it begins with prefix.', 'boolean'),
    meth('endsWith', '(suffix) -> boolean', 'True if it ends with suffix.', 'boolean'),
    meth('includes', '(sub) -> boolean', 'True if sub appears anywhere.', 'boolean'),
    meth('indexOf', '(sub) -> number', 'Index of the first occurrence, or -1.', 'number'),
    meth('slice', '(start, end) -> string', 'A section. Negative indexes count from the end.', 'string'),
    meth('charAt', '(i) -> string', 'The character at an index.', 'string'),
    meth('at', '(i) -> string', 'Like charAt but accepts negative indexes.', 'string'),
    meth('padStart', '(length, pad) -> string', 'Pads on the left to a length.', 'string'),
    meth('padEnd', '(length, pad) -> string', 'Pads on the right to a length.', 'string'),
    meth('repeat', '(count) -> string', 'The string repeated.', 'string'),
    meth('match', '(regexp)', 'Matches against a regular expression.', ''),
    meth('localeCompare', '(other) -> number', 'Sort order against another string.', 'number'),
  ] },
  array: { label: 'array', members: [
    prop('length', 'number', 'How many items.', 'number'),
    meth('push', '(...items) -> number', 'Adds to the end; returns the new length.', 'number'),
    meth('pop', '()', 'Removes and returns the last item.', ''),
    meth('shift', '()', 'Removes and returns the first item.', ''),
    meth('unshift', '(...items) -> number', 'Adds to the front.', 'number'),
    meth('slice', '(start, end) -> array', 'A copy of a section — the original is untouched.', 'array'),
    meth('splice', '(start, count, ...items) -> array', 'Removes and/or inserts in place.', 'array'),
    meth('map', '(fn) -> array', 'A new array with fn applied to every item.', 'array'),
    meth('filter', '(fn) -> array', 'A new array of the items fn keeps.', 'array'),
    meth('reduce', '(fn, initial)', 'Folds the array into a single value.', ''),
    meth('forEach', '(fn) -> undefined', 'Runs fn for each item. Use map when you want a result.', 'undefined'),
    meth('find', '(fn)', 'The first item fn accepts, or undefined.', ''),
    meth('findIndex', '(fn) -> number', 'The index of the first match, or -1.', 'number'),
    meth('includes', '(value) -> boolean', 'True if the value is present.', 'boolean'),
    meth('indexOf', '(value) -> number', 'Index of the value, or -1.', 'number'),
    meth('join', '(sep) -> string', 'Joins the items into a string.', 'string'),
    meth('sort', '(compare) -> array', 'Sorts in place — pass a comparator for numbers.', 'array'),
    meth('reverse', '() -> array', 'Reverses in place.', 'array'),
    meth('some', '(fn) -> boolean', 'True if fn accepts at least one item.', 'boolean'),
    meth('every', '(fn) -> boolean', 'True if fn accepts every item.', 'boolean'),
    meth('concat', '(...arrays) -> array', 'A new array with the others appended.', 'array'),
    meth('flat', '(depth=1) -> array', 'Flattens nested arrays.', 'array'),
    meth('at', '(i)', 'The item at an index; negative counts from the end.', ''),
  ] },
  number: { label: 'number', members: [
    meth('toFixed', '(digits) -> string', 'Text with a fixed number of decimals.', 'string'),
    meth('toString', '(radix=10) -> string', 'The number as text.', 'string'),
    meth('toPrecision', '(digits) -> string', 'Text with a number of significant digits.', 'string'),
  ] },
  promise: { label: 'Promise', members: [
    meth('then', '(onFulfilled) -> Promise', 'Runs when the promise resolves.', 'promise'),
    meth('catch', '(onRejected) -> Promise', 'Runs when it rejects.', 'promise'),
    meth('finally', '(fn) -> Promise', 'Runs either way.', 'promise'),
  ] },
  element: { label: 'Element', members: [
    prop('textContent', 'string', 'The text inside — safe, unlike innerHTML.', 'string'),
    prop('innerHTML', 'string', 'The markup inside. Never assign untrusted text to it.', 'string'),
    prop('value', 'string', 'The current value of an input.', 'string'),
    prop('checked', 'boolean', 'Whether a checkbox or radio is ticked.', 'boolean'),
    prop('disabled', 'boolean', 'Whether the control is disabled.', 'boolean'),
    prop('hidden', 'boolean', 'Whether the element is hidden.', 'boolean'),
    prop('className', 'string', 'The class attribute as one string.', 'string'),
    prop('classList', 'DOMTokenList', 'Add, remove and toggle classes.', 'classList'),
    prop('dataset', 'object', 'The data-* attributes.', 'object'),
    prop('style', 'CSSStyleDeclaration', 'Inline styles.', 'object'),
    prop('id', 'string', 'The id attribute.', 'string'),
    prop('children', 'HTMLCollection', 'Child elements.', 'array'),
    prop('parentElement', 'Element', 'The element containing this one.', 'element'),
    meth('querySelector', '(selector) -> Element', 'The first descendant matching a CSS selector.', 'element'),
    meth('querySelectorAll', '(selector) -> NodeList', 'Every descendant matching a selector.', 'array'),
    meth('addEventListener', '(type, handler) -> undefined', 'Runs handler when the event fires.', 'undefined'),
    meth('removeEventListener', '(type, handler) -> undefined', 'Stops listening.', 'undefined'),
    meth('appendChild', '(node) -> Node', 'Adds a child at the end.', 'element'),
    meth('append', '(...nodes) -> undefined', 'Adds children or text at the end.', 'undefined'),
    meth('remove', '() -> undefined', 'Takes the element out of the document.', 'undefined'),
    meth('closest', '(selector) -> Element', 'The nearest ancestor matching a selector.', 'element'),
    meth('setAttribute', '(name, value) -> undefined', 'Sets an attribute.', 'undefined'),
    meth('getAttribute', '(name) -> string', 'Reads an attribute.', 'string'),
    meth('focus', '() -> undefined', 'Moves keyboard focus here.', 'undefined'),
    meth('click', '() -> undefined', 'Fires a click.', 'undefined'),
    meth('getBoundingClientRect', '() -> DOMRect', 'Size and position on screen.', 'object'),
  ] },
  classList: { label: 'DOMTokenList', members: [
    meth('add', '(...classes) -> undefined', 'Adds classes.', 'undefined'),
    meth('remove', '(...classes) -> undefined', 'Removes classes.', 'undefined'),
    meth('toggle', '(class, force) -> boolean', 'Adds or removes; the second argument forces which.', 'boolean'),
    meth('contains', '(class) -> boolean', 'True if the class is present.', 'boolean'),
  ] },
  map: { label: 'Map', members: [
    prop('size', 'number', 'How many entries.', 'number'),
    meth('get', '(key)', 'The value for a key.', ''),
    meth('set', '(key, value) -> Map', 'Stores a value.', 'map'),
    meth('has', '(key) -> boolean', 'True if the key exists.', 'boolean'),
    meth('delete', '(key) -> boolean', 'Removes an entry.', 'boolean'),
    meth('forEach', '(fn) -> undefined', 'Runs fn for each entry.', 'undefined'),
  ] },
  set: { label: 'Set', members: [
    prop('size', 'number', 'How many items.', 'number'),
    meth('add', '(value) -> Set', 'Adds a value.', 'set'),
    meth('has', '(value) -> boolean', 'True if present.', 'boolean'),
    meth('delete', '(value) -> boolean', 'Removes a value.', 'boolean'),
  ] },
  object: { label: 'object', members: [
    meth('hasOwnProperty', '(key) -> boolean', 'True if the object itself has that key.', 'boolean'),
    meth('toString', '() -> string', 'Text representation.', 'string'),
  ] },
};

const JS_GLOBALS = [
  mem('console', K.MOD, 'namespace', 'Writes to the developer console.', 'console'),
  mem('document', K.MOD, 'Document', 'The page. Start here to find elements.', 'document'),
  mem('window', K.MOD, 'Window', 'The browser window and every global.', 'window'),
  mem('Math', K.MOD, 'namespace', 'Numeric helpers.', 'Math'),
  mem('JSON', K.MOD, 'namespace', 'Convert values to and from JSON text.', 'JSON'),
  mem('localStorage', K.MOD, 'Storage', 'Key-value storage that survives a reload.', 'localStorage'),
  mem('Object', K.MOD, 'namespace', 'Helpers for plain objects.', 'Object'),
  mem('Array', K.MOD, 'namespace', 'Array constructor and helpers.', 'Array'),
  mem('Promise', K.MOD, 'namespace', 'Asynchronous results.', 'Promise'),
  fn('fetch', '(url, options) -> Promise', 'Requests a URL. Returns a promise for the response.', 'promise'),
  fn('setTimeout', '(fn, ms) -> number', 'Runs fn once after a delay.', 'number'),
  fn('setInterval', '(fn, ms) -> number', 'Runs fn repeatedly.', 'number'),
  fn('clearTimeout', '(id) -> undefined', 'Cancels a timeout.', 'undefined'),
  fn('clearInterval', '(id) -> undefined', 'Cancels an interval.', 'undefined'),
  fn('parseInt', '(s, radix=10) -> number', 'Parses a whole number from text.', 'number'),
  fn('parseFloat', '(s) -> number', 'Parses a decimal number from text.', 'number'),
  fn('isNaN', '(x) -> boolean', 'True if the value is not a number.', 'boolean'),
  fn('alert', '(message) -> undefined', 'A blocking message box.', 'undefined'),
  fn('structuredClone', '(value)', 'A deep copy of a value.', ''),
  mem('Number', K.TYPE, 'constructor', 'Number conversions and constants.', 'Number'),
  mem('String', K.TYPE, 'constructor', 'String conversions.', ''),
  mem('Map', K.TYPE, 'constructor', 'A keyed collection that accepts any key type.', ''),
  mem('Set', K.TYPE, 'constructor', 'A collection of unique values.', ''),
  mem('Date', K.TYPE, 'constructor', 'Dates and times.', ''),
  mem('Error', K.TYPE, 'constructor', 'The base error type.', ''),
  konst('null', 'null', 'A deliberate absence of value.', ''),
  konst('undefined', 'undefined', 'A value that was never set.', ''),
  konst('true', 'boolean', 'Boolean true.', 'boolean'),
  konst('false', 'boolean', 'Boolean false.', 'boolean'),
  mem('this', K.VAR, 'the current object', 'What the function was called on. Arrow functions inherit it.', ''),
];

const JS_MODULES = {
  console: [
    fn('log', '(...values) -> undefined', 'Writes to the console.', 'undefined'),
    fn('warn', '(...values) -> undefined', 'A warning.', 'undefined'),
    fn('error', '(...values) -> undefined', 'An error.', 'undefined'),
    fn('info', '(...values) -> undefined', 'Informational output.', 'undefined'),
    fn('table', '(data) -> undefined', 'Renders arrays and objects as a table.', 'undefined'),
    fn('time', '(label) -> undefined', 'Starts a timer.', 'undefined'),
    fn('timeEnd', '(label) -> undefined', 'Stops it and prints the elapsed time.', 'undefined'),
  ],
  Math: [
    fn('floor', '(x) -> number', 'Rounds down.', 'number'), fn('ceil', '(x) -> number', 'Rounds up.', 'number'),
    fn('round', '(x) -> number', 'Rounds to the nearest whole number.', 'number'),
    fn('random', '() -> number', 'A float in [0, 1).', 'number'),
    fn('max', '(...values) -> number', 'The largest argument.', 'number'),
    fn('min', '(...values) -> number', 'The smallest argument.', 'number'),
    fn('abs', '(x) -> number', 'Distance from zero.', 'number'),
    fn('sqrt', '(x) -> number', 'Square root.', 'number'),
    fn('pow', '(x, y) -> number', 'x to the power y — or use x ** y.', 'number'),
    fn('trunc', '(x) -> number', 'Drops the fractional part.', 'number'),
    fn('hypot', '(...values) -> number', 'Square root of the sum of squares.', 'number'),
    konst('PI', 'number', '3.14159…', 'number'), konst('E', 'number', "Euler's number.", 'number'),
  ],
  JSON: [
    fn('stringify', '(value, replacer, space) -> string', 'Serialises to JSON. Pass 2 as the third argument to indent.', 'string'),
    fn('parse', '(text)', 'Parses JSON text. Throws on malformed input.', ''),
  ],
  document: [
    fn('querySelector', '(selector) -> Element', 'The first element matching a CSS selector.', 'element'),
    fn('querySelectorAll', '(selector) -> NodeList', 'Every element matching a selector.', 'array'),
    fn('getElementById', '(id) -> Element', 'The element with that id.', 'element'),
    fn('createElement', '(tag) -> Element', 'Builds a new element.', 'element'),
    fn('addEventListener', '(type, handler) -> undefined', 'Listens on the whole document.', 'undefined'),
    prop('body', 'Element', 'The body element.', 'element'),
    prop('head', 'Element', 'The head element.', 'element'),
    prop('title', 'string', 'The page title.', 'string'),
  ],
  localStorage: [
    fn('getItem', '(key) -> string', 'Reads a stored string, or null.', 'string'),
    fn('setItem', '(key, value) -> undefined', 'Stores a string. Objects must be JSON.stringify-ed first.', 'undefined'),
    fn('removeItem', '(key) -> undefined', 'Removes a key.', 'undefined'),
    fn('clear', '() -> undefined', 'Removes everything.', 'undefined'),
  ],
  Object: [
    fn('keys', '(obj) -> string[]', 'The own enumerable keys.', 'array'),
    fn('values', '(obj) -> any[]', 'The own enumerable values.', 'array'),
    fn('entries', '(obj) -> [string, any][]', 'Key-value pairs — what you loop over.', 'array'),
    fn('assign', '(target, ...sources) -> object', 'Copies properties onto target.', 'object'),
    fn('freeze', '(obj) -> object', 'Makes an object read-only.', 'object'),
    fn('fromEntries', '(pairs) -> object', 'Builds an object from key-value pairs.', 'object'),
  ],
  Array: [
    fn('from', '(iterable, mapFn) -> array', 'Builds an array from anything iterable.', 'array'),
    fn('isArray', '(value) -> boolean', 'True if the value is an array.', 'boolean'),
    fn('of', '(...items) -> array', 'An array of the arguments.', 'array'),
  ],
  Promise: [
    fn('resolve', '(value) -> Promise', 'A promise already fulfilled.', 'promise'),
    fn('reject', '(reason) -> Promise', 'A promise already rejected.', 'promise'),
    fn('all', '(promises) -> Promise', 'Waits for every promise, or rejects on the first failure.', 'promise'),
    fn('allSettled', '(promises) -> Promise', 'Waits for every promise, successes and failures alike.', 'promise'),
    fn('race', '(promises) -> Promise', 'Settles with whichever finishes first.', 'promise'),
  ],
  Number: [
    fn('parseFloat', '(s) -> number', 'Parses a decimal.', 'number'),
    fn('parseInt', '(s, radix) -> number', 'Parses a whole number.', 'number'),
    fn('isInteger', '(x) -> boolean', 'True for whole numbers.', 'boolean'),
    fn('isFinite', '(x) -> boolean', 'True unless infinite or NaN.', 'boolean'),
    konst('MAX_SAFE_INTEGER', 'number', 'The largest exactly representable integer.', 'number'),
  ],
  window: [
    fn('addEventListener', '(type, handler) -> undefined', 'Listens on the window.', 'undefined'),
    fn('setTimeout', '(fn, ms) -> number', 'Runs fn after a delay.', 'number'),
    fn('fetch', '(url) -> Promise', 'Requests a URL.', 'promise'),
    prop('innerWidth', 'number', 'Viewport width in pixels.', 'number'),
    prop('innerHeight', 'number', 'Viewport height in pixels.', 'number'),
    prop('location', 'Location', 'The current URL.', 'object'),
  ],
};

const JS_SNIPPETS = [
  { n: 'fn', detail: 'function declaration', doc: 'A named function.',
    body: 'function ${1:name}(${2:args}) {\n  ${0}\n}' },
  { n: 'arrow', detail: 'arrow function', doc: 'A short function expression.',
    body: 'const ${1:name} = (${2:args}) => {\n  ${0}\n};' },
  { n: 'for', detail: 'for (let i = 0; ...)', doc: 'A counted loop.',
    body: 'for (let i = 0; i < ${1:n}; i++) {\n  ${0}\n}' },
  { n: 'forof', detail: 'for (const x of xs)', doc: 'Loops over the values of an iterable.',
    body: 'for (const ${1:item} of ${2:items}) {\n  ${0}\n}' },
  { n: 'foreach', detail: 'items.forEach(...)', doc: 'Runs a function for each item.',
    body: '${1:items}.forEach((${2:item}) => {\n  ${0}\n});' },
  { n: 'if', detail: 'if (condition)', doc: 'A conditional block.',
    body: 'if (${1:condition}) {\n  ${0}\n}' },
  { n: 'ifelse', detail: 'if / else', doc: 'One branch or the other.',
    body: 'if (${1:condition}) {\n  ${2}\n} else {\n  ${0}\n}' },
  { n: 'try', detail: 'try / catch', doc: 'Handles a thrown error.',
    body: 'try {\n  ${1}\n} catch (err) {\n  ${0:console.error(err);}\n}' },
  { n: 'cls', detail: 'class declaration', doc: 'A class with a constructor.',
    body: 'class ${1:Name} {\n  constructor(${2:value}) {\n    this.value = value;\n  }\n  ${0}\n}' },
  { n: 'log', detail: 'console.log(...)', doc: 'Prints to the console.',
    body: 'console.log(${0});' },
  { n: 'qs', detail: 'document.querySelector(...)', doc: 'Finds one element by CSS selector.',
    body: "const ${1:el} = document.querySelector('${2:selector}');\n${0}" },
  { n: 'listen', detail: 'addEventListener(...)', doc: 'Responds to an event.',
    body: "${1:el}.addEventListener('${2:click}', (${3:event}) => {\n  ${0}\n});" },
  { n: 'afetch', detail: 'await fetch(...)', doc: 'Requests a URL and parses JSON.',
    body: "const res = await fetch('${1:/api}');\nconst ${2:data} = await res.json();\n${0}" },
];

/* ---------------------------------------------------------------- css / html */
const CSS_PROPS = [
  ['display', 'flex | grid | block | inline-block | none', 'How the box is laid out and how it lays out its children.'],
  ['position', 'static | relative | absolute | fixed | sticky', 'How the box is positioned.'],
  ['color', '<color>', 'Text colour.'],
  ['background', '<bg>', 'Shorthand for every background property.'],
  ['background-color', '<color>', 'The colour behind the content.'],
  ['margin', '<length>', 'Space outside the border. Collapses vertically between siblings.'],
  ['padding', '<length>', 'Space inside the border.'],
  ['border', '<width> <style> <color>', 'Shorthand for the border.'],
  ['border-radius', '<length>', 'Rounds the corners.'],
  ['width', '<length> | %', 'The content width.'],
  ['max-width', '<length>', 'An upper bound — the usual way to keep text readable.'],
  ['min-width', '<length>', 'A lower bound. Set 0 on grid and flex children that overflow.'],
  ['height', '<length> | %', 'The content height.'],
  ['font-size', '<length>', 'Text size.'],
  ['font-family', '<stack>', 'Typeface, with fallbacks.'],
  ['font-weight', '400 | 600 | bold', 'Stroke weight.'],
  ['line-height', '<number>', 'Leading. A unitless number scales with the font size.'],
  ['letter-spacing', '<length>', 'Tracking between characters.'],
  ['text-align', 'left | center | right', 'Horizontal alignment of inline content.'],
  ['text-transform', 'uppercase | lowercase | capitalize', 'Changes the case as displayed.'],
  ['flex', '<grow> <shrink> <basis>', 'How a flex child grows and shrinks.'],
  ['flex-direction', 'row | column', 'The main axis of a flex container.'],
  ['flex-wrap', 'nowrap | wrap', 'Whether flex children may move to a new line.'],
  ['justify-content', 'flex-start | center | space-between', 'Alignment along the main axis.'],
  ['align-items', 'stretch | center | flex-start', 'Alignment across the main axis.'],
  ['gap', '<length>', 'Space between grid or flex children — better than margins.'],
  ['grid-template-columns', 'repeat(3, 1fr)', 'The column tracks of a grid.'],
  ['grid-template-rows', '<tracks>', 'The row tracks of a grid.'],
  ['overflow', 'visible | hidden | auto | scroll', 'What happens to content that does not fit.'],
  ['opacity', '0 – 1', 'Transparency of the whole element.'],
  ['transform', 'translate() | scale() | rotate()', 'Moves or distorts without affecting layout.'],
  ['transition', '<property> <duration> <easing>', 'Animates a change in a property.'],
  ['box-shadow', '<x> <y> <blur> <color>', 'A shadow cast by the box.'],
  ['cursor', 'pointer | default | text', 'The mouse cursor over this element.'],
  ['z-index', '<integer>', 'Stacking order. Only applies to positioned elements.'],
  ['top', '<length>', 'Offset from the top, for positioned elements.'],
  ['left', '<length>', 'Offset from the left, for positioned elements.'],
  ['white-space', 'normal | nowrap | pre', 'How whitespace and line breaks are treated.'],
  ['object-fit', 'cover | contain', 'How a replaced element fills its box.'],
  ['visibility', 'visible | hidden', 'Hides while keeping the space.'],
  ['list-style', 'none | disc', 'Bullet style.'],
].map(function (r) { return mem(r[0], K.PROP, r[1], r[2], ''); });

const CSS_SNIPPETS = [
  { n: 'flexcenter', detail: 'centre with flexbox', doc: 'Centres a child both ways.',
    body: 'display: flex;\nalign-items: center;\njustify-content: center;' },
  { n: 'grid', detail: 'responsive grid', doc: 'Columns that wrap without a media query.',
    body: 'display: grid;\ngrid-template-columns: repeat(auto-fit, minmax(${1:220px}, 1fr));\ngap: ${2:16px};' },
  { n: 'media', detail: 'media query', doc: 'Styles below a width.',
    body: '@media (max-width: ${1:720px}) {\n  ${0}\n}' },
  { n: 'transition', detail: 'transition', doc: 'Animates a property change.',
    body: 'transition: ${1:all} ${2:.18s} ${3:ease};' },
];

const HTML_SNIPPETS = [
  { n: 'html5', detail: 'document skeleton', doc: 'A complete minimal HTML page.',
    body: '<!doctype html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width, initial-scale=1">\n  <title>${1:Page}</title>\n</head>\n<body>\n  ${0}\n</body>\n</html>' },
  { n: 'link', detail: 'stylesheet link', doc: 'Attaches a stylesheet.',
    body: '<link rel="stylesheet" href="${1:style.css}">' },
  { n: 'form', detail: 'form with a field', doc: 'A labelled input and a submit button.',
    body: '<form>\n  <label for="email">${1:Email}</label>\n  <input id="email" name="email" type="email">\n  <button type="submit">${0:Send}</button>\n</form>' },
  { n: 'table', detail: 'table skeleton', doc: 'A table with a head and one row.',
    body: '<table>\n  <thead>\n    <tr><th>${1:Column}</th></tr>\n  </thead>\n  <tbody>\n    <tr><td>${0}</td></tr>\n  </tbody>\n</table>' },
];

/* ================================================================ inference
 *
 * A real type checker is out of scope and would be the wrong tool anyway: the
 * buffer is usually half-written and syntactically invalid. This reads what is
 * there line by line and records what it can prove cheaply — assignments,
 * parameters, loop variables, imports, class attributes. Anything it cannot work
 * out simply has no type, and the caller falls back to the generic pool.
 */

const PY_LIT = [
  [/^(['"])/, 'str'], [/^[fF](['"])/, 'str'], [/^[rRbB](['"])/, 'str'],
  [/^\[/, 'list'], [/^\{[^:}]*:/, 'dict'], [/^\{/, 'set'],
  [/^\(/, 'tuple'], [/^\d+\.\d/, 'float'], [/^\d/, 'int'],
  [/^(True|False)\b/, 'bool'], [/^None\b/, 'None'],
];
const JS_LIT = [
  [/^(['"`])/, 'string'], [/^\[/, 'array'], [/^\{/, 'object'],
  [/^\d+\.\d/, 'number'], [/^\d/, 'number'],
  [/^(true|false)\b/, 'boolean'], [/^null\b/, 'null'], [/^new Map\b/, 'map'],
  [/^new Set\b/, 'set'], [/^new Promise\b/, 'promise'], [/^\/[^/]/, 'regexp'],
];

/* ---------------------------------------------------------------- mcu sketches
 *
 * The C-like subset src/mcu.js runs on the schematic's microcontroller. It is NOT
 * Arduino: it has no objects, no strings beyond literals, no arrays, and twenty-four
 * builtins. Everything below is taken from that file's own TYPES, BUILTIN and
 * CONSTANTS tables, and build.mjs fails if the two lists drift apart — a completion
 * for a name the machine does not have teaches the wrong thing twice, once when it is
 * offered and again when the sketch is refused.
 */
const MCU_KW_WORDS = ['if', 'else', 'while', 'for', 'return', 'break', 'continue'];

const MCU_TYPE_WORDS = ['void', 'int', 'long', 'byte', 'char', 'bool', 'boolean',
  'float', 'double'];

/* `long`, `byte`, `bool`, `boolean` and `char` are all the one integer type, and
   `double` is `float`. The machine has one integer width and one float width, so
   there is nothing to widen to; the doc says so rather than letting a learner infer
   precision that is not there. */
const MCU_TYPE_SET = {};
MCU_TYPE_WORDS.forEach(function (w) { MCU_TYPE_SET[w] = 1; });

const MCU_KW_DOC = {
  void: 'No value. The return type of setup(), loop() and every builtin that acts.',
  int: 'A whole number.',
  long: 'The same type as int — this machine has one integer width.',
  byte: 'The same type as int.',
  char: 'The same type as int.',
  bool: 'The same type as int. 0 is false, anything else is true.',
  boolean: 'The same type as int.',
  float: 'A number with a fractional part.',
  double: 'The same type as float — this machine has one float width.',
  if: 'Runs the block when the condition is not zero.',
  else: 'Runs when the if above it did not.',
  while: 'Repeats while the condition is not zero.',
  for: 'init, condition, step — the counting loop.',
  return: 'Leaves the function, with a value if it has one.',
  break: 'Leaves the innermost loop.',
  continue: 'Skips to the next turn of the innermost loop.',
};

const MCU_GLOBALS = [
  fn('pinMode', '(pin, mode) -> void', 'Sets a pin to INPUT, OUTPUT or INPUT_PULLUP. A pin must be an OUTPUT before digitalWrite or analogWrite will drive it.'),
  fn('digitalWrite', '(pin, value) -> void', 'Drives an OUTPUT pin to HIGH or LOW.'),
  fn('analogWrite', '(pin, duty) -> void', 'Drives an OUTPUT pin at a duty between 0 and 255, which the solver sees as that fraction of the supply.'),
  fn('digitalRead', '(pin) -> int', 'Reads a pin as HIGH or LOW.', 'int'),
  fn('analogRead', '(pin) -> int', 'Reads a pin through its converter, 0 to 1023. Only the A pins have one.', 'int'),
  fn('millis', '() -> int', 'Milliseconds since the sketch started.', 'int'),
  fn('micros', '() -> int', 'Microseconds since the sketch started.', 'int'),
  fn('delay', '(ms) -> void', 'Waits, in milliseconds. Time here is the transient the canvas is solving, not real time.'),
  fn('delayMicroseconds', '(us) -> void', 'Waits, in microseconds.'),
  fn('print', '(value, ...) -> void', 'Writes to the console under the panel, with no newline.'),
  fn('println', '(value, ...) -> void', 'Writes to the console under the panel and starts a new line.'),
  fn('map', '(x, inLo, inHi, outLo, outHi) -> int', 'Rescales x from one range to another.', 'int'),
  fn('constrain', '(x, lo, hi) -> int', 'Clamps x between lo and hi.', 'int'),
  fn('min', '(a, b) -> int', 'The smaller of two numbers.', 'int'),
  fn('max', '(a, b) -> int', 'The larger of two numbers.', 'int'),
  fn('abs', '(x) -> int', 'The magnitude, sign dropped.', 'int'),
  fn('sqrt', '(x) -> float', 'The square root.', 'float'),
  fn('pow', '(x, y) -> float', 'x raised to the power y.', 'float'),
  fn('sin', '(x) -> float', 'Sine, in radians.', 'float'),
  fn('cos', '(x) -> float', 'Cosine, in radians.', 'float'),
  fn('tan', '(x) -> float', 'Tangent, in radians.', 'float'),
  fn('floor', '(x) -> int', 'Rounded down.', 'int'),
  fn('ceil', '(x) -> int', 'Rounded up.', 'int'),
  fn('round', '(x) -> int', 'Rounded to the nearest whole number.', 'int'),
  konst('HIGH', 'int = 1', 'The supply rail.'),
  konst('LOW', 'int = 0', 'Ground.'),
  konst('INPUT', 'int = 0', 'A pin that reads and drives nothing.'),
  konst('OUTPUT', 'int = 1', 'A pin that drives the circuit.'),
  konst('INPUT_PULLUP', 'int = 2', 'A pin that reads, with the internal pull-up on.'),
  konst('true', 'int = 1', 'Anything other than zero is true.'),
  konst('false', 'int = 0', ''),
  konst('PI', 'float', '3.14159…'),
  konst('TWO_PI', 'float', 'Two whole turns of phase.'),
  konst('HALF_PI', 'float', 'A quarter turn.'),
  konst('A0', 'int = 14', 'The first analogue pin. A0 to A3 are the four with converters behind them.'),
  konst('A1', 'int = 15', 'An analogue pin.'),
  konst('A2', 'int = 16', 'An analogue pin.'),
  konst('A3', 'int = 17', 'An analogue pin.'),
];

/* The one name with a full stop in it. This subset has no objects — `Serial` is a
   name that happens to contain a dot, which is why only these two exist. */
const MCU_MODULES = {
  Serial: [
    meth('print', '(value, ...) -> void', 'The same as print().'),
    meth('println', '(value, ...) -> void', 'The same as println().'),
  ],
};

const MCU_SNIPPETS = [
  { n: 'setup', detail: 'the run-once function', doc: 'Called once, before loop().',
    body: 'void setup() {\n  $0\n}' },
  { n: 'loop', detail: 'the repeating function', doc: 'Called over and over until the transient ends.',
    body: 'void loop() {\n  $0\n}' },
  { n: 'if', detail: 'if statement', doc: '', body: 'if ($1) {\n  $0\n}' },
  { n: 'for', detail: 'counting loop', doc: '',
    body: 'for (int i = 0; i < $1; i++) {\n  $0\n}' },
  { n: 'while', detail: 'while loop', doc: '', body: 'while ($1) {\n  $0\n}' },
  { n: 'blink', detail: 'drive a pin on and off', doc: 'The smallest complete sketch that changes the circuit.',
    body: 'void setup() {\n  pinMode($1, OUTPUT);\n}\n\nvoid loop() {\n  digitalWrite($1, HIGH);\n  delay(200);\n  digitalWrite($1, LOW);\n  delay(200);\n}' },
];

const MCU_LIT = [
  [/^\d/, 'int'], [/^\d+\.\d/, 'float'], [/^(true|false|HIGH|LOW)\b/, 'int'],
];

function langOf(lang) {
  if (lang === 'python') {
    return { types: PY_TYPES, globals: PY_GLOBALS.concat(PY_EXCEPTIONS), modules: PY_MODULES,
             snippets: PY_SNIPPETS, keywords: PY_KW_WORDS, lits: PY_LIT, id: /[A-Za-z_]\w*/ };
  }
  if (lang === 'js') {
    return { types: JS_TYPES, globals: JS_GLOBALS, modules: JS_MODULES,
             snippets: JS_SNIPPETS, keywords: JS_KW_WORDS, lits: JS_LIT, id: /[A-Za-z_$][\w$]*/ };
  }
  if (lang === 'mcu') {
    /* No `types` table: this subset has no objects, so there are no members to offer
       after a dot on anything except Serial, which is a module here for exactly that
       reason. An empty object rather than a missing one, because the member-access
       path reads it without asking. */
    return { types: {}, globals: MCU_GLOBALS, modules: MCU_MODULES,
             snippets: MCU_SNIPPETS, keywords: MCU_KW_WORDS.concat(MCU_TYPE_WORDS),
             keywordDoc: MCU_KW_DOC, typeWords: MCU_TYPE_SET,
             lits: MCU_LIT, id: /[A-Za-z_]\w*/ };
  }
  return null;
}

/* the declared return type of a call like `foo(...)` or `obj.method(...)` */
function returnTypeOf(L, expr, table) {
  const call = expr.match(/^([A-Za-z_$][\w$]*)\s*\(/);
  if (call) {
    const name = call[1];
    const local = table && table.funcs[name];
    if (local && local.ret) return local.ret;
    for (const g of L.globals) if (g.n === name && g.ret) return g.ret;
    if (L.types[name]) return name;                    /* str(x), list(x) */
    if (table && table.classes[name]) return '@' + name;
  }
  const dotted = expr.match(/^([A-Za-z_$][\w$]*)\.([A-Za-z_$][\w$]*)\s*\(/);
  if (dotted) {
    const mod = L.modules[dotted[1]] || (table && table.imports[dotted[1]] && L.modules[table.imports[dotted[1]]]);
    if (mod) { for (const m of mod) if (m.n === dotted[2] && m.ret) return m.ret; }
    const recv = table && table.vars[dotted[1]];
    if (recv && L.types[recv.type]) {
      for (const m of L.types[recv.type].members) if (m.n === dotted[2] && m.ret) return m.ret;
    }
  }
  return '';
}

function inferType(L, expr, table) {
  const e = String(expr || '').trim();
  if (!e) return '';
  for (const [re, t] of L.lits) if (re.test(e)) return t;
  const ret = returnTypeOf(L, e, table);
  if (ret) return ret;
  /* a bare copy of another name keeps its type */
  const bare = e.match(/^([A-Za-z_$][\w$]*)\s*$/);
  if (bare && table && table.vars[bare[1]]) return table.vars[bare[1]].type;
  if (/^\[.*for .* in /.test(e)) return 'list';
  if (/=>|function\s*\(/.test(e)) return 'callable';
  if (/^await /.test(e)) return inferType(L, e.replace(/^await\s+/, ''), table);
  return '';
}

/* the element type of an iterable, for `for x in xs` */
function elementType(L, containerType) {
  if (containerType === 'str') return 'str';
  if (containerType === 'string') return 'string';
  return '';
}

function analyze(code, lang) {
  const L = langOf(lang);
  const table = { vars: {}, funcs: {}, classes: {}, imports: {}, attrs: {} };
  if (!L) return table;
  const lines = String(code || '').split('\n');
  const put = function (name, type, kind, detail) {
    if (!name || (L.keywords.indexOf(name) !== -1)) return;
    const prev = table.vars[name];
    if (prev && prev.type && !type) return;
    table.vars[name] = { type: type || '', k: kind || K.VAR, detail: detail || type || '' };
  };

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const line = raw.replace(/\s+$/, '');
    if (!line.trim()) continue;

    if (lang === 'python') {
      let m;
      if ((m = line.match(/^\s*def\s+([A-Za-z_]\w*)\s*\(([^)]*)\)\s*(?:->\s*([A-Za-z_]\w*))?/))) {
        const params = m[2].split(',').map(function (x) { return x.trim(); }).filter(Boolean);
        table.funcs[m[1]] = { params: params, ret: m[3] || '', doc: '' };
        params.forEach(function (raw2) {
          const pm = raw2.match(/^\*{0,2}([A-Za-z_]\w*)\s*(?::\s*([A-Za-z_]\w*))?/);
          if (pm && pm[1] !== 'self' && pm[1] !== 'cls') put(pm[1], pm[2] || '', K.PARAM, pm[2] || 'parameter');
        });
        continue;
      }
      if ((m = line.match(/^\s*class\s+([A-Za-z_]\w*)/))) { table.classes[m[1]] = { members: [] }; continue; }
      if ((m = line.match(/^\s*self\.([A-Za-z_]\w*)\s*=\s*(.+)$/))) {
        table.attrs[m[1]] = { type: inferType(L, m[2], table), k: K.FIELD };
        continue;
      }
      if ((m = line.match(/^\s*(?:from\s+([A-Za-z_][\w.]*)\s+)?import\s+(.+)$/))) {
        const from = m[1];
        m[2].split(',').forEach(function (part) {
          const pm = part.trim().match(/^([A-Za-z_][\w.]*)(?:\s+as\s+([A-Za-z_]\w*))?$/);
          if (!pm) return;
          const alias = pm[2] || pm[1].split('.')[0];
          table.imports[alias] = from || pm[1].split('.')[0];
        });
        continue;
      }
      if ((m = line.match(/^\s*with\s+(.+?)\s+as\s+([A-Za-z_]\w*)\s*:/))) {
        put(m[2], inferType(L, m[1], table), K.VAR); continue;
      }
      if ((m = line.match(/^\s*for\s+([A-Za-z_][\w,\s]*?)\s+in\s+(.+?):\s*$/))) {
        const names = m[1].split(',').map(function (x) { return x.trim(); });
        const src = m[2].trim();
        const srcType = inferType(L, src, table);
        names.forEach(function (n2, idx) {
          let t = '';
          if (names.length === 1) t = elementType(L, srcType) || (/^enumerate\(/.test(src) ? '' : '');
          else if (idx === 0 && /^enumerate\(/.test(src)) t = 'int';
          put(n2, t, K.VAR, 'loop variable');
        });
        continue;
      }
      if ((m = line.match(/^\s*except\s+[\w.]+\s+as\s+([A-Za-z_]\w*)/))) { put(m[1], '', K.VAR, 'exception'); continue; }
      if ((m = line.match(/^\s*([A-Za-z_]\w*)\s*(?::\s*([A-Za-z_]\w*))?\s*=\s*(.+)$/)) && !/[=!<>]=$/.test(m[0])) {
        const t = m[2] || inferType(L, m[3], table);
        const isConst = m[1] === m[1].toUpperCase() && /[A-Z]/.test(m[1]);
        put(m[1], t, isConst ? K.CONST : K.VAR, t || (isConst ? 'constant' : ''));
        continue;
      }
    } else {
      let m;
      if ((m = line.match(/^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)/))) {
        table.funcs[m[1]] = { params: m[2].split(',').map(function (x) { return x.trim(); }).filter(Boolean), ret: '', doc: '' };
        table.funcs[m[1]].params.forEach(function (pp) {
          const pm = pp.match(/^\.{0,3}([A-Za-z_$][\w$]*)/);
          if (pm) put(pm[1], '', K.PARAM, 'parameter');
        });
        continue;
      }
      if ((m = line.match(/^\s*(?:export\s+)?class\s+([A-Za-z_$][\w$]*)/))) { table.classes[m[1]] = { members: [] }; continue; }
      if ((m = line.match(/^\s*(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>/))) {
        table.funcs[m[1]] = { params: m[2].split(',').map(function (x) { return x.trim(); }).filter(Boolean), ret: '', doc: '' };
        table.funcs[m[1]].params.forEach(function (pp) {
          const pm = pp.match(/^\.{0,3}([A-Za-z_$][\w$]*)/);
          if (pm) put(pm[1], '', K.PARAM, 'parameter');
        });
        continue;
      }
      if ((m = line.match(/^\s*(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(.+?);?\s*$/))) {
        const t = inferType(L, m[2], table);
        const isConst = /^\s*const\b/.test(line) && m[1] === m[1].toUpperCase() && /[A-Z]/.test(m[1]);
        put(m[1], t, isConst ? K.CONST : K.VAR, t);
        continue;
      }
      if ((m = line.match(/^\s*(?:const|let|var)\s*\{([^}]*)\}\s*=/))) {
        m[1].split(',').forEach(function (x) {
          const pm = x.trim().match(/^([A-Za-z_$][\w$]*)/);
          if (pm) put(pm[1], '', K.VAR, 'destructured');
        });
        continue;
      }
      if ((m = line.match(/^\s*for\s*\(\s*(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s+of\s+(.+?)\)/))) {
        put(m[1], '', K.VAR, 'loop variable'); continue;
      }
      if ((m = line.match(/^\s*this\.([A-Za-z_$][\w$]*)\s*=\s*(.+)$/))) {
        table.attrs[m[1]] = { type: inferType(L, m[2], table), k: K.FIELD };
        continue;
      }
    }
  }
  return table;
}

/* ================================================================ completion */
const Complete = (function () {

  /* --- fuzzy subsequence match, VS Code style ------------------------------ */
  function score(name, query) {
    if (!query) return { ok: true, s: 0, hits: [] };
    const n = name.toLowerCase(), q = query.toLowerCase();
    if (n === q) return { ok: true, s: 1000, hits: rangeOf(0, query.length) };
    if (n.indexOf(q) === 0) return { ok: true, s: 900 - name.length, hits: rangeOf(0, query.length) };
    /* camelCase / snake_case initials: "qs" matches querySelector */
    const initials = [];
    for (let i = 0; i < name.length; i++) {
      if (i === 0 || /[._-]/.test(name[i - 1]) || (/[A-Z]/.test(name[i]) && /[a-z]/.test(name[i - 1] || ''))) initials.push(i);
    }
    let ii = 0, ih = [];
    for (const idx of initials) {
      if (ii < q.length && name[idx].toLowerCase() === q[ii]) { ih.push(idx); ii++; }
    }
    if (ii === q.length) return { ok: true, s: 700 - name.length, hits: ih };
    /* plain subsequence */
    let j = 0; const hits = [];
    for (let i = 0; i < n.length && j < q.length; i++) if (n[i] === q[j]) { hits.push(i); j++; }
    if (j === q.length) {
      const spread = hits[hits.length - 1] - hits[0];
      return { ok: true, s: 400 - spread - name.length, hits: hits };
    }
    const at = n.indexOf(q);
    if (at > 0) return { ok: true, s: 500 - at - name.length, hits: rangeOf(at, query.length) };
    return { ok: false, s: 0, hits: [] };
  }
  function rangeOf(start, len) { const a = []; for (let i = 0; i < len; i++) a.push(start + i); return a; }

  /* --- caret context ------------------------------------------------------- */
  function lineInfo(code, pos) {
    const ls = code.lastIndexOf('\n', pos - 1) + 1;
    return { start: ls, text: code.slice(ls, pos) };
  }

  /* Is the caret inside a string or comment? Scanning the line is enough for the
     single-line cases that matter, and multi-line strings are handled by counting
     triple quotes before the caret. */
  function inStringOrComment(code, pos, lang) {
    if (lang === 'python') {
      const before = code.slice(0, pos);
      const triples = (before.match(/'{3}|"{3}/g) || []).length;
      if (triples % 2 === 1) return true;
    }
    const li = lineInfo(code, pos);
    let q = '';
    for (let i = 0; i < li.text.length; i++) {
      const c = li.text[i];
      if (q) { if (c === '\\') i++; else if (c === q) q = ''; continue; }
      if (c === '"' || c === "'" || (lang === 'js' && c === '`')) { q = c; continue; }
      if (lang === 'python' && c === '#') return true;
      if (lang === 'js' && c === '/' && li.text[i + 1] === '/') return true;
      if (lang === 'css' && c === '/' && li.text[i + 1] === '*') return true;
    }
    return !!q;
  }

  /* the receiver expression immediately left of a trailing dot */
  function receiverBefore(code, dotAt, L) {
    let i = dotAt - 1, depth = 0;
    while (i >= 0) {
      const c = code[i];
      if (c === ')' || c === ']') { depth++; i--; continue; }
      if (c === '(' || c === '[') { if (depth === 0) break; depth--; i--; continue; }
      if (depth > 0) { i--; continue; }
      if (/[A-Za-z0-9_$.]/.test(c)) { i--; continue; }
      if (c === '"' || c === "'" || c === '`') {
        const open = code.lastIndexOf(c, i - 1);
        if (open >= 0) { i = open - 1; continue; }
      }
      break;
    }
    return code.slice(i + 1, dotAt).trim();
  }

  function typeOfExpr(L, expr, table) {
    const e = expr.trim();
    if (!e) return '';
    if (/^(['"]).*\1$/.test(e) || /^[fF](['"])/.test(e)) return L === langOf('python') ? 'str' : 'string';
    for (const [re, t] of L.lits) if (re.test(e)) return t;
    const v = table.vars[e];
    if (v && v.type) return v.type;
    if (table.attrs[e.replace(/^(self|this)\./, '')] && /^(self|this)\./.test(e)) {
      return table.attrs[e.replace(/^(self|this)\./, '')].type;
    }
    const ret = returnTypeOf(L, e + '(', table) || returnTypeOf(L, e, table);
    if (ret) return ret;
    /* chained: a.b().c() — resolve left to right */
    const chain = e.match(/^(.*)\.([A-Za-z_$][\w$]*)\s*\(\s*\)?$/);
    if (chain) {
      const base = typeOfExpr(L, chain[1], table);
      if (base && L.types[base]) {
        for (const m of L.types[base].members) if (m.n === chain[2] && m.ret) return m.ret;
      }
    }
    const idx = e.match(/^(.*)\[[^\]]*\]$/);
    if (idx) {
      const base = typeOfExpr(L, idx[1], table);
      if (base === 'str' || base === 'string') return base;
    }
    return '';
  }

  function memberPool(L, type, table) {
    if (!type) return null;
    if (type.charAt(0) === '@') {                       /* a class defined in this file */
      const cls = type.slice(1);
      const out = [];
      for (const k in table.attrs) out.push(mem(k, K.FIELD, table.attrs[k].type || 'field', 'Defined on ' + cls + '.', ''));
      return out;
    }
    if (L.types[type]) return L.types[type].members.slice();
    return null;
  }

  /* --- the enclosing call, for a signature hint ---------------------------- */
  function enclosingCall(code, pos) {
    let depth = 0;
    for (let i = pos - 1; i >= 0 && pos - i < 2000; i--) {
      const c = code[i];
      if (c === ')') depth++;
      else if (c === '(') {
        if (depth === 0) {
          const before = code.slice(Math.max(0, i - 80), i);
          const m = before.match(/([A-Za-z_$][\w$.]*)\s*$/);
          if (m) {
            const args = code.slice(i + 1, pos);
            let arg = 0, d2 = 0;
            for (const ch of args) {
              if (ch === '(' || ch === '[' || ch === '{') d2++;
              else if (ch === ')' || ch === ']' || ch === '}') d2--;
              else if (ch === ',' && d2 === 0) arg++;
            }
            return { name: m[1], argIndex: arg };
          }
          return null;
        }
        depth--;
      } else if (c === '\n' && depth === 0) return null;
    }
    return null;
  }

  function lookupSignature(L, name, table) {
    const local = table.funcs[name];
    if (local) {
      return { label: name + '(' + local.params.join(', ') + ')', doc: local.doc || 'Defined in this file.', params: local.params };
    }
    const dot = name.split('.');
    if (dot.length === 2) {
      const mod = L.modules[dot[0]] || L.modules[table.imports[dot[0]]];
      if (mod) for (const m of mod) if (m.n === dot[1]) return { label: name + m.detail, doc: m.doc, params: splitParams(m.detail) };
      const recv = table.vars[dot[0]];
      if (recv && L.types[recv.type]) {
        for (const m of L.types[recv.type].members) if (m.n === dot[1]) return { label: name + m.detail, doc: m.doc, params: splitParams(m.detail) };
      }
    }
    for (const g of L.globals) if (g.n === name) return { label: name + g.detail, doc: g.doc, params: splitParams(g.detail) };
    return null;
  }
  function splitParams(detail) {
    const m = String(detail || '').match(/^\(([^)]*)\)/);
    if (!m || !m[1].trim()) return [];
    return m[1].split(',').map(function (x) { return x.trim(); });
  }

  return {
    score: score, analyze: analyze, langOf: langOf,
    inStringOrComment: inStringOrComment, receiverBefore: receiverBefore,
    typeOfExpr: typeOfExpr, memberPool: memberPool,
    enclosingCall: enclosingCall, lookupSignature: lookupSignature,
    lineInfo: lineInfo,
  };
})();

/* ---------- html editing ----------
   Markup is mostly brackets, so an editor that does not help with them makes web
   work feel worse than Python work. These tables drive tag/attribute completion and
   the automatic closing of < > and </tag>. */
const HTML_VOID = {};
'area base br col embed hr img input link meta param source track wbr'.split(' ')
  .forEach(function (n) { HTML_VOID[n] = 1; });

/* Void elements that are almost always bare — the caret belongs after them. Every
   other void element (img, input, link...) is about to be given attributes, so the
   caret stays inside the tag. */
const HTML_VOID_BARE = { br: 1, wbr: 1, hr: 1 };

const HTML_TAGS = (
  /* everyday markup first — the completion sort is stable, so this is the tie-break */
  'div p a span button img input ul ol li h1 h2 h3 form label section header footer nav ' +
  'br table tr td th script link meta style textarea select option main article aside ' +
  /* then the rest, alphabetically */
  'abbr address area audio b base blockquote body canvas caption cite code col colgroup ' +
  'datalist dd details dialog dl dt em embed fieldset figcaption figure h4 h5 h6 head ' +
  'hgroup hr html i iframe legend map mark menu meter noscript object optgroup output ' +
  'picture pre progress q s samp small source strong sub summary sup svg tbody template ' +
  'tfoot thead time title track u var video wbr').split(' ');

/* value:false means it is a boolean attribute — no ="" is inserted */
const HTML_ATTRS = (function () {
  const bare = 'disabled checked selected readonly required hidden autofocus multiple novalidate open loop muted controls autoplay defer async'.split(' ');
  const valued = ('class id style title href src alt type value name placeholder rel target ' +
    'width height min max step pattern maxlength rows cols for action method enctype colspan ' +
    'rowspan role tabindex lang data-id aria-label aria-hidden aria-live onclick oninput ' +
    'onchange onsubmit onkeydown srcset sizes loading download content charset viewBox fill stroke').split(' ');
  const out = [];
  valued.forEach(function (n) { out.push({ n: n, k: 'a', p: false, v: true }); });
  bare.forEach(function (n) { out.push({ n: n, k: 'a', p: false, v: false }); });
  return out;
})();

/* Which unclosed element are we inside at `upto`? Drives </ completion. */
function htmlOpenStack(text) {
  const re = /<\/?([A-Za-z][A-Za-z0-9-]*)\b[^>]*?(\/?)>/g;
  const stack = [];
  let m;
  while ((m = re.exec(text)) !== null) {
    const name = m[1].toLowerCase();
    if (text[m.index + 1] === '/') {
      const i = stack.lastIndexOf(name);
      if (i !== -1) stack.length = i;
    } else if (!(m[2] === '/' || HTML_VOID[name])) {
      stack.push(name);
    }
  }
  return stack;
}

/* script and style bodies are JavaScript and CSS, where "<" is a comparison and
   must not be paired. (Tag names are written bare here on purpose: a literal
   angle-bracket-script inside this file would break the single-file build.) */
function htmlInRawBlock(text) {
  const re = /<(script|style)\b[^>]*>|<\/(script|style)\s*>/gi;
  let depth = null, m;
  while ((m = re.exec(text)) !== null) depth = m[0][1] === '/' ? null : m[0].slice(1).split(/[\s>]/)[0].toLowerCase();
  return depth;
}

/* Where in the markup is the caret? */
function htmlWhere(v, pos) {
  const before = v.slice(0, pos);
  const lt = before.lastIndexOf('<');
  const gt = before.lastIndexOf('>');
  if (lt === -1 || gt > lt) return { at: 'text', raw: htmlInRawBlock(before) };
  const inner = before.slice(lt);
  /* the literal four characters would put the host page's parser into script-data
     escaped state, so the sequence is spelled out — see the same trick at 'cm' above */
  if (inner.indexOf('<!\x2d-') === 0) return { at: 'comment' };
  if (/^<\/[A-Za-z0-9-]*$/.test(inner)) return { at: 'closetag', lt: lt };
  if (/^<[A-Za-z0-9-]*$/.test(inner)) return { at: 'tagname', tag: inner.slice(1), lt: lt };
  const nm = inner.match(/^<([A-Za-z][A-Za-z0-9-]*)/);
  const tag = nm ? nm[1].toLowerCase() : '';
  let q = '';
  for (let i = 1; i < inner.length; i++) {
    const c = inner[i];
    if (q) { if (c === q) q = ''; continue; }
    if (c === '"' || c === "'") q = c;
  }
  return { at: q ? 'attrvalue' : 'attr', tag: tag, lt: lt };
}


const HTML_ATTR_DOC = {
  class: 'One or more class names, separated by spaces.',
  id: 'A unique identifier for this element.',
  href: 'The URL a link points at.',
  src: 'The URL of the resource to load.',
  alt: 'Text shown when an image cannot be displayed — required for accessibility.',
  type: 'The kind of control or resource.',
  value: 'The current value of a form control.',
  placeholder: 'Hint text shown while a field is empty. Not a substitute for a label.',
  for: 'The id of the control this label describes.',
  disabled: 'Makes a control non-interactive.',
  required: 'The form will not submit while this field is empty.',
  role: 'Overrides the implicit accessibility role. Prefer the right element instead.',
};
const HTML_TAG_DOC = {
  div: 'A generic block container with no meaning of its own.',
  span: 'A generic inline container with no meaning of its own.',
  section: 'A thematic grouping, normally with a heading.',
  article: 'A self-contained piece that would still make sense on its own.',
  header: 'Introductory content for its nearest section.',
  footer: 'Closing content for its nearest section.',
  nav: 'A block of navigation links.',
  main: 'The dominant content of the document. Only one per page.',
  p: 'A paragraph of text.',
  a: 'A hyperlink. Needs an href to be focusable.',
  img: 'An image. Always give it an alt.',
  ul: 'An unordered list; its children must be li.',
  ol: 'An ordered list; its children must be li.',
  li: 'One item in a list.',
  button: 'A control that does something when pressed.',
  input: 'A form field. The type attribute decides which kind.',
  label: 'A caption for a form control — pair it with for.',
  form: 'A group of controls that submit together.',
  table: 'Tabular data. Not for layout.',
  h1: 'The top-level heading. One per page.',
  script: 'Runs JavaScript, or loads it with src.',
  style: 'CSS for this document.',
  link: 'Relates an external resource, most often a stylesheet.',
};

/* ================================================================ suggest */
Complete.suggest = function (code, pos, lang, extraCode) {
  const out = { from: pos, to: pos, items: [], signature: null, context: 'none' };
  const L = Complete.langOf(lang);

  /* ---- word under the caret ---- */
  const idRe = lang === 'html' ? /[A-Za-z0-9_-]/ : lang === 'css' ? /[A-Za-z-]/ : (L ? L.id : /[A-Za-z0-9_]/);
  const isId = function (c) { return c !== undefined && (lang === 'html' || lang === 'css' ? idRe.test(c) : new RegExp(L.id.source.replace(/^\[/, '[').replace(/\*$/, '')).test(c) || /[A-Za-z0-9_$]/.test(c)); };
  let ws = pos;
  while (ws > 0 && /[A-Za-z0-9_$-]/.test(code[ws - 1])) {
    if (lang !== 'html' && lang !== 'css' && code[ws - 1] === '-') break;
    ws--;
  }
  const word = code.slice(ws, pos);
  out.from = ws;

  const add = function (e, sortBoost) {
    const sc = Complete.score(e.n, word);
    if (!sc.ok) return;
    out.items.push({
      n: e.n, k: e.k || K.VAR, detail: e.detail || '', doc: e.doc || '',
      body: e.body || '', insert: e.insert || '', hits: sc.hits,
      s: sc.s + (sortBoost || 0),
    });
  };
  const addAll = function (list, boost) { if (list) for (const e of list) add(e, boost); };

  /* ================= html ================= */
  if (lang === 'html') {
    const w = htmlWhere(code, ws);
    out.context = w.at;
    if (w.at === 'comment' || w.at === 'attrvalue') return out;
    if (w.at === 'tagname' || w.at === 'closetag') {
      const near = w.at === 'closetag' ? htmlOpenStack(code.slice(0, w.lt)) : [];
      const top = near.length ? near[near.length - 1] : '';
      HTML_TAGS.forEach(function (n) {
        add({ n: n, k: K.TYPE, detail: HTML_VOID[n] ? 'void element' : 'element',
              doc: HTML_TAG_DOC[n] || '' }, n === top ? 2000 : 0);
      });
      return out;
    }
    if (w.at === 'attr') {
      HTML_ATTRS.forEach(function (a) {
        add({ n: a.n, k: K.PROP, detail: a.v === false ? 'boolean attribute' : 'attribute',
              doc: HTML_ATTR_DOC[a.n] || '', insert: a.v === false ? a.n : a.n + '=""' });
      });
      return out;
    }
    /* plain text: tags at the start of a line, plus snippets */
    const ls = code.lastIndexOf('\n', ws - 1) + 1;
    if (!/^[ \t]*$/.test(code.slice(ls, ws)) || w.raw) return out;
    HTML_SNIPPETS.forEach(function (sn) { add({ n: sn.n, k: K.SNIP, detail: sn.detail, doc: sn.doc, body: sn.body }, 120); });
    HTML_TAGS.forEach(function (n) {
      add({ n: n, k: K.TYPE, detail: HTML_VOID[n] ? 'void element' : 'element', doc: HTML_TAG_DOC[n] || '' });
    });
    out.context = 'text';
    return out;
  }

  /* ================= css ================= */
  if (lang === 'css') {
    const li = Complete.lineInfo(code, ws);
    out.context = /:/.test(li.text) ? 'value' : 'property';
    if (out.context === 'property') {
      CSS_SNIPPETS.forEach(function (sn) { add({ n: sn.n, k: K.SNIP, detail: sn.detail, doc: sn.doc, body: sn.body }, 120); });
      CSS_PROPS.forEach(function (e) { add({ n: e.n, k: K.PROP, detail: e.detail, doc: e.doc, insert: e.n + ': ' }); });
    } else {
      const propName = (li.text.match(/([-\w]+)\s*:/) || [])[1];
      const decl = CSS_PROPS.find(function (e) { return e.n === propName; });
      if (decl) {
        decl.detail.split('|').map(function (x) { return x.trim(); })
          .filter(function (x) { return /^[a-z-]+$/.test(x); })
          .forEach(function (v) { add({ n: v, k: K.CONST, detail: propName, doc: decl.doc }); });
      }
    }
    out.items.sort(function (a, b) { return b.s - a.s; });
    out.items = out.items.slice(0, 60);
    return out;
  }

  if (!L) return out;
  if (Complete.inStringOrComment(code, ws, lang)) return out;

  const table = Complete.analyze(code + '\n' + (extraCode || ''), lang);
  const li = Complete.lineInfo(code, ws);

  /* ================= member access ================= */
  if (code[ws - 1] === '.') {
    out.context = 'member';
    const recv = Complete.receiverBefore(code, ws - 1, L);
    /* a module? */
    const modName = L.modules[recv] ? recv : (table.imports[recv] && L.modules[table.imports[recv]] ? table.imports[recv] : '');
    if (modName) {
      addAll(L.modules[modName]);
      out.items.sort(function (a, b) { return b.s - a.s; });
      return out;
    }
    if (/^(self|this)$/.test(recv)) {
      for (const k in table.attrs) add({ n: k, k: K.FIELD, detail: table.attrs[k].type || 'field', doc: 'Set on the instance.' });
      for (const k in table.funcs) add({ n: k, k: K.METHOD, detail: '(' + table.funcs[k].params.filter(function (p2) { return !/^(self|cls)$/.test(p2); }).join(', ') + ')', doc: 'Defined in this file.' });
      out.items.sort(function (a, b) { return b.s - a.s; });
      return out;
    }
    const t = Complete.typeOfExpr(L, recv, table);
    const pool = Complete.memberPool(L, t, table);
    if (pool) {
      addAll(pool);
      out.signature = t ? { label: recv + ': ' + ((L.types[t] && L.types[t].label) || t), doc: '' } : null;
    } else {
      /* unknown receiver — offer everything that exists on any known type, marked
         as such, rather than nothing at all */
      const seen = {};
      for (const tn in L.types) for (const m2 of L.types[tn].members) {
        if (seen[m2.n]) continue; seen[m2.n] = 1;
        add({ n: m2.n, k: m2.k, detail: m2.detail, doc: m2.doc });
      }
    }
    out.items.sort(function (a, b) { return b.s - a.s; });
    out.items = out.items.slice(0, 60);
    return out;
  }

  /* ================= python import ================= */
  if (lang === 'python') {
    let m;
    if ((m = li.text.match(/^\s*(?:from\s+([A-Za-z_]\w*)\s+)?import\s+[\w,\s]*$/))) {
      out.context = 'import';
      if (m[1]) addAll(L.modules[m[1]] || []);
      else for (const name in L.modules) add({ n: name, k: K.MOD, detail: 'module', doc: 'Standard library module.' });
      out.items.sort(function (a, b) { return b.s - a.s; });
      return out;
    }
    if (/^\s*from\s+[\w]*$/.test(li.text)) {
      out.context = 'import';
      for (const name in L.modules) add({ n: name, k: K.MOD, detail: 'module', doc: 'Standard library module.' });
      out.items.sort(function (a, b) { return b.s - a.s; });
      return out;
    }
    if (/\b(raise|except)\s+[\w]*$/.test(li.text)) {
      out.context = 'exception';
      addAll(PY_EXCEPTIONS, 200);
      out.items.sort(function (a, b) { return b.s - a.s; });
      return out;
    }
    if (/^\s*(def|class)\s+[\w]*$/.test(li.text)) { out.context = 'declaration'; return out; }
  } else {
    if (/^\s*(function|class)\s+[\w$]*$/.test(li.text)) { out.context = 'declaration'; return out; }
    if (/\bnew\s+[\w$]*$/.test(li.text)) {
      out.context = 'constructor';
      for (const g of L.globals) if (g.k === K.TYPE) add(g, 300);
      for (const c in table.classes) add({ n: c, k: K.TYPE, detail: 'class', doc: 'Defined in this file.' }, 400);
      out.items.sort(function (a, b) { return b.s - a.s; });
      return out;
    }
  }

  /* ================= inside a call ================= */
  const call = Complete.enclosingCall(code, pos);
  if (call) {
    const sig = Complete.lookupSignature(L, call.name, table);
    if (sig) {
      out.signature = { label: sig.label, doc: sig.doc, active: call.argIndex, params: sig.params };
      out.context = 'argument';
      /* python keyword arguments for this call */
      if (lang === 'python') {
        sig.params.forEach(function (p2) {
          const nm = p2.split('=')[0].trim().replace(/^\*+/, '');
          if (nm && /^[A-Za-z_]\w*$/.test(nm) && p2.indexOf('=') !== -1) {
            add({ n: nm + '=', k: K.PARAM, detail: p2, doc: 'Keyword argument of ' + call.name + '().' }, 260);
          }
        });
      }
    }
  }

  /* ================= everything in scope ================= */
  if (out.context === 'none') out.context = 'word';
  for (const name in table.vars) {
    const v = table.vars[name];
    add({ n: name, k: v.k, detail: v.detail || v.type || '', doc: v.k === K.PARAM ? 'A parameter of the enclosing function.' : 'Defined in this file.' }, 300);
  }
  for (const name in table.funcs) {
    add({ n: name, k: K.FN, detail: '(' + table.funcs[name].params.join(', ') + ')', doc: 'Defined in this file.' }, 320);
  }
  for (const name in table.classes) {
    add({ n: name, k: K.TYPE, detail: 'class', doc: 'Defined in this file.' }, 320);
  }
  for (const alias in table.imports) {
    add({ n: alias, k: K.MOD, detail: 'module ' + table.imports[alias], doc: 'Imported in this file.' }, 280);
  }
  addAll(L.globals, 100);
  L.keywords.forEach(function (kw) {
    /* Optional, and absent for python and js, which have no aliases worth a sentence
       and whose keywords are the ones every learner already met. */
    const isType = !!(L.typeWords && L.typeWords[kw]);
    add({ n: kw, k: isType ? K.TYPE : K.KW, detail: isType ? 'type' : 'keyword',
          doc: (L.keywordDoc && L.keywordDoc[kw]) || '' }, 40);
  });
  L.snippets.forEach(function (sn) { add({ n: sn.n, k: K.SNIP, detail: sn.detail, doc: sn.doc, body: sn.body }, 160); });

  /* de-duplicate, best score wins */
  const best = {};
  for (const it of out.items) {
    if (!best[it.n] || best[it.n].s < it.s) best[it.n] = it;
  }
  out.items = Object.keys(best).map(function (k2) { return best[k2]; });
  out.items.sort(function (a, b) { return b.s - a.s || a.n.length - b.n.length; });
  out.items = out.items.slice(0, 60);
  return out;
};

Complete.kindLabel = function (k) { return KIND_LABEL[k] || k; };
Complete.kindMark = function (k) { return KIND_MARK[k] || '\u25cb'; };
