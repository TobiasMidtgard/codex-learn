"""WEB301 — Full-Stack & Mobile Development. Web-runtime author module."""

COURSE = {
    "id": "WEB301",
    "title": "Full-Stack & Mobile Development",
    "year": 3,
    "level": "Intermediate",
    "prereqs": ["CS220", "SE201"],
    "stack": ["HTML", "CSS", "JavaScript", "Python"],
    "credits": 15,
    "hours": 160,
    "icon": "⬚",
    "summary": (
        "The browser is the runtime for this course. You write the document a screen "
        "reader can navigate, the stylesheet that survives a 360px phone, the render "
        "loop that turns an array into a list, and the async layer that talks to an "
        "HTTP API without lying to the user about what is happening. Every lab is a "
        "real page: markup, stylesheet and script, checked in the browser that runs it."
    ),
    "outcomes": [
        "Write markup whose landmarks, heading order and labels convey structure without CSS",
        "Bind every form control to a name a screen reader announces, and wire hints with aria-describedby",
        "Build a responsive layout from flexbox and CSS grid with an explicit breakpoint",
        "Derive the DOM from a single state object, re-rendering rather than patching by hand",
        "Delegate events from a stable container so handlers survive a re-render",
        "Handle the loading, empty, error and success states of an asynchronous request explicitly",
        "Persist client state across reloads and recover from unreadable storage",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "MDN Web Docs — HTML, CSS and JavaScript references, developer.mozilla.org",
        "W3C Web Accessibility Initiative, *ARIA Authoring Practices Guide* — patterns and forms",
        "Haverbeke, *Eloquent JavaScript*, 4th ed. — chapters 13-18, the browser platform",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Documents people can actually use",
            "summary": "Semantic elements, heading order, labelled controls and honest alt text.",
            "concepts": [
                "The document outline: header / nav / main / footer as landmarks, not decoration",
                "Exactly one `h1`; heading levels describe nesting and must never skip",
                "`<label for>` binds to a control `id` — placeholder text is not a label",
                "Grouped controls need `<fieldset>` and a `<legend>` to be announced as a set",
                "`alt` describes the image's purpose; an empty `alt` marks it decorative",
                "`aria-describedby` attaches supplementary text without repeating the label",
                "Native elements first: a `<button>` is focusable, activatable and announced for free",
            ],
            "lab": {
                "title": "A booking form a screen reader can navigate",
                "runtime": "web",
                "minutes": 40,
                "brief": r'''
`index.html` is a working page built entirely from `<div>`s. It looks fine and
conveys nothing: no landmarks, no headings, no labels, no alt text. Rewrite the
markup so the structure survives without the stylesheet.

`style.css` is read-only — it already styles the semantic elements you are about
to introduce, so do not add classes to work around it.

What the page must contain:

- a `<header>` holding the `<h1>` and a `<nav>` with an `aria-label`
- a `<main>` with `<h2>` sections `Services` (id `services`) and
  `Book a service` (id `booking`), and an `<h3>` under the first — heading levels
  must never jump by more than one
- at least one `<img>` with alt text that describes what it shows
- a `<form id="booking-form">` in which **every** control has an `id` and a
  matching non-empty `<label for="...">`
- the two service-level radios inside a `<fieldset>` with a `<legend>`
- an email field with `id="email"`, `type="email"`, `required`, and its hint
  wired up with `aria-describedby`
- a `<footer>`

Keep the same words on the page. This is a markup exercise, not a rewrite.
''',
                "files": [
                    {"name": "index.html", "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Riverside Bike Workshop</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<div class="banner">
  <div class="brand">Riverside Bike Workshop</div>
  <div class="menu">
    <a href="#services">Services</a>
    <a href="#booking">Book a service</a>
  </div>
</div>

<div class="content">
  <div class="section-title">Services</div>
  <img src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='480' height='200'%3E%3Crect width='480' height='200' fill='%23d9e2ec'/%3E%3C/svg%3E">
  <div class="sub-title">Standard tune-up</div>
  <p>Gears indexed, brakes bled, wheels trued and bearings checked. Two working days.</p>

  <div class="section-title">Book a service</div>
  <form id="booking-form" action="#" method="post">
    <p>Full name <input type="text" name="name"></p>
    <p>Email address <input type="text" name="email">
      <span class="hint">We only use this to confirm the booking.</span></p>
    <p>Service level
      <input type="radio" name="level" value="basic" checked> Basic
      <input type="radio" name="level" value="full"> Full strip-down</p>
    <p>Anything we should know? <textarea name="notes" rows="3"></textarea></p>
    <button type="submit">Request booking</button>
  </form>
</div>

<div class="foot">Riverside Bike Workshop, 14 Mill Lane. Open Tuesday to Saturday.</div>

</body>
</html>
'''},
                    {"name": "style.css", "ro": True, "content": r'''
:root {
  --ink: #1b1f27;
  --muted: #5a6270;
  --rule: #d7dce4;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: var(--ink);
  background: #fbfbfd;
  line-height: 1.55;
}

header, .banner {
  border-bottom: 1px solid var(--rule);
  padding: 1rem 1.25rem;
}

h1, .brand { font-size: 1.35rem; margin: 0 0 0.5rem; }

nav ul, .menu { display: flex; gap: 1rem; list-style: none; margin: 0; padding: 0; }

main, .content { max-width: 44rem; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }

h2, .section-title { font-size: 1.15rem; margin: 2rem 0 0.5rem; }
h3, .sub-title { font-size: 1rem; margin: 1rem 0 0.25rem; }

img { display: block; max-width: 100%; height: auto; border-radius: 8px; }

form p { margin: 0 0 0.9rem; }

label { display: inline-block; font-weight: 600; margin-bottom: 0.2rem; }

fieldset { border: 1px solid var(--rule); border-radius: 8px; margin: 0 0 0.9rem; }

legend { font-weight: 600; padding: 0 0.4rem; }

fieldset label { font-weight: 400; }

input[type="text"], input[type="email"], textarea {
  display: block;
  width: 100%;
  padding: 0.45rem 0.6rem;
  border: 1px solid var(--rule);
  border-radius: 6px;
  font: inherit;
}

.hint { display: block; color: var(--muted); font-size: 0.85rem; margin-top: 0.25rem; }

button {
  font: inherit;
  padding: 0.5rem 1rem;
  border: 0;
  border-radius: 6px;
  background: #1b1f27;
  color: #fff;
  cursor: pointer;
}

footer, .foot {
  border-top: 1px solid var(--rule);
  padding: 1rem 1.25rem;
  color: var(--muted);
  font-size: 0.9rem;
}
'''},
                ],
                "main": "index.html",
                "solution": [
                    {"name": "index.html", "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Riverside Bike Workshop</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<header>
  <h1>Riverside Bike Workshop</h1>
  <nav aria-label="Primary">
    <ul>
      <li><a href="#services">Services</a></li>
      <li><a href="#booking">Book a service</a></li>
    </ul>
  </nav>
</header>

<main>
  <h2 id="services">Services</h2>
  <img src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='480' height='200'%3E%3Crect width='480' height='200' fill='%23d9e2ec'/%3E%3C/svg%3E" alt="A road bicycle clamped in a workshop repair stand">
  <h3>Standard tune-up</h3>
  <p>Gears indexed, brakes bled, wheels trued and bearings checked. Two working days.</p>

  <h2 id="booking">Book a service</h2>
  <form id="booking-form" action="#" method="post">
    <p>
      <label for="name">Full name</label>
      <input id="name" name="name" type="text" autocomplete="name" required>
    </p>
    <p>
      <label for="email">Email address</label>
      <input id="email" name="email" type="email" autocomplete="email" required aria-describedby="email-hint">
      <span id="email-hint" class="hint">We only use this to confirm the booking.</span>
    </p>
    <fieldset>
      <legend>Service level</legend>
      <p>
        <input id="level-basic" name="level" type="radio" value="basic" checked>
        <label for="level-basic">Basic</label>
      </p>
      <p>
        <input id="level-full" name="level" type="radio" value="full">
        <label for="level-full">Full strip-down</label>
      </p>
    </fieldset>
    <p>
      <label for="notes">Anything we should know?</label>
      <textarea id="notes" name="notes" rows="3"></textarea>
    </p>
    <button type="submit">Request booking</button>
  </form>
</main>

<footer>
  <p>Riverside Bike Workshop, 14 Mill Lane. Open Tuesday to Saturday.</p>
</footer>

</body>
</html>
'''},
                ],
                "hints": [
                    "Swap the wrappers first: `.banner` becomes `<header>`, `.content` becomes `<main>`, `.foot` becomes `<footer>`, and the `.menu` becomes a `<nav>` holding a `<ul>` of links.",
                    "A label only counts when its `for` matches a control `id`. Give every input, textarea and select an `id`, then point a `<label for=\"that-id\">` at it.",
                    "Radios that share a `name` are one question: wrap them in `<fieldset>` and make the question itself the `<legend>`.",
                    "The hint span needs an `id`, and the email input needs `aria-describedby=\"that-id\"` — that is how the extra sentence gets announced after the label.",
                ],
                "tests": [
                    {"name": "The page has landmarks, not divs", "code": r'''
assertEqual(document.querySelectorAll('main').length, 1, 'There should be exactly one <main> landmark, found ' + document.querySelectorAll('main').length);
assert(document.querySelector('header') !== null, 'No <header> element on the page');
assert(document.querySelector('nav') !== null, 'No <nav> element on the page');
assert(document.querySelector('footer') !== null, 'No <footer> element on the page');
assert(document.querySelector('main #booking-form') !== null, 'The booking form belongs inside <main>');
'''},
                    {"name": "Heading levels tell the story", "code": r'''
var _hs = Array.prototype.slice.call(document.querySelectorAll('h1,h2,h3,h4,h5,h6'));
assertEqual(document.querySelectorAll('h1').length, 1, 'A page has exactly one <h1>, found ' + document.querySelectorAll('h1').length);
assert(_hs.length >= 4, 'Expected at least four headings (h1, two h2 sections and an h3), found ' + _hs.length);
assertEqual(_hs[0].tagName.toLowerCase(), 'h1', 'The first heading in the document should be the <h1>, found <' + _hs[0].tagName.toLowerCase() + '>');
var _prev = 0;
for (var _i = 0; _i < _hs.length; _i++) {
  var _lvl = Number(_hs[_i].tagName.charAt(1));
  assert(_lvl <= _prev + 1, 'Heading level jumped from h' + _prev + ' to h' + _lvl + ' at "' + _hs[_i].textContent.trim() + '" — never skip a level');
  _prev = _lvl;
}
assert(document.querySelector('h2#services') !== null, 'The Services heading should be <h2 id="services">');
assert(document.querySelector('h2#booking') !== null, 'The booking heading should be <h2 id="booking">');
'''},
                    {"name": "Every control carries a real label", "code": r'''
var _controls = document.querySelectorAll('#booking-form input, #booking-form select, #booking-form textarea');
assert(_controls.length >= 5, 'Expected at least five form controls, found ' + _controls.length);
for (var _j = 0; _j < _controls.length; _j++) {
  var _c = _controls[_j];
  var _what = _c.tagName.toLowerCase() + '[name=' + _c.name + ']';
  assert(_c.id && _c.id.trim() !== '', 'The ' + _what + ' control has no id, so no <label for> can point at it');
  var _lab = document.querySelector('label[for="' + _c.id + '"]');
  assert(_lab !== null, 'No <label for="' + _c.id + '"> anywhere in the document');
  assert(_lab.textContent.trim() !== '', 'The <label for="' + _c.id + '"> is empty');
}
'''},
                    {"name": "The radios are a labelled group", "code": r'''
var _radios = document.querySelectorAll('#booking-form input[type="radio"]');
assertEqual(_radios.length, 2, 'Expected two service-level radios, found ' + _radios.length);
var _fs = _radios[0].closest('fieldset');
assert(_fs !== null, 'Radio buttons that share a name are one question — wrap them in a <fieldset>');
assert(_fs.contains(_radios[1]), 'Both radios belong inside the same <fieldset>');
var _lg = _fs.querySelector('legend');
assert(_lg !== null, 'The <fieldset> has no <legend>');
assert(_lg.textContent.trim() !== '', 'The <legend> is empty — it should ask the question, e.g. "Service level"');
'''},
                    {"name": "Images describe themselves", "code": r'''
var _imgs = document.querySelectorAll('img');
assert(_imgs.length >= 1, 'The page should still show at least one <img>');
for (var _k = 0; _k < _imgs.length; _k++) {
  var _alt = _imgs[_k].getAttribute('alt');
  assert(_alt !== null, 'An <img> has no alt attribute at all — even decorative images need alt=""');
  assert(_alt.trim().length >= 10, 'The alt text "' + _alt + '" is too short to describe what the image shows');
}
'''},
                    {"name": "Navigation and the email field are wired up", "code": r'''
var _nav = document.querySelector('nav');
var _name = _nav.getAttribute('aria-label') || _nav.getAttribute('aria-labelledby');
assert(_name && _name.trim() !== '', 'Give the <nav> an aria-label so its purpose is announced');
assert(_nav.querySelectorAll('a[href]').length >= 2, 'The nav should still hold both links, found ' + _nav.querySelectorAll('a[href]').length);
var _email = document.getElementById('email');
assert(_email !== null, 'Expected the email control to have id="email"');
assertEqual(_email.type, 'email', 'The email field should use type="email", found type="' + _email.type + '"');
assert(_email.required, 'The email field should be required');
var _d = _email.getAttribute('aria-describedby');
assert(_d !== null, 'Wire the hint sentence to the email field with aria-describedby');
var _hint = document.getElementById(_d);
assert(_hint !== null, 'aria-describedby points at "' + _d + '", but no element has that id');
assert(_hint.textContent.trim() !== '', 'The element referenced by aria-describedby is empty');
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Responsive layout with flexbox and grid",
            "summary": "One navbar, one gallery, one breakpoint, and no sideways scrolling.",
            "concepts": [
                "The box model and why `box-sizing: border-box` removes a whole class of bugs",
                "Flexbox is one-dimensional: main axis, cross axis, `justify-content`, `align-items`",
                "CSS grid is two-dimensional: `grid-template-columns`, `fr` units, `gap`",
                "Mobile-first order: base rules, then `@media` overrides at a named breakpoint",
                "`max-width: 100%` on replaced elements is what stops images bursting their column",
                "Custom properties cascade and can be read from JavaScript with `getPropertyValue`",
                "Horizontal overflow is a layout bug: `scrollWidth` larger than `clientWidth`",
            ],
            "lab": {
                "title": "A gallery that survives a 360px phone",
                "runtime": "web",
                "minutes": 45,
                "brief": r'''
`index.html` is read-only: a header with a nav, and a `<ul id="gallery">` of six
`.card` items. Everything you write goes in `style.css`.

**Wide layout (the default rules)**

- `.site-nav` is a flex row that pushes `.brand` to one end and `.nav-list` to
  the other — `justify-content: space-between`
- `.nav-list` is a flex row with no bullets and a visible `gap`
- `#gallery` is a CSS grid of exactly **three** equal columns with a `gap`, and
  no bullets
- `.card-img` is `display: block` with `max-width: 100%` so it shrinks with its
  column instead of overflowing

**Narrow layout (`@media (max-width: 640px)`)**

- `.nav-list` stacks: `flex-direction: column`
- `#gallery` collapses to a single column

**The breakpoint token**

Publish the active breakpoint so JavaScript can read it. On `:root` declare
`--layout: wide;`, and inside the media query re-declare `--layout: narrow;`.
The checks read it back with
`getComputedStyle(document.documentElement).getPropertyValue('--layout')` and
compare it against `matchMedia('(max-width: 640px)')`, so the page is checked at
whatever width it happens to be showing.

Whatever the width, the page must not scroll sideways.
''',
                "files": [
                    {"name": "index.html", "ro": True, "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Print Studio</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<header class="site-header">
  <nav class="site-nav" aria-label="Primary">
    <a class="brand" href="#top">Print Studio</a>
    <ul class="nav-list">
      <li><a href="#gallery">Gallery</a></li>
      <li><a href="#about">About</a></li>
      <li><a href="#contact">Contact</a></li>
    </ul>
  </nav>
</header>

<main id="top">
  <h1>Recent prints</h1>
  <ul id="gallery" class="gallery">
    <li class="card">
      <img class="card-img" width="480" height="320" alt="Ochre study, a three-colour screen print" src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='480' height='320'%3E%3Crect width='480' height='320' fill='%23e8dcc8'/%3E%3C/svg%3E">
      <h2>Ochre study</h2>
      <p>Three-colour screen print, 2026.</p>
    </li>
    <li class="card">
      <img class="card-img" width="480" height="320" alt="Blue harbour, a two-colour lithograph" src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='480' height='320'%3E%3Crect width='480' height='320' fill='%23cfd9e8'/%3E%3C/svg%3E">
      <h2>Blue harbour</h2>
      <p>Two-colour lithograph, 2025.</p>
    </li>
    <li class="card">
      <img class="card-img" width="480" height="320" alt="Field margin, a linocut in green" src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='480' height='320'%3E%3Crect width='480' height='320' fill='%23d9e8d2'/%3E%3C/svg%3E">
      <h2>Field margin</h2>
      <p>Linocut, 2025.</p>
    </li>
    <li class="card">
      <img class="card-img" width="480" height="320" alt="Rose window, a risograph in pink" src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='480' height='320'%3E%3Crect width='480' height='320' fill='%23e8d2d9'/%3E%3C/svg%3E">
      <h2>Rose window</h2>
      <p>Risograph, 2024.</p>
    </li>
    <li class="card">
      <img class="card-img" width="480" height="320" alt="Violet dusk, an etching in purple" src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='480' height='320'%3E%3Crect width='480' height='320' fill='%23dcd2e8'/%3E%3C/svg%3E">
      <h2>Violet dusk</h2>
      <p>Etching, 2024.</p>
    </li>
    <li class="card">
      <img class="card-img" width="480" height="320" alt="Chalk path, a monotype in pale grey" src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='480' height='320'%3E%3Crect width='480' height='320' fill='%23e0e0d6'/%3E%3C/svg%3E">
      <h2>Chalk path</h2>
      <p>Monotype, 2023.</p>
    </li>
  </ul>
</main>

</body>
</html>
'''},
                    {"name": "style.css", "content": r'''
/* The markup in index.html is fixed. Everything below is yours. */

body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: #1b1f27;
  background: #fbfbfd;
  line-height: 1.5;
}

/* 1. --layout on :root, re-declared inside the breakpoint
   2. .site-nav  — flex row, space-between
   3. .nav-list  — flex row, no bullets, a gap
   4. #gallery   — three-column grid with a gap, no bullets
   5. .card-img  — block, max-width 100%, height auto
   6. @media (max-width: 640px) — stack the nav, collapse to one column */
'''},
                ],
                "main": "index.html",
                "solution": [
                    {"name": "style.css", "content": r'''
:root {
  --layout: wide;
  --gap: 1.25rem;
  --ink: #1b1f27;
  --muted: #5a6270;
  --rule: #d7dce4;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: var(--ink);
  background: #fbfbfd;
  line-height: 1.5;
}

.site-header {
  border-bottom: 1px solid var(--rule);
  padding: 0.85rem 1.25rem;
  background: #fff;
}

.site-nav {
  display: flex;
  justify-content: space-between;
  gap: var(--gap);
  max-width: 64rem;
  margin: 0 auto;
}

.brand {
  font-weight: 700;
  text-decoration: none;
  color: inherit;
}

.nav-list {
  display: flex;
  flex-direction: row;
  gap: var(--gap);
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-list a { color: var(--muted); text-decoration: none; }

main {
  max-width: 64rem;
  margin: 0 auto;
  padding: 1.5rem 1.25rem 3rem;
}

h1 { font-size: 1.4rem; margin: 0 0 1.25rem; }

.gallery {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--gap);
  list-style: none;
  margin: 0;
  padding: 0;
}

.card {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--rule);
  border-radius: 10px;
  overflow: hidden;
  background: #fff;
}

.card-img {
  display: block;
  width: 100%;
  max-width: 100%;
  height: auto;
}

.card h2 { font-size: 1rem; margin: 0.75rem 0.9rem 0.2rem; }

.card p { margin: 0 0.9rem 0.9rem; color: var(--muted); font-size: 0.9rem; }

@media (max-width: 640px) {
  :root { --layout: narrow; }

  .site-nav { flex-direction: column; }

  .nav-list { flex-direction: column; }

  .gallery { grid-template-columns: 1fr; }
}
'''},
                ],
                "hints": [
                    "Start with the token: `:root { --layout: wide; }` and a `@media (max-width: 640px) { :root { --layout: narrow; } }` block. Everything else hangs off that same media query.",
                    "`display: flex` on `.site-nav` plus `justify-content: space-between` is the whole navbar — the brand and the list are its only two children.",
                    "`grid-template-columns: repeat(3, 1fr)` gives three equal tracks; inside the media query override it with `grid-template-columns: 1fr`.",
                    "The images are 480px wide intrinsically. `max-width: 100%; height: auto;` is what stops them widening their track and pushing the page sideways.",
                ],
                "tests": [
                    {"name": "The breakpoint token agrees with the media query", "code": r'''
var _layout = getComputedStyle(document.documentElement).getPropertyValue('--layout').trim();
assert(_layout === 'wide' || _layout === 'narrow', 'Declare --layout on :root as wide, and narrow inside the breakpoint. Read back: "' + _layout + '"');
var _narrow = window.matchMedia('(max-width: 640px)').matches;
assertEqual(_layout, _narrow ? 'narrow' : 'wide', 'At this width matchMedia says narrow=' + _narrow + ', but --layout reads "' + _layout + '"');
'''},
                    {"name": "The navbar is a flex row that spreads its ends", "code": r'''
var _nav = document.querySelector('.site-nav');
assert(_nav !== null, 'No .site-nav element — do not edit index.html');
var _ns = getComputedStyle(_nav);
assertEqual(_ns.display, 'flex', '.site-nav should be a flex container, got display: ' + _ns.display);
assertEqual(_ns.justifyContent, 'space-between', 'Push the brand and the links apart with justify-content: space-between, got ' + _ns.justifyContent);
'''},
                    {"name": "The nav list is a flex list without bullets", "code": r'''
var _ls = getComputedStyle(document.querySelector('.nav-list'));
assertEqual(_ls.display, 'flex', '.nav-list should be flex, got display: ' + _ls.display);
assertEqual(_ls.listStyleType, 'none', 'Remove the bullets from .nav-list, got list-style-type: ' + _ls.listStyleType);
assert(parseFloat(_ls.columnGap) > 0, 'Give .nav-list a gap so the links are not glued together, got column-gap: ' + _ls.columnGap);
var _narrow2 = window.matchMedia('(max-width: 640px)').matches;
assertEqual(_ls.flexDirection, _narrow2 ? 'column' : 'row', 'At this width the nav list should run ' + (_narrow2 ? 'column' : 'row') + ', got ' + _ls.flexDirection);
'''},
                    {"name": "The gallery is a grid with the right track count", "code": r'''
var _g = document.getElementById('gallery');
var _gs = getComputedStyle(_g);
assertEqual(_gs.display, 'grid', '#gallery should use display: grid, got ' + _gs.display);
assert(_gs.gridTemplateColumns !== 'none', 'No grid-template-columns set on #gallery');
assertEqual(_gs.listStyleType, 'none', 'The gallery is a <ul> — drop its bullets, got list-style-type: ' + _gs.listStyleType);
var _tracks = _gs.gridTemplateColumns.trim().split(/\s+/).length;
var _narrow3 = window.matchMedia('(max-width: 640px)').matches;
var _want = _narrow3 ? 1 : 3;
assertEqual(_tracks, _want, 'Expected ' + _want + ' column(s) at this width, found ' + _tracks + ' (' + _gs.gridTemplateColumns + ')');
assert(parseFloat(_gs.rowGap) > 0, 'The gallery needs a gap between cards, got row-gap: ' + _gs.rowGap);
'''},
                    {"name": "Images shrink with their column", "code": r'''
var _img = document.querySelector('.card-img');
var _is = getComputedStyle(_img);
assertEqual(_is.maxWidth, '100%', 'Card images need max-width: 100%, got ' + _is.maxWidth);
assertEqual(_is.display, 'block', 'Make card images display: block to remove the inline baseline gap, got ' + _is.display);
var _cardWidth = _img.closest('.card').getBoundingClientRect().width;
var _imgWidth = _img.getBoundingClientRect().width;
assert(_imgWidth <= _cardWidth + 1, 'The image renders ' + _imgWidth.toFixed(1) + 'px wide inside a ' + _cardWidth.toFixed(1) + 'px card');
'''},
                    {"name": "Grid tracks are equal", "code": r'''
var _cards = document.querySelectorAll('.card');
assertEqual(_cards.length, 6, 'Expected the six cards from index.html, found ' + _cards.length);
var _w0 = _cards[0].getBoundingClientRect().width;
var _w1 = _cards[1].getBoundingClientRect().width;
assert(Math.abs(_w0 - _w1) < 1.5, 'Equal tracks should give equal cards, got ' + _w0.toFixed(1) + 'px and ' + _w1.toFixed(1) + 'px');
assert(_w0 > 0, 'The cards have collapsed to zero width');
'''},
                    {"name": "Nothing scrolls sideways", "code": r'''
var _doc = document.documentElement;
if (_doc.clientWidth > 0) {
  assert(_doc.scrollWidth <= _doc.clientWidth + 1, 'The page scrolls sideways: scrollWidth ' + _doc.scrollWidth + 'px vs clientWidth ' + _doc.clientWidth + 'px — something is wider than its container');
}
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "State, rendering and delegation",
            "summary": "One array of truth, one render function, one listener per container.",
            "concepts": [
                "A single state object is the source of truth; the DOM is a projection of it",
                "Re-render from state instead of patching nodes by hand — patches drift, renders cannot",
                "Event delegation: listen on a stable ancestor and read `event.target.closest(...)`",
                "`data-*` attributes carry the identity a handler needs back into JavaScript",
                "Derived views (`visibleItems()`) belong in functions, not in duplicated filters",
                "`textContent` over `innerHTML`: the difference is whether user input can execute",
                "`localStorage` holds strings only, can be unavailable, and can contain junk",
            ],
            "lab": {
                "title": "A filterable reading list",
                "runtime": "web",
                "minutes": 55,
                "brief": r'''
`index.html` and `style.css` are read-only. All of your work goes in `app.js`.

The state object is already declared:

```js
var state = { items: [], filter: 'all', nextId: 1 };
```

An item is `{ id, title, tag, done }` where `tag` is `js`, `css` or `a11y`.

Implement these, all of them top-level so the checks can call them:

- `saveState()` — write `state` to `localStorage` under `STORAGE_KEY`
- `loadState()` — replace `state` from storage. Missing **or unreadable** data
  must give a fresh `{ items: [], filter: 'all', nextId: 1 }` rather than throw
- `addItem(title, tag)` — trim the title; return `null` and change nothing when
  it is blank. Otherwise append `{ id: state.nextId, title, tag, done: false }`,
  advance `nextId`, save, re-render, and return the new item
- `removeItem(id)` / `toggleDone(id)` — mutate, save, re-render
- `setFilter(tag)` — store it, set `aria-pressed` to `"true"` on the matching
  `.filter` button and `"false"` on the others, save, re-render
- `visibleItems()` — every item when the filter is `all`, otherwise the matching
  ones
- `render()` — rebuild `#list` from `visibleItems()`, and set `#empty.hidden`

Each row must be:

```text
<li class="item" data-id="3">
  <span class="item-title">…</span>
  <span class="item-tag">…</span>
  <button type="button" class="js-done">Done</button>
  <button type="button" class="js-remove">Remove</button>
</li>
```

with the extra class `done` on the `<li>` when the item is done.

Wire up exactly three listeners: one delegated `click` on `#list`, one delegated
`click` on `#filters`, and a `submit` on `#add-form` that calls
`event.preventDefault()`. Because `render()` throws the old rows away, handlers
bound to individual buttons would die on the next render — delegate.
''',
                "files": [
                    {"name": "index.html", "ro": True, "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Reading list</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<main>
  <h1>Reading list</h1>

  <form id="add-form">
    <label for="title-input">Title</label>
    <input id="title-input" name="title" type="text" autocomplete="off">
    <label for="tag-input">Tag</label>
    <select id="tag-input" name="tag">
      <option value="js">js</option>
      <option value="css">css</option>
      <option value="a11y">a11y</option>
    </select>
    <button type="submit">Add</button>
  </form>

  <div id="filters" role="group" aria-label="Filter by tag">
    <button type="button" class="filter" data-tag="all" aria-pressed="true">All</button>
    <button type="button" class="filter" data-tag="js" aria-pressed="false">js</button>
    <button type="button" class="filter" data-tag="css" aria-pressed="false">css</button>
    <button type="button" class="filter" data-tag="a11y" aria-pressed="false">a11y</button>
  </div>

  <ul id="list" class="list"></ul>
  <p id="empty" class="empty" hidden>Nothing to show for this filter.</p>
</main>

<script src="app.js"></script>
</body>
</html>
'''},
                    {"name": "style.css", "ro": True, "content": r'''
* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: #1b1f27;
  background: #fbfbfd;
  line-height: 1.5;
}

main { max-width: 40rem; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }

h1 { font-size: 1.35rem; margin: 0 0 1rem; }

#add-form { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin-bottom: 1rem; }

#add-form input, #add-form select { font: inherit; padding: 0.4rem 0.5rem; border: 1px solid #d7dce4; border-radius: 6px; }

button { font: inherit; padding: 0.35rem 0.75rem; border: 1px solid #d7dce4; border-radius: 6px; background: #fff; cursor: pointer; }

#filters { display: flex; gap: 0.4rem; margin-bottom: 1rem; }

.filter[aria-pressed="true"] { background: #1b1f27; color: #fff; border-color: #1b1f27; }

.list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.4rem; }

.item { display: flex; gap: 0.6rem; align-items: center; padding: 0.5rem 0.7rem; border: 1px solid #d7dce4; border-radius: 8px; background: #fff; }

.item-title { flex: 1; }

.item-tag { color: #5a6270; font-size: 0.85rem; }

.item.done .item-title { text-decoration: line-through; color: #8b93a1; }

.empty { color: #5a6270; }
'''},
                    {"name": "app.js", "content": r'''
var STORAGE_KEY = 'reading-list-v1';

var state = { items: [], filter: 'all', nextId: 1 };

var listEl = document.getElementById('list');
var emptyEl = document.getElementById('empty');
var filtersEl = document.getElementById('filters');
var formEl = document.getElementById('add-form');
var titleEl = document.getElementById('title-input');
var tagEl = document.getElementById('tag-input');

function saveState() {
  // TODO: JSON.stringify(state) into localStorage under STORAGE_KEY
}

function loadState() {
  // TODO: read it back. Missing or unreadable data -> a fresh empty state, never a throw.
}

function addItem(title, tag) {
  // TODO: reject a blank title with null; otherwise append, save, render, return the item
}

function removeItem(id) {
  // TODO
}

function toggleDone(id) {
  // TODO
}

function setFilter(tag) {
  // TODO: store the filter, update aria-pressed on every .filter button, save, render
}

function visibleItems() {
  // TODO: all items when state.filter is 'all', otherwise the matching tags
  return [];
}

function render() {
  // TODO: rebuild #list from visibleItems(), toggle emptyEl.hidden
}

// TODO: one delegated click listener on listEl
// TODO: one delegated click listener on filtersEl
// TODO: a submit listener on formEl that prevents the default and adds the item

loadState();
render();
'''},
                ],
                "main": "index.html",
                "solution": [
                    {"name": "app.js", "content": r'''
var STORAGE_KEY = 'reading-list-v1';

var state = { items: [], filter: 'all', nextId: 1 };

var listEl = document.getElementById('list');
var emptyEl = document.getElementById('empty');
var filtersEl = document.getElementById('filters');
var formEl = document.getElementById('add-form');
var titleEl = document.getElementById('title-input');
var tagEl = document.getElementById('tag-input');

function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    return true;
  } catch (err) {
    return false;
  }
}

function loadState() {
  var fresh = { items: [], filter: 'all', nextId: 1 };
  var raw = null;
  try {
    raw = localStorage.getItem(STORAGE_KEY);
  } catch (err) {
    raw = null;
  }
  if (!raw) {
    state = fresh;
    return state;
  }
  try {
    var parsed = JSON.parse(raw);
    if (!parsed || !Array.isArray(parsed.items)) {
      state = fresh;
      return state;
    }
    state = {
      items: parsed.items,
      filter: typeof parsed.filter === 'string' ? parsed.filter : 'all',
      nextId: typeof parsed.nextId === 'number' ? parsed.nextId : parsed.items.length + 1
    };
  } catch (err) {
    state = fresh;
  }
  return state;
}

function addItem(title, tag) {
  var clean = String(title == null ? '' : title).trim();
  if (clean === '') {
    return null;
  }
  var item = { id: state.nextId, title: clean, tag: tag || 'js', done: false };
  state.nextId += 1;
  state.items.push(item);
  saveState();
  render();
  return item;
}

function removeItem(id) {
  var before = state.items.length;
  state.items = state.items.filter(function (item) { return item.id !== id; });
  if (state.items.length === before) {
    return false;
  }
  saveState();
  render();
  return true;
}

function toggleDone(id) {
  var hit = null;
  state.items.forEach(function (item) {
    if (item.id === id) {
      item.done = !item.done;
      hit = item;
    }
  });
  if (hit === null) {
    return null;
  }
  saveState();
  render();
  return hit;
}

function setFilter(tag) {
  state.filter = tag;
  var buttons = filtersEl.querySelectorAll('.filter');
  for (var i = 0; i < buttons.length; i++) {
    buttons[i].setAttribute('aria-pressed', buttons[i].dataset.tag === tag ? 'true' : 'false');
  }
  saveState();
  render();
}

function visibleItems() {
  if (state.filter === 'all') {
    return state.items.slice();
  }
  return state.items.filter(function (item) { return item.tag === state.filter; });
}

function render() {
  var items = visibleItems();
  listEl.textContent = '';
  items.forEach(function (item) {
    var li = document.createElement('li');
    li.className = item.done ? 'item done' : 'item';
    li.dataset.id = String(item.id);

    var title = document.createElement('span');
    title.className = 'item-title';
    title.textContent = item.title;

    var tag = document.createElement('span');
    tag.className = 'item-tag';
    tag.textContent = item.tag;

    var doneButton = document.createElement('button');
    doneButton.type = 'button';
    doneButton.className = 'js-done';
    doneButton.textContent = item.done ? 'Undo' : 'Done';

    var removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'js-remove';
    removeButton.textContent = 'Remove';

    li.appendChild(title);
    li.appendChild(tag);
    li.appendChild(doneButton);
    li.appendChild(removeButton);
    listEl.appendChild(li);
  });
  emptyEl.hidden = items.length > 0;
}

listEl.addEventListener('click', function (event) {
  var button = event.target.closest('button');
  if (!button) {
    return;
  }
  var row = button.closest('li[data-id]');
  if (!row) {
    return;
  }
  var id = Number(row.dataset.id);
  if (button.classList.contains('js-done')) {
    toggleDone(id);
  } else if (button.classList.contains('js-remove')) {
    removeItem(id);
  }
});

filtersEl.addEventListener('click', function (event) {
  var button = event.target.closest('.filter');
  if (!button) {
    return;
  }
  setFilter(button.dataset.tag);
});

formEl.addEventListener('submit', function (event) {
  event.preventDefault();
  if (addItem(titleEl.value, tagEl.value)) {
    titleEl.value = '';
  }
});

loadState();
setFilter(state.filter);
'''},
                ],
                "hints": [
                    "Build `loadState()` defensively: read the string, and wrap `JSON.parse` in `try` / `catch`. Anything that is not an object with an `items` array is junk — fall back to the fresh state.",
                    "`render()` should start with `listEl.textContent = '';` and then append one `<li>` per visible item. Set `li.dataset.id` — that is the only link back to state.",
                    "In the delegated handler, `event.target.closest('button')` finds the button that was hit, and `button.closest('li[data-id]')` finds the row it belongs to.",
                    "`setFilter` is the one place that touches `aria-pressed`: loop over `filtersEl.querySelectorAll('.filter')` and set it to `'true'` or `'false'` for each one.",
                ],
                "tests": [
                    {"name": "addItem appends and renders one row", "code": r'''
localStorage.removeItem('reading-list-v1');
loadState();
setFilter('all');
var _it = addItem('Eloquent JavaScript', 'js');
assert(_it && _it.title === 'Eloquent JavaScript', 'addItem should return the item it created, got ' + JSON.stringify(_it));
assertEqual(state.items.length, 1, 'state.items should hold one item, got ' + state.items.length);
assertEqual(_it.done, false, 'A new item starts not done, got ' + _it.done);
var _rows = document.querySelectorAll('#list li');
assertEqual(_rows.length, 1, 'render() should put one <li> in #list, found ' + _rows.length);
assert(_rows[0].textContent.indexOf('Eloquent JavaScript') !== -1, 'The row should show the title, got: ' + _rows[0].textContent);
assertEqual(_rows[0].dataset.id, String(_it.id), 'Each row needs data-id so a delegated handler can find it');
assert(_rows[0].querySelector('.js-done') !== null, 'Each row needs a button.js-done');
assert(_rows[0].querySelector('.js-remove') !== null, 'Each row needs a button.js-remove');
'''},
                    {"name": "A blank title is refused", "code": r'''
localStorage.removeItem('reading-list-v1');
loadState();
setFilter('all');
assertEqual(addItem('   ', 'js'), null, 'A whitespace-only title should be rejected with null');
assertEqual(state.items.length, 0, 'A rejected add must not touch state.items, got ' + state.items.length);
assertEqual(document.querySelectorAll('#list li').length, 0, 'A rejected add must not render a row');
var _good = addItem('  CSS Secrets  ', 'css');
assertEqual(_good.title, 'CSS Secrets', 'The stored title should be trimmed, got ' + JSON.stringify(_good.title));
'''},
                    {"name": "Filter buttons are delegated and marked", "code": r'''
localStorage.removeItem('reading-list-v1');
loadState();
setFilter('all');
addItem('Eloquent JavaScript', 'js');
addItem('CSS Secrets', 'css');
addItem('Inclusive Components', 'a11y');
assertEqual(visibleItems().length, 3, 'The "all" filter shows everything, got ' + visibleItems().length);
document.querySelector('.filter[data-tag="css"]').click();
assertEqual(state.filter, 'css', 'Clicking a filter button should set state.filter, got ' + state.filter);
assertEqual(visibleItems().length, 1, 'Only the css item matches, got ' + visibleItems().length);
assertEqual(document.querySelectorAll('#list li').length, 1, 'The list should re-render to one row, found ' + document.querySelectorAll('#list li').length);
assertEqual(document.querySelector('.filter[data-tag="css"]').getAttribute('aria-pressed'), 'true', 'The active filter needs aria-pressed="true"');
assertEqual(document.querySelector('.filter[data-tag="all"]').getAttribute('aria-pressed'), 'false', 'Inactive filters need aria-pressed="false"');
document.querySelector('.filter[data-tag="all"]').click();
assertEqual(document.querySelectorAll('#list li').length, 3, 'Back to "all" should show three rows');
'''},
                    {"name": "Row buttons keep working after a re-render", "code": r'''
localStorage.removeItem('reading-list-v1');
loadState();
setFilter('all');
var _a = addItem('Refactoring UI', 'css');
var _b = addItem('Inclusive Components', 'a11y');
document.querySelector('#list li[data-id="' + _a.id + '"] .js-done').click();
assertEqual(state.items[0].done, true, 'Clicking Done should toggle the item, got done=' + state.items[0].done);
assert(document.querySelector('#list li[data-id="' + _a.id + '"]').classList.contains('done'), 'A finished row should carry the class "done"');
document.querySelector('#list li[data-id="' + _b.id + '"] .js-remove').click();
assertEqual(state.items.length, 1, 'Remove should drop it from state, got ' + state.items.length);
assertEqual(document.querySelectorAll('#list li').length, 1, 'and from the DOM, found ' + document.querySelectorAll('#list li').length);
document.querySelector('#list li[data-id="' + _a.id + '"] .js-done').click();
assertEqual(state.items[0].done, false, 'The handler must still fire on rows built by a later render — delegate from #list');
'''},
                    {"name": "The empty state appears and disappears", "code": r'''
localStorage.removeItem('reading-list-v1');
loadState();
setFilter('all');
render();
assertEqual(document.getElementById('empty').hidden, false, 'With nothing to show, #empty must be visible');
addItem('Eloquent JavaScript', 'js');
assertEqual(document.getElementById('empty').hidden, true, 'With a row on screen, #empty must be hidden');
setFilter('css');
assertEqual(document.querySelectorAll('#list li').length, 0, 'No css items yet, found ' + document.querySelectorAll('#list li').length);
assertEqual(document.getElementById('empty').hidden, false, 'A filter that matches nothing shows the empty state too');
'''},
                    {"name": "State survives a reload", "code": r'''
localStorage.removeItem('reading-list-v1');
loadState();
setFilter('all');
addItem('Eloquent JavaScript', 'js');
addItem('CSS Secrets', 'css');
var _raw = localStorage.getItem('reading-list-v1');
assert(_raw !== null, 'saveState() should write to localStorage under "reading-list-v1"');
var _saved = JSON.parse(_raw);
assert(Array.isArray(_saved.items), 'The stored payload should carry an items array, got ' + _raw);
assertEqual(_saved.items.length, 2, 'Both items should be in storage, got ' + _saved.items.length);
state.items = [];
render();
loadState();
render();
assertEqual(state.items.length, 2, 'loadState() should bring the items back, got ' + state.items.length);
assertEqual(state.items[1].title, 'CSS Secrets', 'and in order, got ' + state.items[1].title);
assertEqual(document.querySelectorAll('#list li').length, 2, 'and the list should render both, found ' + document.querySelectorAll('#list li').length);
'''},
                    {"name": "Unreadable storage does not crash the app", "code": r'''
localStorage.setItem('reading-list-v1', 'not json at all {{{');
var _threw = null;
try {
  loadState();
} catch (err) {
  _threw = err;
}
assert(_threw === null, 'loadState() must survive junk in storage, but it threw: ' + _threw);
assertEqual(state.items.length, 0, 'Unreadable storage should fall back to an empty list, got ' + state.items.length);
assertEqual(state.filter, 'all', 'and to the default filter, got ' + state.filter);
localStorage.removeItem('reading-list-v1');
loadState();
setFilter('all');
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Asynchronous data and the four states",
            "summary": "Promises, async/await, and telling the truth about loading, empty, error and success.",
            "concepts": [
                "The event loop: synchronous code first, then microtasks, then timers",
                "A Promise settles once; `await` unwraps it and rethrows a rejection",
                "`fetch` rejects only on network failure — a 500 still resolves, with `ok === false`",
                "Every request has four outcomes: loading, empty, error, success. All four need UI",
                "`try` / `catch` around the await is where a network failure becomes a message",
                "`role=\"alert\"` makes an error region announce itself when it gains content",
                "Never leave a spinner running: hide it on every exit path, including the failures",
            ],
            "lab": {
                "title": "Book search against a flaky API",
                "runtime": "web",
                "minutes": 55,
                "brief": r'''
`index.html` is read-only. It defines `window.fakeFetch(url)`, a stand-in for
`fetch` with a 30ms delay, backed by a five-book catalogue:

| id | title | author | tag |
|----|-------|--------|-----|
| 1 | Eloquent JavaScript | Marijn Haverbeke | js |
| 2 | JavaScript: The Good Parts | Douglas Crockford | js |
| 3 | CSS: The Definitive Guide | Eric A. Meyer | css |
| 4 | Refactoring UI | Adam Wathan | css |
| 5 | Inclusive Components | Heydon Pickering | a11y |

`GET /api/books?q=…` matches the query as a case-insensitive substring of
`title + author + tag`, and resolves to a response object with `ok`, `status`
and `json()`, whose body is `{ books: [...] }`. Two queries misbehave on
purpose: `q=fail` resolves with **status 500**, and `q=boom` **rejects** with a
`TypeError`, exactly as a dropped connection does.

In `app.js` implement:

- `showState(name, message)` — `name` is one of `loading`, `empty`, `error`,
  `success`. Exactly the matching element out of `#loading`, `#empty`, `#error`
  is visible; on `success` none of the three is. Set `uiState = name`. Put
  `message` into `#error` when erroring and clear it otherwise, and clear
  `#results` for every state except `success`.
- `renderBooks(books)` — rebuild `#results` as
  `<li class="result" data-id="…">` holding a `.result-title` and a
  `.result-author`.
- `async function searchBooks(query)` — show `loading` **before** awaiting, then
  call `window.fakeFetch('/api/books?q=' + encodeURIComponent(query))` and cover
  all four outcomes. It must never let an exception escape: catch the rejection
  and show the error state. On a non-`ok` response the message must mention the
  status number. Return the array of books it rendered (`[]` on the other paths).
- a `submit` handler on `#search-form` that calls `preventDefault()` and
  searches for the current value of `#q`.

An empty query matches everything, which is the whole catalogue.
''',
                "files": [
                    {"name": "index.html", "ro": True, "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Book search</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<main>
  <h1>Book search</h1>

  <form id="search-form">
    <label for="q">Search the catalogue</label>
    <input id="q" name="q" type="search" autocomplete="off">
    <button type="submit">Search</button>
  </form>

  <p id="loading" hidden>Searching...</p>
  <p id="error" role="alert" hidden></p>
  <p id="empty" hidden>No books matched that search.</p>
  <ul id="results"></ul>
</main>

<script>
/* A stand-in for a real HTTP API. This file is read-only. */
(function () {
  var BOOKS = [
    { id: 1, title: 'Eloquent JavaScript', author: 'Marijn Haverbeke', tag: 'js' },
    { id: 2, title: 'JavaScript: The Good Parts', author: 'Douglas Crockford', tag: 'js' },
    { id: 3, title: 'CSS: The Definitive Guide', author: 'Eric A. Meyer', tag: 'css' },
    { id: 4, title: 'Refactoring UI', author: 'Adam Wathan', tag: 'css' },
    { id: 5, title: 'Inclusive Components', author: 'Heydon Pickering', tag: 'a11y' }
  ];

  function respond(status, body) {
    return {
      ok: status >= 200 && status < 300,
      status: status,
      json: function () { return Promise.resolve(body); }
    };
  }

  window.fakeFetch = function (url) {
    return new Promise(function (resolve, reject) {
      setTimeout(function () {
        var text = String(url);
        var mark = text.indexOf('?');
        var path = mark === -1 ? text : text.slice(0, mark);
        var query = mark === -1 ? '' : text.slice(mark + 1);
        var q = '';
        query.split('&').forEach(function (pair) {
          var bits = pair.split('=');
          if (bits[0] === 'q') { q = decodeURIComponent(bits[1] || ''); }
        });
        if (path !== '/api/books') {
          resolve(respond(404, { error: 'no such endpoint' }));
          return;
        }
        if (q === 'boom') {
          reject(new TypeError('Failed to fetch'));
          return;
        }
        if (q === 'fail') {
          resolve(respond(500, { error: 'the catalogue is having a bad day' }));
          return;
        }
        var needle = q.toLowerCase();
        var books = BOOKS.filter(function (b) {
          return (b.title + ' ' + b.author + ' ' + b.tag).toLowerCase().indexOf(needle) !== -1;
        });
        resolve(respond(200, { books: books }));
      }, 30);
    });
  };
})();
</script>
<script src="app.js"></script>
</body>
</html>
'''},
                    {"name": "style.css", "ro": True, "content": r'''
* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: #1b1f27;
  background: #fbfbfd;
  line-height: 1.5;
}

main { max-width: 40rem; margin: 0 auto; padding: 1.5rem 1.25rem 3rem; }

h1 { font-size: 1.35rem; margin: 0 0 1rem; }

#search-form { display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: center; margin-bottom: 1rem; }

#search-form input { font: inherit; padding: 0.4rem 0.5rem; border: 1px solid #d7dce4; border-radius: 6px; }

button { font: inherit; padding: 0.35rem 0.75rem; border: 1px solid #d7dce4; border-radius: 6px; background: #fff; cursor: pointer; }

#loading, #empty { color: #5a6270; }

#error { color: #a11f1a; background: #fbe4e2; border-radius: 6px; padding: 0.5rem 0.7rem; }

#results { list-style: none; margin: 1rem 0 0; padding: 0; display: flex; flex-direction: column; gap: 0.4rem; }

.result { display: flex; justify-content: space-between; gap: 0.6rem; padding: 0.5rem 0.7rem; border: 1px solid #d7dce4; border-radius: 8px; background: #fff; }

.result-author { color: #5a6270; font-size: 0.9rem; }
'''},
                    {"name": "app.js", "content": r'''
var formEl = document.getElementById('search-form');
var queryEl = document.getElementById('q');
var loadingEl = document.getElementById('loading');
var errorEl = document.getElementById('error');
var emptyEl = document.getElementById('empty');
var resultsEl = document.getElementById('results');

var uiState = 'idle';

function showState(name, message) {
  // TODO: set uiState, show exactly the matching element out of
  //       #loading / #empty / #error (none of them on success),
  //       put message into #error when erroring, and clear #results
  //       for every state except success.
}

function renderBooks(books) {
  // TODO: rebuild #results with one <li class="result" data-id="..."> per book,
  //       holding a .result-title and a .result-author
}

async function searchBooks(query) {
  // TODO: showState('loading') first, then
  //       await window.fakeFetch('/api/books?q=' + encodeURIComponent(query))
  //       inside a try/catch. Cover: rejection, !response.ok, zero books, success.
  //       Return the array of books rendered, or [] on the other paths.
  return [];
}

// TODO: submit handler on formEl — preventDefault(), then searchBooks(queryEl.value)
'''},
                ],
                "main": "index.html",
                "solution": [
                    {"name": "app.js", "content": r'''
var formEl = document.getElementById('search-form');
var queryEl = document.getElementById('q');
var loadingEl = document.getElementById('loading');
var errorEl = document.getElementById('error');
var emptyEl = document.getElementById('empty');
var resultsEl = document.getElementById('results');

var uiState = 'idle';

function showState(name, message) {
  uiState = name;
  loadingEl.hidden = name !== 'loading';
  emptyEl.hidden = name !== 'empty';
  errorEl.hidden = name !== 'error';
  errorEl.textContent = name === 'error' ? String(message || 'Something went wrong.') : '';
  if (name !== 'success') {
    resultsEl.textContent = '';
  }
}

function renderBooks(books) {
  resultsEl.textContent = '';
  books.forEach(function (book) {
    var row = document.createElement('li');
    row.className = 'result';
    row.dataset.id = String(book.id);

    var title = document.createElement('span');
    title.className = 'result-title';
    title.textContent = book.title;

    var author = document.createElement('span');
    author.className = 'result-author';
    author.textContent = book.author;

    row.appendChild(title);
    row.appendChild(author);
    resultsEl.appendChild(row);
  });
}

async function searchBooks(query) {
  showState('loading');
  var response;
  try {
    response = await window.fakeFetch('/api/books?q=' + encodeURIComponent(query));
  } catch (err) {
    showState('error', 'Could not reach the catalogue. Check the connection and try again.');
    return [];
  }
  if (!response.ok) {
    showState('error', 'The catalogue answered with status ' + response.status + '. Try again shortly.');
    return [];
  }
  var payload = await response.json();
  var books = (payload && payload.books) || [];
  if (books.length === 0) {
    showState('empty');
    return [];
  }
  showState('success');
  renderBooks(books);
  return books;
}

formEl.addEventListener('submit', function (event) {
  event.preventDefault();
  searchBooks(queryEl.value);
});
'''},
                ],
                "hints": [
                    "`showState` is the only function allowed to touch `hidden`. Write it as four assignments comparing `name` — that way the four states cannot drift out of sync.",
                    "Call `showState('loading')` before the `await`, not after: the synchronous part of an async function runs immediately, which is exactly what makes the spinner appear.",
                    "A 500 is a *successful* HTTP round trip, so `await` resolves. Check `response.ok` yourself, and keep the network failure in a `try` / `catch` around the await.",
                    "Zero results is not an error and not a success — it is its own state. Test `books.length === 0` before rendering anything.",
                ],
                "tests": [
                    {"name": "The happy path renders rows", "code": r'''
var _books = await searchBooks('js');
assert(Array.isArray(_books), 'searchBooks should resolve to an array of books, got ' + JSON.stringify(_books));
assertEqual(_books.length, 2, 'A search for "js" finds the two JavaScript books, got ' + _books.length);
assertEqual(uiState, 'success', 'uiState should be "success" after a hit, got ' + uiState);
var _rows = document.querySelectorAll('#results li');
assertEqual(_rows.length, 2, '#results should hold two rows, found ' + _rows.length);
assert(_rows[0].textContent.indexOf('Eloquent JavaScript') !== -1, 'The first row should name the book, got: ' + _rows[0].textContent);
assert(_rows[0].textContent.indexOf('Marijn Haverbeke') !== -1, 'and its author, got: ' + _rows[0].textContent);
assertEqual(_rows[0].dataset.id, '1', 'Rows should carry the book id in data-id, got ' + _rows[0].dataset.id);
assertEqual(document.getElementById('loading').hidden, true, '#loading must be hidden once the answer arrives');
assertEqual(document.getElementById('error').hidden, true, '#error must stay hidden on the happy path');
assertEqual(document.getElementById('empty').hidden, true, '#empty must stay hidden on the happy path');
'''},
                    {"name": "Loading shows while the request is in flight", "code": r'''
var _pending = searchBooks('css');
assertEqual(document.getElementById('loading').hidden, false, 'Show #loading before the await, not after it');
assertEqual(uiState, 'loading', 'uiState should be "loading" while the request is in flight, got ' + uiState);
assertEqual(document.querySelectorAll('#results li').length, 0, 'Clear the previous results when a new search starts');
await _pending;
assertEqual(document.getElementById('loading').hidden, true, 'Hide #loading once the promise settles');
assertEqual(document.querySelectorAll('#results li').length, 2, 'A search for "css" finds two books, found ' + document.querySelectorAll('#results li').length);
'''},
                    {"name": "No matches is its own state", "code": r'''
var _none = await searchBooks('zzz');
assertEqual(_none.length, 0, 'Nothing matches "zzz", got ' + _none.length);
assertEqual(uiState, 'empty', 'uiState should be "empty" when nothing matched, got ' + uiState);
assertEqual(document.getElementById('empty').hidden, false, '#empty should be visible');
assertEqual(document.querySelectorAll('#results li').length, 0, 'No rows for an empty result, found ' + document.querySelectorAll('#results li').length);
assertEqual(document.getElementById('loading').hidden, true, '#loading should be hidden again');
assertEqual(document.getElementById('error').hidden, true, 'An empty result is not an error');
'''},
                    {"name": "A 500 response becomes a readable error", "code": r'''
await searchBooks('fail');
assertEqual(uiState, 'error', 'A 500 response is the error state, got ' + uiState);
var _err = document.getElementById('error');
assertEqual(_err.hidden, false, '#error should be visible after a 500');
assert(_err.textContent.trim().length > 0, '#error needs a human-readable message, it is empty');
assert(_err.textContent.indexOf('500') !== -1, 'Mention the status the server sent, got: ' + _err.textContent);
assertEqual(document.getElementById('loading').hidden, true, 'Hide #loading on the error path too');
assertEqual(document.querySelectorAll('#results li').length, 0, 'No rows after a failure, found ' + document.querySelectorAll('#results li').length);
'''},
                    {"name": "A rejected request is handled, not thrown", "code": r'''
var _thrown = null;
try {
  await searchBooks('boom');
} catch (err) {
  _thrown = err;
}
assert(_thrown === null, 'searchBooks must catch the rejection itself, but it threw: ' + _thrown);
assertEqual(uiState, 'error', 'A dropped connection is also the error state, got ' + uiState);
assertEqual(document.getElementById('error').hidden, false, '#error should be visible after a network failure');
assert(document.getElementById('error').textContent.trim().length > 0, 'Say something useful in #error');
assertEqual(document.getElementById('loading').hidden, true, 'Hide #loading even when the request fails');
'''},
                    {"name": "Submitting the form searches and clears the error", "code": r'''
document.getElementById('q').value = 'meyer';
var _submit = new Event('submit', { bubbles: true, cancelable: true });
document.getElementById('search-form').dispatchEvent(_submit);
assert(_submit.defaultPrevented, 'Call event.preventDefault() so the form does not navigate away');
for (var _tries = 0; _tries < 60 && uiState !== 'success'; _tries++) {
  await new Promise(function (done) { setTimeout(done, 50); });
}
assertEqual(uiState, 'success', 'Submitting the form should run a search, got uiState ' + uiState);
assertEqual(document.querySelectorAll('#results li').length, 1, 'One book matches "meyer", found ' + document.querySelectorAll('#results li').length);
assertEqual(document.getElementById('error').hidden, true, 'The previous error must clear when the next search succeeds');
'''},
                    {"name": "An empty query lists the whole catalogue", "code": r'''
var _all = await searchBooks('');
assertEqual(uiState, 'success', 'An empty query matches everything, got uiState ' + uiState);
assertEqual(_all.length, 5, 'The catalogue holds five books, got ' + _all.length);
assertEqual(document.querySelectorAll('#results li').length, 5, 'and all five should render, found ' + document.querySelectorAll('#results li').length);
assertEqual(document.getElementById('empty').hidden, true, 'Five results is not the empty state');
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — Field notes, an offline-first CRUD client",
        "runtime": "web",
        "minutes": 300,
        "brief": r'''
A complete single-page client for one resource: list, detail, create, edit,
delete — with hash routing, validation and state that survives a reload. There
is no server: `localStorage` *is* the backing store, which is what makes the app
work offline.

`index.html` and `style.css` are read-only. Everything goes in `app.js`.

## State

```js
var state = { notes: [], nextId: 1, seq: 1, route: { name: 'list', id: null } };
```

A note is `{ id, title, body, tag, seq }`. `nextId` hands out ids; `seq` is a
monotonic counter used for ordering, so the list never depends on the clock.
Persist `notes`, `nextId` and `seq` under `field-notes-v1`.

## Routing

`parseRoute(hash)` maps a location hash onto `{ name, id }`:

```text
''  '#/'  '#/notes'   ->  { name: 'list',   id: null }
'#/notes/new'         ->  { name: 'new',    id: null }
'#/notes/12'          ->  { name: 'detail', id: 12 }
'#/notes/12/edit'     ->  { name: 'edit',   id: 12 }
anything else         ->  { name: 'notfound', id: null }
```

`navigate(hash)` sets `state.route` from `parseRoute`, calls `render()` and
returns the route. Also listen for `hashchange` so the back button works.

## Validation

`validate(draft)` returns an object of field name to message, empty when the
draft is good:

- `title` — required after trimming, and at most 60 characters
- `body` — at least 10 characters after trimming
- `tag` — one of `field`, `lab`, `admin`

## Data functions

`createNote(draft)` and `updateNote(id, draft)` both return `null` and change
nothing when `validate` finds a problem (and `updateNote` also returns `null`
for an unknown id). A successful write stamps the note with the current `seq`
and advances it, so an edited note rises to the top. `deleteNote(id)` returns
`true` or `false`. `getNote(id)` returns the note or `null`. `listNotes()`
returns them newest-touched first.

## Views, all rendered into `#view`

- **list** — `<ul id="note-list">` of `<li class="note-row" data-id="N">`, each
  holding an `<a class="note-link" href="#/notes/N">` titled with the note and a
  `.note-tag`. With no notes at all, render `<p id="no-notes">` instead.
- **detail** — `<article id="note-detail" data-id="N">` with `#detail-title`,
  `#detail-body`, `#detail-tag`, an `<a id="edit-link">` to the edit route and a
  `<button id="delete-btn">`.
- **new / edit** — `<form id="note-form">` with `#f-title`, `#f-body`, `#f-tag`
  (a `<select>` offering the three tags), a `<button id="save-btn">`, and three
  empty message holders `#err-title`, `#err-body`, `#err-tag`. On edit the
  fields start filled from the note.
- **notfound**, and a detail/edit route for an id that is gone — `<p id="not-found">`.

Submitting the form calls `preventDefault()`, validates, and on failure writes
each message into its `#err-…` holder without saving. On success it creates or
updates and then navigates to that note's detail route. The delete button
removes the note and returns to the list.
''',
        "deliverables": [
            "`app.js` — routing, validation, CRUD and rendering, with no `innerHTML` anywhere",
            "A pure `parseRoute(hash)` and a pure `validate(draft)` that the rest of the app is built on",
            "Four rendered views plus a not-found view, all derived from `state` by one `render()`",
            "`localStorage` persistence that round-trips notes, `nextId` and `seq`",
            "Field-level validation messages that appear without the note being written",
            "A delete path that removes the note and routes back to the list",
        ],
        "constraints": [
            "`index.html` and `style.css` are read-only — every selector the checks use is already there",
            "Build DOM with `document.createElement` and `textContent`; `innerHTML` is banned",
            "No `Date.now()` or `Math.random()` in ordering or ids — `seq` and `nextId` are the only sources",
            "Unreadable or missing `localStorage` must degrade to an empty collection, never throw",
            "Exactly one delegated `submit` listener and one delegated `click` listener on `#view`",
        ],
        "rubric": [
            {"criterion": "Correctness of the CRUD and routing model", "weight": 40,
             "evidence": "All automated checks pass, including unknown ids, refused writes and the empty collection."},
            {"criterion": "Validation", "weight": 20,
             "evidence": "validate() is pure and total; invalid submits show per-field messages and write nothing."},
            {"criterion": "Rendering discipline", "weight": 20,
             "evidence": "One render() derives every view from state; no innerHTML, no hand-patched nodes."},
            {"criterion": "Persistence and resilience", "weight": 10,
             "evidence": "State round-trips through localStorage; junk or unavailable storage degrades quietly."},
            {"criterion": "Readability", "weight": 10,
             "evidence": "Small named functions, no duplicated selectors, no dead code or stray console logging."},
        ],
        "hints": [
            "Write `parseRoute` first and test it in isolation — two regular expressions, `^\\/notes\\/(\\d+)$` and `^\\/notes\\/(\\d+)\\/edit$`, cover the parameterised routes once you have stripped the leading `#`.",
            "Keep `validate` pure: it reads a draft and returns messages. `createNote` and `updateNote` should both start with `if (Object.keys(validate(draft)).length > 0) return null;` so there is one definition of valid.",
            "A tiny `el(tag, props, children)` helper removes most of the noise from the four views — handle `text` and `class` specially and pass everything else to `setAttribute`.",
            "`render()` should clear `#view` and switch on `state.route.name`. Because the views are rebuilt every time, both listeners must live on `#view` itself, not on the buttons inside it.",
        ],
        "files": [
            {"name": "index.html", "ro": True, "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Field notes</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<header class="app-bar">
  <h1>Field notes</h1>
  <nav aria-label="Primary">
    <a id="nav-list" href="#/notes">All notes</a>
    <a id="nav-new" href="#/notes/new">New note</a>
  </nav>
</header>

<main>
  <p id="status" role="status"></p>
  <div id="view"></div>
</main>

<script src="app.js"></script>
</body>
</html>
'''},
            {"name": "style.css", "ro": True, "content": r'''
* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: #1b1f27;
  background: #fbfbfd;
  line-height: 1.55;
}

.app-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: baseline;
  justify-content: space-between;
  border-bottom: 1px solid #d7dce4;
  padding: 0.9rem 1.25rem;
  background: #fff;
}

.app-bar h1 { font-size: 1.2rem; margin: 0; }

.app-bar nav { display: flex; gap: 1rem; }

.app-bar a { color: #5a6270; }

main { max-width: 44rem; margin: 0 auto; padding: 1.25rem 1.25rem 3rem; }

#status:empty { display: none; }

#status { color: #5a6270; font-size: 0.9rem; margin: 0 0 0.75rem; }

#note-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.4rem; }

.note-row { display: flex; justify-content: space-between; gap: 0.6rem; padding: 0.55rem 0.75rem; border: 1px solid #d7dce4; border-radius: 8px; background: #fff; }

.note-tag { color: #5a6270; font-size: 0.85rem; }

#note-detail { border: 1px solid #d7dce4; border-radius: 10px; background: #fff; padding: 1rem 1.15rem; }

#note-detail h2 { margin: 0 0 0.5rem; font-size: 1.15rem; }

#note-form { display: flex; flex-direction: column; gap: 0.35rem; max-width: 32rem; }

#note-form label { font-weight: 600; margin-top: 0.5rem; }

#note-form input, #note-form textarea, #note-form select {
  font: inherit;
  padding: 0.45rem 0.6rem;
  border: 1px solid #d7dce4;
  border-radius: 6px;
  background: #fff;
}

.field-error { color: #a11f1a; font-size: 0.85rem; margin: 0; min-height: 1.1em; }

button { font: inherit; padding: 0.4rem 0.9rem; border: 1px solid #d7dce4; border-radius: 6px; background: #fff; cursor: pointer; }

#save-btn { align-self: flex-start; margin-top: 0.75rem; background: #1b1f27; color: #fff; border-color: #1b1f27; }

#delete-btn { margin-left: 0.6rem; color: #a11f1a; }
'''},
            {"name": "app.js", "content": r'''
var STORAGE_KEY = 'field-notes-v1';
var TAGS = ['field', 'lab', 'admin'];

var state = { notes: [], nextId: 1, seq: 1, route: { name: 'list', id: null } };

var viewEl = document.getElementById('view');
var statusEl = document.getElementById('status');

function saveState() {
  // TODO: persist notes, nextId and seq under STORAGE_KEY
}

function loadState() {
  // TODO: restore them. Missing or unreadable storage -> an empty collection, never a throw.
}

function parseRoute(hash) {
  // TODO: '' | '#/' | '#/notes' -> list, '#/notes/new' -> new,
  //       '#/notes/12' -> detail, '#/notes/12/edit' -> edit, anything else -> notfound
  return { name: 'notfound', id: null };
}

function validate(draft) {
  // TODO: return { title?, body?, tag? } messages; an empty object means the draft is good
  return {};
}

function getNote(id) {
  // TODO
  return null;
}

function listNotes() {
  // TODO: newest-touched first, by seq descending
  return [];
}

function createNote(draft) {
  // TODO: refuse an invalid draft with null; otherwise stamp id and seq, save, return the note
  return null;
}

function updateNote(id, draft) {
  // TODO: null for an unknown id or an invalid draft; otherwise write the fields,
  //       restamp seq so the note rises to the top, save, return it
  return null;
}

function deleteNote(id) {
  // TODO: true when something was removed, false otherwise
  return false;
}

function render() {
  // TODO: clear #view, then build the view for state.route.name
}

function navigate(hash) {
  // TODO: set state.route from parseRoute(hash), render, return the route
  return state.route;
}

// TODO: one delegated submit listener on viewEl for #note-form
// TODO: one delegated click listener on viewEl for #delete-btn
// TODO: window hashchange -> navigate(window.location.hash)

loadState();
navigate(window.location.hash);
'''},
        ],
        "main": "index.html",
        "solution": [
            {"name": "app.js", "content": r'''
var STORAGE_KEY = 'field-notes-v1';
var TAGS = ['field', 'lab', 'admin'];

var state = { notes: [], nextId: 1, seq: 1, route: { name: 'list', id: null } };

var viewEl = document.getElementById('view');
var statusEl = document.getElementById('status');

/* ------------------------------------------------------------------ storage */

function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      notes: state.notes,
      nextId: state.nextId,
      seq: state.seq
    }));
    return true;
  } catch (err) {
    return false;
  }
}

function loadState() {
  var data = { notes: [], nextId: 1, seq: 1 };
  var raw = null;
  try {
    raw = localStorage.getItem(STORAGE_KEY);
  } catch (err) {
    raw = null;
  }
  if (raw) {
    try {
      var parsed = JSON.parse(raw);
      if (parsed && Array.isArray(parsed.notes)) {
        data = {
          notes: parsed.notes,
          nextId: typeof parsed.nextId === 'number' ? parsed.nextId : parsed.notes.length + 1,
          seq: typeof parsed.seq === 'number' ? parsed.seq : parsed.notes.length + 1
        };
      }
    } catch (err) {
      data = { notes: [], nextId: 1, seq: 1 };
    }
  }
  state.notes = data.notes;
  state.nextId = data.nextId;
  state.seq = data.seq;
  return state;
}

/* ------------------------------------------------------------------ routing */

function parseRoute(hash) {
  var clean = String(hash == null ? '' : hash).replace(/^#/, '');
  if (clean === '' || clean === '/' || clean === '/notes') {
    return { name: 'list', id: null };
  }
  if (clean === '/notes/new') {
    return { name: 'new', id: null };
  }
  var detail = clean.match(/^\/notes\/(\d+)$/);
  if (detail) {
    return { name: 'detail', id: Number(detail[1]) };
  }
  var edit = clean.match(/^\/notes\/(\d+)\/edit$/);
  if (edit) {
    return { name: 'edit', id: Number(edit[1]) };
  }
  return { name: 'notfound', id: null };
}

/* --------------------------------------------------------------- validation */

function validate(draft) {
  var errors = {};
  var title = String((draft && draft.title) || '').trim();
  var body = String((draft && draft.body) || '').trim();
  var tag = String((draft && draft.tag) || '');
  if (title === '') {
    errors.title = 'A title is required.';
  } else if (title.length > 60) {
    errors.title = 'Keep the title to 60 characters or fewer.';
  }
  if (body.length < 10) {
    errors.body = 'Write at least 10 characters of body text.';
  }
  if (TAGS.indexOf(tag) === -1) {
    errors.tag = 'Choose one of: ' + TAGS.join(', ') + '.';
  }
  return errors;
}

/* --------------------------------------------------------------------- data */

function getNote(id) {
  var wanted = Number(id);
  for (var i = 0; i < state.notes.length; i++) {
    if (state.notes[i].id === wanted) {
      return state.notes[i];
    }
  }
  return null;
}

function listNotes() {
  return state.notes.slice().sort(function (a, b) { return b.seq - a.seq; });
}

function createNote(draft) {
  if (Object.keys(validate(draft)).length > 0) {
    return null;
  }
  var note = {
    id: state.nextId,
    title: String(draft.title).trim(),
    body: String(draft.body).trim(),
    tag: draft.tag,
    seq: state.seq
  };
  state.nextId += 1;
  state.seq += 1;
  state.notes.push(note);
  saveState();
  return note;
}

function updateNote(id, draft) {
  var note = getNote(id);
  if (note === null) {
    return null;
  }
  if (Object.keys(validate(draft)).length > 0) {
    return null;
  }
  note.title = String(draft.title).trim();
  note.body = String(draft.body).trim();
  note.tag = draft.tag;
  note.seq = state.seq;
  state.seq += 1;
  saveState();
  return note;
}

function deleteNote(id) {
  var wanted = Number(id);
  var before = state.notes.length;
  state.notes = state.notes.filter(function (note) { return note.id !== wanted; });
  if (state.notes.length === before) {
    return false;
  }
  saveState();
  return true;
}

/* ------------------------------------------------------------------ display */

function el(tag, props, children) {
  var node = document.createElement(tag);
  var settings = props || {};
  Object.keys(settings).forEach(function (key) {
    if (key === 'text') {
      node.textContent = settings[key];
    } else if (key === 'class') {
      node.className = settings[key];
    } else {
      node.setAttribute(key, settings[key]);
    }
  });
  (children || []).forEach(function (child) { node.appendChild(child); });
  return node;
}

function setStatus(message) {
  statusEl.textContent = message || '';
}

function renderNotFound() {
  viewEl.appendChild(el('p', { id: 'not-found', text: 'That note does not exist.' }));
}

function renderList() {
  var notes = listNotes();
  if (notes.length === 0) {
    viewEl.appendChild(el('p', { id: 'no-notes', text: 'No notes yet. Start with New note.' }));
    return;
  }
  var list = el('ul', { id: 'note-list' });
  notes.forEach(function (note) {
    var link = el('a', { class: 'note-link', href: '#/notes/' + note.id, text: note.title });
    var tag = el('span', { class: 'note-tag', text: note.tag });
    list.appendChild(el('li', { class: 'note-row', 'data-id': String(note.id) }, [link, tag]));
  });
  viewEl.appendChild(list);
}

function renderDetail(id) {
  var note = getNote(id);
  if (note === null) {
    renderNotFound();
    return;
  }
  viewEl.appendChild(el('article', { id: 'note-detail', 'data-id': String(note.id) }, [
    el('h2', { id: 'detail-title', text: note.title }),
    el('p', { id: 'detail-body', text: note.body }),
    el('p', { id: 'detail-tag', class: 'note-tag', text: note.tag }),
    el('a', { id: 'edit-link', href: '#/notes/' + note.id + '/edit', text: 'Edit' }),
    el('button', { id: 'delete-btn', type: 'button', text: 'Delete' })
  ]));
}

function renderForm(note) {
  var form = el('form', { id: 'note-form' });

  form.appendChild(el('label', { for: 'f-title', text: 'Title' }));
  var title = el('input', { id: 'f-title', name: 'title', type: 'text', autocomplete: 'off' });
  title.value = note ? note.title : '';
  form.appendChild(title);
  form.appendChild(el('p', { id: 'err-title', class: 'field-error' }));

  form.appendChild(el('label', { for: 'f-body', text: 'Body' }));
  var body = el('textarea', { id: 'f-body', name: 'body', rows: '5' });
  body.value = note ? note.body : '';
  form.appendChild(body);
  form.appendChild(el('p', { id: 'err-body', class: 'field-error' }));

  form.appendChild(el('label', { for: 'f-tag', text: 'Tag' }));
  var select = el('select', { id: 'f-tag', name: 'tag' });
  select.appendChild(el('option', { value: '', text: 'Choose a tag' }));
  TAGS.forEach(function (tag) {
    select.appendChild(el('option', { value: tag, text: tag }));
  });
  select.value = note ? note.tag : '';
  form.appendChild(select);
  form.appendChild(el('p', { id: 'err-tag', class: 'field-error' }));

  form.appendChild(el('button', {
    id: 'save-btn',
    type: 'submit',
    text: note ? 'Save changes' : 'Create note'
  }));

  viewEl.appendChild(form);
}

function showErrors(errors) {
  ['title', 'body', 'tag'].forEach(function (field) {
    var holder = document.getElementById('err-' + field);
    if (holder) {
      holder.textContent = errors[field] || '';
    }
  });
}

function render() {
  viewEl.textContent = '';
  var route = state.route;
  if (route.name === 'list') {
    renderList();
  } else if (route.name === 'new') {
    renderForm(null);
  } else if (route.name === 'detail') {
    renderDetail(route.id);
  } else if (route.name === 'edit') {
    var note = getNote(route.id);
    if (note === null) {
      renderNotFound();
    } else {
      renderForm(note);
    }
  } else {
    renderNotFound();
  }
}

function navigate(hash) {
  state.route = parseRoute(hash);
  render();
  return state.route;
}

/* ----------------------------------------------------------------- handlers */

viewEl.addEventListener('submit', function (event) {
  if (!event.target || event.target.id !== 'note-form') {
    return;
  }
  event.preventDefault();
  var draft = {
    title: document.getElementById('f-title').value,
    body: document.getElementById('f-body').value,
    tag: document.getElementById('f-tag').value
  };
  var errors = validate(draft);
  if (Object.keys(errors).length > 0) {
    showErrors(errors);
    setStatus('Fix the highlighted fields.');
    return;
  }
  var saved = state.route.name === 'edit'
    ? updateNote(state.route.id, draft)
    : createNote(draft);
  if (saved === null) {
    setStatus('That note could not be saved.');
    return;
  }
  setStatus('Saved.');
  navigate('#/notes/' + saved.id);
});

viewEl.addEventListener('click', function (event) {
  var button = event.target.closest('#delete-btn');
  if (!button) {
    return;
  }
  var article = document.getElementById('note-detail');
  if (!article) {
    return;
  }
  if (deleteNote(Number(article.dataset.id))) {
    setStatus('Note deleted.');
    navigate('#/notes');
  }
});

window.addEventListener('hashchange', function () {
  navigate(window.location.hash);
});

loadState();
navigate(window.location.hash);
'''},
        ],
        "tests": [
            {"name": "parseRoute maps every shape", "code": r'''
var _list = parseRoute('');
assertEqual(_list.name, 'list', 'An empty hash is the list route, got ' + _list.name);
assertEqual(_list.id, null, 'The list route carries no id, got ' + _list.id);
assertEqual(parseRoute('#/').name, 'list', '"#/" is the list route, got ' + parseRoute('#/').name);
assertEqual(parseRoute('#/notes').name, 'list', '"#/notes" is the list route, got ' + parseRoute('#/notes').name);
assertEqual(parseRoute('#/notes/new').name, 'new', '"#/notes/new" is the new route, got ' + parseRoute('#/notes/new').name);
var _detail = parseRoute('#/notes/12');
assertEqual(_detail.name, 'detail', '"#/notes/12" is the detail route, got ' + _detail.name);
assertEqual(_detail.id, 12, 'and its id is the number 12, got ' + JSON.stringify(_detail.id));
var _edit = parseRoute('#/notes/12/edit');
assertEqual(_edit.name, 'edit', '"#/notes/12/edit" is the edit route, got ' + _edit.name);
assertEqual(_edit.id, 12, 'and its id is 12, got ' + JSON.stringify(_edit.id));
assertEqual(parseRoute('#/nonsense').name, 'notfound', 'An unknown path is notfound, got ' + parseRoute('#/nonsense').name);
assertEqual(parseRoute('#/notes/abc').name, 'notfound', 'A non-numeric id is notfound, got ' + parseRoute('#/notes/abc').name);
'''},
            {"name": "validate is total and precise", "code": r'''
var _good = { title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' };
assertEqual(Object.keys(validate(_good)).length, 0, 'A good draft should produce no errors, got ' + JSON.stringify(validate(_good)));
assert(validate({ title: '   ', body: _good.body, tag: 'field' }).title, 'A blank title needs a title message');
var _long = new Array(62).join('x');
assertEqual(_long.length, 61, 'test fixture should be 61 characters, got ' + _long.length);
assert(validate({ title: _long, body: _good.body, tag: 'field' }).title, 'A 61-character title needs a title message');
assert(validate({ title: 'ok', body: 'too short', tag: 'field' }).body, 'A 9-character body needs a body message');
assert(validate({ title: 'ok', body: _good.body, tag: 'weather' }).tag, 'An unknown tag needs a tag message');
var _empty = validate({});
assert(_empty.title && _empty.body && _empty.tag, 'An empty draft is wrong in three ways, got ' + JSON.stringify(_empty));
'''},
            {"name": "createNote stores, numbers and refuses", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
var _a = createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
assert(_a !== null, 'createNote should return the note it created, got null');
assertEqual(_a.id, 1, 'The first note gets id 1, got ' + _a.id);
assertEqual(state.notes.length, 1, 'state.notes should hold one note, got ' + state.notes.length);
var _b = createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
assertEqual(_b.id, 2, 'Ids increment, got ' + _b.id);
assert(_b.seq > _a.seq, 'The newer note should carry the higher seq, got ' + _b.seq + ' vs ' + _a.seq);
assertEqual(createNote({ title: '', body: 'x', tag: 'nope' }), null, 'An invalid draft must be refused with null');
assertEqual(state.notes.length, 2, 'A refused create must leave the collection alone, got ' + state.notes.length);
'''},
            {"name": "getNote and listNotes", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
assertEqual(getNote(1).title, 'Culvert survey', 'getNote(1) should find the first note, got ' + JSON.stringify(getNote(1)));
assertEqual(getNote(99), null, 'An unknown id gives null, got ' + JSON.stringify(getNote(99)));
var _rows = listNotes();
assertEqual(_rows.length, 2, 'listNotes should return both notes, got ' + _rows.length);
assertEqual(_rows[0].id, 2, 'Newest touched first: expected id 2 at the front, got ' + _rows[0].id);
assertEqual(state.notes[0].id, 1, 'listNotes must not reorder state.notes itself, got ' + state.notes[0].id);
'''},
            {"name": "updateNote writes, restamps and refuses", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
var _u = updateNote(1, { title: 'Culvert survey (revisit)', body: 'Water level 55cm after rain, still clear.', tag: 'field' });
assert(_u !== null, 'updateNote should return the note it changed, got null');
assertEqual(getNote(1).title, 'Culvert survey (revisit)', 'The stored title should change, got ' + getNote(1).title);
assertEqual(listNotes()[0].id, 1, 'An edited note rises to the top of listNotes, got id ' + listNotes()[0].id);
assertEqual(updateNote(1, { title: '', body: 'nope', tag: 'field' }), null, 'An invalid edit is refused with null');
assertEqual(getNote(1).title, 'Culvert survey (revisit)', 'A refused edit must not change the note, got ' + getNote(1).title);
assertEqual(updateNote(404, { title: 'x', body: 'aaaaaaaaaaaa', tag: 'lab' }), null, 'Editing an unknown id gives null');
'''},
            {"name": "deleteNote removes exactly once", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
assertEqual(deleteNote(1), true, 'Deleting an existing note returns true');
assertEqual(getNote(1), null, 'and the note is gone, got ' + JSON.stringify(getNote(1)));
assertEqual(state.notes.length, 1, 'one note should remain, got ' + state.notes.length);
assertEqual(deleteNote(1), false, 'Deleting it again returns false');
assertEqual(deleteNote(999), false, 'Deleting an unknown id returns false');
'''},
            {"name": "The list route renders rows and the empty case", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
navigate('#/notes');
var _rows = document.querySelectorAll('#note-list .note-row');
assertEqual(_rows.length, 2, 'The list route should render one row per note, found ' + _rows.length);
assertEqual(_rows[0].dataset.id, '2', 'Newest first: the leading row should be note 2, got ' + _rows[0].dataset.id);
var _link = _rows[0].querySelector('.note-link');
assert(_link !== null, 'Each row needs an <a class="note-link"> to the detail route');
assertEqual(_link.getAttribute('href'), '#/notes/2', 'The link should target the detail route, got ' + _link.getAttribute('href'));
assert(_link.textContent.indexOf('Soil pH') !== -1, 'The link text should be the note title, got: ' + _link.textContent);
localStorage.removeItem('field-notes-v1');
loadState();
navigate('#/notes');
assert(document.getElementById('no-notes') !== null, 'With no notes the list route should render #no-notes');
assert(document.getElementById('note-list') === null, 'and no empty <ul id="note-list">');
'''},
            {"name": "The detail route, and a missing note", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
navigate('#/notes/1');
var _article = document.getElementById('note-detail');
assert(_article !== null, 'The detail route should render #note-detail');
assertEqual(_article.dataset.id, '1', '#note-detail should carry data-id, got ' + _article.dataset.id);
assertEqual(document.getElementById('detail-title').textContent, 'Culvert survey', 'Wrong #detail-title, got ' + document.getElementById('detail-title').textContent);
assert(document.getElementById('detail-body').textContent.indexOf('Water level') !== -1, '#detail-body should show the note body, got: ' + document.getElementById('detail-body').textContent);
assertEqual(document.getElementById('detail-tag').textContent.trim(), 'field', 'Wrong #detail-tag, got ' + document.getElementById('detail-tag').textContent);
assertEqual(document.getElementById('edit-link').getAttribute('href'), '#/notes/1/edit', 'Wrong #edit-link href, got ' + document.getElementById('edit-link').getAttribute('href'));
assert(document.getElementById('delete-btn') !== null, 'The detail view needs a #delete-btn');
navigate('#/notes/404');
assert(document.getElementById('not-found') !== null, 'An id that does not exist renders #not-found');
assert(document.getElementById('note-detail') === null, 'and no stale #note-detail');
'''},
            {"name": "The edit route arrives pre-filled", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
navigate('#/notes/2/edit');
assert(document.getElementById('note-form') !== null, 'The edit route should render #note-form');
assertEqual(document.getElementById('f-title').value, 'Soil pH', '#f-title should start filled, got ' + JSON.stringify(document.getElementById('f-title').value));
assert(document.getElementById('f-body').value.indexOf('Three samples') !== -1, '#f-body should start filled, got ' + JSON.stringify(document.getElementById('f-body').value));
assertEqual(document.getElementById('f-tag').value, 'lab', '#f-tag should start on the note tag, got ' + document.getElementById('f-tag').value);
navigate('#/notes/404/edit');
assert(document.getElementById('not-found') !== null, 'Editing a note that is gone renders #not-found');
'''},
            {"name": "An invalid submit shows messages and saves nothing", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
navigate('#/notes/new');
var _form = document.getElementById('note-form');
assert(_form !== null, 'The new route should render #note-form');
document.getElementById('f-title').value = '';
document.getElementById('f-body').value = 'too short';
document.getElementById('f-tag').value = '';
var _bad = new Event('submit', { bubbles: true, cancelable: true });
_form.dispatchEvent(_bad);
assert(_bad.defaultPrevented, 'Call event.preventDefault() on the form submit');
assertEqual(state.notes.length, 2, 'An invalid submit must not create a note, got ' + state.notes.length);
assert(document.getElementById('err-title').textContent.trim() !== '', '#err-title should explain the problem');
assert(document.getElementById('err-body').textContent.trim() !== '', '#err-body should explain the problem');
assert(document.getElementById('err-tag').textContent.trim() !== '', '#err-tag should explain the problem');
assertEqual(state.route.name, 'new', 'A refused submit stays on the form, got route ' + state.route.name);
'''},
            {"name": "A valid submit creates and routes to the detail view", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
navigate('#/notes/new');
document.getElementById('f-title').value = 'Weir inspection';
document.getElementById('f-body').value = 'Downstream gauge reads 1.2m, gate free to move.';
document.getElementById('f-tag').value = 'field';
document.getElementById('note-form').dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
assertEqual(state.notes.length, 3, 'A valid submit should create the note, got ' + state.notes.length);
assertEqual(state.route.name, 'detail', 'and route to the detail view, got ' + state.route.name);
assertEqual(state.route.id, 3, 'for the id just created, got ' + state.route.id);
assertEqual(document.getElementById('detail-title').textContent, 'Weir inspection', 'The detail view should show the new note, got ' + document.getElementById('detail-title').textContent);
'''},
            {"name": "Delete from the detail view returns to the list", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
navigate('#/notes/2');
document.getElementById('delete-btn').click();
assertEqual(state.notes.length, 1, 'The delete button should remove the note, got ' + state.notes.length);
assertEqual(state.route.name, 'list', 'and route back to the list, got ' + state.route.name);
assertEqual(document.querySelectorAll('#note-list .note-row').length, 1, 'with one row left, found ' + document.querySelectorAll('#note-list .note-row').length);
assertEqual(getNote(2), null, 'and note 2 is gone');
'''},
            {"name": "State survives a reload, and junk does not break it", "code": r'''
localStorage.removeItem('field-notes-v1');
loadState();
createNote({ title: 'Culvert survey', body: 'Water level 40cm, no blockage observed.', tag: 'field' });
createNote({ title: 'Soil pH', body: 'Three samples averaged 6.4 across the north plot.', tag: 'lab' });
var _raw = localStorage.getItem('field-notes-v1');
assert(_raw !== null, 'saveState() should write to localStorage under "field-notes-v1"');
state.notes = [];
loadState();
assertEqual(state.notes.length, 2, 'loadState() should bring both notes back, got ' + state.notes.length);
var _third = createNote({ title: 'Third', body: 'Ten or more characters here.', tag: 'admin' });
assertEqual(_third.id, 3, 'Ids must not restart after a reload, got ' + _third.id);
localStorage.setItem('field-notes-v1', 'not json at all {{{');
var _threw = null;
try {
  loadState();
} catch (err) {
  _threw = err;
}
assert(_threw === null, 'loadState() must survive junk in storage, but it threw: ' + _threw);
assertEqual(state.notes.length, 0, 'Unreadable storage falls back to an empty collection, got ' + state.notes.length);
localStorage.removeItem('field-notes-v1');
loadState();
navigate('#/notes');
'''},
        ],
    },
}
