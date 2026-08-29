"""CS320 — Computer Networks. Author module."""

COURSE = {
    "id": "CS320",
    "title": "Computer Networks",
    "year": 3,
    "level": "Advanced",
    "prereqs": ["CS210"],
    "stack": ["Python", "Go (reference)"],
    "credits": 15,
    "hours": 150,
    "icon": "⛓",
    "summary": (
        "The internet is a stack of protocols, each one solving exactly the problem "
        "the layer below leaves behind. This course builds that stack from the wire "
        "upwards: framing and error detection on a byte channel, reliable delivery "
        "over a channel that loses and reorders, routing that converges without a "
        "central authority, and the request/response and naming protocols the "
        "application layer is made of. Every mechanism is implemented and measured "
        "against a deterministic simulated network, never merely described."
    ),
    "outcomes": [
        "Frame a byte stream with escape stuffing and recover the payload from a damaged frame",
        "Implement the internet checksum and CRC-32, and measure what each one fails to detect",
        "Build stop-and-wait and sliding-window ARQ and compare their goodput on the same channel",
        "Explain and reproduce count-to-infinity, then fix it with split horizon",
        "Compute link-state routes with Dijkstra and show distance vector converges to the same distances",
        "Parse HTTP/1.1 messages, including chunked transfer encoding, from raw bytes",
        "Resolve a name through a delegating hierarchy with caching and expiry",
    ],
    "assessment": "4 lab checkpoints (10% each) + capstone build (60%).",
    "reading": [
        "Kurose & Ross, *Computer Networking: A Top-Down Approach*, 8th ed. (Pearson, 2020) — chapters 3-6",
        "Peterson & Davie, *Computer Networks: A Systems Approach*, 6th ed. (Morgan Kaufmann, 2021) — chapters 2-3",
        "Braden, Borman & Partridge, RFC 1071, *Computing the Internet Checksum* (IETF, 1988)",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "The link layer: framing and error detection",
            "summary": "Turning a byte pipe into delimited frames, and noticing when one is damaged.",
            "concepts": [
                "Framing: how a receiver finds where one frame ends and the next begins",
                "Byte stuffing (PPP, RFC 1662): escape the flag so data can never impersonate it",
                "Stuffing costs bandwidth — the worst case doubles the payload",
                "The internet checksum: 16-bit one's-complement sum, folded, then inverted (RFC 1071)",
                "Why the checksum is weak: reordering whole words leaves the sum unchanged",
                "CRC-32 as polynomial division over GF(2), computed with a reflected 256-entry table",
                "Error *detection* is not correction — a detected frame is simply discarded",
            ],
            "lab": {
                "title": "Framing, checksums and CRC-32",
                "runtime": "python",
                "minutes": 45,
                "brief": r'''
Build the bottom of the stack: a frame format, two integrity checks, and a
measurement of how much each check actually catches.

## Framing (PPP-style byte stuffing)

`FLAG = 0x7E`, `ESC = 0x7D`, `MASK = 0x20`.

- `stuff(payload)` returns `FLAG + escaped body + FLAG`. Inside the body every
  `FLAG` or `ESC` byte becomes `ESC` followed by that byte XOR `MASK`.
- `unstuff(frame)` reverses it, raising `FramingError` (a `ValueError`) when
  the frame is shorter than two bytes, does not begin and end with `FLAG`,
  contains an unescaped `FLAG`, or ends with a dangling `ESC`.

```text
stuff(b"\x7e\x7d\x01")  ->  7e 7d 5e 7d 5d 01 7e
```

## The internet checksum (RFC 1071)

`internet_checksum(data)` returns a 16-bit integer: pad `data` to an even
length with a zero byte, sum the 16-bit **big-endian** words, fold every carry
back into the low 16 bits until none is left, and return the one's complement.
An empty input gives `0xFFFF`.

The RFC's worked example, `00 01 f2 03 f4 f5 f6 f7`, checksums to `0x220D`.
The defining property: appending the checksum to an even-length payload makes
the checksum of the result zero.

## CRC-32

`crc32(data)` returns the standard reflected CRC-32 (polynomial `0xEDB88320`,
initial value `0xFFFFFFFF`, final XOR `0xFFFFFFFF`) — the one `zlib.crc32`
produces. Build the 256-entry table once at import time. `crc32(b"")` is `0`
and `crc32(b"123456789")` is `0xCBF43926`.

## Measuring detection

- `flip_bits(data, positions)` returns a copy with those **bit** positions
  flipped; bit `p` is bit `p % 8` of byte `p // 8`.
- `detection_rate(payload, detector, trials, bits, seed)` returns the fraction
  of corruptions the detector notices. Use `rng = random.Random(seed)` and,
  once per trial, `rng.sample(range(len(payload) * 8), bits)` to choose the
  positions; a corruption counts as detected when the detector's value differs
  from its value on the clean payload.

Both checks catch every single-bit error. Two-bit errors are where they part
company.
''',
                "files": [{"name": "main.py", "content": r'''
import random

FLAG = 0x7E
ESC = 0x7D
MASK = 0x20
CRC_POLY = 0xEDB88320


class FramingError(ValueError):
    """Raised when a byte sequence is not a well-formed frame."""


def stuff(payload):
    """FLAG + escaped payload + FLAG."""
    # your code here


def unstuff(frame):
    """The payload inside a frame; FramingError when the frame is malformed."""
    # your code here


def internet_checksum(data):
    """The 16-bit one's-complement checksum of data (RFC 1071)."""
    # your code here


def crc32(data):
    """The reflected CRC-32 of data, as an unsigned 32-bit integer."""
    # your code here


def flip_bits(data, positions):
    """A copy of data with those bit positions flipped."""
    # your code here


def detection_rate(payload, detector, trials=400, bits=1, seed=7):
    """The fraction of random bit corruptions the detector notices."""
    # your code here


sample = b"\x00\x01\xf2\x03\xf4\xf5\xf6\xf7"
print(stuff(b"\x7e\x7d\x01").hex())
print(hex(internet_checksum(sample)), hex(crc32(b"123456789")))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import random

FLAG = 0x7E
ESC = 0x7D
MASK = 0x20
CRC_POLY = 0xEDB88320


class FramingError(ValueError):
    """Raised when a byte sequence is not a well-formed frame."""


def stuff(payload):
    """FLAG + escaped payload + FLAG."""
    body = bytearray()
    for byte in payload:
        if byte in (FLAG, ESC):
            body.append(ESC)
            body.append(byte ^ MASK)
        else:
            body.append(byte)
    return bytes([FLAG]) + bytes(body) + bytes([FLAG])


def unstuff(frame):
    """The payload inside a frame; FramingError when the frame is malformed."""
    if len(frame) < 2 or frame[0] != FLAG or frame[-1] != FLAG:
        raise FramingError("a frame starts and ends with a flag")
    body = frame[1:-1]
    out = bytearray()
    index = 0
    while index < len(body):
        byte = body[index]
        if byte == FLAG:
            raise FramingError("unescaped flag inside a frame")
        if byte == ESC:
            if index + 1 >= len(body):
                raise FramingError("dangling escape at the end of a frame")
            out.append(body[index + 1] ^ MASK)
            index += 2
            continue
        out.append(byte)
        index += 1
    return bytes(out)


def internet_checksum(data):
    """The 16-bit one's-complement checksum of data (RFC 1071)."""
    padded = bytes(data) + (b"\x00" if len(data) % 2 else b"")
    total = 0
    for index in range(0, len(padded), 2):
        total += (padded[index] << 8) | padded[index + 1]
        total = (total & 0xFFFF) + (total >> 16)
    while total >> 16:
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


def _crc_table():
    """The 256-entry reflected CRC-32 table, built once."""
    table = []
    for index in range(256):
        value = index
        for _ in range(8):
            value = (value >> 1) ^ (CRC_POLY if value & 1 else 0)
        table.append(value)
    return tuple(table)


CRC_TABLE = _crc_table()


def crc32(data):
    """The reflected CRC-32 of data, as an unsigned 32-bit integer."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc = CRC_TABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF


def flip_bits(data, positions):
    """A copy of data with those bit positions flipped."""
    out = bytearray(data)
    for position in positions:
        out[position // 8] ^= 1 << (position % 8)
    return bytes(out)


def detection_rate(payload, detector, trials=400, bits=1, seed=7):
    """The fraction of random bit corruptions the detector notices."""
    rng = random.Random(seed)
    clean = detector(payload)
    detected = 0
    for _ in range(trials):
        positions = rng.sample(range(len(payload) * 8), bits)
        if detector(flip_bits(payload, positions)) != clean:
            detected += 1
    return detected / trials


sample = b"\x00\x01\xf2\x03\xf4\xf5\xf6\xf7"
print(stuff(b"\x7e\x7d\x01").hex())
print(hex(internet_checksum(sample)), hex(crc32(b"123456789")))
'''}],
                "hints": [
                    "Stuffing is a single pass: copy each byte, except that a FLAG or ESC becomes two bytes.",
                    "For the checksum, fold after every addition (`total = (total & 0xFFFF) + (total >> 16)`) and the running value never grows.",
                    "Build the CRC table with `value = (value >> 1) ^ (CRC_POLY if value & 1 else 0)`, eight times per entry.",
                    "`crc = TABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)` is the whole per-byte update; remember the initial and final XOR with 0xFFFFFFFF.",
                ],
                "tests": [
                    {"name": "Stuffing escapes the reserved bytes", "code": r'''
_got = stuff(b"\x7e\x7d\x01")
assert _got == bytes([0x7E, 0x7D, 0x5E, 0x7D, 0x5D, 0x01, 0x7E]), f"Got {_got.hex()}"
assert stuff(b"") == b"\x7e\x7e", f"an empty payload still needs both flags, got {stuff(b'').hex()}"
assert stuff(b"hi") == b"\x7ehi\x7e", f"ordinary bytes pass through, got {stuff(b'hi').hex()}"
assert len(stuff(b"\x7e" * 4)) == 10, "four flag bytes stuff to eight, plus two delimiters"
'''},
                    {"name": "Unstuffing round-trips every payload", "code": r'''
for _p in [b"", b"hi", b"\x7e", b"\x7d", b"\x7e\x7d\x7e", bytes(range(256))]:
    _got = unstuff(stuff(_p))
    assert _got == _p, f"round trip of {_p!r} gave {_got!r}"
'''},
                    {"name": "Malformed frames are rejected", "code": r'''
for _bad in [b"", b"\x7e", b"abc", b"\x7eabc", b"abc\x7e",
             b"\x7e\x7e\x7e", b"\x7eab\x7d\x7e"]:
    try:
        unstuff(_bad)
        assert False, f"unstuff({_bad!r}) should raise FramingError"
    except FramingError:
        pass
assert issubclass(FramingError, ValueError), "FramingError should be a ValueError"
'''},
                    {"name": "The internet checksum matches RFC 1071", "code": r'''
_sample = b"\x00\x01\xf2\x03\xf4\xf5\xf6\xf7"
_got = internet_checksum(_sample)
assert _got == 0x220D, f"internet_checksum of the RFC example gave {hex(_got)}, expected 0x220d"
assert internet_checksum(b"") == 0xFFFF, f"an empty input gives 0xffff, got {hex(internet_checksum(b''))}"
assert internet_checksum(b"\x01\x02\x03") == internet_checksum(b"\x01\x02\x03\x00"), \
    "an odd length is padded with a zero byte"
for _data in [_sample, b"", b"\x01\x02", bytes(range(64))]:
    _c = internet_checksum(_data)
    assert internet_checksum(_data + _c.to_bytes(2, "big")) == 0, \
        f"data plus its own checksum must check to 0, failed for {_data!r}"
'''},
                    {"name": "CRC-32 matches the standard check values", "code": r'''
assert crc32(b"") == 0, f"crc32(b'') gave {crc32(b'')!r}, expected 0"
assert crc32(b"123456789") == 0xCBF43926, f"crc32 of the check string gave {hex(crc32(b'123456789'))}"
assert crc32(b"hello world") == 0x0D4A1185, f"crc32(b'hello world') gave {hex(crc32(b'hello world'))}"
assert crc32(b"a") != crc32(b"b"), "different bytes must give different remainders here"
assert 0 <= crc32(bytes(range(256))) <= 0xFFFFFFFF, "the result is an unsigned 32-bit integer"
'''},
                    {"name": "flip_bits touches exactly the named bits", "code": r'''
assert flip_bits(b"\x00", [0]) == b"\x01", f"Got {flip_bits(b'\x00', [0])!r}"
assert flip_bits(b"\x00", [7]) == b"\x80", f"Got {flip_bits(b'\x00', [7])!r}"
assert flip_bits(b"\x00\x00", [8]) == b"\x00\x01", "bit 8 is the low bit of byte 1"
assert flip_bits(b"\xff", [0, 1]) == b"\xfc", "flipping two set bits clears them"
assert flip_bits(b"\x00", []) == b"\x00", "no positions means no change"
'''},
                    {"name": "Word reordering slips past the checksum, not the CRC", "code": r'''
_a, _b = b"\x12\x34\xab\xcd", b"\xab\xcd\x12\x34"
assert internet_checksum(_a) == internet_checksum(_b), \
    "swapping two 16-bit words leaves the one's-complement sum unchanged"
assert crc32(_a) != crc32(_b), "CRC-32 is position sensitive and must notice the swap"
'''},
                    {"name": "Detection rates: both catch single bits, only CRC catches every pair", "code": r'''
_payload = bytes(range(64))
assert detection_rate(_payload, crc32, 300, 1, 7) == 1.0, "CRC-32 detects every single-bit error"
assert detection_rate(_payload, internet_checksum, 300, 1, 7) == 1.0, \
    "the checksum also detects every single-bit error"
assert detection_rate(_payload, crc32, 400, 2, 7) == 1.0, "CRC-32 detects every double-bit error here"
_chk2 = detection_rate(_payload, internet_checksum, 400, 2, 7)
assert 0.9 < _chk2 < 1.0, \
    f"the checksum should miss a few double-bit errors, got a rate of {_chk2!r}"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Reliable transport over an unreliable channel",
            "summary": "Sequence numbers, acknowledgements and windows, measured as goodput.",
            "concepts": [
                "The reliability problem: loss, duplication and delay, on top of a best-effort layer",
                "Alternating-bit stop-and-wait: one outstanding frame, one sequence bit",
                "Why the receiver must re-acknowledge a duplicate rather than ignore it",
                "A lost acknowledgement is indistinguishable from a lost frame at the sender",
                "Go-Back-N: a window of unacknowledged frames and a cumulative acknowledgement",
                "Out-of-order frames are discarded by a Go-Back-N receiver, so one loss costs a window",
                "Goodput = useful frames delivered / total transmissions; the bandwidth-delay product sets the window",
            ],
            "lab": {
                "title": "Stop-and-wait and Go-Back-N on a deterministic channel",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
Randomised loss makes protocol behaviour impossible to reason about exactly,
so this channel loses *precisely* the transmissions you name.

## The channel

`Link(data_drops=(), ack_drops=())` counts data and acknowledgement
transmissions separately, both from zero:

- `send_data(seq)` increments `data_sends` and returns `False` when this
  transmission's index is in `data_drops`, otherwise `True`.
- `send_ack(seq)` does the same against `ack_sends` and `ack_drops`.

## Stop-and-wait

```text
expected_bit = 0
for index, frame in enumerate(frames):
    seq = index % 2
    loop forever:
        arrived = link.send_data(seq)
        if arrived:
            if seq == expected_bit:          # a new frame
                deliver it; flip expected_bit
            if link.send_ack(seq):           # the receiver acks what it saw,
                break                        # duplicate or not
        timeouts += 1
```

Return `{"delivered": [...], "data_sends": n, "ack_sends": n, "timeouts": n}`.

## Go-Back-N

One round is one window burst followed by at most one cumulative
acknowledgement:

```text
base = 0; expected = 0
while base < len(frames):
    rounds += 1
    for seq in range(base, min(base + window, len(frames))):
        if link.send_data(seq) and seq == expected:
            deliver frames[seq]; expected += 1
    if expected > base and link.send_ack(expected - 1):
        base = expected
```

A frame that arrives out of order is discarded, so the whole window is sent
again next round. Return
`{"delivered": [...], "data_sends": n, "ack_sends": n, "rounds": n}`.
A `window` below 1 raises `ValueError`. Both protocols raise `RuntimeError`
rather than looping for ever once `MAX_ROUNDS` (1000) is exceeded.

## Goodput

`goodput(result, frames)` is `len(frames) / result["data_sends"]`, and `0.0`
when nothing was sent.

```text
frames = [b"a", b"b", b"c", b"d", b"e"]
stop_and_wait(frames, Link())                  data_sends 5, timeouts 0
stop_and_wait(frames, Link(ack_drops={0}))     data_sends 6, ack_sends 6
go_back_n(frames, Link(), 3)                   data_sends 5, ack_sends 2, rounds 2
go_back_n(frames, Link(data_drops={1}), 3)     data_sends 7, ack_sends 3, rounds 3
```
''',
                "files": [{"name": "main.py", "content": r'''
MAX_ROUNDS = 1000


class Link:
    """A deterministic channel: it drops exactly the transmissions you name."""

    def __init__(self, data_drops=(), ack_drops=()):
        self.data_drops = set(data_drops)
        self.ack_drops = set(ack_drops)
        self.data_sends = 0
        self.ack_sends = 0

    def send_data(self, seq):
        """True when this data transmission arrives."""
        # your code here

    def send_ack(self, seq):
        """True when this acknowledgement arrives."""
        # your code here


def stop_and_wait(frames, link):
    """Alternating-bit ARQ. Returns delivered frames and the counters."""
    # your code here


def go_back_n(frames, link, window):
    """Sliding-window ARQ with cumulative acknowledgements."""
    # your code here


def goodput(result, frames):
    """Useful frames per transmission."""
    # your code here


data = [b"a", b"b", b"c", b"d", b"e"]
print(stop_and_wait(data, Link(data_drops={1, 4}, ack_drops={0, 3})))
print(go_back_n(data, Link(data_drops={1}), 3))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
MAX_ROUNDS = 1000


class Link:
    """A deterministic channel: it drops exactly the transmissions you name."""

    def __init__(self, data_drops=(), ack_drops=()):
        self.data_drops = set(data_drops)
        self.ack_drops = set(ack_drops)
        self.data_sends = 0
        self.ack_sends = 0

    def send_data(self, seq):
        """True when this data transmission arrives."""
        index = self.data_sends
        self.data_sends += 1
        return index not in self.data_drops

    def send_ack(self, seq):
        """True when this acknowledgement arrives."""
        index = self.ack_sends
        self.ack_sends += 1
        return index not in self.ack_drops


def stop_and_wait(frames, link):
    """Alternating-bit ARQ. Returns delivered frames and the counters."""
    delivered = []
    expected_bit = 0
    timeouts = 0
    for index, frame in enumerate(frames):
        seq = index % 2
        while True:
            if link.data_sends > MAX_ROUNDS:
                raise RuntimeError("giving up: the channel never delivered")
            if link.send_data(seq):
                if seq == expected_bit:
                    delivered.append(frame)
                    expected_bit ^= 1
                if link.send_ack(seq):
                    break
            timeouts += 1
    return {"delivered": delivered, "data_sends": link.data_sends,
            "ack_sends": link.ack_sends, "timeouts": timeouts}


def go_back_n(frames, link, window):
    """Sliding-window ARQ with cumulative acknowledgements."""
    if window < 1:
        raise ValueError("window must be at least 1")
    delivered = []
    base = 0
    expected = 0
    rounds = 0
    while base < len(frames):
        rounds += 1
        if rounds > MAX_ROUNDS:
            raise RuntimeError("giving up: the channel never delivered")
        for seq in range(base, min(base + window, len(frames))):
            if link.send_data(seq) and seq == expected:
                delivered.append(frames[seq])
                expected += 1
        if expected > base and link.send_ack(expected - 1):
            base = expected
    return {"delivered": delivered, "data_sends": link.data_sends,
            "ack_sends": link.ack_sends, "rounds": rounds}


def goodput(result, frames):
    """Useful frames per transmission."""
    if not result["data_sends"]:
        return 0.0
    return len(frames) / result["data_sends"]


data = [b"a", b"b", b"c", b"d", b"e"]
print(stop_and_wait(data, Link(data_drops={1, 4}, ack_drops={0, 3})))
print(go_back_n(data, Link(data_drops={1}), 3))
'''}],
                "hints": [
                    "`send_data` must increment the counter *before* it decides, so the very first transmission has index 0.",
                    "In stop-and-wait, the receiver acknowledges every frame that arrives — including a duplicate — otherwise a lost ack deadlocks the sender.",
                    "Only advance `expected_bit` when the arriving sequence bit is the one you were waiting for; otherwise you deliver the same frame twice.",
                    "In Go-Back-N the receiver never buffers: `seq == expected` is the whole acceptance test, and a gap makes the rest of the burst useless.",
                ],
                "tests": [
                    {"name": "The channel drops exactly what it was told to", "code": r'''
_link = Link(data_drops={0, 2}, ack_drops={1})
assert _link.send_data(0) is False, "transmission 0 is in data_drops"
assert _link.send_data(0) is True, "transmission 1 is not"
assert _link.send_data(1) is False, "transmission 2 is in data_drops"
assert _link.data_sends == 3, f"data_sends is {_link.data_sends!r}, expected 3"
assert _link.send_ack(0) is True and _link.send_ack(1) is False, "acks are counted separately"
assert _link.ack_sends == 2, f"ack_sends is {_link.ack_sends!r}, expected 2"
assert Link().send_data(0) is True, "a link with no drops delivers everything"
'''},
                    {"name": "Stop-and-wait on a clean channel", "code": r'''
_frames = [b"a", b"b", b"c", b"d", b"e"]
_r = stop_and_wait(_frames, Link())
assert _r["delivered"] == _frames, f"delivered {_r['delivered']!r}"
assert (_r["data_sends"], _r["ack_sends"], _r["timeouts"]) == (5, 5, 0), \
    f"counters were {(_r['data_sends'], _r['ack_sends'], _r['timeouts'])!r}, expected (5, 5, 0)"
_empty = stop_and_wait([], Link())
assert _empty["delivered"] == [] and _empty["data_sends"] == 0, f"Got {_empty!r}"
'''},
                    {"name": "Stop-and-wait retransmits and refuses duplicates", "code": r'''
_frames = [b"a", b"b", b"c", b"d", b"e"]
_r = stop_and_wait(_frames, Link(data_drops={0}))
assert _r["delivered"] == _frames, f"delivered {_r['delivered']!r}"
assert (_r["data_sends"], _r["ack_sends"], _r["timeouts"]) == (6, 5, 1), \
    f"one lost frame: counters were {(_r['data_sends'], _r['ack_sends'], _r['timeouts'])!r}, expected (6, 5, 1)"
_r = stop_and_wait(_frames, Link(ack_drops={0}))
assert _r["delivered"] == _frames, \
    f"a lost ack must not duplicate a frame, delivered {_r['delivered']!r}"
assert (_r["data_sends"], _r["ack_sends"], _r["timeouts"]) == (6, 6, 1), \
    f"one lost ack: counters were {(_r['data_sends'], _r['ack_sends'], _r['timeouts'])!r}, expected (6, 6, 1)"
_r = stop_and_wait(_frames, Link(data_drops={1, 4}, ack_drops={0, 3}))
assert _r["delivered"] == _frames, f"delivered {_r['delivered']!r}"
assert (_r["data_sends"], _r["ack_sends"], _r["timeouts"]) == (9, 7, 4), \
    f"mixed losses: counters were {(_r['data_sends'], _r['ack_sends'], _r['timeouts'])!r}, expected (9, 7, 4)"
'''},
                    {"name": "Go-Back-N bursts a window and acknowledges cumulatively", "code": r'''
_frames = [b"a", b"b", b"c", b"d", b"e"]
_r = go_back_n(_frames, Link(), 3)
assert _r["delivered"] == _frames, f"delivered {_r['delivered']!r}"
assert (_r["data_sends"], _r["ack_sends"], _r["rounds"]) == (5, 2, 2), \
    f"clean window of 3: counters were {(_r['data_sends'], _r['ack_sends'], _r['rounds'])!r}, expected (5, 2, 2)"
_r = go_back_n(_frames, Link(), 10)
assert (_r["data_sends"], _r["ack_sends"], _r["rounds"]) == (5, 1, 1), \
    f"a window larger than the file needs one round, got {(_r['data_sends'], _r['ack_sends'], _r['rounds'])!r}"
_r = go_back_n(_frames, Link(), 1)
assert (_r["data_sends"], _r["ack_sends"], _r["rounds"]) == (5, 5, 5), \
    f"a window of 1 degenerates to one frame per round, got {(_r['data_sends'], _r['ack_sends'], _r['rounds'])!r}"
assert go_back_n([], Link(), 3)["rounds"] == 0, "nothing to send means no rounds"
'''},
                    {"name": "One loss costs the rest of the window", "code": r'''
_frames = [b"a", b"b", b"c", b"d", b"e"]
_r = go_back_n(_frames, Link(data_drops={1}), 3)
assert _r["delivered"] == _frames, f"delivered {_r['delivered']!r}"
assert (_r["data_sends"], _r["ack_sends"], _r["rounds"]) == (7, 3, 3), \
    f"losing frame 1 of the first burst: got {(_r['data_sends'], _r['ack_sends'], _r['rounds'])!r}, expected (7, 3, 3)"
_r = go_back_n(_frames, Link(data_drops={0}), 3)
assert _r["delivered"] == _frames, f"delivered {_r['delivered']!r}"
assert (_r["data_sends"], _r["ack_sends"], _r["rounds"]) == (8, 2, 3), \
    f"losing the base frame wastes the whole burst: got {(_r['data_sends'], _r['ack_sends'], _r['rounds'])!r}, expected (8, 2, 3)"
_r = go_back_n(_frames, Link(ack_drops={0}), 3)
assert _r["delivered"] == _frames, f"a lost cumulative ack must not duplicate data: {_r['delivered']!r}"
assert (_r["data_sends"], _r["ack_sends"], _r["rounds"]) == (8, 3, 3), \
    f"losing the first ack: got {(_r['data_sends'], _r['ack_sends'], _r['rounds'])!r}, expected (8, 3, 3)"
'''},
                    {"name": "A window below one is refused", "code": r'''
for _bad in (0, -1):
    try:
        go_back_n([b"a"], Link(), _bad)
        assert False, f"go_back_n with window={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Goodput quantifies the cost of loss", "code": r'''
_frames = [b"a", b"b", b"c", b"d", b"e"]
_clean = go_back_n(_frames, Link(), 3)
assert goodput(_clean, _frames) == 1.0, f"a clean run has goodput 1.0, got {goodput(_clean, _frames)!r}"
_lossy = go_back_n(_frames, Link(data_drops={1}), 3)
_got = goodput(_lossy, _frames)
assert abs(_got - 5 / 7) < 1e-9, f"goodput was {_got!r}, expected 5/7"
assert goodput({"data_sends": 0}, []) == 0.0, "nothing sent means a goodput of 0.0"
assert goodput(stop_and_wait(_frames, Link(data_drops={0})), _frames) < 1.0, \
    "any retransmission must push goodput below 1"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Routing: distance vector and link state",
            "summary": "Two ways to find the same shortest paths, and what goes wrong with one of them.",
            "concepts": [
                "The routing problem: build a forwarding table with only local information",
                "Bellman-Ford: D(x, y) = min over neighbours v of c(x, v) + D(v, y)",
                "Distance vector is distributed, asynchronous and self-terminating — and slow to react to bad news",
                "Count-to-infinity: a route that loops back through the sender rises one hop at a time",
                "'Infinity' must be small (RIP uses 16) purely to bound how long the counting takes",
                "Split horizon: never advertise a route back to the neighbour you learned it from",
                "Link state: flood the topology, then run Dijkstra locally — same answer, different failure modes",
            ],
            "lab": {
                "title": "Convergence, and how it fails",
                "runtime": "python",
                "minutes": 50,
                "brief": r'''
The same topology, routed two ways.

A graph is `{node: {neighbour: cost}}`, symmetric. `INFINITY` is `16`.

## Link state

- `dijkstra(graph, source)` returns `(dist, prev)`. Every node appears in
  both; unreachable nodes have `float("inf")` distance and `None` predecessor.
  An unknown source raises `KeyError`. Break ties by visiting neighbours in
  sorted order so the result is reproducible.
- `shortest_path(prev, source, dest)` returns the node list from `source` to
  `dest`, `[source]` when they are the same node, and `[]` when there is no
  path.

## Distance vector

A table is `{destination: (cost, next_hop)}`; the entry for the node itself is
`(0, None)`, and an unreachable destination is `(INFINITY, None)`.

- `initial_tables(graph)` — every node knows only itself and its direct links.
- `dv_round(graph, tables, split_horizon=False)` returns **new** tables, one
  synchronous exchange later. Each node recomputes every destination from
  scratch: `min over neighbours v of cost(node, v) + tables[v][dest]`, capped
  at `INFINITY`, taking neighbours in sorted order so ties resolve
  reproducibly. With `split_horizon=True`, a neighbour `v` whose route to
  `dest` has `next_hop == node` is skipped — you never learn a route back
  through yourself.
- `run_dv(graph, tables=None, split_horizon=False, max_rounds=100)` returns
  `(tables, rounds)`, iterating until a round changes nothing. `rounds` counts
  only the rounds that changed something.
- `drop_link(graph, a, b)` returns a **copy** of the graph without that edge.

## What you should see

On the five-node mesh in the starter, distance vector converges in 3 rounds to
exactly the distances Dijkstra computes. On the three-node line `A-B-C` with
unit costs, removing `A-B` sends the survivors counting to infinity — 15 rounds
— while split horizon settles it in 2.
''',
                "files": [{"name": "main.py", "content": r'''
import heapq

INFINITY = 16

MESH = {
    "A": {"B": 2, "C": 5},
    "B": {"A": 2, "C": 1, "D": 4},
    "C": {"A": 5, "B": 1, "D": 2, "E": 8},
    "D": {"B": 4, "C": 2, "E": 3},
    "E": {"C": 8, "D": 3},
}

LINE = {"A": {"B": 1}, "B": {"A": 1, "C": 1}, "C": {"B": 1}}


def dijkstra(graph, source):
    """(dist, prev) for every node, by shortest total cost from source."""
    # your code here


def shortest_path(prev, source, dest):
    """The node list from source to dest, or [] when there is no path."""
    # your code here


def initial_tables(graph):
    """Each node knowing only itself and its direct neighbours."""
    # your code here


def dv_round(graph, tables, split_horizon=False):
    """One synchronous exchange; returns new tables."""
    # your code here


def run_dv(graph, tables=None, split_horizon=False, max_rounds=100):
    """(tables, rounds) once the exchange stops changing anything."""
    # your code here


def drop_link(graph, a, b):
    """A copy of graph with the edge between a and b removed."""
    # your code here


print(dijkstra(MESH, "A")[0])
print(run_dv(MESH)[1])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import heapq

INFINITY = 16

MESH = {
    "A": {"B": 2, "C": 5},
    "B": {"A": 2, "C": 1, "D": 4},
    "C": {"A": 5, "B": 1, "D": 2, "E": 8},
    "D": {"B": 4, "C": 2, "E": 3},
    "E": {"C": 8, "D": 3},
}

LINE = {"A": {"B": 1}, "B": {"A": 1, "C": 1}, "C": {"B": 1}}


def dijkstra(graph, source):
    """(dist, prev) for every node, by shortest total cost from source."""
    if source not in graph:
        raise KeyError(f"unknown node {source!r}")
    dist = {node: float("inf") for node in graph}
    prev = {node: None for node in graph}
    dist[source] = 0
    seen = set()
    queue = [(0, source)]
    while queue:
        cost, node = heapq.heappop(queue)
        if node in seen:
            continue
        seen.add(node)
        for neighbour, weight in sorted(graph[node].items()):
            if cost + weight < dist[neighbour]:
                dist[neighbour] = cost + weight
                prev[neighbour] = node
                heapq.heappush(queue, (cost + weight, neighbour))
    return dist, prev


def shortest_path(prev, source, dest):
    """The node list from source to dest, or [] when there is no path."""
    if source == dest:
        return [source]
    path = [dest]
    while path[-1] is not None and path[-1] != source:
        path.append(prev[path[-1]])
    if path[-1] is None:
        return []
    return list(reversed(path))


def initial_tables(graph):
    """Each node knowing only itself and its direct neighbours."""
    tables = {}
    for node in graph:
        table = {other: (INFINITY, None) for other in graph}
        table[node] = (0, None)
        for neighbour, weight in graph[node].items():
            table[neighbour] = (min(weight, INFINITY), neighbour)
        tables[node] = table
    return tables


def dv_round(graph, tables, split_horizon=False):
    """One synchronous exchange; returns new tables."""
    updated = {}
    for node in graph:
        table = {other: (INFINITY, None) for other in graph}
        table[node] = (0, None)
        for dest in graph:
            if dest == node:
                continue
            best, hop = INFINITY, None
            for neighbour, weight in sorted(graph[node].items()):
                cost, advertised_hop = tables[neighbour][dest]
                if split_horizon and advertised_hop == node:
                    continue
                total = min(weight + cost, INFINITY)
                if total < best:
                    best, hop = total, neighbour
            table[dest] = (best, hop) if best < INFINITY else (INFINITY, None)
        updated[node] = table
    return updated


def run_dv(graph, tables=None, split_horizon=False, max_rounds=100):
    """(tables, rounds) once the exchange stops changing anything."""
    tables = initial_tables(graph) if tables is None else tables
    rounds = 0
    while rounds < max_rounds:
        nxt = dv_round(graph, tables, split_horizon)
        if nxt == tables:
            return tables, rounds
        tables = nxt
        rounds += 1
    return tables, rounds


def drop_link(graph, a, b):
    """A copy of graph with the edge between a and b removed."""
    copy = {node: dict(edges) for node, edges in graph.items()}
    copy[a].pop(b, None)
    copy[b].pop(a, None)
    return copy


print(dijkstra(MESH, "A")[0])
print(run_dv(MESH)[1])
'''}],
                "hints": [
                    "Dijkstra with a heap needs the lazy-deletion guard: pop, skip the node if you have already settled it, then relax its edges.",
                    "Walk `prev` backwards from the destination and reverse the list; a `None` before you reach the source means there is no path.",
                    "`dv_round` must build a whole new table per node from the *old* tables — updating in place makes one node's new route visible to the next in the same round.",
                    "Split horizon is one line: skip a neighbour whose advertised next hop for this destination is you.",
                ],
                "tests": [
                    {"name": "Dijkstra on the mesh", "code": r'''
_dist, _prev = dijkstra(MESH, "A")
assert _dist == {"A": 0, "B": 2, "C": 3, "D": 5, "E": 8}, f"distances from A were {_dist!r}"
assert dijkstra(MESH, "E")[0] == {"A": 8, "B": 6, "C": 5, "D": 3, "E": 0}, \
    f"distances from E were {dijkstra(MESH, 'E')[0]!r}"
try:
    dijkstra(MESH, "Z")
    assert False, "an unknown source should raise KeyError"
except KeyError:
    pass
'''},
                    {"name": "Paths are reconstructed from prev", "code": r'''
_dist, _prev = dijkstra(MESH, "A")
assert shortest_path(_prev, "A", "E") == ["A", "B", "C", "D", "E"], \
    f"Got {shortest_path(_prev, 'A', 'E')!r}"
assert shortest_path(_prev, "A", "A") == ["A"], "a node reaches itself in one step"
assert shortest_path(_prev, "A", "C") == ["A", "B", "C"], \
    f"the direct A-C link costs 5, so the cheap route goes via B: {shortest_path(_prev, 'A', 'C')!r}"
_split = {"A": {"B": 1}, "B": {"A": 1}, "X": {}}
_d, _p = dijkstra(_split, "A")
assert _d["X"] == float("inf"), f"X is unreachable, distance was {_d['X']!r}"
assert shortest_path(_p, "A", "X") == [], "an unreachable destination has no path"
'''},
                    {"name": "Initial tables know only the neighbours", "code": r'''
_t = initial_tables(MESH)
assert _t["A"] == {"A": (0, None), "B": (2, "B"), "C": (5, "C"),
                   "D": (INFINITY, None), "E": (INFINITY, None)}, f"Got {_t['A']!r}"
assert set(_t) == set(MESH), "every node needs a table"
assert all(set(_t[n]) == set(MESH) for n in MESH), "every table needs an entry per destination"
'''},
                    {"name": "Distance vector converges to the link-state answer", "code": r'''
_tables, _rounds = run_dv(MESH)
assert _rounds == 3, f"the mesh converged in {_rounds!r} rounds, expected 3"
for _src in MESH:
    _dist, _ = dijkstra(MESH, _src)
    for _dst in MESH:
        _got = _tables[_src][_dst][0]
        assert _got == _dist[_dst], \
            f"distance vector says {_src}->{_dst} costs {_got!r}, Dijkstra says {_dist[_dst]!r}"
assert _tables["A"]["E"] == (8, "B"), f"A should reach E via B at cost 8, got {_tables['A']['E']!r}"
'''},
                    {"name": "A round is synchronous, not in place", "code": r'''
_before = initial_tables(MESH)
_snapshot = {n: dict(t) for n, t in _before.items()}
_after = dv_round(MESH, _before)
assert _before == _snapshot, "dv_round must not mutate the tables it was given"
assert _after is not _before, "dv_round returns new tables"
assert _after["A"]["D"] == (6, "B"), \
    f"after one round A reaches D via B at 2+4=6, got {_after['A']['D']!r}"
assert _after["A"]["E"] == (13, "C"), \
    f"after one round A only knows E via C at 5+8=13, got {_after['A']['E']!r}"
'''},
                    {"name": "Count-to-infinity, and split horizon", "code": r'''
_converged, _ = run_dv(LINE)
assert _converged["C"]["A"] == (2, "B"), f"C reaches A via B at cost 2, got {_converged['C']['A']!r}"
_broken = drop_link(LINE, "A", "B")
assert "B" not in _broken["A"] and "A" not in _broken["B"], "drop_link removes both directions"
assert LINE["A"] == {"B": 1}, "drop_link must copy, not edit the original graph"
_naive, _slow = run_dv(_broken, {n: dict(t) for n, t in _converged.items()})
assert _slow == 15, f"without split horizon the count to infinity takes 15 rounds, got {_slow!r}"
assert _naive["B"]["A"] == (INFINITY, None), f"B should end up with no route to A, got {_naive['B']['A']!r}"
assert _naive["C"]["A"] == (INFINITY, None), f"C should end up with no route to A, got {_naive['C']['A']!r}"
_fast_tables, _fast = run_dv(_broken, {n: dict(t) for n, t in _converged.items()}, split_horizon=True)
assert _fast == 2, f"split horizon should settle it in 2 rounds, got {_fast!r}"
assert _fast_tables["B"]["A"] == (INFINITY, None) and _fast_tables["C"]["A"] == (INFINITY, None), \
    "split horizon must reach the same final answer, only sooner"
'''},
                    {"name": "Split horizon does not break a healthy network", "code": r'''
_plain, _ = run_dv(MESH)
_guarded, _rounds = run_dv(MESH, split_horizon=True)
for _src in MESH:
    for _dst in MESH:
        assert _guarded[_src][_dst][0] == _plain[_src][_dst][0], \
            f"split horizon changed the cost {_src}->{_dst}: {_guarded[_src][_dst]!r} vs {_plain[_src][_dst]!r}"
assert _rounds <= 4, f"split horizon should not slow convergence down, took {_rounds!r} rounds"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "The application layer: HTTP and naming",
            "summary": "Parsing a text protocol from raw bytes, and walking a delegating name hierarchy.",
            "concepts": [
                "HTTP/1.1 message grammar: start line, header fields, CRLF CRLF, body (RFC 7230)",
                "Header field names are case-insensitive; repeated fields join with a comma",
                "Framing a body: Content-Length, or chunked transfer encoding when the length is unknown",
                "A chunked body is a series of hex-sized pieces terminated by a zero-length chunk",
                "Robustness: a parser that trusts its input is an attack surface",
                "DNS as a delegating hierarchy — root, TLD, then authoritative name server",
                "Caching with a TTL is what makes recursive resolution affordable; CNAME chains need a loop guard",
            ],
            "lab": {
                "title": "An HTTP/1.1 parser and a recursive resolver",
                "runtime": "python",
                "minutes": 55,
                "brief": r'''
Two application-layer protocols, parsed and walked from first principles.

## Part 1 — HTTP/1.1

Everything is `bytes` on the wire; header names and values decode as
`latin-1`. `HttpError` is a `ValueError`.

- `split_head(raw)` returns `(head, body)` around the first `CRLF CRLF`, and
  raises `HttpError` when there is none.
- `parse_headers(lines)` returns `{lowercased name: value}`. Values are
  stripped. A repeated field joins with `", "` in arrival order. A line with
  no colon, an empty name, or whitespace between the name and the colon is an
  `HttpError`.
- `decode_chunked(body)` decodes `<hex size> CRLF <data> CRLF ...` up to a
  zero-size chunk. Any parameters after a `;` on the size line are ignored.
  A bad size, a chunk not followed by CRLF, or a truncated body is an
  `HttpError`.
- `parse_request(raw)` returns
  `{"method", "target", "version", "headers", "body"}`. The request line has
  exactly three space-separated tokens; the method must be alphabetic and
  upper case; the version must start with `HTTP/`; the target must start with
  `/` or be `*`.
- `parse_response(raw)` returns
  `{"version", "status", "reason", "headers", "body"}` with `status` an int.
  A missing reason phrase gives `""`.

Both take the body from `Transfer-Encoding: chunked` when present, else from
`Content-Length` (an integer, and the body must be at least that long — a
longer body is truncated to it), else the body is `b""`.

## Part 2 — a recursive resolver

- `NameServer(name, records=None, referrals=None)`. `records` maps a full name
  to either an address string or a `("CNAME", target)` tuple. `referrals` maps
  a zone to the name of the server that owns it. `referral_for(name)` returns
  the server for the **longest** zone that `name` equals or ends with
  (`".", zone`), else `None`.
- `Resolver(servers, root="root", ttl=30)` with `resolve(name)` returning
  `(address, trace)`, where `trace` lists the servers queried in order. Start
  at the root and follow referrals until a server holds the record. A
  `("CNAME", target)` is followed by resolving `target` and appending its
  trace. No record and no referral raises `NXDomain` (a `LookupError`); a
  chain deeper than 8 raises `ResolutionError`.
- Answers are cached until `clock + ttl`. A live cache hit returns
  `(address, ["cache"])` and queries nobody. `tick(seconds)` advances the
  logical clock, and an entry whose expiry is no longer in the future is stale.
''',
                "files": [{"name": "main.py", "content": r'''
CRLF = b"\r\n"


class HttpError(ValueError):
    """Raised when a message does not follow the HTTP/1.1 grammar."""


class NXDomain(LookupError):
    """Raised when no server in the hierarchy can name an address."""


class ResolutionError(RuntimeError):
    """Raised when resolution cannot terminate."""


def split_head(raw):
    """(head, body) around the first blank line."""
    # your code here


def parse_headers(lines):
    """Lowercased field names to stripped values, repeats joined with a comma."""
    # your code here


def decode_chunked(body):
    """The bytes carried by a chunked body."""
    # your code here


def extract_body(headers, body):
    """The message body implied by the framing headers."""
    # your code here


def parse_request(raw):
    """method, target, version, headers and body of a request."""
    # your code here


def parse_response(raw):
    """version, status, reason, headers and body of a response."""
    # your code here


class NameServer:
    """One server in the hierarchy: some records, some delegations."""

    def __init__(self, name, records=None, referrals=None):
        self.name = name
        self.records = dict(records or {})
        self.referrals = dict(referrals or {})

    def referral_for(self, name):
        """The server owning the longest matching zone, or None."""
        # your code here


class Resolver:
    """A recursive resolver with a TTL cache over a logical clock."""

    def __init__(self, servers, root="root", ttl=30):
        self.servers = dict(servers)
        self.root = root
        self.ttl = ttl
        self.clock = 0
        self.cache = {}

    def tick(self, seconds=1):
        """Advance the logical clock and return it."""
        # your code here

    def resolve(self, name, _depth=0):
        """(address, trace) for a name, walking down from the root."""
        # your code here


REQUEST = (b"POST /api/orders HTTP/1.1\r\nHost: shop.example.com\r\n"
           b"Content-Length: 15\r\nX-Tag: a\r\nX-Tag: b\r\n\r\n"
           b'{"units": 4711}')
print(parse_request(REQUEST))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
CRLF = b"\r\n"


class HttpError(ValueError):
    """Raised when a message does not follow the HTTP/1.1 grammar."""


class NXDomain(LookupError):
    """Raised when no server in the hierarchy can name an address."""


class ResolutionError(RuntimeError):
    """Raised when resolution cannot terminate."""


def split_head(raw):
    """(head, body) around the first blank line."""
    marker = raw.find(CRLF + CRLF)
    if marker == -1:
        raise HttpError("no blank line between the headers and the body")
    return raw[:marker], raw[marker + 4:]


def parse_headers(lines):
    """Lowercased field names to stripped values, repeats joined with a comma."""
    headers = {}
    for line in lines:
        if b":" not in line:
            raise HttpError("header line without a colon: " + repr(line))
        raw_name, _, raw_value = line.partition(b":")
        name = raw_name.decode("latin-1")
        if not name or name != name.strip():
            raise HttpError("bad header field name: " + repr(name))
        key = name.lower()
        value = raw_value.decode("latin-1").strip()
        headers[key] = headers[key] + ", " + value if key in headers else value
    return headers


def decode_chunked(body):
    """The bytes carried by a chunked body."""
    out = bytearray()
    index = 0
    while True:
        end = body.find(CRLF, index)
        if end == -1:
            raise HttpError("chunk size line is not terminated")
        field = body[index:end].split(b";")[0].strip()
        try:
            size = int(field, 16)
        except ValueError:
            raise HttpError("bad chunk size: " + repr(field))
        if size < 0:
            raise HttpError("negative chunk size")
        index = end + 2
        if size == 0:
            return bytes(out)
        if index + size + 2 > len(body):
            raise HttpError("chunk body is truncated")
        if body[index + size:index + size + 2] != CRLF:
            raise HttpError("chunk is not terminated by CRLF")
        out += body[index:index + size]
        index += size + 2


def extract_body(headers, body):
    """The message body implied by the framing headers."""
    if headers.get("transfer-encoding", "").lower() == "chunked":
        return decode_chunked(body)
    if "content-length" in headers:
        field = headers["content-length"]
        if not field.isdigit():
            raise HttpError("Content-Length is not a number: " + repr(field))
        length = int(field)
        if len(body) < length:
            raise HttpError("body is shorter than Content-Length")
        return body[:length]
    return b""


def parse_request(raw):
    """method, target, version, headers and body of a request."""
    head, body = split_head(raw)
    lines = head.split(CRLF)
    parts = lines[0].split(b" ")
    if len(parts) != 3:
        raise HttpError("malformed request line: " + repr(lines[0]))
    method, target, version = (part.decode("latin-1") for part in parts)
    if not method.isalpha() or method != method.upper():
        raise HttpError("bad method: " + repr(method))
    if not target.startswith("/") and target != "*":
        raise HttpError("bad request target: " + repr(target))
    if not version.startswith("HTTP/"):
        raise HttpError("bad version: " + repr(version))
    headers = parse_headers(lines[1:])
    return {"method": method, "target": target, "version": version,
            "headers": headers, "body": extract_body(headers, body)}


def parse_response(raw):
    """version, status, reason, headers and body of a response."""
    head, body = split_head(raw)
    lines = head.split(CRLF)
    parts = lines[0].split(b" ", 2)
    if len(parts) < 2:
        raise HttpError("malformed status line: " + repr(lines[0]))
    version = parts[0].decode("latin-1")
    if not version.startswith("HTTP/"):
        raise HttpError("bad version: " + repr(version))
    code = parts[1].decode("latin-1")
    if len(code) != 3 or not code.isdigit():
        raise HttpError("bad status code: " + repr(code))
    reason = parts[2].decode("latin-1") if len(parts) == 3 else ""
    headers = parse_headers(lines[1:])
    return {"version": version, "status": int(code), "reason": reason,
            "headers": headers, "body": extract_body(headers, body)}


class NameServer:
    """One server in the hierarchy: some records, some delegations."""

    def __init__(self, name, records=None, referrals=None):
        self.name = name
        self.records = dict(records or {})
        self.referrals = dict(referrals or {})

    def referral_for(self, name):
        """The server owning the longest matching zone, or None."""
        best = None
        for zone, server in self.referrals.items():
            if name == zone or name.endswith("." + zone):
                if best is None or len(zone) > len(best[0]):
                    best = (zone, server)
        return best[1] if best else None


class Resolver:
    """A recursive resolver with a TTL cache over a logical clock."""

    def __init__(self, servers, root="root", ttl=30):
        self.servers = dict(servers)
        self.root = root
        self.ttl = ttl
        self.clock = 0
        self.cache = {}

    def tick(self, seconds=1):
        """Advance the logical clock and return it."""
        self.clock += seconds
        return self.clock

    def resolve(self, name, _depth=0):
        """(address, trace) for a name, walking down from the root."""
        if _depth > 8:
            raise ResolutionError("alias chain too long for " + repr(name))
        cached = self.cache.get(name)
        if cached is not None and cached[1] > self.clock:
            return cached[0], ["cache"]
        trace = []
        server = self.servers[self.root]
        while True:
            trace.append(server.name)
            if name in server.records:
                value = server.records[name]
                if isinstance(value, tuple):
                    address, rest = self.resolve(value[1], _depth + 1)
                    self.cache[name] = (address, self.clock + self.ttl)
                    return address, trace + rest
                self.cache[name] = (value, self.clock + self.ttl)
                return value, trace
            nxt = server.referral_for(name)
            if nxt is None:
                raise NXDomain(name)
            server = self.servers[nxt]


REQUEST = (b"POST /api/orders HTTP/1.1\r\nHost: shop.example.com\r\n"
           b"Content-Length: 15\r\nX-Tag: a\r\nX-Tag: b\r\n\r\n"
           b'{"units": 4711}')
print(parse_request(REQUEST))
'''}],
                "hints": [
                    "`raw.find(b'\\r\\n\\r\\n')` locates the head/body boundary; everything four bytes past it is the body.",
                    "`line.partition(b':')` splits a header at the first colon and leaves colons in the value alone — which matters for `Host: a:8080`.",
                    "The chunk loop reads a size line, then exactly that many bytes, then the CRLF that follows them; a size of 0 ends the body.",
                    "For the resolver, keep the walk a `while True` over servers: answer, or refer, or NXDomain — and cache only once you have an address.",
                ],
                "tests": [
                    {"name": "A request parses into its parts", "code": r'''
_raw = (b"POST /api/orders HTTP/1.1\r\nHost: shop.example.com\r\n"
        b"Content-Length: 15\r\nX-Tag: a\r\nX-Tag: b\r\n\r\n"
        b'{"units": 4711}')
_got = parse_request(_raw)
assert _got["method"] == "POST" and _got["target"] == "/api/orders", f"Got {_got!r}"
assert _got["version"] == "HTTP/1.1", f"version was {_got['version']!r}"
assert _got["headers"]["host"] == "shop.example.com", "field names are lowercased and values stripped"
assert _got["headers"]["x-tag"] == "a, b", f"repeated fields join with a comma, got {_got['headers']['x-tag']!r}"
assert _got["body"] == b'{"units": 4711}', f"body was {_got['body']!r}"
_bare = parse_request(b"GET / HTTP/1.1\r\nHost: x\r\n\r\n")
assert _bare["body"] == b"", f"no framing header means an empty body, got {_bare['body']!r}"
'''},
                    {"name": "Malformed requests are refused", "code": r'''
for _bad in [b"GET / HTTP/1.1\r\nHost: x\r\n",
             b"GET /\r\n\r\n",
             b"GET / HTTP/1.1 extra\r\n\r\n",
             b"get / HTTP/1.1\r\n\r\n",
             b"GET / SPDY/1.1\r\n\r\n",
             b"GET index.html HTTP/1.1\r\n\r\n",
             b"GET / HTTP/1.1\r\nBroken\r\n\r\n",
             b"GET / HTTP/1.1\r\nHost : x\r\n\r\n",
             b"GET / HTTP/1.1\r\nContent-Length: ten\r\n\r\nabc",
             b"GET / HTTP/1.1\r\nContent-Length: 99\r\n\r\nabc"]:
    try:
        parse_request(_bad)
        assert False, f"parse_request({_bad!r}) should raise HttpError"
    except HttpError:
        pass
assert issubclass(HttpError, ValueError), "HttpError should be a ValueError"
'''},
                    {"name": "Responses, with and without a reason phrase", "code": r'''
_got = parse_response(b"HTTP/1.1 404 Not Found\r\nContent-Length: 3\r\n\r\nabcXX")
assert (_got["status"], _got["reason"]) == (404, "Not Found"), f"Got {(_got['status'], _got['reason'])!r}"
assert _got["status"] == 404 and isinstance(_got["status"], int), "status comes back as an int"
assert _got["body"] == b"abc", f"the body is truncated to Content-Length, got {_got['body']!r}"
assert parse_response(b"HTTP/1.1 204\r\n\r\n")["reason"] == "", "a missing reason phrase is an empty string"
for _bad in [b"HTTP/1.1\r\n\r\n", b"HTTP/1.1 20 OK\r\n\r\n", b"HTTP/1.1 abc OK\r\n\r\n",
             b"ICY 200 OK\r\n\r\n"]:
    try:
        parse_response(_bad)
        assert False, f"parse_response({_bad!r}) should raise HttpError"
    except HttpError:
        pass
'''},
                    {"name": "Chunked bodies decode and validate", "code": r'''
_body = b"7\r\nMozilla\r\n9\r\nDeveloper\r\n7\r\nNetwork\r\n0\r\n\r\n"
assert decode_chunked(_body) == b"MozillaDeveloperNetwork", f"Got {decode_chunked(_body)!r}"
assert decode_chunked(b"0\r\n\r\n") == b"", "a body of only the final chunk is empty"
assert decode_chunked(b"3;ext=1\r\nabc\r\n0\r\n\r\n") == b"abc", "chunk extensions after ';' are ignored"
assert decode_chunked(b"A\r\n0123456789\r\n0\r\n\r\n") == b"0123456789", "sizes are hexadecimal"
for _bad in [b"zz\r\nabc\r\n0\r\n\r\n", b"3\r\nabcd\r\n0\r\n\r\n", b"9\r\nabc\r\n0\r\n\r\n", b"3"]:
    try:
        decode_chunked(_bad)
        assert False, f"decode_chunked({_bad!r}) should raise HttpError"
    except HttpError:
        pass
_resp = parse_response(b"HTTP/1.1 200 OK\r\nTransfer-Encoding: chunked\r\n\r\n" + _body)
assert _resp["body"] == b"MozillaDeveloperNetwork", f"Got {_resp['body']!r}"
'''},
                    {"name": "Referrals pick the longest matching zone", "code": r'''
_ns = NameServer("gtld", referrals={"com": "com-ns", "example.com": "example-ns"})
assert _ns.referral_for("www.example.com") == "example-ns", \
    f"the longest zone wins, got {_ns.referral_for('www.example.com')!r}"
assert _ns.referral_for("other.com") == "com-ns", f"Got {_ns.referral_for('other.com')!r}"
assert _ns.referral_for("example.com") == "example-ns", "a name equal to the zone matches it"
assert _ns.referral_for("notexample.com") == "com-ns", \
    "a suffix must fall on a label boundary, not mid-label"
assert _ns.referral_for("example.org") is None, "no matching zone gives None"
'''},
                    {"name": "Resolution walks the hierarchy", "code": r'''
_servers = {
    "root": NameServer("root", referrals={"com": "com-gtld", "org": "org-gtld"}),
    "com-gtld": NameServer("com-gtld", referrals={"example.com": "ns.example.com",
                                                  "cdn.com": "ns.cdn.com"}),
    "org-gtld": NameServer("org-gtld", referrals={"ietf.org": "ns.ietf.org"}),
    "ns.example.com": NameServer("ns.example.com", records={
        "example.com": "93.184.216.34",
        "www.example.com": ("CNAME", "static.cdn.com")}),
    "ns.cdn.com": NameServer("ns.cdn.com", records={"static.cdn.com": "203.0.113.9"}),
    "ns.ietf.org": NameServer("ns.ietf.org", records={"ietf.org": "104.16.44.99"}),
}
_r = Resolver(_servers)
assert _r.resolve("ietf.org") == ("104.16.44.99", ["root", "org-gtld", "ns.ietf.org"]), \
    f"Got {_r.resolve('ietf.org')!r}"
_r2 = Resolver(_servers)
assert _r2.resolve("example.com") == ("93.184.216.34", ["root", "com-gtld", "ns.example.com"]), \
    f"Got {_r2.resolve('example.com')!r}"
_r3 = Resolver(_servers)
_address, _trace = _r3.resolve("www.example.com")
assert _address == "203.0.113.9", f"the alias should resolve to the target address, got {_address!r}"
assert _trace == ["root", "com-gtld", "ns.example.com", "root", "com-gtld", "ns.cdn.com"], \
    f"the alias trace should continue into the second walk, got {_trace!r}"
for _bad in ["nope.invalid", "missing.example.com"]:
    try:
        Resolver(_servers).resolve(_bad)
        assert False, f"resolve({_bad!r}) should raise NXDomain"
    except NXDomain:
        pass
'''},
                    {"name": "The cache answers, and then expires", "code": r'''
_servers = {
    "root": NameServer("root", referrals={"org": "org-gtld"}),
    "org-gtld": NameServer("org-gtld", referrals={"ietf.org": "ns.ietf.org"}),
    "ns.ietf.org": NameServer("ns.ietf.org", records={"ietf.org": "104.16.44.99"}),
}
_r = Resolver(_servers, ttl=30)
_first = _r.resolve("ietf.org")
assert _first[1] == ["root", "org-gtld", "ns.ietf.org"], f"the first lookup walks: {_first[1]!r}"
assert _r.resolve("ietf.org") == ("104.16.44.99", ["cache"]), \
    f"a warm cache answers without querying, got {_r.resolve('ietf.org')!r}"
assert _r.tick(29) == 29, "tick returns the new clock"
assert _r.resolve("ietf.org")[1] == ["cache"], "the entry is still live one second before expiry"
_r.tick(1)
assert _r.resolve("ietf.org")[1] == ["root", "org-gtld", "ns.ietf.org"], \
    "at the expiry instant the entry is stale and must be fetched again"
'''},
                    {"name": "An alias loop is stopped", "code": r'''
_looping = {
    "root": NameServer("root", referrals={"test": "ns.test"}),
    "ns.test": NameServer("ns.test", records={"a.test": ("CNAME", "b.test"),
                                              "b.test": ("CNAME", "a.test")}),
}
try:
    Resolver(_looping).resolve("a.test")
    assert False, "a CNAME loop should raise ResolutionError, not recurse for ever"
except ResolutionError:
    pass
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a layered stack delivering a message end to end",
        "runtime": "python",
        "minutes": 280,
        "brief": r'''
Assemble the whole course into one stack and push a message across a multi-hop
network that loses and corrupts frames. Two files: `stack.py` holds the layers
and is what the checks import; `main.py` drives a demo.

## Link layer — framing with an integrity trailer

`FLAG = 0x7E`, `ESC = 0x7D`, `MASK = 0x20`, CRC polynomial `0xEDB88320`.

- `crc32(data)` — the standard reflected CRC-32, table driven.
- `frame(seq, payload)` — build the body as one sequence byte, then the
  payload, then the CRC-32 **of that body so far** as four big-endian bytes;
  byte-stuff the whole body and wrap it in flags. A `seq` outside `0..255`
  raises `ValueError`.
- `deframe(raw)` — `(seq, payload)` for an intact frame, and `None` for
  anything damaged: bad framing, a body under five bytes, or a CRC mismatch.
  It never raises on corrupt input; a receiver simply discards.
- `FramingError(ValueError)` is raised by the internal unstuffing step.

## Network layer — topology and routing

`Topology(links)` where `links` is `{(a, b): cost}`, undirected. `route(source,
dest)` returns the cheapest node-by-node path using Dijkstra, visiting
neighbours in sorted order for reproducible ties, and raises
`UnreachableError` (a `LookupError`) for an unknown or unreachable node.

## The medium

`Network(topology, drop_hops=(), corrupt_hops=())`. Every **hop** of every
delivery is one numbered event, counted in `network.hops` from zero.
`deliver(path, raw)` walks `raw` along `path`:

```text
for each of the len(path) - 1 hops:
    index = self.hops; self.hops += 1
    if index in drop_hops:    return None
    if index in corrupt_hops: raw = raw[:1] + bytes([raw[1] ^ 0x01]) + raw[2:]
return raw
```

## Transport — stop-and-wait over the path

`chunk(data, size)` splits bytes into pieces of at most `size` (a size under 1
raises `ValueError`). `send_message(network, source, dest, message,
chunk_size=4)` routes once, splits the UTF-8 encoding of `message`, and for
each piece:

```text
seq = index % 2
loop:
    data_frames += 1
    arrived = network.deliver(path, frame(seq, piece))
    parsed  = deframe(arrived) if arrived is not None else None
    if parsed is None: continue                  # lost or damaged: resend
    got_seq, payload = parsed
    if got_seq == expected: append payload; expected ^= 1
    ack_frames += 1
    ack = network.deliver(reversed path, frame(got_seq, b""))
    if ack is not None and deframe(ack) is not None: break
```

More than `MAX_ATTEMPTS` (200) attempts on one piece raises `RuntimeError`.
It returns `{"text", "path", "data_frames", "ack_frames", "retransmissions",
"hops"}`, where `retransmissions` is `data_frames - len(pieces)` and `hops` is
the network's hop counter.
''',
        "deliverables": [
            "`stack.py` — link, network and transport layers, importable with no side effects",
            "`main.py` — a demo routing a message across the sample topology, clean and lossy",
            "A CRC-checked frame format whose receiver silently discards damage instead of raising",
            "Dijkstra-based routing that reports unreachable destinations rather than guessing",
            "A deterministic medium in which every hop is a numbered, reproducible event",
            "Stop-and-wait transport that reassembles the exact message under loss and corruption",
        ],
        "constraints": [
            "Standard library only — `heapq` is the only import you need",
            "No `zlib`: the CRC is yours to implement",
            "Importing `stack.py` must print nothing and open no files",
            "The transport layer may not inspect frame bytes directly — it goes through frame/deframe",
            "Every counter must be reproducible: no randomness anywhere in the stack",
        ],
        "rubric": [
            {"criterion": "Correctness", "weight": 40,
             "evidence": "Every automated check passes, including the empty message, single-hop and unreachable cases."},
            {"criterion": "Layering", "weight": 20,
             "evidence": "Framing, routing, the medium and the transport loop are separable; each is testable without the others."},
            {"criterion": "Error handling", "weight": 20,
             "evidence": "Corrupt frames are discarded rather than raised, unreachable routes raise UnreachableError, and a hopeless link fails loudly at MAX_ATTEMPTS."},
            {"criterion": "Determinism", "weight": 10,
             "evidence": "Identical inputs give identical hop, frame and retransmission counts on every run."},
            {"criterion": "Documented API", "weight": 10,
             "evidence": "Every public function and method carries a docstring stating its contract, including what it returns on damage."},
        ],
        "hints": [
            "Build upwards and test each layer alone: framing first, then routing, then the medium, and only then the transport loop.",
            "`deframe` must catch its own FramingError and return None — the whole point is that a receiver discards damage silently.",
            "The corruption flips a bit in the sequence byte, so the CRC is what catches it; put the CRC over the sequence byte as well as the payload.",
            "Count a data frame on every attempt, but an ack frame only when a data frame actually arrived — that asymmetry is what makes the counters reproducible.",
        ],
        "files": [
            {"name": "stack.py", "content": r'''
import heapq

FLAG = 0x7E
ESC = 0x7D
MASK = 0x20
CRC_POLY = 0xEDB88320
MAX_ATTEMPTS = 200


class FramingError(ValueError):
    """Raised when a byte sequence is not a well-formed frame."""


class UnreachableError(LookupError):
    """Raised when the topology offers no path between two nodes."""


def crc32(data):
    """The reflected CRC-32 of data, as an unsigned 32-bit integer."""


def frame(seq, payload):
    """seq byte + payload + CRC-32 trailer, byte-stuffed between two flags."""


def deframe(raw):
    """(seq, payload) for an intact frame, or None when it is damaged."""


class Topology:
    """An undirected weighted graph with shortest-path routing."""

    def __init__(self, links):
        self.graph = {}

    def route(self, source, dest):
        """The cheapest node-by-node path, or UnreachableError."""


class Network:
    """A deterministic medium. Every hop is one numbered transmission event."""

    def __init__(self, topology, drop_hops=(), corrupt_hops=()):
        self.topology = topology
        self.drop_hops = set(drop_hops)
        self.corrupt_hops = set(corrupt_hops)
        self.hops = 0

    def deliver(self, path, raw):
        """Walk raw along path hop by hop; None when a hop drops it."""


def chunk(data, size):
    """data split into consecutive pieces of at most size bytes."""


def send_message(network, source, dest, message, chunk_size=4):
    """Deliver message end to end with stop-and-wait; text plus counters."""
'''},
            {"name": "main.py", "content": r'''
from stack import Network, Topology, send_message

LINKS = {
    ("host-a", "r1"): 1,
    ("r1", "r2"): 2,
    ("r1", "r3"): 5,
    ("r2", "r3"): 1,
    ("r3", "host-b"): 1,
    ("r2", "host-b"): 9,
}

topology = Topology(LINKS)

# route the message across a clean network, then across a lossy one,
# and print the path, the text that arrived and the counters
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "stack.py", "content": r'''
import heapq

FLAG = 0x7E
ESC = 0x7D
MASK = 0x20
CRC_POLY = 0xEDB88320
MAX_ATTEMPTS = 200


class FramingError(ValueError):
    """Raised when a byte sequence is not a well-formed frame."""


class UnreachableError(LookupError):
    """Raised when the topology offers no path between two nodes."""


def _crc_table():
    """The 256-entry reflected CRC-32 table, built once at import time."""
    table = []
    for index in range(256):
        value = index
        for _ in range(8):
            value = (value >> 1) ^ (CRC_POLY if value & 1 else 0)
        table.append(value)
    return tuple(table)


CRC_TABLE = _crc_table()


def crc32(data):
    """The reflected CRC-32 of data, as an unsigned 32-bit integer."""
    crc = 0xFFFFFFFF
    for byte in data:
        crc = CRC_TABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF


def _unstuff(raw):
    """The body between the flags with escapes resolved; FramingError on damage."""
    if len(raw) < 2 or raw[0] != FLAG or raw[-1] != FLAG:
        raise FramingError("a frame starts and ends with a flag")
    body = raw[1:-1]
    out = bytearray()
    index = 0
    while index < len(body):
        byte = body[index]
        if byte == FLAG:
            raise FramingError("unescaped flag inside a frame")
        if byte == ESC:
            if index + 1 >= len(body):
                raise FramingError("dangling escape at the end of a frame")
            out.append(body[index + 1] ^ MASK)
            index += 2
            continue
        out.append(byte)
        index += 1
    return bytes(out)


def frame(seq, payload):
    """seq byte + payload + CRC-32 trailer, byte-stuffed between two flags."""
    if not 0 <= seq <= 255:
        raise ValueError("seq must fit in one byte")
    body = bytes([seq]) + bytes(payload)
    body = body + crc32(body).to_bytes(4, "big")
    stuffed = bytearray()
    for byte in body:
        if byte in (FLAG, ESC):
            stuffed.append(ESC)
            stuffed.append(byte ^ MASK)
        else:
            stuffed.append(byte)
    return bytes([FLAG]) + bytes(stuffed) + bytes([FLAG])


def deframe(raw):
    """(seq, payload) for an intact frame, or None when it is damaged."""
    try:
        body = _unstuff(raw)
    except FramingError:
        return None
    if len(body) < 5:
        return None
    protected, trailer = body[:-4], body[-4:]
    if crc32(protected) != int.from_bytes(trailer, "big"):
        return None
    return protected[0], protected[1:]


class Topology:
    """An undirected weighted graph with shortest-path routing."""

    def __init__(self, links):
        self.graph = {}
        for (left, right), weight in links.items():
            self.graph.setdefault(left, {})[right] = weight
            self.graph.setdefault(right, {})[left] = weight

    def route(self, source, dest):
        """The cheapest node-by-node path, or UnreachableError."""
        if source not in self.graph or dest not in self.graph:
            raise UnreachableError(f"unknown node in {source!r} -> {dest!r}")
        dist = {node: float("inf") for node in self.graph}
        prev = {node: None for node in self.graph}
        dist[source] = 0
        seen = set()
        queue = [(0, source)]
        while queue:
            cost, node = heapq.heappop(queue)
            if node in seen:
                continue
            seen.add(node)
            for neighbour, weight in sorted(self.graph[node].items()):
                if cost + weight < dist[neighbour]:
                    dist[neighbour] = cost + weight
                    prev[neighbour] = node
                    heapq.heappush(queue, (cost + weight, neighbour))
        if dist[dest] == float("inf"):
            raise UnreachableError(f"no path from {source!r} to {dest!r}")
        path = [dest]
        while path[-1] != source:
            path.append(prev[path[-1]])
        return list(reversed(path))


class Network:
    """A deterministic medium. Every hop is one numbered transmission event."""

    def __init__(self, topology, drop_hops=(), corrupt_hops=()):
        self.topology = topology
        self.drop_hops = set(drop_hops)
        self.corrupt_hops = set(corrupt_hops)
        self.hops = 0

    def deliver(self, path, raw):
        """Walk raw along path hop by hop; None when a hop drops it."""
        for _ in range(len(path) - 1):
            index = self.hops
            self.hops += 1
            if index in self.drop_hops:
                return None
            if index in self.corrupt_hops:
                raw = raw[:1] + bytes([raw[1] ^ 0x01]) + raw[2:]
        return raw


def chunk(data, size):
    """data split into consecutive pieces of at most size bytes."""
    if size < 1:
        raise ValueError("chunk size must be at least 1")
    return [data[start:start + size] for start in range(0, len(data), size)]


def send_message(network, source, dest, message, chunk_size=4):
    """Deliver message end to end with stop-and-wait; text plus counters."""
    path = network.topology.route(source, dest)
    back = list(reversed(path))
    pieces = chunk(message.encode("utf-8"), chunk_size)
    received = bytearray()
    expected = 0
    data_frames = 0
    ack_frames = 0
    for index, piece in enumerate(pieces):
        seq = index % 2
        attempts = 0
        while True:
            attempts += 1
            if attempts > MAX_ATTEMPTS:
                raise RuntimeError("the link never delivered this piece")
            data_frames += 1
            arrived = network.deliver(path, frame(seq, piece))
            parsed = deframe(arrived) if arrived is not None else None
            if parsed is None:
                continue
            got_seq, payload = parsed
            if got_seq == expected:
                received += payload
                expected ^= 1
            ack_frames += 1
            ack = network.deliver(back, frame(got_seq, b""))
            if ack is not None and deframe(ack) is not None:
                break
    return {"text": received.decode("utf-8"), "path": path,
            "data_frames": data_frames, "ack_frames": ack_frames,
            "retransmissions": data_frames - len(pieces), "hops": network.hops}
'''},
            {"name": "main.py", "content": r'''
from stack import Network, Topology, deframe, frame, send_message

LINKS = {
    ("host-a", "r1"): 1,
    ("r1", "r2"): 2,
    ("r1", "r3"): 5,
    ("r2", "r3"): 1,
    ("r3", "host-b"): 1,
    ("r2", "host-b"): 9,
}

topology = Topology(LINKS)
print("route:", topology.route("host-a", "host-b"))

clean = Network(topology)
print("clean:", send_message(clean, "host-a", "host-b", "hello networks", 4))

lossy = Network(topology, drop_hops={2, 3, 11}, corrupt_hops={17})
print("lossy:", send_message(lossy, "host-a", "host-b", "hello networks", 4))

sample = frame(1, b"abc")
print("frame:", sample.hex(), deframe(sample))
print("damaged:", deframe(sample[:1] + bytes([sample[1] ^ 0x01]) + sample[2:]))
'''},
        ],
        "tests": [
            {"name": "The CRC matches the standard check values", "code": r'''
from stack import crc32
assert crc32(b"") == 0, f"crc32(b'') gave {crc32(b'')!r}, expected 0"
assert crc32(b"123456789") == 0xCBF43926, f"crc32 of the check string gave {hex(crc32(b'123456789'))}"
assert crc32(b"hello world") == 0x0D4A1185, f"Got {hex(crc32(b'hello world'))}"
'''},
            {"name": "Frames round-trip, including the reserved bytes", "code": r'''
from stack import FLAG, deframe, frame
for _seq in (0, 1, 255):
    for _payload in [b"", b"abc", b"\x7e\x7d", bytes(range(64))]:
        _got = deframe(frame(_seq, _payload))
        assert _got == (_seq, _payload), f"frame/deframe of ({_seq}, {_payload!r}) gave {_got!r}"
_f = frame(1, b"abc")
assert _f[0] == FLAG and _f[-1] == FLAG, "a frame is delimited by flags"
assert FLAG not in _f[1:-1], "the body must not contain a bare flag byte"
try:
    frame(256, b"x")
    assert False, "a sequence number outside 0..255 should raise ValueError"
except ValueError:
    pass
'''},
            {"name": "Damage is discarded, not raised", "code": r'''
from stack import deframe, frame
_f = frame(0, b"payload")
for _bad in [b"", b"\x7e", b"abc", _f[1:], _f[:-1],
             _f[:1] + bytes([_f[1] ^ 0x01]) + _f[2:],
             _f[:-2] + bytes([_f[-2] ^ 0x80]) + _f[-1:]]:
    _got = deframe(_bad)
    assert _got is None, f"deframe({_bad!r}) gave {_got!r}, expected None"
assert deframe(frame(0, b"payload")) == (0, b"payload"), "an intact frame still parses"
'''},
            {"name": "Routing takes the cheapest path", "code": r'''
from stack import Topology, UnreachableError
_links = {("host-a", "r1"): 1, ("r1", "r2"): 2, ("r1", "r3"): 5,
          ("r2", "r3"): 1, ("r3", "host-b"): 1, ("r2", "host-b"): 9}
_t = Topology(_links)
assert _t.route("host-a", "host-b") == ["host-a", "r1", "r2", "r3", "host-b"], \
    f"Got {_t.route('host-a', 'host-b')!r}"
assert _t.route("host-a", "host-a") == ["host-a"], "a node routes to itself in one step"
assert _t.route("host-b", "host-a") == ["host-b", "r3", "r2", "r1", "host-a"], \
    f"the reverse path should mirror the forward one, got {_t.route('host-b', 'host-a')!r}"
assert _t.route("r1", "r3") == ["r1", "r2", "r3"], \
    f"2+1 beats the direct link of 5, got {_t.route('r1', 'r3')!r}"
for _pair in [("host-a", "nowhere"), ("nowhere", "host-a")]:
    try:
        _t.route(*_pair)
        assert False, f"route{_pair!r} should raise UnreachableError"
    except UnreachableError:
        pass
_island = Topology({("a", "b"): 1, ("c", "d"): 1})
try:
    _island.route("a", "d")
    assert False, "two disconnected components should raise UnreachableError"
except UnreachableError:
    pass
'''},
            {"name": "The medium counts hops and applies its events", "code": r'''
from stack import Network, Topology, deframe, frame
_t = Topology({("a", "b"): 1, ("b", "c"): 1})
_path = _t.route("a", "c")
assert _path == ["a", "b", "c"], f"Got {_path!r}"
_clean = Network(_t)
_raw = frame(0, b"hi")
assert _clean.deliver(_path, _raw) == _raw, "a clean medium delivers the bytes unchanged"
assert _clean.hops == 2, f"a two-hop path costs 2 events, got {_clean.hops!r}"
_lossy = Network(_t, drop_hops={0})
assert _lossy.deliver(_path, _raw) is None, "a dropping hop returns None"
assert _lossy.hops == 1, f"the walk stops at the drop, so hops is {_lossy.hops!r}, expected 1"
_bad = Network(_t, corrupt_hops={1})
_damaged = _bad.deliver(_path, _raw)
assert _damaged is not None and _damaged != _raw, "a corrupting hop delivers different bytes"
assert deframe(_damaged) is None, "the CRC must catch the corruption the medium introduced"
assert _bad.hops == 2, f"corruption does not stop the walk, hops was {_bad.hops!r}"
'''},
            {"name": "chunk splits without losing bytes", "code": r'''
from stack import chunk
assert chunk(b"abcdefg", 3) == [b"abc", b"def", b"g"], f"Got {chunk(b'abcdefg', 3)!r}"
assert chunk(b"", 4) == [], "no data means no pieces"
assert chunk(b"ab", 10) == [b"ab"], "a short message is one piece"
assert b"".join(chunk(bytes(range(50)), 7)) == bytes(range(50)), "chunking must be lossless"
for _bad in (0, -1):
    try:
        chunk(b"abc", _bad)
        assert False, f"chunk size {_bad} should raise ValueError"
    except ValueError:
        pass
'''},
            {"name": "End to end across a clean network", "code": r'''
from stack import Network, Topology, send_message
_t = Topology({("host-a", "r1"): 1, ("r1", "r2"): 2, ("r1", "r3"): 5,
               ("r2", "r3"): 1, ("r3", "host-b"): 1, ("r2", "host-b"): 9})
_net = Network(_t)
_r = send_message(_net, "host-a", "host-b", "hello networks", 4)
assert _r["text"] == "hello networks", f"the message arrived as {_r['text']!r}"
assert _r["path"] == ["host-a", "r1", "r2", "r3", "host-b"], f"path was {_r['path']!r}"
assert (_r["data_frames"], _r["ack_frames"], _r["retransmissions"]) == (4, 4, 0), \
    f"clean counters were {(_r['data_frames'], _r['ack_frames'], _r['retransmissions'])!r}, expected (4, 4, 0)"
assert _r["hops"] == 32, f"8 deliveries over a 4-hop path is 32 events, got {_r['hops']!r}"
'''},
            {"name": "An empty message and a single hop", "code": r'''
from stack import Network, Topology, send_message
_t = Topology({("a", "b"): 1})
_net = Network(_t)
_r = send_message(_net, "a", "b", "", 4)
assert _r["text"] == "" and _r["data_frames"] == 0 and _r["hops"] == 0, f"Got {_r!r}"
_net2 = Network(_t)
_r2 = send_message(_net2, "a", "b", "ok", 4)
assert _r2["text"] == "ok" and _r2["path"] == ["a", "b"], f"Got {_r2!r}"
assert _r2["hops"] == 2, f"one data frame and one ack over one hop is 2 events, got {_r2['hops']!r}"
'''},
            {"name": "Loss and corruption cost retransmissions but not correctness", "code": r'''
from stack import Network, Topology, send_message
_t = Topology({("host-a", "r1"): 1, ("r1", "r2"): 2, ("r1", "r3"): 5,
               ("r2", "r3"): 1, ("r3", "host-b"): 1, ("r2", "host-b"): 9})
_net = Network(_t, drop_hops={2, 3, 11}, corrupt_hops={17})
_r = send_message(_net, "host-a", "host-b", "hello networks", 4)
assert _r["text"] == "hello networks", f"loss must not change the message, got {_r['text']!r}"
assert (_r["data_frames"], _r["ack_frames"], _r["retransmissions"]) == (8, 6, 4), \
    f"lossy counters were {(_r['data_frames'], _r['ack_frames'], _r['retransmissions'])!r}, expected (8, 6, 4)"
assert _r["hops"] == 52, f"hop count was {_r['hops']!r}, expected 52"
'''},
            {"name": "A duplicate is acknowledged but never delivered twice", "code": r'''
from stack import Network, Topology, send_message
_t = Topology({("a", "b"): 1})
_net = Network(_t, drop_hops={1})
_r = send_message(_net, "a", "b", "abcdefgh", 4)
assert _r["text"] == "abcdefgh", \
    f"the first ack was lost, so the first piece arrives twice — it must be delivered once: {_r['text']!r}"
assert _r["data_frames"] == 3, f"one retransmission means 3 data frames, got {_r['data_frames']!r}"
assert _r["retransmissions"] == 1, f"Got {_r['retransmissions']!r}"
'''},
            {"name": "A hopeless link fails loudly", "code": r'''
from stack import MAX_ATTEMPTS, Network, Topology, send_message
_t = Topology({("a", "b"): 1})
_net = Network(_t, drop_hops=set(range(MAX_ATTEMPTS + 10)))
try:
    send_message(_net, "a", "b", "never", 4)
    assert False, "a link that drops everything should raise RuntimeError, not loop for ever"
except RuntimeError:
    pass
'''},
            {"name": "stack.py is import-clean and standard-library only", "code": r'''
_src = open("stack.py").read()
assert "print(" not in _src, "stack.py is a library; the printing belongs in main.py"
assert "import zlib" not in _src and "from zlib" not in _src, "the CRC is yours to implement"
assert "random" not in _src, "the stack must be deterministic — no randomness anywhere"
'''},
        ],
    },
}
