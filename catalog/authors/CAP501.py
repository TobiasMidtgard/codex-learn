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
