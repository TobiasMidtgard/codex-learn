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
            "read": [
                {
                    "title": "Where one frame ends, and whether it arrived whole",
                    "minutes": 11,
                    "body": r'''
A serial cable carries bytes. Not messages, not packets — bytes, one after another,
with nothing between them. Send the word `hello` and then the word `world` down such a
cable and what comes out of the far end is `helloworld`, and the receiver has no way to
know there were two of anything. Every protocol that has ever run over a byte pipe has
had to solve this before it could do anything else, and the solution is the first thing
you will build in this module's lab, *Framing, checksums and CRC-32*.

## Reserving a byte

The first move anyone makes is to pick a byte value and declare it a boundary. PPP
picks `0x7E` and calls it the flag: every frame begins with one and ends with one, so
the receiver reads bytes until it sees a flag, and everything since the previous flag
is one frame.

That works right up to the first payload that happens to contain a `0x7E` of its own —
a binary file, a compressed image, a frame carrying another frame. The receiver would
cut the frame in half at the data byte, deliver the front half as a frame, and treat
the back half as the start of the next one. The moment one value carries meaning, data
holding that value has to be disguised, and the disguise is an escape byte: `0x7D`. A
`0x7E` inside the payload goes out as `0x7D` followed by `0x5E`, which is `0x7E` with
bit five cleared (`0x7E ^ 0x20`).

Why bit five, and not some other transformation? Two reasons, and both matter. First,
the byte that follows the escape must not itself be a flag or an escape, or the
receiver is back where it started; `0x5E` and `0x5D` are neither. Second, the escape
byte is now reserved too, so a payload containing `0x7D` must also be disguised — as
`0x7D 0x5D`. The mask is its own inverse, so the receiver has one rule for everything:
see `0x7D`, drop it, take the next byte, XOR it with `0x20`.

Take the payload `7e 7d 01` through that by hand. The first byte is a flag, so it
becomes `7d 5e`. The second is an escape, so it becomes `7d 5d`. The third is ordinary
and passes through. Wrap the result in flags and the frame on the wire is
`7e 7d 5e 7d 5d 01 7e`: three bytes of payload became seven bytes of frame.

```python
FLAG, ESC, MASK = 0x7E, 0x7D, 0x20


def stuff(payload):
    body = bytearray()
    for byte in payload:
        if byte in (FLAG, ESC):
            body += bytes([ESC, byte ^ MASK])
        else:
            body.append(byte)
    return bytes([FLAG]) + bytes(body) + bytes([FLAG])


def unstuff(frame):
    body = frame[1:-1]
    out = bytearray()
    i = 0
    while i < len(body):
        if body[i] == ESC:
            out.append(body[i + 1] ^ MASK)
            i += 2
        else:
            out.append(body[i])
            i += 1
    return bytes(out)


wire = stuff(b"\x7e\x7d\x01")
print(wire.hex(" "))
print(unstuff(wire) == b"\x7e\x7d\x01")
```

That prints `7e 7d 5e 7d 5d 01 7e` and then `True`. The `unstuff` here is the
optimistic half of the lab's version: it trusts its input. The lab's has to raise
`FramingError` for a frame with no flags, a bare flag in the middle, or an escape as the
very last byte of the body — because a receiver on a real wire sees all three, and a
parser that indexes `body[i + 1]` past the end of a frame is a crash waiting for the
first line glitch.

## What stuffing costs

Every escaped byte becomes two, so a payload of $n$ bytes goes out as somewhere between
$n$ and $2n$ bytes of body, plus the two flags. On ordinary data the expansion is small:
if each byte independently has probability $p$ of being one of the two reserved values,
the expected body length is $n(1 + p)$, and for random bytes $p = 2/256$ — under one
percent. The module's derivation unit walks that expression out. The number to remember
is the other one: $p$ is set by whoever is sending, and a payload of solid `7e` bytes
drives it to 1. A link budgeted for the average case has been halved by a sender who
read the specification.

The mistake people make here is to escape the flag and forget the escape. It is
tempting because `0x7D` does not look reserved — it never marks a boundary, so why
disguise it? Trace what happens to the payload `7d 5e` under that rule. The sender
leaves it alone: `7e 7d 5e 7e` goes on the wire. The receiver sees `7d`, treats it as an
escape, and decodes `7d 5e` as the single byte `7e`. Two bytes of payload became one,
silently, with no error anywhere. Escaping the escape is what makes the decoding rule a
function.

## Noticing damage

Framing tells the receiver where a frame is. It says nothing about whether the bytes
inside it are the ones that were sent, and on a real wire some of them will not be: a
bit flips in a noisy cable, a clock drifts, a connector corrodes. The receiver needs a
summary of the data that it can recompute and compare — a check.

The simplest useful check is a sum, and the internet's version of it, from RFC 1071, is
what every IP, TCP and UDP header still carries. Take the data two bytes at a time as
16-bit big-endian words and add them up — but add them in one's complement, which
means that whenever the sum overflows past 16 bits the carry is not thrown away; it is
added back in at the bottom. Then invert every bit of the result.

Run RFC 1071's own example through that. The bytes are `00 01 f2 03 f4 f5 f6 f7`, so
the words are `0x0001`, `0xF203`, `0xF4F5` and `0xF6F7`. The first two add to `0xF204`.
Adding `0xF4F5` gives `0x1E6F9`, which has overflowed; fold the carry back in and it is
`0xE6FA`. Adding `0xF6F7` gives `0x1DDF1`; fold again and it is `0xDDF2`. Invert every
bit and the checksum is `0x220D`, which is what the RFC prints and what the lab's first
checksum test demands.

Why the final inversion? It buys the receiver a shortcut. Add the data to its own
checksum and the sum is `0xDDF2 + 0x220D = 0xFFFF`, all ones, which inverts to zero. So
a receiver does not compare anything: it sums the whole frame, check included, and
looks for zero. That is the property the lab's checksum test exercises on four
different inputs.

```python
def internet_checksum(data):
    data = bytes(data) + (b"\x00" if len(data) % 2 else b"")
    total = 0
    for i in range(0, len(data), 2):
        total += (data[i] << 8) | data[i + 1]
        total = (total & 0xFFFF) + (total >> 16)
    return (~total) & 0xFFFF


sample = bytes.fromhex("0001f203f4f5f6f7")
check = internet_checksum(sample)
print(hex(check))
print(hex(internet_checksum(sample + check.to_bytes(2, "big"))))
print(hex(internet_checksum(b"\x12\x34\xab\xcd")), hex(internet_checksum(b"\xab\xcd\x12\x34")))
```

That prints `0x220d`, then `0x0`, then two identical values. The third line is the
checksum's weakness in one glance. It is a sum, and addition does not care what order
it adds things in, so two whole words exchanged with each other leave the check
untouched. The same blindness covers a subtler case: flip a bit from 0 to 1 in one word
and the same bit from 1 to 0 in another, and the total is unchanged. Two-bit errors are
exactly where the lab's `detection_rate` finds the checksum missing a few percent of
corruptions while the CRC misses none.

## A check that knows where things are

To catch reordering the check has to depend on position, and the way to make position
matter is to stop adding and start dividing. Treat the whole message as one enormous
binary number — or, what is the same thing over the two-element field, as a polynomial
whose coefficients are the bits, with the first bit as the highest power. Divide it by
a fixed generator polynomial and keep the remainder. Moving a bit changes which power
of $x$ it belongs to, so it changes the remainder.

Arithmetic in this field is XOR for addition and for subtraction, and there is no
carry, which makes long division short. Take the message `1101` and the generator
`1011`, which is $x^3 + x + 1$. The remainder will have three bits, so append three
zeros to the message to make room for it: `1101000`. Then repeatedly line the generator
up under the leftmost 1 and XOR.

```python
def crc_bits(message, generator):
    bits = [int(b) for b in message] + [0] * (len(generator) - 1)
    gen = [int(b) for b in generator]
    for i in range(len(message)):
        if bits[i] == 1:
            for j, g in enumerate(gen):
                bits[i + j] ^= g
            print("".join(map(str, bits)))
    return "".join(map(str, bits[-(len(generator) - 1):]))


print("remainder", crc_bits("1101", "1011"))
```

Each printed line is one step of the division; the remainder is `001`, so the sender
transmits `1101 001` and the receiver divides all seven bits and expects zero. Every
real CRC is this calculation with a longer generator and a lot of engineering on top.
CRC-32 uses a generator of degree 32, and the version everything uses — Ethernet, zip,
PNG, `zlib.crc32` — runs the bits through in reflected order, starts the register at
all ones, and inverts the result at the end. The all-ones start is not decoration: from
a zero register a run of leading zero bytes changes nothing, so `00 00 hello` and
`hello` would share a remainder.

A bit-at-a-time loop does eight shift-and-XOR steps per byte. Those eight steps depend
only on the low byte of the register XORed with the incoming byte — 256 possibilities —
so all of them can be computed once, into a table, and the per-byte work becomes one
lookup.

```python
CRC_POLY = 0xEDB88320


def make_table():
    table = []
    for index in range(256):
        value = index
        for _ in range(8):
            value = (value >> 1) ^ (CRC_POLY if value & 1 else 0)
        table.append(value)
    return table


TABLE = make_table()


def crc32(data):
    crc = 0xFFFFFFFF
    for byte in data:
        crc = TABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF


print(hex(crc32(b"123456789")))
print(hex(crc32(b"\x12\x34\xab\xcd")), hex(crc32(b"\xab\xcd\x12\x34")))
```

The first line is `0xcbf43926`, the published check value that every CRC-32
implementation on earth must produce for the string `123456789`; if yours prints
anything else, the lab's CRC test will tell you so. The second line is two different
numbers: the word swap the checksum could not see, seen.

## Where it stops

A CRC detects. It does not correct, and it cannot: 32 bits of remainder cannot point at
which of twelve thousand bits went wrong, because there are vastly more possible
corruptions than there are remainders. A frame whose check fails is discarded, and
whoever sent it finds out from the silence — which is the problem the next module takes
up. Nor does a CRC protect against an adversary. It is a linear function, so anyone who
can change the data can change the check to match; integrity against a person, rather
than against a cable, needs a keyed hash, and that is a different course.

Even against a cable the guarantee is bounded. A CRC-32 catches every single-bit error,
every burst of damage up to 32 bits long, and all but one in $2^{32}$ of the random
patterns beyond that. The internet checksum catches every single-bit error too, and
then a far smaller share of everything else — which is why the link layer beneath it
carries a CRC as well, and why the lab has you measure both on the same corruptions
rather than take either one's reputation on trust.
''',
                },
            ],
            "quiz": {
                "title": "Delimiters, and what a check can tell you",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Why does a PPP-style framer escape any payload byte that happens to equal `0x7E`?",
                        "opts": [
                            "So that the frame length stays even, which the checksum needs",
                            "So that a byte of data can never be read as the end of the frame",
                            "So that a flipped bit cannot turn a data byte into a flag",
                            "So that the payload compresses better on a slow link",
                        ],
                        "a": 1,
                        "why": r"""
Framing is a delimiter problem before it is anything else. The receiver has a byte
stream and no idea where the boundaries are, so one value is reserved to mean *here is
a boundary* — and the moment a value carries meaning, data holding that value has to be
disguised. That is all stuffing is.

Evenness belongs to the checksum, which pads for itself and does not care what the
framer did. Compression is the opposite of what happens: stuffing makes the frame
longer, never shorter. And stuffing offers no protection at all against a bit flip
that manufactures a flag out of ordinary data — that corruption sails straight into
the framer, which cuts the frame short; the CRC on the truncated frame is what catches
it afterwards.
""",
                    },
                    {
                        "q": "An $n$-byte payload is stuffed. In the worst case, how many bytes does the escaped body occupy, not counting the two flags?",
                        "opts": ["$n + 1$", "$n + 2$", "$2n$", "$n$"],
                        "a": 2,
                        "why": r"""
The worst case is a payload made entirely of `0x7E` and `0x7D`. Every single byte then
needs an escape in front of it, so every one byte in becomes two bytes out: $2n$.

A payload of ordinary text hits none of that — it comes out at exactly $n$, which is
what makes the doubling so easy to forget. The link still has to be sized for it,
because the payload is chosen by whoever is sending, and a sender who does not like
you can choose `7e 7e 7e 7e ...`.
""",
                    },
                    {
                        "q": "Which corruption slips past the internet checksum but is caught by CRC-32?",
                        "opts": [
                            "Two bits flipped inside the same byte",
                            "One bit flipped somewhere in the payload",
                            "One byte replaced by a different value",
                            "Two 16-bit words of the payload exchanged with each other",
                        ],
                        "a": 3,
                        "why": r"""
The checksum is a sum, and addition does not care what order it adds things in. Move
two whole 16-bit words past each other and the total is untouched, so the check passes
on data that is now wrong. CRC-32 is a polynomial remainder, and position is baked into
every term of it, so the swap changes the answer.

The other three all change some 16-bit word by a non-zero amount smaller than
$65535$, and the one's-complement sum is arithmetic modulo $65535$ — a change that
small cannot wrap all the way round to invisible. Both checks catch all of them. It is
specifically *rearrangement*, not damage, that the checksum is blind to.
""",
                    },
                    {
                        "q": "A frame arrives and its CRC does not match. What does the link layer do with it?",
                        "opts": [
                            "Drops it, and leaves recovery to a layer that has sequence numbers and timers",
                            "Repairs the damaged bits from the CRC and passes the frame up",
                            "Passes it up with a flag set, so the application can decide",
                            "Recomputes the CRC over what arrived and forwards the frame with the new value",
                        ],
                        "a": 0,
                        "why": r"""
A CRC detects; it does not correct. Thirty-two bits of remainder cannot locate an error
in a twelve-thousand-bit frame — there are far more possible corruptions than there are
remainders — so there is nothing to repair from. The frame is dropped and the layer
above notices the gap, which is what the next module is about.

Passing damaged data up with a warning would push a decision onto code that has no way
to make it. And recomputing the CRC is the genuinely dangerous option: it makes
corrupted data look pristine to everyone downstream, which is why a router that
re-frames a packet must re-derive its check from data it has already verified, never
from data it has not.
""",
                    },
                    {
                        "q": "Why does a reflected CRC-32 implementation build a 256-entry table?",
                        "opts": [
                            "Because a CRC-32 remainder can only take 256 distinct values",
                            "One entry per byte value, so the eight shift-and-XOR steps happen once at build time instead of once per byte of every frame",
                            "Because the polynomial `0xEDB88320` has 256 non-zero terms",
                            "Because the table has to be indexed by the low byte of the polynomial",
                        ],
                        "a": 1,
                        "why": r"""
The bitwise loop does eight shift-and-conditional-XOR steps per byte. Those eight steps
depend only on the low byte of the running remainder XORed with the incoming byte —
256 possibilities — so they can all be computed once and looked up thereafter. The
per-byte cost drops to one XOR, one shift and one array read, which is why CRC-32 is
cheap enough to run on every frame on the wire.

A CRC-32 remainder takes $2^{32}$ values, not 256; the table is indexed by a byte, not
sized by the remainder space. The polynomial has 33 terms in total, of which fifteen
are non-zero. And the index is derived from the data and the running remainder — the
polynomial is a constant and never indexes anything.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Two checks, side by side",
                "minutes": 9,
                "caption": "checks.py — the two integrity checks, four holes",
                "lang": "python",
                "brief": r"""
Both of these functions take bytes in and give a number out, and both are called an
*error check*. The four holes are where the difference between them lives: whether
position matters, and what the running value is doing between bytes.

Nothing is executed here — you are choosing expressions, not writing code.
""",
                "listing": r'''
# The two integrity checks, side by side. Same job, very different strength.

def internet_checksum(data):
    padded = data + (b"\x00" if len(data) % 2 else b"")
    total = 0
    for i in range(0, len(padded), 2):
        total += (padded[i] << ___) | padded[i + 1]   # one big-endian 16-bit word
        total = (total & 0xFFFF) + (total >> 16)      # fold the carry straight back in
    return ___ & 0xFFFF


CRC_POLY = 0xEDB88320                                 # the reflected CRC-32 polynomial

def table_entry(index):
    value = index
    for _ in range(8):
        value = (value >> 1) ^ (CRC_POLY if ___ else 0)
    return value


CRC_TABLE = [table_entry(i) for i in range(256)]


def crc32(data):
    crc = ___
    for byte in data:
        crc = CRC_TABLE[(crc ^ byte) & 0xFF] ^ (crc >> 8)
    return crc ^ 0xFFFFFFFF
''',
                "blanks": [
                    {
                        "prompt": "The word is big-endian: the byte at the lower offset is the more significant half.",
                        "hole": "?",
                        "opts": ["1", "16", "8", "0"],
                        "a": 2,
                        "why": "A shift of 8 puts the earlier byte in the high half of a 16-bit word and leaves room for the next byte to be ORed into the low half. That is what big-endian means, and it is the only step in the whole function that knows which byte came first.",
                        "whys": [
                            "A shift of 1 doubles the byte instead of positioning it, and seven of its eight bits then overlap the next byte in the OR rather than sitting above it. The result is still a number, which is what makes this kind of slip survive a casual test.",
                            "A shift of 16 lands the byte in the carry region, where the very next line folds it straight back into the low half. The two bytes of a word would then contribute equally and become interchangeable — the check would stop noticing a byte swap inside a word.",
                            "A shift of 8 puts the earlier byte in the high half of a 16-bit word and leaves room for the next byte to be ORed into the low half. That is what big-endian means, and it is the only step in the whole function that knows which byte came first.",
                            "With no shift the two bytes are simply ORed on top of each other, which is not even a sum: `41 42` and `42 41` both come out as `43`, and so does `43 40`.",
                        ],
                    },
                    {
                        "prompt": "RFC 1071 calls for the one's complement of the sum.",
                        "hole": "?",
                        "opts": ["total >> 16", "total", "-total", "~total"],
                        "a": 3,
                        "why": "`~total` inverts every bit, and masking to 16 bits gives the one's complement. Inverting is what makes the defining property work: append the result to the data and the receiver's sum comes out zero, so the receiver never has to compare anything.",
                        "whys": [
                            "That is the carry, and the fold on the line above has already driven it to zero — it is provably zero at every exit from that loop. So this returns 0 for every input, carrying no information about the data at all.",
                            "Returning the sum unchanged still detects the same errors, but it breaks the property every receiver relies on: data plus its own check would sum to twice the value rather than to zero, and every implementation on the internet would disagree with this one.",
                            "`-total` is the *two's* complement, which lands exactly one away from the one's complement the RFC specifies. Every value this function returns would then be wrong by one — consistently, and only against the rest of the internet, which is the kind of bug that only shows up in interoperation.",
                            "`~total` inverts every bit, and masking to 16 bits gives the one's complement. Inverting is what makes the defining property work: append the result to the data and the receiver's sum comes out zero, so the receiver never has to compare anything.",
                        ],
                    },
                    {
                        "prompt": "The reflected algorithm shifts right, so which bit is leaving the register each step?",
                        "hole": "?",
                        "opts": ["value & 1", "value & 0x80000000", "index & 1", "value >> 31"],
                        "a": 0,
                        "why": "`value >> 1` drops the least significant bit, so the XOR has to be conditioned on that bit — the one about to be lost. Reflected CRCs run bit-reversed throughout, which is why the polynomial is written as `0xEDB88320` rather than `0x04C11DB7`.",
                        "whys": [
                            "`value >> 1` drops the least significant bit, so the XOR has to be conditioned on that bit — the one about to be lost. Reflected CRCs run bit-reversed throughout, which is why the polynomial is written as `0xEDB88320` rather than `0x04C11DB7`.",
                            "Testing the top bit is right for the *non*-reflected form, which shifts left. Paired with a right shift it tests a bit that is not going anywhere, and the table it builds belongs to no CRC at all.",
                            "`index` is fixed for the whole eight-step loop, so this either XORs on every step or on none of them. Half the table would come out as a bare shift of the index.",
                            "This is the top bit again, extracted differently, and it has the same problem: the register shifts right, so bit 31 is arriving rather than leaving.",
                        ],
                    },
                    {
                        "prompt": "CRC-32 does not start from a blank register.",
                        "hole": "?",
                        "opts": ["0", "0xFFFFFFFF", "CRC_POLY", "0xCBF43926"],
                        "a": 1,
                        "why": "All ones in, all ones out — the initial and final XOR are both `0xFFFFFFFF`. The non-zero start is what makes leading zero bytes visible: from a zero register, a run of `00` bytes changes nothing, so `00 00 hello` and `hello` would share a remainder.",
                        "whys": [
                            "Zero is the mathematically natural start and the reason the standard does not use it: leading zero bytes become invisible, and a length field that is quietly padded would pass its own check.",
                            "All ones in, all ones out — the initial and final XOR are both `0xFFFFFFFF`. The non-zero start is what makes leading zero bytes visible: from a zero register, a run of `00` bytes changes nothing, so `00 00 hello` and `hello` would share a remainder.",
                            "The polynomial is the divisor, not the dividend. Seeding with it produces a self-consistent check that no other implementation agrees with, which is the worst kind: it works perfectly until it has to talk to something.",
                            "That is the published check value for the string `123456789` — an output, used to test an implementation, never an input to one.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "What stuffing costs",
                "minutes": 12,
                "vars": ["n", "p", "L"],
                "brief": r"""
Escaping is not free, and *how* not-free depends on the payload. Take an $n$-byte
payload in which each byte independently has probability $p$ of being `FLAG` or `ESC`,
and work out how many bytes actually go on the wire.
""",
                "steps": [
                    {
                        "prompt": "How many of the $n$ payload bytes does the stuffer have to escape, on average?",
                        "answer": "n p",
                        "hint": "Each byte is its own trial with success probability $p$, and expectations add whether or not the trials are independent.",
                        "deconstruct": [
                            "Write an indicator per byte: 1 if it needs escaping, 0 otherwise.",
                            "Each has expectation $p$, and there are $n$ of them.",
                        ],
                    },
                    {
                        "prompt": "An escaped byte goes out as two bytes; every other byte goes out as one. Write the length of the escaped body in terms of $n$ and $p$.",
                        "given": "On average $np$ of the $n$ bytes need escaping.",
                        "answer": "n(1 + p)",
                        "placeholder": "n \\cdot (\\ldots)",
                        "hint": "Every byte costs at least one byte on the wire, and each escaped one adds exactly one more.",
                        "deconstruct": [
                            "The body is $(n - np)$ single bytes plus $np$ doubled ones: $(n - np) + 2np$.",
                            "That collapses to $n + np$.",
                        ],
                    },
                    {
                        "prompt": "A frame is that body with a `FLAG` byte at each end. Write the whole frame length $L$.",
                        "answer": "n(1 + p) + 2",
                        "hint": "The delimiters are a fixed cost — two bytes, however long the payload is.",
                        "deconstruct": [
                            "One flag opens the frame, one closes it.",
                            "Neither is escaped, and neither scales with $n$.",
                        ],
                    },
                    {
                        "prompt": "Divide by $n$ to get the bytes on the wire per byte of payload.",
                        "given": "$L = n(1 + p) + 2$.",
                        "answer": "1 + p + \\frac{2}{n}",
                        "hint": "Divide each term of $L$ by $n$ separately and simplify the first one.",
                        "deconstruct": [
                            "$n(1+p)/n = 1 + p$.",
                            "The delimiters contribute $2/n$, which shrinks as the payload grows.",
                        ],
                    },
                    {
                        "prompt": "Now the worst case: a payload made entirely of reserved bytes, so $p = 1$. Write $L$ in terms of $n$.",
                        "answer": "2n + 2",
                        "hint": "Substitute $p = 1$ into $L = n(1 + p) + 2$.",
                        "deconstruct": [
                            "$1 + p$ becomes 2, so the body is $2n$.",
                            "The two flags are still there on top.",
                        ],
                    },
                ],
                "closing": r"""
Two numbers make this concrete. On payloads that look like random bytes, two of the 256
values are reserved, so $p = 1/128$ and the body grows by under 1% — invisible. But $p$
is not a property of the protocol, it is a property of whoever is sending: a payload of
solid `7e` bytes drives $p$ to 1 and doubles the frame, and a link sized for the average
case has just been halved by a sender who read the RFC.

The $2/n$ term pulls the other way. It says the delimiters are what hurt *small* frames,
which is why an acknowledgement carrying no data at all is still not free, and why
length-prefixed framing — a counted header instead of a reserved byte — trades a fixed
header for an expansion factor that no payload can inflate.
""",
            },
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
            "read": [
                {
                    "title": "One bit of sequence number, and then a window",
                    "minutes": 11,
                    "body": r'''
Five frames, `a` to `e`, have to cross a link that sometimes loses what it is given.
Not maliciously and not often — but the link makes no promises, and the layer above it
is expected to deliver all five, once each, in order. That gap between what the link
offers and what the application needs is the whole of this module, and the lab,
*Stop-and-wait and Go-Back-N on a deterministic channel*, has you close it twice.

## Send, wait, and the problem with silence

The first idea is the one everyone has: send a frame, wait for the receiver to say it
arrived, and if nothing comes back within some time, send it again. A frame that was
lost gets retransmitted after the timeout; a frame that arrived gets acknowledged and
the sender moves on.

Now lose the acknowledgement instead of the frame. The receiver got `a`, delivered it,
and replied; the reply died on the way back. The sender's timer fires, and from where
the sender stands this is indistinguishable from the frame having been lost — a timeout
is the absence of information, and it looks the same whichever direction the loss was
in. So the sender does the only thing it can and retransmits `a`. The receiver now
holds a second copy of `a`, and if it delivers it, the application reads `aabcde`.

The receiver needs a way to tell a new frame from a repeat, and the way is a sequence
number carried in the frame. How many bits does it need? With only one frame ever
outstanding, the receiver is always in one of two states — waiting for the frame after
the last one it delivered, or being offered that last one again — so one bit is enough.
The sender alternates the bit; the receiver keeps the bit it expects next, delivers a
frame whose bit matches and flips its expectation, and discards a frame whose bit does
not match. This is the alternating-bit protocol, and it is the smallest reliable
transport there is.

There is one more rule, and it is the one people get wrong. When the receiver discards
a duplicate, it must still acknowledge it. The temptation is to stay quiet — the frame
is old news, why reply to it? — but think about why the duplicate exists at all. It
exists because the sender never saw an acknowledgement. If the receiver does not send
another one, the sender's timer fires again, it retransmits again, the receiver
discards again, and the two of them are stuck for ever, each behaving perfectly by its
own lights. Acknowledge the duplicate and the deadlock breaks. The matching rule on the
other side is that the receiver flips its expected bit only for a *new* frame; flip it
on the duplicate and the same frame is delivered twice after all.

## A trace with real numbers

The lab replaces random loss with a channel that drops exactly the transmissions you
name, counting data transmissions and acknowledgements separately from zero. That makes
every run reproducible and every counter checkable. Here is the alternating-bit sender
against a link that drops data transmissions 1 and 4 and acknowledgements 0 and 3.

```python
class Link:
    def __init__(self, data_drops=(), ack_drops=()):
        self.data_drops, self.ack_drops = set(data_drops), set(ack_drops)
        self.data_sends = self.ack_sends = 0

    def send_data(self, seq):
        index = self.data_sends
        self.data_sends += 1
        return index not in self.data_drops

    def send_ack(self, seq):
        index = self.ack_sends
        self.ack_sends += 1
        return index not in self.ack_drops


def stop_and_wait(frames, link):
    delivered, expected, timeouts = [], 0, 0
    for index, frame in enumerate(frames):
        seq = index % 2
        while True:
            if link.send_data(seq):
                if seq == expected:
                    delivered.append(frame)
                    expected ^= 1
                    print(f"{frame.decode()} delivered on data transmission {link.data_sends - 1}")
                else:
                    print(f"duplicate {frame.decode()} discarded but acknowledged")
                if link.send_ack(seq):
                    break
            timeouts += 1
    return delivered, link.data_sends, link.ack_sends, timeouts


frames = [b"a", b"b", b"c", b"d", b"e"]
print(stop_and_wait(frames, Link(data_drops={1, 4}, ack_drops={0, 3})))
```

Follow it. Transmission 0 carries `a`; it arrives, is delivered, and acknowledgement 0
is sent — and dropped. Timeout. Transmission 1 carries `a` again and is dropped.
Timeout. Transmission 2 carries `a` a third time; the receiver sees sequence bit 0 when
it expects 1, discards the payload, and sends acknowledgement 1, which arrives. `b`
goes on transmission 3 and is acknowledged on acknowledgement 2. `c` goes on
transmission 4 and is dropped; on transmission 5 it arrives and acknowledgement 3 is
dropped; transmission 6 is the duplicate, acknowledged on acknowledgement 4. `d` and
`e` are clean. The final line prints all five frames in order, then 9, 7 and 4: nine
data transmissions, seven acknowledgements, four timeouts. Those are the numbers the
lab's third test checks, and now you know where each one comes from.

## The cost of waiting

Stop-and-wait is correct and it is slow, and the slowness is not a matter of
implementation. Take a 100 Mb/s link with a 40 ms round-trip time carrying 10 000-bit
frames. Pushing one frame onto the link takes $L/R = 10^4 / 10^8 = 100$ microseconds.
Then the sender waits 40 ms for the acknowledgement. It was busy for a tenth of a
millisecond out of every forty, which is a utilisation of

$$U = \frac{L/R}{L/R + T} = \frac{L}{L + RT} = \frac{10^4}{10^4 + 4 \times 10^6} \approx 0.0025.$$

A quarter of one percent, on a link that is in no way slow. Notice that $R$ sits in the
denominator: buying a faster link makes this protocol worse, because the frame goes out
sooner and the wait is the same. The module's derivation unit works this expression out
step by step.

The fix is in the picture. During those 40 ms the link could have been carrying
$RT = 4 \times 10^6$ bits — four hundred frames — and the sender let it carry one. The
bandwidth-delay product, $RT/L$, is the number of frames the link can hold in flight,
and a sender that keeps that many outstanding never stops transmitting. That number,
plus one for the frame being sent at the moment the first acknowledgement returns, is
the window.

## A window, and one number at the receiver

Go-Back-N is the alternating-bit protocol with a window. The sender may have up to
`window` frames outstanding, numbered from `base`, the oldest one not yet acknowledged.
The receiver keeps one number, `expected`, and accepts a frame only when its sequence
number is that one; anything else is discarded, however intact it was. Acknowledgements
are cumulative: an acknowledgement naming frame 3 means *I have everything up to and
including 3*, so one of them can cover a whole burst, and a lost one costs nothing if a
later one gets through.

The price of that simple receiver is paid whenever a frame in the middle of a burst is
lost. Every frame after it in the burst arrives, is out of order, and is thrown away;
the sender goes back to the missing one and resends the lot. Trace it with a window of
3 and data transmission 1 lost.

```python
class Link:
    def __init__(self, data_drops=(), ack_drops=()):
        self.data_drops, self.ack_drops = set(data_drops), set(ack_drops)
        self.data_sends = self.ack_sends = 0

    def send_data(self, seq):
        index = self.data_sends
        self.data_sends += 1
        return index not in self.data_drops

    def send_ack(self, seq):
        index = self.ack_sends
        self.ack_sends += 1
        return index not in self.ack_drops


def go_back_n(frames, link, window):
    delivered, base, expected, rounds = [], 0, 0, 0
    while base < len(frames):
        rounds += 1
        burst = list(range(base, min(base + window, len(frames))))
        for seq in burst:
            if link.send_data(seq) and seq == expected:
                delivered.append(frames[seq])
                expected += 1
        print(f"round {rounds}: sent {burst}, receiver now expects {expected}")
        if expected > base and link.send_ack(expected - 1):
            base = expected
    return delivered, link.data_sends, link.ack_sends, rounds


frames = [b"a", b"b", b"c", b"d", b"e"]
print(go_back_n(frames, Link(data_drops={1}), 3))
```

Round 1 sends frames 0, 1 and 2. Frame 0 arrives and is delivered, so `expected`
becomes 1. Frame 1 is transmission 1 and is dropped. Frame 2 arrives — intact,
undamaged, perfectly good — and the receiver, expecting 1, discards it. The
acknowledgement names frame 0 and `base` moves to 1. Round 2 sends 1, 2 and 3, all of
which arrive and are delivered in order; the acknowledgement names 3 and `base` moves
to 4. Round 3 sends frame 4 alone. Seven data transmissions for five frames, three
acknowledgements, three rounds: the counters in the lab's *One loss costs the rest of
the window* test.

Goodput is the fraction of transmissions that carried something useful: $5/7 \approx
0.71$ here, and exactly 1 only on a run where nothing was ever sent twice. It is the
number the lab uses to compare the two protocols on the same channel, and it is worth
being precise about what it measures. It counts data transmissions only. Folding the
acknowledgements into the denominator measures the total cost of the exchange, which is
a real quantity but a different one, and a ratio that comes out above 1 has the
fraction upside down.

## The mistake, and where the idea stops

The mistake in Go-Back-N is to buffer the out-of-order frame. It is tempting for the
best of reasons — frame 2 arrived, throwing it away is waste, and a receiver could keep
it and slot it in once frame 1 turns up. That protocol exists. It is called selective
repeat, and it is a different protocol: the receiver needs a buffer and per-frame
acknowledgements, the sender needs a timer per frame rather than one for the window,
and the counters change. If you build it in this lab, the tests for a Go-Back-N receiver
will fail, because they count what a Go-Back-N receiver does. Build what is specified;
the waste is the specification.

The alternating bit stops working the moment more than one frame is outstanding. With a
window of $W$ the sender needs sequence numbers that do not repeat within a window's
worth of frames, and with $k$ bits of sequence number Go-Back-N can safely run a window
of at most $2^k - 1$: use all $2^k$ and a receiver that has seen a whole window cannot
tell the next new frame from a retransmission of the first old one. The lab sidesteps
this by numbering frames from 0 without wrapping, which is fine for five frames and
would not be for five billion. The other thing the lab's channel cannot do is reorder —
it drops, and only what you name — and a real network reorders freely, which is one of
the reasons TCP numbers bytes rather than frames and treats a timeout as a reason to
slow down rather than only a reason to resend. That is a different protocol with a
different set of problems. For this one, the deterministic channel is the point: every
counter in every test is a number you can derive by hand, as you did above, before you
run a line of code.
''',
                },
            ],
            "quiz": {
                "title": "What the sender knows, and when",
                "minutes": 7,
                "questions": [
                    {
                        "q": "A stop-and-wait receiver gets a frame it has already delivered. Why must it acknowledge it again rather than ignore it?",
                        "opts": [
                            "Because the duplicate might carry different data under the same sequence bit",
                            "So the sender can measure the round-trip time from the repeat",
                            "The duplicate means its previous acknowledgement never arrived, and silence would leave the sender retransmitting for ever",
                            "So the receiver's own sequence bit flips on schedule",
                        ],
                        "a": 2,
                        "why": r"""
There are only two ways a duplicate can turn up: the sender timed out because the frame
was lost, or it timed out because the *acknowledgement* was lost. In the second case the
receiver has already delivered the data and the sender is waiting for a reply that it
will never get unless the receiver sends another one. Staying quiet deadlocks the pair.

Timing is not the point — the sender times out on a clock, not on a pattern of arrivals.
The data under a repeated sequence bit is by definition the same frame, which is exactly
why it is safe to discard the payload and reply anyway. And the receiver's bit must *not*
flip on a duplicate: flipping it is how the same frame gets delivered twice.
""",
                    },
                    {
                        "q": "The sender's timer fires with no acknowledgement in hand. What does it actually know?",
                        "opts": [
                            "That the receiver has run out of buffer space",
                            "That the frame was lost, since a receiver always acknowledges",
                            "That the acknowledgement was lost, since the channel drops replies more often",
                            "Only that nothing came back — a lost frame and a lost acknowledgement look identical from here",
                        ],
                        "a": 3,
                        "why": r"""
A timeout is the absence of information, and the sender cannot distinguish between the
several worlds that produce it: the frame died on the way out, the acknowledgement died
on the way back, or both are still in flight and the timer was simply too short. This is
why the protocol is built to be correct under *all* of them — retransmit, and let the
sequence number sort out what the receiver should do with what arrives.

Nothing about a timeout points at a direction, or at a rate, or at the receiver's
memory. Any design that assumes it does is assuming a fact the sender does not have.
""",
                    },
                    {
                        "q": "A Go-Back-N receiver is waiting for frame 6, and frames 7 and 8 arrive intact. What happens to them?",
                        "opts": [
                            "They are discarded, the receiver re-acknowledges 5, and the sender resends from 6 onwards",
                            "They are buffered until 6 arrives, then all three are delivered in order",
                            "They are delivered immediately and the application reorders them",
                            "They are acknowledged individually so the sender only resends 6",
                        ],
                        "a": 0,
                        "why": r"""
A Go-Back-N receiver keeps exactly one number — the next sequence it wants — and no
buffer. Anything that is not that number is thrown away, however intact it was. That is
the bargain: a trivially simple receiver, paid for by re-sending a whole window every
time one frame goes missing.

Buffering out-of-order arrivals is selective repeat, and it is a genuinely different
protocol: it needs per-frame acknowledgements and a receive buffer, and it recovers
without re-sending what already got through. Delivering out of order breaks the promise
the layer exists to make. And individual acknowledgements are precisely what Go-Back-N
does not have — its acknowledgements are cumulative, which is why a single one can
cover a whole burst.
""",
                    },
                    {
                        "q": "A 100 Mb/s link has a 40 ms round-trip time and carries 10 000-bit frames. Roughly how many frames must be in flight to keep the sender transmitting continuously?",
                        "opts": ["About 40", "About 400", "About 4000", "About 4"],
                        "a": 1,
                        "why": r"""
The bandwidth-delay product is $10^8 \times 0.04 = 4 \times 10^6$ bits, which is
$4 \times 10^6 / 10^4 = 400$ frames sitting on the wire at any instant. A window of
about 400 (401 if you count the one being transmitted) keeps the sender busy; anything
smaller leaves it waiting.

The arithmetic is worth doing rather than eyeballing, because the answer scales with
*both* rate and delay and neither is intuitive. Stop-and-wait on this link would run one
frame per 40 ms — a quarter of one percent of what the link can carry, on a link that is
in no way slow.
""",
                    },
                    {
                        "q": "A transfer of five frames completes after seven data transmissions. What is its goodput?",
                        "opts": ["$5/12 \\approx 0.42$", "$7/5 = 1.4$", "$5/7 \\approx 0.71$", "$2/7 \\approx 0.29$"],
                        "a": 2,
                        "why": r"""
Goodput is useful frames delivered over total transmissions: $5/7$. It is a fraction of
work that was not wasted, so it is at most 1, and it reaches 1 only when nothing was
ever sent twice.

A ratio above 1 has the fraction upside down and would claim the link delivered more
than it carried. Folding the five acknowledgements into the denominator alongside the
seven data transmissions measures something else — the cost of the exchange in total
messages, which is worth knowing but is not this. And $2/7$ is the waste rather than
the useful work: a real quantity, but the complement of the one being asked for.
""",
                    },
                ],
            },
            "blanks": {
                "title": "Go-Back-N, one round at a time",
                "minutes": 9,
                "caption": "gbn.py — one window burst, four holes",
                "lang": "python",
                "brief": r"""
One pass of the `while` loop is one round: the sender bursts everything in its window,
the receiver accepts only what comes next in order, and at most one cumulative
acknowledgement comes back. Every hole takes a plausible neighbouring variable, and none
of the wrong ones is a syntax error — they all fail further downstream than that, and
they fail in different ways. Some deliver the wrong bytes. Some deliver the right ones at
a fraction of the rate. Some leave `base` stuck where it is, and then the `while` loop
never ends at all. And one hole holds a number that goes out on the wire but that nothing
in this listing reads back, so only the protocol's meaning can tell you which value is
right. Work out which kind each one is.

Nothing is executed here — you are choosing names, not writing code.
""",
                "listing": r'''
def go_back_n(frames, link, window):
    """Sliding-window ARQ. `base` is the sender's oldest unacknowledged frame;
    `expected` is the receiver's next in-order sequence number."""
    delivered, base, expected, rounds = [], 0, 0, 0
    while base < len(frames):
        rounds += 1
        for seq in range(base, min(base + ___, len(frames))):
            if link.send_data(seq) and seq == ___:
                delivered.append(frames[seq])       # the receiver never buffers
                expected += 1
        if expected > base and link.send_ack(___):
            base = ___
    return delivered, rounds
''',
                "blanks": [
                    {
                        "prompt": "How far past the oldest unacknowledged frame may the sender go?",
                        "hole": "?",
                        "opts": ["rounds", "1", "len(frames)", "window"],
                        "a": 3,
                        "why": "The window is the whole point of the protocol: it is the number of frames the sender is allowed to have outstanding, so the burst runs from `base` to `base + window`. The `min` with `len(frames)` is only there to stop the last burst running off the end.",
                        "whys": [
                            "`rounds` grows by one each pass, so the window would start at one frame and creep upward with no relation to what the link can hold. Slow start looks a little like this, but it is driven by acknowledgements, not by a loop counter.",
                            "A burst of one is stop-and-wait wearing a sliding-window costume. It is correct, it terminates, and it throws away every bit of the throughput the window exists to buy.",
                            "Sending the whole file every round ignores the window entirely. On a long file that is an enormous burst into a receiver that will discard everything past the first gap.",
                            "The window is the whole point of the protocol: it is the number of frames the sender is allowed to have outstanding, so the burst runs from `base` to `base + window`. The `min` with `len(frames)` is only there to stop the last burst running off the end.",
                        ],
                    },
                    {
                        "prompt": "What is the receiver's whole acceptance test?",
                        "hole": "?",
                        "opts": ["expected", "base", "base + window", "seq"],
                        "a": 0,
                        "why": "`expected` is the only state the receiver has, and comparing against it is the only test it performs. A frame that is not the next one in order is dropped even though it arrived perfectly, which is exactly why one loss costs a whole window.",
                        "whys": [
                            "`expected` is the only state the receiver has, and comparing against it is the only test it performs. A frame that is not the next one in order is dropped even though it arrived perfectly, which is exactly why one loss costs a whole window.",
                            "`base` is the *sender's* variable and the receiver has no access to it. Because `base` only moves after an acceptance, this does deliver frames in order — but one per round, whatever the window is, so every other frame in the burst is transmitted and thrown away. And it duplicates: lose an acknowledgement and `base` stays put, so the next round accepts `frames[base]` a second time.",
                            "`range` stops one short of its upper bound, so `seq` never reaches `base + window` and this test is never true for any frame. Nothing is ever accepted, `expected` stays at 0, `expected > base` is therefore false, `base` never moves — and the `while` loop resends the same burst for ever into a receiver that will not take any of it.",
                            "`seq == seq` is always true, so every frame that arrives is delivered, in whatever order it happens to arrive, gaps and all. That is the layer failing to do the one thing it promised.",
                        ],
                    },
                    {
                        "prompt": "The acknowledgement is cumulative: it names the highest sequence number received in order.",
                        "hole": "?",
                        "opts": ["expected", "expected - 1", "base", "seq"],
                        "a": 1,
                        "why": "`expected` is the frame the receiver *wants next*, so the highest one it actually holds is `expected - 1` — and a cumulative acknowledgement names what arrived, not what is hoped for. Note that this listing cannot tell the four choices apart: `Link.send_ack` reports only whether the acknowledgement got through, and the line below slides to `expected` whatever number was passed. You are choosing what a real peer would be told, and the other three tell it something untrue.",
                        "whys": [
                            "This acknowledges a frame the receiver has not seen. Some real protocols do number their acknowledgements this way — TCP acknowledges the next byte expected — but then the sender's update has to match, and mixing the two conventions is how a frame gets silently skipped.",
                            "`expected` is the frame the receiver *wants next*, so the highest one it actually holds is `expected - 1` — and a cumulative acknowledgement names what arrived, not what is hoped for. Note that this listing cannot tell the four choices apart: `Link.send_ack` reports only whether the acknowledgement got through, and the line below slides to `expected` whatever number was passed. You are choosing what a real peer would be told, and the other three tell it something untrue.",
                            "`base` is the oldest frame the sender has not yet had credited, so naming it credits exactly one frame no matter how many arrived — the cumulative acknowledgement's whole value thrown away. A peer that acted on the number would crawl forward a frame per round; this listing does not act on it, so the wrongness is entirely in what the message says.",
                            "`seq` survives the `for` loop holding the last sequence number the sender *transmitted*, which is not evidence that anything arrived. Naming it claims the whole burst, gap and all — a frame the channel ate in the middle would be acknowledged along with everything after it. Again the claim is false on the wire rather than in this listing, which ignores the number.",
                        ],
                    },
                    {
                        "prompt": "The acknowledgement arrived. How far does the window slide?",
                        "hole": "?",
                        "opts": ["base + window", "base + 1", "expected", "expected - 1"],
                        "a": 2,
                        "why": "The acknowledgement covers everything up to `expected - 1`, so the oldest frame still unaccounted for is `expected`. The window slides by however much got through in that round — sometimes the whole burst, sometimes one frame, sometimes nothing.",
                        "whys": [
                            "This slides by the full window regardless of what was acknowledged. The receiver still accepts only `expected`, so nothing is ever delivered out of order and the list cannot end up with a hole in it — it comes up short instead. `base` marches on past the frames the receiver discarded, and the transfer either stops early having silently skipped them, or `base` overshoots `expected` for good: `expected > base` is then never true again, no acknowledgement is ever sent, `base` stops moving, and the `while` loop resends the same burst for ever.",
                            "Sliding by exactly one throws away the cumulative acknowledgement's whole value: a burst of eight that all arrived would take eight rounds to be credited, and the protocol degenerates to stop-and-wait with extra transmissions.",
                            "The acknowledgement covers everything up to `expected - 1`, so the oldest frame still unaccounted for is `expected`. The window slides by however much got through in that round — sometimes the whole burst, sometimes one frame, sometimes nothing.",
                            "`expected - 1` is the last frame the receiver *has*, so leaving `base` there re-sends it every round for ever. The transfer never terminates, and there is nothing in this listing to stop it.",
                        ],
                    },
                ],
            },
            "derive": {
                "title": "Utilisation, and the window that fills the pipe",
                "minutes": 13,
                "vars": ["L", "R", "T", "W"],
                "brief": r"""
A sender with a long file to move, a link that carries $R$ bits per second, and a
round-trip time of $T$ seconds. Frames are $L$ bits each and nothing is lost. The only
thing between the sender and the full rate of the link is the protocol.
""",
                "steps": [
                    {
                        "prompt": "How long does the sender spend pushing one $L$-bit frame onto an $R$ bit/s link?",
                        "answer": "\\frac{L}{R}",
                        "hint": "Bits divided by bits per second is seconds.",
                        "deconstruct": [
                            "This is transmission time, not propagation.",
                            "It is set by how fast the interface clocks bits out, not by how far they then travel.",
                        ],
                    },
                    {
                        "prompt": "Stop-and-wait sends one frame and may then send nothing until its acknowledgement returns. Write the time from the start of one frame to the start of the next.",
                        "given": "$T$ already covers propagation in both directions and the acknowledgement itself.",
                        "answer": "\\frac{L}{R} + T",
                        "hint": "Transmit the frame, then wait one round trip. Those are the only two things in the cycle.",
                        "deconstruct": [
                            "The sender is busy for the transmission time.",
                            "Then it is idle for $T$, and only then may it start again.",
                        ],
                    },
                    {
                        "prompt": "Utilisation $U$ is the fraction of that cycle the sender is actually transmitting. Clear the inner fraction and write $U$ in terms of $L$, $R$ and $T$.",
                        "given": "$U = (L/R) / (T + L/R)$.",
                        "answer": "\\frac{L}{L + R T}",
                        "placeholder": "\\frac{L}{\\ldots}",
                        "hint": "Multiply the top and the bottom by $R$.",
                        "deconstruct": [
                            "Top: $R \\cdot L/R = L$.",
                            "Bottom: $R(T + L/R) = RT + L$.",
                        ],
                    },
                    {
                        "prompt": "Now let the sender keep several frames in flight. How many frames $W$ exactly fill one cycle, so that the sender never stops transmitting?",
                        "given": "The cycle lasts $T + L/R$ seconds and one frame occupies $L/R$ of it.",
                        "answer": "\\frac{R T}{L} + 1",
                        "hint": "Divide the cycle length by the time a single frame takes.",
                        "deconstruct": [
                            "$W = (T + L/R) / (L/R)$.",
                            "Divide each term of the top by $L/R$: the $T$ gives $RT/L$ and the $L/R$ gives 1.",
                        ],
                    },
                    {
                        "prompt": "With a window of $W$ frames, and $W$ no larger than that limit, write the utilisation.",
                        "answer": "\\frac{W L}{L + R T}",
                        "hint": "$W$ frames go out per cycle now instead of one, and the cycle length has not changed.",
                        "deconstruct": [
                            "The sender is busy for $W \\cdot L/R$ seconds of each cycle.",
                            "So the utilisation is $W$ times what it was.",
                        ],
                    },
                ],
                "closing": r"""
$RT/L$ is the bandwidth-delay product measured in frames — how much data the link is
holding at any instant, and the entire reason a window exists.

Put a satellite hop in: $T = 500$ ms, $R = 10$ Mb/s, $L = 12\,000$ bits. Then $RT/L$ is
about 417, and stop-and-wait runs at $12\,000 / (12\,000 + 5 \times 10^6)$, which is
0.24% of the link. Notice what that expression does when you buy more bandwidth: $R$ is
in the denominator, so a faster link makes stop-and-wait *worse*. Only $W$ helps, and
that is a protocol change, not a purchase.
""",
            },
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
            "read": [
                {
                    "title": "Finding the way with nothing but what your neighbours say",
                    "minutes": 13,
                    "body": r'''
Five routers, lettered A to E, are wired together as in the lab's `MESH`: A sees B at
cost 2 and C at cost 5, B sees A, C and D, and so on round to E, which sees only C and
D. Nobody has a map. Each router knows its own links and their costs and nothing beyond,
and each one has to fill in a forwarding table — for every destination, which neighbour
to hand a packet to — using only what it can learn by talking to the routers next to
it. That constraint, *local information only*, is what makes routing a problem rather
than a lookup, and the lab, *Convergence, and how it fails*, has you solve it two
different ways and watch one of them go wrong.

## Ask your neighbours what they would charge

Suppose A wants to reach E. It cannot see E. What it can do is ask each neighbour what
*that* neighbour's cost to E is, add the cost of its own link to that neighbour, and
take the cheapest total. If B says it can reach E for 7 and the link A–B costs 2, then
A can reach E for 9 by way of B. If C says 5 and A–C costs 5, that is 10 by way of C,
and B's offer wins. Written down, the rule is

$$D(x, y) = \min_{v \in N(x)} \big( c(x, v) + D(v, y) \big),$$

where $N(x)$ is the set of $x$'s neighbours, $c$ is a link cost and $D$ is the best
distance known. That is the Bellman–Ford equation, and the striking thing about it is
that it is *local*: everything on the right-hand side is either a cost $x$ knows
first-hand or a number a neighbour can tell it. The neighbour's number is hearsay — B
got its 7 from somewhere — but if every router applies the rule to whatever it
currently believes, and keeps telling its neighbours the result, the beliefs converge
to the truth.

The protocol built on that is distance vector. Each router keeps a table mapping every
destination to a pair: the cost, and the neighbour to forward to. It starts knowing
only itself at cost 0 and its direct neighbours at their link costs, with every other
destination at *infinity*. Then, in rounds, every router sends its whole table to its
neighbours and recomputes every destination from what it received. A round that changes
nothing anywhere is the sign that it has converged.

## Watching A learn about E

The block below runs the exchange on the lab's mesh and prints A's table after each
round, with the cost and next hop for each destination.

```python
INFINITY = 16
MESH = {
    "A": {"B": 2, "C": 5},
    "B": {"A": 2, "C": 1, "D": 4},
    "C": {"A": 5, "B": 1, "D": 2, "E": 8},
    "D": {"B": 4, "C": 2, "E": 3},
    "E": {"C": 8, "D": 3},
}


def initial_tables(graph):
    tables = {}
    for node in graph:
        table = {other: (INFINITY, None) for other in graph}
        table[node] = (0, None)
        for neighbour, weight in graph[node].items():
            table[neighbour] = (weight, neighbour)
        tables[node] = table
    return tables


def dv_round(graph, tables, split_horizon=False):
    updated = {}
    for node in graph:
        table = {node: (0, None)}
        for dest in graph:
            if dest == node:
                continue
            best, hop = INFINITY, None
            for neighbour, weight in sorted(graph[node].items()):
                cost, their_hop = tables[neighbour][dest]
                if split_horizon and their_hop == node:
                    continue
                total = min(weight + cost, INFINITY)
                if total < best:
                    best, hop = total, neighbour
            table[dest] = (best, hop) if best < INFINITY else (INFINITY, None)
        updated[node] = table
    return updated


tables = initial_tables(MESH)
for round_number in range(1, 5):
    tables = dv_round(MESH, tables)
    print(round_number, tables["A"])
```

Before any exchange A knows B at 2 and C at 5, and D and E are at infinity. After round
1, A has heard B's initial table, which names D at 4, and C's, which names D at 2 and E
at 8. So D is now $2 + 4 = 6$ by way of B (C's offer would be $5 + 2 = 7$), and E is
$5 + 8 = 13$ by way of C, because B has not heard of E yet. Those two pairs, `(6, "B")`
and `(13, "C")`, are what the lab's *A round is synchronous* test looks for after a
single round.

After round 2 the picture improves because B and C have themselves improved. In round
1, B learned E at 7 by way of D and C learned E at 5 by way of D, so A now hears E
offered at $2 + 7 = 9$ from B and $5 + 5 = 10$ from C, and takes 9. After round 3, B
has heard C's offer of 5 and revised its own E to $1 + 5 = 6$, so A's E becomes
$2 + 6 = 8$ by way of B. Round 4 changes nothing, so the fourth printed line matches
the third, and the exchange has converged in three rounds to costs of 0, 2, 3, 5 and 8
for A through E, with the best route to E running A–B–C–D–E. Notice that the route to
C is not the direct link. The direct link costs 5 and B's detour costs 3, and A
discovered that in the first round, from B's table.

The mistake to name here is updating the tables in place. It is tempting because it is
less code: loop over nodes, overwrite each table as you go. But then the second node in
the loop reads the *new* table of the first, not the one everyone else is reading, and
the round is no longer a round — it is a chain of updates whose result depends on the
order the nodes were visited. It usually still converges, to the same distances, in a
different number of rounds, and the lab's tests count rounds. `dv_round` builds every
new table from the old ones and returns them; that is the whole of what synchronous
means.

## Bad news travels slowly

Now the failure. Take the three-node line A–B–C with unit costs, let it converge — B
reaches A directly at 1, C reaches A at 2 by way of B — and then cut the link between A
and B. The block starts from the converged tables, written out in full, and runs the
exchange on the broken graph twice.

```python
INFINITY = 16
converged = {
    "A": {"A": (0, None), "B": (1, "B"), "C": (2, "B")},
    "B": {"A": (1, "A"), "B": (0, None), "C": (1, "C")},
    "C": {"A": (2, "B"), "B": (1, "B"), "C": (0, None)},
}
broken = {"A": {}, "B": {"C": 1}, "C": {"B": 1}}


def dv_round(graph, tables, split_horizon=False):
    updated = {}
    for node in graph:
        table = {node: (0, None)}
        for dest in graph:
            if dest == node:
                continue
            best, hop = INFINITY, None
            for neighbour, weight in sorted(graph[node].items()):
                cost, their_hop = tables[neighbour][dest]
                if split_horizon and their_hop == node:
                    continue
                total = min(weight + cost, INFINITY)
                if total < best:
                    best, hop = total, neighbour
            table[dest] = (best, hop) if best < INFINITY else (INFINITY, None)
        updated[node] = table
    return updated


def run_dv(graph, tables, split_horizon=False):
    rounds = 0
    while True:
        nxt = dv_round(graph, tables, split_horizon)
        if nxt == tables:
            return rounds
        tables = nxt
        rounds += 1
        print(f"round {rounds}: B->A {tables['B']['A']}, C->A {tables['C']['A']}")


print("without split horizon")
slow = run_dv(broken, converged)
print("with split horizon")
fast = run_dv(broken, converged, split_horizon=True)
print(slow, fast)
```

In the first round after the cut, B has lost its link to A, so it recomputes from its
only remaining neighbour. C is advertising A at cost 2. B has no way to know that C's
route runs through B itself — a distance vector carries a number, not a path — so B
adopts $1 + 2 = 3$ by way of C. C, meanwhile, is still reading the table B sent before
the cut, which said 1, and keeps its 2. In the second round C reads B's new 3 and goes
to 4, while B reads C's unchanged 2 and stays at 3. In the third B reads the 4 and goes
to 5. The printout shows the two of them climbing in turn, each one's route to A
running through the other, each believing the other, and it stops only when the costs
reach 16 — the value the lab calls `INFINITY` — and both tables record A as
unreachable. Fifteen rounds to learn that a link is down, on a network of three nodes.

That is why *infinity* is small. Sixteen is not a measurement of any network; it is a
deadline. The counting proceeds one round per exchange until it hits the ceiling, so
the ceiling *is* the time to converge on bad news, and RIP's choice of 16 is a bet that
no network it runs on is wider than that. Making it larger would make every such
failure take proportionally longer to clear.

## Split horizon

The loop starts when C tells B about a route to A that goes through B. The fix is a
rule of silence: never advertise a route back to the neighbour you learned it from. In
the code it is one `continue` — when a neighbour's advertised next hop for a
destination is *us*, skip that advertisement. With `split_horizon=True` the same cut
plays out differently: B, hearing nothing usable from C, marks A unreachable in the
first round; C reads that in the second; the third round changes nothing. The last
printed line is `15 2` — two rounds instead of fifteen, and the same final answer. That
is the point the lab's last test makes on the healthy mesh: split horizon must change
nothing about where a working network converges to, only how fast it recovers.

Where this stops holding is the next shape up. On a triangle, or any loop of three or
more nodes, a router can learn a route to a dead destination from a neighbour who
learned it from a third router who learned it from the first — nobody is echoing
anything straight back, so the silence rule never fires, and the count to infinity
resumes. Poison reverse, which advertises the route back at infinity instead of staying
quiet, and hold-down timers, which refuse to believe good news for a while after bad,
each shorten the damage and neither ends it. The cure is to carry paths rather than
distances, which is what BGP does, or to give up on hearsay altogether.

## Giving everyone the map

Link state is the other way. Instead of telling neighbours your distances, tell
*everyone* your links: each router floods its list of neighbours and costs to the whole
network, and every router assembles the same graph. Once a router has the graph,
routing is an ordinary single-source shortest-path problem it can solve alone, and the
algorithm for that is Dijkstra's.

Dijkstra's idea comes from one observation about positive costs. Keep a tentative
distance to every node, starting at 0 for the source and infinity elsewhere. Pick the
unsettled node with the smallest tentative distance and declare it settled. Can any
other route reach it more cheaply? No — every other route leaves the settled set
through some node whose tentative distance is at least as large, and then adds a
positive edge. So the node is done, and its edges can be used to lower the tentative
distances of its neighbours, after which the next smallest is picked.

On the mesh from A: A settles at 0 and offers B at 2 and C at 5. B is smallest, settles
at 2, and offers C at $2 + 1 = 3$ and D at $2 + 4 = 6$. C settles at 3 and offers D at
$3 + 2 = 5$ and E at $3 + 8 = 11$. D settles at 5 and offers E at $5 + 3 = 8$. E
settles at 8. Those are the distances distance vector arrived at three rounds later,
and the lab checks that the two agree for every pair of nodes. Two algorithms with
nothing in common in their mechanics compute the same numbers, because both are exact;
what differs is what each router had to know. A link-state router needs an identical
copy of the graph to every other router, and when two copies disagree — during a
flood, after a lost advertisement — packets loop until they agree again. A
distance-vector router needs nothing but its neighbours, and cannot see the loop it is
part of.

One last boundary. Dijkstra's argument leaned on every edge being positive; put a
negative cost anywhere and a settled node could be undercut by a route through it, and
the greedy choice is wrong. Bellman–Ford has no such assumption and tolerates negative
edges, as long as no cycle sums below zero. Real link costs are never negative, so in
practice the difference is academic — but it is the reason the module's numeric unit
tells you the costs are all positive before asking you to run the algorithm by hand.
''',
                },
            ],
            "quiz": {
                "title": "Two algorithms, one answer, different things known",
                "minutes": 7,
                "questions": [
                    {
                        "q": "What does a distance vector node actually put in the message it sends its neighbours?",
                        "opts": [
                            "Its forwarding table's next hops, without the costs",
                            "The links it is directly attached to, and their costs",
                            "The shortest paths it has found, as lists of nodes",
                            "Its current cost to every destination it knows about",
                        ],
                        "a": 3,
                        "why": r"""
A distance *vector* is a vector of distances: destination, cost, and nothing else. That
is the whole protocol — a node adds the cost of the link to each advertised cost and
keeps the smallest, which is Bellman's equation applied locally and repeatedly.

Flooding your own links instead is link state, and it is what makes Dijkstra possible:
every node ends up with the graph. Sending whole paths would work and is what BGP does
for exactly the reason you would guess — a node that can see the path can see itself in
it, and refuse. And next hops without costs are unusable: the receiver has nothing to
add its link cost to and no way to compare two offers.
""",
                    },
                    {
                        "q": "The link A-B fails on the line A-B-C. Why does count-to-infinity happen?",
                        "opts": [
                            "B accepts C's advertised route to A without being able to see that the route runs back through B",
                            "The link costs are large enough that the sum overflows before it converges",
                            "B and C update at different times, so one of them uses a stale table",
                            "The graph acquires a negative cycle when the link cost becomes infinite",
                        ],
                        "a": 0,
                        "why": r"""
C says *I can reach A at cost 2*, and that is true right up until it isn't — C's route
goes through B, and B has just lost its own. B has no way to know that: a distance
vector carries a number, not a path, so the loop is invisible from inside it. B adopts
cost 3, tells C, C adopts 4, and the two of them walk each other up one hop per round.

The costs are small here and nothing overflows. Synchrony is not the cause either — the
exchange in the lab is perfectly synchronous and still counts to infinity. And there is
no negative cycle: every cost is positive, which is the case where Bellman-Ford is
supposed to be at its most comfortable.
""",
                    },
                    {
                        "q": "Why does RIP treat 16 as infinity?",
                        "opts": [
                            "Because no real network has a diameter greater than 16 hops",
                            "So that counting to infinity terminates quickly — a larger ceiling only means longer before the routers give up",
                            "Because the hop count field is four bits wide",
                            "Because Dijkstra needs a finite upper bound to terminate",
                        ],
                        "a": 1,
                        "why": r"""
Sixteen is a deadline, not a measurement. When a route dies, the counting proceeds one
round per exchange until it reaches the ceiling, so the ceiling *is* the convergence
time: raise it to a thousand and the same failure takes a thousand rounds to clear. The
price is a hard limit on network diameter, which is the trade RIP accepted and the
reason it does not scale.

Plenty of networks are wider than 16 hops — they simply cannot run RIP. Sixteen needs
five bits, not four, and the field was never short of room in the first place: RIP gives
every route entry a four-octet metric, in RFC 1058 and in RFC 2453 after it. And Dijkstra
never sees an infinity: it is the other algorithm, running on a real graph.
""",
                    },
                    {
                        "q": "What does split horizon do?",
                        "opts": [
                            "A node waits a fixed number of rounds before advertising any route that got worse",
                            "A node advertises the route back to that neighbour with a cost of infinity",
                            "A node does not advertise a route back to the neighbour it learned that route from",
                            "A node advertises only routes whose cost is below half of infinity",
                        ],
                        "a": 2,
                        "why": r"""
Silence, not a statement. If B's route to A goes through C, B says nothing about A when
it talks to C — because whatever B knows about A, C told it, and echoing it back is
where the loop comes from. In the lab that is one `continue` in the middle of the
update.

Advertising it back at infinity is *poison reverse*, a real and closely related
technique: it says the same thing out loud instead of by omission, which is faster
because the neighbour learns immediately rather than waiting to time the route out.
Waiting before accepting worse news is a hold-down timer, a third mechanism again. None
of the three is a cure — all of them fail on loops of three or more nodes.
""",
                    },
                    {
                        "q": "On a static graph, link state and distance vector produce the same distances. What genuinely differs?",
                        "opts": [
                            "Link state needs a central controller to compute the routes",
                            "Link state finds shorter paths, because Dijkstra is optimal and Bellman-Ford is a heuristic",
                            "Distance vector cannot handle links whose cost differs in each direction",
                            "What each node knows: link state floods the topology and every node runs Dijkstra on the whole graph, while a distance vector node never sees the graph at all",
                        ],
                        "a": 3,
                        "why": r"""
Both are shortest-path algorithms and both are exact, so on a fixed graph they agree —
the lab checks that node by node. What differs is the information each node holds, and
that is what decides the failure modes: distance vector cannot see a loop it is part of,
while link state has to get an identical copy of the topology to every node and misroutes
badly when one of them disagrees.

Bellman-Ford is exact, not approximate; it is slower and it handles negative edges,
which Dijkstra cannot. Asymmetric costs are fine for both. And link state is
emphatically not centralised — every router computes for itself, from a database it
built out of flooded advertisements.
""",
                    },
                ],
            },
            "blanks": {
                "title": "One node, one destination, one exchange",
                "minutes": 9,
                "caption": "dv.py — the Bellman-Ford update, four holes",
                "lang": "python",
                "brief": r"""
This is the inner loop of a distance vector node: for one destination, look at what each
neighbour is advertising, add the cost of the link to that neighbour, and keep the best.
The whole protocol is here, split horizon included.

Nothing is executed here — you are choosing names, not writing code.
""",
                "listing": r'''
# `node` is us; `dest` is the destination we are recomputing.
# tables[v][d] is the (cost, next_hop) pair neighbour v is advertising for d.

best, hop = INFINITY, None
for neighbour, weight in sorted(graph[node].items()):
    cost, advertised_hop = tables[neighbour][dest]
    if split_horizon and advertised_hop == ___:
        continue                        # a route back through us is not a route
    total = min(___ + cost, INFINITY)   # our link, then their remaining distance
    if total < best:
        best, hop = total, ___
table[dest] = (best, hop) if best < INFINITY else (INFINITY, ___)
''',
                "blanks": [
                    {
                        "prompt": "Split horizon skips a neighbour whose route to this destination goes back through whom?",
                        "hole": "?",
                        "opts": ["node", "dest", "neighbour", "hop"],
                        "a": 0,
                        "why": "The guard is about *us*: if the neighbour reaches the destination by sending traffic to `node`, then their advertised cost is really our own cost with a link added, and believing it is how the count to infinity starts.",
                        "whys": [
                            "The guard is about *us*: if the neighbour reaches the destination by sending traffic to `node`, then their advertised cost is really our own cost with a link added, and believing it is how the count to infinity starts.",
                            "A next hop equal to the destination just means the neighbour is directly attached to it — the single most trustworthy advertisement there is. Skipping it discards the best routes and keeps the worst.",
                            "`advertised_hop == neighbour` says the neighbour reaches the destination through itself, which is a comparison that never usefully holds. The guard would fire almost never and split horizon would do nothing.",
                            "`hop` is the best next hop found so far in this loop and has nothing to do with what the neighbour is claiming. It also changes as the loop runs, so the guard would depend on the order neighbours are visited.",
                        ],
                    },
                    {
                        "prompt": "Bellman-Ford: the cost of getting to the neighbour, plus what the neighbour says the rest costs.",
                        "hole": "?",
                        "opts": ["best", "weight", "INFINITY", "1"],
                        "a": 1,
                        "why": "`weight` is the cost of our own link to this neighbour — the one piece of the sum we know first-hand. Everything beyond it is hearsay, and adding our link to their claim is the entire recursion.",
                        "whys": [
                            "`best` is the answer this loop is computing, and feeding it back into its own recurrence stops the recurrence from ever starting: `best` begins at `INFINITY`, so `min(best + cost, INFINITY)` is `INFINITY` for the first neighbour, `total < best` is false, and `best` is therefore never lowered — for that neighbour or any after it. The node finishes the round declaring every destination but itself unreachable.",
                            "`weight` is the cost of our own link to this neighbour — the one piece of the sum we know first-hand. Everything beyond it is hearsay, and adding our link to their claim is the entire recursion.",
                            "Adding the ceiling to everything pins `total` at `INFINITY` for every neighbour, so nothing ever beats the `INFINITY` that `best` started at. The tables do not merely stand still, either: a round rebuilds each table from scratch, so this erases even the direct-neighbour costs the initial tables were seeded with and leaves every node knowing only itself.",
                            "Counting one per link is the special case where every cost is 1, which is what a pure hop count does. It converges, and it routes traffic down a congested single hop in preference to two fast ones.",
                        ],
                    },
                    {
                        "prompt": "We have found a better route. Which way do we send the traffic?",
                        "hole": "?",
                        "opts": ["advertised_hop", "dest", "neighbour", "node"],
                        "a": 2,
                        "why": "A forwarding table holds the *next* hop, not the destination and not the rest of the path. We hand the packet to the neighbour whose advertisement won, and what that neighbour does with it afterwards is its own business.",
                        "whys": [
                            "That is the neighbour's next hop, two steps down the path. Forwarding to it would skip the neighbour entirely, and there is generally no link that way.",
                            "Storing the destination as the next hop is only right when the destination is directly attached. Anywhere else it names a node we cannot hand a packet to, because there is no link to it.",
                            "A forwarding table holds the *next* hop, not the destination and not the rest of the path. We hand the packet to the neighbour whose advertisement won, and what that neighbour does with it afterwards is its own business.",
                            "`node` is us, so this points the route back at ourselves and forwards the packet in a tight loop until its time-to-live runs out.",
                        ],
                    },
                    {
                        "prompt": "No neighbour offered anything under the ceiling. What next hop goes in the table?",
                        "hole": "?",
                        "opts": ["INFINITY", "node", "hop", "None"],
                        "a": 3,
                        "why": "An unreachable destination has no next hop, and saying so explicitly is what lets the rest of the code — and the tests — tell *no route* apart from a route that merely costs a lot. The lab compares tables for equality to decide convergence, so a stale hop left beside an infinite cost would keep the exchange running.",
                        "whys": [
                            "`INFINITY` is a cost, and this slot holds a neighbour's name. A later lookup would try to forward a packet to the node called 16.",
                            "Pointing an unreachable destination back at ourselves is a route to nowhere that looks like a route. Worse, it is the shape of entry that split horizon reads as *we own this*, so neighbours would be told to stay away from a destination nobody can reach.",
                            "`hop` is whatever the loop last assigned, which for an unreachable destination is `None` anyway — but only by accident, and only until someone reorders the loop. Saying `None` outright is the difference between correct and correct-for-now.",
                            "An unreachable destination has no next hop, and saying so explicitly is what lets the rest of the code — and the tests — tell *no route* apart from a route that merely costs a lot. The lab compares tables for equality to decide convergence, so a stale hop left beside an infinite cost would keep the exchange running.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "What does the shortest path cost?",
                "minutes": 8,
                "brief": r"""
This is what a link-state router does the moment the flooding settles: the topology is
ordinary local data by then, and finding the routes is a plain single-source shortest
path. Do it by hand once and the tie-breaking, the settled set and the reason greedy
works stop being incantations.
""",
                "prompt": "What is the total cost of the cheapest path from A to F?",
                "note": "Costs are symmetric and every one is positive. Answer with the total cost, not the number of hops.",
                "figure": r"""
```python
graph = {
    "A": {"B": 4, "C": 2},
    "B": {"A": 4, "C": 1, "D": 5},
    "C": {"A": 2, "B": 1, "D": 8, "E": 10},
    "D": {"B": 5, "C": 8, "E": 2, "F": 6},
    "E": {"C": 10, "D": 2, "F": 3},
    "F": {"D": 6, "E": 3},
}
```

```text
   the same nine links, cheapest first

   B-C   1      A-C   2      D-E   2
   E-F   3      A-B   4      B-D   5
   D-F   6      C-D   8      C-E  10
```
""",
                "given": [
                    {"label": "Source", "value": "A"},
                    {"label": "Destination", "value": "F"},
                    {"label": "Links", "value": "9, undirected"},
                    {"label": "Costs", "value": "all positive"},
                ],
                "aside": "Two direct links are traps. A-B at 4 and D-F at 6 each look like the "
                         "obvious move at the moment you meet them, and neither is on the cheapest "
                         "path — both lose to a detour by exactly one.",
                "answer": 13,
                "tol": 0.5,
                "unit": "",
                "hint": "Settle nodes in increasing order of their distance from A, relaxing each "
                        "settled node's edges once. Keep a running table of the best cost known to "
                        "every node; a node is only finished when you pop it.",
                "wrong": "If you got 14, check the two direct links. Reaching B costs 3 through C, "
                         "not the 4 the A-B edge advertises, and leaving D costs 5 through E, not "
                         "the 6 the D-F edge advertises.",
                "why": r"""
Settle in order: A at 0; C at 2; then B at 3, because 2 + 1 through C beats the direct
link at 4; then D at 8, via B; then E at 10, via D; then F at 13, via E. The path is
A-C-B-D-E-F.

Both of the tempting direct edges lose by exactly one. Note that the very first hop of
the cheapest path to F is A-C, which is also the cheapest single edge out of A — but
that is a coincidence of this graph, not a rule. What *is* a rule is why the algorithm
may commit to C: every remaining edge has positive cost, so no route that leaves A by a
more expensive edge can ever come back and undercut a distance of 2. Put one negative
edge in and that argument collapses, which is precisely the case Dijkstra is not allowed
to touch and Bellman-Ford is.
""",
            },
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
            "read": [
                {
                    "title": "Reading a text protocol exactly, and asking the right server",
                    "minutes": 12,
                    "body": r'''
Here is what a browser sends when you ask it for a page, with every line ending made
visible:

```text
GET /index.html HTTP/1.1\r\n
Host: shop.example.com\r\n
Accept: text/html\r\n
\r\n
```

It is text, and that is the trap. It *looks* like something you could read with
`split("\n")` and a couple of string methods, and on the request above that would even
work. But this is a wire format: every one of those `\r\n` pairs is data the parser
counts, the body that may follow has a length that has to be found before it can be
read, and the sender is a stranger who may be careless or hostile. The lab, *An
HTTP/1.1 parser and a recursive resolver*, has you write the parser as if you believed
that, and then a second protocol whose difficulty is not the grammar but the walk.

## Where the head ends

An HTTP/1.1 message is a start line, then zero or more header lines, then an empty
line, then a body. Each line ends in CRLF — carriage return, line feed, `\r\n` — so an
empty line is two CRLFs back to back, and the four bytes `\r\n\r\n` are the only thing
separating head from body. That is the first thing the parser looks for, before it
reads a single header: find the boundary, split there, and everything after it is body
bytes to be dealt with later. No boundary means no message, and the parser refuses
rather than guesses.

The start line of a request is three tokens separated by single spaces: a method, a
target and a version. Each header line is a field name, a colon, and a value that may
have whitespace around it to be stripped. Two rules about field names come straight
from the specification and both matter to the lab. Names are case-insensitive, so
`Content-Length`, `content-length` and `CONTENT-LENGTH` are one field, and the parser
stores every name lowercased so that lookups do not depend on the sender's habits. And
a field may appear more than once, in which case the message means the same as one
field whose value is the two values joined by a comma, in the order they arrived —
`X-Tag: a` then `X-Tag: b` is `x-tag: a, b`. A plain dictionary assignment would let
the second silently overwrite the first, and a parser that disagrees with the next
parser down the line about what a message said is how request smuggling starts.

```python
CRLF = b"\r\n"


def split_head(raw):
    marker = raw.find(CRLF + CRLF)
    if marker == -1:
        raise ValueError("no blank line between the headers and the body")
    return raw[:marker], raw[marker + 4:]


def parse_headers(lines):
    headers = {}
    for line in lines:
        name, _, value = line.partition(b":")
        key = name.decode("latin-1").lower()
        value = value.decode("latin-1").strip()
        headers[key] = headers[key] + ", " + value if key in headers else value
    return headers


raw = (b"POST /api/orders HTTP/1.1\r\nHost: shop.example.com\r\n"
       b"Content-Length: 15\r\nX-Tag: a\r\nX-Tag: b\r\n\r\n"
       b'{"units": 4711}')
head, body = split_head(raw)
lines = head.split(CRLF)
print(lines[0].split(b" "))
headers = parse_headers(lines[1:])
print(headers)
print(body[:int(headers["content-length"])])
```

The first line prints the three tokens of the request line as bytes. The second prints
the header dictionary, with `x-tag` holding `a, b` and `host` holding its value with
the leading space gone. The third prints the fifteen-byte body, which is exactly the
lab's first test. Notice `partition(b":")`: it splits at the *first* colon and leaves
any later ones in the value, which is what keeps `Host: shop.example.com:8080` in one
piece. The lab's version adds the checks this one leaves out — a line with no colon, an
empty name, whitespace between the name and the colon — and raises `HttpError` for each,
because every one of them is a message some other implementation would read
differently.

## Framing the body

The head is self-delimiting; the body is not. Nothing in the bytes of a body says where
it stops, so the head has to say it, and there are two ways. `Content-Length: 15` says
the body is exactly fifteen bytes, and the parser takes fifteen and no more — a longer
buffer is truncated, a shorter one is an error, because a receiver that waits for bytes
that never come hangs until something times out.

The problem with `Content-Length` is that it has to be written before the first byte of
the body goes out, so the sender has to know the whole body's size in advance. A server
streaming a file it is still generating does not. Chunked transfer encoding solves that
by replacing one length known ahead of time with many lengths, each known at the moment
its chunk goes out: the body becomes a sequence of chunks, each announced by its size on
a line of its own, followed by that many bytes, followed by CRLF; a chunk of size zero
says *that was all*.

Two details of that format trip people up, and both are visible in the example below.
The size is written in hexadecimal with no prefix, so twelve bytes are announced as
`c`, not `12` — and `12` is a valid size line meaning eighteen, so a decoder that reads
it as decimal runs six bytes past the end of the chunk and fails somewhere further on,
in a way that does not point back at the cause. And the CRLF after the data is framing,
not payload: it is not counted in the size and not copied into the output.

```python
CRLF = b"\r\n"


def decode_chunked(body):
    out, index = bytearray(), 0
    while True:
        end = body.find(CRLF, index)
        if end == -1:
            raise ValueError("chunk size line is not terminated")
        size = int(body[index:end].split(b";")[0], 16)
        index = end + 2
        if size == 0:
            return bytes(out)
        if body[index + size:index + size + 2] != CRLF:
            raise ValueError("chunk is not terminated by CRLF")
        out += body[index:index + size]
        index += size + 2


stream = b"7\r\nMozilla\r\n9\r\nDeveloper\r\n7\r\nNetwork\r\n0\r\n\r\n"
print(decode_chunked(stream))
print(decode_chunked(b"c;note=ignored\r\nchunked body\r\n0\r\n\r\n"))
```

The first line prints the three chunks joined: `MozillaDeveloperNetwork`. The second
shows a chunk extension — anything after a `;` on the size line — being ignored, and a
size of `c` being read as twelve. What the lab adds is the truncation check: a size that
promises more bytes than the body holds must raise, not slice past the end and return a
short result as if it were whole.

Where the grammar stops holding is worth knowing before you go further. This parser
handles one message that has already arrived complete; a real server reads from a
stream where the next request may begin in the same buffer, so `Content-Length` decides
where the next message starts as well as where this one ends. A message carrying both
`Content-Length` and `Transfer-Encoding: chunked` is ambiguous, and two implementations
that resolve the ambiguity differently can be made to disagree about where one request
ends and the next begins — that is request smuggling, and the specification's answer is
to reject such a message outright. And HTTP/2 abandons the text framing entirely for
binary frames with explicit lengths, keeping the meaning of the fields and discarding
every CRLF. What you are parsing here is the wire format of HTTP/1.1, and it is still
most of what crosses the internet.

## Finding the server to ask

Before any of that can happen the browser needs an address for `shop.example.com`, and
the store that maps names to addresses is not a single server anywhere. It is a
hierarchy of delegations. The root servers do not know `shop.example.com`; they know
who is responsible for `com`. The `com` servers do not know it either; they know who is
responsible for `example.com`. That server knows. A resolver walks down: ask the root,
get referred, ask the referral, get referred, ask again, get an answer.

The rule for a referral is a suffix match on a label boundary, longest zone first. A
server holding delegations for both `com` and `example.com` sends `www.example.com` to
the more specific one, and it must send `notexample.com` to the `com` servers, not to
`example.com` — the name ends in the characters `example.com` but not in the label. The
lab's `referral_for` test checks that boundary exactly, and
`name == zone or name.endswith("." + zone)` is the whole of it.

Sometimes the answer is not an address but another name: `www.example.com` is an alias,
a CNAME, for `static.cdn.com`. The resolver resolves the target, from the root, and the
trace of servers it visited grows to include both walks. An alias can point at an
alias, and two aliases can point at each other, and a resolver that follows them
without a limit recurses until it runs out of stack. The lab caps the chain at eight
and raises `ResolutionError` beyond that.

```python
class NameServer:
    def __init__(self, name, records=None, referrals=None):
        self.name = name
        self.records = dict(records or {})
        self.referrals = dict(referrals or {})

    def referral_for(self, name):
        best = None
        for zone, server in self.referrals.items():
            if name == zone or name.endswith("." + zone):
                if best is None or len(zone) > len(best[0]):
                    best = (zone, server)
        return best[1] if best else None


class Resolver:
    def __init__(self, servers, ttl=30):
        self.servers, self.ttl, self.clock, self.cache = servers, ttl, 0, {}

    def resolve(self, name, depth=0):
        if depth > 8:
            raise RuntimeError("alias chain too long")
        cached = self.cache.get(name)
        if cached is not None and cached[1] > self.clock:
            return cached[0], ["cache"]
        trace, server = [], self.servers["root"]
        while True:
            trace.append(server.name)
            if name in server.records:
                value = server.records[name]
                if isinstance(value, tuple):
                    address, rest = self.resolve(value[1], depth + 1)
                    trace += rest
                else:
                    address = value
                self.cache[name] = (address, self.clock + self.ttl)
                return address, trace
            nxt = server.referral_for(name)
            if nxt is None:
                raise LookupError(name)
            server = self.servers[nxt]


servers = {
    "root": NameServer("root", referrals={"com": "com-gtld"}),
    "com-gtld": NameServer("com-gtld", referrals={"example.com": "ns.example.com",
                                                  "cdn.com": "ns.cdn.com"}),
    "ns.example.com": NameServer("ns.example.com",
                                 records={"www.example.com": ("CNAME", "static.cdn.com")}),
    "ns.cdn.com": NameServer("ns.cdn.com", records={"static.cdn.com": "203.0.113.9"}),
}
resolver = Resolver(servers)
print(resolver.resolve("www.example.com"))
print(resolver.resolve("www.example.com"))
resolver.clock += 30
print(resolver.resolve("www.example.com"))
```

The first line shows the address and a six-server trace: root, `com`, `example.com`'s
server, which answers with an alias, then root, `com` and `cdn.com`'s server for the
target. The second line is the same address with a trace of `["cache"]`: nobody was
asked. The third, thirty seconds later, is the full walk again.

## The cache is the whole economy

Every one of those server visits is a round trip, and the module's numeric unit puts
numbers on it: 160 ms of the 220 ms before a page's first byte is naming. The cache is
what makes the second visit fast, and it is what lets a few hundred root servers answer
for the whole internet, because almost nobody asks them anything twice.

The rule is that an answer is stored with an expiry of *now plus the TTL* and is valid
while that expiry is still in the future. Both halves of that rule get broken. Expiry
at `clock + ttl` and validity while `expiry > clock` mean an entry fetched at time 0
with a 30-second TTL answers at 29 and is stale at 30 — not at 31 — and the lab's cache
test checks that instant on both sides. The other, worse mistake is to refresh the
expiry every time the entry is read. It is tempting because it feels like the cache is
doing its job — popular names stay warm. But the TTL was set by whoever published the
record, and it is their statement of how long the world is permitted to believe the old
address; a resolver that renews on every hit would never let a busy name change at all.
The clock counts down from the fetch, and only a fresh fetch resets it.

The lab's resolver is a model in the ways that matter for building the real thing and
not in the ways that do not. It has no network, no timeouts and no retries, and its
clock is a number you advance by hand — which is exactly why its traces are exact and
every test can name the servers a lookup must visit, in order. What it keeps is the
shape: delegation by suffix, aliases followed by recursion with a depth guard, and a
cache whose expiry belongs to the publisher. Those are what you are about to build.
''',
                },
            ],
            "quiz": {
                "title": "Reading a text protocol exactly",
                "minutes": 7,
                "questions": [
                    {
                        "q": "Where does the head of an HTTP/1.1 message end?",
                        "opts": [
                            "At the first CRLF CRLF — an empty line",
                            "At the first CRLF",
                            "`Content-Length` bytes from the start of the message",
                            "At the first line that does not contain a colon",
                        ],
                        "a": 0,
                        "why": r"""
An empty line closes the header section, which on the wire is two CRLFs back to back.
That is the only thing separating the head from the body, and it is why the parser hunts
for `\r\n\r\n` before it looks at anything else.

A single CRLF ends one line, not the section. `Content-Length` measures the body and
cannot be read until the headers are parsed, so it cannot possibly delimit them. And a
line without a colon is not a terminator, it is a malformed header — treating it as the
end of the head is a request-smuggling bug waiting to be written.
""",
                    },
                    {
                        "q": "A request carries both `Accept-Encoding: gzip` and `accept-encoding: br`. What is true?",
                        "opts": [
                            "They are different fields, because header names are case-sensitive",
                            "They are the same field, because field names are case-insensitive",
                            "The second is ignored, because a field may appear only once",
                            "The lowercase form is invalid and the message must be rejected",
                        ],
                        "a": 1,
                        "why": r"""
Field names are case-insensitive, which is why the parser lowercases every name as it
stores it — comparing `headers["accept-encoding"]` should not depend on how the sender
felt about capitals. HTTP/2 went further and made lowercase the only legal form on the
wire.

The repeat is legal here too, and the two lines mean exactly what one
`accept-encoding: gzip, br` would mean — which is why the lab joins repeats with a comma
rather than letting the last one win. That is not a general licence, though: RFC 7230
§3.2.2 permits a field to be sent more than once only when its value is defined as a
comma-separated list, as `Accept-Encoding` is. `Host` is the field to remember on the
other side of that line — §5.4 requires a server to answer 400 to a request carrying two
of them. Silently dropping a repeat that *is* legal is how two pieces of software end up
disagreeing about what a message said, and disagreement between a proxy and an origin
server is what request smuggling is made of.
""",
                    },
                    {
                        "q": "What is on the size line of a chunk?",
                        "opts": [
                            "The number of chunks still to come",
                            "The number of data bytes in that chunk, in decimal",
                            "The number of data bytes in that chunk, in hexadecimal, optionally followed by `;` and parameters",
                            "The total length of the whole body",
                        ],
                        "a": 2,
                        "why": r"""
Hexadecimal, with no `0x` prefix, and anything after a semicolon is a chunk extension the
decoder is free to skip. A body of twelve bytes is announced as `c`. Writing `12` instead
is the classic way to desynchronise a decoder from its stream, and it is quiet because
`12` is a perfectly valid size line — it just means eighteen.

The point of the format is that each chunk is self-delimiting *locally*: the sender never
has to know how many chunks it will send or how long the body will end up. Both of those
counts would be impossible to write at the moment the first chunk goes out.
""",
                    },
                    {
                        "q": "Why does chunked transfer encoding exist?",
                        "opts": [
                            "HTTP/1.1 requires it for every response body",
                            "It compresses the body, which `Content-Length` cannot express",
                            "It lets the receiver reassemble a body that arrived out of order",
                            "The sender can start transmitting before it knows how long the body will be",
                        ],
                        "a": 3,
                        "why": r"""
`Content-Length` has to be written before the first byte of the body, so it forces the
sender to buffer the whole response — impossible for output that is being generated as it
goes, or streamed from somewhere else. Chunking replaces one length known in advance with
a series of lengths known just in time, and the terminating zero-length chunk is what says
*that was all of it*.

Compression is a separate header and a separate mechanism, and the two compose. Ordering
is TCP's job — HTTP never sees an out-of-order byte. And chunking is optional: a response
whose length is known simply sends `Content-Length` and is done.
""",
                    },
                    {
                        "q": "A resolver holds `shop.example.com` with a 30-second TTL; 12 seconds have passed. Another query for the same name arrives. What happens?",
                        "opts": [
                            "It is answered from the cache and no server is queried",
                            "The authoritative server is queried to confirm, but the root and TLD are not",
                            "The full walk from the root repeats, and the cache only saves the last step",
                            "The cached entry is returned and its TTL restarts at 30 seconds",
                        ],
                        "a": 0,
                        "why": r"""
A live cache entry is the answer. Nobody is asked, nothing is confirmed, and the whole
root-TLD-authoritative walk is skipped — which is the entire reason the root servers can
serve the internet from a few hundred machines rather than a few hundred thousand.

Refreshing the TTL on every hit would be the serious mistake: a popular name would then
never expire, and the zone's owner would lose the ability to move it. The TTL is set by
whoever published the record precisely so they can say how long the world is allowed to
be wrong about it, and it counts down from when the record was fetched.
""",
                    },
                ],
            },
            "blanks": {
                "title": "One exchange, byte for byte",
                "minutes": 9,
                "caption": "a chunked request and its answer, with every CRLF made visible",
                "lang": "text",
                "brief": r"""
Line endings are shown as `<CRLF>` because they are data here, not layout: the parser
counts them. Fill the holes so the exchange is one a conforming server would accept and
a conforming client would understand.
""",
                "listing": r'''
--- request -------------------------------------------------
POST /orders HTTP/1.1<CRLF>
Host: shop.example.com<CRLF>
X-Tag: a<CRLF>
X-Tag: b<CRLF>
Transfer-Encoding: ___<CRLF>
<CRLF>
___<CRLF>
chunked body<CRLF>
0<CRLF>
<CRLF>

--- response ------------------------------------------------
HTTP/1.1 200 OK<CRLF>
Content-Type: application/json<CRLF>
Content-Length: ___<CRLF>
<CRLF>
{"id":7}

--- what the parser hands back ------------------------------
request["body"]              == b"chunked body"
request["headers"]["x-tag"]  == "___"
''',
                "blanks": [
                    {
                        "prompt": "The body's length is not known when the head goes out.",
                        "hole": "?",
                        "opts": ["identity", "chunked", "gzip", "none"],
                        "a": 1,
                        "why": "`chunked` is the transfer coding that frames a body as a run of self-sized pieces. It is the alternative to `Content-Length`, not an addition to it — a message carrying both is ambiguous and a careful parser rejects it outright.",
                        "whys": [
                            "`identity` means no transfer coding at all, which leaves the body unframed: the receiver would read the size line as the first bytes of the payload and keep going until the connection closed.",
                            "`chunked` is the transfer coding that frames a body as a run of self-sized pieces. It is the alternative to `Content-Length`, not an addition to it — a message carrying both is ambiguous and a careful parser rejects it outright.",
                            "`gzip` is a coding, but a compressing one, and it changes the bytes without saying where they stop. Compression belongs in `Content-Encoding`; framing is a separate job and still has to be done.",
                            "There is no such value, and an unrecognised transfer coding is a message the receiver must refuse rather than guess at.",
                        ],
                    },
                    {
                        "prompt": "`chunked body` is twelve bytes long. How is that announced?",
                        "hole": "?",
                        "opts": ["13", "12", "c", "24"],
                        "a": 2,
                        "why": "Chunk sizes are hexadecimal, so twelve is written `c`. Nothing on the line says which base it is in, which is what makes the mistake so easy and so quiet: a decoder that reads it as decimal simply cuts the stream in the wrong place.",
                        "whys": [
                            "Thirteen is twelve plus one, as though the line ending after the data were a single byte. It is two, which is the whole reason this listing spells every one of them `<CRLF>` — and neither byte counts in any case: the terminator is framing, not payload, and the size line measures the data alone.",
                            "Twelve in decimal parses as hexadecimal too — as eighteen. The decoder would run six bytes past the end of the chunk, swallow the CRLF and the next size line, and then fail on whatever it found there.",
                            "Chunk sizes are hexadecimal, so twelve is written `c`. Nothing on the line says which base it is in, which is what makes the mistake so easy and so quiet: a decoder that reads it as decimal simply cuts the stream in the wrong place.",
                            "Twenty-four is the number of hexadecimal digits it would take to write the payload out, not the number of bytes in it.",
                        ],
                    },
                    {
                        "prompt": "The response body `{\"id\":7}` is framed by its length.",
                        "hole": "?",
                        "opts": ["10", "9", "7", "8"],
                        "a": 3,
                        "why": "Eight characters, eight bytes, all of them ASCII. `Content-Length` counts the octets of the body and nothing else — not the head, not the blank line that ends it, and not any line ending the body does not contain.",
                        "whys": [
                            "Ten counts a CRLF as well as the body. The blank line before the body belongs to the head, and there is no line ending after it.",
                            "Nine adds a trailing newline the body does not have. Overstating the length is the worse direction to be wrong in: the receiver waits for a byte that never comes, and the connection hangs until something times out.",
                            "Seven understates it by one, so the closing brace is left in the stream. On a reused connection that stray byte becomes the first byte of the next response, and everything after it is nonsense.",
                            "Eight characters, eight bytes, all of them ASCII. `Content-Length` counts the octets of the body and nothing else — not the head, not the blank line that ends it, and not any line ending the body does not contain.",
                        ],
                    },
                    {
                        "prompt": "The field appears twice. What does the parser store under `x-tag`?",
                        "hole": "?",
                        "opts": ["a, b", "b", "a", "ab"],
                        "a": 0,
                        "why": "Repeated fields combine into one value, joined by a comma, in the order they arrived — the message means exactly the same thing as a single `X-Tag: a, b`. Order is preserved because for some fields it matters, `Accept-Encoding` among them.",
                        "whys": [
                            "Repeated fields combine into one value, joined by a comma, in the order they arrived — the message means exactly the same thing as a single `X-Tag: a, b`. Order is preserved because for some fields it matters, `Accept-Encoding` among them.",
                            "Letting the last one win throws information away silently. It is what a plain dictionary assignment does, which is why the mistake is so common and why the lab makes you write the join by hand.",
                            "Keeping the earliest and discarding the rest loses the same information the other way round, and disagrees with every other implementation about what the message said.",
                            "Concatenating without a separator invents a value that was never sent: a parser splitting on commas downstream would see one token where the sender wrote two.",
                        ],
                    },
                ],
            },
            "numeric": {
                "title": "How long before the first byte?",
                "minutes": 8,
                "brief": r"""
A page feels slow before it has transferred anything, and this is why. Naming happens
before connecting, connecting happens before requesting, and every one of those is a
round trip that no amount of bandwidth shortens.
""",
                "prompt": "How long after the browser asks for the name does the first byte of the response arrive?",
                "note": "Ignore transmission time and all processing time — count only the round trips listed.",
                "figure": r"""
```text
 resolver cache: empty                       round trip
 ─────────────────────────────────────────────────────
 resolver  ->  root name server                  90 ms
 resolver  ->  .com name server                  45 ms
 resolver  ->  authoritative name server         25 ms
 browser   ->  web server: TCP connection setup  30 ms
 browser   ->  web server: GET, first byte back  30 ms
 ─────────────────────────────────────────────────────
```

The resolver is on the same machine as the browser, so asking it costs nothing.
No name in this hierarchy is an alias, and every step happens strictly after the one
above it.
""",
                "given": [
                    {"label": "Root query", "value": "90 ms"},
                    {"label": ".com query", "value": "45 ms"},
                    {"label": "Authoritative query", "value": "25 ms"},
                    {"label": "TCP setup", "value": "30 ms"},
                    {"label": "Request and response", "value": "30 ms"},
                ],
                "aside": "The three naming round trips are 160 of the 220 ms, and every one of them "
                         "disappears on the next page view. That gap between the first visit and the "
                         "second is the TTL cache doing its job.",
                "answer": 220,
                "tol": 0.5,
                "unit": "ms",
                "hint": "Add the three round trips that turn the name into an address, then the two "
                        "that the connection and the request cost. Nothing here overlaps.",
                "wrong": "The usual slip is to treat the connection as free because the third segment "
                         "of the handshake can carry the request. It cannot be free: the first two "
                         "segments are a full round trip that has to complete before the request may "
                         "go at all.",
                "why": r"""
$90 + 45 + 25 = 160$ ms to turn the name into an address, then 30 ms for the handshake
and 30 ms for the request and its answer: 220 ms in total, before a single byte of the
page exists.

The shape of that number is the useful part. Naming is nearly three quarters of it and is
pure round trips — which is why a resolver that caches aggressively feels like a faster
internet connection, and why the DNS is one of the few places where a warm cache changes
the experience more than a faster link does. The other 60 ms is the reason connection
reuse and TLS session resumption exist: every extra connection to the same server pays
those two round trips again.
""",
            },
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
