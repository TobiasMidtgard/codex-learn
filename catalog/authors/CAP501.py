"""CAP501 — Capstone Engineering Project. Author module."""

COURSE = {
    "id": "CAP501",
    "title": "Capstone Engineering Project",
    "year": 5,
    "level": "Expert",
    "prereqs": ["CS330", "CS401", "SE201", "CS220"],
    "stack": ["Python", "SQL", "HTTP"],
    "credits": 30,
    "hours": 300,
    "icon": "★",
    "summary": (
        "The degree's final build. You take a written brief to a running backend "
        "service: a contract with versioning rules, a migrated SQLite schema behind a "
        "repository, a service layer with salted password hashing and per-resource "
        "authorisation, and the logging, health and metrics that let somebody else "
        "operate it. The capstone is a five-module service judged by a conformance "
        "suite, a security review and a performance budget."
    ),
    "outcomes": [
        "Turn a prose brief into a machine-readable API contract and generate its conformance suite mechanically",
        "Classify a contract change as breaking, additive or neutral and derive the version bump it forces",
        "Evolve a schema through forward-only migrations recorded in a schema-version table",
        "Write a repository whose every query is parameterised and whose multi-row writes are transactional",
        "Store credentials as salted, iterated hashes and compare them in constant time",
        "Map domain failures onto HTTP status codes without leaking internals to the caller",
        "Instrument a service with correlation ids, a health check, counters and an asserted performance budget",
    ],
    "assessment": "4 engineering checkpoints (10% each) + the capstone service (60%).",
    "reading": [
        "Fowler, *Patterns of Enterprise Application Architecture*, Addison-Wesley 2002 — Repository, Unit of Work, Data Mapper",
        "Kleppmann, *Designing Data-Intensive Applications*, O'Reilly 2017 — chapters 2 and 7",
        "Beyer, Jones, Petoff & Murphy (eds), *Site Reliability Engineering*, O'Reilly 2016 — chapters 6 and 17",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Architecture and the contract",
            "summary": "A brief becomes a schema; a schema becomes a test suite.",
            "concepts": [
                "The contract is the interface: prose is a starting point, not the specification",
                "A declarative request schema lets validation and test generation share one source of truth",
                "Conformance suites should be *generated* from the contract, not hand-written beside it",
                "Every constraint in a schema implies at least one negative test",
                "Semantic versioning: breaking forces MAJOR, additive forces MINOR, neither forces PATCH",
                "Adding a required field or narrowing an enum breaks callers; adding an optional field does not",
                "`isinstance(True, int)` is True — booleans need checking before integers",
            ],
            "read": [
                {
                    "title": "One paragraph, three services, and sixteen tests nobody typed",
                    "minutes": 15,
                    "body": r'''
Three teams are handed the same paragraph and build three different services.

```text
Users can post notes. A note has a title and a body. Notes are private or
shared with the team. Important ones can carry a priority and be pinned.
```

The mobile client posts `{"title": "", "body": "", "visibility": "public"}` and gets a
201, because nobody said a title had to have characters in it and nobody said which
visibilities exist. The web client posts a 400-character title and gets a 500 from a
`TEXT` column with a length check three layers down, which is a crash dressed up as a
server fault. A batch importer omits `visibility` entirely, because "private or shared
with the team" reads like a sentence with a default hiding in it. Nobody misread the
paragraph. The paragraph does not say how long a title may be, whether `visibility` is
required, or what happens to `"public"`.

Every question a prose brief leaves open is a decision somebody makes silently, in a
different file, on a different day, and each of the three teams above made a defensible
one. The bug reports arrive weeks later and are unarguable in both directions.

## The paragraph wants to be a table

Sit down with the paragraph and write out what it declines to say. For each field: what
type, is it required, what bounds, what values are allowed.

```text
title       string   required   1..80 characters
body        string   required   up to 2000 characters
priority    integer  optional   1..5
visibility  string   required   one of private, team
pinned      boolean  optional
```

That table is the contract. Written as data rather than prose it becomes a *field
schema*: `{"type": "string", "min_length": 1, "max_length": 80}`, and an endpoint is a
method, a path, a success status and an object schema over those fields. The moment it
is data, two things that used to be written separately can be computed from it — the
validator that rejects a bad request, and the test suite that proves the validator does.
That is the whole idea of this module, and it is not an aesthetic preference: a
hand-written suite drifts from the contract silently, and a generated one cannot.

## Every constraint implies at least one negative test

Look at a single line of that table. `title` is a string, required, at least 1
character, at most 80. Four separate promises, and each of them is a promise only if
something breaks when it is violated. A validator that accepts a missing title is not
enforcing "required"; it is documenting an intention. So each constraint earns exactly
one test that violates it and nothing else.

Count them field by field, mechanically, with no judgement anywhere in the loop:

```python
SCHEMA = {
    "title": {"type": "string", "min_length": 1, "max_length": 80},
    "body": {"type": "string", "max_length": 2000},
    "priority": {"type": "integer", "minimum": 1, "maximum": 5, "optional": True},
    "visibility": {"type": "string", "enum": ["private", "team"]},
    "pinned": {"type": "boolean", "optional": True},
}


def violations(field):
    """Every way this one field can be broken, in a fixed order."""
    names = []
    if not field.get("optional"):
        names.append("missing")
    if field["type"] == "string" and field.get("min_length", 0) > 0:
        names.append("too short")
    if field["type"] == "string" and "max_length" in field:
        names.append("too long")
    if field["type"] == "integer" and "minimum" in field:
        names.append("below minimum")
    if field["type"] == "integer" and "maximum" in field:
        names.append("above maximum")
    if "enum" in field:
        names.append("outside the enum")
    names.append("wrong type")
    return names


total = 0
for name, field in SCHEMA.items():
    found = violations(field)
    total += len(found)
    print("{0:<11}{1}  {2}".format(name, len(found), ", ".join(found)))
print("negative cases:", total)
print("with the positive case and the unexpected-key case:", total + 2)
```

It prints four rows of constraints for `title`, three for `body`, three for `priority`,
three for `visibility`, one for `pinned` — then `negative cases: 14` and
`with the positive case and the unexpected-key case: 16`.

Read the asymmetries, because each one is the schema speaking. `body` has no
`min_length`, so there is no `too short` case: an empty body is legal and the suite
must not claim otherwise. `priority` is optional, so there is no `missing` case:
omitting it is a valid request, and a suite that expected a 400 there would be testing a
rule nobody wrote. `pinned` is optional with no bounds, so the only thing that can go
wrong with it is its type. Fourteen negatives, one minimal-valid positive, one request
carrying a key the schema does not mention: sixteen cases for one endpoint with five
fields, and the number is derived rather than chosen.

Nobody types sixteen cases for one endpoint. That is the point. A team that writes the
suite by hand writes six of them, the interesting-looking ones, and then adds
`max_length: 200` to `body` next month and does not add the seventeenth. A generated
suite grows the case the same afternoon the constraint appears, because the case *is*
the constraint, walked.

## The type check that has to come first

There is one ordering trap in the validator, and it is the sort that passes review
because the code reads as correct.

```python
def type_name_naive(value):
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    return type(value).__name__


def type_name(value):
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    return type(value).__name__


for value in (True, 3, "x"):
    print(repr(value), "->", type_name_naive(value), "|", type_name(value))
```

The first line of output is `True -> integer | boolean`. In Python `bool` is a subclass
of `int`, so `isinstance(True, int)` is `True`, and a type check that asks about `int`
before `bool` reports every boolean as a number. Follow that through the validator: a
request sending `{"priority": True}` is typed as an integer, so the range checks run,
and `True` compares as 1 — inside `1..5`. The request is accepted. The database stores
`1`. Nothing raises, nothing is logged, and a boolean has become a priority.

The same slip runs the other way in the generated suite: a `pinned wrong type` case that
sends an integer is only a negative case if `type_name` refuses to call an integer a
boolean, which it will do for free once `bool` is tested first.

## A type mismatch stops the field

When `title` arrives as the integer `5`, the validator reports one error, not three.
Checking `len(5)` raises; checking `5 >= min_length` answers a question nobody asked, in
the affirmative, and the caller is then told their integer title is too short. Neither
is useful, so the rule is: on a type mismatch return exactly one error and stop
inspecting that field. Errors from other fields still accumulate — the caller should
learn about all their mistakes in one round trip, not one per deploy.

Order matters too. Fields are reported in declaration order, and unknown keys come last,
sorted, so that two runs of the same bad request produce the same list. A test that
compares error lists against a dictionary's iteration order is a test that fails when
somebody reorders the schema for readability.

## What a change costs, in one number

Once the contract is data, a release becomes a diff, and the diff answers the version
question by itself. The question is never "how big does this feel"; it is "does an
existing caller, unchanged, still work".

```python
def bump(old, kinds):
    major, minor, patch = (int(part) for part in old.split("."))
    if "breaking" in kinds:
        return "{0}.0.0".format(major + 1)
    if "additive" in kinds:
        return "{0}.{1}.0".format(major, minor + 1)
    return "{0}.{1}.{2}".format(major, minor, patch + 1)


changes = [
    ("add an optional colour field", {"additive"}),
    ("add a required colour field", {"breaking"}),
    ("add public to the visibility enum", {"additive"}),
    ("drop team from the visibility enum", {"breaking"}),
    ("raise min_length on title from 1 to 3", {"breaking"}),
    ("reword the field description in the docs", set()),
]
for description, kinds in changes:
    print("1.4.2 ->", bump("1.4.2", kinds), " ", description)
```

The two `colour` lines differ by one word in the schema and by a whole major version in
the result: `1.5.0` against `2.0.0`. An optional field is invisible to a caller who does
not send it. A required one rejects every request they have ever made. Widening the enum
to include `public` cannot break anyone, because nobody was sending a value that is now
newly allowed; narrowing it to drop `team` breaks precisely the callers who were using
the feature. Raising `min_length` from 1 to 3 rejects two-character titles that were
accepted yesterday, which is a break even though nothing was added or removed.

The mistake here is the honest one: "we only added a field, that is a minor." It is
tempting because the sentence is true about the *diff* and false about the *callers*, and
the version number is a promise to callers. `required_bump` in the lab takes the decision
away from anyone's judgement — it reads the diff and returns `"major"`, `"minor"` or
`"patch"`, and `next_version` applies it, zeroing minor and patch on a major bump because
`2.4.2` would claim to be a superset of `1.4.2` and is not.

## Where this stops holding

A field schema of this shape checks one field at a time, in isolation, and that is a real
ceiling. It cannot say "`priority` may only be set when `visibility` is `team`", or
"`end_date` must be after `start_date`", because both are relationships and every check
here takes a single value. Cross-field rules live in the service layer, and they need
tests written by a person.

Nor does the contract describe behaviour. Two implementations can pass all sixteen cases
and disagree about whether `POST /notes` twice with the same body creates one note or
two, about the order `GET /notes` returns, or about what a caller may assume when the
network drops mid-request. Change the default sort order and you break every client that
relied on it while `diff_contracts` reports nothing at all — the shape did not move.
Semantic versioning over a shape diff catches shape breaks, and only those.

And a generated suite tests the contract, not the world. It will never notice that the
contract itself is wrong: that 80 characters is too short for a real title, or that
`visibility` should have had a third value from the start. It makes the implementation
agree with the specification, which is worth a great deal and is not the same as being
correct.

## What you are about to build

The lab, **Contract, validator and generated conformance suite**, is that whole pipeline
in one file. `type_name` with `bool` before `int`; `example` for the minimal legal body;
`validate_field` short-circuiting on a type mismatch; `validate` walking fields in
declaration order with unknown keys sorted at the end; `conformance_cases` emitting the
sixteen; and `diff_contracts`, `required_bump` and `next_version` turning a release into
a number. The suite it generates is the one your capstone service is then judged by, so
the sharper this contract is, the less of the capstone is guesswork.
''',
                },
            ],
            "quiz": {
                "title": "Contracts, generated suites and the version a change forces",
                "minutes": 8,
                "questions": [
                    {
                        "q": "`pinned` is declared `{\"type\": \"boolean\", \"optional\": True}`. How many negative conformance cases does the generator produce for it?",
                        "opts": [
                            "Two, a wrong-type case and a missing case, since every declared field is omitted once",
                            "One, the wrong-type case, because an optional boolean has no further promise to break",
                            "None, because an optional field is absent from the minimal body and so is never sent",
                            "Three, adding a null case, because a boolean column rejects null as well as a string",
                        ],
                        "a": 1,
                        "whys": [
                            r"The missing case exists to prove that a *required* field is required. `pinned` is optional, so a request without it is valid, and a case expecting 400 there would test a rule the contract never made.",
                            r"Optional removes the missing case, and a bare boolean carries no length, range or enum bound — only its type is left to violate.",
                            r"It is absent from the *positive* case, which is exactly why it needs a negative one: the generator builds each negative body from the minimal valid body and then adds the offending value, so `pinned` is present in its own case and nowhere else.",
                            r"Null is a real thing to worry about in a wire format, but it is not in this contract's type vocabulary — the schema types are string, integer and boolean, and the wrong-type case already covers everything that is not a boolean.",
                        ],
                        "why": r"""
Walk the constraints: optional cancels `missing`; there is no `min_length` or
`max_length` on a boolean, no `minimum` or `maximum`, and no `enum`. What is left
is the one case every field gets — a value of the wrong type. That single case is
what makes the field's declared type a promise rather than a comment, and it is why
the endpoint totals 14 negatives rather than the 15 you get by assuming every field
contributes a missing case.
""",
                    },
                    {
                        "q": "A release removes `\"team\"` from the `visibility` enum and adds an optional `colour` field. What version bump does that force on `1.4.2`?",
                        "opts": [
                            "`1.5.0`, since the only field added is optional and an enum lists values, not shape",
                            "`2.0.0`, since a caller already sending `visibility: team` is now rejected outright",
                            "`1.4.3`, since no endpoint was added or removed and the field list is unchanged",
                            "`1.5.0` and then `2.0.0`, since the two changes must ship as two separate releases",
                        ],
                        "a": 1,
                        "whys": [
                            r"The optional field really is a minor on its own. The bump is decided by the worst change in the release, though, and dropping an enum value sits above it: one breaking change in a release makes the whole release breaking.",
                            r"Callers using `team` today send a request that stops validating, and that is the definition of a break.",
                            r"A patch says every existing caller is unaffected. The callers sending `team` are very much affected, and a field list that is unchanged in length can still have narrowed in what it accepts.",
                            r"Splitting the release is a legitimate thing to do, but it does not change the arithmetic: whether these ship together or apart, the enum removal is still a major bump, so this reaches `2.0.0` either way rather than avoiding it.",
                        ],
                        "why": r"""
Ask the only question that matters: does an unchanged existing caller still work?
A caller sending `visibility: "team"` was valid yesterday and is rejected today, so
something broke, and `required_bump` returns `"major"` the moment `diff_contracts`
puts anything in the breaking list. The additive `colour` field is then irrelevant
to the number — a major bump also zeroes minor and patch, so `1.4.2` becomes
`2.0.0` and not `2.5.0`.
""",
                    },
                    {
                        "q": "In `type_name`, the `bool` check is swapped so that `isinstance(value, int)` is tested first. What actually goes wrong?",
                        "opts": [
                            "Nothing at runtime; the order only decides which of two equivalent error strings comes back",
                            "`True` is typed as an integer, so a boolean then passes the range checks on a numeric field",
                            "`3` is typed as a boolean, because Python treats every non-zero integer as a truth value",
                            "`isinstance` raises a `TypeError` when a `bool` is tested against `int`, and validation dies",
                        ],
                        "a": 1,
                        "whys": [
                            r"There is a runtime consequence and it is silent, which is what makes it dangerous — no error string changes because no error is produced at all.",
                            r"`isinstance(True, int)` is `True`, so the integer branch claims the value, and `True` then compares as 1 inside a 1..5 range.",
                            r"Truthiness and type are different questions. `isinstance(3, bool)` is `False` — the subclassing runs one way only, so an integer is never mistaken for a boolean, however truthy it is.",
                            r"`isinstance` is perfectly happy with any pair of types and answers True or False either way. The failure here is that it answers True where you wanted False, not that it refuses to answer.",
                        ],
                        "why": r"""
`bool` is a subclass of `int` in Python, so `isinstance(True, int)` is `True` while
`isinstance(3, bool)` is `False`. Test `int` first and every boolean is reported as
an integer; a request sending `{"priority": True}` then reaches the range checks,
where `True` behaves as 1 and sits comfortably inside 1..5. The request is accepted,
nothing raises, and a boolean is stored as a priority. Testing the subclass before
the superclass is the general rule, and this is the case where forgetting it costs
nothing visible until the data is already wrong.
""",
                    },
                    {
                        "q": "The team adds `\"max_length\": 200` to the `body` field. What does a generated conformance suite give you that a hand-written one does not?",
                        "opts": [
                            "It replays the previous run's cases against the new schema and reports which changed",
                            "It grows a `body too long` case immediately, because the case is the constraint walked",
                            "It refuses the schema change until a matching negative test has been written beside it",
                            "It marks every case stale, so the whole suite is regenerated and re-reviewed as a unit",
                        ],
                        "a": 1,
                        "whys": [
                            r"Comparing runs is a useful thing to build, but it is not what the generator does — it has no memory of a previous run and derives the whole suite from the current contract each time it is called.",
                            r"`conformance_cases` walks the field's constraints, so a constraint that exists on Tuesday has a case on Tuesday.",
                            r"That is a review policy, not a property of generation. The generator has no opinion about whether a change is wise; it only guarantees that whatever is in the schema is exercised.",
                            r"There is no staleness to mark, because nothing is stored: every call regenerates from scratch. The freshness is not achieved by invalidating old cases but by never keeping any.",
                        ],
                        "why": r"""
A hand-written suite and the contract are two descriptions of the same rules that
have to be kept in step by a person remembering to. The failure mode is not that
somebody writes a wrong test, it is that a constraint is added and no test is,
so the suite stays green while the coverage quietly falls. Deriving the cases from
the contract removes the second description entirely: `conformance_cases` reads
`max_length` and emits a `too long` case because that is the only thing it knows how
to do with a `max_length`.
""",
                    },
                    {
                        "q": "A request arrives with `title` set to the integer `5`. Why does the validator report one error for that field rather than three?",
                        "opts": [
                            "Because the validator stops at the first error in the whole body, whichever field raised it",
                            "Because a length or range check on a value of the wrong type either crashes or misleads",
                            "Because integers are coerced to their string form before the length bounds are applied",
                            "Because `title` is declared first, and later fields are collected into a separate list",
                        ],
                        "a": 1,
                        "whys": [
                            r"Only that field short-circuits. Errors on other fields still accumulate, on purpose — a caller with three mistakes should learn about all three in one round trip rather than one per deploy.",
                            r"`len(5)` raises, and `5 >= 1` answers truthfully about a value that has no business being compared.",
                            r"Nothing is coerced anywhere in this validator, and coercion is the very habit it exists to refuse — accepting the integer `5` as if it were the two-character text is how a type constraint quietly stops being one.",
                            r"Declaration order decides the order errors are *reported*, not how many there are. Swap `title` to the end of the schema and it still produces exactly one error for a wrong type.",
                        ],
                        "why": r"""
Two of the three checks are meaningless on an integer: `len(5)` raises a `TypeError`,
and the `min_length` comparison would answer a question about a value whose type
already disqualifies it. So the rule is per field, not per body — on a type mismatch
return exactly that one error and stop inspecting *this* field, while every other
field is still checked and reported. That is what keeps the error list both honest
and complete: one error for the field that is the wrong shape, all the errors for
the fields that are the right shape and still wrong.
""",
                    },
                    {
                        "q": "Which of these requirements can this field-schema contract genuinely not express?",
                        "opts": [
                            "A `title` of between 1 and 80 characters, since two separate bounds cannot both be applied",
                            "That `priority` may only be sent when `visibility` is `team`, as a field is checked alone",
                            "An enum of exactly two values, since an enum needs three or more members to be useful",
                            "A field required on one endpoint and optional on another, since one schema is shared",
                        ],
                        "a": 1,
                        "whys": [
                            r"Both bounds apply happily and independently — `min_length` and `max_length` sit in the same field schema and produce a `too short` case and a `too long` case each release.",
                            r"That is a relationship between two fields, and every check in this model takes one value and one field schema.",
                            r"Two is a perfectly ordinary enum, and `visibility` is exactly that. Nothing in the model counts members, and a two-value enum still produces its `outside the enum` case like any other.",
                            r"Each endpoint carries its own object schema, so the same field name can be required in one and optional in another. The reasoning about sharing describes a design nobody chose here.",
                        ],
                        "why": r"""
Cross-field rules are the ceiling of this model. `validate_field` receives a name, a
value and that field's schema — it never sees the rest of the body, so it cannot
consult `visibility` while judging `priority`. Conditional requirements, ordering
between two dates and totals that must match a line-item sum all live above this
layer, in the service, with tests a person writes. Knowing precisely where the
generated suite stops is what tells you which tests still have to be thought about.
""",
                    },
                ],
            },
            "lab": {
                "title": "Contract, validator and generated conformance suite",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
A *field schema* is a dict: `{"type": ...}` plus optional `optional`,
`min_length`, `max_length`, `minimum`, `maximum`, `enum`. Types are
`"string"`, `"integer"`, `"boolean"`. An *object schema* is
`{"type": "object", "fields": {name: field_schema, ...}}`. A *contract* is
`{"version": "1.4.2", "endpoints": [...]}`, each endpoint being
`{"method", "path", "success", "request": object_schema}`.

**`parse_version(text)`** -> `(major, minor, patch)`; `ValueError` unless it is
three dotted runs of digits. **`compare_versions(a, b)`** -> `-1`, `0` or `1`.

**`type_name(value)`** -> the schema name of a Python value. Check `bool`
*before* `int`, or every boolean field will happily accept `3`.

**`example(schema)`** -> the minimal instance a schema admits: an object gives
its non-optional fields only; an `enum` gives `enum[0]`; a string gives
`"x" * max(1, min_length)`; an integer gives `minimum` if stated else `0`; a
boolean gives `False`.

**`validate_field(name, value, schema)`** -> a list of error strings. On a type
mismatch return exactly one error and stop:

```text
title: expected string, got integer
visibility: not one of ['private', 'team']
title: shorter than 1
title: longer than 80
priority: below minimum 1
priority: above maximum 5
```

**`validate(value, schema)`** -> the errors for a whole object: fields in
declaration order (`"<name>: missing"` for an absent required field), then
unknown keys sorted alphabetically as `"<name>: unexpected field"`. A
non-object where an object was promised gives
`["body: expected object, got <what arrived>"]`.

**`conformance_cases(endpoint)`** -> a list of
`{"name", "method", "path", "body", "expect"}`. First the positive case
`"<METHOD> <path>: minimal valid body"` expecting `endpoint["success"]`. Then,
walking the fields in declaration order and each field's violations in this
exact order, cases expecting `400`, named `"<METHOD> <path>: <field> <violation>"`:

```text
missing            (only when the field is required)     omit it
too short          (string with min_length > 0)          "x" * (min_length - 1)
too long           (string with max_length)              "x" * (max_length + 1)
below minimum      (integer with minimum)                minimum - 1
above maximum      (integer with maximum)                maximum + 1
outside the enum   (any field with an enum)              "__not_in_the_enum__"
wrong type         (always)                              WRONG_TYPE[field type]
```

Finally one `"<METHOD> <path>: unexpected field"` case adding a key `"__extra__"`.

**`diff_contracts(old, new)`** -> `{"breaking": [...], "additive": [...]}` of
reason strings, keyed on `(method, path)`. Breaking: a removed endpoint, a
removed field, a changed type, an optional field made required, a new required
field, a raised `min_length`, a lowered or newly-imposed `max_length`, a lost
enum value. Additive: a new endpoint, a new optional field, a lowered
`min_length`, a raised or dropped `max_length`, a gained enum value.

**`required_bump(old, new)`** -> `"major"` if anything breaks, else `"minor"` if
anything was added, else `"patch"`. **`next_version(old, new)`** applies that
bump to `old["version"]` — a major bump zeroes minor and patch.
''',
                "files": [{"name": "main.py", "content": r'''
WRONG_TYPE = {"string": 123, "integer": "not-an-integer", "boolean": "not-a-boolean"}


def parse_version(text):
    """(major, minor, patch); ValueError for anything else."""
    # your code here


def compare_versions(a, b):
    """-1, 0 or 1."""
    # your code here


def type_name(value):
    """The schema type name of a Python value. Booleans are not integers here."""
    # your code here


def example(schema):
    """The smallest instance the schema admits."""
    # your code here


def validate_field(name, value, schema):
    """Errors for one field; a type mismatch short-circuits."""
    # your code here


def validate(value, schema):
    """Errors for a whole object schema, in declaration order."""
    # your code here


def conformance_cases(endpoint):
    """One positive case plus one negative case per constraint."""
    # your code here


def diff_contracts(old, new):
    """{'breaking': [...], 'additive': [...]}."""
    # your code here


def required_bump(old, new):
    """'major', 'minor' or 'patch'."""
    # your code here


def next_version(old, new):
    """The version string the change forces."""
    # your code here


CONTRACT = {
    "version": "1.4.2",
    "endpoints": [
        {"method": "POST", "path": "/notes", "success": 201,
         "request": {"type": "object", "fields": {
             "title": {"type": "string", "min_length": 1, "max_length": 80},
             "body": {"type": "string", "max_length": 2000},
             "priority": {"type": "integer", "minimum": 1, "maximum": 5, "optional": True},
             "visibility": {"type": "string", "enum": ["private", "team"]},
             "pinned": {"type": "boolean", "optional": True},
         }}},
    ],
}

print("generated cases:", len(conformance_cases(CONTRACT["endpoints"][0]) or []))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
WRONG_TYPE = {"string": 123, "integer": "not-an-integer", "boolean": "not-a-boolean"}


def parse_version(text):
    """(major, minor, patch); ValueError for anything else."""
    parts = str(text).split(".")
    if len(parts) != 3:
        raise ValueError(f"{text!r} is not a MAJOR.MINOR.PATCH version")
    numbers = []
    for part in parts:
        if not part.isdigit():
            raise ValueError(f"{text!r} has a non-numeric component {part!r}")
        numbers.append(int(part))
    return tuple(numbers)


def compare_versions(a, b):
    """-1, 0 or 1."""
    left, right = parse_version(a), parse_version(b)
    return (left > right) - (left < right)


def type_name(value):
    """The schema type name of a Python value. Booleans are not integers here."""
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, dict):
        return "object"
    if isinstance(value, list):
        return "array"
    return type(value).__name__


def example(schema):
    """The smallest instance the schema admits."""
    kind = schema["type"]
    if kind == "object":
        return {name: example(field) for name, field in schema["fields"].items()
                if not field.get("optional")}
    if "enum" in schema:
        return schema["enum"][0]
    if kind == "string":
        return "x" * max(1, schema.get("min_length", 0))
    if kind == "integer":
        return schema.get("minimum", 0)
    if kind == "boolean":
        return False
    raise ValueError(f"unknown schema type {kind!r}")


def validate_field(name, value, schema):
    """Errors for one field; a type mismatch short-circuits."""
    kind = schema["type"]
    actual = type_name(value)
    if actual != kind:
        return [f"{name}: expected {kind}, got {actual}"]
    errors = []
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{name}: not one of {schema['enum']!r}")
    if kind == "string":
        if "min_length" in schema and len(value) < schema["min_length"]:
            errors.append(f"{name}: shorter than {schema['min_length']}")
        if "max_length" in schema and len(value) > schema["max_length"]:
            errors.append(f"{name}: longer than {schema['max_length']}")
    if kind == "integer":
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{name}: below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{name}: above maximum {schema['maximum']}")
    return errors


def validate(value, schema):
    """Errors for a whole object schema, in declaration order."""
    if schema["type"] != "object":
        return validate_field("value", value, schema)
    if not isinstance(value, dict):
        return [f"body: expected object, got {type_name(value)}"]
    errors = []
    for name, field in schema["fields"].items():
        if name not in value:
            if not field.get("optional"):
                errors.append(f"{name}: missing")
            continue
        errors.extend(validate_field(name, value[name], field))
    for extra in sorted(set(value) - set(schema["fields"])):
        errors.append(f"{extra}: unexpected field")
    return errors


def conformance_cases(endpoint):
    """One positive case plus one negative case per constraint."""
    method, path = endpoint["method"], endpoint["path"]
    schema = endpoint["request"]
    base = example(schema)
    cases = [{"name": f"{method} {path}: minimal valid body", "method": method,
              "path": path, "body": base, "expect": endpoint.get("success", 200)}]

    def negative(field, violation, body):
        cases.append({"name": f"{method} {path}: {field} {violation}", "method": method,
                      "path": path, "body": body, "expect": 400})

    for name, field in schema["fields"].items():
        kind = field["type"]
        if not field.get("optional"):
            without = dict(base)
            without.pop(name, None)
            negative(name, "missing", without)
        if kind == "string" and field.get("min_length", 0) > 0:
            short = dict(base)
            short[name] = "x" * (field["min_length"] - 1)
            negative(name, "too short", short)
        if kind == "string" and "max_length" in field:
            long_one = dict(base)
            long_one[name] = "x" * (field["max_length"] + 1)
            negative(name, "too long", long_one)
        if kind == "integer" and "minimum" in field:
            low = dict(base)
            low[name] = field["minimum"] - 1
            negative(name, "below minimum", low)
        if kind == "integer" and "maximum" in field:
            high = dict(base)
            high[name] = field["maximum"] + 1
            negative(name, "above maximum", high)
        if "enum" in field:
            outside = dict(base)
            outside[name] = "__not_in_the_enum__"
            negative(name, "outside the enum", outside)
        wrong = dict(base)
        wrong[name] = WRONG_TYPE[kind]
        negative(name, "wrong type", wrong)

    extra = dict(base)
    extra["__extra__"] = "x"
    cases.append({"name": f"{method} {path}: unexpected field", "method": method,
                  "path": path, "body": extra, "expect": 400})
    return cases


def _by_key(contract):
    return {(e["method"], e["path"]): e for e in contract["endpoints"]}


def diff_contracts(old, new):
    """{'breaking': [...], 'additive': [...]}."""
    breaking, additive = [], []
    old_map, new_map = _by_key(old), _by_key(new)
    for key, endpoint in old_map.items():
        label = f"{key[0]} {key[1]}"
        if key not in new_map:
            breaking.append(f"removed endpoint {label}")
            continue
        old_fields = endpoint["request"]["fields"]
        new_fields = new_map[key]["request"]["fields"]
        for name, field in old_fields.items():
            if name not in new_fields:
                breaking.append(f"{label}: removed field {name}")
                continue
            other = new_fields[name]
            if other["type"] != field["type"]:
                breaking.append(
                    f"{label}: {name} changed type from {field['type']} to {other['type']}")
            if field.get("optional") and not other.get("optional"):
                breaking.append(f"{label}: {name} became required")
            old_min = field.get("min_length", 0)
            new_min = other.get("min_length", 0)
            if new_min > old_min:
                breaking.append(f"{label}: {name} min_length raised to {new_min}")
            elif new_min < old_min:
                additive.append(f"{label}: {name} min_length lowered to {new_min}")
            old_max = field.get("max_length")
            new_max = other.get("max_length")
            if new_max is not None and (old_max is None or new_max < old_max):
                breaking.append(f"{label}: {name} max_length lowered to {new_max}")
            elif new_max is None and old_max is not None:
                additive.append(f"{label}: {name} max_length removed")
            elif new_max is not None and old_max is not None and new_max > old_max:
                additive.append(f"{label}: {name} max_length raised to {new_max}")
            for value in field.get("enum", []):
                if value not in other.get("enum", []):
                    breaking.append(f"{label}: {name} lost enum value {value!r}")
            for value in other.get("enum", []):
                if value not in field.get("enum", []):
                    additive.append(f"{label}: {name} gained enum value {value!r}")
        for name, field in new_fields.items():
            if name in old_fields:
                continue
            if field.get("optional"):
                additive.append(f"{label}: new optional field {name}")
            else:
                breaking.append(f"{label}: new required field {name}")
    for key in new_map:
        if key not in old_map:
            additive.append(f"added endpoint {key[0]} {key[1]}")
    return {"breaking": breaking, "additive": additive}


def required_bump(old, new):
    """'major', 'minor' or 'patch'."""
    diff = diff_contracts(old, new)
    if diff["breaking"]:
        return "major"
    if diff["additive"]:
        return "minor"
    return "patch"


def next_version(old, new):
    """The version string the change forces."""
    major, minor, patch = parse_version(old["version"])
    bump = required_bump(old, new)
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


CONTRACT = {
    "version": "1.4.2",
    "endpoints": [
        {"method": "POST", "path": "/notes", "success": 201,
         "request": {"type": "object", "fields": {
             "title": {"type": "string", "min_length": 1, "max_length": 80},
             "body": {"type": "string", "max_length": 2000},
             "priority": {"type": "integer", "minimum": 1, "maximum": 5, "optional": True},
             "visibility": {"type": "string", "enum": ["private", "team"]},
             "pinned": {"type": "boolean", "optional": True},
         }}},
    ],
}

print("generated cases:", len(conformance_cases(CONTRACT["endpoints"][0]) or []))
'''}],
                "hints": [
                    "`type_name` must test `isinstance(value, bool)` first — `isinstance(True, int)` is True, so the naive order lets `True` pass as an integer.",
                    "Short-circuit on a type mismatch: length and range checks on a value of the wrong type either crash or lie.",
                    "Build each negative case from `dict(example(schema))` so the other fields stay valid and exactly one constraint is under test.",
                    "`diff_contracts` walks old fields against new (removals, tightenings) and then new fields against old (additions) — two passes, not one.",
                ],
                "tests": [
                    {"name": "versions parse, order and reject", "code": r'''
assert parse_version("1.4.2") == (1, 4, 2), f"parse_version('1.4.2') gave {parse_version('1.4.2')!r}"
assert compare_versions("1.4.2", "1.10.0") == -1, "1.4.2 is older than 1.10.0 — compare numerically, not as text"
assert compare_versions("2.0.0", "2.0.0") == 0, "equal versions compare 0"
assert compare_versions("2.0.1", "2.0.0") == 1, "2.0.1 is newer than 2.0.0"
for _bad in ("1.4", "1.4.2.3", "1.4.x", "v1.4.2", ""):
    try:
        parse_version(_bad)
        assert False, f"parse_version({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "booleans are not integers", "code": r'''
assert type_name(True) == "boolean", f"type_name(True) gave {type_name(True)!r}"
assert type_name(3) == "integer" and type_name("x") == "string", "integers and strings must name themselves"
assert type_name({}) == "object" and type_name([]) == "array", "objects and arrays too"
assert validate_field("pinned", 1, {"type": "boolean"}) == ["pinned: expected boolean, got integer"], \
    f"1 is not a boolean; got {validate_field('pinned', 1, {'type': 'boolean'})!r}"
assert validate_field("priority", True, {"type": "integer"}) == ["priority: expected integer, got boolean"], \
    "True must not sneak in as an integer"
'''},
                    {"name": "example builds the minimal legal body", "code": r'''
_schema = CONTRACT["endpoints"][0]["request"]
_ex = example(_schema)
assert set(_ex) == {"title", "body", "visibility"}, f"optional fields must be left out; got {sorted(_ex)!r}"
assert _ex["title"] == "x" and _ex["body"] == "x", f"minimal strings, got {_ex!r}"
assert _ex["visibility"] == "private", f"an enum's minimal value is its first, got {_ex['visibility']!r}"
assert validate(_ex, _schema) == [], f"the minimal example must validate, got {validate(_ex, _schema)!r}"
assert example({"type": "integer", "minimum": 3}) == 3, "an integer's minimum is its minimal value"
assert example({"type": "integer"}) == 0 and example({"type": "boolean"}) is False, "unconstrained defaults"
'''},
                    {"name": "validate reports every violation, in order", "code": r'''
_schema = CONTRACT["endpoints"][0]["request"]
assert validate({"title": "t", "body": "b", "visibility": "team"}, _schema) == [], "a valid body has no errors"
_got = validate({"body": "b"}, _schema)
assert _got == ["title: missing", "visibility: missing"], f"missing required fields, in declaration order; got {_got!r}"
_got = validate({"title": "", "body": "b", "visibility": "public"}, _schema)
assert _got == ["title: shorter than 1", "visibility: not one of ['private', 'team']"], f"got {_got!r}"
_got = validate({"title": "t", "body": "b", "visibility": "team", "zeta": 1, "alpha": 2}, _schema)
assert _got == ["alpha: unexpected field", "zeta: unexpected field"], f"unknown keys come last, sorted; got {_got!r}"
_got = validate({"title": "t", "body": "b", "visibility": "team", "priority": 9}, _schema)
assert _got == ["priority: above maximum 5"], f"got {_got!r}"
assert validate("not a body", _schema) == ["body: expected object, got string"], f"got {validate('not a body', _schema)!r}"
assert validate({}, {"type": "object", "fields": {}}) == [], "an empty schema accepts an empty body"
'''},
                    {"name": "the suite is generated from the contract", "code": r'''
_endpoint = CONTRACT["endpoints"][0]
_cases = conformance_cases(_endpoint)
assert len(_cases) == 16, f"this endpoint implies 16 cases (1 positive, 14 constraint violations, 1 extra key); got {len(_cases)}"
assert _cases[0]["name"] == "POST /notes: minimal valid body", f"the positive case comes first; got {_cases[0]['name']!r}"
assert _cases[0]["expect"] == 201, f"the positive case expects the endpoint's success code, got {_cases[0]['expect']!r}"
assert _cases[-1]["name"] == "POST /notes: unexpected field", f"the extra-key case comes last; got {_cases[-1]['name']!r}"
_names = [c["name"] for c in _cases]
for _needed in ["POST /notes: title missing", "POST /notes: title too short",
                "POST /notes: title too long", "POST /notes: priority below minimum",
                "POST /notes: priority above maximum", "POST /notes: visibility outside the enum",
                "POST /notes: pinned wrong type"]:
    assert _needed in _names, f"missing generated case {_needed!r} from {_names!r}"
assert "POST /notes: priority missing" not in _names, "priority is optional, so omitting it is legal"
'''},
                    {"name": "every generated case agrees with the validator", "code": r'''
_endpoint = CONTRACT["endpoints"][0]
_schema = _endpoint["request"]
for _case in conformance_cases(_endpoint):
    _errors = validate(_case["body"], _schema)
    if _case["expect"] == _endpoint["success"]:
        assert _errors == [], f"case {_case['name']!r} should be valid but the validator said {_errors!r}"
    else:
        assert _errors, f"case {_case['name']!r} expects 400 but the validator found nothing wrong with {_case['body']!r}"
    assert set(_case) == {"name", "method", "path", "body", "expect"}, f"unexpected case keys {sorted(_case)!r}"
    assert _case["method"] == "POST" and _case["path"] == "/notes", "each case carries its method and path"
'''},
                    {"name": "the diff decides the version bump", "code": r'''
import copy
_v1 = CONTRACT
_same = copy.deepcopy(_v1)
assert diff_contracts(_v1, _same) == {"breaking": [], "additive": []}, "an unchanged contract diffs to nothing"
assert required_bump(_v1, _same) == "patch" and next_version(_v1, _same) == "1.4.3", \
    f"a neutral change is a patch bump; got {next_version(_v1, _same)!r}"

_optional = copy.deepcopy(_v1)
_optional["endpoints"][0]["request"]["fields"]["colour"] = {"type": "string", "optional": True}
assert diff_contracts(_v1, _optional)["breaking"] == [], "a new optional field breaks nobody"
assert diff_contracts(_v1, _optional)["additive"] == ["POST /notes: new optional field colour"], \
    f"got {diff_contracts(_v1, _optional)['additive']!r}"
assert next_version(_v1, _optional) == "1.5.0", f"additive means a minor bump; got {next_version(_v1, _optional)!r}"

_required = copy.deepcopy(_v1)
_required["endpoints"][0]["request"]["fields"]["colour"] = {"type": "string"}
assert diff_contracts(_v1, _required)["breaking"] == ["POST /notes: new required field colour"], \
    f"got {diff_contracts(_v1, _required)['breaking']!r}"
assert next_version(_v1, _required) == "2.0.0", "a new required field forces a major bump, zeroing minor and patch"

_narrowed = copy.deepcopy(_v1)
_narrowed["endpoints"][0]["request"]["fields"]["visibility"]["enum"] = ["private"]
assert required_bump(_v1, _narrowed) == "major", "losing an enum value breaks callers who send it"
_widened = copy.deepcopy(_v1)
_widened["endpoints"][0]["request"]["fields"]["visibility"]["enum"] = ["private", "team", "public"]
assert required_bump(_v1, _widened) == "minor", "gaining an enum value is additive"
_gone = copy.deepcopy(_v1)
_gone["endpoints"] = []
assert diff_contracts(_v1, _gone)["breaking"] == ["removed endpoint POST /notes"], \
    f"got {diff_contracts(_v1, _gone)['breaking']!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "The persistence layer",
            "summary": "Forward migrations, a repository, parameterised SQL, real transactions.",
            "concepts": [
                "Schema changes are forward-only, numbered, and recorded in the database itself",
                "A migration runner is idempotent: re-running it applies nothing",
                "The repository pattern keeps SQL in one place and hands the caller plain dicts",
                "String-formatted SQL is an injection hole; placeholders make the value data, never code",
                "A multi-row write is one transaction: BEGIN, then COMMIT or ROLLBACK, never half",
                "Python's sqlite3 in autocommit mode (`isolation_level = None`) makes those boundaries explicit",
                "LIMIT/OFFSET pagination needs a deterministic ORDER BY or pages overlap",
            ],
            "read": [
                {
                    "title": "Three databases that disagree, and the table that settles it",
                    "minutes": 15,
                    "body": r'''
A deploy goes out on a Tuesday afternoon and the service starts returning 500s from one
endpoint. The stack trace says `no such column: notes.archived`. On your laptop the
column is there. On staging it is there. On production it is not, because in March
somebody added it to staging by hand at the psql prompt during an incident, wrote the
same statement into a wiki page, and the wiki page is not what deploys.

That is the whole problem of schema evolution in one paragraph. The code is versioned,
reviewed and shipped as a unit; the schema is a side effect of whoever ran what, where,
and the two drift apart silently until a query names a column one of them has never
heard of. You cannot diff a running database against a wiki page.

## Let the database say what it is

The only description of the schema that cannot drift is one stored *inside* the database
it describes. So keep a table:

```text
schema_version(version INTEGER PRIMARY KEY, applied_at INTEGER NOT NULL)
```

and a list of migrations in the code, numbered, each a small batch of statements. The
runner compares the two: apply every migration whose number is above the highest row in
that table, insert a row for each one as it lands. Now "which schema is this database
at" is a query, not a memory, and the answer is the same whether you ask your laptop,
staging or production.

Two properties fall straight out of that design and are worth naming, because both are
things the runner must be *written* to have.

It is **idempotent**: run it twice and the second run applies nothing, because every
migration is already recorded. That is what makes it safe to run on every deploy,
unconditionally, rather than as a step somebody remembers.

It is **forward-only**: there is no down migration. A rollback that discards a column
discards the data in it, so the recovery from a bad migration is a new migration
numbered higher, not a reversal.

```python
import sqlite3

MIGRATIONS = [
    (1, ["CREATE TABLE notes (id INTEGER PRIMARY KEY AUTOINCREMENT,"
         " title TEXT NOT NULL, body TEXT NOT NULL, author TEXT NOT NULL)"]),
    (2, ["ALTER TABLE notes ADD COLUMN archived INTEGER NOT NULL DEFAULT 0",
         "CREATE INDEX idx_notes_author ON notes(author)"]),
]


def schema_version(conn):
    """The highest applied migration, or 0 when the table does not exist yet."""
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'schema_version'"
    ).fetchone()
    if row is None:
        return 0
    return conn.execute("SELECT MAX(version) FROM schema_version").fetchone()[0] or 0


def migrate(conn):
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version ("
                 " version INTEGER PRIMARY KEY, applied_at INTEGER NOT NULL)")
    current = schema_version(conn)
    applied = []
    for version, statements in MIGRATIONS:
        if version <= current:
            continue
        conn.execute("BEGIN")
        try:
            for sql in statements:
                conn.execute(sql)
            conn.execute("INSERT INTO schema_version (version, applied_at)"
                         " VALUES (?, ?)", (version, 0))
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        applied.append(version)
    return schema_version(conn), applied


conn = sqlite3.connect(":memory:")
conn.isolation_level = None
print("before any run:", schema_version(conn))
print("first run: ", migrate(conn))
print("second run:", migrate(conn))
print("rows in schema_version:",
      conn.execute("SELECT COUNT(*) FROM schema_version").fetchone()[0])
```

It prints `before any run: 0`, then `first run:  (2, [1, 2])`, then
`second run: (2, [])`, then `rows in schema_version: 2`. The second run reaches the same
version having applied nothing, and the count stays at 2 rather than climbing to 4. That
empty list is the property the deploy pipeline depends on.

Notice what `schema_version` does *not* do. It asks `sqlite_master` whether the table
exists rather than running the `SELECT` and catching whatever comes back. Wrapping the
query in a bare `except` would answer 0 for a missing table, and it would also answer 0
for a locked file, a corrupt page and a typo in the column name — a database in trouble
reported as a fresh one, which is then migrated from scratch on top of live data. The
narrow question deserves the narrow check.

## Migrations run inside `BEGIN`, so you have to own the transaction

Migration 2 is two statements. If the `ALTER TABLE` succeeds and the `CREATE INDEX`
fails on a name collision, the database is at neither version 1 nor version 2, and no
row was written to say so. The next run starts at 1, tries the `ALTER TABLE` again and
fails on a duplicate column. The database is now stuck in a state the runner cannot
reason about.

Wrapping both statements plus the version row in one `BEGIN`/`COMMIT` removes that state
from existence: either the migration and its record land together or neither does. To do
that in Python you have to take the transaction away from the driver, which is what
`conn.isolation_level = None` means. The default sqlite3 module opens transactions
implicitly around some statements and commits at moments that are hard to predict from
reading your own code; setting it to `None` is autocommit mode, where every statement
stands alone *unless* you issue `BEGIN` yourself, and then it does exactly what you wrote
until you `COMMIT`. Explicit and slightly more typing beats implicit and occasionally
surprising, for something whose failure mode is a half-migrated production database.

## Placeholders make a value data, permanently

The repository is the layer that keeps every `SELECT` and `INSERT` in one file behind
plain method names. Its most important rule is one line long: every value the caller
supplied travels as a `?` parameter, never through string formatting.

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, title TEXT, author TEXT)")
conn.executemany("INSERT INTO notes (title, author) VALUES (?, ?)",
                 [("aisle plan", "ada"), ("pay rise", "grace"), ("door keys", "grace")])
conn.commit()

hostile = "nobody' OR author = 'grace"

formatted = "SELECT title FROM notes WHERE author = '{0}'".format(hostile)
print("the SQL that reaches SQLite:")
print("   ", formatted)
print("    returns:", [row[0] for row in conn.execute(formatted)])

rows = conn.execute("SELECT title FROM notes WHERE author = ?", (hostile,)).fetchall()
print("with a placeholder, returns:", [row[0] for row in rows])
```

The formatted version prints the statement it built —
`SELECT title FROM notes WHERE author = 'nobody' OR author = 'grace'` — and returns
`['pay rise', 'door keys']`, which are Grace's private notes handed to a caller who
asked for a user called `nobody`. The parameterised version returns `[]`, because it
looked for an author whose name is literally the 26 characters `nobody' OR author =
'grace` and there is not one.

The difference is not escaping. With a placeholder the SQL text is compiled once, with a
hole in it, and the value is handed to the engine afterwards as data — there is no
moment at which it could be parsed as SQL, so there is nothing for a quote to escape
from. This is why a title of `'; DROP TABLE notes; --` is a perfectly good title:
it round-trips byte for byte and the table is still standing, which is exactly what the
lab's test asserts.

The tempting mistake is to escape by hand — double the quotes, strip the semicolons —
because it feels like the same thing done more explicitly. It is not: it is a filter
that has to be right about every quoting rule of a dialect you did not write, it has to
be applied at every call site by everyone forever, and the one call site that forgets is
the whole hole. A placeholder is right by construction, and a repository is where you
put the rule so there is one place to check.

## All-or-nothing means re-raising, too

```python
import sqlite3


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.isolation_level = None
    conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, title TEXT NOT NULL)")
    return conn


def add(conn, title):
    if not str(title).strip():
        raise ValueError("a note needs a title")
    conn.execute("INSERT INTO notes (title) VALUES (?)", (title,))


def add_many_loose(conn, titles):
    for title in titles:
        add(conn, title)


def add_many(conn, titles):
    conn.execute("BEGIN")
    try:
        for title in titles:
            add(conn, title)
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise


batch = ["agenda", "budget", "   ", "duties"]

loose = fresh()
try:
    add_many_loose(loose, batch)
except ValueError:
    pass
print("no transaction: ", [r[0] for r in loose.execute("SELECT title FROM notes")])

strict = fresh()
try:
    add_many(strict, batch)
except ValueError:
    pass
print("one transaction:", [r[0] for r in strict.execute("SELECT title FROM notes")])
```

The loose version prints `['agenda', 'budget']` — two of a four-row import landed and
two did not, and no record anywhere says which. The transactional version prints `[]`.
A caller who retries the whole batch after fixing the third title gets four rows in the
first case and four rows in the second, but in the first case two of them are duplicates.

The half of this people leave out is the `raise` at the end of the `except`. Roll back
and then return quietly and the caller sees a successful call that wrote nothing, which
is worse than a failure: a failure is retried, and a silent success is not. The rollback
undoes the writes; the re-raise undoes the caller's belief.

## Pagination needs an order that does not move

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE notes (id INTEGER PRIMARY KEY, title TEXT)")
conn.executemany("INSERT INTO notes (title) VALUES (?)",
                 [("beta",), ("delta",), ("gamma",), ("zeta",)])
conn.commit()


def page(offset):
    rows = conn.execute(
        "SELECT title FROM notes ORDER BY title LIMIT 2 OFFSET ?", (offset,))
    return [row[0] for row in rows]


first = page(0)
print("page 1:", first)
conn.execute("INSERT INTO notes (title) VALUES ('alpha')")
conn.commit()
second = page(2)
print("page 2, after one insert:", second)
print("shown twice:", sorted(set(first) & set(second)))
print("never seen: alpha arrived at offset 0, which the reader had already gone past")
```

Page 1 is `['beta', 'delta']`. One insert later, page 2 is `['delta', 'gamma']`: `delta`
appears on both pages, and `alpha` — which now sorts first — is never shown at all,
because the reader passed offset 0 before it existed. `LIMIT`/`OFFSET` counts positions
in a result set that is recomputed for every request, so any change to the rows before
the offset shifts everything after it.

`ORDER BY id` is the defence the lab uses, and it is a defence rather than a cure: ids
are unique and never reordered, so at least ties cannot shuffle between requests and a
page cannot repeat a row because two rows compared equal. Ordering by a non-unique
column and nothing else is strictly worse — the engine is free to break the tie however
it likes on each call, so two requests for the same page can legitimately differ with
nothing having changed at all.

## Where this stops holding

SQLite's `ALTER TABLE` is a narrow instrument. It adds a column and renames things;
older builds cannot drop a column or change its type, and the standard workaround is to
build a new table, copy every row into it, drop the old one and rename — which is a
migration whose cost is proportional to the data rather than the schema. On a large
table that is minutes of held locks, and the one-transaction-per-migration rule that is
free here becomes a production decision about downtime.

The rule is not even portable. PostgreSQL runs DDL inside transactions much as SQLite
does; MySQL, for most of its history, commits implicitly on DDL, so a migration of two
`ALTER`s cannot be made atomic there at all and the runner has to be built around that
instead of assuming it away.

Forward-only migrations also say nothing about *data*. Adding `archived INTEGER NOT NULL
DEFAULT 0` is instant; backfilling a computed value into forty million existing rows is
a batched job with its own progress table, and squeezing it into a migration is how a
deploy times out holding a lock on the busiest table in the service.

And the repository's own shape has a limit. Handing back a list of plain dicts is what
makes it easy to test and easy to swap, and it also means the whole page is in memory
before the caller sees the first row. That is right for a page of 10 and wrong for an
export of a million, which wants a cursor and a different method.

## What you are about to build

The lab, **Migrations and a note repository**, is those two halves side by side:
`connect` with `sqlite3.Row`, autocommit and foreign keys on; `schema_version` that does
not lie about a virgin database; `migrate` that is idempotent, transactional and
stoppable at a target version; and `NoteRepo` with `add`, `get`, `list_by_author`,
`count`, `update_title`, `delete` and an `add_many` that leaves nothing behind when one
row in the batch is bad. The tests feed it `'; DROP TABLE notes; --` as a title and then
check that the table is still there, which is the one assertion in this course that most
directly protects the capstone.
''',
                },
            ],
            "quiz": {
                "title": "Migrations, placeholders, transactions and pages",
                "minutes": 8,
                "questions": [
                    {
                        "q": "`migrate(conn)` is called a second time against a database already recorded at version 2. What must happen?",
                        "opts": [
                            "Both migrations are replayed, which is safe because each statement is written idempotently",
                            "Nothing is applied, and `schema_version` still holds exactly the two rows it already held",
                            "The schema is rolled back to version 0 and the whole list is then replayed from the start",
                            "The call raises, since re-running an applied migration is a deploy mistake worth reporting",
                        ],
                        "a": 1,
                        "whys": [
                            r"`ALTER TABLE ... ADD COLUMN` has no `IF NOT EXISTS` form, so a replayed migration 2 fails on a duplicate column. Writing every statement to tolerate a replay is far more work than recording which ones ran.",
                            r"Every migration below the recorded version is skipped, so a second run reaches the same version having done nothing at all.",
                            r"There is no down path — that is the point of forward-only. Rolling back to 0 would drop the `notes` table and the data in it before replaying, which is a restore from backup, not a migration.",
                            r"Then the runner could not be run unconditionally on every deploy, which is the property that keeps the schema and the code shipping together. A no-op is the correct outcome, not an error.",
                        ],
                        "why": r"""
Idempotence is why `migrate` can be wired into the deploy pipeline with no condition
around it: every environment converges on the same schema whether it was three
versions behind or already current. The runner gets it by comparing the migration
list against the rows in `schema_version` and skipping anything at or below the
current number — so the second run applies nothing, writes no row, and returns the
same version. A runner that instead relied on each statement tolerating a replay
would have to be right about every statement, forever.
""",
                    },
                    {
                        "q": "Why should `schema_version` ask `sqlite_master` whether its table exists, rather than running the `SELECT` and catching the failure?",
                        "opts": [
                            "Because a `SELECT` against a missing table succeeds in SQLite and returns an empty result",
                            "Because a broad `except` would report a locked file or a corrupt page as a fresh database",
                            "Because reading `sqlite_master` is faster than a `SELECT MAX(version)` over two short rows",
                            "Because the table can exist while holding no rows, and that third case needs its own branch",
                        ],
                        "a": 1,
                        "whys": [
                            r"It does not succeed — SQLite raises `OperationalError: no such table`. If it did return empty rows there would be no exception to catch and no question to answer.",
                            r"The catch cannot tell the one expected failure from every other one, so a database in trouble is reported as a database that is brand new.",
                            r"Speed is irrelevant at this size and is not why the check exists. Both queries are trivial; the difference between them is what each one is capable of getting wrong.",
                            r"That case is real and is handled by the `or 0` on the aggregate, which turns a `MAX` over no rows into 0. It is a separate concern from deciding whether to run the query at all.",
                        ],
                        "why": r"""
The failure being caught is `no such table`, and a bare `except` catches everything
else too: a locked database, a corrupt page, a permissions error, a column renamed by
a bad merge. Every one of them is reported as version 0, and version 0 means "virgin
database, apply everything", so the runner then executes `CREATE TABLE` statements
against a live database that was merely unavailable for a moment. Asking a question
whose answer is a fact — is this table in `sqlite_master` — keeps the unexpected
failures unexpected, which is where they can still be seen.
""",
                    },
                    {
                        "q": "A note is stored with the title `'; DROP TABLE notes; --` through a `?` placeholder, then read back. What comes back, and why?",
                        "opts": [
                            "Nothing: SQLite refuses the parameter, since a value may not carry SQL punctuation",
                            "The title unchanged, since a parameter is handed over as data and never parsed as SQL",
                            "The title with each quote doubled, since the driver escapes the value before sending it",
                            "Nothing: the statement runs as two statements and the table it selected from has gone",
                        ],
                        "a": 1,
                        "whys": [
                            r"SQLite has no opinion about what characters a text value contains — punctuation, semicolons and comment markers are all bytes and nothing more once the value is a parameter rather than part of the statement.",
                            r"The statement is compiled with a hole in it and the value arrives afterwards, so there is no point at which it could be read as SQL.",
                            r"Escaping is the mechanism people assume, and assuming it is how the hand-rolled version gets written. If the driver escaped, the stored text would differ from what was sent — it does not, because nothing was rewritten.",
                            r"That is what the formatted version would do, and it is the attack the placeholder prevents. `execute` also refuses to run two statements at once, so even the string-built version fails differently than expected.",
                        ],
                        "why": r"""
A placeholder splits the operation in two: the SQL text is parsed and compiled once,
with a hole where the value goes, and the value is bound afterwards. Parsing has
already finished by the time the engine sees the bytes, so a quote in the value has
nothing to close and a semicolon has nothing to separate. The value is not escaped
and not filtered, which is why it round-trips byte for byte — the reason the lab's
test checks both that the title comes back verbatim *and* that the `notes` table is
still in `sqlite_master`.
""",
                    },
                    {
                        "q": "`add_many` catches the `ValueError` from a blank title, issues a `ROLLBACK`, and returns an empty list rather than re-raising. What has that cost?",
                        "opts": [
                            "The rows are written anyway, because a rollback cannot undo statements already run",
                            "The caller reads the empty list as a batch of no rows and never learns a title was bad",
                            "The connection is left inside an open transaction, so the next write on it blocks forever",
                            "The `schema_version` row for the last migration is rolled back together with the batch",
                        ],
                        "a": 1,
                        "whys": [
                            r"The rollback does its job — that is exactly what a transaction is for, and the uncommitted inserts are discarded. The damage here is to what the caller believes, not to what the table holds.",
                            r"A silent success is not retried, and an import that quietly wrote nothing looks identical to an import of an empty file.",
                            r"`ROLLBACK` closes the transaction as surely as `COMMIT` does, so the connection is left perfectly usable. Swallowing the exception is a reporting bug, not a connection-state bug.",
                            r"That row was committed by its own migration long before, in a separate transaction. A rollback undoes only the work inside the transaction it ends.",
                        ],
                        "why": r"""
All-or-nothing is two guarantees, and the transaction only supplies one of them. The
`ROLLBACK` makes sure no partial write survives; the `raise` makes sure the caller
knows the batch did not happen. Drop the second and the failure becomes indistinguishable
from success on an empty input — the importer logs "0 rows", the operator assumes the
file was empty, and the four notes have vanished. A failure that propagates gets
retried after the bad title is fixed; a failure that returns quietly gets filed away.
""",
                    },
                    {
                        "q": "Page 1 is read with `ORDER BY title LIMIT 2 OFFSET 0`. A note that sorts before all of them is then inserted. Page 2 reads `OFFSET 2`. What goes wrong?",
                        "opts": [
                            "Nothing at all, since `ORDER BY title` is deterministic and each page is computed afresh",
                            "One row appears on both pages, and the row that was newly inserted is never shown at all",
                            "The second query raises, because the offset now exceeds the number of rows in the table",
                            "Page 2 repeats page 1 exactly, because every row after the insert has shifted by two places",
                        ],
                        "a": 1,
                        "whys": [
                            r"Each page really is computed afresh, and that is the cause rather than the cure: the two requests are ordering *different* sets of rows, so the same offset points at a different place in each.",
                            r"Everything after the new row shifts one position later, so the row at the old offset 1 is now at offset 2 and is read twice.",
                            r"An offset past the end returns an empty page rather than raising, and here the offset is well inside the table anyway — the table grew rather than shrank.",
                            r"One insert shifts by one position, not two. Only a single row straddles the boundary and repeats; the rest of page 2 is new to the reader.",
                        ],
                        "why": r"""
`LIMIT`/`OFFSET` counts positions in a result set that is rebuilt for every request,
so it is only stable while the rows before the offset do not change. Insert one row
that sorts ahead of the offset and everything after it slides one place: the row that
ended page 1 now begins page 2 and is shown twice, while the new row sits at a
position the reader has already gone past and is never shown. `ORDER BY id` does not
fix that, but it does remove the other half of the problem — with a unique ordering
key, two requests for the same unchanged page can never disagree because a tie was
broken differently.
""",
                    },
                    {
                        "q": "What does setting `conn.isolation_level = None` on a `sqlite3` connection actually change?",
                        "opts": [
                            "It turns off durability so writes are faster, at the price of losing them in a crash",
                            "It selects autocommit, so `BEGIN`, `COMMIT` and `ROLLBACK` become yours to issue by hand",
                            "It puts each statement in a transaction of its own that no other statement can join",
                            "It hides uncommitted rows from other connections, which is what the isolation level names",
                        ],
                        "a": 1,
                        "whys": [
                            r"Durability is governed by the `synchronous` pragma and the journal mode, neither of which this touches. Nothing here trades safety for speed.",
                            r"The driver stops opening transactions on your behalf, which is the only way to put several statements inside one boundary you chose.",
                            r"That describes what happens to a statement you do *not* wrap, and it is half true — but the important half is that an explicit `BEGIN` does let following statements join, and that is precisely what a migration needs.",
                            r"Uncommitted rows are already invisible to other connections; that is what a transaction does everywhere. This setting is about who issues the transaction statements, not about what other readers can see.",
                        ],
                        "why": r"""
By default the sqlite3 module opens a transaction for you before certain statements
and commits at points that are hard to predict while reading your own code. Setting
`isolation_level = None` hands that back: every statement stands alone unless you have
issued `BEGIN`, and after a `BEGIN` nothing is committed until you say so. That is the
prerequisite for both of this module's atomic operations — a migration whose statements
and version row land together, and an `add_many` that leaves no partial batch — because
neither can be expressed at all while the driver is choosing the boundaries.
""",
                    },
                ],
            },
            "lab": {
                "title": "Migrations and a note repository",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
`MIGRATIONS` is given: a list of `(version, [sql, ...])` applied in order.

**`connect(path=":memory:")`** — a `sqlite3.Connection` with
`row_factory = sqlite3.Row`, `isolation_level = None` (so *you* own the
transaction boundaries) and `PRAGMA foreign_keys = ON`.

**`schema_version(conn)`** — the highest applied version, or `0` when the
`schema_version` table does not exist yet. Look it up in `sqlite_master`; do not
catch a broad exception and guess.

**`migrate(conn, target=None)`** — create `schema_version(version INTEGER
PRIMARY KEY, applied_at INTEGER NOT NULL)` if absent, then apply every migration
above the current version (stopping after `target` when given). Each migration
runs inside its own `BEGIN` / `COMMIT`, with a `ROLLBACK` and a re-raise if any
statement fails, and records its row. Returns the resulting version.

**`class NoteRepo`** over that connection, returning dicts shaped
`{"id", "title", "body", "author", "archived"}` with `archived` a `bool`:

- `add(title, body, author)` -> the new id; `ValueError` when `title` or `author` is blank or whitespace
- `get(note_id)` -> the dict, or `None`
- `list_by_author(author, limit=10, offset=0)` -> notes for one author, ordered by id
- `count(author=None)` -> all rows, or one author's
- `update_title(note_id, title)` -> `True` when a row changed; `ValueError` on a blank title
- `delete(note_id)` -> `True` when a row went
- `add_many(rows)` -> a list of ids for `[(title, body), ...]`, all-or-nothing: one bad title and *none* of them land

Every value reaches SQLite through a `?` placeholder. A title of
`'; DROP TABLE notes; --` is a perfectly good title and must come back byte for
byte, with the table still standing.
''',
                "files": [{"name": "main.py", "content": r'''
import sqlite3
import time

MIGRATIONS = [
    (1, [
        "CREATE TABLE notes ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " title TEXT NOT NULL,"
        " body TEXT NOT NULL,"
        " author TEXT NOT NULL)",
    ]),
    (2, [
        "ALTER TABLE notes ADD COLUMN archived INTEGER NOT NULL DEFAULT 0",
        "CREATE INDEX idx_notes_author ON notes(author)",
    ]),
]


def connect(path=":memory:"):
    """A connection with Row rows, explicit transactions and foreign keys on."""
    # your code here


def schema_version(conn):
    """The highest applied migration, or 0 on a virgin database."""
    # your code here


def migrate(conn, target=None):
    """Apply pending migrations in order; returns the resulting version."""
    # your code here


class NoteRepo:
    """Every query parameterised, every multi-row write transactional."""

    def __init__(self, conn):
        self.conn = conn

    def add(self, title, body, author):
        """Insert one note and return its id."""
        # your code here

    def get(self, note_id):
        """One note as a dict, or None."""
        # your code here

    def list_by_author(self, author, limit=10, offset=0):
        """One author's notes, ordered by id."""
        # your code here

    def count(self, author=None):
        """How many notes, in total or for one author."""
        # your code here

    def update_title(self, note_id, title):
        """True when a row changed."""
        # your code here

    def delete(self, note_id):
        """True when a row went."""
        # your code here

    def add_many(self, rows):
        """All-or-nothing insert of [(title, body), ...] for one author."""
        # your code here


conn = connect()
print("schema version:", migrate(conn))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import sqlite3
import time

MIGRATIONS = [
    (1, [
        "CREATE TABLE notes ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " title TEXT NOT NULL,"
        " body TEXT NOT NULL,"
        " author TEXT NOT NULL)",
    ]),
    (2, [
        "ALTER TABLE notes ADD COLUMN archived INTEGER NOT NULL DEFAULT 0",
        "CREATE INDEX idx_notes_author ON notes(author)",
    ]),
]


def connect(path=":memory:"):
    """A connection with Row rows, explicit transactions and foreign keys on."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.isolation_level = None
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def schema_version(conn):
    """The highest applied migration, or 0 on a virgin database."""
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'schema_version'"
    ).fetchone()
    if row is None:
        return 0
    row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
    return row["v"] or 0


def migrate(conn, target=None):
    """Apply pending migrations in order; returns the resulting version."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version ("
        " version INTEGER PRIMARY KEY, applied_at INTEGER NOT NULL)"
    )
    current = schema_version(conn)
    for version, statements in MIGRATIONS:
        if version <= current:
            continue
        if target is not None and version > target:
            break
        conn.execute("BEGIN")
        try:
            for sql in statements:
                conn.execute(sql)
            conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                (version, int(time.time())),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    return schema_version(conn)


class NoteRepo:
    """Every query parameterised, every multi-row write transactional."""

    def __init__(self, conn):
        self.conn = conn

    @staticmethod
    def _row(row):
        return {"id": row["id"], "title": row["title"], "body": row["body"],
                "author": row["author"], "archived": bool(row["archived"])}

    def add(self, title, body, author):
        """Insert one note and return its id."""
        if not str(title).strip():
            raise ValueError("a note needs a title")
        if not str(author).strip():
            raise ValueError("a note needs an author")
        cur = self.conn.execute(
            "INSERT INTO notes (title, body, author) VALUES (?, ?, ?)",
            (title, body, author),
        )
        return cur.lastrowid

    def get(self, note_id):
        """One note as a dict, or None."""
        row = self.conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return self._row(row) if row is not None else None

    def list_by_author(self, author, limit=10, offset=0):
        """One author's notes, ordered by id."""
        rows = self.conn.execute(
            "SELECT * FROM notes WHERE author = ? ORDER BY id LIMIT ? OFFSET ?",
            (author, limit, offset),
        ).fetchall()
        return [self._row(row) for row in rows]

    def count(self, author=None):
        """How many notes, in total or for one author."""
        if author is None:
            row = self.conn.execute("SELECT COUNT(*) AS c FROM notes").fetchone()
        else:
            row = self.conn.execute(
                "SELECT COUNT(*) AS c FROM notes WHERE author = ?", (author,)).fetchone()
        return row["c"]

    def update_title(self, note_id, title):
        """True when a row changed."""
        if not str(title).strip():
            raise ValueError("a note needs a title")
        cur = self.conn.execute(
            "UPDATE notes SET title = ? WHERE id = ?", (title, note_id))
        return cur.rowcount > 0

    def delete(self, note_id):
        """True when a row went."""
        cur = self.conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cur.rowcount > 0

    def add_many(self, rows):
        """All-or-nothing insert of [(title, body), ...] for one author."""
        self.conn.execute("BEGIN")
        try:
            ids = [self.add(title, body, author) for title, body, author in rows]
            self.conn.execute("COMMIT")
            return ids
        except Exception:
            self.conn.execute("ROLLBACK")
            raise


conn = connect()
print("schema version:", migrate(conn))
'''}],
                "hints": [
                    "`isolation_level = None` puts sqlite3 in autocommit mode, so `BEGIN`, `COMMIT` and `ROLLBACK` are yours to issue — that is the only way to make a migration atomic across several statements.",
                    "`schema_version` on an empty database must not raise: ask `sqlite_master` whether the table exists before selecting from it.",
                    "`cursor.rowcount` after an UPDATE or DELETE tells you whether anything matched; `cursor.lastrowid` after an INSERT gives the new id.",
                    "In `add_many`, wrap the whole loop in one BEGIN/COMMIT and re-raise after ROLLBACK — swallowing the error leaves the caller believing a partial write succeeded.",
                ],
                "tests": [
                    {"name": "the connection is configured for explicit transactions", "code": r'''
import sqlite3
_c = connect()
assert _c.isolation_level is None, f"isolation_level should be None (autocommit), got {_c.isolation_level!r}"
assert _c.row_factory is sqlite3.Row, "row_factory should be sqlite3.Row so rows index by column name"
assert _c.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "foreign key enforcement must be switched on"
'''},
                    {"name": "migrations run once, in order", "code": r'''
_c = connect()
assert schema_version(_c) == 0, f"a virgin database is at version 0, got {schema_version(_c)!r}"
assert migrate(_c) == 2, f"migrate should reach version 2, got {migrate(connect())!r}"
assert schema_version(_c) == 2, "the version must be recorded in the database, not in a variable"
_rows = _c.execute("SELECT COUNT(*) AS c FROM schema_version").fetchone()["c"]
assert _rows == 2, f"one row per applied migration, expected 2 got {_rows}"
assert migrate(_c) == 2, "migrate must be idempotent"
assert _c.execute("SELECT COUNT(*) AS c FROM schema_version").fetchone()["c"] == 2, \
    "re-running migrate must not add rows"
_partial = connect()
assert migrate(_partial, 1) == 1, "target = 1 stops after the first migration"
_cols = [d[0] for d in _partial.execute("SELECT * FROM notes").description]
assert "archived" not in _cols, f"migration 2 must not have run; columns are {_cols!r}"
assert migrate(_partial) == 2, "the rest can be applied later"
assert "archived" in [d[0] for d in _partial.execute("SELECT * FROM notes").description]
'''},
                    {"name": "add and get round-trip, blanks are refused", "code": r'''
_c = connect()
migrate(_c)
_repo = NoteRepo(_c)
_id = _repo.add("Design review", "aisle plan", "ada")
assert _id == 1, f"the first note gets id 1, got {_id!r}"
_note = _repo.get(_id)
assert _note == {"id": 1, "title": "Design review", "body": "aisle plan",
                 "author": "ada", "archived": False}, f"get returned {_note!r}"
assert _repo.get(999) is None, "an unknown id gives None, not an exception"
assert _repo.count() == 1 and _repo.count("ada") == 1 and _repo.count("bob") == 0, \
    f"counts are wrong: {_repo.count()!r}, {_repo.count('ada')!r}, {_repo.count('bob')!r}"
_c = connect()
migrate(_c)
_repo = NoteRepo(_c)
for _bad in [("", "b", "ada"), ("   ", "b", "ada"), ("t", "b", ""), ("t", "b", "  ")]:
    try:
        _repo.add(*_bad)
        assert False, f"add{_bad!r} should raise ValueError"
    except ValueError:
        pass
assert _repo.count() == 0, f"a refused add must leave the table empty, found {_repo.count()} rows"
_id = _repo.add("ok", "b", "ada")
try:
    _repo.update_title(_id, "  ")
    assert False, "update_title with a blank title should raise ValueError"
except ValueError:
    pass
assert _repo.get(_id)["title"] == "ok", "the refused update must not have landed"
'''},
                    {"name": "pagination is ordered and stable", "code": r'''
_c = connect()
migrate(_c)
_repo = NoteRepo(_c)
for _i in range(7):
    _repo.add(f"note {_i}", "body", "ada" if _i % 2 == 0 else "bob")
_page = _repo.list_by_author("ada", limit=2, offset=0)
assert [n["title"] for n in _page] == ["note 0", "note 2"], f"first page is {_page!r}"
_page = _repo.list_by_author("ada", limit=2, offset=2)
assert [n["title"] for n in _page] == ["note 4", "note 6"], f"second page is {_page!r}"
assert _repo.list_by_author("ada", limit=2, offset=99) == [], "an offset past the end gives an empty page"
assert _repo.count("ada") == 4 and _repo.count("bob") == 3, "counts must respect the author filter"
assert _repo.count() == 7, f"seven notes in total, got {_repo.count()!r}"
'''},
                    {"name": "update, delete and their return values", "code": r'''
_c = connect()
migrate(_c)
_repo = NoteRepo(_c)
_id = _repo.add("old", "body", "ada")
assert _repo.update_title(_id, "new") is True, "updating an existing row returns True"
assert _repo.get(_id)["title"] == "new", "the new title must be persisted"
assert _repo.update_title(999, "new") is False, "updating a missing row returns False"
assert _repo.delete(_id) is True, "deleting an existing row returns True"
assert _repo.get(_id) is None and _repo.count() == 0, "the row must really be gone"
assert _repo.delete(_id) is False, "deleting it again returns False"
'''},
                    {"name": "placeholders make values data, not code", "code": r'''
_c = connect()
migrate(_c)
_repo = NoteRepo(_c)
_evil = "'; DROP TABLE notes; --"
_id = _repo.add(_evil, _evil, "ada")
assert _repo.get(_id)["title"] == _evil, f"the title must survive verbatim, got {_repo.get(_id)['title']!r}"
_tables = {r[0] for r in _c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
assert "notes" in _tables, f"the notes table must still exist; tables are {sorted(_tables)!r}"
assert _repo.count() == 1, "and it should still hold exactly the one note"
_src = open("main.py").read()
assert "% (" not in _src and ".format(" not in _src, "build SQL values with ? placeholders, never string formatting"
'''},
                    {"name": "add_many is all-or-nothing", "code": r'''
_c = connect()
migrate(_c)
_repo = NoteRepo(_c)
_ids = _repo.add_many([("a", "1", "ada"), ("b", "2", "ada"), ("c", "3", "ada")])
assert _ids == [1, 2, 3], f"add_many returns the new ids in order, got {_ids!r}"
assert _repo.count() == 3, f"three rows expected, found {_repo.count()}"
try:
    _repo.add_many([("d", "4", "ada"), ("   ", "5", "ada"), ("f", "6", "ada")])
    assert False, "a blank title inside the batch must propagate the ValueError"
except ValueError:
    pass
assert _repo.count() == 3, f"the whole batch must roll back; found {_repo.count()} rows instead of 3"
assert [n["title"] for n in _repo.list_by_author("ada")] == ["a", "b", "c"], "no partial row may survive"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "The service layer",
            "summary": "Domain rules, credentials, authorisation, and errors that become statuses.",
            "concepts": [
                "The service layer owns the rules; the repository owns storage; neither knows HTTP",
                "Passwords are stored as salted, iterated hashes — PBKDF2-HMAC-SHA256 with a per-user salt",
                "`hmac.compare_digest` compares in constant time; `==` leaks by timing",
                "Authentication answers *who*; authorisation answers *may they* — separate checks, separate codes",
                "A uniform 'username or password is wrong' prevents account enumeration",
                "An exception hierarchy carrying `status` and `code` maps the domain onto HTTP in one place",
                "Unexpected exceptions become a generic 500: internals never travel to the caller",
            ],
            "read": [
                {
                    "title": "A leaked table, a repeated digest, and the difference between who and may",
                    "minutes": 16,
                    "body": r'''
A backup of a `users` table turns up on a forum. Three columns: `username`, `password`,
`role`. Whatever is in that `password` column is now, permanently, the property of
everyone who downloads the file. There is no patch you can deploy that takes it back.
The only question left is what the column was worth, and that was decided by a choice
somebody made in an afternoon, months earlier.

Suppose it holds a plain SHA-256 of each password. Hashing is one-way, so this feels
safe. Look at what the dump says before anybody starts cracking:

```python
import hashlib

dump = [("ada", "correct horse"), ("grace", "hunter2"), ("linus", "correct horse")]

print("stored as a bare SHA-256 of the password:")
for username, password in dump:
    digest = hashlib.sha256(password.encode("utf-8")).hexdigest()
    print("   {0:<7}{1}".format(username, digest[:32]))

salts = {"ada": b"3f2a9c11", "grace": b"91c74d80", "linus": b"be0417a6"}
print("stored with a per-user salt:")
for username, password in dump:
    digest = hashlib.sha256(salts[username] + password.encode("utf-8")).hexdigest()
    print("   {0:<7}{1}".format(username, digest[:32]))
```

In the first block `ada` and `linus` print the identical digest `4104d36f8da2c254…`.
Nobody has cracked anything and the dump has already said: these two people use the same
password. Crack one and you have both. It also says, across a million rows, which
password is the *most popular* — sort by digest, take the biggest group, and you know
which single guess will open the most accounts before you have made any.

The second block gives each user a different salt, and the two identical passwords print
completely different digests. That is the whole job of a salt: not to make one hash
harder, but to destroy the structure *between* hashes. A precomputed table of common
passwords is now useless, because it would have to be recomputed for every salt, and
work an attacker does against Ada buys nothing at all against Linus.

## Iterations buy time, and you can price them

A salt does not slow anybody down. One password, one candidate list, one salt — the
attacker still runs through the list at whatever rate the hardware allows. What slows
them is making each attempt cost more, deliberately, by hashing the hash thousands of
times over. PBKDF2 is that idea and very little else.

The cost is worth doing the arithmetic on rather than asserting:

```python
GUESSES_PER_SECOND = 2000000000   # a rented rig, one plain SHA-256 per guess
CANDIDATES = 10 ** 10             # a ten-billion-entry cracking list

for iterations in (1, 1000, 50000, 600000):
    seconds = CANDIDATES * iterations / GUESSES_PER_SECOND
    print("{0:>7} rounds -> {1:>13,.0f} seconds = {2:>8,.1f} days for one user".format(
        iterations, seconds, seconds / 86400))
```

One round: the whole ten-billion list in five seconds. A thousand rounds: 5,000 seconds,
call it an afternoon. Fifty thousand: 2.9 days. Six hundred thousand: 34.7 days. And
because of the salt, every one of those numbers is *per user* — a dump of ten thousand
accounts at 600,000 rounds is 950 machine-years to grind exhaustively, against about
fourteen hours for the unsalted single-round version of the same file.

That is why `DEFAULT_ITERATIONS` is a number you will want to raise, and why it is
stored inside the hash string as `pbkdf2_sha256$<iterations>$<salt>$<digest>` rather
than living in a constant. Every stored hash records the cost it was made at, so raising
the constant tomorrow does not invalidate a single existing password: old hashes verify
at their own recorded count, and each one can be re-hashed at the new count on the next
successful login, when the plaintext is briefly in hand. A constant on its own forces a
choice between never raising it and locking out every user at once.

The lab uses 1,000 rounds because it runs in a browser tab. Treat that number as a
staging prop, not a recommendation.

## Comparison leaks, one character at a time

Verification re-derives the digest and compares it with the stored one. The comparison
looks like the least interesting line in the file.

```python
def naive_equal(a, b):
    """A byte-at-a-time comparison that stops at the first difference."""
    examined = 0
    if len(a) != len(b):
        return False, examined
    for x, y in zip(a, b):
        examined += 1
        if x != y:
            return False, examined
    return True, examined


secret = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
guesses = [
    ("wrong at the first character",
     "0f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"),
    ("wrong at position 41",
     "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b0b0b822cd15d6c15b0f00a08"),
    ("wrong at the last character",
     "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a09"),
    ("exactly right", secret),
]
for label, guess in guesses:
    same, examined = naive_equal(secret, guess)
    print("{0:<30}{1:>3} characters examined, match {2}".format(label, examined, same))
```

One character examined, then 41, then 64, then 64. Every one of those calls returns
`False` except the last, so the *answer* carries no information — but the amount of work
does, and work is time, and time is measurable over enough requests. An attacker who can
submit a candidate and time the response can hunt one character at a time: fix the first
character until the reply gets measurably slower, keep it, move to the second. Sixty-four
characters at sixteen possibilities each is a thousand or so probes rather than
$16^{64}$ guesses, and this is not a thought experiment — it is why `hmac.compare_digest`
exists and why it examines every byte regardless of what it finds.

`==` is what everybody writes, and it is right in every context except this one, which is
exactly why the mistake survives review. The rule is narrow enough to memorise: comparing
anything an attacker is trying to guess uses `compare_digest`.

## Two different refusals

Authentication asks *who are you*; authorisation asks *may you do this*. They fail for
unrelated reasons and so they get unrelated status codes, and confusing them is one of
the most common defects in a working service.

`401 unauthenticated` means the service does not know who is asking: no token, an expired
token, a token whose signature does not verify. The right next step for the caller is to
log in again. `403 forbidden` means the service knows precisely who is asking and the
answer is still no. Logging in again changes nothing; Ada logging in as Ada a second
time still may not edit Bob's note. Return 401 there and you have told a correctly
authenticated user to go and re-authenticate, which she will do, successfully, and be
refused again.

The two questions also come from different places. `authenticate` is one call at the
front of the request. `may_edit(user, resource)` needs the *resource*, so it cannot
happen until the note has been fetched — which is why the lab keeps `require_role` for
role checks that need nothing but the user, and `may_edit`/`authorise_edit` for
ownership checks that need both.

## The login message that says too much

```python
class AuthenticationError(Exception):
    pass


USERS = {"ada": "difference8"}


def chatty_login(username, password):
    if username not in USERS:
        raise AuthenticationError("no account with that username")
    if USERS[username] != password:          # naive on purpose; the message is the point
        raise AuthenticationError("wrong password")
    return {"username": username}


def uniform_login(username, password):
    stored = USERS.get(username)
    if stored is None or stored != password:
        raise AuthenticationError("username or password is wrong")
    return {"username": username}


for login in (chatty_login, uniform_login):
    seen = set()
    for attempt in [("ada", "wrong"), ("nobody", "wrong")]:
        try:
            login(*attempt)
        except AuthenticationError as exc:
            seen.add(str(exc))
    print("{0:<15}{1} distinct message(s): {2}".format(
        login.__name__, len(seen), sorted(seen)))
```

`chatty_login` produces two distinct messages, `uniform_login` one. Two messages turn the
login form into a membership oracle: feed it a list of email addresses and the ones that
come back "wrong password" are customers of this service. For a bank, a dating site or a
medical service, that list is the breach, whether or not a single password ever falls.

The chatty version is written on purpose, every time, because it is better user
experience and everybody knows it. The honest answer is that it is a trade, that the
uniform message costs a confused user one extra attempt, and that the enumeration is
worth more to an attacker than the clarity is worth to the user. The lab enforces it with
a test that collects the messages from three different failures and asserts there is one
distinct string among them.

## Errors that become statuses, exactly once

A service layer that knows about HTTP is a service layer you cannot test without HTTP.
The way out is an exception hierarchy that carries the mapping as data, translated at one
boundary:

```python
class ServiceError(Exception):
    status = 500
    code = "internal"


class NotFoundError(ServiceError):
    status = 404
    code = "not_found"


def to_response(exc):
    if isinstance(exc, ServiceError):
        return exc.status, {"error": {"code": exc.code, "message": str(exc)}}
    return 500, {"error": {"code": "internal", "message": "internal server error"}}


def leaky(exc):
    return 500, {"error": {"code": "internal", "message": str(exc)}}


boom = KeyError("users.password_hash")
print("documented failure:", to_response(NotFoundError("no such note")))
print("leaky handler:     ", leaky(boom))
print("this handler:      ", to_response(boom))
```

The second line prints a response body containing `users.password_hash`. Nobody decided
to publish that column name; a `KeyError` was raised four layers down and a helpful
handler forwarded its message. Repeat that across a service and the error bodies are a
guided tour of your table names, file paths and library versions, assembled by an
attacker for free from ordinary malformed requests.

The `isinstance` check is the entire discipline. A `ServiceError` is a failure somebody
wrote down deliberately, with a status and a message meant for a caller. Everything else
is a bug, and the caller gets a fixed string while the real message goes to the log with
a correlation id — which is the subject of the next module.

## Where this stops holding

A uniform login message closes one enumeration channel and leaves others open. The
registration endpoint still answers `409 conflict` for a name that is taken, which is
the same information through a different door; the fix there is a design decision about
the sign-up flow, not a message string. And the uniform path can still leak through
*timing*: if an unknown user returns immediately while a known one runs a full PBKDF2
derivation first, the clock tells the attacker what the message would not. Closing that
means hashing against a dummy record even when the user does not exist, which is a
deliberate waste of CPU that the lab does not ask for.

`compare_digest` protects the digest comparison and nothing else. The user lookup, the
database index, the JSON parser and the length of the response are all still doing
data-dependent work.

The permission model has a ceiling too. `may_edit` answers from a role and an owner
field, which covers "the owner or an admin" and stops there. It cannot express "editable
for 24 hours after creation", "editable by anyone in the same team", or a note shared
with three named people. Each of those needs rows rather than a function, and the moment
permissions become rows they need their own migrations, their own repository and their
own audit trail.

Finally, PBKDF2 is deliberately slow on a CPU and only on a CPU. Purpose-built hardware
runs it far faster than a server does, which is why scrypt and Argon2 were designed to
demand *memory* as well as time. PBKDF2 with a high round count is defensible and
standard; it is not the strongest thing available, and the round count is the only knob
it gives you.

## What you are about to build

The lab, **Credentials, authorisation and error mapping**, assembles all of it: the five
`ServiceError` subclasses carrying their own status and code; `to_response` with its one
`isinstance` check and its generic 500; `hash_password` producing
`pbkdf2_sha256$rounds$salt$digest` and refusing a password under eight characters or
without a digit; `verify_password` that re-derives at the recorded count, compares with
`hmac.compare_digest` and returns `False` rather than raising on a malformed stored
string; `UserStore` whose public dicts never carry the hash; and `require_role`,
`may_edit` and `authorise_edit` keeping the two refusals apart. The capstone then wraps
that layer in routes, and its security rubric is exactly the list above.
''',
                },
            ],
            "quiz": {
                "title": "Salts, rounds, constant time and the two refusals",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A leaked dump stores each password as a bare SHA-256. Two rows carry the identical digest. What has an attacker learned before cracking anything at all?",
                        "opts": [
                            "That SHA-256 has collided on this pair, so either password now opens either account",
                            "That those two accounts share a password, so one successful crack opens both of them",
                            "That the two rows were written in the same batch, since a digest also fixes the time",
                            "That the function is reversible after all, since a genuine one-way map cannot repeat",
                        ],
                        "a": 1,
                        "whys": [
                            r"A deliberate SHA-256 collision is a research result, not something you stumble on in a user table. Equal digests here mean equal inputs, and equal inputs mean the same password typed twice.",
                            r"Equal inputs hash equally, so a repeated digest is a repeated password, and the work spent on one row is already spent on the other.",
                            r"Nothing about when a row was written reaches the hash — only the password does, which is precisely the problem. Two accounts created years apart print the same digest if the password matches.",
                            r"Repetition is a property every deterministic function has, one-way or not. Reversing SHA-256 is still infeasible; what leaked was the relationship between rows, not the inputs.",
                        ],
                        "why": r"""
An unsalted hash is deterministic, so identical passwords produce identical rows and
the dump exposes the pattern of password reuse for free. At scale it is worse than a
hint: sort a million digests, take the largest group, and you know which single guess
opens the most accounts before making one. A per-user salt does not make any
individual hash harder to compute — it makes the rows unrelated, so an attacker's
work against one account transfers to no other, and a precomputed table has to be
rebuilt per salt.
""",
                    },
                    {
                        "q": "The stored hash records its own iteration count, as `pbkdf2_sha256$50000$…`. Why keep the count there rather than in a module constant?",
                        "opts": [
                            "So the verifier can drop it for slow clients and restore it once a login has succeeded",
                            "So the count can be raised later while hashes written at the old count still verify",
                            "So an attacker who reads the dump cannot know how many rounds a candidate needs",
                            "So each account can carry its own count, which is what makes a per-user salt work",
                        ],
                        "a": 1,
                        "whys": [
                            r"Lowering the cost on request would hand the choice to the caller, and an attacker is a caller. The count is a server-side decision that a client never negotiates.",
                            r"Each hash verifies at the count it was made with, so raising the constant affects new and re-hashed passwords only.",
                            r"It is written in the clear, right there in the string, and that is fine — the round count was never a secret. What it protects is not obscurity but the ability to change it.",
                            r"The salt does its work by being different per user; the count is uniform for everyone hashed on the same day. The two live in the same string and solve different problems.",
                        ],
                        "why": r"""
Hardware gets faster, so the round count has to rise over a service's life. If it
lived only in a constant, raising it would mean every stored hash was computed at a
count the code no longer uses, and there is no way to re-derive them — the plaintext
is gone. Recording the count alongside the salt makes each hash self-describing:
verification reads the count out of the string, so old and new coexist, and a password
can be quietly re-hashed at the new cost during the next successful login, when the
plaintext is briefly available.
""",
                    },
                    {
                        "q": "Comparing a derived digest with the stored one using `==` stops at the first differing character. Why does that matter when both digests are the same public length?",
                        "opts": [
                            "Because the characters after the first difference go unchecked, so a near miss can pass",
                            "Because how long the comparison takes reveals how many of the leading characters matched",
                            "Because `==` on strings tests identity first, so two equal digests can still compare unequal",
                            "Because the loop leaves the derivation half finished, which corrupts the hash that is stored",
                        ],
                        "a": 1,
                        "whys": [
                            r"The answer `==` gives is correct every time — it returns False the moment it can prove inequality, and the unchecked tail cannot change that. What leaks is not the verdict but the effort.",
                            r"A wrong first character costs one comparison and a wrong last one costs sixty-four, and that gap is measurable across enough requests.",
                            r"Python does check identity as a fast path, and then falls through to a full character comparison when the objects differ, so equal strings always compare equal. The shortcut is an optimisation, not a source of wrong answers.",
                            r"Nothing is stored during a verification and nothing is left half done — the derivation completes before the comparison starts. The two steps are entirely separate.",
                        ],
                        "why": r"""
The verdict carries no information; the timing does. An attacker who can submit a
candidate and measure the reply can fix one character at a time — try all sixteen
values for the first, keep whichever makes the response measurably slower, then move
along — turning an infeasible search into roughly a thousand probes. `hmac.compare_digest`
examines every byte whatever it finds and combines the results at the end, so the work
is the same for a value that is wrong everywhere and one that is wrong in a single
place. The rule worth memorising is narrow: anything an attacker is guessing at gets
compared with `compare_digest`, and everything else can use `==`.
""",
                    },
                    {
                        "q": "Ada presents a valid token and asks to edit a note that belongs to Bob. Which status does this contract return, and on what grounds?",
                        "opts": [
                            "401, because her token conveys no rights over that note and so does not authenticate her",
                            "403, because the service knows exactly who she is and is refusing this specific request",
                            "404, because a note outside her scope must not be revealed to exist under any circumstances",
                            "400, because asking for a resource the caller does not own is a malformed request body",
                        ],
                        "a": 1,
                        "whys": [
                            r"Her token authenticates her perfectly — the service read it, verified the signature and knows she is Ada. Answering 401 tells her to log in again, which she can do, successfully, and be refused identically.",
                            r"Authentication succeeded and authorisation failed, and those are the two halves 401 and 403 exist to separate.",
                            r"Hiding existence behind a 404 is a real pattern with a real argument behind it, and it also hides your own bugs: a genuinely missing note and a permissions error become indistinguishable in your logs. This contract chooses 403 for that reason.",
                            r"The request is perfectly well formed — correct path, correct method, valid body, valid token. A 400 says the caller wrote the request wrongly, and nothing here was written wrongly.",
                        ],
                        "why": r"""
401 means the service does not know who is asking; 403 means it does and the answer
is still no. Ada is authenticated, so the failure is entirely about permission, and
sending 401 would instruct a correctly logged-in user to log in again — which fixes
nothing and produces exactly the support ticket that has no cause. The two checks also
happen at different moments: authentication runs once at the front of the request from
the token alone, while ownership cannot be judged until the note has been fetched,
because the answer depends on the resource as much as on the user.
""",
                    },
                    {
                        "q": "An unexpected `KeyError(\"users.password_hash\")` escapes the service layer. Why must `to_response` refuse to put `str(exc)` into the body?",
                        "opts": [
                            "Because an exception message is not valid JSON, so the response body would fail to serialise",
                            "Because the message names internal structure, and error bodies then map the service for free",
                            "Because a 500 response is required by the HTTP specification to carry no body whatsoever",
                            "Because the wording shifts between Python versions and would break the conformance suite",
                        ],
                        "a": 1,
                        "whys": [
                            r"It serialises perfectly well — it is an ordinary string. The reason to keep it out has nothing to do with whether it can be encoded.",
                            r"Column names, file paths and library versions arrive in the caller's hands assembled from ordinary malformed requests.",
                            r"A 500 may carry a body, and this one does — a fixed code and a fixed message. The requirement is that the body says nothing the caller has no business knowing, not that it says nothing.",
                            r"Version-dependent wording is a genuine nuisance for anyone asserting on messages, but it is a testing inconvenience rather than the reason. The message must not leave the process however stable its wording is.",
                        ],
                        "why": r"""
The distinction `to_response` draws is between failures somebody wrote down on purpose
and failures nobody anticipated. A `ServiceError` carries a status, a code and a message
composed for a caller. Anything else is a bug, and its message was composed for a
developer reading a stack trace: it names columns, paths and internal identifiers.
Forwarding it turns every malformed request into a free probe of the implementation,
so the unexpected branch returns one fixed body and the real message goes to the log
under a correlation id the caller can quote at support.
""",
                    },
                    {
                        "q": "`authenticate` returns one identical message for an unknown username and for a wrong password. Which enumeration channel does that leave open?",
                        "opts": [
                            "Telling the two cases apart from the error code, which still differs between them",
                            "Learning that a username exists by trying to register it and reading the 409 conflict",
                            "Reading which field was at fault, since the uniform message still names the failing one",
                            "Seeing the account role in the failure body, which carries the record that was looked up",
                        ],
                        "a": 1,
                        "whys": [
                            r"Both failures raise the same class, so both carry status 401 and the code `unauthenticated`. The code is as uniform as the message, deliberately.",
                            r"Registration has to refuse a taken name somehow, and refusing it is the same fact through a different door.",
                            r"It names neither. The message is a single string covering both cases, which is the entire point of making it uniform — a message that named the failing field would not be uniform.",
                            r"The public dict is built only on success, and the failure path raises before any record is exposed. No role, hash or stored field reaches the caller on a failed login.",
                        ],
                        "why": r"""
A uniform login message closes one channel, not all of them. `register` still answers
409 for a name in use, which tells an attacker exactly what the login form was made to
hide, and the fix there is a decision about the sign-up flow rather than a string.
Timing is a second channel: if a missing user returns at once while a real one runs a
full PBKDF2 derivation first, the clock says what the message would not, and closing
that means deriving against a dummy record for users who do not exist. Knowing which
doors are still open is what stops a uniform message from being mistaken for a
solved problem.
""",
                    },
                ],
            },
            "lab": {
                "title": "Credentials, authorisation and error mapping",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
### The error hierarchy

`ServiceError(Exception)` carries class attributes `status = 500` and
`code = "internal"`. Five subclasses override them:

```text
ValidationError       400  invalid_request
AuthenticationError   401  unauthenticated
AuthorisationError    403  forbidden
NotFoundError         404  not_found
ConflictError         409  conflict
```

**`to_response(exc)`** -> `(status, {"error": {"code": ..., "message": ...}})`.
For a `ServiceError` use its status, code and `str(exc)`. For *anything else*
return `(500, {"error": {"code": "internal", "message": "internal server error"}})`
— the original message is a stack-trace fragment and belongs in a log, not a
response body.

### Credentials

**`hash_password(password, salt=None, iterations=DEFAULT_ITERATIONS)`** returns
`"pbkdf2_sha256$<iterations>$<salt hex>$<digest hex>"`, using
`_pbkdf2(...)` and `secrets.token_bytes(16)` when no salt
is supplied. Raise `ValidationError` for a password under 8 characters or one
with no digit in it.

**`verify_password(password, stored)`** -> `bool`. Re-derive with the stored
salt and iteration count, compare with `hmac.compare_digest`, and return `False`
— never raise — for a malformed `stored` string.

`DEFAULT_ITERATIONS` is 50 000 here so the lab runs in a browser tab. Production
wants several hundred thousand, and the number lives in the stored string
precisely so it can be raised later without invalidating old hashes.

### Users and permissions

**`UserStore`** holds users in a dict:

- `register(username, password, role="user")` -> `{"username", "role"}`.
  `ValidationError` for a username outside `^[a-z0-9_]{3,32}$`, an unknown role,
  or a password the hash rejects; `ConflictError` when the name is taken.
- `authenticate(username, password)` -> the same public dict.
  `AuthenticationError` with the *identical* message whether the user is unknown
  or the password is wrong.
- `get(username)` -> the public dict; `NotFoundError` otherwise.
- No method may ever return the stored hash.

**`require_role(user, *roles)`** raises `AuthorisationError` unless the user's
role is among `roles`. **`may_edit(user, resource)`** -> `True` when the user
owns `resource["owner"]` or is an admin. **`authorise_edit(user, resource)`**
raises `AuthorisationError` when `may_edit` is False.
''',
                "files": [{"name": "main.py", "content": r'''
import hashlib
import hmac
import re
import secrets

DEFAULT_ITERATIONS = 1000
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,32}$")
ROLES = ("user", "admin")


class ServiceError(Exception):
    """Base for every failure the service can explain to a caller."""
    status = 500
    code = "internal"


# define ValidationError, AuthenticationError, AuthorisationError,
# NotFoundError and ConflictError here


def to_response(exc):
    """(status, body) for any exception; unknown ones become a generic 500."""
    # your code here


def hash_password(password, salt=None, iterations=DEFAULT_ITERATIONS):
    """pbkdf2_sha256$iterations$salt$digest. ValidationError on a weak password."""
    # your code here


def verify_password(password, stored):
    """True when the password reproduces the stored digest. Never raises."""
    # your code here


class UserStore:
    """Registration and authentication over an in-memory dict."""

    def __init__(self):
        self.users = {}

    def register(self, username, password, role="user"):
        """Create a user and return the public view of it."""
        # your code here

    def authenticate(self, username, password):
        """The public user, or AuthenticationError with a uniform message."""
        # your code here

    def get(self, username):
        """The public user, or NotFoundError."""
        # your code here


def require_role(user, *roles):
    """AuthorisationError unless the user holds one of these roles."""
    # your code here


def may_edit(user, resource):
    """True when the user owns the resource or is an admin."""
    # your code here


def authorise_edit(user, resource):
    """AuthorisationError when may_edit is False."""
    # your code here


store = UserStore()
print(store.register("ada", "difference8"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import hashlib
import hmac
import re
import secrets

DEFAULT_ITERATIONS = 1000
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,32}$")
ROLES = ("user", "admin")


class ServiceError(Exception):
    """Base for every failure the service can explain to a caller."""
    status = 500
    code = "internal"


class ValidationError(ServiceError):
    status = 400
    code = "invalid_request"


class AuthenticationError(ServiceError):
    status = 401
    code = "unauthenticated"


class AuthorisationError(ServiceError):
    status = 403
    code = "forbidden"


class NotFoundError(ServiceError):
    status = 404
    code = "not_found"


class ConflictError(ServiceError):
    status = 409
    code = "conflict"


def to_response(exc):
    """(status, body) for any exception; unknown ones become a generic 500."""
    if isinstance(exc, ServiceError):
        return exc.status, {"error": {"code": exc.code, "message": str(exc)}}
    return 500, {"error": {"code": "internal", "message": "internal server error"}}


def _pbkdf2(password, salt, iterations, dklen=32):
    """PBKDF2-HMAC-SHA256, written out longhand.

    The browser runtime has no hashlib.pbkdf2_hmac, and writing the loop makes
    the cost of key stretching visible: each round is one more HMAC an attacker
    must pay for. Server-side Python should call hashlib.pbkdf2_hmac instead.
    """
    out = b""
    block = 1
    while len(out) < dklen:
        u = hmac.new(password, salt + block.to_bytes(4, "big"), hashlib.sha256).digest()
        current = u
        for _ in range(iterations - 1):
            u = hmac.new(password, u, hashlib.sha256).digest()
            current = bytes(a ^ b for a, b in zip(current, u))
        out += current
        block += 1
    return out[:dklen]


def hash_password(password, salt=None, iterations=DEFAULT_ITERATIONS):
    """pbkdf2_sha256$iterations$salt$digest. ValidationError on a weak password."""
    if not isinstance(password, str) or len(password) < 8:
        raise ValidationError("password must be at least 8 characters")
    if not any(character.isdigit() for character in password):
        raise ValidationError("password must contain a digit")
    if salt is None:
        salt = secrets.token_bytes(16)
    digest = _pbkdf2(password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${0}${1}${2}".format(iterations, salt.hex(), digest.hex())


def verify_password(password, stored):
    """True when the password reproduces the stored digest. Never raises."""
    try:
        scheme, iterations, salt_hex, digest_hex = stored.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        rounds = int(iterations)
    except (AttributeError, TypeError, ValueError):
        return False
    actual = _pbkdf2(str(password).encode("utf-8"), salt, rounds)
    return hmac.compare_digest(actual, expected)


class UserStore:
    """Registration and authentication over an in-memory dict."""

    def __init__(self):
        self.users = {}

    @staticmethod
    def _public(record):
        return {"username": record["username"], "role": record["role"]}

    def register(self, username, password, role="user"):
        """Create a user and return the public view of it."""
        if not isinstance(username, str) or not USERNAME_RE.match(username):
            raise ValidationError("username must be 3-32 of a-z, 0-9 or underscore")
        if role not in ROLES:
            raise ValidationError(f"role must be one of {list(ROLES)}")
        if username in self.users:
            raise ConflictError("that username is taken")
        record = {"username": username, "role": role,
                  "password": hash_password(password)}
        self.users[username] = record
        return self._public(record)

    def authenticate(self, username, password):
        """The public user, or AuthenticationError with a uniform message."""
        record = self.users.get(username)
        if record is None or not verify_password(password, record["password"]):
            raise AuthenticationError("username or password is wrong")
        return self._public(record)

    def get(self, username):
        """The public user, or NotFoundError."""
        record = self.users.get(username)
        if record is None:
            raise NotFoundError("no such user")
        return self._public(record)


def require_role(user, *roles):
    """AuthorisationError unless the user holds one of these roles."""
    if user.get("role") not in roles:
        raise AuthorisationError(f"this action needs one of {list(roles)}")


def may_edit(user, resource):
    """True when the user owns the resource or is an admin."""
    return user.get("role") == "admin" or resource.get("owner") == user.get("username")


def authorise_edit(user, resource):
    """AuthorisationError when may_edit is False."""
    if not may_edit(user, resource):
        raise AuthorisationError("that resource belongs to somebody else")


store = UserStore()
print(store.register("ada", "difference8"))
'''}],
                "hints": [
                    "Give each subclass only two class attributes — `status` and `code`. No `__init__` is needed; `Exception` already stores the message.",
                    "`to_response` is one `isinstance(exc, ServiceError)` check; everything else must fall through to the same generic 500 body, whatever it says.",
                    "Store the iteration count inside the hash string so a future increase can re-hash lazily on the next successful login.",
                    "`authenticate` must run the same code path for an unknown user as for a wrong password — one `if record is None or not verify_password(...)`, one message.",
                ],
                "tests": [
                    {"name": "the hierarchy carries its own status codes", "code": r'''
for _cls, _status, _code in [(ValidationError, 400, "invalid_request"),
                             (AuthenticationError, 401, "unauthenticated"),
                             (AuthorisationError, 403, "forbidden"),
                             (NotFoundError, 404, "not_found"),
                             (ConflictError, 409, "conflict")]:
    assert issubclass(_cls, ServiceError), f"{_cls.__name__} must subclass ServiceError"
    assert _cls.status == _status, f"{_cls.__name__}.status is {_cls.status!r}, expected {_status}"
    assert _cls.code == _code, f"{_cls.__name__}.code is {_cls.code!r}, expected {_code!r}"
assert ServiceError.status == 500 and ServiceError.code == "internal", "the base stays a 500"
'''},
                    {"name": "errors map onto responses without leaking", "code": r'''
_got = to_response(NotFoundError("no such note"))
assert _got == (404, {"error": {"code": "not_found", "message": "no such note"}}), f"got {_got!r}"
_got = to_response(ConflictError("that username is taken"))
assert _got[0] == 409 and _got[1]["error"]["code"] == "conflict", f"got {_got!r}"
_leak = to_response(KeyError("secret_column_name"))
assert _leak == (500, {"error": {"code": "internal", "message": "internal server error"}}), \
    f"an unexpected exception must become a generic 500, got {_leak!r}"
assert "secret_column_name" not in repr(_leak), "the internal message must not reach the caller"
_leak2 = to_response(ZeroDivisionError("division by zero"))
assert _leak2 == _leak, "every unexpected exception gets the same body"
'''},
                    {"name": "hashes are salted, iterated and self-describing", "code": r'''
_a = hash_password("difference8")
_b = hash_password("difference8")
assert _a != _b, "two hashes of the same password must differ — the salt is random"
_parts = _a.split("$")
assert len(_parts) == 4 and _parts[0] == "pbkdf2_sha256", f"unexpected hash format {_a!r}"
assert int(_parts[1]) == DEFAULT_ITERATIONS, f"the iteration count belongs in the string, got {_parts[1]!r}"
assert len(_parts[2]) == 32, f"a 16-byte salt is 32 hex characters, got {len(_parts[2])}"
assert len(_parts[3]) == 64, f"a sha256 digest is 64 hex characters, got {len(_parts[3])}"
assert "difference8" not in _a, "the password itself must not appear anywhere in the hash"
_fixed = hash_password("difference8", b"0123456789abcdef", 1000)
assert _fixed == hash_password("difference8", b"0123456789abcdef", 1000), "same salt and rounds, same digest"
'''},
                    {"name": "verification is total and constant-time", "code": r'''
_stored = hash_password("difference8")
assert verify_password("difference8", _stored) is True, "the right password must verify"
assert verify_password("difference9", _stored) is False, "a wrong password must not"
assert verify_password("", _stored) is False, "and nor must an empty one"
for _junk in ["", "nonsense", "pbkdf2_sha256$notanumber$aa$bb", "md5$1$aa$bb", None, 17]:
    assert verify_password("difference8", _junk) is False, f"a malformed stored value must return False, not raise: {_junk!r}"
_src = open("main.py").read()
assert "compare_digest" in _src, "compare the digests with hmac.compare_digest, not =="
for _weak in ["short1", "nodigitshere", "1234567"]:
    try:
        hash_password(_weak)
        assert False, f"hash_password({_weak!r}) should raise ValidationError"
    except ValidationError:
        pass
'''},
                    {"name": "registration validates and refuses duplicates", "code": r'''
_store = UserStore()
_user = _store.register("ada", "difference8")
assert _user == {"username": "ada", "role": "user"}, f"register returned {_user!r}"
assert "password" not in _user, "the public view must never carry the hash"
_admin = _store.register("root", "rootword1", "admin")
assert _admin["role"] == "admin", f"got {_admin!r}"
try:
    _store.register("ada", "difference8")
    assert False, "a duplicate username must raise ConflictError"
except ConflictError:
    pass
for _bad in [("ad", "difference8"), ("Ada", "difference8"), ("ada!", "difference8"),
             ("a" * 33, "difference8")]:
    try:
        _store.register(*_bad)
        assert False, f"register{_bad!r} should raise ValidationError"
    except ValidationError:
        pass
try:
    _store.register("bob", "difference8", "wizard")
    assert False, "an unknown role must raise ValidationError"
except ValidationError:
    pass
assert set(_store.users) == {"ada", "root"}, f"no refused registration may land; store holds {sorted(_store.users)!r}"
'''},
                    {"name": "authentication does not enumerate accounts", "code": r'''
_store = UserStore()
_store.register("ada", "difference8")
assert _store.authenticate("ada", "difference8") == {"username": "ada", "role": "user"}, "a good login returns the public user"
_messages = []
for _attempt in [("ada", "difference9"), ("nobody", "difference9"), ("nobody", "difference8")]:
    try:
        _store.authenticate(*_attempt)
        assert False, f"authenticate{_attempt!r} should raise AuthenticationError"
    except AuthenticationError as _exc:
        _messages.append(str(_exc))
assert len(set(_messages)) == 1, f"every failure must read the same, got {set(_messages)!r}"
assert to_response(AuthenticationError(_messages[0]))[0] == 401, "and map to 401"
assert _store.get("ada")["role"] == "user", "get returns the public user"
try:
    _store.get("nobody")
    assert False, "get on an unknown user should raise NotFoundError"
except NotFoundError:
    pass
'''},
                    {"name": "authorisation separates ownership from role", "code": r'''
_owner = {"username": "ada", "role": "user"}
_other = {"username": "bob", "role": "user"}
_admin = {"username": "root", "role": "admin"}
_note = {"id": 1, "owner": "ada"}
assert may_edit(_owner, _note) is True, "the owner may edit"
assert may_edit(_other, _note) is False, "a stranger may not"
assert may_edit(_admin, _note) is True, "an admin may"
authorise_edit(_owner, _note)
authorise_edit(_admin, _note)
try:
    authorise_edit(_other, _note)
    assert False, "authorise_edit should raise AuthorisationError for a stranger"
except AuthorisationError as _exc:
    assert to_response(_exc)[0] == 403, "which maps to 403, not 401"
require_role(_admin, "admin")
require_role(_owner, "user", "admin")
try:
    require_role(_owner, "admin")
    assert False, "require_role should raise AuthorisationError"
except AuthorisationError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Operability",
            "summary": "Logs somebody can query, a health check, counters, and a budget with teeth.",
            "concepts": [
                "Structured logs are records, not prose: one JSON object per line, stable field names",
                "A correlation id threads one request through every line it causes",
                "Bound context (a child logger) beats passing the id down every call signature",
                "Level filtering is a policy decision made once, at the logger",
                "Counters and timers answer different questions; keep count, total, min and max",
                "A health check reports on dependencies and never raises — a broken check is a result",
                "A performance budget only means something when a test fails on breaching it",
            ],
            "read": [
                {
                    "title": "Three in the morning, forty thousand lines, and one field that connects them",
                    "minutes": 15,
                    "body": r'''
It is 03:00 and the page says the error rate is up. A customer has written in: "saving a
note failed, around ten to three". You open the log.

```text
2026-08-14 02:48:11 saving note
2026-08-14 02:48:11 ok
2026-08-14 02:48:12 saving note
2026-08-14 02:48:12 error saving note
2026-08-14 02:48:12 ok
```

Forty thousand lines of this. Which `saving note` belongs to which `ok`? Whose note?
Which of the three concurrent workers wrote which line? The second `ok` at 02:48:12 —
does it belong to the request that failed a moment before, or to a different one that
happened to finish in the same second? There is no answer in the file. The information was never
written down, because each line was composed for a person who already knew the context,
and at 03:00 nobody does.

A log line is not a sentence for a human to read. It is a record, and it should be
queryable. Write one JSON object per line, with stable field names, and the question
above becomes a filter:

```python
import json

sink = []
ticks = iter([1700000000 + n for n in range(10)])


def log(level, event, **fields):
    record = {"ts": next(ticks), "level": level, "event": event}
    record.update(fields)
    sink.append(json.dumps(record, sort_keys=True))
    return record


log("info", "request.start", correlation_id="req-1", user="ada", path="/notes")
log("info", "db.query", correlation_id="req-1", table="notes", rows=3)
log("info", "request.start", correlation_id="req-2", user="bob", path="/notes")
log("error", "request.failed", correlation_id="req-1", error="IntegrityError")
log("info", "request.done", correlation_id="req-2", status=200)

records = [json.loads(line) for line in sink]
failed = [r["correlation_id"] for r in records if r["level"] == "error"]
print("requests that failed:", failed)
for record in records:
    if record["correlation_id"] in failed:
        print("   {0} {1:<15} {2}".format(
            record["ts"], record["event"], record.get("table", "")))
```

It prints `requests that failed: ['req-1']` and then the three lines that request caused,
in order, interleaving with `req-2` in the file and separating cleanly in the query. Two
lines of comprehension replaced an hour of reading. Nothing clever happened: the field
`correlation_id` was written on every line, so the lines could be gathered by it.

That is the whole design. One identifier minted per request, stamped on everything that
request causes, all the way down to the database call. It is also what you hand the
customer in the error body — the capstone's failure envelope carries
`correlation_id` for precisely this reason, so a support ticket arrives with the search
term already in it.

## Bound context, and the bug that shares it

Threading the id through every function signature works and rots: six calls deep,
somebody adds a helper and does not pass it, and that branch goes dark. The alternative
is a child logger that carries the id in its own context, so the call sites below it stay
ignorant. The implementation has one trap in it, and it is the kind that passes tests
written on a single request.

```python
class LeakyLogger:
    """bind() mutates the logger it was called on."""

    def __init__(self, sink, context=None):
        self.sink = sink
        self.context = dict(context or {})

    def bind(self, **fields):
        self.context.update(fields)
        return self

    def log(self, event, **fields):
        record = {"event": event}
        record.update(self.context)
        record.update(fields)
        self.sink.append(record)


class Logger:
    """bind() returns a child over the same sink."""

    def __init__(self, sink, context=None):
        self.sink = sink
        self.context = dict(context or {})

    def bind(self, **fields):
        merged = dict(self.context)
        merged.update(fields)
        return Logger(self.sink, merged)

    def log(self, event, **fields):
        record = {"event": event}
        record.update(self.context)
        record.update(fields)
        self.sink.append(record)


for cls in (LeakyLogger, Logger):
    lines = []
    root = cls(lines)
    root.bind(correlation_id="req-1", user="ada").log("request")
    root.bind(correlation_id="req-2").log("request")
    print("{0:<13}{1}".format(
        cls.__name__, [(r["correlation_id"], r.get("user", "-")) for r in lines]))
```

`LeakyLogger` prints `[('req-1', 'ada'), ('req-2', 'ada')]`. Bob's request is logged as
Ada's, because the first `bind` wrote `user` into the shared root and nothing ever took
it out. `Logger` prints `[('req-1', 'ada'), ('req-2', '-')]`: the child is a new object
over the same sink list, so context accumulates downward and never sideways.

An incident investigated from the first log ends with the wrong person's account being
examined. This is worse than a missing field, because the field is present and wrong,
and nothing in the file says so.

The other half of the field discipline is what you must *not* bind. A request body
travelling into a log record takes the password with it, and the capstone's constraints
say no plaintext password is stored, logged or returned. Log the fields you named on
purpose; never log the body wholesale.

## Levels are one decision, made once

`min_level` on the logger means a debug line costs a dictionary comparison and returns
`None`, and the call sites do not each grow an `if`. `log` returns the record it wrote,
or `None` when the level ranks below the threshold — which is what makes it testable
without reading the sink.

## Counters and timers answer different questions

A counter answers "how many": requests, errors, cache misses. A timer answers "how long",
and it is the one people summarise badly.

```python
latencies = [0.020] * 100 + [4.000]
print("count: {0}".format(len(latencies)))
print("mean:  {0:.3f} s".format(sum(latencies) / len(latencies)))
print("min:   {0:.3f} s".format(min(latencies)))
print("max:   {0:.3f} s".format(max(latencies)))
```

`mean: 0.059 s`. Fifty-nine milliseconds is a perfectly healthy-looking number, and it is
the average of a hundred fast requests and one that took four seconds. The mean does not
merely fail to show the four seconds; it actively conceals it, and a dashboard showing
only means goes green during exactly the incident you built it for. That is why the lab's
`observe` keeps `count`, `total`, `min` and `max`: the total and count give the mean back
whenever you want it, and `max` is the one that pages you. `snapshot` then adds `mean` as
a derived value and copies each timer dict, so a caller reading the registry cannot
scribble on it.

## A health check that raises has told you nothing

```python
def health(checks):
    results = {}
    for name, check in checks.items():
        try:
            results[name] = "ok" if check() else "failed"
        except Exception as exc:
            results[name] = "error: {0}".format(exc)
    status = "ok" if all(v == "ok" for v in results.values()) else "degraded"
    return {"status": status, "checks": results}


def refuse():
    raise RuntimeError("connection refused")


print(health({"database": lambda: True, "cache": lambda: True}))
print(health({"database": lambda: True, "cache": lambda: False}))
print(health({"database": refuse, "cache": lambda: True}))
```

The third call prints
`{'status': 'degraded', 'checks': {'database': 'error: connection refused', 'cache': 'ok'}}`.
A raising check is a failing check, and its exception message is the most useful sentence
in the report — it says *why*. Let it propagate instead and the health endpoint returns a
500 with no body, so the operator learns that health checking is broken and nothing about
the database. The endpoint whose job is to describe failure is the one endpoint that must
not fail, and a check raising is a result to record rather than an error to handle.

Note also that a single failed check degrades the whole service, and that `health({})`
reports `ok`: with nothing being checked, nothing is known to be broken. That is a
deliberate reading of an empty report and worth saying out loud, because it means a
health endpoint with no checks wired into it is indistinguishable from a healthy service.

## A budget nobody asserts is a wish

The capstone says 300 `GET /notes` requests against a populated database must finish
inside two seconds.

```python
import time


def benchmark(fn, n, budget):
    start = time.perf_counter()
    for _ in range(n):
        fn()
    elapsed = time.perf_counter() - start
    per_call = elapsed / n
    return {"n": n, "per_call": per_call, "within_budget": per_call < budget}


print("300 requests in 2.0 s allows {0:.2f} ms each".format(2.0 / 300 * 1000))
print("200 trivial calls under a 10 ms budget:",
      benchmark(lambda: sum(range(10)), 200, 0.01)["within_budget"])
print("200 trivial calls under a 0 s budget: ",
      benchmark(lambda: sum(range(10)), 200, 0.0)["within_budget"])
```

`6.67 ms each` is the number to hold in your head while writing the repository, and it is
generous — until `GET /notes` runs one query per note to fetch its owner, at which point
a page of ten costs eleven round trips and the budget is the thing that notices.

The comparison is `<` rather than `<=` deliberately. A budget of zero must be
unmeetable, and on a coarse clock an elapsed time can round to exactly zero, which under
`<=` would report `0.0 < = 0.0` as a pass and hand you a benchmark that congratulates
itself for measuring nothing.

The mistake worth naming is treating the budget as documentation. A comment saying
"should be fast" is not a budget; a test that fails when `within_budget` is `False` is.
The difference is that the second one notices the N+1 query the week it is introduced
rather than the month the traffic arrives.

## Where this stops holding

The metrics registry is a dictionary in one process. Deploy four workers behind a load
balancer and `GET /metrics` answers from whichever one the balancer picked, reporting
about a quarter of the traffic — and a different quarter each poll. Real deployments
push metrics to a collector, or expose them per instance and aggregate outside. The
in-process registry is right for a single process and silently misleading beyond it.

Percentiles have the same shape of problem and it is worse: means can at least be
combined if you keep the counts, but a median cannot be averaged with another median.
Aggregating across instances needs histogram buckets, not summaries.

Wall-clock benchmarking is noisy. `perf_counter` measures the machine, including whatever
else it is doing, so a budget tight enough to be interesting is also tight enough to fail
on a busy build agent. A budget is a regression alarm — set it several times the observed
cost — and the way to hold an algorithm to its complexity is to count operations rather
than seconds.

The bounded log has a cost too. Keeping the last 200 records means an incident that
produces 5,000 lines in ten seconds leaves you with the last 200, which are the recovery
and not the cause. A ring buffer is a debugging aid inside one process; durable logging
is somewhere else, and knowing which one you have matters at 03:00.

And none of this is tracing. A correlation id links the lines of one request within one
service. Once a request crosses into a second service, you need the id to travel with it
over the wire and to carry parent-child structure, which is where the id becomes a trace
context and the log becomes a span.

## What you are about to build

The lab, **Structured logging, metrics, health and a budget**, is these four pieces:
`Metrics` with `incr`, `observe`, a `snapshot` that copies, and `reset`; `Logger` over an
injected sink and clock, with level filtering and a `bind` that returns a child; `read`
to parse the sink back; `new_correlation_id` from a seeded `random.Random` so the tests
are reproducible; `health` that reports and never raises; `benchmark` with its strict
comparison; and `instrument`, which counts, times and logs one call and re-raises what it
caught — timing the failure too, because a slow failure is the case you most want
measured. Those are the same components the capstone's `METRICS`, `LOG` and `req-N`
correlation ids are graded on.
''',
                },
            ],
            "quiz": {
                "title": "Records, context, tails and budgets with teeth",
                "minutes": 8,
                "questions": [
                    {
                        "q": "A customer reports a failed save at about 02:50. The log holds one JSON object per line, each carrying a `correlation_id`. What does that buy over a line of prose per event?",
                        "opts": [
                            "A smaller file, since a serialised object is more compact than the same text in prose",
                            "Every line one request caused can be gathered by a filter, with nothing left to guess",
                            "Lines that sort into time order, since a serialised record always carries its own clock",
                            "Freedom from writing a level on each call, since the record shape already implies one",
                        ],
                        "a": 1,
                        "whys": [
                            r"JSON is larger than the prose it replaces — field names are repeated on every line. The trade is deliberate: more bytes in exchange for lines that can be queried.",
                            r"The id is on every line the request caused, so gathering them is a comparison rather than a reconstruction.",
                            r"A timestamp field has to be written like any other, and prose lines carry one too. Sorting was never the missing piece; connecting concurrent requests was.",
                            r"The level is an ordinary field that still has to be supplied, and it is what makes the first filter possible at all. Nothing about the record shape says whether an event was routine or a failure.",
                        ],
                        "why": r"""
The failure at 03:00 is not that the log is hard to read but that the connections
between lines were never written down. With three requests in flight, `saving note`
and `ok` a second apart belong to each other or they do not, and the file has no
opinion. A field stamped on every line one request causes makes that a filter: select
the records at error level, take their ids, select everything carrying those ids. The
same id goes into the error body the caller receives, so the support ticket arrives
with the search term already in it.
""",
                    },
                    {
                        "q": "`bind` is written to update `self.context` in place and return `self`. The tests, which log a single request, all pass. What actually breaks?",
                        "opts": [
                            "Two children end up writing into different sinks, so half the records are lost entirely",
                            "Fields bound in one request stay bound, so later lines carry the previous request's user",
                            "The parent loses its own base fields, because the update replaces rather than merges them",
                            "Each record is written twice, once by the parent logger and once by the child sharing it",
                        ],
                        "a": 1,
                        "whys": [
                            r"The sink is the one thing that is shared on purpose — a child logs into the same list. Sharing the sink is correct; sharing the context dictionary is the defect.",
                            r"Nothing removes a bound field, so the root accumulates every request's context and stamps it on the next one.",
                            r"`dict.update` merges, so the base fields survive. The problem is not what is lost from the parent but what is added to it and never taken away.",
                            r"One `log` call appends one record. Returning `self` means the parent and the child are the same object, which produces wrong fields rather than duplicate lines.",
                        ],
                        "why": r"""
A test that handles one request cannot see this, because there is no second request for
the context to leak into. Handle two and the failure appears: the first binds a user and
a correlation id onto the shared root, the second binds only its own id, and the root
still carries the first user — so the second request is logged under the wrong account.
That is worse than a missing field, because an investigator has no way to know the field
is wrong. Returning a new `Logger` over the same sink keeps the sharing where it belongs:
context accumulates from parent to child and never travels sideways between requests.
""",
                    },
                    {
                        "q": "A timer records 100 observations of 20 ms and one of 4 s. Why keep `count`, `total`, `min` and `max` rather than only a running mean?",
                        "opts": [
                            "Because a mean cannot be maintained incrementally, so the count and total must be kept",
                            "Because the mean of those is 59 ms, while the request that mattered took four seconds",
                            "Because min and max are needed to normalise each observation before the mean is taken",
                            "Because a mean over floats accumulates rounding error that min and max are immune to",
                        ],
                        "a": 1,
                        "whys": [
                            r"A mean is maintainable incrementally, and keeping the total and count is one ordinary way to do it. That is a description of the storage rather than a reason for the extra fields.",
                            r"Fifty-nine milliseconds looks healthy and is the average of a hundred fast requests and one four-second one.",
                            r"Nothing is normalised here — every observation is a duration in seconds and goes into the total as it is. Min and max are reported for their own sake, not as inputs to another figure.",
                            r"Rounding error over a hundred floats is far below anything a latency dashboard would notice. The number being hidden is four seconds, not a fraction of a microsecond.",
                        ],
                        "why": r"""
The mean does not merely fail to show the outlier, it conceals it: one four-second
request among a hundred fast ones moves the average from 20 ms to 59 ms, which reads as
healthy. A dashboard of means therefore stays green through the incident it was built to
catch. Keeping the total and count preserves the mean for whenever it is genuinely
wanted, while `max` is the field that reflects the experience of the worst-served caller
and the one worth alerting on.
""",
                    },
                    {
                        "q": "Why must `health` catch a check that raises and record `error: <message>` instead of letting the exception propagate?",
                        "opts": [
                            "Because a check that raised has not truly failed, and calling it failed would misreport it",
                            "Because an endpoint that cannot answer leaves the operator holding no report whatsoever",
                            "Because the failure would be counted twice, once as a failed check and once as a 500",
                            "Because a raising check gets retried by the poller, doubling the load on an ill service",
                        ],
                        "a": 1,
                        "whys": [
                            r"A check that raises has failed in the most complete way available to it — it could not even reach a verdict. Recording it as anything other than a failure would be the misreport.",
                            r"A 500 with no body says health checking is broken and says nothing at all about the database.",
                            r"Double counting is a metrics concern and this endpoint is not incrementing anything. Even if it were, the fix would be to count once rather than to reshape the health report.",
                            r"Retries are a poller policy and are unaffected by how the endpoint handles an exception internally. The endpoint would be retried for a 500 exactly as it is for a degraded 200.",
                        ],
                        "why": r"""
The endpoint whose entire job is to describe failure is the one endpoint that must not
fail. Let a check propagate and the response is a 500 with no body, which tells an
operator only that health checking is broken — the state of every dependency, including
the ones that were fine, is lost with it. Catching turns the exception into the single
most useful sentence in the report, because it says why: `error: connection refused`
names the problem where `failed` would only have named the check. A raising check is a
result to record, not an error to handle.
""",
                    },
                    {
                        "q": "`benchmark` reports `within_budget` as `per_call < budget`, strictly, rather than `per_call <= budget`. What does the strict comparison buy?",
                        "opts": [
                            "A safety margin, so a run that barely fits the budget is reported as a breach anyway",
                            "A budget of zero that can never be met, however coarse the clock the timing came from",
                            "Independence from the clock's resolution, since exact equality is then never reported",
                            "Agreement with the rubric, which resolves a tie against the implementation being graded",
                        ],
                        "a": 1,
                        "whys": [
                            r"There is no margin in it — the difference between the two forms is one exact value, and every run above the budget already fails under either. A margin is something you choose when you pick the budget number.",
                            r"On a coarse clock an elapsed time can round to exactly zero, and `<=` would pass a zero budget on that.",
                            r"The comparison depends on the clock either way; it merely refuses to reward the one reading a coarse clock produces most misleadingly. Nothing here makes the result resolution-independent.",
                            r"The rubric grades whether the budget is asserted at all, and has no tie-breaking rule. The reason for the strict form lives in the arithmetic rather than in how the work is marked.",
                        ],
                        "why": r"""
A timer with millisecond granularity can report an elapsed time of exactly 0.0 for work
too fast to measure, and under `<=` a budget of zero would then pass — a benchmark
congratulating itself for measuring nothing. Requiring strictly less makes a zero budget
unmeetable by construction, which is what the lab's test asserts. It is a small guard
against a large class of self-satisfied test: the point of a budget is to fail, and one
that cannot fail is documentation with an assertion painted on it.
""",
                    },
                    {
                        "q": "The service is deployed as four worker processes behind a load balancer, each with its own `METRICS` dictionary. What does `GET /metrics` now report?",
                        "opts": [
                            "The summed totals, because every worker updates the same registry in the shared process",
                            "One worker's own counts, so a poll shows about a quarter of the traffic, a shifting quarter",
                            "A 503, because a registry held in one process cannot serve a route the balancer shares out",
                            "Doubled totals, because the balancer forwards each incoming request to every worker in turn",
                        ],
                        "a": 1,
                        "whys": [
                            r"Separate processes do not share a dictionary — each has its own address space, and `METRICS` in one is invisible to the other three. Sharing would need a collector or a store outside the process.",
                            r"The balancer routes the metrics request to one worker, and that worker knows only about the requests it served itself.",
                            r"Nothing fails: the route works perfectly and returns a valid, confidently wrong answer. A visible 503 would be far easier to notice than the number this actually returns.",
                            r"A load balancer sends each request to exactly one worker; that is what makes it a balancer. Broadcasting would multiply the work rather than the counts.",
                        ],
                        "why": r"""
The registry is a dictionary in one process, so it counts what that process handled and
nothing else. With four workers, a poll lands on one of them and reports about a quarter
of the traffic — a different quarter each time, so the graph jitters for reasons that
have nothing to do with the service. There is no error to alert on; the endpoint answers
confidently and wrongly. Real deployments either push to a collector or expose each
instance separately and aggregate outside, and percentiles are harder still, because two
medians cannot be averaged into one the way two counts can be added.
""",
                    },
                ],
            },
            "lab": {
                "title": "Structured logging, metrics, health and a budget",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
**`class Metrics`** — `counters` and `timers` dicts.

- `incr(name, n=1)` adds to a counter (creating it at 0 first)
- `observe(name, value)` records into a timer: `count`, `total`, `min`, `max`
- `snapshot()` -> `{"counters": {...}, "timers": {name: {"count", "total", "min", "max", "mean"}}}`, a copy the caller cannot use to mutate the registry
- `reset()` empties both

**`new_correlation_id(rng)`** -> `"{:016x}".format(rng.getrandbits(64))`, so a
seeded `random.Random` gives a reproducible id.

**`class Logger`** — `Logger(sink, clock, min_level="info", context=None)`.
`sink` is a list; `clock` a zero-argument callable returning a number.

- `LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40}`
- `log(level, event, **fields)` builds `{"ts": clock(), "level": level, "event": event}`
  updated with the bound context and then `fields`, appends
  `json.dumps(record, sort_keys=True)` to the sink and returns the record —
  or returns `None`, appending nothing, when the level ranks below `min_level`
- `bind(**fields)` -> a *new* Logger sharing the sink and clock with those fields
  merged into its context; the parent must be unchanged
- `debug/info/warning/error(event, **fields)` are thin wrappers

**`read(sink)`** -> `[json.loads(line) for line in sink]`.

**`health(checks)`** — `checks` maps a name to a zero-argument callable. Each is
run; a truthy return is `"ok"`, a falsey return is `"failed"`, and a raised
exception is `"error: <message>"`. Returns
`{"status": "ok" | "degraded", "checks": {...}}`, degraded when any check is not
`"ok"`. The health check itself never raises.

**`benchmark(fn, n, budget)`** -> `{"n", "elapsed", "per_call", "within_budget"}`
where `elapsed` is the wall-clock seconds for `n` calls, `per_call` is
`elapsed / n`, and `within_budget` is `per_call < budget` — strictly under, so a zero budget is never met however coarse the clock is.

**`instrument(logger, metrics, name, fn, *args, **kwargs)`** — call `fn`,
incrementing `name + ".calls"`, observing `name + ".seconds"`, and logging an
`info` record with `event=name` and `ok=True`. On an exception: increment
`name + ".errors"`, log an `error` record with `event=name`, `ok=False` and
`error` set to the exception's class name, then re-raise.
''',
                "files": [{"name": "main.py", "content": r'''
import json
import time


class Metrics:
    """Counters and timers for one process."""

    def __init__(self):
        self.counters = {}
        self.timers = {}

    def incr(self, name, n=1):
        """Add n to a counter."""
        # your code here

    def observe(self, name, value):
        """Record one observation into a timer."""
        # your code here

    def snapshot(self):
        """A copy of both registries, with a mean per timer."""
        # your code here

    def reset(self):
        """Forget everything."""
        # your code here


def new_correlation_id(rng):
    """A 16-hex-digit id drawn from a seeded random.Random."""
    # your code here


class Logger:
    """One JSON object per line, with bindable context."""

    LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40}

    def __init__(self, sink, clock, min_level="info", context=None):
        self.sink = sink
        self.clock = clock
        self.min_level = min_level
        self.context = dict(context or {})

    def bind(self, **fields):
        """A child logger sharing the sink, with extra context."""
        # your code here

    def log(self, level, event, **fields):
        """Append one record, or None when the level is filtered out."""
        # your code here

    def debug(self, event, **fields):
        return self.log("debug", event, **fields)

    def info(self, event, **fields):
        return self.log("info", event, **fields)

    def warning(self, event, **fields):
        return self.log("warning", event, **fields)

    def error(self, event, **fields):
        return self.log("error", event, **fields)


def read(sink):
    """Parse a sink of JSON lines back into dicts."""
    # your code here


def health(checks):
    """Run every check; report, never raise."""
    # your code here


def benchmark(fn, n, budget):
    """Time n calls and say whether the per-call cost comes in under budget."""
    # your code here


def instrument(logger, metrics, name, fn, *args, **kwargs):
    """Count, time and log one call; re-raise whatever it throws."""
    # your code here


ticks = iter(range(1000))
log = Logger([], lambda: next(ticks))
log.info("started", component="demo")
print("lines:", len(log.sink))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import json
import time


class Metrics:
    """Counters and timers for one process."""

    def __init__(self):
        self.counters = {}
        self.timers = {}

    def incr(self, name, n=1):
        """Add n to a counter."""
        self.counters[name] = self.counters.get(name, 0) + n

    def observe(self, name, value):
        """Record one observation into a timer."""
        timer = self.timers.get(name)
        if timer is None:
            self.timers[name] = {"count": 1, "total": float(value),
                                 "min": float(value), "max": float(value)}
            return
        timer["count"] += 1
        timer["total"] += float(value)
        timer["min"] = min(timer["min"], float(value))
        timer["max"] = max(timer["max"], float(value))

    def snapshot(self):
        """A copy of both registries, with a mean per timer."""
        timers = {}
        for name, timer in self.timers.items():
            timers[name] = dict(timer)
            timers[name]["mean"] = timer["total"] / timer["count"]
        return {"counters": dict(self.counters), "timers": timers}

    def reset(self):
        """Forget everything."""
        self.counters = {}
        self.timers = {}


def new_correlation_id(rng):
    """A 16-hex-digit id drawn from a seeded random.Random."""
    return "{0:016x}".format(rng.getrandbits(64))


class Logger:
    """One JSON object per line, with bindable context."""

    LEVELS = {"debug": 10, "info": 20, "warning": 30, "error": 40}

    def __init__(self, sink, clock, min_level="info", context=None):
        self.sink = sink
        self.clock = clock
        self.min_level = min_level
        self.context = dict(context or {})

    def bind(self, **fields):
        """A child logger sharing the sink, with extra context."""
        merged = dict(self.context)
        merged.update(fields)
        return Logger(self.sink, self.clock, self.min_level, merged)

    def log(self, level, event, **fields):
        """Append one record, or None when the level is filtered out."""
        if self.LEVELS[level] < self.LEVELS[self.min_level]:
            return None
        record = {"ts": self.clock(), "level": level, "event": event}
        record.update(self.context)
        record.update(fields)
        self.sink.append(json.dumps(record, sort_keys=True))
        return record

    def debug(self, event, **fields):
        return self.log("debug", event, **fields)

    def info(self, event, **fields):
        return self.log("info", event, **fields)

    def warning(self, event, **fields):
        return self.log("warning", event, **fields)

    def error(self, event, **fields):
        return self.log("error", event, **fields)


def read(sink):
    """Parse a sink of JSON lines back into dicts."""
    return [json.loads(line) for line in sink]


def health(checks):
    """Run every check; report, never raise."""
    results = {}
    for name, check in checks.items():
        try:
            results[name] = "ok" if check() else "failed"
        except Exception as exc:
            results[name] = "error: {0}".format(exc)
    status = "ok" if all(v == "ok" for v in results.values()) else "degraded"
    return {"status": status, "checks": results}


def benchmark(fn, n, budget):
    """Time n calls and say whether the per-call cost comes in under budget."""
    start = time.perf_counter()
    for _ in range(n):
        fn()
    elapsed = time.perf_counter() - start
    per_call = elapsed / n
    return {"n": n, "elapsed": elapsed, "per_call": per_call,
            "within_budget": per_call < budget}


def instrument(logger, metrics, name, fn, *args, **kwargs):
    """Count, time and log one call; re-raise whatever it throws."""
    metrics.incr(name + ".calls")
    start = time.perf_counter()
    try:
        result = fn(*args, **kwargs)
    except Exception as exc:
        metrics.observe(name + ".seconds", time.perf_counter() - start)
        metrics.incr(name + ".errors")
        logger.error(name, ok=False, error=type(exc).__name__)
        raise
    metrics.observe(name + ".seconds", time.perf_counter() - start)
    logger.info(name, ok=True)
    return result


ticks = iter(range(1000))
log = Logger([], lambda: next(ticks))
log.info("started", component="demo")
print("lines:", len(log.sink))
'''}],
                "hints": [
                    "`bind` must build a *new* Logger over the same sink list — mutating `self.context` would leak one request's id into the next.",
                    "Order matters in `log`: base fields, then bound context, then the call's own fields, so the most specific value wins.",
                    "`snapshot` has to copy each timer dict; returning the live dicts lets a caller corrupt your registry by accident.",
                    "In `instrument`, record the timing in both paths — a slow failure is exactly the case you most want measured.",
                ],
                "tests": [
                    {"name": "counters and timers accumulate", "code": r'''
_m = Metrics()
_m.incr("requests")
_m.incr("requests", 4)
assert _m.counters["requests"] == 5, f"counter is {_m.counters['requests']!r}, expected 5"
_m.observe("latency", 0.2)
_m.observe("latency", 0.6)
_m.observe("latency", 0.4)
_t = _m.timers["latency"]
assert _t["count"] == 3, f"count is {_t['count']!r}, expected 3"
assert abs(_t["total"] - 1.2) < 1e-9, f"total is {_t['total']!r}, expected 1.2"
assert abs(_t["min"] - 0.2) < 1e-9 and abs(_t["max"] - 0.6) < 1e-9, f"min/max are {_t['min']!r}/{_t['max']!r}"
'''},
                    {"name": "the snapshot is a mean-bearing copy", "code": r'''
_m = Metrics()
_m.incr("requests", 3)
_m.observe("latency", 0.2)
_m.observe("latency", 0.4)
_snap = _m.snapshot()
assert set(_snap) == {"counters", "timers"}, f"snapshot keys are {sorted(_snap)!r}"
assert _snap["counters"] == {"requests": 3}, f"got {_snap['counters']!r}"
assert abs(_snap["timers"]["latency"]["mean"] - 0.3) < 1e-9, f"mean is {_snap['timers']['latency']['mean']!r}, expected 0.3"
_snap["counters"]["requests"] = 999
_snap["timers"]["latency"]["count"] = 999
assert _m.counters["requests"] == 3, "mutating the snapshot must not touch the registry"
assert _m.timers["latency"]["count"] == 2, "the timer dicts must be copied too"
_m.reset()
assert _m.snapshot() == {"counters": {}, "timers": {}}, f"reset should empty both, got {_m.snapshot()!r}"
'''},
                    {"name": "logs are JSON records with a stable shape", "code": r'''
import json
_sink = []
_ticks = iter([10, 11, 12, 13])
_log = Logger(_sink, lambda: next(_ticks))
_rec = _log.info("request", method="GET", status=200)
assert len(_sink) == 1, f"one call, one line; sink holds {len(_sink)}"
assert isinstance(_sink[0], str), "the sink holds serialised lines, not dicts"
_parsed = read(_sink)[0]
assert _parsed == {"ts": 10, "level": "info", "event": "request", "method": "GET", "status": 200}, f"got {_parsed!r}"
assert _rec == _parsed, "log should return the same record it wrote"
_log.error("boom", detail="x")
assert read(_sink)[1]["level"] == "error" and read(_sink)[1]["ts"] == 11, f"got {read(_sink)[1]!r}"
'''},
                    {"name": "levels are filtered and context binds", "code": r'''
_sink = []
_ticks = iter(range(100))
_log = Logger(_sink, lambda: next(_ticks), min_level="warning")
assert _log.info("ignored") is None, "an info record under a warning threshold returns None"
assert _log.debug("ignored") is None, "and so does debug"
assert _sink == [], f"nothing should have been written, sink holds {_sink!r}"
assert _log.warning("kept") is not None, "warning meets the threshold"
assert len(_sink) == 1, f"one line expected, got {len(_sink)}"
_root = Logger([], lambda: 0)
_child = _root.bind(correlation_id="abc123")
assert _child is not _root and _child.sink is _root.sink, "bind returns a new Logger over the same sink"
assert _root.context == {}, f"the parent must be untouched, its context is {_root.context!r}"
_child.info("request")
assert read(_root.sink)[0]["correlation_id"] == "abc123", "bound context must appear on every child record"
_grand = _child.bind(user="ada")
_grand.info("request")
_last = read(_root.sink)[-1]
assert _last["correlation_id"] == "abc123" and _last["user"] == "ada", f"context should accumulate, got {_last!r}"
_child.info("request", correlation_id="override")
assert read(_root.sink)[-1]["correlation_id"] == "override", "an explicit field beats bound context"
'''},
                    {"name": "correlation ids are reproducible under a seed", "code": r'''
import random
_a = new_correlation_id(random.Random(7))
_b = new_correlation_id(random.Random(7))
assert _a == _b, f"the same seed must give the same id, got {_a!r} and {_b!r}"
assert len(_a) == 16, f"expected 16 hex digits, got {_a!r}"
assert all(_ch in "0123456789abcdef" for _ch in _a), f"expected lowercase hex, got {_a!r}"
_rng = random.Random(7)
assert new_correlation_id(_rng) != new_correlation_id(_rng), "successive draws from one generator must differ"
'''},
                    {"name": "health reports, and never raises", "code": r'''
def _boom():
    raise RuntimeError("connection refused")

_ok = health({"database": lambda: True, "cache": lambda: True})
assert _ok == {"status": "ok", "checks": {"database": "ok", "cache": "ok"}}, f"got {_ok!r}"
_mixed = health({"database": lambda: True, "cache": lambda: False})
assert _mixed["status"] == "degraded", f"one failure degrades the whole service, got {_mixed!r}"
assert _mixed["checks"]["cache"] == "failed", f"got {_mixed['checks']!r}"
_raised = health({"database": _boom})
assert _raised["status"] == "degraded", "a raising check is a failing check"
assert _raised["checks"]["database"].startswith("error: "), f"got {_raised['checks']['database']!r}"
assert "connection refused" in _raised["checks"]["database"], "the reason belongs in the health report"
assert health({}) == {"status": "ok", "checks": {}}, "no checks means nothing is broken"
'''},
                    {"name": "the budget and the instrumentation", "code": r'''
_fast = benchmark(lambda: sum(range(10)), 200, 0.01)
assert _fast["n"] == 200, f"got {_fast!r}"
assert abs(_fast["per_call"] - _fast["elapsed"] / 200) < 1e-12, "per_call is elapsed / n"
assert _fast["within_budget"] is True, f"summing ten integers must fit a 10 ms budget, got {_fast!r}"
_tight = benchmark(lambda: sum(range(10)), 200, 0.0)
assert _tight["within_budget"] is False, "a zero budget cannot be met"

import random
_m = Metrics()
_sink = []
_log = Logger(_sink, lambda: 0).bind(correlation_id=new_correlation_id(random.Random(3)))
assert instrument(_log, _m, "handler", lambda x: x * 2, 21) == 42, "instrument returns the callee's value"
assert _m.counters["handler.calls"] == 1, f"counters are {_m.counters!r}"
assert _m.timers["handler.seconds"]["count"] == 1, f"timers are {_m.timers!r}"
assert read(_sink)[-1]["ok"] is True and read(_sink)[-1]["event"] == "handler", f"got {read(_sink)[-1]!r}"

def _explode():
    raise KeyError("missing")

try:
    instrument(_log, _m, "handler", _explode)
    assert False, "instrument must re-raise whatever the callee threw"
except KeyError:
    pass
assert _m.counters["handler.errors"] == 1, f"the failure must be counted, counters are {_m.counters!r}"
assert _m.counters["handler.calls"] == 2, "and the call still counted"
assert _m.timers["handler.seconds"]["count"] == 2, "a failing call is timed too"
_last = read(_sink)[-1]
assert _last["level"] == "error" and _last["ok"] is False and _last["error"] == "KeyError", f"got {_last!r}"
assert _last["correlation_id"] == read(_sink)[0]["correlation_id"], "the correlation id must survive the failure path"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- CAP
    "capstone": {
        "title": "A complete backend service",
        "brief": r'''
Five files, one entry point. `api.handle_request(conn, method, path, body)`
returns `(status, payload)` and is the whole public surface.

### db.py

`MIGRATIONS` (given), `connect(path=":memory:")`, `schema_version(conn)` and
`migrate(conn, target=None)` exactly as in the persistence lab: `sqlite3.Row`
rows, `isolation_level = None`, foreign keys on, one transaction per migration,
a `schema_version` table of `(version, applied_at)`.

### repo.py

`UserRepo` — `create(username, password_hash, role)` -> id (let
`sqlite3.IntegrityError` escape on a duplicate), `by_username(username)` -> dict
or `None`. `NoteRepo` — `create(owner, title, body, pinned=False)` -> id,
`get(id)`, `list(owner=None, limit, offset)`, `count(owner=None)`,
`update(id, title=None, body=None, pinned=None)` -> bool, `delete(id)` -> bool,
`create_many(owner, rows)` all-or-nothing. A note dict is
`{"id", "owner", "title", "body", "pinned"}` with `pinned` a bool. Every value
travels as a `?` parameter. `list` orders by `id`.

### auth.py

`ITERATIONS = 1000` and a module `SECRET`. `hash_password(password, salt=None,
iterations=ITERATIONS)` -> `"pbkdf2_sha256$rounds$salt$digest"`, raising
`ValueError` under 8 characters. `verify_password(password, stored)` -> bool via
`hmac.compare_digest`, never raising. `make_token(username, role)` ->
`"<payload>.<signature>"` where the payload is unpadded URL-safe base64 of
`{"sub", "role"}` as compact sorted JSON and the signature is
`hmac.new(SECRET, payload, sha256).hexdigest()`. `read_token(token)` -> the
claims dict, or `None` for anything malformed, unsigned or tampered with.

### api.py

`handle_request(conn, method, path, body=None)`. `body` defaults to `{}`; a
non-dict body is a 400. The bearer token travels as `body["token"]`. Query
parameters come off the path (`/notes?limit=2&offset=4`).

```text
GET    /health           public   200 {"status", "schema_version", "checks"}
POST   /users            public   201 {"id", "username", "role"}
POST   /sessions         public   200 {"token", "role"}
GET    /metrics          admin    200 {"requests_total", "errors_total", "by_status"}
GET    /notes            token    200 {"items", "limit", "offset", "total"}
POST   /notes            token    201 the new note
GET    /notes/{id}       token    200 the note
PATCH  /notes/{id}       token    200 the updated note
DELETE /notes/{id}       token    204 with a payload of None
```

Rules:

- username `^[a-z0-9_]{3,32}$`, password 8-128 characters, title 1-80, body
  0-2000, `pinned` a boolean. Anything else is `400 invalid_request`.
- `role: "admin"` on `POST /users` requires an admin token, else `403`.
- A duplicate username is `409 conflict`.
- A missing, malformed or tampered token is `401 unauthenticated`; a valid token
  without the right to act is `403 forbidden`.
- A plain user sees and touches only their own notes; an admin sees all.
- `limit` defaults to 10 and must be 1-50; `offset` defaults to 0 and must not be
  negative. A non-integer either way is a 400.
- An unknown path is `404 not_found`; a known path with the wrong method is
  `405 method_not_allowed`.
- Every failure body is
  `{"error": {"code": ..., "message": ..., "correlation_id": ...}}`. An
  unexpected exception becomes `500 internal` with the message
  `"internal server error"`.

Observability: a module-level `METRICS` dict (`requests_total`, `errors_total`,
`by_status` keyed by the status as a string), a `LOG` list holding at most the
last 200 request records, a monotonic correlation id `req-1`, `req-2`, ... and
`reset_observability()` to zero all three. Count the request *before* dispatch,
so `GET /metrics` includes itself.

### main.py

Migrate a fresh in-memory database, register a user, log in, post a note, list
it, hit `/health`, and print each outcome.
''',
        "deliverables": [
            "`db.py` — connection factory, the migration list and an idempotent, transactional migration runner",
            "`repo.py` — `UserRepo` and `NoteRepo`, every query parameterised, `create_many` all-or-nothing",
            "`auth.py` — PBKDF2 password hashing, constant-time verification, and HMAC-signed tokens that reject tampering",
            "`api.py` — `handle_request` with routing, validation, authentication, authorisation, pagination and the error envelope",
            "`main.py` — a runnable demonstration of the happy path against an in-memory database",
            "Observability: correlation ids on every request, a bounded log, status counters and an admin-only metrics endpoint",
        ],
        "constraints": [
            "Standard library only; `db.py`, `repo.py`, `auth.py` and `api.py` print nothing when imported",
            "No SQL is ever built by string formatting or concatenation of a caller's value — placeholders throughout",
            "No plaintext password is stored, logged or returned, and no response body carries a password hash",
            "Errors leaving `handle_request` are the envelope only: no traceback, no SQL, no internal identifier",
            "300 `GET /notes` requests against a populated database must complete in under two seconds",
        ],
        "rubric": [
            {"criterion": "Contract conformance", "weight": 30,
             "evidence": "Every documented route returns the documented status and payload shape, pagination and all."},
            {"criterion": "Data layer integrity", "weight": 20,
             "evidence": "Migrations are idempotent and transactional; a hostile title round-trips verbatim; a failed batch leaves no rows."},
            {"criterion": "Security", "weight": 25,
             "evidence": "Salted iterated hashes, constant-time comparison, tamper-rejecting tokens, and 401 versus 403 used correctly."},
            {"criterion": "Observability", "weight": 15,
             "evidence": "Correlation ids on every error, status counters that add up, an admin-only metrics route and a bounded log."},
            {"criterion": "Structure and performance", "weight": 10,
             "evidence": "Four import-clean modules with one responsibility each, and 300 list requests inside the budget."},
        ],
        "runtime": "python",
        "minutes": 300,
        "hints": [
            "Build it bottom-up and keep each layer honest: `db.py` and `repo.py` first with their own checks, then `auth.py`, and only then wire `api.py` over the three.",
            "Route in two steps: find every method allowed on the matched path, and answer 405 before you answer 404 — otherwise a `PUT /notes` is reported as a missing endpoint.",
            "Do authentication once, right after the three public routes, and hand the claims down; scattering `read_token` through every branch is how a route ends up unprotected.",
            "401 means 'I do not know who you are', 403 means 'I do, and no'. Returning 404 for somebody else's note hides existence but also hides your bugs — this contract says 403.",
            "Wrap the whole of `handle_request` in try/except: catch `ApiError` for the documented failures and a bare `Exception` for everything else, and make the second branch return a message you would be content to see on a public status page.",
        ],
        "files": [
            {"name": "db.py", "content": r'''
import sqlite3
import time

MIGRATIONS = [
    (1, [
        "CREATE TABLE users ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " username TEXT NOT NULL UNIQUE,"
        " password TEXT NOT NULL,"
        " role TEXT NOT NULL)",
        "CREATE TABLE notes ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " owner TEXT NOT NULL,"
        " title TEXT NOT NULL,"
        " body TEXT NOT NULL,"
        " FOREIGN KEY (owner) REFERENCES users(username))",
    ]),
    (2, [
        "ALTER TABLE notes ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0",
        "CREATE INDEX idx_notes_owner ON notes(owner)",
    ]),
]


def connect(path=":memory:"):
    """Row rows, explicit transactions, foreign keys on."""
    # your code here


def schema_version(conn):
    """The highest applied migration, or 0."""
    # your code here


def migrate(conn, target=None):
    """Apply pending migrations; returns the resulting version."""
    # your code here
'''},
            {"name": "repo.py", "content": r'''
class UserRepo:
    def __init__(self, conn):
        self.conn = conn

    def create(self, username, password_hash, role):
        """Insert a user and return its id. A duplicate raises sqlite3.IntegrityError."""
        # your code here

    def by_username(self, username):
        """The full user row as a dict, or None."""
        # your code here


class NoteRepo:
    def __init__(self, conn):
        self.conn = conn

    def create(self, owner, title, body, pinned=False):
        """Insert a note and return its id."""
        # your code here

    def get(self, note_id):
        """{'id', 'owner', 'title', 'body', 'pinned'} or None."""
        # your code here

    def list(self, owner=None, limit=10, offset=0):
        """A page of notes ordered by id; owner=None means every owner."""
        # your code here

    def count(self, owner=None):
        """How many notes, in total or for one owner."""
        # your code here

    def update(self, note_id, title=None, body=None, pinned=None):
        """Patch the given fields; True when a row changed."""
        # your code here

    def delete(self, note_id):
        """True when a row went."""
        # your code here

    def create_many(self, owner, rows):
        """All-or-nothing insert of [(title, body), ...]."""
        # your code here
'''},
            {"name": "auth.py", "content": r'''
import base64
import hashlib
import hmac
import json
import secrets

ITERATIONS = 1000
SECRET = b"cap501-demonstration-signing-key"


def hash_password(password, salt=None, iterations=ITERATIONS):
    """pbkdf2_sha256$rounds$salt$digest. ValueError under 8 characters."""
    # your code here


def verify_password(password, stored):
    """Constant-time comparison; False for anything malformed."""
    # your code here


def make_token(username, role):
    """payload.signature, the payload unpadded URL-safe base64 of the claims."""
    # your code here


def read_token(token):
    """The claims, or None if the token is malformed or the signature is wrong."""
    # your code here
'''},
            {"name": "api.py", "content": r'''
import re
import sqlite3

import auth
from db import schema_version
from repo import NoteRepo, UserRepo

USERNAME_RE = re.compile(r"^[a-z0-9_]{3,32}$")
MAX_TITLE = 80
MAX_BODY = 2000
MAX_LIMIT = 50

ROUTES = [
    ("GET", re.compile(r"^/health$")),
    ("GET", re.compile(r"^/metrics$")),
    ("POST", re.compile(r"^/users$")),
    ("POST", re.compile(r"^/sessions$")),
    ("GET", re.compile(r"^/notes$")),
    ("POST", re.compile(r"^/notes$")),
    ("GET", re.compile(r"^/notes/(\d+)$")),
    ("PATCH", re.compile(r"^/notes/(\d+)$")),
    ("DELETE", re.compile(r"^/notes/(\d+)$")),
]

METRICS = {"requests_total": 0, "errors_total": 0, "by_status": {}}
LOG = []
_STATE = {"next_id": 1}


class ApiError(Exception):
    """A failure the caller is allowed to read."""

    def __init__(self, status, code, message):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def reset_observability():
    """Zero the counters, empty the log, restart the correlation ids at req-1."""
    # your code here


def split_path(path):
    """(route, params) — the query string parsed into a dict of strings."""
    # your code here


def handle_request(conn, method, path, body=None):
    """(status, payload) for one request. The only public entry point."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from api import handle_request, reset_observability
from db import connect, migrate

conn = connect()
reset_observability()
print("schema version:", migrate(conn))

print("register:", handle_request(conn, "POST", "/users",
                                  {"username": "ada", "password": "difference8"}))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "db.py", "content": r'''
import sqlite3
import time

MIGRATIONS = [
    (1, [
        "CREATE TABLE users ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " username TEXT NOT NULL UNIQUE,"
        " password TEXT NOT NULL,"
        " role TEXT NOT NULL)",
        "CREATE TABLE notes ("
        " id INTEGER PRIMARY KEY AUTOINCREMENT,"
        " owner TEXT NOT NULL,"
        " title TEXT NOT NULL,"
        " body TEXT NOT NULL,"
        " FOREIGN KEY (owner) REFERENCES users(username))",
    ]),
    (2, [
        "ALTER TABLE notes ADD COLUMN pinned INTEGER NOT NULL DEFAULT 0",
        "CREATE INDEX idx_notes_owner ON notes(owner)",
    ]),
]


def connect(path=":memory:"):
    """Row rows, explicit transactions, foreign keys on."""
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.isolation_level = None
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def schema_version(conn):
    """The highest applied migration, or 0."""
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'schema_version'"
    ).fetchone()
    if row is None:
        return 0
    row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
    return row["v"] or 0


def migrate(conn, target=None):
    """Apply pending migrations; returns the resulting version."""
    conn.execute(
        "CREATE TABLE IF NOT EXISTS schema_version ("
        " version INTEGER PRIMARY KEY, applied_at INTEGER NOT NULL)"
    )
    current = schema_version(conn)
    for version, statements in MIGRATIONS:
        if version <= current:
            continue
        if target is not None and version > target:
            break
        conn.execute("BEGIN")
        try:
            for sql in statements:
                conn.execute(sql)
            conn.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                (version, int(time.time())),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
    return schema_version(conn)
'''},
            {"name": "repo.py", "content": r'''
class UserRepo:
    def __init__(self, conn):
        self.conn = conn

    def create(self, username, password_hash, role):
        """Insert a user and return its id. A duplicate raises sqlite3.IntegrityError."""
        cur = self.conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
        return cur.lastrowid

    def by_username(self, username):
        """The full user row as a dict, or None."""
        row = self.conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row is not None else None


class NoteRepo:
    def __init__(self, conn):
        self.conn = conn

    @staticmethod
    def _row(row):
        return {"id": row["id"], "owner": row["owner"], "title": row["title"],
                "body": row["body"], "pinned": bool(row["pinned"])}

    def create(self, owner, title, body, pinned=False):
        """Insert a note and return its id."""
        cur = self.conn.execute(
            "INSERT INTO notes (owner, title, body, pinned) VALUES (?, ?, ?, ?)",
            (owner, title, body, 1 if pinned else 0),
        )
        return cur.lastrowid

    def get(self, note_id):
        """{'id', 'owner', 'title', 'body', 'pinned'} or None."""
        row = self.conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return self._row(row) if row is not None else None

    def list(self, owner=None, limit=10, offset=0):
        """A page of notes ordered by id; owner=None means every owner."""
        if owner is None:
            rows = self.conn.execute(
                "SELECT * FROM notes ORDER BY id LIMIT ? OFFSET ?",
                (limit, offset)).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT * FROM notes WHERE owner = ? ORDER BY id LIMIT ? OFFSET ?",
                (owner, limit, offset)).fetchall()
        return [self._row(row) for row in rows]

    def count(self, owner=None):
        """How many notes, in total or for one owner."""
        if owner is None:
            row = self.conn.execute("SELECT COUNT(*) AS c FROM notes").fetchone()
        else:
            row = self.conn.execute(
                "SELECT COUNT(*) AS c FROM notes WHERE owner = ?", (owner,)).fetchone()
        return row["c"]

    def update(self, note_id, title=None, body=None, pinned=None):
        """Patch the given fields; True when a row changed."""
        assignments, values = [], []
        if title is not None:
            assignments.append("title = ?")
            values.append(title)
        if body is not None:
            assignments.append("body = ?")
            values.append(body)
        if pinned is not None:
            assignments.append("pinned = ?")
            values.append(1 if pinned else 0)
        if not assignments:
            return self.get(note_id) is not None
        values.append(note_id)
        cur = self.conn.execute(
            "UPDATE notes SET " + ", ".join(assignments) + " WHERE id = ?", tuple(values))
        return cur.rowcount > 0

    def delete(self, note_id):
        """True when a row went."""
        cur = self.conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cur.rowcount > 0

    def create_many(self, owner, rows):
        """All-or-nothing insert of [(title, body), ...]."""
        self.conn.execute("BEGIN")
        try:
            ids = []
            for title, body in rows:
                if not str(title).strip():
                    raise ValueError("every note needs a non-empty title")
                ids.append(self.create(owner, title, body))
            self.conn.execute("COMMIT")
            return ids
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
'''},
            {"name": "auth.py", "content": r'''
import base64
import hashlib
import hmac
import json
import secrets

ITERATIONS = 1000
SECRET = b"cap501-demonstration-signing-key"


def _pbkdf2(password, salt, iterations, dklen=32):
    """PBKDF2-HMAC-SHA256, written out longhand.

    The browser runtime has no hashlib.pbkdf2_hmac, and writing the loop makes
    the cost of key stretching visible: each round is one more HMAC an attacker
    must pay for. Server-side Python should call hashlib.pbkdf2_hmac instead.
    """
    out = b""
    block = 1
    while len(out) < dklen:
        u = hmac.new(password, salt + block.to_bytes(4, "big"), hashlib.sha256).digest()
        current = u
        for _ in range(iterations - 1):
            u = hmac.new(password, u, hashlib.sha256).digest()
            current = bytes(a ^ b for a, b in zip(current, u))
        out += current
        block += 1
    return out[:dklen]


def hash_password(password, salt=None, iterations=ITERATIONS):
    """pbkdf2_sha256$rounds$salt$digest. ValueError under 8 characters."""
    if not isinstance(password, str) or len(password) < 8:
        raise ValueError("password must be a string of at least 8 characters")
    if salt is None:
        salt = secrets.token_bytes(16)
    digest = _pbkdf2(password.encode("utf-8"), salt, iterations)
    return "pbkdf2_sha256${0}${1}${2}".format(iterations, salt.hex(), digest.hex())


def verify_password(password, stored):
    """Constant-time comparison; False for anything malformed."""
    try:
        scheme, iterations, salt_hex, digest_hex = stored.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        rounds = int(iterations)
    except (AttributeError, TypeError, ValueError):
        return False
    actual = _pbkdf2(str(password).encode("utf-8"), salt, rounds)
    return hmac.compare_digest(actual, expected)


def _b64(raw):
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _unb64(text):
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def make_token(username, role):
    """payload.signature, the payload unpadded URL-safe base64 of the claims."""
    claims = json.dumps({"sub": username, "role": role},
                        sort_keys=True, separators=(",", ":"))
    payload = _b64(claims.encode("utf-8"))
    signature = hmac.new(SECRET, payload.encode("ascii"), hashlib.sha256).hexdigest()
    return payload + "." + signature


def read_token(token):
    """The claims, or None if the token is malformed or the signature is wrong."""
    if not isinstance(token, str) or token.count(".") != 1:
        return None
    payload, signature = token.split(".")
    expected = hmac.new(SECRET, payload.encode("ascii"), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return None
    try:
        claims = json.loads(_unb64(payload).decode("utf-8"))
    except Exception:
        return None
    if not isinstance(claims, dict) or "sub" not in claims or "role" not in claims:
        return None
    return claims
'''},
            {"name": "api.py", "content": r'''
import re
import sqlite3

import auth
from db import schema_version
from repo import NoteRepo, UserRepo

USERNAME_RE = re.compile(r"^[a-z0-9_]{3,32}$")
MAX_TITLE = 80
MAX_BODY = 2000
MAX_LIMIT = 50

ROUTES = [
    ("GET", re.compile(r"^/health$")),
    ("GET", re.compile(r"^/metrics$")),
    ("POST", re.compile(r"^/users$")),
    ("POST", re.compile(r"^/sessions$")),
    ("GET", re.compile(r"^/notes$")),
    ("POST", re.compile(r"^/notes$")),
    ("GET", re.compile(r"^/notes/(\d+)$")),
    ("PATCH", re.compile(r"^/notes/(\d+)$")),
    ("DELETE", re.compile(r"^/notes/(\d+)$")),
]

METRICS = {"requests_total": 0, "errors_total": 0, "by_status": {}}
LOG = []
_STATE = {"next_id": 1}


class ApiError(Exception):
    """A failure the caller is allowed to read."""

    def __init__(self, status, code, message):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def reset_observability():
    """Zero the counters, empty the log, restart the correlation ids at req-1."""
    METRICS["requests_total"] = 0
    METRICS["errors_total"] = 0
    METRICS["by_status"] = {}
    del LOG[:]
    _STATE["next_id"] = 1


def _next_correlation_id():
    correlation_id = "req-{0}".format(_STATE["next_id"])
    _STATE["next_id"] += 1
    return correlation_id


def split_path(path):
    """(route, params) — the query string parsed into a dict of strings."""
    if not isinstance(path, str) or not path.startswith("/"):
        raise ApiError(404, "not_found", "no route for that path")
    route, _, query = path.partition("?")
    params = {}
    for chunk in query.split("&"):
        if not chunk:
            continue
        key, _, value = chunk.partition("=")
        params[key] = value
    if len(route) > 1 and route.endswith("/"):
        route = route[:-1]
    return route, params


def _int_param(params, name, default, low, high):
    raw = params.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ApiError(400, "invalid_request", "{0} must be an integer".format(name))
    if not low <= value <= high:
        raise ApiError(400, "invalid_request",
                       "{0} must be between {1} and {2}".format(name, low, high))
    return value


def _require_str(body, field, min_len, max_len):
    value = body.get(field)
    if not isinstance(value, str):
        raise ApiError(400, "invalid_request", "{0} must be a string".format(field))
    if not min_len <= len(value) <= max_len:
        raise ApiError(400, "invalid_request",
                       "{0} must be {1}-{2} characters".format(field, min_len, max_len))
    return value


def _require_bool(body, field):
    value = body.get(field)
    if not isinstance(value, bool):
        raise ApiError(400, "invalid_request", "{0} must be a boolean".format(field))
    return value


def _authenticate(body):
    claims = auth.read_token(body.get("token"))
    if claims is None:
        raise ApiError(401, "unauthenticated", "a valid bearer token is required")
    return claims


def _note_or_404(notes, note_id):
    note = notes.get(note_id)
    if note is None:
        raise ApiError(404, "not_found", "no note with that id")
    return note


def _may_touch(claims, note):
    if claims["role"] != "admin" and note["owner"] != claims["sub"]:
        raise ApiError(403, "forbidden", "that note belongs to somebody else")


def _dispatch(conn, method, route, params, body):
    users = UserRepo(conn)
    notes = NoteRepo(conn)

    if (method, route) == ("GET", "/health"):
        return 200, {"status": "ok", "schema_version": schema_version(conn),
                     "checks": {"database": "ok"}}

    if (method, route) == ("POST", "/users"):
        username = _require_str(body, "username", 3, 32)
        if not USERNAME_RE.match(username):
            raise ApiError(400, "invalid_request",
                           "username may hold only a-z, 0-9 and underscore")
        password = _require_str(body, "password", 8, 128)
        role = body.get("role", "user")
        if role not in ("user", "admin"):
            raise ApiError(400, "invalid_request", "role must be 'user' or 'admin'")
        if role == "admin" and _authenticate(body)["role"] != "admin":
            raise ApiError(403, "forbidden", "only an admin may mint an admin")
        try:
            user_id = users.create(username, auth.hash_password(password), role)
        except sqlite3.IntegrityError:
            raise ApiError(409, "conflict", "that username is taken")
        return 201, {"id": user_id, "username": username, "role": role}

    if (method, route) == ("POST", "/sessions"):
        username = body.get("username")
        record = users.by_username(username) if isinstance(username, str) else None
        if record is None or not auth.verify_password(body.get("password"),
                                                      record["password"]):
            raise ApiError(401, "unauthenticated", "username or password is wrong")
        return 200, {"token": auth.make_token(record["username"], record["role"]),
                     "role": record["role"]}

    claims = _authenticate(body)

    if (method, route) == ("GET", "/metrics"):
        if claims["role"] != "admin":
            raise ApiError(403, "forbidden", "metrics are admin-only")
        return 200, {"requests_total": METRICS["requests_total"],
                     "errors_total": METRICS["errors_total"],
                     "by_status": dict(METRICS["by_status"])}

    if (method, route) == ("GET", "/notes"):
        limit = _int_param(params, "limit", 10, 1, MAX_LIMIT)
        offset = _int_param(params, "offset", 0, 0, 10 ** 6)
        owner = None if claims["role"] == "admin" else claims["sub"]
        return 200, {"items": notes.list(owner, limit, offset), "limit": limit,
                     "offset": offset, "total": notes.count(owner)}

    if (method, route) == ("POST", "/notes"):
        title = _require_str(body, "title", 1, MAX_TITLE)
        text = _require_str(body, "body", 0, MAX_BODY)
        pinned = _require_bool(body, "pinned") if "pinned" in body else False
        return 201, notes.get(notes.create(claims["sub"], title, text, pinned))

    match = re.match(r"^/notes/(\d+)$", route)
    if match:
        note_id = int(match.group(1))
        note = _note_or_404(notes, note_id)
        _may_touch(claims, note)
        if method == "GET":
            return 200, note
        if method == "PATCH":
            title = _require_str(body, "title", 1, MAX_TITLE) if "title" in body else None
            text = _require_str(body, "body", 0, MAX_BODY) if "body" in body else None
            pinned = _require_bool(body, "pinned") if "pinned" in body else None
            if title is None and text is None and pinned is None:
                raise ApiError(400, "invalid_request", "nothing to update")
            notes.update(note_id, title, text, pinned)
            return 200, notes.get(note_id)
        if method == "DELETE":
            notes.delete(note_id)
            return 204, None

    raise ApiError(404, "not_found", "no route for that path")


def handle_request(conn, method, path, body=None):
    """(status, payload) for one request. The only public entry point."""
    correlation_id = _next_correlation_id()
    METRICS["requests_total"] += 1
    body = {} if body is None else body
    try:
        if not isinstance(body, dict):
            raise ApiError(400, "invalid_request", "the request body must be an object")
        route, params = split_path(path)
        allowed = [m for m, pattern in ROUTES if pattern.match(route)]
        if allowed and method not in allowed:
            raise ApiError(405, "method_not_allowed",
                           "{0} is not allowed on {1}".format(method, route))
        status, payload = _dispatch(conn, method, route, params, body)
    except ApiError as exc:
        status = exc.status
        payload = {"error": {"code": exc.code, "message": exc.message,
                             "correlation_id": correlation_id}}
        METRICS["errors_total"] += 1
    except Exception:
        status = 500
        payload = {"error": {"code": "internal", "message": "internal server error",
                             "correlation_id": correlation_id}}
        METRICS["errors_total"] += 1
    key = str(status)
    METRICS["by_status"][key] = METRICS["by_status"].get(key, 0) + 1
    LOG.append({"event": "request", "method": method, "path": path,
                "status": status, "correlation_id": correlation_id})
    del LOG[:-200]
    return status, payload
'''},
            {"name": "main.py", "content": r'''
from api import handle_request, reset_observability
from db import connect, migrate

conn = connect()
reset_observability()
print("schema version:", migrate(conn))

print("register:", handle_request(conn, "POST", "/users",
                                  {"username": "ada", "password": "difference8"}))

status, session = handle_request(conn, "POST", "/sessions",
                                 {"username": "ada", "password": "difference8"})
token = session["token"]
print("login:", status)

print("create:", handle_request(conn, "POST", "/notes",
                                {"token": token, "title": "Analytical engine",
                                 "body": "notes on the mill"}))
print("list:", handle_request(conn, "GET", "/notes?limit=5", {"token": token}))
print("health:", handle_request(conn, "GET", "/health"))
print("missing:", handle_request(conn, "GET", "/notes/99", {"token": token})[0])
'''},
        ],
        "tests": [
            {"name": "migrations are idempotent and transactional", "code": r'''
from db import connect, migrate, schema_version
_c = connect()
assert schema_version(_c) == 0, f"a virgin database is at version 0, got {schema_version(_c)!r}"
assert migrate(_c) == 2, "the schema ends at version 2"
assert migrate(_c) == 2, "migrate must be idempotent"
assert _c.execute("SELECT COUNT(*) AS c FROM schema_version").fetchone()["c"] == 2, \
    "exactly one row per applied migration"
assert _c.isolation_level is None, "isolation_level must be None so transactions are explicit"
assert _c.execute("PRAGMA foreign_keys").fetchone()[0] == 1, "foreign keys must be enforced"
_partial = connect()
assert migrate(_partial, 1) == 1, "target = 1 stops after the first migration"
assert "pinned" not in [d[0] for d in _partial.execute("SELECT * FROM notes").description], \
    "migration 2 must not have run"
assert migrate(_partial) == 2, "and the rest applies later"
'''},
            {"name": "the repository parameterises and rolls back", "code": r'''
from db import connect, migrate
from repo import NoteRepo, UserRepo
_c = connect()
migrate(_c)
UserRepo(_c).create("ada", "x", "user")
_notes = NoteRepo(_c)
_evil = "'; DROP TABLE notes; --"
_id = _notes.create("ada", _evil, "body")
assert _notes.get(_id)["title"] == _evil, f"the hostile title must round-trip verbatim, got {_notes.get(_id)['title']!r}"
assert {r[0] for r in _c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")} >= {"notes", "users"}, \
    "both tables must still exist"
assert _notes.get(999) is None, "an unknown id gives None"
assert _notes.update(999, title="x") is False and _notes.delete(999) is False, \
    "updating or deleting a missing row returns False"
_before = _notes.count()
try:
    _notes.create_many("ada", [("good", "1"), ("   ", "2"), ("also good", "3")])
    assert False, "a blank title in the batch must raise"
except ValueError:
    pass
assert _notes.count() == _before, f"the batch must roll back entirely; count went {_before} -> {_notes.count()}"
assert _notes.create_many("ada", [("a", "1"), ("b", "2")]) == [_id + 1, _id + 2], "a clean batch returns its ids"
'''},
            {"name": "passwords are hashed and tokens are signed", "code": r'''
import auth
_stored = auth.hash_password("difference8")
assert _stored.startswith("pbkdf2_sha256$"), f"unexpected hash format {_stored!r}"
assert "difference8" not in _stored, "the password must not appear in the hash"
assert auth.hash_password("difference8") != _stored, "each hash gets a fresh salt"
assert auth.verify_password("difference8", _stored) is True, "the right password verifies"
assert auth.verify_password("difference9", _stored) is False, "a wrong one does not"
for _junk in [None, "", "nonsense", "md5$1$aa$bb", 17]:
    assert auth.verify_password("difference8", _junk) is False, f"malformed stored value {_junk!r} must return False, not raise"
try:
    auth.hash_password("short")
    assert False, "a password under 8 characters must raise ValueError"
except ValueError:
    pass
_token = auth.make_token("ada", "user")
assert auth.read_token(_token) == {"sub": "ada", "role": "user"}, f"got {auth.read_token(_token)!r}"
_payload, _sig = _token.split(".")
_tampered = _payload + "." + ("0" * len(_sig))
assert auth.read_token(_tampered) is None, "a broken signature must be rejected"
_forged = auth.make_token("ada", "admin").split(".")[0] + "." + _sig
assert auth.read_token(_forged) is None, "swapping the payload under an old signature must be rejected"
for _bad in [None, "", "no-dot", "a.b.c", 42]:
    assert auth.read_token(_bad) is None, f"read_token({_bad!r}) must be None"
'''},
            {"name": "registration, conflict and validation", "code": r'''
from api import handle_request, reset_observability
from db import connect, migrate
_conn = connect()
migrate(_conn)
reset_observability()
_status, _body = handle_request(_conn, "POST", "/users", {"username": "ada", "password": "difference8"})
assert _status == 201, f"registration should be 201, got {_status} {_body!r}"
assert _body == {"id": 1, "username": "ada", "role": "user"}, f"got {_body!r}"
assert "password" not in repr(_body), "no credential may come back in the response"
_status, _body = handle_request(_conn, "POST", "/users", {"username": "ada", "password": "difference8"})
assert _status == 409 and _body["error"]["code"] == "conflict", f"a duplicate must be 409, got {_status} {_body!r}"
for _bad in [{"username": "ad", "password": "difference8"},
             {"username": "Ada", "password": "difference8"},
             {"username": "ada2", "password": "short"},
             {"username": "ada2"},
             {"username": "ada2", "password": "difference8", "role": "wizard"}]:
    _status, _body = handle_request(_conn, "POST", "/users", _bad)
    assert _status == 400, f"{_bad!r} should be 400, got {_status} {_body!r}"
    assert _body["error"]["code"] == "invalid_request", f"got {_body!r}"
_status, _body = handle_request(_conn, "POST", "/users",
                                {"username": "eve", "password": "difference8", "role": "admin"})
assert _status == 401, f"minting an admin without a token is 401, got {_status} {_body!r}"
_status, _session = handle_request(_conn, "POST", "/sessions",
                                   {"username": "ada", "password": "difference8"})
assert _status == 200 and set(_session) == {"token", "role"}, f"got {_status} {_session!r}"
_token = _session["token"]
_wrong = handle_request(_conn, "POST", "/sessions", {"username": "ada", "password": "difference9"})
_unknown = handle_request(_conn, "POST", "/sessions", {"username": "nobody", "password": "difference9"})
assert _wrong[0] == 401 and _unknown[0] == 401, f"both failures are 401, got {_wrong[0]} and {_unknown[0]}"
assert _wrong[1] == _unknown[1] or _wrong[1]["error"]["message"] == _unknown[1]["error"]["message"], \
    "a wrong password and an unknown user must read identically"
assert handle_request(_conn, "GET", "/notes")[0] == 401, "no token means 401"
assert handle_request(_conn, "GET", "/notes", {"token": _token[:-1] + "0"})[0] == 401, \
    "a tampered token means 401"
'''},
            {"name": "notes are created, paginated and totalled", "code": r'''
for _i in range(7):
    _status, _note = handle_request(_conn, "POST", "/notes",
                                    {"token": _token, "title": f"note {_i}", "body": "b"})
    assert _status == 201, f"create returned {_status} {_note!r}"
assert _note["owner"] == "ada" and _note["pinned"] is False, f"got {_note!r}"
_status, _page = handle_request(_conn, "GET", "/notes?limit=3&offset=3", {"token": _token})
assert _status == 200, f"got {_status} {_page!r}"
assert [n["title"] for n in _page["items"]] == ["note 3", "note 4", "note 5"], f"got {_page['items']!r}"
assert _page["limit"] == 3 and _page["offset"] == 3 and _page["total"] == 7, f"got {_page!r}"
assert handle_request(_conn, "GET", "/notes", {"token": _token})[1]["limit"] == 10, "limit defaults to 10"
for _bad in ["/notes?limit=x", "/notes?limit=0", "/notes?limit=51", "/notes?offset=-1"]:
    _status, _body = handle_request(_conn, "GET", _bad, {"token": _token})
    assert _status == 400, f"{_bad!r} should be 400, got {_status} {_body!r}"
_status, _body = handle_request(_conn, "POST", "/notes", {"token": _token, "title": "", "body": "b"})
assert _status == 400, f"an empty title should be 400, got {_status} {_body!r}"
_status, _body = handle_request(_conn, "POST", "/notes",
                                {"token": _token, "title": "t", "body": "b", "pinned": "yes"})
assert _status == 400, f"a non-boolean pinned should be 400, got {_status} {_body!r}"
'''},
            {"name": "one user cannot reach another's notes", "code": r'''
handle_request(_conn, "POST", "/users", {"username": "bob", "password": "difference8"})
_bob = handle_request(_conn, "POST", "/sessions",
                      {"username": "bob", "password": "difference8"})[1]["token"]
assert handle_request(_conn, "GET", "/notes", {"token": _bob})[1]["total"] == 0, \
    "bob owns nothing, so he sees nothing"
assert handle_request(_conn, "GET", "/notes/1", {"token": _bob})[0] == 403, \
    "reading somebody else's note is 403, not 404 and not 200"
assert handle_request(_conn, "PATCH", "/notes/1", {"token": _bob, "title": "hijack"})[0] == 403
assert handle_request(_conn, "DELETE", "/notes/1", {"token": _bob})[0] == 403
assert handle_request(_conn, "GET", "/notes/1", {"token": _token})[1]["title"] == "note 0", \
    "the owner still reads their own note unchanged"
'''},
            {"name": "update and delete follow the contract", "code": r'''
_status, _note = handle_request(_conn, "PATCH", "/notes/2",
                                {"token": _token, "title": "renamed", "pinned": True})
assert _status == 200 and _note["title"] == "renamed" and _note["pinned"] is True, f"got {_status} {_note!r}"
assert handle_request(_conn, "GET", "/notes/2", {"token": _token})[1]["title"] == "renamed", "the change must persist"
assert handle_request(_conn, "PATCH", "/notes/2", {"token": _token})[0] == 400, \
    "a patch with nothing to change is a 400"
assert handle_request(_conn, "PATCH", "/notes/999", {"token": _token, "title": "x"})[0] == 404
_status, _payload = handle_request(_conn, "DELETE", "/notes/2", {"token": _token})
assert _status == 204 and _payload is None, f"a delete is 204 with no body, got {_status} {_payload!r}"
assert handle_request(_conn, "DELETE", "/notes/2", {"token": _token})[0] == 404, "deleting it again is 404"
assert handle_request(_conn, "GET", "/notes", {"token": _token})[1]["total"] == 6, "the note really went"
'''},
            {"name": "routing answers 404, 405 and a bad body", "code": r'''
_status, _body = handle_request(_conn, "GET", "/widgets", {"token": _token})
assert _status == 404 and _body["error"]["code"] == "not_found", f"got {_status} {_body!r}"
_status, _body = handle_request(_conn, "PUT", "/notes", {"token": _token})
assert _status == 405 and _body["error"]["code"] == "method_not_allowed", \
    f"a known path with an unknown method is 405, got {_status} {_body!r}"
assert handle_request(_conn, "DELETE", "/health")[0] == 405, "even a public route rejects the wrong method"
_status, _body = handle_request(_conn, "POST", "/notes", "not-a-dict")
assert _status == 400 and _body["error"]["code"] == "invalid_request", f"got {_status} {_body!r}"
for _payload in [_body, handle_request(_conn, "GET", "/widgets", {"token": _token})[1]]:
    assert set(_payload["error"]) == {"code", "message", "correlation_id"}, \
        f"every error carries exactly code, message and correlation_id; got {sorted(_payload['error'])!r}"
'''},
            {"name": "health is public, metrics are not", "code": r'''
_status, _health = handle_request(_conn, "GET", "/health")
assert _status == 200, f"health must answer without a token, got {_status} {_health!r}"
assert _health["status"] == "ok" and _health["schema_version"] == 2, f"got {_health!r}"
assert handle_request(_conn, "GET", "/metrics", {"token": _token})[0] == 403, \
    "a plain user may not read metrics"
assert handle_request(_conn, "GET", "/metrics")[0] == 401, "and an anonymous caller gets 401 first"
_conn.execute("UPDATE users SET role = 'admin' WHERE username = 'bob'")
_admin = handle_request(_conn, "POST", "/sessions",
                        {"username": "bob", "password": "difference8"})[1]["token"]
_status, _metrics = handle_request(_conn, "GET", "/metrics", {"token": _admin})
assert _status == 200, f"an admin may read metrics, got {_status} {_metrics!r}"
assert _metrics["requests_total"] == sum(_metrics["by_status"].values()) + 1, \
    f"this request is counted before dispatch but classified after the snapshot, so the total runs one ahead; got {_metrics!r}"
assert _metrics["errors_total"] > 0 and _metrics["by_status"]["403"] >= 2, f"got {_metrics!r}"
assert handle_request(_conn, "GET", "/notes", {"token": _admin})[1]["total"] == 6, \
    "an admin sees every note, not only their own"
'''},
            {"name": "observability: ids, log bound, reset", "code": r'''
import api
from db import connect, migrate
_fresh = connect()
migrate(_fresh)
api.reset_observability()
assert api.METRICS["requests_total"] == 0 and api.LOG == [], "reset must zero the counters and empty the log"
_status, _body = handle_request(_fresh, "GET", "/notes")
assert _body["error"]["correlation_id"] == "req-1", f"the first request is req-1, got {_body['error']['correlation_id']!r}"
assert handle_request(_fresh, "GET", "/notes")[1]["error"]["correlation_id"] == "req-2", "ids advance"
assert len(api.LOG) == 2 and api.LOG[-1]["status"] == 401, f"the log holds one record per request, got {api.LOG!r}"
assert api.LOG[-1]["correlation_id"] == "req-2", "the log carries the same id as the response"
for _i in range(250):
    handle_request(_fresh, "GET", "/health")
assert len(api.LOG) == 200, f"the log is bounded at 200 records, got {len(api.LOG)}"
assert api.METRICS["requests_total"] == 252, f"every request is counted, got {api.METRICS['requests_total']!r}"
assert api.METRICS["errors_total"] == 2, f"only the two 401s were errors, got {api.METRICS['errors_total']!r}"
'''},
            {"name": "the performance budget holds", "code": r'''
import time
from api import handle_request, reset_observability
from db import connect, migrate
_perf = connect()
migrate(_perf)
reset_observability()
handle_request(_perf, "POST", "/users", {"username": "ada", "password": "difference8"})
_tok = handle_request(_perf, "POST", "/sessions",
                      {"username": "ada", "password": "difference8"})[1]["token"]
for _i in range(40):
    handle_request(_perf, "POST", "/notes", {"token": _tok, "title": f"n{_i}", "body": "b"})
_start = time.perf_counter()
for _i in range(300):
    _status, _page = handle_request(_perf, "GET", "/notes?limit=10&offset=5", {"token": _tok})
_elapsed = time.perf_counter() - _start
assert _status == 200 and len(_page["items"]) == 10, f"the listing must still be correct, got {_status} {_page!r}"
assert _elapsed < 2.0, f"300 list requests took {_elapsed!r}s, over the two-second budget"
'''},
            {"name": "the modules are libraries; main.py is the demonstration", "code": r'''
for _name in ("db.py", "repo.py", "auth.py", "api.py"):
    _src = open(_name).read()
    assert "print(" not in _src, f"{_name} must define names only; the printing belongs in main.py"
_api = open("api.py").read()
assert "pbkdf2" not in _api, "api.py must delegate hashing to auth.py rather than reimplement it"
_auth = open("auth.py").read()
assert "compare_digest" in _auth, "compare tokens and digests with hmac.compare_digest, not =="
_repo = open("repo.py").read()
assert "% (" not in _repo, "SQL values must be bound with ? placeholders, never string formatting"
assert "schema version: 2" in _out, f"main.py should migrate and report the version; stdout was {_out!r}"
assert "login:" in _out and "health:" in _out, f"main.py should demonstrate the happy path; stdout was {_out!r}"
'''},
        ],
    },
}
