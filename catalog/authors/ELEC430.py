"""ELEC430 — Data Track: Data Engineering at Scale."""

COURSE = {
    "id": "ELEC430",
    "title": "Data Track — Data Engineering at Scale",
    "year": 4,
    "level": "Advanced",
    "prereqs": ["CS220", "MA201"],
    "stack": ["Python", "SQL"],
    "credits": 10,
    "hours": 140,
    "icon": "⌸",
    "summary": (
        "A data platform is four mechanisms wearing a product name: a validating "
        "ingest that never loses a bad record, a storage layout chosen for the scans "
        "you actually run, a windowed stream that stays correct when events arrive "
        "out of order, and an executor that reads as few bytes as the query allows. "
        "You build all four from scratch, measure them, and finish by proving a batch "
        "path and a stream path over the same data agree."
    ),
    "outcomes": [
        "Enforce a declared schema at ingest with typed coercion and a dead-letter queue",
        "Make a pipeline step idempotent so a replay changes nothing it has already absorbed",
        "Measure run-length and dictionary encoding against a raw column and justify the winner",
        "Quantify the scan cost difference between row-major and column-major layouts",
        "Implement tumbling and sliding windows with watermarks that handle late events correctly",
        "Rewrite a logical plan with predicate pushdown and projection pruning, and show the saving",
        "Choose between hash and sort-merge join from a cost model and cross-check both for equality",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Kleppmann, *Designing Data-Intensive Applications*, O'Reilly 2017 — chapters 3, 10 and 11",
        "Abadi, Boncz & Harizopoulos, *The Design and Implementation of Modern Column-Oriented "
        "Database Systems*, Foundations and Trends in Databases 5(3), 2013",
        "Akidau, Chernyak & Lax, *Streaming Systems*, O'Reilly 2018 — chapters 2-4",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Ingestion: contracts, coercion and replay",
            "summary": "Getting untrusted records into a typed store without losing the rejects.",
            "concepts": [
                "A schema is a contract: field name, type, required flag, default",
                "Coercion versus validation — a CSV field arrives as text and must become a value",
                "Fail-closed on the record, not on the batch: one bad row must not stop ingest",
                "Dead-letter queues keep the raw payload plus a machine-readable reason",
                "Idempotency: an upsert keyed on a business key makes replay a no-op",
                "Distinguishing insert, update and exact duplicate is what makes replay auditable",
                "At-least-once delivery is the normal case; exactly-once is idempotency plus retries",
            ],
            "lab": {
                "title": "Schema-validating ingest with a dead-letter queue",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Records arrive from an upstream feed as loosely typed dictionaries. Your job is
the first step of the pipeline: coerce each field to its declared type, reject
what cannot be coerced, and upsert the survivors into a keyed store so that
re-running the same batch changes nothing.

## `coerce_value(value, type_name)`

Returns the coerced value, or raises `SchemaError`. `FIELD_TYPES` lists the four
legal types. Three rules cover the corner cases:

- `None` never satisfies any type.
- A `bool` satisfies **only** `"bool"` — silently counting `True` as `1` is how
  bad data enters a warehouse.
- Strings are stripped before coercion, so `" 42 "` is a valid `int`.

```text
coerce_value("42", "int")     ->  42
coerce_value(3.0, "int")      ->  3
coerce_value(3.5, "int")      ->  SchemaError
coerce_value("YES", "bool")   ->  True
coerce_value(0, "bool")       ->  False
coerce_value(12, "str")       ->  "12"
coerce_value(True, "int")     ->  SchemaError
```

## `validate_record(record, schema)`

Returns a new dict holding **exactly** the schema's fields, coerced. Fields the
schema does not name are dropped. A field that is absent, `None`, or the empty
string counts as missing: required means `SchemaError`, optional means the
field's `default`. The message must name the offending field, because that
string is what a person reads at 03:00.

## `Ingestor.run(records)`

Ingests one batch and returns that batch's counters as
`{"accepted": n, "updated": n, "duplicate": n, "rejected": n}`. For each record:

- invalid — append `{"raw": record, "reason": str(error)}` to `self.dead_letter`
  and count it as **rejected**;
- key unseen — store it, count **accepted**;
- key seen and the coerced record is identical — count **duplicate**, store
  unchanged;
- key seen and the record differs — overwrite, count **updated**.

`self.stats` accumulates the same four counters across every batch. The
constructor raises `ValueError` when `key_field` is not a schema field.

Replaying an identical batch must leave `self.store` byte-for-byte the same.
''',
                "files": [{"name": "main.py", "content": r'''
FIELD_TYPES = ("int", "float", "bool", "str")
TRUE_STRINGS = {"true", "t", "yes", "y", "1"}
FALSE_STRINGS = {"false", "f", "no", "n", "0"}

SCHEMA = [
    {"name": "id", "type": "int", "required": True},
    {"name": "city", "type": "str", "required": True},
    {"name": "temp_c", "type": "float", "required": True},
    {"name": "verified", "type": "bool", "required": False, "default": False},
]


class SchemaError(ValueError):
    """Raised when a value cannot be coerced or a record breaks the schema."""


def coerce_value(value, type_name):
    """Coerce value to type_name, or raise SchemaError explaining why not."""
    # your code here


def validate_record(record, schema):
    """A coerced copy holding exactly the schema fields. Raises SchemaError."""
    # your code here


class Ingestor:
    """Idempotent upsert of validated records into a store keyed on key_field."""

    def __init__(self, schema, key_field):
        # reject a key_field that is not in the schema, then keep both
        self.schema = schema
        self.key_field = key_field
        self.store = {}
        self.dead_letter = []
        self.stats = {"accepted": 0, "updated": 0, "duplicate": 0, "rejected": 0}

    def run(self, records):
        """Ingest one batch; return this batch's four counters."""
        # your code here


BATCH = [
    {"id": "1", "city": " Oslo ", "temp_c": "3.5"},
    {"id": 2, "city": "Bergen", "temp_c": 7, "verified": "yes"},
    {"id": "three", "city": "Tromso", "temp_c": 1.0},
    {"id": 4, "city": "", "temp_c": 2.0},
]

ingestor = Ingestor(SCHEMA, "id")
print("first  pass:", ingestor.run(BATCH))
print("replay pass:", ingestor.run(BATCH))
print("dead letter:", ingestor.dead_letter)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
FIELD_TYPES = ("int", "float", "bool", "str")
TRUE_STRINGS = {"true", "t", "yes", "y", "1"}
FALSE_STRINGS = {"false", "f", "no", "n", "0"}

SCHEMA = [
    {"name": "id", "type": "int", "required": True},
    {"name": "city", "type": "str", "required": True},
    {"name": "temp_c", "type": "float", "required": True},
    {"name": "verified", "type": "bool", "required": False, "default": False},
]


class SchemaError(ValueError):
    """Raised when a value cannot be coerced or a record breaks the schema."""


def coerce_value(value, type_name):
    """Coerce value to type_name, or raise SchemaError explaining why not."""
    if type_name not in FIELD_TYPES:
        raise SchemaError(f"unknown field type {type_name!r}")
    if value is None:
        raise SchemaError("value is null")
    # A bool is an int in Python; refuse to let that leak into numeric columns.
    if isinstance(value, bool) and type_name != "bool":
        raise SchemaError(f"a bool does not satisfy type {type_name!r}")

    if type_name == "int":
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if value != int(value):
                raise SchemaError(f"{value!r} is not a whole number")
            return int(value)
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                raise SchemaError(f"{value!r} is not an int") from None
        raise SchemaError(f"cannot coerce {type(value).__name__} to int")

    if type_name == "float":
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                raise SchemaError(f"{value!r} is not a float") from None
        raise SchemaError(f"cannot coerce {type(value).__name__} to float")

    if type_name == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, int) and value in (0, 1):
            return bool(value)
        if isinstance(value, str):
            text = value.strip().lower()
            if text in TRUE_STRINGS:
                return True
            if text in FALSE_STRINGS:
                return False
        raise SchemaError(f"{value!r} is not a bool")

    # type_name == "str"
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    raise SchemaError(f"cannot coerce {type(value).__name__} to str")


def validate_record(record, schema):
    """A coerced copy holding exactly the schema fields. Raises SchemaError."""
    if not isinstance(record, dict):
        raise SchemaError("record is not a mapping")
    out = {}
    for field in schema:
        name = field["name"]
        raw = record.get(name)
        if name not in record or raw is None or raw == "":
            if field.get("required"):
                raise SchemaError(f"field {name!r}: missing")
            out[name] = field.get("default")
            continue
        try:
            out[name] = coerce_value(raw, field["type"])
        except SchemaError as exc:
            raise SchemaError(f"field {name!r}: {exc}") from None
    return out


class Ingestor:
    """Idempotent upsert of validated records into a store keyed on key_field."""

    def __init__(self, schema, key_field):
        if key_field not in {field["name"] for field in schema}:
            raise ValueError(f"key field {key_field!r} is not in the schema")
        self.schema = schema
        self.key_field = key_field
        self.store = {}
        self.dead_letter = []
        self.stats = {"accepted": 0, "updated": 0, "duplicate": 0, "rejected": 0}

    def run(self, records):
        """Ingest one batch; return this batch's four counters."""
        batch = {"accepted": 0, "updated": 0, "duplicate": 0, "rejected": 0}
        for raw in records:
            try:
                clean = validate_record(raw, self.schema)
            except SchemaError as exc:
                self.dead_letter.append({"raw": raw, "reason": str(exc)})
                batch["rejected"] += 1
                continue
            key = clean[self.key_field]
            if key not in self.store:
                self.store[key] = clean
                batch["accepted"] += 1
            elif self.store[key] == clean:
                batch["duplicate"] += 1          # replay: nothing to do
            else:
                self.store[key] = clean
                batch["updated"] += 1
        for name, count in batch.items():
            self.stats[name] += count
        return batch


BATCH = [
    {"id": "1", "city": " Oslo ", "temp_c": "3.5"},
    {"id": 2, "city": "Bergen", "temp_c": 7, "verified": "yes"},
    {"id": "three", "city": "Tromso", "temp_c": 1.0},
    {"id": 4, "city": "", "temp_c": 2.0},
]

ingestor = Ingestor(SCHEMA, "id")
print("first  pass:", ingestor.run(BATCH))
print("replay pass:", ingestor.run(BATCH))
print("dead letter:", ingestor.dead_letter)
'''}],
                "hints": [
                    "Handle the two universal rules first — `None`, then `isinstance(value, bool) and type_name != \"bool\"` — before you branch on the type.",
                    "`int(\" 42 \")` already strips, but `float(\"abc\")` raises `ValueError`; catch it and re-raise as `SchemaError` so callers only need one except clause.",
                    "In `validate_record`, treat `name not in record or record[name] is None or record[name] == \"\"` as one missing case, then split on `field.get(\"required\")`.",
                    "Idempotency falls out of comparing the *coerced* record to what is already stored: equal means duplicate, different means update.",
                ],
                "tests": [
                    {"name": "coerce_value accepts the legal forms", "code": r'''
assert coerce_value("42", "int") == 42, f'coerce_value("42","int") gave {coerce_value("42","int")!r}'
assert coerce_value(" 42 ", "int") == 42, "strings are stripped before coercion"
assert coerce_value(3.0, "int") == 3, "an integral float is a valid int"
assert coerce_value(7, "float") == 7.0 and isinstance(coerce_value(7, "float"), float), \
    "an int coerces to float"
assert coerce_value("YES", "bool") is True, "bool strings are case-insensitive"
assert coerce_value("n", "bool") is False, f'coerce_value("n","bool") gave {coerce_value("n","bool")!r}'
assert coerce_value(0, "bool") is False and coerce_value(1, "bool") is True, "0/1 are bools"
assert coerce_value(" Oslo ", "str") == "Oslo", "str values are stripped"
assert coerce_value(12, "str") == "12", "numbers render as strings"
'''},
                    {"name": "coerce_value refuses the rest", "code": r'''
for _value, _type in [("3.5", "int"), (3.5, "int"), ("abc", "float"), ("maybe", "bool"),
                      (2, "bool"), (None, "int"), (None, "str"), ([], "str"),
                      (True, "int"), (True, "float"), (True, "str"), (3, "money")]:
    try:
        coerce_value(_value, _type)
        assert False, f"coerce_value({_value!r}, {_type!r}) should raise SchemaError"
    except SchemaError:
        pass
'''},
                    {"name": "validate_record coerces, projects and defaults", "code": r'''
_got = validate_record({"id": "1", "city": " Oslo ", "temp_c": "3.5", "extra": "drop me"}, SCHEMA)
_want = {"id": 1, "city": "Oslo", "temp_c": 3.5, "verified": False}
assert _got == _want, f"Got {_got!r}, expected {_want}"
assert "extra" not in _got, "fields the schema does not name must be dropped"
_got2 = validate_record({"id": 2, "city": "Bergen", "temp_c": 7, "verified": "yes"}, SCHEMA)
assert _got2 == {"id": 2, "city": "Bergen", "temp_c": 7.0, "verified": True}, f"Got {_got2!r}"
'''},
                    {"name": "validate_record names the field it rejected", "code": r'''
for _bad, _field in [({"id": 1, "city": "Oslo"}, "temp_c"),
                     ({"id": 1, "city": "", "temp_c": 2.0}, "city"),
                     ({"id": 1, "city": "Oslo", "temp_c": None}, "temp_c"),
                     ({"id": "three", "city": "Oslo", "temp_c": 2.0}, "id")]:
    try:
        validate_record(_bad, SCHEMA)
        assert False, f"validate_record({_bad!r}) should raise SchemaError"
    except SchemaError as _exc:
        assert _field in str(_exc), \
            f"reason {str(_exc)!r} should name the offending field {_field!r}"
try:
    validate_record("not a record", SCHEMA)
    assert False, "a non-mapping record should raise SchemaError"
except SchemaError:
    pass
'''},
                    {"name": "Ingestor splits a batch and fills the dead-letter queue", "code": r'''
_ing = Ingestor(SCHEMA, "id")
_batch = _ing.run(BATCH)
assert _batch == {"accepted": 2, "updated": 0, "duplicate": 0, "rejected": 2}, \
    f"first pass gave {_batch!r}"
assert len(_ing.dead_letter) == 2, f"dead_letter holds {len(_ing.dead_letter)} entries, expected 2"
for _entry in _ing.dead_letter:
    assert set(_entry) == {"raw", "reason"}, f"dead-letter entry {_entry!r} needs raw and reason"
    assert isinstance(_entry["reason"], str) and _entry["reason"], "reason must be a non-empty string"
assert _ing.store[1]["city"] == "Oslo", f"store[1] is {_ing.store.get(1)!r}"
assert _ing.store[2]["verified"] is True, "the optional field should be coerced, not defaulted"
'''},
                    {"name": "Replaying a batch changes nothing", "code": r'''
_ing = Ingestor(SCHEMA, "id")
_ing.run(BATCH)
_snapshot = {_k: dict(_v) for _k, _v in _ing.store.items()}
_again = _ing.run(BATCH)
assert _again == {"accepted": 0, "updated": 0, "duplicate": 2, "rejected": 2}, \
    f"replay gave {_again!r}, expected two duplicates and two rejects"
assert _ing.store == _snapshot, "a replay must leave the store untouched"
assert _ing.stats == {"accepted": 2, "updated": 0, "duplicate": 2, "rejected": 4}, \
    f"cumulative stats are {_ing.stats!r}"
'''},
                    {"name": "Changed payloads count as updates; edges behave", "code": r'''
_ing = Ingestor(SCHEMA, "id")
_ing.run([{"id": 1, "city": "Oslo", "temp_c": 3.5}])
_b = _ing.run([{"id": 1, "city": "Oslo", "temp_c": 9.9}])
assert _b == {"accepted": 0, "updated": 1, "duplicate": 0, "rejected": 0}, f"Got {_b!r}"
assert _ing.store[1]["temp_c"] == 9.9, f"store[1] is {_ing.store[1]!r} — an update overwrites"
assert _ing.run([]) == {"accepted": 0, "updated": 0, "duplicate": 0, "rejected": 0}, \
    "an empty batch yields four zeros"
try:
    Ingestor(SCHEMA, "not_a_field")
    assert False, "a key_field outside the schema should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Storage layout and lightweight encodings",
            "summary": "Row-major versus column-major, and what run-length and dictionary coding buy.",
            "concepts": [
                "Row-major stores a tuple contiguously; column-major stores one attribute contiguously",
                "Analytical queries touch few columns and many rows — the layout follows the access pattern",
                "Run-length encoding pays a header per run and wins on sorted, low-entropy columns",
                "Dictionary encoding replaces each value with a fixed-width code; distinct count is the lever",
                "Compression ratio is raw size over encoded size, measured on the real column",
                "Selective scans read only the projected columns; projection pruning is a storage-level win",
                "Encoding choice is per column, not per table, and is a cost decision not a taste one",
            ],
            "lab": {
                "title": "Encodings and a selective-scan cost model",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
A fixed, explicit size model lets you compare layouts without a profiler.

```text
bool  -> 1 byte        int   -> 8 bytes        float -> 8 bytes
str   -> len(utf-8) + 1 byte length prefix     None  -> 1 byte
```

`RUN_HEADER_BYTES` is the count stored with each run; `CODE_BYTES` is the width
of one dictionary code. Both are given.

## Layout

`to_columnar(rows, columns)` turns a list of dicts into `{column: [values]}`.
`to_rows(columnar)` inverts it, and raises `ValueError` when the columns are of
unequal length.

## Encodings

- `rle_encode(values)` -> a list of `(value, count)` runs, in order.
  `rle_decode(runs)` inverts it and raises `ValueError` on a count below 1.
- `dict_encode(values)` -> `(dictionary, codes)`, the dictionary holding each
  distinct value once in first-appearance order. `dict_decode(dictionary, codes)`
  inverts it and raises `ValueError` on a code outside the dictionary.

```text
rle_encode(["red","red","blue"])   ->  [("red", 2), ("blue", 1)]
dict_encode(["a","b","a"])         ->  (["a","b"], [0, 1, 0])
```

## Cost

`raw_size`, `rle_size` and `dict_size` all return bytes under the model above;
`encoded_size(values, encoding)` dispatches on `"raw"`, `"rle"` or `"dict"` and
raises `ValueError` otherwise. `compression_ratio` is raw over encoded, and is
`1.0` for an empty column. `best_encoding(values)` returns the cheapest name,
breaking ties in `ENCODINGS` order.

`scan_cost(rows, projection, layout)` returns the bytes a scan must touch. The
`"row"` layout reads every field of every row regardless of the projection; the
`"columnar"` layout reads only the projected columns. Unknown layouts and
unknown columns raise `ValueError`; no rows costs nothing.

Sanity check to aim at: for `["red"] * 4 + ["blue"] * 4`, raw is 36 bytes, RLE
is 17 and dictionary coding is 41 — run-length wins, and dictionary coding does
not, because eight 4-byte codes cost more than the strings they replace.
''',
                "files": [{"name": "main.py", "content": r'''
CODE_BYTES = 4
RUN_HEADER_BYTES = 4
ENCODINGS = ("raw", "rle", "dict")
LAYOUTS = ("row", "columnar")


def value_size(value):
    """Bytes one value occupies under the course size model."""
    # your code here


def to_columnar(rows, columns):
    """Row-major list of dicts -> column-major {column: [values]}."""
    # your code here


def to_rows(columnar):
    """Column-major {column: [values]} -> row-major list of dicts."""
    # your code here


def raw_size(values):
    """Bytes for an uncompressed column."""
    # your code here


def rle_encode(values):
    """[value, ...] -> [(value, run_length), ...]."""
    # your code here


def rle_decode(runs):
    """[(value, run_length), ...] -> [value, ...]. ValueError on a bad count."""
    # your code here


def rle_size(values):
    """Bytes for the run-length encoded column."""
    # your code here


def dict_encode(values):
    """[value, ...] -> (dictionary, codes)."""
    # your code here


def dict_decode(dictionary, codes):
    """(dictionary, codes) -> [value, ...]. ValueError on an out-of-range code."""
    # your code here


def dict_size(values):
    """Bytes for the dictionary encoded column."""
    # your code here


def encoded_size(values, encoding):
    """Dispatch on the encoding name. ValueError for anything unknown."""
    # your code here


def compression_ratio(values, encoding):
    """raw_size / encoded_size, and 1.0 for an empty column."""
    # your code here


def best_encoding(values):
    """The cheapest encoding name; ties broken in ENCODINGS order."""
    # your code here


def scan_cost(rows, projection, layout):
    """Bytes a scan of these rows must read under the given layout."""
    # your code here


ROWS = [{"id": i, "city": "oslo", "temp": 1.0 * i} for i in range(5)]
RUNS = ["red"] * 4 + ["blue"] * 4
LOWCARD = ["northbound", "southbound"] * 4

print("rle  ", raw_size(RUNS), rle_size(RUNS), dict_size(RUNS), best_encoding(RUNS))
print("dict ", raw_size(LOWCARD), rle_size(LOWCARD), dict_size(LOWCARD), best_encoding(LOWCARD))
print("scan ", scan_cost(ROWS, ["temp"], "row"), scan_cost(ROWS, ["temp"], "columnar"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
CODE_BYTES = 4
RUN_HEADER_BYTES = 4
ENCODINGS = ("raw", "rle", "dict")
LAYOUTS = ("row", "columnar")


def value_size(value):
    """Bytes one value occupies under the course size model."""
    if value is None:
        return 1
    if isinstance(value, bool):
        return 1
    if isinstance(value, (int, float)):
        return 8
    if isinstance(value, str):
        return len(value.encode("utf-8")) + 1
    raise TypeError(f"no size model for {type(value).__name__}")


def to_columnar(rows, columns):
    """Row-major list of dicts -> column-major {column: [values]}."""
    return {name: [row[name] for row in rows] for name in columns}


def to_rows(columnar):
    """Column-major {column: [values]} -> row-major list of dicts."""
    names = list(columnar)
    if not names:
        return []
    height = len(columnar[names[0]])
    for name in names:
        if len(columnar[name]) != height:
            raise ValueError(f"column {name!r} has {len(columnar[name])} values, expected {height}")
    return [{name: columnar[name][i] for name in names} for i in range(height)]


def raw_size(values):
    """Bytes for an uncompressed column."""
    return sum(value_size(value) for value in values)


def rle_encode(values):
    """[value, ...] -> [(value, run_length), ...]."""
    runs = []
    for value in values:
        if runs and runs[-1][0] == value:
            runs[-1] = (value, runs[-1][1] + 1)
        else:
            runs.append((value, 1))
    return runs


def rle_decode(runs):
    """[(value, run_length), ...] -> [value, ...]. ValueError on a bad count."""
    out = []
    for value, count in runs:
        if not isinstance(count, int) or isinstance(count, bool) or count < 1:
            raise ValueError(f"run length {count!r} must be a positive integer")
        out.extend([value] * count)
    return out


def rle_size(values):
    """Bytes for the run-length encoded column."""
    return sum(value_size(value) + RUN_HEADER_BYTES for value, _count in rle_encode(values))


def dict_encode(values):
    """[value, ...] -> (dictionary, codes)."""
    dictionary = []
    index = {}
    codes = []
    for value in values:
        if value not in index:
            index[value] = len(dictionary)
            dictionary.append(value)
        codes.append(index[value])
    return dictionary, codes


def dict_decode(dictionary, codes):
    """(dictionary, codes) -> [value, ...]. ValueError on an out-of-range code."""
    out = []
    for code in codes:
        if not isinstance(code, int) or isinstance(code, bool) or not 0 <= code < len(dictionary):
            raise ValueError(f"code {code!r} is outside a dictionary of {len(dictionary)}")
        out.append(dictionary[code])
    return out


def dict_size(values):
    """Bytes for the dictionary encoded column."""
    dictionary, codes = dict_encode(values)
    return sum(value_size(value) for value in dictionary) + CODE_BYTES * len(codes)


def encoded_size(values, encoding):
    """Dispatch on the encoding name. ValueError for anything unknown."""
    if encoding == "raw":
        return raw_size(values)
    if encoding == "rle":
        return rle_size(values)
    if encoding == "dict":
        return dict_size(values)
    raise ValueError(f"unknown encoding {encoding!r}")


def compression_ratio(values, encoding):
    """raw_size / encoded_size, and 1.0 for an empty column."""
    encoded = encoded_size(values, encoding)
    if encoded == 0:
        return 1.0
    return raw_size(values) / encoded


def best_encoding(values):
    """The cheapest encoding name; ties broken in ENCODINGS order."""
    if not values:
        return "raw"
    return min(ENCODINGS, key=lambda name: (encoded_size(values, name), ENCODINGS.index(name)))


def scan_cost(rows, projection, layout):
    """Bytes a scan of these rows must read under the given layout."""
    if layout not in LAYOUTS:
        raise ValueError(f"unknown layout {layout!r}")
    if not rows:
        return 0
    known = set(rows[0])
    for name in projection:
        if name not in known:
            raise ValueError(f"unknown column {name!r}")
    if layout == "row":
        # A row-major reader pulls the whole tuple off the page, projection or not.
        return sum(value_size(value) for row in rows for value in row.values())
    return sum(value_size(row[name]) for row in rows for name in projection)


ROWS = [{"id": i, "city": "oslo", "temp": 1.0 * i} for i in range(5)]
RUNS = ["red"] * 4 + ["blue"] * 4
LOWCARD = ["northbound", "southbound"] * 4

print("rle  ", raw_size(RUNS), rle_size(RUNS), dict_size(RUNS), best_encoding(RUNS))
print("dict ", raw_size(LOWCARD), rle_size(LOWCARD), dict_size(LOWCARD), best_encoding(LOWCARD))
print("scan ", scan_cost(ROWS, ["temp"], "row"), scan_cost(ROWS, ["temp"], "columnar"))
'''}],
                "hints": [
                    "Check `isinstance(value, bool)` before `isinstance(value, int)` in `value_size`; a bool is an int in Python.",
                    "`rle_encode` only needs to compare against `runs[-1][0]`; rebuild the last tuple rather than trying to mutate it.",
                    "`dict_encode` keeps a side dict from value to code so the lookup stays O(1) while the dictionary list keeps first-appearance order.",
                    "`min(ENCODINGS, key=lambda name: (encoded_size(values, name), ENCODINGS.index(name)))` gives the cheapest with the tie rule for free.",
                ],
                "tests": [
                    {"name": "The size model and the layout transpose", "code": r'''
assert value_size(True) == 1 and value_size(None) == 1, "bools and nulls cost one byte"
assert value_size(7) == 8 and value_size(1.5) == 8, "ints and floats cost eight"
assert value_size("oslo") == 5, f'value_size("oslo") gave {value_size("oslo")!r}, expected 5'
assert value_size("") == 1, "an empty string still pays its length prefix"
_cols = to_columnar(ROWS, ["id", "temp"])
assert _cols["id"] == [0, 1, 2, 3, 4], f"Got {_cols!r}"
assert set(_cols) == {"id", "temp"}, "to_columnar projects to the named columns only"
assert to_rows(_cols) == [{"id": i, "temp": 1.0 * i} for i in range(5)], "round trip failed"
assert to_columnar([], ["id"]) == {"id": []} and to_rows({}) == [], "empty inputs must not crash"
try:
    to_rows({"a": [1, 2], "b": [1]})
    assert False, "ragged columns should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "Run-length encoding round-trips", "code": r'''
assert rle_encode(["red", "red", "blue"]) == [("red", 2), ("blue", 1)], \
    f'Got {rle_encode(["red","red","blue"])!r}'
assert rle_encode([]) == [], "an empty column has no runs"
assert rle_encode([7]) == [(7, 1)], f"Got {rle_encode([7])!r}"
assert rle_encode([1, 1, 1]) == [(1, 3)], "one value means one run"
for _col in [[], [7], RUNS, ["a", "b", "a", "a"], [None, None, 3]]:
    assert rle_decode(rle_encode(_col)) == _col, f"round trip lost {_col!r}"
for _bad in [[("a", 0)], [("a", -2)], [("a", 1.5)], [("a", True)]]:
    try:
        rle_decode(_bad)
        assert False, f"rle_decode({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Dictionary encoding round-trips", "code": r'''
_dictionary, _codes = dict_encode(["a", "b", "a", "c", "b"])
assert _dictionary == ["a", "b", "c"], f"dictionary is {_dictionary!r}, expected first-appearance order"
assert _codes == [0, 1, 0, 2, 1], f"codes are {_codes!r}"
assert dict_encode([]) == ([], []), f"Got {dict_encode([])!r}"
for _col in [[], ["a"], RUNS, LOWCARD, [1, 1, 2]]:
    _d, _c = dict_encode(_col)
    assert dict_decode(_d, _c) == _col, f"round trip lost {_col!r}"
for _bad in [(["a"], [1]), (["a"], [-1]), ([], [0]), (["a"], ["0"])]:
    try:
        dict_decode(*_bad)
        assert False, f"dict_decode{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Measured sizes match the model", "code": r'''
assert raw_size(RUNS) == 36, f"raw_size(RUNS) gave {raw_size(RUNS)!r}, expected 36"
assert rle_size(RUNS) == 17, f"rle_size(RUNS) gave {rle_size(RUNS)!r}, expected 17"
assert dict_size(RUNS) == 41, f"dict_size(RUNS) gave {dict_size(RUNS)!r}, expected 41"
assert raw_size(LOWCARD) == 88, f"raw_size(LOWCARD) gave {raw_size(LOWCARD)!r}, expected 88"
assert dict_size(LOWCARD) == 54, f"dict_size(LOWCARD) gave {dict_size(LOWCARD)!r}, expected 54"
assert raw_size([]) == 0 and rle_size([]) == 0 and dict_size([]) == 0, "an empty column is free"
assert abs(compression_ratio(RUNS, "rle") - 36 / 17) < 1e-12, \
    f'compression_ratio(RUNS,"rle") gave {compression_ratio(RUNS, "rle")!r}'
assert compression_ratio([], "rle") == 1.0, "an empty column has ratio 1.0"
try:
    encoded_size(RUNS, "brotli")
    assert False, "an unknown encoding should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "best_encoding picks the cheapest column codec", "code": r'''
assert best_encoding(RUNS) == "rle", f"best_encoding(RUNS) gave {best_encoding(RUNS)!r}"
assert best_encoding(LOWCARD) == "dict", f"best_encoding(LOWCARD) gave {best_encoding(LOWCARD)!r}"
assert best_encoding(["a", "b", "c", "d"]) == "raw", \
    "short distinct values beat both codecs, and raw wins the tie"
assert best_encoding([]) == "raw", "an empty column reports raw"
'''},
                    {"name": "Selective scans favour the columnar layout", "code": r'''
assert scan_cost(ROWS, ["temp"], "row") == 105, f"Got {scan_cost(ROWS, ['temp'], 'row')!r}, expected 105"
assert scan_cost(ROWS, ["temp"], "columnar") == 40, \
    f"Got {scan_cost(ROWS, ['temp'], 'columnar')!r}, expected 40"
assert scan_cost(ROWS, ["id", "city", "temp"], "columnar") == 105, \
    "projecting every column erases the columnar advantage"
assert scan_cost(ROWS, [], "columnar") == 0, "a count(*) over a columnar layout reads nothing"
assert scan_cost([], ["temp"], "row") == 0, "no rows, no cost"
'''},
                    {"name": "scan_cost rejects nonsense", "code": r'''
try:
    scan_cost(ROWS, ["temp"], "hybrid")
    assert False, "an unknown layout should raise ValueError"
except ValueError:
    pass
try:
    scan_cost(ROWS, ["humidity"], "columnar")
    assert False, "projecting a column that does not exist should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Streaming: windows, watermarks and late data",
            "summary": "Aggregating an unbounded, out-of-order event stream without lying about it.",
            "concepts": [
                "Event time versus processing time — only event time gives reproducible results",
                "Tumbling windows partition time; sliding windows overlap and multiply each event",
                "A watermark is a claim that no event older than T will still arrive",
                "Out-of-order is normal; late is a watermark decision, not a property of the event",
                "Allowed lateness trades completeness against how long state must be retained",
                "Closing a window emits its aggregate and frees its state; reopening is not free",
                "A final flush is what turns an unbounded pipeline into a terminating batch job",
            ],
            "lab": {
                "title": "Windowed aggregation with watermarks",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Events are dicts `{"ts": int, "value": number}` with `ts` an event-time stamp in
seconds, non-negative, arriving in any order.

## `tumbling_start(ts, size)`

The start of the tumbling window containing `ts`. `ValueError` for a
non-positive `size` or a negative / non-integer `ts`.

```text
tumbling_start(0, 5) -> 0     tumbling_start(4, 5) -> 0
tumbling_start(5, 5) -> 5     tumbling_start(13, 5) -> 10
```

## `WindowedAggregator(size, step=None, allowed_lateness=0)`

`step` defaults to `size`, which makes the windows tumbling; a smaller `step`
makes them sliding, so an event lands in several windows at once. All three
arguments are validated in the constructor.

`window_starts(ts)` returns every window start `s` with `s <= ts < s + size`,
ascending, clipped at zero.

```text
WindowedAggregator(5).window_starts(12)        -> [10]
WindowedAggregator(4, 2).window_starts(5)      -> [2, 4]
```

`push(event)` places the event in each of its open windows, advances the
watermark to `max_ts - allowed_lateness`, and returns the list of windows that
this push closed. A window `[start, start + size)` closes as soon as
`start + size <= watermark`. Each emitted result is

```text
{"start": s, "end": s + size, "count": n, "sum": total}
```

emitted in ascending `start` order, exactly once. An event whose windows have
**all** already closed is dropped and `self.late_dropped` is incremented; an
out-of-order event that still has an open window is simply aggregated.

`flush()` closes and returns every window that still holds data, again in
ascending order. Nothing is ever emitted twice.
''',
                "files": [{"name": "main.py", "content": r'''
def tumbling_start(ts, size):
    """Start of the tumbling window of the given size containing ts."""
    # your code here


class WindowedAggregator:
    """Count/sum aggregation over tumbling or sliding event-time windows."""

    def __init__(self, size, step=None, allowed_lateness=0):
        # validate size, step and allowed_lateness, then set up the state below
        self.size = size
        self.step = size if step is None else step
        self.allowed_lateness = allowed_lateness
        self.max_ts = None
        self.watermark = None
        self.windows = {}       # start -> {"count": n, "sum": total}
        self.closed = set()     # starts already emitted
        self.late_dropped = 0

    def window_starts(self, ts):
        """Every window start s with s <= ts < s + size, ascending."""
        # your code here

    def push(self, event):
        """Aggregate one event; return the windows this push closed."""
        # your code here

    def emit_ready(self):
        """Close and return every window the watermark has passed."""
        # your code here

    def flush(self):
        """Close and return everything still open, in ascending start order."""
        # your code here


agg = WindowedAggregator(5, allowed_lateness=0)
for _event in [{"ts": 0, "value": 1.0}, {"ts": 1, "value": 2.0},
               {"ts": 4, "value": 3.0}, {"ts": 7, "value": 4.0}]:
    print(_event["ts"], "->", agg.push(_event))
print("flush:", agg.flush(), "late:", agg.late_dropped)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
def tumbling_start(ts, size):
    """Start of the tumbling window of the given size containing ts."""
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise ValueError(f"window size {size!r} must be a positive integer")
    if not isinstance(ts, int) or isinstance(ts, bool) or ts < 0:
        raise ValueError(f"timestamp {ts!r} must be a non-negative integer")
    return (ts // size) * size


class WindowedAggregator:
    """Count/sum aggregation over tumbling or sliding event-time windows."""

    def __init__(self, size, step=None, allowed_lateness=0):
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ValueError(f"window size {size!r} must be a positive integer")
        if step is None:
            step = size
        if not isinstance(step, int) or isinstance(step, bool) or step <= 0:
            raise ValueError(f"step {step!r} must be a positive integer")
        if (not isinstance(allowed_lateness, int) or isinstance(allowed_lateness, bool)
                or allowed_lateness < 0):
            raise ValueError(f"allowed_lateness {allowed_lateness!r} must be a non-negative integer")
        self.size = size
        self.step = step
        self.allowed_lateness = allowed_lateness
        self.max_ts = None
        self.watermark = None
        self.windows = {}
        self.closed = set()
        self.late_dropped = 0

    def window_starts(self, ts):
        """Every window start s with s <= ts < s + size, ascending."""
        if not isinstance(ts, int) or isinstance(ts, bool) or ts < 0:
            raise ValueError(f"timestamp {ts!r} must be a non-negative integer")
        # The smallest multiple of step that is strictly greater than ts - size.
        first = ((ts - self.size) // self.step + 1) * self.step
        if first < 0:
            first = 0
        return [start for start in range(first, ts + 1, self.step)
                if start <= ts < start + self.size]

    def push(self, event):
        """Aggregate one event; return the windows this push closed."""
        ts = event["ts"]
        value = event["value"]
        starts = self.window_starts(ts)          # also validates ts
        if self.max_ts is None or ts > self.max_ts:
            self.max_ts = ts
        self.watermark = self.max_ts - self.allowed_lateness
        placed = 0
        for start in starts:
            if start in self.closed:
                continue                          # too late for this window
            slot = self.windows.setdefault(start, {"count": 0, "sum": 0.0})
            slot["count"] += 1
            slot["sum"] += value
            placed += 1
        if placed == 0:
            self.late_dropped += 1
        return self.emit_ready()

    def emit_ready(self):
        """Close and return every window the watermark has passed."""
        if self.watermark is None:
            return []
        out = []
        for start in sorted(self.windows):
            if start in self.closed:
                continue
            if start + self.size <= self.watermark:
                self.closed.add(start)
                out.append(self._result(start))
        return out

    def flush(self):
        """Close and return everything still open, in ascending start order."""
        out = []
        for start in sorted(self.windows):
            if start in self.closed:
                continue
            self.closed.add(start)
            out.append(self._result(start))
        return out

    def _result(self, start):
        slot = self.windows[start]
        return {"start": start, "end": start + self.size,
                "count": slot["count"], "sum": slot["sum"]}


agg = WindowedAggregator(5, allowed_lateness=0)
for _event in [{"ts": 0, "value": 1.0}, {"ts": 1, "value": 2.0},
               {"ts": 4, "value": 3.0}, {"ts": 7, "value": 4.0}]:
    print(_event["ts"], "->", agg.push(_event))
print("flush:", agg.flush(), "late:", agg.late_dropped)
'''}],
                "hints": [
                    "`tumbling_start` is `(ts // size) * size` once the arguments are validated — validate first so a negative timestamp never silently floors.",
                    "For `window_starts`, the first candidate is the smallest multiple of `step` greater than `ts - size`: `((ts - size) // step + 1) * step`, clipped at zero.",
                    "Advance `self.watermark` from `self.max_ts` on every push, before you decide what to emit, otherwise a window closes one event late.",
                    "Count an event as late only when *every* one of its windows is already in `self.closed`; a sliding event may still land in a younger window.",
                ],
                "tests": [
                    {"name": "tumbling_start and its guards", "code": r'''
for _ts, _size, _want in [(0, 5, 0), (4, 5, 0), (5, 5, 5), (13, 5, 10), (9, 3, 9)]:
    _got = tumbling_start(_ts, _size)
    assert _got == _want, f"tumbling_start({_ts}, {_size}) gave {_got!r}, expected {_want}"
for _bad in [(5, 0), (5, -1), (-1, 5), (1.5, 5)]:
    try:
        tumbling_start(*_bad)
        assert False, f"tumbling_start{_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "window_starts for tumbling and sliding", "code": r'''
_t = WindowedAggregator(5)
assert _t.window_starts(0) == [0], f"Got {_t.window_starts(0)!r}"
assert _t.window_starts(4) == [0], "4 is still inside [0, 5)"
assert _t.window_starts(5) == [5], "5 opens the next window"
assert _t.window_starts(12) == [10], f"Got {_t.window_starts(12)!r}"
_s = WindowedAggregator(4, 2)
assert _s.window_starts(5) == [2, 4], f"Got {_s.window_starts(5)!r}, expected [2, 4]"
assert _s.window_starts(2) == [0, 2], f"Got {_s.window_starts(2)!r}"
assert _s.window_starts(0) == [0], "starts are clipped at zero"
assert _s.window_starts(1) == [0], f"Got {_s.window_starts(1)!r}"
'''},
                    {"name": "In-order tumbling emission follows the watermark", "code": r'''
_a = WindowedAggregator(5)
assert _a.push({"ts": 0, "value": 1.0}) == [], "nothing can close at watermark 0"
assert _a.push({"ts": 1, "value": 2.0}) == []
assert _a.push({"ts": 4, "value": 3.0}) == [], "watermark 4 has not passed the end of [0, 5)"
_emitted = _a.push({"ts": 5, "value": 10.0})
assert _emitted == [{"start": 0, "end": 5, "count": 3, "sum": 6.0}], f"Got {_emitted!r}"
assert _a.push({"ts": 6, "value": 1.0}) == [], "[0, 5) must not be emitted twice"
_tail = _a.flush()
assert _tail == [{"start": 5, "end": 10, "count": 2, "sum": 11.0}], f"flush gave {_tail!r}"
assert _a.flush() == [], "a second flush has nothing left to say"
'''},
                    {"name": "Out-of-order inside the lateness budget is aggregated", "code": r'''
_a = WindowedAggregator(5, allowed_lateness=3)
assert _a.push({"ts": 6, "value": 1.0}) == [], "watermark is 3, [0, 5) stays open"
assert _a.push({"ts": 2, "value": 4.0}) == [], "a late-but-tolerated event just lands"
assert _a.late_dropped == 0, f"late_dropped is {_a.late_dropped!r}, nothing should be dropped yet"
_emitted = _a.push({"ts": 9, "value": 1.0})
assert _emitted == [{"start": 0, "end": 5, "count": 1, "sum": 4.0}], f"Got {_emitted!r}"
'''},
                    {"name": "An event past its closed window is dropped as late", "code": r'''
_a = WindowedAggregator(5)
_a.push({"ts": 0, "value": 1.0})
assert _a.push({"ts": 7, "value": 2.0}) == [{"start": 0, "end": 5, "count": 1, "sum": 1.0}]
assert _a.push({"ts": 3, "value": 99.0}) == [], "the window it belongs to is already closed"
assert _a.late_dropped == 1, f"late_dropped is {_a.late_dropped!r}, expected 1"
assert _a.windows[0] == {"count": 1, "sum": 1.0}, \
    f"the emitted window was mutated after the fact: {_a.windows[0]!r}"
'''},
                    {"name": "Sliding windows count an event more than once", "code": r'''
_a = WindowedAggregator(4, 2)
for _ts in (0, 1, 2, 3):
    _a.push({"ts": _ts, "value": 1.0})
_emitted = _a.push({"ts": 10, "value": 5.0})
assert _emitted == [{"start": 0, "end": 4, "count": 4, "sum": 4.0},
                    {"start": 2, "end": 6, "count": 2, "sum": 2.0}], f"Got {_emitted!r}"
_tail = _a.flush()
assert [w["start"] for w in _tail] == [8, 10], f"flush gave {_tail!r}"
assert sum(w["count"] for w in _tail) == 2, "ts=10 sits in both [8, 12) and [10, 14)"
'''},
                    {"name": "Constructor and timestamp validation", "code": r'''
for _args, _kwargs in [((0,), {}), ((-3,), {}), ((5, 0), {}), ((5, -1), {}),
                       ((5,), {"allowed_lateness": -1}), ((5,), {"allowed_lateness": 1.5})]:
    try:
        WindowedAggregator(*_args, **_kwargs)
        assert False, f"WindowedAggregator{_args!r} {_kwargs!r} should raise ValueError"
    except ValueError:
        pass
_a = WindowedAggregator(5)
assert _a.emit_ready() == [] and _a.flush() == [], "a fresh aggregator emits nothing"
for _bad in (-1, 1.5, "3"):
    try:
        _a.push({"ts": _bad, "value": 1.0})
        assert False, f"a timestamp of {_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Query execution and join strategy",
            "summary": "Rewriting a logical plan, then paying for the join you chose.",
            "concepts": [
                "A logical plan is a tree; optimisation is a rewrite that preserves its result",
                "Predicate pushdown moves selection below the scan so fewer rows survive early",
                "Projection pruning narrows the scan to the columns the plan actually needs",
                "A pushed predicate pins its own column into the scan, so a residual project may remain",
                "Hash join costs one build plus one probe; sort-merge pays for two sorts",
                "Already-sorted inputs make sort-merge free of its sorts and keep the output ordered",
                "Two join algorithms must agree as multisets even when their row order differs",
            ],
            "lab": {
                "title": "Pushdown, pruning and two join algorithms",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
A plan node is a plain dict. Three operators:

```text
{"op": "scan",    "table": name, "columns": [...] or None, "predicates": [...]}
{"op": "filter",  "predicate": (column, op, value), "child": node}
{"op": "project", "columns": [...], "child": node}
```

A predicate is a `(column, comparator, value)` triple; `COMPARATORS` is given.

## `match(row, predicate)`

`True` when the row satisfies it. `ValueError` for an unknown comparator or a
column the row does not have.

## `execute(node, tables, stats=None)`

Returns `(rows, stats)` where `stats` is
`{"rows_scanned": int, "cells_read": int}`, accumulated across the whole tree.
The accounting is the point:

- **scan** — one `rows_scanned` per row in the table. Per row it reads the union
  of its projected columns (all of them when `columns` is `None`) and the
  columns its predicates test; add that many to `cells_read`. Surviving rows are
  emitted projected to `columns`, in the listed order.
- **filter** — the child's rows are already materialised, so charge exactly one
  extra cell per row reaching the filter, then keep the matches.
- **project** — a rename of the visible columns; it reads nothing extra.

Unknown operators and unknown table names raise `ValueError`.

## `optimise(plan)`

Walk the chain of `project` / `filter` nodes down to the scan. Push every
predicate into the scan's `predicates`. Take the **topmost** projection as the
required columns, append any predicate column missing from it, and set that list
as the scan's `columns`. If the scan's column list is then wider than the
required projection, keep one `project` node on top so the result is identical
to the unoptimised plan; otherwise return the bare scan. A plan that does not
bottom out in a scan raises `ValueError`.

## Joins

`hash_join(left, right, left_key, right_key)` builds a hash table on the right
input and probes with the left, emitting `{**left_row, **right_row}` in left
order then right order. `sort_merge_join` sorts both sides and merges; it must
handle repeated keys on both sides. The two need not agree on row order —
`same_rows` is given for the multiset comparison.

`join_cost(n, m, algorithm, left_sorted=False, right_sorted=False)`:

```text
hash        ->  n + m
sort_merge  ->  n + m, plus n*log2(n) if the left is unsorted,
                         plus m*log2(m) if the right is unsorted
```

`choose_join(...)` returns `"sort_merge"` when it costs no more than hashing,
and `"hash"` otherwise. An unknown algorithm raises `ValueError`.
''',
                "files": [{"name": "main.py", "content": r'''
import math

COMPARATORS = {
    "=": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
}

EVENTS = [
    {"event_id": 1, "user_id": 10, "kind": "click", "ms": 120},
    {"event_id": 2, "user_id": 11, "kind": "view", "ms": 80},
    {"event_id": 3, "user_id": 10, "kind": "click", "ms": 300},
    {"event_id": 4, "user_id": 12, "kind": "click", "ms": 45},
    {"event_id": 5, "user_id": 11, "kind": "click", "ms": 210},
]

USERS = [
    {"user_id": 10, "country": "no"},
    {"user_id": 11, "country": "se"},
    {"user_id": 13, "country": "dk"},
]

TABLES = {"events": EVENTS, "users": USERS}

SCAN = {"op": "scan", "table": "events", "columns": None, "predicates": []}
PLAN = {"op": "project", "columns": ["event_id"],
        "child": {"op": "filter", "predicate": ("kind", "=", "click"), "child": SCAN}}


def same_rows(left, right):
    """True when two row lists hold the same rows, order ignored. Given."""
    return (sorted(repr(sorted(row.items())) for row in left)
            == sorted(repr(sorted(row.items())) for row in right))


def match(row, predicate):
    """True when row satisfies (column, comparator, value)."""
    # your code here


def execute(node, tables, stats=None):
    """Run a plan; return (rows, {"rows_scanned": n, "cells_read": n})."""
    # your code here


def optimise(plan):
    """Push predicates into the scan and prune its columns."""
    # your code here


def hash_join(left, right, left_key, right_key):
    """Build on right, probe with left."""
    # your code here


def sort_merge_join(left, right, left_key, right_key):
    """Sort both sides, then merge equal-key groups."""
    # your code here


def join_cost(n, m, algorithm, left_sorted=False, right_sorted=False):
    """Cost of joining n left rows with m right rows."""
    # your code here


def choose_join(n, m, left_sorted=False, right_sorted=False):
    """The cheaper algorithm name; sort_merge wins ties."""
    # your code here


print("plain    ", execute(PLAN, TABLES))
print("optimised", execute(optimise(PLAN), TABLES))
print("join     ", hash_join(EVENTS, USERS, "user_id", "user_id"))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import math

COMPARATORS = {
    "=": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
}

EVENTS = [
    {"event_id": 1, "user_id": 10, "kind": "click", "ms": 120},
    {"event_id": 2, "user_id": 11, "kind": "view", "ms": 80},
    {"event_id": 3, "user_id": 10, "kind": "click", "ms": 300},
    {"event_id": 4, "user_id": 12, "kind": "click", "ms": 45},
    {"event_id": 5, "user_id": 11, "kind": "click", "ms": 210},
]

USERS = [
    {"user_id": 10, "country": "no"},
    {"user_id": 11, "country": "se"},
    {"user_id": 13, "country": "dk"},
]

TABLES = {"events": EVENTS, "users": USERS}

SCAN = {"op": "scan", "table": "events", "columns": None, "predicates": []}
PLAN = {"op": "project", "columns": ["event_id"],
        "child": {"op": "filter", "predicate": ("kind", "=", "click"), "child": SCAN}}


def same_rows(left, right):
    """True when two row lists hold the same rows, order ignored. Given."""
    return (sorted(repr(sorted(row.items())) for row in left)
            == sorted(repr(sorted(row.items())) for row in right))


def match(row, predicate):
    """True when row satisfies (column, comparator, value)."""
    column, comparator, value = predicate
    if comparator not in COMPARATORS:
        raise ValueError(f"unknown comparator {comparator!r}")
    if column not in row:
        raise ValueError(f"unknown column {column!r}")
    return COMPARATORS[comparator](row[column], value)


def execute(node, tables, stats=None):
    """Run a plan; return (rows, {"rows_scanned": n, "cells_read": n})."""
    if stats is None:
        stats = {"rows_scanned": 0, "cells_read": 0}
    op = node.get("op")

    if op == "scan":
        if node["table"] not in tables:
            raise ValueError(f"unknown table {node['table']!r}")
        columns = node.get("columns")
        predicates = list(node.get("predicates") or [])
        predicate_columns = {p[0] for p in predicates}
        out = []
        for row in tables[node["table"]]:
            stats["rows_scanned"] += 1
            visible = set(columns) if columns is not None else set(row)
            stats["cells_read"] += len(visible | predicate_columns)
            if all(match(row, p) for p in predicates):
                out.append(dict(row) if columns is None
                           else {name: row[name] for name in columns})
        return out, stats

    if op == "filter":
        rows, stats = execute(node["child"], tables, stats)
        # One column read per row that actually reaches the filter.
        stats["cells_read"] += len(rows)
        return [row for row in rows if match(row, node["predicate"])], stats

    if op == "project":
        rows, stats = execute(node["child"], tables, stats)
        columns = node["columns"]
        return [{name: row[name] for name in columns} for row in rows], stats

    raise ValueError(f"unknown plan node {op!r}")


def optimise(plan):
    """Push predicates into the scan and prune its columns."""
    projection = None
    pushed = []
    node = plan
    while node.get("op") in ("project", "filter"):
        if node["op"] == "project":
            if projection is None:
                projection = list(node["columns"])
        else:
            pushed.append(tuple(node["predicate"]))
        node = node["child"]
    if node.get("op") != "scan":
        raise ValueError("a plan must bottom out in a scan")

    scan = {"op": "scan", "table": node["table"], "columns": None,
            "predicates": [tuple(p) for p in node.get("predicates") or []] + pushed}
    if projection is None:
        return scan

    needed = list(projection)
    for column, _comparator, _value in scan["predicates"]:
        if column not in needed:
            needed.append(column)     # the scan must still be able to test it
    scan["columns"] = needed
    if needed == projection:
        return scan
    return {"op": "project", "columns": projection, "child": scan}


def hash_join(left, right, left_key, right_key):
    """Build on right, probe with left."""
    index = {}
    for row in right:
        index.setdefault(row[right_key], []).append(row)
    out = []
    for row in left:
        for partner in index.get(row[left_key], ()):
            out.append({**row, **partner})
    return out


def sort_merge_join(left, right, left_key, right_key):
    """Sort both sides, then merge equal-key groups."""
    ls = sorted(left, key=lambda row: row[left_key])
    rs = sorted(right, key=lambda row: row[right_key])
    out = []
    i = j = 0
    while i < len(ls) and j < len(rs):
        lk = ls[i][left_key]
        rk = rs[j][right_key]
        if lk < rk:
            i += 1
        elif lk > rk:
            j += 1
        else:
            i_end = i
            while i_end < len(ls) and ls[i_end][left_key] == lk:
                i_end += 1
            j_end = j
            while j_end < len(rs) and rs[j_end][right_key] == rk:
                j_end += 1
            for a in range(i, i_end):
                for b in range(j, j_end):
                    out.append({**ls[a], **rs[b]})
            i, j = i_end, j_end
    return out


def join_cost(n, m, algorithm, left_sorted=False, right_sorted=False):
    """Cost of joining n left rows with m right rows."""
    if algorithm == "hash":
        return float(n + m)
    if algorithm == "sort_merge":
        cost = float(n + m)
        if not left_sorted and n > 1:
            cost += n * math.log2(n)
        if not right_sorted and m > 1:
            cost += m * math.log2(m)
        return cost
    raise ValueError(f"unknown join algorithm {algorithm!r}")


def choose_join(n, m, left_sorted=False, right_sorted=False):
    """The cheaper algorithm name; sort_merge wins ties."""
    merge = join_cost(n, m, "sort_merge", left_sorted, right_sorted)
    return "sort_merge" if merge <= join_cost(n, m, "hash") else "hash"


print("plain    ", execute(PLAN, TABLES))
print("optimised", execute(optimise(PLAN), TABLES))
print("join     ", hash_join(EVENTS, USERS, "user_id", "user_id"))
'''}],
                "hints": [
                    "Thread one `stats` dict through the recursion rather than merging dicts on the way back up; `execute` returns it so the caller sees the total.",
                    "In the scan, the cells read per row are `len(set(columns or row) | {p[0] for p in predicates})` — the predicate column must be read even when it is not projected.",
                    "`optimise` is a loop, not a recursion: walk down while the node is a project or a filter, collecting as you go, then rebuild from the scan upwards.",
                    "For `sort_merge_join`, advance two indices to the end of each equal-key group and emit the full cross product of the two groups — a repeated key on both sides must produce every pair.",
                ],
                "tests": [
                    {"name": "match evaluates and rejects", "code": r'''
_row = {"kind": "click", "ms": 120}
assert match(_row, ("kind", "=", "click")) is True, "equality on a string"
assert match(_row, ("kind", "!=", "view")) is True
assert match(_row, ("ms", ">", 200)) is False, f'Got {match(_row, ("ms", ">", 200))!r}'
assert match(_row, ("ms", ">=", 120)) is True
try:
    match(_row, ("ms", "~", 1))
    assert False, "an unknown comparator should raise ValueError"
except ValueError:
    pass
try:
    match(_row, ("country", "=", "no"))
    assert False, "a column the row lacks should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "execute runs the unoptimised plan and counts", "code": r'''
_rows, _stats = execute(PLAN, TABLES)
assert _rows == [{"event_id": 1}, {"event_id": 3}, {"event_id": 4}, {"event_id": 5}], f"Got {_rows!r}"
assert _stats == {"rows_scanned": 5, "cells_read": 25}, \
    f"Got {_stats!r}, expected 5 rows and 20 scan cells plus 5 filter cells"
_all, _s2 = execute(SCAN, TABLES)
assert _all == EVENTS and _s2 == {"rows_scanned": 5, "cells_read": 20}, f"Got {_s2!r}"
try:
    execute({"op": "sort", "child": SCAN}, TABLES)
    assert False, "an unknown operator should raise ValueError"
except ValueError:
    pass
try:
    execute({"op": "scan", "table": "nope", "columns": None, "predicates": []}, TABLES)
    assert False, "an unknown table should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "optimise pushes predicates and prunes columns", "code": r'''
_opt = optimise(PLAN)
assert _opt["op"] == "project" and _opt["columns"] == ["event_id"], \
    f"expected a residual project over the scan, got {_opt!r}"
_scan = _opt["child"]
assert _scan["op"] == "scan" and _scan["table"] == "events", f"Got {_scan!r}"
assert [tuple(p) for p in _scan["predicates"]] == [("kind", "=", "click")], \
    f"predicates are {_scan['predicates']!r} — the filter should have moved into the scan"
assert _scan["columns"] == ["event_id", "kind"], \
    f"columns are {_scan['columns']!r}; the pushed predicate pins kind into the scan"
'''},
                    {"name": "The rewrite preserves the result and reads less", "code": r'''
_plain_rows, _plain_stats = execute(PLAN, TABLES)
_opt_rows, _opt_stats = execute(optimise(PLAN), TABLES)
assert _opt_rows == _plain_rows, f"the rewrite changed the answer: {_opt_rows!r}"
assert _opt_stats["cells_read"] < _plain_stats["cells_read"], \
    f"optimised read {_opt_stats['cells_read']} cells, plain read {_plain_stats['cells_read']}"
assert _opt_stats == {"rows_scanned": 5, "cells_read": 10}, f"Got {_opt_stats!r}"
_covering = {"op": "project", "columns": ["event_id", "kind"],
             "child": {"op": "filter", "predicate": ("kind", "=", "click"), "child": SCAN}}
assert optimise(_covering)["op"] == "scan", \
    "when the projection already covers the predicate column, no project node is needed"
try:
    optimise({"op": "filter", "predicate": ("kind", "=", "click"), "child": {"op": "limit"}})
    assert False, "a plan that does not bottom out in a scan should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "hash_join handles repeats, misses and empties", "code": r'''
_got = hash_join(EVENTS, USERS, "user_id", "user_id")
assert [r["event_id"] for r in _got] == [1, 2, 3, 5], f"Got {[r['event_id'] for r in _got]!r}"
assert _got[0] == {"event_id": 1, "user_id": 10, "kind": "click", "ms": 120, "country": "no"}, \
    f"Got {_got[0]!r}"
assert all(r["user_id"] != 12 for r in _got), "user 12 has no matching user row"
_many = hash_join([{"k": 1}, {"k": 1}], [{"k": 1, "v": "a"}, {"k": 1, "v": "b"}], "k", "k")
assert len(_many) == 4, f"a 2x2 key group should give 4 rows, got {len(_many)}"
assert hash_join([], USERS, "user_id", "user_id") == [], "an empty left input joins to nothing"
assert hash_join(EVENTS, [], "user_id", "user_id") == [], "an empty right input joins to nothing"
'''},
                    {"name": "sort_merge_join agrees with hash_join", "code": r'''
for _left, _right in [(EVENTS, USERS), ([], USERS), (EVENTS, []),
                      ([{"k": 1}, {"k": 1}, {"k": 2}],
                       [{"k": 1, "v": "a"}, {"k": 1, "v": "b"}, {"k": 3, "v": "c"}])]:
    _lk = "user_id" if _left is EVENTS or _left == [] and _right is USERS else "k"
    _rk = "user_id" if _right is USERS else "k"
    if _left and _right and _lk not in _left[0]:
        _lk = "k"
    _h = hash_join(_left, _right, _lk, _rk)
    _m = sort_merge_join(_left, _right, _lk, _rk)
    assert same_rows(_h, _m), f"hash gave {_h!r} but sort-merge gave {_m!r}"
_m = sort_merge_join([{"k": 1}, {"k": 1}], [{"k": 1, "v": "a"}, {"k": 1, "v": "b"}], "k", "k")
assert len(_m) == 4, f"a 2x2 key group should give 4 rows, got {len(_m)}"
'''},
                    {"name": "The join cost model drives the choice", "code": r'''
assert join_cost(100, 50, "hash") == 150.0, f"Got {join_cost(100, 50, 'hash')!r}"
_want = 150.0 + 100 * math.log2(100) + 50 * math.log2(50)
assert abs(join_cost(100, 50, "sort_merge") - _want) < 1e-9, \
    f"Got {join_cost(100, 50, 'sort_merge')!r}, expected {_want}"
assert join_cost(100, 50, "sort_merge", True, True) == 150.0, "sorted inputs skip both sorts"
assert join_cost(1, 1, "sort_merge") == 2.0, "a single row needs no sorting"
assert choose_join(100, 50) == "hash", "unsorted inputs favour hashing"
assert choose_join(100, 50, True, True) == "sort_merge", \
    "when both inputs are sorted the merge costs no more and keeps the order"
assert choose_join(0, 0) == "sort_merge", "empty inputs tie, and the tie goes to sort_merge"
try:
    join_cost(10, 10, "nested_loop")
    assert False, "an unknown algorithm should raise ValueError"
except ValueError:
    pass
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a reconciled batch-and-stream pipeline",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
The Lambda architecture's unpaid debt is proof: two code paths over the same
data, and nothing that shows they agree. You build both paths against one
declared contract and finish with a reconciliation report.

`pipeline.py` holds every function the checks import. `main.py` is the demo
run. `CONTRACT` is given.

## Contract enforcement

- `coerce(value, type_name)` — `"int"`, `"float"` and `"str"` only. `None`, the
  empty string and any `bool` are refused; strings are stripped; an integral
  float is a valid int. Raises `ContractError`.
- `validate(record, contract)` — returns a dict of exactly the contract's
  fields, coerced. A missing optional field takes its `default`; a missing or
  uncoercible required field raises `ContractError` whose message names the
  field.

## Batch path

`batch_aggregate(records, contract, window_size)` returns

```text
{"windows": {start: {"count": n, "sum": total}},
 "rows": [...], "accepted": n, "duplicates": n, "dead_letter": [...]}
```

Records are deduplicated on the contract's `key` — first occurrence wins — and
bucketed into tumbling windows on the contract's `event_time`. Rejects go to
`dead_letter` as `{"raw": ..., "reason": ...}`. A non-positive `window_size`
raises `ValueError`.

## Stream path

`StreamPipeline(contract, window_size, allowed_lateness=0)` sees the same
records one at a time, in arrival order. `push(record)` returns the windows that
this record closed; `close()` returns the rest. It maintains `results`
(`{start: {"count", "sum"}}`), `watermark`, `dead_letter`, `duplicates`,
`late_dropped` and `accepted`. Deduplication is on the same key, the watermark
is `max_ts - allowed_lateness`, and a record whose window has already been
emitted is dropped and counted in `late_dropped`.

## Quality, lineage, reconciliation

- `quality_report(rows, rules)` — rules are `{"kind": "not_null"|"range"|
  "unique", "column": name, ...}` with `min`/`max` for `range`. Returns
  `{"passed": bool, "checks": [{"rule", "column", "failed", "passed"}]}`.
  Unknown kinds raise `ValueError`.
- `lineage(source, contract, stats)` — returns `source`, `contract_name`,
  `contract_version`, a copy of `stats`, and a `fingerprint`: the first 16 hex
  characters of the SHA-256 of a key-sorted, compact JSON rendering of the
  source, contract name and version, and stats. Same inputs, same fingerprint.
- `reconcile(batch_windows, stream_windows, tolerance=1e-9)` — returns
  `matched`, `windows_compared`, `only_in_batch`, `only_in_stream` and
  `differences`, each difference being `{"window", "batch", "stream"}`.
- `render_report(recon, meta)` — a multi-line string carrying the fingerprint
  and the word `MATCH` or `MISMATCH`.

## The result you are after

With a generous `allowed_lateness`, the two paths reconcile exactly. With
`allowed_lateness=0` and out-of-order input, they must not — and the report has
to say which window diverged and by how much.
''',
        "deliverables": [
            "`pipeline.py` — contract enforcement, batch path, stream path, quality, lineage and reconciliation, importable with no side effects",
            "`main.py` — a demo that runs both paths over the same records and prints the report twice, once per lateness setting",
            "A dead-letter queue that keeps the raw payload and a reason naming the offending field",
            "Deduplication on the contract key that is identical in both paths",
            "Lineage metadata with a deterministic fingerprint over source, contract version and counts",
            "A reconciliation report that names the diverging window and its batch and stream aggregates",
        ],
        "constraints": [
            "Standard library only — `json` and `hashlib` are the only imports you need",
            "`pipeline.py` must define functions and classes only; importing it must print nothing",
            "Both paths must dedupe on the same key with the same first-wins rule, or reconciliation proves nothing",
            "No wall-clock time anywhere: every window decision is made from event time and the watermark",
            "Two `StreamPipeline` objects must not share state",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "All automated checks pass, including the empty-input, duplicate and late-event edge cases."},
            {"criterion": "Contract enforcement", "weight": 20,
             "evidence": "Bad records are coerced or dead-lettered with a reason naming the field; no bad record reaches an aggregate."},
            {"criterion": "Batch/stream equivalence", "weight": 20,
             "evidence": "With sufficient allowed lateness the two paths reconcile exactly; with none, the report names the diverging window."},
            {"criterion": "Lineage & reporting", "weight": 12,
             "evidence": "Fingerprints are deterministic and change with the inputs; the rendered report is readable and states MATCH or MISMATCH."},
            {"criterion": "Readability", "weight": 8,
             "evidence": "Docstrings on every public function, no dead code, no debug prints left in pipeline.py."},
        ],
        "hints": [
            "Write `coerce` and `validate` first and reuse them from both paths — a second copy is how the two paths start disagreeing for the wrong reason.",
            "Advance the watermark on every *valid* record, including duplicates, before you decide what to emit; do the dedupe check afterwards.",
            "`(ts // window_size) * window_size` is the tumbling start in both paths; sharing that one expression is what makes reconciliation meaningful.",
            "`json.dumps(payload, sort_keys=True, separators=(\",\", \":\"))` gives a canonical byte string, so the SHA-256 over it is stable across runs.",
            "For the mismatch demo, feed an event whose window the watermark has already closed — the batch path has no watermark and will still count it.",
        ],
        "files": [
            {"name": "pipeline.py", "content": r'''
import hashlib
import json

CONTRACT = {
    "name": "sensor_readings",
    "version": "1.2.0",
    "key": "reading_id",
    "event_time": "ts",
    "fields": [
        {"name": "reading_id", "type": "str", "required": True},
        {"name": "sensor", "type": "str", "required": True},
        {"name": "ts", "type": "int", "required": True},
        {"name": "value", "type": "float", "required": True},
    ],
}

CONTRACT_TYPES = ("int", "float", "str")


class ContractError(ValueError):
    """Raised when a record does not satisfy the declared contract."""


def coerce(value, type_name):
    """Coerce one value to a contract type, or raise ContractError."""
    # your code here


def validate(record, contract):
    """A coerced copy holding exactly the contract fields. Raises ContractError."""
    # your code here


def window_start(ts, window_size):
    """Start of the tumbling window containing ts."""
    # your code here


def batch_aggregate(records, contract, window_size):
    """Deduplicate, validate and bucket a whole batch into tumbling windows."""
    # your code here


class StreamPipeline:
    """The same aggregation, one record at a time, driven by a watermark."""

    def __init__(self, contract, window_size, allowed_lateness=0):
        # validate window_size and allowed_lateness, then set up the state below
        self.contract = contract
        self.window_size = window_size
        self.allowed_lateness = allowed_lateness
        self.results = {}
        self.closed = set()
        self.seen_keys = set()
        self.dead_letter = []
        self.duplicates = 0
        self.late_dropped = 0
        self.accepted = 0
        self.max_ts = None
        self.watermark = None

    def push(self, record):
        """Absorb one record; return the windows this record closed."""
        # your code here

    def emit_ready(self):
        """Close and return every window the watermark has passed."""
        # your code here

    def close(self):
        """Close and return everything still open, ascending."""
        # your code here


def quality_report(rows, rules):
    """Run data-quality rules over the accepted rows."""
    # your code here


def lineage(source, contract, stats):
    """Lineage metadata with a deterministic fingerprint."""
    # your code here


def reconcile(batch_windows, stream_windows, tolerance=1e-9):
    """Compare two window dicts and describe every disagreement."""
    # your code here


def render_report(recon, meta):
    """A human-readable reconciliation report."""
    # your code here
'''},
            {"name": "main.py", "content": r'''
from pipeline import (CONTRACT, StreamPipeline, batch_aggregate, lineage,
                      quality_report, reconcile, render_report)

WINDOW = 10

RECORDS = [
    {"reading_id": "a", "sensor": "s1", "ts": 1, "value": 1.0},
    {"reading_id": "b", "sensor": "s1", "ts": 4, "value": "2.0"},
    {"reading_id": "c", "sensor": "s2", "ts": 11, "value": 3.0},
    {"reading_id": "d", "sensor": "s2", "ts": 7, "value": 4.0},
    {"reading_id": "e", "sensor": "s1", "ts": 15, "value": 5.0},
    {"reading_id": "a", "sensor": "s1", "ts": 1, "value": 1.0},
    {"reading_id": "f", "sensor": "", "ts": 3, "value": 9.0},
]

RULES = [
    {"kind": "not_null", "column": "sensor"},
    {"kind": "unique", "column": "reading_id"},
    {"kind": "range", "column": "value", "min": -50.0, "max": 100.0},
]

batch = batch_aggregate(RECORDS, CONTRACT, WINDOW)
print("quality:", quality_report(batch["rows"], RULES)["passed"])

for lateness in (0, 5):
    stream = StreamPipeline(CONTRACT, WINDOW, allowed_lateness=lateness)
    for record in RECORDS:
        stream.push(record)
    stream.close()
    recon = reconcile(batch["windows"], stream.results)
    meta = lineage(f"feed:lateness={lateness}", CONTRACT,
                   {"batch_accepted": batch["accepted"], "stream_accepted": stream.accepted,
                    "late_dropped": stream.late_dropped})
    print(render_report(recon, meta))
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "pipeline.py", "content": r'''
import hashlib
import json

CONTRACT = {
    "name": "sensor_readings",
    "version": "1.2.0",
    "key": "reading_id",
    "event_time": "ts",
    "fields": [
        {"name": "reading_id", "type": "str", "required": True},
        {"name": "sensor", "type": "str", "required": True},
        {"name": "ts", "type": "int", "required": True},
        {"name": "value", "type": "float", "required": True},
    ],
}

CONTRACT_TYPES = ("int", "float", "str")


class ContractError(ValueError):
    """Raised when a record does not satisfy the declared contract."""


def coerce(value, type_name):
    """Coerce one value to a contract type, or raise ContractError."""
    if type_name not in CONTRACT_TYPES:
        raise ContractError(f"unknown contract type {type_name!r}")
    if value is None:
        raise ContractError("value is null")
    if isinstance(value, bool):
        raise ContractError("a bool satisfies no contract type")
    if isinstance(value, str) and not value.strip():
        raise ContractError("value is blank")

    if type_name == "int":
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if value != int(value):
                raise ContractError(f"{value!r} is not a whole number")
            return int(value)
        if isinstance(value, str):
            try:
                return int(value.strip())
            except ValueError:
                raise ContractError(f"{value!r} is not an int") from None
        raise ContractError(f"cannot coerce {type(value).__name__} to int")

    if type_name == "float":
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value.strip())
            except ValueError:
                raise ContractError(f"{value!r} is not a float") from None
        raise ContractError(f"cannot coerce {type(value).__name__} to float")

    # type_name == "str"
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float)):
        return str(value)
    raise ContractError(f"cannot coerce {type(value).__name__} to str")


def validate(record, contract):
    """A coerced copy holding exactly the contract fields. Raises ContractError."""
    if not isinstance(record, dict):
        raise ContractError("record is not a mapping")
    out = {}
    for field in contract["fields"]:
        name = field["name"]
        if name not in record:
            if field.get("required", False):
                raise ContractError(f"field {name!r}: missing")
            out[name] = field.get("default")
            continue
        try:
            out[name] = coerce(record[name], field["type"])
        except ContractError as exc:
            raise ContractError(f"field {name!r}: {exc}") from None
    return out


def window_start(ts, window_size):
    """Start of the tumbling window containing ts."""
    if not isinstance(window_size, int) or isinstance(window_size, bool) or window_size <= 0:
        raise ValueError(f"window_size {window_size!r} must be a positive integer")
    return (ts // window_size) * window_size


def batch_aggregate(records, contract, window_size):
    """Deduplicate, validate and bucket a whole batch into tumbling windows."""
    window_start(0, window_size)          # validates window_size once, up front
    key_field = contract["key"]
    time_field = contract["event_time"]
    seen = {}
    dead_letter = []
    duplicates = 0
    for raw in records:
        try:
            clean = validate(raw, contract)
        except ContractError as exc:
            dead_letter.append({"raw": raw, "reason": str(exc)})
            continue
        key = clean[key_field]
        if key in seen:
            duplicates += 1               # first occurrence wins, as in the stream
            continue
        seen[key] = clean
    windows = {}
    for clean in seen.values():
        start = window_start(clean[time_field], window_size)
        slot = windows.setdefault(start, {"count": 0, "sum": 0.0})
        slot["count"] += 1
        slot["sum"] += clean["value"]
    return {"windows": windows, "rows": list(seen.values()), "accepted": len(seen),
            "duplicates": duplicates, "dead_letter": dead_letter}


class StreamPipeline:
    """The same aggregation, one record at a time, driven by a watermark."""

    def __init__(self, contract, window_size, allowed_lateness=0):
        window_start(0, window_size)
        if (not isinstance(allowed_lateness, int) or isinstance(allowed_lateness, bool)
                or allowed_lateness < 0):
            raise ValueError(f"allowed_lateness {allowed_lateness!r} must be non-negative")
        self.contract = contract
        self.window_size = window_size
        self.allowed_lateness = allowed_lateness
        self.results = {}
        self.closed = set()
        self.seen_keys = set()
        self.dead_letter = []
        self.duplicates = 0
        self.late_dropped = 0
        self.accepted = 0
        self.max_ts = None
        self.watermark = None

    def push(self, record):
        """Absorb one record; return the windows this record closed."""
        try:
            clean = validate(record, self.contract)
        except ContractError as exc:
            self.dead_letter.append({"raw": record, "reason": str(exc)})
            return []
        ts = clean[self.contract["event_time"]]
        if self.max_ts is None or ts > self.max_ts:
            self.max_ts = ts
        self.watermark = self.max_ts - self.allowed_lateness

        key = clean[self.contract["key"]]
        if key in self.seen_keys:
            self.duplicates += 1
            return self.emit_ready()
        self.seen_keys.add(key)

        start = window_start(ts, self.window_size)
        if start in self.closed:
            self.late_dropped += 1        # its window has already been reported
            return self.emit_ready()
        slot = self.results.setdefault(start, {"count": 0, "sum": 0.0})
        slot["count"] += 1
        slot["sum"] += clean["value"]
        self.accepted += 1
        return self.emit_ready()

    def emit_ready(self):
        """Close and return every window the watermark has passed."""
        if self.watermark is None:
            return []
        out = []
        for start in sorted(self.results):
            if start in self.closed:
                continue
            if start + self.window_size <= self.watermark:
                self.closed.add(start)
                out.append(self._result(start))
        return out

    def close(self):
        """Close and return everything still open, ascending."""
        out = []
        for start in sorted(self.results):
            if start in self.closed:
                continue
            self.closed.add(start)
            out.append(self._result(start))
        return out

    def _result(self, start):
        slot = self.results[start]
        return {"start": start, "end": start + self.window_size,
                "count": slot["count"], "sum": slot["sum"]}


def quality_report(rows, rules):
    """Run data-quality rules over the accepted rows."""
    checks = []
    for rule in rules:
        kind = rule["kind"]
        column = rule["column"]
        if kind == "not_null":
            failed = sum(1 for row in rows if row.get(column) is None)
        elif kind == "range":
            low, high = rule["min"], rule["max"]
            failed = sum(1 for row in rows if not low <= row[column] <= high)
        elif kind == "unique":
            counts = {}
            for row in rows:
                counts[row[column]] = counts.get(row[column], 0) + 1
            failed = sum(count - 1 for count in counts.values() if count > 1)
        else:
            raise ValueError(f"unknown quality rule {kind!r}")
        checks.append({"rule": rule.get("name", kind), "column": column,
                       "failed": failed, "passed": failed == 0})
    return {"passed": all(check["passed"] for check in checks), "checks": checks}


def lineage(source, contract, stats):
    """Lineage metadata with a deterministic fingerprint."""
    payload = {"source": source, "contract": contract["name"],
               "version": contract["version"], "stats": stats}
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return {"source": source,
            "contract_name": contract["name"],
            "contract_version": contract["version"],
            "stats": dict(stats),
            "fingerprint": hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]}


def reconcile(batch_windows, stream_windows, tolerance=1e-9):
    """Compare two window dicts and describe every disagreement."""
    starts = sorted(set(batch_windows) | set(stream_windows))
    only_batch = []
    only_stream = []
    differences = []
    for start in starts:
        left = batch_windows.get(start)
        right = stream_windows.get(start)
        if right is None:
            only_batch.append(start)
        elif left is None:
            only_stream.append(start)
        elif left["count"] != right["count"] or abs(left["sum"] - right["sum"]) > tolerance:
            differences.append({"window": start, "batch": dict(left), "stream": dict(right)})
    return {"matched": not (only_batch or only_stream or differences),
            "windows_compared": len(starts),
            "only_in_batch": only_batch,
            "only_in_stream": only_stream,
            "differences": differences}


def render_report(recon, meta):
    """A human-readable reconciliation report."""
    lines = [
        f"reconciliation  {meta['contract_name']} v{meta['contract_version']}",
        f"source          {meta['source']}",
        f"fingerprint     {meta['fingerprint']}",
        f"windows         {recon['windows_compared']}",
        f"status          {'MATCH' if recon['matched'] else 'MISMATCH'}",
    ]
    for start in recon["only_in_batch"]:
        lines.append(f"  window {start}: present in batch only")
    for start in recon["only_in_stream"]:
        lines.append(f"  window {start}: present in stream only")
    for diff in recon["differences"]:
        lines.append(
            f"  window {diff['window']}: batch count={diff['batch']['count']} "
            f"sum={diff['batch']['sum']:.3f} | stream count={diff['stream']['count']} "
            f"sum={diff['stream']['sum']:.3f}"
        )
    return "\n".join(lines)
'''},
            {"name": "main.py", "content": r'''
from pipeline import (CONTRACT, StreamPipeline, batch_aggregate, lineage,
                      quality_report, reconcile, render_report)

WINDOW = 10

RECORDS = [
    {"reading_id": "a", "sensor": "s1", "ts": 1, "value": 1.0},
    {"reading_id": "b", "sensor": "s1", "ts": 4, "value": "2.0"},
    {"reading_id": "c", "sensor": "s2", "ts": 11, "value": 3.0},
    {"reading_id": "d", "sensor": "s2", "ts": 7, "value": 4.0},
    {"reading_id": "e", "sensor": "s1", "ts": 15, "value": 5.0},
    {"reading_id": "a", "sensor": "s1", "ts": 1, "value": 1.0},
    {"reading_id": "f", "sensor": "", "ts": 3, "value": 9.0},
]

RULES = [
    {"kind": "not_null", "column": "sensor"},
    {"kind": "unique", "column": "reading_id"},
    {"kind": "range", "column": "value", "min": -50.0, "max": 100.0},
]

batch = batch_aggregate(RECORDS, CONTRACT, WINDOW)
print("quality:", quality_report(batch["rows"], RULES)["passed"])
print("rejects:", [entry["reason"] for entry in batch["dead_letter"]])

for lateness in (0, 5):
    stream = StreamPipeline(CONTRACT, WINDOW, allowed_lateness=lateness)
    for record in RECORDS:
        stream.push(record)
    stream.close()
    recon = reconcile(batch["windows"], stream.results)
    meta = lineage(f"feed:lateness={lateness}", CONTRACT,
                   {"batch_accepted": batch["accepted"], "stream_accepted": stream.accepted,
                    "late_dropped": stream.late_dropped})
    print(render_report(recon, meta))
'''},
        ],
        "tests": [
            {"name": "coerce enforces the contract types", "code": r'''
from pipeline import ContractError, coerce
assert coerce(" 42 ", "int") == 42, f'coerce(" 42 ","int") gave {coerce(" 42 ", "int")!r}'
assert coerce(3.0, "int") == 3, "an integral float is a valid int"
assert coerce("2.0", "float") == 2.0 and isinstance(coerce("2.0", "float"), float)
assert coerce(7, "float") == 7.0, "an int widens to float"
assert coerce("  s1 ", "str") == "s1", "strings are stripped"
assert coerce(12, "str") == "12", "numbers render as strings"
for _value, _type in [(None, "int"), ("", "str"), ("   ", "str"), (True, "int"),
                      (True, "str"), (3.5, "int"), ("abc", "float"), (1, "bool")]:
    try:
        coerce(_value, _type)
        assert False, f"coerce({_value!r}, {_type!r}) should raise ContractError"
    except ContractError:
        pass
'''},
            {"name": "validate projects, coerces and names its rejects", "code": r'''
from pipeline import CONTRACT, ContractError, validate
_got = validate({"reading_id": "a", "sensor": " s1 ", "ts": "4", "value": "2.5", "junk": 1}, CONTRACT)
assert _got == {"reading_id": "a", "sensor": "s1", "ts": 4, "value": 2.5}, f"Got {_got!r}"
assert "junk" not in _got, "fields outside the contract must be dropped"
for _bad, _field in [({"reading_id": "a", "sensor": "s1", "ts": 1}, "value"),
                     ({"reading_id": "a", "sensor": "", "ts": 1, "value": 1.0}, "sensor"),
                     ({"reading_id": "a", "sensor": "s1", "ts": "x", "value": 1.0}, "ts")]:
    try:
        validate(_bad, CONTRACT)
        assert False, f"validate({_bad!r}) should raise ContractError"
    except ContractError as _exc:
        assert _field in str(_exc), f"reason {str(_exc)!r} should name {_field!r}"
try:
    validate(["not", "a", "record"], CONTRACT)
    assert False, "a non-mapping record should raise ContractError"
except ContractError:
    pass
'''},
            {"name": "batch_aggregate dedupes, buckets and dead-letters", "code": r'''
from pipeline import CONTRACT, batch_aggregate
_recs = [
    {"reading_id": "a", "sensor": "s1", "ts": 1, "value": 1.0},
    {"reading_id": "b", "sensor": "s1", "ts": 4, "value": 2.0},
    {"reading_id": "c", "sensor": "s2", "ts": 11, "value": 3.0},
    {"reading_id": "d", "sensor": "s2", "ts": 7, "value": 4.0},
    {"reading_id": "e", "sensor": "s1", "ts": 15, "value": 5.0},
    {"reading_id": "a", "sensor": "s1", "ts": 1, "value": 99.0},
    {"reading_id": "f", "sensor": "", "ts": 3, "value": 9.0},
]
_b = batch_aggregate(_recs, CONTRACT, 10)
assert _b["windows"] == {0: {"count": 3, "sum": 7.0}, 10: {"count": 2, "sum": 8.0}}, \
    f"Got {_b['windows']!r}"
assert _b["accepted"] == 5 and _b["duplicates"] == 1, f"Got {_b['accepted']!r}/{_b['duplicates']!r}"
assert len(_b["dead_letter"]) == 1 and "sensor" in _b["dead_letter"][0]["reason"], \
    f"Got {_b['dead_letter']!r}"
assert _b["dead_letter"][0]["raw"] is _recs[-1], "the dead letter keeps the raw payload"
_empty = batch_aggregate([], CONTRACT, 10)
assert _empty["windows"] == {} and _empty["accepted"] == 0, f"Got {_empty!r}"
try:
    batch_aggregate(_recs, CONTRACT, 0)
    assert False, "a non-positive window_size should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "StreamPipeline emits on the watermark", "code": r'''
from pipeline import CONTRACT, StreamPipeline
_s = StreamPipeline(CONTRACT, 10)
assert _s.push({"reading_id": "a", "sensor": "s1", "ts": 1, "value": 1.0}) == [], \
    "watermark 1 closes nothing"
assert _s.push({"reading_id": "b", "sensor": "s1", "ts": 4, "value": 2.0}) == []
_emitted = _s.push({"reading_id": "c", "sensor": "s2", "ts": 11, "value": 3.0})
assert _emitted == [{"start": 0, "end": 10, "count": 2, "sum": 3.0}], f"Got {_emitted!r}"
assert _s.watermark == 11, f"watermark is {_s.watermark!r}, expected 11"
assert _s.close() == [{"start": 10, "end": 20, "count": 1, "sum": 3.0}], "close drains the tail"
assert _s.close() == [], "a second close has nothing left"
_other = StreamPipeline(CONTRACT, 10)
assert _other.results == {} and _other.accepted == 0, "two pipelines must not share state"
'''},
            {"name": "Generous lateness reconciles the two paths exactly", "code": r'''
from pipeline import CONTRACT, StreamPipeline, batch_aggregate, reconcile
_recs = [
    {"reading_id": "a", "sensor": "s1", "ts": 1, "value": 1.0},
    {"reading_id": "b", "sensor": "s1", "ts": 4, "value": 2.0},
    {"reading_id": "c", "sensor": "s2", "ts": 11, "value": 3.0},
    {"reading_id": "d", "sensor": "s2", "ts": 7, "value": 4.0},
    {"reading_id": "e", "sensor": "s1", "ts": 15, "value": 5.0},
]
_b = batch_aggregate(_recs, CONTRACT, 10)
_s = StreamPipeline(CONTRACT, 10, allowed_lateness=5)
for _r in _recs:
    _s.push(_r)
_s.close()
assert _s.late_dropped == 0, f"late_dropped is {_s.late_dropped!r}; the budget covers ts=7"
_recon = reconcile(_b["windows"], _s.results)
assert _recon["matched"] is True, f"paths disagreed: {_recon!r}"
assert _recon["windows_compared"] == 2 and _recon["differences"] == [], f"Got {_recon!r}"
'''},
            {"name": "Zero lateness makes the paths disagree, and says how", "code": r'''
from pipeline import CONTRACT, StreamPipeline, batch_aggregate, reconcile
_recs = [
    {"reading_id": "a", "sensor": "s1", "ts": 1, "value": 1.0},
    {"reading_id": "b", "sensor": "s1", "ts": 4, "value": 2.0},
    {"reading_id": "c", "sensor": "s2", "ts": 11, "value": 3.0},
    {"reading_id": "d", "sensor": "s2", "ts": 7, "value": 4.0},
    {"reading_id": "e", "sensor": "s1", "ts": 15, "value": 5.0},
]
_b = batch_aggregate(_recs, CONTRACT, 10)
_s = StreamPipeline(CONTRACT, 10, allowed_lateness=0)
for _r in _recs:
    _s.push(_r)
_s.close()
assert _s.late_dropped == 1, f"late_dropped is {_s.late_dropped!r}, expected 1 (ts=7 arrives too late)"
_recon = reconcile(_b["windows"], _s.results)
assert _recon["matched"] is False, "dropping a late event must show up as a mismatch"
assert len(_recon["differences"]) == 1, f"Got {_recon['differences']!r}"
_diff = _recon["differences"][0]
assert _diff["window"] == 0, f"the divergence is in window 0, report said {_diff['window']!r}"
assert _diff["batch"]["count"] == 3 and _diff["stream"]["count"] == 2, f"Got {_diff!r}"
'''},
            {"name": "reconcile reports one-sided windows", "code": r'''
from pipeline import reconcile
_r = reconcile({0: {"count": 1, "sum": 1.0}, 10: {"count": 1, "sum": 2.0}},
               {10: {"count": 1, "sum": 2.0}, 20: {"count": 1, "sum": 3.0}})
assert _r["only_in_batch"] == [0], f"Got {_r['only_in_batch']!r}"
assert _r["only_in_stream"] == [20], f"Got {_r['only_in_stream']!r}"
assert _r["matched"] is False and _r["windows_compared"] == 3, f"Got {_r!r}"
assert reconcile({}, {})["matched"] is True, "two empty results agree"
_tol = reconcile({0: {"count": 1, "sum": 1.0}}, {0: {"count": 1, "sum": 1.0 + 1e-12}})
assert _tol["matched"] is True, "a difference below the tolerance is not a difference"
'''},
            {"name": "quality_report runs the three rule kinds", "code": r'''
from pipeline import quality_report
_rows = [{"sensor": "s1", "reading_id": "a", "value": 1.0},
         {"sensor": None, "reading_id": "a", "value": 500.0}]
_q = quality_report(_rows, [{"kind": "not_null", "column": "sensor"},
                            {"kind": "unique", "column": "reading_id"},
                            {"kind": "range", "column": "value", "min": -50.0, "max": 100.0}])
assert _q["passed"] is False, "every rule fails on this input"
assert [c["failed"] for c in _q["checks"]] == [1, 1, 1], f"Got {_q['checks']!r}"
_clean = quality_report([{"sensor": "s1", "reading_id": "a", "value": 1.0}],
                        [{"kind": "not_null", "column": "sensor"}])
assert _clean["passed"] is True and _clean["checks"][0]["failed"] == 0, f"Got {_clean!r}"
assert quality_report([], [{"kind": "unique", "column": "reading_id"}])["passed"] is True, \
    "no rows means nothing to violate"
try:
    quality_report(_rows, [{"kind": "no_nulls_please", "column": "sensor"}])
    assert False, "an unknown rule kind should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "lineage fingerprints are deterministic", "code": r'''
from pipeline import CONTRACT, lineage
_a = lineage("feed:one", CONTRACT, {"accepted": 5, "rejected": 1})
_b = lineage("feed:one", CONTRACT, {"rejected": 1, "accepted": 5})
assert _a["fingerprint"] == _b["fingerprint"], "key order must not change the fingerprint"
assert len(_a["fingerprint"]) == 16, f"fingerprint is {_a['fingerprint']!r}, expected 16 hex chars"
assert _a["contract_name"] == "sensor_readings" and _a["contract_version"] == "1.2.0", f"Got {_a!r}"
assert _a["stats"] == {"accepted": 5, "rejected": 1}, f"Got {_a['stats']!r}"
_c = lineage("feed:one", CONTRACT, {"accepted": 6, "rejected": 1})
assert _a["fingerprint"] != _c["fingerprint"], "different counts must give a different fingerprint"
_d = lineage("feed:two", CONTRACT, {"accepted": 5, "rejected": 1})
assert _a["fingerprint"] != _d["fingerprint"], "a different source must give a different fingerprint"
'''},
            {"name": "render_report states the verdict", "code": r'''
from pipeline import CONTRACT, lineage, reconcile, render_report
_meta = lineage("feed:one", CONTRACT, {"accepted": 5})
_ok = render_report(reconcile({0: {"count": 1, "sum": 1.0}}, {0: {"count": 1, "sum": 1.0}}), _meta)
assert isinstance(_ok, str) and "MATCH" in _ok and "MISMATCH" not in _ok, f"Got {_ok!r}"
assert _meta["fingerprint"] in _ok, "the report must carry the lineage fingerprint"
_bad = render_report(reconcile({0: {"count": 3, "sum": 7.0}}, {0: {"count": 2, "sum": 3.0}}), _meta)
assert "MISMATCH" in _bad, f"Got {_bad!r}"
assert "window 0" in _bad, f"the report should name the diverging window: {_bad!r}"
assert len(_bad.strip().split("\n")) >= 6, f"expected a header plus the difference line: {_bad!r}"
'''},
            {"name": "pipeline.py is import-clean", "code": r'''
_src = open("pipeline.py").read()
assert "print(" not in _src, "pipeline.py defines the library; the printing belongs in main.py"
assert "import time" not in _src, "every window decision comes from event time, not the clock"
'''},
        ],
    },
}
