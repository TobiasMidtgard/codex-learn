# Codex Learn — learn by building

A zero-install code learning platform that runs entirely in one HTML file: a real
editor with syntax highlighting and autocomplete, a Python runtime (Pyodide), a
sandboxed web preview, and automated checks on every exercise.

The interface implements the **Codex Learn** design from Claude Design
(`design/Codex Learn.dc.html`, kept in the repo for reference): a dark
`#08090B` ground with drifting ambient light, a 72px glass icon rail, a blurred
header carrying search and live streak/XP, and an acid-lime `#C7F751` accent
used for progress, focus and success. Instrument Sans sets the interface;
JetBrains Mono carries code, labels and every figure.

**[Open it →](https://tobiasmidtgard.github.io/codex-learn/)** — nothing to install.

It ships two things:

1. **Five foundation tracks** — Python, Web, Backend, Data Structures & Algorithms,
   and the Developer Toolkit. Readings, quizzes and auto-checked coding tasks.
2. **A five-year Computer Science degree catalog** — 32 courses from first
   principles to a capstone engineering project, each with 3–5 modules, an
   interactive lab per module, and a portfolio-grade capstone with a marking rubric.

Everything a student writes is checked by tests that actually execute their code.

## Run it

The published copy at
**<https://tobiasmidtgard.github.io/codex-learn/>** needs nothing at all — open it on
any machine and start. Everything runs in the browser, and progress is stored in that
browser.

To run it locally, with accounts and cross-device sync:

```bash
node build.mjs && node server/server.mjs
```

Then open <http://localhost:4173>. That serves the app **and** the account API.
`node tools/serve.mjs` serves the static file alone.

> **The published site is static.** GitHub Pages can only serve files, so there is no
> account API behind it: on that URL, progress lives in the browser you are using, and
> **Export / Import progress** on the Profile screen is how you move it between
> machines. Signing in needs `server/server.mjs` running somewhere both machines can
> reach — point the Profile screen at its address to use it.

Rebuilding writes both `build/codewright.html` and `docs/index.html`; the second is
what Pages publishes, so a push updates the live site.

`build/codewright.html` is fully self-contained — you can also just open that file
directly in a browser, or host it anywhere as a static asset. The only network
request it ever makes is the Pyodide runtime (~10 MB, from a CDN, on the first
Python run); web and JavaScript labs work offline.

## Layout

```
design/
  Codex Learn.dc.html  the imported Claude Design source (reference)
  support.js           its dc-runtime (reference; not shipped)
src/
  index.head.html    doctype, design tokens, all styles, theme bootstrap
  lang.js            language model, type inference, completion, highlighting
  studio.js          LaTeX->MathML, symbolic answer checking, sandbox visualisers
  bundle.1-3.txt     foundation-track content ("@@ key" sections)
  tracks.js          the TRACKS array — foundation curriculum
  engine.js          utilities, highlighter, markdown, editor, runners, storage
  app.js             state, routing, and every view
catalog/
  _spine*.json       one per programme: bands, and the course table
  authors/<ID>.py    one authoring module per course (source of truth)
  <ID>.json          emitted, validated course data (generated)
server/
  server.mjs         serves the app + the account/sync API
  auth.mjs           scrypt hashing, session tokens, login throttling
  store.mjs          one JSON file per account, atomic writes
  merge.mjs          combines two devices' progress without losing either
tools/
  emit.py            author module -> validated JSON
  verify_labs.py     executes every lab against real CPython
  test_api.mjs       end-to-end exercise of the account API
  serve.mjs          static server, no accounts
build.mjs            assembles everything into build/ and docs/
docs/index.html      the published build (GitHub Pages serves this)
data/                accounts and progress (created at runtime, gitignored)
```

## Working on the curriculum

Courses are authored as Python modules rather than JSON so that code samples can be
written literally, in `r'''…'''` blocks, instead of as escaped JSON strings.

```bash
python tools/emit.py catalog/authors/CS101.py     # validate + emit JSON
python -X utf8 tools/verify_labs.py catalog/CS101.json
node build.mjs
```

`emit.py` enforces the schema: 3–5 modules, a lab per module, a capstone whose
rubric weights sum to exactly 100, a solution that only touches starter files, and
so on. It refuses to emit anything malformed.

`verify_labs.py` is the real gate. For every lab it reproduces the browser runner's
semantics with local CPython — same globals dict, same captured `_out`, same dedent
— and answers two questions:

1. Does the reference **solution** pass all of its own checks? (must be yes)
2. Does the **starter** fail at least one? (must be yes, or the exercise is
   pre-solved)

It also rejects imports that do not exist in the browser sandbox.

```
[ok  ] CS210    5 labs
          CS210/M1       solution 8/8 · starter 0/8
          ...
All good: 141 labs verified across 27 courses.
```

### Authoring rules that matter

- Every multi-line string uses `r'''…'''`, never `r"""…"""` — code samples contain
  `"""docstrings"""` that would close the block early.
- Code inside those blocks starts at column 0; a stray leading space is an
  `IndentationError` for the student.
- Standard library only. No numpy/pandas/pytest — they do not exist in Pyodide.
- Seed every RNG. Tests must be deterministic.
- Every expected value in a test must be one you computed, not one you assumed.

## How the runners work

**Python** labs run in Pyodide. The student's `main` file executes with a fresh
globals dict (`__name__ == "__main__"`); stdout is captured into `_out`; each check
is then executed in that same namespace, in order.

**Web / JavaScript** labs run in an iframe sandboxed with `allow-scripts` only. A
harness injected ahead of the student's code forwards `console.*` to the app's
console pane, provides `assert` / `assertEqual`, and installs a memory-backed
`localStorage` (the opaque sandbox origin makes the real one throw, and granting
`allow-same-origin` would let lab code reach back into the app).

**Examples in the reading material** run where they sit. Every fenced Python, JS or
HTML block carries a Run button that opens an output drawer directly underneath it —
console output for Python and JavaScript, a live sandboxed frame for HTML. Running an
example never navigates, re-renders the view, or touches the lesson tree, so the
reader keeps their place in the material. `Playground ↗` is still there for anyone
who wants a full editor, and the Playground it opens carries a one-click way back.

## Progress, and where it lives

Progress is always written locally first, to `localStorage` under
`codewright-progress-v1` (or the host's storage API when one is present). Signing in
adds a second copy on the server so it follows you between machines; the app works
exactly as well without one.

The **Profile** screen — the avatar at the bottom of the icon rail — says which of
those is actually happening, and says so plainly when neither is:

- Opening `codewright.html` straight off disk gives it a `file://` origin, and browsers
  refuse storage there. Nothing persists, and before this was surfaced the app looked
  like it was saving. It now shows **Not saved** in the header and explains why.
- Private windows and blocked-cookie settings do the same thing.

Either way **Export progress** writes a small JSON file and **Import progress** reads it
back, which is also how you move progress to another browser or machine. Serving the
file over http (`node tools/serve.mjs`) makes saving work normally.

## Accounts and sync

`node server/server.mjs [port]` serves the built app and a small JSON API. Accounts
live in `data/` as one file each — no database, nothing to install, and the whole
store is readable and trivially backed up.

| | |
|---|---|
| `POST /api/register`, `/api/login` | returns a bearer token |
| `POST /api/logout` | revokes just that session |
| `GET`/`PUT /api/progress` | read and sync a progress document |
| `GET /api/health` | what the client probes before offering sign-in |

**How syncing behaves.** Every sync is a push that returns the merged document, and
the client adopts what comes back — so each save is a convergence point and there is
no conflict UI to get wrong. The merge can only move progress forward: completed units
are unioned, quiz scores take the best, activity takes the higher count per day, saved
code takes whichever device wrote it last, and XP is recomputed from the merged
`completed` set. Two machines working independently end up agreeing exactly.

One rule worth naming, because the first version got it wrong: a machine signing in
for the first time is empty but has the newest clock, so "newest wins" alone let its
blank fields erase the account's name. An unset field never overwrites a set one.

**Security posture.** Passwords are scrypt with a per-account salt, compared in
constant time; only the parameters and the digest are stored. Session tokens are 32
random bytes, and the server keeps only their SHA-256 — a copy of `data/` cannot be
used to sign in. Sign-in is throttled per address *and* email, an unknown email and a
wrong password give the same answer, request bodies are capped, and the token travels
in an `Authorization` header rather than a cookie, so nothing is sent ambiently and
there is no CSRF surface. It is a personal-scale server: fine on a machine you
control or a private network, and it wants TLS in front of it before it goes public.

## The editor

Completion is not a list of words in the file. `src/lang.js` holds a hand-written
model of each language — types and their members, module contents, builtins,
keywords and snippets — where every entry carries a signature, a one-line
explanation, and the type it returns. The return type is what makes chains work.

`analyze()` then reads the buffer and infers what each name holds: assignments,
function parameters, loop variables, `with ... as`, imports, `self.x`, destructuring.
It is not a type checker and does not try to be — a half-written buffer is rarely
valid — so anything it cannot prove cheaply simply has no type and falls back to a
generic pool.

`Complete.suggest()` decides what is valid at the caret:

| At the caret | What you get |
|---|---|
| `name.` | the members of whatever `name` holds — `str`, `list`, `Element`… |
| `s.upper().` | string members again; return types flow through calls |
| `math.` | that module's contents |
| `from random import ` | that module's contents |
| `print(` | the signature, with the current argument in bold |
| `sorted(items, ` | `key=` and `reverse=` first, as keyword arguments |
| `raise Val` | exceptions only |
| `new M` | constructors only |
| inside a function | its parameters, marked as parameters |
| anywhere | locals, functions, classes, imports, builtins, keywords, snippets |

Suggestions open while typing, after `.` or `<`, and on **Ctrl+Space**. Arrow keys and
PageUp/PageDown move; **Enter** or **Tab** accepts; **Escape** dismisses. Every entry
shows its kind — Variable, Parameter, Function, Method, Property, Field, Type,
Interface, Keyword, Constant, Snippet, Module — with its own icon and colour, its
signature on the right, and a documentation card beside the list.

Matching is fuzzy the way an editor's is: `qsa` finds `querySelectorAll` by its
capitals, and the characters that matched are highlighted in the list.

Accepting does the right thing for what was accepted. A function gets its parentheses
and the caret inside them, an attribute gets `=""` with the caret between the quotes,
an HTML tag gets its closing tag, and a snippet expands with tab stops — `forr`
becomes a counted loop with `i` selected, Tab moves to `n`. (Each stop appears once in
a body: mirrored placeholders would need linked editing, and a half-implemented
version that silently desynchronised would be worse than none.)

## Writing HTML

Type a tag name as a plain word at the start of a line and accepting it writes the
whole element:

```
div        ->  <div>|</div>
h1         ->  <h1>|</h1>
img        ->  <img|>          void: no closing tag, caret inside for attributes
br         ->  <br>|           never takes attributes, so the caret moves past it
```

Typing `<` also works anywhere and pairs to `<>`; finishing a start tag writes its
closer; `</` fills in whichever element is still open, innermost first.

Bare words only trigger at the **start of a line**: half the tag names (`a`, `p`,
`code`, `form`, `section`, `table`) are also ordinary English, and a menu appearing
mid-sentence makes prose miserable to write. Mid-line, type `<`. Nothing fires inside
a `script` or `style` body, so `if (a < b)` types normally.

## Colour

Tokens are classed by role rather than by shape, because the roles are what a reader
needs to tell apart:

- keywords split three ways — control flow, declarations, and word operators
- a name being **defined** is brighter than the same name being read; parameters,
  properties and methods each keep their own colour
- `self` / `this` are distinct from ordinary variables, and `UPPER_CASE` from both
- escapes inside a string, and the expressions inside f-strings and template
  literals, are coloured as what they are rather than as more string
- docstrings are separated from comments; CSS units from their numbers; HTML
  attribute values from attribute names

Both themes are defined token by token; the light palette is not an inversion.

## Programmes

Two majors: a five-year **Computer Science** degree and a graduate **Electrical
Engineering** M.S. A course is placed by `(program, band)`, where a band is a *year*
in CS and a *track* in EE — one neutral word so a track is never labelled "Year 1".
Each programme is a `catalog/_spine*.json`; the build stamps `program` and `band` onto
every course and refuses duplicate ids, because the lesson keyspace is flat and shared
with the foundation track ids.

## The graduate teaching loop

An EE module is three units rather than one, following the shape the curriculum was
specified with:

| Unit | Type | What it is |
|---|---|---|
| Look at it | `sandbox` | a parameter you can move and a consequence you can watch, before any algebra |
| Derive it | `derive` | scaffolded steps, each gated on an answer you type |
| Build it | `code` / `project` | the lab, unchanged from the rest of the platform |

**Mathematics** is written as LaTeX in `$…$` and `$$…$$` and rendered to native
**MathML** — no library, no fonts, nothing fetched. The supported subset is
fractions, scripts, radicals, accents, Greek, matrices, `\text` and the operators this
curriculum uses; anything outside it renders as its own source in monospace, so it is
visibly not understood rather than silently wrong. Markdown pulls maths out before
parsing and puts it back after, because an expression is full of the `_` and `*` that
emphasis wants to eat.

**Answers are checked as mathematics, not as strings.** SymPy runs in Pyodide and
decides equivalence, so `1/(1+sRC)` and `(1/RC)/(s+1/RC)` both pass. Three things had
to be right for that to hold:

- implicit multiplication binds tighter than division. Written maths reads `1/RC` as
  `1/(RC)`; Python reads it as `(1/R)*C`, so the first thing anyone types for a
  first-order pole was being marked wrong.
- a `{…}` pattern cannot nest, so `\sqrt{1-\zeta^{2}}` lost its root entirely.
  Scripts are collapsed first and every argument pass iterates innermost-out.
- symbols the lesson declares are matched whole, so `V_out` stays one symbol while
  `RC` becomes `R*C`.

**Diagnostics are the point.** A wrong answer is tested against the usual mistakes, so
the learner is told *"that is the reciprocal"*, *"those are hertz, the question asked
in rad/s"*, or *"nothing in your answer depends on C"* — rather than being shown the
answer and learning nothing. A step that will not come can be broken into smaller
ones instead of surrendered.

**Sandboxes** are canvas visualisers with declared parameters. They compute honestly
— the step response is a real second-order solution, the Bode plot a real sweep — so
what the learner sees is what the mathematics they are about to derive actually says.
Each one releases its canvas and observers through the view's `teardown`; the
`teardownFns` array that looks like a cleanup registry is never drained.

## Verification status

All 32 courses, 137 modules, 137 labs and 1,359 automated checks are bundled.

| Gate | Result |
|---|---|
| `tools/test_api.mjs`, account + sync API | 30/30 |
| `emit.py` schema validation, 32 courses | pass |
| `verify_labs.py` against CPython, 169 labs | 169/169 |
| Every Python lab re-run in real browser Pyodide | 164/164 labs, 1,319 checks |
| WEB301 web labs driven through the real iframe runner | 39/40 assertions |

The one web assertion not confirmed is a grid-geometry check: the automated pass
ran in a browser pane that never composites, so the preview iframe reports
`clientWidth: 0` and every rectangle measures zero. The cards and CSS it inspects
are present; it passes in a normally displayed browser.

### Divergences the CPython gate could not see

Running everything a second time inside real Pyodide caught four bugs that local
CPython had happily passed, which is why both gates exist:

- `hashlib.pbkdf2_hmac` does not exist in Pyodide. CAP501 now writes the PBKDF2
  loop out with `hmac` + `sha256`, which is better teaching for a security module
  anyway.
- `localStorage` throws in a `sandbox="allow-scripts"` iframe (opaque origin), so
  the harness now installs a memory-backed Storage rather than weakening the
  sandbox with `allow-same-origin`.
- Browser timers are coarse: a fast stage measured 0.0 s, giving a division by
  zero. HPC401's benchmark now auto-ranges like `timeit`, and CAP501's budget
  compares strictly (`per_call < budget`) so a zero budget is never "met".
- `inspect.getsource` cannot see a function defined in the main file, because
  Pyodide compiles it from a string named `<exec>`. `verify_labs.py` now compiles
  the same way, so the harness can never again be more permissive than the
  browser.
