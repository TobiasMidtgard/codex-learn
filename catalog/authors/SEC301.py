"""SEC301 — Cybersecurity & Cryptography. Author module."""

COURSE = {
    "id": "SEC301",
    "title": "Cybersecurity & Cryptography",
    "year": 3,
    "level": "Advanced",
    "prereqs": ["CS320", "MA201"],
    "stack": ["Python"],
    "credits": 10,
    "hours": 140,
    "icon": "⚿",
    "summary": (
        "Cryptography built from primitives rather than imported from a library. You "
        "break a Vigenere cipher with frequency analysis, implement HMAC and PBKDF2 "
        "against published test vectors, expose the pattern leak in ECB mode with a "
        "toy block cipher, generate RSA keys with Miller-Rabin and sign with them, and "
        "watch a machine-in-the-middle silently own an unauthenticated Diffie-Hellman "
        "exchange. Every construction is attacked as well as built."
    ),
    "outcomes": [
        "Break a polyalphabetic cipher using the index of coincidence and chi-squared frequency analysis",
        "Implement HMAC-SHA256 and PBKDF2 from a hash function and validate them against published vectors",
        "Store passwords with a per-user salt, an iterated derivation and a constant-time comparison",
        "Demonstrate why ECB leaks plaintext structure and why a reused CTR nonce is catastrophic",
        "Generate RSA keys with Miller-Rabin primality testing and implement encryption and signatures",
        "Execute a machine-in-the-middle attack on unauthenticated Diffie-Hellman and explain the fix",
        "Assemble authenticated encryption from a KDF, a stream cipher and a MAC, and state its threat model",
    ],
    "assessment": "5 lab checkpoints (8% each) + capstone secure-vault build (60%).",
    "reading": [
        "Katz & Lindell, *Introduction to Modern Cryptography*, 3rd ed. (2020) — chapters 3, 4, 7, 11 and 12",
        "Ferguson, Schneier & Kohno, *Cryptography Engineering* (2010) — chapters 4-6 and 12",
        "RFC 2104 (HMAC) and RFC 8018 (PKCS #5 v2.1, PBKDF2) — the specifications the labs are tested against",
    ],
    "modules": [
        # ------------------------------------------------------------ M1
        {
            "title": "Classical ciphers and how they fall",
            "summary": "Vigenere, and the two statistics that undo it: the index of coincidence and letter frequency.",
            "concepts": [
                "A substitution cipher hides the letters but not the statistics of the language beneath them",
                "The index of coincidence: the chance two letters drawn from a text are equal, about 0.067 for English and 0.038 for uniform noise",
                "A repeating key leaves a period, and slicing the ciphertext by that period restores single-alphabet columns",
                "Kasiski and Friedman both find the period; the IC does it with one pass and no repeated trigrams",
                "Chi-squared scores a candidate shift against expected English frequencies without a dictionary",
                "Key recovery beats brute force: 26 tests per column instead of 26^k over the whole key",
                "The lesson generalises: a cipher must be judged by the structure it leaves behind, not by its key space",
            ],
            "lab": {
                "title": "Vigenere, and a full key recovery",
                "runtime": "python",
                "minutes": 65,
                "brief": r'''
`SAMPLE_TEXT`, the alphabet, the English letter frequencies and a
`letters_only` helper are given. Write the cipher and then the attack on it.

**`vigenere_encrypt(plaintext, key)` / `vigenere_decrypt(ciphertext, key)`** —
letters shift by the corresponding key letter, non-letters pass through
untouched and do **not** consume a key letter, and the case of the input is
preserved. A key that is empty or contains anything but letters raises
`ValueError`.

```text
vigenere_encrypt("ATTACKATDAWN", "LEMON")   ->  "LXFOPVEFRNHR"
vigenere_encrypt("Attack at dawn!", "lemon") ->  "Lxfopv ef rnhr!"
```

**`index_of_coincidence(text)`** — over the letters only, and 0.0 for fewer
than two letters:

```text
IC = sum over letters of n_i * (n_i - 1)  /  (N * (N - 1))
```

**`average_ic(ciphertext, length)`** — the mean IC of the `length` slices
`body[0::length]`, `body[1::length]`, ...

**`guess_key_length(ciphertext, max_length=16)`** — the smallest length whose
average IC reaches 0.06; if nothing does, the length with the highest average.

**`crack_column(column)`** — the shift 0-25 whose decryption best matches
English by the chi-squared statistic

```text
sum over letters of (observed - expected)^2 / expected
```

where `expected = ENGLISH_FREQ[letter] * len(column)`. Lower is better.

**`crack_key(ciphertext, key_length)`** and **`crack(ciphertext)`** — assemble
the key from the columns, then return `(key, plaintext)`.

The recovered key is lowercase. About twelve hundred letters is plenty.
''',
                "files": [{"name": "main.py", "content": r'''
import string

# ------------------------------------------------------------------ given
ALPHABET = string.ascii_lowercase

ENGLISH_FREQ = {
    "a": 0.08167, "b": 0.01492, "c": 0.02782, "d": 0.04253, "e": 0.12702,
    "f": 0.02228, "g": 0.02015, "h": 0.06094, "i": 0.06966, "j": 0.00153,
    "k": 0.00772, "l": 0.04025, "m": 0.02406, "n": 0.06749, "o": 0.07507,
    "p": 0.01929, "q": 0.00095, "r": 0.05987, "s": 0.06327, "t": 0.09056,
    "u": 0.02758, "v": 0.00978, "w": 0.02360, "x": 0.00150, "y": 0.01974,
    "z": 0.00074,
}

SAMPLE_TEXT = (
    "The study of secret writing is older than the printing press, and for most "
    "of that time the people who wrote ciphers were far more confident than the "
    "people who broke them had any reason to allow. A substitution cipher hides "
    "the shape of a letter but not the shape of a language. Vowels cluster, "
    "doubled letters repeat, short words appear again and again, and every one "
    "of those habits survives the journey through a naive cipher and arrives on "
    "the far side intact. The first analysts to notice this counted letters. "
    "They counted them by hand, on paper, in the margins of the messages they "
    "had intercepted, and they discovered that the frequency of a letter in a "
    "long passage of ordinary prose is remarkably stable. That stability is a "
    "weakness. It means the attacker does not need the key at all, only patience "
    "and a long enough message. The polyalphabetic cipher was invented to destroy "
    "that stability by moving the alphabet along as the message advances, and for "
    "three centuries it was thought to be beyond reach. It was not. A repeating "
    "key repeats, and a repeating key leaves a period in the ciphertext that can "
    "be measured. Once the period is known the message falls apart into columns, "
    "each of which is nothing more than a simple shift, and each of which "
    "surrenders to exactly the counting argument the polyalphabetic cipher was "
    "meant to defeat. The lesson is not that these ciphers were badly designed "
    "for their age. The lesson is that a cipher must be judged by what an "
    "adversary can do with the structure it leaves behind, and that structure is "
    "rarely as well hidden as its designer believes."
)


def letters_only(text):
    """Just the lowercase letters of text, in order."""
    return "".join(ch for ch in text.lower() if ch in ALPHABET)


# ------------------------------------------------------------- your code
def vigenere_encrypt(plaintext, key):
    """Shift each letter by the next key letter. ValueError on a bad key."""
    # your code here


def vigenere_decrypt(ciphertext, key):
    """The inverse of vigenere_encrypt."""
    # your code here


def index_of_coincidence(text):
    """The chance that two letters drawn from text are the same one."""
    # your code here


def average_ic(ciphertext, length):
    """Mean index of coincidence over the length slices of the ciphertext."""
    # your code here


def guess_key_length(ciphertext, max_length=16):
    """The smallest period whose average IC reaches 0.06."""
    # your code here


def crack_column(column):
    """The shift 0-25 whose plaintext best matches English by chi-squared."""
    # your code here


def crack_key(ciphertext, key_length):
    """Recover the key, one column at a time."""
    # your code here


def crack(ciphertext, max_length=16):
    """(key, plaintext) recovered from the ciphertext alone."""
    # your code here


secret = vigenere_encrypt(SAMPLE_TEXT, "cipher")
print("plaintext IC:  %.4f" % index_of_coincidence(SAMPLE_TEXT))
print("ciphertext IC: %.4f" % index_of_coincidence(secret))
print("key length:", guess_key_length(secret))
print("recovered key:", crack(secret)[0])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import string

# ------------------------------------------------------------------ given
ALPHABET = string.ascii_lowercase

ENGLISH_FREQ = {
    "a": 0.08167, "b": 0.01492, "c": 0.02782, "d": 0.04253, "e": 0.12702,
    "f": 0.02228, "g": 0.02015, "h": 0.06094, "i": 0.06966, "j": 0.00153,
    "k": 0.00772, "l": 0.04025, "m": 0.02406, "n": 0.06749, "o": 0.07507,
    "p": 0.01929, "q": 0.00095, "r": 0.05987, "s": 0.06327, "t": 0.09056,
    "u": 0.02758, "v": 0.00978, "w": 0.02360, "x": 0.00150, "y": 0.01974,
    "z": 0.00074,
}

SAMPLE_TEXT = (
    "The study of secret writing is older than the printing press, and for most "
    "of that time the people who wrote ciphers were far more confident than the "
    "people who broke them had any reason to allow. A substitution cipher hides "
    "the shape of a letter but not the shape of a language. Vowels cluster, "
    "doubled letters repeat, short words appear again and again, and every one "
    "of those habits survives the journey through a naive cipher and arrives on "
    "the far side intact. The first analysts to notice this counted letters. "
    "They counted them by hand, on paper, in the margins of the messages they "
    "had intercepted, and they discovered that the frequency of a letter in a "
    "long passage of ordinary prose is remarkably stable. That stability is a "
    "weakness. It means the attacker does not need the key at all, only patience "
    "and a long enough message. The polyalphabetic cipher was invented to destroy "
    "that stability by moving the alphabet along as the message advances, and for "
    "three centuries it was thought to be beyond reach. It was not. A repeating "
    "key repeats, and a repeating key leaves a period in the ciphertext that can "
    "be measured. Once the period is known the message falls apart into columns, "
    "each of which is nothing more than a simple shift, and each of which "
    "surrenders to exactly the counting argument the polyalphabetic cipher was "
    "meant to defeat. The lesson is not that these ciphers were badly designed "
    "for their age. The lesson is that a cipher must be judged by what an "
    "adversary can do with the structure it leaves behind, and that structure is "
    "rarely as well hidden as its designer believes."
)


def letters_only(text):
    """Just the lowercase letters of text, in order."""
    return "".join(ch for ch in text.lower() if ch in ALPHABET)


# ------------------------------------------------------------- your code
def check_key(key):
    """A usable Vigenere key, lowercased."""
    if not key or not key.isalpha():
        raise ValueError("the key must be one or more letters")
    return key.lower()


def shift_text(text, key, direction):
    """Shared machinery: direction is +1 to encrypt, -1 to decrypt."""
    key = check_key(key)
    out = []
    used = 0
    for ch in text:
        low = ch.lower()
        if low in ALPHABET:
            shift = ALPHABET.index(key[used % len(key)])
            moved = ALPHABET[(ALPHABET.index(low) + direction * shift) % 26]
            out.append(moved.upper() if ch.isupper() else moved)
            used += 1
        else:
            out.append(ch)
    return "".join(out)


def vigenere_encrypt(plaintext, key):
    """Shift each letter by the next key letter. ValueError on a bad key."""
    return shift_text(plaintext, key, 1)


def vigenere_decrypt(ciphertext, key):
    """The inverse of vigenere_encrypt."""
    return shift_text(ciphertext, key, -1)


def index_of_coincidence(text):
    """The chance that two letters drawn from text are the same one."""
    body = letters_only(text)
    n = len(body)
    if n < 2:
        return 0.0
    total = 0
    for letter in ALPHABET:
        count = body.count(letter)
        total += count * (count - 1)
    return total / (n * (n - 1))


def average_ic(ciphertext, length):
    """Mean index of coincidence over the length slices of the ciphertext."""
    body = letters_only(ciphertext)
    if length < 1 or length > len(body):
        return 0.0
    scores = [index_of_coincidence(body[start::length]) for start in range(length)]
    return sum(scores) / length


def guess_key_length(ciphertext, max_length=16):
    """The smallest period whose average IC reaches 0.06."""
    body = letters_only(ciphertext)
    best_length, best_score = 1, -1.0
    for length in range(1, max_length + 1):
        score = average_ic(body, length)
        if score >= 0.06:
            return length
        if score > best_score:
            best_length, best_score = length, score
    return best_length


def crack_column(column):
    """The shift 0-25 whose plaintext best matches English by chi-squared."""
    best_shift, best_score = 0, None
    size = len(column)
    for shift in range(26):
        plain = "".join(ALPHABET[(ALPHABET.index(ch) - shift) % 26] for ch in column)
        score = 0.0
        for letter in ALPHABET:
            expected = ENGLISH_FREQ[letter] * size
            observed = plain.count(letter)
            score += (observed - expected) ** 2 / (expected if expected else 1e-9)
        if best_score is None or score < best_score:
            best_shift, best_score = shift, score
    return best_shift


def crack_key(ciphertext, key_length):
    """Recover the key, one column at a time."""
    body = letters_only(ciphertext)
    return "".join(ALPHABET[crack_column(body[start::key_length])]
                   for start in range(key_length))


def crack(ciphertext, max_length=16):
    """(key, plaintext) recovered from the ciphertext alone."""
    key = crack_key(ciphertext, guess_key_length(ciphertext, max_length))
    return key, vigenere_decrypt(ciphertext, key)


secret = vigenere_encrypt(SAMPLE_TEXT, "cipher")
print("plaintext IC:  %.4f" % index_of_coincidence(SAMPLE_TEXT))
print("ciphertext IC: %.4f" % index_of_coincidence(secret))
print("key length:", guess_key_length(secret))
print("recovered key:", crack(secret)[0])
'''}],
                "hints": [
                    "Encryption and decryption differ only in the sign of the shift, so write one helper taking `+1` or `-1` and call it twice. Advance the key index only when you actually enciphered a letter.",
                    "The IC is a counting exercise: `count * (count - 1)` summed over the alphabet, divided by `n * (n - 1)`. Guard `n < 2` before you divide.",
                    "`body[start::length]` is the column of letters enciphered by key letter number `start` — that slice is a plain Caesar shift and nothing more.",
                    "Chi-squared compares the *shifted-back* column against `ENGLISH_FREQ[letter] * len(column)`. The winning shift is the smallest score, not the largest.",
                ],
                "tests": [
                    {"name": "The textbook vector, and its inverse", "code": r'''
_got = vigenere_encrypt("ATTACKATDAWN", "LEMON")
assert _got == "LXFOPVEFRNHR", f"encrypting ATTACKATDAWN with LEMON gave {_got!r}"
_got = vigenere_decrypt("LXFOPVEFRNHR", "LEMON")
assert _got == "ATTACKATDAWN", f"decrypting gave {_got!r}, expected ATTACKATDAWN"
assert vigenere_encrypt("hello", "a") == "hello", "a key of 'a' shifts by zero"
'''},
                    {"name": "Case and punctuation survive; the key only advances on letters", "code": r'''
_got = vigenere_encrypt("Attack at dawn!", "lemon")
assert _got == "Lxfopv ef rnhr!", f"got {_got!r}, expected 'Lxfopv ef rnhr!'"
_ct = vigenere_encrypt(SAMPLE_TEXT, "cipher")
assert len(_ct) == len(SAMPLE_TEXT), "the ciphertext has the same length as the plaintext"
assert vigenere_decrypt(_ct, "cipher") == SAMPLE_TEXT, "the round trip must be exact"
assert [i for i, ch in enumerate(_ct) if not ch.isalpha()] == \
       [i for i, ch in enumerate(SAMPLE_TEXT) if not ch.isalpha()], \
    "non-letters must stay exactly where they were"
'''},
                    {"name": "Bad keys are refused", "code": r'''
for _bad in ["", "lemon!", "12", " ", "le mon"]:
    try:
        vigenere_encrypt("hello", _bad)
        assert False, f"the key {_bad!r} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The index of coincidence separates English from noise", "code": r'''
assert index_of_coincidence("aaaa") == 1.0, \
    f"a text of one repeated letter has IC 1.0, got {index_of_coincidence('aaaa')!r}"
assert index_of_coincidence("A a! A") == 1.0, "punctuation and case are ignored"
assert index_of_coincidence("a") == 0.0 and index_of_coincidence("") == 0.0, \
    "fewer than two letters gives 0.0 rather than a ZeroDivisionError"
assert index_of_coincidence(ALPHABET) == 0.0, "26 distinct letters coincide never"
_plain = index_of_coincidence(SAMPLE_TEXT)
assert 0.06 < _plain < 0.08, f"English prose should score about 0.067, got {_plain:.4f}"
_ct = index_of_coincidence(vigenere_encrypt(SAMPLE_TEXT, "monarchy"))
assert _ct < 0.05, f"an 8-letter key should flatten the IC to about 0.042, got {_ct:.4f}"
'''},
                    {"name": "The period comes out of the ciphertext alone", "code": r'''
for _key in ["lemon", "cipher", "monarchy", "zebrastripe"]:
    _ct = vigenere_encrypt(SAMPLE_TEXT, _key)
    _got = guess_key_length(_ct)
    assert _got == len(_key), \
        f"a {len(_key)}-letter key was measured as period {_got}"
    _at_key = average_ic(_ct, len(_key))
    _at_wrong = average_ic(_ct, len(_key) + 1)
    assert _at_key > _at_wrong, \
        f"the true period should score higher: {_at_key:.4f} vs {_at_wrong:.4f}"
'''},
                    {"name": "Chi-squared recovers each column", "code": r'''
_column = letters_only(SAMPLE_TEXT)[:200]
assert crack_column(_column) == 0, "unshifted English is best explained by a shift of 0"
_shifted = "".join(ALPHABET[(ALPHABET.index(ch) + 7) % 26] for ch in _column)
assert crack_column(_shifted) == 7, f"a shift of 7 was read as {crack_column(_shifted)}"
for _key in ["lemon", "cipher", "monarchy"]:
    _ct = vigenere_encrypt(SAMPLE_TEXT, _key)
    _got = crack_key(_ct, len(_key))
    assert _got == _key, f"crack_key recovered {_got!r}, expected {_key!r}"
'''},
                    {"name": "End-to-end recovery from the ciphertext alone", "code": r'''
for _key in ["lemon", "cipher", "monarchy", "zebrastripe"]:
    _ct = vigenere_encrypt(SAMPLE_TEXT, _key)
    _recovered, _plain = crack(_ct)
    assert _recovered == _key, f"crack recovered the key {_recovered!r}, expected {_key!r}"
    assert _plain == SAMPLE_TEXT, "the recovered plaintext should be the original, exactly"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M2
        {
            "title": "Hashing, HMAC and password storage",
            "summary": "Why a hash is not a password store, and what to build instead.",
            "concepts": [
                "Preimage and collision resistance are what a hash promises; slowness is not among them",
                "A raw hash of a password is a lookup, not a secret: rainbow tables amortise the work across every user",
                "A per-user salt makes each password its own problem and kills precomputation",
                "HMAC is not `hash(key + message)`: the inner and outer padding exist to stop length-extension",
                "PBKDF2 iterates HMAC, folding every block with XOR so an attacker cannot skip work",
                "A derived key longer than the hash needs several blocks, each with its own counter",
                "Comparing digests with `==` leaks how many bytes matched; the fix is an XOR accumulator",
            ],
            "lab": {
                "title": "HMAC-SHA256 and PBKDF2 from scratch",
                "runtime": "python",
                "minutes": 65,
                "brief": r'''
Only `hashlib.sha256` and `secrets` are given. Everything else you build, and
the checks compare your output against the published vectors of RFC 4231 and
RFC 8018.

**`hmac_sha256(key, message)`** — RFC 2104 with SHA-256, block size 64:

```text
key longer than 64 bytes  ->  key = sha256(key).digest()
key shorter than 64 bytes ->  pad with zero bytes to 64
ipad = key xor 0x36 * 64      opad = key xor 0x5c * 64
HMAC = sha256(opad + sha256(ipad + message).digest()).digest()
```

**`pbkdf2(password, salt, iterations, dklen=32)`** — PBKDF2-HMAC-SHA256:

```text
block i (counting from 1):
  U1 = HMAC(password, salt + i as 4 big-endian bytes)
  Uj = HMAC(password, U(j-1))            for j = 2..iterations
  T_i = U1 xor U2 xor ... xor U_iterations
output = T_1 || T_2 || ...   truncated to dklen
```

`iterations` below 1 raises `ValueError`.

**`constant_time_equals(a, b)`** — compare two byte strings without leaking
where they differ. Accept `str` as well by encoding it. Different lengths give
`False`, and the comparison over equal lengths must look at every byte.

**`random_salt(size=16)`** — `size` bytes from `secrets`.

**`hash_password(password, iterations=DEFAULT_ITERATIONS)`** — a storable
record, four fields separated by `$`:

```text
pbkdf2_sha256$20000$<salt as hex>$<32-byte derived key as hex>
```

**`verify_password(password, stored)`** — split the record, derive with the
same salt and iteration count, and compare in constant time. A record that is
not four fields, or whose algorithm is not `pbkdf2_sha256`, raises `ValueError`.
''',
                "files": [{"name": "main.py", "content": r'''
import hashlib
import secrets

BLOCK_SIZE = 64          # SHA-256 processes 64-byte blocks
DIGEST_SIZE = 32
ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 20000


def hmac_sha256(key, message):
    """RFC 2104 HMAC with SHA-256. Returns 32 bytes."""
    # your code here


def pbkdf2(password, salt, iterations, dklen=32):
    """PBKDF2-HMAC-SHA256. ValueError when iterations < 1."""
    # your code here


def constant_time_equals(a, b):
    """Compare without revealing the position of the first difference."""
    # your code here


def random_salt(size=16):
    """size unpredictable bytes."""
    # your code here


def hash_password(password, iterations=DEFAULT_ITERATIONS):
    """A storable record: algorithm$iterations$salt$derived key."""
    # your code here


def verify_password(password, stored):
    """True when password reproduces the stored record."""
    # your code here


record = hash_password("correct horse battery staple", iterations=1000)
print(record)
print("right password:", verify_password("correct horse battery staple", record))
print("wrong password:", verify_password("Tr0ub4dor&3", record))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import hashlib
import secrets

BLOCK_SIZE = 64          # SHA-256 processes 64-byte blocks
DIGEST_SIZE = 32
ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 20000


def as_bytes(value):
    """UTF-8 encode a str, pass bytes through."""
    return value.encode("utf-8") if isinstance(value, str) else bytes(value)


def hmac_sha256(key, message):
    """RFC 2104 HMAC with SHA-256. Returns 32 bytes."""
    key = as_bytes(key)
    message = as_bytes(message)
    if len(key) > BLOCK_SIZE:
        key = hashlib.sha256(key).digest()
    key = key + b"\x00" * (BLOCK_SIZE - len(key))
    inner = bytes(b ^ 0x36 for b in key)
    outer = bytes(b ^ 0x5C for b in key)
    return hashlib.sha256(outer + hashlib.sha256(inner + message).digest()).digest()


def pbkdf2(password, salt, iterations, dklen=32):
    """PBKDF2-HMAC-SHA256. ValueError when iterations < 1."""
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    if dklen < 1:
        raise ValueError("dklen must be at least 1")
    password = as_bytes(password)
    salt = as_bytes(salt)
    out = b""
    block = 1
    while len(out) < dklen:
        current = hmac_sha256(password, salt + block.to_bytes(4, "big"))
        accumulator = current
        for _ in range(iterations - 1):
            current = hmac_sha256(password, current)
            accumulator = bytes(x ^ y for x, y in zip(accumulator, current))
        out += accumulator
        block += 1
    return out[:dklen]


def constant_time_equals(a, b):
    """Compare without revealing the position of the first difference."""
    a = as_bytes(a)
    b = as_bytes(b)
    if len(a) != len(b):
        return False
    difference = 0
    for x, y in zip(a, b):
        difference |= x ^ y
    return difference == 0


def random_salt(size=16):
    """size unpredictable bytes."""
    return secrets.token_bytes(size)


def hash_password(password, iterations=DEFAULT_ITERATIONS):
    """A storable record: algorithm$iterations$salt$derived key."""
    salt = random_salt()
    derived = pbkdf2(password, salt, iterations, DIGEST_SIZE)
    return f"{ALGORITHM}${iterations}${salt.hex()}${derived.hex()}"


def verify_password(password, stored):
    """True when password reproduces the stored record."""
    parts = stored.split("$")
    if len(parts) != 4:
        raise ValueError("a stored record has four fields")
    algorithm, iterations, salt_hex, expected_hex = parts
    if algorithm != ALGORITHM:
        raise ValueError(f"unsupported algorithm {algorithm!r}")
    derived = pbkdf2(password, bytes.fromhex(salt_hex), int(iterations), DIGEST_SIZE)
    return constant_time_equals(derived, bytes.fromhex(expected_hex))


record = hash_password("correct horse battery staple", iterations=1000)
print(record)
print("right password:", verify_password("correct horse battery staple", record))
print("wrong password:", verify_password("Tr0ub4dor&3", record))
'''}],
                "hints": [
                    "Normalise inputs first: one `as_bytes` helper that encodes `str` and passes `bytes` through keeps every later function honest about types.",
                    "The two HMAC pads are byte-wise XORs of the padded key: `bytes(b ^ 0x36 for b in key)` and the same with `0x5c`.",
                    "A PBKDF2 block starts from `HMAC(password, salt + i.to_bytes(4, 'big'))` and then feeds each U back in, XOR-ing every result into the accumulator. Note the loop runs `iterations - 1` more times.",
                    "Constant-time comparison never returns early: OR every `x ^ y` into one integer and test that integer once at the end.",
                ],
                "tests": [
                    {"name": "HMAC-SHA256 against RFC 4231", "code": r'''
_cases = [(bytes([0x0b]) * 20, b"Hi There",
           "b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7"),
          (b"Jefe", b"what do ya want for nothing?",
           "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843"),
          (b"", b"",
           "b613679a0814d9ec772f95d778c35fc5ff1697c493715653c6c712144292c5ad")]
for _key, _msg, _want in _cases:
    _got = hmac_sha256(_key, _msg)
    assert isinstance(_got, bytes) and len(_got) == 32, \
        f"hmac_sha256 should return 32 bytes, got {_got!r}"
    assert _got.hex() == _want, f"HMAC({_key!r}, {_msg!r}) gave {_got.hex()}, expected {_want}"
'''},
                    {"name": "Oversized keys are hashed first", "code": r'''
_got = hmac_sha256(bytes([0xaa]) * 131,
                   b"Test Using Larger Than Block-Size Key - Hash Key First").hex()
_want = "60e431591ee0b67f0d8a26aacbf5b77f8e0bc6213728c5140546040f0ee37f54"
assert _got == _want, f"a 131-byte key gave {_got}, expected {_want}"
assert hmac_sha256("Jefe", "what do ya want for nothing?") == \
       hmac_sha256(b"Jefe", b"what do ya want for nothing?"), \
    "str and bytes arguments should agree"
_short = hmac_sha256(b"k", b"m")
assert _short != hashlib.sha256(b"k" + b"m").digest(), \
    "HMAC is not sha256(key + message) — the pads are the point"
'''},
                    {"name": "PBKDF2-HMAC-SHA256 against the published vectors", "code": r'''
_cases = [(1, "120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b"),
          (2, "ae4d0c95af6b46d32d0adff928f06dd02a303f8ef3c251dfd6e2d85a95474c43"),
          (4096, "c5e478d59288c841aa530db6845c4c8d962893a001ce4e11a4963873aa98134a")]
for _iterations, _want in _cases:
    _got = pbkdf2(b"password", b"salt", _iterations, 32).hex()
    assert _got == _want, \
        f"pbkdf2('password', 'salt', {_iterations}, 32) gave {_got}, expected {_want}"
'''},
                    {"name": "Derived keys longer or shorter than one block", "code": r'''
_got = pbkdf2(b"password", b"salt", 100, 64).hex()
_want = ("07e6997180cf7f12904f04100d405d34888fdf62af6d506a0ecc23b196fe99d8"
         "675294ec5aa7944b6a86c51fd97051bbefad5239c8fe47db259c296e98569a86")
assert _got == _want, f"a 64-byte key gave {_got}, expected {_want}"
assert _got[:64] == pbkdf2(b"password", b"salt", 100, 32).hex(), \
    "the first block must not change when more blocks are asked for"
_got = pbkdf2(b"passwd", b"salt", 1, 20).hex()
assert _got == "55ac046e56e3089fec1691c22544b605f9418521", \
    f"a 20-byte key gave {_got}"
for _bad in (0, -1):
    try:
        pbkdf2(b"p", b"s", _bad, 32)
        assert False, f"iterations={_bad} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Constant-time comparison", "code": r'''
assert constant_time_equals(b"abcdef", b"abcdef") is True, "equal inputs compare equal"
assert constant_time_equals(b"abcdef", b"Abcdef") is False, "a difference at the front"
assert constant_time_equals(b"abcdef", b"abcdeF") is False, "a difference at the back"
assert constant_time_equals(b"abc", b"abcd") is False, "different lengths are not equal"
assert constant_time_equals("secret", "secret") is True, "str arguments are accepted"
assert constant_time_equals(b"", b"") is True, "two empty strings are equal"
'''},
                    {"name": "Password records are salted and verifiable", "code": r'''
_record = hash_password("hunter2", iterations=512)
_parts = _record.split("$")
assert len(_parts) == 4, f"a record has four $-separated fields, got {_record!r}"
assert _parts[0] == "pbkdf2_sha256", f"algorithm field was {_parts[0]!r}"
assert _parts[1] == "512", f"iteration field was {_parts[1]!r}"
assert len(bytes.fromhex(_parts[2])) == 16, "the salt should be 16 bytes"
assert len(bytes.fromhex(_parts[3])) == 32, "the derived key should be 32 bytes"
assert verify_password("hunter2", _record) is True, "the right password must verify"
assert verify_password("hunter3", _record) is False, "the wrong password must not"
_again = hash_password("hunter2", iterations=512)
assert _again != _record, "two records for the same password must differ — that is the salt"
assert verify_password("hunter2", _again) is True, "and both must still verify"
assert random_salt(16) != random_salt(16), "salts must not repeat"
assert len(random_salt(24)) == 24 and isinstance(random_salt(8), bytes), \
    "random_salt returns the requested number of bytes"
'''},
                    {"name": "Verification goes through the constant-time compare", "code": r'''
_record = hash_password("hunter2", iterations=256)
_calls = []
_real = constant_time_equals
def _spy(a, b):
    _calls.append((a, b))
    return _real(a, b)
constant_time_equals = _spy
try:
    assert verify_password("hunter2", _record) is True
    assert verify_password("nope", _record) is False
finally:
    constant_time_equals = _real
assert len(_calls) >= 2, "verify_password should compare through constant_time_equals"
for _broken in ["pbkdf2_sha256$100$aabb", "md5$100$aabb$ccdd", "nonsense"]:
    try:
        verify_password("x", _broken)
        assert False, f"the record {_broken!r} should raise ValueError"
    except ValueError:
        pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M3
        {
            "title": "Symmetric encryption and modes of operation",
            "summary": "A toy block cipher, and the difference between ECB and CTR made visible.",
            "concepts": [
                "A block cipher is a keyed permutation on fixed-size blocks — invertible by construction, not by luck",
                "A Feistel network makes any round function invertible, which is why the round function need not be",
                "A mode of operation is what turns a block permutation into a cipher for messages of any length",
                "ECB encrypts each block independently, so equal plaintext blocks give equal ciphertext blocks",
                "CTR encrypts a counter and XORs the result, turning a block cipher into a stream cipher with no padding",
                "PKCS#7 padding is unambiguous because a full block of padding is added when the input already fits",
                "A CTR nonce must never repeat under one key: two messages with the same keystream XOR to each other",
            ],
            "lab": {
                "title": "ECB versus CTR, and the pattern that leaks",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
`round_function` and `xor_bytes` are given, so everyone's cipher agrees. The
block size is 8 bytes and there are 4 Feistel rounds.

**`block_encrypt(block, key)`** — split the 8-byte block into `L` and `R` of
4 bytes each and run

```text
for r in 0, 1, 2, 3:
    L, R = R, xor_bytes(L, round_function(key, r, R))
return L + R
```

**`block_decrypt(block, key)`** — the same rounds backwards:

```text
for r in 3, 2, 1, 0:
    L, R = xor_bytes(R, round_function(key, r, L)), L
```

A block that is not exactly 8 bytes raises `ValueError`.

**`pad(data)` / `unpad(data)`** — PKCS#7 to the block size. Data that already
fits gains a whole extra block, so unpadding is never ambiguous. `unpad`
raises `ValueError` on an empty input, a length that is not a multiple of 8,
or padding bytes that do not agree.

**`ecb_encrypt(data, key)` / `ecb_decrypt(data, key)`** — pad, then each block
on its own.

**`ctr_encrypt(data, key, nonce)`** — the keystream is
`block_encrypt(nonce + counter, key)` for counter 0, 1, 2, ... with a 4-byte
nonce and a 4-byte big-endian counter, XORed against the data and truncated to
its length. No padding, and encryption is its own inverse.

**`count_repeated_blocks(data)`** — how many 8-byte blocks are duplicates of an
earlier one: `len(blocks) - len(set(blocks))`.

The last two checks are the point of the lab: a plaintext of repeating blocks
comes out of ECB with those repeats intact, and out of CTR with none — and
reusing a CTR nonce hands the attacker the XOR of two plaintexts.
''',
                "files": [{"name": "main.py", "content": r'''
import hashlib
import random

BLOCK_SIZE = 8
ROUNDS = 4
HALF = BLOCK_SIZE // 2


def xor_bytes(a, b):
    """Byte-wise XOR, truncated to the shorter argument."""
    return bytes(x ^ y for x, y in zip(a, b))


def round_function(key, index, half):
    """The Feistel round function: 4 bytes out, and deliberately not invertible."""
    return hashlib.sha256(key + bytes([index]) + half).digest()[:HALF]


# ------------------------------------------------------------- your code
def block_encrypt(block, key):
    """One 8-byte block through ROUNDS Feistel rounds."""
    # your code here


def block_decrypt(block, key):
    """The exact inverse of block_encrypt."""
    # your code here


def pad(data):
    """PKCS#7 padding up to a whole number of blocks."""
    # your code here


def unpad(data):
    """Remove PKCS#7 padding. ValueError when it does not agree."""
    # your code here


def ecb_encrypt(data, key):
    """Pad, then encrypt every block independently."""
    # your code here


def ecb_decrypt(data, key):
    """Decrypt every block, then remove the padding."""
    # your code here


def keystream(key, nonce, length):
    """length bytes of block_encrypt(nonce + counter) output."""
    # your code here


def ctr_encrypt(data, key, nonce):
    """XOR the data with the keystream. Its own inverse. 4-byte nonce."""
    # your code here


def count_repeated_blocks(data):
    """How many 8-byte blocks repeat an earlier block."""
    # your code here


message = b"YELLOW SUBMARINE" * 4
key = b"a toy key"
print("ecb repeats:", count_repeated_blocks(ecb_encrypt(message, key)))
print("ctr repeats:", count_repeated_blocks(ctr_encrypt(message, key, b"once")))
print("ctr is its own inverse:",
      ctr_encrypt(ctr_encrypt(message, key, b"once"), key, b"once") == message)
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import hashlib
import random

BLOCK_SIZE = 8
ROUNDS = 4
HALF = BLOCK_SIZE // 2


def xor_bytes(a, b):
    """Byte-wise XOR, truncated to the shorter argument."""
    return bytes(x ^ y for x, y in zip(a, b))


def round_function(key, index, half):
    """The Feistel round function: 4 bytes out, and deliberately not invertible."""
    return hashlib.sha256(key + bytes([index]) + half).digest()[:HALF]


# ------------------------------------------------------------- your code
def block_encrypt(block, key):
    """One 8-byte block through ROUNDS Feistel rounds."""
    if len(block) != BLOCK_SIZE:
        raise ValueError(f"a block is {BLOCK_SIZE} bytes, got {len(block)}")
    left, right = block[:HALF], block[HALF:]
    for index in range(ROUNDS):
        left, right = right, xor_bytes(left, round_function(key, index, right))
    return left + right


def block_decrypt(block, key):
    """The exact inverse of block_encrypt."""
    if len(block) != BLOCK_SIZE:
        raise ValueError(f"a block is {BLOCK_SIZE} bytes, got {len(block)}")
    left, right = block[:HALF], block[HALF:]
    for index in reversed(range(ROUNDS)):
        left, right = xor_bytes(right, round_function(key, index, left)), left
    return left + right


def pad(data):
    """PKCS#7 padding up to a whole number of blocks."""
    missing = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + bytes([missing]) * missing


def unpad(data):
    """Remove PKCS#7 padding. ValueError when it does not agree."""
    if not data or len(data) % BLOCK_SIZE:
        raise ValueError("padded data is a non-empty multiple of the block size")
    count = data[-1]
    if count < 1 or count > BLOCK_SIZE or data[-count:] != bytes([count]) * count:
        raise ValueError("bad padding")
    return data[:-count]


def ecb_encrypt(data, key):
    """Pad, then encrypt every block independently."""
    padded = pad(data)
    return b"".join(block_encrypt(padded[i:i + BLOCK_SIZE], key)
                    for i in range(0, len(padded), BLOCK_SIZE))


def ecb_decrypt(data, key):
    """Decrypt every block, then remove the padding."""
    if not data or len(data) % BLOCK_SIZE:
        raise ValueError("ciphertext is a non-empty multiple of the block size")
    plain = b"".join(block_decrypt(data[i:i + BLOCK_SIZE], key)
                     for i in range(0, len(data), BLOCK_SIZE))
    return unpad(plain)


def keystream(key, nonce, length):
    """length bytes of block_encrypt(nonce + counter) output."""
    out = b""
    counter = 0
    while len(out) < length:
        out += block_encrypt(nonce + counter.to_bytes(HALF, "big"), key)
        counter += 1
    return out[:length]


def ctr_encrypt(data, key, nonce):
    """XOR the data with the keystream. Its own inverse. 4-byte nonce."""
    if len(nonce) != HALF:
        raise ValueError(f"the nonce is {HALF} bytes, got {len(nonce)}")
    return xor_bytes(data, keystream(key, nonce, len(data)))


def count_repeated_blocks(data):
    """How many 8-byte blocks repeat an earlier block."""
    blocks = [data[i:i + BLOCK_SIZE] for i in range(0, len(data), BLOCK_SIZE)]
    return len(blocks) - len(set(blocks))


message = b"YELLOW SUBMARINE" * 4
key = b"a toy key"
print("ecb repeats:", count_repeated_blocks(ecb_encrypt(message, key)))
print("ctr repeats:", count_repeated_blocks(ctr_encrypt(message, key, b"once")))
print("ctr is its own inverse:",
      ctr_encrypt(ctr_encrypt(message, key, b"once"), key, b"once") == message)
'''}],
                "hints": [
                    "The Feistel swap is a single tuple assignment: `left, right = right, xor_bytes(left, round_function(key, index, right))`. Decryption is the same line read backwards, over `reversed(range(ROUNDS))`.",
                    "PKCS#7: `missing = BLOCK_SIZE - (len(data) % BLOCK_SIZE)` is never 0, which is exactly why a whole padding block appears when the data already fits.",
                    "Build the CTR keystream one block at a time with `nonce + counter.to_bytes(4, 'big')`, then truncate to the message length — that is why CTR needs no padding.",
                    "`count_repeated_blocks` is `len(blocks) - len(set(blocks))`. Run it on the ECB and CTR ciphertexts of the same repetitive message and the whole lesson is in the two numbers.",
                ],
                "tests": [
                    {"name": "The block cipher is a permutation", "code": r'''
_got = block_encrypt(b"12345678", b"key").hex()
assert _got == "059a47aecb0c7274", f"block_encrypt(b'12345678', b'key') gave {_got}"
assert block_decrypt(bytes.fromhex("059a47aecb0c7274"), b"key") == b"12345678", \
    "decryption must undo it exactly"
_rng = random.Random(7)
for _ in range(200):
    _block = bytes(_rng.randrange(256) for _ in range(8))
    _key = bytes(_rng.randrange(256) for _ in range(5))
    assert block_decrypt(block_encrypt(_block, _key), _key) == _block, \
        f"round trip failed for block {_block.hex()}"
for _bad in [b"", b"1234567", b"123456789"]:
    try:
        block_encrypt(_bad, b"key")
        assert False, f"a block of {len(_bad)} bytes should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "The key matters and one bit spreads", "code": r'''
assert block_encrypt(b"12345678", b"key") != block_encrypt(b"12345678", b"ke2"), \
    "a different key must give a different block"
assert block_encrypt(b"12345678", b"key") == block_encrypt(b"12345678", b"key"), \
    "the cipher is deterministic"
def _bit_difference(a, b):
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))
_rng = random.Random(7)
_worst = 64
for _ in range(100):
    _block = bytes(_rng.randrange(256) for _ in range(8))
    _index, _mask = _rng.randrange(8), 1 << _rng.randrange(8)
    _flipped = bytes(c ^ _mask if i == _index else c for i, c in enumerate(_block))
    _worst = min(_worst, _bit_difference(block_encrypt(_block, b"key"),
                                         block_encrypt(_flipped, b"key")))
assert _worst >= 12, \
    f"flipping one plaintext bit changed only {_worst} of 64 ciphertext bits"
'''},
                    {"name": "PKCS#7 padding is unambiguous", "code": r'''
assert pad(b"1234567") == b"1234567\x01", f"got {pad(b'1234567')!r}"
assert pad(b"12345678") == b"12345678" + bytes([8]) * 8, \
    "data that already fits gains a whole block of padding"
assert pad(b"") == bytes([8]) * 8, "empty data pads to one full block"
for _data in [b"", b"a", b"12345678", b"123456789", bytes(range(20))]:
    assert unpad(pad(_data)) == _data, f"pad/unpad round trip failed for {_data!r}"
    assert len(pad(_data)) % 8 == 0, "padded data is a whole number of blocks"
for _bad in [b"", b"1234567", b"12345678", b"1234567\x09", b"123456\x02\x03"]:
    try:
        unpad(_bad)
        assert False, f"unpad({_bad!r}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "ECB round-trips and leaks the pattern", "code": r'''
_key = b"a toy key"
for _data in [b"", b"short", b"YELLOW SUBMARINE", bytes(range(40))]:
    assert ecb_decrypt(ecb_encrypt(_data, _key), _key) == _data, \
        f"ECB round trip failed for {_data!r}"
_message = b"CATSCATS" * 8
_ecb = ecb_encrypt(_message, _key)
assert count_repeated_blocks(_message) == 7, "the plaintext itself has 7 repeated blocks"
assert count_repeated_blocks(_ecb) == 7, \
    f"ECB should preserve all 7 repeats, found {count_repeated_blocks(_ecb)}"
assert len(_ecb) == len(_message) + 8, "ECB output is padded to the next whole block"
'''},
                    {"name": "CTR hides the pattern and needs no padding", "code": r'''
_key = b"a toy key"
_message = b"CATSCATS" * 8
_ctr = ctr_encrypt(_message, _key, b"once")
assert count_repeated_blocks(_ctr) == 0, \
    f"CTR should leave no repeated blocks, found {count_repeated_blocks(_ctr)}"
assert len(_ctr) == len(_message), "CTR output is exactly as long as the plaintext"
assert ctr_encrypt(_ctr, _key, b"once") == _message, "CTR is its own inverse"
for _data in [b"", b"a", b"seventeen bytes.."]:
    assert ctr_encrypt(ctr_encrypt(_data, _key, b"n0nc"), _key, b"n0nc") == _data, \
        f"CTR round trip failed for {_data!r}"
    assert len(ctr_encrypt(_data, _key, b"n0nc")) == len(_data), "no padding in CTR"
assert ctr_encrypt(_message, _key, b"once") != ctr_encrypt(_message, _key, b"twic"), \
    "a different nonce must give a different ciphertext"
try:
    ctr_encrypt(b"data", _key, b"toolong")
    assert False, "a nonce that is not 4 bytes should raise ValueError"
except ValueError:
    pass
'''},
                    {"name": "A reused nonce hands over the plaintexts", "code": r'''
_key = b"a toy key"
_m1 = b"attack at dawn!!"
_m2 = b"retreat at dusk!"
_c1 = ctr_encrypt(_m1, _key, b"same")
_c2 = ctr_encrypt(_m2, _key, b"same")
assert xor_bytes(_c1, _c2) == xor_bytes(_m1, _m2), \
    "two messages under one nonce XOR to the XOR of the plaintexts"
_recovered = xor_bytes(xor_bytes(_c1, _c2), _m1)
assert _recovered == _m2, \
    f"knowing one plaintext reveals the other: got {_recovered!r}, expected {_m2!r}"
'''},
                    {"name": "Damaged ciphertext is refused, not guessed", "code": r'''
_key = b"a toy key"
_ecb = ecb_encrypt(b"a secret message", _key)
for _bad in [_ecb[:-1], _ecb[:-8], b""]:
    try:
        ecb_decrypt(_bad, _key)
        assert False, f"ECB decryption of {len(_bad)} bytes should raise ValueError"
    except ValueError:
        pass
try:
    _recovered = ecb_decrypt(_ecb, b"the wrong key")
    assert _recovered != b"a secret message", \
        "the wrong key must not recover the plaintext"
except ValueError:
    pass
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M4
        {
            "title": "Public key cryptography: RSA end to end",
            "summary": "Primality testing, key generation, encryption and signatures with nothing but integers.",
            "concepts": [
                "Trapdoor one-way functions: modular exponentiation is easy, and inverting it needs the factorisation",
                "Fermat's little theorem gives a fast compositeness test, and Carmichael numbers show why it is not enough",
                "Miller-Rabin refines it with the square-root structure of 1, and errs one-sidedly at rate 4^-k",
                "Key generation is a search: sample odd candidates, sieve by small primes, then test",
                "The extended Euclidean algorithm produces the private exponent as the inverse of e modulo lambda(n)",
                "Signing is decryption applied to a hash: it is the hash, not the message, that is exponentiated",
                "Textbook RSA is deterministic and therefore not semantically secure — padding is not optional in practice",
            ],
            "lab": {
                "title": "RSA with Miller-Rabin, encryption and signatures",
                "runtime": "python",
                "minutes": 70,
                "brief": r'''
No library does the mathematics for you here. `SMALL_PRIMES` is given for the
sieve; everything else is yours.

**`is_probable_prime(n, rounds=16, rng=None)`** — Miller-Rabin. Reject `n < 2`,
handle the small primes by trial division, write `n - 1 = d * 2^r` with `d`
odd, and for each of `rounds` random bases `a` in `[2, n-2]`:

```text
x = a^d mod n
if x == 1 or x == n-1: this base says nothing, try the next
repeat r-1 times: x = x^2 mod n; if x == n-1 this base says nothing
otherwise n is composite
```

Carmichael numbers such as 561, 1105, 1729 and 6601 pass the naive Fermat test
and must not pass this one.

**`generate_prime(bits, rng)`** — sample odd candidates with the top bit set,
so the result is exactly `bits` bits, until one is probably prime.

**`egcd(a, b)`** and **`modinv(a, m)`** — the extended Euclidean algorithm, and
`ValueError` when the inverse does not exist.

**`generate_keypair(bits, rng, e=65537)`** — two distinct primes of `bits // 2`
bits, `n = p * q`, `lambda = lcm(p-1, q-1)`, `d = modinv(e, lambda)`. Retry when
`gcd(e, lambda) != 1`. Returns `((n, e), (n, d))`.

**`encrypt(m, public)` / `decrypt(c, private)`** — `pow` with the exponent.
A message outside `0 <= m < n` raises `ValueError`.

**`message_hash(message, n)`** — `int` of the SHA-256 digest, reduced mod `n`.

**`sign(message, private)` / `verify(message, signature, public)`** — sign the
hash, and verify by exponentiating the signature back and comparing.

256-bit keys are used so the checks run instantly. They are far too small to
protect anything; the algorithm is identical at 3072 bits, only slower.
''',
                "files": [{"name": "main.py", "content": r'''
import hashlib
import math
import random

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
PUBLIC_EXPONENT = 65537


def is_probable_prime(n, rounds=16, rng=None):
    """Miller-Rabin. False means composite; True means probably prime."""
    # your code here


def generate_prime(bits, rng):
    """A probable prime of exactly `bits` bits."""
    # your code here


def egcd(a, b):
    """(g, x, y) with a*x + b*y == g == gcd(a, b)."""
    # your code here


def modinv(a, m):
    """The inverse of a modulo m, or ValueError when there is none."""
    # your code here


def generate_keypair(bits, rng, e=PUBLIC_EXPONENT):
    """((n, e), (n, d)) for a modulus of about `bits` bits."""
    # your code here


def encrypt(m, public):
    """m^e mod n. ValueError when m is outside 0 <= m < n."""
    # your code here


def decrypt(c, private):
    """c^d mod n."""
    # your code here


def message_hash(message, n):
    """SHA-256 of the message as an integer, reduced modulo n."""
    # your code here


def sign(message, private):
    """Exponentiate the hash of the message with the private exponent."""
    # your code here


def verify(message, signature, public):
    """True when the signature exponentiates back to the message hash."""
    # your code here


rng = random.Random(7)
public, private = generate_keypair(256, rng)
print("modulus bits:", public[0].bit_length())
secret = encrypt(42, public)
print("42 encrypts to", secret)
print("and back to", decrypt(secret, private))
signature = sign(b"transfer 100 to bob", private)
print("signature verifies:", verify(b"transfer 100 to bob", signature, public))
print("tampered verifies:", verify(b"transfer 900 to bob", signature, public))
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import hashlib
import math
import random

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
                53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
PUBLIC_EXPONENT = 65537


def is_probable_prime(n, rounds=16, rng=None):
    """Miller-Rabin. False means composite; True means probably prime."""
    if n < 2:
        return False
    for small in SMALL_PRIMES:
        if n % small == 0:
            return n == small
    rng = random.Random(7) if rng is None else rng
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits, rng):
    """A probable prime of exactly `bits` bits."""
    if bits < 8:
        raise ValueError("use at least 8 bits")
    while True:
        candidate = rng.getrandbits(bits) | (1 << (bits - 1)) | 1
        if is_probable_prime(candidate, 16, rng):
            return candidate


def egcd(a, b):
    """(g, x, y) with a*x + b*y == g == gcd(a, b)."""
    if b == 0:
        return (a, 1, 0)
    g, x, y = egcd(b, a % b)
    return (g, y, x - (a // b) * y)


def modinv(a, m):
    """The inverse of a modulo m, or ValueError when there is none."""
    g, x, _y = egcd(a % m, m)
    if g != 1:
        raise ValueError(f"{a} has no inverse modulo {m}")
    return x % m


def generate_keypair(bits, rng, e=PUBLIC_EXPONENT):
    """((n, e), (n, d)) for a modulus of about `bits` bits."""
    while True:
        p = generate_prime(bits // 2, rng)
        q = generate_prime(bits // 2, rng)
        if p == q:
            continue
        lam = (p - 1) * (q - 1) // math.gcd(p - 1, q - 1)
        if math.gcd(e, lam) != 1:
            continue
        return (p * q, e), (p * q, modinv(e, lam))


def encrypt(m, public):
    """m^e mod n. ValueError when m is outside 0 <= m < n."""
    n, e = public
    if not 0 <= m < n:
        raise ValueError("the message must satisfy 0 <= m < n")
    return pow(m, e, n)


def decrypt(c, private):
    """c^d mod n."""
    n, d = private
    if not 0 <= c < n:
        raise ValueError("the ciphertext must satisfy 0 <= c < n")
    return pow(c, d, n)


def message_hash(message, n):
    """SHA-256 of the message as an integer, reduced modulo n."""
    if isinstance(message, str):
        message = message.encode("utf-8")
    return int.from_bytes(hashlib.sha256(message).digest(), "big") % n


def sign(message, private):
    """Exponentiate the hash of the message with the private exponent."""
    n, d = private
    return pow(message_hash(message, n), d, n)


def verify(message, signature, public):
    """True when the signature exponentiates back to the message hash."""
    n, e = public
    if not 0 <= signature < n:
        return False
    return pow(signature, e, n) == message_hash(message, n)


rng = random.Random(7)
public, private = generate_keypair(256, rng)
print("modulus bits:", public[0].bit_length())
secret = encrypt(42, public)
print("42 encrypts to", secret)
print("and back to", decrypt(secret, private))
signature = sign(b"transfer 100 to bob", private)
print("signature verifies:", verify(b"transfer 100 to bob", signature, public))
print("tampered verifies:", verify(b"transfer 900 to bob", signature, public))
'''}],
                "hints": [
                    "Trial-divide by `SMALL_PRIMES` first and return `n == small` on a hit — that handles 2, 3, 5 and friends without ever entering the witness loop.",
                    "The inner Miller-Rabin loop wants a `for ... else`: reaching the `else` means no square ever hit `n - 1`, which is a proof of compositeness.",
                    "`candidate = rng.getrandbits(bits) | (1 << (bits - 1)) | 1` forces the top bit (so the length is exact) and the bottom bit (so it is odd).",
                    "Signing exponentiates `message_hash(message, n)`, never the message. Verification recomputes that hash and compares it with `pow(signature, e, n)`.",
                ],
                "tests": [
                    {"name": "Miller-Rabin agrees with the truth on small numbers", "code": r'''
for _p in [2, 3, 5, 7, 13, 97, 101, 7919, 104729, 1000003]:
    assert is_probable_prime(_p) is True, f"{_p} is prime but was rejected"
for _c in [-7, 0, 1, 4, 9, 15, 21, 91, 7917, 1000001]:
    assert is_probable_prime(_c) is False, f"{_c} is composite but was accepted"
for _carmichael in [561, 1105, 1729, 2465, 2821, 6601, 8911]:
    assert is_probable_prime(_carmichael) is False, \
        f"{_carmichael} is a Carmichael number — Fermat is fooled, Miller-Rabin is not"
_count = sum(1 for _n in range(2, 200) if is_probable_prime(_n))
assert _count == 46, f"there are 46 primes below 200, the test found {_count}"
'''},
                    {"name": "Prime generation gives the size it promises", "code": r'''
_rng = random.Random(7)
for _bits in (16, 32, 64, 128):
    _p = generate_prime(_bits, _rng)
    assert _p.bit_length() == _bits, \
        f"generate_prime({_bits}) returned a {_p.bit_length()}-bit number"
    assert _p % 2 == 1, f"{_p} is even"
    assert is_probable_prime(_p, 32), f"{_p} is not prime"
assert generate_prime(64, random.Random(11)) == generate_prime(64, random.Random(11)), \
    "the same seed must give the same prime"
assert generate_prime(64, random.Random(11)) != generate_prime(64, random.Random(12)), \
    "different seeds should not collide"
'''},
                    {"name": "Extended Euclid and modular inverses", "code": r'''
for _a, _b in [(240, 46), (65537, 3120), (17, 3120), (7, 1)]:
    _g, _x, _y = egcd(_a, _b)
    assert _g == math.gcd(_a, _b), f"egcd({_a}, {_b}) reported gcd {_g}"
    assert _a * _x + _b * _y == _g, f"egcd({_a}, {_b}) gave x={_x}, y={_y} which do not fit"
assert modinv(3, 11) == 4, f"modinv(3, 11) gave {modinv(3, 11)}, expected 4"
assert modinv(65537, 3120) * 65537 % 3120 == 1, "the inverse must multiply back to 1"
for _a, _m in [(4, 8), (6, 9), (0, 5)]:
    try:
        modinv(_a, _m)
        assert False, f"modinv({_a}, {_m}) should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Keys are well formed and the round trip works", "code": r'''
_rng = random.Random(7)
_public, _private = generate_keypair(256, _rng)
_n, _e = _public
assert _private[0] == _n, "the modulus is shared by both halves of the key"
assert _e == 65537, f"the public exponent should be 65537, got {_e}"
assert _n.bit_length() in (255, 256), f"the modulus has {_n.bit_length()} bits"
assert _n % 2 == 1 and not is_probable_prime(_n, 8), "a modulus is an odd composite"
for _m in [0, 1, 2, 42, 123456789, _n - 1]:
    _c = encrypt(_m, _public)
    assert decrypt(_c, _private) == _m, f"the round trip failed for m={_m}"
assert encrypt(42, _public) != 42, "textbook RSA still moves the message"
'''},
                    {"name": "Messages outside the modulus are refused", "code": r'''
_rng = random.Random(3)
_public, _private = generate_keypair(256, _rng)
_n = _public[0]
for _bad in [-1, _n, _n + 1, _n * 2]:
    try:
        encrypt(_bad, _public)
        assert False, f"encrypting {_bad} with a modulus of {_n} should raise ValueError"
    except ValueError:
        pass
'''},
                    {"name": "Signatures bind a message to a key", "code": r'''
_public, _private = generate_keypair(256, random.Random(5))
_other_public, _other_private = generate_keypair(256, random.Random(6))
_message = b"transfer 100 to bob"
_signature = sign(_message, _private)
assert verify(_message, _signature, _public) is True, "a genuine signature must verify"
assert verify(b"transfer 900 to bob", _signature, _public) is False, \
    "a changed message must not verify"
assert verify(_message, (_signature + 1) % _public[0], _public) is False, \
    "a changed signature must not verify"
assert verify(_message, _signature, _other_public) is False, \
    "another key must not verify this signature"
assert sign(_message, _private) == _signature, "signing is deterministic here"
assert sign("transfer 100 to bob", _private) == _signature, \
    "a str message hashes the same as its UTF-8 bytes"
'''},
                    {"name": "Key generation is reproducible from its seed", "code": r'''
_a = generate_keypair(256, random.Random(99))
_b = generate_keypair(256, random.Random(99))
assert _a == _b, "the same seed must produce the same keypair"
_c = generate_keypair(256, random.Random(100))
assert _c[0][0] != _a[0][0], "a different seed should give a different modulus"
_n, _d = _a[1]
assert 1 < _d < _n, f"the private exponent {_d} is out of range"
'''},
                ],
            },
        },
        # ------------------------------------------------------------ M5
        {
            "title": "Key agreement and the machine in the middle",
            "summary": "Diffie-Hellman over a safe prime, and the attack that authentication exists to stop.",
            "concepts": [
                "Diffie-Hellman: two exponentiations each, and a shared value neither party transmitted",
                "Security rests on the computational Diffie-Hellman assumption, not on secrecy of p or g",
                "A safe prime p = 2q + 1 leaves only the subgroups of order 1, 2, q and 2q, so validation is cheap",
                "Rejecting the peer values 0, 1 and p-1 kills small-subgroup confinement of the shared secret",
                "A shared group element is not a key: it must be run through a KDF before anything uses it",
                "Unauthenticated key agreement authenticates nobody — the middle can answer both sides at once",
                "Comparing key fingerprints out of band is the cheapest detection; signed exchanges are the real fix",
            ],
            "lab": {
                "title": "Diffie-Hellman, and Mallory in the middle",
                "runtime": "python",
                "minutes": 60,
                "brief": r'''
`P` is a 512-bit safe prime and `G` is 2; both are given, along with a
`is_probable_prime` you can use on the parameters. 512 bits is far too small to
protect real traffic and is chosen so the checks run instantly.

**`make_private(rng)`** — a private exponent drawn from `[2, P-2]`.

**`public_key(private)`** — `G^private mod P`.

**`validate_public(value)`** — raise `ValueError` unless `1 < value < P - 1`.
Those excluded values are exactly the ones that force the shared secret into a
subgroup of size one or two.

**`shared_secret(their_public, my_private)`** — validate, then
`their_public^my_private mod P`.

**`derive_key(secret)`** — SHA-256 of the secret as 64 big-endian bytes. The
group element itself is never used as a key.

**`fingerprint(key)`** — the first 8 hex characters of SHA-256 of the key, the
sort of thing two people read to each other over the telephone.

**`encrypt_message(key, message, nonce)` / `decrypt_message(key, blob, nonce)`**
— XOR against a keystream of `sha256(key + nonce + counter)` blocks with a
4-byte big-endian counter. `encrypt_message` takes a `str` and returns `bytes`;
`decrypt_message` does the reverse.

**`mitm_session(alice_private, bob_private, mallory_private, message)`** — run
the attack. Mallory answers Alice with her own public value and answers Bob with
it too, so Alice and Bob each share a key with Mallory and none with each other.
Return a dict with the keys

```text
alice_key  bob_key  mallory_alice_key  mallory_bob_key  seen  delivered
```

where `seen` is the plaintext Mallory read and `delivered` is what Bob finally
decrypted. A successful attack is one where `delivered == message` and Bob
never notices.
''',
                "files": [{"name": "main.py", "content": r'''
import hashlib
import random

# A 512-bit safe prime: P = 2q + 1 with q prime. Far too small for real use.
P = int("102061240770763168165730749985530608866235195527521819904558904251312486164011"
        "31463145168740366371535658173164110446769725746180938943583391084300892657547")
G = 2

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


def is_probable_prime(n, rounds=16, rng=None):
    """Given: Miller-Rabin, so you can check the parameters yourself."""
    if n < 2:
        return False
    for small in SMALL_PRIMES:
        if n % small == 0:
            return n == small
    rng = random.Random(7) if rng is None else rng
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def xor_bytes(a, b):
    """Byte-wise XOR, truncated to the shorter argument."""
    return bytes(x ^ y for x, y in zip(a, b))


# ------------------------------------------------------------- your code
def make_private(rng):
    """A private exponent in [2, P-2]."""
    # your code here


def public_key(private):
    """G raised to the private exponent, modulo P."""
    # your code here


def validate_public(value):
    """Raise ValueError for a peer value that is not in 1 < value < P-1."""
    # your code here


def shared_secret(their_public, my_private):
    """Validate the peer value, then raise it to our private exponent."""
    # your code here


def derive_key(secret):
    """32 bytes derived from the shared group element."""
    # your code here


def fingerprint(key):
    """Eight hex characters two humans can compare out of band."""
    # your code here


def keystream(key, nonce, length):
    """length bytes of sha256(key + nonce + counter) output."""
    # your code here


def encrypt_message(key, message, nonce):
    """str -> bytes, XORed against the keystream."""
    # your code here


def decrypt_message(key, blob, nonce):
    """bytes -> str, the inverse of encrypt_message."""
    # your code here


def mitm_session(alice_private, bob_private, mallory_private, message,
                 nonce=b"sess"):
    """Run the attack and report both sides' keys, what Mallory read and what Bob got."""
    # your code here


rng = random.Random(7)
alice, bob, mallory = make_private(rng), make_private(rng), make_private(rng)
honest = derive_key(shared_secret(public_key(bob), alice))
print("honest fingerprint:", fingerprint(honest))
result = mitm_session(alice, bob, mallory, "meet me at nine")
print("alice sees:", fingerprint(result["alice_key"]))
print("bob sees:  ", fingerprint(result["bob_key"]))
print("mallory read:", result["seen"])
'''}],
                "main": "main.py",
                "solution": [{"name": "main.py", "content": r'''
import hashlib
import random

# A 512-bit safe prime: P = 2q + 1 with q prime. Far too small for real use.
P = int("102061240770763168165730749985530608866235195527521819904558904251312486164011"
        "31463145168740366371535658173164110446769725746180938943583391084300892657547")
G = 2

SMALL_PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]


def is_probable_prime(n, rounds=16, rng=None):
    """Given: Miller-Rabin, so you can check the parameters yourself."""
    if n < 2:
        return False
    for small in SMALL_PRIMES:
        if n % small == 0:
            return n == small
    rng = random.Random(7) if rng is None else rng
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = rng.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def xor_bytes(a, b):
    """Byte-wise XOR, truncated to the shorter argument."""
    return bytes(x ^ y for x, y in zip(a, b))


# ------------------------------------------------------------- your code
def make_private(rng):
    """A private exponent in [2, P-2]."""
    return rng.randrange(2, P - 1)


def public_key(private):
    """G raised to the private exponent, modulo P."""
    return pow(G, private, P)


def validate_public(value):
    """Raise ValueError for a peer value that is not in 1 < value < P-1."""
    if not isinstance(value, int) or not 1 < value < P - 1:
        raise ValueError("the peer value is degenerate and must be rejected")
    return value


def shared_secret(their_public, my_private):
    """Validate the peer value, then raise it to our private exponent."""
    validate_public(their_public)
    return pow(their_public, my_private, P)


def derive_key(secret):
    """32 bytes derived from the shared group element."""
    return hashlib.sha256(secret.to_bytes(64, "big")).digest()


def fingerprint(key):
    """Eight hex characters two humans can compare out of band."""
    return hashlib.sha256(key).hexdigest()[:8]


def keystream(key, nonce, length):
    """length bytes of sha256(key + nonce + counter) output."""
    out = b""
    counter = 0
    while len(out) < length:
        out += hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest()
        counter += 1
    return out[:length]


def encrypt_message(key, message, nonce):
    """str -> bytes, XORed against the keystream."""
    raw = message.encode("utf-8")
    return xor_bytes(raw, keystream(key, nonce, len(raw)))


def decrypt_message(key, blob, nonce):
    """bytes -> str, the inverse of encrypt_message."""
    return xor_bytes(blob, keystream(key, nonce, len(blob))).decode("utf-8")


def mitm_session(alice_private, bob_private, mallory_private, message,
                 nonce=b"sess"):
    """Run the attack and report both sides' keys, what Mallory read and what Bob got."""
    alice_public = public_key(alice_private)
    bob_public = public_key(bob_private)
    mallory_public = public_key(mallory_private)

    # Mallory intercepts both halves of the exchange and substitutes her own.
    alice_key = derive_key(shared_secret(mallory_public, alice_private))
    bob_key = derive_key(shared_secret(mallory_public, bob_private))
    mallory_alice_key = derive_key(shared_secret(alice_public, mallory_private))
    mallory_bob_key = derive_key(shared_secret(bob_public, mallory_private))

    on_the_wire = encrypt_message(alice_key, message, nonce)
    seen = decrypt_message(mallory_alice_key, on_the_wire, nonce)
    forwarded = encrypt_message(mallory_bob_key, seen, nonce)
    delivered = decrypt_message(bob_key, forwarded, nonce)

    return {"alice_key": alice_key, "bob_key": bob_key,
            "mallory_alice_key": mallory_alice_key,
            "mallory_bob_key": mallory_bob_key,
            "seen": seen, "delivered": delivered}


rng = random.Random(7)
alice, bob, mallory = make_private(rng), make_private(rng), make_private(rng)
honest = derive_key(shared_secret(public_key(bob), alice))
print("honest fingerprint:", fingerprint(honest))
result = mitm_session(alice, bob, mallory, "meet me at nine")
print("alice sees:", fingerprint(result["alice_key"]))
print("bob sees:  ", fingerprint(result["bob_key"]))
print("mallory read:", result["seen"])
'''}],
                "hints": [
                    "Every exponentiation here is one call to `pow(base, exponent, P)` — Python's three-argument `pow` is the whole of the arithmetic.",
                    "`derive_key` must hash a fixed-width encoding: `secret.to_bytes(64, 'big')` pads short secrets so two different secrets can never encode to the same bytes.",
                    "Write `mitm_session` from Mallory's point of view: she has one private exponent and computes two different shared secrets, one with each victim.",
                    "The attack succeeds when `alice_key == mallory_alice_key` and `bob_key == mallory_bob_key` while `alice_key != bob_key`. Compare the fingerprints and the whole story is visible in eight characters.",
                ],
                "tests": [
                    {"name": "The parameters really are what they claim", "code": r'''
assert P.bit_length() == 512, f"P has {P.bit_length()} bits, expected 512"
assert is_probable_prime(P, 20), "P must be prime"
assert is_probable_prime((P - 1) // 2, 20), "P must be a safe prime: (P-1)/2 is prime too"
assert G == 2, f"the generator should be 2, got {G}"
assert pow(G, P - 1, P) == 1, "Fermat: g^(p-1) = 1 mod p"
'''},
                    {"name": "Both sides compute the same secret", "code": r'''
_rng = random.Random(11)
_a, _b = make_private(_rng), make_private(_rng)
assert 2 <= _a <= P - 2 and 2 <= _b <= P - 2, "private exponents live in [2, P-2]"
_A, _B = public_key(_a), public_key(_b)
assert shared_secret(_B, _a) == shared_secret(_A, _b), \
    "Diffie-Hellman: (g^b)^a and (g^a)^b are the same element"
assert derive_key(shared_secret(_B, _a)) == derive_key(shared_secret(_A, _b)), \
    "and so are the keys derived from it"
_c = make_private(random.Random(12))
assert derive_key(shared_secret(public_key(_c), _a)) != derive_key(shared_secret(_B, _a)), \
    "a different peer must give a different key"
'''},
                    {"name": "Degenerate peer values are rejected", "code": r'''
for _bad in [0, 1, -1, P - 1, P, P + 1]:
    try:
        validate_public(_bad)
        assert False, f"validate_public({_bad}) should raise ValueError"
    except ValueError:
        pass
_rng = random.Random(13)
_a = make_private(_rng)
assert validate_public(public_key(_a)) == public_key(_a), "a real public value is accepted"
for _bad in [1, P - 1]:
    try:
        shared_secret(_bad, _a)
        assert False, f"shared_secret should refuse the peer value {_bad}"
    except ValueError:
        pass
'''},
                    {"name": "The group element is hashed into a key", "code": r'''
_rng = random.Random(17)
_a, _b = make_private(_rng), make_private(_rng)
_secret = shared_secret(public_key(_b), _a)
_key = derive_key(_secret)
assert isinstance(_key, bytes) and len(_key) == 32, \
    f"derive_key should give 32 bytes, got {_key!r}"
assert derive_key(_secret) == _key, "derivation is deterministic"
assert derive_key(_secret + 1) != _key, "a different secret gives a different key"
assert _key != _secret.to_bytes(64, "big")[:32], "the raw group element is not the key"
_print = fingerprint(_key)
assert len(_print) == 8 and all(c in "0123456789abcdef" for c in _print), \
    f"a fingerprint is 8 hex characters, got {_print!r}"
assert fingerprint(derive_key(_secret + 1)) != _print, "different keys, different fingerprints"
'''},
                    {"name": "Messages travel and come back", "code": r'''
_key = derive_key(shared_secret(public_key(make_private(random.Random(3))),
                                make_private(random.Random(4))))
for _message in ["meet me at nine", "", "unicode: æøå", "x" * 200]:
    _blob = encrypt_message(_key, _message, b"sess")
    assert isinstance(_blob, bytes), "encrypt_message returns bytes"
    assert len(_blob) == len(_message.encode("utf-8")), "a stream cipher preserves length"
    assert decrypt_message(_key, _blob, b"sess") == _message, \
        f"the round trip failed for {_message!r}"
_blob = encrypt_message(_key, "meet me at nine", b"sess")
assert _blob != b"meet me at nine", "the ciphertext is not the plaintext"
assert encrypt_message(_key, "meet me at nine", b"othr") != _blob, \
    "a different nonce gives a different ciphertext"
'''},
                    {"name": "Mallory owns the conversation", "code": r'''
_rng = random.Random(7)
_alice, _bob, _mallory = make_private(_rng), make_private(_rng), make_private(_rng)
_result = mitm_session(_alice, _bob, _mallory, "meet me at nine")
assert _result["alice_key"] == _result["mallory_alice_key"], \
    "Alice shares her key with Mallory, not with Bob"
assert _result["bob_key"] == _result["mallory_bob_key"], \
    "and so does Bob"
assert _result["alice_key"] != _result["bob_key"], \
    "the two victims must end up with different keys — that is the attack"
assert _result["seen"] == "meet me at nine", \
    f"Mallory should read the plaintext, she got {_result['seen']!r}"
assert _result["delivered"] == "meet me at nine", \
    f"Bob should receive the message unchanged, he got {_result['delivered']!r}"
'''},
                    {"name": "Comparing fingerprints is what would have caught it", "code": r'''
_rng = random.Random(21)
_alice, _bob, _mallory = make_private(_rng), make_private(_rng), make_private(_rng)
_honest = derive_key(shared_secret(public_key(_bob), _alice))
_honest_other = derive_key(shared_secret(public_key(_alice), _bob))
assert fingerprint(_honest) == fingerprint(_honest_other), \
    "an unattacked exchange gives both parties the same fingerprint"
_result = mitm_session(_alice, _bob, _mallory, "wire the money")
assert fingerprint(_result["alice_key"]) != fingerprint(_result["bob_key"]), \
    "under attack the fingerprints disagree, which is the only warning either party gets"
'''},
                ],
            },
        },
    ],
    # ---------------------------------------------------------------- capstone
    "capstone": {
        "title": "Capstone — a secure message vault",
        "runtime": "python",
        "minutes": 300,
        "brief": r'''
Everything in the course, assembled into one small system: a vault that stores
short secrets under a password, encrypted and authenticated, and that refuses
to hand anything back when a single byte has been changed.

`vault.py` holds the cryptography and is what the checks import. `main.py` is a
demonstration script and carries the written threat model.

## The record

`seal(password, message, iterations)` produces a dictionary, all binary fields
base64 text so the whole thing survives JSON:

```text
{"alg": "vault1", "iterations": 4096,
 "salt": "...", "nonce": "...", "ciphertext": "...", "tag": "..."}
```

Construction, in this order:

1. `salt` — 16 fresh random bytes; `nonce` — 8 fresh random bytes.
2. `derive_keys` — PBKDF2-HMAC-SHA256 over the password and salt produces 64
   bytes; the first 32 are the encryption key, the last 32 the MAC key. One
   password, two keys, never the same key for both jobs.
3. `ciphertext` — the UTF-8 message XORed with
   `sha256(enc_key + nonce + counter)` blocks.
4. `tag` — `HMAC(mac_key, "vault1" + salt + nonce + iterations + ciphertext)`.

**Encrypt then MAC**, and the tag covers the parameters as well as the
ciphertext, so an attacker cannot quietly lower the iteration count or swap a
salt.

`open_record(password, record)` re-derives the keys, recomputes the tag, and
compares it in constant time **before** decrypting anything. Any mismatch —
wrong password, edited ciphertext, edited salt, edited iteration count, unknown
algorithm — raises `IntegrityError` and nothing else.

## The vault

`Vault(iterations=DEFAULT_ITERATIONS)` with `add(name, password, message)`,
`get(name, password)`, `names()`, `remove(name)`, `save(path)` and the
classmethod `load(path)`. Each entry carries its own password, salt and nonce.
An unknown name raises `KeyError`; a missing file loads as an empty vault.

## The threat model

`main.py` defines `THREAT_MODEL`, a paragraph naming what this design defends
against and what it does not: offline guessing of a stolen file, tampering with
stored records, and the things it cannot help with — a keylogger, a weak
password, plaintext in memory while the vault is open, and the fact that 4096
PBKDF2 iterations is a teaching number rather than a 2020s one.
''',
        "deliverables": [
            "`vault.py` — HMAC-SHA256, PBKDF2, a keystream, constant-time comparison, `seal`, `open_record` and `Vault`, importable with no output",
            "Encrypt-then-MAC with two independent keys derived from one password",
            "A tag that covers the algorithm, salt, nonce and iteration count as well as the ciphertext",
            "JSON persistence whose file contains no plaintext and survives a round trip",
            "`main.py` — a demonstration run plus `THREAT_MODEL`, a written statement of what the design does and does not defend against",
        ],
        "constraints": [
            "Standard library only: `hashlib`, `secrets`, `base64` and `json`; no `hmac`, and no `hashlib.pbkdf2_hmac`",
            "A fresh salt and a fresh nonce for every sealed record — never a fixed value, never a reused one",
            "Verify the tag before decrypting, and compare tags in constant time",
            "A failure to authenticate raises `IntegrityError` and returns no plaintext, not even partially",
        ],
        "rubric": [
            {"criterion": "Cryptographic correctness", "weight": 40,
             "evidence": "HMAC and PBKDF2 match the published vectors, the round trip works, and separate keys are derived for encryption and authentication."},
            {"criterion": "Integrity under attack", "weight": 25,
             "evidence": "Every tampered field — ciphertext, tag, salt, nonce, iterations, algorithm — is rejected with IntegrityError before any decryption happens."},
            {"criterion": "Interface and persistence", "weight": 20,
             "evidence": "Vault behaves as specified, saves and loads through JSON, and leaks no plaintext into the file."},
            {"criterion": "Threat model", "weight": 15,
             "evidence": "THREAT_MODEL states the attacker assumed, what the design stops, and at least three things it explicitly does not."},
        ],
        "hints": [
            "Build upwards and test as you go: `hmac_sha256` against the RFC 4231 vector, then `pbkdf2` against the RFC 8018 vector, and only then `seal`. A bug in the bottom layer is invisible from the top.",
            "Derive 64 bytes in one PBKDF2 call and split them — `material[:32], material[32:]` — rather than calling PBKDF2 twice with different salts.",
            "`open_record` should compute the tag and return early on failure. Decrypting first and checking afterwards is the mistake this whole design exists to avoid.",
            "Keep `mac_input` a single function used by both `seal` and `open_record`; if the two ever disagree about what is covered, every record silently stops authenticating.",
        ],
        "files": [
            {"name": "vault.py", "content": r'''
import base64
import hashlib
import json
import secrets

ALGORITHM = "vault1"
SALT_SIZE = 16
NONCE_SIZE = 8
KEY_SIZE = 32
BLOCK_SIZE = 64
DEFAULT_ITERATIONS = 4096


class IntegrityError(Exception):
    """The record did not authenticate: wrong password, or someone edited it."""


# ------------------------------------------------------------------ given
def as_bytes(value):
    """UTF-8 encode a str, pass bytes through."""
    return value.encode("utf-8") if isinstance(value, str) else bytes(value)


def xor_bytes(a, b):
    """Byte-wise XOR, truncated to the shorter argument."""
    return bytes(x ^ y for x, y in zip(a, b))


def b64(raw):
    """Bytes -> base64 text."""
    return base64.b64encode(raw).decode("ascii")


def unb64(text):
    """Base64 text -> bytes."""
    return base64.b64decode(text.encode("ascii"))


# ------------------------------------------------------------- your code
def hmac_sha256(key, message):
    """RFC 2104 HMAC with SHA-256, block size 64. Returns 32 bytes."""
    # your code here


def pbkdf2(password, salt, iterations, dklen=32):
    """PBKDF2-HMAC-SHA256. ValueError when iterations < 1."""
    # your code here


def constant_time_equals(a, b):
    """Compare without revealing where the two differ."""
    # your code here


def derive_keys(password, salt, iterations):
    """(encryption key, MAC key), 32 bytes each, from one PBKDF2 call."""
    # your code here


def keystream(key, nonce, length):
    """length bytes of sha256(key + nonce + counter) output."""
    # your code here


def mac_input(salt, nonce, iterations, ciphertext):
    """Exactly the bytes the tag must cover."""
    # your code here


def seal(password, message, iterations=DEFAULT_ITERATIONS):
    """Encrypt then MAC. Returns a JSON-safe record dict."""
    # your code here


def open_record(password, record):
    """Verify the tag, then decrypt. IntegrityError on any mismatch."""
    # your code here


class Vault:
    def __init__(self, iterations=DEFAULT_ITERATIONS):
        self.iterations = iterations
        self.entries = {}

    def add(self, name, password, message):
        """Seal a message under its own password and store it by name."""
        # your code here

    def get(self, name, password):
        """The plaintext for name. KeyError if unknown, IntegrityError if wrong."""
        # your code here

    def names(self):
        """Every stored name, sorted."""
        # your code here

    def remove(self, name):
        """Forget one entry. KeyError when it is not there."""
        # your code here

    def save(self, path):
        """Write the vault to path as JSON."""
        # your code here

    @classmethod
    def load(cls, path, iterations=DEFAULT_ITERATIONS):
        """Read a vault back. A missing file gives an empty vault."""
        # your code here
'''},
            {"name": "main.py", "content": r'''
from vault import Vault, IntegrityError, DEFAULT_ITERATIONS

THREAT_MODEL = (
    "Write the threat model here: who the attacker is, what they can reach, "
    "what this design stops, and at least three things it does not."
)

vault = Vault(iterations=DEFAULT_ITERATIONS)
vault.add("bank", "hunter2", "sort code 60-16-13")
vault.add("diary", "another password", "today I wrote a compiler")

print("entries:", vault.names())
print("bank:", vault.get("bank", "hunter2"))
try:
    vault.get("bank", "wrong password")
    print("the wrong password opened the record, which is a bug")
except IntegrityError:
    print("wrong password rejected")
'''},
        ],
        "main": "main.py",
        "solution": [
            {"name": "vault.py", "content": r'''
import base64
import hashlib
import json
import secrets

ALGORITHM = "vault1"
SALT_SIZE = 16
NONCE_SIZE = 8
KEY_SIZE = 32
BLOCK_SIZE = 64
DEFAULT_ITERATIONS = 4096


class IntegrityError(Exception):
    """The record did not authenticate: wrong password, or someone edited it."""


# ------------------------------------------------------------------ given
def as_bytes(value):
    """UTF-8 encode a str, pass bytes through."""
    return value.encode("utf-8") if isinstance(value, str) else bytes(value)


def xor_bytes(a, b):
    """Byte-wise XOR, truncated to the shorter argument."""
    return bytes(x ^ y for x, y in zip(a, b))


def b64(raw):
    """Bytes -> base64 text."""
    return base64.b64encode(raw).decode("ascii")


def unb64(text):
    """Base64 text -> bytes."""
    return base64.b64decode(text.encode("ascii"))


# ------------------------------------------------------------- your code
def hmac_sha256(key, message):
    """RFC 2104 HMAC with SHA-256, block size 64. Returns 32 bytes."""
    key = as_bytes(key)
    message = as_bytes(message)
    if len(key) > BLOCK_SIZE:
        key = hashlib.sha256(key).digest()
    key = key + b"\x00" * (BLOCK_SIZE - len(key))
    inner = bytes(b ^ 0x36 for b in key)
    outer = bytes(b ^ 0x5C for b in key)
    return hashlib.sha256(outer + hashlib.sha256(inner + message).digest()).digest()


def pbkdf2(password, salt, iterations, dklen=32):
    """PBKDF2-HMAC-SHA256. ValueError when iterations < 1."""
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    password = as_bytes(password)
    salt = as_bytes(salt)
    out = b""
    block = 1
    while len(out) < dklen:
        current = hmac_sha256(password, salt + block.to_bytes(4, "big"))
        accumulator = current
        for _ in range(iterations - 1):
            current = hmac_sha256(password, current)
            accumulator = xor_bytes(accumulator, current)
        out += accumulator
        block += 1
    return out[:dklen]


def constant_time_equals(a, b):
    """Compare without revealing where the two differ."""
    a = as_bytes(a)
    b = as_bytes(b)
    if len(a) != len(b):
        return False
    difference = 0
    for x, y in zip(a, b):
        difference |= x ^ y
    return difference == 0


def derive_keys(password, salt, iterations):
    """(encryption key, MAC key), 32 bytes each, from one PBKDF2 call."""
    material = pbkdf2(password, salt, iterations, 2 * KEY_SIZE)
    return material[:KEY_SIZE], material[KEY_SIZE:]


def keystream(key, nonce, length):
    """length bytes of sha256(key + nonce + counter) output."""
    out = b""
    counter = 0
    while len(out) < length:
        out += hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest()
        counter += 1
    return out[:length]


def mac_input(salt, nonce, iterations, ciphertext):
    """Exactly the bytes the tag must cover."""
    return (ALGORITHM.encode("ascii") + salt + nonce
            + int(iterations).to_bytes(4, "big") + ciphertext)


def seal(password, message, iterations=DEFAULT_ITERATIONS):
    """Encrypt then MAC. Returns a JSON-safe record dict."""
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    salt = secrets.token_bytes(SALT_SIZE)
    nonce = secrets.token_bytes(NONCE_SIZE)
    enc_key, mac_key = derive_keys(password, salt, iterations)
    raw = as_bytes(message)
    ciphertext = xor_bytes(raw, keystream(enc_key, nonce, len(raw)))
    tag = hmac_sha256(mac_key, mac_input(salt, nonce, iterations, ciphertext))
    return {"alg": ALGORITHM, "iterations": iterations, "salt": b64(salt),
            "nonce": b64(nonce), "ciphertext": b64(ciphertext), "tag": b64(tag)}


def open_record(password, record):
    """Verify the tag, then decrypt. IntegrityError on any mismatch."""
    if record.get("alg") != ALGORITHM:
        raise IntegrityError(f"unknown algorithm {record.get('alg')!r}")
    try:
        salt = unb64(record["salt"])
        nonce = unb64(record["nonce"])
        ciphertext = unb64(record["ciphertext"])
        tag = unb64(record["tag"])
        iterations = int(record["iterations"])
    except (KeyError, ValueError, TypeError) as error:
        raise IntegrityError(f"malformed record: {error}")
    if iterations < 1:
        raise IntegrityError("iteration count is not usable")
    enc_key, mac_key = derive_keys(password, salt, iterations)
    expected = hmac_sha256(mac_key, mac_input(salt, nonce, iterations, ciphertext))
    if not constant_time_equals(expected, tag):
        raise IntegrityError("the record does not authenticate")
    return xor_bytes(ciphertext, keystream(enc_key, nonce, len(ciphertext))).decode("utf-8")


class Vault:
    """Named secrets, each sealed under its own password."""

    def __init__(self, iterations=DEFAULT_ITERATIONS):
        self.iterations = iterations
        self.entries = {}

    def add(self, name, password, message):
        """Seal a message under its own password and store it by name."""
        self.entries[name] = seal(password, message, self.iterations)

    def get(self, name, password):
        """The plaintext for name. KeyError if unknown, IntegrityError if wrong."""
        if name not in self.entries:
            raise KeyError(name)
        return open_record(password, self.entries[name])

    def names(self):
        """Every stored name, sorted."""
        return sorted(self.entries)

    def remove(self, name):
        """Forget one entry. KeyError when it is not there."""
        if name not in self.entries:
            raise KeyError(name)
        del self.entries[name]

    def save(self, path):
        """Write the vault to path as JSON."""
        with open(path, "w", encoding="utf-8") as handle:
            json.dump({"alg": ALGORITHM, "entries": self.entries}, handle)

    @classmethod
    def load(cls, path, iterations=DEFAULT_ITERATIONS):
        """Read a vault back. A missing file gives an empty vault."""
        vault = cls(iterations=iterations)
        try:
            with open(path, encoding="utf-8") as handle:
                stored = json.load(handle)
        except FileNotFoundError:
            return vault
        vault.entries = dict(stored.get("entries", {}))
        return vault
'''},
            {"name": "main.py", "content": r'''
from vault import Vault, IntegrityError, DEFAULT_ITERATIONS

THREAT_MODEL = (
    "The attacker assumed here is one who steals the saved vault file: a lost "
    "laptop, a copied backup, a compromised host. Against that attacker the "
    "design offers two things. Confidentiality comes from a key that exists "
    "nowhere in the file: every entry has its own 16-byte salt and the key is "
    "derived with PBKDF2-HMAC-SHA256, so a stolen file cannot be attacked with "
    "precomputed tables and each guessed password costs the attacker the full "
    "iteration count. Integrity comes from encrypt-then-MAC: the HMAC tag "
    "covers the algorithm label, the salt, the nonce, the iteration count and "
    "the ciphertext, so an attacker who edits any of them - including quietly "
    "lowering the iteration count to make guessing cheaper - produces a record "
    "that fails to authenticate, and open_record then returns nothing at all "
    "rather than plausible rubbish. The tag is compared byte-independently, so "
    "an attacker who can time the comparison learns nothing from it. "
    "What this design does not defend against, and should not be trusted to: "
    "a weak password, because no iteration count rescues a password an "
    "attacker can guess in a thousand tries; an attacker present on the "
    "machine while the vault is open, since plaintext and derived keys sit in "
    "ordinary Python objects that are never wiped and may be paged to disk; a "
    "keylogger or a shoulder-surfer, who takes the password before any of this "
    "code runs; traffic analysis of the file itself, which reveals how many "
    "entries exist, their names and the length of every secret, all of which "
    "are stored in the clear; and finally the numbers themselves - 4096 "
    "PBKDF2 iterations is a teaching value chosen to keep the checks fast, "
    "where a deployed system in the 2020s would use a memory-hard function "
    "such as scrypt or Argon2id, or at minimum several hundred thousand "
    "iterations."
)

vault = Vault(iterations=DEFAULT_ITERATIONS)
vault.add("bank", "hunter2", "sort code 60-16-13")
vault.add("diary", "another password", "today I wrote a compiler")

print("entries:", vault.names())
print("bank:", vault.get("bank", "hunter2"))
try:
    vault.get("bank", "wrong password")
    print("the wrong password opened the record, which is a bug")
except IntegrityError:
    print("wrong password rejected")

vault.save("vault.json")
reloaded = Vault.load("vault.json")
print("reloaded entries:", reloaded.names())
print("diary:", reloaded.get("diary", "another password"))
'''},
        ],
        "tests": [
            {"name": "The primitives match the published vectors", "code": r'''
from vault import hmac_sha256, pbkdf2
_got = hmac_sha256(b"Jefe", b"what do ya want for nothing?").hex()
assert _got == "5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843", \
    f"HMAC-SHA256 vector failed: got {_got}"
_got = pbkdf2(b"password", b"salt", 2, 32).hex()
assert _got == "ae4d0c95af6b46d32d0adff928f06dd02a303f8ef3c251dfd6e2d85a95474c43", \
    f"PBKDF2 vector failed: got {_got}"
assert len(pbkdf2(b"p", b"s", 2, 64)) == 64, "a 64-byte derived key needs two blocks"
'''},
            {"name": "seal and open_record round-trip", "code": r'''
from vault import seal, open_record
for _message in ["attack at dawn", "", "unicode: æøå ✓", "x" * 500]:
    _record = seal("hunter2", _message, iterations=512)
    _back = open_record("hunter2", _record)
    assert _back == _message, f"round trip gave {_back!r}, expected {_message!r}"
'''},
            {"name": "The record carries the parameters it needs and nothing else", "code": r'''
from vault import seal, unb64
_record = seal("hunter2", "attack at dawn", iterations=512)
assert set(_record) == {"alg", "iterations", "salt", "nonce", "ciphertext", "tag"}, \
    f"the record fields are {sorted(_record)!r}"
assert _record["alg"] == "vault1", f"algorithm label was {_record['alg']!r}"
assert _record["iterations"] == 512, f"iterations field was {_record['iterations']!r}"
assert len(unb64(_record["salt"])) == 16, "the salt is 16 bytes"
assert len(unb64(_record["nonce"])) == 8, "the nonce is 8 bytes"
assert len(unb64(_record["tag"])) == 32, "the tag is a full SHA-256 HMAC"
assert len(unb64(_record["ciphertext"])) == len("attack at dawn".encode("utf-8")), \
    "a stream cipher does not change the length"
import json as _json
_json.dumps(_record)
'''},
            {"name": "Salt and nonce are fresh every time", "code": r'''
from vault import seal, open_record
_a = seal("hunter2", "attack at dawn", iterations=256)
_b = seal("hunter2", "attack at dawn", iterations=256)
assert _a["salt"] != _b["salt"], "each record needs its own salt"
assert _a["nonce"] != _b["nonce"], "each record needs its own nonce"
assert _a["ciphertext"] != _b["ciphertext"], \
    "the same message under the same password must not encrypt to the same bytes"
assert open_record("hunter2", _a) == open_record("hunter2", _b) == "attack at dawn", \
    "and both must still open"
'''},
            {"name": "The ciphertext does not contain the plaintext", "code": r'''
from vault import seal, unb64
_message = "sort code 60-16-13, account 31926819"
_raw = unb64(seal("hunter2", _message, iterations=256)["ciphertext"])
assert _message.encode("utf-8") not in _raw, "the plaintext is sitting in the ciphertext"
for _word in (b"sort", b"account", b"31926819"):
    assert _word not in _raw, f"{_word!r} survived the encryption"
'''},
            {"name": "A wrong password yields an error, not rubbish", "code": r'''
from vault import seal, open_record, IntegrityError
_record = seal("hunter2", "attack at dawn", iterations=256)
for _wrong in ["hunter3", "", "HUNTER2", "hunter2 "]:
    try:
        _got = open_record(_wrong, _record)
        assert False, f"the password {_wrong!r} should not open the record (got {_got!r})"
    except IntegrityError:
        pass
'''},
            {"name": "Every field is under the tag", "code": r'''
from vault import seal, open_record, b64, unb64, IntegrityError
_record = seal("hunter2", "attack at dawn", iterations=256)
def _flip(record, field):
    _raw = bytearray(unb64(record[field]))
    _raw[0] ^= 1
    _copy = dict(record)
    _copy[field] = b64(bytes(_raw))
    return _copy
for _field in ("ciphertext", "tag", "salt", "nonce"):
    try:
        open_record("hunter2", _flip(_record, _field))
        assert False, f"a flipped bit in {_field} should raise IntegrityError"
    except IntegrityError:
        pass
_lowered = dict(_record)
_lowered["iterations"] = 1
try:
    open_record("hunter2", _lowered)
    assert False, "lowering the iteration count should raise IntegrityError"
except IntegrityError:
    pass
_relabelled = dict(_record)
_relabelled["alg"] = "vault0"
try:
    open_record("hunter2", _relabelled)
    assert False, "an unknown algorithm label should raise IntegrityError"
except IntegrityError:
    pass
'''},
            {"name": "The tag is compared in constant time, before decrypting", "code": r'''
import vault as _vault
_record = _vault.seal("hunter2", "attack at dawn", iterations=256)
_calls = []
_real = _vault.constant_time_equals
def _spy(a, b):
    _calls.append((bytes(a), bytes(b)))
    return _real(a, b)
_vault.constant_time_equals = _spy
try:
    assert _vault.open_record("hunter2", _record) == "attack at dawn"
finally:
    _vault.constant_time_equals = _real
assert _calls, "open_record should compare the tag through constant_time_equals"
assert all(len(a) == 32 for a, b in _calls), \
    f"the compared values should be 32-byte tags, got lengths {[len(a) for a, b in _calls]}"
assert _vault.constant_time_equals(b"ab", b"ab") is True
assert _vault.constant_time_equals(b"ab", b"aB") is False
assert _vault.constant_time_equals(b"ab", b"abc") is False, "different lengths differ"
'''},
            {"name": "The vault stores, finds and forgets entries", "code": r'''
from vault import Vault, IntegrityError
_v = Vault(iterations=256)
assert _v.names() == [], "a new vault is empty"
_v.add("bank", "hunter2", "sort code 60-16-13")
_v.add("diary", "another password", "today I wrote a compiler")
assert _v.names() == ["bank", "diary"], f"names() gave {_v.names()!r}"
assert _v.get("bank", "hunter2") == "sort code 60-16-13", "the entry must come back"
try:
    _v.get("missing", "hunter2")
    assert False, "an unknown name should raise KeyError"
except KeyError:
    pass
try:
    _v.get("bank", "another password")
    assert False, "one entry's password must not open another's"
except IntegrityError:
    pass
_v.remove("bank")
assert _v.names() == ["diary"], f"after remove, names() gave {_v.names()!r}"
try:
    _v.remove("bank")
    assert False, "removing something twice should raise KeyError"
except KeyError:
    pass
_other = Vault(iterations=256)
assert _other.names() == [], "two vaults must not share entries"
'''},
            {"name": "Persistence keeps the secrets secret", "code": r'''
from vault import Vault
_v = Vault(iterations=256)
_v.add("bank", "hunter2", "sort code 60-16-13")
_v.add("diary", "another password", "today I wrote a compiler")
_v.save("cap_vault.json")
_text = open("cap_vault.json", encoding="utf-8").read()
for _secret in ("sort code", "60-16-13", "compiler", "hunter2"):
    assert _secret not in _text, f"{_secret!r} was written to the file in the clear"
_back = Vault.load("cap_vault.json")
assert _back.names() == ["bank", "diary"], f"reloaded names were {_back.names()!r}"
assert _back.get("bank", "hunter2") == "sort code 60-16-13", "and the entry still opens"
assert Vault.load("no-such-vault-8811.json").names() == [], \
    "a missing file should load as an empty vault"
'''},
            {"name": "main.py demonstrates the system and states the threat model", "code": r'''
assert "wrong password rejected" in _out, \
    f"main.py should show the wrong password being refused; it printed:\n{_out}"
assert "sort code 60-16-13" in _out, "main.py should show a successful retrieval"
assert isinstance(THREAT_MODEL, str) and len(THREAT_MODEL) >= 400, \
    f"THREAT_MODEL is {len(THREAT_MODEL)} characters; write a real one"
_terms = ["salt", "iteration", "integrity", "password", "memory", "offline",
          "tamper", "argon", "scrypt", "keylog"]
_hits = [t for t in _terms if t in THREAT_MODEL.lower()]
assert len(_hits) >= 4, \
    f"THREAT_MODEL should name concrete threats and limits; it mentions only {_hits!r}"
_src = open("vault.py", encoding="utf-8").read()
assert "print(" not in _src, "vault.py is a library — the printing belongs in main.py"
assert "pbkdf2_hmac" not in _src, "the point of the exercise is your own PBKDF2"
assert "import hmac" not in _src, "the point of the exercise is your own HMAC"
'''},
        ],
    },
}
