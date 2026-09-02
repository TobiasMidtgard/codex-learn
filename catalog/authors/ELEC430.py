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
            "read": [
                {
                    "title": "The contract at the door, and a replay that changes nothing",
                    "minutes": 12,
                    "body": r'''
At three in the morning a nightly load of forty thousand weather readings fails, and
the on-call message says only `ValueError: invalid literal for int() with base 10:
'three'`. One row, somewhere in the file, has the word `three` where a station id
should be. Thirty-nine thousand nine hundred and ninety-nine good rows are sitting in a
temporary table that the failed job rolled back, the morning dashboards are empty, and
the person who was paged has to find one bad line in a file too big to open in an
editor. Nothing about the data was unusual. The upstream feed had always been allowed
to send whatever it liked, and one night it did.

Every mechanism in this module is a response to that night. The store needs to say
what it will accept; one bad row needs to cost one bad row rather than the batch; the
reject needs to be kept somewhere with a reason a tired person can read; and, because
the fix for a failed load is to run it again, running it again has to be safe.

## What arrives is text

A CSV field is a string. So is a JSON number once it has been through a system that
quoted it, and so is anything typed into a form. The record
`{"id": "1", "city": " Oslo ", "temp_c": "3.5"}` carries three strings, and the store
wants an integer, a stripped name and a float. Turning `"3.5"` into `3.5` is
**coercion**; deciding that `"three"` cannot become an integer at all is
**validation**; the two are one function that either returns a value or explains why
it cannot. The explanation is the part people skimp on, and it is the part that gets
read at 03:00.

The declaration the function works from is a **schema**: for each field, a name, a
type, whether it is required, and a default for when it is optional and absent. That
is a contract between the feed and the store. The store promises that everything past
this point has these fields with these types; the feed is held to it, row by row.

Three rules come out of asking what the corner cases should do, and each one is a real
incident. First: `None` satisfies no type. A null is not a zero, an empty string or
`False`; it is the absence of a value, and letting it through as any of those is how a
column of temperatures acquires a silent zero. Second: strings are stripped before
coercion, because `" 42 "` is what a hand-edited spreadsheet exports and refusing it
teaches nobody anything. Third, and the one that surprises people:

```python
print(isinstance(True, int), True + True, int(True) * 100)
```

That prints `True 2 100`. In Python a `bool` *is* an `int`, so `int(True)` is `1` and
`True + True` is `2`. A coercer that checks `isinstance(value, int)` first will accept
`True` as a perfectly good integer id, and a `verified` flag pasted into the wrong
column becomes station 1. The rule is that a `bool` satisfies only the `bool` type,
and the check for it has to come *before* the integer check, because after it the
integer check has already said yes.

## A coercer that refuses well

Here is the integer branch on its own, with the rules in the order they must run:

```python
class SchemaError(ValueError):
    pass


def coerce_int(value):
    if value is None:
        raise SchemaError("value is null")
    if isinstance(value, bool):
        raise SchemaError("a bool does not satisfy type 'int'")
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


for raw in [" 42 ", 3.0, "three", True]:
    try:
        print(repr(raw), "->", coerce_int(raw))
    except SchemaError as exc:
        print(repr(raw), "-> SchemaError:", exc)
```

The four lines it prints are the shape of the whole function: `' 42 ' -> 42`, then
`3.0 -> 3`, then `'three' -> SchemaError: 'three' is not an int` and finally
`True -> SchemaError: a bool does not satisfy type 'int'`. The `from None` on the
re-raise matters more than it looks. Without it the traceback carries the original
`ValueError` chained underneath, and the person reading the dead-letter queue gets two
exceptions for one fact. The caller wants one kind of thing to catch, and
`SchemaError` is it.

`3.0 -> 3` is a judgement call worth noticing. An integral float is accepted because
it is what a JSON encoder emits for a whole number that passed through a float column
somewhere upstream; `3.5` is refused because there is no integer that it is. The
contract decides where that line goes, and writing the line down is what makes it a
contract.

## Fail closed on the record, not the batch

Once each field can be coerced or refused, the record-level function assembles exactly
the schema's fields. No more, because a field the schema does not name has no type and
cannot be trusted. No fewer, because a required field that is absent, `None` or the
empty string is a `SchemaError` whose message *names the field*. `field 'city':
missing` is something a person can act on; `KeyError: 'city'` three frames deep in a
loop is not.

The batch loop then does something different from the nightly job that failed: it
catches the `SchemaError` per record, appends `{"raw": record, "reason": str(error)}`
to a **dead-letter queue**, counts the reject, and moves on. The raw payload is kept
because the reason alone does not let anyone fix the row, and the reason is kept
because the payload alone does not say what was wrong with it. The good rows go in;
the bad rows go somewhere they can be inspected, replayed after a fix, or shown to the
upstream team as evidence. Forty thousand rows with one bad one is now thirty-nine
thousand nine hundred and ninety-nine rows in the store and one line in a queue.

## Running it again must be safe

The reason this cannot stop at validation is delivery. Feeds retry. A network blip
during acknowledgement means the sender never learned the batch arrived and sends it
again; a fixed job is re-run over the file it failed on; a queue consumer that crashed
after writing but before committing its offset re-reads the same messages.
**At-least-once** is the normal case — every message arrives one or more times — and
the only way to get the *effect* of exactly-once is to make the second arrival change
nothing. That property is **idempotency**, and the mechanism for it is an **upsert
keyed on a business key**: the record's own identity, the station id or the order
number, not a row number the store made up on arrival.

With a keyed store the three outcomes of a valid record are distinguishable, and
distinguishing them is what makes a replay auditable rather than merely harmless. The
key is unseen: store it, count an **accept**. The key is seen and the coerced record
equals what is stored: count a **duplicate** and touch nothing. The key is seen and the
record differs: overwrite and count an **update**. Note that the comparison is on the
*coerced* record. `" Oslo "` and `"Oslo"` are the same city once stripped, and
comparing the raw payloads would report an update where nothing changed.

## The batch, carried through

Take the four records the lab's `main.py` sends, and follow every counter:

```python
SCHEMA = [
    {"name": "id", "type": "int", "required": True},
    {"name": "city", "type": "str", "required": True},
    {"name": "temp_c", "type": "float", "required": True},
    {"name": "verified", "type": "bool", "required": False, "default": False},
]
TRUE_STRINGS = {"true", "t", "yes", "y", "1"}
FALSE_STRINGS = {"false", "f", "no", "n", "0"}


class SchemaError(ValueError):
    pass


def coerce(value, type_name):
    if value is None:
        raise SchemaError("null")
    if isinstance(value, bool) and type_name != "bool":
        raise SchemaError("a bool is not a " + type_name)
    if type_name == "int":
        if isinstance(value, float) and value != int(value):
            raise SchemaError(f"{value!r} is not whole")
        try:
            return int(str(value).strip())
        except ValueError:
            raise SchemaError(f"{value!r} is not an int") from None
    if type_name == "float":
        try:
            return float(str(value).strip())
        except ValueError:
            raise SchemaError(f"{value!r} is not a float") from None
    if type_name == "bool":
        text = str(value).strip().lower()
        if text in TRUE_STRINGS:
            return True
        if text in FALSE_STRINGS:
            return False
        raise SchemaError(f"{value!r} is not a bool")
    return str(value).strip()


def validate(record, schema):
    out = {}
    for field in schema:
        name = field["name"]
        raw = record.get(name)
        if raw is None or raw == "":
            if field["required"]:
                raise SchemaError(f"field {name!r}: missing")
            out[name] = field.get("default")
            continue
        try:
            out[name] = coerce(raw, field["type"])
        except SchemaError as exc:
            raise SchemaError(f"field {name!r}: {exc}") from None
    return out


def ingest(records, store, dead_letter):
    batch = {"accepted": 0, "updated": 0, "duplicate": 0, "rejected": 0}
    for raw in records:
        try:
            clean = validate(raw, SCHEMA)
        except SchemaError as exc:
            dead_letter.append({"raw": raw, "reason": str(exc)})
            batch["rejected"] += 1
            continue
        key = clean["id"]
        if key not in store:
            store[key] = clean
            batch["accepted"] += 1
        elif store[key] == clean:
            batch["duplicate"] += 1
        else:
            store[key] = clean
            batch["updated"] += 1
    return batch


BATCH = [
    {"id": "1", "city": " Oslo ", "temp_c": "3.5"},
    {"id": 2, "city": "Bergen", "temp_c": 7, "verified": "yes"},
    {"id": "three", "city": "Tromso", "temp_c": 1.0},
    {"id": 4, "city": "", "temp_c": 2.0},
]
store, dead = {}, []
print("first ", ingest(BATCH, store, dead))
print("replay", ingest(BATCH, store, dead))
print("update", ingest([{"id": 1, "city": "Oslo", "temp_c": 9.9}], store, dead))
print([entry["reason"] for entry in dead][:2])
```

The first pass prints `{'accepted': 2, 'updated': 0, 'duplicate': 0, 'rejected': 2}`.
Record 1 needed three coercions — `"1"` to `1`, `" Oslo "` to `"Oslo"`, `"3.5"` to
`3.5` — and took the default `False` for the absent `verified`. Record 2 had `"yes"`
coerced to `True`. Record 3 died on `field 'id': 'three' is not an int` and record 4
on `field 'city': missing`, since the empty string counts as absent and `city` is
required; the last line prints both reasons.

The replay prints `{'accepted': 0, 'updated': 0, 'duplicate': 2, 'rejected': 2}`: the
same two rejects go to the queue again, because a bad row is bad every time, and the
two good rows are recognised as already present, byte for byte. Nothing in the store
moved. The third batch changes station 1's temperature to 9.9 and prints one update.
Cumulative statistics, if the ingestor keeps them, are the sum of the three: two
accepted, one updated, two duplicates, four rejected.

## The mistake people make

The tempting shortcut is to make the store a list and the replay a `+= 1`.
`store.append(clean)` is one line, and it is correct for exactly one pass. On the
replay every row goes in a second time, every aggregate built on the store doubles,
and nobody notices for a week because the dashboards move in the right direction. The
reason it is tempting is that the first pass looks identical either way; idempotency
is a property of the *second* pass, and the second pass is the one nobody tests.

The other shortcut is coercing with `int(value)` and letting the exception propagate.
It is tempting because Python already refuses `"three"`. What it also does is accept
`True`, accept `3.7` — `int(3.7)` is `3`, silently — and raise a `ValueError` with no
field name in it, which are the three things the contract exists to stop.

## Where idempotency by upsert stops

An upsert keyed on identity gives last-write-wins, and it assumes the last write is
the newest. Replay a batch from Monday after Tuesday's batch has landed and Monday's
values overwrite Tuesday's: the operation is still idempotent — replay Monday twice
and the second time changes nothing — but it is not *ordered*. Stores that must
survive that carry a version or an event timestamp on the record and refuse to
overwrite a newer one, which is a rule this module leaves alone.

It also only helps for state that is one value per key. A running total is not:
`total += temp_c` on a replayed record double-counts even though the store underneath
deduplicated correctly. An aggregating path has to deduplicate on the key *before* it
adds, which is exactly the discipline the capstone's batch and stream paths share so
that they can be reconciled. And exactly-once across *two* systems — this store and a
downstream one — needs both to agree on the key and both to be idempotent; a keyed
store feeding an append-only log is at-least-once again on the far side.

## What you are about to build

The lab, *Schema-validating ingest with a dead-letter queue*, is the three layers
above in one file. `coerce_value` is the per-value contract with the three universal
rules in front of the type branches. `validate_record` assembles exactly the schema's
fields and names the field it rejects. `Ingestor.run` splits a batch into the four
counters, fills `self.dead_letter`, and — the test the others are in service of —
leaves `self.store` untouched when the same batch is run twice.
''',
                },
            ],
            "quiz": {
                "title": "Contracts, rejects and replays",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why does the coercer test `isinstance(value, bool)` before `isinstance(value, int)`, rather than after it?",
                        "opts": [
                            "Because a bool is an int in Python, so once the int branch has said yes there is nothing left to refuse",
                            "Because the bool branch is the one that handles the strings `\"yes\"` and `\"no\"`, and strings are checked first",
                            "Because `isinstance` matches the most recently defined type first, and bool was defined after int was",
                            "Because the int branch would convert `True` to the string `\"True\"`, which could then never become a number",
                        ],
                        "a": 0,
                        "whys": [
                            r"`isinstance(True, int)` is `True`; an int branch that runs first returns `True` as a valid id, and `True == 1` from then on.",
                            r"The bool branch does parse those strings, but a string fails `isinstance(value, int)` anyway, so order between the branches does not affect strings at all. The order matters for the value `True`, which passes both checks.",
                            r"`isinstance` has no notion of definition order; it answers whether the value's type is the named class or a subclass of it. `bool` subclasses `int`, so the int check says yes to `True` regardless of when either was defined.",
                            r"`int(True)` returns `1`, not a string. The int branch would accept the value, not mangle it, and that acceptance is exactly the defect the ordering prevents.",
                        ],
                        "why": r'''
`bool` is a subclass of `int`, so `isinstance(True, int)` is `True` and `int(True)` is
`1`. A coercer whose int branch runs first therefore accepts a flag pasted into the id
column as station 1 and never reaches the bool check. Testing for `bool` first and
refusing it for every type but `"bool"` is the only ordering that closes that door,
which is why the lab lists it among the universal rules that run before any type branch.
''',
                    },
                    {
                        "q": "One record in a batch of 40,000 carries `\"three\"` where an integer id should be. What does failing closed on the record, rather than on the batch, mean the ingest does?",
                        "opts": [
                            "Sends that record to the dead-letter queue with the field named in the reason, and stores the other 39,999",
                            "Rolls back the whole batch, so that the store never holds a partial load from a file that turned out to have a bad row",
                            "Coerces `\"three\"` to `None` for that one field and stores the record anyway, so that no row is ever lost",
                            "Stops at the bad record and keeps the rows before it, so the sender can re-transmit the tail of the file",
                        ],
                        "a": 0,
                        "whys": [
                            r"One bad row costs one bad row; the rest of the batch lands, and the reject keeps its raw payload and a reason someone can act on.",
                            r"That is failing closed on the batch, and it is the 03:00 page this module opens with: one bad line holds 39,999 good ones hostage and the dashboards are empty until a human finds it.",
                            r"`None` satisfies no type, and a required id that silently becomes `None` is worse than a reject: the bad record is now in the store with no key and no trace that it was ever wrong.",
                            r"Stopping part-way leaves the store half-loaded and the sender guessing where to resume; the point of per-record rejection is that the batch never has a position to resume from, because it finished.",
                        ],
                        "why": r'''
Failing closed means a bad record never enters the store; failing closed *on the
record* means the unit that fails is one row, not the batch. The `SchemaError` is caught
per record, `{"raw": record, "reason": str(error)}` goes to the dead-letter queue, the
`rejected` counter moves, and the loop continues. The other 39,999 rows are stored, and
the one bad row is somewhere a person can read, fix and replay.
''',
                    },
                    {
                        "q": "An identical batch is run twice. After the replay the counters show `updated: 2` where `duplicate: 2` was expected. Which is the likeliest cause?",
                        "opts": [
                            "The duplicate check compared the raw incoming record against the coerced stored one, so `\" Oslo \"` never equalled `\"Oslo\"`",
                            "The upsert was keyed on a row number the store assigned when the record arrived, so each replayed record looked new to the store",
                            "The dead-letter queue was not emptied between the two runs, so the rejects were counted a second time as updates",
                            "The store's watermark advanced past the batch during the first run, so every replayed record was treated as late",
                        ],
                        "a": 0,
                        "whys": [
                            r"Compare coerced with coerced: the stored record is stripped and typed, and the incoming one must be brought to the same form before the equality test means anything.",
                            r"A store-assigned key would make every replayed record *unseen*, which shows up as `accepted: 2`, not `updated: 2`. Updates need the key to be found and the payload to differ, which is what a raw-versus-coerced comparison produces.",
                            r"Rejects never reach the store, so they cannot be counted as updates; a replayed reject is counted as `rejected` again, and the dead-letter queue is meant to keep both copies.",
                            r"There is no watermark in an ingest step; that is a streaming mechanism for closing time windows. A replay of a keyed upsert has no notion of late.",
                        ],
                        "why": r'''
An update is recorded when the key is found and the record differs from what is
stored. On a replay the payloads are identical, so the only way they can differ is if
one side was coerced and the other was not: `" Oslo "` against `"Oslo"`, `"3.5"`
against `3.5`. Coerce first, then compare the coerced record with the stored one, and a
replay is two duplicates and no updates.
''',
                    },
                    {
                        "q": "A feed delivers every message at least once, and sometimes twice. What makes the store's contents the same as if each message had arrived exactly once?",
                        "opts": [
                            "An upsert keyed on the record's own business key, so a second arrival finds the first and changes nothing",
                            "A buffer that holds each batch in memory until the sender acknowledges the receipt, then writes it once",
                            "Asking the sender to retry only after a timeout long enough for the first copy to have been fully stored",
                            "A timestamp on each record, so the store keeps whichever copy arrived most recently and discards the rest",
                        ],
                        "a": 0,
                        "whys": [
                            r"Exactly-once as an effect is idempotency plus retries: the second copy is recognised by its key and counted as a duplicate.",
                            r"The sender's acknowledgement is the thing that gets lost; a buffer waiting for it will either wait forever or write on a retry, and the retry is the duplicate this is meant to absorb.",
                            r"A longer timeout changes how often duplicates happen, not whether they do, and a duplicate that arrives after the timeout is stored twice by a store that has no key to recognise it.",
                            r"Two copies of one message carry the same timestamp, and without a business key the store has nothing to say they are the same record; keeping the latest keeps both.",
                        ],
                        "why": r'''
At-least-once delivery cannot be turned off, because the acknowledgement that would let
the sender stop is itself a message that can be lost. What can be controlled is the
receiver: an upsert keyed on the record's identity makes the second arrival find the
first, compare equal after coercion, and be counted as a duplicate that touches
nothing. Idempotency plus retries is what exactly-once means in practice.
''',
                    },
                    {
                        "q": "Where does last-write-wins by keyed upsert stop being enough on its own?",
                        "opts": [
                            "When an older batch is replayed after a newer one has landed, since the replay overwrites current values with stale ones",
                            "When the batch holds more records than fit in memory at once, since the store can no longer compare every key",
                            "When two records share a business key but carry different values, since the store has no way to tell which of them is the duplicate",
                            "When the schema has an optional field with a default, since a defaulted value cannot be compared with a stored one",
                        ],
                        "a": 0,
                        "whys": [
                            r"The replay is still idempotent — run it twice and the second run changes nothing — but it is not ordered, and only a version or event timestamp on the record can refuse the stale write.",
                            r"A keyed store compares one incoming record with one stored record at a time; batch size does not enter into it, and a store that does not fit in memory is a different problem from an ordering one.",
                            r"That case is handled: same key, different payload is an *update*, and counting it as one is what makes the replay auditable. Neither record is a duplicate, and the store does not need to decide that.",
                            r"A default is applied at coercion time, so the coerced record carries a real value that compares like any other. Optional fields do not weaken the comparison at all.",
                        ],
                        "why": r'''
Last-write-wins assumes the last write is the newest, and a replay breaks that
assumption without breaking idempotency: replaying Monday's batch after Tuesday's
overwrites Tuesday's values, and replaying it again changes nothing further. A store
that must survive out-of-order replays carries a version or event timestamp per record
and refuses to overwrite a newer one; the plain upsert in this module does not.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "The bytes a scan must touch",
                    "minutes": 11,
                    "body": r'''
Five weather rows, three columns each: an integer `id`, the string `"oslo"`, and a
float `temp`. On disk, in the order a program would naturally write them, they look
like this under the size model this module uses — an `int` or a `float` costs 8 bytes,
a string costs its UTF-8 length plus a 1-byte length prefix, a `bool` or a `None`
costs 1:

```text
row 0:  [id 8][oslo 5][temp 8]    21 bytes
row 1:  [id 8][oslo 5][temp 8]    21 bytes
row 2:  [id 8][oslo 5][temp 8]    21 bytes
row 3:  [id 8][oslo 5][temp 8]    21 bytes
row 4:  [id 8][oslo 5][temp 8]    21 bytes
                                 105 bytes
```

Now ask for the average temperature. The query touches one column, but the
temperatures are 8-byte islands in a 21-byte row: to reach the second one you read
past the first row's id and city, and so on for all five. A reader that works at the
granularity of a row pulls all 105 bytes off the page to use 40 of them. That is
**row-major** storage, and it is the right layout for the question "give me everything
about row 3" — one contiguous read — and the wrong one for "give me one attribute of
every row".

Lay the same data out **column-major** — all five ids, then all five cities, then all
five temperatures — and the temperatures are 40 contiguous bytes. The scan reads 40
and stops. Nothing about the data changed; the access pattern was written into the
layout.

## The cost, derived from the picture

From that picture the cost of a scan falls out. For a row layout the projection does
not matter, because the reader takes whole tuples, so the cost is the sum of every
value in every row. For a columnar layout only the projected columns are read, so the
cost is the sum of those values' sizes across every row:

$$ \text{cost}_{\text{row}} = \sum_{r}\sum_{c \in \text{all}} \text{size}(r, c),
\qquad
\text{cost}_{\text{col}} = \sum_{r}\sum_{c \in \text{proj}} \text{size}(r, c) $$

```python
def value_size(value):
    if value is None or isinstance(value, bool):
        return 1
    if isinstance(value, (int, float)):
        return 8
    return len(value.encode("utf-8")) + 1


ROWS = [{"id": i, "city": "oslo", "temp": 1.0 * i} for i in range(5)]


def scan_cost(rows, projection, layout):
    if layout == "row":
        return sum(value_size(v) for row in rows for v in row.values())
    return sum(value_size(row[name]) for row in rows for name in projection)


print(scan_cost(ROWS, ["temp"], "row"), scan_cost(ROWS, ["temp"], "columnar"))
print(scan_cost(ROWS, ["id", "city", "temp"], "row"),
      scan_cost(ROWS, ["id", "city", "temp"], "columnar"))
```

The first line prints `105 40`: a selective scan reads 38% of the bytes under a
columnar layout. The second prints `105 105`, and that is as important as the first.
Project every column and the columnar advantage disappears — the same 105 bytes are
read, from three places instead of one. Analytical queries touch few columns and many
rows, which is why warehouses are columnar; a transactional system that reads and
writes whole records is not helped by the change.

## Runs

Once one attribute is stored contiguously, the values next to each other are of the
same kind, and they are frequently the same value. A column of `"red"` four times and
then `"blue"` four times need not store eight strings. Store each **run** once with a
count: `("red", 4), ("blue", 4)`. That is **run-length encoding**, and its cost is the
size of each run's value plus a header holding the count, per run:

$$ \text{rle} = \sum_{\text{runs}} \big(\text{size}(v) + H\big) $$

where $H$ is `RUN_HEADER_BYTES`, 4 here. Two runs cost $(4 + 4) + (5 + 4) = 17$ bytes
against a raw column of $4 \times 4 + 4 \times 5 = 36$. The **compression ratio** is
raw over encoded, $36 / 17 \approx 2.12$, and it is measured on the real column, not
estimated from the column's type.

## Codes

A different observation about the same column: it holds only two distinct values,
however many rows there are. Store each distinct value once in a **dictionary**, in
first-appearance order, and replace every cell with its index — a fixed-width code of
`CODE_BYTES`, 4 here. That is **dictionary encoding**:

$$ \text{dict} = \sum_{\text{distinct}} \text{size}(v) + C \cdot n $$

with $C$ the code width and $n$ the row count. For the same column the dictionary
`["red", "blue"]` costs $4 + 5 = 9$, eight codes cost $32$, total $41$ — *more* than
the raw 36. A four-byte code replacing a four-byte string saves nothing, and the
dictionary is pure overhead on top of that.

Here are both, with the raw size, on two columns:

```python
CODE_BYTES = 4
RUN_HEADER_BYTES = 4


def value_size(value):
    if value is None or isinstance(value, bool):
        return 1
    if isinstance(value, (int, float)):
        return 8
    return len(value.encode("utf-8")) + 1


def raw_size(values):
    return sum(value_size(v) for v in values)


def rle_size(values):
    runs = []
    for v in values:
        if runs and runs[-1][0] == v:
            runs[-1] = (v, runs[-1][1] + 1)
        else:
            runs.append((v, 1))
    return sum(value_size(v) + RUN_HEADER_BYTES for v, _ in runs)


def dict_size(values):
    distinct = list(dict.fromkeys(values))
    return sum(value_size(v) for v in distinct) + CODE_BYTES * len(values)


RUNS = ["red"] * 4 + ["blue"] * 4
LOWCARD = ["northbound", "southbound"] * 4
for name, column in [("RUNS", RUNS), ("LOWCARD", LOWCARD)]:
    print(name, raw_size(column), rle_size(column), dict_size(column))
```

`RUNS 36 17 41`: run-length wins on the sorted column. `LOWCARD 88 120 54`: the
column `["northbound", "southbound"] * 4` alternates every row, so it has eight runs
of one — each paying an 11-byte string plus a 4-byte header, 120 in all, worse than
raw — while the dictionary pays for two 11-byte strings once and then 4 bytes per row.
The winner is a property of the column, not of its type, and the lever for dictionary
coding is the **distinct count**: it wins when $C \cdot n + \text{dictionary} <
\text{raw}$, which for 11-byte strings is almost immediate and for 3-byte strings is
never.

## Sort order is the lever for runs

Run-length encoding does not care about the distinct count; it cares about
*adjacency*. Take eighty values, forty of each colour, shuffled:

```python
import random

random.seed(7)
CODE_BYTES = 4
RUN_HEADER_BYTES = 4


def rle_size(values):
    runs = []
    for v in values:
        if runs and runs[-1] == v:
            continue
        runs.append(v)
    return sum(len(v) + 1 + RUN_HEADER_BYTES for v in runs)


def dict_size(values):
    return sum(len(v) + 1 for v in set(values)) + CODE_BYTES * len(values)


shuffled = ["red"] * 40 + ["blue"] * 40
random.shuffle(shuffled)
sorted_column = sorted(shuffled)
print("shuffled", rle_size(shuffled), dict_size(shuffled))
print("sorted  ", rle_size(sorted_column), dict_size(sorted_column))
```

Shuffled, the column has around fifty runs and run-length coding costs 417 bytes
against a raw 360 — worse than doing nothing — while the dictionary holds at 329
whatever the order. Sort the column and the same eighty values become two runs and 17
bytes. The dictionary cost is unchanged at 329 because the distinct count is
unchanged. This is why a columnar store's sort key is a storage decision rather than a
presentation one: the column you sort by compresses dramatically, and the columns you
did not sort by are, from the encoder's point of view, shuffled.

## The mistake people make

The tempting rule is "strings get dictionary coded, numbers stay raw", because that is
the default a well-known file format applies and it is usually right. It is wrong on
the `RUNS` column by five bytes, and it is wrong on any column of short,
high-cardinality strings — a column of two-letter country codes with two hundred
distinct values pays 4 bytes a row for codes that replace 3-byte strings. The rule is
tempting because it can be applied without looking at the data, and the whole point of
this module is that the encoding is a cost decision made *per column, on the measured
column*. Three sizes, one comparison, ties broken toward the plainest encoding.

A second mistake is mechanical and Python-specific. In the size model a `bool` costs 1
byte and an `int` costs 8, and `isinstance(True, int)` is `True`. Test for `bool`
first, or every flag in the table is charged 8 bytes and every size below is wrong by
the number of flags.

## Where the model stops holding

The size model is a fiction chosen so the arithmetic can be checked by hand. Real
pages have alignment padding, per-page headers, null bitmaps and checksums; a 4-byte
code is usually bit-packed down to $\lceil \log_2 \text{distinct} \rceil$ bits, which
is why real dictionary coding wins on two-value columns where this model says it
loses. Decoding also costs processor time that the model prices at zero; a scan that
is bound by the processor rather than the disk can be slower on the smaller encoding.

The layout choice has its own edge. Columnar wins when the query touches few columns
and many rows. A point lookup — "everything about row 3" — has to reassemble the
tuple from three columns in three places, and an insert has to append to every column
file. Systems that need both keep a row-major write buffer in front of a columnar
store and pay the conversion in the background, which is a fair description of most
warehouses built in the last decade.

## What you are about to build

The lab, *Encodings and a selective-scan cost model*, has you write the size model,
the transposes `to_columnar` and `to_rows`, both codecs with their inverses and their
error cases, the three size functions under one `encoded_size` dispatcher, and
`best_encoding` choosing the cheapest with ties broken in `ENCODINGS` order.
`scan_cost` is the picture at the top of this reading as a function. The sanity check
in the brief is the arithmetic above: 36, 17 and 41 for the `RUNS` column, with
run-length winning and dictionary coding losing for the reason you now know.
''',
                },
            ],
            "quiz": {
                "title": "Layouts, runs and codes",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A table has five rows of `id` (8 bytes), `city` (5 bytes) and `temp` (8 bytes). A query needs only `temp`. Why does a row-major scan cost 105 bytes rather than 40?",
                        "opts": [
                            "The reader works in whole tuples, so reaching each temperature means reading past the id and the city beside it",
                            "The row layout stores no column boundaries, so the reader has no way to tell where each temperature begins",
                            "The row layout keeps a copy of every column inside every row, so the projection can only be applied after the whole read",
                            "Row-major pages are read in fixed 105-byte units, and five rows of 21 bytes happen to fill exactly one page",
                        ],
                        "a": 0,
                        "whys": [
                            r"The temperatures are 8-byte islands in 21-byte rows, and a row reader takes the whole row to get at the island.",
                            r"The boundaries are known — the size model gives every field a fixed or prefixed width — but knowing where a value starts does not make the bytes before it free; they sit on the same page and come off it together.",
                            r"Each row holds each column once, not a copy of the others. The projection is applied after the read, which is true, but the cost comes from the read taking every field, not from any duplication.",
                            r"There is no page size in the model; 105 is five rows times 21 bytes, and a row layout with fifty rows would cost 1050. The unit of reading is the tuple, not a page.",
                        ],
                        "why": r'''
In a row-major layout the fields of one row are contiguous, so the only way to read
the fifth row's temperature is to have read past the four rows before it, ids and
cities included. The scan cost for a row layout is therefore the sum of every value in
every row, 5 times 21, regardless of the projection. A column-major layout puts the
five temperatures side by side, and the same query reads 40 bytes.
''',
                    },
                    {
                        "q": "The column `[\"red\"] * 4 + [\"blue\"] * 4` costs 36 bytes raw, 17 run-length encoded and 41 dictionary encoded. Why does dictionary coding lose here?",
                        "opts": [
                            "The 4-byte code per row is no smaller than the strings it replaces, and the dictionary itself is added on top of that",
                            "Two distinct values are too few for a dictionary, which needs at least three entries before its header can pay for itself",
                            "The dictionary has to be sorted before it is stored, and sorting adds a header to every entry that it holds",
                            "Dictionary coding only compresses numeric columns, so the strings are stored inside it at their full raw size",
                        ],
                        "a": 0,
                        "whys": [
                            r"Eight codes at 4 bytes are 32, the dictionary is 9, and 41 is more than the 36 bytes of 3- and 4-character strings they stand in for.",
                            r"There is no minimum; a dictionary of two entries is fine when the codes are narrower than the values. `LOWCARD` has two distinct values and dictionary coding wins there by 34 bytes, because its strings are 11 bytes each.",
                            r"The dictionary is kept in first-appearance order and carries no per-entry header; its cost is the sizes of the distinct values, nothing more.",
                            r"Dictionary coding is used for strings more than anything else, and the strings are stored once each. It loses here because the codes cost as much as the values, not because the values are text.",
                        ],
                        "why": r'''
A dictionary code costs `CODE_BYTES`, 4, per row whatever the value was, and the
values here are 3 and 4 characters — 4 and 5 bytes under the model. Replacing them with
4-byte codes saves nothing per row, and the 9-byte dictionary is then pure overhead: 32
plus 9 is 41 against 36 raw. Dictionary coding wins when the values are wide and the
distinct count is low; run-length wins when equal values sit next to each other, which
is what this column has.
''',
                    },
                    {
                        "q": "The column `[\"northbound\", \"southbound\"] * 4` costs 88 bytes raw, 120 run-length encoded and 54 dictionary encoded. What makes run-length the worst of the three?",
                        "opts": [
                            "The values alternate on every row, so there are eight runs of length one, each paying a full value and a header",
                            "The strings are 11 bytes long, and a run-length header can only describe values of 8 bytes or fewer per run",
                            "There are only two distinct values, and run-length encoding needs many distinct values before it can begin to win",
                            "Run-length encoding stores each count as a string, and a count written out costs more than a dictionary code",
                        ],
                        "a": 0,
                        "whys": [
                            r"Eight runs of one is the raw column plus eight 4-byte headers: 88 plus 32 is 120.",
                            r"A run holds any value the size model can price; the 11-byte strings are stored once per run at 11 bytes. The trouble is that there are eight runs, not that the values are wide.",
                            r"Run-length encoding is indifferent to the distinct count; it cares whether equal values are adjacent. Sort this column and it becomes two runs at 30 bytes, with the same two distinct values.",
                            r"The count is a fixed 4-byte header, not text. What costs is paying that header eight times for runs that never get longer than one.",
                        ],
                        "why": r'''
Run-length encoding pays one value plus one header per run, so its cost depends on how
many runs there are, not on how many distinct values. An alternating column has as
many runs as rows, and every run adds a 4-byte header to a value that is stored in
full: 8 times 15 is 120. Dictionary coding pays for the two 11-byte strings once and
then 4 bytes a row, 22 plus 32. The lever for runs is sort order; the lever for codes
is distinct count.
''',
                    },
                    {
                        "q": "Eighty values, forty of each of two colours, are shuffled. Sorting the column takes its run-length size from 417 bytes to 17. What happens to its dictionary size?",
                        "opts": [
                            "It stays the same, because it depends on the distinct count and the row count and not on which values sit next to each other",
                            "It falls by about the same factor, because sorted values are stored as a range of codes instead of one code per row",
                            "It rises, because the dictionary must now record the sort order of the values alongside the distinct values that it already holds",
                            "It falls to two codes in total, because after sorting each distinct value appears in one contiguous block of rows",
                        ],
                        "a": 0,
                        "whys": [
                            r"Two distinct values and eighty rows before and after; the dictionary cost is 9 plus 320 either way.",
                            r"Dictionary coding writes one code per row and has no notion of a range; that is what run-length encoding does, and it is the one that fell to 17.",
                            r"The dictionary is in first-appearance order and stores nothing about the column's order; sorting changes which value appears first, not how many bytes the dictionary costs.",
                            r"A contiguous block of equal values is a run, and collapsing it into one entry is run-length encoding's trick. Dictionary coding still writes eighty codes.",
                        ],
                        "why": r'''
The dictionary cost is the size of the distinct values plus one fixed-width code per
row. Sorting changes neither the distinct count nor the row count, so the size is 329
before and after. Run-length encoding is the codec that reacts to adjacency, which is
why a column's sort order is the lever for runs and the distinct count is the lever
for codes; the two encodings answer to different properties of the same data.
''',
                    },
                    {
                        "q": "When does a column-major layout stop paying for itself?",
                        "opts": [
                            "When the query projects every column or fetches single rows, since a tuple is then reassembled from several places",
                            "When the table has more rows than fit in memory, since a single column can then no longer be read in one contiguous piece",
                            "When a column holds strings rather than numbers, since values of varying width cannot be stored contiguously",
                            "When the table has more than a handful of columns, since every extra column adds a separate seek for each row",
                        ],
                        "a": 0,
                        "whys": [
                            r"`scan_cost` with every column projected is 105 under both layouts, and a point lookup has to visit three column files for one row.",
                            r"A column that does not fit in memory is read in pieces, but each piece is still one attribute of many rows, which is exactly the access pattern a selective scan wants. Size does not remove the advantage.",
                            r"The size model prices strings with a length prefix precisely so that they can be laid end to end; `city` is stored contiguously in the lab's columnar layout and read at 5 bytes a row.",
                            r"More columns make the columnar advantage larger for a selective query, not smaller: a scan of one column out of fifty skips forty-nine. Seeks are per column read, not per row.",
                        ],
                        "why": r'''
A columnar layout wins when a query touches few columns and many rows, because it
reads only the projected columns. Project every column and it reads the same bytes as
the row layout from more places; fetch a single row and it has to reassemble the tuple
from one location per column, which a row layout gives in one contiguous read. Writes
have the same shape, one append per column file, which is why warehouses keep a
row-major buffer in front of the columnar store.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Deciding when a window is finished",
                    "minutes": 12,
                    "body": r'''
A fleet of delivery vans reports its position every second over a mobile link. The
link drops in tunnels and comes back in bursts, so the readings stamped 09:00:03 can
reach the server after the readings stamped 09:00:07, and a van that spent a minute
underground delivers sixty readings at once, all of them stale. The dashboard wants a
count of readings per five-second window. If the server groups readings by the time it
*received* them, the tunnel van contributes sixty readings to whatever window happens
to be open when it resurfaces, and the chart shows a spike that never happened. Run the
same log through the server tomorrow, when the network is quiet, and the chart is
different. Nothing is reproducible.

There are two clocks in that story, and the whole of stream processing is about
keeping them apart. **Event time** is the stamp the van wrote when the reading was
taken; it travels with the event and is the same however the network behaves.
**Processing time** is the wall clock at the server, and it is what a `time.time()` in
the aggregator would give you. Only event time gives an answer that is the same twice.
This module's aggregator never reads the wall clock at all: every decision is made
from the timestamps inside the events.

## Which windows an event belongs to

Partition the event-time axis into five-second slabs: $[0, 5)$, $[5, 10)$, $[10, 15)$
and so on. Each event falls into exactly one; these are **tumbling** windows. The slab
containing timestamp $t$ starts at the largest multiple of the size not above $t$:

$$ \text{start}(t) = \left\lfloor \frac{t}{\text{size}} \right\rfloor \cdot \text{size} $$

so `13 // 5 * 5` is `10`. The half-open interval is deliberate: `4` belongs to $[0, 5)$
and `5` opens $[5, 10)$, and no timestamp belongs to two.

A **sliding** window of size 4 and step 2 gives up that last property on purpose.
Windows start at every multiple of the step — $[0, 4)$, $[2, 6)$, $[4, 8)$ — so an
event at $t = 5$ sits in $[2, 6)$ and in $[4, 8)$, and is counted twice, once per
window. To list an event's windows, find the earliest start $s$ with $s + \text{size} >
t$ — the smallest multiple of the step strictly greater than $t - \text{size}$ — and
walk forward by the step while $s \le t$:

```python
def tumbling_start(ts, size):
    return (ts // size) * size


def window_starts(ts, size, step):
    first = max(0, ((ts - size) // step + 1) * step)
    return [s for s in range(first, ts + 1, step) if s <= ts < s + size]


print([tumbling_start(ts, 5) for ts in (0, 4, 5, 13)])
print(window_starts(12, 5, 5), window_starts(5, 4, 2), window_starts(1, 4, 2))
```

The first line prints `[0, 0, 5, 10]` for the tumbling starts of 0, 4, 5 and 13. The
second prints `[10]` — a sliding window whose step equals its size is a tumbling one —
then `[2, 4]` for $t = 5$, and `[0]` for $t = 1$, where the formula's first candidate
would be $-2$ and is clipped at zero. Note what the clip does to the count: an event at
the start of the stream lands in fewer windows than one in the middle. That is not a
bug, and it is one of the ways a sliding aggregate at the edge of a stream differs
from one in the interior.

## When is a window finished?

Here is the question the tunnel van forces. The window $[0, 5)$ has three readings in
it. Has the server seen all of them? It cannot know. A van might still be underground
with a reading stamped 3 in its buffer. If the server waits forever it never reports
anything; if it reports the moment the clock passes 5 it lies whenever a reading is
late.

The way out is to make a **claim** rather than wait for a fact. A **watermark** at
time $T$ is the aggregator asserting: no event with a timestamp before $T$ will arrive
from now on. Any window whose entire span lies before $T$ can be closed on the
strength of that claim — its aggregate emitted, its state freed. The window
$[s, s + \text{size})$ contains timestamps up to $s + \text{size} - 1$, so the claim
covers all of them exactly when

$$ s + \text{size} \le T $$

The comparison is $\le$, not $<$. With $T = 5$ the claim is "nothing before 5 will
arrive", which covers the event stamped 4, so $[0, 5)$ closes. With $T = 4$ an event
stamped 4 is still allowed, and $[0, 5)$ stays open. Getting that boundary wrong closes
every window one event late, or one event early, and both are wrong in a way that no
single test of a single window will show.

Where does $T$ come from? The plainest honest choice is the largest event time seen so
far, minus a budget for lateness the operator is prepared to tolerate:

$$ T = \max_{\text{seen}} t \; - \; \text{allowed\_lateness} $$

With a budget of zero, the moment a reading stamped 7 arrives the aggregator claims
that nothing before 7 is coming, and $[0, 5)$ closes. With a budget of 3 the claim
after that same reading is only "nothing before 4", and $[0, 5)$ waits until a reading
stamped 8 or later moves the claim to 5.

## A trace, event by event

Run the lab's opening example — tumbling windows of 5, no lateness budget, events at
0, 1, 4 and 7:

```python
class Windows:
    def __init__(self, size, allowed_lateness=0):
        self.size = size
        self.lateness = allowed_lateness
        self.max_ts = None
        self.open = {}
        self.closed = set()
        self.late_dropped = 0

    def push(self, ts, value):
        self.max_ts = ts if self.max_ts is None else max(self.max_ts, ts)
        watermark = self.max_ts - self.lateness
        start = (ts // self.size) * self.size
        if start in self.closed:
            self.late_dropped += 1
        else:
            slot = self.open.setdefault(start, {"count": 0, "sum": 0.0})
            slot["count"] += 1
            slot["sum"] += value
        emitted = []
        for s in sorted(self.open):
            if s not in self.closed and s + self.size <= watermark:
                self.closed.add(s)
                emitted.append((s, self.open[s]["count"], self.open[s]["sum"]))
        return emitted

    def flush(self):
        out = [(s, self.open[s]["count"], self.open[s]["sum"])
               for s in sorted(self.open) if s not in self.closed]
        self.closed.update(self.open)
        return out


agg = Windows(5)
for ts, value in [(0, 1.0), (1, 2.0), (4, 3.0), (7, 4.0)]:
    print(ts, "->", agg.push(ts, value))
print("flush:", agg.flush())
```

```text
0 -> []
1 -> []
4 -> []
7 -> [(0, 3, 6.0)]
flush: [(5, 1, 4.0)]
```

The first three pushes advance the watermark to 0, 1 and 4; none reaches 5, so nothing
closes. The push of 7 moves the watermark to 7, $0 + 5 \le 7$ holds, and $[0, 5)$ is
emitted with its count of 3 and sum of 6.0 — exactly once, because its start goes into
`closed` at the same moment. The reading at 7 itself opened $[5, 10)$, and nothing ever
arrives to move the watermark past 10, so that window would sit open forever.
`flush()` is the answer: close everything still open, in ascending order, and return
it. A flush is what turns an unbounded pipeline into a batch job that terminates, and a
stream that will never be flushed has to accept that its final window is never
reported.

## Late is a decision, not a property

Now the tunnel van. An event stamped 2 arrives after an event stamped 6, and the same
four events are run under two lateness budgets:

```python
class Windows:
    def __init__(self, size, allowed_lateness=0):
        self.size = size
        self.lateness = allowed_lateness
        self.max_ts = None
        self.open = {}
        self.closed = set()
        self.late_dropped = 0

    def push(self, ts, value):
        self.max_ts = ts if self.max_ts is None else max(self.max_ts, ts)
        watermark = self.max_ts - self.lateness
        start = (ts // self.size) * self.size
        if start in self.closed:
            self.late_dropped += 1
        else:
            slot = self.open.setdefault(start, {"count": 0, "sum": 0.0})
            slot["count"] += 1
            slot["sum"] += value
        emitted = []
        for s in sorted(self.open):
            if s not in self.closed and s + self.size <= watermark:
                self.closed.add(s)
                emitted.append((s, self.open[s]["count"], self.open[s]["sum"]))
        return emitted


EVENTS = [(1, 1.0), (6, 1.0), (2, 4.0), (9, 1.0)]
for lateness in (0, 3):
    agg = Windows(5, allowed_lateness=lateness)
    closed = [agg.push(ts, value) for ts, value in EVENTS]
    print(f"lateness={lateness}: closed {closed} late_dropped={agg.late_dropped}")
```

`lateness=0: closed [[], [(0, 1, 1.0)], [], []] late_dropped=1`. The reading at 1
opens $[0, 5)$; 6 moves the watermark to 6 and closes it with a count of 1; then 2
arrives, its window is in `closed`, and it is dropped. The window was reported with
the wrong count, and the aggregator has no way to take the report back.

`lateness=3: closed [[], [], [], [(0, 2, 5.0)]] late_dropped=0`. The same four events,
but the watermark after 6 is only 3, $[0, 5)$ is still open, the reading at 2 lands in
it, and the window closes with a count of 2 and a sum of 5.0 when 9 arrives and moves
the watermark to 6.

The same event, stamped 2, arriving in the same position, is late in one run and on
time in the other. Nothing about the event changed; the watermark's claim did.
**Late** means "arrived after its window was closed", and closing is the aggregator's
decision. **Out of order** is the ordinary condition of a network and, inside the
budget, costs nothing — the reading at 2 was out of order in both runs and was
aggregated in one of them.

The trade is now visible. A larger budget means fewer wrong reports and more state:
every open window is memory, and a budget of an hour on one-minute windows keeps sixty
windows live per key. A budget of zero means the least memory and the most drops.
There is no setting that is right for every feed, which is why it is a constructor
argument.

## The mistake people make

The tempting order inside `push` is: place the event, emit whatever is ready, *then*
update the watermark. It reads naturally — deal with this event, then note that time
has moved on. It closes every window one event late: the push of 7 leaves the
watermark at 4, nothing closes, and $[0, 5)$ is emitted on the *next* push, whatever
that is. Every test that checks "the push of 7 returns the closed window" fails, and
the fix is one line moved. The rule is: advance the watermark from the new maximum
first, then place, then emit.

The other is counting an event as late when *one* of its windows is closed. With
sliding windows an event at $t = 5$ belongs to $[2, 6)$ and $[4, 8)$; if $[2, 6)$ has
closed, the event still has a home in $[4, 8)$ and should land there. It is dropped,
and counted, only when every window it belongs to has closed.

## Where the watermark stops holding

The watermark is a heuristic dressed as a claim. `max_ts - lateness` is right whenever
the stream's disorder is bounded by `lateness`, and no stream promises that. A van
that is underground for ten minutes on a three-second budget produces ten minutes of
drops, and a single reading with a clock set to next year drags the watermark forward
and closes every window at once. Production systems derive the watermark per source
and take the minimum across sources, hold it back when a source goes quiet, and
sometimes emit a corrected result for a closed window — a retraction — which this
module's aggregator, having freed the state, cannot. The capstone measures the cost of
that limit directly: with a budget of zero and out-of-order input, the stream path and
the batch path disagree, and the reconciliation report says by how much.

## What you are about to build

The lab, *Windowed aggregation with watermarks*, is `tumbling_start` and
`window_starts` from the first section, then `WindowedAggregator.push` in the order
the mistake above describes — watermark, place, emit — with `emit_ready` closing every
window whose end is at or before the watermark and `flush` draining the rest.
`late_dropped` counts the events that had nowhere left to land. The trace above is the
first emission test; the sliding-window test counts $t = 10$ in both $[8, 12)$ and
$[10, 14)$, which is the second section's formula at work.
''',
                },
            ],
            "quiz": {
                "title": "Windows, watermarks and what counts as late",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Windows are 5 wide. Why does $[0, 5)$ close when the watermark reaches $T = 5$ but not when it reaches $T = 4$?",
                        "opts": [
                            "The window's last possible timestamp is 4, and a watermark of 5 claims that nothing before 5 will arrive, so 4 is covered",
                            "The window's end is 5, and a watermark equal to the end means an event stamped 5 has already arrived in the window",
                            "A watermark of 4 still sits inside the window, and a window may close only once the watermark has passed it by a whole size",
                            "A watermark of 5 is the processing time at which the fifth event arrived, and five events are what fill a window of size 5",
                        ],
                        "a": 0,
                        "whys": [
                            r"The claim at $T$ covers every timestamp below $T$; the window needs every timestamp below $s + \text{size}$ covered, so it closes when $s + \text{size} \le T$.",
                            r"An event stamped 5 belongs to $[5, 10)$, not to $[0, 5)$; the half-open interval keeps it out. What the watermark says about 5 is irrelevant to whether $[0, 5)$ is complete — what matters is the claim about 4.",
                            r"Waiting a whole extra window is a lateness budget in disguise, and it would close every window one full size late. The rule is $s + \text{size} \le T$, and at $T = 5$ that already holds for $s = 0$.",
                            r"The watermark is event time derived from the events' own stamps, never a wall clock and never a count. Five events at timestamps 0, 0, 0, 0 and 0 leave the watermark at 0 and the window open.",
                        ],
                        "why": r'''
A watermark at $T$ is the claim that no event with a timestamp before $T$ will arrive
again. The window $[0, 5)$ holds timestamps 0 through 4, so it is complete exactly when
that claim covers 4, which is when $T$ is at least 5. At $T = 4$ an event stamped 4 is
still allowed and the window stays open. The condition is $s + \text{size} \le T$, and
getting the boundary off by one closes every window an event early or an event late.
''',
                    },
                    {
                        "q": "An event stamped 2 arrives after one stamped 6. With `allowed_lateness=0` it is dropped; with `allowed_lateness=3` it is aggregated into $[0, 5)$. What does that show about lateness?",
                        "opts": [
                            "Late is a decision the watermark makes about a window it has closed, not a property the event carries with it",
                            "Late is a fixed property of the event, and the larger budget only postpones the moment at which the drop is recorded",
                            "An event is late whenever its stamp is below the largest stamp seen, and the budget hides the drop rather than preventing it",
                            "The budget of 3 rewrites the event's timestamp to 5, moving it into a window that has not yet been closed",
                        ],
                        "a": 0,
                        "whys": [
                            r"The same event in the same position was aggregated in one run and dropped in the other; the only thing that changed was when the aggregator chose to close the window.",
                            r"With the budget of 3 the event is never dropped at all: it lands in $[0, 5)$, and that window is emitted with a count of 2. Nothing is postponed; the report is different.",
                            r"That describes *out of order*, which is the normal condition of a network. The event stamped 2 was out of order in both runs and aggregated correctly in one of them; out of order costs nothing inside the budget.",
                            r"Timestamps are never rewritten; the event's stamp is 2 in both runs and it belongs to $[0, 5)$ in both. What the budget changes is the watermark, $6 - 3 = 3$, which is not yet past the window's end.",
                        ],
                        "why": r'''
Late means "arrived after its window was closed", and closing is the aggregator's
decision, made from the watermark. With a budget of zero the reading stamped 6 moves
the watermark to 6 and $[0, 5)$ is closed before 2 arrives; with a budget of 3 the
watermark is only 3, the window is open, and the same event lands. Out-of-order
arrival is a property of the network and is harmless inside the budget; lateness is a
consequence of the claim the watermark made.
''',
                    },
                    {
                        "q": "Inside `push`, an implementation places the event, emits every ready window, and only then advances the watermark from the new maximum timestamp. What goes wrong?",
                        "opts": [
                            "Every window closes one push late, because the emit step reads the watermark the previous event left behind",
                            "Nothing goes wrong for tumbling windows, but a sliding event can be placed into a window that has already closed",
                            "Every window closes one push early, because the event is placed before the watermark can refuse it",
                            "Windows are emitted twice, once before the watermark moves and once after, because the closed set is updated late",
                        ],
                        "a": 0,
                        "whys": [
                            r"The push of 7 emits against a watermark of 4, nothing closes, and $[0, 5)$ comes out on whatever push happens next.",
                            r"The order of the two steps has nothing to do with sliding windows, and a closed window is refused by the `closed` set regardless of when the watermark moves. Tumbling windows are affected exactly as much: every one of them is a push late.",
                            r"Delaying the watermark can only make the aggregator close *later*, never earlier: at the moment it emits, the watermark is still the old, smaller value.",
                            r"A window is added to `closed` when it is emitted and is skipped from then on, so it cannot be emitted twice however late the watermark moves. The defect is a delay, not a repeat.",
                        ],
                        "why": r'''
The emit step compares each window's end with the watermark, so it has to see the
watermark that the current event implies. Update it afterwards and the push of 7
compares against the watermark left by the event stamped 4; $[0, 5)$ is not yet
closable, and it is emitted on the next push instead, whatever that push is. Advance
the watermark from the new maximum first, then place the event, then emit; the fix is
one line moved.
''',
                    },
                    {
                        "q": "Sliding windows of size 4 and step 2. An event at $t = 5$ arrives after $[2, 6)$ has closed but while $[4, 8)$ is still open. What should happen to it?",
                        "opts": [
                            "It lands in $[4, 8)$ and is not counted as late, because an event is dropped only when every window it belongs to has closed",
                            "It is dropped and counted as late, because one of its windows has already been reported and that report cannot be corrected",
                            "It lands in $[4, 8)$, and $[2, 6)$ is reopened and emitted again with the corrected count, so that both windows end up right",
                            "It lands in $[4, 8)$ twice, once for itself and once to stand in for the contribution that $[2, 6)$ can no longer receive",
                        ],
                        "a": 0,
                        "whys": [
                            r"The event still has a home; `late_dropped` counts events that had nowhere left to land, and this one lands.",
                            r"The report for $[2, 6)$ is indeed wrong and cannot be corrected, but that is no reason to lose the event's contribution to $[4, 8)$ as well. Dropping it makes a second window wrong to punish the first.",
                            r"A closed window has been emitted exactly once and its start sits in `closed`; reopening it would emit it twice, which the lab forbids. A retraction is a real technique, but this aggregator has no way to express one.",
                            r"An event contributes once to each window it belongs to, never twice to the same one. Double-counting in $[4, 8)$ would make that window's count wrong too.",
                        ],
                        "why": r'''
A sliding event belongs to several windows, and each window is closed independently.
The event at $t = 5$ has $[2, 6)$ and $[4, 8)$; the first is closed and skipped, the
second is open and receives the event. Only when *every* window an event belongs to
is closed does it have nowhere to land, and only then is `late_dropped` incremented.
The already-emitted window stays as reported, because nothing is ever emitted twice.
''',
                    },
                    {
                        "q": "A stream stops arriving with $[5, 10)$ still holding data. Why does the aggregator need a `flush()` rather than waiting for the window to close?",
                        "opts": [
                            "The watermark advances only from event timestamps, so with no later event nothing can ever move it past the window's end",
                            "The watermark advances with the wall clock, and a window left open when the clock passes its end is reported as empty",
                            "An open window keeps accumulating state indefinitely, and the flush truncates it to the count seen so far to save memory",
                            "A flush recomputes every window from the raw events it has kept, which is the only way a final result can be trusted",
                        ],
                        "a": 0,
                        "whys": [
                            r"With no event past 10 the claim never reaches 10, so $[5, 10)$ would sit open forever; the flush closes it by decision rather than by claim.",
                            r"The aggregator never reads the wall clock — that is the whole reason its results are reproducible. Waiting on real time would give a different answer on every run.",
                            r"A window that receives no events accumulates nothing, and a flush changes no counts; it emits the windows as they stand and marks them closed.",
                            r"Raw events are not kept; each one is folded into its window's count and sum on arrival and then forgotten. The flush emits those aggregates, it does not recompute them.",
                        ],
                        "why": r'''
Every decision in the aggregator is driven by the watermark, and the watermark is
derived from the largest event time seen. When the stream ends, no event arrives to
move it, so a window whose end is beyond the last watermark can never close by the
ordinary rule. `flush()` closes everything still open, in ascending order, exactly
once. It is what turns an unbounded pipeline into a batch job that terminates.
''',
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Reading fewer cells, and paying for the join",
                    "minutes": 12,
                    "body": r'''
Five click events, four columns each — `event_id`, `user_id`, `kind`, `ms` — and the
question "which events were clicks?". Written as a plan, the plain answer is a tree
read from the bottom: scan the `events` table, keep the rows whose `kind` is
`"click"`, and hand back only `event_id`.

```text
project [event_id]
  filter kind = "click"
    scan events (all columns)
```

Count what that costs. The scan reads every cell of every row: 5 rows times 4
columns, 20 cells. Those 5 rows are materialised — built as dicts — and the filter
then looks at one cell of each to decide, 5 more, for 25 cells read. The projection
reads nothing new; it discards three of the four columns it was handed. Four rows
survive. That is 25 cells read to produce 4 numbers, and 15 of the 25 were columns
nobody asked about.

## Moving work down the tree

The plan is a tree and the executor is a set of operators, each of which takes rows
from its child and yields rows to its parent. A rewrite that produces a different tree
with the same result is an **optimisation**, and two rewrites account for most of the
saving there is to have.

**Predicate pushdown**: the filter tests `kind` on rows the scan has already fully
read. If the scan tested `kind` itself, row by row, before materialising anything, the
non-clicks would never be built at all. The predicate moves into the scan node.

**Projection pruning**: the scan reads all four columns because it was not told which
ones matter. The projection at the top says `event_id`; hand that list down to the
scan and it reads one column instead of four.

The two interact, and the interaction is the detail that catches people. The pushed
predicate tests `kind`, so the scan must read `kind` whether or not it is projected —
a column it cannot see it cannot test. The scan's column list becomes
`["event_id", "kind"]`: the projection's columns, plus every predicate column missing
from them. That list is wider than what the query asked for, so a **residual project**
stays on top to trim `kind` back off, and the result is identical to the plain plan's:

```text
project [event_id]
  scan events, columns [event_id, kind], predicate kind = "click"
```

Had the query asked for `event_id, kind` — a projection that already covers the
predicate — the scan's list would equal the projection, and the bare scan would be the
whole plan.

## The accounting, carried through

```python
EVENTS = [
    {"event_id": 1, "user_id": 10, "kind": "click", "ms": 120},
    {"event_id": 2, "user_id": 11, "kind": "view", "ms": 80},
    {"event_id": 3, "user_id": 10, "kind": "click", "ms": 300},
    {"event_id": 4, "user_id": 12, "kind": "click", "ms": 45},
    {"event_id": 5, "user_id": 11, "kind": "click", "ms": 210},
]


def scan(rows, columns, predicates, stats):
    out = []
    needed = set(columns or rows[0]) | {column for column, _, _ in predicates}
    for row in rows:
        stats["rows_scanned"] += 1
        stats["cells_read"] += len(needed)
        if all(row[column] == value for column, _, value in predicates):
            out.append({name: row[name] for name in (columns or row)})
    return out


def filter_rows(rows, predicate, stats):
    column, _, value = predicate
    stats["cells_read"] += len(rows)
    return [row for row in rows if row[column] == value]


plain = {"rows_scanned": 0, "cells_read": 0}
rows = scan(EVENTS, None, [], plain)
rows = filter_rows(rows, ("kind", "=", "click"), plain)
rows = [{"event_id": row["event_id"]} for row in rows]
print("plain    ", [r["event_id"] for r in rows], plain)

pushed = {"rows_scanned": 0, "cells_read": 0}
rows = scan(EVENTS, ["event_id", "kind"], [("kind", "=", "click")], pushed)
rows = [{"event_id": row["event_id"]} for row in rows]
print("optimised", [r["event_id"] for r in rows], pushed)
```

`plain     [1, 3, 4, 5] {'rows_scanned': 5, 'cells_read': 25}` and then
`optimised [1, 3, 4, 5] {'rows_scanned': 5, 'cells_read': 10}`. The same four event
ids either way — a rewrite that changes the answer is not an optimisation, it is a
bug — and the cells read fall from 25 to 10: 5 rows, 2 cells each, and no separate
filter pass because the scan tested `kind` as it went. `rows_scanned` stays at 5,
because nothing here is an index; the scan still visits every row. What changed is
how much of each row it touched, which is the columnar reading of the previous module
arriving as a query plan.

## Two ways to join

Now attach the users. Each event carries a `user_id`; a `users` table carries
`user_id` and `country`; the join pairs every event with the user row of the same key.
Two algorithms do this, and they cost differently.

**Hash join** builds a hash table on one input — the right, by convention here — keyed
on the join column, with a list per key because keys repeat. It then walks the other
input once, probing the table with each row's key and emitting one merged row per
partner found. Each row of each input is touched once:

$$ \text{cost}_{\text{hash}} = n + m $$

**Sort-merge join** sorts both inputs on the key, then walks them together with two
cursors: advance the side with the smaller key, and when the keys are equal find the
end of the equal-key group on *both* sides and emit every pair in the cross product
before moving both cursors past the group. The merge itself touches each row once; the
sorts are the price:

$$ \text{cost}_{\text{merge}} = n + m + n \log_2 n + m \log_2 m $$

with either sort term dropped when that input is already in key order. The cost
model, and the choice it drives:

```python
import math


def join_cost(n, m, algorithm, left_sorted=False, right_sorted=False):
    cost = float(n + m)
    if algorithm == "sort_merge":
        if not left_sorted and n > 1:
            cost += n * math.log2(n)
        if not right_sorted and m > 1:
            cost += m * math.log2(m)
    return cost


print(join_cost(100, 50, "hash"), round(join_cost(100, 50, "sort_merge"), 1))
print(join_cost(100, 50, "sort_merge", True, True))
print(round(join_cost(1_000_000, 1_000_000, "sort_merge") / join_cost(1_000_000, 1_000_000, "hash"), 1))
```

`150.0 1096.6`: with 100 events and 50 users, hashing costs 150 and sort-merge costs
1096.6, of which 946.6 is sorting. `150.0` again when both inputs are already sorted —
the sorts vanish and the two tie, and the tie goes to sort-merge because its output
comes out in key order for free, which the next operator up the tree may be able to
use. The last line, `20.9`, is the ratio at a million rows a side: the sorts are twenty
times the merge, and an unsorted sort-merge join is a poor choice at any size unless
the sort order is wanted for something else.

## Repeated keys

Two events for user 10 and, in some other table, two rows for user 10 — a user with
two addresses, say — must produce four joined rows. That is what a join means. Both
algorithms get it right only when written for it:

```python
def hash_join(left, right, key):
    index = {}
    for row in right:
        index.setdefault(row[key], []).append(row)
    return [{**row, **partner} for row in left for partner in index.get(row[key], ())]


def sort_merge_join(left, right, key):
    ls, rs = sorted(left, key=lambda r: r[key]), sorted(right, key=lambda r: r[key])
    out, i, j = [], 0, 0
    while i < len(ls) and j < len(rs):
        if ls[i][key] < rs[j][key]:
            i += 1
        elif ls[i][key] > rs[j][key]:
            j += 1
        else:
            k = ls[i][key]
            i_end = i
            while i_end < len(ls) and ls[i_end][key] == k:
                i_end += 1
            j_end = j
            while j_end < len(rs) and rs[j_end][key] == k:
                j_end += 1
            out.extend({**ls[a], **rs[b]} for a in range(i, i_end) for b in range(j, j_end))
            i, j = i_end, j_end
    return out


LEFT = [{"k": 1, "l": "a"}, {"k": 1, "l": "b"}, {"k": 2, "l": "c"}]
RIGHT = [{"k": 1, "r": "x"}, {"k": 1, "r": "y"}, {"k": 3, "r": "z"}]
h = hash_join(LEFT, RIGHT, "k")
m = sort_merge_join(LEFT, RIGHT, "k")
print(len(h), len(m), sorted(sorted(r.items()) for r in h) == sorted(sorted(r.items()) for r in m))
```

`4 4 True`: four rows from each, and the same four rows as multisets. The
`sorted(...) == sorted(...)` at the end is the comparison the lab's `same_rows` makes,
and it is a multiset comparison on purpose: the hash join emits in left order then
right order, the merge emits in key order, and both are correct. A test that compares
the two lists directly fails on order and says nothing about the join.

## The mistake people make

In the merge, on equal keys, the tempting move is to emit one pair and advance *one*
cursor. It is what the unequal-key branches do, so it reads as consistent. On the
2-by-2 group above it emits two rows instead of four — the cross product needs the
inner loop over the whole group on both sides, and the cursors must move past the
group together. The reason it is tempting is that on a key that repeats on only one
side the shortcut happens to work, and most test data has unique keys on at least one
side.

In the optimiser, the tempting shortcut is to set the scan's columns to the
projection's columns and stop. The scan then cannot evaluate the pushed predicate —
`kind` is not in the row it built — and either raises or, worse, is written to skip
predicates on columns it does not have. The pushed predicate pins its own column into
the scan; the residual project exists to take it back out.

## Where the model stops holding

The cost model counts rows touched and prices everything else at zero. A hash join's
table has to fit in memory; when it does not, the join spills partitions to disk and
its cost is nothing like $n + m$. Sort-merge degrades more gracefully under memory
pressure, which is one reason real planners keep it even though the model here almost
never picks it on unsorted inputs. Key skew — one user with a million events — makes
one hash bucket a list of a million rows, and the probe for that key is a long walk
the model does not see.

Pushdown has limits too. A predicate can move below a projection and below another
filter freely; it cannot move below an aggregate that computes the column it tests,
and pushing it below a join is valid only when it mentions columns from one side. This
module's plans are a straight chain of project and filter nodes over one scan, which
is exactly the case where every predicate can go all the way down.

## What you are about to build

The lab, *Pushdown, pruning and two join algorithms*, has `match` evaluating a
predicate against a row; `execute` walking the tree with one `stats` dict threaded
through it — the scan charging the union of its projected and predicate columns per
row, the filter charging one cell per row that reaches it, the project charging
nothing; and `optimise` rebuilding the chain as the pushed-down scan with its residual
project. `hash_join` and `sort_merge_join` must agree under `same_rows` on repeated
keys and on empty inputs, and `join_cost` with `choose_join` is the model above, ties
to sort-merge. The 25-to-10 figure is one of the tests.
''',
                },
            ],
            "quiz": {
                "title": "Pushdown, pruning and the price of a join",
                "minutes": 7,
                "questions": [
                    {
                        "q": "After optimisation, `project [event_id] / filter kind = \"click\" / scan` becomes a scan with columns `[\"event_id\", \"kind\"]` under a residual project. Why does `kind` stay in the scan when the query never returns it?",
                        "opts": [
                            "The scan now evaluates the pushed predicate itself, and it cannot test a column that it did not read",
                            "The scan always keeps the first two columns of the table so a residual project has something to trim",
                            "Pushdown copies the filter's column into the scan as a side effect, and the project on top exists to hide that copy",
                            "Every column named anywhere in the plan has to reach the output, so the project on top is a no-op that keeps `kind`",
                        ],
                        "a": 0,
                        "whys": [
                            r"A pushed predicate pins its own column into the scan; the residual project takes it back out so the result matches the plain plan.",
                            r"There is no such rule; the scan's list is the projection plus whatever the predicates need, in that order, and a query that projected `ms` would keep `ms` and `kind`, not the table's first two columns.",
                            r"It is not a side effect but the point: the scan reads `kind` because it must compare it with `\"click\"` for every row. The project on top is what makes the output identical to the unoptimised plan's, and it is only added when the scan's list is wider than the projection.",
                            r"The residual project narrows the output to `[event_id]`, so `kind` does not reach the output at all. A project is a rename of the visible columns, and here it drops one.",
                        ],
                        "why": r'''
Pushing the predicate into the scan moves the comparison `kind = "click"` to the
moment each row is read, and a comparison needs its column. The scan's column list is
therefore the projection's columns plus every predicate column missing from them,
`["event_id", "kind"]`. That list is wider than what was asked for, so one `project`
node stays on top to trim it. When the projection already covers the predicate column,
the lists match and the bare scan is the whole plan.
''',
                    },
                    {
                        "q": "The plain plan reads 25 cells and the optimised plan reads 10, yet `rows_scanned` is 5 in both. What does that pair of numbers tell you?",
                        "opts": [
                            "The rewrite changed how much of each row the scan touched, not how many rows it visited; nothing here is an index",
                            "The rewrite skipped the non-click rows entirely, but the counter records the table's size rather than the rows visited",
                            "The two counters measure the same thing in different units, and 25 cells is five rows of five cells each",
                            "The optimised plan reads fewer rows, and the filter re-reads the rest so that the scanned count stays equal across plans",
                        ],
                        "a": 0,
                        "whys": [
                            r"Five rows visited both times; 20 cells plus 5 filter cells became 2 cells a row with no filter pass.",
                            r"A scan has no way to skip a row without visiting it — that is what an index would provide, and there is none. The non-click row is visited, tested and not emitted, and it costs its two cells like every other row.",
                            r"The events have four columns, not five; the 25 is 20 scan cells plus 5 cells charged by the filter, one per row that reached it. The counters measure different things, which is why one moved and the other did not.",
                            r"There is no filter in the optimised plan; the predicate moved into the scan. Both plans visit all five rows, and the scanned count is equal because the visits are equal, not because anything re-read them.",
                        ],
                        "why": r'''
`rows_scanned` counts visits and `cells_read` counts the columns touched per visit,
plus one cell per row for every filter that runs on materialised rows. Pushdown and
pruning do not reduce visits — a scan without an index sees every row — but they cut
the columns read per row from four to two and remove the filter's separate pass, which
is 5 times 2 against 5 times 4 plus 5. The rows are the same; the bytes are not.
''',
                    },
                    {
                        "q": "Joining 100 unsorted events with 50 unsorted users, the model gives hash 150 and sort-merge 1096.6. If both inputs arrive already sorted on the key, which join is chosen, and why?",
                        "opts": [
                            "Sort-merge, because both sort terms vanish, it ties hash at 150, and a tie goes to the join whose output stays in key order",
                            "Hash, because building and probing a table is cheaper than a merge whatever order the two inputs happen to arrive in",
                            "Sort-merge, because sorted inputs let it skip the merge as well as the sorts, so it costs strictly less than hashing does on any input",
                            "Hash, because sorted inputs make the hash table smaller to build, so it beats the merge by a wider margin than before",
                        ],
                        "a": 0,
                        "whys": [
                            r"With no sorting to pay for, both cost $n + m$, and `choose_join` breaks the tie toward the algorithm that hands the next operator ordered rows.",
                            r"The sorts were 946.6 of the 1096.6; without them the merge is the same $n + m$ as the hash join. Hashing is not cheaper than merging, it is cheaper than *sorting and then* merging.",
                            r"The merge still walks both inputs once, so the cost is $n + m$, equal to hashing, not below it. Sort-merge wins the tie by the rule, not by being cheaper.",
                            r"A hash table is built from every right row whatever their order; sortedness does nothing for it. Its cost stays at 150 while sort-merge falls to meet it.",
                        ],
                        "why": r'''
Sort-merge pays $n \log_2 n$ and $m \log_2 m$ for the sorts and $n + m$ for the merge;
when an input is already sorted, its sort term is dropped. With both sorted it costs
150, exactly what hashing costs, and `choose_join` returns `"sort_merge"` on a tie
because its output is in key order, which a later operator may use for free. Hashing
gains nothing from sorted input; its cost is $n + m$ regardless.
''',
                    },
                    {
                        "q": "Two left rows and two right rows share the key 1. A sort-merge join emits two rows for that key rather than four. What went wrong?",
                        "opts": [
                            "On equal keys it emitted one pair and advanced a single cursor, instead of the cross product of the two equal-key groups",
                            "The sort placed the two equal keys on different sides of a group boundary, so the merge treated them as two keys",
                            "Sort-merge cannot represent repeated keys at all, and the join has to fall back to hashing whenever a key is not unique on both sides",
                            "The two rows are correct, because a join pairs each left row with a single right row and never multiplies the rows",
                        ],
                        "a": 0,
                        "whys": [
                            r"The merge must find the end of the equal-key group on both sides and emit every left-right pair before moving both cursors past the group.",
                            r"Sorting puts equal keys next to each other; that is what makes the group findable. Two rows with key 1 are adjacent after the sort, and a merge that scans to the end of the run sees them as one group.",
                            r"Sort-merge handles repeated keys as well as any join does, provided the equal-key branch loops over the whole group on both sides. The lab's `same_rows` test on a 2-by-2 group is there to prove it.",
                            r"A join emits one row for every matching pair; two left rows and two right rows with the same key are four pairs. `hash_join` on the same input returns four, and the two algorithms must agree.",
                        ],
                        "why": r'''
The equal-key branch of a merge has to collect the whole run of equal keys on each
side and emit the cross product, then move both cursors past both runs. Emitting one
pair and advancing one cursor happens to work when a key repeats on only one side,
which is why the shortcut survives most test data, and it drops half the rows on a
2-by-2 group. Hash join gets this right by keeping a list per key; the merge has to
earn it with the inner loop.
''',
                    },
                    {
                        "q": "The cost model prices a hash join at $n + m$ whatever the inputs. Where does that stop holding?",
                        "opts": [
                            "When the hash table no longer fits in memory or one key is heavily skewed, since spills and long buckets are priced at zero",
                            "When the inputs arrive sorted, since a hash table built from sorted input degenerates into a single long chain of colliding entries",
                            "When $n$ and $m$ differ greatly, since the table then has to be built on the larger side and probed with the smaller one",
                            "When the keys are strings rather than integers, since hashing a string costs $\\log n$ per row rather than a constant",
                        ],
                        "a": 0,
                        "whys": [
                            r"Real planners keep sort-merge partly because it degrades better when memory runs out, and skew makes one probe a walk down a million-row list.",
                            r"A hash function does not care about input order; sorted keys spread across buckets like any others. Sortedness is what helps sort-merge, and it leaves the hash join's cost where it was.",
                            r"The table is built on whichever side is smaller when the planner has the choice, which makes unequal sizes *better* for hashing, not worse; the model's $n + m$ is the same either way.",
                            r"Hashing a string costs its length, a constant that does not grow with $n$. The model ignores that cost too, but it is not what breaks the $n + m$ picture at scale.",
                        ],
                        "why": r'''
$n + m$ assumes every row is touched once at a constant cost, which holds while the
hash table lives in memory and buckets stay short. A table that does not fit is
partitioned and spilled to disk, and the join's real cost is dominated by that traffic;
a key that repeats a million times on the build side makes one bucket a million-row
list that every matching probe walks. The model prices both at zero, which is where
the module's cost model, deliberately, stops.
''',
                    },
                ],
            },
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
