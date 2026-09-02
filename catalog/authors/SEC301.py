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
            "read": [
                {
                    "title": "Counting letters, and why that was enough",
                    "minutes": 16,
                    "body": r'''
In the summer of 1586 a clerk named Thomas Phelippes sat in Sir Francis Walsingham's
house in London with a stack of letters that were not addressed to him. They had passed
between Mary, Queen of Scots, held under guard in Staffordshire, and Anthony Babington
in London, smuggled in and out of the house in the stopper of a beer barrel by a courier
who was working for Walsingham the whole time. The letters were enciphered — a couple of
dozen symbols standing for letters, three dozen more standing for names and common
words — and Phelippes had no table.

So he counted. He tallied how often each symbol appeared, and how often pairs of them
appeared side by side, and wrote the tallies in the margin. English hands roughly one
letter in eight to `e` and about one in a thousand to `q`; a symbol turning up a hundred
and twenty times in a thousand is not going to be `q`. Within days he had reconstructed
the table. He deciphered the letter in which Mary approved the killing of Elizabeth,
drew a gallows on his copy, and sent it on. She was tried that October and executed the
following February. The thing that convicted her was arithmetic done on paper by someone
who never saw the key.

That is the whole of classical cryptanalysis in one anecdote, and the rest of this
reading is about turning Phelippes' marginal tallies into two numbers a program can
compute.

## What a tally is really measuring

Put every letter of a message into a bag and draw two of them out, without replacement.
What is the chance they are the same letter?

Count the pairs. If the letter `e` occurs $n_e$ times, there are $n_e(n_e - 1)$ ordered
ways to draw `e` twice. Every letter contributes its own such term, and the total number
of ordered draws is $N(N-1)$ for a text of $N$ letters. Divide one by the other and you
have the *index of coincidence*:

$$\text{IC} = \frac{\sum_{i=a}^{z} n_i\,(n_i - 1)}{N\,(N-1)}$$

Nothing was assumed there about English, or about ciphers. It is a count of matching
pairs divided by a count of pairs. Do it by hand on the word `coincidence`, which has
three `c`, two each of `i`, `n` and `e`, and one each of `o` and `d`:

```python
from collections import Counter

word = "coincidence"
counts = Counter(word)
n = len(word)
equal = sum(k * (k - 1) for k in counts.values())
print(sorted(counts.items()))
print(equal, "matching pairs out of", n * (n - 1))
print("IC =", round(equal / (n * (n - 1)), 4))
```

That prints `12 matching pairs out of 110` and an IC of `0.1091`: the three `c` supply
$3 \times 2 = 6$ of the twelve, and the three doubled letters supply two each.

Now let the text get long. If letter $i$ turns up with probability $p_i$, the chance both
draws land on it approaches $p_i^2$, so the IC of a long passage tends to $\sum_i p_i^2$.
That sum is a property of the *language*, not of the message. Using the frequency table
the lab gives you:

```python
ENGLISH_FREQ = {
    "a": 0.08167, "b": 0.01492, "c": 0.02782, "d": 0.04253, "e": 0.12702,
    "f": 0.02228, "g": 0.02015, "h": 0.06094, "i": 0.06966, "j": 0.00153,
    "k": 0.00772, "l": 0.04025, "m": 0.02406, "n": 0.06749, "o": 0.07507,
    "p": 0.01929, "q": 0.00095, "r": 0.05987, "s": 0.06327, "t": 0.09056,
    "u": 0.02758, "v": 0.00978, "w": 0.02360, "x": 0.00150, "y": 0.01974,
    "z": 0.00074,
}
print("English prose:", round(sum(p * p for p in ENGLISH_FREQ.values()), 4))
print("uniform noise:", round(26 * (1 / 26) ** 2, 4))
```

`0.0655` against `0.0385`. Those two numbers are the entire attack surface of this
module. English is skewed, so its letters collide nearly twice as often as letters drawn
uniformly do, and the IC reports that skew in one number without knowing a word of
English.

## Why a Caesar shift cannot hide from it

Look at the formula again. It depends on the counts $n_i$ but never on *which* letter had
which count — replace every `e` by `h` and every `h` by `k` and the multiset of counts is
untouched, so the IC is untouched. A monoalphabetic substitution is exactly such a
relabelling. Its ciphertext therefore scores about 0.067 as loudly as the plaintext did,
which is why Phelippes' method worked at all.

The polyalphabetic answer, published by Bellaso in 1553 and later attached to Vigenere's
name, was to move the alphabet along: letter $i$ of the message is shifted by key letter
$i \bmod k$. Now two letters drawn from different positions were usually shifted by
different amounts, and the coincidence probability for a pair shifted by a relative
displacement $d$ is $\sum_i p_i\,p_{i+d}$, which for almost every $d$ is close to
$1/26$. Interleave enough alphabets and the IC of the whole ciphertext falls towards
0.0385. For three hundred years that was thought to be the end of the matter, and the
cipher was called *le chiffre indechiffrable*.

The crack is one line of reasoning. Take every $k$-th letter of the ciphertext. Every one
of them was shifted by the *same* key letter, so that slice is a monoalphabetic
enciphering of a sample of English — and by the argument above its IC is back at 0.067.
A wrong $k$ mixes alphabets together and the slice scores near 0.038. So the period
announces itself: try each candidate length, average the IC over its slices, and read off
which one lights up.

## The trace

Here is that scan on 504 letters of prose enciphered with the six-letter key `cipher`:

```python
import string

ALPHABET = string.ascii_lowercase
TEXT = (
    "The people who wrote ciphers were far more confident than the people who "
    "broke them had any reason to allow. A substitution cipher hides the shape "
    "of a letter but not the shape of a language. Vowels cluster, doubled "
    "letters repeat, short words appear again and again, and every one of those "
    "habits survives the journey through a naive cipher and arrives on the far "
    "side intact. The first analysts to notice this counted letters, by hand, "
    "in the margins of the messages they had intercepted, and they found that "
    "the frequency of a letter in a long passage of ordinary prose is "
    "remarkably stable. That stability is a weakness."
)


def ic(body):
    n = len(body)
    if n < 2:
        return 0.0
    return sum(body.count(c) * (body.count(c) - 1) for c in ALPHABET) / (n * (n - 1))


plain = "".join(c for c in TEXT.lower() if c in ALPHABET)
key = "cipher"
secret = "".join(
    ALPHABET[(ALPHABET.index(c) + ALPHABET.index(key[i % len(key)])) % 26]
    for i, c in enumerate(plain)
)

print(len(plain), "letters")
print("plaintext  IC %.4f" % ic(plain))
print("ciphertext IC %.4f" % ic(secret))
for length in range(1, 13):
    columns = [secret[start::length] for start in range(length)]
    average = sum(ic(col) for col in columns) / length
    print("period %2d  %.4f %s" % (length, average, "<--" if average >= 0.06 else ""))
```

The plaintext scores 0.0694 and the ciphertext 0.0454. The scan gives 0.0454, 0.0502,
0.0551, 0.0502, 0.0472, **0.0713**, 0.0450, 0.0496, 0.0556, 0.0548, 0.0468, **0.0728**.

Two things in that list are worth stopping on. The wrong periods do not sit at 0.0385;
they wander between 0.045 and 0.056, because a slice of 84 letters is a small sample and
the IC of a small sample is noisy. The signal is a gap, not a threshold reached from
below. And period 12 scores *higher* than period 6 — because every 12th letter is also
every 6th letter, so `key[i % 12 % 6]` is `key[i % 6]` and any multiple of the true
period is also a valid period. Return the highest-scoring length and this ciphertext
hands you a twelve-letter key that is `cipher` written twice. That is precisely why
`guess_key_length` in the lab is specified as *the smallest length whose average reaches
0.06*, with the highest average kept only as a fallback for texts where nothing crosses
the line.

## Reading one column

The period splits the problem into six independent Caesar shifts, and 26 candidates each
is 156 trials against $26^6 \approx 3 \times 10^8$ for the key as a whole. That collapse
is the reason key recovery beats brute force, and it is worth naming: the columns are
independent because nothing in the cipher couples them.

To pick the shift you need a number for "this looks like English". Shift the column back
by a guess and count its letters. English predicts $E_\ell = p_\ell \cdot n$ occurrences
of letter $\ell$ in $n$ letters; you observe $O_\ell$. Summing $(O_\ell - E_\ell)^2$ would
weigh a miss of 3 on a letter expected 10 times the same as a miss of 3 on a letter
expected 0.08 times, and those are not comparable errors — the second is outrageous and
the first is nothing. Scale each squared gap by the size of the thing it is a gap in, and
you have the chi-squared statistic:

$$\chi^2 = \sum_{\ell} \frac{(O_\ell - E_\ell)^2}{E_\ell}$$

Small is good. Run all 26 shifts on the first column of the ciphertext above:

```python
import string

ALPHABET = string.ascii_lowercase
ENGLISH_FREQ = {
    "a": 0.08167, "b": 0.01492, "c": 0.02782, "d": 0.04253, "e": 0.12702,
    "f": 0.02228, "g": 0.02015, "h": 0.06094, "i": 0.06966, "j": 0.00153,
    "k": 0.00772, "l": 0.04025, "m": 0.02406, "n": 0.06749, "o": 0.07507,
    "p": 0.01929, "q": 0.00095, "r": 0.05987, "s": 0.06327, "t": 0.09056,
    "u": 0.02758, "v": 0.00978, "w": 0.02360, "x": 0.00150, "y": 0.01974,
    "z": 0.00074,
}
# every sixth letter of that ciphertext: one Caesar shift, 84 letters
COLUMN = ("vrykytqpvrdjcunwwkkgqvpuhwywqnuvyrifcthjugqvjgttptpj"
          "vuqjpvapthuvfecavggctpctaktuvcac")


def chi_squared(shift):
    plain = "".join(ALPHABET[(ALPHABET.index(c) - shift) % 26] for c in COLUMN)
    total = 0.0
    for letter in ALPHABET:
        expected = ENGLISH_FREQ[letter] * len(COLUMN)
        total += (plain.count(letter) - expected) ** 2 / expected
    return total


scores = sorted((chi_squared(s), s) for s in range(26))
for score, shift in scores[:3]:
    print("shift %2d (%s)  chi-squared %7.1f" % (shift, ALPHABET[shift], score))
print("worst of the 26: shift %d, %.1f" % (scores[-1][1], scores[-1][0]))

commonest = max(ALPHABET, key=COLUMN.count)
print("commonest letter:", commonest, COLUMN.count(commonest), "of", len(COLUMN))
print("if that were 'e' the key letter would be",
      ALPHABET[(ALPHABET.index(commonest) - ALPHABET.index("e")) % 26])
```

Shift 2 — the letter `c`, the first letter of the key — scores 23.3. The runner-up scores
226.3 and the worst candidate 2345.9. A factor of ten between first and second place is
not a close call, and it holds up over columns of a few dozen letters.

## The shortcut that eats keys

The tempting move is to skip chi-squared. `e` is the commonest letter in English, so
find the commonest letter in the column, assume it is the enciphered `e`, and subtract.
One count instead of twenty-six, and on a long single-alphabet text it is nearly always
right.

The last two lines of that block show what it does here. The commonest letter in the
column is `v`, ten of the 84, which would make the key letter `r`. The key letter is `c`.
Run the same shortcut on all six columns of this ciphertext and it returns `rxpher`:
four letters right, two wrong, and a Vigenere key with two wrong letters decrypts to
gibberish in a third of its positions — it is not a near miss you can read through.

The reason is sample size. In 84 letters `e` is expected 10.7 times and `t` 7.6, and the
standard deviation of a count that size is around 3. The top of the table is a coin toss.
Chi-squared survives because it is not deciding on one letter: the 24 letters nobody is
arguing about still vote, and `q`, `j`, `x` and `z` vote hardest of all, since expecting
0.08 occurrences of `q` and observing three is a contribution of over a hundred on its
own. The lesson generalises past this cipher: a statistic that pools all the evidence
beats one that reads the maximum, and it beats it by more the less data you have.

## Where this stops working

The counting argument needs letters to count. Below roughly 30 letters per column both
statistics are noise, so a 60-letter message under a 10-letter key is out of reach — the
columns have six letters each and no amount of cleverness puts information there that
was never sent. Push that to its limit: make the key as long as the message and never
reuse it, and every column holds one letter. The IC is undefined, chi-squared has one
observation, and the attack has nothing to bite on. That is the one-time pad, and its
security is not a matter of the attack being hard.

Chi-squared also needs the right table. A message in Welsh, a base64 blob, a compressed
file — all defeat the scoring step while leaving the IC step working, because the IC only
needs the plaintext to be skewed somehow, not skewed like English. And a key with
internal repetition breaks the tidy story about periods: encipher with `abab` and the
true period is 2. The scan finds 2, and it is right; the key it reports is `ab`. The
0.06 threshold itself is a tuned constant, not a law — it sits in the gap between 0.038
and 0.067 at the message sizes this course uses, and on a very short text nothing reaches
it, which is why the specification names a fallback.

## The lab

**Vigenere, and a full key recovery** asks you to build both halves of this. First the
cipher: `vigenere_encrypt` and `vigenere_decrypt`, differing only in the sign of the
shift, with the detail that catches almost everybody — a non-letter passes through and
does **not** consume a key letter, so `"Attack at dawn!"` under `lemon` is
`"Lxfopv ef rnhr!"` and not something a space has pushed out of step. Then the attack:
`index_of_coincidence` (returning 0.0 rather than dividing by zero when there are fewer
than two letters), `average_ic`, `guess_key_length` with the 0.06 rule you now know the
reason for, `crack_column` with chi-squared, and `crack_key` assembling the columns. The
checks encipher the same passage under keys of length 5, 6, 8 and 11 and require the
exact key and the exact plaintext back, from the ciphertext alone.
''',
                },
            ],
            "quiz": {
                "title": "Periods, coincidences and the shape of a language",
                "minutes": 9,
                "questions": [
                    {
                        "q": "A message is enciphered with a simple monoalphabetic substitution — a fixed table sending each letter to another. What happens to the index of coincidence?",
                        "opts": [
                            "It drops to about 0.038, since the ciphertext letters are now spread evenly over the alphabet",
                            "It rises above 0.067, because a substitution table concentrates the text on fewer distinct letters",
                            "It stays at about 0.067: the statistic depends on the counts, not on which letters carry them",
                            "It becomes impossible to compute until the substitution table itself has been recovered",
                        ],
                        "a": 2,
                        "whys": [
                            r"Nothing was spread out. A substitution is a bijection: the letter that occurred 87 times still occurs 87 times, under a new name. Flattening the counts is what a *poly*alphabetic cipher does, and that is the whole difference between the two.",
                            r"A table sends distinct letters to distinct letters, so the number of distinct symbols is unchanged and no concentration happens. Concentration would raise the IC, but nothing here causes any.",
                            r"The formula reads $n_i(n_i-1)$ summed over the alphabet, and relabelling permutes the terms of a sum.",
                            r"The IC is computed from the ciphertext by counting it, with no table involved — that is the property that makes it useful. Needing the key to measure the text would leave the statistic with no attack to be part of.",
                        ],
                        "why": r"""
The IC is a sum of $n_i(n_i - 1)$ over the alphabet, and a substitution permutes which
letter carries which count without changing the multiset of counts. A permuted sum is the
same sum, so English enciphered this way still scores about 0.067 — and that is exactly
why frequency analysis undoes it. The number only falls when several different shifts are
interleaved, because then a pair of letters drawn from different positions was
enciphered under different alphabets.
""",
                    },
                    {
                        "q": "Scanning candidate periods on a Vigenere ciphertext gives average ICs of 0.045, 0.050, 0.055, 0.050, 0.047, 0.071, 0.045, 0.050, 0.056, 0.055, 0.047, 0.073 for lengths 1 to 12. What is the key length?",
                        "opts": [
                            "12, because it has the highest average and the highest score is the strongest evidence available",
                            "6, because 12 scores high only as a multiple of 6, and a multiple of a period is a period too",
                            "3, because 0.055 is the first score to rise well above the run of values before it",
                            "It cannot be told apart from 12 without a second ciphertext enciphered under the same key",
                        ],
                        "a": 1,
                        "whys": [
                            r"Highest is the wrong test, and this list shows why: taking every 12th letter of a text with period 6 gives a slice that is still one alphabet, and a shorter slice of a purer sample often scores a shade higher. Trusting the maximum returns `cipher` written out twice.",
                            r"`key[i % 12 % 6]` is `key[i % 6]`, so the multiples all light up and the smallest is the real one.",
                            r"0.055 is inside the noise of the wrong periods here — 9 and 10 score 0.056 and 0.055 without meaning anything. The gap that matters is the one to 0.071, and 3 is not on the right side of it.",
                            r"One ciphertext is enough, and the tie is broken by taking the smallest length that crosses the line rather than by gathering more material. That rule is in the specification for exactly this reason.",
                        ],
                        "why": r"""
Every 12th letter is also every 6th letter, so if the true period is 6 then period 12
slices are still single-alphabet and score as high — often a touch higher, since a
shorter slice of one alphabet can be a cleaner sample. Multiples of the true period all
light up, which is why the rule is *the smallest length whose average reaches the
threshold* rather than the highest average. Reading the maximum off this table returns a
twelve-letter key that is the six-letter one repeated.
""",
                    },
                    {
                        "q": "Why is the chi-squared score divided by the expected count of each letter rather than left as a plain sum of squared differences?",
                        "opts": [
                            "To keep the total below 1.0 so that scores from columns of different lengths can be compared",
                            "Because dividing is what makes the statistic reach its minimum at the correct shift instead of its maximum",
                            "Because a miss of three on a letter expected 0.08 times is damning, and on one expected ten times is not",
                            "Because the expected counts must sum to the column length, which the division is what enforces",
                        ],
                        "a": 2,
                        "whys": [
                            r"It does no such thing: the worst shift on an 84-letter column scores 2345.9, and the statistic grows with the column length under every shift. Comparability across columns is not what the division buys, and it is not needed, since shifts are only ever compared within one column.",
                            r"The minimum is at the correct shift either way — a plain sum of squares is also smallest when the counts match. What changes is how reliably it is smallest, since without the weighting the rare letters carry almost no influence at all.",
                            r"Weighting each squared gap by the size of the thing it is a gap in is the difference between noise and evidence.",
                            r"They sum to the column length because the frequencies sum to 1, and they do that before any division. The scaling happens inside the sum over letters and changes no total.",
                        ],
                        "why": r"""
An absolute gap of three means very different things at different expected counts: on a
letter English predicts ten times it is ordinary sampling noise, and on `q`, predicted
0.08 times in 84 letters, it is a contribution of over a hundred to the score all by
itself. Dividing by $E_\ell$ turns each term into a gap measured in units of the scale it
lives on, which is what lets the rare letters — the ones that are most informative
precisely because they should hardly ever appear — carry weight. It is also why
chi-squared beats the shortcut of matching the commonest letter to `e`: every letter
votes, not only the argmax.
""",
                    },
                    {
                        "q": "On an 84-letter column, taking the commonest letter to be the enciphered `e` gives the wrong key letter more often than not. What is the underlying reason?",
                        "opts": [
                            "The shortcut assumes a monoalphabetic cipher, and a column of a Vigenere ciphertext is not one",
                            "`e` is the commonest letter of English in general but rarely the commonest in any one passage",
                            "In 84 letters `e` is expected about 10.7 times and `t` about 7.6, a gap smaller than the sampling noise",
                            "The column holds only every sixth letter of the message, and a subsequence like that is no longer English",
                        ],
                        "a": 2,
                        "whys": [
                            r"A column *is* monoalphabetic — that is the entire point of slicing by the period, and it is what makes any letter-frequency reasoning legal here. If the assumption failed, chi-squared would fail with it, and chi-squared reads this column correctly.",
                            r"`e` really is the commonest letter in the great majority of English passages of any length; the tables are not a fluke of one corpus. The trouble is not that `e` is unusual, it is that 84 letters is too few to resolve a lead of three expected occurrences.",
                            r"A count of ten has a standard deviation around three, so the top of the table is close to a coin toss.",
                            r"Every sixth letter of English prose has the same letter frequencies as the prose does — sampling every sixth letter does not change what letters are there, only how many. If the subsequence were not English-distributed, the whole column attack would collapse.",
                        ],
                        "why": r"""
Sampling noise, and nothing more exotic. With $n = 84$ the expected counts are 10.7 for
`e` and 7.6 for `t`, while the standard deviation of a count near ten is about three, so
which of them tops the table in any particular column is close to a coin toss. On the
worked ciphertext the commonest letter is `v`, which would name the key letter `r` when
the truth is `c`, and running the shortcut over all six columns yields `rxpher` — four of
six right, which decrypts to nothing readable. Chi-squared survives the same 84 letters
because it pools all 26 counts instead of reading the maximum of two of them.
""",
                    },
                    {
                        "q": "A 60-letter message is enciphered with a 10-letter Vigenere key. Why does the index-of-coincidence attack fail on it?",
                        "opts": [
                            "Because a 10-letter key exceeds the 16-length scan and the true period is never tried at all",
                            "Because each of the ten columns holds six letters, far too few for either statistic to mean anything",
                            "Because a key that long makes the ciphertext's own index of coincidence rise back towards that of English",
                            "Because the key is longer than the alphabet is deep, so several columns share the same shift",
                        ],
                        "a": 1,
                        "whys": [
                            r"A scan to length 16 does try 10; the difficulty arrives after the length has been tried, when the six-letter slices score nothing distinguishable. Widening the scan changes none of that.",
                            r"Six letters give fifteen pairs to count and six observations against 26 expected frequencies.",
                            r"It moves the other way. Interleaving more alphabets pushes the whole ciphertext's IC further towards 0.038, not back towards 0.067 — that is what a longer key is for.",
                            r"Ten is smaller than 26, and in any case repeated shifts within a key would help an attacker rather than hinder one: two columns with the same shift are one longer column, which is more evidence and not less.",
                        ],
                        "why": r"""
Slicing by 10 leaves columns of six letters. Six letters give $6 \times 5 = 30$ ordered
pairs for an IC estimate and six observations to compare against 26 expected frequencies,
so both statistics are dominated by noise and the correct period does not stand out from
the wrong ones. This is a limit of the evidence, not of the method: the message never
carried enough repetition to reveal any. Extend the idea and it is the one-time pad —
a key as long as the message puts exactly one letter in every column, and the attack has
nothing left to count.
""",
                    },
                    {
                        "q": "Recovering a 6-letter key column by column costs 156 trials rather than the $26^6$ of a brute-force search. What property of the cipher makes that collapse legitimate?",
                        "opts": [
                            "Chi-squared is an approximation, and 156 trials is the price of its small chance of error",
                            "Each column is scored on its own, and no key letter's correctness depends on any other being right",
                            "The scan has already ruled out most keys, leaving only 156 of the $26^6$ still consistent with the ciphertext",
                            "English redundancy means most of the $26^6$ keys produce identical decryptions and need not be tried twice",
                        ],
                        "a": 1,
                        "whys": [
                            r"Cost and accuracy are separate matters here. The saving comes from the problem splitting into six independent ones, and it would still be 156 trials if the scoring function were exact.",
                            r"Column $j$ is enciphered by key letter $j$ and by nothing else, so its 26 candidates can be judged without knowing any other column.",
                            r"The scan produced one number, the period. It eliminated no key letters whatever — all $26^6$ six-letter keys are still consistent with the ciphertext after it, and what changed is that they no longer have to be searched as a block.",
                            r"Different keys give different decryptions, and duplicates are not the issue. Redundancy is what makes chi-squared able to *score* a candidate; it is not what reduces the number of candidates.",
                        ],
                        "why": r"""
The cipher applies key letter $j$ to column $j$ and to nothing else, so the six choices
are independent and can be made one at a time — 6 columns times 26 shifts is 156 scored
decryptions, against $26^6 \approx 3 \times 10^8$ for the key as a whole. Independence is
the whole saving, and it is a property of the construction rather than of the attack: a
cipher whose key letters interacted, so that a column could not be judged until its
neighbours were right, would not decompose this way. Judging a design by the structure it
leaves for an attacker to exploit, rather than by the size of its key space, is the habit
this module exists to build.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "Why a stolen password file is not a stolen secret",
                    "minutes": 17,
                    "body": r'''
On 5 June 2012 a file appeared on a Russian password-cracking forum: 6,458,020 lines,
each one forty hexadecimal characters. It was the SHA-1 password hashes of LinkedIn
accounts, with no salt and no iteration. The forum was not asked to break the hash
function; it was asked to help finish a list. Within days the great majority were
recovered, and four years later a set of about 117 million credentials from the same
breach went on sale.

Look at what the file gives away before anyone does any work at all:

```python
import hashlib

USERS = [("ada", "letmein"), ("bob", "hunter2"), ("cy", "letmein"),
         ("dee", "password1"), ("eve", "hunter2")]

print("unsalted SHA-256, first 12 hex characters")
for name, password in USERS:
    print("  %-4s %s" % (name, hashlib.sha256(password.encode()).hexdigest()[:12]))

print("salted, one fixed 8-byte salt per user")
for i, (name, password) in enumerate(USERS):
    salt = b"salt%04d" % i
    print("  %-4s %s" % (name, hashlib.sha256(salt + password.encode()).hexdigest()[:12]))
```

`ada` and `cy` both print `1c8bfe8f801d`; `bob` and `eve` both print `f52fbd32b2b3`. A
hash function is deterministic, so equal passwords give equal digests, and the dump
therefore sorts the users into groups by shared password without revealing a single one
of them. Sort those groups by size and the largest is almost certainly `123456`. Add a
different salt to each user and the five lines have nothing in common. The mechanism is
not subtle, and neither is the mistake it fixes.

## What preimage resistance actually promises

SHA-256's guarantee is that given a digest, finding *any* input that hashes to it costs
about $2^{256}$ work. That is a statement about the space of all inputs. A password is
not drawn from the space of all inputs. It is drawn from a list — a leaked corpus like
RockYou has around 14 million distinct entries, and a large fraction of real accounts are
in it. The hash function keeps every promise it made and the password falls anyway,
because the promise was about the wrong distribution.

So the attacker's cost is not $2^{256}$; it is the number of *distinct hash inputs* he
must compute. That is the quantity to attack, and every defence in this module is a way
of driving it up.

```python
GPU = 2e10            # raw SHA-256 compressions a second, one high-end 2024 card
DICTIONARY = 14e6     # unique entries in the leaked RockYou password list
USERS = 6.5e6         # accounts in the 2012 LinkedIn dump


def seconds(hashes):
    return hashes / GPU


print("unsalted, 1 hash per guess:    %.4f seconds" % seconds(DICTIONARY))
print("salted,   1 hash per guess:    %.0f minutes" % (seconds(DICTIONARY * USERS) / 60))
per_guess = 2 * 20000                      # two SHA-256 per HMAC, 20000 iterations
print("salted, 20000 iterations:      %.1f years"
      % (seconds(DICTIONARY * USERS * per_guess) / 86400 / 365))
print("one targeted user, 20000 iterations: %.0f seconds"
      % seconds(DICTIONARY * per_guess))
```

Unsalted, one pass over the dictionary covers **every user at once**: hash each candidate
once, look the digest up in a set of six and a half million, move on. That is 0.0007
seconds of hashing for the whole dump. Salted, the salt is part of the input, so the pass
has to be repeated for every user — 6.5 million times the work, and the same GPU now
needs 76 minutes.

Two conclusions, and the second is the uncomfortable one. The salt buys a factor of
6,500,000, which is why it is not optional. And 76 minutes is not safety. The salt kills
*precomputation and amortisation*; it does not make a single guess expensive, and by
itself it is nowhere near enough on 2024 hardware.

## Making one guess expensive

If the amortisation is gone, the remaining lever is the cost of one derivation. Multiply
it by $c$ and the attacker's bill multiplies by $c$ as well. That is PBKDF2:

$$U_1 = \text{HMAC}(pw,\; salt \,\|\, i), \qquad U_j = \text{HMAC}(pw,\; U_{j-1}),
\qquad T_i = U_1 \oplus U_2 \oplus \cdots \oplus U_c$$

Two design choices in there are worth deriving rather than accepting. Why a *chain*
instead of hashing one very long string? Because $U_j$ cannot start until $U_{j-1}$ has
finished, so the work inside a single guess is strictly sequential and no amount of
parallel hardware shortens it. Why XOR every intermediate in, rather than output $U_c$
alone? Because then the result depends on the whole chain. Should the iteration ever
wander into a short cycle, outputting the last value would silently collapse the output
space, while the running XOR still carries everything that came before the cycle.

The counter $i$ is there because one HMAC gives 32 bytes and a caller may want more:
blocks $T_1, T_2, \dots$ are generated with $i = 1, 2, \dots$ as four big-endian bytes and
concatenated, then truncated. That has a consequence the lab checks — the first 32 bytes
of a 64-byte derived key are exactly the 32-byte derived key, because $T_1$ does not know
how many blocks will follow.

With 20,000 iterations, each guess costs two SHA-256 per HMAC times 20,000, so 40,000
hashes. The salted attack that took 76 minutes takes 5.8 years.

## Why HMAC is not `sha256(key + message)`

The natural way to authenticate a message with a shared key is to hash them together.
It is the first thing almost everyone writes, and it is broken — not by a weakness in
SHA-256, but by the shape of it.

SHA-256 is a Merkle-Damgard construction: it pads the message to a whole number of
64-byte blocks and folds them one at a time into a 32-byte state, and **the digest it
returns is that state**. Hand someone a digest and you have handed them the machine's
internal condition at the moment it stopped. They can start it again.

Here is that attack in full, on a toy hash with the same shape:

```python
import hashlib

BLOCK = 8            # SHA-256 uses 64; the shape is the same
IV = b"\x00" * 8


def compress(state, block):
    """One compression step: old state and one block in, new state out."""
    return hashlib.sha256(state + block).digest()[:8]


def padding(length):
    """The suffix that makes a message a whole number of blocks, SHA-style."""
    pad = b"\x80" + b"\x00" * ((BLOCK - 1 - (length + 8) % BLOCK) % BLOCK)
    return pad + (length * 8).to_bytes(8, "big")


def toy_hash(message, state=IV, already=0):
    """Merkle-Damgard. `state`/`already` let a caller RESUME a finished hash."""
    data = message + padding(already + len(message))
    for i in range(0, len(data), BLOCK):
        state = compress(state, data[i:i + BLOCK])
    return state


secret = b"s3cr3t!!"                       # the attacker never sees this
message = b"user=ada&admin=0"
tag = toy_hash(secret + message)
print("server tag:", tag.hex())

# The attacker knows message, tag and len(secret) — and nothing else.
glue = padding(len(secret) + len(message))
extension = b"&admin=1"
forged_message = message + glue + extension
forged_tag = toy_hash(extension, state=tag,
                      already=len(secret) + len(message) + len(glue))
print("forged tag:", forged_tag.hex())
print("server would compute:", toy_hash(secret + forged_message).hex())
print("forgery accepted:", forged_tag == toy_hash(secret + forged_message))


def toy_hmac(key, message):
    """The same toy hash, wrapped the way RFC 2104 wraps SHA-256."""
    key = key + b"\x00" * (BLOCK - len(key))
    inner = bytes(b ^ 0x36 for b in key)
    outer = bytes(b ^ 0x5C for b in key)
    return toy_hash(outer + toy_hash(inner + message))


mac = toy_hmac(secret, message)
forged_mac = toy_hash(extension, state=mac, already=BLOCK + BLOCK)
print("HMAC forgery accepted:", forged_mac == toy_hmac(secret, forged_message))
```

It prints `forgery accepted: True`. The attacker never learned `secret`. He resumed the
hash from the tag, appended `&admin=1`, and produced a tag the server will accept for a
message he chose. The only thing he needed beyond the public message and its tag was the
*length* of the key, and that is usually guessable in a couple of dozen tries. This is
not a thought experiment: Flickr's API in 2009 signed requests with the digest of a
secret followed by the parameters, and Thai Duong and Juliano Rizzo forged calls against
it with exactly this.

Now look at what HMAC releases. It is $H(K_o \,\|\, H(K_i \,\|\, m))$, so the value on the
wire is the state of a hash whose input began with $K_o$ — and resuming it requires
knowing $K_o$, which the attacker does not. The last line prints `False`. The inner and
outer pads differ (`0x36` and `0x5c`) so that the two keys are different: reusing one key
for both passes would let a length-extension of the inner hash be replayed against the
outer one.

The mirror mistake, `sha256(message + key)`, resists length extension and fails
differently. Its security now leans on collision resistance: two messages that collide
under SHA-256 have the same tag under *every* key, so a collision found once forges
forever. HMAC needs neither property — its proof rests on the compression function
behaving like a pseudorandom function — which is why HMAC-MD5 did not fall the day MD5
collisions arrived.

## Comparing the answer

One line remains where a correct implementation still leaks. `digest == expected` in any
language stops at the first byte that differs, and the time it takes is therefore a
function of how many leading bytes were right.

```python
import hashlib

REAL = hashlib.sha256(b"transfer 100 to bob").digest()


def naive_equals(a, b):
    """`a == b` written out, so the bytes it inspects can be counted."""
    looked = 0
    for x, y in zip(a, b):
        looked += 1
        if x != y:
            return False, looked
    return True, looked


def constant_equals(a, b):
    looked = 0
    difference = 0
    for x, y in zip(a, b):
        looked += 1
        difference |= x ^ y
    return difference == 0, looked


for right in range(4):
    guess = REAL[:right] + bytes([REAL[right] ^ 0xFF]) + bytes(31 - right)
    print("first %d byte(s) correct -> naive inspects %d, constant-time inspects %d"
          % (right, naive_equals(REAL, guess)[1], constant_equals(REAL, guess)[1]))
print("guesses to walk a 32-byte tag one byte at a time:", 256 * 32)
print("guesses to search a 32-byte tag outright: 2 **", 8 * 32)
```

The naive count is 1, 2, 3, 4 — it is a direct readout of how much of the tag the
attacker already has. Turn that into an attack: try all 256 values of byte 0, keep the
one that took longest, then move to byte 1. That is $256 \times 32 = 8192$ attempts to
forge a tag, against $2^{256}$ to search for one. The fix is in the second function: OR
every `x ^ y` into an accumulator and test it once at the end, so the count is 32 whatever
the input. Google's Keyczar library shipped a byte-wise comparison in its HMAC
verification until 2009, when Nate Lawson pointed out that this made remote forgery
practical.

## Where all this stops holding

The last line of the cost table is the honest one: against a *targeted* user, 20,000
iterations buy 28 seconds. Salting and stretching destroy the bulk attack on a whole
dump; they do nothing about one weak password on one account someone cares about. No
server-side scheme repairs `hunter2`.

PBKDF2 also buys its cost in the one currency an attacker has cheapest. Its work is
sequential in *time* but needs a few hundred bytes of memory, so a GPU with thousands of
cores runs thousands of guesses side by side. scrypt and Argon2 answer that by demanding
megabytes per guess, which turns parallelism into silicon area; Argon2id won the Password
Hashing Competition in 2015 and is what a new system should use. PBKDF2 is in this course
because it is the one you can build from a hash function in twenty lines and check
against a published vector.

Iteration counts date, too. The 1,000 in RFC 8018's examples was a figure from around
2000, and current guidance for PBKDF2-HMAC-SHA256 is in the hundreds of thousands; the
lab's 20,000 is a teaching number chosen so the checks finish quickly. Because the right
number changes, a stored record has to *carry* the number it used, which is why the
format has four fields rather than two — and why the capstone's authentication tag covers
the iteration count as well as the ciphertext, so that nobody can quietly rewrite it
downwards.

Finally, constant-time comparison fixes the comparison and nothing else. If the code
around it branches on the length of the password, or the key derivation itself is
variable-time, the leak has moved rather than closed.

## The lab

**HMAC-SHA256 and PBKDF2 from scratch** builds this bottom-up from `hashlib.sha256` and
`secrets`, and grades it against the specifications rather than against itself. Your
`hmac_sha256` meets the RFC 4231 vectors, including the empty-key-empty-message case and
the 131-byte key that has to be hashed down to 32 bytes before padding; your `pbkdf2`
meets the RFC 8018 vectors at 1, 2 and 4096 iterations, plus a 64-byte derivation whose
first 32 bytes must equal the 32-byte one. `constant_time_equals` must inspect every byte
of an equal-length pair, `hash_password` must emit
`pbkdf2_sha256$20000$<salt hex>$<key hex>` with a fresh salt every call, and one check
replaces `constant_time_equals` with a spy to confirm that `verify_password` goes through
it rather than around it.
''',
                },
            ],
            "quiz": {
                "title": "Salts, stretching and the two ways to build a MAC",
                "minutes": 9,
                "questions": [
                    {
                        "q": "The salt is stored in the clear, right next to the digest it was used with. Why does adding it help at all?",
                        "opts": [
                            "It lengthens the hash input past one 64-byte block, so an attacker must run two compressions per guess",
                            "It makes the digest unpredictable, so an attacker who knows the password cannot confirm it",
                            "It forces the dictionary pass to be repeated per user, since a guess is now tied to one account",
                            "It hides how many accounts share a password by spreading equal passwords over different digests",
                        ],
                        "a": 2,
                        "whys": [
                            r"A 16-byte salt in front of a short password does not cross the block boundary, and even if it did, doubling the cost of one hash is nothing next to the factor of six and a half million the salt actually buys.",
                            r"An attacker holding a candidate password and the record can confirm it in one derivation — the salt is right there. Confirming a guess was never what a salt makes hard; making the guess *reusable* is.",
                            r"Unsalted, one pass over the dictionary tests every user at once; salted, each user needs a pass of their own.",
                            r"It does have that effect, and it is worth having, but it is a side benefit. The 6,500,000-fold increase in attacker work comes from the loss of amortisation, and it would be there even if every user's password were distinct.",
                        ],
                        "why": r"""
Without a salt, one pass over a candidate list produces digests that can be looked up
against the whole dump at once, so the cost of attacking six and a half million accounts
equals the cost of attacking one. The salt puts the account into the hash input, so a
candidate hashed for one user says nothing about any other, and the pass must be run
again per account. That is the whole factor of 6,500,000 — it comes from destroying
amortisation and precomputation, and it needs no secrecy whatever, only uniqueness. What
a salt does not do is make any individual guess expensive; that is the iteration count's
job, and it is a separate defence.
""",
                    },
                    {
                        "q": "A service authenticates API calls with `tag = sha256(secret + params)`. An attacker has one valid `(params, tag)` pair. What can they do?",
                        "opts": [
                            "Nothing without a SHA-256 collision, which is why this construction is considered adequate in practice",
                            "Recover `secret` from the tag by running the compression function backwards from the released state",
                            "Append data of their choosing and compute a valid tag, because the released digest is the hash's state",
                            "Replay the same call indefinitely, which is the only weakness, and a nonce in the parameters removes it",
                        ],
                        "a": 2,
                        "whys": [
                            r"No collision is needed. The extension attack works on a hash with no known collisions at all, because it exploits the shape of Merkle-Damgard rather than any weakness in the compression function.",
                            r"The compression function is one-way, and running it backwards is exactly the problem SHA-256 is built to make hard. Forgery here needs no inversion — the attacker goes forwards from a state he was handed.",
                            r"A Merkle-Damgard digest is the internal state, so anyone holding it can resume the machine.",
                            r"Replay is a real problem and a nonce is a real fix, but a nonce does nothing here: the attacker is not resending the old call, he is producing a tag for a message that has never been sent.",
                        ],
                        "why": r"""
SHA-256 folds 64-byte blocks into a 32-byte state and returns that state as the digest,
so a released tag is a running hash that can be restarted. The attacker appends the
padding the hash would have applied to `secret + params`, then whatever they want, and
resumes from the tag to compute the digest of the longer message — without ever learning
`secret`. They need only the length of the secret, which is a couple of dozen guesses.
Flickr's API was forged this way in 2009. HMAC is immune because the value it releases is
the state of a hash whose input began with the outer key, and resuming that requires the
key.
""",
                    },
                    {
                        "q": "PBKDF2 chains HMAC calls, feeding each output back in as the next input. What does the chaining buy that hashing a long padded string would not?",
                        "opts": [
                            "The work inside one guess is sequential, so extra cores cannot shorten a single derivation",
                            "The derived key grows with the iteration count, so more iterations give more bytes",
                            "Each iteration mixes in fresh salt bytes, so a precomputed table would have to cover them all",
                            "It keeps the derived key uniform, since a hash of a long input is biased towards its later blocks",
                        ],
                        "a": 0,
                        "whys": [
                            r"$U_j$ cannot begin until $U_{j-1}$ is finished, and no hardware repeals that.",
                            r"The output is 32 bytes per block whatever the iteration count; extra length comes from extra blocks, generated with a counter of their own. Iterations buy time, not size, and the two knobs are independent.",
                            r"The salt appears once, in $U_1$, and never again. Precomputation is defeated by the salt being there at all, which a single hash of `salt + password` also achieves — the chain is answering a different question.",
                            r"A hash of a long input is not biased towards anything; every block is folded into the same state and the output is uniform either way. Merkle-Damgard has real weaknesses, and this is not one of them.",
                        ],
                        "why": r"""
Hashing one very long string costs the same total work but is not forced to be
sequential in a way that matters, and it is trivially pipelined; the chain makes $U_j$
depend on the completed $U_{j-1}$, so a single guess occupies one core for the full
duration however much hardware is available. The XOR fold on top of that makes the result
depend on every intermediate rather than only the last, so a chain that wandered into a
short cycle could not silently shrink the output space. Note what the chain does *not*
buy: the attacker still runs thousands of separate guesses in parallel, which is why
PBKDF2 loses to GPUs and why memory-hard designs replaced it.
""",
                    },
                    {
                        "q": "Verification compares a 32-byte tag with `==`. Roughly how many attempts does an attacker who can time the response need to forge a tag?",
                        "opts": [
                            "About $2^{128}$, since timing halves the exponent the way a birthday attack does",
                            "About 8192: 256 values for each byte position, walked left to right across 32 bytes",
                            "About $2^{256}$ still, because the timing difference is far below network jitter and cannot be used",
                            "About 32, one per byte, since each comparison reveals the byte it stopped on outright",
                        ],
                        "a": 1,
                        "whys": [
                            r"Timing here does not shave an exponent, it removes one. The leak turns a search over the whole tag into 32 independent searches over one byte, which is a change of kind rather than of degree.",
                            r"Fix the leading bytes, try all 256 values of the next, and keep whichever ran longest.",
                            r"Jitter makes the measurement need repetition and statistics; it does not destroy the signal, and remote timing attacks on differences of this size have been demonstrated on real networks. Difficulty of measurement is not a security property.",
                            r"The comparison reveals only *how far* it got, not what it found — the attacker still has to try values until one runs a byte longer. That is 256 tries per position, not one.",
                        ],
                        "why": r"""
A short-circuiting comparison inspects 1, 2, 3 … bytes as the guess gets more of the
prefix right, so its running time reports how many leading bytes are correct. The attacker
fixes the prefix he has, tries all 256 values of the next byte, keeps the one that took
measurably longer, and moves on: $256 \times 32 = 8192$ attempts, against $2^{256}$ to
search the tag space. The fix is to inspect all 32 bytes every time — OR each `x ^ y` into
an accumulator and test it once — which is what `constant_time_equals` does and what the
lab's spy check confirms `verify_password` actually calls.
""",
                    },
                    {
                        "q": "A site salts every password and runs 20,000 PBKDF2 iterations. An attacker steals the database and targets one specific account whose password is in a 14-million-entry leaked list. What happens?",
                        "opts": [
                            "The iteration count applies per record, so recovering one password costs as much as recovering the whole database",
                            "The salt is unknown to the attacker for that account, so the dictionary cannot be tested against it at all",
                            "That password falls in well under a minute, because the defences remove amortisation and not guessability",
                            "Nothing: 20,000 iterations put a single dictionary pass beyond the reach of any single machine",
                        ],
                        "a": 2,
                        "whys": [
                            r"The whole database is 6.5 million records and one record is one; the costs differ by that factor exactly. This has it backwards — the per-record cost is what stops the *bulk* attack, and it is small when only one record is wanted.",
                            r"The salt is stored beside the digest, in the clear, and the attacker has the database. Salts were never secret, and a scheme that needed them to be would break every login.",
                            r"14 million candidates at 40,000 hashes each is under 30 seconds on one card.",
                            r"14 million times 40,000 is $5.6 \times 10^{11}$ hashes, which a single high-end card retires in about half a minute. Iteration counts move the bar; they do not put one dictionary pass out of reach.",
                        ],
                        "why": r"""
14 million candidates at 40,000 hashes each is $5.6 \times 10^{11}$ hashes, about 28
seconds on one high-end card. Salting and stretching multiply the cost of attacking
*everybody*, and the numbers there are decisive: 0.0007 seconds unsalted, 76 minutes
salted, 5.8 years salted and stretched. Against one chosen account with a password on a
public list, they buy half a minute. No server-side scheme repairs a guessable password;
what these defences protect is every other user in the file, which is most of the value
and none of the comfort for that one account.
""",
                    },
                    {
                        "q": "Why does the stored record carry its iteration count as a field, instead of the code applying a single constant?",
                        "opts": [
                            "So that verification can lower the count on a slow machine and raise it again on a fast one",
                            "So that records written under an older, cheaper setting still verify once the constant is raised",
                            "So that each account can be given a different count, which frustrates a precomputed table",
                            "So that the derived key length can be worked out from it, since the two are linked by the block counter",
                        ],
                        "a": 1,
                        "whys": [
                            r"The count is not a tuning parameter that verification may choose. Deriving with a different number than the one used at storage time produces a different key and a failed login, whatever machine it runs on.",
                            r"The right number keeps rising, and the records already on disk were written under the old one.",
                            r"Varying the count per account is a defence the salt already provides far better, and a precomputed table is already dead once a per-user salt exists. Iterations raise the cost of a guess; they are not a second separator.",
                            r"The block counter runs 1, 2, 3 over output blocks and has nothing to do with iterations. A 32-byte and a 64-byte key can be derived at the same count, and the lab checks that the first 32 bytes agree.",
                        ],
                        "why": r"""
The appropriate count rises as hardware gets faster — 1,000 in RFC 8018's examples was a
figure from around 2000, and current guidance is in the hundreds of thousands. Every
password already on disk was derived under whatever number was current when it was
stored, and that derivation cannot be redone without the password. Carrying the count in
the record lets old entries verify while new ones use the new setting, and lets an entry
be upgraded at the next successful login, when the plaintext is briefly available. It
also creates a target: an attacker who can edit the field to 1 has removed the defence
entirely, which is why the capstone's authentication tag covers the iteration count as
well as the ciphertext.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "A block cipher is not yet an encryption scheme",
                    "minutes": 17,
                    "body": r'''
In October 2013 a 9.3 GB file of Adobe account records went public: about 153 million
rows, each holding an email address, an encrypted password and — in the clear, right
beside it — the password *hint* the user had typed. The passwords were not hashed. They
were encrypted with Triple DES under a single key, in ECB mode, with no salt.

Nobody recovered that key. They did not need to. Because ECB encrypts each 8-byte block
on its own with a deterministic function, two users with the same password have byte-for-
byte identical ciphertext, and one 8-byte ciphertext appeared on more than 1.9 million
rows. Sort the rows by ciphertext, read the hints attached to the biggest group — "numbers
in order", "1 to 6" — and the password is recovered by crossword rather than cryptanalysis.
The cipher did exactly what it promised. The *mode* gave everything away.

This module is about that gap. A block cipher is a small, rigid object: a permutation on
one fixed-size block. Turning it into something that can encrypt a message is a separate
design decision, and it is the one that decides whether the result is safe.

## Why the block cipher has to be a permutation

Take the lab's parameters: 8-byte blocks, so $2^{64}$ possible inputs. For a fixed key,
encryption maps that set into itself. If two different blocks ever mapped to the same
output, decryption would have to choose between them, and there is nothing in the
ciphertext to choose with. So $E_k$ must be a bijection — a permutation of the block
space, one for each key. Invertibility is not a property you test for afterwards; it has
to be built in.

That is awkward, because the things that make a cipher strong — mixing, avalanche,
non-linearity — are exactly the things that make a function hard to invert. The Feistel
network is the trick that resolves it. Split the block into halves $L$ and $R$ and do:

$$L' = R, \qquad R' = L \oplus F(k, r, R)$$

Now invert it, and watch that $F$ is never inverted. You are handed $(L', R')$. Since
$L' = R$, you already have $R$. So you can recompute $F(k, r, L')$, which is
$F(k, r, R)$, and then $L = R' \oplus F(k, r, R)$. Both halves recovered, with $F$ only
ever run forwards. The round function can be anything at all — the lab uses a truncated
SHA-256, which is emphatically not invertible — and the cipher is still exactly
invertible.

Here is one block going through the lab's four rounds, with the actual key and the actual
values:

```python
import hashlib

BLOCK, ROUNDS, HALF = 8, 4, 4


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def round_function(key, index, half):
    """Deliberately not invertible: a truncated hash."""
    return hashlib.sha256(key + bytes([index]) + half).digest()[:HALF]


block, key = b"12345678", b"key"
left, right = block[:HALF], block[HALF:]
print("start   L=%s R=%s" % (left.hex(), right.hex()))
for index in range(ROUNDS):
    left, right = right, xor_bytes(left, round_function(key, index, right))
    print("round %d L=%s R=%s" % (index, left.hex(), right.hex()))
cipher = left + right
print("cipher  ", cipher.hex())

for index in reversed(range(ROUNDS)):
    left, right = xor_bytes(right, round_function(key, index, left)), left
print("back to ", (left + right).hex(), (left + right) == block)
```

The halves go `31323334`/`35363738` to `35363738`/`c9a08b17` to `c9a08b17`/`3626dacd` and
so on, and the ciphertext is `059a47aecb0c7274` — the vector the lab's first check
requires. Notice that the left half of the output, `059a47ae`, is the right half from one
round earlier: the Feistel swap means half of every round's output is carried straight
through, which is why four rounds is the minimum anyone considers and why real designs
use sixteen.

## The mode is where the message goes

A permutation on 8 bytes cannot encrypt 64 bytes. Something has to say how the blocks
relate, and the simplest answer — encrypt each one independently — is Electronic
Codebook. Its failure follows in one line from the definition: $E_k$ is a function, so
equal inputs give equal outputs, so **every repetition in the plaintext survives into the
ciphertext**.

```python
import hashlib

BLOCK, ROUNDS, HALF = 8, 4, 4


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def round_function(key, index, half):
    return hashlib.sha256(key + bytes([index]) + half).digest()[:HALF]


def block_encrypt(block, key):
    left, right = block[:HALF], block[HALF:]
    for index in range(ROUNDS):
        left, right = right, xor_bytes(left, round_function(key, index, right))
    return left + right


def ecb(data, key):
    missing = BLOCK - (len(data) % BLOCK)
    padded = data + bytes([missing]) * missing
    return b"".join(block_encrypt(padded[i:i + BLOCK], key)
                    for i in range(0, len(padded), BLOCK))


def ctr(data, key, nonce):
    stream = b""
    counter = 0
    while len(stream) < len(data):
        stream += block_encrypt(nonce + counter.to_bytes(HALF, "big"), key)
        counter += 1
    return xor_bytes(data, stream)


def repeats(data):
    blocks = [data[i:i + BLOCK] for i in range(0, len(data), BLOCK)]
    return len(blocks) - len(set(blocks))


message = b"CATSCATS" * 8
key = b"a toy key"
print("plaintext: %d bytes, %d repeated blocks" % (len(message), repeats(message)))
hidden = ecb(message, key)
print("ECB:       %d bytes, %d repeated blocks" % (len(hidden), repeats(hidden)))
print("  block 0:", hidden[:8].hex(), " block 1:", hidden[8:16].hex())
stream = ctr(message, key, b"once")
print("CTR:       %d bytes, %d repeated blocks" % (len(stream), repeats(stream)))
print("  block 0:", stream[:8].hex(), " block 1:", stream[8:16].hex())
```

Seven repeated blocks go in and seven come out; the first two ECB blocks are both
`b3007723be081fb4`. This is what the famous encrypted-penguin image is showing, and it is
what happened to those 1.9 million Adobe rows. CTR leaves zero repeats and does not
lengthen the message.

## Counter mode, derived

If the problem is that the same plaintext block always meets the same permutation, the
cure is to stop putting plaintext into the cipher at all. Encrypt a *counter* instead —
something guaranteed never to repeat — and XOR the result over the message:

$$C_i = P_i \oplus E_k(\text{nonce} \,\|\, i)$$

Four consequences fall straight out of that line, and every one of them shows up in the
lab's checks. The output is the same length as the input, because XOR is byte-for-byte,
so there is no padding at all. Encryption and decryption are the same operation, because
XOR is its own inverse — `ctr_encrypt(ctr_encrypt(x)) == x`. Any block can be decrypted
without touching the others, because block $i$ needs only counter $i$. And the block
cipher is only ever run forwards, which is why the lab never needs `block_decrypt` for
CTR.

## Padding, and the block that looks unnecessary

ECB does need padding, and PKCS#7 has one rule that surprises people: when the data
already fills a whole number of blocks, a **complete extra block** of padding is added.

```python
BLOCK = 8


def pad(data):
    missing = BLOCK - (len(data) % BLOCK)
    return data + bytes([missing]) * missing


print("missing bytes for inputs of length 0..16:")
print([BLOCK - (n % BLOCK) for n in range(17)])
for data in (b"1234567", b"12345678", b""):
    print("%-11r -> %r" % (data, pad(data)))
print("unpad reads the last byte:", pad(b"12345678")[-1])
```

The list runs `8, 7, 6, 5, 4, 3, 2, 1, 8, 7, …` and never contains a zero. That is the
whole design. Unpadding works by reading the final byte and removing that many, so if
"add nothing" were ever legal the receiver could not distinguish a message whose real last
byte is `0x03` from three bytes of padding. Making `missing` always fall between 1 and 8
costs at most one block and makes the decoding unambiguous for every input. The lab's
`unpad` therefore rejects an empty input, a length that is not a multiple of 8, and a
final run of bytes that does not agree with itself.

## The mistake, and what it costs

Two mistakes live here, and both are tempting for the same reason: the code runs and the
output looks like noise.

The first is choosing ECB by accident. `Cipher.getInstance("AES")` in Java gives you
AES/ECB/PKCS5Padding, and plenty of APIs make ECB the path of least resistance. The
output is unreadable to a person, the round trip works, the tests pass — and the structure
of the plaintext is sitting in the ciphertext in plain sight. Confidentiality of *bytes*
is not confidentiality of *patterns*.

The second is treating CTR's tidiness as safety. It has no padding, no repeats, no length
growth, and no integrity whatsoever:

```python
import hashlib
import math


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def keystream(key, nonce, length):
    out = b""
    counter = 0
    while len(out) < length:
        out += hashlib.sha256(key + nonce + counter.to_bytes(4, "big")).digest()
        counter += 1
    return out[:length]


key = b"a toy key"
m1, m2 = b"attack at dawn!!", b"retreat at dusk!"
c1 = xor_bytes(m1, keystream(key, b"same", len(m1)))
c2 = xor_bytes(m2, keystream(key, b"same", len(m2)))
print("c1 xor c2 equals m1 xor m2:", xor_bytes(c1, c2) == xor_bytes(m1, m2))
print("knowing m1 gives m2:", xor_bytes(xor_bytes(c1, c2), m1))

order = b"transfer 0100 to bob"
sealed = xor_bytes(order, keystream(key, b"ord1", len(order)))
flip = ord("1") ^ ord("9")
tampered = bytes(b ^ flip if i == 10 else b for i, b in enumerate(sealed))
print("the bank decrypts:", xor_bytes(tampered, keystream(key, b"ord1", len(tampered))))

space = 2 ** 24
print("WEP had %d IV values; a repeat is likely after about %.0f packets"
      % (space, math.sqrt(2 * math.log(2) * space)))
```

The first half is the nonce-reuse disaster. With the same nonce, $C_1 = P_1 \oplus KS$ and
$C_2 = P_2 \oplus KS$, so $C_1 \oplus C_2 = P_1 \oplus P_2$ and the key has cancelled out.
Knowing either message hands over the other exactly, and knowing neither still leaves two
English texts XORed together, which is a solved problem. WEP shipped a 24-bit IV, and the
last line computes what that means: a repeat becomes likely after about 4,823 frames,
which on a busy access point is seconds.

The second half needs no key at all. The attacker XORs one byte of the ciphertext with
`ord("1") ^ ord("9")` and the bank decrypts `transfer 0900 to bob`. In a stream cipher the
relationship between ciphertext and plaintext is XOR, so a controlled change to one is a
controlled change to the other. Encryption answers "who can read this"; it says nothing
about "who wrote it". That is why the capstone builds encrypt-then-MAC and why its
`open_record` verifies the tag *before* decrypting anything.

## Where these ideas stop

The lab's cipher is a teaching object, not a proposal. Four Feistel rounds with a hash as
the round function is not a security argument, and the 8-byte block is a hard limit of its
own: by the birthday bound, a random 64-bit block repeats after about $2^{32}$ blocks —
roughly 32 GB under one key — and in ECB that repeat is visible, while in CTR the counter
space runs out entirely. This is not academic; it is why 64-bit block ciphers were retired
from TLS after the Sweet32 attacks of 2016, and why AES uses 128-bit blocks.

ECB is not wrong in every possible use. Encrypting a single block of full-entropy data —
wrapping one key under another, say — has no repetitions to leak, because there is only
one block and nothing to compare it with. What ECB cannot do is hide structure, and
almost all real plaintext is structure.

CTR's guarantee lasts exactly as long as the nonce does. The lab splits eight bytes as a
4-byte nonce and a 4-byte counter, which allows $2^{32}$ blocks per nonce and no more —
past that the counter carries into the nonce field and the stream of the next nonce is
reused. And a nonce must be *unique*, which is a stronger and more fragile requirement
than being unpredictable: a counter kept in a file works until the file is restored from
a backup, and a random nonce works until the birthday bound catches it.

## The lab

**ECB versus CTR, and the pattern that leaks** has you build every piece above.
`block_encrypt` and `block_decrypt` are checked against `059a47aecb0c7274` and then
round-tripped over 200 random blocks, with an avalanche check that flipping one plaintext
bit must change at least 12 of the 64 ciphertext bits. `pad` and `unpad` are checked for
the whole-extra-block rule and for rejecting malformed padding. Then the two modes side by
side on `b"CATSCATS" * 8`: ECB must preserve all 7 repeats and grow by one block, CTR must
leave 0 repeats and preserve the length exactly. The last two checks are the point of the
whole exercise — one shows that two messages under a reused nonce XOR to the XOR of their
plaintexts, and one shows that a truncated or wrongly-keyed ECB ciphertext is refused
rather than half-decoded.
''',
                },
            ],
            "quiz": {
                "title": "Permutations, padding and the price of a repeated nonce",
                "minutes": 9,
                "questions": [
                    {
                        "q": "The lab's Feistel round function is a truncated SHA-256, which cannot be inverted. How can the cipher still decrypt?",
                        "opts": [
                            "Decryption inverts the round function by searching the 4-byte output space, which is small enough to be quick",
                            "The round function is applied to the half that survives the swap, so decryption recomputes it forwards",
                            "SHA-256 is invertible on inputs shorter than one block, and each half is only 4 bytes long",
                            "The XOR at the end of each round cancels the round function out, so its value never has to be known",
                        ],
                        "a": 1,
                        "whys": [
                            r"A $2^{32}$ search per round per block would be a strange price for a cipher, and no search happens: `block_decrypt` is the same handful of operations as `block_encrypt`, and both run in constant time.",
                            r"After the swap, $L' = R$, so the input the round function needs is sitting in the ciphertext.",
                            r"SHA-256 is one-way on inputs of every length; being short does not make a digest invertible, and in any case the round function is fed the key and the round index alongside the half.",
                            r"Cancellation is exactly what happens, but it needs the value: $R' \oplus F = L$ works only once $F$ has been recomputed. The point is that recomputing it is possible, not that it is unnecessary.",
                        ],
                        "why": r"""
The swap is what makes it work. One round leaves $L' = R$ and $R' = L \oplus F(R)$, so a
decryptor holding $(L', R')$ already has $R$ — it is $L'$ — and can therefore compute
$F(R)$ by running the round function *forwards*, then recover $L$ as $R' \oplus F(R)$.
Nothing is ever inverted, which is why the round function is free to be a hash, or
anything else with good mixing and no inverse at all. The price is that half of each
round's output passes through untouched, which is why real Feistel designs use sixteen
rounds and not four.
""",
                    },
                    {
                        "q": "153 million Adobe passwords were encrypted with 3DES in ECB mode under one key, and millions were recovered without anyone finding that key. What made it possible?",
                        "opts": [
                            "3DES has an 8-byte block, and blocks that short can be searched exhaustively on modern hardware",
                            "Encrypting so much data under one key eventually leaks it, and 153 million records is far past that limit",
                            "Equal passwords gave equal ciphertext, so rows sorted into groups the plaintext hints then named",
                            "ECB reuses the same keystream for every block, so two ciphertexts XOR to the XOR of their plaintexts",
                        ],
                        "a": 2,
                        "whys": [
                            r"Searching a 64-bit block space is $2^{64}$ work per block and was not what happened. The 8-byte block does have a real weakness — the birthday bound on repeats — but that is a different attack and it was not needed here.",
                            r"Volume under one key raises the chance of repeated blocks; it does not leak the key. The recovery here used no key material at all, and would have worked identically on the first thousand rows.",
                            r"One ciphertext appeared on 1.9 million rows, and their hints said what it was.",
                            r"ECB has no keystream — that description belongs to CTR, and it is the failure of a *reused nonce* rather than of ECB. ECB's leak is repetition between blocks, not a cancelling XOR.",
                        ],
                        "why": r"""
ECB applies a deterministic permutation to each block independently, so identical
plaintext blocks become identical ciphertext blocks. Sorting 153 million rows by
ciphertext therefore grouped the users by password without decrypting anything, and the
password hints — stored unencrypted in the same file — labelled the groups. One block
appeared on over 1.9 million rows; its hints said "numbers in order". The cipher was never
attacked. This is the same defect the lab measures with `count_repeated_blocks`: seven
repeats go into ECB and seven come out.
""",
                    },
                    {
                        "q": "PKCS#7 adds a whole extra block of padding when the data already fills a whole number of blocks. Why not add nothing?",
                        "opts": [
                            "Because a mode needs at least one block of padding to hold the nonce and the message length",
                            "Because a ciphertext whose length gave away the exact plaintext length would leak more than it should",
                            "Because unpadding reads the last byte as a count, and a count of zero cannot be told from real data",
                            "Because the final block would otherwise be encrypted with no diffusion from the blocks before it",
                        ],
                        "a": 2,
                        "whys": [
                            r"Neither the nonce nor a length lives in the padding. ECB carries no nonce at all, and CTR carries its nonce beside the ciphertext while using no padding whatever.",
                            r"The padding hides the length only to the nearest block, so a length leak of up to seven bytes remains either way. Hiding length is a real concern and PKCS#7 is not the tool for it.",
                            r"`missing` runs 8, 7, 6, … 1, 8 and is never 0, so the last byte is always a genuine count.",
                            r"Diffusion between blocks is a property of the mode, not the padding — ECB has none whatever the padding, and CBC has it because of the chaining. Padding changes nothing about it.",
                        ],
                        "why": r"""
Unpadding is defined as: read the final byte, treat it as a count, and remove that many
bytes. For that to be unambiguous every valid count must be one the encoder could have
written. If "add nothing" were legal, a message whose genuine last byte happened to be
`0x03` would be indistinguishable from a message with three bytes of padding, and the
receiver would silently truncate it. `missing = BLOCK - (len(data) % BLOCK)` runs
8, 7, 6, 5, 4, 3, 2, 1, 8, … and never reaches zero, so the rule costs at most one block
and buys a decoding that is correct for every input — which is what the lab's `unpad`
round-trip check over five different lengths is confirming.
""",
                    },
                    {
                        "q": "Two messages are sent under CTR with the same key and the same nonce. What does an attacker who has both ciphertexts learn?",
                        "opts": [
                            "The XOR of the two plaintexts, which reveals either message completely once the other is known",
                            "The keystream itself, from which the block cipher's key follows by inverting one block",
                            "Nothing beyond the fact of the reuse, unless the block cipher is also weak against a chosen-plaintext attack",
                            "The first block of each message, since the counter starts at zero and that block is therefore predictable",
                        ],
                        "a": 0,
                        "whys": [
                            r"$C_1 \oplus C_2 = (P_1 \oplus KS) \oplus (P_2 \oplus KS) = P_1 \oplus P_2$.",
                            r"The keystream comes out only if a plaintext is known, and even then it yields $E_k(\text{nonce} \| i)$, not $k$. Recovering the key from input-output pairs is precisely what a block cipher is designed to prevent.",
                            r"The reuse is the attack, and it needs no weakness in the cipher. A perfect block cipher gives a perfect keystream, and reusing a perfect keystream still cancels it out of the XOR.",
                            r"A predictable counter is fine and intended — the counter is not secret. What must not repeat is the *nonce*, because that is what makes the keystream unique to one message.",
                        ],
                        "why": r"""
CTR encrypts by XOR: $C_1 = P_1 \oplus KS$ and $C_2 = P_2 \oplus KS$. XOR the two
ciphertexts and the keystream cancels, leaving $P_1 \oplus P_2$ with no key involved.
Knowing either plaintext then hands over the other exactly, and knowing neither leaves two
natural-language texts XORed together, which is a century-old solved problem. This is why
uniqueness of the nonce is not a recommendation but a precondition: WEP's 24-bit IV made a
repeat likely after about 4,823 frames, which on a busy link is a few seconds. The lab
checks it directly, asserting that `xor_bytes(c1, c2) == xor_bytes(m1, m2)` for two
messages sent under one nonce.
""",
                    },
                    {
                        "q": "A CTR-encrypted order reads `transfer 0100 to bob`. An attacker who does not have the key changes one ciphertext byte and the bank decrypts `transfer 0900 to bob`. What does this show?",
                        "opts": [
                            "That the nonce was reused, since only a repeated keystream lets an attacker predict a change",
                            "That CTR gives confidentiality alone, and a chosen ciphertext change is a chosen plaintext change",
                            "That the keystream had been recovered beforehand, which is what made the substitution possible",
                            "That CTR should be replaced with ECB here, whose block-wide diffusion would make such an edit fail",
                        ],
                        "a": 1,
                        "whys": [
                            r"The nonce was used once. Malleability needs no reuse at all — it follows from the plaintext and ciphertext being related by XOR, whatever the keystream is.",
                            r"$C \oplus \delta$ decrypts to $P \oplus \delta$, and the attacker chose $\delta$.",
                            r"Nothing about the keystream is known or needed. The attacker XORs `ord('1') ^ ord('9')` into a position and that difference passes through decryption untouched, whatever byte of keystream was sitting there.",
                            r"ECB would confine the damage to one 8-byte block rather than one byte, which is a different failure and not a fix — the block would decrypt to garbage the bank might still act on. Integrity comes from a MAC, not from a choice of mode.",
                        ],
                        "why": r"""
Decryption is $P = C \oplus KS$, so changing $C$ to $C \oplus \delta$ makes the plaintext
$P \oplus \delta$. The attacker who knows the plaintext's format — and message formats are
rarely secret — picks $\delta$ to be the XOR of the character they have and the one they
want, and the change passes through decryption exactly. No key, no keystream, no nonce
reuse. A cipher answers "who can read this" and says nothing about "who wrote this", which
is why the capstone seals records with encrypt-then-MAC and verifies the tag *before* it
decrypts a byte.
""",
                    },
                    {
                        "q": "The lab's cipher uses an 8-byte block. Beyond it being a toy, why is a 64-bit block a real problem for a serious cipher?",
                        "opts": [
                            "A 64-bit block means a 64-bit key, which is inside the reach of a determined attacker today",
                            "Only $2^{64}$ distinct messages can be encrypted before the permutation must repeat one of them",
                            "By the birthday bound, blocks start repeating after about $2^{32}$ of them, and a mode leaks when they do",
                            "Padding costs a whole block, so short records nearly double in size and the overhead reveals their lengths",
                        ],
                        "a": 2,
                        "whys": [
                            r"Block size and key size are independent: 3DES has a 64-bit block and a 112-bit effective key, and AES-256 has a 128-bit block. Confusing the two is common and leads to the wrong estimate of what is at risk.",
                            r"A permutation on $2^{64}$ blocks never repeats an output for distinct inputs — that is what makes it a permutation. The trouble is repeated *inputs* arising by chance across a long message.",
                            r"About $2^{32}$ blocks is 32 GB, and Sweet32 turned that into a practical attack in 2016.",
                            r"Padding overhead is at most one block and is not a security property worth the name. The birthday problem is the reason 64-bit blocks were retired, and it has nothing to do with size on disk.",
                        ],
                        "why": r"""
Encrypt enough blocks under one key and two of them coincide by chance; with 64-bit blocks
the birthday bound puts that at roughly $2^{32}$ blocks, about 32 GB. In ECB a coincidence
is a visible repeat, and in CBC a repeated ciphertext block yields the XOR of two plaintext
blocks — which is what the Sweet32 attacks exploited in 2016 to pull authentication cookies
out of long-lived TLS and OpenVPN connections using 3DES and Blowfish. AES uses 128-bit
blocks, which pushes the same bound out to $2^{64}$ blocks and out of reach. The lab's
8-byte block is fine for demonstrating a mode and would be indefensible in anything real.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "The trapdoor, and how it was actually opened",
                    "minutes": 18,
                    "body": r'''
In early 2012 two groups did the same unglamorous thing: they collected public RSA keys
off the internet — millions of TLS and SSH host keys, scraped from every reachable
address — and put the moduli in a big list. Then they took greatest common divisors of
pairs.

Lenstra and colleagues found that of 6.4 million distinct RSA moduli, about 12,700 shared
a prime factor with some other modulus. Heninger and colleagues, working independently,
found roughly 0.5% of TLS hosts had keys they could factor outright. Nobody attacked the
factoring problem. Two devices — usually cheap routers and firewalls generating a key at
first boot, before their entropy pool had anything in it — had picked the same first
prime, and Euclid's algorithm from around 300 BC does the rest in microseconds:

```python
import math

# two moduli from two devices whose key generator picked the same first prime
n1 = 303986257460055367239258469511722781249
n2 = 323515098865190899620144541583455803797
shared = math.gcd(n1, n2)
print("gcd(n1, n2) =", shared)
print("n1 = %d * %d" % (shared, n1 // shared))
print("n2 = %d * %d" % (shared, n2 // shared))
print("the shared factor has", shared.bit_length(), "bits")
```

Both private keys fall out of one line. Hold that picture through everything below: RSA's
security is a claim about a hard problem, and the way it fails in the field is almost
never that the problem turned out to be easy.

## The trapdoor

Fix a modulus $n = pq$ and exponentiate: $c = m^e \bmod n$. Going forwards is cheap —
square-and-multiply turns a 2048-bit exponent into about 3,000 modular multiplications.
Going backwards, recovering $m$ from $c$ without help, is believed to need the
factorisation of $n$.

The help is a second exponent. Carmichael's function $\lambda(n) = \text{lcm}(p-1, q-1)$
is the exponent to which every unit belongs, so $m^{\lambda(n)} \equiv 1$; choose $d$ with
$ed \equiv 1 \pmod{\lambda(n)}$ and then

$$m^{ed} = m^{1 + k\lambda(n)} = m \cdot \left(m^{\lambda(n)}\right)^k \equiv m \pmod n$$

Everything about RSA is in that line. Computing $\lambda(n)$ needs $p$ and $q$; anyone who
has them can produce $d$; anyone who has only $n$ and $e$ cannot. Here it is on numbers
small enough to check by hand:

```python
import math

p, q = 61, 53
n = p * q
lam = (p - 1) * (q - 1) // math.gcd(p - 1, q - 1)
e = 17
d = pow(e, -1, lam)
print("n = %d, lambda(n) = %d, e = %d, d = %d" % (n, lam, e, d))
print("e * d mod lambda(n) =", e * d % lam)
c = pow(65, e, n)
print("65 encrypts to", c, "and decrypts to", pow(c, d, n))
print("every m in 0..n-1 comes back:",
      all(pow(pow(m, e, n), d, n) == m for m in range(n)))
```

$n = 3233$, $\lambda(n) = 780$, $d = 413$, and 65 encrypts to 2790 and back again — as does
every one of the 3233 residues, including the handful that share a factor with $n$.

Finding $d$ is solving $ed \equiv 1 \pmod{\lambda}$, which is finding integers with
$ed + \lambda y = 1$ — exactly what the extended Euclidean algorithm returns, and it
returns it only when $\gcd(e, \lambda) = 1$. That is why `generate_keypair` in the lab
draws a fresh pair of primes and starts over when $\gcd(65537, \lambda) \neq 1$: there is
no inverse to be had, so there is no private key.

## Finding the primes

Key generation is not a construction, it is a search: sample a random odd number of the
right size and ask whether it is prime. By the prime number theorem the density of primes
near $2^{512}$ is about $1/\ln 2^{512}$, and $512 \ln 2 = 354.9$, so about one candidate in
355 is prime — one in 178 once you only sample odd ones. A few hundred tries, then, and
the lab's `generate_prime` loop is that search written out, with `| (1 << (bits - 1))` to
force the size and `| 1` to force oddness.

Most of those candidates should be rejected cheaply. Trial division by the primes up to 97
costs 24 divisions and eliminates about 76% of odd candidates before any expensive test
runs, which is why `SMALL_PRIMES` is given to you and why the lab's `is_probable_prime`
uses it first.

For the survivors you need a real test. Fermat's little theorem says $a^{n-1} \equiv 1
\pmod n$ for prime $n$ and $a$ not divisible by $n$, so a base that fails is a proof of
compositeness. The trouble is what happens when a base passes:

```python
import math

n = 561
coprime = [a for a in range(2, n) if math.gcd(a, n) == 1]
liars = [a for a in coprime if pow(a, n - 1, n) == 1]
print("561 = 3 * 11 * 17")
print("bases coprime to 561: %d, of which Fermat calls 561 prime: %d"
      % (len(coprime), len(liars)))
d, r = n - 1, 0
while d % 2 == 0:
    d //= 2
    r += 1
print("561 - 1 = %d * 2^%d" % (d, r))
for a in (2, 5):
    print("a=%d:" % a, [pow(a, d * 2 ** i, n) for i in range(r + 1)])
print("67 * 67 mod 561 =", 67 * 67 % 561, "and 67 is neither 1 nor 560")
print("gcd(66, 561) =", math.gcd(66, n), "  gcd(68, 561) =", math.gcd(68, n))
```

All 319 bases coprime to 561 pass Fermat's test. 561 is $3 \times 11 \times 17$. These are
the Carmichael numbers, and no amount of extra bases helps — the test is wrong about them
for every base it is allowed to use.

## What Miller-Rabin adds

The fix comes from a second fact about primes. In $\mathbb{Z}_p$ the equation $x^2 \equiv 1$
has exactly two solutions, $x \equiv \pm 1$, because $p \mid (x-1)(x+1)$ forces $p$ to
divide one factor. A composite modulus with several prime factors has more square roots of
1 than that, and finding one is a proof of compositeness that Fermat's test throws away.

So write $n - 1 = d \cdot 2^r$ with $d$ odd and look at the whole squaring chain
$a^d, a^{2d}, a^{4d}, \dots, a^{2^r d} = a^{n-1}$ rather than only its last entry. If the
chain ends at 1, it arrived there by squaring something whose square is 1. For a prime,
that something has to be $\pm 1$. For 561 with base 2, the chain is
`263, 166, 67, 1, 1` — and 67 squares to 1 without being 1 or 560. That is a nontrivial
square root of 1, so 561 is composite, and Miller-Rabin says so on the very first base
Fermat was fooled by. The last line of the block shows the bonus: $\gcd(67 - 1, 561) = 33$
and $\gcd(67 + 1, 561) = 17$, so the witness hands over the factorisation as well.

Rabin's theorem bounds how often this can fail: for any odd composite, at most a quarter
of the bases in $[2, n-2]$ are liars, so $k$ independently chosen bases leave a failure
probability under $4^{-k}$ — about $2 \times 10^{-10}$ at the lab's 16 rounds. Note which
way that error runs. `False` is a *proof*: a witness was found, the number is composite,
no probability involved. `True` is a statement about the bases that happened to be drawn.

## Signing, and why it is the hash that gets exponentiated

Encryption and signing use the same operation with the exponents swapped: signing raises
to $d$, verifying raises to $e$. The temptation is to sign the message itself. Two things
go wrong, and the second is the interesting one:

```python
import hashlib
import math

p, q = 1000003, 1000033
n = p * q
lam = (p - 1) * (q - 1) // math.gcd(p - 1, q - 1)
e = 65537
d = pow(e, -1, lam)
s7, s11 = pow(7, d, n), pow(11, d, n)
print("signature on 7 :", s7)
print("signature on 11:", s11)
print("their product verifies as:", pow(s7 * s11 % n, e, n))


def message_hash(message):
    return int.from_bytes(hashlib.sha256(message).digest(), "big") % n


print("hash(7) * hash(11) mod n =", message_hash(b"7") * message_hash(b"11") % n)
print("hash(77)                 =", message_hash(b"77"))
for vote in (b"yes", b"no"):
    print("public encryption of %r is always %d"
          % (vote, pow(int.from_bytes(vote, "big"), e, n)))
```

RSA is multiplicative: $(m_1 m_2)^d = m_1^d \cdot m_2^d$. So anyone holding signatures on
7 and on 11 can multiply them and obtain a valid signature on 77, having signed nothing.
The block prints `their product verifies as: 77` from a signer who was never asked about
77. Hashing first destroys the structure — the fourth and fifth lines show
$H(7) \cdot H(11)$ and $H(77)$ are unrelated numbers — and it also solves the mundane
problem that a message must be smaller than $n$. The lab's `sign` therefore exponentiates
`message_hash(message, n)` and never the message, and `verify` recomputes that hash rather
than trusting anything sent alongside.

## The mistake

Textbook RSA is deterministic, and the last two lines of that block are the consequence.
Encrypting a vote with a public key produces one fixed ciphertext for `yes` and one for
`no` — and the key is public, so an eavesdropper encrypts both candidates himself and
compares. The message is never decrypted and never needs to be. The same argument works
against any message drawn from a guessable set: an amount, a name, a session identifier, a
yes-or-no answer.

This is a tempting error precisely because everything appears correct. The mathematics is
right, the round trip works, the tests pass, and the ciphertext is a large unreadable
number. What is missing is not correctness but *semantic security*: a scheme is only
secure if the ciphertext of one chosen message is indistinguishable from that of another,
and a deterministic function can never manage that. The answer is randomised padding —
OAEP for encryption, PSS for signatures — which puts fresh random bytes into every
operation. The lab implements textbook RSA on purpose, so that you meet the gap rather
than reading about it, and its brief says so.

A close relative of the same mistake: with a small exponent and a small message, $m^e$ may
be smaller than $n$, so no reduction happens at all and an integer $e$-th root recovers $m$
with no key. With $e = 3$ and $m = 42$, $m^3 = 74088$, and every modulus in this course is
larger than that.

## Where this stops holding

The lab uses 256-bit keys so the checks finish instantly, and a 256-bit modulus is
factored on a laptop in seconds. For reference, the largest published general factorisation
is RSA-250 at 829 bits, done in 2020 at a cost of about 2,700 core-years — so 1024-bit keys
are retired, 2048 is the working minimum, and 3072 is the recommendation for keys that must
outlive this decade. The algorithm in the lab is exactly the one used at 3072 bits; only
the numbers change.

Miller-Rabin's $4^{-k}$ bound assumes the bases are chosen *randomly*. Against a modulus
supplied by an adversary rather than generated by you, a fixed list of bases is a target:
"Prime and Prejudice" (2018) constructed composites that pass the specific base sets
several real libraries used. The lab's `is_probable_prime` defaults its `rng` to
`random.Random(7)` so that the checks are reproducible, which is a teaching compromise and
is precisely the pattern that paper attacks — worth knowing you are looking at.

RSA is also not how anything encrypts a message in practice. The plaintext must be smaller
than $n$ and exponentiation is thousands of times slower than a block cipher, so real
systems encrypt a symmetric key with RSA and the message with that key. And padding is
where deployed RSA has actually broken: Bleichenbacher's 1998 adaptive attack on PKCS#1
v1.5 recovered plaintext from a server that merely reported whether padding was
well-formed, and the ROBOT results of 2017 found the same flaw still live in major TLS
stacks nineteen years later. Getting the exponentiation right is the easy part.

## The lab

**RSA with Miller-Rabin, encryption and signatures** builds the whole chain with `pow`,
`math.gcd` and `hashlib` and nothing else. `is_probable_prime` must agree with the truth on
every number below 200 — 46 primes, no more and no fewer — and must reject 561, 1105, 1729,
2465, 2821, 6601 and 8911, the Carmichael numbers that defeat Fermat. `generate_prime` must
return a value of exactly the requested bit length, and the same seed must give the same
prime. `egcd` and `modinv` are checked against `math.gcd` and must raise when no inverse
exists. Then `generate_keypair`, `encrypt` and `decrypt` round-trip every interesting
message including 0, 1 and $n-1$, and `sign` and `verify` must reject a changed message, a
changed signature and a signature checked against another key.
''',
                },
            ],
            "quiz": {
                "title": "Trapdoors, witnesses and the structure RSA leaves behind",
                "minutes": 9,
                "questions": [
                    {
                        "q": "Researchers factored thousands of live RSA keys in 2012 by taking pairwise greatest common divisors of public moduli. What had gone wrong?",
                        "opts": [
                            "The moduli were too small, so a gcd over a large collection was faster than factoring one of them",
                            "Devices with too little entropy at first boot generated keys sharing a prime with other devices",
                            "The public exponent 65537 is used almost everywhere, and shared exponents make moduli share factors",
                            "A gcd of two moduli always yields a factor, which is why keys must never be published together",
                        ],
                        "a": 1,
                        "whys": [
                            r"The keys were ordinary 1024- and 2048-bit moduli, and none of them was factored by any general method, fast or slow. A gcd finds a *shared* factor and is useless on two keys that share nothing.",
                            r"Two generators with no randomness available reached for the same first prime.",
                            r"The exponent has nothing to do with the modulus. Almost every key does use 65537, and it causes no sharing whatever — the factors come from the primes that were sampled, not from $e$.",
                            r"The gcd of two moduli with no common factor is 1, which is what a correctly generated pair gives. Publishing public keys is the point of public keys; this attack needed a defect in how they were made.",
                        ],
                        "why": r"""
Embedded devices — routers, firewalls — often generate their host key on first boot, before
anything has stirred their entropy pool, so two units of the same model can walk the same
sequence of candidates and settle on the same first prime. Two moduli sharing one factor
give it up to Euclid's algorithm in microseconds, and the second factor of each is then a
division. Of 6.4 million moduli collected, about 12,700 fell this way. The lesson is that
the factoring problem was never touched: RSA's field failures are overwhelmingly failures
of randomness, of padding or of implementation, not of the hard problem it rests on.
""",
                    },
                    {
                        "q": "561 passes Fermat's test for every one of the 319 bases coprime to it, yet $561 = 3 \\times 11 \\times 17$. What does Miller-Rabin look at that Fermat's test does not?",
                        "opts": [
                            "The whole squaring chain up to $a^{n-1}$, so a square root of 1 other than $\\pm 1$ is caught",
                            "Several bases rather than one, so a composite that fools a single base is found by the next",
                            "The size of $\\gcd(a, n)$, which exposes a shared factor whenever the base is not coprime to $n$",
                            "Whether $n - 1$ factors as $d \\cdot 2^r$, since a Carmichael number never has such a form",
                        ],
                        "a": 0,
                        "whys": [
                            r"A prime modulus admits only $\pm 1$ as square roots of 1, so any other one found along the chain proves the modulus composite.",
                            r"More bases is exactly what does not help here: 561 fools all 319 of them. Miller-Rabin also uses several bases, but that is not what makes it succeed where Fermat fails.",
                            r"That check catches only the bases sharing a factor with $n$, of which there are few, and Fermat's test already fails those. The 319 coprime bases are the problem, and no gcd touches them.",
                            r"Every even number factors as $d \cdot 2^r$, so $n-1$ always does for odd $n$. For 561 it is $35 \cdot 2^4$ — the decomposition is a step in the method, not a test that anything can fail.",
                        ],
                        "why": r"""
Fermat's test reads one value, $a^{n-1} \bmod n$, and Carmichael numbers make that value 1
for every base coprime to them. Miller-Rabin writes $n - 1 = d \cdot 2^r$ and reads the
whole chain $a^d, a^{2d}, a^{4d}, \dots$ that squares up to it. If the chain ends at 1, it
got there by squaring something whose square is 1 — and modulo a prime the only such values
are $\pm 1$. For 561 with base 2 the chain is `263, 166, 67, 1, 1`, and 67 is neither 1 nor
560, so 561 is proved composite on the first base. The witness even yields the factors:
$\gcd(66, 561) = 33$ and $\gcd(68, 561) = 17$.
""",
                    },
                    {
                        "q": "`is_probable_prime(n, rounds=16)` returns `False`. What have you learned?",
                        "opts": [
                            "That $n$ is composite with probability $1 - 4^{-16}$, so a further test is prudent before rejecting it",
                            "That $n$ is composite, since a base that fails is a proof and no probability is involved",
                            "That $n$ is composite unless it is a Carmichael number, the one family it misjudges",
                            "That $n$ failed 16 independent trials, so it is composite unless every base drawn was unlucky",
                        ],
                        "a": 1,
                        "whys": [
                            r"The probabilistic bound applies to the other answer. A `False` is returned only when a witness was found, and a witness is a certificate — there is nothing left to be uncertain about.",
                            r"A witness exhibits a nontrivial square root of 1, or a chain that never reaches $n-1$, and no prime can do either.",
                            r"Carmichael numbers are what defeat *Fermat's* test, and Miller-Rabin handles them like any other composite. In any case they are composite, so calling them so is correct.",
                            r"One failing base is enough; the other fifteen are never reached. And a base cannot be 'unlucky' in this direction — the error is entirely one-sided, and a prime has no witnesses at all.",
                        ],
                        "why": r"""
The error is one-sided, and knowing which side matters. `False` means a witness was found:
either $a^d$ started somewhere other than $\pm 1$ and the chain reached 1 without passing
through $n-1$, or it never reached 1 at all. A prime admits neither, so `False` is a proof.
`True` is the probabilistic answer — it means none of the bases drawn happened to be a
witness, and since at most a quarter of the bases are liars for any odd composite, 16
rounds leave a failure chance under $4^{-16}$, about $2 \times 10^{-10}$. That bound also
assumes the bases were drawn at random, which is why the lab threads an `rng` through the
call.
""",
                    },
                    {
                        "q": "Why does `sign` exponentiate the SHA-256 hash of the message rather than the message itself?",
                        "opts": [
                            "Because a hash is shorter, so the modular exponentiation runs in far fewer multiplications",
                            "Because the private exponent is only defined for inputs coprime to $n$, and a hash is very likely to be",
                            "Because RSA is multiplicative, so signatures on two messages multiply into a signature on their product",
                            "Because a signature must not reveal the message, and hashing hides it from anyone who verifies",
                        ],
                        "a": 2,
                        "whys": [
                            r"Exponentiation cost depends on the size of the *exponent* and modulus, not on the message, so a 32-byte input costs the same as any other residue. Hashing does bring the message under $n$, but that is a separate practical point.",
                            r"$m^{ed} \equiv m$ holds for every residue when $n$ is squarefree, including those sharing a factor with $n$ — the lab's small-key check confirms it for all 3233 of them. Coprimality is not required.",
                            r"$s_1 s_2 = (m_1 m_2)^d$, so signatures on 7 and 11 multiply into a valid signature on 77.",
                            r"A signature is attached to a message everyone can already see, and verification recomputes the hash from that message, so nothing is being hidden. Hiding content is encryption's job, not signing's.",
                        ],
                        "why": r"""
$(m_1 m_2)^d \equiv m_1^d \cdot m_2^d \pmod n$, so an attacker holding valid signatures on
7 and on 11 multiplies them and obtains a valid signature on 77 without the private key and
without ever asking the signer about 77. This is existential forgery, and it is a direct
consequence of RSA's algebra rather than a flaw in it. Hashing first breaks the
relationship: $H(7) \cdot H(11) \bmod n$ and $H(77)$ are unrelated values, so a product of
signatures verifies against nothing anyone can produce a preimage for. It also solves the
mundane requirement that the signed value be smaller than $n$, which is why `message_hash`
reduces modulo $n$.
""",
                    },
                    {
                        "q": "A referendum server publishes its RSA public key and asks voters to send `encrypt(vote, public)`. What is wrong?",
                        "opts": [
                            "Encryption is deterministic, so an eavesdropper encrypts both candidate votes and compares",
                            "The votes are shorter than the modulus, so the exponentiation wraps around and loses information",
                            "The public key cannot encrypt, only verify, so the server could not read any ballot",
                            "Voters share one modulus, so the common-modulus attack lets any two of them recover the private key",
                        ],
                        "a": 0,
                        "whys": [
                            r"There are two possible plaintexts and the encryption function is public.",
                            r"Short messages do not wrap around — they wrap around too little, and with a small exponent that is its own weakness, since $m^e < n$ leaves an integer root to take. Neither is what breaks this scheme.",
                            r"The public exponent encrypts and the private one decrypts; verification is the private key's operation applied in reverse. The server can read the ballots perfectly well, which is the trouble.",
                            r"The common-modulus attack needs two *different exponents* on one modulus given to different parties. Here there is one public key used by everyone in the ordinary way, and no voter holds a private exponent at all.",
                        ],
                        "why": r"""
Textbook RSA is a function, so `encrypt("yes", public)` is the same number every time.
The key is public, so anyone who intercepts a ballot encrypts both candidate votes himself
and sees which one matches; nothing is decrypted and no key is needed. The same argument
works against any message from a guessable set — an amount, a name, a session identifier.
The property being violated is semantic security, and no deterministic encryption can have
it. The fix is randomised padding such as OAEP, which mixes fresh random bytes into every
encryption so the same plaintext gives a different ciphertext each time. The lab implements
textbook RSA deliberately, so that this gap is something you have seen rather than
something you have been told about.
""",
                    },
                    {
                        "q": "Generating a 512-bit prime means sampling random odd candidates until one is prime. Roughly how many candidates, and why is `SMALL_PRIMES` tried first?",
                        "opts": [
                            "About 512, one per bit; the sieve is there to make each Miller-Rabin round cheaper to run",
                            "About 180; trial division by the primes to 97 discards roughly three quarters of them cheaply",
                            "About 355 000; the sieve is what brings that figure down into the range of a practical search",
                            "About 26; the sieve exists to reject candidates that are even, which sampling cannot avoid",
                        ],
                        "a": 1,
                        "whys": [
                            r"One candidate per bit is not a rule anything implies, and the sieve does not change the cost of a Miller-Rabin round — it changes how many rounds are ever started.",
                            r"$512 \ln 2 \approx 355$, halved because only odd candidates are drawn.",
                            r"That is $\ln 2^{512}$ multiplied by a thousand from somewhere. And the sieve changes only the cost per candidate, never how many must be examined before a prime appears.",
                            r"Oddness is forced by `| 1` at sampling time, so no even candidate is ever produced and the sieve has nothing to reject there. 26 is roughly the count for a 64-bit prime, not a 512-bit one.",
                        ],
                        "why": r"""
The prime number theorem puts the density near $2^{512}$ at about $1/\ln 2^{512}$, and
$512 \ln 2 = 354.9$, so about one candidate in 355 is prime — one in 178 once oddness is
forced by `| 1`. Roughly 180 candidates, then. Most of them are worth rejecting for the
price of a division rather than a full Miller-Rabin: trial division by the 25 primes up to
97 leaves only about 24% of odd candidates standing, so three quarters of the search is
disposed of in a few dozen cheap operations. That is what `SMALL_PRIMES` is for, and why
the lab's `is_probable_prime` runs it before the witness loop — and returning `n == small`
on a hit is what keeps the small primes themselves correctly classified.
""",
                    },
                ],
            },
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
            "read": [
                {
                    "title": "The exchange that authenticates nobody",
                    "minutes": 18,
                    "body": r'''
On 28 August 2011 a Gmail user in Iran posted to a Google support forum that his browser
was refusing to connect. Chrome had been shipped with Google's own certificates pinned
into it, and the certificate arriving from the network did not match — it was a valid
wildcard for `*.google.com`, correctly signed, issued on 10 July by DigiNotar, a Dutch
certificate authority whose systems had been broken into weeks earlier. Fox-IT's
investigation later estimated that about 300,000 unique addresses, over 99% of them in
Iran, had reached Google through that certificate. Every one of those TLS sessions was
cryptographically flawless. The key exchange succeeded. Both ends derived a shared key and
used it correctly. The key was shared with the wrong party.

That is the subject of this module, and the thing to keep hold of is that no arithmetic
was broken. Key agreement gets two parties to the same secret over a public wire. It does
not tell either of them who is at the other end, and if you do not add something that
does, the wire decides.

## The exchange

Two people who have never met need a shared secret, and everything they send is read by
everyone. Fix a prime $p$ and a base $g$, both public. Alice draws a secret exponent $a$
and sends $A = g^a \bmod p$; Bob draws $b$ and sends $B = g^b \bmod p$. Then Alice
computes $B^a$ and Bob computes $A^b$, and

$$B^a = (g^b)^a = g^{ab} = (g^a)^b = A^b \pmod p$$

The shared value was never transmitted, and it was never assembled anywhere except inside
the two endpoints. The wire carried $g^a$ and $g^b$; recovering $g^{ab}$ from those two is
the computational Diffie-Hellman problem, and no efficient method is known.

Note what is *not* secret. $p$ and $g$ are published, standardised, and often hard-coded
into protocols. The security rests entirely on the exponents, and on the difficulty of the
discrete logarithm — a scheme whose safety depended on hiding its parameters would be a
different and much worse design.

## The parameters have to be checked

An exponentiation lands in the subgroup generated by its base, and by Lagrange's theorem
the size of that subgroup divides $p - 1$. When $p-1$ has small factors, that is an attack:

```python
for modulus in (31, 23):
    orders = {h: min(k for k in range(1, modulus) if pow(h, k, modulus) == 1)
              for h in range(1, modulus)}
    print("p = %d, p-1 = %d, orders present: %s"
          % (modulus, modulus - 1, sorted(set(orders.values()))))
p = 31
h = 2                       # an element of order 5, because 5 divides 30
print("p=31: 2 has order", min(k for k in range(1, p) if pow(2, k, p) == 1))
print("      2^a takes only", sorted({pow(h, a, p) for a in range(1, 60)}))
p = 23
print("p=23: p-1 = 22 has order", min(k for k in range(1, p) if pow(22, k, p) == 1))
```

Modulo 31, where $p - 1 = 30 = 2 \times 3 \times 5$, subgroups of order 3, 5, 6, 10 and 15
all exist. Send Alice the value 2, which has order 5, and her "shared secret" $2^a$ can
only ever be one of `1, 2, 4, 8, 16`. An attacker guesses among five possibilities, and
learns $a \bmod 5$ into the bargain.

A safe prime is the cure, and the reason is visible in the second line of output. With
$p = 2q + 1$ and $q$ prime, $p - 1 = 2q$ has exactly four divisors, so the only subgroup
orders that exist at all are 1, 2, $q$ and $2q$. The single element of order 1 is 1 and the
single element of order 2 is $p - 1$. So rejecting exactly those two values — plus 0 and
anything at or above $p$, which are not group elements — leaves every remaining peer value
generating a subgroup of size at least $q$. That is the whole of the lab's
`validate_public`, and the reason it can be three comparisons instead of an exponentiation.

## A group element is not a key

The shared value is a number in $[1, p-1]$, and it carries algebraic structure that a
32-byte key must not. The cleanest example is one bit that an eavesdropper can read
without solving anything:

```python
p, g = 23, 5


def is_qr(x):
    return pow(x, (p - 1) // 2, p) == 1


print("a  b   A   B   s   s is a QR   a*b even")
for a, b in ((6, 15), (4, 15), (6, 14), (3, 7)):
    A, B = pow(g, a, p), pow(g, b, p)
    s = pow(B, a, p)
    print("%2d %2d  %2d  %2d  %2d   %-9s  %s" % (a, b, A, B, s, is_qr(s), a * b % 2 == 0))
agree = all(is_qr(pow(pow(g, b, p), a, p)) == (is_qr(pow(g, a, p)) or is_qr(pow(g, b, p)))
            for a in range(1, 23) for b in range(1, 23))
print("an eavesdropper reads that bit off A and B alone:", agree)
```

With $a = 6, b = 15$ the exchange gives $A = 8$, $B = 19$ and a shared value of 2. Whether
that value is a quadratic residue is decided by the parity of $ab$ — and the parity of $a$
is decided by whether $A$ is a residue, which anyone watching the wire can test with one
exponentiation. So one bit of the raw shared secret is public. Use those bits directly as
a key and you have handed that bit over.

Hashing removes it. `derive_key` runs SHA-256 over the secret and returns 32 bytes with no
algebraic relationship to anything, and it encodes the integer at a fixed width —
`secret.to_bytes(64, "big")` — so that a short secret and a long one can never present the
same bytes to the hash. This is why the lab checks
`_key != _secret.to_bytes(64, "big")[:32]`: truncating the group element is not deriving a
key.

## The attack

Now the part that no amount of parameter checking touches. Nothing in the exchange binds
$A$ to Alice. It is a number on a wire. Mallory, sitting between them, answers Alice's
message with her own $M = g^m$ and answers Bob with the same $M$. Alice computes
$M^a = g^{ma}$; Mallory computes $A^m = g^{am}$. They are the same value. Bob and Mallory
likewise. Both victims complete a textbook-correct exchange, and both completed it with
Mallory.

```python
import hashlib
import random

P = int("102061240770763168165730749985530608866235195527521819904558904251312486164011"
        "31463145168740366371535658173164110446769725746180938943583391084300892657547")
G = 2


def derive_key(secret):
    return hashlib.sha256(secret.to_bytes(64, "big")).digest()


def fingerprint(key):
    return hashlib.sha256(key).hexdigest()[:8]


rng = random.Random(7)
alice, bob, mallory = (rng.randrange(2, P - 1) for _ in range(3))
A, B, M = pow(G, alice, P), pow(G, bob, P), pow(G, mallory, P)

print("undisturbed:  alice %s   bob %s"
      % (fingerprint(derive_key(pow(B, alice, P))),
         fingerprint(derive_key(pow(A, bob, P)))))

alice_key = derive_key(pow(M, alice, P))
bob_key = derive_key(pow(M, bob, P))
print("under attack: alice %s   bob %s" % (fingerprint(alice_key), fingerprint(bob_key)))
print("mallory holds alice's key:", alice_key == derive_key(pow(A, mallory, P)))
print("mallory holds bob's key:  ", bob_key == derive_key(pow(B, mallory, P)))
```

Undisturbed, both parties print `513a3071` — the same fingerprint the lab's starter script
reports. Under attack Alice holds `88fa5a40` and Bob holds `05159a54`, Mallory holds both,
and neither victim has anything that would tell them so. She decrypts what Alice sends,
reads it, re-encrypts it under Bob's key, and forwards it. The message arrives unaltered
and on time. There is no error, no delay worth noticing, and no failed check.

## The mistake

The mistake is believing that a correct key exchange is a secure channel, and it is
tempting for a specific and uncomfortable reason: **the honest test passes either way**.
Write an implementation, run Alice and Bob against each other, confirm they agree on a key
and can exchange messages, and every assertion is green. A machine-in-the-middle changes
none of that. Both sides still agree with *someone*, still derive a key correctly, still
decrypt what they are sent. The property that has been lost — that the party at the other
end is the one you meant — is not one that any test of the honest path can observe.

The second mistake is more mechanical: reusing one long-lived exponent without validating
peer values. Ephemeral exponents limit the damage from a small-subgroup probe to one
session; a static key that answers thousands of probes with a confined secret leaks the
exponent modulo one small factor at a time until the Chinese remainder theorem assembles
it.

## Detecting it, and fixing it

Detection is cheap because the attack has an unavoidable signature: the two victims end
with *different* keys. Any function of the key therefore differs, so if Alice and Bob can
compare eight hex characters over a channel Mallory does not control — reading them aloud
on a phone call — the attack is visible. This is what Signal's safety numbers are, and
ZRTP's short authentication string before that.

Two honest caveats. The comparison needs a channel that is itself authenticated, and
"authenticated" for a voice call means recognising the voice; there is no free lunch,
only a cheaper one. And 8 hex characters is 32 bits, so a Mallory willing to grind about
$2^{32}$ candidate exponents can find one whose fingerprint matches the value Alice expects.
That is hours of work, not centuries. The lab's 8 characters are a size chosen for
readability in a printout; Signal shows 60 digits for this reason.

The real fix is to authenticate the exchange itself, so that $A$ arrives with evidence that
Alice sent it. Sign the public value with a long-term key whose owner is already known —
that is the station-to-station protocol, and it is what TLS does when it signs the server's
ephemeral share with the certificate's key. Which is exactly why DigiNotar mattered: TLS
does authenticate its exchange, and the attack succeeded by subverting the thing that vouches
for the identity rather than the mathematics that uses it.

## Where this stops holding

The lab's 512-bit prime is labelled far too small in its own brief, and 2015 showed how
small. The Logjam work found 8.4% of the Alexa top million HTTPS sites would negotiate
512-bit export-grade Diffie-Hellman when asked, and — because the expensive stage of the
number field sieve depends only on $p$ — a single precomputation against one prime breaks
every connection that uses it. A single 512-bit prime covered 82% of the vulnerable
servers, and after the precomputation an individual connection fell in about a minute. The
same paper argued that a state-sized budget puts 1024-bit primes in the same position,
which is why widely shared groups are a liability in a way that per-connection RSA keys are
not.

Everything above assumes the exponents are ephemeral and discarded. Static Diffie-Hellman
gives no forward secrecy: recover the long-term exponent later and every recorded session
opens. And all of it rests on the discrete logarithm being hard for the adversary you have
in mind, which a large quantum computer would not be — the same Shor's algorithm that
retires RSA retires this, which is why the standardised replacements are lattice
constructions such as ML-KEM rather than better primes.

## The lab

**Diffie-Hellman, and Mallory in the middle** hands you the 512-bit safe prime and a
Miller-Rabin so you can verify the parameters yourself: the checks confirm that $P$ is
prime, that $(P-1)/2$ is prime, and that $g^{P-1} \equiv 1$. Then `make_private`,
`public_key`, and `validate_public` rejecting 0, 1, $-1$, $P-1$, $P$ and $P+1$ — the
degenerate peer values the safe prime reduces the problem to. `derive_key` hashes the
fixed-width encoding, `fingerprint` gives the eight characters two people would read to
each other, and `mitm_session` runs the attack and returns both victims' keys along with
Mallory's two. The final assertions are the lesson: `alice_key == mallory_alice_key`,
`bob_key == mallory_bob_key`, `alice_key != bob_key`, and the message Bob receives is
exactly the one Alice sent.
''',
                },
            ],
            "quiz": {
                "title": "Agreement, subgroups and who is at the other end",
                "minutes": 9,
                "questions": [
                    {
                        "q": "An implementation of Diffie-Hellman passes every test: both parties derive the same key and exchange messages correctly. Why does that not rule out a machine in the middle?",
                        "opts": [
                            "The tests use one process, and an attacker on a real network can alter timings the tests cannot show",
                            "Under attack each party still agrees with somebody and derives a key correctly, so nothing observable fails",
                            "The tests use a fixed seed, so the exponents are predictable and the honest path is the only one reachable",
                            "An attacker would corrupt the messages, and a test that only sends short strings would not notice the damage",
                        ],
                        "a": 1,
                        "whys": [
                            r"A machine in the middle does add a hop, but the delay is milliseconds and is not what the honest test is failing to see. Run the attack on one machine and every assertion still passes — timing is not the missing observation.",
                            r"Both victims complete a correct exchange; the party they completed it with is not something the protocol reports.",
                            r"A fixed seed makes the run reproducible and has no bearing on this. Draw fresh random exponents and the honest path still passes under attack, because it is the honest path that is being tested.",
                            r"A competent attacker corrupts nothing — she decrypts, reads, re-encrypts under the other key and forwards. The message arrives byte for byte, which is exactly what makes the attack invisible.",
                        ],
                        "why": r"""
The attack does not break anything the honest path can see. Alice runs a textbook-correct
exchange and derives a key; so does Bob; Mallory holds both and relays the plaintext
unchanged, so messages arrive intact. Every assertion about agreement, derivation and round
trips passes. What has been lost is that the peer is the intended one, and no test of the
honest path observes identity — the protocol never carried any. This is why the lab's final
checks assert `alice_key != bob_key` rather than testing the happy case again: the defect is
only visible when you look at both victims at once, which neither victim can do.
""",
                    },
                    {
                        "q": "Why does using a safe prime $p = 2q + 1$ let `validate_public` be three comparisons instead of an exponentiation?",
                        "opts": [
                            "Because $g^{(p-1)/2}$ is 1 for every valid peer value, and comparisons test that more cheaply",
                            "Because a safe prime makes every element a generator, so no peer value can be degenerate at all",
                            "Because $p-1 = 2q$ has only four divisors, so the sole dangerous elements are 1 and $p-1$",
                            "Because $q$ is prime, so the discrete logarithm is hard and peer values need no checking",
                        ],
                        "a": 2,
                        "whys": [
                            r"That test is one exponentiation, which is precisely the cost the safe prime lets you avoid. It also checks membership of the residue subgroup, which is a different question from whether the element has small order.",
                            r"The elements 1 and $p-1$ have orders 1 and 2 and generate nothing useful, so not every element is a generator. That is exactly why two of them have to be excluded.",
                            r"Subgroup orders divide $p-1 = 2q$, so the only options are 1, 2, $q$ and $2q$.",
                            r"Hardness of the discrete logarithm says nothing about what an attacker may *send* you. A small-order peer value confines the shared secret without anyone taking a logarithm.",
                        ],
                        "why": r"""
Subgroup orders divide $p - 1$. With a safe prime that is $2q$ for prime $q$, so the only
possible orders are 1, 2, $q$ and $2q$ — there is nothing small to hide in. The single
element of order 1 is 1 and the single element of order 2 is $p-1$, so excluding those two
(along with 0 and anything at or above $p$, which are not group elements) guarantees every
accepted value generates a subgroup of at least $q$ elements. Compare a modulus like 31,
where $p-1 = 30$ admits subgroups of order 3, 5, 6, 10 and 15: sending the value 2, of order
5, confines the victim's shared secret to five possibilities and leaks their exponent
modulo 5.
""",
                    },
                    {
                        "q": "Why is the shared group element $g^{ab} \\bmod p$ run through SHA-256 instead of being used as key material directly?",
                        "opts": [
                            "Because the shared element is far too large, and hashing is how a 512-bit value is shortened to 32 bytes",
                            "Because both parties must agree on the key, and only a hash makes their two computations produce equal bytes",
                            "Because it carries algebraic structure — whether it is a quadratic residue follows from what is on the wire",
                            "Because SHA-256 is one-way, so an attacker who later learns the key cannot work back to the exponents",
                        ],
                        "a": 2,
                        "whys": [
                            r"Truncating would shorten it, and truncation is exactly what the lab forbids — the check `_key != _secret.to_bytes(64, 'big')[:32]` exists to catch it. Length is the easy part of the problem and not the reason for the hash.",
                            r"Both parties compute the identical integer already; that is the whole point of the exchange. Hashing equal inputs gives equal outputs, so it changes nothing about agreement.",
                            r"The parity of $a$ shows in whether $A$ is a residue, and the parity of $ab$ decides the same for the secret.",
                            r"Working back to the exponents means solving a discrete logarithm, which is hard with or without a hash. Protecting the exponents is not what the KDF is for.",
                        ],
                        "why": r"""
The shared value is not uniform bytes; it is an element of a group, and the group's
structure is visible from outside. Whether $g^{ab}$ is a quadratic residue is decided by the
parity of $ab$, and the parity of $a$ is decided by whether $A$ is a residue — which any
eavesdropper tests with a single exponentiation. So one bit of the raw secret is public
before anyone starts. A hash destroys every such relationship and returns bytes with no
algebraic tie to the exponents. The fixed-width encoding matters too: `to_bytes(64, "big")`
pads short secrets so that two different integers can never present the same bytes to the
hash.
""",
                    },
                    {
                        "q": "Alice and Bob read their 8-character key fingerprints to each other over the telephone. What does this achieve, and what does it assume?",
                        "opts": [
                            "It proves no eavesdropper recorded the exchange, and assumes the telephone line is not being recorded",
                            "It detects a middle, since the victims hold different keys, and assumes the call itself cannot be faked",
                            "It replaces authentication entirely, and assumes only that both parties can compute the same hash function",
                            "It confirms the exponents were random, and assumes each party generated theirs on a trustworthy machine",
                        ],
                        "a": 1,
                        "whys": [
                            r"Recording the exchange is harmless — that is what public-key agreement is for. A passive eavesdropper learns nothing whether or not the fingerprints are compared.",
                            r"The attack forces two different keys, so any function of the key differs; the check is only as good as the channel it runs over.",
                            r"It detects an attack after the fact rather than preventing one, and it needs a human to do it every time. Signed exchanges replace authentication; a read-aloud fingerprint is a fallback for when nothing else vouches for either party.",
                            r"A fingerprint is a hash of a derived key and says nothing about how the exponents were drawn. Two parties with dreadful randomness would still see matching fingerprints in an unattacked exchange.",
                        ],
                        "why": r"""
The attack has one unavoidable signature: Alice and Bob end up with different keys, so any
function of the key — a fingerprint — differs, and comparing eight characters exposes it.
The assumption is the awkward part. The comparison channel has to be one the attacker
cannot control or impersonate, and for a voice call "authenticated" means recognising the
voice. There is also a size question: 8 hex characters is 32 bits, so an attacker willing to
grind about $2^{32}$ candidate exponents can find one whose fingerprint matches what Alice
expects. That is hours of work rather than centuries, which is why Signal's safety numbers
run to 60 digits and why the lab's shorter value is a readability choice, not a security
one.
""",
                    },
                    {
                        "q": "The Logjam work found that a single 512-bit prime was used by 82% of servers offering export-grade Diffie-Hellman. Why did that concentration matter so much?",
                        "opts": [
                            "Servers sharing a prime derive related session keys, so breaking one connection reveals the others",
                            "A shared prime means a shared generator, and a known generator makes the discrete logarithm tractable",
                            "The expensive stage of the number field sieve depends only on the prime, so one effort served them all",
                            "Sharing a prime raises the chance two servers pick the same exponent, which a birthday search then finds",
                        ],
                        "a": 2,
                        "whys": [
                            r"Session keys under one prime are unrelated: they depend on exponents drawn independently by each pair. Breaking one connection tells you nothing about the next, which is why the *precomputation* rather than the individual break was the finding.",
                            r"The generator is public in every Diffie-Hellman group and always has been — usually 2. Knowing it makes no logarithm easier; the design assumes the adversary has it.",
                            r"Pay once per prime, then break each connection using it in about a minute.",
                            r"Exponents are drawn from a space of about $2^{512}$, so collisions are not a practical concern, and a collision between two servers would not help an attacker who wants a third one's traffic.",
                        ],
                        "why": r"""
The number field sieve splits into a stage that depends only on the modulus and a much
cheaper stage that depends on the particular target. Concentrate 82% of vulnerable servers
on one 512-bit prime and the expensive stage is paid once for all of them; individual
connections then fell in about a minute each. That is an economics of scale attackers do
not get against RSA, where every host has its own modulus, and it is the reason the paper
argued a state-sized budget puts widely shared 1024-bit groups in the same position. The
lab's 512-bit prime is labelled far too small in its own brief for exactly this reason —
the algorithm is unchanged at 3072 bits, only the arithmetic is slower.
""",
                    },
                    {
                        "q": "What is Diffie-Hellman's security actually resting on?",
                        "opts": [
                            "That $p$ and $g$ are kept secret between the two parties, since anyone knowing both can compute the shared value",
                            "That deriving $g^{ab}$ from the transmitted $g^a$ and $g^b$ is hard while exponentiating is cheap",
                            "That each party keeps their own public value hidden until the other has committed to theirs",
                            "That the exponents are large enough that a search over the exponent space is infeasible",
                        ],
                        "a": 1,
                        "whys": [
                            r"$p$ and $g$ are published and often standardised into a protocol, and knowing them lets anyone perform the exchange without learning any secret. A scheme relying on hidden parameters would be a much weaker one.",
                            r"That gap between forwards and backwards is the whole construction.",
                            r"The public values are meant to be public and their order of arrival is not a security property. Commitment schemes solve a different problem, and adding one here would not stop a middle from substituting both.",
                            r"Necessary but far from sufficient. Enormous exponents are no help if the discrete logarithm can be computed directly, which is what the number field sieve does at 512 bits regardless of how large $a$ and $b$ are.",
                        ],
                        "why": r"""
The construction is a gap between two directions: exponentiating modulo $p$ is cheap, and
recovering $g^{ab}$ from $g^a$ and $g^b$ is believed hard — the computational
Diffie-Hellman assumption, which would follow from the discrete logarithm being hard.
Everything else is public by design. The prime and the generator are standardised and
hard-coded into protocols, the public values are broadcast, and the order they arrive in is
irrelevant. Large exponents are necessary but not the point: at 512 bits the modulus falls
to the number field sieve however the exponents were drawn, which is what Logjam
demonstrated.
""",
                    },
                ],
            },
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
