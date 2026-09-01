/* ============ Codewright engine ============ */
'use strict';

/* ---------- utilities ---------- */
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
function dedent(s) {
  const lines = String(s).replace(/^\n+/, '').replace(/\s+$/, '').split('\n');
  let min = Infinity;
  for (const l of lines) { if (!l.trim()) continue; const n = l.match(/^[ \t]*/)[0].length; if (n < min) min = n; }
  if (!isFinite(min) || min === 0) return lines.join('\n');
  return lines.map(l => l.slice(min)).join('\n');
}
function debounce(fn, ms) { let t = null; return function () { const a = arguments; clearTimeout(t); t = setTimeout(() => fn.apply(null, a), ms); }; }
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

function langOfFile(name) {
  if (/\.py$/.test(name)) return 'python';
  if (/\.js$/.test(name)) return 'js';
  if (/\.css$/.test(name)) return 'css';
  if (/\.html?$/.test(name)) return 'html';
  return 'text';
}

/* ---------- content bundle ---------- */
let BUNDLE = {};
function parseBundle(raw) {
  const text = String(raw).replace(/<\\\/script/g, '<' + '/script').replace(/<\\!--/g, '<' + '!--');
  const parts = text.split(/^@@[ \t]+(\S+)[ \t]*$/m);
  const map = {};
  for (let i = 1; i < parts.length; i += 2) {
    map[parts[i]] = parts[i + 1].replace(/^\n+/, '').replace(/\s+$/, '');
  }
  return map;
}
function bundleFile(key) {
  if (!(key in BUNDLE)) return '# missing: ' + key + '\n';
  return BUNDLE[key] + '\n';
}

/* ---------- syntax highlighting ----------
   Colour is information, so tokens are split by role rather than by shape: a
   keyword that declares reads differently from one that branches, a name being
   defined from one being called, a parameter from a local. The classes are stable
   names the stylesheet maps to the palette. */
