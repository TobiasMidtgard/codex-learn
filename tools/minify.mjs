/**
 * minify.mjs — take the comments and the indentation out of what ships.
 *
 * The source files are a quarter to a half comment by bytes, and the comments are
 * the repository's memory: they stay exactly as they are. What a browser has to
 * download and parse before the first paint is another matter, so the build runs
 * the scripts and the stylesheet through this before inlining them.
 *
 * This is deliberately NOT a minifier in the renaming sense. It does three things
 * and no more: drops comments, drops the whitespace at the start of every line,
 * and collapses runs of blank lines. Every newline that carried a token survives,
 * so automatic semicolon insertion sees exactly the line structure it saw in the
 * source, and a stack trace's line numbers stay recognisable to within the lines
 * removed. Renaming and expression rewriting need a real parser and a dependency,
 * and the repository has neither.
 *
 * The only hard part is knowing what is a comment. A `/*` inside a string, a
 * template literal or a regular expression is not one, and `/` starts a regular
 * expression or a division depending on what came before it. The tokenizer here
 * tracks all four, and tools/verify_minify.mjs proves the result has the same
 * token stream as the source and still parses.
 */

const PUNCT_BEFORE_REGEX = new Set(['(', ',', '=', ':', '[', '!', '&', '|', '?', '{', '}', ';',
  '+', '-', '*', '%', '<', '>', '~', '^', '/']);
const WORDS_BEFORE_REGEX = new Set(['return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete',
  'void', 'throw', 'case', 'do', 'else', 'yield', 'await']);

/* identifier characters, with every non-ASCII code unit treated as one — only the
   regex-or-division decision reads this, and a non-ASCII character is never an
   operator */
const isIdent = (ch) => /[A-Za-z0-9_$]/.test(ch) || ch.charCodeAt(0) > 127;

/**
 * Tokenise JavaScript into { t, v } — t is 'code' (a run of non-comment, non-string
 * source), 'str', 'tpl', 're', 'lc' (line comment) or 'bc' (block comment).
 * A template literal is one token including its `${}` parts.
 */
export function tokenizeJs(src) {
  const out = [];
  let i = 0;
  const n = src.length;
  let lastSig = '';          /* the last significant token text, for the regex decision */
  const push = (t, v) => { out.push({ t, v }); };

  function regexAllowed() {
    if (!lastSig) return true;
    if (PUNCT_BEFORE_REGEX.has(lastSig)) return true;
    if (WORDS_BEFORE_REGEX.has(lastSig)) return true;
    return false;
  }

  function readTemplate(start) {
    /* returns the index just past the closing backtick */
    let j = start + 1;
    while (j < n) {
      const ch = src[j];
      if (ch === '\\') { j += 2; continue; }
      if (ch === '`') return j + 1;
      if (ch === '$' && src[j + 1] === '{') {
        j += 2;
        let depth = 1;
        while (j < n && depth > 0) {
          const c = src[j];
          if (c === '\\') { j += 2; continue; }
          if (c === '`') { j = readTemplate(j); continue; }
          if (c === "'" || c === '"') { j = readString(j); continue; }
          if (c === '/' && src[j + 1] === '*') { j = src.indexOf('*/', j + 2); j = j < 0 ? n : j + 2; continue; }
          if (c === '/' && src[j + 1] === '/') { const e = src.indexOf('\n', j); j = e < 0 ? n : e; continue; }
          if (c === '{') depth++;
          else if (c === '}') depth--;
          j++;
        }
        continue;
      }
      j++;
    }
    return n;
  }
  function readString(start) {
    const q = src[start];
    let j = start + 1;
    while (j < n) {
      const ch = src[j];
      if (ch === '\\') { j += 2; continue; }
      if (ch === q || ch === '\n') return j + 1;
      j++;
    }
    return n;
  }
  function readRegex(start) {
    let j = start + 1;
    let cls = false;
    while (j < n) {
      const ch = src[j];
      if (ch === '\\') { j += 2; continue; }
      if (ch === '\n') return j;          /* not a regex after all; the verifier will notice */
      if (cls) { if (ch === ']') cls = false; }
      else if (ch === '[') cls = true;
      else if (ch === '/') { j++; while (j < n && isIdent(src[j])) j++; return j; }
      j++;
    }
    return n;
  }

  let codeStart = 0;
  const flushCode = (end) => { if (end > codeStart) push('code', src.slice(codeStart, end)); };

  while (i < n) {
    const ch = src[i], nx = src[i + 1];
    if (ch === '/' && nx === '/') {
      flushCode(i);
      let e = src.indexOf('\n', i); if (e < 0) e = n;
      push('lc', src.slice(i, e)); i = e; codeStart = i; continue;
    }
    if (ch === '/' && nx === '*') {
      flushCode(i);
      let e = src.indexOf('*/', i + 2); e = e < 0 ? n : e + 2;
      push('bc', src.slice(i, e)); i = e; codeStart = i; continue;
    }
    if (ch === "'" || ch === '"') {
      flushCode(i);
      const e = readString(i); push('str', src.slice(i, e)); lastSig = 'str'; i = e; codeStart = i; continue;
    }
    if (ch === '`') {
      flushCode(i);
      const e = readTemplate(i); push('tpl', src.slice(i, e)); lastSig = 'tpl'; i = e; codeStart = i; continue;
    }
    if (ch === '/' && regexAllowed()) {
      flushCode(i);
      const e = readRegex(i); push('re', src.slice(i, e)); lastSig = 're'; i = e; codeStart = i; continue;
    }
    /* ordinary code: track the last significant token */
    if (isIdent(ch)) {
      let j = i; while (j < n && isIdent(src[j])) j++;
      lastSig = src.slice(i, j); i = j; continue;
    }
    if (!/\s/.test(ch)) lastSig = ch;
    i++;
  }
  flushCode(n);
  return out;
}

