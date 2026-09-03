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
            "read": [
                {
                    "title": "What a screen reader hears",
                    "minutes": 12,
                    "body": r'''
Someone opens the Riverside Bike Workshop page with a screen reader running. It is the
page you are handed in this module's lab, and on a monitor it looks finished: a banner, a
menu, a photograph, two sections, a form with a button. The screen reader user presses the
key that lists the page's landmarks and hears *no landmarks*. They press H to move to the
next heading and hear *no headings*. They press Tab until focus lands in the form and hear
*edit text* — a field, with no word attached to say what it is for. Every one of those
failures is a `<div>` where a more specific element should have been, and not one of them
is visible on the monitor, because the stylesheet paints a `<div class="brand">` and an
`<h1>` identically.

## Two trees from one file

The browser builds the DOM from your markup, and then it builds a second tree from the
first: the accessibility tree. Every node in it carries a **role** (heading, button, text
field, landmark), a **name** (the words announced when the node is reached), and sometimes
a **state** (checked, expanded, disabled). Assistive technology reads that second tree and
nothing else. It does not see the pixels.

A `<div>` contributes a node with no role worth announcing, so a page built from them is a
page whose second tree is a flat run of text. An `<h2>` contributes *heading, level 2* plus
its text. A `<button>` contributes *button* plus its label, and the promise that Enter and
Space will activate it. Semantic markup is not a courtesy to the reader of the source; it
is the only way anything gets into the tree the screen reader is reading.

Here is a toy version of what a screen reader does with the two trees. It handles four
cases — landmarks, headings, and a text field with or without a label — which is enough
to hear the difference between the lab's starting page and where it needs to go.

```js
var divSoup =
  '<div class="banner"><div class="brand">Riverside Bike Workshop</div></div>' +
  '<div class="content"><div class="section-title">Book a service</div>' +
  '<p>Email address <input type="text" name="email"></p></div>';

var semantic =
  '<header><h1>Riverside Bike Workshop</h1></header>' +
  '<main><h2>Book a service</h2>' +
  '<p><label for="email">Email address</label>' +
  '<input id="email" name="email" type="email"></p></main>';

function announce(html) {
  var doc = new DOMParser().parseFromString(html, 'text/html');
  var landmarks = { header: 'banner', nav: 'navigation', main: 'main', footer: 'contentinfo' };
  var lines = [];
  doc.body.querySelectorAll('*').forEach(function (el) {
    var tag = el.tagName.toLowerCase();
    if (landmarks[tag]) {
      lines.push('landmark, ' + landmarks[tag]);
    } else if (/^h[1-6]$/.test(tag)) {
      lines.push('heading level ' + tag.charAt(1) + ', ' + el.textContent.trim());
    } else if (tag === 'input') {
      var label = el.id ? doc.querySelector('label[for="' + el.id + '"]') : null;
      lines.push((label ? label.textContent.trim() : '(no name)') + ', edit text');
    }
  });
  return lines;
}

console.log('--- the div version');
announce(divSoup).forEach(function (line) { console.log(line); });
console.log('--- the semantic version');
announce(semantic).forEach(function (line) { console.log(line); });
```

The div version produces one line, `(no name), edit text`, because nothing else in it has
a role. The semantic version produces five: a banner landmark, a level-1 heading, a main
landmark, a level-2 heading, and `Email address, edit text`. Same words on screen, same
stylesheet, and the only difference is which tags were chosen. Two notes on the toy:
`DOMParser` gives a detached document, so nothing here is drawn, and a real screen
reader's name computation has a dozen more cases than this — `aria-labelledby`, wrapping
labels, `title` — but the four handled here are the ones that decide most of what the lab
checks.

## Landmarks are the map

Press the landmarks key on a well-built page and you hear something like *banner,
navigation Primary, main, contentinfo*. Those come from `<header>`, `<nav>`, `<main>` and
`<footer>`, and they let someone jump straight to the content without arrowing through the
menu every time. Two rules fall out of what that list is for. There is exactly one
`<main>`, because "jump to the main content" has to have one answer. And when a page has
several `<nav>` elements — a primary menu, a breadcrumb, a footer nav — each needs an
`aria-label`, or the list reads *navigation, navigation, navigation* and the map is
useless. The lab's first check counts `<main>` elements and expects one, and its last
check reads the `aria-label` off the `<nav>`.

## Headings are the table of contents

A sighted reader skims a page by its headings; a screen reader user does the same with a
key that jumps from heading to heading, and the level is announced each time. So the
levels are not sizes. They are nesting: an `h2` is a section of the page, an `h3` is a
section of the `h2` above it. Jump from an `h1` to an `h3` and the announcement says
*there is a subsection here, of a section you were never told about*. Nothing breaks and
nothing fails to render, which is why it survives review; the information is wrong, and
it stays wrong.

That is the rule the lab enforces: walking the headings in document order, no level may be
more than one greater than the one before it. One `h1`, then `h2` for `Services` and
`Book a service`, and `h3` for `Standard tune-up` underneath the first. The temptation to
skip is always visual — `h2` looked too big — and the fix is a line of CSS on the `h2`,
not a different element.

## What a field is called

Focus lands in a text field. The screen reader needs a word to say, and it looks for one
in a fixed order. First, a `<label>` whose `for` attribute holds the field's `id`. Second,
a `<label>` wrapped around the field. Then `aria-labelledby`, then `aria-label`. If all of
those are absent, the placeholder is a last-resort fallback that not every browser and
screen reader pair honours, and what is left is the *edit text* the reader heard at the
start.

Why does `for` bind to `id` and not to `name`? Because `name` is the key the value is
submitted under, and it is deliberately not unique — the two service-level radios in the
lab share `name="level"`, which is what makes them one question. An `id` is unique by
definition, so it can identify one control, and the browser resolves `for` the way it
resolves `getElementById`. The visible proof that a binding took is that clicking the
label focuses the field.

Try it below. Click on the words, not on the boxes.

```html
<style>
  body { font-family: system-ui, sans-serif; line-height: 1.6; padding: 1rem; }
  label { display: block; font-weight: 600; margin-top: 0.75rem; }
  input[type="text"], input[type="email"] { display: block; width: 18rem; padding: 0.35rem 0.5rem; }
  fieldset { margin-top: 1rem; width: 18rem; }
  fieldset label { display: inline; font-weight: 400; }
  .hint { display: block; color: #555; font-size: 0.85rem; }
</style>

<form>
  <label for="name">Full name</label>
  <input id="name" name="name" type="text">

  <label for="email">Email address</label>
  <input id="email" name="email" type="email" required aria-describedby="email-hint">
  <span id="email-hint" class="hint">We only use this to confirm the booking.</span>

  <fieldset>
    <legend>Service level</legend>
    <input id="level-basic" name="level" type="radio" value="basic" checked>
    <label for="level-basic">Basic</label>
    <input id="level-full" name="level" type="radio" value="full">
    <label for="level-full">Full strip-down</label>
  </fieldset>
</form>
```

Clicking *Full name* puts the cursor in the field; clicking *Basic* selects the radio.
Both work because the label knows which control it belongs to, and a screen reader uses
the same binding to know what to say.

## A group is a question

The two radios above have labels, so each announces as *Basic, radio button* or *Full
strip-down, radio button*. What is missing from that is the question. Which of the two is
the right answer depends on knowing they are choices for *Service level*, and that text is
a paragraph somewhere above — visually adjacent, structurally unrelated. `<fieldset>` with
a `<legend>` is how the relation is written down: the legend is announced when focus
enters the group, so the reader hears *Service level, group, Basic, radio button, one of
two*. Any set of controls that answer one question belongs in a fieldset, and radios
sharing a `name` always do.

## A description is not a name

The email field has a hint: *We only use this to confirm the booking.* The tempting move
is to put that sentence in the label, so it is announced. It is announced — every single
time focus lands there, before the person can type, and a voice-control user now has to
say the whole sentence to reach the field. A control has one name, which wants to be
short, and any amount of description, which is announced after the name and can be
skipped. `aria-describedby="email-hint"` on the input, pointing at the `id` of the span,
makes the sentence a description. The span stays where it was, visible to everyone; the
attribute only records how the two are related. The lab's last check follows that `id`
and insists the element it lands on exists and has text in it.

## What a picture says

When the reader reaches an image, three things can happen. With `alt="A road bicycle
clamped in a workshop repair stand"`, that sentence is read, in the voice of the page.
With `alt=""`, the image is skipped, because an empty `alt` is a statement: *this carries
nothing the text does not*. With no `alt` attribute at all, the screen reader has no
description and falls back to what it does have, which is the file name — `stand.jpg`,
spelled out. So every `<img>` gets an `alt`, and the choice is between describing it and
declaring it decorative. The lab's photo is on a booking page because it shows the
workshop has proper stands, so it earns a description, and the check asks for at least ten
characters of one — a clause, not a word.

## Native elements arrive finished

`<div role="button" tabindex="0">Delete</div>` announces as a button and can be tabbed to,
and people who have got that far often stop. Press Enter on it and nothing happens. A real
`<button>` fires a click on Enter and on Space, honours `disabled`, submits a form when it
is the form's submit button, and sits in the tab order without being asked. The `div` has
to be handed each of those by hand, in JavaScript, and the usual result is a control that
works with a mouse and not otherwise. This module's tab-stop exercise counts what needs
nothing written on it — `<a href>`, `<button>`, `<input>`, `<select>`, `<textarea>` — and
it is most of the list.

The same goes for `type="submit"` on the form's button. It is what makes Enter in the
email field send the form, and it is what runs constraint validation on the way, so
`required` and `type="email"` are checked without a line of script.

## The mistake, and why it is tempting

The one that ships most often is the placeholder used as the label:
`<input placeholder="Email address">` with no `<label>` at all. It is tempting because it
looks tidy, it saves a line of vertical space, and on the developer's own screen the field
is plainly an email field. Then someone types into it and the words vanish at exactly the
moment they want to check what the field was for; the grey text fails contrast before
that; and it reaches the accessibility tree as a name only as a fallback, so some screen
readers say *edit text* and nothing more. The label is not decoration that the placeholder
replaces. It is the name.

## Where this stops holding

Semantic markup gets the structure into the tree; it does not make the words true. The lab
checks that an `alt` is at least ten characters long, and `alt="aaaaaaaaaaaa"` passes it —
no automated check can tell whether a description describes. A `<header>` is announced as
a banner only when it is the page's header, not when it is nested inside an `<article>`
or `<section>`. `aria-label` on a `<div>` with no role does nothing at all, and
`aria-label` on a `<button>` *overrides* its visible text, which is how a button that says
*Send* comes to announce as *Submit form* and stops answering to the word a voice-control
user can see. And screen readers disagree with each other in the details: the
announcements in this reading are the common shape, not a transcript of any one product.

## In the lab

*A booking form a screen reader can navigate* hands you the div-only page and a read-only
stylesheet that already styles `header`, `main`, `h2`, `label` and `fieldset`. You rewrite
`index.html` so that every failure the reader met in the first paragraph is gone:
landmarks with one `<main>`, headings that never skip a level, a `<label for>` on every
control, the radios in a `<fieldset>` with a `<legend>`, an `alt` on the image, and the
email field wired to its hint with `aria-describedby`. Keep the same words on the page.
Six checks read the accessibility tree back, and each one corresponds to something the
reader could not hear.
''',
                },
                {
                    "title": "What the browser does with your file",
                    "minutes": 11,
                    "body": r'''
Save a file called `index.html`, open it, and a page appears. The browser did not *run*
that file the way a Python interpreter runs a script. It **parsed** it: read the
characters once, top to bottom, and built out of them a tree of objects — the DOM. Every
other thing that happens afterwards is work done on that tree and not on your file. The
pixels are painted from it. The stylesheet matches against it. Script reads and rewrites
it. The accessibility tree this module's first reading is about is built from it. So the
first question to ask about a piece of markup is not how it will look; it is *what node
does this become*.

## Four steps, and where you get a say

1. The browser asks a server for a URL, and gets bytes back with a `Content-Type` header
   saying what kind of thing they are.
2. It decodes those bytes into characters, using `<meta charset="utf-8">` if you supplied
   one and guessing if you did not — which is where a curly quote turns into `â€™`.
3. It parses the characters into the DOM, one node per element, per attribute, and per
   run of text.
4. It fetches whatever the tree points at — the stylesheet in `<link>`, the code in
   `<script>`, the picture in `<img>` — and applies each to the tree.

You write the markup at step 3 and the two languages that arrive at step 4. Everything in
this course is one of those three.

## An element, taken apart

```html
<p class="intro">Wiper blades, <strong>fitted while you wait</strong>.</p>
```

`<p>` is the start tag, `</p>` the end tag, and what sits between them is the element's
content. `class="intro"` is an **attribute**: a name and a value, written on the start
tag, that carries information the tag alone cannot. Elements nest, so the `<strong>` is a
child of the `<p>`, and an end tag closes the most recently opened element — you close in
the reverse of the order you opened.

A handful of elements have no content and therefore no end tag: `<img>`, `<br>`,
`<input>`, `<meta>`, `<link>`, `<hr>`. Writing `<img></img>` does not create a closed
image; it creates an image and then a stray end tag the parser throws away.

## The skeleton, line by line

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Shown in the browser tab</title>
    <link rel="stylesheet" href="style.css">
  </head>
  <body>
    <!-- everything visible goes here -->
  </body>
</html>
```

Not one of those lines is decoration. `<!doctype html>` selects standards mode; leave it
out and the browser switches to a quirks mode written to keep 1998 working, in which the
box model is the wrong one. `lang="en"` tells a screen reader which voice to read with
and a browser which hyphenation rules to use. `charset` fixes step 2, and it has to
appear in the first 1024 bytes, which is why it is the first thing in the `<head>`. The
viewport meta is what makes a phone report a 360-pixel viewport instead of pretending to
be a 980-pixel desktop, and without it the next module's media queries never match.
`<title>` names the tab, the bookmark and the search result. `<!-- -->` is a comment: it
becomes a node in the tree, and it is never drawn.

## Markup is a tree, and the parser will make one whether or not you did

The nesting is the tree, and the parser refuses to hand back anything that is not one. If
your tags do not describe a tree, it repairs them — silently, by rules you did not choose.

```js
var written =
  '<div id="card">' +
  '<p>Fitted while you wait. <div class="note">Two working days.</div></p>' +
  '</div>';

var doc = new DOMParser().parseFromString(written, 'text/html');

function outline(node, depth) {
  var lines = [];
  Array.prototype.forEach.call(node.children, function (el) {
    lines.push(new Array(depth + 1).join('  ') + '<' + el.tagName.toLowerCase() +
      (el.id ? ' id="' + el.id + '"' : '') +
      (el.className ? ' class="' + el.className + '"' : '') + '>');
    lines = lines.concat(outline(el, depth + 1));
  });
  return lines;
}

console.log(outline(doc.body, 0).join('\n'));
console.log('#card holds ' + doc.getElementById('card').children.length + ' child element(s)');
console.log('.note sits inside <' + doc.querySelector('.note').parentElement.tagName.toLowerCase() + '>');
```

Two elements were written inside `#card` and three come out. A `<div>` start tag is not
allowed inside a `<p>`, so the parser closes the paragraph before it, hangs the `<div>`
off `#card` as a sibling, and then meets a `</p>` with no open paragraph to close — which
it handles by inserting an empty one. `.note` is a child of the `div`, not of the `p`, so
a rule written as `p .note { ... }` matches nothing and a script that reads
`noteEl.parentElement` gets `#card`. Nothing threw, nothing failed to render, and the
tree is not the tree you wrote.

## The elements you will reach for

| Element | Job |
|---|---|
| `<h1>` … `<h6>` | headings — one `<h1>` per page, `<h2>` for its sections |
| `<p>` | a paragraph of prose |
| `<a href="https://…">` | a link; `href` is where it goes, and without one it is not a link |
| `<img src="photo.jpg" alt="…">` | an image, with `alt` standing in for it |
| `<ul>` `<ol>` `<li>` | unordered and ordered lists; only `<li>` may be their child |
| `<button>` | something to press |
| `<form>` `<label>` `<input>` | collecting what someone types |
| `<div>` `<span>` | a block and an inline box with no meaning of their own |

`<div>` and `<span>` are last on the list on purpose. They are the elements to reach for
when nothing more specific fits, and the moment something more specific does fit — a
heading, a list, a button — the tree is better for it, because a `<div>` contributes a
node that says nothing.

## Sectioning, next to landmarks

`<header>`, `<nav>`, `<main>` and `<footer>` are the landmarks the module's other reading
covers: they answer *where am I on this page*. `<section>`, `<article>` and `<aside>`
answer a different question — *what is this piece of content*. An `<article>` is
self-contained enough to make sense lifted out of the page: a post, a product card, a
comment. A `<section>` is a thematic group inside the page and wants a heading, because a
section nobody named is one a screen reader announces as *region* with nothing after it.
An `<aside>` is related but skippable. Use them for what they say, not for the boxes they
draw, because they draw none.

## id and class

`id="x"` names exactly one element in the document. `class="a b"` is a reusable label and
an element can carry several, separated by spaces. The distinction is not stylistic: an
`id` is what `<label for>` binds to, what `aria-describedby` points at, what a `#fragment`
in a URL scrolls to, and what `document.getElementById` looks up — all of which assume
there is one. Repeat an `id` and the browser does not complain; it hands the first match
to every one of those and the rest of them stop working.

## The mistake, and why it is tempting

The one that costs the most time is putting a block element inside a `<p>` — the bug the
example above ran into. It is tempting because it reads correctly in the file: a note
belongs to the paragraph it is about, so nesting it looks like saying so. But `<p>` is
defined as holding only inline content, and the parser enforces that by moving your
element rather than by telling you. You then write CSS that matches nothing and read a
`parentElement` that is not the one on screen, and the source in your editor disagrees
with the tree in the inspector. The fix is not to nest more carefully; it is to notice
that `<p>` means *paragraph of text*, and a container that holds other blocks is a
`<div>` or a `<section>`.

## Where this stops holding

The DOM is not a copy of the file, and it drifts from it as soon as anything runs. View
Source shows the bytes that arrived; the Elements panel shows the tree as it is right
now, including everything script has added. When the two disagree, the panel is the one
that is true.

The repairs above are helpful precisely when you do not want them: a validator will tell
you about broken nesting, the parser will not. And `<script>` is a special case in the
parse — a classic `<script src>` in the `<head>` blocks parsing until it has been fetched
and run, which is why the tag is written immediately before `</body>` in the labs here,
or given `defer` so it waits for the tree to be finished.

## In the lab

*A profile page built from real elements* hands you an empty `<body>` and asks for a
page: a `<header>` with the name in an `<h1>`, a `<main>` around the content, an image
whose `alt` says what it shows, a paragraph, a list of at least three items, and a link
that actually goes somewhere. Six checks read the tree back — none of them looks at a
single pixel.
''',
                },
            ],
            "quiz": [{
                "title": "What the markup promises",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A `<label for=\"...\">` binds to a control. What does the value of `for` have to match?",
                        "opts": [
                            "The control's `id`",
                            "The control's `name`",
                            "The control's `placeholder`",
                            "The `id` of the form the control sits in",
                        ],
                        "a": 0,
                        "why": r"""
`for` holds an id and the browser resolves it the way `getElementById` does. `name` is
what the server sees on submit and is deliberately *not* unique — the two radios in this
lab share `name="level"` — so binding to it could not identify one control. And a
placeholder is not a label at all: it vanishes the moment someone types, which is
exactly when they most want to check what the field was for.
""",
                    },
                    {
                        "q": "A page has an `h1`, then a section headed `h3` because `h2` looked too big. What did that cost?",
                        "opts": [
                            "Nothing — heading levels are a visual choice",
                            "The outline now implies a level-2 section that does not exist, so anyone navigating by heading hears a gap",
                            "The page stops validating and the browser skips the section",
                            "Search engines discard every heading after the skip",
                        ],
                        "a": 1,
                        "why": r"""
Headings are the page's table of contents, and a screen reader user moves through them
the way a sighted reader skims — jumping from level to level. A jump from `h1` to `h3`
says *there is a subsection here, of a section you were never told about*. Nothing
breaks and nothing fails to render; the information is simply wrong. Size is a separate
question entirely: `h2 { font-size: 1rem }` costs you nothing and keeps the outline
honest.
""",
                    },
                    {
                        "q": "A decorative flourish sits beside a heading and repeats it. What belongs in its `alt`?",
                        "opts": [
                            "`alt=\"\"` — an empty string",
                            "No `alt` attribute at all",
                            "`alt=\"decorative image\"`",
                            "`alt=\"flourish.svg\"`",
                        ],
                        "a": 0,
                        "why": r"""
An empty `alt` is a statement, not an omission: *this image carries nothing the text
does not already say, skip it*. Leaving the attribute off is a different thing — the
image has no description, and assistive technology commonly falls back to announcing the
file name, so `flourish.svg` gets read aloud one character at a time. Writing
`decorative image` is the same problem said politely: it is an interruption that adds
nothing.
""",
                    },
                    {
                        "q": "`<div role=\"button\" tabindex=\"0\">Delete</div>` announces as a button and can be tabbed to. What is still missing?",
                        "opts": [
                            "Nothing — that is equivalent to a `<button>`",
                            "An accessible name, which a `<div>` cannot have",
                            "Keyboard activation: a real button fires a click on Enter and Space, a div does not",
                            "Focus — `tabindex=\"0\"` does not put an element in the tab order",
                        ],
                        "a": 2,
                        "why": r"""
`role` buys the announcement and `tabindex="0"` buys the focus stop, and both of those
are true here. What neither buys is *behaviour*. Press Enter or Space on that div and
nothing happens until you write a `keydown` handler for both keys — and then you still
owe it `disabled` semantics, and form submission if it lives in a form. Its text content
does give it a name, so that part is fine. This is the argument for reaching for
`<button>` first: everything above arrives already written.
""",
                    },
                    {
                        "q": "What does `aria-describedby` do that `<label for>` does not?",
                        "opts": [
                            "It replaces the label for controls that have no visible text",
                            "It attaches supplementary text that is announced after the name, without becoming the name",
                            "It only works on elements with an explicit `role`",
                            "It hides the referenced text from sighted users",
                        ],
                        "a": 1,
                        "why": r"""
A control has one name and any amount of description. The name is what gets announced
when focus lands and what a voice-control user says out loud, so it wants to stay short:
*Email address*. The hint — "we only use this to confirm the booking" — is a
description, announced after the name and skippable. Fold it into the label and every
visit to that field replays the whole sentence. The referenced element stays perfectly
visible; `aria-describedby` only says how the two are related.
""",
                    },
                ],
            }, {
                "title": "Elements, attributes and the tree",
                "minutes": 6,
                "questions": [
                    {
                        "q": "A photo of a bicycle in a repair stand sits on the page. What does its `alt` attribute do?",
                        "opts": [
                            "Stands in for the picture — read aloud, and shown when the file fails to load",
                            "Shows a tooltip with the same words when the pointer rests on the image",
                            "Tells the browser which file to request, so `src` and `alt` must agree",
                            "Marks the image decorative, so assistive technology passes over it without announcing anything",
                        ],
                        "a": 0,
                        "why": r"""
`alt` is the picture written down, and it earns its keep in two different failures: the
person cannot see the image, or the image never arrived. The tooltip is a different
attribute — `title` — announced inconsistently, never on touch, and never on keyboard
focus in several browsers. `src` alone names the file; an `alt` that repeats the file
name is the worst outcome, because that is exactly what assistive technology falls back
to when the attribute is missing entirely. And an image is declared decorative by
`alt=""` — the empty string, deliberately written — not by describing it as decorative.
""",
                    },
                    {
                        "q": "Which of these is a correctly structured list?",
                        "opts": [
                            "`<ul><li>One</li><li>Two</li></ul>`",
                            "`<li><ul>One</ul><ul>Two</ul></li>`",
                            "`<ul>One<br>Two</ul>`",
                            "`<list><item>One</item><item>Two</item></list>`",
                        ],
                        "a": 0,
                        "why": r"""
The items live inside the list and the text lives inside the items: the children of a
`<ul>` are `<li>` elements, and that is what lets a screen reader announce *list, three
items* and
then count down as you move. Turning it inside out puts a list inside an item, which the
parser will rearrange rather than reject. Two lines separated by `<br>` look identical on
screen and are one run of text in the tree, with no count and no items. And `<list>` and
`<item>` are not HTML: an unknown tag is not an error either, it becomes an inline
element with no meaning, styled by nothing and announced as nothing.
""",
                    },
                    {
                        "q": "In `<a href=\"https://example.com\">Read more</a>`, what is `href`?",
                        "opts": [
                            "An attribute on the start tag, holding the address the link goes to",
                            "A tag nested inside the anchor, which the browser resolves before drawing it",
                            "The visible label, which the browser draws in place of the text",
                            "A CSS property that gives the anchor its underline and colour",
                        ],
                        "a": 0,
                        "why": r"""
An attribute is a name and a value written on a start tag, and `href` is the one that
carries the destination. It is worth separating from the two things beside it. The label
is the content between the tags, which is what someone reads and what a voice-control
user says out loud; the underline and colour come from the browser's own stylesheet, and
CSS can take them away without the link ceasing to be one. The reverse is not true: an
`<a>` with no `href` is not a link at all — it is text in an anchor element, with no
focus stop, no activation and nothing in the accessibility tree to say it goes anywhere.
""",
                    },
                    {
                        "q": "Why write `<main>` and `<nav>` rather than `<div class=\"main\">` and `<div class=\"nav\">`?",
                        "opts": [
                            "The semantic elements are announced with a role, so the structure reaches the accessibility tree",
                            "The semantic elements are quicker to parse, so the first paint arrives sooner on a slow connection",
                            "`<div>` is deprecated, and browsers will stop supporting it",
                            "The semantic elements arrive with default styling that a `<div>` has to be given",
                        ],
                        "a": 0,
                        "why": r"""
On screen the two are indistinguishable — that is the whole difficulty. The difference is
in the second tree the browser builds: `<main>` contributes a landmark someone can jump
to and `<nav>` contributes another, while a `<div>` contributes a node with no role worth
announcing, whatever its class says. Parsing cost is not the argument; the two are the
same handful of bytes. `<div>` is not deprecated and never will be — it is the right
element when nothing more specific fits. Nor do the semantic elements bring styling worth
having: `<main>` renders as a plain block, which is why the div version looks finished.
""",
                    },
                    {
                        "q": "How many `<h1>` elements does a page normally carry?",
                        "opts": [
                            "One — the page's own title, with `<h2>` and below for its sections",
                            "As many as look right, since the level chooses a size rather than a structure",
                            "None: `<h1>` is reserved for the browser's own chrome",
                            "Six, one of each level, or the outline is incomplete",
                        ],
                        "a": 0,
                        "why": r"""
The headings are the page's table of contents, and someone navigating by heading hears
the level announced each time. One `<h1>` gives that outline a single root; several give
it several, and the reader has no way to tell which one the page is about. The level is
not a size — `h2 { font-size: 1rem }` costs nothing and keeps the outline honest, which
is the fix whenever a heading looks too big. And the six levels are a range to draw from
as the nesting needs them, not a set to be filled in.
""",
                    },
                    {
                        "q": "Which element collects one line of typed text?",
                        "opts": [
                            "`<input>`, bound by `id` to a `<label>` that names it",
                            "`<button>`, whose text content becomes the value",
                            "`<span contenteditable>`, the element built for typing",
                            "`<text>`, the element the form specification defines for this",
                        ],
                        "a": 0,
                        "why": r"""
`<input>` is the form control, and it is only half a control until a `<label for>` points
at its `id` — that binding is what gives it a name to be announced by and what makes
clicking the words focus the field. A `<button>` is pressed, not typed into, and carries
no value a form would submit for it. `contenteditable` does make a `<span>` typeable, and
it is how rich-text editors are built, but it is not a form control: no name, no `value`,
nothing submitted, and every keyboard behaviour written by hand. There is no `<text>`
element; an unrecognised tag falls back to an inline box that quietly does nothing.
""",
                    },
                ],
            }],
            "blanks": {
                "title": "The booking form, attribute by attribute",
                "minutes": 9,
                "caption": "index.html — six holes",
                "lang": "html",
                "brief": r'''
Every hole below is somewhere the page still renders identically and conveys
something different. Nothing is executed here: you are choosing markup, and the
question each time is what the browser puts in the accessibility tree as a result.
''',
                "listing": r'''<header>
  <h1>Riverside Bike Workshop</h1>
  <nav ___="Primary">
    <ul><li><a href="#booking">Book a service</a></li></ul>
  </nav>
</header>

<main>
  <h2 id="booking">Book a service</h2>
  <img src="stand.jpg" alt="___">

  <form id="booking-form" action="#" method="post">
    <label ___="email">Email address</label>
    <input id="email" name="email" type="___" required ___="email-hint">
    <span id="email-hint">We only use this to confirm the booking.</span>

    <fieldset>
      <legend>Service level</legend>
      <input id="level-basic" name="level" type="radio" value="basic">
      <label for="level-basic">Basic</label>
      <input id="level-full" name="level" type="radio" value="full">
      <label for="level-full">Full strip-down</label>
    </fieldset>

    <button type="___">Request booking</button>
  </form>
</main>
''',
                "blanks": [
                    {
                        "prompt": "A page may hold several nav landmarks. How does this one say which it is?",
                        "hole": "attr",
                        "opts": ["aria-label", "title", "name", "id"],
                        "a": 0,
                        "why": "`aria-label` names the landmark, so the landmarks list reads *navigation, Primary* rather than *navigation, navigation*.",
                        "whys": [
                            "`aria-label` names the landmark, so the landmarks list reads *navigation, Primary* rather than *navigation, navigation*. With one nav on the page it is a nicety; with a primary nav, a breadcrumb and a footer nav it is the only thing telling them apart.",
                            "`title` produces a tooltip on hover and is announced inconsistently — it is the attribute that gets recommended and then quietly ignored by half the stack. It is not how a landmark is named.",
                            "`name` means something on form controls and on `<iframe>`; on a `<nav>` it is an invalid attribute the browser drops. Nothing reads it.",
                            "`id` is an anchor for links and for `for`/`aria-*` references. It is never announced, so `id=\"Primary\"` names this nav for your CSS and for nobody else.",
                        ],
                    },
                    {
                        "prompt": "The photo shows a bike in a repair stand. What goes in its alt text?",
                        "hole": "text",
                        "opts": ["stand.jpg", "A road bike clamped in a repair stand", "Image of a bike", "bike"],
                        "a": 1,
                        "why": "Alt text stands in for the picture: describe what it shows and why it is here, in the voice of the surrounding page.",
                        "whys": [
                            "The file name is the one thing assistive technology falls back to when there is no alt at all, so writing it deliberately is the worst of both worlds — it is read out character by character and says nothing.",
                            "Alt text stands in for the picture: describe what it shows and why it is here, in the voice of the surrounding page. A sentence is fine; this one tells you the workshop has proper stands, which is the reason the photo is on a booking page.",
                            "\"Image of\" is redundant — the element is already announced as an image — and \"a bike\" is the level of detail you would get from guessing. Everything informative has been left out.",
                            "One word is not wrong so much as wasted. If the picture is worth its bytes it is worth a clause; if it is not, `alt=\"\"` says so honestly.",
                        ],
                    },
                    {
                        "prompt": "Which attribute points a label at the control it names?",
                        "hole": "attr",
                        "opts": ["id", "for", "name", "aria-labelledby"],
                        "a": 1,
                        "why": "`<label for=\"email\">` binds to the control whose `id` is `email`; clicking the label then focuses the field, which is the visible proof the binding took.",
                        "whys": [
                            "An `id` on the label identifies the label itself. That is useful when a control points *back* with `aria-labelledby`, but on its own it binds nothing.",
                            "`<label for=\"email\">` binds to the control whose `id` is `email`; clicking the label then focuses the field, which is the visible proof the binding took.",
                            "`name` is the key the value is submitted under. Two controls can share it — radios always do — so it could not identify one field to label.",
                            "`aria-labelledby` runs the other way: it goes on the *control* and names the element that labels it. Putting it on the label points the label at itself.",
                        ],
                    },
                    {
                        "prompt": "The field takes an email address. Which input type?",
                        "hole": "type",
                        "opts": ["text", "string", "email", "mail"],
                        "a": 2,
                        "why": "`type=\"email\"` gives constraint validation for free, and on a phone it changes the keyboard that comes up — the `@` and the dot move onto the front row.",
                        "whys": [
                            "`type=\"text\"` works, in the sense that the form still submits. It just declines every piece of help the browser was ready to give: no format check, no autofill hint, and a phone keyboard with the `@` two taps away.",
                            "There is no `string` input type. Unknown types silently fall back to `text`, which is why this class of typo survives review — the field looks fine and quietly does less.",
                            "`type=\"email\"` gives constraint validation for free, and on a phone it changes the keyboard that comes up — the `@` and the dot move onto the front row. Paired with `required` it is a whole validation rule you did not have to write.",
                            "`mail` is not a type either, and falls back to `text` in the same silent way. The list is short and worth knowing: `email`, `tel`, `url`, `number`, `search`, `date`.",
                        ],
                    },
                    {
                        "prompt": "The hint sentence should be announced after the field's name, not as part of it.",
                        "hole": "attr",
                        "opts": ["aria-describedby", "aria-labelledby", "aria-label", "title"],
                        "a": 0,
                        "why": "`aria-describedby` attaches the span as a *description*: announced after the name, and skippable on the second visit to the field.",
                        "whys": [
                            "`aria-describedby` attaches the span as a *description*: announced after the name, and skippable on the second visit to the field. The label stays short, the hint stays visible to everyone, and neither has to be duplicated.",
                            "`aria-labelledby` would make that sentence the field's *name*, and it overrides the `<label>` outright — so the field would announce as \"We only use this to confirm the booking\" and the word *email* would disappear.",
                            "`aria-label` takes a string, not an id, so pointing it at `email-hint` names the field the literal text \"email-hint\". It would also override the visible label, which is the bug that produces controls whose spoken name does not match their printed one.",
                            "`title` is a tooltip. It is announced only sometimes, never on touch, and never on keyboard focus in several browsers — which is why the sentence is in the page as a real element instead.",
                        ],
                    },
                    {
                        "prompt": "The button ends the form. What type is it?",
                        "hole": "type",
                        "opts": ["button", "submit", "reset", "send"],
                        "a": 1,
                        "why": "`type=\"submit\"` is what makes the button submit the form, and what Enter in a text field activates — constraint validation runs on the way.",
                        "whys": [
                            "`type=\"button\"` is the inert one: it does nothing at all unless JavaScript is listening, and the form is left with no default button, so pressing it validates nothing and fires no `submit` event. Enter is the surprise in the other direction. Only text-entry fields block implicit submission — radios and checkboxes do not — so this form has exactly one, the email input, and a form with no submit button and only one such field still submits when Enter is pressed in it. The form can still be sent; the button has simply stopped being the thing that sends it.",
                            "`type=\"submit\"` is what makes the button submit the form, and what Enter in a text field activates — constraint validation runs on the way, so the `required` email is checked because a submit was attempted. It is also the default inside a form, but writing it down means the next person does not have to remember that.",
                            "`type=\"reset\"` wipes every field back to its initial value. It sits one letter away in the autocomplete list and destroys the booking someone has just typed, which is why reset buttons have quietly disappeared from the web.",
                            "There is no `send` type. `submit` is both the default and the fallback for an unrecognised value, so this one accidentally works — which is the worst kind of typo, because nothing ever tells you and the next reader assumes a distinction was meant.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How many tab stops?",
                "minutes": 7,
                "brief": r'''
Keyboard order is not a feature you add at the end. It falls out of which elements
you chose, and you can read it off the markup before the page has any CSS at all.

```html
<a href="#main">Skip to content</a>
<a>Help</a>
<button type="button">Menu</button>
<input id="q" type="search">
<button type="button" disabled>Clear</button>
<div role="button" tabindex="0">Filters</div>
<h2 tabindex="-1">Results</h2>
<textarea id="notes"></textarea>
<select id="sort"><option>Newest</option></select>
```

Nine elements, all visible, none hidden by CSS. Tab forward through them from the
address bar and count where focus actually lands.
''',
                "prompt": "How many of the nine elements does keyboard focus land on?",
                "note": "A whole number. Count stops, not elements.",
                "figure": "`<a href=\"#main\">` Skip to content · `<a>` Help · `<button>` Menu · "
                          "`<input type=\"search\">` Search · `<button disabled>` Clear · "
                          "`<div role=\"button\" tabindex=\"0\">` Filters · `<h2 tabindex=\"-1\">` Results · "
                          "`<textarea>` Notes · `<select>` Sort",
                "given": [
                    {"label": "Elements in the fragment", "value": "9"},
                    {"label": "Stylesheet", "value": "none — nothing hidden or reordered"},
                    {"label": "Direction", "value": "Tab, forwards, from the address bar"},
                ],
                "aside": "The hand-made `<div role=\"button\" tabindex=\"0\">` is a tab stop and announces "
                         "as a button, and still does nothing when you press Enter. Focus is the easy half.",
                "answer": 6,
                "tol": 0,
                "unit": "stops",
                "hint": "Five things are focusable with no help at all: `<a>` **with an href**, `<button>`, "
                        "`<input>`, `<select>`, `<textarea>`. Anything carrying `tabindex=\"0\"` joins them. "
                        "Two things take an element back out again: `disabled`, and `tabindex=\"-1\"`.",
                "wrong": "Nine counts every element rather than every stop. Seven or eight usually means "
                         "`disabled` or `tabindex=\"-1\"` slipped through — both elements are still in the "
                         "DOM and still on screen, they are simply not in the tab order.",
                "why": r"""
Six: the `<a href>`, the `<button>`, the `<input>`, the `<div tabindex="0">`, the
`<textarea>` and the `<select>`. The three skipped are skipped for three different
reasons, and each is worth knowing on its own. An `<a>` with no `href` is not a link —
it is text inside an anchor element, and the browser gives it no behaviour and no focus.
`disabled` removes a control from the tab order along with its events. And
`tabindex="-1"` is the deliberate one: reachable from script with `.focus()`, so a
router can move focus to the results heading after a navigation, but never reached by
tabbing. Notice the shape of the count — five of the six needed nothing written on them,
and the only hand-made control needed an attribute to buy back part of what `<button>`
comes with.
""",
            },
            "lab": [{
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
            }, {
                "title": "A profile page built from real elements",
                "runtime": "web",
                "minutes": 16,
                "brief": r'''
`index.html` holds an empty `<body>` and one image. Build a profile page for a
person — real or invented — out of the elements that say what each part is. There
is no stylesheet, so nothing here can be faked with a class name: every check
reads the tree.

The page must contain:

- a `<header>` holding an `<h1>` with the person's name
- a `<main>` around everything else
- the `<img>`, given an `alt` that describes what the picture shows
- a `<p>` inside `<main>` with a short biography
- a `<ul>` of at least **three** skills, one `<li>` each
- an `<a>` whose `href` starts with `https://`, with visible link text

Press Run to see the preview beside the checks. The page will look plain, and it
is meant to — the structure is the exercise.
''',
                "files": [
                    {"name": "index.html", "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Profile</title>
</head>
<body>

<!-- Build the profile page here. The image below is yours to place and describe. -->
<img src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Crect width='160' height='160' fill='%23d9e2ec'/%3E%3C/svg%3E" alt="">

</body>
</html>
'''},
                ],
                "main": "index.html",
                "solution": [
                    {"name": "index.html", "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Ada Lovelace — profile</title>
</head>
<body>

<header>
  <h1>Ada Lovelace</h1>
  <p>Analyst, metaphysician, first programmer</p>
</header>

<main>
  <img src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Crect width='160' height='160' fill='%23d9e2ec'/%3E%3C/svg%3E" alt="Portrait of Ada Lovelace at a writing desk">

  <p>Ada wrote the first algorithm intended for a machine, decades before anyone
  built one that could run it.</p>

  <h2>Skills</h2>
  <ul>
    <li>Algorithms</li>
    <li>Mathematics</li>
    <li>Technical writing</li>
  </ul>

  <h2>Elsewhere</h2>
  <p><a href="https://en.wikipedia.org/wiki/Ada_Lovelace">Read more about Ada Lovelace</a></p>
</main>

</body>
</html>
'''},
                ],
                "hints": [
                    "Skeleton first: a `<header>` holding the `<h1>`, then a `<main>` holding everything else. Nothing else can pass until those two exist.",
                    "A list is a `<ul>` wrapped around three or more `<li>` elements — the text goes inside the items, never loose inside the `<ul>`.",
                    "The link needs both halves: an `href` that starts with `https://`, and words between the tags for someone to read and click.",
                    "Alt text stands in for the picture. Describe what it shows in a clause, in the voice of the page — not `photo`, and not the file name.",
                ],
                "tests": [
                    {"name": "The name is an h1 inside a header", "code": r'''
var _h1 = document.querySelector('header h1');
assert(_h1 !== null, 'Expected an <h1> inside a <header> — found ' + document.querySelectorAll('h1').length + ' <h1> and ' + document.querySelectorAll('header').length + ' <header> on the page');
assert(_h1.textContent.trim().length > 0, 'The <h1> is empty — put the person name in it');
assertEqual(document.querySelectorAll('h1').length, 1, 'A page has exactly one <h1>, found ' + document.querySelectorAll('h1').length);
'''},
                    {"name": "The content lives in a main landmark", "code": r'''
assertEqual(document.querySelectorAll('main').length, 1, 'Wrap the content in exactly one <main>, found ' + document.querySelectorAll('main').length);
assert(document.querySelector('main').textContent.trim().length > 0, 'The <main> is empty — the biography, the list and the link belong inside it');
'''},
                    {"name": "The image describes itself", "code": r'''
var _img = document.querySelector('img');
assert(_img !== null, 'The <img> has gone — keep it on the page');
var _alt = _img.getAttribute('alt');
assert(_alt !== null, 'The <img> has no alt attribute at all');
assert(_alt.trim().length >= 10, 'The alt text "' + _alt + '" is too short to describe what the picture shows');
'''},
                    {"name": "There is a biography paragraph", "code": r'''
var _ps = document.querySelectorAll('main p');
assert(_ps.length >= 1, 'Add a <p> with a short biography inside <main>, found ' + _ps.length + ' paragraph(s) there');
var _long = Array.prototype.filter.call(_ps, function (p) { return p.textContent.trim().length >= 20; });
assert(_long.length >= 1, 'The paragraph in <main> is a few characters long — write a sentence about the person');
'''},
                    {"name": "The skills are a real list", "code": r'''
var _ul = document.querySelector('ul');
assert(_ul !== null, 'No <ul> on the page — the skills belong in a list');
var _items = _ul.querySelectorAll(':scope > li');
assert(_items.length >= 3, 'Found ' + _items.length + ' <li> directly inside the <ul> — at least three are needed');
for (var _i = 0; _i < _items.length; _i++) {
  assert(_items[_i].textContent.trim() !== '', 'List item ' + (_i + 1) + ' is empty');
}
'''},
                    {"name": "The link goes somewhere and says so", "code": r'''
var _a = document.querySelector('a[href]');
assert(_a !== null, 'Needs an <a> with an href — an anchor without one is not a link');
var _href = _a.getAttribute('href');
assert(_href.indexOf('https://') === 0, 'The href should start with https://, got "' + _href + '"');
assert(_a.textContent.trim().length > 0, 'Give the link visible text — a link nobody can read is a link nobody can follow');
'''},
                ],
            }],
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
            "read": [
                {
                    "title": "Where the sideways scrollbar comes from",
                    "minutes": 12,
                    "body": r'''
Open this module's gallery on a 360-pixel-wide phone before any of the stylesheet has been
written and the page scrolls sideways. The header sits where it should, the heading is
fine, and then the six cards run off the right edge, each one wider than the screen.
Sideways scrolling is never a feature on a phone; it is a measurement that came out wrong,
and the useful question is not *how do I hide it* but *which pixels are these*. They can
be counted, and this reading counts them.

## Every box is four boxes

Every element the browser lays out is a content area wrapped in padding, wrapped in a
border, wrapped in margin. The question the box model answers is which of those `width`
refers to, and the default answer is the surprising one. Under `box-sizing: content-box` —
the initial value — `width: 200px` is the content alone, and padding and border are added
outside it. Give a card `padding: 16px` and `border: 1px solid` and it renders
$200 + 2 \times 16 + 2 \times 1 = 234$ pixels wide, while its stylesheet says 200.

Three of those cards in a row inside a 640-pixel container, with two 16-pixel gaps between
them, need $3 \times 234 + 2 \times 16 = 734$ pixels. The container has 640. The row
overflows by 94 pixels, and every one of them came from a declaration that looked correct.
Switch to `box-sizing: border-box` and the declared width becomes the width you can
measure with a ruler: padding and border eat into the content instead of pushing the edges
out, so the three cards need $3 \times 200 + 32 = 632$ pixels and fit. That is why
`* { box-sizing: border-box; }` sits near the top of every stylesheet in this course.
Margin sits outside the box under both rules; nothing puts it inside.

Two boxes with the same declared width, one rule apart:

```html
<style>
  body { font-family: system-ui, sans-serif; padding: 1rem; }
  .ruler { width: 200px; height: 6px; background: #1b1f27; margin-bottom: 4px; }
  .box { width: 200px; padding: 16px; border: 1px solid #1b1f27; margin-bottom: 1rem; background: #e8eef7; }
  .content-box { box-sizing: content-box; }
  .border-box { box-sizing: border-box; }
</style>

<div class="ruler"></div>
<div class="box content-box">content-box: width 200px, renders 234px</div>
<div class="box border-box">border-box: width 200px, renders 200px</div>
```

The black bar is 200 pixels. The first box overhangs it by 34; the second lines up with
it.

## One axis or two

The lab's header holds two children, a brand link and a list of links, and the design
wants the brand at the left edge and the list at the right. Ask how many axes are being
arranged along: one. The children follow each other in a row and size themselves to their
text. That is flexbox's whole model. `display: flex` on `.site-nav` makes the two children
flex items along a main axis, and `justify-content` says what to do with the space left
over once they have taken what they need. In a 960-pixel header where the brand measures
120 and the list 300, there are 540 pixels free. `space-between` puts every one of them
into the gap between the items and none on the outside, so the two children land on the
two edges. `center` would split the 540 into 270 on each side; `flex-start` would leave
all of it on the right.

The gallery is a different question. Six cards, in rows *and* columns that line up in
both directions: the third card and the sixth sit in the same column and their edges
agree. Two axes at once is what CSS grid exists for. `display: grid` on `#gallery` and
`grid-template-columns: repeat(3, 1fr)` declare three tracks, and the six `<li>` items
flow into them in order — three across, then the next row — with no arithmetic from you
and no clearing.

What `1fr` means can be derived rather than remembered. Call the container's content width
$W$, the gap between neighbouring tracks $g$, and the number of tracks $k$. The tracks
stand side by side with a gap in every join but none on the outside edges, so a full row
occupies $k\,t + (k-1)\,g$ for tracks of width $t$. A row that fills the container exactly
has that equal to $W$, so

$$t = \frac{W - (k - 1)\,g}{k}.$$

Take the gaps out first, then share what is left equally: that is `1fr`, one share of the
leftover space. With $W = 920$ (a 960-pixel viewport less 20 pixels of padding each side),
$g = 20$ and $k = 3$, each track is $(920 - 40)/3 = 293.3$ pixels. This module's
derivation exercise carries the same line one step further, to how many tracks
`auto-fill` can place before one drops below its minimum.

## The image that will not shrink

Now the pixels that were scrolling sideways. Each card holds an image that is 480 pixels
wide intrinsically, sitting in a track that the arithmetic says is 293 wide. A `1fr`
track has a floor: it is not allowed to be narrower than the minimum size of its
contents, and an image's minimum size is its own width. So the image wins, every track
grows to 480, and the row is $3 \times 480 + 40 = 1480$ pixels inside a 920-pixel
container. The document's `scrollWidth` is now larger than its `clientWidth`, which is the
exact test the lab runs last, and the difference is the scrollbar.

`max-width: 100%` on the image caps its rendered width at its container, the grid track.
That does two things: the image can no longer be wider than the track, and its claim on
the track's minimum goes away, so the track returns to its `1fr` share and the image
renders 293 pixels wide. `height: auto` then lets the image's own aspect ratio choose the
height — 480 by 320 is 3:2, so 293 wide comes out 195.6 tall — instead of squashing it
into whatever the box happened to be. `display: block` removes the small gap below an
inline image, which is the descender space the line box reserves for text that is not
there.

The whole calculation, at two viewport widths:

```js
function trackShare(W, gap, k) {
  return (W - (k - 1) * gap) / k;
}

function layout(viewport, padding, gap, columns, imageWidth, capped) {
  var W = viewport - 2 * padding;
  var share = trackShare(W, gap, columns);
  var image = capped ? Math.min(imageWidth, share) : imageWidth;
  var track = Math.max(share, image);
  var row = columns * track + (columns - 1) * gap;
  var verdict = row > W + 0.5 ? 'OVERFLOWS by ' + (row - W).toFixed(1) + 'px' : 'fits';
  console.log(viewport + 'px viewport, ' + columns + ' column(s), image ' +
    (capped ? 'capped' : 'uncapped') + ': track ' + track.toFixed(1) +
    'px, row ' + row.toFixed(1) + 'px of ' + W + 'px -> ' + verdict);
}

layout(960, 20, 20, 3, 480, false);
layout(960, 20, 20, 3, 480, true);
layout(360, 20, 20, 3, 480, true);
layout(360, 20, 20, 1, 480, true);
```

The first line is the starting page: tracks forced to 480, a 1480-pixel row, an overflow
of 560. The second is the same page with `max-width: 100%`: tracks of 293.3, the row
fits. The third is what the fix looks like on the phone — it fits, at 93 pixels per
column, which is a width no card can be read at. The fourth is the answer to that: one
column, 320 pixels wide, which is what the breakpoint is for.

## Mobile-first, and the direction a stylesheet reads

Ninety-three-pixel columns fit and are useless, so at some width the layout has to
change: the gallery to one column, the nav list stacked. A media query is the switch —
`@media (max-width: 640px) { ... }` — and the rules inside it apply only while the
viewport is at most 640 pixels wide. Where the block goes matters more than it looks. A
media query contributes nothing to specificity.
`.gallery { grid-template-columns: repeat(3, 1fr); }` and
`.gallery { grid-template-columns: 1fr; }` inside a media query select the same element
with the same weight, so the cascade falls through to document order and the later
declaration wins. Put the media query above the base rule and the phone gets three
columns; put it below and the override takes. So a stylesheet reads in one direction: the
base rules, then the breakpoints that amend them.

The lab adds one more line to the breakpoint, and it is the line that lets script and
stylesheet agree. On `:root` declare `--layout: wide;`, and inside the media query
re-declare `--layout: narrow;`. A custom property is an ordinary inherited property that
happens to hold a token, so every element on the page sees the current value, and
JavaScript can read it with
`getComputedStyle(document.documentElement).getPropertyValue('--layout')`. The condition
`640px` is now written in exactly one place; anything else that needs to know which
layout is showing asks the token. The lab's first check does precisely that, and compares
the answer with `matchMedia('(max-width: 640px)')`, so it holds at whatever width the page
happens to be showing.

## The mistake, and why it is tempting

The fix people reach for first is `body { overflow-x: hidden; }`. It is one line, the
scrollbar disappears, and it is tempting because the symptom was the scrollbar. But the
cards are still 1480 pixels wide. The right third of the third card is now clipped
instead of scrolled to, on a phone it is unreachable, and the layout bug is exactly where
it was with its only visible evidence removed. The lab's last check reads `scrollWidth`,
which reports the content's width whether or not it is clipped, so this fix does not pass
it, and that is deliberate. The close cousin is `width: 100vw`, which reads as *the full
width* and is the viewport's width including the vertical scrollbar, so on a desktop it is
reliably a few pixels wider than the space available and produces the overflow it was
meant to cure.

## Where this stops holding

The track floor that the image hit is not only an image's. Text has a minimum too — its
longest unbreakable word — and a card with a fifty-character URL in it will force its
track wider in the same way, with `max-width` powerless because there is no replaced
element to cap. The fix there is `min-width: 0` on the grid item, or
`overflow-wrap: anywhere` on the text, and it is the second thing to look for when
`scrollWidth` disagrees with `clientWidth`. Media queries measure the viewport, not the
container: a gallery placed in a 300-pixel sidebar on a 1400-pixel screen matches no
`max-width: 640px` rule and renders three columns of 87 pixels. Container queries answer
that, at the cost of a wrapper with `container-type` set. And the pixels in every number
above are CSS pixels, not device pixels — a phone with 1080 physical pixels across and a
device pixel ratio of 3 reports a 360-pixel viewport to both the media query and
`matchMedia`, which is why the two agree, and why `width=device-width` in the viewport
meta tag is not optional.

## In the lab

*A gallery that survives a 360px phone* gives you a read-only `index.html` — the header,
the nav list, six cards with 480-pixel images — and a `style.css` with six numbered
comments and nothing else. You write the flex row with `space-between`, the flex list
without bullets, the three-column grid with a gap, the capped block-level image, the
breakpoint that stacks the nav and collapses the grid, and the `--layout` token on both
sides of it. Seven checks read the computed styles back at whatever width the page is
showing, and the last of them is the one this reading opened with: `scrollWidth` no larger
than `clientWidth`.
''',
                },
                {
                    "title": "Which rule wins",
                    "minutes": 11,
                    "body": r'''
You write `.card h2 { color: teal; }`, reload, and the heading is still black. Open the
inspector, click the heading, and your declaration is there in the Styles panel with a
line through it. Nothing is broken. Two rules matched the same element, they disagreed,
and the browser resolved the disagreement by a procedure — one you can run on paper
before you reload. This reading is that procedure, and the three other things a
stylesheet does that are not layout: inherit, measure, and name.

## A rule, and what connects it

```html
<link rel="stylesheet" href="style.css">
```

That line in the `<head>` is what pairs a stylesheet with a document. The stylesheet
itself is a list of **rules**, and each rule is a *selector* saying which elements it is
about, followed by a block of *declarations* — property, colon, value, semicolon.

```css
h1 {
  color: #1b1f2a;
  font-size: 2rem;
}
```

The selectors worth knowing at the start are few:

| Selector | Matches |
|---|---|
| `p` | every `<p>` — a **type** selector |
| `.card` | anything whose `class` list contains `card` |
| `#main-nav` | the one element with `id="main-nav"` |
| `.card h2` | an `<h2>` anywhere inside `.card` — a **descendant** |
| `.card > h2` | an `<h2>` that is a direct child of `.card` |
| `a:hover` | a link while the pointer is over it |
| `input[type="email"]` | by attribute |
| `.card, .panel` | either, as two independent selectors |

That last row is worth pausing on. A comma does not create one selector matching both; it
duplicates the whole rule, and each half is weighed separately when the disagreement is
resolved.

## Specificity is three numbers

When two rules set the same property on the same element, the browser scores each
selector as a triple — write it `(a, b, c)`:

- **a** — how many `#id` selectors it contains
- **b** — how many classes, attribute selectors and pseudo-classes (`.note`,
  `[type="email"]`, `:hover`)
- **c** — how many element types and pseudo-elements (`p`, `h2`, `::before`)

Compare the triples left to right, and the first column that differs decides it. A single
id beats any number of classes, because column *a* is read before column *b* ever is:
`(1, 0, 0)` beats `(0, 9, 0)`. Only when two triples are identical does the tiebreak
happen, and the tiebreak is document order — the rule written **later** wins.

Five rules against three paragraphs, with the answers read back off the live page:

```js
var css = [
  'p { color: rgb(20, 20, 20); }',          /* (0, 0, 1) */
  'article p { color: rgb(0, 0, 200); }',   /* (0, 0, 2) */
  '.note { color: rgb(0, 120, 0); }',       /* (0, 1, 0) */
  '.note { color: rgb(120, 0, 120); }',     /* (0, 1, 0), written later */
  '#lead { color: rgb(200, 0, 0); }'        /* (1, 0, 0) */
].join('\n');

var sheet = document.createElement('style');
sheet.textContent = css;
document.head.appendChild(sheet);

var article = document.createElement('article');
[['one', 'lead', 'note'], ['two', '', 'note'], ['three', '', '']].forEach(function (row) {
  var p = document.createElement('p');
  p.textContent = row[0];
  if (row[1]) { p.id = row[1]; }
  if (row[2]) { p.className = row[2]; }
  article.appendChild(p);
});
document.body.appendChild(article);

article.querySelectorAll('p').forEach(function (p) {
  console.log(p.textContent + ' -> ' + getComputedStyle(p).color);
});
```

*one* comes out `rgb(200, 0, 0)`: four rules match it and `#lead` at `(1, 0, 0)` is ahead
of every one of them on the first column. *two* comes out `rgb(120, 0, 120)`: the two
`.note` rules at `(0, 1, 0)` both beat `article p` at `(0, 0, 2)` — a class outranks any
pile of element names — and between the two identical triples the later one takes it.
*three* comes out `rgb(0, 0, 200)`, because `article p` at `(0, 0, 2)` beats bare `p` at
`(0, 0, 1)`. The heading at the top of this reading was the second case: `.card h2` is
`(0, 1, 1)`, and whatever was painting it black had a class more.

## Inheritance is a different mechanism

A rule that matches nothing can still change an element, because some properties pass
down the tree on their own. `color`, `font-family`, `font-size`, `line-height`,
`text-align` and `visibility` inherit; `margin`, `padding`, `border`, `background`,
`width` and `display` do not. That is why setting `font-family` once on `body` styles the
whole page and setting `border` on `body` draws exactly one box.

Inheritance loses to any rule that matches. An inherited value is what an element gets
when nothing said otherwise, so a browser default such as `a { color: -webkit-link }`
beats the `color` inherited from a parent — which is why links keep their blue inside a
paragraph you have coloured, and why `a { color: inherit; }` is the line that fixes it.

## Units, and which to use where

`px` is an absolute length and ignores everything about the reader. `rem` is a multiple
of the root font size, so text set in `rem` grows when someone raises their browser's
default from 16px — a setting people who need it do use, and `px` silently overrides.
`em` is a multiple of the *element's own* font size, which makes it good for padding that
should scale with its text and treacherous when nested, because two levels of
`font-size: 0.9em` compound to 0.81. `%` is relative to the parent's corresponding
length. Text and spacing in `rem`, hairlines and radii in `px`, is a defensible default.

Colour has four common spellings for the same thing: a keyword (`tomato`), hex
(`#f26a1b`), `rgb(242 106 27)`, and `rgb(242 106 27 / 10%)` when part of what you want is
transparency. Nothing distinguishes them but readability.

## Custom properties are inherited properties

```css
:root { --accent: #f26a1b; }
button { background: var(--accent); }
```

`--accent` is not a compile-time constant. It is an ordinary CSS property that inherits,
declared here on `:root` — the `<html>` element — so every descendant computes the same
value and `var(--accent)` resolves against whatever the element itself inherited. Two
consequences fall out. Re-declaring it lower down changes it for that subtree only, which
is how a `.panel--warning` recolours everything inside it with one line. And re-declaring
it inside a media query changes it for the whole page at one width, which is how the
module's lab publishes `--layout` for JavaScript to read. `var(--gap, 1rem)` supplies a
fallback for the case where the property was never declared at all.

## The mistake, and why it is tempting

The heading is still black, so you write `color: teal !important;` and move on. It works,
and it has cost more than it looks. `!important` is not a bigger number in the same
comparison — it moves the declaration into a separate round that is resolved before the
ordinary one, so nothing you write later at any specificity can override it without being
`!important` too. The next person needing a different colour has one move available, and
from then on the file is a ladder of exclamation marks with the real precedence buried
under it.

The cousin is winning by inflation: adding `#page` to the front of the selector to
outscore whatever beat you. It works once, and it raises the floor for every rule after
it. Both are the same misreading — treating a lost comparison as something to beat rather
than something to look at. The comparison told you which rule won and why. Usually the
answer is to lower the winner rather than raise the loser: replace `article p` with a
class, or move your rule below its equal.

## Where this stops holding

The triple is not the whole order. An inline `style="…"` attribute outranks every
selector; `!important` declarations are resolved in their own pass, and there they run
from the *bottom* of the priority list upwards, so a reader's `!important` in a user
stylesheet beats yours. `:where(...)` contributes zero to the triple no matter what is
inside it, which is how a design system ships defaults that are trivial to override, and
`:is(...)` contributes its most specific argument, so `:is(#a, p)` scores `(1, 0, 0)`
even when it matched the `p`. Cascade layers reorder the whole thing again, and are
resolved before specificity is consulted at all.

And `getComputedStyle` does not report what you wrote. It reports the resolved value:
`font-size: 2rem` reads back as `32px`, `color: teal` as `rgb(0, 128, 128)`, and a `width`
in `%` as the pixels it currently occupies. Every check in this module's labs is written
against those resolved strings, which is why they compare `'rgb(0, 0, 0)'` rather than
`'black'`.

## In the lab

*A card with shape* gives you the finished markup — an `<article class="card">` holding
an avatar, a heading, two paragraphs and a `<ul class="skills">` of `.tag` items — and a
stylesheet with the reset and the page background already written. You add the rules: a
rounded, padded, shadowed white card; the skills list as a flex row with a gap and no
bullets; padded, rounded tags; and a heading in something other than the default black.
Five checks read the computed styles back off the live page.
''',
                },
            ],
            "quiz": [{
                "title": "Boxes, axes and the cascade",
                "minutes": 7,
                "questions": [
                    {
                        "q": "With `box-sizing: border-box`, what does `width: 200px` on a padded, bordered element describe?",
                        "opts": [
                            "The content alone — padding and border are added outside it",
                            "Content plus padding plus border, together",
                            "Content plus padding plus border plus margin",
                            "The width the element would have with no padding or border at all",
                        ],
                        "a": 1,
                        "why": r"""
`border-box` makes the declared width the width you can measure with a ruler: whatever
padding and border you add eat into the content instead of pushing the box wider. Under
the default `content-box`, the same element with `1rem` of padding and a `1px` border
takes 200 + 32 + 2 = 234px, which is how a three-column grid of "200px" cards ends up
overflowing a 640px container. Margin is outside the box under either rule — no value of
`box-sizing` includes it.
""",
                    },
                    {
                        "q": "A row of navigation links of differing widths needs to sit in a line with an even gap. Which is the smaller tool?",
                        "opts": [
                            "CSS grid, because a navbar is a layout",
                            "Flexbox — one axis, and the items size themselves to their text",
                            "Floats, which is what they were designed for",
                            "Absolute positioning, so the links cannot move",
                        ],
                        "a": 1,
                        "why": r"""
The question to ask is *how many axes am I arranging on*. A nav list is one row: items
follow each other along the main axis and size themselves to their content, which is
flexbox's whole model. Grid is the right answer when you are placing things into rows
*and* columns that line up across both — the gallery below is exactly that. Floats
predate both and need clearing hacks to contain anything, and absolute positioning takes
the links out of flow entirely, so the header collapses to nothing behind them.
""",
                    },
                    {
                        "q": "`@media (max-width: 640px) { .gallery { grid-template-columns: 1fr; } }` is written *above* the plain `.gallery { grid-template-columns: repeat(3, 1fr); }`. What renders on a 400px screen?",
                        "opts": [
                            "Three columns — equal specificity, so the later rule wins",
                            "One column — a media query outranks an unconditional rule",
                            "One column — the narrower the matching context, the higher the priority",
                            "Neither rule applies, and the grid falls back to one implicit column",
                        ],
                        "a": 0,
                        "why": r"""
A media query contributes nothing to specificity. Both rules select `.gallery` — one
class each, identical weight — so the cascade falls through to document order and the
last declaration wins, media query or not. The override renders three columns on a
phone, and the fix is to move it below rather than to reach for `!important`. This is
also the reason a stylesheet reads in one direction: base rules first, then the
breakpoints that amend them.
""",
                    },
                    {
                        "q": "A 480px-wide `<img>` sits in a 300px grid track and pushes the page sideways. Which declaration makes it fit and keeps its shape?",
                        "opts": [
                            "`max-width: 100%; height: auto;`",
                            "`width: 100%; height: 100%;`",
                            "`overflow: hidden;` on the card around it",
                            "`max-height: 100%;`",
                        ],
                        "a": 0,
                        "why": r"""
`max-width: 100%` caps the rendered width at the containing block, and `height: auto`
then lets the intrinsic aspect ratio choose the height, so the picture shrinks rather
than squashes. Setting both `width` and `height` to 100% stretches the image to whatever
shape the box happens to be. `overflow: hidden` crops the part that does not fit instead
of fitting it — the page stops scrolling and you have silently thrown away a third of the
photo. And `max-height` constrains the axis that is not overflowing.
""",
                    },
                    {
                        "q": "`--layout` is declared once on `:root`. Why can `.card` read it without it being repeated?",
                        "opts": [
                            "Custom properties inherit, so every descendant sees the value unless something nearer overrides it",
                            "`:root` has higher specificity than any other selector",
                            "Custom properties are global variables and sit outside the cascade",
                            "`var()` searches the whole stylesheet for a matching declaration",
                        ],
                        "a": 0,
                        "why": r"""
A custom property is an ordinary inherited CSS property that happens to hold a token
instead of a length. `var(--layout)` resolves against the element's own computed value,
which it inherited from its parent, and so on up to `:root`. That is why re-declaring
`--layout` on `:root` inside a media query changes it for the entire page at once, and
why re-declaring it on `.card` would change it only inside cards and their descendants.
`:root` is just `html` with one extra point of specificity; nothing about it is special
here beyond being the common ancestor.
""",
                    },
                ],
            }, {
                "title": "Selectors, inheritance and units",
                "minutes": 6,
                "questions": [
                    {
                        "q": "Which selector matches every element carrying `class=\"card\"`?",
                        "opts": [
                            "`.card`",
                            "`#card`",
                            "`card`",
                            "`*[card]`",
                        ],
                        "a": 0,
                        "why": r"""
A leading dot means a class, a leading hash means an id, and a bare name means an element
type. `#card` matches the one element with `id="card"` and nothing else, which is a
different element or none at all. `card` is a type selector for a `<card>` element, and
since no such element exists it matches nothing — quietly, because an unmatched selector
is not an error. `*[card]` is an attribute selector: it would match `<div card>`, not
`<div class="card">`, because the attribute here is called `class` and `card` is one word
of its value.
""",
                    },
                    {
                        "q": "A `.card` has a background colour, 16px of padding and 24px of margin. How far out does the background paint?",
                        "opts": [
                            "To the border's outer edge — under the padding, but not under the margin",
                            "To the content's edge, so neither the padding band nor the margin takes the colour",
                            "To the margin's outer edge, since margin is part of the element's box",
                            "As far as `background-clip` says, and it has no initial value to fall back on",
                        ],
                        "a": 0,
                        "why": r"""
Padding is inside the border and margin is outside it, and the background fills
everything up to and including the border box. That is the practical difference between
the two, and the reason a card with a background gets breathing room from `padding` and
separation from its neighbours with `margin` — swap them and the text touches a coloured
edge while a coloured gap sits between the cards. Two more consequences follow from the
same picture: adjacent vertical margins collapse into one and padding never does, and a
click landing in the padding hits the element while a click in the margin does not.
`background-clip` can move that edge, but its initial value is `border-box`, which is the
behaviour described here.
""",
                    },
                    {
                        "q": "`#page p { color: red }` and `.intro { color: blue }` both match one paragraph. Which colour renders?",
                        "opts": [
                            "Red — an id in the selector outranks a class, whatever else is in either",
                            "Blue — the later rule wins whenever two rules disagree about a property",
                            "Blue — `.intro` names the element more precisely than a descendant chain",
                            "Red — the selector with more parts wins, and `#page p` has two of them",
                        ],
                        "a": 0,
                        "why": r"""
Specificity is three numbers compared left to right: ids, then classes, then element
types. `#page p` scores `(1, 0, 1)` and `.intro` scores `(0, 1, 0)`, and the first column
settles it before the second is looked at — one id beats any number of classes. Document
order is real but it is the *tiebreak*, reached only when the triples are identical, so
writing `.intro` last changes nothing here. Counting parts is the other tempting rule and
it is not the rule: `article section div p` has four parts, scores `(0, 0, 4)`, and still
loses to a single class.
""",
                    },
                    {
                        "q": "`body { font-family: system-ui; border: 1px solid; }` — what do the elements inside `body` get?",
                        "opts": [
                            "The font, because `font-family` inherits; the border stops at `body`",
                            "Both, since any property set on an ancestor cascades down to its descendants",
                            "Neither — `body` is not an ancestor for the purposes of inheritance",
                            "The border, because box properties inherit while text properties are resolved per element",
                        ],
                        "a": 0,
                        "why": r"""
Inheritance is a property-by-property fact, not a general one. Text properties —
`color`, `font-family`, `font-size`, `line-height`, `text-align` — pass down the tree,
which is why one declaration on `body` sets the typeface for the whole page. Box
properties — `border`, `padding`, `margin`, `background`, `width`, `display` — do not,
which is why the same rule draws exactly one rectangle and not one around every element
on the page. The cascade and inheritance get conflated because both travel downwards in
the file; the cascade decides which matching rule wins, and inheritance supplies a value
when no rule matched at all.
""",
                    },
                    {
                        "q": "`@media (max-width: 640px) { … }` — when do the rules inside apply?",
                        "opts": [
                            "While the viewport is 640 CSS pixels wide or narrower, whatever the element",
                            "While the viewport is wider than 640 pixels, the number being a floor and not a ceiling",
                            "Never on a phone, because a phone reports its physical pixel count",
                            "Whenever the element being styled has been measured at 640px or less",
                        ],
                        "a": 0,
                        "why": r"""
`max-width` is a ceiling on the viewport: at 640 and below the block applies, above it
the block is inert. Reading it as a floor is the error that produces a stylesheet whose
two layouts are the wrong way round, and it survives review because both versions render
something. The phone answer is worth taking seriously and is wrong for a specific reason:
a device with 1080 physical pixels across and a device pixel ratio of 3 reports a
360-pixel viewport to the media query, which is what `<meta name="viewport"
content="width=device-width">` arranges, and what makes the numbers in a breakpoint mean
anything. And the condition measures the viewport, never the element — a gallery in a
300-pixel sidebar on a wide screen matches no `max-width: 640px` rule at all, which is
the gap container queries exist to fill.
""",
                    },
                    {
                        "q": "Which length grows when the reader raises their browser's default font size?",
                        "opts": [
                            "`rem`, which is a multiple of the root font size",
                            "`px`, which the browser scales along with the text",
                            "`vh`, which tracks the viewport rather than the type",
                            "`cm`, which is anchored to the physical display",
                        ],
                        "a": 0,
                        "why": r"""
`1rem` is whatever the root element's font size currently is, so raising the default from
16px to 20px widens every `rem` on the page by a quarter — text, padding and gaps
together. `px` is the one that does not move: a CSS pixel is an absolute length, and
sizing body text in `px` overrides a preference the reader deliberately set, which is the
whole argument for `rem`. `vh` is one hundredth of the viewport height and answers to the
window, not the reader. `cm` sounds physical and is not measured on any ruler either — it
is pinned to 96 CSS pixels per inch regardless of the actual display.
""",
                    },
                ],
            }],
            "blanks": {
                "title": "One stylesheet, two widths",
                "minutes": 9,
                "caption": "style.css — six holes",
                "lang": "css",
                "brief": r'''
The gallery stylesheet, with the load-bearing declarations removed. Every hole is a
place where the wrong value still produces a page that looks plausible on the machine
you wrote it on and falls apart on a phone.
''',
                "listing": r''':root {
  --layout: wide;
  --gap: 1.25rem;
}

* { box-sizing: border-box; }

.site-nav {
  display: ___;
  justify-content: ___;
}

.nav-list {
  display: flex;
  gap: var(--gap);
  list-style: none;
  margin: 0;
  padding: 0;
}

.gallery {
  display: ___;
  grid-template-columns: ___;
  gap: var(--gap);
  list-style: none;
}

.card-img {
  display: block;
  max-width: ___;
  height: auto;
}

@media (max-width: 640px) {
  :root { --layout: ___; }
  .nav-list { flex-direction: column; }
  .gallery { grid-template-columns: 1fr; }
}
''',
                "blanks": [
                    {
                        "prompt": "The navbar holds two children in a line. What kind of container is it?",
                        "hole": "value",
                        "opts": ["flex", "block", "inline", "table-row"],
                        "a": 0,
                        "why": "`display: flex` makes the two children flex items on one axis, which is the whole of what a navbar needs.",
                        "whys": [
                            "`display: flex` makes the two children flex items on one axis, which is the whole of what a navbar needs — and it is what gives `justify-content` anything to do.",
                            "`block` is what it already is. The brand and the list would stack, and `justify-content` on the line below would be ignored entirely, because block layout has no main axis to distribute along.",
                            "`inline` makes the header itself inline-level, so it stops being a full-width band and shrinks to its contents. The children are unaffected.",
                            "`table-row` borrows table layout for something that is not a table: the children have to be table cells, sizing is content-driven and unpredictable, and `gap` behaves differently. It was the 2005 workaround and there is no reason to reach for it now.",
                        ],
                    },
                    {
                        "prompt": "Brand at one end, links at the other, all the slack in the middle.",
                        "hole": "value",
                        "opts": ["center", "space-around", "space-between", "flex-start"],
                        "a": 2,
                        "why": "`space-between` puts every pixel of free space into the gaps *between* items and none on the outside, so the two children land on the two edges.",
                        "whys": [
                            "`center` collects both children in the middle with the free space split to the outsides — a perfectly good navbar, just not this one.",
                            "`space-around` gives each item an equal share of space on both sides, so the outer margins come out half the size of the middle one and the brand sits a little way in from the edge rather than on it.",
                            "`space-between` puts every pixel of free space into the gaps *between* items and none on the outside, so with two children they land on the two edges. Add a third child later and it goes exactly halfway between them.",
                            "`flex-start` packs both children against the start edge, which is what a plain flex row does anyway. The links end up glued to the brand.",
                        ],
                    },
                    {
                        "prompt": "The gallery lays cards out in rows and columns that line up in both directions.",
                        "hole": "value",
                        "opts": ["table", "grid", "flex", "block"],
                        "a": 1,
                        "why": "Two axes at once is grid's reason to exist: you declare the tracks, and items flow into them in order.",
                        "whys": [
                            "A `table` display would line the columns up, and would also drag in table sizing rules, demand rows and cells, and refuse to wrap onto a new line — which is precisely what a gallery has to do.",
                            "Two axes at once is grid's reason to exist: you declare the tracks, and items flow into them in order. Card three and card six sit in the same column with no arithmetic from you.",
                            "`flex` with `flex-wrap: wrap` gets close, and is what people reach for first. The difference shows on the last row: flex items size themselves, so four cards wrapping into 3 + 1 leave the lone card stretched or stranded, where grid keeps every track the same width.",
                            "`block` stacks the list items vertically, one per line. That is the correct *narrow* layout, but it is what the breakpoint is for.",
                        ],
                    },
                    {
                        "prompt": "Three equal columns, whatever is inside them.",
                        "hole": "tracks",
                        "opts": ["repeat(3, 1fr)", "repeat(3, auto)", "1fr", "3fr"],
                        "a": 0,
                        "why": "`1fr` means *one share of the leftover space*, so three of them split the row into three identical tracks regardless of the content.",
                        "whys": [
                            "`1fr` means *one share of the leftover space*, so three of them split the row into three identical tracks regardless of what the cards contain. `repeat(3, ...)` is shorthand for writing it out three times.",
                            "`repeat(3, auto)` does give three tracks, but `auto` sizes each one to its content — the card with the longest title gets the widest column, and the row looks accidentally ragged.",
                            "A single `1fr` declares one column. The other cards land in implicitly created rows underneath, which renders as a single stacked column.",
                            "`3fr` is still one track. The `fr` value is a proportion, not a count: with only one track it takes all the free space, and three shares of everything is everything.",
                        ],
                    },
                    {
                        "prompt": "The images are 480px wide intrinsically and the tracks are narrower than that.",
                        "hole": "value",
                        "opts": ["480px", "none", "100vw", "100%"],
                        "a": 3,
                        "why": "`max-width: 100%` caps the image at the width of its containing block — the grid track — so it shrinks with the column instead of bursting out of it.",
                        "whys": [
                            "Pinning the image to its intrinsic 480px is the bug, written down. The track is 300px, the image is 480px, and the difference is the sideways scrollbar.",
                            "`none` is the initial value, which is to say no cap at all. This is what the page does before you touch it.",
                            "`100vw` is one hundred percent of the *viewport*, not of the track. Inside a padded container it is reliably wider than the space available, which makes it a common and confusing source of overflow in its own right.",
                            "`max-width: 100%` caps the image at the width of its containing block — the grid track — so it shrinks with the column instead of bursting out of it. Paired with `height: auto` the aspect ratio survives.",
                        ],
                    },
                    {
                        "prompt": "The token JavaScript reads to find out which layout is showing.",
                        "hole": "token",
                        "opts": ["narrow", "wide", "640px", "column"],
                        "a": 0,
                        "why": "Inside the breakpoint the token has to change, or reading it back tells you nothing you did not already know.",
                        "whys": [
                            "Inside the breakpoint the token has to change, or reading it back tells you nothing you did not already know. `wide` on `:root` and `narrow` here means one declaration is the single answer to *which layout am I in*, and the media query condition lives in exactly one place.",
                            "Re-declaring the same value is a no-op with a comment's worth of intent. The check reads `--layout` back and compares it against `matchMedia`, so it would report `wide` on a 400px screen.",
                            "The token is a name for the layout, not a copy of the condition. Putting `640px` in it means every reader has to know which side of the comparison they are on, which is the thing the token existed to hide.",
                            "`column` describes what the nav list does at this width, not what the page's layout is called. The gallery is not a column of anything — it is a single-column grid — so the name would mislead the moment a second component read it.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "How many columns does auto-fill place?",
                "minutes": 12,
                "vars": ["W", "t", "g", "k", "m"],
                "brief": r'''
`grid-template-columns: repeat(auto-fill, minmax(220px, 1fr))` is the responsive
gallery in one declaration: no breakpoint, no media query, the browser works out the
column count itself on every resize. What it is working out is one line of algebra.

Let the container's content width be $W$, the gap between neighbouring tracks be $g$,
the number of tracks be $k$, each of width $t$, and let $m$ be the smallest width a
track is allowed to have.
''',
                "steps": [
                    {
                        "prompt": "Write the total width a row of $k$ tracks occupies, in terms of $k$, $t$ and $g$.",
                        "answer": "k t + (k - 1) g",
                        "hint": "Fence posts. The tracks stand side by side and a gap sits in each join — but not on the outside edges.",
                        "deconstruct": [
                            "The tracks themselves contribute $k$ lots of $t$.",
                            "A gap sits between neighbours only, so there are $k - 1$ of them.",
                        ],
                    },
                    {
                        "prompt": "The row fills the container exactly. Solve for the track width $t$.",
                        "given": "$k t + (k - 1) g = W$",
                        "answer": "\\frac{W - (k - 1) g}{k}",
                        "placeholder": "\\frac{?}{k}",
                        "hint": "Take the gaps out of $W$ first. Whatever is left is shared equally between the $k$ tracks.",
                        "deconstruct": [
                            "Move the gaps across: $k t = W - (k - 1) g$.",
                            "Divide both sides by $k$.",
                        ],
                    },
                    {
                        "prompt": "`minmax(m, 1fr)` forbids a track narrower than $m$. Find the value of $k$ at which $t$ is exactly $m$ — the point where one more column stops fitting.",
                        "given": "Put $t = m$ into $k t + (k - 1) g = W$ and solve for $k$.",
                        "answer": "\\frac{W + g}{m + g}",
                        "hint": "Expand the bracket, then collect the two terms that carry $k$.",
                        "deconstruct": [
                            "$k m + (k - 1) g = W$ expands to $k m + k g - g = W$.",
                            "Collect: $k(m + g) = W + g$.",
                            "Divide by $m + g$.",
                        ],
                    },
                    {
                        "prompt": "A 960px content box, a 16px gap, and `minmax(220px, 1fr)`. How many whole columns does `auto-fill` place?",
                        "given": "$W = 960$, $g = 16$, $m = 220$. Round down — a partial column is no column.",
                        "answer": "4",
                        "hint": "Substitute into the expression you just derived, then take the floor of it.",
                        "deconstruct": [
                            "$(960 + 16)/(220 + 16) = 976/236 \\approx 4.14$.",
                            "Four whole tracks fit; a fifth would force every track below the 220px floor.",
                        ],
                    },
                    {
                        "prompt": "Those four tracks share the row. How wide is each one, in pixels?",
                        "given": "$W = 960$, $g = 16$, $k = 4$.",
                        "answer": "228",
                        "hint": "Four tracks have three gaps between them. Take those out of $W$ before dividing.",
                        "deconstruct": [
                            "Gaps: $3 \\times 16 = 48$px.",
                            "$(960 - 48)/4 = 912/4$.",
                        ],
                    },
                ],
                "closing": r'''
That is the whole of `repeat(auto-fill, minmax(220px, 1fr))`, and the browser redoes it
on every resize. Notice what the `1fr` half is for: four tracks at the 220px minimum
plus 48px of gaps comes to 928px, so 32px of the row would be left empty on the right.
`1fr` hands that slack back out — eight pixels each — and every track lands on 228.
Swap `auto-fill` for `auto-fit` and the empty tracks collapse instead, which is the same
arithmetic with the leftovers spent differently.
''',
            },
            "lab": [{
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
            }, {
                "title": "A card with shape",
                "runtime": "web",
                "minutes": 18,
                "brief": r'''
`index.html` is finished and read-only: an `<article class="card">` holding an
avatar, a heading, a role line, a paragraph and a `<ul class="skills">` of three
`.tag` items. `style.css` has the reset and the page background and nothing else.

Write the rules that give the card a shape:

- `.card` — a `border-radius`, at least **12px** of padding, a visible
  `box-shadow`, and a background colour of its own so it lifts off the grey page
- `.skills` — a flex row with a `gap` between the tags, and no bullets
- `.tag` — horizontal padding and rounded corners, so each one reads as a pill
- `h1` — any colour other than the default black

Five checks read the computed styles back off the live page, so what they see is
what the browser resolved, not what you typed: `border-radius: 16px` reads back
as `16px`, and a colour reads back as `rgb(...)` whatever notation you wrote it
in. Press Run and switch to Preview to watch it take shape.
''',
                "files": [
                    {"name": "index.html", "ro": True, "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Card</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<article class="card">
  <img class="avatar" width="96" height="96" alt="Portrait of Grace Hopper in naval uniform" src="data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='96' height='96'%3E%3Crect width='96' height='96' fill='%23d9e2ec'/%3E%3C/svg%3E">
  <h1>Grace Hopper</h1>
  <p class="role">Rear admiral, compiler pioneer</p>
  <p>Believed that code should read like the language people already speak, and
  invented the compiler to prove it.</p>
  <ul class="skills">
    <li class="tag">COBOL</li>
    <li class="tag">Compilers</li>
    <li class="tag">Leadership</li>
  </ul>
</article>

</body>
</html>
'''},
                    {"name": "style.css", "content": r'''
* { box-sizing: border-box; }

body {
  margin: 0;
  padding: 24px;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  background: #f0f2f5;
}

/* 1. .card    — radius, padding (12px or more), box-shadow, its own background
   2. .skills  — flex row, a gap, no bullets and no list padding
   3. .tag     — horizontal padding and a radius
   4. h1       — a colour that is not the default black */
'''},
                ],
                "main": "index.html",
                "solution": [
                    {"name": "style.css", "content": r'''
* { box-sizing: border-box; }

body {
  margin: 0;
  padding: 24px;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  background: #f0f2f5;
}

.card {
  max-width: 26rem;
  margin: 0 auto;
  padding: 1.5rem;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}

.avatar { display: block; border-radius: 50%; }

h1 {
  margin: 0.75rem 0 0.25rem;
  color: #c9530e;
  font-size: 1.6rem;
}

.role { color: #5a6270; margin-top: 0; }

.skills {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  list-style: none;
  margin: 1rem 0 0;
  padding: 0;
}

.tag {
  padding: 0.25rem 0.65rem;
  border-radius: 999px;
  background: #ffeadf;
  color: #8a2f00;
  font-size: 0.85rem;
}
'''},
                ],
                "hints": [
                    "One rule per requirement. `.card { border-radius: 16px; padding: 1.5rem; background: #fff; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08); }` covers the first four checks between them.",
                    "A `<ul>` arrives with bullets and a large left padding, and neither goes away on its own: `list-style: none; padding: 0;` before `display: flex; gap: 0.5rem;`.",
                    "A pill is padding plus a radius larger than the element is tall — `border-radius: 999px` is the usual way to say *as round as it can be* without measuring.",
                    "The check compares against `rgb(0, 0, 0)`, because that is what the browser resolves the default `color` to. Any other colour passes.",
                ],
                "tests": [
                    {"name": "The card has a shape of its own", "code": r'''
var _card = document.querySelector('.card');
assert(_card !== null, 'No .card element — index.html is read-only, so it should still be there');
var _cs = getComputedStyle(_card);
assert(parseFloat(_cs.borderTopLeftRadius) > 0, 'Give .card a border-radius, got ' + _cs.borderTopLeftRadius);
assert(parseFloat(_cs.paddingTop) >= 12, '.card needs at least 12px of padding, got padding-top: ' + _cs.paddingTop);
assert(parseFloat(_cs.paddingLeft) >= 12, '.card needs padding on the sides too, got padding-left: ' + _cs.paddingLeft);
'''},
                    {"name": "The card lifts off the page", "code": r'''
var _cs = getComputedStyle(document.querySelector('.card'));
assert(_cs.boxShadow && _cs.boxShadow !== 'none', 'Add a box-shadow to .card so it sits above the grey background');
var _bg = _cs.backgroundColor;
assert(_bg !== 'rgba(0, 0, 0, 0)' && _bg !== 'transparent', 'Give .card its own background colour — without one the page grey shows straight through');
'''},
                    {"name": "The skills flow as a flex row", "code": r'''
var _s = getComputedStyle(document.querySelector('.skills'));
assertEqual(_s.display, 'flex', '.skills should be display: flex, got ' + _s.display);
assert(parseFloat(_s.columnGap) > 0, 'Add a gap between the tags, got column-gap: ' + _s.columnGap);
assertEqual(_s.listStyleType, 'none', 'Drop the bullets from .skills, got list-style-type: ' + _s.listStyleType);
assert(parseFloat(_s.paddingLeft) < 8, 'A <ul> starts with a large left padding for its bullets — with the bullets gone, set padding: 0. Got padding-left: ' + _s.paddingLeft);
'''},
                    {"name": "The tags read as pills", "code": r'''
var _tags = document.querySelectorAll('.tag');
assertEqual(_tags.length, 3, 'Expected the three .tag items from index.html, found ' + _tags.length);
var _t = getComputedStyle(_tags[0]);
assert(parseFloat(_t.paddingLeft) > 0, 'Each .tag needs horizontal padding, got padding-left: ' + _t.paddingLeft);
assert(parseFloat(_t.borderTopLeftRadius) > 0, 'Round the .tag corners, got ' + _t.borderTopLeftRadius);
var _r0 = _tags[0].getBoundingClientRect();
var _r1 = _tags[1].getBoundingClientRect();
assert(Math.abs(_r0.top - _r1.top) < 2, 'The tags should sit on one row while there is space for them, not stack');
'''},
                    {"name": "The heading carries a colour", "code": r'''
var _c = getComputedStyle(document.querySelector('h1')).color;
assert(_c !== 'rgb(0, 0, 0)', 'Move the h1 away from the default black — it reads back as ' + _c);
'''},
                ],
            }],
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
            "read": [
                {
                    "title": "Two copies of the truth",
                    "minutes": 14,
                    "body": r'''
Here is this module's reading list, built the way most people build their first one.
Three books are on the page. The reader clicks *Done* on *Eloquent JavaScript*, and the
handler bound to that button does the natural thing: it adds the class `done` to the row,
and the title gets its strike-through. Then they click the `css` filter. That handler
rebuilds the list from the array, because only the array knows which book carries which
tag, and *Eloquent JavaScript* disappears, as it should. Click *All* and it is back —
without the strike-through. Nothing threw; the console is empty. The array never heard
about the first click: that handler changed the page and not the data, and when the page
was redrawn from the data, the change was gone.

The bug has a shape worth naming before any code. There were two descriptions of which
books were done — the `done` field of each item in `state.items`, and the class attribute
of each row — and two different pieces of code were allowed to write to them. Two copies
of one fact, kept up to date by hand, disagree the first time one path forgets the other,
and a page like this has a dozen paths: add, remove, toggle, filter, reload. The fix is
not to be more careful on each path. It is to stop having two copies.

## One array, and everything drawn from it

Say the array is the truth. Then the DOM is not a second copy of it but a picture of it,
and a picture is redrawn rather than edited. Every change goes into the array, and after
every change one function, `render()`, throws the old rows away and builds new ones from
what the array now says. The rows cannot disagree with the array, because nothing writes
to a row except the one function that reads the array.

The lab's whole architecture can be read off that sentence. There is one `state` object,
`{ items: [], filter: 'all', nextId: 1 }`, and every function that changes anything
changes `state` and then calls `render()`; none of them touches a row. Here is that loop
with the opening's clicks replayed against it, on a list never put on the page because
the console shows enough:

```js
var state = { items: [], filter: 'all', nextId: 1 };
var listEl = document.createElement('ul');

function visibleItems() {
  if (state.filter === 'all') { return state.items.slice(); }
  return state.items.filter(function (item) { return item.tag === state.filter; });
}

function render() {
  listEl.textContent = '';
  visibleItems().forEach(function (item) {
    var li = document.createElement('li');
    li.className = item.done ? 'item done' : 'item';
    li.dataset.id = String(item.id);
    li.textContent = item.title;
    listEl.appendChild(li);
  });
}

function show(label) {
  var rows = [];
  listEl.querySelectorAll('li').forEach(function (li) {
    rows.push(li.textContent + (li.classList.contains('done') ? ' [done]' : ''));
  });
  console.log(label + ': ' + rows.join(' | '));
}

function addItem(title, tag) {
  state.items.push({ id: state.nextId, title: title, tag: tag, done: false });
  state.nextId += 1;
  render();
}

function toggleDone(id) {
  state.items.forEach(function (item) { if (item.id === id) { item.done = !item.done; } });
  render();
}

function setFilter(tag) { state.filter = tag; render(); }

addItem('Eloquent JavaScript', 'js');
addItem('CSS Secrets', 'css');
addItem('Inclusive Components', 'a11y');
show('three added');
toggleDone(1);
show('after Done on id 1');
setFilter('css');
show('filter css');
setFilter('all');
show('back to all');
```

The second and fourth lines are the ones the opening got wrong. *Eloquent JavaScript*
comes back from the `css` filter still marked done, because the mark was never in the
row. It was in `state.items[0].done`, and the row was drawn from that field both times.

## The listener that outlived its button

Redrawing has a cost, and it shows up the first time a button is clicked twice.
`render()` throws the rows away, and a listener attached to a button goes with the
button. Bind a click handler to each *Done* button after the first render and it works
exactly once: the click toggles `done`, the render replaces the row, and the new *Done*
has no listener on it. The second click does nothing, with nothing in the console to say
why. The lab's fourth check clicks *Done* on the same row before and after a re-render
for precisely this reason.

The way out is in how a click travels. It does not stay at the button: the event starts
there and then *bubbles*, visiting the `<li>`, the `<ul>`, `<main>`, `<body>`, `<html>`
and `document`, and a listener on any of those hears it. So bind one listener to the
`<ul>`, which is in the read-only HTML and is never replaced, and every button that will
ever exist inside it is covered, including the ones the next render has not built yet.

```js
var state = { items: [{ id: 1, title: 'Refactoring UI', done: false }] };
var direct = document.createElement('ul');
var delegated = document.createElement('ul');
document.body.appendChild(direct);
document.body.appendChild(delegated);
var directClicks = 0;
var delegatedClicks = 0;

function row(item) {
  var li = document.createElement('li');
  li.dataset.id = String(item.id);
  var button = document.createElement('button');
  button.className = 'js-done';
  button.textContent = 'Done';
  li.appendChild(button);
  return li;
}

function renderBoth() {
  direct.textContent = '';
  delegated.textContent = '';
  state.items.forEach(function (item) {
    direct.appendChild(row(item));
    delegated.appendChild(row(item));
  });
}

renderBoth();

/* Direct: bind to the buttons that exist right now. */
direct.querySelectorAll('.js-done').forEach(function (button) {
  button.addEventListener('click', function () { directClicks += 1; });
});

/* Delegated: bind once, to the list. */
delegated.addEventListener('click', function (event) {
  var button = event.target.closest('button');
  if (!button) { return; }
  var id = Number(button.closest('li[data-id]').dataset.id);
  delegatedClicks += 1;
  console.log('delegated: a click on item ' + id + ' (a ' + typeof id + ')');
});

direct.querySelector('.js-done').click();
delegated.querySelector('.js-done').click();
console.log('one click each: direct ' + directClicks + ', delegated ' + delegatedClicks);

renderBoth();
direct.querySelector('.js-done').click();
delegated.querySelector('.js-done').click();
console.log('re-render, one click each: direct ' + directClicks + ', delegated ' + delegatedClicks);
```

The last line shows what a re-render does to the direct version: the count stops at one,
because the button it was bound to is gone and the new one was never bound. The
delegated listener was bound before any row existed and is still bound after the last;
the module's counting exercise puts a number on that difference.

Inside the handler, two properties answer two questions.
`event.currentTarget` is the element whose listener is running: always the `<ul>`.
`event.target` is where the click landed, the deepest element under the pointer — the
button, or a `<span>` inside it if the markup had one. `event.target.closest('button')`
walks up from there to the nearest button, and returns `null` when the click was on the
list's own padding, which is why the handler opens with a guard. From the button,
`button.closest('li[data-id]')` walks further up to the row.

That last step needs the row to know which item it is. An element has no memory of the
array entry it was drawn from, so the render writes it down, as `data-id="3"`, and the
handler reads it back through `row.dataset.id`. One trap on that line catches nearly
everyone once: every attribute in the DOM is a string. `dataset.id` is `"3"`,
`state.items[2].id` is `3`, and `"3" === 3` is false, so `item.id !== id` holds for every
item and `removeItem` filters nothing out while reporting nothing wrong. The block above
converts at the boundary with `Number(...)`, and everything past that line deals in
numbers.

## A view is a function, not a second array

The filter is where a second copy creeps back in under another name. It is tempting to
keep `visible`, an array of the items matching the current tag, updated whenever the
filter or the items change. That is a second copy of `state.items`, and it drifts the
same way. `visibleItems()` in the lab is a function: it reads `state.items` and
`state.filter` and returns the matches, computed fresh on every call, with nothing to
keep in step because nothing is stored.

`render()` draws from `visibleItems()`, and so does the empty message:
`emptyEl.hidden = items.length > 0` asks the derived list, because a filter that matches
nothing must show *Nothing to show for this filter* while `state.items` is far from
empty. The lab's fifth check switches to `css` with only a `js` book in the list and
expects the message; ask `state.items` instead and it stays hidden over a blank panel.

The filter buttons are the one thing the lab has you update in place: they live in the
read-only HTML outside `#list`, so `render()` never rebuilds them, and `setFilter` writes
`aria-pressed` on all four from `state.filter` every time the filter changes. The rule
is the same; only the drawing differs.

## Text goes in as text

The title in every row was typed by a person, and two properties will put a string into
a `<span>`. They differ in what they do with angle brackets:

```js
var typed = '<b>Eloquent</b> JavaScript';

var asText = document.createElement('span');
asText.textContent = typed;

var asMarkup = document.createElement('span');
asMarkup.innerHTML = typed;

console.log('textContent: ' + asText.childNodes.length + ' child node (' +
  asText.firstChild.nodeName + '), on screen: ' + asText.textContent);
console.log('innerHTML: ' + asMarkup.childNodes.length + ' child nodes (' +
  asMarkup.firstChild.nodeName + ' then ' + asMarkup.lastChild.nodeName +
  '), on screen: ' + asMarkup.textContent);
```

`textContent` makes one text node whose characters are the string, angle brackets
included, and that is what appears on screen. `innerHTML` hands the string to the HTML
parser and appends whatever it builds — here a `<b>` element and a text node. Swap the
harmless `<b>` for `<img src=x onerror="...">` and the parser builds an image, the image
fails to load, and the code in the attribute runs with everything your page can do. A
`script` element inserted this way does *not* run, which is why `innerHTML` gets a
reputation for being safe and why `onerror` is the attribute every real payload uses.
The rule that survives is short: text goes in with `textContent`; the capstone bans
`innerHTML` outright.

## Storage holds strings

Reload the page and `state` is `{ items: [] }` again, because the array lived in memory.
`localStorage` persists per origin across reloads — but it holds strings and nothing
else, and `setItem` does not refuse an object. It converts it with `String(value)` and
stores the result:

```js
var KEY = 'reading-list-demo';

localStorage.setItem(KEY, { items: [] });
console.log('stored an object directly, read back: ' + localStorage.getItem(KEY));

localStorage.setItem(KEY, JSON.stringify({
  items: [{ id: 1, title: 'CSS Secrets', tag: 'css', done: true }],
  filter: 'css',
  nextId: 2
}));
console.log('stored JSON, read back: ' + localStorage.getItem(KEY));

function loadState() {
  var fresh = { items: [], filter: 'all', nextId: 1 };
  var raw = null;
  try { raw = localStorage.getItem(KEY); } catch (err) { return fresh; }
  if (!raw) { return fresh; }
  try {
    var parsed = JSON.parse(raw);
    if (!parsed || !Array.isArray(parsed.items)) { return fresh; }
    return parsed;
  } catch (err) {
    return fresh;
  }
}

console.log('loaded: ' + loadState().items.length + ' item(s), filter ' + loadState().filter);
localStorage.setItem(KEY, 'not json at all {{{');
console.log('after junk: ' + loadState().items.length + ' item(s), filter ' + loadState().filter);
localStorage.setItem(KEY, '{"items": "three"}');
console.log('after the wrong shape: ' + loadState().items.length + ' item(s), filter ' + loadState().filter);
```

The first line is the trap: `[object Object]` is what every plain object stringifies to,
so the list was gone before it was stored, and no exception said so. The second is the
contract — `JSON.stringify` in, `JSON.parse` out. The last three are why the way out
needs guarding: the string in storage may have been written by an older version of the
code, by another tab, or by the lab's last check, which stores `not json at all {{{` and
calls `loadState()`. `JSON.parse` throws on the junk; the wrong shape parses without
complaint and would crash later, at the first `state.items.filter`. So `loadState` reads
inside a `try`, because `localStorage` itself throws when storage is disabled or the
browser is in a private mode; parses inside a `try`; checks for an object with an
`items` array; and on any failure hands back the fresh state, never a throw.

## The mistake, and why it is tempting

It is the one from the opening: the handler edits the element it is holding. It is
tempting because `event.target` is right there, `classList.toggle('done')` is one line,
and the screen changes before your finger is off the mouse, which feels like the job
being done. It is the half that does not last. The array does not know, the storage does
not know, and the next render draws the row from an array that still says `done: false`.

The version that hides longest is the double update: toggle the class *and* flip the
field. It works, and from then on every feature is written twice, until someone writes
only one half. Delete the picture half and let `render()` do it.

## Where this stops holding

Rebuilding every row is $O(n)$ per change. For twenty rows that is invisible. For five
thousand, or for rows holding an `<input>` the person is typing into, it is not: the
input is destroyed and recreated, focus and the caret go with it, and the scroll position
can jump. That is where a keyed diff — compare the new state against the rows on screen
and touch only the ones that changed — earns its complexity, and it is what every
framework's render loop is. State stays the truth; what changes is how the picture is
brought up to date.

Delegation has an edge too: `focus`, `blur`, `mouseenter` and `mouseleave` do not
bubble, so a `focus` listener on the `<ul>` never fires for a button inside it, and
`focusin` and `focusout` are the delegated forms. And `localStorage` is synchronous,
holds around five megabytes per origin, is shared by every tab of the site, which can
overwrite it under you, and carries no version, which is why the lab's key is
`reading-list-v1`: when the shape of the state changes, the name changes, and old data
stops being read as new.

## In the lab

*A filterable reading list* gives you a read-only `index.html` — the form, the four
filter buttons with `data-tag` and `aria-pressed` already on them, the empty
`<ul id="list">` and the hidden `#empty` paragraph — and an `app.js` of stubs. You write
`saveState` and `loadState`, the four mutators that change `state` and render,
`visibleItems`, `render`, and exactly three listeners: a delegated `click` on `#list`, a
delegated `click` on `#filters`, and a `submit` on the form that prevents the default.
Seven checks read it back: one row with `data-id`, `.js-done` and `.js-remove` after an
add; `null` for a blank title and a trimmed one for a padded title; `aria-pressed` on the
buttons after a click on `css`; *Done* still working on a row after another row's
removal re-rendered the list — the check this reading's second block was written for;
`#empty` showing for an empty list and for a filter that matches nothing; both items back
after `state.items` is emptied and `loadState()` called; and the fresh state, not a
throw, when storage holds junk.
''',
                },
                {
                    "title": "Values, and the four things you do to them",
                    "minutes": 11,
                    "body": r'''
A cart holds three items and the subtotal comes out as `120899249`. Nothing threw. The
number is not a rounding error or an off-by-one; it is the three prices written down next
to each other, because one of them arrived from an input as the string `'899'` and `+`
had to decide what to do with a number and a string. It decided to make text. This
reading is the small set of facts that make that decision predictable, and the four
operations — transform, keep, fold, find — that most of the code in this module is built
out of.

## What a value is

```js
var prices = [120, '899', 249];
var sum = 0;
prices.forEach(function (p) { sum = sum + p; });
console.log('sum: ' + sum + ' (a ' + typeof sum + ')');
```

`sum: 120899249 (a string)`. The first addition is `0 + 120` and both sides are numbers,
so it is arithmetic. The second is `120 + '899'`, and `+` is the one operator that means
two things: with two numbers it adds, and with a string on either side it joins. From
that point on `sum` is a string and every later `+` joins as well.

```js
console.log('120 + "899" is ' + (120 + '899'));
console.log('120 * "899" is ' + (120 * '899'));
console.log('"5" == 5 is ' + ('5' == 5));
console.log('"5" === 5 is ' + ('5' === 5));
console.log('Number("899") + 1 is ' + (Number('899') + 1));
console.log('Number("") is ' + Number(''));
console.log('Number("12px") is ' + Number('12px'));
console.log('NaN === NaN is ' + (NaN === NaN));
```

`120899`, then `107880`. Only `+` is ambiguous; `*`, `-` and `/` have no string meaning,
so they convert and do arithmetic, which is exactly why the bug hides — a total computed
as `price * qty` is fine and the same value added to a running sum is not.

Then `true`, then `false`. `==` converts before comparing and `===` refuses to, and the
whole of the difference is that one line. Use `===` and `!==` everywhere; the cases where
`==` is what you wanted are rare enough to write out longhand.

The last three are the boundary. `Number(...)` is where a string becomes a number, and it
is worth doing once, at the edge where the value arrives, rather than hoping. `Number('')`
is `0`, which is why an empty field can look like a legitimate zero. `Number('12px')` is
`NaN`, and `NaN === NaN` is `false` — the only value in the language not equal to itself,
so `Number.isNaN(x)` is how you ask.

The types you will meet are `number` (one type: `42` and `4.2` are both it), `string`,
`boolean`, `undefined` — a variable with no value yet — and `null`, which is the value
you assign to mean *deliberately nothing*. `typeof` names them.

## Naming, and the two keywords

```js
const taxRate = 0.25;
let total = 0;
total = total + 10;
```

`const` refuses reassignment; `let` allows it. Reach for `const` by default and change it
to `let` at the moment you need to reassign, because a name that cannot be reassigned is
one fewer thing to hold in your head while reading. `const` is not deep: `const cart = []`
forbids `cart = somethingElse` and permits `cart.push(item)` all day, which is the
behaviour you want and the one people expect least. `var` is the older keyword, scoped to
the whole enclosing function rather than to its block, and it exists in this course only
because the labs are written in it for consistency with the sandbox.

Backticks make a template literal: `` `Hello, ${name}` `` splices any expression into a
string, which beats a chain of `+` as soon as there are more than two pieces.

## Functions, in two spellings

```js
function greet(name) {
  return `Hello, ${name}`;
}

const double = (n) => n * 2;

const describe = (item) => {
  const label = item.name.toUpperCase();
  return `${label}: ${item.price}`;
};
```

An arrow function with a single expression and no braces returns that expression. Put
braces around the body and you are writing statements, and a `return` becomes your
responsibility — a function that ends without one returns `undefined`, which is how a
`map` quietly produces an array of nothings.

## Four things to do to a list

```js
var cart = [
  { name: 'Wiper blades', price: 120, qty: 2 },
  { name: 'Jack', price: 899, qty: 0 },
  { name: 'Torch', price: 249, qty: 1 }
];

var total = cart.reduce(function (sum, item) { return sum + item.price * item.qty; }, 0);
var available = cart.filter(function (item) { return item.qty > 0; });
var names = available.map(function (item) { return item.name; });

console.log('total: ' + total);
console.log('in stock: ' + names.join(', '));
console.log('cart still has ' + cart.length + ' entries');
console.log('first over 200: ' + cart.find(function (i) { return i.price > 200; }).name);
```

`total: 489` — that is $120 \times 2 + 899 \times 0 + 249 \times 1$. `in stock: Wiper
blades, Torch`. `cart still has 3 entries`, which is the point: `map`, `filter` and
`reduce` each build a new array or a new value and leave the original where it was, so
they chain without any of them being a hidden edit. `first over 200: Jack` — `find`
returns the element itself, or `undefined` when nothing matched, which is why reading
`.name` off it without a guard is a crash waiting for the empty case.

The shapes are worth naming, because choosing between them is most of the work: `map` is
one-in-one-out, `filter` is keep-or-drop with the elements unchanged, `reduce` folds the
whole list into a single value, `find` returns the first match, and `forEach` returns
nothing at all and exists for side effects. `push`, `splice` and `sort` are the mutating
ones — they change the array in place and return something other than the new array,
which is a common surprise.

An object is a bag of named values, read with `item.price` or `item['price']` when the
name is itself in a variable. `const { name, price } = item` pulls two of them into
variables in one line, and `Object.entries(item)` gives an array of `[key, value]` pairs
to loop over.

## The mistake, and why it is tempting

The one this reading opened with: taking a value out of the page and using it without
converting it. Everything that comes back from the DOM is a string — `input.value`,
`dataset.id`, `getAttribute(...)` — and a string behaves like a number under `*`, `-` and
`/` for long enough that the code looks correct. Then a `+` appears, or a `===` against a
real number fails silently, and the symptom shows up somewhere unrelated to the line that
caused it. Convert at the boundary, with `Number(...)`, on the line the value arrives.

## Where this stops holding

`Number` and `parseInt` disagree on purpose: `parseInt('12px')` is `12` and
`Number('12px')` is `NaN`, so the forgiving one is right for reading a CSS length and
wrong for validating a form. Floating point is the same everywhere and still surprises:
`0.1 + 0.2` is `0.30000000000000004`, so money is best held in whole pence, and
`toFixed(2)` returns a **string** — which is exactly the ingredient the opening bug was
made of.

`typeof null` is `'object'`, a bug preserved since 1995 for compatibility; test for it
with `x === null`. And `typeof []` is `'object'` too, so `Array.isArray(x)` is how you ask
whether something is a list — the check the previous module's `loadState` runs on whatever
came out of storage.

## In the lab

*Cart arithmetic that survives its inputs* gives you `cart.js` with four function bodies
to fill in and no page at all: `cartTotal` folds price times quantity, `formatPrice`
turns a number into `"$12.50"`, `applyDiscount` recognises two codes case-insensitively
and passes everything else through unchanged, and `inStock` filters then maps. Four
checks call them directly with the awkward inputs — an empty cart, an unknown code, a
missing code, a whole number that still needs two decimals.
''',
                },
                {
                    "title": "Reaching into the page",
                    "minutes": 11,
                    "body": r'''
`Uncaught TypeError: Cannot read properties of null (reading 'addEventListener')`, and
the line it points at is `button.addEventListener('click', onAdd)`. The button is on the
page — you can see it, you can click it, and the inspector shows it with the id the
selector asked for. The problem is not the selector; it is the clock. The `<script>` tag
was in the `<head>`, the parser stopped to fetch and run it, and at the moment it ran the
`<body>` had not been parsed. `document.querySelector('#add')` looked in a document that
did not contain the button yet and did what it always does when nothing matches: returned
`null`.

This reading is the DOM API those two lines belong to — how to find nodes, how to read
and change them, how to build new ones, and how to hear about what someone does to them.
The module's other reading argues for what to do with all of it: one state object, one
`render()`, one delegated listener. This one is the vocabulary that argument is written
in.

## Finding things

```js
const title = document.querySelector('h1');
const button = document.querySelector('#add');
const rows = document.querySelectorAll('.item');
```

Both take a CSS selector — the same language as a stylesheet, so anything you can style
you can find. `querySelector` returns the first match **in document order**, or `null`.
`querySelectorAll` returns a `NodeList`, which is empty rather than `null` when nothing
matches, and which has `forEach` but not `map` or `filter` — `Array.from(rows)` or
`Array.prototype.slice.call(rows)` when you want those.

`document.getElementById('add')` is the same lookup without the selector parsing, and it
is the one to reach for when you have an id. Its cousin
`document.getElementsByClassName('row')` is not equivalent to `querySelectorAll`, and the
difference matters:

```js
var box = document.createElement('div');
document.body.appendChild(box);
['a', 'b', 'c'].forEach(function (t) {
  var p = document.createElement('p');
  p.className = 'row';
  p.textContent = t;
  box.appendChild(p);
});

var snapshot = box.querySelectorAll('.row');
var live = box.getElementsByClassName('row');
console.log('before: snapshot ' + snapshot.length + ', live ' + live.length);

box.removeChild(box.firstElementChild);
console.log('after one removal: snapshot ' + snapshot.length + ', live ' + live.length);

for (var i = 0; i < live.length; i++) { live[i].remove(); }
console.log('after the loop: ' + box.children.length + ' left, expected 0');
```

`before: snapshot 3, live 3`. Then `after one removal: snapshot 3, live 2` — the
`NodeList` from `querySelectorAll` is a static list of the nodes that matched at the
moment it was taken, and the `HTMLCollection` from `getElementsByClassName` is a live view
that re-answers the question every time you ask. The last line reads `after the loop: 1
left, expected 0`: removing `live[0]` shortens `live` under the loop, `i` moves to 1, the
length is now 1, and the loop exits with one element still on the page. Iterate backwards,
or take a snapshot first.

## Reading and writing a node

```js
title.textContent = 'Inventory';
input.value;
img.src = 'photo.jpg';
el.classList.add('done');
el.classList.toggle('done', isDone);
el.hidden = true;
el.dataset.id;
```

`textContent` is the text of an element and everything inside it. `value` is the current
contents of a form control and is not the same thing as its `value` **attribute**:

```js
var form = document.createElement('form');
var input = document.createElement('input');
input.setAttribute('value', 'Torch');
form.appendChild(input);
document.body.appendChild(form);

input.value = 'Wiper blades';
console.log('property: ' + input.value);
console.log('attribute: ' + input.getAttribute('value'));
```

`property: Wiper blades`, `attribute: Torch`. The attribute is what the markup said and
it does not move; the property is the live state. Every time someone types, the two drift
apart, which is why reading a field with `getAttribute('value')` returns what it started
as and why a form reset puts the attribute's value back. The same split shows up as
`checked`, `disabled` and `hidden`: read and write the property, and treat the attribute
as the initial value.

`classList` has `add`, `remove`, `contains`, and `toggle` — whose two-argument form,
`toggle('done', task.done)`, is a conditional add-or-remove and reads better than an `if`.
`dataset.id` maps to the `data-id` attribute, and the mapping is camel-case both ways:
`data-item-id` arrives as `dataset.itemId`. Everything it returns is a string.

## Building nodes

```js
const li = document.createElement('li');
li.className = 'item';
li.textContent = task.title;
list.append(li);
li.remove();
list.replaceChildren();
```

`createElement` makes a detached node — it exists, it is not on the page, and nothing is
drawn until it is inserted. `append` adds at the end and `prepend` at the start; both
accept several nodes at once, and both accept plain strings, which are inserted as text.
`remove()` takes a node off the page. `replaceChildren()` with no arguments empties a
container, and `el.textContent = ''` does the same thing; both are worth knowing because
the third way, `el.innerHTML = ''`, is a habit that ends in the one place `innerHTML` must
never be used.

## Hearing about what happened

```js
button.addEventListener('click', function () {
  count += 1;
  render();
});

input.addEventListener('input', function (event) {
  console.log(event.target.value);
});

form.addEventListener('submit', function (event) {
  event.preventDefault();
  addTask(input.value);
});
```

`addEventListener(type, handler)` can be called any number of times on the same element
for the same type, and every handler runs. The handler is given an event object: `type`,
`target` — the deepest element the event actually landed on — and `currentTarget`, the
element whose listener is running.

The types cover most of what a page needs. `click` for buttons and links, and it fires for
Enter and Space on a real `<button>` as well as for a mouse. `input` fires on every
keystroke in a text field; `change` fires when a `<select>` or a checkbox settles, and for
a text field only when it loses focus. `submit` fires on the form, not on the button, and
its default action is a full page navigation — which `preventDefault()` cancels, and which
is why a form handler that forgets that line appears to do nothing except reload.

`preventDefault()` and `stopPropagation()` are different tools and get confused. The first
cancels what the browser was going to do — navigate, submit, tick the checkbox — and lets
the event carry on travelling. The second stops the event travelling and leaves the
default action in place. Delegation depends on events travelling, so `stopPropagation` in
a handler is how a delegated listener higher up silently stops firing.

## The mistake, and why it is tempting

The opening one: running the script before the elements exist. It is tempting because
`<head>` is where a page's other resources go, and because moving the tag makes the error
disappear without explaining anything. Two fixes are worth telling apart. Putting
`<script src="app.js"></script>` immediately before `</body>` means the parser has already
built everything above it, which is what the labs in this course do. Writing
`<script defer src="app.js"></script>` in the `<head>` lets the file be fetched in
parallel and runs it once the document is parsed — same guarantee, one less thing to
remember, and it is the better default outside a teaching sandbox.

## Where this stops holding

`querySelector` searches the DOM, not your file, so an element added by a later render is
found and an element in the file that a script removed is not.

`event.target` is not always the element you bound to, and depends on the markup inside
it: a click on the `<span>` inside a button has that span as its target, which is why
`event.target.closest('button')` appears in every delegated handler in this course.
`focus`, `blur`, `mouseenter` and `mouseleave` do not travel upwards at all, so they
cannot be delegated; `focusin` and `focusout` are the versions that can.

And a listener attached to a node is discarded with that node. A page that rebuilds its
rows throws away every handler bound to them, which is the whole reason the next reading
is about listening on the container instead.

## In the lab

Two labs run on this vocabulary. *A counter that renders from a variable* is the smallest
possible version: one number, three buttons, and a `render()` that puts the number on the
page — with a floor at zero, so the decrement button has a rule to obey. *A to-do list
that counts what is left* adds the array: a `submit` handler that trims the input and
refuses a blank, a delegated `click` on the list that toggles an item, and a count of the
undone that is derived on every render rather than kept alongside.
''',
                },
            ],
            "quiz": [{
                "title": "One truth, one render, one listener",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why rebuild the whole list in `render()` instead of patching the row that changed?",
                        "opts": [
                            "Because rebuilding is faster than patching in every browser",
                            "Because the DOM offers no way to change a single node",
                            "Because a patch is a second description of the truth, and it drifts the first time a case is forgotten",
                            "Because `textContent` can only be assigned once per element",
                        ],
                        "a": 2,
                        "why": r"""
Patching means writing the transition for every change: mark done, un-mark, remove,
rename, re-tag, and every pair of those happening close together. Each one is a separate
chance to update the array and forget the DOM, and the symptom is a row that says
something the state does not. Re-rendering has one path, so there is one place to be
wrong. It is not automatically faster — for very long lists it is measurably slower, and
that is when a keyed diff earns its complexity. Start with the version that cannot drift.
""",
                    },
                    {
                        "q": "A click handler is bound to `#list`. Inside it, what is `event.currentTarget`?",
                        "opts": [
                            "The deepest element the click actually landed on",
                            "`#list` — the element the listener is attached to",
                            "The `<li>` containing the button that was clicked",
                            "`document`, since the event has finished bubbling",
                        ],
                        "a": 1,
                        "why": r"""
`target` is where the event started — usually the `<button>`, sometimes a `<span>`
inside it — and it does not change as the event bubbles. `currentTarget` is whichever
element is running a handler right now, so inside a listener bound to `#list` it is
always `#list`. Delegation is built on having both: bind to the stable element, then ask
`event.target.closest('button')` which control the person was actually aiming at.
""",
                    },
                    {
                        "q": "For `<li data-id=\"3\">`, what does `li.dataset.id === 3` evaluate to?",
                        "opts": [
                            "`false` — `dataset` gives back the string `\"3\"`",
                            "`true`",
                            "`true`, because the browser coerces numeric data attributes",
                            "A `TypeError`, because `dataset` has no `id` property",
                        ],
                        "a": 0,
                        "why": r"""
Every attribute in the DOM is a string, `data-*` included, so `li.dataset.id` is `"3"`
and `"3" === 3` is false. This is the bug that makes a delegated handler look broken:
the click fires, the row is found, and then `state.items.filter(i => i.id !== id)`
removes nothing because it is comparing numbers with a string. Convert once, on the way
in — `Number(row.dataset.id)` — and let everything downstream deal in numbers.
""",
                    },
                    {
                        "q": "A user titles a book `<img src=x onerror=alert(1)>`. What separates `title.textContent = item.title` from `title.innerHTML = item.title`?",
                        "opts": [
                            "Nothing — both escape the string before inserting it",
                            "`textContent` puts those characters on the page as text; `innerHTML` parses them as markup and the `onerror` fires",
                            "`innerHTML` is simply the faster of the two",
                            "`textContent` strips the tags and `innerHTML` keeps them, but neither runs anything",
                        ],
                        "a": 1,
                        "why": r"""
`textContent` sets a text node: the angle brackets are just characters and the title
appears on screen exactly as it was typed. `innerHTML` hands the string to the HTML
parser, which builds an `<img>` with a broken `src`, fires its error handler, and runs
whatever was in the attribute. It is a common surprise that an injected `<script>` tag
does *not* execute this way — which is why people conclude `innerHTML` is safe, and why
the `onerror` trick is the one every payload uses. The rule that survives contact with
reality is simpler: text goes in with `textContent`.
""",
                    },
                    {
                        "q": "`localStorage.setItem('k', { a: 1 })`, then `localStorage.getItem('k')`. What comes back?",
                        "opts": [
                            "The object `{ a: 1 }`",
                            "`null`, because objects are rejected",
                            "A `TypeError`, because the Storage API only accepts strings",
                            "`\"[object Object]\"` — storage holds strings, and the object was coerced into one",
                        ],
                        "a": 3,
                        "why": r"""
The Storage API stringifies whatever it is handed, so the object becomes
`"[object Object]"` and the data is gone — with no exception to tell you. `JSON.stringify`
going in and `JSON.parse` coming out is the whole contract, and the parse is the half
that needs a `try`/`catch`: the string sitting in storage was written by an older version
of your code, or by a different tab, or by nothing at all. Note that quota errors *do*
throw, so the write is worth wrapping too.
""",
                    },
                ],
            }, {
                "title": "Values, nodes and handlers",
                "minutes": 7,
                "questions": [
                    {
                        "q": "`const cart = [];` is at the top of the file. Which line below it is refused?",
                        "opts": [
                            "`cart = [];` — the name cannot be pointed at a different array",
                            "`cart.push(item);` — a `const` array is frozen against every change",
                            "`cart.length = 0;` — `const` forbids writing any property",
                            "Both `cart = []` and `cart.push(item)`, for the same reason",
                        ],
                        "a": 0,
                        "why": r"""
`const` freezes the binding, not the value. The name `cart` will point at that one array
for the rest of its scope, and the array itself stays as mutable as any other —
`push`, `splice`, `sort` and `cart.length = 0` all work. That is the behaviour you want,
and the one people expect least, which is why `const` is the sensible default for
practically every declaration: it says *this name means one thing here*, which is the
useful promise, without pretending the contents cannot move. Freezing the contents is a
separate request — `Object.freeze(cart)` — and a write to a frozen array throws under
strict mode and is discarded without a word outside it.
""",
                    },
                    {
                        "q": "Why prefer `===` over `==`?",
                        "opts": [
                            "`===` compares without converting first, so `'5' === 5` comes out false",
                            "`==` was removed from the language and now throws in files using strict mode",
                            "`===` is required whenever either side might be `null` or `undefined`",
                            "They behave identically; `===` is a style preference some teams hold",
                        ],
                        "a": 0,
                        "why": r"""
`==` converts its operands to a common type before comparing, so `'5' == 5` is true and
`'' == 0` is true and `null == undefined` is true. Every value that comes out of the DOM
is a string, so an id read from `dataset` compared with `==` against a number matches when
you meant it to and also when you did not, and the failure is silent either way. `===`
refuses the conversion and answers the question you asked. `==` is still in the language
and always will be — nothing throws — and the two are emphatically not identical, which
is the whole reason the rule exists.
""",
                    },
                    {
                        "q": "`[1, 2, 3].map(n => n * 2)` evaluates to what, and what becomes of the original array?",
                        "opts": [
                            "`[2, 4, 6]`, and the original is untouched",
                            "`6`, the sum, with the original untouched",
                            "`[2, 4, 6]`, with the original array rewritten in place",
                            "`[1, 2, 3, 2, 4, 6]`, the original with the results appended",
                        ],
                        "a": 0,
                        "why": r"""
`map` is one-in, one-out: it walks the array, calls the function on each element, and
collects the return values into a **new** array of the same length. The original is left
exactly as it was, which is what makes `map`, `filter` and `find` safe to chain — no step
can quietly change the input of the one before it. Folding a list down to a single value
is `reduce`, and it needs a starting value to fold into. The mutating methods are a
separate group worth knowing by name: `push`, `pop`, `splice`, `sort` and `reverse` change
the array in place and hand back something other than a new one.
""",
                    },
                    {
                        "q": "`document.querySelector('.item')` on a page that has no `.item` returns what?",
                        "opts": [
                            "`null`, which is why a guard belongs before the first property read",
                            "An empty `NodeList`, so `.length` is `0` and a loop runs zero times",
                            "`undefined`, the value of any lookup that found nothing",
                            "The `<body>`, because the search falls back to the document root",
                        ],
                        "a": 0,
                        "why": r"""
`querySelector` returns the first match or `null`, and `null` is where
*Cannot read properties of null* comes from one line later. Its plural,
`querySelectorAll`, is the one that returns an empty `NodeList` — never `null` — so a
`forEach` over it is safe with no guard at all, and that difference is worth keeping
straight because it decides whether you owe the next line a check. The commonest cause of
a `null` here is not a wrong selector but a script that ran before the element was parsed:
put the tag before `</body>`, or give it `defer`.
""",
                    },
                    {
                        "q": "A `submit` handler runs, and then the page reloads and everything typed is gone. What is missing?",
                        "opts": [
                            "`event.preventDefault()`, which cancels the browser's own navigation",
                            "`event.stopPropagation()`, which keeps the event off the document",
                            "`return false` at the end, which is what every form handler is required to end with",
                            "An `action` on the `<form>`, without which the browser reloads the page",
                        ],
                        "a": 0,
                        "why": r"""
Submitting a form has a default action — navigate to the form's target, sending the
values — and it happens whether or not you listened for the event. `preventDefault()` is
what cancels it, leaving your handler as the only thing that acts. `stopPropagation()` is
the other tool and does the other job: it stops the event travelling up to ancestors and
leaves the default action untouched, so the page still reloads and any delegated listener
above quietly stops firing. `return false` cancels the default in old inline `onsubmit`
attributes and means nothing to `addEventListener`. And a form with no `action` submits
to the current URL, which is the reload you saw.
""",
                    },
                    {
                        "q": "The markup is `<input value=\"Torch\">` and someone types `Wiper blades`. What do `input.value` and `input.getAttribute('value')` read back?",
                        "opts": [
                            "`Wiper blades` and `Torch` — the property is live, the attribute is the initial value",
                            "`Wiper blades` from both, because the attribute is kept in step with the property as it changes",
                            "`Torch` from both, because the markup is what the browser keeps",
                            "`Wiper blades` and `null`, the attribute being consumed at parse time",
                        ],
                        "a": 0,
                        "why": r"""
The attribute is what the markup said and it does not move; the property is the control's
current state. They start equal and part company the first time anyone types, which is why
reading a field with `getAttribute('value')` returns a stale answer that looked correct in
testing — before anybody had typed. The same split runs through `checked`, `selected` and
`disabled`: write and read the property, and treat the attribute as the starting value.
It is also what a form reset restores from, which is why resetting puts `Torch` back.
""",
                    },
                    {
                        "q": "`var live = box.getElementsByClassName('row');` then `for (var i = 0; i < live.length; i++) { live[i].remove(); }`. What happens to the rows?",
                        "opts": [
                            "Half the rows survive — the collection is live and shrinks under the loop",
                            "Every row goes, since the collection was fixed when it was taken",
                            "It throws, because a live collection cannot be changed while it is being read",
                            "Nothing at all: a live collection is read-only and `remove()` is refused",
                        ],
                        "a": 0,
                        "why": r"""
An `HTMLCollection` from `getElementsByClassName` is a live view, not a list: it
re-answers the question every time it is asked. Remove `live[0]` and everything shifts
down while `i` moves up, so the loop skips every other element and stops early with half
the rows still on the page — and nothing throws, which is what makes it hard to spot.
`querySelectorAll` returns a static `NodeList` taken once, which is why it is the safe one
to iterate while removing; the alternatives are to loop backwards, or to snapshot with
`Array.from(live)` first.
""",
                    },
                ],
            }],
            "blanks": {
                "title": "Delegation and render, line by line",
                "minutes": 9,
                "caption": "app.js — five holes",
                "lang": "js",
                "brief": r'''
The two halves that have to agree with each other: the render that builds rows, and the
one listener that has to keep working on rows built by a render that had not happened
yet when it was bound. Nothing runs here — you are choosing identifiers.
''',
                "listing": r'''/* One listener for the whole list, bound once, before any row exists. */
listEl.addEventListener('click', function (event) {
  var button = event.___.closest('button');
  if (!button) { return; }
  var row = button.closest('li[data-id]');
  var id = ___(row.dataset.id);
  if (button.classList.contains('js-done')) { toggleDone(id); }
  if (button.classList.contains('js-remove')) { removeItem(id); }
});

function render() {
  var items = visibleItems();
  listEl.textContent = '';
  items.forEach(function (item) {
    var li = document.createElement('li');
    li.className = item.done ? 'item done' : 'item';
    li.dataset.___ = String(item.id);

    var title = document.createElement('span');
    title.className = 'item-title';
    title.___ = item.title;

    li.appendChild(title);
    listEl.appendChild(li);
  });
  emptyEl.hidden = ___;
}
''',
                "blanks": [
                    {
                        "prompt": "Which element did the click actually land on?",
                        "hole": "prop",
                        "opts": ["currentTarget", "target", "relatedTarget", "detail"],
                        "a": 1,
                        "why": "`event.target` is the deepest element under the pointer, so `target.closest('button')` walks back up to the control that was pressed.",
                        "whys": [
                            "`currentTarget` is `listEl` itself — the element running the handler. Calling `closest('button')` on a `<ul>` searches the `<ul>` and its ancestors, finds no button, and returns null, so the handler gives up on every click.",
                            "`event.target` is the deepest element under the pointer, so `target.closest('button')` walks back up to the control that was pressed. It matters that it walks up: click the text inside the button and the target is the text's element, not the button.",
                            "`relatedTarget` is the *other* element in an enter/leave or focus pair — where the pointer came from, or where focus went. On a click event it is null.",
                            "`event.detail` on a mouse event is the click count: 1 for a single click, 2 for the second of a double. It is a number, and numbers have no `closest`.",
                        ],
                    },
                    {
                        "prompt": "The ids in `state.items` are numbers. What has to happen to the attribute?",
                        "hole": "fn",
                        "opts": ["String", "Boolean", "Number", "Object"],
                        "a": 2,
                        "why": "`dataset` hands back a string, and `\"3\" !== 3`, so every strict comparison downstream would fail silently.",
                        "whys": [
                            "`String` is what it already is. Leaving it as text means `item.id !== id` compares a number with a string, is always true, and `removeItem` cheerfully filters nothing out while reporting success.",
                            "`Boolean('3')` is `true`, and every row would answer to the same id. The list would behave as though there were one item in it.",
                            "`dataset` hands back a string, and `\"3\" !== 3`, so every strict comparison downstream would fail silently. Convert once here and the rest of the app deals only in numbers.",
                            "`Object('3')` gives a String wrapper object, which is worse than the string: it is never `===` anything, and it prints as `3` in the console while comparing equal to nothing at all.",
                        ],
                    },
                    {
                        "prompt": "The handler looks for `li[data-id]`. What must the render write?",
                        "hole": "key",
                        "opts": ["id", "itemId", "key", "index"],
                        "a": 0,
                        "why": "`dataset.id` is the `data-id` attribute — the dataset key and the attribute suffix are the same name, in camelCase.",
                        "whys": [
                            "`dataset.id` is the `data-id` attribute — the dataset key and the attribute suffix are the same name, and the selector in the handler is written against the attribute. The two spellings have to agree or the row is never found.",
                            "`dataset.itemId` writes `data-item-id`, because dataset camelCase maps onto hyphens in the attribute. The selector `li[data-id]` then matches nothing, and every click falls through the `if (!row)` guard in silence.",
                            "`dataset.key` writes `data-key`. It is a perfectly good name — as long as the selector is changed to match. Here it is not.",
                            "`dataset.index` writes `data-index`, and the name is a trap beyond the mismatch: a position in the array is not an identity. Remove one row and every index below it now points at the wrong item.",
                        ],
                    },
                    {
                        "prompt": "The title came from a text field somebody typed into.",
                        "hole": "prop",
                        "opts": ["innerHTML", "textContent", "outerHTML", "nodeValue"],
                        "a": 1,
                        "why": "`textContent` writes the characters as text, so a title containing angle brackets appears as typed rather than being parsed as markup.",
                        "whys": [
                            "`innerHTML` parses the string as HTML. A title of `<img src=x onerror=...>` becomes a real element and its error handler runs — user input reaching the parser is the whole of this class of bug.",
                            "`textContent` writes the characters as text, so a title containing angle brackets appears as typed rather than being parsed as markup. It is also the faster of the two, because no parser is involved.",
                            "`outerHTML` replaces the span *itself* with whatever the string parses to. The element you just created and are about to append is gone before it was used.",
                            "`nodeValue` is meaningful on text and comment nodes; on an element it reads as null and assigning to it does nothing at all. The row would render with an empty title and no error anywhere.",
                        ],
                    },
                    {
                        "prompt": "The message reads 'Nothing to show for this filter.' When is it hidden?",
                        "hole": "expr",
                        "opts": ["items.length > 0", "items.length === 0", "state.items.length > 0", "false"],
                        "a": 0,
                        "why": "`hidden` is true when there *is* something on screen, so the test is on the visible rows this render just produced.",
                        "whys": [
                            "`hidden` is true when there *is* something on screen, so the test is on the visible rows this render just produced. Empty list, or a filter that matches nothing: both give zero, both show the message.",
                            "That is the condition inverted — the message would appear exactly when there are rows to read and vanish when there are none.",
                            "`state.items` is everything, before the filter. Switch to a tag with no matches and the list renders empty while the message stays hidden, leaving a blank panel that says nothing. The derived view is what the render is showing, so the derived view is what it should ask.",
                            "`hidden = false` un-hides the paragraph, and nothing ever hides it again — so *Nothing to show for this filter.* sits there on every render, including above a full list of rows. A constant cannot follow a changing list in either direction: `false` shows the message forever, `true` would hide it forever. This is the half that announces itself the first time you load the page with data in it.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "What binding to every button costs",
                "minutes": 6,
                "brief": r'''
The argument for delegation is usually made as a matter of taste. It is cheaper than
that to make it as a count.

A dashboard shows a fixed table of 250 rows, and every row carries three buttons —
`Done`, `Edit`, `Remove`. `render()` clears the container and rebuilds all 250 rows
from state, and it runs eight times over the session: the first paint plus seven
changes. The direct version calls `addEventListener('click', ...)` on each button as
it is created. The delegated version calls it once, on the container, before a single
row exists.
''',
                "prompt": "How many `addEventListener` calls does the direct version make in total?",
                "note": "A whole number of calls, over the whole session.",
                "figure": "250 rows × 3 buttons per row, rebuilt on every one of 8 renders — against "
                          "one listener on the container, bound once and never rebound.",
                "given": [
                    {"label": "Rows, every render", "value": "250"},
                    {"label": "Buttons per row", "value": "3"},
                    {"label": "Renders in the session", "value": "8"},
                    {"label": "Delegated version", "value": "1 listener, bound once"},
                ],
                "aside": "The old nodes are discarded on each render and their listeners go with them — "
                         "but they were still created, one closure at a time.",
                "answer": 6000,
                "tol": 0,
                "unit": "calls",
                "hint": "Count the buttons on screen after one render, then ask how many times those "
                        "buttons are built from scratch.",
                "wrong": "750 is a single render's worth. The buttons are new elements every time "
                         "`render()` clears the container, so the listeners have to be attached again.",
                "why": r"""
$250 \times 3 = 750$ buttons on screen, rebuilt eight times: $750 \times 8 = 6000$
calls, against exactly one for the delegated version — bound before the first row
existed and still bound after the last re-render. The size of the number is not really
the point. The point is its shape: the direct count grows with the data *and* with the
number of renders, and the delegated one is constant in both. That same fact is why a
handler attached to a button stops firing after a re-render, which is the bug that sends
people looking for delegation in the first place — the element it was attached to no
longer exists.
""",
            },
            "lab": [{
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
            }, {
                "title": "Cart arithmetic that survives its inputs",
                "runtime": "js",
                "minutes": 16,
                "brief": r'''
No page here — `cart.js` on its own, and four functions to fill in. An item is
`{ name: "Jack", price: 899, qty: 2 }`.

- **`cartTotal(items)`** — the sum of `price * qty` across the list. An empty
  cart totals `0`, not `undefined`.
- **`formatPrice(amount)`** — a string with a `$` and exactly two decimal places:
  `formatPrice(12.5)` is `"$12.50"` and `formatPrice(1283)` is `"$1283.00"`.
- **`applyDiscount(total, code)`** — `"SAVE10"` takes 10% off, `"HALF"` takes
  50% off, and everything else — an unknown code, and `undefined` for no code at
  all — comes back unchanged. Codes are case-insensitive.
- **`inStock(items)`** — the **names** of the items whose `qty` is above zero, in
  the order they appear.

`reduce`, `filter` and `map` are built for the first and the last of those. The
`console.log` calls at the bottom of the file print to the Console tab while you
work; the checks call the functions directly, with the awkward inputs.
''',
                "files": [
                    {"name": "cart.js", "content": r'''
function cartTotal(items) {
  // TODO: fold the list into one number: price * qty, summed. Empty cart -> 0.
}

function formatPrice(amount) {
  // TODO: "$12.50" — a dollar sign and exactly two decimal places
}

function applyDiscount(total, code) {
  // TODO: SAVE10 -> 10% off, HALF -> 50% off, anything else unchanged.
  //       Case-insensitive, and `undefined` is one of the "anything else" cases.
}

function inStock(items) {
  // TODO: the names of the items with qty > 0, in order
}

const cart = [
  { name: "Wiper blades", price: 120, qty: 2 },
  { name: "Jack", price: 899, qty: 0 },
  { name: "Torch", price: 249, qty: 1 },
];

console.log(cartTotal(cart));
console.log(formatPrice(cartTotal(cart)));
console.log(applyDiscount(100, "save10"));
console.log(inStock(cart));
'''},
                ],
                "main": "cart.js",
                "solution": [
                    {"name": "cart.js", "content": r'''
function cartTotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.qty, 0);
}

function formatPrice(amount) {
  return `$${amount.toFixed(2)}`;
}

function applyDiscount(total, code) {
  const normalised = (code || "").toUpperCase();
  if (normalised === "SAVE10") return total * 0.9;
  if (normalised === "HALF") return total * 0.5;
  return total;
}

function inStock(items) {
  return items.filter(item => item.qty > 0).map(item => item.name);
}

const cart = [
  { name: "Wiper blades", price: 120, qty: 2 },
  { name: "Jack", price: 899, qty: 0 },
  { name: "Torch", price: 249, qty: 1 },
];

console.log(cartTotal(cart));
console.log(formatPrice(cartTotal(cart)));
console.log(applyDiscount(100, "save10"));
console.log(inStock(cart));
'''},
                ],
                "hints": [
                    "`cartTotal` is a fold: `items.reduce((sum, item) => sum + item.price * item.qty, 0)`. The `0` is not decoration — it is what an empty cart returns.",
                    "`toFixed(2)` gives exactly two decimal places and returns a **string**, so the `$` goes on with a template literal or a `+`. Anything it produces is text from then on.",
                    "Normalise the code before comparing: `(code || \"\").toUpperCase()` turns `undefined` into `\"\"` and `\"half\"` into `\"HALF\"`, so one comparison covers both awkward cases.",
                    "`inStock` is two steps in order — `filter` down to the items with stock, then `map` those to their names. Reversing the two would try to read `qty` off a string.",
                ],
                "tests": [
                    {"name": "cartTotal folds price times quantity", "code": r'''
assertEqual(cartTotal([{ name: "a", price: 120, qty: 2 }, { name: "b", price: 10, qty: 3 }]), 270, '120x2 + 10x3 should be 270');
assertEqual(cartTotal([]), 0, 'An empty cart totals 0 — check the starting value of the fold');
assertEqual(cartTotal([{ name: "a", price: 99, qty: 0 }]), 0, 'A quantity of zero contributes nothing');
'''},
                    {"name": "formatPrice always shows two decimals", "code": r'''
assertEqual(formatPrice(12.5), "$12.50", 'One decimal place needs padding to two');
assertEqual(formatPrice(1283), "$1283.00", 'A whole number still gets .00');
assertEqual(formatPrice(0.1), "$0.10", 'And a value under a dollar');
assertEqual(typeof formatPrice(5), "string", 'formatPrice returns a string, not a number');
'''},
                    {"name": "applyDiscount knows two codes and no others", "code": r'''
assertEqual(applyDiscount(100, "SAVE10"), 90, 'SAVE10 takes ten per cent off');
assertEqual(applyDiscount(100, "half"), 50, 'Codes are case-insensitive');
assertEqual(applyDiscount(100, "NOPE"), 100, 'An unknown code changes nothing');
assertEqual(applyDiscount(100, undefined), 100, 'No code at all changes nothing — and must not throw');
assertEqual(applyDiscount(0, "HALF"), 0, 'Half of nothing is still nothing');
'''},
                    {"name": "inStock filters, then maps to names", "code": r'''
assertEqual(inStock([{ name: "a", price: 1, qty: 0 }, { name: "b", price: 1, qty: 2 }, { name: "c", price: 1, qty: 1 }]), ["b", "c"], 'Only the items with stock, in the order they appear');
assertEqual(inStock([]), [], 'An empty cart has nothing in stock');
var _src = [{ name: "a", price: 1, qty: 0 }];
inStock(_src);
assertEqual(_src.length, 1, 'inStock must not remove anything from the array it was given — filter returns a new one');
'''},
                ],
            }, {
                "title": "A counter that renders from a variable",
                "runtime": "web",
                "minutes": 14,
                "brief": r'''
The smallest possible version of the pattern this module is about: one value,
one function that draws it, and three buttons that change the value and ask for
a redraw. `index.html` is read-only; everything goes in `app.js`.

- `#count` shows `0` to begin with
- `#increment` adds one; `#decrement` subtracts one, and the count never goes
  below zero
- `#reset` puts it back to zero
- the number on screen is correct after every click

Write `render()` so that it puts `count` on the page and does nothing else, and
have every handler change `count` and then call it. Nothing but `render()` should
touch `#count` — that is the habit the rest of the module is built on, and it is
what makes the next two labs short.
''',
                "files": [
                    {"name": "index.html", "ro": True, "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Counter</title>
<style>
  body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; display: grid; place-items: center; min-height: 100vh; margin: 0; }
  .counter { text-align: center; }
  #count { font-size: 64px; font-weight: 700; margin: 0 0 12px; }
  button { font: inherit; font-size: 18px; padding: 8px 18px; margin: 0 4px; border-radius: 8px; border: 1px solid #d7dce4; background: #fff; cursor: pointer; }
  button:hover { background: #f4f4f6; }
</style>
</head>
<body>

<main class="counter">
  <h1 id="count-label">Counter</h1>
  <p id="count" aria-live="polite" aria-labelledby="count-label">0</p>
  <button id="decrement" type="button">Subtract one</button>
  <button id="increment" type="button">Add one</button>
  <button id="reset" type="button">Reset</button>
</main>

<script src="app.js"></script>
</body>
</html>
'''},
                    {"name": "app.js", "content": r'''
let count = 0;

const countEl = document.querySelector("#count");

function render() {
  // TODO: put `count` on the page. One line, and the only line that touches #count.
}

// TODO: wire the three buttons. Each one changes `count`, then calls render().

render();
'''},
                ],
                "main": "index.html",
                "solution": [
                    {"name": "app.js", "content": r'''
let count = 0;

const countEl = document.querySelector("#count");

function render() {
  countEl.textContent = count;
}

document.querySelector("#increment").addEventListener("click", () => {
  count += 1;
  render();
});

document.querySelector("#decrement").addEventListener("click", () => {
  if (count > 0) {
    count -= 1;
  }
  render();
});

document.querySelector("#reset").addEventListener("click", () => {
  count = 0;
  render();
});

render();
'''},
                ],
                "hints": [
                    "`render()` is one line: `countEl.textContent = count;`. Resist putting the arithmetic in it — it draws, it does not decide.",
                    "Each button is the same three lines: `document.querySelector(\"#increment\").addEventListener(\"click\", () => { count += 1; render(); });`",
                    "The floor belongs in the handler, not in `render()`: `if (count > 0) { count -= 1; }`. Clamping while drawing would leave the variable and the screen disagreeing.",
                    "The final `render()` at the bottom is what puts the starting value on screen. Without it the page shows whatever the markup happened to say.",
                ],
                "tests": [
                    {"name": "It starts at zero", "code": r'''
document.querySelector('#reset').click();
assertEqual(document.querySelector('#count').textContent.trim(), '0', 'The count should read 0 after a reset');
'''},
                    {"name": "Add one, twice", "code": r'''
document.querySelector('#reset').click();
var _c = document.querySelector('#count');
document.querySelector('#increment').click();
document.querySelector('#increment').click();
assertEqual(_c.textContent.trim(), '2', 'After two clicks on Add one the count reads ' + _c.textContent.trim());
'''},
                    {"name": "Subtract one, and never below zero", "code": r'''
document.querySelector('#reset').click();
var _c = document.querySelector('#count');
document.querySelector('#increment').click();
document.querySelector('#increment').click();
document.querySelector('#decrement').click();
assertEqual(_c.textContent.trim(), '1', 'Two up and one down should read 1, got ' + _c.textContent.trim());
for (var _i = 0; _i < 5; _i++) { document.querySelector('#decrement').click(); }
assertEqual(_c.textContent.trim(), '0', 'The count must not fall below zero, got ' + _c.textContent.trim());
'''},
                    {"name": "Reset returns to zero", "code": r'''
document.querySelector('#increment').click();
document.querySelector('#increment').click();
document.querySelector('#reset').click();
assertEqual(document.querySelector('#count').textContent.trim(), '0', 'Reset should put the count back to 0');
document.querySelector('#increment').click();
assertEqual(document.querySelector('#count').textContent.trim(), '1', 'and the counter should keep working afterwards');
'''},
                ],
            }, {
                "title": "A to-do list that counts what is left",
                "runtime": "web",
                "minutes": 20,
                "brief": r'''
The counter with an array behind it. `index.html` is read-only; write `app.js`.

- Submitting `#task-form` — by pressing Enter in the field or clicking **Add** —
  appends the text of `#new-task` to `tasks` and clears the input.
- A title that is empty or only spaces is refused: nothing is added, and the
  input is left alone so the person can see what they typed.
- Clicking a task's `<li>` toggles its `done` flag, and the row carries the class
  `done` exactly when the flag is set.
- `#remaining` always shows how many tasks are **not** done.

The shape is the one from the counter, one size up. `tasks` is the truth,
`render()` rebuilds `#tasks` from it and writes `#remaining`, and every handler
changes `tasks` and calls `render()`. Two rules make the difference here: the
submit handler needs `event.preventDefault()`, or the page reloads and the array
goes with it; and the click listener belongs on `#tasks`, not on each `<li>`,
because every render throws the rows away and a listener bound to a row goes
with it.

Give each row a `data-id` from the task's own id, and read it back with
`Number(...)` — `dataset` hands you a string, and `"3" === 3` is false.
''',
                "files": [
                    {"name": "index.html", "ro": True, "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Today</title>
<style>
  body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; max-width: 26rem; margin: 2.5rem auto; padding: 0 1rem; color: #1b1f27; }
  form { display: flex; gap: 0.5rem; }
  input { flex: 1; font: inherit; padding: 0.5rem 0.6rem; border: 1px solid #d7dce4; border-radius: 6px; }
  button { font: inherit; padding: 0.5rem 0.9rem; border-radius: 6px; border: 0; background: #1b1f27; color: #fff; font-weight: 600; cursor: pointer; }
  ul { list-style: none; padding: 0; }
  li { padding: 0.6rem 0.7rem; border-bottom: 1px solid #eceff3; cursor: pointer; }
  li.done { text-decoration: line-through; color: #8b93a1; }
  .meta { color: #5a6270; font-size: 0.9rem; }
  .sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
</style>
</head>
<body>

<main>
  <h1>Today</h1>

  <form id="task-form">
    <label class="sr-only" for="new-task">What needs doing?</label>
    <input id="new-task" name="task" type="text" placeholder="What needs doing?" autocomplete="off">
    <button type="submit">Add</button>
  </form>

  <ul id="tasks"></ul>
  <p class="meta"><span id="remaining">0</span> left</p>
</main>

<script src="app.js"></script>
</body>
</html>
'''},
                    {"name": "app.js", "content": r'''
const form = document.querySelector("#task-form");
const input = document.querySelector("#new-task");
const list = document.querySelector("#tasks");
const remaining = document.querySelector("#remaining");

let tasks = [];      // { id, title, done }
let nextId = 1;

function render() {
  // TODO: rebuild #tasks from `tasks` — one <li> per task, carrying data-id and
  //       the class "done" when it is done — then write the undone count into
  //       #remaining.
}

// TODO: a submit listener on the form that prevents the default, trims the
//       input, refuses a blank title, appends, clears the field and renders.

// TODO: one delegated click listener on `list` that finds the <li> the click
//       landed in, toggles that task, and renders.

render();
'''},
                ],
                "main": "index.html",
                "solution": [
                    {"name": "app.js", "content": r'''
const form = document.querySelector("#task-form");
const input = document.querySelector("#new-task");
const list = document.querySelector("#tasks");
const remaining = document.querySelector("#remaining");

let tasks = [];      // { id, title, done }
let nextId = 1;

function render() {
  list.textContent = "";
  tasks.forEach((task) => {
    const li = document.createElement("li");
    li.textContent = task.title;
    li.dataset.id = String(task.id);
    li.classList.toggle("done", task.done);
    list.append(li);
  });
  remaining.textContent = tasks.filter((task) => !task.done).length;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = input.value.trim();
  if (!title) {
    return;
  }
  tasks.push({ id: nextId, title: title, done: false });
  nextId += 1;
  input.value = "";
  render();
});

list.addEventListener("click", (event) => {
  const li = event.target.closest("li[data-id]");
  if (!li) {
    return;
  }
  const id = Number(li.dataset.id);
  const task = tasks.find((t) => t.id === id);
  if (!task) {
    return;
  }
  task.done = !task.done;
  render();
});

render();
'''},
                ],
                "hints": [
                    "`render()` in three moves: empty the list with `list.textContent = \"\"`, append one `<li>` per task, then write `tasks.filter(t => !t.done).length` into `#remaining`.",
                    "The submit handler starts with `event.preventDefault()` and then `input.value.trim()`. Return early when the trimmed title is empty — before anything is pushed and before the field is cleared.",
                    "`classList.toggle(\"done\", task.done)` adds or removes the class in one line from the flag, so the row can never disagree with the array.",
                    "One listener on `list`, not one per row: `event.target.closest(\"li[data-id]\")` gives you the row a click landed in, or `null` when the click missed. `Number(li.dataset.id)` converts at the boundary.",
                ],
                "tests": [
                    {"name": "Adding a task renders a row", "code": r'''
tasks.length = 0;
render();
var _input = document.querySelector('#new-task');
var _form = document.querySelector('#task-form');
_input.value = 'Order oil filters';
_form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
var _items = document.querySelectorAll('#tasks li');
assertEqual(_items.length, 1, 'Expected one row after adding, found ' + _items.length);
assert(_items[0].textContent.indexOf('Order oil filters') !== -1, 'The row should show the title, got: ' + _items[0].textContent);
assert(_items[0].dataset.id, 'Each row needs a data-id, so a delegated handler can tell which task it is');
assertEqual(_input.value, '', 'Clear the input after a successful add');
'''},
                    {"name": "A blank title is refused", "code": r'''
tasks.length = 0;
render();
var _input = document.querySelector('#new-task');
var _form = document.querySelector('#task-form');
_input.value = '   ';
_form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
assertEqual(document.querySelectorAll('#tasks li').length, 0, 'Whitespace is not a task — nothing should have been added');
assertEqual(tasks.length, 0, 'and nothing should have reached the array either, got ' + tasks.length);
_input.value = '  Check tyre stock  ';
_form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
assertEqual(tasks.length, 1, 'A padded but real title should still be accepted');
assertEqual(tasks[0].title, 'Check tyre stock', 'Store the trimmed title, got ' + JSON.stringify(tasks[0].title));
'''},
                    {"name": "Clicking a row toggles it, before and after a re-render", "code": r'''
tasks.length = 0;
render();
var _input = document.querySelector('#new-task');
var _form = document.querySelector('#task-form');
_input.value = 'Sweep bay 2';
_form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
document.querySelector('#tasks li').click();
assert(document.querySelector('#tasks li').classList.contains('done'), 'A click should mark the row done');
assertEqual(tasks[0].done, true, 'and the flag in the array should be true, got ' + tasks[0].done);
document.querySelector('#tasks li').click();
assert(!document.querySelector('#tasks li').classList.contains('done'), 'Clicking again should clear it — the handler must still fire on the row the last render built');
assertEqual(tasks[0].done, false, 'and the flag should be back to false, got ' + tasks[0].done);
'''},
                    {"name": "Remaining counts what is not done", "code": r'''
tasks.length = 0;
render();
var _input = document.querySelector('#new-task');
var _form = document.querySelector('#task-form');
['Order oil filters', 'Check tyre stock', 'Sweep bay 2'].forEach(function (title) {
  _input.value = title;
  _form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
});
assertEqual(document.querySelector('#remaining').textContent.trim(), '3', 'Three open tasks should show 3, got ' + document.querySelector('#remaining').textContent.trim());
document.querySelectorAll('#tasks li')[1].click();
assertEqual(document.querySelector('#remaining').textContent.trim(), '2', '#remaining should fall to 2 when one is marked done, got ' + document.querySelector('#remaining').textContent.trim());
document.querySelectorAll('#tasks li')[1].click();
assertEqual(document.querySelector('#remaining').textContent.trim(), '3', 'and rise again when it is unmarked, got ' + document.querySelector('#remaining').textContent.trim());
'''},
                ],
            }],
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
            "read": [
                {
                    "title": "The spinner that never stopped",
                    "minutes": 14,
                    "body": r'''
Type `fail` into this module's book search and press *Search*. The page says
*Searching...* and keeps saying it. No error appears, the console is empty, the button
still works, and pressing it again produces the same word. The request finished thirty
milliseconds after it was sent: the catalogue answered, with status 500 and a body that
says it is having a bad day, and the code that sent the request did this with the answer:

```text
if (response.ok) {
  renderBooks(payload.books);
  loadingEl.hidden = true;
}
```

There is no `else`. On a good answer the spinner comes down; on a bad one nothing runs,
so it stays up, and a paragraph that was honest a moment ago has become a lie. Nothing is
broken in the sense a debugger would show. The function did what it was told, and what it
was told had a gap in it.

Every bug in this module has that shape: a request has more outcomes than the code has
branches, and the outcomes without branches are the ones the user sees. This reading
counts the outcomes, follows what the browser does between sending and receiving, and
derives from that the four states the lab's `showState` has to draw.

## A value that is not there yet

`fetch(url)` cannot return the response, because the response does not exist when `fetch`
returns. The request has left the machine, the answer is somewhere on the network, and
the function has to hand its caller something to hold in the meantime. What it hands back
is a promise: an object standing for a value that will arrive later, or for a failure
that will arrive instead. A promise starts pending, and then exactly once it *settles* —
fulfilled with a value, or rejected with a reason — and after that it never changes again.

Code can be attached to the settling: `p.then(onValue, onReason)`. `await` is the same
thing with the plumbing hidden. Inside an `async` function,
`var response = await fetch(url)` stops the function at that line, hands control back to
whoever called it, and resumes when the promise settles — with the value in `response` if
it was fulfilled, or by *throwing* the reason if it was rejected. That last part is what
makes `try` / `catch` work with `await`: a rejection becomes an ordinary exception at the
line of the `await`, and nowhere else. Wrap that line in a `try` and the `catch` runs.
Leave it out and the rejection escapes the function, becomes an *unhandled promise
rejection* in the console, and the spinner stays up.

## Where the pause goes

*Stops the function* hides a sequence that decides the lab's second check, so follow it.
JavaScript runs one thing at a time. A script or a handler runs to its end without
interruption, and only when it returns does the browser look for the next thing to run.
There are two queues of next things. *Microtasks* — the continuations of promises that
have settled — are drained first, all of them, before anything else is considered.
*Tasks* — a timer firing, a click, data arriving from the network — are taken one at a
time, after the microtasks are gone. An `async` function that reaches an `await` returns
to its caller at once, handing back its own promise, and its continuation is queued as a
microtask when the awaited promise settles.

```js
async function searchBooks() {
  console.log('2  showState(loading) runs at once, before the first await');
  var response = await new Promise(function (resolve) {
    setTimeout(function () { resolve({ ok: true, status: 200 }); }, 0);
  });
  console.log('5  the await resumed with status ' + response.status);
}

console.log('1  submit handler starts');
searchBooks();
console.log('3  searchBooks returned a promise; the handler carries on');
Promise.resolve().then(function () { console.log('4  a microtask queued after the call'); });
```

Line 2 prints before line 3: the async function ran as ordinary synchronous code up to
its first `await`, so a `showState('loading')` placed before the `await` has changed the
page before the submit handler even finishes. Move it after the `await` and it runs at
line 5, with the answer already in hand — the spinner appears for one frame at the exact
moment it is no longer needed. Line 4 prints before line 5 even though the timer was set
to zero, because the timer is a task and the microtask queue is drained before the
browser takes the next task; only then does the timer fire, resolve the promise, and
queue the continuation. The lab's stand-in waits thirty milliseconds instead of zero,
which changes nothing about the order.

## What a server can and cannot say

The lab's `window.fakeFetch` is a stand-in, so it is worth seeing what it stands in for.
On the other side of a real request is a function like this one, and what matters is
what it produces for each of three queries:

```python
CATALOGUE = ["Eloquent JavaScript", "Refactoring UI", "Inclusive Components"]


def handle(query):
    """The server side of GET /api/books?q=... — returns (status, body)."""
    try:
        if query == "fail":
            raise RuntimeError("the catalogue is having a bad day")
        hits = [title for title in CATALOGUE if query.lower() in title.lower()]
        return 200, {"books": hits}
    except RuntimeError as err:
        return 500, {"error": str(err)}


for q in ["script", "zzz", "fail"]:
    status, body = handle(q)
    print(f"q={q!r:<9} -> {status} {body}")
```

All three lines carry a status and a body. Even `fail` does: the exception was caught by
the server's framework — the `except` here is the toy version of that — and written out
as a 500 with a message. In all three cases bytes came back down the wire, so in all
three cases the promise from `fetch` is *fulfilled*, and what tells them apart is
`response.ok`, which is true exactly when the status is in the 200s. A 500 is an answer.
It is bad news, but it arrived.

What rejects is the case where this function never ran, or its answer never arrived: the
name did not resolve, the connection dropped halfway, the browser blocked the request
before it left. The lab's stand-in calls that case `boom` and rejects with
`TypeError('Failed to fetch')`, which is the error Chrome raises for a dropped
connection, with no status attached because there was no response to take one from. So the promise answers
one question — did an answer arrive — and `ok` answers a second — was it good — and
`response.json()` answers a third — what did it say. That last one is a promise as well,
because the body streams in after the headers and reading it to the end takes its own
time, which is why it gets its own `await`.

Look at the middle line again. `zzz` matched nothing, and the server said so with a 200
and an empty list. That is not a fault. It is information, and it is the outcome that is
easiest to leave without a branch, because fixture data always has something in it.

## Four outcomes, one function

The branches now write themselves from those three questions. The `await` throws: no
answer, so *error*, with a message about the connection. The answer is not `ok`: *error*
again, with the status number in the message, because a 404 and a 500 ask the person to
do different things. The answer is `ok` and holds zero books: *empty*. The answer is `ok`
and holds books: *success*. And from the moment the request goes out until one of those
is reached: *loading*. The lab folds the two error branches into one state that differs
only in its message, which leaves the four the module is named for.

Each state is a different set of elements showing — `#loading`, `#error`, `#empty` and
the results list. Hiding and showing them at each site in `searchBooks` that reaches a
state is how the opening bug happens: one site forgot one element. The alternative is one
function that owns `hidden`:

```text
function showState(name, message) {
  uiState = name;
  loadingEl.hidden = name !== 'loading';
  emptyEl.hidden = name !== 'empty';
  errorEl.hidden = name !== 'error';
  errorEl.textContent = name === 'error' ? String(message || 'Something went wrong.') : '';
  if (name !== 'success') { resultsEl.textContent = ''; }
}
```

Each element's visibility is one comparison against `name`, so there is no path through
the function that leaves two showing or none. This is the previous module's idea again —
the picture is drawn from one value rather than patched — with `name` as the state.
Every exit from `searchBooks` calls it, so the spinner comes down on every path,
including the two failures, which is the sentence the opening bug violated. Here is the
whole function against a stand-in with the lab's four behaviours, traced through four
queries one after another so the transitions can be read:

```js
var BOOKS = [
  { id: 1, title: 'Eloquent JavaScript', author: 'Marijn Haverbeke' },
  { id: 4, title: 'Refactoring UI', author: 'Adam Wathan' }
];

function fakeFetch(query) {
  return new Promise(function (resolve, reject) {
    setTimeout(function () {
      if (query === 'boom') { reject(new TypeError('Failed to fetch')); return; }
      if (query === 'fail') {
        resolve({ ok: false, status: 500, json: function () { return Promise.resolve({ error: 'bad day' }); } });
        return;
      }
      var hits = BOOKS.filter(function (b) { return b.title.toLowerCase().indexOf(query.toLowerCase()) !== -1; });
      resolve({ ok: true, status: 200, json: function () { return Promise.resolve({ books: hits }); } });
    }, 0);
  });
}

var uiState = 'idle';

function showState(name, message) {
  uiState = name;
  console.log('    showState(' + name + (message ? ', "' + message + '"' : '') + ')');
}

async function searchBooks(query) {
  showState('loading');
  var response;
  try {
    response = await fakeFetch(query);
  } catch (err) {
    showState('error', 'Could not reach the catalogue.');
    return [];
  }
  if (!response.ok) {
    showState('error', 'The catalogue answered with status ' + response.status + '.');
    return [];
  }
  var payload = await response.json();
  var books = payload.books || [];
  if (books.length === 0) {
    showState('empty');
    return [];
  }
  showState('success');
  return books;
}

async function run() {
  var queries = ['java', 'zzz', 'fail', 'boom'];
  for (var i = 0; i < queries.length; i++) {
    console.log('search "' + queries[i] + '"');
    var books = await searchBooks(queries[i]);
    console.log('    -> ' + books.length + ' book(s) rendered, uiState ' + uiState);
  }
}

run();
```

Every search opens with `loading` and closes with exactly one of the other three. The
`fail` search shows the 500 in its message, because `response.status` was there to read;
the `boom` search cannot, because the `catch` holds an error and no response. The four
searches run one after another on purpose, so that the log reads in order; a real page
would not chain them, and the module's timing exercise counts what chaining costs.

## An error that announces itself

`#error` is `<p id="error" role="alert" hidden>` in the read-only HTML, and the role is
doing work. It marks a live region of the assertive kind: when its contents change, a
screen reader interrupts what it was saying and reads the new text, without moving focus,
so the person keeps their place in the search field and can retype. That is why the
element sits in the markup from the start, empty and hidden, and is filled in by
`showState` rather than created when needed — a live region created and populated in the
same moment is announced unreliably across screen readers. It is also why `showState`
empties it for every state that is not `error`: the sixth check runs a failing search and
then a successful one and expects the old message gone, because a message lingering under
a list of results is the spinner's lie again.

## The mistake, and why it is tempting

The first is the opening bug: branches for the happy path and nothing else. It is
tempting because during development the server is healthy, every manual test succeeds,
and the `else` is code for a case you never see happen. Write `showState` first and route
every exit through it, and the case you never see is handled by construction.

The second is subtler and looks like caution. Wrap the whole body of `searchBooks` in one
`try`, so that anything at all that goes wrong is caught. Then a bug in `renderBooks` —
`book.tittle`, say — is caught with everything else and reported as *Could not reach the
catalogue. Check the connection*, which sends the person to restart their router over
your typo and hides the stack trace from you. Catch narrowly. The `try` holds the one
line that can reject for a network reason; a genuine bug should reach the console as one.

## Where this stops holding

The stand-in answers in a fixed thirty milliseconds, so two searches always settle in the
order they were sent. Real networks promise no such thing. Type `a`, then `ab`: if the
answer to `a` takes longer, it arrives last and overwrites the results for `ab`, leaving
a screen that shows the wrong list under the right query. `showState` cannot see this; it
draws whatever it is told last. The fix is to number each request and ignore any answer
that is not from the latest, or to cancel the earlier one with an `AbortController` — and
an aborted `fetch` rejects with an `AbortError`, which the `catch` must not report as a
connection failure. `fetch` has no timeout either: a server that never answers leaves the
promise pending forever, with the spinner honest but eternal, and a timeout is another
`AbortController` on a timer.

`response.json()` is its own point of failure. A 200 whose body is an HTML login page — a
hotel's captive portal — rejects at the parse, outside the lab's `try`. A cross-origin
request blocked by CORS rejects with the same `TypeError` as a dropped connection, with
no status to show. And `ok` is exactly 200 to 299: a 304 is not ok, a redirect has
already been followed before you see anything, and a 204 is ok with no body to parse.

## In the lab

*Book search against a flaky API* gives you a read-only `index.html` — the form, the
three state paragraphs, the results list, and `window.fakeFetch` with its five-book
catalogue and two misbehaving queries — and an `app.js` with four stubs: `showState`,
`renderBooks`, `searchBooks` and the submit handler. Seven checks read it back: two rows
with titles, authors and `data-id` for `js`; `#loading` visible and the old results
cleared *before* the search is awaited — the check the event-loop trace was written for;
the empty state for `zzz`, with the error hidden; an error message mentioning `500` for
`fail`; a settled promise rather than a throw for `boom`, with the error showing and the
spinner gone; the previous error cleared after the form is submitted for `meyer`; and
all five books for a query of nothing at all.
''',
                },
                {
                    "title": "Chains, bodies and origins",
                    "minutes": 11,
                    "body": r'''
Most of the asynchronous code you will read was written before `await` existed or by
someone who prefers not to use it, and it is built out of `.then`. The two are the same
machinery with different punctuation, and the translation between them is worth having,
because the places a chain goes wrong are not the places an `await` goes wrong. This
reading is the chain, the second half of `fetch` — sending rather than reading — and the
rule that decides whether a request to somebody else's server is allowed to happen at
all.

## Handing over a function to be called later

```js
setTimeout(function () { console.log('this line runs second'); }, 2000);
console.log('this line runs first');
```

That is the whole of asynchrony in miniature. `setTimeout` does not wait; it files a
function away to be run later and returns immediately, and the script carries on to its
end. Reading a file, asking a server and waiting for a timer are the same shape: the
browser refuses to freeze the page while something slow happens, so the slow thing takes
a function and calls it when there is something to say.

## A chain is a sequence of small handovers

`p.then(fn)` registers `fn` to run when `p` settles, and — this is the part that makes
chaining work — it **returns a new promise**. What that new promise settles with depends
on what `fn` returned:

```js
function later(value, ms) {
  return new Promise(function (resolve) { setTimeout(function () { resolve(value); }, ms); });
}

later(2, 10)
  .then(function (n) { return n * 3; })
  .then(function (n) { console.log('a value came back: ' + n); return later(n + 1, 10); })
  .then(function (n) { console.log('a promise came back, and its value arrived: ' + n); })
  .then(function (n) { console.log('nothing came back, so this step receives: ' + n); });

console.log('the chain is only set up here; this line runs first');
```

The output reads:

```text
the chain is only set up here; this line runs first
a value came back: 6
a promise came back, and its value arrived: 7
nothing came back, so this step receives: undefined
```

Three rules, one per line. Return an ordinary value and the next step receives it. Return
a **promise** and the chain waits for it and passes on its value — which is what makes
`fetch(url).then(function (r) { return r.json(); })` work, since `r.json()` is itself a
promise. Return nothing and the next step receives `undefined`; that last line is the
commonest defect in a chain, because a function body with braces that ends without a
`return` looks finished.

## One catch for the whole chain

```js
later(1, 5)
  .then(function () { throw new Error('the body would not parse'); })
  .then(function () { console.log('this step is skipped entirely'); })
  .catch(function (err) { console.log('caught at the end of the chain: ' + err.message); })
  .finally(function () { console.log('finally runs whichever way it went'); });
```

A rejection — or a thrown error, which becomes one — skips every `.then` after it until
it reaches a `.catch`. So one `.catch` at the end covers every step above it, exactly the
way one `try` block covers every line inside it. `.finally` runs on both paths and is
where a spinner comes down.

The translation is now mechanical:

| Chain | `async` / `await` |
|---|---|
| `p.then(fn)` | `var v = await p;` then the body of `fn` |
| returning a promise from a `.then` | `await` on the next line |
| `.catch(fn)` | `catch (err) { ... }` around the awaits |
| `.finally(fn)` | `finally { ... }` |

`await` is the version to write. The chain is the version to be able to read, and the one
you need when there is no `async` function to be inside.

## Sending, not only reading

`fetch(url)` with one argument makes a `GET` with no body. The second argument is where
everything else goes:

```js
const response = await fetch("/api/todos", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ title: "Order brake pads" }),
});
```

Three things are doing work. `method` chooses the verb. `body` must be a string — `fetch`
will not serialise an object for you, and handing it one gives the server the characters
`[object Object]`, which is the same trap `localStorage` sets. And the `Content-Type`
header is how the server knows to parse those characters as JSON rather than as form
fields; leave it out and a framework that reads by content type finds an empty body and
reports a validation error about a field you definitely sent.

The response comes back the same way it does for a `GET`: check `response.ok`, then
`await response.json()`. A successful create answers `201`, not `200`, and `ok` covers
both.

## The wall between origins

A page served from `https://shop.example` fetches `https://api.other.com/books` and the
console says *blocked by CORS policy*. Nothing is wrong with your code. The browser
enforces a rule that a page may not read a response from a different **origin** — scheme,
host and port, all three — unless that server says it may, by sending
`Access-Control-Allow-Origin` naming your page's origin or `*`. The request often reaches
the server and runs; what is blocked is your page reading the answer.

Two consequences follow. The failure surfaces as a rejected promise with a `TypeError`
and no status code, indistinguishable from a dropped connection, because there was no
response your code was allowed to see. And the fix is not on your side — it is a header
the other server has to send, which is why the answer is either "ask them" or "call it
from your own backend, where the rule does not apply". A browser is the only client that
enforces it; `curl` from a terminal never sees it.

## The mistake, and why it is tempting

The forgotten `return` in a `.then`, and its bigger sibling: the forgotten `return` on the
whole chain. A function that builds a chain and does not return it hands its caller
nothing to wait on, so the caller carries on as though the work were finished, and a
rejection in that chain has no `catch` anywhere above it — it becomes an *unhandled
promise rejection* in the console, several seconds after the line that caused it. It is
tempting because the code works whenever the request succeeds, which during development
is every time.

The same shape appears with `await`: calling an `async` function without awaiting it or
returning it starts the work and abandons the result.

## Where this stops holding

`Promise.all([a, b, c])` waits for all three and rejects as soon as any one of them does,
throwing away the two that succeeded; `Promise.allSettled` waits for all three and reports
each outcome, which is what you want when a partial answer is still useful. This module's
timing exercise counts what running requests together buys.

An `async` function always returns a promise, so a `try`/`catch` **inside** it does not
protect its caller from a rejection thrown after the awaits, and a `catch` in the caller
is still owed. `fetch` sends no cookies to another origin unless you ask with
`credentials: 'include'`, and asking makes the CORS rules stricter rather than looser.
And `JSON.stringify` drops `undefined` values and functions, so a field you set to
`undefined` does not arrive as null — it does not arrive.

## In the lab

*Load and render data* is the smallest complete round trip: a button, a stand-in for
`fetch` that answers after 200ms, and three things to get right. `loadUsers()` is `async`
and returns the array. The click handler puts *Loading…* on screen before it awaits,
renders one row per user, and finishes with a count. And the failure path — a response
whose `ok` is false — leaves the list empty and says so, instead of leaving the word
*Loading* on the page forever.
''',
                },
                {
                    "title": "The request and the response",
                    "minutes": 12,
                    "body": r'''
`window.fakeFetch` in this module's lab answers in thirty milliseconds from an array in
memory, and it is shaped the way it is because of what it stands in for. On the other
side of a real `fetch` there is a second computer, a text protocol both machines agree on,
and a function someone wrote that turns one message into another. This reading is that
protocol — enough of it to read a network panel, to choose a status code on purpose, and
to write the handler the next lab asks for.

## Two messages

Every backend does the same job: receive a **request**, do some work, send a **response**.
A request has four parts, in this order.

```text
POST /todos HTTP/1.1              <- method and path
Host: api.example.com             <- headers: metadata about the message
Content-Type: application/json
                                  <- a blank line, which ends the headers
{"title": "Order brake pads"}     <- the body, optional
```

A response mirrors it exactly, with a status line where the request had a method line:

```text
HTTP/1.1 201 Created
Content-Type: application/json

{"id": 7, "title": "Order brake pads", "done": false}
```

That is all `fetch` is doing. `response.status` is the number on the first line,
`response.ok` is whether that number is in the 200s, and `response.json()` parses the
body — which is why it is a separate promise: the headers arrive first and the body
streams in after them.

## Nothing is remembered

HTTP is **stateless**: the server keeps no memory of the conversation between one request
and the next. Two requests from the same person, one second apart, arrive as two
unrelated messages. Everything that has to survive between them travels in the request
itself — a cookie, an `Authorization` header carrying a token — or lives in a database
the server reads on each one.

That is a constraint and also the reason the web scales: any server in a pool can answer
any request, because none of them is holding anything the others lack.

## The verbs

| Method | Meaning | Body? | Safe to repeat? |
|---|---|---|---|
| `GET` | read something | no | yes, and it changes nothing |
| `POST` | create something new | yes | no — a second one creates a second thing |
| `PUT` | replace something entirely | yes | yes |
| `PATCH` | change part of something | yes | usually |
| `DELETE` | remove something | no | yes |

Two properties are hiding in that last column. A method is **safe** when it changes
nothing — only `GET` is. It is **idempotent** when doing it twice leaves the world as it
was after doing it once: `DELETE /todos/7` twice ends with the todo gone both times, and
`PUT` writes the same four fields both times, while `POST` twice creates two rows. That
is not pedantry; it decides whether a client, a proxy or a phone with a flaky connection
may retry a request it is not sure arrived.

## The status code

| Code | Meaning | When |
|---|---|---|
| `200 OK` | here is your data | a successful read or update |
| `201 Created` | made it | a successful `POST`, with the new thing in the body |
| `204 No Content` | done, nothing to say | a successful `DELETE` |
| `301` / `302` | it moved | redirects |
| `400 Bad Request` | this request makes no sense | validation failed |
| `401 Unauthorized` | who are you? | missing or bad credentials |
| `403 Forbidden` | I know who you are, and no | authenticated but not permitted |
| `404 Not Found` | no such thing | wrong path, or an id that is not there |
| `405 Method Not Allowed` | not that verb, here | `DELETE /todos` on the collection |
| `409 Conflict` | the current state forbids it | buying more stock than exists |
| `500 Internal Server Error` | we crashed | your bug, not the caller's |

The rule of thumb is worth memorising because it decides who goes and fixes it: **4xx
means the client got it wrong, 5xx means the server did**. And the first digit is enough
to know that much:

```python
def classify(code):
    """Which family a status code belongs to, and whose problem it is."""
    return {
        1: ("informational", "nobody yet"),
        2: ("success", "nobody"),
        3: ("redirect", "the client, by following"),
        4: ("client error", "the client"),
        5: ("server error", "the server"),
    }.get(code // 100, ("unknown", "nobody knows"))


def route(method, path):
    """The table below, as code: a noun in the path, the verb in the method."""
    parts = [p for p in path.split("/") if p]
    if parts == ["books"]:
        return {"GET": 200, "POST": 201}.get(method, 405)
    if len(parts) == 2 and parts[0] == "books":
        if not parts[1].isdigit():
            return 404
        return {"GET": 200, "PUT": 200, "DELETE": 204}.get(method, 405)
    return 404


for method, path in [("GET", "/books"), ("POST", "/books"), ("DELETE", "/books"),
                     ("GET", "/books/42"), ("DELETE", "/books/42"),
                     ("GET", "/books/forty-two"), ("GET", "/authors")]:
    code = route(method, path)
    name, whose = classify(code)
    print(f"{method:<7}{path:<18}-> {code} {name:<13} whose fault: {whose}")
```

Read the two 404s at the bottom against the 405 above them. `DELETE /books` is a path the
server knows with a verb it does not support there, and 405 says so precisely — the caller
has the right resource and the wrong method. `GET /books/forty-two` and `GET /authors` are
paths the server has nothing at. Answering 404 to all three would be true and useless; the
distinction is the difference between "you asked the wrong thing" and "you asked the right
thing the wrong way".

## REST is a naming convention

```text
GET    /books                             list them
POST   /books                             create one
GET    /books/42                          one of them
PUT    /books/42                          replace it
DELETE /books/42                          remove it
GET    /books?author=le+guin&sort=title   filter and order the listing
```

The resources are **nouns** and the action is already in the method, which is why
`GET /getBooks` and `POST /deleteBook` are the shapes to avoid — they put a verb in the
path and then need a second convention to say what the method meant. A **path parameter**
identifies one resource; a **query parameter** filters, sorts or pages a collection. Both
of those are visible in the URL, so neither is a place for anything private.

## The mistake, and why it is tempting

Using `GET` for something that changes state — `GET /books/42/delete`, reached from a
link. It is tempting because a link is the easiest thing to build and it works the first
time you click it. Then a crawler follows every link on the page, or the browser
prefetches one on hover, or a proxy caches the response and serves it to somebody else,
and rows disappear with nobody having pressed anything. `GET` is defined as safe, and the
whole infrastructure between your page and the server is entitled to act on that promise.
Anything that changes state is a `POST`, `PUT`, `PATCH` or `DELETE`.

## Where this stops holding

Plenty of real APIs answer `200` with `{"error": ...}` in the body, so `response.ok` is
true and the request failed — which is why an integration starts by reading the API's own
documentation rather than assuming the conventions here. `ok` is exactly 200 to 299: a
`304 Not Modified` is not ok even though nothing went wrong, a redirect has already been
followed before your code sees anything, and a `204` is ok with no body, so calling
`.json()` on it throws.

The literal text above is HTTP/1.1. HTTP/2 and HTTP/3 send the same methods, paths,
headers and status codes in a compressed binary framing, so everything in this reading
holds and none of it is what goes down the wire. And REST is a set of conventions, not a
specification anyone validates — which is what makes them worth following, since nothing
enforces them for you.

## In the lab

*Build a REST handler* is that routing table as one function and no framework:
`handle_request(method, path, body)` returning a `(status, data)` pair. `GET /todos`
lists, `POST /todos` creates or rejects a missing title with 400, `GET`, `PATCH` and
`DELETE` on `/todos/<id>` each find the row or 404, an unknown path is 404, and a known
path with an unsupported verb is 405. Seven checks call it directly with each of those.
''',
                },
                {
                    "title": "What a framework does for you",
                    "minutes": 11,
                    "body": r'''
The `handle_request(method, path, body)` you write in this module's REST lab is not a
teaching stand-in for a framework. It **is** the part of a framework that matters, with
the plumbing removed. A framework parses the raw bytes into a method, a path and a decoded
body, looks your function up in a table, calls it, and turns whatever you returned back
into bytes. This reading is that claim made concrete, and then the ring of things
production adds around it — the ones that are nobody's favourite work and are the
difference between a program and a service.

## Thirty lines of framework

```python
class MicroApp:
    """A route table and a lookup. That is the part a framework does for you."""

    def __init__(self):
        self.routes = {}

    def route(self, method, path):
        def register(fn):
            self.routes[(method, path)] = fn
            return fn
        return register

    def get(self, path):
        return self.route("GET", path)

    def post(self, path):
        return self.route("POST", path)

    def handle(self, method, path, body=None):
        fn = self.routes.get((method, path))
        if fn is None:
            known_path = any(p == path for _, p in self.routes)
            return (405 if known_path else 404), {"error": "no handler"}
        return fn(body)


app = MicroApp()
TODOS = []


@app.get("/todos")
def list_todos(body):
    return 200, TODOS


@app.post("/todos")
def create_todo(body):
    title = (body or {}).get("title")
    if not title:
        return 400, {"error": "title is required"}
    todo = {"id": len(TODOS) + 1, "title": title, "done": False}
    TODOS.append(todo)
    return 201, todo


print(app.handle("POST", "/todos", {"title": "Order brake pads"}))
print(app.handle("POST", "/todos", {}))
print(app.handle("GET", "/todos"))
print(app.handle("DELETE", "/todos"))
print(app.handle("GET", "/nope"))
```

```text
(201, {'id': 1, 'title': 'Order brake pads', 'done': False})
(400, {'error': 'title is required'})
(200, [{'id': 1, 'title': 'Order brake pads', 'done': False}])
(405, {'error': 'no handler'})
(404, {'error': 'no handler'})
```

`@app.get("/todos")` looks like magic and is a dictionary write. `app.get(path)` returns
`register`, Python calls `register` with the function defined underneath it, `register`
files that function under the key `("GET", "/todos")` and hands it straight back
unchanged. That is the entire mechanism. The `if` chain in the lab's `handle_request`
becomes a table lookup, and the 404-versus-405 distinction, which the chain expresses with
a `return` at the end of a block, becomes a second question asked about the same table.

## The same API, twice

Two frameworks, side by side. Neither of them runs in this sandbox, so read them rather
than pressing anything.

```text
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
TODOS = []

class TodoIn(BaseModel):
    title: str

@app.get("/todos")
def list_todos():
    return TODOS

@app.post("/todos", status_code=201)
def create_todo(todo: TodoIn):
    new = {"id": len(TODOS) + 1, "title": todo.title, "done": False}
    TODOS.append(new)
    return new

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int):
    for t in TODOS:
        if t["id"] == todo_id:
            return t
    raise HTTPException(404, "not found")
```

```text
const express = require("express");
const app = express();
app.use(express.json());

const TODOS = [];

app.get("/todos", (req, res) => res.json(TODOS));

app.post("/todos", (req, res) => {
  if (!req.body.title) return res.status(400).json({ error: "title is required" });
  const todo = { id: TODOS.length + 1, title: req.body.title, done: false };
  TODOS.push(todo);
  res.status(201).json(todo);
});

app.listen(3000);
```

Same verbs, same paths, same status codes, same shape as the toy above. What each adds is
worth naming. FastAPI reads the type annotations: `todo: TodoIn` means the body is parsed
and validated before your function is entered, and `todo_id: int` means the path segment
is converted, so `/todos/abc` never reaches you. It generates interactive documentation at
`/docs` from those same annotations. Express is thinner: `express.json()` is middleware
you opt into to get a parsed `req.body` at all, and validation is yours to write, which is
why the check is there in the handler. Flask sits close to Express in that respect and in
Python. Pick the language the team already writes; the shape does not change.

## What production adds around this

- **Configuration from the environment.** Anything that differs between your laptop and
  the server — `DATABASE_URL`, `SECRET_KEY`, `PORT` — is read at start-up with
  `os.environ` or `process.env`. A local `.env` file supplies them in development and
  never enters version control.
- **Logging.** Every request and every error, with a timestamp and enough identity to
  find one request among thousands. At two in the morning the logs are the only witness.
- **A health check.** `GET /health` returning 200 and almost nothing, so a load balancer
  can tell a live process from a hung one and stop routing to the hung one.
- **A reverse proxy.** nginx, Caddy or the platform's own router sits in front,
  terminates HTTPS and forwards plain HTTP to your app, so certificates are one concern
  instead of one per service.
- **A container.** A `Dockerfile` lists the steps — a base image, copy the code, install
  the dependencies, the command to run — and the resulting image carries the app and its
  exact dependency versions together. *Works on my machine* becomes *ships as my machine*.
- **A host.** Platforms take a repository or an image, hold the environment variables in
  their own settings, and give you a URL. Deployment becomes a push.

## The mistake, and why it is tempting

Writing configuration into the source: the database URL as a constant, the API key in a
string. It is tempting because it works instantly, the file is already open, and adding a
second way to read a value feels like ceremony for one line. Two costs arrive later. A
secret committed once is in the repository's history permanently, and rotating it is the
only real fix. And the moment there is a second environment, the two differ by an edit
nobody wrote down, so the staging deploy quietly reads the production database. Read it
from the environment on day one, while it costs one line.

## Where this stops holding

A framework's validation runs before your code and answers with **its** convention, not
yours: FastAPI rejects a malformed body with `422`, where the handler you write by hand
returns `400`. If a client depends on the number, the framework has changed your contract
without asking.

`uvicorn main:app --reload` and `flask run` are development servers — single-worker,
verbose, and explicitly not for production, where a process manager runs several workers
behind the proxy. A health check that returns 200 without touching anything reports that
the process is alive and nothing about whether it can serve, so an app whose database
connection has died keeps receiving traffic. And a container fixes your dependencies, not
your data: the database lives outside it, because the image is thrown away and rebuilt on
every deploy.

## In the lab

*A bookstore API, cleanly split* is the last of these: three files, with `db.py` owning
the schema, `api.py` owning the routing and the SQL, and `main.py` doing nothing but a
demonstration run. `handle_request(conn, method, path, body)` keeps the shape from the
earlier lab and adds what a real service needs — validation of every field on both `POST`
and `PUT`, a filter passed as a **parameter** rather than glued into the SQL, and a
`purchase` sub-route that answers `409` when the stock will not cover the order.
''',
                },
            ],
            "quiz": [{
                "title": "What settles, when, and what it means",
                "minutes": 7,
                "questions": [
                    {
                        "q": "`console.log('a')`, then `setTimeout(() => console.log('b'), 0)`, then `Promise.resolve().then(() => console.log('c'))`, then `console.log('d')`. What is printed?",
                        "opts": [
                            "a d c b",
                            "a b c d",
                            "a d b c",
                            "a c d b",
                        ],
                        "a": 0,
                        "why": r"""
Synchronous code runs to completion first, so `a` then `d`. Then the microtask queue
drains — that is where a resolved promise's callback waits — giving `c`. Timers are a
separate, later queue, so `b` comes last even at zero milliseconds. `setTimeout(fn, 0)`
does not mean *now*; it means *after the current task and everything its microtasks
queue*. This is also why an `await` never lets other synchronous code interleave halfway
through a statement: the continuation is a microtask, not a thread.
""",
                    },
                    {
                        "q": "`await fetch(url)` where the server replies 500. What happens?",
                        "opts": [
                            "The promise rejects, so the `catch` block runs",
                            "The promise resolves; the response has `ok === false` and `status === 500`",
                            "`fetch` retries the request once before rejecting",
                            "The promise never settles and the await hangs",
                        ],
                        "a": 1,
                        "why": r"""
`fetch` rejects only when there was no answer at all — DNS failure, a dropped
connection, a blocked cross-origin request. A 500 is a completed round trip whose answer
happens to be bad news, so it resolves normally and hands you a response to inspect.
That split is why real code needs both halves: a `try`/`catch` around the await for the
no-answer case, and an `if (!response.ok)` after it for the bad-answer case. Leave out
the second and a 500 renders as an empty list — the server is on fire and the UI says
"no results".
""",
                    },
                    {
                        "q": "A search completes and matches nothing. Which of the four states is that?",
                        "opts": [
                            "Error — nothing came back",
                            "Empty — a successful answer that happens to contain no rows",
                            "Loading, until the user searches again",
                            "Success; the list simply renders zero rows",
                        ],
                        "a": 1,
                        "why": r"""
The request worked. The catalogue just has nothing matching, which is information, not a
fault. Calling it an error tells someone something is broken when nothing is, and
sending it down the success path renders an empty rectangle that is indistinguishable
from a spinner that never finished — the reader cannot tell whether to wait, retry, or
search for something else. Empty is the state that gets forgotten most often, because it
never shows up in the fixture data you developed against.
""",
                    },
                    {
                        "q": "Why does `showState('loading')` belong before the `await` rather than after it?",
                        "opts": [
                            "An async function runs synchronously up to its first `await`, so anything before it takes effect immediately",
                            "Because `await` may not be the first statement in a function body",
                            "It makes no difference — both run before the response arrives",
                            "Because `showState` is itself asynchronous and needs the head start",
                        ],
                        "a": 0,
                        "why": r"""
An `async` function is ordinary synchronous code until it reaches its first `await`;
that is the point where it returns a pending promise to its caller and the rest becomes
a continuation scheduled for later. So a call before the await has already run and
painted by the time the request goes out. Move it after and it runs when the response is
already in hand — the spinner appears for one frame at the exact moment it is no longer
needed, which reads as a flicker rather than as feedback.
""",
                    },
                    {
                        "q": "The error paragraph is `<p id=\"error\" role=\"alert\" hidden></p>`. What does `role=\"alert\"` buy?",
                        "opts": [
                            "It styles the message as an error",
                            "Content appearing in it is announced immediately, without focus moving",
                            "Keyboard focus jumps to the message when it appears",
                            "It stops the form from submitting while the message is showing",
                        ],
                        "a": 1,
                        "why": r"""
`role="alert"` marks an assertive live region: change its contents and a screen reader
interrupts whatever it was saying to read the new text. It deliberately does *not* move
focus, so the person keeps their place in the form and can carry on typing. This is why
the element sits in the markup from the start, empty and hidden, and is filled in later
rather than created on demand — a live region that is created and populated in the same
tick is announced unreliably across screen readers. Styling is entirely separate; the
`#error` rule in the stylesheet does that.
""",
                    },
                ],
            }, {
                "title": "Verbs, paths and status codes",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A `POST` that created a row should answer with which status?",
                        "opts": [
                            "`201 Created`, with the new row in the response body",
                            "`200 OK`, which covers every successful request",
                            "`204 No Content`, since the client already has what it sent",
                            "`301 Moved Permanently`, pointing at the new row",
                        ],
                        "a": 0,
                        "why": r"""
`201` says a new resource exists that did not before, and the body carries it — which
matters, because the server assigned the id and the client has no other way to learn it.
`200` is not wrong in the sense of breaking anything, and it throws that distinction away:
a client cannot tell a create from a read. `204` promises there is no body at all and
belongs to `DELETE`, where there is genuinely nothing left to return. And a `3xx` is a
redirect — an instruction to go and ask somewhere else, not a report that something was
made.
""",
                    },
                    {
                        "q": "`404 Not Found` says what, exactly?",
                        "opts": [
                            "There is nothing at that path, or nothing with that id",
                            "The server crashed part-way through building the response",
                            "You are authenticated, and not permitted to see it",
                            "The body was malformed and could not be parsed",
                        ],
                        "a": 0,
                        "why": r"""
404 is about the *thing being addressed*: the path names no route, or the route is right
and the id matches no row. Both cases are the caller looking for something that is not
there, which is why one code covers them. A crash while answering is `500`, and the
difference is who has to act — a 404 is fixed by asking for something else, a 500 by
fixing the server. A refusal from someone the server has identified is `403`, which is a
statement about permission rather than existence. And an unparseable body is `400`: the
address was fine and the message was not.
""",
                    },
                    {
                        "q": "A response comes back with a status in the 400s. Who goes and fixes it?",
                        "opts": [
                            "The client — the request was wrong, so the request changes",
                            "The server — a 4xx is raised when a handler throws",
                            "Neither: the 400s are redirects the browser follows itself",
                            "Both, since 4xx covers a failure on either side of the wire",
                        ],
                        "a": 0,
                        "why": r"""
The first digit is the whole answer: 4xx means the request was wrong and 5xx means the
server was, and that single fact decides which of two people opens an editor. An
unhandled exception in a handler produces `500`, not a 4xx — a framework catches it and
reports the family that means *our fault*. Redirects are the 300s, and they are followed
before your code sees anything. Splitting the blame between both sides is the tempting
answer and it is what the two families exist to avoid: the code is the server's opinion
about whose problem it is.
""",
                    },
                    {
                        "q": "Which request removes book 42, following the usual conventions?",
                        "opts": [
                            "`DELETE /books/42`",
                            "`POST /deleteBook?id=42`",
                            "`GET /books/delete/42`",
                            "`REMOVE /book42`",
                        ],
                        "a": 0,
                        "why": r"""
The path names a noun and the method supplies the verb, so the resource is `/books/42`
whatever you are doing to it and `DELETE` says what that is. Putting the verb in the path
needs a second convention to explain what the method meant, and then two of them disagree.
The `GET` version is the dangerous one rather than the ugly one: `GET` is defined as safe,
so a crawler, a link prefetcher or a caching proxy is entitled to follow it, and rows
vanish with nobody having pressed anything. And `REMOVE` is not an HTTP method; a server
that has never heard of a verb answers `501`.
""",
                    },
                    {
                        "q": "HTTP is stateless. What follows from that?",
                        "opts": [
                            "Anything that must survive between requests travels in the request or lives in a store",
                            "A connection has to be held open for as long as someone is using the site",
                            "Only `GET` may be used, since every other verb would need a memory of what came before it",
                            "Two requests from one person are guaranteed to reach the same server process",
                        ],
                        "a": 0,
                        "why": r"""
The server keeps no memory of the conversation, so each request has to carry or reference
whatever context it needs: a cookie, a token in an `Authorization` header, or an id that
sends the handler to a database. That is a constraint and also the reason the web scales
— any server in a pool can answer any request, because none of them holds anything the
others lack. Pinning a person to one server process is what statelessness frees you from
rather than something it promises. The connection is a separate matter again: one may be
reused for many requests as an optimisation, and the protocol never depends on it.
""",
                    },
                    {
                        "q": "`401` and `403` both refuse a request. What separates them?",
                        "opts": [
                            "`401` means the server does not know who you are; `403` means it does, and refuses",
                            "`401` is reserved for admin-only routes, and `403` covers every other refusal there is",
                            "`403` asks you to try again later, once the rate limit window has passed",
                            "They are two spellings of the same refusal, and either may be sent",
                        ],
                        "a": 0,
                        "why": r"""
`401` is about **authentication** — no credentials, or credentials the server could not
verify — and the useful response to it is to log in. `403` is about **authorisation** —
the server knows exactly who you are and this account may not have that thing — and
logging in again changes nothing. Sending the wrong one wastes the caller's time in a
specific way, by inviting a sign-in that cannot help. Neither is about rate limiting,
which has its own code, `429`, with a `Retry-After` header saying how long to wait.
""",
                    },
                    {
                        "q": "`GET /books?author=le+guin&sort=title` — what is the query string doing?",
                        "opts": [
                            "Filtering, sorting or paging a collection that is already identified",
                            "Identifying the single resource the request is about",
                            "Carrying credentials, which is what a query string is designed to be used for",
                            "Sending a body, for verbs that are not allowed to have one",
                        ],
                        "a": 0,
                        "why": r"""
The path says *which* resource — here, the collection `/books` — and the query refines
what comes back from it: which subset, in what order, which page. That division is why
`/books/42` is a path parameter and `?author=…` is not; one identifies, the other narrows.
The query string is emphatically not a place for credentials or anything else private: it
is part of the URL, so it ends up in browser history, in server access logs and in the
`Referer` header sent to the next site. And it is not a body — a `GET` has none, which is
part of what makes it safe to repeat.
""",
                    },
                ],
            }, {
                "title": "Frameworks, config and shipping",
                "minutes": 5,
                "questions": [
                    {
                        "q": "What does a web framework do that your own `handle_request` did not?",
                        "opts": [
                            "Parses the raw HTTP and routes to your function, then serialises what it returns",
                            "Writes the business logic, so the handlers become configuration rather than code",
                            "Replaces the database, holding the rows in memory between requests",
                            "Hosts the application, so no server or platform is needed",
                        ],
                        "a": 0,
                        "why": r"""
A framework owns the two edges: bytes in, turned into a method, a path and a decoded body;
and whatever your function returned, turned back into a status line, headers and bytes
out. The middle is yours, and it is the same `if` chain you wrote by hand — which is why
that lab is worth doing before meeting a framework rather than after. The routing table
is the visible difference: `@app.get("/todos")` writes your function into a dictionary
under the key `("GET", "/todos")`, and the dispatch is a lookup. Storage and hosting are
separate concerns that a framework has opinions about and does not provide.
""",
                    },
                    {
                        "q": "Where should a value like `DATABASE_URL` come from?",
                        "opts": [
                            "The environment, read at start-up",
                            "A constant near the top of the file",
                            "The README, copied in by hand",
                            "The client, sent with each request",
                        ],
                        "a": 0,
                        "why": r"""
Configuration is the set of values that differ between one machine and the next, so it
belongs outside the code that is identical on all of them — `os.environ` or `process.env`
at start-up, with a local `.env` file in development and the platform's own settings in
production. A constant in the source is the tempting one because it works immediately,
and it means every environment differs by an edit nobody recorded; if the value is a
secret it is also in the repository's history for good. Anything sent by the client is
worse still: a connection string the caller supplies is a connection string the caller
chooses.
""",
                    },
                    {
                        "q": "Why does a service expose a `GET /health` endpoint?",
                        "opts": [
                            "So a load balancer or a monitor can tell a live process from a hung one",
                            "So users have somewhere to sign in when the main page is unavailable",
                            "So the cache stays warm and the first real request is not the slow one to arrive",
                            "So the database connection pool is reset on a schedule by the prober",
                        ],
                        "a": 0,
                        "why": r"""
A load balancer needs a cheap, frequent question it can ask every instance — *are you
able to answer* — so that it stops sending traffic to a process that has hung or is still
starting up. That is the whole job, which is why the endpoint returns almost nothing and
touches almost nothing. The limit is worth knowing: a health check that returns 200
without consulting anything reports that the process is alive and says nothing about
whether it can serve, so an instance whose database connection has died keeps receiving
requests until the check is made to test something real.
""",
                    },
                    {
                        "q": "What does packaging an application into a container image get you?",
                        "opts": [
                            "The app and its exact dependency versions, running the same everywhere",
                            "A faster runtime, since the image is compiled ahead of time and then cached",
                            "Free hosting, because platforms run images at no charge",
                            "Automatic scaling, handled by the image format itself",
                        ],
                        "a": 0,
                        "why": r"""
The image is the app plus the interpreter plus every library at a pinned version, built
once and run unchanged on a laptop, in CI and in production. *Works on my machine*
becomes *ships as my machine*, and the class of bug caused by a different Python or a
library one minor version ahead disappears. Nothing is compiled and nothing is faster;
a container is process isolation, not a translation step. Scaling and hosting are what a
platform does with the image, and they cost what they cost. The one thing an image does
not carry is your data — the database lives outside it, because the image is thrown away
and rebuilt on every deploy.
""",
                    },
                    {
                        "q": "FastAPI sees `def create_todo(todo: TodoIn)` where `TodoIn` is a model. What does the annotation buy?",
                        "opts": [
                            "The body is parsed and validated before your function is entered",
                            "The handler runs in a thread pool, one request at a time per model",
                            "The response is cached, keyed on the fields the model declares",
                            "The database table is created from the model's field types",
                        ],
                        "a": 0,
                        "why": r"""
Declaring the shape once moves validation to the edge: a request missing `title`, or
sending a number where a string was declared, is refused before a line of your code runs,
and the same declaration generates the interactive documentation at `/docs`. The catch is
worth knowing before a client depends on it — the framework answers `422 Unprocessable
Entity` for that failure, where a handler you write by hand returns `400`, so adopting a
framework can change a contract you thought you owned. Persistence is a separate library's
job; a model that describes a request body creates no tables.
""",
                    },
                ],
            }],
            "blanks": {
                "title": "Four outcomes, one function",
                "minutes": 9,
                "caption": "app.js — five holes",
                "lang": "js",
                "brief": r'''
`searchBooks` in full, with the five decisions taken out. Each hole is a place where
the wrong choice still produces a function that works perfectly against a fast, healthy
server and misleads the user the first time the server is neither.
''',
                "listing": r'''async function searchBooks(query) {
  showState('loading');

  var response;
  try {
    response = ___ window.fakeFetch('/api/books?q=' + ___(query));
  } catch (err) {
    showState('error', 'Could not reach the catalogue. Check the connection and try again.');
    return [];
  }

  if (!response.___) {
    showState('error', 'The catalogue answered with status ' + response.status + '.');
    return [];
  }

  var payload = await response.___();
  var books = (payload && payload.books) || [];

  if (books.length === 0) {
    showState('___');
    return [];
  }

  showState('success');
  renderBooks(books);
  return books;
}
''',
                "blanks": [
                    {
                        "prompt": "`fakeFetch` hands back a promise. How does the response get out of it?",
                        "hole": "kw",
                        "opts": ["await", "return", "yield", "new"],
                        "a": 0,
                        "why": "`await` suspends the function until the promise settles, then either produces the value or rethrows the rejection — which is what puts the `catch` in play.",
                        "whys": [
                            "`await` suspends the function until the promise settles, then either produces the value or rethrows the rejection — which is what puts the surrounding `catch` in play at all. Without it the `try` block cannot see the failure, because the rejection happens long after the block has been left.",
                            "`return` is a statement, not an operator, so it cannot sit on the right-hand side of an assignment: `response = return window.fakeFetch(...)` is a syntax error and the file never parses, so not one of the four states is ever reached. Written on its own line it would at least run — and still be wrong, because an `async` function's own promise simply adopts the one it returns, so awaiting `searchBooks` hands the caller a raw response object where it expected an array of books, and every state below the return is skipped.",
                            "`yield` belongs to generator functions, declared `function*`. In an `async function` it is a syntax error.",
                            "`new` would try to construct `window.fakeFetch` as a class. It is a plain function returning a promise, so this produces an object that is not a response and has no `ok`.",
                        ],
                    },
                    {
                        "prompt": "The query is whatever the user typed — `C++`, `rock & roll`, `50% off`.",
                        "hole": "fn",
                        "opts": ["encodeURI", "encodeURIComponent", "escape", "String"],
                        "a": 1,
                        "why": "`encodeURIComponent` escapes the characters that are structural in a URL — `&`, `=`, `+`, `#`, `/` — which is exactly right for a value being placed inside one.",
                        "whys": [
                            "`encodeURI` is for encoding a whole URL, so it deliberately leaves `&`, `=`, `?` and `/` alone — they are the punctuation it is trying to preserve. Search for `rock & roll` and the server sees a query of `rock ` plus a parameter called ` roll`.",
                            "`encodeURIComponent` escapes the characters that are structural in a URL — `&`, `=`, `+`, `#`, `/` — which is exactly right for a value being placed inside one. This is the one to reach for whenever you are building a query string by concatenation.",
                            "`escape` is deprecated and was never URL encoding: it uses a different escape syntax, mangles non-ASCII into `%uXXXX`, and leaves `+` untouched — where `+` in a query string already means a space.",
                            "`String` changes nothing about the text; the value is already a string. Every unescaped `&` in it still splits the query into parameters that were never intended.",
                        ],
                    },
                    {
                        "prompt": "The request completed. Did it succeed?",
                        "hole": "prop",
                        "opts": ["status", "ok", "error", "body"],
                        "a": 1,
                        "why": "`response.ok` is true exactly for statuses 200-299, which is the question being asked.",
                        "whys": [
                            "`status` is a number, and every real status is truthy — `!500` and `!200` are both false — so this branch would never run and a 500 would fall through to `json()` and render as an empty result.",
                            "`response.ok` is true exactly for statuses 200-299, which is the question being asked. The message below still reads `response.status`, because *which* failure it was is what the reader needs.",
                            "There is no `error` property on a `Response`. It reads as `undefined`, `!undefined` is true, and every response — including the good ones — takes the error path.",
                            "`body` is a `ReadableStream` and is truthy whether the request went well or badly. Touching it here also risks consuming the stream that `json()` is about to need.",
                        ],
                    },
                    {
                        "prompt": "The payload is `{ books: [...] }`, sent as JSON.",
                        "hole": "method",
                        "opts": ["json", "text", "parse", "body"],
                        "a": 0,
                        "why": "`response.json()` reads the body to the end and parses it, returning a promise — which is why it is awaited too.",
                        "whys": [
                            "`response.json()` reads the body to the end and parses it, returning a promise for the parsed value — which is why it is awaited as well. Reading the body is a second asynchronous step, separate from receiving the headers.",
                            "`response.text()` resolves to the raw string. `payload.books` on a string is `undefined`, the fallback gives `[]`, and every successful search renders as the empty state — a failure with no error message anywhere.",
                            "`parse` is a method of `JSON`, not of `Response`. Calling `response.parse()` throws a TypeError, and because it is outside the `try` the rejection escapes the function entirely.",
                            "`body` is a property, not a method, so this calls a `ReadableStream` as a function and throws. The stream is the low-level way in, for when you want to read a response progressively rather than all at once.",
                        ],
                    },
                    {
                        "prompt": "The server answered, correctly, with nothing.",
                        "hole": "state",
                        "opts": ["error", "success", "empty", "loading"],
                        "a": 2,
                        "why": "Zero results is a successful answer with nothing in it, and it needs its own message — otherwise it is a blank panel the reader cannot interpret.",
                        "whys": [
                            "Nothing failed. Reporting an error sends someone off to check their connection over a search that worked perfectly and simply matched no books.",
                            "The success path calls `renderBooks` on an empty array and leaves an empty `<ul>`, which on screen is indistinguishable from a request that is still running. The reader has no way to tell whether to wait or to try different words.",
                            "Zero results is a successful answer with nothing in it, and it needs its own message. This is the state that survives development untested, because the fixtures always have data in them.",
                            "`loading` leaves the spinner up over a request that has already finished, which is the one outcome worse than no feedback: it promises something is still coming when nothing is.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How long does the waterfall take?",
                "minutes": 7,
                "brief": r'''
A dashboard's first paint needs 18 independent `GET` calls to the same origin. They
are all started at once — no `await` inside a loop, one `Promise.all` — so as far as
your code is concerned they are simultaneous.

The browser disagrees. It keeps at most 6 connections open to a single origin over
HTTP/1.1, and the rest wait their turn. Every call takes 120 ms from request to last
byte, and the server itself adds no queueing delay.
''',
                "prompt": "How long after the first request goes out does the last response arrive?",
                "note": "Milliseconds. Assume each connection starts its next request the instant the previous one finishes.",
                "figure": "18 requests, 6 connections, 120 ms each — issued together, served six at a time.",
                "given": [
                    {"label": "Requests", "value": "18"},
                    {"label": "Concurrent connections per origin", "value": "6"},
                    {"label": "Round trip per request", "value": "120 ms"},
                    {"label": "Server queueing", "value": "none"},
                ],
                "aside": "Six per origin is the long-standing HTTP/1.1 browser limit. Over a single "
                         "HTTP/2 connection the requests are multiplexed instead and the batching "
                         "disappears — which is what made domain sharding obsolete.",
                "answer": 360,
                "tol": 0,
                "unit": "ms",
                "hint": "The six connections work through the queue in waves. How many waves, and what "
                        "does one wave cost?",
                "wrong": "2160 ms is the sequential figure — an `await` inside a `for` loop, one request "
                         "at a time. 120 ms is what you would get if the connection limit did not exist.",
                "why": r"""
Six at a time through eighteen requests is three waves — $\lceil 18/6 \rceil = 3$ — and
each wave costs one full round trip, so $3 \times 120 = 360$ ms. Two numbers bracket it
and both are worth carrying around. With no connection limit it would be 120 ms, the
cost of a single round trip, because the requests genuinely were issued together. Await
them one at a time inside a loop instead and it is $18 \times 120 = 2160$ ms — six times
worse than the real answer, and the version you get by accident, because writing
`for (const url of urls) { await get(url); }` reads so naturally. `Promise.all` is what
buys the difference, and the connection limit is what stops it being free.
""",
            },
            "lab": [{
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
            }, {
                "title": "Loading users, and saying so",
                "runtime": "web",
                "minutes": 20,
                "brief": r'''
The smallest complete round trip: press a button, wait, draw what came back.
`index.html` is read-only and defines `window.fakeFetch(url)` — a stand-in for
`fetch` that resolves after 200ms with an object carrying `ok`, `status` and
`json()`. For `"/api/users"` the body is an array of three users with `id`,
`name` and `role`; every other path answers **404**.

In `app.js`:

- `async function loadUsers()` — call `window.fakeFetch("/api/users")`, throw
  when `response.ok` is false, and otherwise **return the array** the body holds.
- `renderUsers(users)` — rebuild `#users` as one `<li>` per user showing the
  name.
- a `click` handler on `#load` that writes `Loading…` into `#status` **before**
  it awaits, then renders and sets `#status` to `Loaded 3 users`. When
  `loadUsers` throws, the list is left empty and `#status` reads
  `Could not load users`.

The last of those is the whole exercise. A page that only handles success
leaves the word *Loading* on screen forever, and the person waiting has no way
to tell a slow network from a broken one.
''',
                "files": [
                    {"name": "index.html", "ro": True, "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Team</title>
<style>
  body { font-family: system-ui, -apple-system, "Segoe UI", sans-serif; max-width: 26rem; margin: 2.5rem auto; padding: 0 1rem; color: #1b1f27; }
  button { font: inherit; padding: 0.5rem 0.9rem; border-radius: 6px; border: 0; background: #1b1f27; color: #fff; font-weight: 600; cursor: pointer; }
  #status { color: #5a6270; min-height: 1.4em; }
  ul { list-style: none; padding: 0; }
  li { padding: 0.4rem 0; border-bottom: 1px solid #eceff3; }
</style>
</head>
<body>

<main>
  <h1>Team</h1>
  <button id="load" type="button">Load users</button>
  <p id="status" aria-live="polite"></p>
  <ul id="users"></ul>
</main>

<script>
/* A stand-in for fetch(). This file is read-only. */
(function () {
  var DB = {
    '/api/users': [
      { id: 1, name: 'Ada Lovelace', role: 'Analyst' },
      { id: 2, name: 'Grace Hopper', role: 'Compiler engineer' },
      { id: 3, name: 'Linus Torvalds', role: 'Kernel maintainer' }
    ]
  };

  window.fakeFetch = function (url) {
    return new Promise(function (resolve) {
      setTimeout(function () {
        var data = DB[url];
        resolve({
          ok: data !== undefined,
          status: data !== undefined ? 200 : 404,
          json: function () {
            return Promise.resolve(data !== undefined ? data : { error: 'Not found' });
          }
        });
      }, 200);
    });
  };
})();
</script>
<script src="app.js"></script>
</body>
</html>
'''},
                    {"name": "app.js", "content": r'''
const loadButton = document.querySelector("#load");
const statusEl = document.querySelector("#status");
const list = document.querySelector("#users");

async function loadUsers() {
  // TODO: await window.fakeFetch("/api/users"), throw when the response is not
  //       ok, and return the array the body holds.
}

function renderUsers(users) {
  // TODO: rebuild #users as one <li> per user, showing the name
}

// TODO: a click handler on #load. Set the status to "Loading…" before awaiting,
//       then render and report the count — or, on a failure, leave the list
//       empty and say "Could not load users".
'''},
                ],
                "main": "index.html",
                "solution": [
                    {"name": "app.js", "content": r'''
const loadButton = document.querySelector("#load");
const statusEl = document.querySelector("#status");
const list = document.querySelector("#users");

async function loadUsers() {
  const response = await window.fakeFetch("/api/users");
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return await response.json();
}

function renderUsers(users) {
  list.textContent = "";
  for (const user of users) {
    const li = document.createElement("li");
    li.textContent = user.name;
    list.append(li);
  }
}

loadButton.addEventListener("click", async () => {
  statusEl.textContent = "Loading…";
  try {
    const users = await loadUsers();
    renderUsers(users);
    statusEl.textContent = `Loaded ${users.length} users`;
  } catch (error) {
    renderUsers([]);
    statusEl.textContent = "Could not load users";
  }
});
'''},
                ],
                "hints": [
                    "`loadUsers` is three lines: `const response = await window.fakeFetch(\"/api/users\");`, then `if (!response.ok) { throw new Error(...); }`, then `return await response.json();`.",
                    "A rejected promise reaches you as an ordinary exception at the line of the `await`, so the caller's `try` / `catch` is what turns a failure into a message.",
                    "The handler has to be `async` itself before it can `await loadUsers()`. Write it as `async () => { ... }`.",
                    "The status line goes on the page *before* the await, not after it. Set after, it appears for one frame at the moment it has stopped being true.",
                ],
                "tests": [
                    {"name": "loadUsers is async and resolves with the array", "code": r'''
assertEqual(typeof loadUsers, 'function', 'Define a function called loadUsers');
var _p = loadUsers();
assert(_p && typeof _p.then === 'function', 'loadUsers should be async, so calling it returns a promise');
var _users = await _p;
assert(Array.isArray(_users), 'loadUsers should resolve with the array of users, got ' + JSON.stringify(_users));
assertEqual(_users.length, 3, 'The catalogue holds three users, got ' + _users.length);
assertEqual(_users[0].name, 'Ada Lovelace', 'and in the order the body sent them, got ' + _users[0].name);
'''},
                    {"name": "Clicking Load renders one row per name", "code": r'''
document.querySelector('#users').textContent = '';
document.querySelector('#load').click();
await new Promise(function (r) { setTimeout(r, 450); });
var _items = document.querySelectorAll('#users li');
assertEqual(_items.length, 3, 'Expected three rows after loading, found ' + _items.length);
assert(_items[1].textContent.indexOf('Grace Hopper') !== -1, 'Each row should show the user name, got: ' + _items[1].textContent);
'''},
                    {"name": "The status says loading first, then the count", "code": r'''
var _st = document.querySelector('#status');
document.querySelector('#load').click();
await new Promise(function (r) { setTimeout(r, 30); });
assert(_st.textContent.indexOf('Loading') === 0, 'The status should read Loading... straight away, before the await. Got: "' + _st.textContent + '"');
await new Promise(function (r) { setTimeout(r, 450); });
assertEqual(_st.textContent, 'Loaded 3 users', 'After the load the status should read "Loaded 3 users", got "' + _st.textContent + '"');
'''},
                    {"name": "A failing request leaves an empty list and says so", "code": r'''
var _real = window.fakeFetch;
window.fakeFetch = function () { return _real('/api/missing'); };
document.querySelector('#load').click();
await new Promise(function (r) { setTimeout(r, 450); });
window.fakeFetch = _real;
assertEqual(document.querySelector('#status').textContent, 'Could not load users', 'On a 404 the status should read "Could not load users", got "' + document.querySelector('#status').textContent + '"');
assertEqual(document.querySelectorAll('#users li').length, 0, 'and the list should be empty, found ' + document.querySelectorAll('#users li').length + ' row(s)');
'''},
                ],
            }, {
                "title": "A REST handler with no framework",
                "runtime": "python",
                "minutes": 28,
                "brief": r'''
The routing table from the reading, as one function and nothing else.
Implement `handle_request(method, path, body=None)` returning a
`(status, data)` pair. The module-level list `TODOS` is the database and
`next_id()` hands out ids; a todo is `{"id": 1, "title": "...", "done": False}`.

| Request | Answer |
|---|---|
| `GET /todos` | `(200, [every todo])` |
| `POST /todos` with `{"title": "..."}` | append, then `(201, the new todo)` |
| `POST /todos` with no title, or an empty one | `(400, {"error": "title is required"})` |
| `GET /todos/<id>` | `(200, todo)`, or `(404, {"error": "not found"})` |
| `PATCH /todos/<id>` with `{"done": True}` | update `done`, then `(200, todo)`, or 404 |
| `DELETE /todos/<id>` | remove it, then `(204, None)`, or 404 |
| any other path | `(404, {"error": "not found"})` |
| a known path, an unsupported verb | `(405, {"error": "method not allowed"})` |

That last row is the one worth getting right. `DELETE /todos` is not a missing
resource — it is a resource that does not accept that verb, and 405 is what says
so. Split the path with `path.split("/")`, and remember that the id arrives as a
string.
''',
                "files": [
                    {"name": "main.py", "content": r'''
TODOS = []
_id_counter = 0


def next_id():
    global _id_counter
    _id_counter += 1
    return _id_counter


def handle_request(method, path, body=None):
    """Return a (status, data) tuple for the to-do API."""
    # TODO: split the path, then handle the collection and the item separately.
    return (404, {"error": "not found"})


print(handle_request("POST", "/todos", {"title": "Order brake pads"}))
print(handle_request("GET", "/todos"))
'''},
                ],
                "main": "main.py",
                "solution": [
                    {"name": "main.py", "content": r'''
TODOS = []
_id_counter = 0


def next_id():
    global _id_counter
    _id_counter += 1
    return _id_counter


def find_todo(todo_id):
    for todo in TODOS:
        if todo["id"] == todo_id:
            return todo
    return None


def handle_request(method, path, body=None):
    """Return a (status, data) tuple for the to-do API."""
    parts = [p for p in path.split("/") if p]

    if parts == ["todos"]:
        if method == "GET":
            return (200, TODOS)
        if method == "POST":
            title = (body or {}).get("title")
            if not title:
                return (400, {"error": "title is required"})
            todo = {"id": next_id(), "title": title, "done": False}
            TODOS.append(todo)
            return (201, todo)
        return (405, {"error": "method not allowed"})

    if len(parts) == 2 and parts[0] == "todos" and parts[1].isdigit():
        todo = find_todo(int(parts[1]))
        if todo is None:
            return (404, {"error": "not found"})
        if method == "GET":
            return (200, todo)
        if method == "PATCH":
            if body and "done" in body:
                todo["done"] = bool(body["done"])
            return (200, todo)
        if method == "DELETE":
            TODOS.remove(todo)
            return (204, None)
        return (405, {"error": "method not allowed"})

    return (404, {"error": "not found"})


print(handle_request("POST", "/todos", {"title": "Order brake pads"}))
print(handle_request("GET", "/todos"))
'''},
                ],
                "hints": [
                    "`parts = [p for p in path.split(\"/\") if p]` drops the empty strings the leading slash produces, so `/todos` becomes `[\"todos\"]` and `/todos/3` becomes `[\"todos\", \"3\"]`.",
                    "Write a `find_todo(todo_id)` helper first — three of the routes need it, and it is the one place that decides what 'not found' means.",
                    "Treat the collection and the item as two blocks. Inside each, dispatch on the method and end the block with the 405; fall out of both blocks to the final 404.",
                    "The id in the path is a string. `parts[1].isdigit()` guards the conversion, and `int(parts[1])` does it — `\"3\" == 3` is False, so comparing without converting finds nothing and reports nothing wrong.",
                ],
                "tests": [
                    {"name": "POST creates a todo and answers 201", "code": r'''
TODOS.clear()
_status, _todo = handle_request("POST", "/todos", {"title": "Order brake pads"})
assert _status == 201, f"A successful create answers 201, got {_status}"
assert isinstance(_todo, dict), f"The body should be the new todo, got {_todo!r}"
assert _todo["title"] == "Order brake pads", f"Got {_todo!r}"
assert _todo["done"] is False, f"A new todo starts not done, got {_todo!r}"
assert "id" in _todo, f"The server assigns the id, so it has to come back: {_todo!r}"
'''},
                    {"name": "GET /todos lists them in the order they arrived", "code": r'''
TODOS.clear()
handle_request("POST", "/todos", {"title": "a"})
handle_request("POST", "/todos", {"title": "b"})
_status, _list = handle_request("GET", "/todos")
assert _status == 200, f"A successful read answers 200, got {_status}"
assert [t["title"] for t in _list] == ["a", "b"], f"Got {_list!r}"
'''},
                    {"name": "A missing or empty title is refused with 400", "code": r'''
TODOS.clear()
_status, _err = handle_request("POST", "/todos", {})
assert _status == 400, f"A body with no title should give 400, got {_status}"
assert "error" in _err, f"Say what was wrong: {_err!r}"
assert handle_request("POST", "/todos", {"title": ""})[0] == 400, "An empty title is not a title"
assert TODOS == [], f"A refused create must not append anything, got {TODOS!r}"
'''},
                    {"name": "GET /todos/<id> finds one, or 404s", "code": r'''
TODOS.clear()
_todo = handle_request("POST", "/todos", {"title": "find me"})[1]
_status, _found = handle_request("GET", "/todos/" + str(_todo["id"]))
assert _status == 200 and _found["title"] == "find me", f"Got {(_status, _found)!r}"
assert handle_request("GET", "/todos/999999")[0] == 404, "An id that is not there gives 404"
'''},
                    {"name": "PATCH updates done and returns the todo", "code": r'''
TODOS.clear()
_todo = handle_request("POST", "/todos", {"title": "x"})[1]
_status, _updated = handle_request("PATCH", "/todos/" + str(_todo["id"]), {"done": True})
assert _status == 200, f"A successful update answers 200, got {_status}"
assert _updated["done"] is True, f"Got {_updated!r}"
assert handle_request("PATCH", "/todos/999999", {"done": True})[0] == 404
'''},
                    {"name": "DELETE removes it with 204, and then it is gone", "code": r'''
TODOS.clear()
_todo = handle_request("POST", "/todos", {"title": "x"})[1]
_id = str(_todo["id"])
assert handle_request("DELETE", "/todos/" + _id) == (204, None), "DELETE answers (204, None) — nothing left to send"
assert handle_request("GET", "/todos/" + _id)[0] == 404, "The deleted todo should be gone"
assert handle_request("DELETE", "/todos/" + _id)[0] == 404, "Deleting it twice leaves the world the same, and says 404 the second time"
'''},
                    {"name": "Unknown path 404, unsupported verb 405", "code": r'''
TODOS.clear()
assert handle_request("GET", "/nope")[0] == 404, "A path the server has nothing at gives 404"
assert handle_request("DELETE", "/todos")[0] == 405, "The collection exists and does not accept DELETE — that is 405, not 404"
_todo = handle_request("POST", "/todos", {"title": "x"})[1]
assert handle_request("POST", "/todos/" + str(_todo["id"]))[0] == 405, "An item does not accept POST either"
'''},
                ],
            }, {
                "title": "A task board with three columns",
                "runtime": "web",
                "minutes": 55,
                "brief": r'''
The state-and-render pattern at the size of a small application: three columns,
cards that move between them, and counts that cannot drift because nothing
stores them. You are given a skeleton in three files and the structure the
checks look for; the rest is yours.

## Structure

- a `.board` container laid out with **grid or flex**
- three `.column` elements with `data-status` of `todo`, `doing` and `done`,
  each holding an `<h2>` containing a `.count` span, and a `<ul class="cards">`
- the form `#new-card` with the text input `#card-title` and a submit button —
  both are already in `index.html`

## Behaviour

- Submitting the form adds a `.card` to the **todo** column showing the title.
  A blank title is ignored; a successful add clears the input.
- Every card carries a `.move` button that sends it one step along
  todo → doing → done. Cards already in **done** have no `.move` button.
- Every card carries a `.delete` button that removes it.
- Each column's `.count` shows how many cards are in that column.
- It should look like a board: columns side by side, headers you can read,
  cards that read as cards.

## Approach

Keep an array of `{ id, title, status }` and one `render()` that rebuilds all
three columns from it and writes all three counts. Write the three
`<section class="column">` blocks into `index.html` by hand — only the cards are
dynamic. Delegate both buttons from `.board`, since every render throws the old
buttons away, and put the card's id on the `<li>` as `data-id` so a handler can
find its way back to the array.

Derive the counts inside `render()` from the same filtered list that built the
column. A count stored anywhere else is the second copy of the truth this
module opened with.
''',
                "files": [
                    {"name": "index.html", "content": r'''
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Task board</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<header>
  <h1>Task board</h1>
  <form id="new-card">
    <label class="sr-only" for="card-title">New task</label>
    <input id="card-title" name="title" type="text" placeholder="New task" autocomplete="off">
    <button type="submit">Add</button>
  </form>
</header>

<main class="board">
  <!-- Three <section class="column"> blocks go here. Each needs a data-status of
       todo, doing or done, an <h2> holding a <span class="count">, and a
       <ul class="cards"> for the cards to be rendered into. -->
</main>

<script src="app.js"></script>
</body>
</html>
'''},
                    {"name": "style.css", "content": r'''
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: #f0f2f5; color: #171a21; }
header { display: flex; align-items: center; gap: 1rem; padding: 1rem 1.25rem; background: #fff; border-bottom: 1px solid #d7dce4; }
h1 { margin: 0; font-size: 1.25rem; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

/* Lay out .board, then style .column, .cards and .card. */
'''},
                    {"name": "app.js", "content": r'''
const board = document.querySelector(".board");
const form = document.querySelector("#new-card");
const input = document.querySelector("#card-title");

const ORDER = ["todo", "doing", "done"];
let cards = [];       // { id, title, status }
let nextId = 1;

function render() {
  // TODO: for each status in ORDER, find that column, rebuild its ul.cards from
  //       the cards with that status, and write the number into its .count.
  //       A card is an <li class="card" data-id="N"> holding the title, a
  //       .delete button, and a .move button unless it is already done.
}

// TODO: a submit listener on the form: prevent the default, trim the title,
//       refuse a blank one, append with status "todo", clear the input, render.

// TODO: one delegated click listener on `board` that finds the .card the click
//       landed in, then acts on .move or .delete and renders.

render();
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
<title>Task board</title>
<link rel="stylesheet" href="style.css">
</head>
<body>

<header>
  <h1>Task board</h1>
  <form id="new-card">
    <label class="sr-only" for="card-title">New task</label>
    <input id="card-title" name="title" type="text" placeholder="New task" autocomplete="off">
    <button type="submit">Add</button>
  </form>
</header>

<main class="board">
  <section class="column" data-status="todo">
    <h2>To do <span class="count">0</span></h2>
    <ul class="cards"></ul>
  </section>
  <section class="column" data-status="doing">
    <h2>Doing <span class="count">0</span></h2>
    <ul class="cards"></ul>
  </section>
  <section class="column" data-status="done">
    <h2>Done <span class="count">0</span></h2>
    <ul class="cards"></ul>
  </section>
</main>

<script src="app.js"></script>
</body>
</html>
'''},
                    {"name": "style.css", "content": r'''
* { box-sizing: border-box; }
body { margin: 0; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; background: #f0f2f5; color: #171a21; }
header { display: flex; align-items: center; gap: 1rem; padding: 1rem 1.25rem; background: #fff; border-bottom: 1px solid #d7dce4; }
h1 { margin: 0; font-size: 1.25rem; }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }

#new-card { display: flex; gap: 0.5rem; margin-left: auto; }
#card-title { font: inherit; padding: 0.5rem 0.6rem; border: 1px solid #d7dce4; border-radius: 6px; min-width: 14rem; }
#new-card button { font: inherit; padding: 0.5rem 0.9rem; border: 0; border-radius: 6px; background: #1b1f27; color: #fff; font-weight: 600; cursor: pointer; }

.board {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  padding: 1.25rem;
  align-items: start;
}

.column { background: #e4e7ec; border-radius: 12px; padding: 0.75rem; }

.column h2 {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #4e5766;
  margin: 0.25rem 0.25rem 0.75rem;
}

.count { background: #fff; border-radius: 999px; padding: 0 0.5rem; font-size: 0.75rem; }

.cards { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; min-height: 2.5rem; }

.card {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #fff;
  border-radius: 8px;
  padding: 0.6rem 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.card .title { flex: 1; }

.card button { font: inherit; border: 0; background: #f0f2f5; border-radius: 6px; padding: 0.2rem 0.5rem; cursor: pointer; font-size: 0.8rem; }

.card button:hover { background: #d7dce4; }

.card .delete { color: #a5271f; }

@media (max-width: 700px) {
  .board { grid-template-columns: 1fr; }
  header { flex-wrap: wrap; }
  #new-card { margin-left: 0; width: 100%; }
}
'''},
                    {"name": "app.js", "content": r'''
const board = document.querySelector(".board");
const form = document.querySelector("#new-card");
const input = document.querySelector("#card-title");

const ORDER = ["todo", "doing", "done"];
let cards = [];       // { id, title, status }
let nextId = 1;

function cardElement(card) {
  const li = document.createElement("li");
  li.className = "card";
  li.dataset.id = String(card.id);

  const title = document.createElement("span");
  title.className = "title";
  title.textContent = card.title;
  li.append(title);

  if (card.status !== "done") {
    const move = document.createElement("button");
    move.type = "button";
    move.className = "move";
    move.textContent = "Move on";
    li.append(move);
  }

  const del = document.createElement("button");
  del.type = "button";
  del.className = "delete";
  del.textContent = "Delete";
  li.append(del);

  return li;
}

function render() {
  for (const status of ORDER) {
    const column = board.querySelector(`.column[data-status="${status}"]`);
    const list = column.querySelector(".cards");
    const inColumn = cards.filter((card) => card.status === status);

    list.textContent = "";
    for (const card of inColumn) {
      list.append(cardElement(card));
    }
    column.querySelector(".count").textContent = inColumn.length;
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const title = input.value.trim();
  if (!title) {
    return;
  }
  cards.push({ id: nextId, title: title, status: "todo" });
  nextId += 1;
  input.value = "";
  render();
});

board.addEventListener("click", (event) => {
  const cardEl = event.target.closest(".card[data-id]");
  if (!cardEl) {
    return;
  }
  const id = Number(cardEl.dataset.id);
  const card = cards.find((c) => c.id === id);
  if (!card) {
    return;
  }

  if (event.target.closest(".move")) {
    const next = ORDER[ORDER.indexOf(card.status) + 1];
    if (next) {
      card.status = next;
    }
  } else if (event.target.closest(".delete")) {
    cards = cards.filter((c) => c.id !== id);
  } else {
    return;
  }
  render();
});

render();
'''},
                ],
                "hints": [
                    "Write the three `<section class=\"column\">` blocks into `index.html` by hand. Only the cards change at runtime, so the columns are markup, not output.",
                    "`render()` is a loop over `ORDER`. For each status: find `.column[data-status=\"...\"]`, empty its `.cards`, append one `<li>` per matching card, and write the length into `.count`. Deriving the count from the same filtered array is what keeps it honest.",
                    "Build the `<li>` with `document.createElement` and `textContent`, and set `li.dataset.id = String(card.id)`. Append the `.move` button only when the status is not `done` — that is the whole of the last check.",
                    "One `click` listener on `board`. `event.target.closest(\".card[data-id]\")` gives the card, and `event.target.closest(\".move\")` or `.closest(\".delete\")` says which button was hit. Return early when neither matched, or a click on the column background re-renders for nothing.",
                ],
                "tests": [
                    {"name": "Three columns, with the structure the checks read", "code": r'''
var _cols = document.querySelectorAll('.board .column');
assertEqual(_cols.length, 3, 'Found ' + _cols.length + ' .column elements inside .board — three are needed');
var _statuses = Array.prototype.map.call(_cols, function (c) { return c.dataset.status; });
['todo', 'doing', 'done'].forEach(function (s) {
  assert(_statuses.indexOf(s) !== -1, 'No column with data-status="' + s + '" — found ' + JSON.stringify(_statuses));
});
Array.prototype.forEach.call(_cols, function (c) {
  assert(c.querySelector('h2 .count') !== null, 'The ' + c.dataset.status + ' column needs a .count span inside its <h2>');
  assert(c.querySelector('ul.cards') !== null, 'The ' + c.dataset.status + ' column needs a <ul class="cards">');
});
'''},
                    {"name": "The board is laid out as a board", "code": r'''
var _d = getComputedStyle(document.querySelector('.board')).display;
assert(_d === 'grid' || _d === 'flex', '.board should use grid or flex so the columns sit side by side, got display: ' + _d);
var _cols = document.querySelectorAll('.board .column');
var _tops = Array.prototype.map.call(_cols, function (c) { return Math.round(c.getBoundingClientRect().top); });
assert(_tops[0] === _tops[1] && _tops[1] === _tops[2], 'The three columns should start at the same height, got tops ' + JSON.stringify(_tops));
'''},
                    {"name": "Adding puts a card in To do, and a blank title does not", "code": r'''
var _guard = 0;
while (document.querySelector('.card .delete') && _guard < 60) { document.querySelector('.card .delete').click(); _guard += 1; }
assertEqual(document.querySelectorAll('.card').length, 0, 'Could not clear the board through the delete buttons — check that .delete removes a card');
var _input = document.querySelector('#card-title');
var _form = document.querySelector('#new-card');
_input.value = 'Price the winter tyres';
_form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
var _todo = document.querySelectorAll('.column[data-status="todo"] .card');
assertEqual(_todo.length, 1, 'A new card belongs in the todo column, found ' + _todo.length + ' there');
assert(_todo[0].textContent.indexOf('Price the winter tyres') !== -1, 'The card should show its title, got: ' + _todo[0].textContent);
assert(_todo[0].dataset.id, 'Each card needs a data-id so a delegated handler can find it in the array');
assertEqual(_input.value, '', 'Clear the input after a successful add');
_input.value = '   ';
_form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
assertEqual(document.querySelectorAll('.card').length, 1, 'A blank title should add nothing');
'''},
                    {"name": "The counts follow the columns", "code": r'''
var _guard = 0;
while (document.querySelector('.card .delete') && _guard < 60) { document.querySelector('.card .delete').click(); _guard += 1; }
var _input = document.querySelector('#card-title');
var _form = document.querySelector('#new-card');
['Price the winter tyres', 'Sweep bay 2'].forEach(function (t) {
  _input.value = t;
  _form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
});
var _todo = document.querySelector('.column[data-status="todo"]');
assertEqual(_todo.querySelector('.count').textContent.trim(), '2', 'Two cards in todo should show a count of 2, got ' + _todo.querySelector('.count').textContent.trim());
assertEqual(document.querySelector('.column[data-status="doing"] .count').textContent.trim(), '0', 'An empty column shows 0');
'''},
                    {"name": "Move walks a card along the pipeline", "code": r'''
var _guard = 0;
while (document.querySelector('.card .delete') && _guard < 60) { document.querySelector('.card .delete').click(); _guard += 1; }
var _input = document.querySelector('#card-title');
var _form = document.querySelector('#new-card');
_input.value = 'Order oil filters';
_form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
var _first = document.querySelector('.column[data-status="todo"] .card .move');
assert(_first !== null, 'A card in todo needs a .move button');
_first.click();
assertEqual(document.querySelectorAll('.column[data-status="doing"] .card').length, 1, 'One move should land the card in doing');
var _again = document.querySelector('.column[data-status="doing"] .card .move');
assert(_again !== null, 'A card in doing needs a .move button too');
_again.click();
var _done = document.querySelectorAll('.column[data-status="done"] .card');
assertEqual(_done.length, 1, 'A second move should land it in done');
assert(_done[0].querySelector('.move') === null, 'A card in done has nowhere to go, so it carries no .move button');
'''},
                    {"name": "Delete removes exactly one card", "code": r'''
var _guard = 0;
while (document.querySelector('.card .delete') && _guard < 60) { document.querySelector('.card .delete').click(); _guard += 1; }
var _input = document.querySelector('#card-title');
var _form = document.querySelector('#new-card');
['one', 'two', 'three'].forEach(function (t) {
  _input.value = t;
  _form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
});
var _del = document.querySelector('.card .delete');
assert(_del !== null, 'Every card needs a .delete button');
_del.click();
assertEqual(document.querySelectorAll('.card').length, 2, 'Deleting one card should leave two, found ' + document.querySelectorAll('.card').length);
assert(document.body.textContent.indexOf('one') === -1 || document.querySelectorAll('.card').length === 2, 'Delete should remove the card that was clicked');
'''},
                    {"name": "Every count matches the column it sits in", "code": r'''
Array.prototype.forEach.call(document.querySelectorAll('.column'), function (col) {
  var _n = col.querySelectorAll('.card').length;
  var _shown = col.querySelector('.count').textContent.trim();
  assertEqual(_shown, String(_n), 'The ' + col.dataset.status + ' column holds ' + _n + ' card(s) and shows "' + _shown + '" — derive the count in render() from the same list that built the column');
});
'''},
                ],
            }, {
                "title": "A bookstore API, cleanly split",
                "runtime": "python",
                "minutes": 65,
                "brief": r'''
The handler from the earlier lab, grown into something with a database behind it
and split the way a service is: `db.py` owns the schema, `api.py` owns the
routing and the SQL, and `main.py` does nothing but a demonstration run. The
checks import your modules and call
`handle_request(conn, method, path, body)` directly.

## `db.py`

`init_db(conn)` creates the table
`books (id INTEGER PRIMARY KEY, title TEXT, author TEXT, price REAL, stock INTEGER)`.
It must be safe to call twice — `CREATE TABLE IF NOT EXISTS`.

## `api.py` — `handle_request(conn, method, path, body=None)` returns `(status, data)`

A book travels as `{"id", "title", "author", "price", "stock"}`.

- `GET /books` → `(200, [...])`, ordered by id
- `GET /books?author=X` → only that author, matched case-insensitively, and
  **passed as a parameter rather than glued into the SQL** — one check sends an
  injection string and expects an empty list back
- `POST /books` → validate first: `title` and `author` non-empty strings,
  `price` a number at least 0, `stock` an integer at least 0. Valid inserts and
  answers `(201, book)`; invalid answers `(400, {"error": "..."})`
- `GET /books/<id>` → `(200, book)` or `(404, {"error": "not found"})`
- `PUT /books/<id>` → the same validation, then replace all four fields →
  `(200, book)`, or 404
- `DELETE /books/<id>` → `(204, None)`, or 404
- `POST /books/<id>/purchase` with `{"quantity": n}` — `n` an integer of 1 or
  more, else 400. When `stock` is below `n`, `(409, {"error": "insufficient stock"})`;
  otherwise reduce the stock and answer `(200, book)`
- an unknown path is 404; a known path with an unsupported verb is 405

## A suggested order

`init_db`, then a `row_to_book` helper, then `POST` and `GET /books`, then the
three routes on `/books/<id>`, then the author filter, then `purchase`. Write
one `validate(body)` returning an error string or `None` and call it from both
`POST` and `PUT`, so there is exactly one definition of a valid book.
''',
                "files": [
                    {"name": "db.py", "content": r'''
def init_db(conn):
    """Create the books table. Safe to call more than once."""
    pass
'''},
                    {"name": "api.py", "content": r'''
def row_to_book(row):
    """(id, title, author, price, stock) -> dict."""
    pass


def validate(body):
    """Return an error string, or None when the body is a valid book."""
    pass


def handle_request(conn, method, path, body=None):
    """Route a request to the right SQL and return (status, data)."""
    return (404, {"error": "not found"})
'''},
                    {"name": "main.py", "content": r'''
import sqlite3
from db import init_db
from api import handle_request

conn = sqlite3.connect(":memory:")
init_db(conn)

print(handle_request(conn, "POST", "/books",
                     {"title": "The Dispossessed", "author": "Le Guin",
                      "price": 129.0, "stock": 3}))
print(handle_request(conn, "GET", "/books"))
'''},
                ],
                "main": "main.py",
                "solution": [
                    {"name": "db.py", "content": r'''
def init_db(conn):
    """Create the books table. Safe to call more than once."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT,
            author TEXT,
            price REAL,
            stock INTEGER
        )
    """)
    conn.commit()
'''},
                    {"name": "api.py", "content": r'''
COLUMNS = "id, title, author, price, stock"


def row_to_book(row):
    """(id, title, author, price, stock) -> dict."""
    return {
        "id": row[0],
        "title": row[1],
        "author": row[2],
        "price": row[3],
        "stock": row[4],
    }


def validate(body):
    """Return an error string, or None when the body is a valid book."""
    body = body or {}
    title = body.get("title")
    author = body.get("author")
    price = body.get("price")
    stock = body.get("stock")
    if not isinstance(title, str) or not title.strip():
        return "title is required"
    if not isinstance(author, str) or not author.strip():
        return "author is required"
    if not isinstance(price, (int, float)) or isinstance(price, bool) or price < 0:
        return "price must be a number >= 0"
    if not isinstance(stock, int) or isinstance(stock, bool) or stock < 0:
        return "stock must be an integer >= 0"
    return None


def get_book(conn, book_id):
    row = conn.execute(
        f"SELECT {COLUMNS} FROM books WHERE id = ?", (book_id,)
    ).fetchone()
    return row_to_book(row) if row else None


def handle_collection(conn, method, query, body):
    if method == "GET":
        if query.startswith("author="):
            author = query[len("author="):].replace("+", " ")
            rows = conn.execute(
                f"SELECT {COLUMNS} FROM books WHERE LOWER(author) = LOWER(?) ORDER BY id",
                (author,),
            ).fetchall()
        else:
            rows = conn.execute(f"SELECT {COLUMNS} FROM books ORDER BY id").fetchall()
        return (200, [row_to_book(r) for r in rows])
    if method == "POST":
        error = validate(body)
        if error:
            return (400, {"error": error})
        cursor = conn.execute(
            "INSERT INTO books (title, author, price, stock) VALUES (?, ?, ?, ?)",
            (body["title"], body["author"], body["price"], body["stock"]),
        )
        conn.commit()
        return (201, get_book(conn, cursor.lastrowid))
    return (405, {"error": "method not allowed"})


def handle_purchase(conn, book, body):
    quantity = (body or {}).get("quantity")
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity < 1:
        return (400, {"error": "quantity must be an integer >= 1"})
    if book["stock"] < quantity:
        return (409, {"error": "insufficient stock"})
    conn.execute(
        "UPDATE books SET stock = stock - ? WHERE id = ?", (quantity, book["id"])
    )
    conn.commit()
    return (200, get_book(conn, book["id"]))


def handle_item(conn, method, book_id, book, body):
    if method == "GET":
        return (200, book)
    if method == "PUT":
        error = validate(body)
        if error:
            return (400, {"error": error})
        conn.execute(
            "UPDATE books SET title = ?, author = ?, price = ?, stock = ? WHERE id = ?",
            (body["title"], body["author"], body["price"], body["stock"], book_id),
        )
        conn.commit()
        return (200, get_book(conn, book_id))
    if method == "DELETE":
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        return (204, None)
    return (405, {"error": "method not allowed"})


def handle_request(conn, method, path, body=None):
    """Route a request to the right SQL and return (status, data)."""
    path, _, query = path.partition("?")
    parts = [p for p in path.split("/") if p]

    if parts == ["books"]:
        return handle_collection(conn, method, query, body)

    if len(parts) >= 2 and parts[0] == "books" and parts[1].isdigit():
        book_id = int(parts[1])
        book = get_book(conn, book_id)

        if len(parts) == 3 and parts[2] == "purchase":
            if method != "POST":
                return (405, {"error": "method not allowed"})
            if book is None:
                return (404, {"error": "not found"})
            return handle_purchase(conn, book, body)

        if len(parts) == 2:
            if book is None:
                return (404, {"error": "not found"})
            return handle_item(conn, method, book_id, book, body)

    return (404, {"error": "not found"})
'''},
                    {"name": "main.py", "content": r'''
import sqlite3
from db import init_db
from api import handle_request

conn = sqlite3.connect(":memory:")
init_db(conn)

print(handle_request(conn, "POST", "/books",
                     {"title": "The Dispossessed", "author": "Le Guin",
                      "price": 129.0, "stock": 3}))
print(handle_request(conn, "GET", "/books"))
print(handle_request(conn, "POST", "/books/1/purchase", {"quantity": 2}))
print(handle_request(conn, "GET", "/books/1"))
'''},
                ],
                "hints": [
                    "Split the query string before anything else: `path, _, query = path.partition(\"?\")` leaves `path` as `/books` and `query` as `author=le+guin`, so the routing below never has to think about it.",
                    "`row_to_book` keeps the tuple-index juggling in exactly one place. Every route that returns a book goes through it, so the field order is written down once.",
                    "One `validate(body)` returning an error string or `None` serves both `POST` and `PUT`. Beware `isinstance(True, int)` — it is `True` in Python, so a boolean passes an integer check unless you rule it out.",
                    "`purchase` is a sub-route: `parts == [\"books\", \"<id>\", \"purchase\"]`. Test for it before the plain `/books/<id>` block, or the two-part branch will never see it.",
                    "The author filter is `WHERE LOWER(author) = LOWER(?)` with the value passed as a parameter. Gluing it into the string with an f-string is what makes `' OR '1'='1` a query instead of a name.",
                ],
                "tests": [
                    {"name": "init_db creates the table, twice if asked", "code": r'''
import sqlite3 as _sq
from db import init_db
_c = _sq.connect(":memory:")
init_db(_c)
init_db(_c)
_c.execute("SELECT id, title, author, price, stock FROM books")
'''},
                    {"name": "POST creates; GET lists in id order", "code": r'''
import sqlite3 as _sq
from db import init_db
from api import handle_request
_c = _sq.connect(":memory:")
init_db(_c)
_s1, _b1 = handle_request(_c, "POST", "/books", {"title": "The Dispossessed", "author": "Le Guin", "price": 129.0, "stock": 3})
assert _s1 == 201, f"A successful create answers 201, got {_s1}"
assert _b1.get("id"), f"The server assigns the id, so it has to come back: {_b1!r}"
assert _b1["stock"] == 3, f"Got {_b1!r}"
handle_request(_c, "POST", "/books", {"title": "Kindred", "author": "Butler", "price": 149.0, "stock": 2})
_s2, _list = handle_request(_c, "GET", "/books")
assert _s2 == 200 and [b["title"] for b in _list] == ["The Dispossessed", "Kindred"], f"Got {_list!r}"
'''},
                    {"name": "POST validates every field", "code": r'''
import sqlite3 as _sq
from db import init_db
from api import handle_request
_c = _sq.connect(":memory:")
init_db(_c)
_bad_bodies = [
    {},
    {"title": "", "author": "x", "price": 1, "stock": 1},
    {"title": "x", "author": "", "price": 1, "stock": 1},
    {"title": "x", "author": "y", "price": -1, "stock": 1},
    {"title": "x", "author": "y", "price": 1, "stock": "many"},
    {"title": "x", "author": "y", "price": 1, "stock": -2},
]
for _bad in _bad_bodies:
    _s, _e = handle_request(_c, "POST", "/books", _bad)
    assert _s == 400, f"{_bad!r} should be refused with 400, got {_s}"
    assert "error" in _e, f"Say what was wrong: {_e!r}"
assert handle_request(_c, "GET", "/books")[1] == [], "A refused create must not insert anything"
'''},
                    {"name": "GET and DELETE by id, with their 404s", "code": r'''
import sqlite3 as _sq
from db import init_db
from api import handle_request
_c = _sq.connect(":memory:")
init_db(_c)
_b = handle_request(_c, "POST", "/books", {"title": "Dune", "author": "Herbert", "price": 99.0, "stock": 1})[1]
_id = str(_b["id"])
assert handle_request(_c, "GET", "/books/" + _id)[0] == 200
assert handle_request(_c, "GET", "/books/424242")[0] == 404, "An id that is not there gives 404"
assert handle_request(_c, "DELETE", "/books/" + _id) == (204, None), "DELETE answers (204, None)"
assert handle_request(_c, "GET", "/books/" + _id)[0] == 404, "The deleted book should be gone"
'''},
                    {"name": "PUT replaces, after validating", "code": r'''
import sqlite3 as _sq
from db import init_db
from api import handle_request
_c = _sq.connect(":memory:")
init_db(_c)
_b = handle_request(_c, "POST", "/books", {"title": "Dune", "author": "Herbert", "price": 99.0, "stock": 1})[1]
_s, _u = handle_request(_c, "PUT", "/books/" + str(_b["id"]), {"title": "Dune", "author": "Herbert", "price": 129.0, "stock": 4})
assert _s == 200 and _u["price"] == 129.0 and _u["stock"] == 4, f"Got {(_s, _u)!r}"
assert handle_request(_c, "PUT", "/books/" + str(_b["id"]), {"title": ""})[0] == 400, "PUT validates the same way POST does"
assert handle_request(_c, "GET", "/books/" + str(_b["id"]))[1]["price"] == 129.0, "A refused PUT must leave the row alone"
assert handle_request(_c, "PUT", "/books/424242", {"title": "x", "author": "y", "price": 1, "stock": 1})[0] == 404
'''},
                    {"name": "The author filter is case-insensitive and injection-proof", "code": r'''
import sqlite3 as _sq
from db import init_db
from api import handle_request
_c = _sq.connect(":memory:")
init_db(_c)
handle_request(_c, "POST", "/books", {"title": "The Dispossessed", "author": "Le Guin", "price": 129.0, "stock": 3})
handle_request(_c, "POST", "/books", {"title": "The Left Hand of Darkness", "author": "Le Guin", "price": 119.0, "stock": 2})
handle_request(_c, "POST", "/books", {"title": "Kindred", "author": "Butler", "price": 149.0, "stock": 2})
_s, _hits = handle_request(_c, "GET", "/books?author=LE GUIN")
assert _s == 200 and len(_hits) == 2, f"A case-insensitive filter should find two, got {_hits!r}"
_s2, _inj = handle_request(_c, "GET", "/books?author=' OR '1'='1")
assert _s2 == 200 and _inj == [], "Passed as a parameter, the injection string is only a strange author name — expected an empty list"
'''},
                    {"name": "Purchase reduces the stock, and 409s when it cannot", "code": r'''
import sqlite3 as _sq
from db import init_db
from api import handle_request
_c = _sq.connect(":memory:")
init_db(_c)
_b = handle_request(_c, "POST", "/books", {"title": "Dune", "author": "Herbert", "price": 99.0, "stock": 3})[1]
_p = "/books/" + str(_b["id"]) + "/purchase"
_s, _u = handle_request(_c, "POST", _p, {"quantity": 2})
assert _s == 200 and _u["stock"] == 1, f"Two of three bought should leave one, got {(_s, _u)!r}"
assert handle_request(_c, "POST", _p, {"quantity": 5})[0] == 409, "Buying more than the stock is a conflict, not a bad request"
assert handle_request(_c, "GET", "/books/" + str(_b["id"]))[1]["stock"] == 1, "A refused purchase must not touch the stock"
assert handle_request(_c, "POST", _p, {"quantity": 0})[0] == 400, "A quantity has to be a positive integer"
assert handle_request(_c, "POST", "/books/424242/purchase", {"quantity": 1})[0] == 404
'''},
                ],
            }],
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