const Highlight = (function () {
  function span(cls, s) { return cls ? '<span class="tk-' + cls + '">' + esc(s) + '</span>' : esc(s); }

  function makeTokenizer(rules, flags) {
    const src = rules.map(function (r) { return '(' + r[0].source + ')'; }).join('|');
    const f = flags || 'gm';
    return function (code) {
      /* A fresh RegExp per call, because this has to be reentrant: an f-string or a
         template literal highlights the expression inside it with this very
         tokenizer, and a shared lastIndex would be clobbered by the nested call and
         restart the outer scan forever. */
      const re = new RegExp(src, f);
      let out = '', last = 0, m;
      while ((m = re.exec(code)) !== null) {
        if (m.index > last) out += esc(code.slice(last, m.index));
        let gi = 0;
        for (let k = 1; k < m.length; k++) { if (m[k] !== undefined) { gi = k - 1; break; } }
        const cls = rules[gi][1];
        out += (typeof cls === 'function') ? cls(m[0]) : span(cls, m[0]);
        last = m.index + m[0].length;
        if (m[0].length === 0) re.lastIndex++;
      }
      return out + esc(code.slice(last));
    };
  }

  const words = function (list) { return new RegExp('\\b(?:' + list.join('|') + ')\\b'); };

  /* escapes inside a string literal are worth seeing */
  function strBody(text, cls) {
    return String(text).replace(/\\(?:u\{[\da-fA-F]+\}|u[\da-fA-F]{4}|x[\da-fA-F]{2}|[\s\S])/g, function (esc2) {
      return '\x00' + esc2 + '\x01';
    }).split(/\x00|\x01/).map(function (part, i) {
      return i % 2 ? span('str-esc', part) : span(cls || 'str', part);
    }).join('');
  }

  /* an f-string or template literal: literal text is a string, {expr} is code */
  function interp(text, open, inner) {
    const re = open === '{' ? /\{\{|\}\}|\{([^{}]*)\}/g : /\$\{([^{}]*)\}/g;
    let out = '', last = 0, m;
    while ((m = re.exec(text)) !== null) {
      out += strBody(text.slice(last, m.index));
      if (m[1] === undefined) out += span('str', m[0]);        /* an escaped brace */
      else {
        out += span('interp-b', open === '{' ? '{' : '${') +
          inner(m[1]) + span('interp-b', '}');
      }
      last = m.index + m[0].length;
    }
    return out + strBody(text.slice(last));
  }

  /* ------------------------------------------------------------ python */
  const PY_CTL = ['if', 'elif', 'else', 'for', 'while', 'break', 'continue', 'return',
    'yield', 'pass', 'raise', 'try', 'except', 'finally', 'with', 'assert', 'await', 'async'];
  const PY_DECL = ['def', 'class', 'lambda', 'import', 'from', 'as', 'global', 'nonlocal', 'del'];
  const PY_OPW = ['and', 'or', 'not', 'in', 'is'];
  const PY_CONST = ['True', 'False', 'None'];

  function pyDef(m) {
    const mm = m.match(/^(def|class)(\s+)([A-Za-z_]\w*)([\s\S]*)$/);
    if (!mm) return span('kw-decl', m);
    let out = span('kw-decl', mm[1]) + esc(mm[2]) +
      span(mm[1] === 'class' ? 'type-def' : 'fn-def', mm[3]);
    if (mm[4]) out += pyParams(mm[4]);
    return out;
  }
  function pyParams(text) {
    /* inside a signature every bare name is a parameter, and defaults are code */
    return text.replace(/[\s\S]*/, function (t) {
      let out = '', last = 0, m;
      const re = /([A-Za-z_]\w*)(\s*)(?=[,)=:]|$)|(=)|(:)|([(),])/g;
      while ((m = re.exec(t)) !== null) {
        out += esc(t.slice(last, m.index));
        if (m[1]) out += span(m[1] === 'self' || m[1] === 'cls' ? 'self' : 'param', m[1]) + esc(m[2]);
        else out += span('punc', m[0]);
        last = m.index + m[0].length;
      }
      return out + esc(t.slice(last));
    });
  }

  let pyTok = null;
  const pyRules = [
    [/#[^\n]*/, 'cm'],
    [/(?:[rRbBuU]?[fF]|[fF][rR])(?:"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3})/, function (m) { return interp(m, '{', function (c) { return pyTok(c); }); }],
    [/(?:[rRbBuU]{0,2})(?:"{3}[\s\S]*?"{3}|'{3}[\s\S]*?'{3})/, 'cm-doc'],
    [/(?:[rRbBuU]?[fF]|[fF][rR])(?:"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')/, function (m) { return interp(m, '{', function (c) { return pyTok(c); }); }],
    [/(?:[rRbBuU]{0,2})(?:"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')/, function (m) { return strBody(m); }],
    [/@[A-Za-z_][\w.]*/, 'dec'],
    [/\b(?:def|class)\s+[A-Za-z_]\w*\s*(?:\([^)]*\))?/, pyDef],
    [words(PY_CONST), 'const'],
    [words(PY_CTL), 'kw-ctl'],
    [words(PY_DECL), 'kw-decl'],
    [words(PY_OPW), 'kw-op'],
    [/\b(?:self|cls)\b/, 'self'],
    [/\b\d[\d_]*(?:\.[\d_]+)?(?:[eE][+-]?\d+)?j?\b|\b0[xXbBoO][\da-fA-F_]+\b/, 'num'],
    [/\.\s*[A-Za-z_]\w*(?=\s*\()/, function (m) { return span('punc', '.') + span('method', m.slice(1)); }],
    [/\.\s*[A-Za-z_]\w*/, function (m) { return span('punc', '.') + span('prop', m.slice(1)); }],
    [/\b[A-Za-z_]\w*(?=\s*=[^=])/, function (m) { return span(/^[A-Z_0-9]+$/.test(m) ? 'const' : 'var-def', m); }],
    [words(PY_BI_WORDS), 'bi'],
    [/\b[A-Z][A-Z_0-9]{1,}\b/, 'const'],
    [/\b[A-Z]\w*\b/, 'type'],
    [/\b[A-Za-z_]\w*(?=\s*\()/, 'fn'],
    [/:=|\*\*|\/\/|->|[-+*/%=<>!&|^~]+/, 'op'],
    [/[()[\]{}]/, 'bracket'],
    [/[,.:;]/, 'punc'],
  ];
  const python = makeTokenizer(pyRules);
  pyTok = python;

  /* ------------------------------------------------------------ javascript */
  const JS_CTL = ['if', 'else', 'for', 'while', 'do', 'switch', 'case', 'default', 'break',
    'continue', 'return', 'throw', 'try', 'catch', 'finally', 'await', 'yield'];
  const JS_DECL = ['const', 'let', 'var', 'function', 'class', 'extends', 'import', 'export',
    'from', 'as', 'static', 'get', 'set', 'async', 'new'];
  const JS_OPW = ['typeof', 'instanceof', 'in', 'of', 'delete', 'void'];
  const JS_CONST = ['true', 'false', 'null', 'undefined', 'NaN', 'Infinity'];

  function jsDef(m) {
    const mm = m.match(/^(function|class)(\s+)([A-Za-z_$][\w$]*)([\s\S]*)$/);
    if (!mm) return span('kw-decl', m);
    let out = span('kw-decl', mm[1]) + esc(mm[2]) +
      span(mm[1] === 'class' ? 'type-def' : 'fn-def', mm[3]);
    if (mm[4]) out += jsParams(mm[4]);
    return out;
  }
  function jsParams(t) {
    let out = '', last = 0, m;
    const re = /([A-Za-z_$][\w$]*)|([(),])/g;
    while ((m = re.exec(t)) !== null) {
      out += esc(t.slice(last, m.index));
      out += m[1] ? span('param', m[1]) : span('punc', m[0]);
      last = m.index + m[0].length;
    }
    return out + esc(t.slice(last));
  }

  let jsTok = null;
  const js = makeTokenizer([
    [/\/\/[^\n]*|\/\*[\s\S]*?\*\//, 'cm'],
    [/`(?:\\.|[^`\\])*`/, function (m) { return interp(m, '$', function (c) { return jsTok(c); }); }],
    [/"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'/, function (m) { return strBody(m); }],
    [/\b(?:function|class)\s+[A-Za-z_$][\w$]*\s*(?:\([^)]*\))?/, jsDef],
    [words(JS_CONST), 'const'],
    [words(JS_CTL), 'kw-ctl'],
    [words(JS_DECL), 'kw-decl'],
    [words(JS_OPW), 'kw-op'],
    [/\bthis\b|\bsuper\b/, 'self'],
    [/\b\d[\d_]*(?:\.[\d_]+)?(?:[eE][+-]?\d+)?n?\b|\b0[xX][\da-fA-F]+\b/, 'num'],
    [/\.\s*[A-Za-z_$][\w$]*(?=\s*\()/, function (m) { return span('punc', '.') + span('method', m.slice(1)); }],
    [/\.\s*[A-Za-z_$][\w$]*/, function (m) { return span('punc', '.') + span('prop', m.slice(1)); }],
    [/\b[A-Za-z_$][\w$]*(?=\s*=>)/, 'param'],
    [/\b[A-Za-z_$][\w$]*(?=\s*=[^=>])/, function (m) { return span(/^[A-Z_0-9]+$/.test(m) ? 'const' : 'var-def', m); }],
    [words(JS_BI_WORDS), 'bi'],
    [/\b[A-Z][A-Z_0-9]{1,}\b/, 'const'],
    [/\b[A-Z][\w$]*\b/, 'type'],
    [/\b[A-Za-z_$][\w$]*(?=\s*\()/, 'fn'],
    [/=>|\.{3}|\?\.|\?\?|[-+*/%=<>!&|^~?]+/, 'op'],
    [/[()[\]{}]/, 'bracket'],
    [/[,.;:]/, 'punc'],
  ]);
  jsTok = js;

  /* ------------------------------------------------------------ css */
  const css = makeTokenizer([
    [/\/\*[\s\S]*?\*\//, 'cm'],
    [/"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*'/, 'str'],
    [/@[\w-]+/, 'at-rule'],
    [/!important/, 'kw-ctl'],
    [/--[\w-]+/, 'css-var'],
    [/\bvar\(/, function (m) { return span('fn', 'var') + span('bracket', '('); }],
    [/[-\w]+(?=\s*:[^{};\n]*(?:;|\n|\}|$))/, 'css-prop'],
    [/#[\da-fA-F]{3,8}\b/, 'color'],
    [/\b\d+(?:\.\d+)?(?:px|rem|em|%|vh|vw|s|ms|deg|fr|ch|ex|pt|vmin|vmax)?\b/, function (m) {
      const mm = m.match(/^([\d.]+)([a-z%]*)$/i);
      return mm && mm[2] ? span('num', mm[1]) + span('unit', mm[2]) : span('num', m);
    }],
    [/\b[a-z-]+(?=\s*\()/, 'fn'],
    [/::?[a-z-]+(?:\([^)]*\))?/, 'pseudo'],
    [/[.#][-\w]+/, 'selector'],
    [/\b[a-z][\w-]*(?=[^{}:;]*\{)/, 'tag'],
    [/[{}]/, 'bracket'],
    [/[():;,>+~*]/, 'punc'],
  ]);

  /* ------------------------------------------------------------ html */
  const htmlPart = makeTokenizer([
    [/<!\x2d-[\s\S]*?-->/, 'cm'],
    [/<!doctype[^>]*>/i, 'cm-doc'],
    [/<\/?[a-zA-Z][\w-]*/, function (m) {
      const i = m.indexOf('/') === 1 ? 2 : 1;
      return span('bracket', m.slice(0, i)) + span('tag', m.slice(i));
    }],
    [/\/?>/, 'bracket'],
    [/[\w-]+(?=\s*=)/, 'attr'],
    [/"[^"]*"|'[^']*'/, 'attr-val'],
    [/&[a-zA-Z#]\w*;/, 'entity'],
    [/=/, 'op'],
  ], 'gmi');

  function html(code) {
    const re = /(<(style|script)\b[^>]*>)([\s\S]*?)(<\/\2\s*>)/gi;
    let out = '', last = 0, m;
    while ((m = re.exec(code)) !== null) {
      out += htmlPart(code.slice(last, m.index));
      out += htmlPart(m[1]);
      out += (m[2].toLowerCase() === 'style') ? css(m[3]) : js(m[3]);
      out += htmlPart(m[4]);
      last = m.index + m[0].length;
    }
    return out + htmlPart(code.slice(last));
  }

  function normLang(lang) {
    lang = String(lang || '').toLowerCase();
    if (lang === 'javascript' || lang === 'jsx' || lang === 'mjs') return 'js';
    if (lang === 'py' || lang === 'python3') return 'python';
    return lang;
  }
  function render(code, lang) {
    lang = normLang(lang);
    try {
      if (lang === 'python') return python(code);
      if (lang === 'js') return js(code);
      if (lang === 'css') return css(code);
      if (lang === 'html') return html(code);
    } catch (e) { /* fall through to plain text */ }
    return esc(code);
  }
  return { render: render, normLang: normLang };
})();

/* ---------- markdown ---------- */
/* Mathematics is pulled out before markdown runs and put back after: an expression
   is full of the characters markdown wants to eat (_ for emphasis, * for bold,
   backslashes for escapes), and MathML is markup markdown must not touch either. */
const MATH_SLOTS = [];
function protectMath(text) {
  if (typeof MathML === 'undefined') return String(text);
  return String(text)
    .replace(/(^|[^\\])\$\$([\s\S]+?)\$\$/g, function (m, pre, body) {
      MATH_SLOTS.push(MathML.render(body, true));
      return pre + '\u0001M' + (MATH_SLOTS.length - 1) + '\u0001';
    })
    .replace(/(^|[^\\])\$([^$\n]+?)\$/g, function (m, pre, body) {
      MATH_SLOTS.push(MathML.render(body, false));
      return pre + '\u0001M' + (MATH_SLOTS.length - 1) + '\u0001';
    });
}
function restoreMath(html) {
  return String(html)
    .replace(/\u0001M(\d+)\u0001/g, function (m, i) { return MATH_SLOTS[+i] || ''; })
    .replace(/\\\$/g, '$');
}


let _cbSeq = 0;
const CB_STORE = {};
function mdInline(s) { return restoreMath(mdInlineInner(protectMath(s))); }
function mdInlineInner(s) {
  let t = esc(s);
  t = t.replace(/`([^`]+)`/g, function (_, c) { return '<code>' + c + '</code>'; });
  t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/(^|[^*\w])\*([^*\n]+)\*(?![\w*])/g, '$1<em>$2</em>');
  t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  return t;
}
function mdCodeBlock(code, lang) {
  const norm = Highlight.normLang(lang);
  const runnable = norm === 'python' || norm === 'js' || norm === 'html';
  const id = 'cb' + (++_cbSeq);
  CB_STORE[id] = { code: code, lang: norm };
  /* Examples run in a drawer under the block. Nothing here navigates: leaving the
     page to run three lines would cost the reader their place in the material. */
  const acts = runnable
    ? '<button class="cb-btn cb-run" data-cb="' + id + '" type="button">▶ Run</button>' +
      '<button class="cb-btn cb-copy" data-cb="' + id + '" type="button">Copy</button>' +
      '<button class="cb-btn cb-open" data-cb="' + id + '" type="button" ' +
        'title="Open a full editor in the Playground"><span class="lbl">Playground </span>↗</button>'
    : '<button class="cb-btn cb-copy" data-cb="' + id + '" type="button">Copy</button>';
  return '<div class="cbx" data-cbx="' + id + '">' +
    '<div class="cb-head"><span class="lang">' + esc(lang || 'text') + '</span><span class="sp"></span>' +
      acts +
    '</div>' +
    '<pre class="md-code"><code>' + Highlight.render(code, norm) + '</code></pre>' +
  '</div>';
}
function renderMd(src) { return restoreMath(renderMdInner(protectMath(src))); }
function renderMdInner(src) {
  const lines = String(src).replace(/\r/g, '').split('\n');
  let out = '', i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (/^```/.test(line)) {
      const lang = line.slice(3).trim();
      const buf = [];
      i++;
      while (i < lines.length && !/^```/.test(lines[i])) { buf.push(lines[i]); i++; }
      i++;
      out += mdCodeBlock(buf.join('\n'), lang);
      continue;
    }
    if (/^#{1,4}\s/.test(line)) {
      const lvl = Math.max(2, Math.min(4, line.match(/^#+/)[0].length));
      out += '<h' + lvl + '>' + mdInline(line.replace(/^#+\s*/, '')) + '</h' + lvl + '>';
      i++; continue;
    }
    if (/^---+\s*$/.test(line)) { out += '<hr>'; i++; continue; }
    if (/^>\s?/.test(line)) {
      const buf = [];
      while (i < lines.length && /^>\s?/.test(lines[i])) { buf.push(lines[i].replace(/^>\s?/, '')); i++; }
      out += '<blockquote>' + renderMd(buf.join('\n')) + '</blockquote>';
      continue;
    }
    if (/^\|/.test(line)) {
      const rows = [];
      while (i < lines.length && /^\|/.test(lines[i])) { rows.push(lines[i]); i++; }
      const cells = r => r.replace(/^\|/, '').replace(/\|\s*$/, '').split('|').map(c => c.trim());
      /* Wrapped, because .main is the page's scroll container: a table wider than the
         prose column scrolled the whole pane sideways. tabindex puts the scroll box in
         the tab order, since a scrollable region reachable only by pointer is not
         reachable at all. */
      let t = '<div class="tw" tabindex="0"><table><thead><tr>' + cells(rows[0]).map(c => '<th>' + mdInline(c) + '</th>').join('') + '</tr></thead><tbody>';
      for (let r = 1; r < rows.length; r++) {
        if (/^\|\s*:?-{2,}/.test(rows[r])) continue;
        t += '<tr>' + cells(rows[r]).map(c => '<td>' + mdInline(c) + '</td>').join('') + '</tr>';
      }
      out += t + '</tbody></table></div>';
      continue;
    }
    if (/^\s*[-*]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[-*]\s+/.test(lines[i])) {
        let item = lines[i].replace(/^\s*[-*]\s+/, ''); i++;
        while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*[-*]\s+/.test(lines[i])) { item += ' ' + lines[i].trim(); i++; }
        items.push(item);
      }
      out += '<ul>' + items.map(it => '<li>' + mdInline(it) + '</li>').join('') + '</ul>';
      continue;
    }
    if (/^\s*\d+[.)]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+[.)]\s+/.test(lines[i])) {
        let item = lines[i].replace(/^\s*\d+[.)]\s+/, ''); i++;
        while (i < lines.length && /^\s{2,}\S/.test(lines[i]) && !/^\s*\d+[.)]\s+/.test(lines[i])) { item += ' ' + lines[i].trim(); i++; }
        items.push(item);
      }
      out += '<ol>' + items.map(it => '<li>' + mdInline(it) + '</li>').join('') + '</ol>';
      continue;
    }
    if (line.trim() === '') { i++; continue; }
    const buf = [line]; i++;
    while (i < lines.length && lines[i].trim() !== '' && !/^(#{1,4}\s|```|\s*[-*]\s+|\s*\d+[.)]\s+|>|\||---+\s*$)/.test(lines[i])) { buf.push(lines[i]); i++; }
    out += '<p>' + mdInline(buf.join(' ')) + '</p>';
  }
  return out;
}

/* ---------- code editor ---------- */
const PAIRS = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'" };
function createEditor(root, opts) {
  opts = opts || {};
  root.classList.add('cw-editor');
  root.innerHTML = '<div class="ed-gutter" aria-hidden="true"></div>' +
    '<div class="ed-body"><pre class="ed-hl" aria-hidden="true"><code></code></pre>' +
    '<textarea class="ed-ta" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" wrap="off" aria-label="Code editor"></textarea></div>';
  const ta = root.querySelector('.ed-ta');
  const hl = root.querySelector('.ed-hl code');
  const pre = root.querySelector('.ed-hl');
  const gutter = root.querySelector('.ed-gutter');
  const edBody = root.querySelector('.ed-body');
  let lang = opts.lang || 'python';
  let lineCount = -1;

  function unit() { return lang === 'python' ? '    ' : '  '; }
  function refresh() {
    hl.innerHTML = Highlight.render(ta.value, lang) + '\n';
    const n = ta.value.split('\n').length;
    if (n !== lineCount) {
      lineCount = n;
      let g = '';
      for (let k = 1; k <= n; k++) g += '<div>' + k + '</div>';
      gutter.innerHTML = g;
      gutter.scrollTop = ta.scrollTop;
    }
  }
  function fireInput() { ta.dispatchEvent(new Event('input', { bubbles: true })); }
  function editRange(start, end, text) {
    ta.focus();
    ta.setSelectionRange(start, end);
    let ok = false;
    try { ok = document.execCommand(text ? 'insertText' : 'delete', false, text || undefined); } catch (e) { ok = false; }
    if (!ok) {
      if (ta.setRangeText) { ta.setRangeText(text, start, end, 'end'); }
      else {
        const v2 = ta.value;
        ta.value = v2.slice(0, start) + text + v2.slice(end);
        ta.setSelectionRange(start + text.length, start + text.length);
      }
      fireInput();
    }
  }
  ta.addEventListener('input', function () {
    refresh();
    if (opts.onChange) opts.onChange(ta.value);
    if (acSquelch) acSquelch = false; else acInput();
  });
  ta.addEventListener('scroll', function () { pre.scrollTop = ta.scrollTop; pre.scrollLeft = ta.scrollLeft; gutter.scrollTop = ta.scrollTop; acClose(); });
  ta.addEventListener('pointerdown', function () { acClose(); });
  ta.addEventListener('blur', function () { setTimeout(acClose, 120); });
  ta.addEventListener('keydown', function (e) {
    if (acKey(e)) return;
    const v = ta.value, s = ta.selectionStart, en = ta.selectionEnd;
    const mod = e.ctrlKey || e.metaKey;
    if (mod && e.key === 'Enter') { e.preventDefault(); if (opts.onRun) opts.onRun(); return; }
    if (mod && (e.key === 's' || e.key === 'S')) { e.preventDefault(); if (opts.onSave) opts.onSave(); return; }
    if (ta.readOnly) return;
    if (mod && e.key === '/') {
      if (lang !== 'python' && lang !== 'js') return;
      e.preventDefault();
      const prefix = lang === 'python' ? '# ' : '// ';
      const ls = v.lastIndexOf('\n', s - 1) + 1;
      let le = v.indexOf('\n', en); if (le === -1) le = v.length;
      const block = v.slice(ls, le).split('\n');
      const allOn = block.every(l => !l.trim() || l.trimStart().startsWith(prefix.trim()));
      const outB = block.map(function (l) {
        if (!l.trim()) return l;
        if (allOn) return l.replace(lang === 'python' ? /^(\s*)#\s?/ : /^(\s*)\/\/\s?/, '$1');
        return l.replace(/^(\s*)/, '$1' + prefix);
      }).join('\n');
      editRange(ls, le, outB);
      ta.setSelectionRange(ls, ls + outB.length);
      return;
    }
    if (mod || e.altKey) return;
    if (e.key === 'Tab') {
      e.preventDefault();
      const u = unit();
      if (s !== en && v.slice(s, en).indexOf('\n') !== -1) {
        const ls = v.lastIndexOf('\n', s - 1) + 1;
        let le = v.indexOf('\n', en - 1); if (le === -1) le = v.length;
        const block = v.slice(ls, le).split('\n');
        const outB = block.map(function (l) {
          if (e.shiftKey) return l.startsWith(u) ? l.slice(u.length) : l.replace(/^[ \t]/, '');
          return u + l;
        }).join('\n');
        editRange(ls, le, outB);
        ta.setSelectionRange(ls, ls + outB.length);
      } else if (e.shiftKey) {
        const ls = v.lastIndexOf('\n', s - 1) + 1;
        const rest = v.slice(ls);
        const rm = rest.startsWith(u) ? u.length : (/^[ \t]/.test(rest) ? 1 : 0);
        if (rm) { const off = s - ls; editRange(ls, ls + rm, ''); ta.setSelectionRange(Math.max(ls, ls + off - rm), Math.max(ls, ls + off - rm)); }
      } else {
        editRange(s, en, u);
      }
      return;
    }
    if (e.key === 'Enter') {
      e.preventDefault();
      const ls = v.lastIndexOf('\n', s - 1) + 1;
      const line = v.slice(ls, s);
      const indent = (line.match(/^[ \t]*/) || [''])[0];
      const trimmed = line.replace(/\s+$/, '');
      const lastCh = trimmed.slice(-1);
      let add = '';
      if (lang === 'python' && lastCh === ':') add = unit();
      else if (lastCh === '{' || lastCh === '[' || lastCh === '(') add = unit();
      const closer = { '{': '}', '[': ']', '(': ')' }[lastCh];
      if (closer && v[en] === closer) {
        editRange(s, en, '\n' + indent + add + '\n' + indent);
        ta.setSelectionRange(s + 1 + indent.length + add.length, s + 1 + indent.length + add.length);
      } else {
        editRange(s, en, '\n' + indent + add);
      }
      return;
    }
    if (e.key === 'Backspace' && s === en && s > 0) {
      if (PAIRS[v[s - 1]] === v[s]) { e.preventDefault(); editRange(s - 1, s + 1, ''); return; }
      /* the <> pair deletes as one, like every other pair */
      if (lang === 'html' && v[s - 1] === '<' && v[s] === '>') { e.preventDefault(); editRange(s - 1, s + 1, ''); return; }
      return;
    }
    if (lang === 'html' && htmlKey(e, v, s, en)) return;
    if ((e.key === ')' || e.key === ']' || e.key === '}' || e.key === '"' || e.key === "'") && s === en && v[en] === e.key) {
      e.preventDefault();
      ta.setSelectionRange(en + 1, en + 1);
      return;
    }
    if (PAIRS[e.key]) {
      const close = PAIRS[e.key];
      if (s !== en) {
        e.preventDefault();
        const sel = v.slice(s, en);
        editRange(s, en, e.key + sel + close);
        ta.setSelectionRange(s + 1, s + 1 + sel.length);
        return;
      }
      const next = v[en] || '';
      const prev = v[s - 1] || '';
      const isQuote = e.key === '"' || e.key === "'";
      if (isQuote && (/[\w'"]/.test(prev) || /\w/.test(next))) return;
      if (next === '' || /[\s)\]}.,;:]/.test(next)) {
        e.preventDefault();
        editRange(s, en, e.key + close);
        ta.setSelectionRange(s + 1, s + 1);
      }
      return;
    }
  });

  /* ---- html brackets ----
     "<" pairs to "<>", ">" closes the element, and "</" fills in whatever is still
     open. Everything here is opt-in per keystroke: if the caret is not somewhere that
     wants markup (a script body, a comment, an attribute string) it does nothing and
     the ordinary typing path runs. */
  function htmlKey(e, v, s, en) {
    if (e.key === '<') {
      if (s !== en) {                       /* wrap the selection */
        const sel = v.slice(s, en);
        e.preventDefault();
        editRange(s, en, '<' + sel + '>');
        ta.setSelectionRange(s + 1, s + 1 + sel.length);
        return true;
      }
      const w = htmlWhere(v, s);
      if (w.at === 'comment' || w.at === 'attrvalue' || w.raw) return false;
      if (w.at === 'attr' || w.at === 'tagname') return false;   /* already inside a tag */
      const next = v[s] || '';
      if (next && !/[\s<>]/.test(next)) return false;            /* typing into a word */
      e.preventDefault();
      editRange(s, en, '<>');
      ta.setSelectionRange(s + 1, s + 1);
      return true;
    }

    if (e.key === '/' && s === en && v[s - 1] === '<') {
      const open = htmlOpenStack(v.slice(0, s - 1));
      if (!open.length) return false;
      const name = open[open.length - 1];
      const skip = v[s] === '>' ? 1 : 0;
      e.preventDefault();
      editRange(s, en + skip, '/' + name + '>');
      const caret = s + name.length + 2;
      ta.setSelectionRange(caret, caret);
      refresh();
      return true;
    }

    if (e.key === '>' && s === en) {
      const w = htmlWhere(v, s);
      if (w.at !== 'tagname' && w.at !== 'attr') {
        /* not in a tag: just step over a ">" the pairing already put there */
        if (v[s] === '>') { e.preventDefault(); ta.setSelectionRange(s + 1, s + 1); return true; }
        return false;
      }
      const inner = v.slice(w.lt, s);
      const nm = inner.match(/^<([A-Za-z][A-Za-z0-9-]*)/);
      const name = nm ? nm[1] : '';
      const skip = v[s] === '>' ? 1 : 0;
      const selfClosing = /\/\s*$/.test(inner) || (name && HTML_VOID[name.toLowerCase()]);
      if (!name) {
        if (skip) { e.preventDefault(); ta.setSelectionRange(s + 1, s + 1); return true; }
        return false;
      }
      e.preventDefault();
      if (selfClosing) {
        editRange(s, en + skip, '>');
        ta.setSelectionRange(s + 1, s + 1);
      } else {
        editRange(s, en + skip, '></' + name + '>');
        ta.setSelectionRange(s + 1, s + 1);
      }
      refresh();
      return true;
    }
    return false;
  }

  /* ---- completion ----
     The menu is a view over Complete.suggest(): it decides what is valid at the
     caret, this decides how it looks and what accepting one does. Every suggestion
     carries its kind, a signature and a sentence of documentation, because a bare
     list of names teaches nobody anything. */
  let acEl = null, acDoc = null, acSig = null;
  let acItems = [], acSel = 0, acSquelch = false, charW = 0;
  let acCtx = { from: 0, context: 'none' };
  let snip = null;                       /* active snippet session */

  function measureChar() {
    if (charW) return charW;
    const sp = document.createElement('span');
    sp.textContent = 'MMMMMMMMMM';
    sp.style.visibility = 'hidden';
    hl.appendChild(sp);
    let w = 0;
    try { w = sp.getBoundingClientRect().width / 10; } catch (e) { w = 0; }
    sp.remove();
    charW = w > 1 ? w : 8.11;
    return charW;
  }

  function acClose() {
    if (acEl) { acEl.remove(); acEl = null; }
    if (acDoc) { acDoc.remove(); acDoc = null; }
    if (acSig) { acSig.remove(); acSig = null; }
    acItems = [];
  }

  function markup(name, hits) {
    if (!hits || !hits.length) return esc(name);
    const set = {};
    hits.forEach(function (i) { set[i] = 1; });
    let out = '';
    for (let i = 0; i < name.length; i++) {
      out += set[i] ? '<b>' + esc(name[i]) + '</b>' : esc(name[i]);
    }
    return out;
  }

  function acPaint() {
    let h = '';
    for (let i = 0; i < acItems.length; i++) {
      const it = acItems[i];
      h += '<div class="ac-item k-' + it.k + (i === acSel ? ' sel' : '') + '" data-i="' + i + '" ' +
        'role="option" aria-selected="' + (i === acSel ? 'true' : 'false') + '" ' +
        'title="' + esc(Complete.kindLabel(it.k)) + '">' +
        '<span class="ac-ic">' + esc(Complete.kindMark(it.k)) + '</span>' +
        '<span class="ac-n">' + markup(it.n, it.hits) + '</span>' +
        '<span class="ac-d">' + esc(it.detail || '') + '</span>' +
      '</div>';
    }
    acEl.innerHTML = h;
    const sel = acEl.children[acSel];
    if (sel && sel.scrollIntoView) { try { sel.scrollIntoView({ block: 'nearest' }); } catch (e) {} }
    paintDoc();
  }

  function paintDoc() {
    const it = acItems[acSel];
    if (!it || (!it.doc && !it.detail)) { if (acDoc) { acDoc.remove(); acDoc = null; } return; }
    if (!acDoc) {
      acDoc = document.createElement('div');
      acDoc.className = 'ac-doc';
      edBody.appendChild(acDoc);
    }
    acDoc.innerHTML =
      '<div class="ac-doc-h"><span class="ac-ic k-' + it.k + '">' + esc(Complete.kindMark(it.k)) + '</span>' +
        '<b>' + esc(it.n) + '</b><span class="ac-kind">' + esc(Complete.kindLabel(it.k)) + '</span></div>' +
      (it.detail ? '<div class="ac-sig">' + esc(it.n) + esc(/^\(/.test(it.detail) ? it.detail : '') +
        (/^\(/.test(it.detail) ? '' : '<span class="ac-ty"> \u2014 ' + esc(it.detail) + '</span>') + '</div>' : '') +
      (it.doc ? '<p>' + esc(it.doc) + '</p>' : '');
    place(acDoc, true);
  }

  function paintSig(sig) {
    if (!sig || !sig.label) { if (acSig) { acSig.remove(); acSig = null; } return; }
    if (!acSig) {
      acSig = document.createElement('div');
      acSig.className = 'ac-sighint';
      edBody.appendChild(acSig);
    }
    let label = esc(sig.label);
    if (sig.params && sig.params.length && typeof sig.active === 'number') {
      const p = sig.params[Math.min(sig.active, sig.params.length - 1)];
      if (p) label = label.replace(esc(p), '<b>' + esc(p) + '</b>');
    }
    acSig.innerHTML = '<span class="ac-sig-l">' + label + '</span>' +
      (sig.doc ? '<span class="ac-sig-d">' + esc(sig.doc) + '</span>' : '');
    place(acSig, false, true);
  }

  /* caret-relative placement, clamped inside the editor body */
  function caretXY(from) {
    const upto = ta.value.slice(0, from);
    const nl = upto.lastIndexOf('\n');
    const lineText = upto.slice(nl + 1);
    let col = 0;
    for (let i = 0; i < lineText.length; i++) col = lineText[i] === '\t' ? (Math.floor(col / 4) + 1) * 4 : col + 1;
    const line = nl === -1 ? 0 : (upto.match(/\n/g) || []).length;
    return { x: 14 + col * measureChar() - ta.scrollLeft, y: 12 + line * 21.6 - ta.scrollTop };
  }

  function place(node, beside, above) {
    const at = caretXY(acCtx.from);
    const bw = edBody.clientWidth || 400, bh = edBody.clientHeight || 300;
    const nh = node.offsetHeight || 90, nw = node.offsetWidth || 220;
    if (above) {
      node.style.left = clamp(at.x, 4, Math.max(4, bw - nw - 4)) + 'px';
      node.style.top = clamp(at.y - nh - 4, 4, Math.max(4, bh - nh - 4)) + 'px';
      return;
    }
    const menu = acEl ? (acEl.offsetHeight || 120) : 0;
    let top = at.y + 21.6 + 2;
    if (top + menu > bh - 4 && at.y - menu - 2 > 0) top = at.y - menu - 2;
    top = clamp(top, 2, Math.max(2, bh - Math.max(menu, nh) - 2));
    if (beside) {
      const mw = acEl ? (acEl.offsetWidth || 240) : 0;
      const right = at.x + mw + 8;
      const fits = right + nw < bw - 4;
      node.style.left = (fits ? right : Math.max(4, at.x - nw - 8)) + 'px';
      node.style.top = top + 'px';
    } else {
      node.style.left = clamp(at.x, 2, Math.max(2, bw - nw - 2)) + 'px';
      node.style.top = top + 'px';
    }
  }

  function acShow(force) {
    if (ta.readOnly) return;
    const res = Complete.suggest(ta.value, ta.selectionStart, lang,
      opts.acExtra ? String(opts.acExtra() || '') : '');
    acCtx = res;
    paintSig(res.signature);
    if (!res.items.length) {
      if (acEl) { acEl.remove(); acEl = null; }
      if (acDoc) { acDoc.remove(); acDoc = null; }
      acItems = [];
      return;
    }
    /* a single exact match that would change nothing is noise, unless asked for */
    if (!force && res.items.length === 1 && res.items[0].n === ta.value.slice(res.from, ta.selectionStart) &&
        !res.items[0].body && !res.items[0].insert && res.context !== 'text' && res.context !== 'tagname') {
      acClose();
      return;
    }
    acItems = res.items;
    acSel = 0;
    if (!acEl) {
      acEl = document.createElement('div');
      acEl.className = 'ac-menu';
      acEl.setAttribute('role', 'listbox');
      acEl.addEventListener('pointerdown', function (e) {
        const it = e.target.closest ? e.target.closest('.ac-item') : null;
        if (!it) return;
        e.preventDefault();
        acSel = +it.dataset.i;
        acAccept();
      });
      edBody.appendChild(acEl);
    }
    acPaint();
    place(acEl, false);
    paintDoc();
  }

  function acInput() {
    if (ta.readOnly) return;
    const pos = ta.selectionStart;
    const prev = ta.value[pos - 1] || '';
    /* a dot always opens the member list, even with nothing typed after it */
    if (prev === '.' || prev === '<') { acShow(true); return; }
    const res = Complete.suggest(ta.value, pos, lang, '');
    if (res.from === pos && res.context !== 'member' && res.context !== 'tagname' && res.context !== 'closetag') {
      /* nothing typed: keep any signature hint, drop the list */
      paintSig(res.signature);
      if (acEl) { acEl.remove(); acEl = null; }
      if (acDoc) { acDoc.remove(); acDoc = null; }
      acItems = [];
      return;
    }
    acShow(false);
  }

  /* ---- snippets ---------------------------------------------------------- */
  function parseSnippet(body) {
    const stops = [];
    let text = '', i = 0;
    while (i < body.length) {
      const m = /^\$\{(\d+)(?::([^}]*))?\}/.exec(body.slice(i));
      if (m) {
        stops.push({ order: +m[1] === 0 ? Infinity : +m[1], at: text.length, len: (m[2] || '').length });
        text += m[2] || '';
        i += m[0].length;
        continue;
      }
      text += body[i++];
    }
    stops.sort(function (a, b) { return a.order - b.order; });
    return { text: text, stops: stops };
  }

  function startSnippet(at, parsed) {
    if (!parsed.stops.length) { ta.setSelectionRange(at + parsed.text.length, at + parsed.text.length); return; }
    snip = { base: at, stops: parsed.stops, i: 0 };
    gotoStop(0);
  }
  function gotoStop(i) {
    if (!snip || i >= snip.stops.length) { snip = null; return; }
    snip.i = i;
    const st = snip.stops[i];
    ta.focus();
    ta.setSelectionRange(snip.base + st.at, snip.base + st.at + st.len);
  }
  function snippetTab() {
    if (!snip) return false;
    if (snip.i + 1 >= snip.stops.length) { snip = null; return false; }
    gotoStop(snip.i + 1);
    return true;
  }

  /* ---- accepting --------------------------------------------------------- */
  function acAccept() {
    if (!acEl || !acItems.length) return;
    const it = acItems[acSel];
    const start = acCtx.from;
    let end = ta.selectionStart;
    const after = ta.value[end] || '';
    const ctx = acCtx.context;
    let text = it.n, caret = start + it.n.length, parsed = null;

    if (it.body) {
      parsed = parseSnippet(it.body);
      text = parsed.text;
    } else if (lang === 'html' && (ctx === 'tagname' || ctx === 'text') && it.k === K.TYPE) {
      if (ctx === 'tagname' && after === '>') end = end + 1;
      if (ctx === 'tagname' && ta.value[start - 1] !== '<') { /* defensive: leave as typed */ }
      const open = ctx === 'text' ? '<' : '';
      if (HTML_VOID[it.n]) {
        text = open + it.n + '>';
        caret = start + text.length - (HTML_VOID_BARE[it.n] ? 0 : 1);
      } else {
        text = open + it.n + '></' + it.n + '>';
        caret = start + open.length + it.n.length + 1;
      }
    } else if (lang === 'html' && ctx === 'closetag') {
      text = it.n + '>';
      if (after === '>') end = end + 1;
      caret = start + text.length;
    } else if (it.insert) {
      text = it.insert;
      caret = /""$/.test(text) ? start + text.length - 1
        : /: $/.test(text) ? start + text.length
        : start + text.length;
    } else if ((it.k === K.FN || it.k === K.METHOD) && after !== '(' && ctx !== 'import') {
      text = it.n + '()';
      caret = start + it.n.length + 1;
    }

    acClose();
    acSquelch = true;
    editRange(start, end, text);
    if (parsed) startSnippet(start, parsed);
    else ta.setSelectionRange(caret, caret);
    refresh();
    /* an accepted call is exactly when a signature is wanted */
    if (!parsed) {
      const sig = Complete.suggest(ta.value, ta.selectionStart, lang, '').signature;
      paintSig(sig);
    }
  }

  function acKey(e) {
    const mod = e.ctrlKey || e.metaKey;
    if (mod && (e.key === ' ' || e.code === 'Space')) {
      if (!ta.readOnly) { e.preventDefault(); acShow(true); }
      return true;
    }
    if (!acEl) {
      if (e.key === 'Tab' && !e.shiftKey && snip && snippetTab()) { e.preventDefault(); return true; }
      if (e.key === 'Escape' && snip) { snip = null; }
      return false;
    }
    if (mod && e.key === 'Enter') { acClose(); return false; }
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      acSel = (acSel + (e.key === 'ArrowDown' ? 1 : acItems.length - 1)) % acItems.length;
      acPaint();
      return true;
    }
    if (e.key === 'PageDown' || e.key === 'PageUp') {
      e.preventDefault();
      acSel = clamp(acSel + (e.key === 'PageDown' ? 6 : -6), 0, acItems.length - 1);
      acPaint();
      return true;
    }
    if (e.key === 'Home' && acEl) { e.preventDefault(); acSel = 0; acPaint(); return true; }
    if (e.key === 'End' && acEl) { e.preventDefault(); acSel = acItems.length - 1; acPaint(); return true; }
    if (e.key === 'Enter' || e.key === 'Tab') { e.preventDefault(); acAccept(); return true; }
    if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); acClose(); return true; }
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') { acClose(); return false; }
    return false;
  }

  refresh();
  return {
    el: root,
    getValue: function () { return ta.value; },
    setValue: function (v) { acClose(); ta.value = v; lineCount = -1; refresh(); ta.scrollTop = 0; ta.scrollLeft = 0; pre.scrollTop = 0; pre.scrollLeft = 0; },
    setLang: function (l) { lang = l; refresh(); },
    setReadOnly: function (ro) { ta.readOnly = !!ro; ta.classList.toggle('ro', !!ro); },
    focus: function () { ta.focus(); },
    insertIndent: function () { if (!ta.readOnly) editRange(ta.selectionStart, ta.selectionEnd, unit()); },
  };
}

/* ---------- web / js runner (sandboxed iframe) ---------- */
function escScript(s) { return String(s).replace(/<\/script/gi, '<\\/script'); }
function escapeReg(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

/* Runs INSIDE the iframe. Must be self-contained (it gets stringified). */
function __cwHarness(RUN, OFFSET) {
  function post(type, payload) {
    try { parent.postMessage({ source: 'cw-runner', runId: RUN, type: type, payload: payload }, '*'); } catch (e) {}
  }
  function fmt(a) {
    if (typeof a === 'string') return a;
    if (a === undefined) return 'undefined';
    if (a === null) return 'null';
    if (typeof a === 'function') return String(a);
    if (a instanceof Error) return (a.name ? a.name + ': ' : '') + a.message;
    try { var s = JSON.stringify(a); return s === undefined ? String(a) : s; } catch (e) { return String(a); }
  }
  ['log', 'info', 'warn', 'error', 'debug'].forEach(function (l) {
    var orig = console[l];
    console[l] = function () {
      var args = Array.prototype.slice.call(arguments);
      post('console', { level: (l === 'debug' || l === 'info') ? 'log' : l, text: args.map(fmt).join(' ') });
      if (orig) { try { orig.apply(console, args); } catch (e) {} }
    };
  });
  window.addEventListener('error', function (e) {
    var where = '';
    if (e.lineno && e.lineno - OFFSET > 0) where = '  (line ' + (e.lineno - OFFSET) + ')';
    post('console', { level: 'error', text: (e.message || 'Script error') + where });
  });
  window.addEventListener('unhandledrejection', function (e) {
    var r = e.reason;
    post('console', { level: 'error', text: 'Unhandled promise rejection: ' + ((r && r.message) || r) });
  });
  /* The preview iframe is sandboxed without allow-same-origin, so it has an
     opaque origin and every localStorage access throws a SecurityError. Rather
     than weaken the sandbox (allow-scripts + allow-same-origin would let student
     code reach back into the app), give the frame a memory-backed Storage that
     behaves like the real one for the lifetime of the run. */
  (function () {
    var usable = false;
    try { window.localStorage.getItem('__cw'); usable = true; } catch (e) { usable = false; }
    if (usable) return;
    function makeStore() {
      var map = Object.create(null);
      var api = {
        getItem: function (k) { k = String(k); return k in map ? map[k] : null; },
        setItem: function (k, v) { map[String(k)] = String(v); },
        removeItem: function (k) { delete map[String(k)]; },
        clear: function () { map = Object.create(null); },
        key: function (i) { var ks = Object.keys(map); return i < ks.length ? ks[i] : null; },
      };
      Object.defineProperty(api, 'length', { get: function () { return Object.keys(map).length; } });
      return api;
    }
    ['localStorage', 'sessionStorage'].forEach(function (name) {
      try {
        Object.defineProperty(window, name, { value: makeStore(), configurable: true, writable: false });
      } catch (e) {
        try { window[name] = makeStore(); } catch (e2) {}
      }
    });
  })();

  window.assert = function (cond, msg) { if (!cond) throw new Error(msg || 'Assertion failed'); };
  window.assertEqual = function (a, b, msg) {
    var sa, sb;
    try { sa = JSON.stringify(a); } catch (e) { sa = String(a); }
    try { sb = JSON.stringify(b); } catch (e) { sb = String(b); }
    if (sa !== sb) throw new Error((msg ? msg + ' — ' : '') + 'expected ' + sb + ' but got ' + sa);
  };
  window.__cw = { post: post };
}

/* Runs INSIDE the iframe after load. */
function __cwTests(tests) {
  function runFrom(i, results) {
    if (i >= tests.length) { window.__cw.post('tests', results); window.__cw.post('done'); return; }
    var t = tests[i];
    var p;
    try {
      var fn = new Function('"use strict"; return (async function () {\n' + t.code + '\n})();');
      p = Promise.resolve(fn());
    } catch (e) { p = Promise.reject(e); }
    p.then(function () {
      results.push({ name: t.name, pass: true });
      runFrom(i + 1, results);
    }, function (e) {
      results.push({ name: t.name, pass: false, message: String((e && e.message) || e) });
      runFrom(i + 1, results);
    });
  }
  function start() { setTimeout(function () { runFrom(0, []); }, 40); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start);
  else start();
}

const WebRunner = (function () {
  let seq = 0;
  const handlers = {};
  if (typeof window !== 'undefined') {
    window.addEventListener('message', function (e) {
      const d = e.data;
      if (!d || d.source !== 'cw-runner') return;
      const h = handlers[d.runId];
      if (h) h(d.type, d.payload);
    });
  }
  function buildDoc(kind, files, main, tests, runId) {
    const SCRIPT_OPEN = '<scr' + 'ipt>';
    const SCRIPT_CLOSE = '<\/scr' + 'ipt>';
    const testsJson = escScript(JSON.stringify(tests.map(t => ({ name: t.name, code: dedent(t.code) }))));
    const testTag = SCRIPT_OPEN + '(' + __cwTests.toString() + ')(' + testsJson + ');' + SCRIPT_CLOSE;
    if (kind === 'js') {
      const mainFile = files.find(f => f.name === main) || files[0];
      const prefix = '<!doctype html><html><head><meta charset="utf-8"></head><body>' +
        SCRIPT_OPEN + '(' + __cwHarness.toString() + ')(' + runId + ', OFFSET_PLACEHOLDER);' + SCRIPT_CLOSE +
        SCRIPT_OPEN + '\n';
      const offset = prefix.split('\n').length - 1;
      return prefix.replace('OFFSET_PLACEHOLDER', String(offset)) +
        escScript(mainFile.content) + '\n' + SCRIPT_CLOSE + testTag + '</body></html>';
    }
    /* kind === 'web' */
    const mainFile = files.find(f => f.name === main) || files[0];
    let doc = mainFile.content;
    for (const f of files) {
      if (/\.css$/.test(f.name)) {
        doc = doc.replace(new RegExp('<link[^>]*href=["\']' + escapeReg(f.name) + '["\'][^>]*>', 'i'),
          function () { return '<style>\n' + f.content + '\n</style>'; });
      } else if (/\.js$/.test(f.name)) {
        doc = doc.replace(new RegExp('<scr' + 'ipt[^>]*src=["\']' + escapeReg(f.name) + '["\'][^>]*>\\s*<\\/scr' + 'ipt>', 'i'),
          function () { return SCRIPT_OPEN + '\n' + escScript(f.content) + '\n' + SCRIPT_CLOSE; });
      }
    }
    const inj = SCRIPT_OPEN + '(' + __cwHarness.toString() + ')(' + runId + ', 0);' + SCRIPT_CLOSE;
    if (/<head[^>]*>/i.test(doc)) doc = doc.replace(/<head[^>]*>/i, function (m) { return m + inj; });
    else doc = inj + doc;
    if (/<\/body>/i.test(doc)) doc = doc.replace(/<\/body>/i, function () { return testTag + '<\/body>'; });
    else doc = doc + testTag;
    return doc;
  }
  function run(opts) {
    const runId = ++seq;
    const mount = opts.mount;
    mount.innerHTML = '';
    const frame = document.createElement('iframe');
    frame.className = 'preview-frame';
    frame.setAttribute('sandbox', 'allow-scripts');
    frame.setAttribute('title', 'Program output');
    let finished = false;
    const timeout = setTimeout(function () {
      if (finished) return;
      finished = true;
      delete handlers[runId];
      opts.onConsole('error', 'Tests did not finish within 10s — an infinite loop, or a very long timer?');
      opts.onDone(null);
    }, 10000);
    handlers[runId] = function (type, payload) {
      if (type === 'console') opts.onConsole(payload.level, payload.text);
      else if (type === 'tests') opts.onTests(payload);
      else if (type === 'done') {
        if (finished) return;
        finished = true;
        clearTimeout(timeout);
        delete handlers[runId];
        opts.onDone(true);
      }
    };
    frame.srcdoc = buildDoc(opts.kind, opts.files, opts.main, opts.tests || [], runId);
    mount.appendChild(frame);
    return runId;
  }
  return { run: run };
})();

/* ---------- python runner (pyodide) ---------- */
const PyRunner = (function () {
  let py = null;
  let loadingPromise = null;
  let status = 'idle';
  const listeners = [];
  /* jsdelivr leads because it is the only mirror that serves the *packages*:
     cdnjs has the runtime but 404s pyodide-lock.json and CORS-blocks the wheels, so
     anything importing numpy or sympy failed there first and fell back anyway,
     costing a round trip and filling the console with errors on every lesson. */
  const SOURCES = [
    'https://cdn.jsdelivr.net/pyodide/v0.27.7/full/',
    'https://cdnjs.cloudflare.com/ajax/libs/pyodide/0.27.7/',
    'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/',
    'https://cdnjs.cloudflare.com/ajax/libs/pyodide/0.26.4/',
    'https://cdn.jsdelivr.net/pyodide/v0.25.1/full/',
  ];
  /* Sandboxed previews (e.g. artifact panes) relay fetch() to the host page via
     postMessage. Pyodide hands fetch URL objects, which cannot be structured-cloned
     ("DataCloneError: URL object could not be cloned") — so its .wasm download dies.
     hardenEnv() makes the runtime loadable there: every fetch input is reduced to a
     plain string, and wasm instantiation goes through an ArrayBuffer instead of
     streaming (streaming also breaks behind proxies that drop the wasm MIME type). */
  let hardened = false;
  function hardenEnv() {
    if (hardened) return;
    hardened = true;
    try {
      const origFetch = window.fetch;
      const PY_ASSET = /(cdnjs\.cloudflare\.com\/ajax\/libs\/pyodide\/|cdn\.jsdelivr\.net\/pyodide\/)/;
      function mirrorUrl(u) {
        let m = u.match(/cdnjs\.cloudflare\.com\/ajax\/libs\/pyodide\/([\d.]+)\/(.+)$/);
        if (m) return 'https://cdn.jsdelivr.net/pyodide/v' + m[1] + '/full/' + m[2];
        m = u.match(/cdn\.jsdelivr\.net\/pyodide\/v([\d.]+)\/full\/(.+)$/);
        if (m) return 'https://cdnjs.cloudflare.com/ajax/libs/pyodide/' + m[1] + '/' + m[2];
        return null;
      }
      function pause(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
      if (origFetch) {
        window.fetch = function (resource, init) {
          try {
            if (typeof URL !== 'undefined' && resource instanceof URL) resource = resource.href;
            else if (typeof Request !== 'undefined' && resource instanceof Request && !init &&
                     !resource.body && (resource.method || 'GET').toUpperCase() === 'GET') {
              resource = resource.url;
            } else if (resource && typeof resource === 'object' && typeof resource.href === 'string' && typeof resource.toString === 'function') {
              resource = String(resource);
            }
          } catch (e) { /* pass the original through untouched */ }
          if (typeof resource !== 'string' || !PY_ASSET.test(resource)) {
            return origFetch.call(this, resource, init);
          }
          /* pyodide runtime asset: sanitized init + retries + mirror CDN.
             Relayed environments fail sporadically ("Failed to fetch") and their
             synthesized responses can't satisfy integrity checks. */
          if (init) {
            init = Object.assign({}, init);
            delete init.integrity;
            delete init.cache;
          }
          const self = this;
          const urls = [resource];
          const alt = mirrorUrl(resource);
          if (alt) urls.push(alt);
          return (async function () {
            let lastErr = null;
            for (const url of urls) {
              for (let attempt = 0; attempt < 3; attempt++) {
                if (attempt > 0 || url !== resource) await pause(250 * (attempt + 1));
                try {
                  const r = await origFetch.call(self, url, init);
                  if (r && (r.ok || r.status === 0 || r.type === 'opaque')) return r;
                  lastErr = new Error('HTTP ' + (r && r.status));
                } catch (e) { lastErr = e; }
              }
            }
            throw (lastErr || new Error('Failed to fetch ' + resource));
          })();
        };
      }
    } catch (e) {}
    try {
      if (typeof WebAssembly !== 'undefined' && WebAssembly.instantiate) {
        WebAssembly.instantiateStreaming = async function (source, imports) {
          const resp = await source;
          const buf = await resp.arrayBuffer();
          return WebAssembly.instantiate(buf, imports);
        };
        WebAssembly.compileStreaming = async function (source) {
          const resp = await source;
          const buf = await resp.arrayBuffer();
          return WebAssembly.compile(buf);
        };
      }
    } catch (e) {}
  }
  function setStatus(s) { status = s; listeners.forEach(function (fn) { try { fn(s); } catch (e) {} }); }
  function onStatus(fn) { listeners.push(fn); fn(status); }
  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      const el = document.createElement('script');
      const timer = setTimeout(function () { reject(new Error('timeout')); }, 45000);
      el.src = src;
      el.onload = function () { clearTimeout(timer); resolve(); };
      el.onerror = function () { clearTimeout(timer); reject(new Error('load failed')); };
      document.head.appendChild(el);
    });
  }
  function ensure() {
    if (py) return Promise.resolve(py);
    if (!loadingPromise) {
      loadingPromise = (async function () {
        setStatus('loading');
        hardenEnv();
        const initNoise = [];
        function collectNoise(line) {
          initNoise.push(String(line));
          if (initNoise.length > 60) initNoise.shift();
        }
        for (const base of SOURCES) {
          try {
            await loadScript(base + 'pyodide.js');
            if (typeof loadPyodide !== 'function') continue;
            const p = await loadPyodide({ indexURL: base, stderr: collectNoise });
            try { p.setStderr(); } catch (e) {}
            py = p;
            setStatus('ready');
            return p;
          } catch (err) { collectNoise(String((err && err.message) || err)); /* next source */ }
        }
        setStatus('error');
        if (initNoise.length) {
          try { console.warn('[codewright] python runtime init failed — last messages:\n' + initNoise.slice(-8).join('\n')); } catch (e) {}
        }
        /* This used to say "download codewright.html and open it directly". That file
           is a local build artifact and has never been published, so the instruction
           was not actionable for anyone reading it on the site — and since the catalog
           was split out it would also be the wrong advice, because the published page
           fetches its courses and a file:// copy cannot. Name the actual cause. */
        throw new Error('The Python runtime could not be started here. Embedded previews sometimes block the ~10 MB download it needs from cdnjs.cloudflare.com — open this page in a normal browser tab rather than inside an embedded preview, then press Run again. Web and JavaScript lessons work everywhere either way.');
      })();
      loadingPromise.catch(function () { loadingPromise = null; });
    }
    return loadingPromise;
  }
  function formatPyError(e, mainName) {
    const msg = String((e && e.message) || e);
    const lines = msg.split('\n');
    const keep = [];
    for (let i = 0; i < lines.length; i++) {
      const l = lines[i];
      if (l.indexOf('_pyodide/_base.py') !== -1 || l.indexOf('pyodide/webloop') !== -1 || l.indexOf('site-packages/pyodide') !== -1) {
        i++; /* skip its source line too */
        continue;
      }
      keep.push(l);
    }
    return keep.join('\n').split('File "<exec>"').join('File "' + mainName + '"').trim();
  }
  function pyTestMessage(e) {
    const lines = String((e && e.message) || e).trim().split('\n');
    const last = (lines[lines.length - 1] || 'failed').trim();
    if (last === 'AssertionError') return 'Assertion failed';
    if (last.indexOf('AssertionError: ') === 0) return last.slice(16);
    /* A check reads the learner's variables by name, so a NameError here means their
       program never created one — not that anything is broken. Raw Python wording
       ("name 'subtotal' is not defined. Did you mean: 'max'?") sends people hunting
       for a typo instead, so say what the check actually wanted. */
    const nameErr = last.match(/^NameError: name '([^']+)' is not defined/);
    if (nameErr) {
      return 'Your program never creates ' + nameErr[1] + '. This check reads your ' +
        'variables directly, so ' + nameErr[1] + ' needs a line of its own \u2014 ' +
        nameErr[1] + ' = \u2026 \u2014 rather than being computed inside the print.';
    }
    return last;
  }
  async function runOne(opts) {
    const p = await ensure();
    setStatus('running');
    try {
      try { await p.loadPackagesFromImports(opts.files.map(function (f) { return f.content; }).join('\n')); } catch (e) {}
      const dir = '/home/pyodide';
      for (const f of opts.files) {
        try { p.FS.writeFile(dir + '/' + f.name, f.content); } catch (e) {}
      }
      const mods = opts.files
        .filter(function (f) { return /\.py$/.test(f.name) && f.name !== opts.main; })
        .map(function (f) { return f.name.slice(0, -3); });
      p.runPython(
        'import sys, os, importlib\n' +
        'os.chdir(' + JSON.stringify(dir) + ')\n' +
        'if ' + JSON.stringify(dir) + ' not in sys.path:\n' +
        '    sys.path.insert(0, ' + JSON.stringify(dir) + ')\n' +
        'for _m in ' + JSON.stringify(mods) + ':\n' +
        '    sys.modules.pop(_m, None)\n' +
        'importlib.invalidate_caches()\n'
      );
      let out = '';
      p.setStdout({ batched: function (s) { out += s + '\n'; opts.onConsole('log', s); } });
      p.setStderr({ batched: function (s) { opts.onConsole('error', s); } });
      const mainFile = opts.files.find(function (f) { return f.name === opts.main; });
      const ns = p.globals.get('dict')();
      ns.set('__name__', '__main__');
      let ok = true;
      try {
        await p.runPythonAsync(mainFile.content, { globals: ns });
      } catch (e) {
        ok = false;
        opts.onConsole('error', formatPyError(e, opts.main));
      }
      p.setStdout();
      p.setStderr();
      const results = [];
      ns.set('_out', out);
      for (const t of (opts.tests || [])) {
        try {
          p.runPython(dedent(t.code), { globals: ns });
          results.push({ name: t.name, pass: true });
        } catch (e) {
          results.push({ name: t.name, pass: false, message: pyTestMessage(e) });
        }
      }
      try { ns.destroy(); } catch (e) {}
      return { ok: ok, results: results };
    } finally {
      setStatus('ready');
    }
  }
  /* One Pyodide instance, one set of global stdout/stderr hooks. Two overlapping
     runs would rebind each other's streams mid-flight, so output lands in the wrong
     panel and whichever finishes first unhooks the other. Callers no longer have to
     know that: runs queue. */
  let pyChain = Promise.resolve();
  function run(opts) {
    const next = pyChain.then(function () { return runOne(opts); },
                              function () { return runOne(opts); });
    pyChain = next.then(function () {}, function () {});
    return next;
  }
  return { run: run, ensure: ensure, onStatus: onStatus, getStatus: function () { return status; } };
})();

/* ---------- account sync ----------
   Optional by design. The app is a single file that has to keep working with no
   server at all, so every call here fails soft: if the API is not reachable the
   learner simply stays on local storage and is told so, rather than being blocked.

   The token goes in an Authorization header rather than a cookie. That keeps the app
   usable from a different origin than the server, and means no credential is ever
   sent ambiently — so there is nothing for a cross-site request to abuse. */
const Sync = (function () {
  const K_TOKEN = 'codex-learn-token';
  const K_BASE = 'codex-learn-server';
  const K_USER = 'codex-learn-user';
  const mem = {};

  function get(k) { try { const v = localStorage.getItem(k); return v === null ? (mem[k] || null) : v; } catch (e) { return mem[k] || null; } }
  function set(k, v) { mem[k] = v; try { localStorage.setItem(k, v); } catch (e) {} }
  function del(k) { delete mem[k]; try { localStorage.removeItem(k); } catch (e) {} }

  function defaultBase() {
    if (typeof location === 'undefined') return '';
    return /^https?:$/.test(location.protocol) ? location.origin : '';
  }
  function base() { return (get(K_BASE) || defaultBase()).replace(/\/+$/, ''); }
  function setBase(url) {
    const u = String(url || '').trim().replace(/\/+$/, '');
    if (u) set(K_BASE, u); else del(K_BASE);
  }
  function token() { return get(K_TOKEN) || ''; }
  function user() { try { return JSON.parse(get(K_USER) || 'null'); } catch (e) { return null; } }
  function signedIn() { return !!token(); }
  function forget() { del(K_TOKEN); del(K_USER); }

  async function call(path, method, body, auth, timeoutMs) {
    const b = base();
    if (!b) throw new Error('No sync server configured.');
    const headers = {};
    if (body !== undefined) headers['Content-Type'] = 'application/json';
    if (auth) {
      const t = token();
      if (!t) throw new Error('Not signed in.');
      headers['Authorization'] = 'Bearer ' + t;
    }
    /* A machine that cannot see the server must not be able to hold the app hostage:
       an unreachable host can leave fetch pending for a minute or more, and the boot
       path awaits this. Everything here is bounded. */
    const ctrl = (typeof AbortController !== 'undefined') ? new AbortController() : null;
    const timer = setTimeout(function () { if (ctrl) ctrl.abort(); }, timeoutMs || 12000);
    let res;
    try {
      res = await fetch(b + path, {
        method: method,
        headers: headers,
        body: body === undefined ? undefined : JSON.stringify(body),
        credentials: 'omit',
        signal: ctrl ? ctrl.signal : undefined,
      });
    } catch (e) {
      throw new Error((e && e.name === 'AbortError')
        ? 'The sync server did not answer in time.'
        : 'Could not reach the sync server.');
    } finally {
      clearTimeout(timer);
    }
    let data = null;
    try { data = await res.json(); } catch (e) { data = null; }
    if (!res.ok) {
      const err = new Error((data && data.error) || ('Request failed (' + res.status + ')'));
      err.status = res.status;
      if (res.status === 401) forget();          /* the session is gone; drop the stale token */
      throw err;
    }
    return data || {};
  }

  async function health(timeoutMs) {
    if (!base()) return { ok: false, reason: 'none' };
    try {
      const r = await call('/api/health', 'GET', undefined, false, timeoutMs || 4000);
      return { ok: !!r.ok };
    } catch (e) {
      return { ok: false, reason: 'unreachable' };
    }
  }

  function device() {
    const ua = (typeof navigator !== 'undefined' && navigator.userAgent) || '';
    const m = ua.match(/(Windows|Macintosh|Linux|Android|iPhone|iPad)/);
    return m ? m[1] : 'device';
  }

  async function register(email, password) {
    const r = await call('/api/register', 'POST', { email: email, password: password, device: device() });
    set(K_TOKEN, r.token);
    set(K_USER, JSON.stringify(r.user));
    return r.user;
  }
  async function login(email, password) {
    const r = await call('/api/login', 'POST', { email: email, password: password, device: device() });
    set(K_TOKEN, r.token);
    set(K_USER, JSON.stringify(r.user));
    return r.user;
  }
  async function logout() {
    try { await call('/api/logout', 'POST', {}, true); } catch (e) {}
    forget();
  }
  async function pull() { return call('/api/progress', 'GET', undefined, true); }
  async function push(progress, timeoutMs) { return call('/api/progress', 'PUT', { progress: progress }, true, timeoutMs); }

  return {
    base: base, setBase: setBase, hasDefaultBase: function () { return !!defaultBase(); },
    signedIn: signedIn, user: user, forget: forget,
    health: health, register: register, login: login, logout: logout,
    pull: pull, push: push,
  };
})();

/* ---------- persistent store ---------- */
const Store = (function () {
  const KEY = 'codewright-progress-v1';
  const mem = {};
  /* Which backend actually took the last write, so the app can tell the truth about
     whether progress survives a reload instead of silently dropping it. */
  let mode = 'unknown';        /* 'backend' | 'local' | 'memory' */
  let lastError = '';
  function localAvailable() {
    try {
      localStorage.setItem(KEY + ':probe', '1');
      localStorage.removeItem(KEY + ':probe');
      return true;
    } catch (e) {
      lastError = String((e && e.name) || e);
      return false;
    }
  }
  async function backendGet() {
    if (typeof window !== 'undefined' && window.storage && window.storage.get) {
      try {
        const r = await window.storage.get(KEY);
        return r && r.value ? r.value : null;
      } catch (e) { /* missing key or unavailable */ }
    }
    try { return localStorage.getItem(KEY); } catch (e) {}
    return mem[KEY] || null;
  }
  async function backendSet(value) {
    let saved = false;
    if (typeof window !== 'undefined' && window.storage && window.storage.set) {
      try {
        const r = await window.storage.set(KEY, value);
        saved = !!r;
        if (saved) mode = 'backend';
      } catch (e) { saved = false; lastError = String((e && e.message) || e); }
    }
    try {
      localStorage.setItem(KEY, value);
      saved = true;
      if (mode !== 'backend') mode = 'local';
    } catch (e) {
      lastError = String((e && e.name) || e);
    }
    mem[KEY] = value;
    if (!saved) mode = 'memory';
    return saved;
  }
  async function load() {
    try {
      const raw = await backendGet();
      if (!raw) return null;
      return JSON.parse(raw);
    } catch (e) { return null; }
  }
  async function save(obj) {
    try { return await backendSet(JSON.stringify(obj)); } catch (e) { return false; }
  }
  /* The unload write. A page that is going away cannot await anything: `pagehide` runs
     its handlers and the document is gone, and a promise continuation queued inside one
     may never be reached at all. save() defers its whole body through `await`, so the
     app's debounced save had no way to land the last few hundred milliseconds of work.
     This is backendSet's localStorage half with the awaits taken out — everything it can
     honestly finish before the handler returns, and nothing it cannot. The backend needs
     a round trip, so it is deliberately not attempted here; the next open syncs it. */
  function saveSync(obj) {
    let value;
    try { value = JSON.stringify(obj); } catch (e) { return false; }
    mem[KEY] = value;
    try {
      localStorage.setItem(KEY, value);
      if (mode !== 'backend') mode = 'local';
      return true;
    } catch (e) {
      lastError = String((e && e.name) || e);
      if (mode !== 'backend') mode = 'memory';
      return false;
    }
  }
  /* Called before the first save so the UI can warn straight away rather than after
     the learner has already earned progress they are about to lose. */
  function status() {
    if (mode === 'unknown') {
      if (typeof window !== 'undefined' && window.storage && window.storage.set) mode = 'backend';
      else mode = localAvailable() ? 'local' : 'memory';
    }
    return {
      mode: mode,
      persistent: mode !== 'memory',
      error: lastError,
      fromFile: (typeof location !== 'undefined' && location.protocol === 'file:'),
    };
  }
  return { load: load, save: save, saveSync: saveSync, status: status, key: KEY };
})();