/** The comparable stream: comments become a space, runs of code merge, and the
    whitespace inside code is normalised; strings, templates and regexes stay
    byte for byte. A comment that split a run of code in the source no longer
    splits it in the output, which is why the merge has to happen before the
    normalisation. */
export function significantJs(src) {
  const parts = [];
  const code = (s) => {
    if (parts.length && parts[parts.length - 1].code !== undefined) parts[parts.length - 1].code += s;
    else parts.push({ code: s });
  };
  for (const k of tokenizeJs(src)) {
    if (k.t === 'lc' || k.t === 'bc') code(' ');
    else if (k.t === 'code') code(k.v);
    else parts.push({ lit: k.v });
  }
  return parts.map((p) => (p.code !== undefined ? p.code.replace(/\s+/g, ' ').trim() : p.lit))
    .filter((v) => v !== '').join('');
}

export function stripJs(src) {
  const parts = [];
  for (const k of tokenizeJs(src)) {
    if (k.t === 'lc') continue;
    if (k.t === 'bc') {
      /* a block comment that spanned lines was a line of its own; keep one newline
         so a token on either side never joins the next line */
      if (k.v.includes('\n')) parts.push('\n');
      continue;
    }
    if (k.t === 'code') {
      parts.push(k.v.split('\n').map((line, idx) => (idx === 0 ? line : line.replace(/^[ \t]+/, ''))).join('\n'));
      continue;
    }
    parts.push(k.v);
  }
  let out = parts.join('');
  /* a line that is only whitespace, and any run of blank lines */
  out = out.replace(/[ \t]+\n/g, '\n').replace(/\n{2,}/g, '\n');
  /* the first line's own indentation, and a leading blank line */
  return out.replace(/^\s+/, '');
}

/**
 * CSS: comments outside strings, then leading whitespace. A `url(...)` with an
 * unquoted `/*` is not something this stylesheet writes, and the verifier would
 * catch it if it did.
 */
export function stripCss(src) {
  let out = '';
  let i = 0;
  const n = src.length;
  while (i < n) {
    const ch = src[i];
    if (ch === '"' || ch === "'") {
      let j = i + 1;
      while (j < n && src[j] !== ch) { if (src[j] === '\\') j++; j++; }
      out += src.slice(i, j + 1); i = j + 1; continue;
    }
    if (ch === '/' && src[i + 1] === '*') {
      const e = src.indexOf('*/', i + 2); i = e < 0 ? n : e + 2; continue;
    }
    out += ch; i++;
  }
  return out.split('\n').map((l) => l.replace(/^[ \t]+/, '').replace(/[ \t]+$/, ''))
    .filter((l) => l !== '').join('\n');
}

export function significantCss(src) {
  return stripCss(src).replace(/\s+/g, ' ').trim();
}
