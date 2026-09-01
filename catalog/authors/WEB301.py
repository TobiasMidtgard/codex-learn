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
            ],
            "quiz": {
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
            },
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
            ],
            "quiz": {
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
            },
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
            "quiz": {
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
            },
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
            "quiz": {
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
            },
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
